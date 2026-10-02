"""Layer 4 task L4-E12 (MESHSAT-1478 under MESHSAT-1357, 2 October 2026; v2/docs/records/l4e12/): the kit's electronics against
the inside air at D-02a's +55 C operating margin (E3-O) and E5's +60 C dwell, held as predicates on what l4e12_thermal.py
computes, revised after the focused check astra-check-l4e12-1 and the targeted recheck astra-check-l4e12-2.

The predicates: the power model and the reduced-mode model are reproduced byte for byte before any figure is used, and
T-H1's floor and L4-E10's inside air are reproduced from them; the acceptance is read from the texts, not typed; every
fitted line, module and undeclared line is screened and every part the first pass finds within reach is read one by one;
every judged limit names its rating category, a powered part is judged on its recommended or operating range, and an
absolute rating clears nothing on its own (the SGP41 on Table 4); approach (a)'s line lies between the low case's outer-film
cap and W4's high case; the selected route keeps E3-O as TEST-PLAN states it (every radio C1 leaves on stays on) and lets
the hold act only in E5, inside a trigger window that exists only with a calibrated reference; the SGP41 is off before its
local +55 C and its output is used only under Table 4's +50 C, on a reference with a printed maximum error; no location
holds it inside its maker's conditions in the envelope, so the owner question is raised for it and for nothing at the
margins; the two 3.3 V regulators are part of the route; every line with no range held carries an evidence obligation and
the fans are architecture-level; the page carries the .out's figures; the committed .out is what the script prints; the
record's own files carry no long dashes and no claim words; both checks are filed and listed. The dependency round of 2
October 2026 (the record's section 13, the .out's section 8): the lines' basis and sensitivities; the configuration and the
fans-off case; the fans counted in the power budget, the profile and its replay; T-H1's owner, method, steady-state times
and pass line, with its draft procedure; a failed reading's cases and the session's fallbacks. Nothing here writes into the
tree.
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


def t_the_corrected_rule_names_every_category_and_clears_nothing_on_an_absolute_rating():
    R = _R()
    m = _CACHE["M"]
    S = R["S"]
    P = {p["k"]: p for p in m.PARTS}
    g = m.govern(P["PCM2912A"], "work", S)
    assert (g["lim"], g["key"], g["cat"], g["absv"]) == (70.0, "pcm_rec", "recommended", 125.0) and m.is_abs(m.CAT[g["abs_key"]])
    assert m.verdict(70.0, 76.0, 78.0, "on", 125.0) == "INCONCLUSIVE" and m.verdict(70.0, 76.0, 78.0, "work", 125.0) == "REACHED"
    assert m.verdict(None, 76.0, 78.0, "work", 150.0) == "INCONCLUSIVE", "an absolute rating alone cleared a part"
    assert m.verdict(None, 76.0, 78.0, "work", 77.0) == "PLACEMENT" and m.verdict(None, 76.0, 78.0, "work", 75.0) == "REACHED"
    on, off = m.govern(P["SGP41"], "work", S), m.govern(P["SGP41"], "off", S)
    assert (on["lim"], on["key"], on["absv"]) == (50.0, "sgp_rec", 55.0), "a powered SGP41 is judged on Table 4's +50 C, Table 5's +55 C a screen"
    assert (off["lim"], off["absv"]) == (50.0, 70.0) and m.is_abs(m.CAT[off["abs_key"]])
    assert m.govern(P["LIME"], "off", S)["lim"] == 70.0 and m.govern(P["AW7915"], "off", S)["lim"] == 90.0
    assert m.govern(P["RM520N"], "work", S)["lim"] == 75.0 and m.govern(P["RM520N"], "off", S)["lim"] == 90.0
    for k in ("RB9704", "SA868", "G6K", "EPAPER"):
        g = m.govern(P[k], "off", S)
        assert g["basis"].startswith("unpowered, inside a range it may operate in") and g["lim"] == m.hi_of(S, P[k]["op"]), k
    for k in ("pcm_bias", "pcm_st", "sgp_op", "sgp_st", "csd77_tj", "csd78_tj", "ap2112_tj", "ap64500_tj", "ap6320_tj", "tps62933_tj",
              "tlv755_tjabs", "tlv758_tjabs", "bme_st"):
        assert m.is_abs(m.CAT[k]), k
    for k in ("pcm_rec", "sgp_rec", "sgp_rec_st", "tlv755_tjrec", "tlv758_tjrec", "tps62933_tjrec", "tusb8041_tj", "tusb2046_ta", "ap64500_tjop"):
        assert not m.is_abs(m.CAT[k]), k
    assert R["heads"] == sorted(m.HEADS) and S["bme_t_typ"]["v"] is True
    rows = R["screen"] + R["ap"]["c"]["screen"]
    for r in rows:
        if set(r["verdict"].values()) <= {"NO PART", "OUT OF SCOPE", "NOT FITTED"} or "level2" in r:
            continue
        assert r["max"] is None or r.get("cat"), "a screened line with no category: %s" % r["part"]
        if m.is_abs(r.get("cat")):
            assert "NOT REACHED" not in r["verdict"].values(), "cleared on an absolute rating alone: %s" % r["part"]
    csd = [r for r in R["screen"] if r["part"].startswith("CSD17577")]
    assert csd and m.is_abs(csd[0]["cat"]) and set(csd[0]["verdict"].values()) == {"INCONCLUSIVE"}, "CSD17577Q5A's +150 C is an absolute rating"
    tusb = [r for r in R["screen"] if "TUSB2046" in r["part"]]
    assert tusb and tusb[0]["cat"] == "recommended" and tusb[0]["max"] == 85.0
    assert S["pdi_storage_stated"]["v"] is False, "the e-paper's flyer now states a storage range: re-read it"
    assert S["pcm_absnote"]["v"] is True and S["tlv755_absnote"]["v"] is True and S["rm_recover"]["v"] is True
    assert R["pred"]["P11 every judged limit names its category and none is cleared on an absolute rating alone (the SGP41 on Table 4)"]


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


def t_the_sgp41_is_off_before_its_local_55_c_and_used_only_under_table_4():
    R = _R()
    sg, S = R["ap"]["sgp"], R["S"]
    assert sg["err"] == S["tmp117_acc70"]["v"][0] == 0.15, "the reference's printed maximum error to 70 C"
    assert abs(sg["lag"] - 15.0 / 3600.0 * 61.0) < 1e-12
    assert abs(sg["t_off_x"] - (55.0 - 0.15 - 0.5 - sg["lag"])) < 1e-12 and sg["t_off"] == 54.0 and sg["t_off"] <= sg["t_off_x"]
    assert abs(sg["t_on_x"] - (50.0 - 0.15 - 0.5 - sg["lag"])) < 1e-12 and sg["t_on"] == 49.0 and sg["t_on"] <= sg["t_on_x"]
    assert sg["off_at"] <= S["sgp_op"]["v"][1] and sg["on_at"] <= S["sgp_rec"]["v"][1]
    assert abs(sg["loc_max"] - (sg["t_on"] - sg["err"] - sg["m"])) < 1e-12


def t_no_location_holds_the_sgp41_inside_its_makers_conditions_in_the_envelope():
    R = _R()
    sg, T = R["ap"]["sgp"], R["T"]
    wall = sg["locs"][1]
    assert wall["g_need"] == min(l_["g_need"] for l_ in sg["locs"]), "the east wall's skin is the coolest place that samples the bay"
    assert wall["g_need"] > max(T["g_3253_closed"][1], T["w4_closed"][1]), "a lid-closed conductance the record carries reaches the line"
    assert wall["g_need"] < max(T["g_3253_open"][1], T["w4_open"][1])
    assert wall["open_line"] > sg["loc_max"] > wall["c1"] and sg["warm"] <= sg["loc_max"]
    assert sg["stor_out"] and tuple(sg["stor_rec"]) == (5.0, 30.0) and tuple(sg["st_env"]) == (-20.0, 45.0)
    assert sg["rec_h"][0] < sg["rec_h"][1] and sg["stop_bind"]
    assert all(v["bay"] <= sg["stor_lim"] + 1e-9 and v["skin"] < v["bay"] for v in sg["marg"].values())
    assert R["pred"]["P14 no location holds the SGP41 to Table 4 in the envelope: the coolest skin's line over every lid-closed conductance held, storage outside Table 4"]


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
    ab = [r for r in R["ap"]["c"]["screen"] if r.get("screen_k")]
    assert ab and all(m.is_abs(r["cat"]) for r in ab), "a line cleared by a screen whose rating is not absolute"
    out = open(OUT, encoding="utf-8").read()
    assert "7d The lines cleared only by an absolute rating (INCONCLUSIVE at the line, the exclusion screen cleared): %d;" % len(ab) in out


def t_the_owner_question_is_raised_for_the_sgp41_in_the_envelope_and_nothing_at_the_margins():
    R = _R()
    assert R["forced_margin"] == [] and R["sgp_forced"] and R["forced"] == ["SGP41 in the envelope"]
    rt = R["route"]
    assert rt["EPAPER"]["c"] == "INCONCLUSIVE" and rt["EPAPER"]["b"] == "OUTSIDE AUTHORITY"
    assert rt["SGP41"]["b"] == "OUTSIDE AUTHORITY" and rt["SGP41"]["c"] == "INCONCLUSIVE"
    assert rt["ATP19"]["b"] == "CLOSES"
    assert abs(R["g2"]["e3o"] - 68.543) < 5e-4 and abs(R["g2"]["e5"] - 70.793) < 5e-4, "the escalation example of the recheck"
    out = open(OUT, encoding="utf-8").read()
    sec = out[out.index("6b Inside the envelope"):out.index("6c Escalation")]
    assert re.findall(r"(?m)^   ([A-Z])  ", sec) == ["A", "B", "C"], "the owner's question carries at most three options"
    assert "6c Escalation is not limited to 6b" in out


def t_the_page_carries_the_out_figures():
    R = _R()
    page = open(PAGE, encoding="utf-8").read()
    out = open(OUT, encoding="utf-8").read()
    T, a, c = R["T"], R["ap"]["a"], R["ap"]["c"]
    sg, tr = R["ap"]["sgp"], c["trip"]
    for fig in ("%.3f" % c["gmax"], "%.3f" % a["gmax"], "%.3f" % c["g_e3o"], "%.2f" % T["air"]["E3-O"], "%.2f" % T["air"]["E5"], "%.3f" % T["q_m"],
                "%.3f" % T["q_hs"], "%.4f" % T["g_floor_ballast"], "%.2f" % c["L"]["E3-O"]["mixed"], "%.6f" % tr["e_allow"], "%.2f" % tr["width"],
                "%.6f" % sg["t_off_x"], "%.6f" % sg["t_on_x"], "%.3f" % sg["locs"][1]["g_need"], "%.2f" % sg["loc_max"], "%.2f" % tr["trip_mid"],
                "%.3f" % tr["g_plume"], "%.3f" % R["g2"]["e3o"], "%.3f" % R["g2"]["e5"],
                "%.3f" % R["dep"]["th1"]["ub"][10.0]["pass"], "%.3f" % R["dep"]["deep"]["line"], "%.3f" % R["dep"]["plate"]["e5_floor"],
                "%.3f" % R["dep"]["plate"]["e3o_floor"], "%.3f" % R["dep"]["plate"]["e5_deep_floor"], "%.3f" % R["dep"]["fan_sens"]["g_lo"],
                "%.3f" % R["dep"]["fan_sens"]["g_hi"], "%.3f" % R["dep"]["fan_sens"]["prof_hi"], "%.2f" % R["dep"]["fans_off"]["e5_plate_max"]):
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


def t_the_basis_of_the_lines_is_the_heat_over_the_room_to_the_limit():
    R = _R()
    d, T, c, a = R["dep"], R["T"], R["ap"]["c"], R["ap"]["a"]
    rw = d["rows"]
    assert abs(rw["E5, the hold"]["G"] - c["gmax"]) < 1e-12 and abs(rw["E3-O, the heat stage"]["G"] - c["g_e3o"]) < 1e-12
    assert abs(rw["E5, no hold"]["G"] - a["gmax"]) < 1e-12
    for r in rw.values():
        assert abs(r["Q"] - (r["q"] + T["qb"])) < 1e-12 and abs(r["dGdW"] - 1.0 / r["dT"]) < 1e-12 and abs(r["dGdK"] + r["Q"] / r["dT"] ** 2) < 1e-12
        assert r["w"][0] < r["G"] < r["w"][1] and r["k"][0] < r["G"] < r["k"][1]
    h = d["hold"]
    assert abs(h["p_load"] + h["loss"] + h["dist"] + h["front"] - T["q_m"]) < 1e-9 and abs(sum(h["place"].values()) - T["q_m"]) < 1e-9
    assert R["A"]["l4e8_ballast"] == T["qb"] and R["A"]["l4e10_floor"] == 1.6664 and R["A"]["m507"]["dwell_h"] == 6.0
    assert d["hold_action"] and all(b < a_ for _k, a_, b in d["hold_action"]), "the hold only lowers loads"
    assert ("H5007NL", "on", 70.0, "operating") in d["setters"], "the class the hold leaves powered in the air"


def t_the_configuration_and_the_fans_off_case():
    R = _R()
    d = R["dep"]
    assert [n for n, _w in d["fans_running"]["E5"]] == ["two mixer fans", "cooler fan slot 3"]
    fo = d["fans_off"]
    assert fo["e5_air"][0] > 70.0 and fo["g_needed_e5"] > R["T"]["w4_open_still"][1], "the fans-off case is past +70 C on W4's still values"
    assert fo["e5_plate_max"] <= 70.0, "the plate-coupled parts stay at the plate with the fans stopped"
    for case in ("low", "high"):
        tot, walls, face = d["conf"][case]["open_fans"]
        assert abs(tot - walls - face) < 1e-12


def t_the_fans_are_counted_in_the_energy_budget():
    R = _R()
    d, A = R["dep"], R["A"]
    assert len(A["trace_fans"]) == 4 and all(t == "R" for _w, t, _n in A["trace_fans"])
    assert A["replay_profile"] == (42.8, 39) and A["trace_total"][1] == 42.8
    assert not any("fan" in n for _w, n in A["replay_undoc"][1]) and len(A["replay_undoc"][1]) == 3
    fp = dict((r["label"], r) for r in d["fan_power"])
    assert abs(fp["PS-IDLE-SPEC (the profile)"]["plan"]["state"] - 42.8) < 0.05 and fp["E5's hold"]["plan"]["n"] == 2
    fs = d["fan_sens"]
    assert fs["g_lo"] < R["ap"]["c"]["gmax"] < fs["g_hi"] and fs["runtime_factor"] < 1.0
    out = open(OUT, encoding="utf-8").read()
    assert "Register row drafted for L4-E9's downstream register" in out


def t_t_h1_has_an_owner_a_method_and_a_pass_line():
    R = _R()
    t1, c = R["dep"]["th1"], R["ap"]["c"]
    assert t1["ub"][10.0]["pass"] > t1["ub"][20.0]["pass"] > c["gmax"]
    assert 0 < t1["taus"][0] < t1["tau_line"] < t1["taus"][1] and t1["points"] == 8
    assert abs(t1["rise_line"][0] - R["A"]["rta_heater"][2] / c["gmax"]) < 1e-12
    assert t1["rad"]["low"] > 1.0 and t1["rad"]["high"] > 1.0
    proc = os.path.join(REC, "T-H1-PROCEDURE-DRAFT.md")
    need(proc, "the T-H1 procedure draft")
    t = open(proc, encoding="utf-8").read()
    for fig in ("%.3f" % c["gmax"], "%.3f" % t1["ub"][10.0]["pass"], "%.3f" % t1["ub"][20.0]["pass"], "%.1f" % t1["heater"][2],
                "%.1f to %.1f h" % t1["t_ss"], "%.0f to %.0f h" % t1["total_h"], "%.6f" % c["trip"]["e_allow"],
                "%.3f" % R["dep"]["plate"]["e5_floor"], "%.3f" % R["dep"]["plate"]["e3o_floor"], "%.2f" % R["dep"]["fans_off"]["e5_plate_max"]):
        assert fig in t, "the procedure draft lacks %s" % fig
    assert "prototype bench" in t and "Layer 9" in t and "owner authorises" in t


def t_a_failed_reading_has_a_fallback_inside_the_rulings():
    R = _R()
    d, c = R["dep"], R["ap"]["c"]
    for g, a3, a5 in d["fail"]:
        assert (a3 <= 70.0 + 1e-9) == (g >= c["g_e3o"] - 1e-9) and a5 > 70.0
    pl = d["plate"]
    assert pl["e5_deep_floor"] < pl["e5_floor"] < c["g_e3o"] and pl["e3o_floor_out"] <= pl["e3o_floor"] < c["g_e3o"]
    assert d["deep"]["q"] < R["T"]["q_m"] and d["deep"]["line"] < c["g_e3o"]
    fn = d["fins"]
    assert fn["ratio"]["both2"][0] > fn["ratio"]["out2"][1] > 1.0 and fn["low_cap_out"] < c["gmax"]
    assert all(a > b > 0 for _g, a, b, _e in d["cond"])


def t_both_checks_are_filed_and_listed():
    readme = open(os.path.join(REC, "README.md"), encoding="utf-8").read()
    for n_, job in ((1, "cx31-l4e12-check"), (2, "cx32-l4e12-recheck")):
        p = os.path.join(REC, "checks", "astra-check-l4e12-%d.md" % n_)
        need(p, "the filed check %d" % n_)
        t = open(p, encoding="utf-8").read()
        assert t.startswith("accepted: no\n") and "`%s`" % job in t and "## Blocking discrepancies" in t
        assert "checks/astra-check-l4e12-%d.md" % n_ in readme
