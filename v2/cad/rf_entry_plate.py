#!/usr/bin/env python3
"""The two RF entry plates on the Peli 1450's end walls (C4 of v2/docs/CASE-MARGINS.md, the session's choice SC-07 under the owner's standing rule
of 26 Sep 2026) and their gaskets. MESHSAT-1357, 27 Sep 2026. Prototype design: nothing has been made or bought.

One 6.0 aluminium plate per end wall, 220.2 x 48.9, outside the wall at case Y -110.1 to +110.1, Z 34.55 to 83.45, on a 2.0 closed-cell gasket of
the same outline. It carries that wall's ruled PolyPhaser GTH-SFF-AL gas-discharge arrestors, which ARE the antenna bulkheads (C2): five on the
east plate (5G MAIN -62, 5G DIV -31, 5G ANT3 0, IRIDIUM +31, LORA +62) and seven on the west (VHF -93, HF -62, WIFI 2.4 -31, GNSS 0, SDR +31,
WIFI P2P A +62, WIFI P2P B +93), axis Z 59 (panel1450.WALL_EAST, WALL_WEST, SMA_Z). Each arrestor passes a 16.3 hole, its O-ring on the plate's
machined outer face, its lock washer and nut on the floor of a 26.0 spot-face 1.5 deep in the plate's BACK (the face against the gasket), so the
nut sits 1.5 lower on the thread (M13); it is tightened on the bench, cap up and ground lug down, before the plate goes on. Eight M4 x 12 A2
ISO 7380 button heads from inside the case, on rubber-faced sealing washers, go through 5.0 wall holes into M4 threads tapped through the plate
at Y +-45 and +-100, Z 40.65 and 77.35. The two plates share one outline and one screw pattern (panel1450.RF_PLATE).

Frames. The STEP is in the plate's own frame: u along case Y, v along case Z (the case frame's values), the plate's back (against the gasket)
at w 0 and its outer face at w +6.0; mounted, w points out of the case (+X on the east wall, -X on the west), following the wall's 2 degree draft.
The DXFs are drawn as seen from OUTSIDE each wall: on the EAST wall the viewer faces west and case +Y (the hinge wall) is on the RIGHT; on the
WEST wall the viewer faces east and case +Y is on the LEFT.

Usage: rf_entry_plate.py <out dir>   (build123d, ezdxf: v2/cad/requirements-cad.txt). Writes rf-entry-plate-east.step/.stl,
rf-entry-plate-west.step/.stl, and per wall rf-entry-plate-<wall>.dxf (outline, 16.3 holes, the 26.0 spot-faces on the back, M4 tap drills)
and rf-entry-gasket-<wall>.dxf (the gasket: the 27 and 5.0 wall holes)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ecad", "tools"))
import panel1450 as L

R = L.RF_PLATE
M4_TAP = 3.3


def sites(wall):
    return L.WALL_EAST if wall == "east" else L.WALL_WEST


def solid(wall):
    from build123d import BuildSketch, Locations, RectangleRounded, extrude, Plane, Cylinder, Location, Vector
    w, h = 2 * R["y"], R["z1"] - R["z0"]
    with BuildSketch(Plane.XY) as sk:
        with Locations((0.0, (R["z0"] + R["z1"]) / 2)): RectangleRounded(w, h, R["corner_r"])
    plate = extrude(sk.sketch, amount=R["t"])
    sd, sdep = R["spot"]
    for name, y in sites(wall):
        plate -= Cylinder(R["hole"] / 2, R["t"] + 2).moved(Location(Vector(y, L.SMA_Z, R["t"] / 2)))
        plate -= Cylinder(sd / 2, sdep + 1.0).moved(Location(Vector(y, L.SMA_Z, (sdep - 1.0) / 2)))      # from the back face (w 0) up to w 1.5
    for (y, z) in R["screws"]:
        plate -= Cylinder(M4_TAP / 2, R["t"] + 2).moved(Location(Vector(y, z, R["t"] / 2)))
    return plate


def dxf(path, wall, gasket=False):
    import ezdxf
    doc = ezdxf.new("R2010"); doc.header["$INSUNITS"] = 4; msp = doc.modelspace()
    for n in ("OUTLINE", "THROUGH", "SPOTFACE_26.0_DEPTH_1.5_BACK", "TAP_M4_DRILL_3.3", "NOTES"): doc.layers.add(n)
    sgn = 1.0 if wall == "east" else -1.0          # east: +Y to the viewer's right; west: +Y to the viewer's left
    V = lambda y, z: (sgn * y, z)
    r = R["corner_r"]; y0, y1, z0, z1 = -R["y"], R["y"], R["z0"], R["z1"]; pts = []
    for (cy, cz, a0) in ((y1 - r, z1 - r, 0), (y0 + r, z1 - r, 90), (y0 + r, z0 + r, 180), (y1 - r, z0 + r, 270)):
        for k in range(0, 91, 10): pts.append(V(cy + r * math.cos(math.radians(a0 + k)), cz + r * math.sin(math.radians(a0 + k))))
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "OUTLINE"})
    if gasket:
        for name, y in sites(wall): msp.add_circle(V(y, L.SMA_Z), R["wall_hole"] / 2, dxfattribs={"layer": "THROUGH"})
        for (y, z) in R["screws"]: msp.add_circle(V(y, z), R["wall_screw_hole"] / 2, dxfattribs={"layer": "THROUGH"})
        note = "MeshSat V2 RF entry plate GASKET (%s wall), 2.0 closed-cell, the plate's outline, holes = the wall holes; seen from outside" % wall
    else:
        for name, y in sites(wall):
            msp.add_circle(V(y, L.SMA_Z), R["hole"] / 2, dxfattribs={"layer": "THROUGH"})
            msp.add_circle(V(y, L.SMA_Z), R["spot"][0] / 2, dxfattribs={"layer": "SPOTFACE_26.0_DEPTH_1.5_BACK"})
            msp.add_text(name, dxfattribs={"layer": "NOTES", "height": 2.0}).set_placement(V(y - 4.0, L.SMA_Z + 16.0))
        for (y, z) in R["screws"]: msp.add_circle(V(y, z), M4_TAP / 2, dxfattribs={"layer": "TAP_M4_DRILL_3.3"})
        note = "MeshSat V2 RF entry plate (C4), %s wall, %.1f 6061-T6 or 5052-H32, seen from OUTSIDE (case +Y to the %s); spot-faces on the BACK face" % (
            wall.upper(), R["t"], "right" if wall == "east" else "left")
    msp.add_text(note, dxfattribs={"layer": "NOTES", "height": 1.8}).set_placement((-R["y"], R["z0"] - 8.0))
    doc.saveas(path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    from build123d import export_step, export_stl
    for wall in ("east", "west"):
        p = solid(wall); bb = p.bounding_box()
        export_step(p, os.path.join(out, "rf-entry-plate-%s.step" % wall)); export_stl(p, os.path.join(out, "rf-entry-plate-%s.stl" % wall))
        dxf(os.path.join(out, "rf-entry-plate-%s.dxf" % wall), wall); dxf(os.path.join(out, "rf-entry-gasket-%s.dxf" % wall), wall, gasket=True)
        print("rf-entry-plate-%s %.1f x %.1f x %.1f, %d arrestor holes, volume %.0f mm3, %.0f g in aluminium" % (
            wall, bb.size.X, bb.size.Y, bb.size.Z, len(sites(wall)), p.volume, p.volume * 2.70e-3))
    print("RF-ENTRY-PLATE-DONE")
