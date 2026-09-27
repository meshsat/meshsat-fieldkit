#!/usr/bin/env python3
"""Text reader for .kicad_pcb footprints (no pcbnew): prints reference, layer, position in the case frame,
the absolute position of every pad, and matching gr_text phase strings. Usage: fpread.py <board> <OX> <OY> <regex-of-refs>"""
import sys, re, math
path, OX, OY, pat = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), re.compile(sys.argv[4])
s = open(path, encoding="utf-8").read()
def parse(s):
    tok = re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()"]+', s)
    stack = [[]]
    for t in tok:
        if t == "(": stack.append([])
        elif t == ")": x = stack.pop(); stack[-1].append(x)
        else: stack[-1].append(t.strip('"') if t.startswith('"') else t)
    return stack[0][0]
root = parse(s)
def get(node, key): return [c for c in node if isinstance(c, list) and c and c[0] == key]
for fp in get(root, "footprint"):
    ref = None
    for p in get(fp, "property"):
        if p[1] == "Reference": ref = p[2]
    if ref is None:
        for t in get(fp, "fp_text"):
            if t[1] == "reference": ref = t[2]
    if not ref or not pat.fullmatch(ref): continue
    at = get(fp, "at")[0]; x, y = float(at[1]), float(at[2]); rot = float(at[3]) if len(at) > 3 else 0.0
    layer = get(fp, "layer")[0][1]; name = fp[1]
    print("%-10s %-45s %-5s at case (%.3f, %.3f) rot %.1f" % (ref, name, layer, x - OX, OY - y, rot))
    for pd in get(fp, "pad"):
        pat_ = get(pd, "at")[0]; dx, dy = float(pat_[1]), float(pat_[2])
        # KiCad stores pad (at) in footprint frame with the footprint rotation applied as -rot (y down)
        a = math.radians(rot)
        ax = x + dx * math.cos(a) + dy * math.sin(a); ay = y - dx * math.sin(a) + dy * math.cos(a)
        drill = get(pd, "drill"); d = drill[0][1:] if drill else []
        print("    pad %-3s %-12s case (%.3f, %.3f) drill %s" % (pd[1], pd[2], ax - OX, OY - ay, " ".join(str(v) for v in d if not isinstance(v, list))))
if len(sys.argv) > 5:
    for t in get(root, "gr_text"):
        if re.search(sys.argv[5], t[1]): print("gr_text:", t[1][:160])
