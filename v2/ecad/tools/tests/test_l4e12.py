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
and pass line, with its draft procedure; a failed reading's cases and the session's fallbacks. The consolidation (section 14, the .out's section 9): a first-principles
conservative bound from held geometry at the coefficients' conservative ends, reconciled with W4's 1.22 W/K; U-02's class
DECIDES because E3-O's gap stays positive with every session measure; the smallest experiment's thresholds. The heat-rejection
question (section 15, the .out's section 10): three approaches on the same bound, none reaching the approved profile's need at
+40 C or charging on the design day, the shortfall, the owner's options and the deciding point. The thermal reconciliation
(section 16, the .out's section 11, the owner's amendment of 2 October 2026, 14:20): 1.509 W/K at 42.4 W is 1.447 W/K after its
uncertainty and stands for no requirement's mode; every condition's heat, ambient, limit and need from the texts; the +55 C
inside-air limit is the heat stage's (1.806 W/K, LO-01a with the ballasts); the heat counted once with P = the heaters + the
fans; the relationship QS = A k dT on the case's own films; the room reading conservative; each point's threshold, setting,
spread and duration; the page and the procedure carry the figures. The fix round of the Layer 4 review (section 17, the .out's
section 12, astra-check-l4close-1's B3, B4 and B7): no absolute rating decides a line and each mode's governing line is its
tightest correctly categorised local limit, per CFL-002 option with C as defined; the charging heat is input less stored less
exported; the battery-only run is coupled to C1 and 2.52 h stays energy-only. Nothing here writes into the tree.
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
                "%.3f" % R["dep"]["fan_sens"]["g_hi"], "%.3f" % R["dep"]["fan_sens"]["prof_hi"], "%.2f" % R["dep"]["fans_off"]["e5_plate_max"],
                "%.3f" % R["cb"]["E5"]["open"]["g"], "%.3f" % R["cb"]["E3-O"]["open"]["g"], "%.3f" % R["cb"]["gap_w"]["E3-O"],
                "%.3f" % R["cb"]["bind"]["E3-O with F4"]["need"], "%.3f" % R["cb"]["cap"]["E5"], "%.2f" % R["cb"]["ops"]["E3-O, the heat stage"]["air"],
                "%.3f" % R["cb"]["exp"]["targets"][0][2], "%.3f" % R["cb"]["exp"]["targets"][1][2], "%.3f" % R["cb"]["exp"]["targets"][4][2],
                "%.3f" % R["hr"]["short_w"], "%.3f" % R["hr"]["q_max_best"], "%.3f" % R["hr"]["rows"][-1]["use"]["g"], "%.3f" % R["hr"]["q_idle"],
                "%.3f" % R["hr"]["need_ch"][0], "%.3f" % R["hr"]["need_ch"][1], "%.3f" % R["hr"]["exp2"][0][2], "%.3f" % R["hr"]["exp2"][2][2]):
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


def t_the_conservative_bound_and_u02s_class():
    R = _R()
    m = _CACHE["M"]
    cb, T, A = R["cb"], R["T"], R["A"]
    gm = A["geo_m"]
    held = ((gm["t_wall"], 0.00534), (gm["depth"], 0.10897), (gm["mid"][0], 0.37775), (gm["mid"][1], 0.26345), (gm["feet"], 8.38))
    assert all(abs(a - b) < 1e-12 for a, b in held), "the held geometry read from CASE-MARGINS moved"
    assert (m.EPS_PLATE[0], m.EPS_SHELL[0], m.K_PP[0], m.F_OPEN[0]) == (0.70, 0.85, 0.12, 0.70), "the bound takes the conservative ends"
    for mg in ("E5", "E3-O"):
        r = cb[mg]
        assert r["open"]["g"] < r["open_opt"]["g"] and r["closed"]["g"] < r["open"]["g"] < T["w4_open"][0]
        assert r["open"]["g"] < r["v"][0][1] < r["v"][1][1] < r["v"][2][1] < r["cap"]
        assert r["cap"] < cb["lines"][mg], "a line under the outside films' cap would let an inside measure reach it"
    assert abs(cb["recon"][0][1] - T["w4_open"][0]) < 1e-9 and abs(cb["recon"][-1][1] - cb["E5"]["open"]["g"]) < 1e-6
    b3, b5 = cb["bind"]["E3-O with F4"], cb["bind"]["E5 with F4 and F3"]
    assert abs(b3["need"] - (T["q_hs"] + T["qb"]) / 30.0) < 1e-9 and abs(b5["need"] - (R["dep"]["deep"]["q"] + T["qb"]) / 25.0) < 1e-9
    assert b3["gap"] > 0 and b5["gap"] <= 0 and cb["klass"] == "DECIDES"
    assert b3["credits"][-1][1] > b3["need"] > b3["credits"][0][1], "only the unbounded credits together close E3-O's gap"
    assert cb["ops"]["E3-O, the heat stage"]["air"] > 85.0 and cb["ops"]["E5, the deeper hold (F3)"]["air"] <= 85.0
    rd = [x[2] for x in cb["exp"]["targets"]]
    assert all(x[2] > x[1] for x in cb["exp"]["targets"]) and rd == sorted(rd, reverse=True)
    out = open(OUT, encoding="utf-8").read()
    assert "9e U-02'S CLASS: T-H1 DECIDES." in out


def t_the_heat_rejection_approaches_and_the_shortfall():
    R = _R()
    hr, T = R["hr"], R["T"]
    assert abs(hr["q_prof"] - 43.4) < 0.02, "the profile's heat into the case is L4-E9's 43.4 W"
    assert abs(hr["need_g"] - hr["q_prof"] / (R["ap"]["c"]["trip"]["need_by"] - T["t_use"])) < 1e-12
    assert hr["t3"] == 42.0 and hr["day"] == (13.2, 18.3)
    assert abs(hr["need_ch"][0] - hr["q_chg"] / (42.0 - 13.2)) < 1e-12 and abs(hr["need_ch"][1] - hr["q_chg"] / (42.0 - 18.3)) < 1e-12
    assert abs(hr["q_chg"] - T["chg_prof"]["heat"] - T["qb"]) < 1e-12, "the charging heat is the balance plus the solar stage's ballasts"
    rows = hr["rows"]
    assert len(rows) == 7 and rows[-1]["use"]["g"] == max(r["use"]["g"] for r in rows) and rows[0]["use"]["g"] == min(r["use"]["g"] for r in rows)
    for r in rows:
        assert abs(r["use"]["g"] - hr["q_prof"] / (r["use"]["air"] - T["t_use"])) < 1e-9
        assert r["use"]["walls"] > 0 and r["use"]["plate_out"] > 0
    assert not hr["reaches"] and not hr["charges"] and hr["short_w"] > 0 and hr["short_g"] > 0 and min(hr["short_ch"]) > 0
    assert hr["q_idle"] < hr["q_max_best"] < hr["q_prof"] and hr["q_max_bare"] < hr["q_max_best"]
    ex = hr["exp2"]
    assert all(rd > tg for _l, tg, rd, _r in ex) and ex[0][1] == hr["need_g"]
    assert R["pred"]["P21 heat rejection on the bound: no approach reaches the profile at +40 C (the best short by a positive margin) nor charging on the design day; U-02 stays a closure condition"]


def t_the_thermal_reconciliation():
    R = _R()
    m = _CACHE["M"]
    rc, T, A, hr = R["rc"], R["T"], R["A"], R["hr"]
    c5 = rc["check509"]
    assert abs(c5["after"] - c5["target"]) < 1e-6 and abs(c5["target"] - hr["need_g"]) < 1e-12, "1.509 W/K is 1.447 W/K after its uncertainty"
    assert abs(c5["p"] - 2.0 * A["rta_heater"][2]) < 1e-12 and abs(c5["air40"] - (T["t_use"] + c5["p"] / c5["reading"])) < 1e-12
    assert 68.0 < c5["air40"] < 68.2, "the owner's +68.1 C"
    k = {x[0]: x for x in rc["conds"]}
    assert list(k) == ["K%d" % i for i in range(1, 11)] + ["X1", "X2", "X3"]
    for key, x in k.items():
        assert abs(x[7] - x[2] / (x[5] - x[3])) < 1e-12, "%s: the need is Q over the room" % key
    assert abs(k["K1"][7] - T["g_floor_ballast"]) < 1e-9 and k["K1"][5] == 55.0 and k["K1"][3] == T["t_use"] == 40.0
    assert k["K5"][6] == "lid closed" and k["K5"][7] == k["K1"][7] and k["K9"][3] == A["e3o_t"] and abs(k["K9"][7] - k["K1"][7]) < 1e-9
    assert k["K6"][3] == 20.0 and k["K6"][5] == 50.0 and abs(k["K6"][7] - hr["need_g"]) < 1e-12 and k["K6"][7] == k["X2"][7]
    assert k["K7"][5] == k["K8"][5] == hr["t3"] and (k["K7"][3], k["K8"][3]) == hr["day"]
    assert abs(k["K7"][2] - hr["q_chg"]) < 1e-12 and abs(k["K7"][7] - hr["need_ch"][0]) < 1e-12 and abs(k["K8"][7] - hr["need_ch"][1]) < 1e-12
    assert abs(k["X3"][7] - 42.4 / 15.0) < 1e-9 and k["X1"][7] > k["X3"][7] > k["K1"][7], "the owner's 2.83 W/K is no requirement's mode"
    assert abs(k["K10"][2] - (T["q_m"] + T["qb"])) < 1e-12 and abs(k["K10"][7] - R["ap"]["c"]["gmax"]) < 1e-9
    lm = rc["lim"]
    assert "inside-air (+50 C)" in lm["req024_c1"] and "-20 to +40 C ambient" in lm["req024_env"] and "QUALIFICATION MARGINS" in lm["d02a"]
    assert "SGP41 above +55 C" in lm["req052"] and "SGP41 above +55 C fails E3-L" in lm["e3l_air"] and lm["no505"]
    assert "one module" in lm["d02b_35"] and "full-sun design is a later" in lm["d02e"] and "shaded (D-02e)" in lm["req024_shade"]
    q = rc["q"]
    assert abs(q["prof"]["loads"] + q["prof"]["conv"] + q["prof"]["i2r"] - q["prof"]["total"]) < 1e-9
    assert abs(q["hs"]["loads"] + q["hs"]["conv"] + q["hs"]["front"] + q["hs"]["ballast"] - q["hs"]["total"]) < 1e-9
    assert abs(q["charge"]["total"] - hr["q_chg"]) < 1e-12 and abs(q["charge"]["total"] - q["prof"]["total"] - q["charge"]["extra"]) < 1e-12
    assert abs(q["bench"]["prof_heaters"] + q["prof"]["fans"] - q["prof"]["total"]) < 1e-12 and abs(q["bench"]["hs_heaters"] + q["hs"]["fans"] - q["hs"]["total"]) < 1e-12
    for s in q["settings"]:
        assert abs(s["heaters"] + s["fans"] - s["Q"]) < 1e-12 and abs(sum(v for _k, v in s["spread"]) - s["heaters"]) < 1e-6
        assert abs(s["v"] ** 2 / q["bench"]["r"] * s["n"] - s["heaters"]) < 1e-9 and not any(p_.startswith("fans") for p_, _v in s["spread"])
    assert [s["n"] for s in q["settings"]] == [1, 1, 1, 2, 2]
    for row in rc["trans"]:
        for rise, g_room, g_op, ratio in row[1:]:
            assert 1.0 <= ratio < 1.05 and g_op > g_room, "the room reading is the conservative side, and not by much"
    for key, Q_, gneed, rd, rise_, ur in rc["marg"]:
        assert rd > gneed and abs(rd * (1.0 - ur) - gneed) < 1e-6 and abs(rise_ - Q_ / rd) < 1e-12
    rt = rc["rit"]
    assert m.RITTAL_K_STEEL == 5.5 and len(m.RITTAL_SHA) == 64 and abs(rt["area"] - rt["a_plate"] - rt["a_wall"]) < 1e-15
    assert rt["rows"][0][4] < rt["steel_g"] < k["K1"][7] and rt["cap"][0] < k["K1"][7] < T["w4_open"][1]
    assert abs(rt["rows"][0][4] - rc["trans"][0][1][2]) < 1e-6, "A k at K1's rise is the bound's +40 C conductance"
    assert [x[0] for x in rc["times"]] == ["K1", "K5", "K10", "K6", "K7"] and all(x[2] > x[3] > x[1] > 0 for x in rc["times"])
    assert R["pred"][[p_ for p_ in R["pred"] if p_.startswith("P22 ")][0]]
    out = open(OUT, encoding="utf-8").read()
    page = open(PAGE, encoding="utf-8").read()
    proc = open(os.path.join(REC, "T-H1-PROCEDURE-DRAFT.md"), encoding="utf-8").read()
    for h in ("11 THE THERMAL RECONCILIATION", "11a THE CLAIM, CHECKED.", "11b THE HEAT, COUNTED ONCE", "11c THE NODES AND THE LIMITS.",
              "11d THE RELATIONSHIP AND THE TRANSLATION.", "11e THE MARGIN.", "11f WHAT ONE POINT CLOSES, AND WHAT REMAINS (CORRECTED by 12a",
              "11g THE PROCEDURE", "\n13 Predicates\n"):
        assert h in out, "the .out lacks %r" % h
    assert "## 16. The thermal reconciliation" in page and all("### 16.%d " % i in page for i in range(1, 10))
    figs = ["%.3f W/K" % k[x][7] for x in ("K1", "K2", "K3", "K4", "K6", "K7", "K8", "K10", "X1", "X3")]
    figs += ["%.3f W" % x for x in (q["prof"]["total"], q["charge"]["total"], q["hs"]["total"], q["bench"]["prof_heaters"], q["bench"]["hs_heaters"])]
    figs += ["%.3f W/K" % x[3] for x in rc["marg"]] + ["%.1f to %.1f %%" % (
        100.0 * (min(x[3] for row in rc["trans"] for x in row[1:]) - 1.0), 100.0 * (max(x[3] for row in rc["trans"] for x in row[1:]) - 1.0))]
    figs += ["%.3f W/K" % rt["steel_g"], "%.2f W/m2K" % rt["k_need"], "%.3f W/K" % rt["cap"][0], "%.3f" % rt["rows"][0][4], m.RITTAL_SHA[:16]]
    for fig in figs:
        assert fig in page and fig in out, "the figure %s is not on both the page and the .out" % fig
    for s in q["settings"]:
        for fig in ("%.3f W" % s["Q"], "%.3f W" % s["heaters"], "%.2f V" % s["v"]):
            assert fig in proc and fig in out and fig in page, "the setting %s is not in the procedure, the .out and the page" % fig
    for pt in R["pm"]["points"]:
        assert "%.2f h" % pt["tau"] in proc and "%.1f h" % pt["steady"] in proc and "%.1f h" % pt["steady"] in out
    for fig in ["%.3f W/K" % x[3] for x in rc["marg"] if x[0] in ("K2", "K6", "K7", "K8", "K10")] + ["%.1f h" % rc["t_bound"], "%.1f K/h" % m.DRIFT_K_H, "0.05 K RMS"]:
        assert fig in proc, "the procedure lacks %s" % fig
    for words in ("P = the heaters + the fans", "Authorisation to perform", "coordinator's check", "**inconclusive**", "No temperature requirement is relaxed"):
        assert words in proc, "the procedure lacks %r" % words
    readme = open(os.path.join(REC, "README.md"), encoding="utf-8").read()
    assert "section 11 the thermal reconciliation, section 12 the fix round" in readme and "section 13 prints the predicates" in readme
    assert "v2/vendor/rittal/held/" in readme


def t_the_fix_round_of_the_layer4_review():
    """astra-check-l4close-1's B3, B4 and B7 (the record's section 17, the .out's section 12)."""
    import math
    R = _R()
    m = _CACHE["M"]
    pm, br, T, hr, rc = R["pm"], R["br"], R["T"], R["hr"], R["rc"]
    for key in ("P23 ", "P24 ", "P25 "):
        assert R["pred"][[p_ for p_ in R["pred"] if p_.startswith(key)][0]], key
    md = {m_["id"]: m_ for m_ in pm["modes"]}
    assert list(md) == ["M%d" % i for i in range(1, 10)]
    k = {x[0]: x for x in rc["conds"]}
    # B3: no absolute rating decides a line; the governing line is the tightest; option C moves the heat stage to the hot stop
    for m_ in pm["modes"]:
        assert abs(m_["Q"] - sum(v for _k, v in m_["heat"])) < 1e-12
        for o in m.OPTIONS:
            b = m_["by"][o]
            assert all("ABSOLUTE" not in x["cat"] for x in b["lines"]) and all("ABSOLUTE" in s[1] for s in b["screens"])
            assert b["gov"]["g"] == max(x["g"] for x in b["lines"]) and b["stated"]["g"] <= b["gov"]["g"]
    th = pm["th"]
    assert (th["h1"], th["c1_air"], th["c1_cell"], th["t3"], th["t4"], th["otc"], th["chg"], th["dis"]) == (56.5, 50.0, 55.0, 42.0, 43.0, 44.0, 45.0, 60.0)
    assert (th["sgp4"], th["sgp5"]) == (50.0, 55.0)
    for i_ in ("M1", "M2", "M3", "M4"):
        assert md[i_]["by"]["as ruled"]["gov"]["short"] == "the SGP41's Table 4" and abs(md[i_]["by"]["as ruled"]["gov"]["t"] - 50.0) < 1e-12
        for o in ("C", "A", "B"):
            assert "hot stop H1" in md[i_]["by"][o]["gov"]["short"]
            assert not any("SGP41's sensing" in x["name"] for x in md[i_]["by"][o]["lines"])
    assert abs(md["M2"]["by"]["as ruled"]["gov"]["g"] - k["K2"][7]) < 1e-9 and abs(md["M2"]["Q"] - k["K1"][2]) < 1e-12
    assert abs(md["M1"]["by"]["C"]["gov"]["t"] - (56.5 - md["M1"]["pack"][1] / pm["gb"])) < 1e-12
    assert md["M5"]["by"]["C"]["gov"]["short"] == "C1's air trigger" and abs(md["M5"]["by"]["C"]["gov"]["g"] - k["K6"][7]) < 1e-9
    assert "INFERRED" in md["M6"]["by"]["C"]["gov"]["cat"] and abs(md["M6"]["by"]["C"]["stated"]["g"] - k["K9"][7]) < 1e-9
    assert math.isinf(md["M7"]["by"]["C"]["gov"]["g"]) and abs(md["M7"]["by"]["C"]["stated"]["g"] - k["K10"][7]) < 1e-9
    for i_ in ("M8", "M9"):
        assert md[i_]["by"]["C"]["gov"]["short"] == "T4 on the charging cells" and md[i_]["by"]["C"]["gov"]["g"] > md[i_]["Q"] / (42.0 - md[i_]["amb"])
    assert [p_["ids"] for p_ in pm["points"]] == [("M2", "M6"), ("M1",), ("M4",), ("M3",), ("M7",), ("M5",), ("M8", "M9")]
    # B4: input less stored less exported is the case heat; the reviewer's boundary reproduced
    cb = T["chg_prof"]
    assert abs(cb["p_in"] - cb["stored"] - cb["exported"] - cb["heat"]) < 1e-12 and abs(sum(cb["parts"].values()) - cb["heat"]) < 1e-12
    assert abs(cb["heat"] - 50.04367) < 5e-5 and abs(cb["parts"]["supply"] - 3.17382) < 5e-5 and abs(cb["parts"]["charge"] - 3.44629) < 5e-5
    rows = pm["b4"]["rows"]
    assert abs(rows[0][2] - 1.7376) < 5e-5 and abs(rows[2][2] - 2.1115) < 5e-5 and abs(rows[0][3] - 1.8135) < 5e-4 and abs(rows[2][3] - 2.2222) < 5e-4
    assert abs(T["charge_extra"] - cb["parts"]["charge"]) < 1e-12, "E3-O's charge with the pack outside: the charge path only"
    assert abs(md["M8"]["Q"] - hr["q_chg"]) < 1e-12 and abs(k["K7"][2] - hr["q_chg"]) < 1e-12
    # B7: the run coupled to C1
    assert abs(br["rev"][0][1] - 2.063) < 5e-3 and abs(br["rev"][1][1] - 2.151) < 5e-3 and abs(br["rev"][0][2] - 54.47) < 0.02
    b0 = br["runs"][0]
    assert b0["t_c1"] < br["t_energy"] < b0["t_end"] and not any(r_["hot_stop"] for r_ in br["runs"])
    assert br["g_full"][0][1] > br["g_full"][1][1] and abs(br["t_energy"] - 2.52) < 5e-3
    out = open(OUT, encoding="utf-8").read()
    page = open(PAGE, encoding="utf-8").read()
    proc = open(os.path.join(REC, "T-H1-PROCEDURE-DRAFT.md"), encoding="utf-8").read()
    for h in ("12 THE FIX ROUND OF THE LAYER 4 REVIEW", "12a B3, THE SGP41 AND OPTION C, RESTATED.", "12b B4, THE CHARGING HEAT AS A BALANCE",
              "12c B7, THE BATTERY-ONLY RUN COUPLED TO C1", "12d THE BENCH POINTS", "CORRECTED in the fix round (12a"):
        assert h in out, "the .out lacks %r" % h
    assert "A +55 C inside-air limit EXISTS" not in out and "switches the sensor off at a 54.0 C reading" in out
    assert "## 17. The fix round of the Layer 4 review" in page and all("### 17.%d " % i in page for i in range(1, 9))
    figs = []
    for m_ in pm["modes"]:
        for o in ("as ruled", "C"):
            b = m_["by"][o]
            if math.isfinite(b["gov"]["g"]):
                figs.append("%.3f W/K" % b["gov"]["g"])
                figs.append("%.3f W/K" % b["read"])
    figs += ["%.3f" % cb["p_in"], "%.3f" % cb["stored"], "%.3f W" % cb["heat"], "%.3f W" % hr["q_chg"]]
    figs += ["%.4f W/K" % r_[2] for r_ in rows] + ["%.4f W/K" % r_[3] for r_ in rows]
    figs += ["%.3f h" % br["rev"][0][1], "%.3f h" % br["rev"][1][1], "%.2f C" % br["rev"][0][2], "%.2f h" % b0["t_c1"], "%.2f h" % b0["t_end"],
             "%.3f W/K" % br["g_full"][0][1], "%.3f W/K" % br["g_full"][1][1]]
    for fig in figs:
        assert fig in page and fig in out, "the figure %s is not on both the page and the .out" % fig
    for pt in pm["points"]:
        for i_, o, sh, g_, rd, sh2, g2, rd2 in pt["reads"]:
            if math.isfinite(rd):
                assert "%.3f W/K" % rd in proc, "the procedure lacks %s's reading %.3f" % (i_, rd)
    for words in ("### 4a. The transient point", "energy-equivalent end of the run", "M3 and M4, closed for them", "What this test closes"):
        assert words in proc, "the procedure lacks %r" % words
    assert "energy-only" in page and "2.52 to 2.95 h" in page


def t_the_outside_capacity_and_the_three_classes():
    """The addendum to the fix round (the record's 17.9, the .out's 12e): every line against the MODELLED outside capacity with a zero
    inside resistance, bare and with the combined route; a line is over the model only where no coefficient end in the held ranges
    carries it, and then it is put in a named category by its own property (the review of the provisional fixes, L4-F04): a MISSING
    STORAGE QUALIFICATION when its limit is an operating row INFERRED to cover the part unpowered, a DEMONSTRATED CONFLICT only when
    every admitted arrangement has a measured local temperature over the limit or a bound says none can meet it (the recheck's
    discrepancy 6: one arrangement's failure is a MEASURED SHORTFALL OF ONE ARRANGEMENT), else a MODELLED SHORTFALL OF THE ANALYSED
    ARRANGEMENT; the rule and the soak specification (the claimed +70 C at the glass, the required durations) are on the page and the .out."""
    import math
    R = _R()
    m = _CACHE["M"]
    cp, cb = R["cap"], R["cb"]
    assert R["pred"][[p_ for p_ in R["pred"] if p_.startswith("P26 ")][0]]
    geo = cb["geo"]
    # a zero inside resistance passes more than the 50 m/s inside flow section 9 had called the cap
    assert cp["check9"][0] > cb["cap"]["E3-O"] + 0.2 and cp["check9"][2] > cb["cap"]["E5"] + 0.2
    assert cp["check9"][0] > R["ap"]["c"]["g_e3o"] > cb["cap"]["E3-O"], "E3-O's line lies under the capacity proper"
    # the capacity grows with the route, the optimistic ends and the rise; the closed case passes less than the open one
    c1 = m.outside_cap(40.0, 10.0, cb["cons"], geo, "open")["g"]
    assert c1 < m.outside_cap(40.0, 20.0, cb["cons"], geo, "open")["g"] and c1 > m.outside_cap(40.0, 10.0, cb["cons"], geo, "closed")["g"]
    for e in cp["lines"]:
        assert e["route"][0] >= e["bare"][0] - 1e-9 and e["bare"][1] >= e["bare"][0] and e["route"][1] >= e["route"][0]
        need = e["line"]["g"]
        if e["cls"] == "over":
            assert (not math.isfinite(need)) or (need > e["route"][1] and abs(e["short_w"] - (e["Q"] - e["route"][1] * e["rise"])) < 1e-9)
            want = m.CAT_STORE if "INFERRED to cover it unpowered" in e["line"]["cat"] else m.CAT_MODEL
            assert e["cat_over"] == want, (e["mode"], e["cat_over"])
        else:
            assert e["cat_over"] is None
        if e["cls"] == "ii":
            assert e["bare"][1] < need <= e["route"][1]
        elif e["cls"] == "i":
            assert need <= e["bare"][1]
        if e["lid"] == "closed":
            assert e["route"] == e["bare"], "the route is not credited with the lid closed"
    over = sorted(set((e["mode"], e["line"]["short"], e["cat_over"]) for e in cp["lines"] if e["cls"] == "over"))
    assert over == [("M3", "the SGP41's Table 4", m.CAT_MODEL), ("M4", "the SGP41's Table 4", m.CAT_MODEL),
                    ("M6", "the EPAPER's +60 C", m.CAT_STORE), ("M7", "the EPAPER's +60 C", m.CAT_STORE)]
    # no conflict is demonstrated while nothing is measured; one arrangement's measured failure is that arrangement's shortfall; the
    # measured failure of every admitted arrangement, or a bound that none can meet the limit, makes a conflict; a reading under the
    # limit changes nothing; an arrangement the design does not admit is refused
    assert m.MEASURED_LOCAL == () and m.NO_ARRANGEMENT_BOUND == () and cp["conflict"] == []
    assert len(m.ADMITTED_ARRANGEMENTS) == 2 and "relocated" in m.ADMITTED_ARRANGEMENTS[1]
    e3 = [e for e in cp["lines"] if e["mode"] == "M3" and e["cls"] == "over"][0]
    lim, sh = e3["line"]["t"], e3["line"]["short"]
    A0, A1 = m.ADMITTED_ARRANGEMENTS
    assert m.over_category(e3, [("M3", sh, lim + 1.0, A0)]) == m.CAT_MEASURED
    assert m.over_category(e3, [("M3", sh, lim + 1.0, A1)]) == m.CAT_MEASURED
    assert m.over_category(e3, [("M3", sh, lim + 1.0, A0), ("M3", sh, lim - 1.0, A1)]) == m.CAT_MEASURED
    assert m.over_category(e3, [("M3", sh, lim + 1.0, A0), ("M3", sh, lim + 1.0, A1)]) == m.CAT_CONFLICT
    assert m.over_category(e3, [], [("M3", sh)]) == m.CAT_CONFLICT
    assert m.over_category(e3, [("M3", sh, lim - 1.0, A0)]) == m.CAT_MODEL
    assert m.over_category(e3, [("M4", sh, lim + 1.0, A0), ("M4", sh, lim + 1.0, A1)]) == m.CAT_MODEL, "another mode's readings"
    try:
        m.over_category(e3, [("M3", sh, lim + 1.0, "the route fitted")])
        raise AssertionError("an arrangement the design does not admit was accepted")
    except ValueError:
        pass
    for f_ in (open(PAGE, encoding="utf-8").read(), open(OUT, encoding="utf-8").read()):
        flat = " ".join(f_.split())
        assert m.CONFLICT_RULE in flat and m.SOAK_SPEC in flat, "the rule or the soak specification is not stated as the script holds it"
        assert "a line enters it only on a measured local temperature over a mandatory limit with the route fitted" not in flat
        assert "only if a measurement demonstrates the conflict" not in flat and "only when a measurement demonstrates the conflict" not in flat
        assert "only if the conflict is demonstrated" not in flat and "at the mode's temperature, its function read back" not in flat
    assert all(e["cls"] == "i" for e in cp["lines"] if "hot stop H1" in e["line"]["short"])
    assert all(a_ < b_ < 40.0 for a_, b_ in cp["ceil_sgp"].values()), "the SGP41's closed-lid ceilings lie under +40 C at both ends"
    assert cp["epaper"]["M7"]["need"] is None and cp["epaper"]["M6"]["need"] < cp["epaper"]["M6"]["need_hi"] < 5.417
    out = open(OUT, encoding="utf-8").read()
    page = open(PAGE, encoding="utf-8").read()
    proc = open(os.path.join(REC, "T-H1-PROCEDURE-DRAFT.md"), encoding="utf-8").read()
    assert "12e THE OUTSIDE CAPACITY" in out and "### 17.9 The outside capacity" in page and "What a reading can pass at all" in proc
    figs = ["%.3f" % cp["check9"][0], "%.3f" % cp["check9"][2], "%.3f W/K" % cp["k1"][0]]
    for e in cp["lines"]:
        if e["cls"] == "over" and math.isfinite(e["short_g"]):
            figs += ["%.3f W/K" % e["short_g"], "%.3f W" % e["short_w"]]
    figs += ["+%.1f" % x for v in cp["ceil_sgp"].values() for x in v] + ["%.3f W/K" % cp["epaper"]["M6"]["need"], "%.3f W/K" % cp["epaper"]["M6"]["need_hi"]]
    for fig in figs:
        assert fig in page and fig in out, "the figure %s is not on both the page and the .out" % fig
    for e in cp["lines"]:
        if math.isfinite(e["line"]["g"]):
            assert "%.3f / %.3f" % e["bare"] in page, "the page lacks %s's bare capacity" % e["mode"]
    # the categories are named on both, the old category is gone and no line is called one no reading can pass
    for f_ in (page, out, proc):
        assert "class (iii)" not in f_ and "(iii)" not in f_, "the withdrawn category"
        assert "no measurement can pass it:" not in f_ and "no point here can pass" not in f_
    for name in (m.CAT_MODEL, m.CAT_STORE, m.CAT_CONFLICT):
        assert name in page and name in out, name


def t_both_checks_are_filed_and_listed():
    readme = open(os.path.join(REC, "README.md"), encoding="utf-8").read()
    for n_, job in ((1, "cx31-l4e12-check"), (2, "cx32-l4e12-recheck")):
        p = os.path.join(REC, "checks", "astra-check-l4e12-%d.md" % n_)
        need(p, "the filed check %d" % n_)
        t = open(p, encoding="utf-8").read()
        assert t.startswith("accepted: no\n") and "`%s`" % job in t and "## Blocking discrepancies" in t
        assert "checks/astra-check-l4e12-%d.md" % n_ in readme
