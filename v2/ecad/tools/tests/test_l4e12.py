"""Layer 4 task L4-E12 (MESHSAT-1478 under MESHSAT-1357, 2 October 2026; v2/docs/records/l4e12/): the kit's electronics against
the inside air at D-02a's +55 C operating margin (E3-O) and E5's +60 C dwell, held as predicates on what l4e12_thermal.py
computes.

The predicates: the power model and the reduced-mode model are reproduced byte for byte before any figure is used, and
T-H1's floor and L4-E10's inside air are reproduced from them; the acceptance is read from the texts, not typed; every
fitted line, module and undeclared line is screened and every part the first pass finds within reach is read one by one;
the ratings rule takes an absolute maximum or a storage range only where its maker states one; approach (a) needs more than
the sealed case's outer films give at W4's low coefficients; the hold lowers the enclosure line, acts nowhere inside the
envelope, stays engaged once entered, closes E3-O at T-H1's floor and holds every part it routes by the air at the selected
line; no owner question is forced and the e-paper's route waits on its maker; the record's page carries the .out's figures;
the committed .out is what the script prints; the record's files carry no long dashes and no claim words. Nothing here
writes into the tree.
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
    # the floor is the SGP41's line by construction: the same heat over the same conductance gives the same 15 K rise
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
            only_p = list(r.get("refs", {}).keys()) in (["P"], ["module"])
            assert only_p, "a line outside board P and the cells is out of scope: %s" % r["part"]
    assert not R["unread"], "lines within reach that no one read: %s" % R["unread"]


def t_the_ratings_rule_takes_wider_statements_only_where_stated():
    R = _R()
    m = _CACHE["M"]
    S = R["S"]
    P = {p["k"]: p for p in m.PARTS}
    assert m.govern(P["PCM2912A"], "powered", S)[0] == 125.0, "the PCM2912A's absolute ambient under bias"
    assert m.govern(P["SGP41"], "powered", S)[0] == 55.0 and m.govern(P["SGP41"], "unpowered", S)[0] == 70.0
    assert m.govern(P["LIME"], "unpowered", S)[0] == 70.0 and m.govern(P["AW7915"], "unpowered", S)[0] == 90.0
    assert m.govern(P["RM520N"], "powered", S)[0] == 85.0 and m.govern(P["RM520N"], "unpowered", S)[0] == 90.0
    # with no storage range stated, an unpowered part is judged on its operating range
    for k in ("RB9704", "SA868", "G6K", "EPAPER"):
        lim, basis, _key = m.govern(P[k], "unpowered", S)
        assert "operating" in basis and lim == S[P[k]["op"]]["v"][-1], k
    assert S["pdi_storage_stated"]["v"] is False, "the e-paper's flyer now states a storage range: re-read it"


def t_approach_a_passes_the_sealed_case_cap():
    R = _R()
    a, T = R["ap"]["a"], R["T"]
    assert abs(a["gmax"] - (T["q_hs"] + T["qb"]) / 10.0) < 1e-9, "(a)'s line is not the +70 C class at E5"
    assert a["gmax"] > T["cap"][0] and a["g_m"][1] > T["w4_open"][1]
    assert set(k for k, _w in a["open"]) == {"SGP41", "ATP19", "EPAPER"}


def t_the_hold_lowers_the_line_and_closes_e3o_at_the_floor():
    R = _R()
    c, a, T = R["ap"]["c"], R["ap"]["a"], R["T"]
    assert c["gmax"] < a["gmax"] and T["q_m"] < T["q_hs"]
    assert abs(c["L"]["E5"]["mixed"] - 70.0) < 1e-9, "the selected line does not put E5's mixed air at the +70 C class"
    assert c["L_floor"]["E3-O"]["mixed"] < 70.0
    for pr in c["parts"]:
        if pr["k"] in c["g"]:
            assert pr["temps"]["E5"][0] <= pr["lim"] + 1e-9 and pr["temps"]["E3-O"][0] <= pr["lim"] + 1e-9, pr["k"]
    assert {k for k, _w in c["open"]} == {"ATP19", "EPAPER"}
    t = c["trip"]
    assert t["never_in_env"] and t["stays"] and t["before_trip_hi"] <= 70.0 and t["e5_low"] < t["trip"]


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
    for fig in ("%.3f" % c["gmax"], "%.3f" % a["gmax"], "%.2f" % T["air"]["E3-O"], "%.2f" % T["air"]["E5"], "%.3f" % T["q_m"],
                "%.3f" % T["q_hs"], "%.4f" % T["g_floor_ballast"], "%.2f" % c["L_floor"]["E3-O"]["mixed"], "%.1f" % m_trip()):
        assert fig in page and fig in out, "the figure %s is not on both the page and the .out" % fig


def m_trip():
    _R()
    return _CACHE["M"].HOLD_TRIP_C


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
             if f.endswith((".md", ".py", ".out", ".txt")) and "__pycache__" not in dp] + [os.path.abspath(__file__)]
    claim = re.compile(r"(?i)\b(certified|compliant|qualified|proven|guaranteed|withstands|survives|rated for)\b")
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert not re.search("[%s%s]" % (chr(0x2013), chr(0x2014)), t), "a long dash in %s" % p
        bad = [m.group(0) for m in claim.finditer(t) if not re.search(r"[\w-]*CERTIFIED\.tsv", t[max(0, m.start() - 8):m.end() + 4])]
        assert not bad or p == os.path.abspath(__file__), "claim words %s in %s" % (bad, p)
