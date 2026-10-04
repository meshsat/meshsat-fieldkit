"""Layer 9 task T5, record l9t5 (MESHSAT-1357, 4 October 2026; v2/docs/records/l9t5/): C-ALLTX rev 2 and C-DEV rev 1, held as
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
              "%.3f mOhm" % (A["a2_band"][2] * 1000), "%.4f V" % A["a3_unc"]["need"], "16.214", "C-ALLTX rev 2", "C-DEV rev 1"):
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
    """the generator with one draft on a scratch copy, regenerated by record l8p's gen_netlist.py: (rc, netlist path or last line)."""
    import subprocess
    gn = _mod(os.path.join(ROOT, "v2", "docs", "records", "l8p", "gen_netlist.py"), "l9t5_test_gen_netlist")
    t = os.path.join(d, "%s_gen_sch_%s.py" % (tag, board))
    shutil.copy(GENS[board], t)
    r = subprocess.run([sys.executable, "-B", script, t, "--write"], capture_output=True)
    assert r.returncode == 0, "the draft refused a clean copy: %s" % r.stderr.decode()[-300:]
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
    assert len(rows) == 12 and all(l.rstrip().endswith(" yes") for l in rows), rows
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
    assert "BOARD A'S HALF: HOLDS" in txt and "BOARD B'S HALF: HOLDS" in txt
    # round 3: the shared return's finding stays visible beside the result, and I-03 stays open until the independent recheck
    assert "L8R2-F31 stays OPEN beside this result and is not this record's" in txt and "I-03 STAYS OPEN" in txt


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
    assert not [f for f in os.listdir(REC) if f.startswith("apply_gen_sch_d_")]


def t_record_hygiene():
    files = [SCRIPT, OUT, PAGE, README, os.path.abspath(__file__), DRAFTS, DRAFTS_OUT, CHECK, NEW["a"], NEW["b"], A1, A1_OUT,
             os.path.join(REC, "fetch_held_back.py")]
    inputs = os.path.join(REC, "inputs")
    copies = [os.path.join(inputs, f) for f in sorted(os.listdir(inputs))] if os.path.isdir(inputs) else []
    for p in files + copies:
        need(p, os.path.basename(p))
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "a long dash in %s" % os.path.basename(p)
        for bad in ("/" + "home" + "/", "/" + "tmp" + "/"):
            assert bad not in t, "a private path in %s" % os.path.basename(p)
        if p in (SCRIPT, OUT, PAGE, README, DRAFTS, DRAFTS_OUT, CHECK, A1, A1_OUT):
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
