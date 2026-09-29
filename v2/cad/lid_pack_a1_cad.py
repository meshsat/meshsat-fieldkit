#!/usr/bin/env python3
"""Solids of the Option A(i) lid module (MESHSAT-1357, stream a1mech) and a check of lid_pack_a1.py's clearance arithmetic by booleans.

Builds, from v2/cad/lid_pack_a1.py (imported: the one source of every number), for each arrangement (A, B, C, C10, D):
  - the module's envelope: each slice's one-layer box, each layer-2 cell's two-layer box, P2's box, the tablet's box, hung from a
    ceiling placed at the WORST room above the face top (face top at Z 0, ceiling at Z 44.39) and lowered by the module's own
    allowances (0.43; the tablet's 0.83);
  - the face parts as boxes from Z 0 to their height + the 1.0 minimum, grown in plan by the plan allowance (1.06); a part of TBD height
    stands to the ceiling;
and reports every intersection volume, which must be 0.000 wherever lid_pack_a1.out reads a margin of 1.0 or more at the worst, and
positive wherever it reads less (two controls prove the check can fail). Then exports arrangement B in the case frame at the nominal
ceiling Z 154.44: the lid plate, every cell (d 18.55, L 65.25, the sheet's maxima), the cover envelope and P2's envelope, as STEP and STL.
Usage: lid_pack_a1_cad.py <out dir>   (build123d; the CAD venv of v2/cad/requirements-cad.lock). Prototype design, AI review."""
import os, sys
from build123d import Box, Cylinder, Location, Vector, Compound, export_step, export_stl, Axis

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lid_pack_a1 as L

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)


def box(x0, y0, z0, x1, y1, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0).moved(Location(Vector((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))


def envelope_parts(a, ceil_z, own_scale=1.0):
    """(name, solid) for the module's zones hung from ceil_z; the own allowances lower each zone."""
    parts = [("lid plate %d" % i, box(r[0], r[1], ceil_z - L.BOND - L.PLATE - own_scale * L.OWN_SUM, r[2], r[3], ceil_z)) for i, r in enumerate(L.plate_rects(a))]
    for s, (x0, x1, ys, j) in enumerate(a["south"]):
        xa = a["x_w"] if s == 0 else x0
        xb = a["x_e"] if s == len(a["south"]) - 1 else x1
        d = L.DEPTH1 + own_scale * L.OWN_SUM
        parts.append(("one-layer zone, slice %d" % s, box(xa, ys, ceil_z - d, xb, a["y_n"], ceil_z)))
    for c in a["cells"]:
        if c["layer"] == 2:
            f = L.l2_fp(c); d = L.DEPTH2 + own_scale * L.OWN_SUM
            parts.append(("two-layer zone s%d j%d" % (c["s"], c["j"]), box(f[0], f[1], ceil_z - d, f[2], f[3], ceil_z)))
    p = a["p2_rect"]; d = L.P2_DEPTH + own_scale * L.OWN_SUM
    parts.append(("P2", box(p[0], p[1], ceil_z - d, p[2], p[3], ceil_z)))
    if a["tablet"]:
        t = a["tablet_rect"]; d = L.tablet_depth(a["tablet"]) + own_scale * (L.OWN_SUM + L.TAB_OWN)
        parts.append(("tablet", box(t[0], t[1], ceil_z - d, t[2], t[3], ceil_z - L.DEPTH1)))
    return parts


def face_solids(ceil_z):
    out = []
    g = L.PLAN_ALLOW
    for ref, r, h, _s in L.FACE:
        top = ceil_z if h is None else h + L.MIN_CLEAR
        out.append((ref, box(r[0] - g, r[1] - g, 0.0, r[2] + g, r[3] + g, top)))
    return out


def inter(a, b):
    bb1, bb2 = a.bounding_box(), b.bounding_box()
    if bb1.max.X <= bb2.min.X or bb2.max.X <= bb1.min.X or bb1.max.Y <= bb2.min.Y or bb2.max.Y <= bb1.min.Y or bb1.max.Z <= bb2.min.Z or bb2.max.Z <= bb1.min.Z:
        return 0.0
    x = a & b
    return x.volume if x is not None else 0.0


def main():
    lines = ["Solids check of v2/cad/lid_pack_a1.py (build123d): the module's zones at the WORST room (face top Z 0, ceiling Z %.2f), lowered by their own" % L.ROOM_WORST,
             "allowances, against the face parts grown %.2f in plan and standing %.1f above their height (a TBD part to the ceiling)." % (L.PLAN_ALLOW, L.MIN_CLEAR),
             "Every intersection must be 0.000 mm3 where lid_pack_a1.out reads 1.0 or more at the worst. Prototype design, AI review.", ""]
    arr = {a["name"].split(":")[0]: a for a in L.arrangements()}
    faces = face_solids(L.ROOM_WORST)
    total_bad = 0
    for key in ("A", "B", "C", "C10", "D"):
        a = arr[key]
        env = envelope_parts(a, L.ROOM_WORST)
        bad = []
        for zn, zs in env:
            for ref, fs in faces:
                v = inter(zs, fs)
                if v > 1e-6: bad.append((zn, ref, v))
        # the tablet box hangs under the one-layer cover: it must not meet any two-layer zone
        if a["tablet"]:
            tb = [s for n, s in env if n == "tablet"][0]
            for zn, zs in env:
                if zn.startswith("two-layer"):
                    v = inter(zs, tb)
                    if v > 1e-6: bad.append((zn, "tablet", v))
        total_bad += len(bad)
        lines.append("%-4s %-46s zones %3d x face parts %3d: intersections %s" % (key, a["name"].split(": ")[1], len(env), len(faces),
                                                                                 "none (0.000 mm3)" if not bad else "; ".join("%s x %s %.3f" % b for b in bad)))
    # controls: the same check must fail when the room is 1.1 smaller than the worst (the tightest rows are 2.40 and 3.10 above 1.0),
    # and when the layer-2 zones are lowered by 2.5 (the LED bar's row, 2.40 at the worst, then falls to -0.10)
    a = arr["B"]
    env_c1 = envelope_parts(a, L.ROOM_WORST - 2.5)
    c1 = sum(1 for zn, zs in env_c1 for ref, fs in faces if inter(zs, fs) > 1e-6)
    guard_box = [s for r, s in faces if r == "SW_SOS_GUARD"][0]
    shifted = envelope_parts(dict(a, x_w=a["x_w"] - 3.0, south=[(a["south"][0][0] - 3.0,) + a["south"][0][1:]] + a["south"][1:]), L.ROOM_WORST)
    c2 = sum(1 for zn, zs in shifted if inter(zs, guard_box) > 1e-6)
    lines += ["", "CONTROL 1, which must FAIL: arrangement B with the ceiling 2.5 lower: %d zone and part pairs intersect (must be > 0)" % c1,
              "CONTROL 2, which must FAIL: arrangement B's west edge 3.0 further west, over the SOS guard's cap: %d intersections (must be > 0)" % c2]
    ok = total_bad == 0 and c1 > 0 and c2 > 0
    # the solids of B in the case frame, nominal ceiling
    cz = L.CEIL_Z_NOM
    plate_parts = [box(r[0], r[1], cz - L.BOND - L.PLATE, r[2], r[3], cz - L.BOND) for r in L.plate_rects(a)]   # the plate follows the slices (check M2)
    plate = plate_parts[0]
    for p_ in plate_parts[1:]:
        plate = plate + p_
    cells = []
    for c in a["cells"]:
        zc = cz - L.BOND - L.PLATE - L.WRAP - L.CELL_D / 2 - (L.NEST_DZ if c["layer"] == 2 else 0.0)
        cyl = Cylinder(L.CELL_D / 2, L.CELL_L).rotate(Axis.Y, 90).moved(Location(Vector((c["x0"] + c["x1"]) / 2, c["yc"], zc)))
        cells.append(cyl)
    env_nom = [s for n, s in envelope_parts(a, cz, own_scale=0.0) if not n.startswith(("P2", "lid plate"))]
    p = a["p2_rect"]
    p2 = box(p[0], p[1], cz - L.P2_DEPTH, p[2], p[3], cz - L.BOND - L.PLATE)
    comp_cells = Compound(children=cells)
    env_union = env_nom[0]
    for s in env_nom[1:]:
        env_union = env_union + s
    # every cell inside the envelope: the cells minus the envelope must be empty
    outside = sum((cl - env_union).volume for cl in cells)
    lines += ["", "ARRANGEMENT B solids, case frame, lid closed, ceiling Z %.2f: plate over %.1f x %.1f (per slice) x %.1f; %d cells d %.2f x %.2f (the sheet's maxima);" % (
        cz, a["x_e"] - a["x_w"], a["y_n"] - min(s[2] for s in a["south"]), L.PLATE, len(cells), L.CELL_D, L.CELL_L),
              "cell volume outside the module's envelope: %.3f mm3 (must be 0.000); lowest point of the envelope Z %.2f (face top %.2f nominal: %.2f)" % (
        outside, env_union.bounding_box().min.Z, L.FACE_Z_NOM, env_union.bounding_box().min.Z - L.FACE_Z_NOM)]
    ok = ok and outside < 1e-3
    export_step(Compound(children=[plate, comp_cells, p2]), os.path.join(OUT, "lid-pack-a1-B-module.step"))
    export_step(env_union, os.path.join(OUT, "lid-pack-a1-B-envelope.step"))
    export_stl(Compound(children=[plate, comp_cells, p2]), os.path.join(OUT, "lid-pack-a1-B-module.stl"))
    lines += ["", "RESULT: %s" % ("PASS: no zone meets a face part at the worst, every control fails as it must, every cell inside its envelope" if ok else "FAIL"),
              "files: lid-pack-a1-B-module.step/.stl (plate, cells, P2 envelope), lid-pack-a1-B-envelope.step (the zones the face rows are judged on)"]
    with open(os.path.join(OUT, "lid_pack_a1_cad.out"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("A1CAD-DONE")


if __name__ == "__main__":
    main()
