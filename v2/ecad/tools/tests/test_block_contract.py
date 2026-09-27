#!/usr/bin/env python3
"""The dock block against the board whose pins land on it (rule SCH-003 for E5, MESHSAT-862, 17 Sep 2026; INT-001 on
E5 since 27 September 2026, MESHSAT-1357, stream w4r).

Board E5 has no schematic and no netlist: `gen_pcb_e5.py` reads board A's BOARD FILE, finds the spring-pin
connector and puts a target under each pin carrying that pin's net. `check_contracts.py` had declared that
unjudgeable and written INCONCLUSIVE, which was honest and left the one BLIND-MATE interface in the kit with
no check on its pin map at all: the pins are hidden once it is assembled, so a target on the wrong net is
invisible until 9 A of pack current is on the wrong conductor.

Since 27 September 2026 the tool reads board A's NETLIST (its current candidate) and the J_DOCK land that netlist names,
never board A's board file. The proofs are fixtures, never the tree's design state (a test that fails when the design is
fixed is a test about history): an acceptable pair whose verdict must be PASS (the block as built against a board A
netlist carrying exactly the dock map the block was generated from), and defective ones whose verdict must be FAIL (one
target's net changed; a power pin board A gains with no target under it). They need KiCad, so they skip where pcbnew is
not importable and run where the boards are. What a reading records, the thing rules_status binds, is asked of a run on
the tree's own files, whatever that run's answer is.
"""
import os, re, sys, tempfile, subprocess, json, hashlib, atexit, shutil

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
from harness import Skip, need
import block_contract as B

ECAD = os.path.dirname(TOOLS)
E5 = os.path.join(ECAD, "pcb-e5-block", "pcb-e5-block.kicad_pcb")


def _tmp(prefix):
    d = tempfile.mkdtemp(prefix=prefix)
    atexit.register(shutil.rmtree, d, True)
    return d


def _run(board, out_dir, a=None):
    env = dict(os.environ, VERDICT_DIR=out_dir)
    args = [sys.executable, os.path.join(TOOLS, "block_contract.py"), board] + ([a] if a else [])
    p = subprocess.run(args, capture_output=True, text=True, env=env, cwd=ECAD)
    f = os.path.join(out_dir, "check_contracts_e5.verdict.json")
    rec = json.load(open(f)) if os.path.exists(f) else {}
    return p, rec


def _need_kicad():
    try: import pcbnew  # noqa: F401
    except Exception as e: raise Skip("no pcbnew here (%s)" % type(e).__name__)
    need(E5, "board E5 is not in this tree")


def _block_map(board_text):
    """{pin: net} the block's own targets were generated from: T_SIG's pads carry `<net>_P<pin>`."""
    root = B._sexp(board_text)[0]
    out = {}
    for fp in root[1:]:
        if not (isinstance(fp, list) and fp and fp[0] == "footprint"): continue
        ref = next((x[2] for x in fp[1:] if isinstance(x, list) and len(x) > 2 and x[0] == "property" and x[1] == "Reference"), None)
        if ref != B.SIGNAL_TARGET: continue
        for pad in fp[1:]:
            if not (isinstance(pad, list) and pad and pad[0] == "pad"): continue
            net = B._kv(pad, "net")
            m = re.fullmatch(r"(.+)_P(\d+)", str(net[-1]) if net else "")
            if m: out[int(m.group(2))] = m.group(1)
    return out


def _netlist(dock, extra=()):
    """A board A netlist with J_DOCK on `dock` ({pin: net}), the pack pins E5 carries targets for, and `extra`
    ((ref, net) power pins)."""
    comps = [("J_DOCK", "meshsat:PogoPins_2x6")]
    power = [("J_CP%d" % k, "CELL+") for k in range(1, 5)] + [("J_CN%d" % k, "GND") for k in range(1, 5)] + \
            [("J_PRE1", "PRECHG")] + list(extra)
    comps += [(r, "meshsat:Mill-Max_0858_power_pin") for r, _n in power]
    nets = {}
    for pin, net in dock.items(): nets.setdefault(net, []).append(("J_DOCK", str(pin)))
    for r, net in power: nets.setdefault(net, []).append((r, "1"))
    L = ['(export (version "E")', '  (components']
    L += ['    (comp (ref "%s") (value "fixture") (footprint "%s"))' % (r, f) for r, f in comps]
    L += ['  )', '  (nets']
    for i, (net, nodes) in enumerate(sorted(nets.items()), 1):
        L.append('    (net (code "%d") (name "/%s")' % (i, net) +
                 "".join(' (node (ref "%s") (pin "%s") (pintype "passive"))' % n for n in nodes) + ")")
    L += ['  )', ')']
    return "\n".join(L) + "\n"


def _pair(prefix, board_text=None, extra=()):
    """(block path, board A netlist path, out dir) of a fixture pair in a temporary directory."""
    need(E5, "board E5 is not in this tree")
    d = _tmp(prefix)
    txt = board_text if board_text is not None else open(E5, encoding="utf-8", errors="replace").read()
    b = os.path.join(d, "pcb-e5-block.kicad_pcb"); open(b, "w", encoding="utf-8").write(txt)
    dock = _block_map(open(E5, encoding="utf-8", errors="replace").read())
    assert len(dock) == 12, dock
    n = os.path.join(d, "pcb-a-power.net"); open(n, "w", encoding="utf-8").write(_netlist(dock, extra))
    return b, n, d


def t_the_block_passes_against_the_dock_map_it_was_generated_from():
    """The acceptable input: the block as built, against a board A netlist whose J_DOCK carries the map the block's
    targets name. The signal half passes only if the land mounted as DOCK_MOUNT says puts each pin over the target that
    names it, so this is the geometry's proof too."""
    _need_kicad()
    b, n, d = _pair("block-ok-")
    p, rec = _run(b, d, n)
    assert rec.get("verdict") == "PASS", ((p.stdout + p.stderr)[-800:], rec.get("counts"), rec.get("evidence"))
    assert (rec.get("counts") or {}).get("pass", 0) >= 30, rec


def t_a_target_on_the_wrong_net_is_refused():
    """The defective fixture: one signal target's net renamed in a copy of the block. Board A's netlist is the one
    the block was generated from, so the only thing that can refuse it is the comparison itself."""
    _need_kicad()
    txt = open(E5, encoding="utf-8", errors="replace").read()
    m = re.search(r'"(\w[\w+]*_P\d+)"', txt)
    assert m, "the block carries no <net>_P<pin> target net to damage"
    b, n, d = _pair("block-bad-", txt.replace('"%s"' % m.group(1), '"WRONG_P99"'))
    p, rec = _run(b, d, n)
    assert rec.get("verdict") == "FAIL", \
        "a target carrying another net was accepted: %s\n%s" % (rec.get("counts"), (p.stdout + p.stderr)[-400:])
    assert any("WRONG_P99" in str(e) for e in (rec.get("evidence") or [])), rec.get("evidence")


def t_a_power_pin_board_a_gains_with_no_target_is_refused():
    """EQ-16's shape: board A's netlist gains four VIN_RAW power pins and four returns, and the block carries no target
    under them. A pin the stack lowers onto nothing is a FAIL naming the pins, not a pass of the pins that exist."""
    _need_kicad()
    extra = [("J_VR%d" % k, "VIN_RAW") for k in range(1, 5)] + [("J_VN%d" % k, "GND") for k in range(1, 5)]
    b, n, d = _pair("block-pin-", extra=extra)
    p, rec = _run(b, d, n)
    assert rec.get("verdict") == "FAIL", ((p.stdout + p.stderr)[-600:], rec.get("counts"))
    ev = " ".join(str(e) for e in rec.get("evidence") or [])
    assert "J_VR1" in ev and "J_VN1" in ev, ev


def t_it_records_what_binds_it_to_both_boards():
    """What rules_status binds a reading by: E5's board file (its design) by sha, board A's netlist by sha and by
    content, the J_DOCK land by sha, and no other board file, because a reading of board A's layout could be current
    only when that layout is (OTHER_BOARD). Asked of a run on the tree's own files, whatever it answers."""
    _need_kicad()
    d = _tmp("block-inputs-")
    _p, rec = _run(E5, d)
    inp = rec.get("inputs") or {}
    sha = hashlib.sha256(open(E5, "rb").read()).hexdigest()[:16]
    assert (inp.get("board") or {}).get("sha256_16") == sha, inp.get("board")
    an = inp.get("board_a_netlist") or {}
    assert str(an.get("path", "")).endswith("pcb-a-power.net") and an.get("sha256_16") and an.get("content16"), an
    assert str((inp.get("dock_land") or {}).get("path", "")).endswith(".kicad_mod"), inp.get("dock_land")
    boards = [v for v in inp.values() if isinstance(v, dict) and str(v.get("path", "")).endswith(".kicad_pcb")]
    assert all(v.get("sha256_16") == sha for v in boards), boards
    assert "INT-001" in (rec.get("rules") or []) and "SCH-003" in (rec.get("rules") or []), rec.get("rules")


def t_the_contract_check_no_longer_writes_this_board_s_verdict():
    """Two tools writing one verdict name is how a reading gets overwritten by a weaker one."""
    src = open(os.path.join(TOOLS, "check_contracts.py"), encoding="utf-8").read()
    i = src.index("for _bd in sorted(set(list(per_board)")
    assert 'if _bd == "E5": continue' in src[i:i + 400], \
        "check_contracts still writes board E5's verdict, which block_contract.py now decides"
    assert "check_contracts_e5" not in src[i:], "check_contracts still names board E5's verdict"
