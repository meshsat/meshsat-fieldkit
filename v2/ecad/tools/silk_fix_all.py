#!/usr/bin/env python3
"""Legend (PCB_TEXT) corrections on the routed boards, by text content, no re-route. Usage: silk_fix_all.py <board.kicad_pcb> <key>
key: a|b|c|d|e1|e2 (the spacer ring R1 is retired with C5). Rules: ("match", {"text"?, "pos"?, "layer"?, "size"?, "angle"?, "halign"?, "delete"?}); match = prefix of the current text."""
import sys, pcbnew
from pcbnew import VECTOR2I, FromMM
OX, OY = {"c": (297.0, 210.0), "e2": (200.0, 20.0)}.get(sys.argv[2], (150.0, 110.0))
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
F, B = pcbnew.F_SilkS, pcbnew.B_SilkS
RULES = {
 "a": [("MESHSAT FIELD KIT  -  PCB-A POWER", dict(text="MESHSAT FIELD KIT  -  PCB-A POWER + I/O  -  REV A (A18)", pos=(55, 76.5), size=2.2)),
       ("MESHSAT-709  |  285 x 160", dict(text="MESHSAT-709  |  285 x 160 x 1.6 mm FR-4, 4 layers  |  matte black  |  2026-09-04", pos=(55, 73.3), size=1.1)),
       ("BACK WALL (+Y)", dict(pos=(-20, 77.0))),
       ("FRONT WALL (-Y)   v v v   LED row", dict(text="FRONT WALL (-Y)   v v v", pos=(20, -76.0))),
       ("PCB-A UNDERSIDE - sits 2.4 mm", dict(text="PCB-A UNDERSIDE - on 6 mm spacers over the dock strip; spring pins J_DOCK land on PCB-E1", pos=(60, -76.0)))],
 "b": [("J_PANEL ribbon up to PCB-C", dict(pos=(86, 75.5), angle=0)),
       ("PCB-B COMPUTE  REV A (", dict(text="PCB-B COMPUTE  REV A (B12)")),
       ("MESHSAT-709 | 245x170x1.6 4L", dict(text="MESHSAT-709 | 245x170x1.6 4L | matte black | 2026-09-04")),
       ("BACK WALL (+Y)", dict(pos=(-68, 83.0))),
       ("FRONT WALL (-Y)   v v v", dict(pos=(45, -81.5))),
       ("J_RTL1", dict(pos=(-12, 9.5))),
       ("Pi 5 + cooler on 4x M2.5 standoffs", dict(pos=(-69, 40.0), size=0.9)),
       ("B12: no X1202", dict(pos=(-69, -40.0), size=0.9))],
 "c": [("MESHSAT FIELD KIT  -  CONTROL PANEL PCB-C", dict(text="MESHSAT FIELD KIT  -  CONTROL PANEL")),
       ("TD2 7in glass 189.32", dict(layer=B)), ("CONNECTOR END = PORT", dict(layer=B)), ("TAPE", dict(delete=True)),
       ("BACK WALL (+Y)", dict(layer=B, pos=(-160, 139.6))), ("FRONT WALL (-Y)   v v v", dict(layer=B)), ("PORT (-X)", dict(layer=B)), ("STARBOARD (+X)", dict(layer=B)),
       ("PCB-C UNDERSIDE", dict(text="PCB-C UNDERSIDE (REV A, C5, MESHSAT-709, 2026-09-04) - sealed face: plugged vias, gasket band, silicone beads on the LED joints - faces PCB-B - ribbon J_PANEL (SMD), leads J_MAINSW / J_PIJ2 on solder lands"))],
 # the D5-era legend rules (DMR858M on sockets, the D5 stamp) were dropped on 8 Sep 2026: the DMR858M left the device set on 6 September and D8 stamps "PCB-D APRS MEZZANINE", which none of them matched
 "e12": [("MESHSAT PCB-E1 DOCK", dict(size=1.2, pos=(0, -52.3)))],
}
b = pcbnew.LoadBoard(sys.argv[1]); n = 0
for d in list(b.GetDrawings()):
    if not isinstance(d, pcbnew.PCB_TEXT) or d.GetLayer() not in (F, B): continue
    s = d.GetText()
    for match, r in RULES.get(sys.argv[2], []):   # a board with no legend rules left (D since 8 Sep 2026) passes through untouched
        if not s.startswith(match): continue
        if r.get("delete"): b.Remove(d); n += 1; break
        if "text" in r: d.SetText(r["text"])
        if "pos" in r: d.SetPosition(P(*r["pos"]))
        if "shift" in r: p = d.GetPosition(); d.SetPosition(VECTOR2I(p.x + FromMM(r["shift"][0]), p.y - FromMM(r["shift"][1])))
        if "size" in r: d.SetTextSize(VECTOR2I(FromMM(r["size"]), FromMM(r["size"]))); d.SetTextThickness(FromMM(max(0.15, r["size"] * 0.16)))
        if "angle" in r: d.SetTextAngleDegrees(r["angle"])
        if "layer" in r: d.SetLayer(r["layer"]); d.SetMirrored(r["layer"] == B)
        n += 1; break
if sys.argv[2] == "e12":
    for fp in b.GetFootprints():
        if fp.GetReference() == "U2": fp.Reference().SetPosition(P(17.2, -60.6)); n += 1
pcbnew.SaveBoard(sys.argv[1], b); print("%s: %d legend items changed" % (sys.argv[2], n))
