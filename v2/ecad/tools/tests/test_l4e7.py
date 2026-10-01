"""Layer 4 task L4-E7 (MESHSAT-1357, 1 October 2026; v2/docs/records/l4e7/): real component settings for board E's solar
stage, held as predicates on the values l4e7_stage_settings.py computes.

The predicates: l4e_replay.out and l4e5_source_control.out are reproduced byte for byte in child processes, and
l4e_replay.py prints its record in-process, before any figure is used; the grade is the I grade, the only one the drawn QFN
offers that 8705af guarantees below 0 C junction, and the junction range it needs lies inside its tested range; the 100 W
corner holds at both temperature ends on the achieved setting, recomputed here in closed form from the chosen parts' own
tolerance and TCR, and the next larger catalogue setting fails the same design floor; every unprinted row carries a
break-even and a bench row; the hold's band and its energy are as chosen and the margin costs nothing on SC-37's day; the
committed .out is what the script prints; the hold keeps REQ-016's ratio and no draft carries the proposal; each draft apply script checks without writing, applies once to a copy and
refuses a second application, the three apply in either order and on top of L4-E5's R10 change, and none touches R10.
The control decision (L4-E7R, second round): the verdict on the present limit names the unwarranted values it rests on;
the comparison holds at most three approaches, each quantified on both days, one on warranted rows only and chosen; the
chosen bound's terms are printed limits at their own condition and the bound reproduces in separate arithmetic; the trip
never acts on SC-37's day and the regulation sits under its aged lowest on one basis; the supply sequencing, the dynamic
basis and the solar entry's ratings hold on their rows; the backstop's draft applies only after the hold and input limit
drafts; the drafts to the makers follow the decision. Nothing here writes into the tree.
"""
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e7")
SCRIPT = os.path.join(REC, "l4e7_stage_settings.py")
GEN_E = os.path.join(TOOLS, "gen_sch_e.py")
DRAFTS = ("apply_gen_sch_e_u5_grade.py", "apply_gen_sch_e_hold.py", "apply_gen_sch_e_input_limit.py")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_CACHE = {}


def _R():
    if "R" not in _CACHE:
        need(SCRIPT, "the L4-E7 record")
        need(os.path.join(ROOT, ".git"), "a git checkout (the scripts find the tree by git)")
        for rel in ("v2/vendor/power/lt8705a.pdf", "v2/vendor/passives/held/yageo-rt-series-v16-2025-05-06.pdf",
                    "v2/vendor/power/held/infineon-bsc028n06ns-rev2.1-c148250.pdf",
                    "v2/vendor/solar/held/sunpower-spr-e-flex-100-datasheet-523809-revd.pdf",
                    "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net", "v2/vendor/ti/held/ti-ina250-sbos511c.pdf",
                    "v2/vendor/ti/held/ti-tps3701-sbvs240c.pdf", "v2/vendor/power/littelfuse-smcj-series-tvs.pdf"):
            need(os.path.join(ROOT, rel), "an input of the L4-E7 record (held documents: its fetch_held_back.py)")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        _CACHE["gen_before"] = _sha(GEN_E)
        sp = importlib.util.spec_from_file_location("l4e7_stage_settings_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        try:
            _CACHE["R"] = m.compute()
        except SystemExit as e:
            raise AssertionError("l4e7_stage_settings.py refused (exit %s)" % e.code)
        _CACHE["M"] = m
    return _CACHE["R"]


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def t_replay_and_l4e5_reproduced_byte_for_byte():
    R = _R()
    assert R["r0a"], "l4e_replay.out not reproduced in a child process"
    assert R["r0b"], "l4e5_source_control.out not reproduced in a child process"
    assert R["r0c"], "l4e_replay.main() does not print its record in-process"


def t_grade_is_i_and_covers_the_kit_junction_range():
    R = _R()
    assert R["grade"] == "I"
    assert R["qfn"] == ["E", "I"], "the drawn QFN offers %s" % R["qfn"]
    assert "LT8705AI is guaranteed over the full -40" in R["note3"] and "assured by design, characterization" in R["note3"]
    rows = dict((g, r_) for g, r_ in R["order"].items())
    lo, hi = [(a, b) for pk, _pn, a, b in rows["I"] if pk == "UHF"][0]
    assert lo <= R["tj_cold"] and R["tj_hot"] <= hi, "junction %.1f to %.1f C outside the I grade's %d to %d C" % (R["tj_cold"], R["tj_hot"], lo, hi)
    assert R["tj_cold"] < 0, "the E grade would have served: the cold end is not below 0 C"
    assert (R["gm_lo"], R["gm_hi"]) == (0.94, 1.06)
    assert R["ceil5"][2] > 30.0 and R["tj_hot"] > R["tj_hot_old"], "U5's junction not taken at L4-E5's raised EXTVCC"


def t_corner_predicate_holds_on_the_achieved_values_at_both_ends():
    R = _R()
    i_nom = 1.208 / (1e-3 * R["rs"] * R["rm"])
    assert abs(i_nom - R["i_nom"]) < 1e-12, "the setting is not the one the chosen parts achieve"
    assert abs(R["rs"] - 0.015) < 1e-12 and R["rs_code"] == "C2903494" and abs(R["rm"] - 23200.0) < 1e-6 and R["rm_code"] == "C861244"
    for k, (lab, t_rs, t_rm, _air, _p) in enumerate(R["ends"]):
        rs_lo = (1 - R["tol_h"]) * (1 - R["tcr_h"] * abs(t_rs - 25.0))
        rm_lo = (1 - R["tol_y"]) * (1 - R["tcr_y"] * abs(t_rm - 25.0))
        vref = R["ref_p"]["max"] * (1 + R["line_p"] * 1e-2 * (25.0 - 12.0)) + 1.5 / R["ea2"]
        p = 25.0 * i_nom * vref / 1.208 / R["gm_lo"] / (rs_lo * rm_lo)
        assert p <= 100.0, "%s: %.4f W" % (lab, p)
        assert abs(p - R["main_chk"][k][1][0]) < 1e-6, "%s: closed form %.6f W, the script's worst %.6f W" % (lab, p, R["main_chk"][k][1][0])
        assert abs(R["main_chk"][k][1][1] - 25.0) < 1e-9, "the worst corner is not at REQ-016's 25 V"
    assert R["ends"][0][1] == R["t_cold"] == -20 and R["ends"][1][2] == R["t_air"], "the two ends are not the envelope's"
    assert R["ends"][1][1] > R["t_air"], "RSENSE1's own rise missing at the hot end"
    for lab, w, _n in R["chk_floor"]:
        assert w[0] <= 100.0, "the design floor fails at %s" % lab


def t_next_larger_setting_fails_the_same_floor():
    R = _R()
    stocked = sorted([r_ for r_ in R["rows_rm"] if r_[2] >= 1000], key=lambda t: t[0])
    k = [r_[1] for r_ in stocked].index(R["rm_code"])
    assert k > 0, "no larger stocked setting to test against"
    larger = stocked[k - 1]
    assert larger[5] > 100.0, "the next larger setting %s passes the floor (%.3f W): the rule did not take the largest" % (larger[1], larger[5])
    assert stocked[k][5] <= 100.0
    assert R["zero"][1] == larger[1] and R["zero"][4] <= 100.0, "the zero-margin setting is not the next larger one"
    assert R["old_on_parts"] < 100.0 and R["i_nom"] < 3.548, "the chosen setting is not a design margin below the replay's grid"


def t_unprinted_rows_have_break_evens_and_bench_rows():
    R = _R()
    g1 = R["be_gain"][(1.0, False)]
    assert all(g is not None and g < R["ea2"] / 2.0 for g in g1), "EA2's break-even %s not below the floor of half its typical" % g1
    gd = R["be_gain"][(2.0, True)]
    assert all(g is not None and g < R["ea2"] / 2.0 for g in gd), "with the drifts and line x2 the floor does not cover EA2: %s" % gd
    assert R["be_line"][0] > 2.0 and R["be_line"][1] > 2.0
    assert R["be_tcr_cold"] is None or R["be_tcr_cold"] > 10 * R["tcr_h"]
    assert R["be_tcr_cold_floor"] is not None and R["be_tcr_cold_floor"] > R["tcr_h"], "under the design floor the printed TCR fails"
    assert abs(R["be_tcr_cold_floor"] * 1e6 - 122.295) < 0.01, "stack C's cold TCR break-even is not the check's"
    text = "\n".join(_CACHE["M"].render(R))
    sec7 = text.split("7. INCONCLUSIVE")[1].split("8. BENCH ROWS")[0]
    for row in ("EA2's voltage gain", "line regulation", "RSENSE1's TCR below", "EA3's gain", "U5's junction"):
        assert row in sec7 and "Bench" in sec7, "INCONCLUSIVE row %s or its bench measurement missing" % row
    sec8 = text.split("8. BENCH ROWS")[1]
    assert "7b.9 (steady state)" in sec8 and "7b.9t (transients, recorded apart)" in sec8
    assert ("from %.3f V" % R["hb3"][0]) in sec8 and ("accepted inside %.3f to %.3f V" % (R["hb3"][0], R["hb3"][2])) in sec8, \
        "the sweep and the hold acceptance do not start at the conditioned envelope's low end (M3)"
    assert "(stack A)" in sec7 and "(stack C)" in sec7, "a break-even without its stack (M2)"


def t_hold_keeps_req016_ratio_and_its_band_reproduces():
    """B1 of astra-check-l4e7-1: REQ-016's 17.6 V point and D-34 stand, so the hold keeps the drawn 102k over 7.5k as 0.1 %
    25 ppm/K parts; the band reproduces the check's figures; the drawn E-grade lower corner is reported (M1)."""
    R = _R()
    lo, nom, hi = R["hb"]
    assert (R["r8c"], R["r9c"]) == ("C861068", "C728597") and (R["r8v"], R["r9v"]) == (102000.0, 7500.0)
    assert abs(nom - 1.205 * (1 + 102.0 / 7.5)) < 1e-9 and abs(nom - R["hold_drawn"][1]) < 1e-9, "the nominal hold is not the drawn one"
    assert abs(lo - 16.970441) < 5e-7 and abs(hi - 18.220502) < 5e-7, "the band %.6f to %.6f V is not the check's" % (lo, hi)
    assert abs(R["drawn_e_lo"] - 16.723678) < 5e-7, "the drawn E-grade lower corner %.6f V" % R["drawn_e_lo"]
    assert hi - lo < R["hold_drawn"][2] - R["hold_drawn"][0], "the band is not narrower than as drawn"
    assert R["hb3"][0] < R["hb2"][0] < lo and hi < R["hb2"][2] < R["hb3"][2], "the conditioned bands do not nest"
    e_nom = [r_ for r_ in R["grid_e"] if r_[0] == "nominal hold"][0][2]
    assert abs(e_nom - 349.9991) < 5e-4, "the kept hold's nominal energy %.4f Wh is not the check's" % e_nom
    pr = R["proposal"]
    assert abs(pr["band"][1] - 1.205 * (1 + 94.2 / 7.5)) < 1e-9 and 24.5 < pr["e_band"][1] - pr["e_nom_kept"] < 25.5


def t_no_draft_carries_the_proposal_and_the_entry_keeps_17_6_v():
    need(GEN_E, "board E's generator")
    for name in DRAFTS:
        spec = importlib.util.spec_from_file_location(name[:-3] + "_p", os.path.join(REC, name))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        new = m.patched(open(GEN_E, encoding="utf-8").read())
        assert new.count('    _intent.rail(_pvn, 17.6, 5.68, 6.25, "J_SOLAR" if _pvn == "PV_IN" else "F2",') == 1, "%s moves the entry's 17.6 V" % name
        assert "C861602" not in new and "94.2k" not in new and "16.34 V" not in new, "%s carries the unadopted proposal" % name
    hold = [n for n in DRAFTS if "hold" in n][0]
    spec = importlib.util.spec_from_file_location("hold_p", os.path.join(REC, hold))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert len(m.EDITS) == 1 and 'r("R8", "102k 0.1% 25ppm' in m.EDITS[0][1] and 'r("R9", "7.50k 0.1% 25ppm' in m.EDITS[0][1]


def t_margin_costs_nothing_on_the_design_day():
    R = _R()
    d = [row[3 + k][0] - row[6 + k][0] for row in R["grid_e"] for k in range(3)]
    assert min(d) >= -0.05, "the margin gives up %.2f Wh at some cell of SC-37's day" % -min(d)
    a2 = [v for (lab, ak), v in R["runs"].items() if ak == "A2" and lab.startswith("NEW nominal")][0]
    was = R["old_runs"][("CORRECTED, WE; O-2 nominal", "A2")]
    assert all(abs(a2[2][k] - was[1][k]) < 0.05 for k in range(2)), "the kept nominal hold does not give the replay's A2 figures"


def t_committed_out_is_what_the_script_prints():
    R = _R()
    text = "\n".join(_CACHE["M"].render(R)) + "\n"
    committed = open(os.path.join(REC, "l4e7_stage_settings.out"), encoding="utf-8").read()
    assert text == committed, "l4e7_stage_settings.out is not the script's current output"
    assert "\u2013" not in committed and "\u2014" not in committed, "a dash character in the output"


def _run(script, target, *flags):
    return subprocess.run([sys.executable, "-B", os.path.join(REC, script), target] + list(flags), capture_output=True, text=True,
                          cwd=os.path.dirname(target))


def t_each_draft_checks_applies_once_and_refuses_a_second_application_on_a_copy():
    need(GEN_E, "board E's generator")
    before = _sha(GEN_E)
    for name in DRAFTS:
        need(os.path.join(REC, name), "the draft apply script")
        d = tempfile.mkdtemp(prefix="l4e7-apply-")
        try:
            cp = os.path.join(d, "gen_sch_e.py")
            shutil.copyfile(GEN_E, cp)
            orig = _sha(cp)
            r = _run(name, cp, "--check")
            assert r.returncode == 0 and "CHECK OK" in r.stdout, (name, r.returncode, r.stderr)
            assert _sha(cp) == orig, "%s --check wrote" % name
            r = _run(name, cp, "--write")
            assert r.returncode == 0 and _sha(cp) != orig, (name, r.returncode, r.stderr)
            r = _run(name, cp, "--write")
            assert r.returncode == 3 and "already applied" in r.stderr, (name, r.returncode, r.stderr)
            r = _run(name, cp, "--check")
            assert r.returncode == 3, (name, r.returncode)
            open(cp, "w", encoding="utf-8").write("x = 1\n")
            r = _run(name, cp, "--check")
            assert r.returncode == 3 and "occurs 0 times" in r.stderr, (name, r.returncode, r.stderr)
        finally:
            shutil.rmtree(d)
    assert _sha(GEN_E) == before, "the tree's gen_sch_e.py changed"


def t_drafts_apply_in_either_order_on_top_of_l4e5_and_leave_r10_alone():
    need(GEN_E, "board E's generator")
    src = open(GEN_E, encoding="utf-8").read()
    r10_old = 'r("R10", "115k 1% (RFBOUT1: 15.1 V)"'
    assert src.count(r10_old) == 1
    results = []
    for order, base in ((DRAFTS, src), (tuple(reversed(DRAFTS)), src),
                        (DRAFTS, src.replace(r10_old, 'r("R10", "232k 1% (RFBOUT1: L4-E5 ceiling)"'))):
        d = tempfile.mkdtemp(prefix="l4e7-order-")
        try:
            cp = os.path.join(d, "gen_sch_e.py")
            open(cp, "w", encoding="utf-8").write(base)
            for name in order:
                r = _run(name, cp, "--write")
                assert r.returncode == 0, (order, name, r.stderr)
            out = open(cp, encoding="utf-8").read()
            results.append(out)
            r10_line = [l for l in base.splitlines() if l.startswith('r("R10"')][0]
            assert out.count(r10_line) == 1, "R10's line changed under %s" % (order,)
        finally:
            shutil.rmtree(d)
    assert results[0] == results[1], "the drafts do not commute"
    for name in DRAFTS:
        spec = importlib.util.spec_from_file_location(name[:-3] + "_t", os.path.join(REC, name))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        assert not any("R10" in o or "C26" in o or "C27" in o for o, _n in m.EDITS), "%s edits L4-E5's parts" % name


def t_the_record_names_the_drafts_codes_and_never_wrote_the_tree():
    R = _R()
    for name, (n_e, touches, r10_once, codes_ok, codes) in R["drafts"].items():
        assert n_e > 0 and not touches and r10_once and codes_ok, (name, codes)
    assert _sha(GEN_E) == _CACHE["gen_before"], "the tree's gen_sch_e.py changed during the record's run"


# ---------------------------------------------------------------- the qualification of the 100 W bound (owner, 1 October 2026)
QUAL_IDS = {"EA2", "A7", "LINE", "TCR", "HOLD", "TJ"}
CLAR = os.path.join(REC, "clarification")


def t_every_unprinted_row_is_classified():
    R = _R()
    rows = R["qual_rows"]
    assert {r_["id"] for r_ in rows} == QUAL_IDS and len(rows) == len(QUAL_IDS), [r_["id"] for r_ in rows]
    for r_ in rows:
        for k in ("bound", "stability", "protection"):
            assert isinstance(r_[k], bool), (r_["id"], k)
        for k in ("why_bound", "why_stability", "why_protection", "sheet", "other", "conservative", "qualification"):
            assert isinstance(r_[k], str) and len(r_[k]) > 10, "%s has no %s" % (r_["id"], k)
        for outcome, text in r_["small"].items():
            assert r_[outcome], "%s calls its %s effect small but does not mark it" % (r_["id"], outcome)
            assert "%" in text and any(ch.isdigit() for ch in text), "%s's small %s effect carries no number" % (r_["id"], outcome)
    for k, v in R["unprinted_rows"].items():
        assert not v[1], "%s is a full-range row, not an unprinted one" % k


def t_a_row_that_moves_the_bound_has_an_assumption_a_qualification_and_a_margin():
    R = _R()
    moving = [r_ for r_ in R["qual_rows"] if r_["bound"]]
    assert moving, "no row moves the bound"
    for r_ in moving:
        assert r_["conservative"] and r_["qualification"] and r_["breakeven"], r_["id"]
        margin = r_["margin_w"] if r_["margin_w"] is not None else r_.get("margin_k")
        assert margin is not None and margin > 0, "%s keeps no positive margin" % r_["id"]
        if not r_["resolved"] and r_["id"] != "TJ":
            assert r_["clarification"], "%s has no clarification request" % r_["id"]
        if r_["id"] == "TJ":
            assert "design verification" in r_["qualification"]
        else:
            assert "warrants" in r_["qualification"] and "supporting evidence, not a production guarantee" in r_["qualification"], r_["id"]
    assert R["cons"]["joint"] < 100.0 and all(R["cons"][k] < 100.0 for k in ("ea2", "line", "tcr"))


def t_clarification_texts_exist_and_contact_no_one():
    R = _R()
    named = {r_["clarification"] for r_ in R["qual_rows"] if r_["clarification"]}
    assert named == {"analog-devices-lt8705a.txt", "milliohm-hojlr2512.txt"}, named
    for nm in named:
        p = need(os.path.join(CLAR, nm), "a clarification text")
        t = open(p, encoding="utf-8").read()
        assert t.startswith("DRAFT FOR THE OWNER TO SEND.") and "contacts no outside party" in t, nm
        assert "\u2013" not in t and "\u2014" not in t and all(ord(c) < 128 for c in t), "%s is not plain ASCII text" % nm
    ad = " ".join(open(os.path.join(CLAR, "analog-devices-lt8705a.txt"), encoding="utf-8").read().split())
    assert "LT8705AIUHF" in ad and "EA2" in ad and "line regulation" in ad and "VC" in ad
    assert "A7" in ad and "common mode" in ad and "transfer error" in ad and "while switching" in ad, "the A7 question is missing"
    mo = " ".join(open(os.path.join(CLAR, "milliohm-hojlr2512.txt"), encoding="utf-8").read().split())
    assert "HoJLR2512-3W-15mR-1%" in mo and "-40 C to +25 C" in mo
    for t in (ad, mo):
        assert "warrant" in t and "supporting" in t and "production guarantee" in t, "a draft lets characterization stand as a guarantee"


def t_result_is_conditional_exactly_when_an_unresolved_row_moves_the_bound():
    R = _R()
    M = _CACHE["M"]
    assert R["bound_status"] == M.bound_status(R["qual_rows"]) == "CONDITIONAL"
    base = [dict(r_) for r_ in R["qual_rows"]]
    resolved = [dict(r_, resolved=True) for r_ in base]
    assert M.bound_status(resolved) == "UNCONDITIONAL"
    only_hold_open = [dict(r_, resolved=(r_["id"] != "HOLD")) for r_ in base]
    assert M.bound_status(only_hold_open) == "UNCONDITIONAL", "a row that does not move the bound made it conditional"
    for k in ("EA2", "A7", "LINE", "TCR", "TJ"):
        one_open = [dict(r_, resolved=(r_["id"] != k)) for r_ in base]
        assert M.bound_status(one_open) == "CONDITIONAL", k
    text = "\n".join(M.render(R))
    assert "THE RESULT: CONDITIONAL on EA2, A7, LINE, TCR, TJ." in text


def t_the_corners_bound_the_permitted_range():
    R = _R()
    assert min(R["dpdv"]) > 0, "the power is not increasing in the input voltage at every vertex"
    for chk in (R["main_chk"], R["chk_printed"], R["chk_floor"], R["chk_drift"]):
        assert all(abs(w[1] - 25.0) < 1e-9 for _l, w, _n in chk), "a stack's worst is not at the 25 V vertex"
    hl = R["p_hold_lo"]
    assert hl["a"] < R["main_chk"][0][1][0] and hl["c"] < R["chk_floor"][0][1][0] and hl["joint"] < R["cons"]["joint"], \
        "the hold's lowest is not below the 25 V corner under a matching stack"
    t_be_a, t_be_c = R["rs_t_be"]
    assert (t_be_a is None or t_be_a > R["ends"][1][1]) and t_be_c is not None and t_be_c > R["ends"][1][1] + 50.0
    assert R["ends"][0][1] == R["t_cold"] and R["ends"][1][2] == R["t_air"]
    assert R["outside"]["voc40"] > 25.0, "below -20 C the candidate is not outside REQ-016's window"


def t_the_sheet_is_the_owners_official_url():
    R = _R()
    pv = R["prov"]
    assert pv["url"] == "https://www.analog.com/media/en/technical-documentation/data-sheets/8705af.pdf"
    assert pv["snapshot"] == "20250322064938" and pv["sha"].startswith("8f552a0b57677bfa")
    assert pv["sha"] == hashlib.sha256(open(os.path.join(ROOT, "v2/vendor/power/lt8705a.pdf"), "rb").read()).hexdigest()


def t_the_full_range_tcr_swap_is_evaluated_and_not_taken():
    R = _R()
    w = R["wsl"]
    assert w["p_floor"] > 100.0, "the alternative passes the design floor at 23.2k: the swap would cost nothing"
    assert w["pick"] is not None and w["pick"][0] > R["rm"] and w["cost"] > 0.0
    for name, (_n, _t, _r, codes_ok, codes) in R["drafts"].items():
        assert "C844695" not in codes
    assert "C2903494" in R["drafts"]["apply_gen_sch_e_input_limit.py"][4]


def t_a7_is_a_condition_with_its_sensitivity():
    """B1 of astra-check-l4e7q-1: A7's gm row is printed at a 50 mV differential with CSPIN at 5.025 V; applying it at the
    design's common mode and differential is a condition of the bound, with its sensitivity printed."""
    R = _R()
    a7 = [r_ for r_ in R["qual_rows"] if r_["id"] == "A7"][0]
    assert a7["bound"] and not a7["resolved"] and a7["clarification"] == "analog-devices-lt8705a.txt"
    assert "5.025 V" in a7["sheet"] and "50 mV" in a7["sheet"] and "TYPICAL" in a7["sheet"] and "against the differential only" in a7["sheet"]
    q = R["a7q"]
    assert abs(q["be"]["joint"] - 0.939053) < 1e-6 and abs(q["loss"]["joint"] - 0.100779) < 1e-5, (q["be"]["joint"], q["loss"]["joint"])
    assert q["be"]["a"][0] < q["be"]["c"][0] < q["be"]["joint"] < R["gm_lo"], "the break-evens are not ordered A, C, together"
    assert q["cm"][1] == 25.0 and q["cm"][0] > 5.025, "the design's common mode is not away from the test point"


def t_tcr_and_line_carry_their_small_nonzero_effects():
    """B2 of astra-check-l4e7q-1: the cold TCR moves the sense-path loop gain and the current at which the fault trips, not the
    comparator's threshold; the fault-to-limit ratio counts the line and EA2 allowances; the line couples the source voltage."""
    R = _R()
    rows = {r_["id"]: r_ for r_ in R["qual_rows"]}
    tcr, line = rows["TCR"], rows["LINE"]
    assert tcr["stability"] and tcr["protection"] and set(tcr["small"]) == {"stability", "protection"}
    e = R["tcr_effects"]
    assert abs(100 * e["loop"] + 0.2255) < 5e-4 and abs(100 * e["trip"] - 0.2260) < 5e-4, (e["loop"], e["trip"])
    assert "threshold voltage" in tcr["why_protection"] and "does not move" in tcr["why_protection"] and "trips" in tcr["why_protection"]
    fr = R["fault_ratio"]
    assert abs(fr["reg_c"] - 1.253674623) < 1e-9 and abs(fr["c"] - 1.236365) < 5e-7, (fr["reg_c"], fr["c"])
    assert fr["c"] < fr["a"] < 1.55 / 1.229, "the ratio leaves out the line or EA2 allowance"
    assert ("%.6f" % fr["c"]) in tcr["why_protection"] and "1.55 / 1.229" not in tcr["why_protection"]
    assert line["stability"] and "stability" in line["small"] and "couples" in line["why_stability"]
    assert R["line_coupling"]["assumed"] > R["line_coupling"]["printed"] > 0


def t_thermal_coupling_hold_floor_junction_and_panel_scenarios():
    """M1 to M4 of astra-check-l4e7q-1."""
    R = _R()
    th = R["thermal"]
    assert abs(th["mixed"]["a"] - 96.248120559) < 1e-8 and abs(th["mixed"]["c"] - 99.674651953) < 1e-8, th["mixed"]
    for k in ("a", "c", "joint"):
        assert th["paired"][k] <= th["mixed"][k] + 1e-12 and th["sweep"][k] <= th["mixed"][k] + 1e-12 and th["mixed"][k] < 100.0
    hl = R["p_hold_lo"]
    assert 65.40 < hl["c"] < 65.42 and 65.55 < hl["joint"] < 65.57 and hl["c"] < R["chk_floor"][0][1][0]
    tj = [r_ for r_ in R["qual_rows"] if r_["id"] == "TJ"][0]
    assert "INFERRED estimate" in tj["conservative"] and "not a demonstrated upper bound" in tj["conservative"]
    assert "not switching, EXTVCC = 0" in tj["sheet"]
    o = R["outside"]
    assert abs(o["p_panel_soak"] - 122.695) < 0.01 and o["p_panel_cold"] < o["p_panel_soak"]
    text = "\n".join(_CACHE["M"].render(R))
    sec8 = text.split("8. BENCH ROWS")[1].split("9. QUALIFICATION")[0]
    assert ("%.1f W, a warmed" % o["p_panel_cold"]) in sec8 and ("%.1f W, a cold-soaked" % o["p_panel_soak"]) in sec8


def t_the_junction_estimate_is_never_called_a_bound_and_line_keeps_its_coupling():
    """The residues of astra-check-l4e7q-2: U5's junction (about 105.4 C) is an INFERRED estimate everywhere, never "at most",
    an "upper bound" or a "limit"; LINE's stability wording drops "no gain of its own" and keeps its quantified coupling."""
    import re
    R = _R()
    tj = "%.1f" % R["tj_hot"]
    texts = {"out": open(os.path.join(REC, "l4e7_stage_settings.out"), encoding="utf-8").read()}
    for nm in ("L4E7-STAGE-SETTINGS.md", "L4E7-QUALIFICATION.md", "README.md"):
        texts[nm] = open(os.path.join(REC, nm), encoding="utf-8").read()
    for nm, t in texts.items():
        flat_ = " ".join(t.split())
        assert not re.search(r"at most (about )?%s" % re.escape(tj), flat_), "%s calls the junction 'at most %s C'" % (nm, tj)
        assert not re.search(r"%s C? ?(\w+ ){0,3}(limit|upper bound)" % re.escape(tj), flat_), "%s calls %s C a limit or bound" % (nm, tj)
        assert not re.search(r"(limit|upper bound)( of| at)? (about )?%s" % re.escape(tj), flat_), "%s calls %s C a limit or bound" % (nm, tj)
        rest = flat_.replace("not a demonstrated upper bound", "").replace("not a demonstrated bound", "")
        assert "upper bound" not in rest, "%s calls something an upper bound outside the negation" % nm
        assert "no gain of its own" not in t, "%s keeps 'no gain of its own'" % nm
    assert "TJ estimated about %s C (INFERRED)" % tj in " ".join(texts["out"].split())
    line = [r_ for r_ in R["qual_rows"] if r_["id"] == "LINE"][0]
    assert "no gain of its own" not in line["why_stability"] and "couples a moving source voltage" in line["why_stability"]
    assert "%.4f %%" % (2.0 * R["line_p"]) in line["why_stability"] and "setpoint" in line["small"]["stability"]


# ---------------------------------------------------------------- the control decision (L4-E7R, owner, 1 October 2026; second
# round after checks/astra-check-l4e7r-1.md)
BACKSTOP = "apply_gen_sch_e_backstop.py"
WARRANTED = {"warranted", "warranted (printed test limits)", "warranted (the rows, read both ways)", "rating (the pin's absolute maximum)",
             "requirement"}
ANSWERS = ("EA2", "A7", "LINE", "RSENSE1", "HoJLR", "Milliohm", "Analog Devices")


def _approach(R, i):
    return [a for a in R["decision"]["approaches"] if a["id"] == i][0]


def t_the_verdict_names_what_the_present_limit_rests_on():
    R = _R()
    v = R["decision"]["verdict"]
    assert v["shown"] is False
    assert {i for i, _b in v["depends"]} == {"EA2", "A7", "LINE", "TCR", "TJ"}, v["depends"]
    assert all(b for _i, b in v["depends"]), "a value the verdict rests on has no break-even"
    text = " ".join("\n".join(_CACHE["M"].render(R)).split())
    assert "THE VERDICT ON THE CURRENT CONTROL: NOT SHOWN on warranted manufacturer limits alone." in text


def t_at_most_three_approaches_each_quantified_one_on_warranted_rows_only():
    R = _R()
    d = R["decision"]
    ap = d["approaches"]
    assert 1 <= len(ap) <= 3, len(ap)
    for a in ap:
        assert isinstance(a["bound"], float) and 90.0 < a["bound"] <= 100.0, (a["id"], a["bound"])
        assert a["status"] in ("CONDITIONAL", "UNCONDITIONAL")
        assert [e_[0] for e_ in a["energy"]] == ["lower", "nominal", "upper", "bright"]
        assert all(e_[2] > 0 and isinstance(e_[3], int) for e_ in a["energy"]), "an approach's energy or bound hours are missing"
        assert a["classes"] and a["parts"] and a["failure"] and a["depends"] and a["surge"], a["id"]
        assert 0 < a["noon_red"] < a["cur_red"], "%s: the noon power reduction is not computed below the current reduction" % a["id"]
    ind = [a for a in ap if a["independent"]]
    assert len(ind) >= 1 and all(a["status"] == "UNCONDITIONAL" for a in ind)
    assert all(a["status"] == "CONDITIONAL" for a in ap if not a["independent"])
    assert d["chosen"] == "C" and _approach(R, "C")["independent"]


def t_the_chosen_bound_rests_only_on_warranted_rows_and_reproduces_in_closed_form():
    R = _R()
    d = R["decision"]
    c, rw = d["c"], d["rows"]
    assert {t_[2] for t_ in c["terms"]} <= WARRANTED, {t_[2] for t_ in c["terms"]}
    for t_ in c["terms"]:
        assert not any(w in t_[0] for w in ANSWERS), "the chosen bound names %s" % t_[0]
        assert "typical" not in t_[2] and "times its typical" not in t_[1] and "twice" not in t_[0], t_
    assert set(_approach(R, "C")["classes"]) <= {"warranted", "rating", "requirement"}
    assert [t_[0] for t_ in c["terms"] if t_[2].startswith("rating")] == [t_[0] for t_ in c["terms"] if "VIN+ pin" in t_[0]]
    # the controlling calculation in separate arithmetic: the highest trip at 25 V and the bound
    dt = 45.0
    r66 = rw["r66"] * (1 - 0.001) * (1 - 25e-6 * dt) * (1 - 0.005 - 0.05 / rw["r66"]) ** 2
    gm = rw["gm169"][0] * (1 - rw["nl169"])
    base = (rw["vth"][1] + rw["iin_t"] * r66) / (gm * r66)
    vs = base + rw["vos169"] + (10 ** (-rw["cmr169"] / 20.0) * 13.0 + rw["psr169"] * 20.0) * max(1.0, base / 0.050)
    rp = c["rp"]
    rb = rp / c["n"] * (1 - 0.01) * (1 - rw["wtcr"] * dt) * (1 - 0.005 - 0.0005 / rp) * (1 - 0.01 - 0.0005 / rp)
    p = 25.0 * vs / rb + 625.0 / (R["r8v"] + R["r9v"]) / ((1 - 0.001) * (1 - 25e-6 * dt) * (1 - 0.005 - 0.05 / R["r8v"]) ** 2) + 25.0 * rw["ipin169"]
    assert abs(c["v_hi"] - 25.0) < 1e-9 and abs(p - c["p_static"]) < 1e-6, (p, c["p_static"])
    assert c["p_static"] < 100.0 and c["p_dyn_typ"] < 100.0 and c["t_resp_max"] > 10 * c["t_resp_typ"]


def t_the_trip_never_acts_on_the_day_and_the_regulation_sits_under_it_on_one_basis():
    R = _R()
    c = R["decision"]["c"]
    assert c["trip_lo_hold"] > c["pk_day"], "the trip would act on SC-37's day"
    assert c["reg_hi25"] <= c["i_lo_aged"] < c["i_lo_new"] < c["i_hi25"], "the regulation is not coordinated under the aged trip"
    assert c["rm"][0] > R["rm"] and c["rm"][2] >= 1000
    assert c["exposed"] and all(p_ > 0 for _h, _g, p_ in c["exposed"])


def t_the_supply_sequencing_holds_on_printed_rows():
    R = _R()
    sq, rw = R["decision"]["seq"], R["decision"]["rows"]
    assert sq["rel_hi"] < sq["ldo_lo"], "U20 could hold RESET with LDO33 in regulation"
    assert sq["ldo_enable_min"] > max(sq["vdd38"], sq["vdd_t"]), "SWEN could rise before U19 and U20 work"
    assert sq["swen_at_ldo_lo"] > rw["swen"][1] and sq["i_sw_reset"] <= 1e-3 and sq["td_min"] >= 0.18 > rw["st_t"]
    assert sq["uv_ts_lo"] > 2.7 and sq["uv_ts_hi"] < 15.0, "U19's INA does not cover U18's supply below the hold"
    c = R["decision"]["c"]
    assert sq["i_ldo"] < 5e-3 and c["vout_hi"] < sq["uv_ts_lo"] - rw["sw169"], "LDO33's load or U18's compliance"


def t_the_dynamic_bound_uses_the_input_edge_and_names_its_basis():
    R = _R()
    d = R["decision"]
    c, rw = d["c"], d["rows"]
    assert d["w_avg"] == 0.1 and abs(rw["tpd_lh"] - 28.1e-6) < 1e-12, "the rising INB edge is not the 28.1 us row"
    assert c["e_cap"] > 0 and c["p_ev"] == 25.0 * rw["amps_pk"]
    assert abs(c["p_dyn_typ"] - (c["p_static"] + (c["e_cap"] + c["p_ev"] * c["t_resp_typ"]) / d["w_avg"])) < 1e-9
    text = " ".join("\n".join(_CACHE["M"].render(R)).split())
    assert "7b.16" in text and "%.3f ms" % (1e3 * c["t_resp_max"]) in text


def t_the_solar_entry_stays_inside_its_ratings_at_the_derived_disturbance():
    R = _R()
    d = R["decision"]
    sg, rw = d["surge"], d["rows"]
    assert sg["vc"] == 45.4 and sg["ipp"] == 33.1 and rw["za"]["v"] >= sg["vc"]
    assert sg["d169"] < sg["d169_abs"] and sg["v_pvp"] < min(sg["cm169_abs"], sg["vs169_abs"])
    assert max(v_ for _l, v_ in sg["s59"]) < sg["csd_abs"], sg["s59"]
    assert sg["b_abs"] < sg["vc"] and _approach(R, "B")["surge"].startswith("FAILS")
    assert _approach(R, "C")["surge"].startswith("passes")


def t_the_backstop_draft_follows_the_hold_and_input_limit_drafts_on_a_copy():
    need(GEN_E, "board E's generator")
    before = _sha(GEN_E)
    src = open(GEN_E, encoding="utf-8").read()
    outs = []
    for order in (DRAFTS, tuple(reversed(DRAFTS))):
        d = tempfile.mkdtemp(prefix="l4e7-bk-")
        try:
            cp = os.path.join(d, "gen_sch_e.py")
            open(cp, "w", encoding="utf-8").write(src)
            r = _run(BACKSTOP, cp, "--check")
            assert r.returncode == 3 and "occurs 0 times" in r.stderr, (r.returncode, r.stderr)
            for name in order:
                assert _run(name, cp, "--write").returncode == 0, name
            orig = _sha(cp)
            r = _run(BACKSTOP, cp, "--check")
            assert r.returncode == 0 and "CHECK OK" in r.stdout and _sha(cp) == orig, (r.returncode, r.stderr)
            r = _run(BACKSTOP, cp, "--write")
            assert r.returncode == 0 and _sha(cp) != orig, r.stderr
            r = _run(BACKSTOP, cp, "--write")
            assert r.returncode == 3 and "already applied" in r.stderr, r.stderr
            out = open(cp, encoding="utf-8").read()
            outs.append(out)
            for want in ('"36": "TRK_SWEN"', '"33": "TRK_VS"', '"TRK_VS", "TRK_VIN", "RS2512"', '"C44322")', '"C132788")', '"C43698")',
                         'r("R16", "29.4k', '{"1": "TRK_VS", "2": "GND"}, "C224047")', 'r("R14", "100k 1%", "TRK_VS", "TRK_SHDN")',
                         '_intent.rail("TRK_VS"', 'part("C69", '):
                assert out.count(want) == 1, want
            assert out.count('"C178637")') == 2 and '"C454360")' not in out
            assert out.count('r("R10", "115k 1% (RFBOUT1: 15.1 V)"') == 1
        finally:
            shutil.rmtree(d)
    assert outs[0] == outs[1], "the backstop does not land the same after either order of the three"
    R = _R()
    assert all(R["backstop_draft"].values()), R["backstop_draft"]
    assert R["drafts"][BACKSTOP][3]
    assert _sha(GEN_E) == before, "the tree's gen_sch_e.py changed"


def t_the_clarification_drafts_follow_the_decision():
    R = _R()
    assert R["decision"]["clar"] == ["analog-devices-lt8705a.txt", "milliohm-hojlr2512.txt", "texas-instruments-ina169.txt"]
    assert not os.path.exists(os.path.join(CLAR, "texas-instruments-ina250.txt"))
    ti = open(need(os.path.join(CLAR, "texas-instruments-ina169.txt"), "the TI draft"), encoding="utf-8").read()
    assert ti.startswith("DRAFT FOR THE OWNER TO SEND.") and "contacts no outside party" in ti and all(ord(ch) < 128 for ch in ti)
    t = " ".join(ti.split())
    assert "INA169" in t and "VIN+" in t and "warrant" in t and "supporting" in t and "production guarantee" in t
    ad = " ".join(open(os.path.join(CLAR, "analog-devices-lt8705a.txt"), encoding="utf-8").read().split())
    assert "SWEN" in ad and "input current" in ad


def t_the_minors_and_the_faults():
    R = _R()
    d = R["decision"]
    b, c = d["b"], d["c"]
    assert abs(b["loss"][0] - 0.1855) < 5e-4, b["loss"]
    rep = dict((rv, (e_, nr)) for rv, e_, nr in c["check_repro"])
    assert abs(rep[26100.0][0] - 495.3165) < 5e-5 and abs(rep[28700.0][0] - 465.6367) < 5e-5 and abs(100 * rep[26100.0][1] - 10.06) < 5e-3
    assert abs(100 * _approach(R, "A")["noon_red"] - 24.57) < 5e-3
    fl = d["faults"]
    assert fl["defeat"] and fl["stop"] and "Layer 8" in fl["acceptance"]
    text = " ".join("\n".join(_CACHE["M"].render(R)).split())
    assert "the smallest stocked RIMON_IN" in text and "largest stocked RIMON_IN" not in text.split("10. THE CONTROL DECISION")[1]


def t_the_decision_page_is_linked_and_carries_the_printed_figures():
    R = _R()
    page = need(os.path.join(REC, "L4E7-CONTROL-DECISION.md"), "the decision page")
    t = " ".join(open(page, encoding="utf-8").read().split())
    for nm in ("L4E7-STAGE-SETTINGS.md", "README.md"):
        assert "L4E7-CONTROL-DECISION.md" in open(os.path.join(REC, nm), encoding="utf-8").read(), nm
    d = R["decision"]
    c = d["c"]
    for a in d["approaches"]:
        assert ("%.4f" % a["bound"]) in t, a["id"]
    for fig in ("%.4f W" % c["p_static"], "%.4f W" % (100.0 - c["p_static"]), "%.4f A" % c["i_lo_aged"], c["model"],
                "%gk" % (c["rm"][0] / 1e3), "%.3f ms" % (1e3 * c["t_resp_max"]), "%.4f W" % c["p_dyn_typ"]):
        assert fig in t, fig
    assert "\u2013" not in t and "\u2014" not in t
