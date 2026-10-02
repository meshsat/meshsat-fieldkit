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
The control decision (L4-E7R, third round, the owner's decision process of 2 October 2026): the verdict on the present
limit names the unwarranted values it rests on; what REQ-016 bounds is read from it and the window is an interpretation;
the comparison holds at most three approaches, each quantified on both days, none called unconditional; one error budget
names its two assumptions and the bound reproduces in separate arithmetic; the setting is the least-cost one carrying both
assumptions past their meaning; check (b) counts the capacitor input energy, the panel's own current and the events; SWEN
is off by default on printed rows; the disturbances come from the approved test plan and every part holds; the panel lead's
surge and sustained over-voltage are derived from the lead the records give and the row REQ-063 commits to, each judged by
REQ-016's own criterion, the clamp and the source figures reproduced in closed form; the solar-fault remedies select one
remedy for each fault on held sheets, the cut-off's band recomputed here, the window kept and the re-runs named, and their
draft applies once after the five drafts it follows; the guard already on (the consolidation review's B6) is bounded in the
loaded network against every printed rating with the least lead inductance each holds at, the solver checked against the
closed-form series RLC step, the drafted network failing and each change necessary; the backstop's
draft applies only after the hold and input limit drafts; the drafts to the makers follow the decision and quote its
figures; L4-E9's figures are named. Nothing here writes into the tree.
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
                    "v2/vendor/ti/held/ti-tps3701-sbvs240c.pdf", "v2/vendor/power/littelfuse-smcj-series-tvs.pdf",
                    "v2/vendor/ti/held/ti-ina169-sbos181f.pdf", "v2/vendor/power/held/panasonic-za-eehza1h330xp-2017-11-07.pdf",
                    "v2/vendor/power/held/mil-std-461g-2015-12-11.pdf", "v2/vendor/passives/held/vishay-wsl-30100-2023-11-23.pdf",
                    "v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf"):
            need(os.path.join(ROOT, rel), "an input of the L4-E7 record (held documents: its fetch_held_back.py)")
        if shutil.which("pdftotext") is None or shutil.which("pdftocairo") is None:
            raise Skip("pdftotext and pdftocairo are needed")
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


# ---------------------------------------------------------------- the control decision (L4-E7R, owner, 1 October 2026; third
# round after checks/astra-check-l4e7r-2.md and the owner's decision process of 2 October 2026)
BACKSTOP = "apply_gen_sch_e_backstop.py"
CLASSES = {"warranted", "warranted (printed test limits)", "warranted (at 50 mV)", "warranted (from the rows above)",
           "documented dependency (typical row)", "assumption", "requirement"}
ANSWERS = ("EA2", "A7", "LINE", "RSENSE1", "HoJLR", "Milliohm", "Analog Devices")


def _approach(R, i):
    return [a for a in R["decision"]["approaches"] if a["id"] == i][0]


def _s10(R):
    return " ".join("\n".join(_CACHE["M"].render(R)).split()).split("10. THE CONTROL DECISION", 1)[1]


def t_the_verdict_names_what_the_present_limit_rests_on():
    R = _R()
    v = R["decision"]["verdict"]
    assert v["shown"] is False
    assert {i for i, _b in v["depends"]} == {"EA2", "A7", "LINE", "TCR", "TJ"}, v["depends"]
    assert all(b for _i, b in v["depends"]), "a value the verdict rests on has no break-even"
    assert "THE VERDICT ON THE CURRENT CONTROL: NOT SHOWN on warranted manufacturer limits alone." in _s10(R)


def t_what_is_bounded_is_read_from_req016_and_the_window_is_an_interpretation():
    R = _R()
    d = R["decision"]
    bs = d["basis"]
    assert bs["window_printed"] is False and bs["vm"] == ["CALCULATION", "PROTOTYPE_MEASUREMENT"] and bs["lead_hits"] == 0
    assert d["w_avg"] == 0.1 and "panel entry" in bs["boundary"]
    s = _s10(R)
    assert "The averaging window: REQ-016 states none" in s and "CONDITIONAL for layer 8 to confirm" in s
    assert "A longer window would be easier to meet and is not taken." in s
    c = d["c"]
    assert c["e_part_allow"] < 0.01 * 1.0 * d["w_avg"] and c["e_r59_allow"] < 0.01 * 3.0 * d["w_avg"]
    for k in ("CHECK (a), NORMAL OPERATION", "CHECK (b), STARTUP, SHUTDOWN AND THE FAULT RESPONSE", "CHECK (c), THE PARTS' RATINGS DURING THE SPECIFIED DISTURBANCES"):
        assert k in s, k


def t_at_most_three_approaches_each_quantified_none_called_unconditional():
    R = _R()
    d = R["decision"]
    ap = d["approaches"]
    assert 1 <= len(ap) <= 3, len(ap)
    for a in ap:
        assert isinstance(a["bound"], float) and 90.0 < a["bound"] <= 100.0, (a["id"], a["bound"])
        assert a["status"] == "CONDITIONAL" and a["independent"] is False, a["id"]
        assert [e_[0] for e_ in a["energy"]] == ["lower", "nominal", "upper", "bright"]
        assert all(e_[2] > 0 and isinstance(e_[3], int) for e_ in a["energy"]), "an approach's energy or bound hours are missing"
        assert a["classes"] and a["parts"] and a["failure"] and a["depends"] and a["surge"], a["id"]
        assert 0 < a["noon_red"] < a["cur_red"], "%s: the noon power reduction is not computed below the current reduction" % a["id"]
    assert d["chosen"] == "C" and "UNCONDITIONAL" not in _s10(R)


def t_one_error_budget_names_its_assumptions_and_reproduces_in_closed_form():
    R = _R()
    d = R["decision"]
    c, rw = d["c"], d["rows"]
    assert {t_[2] for t_ in c["terms"]} <= CLASSES, {t_[2] for t_ in c["terms"]}
    assm = [t_[0] for t_ in c["terms"] if t_[2] == "assumption"]
    assert len(assm) == 2 and "G_CM" in assm[0] and "VIN+ input bias" in assm[1], assm
    assert not any(t_[2].startswith("rating") for t_ in c["terms"]), "an absolute maximum is used as a ceiling"
    for t_ in c["terms"]:
        assert not any(w in t_[0] for w in ANSWERS), "the chosen bound names %s" % t_[0]
    assert set(_approach(R, "C")["classes"]) == {"warranted", "assumption", "documented dependency", "requirement"}
    # the controlling calculation in separate arithmetic: the highest trip at 25 V and the bound, at the chosen R66
    dt = 45.0
    agl = lambda r_, s_: (1 + s_ * 0.001) * (1 + s_ * 25e-6 * dt) * (1 + s_ * (0.005 + 0.05 / r_)) ** 2
    r66 = rw["r66"] * agl(rw["r66"], -1)
    gm = rw["gm169"][0] * (1 - rw["nl169"])
    base = (rw["vth"][1] + rw["iin_t"] * r66) / (gm * r66)
    rej = 10 ** (-rw["cmr169"] / 20.0) * 13.0 + rw["psr169"] * 20.0
    load = rw["r65"] * agl(rw["r65"], -1) + r66
    vs = base + rw["vos169"] + rej + c["g_cm"] * abs(base + rw["vos169"] + rej - 0.050) + base * abs(load - 25e3) / rw["ro169"]
    rp = c["rp"]
    rb = rp / c["n"] * (1 - 0.01) * (1 - rw["wtcr"] * dt) * (1 - 0.005 - 0.0005 / rp) * (1 - 0.01 - 0.0005 / rp)
    r89 = (R["r8v"] + R["r9v"]) * (1 - 0.001) * (1 - 25e-6 * dt) * (1 - 0.005 - 0.05 / R["r8v"]) ** 2
    p = 25.0 * vs / rb + 625.0 / r89 + 25.0 * (vs * rw["gm169"][1] * (1 + rw["nl169"]) + c["i_b"]) + (25.0 * c["leak"] if c["layout"] == "ahead" else 0.0)
    assert abs(c["v_hi"] - 25.0) < 1e-9 and abs(p - c["p_static"]) < 1e-6, (p, c["p_static"])
    bu = c["budget"]
    assert abs(bu["e_margin"] - (bu["e_tol"] - bu["e_sup"])) < 1e-12 and bu["e_margin"] > 0 and abs(bu["p_margin"] - (100.0 - c["p_static"])) < 1e-9
    assert abs(25.0 * bu["i_100"] + c["pb25"] - 100.0) < 1e-9
    assert c["g_cm"] == 0.01 and c["i_b"] == 1e-3


def t_the_setting_holds_round_3s_rule_and_the_cs101_search_takes_the_least_cost():
    R = _R()
    d = R["decision"]
    c, rw, cs = d["c"], d["rows"], R["cs101"]
    st = c["settings"]
    assert [s_["r66"] for s_ in st] == sorted(s_["r66"] for s_ in st) and len(st) >= 3
    r3 = [s_ for s_ in st if abs(s_["r66"] - 8250.0) < 1e-6][0]
    assert r3["ok"] and r3["g_cm_be"] >= 1.0 and not st[0]["ok"] and st[0]["g_cm_be"] < 1.0, "round 3's rule no longer picks 8.25k"
    assert c["t_fac"] == 10.0 and c["t_spread"] <= c["t_fac"] / 5.0
    b = cs["best"]
    assert b["immune"] and b["protect"] and abs(b["r66"] - c["r66"]) < 1e-6 and b["rm"][0] == c["rm"][0] and b["layout"] == c["layout"]
    assert c["r66_code"] == "C861590" and c["rm"][1] == "C705766" and c["layout"] == "ahead" and c["n_cf"] == 5
    # no candidate of more energy holds the three conditions, and the filter's size balances the two unprinted rooms
    assert cs["top_e"] == (round(b["energy"][1][2], 6), round(b["energy"][3][2], 6)) and cs["n_cands"] >= len(cs["top"]) >= 1
    assert max(min(lb_, rr_) for *_x, lb_, _ta, rr_ in cs["top"]) == min(cs["loop_be"], cs["best"]["resp_room"])
    assert c["g_cm_be_b"] >= 1.0 and c["i_b_be_b"] >= rw["ipin169"] and c["t_allow"] >= c["t_fac"] * c["t_resp_typ"]
    s = _s10(R)
    assert "THE SETTING (SESSION, the margin decided by what it must absorb, no percentage)" in s and "round 3's choice" in "\n".join(_CACHE["M"].render(R))


def t_check_b_counts_the_capacitor_input_energy_the_panels_current_and_the_events():
    R = _R()
    d = R["decision"]
    c, rw = d["c"], d["rows"]
    za = rw["za"]
    cmax = 3 * za["c"] * (1 + za["tol"]) * (1 + za["end_dc"]) + (0.1e-6 + 4 * 10e-6 + 24.8e-6) * 1.10
    assert abs(c["c_entry_max"] - cmax) < 1e-12 and abs(c["e_cap"] - cmax * 625.0) < 1e-12 and c["n_ca"] == 4
    assert abs(c["i_src"] - rw["isc_hot"] * (1 + rw["tol_p"])) < 1e-12 and abs(c["i_src"] - rw["amps_pk"]) > 0.05
    assert abs(c["t_allow"] - ((100.0 - c["p_static"]) * d["w_avg"] - c["e_cap"] - c["e_f"]) / (c["p_src"] - c["p_static"])) < 1e-12
    assert abs(c["e_f"] - 25.0 * c["i_hi25"] * c["tau"][1]) < 1e-9 and c["tau"][1] > c["tau"][0] > 0
    assert c["e_window_typ"] <= 100.0 * d["w_avg"] and c["e_start"] < 1.0 and c["td_min"] > d["w_avg"]
    assert c["cycle_be"] > 1.0 and 0 < c["cycle_e"] < c["e_cap"]
    assert abs(rw["tpd_lh"] - 28.1e-6) < 1e-12
    s = _s10(R)
    assert "7b.16" in s and "%.3f ms" % (1e3 * c["t_allow"]) in s and "SWEN held low" in s and "CONDITIONAL" in s


def t_the_supply_sequencing_is_default_off_on_printed_rows():
    R = _R()
    sq, rw = R["decision"]["seq"], R["decision"]["rows"]
    assert sq["guard_v"] > sq["vdd_sense"] >= max(sq["vdd38"], sq["vdd_t"]), "SWEN could rise below a sensing part's supply range"
    assert sq["sw_hi_min"] > sq["swen"][1] and sq["i_reset"] <= 1e-3 and sq["rel_hi"] < sq["ldo_lo"] and sq["td_min"] >= 0.18 > rw["st_t"]
    assert sq["i_sw_be"] >= 50e-6 and sq["i_sw_be_dead"] > sq["i_sw_be"] and sq["hys_be"] > 0.5
    assert not {"vpor", "ramp", "ramp_limit", "pin_needed_13"} & set(sq), "the sequencing still leans on the power-up row or a ramp"
    assert sq["uv_ts_lo"] > 2.7 and sq["uv_ts_hi"] < 15.0 and sq["i_ldo"] < 5e-3 and abs(rw["r70"] - 8060.0) < 1e-6 and abs(rw["r71"] - 6040.0) < 1e-6
    c = R["decision"]["c"]
    assert c["vout_hi"] < sq["uv_ts_lo"] - rw["sw169"]
    assert "with no condition on TRK_LDO33's ramp or sag rate and no use of U20's power-up row" in _s10(R)


def t_the_disturbances_come_from_the_approved_plan_and_every_part_holds():
    R = _R()
    d = R["decision"]
    sg, rw = d["surge"], d["rows"]
    ds = sg["dist"]
    assert abs(ds["v101"] - 1.9953) < 1e-3 and abs(ds["v101_150k"] - 0.0668) < 1e-3 and ds["p101"] == (80.0, 0.09)
    assert abs(ds["i114"] - 0.1413) < 1e-3 and ds["esd"] == (8e3, 15e3) and ds["r_esd"] == 330.0 and ds["c_esd"] == 150e-12
    assert abs(sg["d4_der"] - (1.0 - 0.40 * (rw["t_air"] - 25.0) / 125.0)) < 1e-12
    kinds = {x_["kind"] for x_ in sg["cases"]}
    assert kinds == {"capability", "M7"}
    assert sg["worst"]["d59"] < sg["rating"]["csd"] and sg["d59_margin"] >= sg["d59_op"] and sg["alt_ca"][2] > sg["worst_app"]["d59"]
    assert sg["c101"]["d59"] < sg["rating"]["csd"] and sg["c114"]["d59"] < sg["rating"]["csd"]
    assert -min(x_["d59n"] for x_ in sg["cases"]) < sg["rating"]["csd"]
    assert sg["c101"]["v_pk"] < rw["d4"]["vr"] and sg["c101"]["part_w"] < 1.0
    assert sg["v_pk"] < min(sg["rating"]["za_v"], sg["rating"]["cer_v"], sg["rating"]["q3"]) and sg["v_pvp"] < sg["rating"]["vs169"]
    assert sg["d169"] < sg["rating"]["d169"] and sg["v_inb"] < sg["rating"]["tps_in"] and sg["v_ina"] < sg["rating"]["tps_in"]
    assert max(x_["id4"] for x_ in sg["cases"] if x_["kind"] == "capability") < rw["d4"]["ipp"]
    assert 0 < sg["c101"]["ratio_drawn"] <= sg["c101"]["ratio_bound"] and sg["v_bulk"] < sg["rating"]["za_v"]
    s = _s10(R)
    assert "CAPABILITY SCENARIO, labelled" in s and "nothing in series with CSPIN or CSNIN" in s and "the Vishay draft asks" in s
    assert "M2 records the cans' temperature" in s and "a long outdoor lead" in s


def t_the_panel_lead_is_derived_from_the_committed_row_and_judged_per_disturbance():
    """The surge round (the findings ledger's item 1, R-156): the exposure is the lead the records give, the basis is the row REQ-063
    commits to, each disturbance is judged by REQ-016's own criterion, and the clamp and source figures reproduce in closed form."""
    R = _R()
    ld, d = R["lead"], R["decision"]
    le_, rw, sg = ld["lead"], d["rows"], d["surge"]
    assert (le_["m"], le_["mm2"]) == (5.0, 4.0) and abs(le_["r"] - 0.0465) < 5e-4 and abs(le_["f_q"] - 299792458.0 / 20.0) < 1e-6
    assert [ld["tv"][k] for k in ("CS101", "CS114", "CS115", "CS116", "CS117")] == ["A", "A", "A", "A", "S"]
    assert "CS115" not in open(os.path.join(ROOT, "v2", "docs", "TEST-PLAN.md"), encoding="utf-8").read()
    # Figure CS116-2 as drawn, at the six frequencies and the lead's quarter wave
    ips = {round(r_["f"]): r_["ip"] for r_ in ld["r116"]}
    want = {10000: 0.1, 100000: 1.0, 1000000: 10.0, 10000000: 10.0, round(le_["f_q"]): 10.0, 30000000: 10.0, 100000000: 3.0}
    assert set(ips) == set(want) and all(abs(ips[k] - want[k]) < 1e-12 for k in want), ips
    # REQ-016's criterion in closed form: the highest part's breakdown at the hot end (the sheet's typical 0.1 %/C), the printed slope
    d4 = rw["d4"]
    rd = (d4["vc"] - d4["vbr"][1]) / d4["ipp"]
    v10 = d4["vbr"][1] * (1 + 0.001 * (rw["t_air"] - 25.0)) + rd * 10.0
    assert abs(ld["aT"] - 0.001) < 1e-15 and abs(ld["v116"] - v10) < 1e-9 and v10 <= ld["lim_draft"] == 50.0 and v10 > ld["lim_drawn"] == 35.0
    # the loaded network: D4 never conducts under CS116 or CS115, TRK_VS stays under the least breakdown at the cold end
    vbr_cold = d4["vbr"][0] * (1 + 0.001 * (rw["t_cold"] - 25.0))
    assert abs(ld["vbr_cold"] - vbr_cold) < 1e-12 and abs(vbr_cold - 29.70) < 0.005
    assert ld["peak_v"] < vbr_cold and all(r_["id4"] == 0.0 and r_["e_d4"] == 0.0 for r_ in ld["r116"] if r_["lumped"]) and ld["r115"]["id4"] == 0.0
    assert all(r_["d59_b"] < sg["rating"]["csd"] and r_["y_trip"] < ld["m_trip"] for r_ in ld["r116"])
    assert ld["r115"]["be_b"] > ld["r115"]["a"] and ld["r115"]["be_l"] > ld["r115"]["be_b"]
    # the stiff source: the least part at the cold end through the lead's loop, against D4's continuous capability on the board
    i_ = (ld["v_src"] - vbr_cold) / (rd + le_["r"])
    src = {lab_: (i2, p2) for lab_, _v, i2, p2 in ld["src"]}
    assert ld["v_src"] == 36.0 and abs(src["the least part at the cold end"][0] - i_) < 1e-9
    assert min(p_ for _i, p_ in src.values()) > 10 * ld["p_ok"][1] and abs(ld["p_ok"][0] - (150.0 - rw["t_air"]) / 75.0) < 1e-12
    # the smallest change: the least held row that stands off 36 V and does not break down at the cold end, and why it is not enough alone
    r36 = ld["r36"]
    assert r36["n"] == 36 and r36["vbr_cold"] > ld["v_src"] and r36["vc116_25"] <= 50.0 < r36["vc116_h"]
    assert [(v_["id"], v_["ok"], v_["drawn"]) for v_ in ld["verd"]] == [("D1", True, False), ("D2", True, False), ("D3", True, True),
                                                                      ("D4", False, False), ("D5", False, False)]
    s = _s10(R)
    for k in ("THE PANEL LEAD'S DISTURBANCES, DERIVED", "nearby lightning called out in MIL-STD-464", "FOR L4-E9'S REGISTER",
              "the entry's margin beyond that derived basis", "SMCJ36A WITH the entry's 50 V parts", "NOT COVERED"):
        assert k in s, k
    assert "no level is ruled (REQ-016, DECISION-31 section 3), so D4" not in s
    page = " ".join(open(os.path.join(REC, "L4E7-CONTROL-DECISION.md"), encoding="utf-8").read().split())
    for fig in ("%.2f V" % ld["v116"], "%.2f V" % vbr_cold, "%.2f V" % r36["vc116_h"], "%.1f A" % ld["r115"]["be_b"], "SMCJ36A", "CS116", "CS115",
                "%.2f W" % ld["p_ok"][0]):
        assert fig in page, fig
    assert "no level is ruled (REQ-016, DECISION-31 section 3), so D4's own" not in page


def t_the_backstop_holds_through_cs101_and_the_failing_case_is_kept():
    R = _R()
    cs = R["cs101"]
    fl, ra, rb, be = cs["fail"], cs["rem_a"], cs["rem_b"], cs["best"]
    tab = cs["tab"]
    assert len(cs["freqs"]) == 121 and abs(cs["freqs"][0] - 30.0) < 1e-9 and abs(cs["freqs"][-1] - 150e3) < 1e-6
    # the failing case: round 3's circuit trips at every frequency; each remedy alone fails somewhere; the selection nowhere
    assert fl["layout"] == "behind" and abs(fl["r66"] - 8250.0) < 1e-6 and fl["rm"][0] == 30000.0 and fl["n_cf"] == 0
    assert not fl["immune"] and all(not r_[4] for r_ in tab["fail"])
    assert not ra["immune"] and ra["t_allow"] >= 10.0 * R["decision"]["c"]["t_resp_typ"] and not tab["rem_a"][0][4], "(a) alone at 30 Hz"
    assert not rb["immune"] and tab["rem_b"][0][4] and not all(r_[4] for r_ in tab["rem_b"]), "(b) alone"
    assert be["immune"] and all(r_[4] for r_ in tab["best"]) and all(r_[3] <= be["m"] for r_ in tab["best"])
    assert all(max(r_[1], r_[2]) >= r_[3] for r_ in tab["best"]), "a filtered value above its own unfiltered current"
    # remedy (b) taken far cannot lower the voltage-limit setup at all
    assert all(abs(a_[0] - b_[0]) < 1e-9 for _f, a_, b_ in cs["rem_b_add"]) and any(b_[1] < a_[1] - 1e-6 for _f, a_, b_ in cs["rem_b_add"])
    # the coordinator's estimate tested; the loop branch's room; the step crossing times inside the allowance's arithmetic
    es = cs["est"]
    assert es["r30"] > fl["m"] and es["m_hi"] > 10 * fl["m"] and abs(1e3 * es["t_cross"] - 0.196) < 0.01
    assert cs["loop_be"] >= 2.0 and cs["t_stepr"] < cs["t_step0"]
    s = _s10(R)
    for k in ("no upset of the kit's operation, no reset, no loss of a bearer", "That is an upset of the kit's operation",
              "THE CONTROLLING TRADE-OFF", "(i) NO UPSET under M2", "(ii) PROTECTION", "(iii) RATINGS", "the coordinator's starting estimate, tested",
              "M2 (the laboratory validation of CS101, downstream", "what it does not: the bulk's charge"):
        assert k in s, k


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
            for want in ('"36": "TRK_SWEN"', '"33": "TRK_VS"', '"32": "TRK_VIN"', '"TRK_VS", "TRK_VIN", "RS2512"', '"C44322")', '"C132788")',
                         '"C43698")', 'r("R16", "31.6k', 'r("R66", "8.45k', '"C861590")',
                         'for _cf in ("C70", "C75", "C76", "C77", "C78"): c(_cf, "100n NP0 50V", "TRK_BKS", "GND", "C10u50", "C170182")',
                         '"C728595")', 'for _ca in range(4): c("C7%d" % (_ca + 1), "10u 50V", "TRK_VS", "GND", "C10u50")',
                         '{"1": "TRK_VS", "2": "GND"}, "C224047")', 'r("R14", "100k 1%", "TRK_VS", "TRK_SHDN")', '_intent.rail("TRK_VS"',
                         'part("C69", '):
                assert out.count(want) == 1, want
            assert out.count('{"1": "PV_P", "2": "GND"}, "C178637")') == 2 and '"C454360")' not in out and "CSPF" not in out and "C469656" not in out
            assert 'c("C70", "1n", "TRK_BKS"' not in out
            assert out.count('r("R10", "115k 1% (RFBOUT1: 15.1 V)"') == 1
        finally:
            shutil.rmtree(d)
    assert outs[0] == outs[1], "the backstop does not land the same after either order of the three"
    R = _R()
    assert all(R["backstop_draft"].values()), R["backstop_draft"]
    assert R["drafts"][BACKSTOP][3]
    assert _sha(GEN_E) == before, "the tree's gen_sch_e.py changed"


GUARD = "apply_gen_sch_e_solar_guard.py"


def _run_any(path, target, *flags):
    return subprocess.run([sys.executable, "-B", path, target] + list(flags), capture_output=True, text=True, cwd=os.path.dirname(target))


def t_the_solar_fault_remedies_select_one_for_each_fault_and_keep_the_window():
    """The owner's amendment of 2 October 2026, item 3: three implementations compared on held sheets, the selected cut-off and
    return switch each meeting its fault, the cut-off's band recomputed here from the comparator's rows and the divider, the
    window kept, CS101 and check (b) re-run, and the draft applying once after the five drafts it follows."""
    R = _R()
    rm, d = R["remedy"], R["decision"]
    T4, ovs, bA = rm["T48"], rm["ovs"], rm["bandA"]
    assert T4["ovr"] == (1.16, 1.18, 1.2) and T4["ovf"] == (1.1, 1.11, 1.13) and abs(T4["ovleak"] - 300e-9) < 1e-15
    # implementation 1 fails on its own pins, implementation 2 on its CATHODE-to-ANODE rating at the hot end
    assert rm["i1"]["pins"] < rm["i1"]["pins_abs"] and rm["i1"]["ring"] < rm["i1"]["src_abs"] < rm["i1"]["src_rev"]
    assert rm["i2"]["ca36_hot"] > rm["LM"]["ca"] > rm["i2"]["ca36_25"] and 500.0 < rm["i2"]["f_rect"] < 2121.0
    # the band in closed form: the stocked divider aged by the RT sheet's printed limits, the comparator's rows, the leakage
    rws = d["rows"]
    lead = R["lead"]
    k = lambda r, s: (1 + s * 0.001) * (1 + s * 25e-6 * 45.0) * (1 + s * (0.005 + 0.05 / r)) * (1 + s * (0.005 + 0.05 / r))
    a, b, rb = ovs["a"], ovs["b"], ovs["rb"]
    rt_hi = a * k(a, 1) + b * k(b, 1)
    k_lo = (a * k(a, -1) + b * k(b, -1) + rb * k(rb, 1)) / (rb * k(rb, 1))
    k_hi = (rt_hi + rb * k(rb, -1)) / (rb * k(rb, -1))
    assert abs(bA["rise"][0] - (1.16 * k_lo - 300e-9 * rt_hi)) < 1e-9 and abs(bA["rise"][1] - (1.20 * k_hi + 300e-9 * rt_hi)) < 1e-9
    cs101_pk = 25.0 + 2 ** 0.5 * 10 ** (126.0 / 20.0) * 1e-6
    assert abs(rm["cs101_pk"] - cs101_pk) < 1e-6
    d4n = rm["D4N"]
    assert d4n["n"] == 30 and abs(d4n["vbr_cold"] - 33.30 * (1 - 0.001 * 45.0)) < 1e-9
    assert bA["rise"][0] > cs101_pk and bA["rise"][1] < d4n["vbr_cold"] and bA["fall"][0] > 25.0
    assert min(rm["ov28"]["aged"]["m"]) < 0 < min(rm["ov28"]["new"]["m"]), "the SMCJ28A band: fits new, fails aged"
    assert abs(d4n["v116"] - (36.8 * (1 + 0.001 * (rws["t_air"] - 25.0)) + (48.4 - 36.8) / 31.0 * 10.0)) < 1e-9 and d4n["v116"] <= 50.0
    # each fault and disturbance
    assert [(v["id"], v["ok"]) for v in rm["verd"]] == [("D4", True), ("D5", True), ("CS116/115 on", True), ("CS116/115 off", True),
                                                        ("already on", True), ("window", True)]
    vd = {v["id"]: v.get("note", "") for v in rm["verd"]}
    assert "CONDITIONAL on Q13's leakage" in vd["D5"] and "CS115 CONDITIONAL on R-174" in vd["CS116/115 on"]
    assert "CONDITIONAL on the lead's loop inductance at least %.2f uH" % (1e6 * rm["b6"]["Lb"]) in vd["already on"]
    assert vd["D4"] == vd["CS116/115 off"] == vd["window"] == ""
    assert rm["f36"]["st_min"] > 0.04 and rm["f36"]["cut_hi"] < lead["v_src"] and rm["f36"]["ring"] < rm["QF"]["vds"]
    assert rm["rev"]["vds"] < rm["QF"]["vds"] and rm["rev"]["i_be"] > 10 * rm["rev"]["idss"]
    assert rm["scp_f"] < rm["scp_lo"] and rm["v_tmr"] < T4["tmr_v"][0] and rm["ov_in116"] < bA["rise"][0]
    assert rm["off116"]["v"] < rm["QF"]["vds"] and rm["off116"]["inp"] < T4["pin_abs"] and rm["off116"]["floor"] > -1.0
    # the window, the static bound and the re-runs
    c = d["c"]
    assert c["p_static"] < rm["p_static_blk"] < 100.0 and rm["t_allow_blk"] >= rm["t_fac"] * rm["t_resp_typ"] and rm["t_allow_blk"] < c["t_allow"]
    assert max(rm["L11"]["uv"][2], rm["b6"]["inp_on"]) < rm["shdn"] and rm["i_bank_slew"] < c["i_lo_aged"] and rm["b6"]["i_start"] < rm["ocp_lo"]
    cr = rm["cs_re"]
    assert abs(cr["none"]["worst"][2] - R["cs101"]["best"]["worst"][2]) < 1e-9
    assert cr["none"]["worst"][2] <= cr["least"]["worst"][2] <= cr["most"]["worst"][2] < rm["margin"]
    assert rm["gap"][0] == 25.0 and rm["gap"][1] == bA["rise"][1] and rm["gap"][2] > 100.0
    assert 0 < rm["e_blk"][0] < 0.01 * rm["e_day"][0]
    assert all(R["guard_draft"].values()), R["guard_draft"]
    assert R["drafts"][GUARD][3] and not R["drafts"][GUARD][1] and R["drafts"][GUARD][2]
    s = _s10(R)
    for k_ in ("THE SOLAR-FAULT REMEDIES (the owner's amendment of 2 October 2026", "NOT TAKEN. (2) The LM74700-Q1", "SELECTED (SESSION)",
               "THE WINDOW KEPT", "NOT CLAIMED, a residual named for layer 8", "with the block's series resistance ahead of the bulk",
               "STAYING VALID UNCHANGED", "THE TVS-ONLY CHANGE for D4, evaluated and not taken"):
        assert k_ in s, k_
    page = " ".join(open(os.path.join(REC, "L4E7-CONTROL-DECISION.md"), encoding="utf-8").read().split())
    for fig in ("%.2f to %.2f V" % (bA["rise"][0], bA["rise"][1]), "%.3f V over CS101's peak" % ovs["m"][0], "%.3f V under the clamp" % ovs["m"][1],
                "%.4f W" % rm["p_static_blk"], "%.3f ms" % (1e3 * rm["t_allow_blk"]), "%.4f A" % cr["most"]["worst"][2],
                "%.1f W" % rm["gap"][2], "%.2f Wh of %.1f Wh" % (rm["e_blk"][0], rm["e_day"][0]), "%.3f V" % min(rm["ov28"]["aged"]["m"]),
                "SMCJ30A", "apply_gen_sch_e_solar_guard.py", "## The solar-fault remedies"):
        assert fig in page, fig


def t_the_solar_guard_draft_follows_the_five_drafts_on_a_copy():
    need(GEN_E, "board E's generator")
    before = _sha(GEN_E)
    src = open(GEN_E, encoding="utf-8").read()
    chain = [os.path.join(REC, n) for n in ("apply_gen_sch_e_hold.py", "apply_gen_sch_e_input_limit.py", BACKSTOP)] + [
        os.path.join(ROOT, "v2", "docs", "records", "l4e9", "apply_gen_sch_e_hotswap.py"),
        os.path.join(ROOT, "v2", "docs", "records", "l4e11", "apply_gen_sch_e_entry.py")]
    g = os.path.join(REC, GUARD)
    dd = tempfile.mkdtemp(prefix="l4e7-sg-")
    try:
        cp = os.path.join(dd, "gen_sch_e.py")
        open(cp, "w", encoding="utf-8").write(src)
        r = _run_any(g, cp, "--check")
        assert r.returncode == 3 and "a draft this one follows is not applied" in r.stderr, (r.returncode, r.stderr)
        for path in chain:
            assert _run_any(path, cp, "--write").returncode == 0, path
        orig = _sha(cp)
        r = _run_any(g, cp, "--check")
        assert r.returncode == 0 and "CHECK OK" in r.stdout and _sha(cp) == orig, (r.returncode, r.stderr)
        r = _run_any(g, cp, "--write")
        assert r.returncode == 0 and _sha(cp) != orig, r.stderr
        r = _run_any(g, cp, "--write")
        assert r.returncode == 3 and "already applied" in r.stderr, r.stderr
        out = open(cp, encoding="utf-8").read()
        for want in ('"VH2", {"1": "PV_IN", "2": "PV_RTN"}, "C274411")', '"FUSE", {"1": "PV_IN", "2": "PV_F"})', 'ic("U21", 20, "TPS48110AQDGXRQ1', 'r("R87", "4.5mOhm 1% 2512 3W 50ppm',
                     '{"1": "PV_F", "2": "PV_RTN"}, "C80273")', '"PV_RG", "PV_RTN", "GND", lcsc="C473333")', '"C124196")',
                     '{"switch": "U21", "enable_net": "PV_UVLO"}),', '_intent.rail("PV_RTN"', 'part("D4", "Device", "D_Zener", "SMCJ30A',
                     'c("C131", "10u 100V X7R 1210', 'c("C132", "10u 100V X7R 1210', 'c("C126", "330p C0G 100V', 'r("R97", "30.0k 1%',
                     'c("C133", "10u 50V', 'c("C134", "10u 50V"', '"C132", "C133", "C134", "D4", '):
            assert out.count(want) == 1, want
        assert '"1u 100V 1210 (panel port' not in out and 'r("R97", "39k' not in out and 'c("C126", "1n C0G' not in out
        assert '"SMCJ28A (panel surge' not in out and out.count('r("R10", "115k 1% (RFBOUT1: 15.1 V)"') == 1
    finally:
        shutil.rmtree(dd)
    r = _run_any(g, GEN_E, "--write")
    assert r.returncode == 3 and ("NOT RELEASED" in r.stderr or "not applied" in r.stderr), r.stderr
    assert _sha(GEN_E) == before, "the tree's gen_sch_e.py changed"


def t_the_guard_already_on_is_bounded_in_the_loaded_network():
    """The consolidation review's B6 (astra-check-l4close-1): a stiff 36 V source arriving with the solar guard already on.
    The solver against the closed-form series RLC step; the latest corner bounding (the lead's current still rising at every
    command); every rating at the binding inductance on its side of its printed limit; the binding rating and the conductor
    spacing it needs recomputed; below it NOT MET; the drafted network failing and each change necessary; ramps, the cold
    connection, the SOA reading, D11's energy, CS115 carried CONDITIONAL; the page and the draft carrying the figures."""
    R = _R()
    m = _CACHE["M"]
    rm, b6 = R["remedy"], R["remedy"]["b6"]
    # the solver: the port alone (cold), D11 out of reach, against the underdamped series RLC step's first peak
    L, C, Rl, E = 3e-6, 4.5e-6, 0.0465, 36.0
    g = dict(E=E, r_lead=Rl, c131=C, n_ca=4, esr_cer=0.01, n_pc=0, rb=0.0137, r59=0.0155, r_on=0.0045, d4=(1e3, 1.0), d11=(1e3, 1.0),
             ov=1e3, isc=1e6, tau=1e-6, t_ov=4e-6, t_sc=5e-6, t_f=0.2e-6, v_behind=0.0)
    r = m.guard_event(g, 0.0, 0.0, L, (0.0, 1e-4), 1.0, cold=True, dt=2e-9, t_end=30e-6)
    zeta = Rl / 2.0 * (C / L) ** 0.5
    peak = E * (1 + __import__("math").exp(-zeta * __import__("math").pi / (1 - zeta ** 2) ** 0.5))
    assert abs(r["vF"] - peak) < 0.01 * peak, (r["vF"], peak)
    assert abs(r["iL"] - E / (L / C) ** 0.5 * __import__("math").exp(-zeta * __import__("math").atan((1 - zeta ** 2) ** 0.5 / zeta) / (1 - zeta ** 2) ** 0.5)) < 0.02 * E / (L / C) ** 0.5
    # the binding inductance: every rating on its side, U5's positive differential the binding one, below it NOT MET
    W = b6["W"]
    assert W["mono"] and W["why"] == {"SCP"}
    for id_, v, lim, s in b6["vals"]:
        assert (lim - v) * s >= -1e-12, (id_, v, lim)
    assert b6["bind"] == ["u5p"] and 1.0e-6 < b6["Lb"] < 7.04e-6 and abs(W["u5"] - 0.3) < 0.002
    assert "u5p" in b6["fail_lo"] and "inp" in b6["fail_lo"]
    r_c = (4e-6 / __import__("math").pi) ** 0.5
    assert abs(b6["s_star"] - 2 * r_c * __import__("math").cosh(b6["Lb"] / (4e-7 * 5.0))) < 1e-9
    assert W["i4"] == 0.0 and W["vS"] < rm["D4N"]["vbr_cold"] and W["vP"] < 50.0 and W["vF"] < 100.0 and W["slew"] < 60e6
    assert W["soa12"] < 1.0 and W["soa13"] < 1.0 and b6["e11"] < b6["e11_room"] and b6["i_cs"] < b6["ics_abs"]
    assert b6["der"][0] < 1.0 and b6["tc"][0] > R["decision"]["rows"]["t_air"]
    # each change necessary; the drafted network fails PV_F, its slew, INP and U5
    var = dict(b6["var"])
    assert all(var.values())
    assert sorted(i for i, _v, _l in var["as drafted in the remedies round (C131 1 uF, R97 39k, CSCP 1 nF, no C133 and C134)"]) == ["inp", "pvf", "slew", "u5p"]
    # ramps and the cold connection
    assert b6["ramp_ok"] and all(r_["i4"] == 0.0 for r_ in b6["ramp"]) and b6["ramp_w"]["vS"] < rm["D4N"]["vbr_cold"]
    assert b6["cold_ok"] and max(c["vF"] for c in b6["cold"]) < 100.0
    assert sum(1 for r_ in b6["ramp"] if 0.7 * b6["s_h"] - 100.0 <= r_["rate"] <= 1.1 * b6["s_h"] + 100.0) >= 35
    # CS115 carried CONDITIONAL; CS116's screen as the review computes it
    assert abs(b6["d59_116"] - 0.2123) < 0.0005 and abs(b6["be115"] - 15.680) < 0.002
    assert rm["scp_f"] < rm["scp_lo"] and abs(b6["tau"][0] - 3010 * 0.99 * 330e-12 * 0.95) < 1e-15
    s = _s10(R)
    for k_ in ("THE GUARD ALREADY ON (B6", "THE BINDING RATING", "THE REVIEWED CASE", "RAMPS (from", "THE COLD CONNECTION",
               "THE CHANGES, AND WHY EACH", "R-176's bench rows, REVISED", "CS115 CONDITIONAL on R-174"):
        assert k_ in s, k_
    page = " ".join(open(os.path.join(REC, "L4E7-CONTROL-DECISION.md"), encoding="utf-8").read().split())
    for fig in ("%.2f uH" % (1e6 * b6["Lb"]), "%.2f mm" % (1e3 * b6["s_star"]), "%.4f V" % W["u5"], "%.1f A" % W["iQ"],
                "%.3f V" % (rm["D4N"]["vbr_cold"] - b6["ramp_w"]["vS"]), "%.3f A" % b6["i_start"], "%.2f A" % b6["be115"],
                "### The guard already on (B6 of the consolidation review)", "R-176's acceptance, revised"):
        assert fig in page, fig


def t_the_external_reviews_witnesses_reproduce_on_the_record_function():
    """L4-F01 (the external review of the provisional fixes, 2 October 2026): its four witnesses rebuilt with the record's own
    function and parameters (36 V step from U21's least turn-off, no load, 2.47 uH, the aged bulk at -40 C), the bias factor
    per bank (PV_P, TRK_VS, TRK_VIN). They show the drafted network's 0.3 V margin is not robust: the finer step and an
    independent TRK_VS factor each move U5 by more than the margin."""
    R = _R()
    m = _CACHE["M"]
    b6 = R["remedy"]["b6"]
    g = dict(b6["G6"])
    u = lambda k, dt: m.guard_event(g, b6["uvf_lo"], 0.0, 2.47e-6, b6["bulk_cold"], k, dt=dt, t_end=60e-6)["u5"]
    w20, w1 = u(1.0, 20e-9), u(1.0, 1e-9)
    w99, w95 = u((1.0, 0.99, 1.0), 20e-9), u((1.0, 0.95, 1.0), 20e-9)
    assert u((1.0, 1.0, 1.0), 20e-9) == w20
    assert 0.2985 < w20 < 0.3 and 0 < w1 - w20 < 0.001 and w99 > w20 and w95 > 0.303, (w20, w1, w99, w95)


def t_the_clarification_drafts_follow_the_decision():
    R = _R()
    assert R["decision"]["clar"] == ["analog-devices-lt8705a.txt", "milliohm-hojlr2512.txt", "texas-instruments-ina169.txt", "vishay-wsl2512.txt"]
    assert not os.path.exists(os.path.join(CLAR, "texas-instruments-ina250.txt"))
    for nm in ("texas-instruments-ina169.txt", "vishay-wsl2512.txt"):
        raw = open(need(os.path.join(CLAR, nm), nm), encoding="utf-8").read()
        assert raw.startswith("DRAFT FOR THE OWNER TO SEND.") and "contacts no outside party" in raw and all(ord(ch) < 128 for ch in raw), nm
        t = " ".join(raw.split())
        assert "warrant" in t and "production guarantee" in t, nm
    ti = " ".join(open(os.path.join(CLAR, "texas-instruments-ina169.txt"), encoding="utf-8").read().split())
    assert "total error of the output current" in ti and "VIN+ pin" in ti and "1 kOhm" in ti and "supporting" in ti
    ad = " ".join(open(os.path.join(CLAR, "analog-devices-lt8705a.txt"), encoding="utf-8").read().split())
    assert "SWEN" in ad and "input current" in ad and "falling threshold" in ad


def t_the_minors_the_l4e9_figures_and_the_faults():
    R = _R()
    d = R["decision"]
    b, c = d["b"], d["c"]
    assert 0 < c["loss"][0] < c["loss"][1] and 0 < b["loss"][0] < b["loss"][1]
    rep = dict((rv, (e_, nr)) for rv, e_, nr in c["check_repro"])
    assert abs(rep[26100.0][0] - 495.3165) < 5e-5 and abs(rep[28700.0][0] - 465.6367) < 5e-5 and abs(100 * rep[26100.0][1] - 10.06) < 5e-3
    assert abs(100 * _approach(R, "A")["noon_red"] - 24.57) < 5e-3
    fl = d["faults"]
    assert fl["defeat"] and fl["stop"] and fl["guard"] and "Layer 8" in fl["acceptance"]
    s = _s10(R)
    assert "the smallest stocked RIMON_IN" in s and "largest stocked RIMON_IN" not in s
    assert "printed 1.0507, applied 1.0240) is withdrawn" in s and "it releases at 3.194 V at most" in s
    assert "%.2fk together, %.2fk to %.2fk with tolerance, drift and aging" % (c["r_load"][0] / 1e3, c["r_load"][1] / 1e3, c["r_load"][2] / 1e3) in s
    assert "at the selected regulation's own currents" in s
    l9 = c["l4e9"]
    assert l9["p_hold_hi"] < 93.0 and l9["reg_hi_hold"] < 3.4713 and "L4-E9'S FIGURES THIS ROUND SETS" in s
    for k in ("line 86", "line 97", "lines 99, 105 and 115", "line 119", "line 307"):
        assert k in s, k


def t_the_decision_page_is_linked_and_carries_the_printed_figures():
    R = _R()
    page = need(os.path.join(REC, "L4E7-CONTROL-DECISION.md"), "the decision page")
    t = " ".join(open(page, encoding="utf-8").read().split())
    for nm in ("L4E7-STAGE-SETTINGS.md", "README.md"):
        assert "L4E7-CONTROL-DECISION.md" in open(os.path.join(REC, nm), encoding="utf-8").read(), nm
    d = R["decision"]
    c, sg, sq = d["c"], d["surge"], d["seq"]
    for a in d["approaches"]:
        assert ("%.4f" % a["bound"]) in t, a["id"]
    for fig in ("%.4f W" % c["p_static"], "%.4f W" % (100.0 - c["p_static"]), "%.4f A" % c["i_lo_aged"], c["model"],
                "%gk" % (c["rm"][0] / 1e3), "%gk" % (c["r66"] / 1e3), "%.3f ms" % (1e3 * c["t_allow"]), "%.1f mJ" % (1e3 * c["e_cap"]),
                "%.3f A" % c["i_src"], "%.4f V" % sg["worst"]["d59"], "%.3f V" % sq["guard_v"], "%.1f %%" % (100 * c["g_cm_be_b"]),
                "%.2f %%" % (100 * c["budget"]["e_tol"]), "%.2f %%" % (100 * c["budget"]["e_sup"])):
        assert fig in t, fig
    assert "\u2013" not in t and "\u2014" not in t
    assert "CONDITIONAL on two named assumptions" in t and "astra-check-l4e7r-2" in t
