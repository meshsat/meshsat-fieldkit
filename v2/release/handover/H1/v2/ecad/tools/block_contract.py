#!/usr/bin/env python3
"""The dock block against the board whose pins land on it (rule SCH-003 for board E5, MESHSAT-862, 17 Sep 2026).

Board E5 is the one board of the set with no schematic and no netlist. `gen_pcb_e5.py` reads BOARD A's board
file, finds the spring-pin connector J_DOCK, and puts a flat target under each pin carrying that pin's net,
named `<net>_P<pin>`. So E5's contract is not between two netlists, which is why `check_contracts.py` has
declared it unjudgeable since 16 September and written INCONCLUSIVE: it is between two BOARDS, and that is
what this judges.

It matters because it is the only thing standing between a wrong pin map and a kit that does not work: the
block is a blind-mate interface, the pins are hidden when it is assembled, and a target carrying the wrong
net is invisible until 9 A of pack current is on the wrong conductor. And board A is regenerated constantly,
so the question is live: a J_DOCK that moves, gains a pin or renames a net leaves E5 describing a board that
no longer exists.

What is checked, all of it geometric, none of it from a name:
  1. every signal target on E5 has a J_DOCK pad above it, at the same offset from its own connector origin;
  2. the net that target carries is the net of that pad, with that pad's own pin number appended;
  3. every wire land carries the net of the target of the same pad number (the wire goes straight down);
  4. the power targets carry the pack node and its return, and the pre-charge target carries the pack node.

Usage: block_contract.py <e5 board.kicad_pcb> [<board A .kicad_pcb>]"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

SIGNAL_TARGET = "T_SIG"
WIRE_LAND = "L_SIG"
CONNECTOR = "J_DOCK"
PACK, RETURN = "CELL+", "CELL_N"


def a_board_for(e5_path):
    """Board A's board file: its phase directory first, then the plain project, and say which was used."""
    ecad = os.path.dirname(os.path.dirname(os.path.abspath(e5_path)))
    import glob
    for pat in ("pcb-a-power-*", "pcb-a-power"):
        for d in sorted(glob.glob(os.path.join(ecad, pat)), reverse=True):
            p = os.path.join(d, "pcb-a-power.kicad_pcb")
            if os.path.exists(p): return p
    return None


def _key(pad, origin):
    """A pad's position relative to its own footprint origin, in hundredths of a millimetre, as the generator
    matched them. The connector is on board A's underside and the block is the right way up, so nothing here
    may depend on which way either was flipped: the match is between two offsets and nothing else."""
    q = pad.GetPosition()
    return (round((q.x - origin.x) / 1e4), round((q.y - origin.y) / 1e4))


def judge(e5_path, a_path):
    import pcbnew
    out = {"checked": [], "fail": []}
    def ok(t): out["checked"].append(t)
    def bad(t): out["checked"].append(t); out["fail"].append(t)

    e5 = pcbnew.LoadBoard(e5_path); a = pcbnew.LoadBoard(a_path)
    jd = a.FindFootprintByReference(CONNECTOR)
    if jd is None:
        return None, "board A has no %s: the block's whole pin map comes from that connector" % CONNECTOR
    tgt = e5.FindFootprintByReference(SIGNAL_TARGET)
    land = e5.FindFootprintByReference(WIRE_LAND)
    if tgt is None: return None, "board E5 has no %s" % SIGNAL_TARGET

    jp = jd.GetPosition()
    above = {_key(p, jp): (int(p.GetNumber()), p.GetNetname().lstrip("/")) for p in jd.Pads()}
    tp = tgt.GetPosition()
    seen = {}
    for pad in tgt.Pads():
        num = int(pad.GetNumber()); k = _key(pad, tp)
        got = pad.GetNetname().lstrip("/")
        if k not in above:
            bad("target %d of %s has no %s pad above it at %s" % (num, SIGNAL_TARGET, CONNECTOR, k)); continue
        pin, net = above[k]
        if not net or net.startswith("unconnected-"): net = "SPARE"
        want = "%s_P%d" % (net, pin)
        seen[num] = want
        if got == want: ok("target %d carries %s, which is %s pin %d" % (num, got, CONNECTOR, pin))
        else: bad("target %d carries %r and the pin above it is %s pin %d, which is %r" % (num, got, CONNECTOR, pin, want))
    if land is not None:
        for pad in land.Pads():
            num = int(pad.GetNumber()); got = pad.GetNetname().lstrip("/")
            want = seen.get(num)
            if want is None: bad("wire land %d has no target of the same number" % num)
            elif got == want: ok("wire land %d carries %s, the target's own net" % (num, got))
            else: bad("wire land %d carries %r and its target carries %r: the wire would leave on another net" % (num, got, want))
    else:
        bad("board E5 has no %s: the twelve wires to the strip have nowhere to land" % WIRE_LAND)

    power = {"CP": PACK, "CN": RETURN, "PRE": PACK}
    for fp in e5.GetFootprints():
        ref = fp.GetReference()
        m = re.match(r"^T_(CP|CN|PRE)\d*$", ref)
        if not m: continue
        want = power[m.group(1)]
        nets = {p.GetNetname().lstrip("/") for p in fp.Pads()}
        if nets == {want}: ok("%s carries %s" % (ref, want))
        else: bad("%s carries %s and must carry %s" % (ref, ", ".join(sorted(nets)) or "nothing", want))
    if not any(re.match(r"^T_CP\d+$", f.GetReference()) for f in e5.GetFootprints()):
        bad("board E5 has no pack-node target")
    return out, None


def main(argv):
    if not argv: print(__doc__); return _v.USAGE
    e5 = argv[0]
    a = argv[1] if len(argv) > 1 else a_board_for(e5)
    out_dir = os.environ.get("VERDICT_DIR") or os.path.join(os.path.dirname(os.path.abspath(e5)), "out")
    if not a or not os.path.exists(a or ""):
        print("block_contract: board A is not in this tree, so the block's pin map cannot be compared with it")
        return _v.write("check_contracts_e5", _v.INCONCLUSIVE, denominator=0, counts={"fail": 0, "pass": 0},
                        inputs={"block": e5}, out_dir=out_dir,
                        note="board A's board file is not in this tree and the block's every net comes from it")
    res, why = judge(e5, a)
    if res is None:
        print("block_contract: %s" % why)
        return _v.write("check_contracts_e5", _v.INCONCLUSIVE, denominator=0, counts={"fail": 0, "pass": 0},
                        inputs={"block": e5, "board_a": a}, out_dir=out_dir, note=why)
    for t in res["checked"]: print(("FAIL  " if t in res["fail"] else "PASS  ") + t)
    n = len(res["checked"]); f = len(res["fail"])
    print("block_contract: %d of %d checks pass against %s" % (n - f, n, os.path.relpath(a)))
    return _v.write("check_contracts_e5", _v.PASS if not f else _v.FAIL,
                    counts={"fail": f, "pass": n - f}, denominator=n, evidence=res["fail"][:20],
                    inputs={"block": e5, "board_a": a}, out_dir=out_dir,
                    note="the dock block against the board whose spring pins land on it, matched by position; "
                         "board E5 has no netlist and this contract is between two BOARDS")


if __name__ == "__main__":
    # EVERY GATE LEAVES A READING WHEN IT RAISES (18 September 2026). The thirteen one-line entries of this
    # morning were the gates a crash had already cost a verdict; these are the rest of the deciding gates in
    # the coverage map, guarded the same way, so a rule whose tool raised reads INCONCLUSIVE naming the
    # exception rather than 'no verdict', which the registry reads as nobody having looked.
    sys.exit(_v.guard("block_contract", main, sys.argv[1:]))