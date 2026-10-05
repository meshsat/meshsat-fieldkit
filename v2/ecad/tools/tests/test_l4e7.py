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
draft applies only after the hold and input limit drafts, and gives its three supply capacitors class D, so board E's generator
composed in L4-E9's change-list order runs past its decoupling table (record l8p's L8P-F01); the drafts to the makers follow the decision and quote its
figures; L4-E9's figures are named. Nothing here writes into the tree.
"""
import contextlib
import hashlib
import importlib.util
import io
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
        for pn in ("CL31B106KBHNNN", "CL32B106KBJNNN", "CL32B225KCJSNN"):
            need(os.path.join(ROOT, "v2/vendor/passives/held/samsung-%s-2026-10-02.json" % pn),
                 "an input of the L4-E7 record (Samsung's held excerpts: its fetch_maker_curves.py)")
        if shutil.which("pdftotext") is None or shutil.which("pdftocairo") is None:
            raise Skip("pdftotext and pdftocairo are needed")
        _CACHE["gen_before"] = _sha(GEN_E)
        sp = importlib.util.spec_from_file_location("l4e7_stage_settings_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        try:
            _CACHE["R"] = m.results()      # from the results cache when its KEY holds for this tree, else computed (nothing written)
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


def t_the_results_cache_renders_the_committed_output_and_its_key_follows_the_numbers():
    """The owner's review (Execution efficiency): compute() is the solver, render() the presentation. The committed cache's KEY holds
    for this tree and rendering it prints the committed output byte for byte; the cache file is the encoding of what it renders; a
    rendering string leaves the KEY's source part unchanged while a numerical constant or a solver function's body changes it; a
    cache whose KEY differs is never rendered from."""
    import json
    _R()
    m = _CACHE["M"]
    committed = open(os.path.join(REC, "l4e7_stage_settings.out"), encoding="utf-8").read()
    data = json.load(open(m.CACHE, encoding="utf-8"))
    assert set(data) == {"key", "parts", "R"} and set(data["parts"]) == {"src", "files", "scans", "solver", "python", "pdftotext"}
    assert data["key"] == m.key_of(data["parts"]) == m.key_of(m.key_parts(data["parts"]["files"])), "the committed cache's KEY does not hold for this tree"
    Rc = m.load_cache()
    assert Rc is not None and "\n".join(m.render(Rc)) + "\n" == committed, "the committed output is not render(cache)"
    dump = lambda x: json.dumps(x, sort_keys=True, separators=(",", ":"))
    assert dump(m._enc(m._dec(data["R"]))) == dump(data["R"])
    # the files part: every pinned input compute() reads is in it, and nothing outside the repository
    assert all(rel in data["parts"]["files"] for rel in m.PINS) and not any(f.startswith(("/", "..")) for f in data["parts"]["files"])
    assert "render" not in data["parts"]["src"] and {"compute", "guard_event_b", "sense_ripple", "CerBank", "PINS", "lead_scan"} <= set(data["parts"]["src"])
    # the source part on synthetic edits of this script's text
    text = open(SCRIPT, encoding="utf-8").read()
    base = m.src_part(text)
    assert base == data["parts"]["src"]
    a = 'wrapP("       ", "       ", "THE THREE APPROACHES (at most three'
    assert text.count(a) == 1 and m.src_part(text.replace(a, a.replace("THREE APPROACHES", "3 APPROACHES"))) == base
    c = "EA2_FLOOR_DIV = 2.0"
    assert text.count(c) == 1 and m.src_part(text.replace(c, "EA2_FLOOR_DIV = 2.5")) != base
    b = 'l59 = g.get("l59", 0.0)'
    assert text.count(b) == 1 and m.src_part(text.replace(b, 'l59 = g.get("l59", 1e-12)')) != base
    # a cache whose KEY differs is never rendered from, and the KEY moves with every part
    with tempfile.TemporaryDirectory() as td:
        bad = dict(data, key="0" * 64)
        p = os.path.join(td, "stale.results.json")
        open(p, "w", encoding="utf-8").write(json.dumps(bad))
        assert m.load_cache(p) is None
    for part in ("src", "files", "scans", "solver", "python", "pdftotext"):
        moved = json.loads(json.dumps(data["parts"]))
        moved[part] = {"changed": True}
        assert m.key_of(moved) != data["key"], part


def _git_status():
    return subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def _lead_tree(td, m):
    """A scratch tree holding the guard's input (a1solar's array_calc.py) and every document of the real tree that states a panel
    lead length today; nothing is written into the repository."""
    for rel in [m.A1_CALC] + sorted({p_ for p_, _l, _v in m.lead_scan()[0]}):
        os.makedirs(os.path.dirname(os.path.join(td, rel)), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, rel), os.path.join(td, rel))


def t_a_new_document_citing_the_input_moves_neither_the_key_nor_the_output():
    """The coordinator's amendment (set 28): a consistent citation changes no computed figure, so it enters neither the results
    cache's KEY nor the output. On a scratch tree (the input and today's citing documents copied, nothing written into the
    repository, whose git status must not change during the test): a new document stating "panel lead ... 5 m" passes the guard as
    a run does it (the citation on stderr), the KEY's scan term and the KEY are unchanged, and the output rendered from the cache is
    the committed one byte for byte; one stating 12 m refuses with exit 3, naming the file, its line and both values."""
    import contextlib, io, json
    R = _R()
    m = _CACHE["M"]
    before = _git_status()
    committed = open(os.path.join(REC, "l4e7_stage_settings.out"), encoding="utf-8").read()
    data = json.load(open(m.CACHE, encoding="utf-8"))
    assert set(data["parts"]["scans"]) == {"lead_input", "iec61000_4_5"} and data["parts"]["scans"]["lead_input"] == m.lead_input()
    with tempfile.TemporaryDirectory() as td:
        _lead_tree(td, m)
        assert m.scan_part(td) == data["parts"]["scans"]
        fx = os.path.join(td, "v2", "docs", "new-record.md")
        open(fx, "w", encoding="utf-8").write("# A new record\n\nThe panel lead runs 5 m from the array to the case.\n")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            ok = m.lead_guard(td, report=True)
        assert ("v2/docs/new-record.md", 3, 5.0) in ok and "v2/docs/new-record.md line 3: 5 m" in err.getvalue()
        parts = json.loads(json.dumps(data["parts"]))
        assert m.scan_part(td) == data["parts"]["scans"] and m.key_of(dict(parts, scans=m.scan_part(td))) == data["key"]
        Rc = m.load_cache()
        assert Rc is not None and "\n".join(m.render(Rc)) + "\n" == committed
        open(fx, "w", encoding="utf-8").write("# A new record\n\nThe panel lead is 12 m long.\n")
        err = io.StringIO()
        try:
            with contextlib.redirect_stderr(err):
                m.lead_guard(td, report=True)
            raise AssertionError("the guard did not refuse 12 m")
        except SystemExit as e:
            msg = err.getvalue()
            assert e.code == 3 and "v2/docs/new-record.md line 3: 12 m" in msg and "LEAD_M = 5 m" in msg, msg
    assert _git_status() == before, "the repository's git status changed during the test"

def t_the_lead_guard_compares_the_stated_length_with_the_input():
    """The coordinator's fixtures (set 28): a document stating "panel lead ... 5 m" passes and is cited; one stating "panel lead ...
    12 m" refuses with exit 3, naming the file and both values; the set 28 preparation's RESULT.md line (F-7) as it stands passes."""
    import contextlib, io
    _R()
    m = _CACHE["M"]
    assert m.lead_input() == 5.0
    before = _git_status()
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.dirname(os.path.join(td, m.A1_CALC)))
        shutil.copyfile(os.path.join(ROOT, m.A1_CALC), os.path.join(td, m.A1_CALC))
        d = os.path.join(td, "v2", "docs", "fixtures")
        os.makedirs(d)
        open(os.path.join(d, "a.md"), "w", encoding="utf-8").write("# A\n\nThe panel lead runs 5 m from the array to the case.\n")
        assert m.lead_guard(td) == [("v2/docs/fixtures/a.md", 3, 5.0)]
        res = os.path.join(ROOT, "v2", "docs", "records", "int28", "RESULT.md")
        if os.path.exists(res):
            line = [ln for ln in open(res, encoding="utf-8").read().splitlines() if ln.startswith("| F-7 |")]
            assert line, "the F-7 line of int28's RESULT.md"
            open(os.path.join(d, "f7.md"), "w", encoding="utf-8").write(line[0] + "\n")
            assert ("v2/docs/fixtures/f7.md", 1, 5.0) in m.lead_guard(td)
        open(os.path.join(d, "b.md"), "w", encoding="utf-8").write("# B\n\nThe panel lead is 12 m long.\n")
        err = io.StringIO()
        try:
            with contextlib.redirect_stderr(err):
                m.lead_guard(td)
            raise AssertionError("the guard did not refuse 12 m")
        except SystemExit as e:
            msg = err.getvalue()
            assert e.code == 3 and "v2/docs/fixtures/b.md line 3: 12 m" in msg and "LEAD_M = 5 m" in msg, msg
        ok, bad = m.lead_scan(td)
        assert ("v2/docs/fixtures/b.md", 3, 12.0) in bad and ("v2/docs/fixtures/a.md", 3, 5.0) in ok
        # a millimetre figure beside the phrase is not a length in metres
        open(os.path.join(d, "b.md"), "w", encoding="utf-8").write("# B\n\nThe panel lead's conductors sit 6.09 mm apart.\n")
        ok2, bad2 = m.lead_scan(td)
        assert not bad2 and not any(p_ == "v2/docs/fixtures/b.md" for p_, _l, _v in ok2)
    assert _git_status() == before, "the repository's git status changed during the test"


@contextlib.contextmanager
def _on_tree(m, td):
    """The script's tree pointed at the scratch tree td, its solver made to fail if reached (a results cache miss would reach it)."""
    def no_compute():
        raise AssertionError("the run reached the solver (a results cache miss)")
    top0, rr0 = m.TOP, m.run_recorded
    m.TOP, m.run_recorded = td, no_compute
    try:
        yield
    finally:
        m.TOP, m.run_recorded = top0, rr0


def _main_on(m, td):
    """main() as a run does it, on the scratch tree td: (exit code, stdout, stderr); the solver is never reached."""
    out_, err_ = io.StringIO(), io.StringIO()
    with _on_tree(m, td), contextlib.redirect_stdout(out_), contextlib.redirect_stderr(err_):
        try:
            code_ = m.main([])
        except SystemExit as e:
            code_ = e.code
    return code_, out_.getvalue(), err_.getvalue()


def _link_key_inputs(td, data):
    """Symlink into td every input the committed results cache's KEY records that td does not already hold (read, never written), so
    a run on td checks the KEY on the same bytes; the documents a test edits are copies made before this."""
    for rel in data["parts"]["files"]:
        if not os.path.lexists(os.path.join(td, rel)):
            os.makedirs(os.path.dirname(os.path.join(td, rel)), exist_ok=True)
            os.symlink(os.path.join(ROOT, rel), os.path.join(td, rel))


def t_a_second_length_in_the_approved_statements_cell_is_caught():
    """The supplier package's external review (finding L4-RC01): the older guard took a statement as approved whenever its Markdown
    table cell held an approved sentence, so "The selected panel lead is 9 m." appended to the cell of R-180's statement (5 m) gave
    no hit and an unchanged scan key. On a scratch tree (the input and today's citing documents copied by _lead_tree, the KEY's
    recorded inputs symlinked and never written, the real R-180 cell taken from L4-E9's DOWNSTREAM-REGISTER.md; nothing written into
    the repository, whose git status must not change during the test), each case run through main() as a run does it, with the
    solver made to fail if reached: the unmodified cell passes and is cited at 5 m; the reviewer's sentence appended to the SAME cell
    refuses with exit 3, naming the file, its line, 9 m and LEAD_M = 5 m, while the cell's own 5 m stays a consistent citation; the
    cell's own 5 m edited to 9 m refuses too; an unrelated sentence appended to the same cell passes with the KEY unchanged, the
    output rendered from the cache byte for byte and the cache file untouched (no recompute)."""
    import json
    _R()
    m = _CACHE["M"]
    reg = "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"
    anchor = "two conductors 6.09 mm apart over 5 m"
    real = open(os.path.join(ROOT, reg), encoding="utf-8").read()
    lines = real.split("\n")
    rows = [i for i, ln in enumerate(lines) if anchor in ln]
    assert len(rows) == 1 and lines[rows[0]].startswith("| R-180 |"), "R-180's row in %s" % reg
    line, cells = rows[0] + 1, lines[rows[0]].split("|")
    cols = [k for k, c in enumerate(cells) if anchor in c]
    assert len(cols) == 1 and cells[cols[0]].count(anchor) == 1, "R-180's statement cell"
    cell = cells[cols[0]]

    def with_cell(text):
        """The real register with R-180's statement cell replaced by text, every other byte unchanged."""
        return "\n".join(lines[:rows[0]] + ["|".join(cells[:cols[0]] + [text] + cells[cols[0] + 1:])] + lines[rows[0] + 1:])

    committed = open(os.path.join(REC, "l4e7_stage_settings.out"), encoding="utf-8").read()
    cache_bytes = open(m.CACHE, "rb").read()
    data = json.loads(cache_bytes)
    refusal = "differs from the derivation's input (%s LEAD_M = 5 m): %s line %d: 9 m; refusing" % (m.A1_CALC, reg, line)
    cited = "consistent panel lead length %s line %d: 5 m (the input 5 m)" % (reg, line)
    before = _git_status()
    with tempfile.TemporaryDirectory() as td:
        _lead_tree(td, m)
        _link_key_inputs(td, data)
        dst = os.path.join(td, reg)
        assert not os.path.islink(dst) and open(dst, encoding="utf-8").read() == real, "the register is a scratch copy"
        # the unmodified cell: consistent at 5 m, the committed output from the cache
        code, out, err = _main_on(m, td)
        assert code == 0 and cited in err and out == committed, (code, err)
        # the reviewer's sentence in the SAME cell: refused; the cell's own 5 m is still compared, and consistent
        open(dst, "w", encoding="utf-8").write(with_cell(cell.rstrip() + " The selected panel lead is 9 m. "))
        ok, bad = m.lead_scan(td)
        assert bad == [(reg, line, 9.0)] and (reg, line, 5.0) in ok, (bad, ok)
        code, out, err = _main_on(m, td)
        assert code == 3 and refusal in err and out == "", (code, err)
        # the cell's own 5 m edited to 9 m: refused
        open(dst, "w", encoding="utf-8").write(with_cell(cell.replace(anchor, anchor[:-3] + "9 m")))
        code, out, err = _main_on(m, td)
        assert code == 3 and refusal in err and out == "", (code, err)
        # an unrelated sentence in the same cell: the KEY unchanged, the committed output from the cache, no recompute
        open(dst, "w", encoding="utf-8").write(with_cell(cell.rstrip() + " The engineer answers this row in the supplier's phase 1. "))
        with _on_tree(m, td):
            assert m.key_of(m.key_parts(data["parts"]["files"])) == data["key"], "unrelated prose moved the KEY"
        code, out, err = _main_on(m, td)
        assert code == 0 and cited in err and out == committed, (code, err)
    assert open(m.CACHE, "rb").read() == cache_bytes and not os.path.exists(m.CACHE + ".tmp"), "the results cache was written"
    assert _git_status() == before, "the repository's git status changed during the test"


def t_an_archived_review_is_left_unread_only_while_designated_and_unchanged():
    """The owner's amendment to L4-RC01's round: a filed external review is a third party's text kept verbatim and may quote a probe
    (the supplier package's review quotes "The selected panel lead is 9 m."); the guard leaves a file unread only when
    ARCHIVED-REVIEWS.yaml lists its path AND its sha256 equals the listed one. In the real tree every listed file is at its listed
    sha256, no stated length differs and no listed file is cited. On a scratch tree (today's citing documents, the designation and the
    listed reviews copied, the KEY's recorded inputs symlinked and never written; the repository's git status unchanged), each case
    run through main() with the solver made to fail if reached: (e) the valid unchanged tree passes, the committed output from the
    cache, the KEY unchanged; (b) the 9 m quotation inside the designated, fingerprint-matching review passes, is not read and is not
    cited; (c) the same text in an undesignated design document named X-AS-RECEIVED.md refuses with exit 3 on its 9 m; (d) the
    designated review with its content changed is read again and refuses on its 9 m."""
    import json
    _R()
    m = _CACHE["M"]
    rev = "v2/docs/records/l4close/REVIEW-SUPPLIER-RELEASE-CANDIDATE-AS-RECEIVED.md"
    held = m.archived()
    assert rev in held, "the release candidate review is designated"
    assert all(_sha(os.path.join(ROOT, p_)) == d_ for p_, d_ in held.items()), "a designated review is not at its listed sha256"
    q = [i + 1 for i, ln in enumerate(open(os.path.join(ROOT, rev), encoding="utf-8").read().split("\n")) if ln == "> The selected panel lead is 9 m."]
    assert len(q) == 1, "the review's quotation"
    ok, bad = m.lead_scan()
    assert bad == [] and not any(p_ in held for p_, _l, _v in ok), (bad, ok)
    committed = open(os.path.join(REC, "l4e7_stage_settings.out"), encoding="utf-8").read()
    cache_bytes = open(m.CACHE, "rb").read()
    data = json.loads(cache_bytes)
    hit = "%s line %d: 9 m" % (rev, q[0])
    before = _git_status()
    with tempfile.TemporaryDirectory() as td:
        _lead_tree(td, m)
        for rel in [m.ARCHIVED] + sorted(held):
            os.makedirs(os.path.dirname(os.path.join(td, rel)), exist_ok=True)
            shutil.copyfile(os.path.join(ROOT, rel), os.path.join(td, rel))
        _link_key_inputs(td, data)
        assert not os.path.islink(os.path.join(td, rev)), "the review is a scratch copy"
        # (e) and (b): passes, the committed output from the cache, the KEY unchanged; the review not read and not cited
        code, out, err = _main_on(m, td)
        assert code == 0 and out == committed, (code, err)
        assert "archived review not read: %s (its sha256 matches %s)" % (rev, m.ARCHIVED) in err and "length %s line" % rev not in err, err
        with _on_tree(m, td):
            assert m.key_of(m.key_parts(data["parts"]["files"])) == data["key"], "the designation moved the KEY"
        skipped = []
        ok, bad = m.lead_scan(td, None, skipped)
        assert bad == [] and rev in skipped and not any(p_ == rev for p_, _l, _v in ok), (bad, ok, skipped)
        # (c): the same text in an undesignated design document named X-AS-RECEIVED.md
        fx = "v2/docs/X-AS-RECEIVED.md"
        shutil.copyfile(os.path.join(td, rev), os.path.join(td, fx))
        code, out, err = _main_on(m, td)
        assert code == 3 and out == "" and "%s line %d: 9 m" % (fx, q[0]) in err and "LEAD_M = 5 m" in err and hit not in err, (code, err)
        os.remove(os.path.join(td, fx))
        # (d): the designated review with its content changed is read again
        open(os.path.join(td, rev), "a", encoding="utf-8").write("\nEdited after filing.\n")
        skipped = []
        ok, bad = m.lead_scan(td, None, skipped)
        assert (rev, q[0], 9.0) in bad and rev not in skipped, (bad, skipped)
        code, out, err = _main_on(m, td)
        assert code == 3 and out == "" and hit in err and "LEAD_M = 5 m" in err, (code, err)
    assert open(m.CACHE, "rb").read() == cache_bytes and not os.path.exists(m.CACHE + ".tmp"), "the results cache was written"
    assert _git_status() == before, "the repository's git status changed during the test"


def t_r176_row_3_carries_the_computed_turn_off_everywhere_it_is_supplied():
    """R-176 row 3's Q12 turn-off figure (the step test's bound) is the computed one, rounded up: the worst over every start, bulk
    corner, D11 end and both fault positions at round 2's loop (b6's W). The output's register paragraph and every current R-176
    row on the page carry that figure; the round-1 history row of the checks table keeps its own."""
    import re
    R = _R()
    b6 = R["remedy"]["b6"]
    amps, us = "%.0f" % (b6["W"]["iQ"] + 0.5), "%.0f" % (1e6 * b6["W"]["ton"] + 0.5)
    assert b6["W"]["iQ"] <= int(amps) < b6["W"]["iQ"] + 1 and 1e6 * b6["W"]["ton"] <= int(us) < 1e6 * b6["W"]["ton"] + 1
    out = " ".join(open(os.path.join(REC, "l4e7_stage_settings.out"), encoding="utf-8").read().split())
    raw = open(os.path.join(REC, "L4E7-CONTROL-DECISION.md"), encoding="utf-8").read()
    page = " ".join(ln for ln in raw.splitlines() if not ln.startswith("| R-176's zero-current acceptance |"))
    page = " ".join(page.split())
    found = []
    for text, where in ((out, "out"), (page, "page")):
        for m_ in re.finditer(r"(?:U21 turning Q12 off \(at most|Q12 off at most) (\d+) A,? within (\d+) us", text):
            found.append((where, m_.group(1), m_.group(2)))
    assert ("out", amps, us) in found and ("page", amps, us) in found and len([f for f in found if f[0] == "page"]) >= 2
    assert all((a_, u_) == (amps, us) for _w, a_, u_ in found), found


def t_recompute_reproduces_the_committed_output():
    """--recompute equals render(cache): the solver run once more (about 30 to 50 minutes on a loaded host), so it runs only when
    L4E7_RECOMPUTE=1 is set."""
    if os.environ.get("L4E7_RECOMPUTE") != "1":
        raise Skip("the solver's own re-run: set L4E7_RECOMPUTE=1")
    import json
    _R()
    m = _CACHE["M"]
    committed = open(os.path.join(REC, "l4e7_stage_settings.out"), encoding="utf-8").read()
    R2, files = m.run_recorded()
    assert "\n".join(m.render(m._dec(json.loads(json.dumps(m._enc(R2)))))) + "\n" == committed
    data = json.load(open(m.CACHE, encoding="utf-8"))
    dump = lambda x: json.dumps(x, sort_keys=True, separators=(",", ":"))
    assert dump(m._enc(R2)) == dump(data["R"]) and sorted(files) == sorted(data["parts"]["files"])


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
    # set 28: the guard compares the lengths stated beside a panel lead with the derivation's input (a1solar's LEAD_M, read with ast);
    # every cited file states that value, and the live scan finds nothing that differs
    mm = _CACHE["M"]
    assert ld["input"]["metres"] == le_["m"] == mm.lead_input() and ld["input"]["path"] == mm.A1_CALC and "cited" not in ld
    ok_, bad_ = mm.lead_scan()
    assert not bad_ and all(v_ == le_["m"] for _p, _l, v_ in ok_)
    out_ = " ".join(open(os.path.join(REC, "l4e7_stage_settings.out"), encoding="utf-8").read().split())
    lead_par = out_[out_.index("THE LEAD'S LENGTH AS A CITED INPUT"):out_.index("THE BASIS (SESSION")]
    assert "No stated panel-lead length in v2's documents differs from the input" in lead_par and ld["input"]["path"] in lead_par
    assert not any(p_ in lead_par for p_, _l, _v in ok_), "a citation entered the output"
    if ld["input"]:
        s10 = _s10(R)
        b6 = R["remedy"]["b6"]
        assert "THE LEAD'S LENGTH AS A CITED INPUT (set 27, restated on the input at set 28)" in s10 and "%.3f uH/m at round 2's reference loop" % (1e6 * b6["LA"] / le_["m"]) in s10
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


# L8P-F01 (record l8p, Layer 8's breaker author, 4 October 2026): the backstop declared C66, C67 and C68 against their supply pins
# with no decoupling class, so board E's generator, composed in L4-E9's change-list order, stopped at its G14 table
L4E9_PY = os.path.join(ROOT, "v2", "docs", "records", "l4e9", "l4e9_power_path.py")
# L4-E9's register rows of board E's drafts (DOWNSTREAM-REGISTER.md) and their apply scripts; their order is CHANGE_ORDER's
E_ROWS = {"R-17": ("l4e9", "q1"), "R-12": ("l4e7", "u5_grade"), "R-19": ("l4e7", "hold"), "R-20": ("l4e7", "input_limit"),
          "R-21": ("l4e7", "backstop"), "R-18": ("l4e9", "f1"), "R-94": ("l4e9", "hotswap"), "R-123": ("l4e11", "entry"),
          "R-173": ("l4e7", "solar_guard"), "R-177": ("l4e11", "aux"), "R-16": ("d8dec31", "cin")}
E_NET = os.path.join(ROOT, "v2", "ecad", "pcb-e1-dock-e7", "out", "pcb-e1-dock.net")
L8P_ENABLE = os.path.join(ROOT, "v2", "docs", "records", "l8p", "apply_gen_sch_e_enable.py")
DEC_DOCS = {"C66": ("U18", "5", "SBOS181F", "v2/vendor/ti/held/ti-ina169-sbos181f.pdf"),
            "C67": ("U19", "5", "SBVS240C", "v2/vendor/ti/held/ti-tps3701-sbvs240c.pdf"),
            "C68": ("U20", "6", "SBVS050N", "v2/vendor/ti/ti-tps3808.pdf")}
_STUB = 'def run(parts, sections, power, bypass, header, phase, board_title):\n    return ("A3", 1, 1, 1)\n'
_RUNNER = ('import importlib.util, os, runpy, sys\n'
           '_sp = importlib.util.spec_from_file_location("schlayout", os.path.join(os.path.dirname(os.path.abspath(__file__)), "stub_schlayout.py"))\n'
           '_m = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_m); sys.modules["schlayout"] = _m\n'
           'sys.argv = sys.argv[1:]\n'
           'runpy.run_path(sys.argv[0], run_name="__main__")\n')


def _l4e9_board_e_order():
    """Board E's drafts in L4-E9's change-list order: CHANGE_ORDER's register ids read with ast from l4e9_power_path.py (never
    imported), kept where E_ROWS names an apply script; every board E draft of its CHANGE_SCRIPTS is in it (L4-E11's timer only
    as the LM5069 alternative, R-119); Layer 6's l6r2 tables, outside the list and order-independent, after them as record l8p ran them."""
    import ast
    need(L4E9_PY, "L4-E9's record (its change list)")
    tree = ast.parse(open(L4E9_PY, encoding="utf-8").read()).body
    rows = [n for n in tree if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "CHANGE_ORDER" for x in n.targets)]
    assert len(rows) == 1, "L4-E9's CHANGE_ORDER"
    ids = [e.elts[1].value for e in rows[0].value.elts if isinstance(e, ast.Tuple) and isinstance(e.elts[1], ast.Constant)]
    seq = [E_ROWS[i] for i in ids if i in E_ROWS]
    assert sorted(seq) == sorted(E_ROWS.values()), "L4-E9's change list no longer names each board E draft row once: %s" % ids
    lst = [n for n in tree if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "CHANGE_SCRIPTS" for x in n.targets)]
    assert len(lst) == 1, "L4-E9's CHANGE_SCRIPTS"
    have = {(s_.split("/")[0], s_.split("/")[1][len("apply_gen_sch_e_"):-3]) for s_ in ast.literal_eval(lst[0].value) if "/apply_gen_sch_e_" in s_}
    # P0 round (record l9t5, Slot A, 5 October 2026): L4-E9's list carries P0-7's sense draft (R-240) since P0-7's merge, without which
    # L4-E9's change list refuses the tree; route B2 is out of the baseline (no row, after cx45 Q6); the compositions of this record's
    # earlier rounds predate P0-7 and stay as they were; P0-7's own tests (t_p0sol_) compose its drafts in their places
    assert have - set(seq) <= {("l4e11", "timer"), ("l4e7", "p0sol"), ("l4e7", "p0sol_b2")}, \
        "a board E draft of L4-E9's list outside the composition: %s" % sorted(have - set(seq))
    return seq + [("l6r2", "xal_land"), ("l6r2", "lcsc")]


def _compose_e(d, seq, after_aux=None):
    """A copy of gen_sch_e.py in d with seq applied in order (d8dec31's draft takes the committed netlist, the others --write);
    after_aux, a draft's path, applied right after L4-E11's aux draft (record l8p's slot for its enable draft)."""
    cp = os.path.join(d, "gen_sch_e.py")
    shutil.copy(GEN_E, cp)
    for rec, name in seq:
        s = os.path.join(ROOT, "v2", "docs", "records", rec, "apply_gen_sch_e_%s.py" % name)
        need(s, "board E's draft %s/%s" % (rec, name))
        r = _run_any(s, cp, E_NET) if rec == "d8dec31" else _run_any(s, cp, "--write")
        assert r.returncode == 0, "%s/%s refused: %s" % (rec, name, r.stderr[-300:])
        if after_aux and (rec, name) == ("l4e11", "aux"):
            r = _run_any(after_aux, cp, "--write")
            assert r.returncode == 0, "%s refused: %s" % (after_aux, r.stderr[-300:])
    return cp


def _gen_e_run(gen):
    """A copy of a (patched) gen_sch_e.py run to its end with a stand-in layout step, record l8p's method (its gen_netlist.py): kisch,
    intent and the generator's own checks are the tree's; only schlayout, which needs KiCad's symbol libraries, is replaced by one
    that lays out nothing. (exit code, the run's output, the intent it wrote or None); nothing is written outside a temporary
    directory."""
    import json
    with tempfile.TemporaryDirectory(prefix="l4e7-gen-") as d:
        g = os.path.join(d, "gen_sch_e.py")
        shutil.copy(gen, g)
        open(os.path.join(d, "stub_schlayout.py"), "w", encoding="utf-8").write(_STUB)
        open(os.path.join(d, "run_gen.py"), "w", encoding="utf-8").write(_RUNNER)
        env = dict(os.environ, PYTHONPATH=TOOLS, KICAD_SYMBOLS=os.path.join(d, "no-kicad-symbols"), PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, "-B", os.path.join(d, "run_gen.py"), g, os.path.join(d, "pcb-e1-dock.kicad_sch"), "pcb-e1-dock"],
                           capture_output=True, text=True, cwd=d, env=env)
        ip = os.path.join(d, "out", "pcb-e1-dock-intent.json")
        intent = json.load(open(ip, encoding="utf-8")) if r.returncode == 0 and os.path.isfile(ip) else None
    return r.returncode, r.stdout + r.stderr, intent


def _dec_rows(text):
    """{designator: (class, basis)} of the G14 table (_DEC_CLASS) in a generator's text, read with ast."""
    import ast
    rows = [n for n in ast.walk(ast.parse(text)) if isinstance(n, ast.Assign) and isinstance(n.value, ast.Dict)
            and any(isinstance(x, ast.Name) and x.id == "_DEC_CLASS" for x in n.targets)]
    assert len(rows) == 1, "the generator's G14 table"
    return {k.value: (v.elts[0].value, v.elts[1].value) for k, v in zip(rows[0].value.keys, rows[0].value.values)
            if isinstance(k, ast.Constant) and isinstance(v, ast.Tuple) and all(isinstance(e, ast.Constant) for e in v.elts[:2])}


def t_the_backstop_gives_its_three_supply_capacitors_their_decoupling_class_in_l4e9s_order():
    """L8P-F01 (record l8p at b1295c1e, 4 October 2026): composed in L4-E9's change-list order, board E's generator stopped at its
    G14 table on C66 (U18's V+). On scratch copies: (1) the drafts up to the backstop (L4-E9's order to R-21) give a generator that
    runs to its end with a stand-in layout, its intent naming C66 at U18 pin 5, C67 at U19 pin 5 and C68 at U20 pin 6, each class D
    with its maker's document (held in the tree); the same text without the backstop's class rows (its DEC_ROWS) refuses on C66 as
    the finding read; (2) every board E draft in L4-E9's order (and record l8p's enable draft after L4-E11's aux draft when the tree
    holds it) applies, the composed G14 table gives the three class D, and a refusal of the composed generator, if any, is never a
    missing class of theirs (another record's defect, such as L8P-F03, is that record's); (3) the backstop still refuses the tree's
    own generator (NOT RELEASED), which is unchanged."""
    need(GEN_E, "board E's generator")
    need(E_NET, "board E's committed netlist (d8dec31's draft reads it)")
    for _c, (_u, _p, _doc, rel) in DEC_DOCS.items():
        need(os.path.join(ROOT, rel), "the maker's document of %s" % _c)
    before = _sha(GEN_E)
    seq = _l4e9_board_e_order()
    prefix = seq[:seq.index(("l4e7", "backstop")) + 1]
    assert [x for x in prefix if x[0] == "l4e7"] == [("l4e7", "u5_grade"), ("l4e7", "hold"), ("l4e7", "input_limit"), ("l4e7", "backstop")], prefix
    sp = importlib.util.spec_from_file_location("backstop_for_l8pf01", os.path.join(REC, BACKSTOP))
    bk = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(bk)
    assert sum(1 for _o, rep in bk.EDITS if bk.DEC_ROWS in rep) == 1, "the class rows are not one edit of the backstop draft"
    with tempfile.TemporaryDirectory(prefix="l4e7-f01-") as d:
        cp = _compose_e(d, prefix)
        text = open(cp, encoding="utf-8").read()
        dec = _dec_rows(text)
        for c_, (u_, p_, doc, rel) in DEC_DOCS.items():
            assert dec.get(c_, ("",))[0] == "D" and doc in dec[c_][1] and rel in dec[c_][1], (c_, dec.get(c_))
        rc, log, intent = _gen_e_run(cp)
        assert rc == 0 and intent is not None, "the composition to the backstop does not run to its end: %s" % log.strip().splitlines()[-1:]
        by = {e["cap"]: e for e in intent["bypass"]}
        for c_, (u_, p_, doc, _rel) in DEC_DOCS.items():
            e = by.get(c_)
            assert e and (e["part"], e["pin"], e.get("class")) == (u_, p_, "D") and doc in e.get("basis", ""), (c_, e)
        # the defect as the finding read: the same text without the backstop's class rows stops at C66
        bare = os.path.join(d, "bare_gen_sch_e.py")
        assert text.count(bk.DEC_ROWS) == 1
        open(bare, "w", encoding="utf-8").write(text.replace(bk.DEC_ROWS, ""))
        rc, log, _i = _gen_e_run(bare)
        assert rc != 0 and "decoupling entry C66 -> U18.5 carries no class (G14)" in log, log.strip().splitlines()[-1:]
    variants = [None] + ([L8P_ENABLE] if os.path.isfile(L8P_ENABLE) else [])
    for extra in variants:
        with tempfile.TemporaryDirectory(prefix="l4e7-f01-all-") as d:
            cp = _compose_e(d, seq, after_aux=extra)
            dec = _dec_rows(open(cp, encoding="utf-8").read())
            assert all(dec.get(c_, ("",))[0] == "D" for c_ in DEC_DOCS), {c_: dec.get(c_) for c_ in DEC_DOCS}
            rc, log, intent = _gen_e_run(cp)
            for c_, (u_, p_, _doc, _rel) in DEC_DOCS.items():
                assert "decoupling entry %s -> %s.%s carries no class" % (c_, u_, p_) not in log, log.strip().splitlines()[-1:]
            if rc == 0:
                by = {e["cap"]: e for e in intent["bypass"]}
                assert all(by[c_].get("class") == "D" for c_ in DEC_DOCS), {c_: by.get(c_) for c_ in DEC_DOCS}
    r = _run(BACKSTOP, GEN_E, "--write")
    assert r.returncode == 3 and "NOT RELEASED" in r.stderr, r.stderr
    assert _sha(GEN_E) == before, "the tree's gen_sch_e.py changed"


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
    assert [(v["id"], v["ok"]) for v in rm["verd"]] == [("D4", False), ("D5", True), ("CS116/115 on", True), ("CS116/115 off", True),
                                                        ("already on", False), ("window", True)]
    vd = {v["id"]: v.get("note", "") for v in rm["verd"]}
    assert "CONDITIONAL on Q13's leakage" in vd["D5"] and "CS115 CONDITIONAL on R-174" in vd["CS116/115 on"]
    assert "round 2's %.2f uH is WITHDRAWN as a passing floor" % (1e6 * rm["b6"]["LA"]) in vd["already on"] and "B6-ENG-1" in vd["already on"]
    assert rm["verd"][4]["holds"] is False and rm["verd"][4]["budget_stated"] and "no loop is claimed to pass" in rm["verd"][4]["note"]
    assert vd["CS116/115 off"] == vd["window"] == "" and "round 5" in vd["D4"] and "no lead resistance credited" in vd["D4"]
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
                     'c("C131", "2.2u 100V X7R 1210 Samsung CL32B225KCJSNNE', 'for _cf in ("C132", "C135", "C136"): c(_cf, "2.2u 100V X7R 1210 Samsung CL32B225KCJSNNE',
                     'c("C126", "330p C0G 100V', 'r("R97", "28.0k 0.1% 25ppm', 'c("C133", "10u 50V X7R 1210 Samsung CL32B106KBJNNNE',
                     'c("C134", "10u 50V X7R 1210 Samsung CL32B106KBJNNNE"', 'c("C7%d" % (_ca + 1), "10u 50V X7R 1210 Samsung CL32B106KBJNNNE',
                     '"C132", "C133", "C134", "C135", "C136", "D4", '):
            assert out.count(want) == 1, want
        assert '"1u 100V 1210 (panel port' not in out and 'r("R97", "39k' not in out and 'c("C126", "1n C0G' not in out
        assert 'c("C7%d" % (_ca + 1), "10u 50V", ' not in out and '"10u 100V X7R 1210 (panel port' not in out
        assert '"SMCJ28A (panel surge' not in out and out.count('r("R10", "115k 1% (RFBOUT1: 15.1 V)"') == 1
    finally:
        shutil.rmtree(dd)
    r = _run_any(g, GEN_E, "--write")
    assert r.returncode == 3 and ("NOT RELEASED" in r.stderr or "not applied" in r.stderr), r.stderr
    assert _sha(GEN_E) == before, "the tree's gen_sch_e.py changed"


def t_the_guard_already_on_is_bounded_in_the_loaded_network():
    """B6 round 2 (the external review's L4-F01): the margin decided first (U5 within +-0.240 V, the numerical error added); the
    round-2 solver reproduces the round-1 solver on flat capacitors and the closed-form series RLC step inside 0.3 %; the maker's
    curves bound each bank on its own; the timestep study's error is small against the margin; the selected network holds every
    rating with its margin from its floor and fails under it; the sixteen combinations of the banks' bounds all hold there, the
    selected corner the worst on U5; the approaches B (excluded by the sheet) and D (no OV pin) are
    stated; ramps, the cold connection and the start hold; the page and the draft carry the figures and the engineer's row."""
    import math
    R = _R()
    m = _CACHE["M"]
    rm, b6 = R["remedy"], R["remedy"]["b6"]
    # the round-2 solver against the round-1 solver, flat banks of the same constants (k = 0.5 in every bank)
    g1 = dict(b6["G1"])
    k = 0.5
    flat = lambda c: m.CerBank([(1, c, None, 1.0, 1.0)])
    g2 = dict(g1, bF=flat(g1["c131"]), bP=flat(g1["n_pc"] * 10e-6 * 0.9 * k), bS=flat(g1["n_ca"] * 10e-6 * 0.9 * k),
              bC=flat((20e-6 * k + 4.8e-6) * 1.10), esrP=g1["esr_cer"] / g1["n_pc"], esrS=g1["esr_cer"] / g1["n_ca"])
    for v0, i0 in ((7.46, 0.0), (25.0, 3.7408)):
        r1 = m.guard_event(g1, v0, i0, 3.0e-6, b6["bulk_cold"], k)
        r2 = m.guard_event_b(g2, v0, i0, 3.0e-6, b6["bulk_cold"])
        for key in ("u5", "vF", "vS", "iQ", "slew"):
            assert abs(r1[key] - r2[key]) <= 1e-6 * max(1.0, abs(r1[key])), (key, r1[key], r2[key])
    # the closed-form series RLC step: the port alone (cold), D11 out of reach
    L, C, Rl, E = 3e-6, 4.5e-6, 0.0465, 36.0
    gc = dict(g2, E=E, r_lead=Rl, bF=flat(C), d11=(1e3, 1.0), v_behind=0.0)
    r = m.guard_event_b(gc, 0.0, 0.0, L, (0.0, 1e-4), cold=True, dt=2e-9, t_end=30e-6)
    zeta = Rl / 2.0 * (C / L) ** 0.5
    peak = E * (1 + math.exp(-zeta * math.pi / (1 - zeta ** 2) ** 0.5))
    ipk = E / (L / C) ** 0.5 * math.exp(-zeta * math.atan((1 - zeta ** 2) ** 0.5 / zeta) / (1 - zeta ** 2) ** 0.5)
    assert abs(r["vF"] - peak) < 0.003 * peak and abs(r["iL"] - ipk) < 0.003 * ipk, (r["vF"], peak, r["iL"], ipk)
    # the margin and the timestep
    assert b6["U5_LIM"] == 0.240 and b6["M_OTHER"] == 0.10
    conv = b6["conv"]
    assert [dt for dt, _u in conv] == [40e-9, 20e-9, 10e-9, 5e-9, 2e-9, 1e-9, 0.5e-9]
    assert abs(b6["ERR"] - 2 * max(abs(u - conv[-1][1]) for dt, u in conv if dt <= 20e-9)) < 1e-12
    assert 0 < b6["ERR"] < 0.1 * (0.3 - b6["U5_LIM"]) and abs(conv[-2][1] - conv[-1][1]) < 0.25 * b6["ERR"]
    # the makers' curves and the bounds
    for pn, (tf, esr) in b6["bounds"].items():
        assert pn in ("CL31B106KBHNNN", "CL32B106KBJNNN", "CL32B225KCJSNN") and 0.9 < tf[0] <= 1.0 <= tf[1] < 1.1 and 0.001 < esr < 0.02
    ce = b6["ceff"]
    assert ce["F_lo"][1] < ce["F_lo"][0] < 4 * 2.2e-6 and ce["S_lo"][1] < ce["S_lo"][0] < 4 * 10e-6 and ce["C_hi"][1] < ce["C_hi"][0] <= (20e-6 + 4.8e-6) * 1.1 + 1e-12
    # the drafted network at round 2's reference loop (no passing floor claimed, round 5), U5 binding, failing under it
    W = b6["W"]
    # round 5: at round 2's reference loop the only resistive rating outside its line is U5's positive peak, and only for a fault at
    # the connector (no lead resistance credited); the far-end case is round 2's figure; no passing floor is claimed
    fails = [id_ for id_, v, lim, s in b6["valsA"] if (lim - v) * s < -1e-12]
    # every rating outside its line at the reference loop is one whose least loop on the grid lies above it (a property, round 5)
    assert "u5p" in fails and all(isinstance(b6["lsA"][f], float) and b6["lsA"][f] > b6["LA"] for f in fails)
    assert b6["LA"] == 3.3e-6 == b6["L_REF"] and set(b6["r_cases"]) == {0.0, b6["r_lead"]}
    assert abs(b6["u5_case"][b6["r_lead"]] + b6["ERR"] - 0.240) < 0.002 and b6["u5_case"][0.0] + b6["ERR"] > b6["U5_LIM"] and W["u5"] == b6["u5_case"][0.0]
    assert "u5p" in b6["bindA"] and set(b6["bindA"]) <= set(fails) and 1.0e-6 < b6["LD"] < b6["LA"]
    assert "u5p" in b6["fail1"] and b6["W1u"]["u5"] > 0.3 and W["mono"] and W["i4"] == 0.0 and W["soa12"] < 1.0 and W["soa13"] < 1.0
    # the corner search: the four banks independent, every combination of their bounds at the floor holds, the selected corner the worst
    cn = b6["cnr"]
    # round 5: with the connector case some combinations fail; every failure is U5's positive peak or INP (PV_F and TRK_VS stay under
    # their lines over all sixteen), and the selected corner is still the worst on U5
    assert len(cn) == 16 and len({c["c"] for c in cn}) == 16 and any(c["ok"] for c in cn) and not all(c["ok"] for c in cn)
    assert all(set(c["fails"]) <= {"u5p", "inp"} for c in cn) and max(c["vF"] for c in cn) < 90.0 and max(c["vS"] for c in cn) < rm["D4N"]["vbr_cold"]
    assert b6["cnr_w"]["c"] == ("lo", "lo", "lo", "hi") and abs(b6["cnr_w"]["u5"] - W["u5"]) < 1e-12
    assert min(c["u5"] for c in cn) < W["u5"]
    r_c = (4e-6 / math.pi) ** 0.5
    assert abs(b6["sA"] - 2 * r_c * math.cosh(b6["LA"] / (4e-7 * 5.0))) < 1e-12
    # the witnesses, the approaches, ramps, the cold connection and the start
    wl = [u for _l, u in b6["wit"]]
    assert 0.2985 < wl[0] < 0.3 and 0 < wl[1] - wl[0] < 0.001 and wl[2] > wl[0] and wl[3] > 0.303 and wl[4] > 0.45 and b6["witA"] < wl[0]
    assert abs(b6["lim_err"] - 10.0 * b6["ibias_sum"] / (rm["i_reg_hi"] * b6["G6"]["r59"])) < 1e-12 and 0.005 < b6["lim_err"] < 0.01
    assert b6["ibias_sum"] == 31e-6 and b6["tsc11"][1] == 1.6 and b6["tsc"][1] == 5.0 and b6["tinp"] == 1.0
    assert b6["ramp_ok"] and all(r_["i4"] == 0.0 for r_ in b6["ramp"]) and b6["ramp_w"]["vS"] < rm["D4N"]["vbr_cold"]
    # round 5: the cold ring at a connector fault (no lead resistance credited) is inside the absolute ratings but outside the 10 %
    # margin lines near the envelope's floor; with the lead's resistance credited (round 2's case) it holds the margins
    cc = b6["cold_c"]
    assert not b6["cold_ok"] and b6["cold_abs_ok"] and b6["cold_r"]["ok"] and not cc["ok"]
    assert not (cc["vF"] <= 90.0 and cc["slew"] <= 0.9 * b6["slew_abs"] and cc["vF"] * b6["kinp"] <= 18.0) and cc["vF"] <= 100.0 and cc["slew"] <= b6["slew_abs"]
    assert b6["cold_from"] is not None and 0.30e-6 < b6["cold_from"] < 10.2e-6 and "round 5" in rm["verd"][0]["note"]
    assert b6["i_start"] < rm["ocp_lo"] and b6["e11"] < b6["e11_room"] and b6["i_cs"] < b6["ics_abs"]
    assert abs(b6["d59_116"] - 0.2123) < 0.0005 and abs(b6["be115"] - 15.680) < 0.002
    s = _s10(R)
    for k_ in ("THE GUARD ALREADY ON, ROUND 2", "THE MARGIN, decided before any value", "THE REVIEW'S WITNESSES", "THE PARTS AND THEIR BOUNDS",
               "THE CORNER SEARCH at", "THE THREE APPROACHES", "THE ENGINEER'S ROW B6-ENG-1", "R-176's bench rows, REVISED", "CS115 CONDITIONAL on R-174",
               "do not place resistors in series with any of the CSxIN or CSxOUT pins"):
        assert k_ in s, k_
    page = " ".join(open(os.path.join(REC, "L4E7-CONTROL-DECISION.md"), encoding="utf-8").read().split())
    for fig in ("%.2f uH" % (1e6 * b6["LA"]), "%.2f mm" % (1e3 * b6["sA"]), "%.4f V" % (W["u5"] + b6["ERR"]), "%.6f V" % b6["ERR"],
                "%.2f uH" % (1e6 * b6["LD"]), "%.6f V" % b6["witA"], "%.3f A" % b6["i_start"], "%.2f A" % b6["be115"], "B6-ENG-1", "**The corner search**", "%.4f to %.4f V" % (min(c["u5"] for c in cn), b6["cnr_w"]["u5"]),
                "### The guard already on (B6): round 1, and round 2 after the external review (L4-F01)", "R-176's acceptance, revised again"):
        assert fig in page, fig


def t_the_external_reviews_witnesses_reproduce_on_the_record_function():
    """L4-F01 (the external review of the provisional fixes, 2 October 2026): its four witnesses rebuilt with the record's own
    round-1 function and parameters (36 V step from U21's least turn-off, no load, 2.47 uH, the aged bulk at -40 C), the bias
    factor per bank (PV_P, TRK_VS, TRK_VIN), as the record prints them."""
    R = _R()
    m = _CACHE["M"]
    b6 = R["remedy"]["b6"]
    g = dict(b6["G1"])
    u = lambda k, dt: m.guard_event(g, b6["uvf_lo"], 0.0, 2.47e-6, b6["bulk_cold"], k, dt=dt, t_end=60e-6)["u5"]
    got = [u(1.0, 20e-9), u(1.0, 1e-9), u((1.0, 0.99, 1.0), 20e-9), u((1.0, 0.95, 1.0), 20e-9), u((0.25, 0.25, 1.0), 20e-9)]
    assert got == [w for _l, w in b6["wit"]], (got, b6["wit"])
    assert abs(got[0] - 0.299128) < 2e-5 and abs(got[1] - 0.299598) < 2e-5 and abs(got[2] - 0.300218) < 2e-5 and abs(got[3] - 0.304662) < 2e-5


def t_route_3_the_sense_moved_off_the_input_capacitance_does_not_hold():
    """B6 round 3 (the coordinator's one design-convergence attempt): the periodic model of the sense in operation reproduces its
    two limits; every split of the input ceramics is judged on the transient at 0.30 uH with the parasitics added and on the
    sense's printed operating range at the 25 V corner; none holds both, so route 3 is result (ii) and B6-ENG-1 stands; the
    as-drafted split leaves the operating range at that corner (the new finding B6-ENG-2); the parasitics' budget at the
    selected network's floor stays inside round 2's margin; the page and the clarification carry it."""
    R = _R()
    m = _CACHE["M"]
    b6 = R["remedy"]["b6"]
    r3 = b6["r3"]
    assert abs(r3["V_OP"][0] + 0.1) < 1e-12 and abs(r3["V_OP"][1] - 0.1) < 1e-12 and r3["F_LO"] == 170e3 and abs(r3["L1_LO"] - 8e-6) < 1e-12 and r3["T_RF"] == 20e-9 and r3["L59"] == 5e-9
    assert r3["xrow"][:2] == ("6.80", "9.00") and r3["V_OUTS"][0] == 12.0 and abs(r3["V_OUTS"][1] - 15.0875) < 1e-3
    for pn, esl in r3["esl"].items():
        assert 0.5e-9 < esl < 1.5e-9 and 1.0 < r3["srf"][pn] < 5.0, (pn, esl)
    # the periodic model's limits, re-run here: a huge bank behind reads the flat average, none behind reads M1's peak
    vf1 = m.sense_ripple((2e-5, 0.002, 0.8e-9), (1.0, 1e-4, 0.0), r3["i_reg_hi"], 25.0, 12.0, r3["F_LO"], r3["L1_LO"], r3["T_RF"], b6["G6"]["r59"], r3["L59"], b6["G6"]["rb"], r3["bulk_op"], periods=8)
    vf2 = m.sense_ripple((1.0, 1e-4, 0.0), (1e-9, 1e-4, 0.0), r3["i_reg_hi"], 25.0, 12.0, r3["F_LO"], r3["L1_LO"], r3["T_RF"], b6["G6"]["r59"], 0.0, b6["G6"]["rb"], r3["bulk_op"], periods=8)
    assert vf1["peak"] - vf1["trough"] < 0.003 and abs(vf2["r_peak"] - vf2["i_p"] * b6["G6"]["r59"]) < 1e-5     # the 1 F test capacitors drift slowly
    assert abs(vf2["i_p"] - (r3["i_reg_hi"] / 0.48 + 0.5 * 13.0 * 0.48 / (r3["F_LO"] * r3["L1_LO"]))) < 1e-6
    # the splits: seven, the as-drafted first and the sheet's Figure 1 last; none holds both duties; every route-3 split that
    # holds the transient at 0.30 uH leaves the operating range, and the operating range is left by the as-drafted split too
    rows = r3["rows"]
    assert len(rows) == 7 and rows[0]["lab"].startswith("A, as drafted") and rows[6]["lab"].startswith("Figure 1") and rows[6]["cu"] is None
    assert not r3["holds"] and not any(r["holds"] for r in rows)
    assert any(r["holds_u5"] for r in rows[1:6]) and not any(r["holds_tr"] for r in rows) and not any(r["holds_op"] for r in rows)
    for r in rows:
        t3 = r["tr"][0.30e-6]
        assert r["op_peak"] > r["r_peak_reg"] > 0 and r["op_trough"] < 0 and abs(r["err_reg"]) < 0.8 and t3["fails"] and not t3["ok"]
        assert t3["pins_hi"] >= t3["u5"] + b6["ERR"] - 1e-4 and t3["pins_lo"] <= t3["u5n"] - b6["ERR"] + 1e-4 and t3["di_up"] > 0 > t3["di_dn"]
        assert r["holds_u5"] == ("u5p" not in t3["fails"] and "u5n" not in t3["fails"] and t3["pins_hi"] <= b6["csd_abs"] and t3["pins_lo"] >= -b6["csd_abs"])
        assert r["holds_tr"] == (t3["ok"] and r["holds_u5"])
    assert all(r["r_peak_reg"] > r3["V_OP"][1] for r in rows[:6])
    for r in (rows[0], rows[6]):
        assert r["tr"][0.30e-6]["vF"] > 100.0 * (1 - b6["M_OTHER"]) and "pvf" in r["tr"][0.30e-6]["fails"]
    # the property the record prints: every split with ceramics ahead of RSENSE1 (rows 0 to 5) reads over 0.1 V at the regulation's
    # current; the sheet's Figure 1 arrangement (row 6) alone reads under it, and it fails U5's transient at every loop on the grid:
    # the only arrangement inside the operating range does not hold the fault (B6-ENG-2)
    assert abs(rows[0]["tr"][3.3e-6]["u5"] - b6["W"]["u5"]) < 1e-5
    assert all(r["r_peak_reg"] > r3["V_OP"][1] for r in rows[:6]) and rows[6]["r_peak_reg"] < r3["V_OP"][1]
    assert "u5p" in rows[6]["tr"][3.3e-6]["fails"] and r3["floors"][rows[6]["lab"]]["u5p"] is None
    assert all(f in r3["floors"] for f in (rows[1]["lab"], rows[2]["lab"], rows[6]["lab"]))
    # the parasitics' budget at round 2's reference loop (round 5): the rise is over the margin line and Q12's turn-off past it;
    # the inductance scan is monotone and names the largest inductance the margin holds for
    pa = r3["parA"]
    assert pa["up"] > 0 > pa["dn"] and abs(pa["dn"]) > pa["up"] and abs(pa["l_up"] - r3["L59"] * pa["up"]) < 1e-12 and abs(pa["l_dn"] - r3["L59"] * pa["dn"]) < 1e-12
    assert b6["W"]["u5"] + b6["ERR"] - 1e-4 < pa["hi"] and pa["lo"] < b6["W"]["u5n"]
    sc = r3["l59_scan"]
    assert [l for l, _h, _l, _o in sc] == [0.5e-9, 1e-9, 1.5e-9, 2e-9, 3e-9, 5e-9] and all(sc[i][2] >= sc[i + 1][2] for i in range(len(sc) - 1))
    assert abs(sc[-1][1] - pa["hi"]) < 1e-9 and abs(sc[-1][2] - pa["lo"]) < 1e-9      # the scan's 5 nH is the budget's own evaluation
    assert all(ok == (lo >= -b6["U5_LIM"] and hi <= b6["U5_LIM"]) for _l, hi, lo, ok in sc) and r3["l59_ok"] == max([l for l, _h, _l, ok in sc if ok], default=None)
    # the complete budget at round 2's loop is outside the margin line in both polarities, the connector case the worse on the rise
    p0, pr = r3["parA0"], r3["parAr"]
    # the combined budget takes each term's worst over both positions, so it bounds each position's own budget from outside
    assert pa["hi"] > b6["U5_LIM"] and pa["lo"] < -b6["U5_LIM"] and p0["hi"] >= pr["hi"] - 1e-12
    assert max(p0["hi"], pr["hi"]) - 1e-12 <= pa["hi"] < max(p0["hi"], pr["hi"]) + 5e-4 and min(p0["lo"], pr["lo"]) - 5e-4 < pa["lo"] <= min(p0["lo"], pr["lo"]) + 1e-12
    assert p0["u5"] > pr["u5"] and pa["hi"] < b6["csd_abs"]
    assert r3["op_hold"]["r_peak"] < r3["V_OP"][1] and r3["op_l59"][5e-9]["trough"] < r3["op_l59"][1e-9]["trough"] < 0
    s = _s10(R)
    for k_ in ("ROUND 3, ROUTE 3", "THE SPLITS", "THE FLOORS of the splits", "THE PARASITICS' BUDGET", "THE VERDICT ON ROUTE 3 (SESSION): route 3 does NOT hold",
               "A NEW FINDING, independent of B6", "B6-ENG-2", "Discontinuous input current is highest in the buck region"):
        assert k_ in s, k_
    page = " ".join(open(os.path.join(REC, "L4E7-CONTROL-DECISION.md"), encoding="utf-8").read().split())
    rA = rows[0]
    for fig in ("### Round 3: the sense moved off the stage's input capacitance (route 3), result (ii)", "B6-ENG-2",
                "%.4f V" % rA["r_peak_reg"], "%.4f V" % rows[6]["r_peak_reg"], "%+.1f %%" % (100 * rA["err_reg"]), "%+.4f V" % pa["lo"], "%+.4f V" % pa["hi"],
                "%+.4f to %+.4f V" % (p0["lo"], p0["hi"]), "%+.4f to %+.4f V" % (pr["lo"], pr["hi"]),
                "%.4f V" % (rows[1]["tr"][0.30e-6]["u5"] + b6["ERR"]), "%.1f A/us" % (1e-6 * abs(pa["dn"])), "%.2f A/us" % (1e-6 * pa["up"])):
        assert fig in page, fig
    clar = open(os.path.join(REC, "clarification", "analog-devices-lt8705a.txt"), encoding="utf-8").read()
    assert "7. The input current monitor with a pulsed sense voltage" in clar


def t_round_4_the_inp_divider_tolerance_and_pv_fs_operating_row():
    """Round 4 (the Layer 6 author's L6P-F04 and L6P-F10): the draft's R97 carries the tolerance the analysis relies on (0.1 %, a
    named 0.1 % 25 ppm/K series), the record's INP divider is taken at that tolerance; PV_F is judged against the TPS4811-Q1's
    recommended operating row as well as the exclusion line, and the exceedance at the floor is an OPEN item carried in R-176
    and B6-ENG-1 with the loop from which the row holds."""
    import re
    R = _R()
    b6 = R["remedy"]["b6"]
    draft = open(os.path.join(REC, "apply_gen_sch_e_solar_guard.py"), encoding="utf-8").read()
    m = re.search(r'r\("R97", "28\.0k ([\d.]+)% 25ppm \(INP: high from ([\d.]+) V,[^"]*YAGEO RT0603BRD0728KL, LCSC code owed\)", "PV_INP", "GND", "R"\)', draft)
    assert m, "the draft's R97 line"
    m96 = re.search(r'r\("R96", "100k ([\d.]+)% 25ppm \(INP top; YAGEO RT0603BRD07100KL, LCSC code owed\)", "PV_F", "PV_INP", "R"\)', draft)
    assert m96, "the draft's R96 line"
    assert abs(float(m.group(1)) / 100.0 - b6["tol_inp"]) < 1e-12 and abs(float(m96.group(1)) / 100.0 - b6["tol_inp"]) < 1e-12 and b6["tol_inp"] == 0.001
    assert abs(float(m.group(2)) - b6["inp_on"]) < 0.005, (m.group(2), b6["inp_on"])
    assert b6["vs_rec"] == 80.0 and b6["W"]["vF"] > b6["vs_rec"] and b6["pvf80"] is not None and b6["pvf80"] > b6["LA"]
    inp_row = [v for v in b6["valsA"] if v[0] == "inp"][0]
    assert abs(inp_row[1] - b6["W"]["vF"] * b6["kinp"]) < 1e-9 and inp_row[1] <= 20.0
    assert (inp_row[1] > inp_row[2]) == any(v[0] == "inp" and (v[2] - v[1]) * v[3] < -1e-12 for v in b6["valsA"])
    s_ = _s10(R)
    for k_ in ("PV_F'S BASIS (round 4, L6P-F10)", "RECOMMENDED operating row for VS, CS+ and CS- is 80 V", "THE INP DIVIDER (rounds 4 and 5, L6P-F04)",
               "PV_F under the recommended operating 80 V row (OPEN at round 2's loop"):
        assert k_ in s_, k_
    page = " ".join(open(os.path.join(REC, "L4E7-CONTROL-DECISION.md"), encoding="utf-8").read().split())
    for fig in ("%.2f uH" % (1e6 * b6["pvf80"]), "RT0603BRD0728KL", "recommended operating", "%.2f V" % b6["W"]["vF"], "L6P-F04", "L6P-F10",
                "%.2f V" % inp_row[1]):
        assert fig in page, fig


def t_round_5_the_output_and_the_page_agree_on_the_floor_and_the_turn_off():
    """Round 5's residues (the consolidation reading 1a73f5b4): the output's approaches paragraph says what the page's table says,
    (A) a reference loop only with no passing loop, never SELECTED with the floor standing; the budget sentence compares each
    turn-off figure with the absolute maximum and the margin line in words that match its sign, at both fault positions; no
    stale floor wording survives in the output or in the page's budget and approaches."""
    import re
    R = _R()
    b6 = R["remedy"]["b6"]
    r3 = b6["r3"]
    out = " ".join(open(os.path.join(REC, "l4e7_stage_settings.out"), encoding="utf-8").read().split())
    raw_page = open(os.path.join(REC, "L4E7-CONTROL-DECISION.md"), encoding="utf-8").read()
    page = " ".join(raw_page.split())
    # (A): the output's approaches paragraph and the page's row
    i = out.find("THE THREE APPROACHES"); j = out.find("(B) A pin-level limiter", i)
    a_out = out[i:j]
    assert 0 < i < j and "SELECTED" not in a_out and "floor stays" not in a_out and "WITHDRAWN" in a_out and "NO PASSING LOOP" in a_out
    assert "%+.4f to %+.4f V" % (r3["parA0"]["lo"], r3["parA0"]["hi"]) in a_out
    row = [ln for ln in raw_page.splitlines() if ln.startswith("| (A) |")]
    assert len(row) == 1
    cells = [c.strip() for c in row[0].strip("|").split("|")]
    assert "Selected" not in cells[1] and "WITHDRAWN" in cells[2] and "no passing loop" in cells[3].lower()
    # the turn-off against the absolute maximum and the margin line, in words matching the sign, both fault positions
    m0 = re.search(r"at the connector \(no lead resistance credited\) the pins read ([+-][\d.]+) to ([+-][\d.]+) V, and the turn-off's ([+-][\d.]+) V is (PAST|inside) the -([\d.]+) V absolute maximum", out)
    mr = re.search(r"at the lead's far end they read ([+-][\d.]+) to ([+-][\d.]+) V, and the turn-off's ([+-][\d.]+) V is (PAST|inside) the absolute maximum and (past|inside) the -([\d.]+) V margin line", out)
    assert m0 and mr
    lim, line = float(m0.group(5)), float(mr.group(6))
    assert lim == b6["csd_abs"] and line == b6["U5_LIM"]
    t0, tr = float(m0.group(3)), float(mr.group(3))
    assert abs(t0 - r3["parA0"]["lo"]) < 5e-5 and abs(tr - r3["parAr"]["lo"]) < 5e-5
    assert (m0.group(4) == "PAST") == (t0 < -lim) and (mr.group(4) == "PAST") == (tr < -lim) and (mr.group(5) == "past") == (tr < -line)
    mp = re.search(r"Against the ([\d.]+) V margin line the rise is (over|under) it by ([\d.]+) V .*? and the turn-off (is past|stays inside) it by ([\d.]+) V", out)
    assert mp and (mp.group(2) == "over") == (r3["parA"]["hi"] > b6["U5_LIM"]) and (mp.group(4) == "is past") == (r3["parA"]["lo"] < -b6["U5_LIM"])
    # the page's budget bullets say the same, with the sign
    assert ("turn-off's %+.4f V is **PAST the -0.3 V absolute maximum**" % r3["parA0"]["lo"] in page) == (r3["parA0"]["lo"] < -b6["csd_abs"])
    assert "turn-off's %+.4f V is inside the absolute maximum but past the -0.240 V margin line" % r3["parAr"]["lo"] in page
    # no stale floor wording in the output; none in the page's budget and approaches either
    for phrase in ("the floor stays", "(A) SELECTED", "holds from 3.30", "a pass only for a loop", "every rating with its margin for a loop of at least",
                   "every rating with its margin for a source loop of at least", "the floor bisected", "at the floor against", "the floor's",
                   "the turn-off at 5 nH does NOT", "the turn-off at 5 nH stays"):
        assert phrase not in out, phrase
    k = raw_page.find("**The parasitics' budget** at round 2's reference loop"); e = raw_page.find("So RSENSE1's inductance", k)
    budget_page = raw_page[k:e]
    assert 0 < k < e and "does NOT;" not in budget_page and max(len(ln) for ln in raw_page.splitlines()) < 2000


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


# ---- P0-7 (MESHSAT-1357, 5 October 2026): the solar stage's D-10 and D-16 by circuit alternatives (L4E7-P0SOL.md, l4e7_p0sol.py).
# These never call _R(): the record's results cache is re-keyed only by the integrator's recompute; they run P0-7's own parts.
P0SOL = os.path.join(REC, "l4e7_p0sol.py")
P0SOL_OUT = os.path.join(REC, "l4e7_p0sol.out")
P0SOL_DRAFT = os.path.join(REC, "apply_gen_sch_e_p0sol.py")


def _p0sol():
    if "P0" not in _CACHE:
        need(P0SOL, "P0-7's script")
        need(os.path.join(ROOT, ".git"), "a git checkout (the script reads one input at a commit of this branch's history)")
        for rel in ("v2/vendor/power/lt8705a.pdf", "v2/vendor/ti/held/ti-ina169-sbos181f.pdf", "v2/vendor/ti/held/ti-tps3701-sbvs240c.pdf",
                    "v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf", "v2/vendor/passives/held/vishay-wsl-30100-2023-11-23.pdf",
                    "v2/vendor/power/coilcraft-xal1510.pdf"):
            need(os.path.join(ROOT, rel), "an input of P0-7 (held documents: the L4-E7 record's fetch_held_back.py)")
        for pn in ("CL31B106KBHNNN", "CL32B106KBJNNN", "CL32B225KCJSNN"):
            need(os.path.join(ROOT, "v2/vendor/passives/held/samsung-%s-2026-10-02.json" % pn), "Samsung's held excerpts (fetch_maker_curves.py)")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        sp = importlib.util.spec_from_file_location("l4e7_p0sol_under_test", P0SOL)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        _CACHE["P0"] = m
    return _CACHE["P0"]


def t_p0sol_committed_out_is_what_the_script_prints():
    """The committed l4e7_p0sol.out is the script's output on this tree (about 70 s): section 0 reproduces both failing cases
    before any figure, and the script refuses (exit 4) if a reproduction, the composition or a mutation's failure does not hold."""
    m = _p0sol()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = m.main()
        except SystemExit as e:
            raise AssertionError("l4e7_p0sol.py refused (exit %s)" % e.code)
    committed = open(P0SOL_OUT, encoding="utf-8").read()
    assert rc == 0 and buf.getvalue() == committed, "l4e7_p0sol.out is not the script's current output"
    assert "–" not in committed and "—" not in committed


def t_p0sol_the_inputs_it_pins_are_this_trees_files():
    text = open(P0SOL_OUT, encoding="utf-8").read()
    pins = [l.split() for l in text.split("INPUTS (sha256", 1)[1].split("\n\n", 1)[0].splitlines()[1:]]
    assert len(pins) >= 19
    for h, rel in pins:
        assert _sha(os.path.join(ROOT, rel)).startswith(h), rel


def t_p0sol_the_ladder_reproduces_the_records_sense_ripple_and_takes_the_selected_network():
    """The periodic model P0-7 writes out is the record's sense_ripple term for term on the as-drafted split (to 1e-12 V), and
    with RSENSE1 removed it returns the bank's current, which at the 25 V corner never reverses."""
    import json
    m = _p0sol()
    LS = m.load("l4e7_stage_settings_for_test_p0sol", m.LS_PY)
    R = LS._dec(json.load(open(os.path.join(ROOT, m.LS_CACHE), encoding="utf-8"))["R"])
    r3, G6 = R["remedy"]["b6"]["r3"], R["remedy"]["b6"]["G6"]
    row0, rowF = r3["rows"][0], r3["rows"][6]
    s = LS.sense_ripple(row0["cu"], row0["cd"], r3["i_reg_hi"], 25.0, 12.0, r3["F_LO"], r3["L1_LO"], r3["T_RF"], G6["r59"], r3["L59"], G6["rb"], r3["bulk_op"])
    lad = m.ladder(row0["cu"], row0["cd"], r3["i_reg_hi"], 25.0, 12.0, r3["F_LO"], r3["L1_LO"], r3["T_RF"], G6["rb"], 0.0, G6["r59"], r3["L59"], r3["bulk_op"])
    assert abs(max(lad["v59"]) - s["peak"]) < 1e-12 and abs(min(lad["v59"]) - s["trough"]) < 1e-12
    assert abs(max(G6["r59"] * i for i in lad["i59"]) - s["r_peak"]) < 1e-12
    sel = m.ladder(None, rowF["cd"], r3["i_reg_hi"], 25.0, 12.0, r3["F_LO"], r3["L1_LO"], r3["T_RF"], G6["rb"], 5e-9, None, None, r3["bulk_op"])
    assert min(sel["ib"]) > 0.3 and abs(sum(sel["ib"]) / len(sel["ib"]) - r3["i_reg_hi"]) < 1e-3
    assert m.clip_avg([1.0, -1.0, 3.0]) == 4.0 / 3.0


def t_p0sol_the_draft_composes_in_l4e9_order_and_its_netlist_check_bites():
    """Board E's generator composed in L4-E9's change-list order with P0-7's draft after the solar guard: every draft applies, the
    draft refuses a second application, the generator runs to its end, every predicate on the changed nets holds, and each of the
    four mutations fails the check (the check is not blind to the defect it guards)."""
    m = _p0sol()
    K = m.compose_and_check()
    assert not K.get("refused"), K.get("refused")
    assert [s for s, _rc in K["steps"]] == ["%s/%s" % x for x in m.ORDER_E] and all(rc == 0 for _s, rc in K["steps"])
    assert K["second"] == 3 and K["checks"] and all(ok for _s, ok in K["checks"]), K["checks"]
    assert len(K["mutations"]) == 4 and all(r.startswith("FAILS") for _l, r in K["mutations"]), K["mutations"]


def t_p0sol_the_draft_refuses_without_the_drafts_it_follows_and_never_writes_the_tree():
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "gen_sch_e.py")
        shutil.copy(GEN_E, p)
        r = _run("apply_gen_sch_e_p0sol.py", p, "--write")
        assert r.returncode == 3 and "not applied" in r.stderr, r.stderr
        assert open(p, encoding="utf-8").read() == open(GEN_E, encoding="utf-8").read()
    r = subprocess.run([sys.executable, "-B", P0SOL_DRAFT, GEN_E, "--write"], capture_output=True, text=True)
    assert r.returncode == 3 and "NOT RELEASED" in r.stderr, r.stderr
    tree = open(GEN_E, encoding="utf-8").read()
    assert "P0-7" not in tree and '"U23"' not in tree and not os.path.exists(os.path.join(REC, "RELEASE.md"))


def t_p0sol_the_selection_verdicts_and_owed_texts_are_written_where_they_belong():
    out = " ".join(open(P0SOL_OUT, encoding="utf-8").read().split())
    page = " ".join(open(os.path.join(REC, "L4E7-P0SOL.md"), encoding="utf-8").read().split())
    for s in ("REPRODUCED: D-16 stands on the base", "REPRODUCED: D-10 stands on the base", "BYTE-IDENTICAL", "THE SELECTION (SESSION",
              "): (C2).", "D-16 (B6-ENG-2): CORRECTED on the drafted circuit",
              "D-10 (B6, L4-F01): an UNRESOLVED PROTECTION DEFECT in the present model", "REJECTED"):
        assert s in out, s
    for fig in ("0.1174", "-0.3021", "0.3645 A", "2.5378 A", "2.9212 A", "0.1093 A", "16.90 V", "10.05 V", "+1.34 %", "93.5783 W",
                "1.052 ms", "3.67 uA"):
        assert fig in out and fig in page, fig
    assert page.startswith("DONE:") and "NOT DONE:" in page and "NEXT:" in page
    assert "–" not in page and "—" not in page
    readme = open(os.path.join(REC, "README.md"), encoding="utf-8").read()
    for nm in ("L4E7-P0SOL.md", "l4e7_p0sol.py", "apply_gen_sch_e_p0sol.py", "SUPPLIER-P1-1-P0SOL.md", "analog-devices-lt8705a-p0sol.txt"):
        assert nm in readme, nm
    sup = open(os.path.join(REC, "SUPPLIER-P1-1-P0SOL.md"), encoding="utf-8").read()
    clar = open(os.path.join(REC, "clarification", "analog-devices-lt8705a-p0sol.txt"), encoding="utf-8").read()
    assert "UNSENT" in sup.splitlines()[0] and clar.startswith("DRAFT FOR THE OWNER TO SEND. UNSENT.")
    for s in ("Specimen", "Pass:", "Capability needed", "Acceptance"):
        assert s in sup, s


def t_p0sol_b2_composes_after_the_c2_draft_and_its_netlist_check_bites():
    """Route B2 (the coordinator's task of 5 October 2026, 17:12): the presence-loop draft composed in L4-E9's order after P0-7's C2
    draft; every draft applies, it refuses a second application, every predicate holds (C2's nine and B2's four), and each of
    B2's four mutations fails the check."""
    m = _p0sol()
    K = m.compose_and_check_b2()
    assert not K.get("refused"), K.get("refused")
    assert [s for s, _rc in K["steps"]] == ["%s/%s" % x for x in m.ORDER_E_B2] and all(rc == 0 for _s, rc in K["steps"])
    assert m.ORDER_E_B2.index(("l4e7", "p0sol_b2")) == m.ORDER_E_B2.index(("l4e7", "p0sol")) + 1
    assert K["second"] == 3 and len(K["checks"]) == 13 and all(ok for _s, ok in K["checks"]), K["checks"]
    assert len(K["mutations"]) == 4 and all(r.startswith("FAILS") for _l, r in K["mutations"]), K["mutations"]


def t_p0sol_b2_refuses_without_the_c2_draft_and_never_writes_the_tree():
    draft = os.path.join(REC, "apply_gen_sch_e_p0sol_b2.py")
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "gen_sch_e.py")
        shutil.copy(GEN_E, p)
        r = subprocess.run([sys.executable, "-B", draft, p, "--write"], capture_output=True, text=True)
        assert r.returncode == 3 and "not applied" in r.stderr, r.stderr
        assert open(p, encoding="utf-8").read() == open(GEN_E, encoding="utf-8").read()
    r = subprocess.run([sys.executable, "-B", draft, GEN_E, "--write"], capture_output=True, text=True)
    assert r.returncode == 3 and "NOT RELEASED" in r.stderr, r.stderr
    assert "J_SOLP" not in open(GEN_E, encoding="utf-8").read()


def t_p0sol_b2_page_carries_the_authority_finding_the_owner_item_and_the_figures():
    page = " ".join(open(os.path.join(REC, "B2-PRESENCE.md"), encoding="utf-8").read().split())
    out = " ".join(open(P0SOL_OUT, encoding="utf-8").read().split())
    for s in ("reserved.json", "two-part test", "No owner item", "WITHDRAWN AS DRAFTED", "R-180", "make-last", "Layer 6", "authority",
              "ruled_by", "What stays OPEN whatever becomes of B2", "second stiff source added on the same lead"):
        assert s in page, s
    for fig in ("0.544 ms", "84.62 V", "56.10 V/us", "16.90 V", "12.48 V", "0.33 uH", "0.78 uH", "608 events"):
        assert fig in page and fig in out, fig
    assert "5. ROUTE B2" in out and "UNSELECTED, WITHDRAWN AS DRAFTED" in out
    assert "–" not in page and "—" not in page


def t_p0sol_d10_is_written_as_an_unresolved_defect_and_b2_never_as_its_closure():
    """The owner's review of checkpoint 4 (part 23): D-10 is an unresolved protection defect in the present model, written as the
    receiving company's remaining engineering item E-1 with its failing cases, requirements, needed correction and the outputs that
    stay PROVISIONAL; route B2 is an unapproved PARTIAL proposal and no text says adopting or declining it resolves D-10."""
    import re
    texts = {nm: " ".join(open(os.path.join(REC, nm), encoding="utf-8").read().split())
             for nm in ("l4e7_p0sol.out", "L4E7-P0SOL.md", "B2-PRESENCE.md", "SUPPLIER-P1-1-P0SOL.md")}
    sup = texts["SUPPLIER-P1-1-P0SOL.md"]
    for s in ("REMAINING ENGINEERING E-1 (D-10)", "UNRESOLVED PROTECTION DEFECT", "(a) The failing cases", "(b) The applicable requirements",
              "no new exclusion", "(c) The correction or justified model revision needed before any passing claim",
              "(d) What stays PROVISIONAL, and what is completed independently", "| F1,", "| F2,", "| F3,", "| F4,"):
        assert s in sup, s
    for nm, tx in texts.items():
        assert "UNRESOLVED PROTECTION DEFECT" in tx or "unresolved protection defect" in tx, nm
        for m in re.finditer(r"(\S+ \S+ \S+) (resolves?|closes?) D-10", tx):
            assert re.search(r"\b(not|neither|nor|never)\b", m.group(1)), (nm, m.group(0))
        for m in re.finditer(r"B2[^.]{0,80}\b(closes|resolves|closed|resolved)\b D-10", tx):
            assert re.search(r"\b(not|neither|nor|never)\b", m.group(0)), (nm, m.group(0))
    assert "UNSELECTED" in texts["B2-PRESENCE.md"] and "D-10 stays open either way" in texts["B2-PRESENCE.md"]


def t_p0sol_b2_cold_guarantee_withdrawn_and_pair_faults_tabled():
    """Astra's focused check cx45 (5 October 2026, Q6): B2's cold-connection guarantee was claimed without a selected sequenced
    connector or a contact and control timing proof, and "a shorted presence core can only hold INP low" was false. The output
    withdraws the guarantee (5e: the time leads, BST kept charged from VS, bounce, the enable path not simulated), solves the pair's
    faults as a circuit and tables them (5f), and takes no protection credit; no text, the draft's included, keeps either claim."""
    import re
    out = " ".join(open(P0SOL_OUT, encoding="utf-8").read().split())
    for s in ("5d THE ARRIVING SOURCE IF IT MEETS Q12 OFF (a CONDITION, not a result", "5e THE COLD-CONNECTION GUARANTEE, WITHDRAWN",
              "THE TIME LEAD, NOT A DISTANCE", "BST IS NOT DISCHARGED BY A WITHDRAWAL", "charge pump is derived from VS terminal",
              "BOUNCE AND INTERRUPTION", "THE COMPLETE ENABLE PATH is not simulated", "5f THE PRESENCE PAIR'S FAULTS",
              "NO PROTECTION CREDIT", "a defect of the withdrawn draft, REMAINING ENGINEERING outside the baseline",
              "a LATENT loss of B2's function"):
        assert s in out, s
    rows = {}
    for line in open(P0SOL_OUT, encoding="utf-8").read().split("5f THE PRESENCE PAIR'S FAULTS", 1)[1].splitlines():
        mm = re.match(r"\s+(P\d|none)\s+(.+?)\s+(\d+\.\d{4})\s+((?:\s*\d+\.\d\d){6})\s", line)
        if mm:
            rows.setdefault(mm.group(1), []).append((float(mm.group(3)), [float(x) for x in mm.group(4).split()]))
    assert sorted(rows) == ["P1", "P2", "P3", "P4", "P5", "P6", "none"] and len(rows["none"]) == 2, sorted(rows)
    # independent arithmetic from the printed corners: R96 99.9 kOhm at its least, R97 24.92 kOhm at its highest
    r96 = float(re.search(r"R96 at its least ([\d.]+) kOhm", out).group(1))
    r97 = float(re.search(r"R97 at its highest ([\d.]+) kOhm", out).group(1))
    assert abs(rows["P1"][0][0] - r97 / (r96 + r97)) < 2e-4 and rows["P1"][0] == rows["none"][0]
    for p_ in ("P2", "P3"):
        a_, inp_ = rows[p_][0]
        assert abs(a_ - 1.0) < 1e-3 and max(inp_) > 20.0, (p_, inp_)        # INP over its 20 V absolute maximum
    for p_ in ("P4", "P5", "P6"):
        assert max(rows[p_][0][1]) < 0.8, p_                                    # the guard held off
    assert re.search(r"INP over its 20 V absolute maximum from PV_F 20\.00 V", out)
    texts = {nm: " ".join(open(os.path.join(REC, nm), encoding="utf-8").read().split())
             for nm in ("l4e7_p0sol.out", "L4E7-P0SOL.md", "B2-PRESENCE.md", "SUPPLIER-P1-1-P0SOL.md", "apply_gen_sch_e_p0sol_b2.py")}
    for nm, tx in texts.items():
        for m in re.finditer(r"can only hold INP low", tx):
            ctx = tx[max(0, m.start() - 160):m.end() + 60]
            assert "FALSE" in ctx or "withdrawn" in ctx, (nm, ctx)
        for bad in ("never closed when a stiff source arrives", "can only ever arrive cold", "guard-on event is then removed",
                    "such an arrival meets the cold connection", "BST until it charges"):
            for m in re.finditer(re.escape(bad), tx):
                assert "withdrawn" in tx[max(0, m.start() - 160):m.end() + 60], (nm, bad)
    page = texts["B2-PRESENCE.md"]
    for s in ("NO PROTECTION CREDIT", "GUARANTEE is WITHDRAWN", "5a. The cold-connection guarantee, WITHDRAWN",
              "5b. The presence pair's faults", "| P1,", "| P2,", "| P3,", "| P4,", "| P5,", "| P6,"):
        assert s in page, s
    draft = texts["apply_gen_sch_e_p0sol_b2.py"]
    assert "WITHDRAWN" in draft and "not fail-safe" in draft and "No protection credit" in draft


def t_p0sol_the_baseline_does_not_depend_on_b2():
    """The owner's review, part 24: the baseline must not depend on an unapproved proposal. The baseline composition of board E has
    no B2 step (B2 is composed only in its separate check), and the record files B2's draft, contact requirement and Layer 6 rows
    as a proposal that enters no change list."""
    m = _p0sol()
    assert ("l4e7", "p0sol_b2") not in m.ORDER_E and ("l4e7", "p0sol_b2") in m.ORDER_E_B2
    assert [x for x in m.ORDER_E_B2 if x != ("l4e7", "p0sol_b2")] == list(m.ORDER_E)
    page = " ".join(open(os.path.join(REC, "L4E7-P0SOL.md"), encoding="utf-8").read().split())
    b2 = " ".join(open(os.path.join(REC, "B2-PRESENCE.md"), encoding="utf-8").read().split())
    draft = " ".join(open(os.path.join(REC, "apply_gen_sch_e_p0sol_b2.py"), encoding="utf-8").read().split())
    out = " ".join(open(P0SOL_OUT, encoding="utf-8").read().split())
    assert "**R-180**: UNCHANGED in the baseline" in page and "no row for B2 enters L4-E9's change list" in page
    assert "**R-NEW2**" not in page
    assert "The baseline does not depend on B2" in b2 and "NOT entered in L4-E9's change list" in b2 and "NOT entered in Layer 6" in b2
    assert "NOT in L4-E9's change list and not part of the baseline" in draft
    assert "NOT part of the baseline: the baseline composition ORDER_E has no B2 step" in out


def t_p0sol_b2_is_unselected_and_withdrawn_as_drafted_with_no_owner_request():
    """Astra's recheck cx46 (item 18) and the owner's review part 25: route B2 is UNSELECTED and WITHDRAWN AS DRAFTED throughout; no
    text calls it selected, describes a prevention it achieves, asks a decision or recommends adoption; no owner action rests on it
    (the approved interface stands); its defects P2 and P3 stay explicit REMAINING ENGINEERING outside the baseline."""
    import re
    names = ("l4e7_p0sol.out", "L4E7-P0SOL.md", "B2-PRESENCE.md", "SUPPLIER-P1-1-P0SOL.md", "apply_gen_sch_e_p0sol_b2.py", "README.md")
    texts = {nm: " ".join(open(os.path.join(REC, nm), encoding="utf-8").read().split()) for nm in names}
    for nm, tx in texts.items():
        assert "WITHDRAWN AS DRAFTED" in tx, nm
        for bad in ("Decision asked", "Adopt the presence pair", "Recommendation", "selected by the coordinator", "B2 selected", "would prevent",
                    "unapproved PARTIAL", "PARTIAL proposal", "PARTIAL interface proposal", "if the owner adopts", "owner adopts",
                    "if B2 is adopted", "if B2 is pursued", "a PROPOSAL until the owner"):
            assert bad not in tx, (nm, bad)
        for m in re.finditer(r"owner item", tx):
            pre = tx[max(0, m.start() - 12):m.start()]
            assert re.search(r"(\bno |\bNo |NO |[Rr]ound 2's )$", pre), (nm, tx[max(0, m.start() - 60):m.end() + 30])
    for nm in ("B2-PRESENCE.md", "l4e7_p0sol.out", "L4E7-P0SOL.md", "SUPPLIER-P1-1-P0SOL.md"):
        tx = texts[nm]
        assert any("REMAINING ENGINEERING" in tx[m.start():m.start() + 400] for m in re.finditer(r"P2 and P3", tx)), nm
    page = texts["B2-PRESENCE.md"]
    assert "No owner item (the owner's review, part 25)" in page and "the approved interface stands" in page
    assert "(recommended)" not in page and "(recommended)" not in texts["apply_gen_sch_e_p0sol_b2.py"]
    assert "UNSELECTED, WITHDRAWN AS DRAFTED" in page.split("Prepared", 1)[0]
