"""Layer 4 task L4-E10 (MESHSAT-1357, 2 October 2026; v2/docs/records/l4e10/): FEA-008, the cell and thermal design of the
battery path, held as predicates on properties of what l4e10_cell_thermal.py computes.

The predicates: the thermal records it rests on are reproduced byte for byte and the committed .out is what the script
prints; every LO row of Layer 3's cell modes table has a decision of a known kind with its complete acceptance; a row
recorded as closed or free of collision rests on MAKER or bounded MODELED evidence only, and a row resting on INFERRED or
ASSUMPTION figures is never recorded as closed; no cell change is recorded as taken, and any cell route names the owner's
approval; an owner decision is recorded only where every route of a row is rejected, and an open row keeps a route that is
not; the collisions are recomputed here in closed form and agree with Layer 3's table; LO-01a's three thresholds (the
rating, FEA-008's +59 C abort, the complete pass line) are recomputed here and ordered; the coupling measure's figures
are recomputed from the W4 constants and shown not to meet the air criteria; LO-01g's pack-only heating and the two-node
storage lag are recomputed in closed form; the screen covers every row and every TEST-PLAN exposure it maps; the cooler's
balance conserves energy at every equilibrium it reports; the comparison holds at most three complete approaches judged
on every row, recommends the least complex one with no row rejected and no added energy storage, and its conditioned
corner, margins and U2 shift are recomputed here; the primary battery stays a proposal under D-06; E5's profile is Method
507.6's; both checks are filed byte for byte from their results; the page's figures are the .out's; the held files are
ignored by git and pinned alike in the script and the fetcher; no dash or claim word is written. Nothing here writes
into the tree.
"""
import ast
import hashlib
import importlib.util
import math
import os
import re
import shutil
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e10")
SCRIPT = os.path.join(REC, "l4e10_cell_thermal.py")
OUT = os.path.join(REC, "l4e10_cell_thermal.out")
PAGE = os.path.join(REC, "L4E10-CELL-THERMAL.md")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_CACHE = {}
HELD = ("v2/vendor/battery/held/samsung-inr18650-30q6-v1.0-2020.pdf", "v2/vendor/battery/held/samsung-inr18650-30q-v1.0-2015.pdf",
        "v2/vendor/battery/held/samsung-inr18650-30q6-draft-v0.1-2024.pdf", "v2/vendor/battery/held/lg-inr18650hg2-rev0-2014.pdf",
        "v2/vendor/battery/held/saft-lsh20-31015-2-0426.pdf", "v2/vendor/battery/held/saft-lsh20hts-31057-2-0710.pdf",
        "v2/vendor/battery/held/toshiba-scib-brochure-2020.pdf", "v2/vendor/battery/held/ultraxel-hl18650t-flyer-2025.pdf")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _R():
    if "R" not in _CACHE:
        need(SCRIPT, "the L4-E10 record")
        need(os.path.join(ROOT, ".git"), "a git checkout (the script finds the tree by git)")
        for rel in HELD:
            need(os.path.join(ROOT, rel), "a held cell specification (v2/docs/records/l4e10/fetch_held_back.py)")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        try:
            import yaml  # noqa: F401
        except ImportError:
            raise Skip("PyYAML is needed")
        m = _load("l4e10_cell_thermal_under_test", SCRIPT)
        try:
            R = m.compute()
            text = "\n".join(m.render(R)) + "\n"
        except SystemExit as e:
            raise AssertionError("l4e10_cell_thermal.py refused (exit %s)" % e.code)
        _CACHE.update(R=R, M=m, text=text)
    return _CACHE["R"]


def t_records_reproduced_and_out_is_what_the_script_prints():
    R = _R()
    for k in ("r0a", "r0b", "r0c", "r0d"):
        assert R[k] is True, "reproduction %s failed" % k
    assert _CACHE["text"].encode("utf-8") == open(OUT, "rb").read(), "the committed .out is not what the script prints"


def t_every_lo_row_has_a_decision_of_a_known_kind():
    R = _R()
    import yaml
    l3 = yaml.safe_load(open(os.path.join(ROOT, "v2/docs/handover/layer3/l3r2.yaml"), encoding="utf-8"))
    ids = sorted(m["id"] for m in l3["cell_modes"])
    assert ids == sorted(R["dec"]), "decisions %s against Layer 3's rows %s" % (sorted(R["dec"]), ids)
    kinds = {"CLOSED", "CONDITIONAL", "NO_COLLISION", "OPEN"}
    assert all(d["decision"] in kinds for d in R["dec"].values())
    assert all(d["acceptance"] for d in R["dec"].values()), "a row without its complete acceptance"
    for k in ("LO-01a", "LO-01d", "LO-01e", "LO-01f", "LO-01g", "LO-01h"):   # FEA-008's blocker rows
        assert R["dec"][k]["gap"] and R["dec"][k]["acceptance"], "%s has no gap or acceptance" % k


def t_closed_rows_rest_on_maker_or_bounded_modeled_only():
    R = _R()
    for k, d in R["dec"].items():
        assert set(d["evidence"]) <= set(R["classes"]), "%s carries an unknown class" % k
        if d["decision"] in ("CLOSED", "NO_COLLISION"):
            assert set(d["evidence"]) <= {"MAKER", "MODELED"} and d["bounded"], "%s is %s on %s" % (k, d["decision"], d["evidence"])
        if {"INFERRED", "ASSUMPTION"} & set(d["evidence"]):
            assert d["decision"] != "CLOSED", "%s is closed on INFERRED or ASSUMPTION evidence" % k


def t_no_cell_change_is_taken_without_the_owner():
    R = _R()
    for k, d in R["dec"].items():
        cc = d["cell_change"]
        if cc is not None:
            assert cc["taken"] is False and cc["owner_approval_required"] is True, "%s records a cell change as taken" % k
    page = open(PAGE, encoding="utf-8").read()
    assert "no cell change is taken" in page
    assert not re.search(r"(?<!no )cell change (is|was) taken", page.replace("No row is recorded as CLOSED, and no cell change is taken", "").replace("No cell change is taken", ""), re.I)
    b = " ".join(_CACHE["M"].later_lines(R))
    assert "approval" in b and "none proposed" not in b


def t_collisions_recomputed_in_closed_form_agree_with_layer3():
    R = _R()
    qR, pR = R["heat"]["SURVR"]
    qS, pS = R["heat"]["SURV"]
    air = 40.0 + (qR + pR) / 1.06
    assert abs(math.floor(air * 10 + 1e-9) / 10 - R["modes"]["LO-01a"]["req_c"]) < 1e-9
    assert abs(air - 60.0 - R["gaps"]["LO-01a"]) < 1e-9
    cell = air + pR / R["blk"]["h"][0] / R["blk"]["A"]
    assert abs(cell - R["a"]["cell_closed_W4_pack"]) < 1e-9 and cell > air, "the cells on the pack are not above the air by their I2R"
    lo, hi = 55.0 + (qS + pS) / 3.3, 55.0 + (qR + pR) / 1.22
    assert abs(lo - R["d"]["air_lo"]) < 1e-9 and abs(hi - R["d"]["air_hi"]) < 1e-9
    assert abs(math.floor(hi * 10 + 1e-9) / 10 - R["modes"]["LO-01d"]["req_c"]) < 1e-9
    assert abs(round(60.0 + (qS + pS) / 3.3, 2) - R["modes"]["LO-01e"]["req_c"]) < 1e-9
    assert R["gaps"]["LO-01f"] == R["modes"]["LO-01f"]["req_c"] - R["modes"]["LO-01f"]["limit_c"] == 11.0
    assert R["gaps"]["LO-01g"][0] == R["modes"]["LO-01g"]["limit_c"] - R["modes"]["LO-01g"]["req_c"] == 13.0
    assert all(v[2] for v in R["agree"].values())


def t_coupling_measure_recomputed_from_its_inputs():
    R = _R()
    w4 = {}
    tree = ast.parse(open(os.path.join(ROOT, "v2/docs/records/w4/w4-scratch-thermal.py"), encoding="utf-8").read())
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("H_OUT_WALL", "H_OUT_FLOOR", "T_OVER_K_WALL", "H_IN_FANS"):
            w4[n.targets[0].id] = ast.literal_eval(n.value)
    X, Y, Z = R["blk"]["X"], R["blk"]["Y"], R["blk"]["Z"]
    aE, aB = Y * Z, X * Y
    aI = 2 * (X * Y + X * Z + Y * Z) - aE - aB
    m = _CACHE["M"]
    gE = 1 / (R["m4b_gap_max_mm"] / 1000 / (m.K_PAD * aE) + w4["T_OVER_K_WALL"] / aE + 1 / (w4["H_OUT_WALL"][0] * aE))
    gB = 1 / (m.T_MAT / (m.K_MAT * aB) + w4["T_OVER_K_WALL"] / aB + 1 / (w4["H_OUT_FLOOR"][0] * aB))
    gI = R["blk"]["h"][1] * aI
    assert abs(gE + gB - R["worst"]["g_amb"]) < 1e-12 and abs(gI - R["worst"]["g_in"]) < 1e-12
    f = gI / (gI + gE + gB)
    assert abs(f - R["worst"]["f"]) < 1e-12 and 0 < R["best"]["f"] < f < 1
    # the two-node model reduces to pwr_budget's cell_temp with no skin path, and the measure lowers the worst corner
    assert R["meas"]["two_node_matches_record"]
    assert R["meas"]["a_pack_worst"][1] < R["a"]["cell_closed_W4_pack"]
    assert R["meas"]["a_pack_worst"][1] <= 60.0 < R["a"]["cell_closed_W4_pack"], "the measure's stated effect on LO-01a"
    # it cannot close the +55 C margin: the cells stay above H1's reading at every corner
    assert R["meas"]["d_best"][1] > R["hot"]["H1"] and R["meas"]["d_worst"][1] > 60.0
    # the cold-end cost is carried, and charging at the cold end clears the panel's hold with the existing mat
    assert R["cold"]["meas"][1] < R["cold"]["base"][1] and R["cold"]["p_h"] > 0
    assert R["cchg"]["base"][1] > R["cchg"]["hold"] and R["cchg"]["meas"][1] > R["cchg"]["hold"]


def t_screen_covers_every_row_and_judges_power_and_hold_time():
    R = _R()
    rows = R["screen"]
    assert set(r["lo"] for r in rows if r["lo"]) == set(R["dec"])
    for r in rows:
        assert r["power"] and r["gap"] and r["result"], r["id"]
        if r["zero_power"]:
            assert r["power"].startswith("zero"), r["id"]
            assert not r["result"].startswith("CREDIBLE: thermal"), "%s credits a thermal design with no power" % r["id"]
    for k in ("LO-01d", "LO-01e", "LO-01f", "LO-01g"):
        rr = [r for r in rows if r["lo"] == k]
        assert rr and all(r["result"].startswith("OPEN") and any("INCONCLUSIVE" in a for a in r["approaches"]) for r in rr), "%s's screen row" % k
    H = R["hold"]
    assert 3 * H["tau_kit_s"][1] < R["f"]["hours"] * 3600.0 and 3 * H["tau_pack_s"][1] < H["e3o_s"]
    assert max(r["Wh_prim_direct"] for r in R["selfheat"]["rows"].values()) < min(H["e_kit_cold_Wh"]), "the pack-only demand is not below the whole-kit figure"


def t_no_owner_decision_unless_every_route_is_rejected():
    R = _R()
    forced = sorted(k for k, d in R["dec"].items() if d["decision"] == "OPEN" and all(r["status"] == "REJECTED" for r in d["routes"]))
    assert R["owner_decision_required"] is bool(forced) and R["forced_rows"] == forced
    assert R["owner_decision_required"] is False, "no row has every route rejected, yet an owner decision is recorded"
    for k, d in R["dec"].items():
        if d["decision"] == "OPEN":
            assert d["routes"] and any(r["status"] == "INCONCLUSIVE" for r in d["routes"]), "%s is open with no live route" % k
            for r in d["routes"]:
                if r["status"] == "INCONCLUSIVE":
                    assert r["missing"] and r["missing"] != "none", "%s: an INCONCLUSIVE route names no missing input" % k
    lines = _CACHE["M"].later_lines(R)
    assert sum(1 for l in lines if re.match(r"^[A-Z]\. ", l)) <= 3
    assert any("requirement change" in l for l in lines) and any("fallback" in l for l in lines)
    out = open(OUT, encoding="utf-8").read()
    assert "OWNER DECISION: none is forced" in out
    assert "contradiction" not in open(PAGE, encoding="utf-8").read().replace("not a contradiction between owner requirements", "")
    assert R["meets"]["30Q6"]["LO-01h"] is False and R["meets"]["35E"]["LO-01h"] is True, "S2's year row"


def t_lo01a_thresholds_recomputed_and_ordered():
    R = _R()
    qR, pR = R["heat"]["SURVR"]
    g = R["Gblk"][0]
    assert abs((qR + pR) / (60.0 - 40.0 - pR / g) - R["gov"]["rating_pack"]) < 1e-12
    assert abs((qR + pR) / (59.0 - 40.0 - pR / g) - 1.315393) < 5e-7, "the +59 C abort's conductance"
    assert abs((qR + pR) / (56.5 - 40.0 - pR / g) - 1.529988) < 5e-7, "H1's conductance"
    sgp = (R["shore_heat"]) / (55.0 - 40.0)
    assert abs(sgp - R["gov"]["all"][4]) < 1e-12 and R["gov"]["all"][0].startswith("SGP41")
    assert R["gov"]["all"][4] > R["gov"]["fea008_pack"] > R["gov"]["rating_pack"]
    assert max(c[4] for c in R["crit"]) == R["gov"]["all"][4]
    # the coupling meets the cell criteria at the worst corner and not the air criteria
    vs = dict((n, (v, l)) for n, v, l in R["meas"]["fallback_vs"])
    assert vs["cell rating"][0] <= vs["cell rating"][1] and vs["the +59 C abort"][0] <= vs["the +59 C abort"][1]
    assert vs["SGP41 air"][0] > vs["SGP41 air"][1] and vs["F2 at the air"][0] > vs["F2 at the air"][1]
    # lid open at the bound's lowest also passes +60 C on the pack
    assert R["open_worst"]["cell_pack"] > 60.0


def t_lo01g_three_cases_on_usable_energy():
    R = _R()
    sh, H = R["selfheat"], R["hold"]
    gs = [1.0 / (1.0 / R["Gblk"][i] + 1.0 / R["Gb"]["closed_still"][i]) for i in (0, 1)]
    assert all(abs(a - b) < 1e-12 for a, b in zip(gs, sh["g_series"]))
    # a heater at the storage floor, driven direct: the series path times 13 K for 24 h
    e = [g * 13.0 * 24.0 for g in gs]
    assert abs(e[0] - sh["rows"]["slow"]["Wh_prim_direct"]) < 1e-9 and abs(e[1] - sh["rows"]["fast"]["Wh_prim_direct"]) < 1e-9
    assert abs(e[0] - 38.1) < 0.05 and abs(e[1] - 106.1) < 0.05
    # the pack-fed heater discharges the cells: its setpoint sits on the discharge side, UTD plus the published cold budget
    assert abs(sh["set_pack"] - (R["ladder"]["UTD"] + sh["budget_cold"])) < 1e-12 and sh["set_pack"] > -10.0
    # usable energy at the stored charge, recomputed: never 24 h at any corner, and no protected path in shutdown
    lim = R["S"]["35E_11"]
    for cf, row, dur in ((sh["cold_f"][0], "fast", sh["dur_h_range"][0]), (sh["cold_f"][1], "slow", sh["dur_h_range"][1])):
        e_use = 12 * lim["c_min"] * 3.6 * sh["age"] * (sh["soc_store"] - sh["reserve"]) * cf
        assert abs(e_use / sh["rows"][row]["pt_pack"] - dur) < 1e-9
    assert sh["dur_h_range"][1] + max(r["tc_pack_h"] for r in sh["rows"].values()) < R["g"]["hours"], "the pack-fed heater covers E4-S after all"
    assert "turns off the FETs" in sh["shutdown_fets_off"]
    # the regulator's loss is counted once, into the air node: the terminal power exceeds the mat's by exactly that share
    for row in sh["rows"].values():
        assert row["pt_prim_reg"] > row["pt_prim_direct"]
    # the nominal comparison is withdrawn on the page and in the output
    assert "WITHDRAWN as a feasibility basis" in open(OUT, encoding="utf-8").read()
    assert "**withdrawn** as a feasibility basis" in open(PAGE, encoding="utf-8").read()
    # the separately fed heater stays INCONCLUSIVE with its missing facts named
    rt = [r for r in R["dec"]["LO-01g"]["routes"] if "primary battery" in r["route"]][0]
    assert rt["status"] == "INCONCLUSIVE" and "not adopted" in rt["route"] and "D-06" in rt["missing"] and "minimum capacity at -33 C" in rt["missing"]
    assert abs(H["resid2_hot"] - 0.351) < 0.001 and abs(H["resid2_cold"] - 0.301) < 0.001
    for k in ("LO-01f", "LO-01g"):
        assert R["passive"][k]["ins_mm"] > 2.66, "%s's passive route fits the pocket after all" % k


def t_cooler_balance_conserves_energy():
    R = _R()
    # the air gains the kit's heat plus only the cooler's input Q_c/COP: G_e a = q + G_b (a - d)/COP at every reported equilibrium
    cc = R["condc"]
    gb = R["Gblk"][1]
    for (key, cop), v in cc["cool"].items():
        t_amb = 55.0 if key == "E3-O" else R["e"]["amb"]
        a, d = v["air"] - t_amb, R["hot"]["H1"] - t_amb
        assert abs(cc["G_e"] * a - (R["shore_heat"] + gb * (a - d) / cop)) < 1e-9, (key, cop)
        assert abs(v["p_in"] - gb * (a - d) / cop) < 1e-9 and v["air"] > 60.0, "the conditioned corner's cooler keeps the air inside F2's +60 C"
    for key in ("E3-O", "E5"):
        for (cn, cop), v in R["cool"][key]["inside"].items():
            if v:
                assert abs(v["p_in"] - v["qc"] / cop) < 1e-12


def t_comparison_recommends_the_least_complex_qualifying_approach():
    R = _R()
    cm = R["cmp"]
    ap = cm["apr"]
    assert sorted(ap) == ["I", "II", "III"] and all(sorted(a["rows"]) == sorted(R["dec"]) for a in ap.values())
    lines = "\n".join(_CACHE["M"].comparison_lines(R))
    for attr in ("maker limits", "usable energy", "thermal demand", "mass and volume", "maintenance", "implementation", "constraints changed", "remaining"):
        assert lines.count("   " + attr) == 3, "%s is not shown for each approach" % attr
    assert cm["rec"] == "II" and ap["II"]["qualifies"] and not ap["I"]["qualifies"] and not ap["III"]["qualifies"]
    assert len(ap["II"]["added"]) == 0 < len(ap["III"]["added"]) < len(ap["I"]["added"])
    # the conditioned corner: LO-01a's governing conductance with the worst heat; the E3-O air settles 15 K over the chamber
    g = R["gov"]["all"][4]
    assert abs(R["condc"]["G_e"] - g) < 1e-12 and abs(R["condc"]["e3o_air_ss"] - (55.0 + R["shore_heat"] / g)) < 1e-9
    assert abs(R["shore_heat"] / g - 15.0) < 1e-9, "the SGP41's +55 C at +40 C is a 15 K rise"
    # (II)'s first-cut ladder keeps today's offsets under the page's 30-day row; U2's lowest trip shifts by the BQ7720700's
    hl = R["S"]["HL18650V"]
    assert cm["lim2"] == hl["st_30d"][1] == 80.0
    h1n = cm["lim2"] - (60.0 - R["hot"]["H1"]) - R["hot"]["terms"]["thermistor interchangeability"]
    assert abs(cm["h1n2"] - h1n) < 1e-12
    shift = 70.0 - R["ladder"]["U2_trip_lo"]
    assert abs(cm["u2lo"]["BQ7720704"] - (83.0 - shift)) < 1e-9 and cm["u2_pick"] == "BQ7720704"
    assert cm["u2lo"]["BQ7720701"] < cm["clear"] < cm["u2lo"]["BQ7720704"], "the 80 C variant would clear every level after all"
    m2 = cm["m2"]
    assert abs(m2["LO-01d"]["m_h1"] - (h1n - R["condc"]["e3o_peak"])) < 1e-9 and abs(m2["LO-01e"]["m_h1"] - (h1n - R["condc"]["e5_peak"])) < 1e-9
    assert m2["LO-01f"]["m_limit"] == 80.0 - 71.0 and m2["LO-01g"]["m_limit"] == -33.0 - (-40.0)
    assert all(v[k] > 0 for v in m2.values() for k in ("m_limit", "m_h1", "m_u2") if k in v)
    # at the bound's worst corner E5 passes the re-derived H1: (II) carries T-H1's condition
    assert cm["m2_unc"]["e5_peak"] > h1n
    # the primary battery is added energy storage, several times the pack, and stays a proposal
    ii = cm["iii"]
    psel = R["prim"]["configs"]["5S, -40 C curve (lower)"]
    assert ii["wh_nom"] == (psel["slow"]["cells"] * 47.0, psel["fast"]["cells"] * 47.0) and ii["x_pack"][0] > 3.0
    assert ii["st_max"] == 30.0 < ii["st_env"] and ii["no_recharge"]
    assert psel["fast"]["duty"] < 1.0 < R["prim"]["configs"]["4S, -40 C curve (lower)"]["fast"]["duty"], "5S is chosen for the fast corner's demand"
    out = open(OUT, encoding="utf-8").read()
    page = open(PAGE, encoding="utf-8").read()
    assert "RECOMMENDATION (4d): (II)" in out and "not met by this record" in out
    assert "(II) RECOMMENDED" in page and "not met by this record" in page and "ADDED ENERGY STORAGE" in page
    # E5's profile is Method 507.6 Procedure II's, recomputed from its table
    ep = R["e5_profile"]
    assert ep["knots"] == [(0.0, 30.0), (2.0, 60.0), (8.0, 60.0), (16.0, 30.0), (24.0, 30.0)] and ep["cond"] == 23.0
    assert abs(ep["mean"] - (2 * 45 + 6 * 60 + 8 * 45 + 8 * 30) / 24.0) < 1e-12


def t_check_filed_byte_for_byte():
    import json
    for name, job, run in (("astra-check-l4e10-1.md", "cx26-l4e10-check", "20261001T223709Z-4184732"),
                           ("astra-check-l4e10-2.md", "cx27-l4e10-recheck", "20261001T231603Z-57210")):
        p = os.path.join(REC, "checks", name)
        need(p, "the filed check")
        t = open(p, encoding="utf-8").read()
        assert t.startswith("accepted: no\n"), name
        res = os.path.join(os.path.dirname(ROOT), "_runs", "codex", job, run, "result.json")
        if not os.path.exists(res):
            continue
        d = json.load(open(res, encoding="utf-8"))
        for b in d["blockers"]:
            assert "- " + b in t, "a blocker of %s is not filed verbatim" % name
        assert d["summary"] in t and d["closure_criterion"] in t and d["smallest_next_action"] in t, name


def t_page_figures_are_the_outs():
    R = _R()
    out = open(OUT, encoding="utf-8").read()
    page = open(PAGE, encoding="utf-8").read()
    figs = ["63.29", "62.12", "56.22", "60.39", "60.49", "1.2455", "1.3154", "1.5300", "1.6043", "1.6664", "58.64", "59.30", "63.42",
            "0.824", "0.485", "-10.24", "-5.52", "12.44", "12.84", "0.38 W", "0.44 W", "0.351 K", "0.301 K", "24.6 mm", "30.3 mm",
            "38.1 to 106.1", "3.37 to 9.30", "8.20 W", "11.9 to 28.9", "1.3 to 8.6", "-8.14", "0.30 to 1.09", "1.57 to 4.57",
            "2.58 to 7.27", "0.133 to 0.183", "86.4 to 144.8", "0.86 to 3.44", "0.70 to 1.48", "0.051 to 0.525", "0.150 to 1.009", "38 to 213", "0.054 to 0.090",
            "2.34 to 2.47", "1.39 to 2.12", "68.86", "74.73", "70.00", "58.75", "8.18 to 25.69", "11.21 to 35.21", "74.9 to 96.1",
            "0.162", "1.489", "3.30 W/K", "11.14", "6.93", "6.84", "5.27", "1.06", "0.97", "9.00", "4.70", "7.00", "55.25", "29.75",
            "20.54", "79.63", "75.7", "470 to 940", "3.2 to 6.5", "38 to 76", "0.54 to 1.07", "25.8 to 35.9", "12.5 to 24.9",
            "-5.0 to 44.8", "4.9 to 21.1", "75.00", "0.092", "0.102", "7.12", "0.011", "0.012", "0.183", "0.203", "0.79 K", "0.248", "0.275", "1.057",
            "1.175", "52 to 117", "58.7 to 163.2", "47.5", "84.2", "1.51", "2.07", "50.82", "64.24", "66.72", "61.26", "72.42",
            "144.7", "127.4", "121.0", "108.1", "95.2", "90.4", "2.52", "2.22", "2.11", "1.37 to 3.24", "56.37 to 58.24",
            "4.67 to 8.00", "10.5 to 54.0", "52.04", "53.29", "1.725", "0.056", "0.121"]
    for f in figs:
        assert f in out, "%s not in the .out" % f
        assert f in page, "%s not on the page" % f


def t_held_files_ignored_and_pinned_alike():
    R = _R()
    fhb = _load("l4e10_fetch_under_test", os.path.join(REC, "fetch_held_back.py"))
    pins = R["pins"]
    for rel, _url, want in fhb.DOCS:
        assert pins.get(rel) == want, "%s pinned differently in the script and the fetcher" % rel
        r = subprocess.run(["git", "-C", ROOT, "check-ignore", "-q", rel])
        assert r.returncode == 0, "%s is not ignored by git" % rel
    src = open(os.path.join(ROOT, "v2/vendor/sources.txt"), encoding="utf-8").read()
    for rel in list(HELD) + ["v2/vendor/battery/molicel-inr18650-p28a-v1.pdf"]:
        line = [l for l in src.splitlines() if l.startswith(rel[len("v2/vendor/"):] + " ")]
        assert line and hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest() in line[0], "no source line for %s" % rel


def t_no_dash_or_claim_word():
    files = [SCRIPT, OUT, PAGE, os.path.join(REC, "README.md"), os.path.join(REC, "fetch_held_back.py")]
    files += [os.path.join(REC, "clarification", f) for f in sorted(os.listdir(os.path.join(REC, "clarification")))]
    rx = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives|rated for)\b", re.I)
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert "–" not in t and "—" not in t, "%s carries an en or em dash" % p
        assert not rx.search(t), "%s carries a claim word: %s" % (p, rx.search(t).group(0))
