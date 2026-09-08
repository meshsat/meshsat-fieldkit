#!/usr/bin/env python3
"""Jittered placements for the learned-critic data campaign (MESHSAT-862 Stage E1, 8 Sep 2026). Takes a placed, unrouted board (the chain's
board after gen_pcb_*3.py, before escape.py) and a seed, and returns a neighbour of that placement: every shelf-packed passive (C, R, L, D, FB, Q references; the gates pin the ICs and
connectors to 0.6 mm) moves by a uniform offset within +-DX mm (0.4 mm: the packer's 1.2 mm gap minus courtyard growth), and pairs of footprints with the same footprint id within SWAP mm of each other are swapped with
probability P_SWAP. The chain's own gates decide whether the sample is legal (courtyard overlaps and the numeric gate refuse it); the router
then labels it. The pre-route hash of each sample is its identity in the journal (routeflow rule).

Usage: place_jitter.py <board.kicad_pcb> <seed> [--dx 1.0] [--swap 15] [--p-swap 0.3] [--fixed REF,REF]   -> writes the board in place, prints the moves."""
import sys, os, random, re, pcbnew

def main(a):
    if len(a) < 2: print(__doc__); return 2
    b = pcbnew.LoadBoard(a[0]); seed = int(a[1]); rnd = random.Random(seed)
    dx = float(a[a.index("--dx") + 1]) if "--dx" in a else 0.4; swap = float(a[a.index("--swap") + 1]) if "--swap" in a else 15.0
    ps = float(a[a.index("--p-swap") + 1]) if "--p-swap" in a else 0.3
    fixed = set(a[a.index("--fixed") + 1].split(",")) if "--fixed" in a else set()
    # only the shelf-packed passives move (C, R, L, D, FB, Q): the board gates check the ICs' and connectors' positions to 0.6 mm, so a moved U or J is refused before it is routed (first campaign, 8 Sep 2026: 20 of 20 D8 samples refused at 1 mm on every part)
    fps = [f for f in b.GetFootprints() if not f.IsLocked() and f.GetReference() not in fixed and re.match(r"^(C|R|L|D|FB|Q)\d", f.GetReference())]
    moved = 0
    for f in fps:
        ox, oy = rnd.uniform(-dx, dx), rnd.uniform(-dx, dx); f.Move(pcbnew.VECTOR2I(int(ox * 1e6), int(oy * 1e6))); moved += 1
    byid = {}
    for f in fps: byid.setdefault(f.GetFPIDAsString(), []).append(f)
    swapped = 0
    for fid, group in byid.items():
        rnd.shuffle(group)
        for i in range(0, len(group) - 1, 2):
            f, g = group[i], group[i + 1]; pf, pg = f.GetPosition(), g.GetPosition()
            if ((pf.x - pg.x) ** 2 + (pf.y - pg.y) ** 2) ** 0.5 <= swap * 1e6 and rnd.random() < ps:
                f.SetPosition(pg); g.SetPosition(pf); swapped += 1
    pcbnew.SaveBoard(a[0], b)
    print("place_jitter: seed %d, %d footprints moved by up to %.1f mm, %d pairs swapped, %d fixed" % (seed, moved, dx, swapped, len(list(b.GetFootprints())) - moved))
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
