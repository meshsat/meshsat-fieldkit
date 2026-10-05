"""Layer 9 task T5, record l9t5 (MESHSAT-1357, 4 October 2026; v2/docs/records/l9t5/): C-ALLTX rev 3 and C-DEV rev 1, held as
predicates on what l9t5_case.py computes.

The predicates: the committed .out is what the script prints and every pinned input is present at the sha256 the output names; the
copies in inputs/ carry the sha256 SOURCES.txt names; every predicate the script states holds; the case row's parts sum to the cells'
EMF plus the deficit and its allowance is re-solved here; the gauge's terms are re-solved here from the figures the script read;
A1's PA figures are the loop's high end over the maker's efficiency; C-DEV's two options are re-solved from VSNS and R43; the page
carries the output's figures; the record carries no long dash, no claim word outside the copies and no private path. These are
software predicates on the record's arithmetic: they establish no property of any board, converter, PA or pack.
"""
import hashlib
import importlib.util
import math
import os
import re
import shutil
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l9t5")
SCRIPT = os.path.join(REC, "l9t5_case.py")
OUT = os.path.join(REC, "l9t5_case.out")
PAGE = os.path.join(REC, "L9T5-CASES.md")
README = os.path.join(REC, "README.md")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}
CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)


def _M():
    if "M" not in _C:
        need(SCRIPT, "the l9t5 record")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        sp = importlib.util.spec_from_file_location("l9t5_case_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        for rel in m.PINS.values():
            need(os.path.join(ROOT, rel), "a pinned input of the l9t5 record")
        try:
            R = m.compute()
        except SystemExit as e:
            raise AssertionError("l9t5_case.py refused (exit %s)" % e.code)
        _C.update(M=m, R=R, text=m.render(R))
    return _C["M"]


def t_output_reproduced_byte_for_byte():
    _M()
    need(OUT, "the committed output")
    assert _C["text"] == open(OUT, encoding="utf-8").read(), "l9t5_case.out is not what the script prints"


def t_every_input_is_pinned_and_present():
    m = _M()
    for key, rel in m.PINS.items():
        sha = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
        assert ("%s  sha256 %s" % (rel, sha[:16])) in _C["text"], "%s is not pinned at its current sha256" % rel
    src = open(os.path.join(ROOT, m.PINS["sources"]), encoding="utf-8").read()
    for k in m.COPIES:
        full = hashlib.sha256(open(os.path.join(ROOT, m.PINS[k]), "rb").read()).hexdigest()
        assert "%s sha256 %s" % (os.path.basename(m.PINS[k]), full) in src, k


def t_every_predicate_holds():
    _M()
    P = _C["R"]["pred"]
    assert len(P) >= 16
    bad = [k for k, v in P.items() if not v]
    assert not bad, "false: %s" % "; ".join(bad)
    assert all(("   %s" % k) in _C["text"] for k in P)


def t_the_case_row_closes_and_its_allowance_is_re_solved():
    _M()
    c, R = _C["R"]["case"], _C["R"]
    assert abs(c["load"] + c["conv"] + c["path_w"] + c["cell_w"] - c["emf_w"] - c["deficit"]) < 1e-9
    i, v = R["I"], R["V"]
    assert abs(c["allow"] - i * (v - i * (c["r_path"] + 4 * 0.06 / 3.0))) < 1e-9 and round(c["allow"], 3) == 240.747
    assert abs(c["need"] - (c["p"] / i + i * (c["r_path"] + c["r_cells"]))) < 1e-9
    assert abs(c["vbat"] * i - c["p"]) < 1e-6, "the converters are evaluated at the VBAT the case sets"
    assert abs(sum(x for _l, x in R["conv_parts"]) - c["conv"]) < 1e-9
    q = R["case_quote_row"]
    assert round(q["V_rest"]["hi"], 3) == 16.214 and round(c["need"], 4) == 15.5162


def t_the_gauge_terms_are_re_solved_from_the_read_figures():
    _M()
    I, U = _C["R"]["in"], _C["R"]["U"]
    fsr = I["g_vref1"] / I["g_fsr_div"]
    terms = dict((lab.split(",")[0], x) for lab, x in U["gauge_terms"])
    assert abs(terms["gain error"] - I["g_gain"] * fsr / I["r10"]) < 1e-12 and round(terms["gain error"], 3) == 0.486
    assert abs(terms["integral nonlinearity"] - I["g_inl"] * I["g_lsb"] / I["r10"]) < 1e-12
    assert abs(U["gauge_uncal"] - sum(x for _l, x in U["gauge_terms"])) < 1e-12
    assert U["gauge_uncal_row"]["i"] == 18.0 - U["gauge_uncal"] and U["gauge_uncal_row"]["need"] > U["gauge_cal_row"]["need"] > _C["R"]["case"]["need"]


def t_a1_is_the_loops_high_end_over_the_makers_efficiency():
    m = _M()
    I, A = _C["R"]["in"], _C["R"]["A"]
    assert abs(A["a1_ex_w"] - I["pa_ex_vdd"] * sum(I["pa_ex_idd"])) < 1e-12 and round(A["a1_ex_w"], 1) == 75.0
    assert A["a1_pa_now"] == 113.0 and abs(I["pa_pout_max"] / I["pa_eta_min"] - 112.5) < 1e-9
    for a in A["a1"]:
        assert abs(a["p_hi"] - m.PA_SERVICE_W * 10 ** (2 * a["db"] / 10.0)) < 1e-12
        assert abs(a["p_dc"] - a["p_hi"] / I["pa_ex_eta"]) < 1e-12
        assert a["unc"]["i"] < 18.0
        # the loop's high end at +-0.25 and +-0.5 dB is under today's 113 W; at +-1 dB it passes the 45 W rating and the PA draws more
        assert (a["nom"]["p"] < _C["R"]["case"]["p"]) == (a["db"] < 1.0), a["db"]
        assert (a["p_hi"] > I["pa_pout_max"]) == (a["db"] == 1.0), a["db"]


def t_cdev_options_are_re_solved():
    _M()
    C = _C["R"]["C"]
    lo, hi = C["vsns"][0], C["vsns"][2]
    assert abs(C["lim_min"] - lo / (C["rs"] * (1 + C["tol"]))) < 1e-12
    assert abs(C["a_need_max"] - lo / (C["i_least"] * (1 + C["tol"]))) < 1e-12
    assert abs(C["a_need_min"] - hi / (10.0 * (1 - C["tol"]))) < 1e-12 and C["a_need_max"] < C["a_need_min"]
    assert abs(C["b_i_least"] - (C["i_least"] - C["ioc_in_w"] / C["v_least"])) < 1e-12 and C["b_margin"] > 1.0


def t_the_page_carries_the_outputs_figures():
    _M()
    R = _C["R"]
    need(PAGE, "the page")
    page = open(PAGE, encoding="utf-8").read()
    c, U, A, C = R["case"], R["U"], R["A"], R["C"]
    by = {a["db"]: a for a in A["a1"]}
    for s in ("%.4f V" % c["need"], "%.3f" % c["allow"], "%.3f" % c["p"], "%+.3f W" % c["deficit"], "%.4f V" % U["gauge_uncal_row"]["need"],
              "%.4f A" % U["gauge_uncal"], "%.4f V" % U["comb_printed"]["need"], "%.4f V" % by[0.5]["unc"]["need"], "%.4f V" % by[0.25]["m8"]["need"],
              "%.4f A against %.4f A" % (C["b_i_least"], C["lim_min"]), "%.4f mOhm" % (C["a_need_max"] * 1000), "%.4f mOhm" % (C["a_need_min"] * 1000),
              "%.3f mOhm" % (A["a2_band"][2] * 1000), "%.4f V" % A["a3_unc"]["need"], "16.214", "C-ALLTX rev 3", "C-DEV rev 1"):
        assert s in page, "the page does not carry %r" % s
    need(README, "the README")
    assert "%.4f V" % c["need"] in open(README, encoding="utf-8").read()


# ---------------------------------------------------------------------------------------------- round 2: I-03's drafts (l9t5_drafts.py)
DRAFTS = os.path.join(REC, "l9t5_drafts.py")
DRAFTS_OUT = os.path.join(REC, "l9t5_drafts.out")
CHECK = os.path.join(REC, "check_l9t5_netlist.py")
OLD_B = os.path.join(REC, "inputs", "apply_gen_sch_b_iocbuck-bdbed9bb.py")
NEW = {b: os.path.join(REC, "apply_gen_sch_%s_iocbuck.py" % b) for b in "ab"}
GENS = {b: os.path.join(TOOLS, "gen_sch_%s.py" % b) for b in "ab"}


def _mod(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _regen(board, script, d, tag):
    """the generator with one draft (or a tuple of drafts, in order) on a scratch copy, regenerated by record l8p's gen_netlist.py:
    (rc, netlist path or last line)."""
    import subprocess
    gn = _mod(os.path.join(ROOT, "v2", "docs", "records", "l8p", "gen_netlist.py"), "l9t5_test_gen_netlist")
    t = os.path.join(d, "%s_gen_sch_%s.py" % (tag, board))
    shutil.copy(GENS[board], t)
    for one in (script if isinstance(script, tuple) else (script,)):
        r = subprocess.run([sys.executable, "-B", one, t, "--write"], capture_output=True)
        assert r.returncode == 0, "the draft %s refused a clean copy: %s" % (os.path.basename(one), r.stderr.decode()[-300:])
    out = os.path.join(d, "%s_%s.net" % (tag, board))
    rc, log, _t = gn.run(t, out, {"a": "pcb-a-power", "b": "pcb-b-compute"}[board])
    return rc, (out if rc == 0 else (log.strip().splitlines() or [""])[-1])


def t_round2_drafts_output_reproduced_and_every_predicate_holds():
    import subprocess
    need(DRAFTS, "the drafts script")
    need(DRAFTS_OUT, "the drafts output")
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is needed")
    r = subprocess.run([sys.executable, "-B", DRAFTS], cwd=ROOT, capture_output=True)
    assert r.returncode == 0, "l9t5_drafts.py exited %d: %s" % (r.returncode, r.stderr.decode()[-300:])
    text = r.stdout.decode("utf-8")
    assert text == open(DRAFTS_OUT, encoding="utf-8").read(), "l9t5_drafts.out is not what the script prints"
    pred = text.split("9. THE PREDICATES")[1].split("l9t5_drafts: done")[0]
    rows = [l for l in pred.splitlines() if l.strip()]
    assert len(rows) == 15 and all(l.rstrip().endswith(" yes") for l in rows), rows
    for p in re.findall(r"^\s{3}([0-9a-f]{16}) (v2/\S+)$", text, re.M):
        assert hashlib.sha256(open(os.path.join(ROOT, p[1]), "rb").read()).hexdigest().startswith(p[0]), p[1]


def t_round2_board_b_old_text_fails_and_the_correction_passes():
    """the regression: board B's round 1 draft (fnd/l9t5 at bdbed9bb, kept in inputs/) makes the generator refuse on the LDO input
    capacitor's bypass entry; round 2's draft runs and its nets read DRAWN; the committed netlists read NOT DRAWN (today's state)."""
    import tempfile
    need(OLD_B, "the round 1 copy")
    chk = _mod(CHECK, "l9t5_test_check")
    with tempfile.TemporaryDirectory(prefix="l9t5_test_") as d:
        rc, line = _regen("b", OLD_B, d, "old")
        assert rc != 0 and "bypass C400 -> U40.1" in line and "+5V_DEV" in line, (rc, line)
        rc, path = _regen("b", NEW["b"], d, "new")
        assert rc == 0, path
        rca, patha = _regen("a", NEW["a"], d, "new")
        assert rca == 0, patha
        import io
        kit, v = chk.run({"a": patha, "b": path}, ROOT, io.StringIO())
        assert kit == "DRAWN" and v.get("pair") == "DRAWN", v
        kit0, _v0 = chk.run({b: os.path.join(ROOT, p) for b, p in chk.COMMITTED.items()}, ROOT, io.StringIO())
        assert kit0 == "NOT DRAWN"
        # a mutation: controller B's LDO back on the device rail must FAIL
        raw = open(path, encoding="utf-8").read()
        a_, b_ = '(node (ref "U50") (pin "1"))', '(node (ref "D1") (pin "1"))'
        assert raw.count(a_) == 1 and raw.count(b_) == 1
        mp = os.path.join(d, "mut.net")
        open(mp, "w", encoding="utf-8").write(raw.replace(a_, "\0").replace(b_, a_).replace("\0", b_))
        kitm, vm = chk.run({"b": mp}, ROOT, io.StringIO())
        assert kitm == "FAIL" and vm["b"] == "FAIL"


def t_round2_cdev_acceptance_is_re_solved():
    """board A's half on C-DEV rev 1 from the figures the script read: U7's margin, U601's rating and limit against the lead, the set
    point against the LDOs' need (the s99a band 4.872 to 5.133 V)."""
    _M()
    chk = _mod(CHECK, "l9t5_test_check2")
    C = _C["R"]["C"]
    assert abs(C["b_i_least"] - 6.0359) < 5e-5 and abs(C["lim_min"] - 7.0957) < 5e-5 and C["b_margin"] > 1.0
    assert C["b_buck_a"] < 3.0 and (5.8 + 4.5) / 2.0 < 10.0
    lo, nom, hi = chk.vout_band(56.2e3, 10.7e3)
    assert round(lo, 3) == 4.872 and round(hi, 3) == 5.133 and round(nom, 3) == 5.002
    assert lo * (1 - 0.035) > 3.3 * 1.015 + 0.400 and hi < 6.0
    txt = open(DRAFTS_OUT, encoding="utf-8").read()
    assert "BOARD A'S HALF: HOLDS" in txt and "BOARD B'S HALF, ITS OWN PARTS: HOLDS" in txt
    # round 4: the connected path is never a pass on this record's evidence; I-03 stays open
    assert "THE CONNECTED PATH: CONDITIONAL" in txt and "L8R2-F31 stays OPEN until its independent check" in txt and "I-03 STAYS OPEN" in txt


def _basis(m):
    """the declarations' basis, re-solved here from the case script (never read from the drafts or the output)."""
    _M()
    chk = _mod(CHECK, "l9t5_test_check3")
    C = _C["R"]["C"]
    lo, _nom, _hi = chk.vout_band(56.2e3, 10.7e3)
    return chk, {"dev_lead": (C["i_least"] * C["v_least"] - C["ioc_in_w"]) / C["v_least"], "ioc": C["ioc_in_w"] / (lo - 0.02 * 5.0), "wall": 0.9142}


def t_round3_board_b_composes_with_l8r2s_round7_drafts_and_the_tree_before_them_stops():
    """Round 3: board B's composition in L4-E9's order with record l8r2's fandec and gndret runs to its end and reads DRAWN on the
    netlist and on its declarations; without those two drafts (the tree before T5b) the generator stops on GND's declared peak."""
    import io
    import tempfile
    m = _mod(DRAFTS, "l9t5_test_drafts")
    assert ("l8r2", "fandec") in m.ORDER["b"] and ("l8r2", "gndret") in m.ORDER["b"]
    chk, basis = _basis(m)
    with tempfile.TemporaryDirectory(prefix="l9t5_test_") as d:
        p, _res, ok = m.compose("b", m.seq_of("b", "slot"), d, "t_fwd")
        assert ok
        rc, path, table = m.netlist("b", p, d, "t_fwd")
        assert rc == 0, path
        kit, v = chk.run({"b": path}, ROOT, io.StringIO())
        assert kit == "DRAWN", v
        assert chk.decl("b", table["intent"], basis)[0] == "DRAWN", chk.decl("b", table["intent"], basis)
        gnd = chk.rails_of(table["intent"])["GND"]
        assert "J_5V_IOC" in gnd["source"] and "J_54V" in gnd["source"] and gnd["amps_peak"] > 27.0   # derived by record l8r2's gndret
        q, _res, ok = m.compose("b", m.seq_of("b", "slot", skip=m.ROUND7), d, "t_old")
        assert ok
        rc, line, _t = m.netlist("b", q, d, "t_old")
        assert rc != 0 and "rail GND declares a 21.00 A peak" in line, (rc, line)


def t_round3_the_declarations_stand_on_their_basis_and_round2s_fail():
    """L8R2-F35: round 2's drafts (kept in inputs/) declare the device lead at a typed 6.0 A, under its own 6.0359 A on C-DEV rev 1,
    and +5V_IOC at 1.38 A: the declaration check FAILS on them and reads DRAWN on round 3's; a typed figure that merely passes
    (6.04 A) is refused as well, because the check holds the declaration to its basis, not to an inequality."""
    import subprocess
    import tempfile
    m = _mod(DRAFTS, "l9t5_test_drafts2")
    chk, basis = _basis(m)
    assert chk.ceil4(basis["dev_lead"]) == 6.0359 and chk.ceil4(basis["ioc"]) == 1.4749 and basis["dev_lead"] > 6.0
    with tempfile.TemporaryDirectory(prefix="l9t5_test_") as d:
        for b in "ab":
            for tag, script, want in (("old", m.OLD_R2[b], "FAIL"), ("new", NEW[b], "DRAWN")):
                t = os.path.join(d, "%s_gen_sch_%s.py" % (tag, b))
                shutil.copy(GENS[b], t)
                assert subprocess.run([sys.executable, "-B", script, t, "--write"], capture_output=True).returncode == 0
                rc, path, table = m.netlist(b, t, d, tag)
                assert rc == 0, path
                got, why = chk.decl(b, table["intent"], basis)
                assert got == want, (b, tag, why)
                if tag == "old" and b == "b":
                    assert any("6.0000 A peak" in x for x in why), why
        # a number that merely passes
        src = open(NEW["b"], encoding="utf-8").read()
        assert src.count("DEV_LEAD_PEAK = 6.0359") == 1
        typed = os.path.join(d, "apply_typed.py")
        open(typed, "w", encoding="utf-8").write(src.replace("DEV_LEAD_PEAK = 6.0359", "DEV_LEAD_PEAK = 6.0400"))
        t = os.path.join(d, "typed_gen_sch_b.py")
        shutil.copy(GENS["b"], t)
        assert subprocess.run([sys.executable, "-B", typed, t, "--write"], capture_output=True).returncode == 0
        rc, path, table = m.netlist("b", t, d, "typed")
        assert rc == 0, path
        assert chk.decl("b", table["intent"], basis)[0] == "FAIL"


def t_round3_l8r2_f35_is_answered_in_the_drafts_and_the_readme():
    """the lead is named in both drafts, the return sentence is withdrawn for pin 2, and the README carries V3's claim table."""
    for b in "ab":
        t = open(NEW[b], encoding="utf-8").read()
        assert "16 AWG, 150 mm" in t and "ASSEMBLY.md section 4" in t, b
    tb = open(NEW["b"], encoding="utf-8").read()
    assert "now through J_5V_IOC's pin 2" not in tb and "L8R2-F31" in tb
    out = open(DRAFTS_OUT, encoding="utf-8").read()
    assert "WITHDRAWN for pin 2" in out and "It holds for pin 1 only" in out
    readme = open(README, encoding="utf-8").read()
    assert "## The claim table for the independent recheck V3" in readme
    rows = [l for l in readme.split("## The claim table for the independent recheck V3")[1].splitlines() if l.startswith("| C")]
    assert len(rows) >= 20 and all(l.count("|") >= 7 for l in rows), len(rows)
    for lab in ("guaranteed", "typical", "declared", "model", "assumed"):
        assert any(("| %s" % lab) in l for l in rows), lab


A1 = os.path.join(REC, "l9t5_a1.py")
A1_OUT = os.path.join(REC, "l9t5_a1.out")


def t_round2_a1_detector_survey_reproduced_and_a1_stays_a_direction():
    """A1's detector from the makers' sheets (held back: python3 v2/docs/records/l9t5/fetch_held_back.py): the survey reproduces, no
    sheet prints its temperature row as a limit, and so record l9t5 holds no board D draft (the brief: never assume a figure)."""
    import subprocess
    need(A1, "the A1 survey script")
    need(A1_OUT, "the A1 survey output")
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is needed")
    m = _mod(A1, "l9t5_test_a1")
    for rel in m.SHEETS.values():
        need(os.path.join(ROOT, rel), "a held detector sheet (python3 v2/docs/records/l9t5/fetch_held_back.py)")
    r = subprocess.run([sys.executable, "-B", A1], cwd=ROOT, capture_output=True)
    assert r.returncode == 0, "l9t5_a1.py exited %d: %s" % (r.returncode, r.stderr.decode()[-300:])
    text = r.stdout.decode("utf-8")
    assert text == open(A1_OUT, encoding="utf-8").read(), "l9t5_a1.out is not what the script prints"
    assert "a detector whose PRINTED LIMIT supports A1's tolerance: NONE" in text and "A1 STAYS A SELECTED DIRECTION, NOT DRAFTED" in text
    # P0-1 (5 October 2026): the record holds correction (c)'s board D draft (resistors and a capacitor); A1 stays undrafted: no board D
    # draft of this record adds an IC (A1 would add a detector), read from each draft's ADDS with ast
    import ast as _ast
    for f in sorted(os.listdir(REC)):
        if f.startswith("apply_gen_sch_d_"):
            for node in _ast.parse(open(os.path.join(REC, f), encoding="utf-8").read()).body:
                if isinstance(node, _ast.Assign) and any(getattr(t, "id", None) == "ADDS" for t in node.targets):
                    assert not [e.value for e in node.value.elts if e.value.startswith("U")], f


def t_round4_the_connected_path_consumes_l8r2s_worst_vertex_and_is_never_a_pass():
    """V3's material blocker (1a). Round 3 accepted the lead's pin 2 on a sampled maximum (9.404 A) and said the acceptance did not
    depend on L8R2-F31. Now: the as-drawn figure is record l8r2's worst vertex and is OVER the VH's printed 10 A on the case (the row
    reads NOT MET there); with that record's return drafts composed the row is CONDITIONAL; which one applies is read from the
    composed netlists (the return sockets), never typed; the independence claim is gone from the output and the README."""
    import io
    import tempfile
    m = _mod(DRAFTS, "l9t5_test_drafts4")
    chk = _mod(CHECK, "l9t5_test_check4")
    G = m.gndret()
    assert G["ioc"]["drawn_hot"] > 10.0 and G["ioc"]["drawn_cold"] > G["ioc"]["drawn_hot"], G["ioc"]           # the old statement: 9.404 A, "within it"
    assert abs(G["ioc"]["drawn_hot"] - 10.6376) < 5e-4                                                          # V3's corner, 10.6375 A
    assert G["ret"][(G["ub_total"], -20.0)]["lead"] < 10.0 and G["shift_ret"] < G["shift_drawn_ub"]
    assert ("l8r2", "gndrtn") in m.ORDER["a"] and m.ORDER["a"].index(("l8r2", "gndrtn")) < m.ORDER["a"].index(("d8dec31", "mainpb"))
    assert m.ORDER["b"].index(("l8r2", "gndrtn")) == m.ORDER["b"].index(("l8r2", "gndret")) + 1
    with tempfile.TemporaryDirectory(prefix="l9t5_test_") as d:
        for b in "ab":
            for tag, skip, want in (("ret", (), "DRAWN"), ("noret", m.RETURN, "NOT DRAWN")):
                p, _res, ok = m.compose(b, m.seq_of(b, "slot", skip=skip), d, "t4_%s" % tag)
                assert ok, (b, tag)
                rc, path, _t = m.netlist(b, p, d, "t4_%s" % tag)
                assert rc == 0, path
                assert chk.return_drawn(chk.read(open(path, "rb").read()))[0] == want, (b, tag)
    out = open(DRAFTS_OUT, encoding="utf-8").read()
    assert "AS DRAWN (no dedicated return)" in out and "NOT MET (the recheck's corner, 10.6375 A)" in out
    assert "THE CONNECTED PATH: CONDITIONAL. It holds ONLY WITH that return correction" in out
    assert "does NOT depend on, and does not close" not in out and "is WITHDRAWN: the draft adds a VH contact" in out
    readme = open(README, encoding="utf-8").read()
    assert "does not depend on" not in readme.split("## The claim table")[1].split("## Round 2 in short")[0].replace("does not depend on L8R2-F31 is withdrawn", "")


def t_round4_the_ldo_requirement_carries_its_regulation_terms():
    """V3's blocker 2 (1b): 3.7495 V was the output tolerance (printed at 1 to 30 mA) and the dropout alone; with the printed load
    and line regulation maxima the requirement is 3.7674 V and the ground shift the LDOs allow 0.9417 V."""
    m = _mod(DRAFTS, "l9t5_test_drafts5")
    P = m.figures()
    chk = _mod(CHECK, "l9t5_test_check5")
    lo, _n, hi = chk.vout_band(56.2e3, 10.7e3)
    need = 3.3 * (P["ap_vout_hi"] + P["ap_load"] * 0.46 + P["ap_line"] * (hi - 4.3)) + P["ap_drop"]
    assert P["ap_load"] == 0.01 and P["ap_line"] == 0.001 and abs(need - 3.7674) < 5e-5 and need > 3.7495
    out = open(DRAFTS_OUT, encoding="utf-8").read()
    assert "3.7674 V (round 3's 3.7495 V was the simplified figure" in out and "The ground shift the LDOs allow: 0.9417 V" in out


def t_round4_sequencing_is_stated_as_an_enable_relation():
    """V3's blocker 3 (1c): shared enable connectivity is not evidence that the supervisors' rail is valid whenever the device rail
    is; the old sentence is gone and the timing stays an unverified bench item."""
    out = open(DRAFTS_OUT, encoding="utf-8").read()
    assert "the supervisors are up whenever the device rail is (record l9t5 out 5's condition)" not in out
    assert "the enable RELATION" in out and "That is connectivity, not timing" in out and "UNVERIFIED: a bench item" in out


def t_round4_the_gauge_bound_has_its_offset_drift_and_the_case_file_is_rev_3():
    """V3's blockers 4 and 5 (1d, 1e): the BQ4050's printed offset drift is in the gauge's sum (0.0048 A over the assumed 32 K; the
    bound 16.0684 V becomes 16.0718 V; F01 stays open on either), and the case script pins and labels the rev 3 case file."""
    m = _M()
    R = _C["R"]
    I, U = R["in"], R["U"]
    assert abs(I["g_off_drift"] - 0.3e-6) < 1e-12 and abs(U["off_drift"] - 0.3e-6 * 32.0 / 0.002) < 1e-9 and round(U["off_drift"], 4) == 0.0048
    assert any(lab.startswith("offset drift") for lab, _x in U["gauge_terms"])
    assert round(U["comb_before_r4"]["need"], 4) == 16.0684 and round(U["comb_printed"]["need"], 4) == 16.0718 and U["comb_printed"]["need"] > 15.5
    assert m.PINS["cases"].endswith("coordinator-cases-2026-10-04-rev3.md")
    first = _C["text"].splitlines()[0]
    assert first.startswith("l9t5_case: C-ALLTX rev 3 and C-DEV rev 1") and "1. THE CASE ROW, C-ALLTX REV 3" in _C["text"]
    assert abs(I["rev3_case"][1] - R["case"]["need"]) < 5e-5 and I["rev3_bound"] == 16.0684


# ------------------------------------------------------------------------- round 4 part 2: T10, the supervisors' regulators (l9t5_t10.py)
T10 = os.path.join(REC, "l9t5_t10.py")
T10_OUT = os.path.join(REC, "l9t5_t10.out")
PRE = {b: os.path.join(REC, "apply_gen_sch_%s_iocpre.py" % b) for b in "ab"}
SHDN = os.path.join(REC, "apply_gen_sch_b_canshdn.py")
GUARD_B = os.path.join(REC, "apply_gen_sch_b_iocguard.py")
CONTRACT_DRAFT = os.path.join(REC, "apply_hw_fw_contract_t10.py")
ROUND5 = os.path.join(REC, "T10-ROUND5.md")
CM5 = os.path.join(REC, "l9t5_cm5.py")
CM5_OUT = os.path.join(REC, "l9t5_cm5.out")


def _run_script(path, out, head, n_pred, what):
    """a record script run from the repository root: its output is the committed one, its inputs are at the sha256 it names, and its
    predicate section carries n_pred rows that all read yes. Returns the text."""
    import subprocess
    need(path, what)
    need(out, what + "'s output")
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is needed")
    r = subprocess.run([sys.executable, "-B", path], cwd=ROOT, capture_output=True)
    assert r.returncode == 0, "%s exited %d: %s" % (os.path.basename(path), r.returncode, r.stderr.decode()[-300:])
    text = r.stdout.decode("utf-8")
    assert text == open(out, encoding="utf-8").read(), "%s is not what the script prints" % os.path.basename(out)
    rows = [l for l in text.split(head)[1].split("\nl9t5_")[0].splitlines() if l.strip()]
    assert len(rows) == n_pred and all(l.rstrip().endswith(" yes") for l in rows), rows
    pins = re.findall(r"^\s{3}([0-9a-f]{16}) (v2/\S+)$", text, re.M)
    assert pins
    for h, rel_ in pins:
        assert hashlib.sha256(open(os.path.join(ROOT, rel_), "rb").read()).hexdigest().startswith(h), rel_
    return text


def t_round4_t10_output_reproduced_and_every_predicate_holds():
    text = _run_script(T10, T10_OUT, "12. THE PREDICATES", 28, "the T10 script")
    for s_ in ("FINDING: THE STATE IS UNBOUNDED", "SELECTED (SESSION): K3 WITH K2's ROW AS ITS CONDITION", "L9T5-F06 STAYS OPEN",
               "T10-A1", "T10-A2", "T10-A3", "T10-A4", "T10-A5", "NOT the owner's", "Round 4 was the first attempt at this correction",
               "round 5 is the second round on the same correction"):
        assert s_ in text, s_
    _C["t10_text"] = text


def t_round4_t10_the_state_and_the_regulators_thermal_limit_are_re_solved():
    """the owner's part 7: the applicable operating conditions verified from the sources. Round 3 stated L9T5-F06 as a current deficit
    only (0.900 A asked of a 600 mA part in the TJ 125 C state). Re-solved here from the figures the script read: no document bounds
    the state; the controller itself has no operating point in that state at the inside air; and the regulator's limit is thermal,
    0.2187 A at its 150 C from the 5 V rail, so the old statement (a 600 mA limit) fails as the binding one."""
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is needed")
    m = _mod(T10, "l9t5_test_t10")
    for rel_ in list(m.SHEETS.values()) + list(m.DOCS.values()):
        need(os.path.join(ROOT, rel_), "a pinned input of T10")
    P = m.figures()
    chk = _mod(CHECK, "l9t5_test_check_t10a")
    assert P["Y"][("on", 400)] == (165.0, 220.0, 400.0, 500.0, 840.0) and P["V"][("on", 400)] == (167.0, 256.0, 327.0, 416.0, 536.0)
    assert (P["theta_mcu"], P["tj_mcu"], P["theta_ldo"], P["tj_ldo"], P["imax"]) == (45.0, 125.0, 184.0, 150.0, 0.6)
    assert P["contract_rows"] >= 1 and not P["contract_bound"] and not P["panel_bound"] and P["fw"] == ["panel"]
    air = P["air"]
    assert abs(air - 76.25) < 0.005
    # the controller: its ceiling at this air, and no operating point in the worst printed state on either revision
    assert round((P["tj_mcu"] - air) / P["theta_mcu"] / 3.3, 3) == 0.328
    assert m.point(P["Y"][("on", 400)], air, P["theta_mcu"], P["tj_mcu"]) is None and m.point(P["V"][("on", 400)], air, P["theta_mcu"], P["tj_mcu"]) is None
    assert air + P["theta_mcu"] * 3.3 * 0.840 > 190.0
    # the bound: the operating point is a fixed point of the printed maxima (checked by substitution), the larger revision taken
    pts = {rev: m.point(P[rev][("off", m.BOUND[1])], air, P["theta_mcu"], P["tj_mcu"]) for rev in "YV"}
    for rev, (tj, i) in pts.items():
        assert abs(air + P["theta_mcu"] * 3.3 * i - tj) < 1e-6 and abs(m.interp(P[rev][("off", m.BOUND[1])], tj) - i) < 1e-12, rev
    i_mcu = max(v[1] for v in pts.values())
    d_bound = i_mcu + sum(P["decl_loads"][1:])
    assert round(i_mcu, 4) == 0.1691 and round(d_bound, 4) == 0.2291
    # the regulator as drawn (from +5V_IOC at I-03's band) and with the pre-regulator
    _lo5, _n5, hi5 = chk.vout_band(56.2e3, 10.7e3)
    lo3, nom3, hi3 = chk.vout_band(56.2e3, 13.3e3)

    def tj(i, vin):
        return air + P["theta_ldo"] * (vin - 3.3) * i

    def ceil_i(vin, t):
        return (t - air) / P["theta_ldo"] / (vin - 3.3)
    assert round(ceil_i(hi5, 150.0), 4) == 0.2187 and round(ceil_i(hi5, 125.0), 4) == 0.1445 and ceil_i(hi5, 150.0) < P["imax"]
    assert tj(d_bound, hi5) > P["tj_ldo"] and round(tj(d_bound, hi5), 1) == 153.5
    assert round(tj(d_bound, hi3), 1) == 118.0 and round(tj(P["decl"][1], hi3), 1) == 121.8 and tj(P["decl"][1], hi3) <= m.TJ_GOAL
    assert tj(P["rv"][2] + 0.06, hi3) > m.TJ_GOAL and round(tj(P["rv"][2] + 0.06, hi3), 1) == 160.1      # the case's HIGH is NOT covered
    # what the criterion does not cover is printed, not hidden: both transceivers dominant (momentary), one and both buses faulted
    d_mom = i_mcu + 2 * P["can_dom_hi"] + P["decl_loads"][3]
    d_f1 = i_mcu + P["can_fault"] + P["can_rec"] + P["decl_loads"][3]
    d_f2 = i_mcu + 2 * P["can_fault"] + P["decl_loads"][3]
    assert (round(d_mom, 4), round(d_f1, 4), round(d_f2, 4)) == (0.3091, 0.3726, 0.5491)
    assert (round(tj(d_mom, hi3), 1), round(tj(d_f1, hi3), 1), round(tj(d_f2, hi3), 1)) == (132.6, 144.2, 176.3)
    assert tj(d_mom, hi3) > m.TJ_GOAL and tj(d_f2, hi3) > P["tj_ldo"]
    # the owner's rule of 5 October 2026: 125 C (T10's criterion) in a state the design must serve, 150 C (the printed absolute
    # maximum) in any state; the 160 C shutdown is TYPICAL behaviour with no maximum trip printed and never an acceptance. Each row
    # with its scope: (m) the held dominant figure, served; (f1) one fabric faulted, served (IOHA row 7); (f2) both, any state.
    # All six (with and without the pre-regulator) FAIL; no current reaches the 600 mA capability (no foldback in any row)
    def fails(x, served):
        return x > P["tj_ldo"] or (served and x > m.TJ_GOAL)
    six = ((d_mom, hi3, True), (d_f1, hi3, True), (d_f2, hi3, False), (d_mom, hi5, True), (d_f1, hi5, True), (d_f2, hi5, False))
    assert all(fails(tj(i, v), s) for i, v, s in six)
    assert m.TJ_GOAL < tj(d_f1, hi3) < P["tj_ldo"] < tj(d_f2, hi3) and d_f1 < d_f2 < P["imax"] and P["tsd"] == 160.0
    assert P["can_dto"] == (1.2, 2.6, 3.8)          # the driver's time-out ends a held TXD (SLLSEQ7F); it bounds no transmit share
    # the set point: 13.3 k holds the LDOs' input over their 600 mA requirement; the next E96 value up (13.7 k) does not
    G, DP = m.D.gndret(), m.D.figures()
    need600 = 3.3 * (P["vout_hi"] + P["load"] * 0.6) + P["drop"][600]
    assert round(need600, 4) == 3.7693
    drop = 3 * 0.6 * (G["rhot"] + 2 * DP["vh_r"][1]) + G["shift_drawn_ub"]
    at = {rb: chk.vout_band(56.2e3, rb)[0] - m.D.RAIL_BUDGET * chk.vout_band(56.2e3, rb)[1] - drop for rb in (13.3e3, 13.7e3)}
    assert round(at[13.3e3], 4) == 3.8428 and at[13.3e3] >= need600 > at[13.7e3], at
    assert round(nom3, 4) == 4.1805 and (round(lo3, 4), round(hi3, 4)) == (4.0711, 4.2907) and P["vin"][0] < at[13.3e3] and hi3 < P["vin"][1]
    text = _C.get("t10_text") or open(T10_OUT, encoding="utf-8").read()
    for s_ in ("junction 150 C at 0.2187 A", "0.2291 A: junction  153.5 C: OVER the absolute maximum", "R602 13.3 k, 4.1805 V nominal, 4.0711 to 4.2907 V",
               "at least 3.8428 V", "the case's HIGH 160.1 C (still over)", "NOT INSIDE THE BOUND, each row judged against its own limit",
               "never to be exceeded and never", "no maximum trip printed", "junction 132.6 C MODEL", "junction 176.3 C MODEL",
               "OPEN DEFECT L9T5-F13", "OPEN DEFECT L9T5-F16", "OPEN DEFECT L9T5-F17", "COVERED BY CON-004",
               "before the LDO's junction reaches 150 C (the clock read-back's reset or the watchdog)", "is no acceptance: Layer 5's FMEA row", "A DRAFTED CANDIDATE, UNCHECKED"):
        assert s_ in text, s_
    # the shutdown is never the place a fault ends acceptably (the staged wording, the interim wording and round 4's T10-A5 each did)
    for bad in ("or its foldback", "only the thermal shutdown", "must end in the LDO's thermal shutdown", "NOT INSIDE THE CRITERION, and stated so"):
        assert bad not in text, bad
    # V6-B3, the regression: round 4 said no requirement covers the fabric faults; CON-004 does (the trace, IOHA rows 7 and 8, A7)
    assert "NO REQUIREMENT COVERS" not in text.upper()


def t_round4_t10_the_draft_needs_i03s_and_the_state_before_it_fails_its_check():
    """T10-A4, and the regression: with I-03's draft alone (the state before T10) board A's divider reads 56.2k over 10.7k and the
    pre-regulator's check FAILS; with the T10 draft after it the check reads DRAWN and I-03's own 5 V check FAILS; each T10 draft
    refuses a generator without I-03's draft (leaving it untouched) and refuses the tree's generator."""
    import io
    import subprocess
    import tempfile
    chk = _mod(CHECK, "l9t5_test_check_t10b")
    with tempfile.TemporaryDirectory(prefix="l9t5_test_") as d:
        for b in "ab":
            need(PRE[b], "the T10 draft for board %s" % b.upper())
            t = os.path.join(d, "bare_gen_sch_%s.py" % b)
            shutil.copy(GENS[b], t)
            r = subprocess.run([sys.executable, "-B", PRE[b], t, "--write"], capture_output=True)
            assert r.returncode == 3 and open(t, "rb").read() == open(GENS[b], "rb").read(), (b, r.returncode)
            before = open(GENS[b], "rb").read()
            r = subprocess.run([sys.executable, "-B", PRE[b], GENS[b], "--check"], capture_output=True)
            assert r.returncode == 3 and open(GENS[b], "rb").read() == before, (b, r.returncode)
        rc, old = _regen("a", NEW["a"], d, "i03")
        assert rc == 0, old
        rc, new = _regen("a", (NEW["a"], PRE["a"]), d, "t10")
        assert rc == 0, new
        assert chk.run({"a": old}, ROOT, io.StringIO(), div="i03")[0] == "DRAWN" and chk.run({"a": old}, ROOT, io.StringIO(), div="t10")[0] == "FAIL"
        assert chk.run({"a": new}, ROOT, io.StringIO(), div="t10")[0] == "DRAWN" and chk.run({"a": new}, ROOT, io.StringIO(), div="i03")[0] == "FAIL"
        # board B's draft changes declarations only: the netlist with it is the netlist without it
        rc, b_old = _regen("b", NEW["b"], d, "i03")
        assert rc == 0, b_old
        rc, b_new = _regen("b", (NEW["b"], PRE["b"]), d, "t10")
        assert rc == 0, b_new

        def nets(path):
            return sorted(re.findall(r'\(node \(ref "[^"]+"\) \(pin "[^"]+"\)', open(path, encoding="utf-8").read()))
        assert len(nets(b_old)) > 1000 and nets(b_old) == nets(b_new)
        assert chk.run({"a": new, "b": b_new}, ROOT, io.StringIO(), div="t10")[0] == "DRAWN"


# ------------------------------------------------------------------------- round 4 part 3: SDR3-F02, the CM5's supply design figure
def t_round4_cm5_output_reproduced_and_every_predicate_holds():
    text = _run_script(CM5, CM5_OUT, "7. THE PREDICATES", 6, "the CM5 assessment")
    for s_ in ("Power supply designs should accommodate 5 V at up to 2.5 A", "a SUPPLY DESIGN FIGURE", "LABELLED SCENARIO", "L9T5-F15",
               "a case row's change is the coordinator's and none is made here", "SDR3-F02 is CONFIRMED as a finding"):
        assert s_ in text, s_
    _C["cm5_text"] = text


def t_round4_cm5_the_scenario_is_re_solved_and_no_case_row_moves():
    """SDR3-F02. The old statement: the generator's comment reads 'no maximum given' and every budget takes a module's HIGH at the
    declared 1.6 A, with nothing beside it. Re-solved here from the budget's own stage rows: at the maker's 2.5 A (12.5 W) the slot
    stages hold their steady load and pass the loop's least when a cooler's bounded start coincides; C-ALLTX at that figure is a
    scenario beside the row, and the row itself (15.5162 V at the modules' typical) is what the case script still prints."""
    _M()
    if "bm" not in _C:
        bm = _mod(os.path.join(ROOT, "v2", "docs", "records", "l9pwr", "l9pwr_budget.py"), "l9t5_test_budget")
        _C["bm"], _C["B"] = bm, bm.compute()
    bm, B = _C["bm"], _C["B"]
    d_i = (12.5 - 8.0) / B["stages"][("DRAFTED", "ALLTX", "S1")]["v_least"]
    assert round(d_i, 4) == 0.9180
    steady, start, deg = (bm.slot_least(B, k, rails=("S1", "S2", "S3"))[0] - d_i for k in ("i_least", "start", "degraded"))
    assert steady > 0 > start and deg > 0
    text = _C.get("cm5_text") or open(CM5_OUT, encoding="utf-8").read()
    for s_ in ("%+.4f A" % steady, "%+.4f A" % start, "%+.4f A" % deg):
        assert s_ in text, s_
    # the old statement holds only with the module at the budget's 8 W: there the start row is inside the loop's least
    assert bm.slot_least(B, "start", rails=("S1", "S2", "S3"))[0] > 0
    Dc = B["cfgs"]["DRAFTED"]
    row = bm.case_row(B["d11_rv_record"], B["F"], Dc, bm.case_vals(Dc, cm5=12.5)[0])
    assert ("%.4f V" % row["need"]) in text and row["need"] > B["calltx"]["cm5_8"]["need"] > B["calltx"]["new"]["need"]
    assert abs(_C["R"]["case"]["need"] - B["calltx"]["new"]["need"]) < 1e-12 and bm.CASE_CM5 == 4.5      # the case row is not moved
    gb = open(GENS["b"], encoding="utf-8").read()
    assert '"U3%dA" % (s - 1): 1.6,' in gb and "no maximum given" in gb       # the tree's generator is not edited by this record


def t_round4_the_page_and_the_readme_carry_t10_and_the_cm5_assessment():
    """the page's sections 0c and 0d and the README's rows C36 onward carry what the two outputs print: every figure with a unit in
    those sections is in an output, the criterion's five conditions are numbered, L9T5-F06 is OPEN and no case row is changed."""
    page = open(PAGE, encoding="utf-8").read()
    sec = page.split("## 0d. Round 4, part 3")[1].split("## 0b. Round 4")[0]
    outs = open(T10_OUT, encoding="utf-8").read() + open(CM5_OUT, encoding="utf-8").read()
    figs = sorted(set(re.findall(r"[+-]?\d+\.\d+ (?:A|V|C|W)\b", sec)))
    assert len(figs) >= 50
    missing = [f for f in figs if f not in outs]
    assert not missing, "the page's figures not in an output: %s" % missing
    for s_ in ("T10-A1", "T10-A2", "T10-A3", "T10-A4", "T10-A5", "L9T5-F06 STAYS OPEN", "Selected (SESSION): K3 with K2's row as its condition",
               "No case row is changed here", "L9T5-F15", "This is the first attempt at this correction", "**L9T5-F13, OPEN**",
               "**L9T5-F16, OPEN**", "**L9T5-F17, OPEN**", "covered by CON-004", "a DRAFTED CANDIDATE, unchecked",
               "never to be exceeded and never an operating target", "Junction with the pre-regulator (MODEL)"):
        assert s_ in sec, s_
    for bad in ("or its foldback", "only the thermal shutdown", "must end in the LDO's thermal shutdown", "no requirement covers"):
        assert bad not in sec, bad
    readme = open(README, encoding="utf-8").read()
    rows = [l for l in readme.splitlines() if re.match(r"\| C\d\d \|", l)]
    assert [l[2:5] for l in rows] == ["C%02d" % i for i in range(1, 61)]
    new = {l[2:5]: l for l in rows[35:]}
    for k, s_ in (("C41", "0.2187 A"), ("C44", "13.3 k"), ("C45", "118.0 C"), ("C51", "OPEN"), ("C53", "-0.3546 A"), ("C54", "17.0148 V"),
                  ("C43", "DRAFTED CANDIDATE, unchecked"), ("C57", "L9T5-F13 OPEN"), ("C58", "L9T5-F16 OPEN"), ("C59", "L9T5-F17 OPEN"),
                  ("C60", "withdrawn")):
        assert s_ in new[k], k
    assert "T10 (L9T5-F06, the supervisors' regulators): STAYS OPEN" in readme.splitlines()[0] and "no case row is changed" in readme.splitlines()[0]
    assert "DRAFTED CANDIDATE, unchecked" in readme.splitlines()[0] and "L9T5-F13, F16 and F17 OPEN" in readme.splitlines()[0]


def t_round5_t10_the_fault_rows_are_traced_to_con004_and_re_solved():
    """round 5 (V6 item C, V6-B3): the requirement read where it is written, and the credible bus faults re-solved here from the figures
    the script read. The old statements fail: 'no requirement covers either fault state' (CON-004 does), and the held rows as the
    figures the design meets (each held bus-fault row FAILS 125 C; only FW-B21's share closes them). The share keeps a transceiver's
    average under its 20 mA declaration for any dominant current up to 333.5 mA, so the unprinted fault currents (B1, B2, B5) do not
    decide the result."""
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is needed")
    m = _mod(T10, "l9t5_test_t10r5")
    for rel_ in list(m.SHEETS.values()) + list(m.DOCS.values()):
        need(os.path.join(ROOT, rel_), "a pinned input of T10")
    P = m.figures()
    Q = m.figures5(P)
    assert P["con004_class"] == ("constraint", "core", "BLOCKER") and "two independent CAN-FD fabrics" in P["con004"]
    assert "A7" in P["con004_acc"] and P["a7"][1].startswith("cut fabric A") and "nothing moves" in P["a7"][2]
    assert P["row7"][0] == "One CAN fabric breaks or a transceiver fails dominant" and P["row8"][0] == "Both CAN fabrics break"
    assert "revision V or X" in Q["c17_5"] and "revision Y or W" in Q["c17_4"]
    assert (Q["hsi"], m.BOUND) == (64.0, ("VOS3", 144)) and "VOS3" in Q["rm_vos"] and "DAR" in Q["rm_dar"] and "129 occurrences" in Q["rm_bo"]
    assert (P["can_rec"], P["can_dom_hi"], P["can_fault"], Q["ios_dom"], Q["ios_rec"]) == (0.0035, 0.06, 0.18, 0.2, 0.005)
    assert abs(Q["icc_shdn"] - 2.5e-6) < 1e-12 and Q["vbus_abs"] == 14.0 and abs(Q["rl_min"] - 59.796) < 1e-9
    # the share: the transceiver's average and the largest dominant current the declaration still covers
    i_can = P["can_rec"] + (P["can_dom_hi"] - P["can_rec"]) * m.SHARE
    i_max = (P["decl_loads"][1] - P["can_rec"]) / m.SHARE + P["can_rec"]
    assert m.SHARE == 0.02 and round(i_can * 1000, 2) == 4.63 and round(i_max * 1000, 1) == 828.5 and i_max > max(P["can_fault"], Q["ios_dom"])
    # the enabled subset: FDCAN counted twice; the max/typ ratio from the whole set's printed rows
    assert round(Q["s_Y"], 1) == 50.9 and round(Q["s_V"], 1) == 47.3
    assert abs(m.kfac(P, "Y", 125.0) - 170.0 / 45.0) < 1e-12 and abs(m.kfac(P, "V", 125.0) - 90.0 / 29.0) < 1e-12
    # the bounded state at the case's air on both revisions, with the circuit's auxiliaries (taken from the output) and the share
    text = open(T10_OUT, encoding="utf-8").read()
    i_aux = float(re.search(r"over its value less 1 % \(ASSUMED\): ([\d.]+) A at most", text).group(1))
    assert 0.006 < i_aux < P["decl_loads"][3]
    chk = _mod(CHECK, "l9t5_test_check_t10r5")
    hi3 = chk.vout_band(56.2e3, 13.3e3)[2]
    air = P["air"]

    # part 21 (1): the drop at its worst corner, the pre-regulator's top less the LDO's least output (98.5 %); round 4 took 3.3 V
    assert P["vout_lo"] == 0.985 and P["vout_hi"] == 1.015

    def tj(i):
        return air + P["theta_ldo"] * (hi3 - 3.3 * P["vout_lo"]) * i
    for rev in "YV":
        tj_m, i_m = m.mcu_point(P, Q, rev, air)
        assert abs(air + P["theta_mcu"] * 3.3 * i_m - tj_m) < 1e-6
        reg = i_m + i_aux + 2 * i_can
        if rev == "Y":
            # the old statement (round 5's first pass, at the nominal drop) held; at the worst corner rev Y's cover does not
            assert air + P["theta_ldo"] * (hi3 - 3.3) * reg <= m.TJ_GOAL < tj(reg), tj(reg)
            continue
        assert tj(reg) <= m.TJ_GOAL, (rev, tj(reg))
        # each credible bus fault on one fabric, held: FAILS; with the share: holds 125 C (B4 carries the other nodes' bits too)
        v33 = 3.3 * P["vout_hi"]
        for i_f, extra in ((P["can_fault"], 0.0), (Q["ios_dom"], 0.0), (P["can_dom_hi"] + v33 / Q["rl_min"], 2 * m.SHARE * v33 / Q["rl_min"])):
            held = i_m + i_aux + i_can + i_f
            resp = i_m + i_aux + i_can + P["can_rec"] + (i_f - P["can_rec"]) * m.SHARE + extra
            assert tj(resp) <= m.TJ_GOAL < tj(held), (rev, i_f)
        both = i_m + i_aux + 2 * (P["can_rec"] + (Q["ios_dom"] - P["can_rec"]) * m.SHARE)
        assert tj(both) <= P["tj_ldo"] and tj(i_m + i_aux + 2 * Q["ios_dom"]) > P["tj_ldo"]
    # rev Y's rows have no controller operating point in the exhaust air: the record says so and ties it to the inside air (U-02)
    assert m.mcu_point(P, Q, "Y", P["air_exhaust"]) is None and m.mcu_point(P, Q, "V", P["air_exhaust"]) is not None
    for s_ in ("COVERED BY CON-004", "A7 as written CUTS a fabric", "NO OPERATING POINT at or under 125 C: the H743 itself", "U-02",
               "PROVISIONAL CHOICE (SESSION L9T5-D7)", "pass limit: at most 0.2318 A", "SESSION decision L9T5-D6", "L9T5-F21", "L9T5-F22",
               "SESSION decision (L9T5-D5): tolerated", "L9T5-F18", "L9T5-F19", "L9T5-F20", "LABELLED SCENARIO until the coordinator issues the row",
               "CONFIRMED on the bench by V-B21, not decided there", "the declaration holds for ANY dominant current up to 828.5 mA"):
        assert s_ in text, s_


def t_round5_t10_the_four_answers_of_part_21_are_re_solved():
    """The owner's review of checkpoint 2 (part 21): (1) the margin and the corner it is lost at, re-solved: rev V's rows keep over 14 K at the
    drop's worst corner and hold to a local air over the exhaust's; rev Y's (the cover for a rev X part) miss 125 C there, and the controller
    figure a rev X part must meet is the one printed; (2) the service: at FW-B21's 500 kbit/s floor the share leaves 7 frames a window, the
    assumed need fits within two windows; (3) the firmware as the faulting party is bounded under 150 C while it keeps the clock bound;
    (4) the contract draft carries the figures and C-DEV rev 2's copy carries this output's."""
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is needed")
    m = _mod(T10, "l9t5_test_t10r5c")
    P = m.figures(); Q = m.figures5(P)
    text = open(T10_OUT, encoding="utf-8").read()
    sec = text.split("   10h. THE FOUR QUESTIONS")[1].split("\n11. THE STATE")[0]
    led = {(r, l): float(x) for r, l, x in re.findall(r"rev ([YV]), (the bounded state|the worst single fault, responded|both fabrics faulted, responded): +[\d.]+ A, ([\d.]+) C", sec)}
    assert len(led) == 6
    assert all(v <= m.TJ_GOAL - 14.0 for (r, _l), v in led.items() if r == "V") and all(v > m.TJ_GOAL for (r, _l), v in led.items() if r == "Y")
    air_v = [float(x) for x in re.findall(r"rev V, [^\n]*?lost at a local air of ([\d.]+) C", sec)]
    assert len(air_v) == 3 and min(air_v) > P["air_exhaust"]
    i_aux = float(re.search(r"over its value less 1 % \(ASSUMED\): ([\d.]+) A at most", text).group(1))
    chk = _mod(CHECK, "l9t5_test_check_t10r5c")
    hi3 = chk.vout_band(56.2e3, 13.3e3)[2]
    k = P["theta_ldo"] * (hi3 - 3.3 * P["vout_lo"])
    v33, rl = 3.3 * P["vout_hi"], Q["rl_min"]
    f_resp = max(P["can_rec"] + (i_f - P["can_rec"]) * m.SHARE + extra for i_f, extra in (
        (P["can_fault"], 0.0), (Q["ios_dom"], 0.0), (P["can_dom_hi"] + v33 / rl, 2 * m.SHARE * v33 / rl)))
    i_cap = (m.TJ_GOAL - P["air"]) / k - (i_aux + 2 * f_resp)
    assert "pass limit: at most %.4f A" % i_cap in sec and m.mcu_point(P, Q, "V", P["air"])[1] < i_cap < m.mcu_point(P, Q, "Y", P["air"])[1]
    # (2) the service at the contract's rates
    for rate, n in ((500e3, 7), (1e6, 14)):
        assert int(m.SHARE * m.WINDOW_MS * 1e-3 * rate // (m.FRAME_BITS + 2)) == n
    assert "between 500 kbit/s and 1 Mbit/s" in open(CONTRACT_DRAFT, encoding="utf-8").read()
    # (3) the babbling supervisor at the clock bound, both transceivers held dominant: under 150 C on rev Y's cover
    i_b = m.mcu_point(P, Q, "Y", P["air"])[1] + i_aux + 2 * P["can_dom_hi"]
    assert m.TJ_GOAL < P["air"] + k * i_b < P["tj_ldo"]
    for s_ in ("THE FIRMWARE AS THE FAULTING PARTY", "SYSTEMATIC firmware defect", "an unapplied contract row is no mechanism", "IWDG",
               "every one equal", "): every one\n"):
        assert s_ in sec, s_
    # L9T5-F22's scenario: 14.0 k holds the held current's requirement and brings rev Y's cover under 125 C
    assert re.search(r"14\.0 k: [\d.]+ V nominal, top [\d.]+ V; the LDOs' input at least [\d.]+ V \(holds\); rev Y's cover, both fabrics faulted, 1[01]\d\.\d C", sec)


def t_round5_t10_part22_the_babbling_row_fails_at_13k3_and_holds_with_the_set_point_delta():
    """The owner's review of checkpoint 3 (part 22), B and C. The old statement: the babbling row at 146.4 C read 'under 150 C' as if the
    absolute maximum were its criterion. A babbler is a SUSTAINED state (nothing in hardware ends it), so 125 C applies: re-solved here, on
    revision V's rows (the fitted revision) it FAILS with iocpre's 13.3k and holds with the set point delta's 14.0k; the delta composes,
    reads 14.0k and both its mutations fail; the proof is keyed to revision V and the cover's rows decide nothing."""
    import io as _io
    import subprocess
    import tempfile
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is needed")
    m = _mod(T10, "l9t5_test_t10p22")
    P = m.figures(); Q = m.figures5(P)
    assert (m.FITTED_REV, m.COVER_REV, m.R602_SET) == ("V", "Y", 14.0e3)
    text = open(T10_OUT, encoding="utf-8").read()
    i_aux = float(re.search(r"over its value less 1 % \(ASSUMED\): ([\d.]+) A at most", text).group(1))
    chk = _mod(CHECK, "l9t5_test_check_p22")
    hi13 = chk.vout_band(56.2e3, 13.3e3)[2]
    lo14, nom14, hi14 = chk.vout_band(56.2e3, 14.0e3)
    assert (round(lo14, 4), round(nom14, 4), round(hi14, 4)) == (3.9063, 4.0114, 4.1174)
    i_m = m.mcu_point(P, Q, "V", P["air"])[1]
    i_bab = i_m + i_aux + 2 * P["can_dom_hi"]
    t13 = P["air"] + P["theta_ldo"] * (hi13 - 3.3 * P["vout_lo"]) * i_bab
    t14 = P["air"] + P["theta_ldo"] * (hi14 - 3.3 * P["vout_lo"]) * i_bab
    assert t14 <= m.TJ_GOAL < t13 < P["tj_ldo"], (t13, t14)
    sec = text.split("   10i. THE OWNER'S REVIEW OF CHECKPOINT 3")[1].split("\n11. THE STATE")[0]
    assert re.search(r"babbling \(nothing ends it\) +V +%.4f A +125 C \(sustained\) +%.1f C FAILS +%.1f C holds" % (i_bab, t13, t14), sec)
    assert "never applied to revisions X or Y" in sec and "SILICON REVISION" in sec and "REV_ID 0x2003" in sec
    assert "the set point DRAWN; mutations: the divider inverted FAIL, R602 back to 13.3k FAIL" in sec
    # the delta refuses a generator without iocpre and the tree's; applies once after iocpre
    with tempfile.TemporaryDirectory(prefix="l9t5_test_p22_") as d:
        for b in "ab":
            s = os.path.join(REC, "apply_gen_sch_%s_iocset.py" % b)
            t0 = os.path.join(d, "bare_%s.py" % b)
            shutil.copy(GENS[b], t0)
            assert subprocess.run([sys.executable, "-B", s, t0, "--write"], capture_output=True).returncode == 3
            assert subprocess.run([sys.executable, "-B", s, GENS[b], "--write"], capture_output=True).returncode == 3
            rc, net = _regen(b, (NEW[b], PRE[b], s), d, "p22")
            assert rc == 0, net
            if b == "a":
                assert m.set_check(chk.read(open(net, "rb").read()))[0] == "DRAWN"
                assert m.set_check(chk.read(open(net, "rb").read().replace(b"14.0k 0.1%", b"13.3k 0.1%")))[0] == "FAIL"


def t_round5_t10_the_shdn_draft_composes_and_the_contract_draft_applies_once():
    """round 5's response, drafted: board B's SHDN draft reads on a regenerated netlist (each TCAN334D's pin 5 on its controller's PD2 or
    PB14 and a 100 k to GND); the board without it and two mutations FAIL; it refuses a second application and the tree's generator. The
    contract draft applies once to a copy of the page, re-parses (FW-B01 to FW-B21) and refuses a second run."""
    import subprocess
    import tempfile
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is needed")
    m = _mod(T10, "l9t5_test_t10r5b")
    d0 = m.D
    with tempfile.TemporaryDirectory(prefix="l9t5_test_r5_") as d:
        rc, new = _regen("b", (NEW["b"], PRE["b"], SHDN), d, "shdn")
        assert rc == 0, new
        rc, old = _regen("b", (NEW["b"], PRE["b"]), d, "noshdn")
        assert rc == 0, old
        rd = m.CHK.read
        assert m.shdn_check(rd(open(new, "rb").read()))[0] == "DRAWN" and m.shdn_check(rd(open(old, "rb").read()))[0] == "FAIL"
        for tag, swaps in (("m1", [(("U43", "5"), ("U43", "8"))]), ("m2", [(("R80", "2"), ("U53", "3"))]), ("m3", [(("R91", "1"), ("R92", "1"))])):
            assert m.shdn_check(rd(open(d0.mutate(new, d, tag, swaps), "rb").read()))[0] == "FAIL", tag
        t = os.path.join(d, "again_gen_sch_b.py")
        shutil.copy(GENS["b"], t)
        assert subprocess.run([sys.executable, "-B", SHDN, t, "--write"], capture_output=True).returncode == 0
        assert subprocess.run([sys.executable, "-B", SHDN, t, "--write"], capture_output=True).returncode == 3
        before = open(GENS["b"], "rb").read()
        assert subprocess.run([sys.executable, "-B", SHDN, GENS["b"], "--write"], capture_output=True).returncode == 3
        assert open(GENS["b"], "rb").read() == before
        page = os.path.join(ROOT, "v2", "docs", "HW-FW-CONTRACT.md")
        cp = os.path.join(d, "HW-FW-CONTRACT.md")
        shutil.copy(page, cp)
        before = open(page, "rb").read()
        assert subprocess.run([sys.executable, "-B", CONTRACT_DRAFT, cp], capture_output=True).returncode == 0
        assert open(cp, "rb").read() == before
        r = subprocess.run([sys.executable, "-B", CONTRACT_DRAFT, cp, "--write"], capture_output=True)
        assert r.returncode == 0, r.stderr.decode()[-300:]
        got = open(cp, encoding="utf-8").read()
        ids = [l.split(" | ")[0].lstrip("| ") for l in got.splitlines() if re.match(r"\| FW-B\d\d \|", l)]
        assert ids == ["FW-B%02d" % i for i in range(1, 23)]
        assert "at most 2 % of every 100 ms window" in got and "FDCAN_CCCR.DAR = 1" in got and "| V-B21 | FW-B21 |" in got
        assert subprocess.run([sys.executable, "-B", CONTRACT_DRAFT, cp, "--write"], capture_output=True).returncode == 3
        assert open(page, "rb").read() == before


def t_round5_the_page_carries_the_outputs_figures():
    """T10-ROUND5.md: its first line states DONE, NOT DONE and NEXT; every figure with a unit on it is one the output prints; F13, F16
    and F17 are drafted corrections that stay OPEN; nothing is called corrected that the output does not read as such."""
    need(ROUND5, "the round 5 page")
    page = open(ROUND5, encoding="utf-8").read()
    first = page.splitlines()[0]
    assert all(s_ in first for s_ in ("DONE:", "NOT DONE:", "NEXT:"))
    out = open(T10_OUT, encoding="utf-8").read()
    figs = sorted(set(re.findall(r"[+-]?\d+\.\d+ (?:A|V|C|W|mA)\b", page)))
    assert len(figs) >= 30
    missing = [f for f in figs if f not in out]
    assert not missing, "the page's figures not in the output: %s" % missing
    # round 6 (cx45 Q3 (d)): L9T5-D5 is withdrawn, so the page states the residual and the withdrawal, not the tolerance
    for s_ in ("they stay OPEN in the register", "L9T5-F06: STAYS OPEN", "**Residual B7b:**", "(round 6: L9T5-D5 WITHDRAWN", "SESSION L9T5-D7", "L9T5-F22",
               "covered by CON-004", "the drop's worst corner"):
        assert s_ in page, s_
    for s_ in ("L9T5-F13: A DRAFTED CORRECTION, DESK ACCEPTANCE MET BY ITS AUTHOR ON REV V", "L9T5-F16: A DRAFTED CORRECTION",
               "L9T5-F17: A DRAFTED CORRECTION", "L9T5-F06 STAYS OPEN"):
        assert s_ in out, s_


# ------------------------------------------------------------------------------------------------ P0-1 (5 October 2026, Slot A)
F01 = os.path.join(REC, "l9t5_f01.py")
F01_OUT = os.path.join(REC, "l9t5_f01.out")
F01D = os.path.join(REC, "l9t5_f01_drafts.py")
F01D_OUT = os.path.join(REC, "l9t5_f01_drafts.out")
PALOOP = os.path.join(REC, "l9t5_paloop.py")
F01_CHECK = os.path.join(REC, "check_f01_netlist.py")
F01_NEW = {b: os.path.join(REC, "apply_gen_sch_%s_paloop.py" % b) for b in "ad"}
_F01 = {}


def _run_plain(path, out):
    """a record script run from the repository root, its output the committed one byte for byte"""
    import subprocess
    need(path, os.path.basename(path))
    need(out, os.path.basename(out))
    need(os.path.join(ROOT, "v2", "vendor", "ti", "held", "ti-ina250-sbos511c.pdf"), "the held INA250 sheet (record l4e7's fetch_held_back.py)")
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is needed")
    if path not in _F01:
        r = subprocess.run([sys.executable, "-B", path], cwd=ROOT, capture_output=True)
        assert r.returncode == 0, "%s exited %d: %s" % (os.path.basename(path), r.returncode, r.stderr.decode()[-300:])
        _F01[path] = r.stdout.decode("utf-8")
    text = _F01[path]
    assert text == open(out, encoding="utf-8").read(), "%s is not what the script prints" % os.path.basename(out)
    return text


def t_p0_f01_output_reproduced_pinned_and_every_predicate_holds():
    text = _run_plain(F01, F01_OUT)
    rows = [l for l in text.split("8. PREDICATES")[1].split("l9t5_f01: done")[0].splitlines() if l.strip()]
    assert len(rows) >= 20 and all(l.rstrip().endswith(" yes") for l in rows), rows
    pins = re.findall(r"^\s{3}\S+\s+(v2/\S+)\s+sha256 ([0-9a-f]{16})$", text, re.M)
    assert len(pins) >= 20
    for rel_, h in pins:
        assert hashlib.sha256(open(os.path.join(ROOT, rel_), "rb").read()).hexdigest().startswith(h), rel_


def t_p0_f01_the_ten_findings_are_disposed_of_and_f01_reads_provisional():
    """the owner's part 21: each of cx44's ten findings in one of three states; F01 / D-17 and its dependants PROVISIONAL, never
    closed on printed limits; round 1's closure words gone"""
    text = open(F01_OUT, encoding="utf-8").read()
    sec = text.split("7. CX44'S TEN FINDINGS")[1].split("8. PREDICATES")[0]
    states = ("CORRECTED WITH DESK EVIDENCE", "STILL AN OPEN DESIGN DEFECT", "GENUINELY EXTERNAL")
    for i in range(1, 11):
        line = [l for l in sec.splitlines() if re.match(r"^   %d\s" % i, l)]
        assert len(line) == 1 and any(st in line[0] for st in states), i
    assert "GENUINELY EXTERNAL" in [l for l in sec.splitlines() if re.match(r"^   1\s", l)][0]   # the service transfer
    for s_ in ("F01 / D-17's row reads PROVISIONAL on B-PA1", "never closed on printed limits", "L9P-F04 PROVISIONAL with the selection",
               "its dependants read PROVISIONAL too", "WITHDRAWN (cx44)"):
        assert s_ in text, s_
    for bad in ("L9P-F04 CLOSES", "CORRECTED IN THE STEADY STATE", "CLOSES THE CASE ON PRINTED LIMITS"):
        assert bad not in text, bad
    page = open(PAGE, encoding="utf-8").read()
    p0 = page.split("## 0f. P0-1")[1].split("## 0e.")[0]
    assert [l.split("|")[1].strip() for l in p0.splitlines() if re.match(r"^\| \d+ \|", l)] == [str(i) for i in range(1, 11)]
    figs = sorted(set(re.findall(r"\d+\.\d+ (?:A|V|W|mA|mV|Ohm|mOhm|ms|deg)\b", p0)))
    outs = text + open(F01D_OUT, encoding="utf-8").read()
    missing = [f for f in figs if f not in outs]
    assert not missing, "the page's figures not in an output: %s" % missing
    first = open(README, encoding="utf-8").read().splitlines()[0]
    assert "F01 / D-17 PROVISIONAL" in first and "1c DRAFTED" in first


def t_p0_f01_the_cap_and_the_case_are_re_solved():
    """the cap's band recomputed here from the module's own read rows by a separate formula, the BIAS bound against the room, the case
    at the cap's top as l9t5_case.py's section 8 prints it"""
    _run_plain(F01, F01_OUT)
    sp = importlib.util.spec_from_file_location("paloop_under_test", PALOOP)
    P = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(P)
    S = P.read_sheets()
    L = P.cap(S)
    e = P.DIV_TOL + P.DIV_TCR * P.DIV_DT
    # cx45 Q1: the reference's load residual (10 x the TYPICAL load regulation over the load's distance from 1 mA) and R553 at its low corner
    leak = P.IDSS_25 * 2 ** ((P.T_AIR - P.T_REF) / P.IDSS_DOUBLE_K) + P.V5[2] / (P.IR_X7R_OHM_F / P.C_SS)
    load_hi = S["ref_vfb"] * (1 + S["ref_acc"]) / (P.R_SET_BOT * (1 - e)) + S["ref_ifb"] + leak
    load_lo = S["ref_vfb"] * (1 - S["ref_acc"]) / (P.R_SET_BOT * (1 + e)) - S["ref_ifb"]
    resid = P.LOADREG_X * S["ref_loadreg"] * max(abs(load_hi - 1e-3), abs(load_lo - 1e-3))
    assert abs(S["ref_loadreg"] - 0.030) < 1e-12 and 0.98e-3 < load_lo < 1e-3 < load_hi < 1.02e-3
    vs_hi = S["ref_vfb"] * (1 + S["ref_acc"]) * (1 + P.R_SET_TOP * (1 + e) / (P.R_SET_BOT * (1 - e))) + S["ref_ifb"] * P.R_SET_TOP + S["ref_line"] + resid
    rb = P.R_BIAS * (1 + P.R1PC_TOL + P.R1PC_TCR * 65.0)
    rint = P.R_INT * (1 - e)
    i_max = (vs_hi * (1 + rint / rb) - P.V5[0] * rint / rb + L["vos"]) / (P.G_SENSE * (1 - L["gerr"])) + L["ios"]
    assert abs(i_max - L["i_max"]) < 1e-9
    assert L["i_max"] > L["i_max_nores"] and L["i_min"] < L["i_min_nores"]          # R553's and R559's corners widen the band
    assert abs(S["ina_gerr"] - 0.0075) < 1e-12 and abs(S["ref_acc"] - 0.01) < 1e-12 and abs(S["oa_vos"] - 0.002) < 1e-12
    text = open(F01_OUT, encoding="utf-8").read()
    assert ("%.4f to %.4f A over every corner" % (L["i_min"], L["i_max"])) in text
    assert L["bias"][0] > L["u13_min"] - L["i_max"] > 0.1                   # BIAS would not fit; with it moved the room is 0.1 A
    assert L["ref_preload"] >= 1e-3
    case_out = open(OUT, encoding="utf-8").read()
    m = re.search(r"contacts' maximum: need ([\d.]+) V: MEETS against REQ-018's 15\.5 V, margin ([\d.]+) V", case_out)
    assert m and ("need %s V, a MODEL margin of %s V" % (m.group(1), m.group(2))) in text
    assert float(m.group(1)) < 15.5
    # cx46 item 2: Q551's held load (cx46's own nominal reading 0.55/549 + 3.3551/1000 = 4.3569 mA lies under the module's upper bound),
    # the IB and C554 terms at R553's top corner, the PRINTED-rows band free of the ASSUMPTION residual, B-PA1 rounded down
    nominal_held = 0.55 / 549.0 + 3.3551 / 1000.0
    assert nominal_held < L["ref_held"] < 1.05 * nominal_held and L["ref_held"] > load_hi
    ib = [x for lab, k, x in L["vos_terms"] if lab.startswith("IB")][0]
    assert abs(ib - P.IB_BOUND * P.R_INT * (1 + e)) < 1e-15
    assert abs(L["vset_printed"][2] - (L["vset"][2] - L["ref_resid"])) < 1e-15
    assert L["bpa1_limit"] == math.floor(L["i_min"] * 1000.0) / 1000.0 and L["bpa1_limit"] <= L["i_min"]
    flat = " ".join(text.split())
    assert ("at most %.3f A (the band's floor %.4f A rounded DOWN, cx46)" % (L["bpa1_limit"], L["i_min"])) in flat
    assert ("at Q551's held load (up to %.3f mA)" % (L["ref_held"] * 1e3)) in flat and "which is NOT a guaranteed band" in flat
    assert "REMAINING ENGINEERING for the receiving company, never a qualification-only item" in flat
    assert "at most 6.352 A" not in text


def t_p0_f01_drafts_compose_read_drawn_and_every_mutation_fails():
    text = _run_plain(F01D, F01D_OUT)
    assert text.count("F01 check: DRAWN") == 2 and "HOLDS (PA_ILIM / PA_ILIM)" in text
    m = re.search(r"(\d+) of (\d+) mutations fail", text)
    assert m and m.group(1) == m.group(2) and int(m.group(2)) >= 10
    assert "board A without this draft" in text and "regenerated rc 0: NOT DRAWN" in text
    assert "REFUSED as it must: it needs record l8r2's fb01 keyword" in text
    rows = [l for l in text.split("7. THE PREDICATES")[1].split("l9t5_f01_drafts: done")[0].splitlines() if l.strip()]
    assert len(rows) == 8 and all(l.rstrip().endswith(" yes") for l in rows), rows


def t_p0_f01_the_drafts_refuse_the_tree_and_a_second_application():
    import subprocess
    import tempfile
    for b in "ad":
        need(F01_NEW[b], "the F01 draft of board %s" % b)
        tree = os.path.join(TOOLS, "gen_sch_%s.py" % b)
        before = hashlib.sha256(open(tree, "rb").read()).hexdigest()
        r = subprocess.run([sys.executable, "-B", F01_NEW[b], tree, "--write"], capture_output=True)
        assert r.returncode == 3 and (b"NOT RELEASED" in r.stderr or b"fb01" in r.stderr), r.stderr[-200:]
        assert hashlib.sha256(open(tree, "rb").read()).hexdigest() == before
    with tempfile.TemporaryDirectory() as d:
        g = os.path.join(d, "gen_sch_d.py")
        shutil.copy(os.path.join(TOOLS, "gen_sch_d.py"), g)
        assert subprocess.run([sys.executable, "-B", F01_NEW["d"], g, "--write"], capture_output=True).returncode == 0
        r = subprocess.run([sys.executable, "-B", F01_NEW["d"], g, "--write"], capture_output=True)
        assert r.returncode == 3, "a second application was not refused"


CONN = os.path.join(REC, "l9t5_connected.py")
CONN_OUT = os.path.join(REC, "l9t5_connected.out")
L4E9_DIR = os.path.join(ROOT, "v2", "docs", "records", "l4e9")


def _l4e9():
    """L4-E9's register and script with this record's change-list draft applied in memory (the tree's files are not written)"""
    sp = importlib.util.spec_from_file_location("cl_draft_for_p0_test", os.path.join(REC, "apply_l4e9_changelist_p0.py"))
    d = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(d)
    files, ch, m = d.patch_all(ROOT)
    reg = m.md_table(files[os.path.join(L4E9_DIR, "DOWNSTREAM-REGISTER.md")], "| ID | Kind |")
    return d, files, ch, m, reg


def t_p0_connected_output_reproduced_pinned_and_every_predicate_holds():
    """4b and 4c: the connected candidate's output is what the script prints, its pins are the tree's bytes, every predicate holds"""
    text = _run_plain(CONN, CONN_OUT)
    rows = [l for l in text.split("12. THE PREDICATES")[1].split("l9t5_connected: done")[0].splitlines() if l.strip()]
    assert len(rows) >= 16 and all(l.rstrip().endswith(" yes") for l in rows), rows
    pins = re.findall(r"^   ([0-9a-f]{16}) (v2/\S+)$", text.split("1. THE CASE ROWS")[0], re.M)
    assert len(pins) >= 30
    for h, rel_ in pins:
        assert hashlib.sha256(open(os.path.join(ROOT, rel_), "rb").read()).hexdigest().startswith(h), rel_


def t_p0_connected_every_check_reads_drawn_and_every_mutation_fails():
    """V6's two breaking checks read the composed design (DD-7 with the guard, l9t5's automatic mode); one mutation per check fails it"""
    text = open(CONN_OUT, encoding="utf-8").read()
    sec3 = text.split("3. EVERY RECORD NETLIST CHECK")[1].split("   not netlist checks")[0]
    checks = [l for l in sec3.splitlines()[1:] if l.startswith("   ") and not l.startswith("    ")]
    verdicts = [l[66:].split("  ")[0].strip() for l in checks]
    assert len(checks) >= 14 and all(v == "DRAWN" for v in verdicts), list(zip(checks, verdicts))
    for k in ("L4-E11 DD-7 (round 17, with the guard), board A", "l9t5 I-03 / T10, board A (automatic mode)"):
        assert any(l.startswith("   " + k) for l in checks), k
    m = re.search(r"(\d+) of (\d+) mutations do not read DRAWN", text)
    assert m and m.group(1) == m.group(2) == str(len(checks))
    for b in "ABD":
        assert re.search(r"board %s: \d+ drafts, every one applied; regenerated rc 0: \d+ parts, 0 unplaced, intent written True, "
                         r"designators unique" % b, text), b


def t_p0_connected_the_change_list_carries_every_composed_draft():
    """V6-m11: every circuit draft the candidate composes has a register row in L4-E9's change list, in the composition's order; FAN_OK's
    rows are WITHDRAWN; the page's section 3 table is the script's change list (the record's other generated sections are owed)"""
    tree_reg = open(os.path.join(L4E9_DIR, "DOWNSTREAM-REGISTER.md"), encoding="utf-8").read()
    assert "| R-220 |" not in tree_reg, "the draft is the integrator's to apply, not this branch's"
    d, files, ch, m, reg = _l4e9()
    assert ch == m.cons_changes(reg)
    named = {}
    for c in ch:
        for s_ in re.findall(r"apply_[a-z0-9_]+\.py", c[4]):
            named[s_] = (c[2], c[0], c[8])
    sp = importlib.util.spec_from_file_location("conn_under_test", CONN)
    C = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(C)
    for b, keys in C.ORDER.items():
        seq = []
        for k in keys:
            if k.split("/")[0] in C.ORDER_FREE:
                continue
            s_ = os.path.basename(C.script_of(b, k))
            assert s_ in named, "%s (board %s) has no change-list row" % (k, b)
            seq.append(named[s_][1])
        assert seq == sorted(seq), "board %s composes out of the change list's order" % b
    for rid in ("R-210", "R-211", "R-212"):
        row = [r for r in reg if r[0] == rid][0]
        assert row[6] == "WITHDRAWN" and "FAN_OK is rejected" in " | ".join(row[2:6]), rid
        assert [c for c in ch if c[2] == rid][0][8].startswith("WITHDRAWN")
    page = m.md_table(files[os.path.join(L4E9_DIR, "L4-POWER-ARCHITECTURE.md")], "| # | Step | Row |")
    assert page == [["%d" % c[0]] + [str(x) for x in c[1:]] for c in ch], "the patched page's change list is the patched script's"
    # a second application is refused (the register and the page already carry the rows)
    for fn, arg in ((d.patch_register, files[os.path.join(L4E9_DIR, "DOWNSTREAM-REGISTER.md")]),):
        try:
            fn(arg)
            raise AssertionError("a second application must be refused")
        except SystemExit as e:
            assert e.code == 3
    for r in reg:
        if r[0] in ("R-210", "R-211", "R-212") or (r[0].startswith("R-2") and int(r[0][2:]) >= 220):
            want = ("DO: nothing: WITHDRAWN by the owner's rejection of FAN_OK (P0 brief, 5 October 2026); D-17's correction is R-227 and "
                    "R-238; never applied") if r[6] == "WITHDRAWN" else (
                "DO: step %s (%s), no open question; it continues while the open items are worked" % (r[7], r[6]))
            assert r[1] == "IMPLEMENTATION" and r[8] == "SETTLED WORK" and r[9] == want, r[0]
            assert r[4] in m.OWNERS, r[0]
    # D-10 restated from record l4e7's S1 rewrite (the owner's part 23): an unresolved protection defect; B2 never its resolution
    dd = {x["id"]: x for x in m.DEFECTS}
    assert dd["D-10"]["state"].startswith("OPEN: AN UNRESOLVED PROTECTION DEFECT") and "does not resolve D-10" in dd["D-10"]["state"]
    assert dd["D-16"]["state"].startswith("ADDRESSED IN DRAFTS")
    # a broken order is refused: the PA cap's board A half before fb01
    saved = list(m.CHANGE_ORDER)
    try:
        i = [k for k, c in enumerate(saved) if c[1] == "R-227"][0]
        j = [k for k, c in enumerate(saved) if c[1] == "R-200"][0]
        bad = list(saved)
        bad[i], bad[j] = bad[j], bad[i]
        m.CHANGE_ORDER = bad
        try:
            m.cons_changes(reg)
            raise AssertionError("the PA cap before fb01 must be refused")
        except SystemExit:
            pass
    finally:
        m.CHANGE_ORDER = saved


def t_p0_connected_the_re_trace_reads_its_sources():
    """4b: the figures the re-trace prints are its sources' figures (the case, the breaker, the return solver, the eFuse bands)"""
    text = open(CONN_OUT, encoding="utf-8").read()
    case = open(OUT, encoding="utf-8").read()
    m = re.search(r"contacts' maximum: need ([\d.]+) V: MEETS against REQ-018's 15\.5 V, margin ([\d.]+) V", case)
    assert m and ("%s V (MODEL on PRINTED" % m.group(1)) in text and ("margin %s V" % m.group(2)) in text
    stk = open(os.path.join(ROOT, "v2", "docs", "records", "l9stk", "l9stk_protection.out"), encoding="utf-8").read()
    b = re.search(r"current limit ([\d.]+) / ([\d.]+) / ([\d.]+) A \(VCL", stk)
    assert b and ("breaker band %s /" % b.group(1)) in text
    dist = open(os.path.join(ROOT, "v2", "docs", "records", "l8r2", "l8r2_dist.out"), encoding="utf-8").read()
    # cx45 Q2: the return is the PLACED distributed model's; every row the connected output prints is l8r2_dist.out's
    for lab, tot in re.findall(r"^   (C-DEV rev 2|C-DEV rev 1|the largest steady state|the declared upper bound)[^:]*: ([\d.]+) A \(", dist, re.M):
        assert re.search(r"^     %s\s+%s A: " % (re.escape(lab), re.escape(tot)), text, re.M), lab
    for r_ in re.findall(r"^     ([+-]\d+\.\d\d C (?:VH|RIB|RET))\s+\S+\s+([\d.]+) A \(", dist, re.M):
        assert ("%s %s A" % r_) in text, r_
    assert "L8R2-F33a is realisable" not in text and "CORRECTED IN DRAFT on the desk model (placement and distributed solve)" not in text
    assert "V6-B1: OPEN, REMAINING ENGINEERING for the receiving company" in " ".join(text.split())   # cx46 item 4
    ef = open(os.path.join(ROOT, "v2", "docs", "records", "efuse", "efuse_check.out"), encoding="utf-8").read()
    bands = re.findall(r"^   EFUSE   [AB] U\d+\s+tps2596\s+([\d.]+) / [\d.]+ / ([\d.]+) A", ef, re.M)
    assert len(bands) == 3
    for lo, hi in bands:
        assert ("band %s to %s A" % (lo, hi)) in text, (lo, hi)
    # cx45 Q7: the coordination names what it does not establish; the active C-DEV row is rev 2; the CAN service per state
    for s_ in ("NOT COVERED at 76.25 C", "demand the 30 W service: NOT ESTABLISHED", "in its COMPOSED form", "no single failure removes the trip", "L8P-R9-F1, handed over",
               "NOT ESTABLISHED for", "a TX pin repurposed as a GPIO", "U7 with I-03 carries C-DEV rev 2 (the active row)"):
        assert s_ in text, s_
    assert "U7 with I-03 carries C-DEV rev 1" not in text
    assert "the required service unchanged" in text and "replaced, by the cap's top" in text
    assert "DECISION L9T5-D9 (SESSION" in text and "Slot C's set point delta (R602 14.0 k) is TAKEN" in text and "ADAPTATION REJECTED" in text
    # L9T5-F22 over the connected circuit WITH THE CONTAINMENT composed (cx45 Q3, Slot C's round 6): every row carries its LDO's own sense
    # resistor; three currents a set point and return: the printed 600 mA, the hardware bound (the rail trip's maximum, 10j (d)) and
    # L9T5-D8's superseded 0.4512 A
    rows = re.findall(r"R602 (1\d\.\d) k .*?return (as drawn|with the dedicated return)\s+shift [\d.]+ V, ([\d.]+) A a LDO \((the rating|the hardware bound|L9T5-D8, superseded); .*?: (holds|FAILS) ", text)
    assert len(rows) == 18, rows
    by = {}
    for rb, ret, _i, crit, v in rows:
        by.setdefault(crit, {})[(rb, ret)] = v
    assert set(by["the rating"].values()) == {"FAILS"}, by        # the sense resistor's drop takes the 600 mA row out at every set point
    assert set(by["the hardware bound"].values()) == {"holds"}, by  # T10-A3 at the trip's maximum holds everywhere, either return
    assert by["L9T5-D8, superseded"][("13.3", "as drawn")] == "holds" and by["L9T5-D8, superseded"][("14.0", "as drawn")] == "FAILS", by
    t10 = open(T10_OUT, encoding="utf-8").read()
    t10j = " ".join(t10.split("10j. THE CHECK cx45's Q3", 1)[1].split())
    a3 = re.search(r"each LDO's input at ([\d.]+) A, the sense resistor's drop counted: at least ([\d.]+) V against ([\d.]+) V", t10j)
    assert a3 and ("input %s V against %s V (Slot C: %s V against" % (a3.group(2), a3.group(3), a3.group(2))) in text   # Slot C's figure reproduced
    assert "%s V): the same" % a3.group(3) in text
    assert "0.3R 1% 0805 for U40" in text and "taken at 0.3030 Ohm" in text      # the sense resistor read on the composed board B
    # the babbling row on revision V without the containment: Slot C's two computed points, read from l9t5_t10.out
    bab = re.search(r"babbling \(nothing ends it\)\s+V\s+[\d.]+ A\s+125 C \(sustained\)\s+([\d.]+) C FAILS\s+([\d.]+) C holds", t10)
    assert bab and ("R602 13.3 k %s C (Slot C's MODEL) FAILS" % bab.group(1)) in text and ("R602 14.0 k %s C (Slot C's MODEL) holds" % bab.group(2)) in text
    # with the containment: a constant current at the trip's average maximum (Slot C's MODEL at 14.0 k, NOT a bound after cx46) and
    # cx46's periodic countermodel over 125 C as Slot C reproduces it
    th = re.search(r"a constant current at the trip's average maximum [\d.]+ A reads the LDO's junction ([\d.]+) C at ([\d.]+) C air", t10j)
    assert th and ("R602 14.0 k: %s C (Slot C's MODEL): holds" % th.group(1)) in text
    pk = re.search(r"the junction's periodic peak ([\d.]+) C, OVER 125 C", t10j)
    assert pk and float(pk.group(1)) > 125.0 and ("at 14.0 k: %s C, OVER 125 C" % pk.group(1)) in " ".join(text.split())
    assert "a constant-current MODEL, not a bound" in " ".join(text.split())
    assert "FINDING L9T5-F27" in text and "ANSWERED, Slot C renamed it L9T5-D10" in " ".join(text.split()) and "superseded" in text
    assert "route B2 is UNSELECTED and WITHDRAWN AS DRAFTED (record l4e7 reads it so)" in " ".join(text.split())
    assert "the owner's item" not in text and "unapproved PARTIAL interface proposal" not in text
    m = re.search(r"14\.0 k: [\d.]+ V nominal, top ([\d.]+) V; the LDOs' input at least ([\d.]+) V", t10)
    assert m and ("top %s V)" % m.group(1)) in text
    # the same chain as Slot C's part 22 scenario (no containment then): at 14.0 k, as drawn, at 0.4512 A the only difference is the sense drop
    r14 = re.search(r"R602 14\.0 k .*?return as drawn\s+shift [\d.]+ V, 0\.4512 A a LDO \(L9T5-D8, superseded; .*?\): input ([\d.]+) V", text)
    assert r14 and abs(float(r14.group(1)) + 0.3030 * 0.4512 - float(m.group(2))) < 2e-4, (r14 and r14.group(1), m.group(2))
    # L8R2-F33a after cx45's Q2: record l8r2 withdraws the group-centre claim, and the re-trace cites the PLACED distributed model instead
    p0 = open(os.path.join(ROOT, "v2", "docs", "records", "l8r2", "l8r2_p0.out"), encoding="utf-8").read()
    assert "claim to that effect is WITHDRAWN" in " ".join(p0.split()) and not re.search(r"holds every entry within [\d.]+ mm of its socket on both boards: MET", p0)
    assert not re.search(r"within [\d.]+ mm of its socket on both", text)
    flat = " ".join(text.split())
    assert "a STUDY, the sockets placed on the drawn boards on a stand-in XT60-M land" in flat
    assert "V6-B1 OPEN, REMAINING ENGINEERING (7; the distributed study" in flat and "CORRECTED IN DRAFT on the placed distributed model" not in text
    assert "J_PA and its 16 AWG lead" in text and "PROVISIONAL with L8R2-F43's vendor task" in text


def t_p0_connected_the_verdict_depends_on_the_open_fault_rows():
    """cx46 items 13 and 17: the connected verdict reads REMAINING ENGINEERING while any fault row it depends on is open; the rows are
    read here from the filed cx46 record's JSON independently of the script; no positive thermal or guard acceptance survives"""
    import json as _json
    text = open(CONN_OUT, encoding="utf-8").read()
    flat = " ".join(text.split())
    raw = open(os.path.join(ROOT, "v2", "docs", "records", "l4close", "CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md"), encoding="utf-8").read()
    J = _json.loads(raw.split("```json", 1)[1].split("```", 1)[0])
    state = {int(c["item"].split(".")[0].split(" ")[0]): c["item"].rsplit(": ", 1)[1] for c in J["classification"]}
    m = _mod(CONN, "l9t5_test_conn_faults")
    assert [r[1] for r in m.FAULT_ROWS] == [6, 7, 10, 5, 17, 4, 2]
    rows = re.findall(r"^     (OPEN|SHUT) (.+)\n          cx46 item (\d+): (NOT CLOSED|CLOSED BY THE CORRECTION|CLOSED AS CONDITIONAL);", text, re.M)
    assert len(rows) == len(m.FAULT_ROWS), rows
    for op, _row, item, cl in rows:
        assert state[int(item)] == cl and (op == "OPEN") == (cl == "NOT CLOSED"), (item, cl)
    any_open = any(op == "OPEN" for op, _r, _i, _c in rows)
    assert ("THE CONNECTED ELECTRICAL VERDICT: REMAINING ENGINEERING." in flat) == any_open and any_open
    assert "THE WORST-CASE MARGIN ROW: PROVISIONAL/OPEN" in flat
    assert "the guard row's C-PROT claim reads REMAINING ENGINEERING" in flat and "UNCHECKED" in flat
    preds = text.split("12. THE PREDICATES")[1]
    for bad in ("every revision V T10 row holds its criterion at the taken set point   ", "the final R602 figures: every revision V served state",
                "the placed distributed return holds every printed row"):
        assert bad not in preds, bad
    assert "the connected electrical verdict reads REMAINING ENGINEERING, never a positive acceptance" in preds


def t_round6_t10_cx45_q3_the_containment_and_the_envelope_are_re_solved():
    """The check cx45's Q3, round 6, and its recheck cx46 (l9t5_t10.out 10j), re-solved from the drafts' own values and the printed rows,
    as a DISPOSITION: the schedule's dominant bound inside the share (a traffic model); the limiter's threshold window and the rail trip's
    window reproduce; the rail trip's charging path is RL + RF, so V-B23's 0.2 s does not follow and is withdrawn; cx46's periodic
    countermodel stays under the trip and passes 125 C, so the sustained bound is withdrawn; no positive closure is printed, every item is
    OPEN, PROVISIONAL or REMAINING ENGINEERING; the contract draft carries the withdrawals; revision X has no admission route."""
    m = _mod(T10, "l9t5_test_t10r6")
    gv = m.guard_values()
    assert 6 * 135 + 12 == 822 <= 0.02 * 0.1 * 500e3
    r1, r2 = gv["r1"], gv["r2"]
    k_lo, k_hi = r2 * 0.999 / (r1 * 1.001 + r2 * 0.999), r2 * 1.001 / (r1 * 0.999 + r2 * 1.001)
    e = 25e-9 * r1 * 1.001 * r2 * 1.001 / (r1 * 1.001 + r2 * 1.001)
    d_lo, d_hi = 1 - (0.400 + e) / (3.3 * 0.985 * k_lo), 1 - (0.387 - e) / (3.3 * 1.015 * k_hi)
    assert round(100 * d_lo, 1) == 4.7 and round(100 * d_hi, 1) == 12.3 and 0.02 < d_lo and d_hi < m.FRAME_D_MIN
    rs, rl, rf, cf = gv["rs"], gv["rl"], gv["rf"], gv["cf"]
    i_max = (0.403 / (990e-6 * rl * 0.99) + 1e-3) / (rs * 0.99) + 25e-9 * rf * 1.01 / (990e-6 * rl * 0.99 * rs * 0.99)
    i_min = (0.397 / (1010e-6 * rl * 1.01) - 1e-3) / (rs * 1.01) - 25e-9 * rf * 1.01 / (1010e-6 * rl * 1.01 * rs * 1.01)
    assert round(i_min, 4) == 0.2183 and round(i_max, 4) == 0.2452
    # V-B23 (cx46 6): the charging path is RL + RF; from the bounded state (with the pull-ups) to 0.30 A the average passes i_max late
    tau = (rf + rl) * 1.01 * cf * 1.1
    t = tau * math.log((0.30 - 0.1739) / (0.30 - i_max))
    assert t > 0.2 and abs(t - 0.98) < 0.02
    # cx46's countermodel (7): 0.50 A for 0.40 s every 1.50 s, one pole of 184 K/W and 0.25 s, 0.020 V extra drop, the 0.30 ohm sense
    p_on = (4.1174 - 3.3 * 0.985 - 0.020 - rs * 0.50) * 0.50
    tj = 76.25 + 184.0 * p_on * (1 - math.exp(-0.40 / 0.25)) / (1 - math.exp(-1.50 / 0.25))
    f = 0.50 * (1 - math.exp(-0.40)) / (1 - math.exp(-1.50))
    assert round(p_on, 5) == 0.34845 and abs(tj - 127.54) < 0.02 and f < i_min and tj > m.TJ_GOAL
    out = open(T10_OUT, encoding="utf-8").read()
    sec = out.split("   10j. THE CHECK cx45's Q3")[1].split("\n11. THE STATE OF L9T5-F06")[0]
    for s_ in ("this section is the DISPOSITION", "822 bit-times against FW-B21's 1000", "PROVISIONAL (cx46 5): this establishes the traffic MODEL",
               "silenced when its share passes 4.7 to 12.3 %", "0.2183 to 0.2452 A at the tolerances", "is WITHDRAWN (cx46 6)",
               "127.54 C, OVER 125 C: the universal sustained bound and its positive margin are WITHDRAWN",
               "NOT an acceptance of the sustained bound", "revision X is HELD with no admission route", "CON-004's quorum verdict (OPEN)",
               "DISPOSITION (10j, after cx46): cx45's Q3 NOT CLOSED", "REMAINING ENGINEERING, for the receiving company", "L9T5-F25"):
        assert s_ in sec, s_
    for bad in ("desk acceptance MET", "CORRECTED IN DRAFT", "the trip's maximum holds 125 C", "within 0.2 s and the supervisor"):
        assert bad not in sec, bad
    preds = out.split("12. THE PREDICATES")[1]
    assert "the countermodel stays under the trip's least filtered current and over 125 C" in preds and "V-B23's 0.2 s" in preds
    cd = _mod(CONTRACT_DRAFT, "l9t5_test_contract_r6")
    assert "silicon revision V only" in cd.FW_B20 and "4.01 V" in cd.FW_B20 and "4.18 V" not in cd.FW_B20 and " or X" not in cd.FW_B20
    assert "| FW-B22 |" in cd.FW_B22 and "PROVISIONAL" in cd.FW_B22 and "REMAINING ENGINEERING" in cd.FW_B22
    assert "WITHDRAWN" in cd.V_B23 and "within 0.2 s and the supervisor is unpowered" not in cd.V_B23 and "NOT an acceptance" in cd.V_B20
    page = open(ROUND5, encoding="utf-8").read()
    for s_ in ("## 12. Round 6 and its disposition", "| L9T5-D5 | WITHDRAWN (round 6)", "| L9T5-D8 | SUPERSEDED (round 6)", "| L9T5-D10 (round 6; renamed from D9",
               "- **Revision X: HELD**", "**SUPERSEDED (round 6, and the recheck cx46's item 8)", "Consequence (SUPERSEDED in its admission clauses"):
        assert s_ in page, s_
    assert "For a rev X part: PROVISIONAL" not in page and "L9T5-D9 (round 6)" not in page

def t_record_hygiene():
    files = [SCRIPT, OUT, PAGE, README, os.path.abspath(__file__), DRAFTS, DRAFTS_OUT, CHECK, NEW["a"], NEW["b"], A1, A1_OUT,
             os.path.join(REC, "fetch_held_back.py"), T10, T10_OUT, PRE["a"], PRE["b"], CM5, CM5_OUT, SHDN, CONTRACT_DRAFT, ROUND5,
             F01, F01_OUT, F01D, F01D_OUT, PALOOP, F01_CHECK, F01_NEW["a"], F01_NEW["d"], CONN, CONN_OUT,
             os.path.join(REC, "apply_gen_sch_a_iocset.py"), os.path.join(REC, "apply_gen_sch_b_iocset.py"), GUARD_B]
    inputs = os.path.join(REC, "inputs")
    copies = [os.path.join(inputs, f) for f in sorted(os.listdir(inputs))] if os.path.isdir(inputs) else []
    for p in files + copies:
        need(p, os.path.basename(p))
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "a long dash in %s" % os.path.basename(p)
        for bad in ("/" + "home" + "/", "/" + "tmp" + "/"):
            assert bad not in t, "a private path in %s" % os.path.basename(p)
        if p in (SCRIPT, OUT, PAGE, README, DRAFTS, DRAFTS_OUT, CHECK, A1, A1_OUT, T10, T10_OUT, PRE["a"], PRE["b"], CM5, CM5_OUT, SHDN, CONTRACT_DRAFT, ROUND5,
                 F01, F01_OUT, F01D, F01D_OUT, PALOOP, F01_CHECK, F01_NEW["a"], F01_NEW["d"], CONN, CONN_OUT, GUARD_B):
            if p == README:
                # round 3: the claim table for the recheck V3 labels a maker's printed limit with the round 3 brief's own word. That
                # word is taken out of the table's LABEL cell (the fifth), and of nothing else, before the claim-word scan: the other
                # cells and the prose around the table are still scanned
                kept = []
                for line in t.splitlines():
                    if re.match(r"\| C\d\d \|", line):
                        cells = line.split(" | ")
                        assert len(cells) == 6, "a claim row without six cells: %s" % line[:60]
                        cells[4] = cells[4].replace("guaranteed", "")
                        line = " | ".join(cells)
                    kept.append(line)
                t = "\n".join(kept)
            mm = CLAIM.search(t)
            assert not mm, "a claim word %r in %s" % (mm.group(0), os.path.basename(p))
