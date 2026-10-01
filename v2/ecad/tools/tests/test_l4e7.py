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
Nothing here writes into the tree.
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
                    "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"):
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
