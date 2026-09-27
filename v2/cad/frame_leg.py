#!/usr/bin/env python3
"""The four setting legs of C6 (v2/docs/CASE-MARGINS.md section 4, the session's choice SC-07 under the owner's standing rule of 26 Sep 2026),
their printed locator and the printed centring wedges. MESHSAT-1357, 27 Sep 2026. Prototype design: nothing has been made.

What they do. Peli seats the 1450PF frame "fully seated on the internal ribs", and at the current moulding (drawing 1451-931 of 15 Jan 2025) that
seat is a knife edge: the frame can come to rest anywhere in a band 11.9 mm deep on its own published tolerance (CASE-MARGINS.md 2.7). Four legs
bonded under the frame's ring and standing on Peli's flat floor give the frame a floor-referenced height, the same datum as the board stack, so
the face over the monitor (M1) no longer carries the rib's height. The legs are placed on the frame by a printed locator in each window corner,
bonded by a VHB 5952 pad in a 0.9 pocket of the pad top (the aluminium rim meets the ring and sets the height), and the frame's own centring (two
pairs of printed wedges) places them against the case. Peli's four self-tapping screws then fix the frame as Peli instructs; the legs carry it in
compression and stay in the case.

Every number is panel1450.LEG / LEG_TOP_Z / PELI (v2/ecad/tools/panel1450.py): the profile lies in the X-Z plane at |Y| 106.4 to 112.4; the foot
bears on the flat floor over |X| 156.0 to 169.0; beyond the foot the underside rises to the fillet's 2.5 normal offset and follows Peli's R 15.88
floor fillet at that offset; the column runs up at |X| 175.40 to 180.17 to the pad top at Z 94.13 +-0.10; a gusset joins the column to the foot
below Z 30. The foot's height (8.0) and the gusset's line are the session's shape (INFERRED), inside the zone the legs claim (|X| 156.0 to 180.17,
|Y| 106.4 to 112.4, floor to Z 94.2), which every CASE-MARGINS row carries.

Usage: frame_leg.py <out dir>   (build123d, ezdxf: v2/cad/requirements-cad.txt). Writes frame-leg.step/.stl (one leg, east-front, in the case
frame), frame-legs-4.step (all four in place), frame-leg.dxf (the profile for a waterjet or laser cut from 6.0 6061-T6), leg-locator.step/.stl,
wedge.step/.stl, and prints the masses and the figures the drawing states."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ecad", "tools"))
import panel1450 as L
from build123d import (BuildSketch, BuildLine, Polyline, ThreePointArc, make_face, extrude, Plane, Box, Location, Vector, Axis, Compound,
                       export_step, export_stl, Locations, RectangleRounded, Rectangle, Cylinder)

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)
G = L.LEG
FIL_R = L.PELI["fillet_r"]; FLAT_X = L.PELI["flat_floor"][0]
TOP = L.LEG_TOP_Z
X0F, X1F = G["foot_x"]; C0, C1 = G["col_x"]; RO = FIL_R - G["relief"]


def fil_off_z(x):
    """The underside's Z at x beyond the fillet tangent: Peli's R 15.88 floor fillet (centre X 171.64, Z 15.88) offset 2.5 along its normal."""
    d = x - FLAT_X
    return FIL_R - math.sqrt(RO * RO - d * d) if d > 0 else G["relief"]


def profile_pts():
    """The leg's profile in the X-Z plane (east leg, X positive), counter-clockwise from the foot's inner bearing corner."""
    z_out = fil_off_z(C1)
    xm = (FLAT_X + C1) / 2; zm = fil_off_z(xm)
    return dict(p0=(X0F, 0.0), p1=(X1F, 0.0), p2=(X1F, G["relief"]), p3=(FLAT_X, G["relief"]), mid=(xm, zm), p4=(C1, z_out),
                p5=(C1, TOP), p6=(C0, TOP), p7=(C0, G["gusset_z"]), p8=(X0F, G["foot_h"]))


def leg_solid():
    p = profile_pts()
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine():
            Polyline(p["p8"], p["p0"], p["p1"], p["p2"], p["p3"])
            ThreePointArc(p["p3"], p["mid"], p["p4"])
            Polyline(p["p4"], p["p5"], p["p6"], p["p7"], p["p8"])
        make_face()
    # Plane.XZ's normal is -Y: extrude by the profile's thickness, then move the slab to |Y| 106.4 .. 112.4 on the front (-Y) side
    leg = extrude(sk.sketch, amount=G["t"])
    bb = leg.bounding_box()
    leg = leg.moved(Location(Vector(0, -G["y"][0] - bb.max.Y, 0)))
    # the VHB pocket in the pad top: 0.5 rim all round, 0.9 deep (INFERRED rim)
    pw, pd = (C1 - C0) - 1.0, G["t"] - 1.0
    pocket = Box(pw, pd, G["vhb_pocket"] + 1.0).moved(Location(Vector((C0 + C1) / 2, -(G["y"][0] + G["y"][1]) / 2, TOP - G["vhb_pocket"] + (G["vhb_pocket"] + 1.0) / 2)))
    return leg - pocket


def locator_solid():
    """The printed locator, used with the frame face down on the bench: its key drops into a window corner and registers on both window faces;
    its slot holds the leg's pad at its drawn place on the ring's underside (0.2 clearance round the pad, INFERRED). Drawn for the east-front
    corner in case X and Y; its Z is the ring's underside (0 here), the key reaching 4.0 into the window."""
    wx, wy = L.WINDOW[0] / 2, L.WINDOW[1] / 2        # the window's edges (349.65 x 233.83); corner R 6.35 (frame STEP)
    # the plate lying on the ring's underside: with the frame face down the skirt stands up round the ring, so the plate keeps 1.0 inside the
    # skirt's inner corner (R 17.53 about (165.81, 107.90), frame STEP) and 1.3 of wall round the pad slot
    bx0, bx1, by0, by1 = wx - 11.0, 181.2, -113.9, -97.0
    body = Box(bx1 - bx0, by1 - by0, 3.0).moved(Location(Vector((bx0 + bx1) / 2, (by0 + by1) / 2, 1.5)))
    key = Box(10.0, 10.0, 4.0).moved(Location(Vector(wx - 5.0, -(wy - 5.0), -2.0)))          # the key inside the window corner
    # the key's corner follows the window's R 6.35 corner: cut the square corner away and add the radius
    corner_cut = Box(6.35, 6.35, 4.2).moved(Location(Vector(wx - 6.35 / 2, -(wy - 6.35 / 2), -2.0)))
    corner_add = Cylinder(6.35, 4.2).moved(Location(Vector(wx - 6.35, -(wy - 6.35), -2.0)))
    key = (key - corner_cut) + (corner_add & Box(6.35, 6.35, 4.2).moved(Location(Vector(wx - 6.35 / 2, -(wy - 6.35 / 2), -2.0))))
    slot = Box((C1 - C0) + 0.4, G["t"] + 0.4, 8.0).moved(Location(Vector((C0 + C1) / 2, -(G["y"][0] + G["y"][1]) / 2, 1.5)))
    return (body + key) - slot


def wedge_solid():
    """A centring wedge: 0 to 2.0 over 40 (panel1450.LEG['wedge']), 10 wide, with a 15 mm grip tab and depth marks every 10 mm (printed)."""
    t0, t1, ln = G["wedge"]
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine():
            Polyline((0, 0), (ln, 0), (ln, t1), (ln + 15.0, t1), (ln + 15.0, 0.0), (ln + 15.0, t1 + 3.0), (ln, t1 + 3.0), (0, max(t0, 0.3)), (0, 0))
        make_face()
    w = extrude(sk.sketch, amount=10.0)
    for k in range(1, 4):
        w -= Box(0.6, 12.0, 0.4).moved(Location(Vector(10.0 * k, -5.0, t1 * 10.0 * k / ln + 0.2)))
    return w


def area_profile():
    """Profile area (mm2) by the shoelace formula on a fine polyline of the outline."""
    p = profile_pts(); pts = [p["p8"], p["p0"], p["p1"], p["p2"], p["p3"]]
    for k in range(1, 20):
        x = FLAT_X + (C1 - FLAT_X) * k / 20.0; pts.append((x, fil_off_z(x)))
    pts += [p["p4"], p["p5"], p["p6"], p["p7"]]
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))) / 2


def dxf(path):
    import ezdxf
    doc = ezdxf.new("R2010"); doc.header["$INSUNITS"] = 4; msp = doc.modelspace()
    for n in ("PROFILE_6MM_6061T6", "POCKET_0.9MM_PAD_TOP", "NOTES"): doc.layers.add(n)
    p = profile_pts()
    pts = [p["p8"], p["p0"], p["p1"], p["p2"], p["p3"]]
    for k in range(1, 40):
        x = FLAT_X + (C1 - FLAT_X) * k / 40.0; pts.append((x, fil_off_z(x)))
    pts += [p["p4"], p["p5"], p["p6"], p["p7"]]
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "PROFILE_6MM_6061T6"})
    msp.add_lwpolyline([(C0 + 0.5, TOP), (C1 - 0.5, TOP), (C1 - 0.5, TOP - G["vhb_pocket"]), (C0 + 0.5, TOP - G["vhb_pocket"])], close=True,
                       dxfattribs={"layer": "POCKET_0.9MM_PAD_TOP"})
    msp.add_text("MeshSat V2 setting leg (C6), 6.0 6061-T6, 4 off; X and Z in the case frame (X from the case centre, Z from the cavity floor); "
                 "the pad-top pocket is 0.9 deep across the 6.0 thickness less a 0.5 rim", dxfattribs={"layer": "NOTES", "height": 2.0}).set_placement((X0F, -12.0))
    doc.saveas(path)


if __name__ == "__main__":
    leg = leg_solid()
    bb = leg.bounding_box()
    export_step(leg, os.path.join(OUT, "frame-leg.step")); export_stl(leg, os.path.join(OUT, "frame-leg.stl"))
    legs = [leg, leg.mirror(Plane.YZ), leg.mirror(Plane.XZ), leg.mirror(Plane.YZ).mirror(Plane.XZ)]
    export_step(Compound(children=legs), os.path.join(OUT, "frame-legs-4.step"))
    dxf(os.path.join(OUT, "frame-leg.dxf"))
    loc = locator_solid(); export_step(loc, os.path.join(OUT, "leg-locator.step")); export_stl(loc, os.path.join(OUT, "leg-locator.stl"))
    wd = wedge_solid(); export_step(wd, os.path.join(OUT, "wedge.step")); export_stl(wd, os.path.join(OUT, "wedge.stl"))
    a = area_profile()
    print("frame-leg: bbox X %.2f..%.2f Y %.2f..%.2f Z %.2f..%.2f; profile %.0f mm2, volume %.0f mm3, %.1f g in 6061 (4 off %.1f g)" % (
        bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z, a, leg.volume, leg.volume * 2.70e-3, 4 * leg.volume * 2.70e-3))
    print("frame-leg: underside under the column's outer face Z %.2f; pad top %.2f; pad %.2f x %.2f" % (fil_off_z(C1), TOP, C1 - C0, G["t"]))
    print("leg-locator volume %.0f mm3; wedge volume %.0f mm3" % (loc.volume, wd.volume))
    print("FRAME-LEG-DONE")
