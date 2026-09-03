#!/usr/bin/env python3
"""Legend (PCB_TEXT) corrections on the routed boards, by text content, no re-route. Usage: silk_fix_all.py <board.kicad_pcb> <key>
key: a|b|c|d|e1|e2|ring. Rules: ("match", {"text"?, "pos"?, "layer"?, "size"?, "angle"?, "halign"?, "delete"?}); match = prefix of the current text."""
import sys, pcbnew
from pcbnew import VECTOR2I, FromMM
OX, OY = {"c": (297.0, 210.0), "e2": (200.0, 20.0), "ring": (60.0, 30.0)}.get(sys.argv[2], (150.0, 110.0))
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
F, B = pcbnew.F_SilkS, pcbnew.B_SilkS
RULES = {
 "a": [("MESHSAT FIELD KIT  -  PCB-A POWER", dict(text="MESHSAT FIELD KIT  -  PCB-A POWER + I/O  -  REV A (A17)", pos=(55, 76.5), size=2.2)),
       ("MESHSAT-709  |  285 x 160", dict(text="MESHSAT-709  |  285 x 160 x 1.6 mm FR-4, 4 layers  |  matte black  |  2026-09-04", pos=(55, 73.3), size=1.1)),
       ("BACK WALL (+Y)", dict(pos=(-20, 77.0))),
       ("FRONT WALL (-Y)   v v v   LED row", dict(text="FRONT WALL (-Y)   v v v", pos=(20, -76.0))),
       ("PCB-A UNDERSIDE - sits 2.4 mm", dict(text="PCB-A UNDERSIDE - on 6 mm spacers over the dock strip; spring pins J_DOCK land on PCB-E1", pos=(60, -76.0)))],
 "b": [("J_PANEL ribbon up to PCB-C", dict(pos=(86, 75.5), angle=0)),
       ("PCB-B COMPUTE  REV A (", dict(text="PCB-B COMPUTE  REV A (B11)")),
       ("MESHSAT-709 | 245x170x1.6 4L", dict(text="MESHSAT-709 | 245x170x1.6 4L | matte black | 2026-09-04")),
       ("BACK WALL (+Y)", dict(pos=(-68, 83.0))),
       ("FRONT WALL (-Y)   v v v", dict(pos=(45, -81.5))),
       ("J_RTL1", dict(pos=(-12, 9.5)))],
 "c": [("MESHSAT FIELD KIT  -  CONTROL PANEL PCB-C", dict(text="MESHSAT FIELD KIT  -  CONTROL PANEL")),
       ("TD2 7in glass 189.32", dict(layer=B)), ("CONNECTOR END = PORT", dict(layer=B)), ("TAPE", dict(delete=True)),
       ("BACK WALL (+Y)", dict(layer=B, pos=(-160, 139.6))), ("FRONT WALL (-Y)   v v v", dict(layer=B)), ("PORT (-X)", dict(layer=B)), ("STARBOARD (+X)", dict(layer=B)),
       ("PCB-C UNDERSIDE - faces PCB-B", dict(text="PCB-C UNDERSIDE (REV A, C4, MESHSAT-709, 2026-09-03) - faces PCB-B - panel electronics, ribbon J_PANEL, leads J_X1202SW / J_PIJ2"))],
 "d": [("DMR858M 5 W UHF on 2 x 1x12 sockets", dict(text="DMR858M on 2x 1x12 sockets 8.5 mm + M2.5 x 11 standoffs, heatsink up", layer=B, pos=(10, -8.5), size=0.85)),
       ("SMA east -> UHF bulkhead", dict(text="SMA east -> UHF bulkhead | USB-C west (unplug the module to configure) | pin 1 = VCC (NE)", layer=B, pos=(10, -11.5), size=0.8)),
       ("rows and holes per NiceRF", dict(text="rows and holes per NiceRF datasheet V1.2 p.10", layer=B, pos=(10, -14.5), size=0.8)),
       ("J_HARN1 to PCB-A J_MEZZ1", dict(shift=(2.0, -4.0))),
       ("J_PWR1 CELL+ GND", dict(text="J_PWR1 MEZZ_CELL GND")),
       ("PCB-D APRS BOARD REV A", dict(text="PCB-D APRS BOARD REV A (D5) | MESHSAT-709/748 | 2026-09-03"))],
 "e1": [("MESHSAT PCB-E1 DOCK", dict(text="MESHSAT PCB-E1 DOCK  -  shore 9-36 V -> 12 V 40 W -> PCB-A spring pins  -  rods through H1/H2", pos=(0, -52.7), size=1.4)),
        ("DC IN +/-  (IP68 bulkhead lead)", dict(text="DC IN +/- (IP68 bulkhead lead)  |  F1 7.5 A mini blade  |  reverse polarity + 33 V TVS  |  opto inhibit on pin 8  |  VHB pads to the floor", pos=(0, -93.3), size=1.3)),
        ("F1 5A", dict(text="F1 7.5A"))],
 "e2": [("SMA F-F", dict(delete=True)),
        ("MESHSAT PCB-E2 RF JUNCTION", dict(text="MESHSAT PCB-E2 RF JUNCTION  -  device pigtails above, wall pigtails below  -  RF HAZARD DURING TX", pos=(0, 9.5), size=1.4))],
 "ring": [("MESHSAT PCB-C RING", dict(text="RING 1.0", pos=(-50.2, 0), angle=90, size=1.0))],
 "a2": [("MESHSAT FIELD KIT  -  PCB-A POWER", dict(pos=(48, 76.5))),
        ("MESHSAT-709  |  285 x 160", dict(pos=(48, 73.3))),
        ("PCB-A UNDERSIDE - on 6 mm spacers", dict(text="PCB-A UNDERSIDE - 6 mm spacers on the dock strip; J_DOCK pins land on PCB-E1", pos=(45, -76.0))),
        ("WELDED PACK 1S8P", dict(text="WELDED PACK 1S8P (8x Samsung 35E, 130 x 74 x 18.5) -> J_PACK XT60 -> F1 -> J_X1202BAT lead; strap through the slots", pos=(-95, 46.5)))],
 "b2": [("BACK WALL (+Y)", dict(pos=(-10, 83.0))), ("FRONT WALL (-Y)   v v v", dict(pos=(-100, -83.2)))],
 "c2": [("MESHSAT FIELD KIT   P/N MS709-C", dict(text="MESHSAT FIELD KIT   P/N MS709-C   REV A")), ("FRONT WALL (-Y)   v v v", dict(pos=(-150, -140.6)))],
 "d2": [("DMR858M on 2x 1x12 sockets", dict(text="DMR858M on 2x 1x12 sockets + M2.5 x 11 standoffs, heatsink up", size=0.75)),
        ("SMA east -> UHF bulkhead", dict(text="SMA east -> UHF bulkhead | USB-C west | pin 1 = VCC (NE)", size=0.75)),
        ("rows and holes per NiceRF", dict(size=0.75)),
        ("J_PWR1 MEZZ_CELL GND", dict(shift=(0.0, 13.0)))],
 "e12": [("MESHSAT PCB-E1 DOCK", dict(size=1.2, pos=(0, -52.3)))],
}
b = pcbnew.LoadBoard(sys.argv[1]); n = 0
for d in list(b.GetDrawings()):
    if not isinstance(d, pcbnew.PCB_TEXT) or d.GetLayer() not in (F, B): continue
    s = d.GetText()
    for match, r in RULES[sys.argv[2]]:
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
