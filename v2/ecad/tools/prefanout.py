#!/usr/bin/env python3
"""Before autorouting: give every SMD pad on a plane net (GND, +5V) a fanout via + stub so the inner planes reach it.
Usage: prefanout.py <board.kicad_pcb>"""
import sys, math, pcbnew
from pcbnew import VECTOR2I, FromMM
b = pcbnew.LoadBoard(sys.argv[1])
PLANES = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else {"GND", "+5V"}
SKIP = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else set()   # footprints whose plane pads are handled elsewhere ("fine" = every fine-pitch part, see escape.py)
import re as _re
def is_fine(fp):
    if _re.search(r"SOT-23-[68]", fp.GetFPIDAsString()): return True
    pads = [p.GetPosition() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    best = 1e9
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = math.hypot(pads[i].x - pads[j].x, pads[i].y - pads[j].y)
            if 0 < d < best: best = d
    return best <= FromMM(0.7)
VIA_D, VIA_DRILL, TRACK_W = FromMM(0.8), FromMM(0.4), FromMM(0.4)
allpads = [(p, p.GetPosition(), max(p.GetSize().x, p.GetSize().y) / 2) for fp in b.GetFootprints() for p in fp.Pads()]
rule_areas = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()] + [z for fp in b.GetFootprints() for z in fp.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]   # A19: inner-layer track bans allow vias and must not block escapes or fanout; B13: footprint keep-outs (the E72 antenna) count too
edges = b.GetBoardEdgesBoundingBox()
placed = [t.GetPosition() for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]; placed_nets = []   # escapes already on the board count as placed vias
def clear(v, me, r=None):
    r = VIA_D / 2 if r is None else r
    mp = me.GetPosition()
    if not (edges.GetLeft() + FromMM(1.5) < v.x < edges.GetRight() - FromMM(1.5) and edges.GetTop() + FromMM(1.5) < v.y < edges.GetBottom() - FromMM(1.5)): return False
    for q, qp, qr in allpads:
        if qp.x == mp.x and qp.y == mp.y: continue            # the pad itself (wrapper objects differ, compare by position)
        gap = FromMM(0.45) if q.GetNetname() == me.GetNetname() else FromMM(0.75)   # keep other-net pads' exit lanes open for the router
        if math.hypot(v.x - qp.x, v.y - qp.y) < qr + r + gap: return False
    for w in placed:
        if math.hypot(v.x - w.x, v.y - w.y) < VIA_D + FromMM(0.5): return False
    for z in rule_areas:
        o = z.Outline()
        for ddx, ddy in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r)):
            if o.Contains(VECTOR2I(int(v.x + ddx * 1.3), int(v.y + ddy * 1.3))): return False
    return True
added = skipped = 0
for fp in b.GetFootprints():
    if fp.GetReference() in SKIP or ("fine" in SKIP and is_fine(fp)): continue
    fc = fp.GetPosition()
    for pad in fp.Pads():
        if pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or pad.GetNetname() not in PLANES: continue
        c = pad.GetPosition(); half = max(pad.GetSize().x, pad.GetSize().y) / 2
        TRACK_W = min(FromMM(0.4), max(FromMM(0.2), min(pad.GetSize().x, pad.GetSize().y)))   # never wider than the pad: fine-pitch neighbours keep a legal corridor
        dx, dy = c.x - fc.x, c.y - fc.y; n = math.hypot(dx, dy)
        u = (dx / n, dy / n) if n > FromMM(0.3) else (1.0, 0.0)
        sx, sy = pad.GetSize().x, pad.GetSize().y
        if max(sx, sy) > 1.4 * min(sx, sy):                       # elongated IC pad: leave along its long axis, away from the body
            th = math.radians(pad.GetOrientationDegrees())
            L = (math.cos(th), -math.sin(th)) if sx >= sy else (math.sin(th), math.cos(th))
            if L[0] * u[0] + L[1] * u[1] < 0: L = (-L[0], -L[1])
            u = L
        s2 = math.sqrt(0.5)
        dirs = [u, (-u[1], u[0]), (u[1], -u[0]), (-u[0], -u[1])]
        done = False
        for off in (half + FromMM(0.65), half + FromMM(1.1), half + FromMM(1.6)):
            for ux, uy in dirs:
                v = VECTOR2I(int(c.x + ux * off), int(c.y + uy * off))
                mid = VECTOR2I(int((c.x + v.x) / 2), int((c.y + v.y) / 2)); q3 = VECTOR2I(int((c.x + 3 * v.x) / 4), int((c.y + 3 * v.y) / 4))
                if clear(v, pad) and clear(mid, pad, TRACK_W / 2) and clear(q3, pad, TRACK_W / 2):
                    layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
                    via = pcbnew.PCB_VIA(b); via.SetPosition(v); via.SetDrill(VIA_DRILL); via.SetWidth(VIA_D); via.SetViaType(pcbnew.VIATYPE_THROUGH)
                    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(pad.GetNet()); b.Add(via)
                    t = pcbnew.PCB_TRACK(b); t.SetStart(c); t.SetEnd(v); t.SetWidth(TRACK_W); t.SetLayer(layer); t.SetNet(pad.GetNet()); b.Add(t)
                    placed.append(v); placed_nets.append((v, pad.GetNetname())); added += 1; done = True; break
            if done: break
        if not done: skipped += 1; print("  no room for a fanout via at %s pad %s (%s)" % (fp.GetReference(), pad.GetNumber(), pad.GetNetname()))
print("fanout: %d vias added, %d pads skipped" % (added, skipped))
pcbnew.SaveBoard(sys.argv[1], b)
