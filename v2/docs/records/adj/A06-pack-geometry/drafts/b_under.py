#!/usr/bin/env python3
"""A06: list every footprint on the B.Cu side of the committed B21 board (and any F.Cu part whose courtyard crosses the pocket X ranges, for context),
in the case frame (case x = board X - 150, case y = 110 - board Y; gen_pcb_b.py:24-25), with courtyard bbox and 3D model refs. Plain text parse, no pcbnew."""
import re, sys, json, math, hashlib
PATH = sys.argv[1]
OX, OY = 150.0, 110.0
raw = open(PATH, encoding="utf-8").read()
print("sha256", hashlib.sha256(raw.encode()).hexdigest()[:16], file=sys.stderr)
tok_re = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
def parse(s):
    stack = [[]]
    for m in tok_re.finditer(s):
        t = m.group(0)
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop(); stack[-1].append(x)
        else:
            stack[-1].append(t[1:-1] if t.startswith('"') else t)
    return stack[0][0]
tree = parse(raw)
def kids(n, name): return [c for c in n if isinstance(c, list) and c and c[0] == name]
def kid(n, name):
    k = kids(n, name); return k[0] if k else None
out = []
edge = []
for fp in kids(tree, "footprint"):
    lib = fp[1]
    layer = kid(fp, "layer")[1]
    at = kid(fp, "at"); fx, fy = float(at[1]), float(at[2]); rot = float(at[3]) if len(at) > 3 else 0.0
    ref = val = ""
    for p in kids(fp, "property"):
        if p[1] == "Reference": ref = p[2]
        if p[1] == "Value": val = p[2]
    # courtyard: collect points of graphics on *.CrtYd, in footprint-local coords, then transform
    pts = []
    for g in fp:
        if not (isinstance(g, list) and g and g[0] in ("fp_line", "fp_rect", "fp_poly", "fp_circle", "fp_arc")): continue
        L = kid(g, "layer")
        if not L or "CrtYd" not in L[1]: continue
        if g[0] in ("fp_line", "fp_rect", "fp_arc"):
            for k in ("start", "end", "mid"):
                q = kid(g, k)
                if q: pts.append((float(q[1]), float(q[2])))
        elif g[0] == "fp_circle":
            c = kid(g, "center"); e = kid(g, "end"); cx, cy = float(c[1]), float(c[2]); r = math.hypot(float(e[1]) - cx, float(e[2]) - cy)
            pts += [(cx - r, cy - r), (cx + r, cy + r), (cx - r, cy + r), (cx + r, cy - r)]
        elif g[0] == "fp_poly":
            for xy in kids(kid(g, "pts"), "xy"): pts.append((float(xy[1]), float(xy[2])))
    # KiCad: board = at + R(-rot) * local (local already mirrored in file for flipped parts)
    a = math.radians(rot)
    def tr(px, py):
        return (fx + px * math.cos(a) + py * math.sin(a), fy - px * math.sin(a) + py * math.cos(a))
    bpts = [tr(*p) for p in pts]
    if bpts:
        xs = [p[0] for p in bpts]; ys = [p[1] for p in bpts]
        cx0, cx1 = min(xs) - OX, max(xs) - OX; cy0, cy1 = OY - max(ys), OY - min(ys)
    else:
        # pads bbox fallback
        cx0 = cx1 = fx - OX; cy0 = cy1 = OY - fy
    models = []
    for m in kids(fp, "model"):
        off = kid(m, "offset"); sc = kid(m, "scale"); rt = kid(m, "rotate")
        def xyz(n): 
            if not n: return None
            q = kid(n, "xyz"); return [float(q[1]), float(q[2]), float(q[3])]
        hide = any(isinstance(c, list) and c and c[0] == "hide" and c[1:] == ["yes"] for c in m) or "hide" in m
        models.append({"path": m[1], "offset": xyz(off), "scale": xyz(sc), "rotate": xyz(rt), "hide": hide})
    out.append({"ref": ref, "value": val, "lib": lib, "layer": layer, "at_case": [round(fx - OX, 3), round(OY - fy, 3), rot],
                "crtyd_case": [round(cx0, 3), round(cy0, 3), round(cx1, 3), round(cy1, 3)], "crtyd_pts": len(pts), "models": models})
json.dump(out, open(sys.argv[2], "w"), indent=1)
sel = [o for o in out if (o["crtyd_case"][2] > 118 or o["crtyd_case"][0] < -118)]
print("footprints", len(out), "B.Cu", sum(o["layer"] == "B.Cu" for o in out), "over X>118 or X<-118 (either side)", len(sel))
for o in sorted(sel, key=lambda o: (o["layer"], o["at_case"][0])):
    if o["layer"] != "B.Cu": continue
    c = o["crtyd_case"]
    print("%-6s %-10s %-22s %-40s at(%.2f,%.2f,r%.0f) crtyd X %.2f..%.2f Y %.2f..%.2f  models=%s" % (o["layer"], o["ref"], o["value"][:22], o["lib"][:40], *o["at_case"], c[0], c[2], c[1], c[3],
          ";".join(m["path"].split("/")[-1] + ("[H]" if m["hide"] else "") for m in o["models"])))
