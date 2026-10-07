"""Record l4hod (MESHSAT-1357, 7 October 2026, W146; v2/docs/records/l4hod/, record l9t5's apply_gen_sch_b_hodtest.py): Layer 4 task
L4A-58, the ledger's HO-D under W138's limiter, held as predicates on what l4hod.py computes and on the record's files, with the
MUTANTS the brief names, each of which must FAIL: a test that cannot detect a lost limit; a stuck test switch left undetected; a test
a single peer can start.

The predicates: the committed l4hod.out is what the script prints and every input it pins is present at the sha256 it names; every
predicate it states reads yes; the composition in every order the four drafts admit gives one netlist; the test path reads DRAWN and
each test needs a 2-of-2 of its target's two peers, re-read here on an independent composition with the single-peer and the lost-limit
mutants; the draft refuses the tree's generator and leaves it byte for byte; the judge's demand, lost-limit current and pass band are
re-solved here from the printed values the output names; the judge's mutants (a test load that never makes a healthy limiter limit, a
TYPICAL deglitch used as a bound) FAIL; the procedure's mutants (no single-switch steps, no restore check first) leave faults NOT FOUND;
the page carries the disposition and claims no closure; the record's files carry no long dash, no private path and no claim word
outside quotations. These are software predicates on DRAFTS and a desk MODEL: they establish no property of any board, limiter, switch
or controller, and nothing in the kit has been built, bought, powered or measured.

Runs under the suite's runner (`env -C v2/ecad/tools python3 tests/run.py test_l4hod.`); about a minute (the record once and one
composition)."""
import hashlib
import importlib.util
import math
import os
import re
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4hod")
L9 = os.path.join(ROOT, "v2", "docs", "records", "l9t5")
SCRIPT = os.path.join(REC, "l4hod.py")
OUT = os.path.join(REC, "l4hod.out")
PAGE = os.path.join(REC, "L4HOD.md")
DRAFT = os.path.join(L9, "apply_gen_sch_b_hodtest.py")
GEN_B = os.path.join(TOOLS, "gen_sch_b.py")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import need  # noqa: E402

_C = {}
CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)


def _out():
    if "out" not in _C:
        need(SCRIPT, "record l4hod's script")
        r = subprocess.run([sys.executable, "-B", SCRIPT], cwd=ROOT, capture_output=True)
        _C["out"], _C["rc"], _C["err"] = r.stdout.decode("utf-8"), r.returncode, r.stderr.decode("utf-8", "replace")
    return _C["out"]


def _mod(path, name):
    if name not in _C:
        sp = importlib.util.spec_from_file_location(name, need(path, os.path.basename(path)))
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        _C[name] = m
    return _C[name]


def _num(pat, text_):
    m = re.search(pat, text_, re.M) or re.search(pat, " ".join(text_.split()))
    assert m, "the output no longer prints %r" % pat
    return float(m.group(1))


def t_output_reproduced_and_every_input_pinned():
    text_ = _out()
    assert _C["rc"] == 0, "l4hod.py exited %d: %s" % (_C["rc"], _C["err"][-300:])
    assert text_ == open(need(OUT, "the committed output"), encoding="utf-8").read(), "l4hod.out is not what the script prints"
    pins = re.findall(r"^\s{3}([0-9a-f]{16}) (v2/\S+)", text_, re.M)
    assert len(pins) >= 30, pins
    for h, rel in pins:
        assert hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest().startswith(h), "%s is not pinned at its current sha256" % rel


def t_every_predicate_holds():
    rows = [l for l in _out().split("12. THE PREDICATES")[1].splitlines()[1:] if l.strip()]
    assert len(rows) == 14, rows
    assert all(l.endswith(": yes") for l in rows), [l for l in rows if not l.endswith(": yes")]


def t_the_composition_in_every_order():
    text_ = _out()
    orders = re.findall(r"^     order (.*?):\s+(\d+) steps, every one (OK|NOT OK)$", text_, re.M)
    assert len(orders) == 5 and all(v == "OK" for _o, _n, v in orders), orders
    assert {o for o, _n, _v in orders} == {"canmb, regstage, canen, hodtest", "canmb, regstage, hodtest, canen", "regstage, canmb, canen, hodtest",
                                            "regstage, canmb, hodtest, canen", "regstage, hodtest, canmb, canen"}
    assert "the netlists of the 5 orders: IDENTICAL (1608 parts" in text_ and "without this draft (canmb, regstage, canen): 1554 parts" in text_
    assert "CON-004 on the composed netlist (record l4canen's reading): HOLDS; canmb by pin on the limiter's state: DRAWN; canen's EN route by pin: DRAWN" in text_
    assert "it removes 0; changes the value or nets of 6: U41, U45, U51, U55, U61, U65" in text_


def t_a_test_a_single_peer_can_start_fails_and_a_test_that_cannot_detect_a_lost_limit_fails():
    """the brief's mutants on the netlist, re-read here on an independent composition (the order regstage, hodtest, canmb, canen): the two
    halves' gates on one peer, and the upper half bridged, each leave the test to one controller; the load moved ahead of the limiter
    leaves no load on its output, so no lost limit is ever shown; the draft as written needs both of the target's peers for every test"""
    text_ = _out()
    muts = re.findall(r"^     mutated, (.*?):\s+(FAIL|DRAWN) \(A's test: (.*?); read by", text_, re.M)
    assert len(muts) == 7 and all(v == "FAIL" for _l, v, _s in muts), muts
    assert muts[0][2] == "1 of 1" and muts[1][2] == "1 of 1" and muts[2][2] == "SELF" and muts[3][2] == "NO LOAD"
    m = _mod(SCRIPT, "l4hod_under_test")
    H = _mod(DRAFT, "l4hod_draft_under_test")
    with tempfile.TemporaryDirectory(prefix="t_l4hod_") as d:
        seq, res, ok, p, net, nl = m.build(d, "RHME")
        assert ok, res
        assert m.hod_check(nl, H)[0] == "DRAWN"
        assert [m.start_verdict(nl, k)[0] for k in range(3)] == ["2 of 2"] * 3
        assert m.starters(nl, 0)[1] == [{"B", "C"}]
        q = m.D.mutate(net, d, "single", [(("Q591", "1"), ("R802", "1"))])
        nq = m.CHK.read(open(q, "rb").read())
        assert m.hod_check(nq, H)[0] == "FAIL" and m.start_verdict(nq, 0)[0] == "1 of 1" and m.starters(nq, 0)[1] == [{"B"}]
        q = m.D.mutate(net, d, "ahead", [(("R800", "1"), ("C940", "1"))])
        nq = m.CHK.read(open(q, "rb").read())
        assert m.hod_check(nq, H)[0] == "FAIL" and m.start_verdict(nq, 0)[0] == "NO LOAD"


def t_the_draft_refuses_the_tree_and_leaves_it_unchanged():
    before = hashlib.sha256(open(GEN_B, "rb").read()).hexdigest()
    r = subprocess.run([sys.executable, "-B", DRAFT, GEN_B, "--write"], capture_output=True)
    assert r.returncode == 3 and b"NOT RELEASED" in r.stderr, r.stderr[-200:]
    r = subprocess.run([sys.executable, "-B", DRAFT, GEN_B], capture_output=True)
    assert r.returncode == 3 and b"regstage" in r.stderr, r.stderr[-200:]
    assert hashlib.sha256(open(GEN_B, "rb").read()).hexdigest() == before, "the tree's generator changed"
    H = _mod(DRAFT, "l4hod_draft_under_test")
    assert len(H.ADDS) == 54 and H.REMOVES == () and H.CHANGED == ("U45", "U55", "U65")
    assert sorted(H.TEST_PINS) == [15, 16, 42, 43, 44, 45] and H.R_LOAD == "3R 1% 2512 1W" and H.FET == "AO3400A" and H.DIODE.startswith("BAT46W")
    src = open(DRAFT, encoding="utf-8").read()
    assert "None is APPLIED" in src and "NOT RELEASED" in src and "_RSTV%s" in src


def t_the_judge_is_re_solved_from_the_printed_values():
    """re-solved from the values the output prints: the limiter's band 0.4702 to 0.5878 A (SLVS841F's 49.9 kOhm row with the 1 % RILIM,
    enveloped with TI's Equation 1 at the resistor's bounds, W159 on W157-F2);
    the test load 3.0 Ohm at 1 %, 200 ppm/C over 51.25 K and the load life's 1 % + 0.05 Ohm; the switches' 48 mOhm at 2.5 V scaled by the
    10 V rows' 38/26.5; the limiter's 0.135 Ohm; record l9t5's supply path (W138's); the rail's top 4.1174 V; U601's 3 A; the regulator's
    76.0 C/W at the 0.8669 V corner from 76.25 C air"""
    text_ = _out()
    tcr = 200e-6 * 51.25
    rlo = 3.0 * 0.99 * (1 - tcr) * 0.99 - 0.05
    rhi = 3.0 * 1.01 * (1 + tcr) * 1.01 + 0.05
    assert abs(_num(r"R_T ([\d.]+) to [\d.]+ Ohm \(1 %", text_) - round(rlo, 4)) < 1e-4
    assert abs(_num(r"R_T [\d.]+ to ([\d.]+) Ohm \(1 %", text_) - round(rhi, 4)) < 1e-4
    lost = 4.1174 / rlo
    assert abs(_num(r"a lost limit draws at most ([\d.]+) A", text_) - round(lost, 4)) < 1e-3
    s3 = 0.4240
    assert lost + 3 * s3 <= 3.0
    i125 = (125.0 - 76.25) / (76.0 * 0.8669)
    assert abs(_num(r"the regulator's 125 C current is ([\d.]+) A", text_) - round(i125, 4)) < 1e-3
    pmax = _num(r"a PASS admits IOS [\d.]+ to ([\d.]+) A", text_)
    assert pmax < i125, (pmax, i125)
    rfet = 0.048 * 0.038 / 0.0265
    fixed = _num(r"at board B \(W138's reading of it\): the least input ([\d.]+) V less", text_)
    r_sup = _num(r"V less ([\d.]+) Ohm times the lead's current", text_)
    dmin = (fixed - 2 * s3 * r_sup) / (rhi + 2 * rfet + 0.135 + r_sup)
    assert abs(_num(r"the demand at the least input ([\d.]+) A against IOSmax", text_) - round(dmin, 4)) < 2e-4, dmin
    assert dmin > 1.8 * 0.5878
    v_ov = 2.5 * math.sqrt(1.0 * 3.0)
    assert abs(_num(r"short-time overload of 2\.5 x RCWV = ([\d.]+) V for 5 s", text_) - round(v_ov, 3)) < 1e-3 and 4.1174 < v_ov
    assert re.search(r"^   the judge: HOLDS$", text_, re.M)


def t_the_makers_rows_are_read_as_printed():
    """the record's own reads of the makers' texts (through its PDFTEXT table; the held sheets' texts staged as the suite stages them):
    SLVS841F's 49.9 kOhm row and deglitch, the FAULT rows, SBVS067W's EN low and its shutdown current (TYPICAL), the AO3400A's 2.5 V
    row, the BAT46W's forward rows, DS12110 revision V's VBOR2 and its ADC note, SLLSEQ7F's undervoltage row, RM0433's reset sentence,
    UNI-ROYAL's 2512 rating, overload factor, TCR and load life"""
    m = _mod(SCRIPT, "l4hod_under_test")
    F = m.figures()
    assert F["ios49"][0] == (0.475, 0.52, 0.565) and F["ios49"][1] == "PRINTED"
    assert F["deglitch"][0] == (0.005, 0.0075, 0.01) and F["deglitch"][1] == "PRINTED" and F["tios"][1] == "TYPICAL"
    assert F["flt_vol"][0] == (0.18, 0.001) and F["flt_lkg"][0] == 1e-6 and F["flt_sink"][0] == (0.025, 0.01)
    assert F["ldo_en_lo"][0] == 0.5 and F["ldo_shdn"][1] == "TYPICAL" and F["ldo_rja"][0] == 76.0
    assert F["rds25"][0] == 0.048 and F["vth"][0] == (0.65, 1.05, 1.45) and F["vf"][0] == (0.25, 0.45)
    assert F["vbor2"][0] == (2.25, 2.31, 2.37) and F["tue_typ"][1] == "TYPICAL" and F["tcan_uv"][0] == (1.65, 2.0, 2.5)
    assert F["rm_reset"].startswith("During and just after reset") and F["latch_exit"].startswith("The device remains off")
    assert F["uni_p"][0] == 1.0 and F["uni_ov_k"][0] == 2.5 and abs(F["uni_tcr"][0] - 200e-6) < 1e-12 and F["uni_life"][0] == (0.01, 0.05)
    assert [F["t9"][p_][1] for p_ in (15, 16, 42)] == ["FT_a", "FT_ha", "FT_h"]


def t_the_judges_mutants_fail():
    """a test load that never makes a healthy limiter limit (10 Ohm) cannot tell a lost limit from a healthy one: J1 FAILS; a TYPICAL
    deglitch used as a bound FAILS J0; single steps over the least deglitch FAIL J6; re-run here on the module's judge"""
    m = _mod(SCRIPT, "l4hod_under_test")
    text_ = _out()
    jm = re.findall(r"^     mutated, (.*?):\s+(FAILS \(.*?\)|HOLDS)$", text_, re.M)
    assert len(jm) == 5 and all(v.startswith("FAILS") for _l, v in jm), jm
    assert jm[0][1] == "FAILS (J0)" and "J1" in jm[1][1] and "J6" in jm[3][1]
    assert jm[1][0].startswith("a test that cannot detect a lost limit")


def t_a_stuck_test_switch_left_undetected_fails():
    """the brief's mutant on the procedure: without the single-switch steps a half stuck on is found by nothing (NOT FOUND), and without
    the restore check first a restore-route fault leaves its supervisor latched; the full procedure leaves no single fault NOT FOUND and
    only the part's own latch can leave its supervisor off"""
    m = _mod(SCRIPT, "l4hod_under_test")
    full = set(m.CHECKS)
    rows = m.faults(full)
    assert not [r for r in rows if r[3] is None]
    assert [(r[0], r[5]) for r in rows if r[5]] == [("the limiter", True)]
    no2 = m.faults(full - {"single_a", "single_b"})
    und = [r for r in no2 if r[3] is None]
    assert any(r[0] == "the upper switch" and r[1].startswith("drain-source short") for r in und)
    assert any(r[0] == "the lower switch" and r[1].startswith("drain-source short") for r in und)
    no1 = m.faults(full - {"pre"})
    assert any(r[0] == "canen's restore route" and r[3] is None and r[5] for r in no1)
    text_ = _out()
    pm = re.findall(r"^   mutated procedure, (.*?):\s+(FAIL|HOLDS) ", text_, re.M)
    assert len(pm) == 5 and all(v == "FAIL" for _l, v in pm), pm


def t_the_interval_and_the_detection_interval():
    """the interval out of the quorum and the detection interval re-added from the printed and drafted terms the output names"""
    text_ = _out()
    m = re.search(r"THE INTERVAL THE TARGET IS OUT of the quorum: ([\d.]+) s \(the announcement ([\d.]+) s, step 1 ([\d.]+) s, settle ([\d.]+) s, "
                  r"step 2 ([\d.]+) s, step 3 ([\d.]+) s, step 4 ([\d.]+) s\)", text_)
    assert m
    vals = [float(x) for x in m.groups()]
    assert abs(vals[0] - sum(vals[1:])) < 2e-3 and vals[0] < 10.0
    step4 = 1e-3 + 2.0 + 0.799 + 3e-3 + 1.5e-3 + 0.8
    assert abs(vals[6] - step4) < 1e-3
    det = _num(r"a limit lost after start-up is found within\s+3600 s \+ [\d.]+ s = ([\d.]+) s", text_)
    assert 3600.0 < det < 3610.0
    flat = " ".join(text_.split())
    assert "W139's loss count respected" in flat and "survivors' gap 0 windows against the loss count 3" in flat
    assert "is NOT bounded on printed figures" in flat and "PROVISIONAL, finding W146-F10" in flat
    # the hold-up, re-solved: the rail before the step on record l9t5's path with all three at their peak, the survivors' need at their
    # limiter's input (the TPS737's 1.5 % and 0.25 V at 1 A scaled, plus the limiter's 0.135 Ohm), board B's 10.3 uF, a survivor's 12.0 uF
    v0 = 3.7579 - 3 * 0.4240 * 0.04252
    need_ = 3.3 * 1.015 + 0.25 * 0.4240 + 0.4240 * 0.135
    t_rail = 10.3e-6 * (v0 - need_) / 1.4396
    t_hold = 12.0e-6 * (3.3 * 0.985 - 2.37) / 0.4240
    assert abs(_num(r"the survivors stay out of reset if U601 and the lead carry the step within ([\d.]+) us", text_) - (t_rail + t_hold) * 1e6) < 0.15


def t_the_page_states_the_disposition():
    raw = open(need(PAGE, "the record's page"), encoding="utf-8").read()
    first = raw.splitlines()[0]
    page = " ".join(raw.split())
    assert first.startswith("**L4A-58") and "DONE:" in first and "NOT DONE:" in first and "NEXT:" in first, first[:200]
    for s_ in ("apply_gen_sch_b_hodtest.py", "None is APPLIED", "NOT CLOSED", "REMAINING ENGINEERING", "W146-D1", "W146-F1", "W146-F10",
               "5.945 s", "3602.341 s", "2 of 2", "1 of 1", "NO LOAD", "49 of 100; 14 supplies, 37 unconnected", "PROVISIONAL", "D406"):
        assert s_ in page, s_
    for bad in ("HO-D CLOSED", "cx46's item 6 CLOSED", "desk acceptance MET", "CORRECTED IN DRAFT"):
        assert bad not in page, bad


def t_record_hygiene():
    files = [SCRIPT, OUT, DRAFT, PAGE, os.path.join(REC, "inputs", "SOURCES.txt"), os.path.abspath(__file__)]
    for p in files:
        t = open(need(p, os.path.basename(p)), encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "a long dash in %s" % os.path.basename(p)
        for bad in ("/" + "home" + "/", "/" + "tmp" + "/"):
            assert bad not in t, "a private path in %s" % os.path.basename(p)
        if p != os.path.abspath(__file__):
            scan = re.sub(r"\"[^\"\n]*\"", "", t)
            mm = CLAIM.search(scan)
            assert not mm, "a claim word %r in %s" % (mm.group(0), os.path.basename(p))


# pytest aliases
for _n, _f in list(globals().items()):
    if _n.startswith("t_") and callable(_f):
        globals()["test_" + _n[2:]] = _f
