#!/usr/bin/env python3
"""The connector plate on the Peli 1450's back wall (C3 of v2/docs/CASE-MARGINS.md, the session's choice SC-07 under the owner's standing rule
of 26 Sep 2026) and its gasket. MESHSAT-1357, 27 Sep 2026. Prototype design: nothing has been made or bought.

114.0 x 68.3 x 5.0 aluminium (5052-H32 or 6061-T6), outside the back (hinge) wall between the hinge fairings, centred at case X 0, Z 18.3 to 86.6,
on a 2.0 closed-cell gasket of the same outline. It carries the six items the tree rules for the back wall, each laid out as the class its pick
must meet (panel1450.CONN_ITEMS; CASE-MARGINS.md 3.3 and section 6):
  A sealed RJ45 with PoE out   MIL-DTL-38999 shell 15 wall-mount class (PICK OPEN: the recommended Bulgin PX0833 fails the envelope and 54 V)
  C shore DC                   Glenair D38999/20 shell 13, round holes (D0)
  B sealed USB-C 45 W          Bulgin 4000 series rear-panel class (PICK OPEN on its panel drawing: PXP4043/C)
  E outside sensor pod         on its M8 receptacle (binder 86 6618 1121 00004 recommended, sheet not held: OPEN)
  D USB host                   Glenair 233-370 shell 15 (D0)
  F ground stud                M6 class (OPEN)
The flanges of A, C and D go on M3 into threads tapped in the plate; six M4 x 25 hold the plate to the wall under bonded sealing washers.
Every cut-out of an OPEN pick is the class's and is PROVISIONAL until the picked part's own drawing confirms it.

Frames. The STEP is in the plate's own frame: u along case X, v along case Z (both the case frame's values), the plate's inner face (against
the gasket) at w 0 and its outer face at w +5.0; mounted, w points out of the case (+Y), and the plate follows the back wall's 2 degree draft.
The DXFs are drawn as seen from OUTSIDE the back wall, so case +X is on the viewer's LEFT (u_drawn = -X).

Usage: connector_plate.py <out dir>   (build123d, ezdxf: v2/cad/requirements-cad.txt). Writes connector-plate.step/.stl, connector-plate.dxf
(outline, through cut-outs, M3 tap drills, M4 clearance holes, seen from outside), connector-plate-gasket.dxf (the gasket: the wall holes)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ecad", "tools"))
import panel1450 as L

P = L.CONN_PLATE
M3_TAP, M4_CLEAR = 2.5, P["screw_hole"]


def features():
    """Every hole of the plate and of its gasket, in case (X, Z): (kind, x, z, d, note). kind: cut (a through cut-out), dcut (round with one flat),
    tap3 (M3 tap drill), m4 (the plate's M4 clearance)."""
    f = []
    for it in L.CONN_ITEMS:
        x, z = it["c"]
        if it["key"] == "B":
            f.append(("dcut", x, z, it["cutout"], "B: 19.2 with one flat %.2f from the centre toward -Z (4000 series class, PROVISIONAL)" % L.CONN_B_FLAT))
        else:
            f.append(("cut", x, z, it["cutout"], "%s: %.2f %s" % (it["key"], it["cutout"], "(PROVISIONAL, pick OPEN)" if it["status"] == "OPEN" else "")))
        if it["screws"]:
            s = it["screws"][0] / 2
            for dx in (-s, s):
                for dz in (-s, s): f.append(("tap3", x + dx, z + dz, M3_TAP, "%s flange M3" % it["key"]))
    for (x, z) in P["screws"]: f.append(("m4", x, z, M4_CLEAR, "M4 x 25"))
    return f


def solid():
    from build123d import BuildSketch, Locations, RectangleRounded, extrude, Plane, Cylinder, Box, Location, Vector
    w, h = P["x1"] - P["x0"], P["z1"] - P["z0"]
    with BuildSketch(Plane.XY) as sk:
        with Locations(((P["x0"] + P["x1"]) / 2, (P["z0"] + P["z1"]) / 2)): RectangleRounded(w, h, P["corner_r"])
    plate = extrude(sk.sketch, amount=P["t"])
    for kind, x, z, d, _ in features():
        c = Cylinder(d / 2, P["t"] + 2).moved(Location(Vector(x, z, P["t"] / 2)))
        if kind == "dcut":
            # the flat lies CONN_B_FLAT below the centre (toward -Z): keep the circle above z - flat
            keep = Box(d + 2, d + 2, P["t"] + 2).moved(Location(Vector(x, z - L.CONN_B_FLAT + (d + 2) / 2, P["t"] / 2)))
            c = c & keep
        plate -= c
    return plate


def dxf(path, gasket=False):
    import ezdxf
    doc = ezdxf.new("R2010"); doc.header["$INSUNITS"] = 4; msp = doc.modelspace()
    for n in ("OUTLINE", "THROUGH", "TAP_M3_DRILL_2.5", "NOTES"): doc.layers.add(n)
    V = lambda x, z: (-x, z)            # seen from outside the back wall: case +X to the viewer's left
    r = P["corner_r"]; pts = []
    for (cx, cz, a0) in ((P["x1"] - r, P["z1"] - r, 0), (P["x0"] + r, P["z1"] - r, 90), (P["x0"] + r, P["z0"] + r, 180), (P["x1"] - r, P["z0"] + r, 270)):
        for k in range(0, 91, 10): pts.append(V(cx + r * math.cos(math.radians(a0 + k)), cz + r * math.sin(math.radians(a0 + k))))
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "OUTLINE"})
    if gasket:
        for it in L.CONN_ITEMS: msp.add_circle(V(*it["c"]), it["wall_hole"] / 2, dxfattribs={"layer": "THROUGH"})
        for (x, z) in P["screws"]: msp.add_circle(V(x, z), M4_CLEAR / 2, dxfattribs={"layer": "THROUGH"})
        note = "MeshSat V2 connector plate GASKET, 2.0 closed-cell (EPDM or neoprene), the plate's outline, holes = the wall holes; seen from outside, case +X to the left"
    else:
        for kind, x, z, d, _ in features():
            if kind == "dcut":
                # arc above the flat, then the flat
                half = math.degrees(math.acos(L.CONN_B_FLAT / (d / 2)))
                a0, a1 = -90 + half, 270 - half
                arc = [(x + d / 2 * math.cos(math.radians(a)), z + d / 2 * math.sin(math.radians(a))) for a in [a0 + (a1 - a0) * k / 60 for k in range(61)]]
                msp.add_lwpolyline([V(*q) for q in arc], close=True, dxfattribs={"layer": "THROUGH"})
            else:
                msp.add_circle(V(x, z), d / 2, dxfattribs={"layer": "TAP_M3_DRILL_2.5" if kind == "tap3" else "THROUGH"})
        note = "MeshSat V2 connector plate (C3), %.1f 5052-H32 or 6061-T6, seen from OUTSIDE (case +X to the left); X and Z are the case frame's, negated in X for the view" % P["t"]
    msp.add_text(note, dxfattribs={"layer": "NOTES", "height": 1.8}).set_placement((-P["x1"], P["z0"] - 8.0))
    doc.saveas(path)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    from build123d import export_step, export_stl
    p = solid(); bb = p.bounding_box()
    export_step(p, os.path.join(out, "connector-plate.step")); export_stl(p, os.path.join(out, "connector-plate.stl"))
    dxf(os.path.join(out, "connector-plate.dxf")); dxf(os.path.join(out, "connector-plate-gasket.dxf"), gasket=True)
    print("connector-plate %.1f x %.1f x %.1f, volume %.0f mm3, %.0f g in aluminium; %d holes" % (bb.size.X, bb.size.Y, bb.size.Z, p.volume, p.volume * 2.70e-3, len(features())))
    print("CONNECTOR-PLATE-DONE")
