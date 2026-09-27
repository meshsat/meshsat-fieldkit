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


def hard_count(board_path, label, want_report=False):
    """The fifteen-type hard set on this board, through the tools that already decide it.

    With `want_report` it also returns the DRC path, because WHERE a violation is decides which segments have
    to give the width back: a rail is not refused by its whole length, it is refused at the two or three places
    where the corridor is full."""
    drc = os.path.join(os.path.dirname(os.path.abspath(board_path)) or ".", "out", "widen-%s-drc.json" % label)
    os.makedirs(os.path.dirname(drc), exist_ok=True)
    subprocess.run([os.path.join(HERE, "drc.sh"), board_path, drc], capture_output=True, text=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, "hardset.py"), drc, "post", "--counts"],
                       capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    n = None
    try:
        n = int(next(t.split()[1] for t in out.splitlines() if t.strip().startswith("hard ")))
    except Exception:
        import re
        m = re.search(r"hard (\d+)", out)
        n = int(m.group(1)) if m else None
    return (n, drc) if want_report else n


def hard_places(drc_path):
    """(x, y) in mm of every hard violation in this report, so the offenders can be found by position."""
    try:
        d = json.load(open(drc_path, encoding="utf-8"))
    except Exception:
        return []
    import importlib.util
    spec = importlib.util.spec_from_file_location("hardset", os.path.join(HERE, "hardset.py"))
    hs = importlib.util.module_from_spec(spec); spec.loader.exec_module(hs)
    types = set(getattr(hs, "HARD_POST", ()) or ())
    out = []
    for v in (d.get("violations") or []):
        if types and v.get("type") not in types: continue
        for it in (v.get("items") or []):
            p = it.get("pos") or {}
            if "x" in p and "y" in p: out.append((float(p["x"]), float(p["y"])))
    return out


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
            orig_w = {t.m_Uuid.AsString(): ToMM(t.GetWidth()) for t in segs}
            for t in segs: t.SetWidth(FromMM(target))
            if dry:
                print("widen_net: DRY RUN, %d segment(s) would go to %.2f mm" % (len(segs), target)); return 0
            # THE REFILL BEFORE THE JUDGEMENT, which is the 14 September rule: a pour retreats from copper
            # that has just been widened, and a board measured against a stale fill answers about a board that
            # no longer exists.
            pcbnew.ZONE_FILLER(board).Fill(board.Zones())
            pcbnew.SaveBoard(board_path, board)
            after, drc = hard_count(board_path, "after", want_report=True)
            if after is not None and after <= base:
                print("widen_net: KEPT %d segment(s) at %.2f mm (%d left at a narrow pad); hard %d -> %d"
                      % (len(segs), target, skipped, base, after))
                return 0
            # THE RAIL IS NOT REFUSED BY ITS LENGTH, IT IS REFUSED AT THE PLACES WHERE THE CORRIDOR IS FULL
            # (16 September 2026). Board A's +5V_D8 at 1.0 mm read 7 hard and at 0.6 mm read 3, and giving the
            # whole rail back for them wastes the ninety percent of its length that had room. Each round hands
            # the width back ONLY where a violation is, and asks the board again; it stops when the board is
            # clean or when a round gives nothing back, which is the honest end of the search.
            for _round in range(3):
                places = hard_places(drc)
                if not places: break
                board = pcbnew.LoadBoard(board_path)
                gave, R = 0, 2.0   # mm: a violation is reported at a point, the segment that caused it is near it
                for t in board.GetTracks():
                    if t.GetClass() != "PCB_TRACK": continue
                    if t.GetNetname().lstrip("/") != net.lstrip("/"): continue
                    if abs(ToMM(t.GetWidth()) - target) > 1e-6: continue
                    sx, sy = ToMM(t.GetStart().x), ToMM(t.GetStart().y)
                    ex, ey = ToMM(t.GetEnd().x), ToMM(t.GetEnd().y)
                    mx, my = (sx + ex) / 2.0, (sy + ey) / 2.0
                    if any(min((px - sx) ** 2 + (py - sy) ** 2, (px - ex) ** 2 + (py - ey) ** 2,
                               (px - mx) ** 2 + (py - my) ** 2) <= R * R for px, py in places):
                        t.SetWidth(FromMM(orig_w.get(t.m_Uuid.AsString(), 0.4))); gave += 1
                if not gave: break
                pcbnew.ZONE_FILLER(board).Fill(board.Zones()); pcbnew.SaveBoard(board_path, board)
                after, drc = hard_count(board_path, "after", want_report=True)
                print("widen_net: gave %d segment(s) back at the %d violation site(s); hard now %s"
                      % (gave, len(places), after))
                if after is not None and after <= base:
                    left = sum(1 for t in pcbnew.LoadBoard(board_path).GetTracks()
                               if t.GetClass() == "PCB_TRACK" and t.GetNetname().lstrip("/") == net.lstrip("/")
                               and abs(ToMM(t.GetWidth()) - target) < 1e-6)
                    print("widen_net: KEPT %d of %d segment(s) at %.2f mm; hard %d -> %d"
                          % (left, len(segs), target, base, after))
                    return 0
            print("widen_net: %.2f mm made it worse (hard %s against %d) and giving the offenders back did not "
                  "recover it, reverting and trying narrower" % (target, after, base))
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
