#!/usr/bin/env python3
"""MeshSat v0.6 clash check.

Intersects every printed part (exported in ASSEMBLED position: body + a_*.stl)
with the manufacturers' board geometry (STEP tessellations, registered with the
same transforms as supreme_ref()/rb9704_ref() in the .scad) and with each other.

usage: clash_check.py <build_dir> <mesh_dir> <reg.json>
Requires: trimesh, numpy, manifold3d
"""
import sys, json, itertools
import numpy as np, trimesh, manifold3d as m3

build, meshdir, regf = sys.argv[1], sys.argv[2], sys.argv[3]
R = json.load(open(regf))
TOL = 0.01   # mm^3 reported threshold

def to_mf(tm):
    tm = tm.copy(); tm.merge_vertices()
    return m3.Manifold(m3.Mesh(vert_properties=np.asarray(tm.vertices, np.float32),
                               tri_verts=np.asarray(tm.faces, np.uint32)))

def bodies(path, T):
    m = trimesh.load(path); m.apply_transform(T)
    out = []
    for b in m.split(only_watertight=False):
        if not b.is_watertight:
            if len(b.vertices) < 4 or b.extents.min() < 1e-4: continue   # degenerate sliver
            try: b = b.convex_hull                                       # conservative for open shells
            except Exception: continue
        mf = to_mf(b)
        if mf.volume() > 1e-6: out.append((b.bounds, mf))
    return out

def T_of(t, rz_deg):
    M = trimesh.transformations.rotation_matrix(np.radians(rz_deg), [0, 0, 1])
    M[:3, 3] = t
    return M

boards = {
  "Supreme STEP": bodies(f"{meshdir}/supreme_step.stl", T_of(R["sup_T"], 180)),
  "RockBLOCK 9704 STEP": bodies(f"{meshdir}/rb9704_step.stl", T_of(R["rb_T"], 90)),
}
cyl = trimesh.creation.cylinder(radius=R["hold_r"], height=R["hold_l"], sections=96)
cyl.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0]))
cyl.apply_translation(R["hold_c"])
boards["18650 holder envelope (LilyGO shell)"] = [(cyl.bounds, to_mf(cyl))]

parts = {}
for name in ["body", "a_separator", "a_lid", "a_membrane", "a_plungers", "a_retainer"]:
    tm = trimesh.load(f"{build}/{name}.stl")
    parts[name] = (tm.bounds, to_mf(tm))

def overlap(b1, b2):
    return np.all(b1[0] < b2[1]) and np.all(b2[0] < b1[1])

report = {"board_clashes": [], "part_pairs": [], "status": "PASS"}
for pn, (pb, pmf) in parts.items():
    for bn, blist in boards.items():
        tot, worst = 0.0, None
        for bb, bmf in blist:
            if not overlap(pb, bb): continue
            v = (pmf ^ bmf).volume()
            if v > TOL:
                tot += v
                bx = (pmf ^ bmf).bounding_box()
                if worst is None or v > worst[0]: worst = (v, [round(x, 2) for x in bx])
        line = f"{pn:12s} vs {bn:38s}: {tot:9.3f} mm3" + (f"  worst {worst[0]:.3f} at {worst[1]}" if worst else "")
        print(line)
        if tot > TOL:
            report["board_clashes"].append({"part": pn, "board": bn, "mm3": round(tot, 3), "worst_bbox": worst[1]})
            report["status"] = "FAIL"

intended = {("a_membrane", "a_retainer"): "flange compression 0.3 mm (intended)",
            ("body", "a_membrane"): "flange seated in pocket (contact only expected)",
            ("a_membrane", "a_plungers"): "membrane drawn uncompressed: 0.3 mm onto plunger heads (intended)"}
for (a, (ab, am)), (b, (bb, bm)) in itertools.combinations(parts.items(), 2):
    if not overlap(ab, bb): continue
    v = (am ^ bm).volume()
    note = intended.get((a, b), "")
    print(f"{a:12s} x {b:12s}: {v:9.3f} mm3 {note}")
    if v > TOL:
        report["part_pairs"].append({"a": a, "b": b, "mm3": round(v, 3), "note": note})
        if not note.endswith("(intended)"): report["status"] = "FAIL"

json.dump(report, open(f"{build}/clash_report.json", "w"), indent=2)
print("STATUS:", report["status"])
