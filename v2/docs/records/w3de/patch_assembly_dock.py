#!/usr/bin/env python3
"""DRAFT for the owner of v2/docs/ASSEMBLY.md (w3de, 27 September 2026): the dock's wiring after EQ-16.

Board E's half of EQ-16 (gen_sch_e.py) adds the 12 AWG pads P_VR (VIN_RAW) and P_VN (GND) and puts J_BLK pins 1 to 4 on
GND. The lead table, build step 2 and the E6/E5 fitting lists name "the twelve signal wires and the 12 AWG pair"; after
EQ-16 there are two 12 AWG pairs (the pack's and VIN_RAW's), and the signal wires carry no VIN_RAW. Apply with board A's
half and E5's (drafts/w3de/EQ16-dock-vin-raw.md), not before: until then the block has no holes for the second pair.

Usage: patch_assembly_dock.py <tree root holding v2/docs>"""
import os, sys
p = os.path.join(sys.argv[1], "v2", "docs", "ASSEMBLY.md")
s = open(p, encoding="utf-8").read(); o = s
EDITS = [
    ("| Block signal wires | E6 `J_BLK` (twelve lands) | dock block wire lands, underside | 24 AWG, 60 mm each, named on the block's legend | soldered both ends |\n"
     "| Block power pair | E6 `P_CP` and `P_CN` | dock block wire holes | 12 AWG silicone, 60 mm | soldered both ends |",
     "| Block signal wires | E6 `J_BLK` (twelve lands: 1 to 7 and 11 ground, 8 SHORE_INHIBIT, 9 and 10 USB, 12 spare; no VIN_RAW since EQ-16) | dock block wire lands, underside | 24 AWG, 60 mm each, named on the block's legend | soldered both ends |\n"
     "| Block power pair | E6 `P_CP` and `P_CN` | dock block wire holes | 12 AWG silicone, 60 mm | soldered both ends |\n"
     "| Block VIN_RAW pair (EQ-16, 27 September 2026) | E6 `P_VR` (VIN_RAW) and `P_VN` (its return) | the dock block's two VIN_RAW wire holes, under board A's `J_VR1`-`J_VR4` and `J_VN1`-`J_VN4` | 12 AWG silicone, 60 mm | soldered both ends |"),
    ("Solder the twelve signal wires and the 12 AWG pair from the strip into the block's plated lands from below;",
     "Solder the twelve signal wires and the two 12 AWG pairs (the pack's `P_CP`/`P_CN` and, since EQ-16, VIN_RAW's `P_VR`/`P_VN`) from the strip into the block's plated lands from below;"),
    ("the twelve signal wires and the 12 AWG pair up to the block,",
     "the twelve signal wires and the two 12 AWG pairs up to the block (EQ-16),"),
    ("and the twelve signal wires and the 12 AWG pair are soldered into its plated lands from below before the stack is fitted.",
     "and the twelve signal wires and the two 12 AWG pairs (EQ-16) are soldered into its plated lands from below before the stack is fitted."),
]
for old, new in EDITS:
    if s.count(old) != 1: raise SystemExit("patch_assembly_dock: the old text is not there exactly once: %r" % old[:90])
    s = s.replace(old, new)
assert s != o
open(p, "w", encoding="utf-8").write(s); print("patch_assembly_dock: %s edited, %d hunks" % (p, len(EDITS)))
