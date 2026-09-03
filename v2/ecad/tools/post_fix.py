#!/usr/bin/env python3
"""Small fixes applied directly to the routed board (mirrors of generator changes): move the XIAO site labels."""
import sys, pcbnew
from pcbnew import VECTOR2I, FromMM
b = pcbnew.LoadBoard(sys.argv[1]); OX, OY = 150.0, 110.0
moved = 0
for d in b.GetDrawings():
    if d.GetClass() == "PCB_TEXT" and d.GetText().startswith(("XIAO ESP32S3 + Wio", "1x M2 + tie slots")):
        y = 44.5 + (1.6 if d.GetText().startswith("XIAO") else -1.4)
        d.SetPosition(VECTOR2I(FromMM(OX - 62.0), FromMM(OY - y))); moved += 1
pcbnew.SaveBoard(sys.argv[1], b); print("post_fix: moved %d texts" % moved)
