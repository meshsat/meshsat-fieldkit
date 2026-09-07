#!/usr/bin/env python3
"""fix_c7_u3.py <board.kicad_pcb>: the post-route closure of C7 run 2 (7 Sep 2026 09:40 UTC, appendix 32.61).

Freerouting 1.9.0 left one connection open on the C7 backer: pad 1 of the RP2040 (IOVDD, +3V3), whose escape via sits fenced between the
0.4 mm escape rows, the router's In2 and F.Cu tracks and the B.Cu pours; a continuation route thrashed for 25 minutes, the stub router
closed nothing, and every detour outside the part crossed another net. The free copper is INSIDE the QFN outline, on B.Cu between the
pad tips and the exposed pad: a locked 0.127 mm track from pad 1 east to x = 421.52 (0.19 mm past the pad tips at 421.33, 0.39 mm
short of the RAIL_SENSE via at 422.02), north to pad 10 (IOVDD as well), and back onto it. DRC after the refill: 0 hard, 0 unconnected.
Kept here as the record of a hand fix on the routed board (the rule: post-route fixes are bars on top of router tracks, checked by DRC)."""
import sys, pcbnew
FromMM = pcbnew.FromMM
b = pcbnew.LoadBoard(sys.argv[1]); u3 = next(fp for fp in b.GetFootprints() if fp.GetReference() == "U3")
p1 = next(p for p in u3.Pads() if p.GetNumber() == "1"); p10 = next(p for p in u3.Pads() if p.GetNumber() == "10"); net = p1.GetNetCode()
XI = FromMM(421.52); pts = [(p1.GetPosition().x, p1.GetPosition().y), (XI, p1.GetPosition().y), (XI, p10.GetPosition().y), (p10.GetPosition().x, p10.GetPosition().y)]
for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
    t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(x0, y0)); t.SetEnd(pcbnew.VECTOR2I(x1, y1)); t.SetWidth(FromMM(0.127)); t.SetLayer(pcbnew.B_Cu); t.SetNetCode(net); t.SetLocked(True); b.Add(t)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[1]); print("fix_c7_u3: 3 locked B.Cu segments inside the QFN ring, pad 1 to pad 10 of U3, zones refilled")
