#!/usr/bin/env python3
"""List footprints on a given side inside a case-frame window, with their footprint names (text parse, no pcbnew).
Usage: underside.py <board> <OX> <OY> <layer F.Cu|B.Cu> <x0> <y0> <x1> <y1>"""
import sys, re, collections
path, OX, OY, LAY = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
x0, y0, x1, y1 = map(float, sys.argv[5:9])
s = open(path, encoding="utf-8").read()
tok = re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()"]+', s)
stack = [[]]
for t in tok:
    if t == "(": stack.append([])
    elif t == ")": x = stack.pop(); stack[-1].append(x)
    else: stack[-1].append(t.strip('"') if t.startswith('"') else t)
root = stack[0][0]
def get(n, k): return [c for c in n if isinstance(c, list) and c and c[0] == k]
names = collections.Counter(); rows = []
for fp in get(root, "footprint"):
    lay = get(fp, "layer")[0][1]
    if lay != LAY: continue
    at = get(fp, "at")[0]; cx, cy = float(at[1]) - OX, OY - float(at[2])
    if not (x0 <= cx <= x1 and y0 <= cy <= y1): continue
    ref = next((p[2] for p in get(fp, "property") if p[1] == "Reference"), "?")
    rows.append((ref, fp[1], cx, cy)); names[fp[1].split(":")[-1]] += 1
for n, c in names.most_common(): print("%4d  %s" % (c, n))
for r in sorted(rows, key=lambda r: r[1]):
    if not re.search(r"^(Capacitor|Resistor)|_0402|_0201|_0603", r[1]): print("   %-10s %-50s (%.1f, %.1f)" % r)
