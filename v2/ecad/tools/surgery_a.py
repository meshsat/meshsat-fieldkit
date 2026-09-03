#!/usr/bin/env python3
"""Graft the 19.8 gate items 2 and 7 onto the routed A5 board without re-routing it:
U1 pin 2 -> net CHG_PSEL (re-net its existing GND fanout stub + via), U1 pin 12 -> net CHG_QON; R45 (0R to GND) and R46 (DNP, to REGN) on B.Cu next to that via;
TP11 (CHG_QON) on B.Cu near pin 12. The short links are closed afterwards by stub_router / gap_closer (DRC-gated).
Usage: surgery_a.py <board> <netlist.net>"""
import sys, math, re, pcbnew
from pcbnew import VECTOR2I, FromMM
BOARD, NET = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(BOARD); fps = {f.GetReference(): f for f in b.GetFootprints()}
LIBS = "/usr/share/kicad/footprints/"
PRELOADED = {("Resistor_SMD", "R_0603_1608Metric", 0): pcbnew.FootprintLoad(LIBS + "Resistor_SMD.pretty", "R_0603_1608Metric"),
             ("Resistor_SMD", "R_0603_1608Metric", 1): pcbnew.FootprintLoad(LIBS + "Resistor_SMD.pretty", "R_0603_1608Metric"),
             ("TestPoint", "TestPoint_Pad_D1.5mm", 0): pcbnew.FootprintLoad(LIBS + "TestPoint.pretty", "TestPoint_Pad_D1.5mm")}
print("footprints preloaded:", all(v is not None for v in PRELOADED.values()))
def net_for(name):
    n = b.FindNet(name)
    if n is None or n.GetNetCode() <= 0: n = pcbnew.NETINFO_ITEM(b, name); b.Add(n)
    return n
u1 = fps["U1"]; p2 = next(p for p in u1.Pads() if p.GetNumber() == "2"); p12 = next(p for p in u1.Pads() if p.GetNumber() == "12")
psel, qon = net_for("/CHG_PSEL"), net_for("/CHG_QON")
p2.SetNet(psel); p12.SetNet(qon)
# delete the GND fanout stub hanging off pad 2 (and its via if nothing else uses it): the lane is then free for CHG_PSEL.
# Phase 1 collects (positions copied by value), phase 2 removes: a SWIG proxy read after Remove() is garbage.
p2pos = VECTOR2I(p2.GetPosition().x, p2.GetPosition().y)
def same(a, c): return abs(a.x - c.x) < 2000 and abs(a.y - c.y) < 2000
tracks = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK" and t.GetNetname() == "GND"]
vias = [v for v in b.GetTracks() if v.GetClass() == "PCB_VIA" and v.GetNetname() == "GND"]
gpads = [p for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() == "GND" and not (f.GetReference() == "U1" and p.GetNumber() == "2")]
kill = []; frontier = [t for t in tracks if p2.HitTest(t.GetStart()) or p2.HitTest(t.GetEnd())]
via_pos = None
def degree(pt, excluding):
    n = 0
    for u in tracks:
        if u in excluding: continue
        if same(u.GetStart(), pt) or same(u.GetEnd(), pt): n += 1
    return n
while frontier:
    t = frontier.pop(); 
    if t in kill: continue
    kill.append(t)
    for end in (VECTOR2I(t.GetStart().x, t.GetStart().y), VECTOR2I(t.GetEnd().x, t.GetEnd().y)):
        if p2.HitTest(end): continue
        v_here = [v for v in vias if same(v.GetPosition(), end)]; pad_here = any(p.HitTest(end) for p in gpads)
        if v_here:
            via_pos = VECTOR2I(end.x, end.y)
            if degree(end, kill) == 0 and v_here[0] not in kill: kill.append(v_here[0])   # via only served this chain
            continue
        if pad_here: continue
        nxt = [u for u in tracks if u not in kill and (same(u.GetStart(), end) or same(u.GetEnd(), end))]
        if len(nxt) == 1: frontier.append(nxt[0])          # plain continuation: keep walking; a junction (>= 2) is where the real GND net begins
removed = len(kill)
for it in kill: b.Remove(it)
print("pad 2 GND stub removed: %d items; anchor" % removed, None if via_pos is None else (via_pos.x / 1e6 - 150, 110 - via_pos.y / 1e6))
# SWIG proxies obtained before Remove() are dead: re-acquire everything from the board
fps = {f.GetReference(): f for f in b.GetFootprints()}; u1 = fps["U1"]
p2 = next(p for p in u1.Pads() if p.GetNumber() == "2"); p12 = next(p for p in u1.Pads() if p.GetNumber() == "12")
p2.SetNet(psel); p12.SetNet(qon)
if via_pos is None: via_pos = p2pos
p12pos = VECTOR2I(p12.GetPosition().x, p12.GetPosition().y)
if via_pos is None: via_pos = p2.GetPosition()
# obstacle test on B.Cu for a new footprint bbox (tracks/vias/pads/courtyards of other items), 0.3 mm margin
def clear_bbox(x0, y0, x1, y1):
    m = FromMM(0.3)
    for f in b.GetFootprints():
        for p in f.Pads():
            if not (p.IsOnLayer(pcbnew.B_Cu) or p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)): continue
            bb = p.GetBoundingBox()
            if not (bb.GetRight() + m < x0 or bb.GetLeft() - m > x1 or bb.GetBottom() + m < y0 or bb.GetTop() - m > y1): return False
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA" or t.GetLayer() == pcbnew.B_Cu:
            bb = t.GetBoundingBox()
            if not (bb.GetRight() + m < x0 or bb.GetLeft() - m > x1 or bb.GetBottom() + m < y0 or bb.GetTop() - m > y1): return False
    for z in b.Zones():
        if z.GetIsRuleArea() and z.Outline().Contains(VECTOR2I(int((x0 + x1) / 2), int((y0 + y1) / 2))): return False
    eb = b.GetBoardEdgesBoundingBox()
    if x0 < eb.GetLeft() + FromMM(1.5) or x1 > eb.GetRight() - FromMM(1.5) or y0 < eb.GetTop() + FromMM(1.5) or y1 > eb.GetBottom() - FromMM(1.5): return False
    return True
def place_back(ref, lib, name, value, near, w, h, nets, rot=0):
    fp = PRELOADED.pop((lib, name, 0), None) or PRELOADED.pop((lib, name, 1), None); fp.SetReference(ref); fp.SetValue(value)
    hw, hh = FromMM(w / 2), FromMM(h / 2)
    for r_mm in (1.8, 2.6, 3.4, 4.2, 5.0, 6.0, 7.0, 8.0):
        for k in range(16):
            a = 2 * math.pi * k / 16; cx, cy = int(near.x + FromMM(r_mm) * math.cos(a)), int(near.y + FromMM(r_mm) * math.sin(a))
            if clear_bbox(cx - hw, cy - hh, cx + hw, cy + hh):
                fp.SetPosition(VECTOR2I(cx, cy)); b.Add(fp); fp.Flip(VECTOR2I(cx, cy), False); fp.SetOrientationDegrees(rot)
                for num, net in nets.items():
                    for p in fp.Pads():
                        if p.GetNumber() == num: p.SetNet(net_for(net))
                print("  %s placed on B.Cu at (%.2f, %.2f)" % (ref, cx / 1e6 - 150, 110 - cy / 1e6)); return fp
    print("  NO ROOM for", ref); return None
r45 = place_back("R45", "Resistor_SMD", "R_0603_1608Metric", "0R (fitted: PSEL low = 2.4 A adapter limit)", via_pos, 2.6, 1.6, {"1": "/CHG_PSEL", "2": "GND"})
r46 = place_back("R46", "Resistor_SMD", "R_0603_1608Metric", "DNP 0R (PSEL high = 500 mA USB limit)", via_pos, 2.6, 1.6, {"1": "/CHG_PSEL", "2": "/REGN"})
tp = place_back("TP11", "TestPoint", "TestPoint_Pad_D1.5mm", "CHG_QON", p12pos, 2.6, 2.6, {"1": "/CHG_QON"})
# NTC value from the netlist
s = open(NET).read(); m = re.search(r'\(comp \(ref "NTC1"\)\s*\(value "([^"]+)"', s)
ntc = next((f for f in b.GetFootprints() if f.GetReference() == "NTC1"), None)
if m and ntc is not None: ntc.SetValue(m.group(1)); print("  NTC1 value:", m.group(1)[:50])
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(BOARD, b); print("surgery saved")
