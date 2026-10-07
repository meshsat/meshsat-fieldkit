"""Layer 4 task L4A-54, record l9t5 round 7 (MESHSAT-1357, 7 October 2026; v2/docs/records/l9t5/): the ledger's RE-5 and HO-C by method
M-B, the peers' TXD observation and 2-of-2 SHDN vote on both fabrics (apply_gen_sch_b_canmb.py), held as predicates on what
l9t5_canmb.py computes and on the files of the round.

The predicates: the committed l9t5_canmb.out is what the script prints and every input it pins is present at the sha256 it names;
every predicate the script states reads yes (twelve); its six mutations read FAIL, the three the brief names among them, and CON-004
reads HOLDS with and without the draft; the draft refuses the tree's generator, a target without iocguard and a second application,
and leaves the tree byte for byte; its pin plan covers each (peer, fabric) once with pins the tree's controller map leaves free; the
levels, the interval and the controller's rail figure are re-solved here from the makers' printed values the output prints; the
round page carries the disposition, the SESSION decisions and the findings and claims no closure; the record's new files carry no
long dash, no private path and no claim word outside quotations. These are software predicates on a DRAFT and its arithmetic: they
establish no property of any board, transceiver, gate or controller, and nothing in the kit has been built or measured.
"""
import ast
import hashlib
import importlib.util
import math
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l9t5")
SCRIPT = os.path.join(REC, "l9t5_canmb.py")
OUT = os.path.join(REC, "l9t5_canmb.out")
DRAFT = os.path.join(REC, "apply_gen_sch_b_canmb.py")
PAGE = os.path.join(REC, "T10-ROUND6.md")
GEN_B = os.path.join(TOOLS, "gen_sch_b.py")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need  # noqa: E402

_C = {}
CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)


def _out():
    """the script run from the repository root, once; its stdout, its exit status"""
    if "out" not in _C:
        need(SCRIPT, "the round 7 script")
        r = subprocess.run([sys.executable, "-B", SCRIPT], cwd=ROOT, capture_output=True)
        _C["out"], _C["rc"], _C["err"] = r.stdout.decode("utf-8"), r.returncode, r.stderr.decode("utf-8", "replace")
    return _C["out"]


def _draft():
    sp = importlib.util.spec_from_file_location("l9t5_canmb_draft_under_test", need(DRAFT, "the draft"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _num(pat, text_):
    m = re.search(pat, text_)
    assert m, "the output no longer prints %r" % pat
    return float(m.group(1))


def t_output_reproduced_and_every_input_pinned():
    text_ = _out()
    assert _C["rc"] == 0, "l9t5_canmb.py exited %d: %s" % (_C["rc"], _C["err"][-300:])
    assert text_ == open(need(OUT, "the committed output"), encoding="utf-8").read(), "l9t5_canmb.out is not what the script prints"
    pins = re.findall(r"^\s{3}([0-9a-f]{16}) (v2/\S+)", text_, re.M)
    assert len(pins) >= 25, pins
    for h, rel in pins:
        assert hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest().startswith(h), "%s is not pinned at its current sha256" % rel


def t_every_predicate_holds():
    text_ = _out()
    rows = [l for l in text_.split("9. THE PREDICATES")[1].splitlines()[1:] if l.strip()]
    assert len(rows) == 12, rows
    assert all(l.endswith(": yes") for l in rows), [l for l in rows if not l.endswith(": yes")]


def t_the_mutations_fail_and_con004_holds():
    """the brief's three mutations (a draft that removes a fabric, a vote output not reaching its SHDN, an observation reading the
    node's own TXD) and three more each read FAIL; CON-004 reads HOLDS on the candidate with and without the draft"""
    text_ = _out()
    muts = re.findall(r"^   mutated, (.*?):\s+(FAIL|DRAWN|HOLDS|REFUSED) \((.*?)\)$", text_, re.M)
    assert len(muts) == 6 and all(v == "FAIL" for _l, v, _b in muts), muts
    labs = " | ".join(l for l, _v, _b in muts)
    for s_ in ("a draft that removes fabric B", "a vote that does not reach its SHDN", "an observation reading the node's own TXD",
               "a 1-of-1 vote", "the gate on a peer's rail", "an observation without its isolation"):
        assert s_ in labs, s_
    assert re.search(r"no part joining the fabrics\): HOLDS \(before canmb: HOLDS\)", text_)
    assert "the limiter's parts gone; the rail trips in place): DRAWN" in text_
    assert "the draft on a generator without iocguard: refused; a second time: refused; on the tree's own generator: refused (NOT RELEASED)" in text_


def t_the_draft_refuses_the_tree_and_leaves_it_unchanged():
    before = hashlib.sha256(open(GEN_B, "rb").read()).hexdigest()
    r = subprocess.run([sys.executable, "-B", DRAFT, GEN_B, "--write"], capture_output=True)
    assert r.returncode == 3 and b"NOT RELEASED" in r.stderr, r.stderr[-200:]
    r = subprocess.run([sys.executable, "-B", DRAFT, GEN_B], capture_output=True)
    assert r.returncode == 3 and b"iocguard" in r.stderr, r.stderr[-200:]
    assert hashlib.sha256(open(GEN_B, "rb").read()).hexdigest() == before, "the tree's generator changed"


def t_the_pin_plan_covers_each_peer_and_fabric_on_free_pins():
    m = _draft()
    assert sorted((d, f) for _p, (_port, d, f, _af, _n) in m.OBS_PINS.items()) == [(1, "A"), (1, "B"), (2, "A"), (2, "B")]
    assert sorted((d, f) for _p, (_port, d, f) in m.VOTE_PINS.items()) == [(1, "A"), (1, "B"), (2, "A"), (2, "B")]
    assert all(af == 2 and func.startswith("TIM3_CH") for _p, (_port, _d, _f, func, af) in m.OBS_PINS.items())
    assert len(set(m.ADDS)) == 12 and len(set(m.REMOVES)) == 12 and not set(m.ADDS) & set(m.REMOVES)
    # the tree's controller map (read with ast) and canshdn's two SHDN pins leave every planned pin free
    tree = ast.parse(open(GEN_B, encoding="utf-8").read())
    h743 = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "H743")
    src = open(GEN_B, encoding="utf-8").read()
    blk = src[src.index('    m.update({14: "IOC%s_RST_n" % _tag'):src.index("    synth(U_(1), \"STM32H743VI\"")]
    used = {int(x) for x in re.findall(r"(?<![\d.])(\d{1,3}): \"", blk)} | {83, 53}
    for p, row in list(m.OBS_PINS.items()) + list(m.VOTE_PINS.items()):
        assert p not in used, "pin %d is already on the controllers' map" % p
        assert h743[p] == row[0], "pin %d is %s on the generator's table, not %s" % (p, h743[p], row[0])
    text_ = _out()
    assert text_.count("free before: yes") == 24 and "free before: NO" not in text_
    assert re.search(r"the candidate with canmb\s+40 of 100; 14 supplies, 46 unconnected \(the same for B and C: yes\)", text_)
    assert re.search(r"the tree's board B \(U41, committed netlist\)\s+30 of 100; 14 supplies, 56 unconnected", text_)


def t_the_levels_and_the_rail_are_re_solved():
    """re-solved here from the printed values the output names: the AP2112K-3.3 band 98.5 to 101.5 % with -1 to +1 %/A at 0.25 A; the
    H743's VOH VDD - 0.4 V and VOL 0.4 V at 8 mA, VIL 0.3 VDD, VIH 0.7 VDD, RPU at least 30 kOhm; the SN74LVC1G08's VCC - 0.15 V at
    -100 uA and the 1N4148W's 0.715 V; the TCAN334's SHDN VIH 2 V and IIL 4 uA"""
    text_ = _out()
    m = _draft()
    lo, hi = 3.3 * (0.985 - 0.01 * 0.25), 3.3 * (1.015 + 0.01 * 0.25)
    riso = float(re.match(r"([\d.]+)k", m.R_ISO).group(1)) * 1e3
    assert abs(_num(r"0\.25 A: ([\d.]+) V to", text_) - round(lo, 4)) < 1e-4 and abs(_num(r"V to ([\d.]+) V, inside the gate", text_) - round(hi, 4)) < 1e-4
    obs_lo = 0.4 + (hi - 0.4) * riso * 1.01 / (riso * 1.01 + 30e3)
    assert abs(_num(r"TXD low reads at most ([\d.]+) V", text_) - round(obs_lo, 4)) < 1e-4 and obs_lo < 0.3 * lo
    assert abs(_num(r"SHDN lifted by the vote: at least ([\d.]+) V", text_) - round(lo - 0.15 - 0.715, 4)) < 1e-4 and lo - 0.15 - 0.715 > 2.0
    fault = hi / (riso * 0.99) + hi / (riso * 0.99 + 30e3)
    assert abs(_num(r"at most ([\d.]+) mA through its", text_) - round(fault * 1e3, 3)) < 1e-3 and fault < 8e-3
    assert 4e-6 * 105e3 < 0.8 and lo - 0.4 > 2.0 and lo - 0.4 > 0.7 * hi
    rail = 0.1739 - 2 * hi / 9.9e3 + 2 * 10e-6 + 4 * hi / (riso * 0.99 + 30e3) + max(2 * hi / 9.5e3, 2 * 500e-6)
    assert abs(_num(r"all at once: at most ([\d.]+) A", text_) - round(rail, 4)) < 1e-4 and rail < 0.2558


def t_the_self_test_interval_is_re_solved():
    """six transceivers, four phases each, one per 100 ms window, a 2nd consecutive failure: (24 x 0.1 + 0.1) x 2 = 5.0 s, the crystal's
    +-20 ppm included; the hardware response is tMODE 10 us + 3.6 ns + 16.6 ns; the guard 10 ms over the 4.6 ms queue"""
    text_ = _out()
    cyc = 6 * 4 * 0.1 * (1 + 20e-6)
    det = 2 * (cyc + 0.1 * (1 + 20e-6))
    assert abs(_num(r"x 100 ms = ([\d.]+) s;", text_) - round(cyc, 4)) < 1e-4
    assert abs(_num(r"DETECTED WITHIN ([\d.]+) s of its onset", text_) - round(det, 2)) < 1e-2 and det < 10.0
    t_on = 16.6e-9 + 3.6e-9 + 10e-6
    assert abs(_num(r"silence takes effect within ([\d.]+) us", text_) - round(t_on * 1e6, 3)) < 1e-3
    t_off = 105e3 * 20e-12 * math.log(3.3 * (1.015 + 0.0025) / 0.8) + 10e-6
    assert abs(_num(r"it ends within ([\d.]+) us of the release", text_) - round(t_off * 1e6, 2)) < 1e-2
    assert abs(_num(r"margin ([\d.]+) ms", text_) - round((10e-3 - (4.6e-3 + 2 * 20e-6 * 0.1 + t_off)) * 1e3, 3)) < 1e-3
    sec = text_.split("THE SELF-TEST'S OWN FAULTS")[1].split("   coverage:")[0]
    assert sec.count("RESIDUAL") == 3 and sec.count("within 5.00 s") >= 10
    assert "every part canmb adds or re-uses is among them: yes" in text_
    assert "finding W137-F1" in text_ and "firmware does not use DAR" in text_


def t_the_round_page_states_the_disposition():
    page = open(need(PAGE, "the round page"), encoding="utf-8").read()
    first = page.splitlines()[0]
    assert first.startswith("**ROUND 7") and "DONE:" in first and "NOT DONE:" in first and "NEXT:" in first, first[:200]
    for s_ in ("CON-004", "IOHA row 7", "A7", "L4A-55", "W137-D1", "W137-D2", "W137-F1", "NOT CLOSED", "REMAINING ENGINEERING",
               "40 of 100; 14 supplies, 46 unconnected", "5.00 s", "apply_gen_sch_b_canmb.py", "None is APPLIED"):
        assert s_ in page, s_
    for bad in ("CORRECTED IN DRAFT", "cx46's item 5 CLOSED", "quorum service HOLDS", "desk acceptance MET"):
        assert bad not in page, bad


def t_record_hygiene():
    files = [SCRIPT, OUT, DRAFT, PAGE, os.path.abspath(__file__)]
    for p in files:
        t = open(need(p, os.path.basename(p)), encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "a long dash in %s" % os.path.basename(p)
        for bad in ("/" + "home" + "/", "/" + "tmp" + "/"):
            assert bad not in t, "a private path in %s" % os.path.basename(p)
        if p != os.path.abspath(__file__):
            scan = re.sub(r"\"[^\"\n]*\"", "", t)          # a quotation of a record or a sheet is the record's word, not this round's
            mm = CLAIM.search(scan)
            assert not mm, "a claim word %r in %s" % (mm.group(0), os.path.basename(p))
