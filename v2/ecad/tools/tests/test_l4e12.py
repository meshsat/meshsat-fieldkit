"""Layer 4 task L4-E12 (MESHSAT-1478 under MESHSAT-1357, 2 October 2026; v2/docs/records/l4e12/): the kit's electronics against
the inside air at D-02a's +55 C operating margin (E3-O) and E5's +60 C dwell, held as predicates on what l4e12_thermal.py
computes, revised after the focused check astra-check-l4e12-1.

The predicates: the power model and the reduced-mode model are reproduced byte for byte before any figure is used, and
T-H1's floor and L4-E10's inside air are reproduced from them; the acceptance is read from the texts, not typed; every
fitted line, module and undeclared line is screened and every part the first pass finds within reach is read one by one;
the corrected rule judges a powered part on its recommended or operating range and uses an absolute maximum only as an
exclusion screen; approach (a)'s line lies between the low case's outer-film cap and W4's high case; the selected route keeps
E3-O as TEST-PLAN states it (every radio C1 leaves on stays on) and lets the hold act only in E5, inside a trigger window
that exists only with a calibrated reference; the SGP41's own shutdown acts before its local +55 C; the two 3.3 V regulators
are part of the route; every line with no range held carries an evidence obligation and the fans are architecture-level; no
owner question is forced; the page carries the .out's figures; the committed .out is what the script prints; the record's
own files carry no long dashes and no claim words; the check is filed and listed. Nothing here writes into the tree.
"""
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e12")
SCRIPT = os.path.join(REC, "l4e12_thermal.py")
OUT = os.path.join(REC, "l4e12_thermal.out")
PAGE = os.path.join(REC, "L4E12-ELECTRONICS-THERMAL.md")
WATCH = [os.path.join(TOOLS, g) for g in ("gen_sch_b.py", "gen_sch_c.py", "gen_sch_d.py", "gen_sch_e.py", "pcb_requirements.yaml")]
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_CACHE = {}


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _R():
    if "R" not in _CACHE:
        need(SCRIPT, "the L4-E12 record")
        need(os.path.join(ROOT, ".git"), "a git checkout (the script finds the tree by git)")
        need(os.path.join(ROOT, "v2", "vendor", "ti", "held", "ti-tlv755p-c404027.pdf"), "a held document of the L4-E12 record (its fetch_held_back.py)")
        need(os.path.join(ROOT, "v2", "vendor", "ti", "held", "ti-csd17577q5a-slps516.pdf"), "a held document (records/s117/fetch_held_back.py)")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        _CACHE["before"] = {p: _sha(p) for p in WATCH}
        sp = importlib.util.spec_from_file_location("l4e12_thermal_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        try:
            _CACHE["R"] = m.compute()
        except SystemExit as e:
            raise AssertionError("l4e12_thermal.py refused (exit %s)" % e.code)
        _CACHE["M"] = m
    return _CACHE["R"]


def t_models_reproduced_and_the_floor_and_air_from_them():
    R = _R()
    assert R["r0a"] and R["r0b"] and R["r0c"], "a reproduction failed"
    T = R["T"]
    assert abs(T["g_floor"] - 1.6664) < 5e-5 and T["agree_g"], "T-H1's floor is not LO-01a's 1.6664 W/K"
    assert abs(T["air_uncond"][0] - 70.00) < 5e-3 and abs(T["air_uncond"][1] - 75.00) < 5e-3, T["air_uncond"]
    assert abs((T["air_uncond"][1] - 60.0) - (T["sgp55"] - T["t_use"])) < 1e-9
    assert abs(T["ballast_k"] * T["g_floor"] - 2.09) < 1e-9


def t_the_acceptance_is_read_not_typed():
    R = _R()
    A = R["A"]
    assert "survive and recover at the margin" in A["d02a"] and "operate to specification inside the envelope" in A["d02a"]
    assert "CM5 throttling logged but no shutdown" in A["e3o_pass"]
    assert A["e3o_config"].startswith("deployed with the monitor and radios on")
    assert "with the kit logging" in A["e5_config"] and "survive and recover (D-02a, SC-03)" in A["e5_pass"]
    assert "only C1's inside-air trigger sheds modules" in A["controls"]
    assert (A["e3o_h"], A["e3o_t"]) == (4.0, 55.0) and A["e5"][4] == 60.0
    assert "both WiFi link cards, the monitor" in A["heat_off"]
    assert "radios dark" in A["emcon"]


def t_every_line_is_screened_and_the_reached_ones_are_read():
    R = _R()
    scr = R["screen"]
    assert len(scr) == R["gc"]["rows"] + R["gc"]["mods"] + R["gc"]["undeclared"]
    assert R["gc"]["rows"] >= 140 and R["gc"]["mods"] >= 15, R["gc"]
    for r in scr:
        if "OUT OF SCOPE" in r["verdict"].values():
            assert list(r.get("refs", {}).keys()) in (["P"], ["module"]), "a line outside board P and the cells is out of scope: %s" % r["part"]
    assert not R["unread"], "lines within reach that no one read: %s" % R["unread"]


def t_the_corrected_rule_judges_powered_parts_on_their_operating_ranges():
    R = _R()
    m = _CACHE["M"]
    S = R["S"]
    P = {p["k"]: p for p in m.PARTS}
    lim, basis, key, absv = m.govern(P["PCM2912A"], "work", S)
    assert lim == 70.0 and absv == 125.0 and key == "pcm_rec", "a powered PCM2912A is judged on its recommended +70 C, its +125 C a screen"
    assert m.verdict(70.0, 76.0, 78.0, "on", 125.0) == "INCONCLUSIVE" and m.verdict(70.0, 76.0, 78.0, "work", 125.0) == "REACHED"
    assert m.govern(P["SGP41"], "work", S)[0] == 55.0 and m.govern(P["SGP41"], "off", S)[0] == 70.0
    assert m.govern(P["LIME"], "off", S)[0] == 70.0 and m.govern(P["AW7915"], "off", S)[0] == 90.0
    assert m.govern(P["RM520N"], "work", S)[0] == 75.0 and m.govern(P["RM520N"], "off", S)[0] == 90.0
    for k in ("RB9704", "SA868", "G6K", "EPAPER"):
        lim, basis, _key, _a = m.govern(P[k], "off", S)
        assert "operating" in basis and lim == S[P[k]["op"]]["v"][-1], k
    assert S["pdi_storage_stated"]["v"] is False, "the e-paper's flyer now states a storage range: re-read it"
    assert S["pcm_absnote"]["v"] is True and S["tlv755_absnote"]["v"] is True and S["rm_recover"]["v"] is True


def t_approach_a_sits_between_the_low_case_cap_and_the_high_case():
    R = _R()
    a, T = R["ap"]["a"], R["T"]
    assert abs(a["gmax"] - (T["q_hs"] + T["qb"]) / 10.0) < 1e-9, "(a)'s line is not the +70 C class at E5"
    assert T["cap"][0] < a["gmax"] < T["w4_open"][1] < T["cap"][1]
    assert abs(a["g_e3o"] - (T["q_hs"] + T["qb"]) / 15.0) < 1e-9
    assert set(k for k, _w in a["open"]) == {"ATP19", "EPAPER"}


def t_the_route_keeps_e3o_as_stated_and_the_hold_acts_only_in_e5():
    R = _R()
    m = _CACHE["M"]
    c, a, T = R["ap"]["c"], R["ap"]["a"], R["T"]
    route = {p["k"]: p["route"] for p in m.PARTS}
    for k in ("RB9704", "SA868", "PCM2912A", "G6K"):
        assert route[k][0] == "work" and route[k][1] == "off", k
    assert c["gmax"] < a["gmax"] and abs(c["gmax"] - c["g_e5"]) < 1e-12 and c["g_e3o"] < c["g_e5"]
    assert abs(c["L"]["E3-O"]["mixed"] - (55.0 + (T["q_hs"] + T["qb"]) / c["gmax"])) < 1e-9, "E3-O at the line is not the heat stage"
    assert abs(c["L"]["E5"]["mixed"] - 70.0) < 1e-9
    for pr in c["parts"]:
        if pr["k"] in c["g"]:
            for mg in ("E3-O", "E5"):
                assert pr["temps"][mg][0] <= pr["lim"][mg] + 1e-9, (pr["k"], mg)
    assert {k for k, _w in c["open"]} == {"ATP19", "EPAPER"}
    tr = c["trip"]
    assert abs(tr["width"] - (15.0 - (T["q_hs"] + T["qb"]) / c["gmax"])) < 1e-9
    assert tr["e_allow"] > 0 and tr["plume_window"] < 0 and tr["g_plume"] > T["w4_open"][1]
    assert tr["env_mix"] < tr["e3o_mix"] < tr["trip_mid"] < tr["need_by"]


def t_the_sgp41_shutdown_acts_before_its_local_55_c():
    R = _R()
    sg, S = R["ap"]["sgp"], R["S"]
    assert sg["t_off"] + sg["err"] + sg["grad"] + sg["lag"] <= S["sgp_op"]["v"][1] + 1e-9
    assert sg["t_on"] == S["sgp_rec"]["v"][1] == 50.0 and sg["t_on"] < sg["t_off"]
    assert sg["env_margin"] > 0, "the SGP41 would be off inside the envelope at the line"
    assert sg["env_air_floor"] > sg["kept_to"], "at T-H1's floor the function is lost at the hot edge; the record says so"


def t_the_regulators_are_part_of_the_route():
    R = _R()
    rg = R["ap"]["reg"]["rows"]
    rec = R["decl"]["rec755"]
    plan = rg["E U13 at the model's plan"]
    assert all(plan["DBV"][mg] > rec for mg in ("E3-O", "E5")) and all(plan["DRV"][mg] < rec for mg in ("E3-O", "E5"))
    assert rg["E U13 at its rail's declared typical"]["DRV"]["E5"] > rec, "the declared 0.35 A needs more than the DRV package"
    assert all(rg["C U5 at its rail's declared typical"]["DRV"][mg] < rec for mg in ("E3-O", "E5"))


def t_the_unrated_lines_are_named_and_the_fans_are_architecture_level():
    R = _R()
    m = _CACHE["M"]
    names = [u[0] for u in m.UNRATED]
    assert dict((u[0], u[1]) for u in m.UNRATED)["IP68 fans"] == "ARCHITECTURE"
    open_rows = [r for r in R["ap"]["c"]["screen"] if r["max"] is None and "INCONCLUSIVE" in r["verdict"].values()]
    assert len(open_rows) == 11, len(open_rows)
    for r in open_rows:
        assert any(n_.split(" ")[0] in r["part"] for n_ in names), "an unrated line without an evidence obligation: %s" % r["part"]


def t_no_owner_question_is_forced():
    R = _R()
    assert R["forced"] == []
    rt = R["route"]
    assert rt["EPAPER"]["c"] == "INCONCLUSIVE" and rt["EPAPER"]["b"] == "OUTSIDE AUTHORITY"
    assert rt["SGP41"]["b"] == "OUTSIDE AUTHORITY" and rt["SGP41"]["c"] == "CONDITIONAL"
    assert rt["ATP19"]["b"] == "CLOSES"


def t_the_page_carries_the_out_figures():
    R = _R()
    page = open(PAGE, encoding="utf-8").read()
    out = open(OUT, encoding="utf-8").read()
    T, a, c = R["T"], R["ap"]["a"], R["ap"]["c"]
    sg, tr = R["ap"]["sgp"], c["trip"]
    for fig in ("%.3f" % c["gmax"], "%.3f" % a["gmax"], "%.3f" % c["g_e3o"], "%.2f" % T["air"]["E3-O"], "%.2f" % T["air"]["E5"], "%.3f" % T["q_m"],
                "%.3f" % T["q_hs"], "%.4f" % T["g_floor_ballast"], "%.2f" % c["L"]["E3-O"]["mixed"], "%.2f" % tr["e_allow"], "%.2f" % tr["width"],
                "%.2f" % sg["t_off"], "%.2f" % tr["trip_mid"], "%.3f" % tr["g_plume"]):
        assert fig in page and fig in out, "the figure %s is not on both the page and the .out" % fig


def t_out_is_what_the_script_prints():
    _R()
    ch = subprocess.run([sys.executable, "-B", SCRIPT], cwd=ROOT, capture_output=True)
    assert ch.returncode == 0, ch.stderr.decode()[-400:]
    assert ch.stdout == open(OUT, "rb").read(), "l4e12_thermal.out is not what l4e12_thermal.py prints"


def t_nothing_written_into_the_tree():
    _R()
    after = {p: _sha(p) for p in WATCH}
    assert after == _CACHE["before"]


def t_the_record_carries_no_long_dashes_and_no_claim_words():
    files = [os.path.join(dp, f) for dp, _dn, fs in os.walk(REC) for f in fs
             if f.endswith((".md", ".py", ".out", ".txt")) and "__pycache__" not in dp and os.sep + "checks" not in dp] + [os.path.abspath(__file__)]
    claim = re.compile(r"(?i)\b(certified|compliant|qualified|proven|guaranteed|withstands|survives|rated for)\b")
    dash = "[%s%s]" % (chr(0x2013), chr(0x2014))
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert not re.search(dash, t), "a long dash in %s" % p
        bad = [m.group(0) for m in claim.finditer(t) if not re.search(r"[\w-]*CERTIFIED\.tsv", t[max(0, m.start() - 8):m.end() + 4])]
        assert not bad or p == os.path.abspath(__file__), "claim words %s in %s" % (bad, p)


def t_the_check_is_filed_and_listed():
    p = os.path.join(REC, "checks", "astra-check-l4e12-1.md")
    need(p, "the filed check")
    t = open(p, encoding="utf-8").read()
    assert t.startswith("accepted: no\n") and "`cx31-l4e12-check`" in t and "## Blocking discrepancies" in t
    assert "checks/astra-check-l4e12-1.md" in open(os.path.join(REC, "README.md"), encoding="utf-8").read()
