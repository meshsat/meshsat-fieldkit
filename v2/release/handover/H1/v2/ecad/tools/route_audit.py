#!/usr/bin/env python3
"""Audit image of a routed (or partly routed) board for the session's own visual check (owner ruling 5 Sep 2026: when a chain stops, the session
screenshots the board, audits it, traces the cause and iterates; no human look). Draws the outline, every pad (grey), every track per copper layer
(one colour per layer), the vias (black rings), the rule areas (hatched outlines) and, from a DRC JSON, every unconnected item as a red cross with
its net name, plus a table of the open nets by count in the title. Usage: route_audit.py <board.kicad_pcb> <out.png> [drc.json] [px per mm]"""
import sys, json, collections, pcbnew
from PIL import Image, ImageDraw
b = pcbnew.LoadBoard(sys.argv[1]); out = sys.argv[2]; drc = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None; ppm = float(sys.argv[4]) if len(sys.argv) > 4 else 6.0
mm = pcbnew.ToMM
bb = b.GetBoardEdgesBoundingBox(); x0, y0, x1, y1 = mm(bb.GetLeft()) - 5, mm(bb.GetTop()) - 5, mm(bb.GetRight()) + 5, mm(bb.GetBottom()) + 5
if len(sys.argv) > 8:   # a region in KiCad mm: x0 y0 x1 y1 (use the board's own coordinates; case frame = KiCad minus the user origin)
    x0, y0, x1, y1 = [float(v) for v in sys.argv[5:9]]
W, H = int((x1 - x0) * ppm), int((y1 - y0) * ppm) + 60
im = Image.new("RGB", (W, H), (250, 250, 248)); d = ImageDraw.Draw(im)
def P(x, y): return ((x - x0) * ppm, (y - y0) * ppm + 60)
LC = {"F.Cu": (200, 30, 30), "B.Cu": (30, 60, 200), "In1.Cu": (200, 160, 0), "In2.Cu": (0, 150, 60), "In3.Cu": (150, 0, 150), "In4.Cu": (0, 150, 150)}
for k in range(0, int(x1 - x0) + 1, 10):
    X = P(x0 + k, 0)[0]; d.line([(X, 60), (X, H)], fill=(225, 225, 225), width=1)
for k in range(0, int(y1 - y0) + 1, 10):
    Y = P(0, y0 + k)[1]; d.line([(0, Y), (W, Y)], fill=(225, 225, 225), width=1)
for dr in b.GetDrawings():
    if dr.GetLayer() == pcbnew.Edge_Cuts and dr.GetClass() == "PCB_SHAPE" and dr.GetShape() == pcbnew.SHAPE_T_SEGMENT:
        d.line([P(mm(dr.GetStart().x), mm(dr.GetStart().y)), P(mm(dr.GetEnd().x), mm(dr.GetEnd().y))], fill=(0, 0, 0), width=2)
for z in b.Zones():
    if not z.GetIsRuleArea(): continue
    o = z.Outline()
    for i in range(o.OutlineCount()):
        pts = [P(mm(o.CVertex(j, i, -1).x), mm(o.CVertex(j, i, -1).y)) for j in range(o.VertexCount(i))]
        if len(pts) > 2: d.line(pts + [pts[0]], fill=(255, 140, 0), width=1)
for f in b.GetFootprints():
    for p in f.Pads():
        bx = p.GetBoundingBox(); d.rectangle([P(mm(bx.GetLeft()), mm(bx.GetTop())), P(mm(bx.GetRight()), mm(bx.GetBottom()))], fill=(190, 190, 190))
def via_w(v):   # KiCad 9 wants a layer for a via's width
    try: return v.GetWidth(pcbnew.F_Cu)
    except TypeError: return v.GetWidth()
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        c = P(mm(t.GetPosition().x), mm(t.GetPosition().y)); r = mm(via_w(t)) / 2 * ppm; d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=(0, 0, 0), width=1)
    elif t.GetClass() == "PCB_TRACK":
        col = LC.get(b.GetLayerName(t.GetLayer()), (100, 100, 100)); d.line([P(mm(t.GetStart().x), mm(t.GetStart().y)), P(mm(t.GetEnd().x), mm(t.GetEnd().y))], fill=col, width=max(1, int(mm(t.GetWidth()) * ppm)))
opens = collections.Counter(); n_unc = 0
if drc:
    dj = json.load(open(drc))
    for u in dj.get("unconnected_items", []):
        n_unc += 1
        for it in u.get("items", [])[:2]:
            pos = it.get("pos", {}); x, y = pos.get("x"), pos.get("y")
            if x is None: continue
            c = P(x, y); d.line([(c[0] - 5, c[1] - 5), (c[0] + 5, c[1] + 5)], fill=(255, 0, 0), width=2); d.line([(c[0] - 5, c[1] + 5), (c[0] + 5, c[1] - 5)], fill=(255, 0, 0), width=2)
        desc = u.get("description", ""); net = desc.split("[")[1].split("]")[0] if "[" in desc else desc[:24]; opens[net] += 1
title = "%s: %d tracks, %d vias, %d unconnected; open nets: %s" % (sys.argv[1].split("/")[-1], sum(1 for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"), sum(1 for t in b.GetTracks() if t.GetClass() == "PCB_VIA"), n_unc, ", ".join("%s x%d" % kv for kv in opens.most_common(12)))
d.text((8, 6), title[:260], fill=(0, 0, 0)); d.text((8, 24), "layers: " + "  ".join(k for k in LC if k in [b.GetLayerName(l) for l in b.GetEnabledLayers().CuStack()]) + "   orange = rule areas, red X = open ends, grid 10 mm", fill=(60, 60, 60))
im.save(out); print("route audit:", out, "unconnected", n_unc, "open nets", len(opens))
