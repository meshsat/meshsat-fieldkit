#!/usr/bin/env python3
"""Stdlib STEP (AP214) face reader for the Peli 1450 bodies (MESHSAT-1357, case margins). For every ADVANCED_FACE it prints the
surface type, the plane normal (planes), the radius (cylinders, cones) and the bounding box of the face's vertices, converted to mm
(the Peli files declare CONVERSION_BASED_UNIT 'INCH', 0.0254 m). No OCC on the runner or the box, so no B-rep evaluation: a face's
extent is the box of its edge vertices, which is exact for planar faces bounded by lines and a lower bound where an edge is a spline.
Usage: step_faces.py FILE.STEP [scale]"""
import re, sys, math
path = sys.argv[1]; S = float(sys.argv[2]) if len(sys.argv) > 2 else 25.4
txt = open(path, encoding="latin-1").read()
data = txt[txt.index("DATA;") + 5:txt.rindex("ENDSEC;")]
ent = {}
for m in re.finditer(r"#(\d+)\s*=\s*(.*?);\s*(?=#\d+\s*=|$)", data, re.S):
    ent[int(m.group(1))] = " ".join(m.group(2).split())
def typ(i): s = ent[i]; return s[:s.index("(")].strip() if not s.startswith("(") else "COMPLEX"
def refs(s): return [int(x) for x in re.findall(r"#(\d+)", s)]
def nums(s): return [float(x) for x in re.findall(r"[-+]?\d*\.\d+(?:[Ee][-+]?\d+)?|[-+]?\d+(?:[Ee][-+]?\d+)?", s)]
def point(i):
    s = ent[i]; inner = s[s.index("(", s.index("(") + 1):]
    return tuple(v * S for v in nums(inner)[:3])
def direction(i):
    s = ent[i]; inner = s[s.index("(", s.index("(") + 1):]
    return tuple(nums(inner)[:3])
def vpt(i): return point(refs(ent[i])[0])
def face_vertices(fi):
    s = ent[fi]; out = []
    for b in refs(s)[:-1]:
        if typ(b) not in ("FACE_OUTER_BOUND", "FACE_BOUND"): continue
        loop = refs(ent[b])[0]
        for oe in refs(ent[loop]):
            ec = refs(ent[oe])[-1]
            r = refs(ent[ec])
            out += [vpt(r[0]), vpt(r[1])]
            cur = r[2]
            if typ(cur) == "B_SPLINE_CURVE_WITH_KNOTS":
                out += [point(p) for p in refs(ent[cur]) if typ(p) == "CARTESIAN_POINT"]
    return out
rows = []
for i in sorted(ent):
    if typ(i) != "ADVANCED_FACE": continue
    r = refs(ent[i]); surf = r[-1]; st = typ(surf); info = ""
    if st in ("PLANE", "CYLINDRICAL_SURFACE", "CONICAL_SURFACE", "SPHERICAL_SURFACE"):
        ax = refs(ent[surf])[0]; a = refs(ent[ax]); loc = point(a[0]); n = direction(a[1])
        extra = nums(ent[surf].split(",", 2)[-1]) if st != "PLANE" else []
        info = "loc (%.2f, %.2f, %.2f) axis (%.4f, %.4f, %.4f)%s" % (loc + n + ((" r %.2f" % (extra[0] * S)) if extra else "",))
        if st == "CONICAL_SURFACE" and len(extra) > 1: info += " half-angle %.4f" % extra[1]
    v = face_vertices(i)
    if not v: continue
    bb = [(min(p[k] for p in v), max(p[k] for p in v)) for k in range(3)]
    rows.append((i, st, info, bb))
for i, st, info, bb in rows:
    print("#%-6d %-26s x %8.2f..%8.2f  y %8.2f..%8.2f  z %8.2f..%8.2f  %s" % (i, st, bb[0][0], bb[0][1], bb[1][0], bb[1][1], bb[2][0], bb[2][1], info))
