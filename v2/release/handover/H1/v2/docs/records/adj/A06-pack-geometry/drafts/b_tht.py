#!/usr/bin/env python3
"""A06: every footprint (either side) with a through-hole or NPTH pad whose case position lies at X > +118 or X < -118 on the committed B21 board,
plus footprint attributes (dnp, smd/through_hole). THT leads of a top-side part stand out below B's underside; NPTH/mounting holes carry screws."""
import re, sys, math
PATH = sys.argv[1]; OX, OY = 150.0, 110.0
raw = open(PATH, encoding="utf-8").read()
tok_re = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
def parse(s):
    st = [[]]
    for m in tok_re.finditer(s):
        t = m.group(0)
        if t == '(': st.append([])
        elif t == ')': x = st.pop(); st[-1].append(x)
        else: st[-1].append(t[1:-1] if t.startswith('"') else t)
    return st[0][0]
tree = parse(raw)
def kids(n, name): return [c for c in n if isinstance(c, list) and c and c[0] == name]
def kid(n, name):
    k = kids(n, name); return k[0] if k else None
rows = []
for fp in kids(tree, "footprint"):
    layer = kid(fp, "layer")[1]
    at = kid(fp, "at"); fx, fy = float(at[1]), float(at[2]); rot = float(at[3]) if len(at) > 3 else 0.0
    ref = val = ""
    for p in kids(fp, "property"):
        if p[1] == "Reference": ref = p[2]
        if p[1] == "Value": val = p[2]
    attr = kid(fp, "attr"); attrs = attr[1:] if attr else []
    a = math.radians(rot)
    hits = []
    for pd in kids(fp, "pad"):
        typ = pd[2]
        if typ not in ("thru_hole", "np_thru_hole"): continue
        pa = kid(pd, "at"); px, py = float(pa[1]), float(pa[2])
        bx = fx + px * math.cos(a) + py * math.sin(a); by = fy - px * math.sin(a) + py * math.cos(a)
        cx, cy = bx - OX, OY - by
        dr = kid(pd, "drill"); d = [x for x in dr[1:] if not isinstance(x, list)] if dr else []
        if cx > 118 or cx < -118: hits.append((pd[1], typ, round(cx, 2), round(cy, 2), d))
    if hits:
        xs = [h[2] for h in hits]; ys = [h[3] for h in hits]
        rows.append((layer, ref, val[:30], kid(fp, "property") and fp[1][:45], attrs, len(hits), min(xs), max(xs), min(ys), max(ys), hits[0][1], hits[0][4]))
for r in sorted(rows, key=lambda r: (r[6] > 0, r[6])):
    print("%-5s %-10s %-30s %-45s attrs=%s n=%d X %.2f..%.2f Y %.2f..%.2f type=%s drill=%s" % r)
