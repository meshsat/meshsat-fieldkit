#!/usr/bin/env python3
"""Widen a rail's routed copper in place, as far as the board allows (MESHSAT-862, 16 September 2026).

WHY THIS EXISTS. Board A's `+5V_D8` leaves the board through the mezzanine harness and the router laid it at
its class width, 0.4 mm, for 63.9 mm on B.Cu at 1.0 A: 134 mV, 2.68 percent of 5 V, against the 1.5 percent
this board declared as its share of the rail's end-to-end budget. Nothing about that is a routing failure; the
copper is simply too thin for the current, and the class it belongs to is shared with rails that are fine.

The two obvious answers are both worse. Widening the CLASS re-routes the board and costs connections elsewhere
(board D's 1.2 mm ruling cost 27 of 416, measured). Drawing a band across the board is a placement-time
decision made after the placement, and the record carries three cases where a keep-out drawn late cost the
router connections it had already made.

So this widens THE TRACKS THAT ARE ALREADY THERE, which changes no topology at all: same path, same vias, same
pads, more copper. A pad narrower than the target width is respected by leaving the two segments that touch it
alone, because a track wider than its pad spills past the pad edges (board D, 12 September, 191 of 230 pads).

IT IS A TRIAL, NEVER AN EDIT. The board is measured first, the widening is applied, the board is re-filled and
re-measured, and it is kept ONLY if the hard set is no worse than the baseline. Anything else is reverted, and
a width that fails is retried one step narrower. That is the `stub_accept` discipline of 11 September, which
exists because a fixer that hurts silently is worse than no fixer.

Usage: widen_net.py <board.kicad_pcb> <net> [--to 1.0] [--steps 1.0,0.8,0.6] [--layers F.Cu,B.Cu] [--dry]
"""
import os, sys, json, subprocess, shutil, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pcbnew
from pcbnew import FromMM, ToMM


def hard_count(board_path, label):
    """The fifteen-type hard set on this board, through the tools that already decide it."""
    drc = os.path.join(os.path.dirname(os.path.abspath(board_path)) or ".", "out", "widen-%s-drc.json" % label)
    os.makedirs(os.path.dirname(drc), exist_ok=True)
    subprocess.run([os.path.join(HERE, "drc.sh"), board_path, drc], capture_output=True, text=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, "hardset.py"), drc, "post", "--counts"],
                       capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    try:
        return int(next(t.split()[1] for t in out.splitlines() if t.strip().startswith("hard ")))
    except Exception:
        import re
        m = re.search(r"hard (\d+)", out)
        return int(m.group(1)) if m else None


def pad_limit(board, net):
    """The narrowest pad on this net, in mm: a track wider than the pad it lands on spills past its edges."""
    w = None
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.GetNetname().lstrip("/") != net.lstrip("/"): continue
            s = p.GetSize(); m = min(ToMM(s.x), ToMM(s.y))
            w = m if w is None else min(w, m)
    return w


def touches_pad(board, seg, net):
    """True when either end of this segment lands in a pad of its own net: those two are left alone."""
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.GetNetname().lstrip("/") != net.lstrip("/"): continue
            for pt in (seg.GetStart(), seg.GetEnd()):
                if p.HitTest(pt): return True
    return False


def widen(board_path, net, steps, layers=None, dry=False):
    base = hard_count(board_path, "before")
    if base is None:
        print("widen_net: the DRC could not be read, so nothing is changed"); return 2
    print("widen_net: %s at hard %d before" % (os.path.basename(board_path), base))
    board = pcbnew.LoadBoard(board_path)
    lim = pad_limit(board, net)
    print("widen_net: narrowest pad on %s is %s mm" % (net, ("%.2f" % lim) if lim else "unknown"))
    backup = board_path + ".widen-backup"
    shutil.copy(board_path, backup)
    try:
        for target in steps:
            board = pcbnew.LoadBoard(board_path)
            segs, kept, skipped = [], 0, 0
            for t in board.GetTracks():
                if t.GetClass() != "PCB_TRACK": continue          # a via has no width to widen
                if t.GetNetname().lstrip("/") != net.lstrip("/"): continue
                if layers and board.GetLayerName(t.GetLayer()) not in layers: continue
                if ToMM(t.GetWidth()) >= target - 1e-9: continue
                if lim and target > lim and touches_pad(board, t, net): skipped += 1; continue
                segs.append(t)
            if not segs:
                print("widen_net: nothing to widen at %.2f mm (%d segment(s) already at or above it, %d at a narrow pad)"
                      % (target, kept, skipped)); continue
            for t in segs: t.SetWidth(FromMM(target))
            if dry:
                print("widen_net: DRY RUN, %d segment(s) would go to %.2f mm" % (len(segs), target)); return 0
            # THE REFILL BEFORE THE JUDGEMENT, which is the 14 September rule: a pour retreats from copper
            # that has just been widened, and a board measured against a stale fill answers about a board that
            # no longer exists.
            pcbnew.ZONE_FILLER(board).Fill(board.Zones())
            pcbnew.SaveBoard(board_path, board)
            after = hard_count(board_path, "after")
            if after is not None and after <= base:
                print("widen_net: KEPT %d segment(s) at %.2f mm (%d left at a narrow pad); hard %d -> %d"
                      % (len(segs), target, skipped, base, after))
                return 0
            print("widen_net: %.2f mm made it worse (hard %s against %d), reverting and trying narrower"
                  % (target, after, base))
            shutil.copy(backup, board_path)
        print("widen_net: no width in %s could be kept; the board is unchanged"
              % ", ".join("%.2f" % s for s in steps))
        shutil.copy(backup, board_path)
        return 1
    finally:
        if os.path.exists(backup) and os.path.getsize(backup) and not dry:
            os.remove(backup)


def main(argv):
    if len(argv) < 2: print(__doc__); return 2
    board, net = argv[0], argv[1]
    steps = [float(x) for x in argv[argv.index("--steps") + 1].split(",")] if "--steps" in argv else None
    if steps is None:
        to = float(argv[argv.index("--to") + 1]) if "--to" in argv else 1.0
        steps = [to, to * 0.8, to * 0.6]
    layers = argv[argv.index("--layers") + 1].split(",") if "--layers" in argv else None
    return widen(board, net, steps, layers, "--dry" in argv)


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
