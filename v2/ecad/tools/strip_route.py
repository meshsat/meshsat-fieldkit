#!/usr/bin/env python3
"""strip_route: turn a released (routed) board back into its pre-route board by removing every unlocked track and via.

The locked copper stays: escape stubs and vias (escape.py), fanout vias (prefanout.py), adjacent-pin joins (join_adjacent_pins.py), the A21
rail spines and any hand-laid bus. Zones are refilled on save so the result is the board a sweep starts from without re-running its chain.
Boards whose fanout predates the locking rule (see the plan of 6 Sep 2026) must regenerate through their pre-route chain instead; the counts
printed here tell which: a released board with zero locked vias is one of those.
Usage: strip_route.py <routed.kicad_pcb> <out.kicad_pcb>"""
import sys, pcbnew

src, dst = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(src)
removed_t = removed_v = kept_t = kept_v = 0
for t in list(b.GetTracks()):
    is_via = t.GetClass() == "PCB_VIA"
    if t.IsLocked():
        if is_via: kept_v += 1
        else: kept_t += 1
        continue
    b.Remove(t)
    if is_via: removed_v += 1
    else: removed_t += 1
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(dst, b)
print("strip_route: removed %d tracks and %d vias, kept %d locked tracks and %d locked vias -> %s" % (removed_t, removed_v, kept_t, kept_v, dst))
if kept_v == 0 and kept_t == 0: print("strip_route: WARNING no locked copper at all; this board predates the locking rule, regenerate it through its pre-route chain")
