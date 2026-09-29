#!/usr/bin/env python3
"""H1, the heat-test face plate blank of the MeshSat field kit V2 in the Peli 1450 (MESHSAT-1357, stream od01b, 29 Sep 2026).

H1 is its own part with its own definition, not "C1's CAD plus prose". It serves ONLY the empty-case heat-balance test
(v2/docs/records/od01/TEST-BRIEF.md, test A): it seals the base under the 1450PF frame's o-ring the way C1 does and carries the
test's patch resistor (Arcol HS100) where the PA flange sits, and nothing else.

Every figure it shares with C1 is read from the same single source as C1, v2/ecad/tools/panel1450.py (the one geometry source of
v2/cad/face_plate.py and v2/cad/plate_drawing.py); none is typed here:
  outline      panel1450.PLATE (377.2 x 263.0 x 3.0), panel1450.PLATE_R (R16)
  rebate       panel1450.REB_IN (368.0 x 253.0, R panel1450.REBATE_R), panel1450.REBATE (2.0 from the top face, 1.0 left)
  relief       panel1450.RELIEF_POCKET (0.8 deep in the underside over the frame's raised "1450 FRONT" lettering)
  screw holes  panel1450.FRAME_BOSSES (ten), panel1450.FACE_HOLE (4.6), for 6-32 UNC x 1/2 in into Peli's brass inserts
  patch site   panel1450.PA_MOUNT["c"] (the PA flange site, X -45.0, Y 70.0)
The one H1-only feature is the patch resistor's fixing: four PEM S-M3 self-clinching nuts on the HS100's own hole pattern,
F 35.0 +-0.3 by G 37.0 +-0.3, mounting holes L 4.4 +-0.25 (Arcol "HS Aluminium Housed Resistors" sheet 12/14.08, page 2, held in
v2/vendor/arcol/; the "3.2 max." on that page is the solder tag's hole, not the mounting hole), centred on
the PA flange site, G 37.0 along the plate's X and F 35.0 along its Y (the owner's instruction of 29 Sep 2026, R6), so the
resistor's long axis (B 88.0 max) runs along Y. The nuts go in 4.2 holes like C1's PEM hardware (panel1450 has no nut hole
constant; face_plate.py writes 4.2 for its PEM nuts and standoffs; this file writes PEM's own 4.22 +0.08, PEM_HOLE below).

Omitted from C1 on purpose (H1 must stay a closed skin): both windows and the e-paper pocket, every control and light-guide hole,
the monitor frame's four 4.5 holes, the eight PEM SO-M3-10 standoffs and C1's two PA nuts 60 apart. No laser marking.

Usage: h1_heat_test_plate.py <out dir> [--no-solid]
  writes h1-heat-test-plate.dxf (ezdxf), h1-heat-test-plate.step and .stl (build123d; skipped with --no-solid) and
  h1-heat-test-plate-check.out (the check below). Needs the pinned CAD set of v2/cad/requirements-cad.lock.
The check PARSES both DXF files with ezdxf and exits 1 if H1's shared features differ from the released C1 DXF
(v2/release/case-2026-09-27/face-plate/face-plate.dxf) by more than 0.001 mm, if a layer holds an unexpected entity, or if the
resistor's footprint meets a screw hole, the relief or the frame's window edge. Plate frame = case frame (X, Y from the case centre,
+Y toward the hinge wall), Z up from the plate's underside. Prototype: nothing has been made; the geometry establishes no fit or seal.
"""
import sys, os, math, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "ecad", "tools"))
import panel1450 as L

C1_DXF = os.path.join(REPO, "v2", "release", "case-2026-09-27", "face-plate", "face-plate.dxf")
W, H, T = L.PLATE
PEM_HOLE = 4.22                     # PEM bulletin CL (v2/vendor/pem/, S metric table): M3 x 0.5 shank code 2, mounting hole
PEM_HOLE_TOL = "+0.08/-0.00"         # 4.22 +0.08 (the independent check of od01b, minor item m1); face_plate.py's 4.2 for C1 is
                                     # a separate open item of the case set, not changed here
PEM_PART = "PEM S-M3-2"             # self-clinching nut, M3, shank code 2 (for sheets of 1.4 mm and thicker); steel, zinc plated
# Arcol HS sheet 12/14.08 page 2 (v2/vendor/arcol/arcol-hs-datasheet-12-14-08.pdf), HS100 row
HS100 = dict(F=35.0, G=37.0, FG_tol=0.3, L_hole=4.4, L_tol=0.25, A_max=47.5, B_max=88.0, C_max=24.1, D_max=27.3, K_max=3.7)
PATCH_C = tuple(L.PA_MOUNT["c"])
# the pattern: G (37.0) along X, F (35.0) along Y
PEM_XY = [(PATCH_C[0] + sx * HS100["G"] / 2, PATCH_C[1] + sy * HS100["F"] / 2) for sy in (-1, 1) for sx in (-1, 1)]
# the resistor's footprint on the underside (A across its axis = X, B along its axis = Y), for the clearance check
PATCH_RECT = (PATCH_C[0] - HS100["A_max"] / 2, PATCH_C[1] - HS100["B_max"] / 2, PATCH_C[0] + HS100["A_max"] / 2, PATCH_C[1] + HS100["B_max"] / 2)

LAYERS = ("OUTLINE", "THROUGH", "REBATE_2MM_TOP", "RELIEF_0.8MM_UNDERSIDE", "PEM_S_M3", "INFO")


def rrect_pts(cx, cy, w, h, r):
    """The rounded rectangle as face_plate.py writes it (corner arcs in 10 degree steps), so the DXF polylines compare point for point."""
    pts = []
    for (ax, ay, a0) in ((cx + w / 2 - r, cy + h / 2 - r, 0), (cx - w / 2 + r, cy + h / 2 - r, 90), (cx - w / 2 + r, cy - h / 2 + r, 180), (cx + w / 2 - r, cy - h / 2 + r, 270)):
        for k in range(0, 91, 10):
            pts.append((ax + r * math.cos(math.radians(a0 + k)), ay + r * math.sin(math.radians(a0 + k))))
    return pts


def features():
    """H1's features as plain data: (layer, kind, params). Kinds: poly (closed point list), circle (x, y, d)."""
    rx0, ry0, rx1, ry1, rdep = L.RELIEF_POCKET
    f = [("OUTLINE", "poly", rrect_pts(0, 0, W, H, L.PLATE_R)),
         ("REBATE_2MM_TOP", "poly", rrect_pts(0, 0, L.REB_IN[0], L.REB_IN[1], L.REBATE_R)),
         ("RELIEF_0.8MM_UNDERSIDE", "poly", [(rx0, ry0), (rx1, ry0), (rx1, ry1), (rx0, ry1)])]
    f += [("THROUGH", "circle", (x, y, L.FACE_HOLE)) for (x, y) in L.FRAME_BOSSES]
    f += [("PEM_S_M3", "circle", (x, y, PEM_HOLE)) for (x, y) in PEM_XY]
    return f


def write_dxf(out):
    import ezdxf
    doc = ezdxf.new("R2010"); msp = doc.modelspace(); doc.header["$INSUNITS"] = 4
    for name in LAYERS: doc.layers.add(name)
    for layer, kind, p in features():
        if kind == "poly": msp.add_lwpolyline(p, close=True, dxfattribs={"layer": layer})
        else: msp.add_circle((p[0], p[1]), p[2] / 2, dxfattribs={"layer": layer})
    msp.add_text("H1 HEAT-TEST PLATE BLANK: see h1-heat-test-plate-drawing.pdf (governs). PEM_S_M3 = 4 x %s pressed from the TOP face, flush on the underside." % PEM_PART,
                 height=3.0, dxfattribs={"layer": "INFO"}).set_placement((-W / 2, -H / 2 - 12))
    fn = os.path.join(out, "h1-heat-test-plate.dxf"); doc.saveas(fn); return fn


def write_solid(out):
    from build123d import Box, Cylinder, Location, Vector, Plane, BuildSketch, Locations, RectangleRounded, extrude, export_step, export_stl

    def rrect(cx, cy, w, h, r, z0, depth):
        with BuildSketch(Plane.XY.offset(z0)) as sk:
            with Locations((cx, cy)): RectangleRounded(w, h, r)
        return extrude(sk.sketch, amount=depth)

    def cyl(cx, cy, d, z0, depth):
        return Cylinder(d / 2, depth).moved(Location(Vector(cx, cy, z0 + depth / 2)))

    # the same construction as face_plate.py for every shared feature
    plate = rrect(0, 0, W, H, L.PLATE_R, 0, T)
    plate -= rrect(0, 0, W + 10.0, H + 10.0, L.PLATE_R, T - L.REBATE, L.REBATE + 1.0) - rrect(0, 0, L.REB_IN[0], L.REB_IN[1], L.REBATE_R, T - L.REBATE - 1.0, L.REBATE + 3.0)
    rx0, ry0, rx1, ry1, rdep = L.RELIEF_POCKET
    plate -= Box(rx1 - rx0, ry1 - ry0, rdep + 1.0).moved(Location(Vector((rx0 + rx1) / 2, (ry0 + ry1) / 2, (rdep - 1.0) / 2)))
    for (x, y) in L.FRAME_BOSSES: plate -= cyl(x, y, L.FACE_HOLE, -1, T + 2)
    for (x, y) in PEM_XY: plate -= cyl(x, y, PEM_HOLE, -1, T + 2)
    export_step(plate, os.path.join(out, "h1-heat-test-plate.step")); export_stl(plate, os.path.join(out, "h1-heat-test-plate.stl"))
    bb = plate.bounding_box()
    return (bb.size.X, bb.size.Y, bb.size.Z, plate.volume)


def dxf_entities(fn, layers):
    """Parse a DXF: per layer, sorted circles (x, y, d) and polylines (point lists), rounded to 1e-4."""
    import ezdxf
    doc = ezdxf.readfile(fn); out = {k: dict(circle=[], poly=[], other=[]) for k in layers}
    for e in doc.modelspace():
        lay = e.dxf.layer
        if lay not in out: continue
        t = e.dxftype()
        if t == "CIRCLE": out[lay]["circle"].append((round(e.dxf.center.x, 4), round(e.dxf.center.y, 4), round(2 * e.dxf.radius, 4)))
        elif t == "LWPOLYLINE": out[lay]["poly"].append([(round(p[0], 4), round(p[1], 4)) for p in e.get_points("xy")])
        else: out[lay]["other"].append(t)
    for v in out.values(): v["circle"].sort(); v["poly"].sort()
    return out


def check(out_fn, h1_dxf, solid):
    lines, bad = [], []
    def rec(ok, text):
        lines.append(("PASS  " if ok else "FAIL  ") + text)
        if not ok: bad.append(text)
    h1 = dxf_entities(h1_dxf, LAYERS[:-1])
    c1 = dxf_entities(C1_DXF, ("OUTLINE", "THROUGH", "REBATE_2MM_TOP", "RELIEF_0.8MM_UNDERSIDE", "STANDOFF_M3"))
    # 1. the shared features equal the released C1 DXF's (parsed, not typed)
    for lay in ("OUTLINE", "REBATE_2MM_TOP", "RELIEF_0.8MM_UNDERSIDE"):
        a, b = h1[lay]["poly"], c1[lay]["poly"]
        same = len(a) == len(b) == 1 and len(a[0]) == len(b[0]) and all(abs(p[0] - q[0]) <= 1e-3 and abs(p[1] - q[1]) <= 1e-3 for p, q in zip(a[0], b[0]))
        rec(same, "%s: H1's polyline equals the released C1 DXF's (%d points, tolerance 0.001 mm)" % (lay, len(a[0]) if a else 0))
    c1_screws = sorted(c for c in c1["THROUGH"]["circle"] if abs(c[2] - L.FACE_HOLE) < 1e-6)   # every 4.6 circle C1's DXF holds, wherever it is
    rec(h1["THROUGH"]["circle"] == c1_screws and len(c1_screws) == 10,
        "THROUGH: H1's ten %.1f screw holes equal the released C1 DXF's ten at Peli's insert bores" % L.FACE_HOLE)
    # 2. every H1 layer holds exactly what H1 defines, nothing else
    exp = {"OUTLINE": (1, 0), "REBATE_2MM_TOP": (1, 0), "RELIEF_0.8MM_UNDERSIDE": (1, 0), "THROUGH": (0, 10), "PEM_S_M3": (0, 4)}
    for lay, (np_, nc) in exp.items():
        rec(len(h1[lay]["poly"]) == np_ and len(h1[lay]["circle"]) == nc and not h1[lay]["other"],
            "%s: %d polyline(s) and %d circle(s), no other entity" % (lay, np_, nc))
    # 3. the patch pattern: the HS100's F x G, G along X, centred on the PA flange site
    xs = sorted(set(c[0] for c in h1["PEM_S_M3"]["circle"])); ys = sorted(set(c[1] for c in h1["PEM_S_M3"]["circle"]))
    ok = len(xs) == 2 and len(ys) == 2 and abs((xs[1] - xs[0]) - HS100["G"]) < 1e-3 and abs((ys[1] - ys[0]) - HS100["F"]) < 1e-3 \
        and abs((xs[0] + xs[1]) / 2 - PATCH_C[0]) < 1e-3 and abs((ys[0] + ys[1]) / 2 - PATCH_C[1]) < 1e-3 and all(abs(c[2] - PEM_HOLE) < 1e-6 for c in h1["PEM_S_M3"]["circle"])
    rec(ok, "PEM_S_M3: four %.1f holes on X %.1f apart (G) and Y %.1f apart (F), centred on the PA flange site (%.1f, %.1f): X %s, Y %s"
        % (PEM_HOLE, HS100["G"], HS100["F"], PATCH_C[0], PATCH_C[1], ", ".join("%.2f" % v for v in xs), ", ".join("%.2f" % v for v in ys)))
    # 4. the resistor's footprint (A max across, B max along its axis) against the frame window edge, the screw holes and the relief
    x0, y0, x1, y1 = PATCH_RECT
    win_x, win_y = L.WINDOW[0] / 2, L.WINDOW[1] / 2
    m_win = min(win_x - x1, x0 + win_x, win_y - y1, y0 + win_y)
    rec(m_win > 0, "the HS100 footprint X %.2f..%.2f, Y %.2f..%.2f lies inside the 1450PF window (+-%.2f, +-%.2f) with %.2f mm to its nearest edge (Y, the ring under the plate)"
        % (x0, x1, y0, y1, win_x, win_y, m_win))
    def rect_circle_gap(x, y, d):
        dx = max(x0 - x, 0, x - x1); dy = max(y0 - y, 0, y - y1); return math.hypot(dx, dy) - d / 2
    g = min(rect_circle_gap(x, y, L.FACE_HOLE) for (x, y) in L.FRAME_BOSSES)
    rec(g > 0, "the HS100 footprint keeps %.2f mm to the nearest of the ten screw holes" % g)
    rx0, ry0, rx1, ry1, _ = L.RELIEF_POCKET
    rel_gap = max(rx0 - x1, x0 - rx1, ry0 - y1, y0 - ry1)
    rec(rel_gap > 0, "the HS100 footprint keeps %.2f mm to the relief pocket" % rel_gap)
    # 5. PEM hole edge distances: to the plate edge and to the rebate line (the nuts must sit in the full 3.0 thickness)
    e_reb = min(min(L.REB_IN[0] / 2 - abs(x), L.REB_IN[1] / 2 - abs(y)) for (x, y) in PEM_XY) - PEM_HOLE / 2
    rec(e_reb > 0, "every PEM hole lies in the full-thickness face, %.2f mm from its edge to the rebate line" % e_reb)
    if solid:
        sx, sy, sz, vol = solid
        rec(abs(sx - W) < 0.01 and abs(sy - H) < 0.01 and abs(sz - T) < 0.01, "solid %.2f x %.2f x %.2f mm, volume %.0f mm3 (%.0f g at 2.70 g/cm3)" % (sx, sy, sz, vol, vol * 2.7e-3))
    head = ["# H1 heat-test plate blank: check record (v2/cad/h1_heat_test_plate.py, MESHSAT-1357 stream od01b)",
            "# inputs, sha256 first 16:"]
    for p in ("v2/ecad/tools/panel1450.py", "v2/cad/h1_heat_test_plate.py", "v2/release/case-2026-09-27/face-plate/face-plate.dxf", "v2/vendor/arcol/arcol-hs-datasheet-12-14-08.pdf"):
        fp = os.path.join(REPO, p)
        head.append("#   %s  %s" % (hashlib.sha256(open(fp, "rb").read()).hexdigest()[:16] if os.path.exists(fp) else "absent          ", p))
    head.append("# PEM holes (x, y): " + "; ".join("(%.2f, %.2f)" % xy for xy in PEM_XY))
    lines = head + lines + ["RESULT %s: %d checks, %d failed" % ("PASS" if not bad else "FAIL", len(lines), len(bad))]
    open(out_fn, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return not bad


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    dxf = write_dxf(out)
    solid = None if "--no-solid" in sys.argv else write_solid(out)
    ok = check(os.path.join(out, "h1-heat-test-plate-check.out"), dxf, solid)
    print("H1-DONE" if ok else "H1-CHECK-FAILED")
    sys.exit(0 if ok else 1)
