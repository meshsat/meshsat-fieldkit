#!/usr/bin/env python3
"""A18 on the routed A17 board, no part moves: J_DOCK drills 1.5 -> 1.1 mm for the Preci-Dip 813-S1-008-10-016101 solder tails
(0.8 mm, appendix 32.10), silk phase label A17 -> A18. Pads keep their 2.2 mm size, so the annular ring only grows."""
import sys, pcbnew
from pcbnew import VECTOR2I, FromMM
b = pcbnew.LoadBoard(sys.argv[1]); n = t = 0
for fp in b.GetFootprints():
    if fp.GetReference() == "J_DOCK":
        for p in fp.Pads():
            if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                p.SetDrillSize(VECTOR2I(FromMM(1.1), FromMM(1.1))); n += 1
for d in b.GetDrawings():
    if isinstance(d, pcbnew.PCB_TEXT) and "(A17)" in d.GetText():
        d.SetText(d.GetText().replace("(A17)", "(A18)")); t += 1
pcbnew.SaveBoard(sys.argv[1], b); print("bump_a18: %d J_DOCK drills set to 1.1 mm, %d phase labels" % (n, t))
