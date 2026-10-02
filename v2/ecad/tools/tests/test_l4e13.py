"""Layer 4 task L4-E13 (MESHSAT-1357, 2 October 2026; v2/docs/records/l4e13/): U-03, a panel whose open-circuit voltage is
bounded at the coldest operating temperature inside REQ-016's window, by its maker's document (route 1) or by the
measurement of one identified unit (route 2, PANEL-ACC), with the disturbance check judged apart from the window, held as
predicates on what l4e13_panel.py computes and prints.

The predicates: the committed l4e13_panel.out is what the script prints and every input is pinned; REQ-016's limits and
REQ-024's coldest temperature are read from the registry, not typed, and the requirement admits no series element in place of
the panel's own open circuit; the energy method is the replay's (its record printed in-process, its trace and day sums and
L4-E7's A1 and A2 rows reproduced, the rated unit's corner trace among them); THE WINDOW carries no irradiance term (A-1 is
Vm20 + U_V, route 1 is each maker's band top at -20 C and 1000 W/m2, recomputed here in closed form, the scenario and the
extrapolation told apart, and a band the maker does not print is never invented); the maker-route windows take the higher
floor and the stricter ceiling; THE DISTURBANCE CHECK's threshold follows from junction physics for n 2 and n 3, the coldest
cells are shown to be the worst case and the typical unit's n stays under n_max; A-2 is measured on the conservative side
(its offsets' signs, the hold above Vmp, its lower bound from U_I and U_V through dI/dV, the floor unit on the useful-power
line); A-3 is split three ways (normal operation under L4-E7's limit, a sustained fault with the maker's quoted 1.25, the
double contingency as a component limitation); the classification admits both routes and the record says no physical unit is
accepted; the clarification drafts contact no one, are plain ASCII and ask for exactly the window the record computes; the
page agrees with the output; the held documents are not tracked and their sources are registered; no em or en dash and no
claim word in the record (a filed check is exempt from the claim words, being the collaborator's text). These are software
predicates on the record's own text and arithmetic: they establish no electrical property of any panel and accept no unit.
"""
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e13")
SCRIPT = os.path.join(REC, "l4e13_panel.py")
OUT = os.path.join(REC, "l4e13_panel.out")
PAGE = os.path.join(REC, "L4E13-PANEL.md")
CLAR = os.path.join(REC, "clarification")
FETCH = os.path.join(REC, "fetch_held_back.py")
SOURCES = os.path.join(ROOT, "v2", "vendor", "sources.txt")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}
CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)


def _M():
    if "M" not in _C:
        need(SCRIPT, "the L4-E13 record")
        need(os.path.join(ROOT, ".git"), "a git checkout (the script finds the tree by git)")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        sp = importlib.util.spec_from_file_location("l4e13_panel_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        for key, (rel, _sha) in m.PINS.items():
            if "/held/" in rel and not os.path.exists(os.path.join(ROOT, rel)):
                raise Skip("%s is held back (its fetch_held_back.py fetches it)" % rel)
        try:
            R = m.compute()
        except SystemExit as e:
            raise AssertionError("l4e13_panel.py refused (exit %s)" % e.code)
        _C.update(M=m, R=R, text=m.render(R))
    return _C["M"]


def _cands():
    _M()
    return {c["key"]: c for c in _C["R"]["cands"]}


def t_output_reproduced_byte_for_byte():
    _M()
    assert _C["text"] == open(OUT, encoding="utf-8").read(), "l4e13_panel.out is not what the script prints"


def t_every_input_is_pinned():
    m = _M()
    for key, (rel, sha) in m.PINS.items():
        assert sha and re.fullmatch(r"[0-9a-f]{64}", sha), "%s (%s) is not pinned by sha256" % (key, rel)
        got = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
        assert got == sha, "%s is not the pinned file" % rel


def t_the_requirement_is_read_not_typed():
    _M()
    R = _C["R"]
    assert (R["v_oc"], R["v_hold_req"], R["p_win"], R["entry_a"]) == (25.0, 17.6, 100.0, 10.0)
    assert R["t_cold"] == -20.0 and R["req024_range"] == ("-20", "40")
    assert not R["series_admitted"], "REQ-016's text constrains the panel's own open circuit; a series element is not admitted"
    src = open(SCRIPT, encoding="utf-8").read()
    for lit in ("= 25.0\n", "= -20.0\n", "= 17.6\n"):
        assert lit not in src, "a requirement figure is typed into the script (%r)" % lit.strip()


def t_the_energy_method_is_the_replays():
    _M()
    R = _C["R"]
    assert R["r0"], "the replay did not print its record in-process"
    assert len(R["m1"]) == 3 and all(a == b for _v, a, b in R["m1"]), R["m1"]
    assert len(R["m2"]) == 5 and all(a == b for _v, a, b in R["m2"]), R["m2"]
    assert [ak for ak, ok, _m in R["m3"] if ok] == ["A1", "A2"], "A1 and A2 on the SunPower trace differ from L4-E7's rows"


def t_the_window_carries_no_irradiance_term():
    m = _M()
    R = _C["R"]
    src = open(SCRIPT, encoding="utf-8").read()
    assert "g_max" not in src and "ln_g" not in src and "env_term" not in src, "an irradiance maximum still feeds the window"
    spr = _cands()["SPR"]
    ra, ru = R["acc"]["rated"], R["acc"]["rated_unit"]
    assert abs(ra["a1"] - (ru["vm20"] + m.SPEC_UV)) < 1e-12 and ra["a1_ok"], "A-1 is not Vm20 + U_V"
    assert abs(ru["vm20"] - max(spr["voc"] * (1 + abs(spr["beta_rel"]) * 45.0), spr["voc"] + abs(spr["beta_voc_abs"]) * 45.0)) < 1e-12
    assert abs((R["v_oc"] - ra["a1"]) - 0.8495) < 1e-4, R["v_oc"] - ra["a1"]
    A = R["acc"]
    assert abs(A["vm20_ceil"] + m.SPEC_UV - 25.0) < 1e-9 and A["k_floor"] < 1.0 <= A["k_ceil"] and A["feasible"]
    assert "WITHDRAWN as a decision input" in _C["text"] and R["g_t"] > 2000.0     # the old level survives only as A-3(c)'s


def t_route1_bounds_are_read_in_the_window_from_the_printed_band():
    c = _cands()
    R = _C["R"]
    dt = 25.0 - R["t_cold"]
    spr, bgv, sbx = c["SPR"], c["BGV"], c["SBX"]
    q = spr["qual_pct"]
    assert q == 0.10 and abs(spr["band"][1] - 1 / 0.9) < 1e-12 and abs(spr["band"][0] - 1 / 1.1) < 1e-12
    beta = abs(spr["beta_voc_abs"])
    want = {spr["voc"] / 0.9 * (1 + beta / spr["voc"] * dt), spr["voc"] / 0.9 + beta * dt, spr["voc"] * 1.1 + beta * dt}
    got = {v for _l, v in spr["readings"]}
    assert len(got) == 3 and all(min(abs(g - w) for w in want) < 1e-9 for g in got), (got, want)
    labs = [l_ for l_, _v in spr["readings"]]
    assert labs[0].startswith("SCENARIO") and labs[1].startswith("EXTRAPOLATION"), "the scenario and the extrapolation are not told apart"
    assert abs(spr["bound"] - max(want)) < 1e-9 and abs(spr["bound"] - 26.722778) < 1e-6 and not spr["bounded"]
    assert bgv["band"] == (0.95, 1.10) and abs(bgv["bound"] - bgv["voc"] * 1.10 * (1 + abs(bgv["beta_voc"]) * dt)) < 1e-9 and bgv["bounded"]
    assert sbx["band"] is None and sbx["bound"] is None and not sbx["bounded"] and not sbx["readings"]
    assert R["bounded_any"] == ["BGV"] and not R["qualifying"], "route 1 must close nothing: BougeRV bounded but not held"
    assert not bgv["reach_cond_upper"] and bgv["voc_noon_nom"] < R["hold_cond"][1]


def t_a_band_the_maker_does_not_print_is_not_invented():
    c = _cands()
    sbx = c["SBX"]
    assert not sbx["voc_tol_printed"], "the Solbian sheet is read as printing no Voc tolerance"
    assert sbx["p_tol"] == (0.0, 0.05), "the sheet's only tolerance is on Pmax"
    assert abs(sbx["voc_cold_nom"] - sbx["voc"] * (1 + abs(sbx["beta_voc"]) * 45.0)) < 1e-9
    assert abs(sbx["tol_needed_up"] - (25.0 / sbx["voc_cold_nom"] - 1.0)) < 1e-12
    out = _C["text"]
    assert "on the nominal model only (no band printed)" in out and "NOMINAL (no Isc band printed)" in out
    assert "not this maker's instruction" in out, "the 1.25 factor's transfer to Solbian is not explicit"


def t_the_maker_route_windows_take_the_higher_floor_and_the_stricter_ceiling():
    c = _cands()
    R = _C["R"]
    up = R["hold_cond"][1]
    for cc in c.values():
        dv = abs(cc["beta_rel"]) * cc["voc"] * 45.0
        assert abs(cc["maker_ceiling"] - cc["voc"] * min(25.0 / cc["voc_cold_nom"], (25.0 - dv) / cc["voc"])) < 1e-9
        assert abs(cc["voc_noon_nom"] * cc["k_reach_cond"] - up) < 1e-9
        assert cc["maker_floor"] == cc["voc"] * max(cc["k_reach_cond"], cc["k_reach_abs"] or 0.0)
    spr = c["SPR"]
    assert spr["k_reach_abs"] > spr["k_reach_cond"] and abs(spr["maker_floor"] - 20.118679) < 2e-4, spr["maker_floor"]
    assert abs(spr["maker_ceiling"] - 22.244860) < 2e-4, spr["maker_ceiling"]


def t_the_disturbance_threshold_follows_from_junction_physics():
    m = _M()
    R = _C["R"]
    D = R["dist"]
    assert (R["d4_vr"], R["d4_ir_ua"], R["cap_v"]) == (28.0, 1.0, 35.0) and R["d4_row"][:3] == (28.0, 31.10, 34.40)
    assert R["d4_alpha_t"] == 0.001 and abs(R["d4_vbr_cold"] - 31.10 * (1 - 0.001 * 45.0)) < 1e-9
    assert D["ns"] == 32 and abs(D["vt_cold"] - 253.15 * 1.380649e-23 / 1.602176634e-19) < 1e-9
    assert abs(D["dv"] - (28.0 - 25.0)) < 1e-12
    rows = {round(r[1], 4): r for r in D["rows"]}
    for n in (2.0, 3.0):
        g = 1000.0 * math.exp(3.0 / (n * 32 * D["vt_cold"]))
        assert abs(rows[n][3] - g) < 1e-6 * g, (n, rows[n][3], g)
    assert 8500.0 < rows[2.0][3] < 8650.0 and 4100.0 < rows[3.0][3] < 4300.0
    assert abs(rows[2.0][4] - rows[2.0][3] / R["e0_max"]) < 1e-12 and rows[2.0][4] > 6.0
    assert m.N_MAX == 2.0 and D["g_thr_dec"] == rows[2.0][3] and D["implied"]
    assert D["beta_mag_min"] > D["dlog_dt_max"] and abs(D["dlog_dt_max"] - 3.0 / 253.15) < 1e-12, "the coldest cells must be the worst case"
    assert D["n_meas_typ_upper"] <= m.N_MAX, "the typical unit's n with its uncertainty must stay under n_max"
    out = " ".join(_C["text"].split())
    assert "MODELLING_ASSUMPTION" in out and "no irradiance maximum is a decision input" in out and "re-judged" in out


def t_a2_is_measured_on_the_conservative_side():
    m = _M()
    R = _C["R"]
    g, t = R["a2_corner"]
    assert abs(g - R["g_noon"] * (1 - m.SPEC_UG)) < 1e-12 and abs(t - (R["tc_noon"] + m.SPEC_UTC)) < 1e-12
    for sg in (R["a2_signs_rated"], R["a2_signs_floor"]):
        assert sg["di_dg"] > 0.0 and sg["di_dt"] < 0.0, "an offset is not conservative"
        assert sg["vmp"] < R["hold_cond"][1] and sg["vmp_noon"] < R["hold_cond"][1], "the hold is not above Vmp"
    a2 = R["acc"]["rated"]["a2"]
    vh = R["hold_cond"][1]
    assert abs(a2["p"] - vh * a2["i"]) < 1e-12 and a2["didv"] < 0.0
    assert abs(a2["u_p"] - vh * math.sqrt((m.SPEC_UI * a2["i"]) ** 2 + (a2["didv"] * m.SPEC_UV) ** 2)) < 1e-12
    assert a2["p_low"] == a2["p"] - a2["u_p"] and a2["p_low"] > R["p_use"] and a2["ok"]
    assert abs(R["acc"]["floor"]["a2"]["p_low"] - R["p_use"]) < 1e-6, "the floor unit is not on the useful-power line"


def t_a3_is_split_three_ways():
    m = _M()
    R = _C["R"]
    ra = R["acc"]["rated"]
    sc = R["stack_c"]
    assert abs(R["i_norm_max"] - max(sc[0] / sc[1], sc[2] / sc[3])) < 1e-12 and ra["a3a"] < 10.0 and ra["a3a_ok"]
    spr = _cands()["SPR"]
    isc_hot = spr["isc"] * (1 + m.SPEC_UI) * (1 + spr["alpha_isc_abs"] / spr["isc"] * 45.0)
    assert abs(ra["isc_hot"] - isc_hot) < 1e-12 and abs(ra["a3b"] - 1.25 * isc_hot) < 1e-12 and ra["a3b"] <= 10.0
    assert abs(ra["a3c"] - isc_hot * R["g_t"] / 1000.0) < 1e-12 and ra["a3c"] > 10.0
    assert "multiplied by a factor of 1.25 when determining component voltage ratings, conductor capacities, fuse sizes" in R["clause_quote"]
    assert R["vh_rating"] == "Current rating: 10 A AC/DC" and not R["vh_overload"]
    assert abs(R["acc"]["g_20a"] - 20.0 / isc_hot * 1000.0) < 1e-9
    out = " ".join(_C["text"].split())
    assert "COMPONENT_LIMITATION" in out and "A-3(c)" in out and "a design level, not a claimed maximum" in out


def t_a3a_and_a4_rest_on_l4e7r_regulation_and_backstop():
    m = _M()
    R = _C["R"]
    r7 = R["l4e7r"]
    rel, _sha = m.PINS["l4e7_out"]
    o7 = " ".join(open(os.path.join(ROOT, rel), encoding="utf-8").read().split())
    # the figures are read from L4-E7R's accepted output, not typed
    for v in (r7["reg"][0], r7["reg"][2], r7["coord"][1], r7["coord"][2], r7["trip"][0], r7["own"][0], r7["dec"][0],
              r7["dec"][1], r7["resp"][0], r7["crit"][0]):
        assert v in o7, v
    # the kept 3.9870 A stays the conservative upper bound: above the backstop's highest trip and the regulation's highest
    assert R["i_reg_nom"] < R["i_reg_hi"] < R["i_trip_max"] < R["i_norm_max"] < 10.0
    assert R["i_trip_min"] < R["i_trip_max"] and R["i_reg_hi"] < R["i_trip_min"]
    # the conditioned upper corner's energy rows are below every limit L4-E7R draws, so they do not move
    assert R["corner_unmoved"] and R["corner_i"][0] < R["i_reg_nom"]
    out = " ".join(_C["text"].split())
    page = " ".join(open(PAGE, encoding="utf-8").read().split())
    for s in ("RIMON_IN %s" % r7["reg"][0], "%.4f A" % R["i_reg_hi"], "%.4f A" % R["i_trip_max"], "%.4f A" % R["i_trip_min"],
              "%.4f A" % R["i_norm_max"], "%s W" % r7["own"][0], "%s W" % r7["dec"][0], "margin %s W" % r7["dec"][1],
              "CONDITIONAL on G_CM (break-even %s %%)" % r7["dec"][2], "(break-even %s mA)" % r7["dec"][3], r7["crit"][0],
              "The backstop does not limit", "turns the stage off"):
        assert s.lower() in out.lower() and s.lower() in page.lower(), s
    assert "%s Wh" % r7["energy"][1] in out and "%s Wh" % r7["energy"][1] in page


def t_the_classification_admits_both_routes():
    m = _M()
    R = _C["R"]
    assert m.classify(True, False).startswith("DOWNSTREAM PURCHASE") and m.classify(True, True).startswith("DOWNSTREAM PURCHASE")
    assert m.classify(False, True) == "CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC)"
    assert m.classify(False, False).startswith("OPEN")
    assert R["decision"] == m.classify(R["route1"], R["route2"])
    assert not R["route1"] and R["route2"] and R["decision"] == "CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC)"
    out = " ".join(_C["text"].split())
    assert "NO PHYSICAL UNIT IS ACCEPTED" in out and "the owner's actions" in out
    others = R["acc_cands"]
    assert not others["BGV"]["a2_ok"] and not others["SBX"]["a3b_ok"], "the unit's choice is not argued"
    assert [r[0] for r in R["m4"] if r[1]] == ["A1", "A2"], "the rated unit's corner trace is not L4-E7's row"
    assert all(r[2] > 0.0 for r in R["acc_runs"]) and len(R["acc_runs"]) == 3


def t_the_hold_predicate_follows_from_the_rows():
    _M()
    R = _C["R"]
    up, upt = R["hold_cond"][1], R["hold_typ"][2]
    assert (round(up, 3), round(upt, 3)) == (18.813, 18.221) and R["hold_typ"][1] == 17.593
    for c in R["cands"]:
        assert c["reach_cond_upper"] == all(v["voc_noon"] > up for v in c["variants"])
        assert c["reach_typ_upper"] == all(v["voc_noon"] > upt for v in c["variants"])
        assert c["qualifies"] == bool(c["bounded"] and c["reach_cond_upper"] and c["portable"]), c["key"]
        if c["band_ratio"] is not None and c["band_ratio"] > c["w_cond"] + 1e-12:
            assert not c["qualifies"], "%s: a band wider than the window's ratio cannot be both bounded and held" % c["key"]
        assert abs(c["w_cond"] - c["k_bound"] / c["k_reach_cond"]) < 1e-12
    c = _cands()
    assert not c["SPR"]["variants"][1]["reach"][up] and c["SPR"]["variants"][0]["reach"][up]


def t_power_and_entry_rows_are_consistent():
    c = _cands()
    for cc in c.values():
        assert cc["p_lim_max"] <= 25.0 * _C["R"]["i_set"] + 1e-9, "a limited operating point above the 25 V corner's power"
        assert abs(cc["isc_hot_clause"] - 1.25 * cc["isc_hot"]) < 1e-12
        assert cc["portable"] and cc["mass"] <= _C["M"].PORTABLE_KG
    assert c["SBX"]["isc_hot_clause"] > 10.0 >= c["SPR"]["isc_hot_clause"] and c["BGV"]["isc_hot_clause"] <= 10.0
    for key, lab, tot, rr, tr in _C["R"]["runs"]:
        assert max(tr) <= 100.0 and abs(sum(tr) - tot) < 0.05 * len(tr), (key, lab)
        assert set(rr) == {"A1", "A2"}


def t_clarification_drafts_contact_no_one_and_ask_for_the_computed_window():
    c = _cands()
    names = sorted(os.listdir(need(CLAR, "the clarification drafts")))
    assert names == ["solbian-sx-156.txt", "sunpower-spr-e-flex-100.txt"], names
    for nm, key in (("sunpower-spr-e-flex-100.txt", "SPR"), ("solbian-sx-156.txt", "SBX")):
        t = open(os.path.join(CLAR, nm), encoding="utf-8").read()
        assert t.startswith("DRAFT FOR THE OWNER TO SEND.") and "contacts no outside party" in t, nm
        assert all(ord(ch) < 128 for ch in t) and chr(0x2013) not in t and chr(0x2014) not in t, "%s is not plain ASCII" % nm
        f = " ".join(t.split())
        assert "warrant" in f and "supporting evidence" in f and "production guarantee" in f, nm
        m = re.search(r"between (\d+\.\d+) V and (\d+\.\d+) V", f)
        assert m, "%s names no window" % nm
        lo, hi = float(m.group(1)), float(m.group(2))
        assert c[key]["maker_floor"] <= lo < hi <= c[key]["maker_ceiling"], (nm, lo, hi, c[key]["maker_floor"], c[key]["maker_ceiling"])
        assert ("%.2f V" % c[key]["voc_cold_nom"]) in f and "1000 W/m2" in f, "%s does not state the window" % nm
        assert "2111" not in f, "%s still carries the withdrawn irradiance" % nm


def t_the_page_agrees_with_the_output():
    c = _cands()
    R = _C["R"]
    A = R["acc"]
    t = open(PAGE, encoding="utf-8").read()
    f = " ".join(t.split())
    for key in ("SPR", "BGV"):
        assert "**%.3f V**" % c[key]["bound"] in t, "the page does not carry %s's bound in the window" % key
    body = t.split("## The first check's items and their changes")[0]          # the mapping tables quote the old figures
    assert "27.475" not in body and "25.042" not in body, "a band-top-over-envelope figure is still on the page"
    assert "%.6f W" % R["p_use"] in f and "%.4f V" % A["rated"]["a1"] in f and "%.4f V" % (R["v_oc"] - A["rated"]["a1"]) in f
    assert "%.3f V to %.3f V" % (A["v25_floor"], A["v25_ceil"]) in f and "%.3f V" % A["vm20_ceil"] in f
    assert "%.4f W" % A["rated"]["a2"]["p_low"] in f
    for v in (A["rated"]["a3a"], A["rated"]["a3b"], A["rated"]["a3c"]):
        assert "%.4f A" % v in f, v
    D = R["dist"]
    for r in D["rows"]:
        assert "%.0f W/m2" % r[3] in f and "%.2f" % r[4] in f, r
    for lab, vh, tot, nl, zh, noon_w, rr, tr in R["acc_runs"]:
        assert "%.1f Wh" % tot in f, lab
    qrow = [ln for ln in t.split("\n") if ln.startswith("| **Route 1")]
    assert len(qrow) == 1 and qrow[0].count("| no") == 3 and not R["qualifying"]
    assert R["decision"] in f and "NO PHYSICAL UNIT IS ACCEPTED" in f
    words = {14: "Fourteen", 15: "Fifteen", 13: "Thirteen"}
    assert words[len(R["screen"]["rows"])] + " makers' documents" in t and "search history" in f
    for key in ("SPR", "SBX", "BGV"):
        assert "%.4f to %.4f V" % (c[key]["maker_floor"], c[key]["maker_ceiling"]) in f, key
    win = "%.4f to %.4f" % (min(cc["w_cond"] for cc in c.values()), max(cc["w_cond"] for cc in c.values()))
    assert win in f, win
    assert "checks/astra-check-l4e13-2.md" in f and "The recheck's items and their changes" in f


def t_held_documents_are_not_tracked_and_their_sources_are_registered():
    m = _M()
    r = subprocess.run(["git", "-C", ROOT, "ls-files", "v2/vendor/solar/held"], capture_output=True, text=True)
    assert r.returncode == 0 and not r.stdout.strip(), "a held-back document is tracked: %s" % r.stdout[:200]
    src = open(SOURCES, encoding="utf-8").read()
    for key in ("sbx_ds", "bgv_page", "enh"):
        rel = m.PINS[key][0]
        line = [ln for ln in src.split("\n") if ln.startswith(rel.replace("v2/vendor/", "") + " ")]
        assert len(line) == 1, "%s has no line in sources.txt" % rel
        if key == "sbx_ds":
            assert m.PINS[key][1] in line[0] and "HELD BACK, NOT FILED" in line[0]
        elif key == "enh":
            assert "837d474b0707c34a96a1a354e174e913640bae3b2cf843daaa38cc08ca742688" in line[0] and "CC BY 4.0" in line[0]
        else:
            assert "ffc8cf990599ab0b4463648878a5cc790db76ec503660ff9948df8bf79c28439" in line[0] and "FILED" in line[0]
    fsrc = open(FETCH, encoding="utf-8").read()
    assert m.PINS["sbx_ds"][1] in fsrc and m.PINS["sbx_ds"][0] in fsrc, "fetch_held_back.py does not fetch the pinned sheet"
    scr = json.load(open(os.path.join(ROOT, m.PINS["screen"][0]), encoding="utf-8"))
    for row in scr["rows"]:
        assert re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) and row["url"].startswith("http") and row["why_not"], row["model"]


def t_no_dashes_and_no_claim_words_in_the_record():
    files = [os.path.join(dp, f) for dp, _dn, fs in os.walk(REC) for f in fs if f.endswith((".md", ".py", ".out", ".txt", ".json"))
             and os.path.basename(dp) != "checks"]          # a filed check is the collaborator's text, byte for byte
    files += [os.path.join(ROOT, "v2", "vendor", "solar", "bougerv-sp001-100w-n-type-foldable-product-page-2026-10-02.md"),
              os.path.join(ROOT, "v2", "vendor", "solar", "irradiance-enhancement-sources-2026-10-02.md"),
              os.path.abspath(__file__)]
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "%s carries an em or en dash" % os.path.relpath(p, ROOT)
        if p != os.path.abspath(__file__):
            hit = CLAIM.search(t)
            assert not hit, "%s carries the claim word %r" % (os.path.relpath(p, ROOT), hit.group(0))
