#!/usr/bin/env python3
"""The QMX lid tray, revision r2 (MESHSAT-1357, 27 Sep 2026, S-63 and ENGINEERING-QUESTIONS EQ-24; worktree fnd/w5tray). It replaces the
tray of 9 September 2026 (v2/cad/lid_bracket_qmx.py, released unchanged in v2/release/case-2026-09-27/lid-tray-qmx/ and sheet 14), which
was notched at one end while the unit has jacks on both end panels, and whose 95 x 63 x 25 no maker document backed. Prototype design:
nothing here has been made, printed, bought or fitted.

THE UNIT, from the maker (v2/vendor/qrp-labs/):
  * the enclosure is "95 x 63 x 25mm without protrusions", 220 g with the enclosure (qmx-product-page-2026-09-27.txt, the product page of
    24 Sep 2026; assembly manual 1.04r page 2, qmx-assembly-1_04r-pages-1-3-20-21-75-78.pdf); left and right end panels, eight M2.5 panel
    screws, four self-adhesive rubber feet whose fitting the maker calls optional, two knobs listed as "15mm" (assembly manual page 21);
  * the left panel carries Paddle, Audio and DC, the right panel RF (BNC), PTT and USB-C (operating manual 1_04_004 pages 7 and 8); the
    VOL and TUNE encoders and two buttons sit along one long edge of the top face and the LCD window in its middle (page 13);
  * where each jack sits is SCALED from those undimensioned figures (v2/vendor/qrp-labs/measure_qmx_figures.py, qmx-figures.out: the
    figures come out at the maker's 63 x 25 within 0.4 percent) and cross-checked on the maker's photograph of the right panel: the RF jack
    reads 12.1 from the knob edge on the figure and 8.3 on the photograph, so the tray takes every jack over the range of both, widened by
    0.5 (JACK_RANGE); INFERRED, not a maker dimension;
  * the knob height above the top face is not stated by the maker: 11.6 scaled from the assembly manual's photograph 15 of the sibling
    QCX-mini in the same enclosure family (11.1 on the print, +5 percent for the knob standing behind the photographed face; INFERRED);
    the design is judged for any knob up to KNOB_H_MAX, the height at which the knob tips reach the face's 1.0 minimum at the worst.

WHAT THE TRAY DOES (the session's choices under the owner's standing rule of 26 Sep 2026, recorded in the r2 release README with reasons
and reversals): the unit lies top face out, its knob edge west and its right panel toward the hinge; BOTH end panels are open over their
whole height above a 1.5 mm sill, so every jack takes its plug from any side and no jack position the figures leave uncertain can meet a
wall; the unit slides in from the front (left-panel) end under two long ledges, is pressed up against them by two PORON 4701-30 pads and
is kept along its length by the tray's integral end block at the hinge end and a screwed keeper at the front end; the walls stand on
gussets and are tied at the top by a lintel at each end; the tray is printed in Prusament PC Blend (HDT 113 C at 0.45 MPa, where the
PETG of r1 is 68 C, under E3-S's +71 C storage) and screwed with ten flush M3 countersunk screws into a 2.0 mm 5052-H32 aluminium lid
plate tapped through, which is bonded to the lid's unribbed inner face with 3M DP8005 (no hole in the case, ruling of 7 Sep 2026).

FRAMES. Part frame: x along the unit's length, +x toward the RIGHT panel (RF, PTT, USB), which faces the hinge (case +Y); y across, +y
toward the unit's BACK long edge (case +X, east), -y toward the knob edge (west); z up from the lid plate's face, the pocket opening
toward +z (toward the face plate with the lid closed). Case frame with the lid closed: X = PLACE_X + y, Y = PLACE_Y + x,
Z = ceiling - BOND - PLATE_T - z (a proper rotation). Importing this module builds nothing; build_*() need build123d
(v2/cad/requirements-cad.lock). Usage: lid_tray_qmx_r2.py <out dir>."""
import os, sys, math

# ---------------------------------------------------------------- the unit (maker figures; SCALED ones marked)
UNIT = (95.0, 63.0, 25.0)                  # length, width, height without protrusions (maker)
UNIT_MASS = 0.220                          # kg with the enclosure (maker)
UNIT_TOL = 0.2                             # the extrusion's and panels' tolerance: not stated by the maker (INFERRED)
PANEL_T = 1.5                              # each end panel: (95 - 92.0) / 2, the top-face figure's 92.0 long extrusion (SCALED)
# jacks: name -> (panel, v from the KNOB (front) edge, height above the unit's bottom face, figure's opening, who plugs it)
#   left panel figure x -> v = 63 - x (the panel is drawn from outside, where the knob edge is on the right); right panel v = x
JACKS = {
    "DC":     dict(panel="L", v=(10.7, 10.7), h=(11.9, 11.9), hole=6.3, use="lid harness: 12.0 V lead to A22 J_HF (2.1 x 5.5 barrel)"),
    "Audio":  dict(panel="L", v=(20.9, 20.9), h=(8.5, 8.5), hole=6.3, use="operator: earphones (3.5 mm stereo), lid open only"),
    "Paddle": dict(panel="L", v=(32.8, 32.8), h=(8.5, 8.5), hole=6.2, use="operator: paddle, microphone or GPS (3.5 mm stereo), lid open only"),
    "RF":     dict(panel="R", v=(8.3, 12.1), h=(10.5, 11.6), hole=12.4, use="lid harness: RG-316 BNC-to-SMA jumper to A22 J_RF2"),
    "PTT":    dict(panel="R", v=(29.0, 29.7), h=(7.9, 8.5), hole=6.3, use="operator: PTT output to an amplifier (3.5 mm), lid open only"),
    "USB":    dict(panel="R", v=(41.1, 41.1), h=(6.8, 7.0), hole=(8.8, 3.4), use="lid harness: USB-C lead to B16 J_QMX"),
}
JACK_RANGE = 0.5                           # every scaled figure widened by this, beyond the figure-to-photograph spread
USBC_OVERMOLD_W = 12.35                    # the widest USB-C overmold the admitted envelope is also checked against (a class, INFERRED)
KNOB_U = 21.4                              # both encoder centres from their own end face (top-face figure, SCALED)
KNOB_V = 13.7                              # from the knob edge (SCALED)
KNOB_D = 18.0                              # the knob class the tray keeps clear: the "15mm" knob and its skirt, 17.6 on the photograph (INFERRED)
KNOB_H = 11.6                              # knob top above the top face (INFERRED, above)
FINGER = 6.0                               # finger room kept free of any ledge around each knob
BUTTONS = [(39.9, 10.3), (55.0, 10.3)]     # u from the left end face, v from the knob edge (SCALED), 4.3 openings
LCD = (15.5, 79.5, 16.3, 30.5)             # u0, u1 from the left end face; w0, w1 from the BACK edge (SCALED)

# ---------------------------------------------------------------- the stack and the part
BOND = 0.20                                # DP8005 bond line: its .008 in microspheres set it (3m-scotch-weld-dp8005.pdf, page 3)
PLATE_T = 2.0                              # the aluminium lid plate
FLOOR = 1.6                                # tray floor
G_B = 0.5                                  # the unit's bottom above the floor top, nominal (it rides on the pads, pressed up to the ledges)
CLR = 0.3                                  # clearance to the unit at the side walls and at the sill and keeper faces
WALL = 4.0
LEDGE_T = 2.0
LEDGE_BACK = 4.0                           # overhang over the back long edge (nothing on the top face within 16.3 of it)
LEDGE_FRONT = 3.0                          # overhang over the knob edge, in three segments clear of the knobs
SILL_H = 1.5                               # sill and keeper above the unit's bottom face: below every plug the jacks admit
GUSSET = dict(x=(-44.0, -22.0, 0.0, 22.0, 44.0), t=2.5, depth=8.0, z_top=25.0)
LINTEL_W = 3.0                             # the tie across each open end at ledge level, beyond the unit's end faces
END_L = 8.0                                # the end block (hinge end) and the keeper (front end), along x
PAD = dict(size=(24.0, 20.0), x=(-22.0, 22.0), material="Rogers PORON 4701-30 Very Soft, 320 kg/m3, 3.18 mm (0.125 in), black (04)",
           t=3.18, t_tol=0.10, cfd25_kpa=(21.0, 55.0))   # through-windows in the floor; the pads stand on the plate (rogers-poron-4701-30-very-soft.pdf)
CSK = dict(d_head=6.72, k=1.86, hole=3.4)  # M3 countersunk hex socket, ISO 10642 class (head 6.72 and 1.86 at most; standard not held, INFERRED)
SCREW = "M3 x 5 countersunk hex socket, ISO 10642 class, A2"
TAP = 2.5                                  # tap drill for M3 in the lid plate

# derived numbers (all in the part frame)
U0 = UNIT[0] / 2                           # 47.5: the unit's end faces at x = +-U0
SIDE_IN = UNIT[1] / 2 + CLR                # 31.8: wall inner faces
SIDE_OUT = SIDE_IN + WALL                  # 35.8: wall outer faces
BASE_Y = SIDE_OUT + GUSSET["depth"]        # 43.8: the floor's and the plate's half width
FACE_X = U0 + CLR                          # 47.8: the sill and keeper faces, and the walls' ends
BASE_X = FACE_X + END_L                    # 55.8: the floor's and the plate's half length
Z_UB = FLOOR + G_B                         # 2.1: the unit's bottom face
Z_UT = Z_UB + UNIT[2]                      # 27.1: its top face, and the ledges' underside
Z_TOP = Z_UT + LEDGE_T                     # 29.1: the tray's open face
Z_SILL = Z_UB + SILL_H                     # 3.6: the end block's, keeper's and screw bosses' top
KNOB_X = U0 - KNOB_U                       # 26.1: encoder centres at x = +-26.1
KNOB_Y = -UNIT[1] / 2 + KNOB_V             # -17.8
KNOB_ZONE = (KNOB_X - KNOB_D / 2 - FINGER, KNOB_X + KNOB_D / 2 + FINGER)   # |x| over which the knob edge has no ledge and a low wall
FRONT_SEGMENTS = [(-(U0 - 1.0), -KNOB_ZONE[1]), (-KNOB_ZONE[0], KNOB_ZONE[0]), (KNOB_ZONE[1], U0 - 1.0)]
BACK_LEDGE = (-(U0 - 1.0), U0 - 1.0)
SCREWS_BOSS = [(sx * 33.0, sy * (SIDE_OUT + GUSSET["depth"] / 2)) for sx in (-1, 1) for sy in (-1, 1)]   # tray fixings, in the side flanges
SCREWS_END_R = [(FACE_X + END_L / 2, y) for y in (-24.0, 0.0, 24.0)]                                    # through the integral end block
SCREWS_KEEPER = [(-(FACE_X + END_L / 2), y) for y in (-24.0, 0.0, 24.0)]                                # through the keeper and the deck
PLATE_HOLES = SCREWS_BOSS + SCREWS_END_R + SCREWS_KEEPER
SIZE = (2 * BASE_X, 2 * BASE_Y, Z_TOP)     # 111.6 x 87.6 x 29.1: the tray over its base
# place with the lid closed (case frame): the east edge stays at panel1450.QMX_TRAY_X[1], 171.0, so C5's M19 is unchanged; the tray grows
# west (the lid's ceiling is free there: the tablet bracket keeps the west third). PLACE_Y is the r1 tray's centre along Y (scene.py QY 10.0).
EAST_EDGE_X = 171.0
PLACE_X = EAST_EDGE_X - BASE_Y             # 127.2: the unit's centre across the case
PLACE_Y = 10.0
SPAN_X = (PLACE_X - BASE_Y, PLACE_X + BASE_Y)
SPAN_Y = (PLACE_Y - BASE_X, PLACE_Y + BASE_X)


def admitted_radius(name):
    """The largest plug body radius the tray admits about a jack's axis at the worst of its scaled place: the plug clears the sill and
    keeper top (Z_SILL) by 0.5, nothing else of the tray lies in front of an end panel below the lintel, and the lintel stands above the
    unit's top face."""
    j = JACKS[name]
    return Z_UB + min(j["h"]) - JACK_RANGE - Z_SILL - 0.5


def to_case(x, y, ceiling):
    return (PLACE_X + y, PLACE_Y + x, ceiling - BOND - PLATE_T)


# ---------------------------------------------------------------- the solids (build123d)
def _bd():
    import build123d as bd
    return bd


def _box(bd, x0, x1, y0, y1, z0, z1):
    return bd.Box(x1 - x0, y1 - y0, z1 - z0).moved(bd.Location(bd.Vector((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))


def _csk(bd, x, y, z_top, depth):
    """A countersunk M3 hole from z_top down through `depth` (90 degree cone to CSK d_head at the top)."""
    cone_h = (CSK["d_head"] - CSK["hole"]) / 2
    cone = bd.Cone(CSK["hole"] / 2, CSK["d_head"] / 2, cone_h).moved(bd.Location(bd.Vector(x, y, z_top - cone_h / 2)))   # narrow end down
    shaft = bd.Cylinder(CSK["hole"] / 2, depth + 2).moved(bd.Location(bd.Vector(x, y, z_top - depth / 2)))
    head_room = bd.Cylinder(CSK["d_head"] / 2, 2.0).moved(bd.Location(bd.Vector(x, y, z_top + 1.0)))
    return cone + shaft + head_room


def build_tray():
    bd = _bd()
    t = _box(bd, -BASE_X, BASE_X, -BASE_Y, BASE_Y, 0, FLOOR)                                   # the base (floor and deck)
    for sy in (-1, 1):                                                                          # the two long walls
        t += _box(bd, -FACE_X, FACE_X, *sorted((sy * SIDE_IN, sy * SIDE_OUT)), 0, Z_TOP)
    t += _box(bd, BACK_LEDGE[0], BACK_LEDGE[1], SIDE_IN - LEDGE_BACK, SIDE_IN, Z_UT, Z_TOP)   # back ledge, full length
    for x0, x1 in FRONT_SEGMENTS:                                                               # knob-edge ledge segments
        t += _box(bd, x0, x1, -SIDE_IN, -SIDE_IN + LEDGE_FRONT, Z_UT, Z_TOP)
    for sx in (-1, 1):                                                                          # the lintels at ledge level beyond each end face
        t += _box(bd, *sorted((sx * U0, sx * (U0 + LINTEL_W))), -SIDE_OUT, SIDE_OUT, Z_UT, Z_TOP)
    t += _box(bd, FACE_X, BASE_X, -BASE_Y, BASE_Y, 0, Z_SILL)                                  # the integral end block (hinge end, +x)
    for x, y in SCREWS_BOSS:                                                                    # screw bosses in the side flanges
        t += bd.Cylinder(4.0, Z_SILL).moved(bd.Location(bd.Vector(x, y, Z_SILL / 2)))
    for gx in GUSSET["x"]:                                                                      # gussets on both walls' outer faces
        for sy in (-1, 1):
            with bd.BuildSketch(bd.Plane.YZ.offset(gx - GUSSET["t"] / 2)) as sk:
                y0 = sy * SIDE_OUT; y1 = sy * (SIDE_OUT + GUSSET["depth"])
                bd.Polygon((y0, FLOOR), (y1, FLOOR), (y0, GUSSET["z_top"]), align=None)
            t += bd.extrude(sk.sketch, amount=GUSSET["t"])
    # cuts: the front wall lowered to the unit's top face in the knob zones; the pad windows; the countersunk holes
    for sx in (-1, 1):
        t -= _box(bd, *sorted((sx * KNOB_ZONE[0], sx * KNOB_ZONE[1])), -SIDE_OUT - 1, -SIDE_IN + 0.01, Z_UT, Z_TOP + 1)
    for px in PAD["x"]:
        t -= _box(bd, px - PAD["size"][0] / 2, px + PAD["size"][0] / 2, -PAD["size"][1] / 2, PAD["size"][1] / 2, -1, FLOOR + 1)
    for x, y in SCREWS_BOSS + SCREWS_END_R:
        t -= _csk(bd, x, y, Z_SILL, Z_SILL)
    for x, y in SCREWS_KEEPER:                                                                  # the keeper's screws pass the deck
        t -= bd.Cylinder(CSK["hole"] / 2, FLOOR + 2).moved(bd.Location(bd.Vector(x, y, FLOOR / 2)))
    return t


def build_keeper():
    """The front-end keeper, printed separately: it lies on the deck (z FLOOR..Z_SILL), its face at x = -FACE_X on the left panel's
    bottom band, held by three flush M3 countersunk screws through the deck into the lid plate."""
    bd = _bd()
    k = _box(bd, -BASE_X, -FACE_X, -SIDE_OUT, SIDE_OUT, FLOOR, Z_SILL)
    for x, y in SCREWS_KEEPER:
        k -= _csk(bd, x, y, Z_SILL, Z_SILL - FLOOR)
    return k


def build_plate():
    """The lid plate: 5052-H32 aluminium 2.0, the tray's base outline with R6 corners, ten M3 tapped through (tap drill 2.5)."""
    bd = _bd()
    with bd.BuildSketch() as sk:
        bd.RectangleRounded(2 * BASE_X, 2 * BASE_Y, 6.0)
        with bd.Locations(*PLATE_HOLES):
            bd.Circle(TAP / 2, mode=bd.Mode.SUBTRACT)
    return bd.extrude(sk.sketch, amount=PLATE_T)


def write_plate_dxf(path):
    import ezdxf
    doc = ezdxf.new("R2010"); doc.units = ezdxf.units.MM; msp = doc.modelspace()
    for name, col in (("OUTLINE", 7), ("TAPPED_M3_THROUGH", 1), ("NOTE", 3)):
        doc.layers.add(name, color=col)
    r, w, h = 6.0, 2 * BASE_X, 2 * BASE_Y
    x0, y0, x1, y1 = -BASE_X, -BASE_Y, BASE_X, BASE_Y
    msp.add_line((x0 + r, y0), (x1 - r, y0), dxfattribs={"layer": "OUTLINE"}); msp.add_line((x1, y0 + r), (x1, y1 - r), dxfattribs={"layer": "OUTLINE"})
    msp.add_line((x1 - r, y1), (x0 + r, y1), dxfattribs={"layer": "OUTLINE"}); msp.add_line((x0, y1 - r), (x0, y0 + r), dxfattribs={"layer": "OUTLINE"})
    for cx, cy, a0 in ((x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        msp.add_arc((cx, cy), r, a0, a0 + 90, dxfattribs={"layer": "OUTLINE"})
    for x, y in PLATE_HOLES:
        msp.add_circle((x, y), TAP / 2, dxfattribs={"layer": "TAPPED_M3_THROUGH"})
    msp.add_text("QMX LID PLATE r2: 5052-H32 2.0 mm; 10 x M3 TAPPED THROUGH (tap drill 2.5); deburr; bond face abraded and degreased",
                 height=2.0, dxfattribs={"layer": "NOTE"}).set_placement((x0, y0 - 6.0))
    doc.saveas(path)


if __name__ == "__main__":
    import build123d as bd
    OUT = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(OUT, exist_ok=True)
    tray, keeper, plate = build_tray(), build_keeper(), build_plate()
    bd.export_step(tray, os.path.join(OUT, "lid-tray-qmx-r2.step")); bd.export_stl(tray, os.path.join(OUT, "lid-tray-qmx-r2.stl"))
    bd.export_step(keeper, os.path.join(OUT, "lid-tray-qmx-r2-keeper.step")); bd.export_stl(keeper, os.path.join(OUT, "lid-tray-qmx-r2-keeper.stl"))
    bd.export_step(plate, os.path.join(OUT, "lid-plate-qmx-r2.step")); write_plate_dxf(os.path.join(OUT, "lid-plate-qmx-r2.dxf"))
    for nm, s, rho in (("tray", tray, 1.22e-3), ("keeper", keeper, 1.22e-3), ("lid plate", plate, 2.68e-3)):
        b = s.bounding_box()
        print("%-9s %6.1f x %5.1f x %5.1f mm, %8.0f mm3, %5.1f g (%s)" % (nm, b.size.X, b.size.Y, b.size.Z, s.volume, s.volume * rho,
              "PC Blend 1.22 g/cm3" if rho < 2e-3 else "5052 2.68 g/cm3"))
    print("LID-TRAY-QMX-R2-DONE")
