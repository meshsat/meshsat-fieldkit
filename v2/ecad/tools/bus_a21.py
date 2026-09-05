#!/usr/bin/env python3
"""A21 (5 Sep 2026): the BOOST_EN enable line of the three TPS61288L converters is laid by hand after the escapes, as a locked 0.25 mm In1 bus south of the
converter row that joins the three pin-6 escape vias. Runs 13 and 17 left that link open: between U23 and U24 every layer but In1 is walled by the
boost 3 feed columns and their keep-outs, and Freerouting did not find the In1 path. Usage: bus_a21.py <board.kicad_pcb>"""
import sys, pcbnew
FromMM = pcbnew.FromMM
b = pcbnew.LoadBoard(sys.argv[1])
vias = sorted([t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname().lstrip("/") == "BOOST_EN" and 125e6 < t.GetPosition().y < 132e6], key=lambda t: t.GetPosition().x)
if len(vias) != 3: print("bus_a21: expected the three BOOST_EN escape vias, found", len(vias)); sys.exit(1)
net = vias[0].GetNet()
obstacles = [(t.GetPosition(), t.GetWidth() / 2 if t.Type() == pcbnew.PCB_VIA_T else 0) for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetcode() != net.GetNetCode()]
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) and p.GetNetcode() != net.GetNetCode(): obstacles.append((p.GetPosition(), max(p.GetSizeX(), p.GetSizeY()) / 2))
def clear(x0, y0, x1, y1, w=FromMM(0.25), clr=FromMM(0.2)):
    """no foreign via or through pad within clearance of the axis-parallel segment"""
    xa, xb = min(x0, x1) - w // 2 - clr, max(x0, x1) + w // 2 + clr; ya, yb = min(y0, y1) - w // 2 - clr, max(y0, y1) + w // 2 + clr
    return not any(xa - r < c.x < xb + r and ya - r < c.y < yb + r for c, r in obstacles)
def track(x0, y0, x1, y1):
    t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(int(x0), int(y0))); t.SetEnd(pcbnew.VECTOR2I(int(x1), int(y1))); t.SetWidth(FromMM(0.25)); t.SetLayer(pcbnew.In1_Cu); t.SetNet(net); t.SetLocked(True); b.Add(t)
dx = FromMM(0.9)
for ybus in (FromMM(y) for y in (133.0, 133.5, 132.6, 134.0, 134.6, 135.2)):
    xs = [v.GetPosition().x + dx for v in vias]
    ok = clear(xs[0], ybus, xs[-1], ybus) and all(clear(v.GetPosition().x, v.GetPosition().y, x, v.GetPosition().y) and clear(x, v.GetPosition().y, x, ybus) for v, x in zip(vias, xs))
    if ok:
        for v, x in zip(vias, xs):
            p = v.GetPosition(); track(p.x, p.y, x, p.y); track(x, p.y, x, ybus)
        track(xs[0], ybus, xs[-1], ybus); pcbnew.SaveBoard(sys.argv[1], b)
        print("bus_a21: BOOST_EN bus on In1 at y %.1f mm from x %.2f to %.2f, locked" % (ybus / 1e6, xs[0] / 1e6, xs[-1] / 1e6)); sys.exit(0)
print("bus_a21: no clean row for the BOOST_EN bus"); sys.exit(1)
