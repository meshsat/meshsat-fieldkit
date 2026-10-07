"""Record l4canen and record l9t5's T10 round 9 (MESHSAT-1357, 7 October 2026, W143; v2/docs/records/l4canen/, v2/docs/records/l9t5/):
row (b)'s CAN draft corrected on W139's quorum analysis, held as predicates on what l4canen.py computes and on the round's files, with
the MUTANTS the brief names, each of which must FAIL: an EN route a single peer can hold; a self-test whose S phases never run; FW-B21's
stop at a single window against the GPIO jammer's row.

The predicates: the committed l4canen.out is what the script prints and every input it pins is present at the sha256 it names; every
predicate it states reads yes; its seven mutations read FAIL, the single-peer route among them, and an independent composition here
re-reads the first two; the draft refuses the tree's generator and leaves it byte for byte; the levels, the restart and the recovery
interval are re-solved here from the printed values the output names; the single-window stop loses the quorum under W139's model where
the loss-count stop contains the jammer; round 7's precondition as worded never finds an open own-request diode where the restated
schedule does; the contract text quotes ES0392's workaround as the sheet prints it, with its page; the round page carries the
disposition and claims no closure; the round's new files carry no long dash, no private path and no claim word outside quotations.
These are software predicates on DRAFTS and a desk MODEL: they establish no property of any board, gate, FET, limiter or controller,
and nothing in the kit has been built, bought, powered or measured.

Runs under the suite's runner (`env -C v2/ecad/tools python3 tests/run.py test_l4canen.`); about a minute (the record once, one
composition, W139's model on its quick scan)."""
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
REC = os.path.join(ROOT, "v2", "docs", "records", "l4canen")
L9 = os.path.join(ROOT, "v2", "docs", "records", "l9t5")
SCRIPT = os.path.join(REC, "l4canen.py")
OUT = os.path.join(REC, "l4canen.out")
DRAFT = os.path.join(L9, "apply_gen_sch_b_canen.py")
CONTRACT = os.path.join(L9, "apply_hw_fw_contract_canq.py")
PAGE = os.path.join(L9, "T10-ROUND9.md")
GEN_B = os.path.join(TOOLS, "gen_sch_b.py")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import need  # noqa: E402

_C = {}
CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)


def _out():
    if "out" not in _C:
        need(SCRIPT, "record l4canen's script")
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
    m = re.search(pat, text_, re.M)
    assert m, "the output no longer prints %r" % pat
    return float(m.group(1))


def t_output_reproduced_and_every_input_pinned():
    text_ = _out()
    assert _C["rc"] == 0, "l4canen.py exited %d: %s" % (_C["rc"], _C["err"][-300:])
    assert text_ == open(need(OUT, "the committed output"), encoding="utf-8").read(), "l4canen.out is not what the script prints"
    pins = re.findall(r"^\s{3}([0-9a-f]{16}) (v2/\S+)", text_, re.M)
    assert len(pins) >= 30, pins
    for h, rel in pins:
        assert hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest().startswith(h), "%s is not pinned at its current sha256" % rel


def t_every_predicate_holds():
    rows = [l for l in _out().split("11. THE PREDICATES")[1].splitlines()[1:] if l.strip()]
    assert len(rows) == 13, rows
    assert all(l.endswith(": yes") for l in rows), [l for l in rows if not l.endswith(": yes")]


def t_the_composition_and_the_route_read_by_pin():
    text_ = _out()
    assert text_.count("21 steps, every one OK") == 2
    assert "IDENTICAL with canen (1554 parts" in text_ and "IDENTICAL without it (1521 parts" in text_
    assert re.search(r"no part joining the fabrics\): HOLDS$", text_, re.M)
    assert re.search(r"replaced by W138's limiter and regulator\):\n\s+DRAWN$", text_, re.M)
    assert "order canmb first: DRAWN; order regstage first: DRAWN" in text_
    for t, a, b in (("A", "B", "C"), ("B", "C", "A"), ("C", "A", "B")):
        assert "controller %s's EN: AND of {%s} and {%s}" % (t, a, b) in text_


def t_the_mutations_fail_a_single_peer_route_among_them():
    """the brief's mutant (an EN route a single peer can hold) and six more read FAIL; re-read here on an independent composition: both of
    A's gate inputs from B leaves A's EN to B alone, the FET's gate on B's vote leaves it to B directly; the draft as written gives
    every EN to its two peers"""
    text_ = _out()
    muts = re.findall(r"^     mutated, (.*?):\s+(FAIL|DRAWN) \(A's EN: (.*?)\)$", text_, re.M)
    assert len(muts) == 7 and all(v == "FAIL" for _l, v, _h in muts), muts
    assert muts[0][0].startswith("an EN route a single peer can hold") and muts[0][2] == "AND {B} {B}"
    assert muts[1][2] == "DIRECT {B}"
    assert "without regstage: refused; without canmb: refused; a second time: refused; on the tree's own generator: refused (NOT RELEASED)" in text_
    m = _mod(SCRIPT, "l4canen_under_test")
    E = _mod(DRAFT, "l4canen_draft_under_test")
    with tempfile.TemporaryDirectory(prefix="t_l4canen_") as d:
        seq, res, ok, p, net, nl = m.build(d, "t", first="reg")
        assert ok, res
        assert m.en_check(nl, E)[0] == "DRAWN" and m.holders(nl, 0) == ("AND", {"B"}, {"C"})
        q = m.D.mutate(net, d, "single", [(("U586", "2"), ("R616", "1"))])
        nq = m.CHK.read(open(q, "rb").read())
        assert m.en_check(nq, E)[0] == "FAIL" and m.holders(nq, 0) == ("AND", {"B"}, {"B"})
        q = m.D.mutate(net, d, "direct", [(("Q586", "1"), ("R616", "1"))])
        nq = m.CHK.read(open(q, "rb").read())
        assert m.en_check(nq, E)[0] == "FAIL" and m.holders(nq, 0) == ("DIRECT", {"B"})


def t_the_draft_refuses_the_tree_and_leaves_it_unchanged():
    before = hashlib.sha256(open(GEN_B, "rb").read()).hexdigest()
    r = subprocess.run([sys.executable, "-B", DRAFT, GEN_B, "--write"], capture_output=True)
    assert r.returncode == 3 and b"NOT RELEASED" in r.stderr, r.stderr[-200:]
    r = subprocess.run([sys.executable, "-B", DRAFT, GEN_B], capture_output=True)
    assert r.returncode == 3 and (b"canmb" in r.stderr or b"regstage" in r.stderr), r.stderr[-200:]
    assert hashlib.sha256(open(GEN_B, "rb").read()).hexdigest() == before, "the tree's generator changed"
    E = _mod(DRAFT, "l4canen_draft_under_test")
    assert len(E.ADDS) == 33 and E.REMOVES == () and E.CHANGED == ("R602", "R622", "R642")
    assert sorted(E.RST_PINS) == [59, 60, 61] and E.R_ENPU == "10k 1%" and E.GATE.startswith("SN74LVC1G08") and E.FET == "AO3400A"


def t_the_levels_restart_and_recovery_are_re_solved():
    """re-solved from the printed values the output names: the rail envelope 3.2422 to 3.3577 V; +5V_IOC 3.9063 x 0.98 to 4.1174 V; the
    SN74LVC1G08's ICC 10 uA, delta ICC 500 uA, VCC - 0.15 V at -100 uA, VOL 0.1 V at 100 uA; the AO3400A's VGS(th) 0.65 V and 48 mOhm
    at 2.5 V, IGSS 100 nA, IDSS 5 uA at 55 C; the TPS2553's VIL 0.66 V, VIH 1.1 V, IEN 0.5 uA, ton 3 ms; the TPS737's 431 us; the
    rejoin 0.8 s; the RC 100 kOhm, 1 MOhm, 4.7 uF (+10 %, at least 1 uF effective); the drafted 2 s, 2 s and 10 s"""
    text_ = _out()
    lo, hi = 3.2422, 3.3577
    i_g = 10e-6 + 2 * 500e-6 + hi / (99e3 + 990e3) + 250e-9
    env_lo = lo - 101 * i_g
    k_lo = 990e3 / (101e3 + 990e3)
    k_hi = 1010e3 / (99e3 + 1010e3)
    vinf_lo, vinf_hi = (env_lo - 0.15) * k_lo, hi * k_hi
    rp = lambda a, b: a * b / (a + b)
    rest = 0.1 * k_hi + 100e-9 * rp(101e3, 1010e3)
    tau_min, tau_max = rp(99e3, 990e3) * 1e-6, rp(101e3, 1010e3) * 4.7e-6 * 1.1
    pulse = rest + (vinf_hi - rest) * (1 - math.exp(-4e-3 / tau_min))
    assert abs(_num(r"drives it toward at least ([\d.]+) V", text_) - round(vinf_lo, 4)) < 1e-4 and vinf_lo > 2.5
    assert abs(_num(r"moves the FET's gate to at most ([\d.]+) V", text_) - round(pulse, 4)) < 1e-4 and pulse < 0.65
    en_lo = 4.1174 * (470 * 1.01 + 0.048) / (10e3 * 0.99 + 470 * 1.01 + 0.048)
    assert abs(_num(r"low at most ([\d.]+) V \(", text_) - round(en_lo, 4)) < 1e-4 and en_lo < 0.66
    leak = (3.9063 * 0.98 - 1.1) / (10e3 * 1.01) - 0.5e-6
    assert abs(_num(r"for any leakage up to ([\d.]+) uA", text_) - round(leak * 1e6, 1)) < 0.1 and leak > 5e-6
    t_ch = tau_max * math.log(vinf_lo / (vinf_lo - 2.5))
    assert abs(_num(r"passes 2\.5 V within ([\d.]+) s of the second vote", text_) - round(t_ch, 3)) < 1e-3 and t_ch < 2.0
    t_dis = tau_max * math.log((vinf_hi - rest) / (0.65 - rest))
    rec = 2.0 + 1e-3 + 2.0 + t_dis + 3e-3 + 431e-6 + 0.8
    assert abs(_num(r"= ([\d.]+) s \(MODEL on PRINTED, DRAFTED and the boot ASSUMPTION\)", text_) - round(rec, 3)) < 1e-3 and rec < 10.0
    assert "before this round: NONE," in text_


def t_the_single_window_stop_fails_the_jammer_row():
    """the brief's mutant: FW-B21's drafted single-window stop FAILS the GPIO jammer's row (M1c: required 'a node out and contained'),
    and the stop at the loss count contains it, under W139's model on its quick scan"""
    q = _mod(os.path.join(L9, "l9t5_canq.py"), "l9t5_canq_for_l4canen")
    one = q.analyse({"stop_windows": 1}, scan="quick", only=("M1c",), latent=False, recover=False)
    three = q.analyse(None, scan="quick", only=("M1c",), latent=False, recover=False)
    assert one["rows"][("restated", "M1c")]["outcome"] == 0, "the single-window stop does not lose the quorum: the mutant does not FAIL"
    assert three["rows"][("restated", "M1c")]["outcome"] == 1 and three["rows"][("restated", "M1c")]["sc"].required == 1
    assert "the single-window stop FAILS the jammer row" in _out()


def t_a_self_test_whose_s_phases_never_run_fails():
    """the brief's mutant: round 7's precondition as worded never runs an S phase, so an open own-request diode is never found (W139's
    model, quick scan); the restated schedule finds it within the 2.60 s the record states"""
    q = _mod(os.path.join(L9, "l9t5_canq.py"), "l9t5_canq_for_l4canen")
    P, _Q = q.figures()
    lit = q.detect({"own_dead": {("A", "A")}}, dict(q.CFG, variant="w137", w137_literal=True), P, "quick")
    rst = q.detect({"own_dead": {("A", "A")}}, dict(q.CFG, variant="restated"), P, "quick")
    assert lit is None, "round 7's literal precondition finds the fault: the mutant does not FAIL"
    assert rst is not None and rst / 1e6 <= 2.60, rst


def t_the_contract_quotes_es0392_with_its_page():
    m = _mod(SCRIPT, "l4canen_under_test")
    F = m.figures()
    src = open(need(CONTRACT, "the contract draft"), encoding="utf-8").read()
    row = m.literal(src, "FW_B22_CANQ")
    assert "ES0392 Rev 15 2.24.5's printed workaround (page 48/73: '%s')" % F["es_work"] in row
    assert F["es_work"].startswith("Upon failure, clear the corresponding Tx buffer transmission request bit TRPx")
    assert "DAR = 1" in row and "RESTART" in row and "12-window cycle" in row and "its only frame in that hold" in row
    assert "more than 3 windows" in m.literal(src, "FW_B21_NEW")


def t_the_round_page_states_the_disposition():
    page = open(need(PAGE, "the round page"), encoding="utf-8").read()
    first = page.splitlines()[0]
    assert first.startswith("**ROUND 9") and "DONE:" in first and "NOT DONE:" in first and "NEXT:" in first, first[:200]
    for s_ in ("W139-F2", "W139-F5", "W139-F8", "W137-F1", "2.60 s", "5.603 s", "page 48/73", "43 of 100; 14 supplies, 43 unconnected",
               "apply_gen_sch_b_canen.py", "None is APPLIED", "NOT CLOSED", "W143-D1", "W143-F1", "AND {B} {B}"):
        assert s_ in page, s_
    for bad in ("CORRECTED IN DRAFT", "cx46's item 5 CLOSED", "quorum service HOLDS", "desk acceptance MET"):
        assert bad not in page, bad


def t_record_hygiene():
    files = [SCRIPT, OUT, DRAFT, PAGE, os.path.join(REC, "fetch_held_back.py"), os.path.join(REC, "inputs", "SOURCES.txt"), os.path.abspath(__file__)]
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
