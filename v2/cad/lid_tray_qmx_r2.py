#!/usr/bin/env python3
"""The QMX lid tray, revision r2 (MESHSAT-1357, S-63 and ENGINEERING-QUESTIONS EQ-24; stream w5tray, second pass of 27 to 28 Sep 2026).
It replaces the tray of 9 September 2026 (v2/cad/lid_bracket_qmx.py, released unchanged in v2/release/case-2026-09-27/lid-tray-qmx/ and
sheet 14), which was notched at one end while the unit has jacks on both end panels, and whose 95 x 63 x 25 no maker document backed.
Prototype design: nothing here has been made, printed, bought or fitted.

THE SECOND PASS. The first pass of r2 (recovered in v2/docs/records/w5tray/, module sha256 3e89a3ca4d3d1d3b) held the unit under ledges
and end lintels that were part of the tray and had it slid in from one end. Its checker found that the unit cannot be fitted: the lintel
at the entry end stands at the height of the unit's top face, and the knobs, the encoder shafts and the button actuators stand above that
face (blocking item B1). This pass keeps the first pass's unit figures, place, material, pads, lid plate and fixing, and changes HOW THE
UNIT GOES IN AND IS HELD: it is lowered into an open pocket from above, and a RETAINING FRAME is then screwed over it.

THE UNIT, from the maker (v2/vendor/qrp-labs/):
  * the enclosure is "95 x 63 x 25mm without protrusions", 220 g with the enclosure (qmx-product-page-2026-09-27.txt, the product page of
    24 Sep 2026; assembly manual 1.04r page 3, qmx-assembly-1_04r-pages-1-3-20-21-75-78.pdf); left and right end panels held by eight
    "small black countersunk screws" (pages 76 and 77), four self-adhesive rubber feet whose fitting the maker calls optional (page 77),
    two knobs listed as "15mm" (page 21) and held by grub screws with "a small gap" to the top face (page 77);
  * the left panel carries Paddle, Audio and DC, the right panel RF (BNC), PTT and USB-C (operating manual 1_04_004 pages 7 and 8); the
    VOL and TUNE encoders and two buttons sit along one long edge of the top face and the LCD window in its middle (page 13);
  * where each jack sits is SCALED from those undimensioned figures (v2/vendor/qrp-labs/measure_qmx_figures.py, qmx-figures.out: the
    figures come out at the maker's 63 x 25 within 0.4 percent) and cross-checked on the maker's photograph of the right panel: the RF jack
    reads 12.1 from the knob edge on the figure and 8.3 on the photograph, so the tray takes every jack over the range of both, widened by
    0.5 (JACK_RANGE); INFERRED, not a maker dimension;
  * what stands PROUD of the enclosure is not dimensioned by the maker either; PROUD below lists it as read from the maker's photographs
    (assembly manual page 77, photographs 13 and 15 of the sibling QCX-mini in the same enclosure family, and the right-panel product
    photograph), each INFERRED: the knobs, the encoder shafts under them, the two button actuators, the BNC jack's barrel and nut and the
    bushings of the 3.5 mm jacks. The knob height is 11.6 (11.1 on the print, +5 percent for the knob standing behind the photographed face).

WHAT THE SET DOES (the session's choices under the owner's standing rule of 26 Sep 2026, recorded in the r2 README with reasons and
reversals): the unit lies top face out, its knob edge west and its right panel toward the hinge; BOTH end panels are open over their whole
height above a 1.5 mm sill, and under the RF jack the sill is cut down to the floor; the unit is lowered from above into a pocket of two
long walls (buttressed by posts, on a flange as thick as the sills) and two sills, onto two PORON 4701-30 pads; the retaining frame, a flat printed ring, is laid on the wall
tops and held by six M3 button-head screws into square nuts in the posts; its ledges press on the unit's top face along the back edge, the
knob edge (clear of both knobs and their finger room) and both ends, and the pads press the unit up against them. Both printed parts are
Prusament PC Blend (HDT 113 C at 0.45 MPa and 93 C at 1.80 MPa, where the PETG of r1 is 68 C, under E3-S's +71 C storage); neither has an
overhang or a bridge but the six nut slots (5.8 wide). The tray is screwed with ten flush M3 countersunk screws into a 2.0 mm 5052-H32
aluminium lid plate tapped through, which is bonded to the lid's unribbed inner face with 3M DP8005 (no hole in the case, ruling of
7 Sep 2026).

FRAMES. Part frame: x along the unit's length, +x toward the RIGHT panel (RF, PTT, USB), which faces the hinge (case +Y); y across, +y
toward the unit's BACK long edge (case +X, east), -y toward the knob edge (west); z up from the lid plate's face, the pocket opening
toward +z (toward the face plate with the lid closed). Case frame with the lid closed: X = PLACE_X + y, Y = PLACE_Y + x,
Z = ceiling - BOND - PLATE_T - z (a proper rotation).

ONE TABLE. elements() lists every solid of the set as a named box (or a named cylinder, carried with its bounding box) in the part frame.
build_tray() and build_frame() build the solids from that table, and v2/cad/lid_tray_qmx_r2_check.py computes the insertion clearances and
the face room from the same table without the CAD set; with --solids the check proves on the built solids that the table is what was built.
Importing this module builds nothing; build_*() need build123d (v2/cad/requirements-cad.lock). Usage: lid_tray_qmx_r2.py <out dir>."""
import os, sys, math

# ---------------------------------------------------------------- the unit (maker figures; SCALED and INFERRED ones marked)
UNIT = (95.0, 63.0, 25.0)                  # length, width, height without protrusions (maker)
UNIT_MASS = 0.220                          # kg with the enclosure (maker)
UNIT_TOL = 0.2                             # on each overall dimension of the enclosure: not stated by the maker (INFERRED)
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
KNOB_D = 18.0                              # the knob class the set keeps clear: the "15mm" knob and its skirt, 17.6 on the photograph (INFERRED)
KNOB_H = 11.6                              # knob top above the top face (INFERRED, above)
FINGER = 6.0                               # finger room kept free of the frame around each knob
BUTTONS = [(39.9, 10.3), (55.0, 10.3)]     # u from the left end face, v from the knob edge (SCALED), 4.3 openings
LCD = (15.5, 79.5, 16.3, 30.5)             # u0, u1 from the left end face; w0, w1 from the BACK edge (SCALED)
# what stands proud of the enclosure (INFERRED from the maker's photographs; the maker dimensions none of it). Heights are above the face
# the item stands on; PROUD_TOL widens every item's size and place in the insertion envelope.
SHAFT = dict(d=6.0, h=8.0)                 # the encoder shaft with its knob off (photograph 13)
BUTTON_ACT = dict(d=4.3, h=2.0)            # a button actuator in its 4.3 opening, about 2 above the top face (photograph 15)
BNC = dict(across_corners=16.5, out=14.0)  # the RF jack: its nut 9/16 in across flats (14.29), 16.50 across corners, and its barrel,
                                           # 14 beyond the right panel's face (the right-panel photograph; photograph 13)
BUSHING = dict(d=8.0, out=3.0)             # the bushing and ring nut of a 3.5 mm jack (the right-panel photograph)
PROUD_TOL = 0.5
FEET_FITTED = False                        # the four self-adhesive feet are NOT fitted (the maker calls them optional): the unit's bottom is flat

# ---------------------------------------------------------------- the stack and the parts
BOND = 0.20                                # DP8005 bond line: its .008 in microspheres set it (3m-scotch-weld-dp8005.pdf, page 3)
PLATE_T = 2.0                              # the aluminium lid plate
FLOOR = 1.6                                # tray floor
G_B = 0.5                                  # the unit's bottom above the floor top, nominal (it rides on the pads, pressed up to the frame's ledges)
CLR = 0.4                                  # clearance to the unit at the side walls and at the sill faces (0.3 in the first pass: the unit at its
                                           # largest then kept only the printed part's own tolerance to a wall)
WALL = 4.0
WALL_END = 1.5                             # each long wall stops this far short of the unit's end faces, so no wall stands beside a plug
POST = dict(x=(-41.0, -20.5, 0.0, 20.5, 41.0), w=10.0, depth=8.0)  # the posts that buttress both walls, full height, outside them
FRAME_T = 3.0                              # the retaining frame, a flat ring
LEDGE_BACK = 4.0                           # the frame's reach inward from the back wall's inner face (nothing on the top face within 16.3 of the back edge)
LEDGE_FRONT = 3.0                          # the same from the knob-edge wall, clear of the knobs
LEDGE_END = 3.0                            # the frame's reach over each end of the top face (no control within 6.4 of an end face)
LINTEL_W = 3.0                             # and its reach beyond each end face
SILL_H = 1.5                               # the sills above the unit's bottom face: below every plug the jacks admit
END_L = 8.0                                # the end blocks, along x
PLUG_GAP = 0.5                             # kept between an admitted plug body and the tray under or beside it
PAD = dict(size=(24.0, 20.0), x=(-22.0, 22.0), material="Rogers PORON 4701-30 Very Soft, 320 kg/m3, 3.18 mm (0.125 in), black (04)",
           t=3.18, t_tol=0.10, cfd25_kpa=(21.0, 55.0))   # through-windows in the floor; the pads stand on the plate (rogers-poron-4701-30-very-soft.pdf)
CSK = dict(d_head=6.72, k=1.86, hole=3.4)  # M3 countersunk hex socket, ISO 10642 class (head 6.72 and 1.86 at most; standard not held, INFERRED)
SCREW = "M3 x 5 countersunk hex socket, ISO 10642 class, A2"
TAP = 2.5                                  # tap drill for M3 in the lid plate
BH = dict(d_head=5.7, k=1.65, hole=3.4, length=10.0)   # M3 x 10 button head hex socket, ISO 7380-1 class (head 5.7 and 1.65 at most; INFERRED)
FRAME_SCREW = "M3 x 10 button head hex socket, ISO 7380-1 class, A2"
NUT = dict(s=5.5, m=1.8, slot_w=5.8, slot_h=2.1, roof=3.0)       # M3 square nut, DIN 562 class (5.5 across, 1.8 thick; INFERRED); its slot in a post
FRAME_NUT = "M3 square nut, DIN 562 class, A2"
BOSS_R = 4.0                               # the bosses of the ten tray screws

# derived numbers (all in the part frame)
U0 = UNIT[0] / 2                           # 47.5: the unit's end faces at x = +-U0
SIDE_IN = UNIT[1] / 2 + CLR                # 31.9: wall inner faces
SIDE_OUT = SIDE_IN + WALL                  # 35.9: wall outer faces
BASE_Y = SIDE_OUT + POST["depth"]          # 43.9: the floor's, the frame's and the plate's half width
FACE_X = U0 + CLR                          # 47.9: the sill faces
BASE_X = FACE_X + END_L                    # 55.9: the floor's and the plate's half length
WALL_X = U0 - WALL_END                     # 46.0: the long walls' ends
FRAME_X = U0 + LINTEL_W                    # 50.5: the frame's half length
Z_UB = FLOOR + G_B                         # 2.1: the unit's bottom face
Z_UT = Z_UB + UNIT[2]                      # 27.1: its top face, the wall and post tops, and the frame's underside
Z_TOP = Z_UT + FRAME_T                     # 30.1: the frame's top face
Z_HEAD = Z_TOP + BH["k"]                   # 31.75: the six frame screw heads
Z_SILL = Z_UB + SILL_H                     # 3.6: the sills' and the screw bosses' top
KNOB_X = U0 - KNOB_U                       # 26.1: encoder centres at x = +-26.1
KNOB_Y = -UNIT[1] / 2 + KNOB_V             # -17.8
KNOB_ZONE = (KNOB_X - KNOB_D / 2 - FINGER, KNOB_X + KNOB_D / 2 + FINGER)   # |x| over which the frame keeps off the knob edge
FRONT_SEGMENTS = [(-FRAME_X, -KNOB_ZONE[1]), (-KNOB_ZONE[0], KNOB_ZONE[0]), (KNOB_ZONE[1], FRAME_X)]
POST_Y = SIDE_OUT + POST["depth"] / 2      # 39.9: the posts' and every screw's line
FRAME_SCREWS = [(x, s * POST_Y) for x in (POST["x"][0], POST["x"][2], POST["x"][4]) for s in (-1, 1)]   # six, in the posts at x -41, 0, +41
SCREWS_BOSS = [(sx * 30.75, sy * POST_Y) for sx in (-1, 1) for sy in (-1, 1)]                           # tray fixings between the posts
SCREWS_END = [(sx * (FACE_X + END_L / 2), y) for sx in (-1, 1) for y in (-POST_Y, 0.0, POST_Y)]         # and through both end blocks
PLATE_HOLES = SCREWS_BOSS + SCREWS_END
NUT_Z = (Z_UT - NUT["roof"] - NUT["slot_h"], Z_UT - NUT["roof"])          # 22.0 .. 24.1: the nut slots
SIZE = (2 * BASE_X, 2 * BASE_Y, Z_TOP)     # 111.8 x 87.8 x 30.1: the tray with its frame, over the base
# place with the lid closed (case frame): the east edge stays at panel1450.QMX_TRAY_X[1], 171.0, so C5's M19 is unchanged; the tray grows
# west (the lid's ceiling is free there: the tablet bracket keeps the west third). PLACE_Y is the r1 tray's centre along Y (scene.py QY 10.0).
EAST_EDGE_X = 171.0
PLACE_X = EAST_EDGE_X - BASE_Y             # 127.1: the unit's centre across the case
PLACE_Y = 10.0
SPAN_X = (PLACE_X - BASE_Y, PLACE_X + BASE_Y)
SPAN_Y = (PLACE_Y - BASE_X, PLACE_Y + BASE_X)


def under_plug(name):
    """The top of the tray under a jack's plug: the floor under the RF jack (its sill is cut away), the sill under every other."""
    return FLOOR if name == "RF" else Z_SILL


def admitted_radius(name):
    """The largest plug body radius the set admits about a jack's axis at the worst of its scaled place: the plug clears the top of the
    tray under it by PLUG_GAP; nothing else of the tray lies in front of an end panel, and the frame stands above the unit's top face."""
    j = JACKS[name]
    return Z_UB + min(j["h"]) - JACK_RANGE - under_plug(name) - PLUG_GAP


def rf_notch():
    """The cut in the hinge-end sill under the RF jack, in y: the admitted RF plug over its scaled place, PLUG_GAP each side."""
    j = JACKS["RF"]; r = admitted_radius("RF")
    return (-UNIT[1] / 2 + min(j["v"]) - JACK_RANGE - r - PLUG_GAP, -UNIT[1] / 2 + max(j["v"]) + JACK_RANGE + r + PLUG_GAP)


def to_case(x, y, ceiling):
    return (PLACE_X + y, PLACE_Y + x, ceiling - BOND - PLATE_T)


# ---------------------------------------------------------------- the one table of solids
def _e(part, name, x0, x1, y0, y1, z0, z1, shape="box", seat=()):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1))
    return dict(part=part, name=name, box=(round(x0, 4), round(x1, 4), round(y0, 4), round(y1, 4), round(z0, 4), round(z1, 4)), shape=shape, seat=tuple(seat))


def elements():
    """Every solid of the set, the unit and what stands proud of it, as named boxes in the part frame (a cylinder about z is carried as
    its bounding box, shape "cyl_z"). part is one of tray, frame, screw, plate, pad, unit, proud. seat names the parts a solid is
    DESIGNED to touch when everything is in place (the unit under the frame's ledges, the frame on the wall tops), so a check of
    clearances knows a designed contact from a collision."""
    E = []
    n0, n1 = rf_notch()
    E.append(_e("plate", "lid plate", -BASE_X, BASE_X, -BASE_Y, BASE_Y, -PLATE_T, 0.0))
    E.append(_e("tray", "floor", -BASE_X, BASE_X, -BASE_Y, BASE_Y, 0.0, FLOOR, seat=("unit",)))
    for sy, nm in ((-1, "knob-edge"), (1, "back")):
        E.append(_e("tray", "%s wall" % nm, -WALL_X, WALL_X, sy * SIDE_IN, sy * SIDE_OUT, 0.0, Z_UT, seat=("frame",)))
        for px in POST["x"]:
            E.append(_e("tray", "%s post at x %+.1f" % (nm, px), px - POST["w"] / 2, px + POST["w"] / 2, sy * SIDE_OUT, sy * BASE_Y, 0.0, Z_UT, seat=("frame",)))
        E.append(_e("tray", "%s flange" % nm, -BASE_X, BASE_X, sy * SIDE_OUT, sy * BASE_Y, 0.0, Z_SILL))
    E.append(_e("tray", "front-end sill (left panel)", -BASE_X, -FACE_X, -BASE_Y, BASE_Y, 0.0, Z_SILL))
    E.append(_e("tray", "hinge-end sill, knob-edge corner", FACE_X, BASE_X, -BASE_Y, n0, 0.0, Z_SILL))
    E.append(_e("tray", "hinge-end sill, from the PTT jack east", FACE_X, BASE_X, n1, BASE_Y, 0.0, Z_SILL))
    for x, y in PLATE_HOLES:
        E.append(_e("tray", "screw boss at (%+.2f, %+.1f)" % (x, y), x - BOSS_R, x + BOSS_R, y - BOSS_R, y + BOSS_R, 0.0, Z_SILL, shape="cyl_z"))
    for px in PAD["x"]:
        E.append(_e("pad", "PORON pad at x %+.0f" % px, px - PAD["size"][0] / 2, px + PAD["size"][0] / 2, -PAD["size"][1] / 2, PAD["size"][1] / 2, 0.0, Z_UB, seat=("unit",)))
    # the retaining frame: two rails over the posts, the ledges over the unit's long edges, a bar over each end
    E.append(_e("frame", "frame back rail and ledge", -FRAME_X, FRAME_X, SIDE_IN - LEDGE_BACK, BASE_Y, Z_UT, Z_TOP, seat=("unit", "tray")))
    E.append(_e("frame", "frame knob-edge rail", -FRAME_X, FRAME_X, -BASE_Y, -SIDE_OUT, Z_UT, Z_TOP, seat=("tray",)))
    for k, (x0, x1) in enumerate(FRONT_SEGMENTS):
        E.append(_e("frame", "frame knob-edge ledge %d" % (k + 1), x0, x1, -SIDE_OUT, -SIDE_IN + LEDGE_FRONT, Z_UT, Z_TOP, seat=("unit", "tray")))
    for sx, nm in ((-1, "front"), (1, "hinge")):
        E.append(_e("frame", "frame %s-end bar" % nm, sx * (U0 - LEDGE_END), sx * FRAME_X, -SIDE_IN + LEDGE_FRONT, SIDE_IN - LEDGE_BACK, Z_UT, Z_TOP, seat=("unit",)))
    for x, y in FRAME_SCREWS:
        E.append(_e("screw", "frame screw head at (%+.0f, %+.1f)" % (x, y), x - BH["d_head"] / 2, x + BH["d_head"] / 2, y - BH["d_head"] / 2, y + BH["d_head"] / 2,
                    Z_TOP, Z_HEAD, shape="cyl_z", seat=("frame",)))
    # the unit, at its nominal size and place, and what stands proud of it
    E.append(_e("unit", "unit body", -U0, U0, -UNIT[1] / 2, UNIT[1] / 2, Z_UB, Z_UT, seat=("frame", "pad")))
    for sx, nm in ((-1, "VOL"), (1, "TUNE")):
        E.append(_e("proud", "%s knob" % nm, sx * KNOB_X - KNOB_D / 2, sx * KNOB_X + KNOB_D / 2, KNOB_Y - KNOB_D / 2, KNOB_Y + KNOB_D / 2, Z_UT, Z_UT + KNOB_H, shape="cyl_z"))
    for k, (u, v) in enumerate(BUTTONS):
        bx, by = u - U0, -UNIT[1] / 2 + v
        E.append(_e("proud", "button actuator %d" % (k + 1), bx - BUTTON_ACT["d"] / 2, bx + BUTTON_ACT["d"] / 2, by - BUTTON_ACT["d"] / 2, by + BUTTON_ACT["d"] / 2,
                    Z_UT, Z_UT + BUTTON_ACT["h"], shape="cyl_z"))
    for nm, j in JACKS.items():
        if nm == "RF": r, out = BNC["across_corners"] / 2, BNC["out"]
        elif nm in ("Audio", "Paddle", "PTT"): r, out = BUSHING["d"] / 2, BUSHING["out"]
        else: continue                                                          # the DC jack and the USB-C socket end flush with their panel
        sx = 1 if j["panel"] == "R" else -1
        y0, y1 = -UNIT[1] / 2 + min(j["v"]) - JACK_RANGE - r, -UNIT[1] / 2 + max(j["v"]) + JACK_RANGE + r
        z0, z1 = Z_UB + min(j["h"]) - JACK_RANGE - r, Z_UB + max(j["h"]) + JACK_RANGE + r
        E.append(_e("proud", "%s jack, proud of the %s panel" % (nm, "right" if sx > 0 else "left"), sx * U0, sx * (U0 + out), y0, y1, z0, z1))   # over its scaled place
    return E


def parts(E, *names):
    return [e for e in E if e["part"] in names]


# ---------------------------------------------------------------- the solids (build123d)
def _bd():
    import build123d as bd
    return bd


def _box(bd, x0, x1, y0, y1, z0, z1):
    return bd.Box(x1 - x0, y1 - y0, z1 - z0).moved(bd.Location(bd.Vector((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))


def _solid(bd, e):
    """One element of the table as a solid: a box, or the cylinder its bounding box carries."""
    x0, x1, y0, y1, z0, z1 = e["box"]
    if e["shape"] == "cyl_z":
        return bd.Cylinder((x1 - x0) / 2, z1 - z0).moved(bd.Location(bd.Vector((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))
    return _box(bd, x0, x1, y0, y1, z0, z1)


def _union(bd, els):
    s = None
    for e in els:
        p = _solid(bd, e)
        s = p if s is None else s + p
    return s


def _csk(bd, x, y, z_top, depth):
    """A countersunk M3 hole from z_top down through `depth` (90 degree cone to CSK d_head at the top)."""
    cone_h = (CSK["d_head"] - CSK["hole"]) / 2
    cone = bd.Cone(CSK["hole"] / 2, CSK["d_head"] / 2, cone_h).moved(bd.Location(bd.Vector(x, y, z_top - cone_h / 2)))   # narrow end down
    shaft = bd.Cylinder(CSK["hole"] / 2, depth + 2).moved(bd.Location(bd.Vector(x, y, z_top - depth / 2)))
    head_room = bd.Cylinder(CSK["d_head"] / 2, 2.0).moved(bd.Location(bd.Vector(x, y, z_top + 1.0)))
    return cone + shaft + head_room


def build_tray():
    """The tray: the table's tray solids, less the pad windows, the ten countersunk holes, and in the six screwed posts the screw hole
    and the nut slot, which opens on the post's outer face."""
    bd = _bd()
    t = _union(bd, parts(elements(), "tray"))
    for px in PAD["x"]:
        t -= _box(bd, px - PAD["size"][0] / 2, px + PAD["size"][0] / 2, -PAD["size"][1] / 2, PAD["size"][1] / 2, -1, FLOOR + 1)
    for x, y in PLATE_HOLES:
        t -= _csk(bd, x, y, Z_SILL, Z_SILL)
    hole_bottom = Z_TOP - BH["length"] - 2.0                                   # 2.0 of room under the screw's tip
    for x, y in FRAME_SCREWS:
        sy = 1 if y > 0 else -1
        t -= bd.Cylinder(BH["hole"] / 2, Z_UT + 1 - hole_bottom).moved(bd.Location(bd.Vector(x, y, (Z_UT + 1 + hole_bottom) / 2)))
        t -= _box(bd, x - NUT["slot_w"] / 2, x + NUT["slot_w"] / 2, *sorted((sy * (POST_Y - NUT["slot_w"] / 2), sy * (BASE_Y + 1))), NUT_Z[0], NUT_Z[1])
    return t


def build_frame():
    """The retaining frame: the table's frame solids with six plain holes; flat, printed with either face on the bed."""
    bd = _bd()
    f = _union(bd, parts(elements(), "frame"))
    for x, y in FRAME_SCREWS:
        f -= bd.Cylinder(BH["hole"] / 2, FRAME_T + 2).moved(bd.Location(bd.Vector(x, y, Z_UT + FRAME_T / 2)))
    return f


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
    tray, frame, plate = build_tray(), build_frame(), build_plate()
    bd.export_step(tray, os.path.join(OUT, "lid-tray-qmx-r2.step")); bd.export_stl(tray, os.path.join(OUT, "lid-tray-qmx-r2.stl"))
    bd.export_step(frame, os.path.join(OUT, "lid-tray-qmx-r2-frame.step")); bd.export_stl(frame, os.path.join(OUT, "lid-tray-qmx-r2-frame.stl"))
    bd.export_step(plate, os.path.join(OUT, "lid-plate-qmx-r2.step")); write_plate_dxf(os.path.join(OUT, "lid-plate-qmx-r2.dxf"))
    for nm, s, rho in (("tray", tray, 1.22e-3), ("frame", frame, 1.22e-3), ("lid plate", plate, 2.68e-3)):
        b = s.bounding_box()
        print("%-9s %6.1f x %5.1f x %5.1f mm, %8.0f mm3, %5.1f g (%s)" % (nm, b.size.X, b.size.Y, b.size.Z, s.volume, s.volume * rho,
              "PC Blend 1.22 g/cm3" if rho < 2e-3 else "5052 2.68 g/cm3"))
    print("LID-TRAY-QMX-R2-DONE")
