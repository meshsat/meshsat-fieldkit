#!/usr/bin/env python3
"""Stdlib DXF reader for the Peli 1451-931 customer drawing (MESHSAT-1357, case margins). The drawing is at 1:3 on the sheet
($DIMLFAC 3.0 in its header; the 411 dimension spans 137.16 sheet units). Prints the HATCH boundary polylines (the cut walls of
sections A-A and B-B) and the LINE/ARC/SPLINE geometry crossing a chosen height band, converted to case millimetres with the
section's own datum: B-B has the cavity floor at sheet y 95.295 (the 109 dimension, _D_7) and the case centre at sheet x 169.114
(the 371/375 dimensions, _D_4/_D_5). Usage: dxf_read.py DXF, or dxf_read.py DXF --backwall for the back wall's outside
(added 26 Sep 2026 for the connector plate): the top view's hinge fairings, the section A-A cut line and its back-wall
boundary, and the end view's back features, each by its index in the ENTITIES section (the numbers the document cites)."""
import sys, math, collections
f = open(sys.argv[1], encoding="latin-1").read().splitlines()
pairs = [(f[i].strip(), f[i + 1].rstrip()) for i in range(0, len(f) - 1, 2)]
ents = []; cur = None; in_blocks = False; sec = None
for k, v in pairs:
    if k == "0":
        if cur: ents.append(cur)
        cur = {"type": v.strip(), "g": [], "sec": sec}
    elif cur is not None:
        cur["g"].append((k, v.strip()))
        if cur["type"] == "SECTION" and k == "2": sec = v.strip()
ents.append(cur)
ents = [e for e in ents if e["sec"] == "ENTITIES"]
S = 3.0
def hatch_paths(e):
    g = e["g"]; paths = []; i = 0; pts = []
    xs = [float(v) for k, v in g if k == "10"]; ys = [float(v) for k, v in g if k == "20"]
    return list(zip(xs, ys))
out = collections.OrderedDict()
for n, e in enumerate(ents):
    if e["type"] == "HATCH":
        pts = hatch_paths(e)
        if not pts: continue
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        print("HATCH %d: %d points, sheet x %.3f..%.3f y %.3f..%.3f" % (n, len(pts), min(xs), max(xs), min(ys), max(ys)))

def hatch_edges(e):
    """Parse a HATCH's boundary edges (line, arc, spline control polygon) into case-mm segments for the B-B datum."""
    g = e["g"]; i = 0; segs = []
    while i < len(g) and g[i][0] != "91": i += 1
    npaths = int(g[i][1]); i += 1
    for _ in range(npaths):
        while g[i][0] != "92": i += 1
        flag = int(g[i][1]); i += 1
        if flag & 2:
            while g[i][0] != "93": i += 1
            nv = int(g[i][1]); i += 1; pts = []
            while len(pts) < nv or pts[-1][1] is None:
                if g[i][0] == "10": pts.append([float(g[i][1]), None])
                elif g[i][0] == "20": pts[-1][1] = float(g[i][1])
                i += 1
            segs += [("L", pts[j], pts[(j + 1) % nv]) for j in range(nv)]
            continue
        while g[i][0] != "93": i += 1
        ne = int(g[i][1]); i += 1
        for _ in range(ne):
            while g[i][0] != "72": i += 1
            et = int(g[i][1]); i += 1
            if et == 1:
                v = {}
                while len(v) < 4:
                    if g[i][0] in ("10", "20", "11", "21"): v[g[i][0]] = float(g[i][1])
                    i += 1
                segs.append(("L", (v["10"], v["20"]), (v["11"], v["21"])))
            elif et == 2:
                v = {}
                while len(v) < 5:
                    if g[i][0] in ("10", "20", "40", "50", "51"): v[g[i][0]] = float(g[i][1])
                    i += 1
                segs.append(("A", (v["10"], v["20"]), v["40"], v["50"], v["51"]))
            elif et == 4:
                while g[i][0] != "96": i += 1
                ncp = int(g[i][1]); i += 1; cps = []
                while len(cps) < ncp or cps[-1][1] is None:
                    if g[i][0] == "10": cps.append([float(g[i][1]), None])
                    elif g[i][0] == "20": cps[-1][1] = float(g[i][1])
                    i += 1
                segs += [("L", cps[j], cps[j + 1]) for j in range(ncp - 1)]
            else:
                segs.append(("?", et))
    return segs

X0, Y0 = 169.114, 95.295
def case(p): return ((p[0] - X0) * S, (p[1] - Y0) * S)
def crossings(segs, zc):
    """X positions (case mm) where the hatch boundary crosses height zc (case mm above the cavity floor)."""
    xs = []
    for s in segs:
        if s[0] == "L":
            (x1, z1), (x2, z2) = case(s[1]), case(s[2])
            if (z1 - zc) * (z2 - zc) <= 0 and z1 != z2: xs.append(x1 + (zc - z1) * (x2 - x1) / (z2 - z1))
        elif s[0] == "A":
            (cx, cz) = case(s[1]); r = s[2] * S
            if abs(zc - cz) <= r:
                dx = math.sqrt(r * r - (zc - cz) ** 2)
                for x in (cx - dx, cx + dx):
                    ang = math.degrees(math.atan2(zc - cz, x - cx)) % 360; a0, a1 = s[3] % 360, s[4] % 360
                    if (a0 <= ang <= a1) if a0 <= a1 else (ang >= a0 or ang <= a1): xs.append(x)
    return sorted(set(round(x, 2) for x in xs))

def line_pts(n):
    d = dict(ents[n]["g"]); assert ents[n]["type"] == "LINE", n
    return (float(d["10"]), float(d["20"])), (float(d["11"]), float(d["21"]))

def backwall():
    """The back wall's outside, as the drawing shows it (see the docstring)."""
    print("TOP VIEW (case X = (sheet x - %.3f) x 3, the front view's and B-B's centre; the hinge side at the top, sheet y up)" % X0)
    for n in (4931, 4992, 5107, 5071, 5116, 4983, 4985, 4966, 4991):
        p, q = line_pts(n)
        print("  #%d LINE X %+8.2f .. %+8.2f at sheet y %.3f .. %.3f" % (n, (p[0] - X0) * S, (q[0] - X0) * S, p[1], q[1]))
    p, q = line_pts(3130)
    print("SECTION A-A cut line #3130 (PHANTOM, front view): X %+.2f" % ((p[0] - X0) * S))
    d3 = [e for e in ents if e["type"] == "DIMENSION" and ("2", "_D_3") in e["g"]][0]
    xs = [float(v) for k, v in d3["g"] if k in ("13", "14")]
    ca = sum(xs) / 2.0; fa = 230.609                     # A-A centre from _D_3's extension points (the inner walls at Z 15.32); floor #7590
    print("SECTION A-A (#7590; centre sheet x %.3f from _D_3, cavity floor sheet y %.3f; the back wall is the view's left side)" % (ca, fa))
    for s_ in hatch_edges(ents[7590]):
        if s_[0] == "L" and max(s_[1][0], s_[2][0]) < 540.5:
            (x1, y1), (x2, y2) = s_[1], s_[2]
            print("  L Y %7.2f Z %6.2f .. Y %7.2f Z %6.2f" % ((ca - x1) * S, (y1 - fa) * S, (ca - x2) * S, (y2 - fa) * S))
    print("END VIEW (Y = (sheet x - 390.400) x 3 from the end-wall feature at Y 0; Z = (sheet y - 227.815) x 3 - 8.38 from the feet line; back to the right)")
    for n in (7018, 7072, 7105, 7106, 7110, 6704):
        (x1, y1), (x2, y2) = line_pts(n)
        print("  #%d LINE Y %7.2f Z %6.2f .. Y %7.2f Z %6.2f" % (n, (x1 - 390.4) * S, (y1 - 227.815) * S - 8.38, (x2 - 390.4) * S, (y2 - 227.815) * S - 8.38))

if __name__ == "__main__" and "--backwall" in sys.argv:
    backwall()
elif __name__ == "__main__":
    for n, e in enumerate(ents):
        if e["type"] != "HATCH": continue
        segs = hatch_edges(e)
        pts = [case(s[1]) for s in segs if s[0] in ("L", "A")]
        if not pts: continue
        xs = [p[0] for p in pts]; zs = [p[1] for p in pts]
        print("HATCH %d: %d edges, case X %.1f..%.1f Z %.1f..%.1f (B-B datum)" % (n, len(segs), min(xs), max(xs), min(zs), max(zs)))
        if max(xs) < 300:
            for zc in (0.5, 5, 15.32, 26.4, 50, 75, 80, 84.6, 86, 88, 90, 92, 96, 100, 101, 104, 108, 108.9):
                print("   Z %6.2f: boundary X %s" % (zc, crossings(segs, zc)))
