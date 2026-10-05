#!/usr/bin/env python3
"""Mesh hygiene + printability report for every STL in the given folders.
Removes zero-area triangles in place (only if the mesh stays watertight)."""
import sys, glob, hashlib, json
import numpy as np, trimesh

rows = []
for d in sys.argv[1:]:
    for f in sorted(glob.glob(f"{d}/*.stl")):
        m = trimesh.load(f)
        deg = int((m.area_faces < 1e-9).sum())
        if deg:
            c = m.copy(); c.update_faces(c.nondegenerate_faces()); c.remove_unreferenced_vertices(); c.merge_vertices()
            if c.is_watertight: m = c; m.export(f)
        parts = m.split(only_watertight=False)
        n, cz, A = m.face_normals, m.triangles_center[:, 2], m.area_faces
        r = dict(file=f, size_mm=[round(float(x), 2) for x in m.extents], watertight=bool(m.is_watertight),
                 bodies=len(parts), floating_bodies=[round(float(p.bounds[0][2]), 2) for p in parts if p.bounds[0][2] > 0.05],
                 degenerate_removed=deg, degenerate_left=int((m.area_faces < 1e-9).sum()),
                 overhang_gt45_mm2=round(float(A[(n[:, 2] < -0.71) & (cz > 0.3)].sum()), 1),
                 horizontal_ceiling_mm2=round(float(A[(n[:, 2] < -0.99) & (cz > 0.3)].sum()), 1),
                 volume_cm3=round(float(m.volume) / 1000, 1),
                 sha256=hashlib.sha256(open(f, "rb").read()).hexdigest()[:16])
        rows.append(r); print(json.dumps(r))
json.dump(rows, open("validation/build/mesh_report.json", "w"), indent=1)
