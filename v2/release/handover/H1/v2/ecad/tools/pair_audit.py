#!/usr/bin/env python3
"""Audit image of a differential pair for the session's own visual check (owner ruling 5 Sep 2026: when a chain stops on a pair, the session
screenshots the region, audits it, traces the cause and iterates; no human look). Draws the two legs (P red, N blue), their vias, and every
other copper item in the region (grey), per layer, with a 10 mm grid and the lengths in the title. Usage: pair_audit.py <board> <pair> <out.png> [margin mm]"""
import sys, math, pcbnew
from PIL import Image, ImageDraw
b = pcbnew.LoadBoard(sys.argv[1]); pair = sys.argv[2]; out = sys.argv[3]; margin = float(sys.argv[4]) if len(sys.argv) > 4 else 6.0
mm = pcbnew.ToMM
def net_of(n): return b.GetNetInfo().GetNetItem(n) or b.GetNetInfo().GetNetItem("/" + n)
legs = {"P": net_of(pair + "_P"), "N": net_of(pair + "_N")}
if not all(legs.values()): print("pair_audit: nets not found for", pair); sys.exit(1)
codes = {k: v.GetNetCode() for k, v in legs.items()}
items = [t for t in b.GetTracks() if t.GetNetCode() in codes.values()]
xs = [mm(p.x) for t in items for p in (t.GetStart(), t.GetEnd())]; ys = [mm(p.y) for t in items for p in (t.GetStart(), t.GetEnd())]
x0, x1, y0, y1 = min(xs) - margin, max(xs) + margin, min(ys) - margin, max(ys) + margin
S = min(12.0, 3800 / max(x1 - x0, y1 - y0))            # px per mm
W, H = int((x1 - x0) * S) + 1, int((y1 - y0) * S) + 1
layers = [l for l in b.GetEnabledLayers().CuStack()]
def px(x, y): return ((x - x0) * S, (y - y0) * S)
length = {k: sum(mm(t.GetLength()) for t in items if t.Type() == pcbnew.PCB_TRACE_T and t.GetNetCode() == c) for k, c in codes.items()}
sheets = []
for L in layers:
    im = Image.new("RGB", (W, H), (250, 250, 250)); d = ImageDraw.Draw(im)
    for g in range(int(x0 // 10) * 10, int(x1) + 10, 10): X = px(g, 0)[0]; d.line([(X, 0), (X, H)], fill=(225, 225, 225))
    for g in range(int(y0 // 10) * 10, int(y1) + 10, 10): Y = px(0, g)[1]; d.line([(0, Y), (W, Y)], fill=(225, 225, 225))
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if not (p.IsOnLayer(L) or p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH): continue
            bb = p.GetBoundingBox(); a, c = px(mm(bb.GetX()), mm(bb.GetY())), px(mm(bb.GetRight()), mm(bb.GetBottom()))
            if c[0] < 0 or a[0] > W or c[1] < 0 or a[1] > H: continue
            col = (220, 80, 80) if p.GetNetCode() == codes["P"] else (80, 80, 220) if p.GetNetCode() == codes["N"] else (170, 170, 170)
            d.rectangle([a, c], outline=col, fill=col if col != (170, 170, 170) else (205, 205, 205))
    for t in b.GetTracks():
        col = (220, 40, 40) if t.GetNetCode() == codes["P"] else (40, 40, 220) if t.GetNetCode() == codes["N"] else (150, 150, 150)
        if t.Type() == pcbnew.PCB_VIA_T:
            c = px(mm(t.GetPosition().x), mm(t.GetPosition().y)); r = mm(t.GetWidth(L)) / 2 * S
            if -r < c[0] < W + r and -r < c[1] < H + r: d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=col, width=2)
        elif t.GetLayer() == L:
            a, c = px(mm(t.GetStart().x), mm(t.GetStart().y)), px(mm(t.GetEnd().x), mm(t.GetEnd().y))
            if max(a[0], c[0]) < 0 or min(a[0], c[0]) > W or max(a[1], c[1]) < 0 or min(a[1], c[1]) > H: continue
            d.line([a, c], fill=col, width=max(2, int(mm(t.GetWidth()) * S)))
    for z in b.Zones():
        if z.GetIsRuleArea() and z.IsOnLayer(L):
            bb = z.GetBoundingBox(); a, c = px(mm(bb.GetX()), mm(bb.GetY())), px(mm(bb.GetRight()), mm(bb.GetBottom())); d.rectangle([a, c], outline=(240, 160, 60), width=2)
    d.text((8, 6), "%s on %s   P %.2f mm (red)   N %.2f mm (blue)   mismatch %.2f mm   region x %.0f..%.0f y %.0f..%.0f (KiCad mm), grid 10 mm, orange = track keep-out" % (pair, b.GetLayerName(L), length["P"], length["N"], abs(length["P"] - length["N"]), x0, x1, y0, y1), fill=(0, 0, 0))
    sheets.append(im)
tot = Image.new("RGB", (W, (H + 10) * len(sheets)), (255, 255, 255))
for i, im in enumerate(sheets): tot.paste(im, (0, i * (H + 10)))
tot.save(out); print("pair_audit: %s -> %s (%d x %d, %d layers)" % (pair, out, tot.width, tot.height, len(sheets)))
