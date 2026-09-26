#!/usr/bin/env python3
"""MESHSAT-1357 case margins, part 2 (26 Sep 2026, revised six times the same day after independent checks): where the Peli
1450PF frame can come to rest in the 1450 base, why no face mounting referenced to that rest holds, the setting legs that give
the frame a designed height (fixed to the frame's ring and placed by the frame's own centring), every case-dependent margin of
the chosen arrangement across its whole range, the connector plate on the back wall with the full ruled connector set, and the
ruled gas-discharge arrestors as the antenna bulkheads on one RF entry plate per end wall, with the route of their jumpers to the
dock strip's float clamps.

Stdlib only, runs in about a second, runner-safe; nothing is read from disk, every constant carries its source:
  STEP  faces of v2/vendor/peli/1450/1451-931-bottom.STEP and 1450-panel-frame.STEP (unit INCH, x 25.4), read with
        v2/vendor/peli/step_faces.py; entity ids beside each number (case frame: X = STEP x, Y = STEP z (sign INFERRED),
        Z = STEP y for the base; the frame STEP's own z is its height, its x and y map to case X and Y).
  DXF   v2/vendor/peli/1450/1451-931-customer-drawing.dxf (sheet at 1:3): top view hinge fairings #4985/#4991/#4992/#5071/
        #5107/#5116, section A-A cut line #3130 and hatch #7590, end view back features #6704/#7105/#7106/#7110, end view
        features at Y 0 and +-79.0 (ellipses, semi-axes 3.05 x 4.47 about Z 92.4), section B-B hatch #7866.
  SHEET Peli 1450 panel frame instruction sheet 1453-314-000 rev A (v2/vendor/peli/1450/1450_pf.pdf): tolerance
        block +-0.76 on one-decimal mm; 378.4 x 263.1 x 17.5; ten inserts on 358.1 x 242.3.
  GLN   Glenair sheets in v2/vendor/d38999/ (233-370 page C-15, D38999/20 page 30, 233-340 page C-4: the G6 plug is
        1.280 (32.51) max across; M85049/38 (glenair-as85049-38.pdf) Table I shell 13: E max 1.157 (29.4)); flange and
        hole figures as v2/ecad/tools/case_wall_cutouts.py:10-14 quotes them.
  AMPH  Amphenol MIL-DTL-38999 Series III catalogue (v2/vendor/d38999/amphenol-d38999-iii-federal.pdf), catalogue page 52 (PDF page 51): the
        D38999/26 straight plug, Q dia max 1.157 (29.4) for shell 13 and 1.280 (32.5) for shell 15.
  BUL   Bulgin sheets: v2/vendor/bulgin/bulgin-px0833-sealed-rj45-coupler.pdf (PX0833), and the two filed with this
        document (PXP4043 micro-B rear panel mount, PXP4043/C C-type), fetched from bulgin.com 26 Sep 2026.
  POLY  PolyPhaser GTH-SFF-AL sheet (v2/vendor/polyphaser/polyphaser-gth-sff-al-sma-surge-protector.pdf): 2.2 x 0.9 x 1.2 in
        (55 x 23 x 31 mm) max, 0.25 lb; drawing rev B page 3: 2.18 overall, .47 of 5/8-24UNEF-2A thread, .30 SMA jack on the
        thread side, .35 SMA jack on the body side, O-ring, split lock washer and hex nut, crimp ring terminal for the ground
        wire; leading dimensions in inches, .XX +-.02 (0.51), and "ALL DIMENSIONS SHOWN ARE FOR REFERENCE ONLY" in the title
        block. Not dimensioned, scaled from the page rendered at 600 dpi (20.95 px/mm on the 2.18): the O-ring on the thread's
        root stands 0.63 proud of the body's face, inside the .47; the hex nut 19.1 across its flats (3/4 in) and 3.4 thick, the
        lock washer 20.5 across and 1.3 thick.
  AMP   Amphenol Connex 132170 drawing rev D (v2/vendor/rf/): the coupler the tree carries at 29f00554, retired by the arrestors.
  TREE  v2/ecad/tools/panel1450.py, gen_pcb_*.py, v2/docs/ASSEMBLY.md, v2/vendor/open-picks.txt (line numbers at main 29f00554).
  STD   ISO 7380 (button head length js15), ISO 965 6g (M3 major 2.874 to 2.980, M4 3.838 to 3.978, M6 5.794 min, M10 x 0.75
        9.838 min), ASME B1.1 class 2A (the drawing's 5/8-24UNEF-2A: major 0.6167 in (15.66) min) and MIL-DTL-17 (RG-316
        0.098 in): classes used, standards not held (INFERRED). A screw's largest major decides whether it passes a hole, its
        smallest how far the part it holds floats.
Allowances marked INFERRED are the session's, not a source's; the document CASE-MARGINS.md lists them and says which are stated
(a class a part is bought to, the kit's own drawing tolerances) and which unstated (below: UNSTATED). Each row's verdict is MET, NOT MET
or OPEN: OPEN when a named dependency decides it, or when it falls below its minimum with every allowance no source states taken twice
(the review of 26 Sep 2026, v2/docs/reviews/2026-09-26-foundation-progress-review.md section 4: a margin whose tolerances are not specified
is unknown). No verdict here says that a part fits, seals or aligns: nominal CAD establishes none of that."""
import math

# ------------------------------------------------------------------ Peli base (STEP 1451-931-bottom)
TW = 0.0349 / 0.9994                       # wall draft, normals of #1193/#1922/#172/#1851 (2.0 degrees)
HX0, HY0 = 186.97, 129.82                  # end and long wall planes at Z 0 (#1193 loc x 186.97; #172 loc z -129.82)
def hx(z): return HX0 + TW * z             # inner half-length at height z (above the fillet tangent, Z 15.32)
def hy(z): return HY0 + TW * z
FIL_R, FIL_T, FLAT_X, FLAT_Y = 15.88, 15.32, 171.64, 114.49   # floor fillet #355/#1295/#1211/#2244; flat floor #1321
SHOULDER, RIM = 101.04, 108.97             # #776 (up-facing ledge 0.51 wide) and #1637; DXF _D_7 108.97
RIMZ_X, RIMZ_Y = 191.01, 133.86            # rim zone inner faces at the shoulder (#850, #1689)
RIB_TOP, RIB_R0, RIB_TAN = 84.58, 0.762, math.tan(0.0218)     # rib cones r 0.03 in, half-angle 0.0218 rad (#1604, #229 ...)
RIB_AX_X, RIB_AX_Y = 189.93, 132.78        # rib axes: end walls x +-189.93 (#1604), long walls z +-132.78 (#229)
def rib_in(ax, z, top=RIB_TOP): return ax - (RIB_R0 + RIB_TAN * (top - z))   # innermost point of a rib at z <= top
def rib_proud_long(z): return hy(z) - rib_in(RIB_AX_Y, z) if z >= 27.0 else 0.0   # a long-wall rib's height off its wall
CORNER_R = 15.88                           # vertical corners #241/#1024/#595/#1345
LID_STEP, LID_WEB = 45.47, 44.45           # lid depth: STEP top #736 and DXF _D_6; pelican.com 1.75 in (capture 29 Mar 2026)
LID_OPEN = (186.94, 129.79)                # lid cavity at the parting plane (STEP top #410/#540, #1467/#1744): X half, and the smaller Y half (132.08 / 129.79)
WALL_T = 5.34                              # DXF B-B #7866 and A-A #7590: 5.34 (end and long walls)
OUT_CORNER_R = CORNER_R + WALL_T           # outer vertical corners concentric with the inner ones (INFERRED; the outer skin is an envelope block in the STEP)
FEAT_Z_LOW = 92.4 - 4.47                   # DXF end view: the features at Y 0, +-79.0 reach down to Z 87.93

# ------------------------------------------------------------------ Peli 1450PF frame (STEP 1450-panel-frame; frame z -8.76 .. 8.76)
F_OUT = dict(x=(189.18, 189.48, 189.29), y=(131.27, 131.57, 131.38))   # skirt at z -8.76 (#1, #3683), widest at z 0 (#3683/#6617), at the step z 5.46 (#1488)
FH, RING_UNDER, RING_T = 17.52, 8.13, 9.39 # #1 .. #5527; ring underside #1703 at z -0.63
F_SKIRT_IN = (183.34, 125.42)              # #5759/#4475, #3645/#2903 (straight to |Y| 107.90 / |X| 165.81, then R 17.53 #494 ...)
F_SKIRT_IN_R, F_SKIRT_IN_C = 17.53, (165.81, 107.90)
F_WIN = (174.83, 116.91)                   # window #1928, #1818; corners R 6.35 about (168.48, 110.56) (#63 ...)
F_WIN_R, F_WIN_C = 6.35, (168.48, 110.56)
F_OUT_R, F_OUT_C = 16.51, (172.68, 114.77) # outer corners #753/#3257 (drafted)
F_FLANGE = (184.35, 126.44)                # top flange above the gasket step (#3095, #3162)
INSERTS = [(179.07, 75.95), (0.0, 121.16), (139.45, 121.16)]   # insert bores through the ring (STEP), one quadrant; SHEET pattern 358.1 x 242.3

def frame_half(h, prof):
    """Half-width of the frame's outer face at height h above its bottom (prof = F_OUT['x'] or ['y']); None above the gasket step."""
    bot, mid, step = prof
    if h <= 8.76: return bot + (mid - bot) * h / 8.76
    if h <= 14.22: return mid - (mid - step) * (h - 8.76) / 5.46
    return None

# ------------------------------------------------------------------ allowances
T_SHEET = 0.76      # SHEET, one-decimal mm (frame height 17.5, outline 378.4 x 263.1, window, insert pattern): VERIFIED
T_CASE_Z = 0.76     # a case height (rib top, rim, shoulder) against the floor under the stack: the SHEET class applied to the case, INFERRED
T_FLOOR = 0.76      # floor point to floor point (a leg's foot against the stack's pads): INFERRED, the M6 allowance
T_WALL = 0.38       # per wall of the case interior: INFERRED (half the SHEET class)
T_LEG = 0.10        # setting leg height, a drawing tolerance of the kit's own part
T_PLATE = 0.13      # 3.0 mm plate, EN 485-4 class, INFERRED (standard not held)
T_REBATE = 0.10     # rebate depth and rebate line, drawing tolerance
T_OUTLINE = 0.10    # plate outline and machined hole positions, drawing tolerance
T_CENTRE = 0.20     # frame centred by wedge pairs at the build (C6), INFERRED
SCREW_632 = 0.1380 * 25.4                  # 6-32 UNC major 0.1380 in (3.505), the basic size, which no class 2A or 3A screw exceeds
SCREW_632_MIN = 0.1312 * 25.4              # 6-32 UNC-2A major 0.1312 in (3.332) at least (ASME B1.1 class, standard not held, INFERRED)
FACE_HOLE = 4.6                            # C1: the face plate's holes for the 6-32 screws (a 4.6 drill)
T_HOLE = (FACE_HOLE - SCREW_632) / 2       # the largest screw passes its hole with this to spare
T_FLOAT = (FACE_HOLE - SCREW_632_MIN) / 2  # the plate floats this far on the smallest
PAN_632 = 0.270 * 25.4 / 2                 # 6-32 pan head max diameter 0.270 in (ASME B18.6.3 class, standard not held, INFERRED)
T_STACK = 1.00      # stack placement in plan (the dock strip is laid on its VHB pads by hand), INFERRED
T_JACK = 0.30       # a wall hole or a plate marked from the 1:1 template, INFERRED
T_JIG = 0.30        # a leg placed on the frame by the printed locator in the window corner: print 0.20 plus the leg's fit 0.10, INFERRED
T_SKIRT = 0.38      # the skirt's inner face per side against the frame's centre (the SHEET class on an undimensioned face), INFERRED
T_BACKER = 0.20     # the backer ring on the plate's standoffs, INFERRED
T_MACH = 0.10       # positions machined into a plate, INFERRED
T_LID = 0.38        # the closed lid's cavity against the base (tongue in groove), INFERRED
LAM, VHB_T, BOW = 0.16, 0.11, 0.30         # JLC 1.6 +-10 % (fabricator note :29), 3M VHB 5952 1.1 +-10 %, B bow INFERRED
BOARD_TOLS = [("laminate E", LAM), ("laminate A", LAM), ("laminate B", LAM), ("VHB 5952", VHB_T), ("B bow (INFERRED)", BOW)]
LEG_IN_CASE = [("frame centring", T_CENTRE), ("window per side (SHEET)", T_SHEET / 2), ("leg locator on the window", T_JIG)]   # a leg against the case centre

# ------------------------------------------------------------------ design numbers
XEN_H, HEATSINK = 28.66, 21.0              # panel1450.py:44, :36
B_UNDER = 47.9 + 1.1                       # panel1450.py:23 (top copper 49.5 less 1.6) plus the VHB pads lifting the stack (C1 follow-on (a), ASSEMBLY.md:47)
B_TOP = 49.5 + 1.1
B_OUT = (165.0, 100.0)                     # panel1450.py:22
A_EDGE_Y = 80.0                            # gen_pcb_a.py:16 (BOARD_W 160, centred): A22 spans Y -80 .. 80
U51_H = 1.6                                # U51 (LQFP-100, Y 68.3 .. 85.8) on B16's underside by the back edge (A06); body height INFERRED
PLATE = (377.2, 263.0, 3.0)                # C1 (0.8 narrower in X than the first issue's 378.0, for the float the 4.6 holes give the smallest 6-32)
REBATE = 2.0                               # C1: the band outside REB_IN is rebated 2.0 from the top
REB_IN = (368.0, 253.0)                    # C1: the full-thickness face (the previous issue's was 367.0 x 251.0)
TRAY = 28.0                                # v2/cad/lid_bracket_qmx.py:13-16
PACK_EAST = 178.65                         # the 4S3P block's east face (case_margins.out, M4; west face X 122.0, A06)
PACK_TOP = B_UNDER - (3.32 + 1.1)          # M6: the block's top under B16's underside
MIN_FACE, MIN_MECH = 2.0, 1.0              # z_budget.py:16; the document's rigid-to-rigid minimum
MIN_WEB, MIN_BAND = 2.0, 3.0                # wall web between two holes (twice the rigid minimum) and a hole's gasket band to the plate edge (1.5 x the 2.0 gasket): INFERRED
# the setting legs (C6): the pad top is the lowest that keeps the plate's underside 0.10 above the highest the shoulder can stand
LEG_TOP = round(SHOULDER + T_CASE_Z + 0.10 - RING_T + (T_FLOOR + T_LEG + T_SHEET), 2)
LEG_Y = (106.4, 112.4); LEG_X = (175.4, 180.17); FOOT_X = (156.0, 169.0); RELIEF = 2.5   # column 0.20 inboard of the previous issue's (M21d)

# ------------------------------------------------------------------ helpers
# The review of 26 Sep 2026 (v2/docs/reviews/2026-09-26-foundation-progress-review.md, section 4): Peli geometry and stated tolerances are
# the design basis, and a margin whose tolerances are not specified is unknown. Stated: the frame sheet's class, makers' sheets, the kit's own
# drawing tolerances and the classes a pick is bought to. Unstated: every allowance on Peli's case (Peli publishes none for it) and every
# build allowance (placement by hand, marking from the template, centring, the locator, ties, a gasket's compression, board bow).
UNSTATED = ("case per wall", "case per side", "case Z", "rib per wall", "lid per wall", "lid on the base", "rim against the stack floor",
            "shoulder against the floor", "floor under the leg", "floor flatness", "wall thickness", "wall -0.76", "skirt per side",
            "skirt below the ring", "ring 9.39", "rear face worst", "gasket", "stack placement", "strip placement", "pack placed by hand",
            "frame centring", "leg locator on the window", "hole marking", "plate marking", "wall hole marked from the template",
            "bundle ties", "backer on the plate", "B bow", "thread (POLY", "thread and inner jack (POLY", "O-ring")
# the arrestor's drawing marks every dimension "for reference only", as Peli's does, so its .XX +-0.51 is taken as unstated
def unstated(label, t):
    """The part of an allowance that no source states (the window's share of a leg's placement is the frame sheet's, and stated)."""
    if label.startswith("leg against the case centre"): return T_CENTRE + T_JIG
    if label.startswith("leg locator and window"): return T_JIG
    return t if label.startswith(UNSTATED) else 0.0

ROWS = []
def row(key, label, minimum, nominal, tols, note="", worst=None, rss=None, wc2=None, open_=None):
    """Verdict: NOT MET below the minimum at the worst; OPEN when a named dependency decides it (open_) or when it falls below the minimum
    with every unstated allowance taken twice (wc2, the session's sensitivity reading of the review's rule); MET otherwise."""
    if worst is None: worst = nominal - sum(t for _, t in tols)
    if rss is None: rss = math.sqrt(sum(t * t for _, t in tols))
    if wc2 is None: wc2 = worst - sum(unstated(l, t) for l, t in tols)
    if open_: ok = "OPEN"
    elif worst < minimum - 1e-9: ok = "NOT MET"
    elif wc2 < minimum - 1e-9: ok = "OPEN"
    else: ok = "MET"
    r = dict(key=key, label=label, min=minimum, nom=nominal, wc=worst, rss_low=nominal - rss, wc2=wc2, ok=ok,
             note="; ".join(s for s in (note, open_) if s))
    ROWS.append(r); return r

def seat(u, c, dtop, walls_only=False, ribs="end"):
    """Highest frame-bottom Z at which the frame first touches a rib or a wall while lowered into the case.
    u: frame undersize per side (+ = smaller); c: case interior per wall (+ = larger); dtop: rib top offset."""
    top = RIB_TOP + dtop
    def touch(zb):
        for i in range(0, 1423, 2):
            h = i / 100.0; z = zb + h
            for axis in ("x", "y"):
                fh = frame_half(h, F_OUT[axis])
                if fh is None: continue
                fh -= u
                wall = (hx(z) if axis == "x" else hy(z)) + c
                if fh >= wall: return "%s wall at Z %.2f" % ("end" if axis == "x" else "long", z)
                if walls_only or z > top + 1e-9: continue
                if axis == "x" or ribs == "all":
                    r = rib_in(RIB_AX_X if axis == "x" else RIB_AX_Y, z, top) + c
                    if fh >= r: return "%s rib at Z %.2f (%s)" % ("end-wall" if axis == "x" else "long-wall", z, "top cap" if abs(z - top) < 0.011 else "flank")
        return None
    zb = top + 0.5
    while zb > 20.0 and not touch(zb): zb -= 0.25             # coarse, then back up and step 0.01
    zb += 0.25
    while zb > 20.0:
        why = touch(zb)
        if why: return round(zb, 2), why
        zb -= 0.01
    return None, "no stop above Z 20"

if __name__ == "__main__":
    print("== (A) every feature that could stop the 1450PF going lower")
    print("  rib catch at the rib top, frame and case nominal: end walls %+.3f, long walls %+.3f (positive = the rib is under the frame's bottom edge)" % (
        F_OUT["x"][0] - rib_in(RIB_AX_X, RIB_TOP), F_OUT["y"][0] - rib_in(RIB_AX_Y, RIB_TOP)))
    print("  rib stands proud of its wall by %.2f at its top: the frame's bottom edge must land in that band, and the frame outline and" % (hx(RIB_TOP) - rib_in(RIB_AX_X, RIB_TOP)))
    print("  the case interior each move it by +-%.2f per side, so no frame size is caught by the ribs across both tolerances" % T_WALL)
    print("  shoulder Z %.2f: cavity below it %.2f x %.2f; frame widest %.2f x %.2f (+0.76: %.2f x %.2f): clear by %.2f / %.2f per side at the worst" % (
        SHOULDER, 2 * 190.50, 2 * 133.35, 2 * F_OUT["x"][1], 2 * F_OUT["y"][1], 2 * F_OUT["x"][1] + T_SHEET, 2 * F_OUT["y"][1] + T_SHEET,
        190.50 - T_WALL - (F_OUT["x"][1] + T_SHEET / 2), 133.35 - T_WALL - (F_OUT["y"][1] + T_SHEET / 2)))
    print("  rim Z %.2f and the lid tongue: nothing on the frame reaches outboard of %.2f x %.2f, so neither can carry it" % (RIM, 2 * F_OUT["x"][1], 2 * F_OUT["y"][1]))
    print("  the gasket step (#1488, frame z 5.46) and its o-ring: the o-ring goes in after the frame is screwed (instruction step 4), so it holds nothing")
    zc = RIB_TOP + 8.76; cc = (170.81 + 0.03494 * (zc + 7.94), 113.66 + 0.03494 * (zc + 7.94))
    fc = (F_OUT_C[0] + 0.0, F_OUT_C[1] + 0.0); d45 = math.hypot(fc[0] + F_OUT_R * math.sqrt(0.5) - cc[0], fc[1] + F_OUT_R * math.sqrt(0.5) - cc[1])
    print("  vertical corners: case R %.2f (#595) against the frame's R %.2f (#3257): gap on the diagonal %.2f, larger than the sides" % (CORNER_R, F_OUT_R, CORNER_R - d45))
    for name, z in (("end walls (the frame's widest line meets the drafted wall)", (F_OUT["x"][1] - HX0) / TW), ("long walls", (F_OUT["y"][1] - HY0) / TW)):
        print("  walls alone, %s: frame bottom Z %.2f" % (name, z - 8.76))

    print("\n== (B) the seat without a designed stop (Peli: 'fully seated on the internal ribs'), geometric (sharp edges)")
    cases = [("frame +0.76, rib tops +0.76 (highest)", -0.38, 0.0, +0.76), ("frame +0.76", -0.38, 0.0, 0.0), ("all nominal", 0.0, 0.0, 0.0),
             ("frame -0.10", 0.05, 0.0, 0.0), ("frame -0.20", 0.10, 0.0, 0.0), ("frame -0.40", 0.20, 0.0, 0.0), ("frame -0.76", 0.38, 0.0, 0.0),
             ("frame -0.76, rib tops -0.76", 0.38, 0.0, -0.76), ("frame -0.76, case +0.76", 0.38, 0.38, 0.0),
             ("frame -0.76, case +0.76, rib tops -0.76 (lowest)", 0.38, 0.38, -0.76)]
    seats = {}
    for name, u, c, dt in cases:
        zb, why = seat(u, c, dt); seats[name] = zb
        print("  %-52s frame bottom Z %6.2f  face top (plate on the frame) %6.2f  first contact: %s" % (name, zb, zb + FH + PLATE[2], why))
    zb_e, why_e = seat(0.0 + 0.10, 0.0, 0.0)
    print("  with a 0.10 mm moulded edge allowance on the catch (INFERRED), the all-nominal frame does not hold on the rib tops: it rests at Z %.2f (%s)" % (zb_e, why_e))
    face_need_lo = B_TOP + HEATSINK + sum(t for _, t in BOARD_TOLS) + MIN_FACE + XEN_H
    face_need_hi = RIM - T_CASE_Z - MIN_MECH + REBATE - T_REBATE
    print("  window for the worst face top: M1 needs >= %.2f, M2 (with the 2.0 rebate) needs <= %.2f: %.2f mm wide" % (face_need_lo, face_need_hi, face_need_hi - face_need_lo))
    rng_f = seats["frame +0.76"] - seats["frame -0.76"]
    rng_r = seats["frame +0.76, rib tops +0.76 (highest)"] - seats["frame -0.76"]
    rng_all = seats["frame +0.76, rib tops +0.76 (highest)"] - seats["frame -0.76, case +0.76, rib tops -0.76 (lowest)"]
    print("  the rib seat spans %.2f mm on the frame sheet's tolerance alone, %.2f with the rib-top allowance and %.2f with every case allowance:" % (rng_f, rng_r, rng_all))
    print("  each more than the window, so no")
    print("  plate position referenced to the frame's rest meets M1 and M2 together; the frame needs a designed stop")

    print("\n== (C) C6: four setting legs under the frame's ring, fixed to the ring first and placed by the frame's own centring")
    zb_nom = LEG_TOP - RING_UNDER
    t_pad = T_FLOOR + T_LEG
    zb_lo, zb_hi = zb_nom - t_pad - T_SHEET, zb_nom + t_pad + T_SHEET
    face_nom = LEG_TOP + RING_T + PLATE[2]
    face_tols = [("floor under the leg (INFERRED)", T_FLOOR), ("leg height (drawing)", T_LEG), ("ring 9.39 (SHEET class, INFERRED)", T_SHEET), ("plate 3.0 (INFERRED)", T_PLATE)]
    face_lo = face_nom - sum(t for _, t in face_tols); face_hi = face_nom + sum(t for _, t in face_tols)
    rib_face_hi = RIB_TOP + T_CASE_Z + FH + T_SHEET + PLATE[2] + T_PLATE
    under_lo = LEG_TOP - t_pad + RING_T - T_SHEET
    print("  pad top %.2f = shoulder %.2f + %.2f + 0.10 - ring %.2f + (floor %.2f + leg %.2f + ring %.2f): the lowest pad that keeps the plate's underside 0.10 above" % (
        LEG_TOP, SHOULDER, T_CASE_Z, RING_T, T_FLOOR, T_LEG, T_SHEET))
    print("  the highest the shoulder can stand (%.2f)" % (SHOULDER + T_CASE_Z))
    print("  frame bottom %.2f nominal, %.2f .. %.2f (legs); an oversize frame the ribs catch can only sit higher, at most rib top %.2f, where the feet hover at most %.2f" % (
        zb_nom, zb_lo, zb_hi, RIB_TOP + T_CASE_Z, RIB_TOP + T_CASE_Z - zb_lo))
    print("  face top %.2f nominal, %.2f .. %.2f on the legs; on the ribs at most %.2f; so %.2f .. %.2f in every case (window %.2f .. %.2f: %.2f below, %.2f above)" % (
        face_nom, face_lo, face_hi, rib_face_hi, face_lo, max(face_hi, rib_face_hi), face_need_lo, face_need_hi, face_lo - face_need_lo, face_need_hi - max(face_hi, rib_face_hi)))
    print("  plate underside at least %.2f against the shoulder at %.2f .. %.2f (M8z): the rebated band faces the rim zone at every seat" % (
        under_lo, SHOULDER - T_CASE_Z, SHOULDER + T_CASE_Z))
    # the leg itself
    def fil_z(x, off): d = x - FLAT_X; return FIL_R - math.sqrt((FIL_R - off) ** 2 - d * d) if d > 0 else 0.0
    rel_out = fil_z(LEG_X[1], RELIEF) + 0.0
    skirt_in_at = lambda y: F_SKIRT_IN[0] if y <= F_SKIRT_IN_C[1] else F_SKIRT_IN_C[0] + math.sqrt(F_SKIRT_IN_R ** 2 - (y - F_SKIRT_IN_C[1]) ** 2)
    win_at = lambda y: F_WIN[0] if y <= F_WIN_C[1] else F_WIN_C[0] + math.sqrt(F_WIN_R ** 2 - (y - F_WIN_C[1]) ** 2)
    sk = min(skirt_in_at(y) for y in (LEG_Y[0], LEG_Y[1])); wn = max(win_at(y) for y in (LEG_Y[0], LEG_Y[1]))
    leg_case = sum(t for _, t in LEG_IN_CASE)
    print("  leg: 6061-T6, profile cut from 6.0 plate at |Y| %.1f..%.1f; foot bears on the flat floor X %.1f..%.1f; column X %.2f..%.2f to the pad" % (
        LEG_Y[0], LEG_Y[1], FOOT_X[0], FOOT_X[1], LEG_X[0], LEG_X[1]))
    print("  placed on the frame (face down on the bench) by a printed locator in each window corner, bonded to the ring's underside by a VHB 5952 pad")
    print("  in a 0.9 pocket of its pad (metal on the ring sets the height); a leg sits within %.2f of its place against the case centre (centring %.2f," % (leg_case, T_CENTRE))
    print("  window per side %.2f, locator %.2f), %.2f against a case feature (plus %.2f per wall); the locator registers on both window faces, so" % (T_SHEET / 2, T_JIG, leg_case + T_WALL, T_WALL))
    print("  the leg moves by up to %.2f in X and in Y at once against the frame's own features (window per side and locator)" % (T_SHEET / 2 + T_JIG))
    print("  underside over the fillet relieved at %.1f normal to Peli's R %.2f (%.2f high under the column's outer face)" % (RELIEF, FIL_R, rel_out))
    pad = (LEG_X[1] - LEG_X[0]) * (LEG_Y[1] - LEG_Y[0])
    print("  pad %.2f x %.2f = %.1f mm2 under the ring (ring spans X %.2f..%.2f over the leg's Y)" % (LEG_X[1] - LEG_X[0], LEG_Y[1] - LEG_Y[0], pad, wn, 182.75))
    I = (LEG_Y[1] - LEG_Y[0]) * (LEG_X[1] - LEG_X[0]) ** 3 / 12.0; L = LEG_TOP - 5.0
    print("  column buckling (pinned, E 69 GPa): %.0f N; a 25 N face shared by the four legs bears %.2f MPa on each pad; a 100 g shock of a 2.5 kg face (INFERRED): %.1f MPa per pad" % (
        math.pi ** 2 * 69000 * I / L ** 2, 25.0 / 4 / pad, 2.5 * 9.81 * 100 / 4 / pad))
    area = (LEG_X[1] - LEG_X[0]) * (LEG_TOP - 5) + (FOOT_X[1] - FOOT_X[0]) * 8 + (LEG_X[0] - FOOT_X[0]) * 18 / 2 + (LEG_X[0] - FOOT_X[1]) * 4
    print("  mass about %.1f g each (%.0f mm2 x 6.0 at 2.70 g/cm3)" % (area * 6.0 * 2.70e-3, area))
    lead_w = (hx(FIL_T) - T_WALL) - (LEG_X[1] + leg_case + T_WALL)
    print("  the shore lead between a west leg and the end wall above the fillet: %.2f nominal, %.2f at the worst" % (hx(FIL_T) - LEG_X[1], lead_w))

    print("\n== (D) every case-dependent margin of the chosen arrangement (C1 on the C6 legs, C2 to C5), nominal / worst / RSS low")
    heat = B_TOP + HEATSINK
    row("M1", "monitor body over the CM5 heatsinks", MIN_FACE, face_nom - XEN_H - heat, face_tols + BOARD_TOLS,
        open_="left out, TBD: the Xenarc body's tolerance and rear frame, the heatsink's height, the spacers")
    rim_tols = [("rim against the stack floor (INFERRED)", T_CASE_Z)]
    row("M2", "rebated plate band below the rim, under the lid's wall", MIN_MECH, RIM - (face_nom - REBATE), face_tols + [("rebate depth", T_REBATE)] + rim_tols)
    face_plan = [("plate float on its 6-32 screws", T_FLOAT), ("frame centring", T_CENTRE), ("rebate line", T_REBATE)]
    row("M2b", "full-thickness face (%.1f x %.1f) inside the lid's opening, in X (Y: %.2f nominal)" % (REB_IN[0], REB_IN[1], LID_OPEN[1] - REB_IN[1] / 2), MIN_MECH,
        LID_OPEN[0] - REB_IN[0] / 2, [("lid per wall", T_WALL), ("lid on the base (INFERRED)", T_LID)] + face_plan)
    row("M3", "space under the QMX tray for the face parts (lid STEP 45.47; web 44.45 in the worst)", MIN_MECH, RIM + LID_STEP - TRAY - face_nom,
        face_tols + rim_tols + [("lid depth, web page against STEP", LID_STEP - LID_WEB)], open_="parts under the tray: C&K button heights TBD")
    row("M5", "pack group (205.5 long, A06) to the east legs' inner faces at |Y| %.1f, per side" % LEG_Y[0], MIN_MECH, (2 * LEG_Y[0] - 205.5) / 2,
        [("pack placed by hand (INFERRED)", 1.0)] + LEG_IN_CASE, "group centred in Y")
    row("M7", "stack lift-out through the frame window, per side in X (Y has 16.91)", MIN_MECH, F_WIN[0] - B_OUT[0],
        [("window -0.76", T_SHEET / 2), ("frame centring", T_CENTRE), ("stack placement", T_STACK)])
    plate_x = [("case per wall", T_WALL), ("plate outline", T_OUTLINE), ("frame centring", T_CENTRE), ("plate float on its 6-32 screws", T_FLOAT)]
    row("M8x", "plate edge to the rim zone in X, frame centred (plate %.1f wide)" % PLATE[0], MIN_MECH, RIMZ_X - PLATE[0] / 2, plate_x)
    row("M8y", "plate edge to the rim zone in Y, frame centred", MIN_MECH, RIMZ_Y - PLATE[1] / 2, plate_x)
    row("M8z", "plate underside above the shoulder, so the plate edge faces the rim zone", 0.0, LEG_TOP + RING_T - SHOULDER,
        [("floor under the leg", T_FLOOR), ("leg height", T_LEG), ("ring 9.39", T_SHEET), ("shoulder against the floor (INFERRED)", T_CASE_Z)], "a condition")
    row("M8f", "each 6-32 passes its %.1f plate hole with the inserts at the pattern's worst (float, pattern, hole)" % FACE_HOLE, 0.0, T_HOLE,
        [("insert pattern per side (SHEET)", T_SHEET / 2), ("hole position in the plate", T_OUTLINE)], "a condition")
    hx_head = REB_IN[0] / 2 - (INSERTS[0][0] + PAN_632); hy_head = REB_IN[1] / 2 - (INSERTS[1][1] + PAN_632)
    row("M8h", "6-32 pan heads (%.2f across) on the full-thickness face: end inserts in X (long-wall inserts in Y: %.2f)" % (2 * PAN_632, hy_head), 0.0, min(hx_head, hy_head),
        [("screw in its hole", T_FLOAT), ("rebate line", T_REBATE)], "a condition")
    zmid = LEG_TOP + 0.63
    for ax, wall_p, wall_f, fhalf, ph in (("X", RIMZ_X, hx(zmid), F_OUT["x"][1], PLATE[0] / 2), ("Y", RIMZ_Y, hy(zmid), F_OUT["y"][1], PLATE[1] / 2)):
        g = (wall_p - wall_f) + (fhalf - ph) - T_FLOAT
        print("  M8 without the centring step, frame pushed against the %s wall until its skirt touches and the plate floated the same way: plate gap %.2f nominal, %.2f with the frame -0.76" % (
            ax, g, g - T_SHEET / 2))
    skirt_tols = [("floor under the leg", T_FLOOR), ("leg height", T_LEG), ("skirt below the ring (SHEET class, INFERRED)", T_SHEET)]
    row("M19", "QMX tray east edge inside the lid's flat ceiling (C5)", MIN_MECH, 173.08 - 171.0, [("case per wall", T_WALL)])
    print("  M20 (the seat, a statement): frame bottom %.2f nominal against rib tops %.2f: %.2f above them; at the extremes the legs may sit %.2f below the"
          " highest rib top, where an oversize frame rests on the ribs instead, higher and never lower" % (zb_nom, RIB_TOP, zb_nom - RIB_TOP, RIB_TOP + T_CASE_Z - zb_lo))

    # ---------------- floor items (positions from case_margins.out lines 34 to 36 and 64 to 65; A06 for the pack)
    row("M4a", "pack block's east corner to Peli's R 15.88 floor fillet (west face X 122, A06)", MIN_MECH, 3.71,
        [("web interior at the fillet, against STEP", 3.71 - 2.85), ("pack placed by hand (INFERRED)", 1.0)])
    row("M4b", "pack block's east face to the east wall", MIN_MECH, 9.68, [("web interior, against STEP", 9.68 - 8.38), ("pack placed by hand (INFERRED)", 1.0)])
    row("M6", "pack top under B16's underside (A06 3.32 at its pessimistic base, plus the 1.1 VHB lift)", MIN_MECH, 3.32 + 1.1, [("floor flatness (INFERRED)", T_FLOOR)])
    lift = math.sqrt(FIL_R ** 2 - (FIL_R - 1.1) ** 2)
    row("M15a", "dock strip's underside (on 1.1 pads) to the front floor fillet (edge Y -113, gen_pcb_e.py:15)", MIN_MECH, (FLAT_Y - 113.0) + lift,
        [("case per wall", T_WALL), ("strip placement", T_STACK)], "the fillet reaches Z 1.1 at %.2f past its tangent" % lift)
    row("M15b", "dock strip's corner pads on the flat floor (edge to the tangent)", 0.0, FLAT_Y - 113.0, [("case per wall", T_WALL), ("strip placement", T_STACK)], "bearing must stay on flat floor")
    row("M16", "rods (+-110.5, +-73) to the long-wall fillet tangents (61.14 to the end walls)", MIN_MECH, FLAT_Y - 73.0, [("case per wall", T_WALL), ("stack placement", T_STACK)])

    # ---------------- the setting legs against their neighbours (each carries its placement: the frame's centring, the window, the locator)
    to_case = LEG_IN_CASE + [("case per wall", T_WALL)]
    row("M21a", "leg foot on the flat floor: foot end X %.1f to the fillet tangent" % FOOT_X[1], 0.0, FLAT_X - FOOT_X[1], to_case, "bearing must stay on flat floor")
    row("M21b", "leg foot on the flat floor: foot |Y| %.1f to the long-wall fillet tangent" % LEG_Y[1], 0.0, FLAT_Y - LEG_Y[1], to_case, "bearing must stay on flat floor")
    row("M21c", "leg relief to Peli's floor fillet (normal)", MIN_MECH, RELIEF, to_case)
    # M21d in two dimensions: the column's outer-back corner lies in the skirt's corner arc; the leg moves in X and Y at once
    corner = (LEG_X[1], LEG_Y[1]); d0 = math.hypot(corner[0] - F_SKIRT_IN_C[0], corner[1] - F_SKIRT_IN_C[1])
    arc_nom = F_SKIRT_IN_R - d0; straight_nom = F_SKIRT_IN[0] - LEG_X[1]
    t_leg = T_SHEET / 2 + T_JIG
    worst_shift = min(F_SKIRT_IN_R - math.hypot(corner[0] + a - (F_SKIRT_IN_C[0] + c), corner[1] + b - (F_SKIRT_IN_C[1] + d))
                      for a in (-t_leg, t_leg) for b in (-t_leg, t_leg) for c in (-T_SKIRT, T_SKIRT) for d in (-T_SKIRT, T_SKIRT))
    worst_offset = min(F_SKIRT_IN_R - T_SKIRT - math.hypot(corner[0] + a - F_SKIRT_IN_C[0], corner[1] + b - F_SKIRT_IN_C[1])
                       for a in (-t_leg, t_leg) for b in (-t_leg, t_leg))
    t_leg2, t_skirt2 = t_leg + T_JIG, 2 * T_SKIRT                  # the unstated shares (locator, skirt face) taken twice
    worst2 = min(min(F_SKIRT_IN_R - math.hypot(corner[0] + a - (F_SKIRT_IN_C[0] + c), corner[1] + b - (F_SKIRT_IN_C[1] + d))
                     for a in (-t_leg2, t_leg2) for b in (-t_leg2, t_leg2) for c in (-t_skirt2, t_skirt2) for d in (-t_skirt2, t_skirt2)),
                 min(F_SKIRT_IN_R - t_skirt2 - math.hypot(corner[0] + a - F_SKIRT_IN_C[0], corner[1] + b - F_SKIRT_IN_C[1])
                     for a in (-t_leg2, t_leg2) for b in (-t_leg2, t_leg2)))
    ux, uy = (corner[0] - F_SKIRT_IN_C[0]) / d0, (corner[1] - F_SKIRT_IN_C[1]) / d0
    rss_d = math.sqrt((T_JIG ** 2 + (T_SHEET / 2) ** 2 + T_SKIRT ** 2) * (ux * ux + uy * uy))
    print("  M21d in two dimensions: column outer-back corner (%.2f, %.2f) to the skirt's R %.2f corner about (%.2f, %.2f): %.2f nominal (straight face %.2f);"
          " worst with the leg moved %.2f in X and Y: %.2f with the skirt's %.2f as a shift of the arc's centre, %.2f as a profile offset" % (
          corner[0], corner[1], F_SKIRT_IN_R, F_SKIRT_IN_C[0], F_SKIRT_IN_C[1], arc_nom, straight_nom, t_leg, worst_shift, T_SKIRT, worst_offset))
    row("M21d", "leg column to the frame skirt's inner face: Euclidean, the leg placed in X and Y (outer-back corner)", MIN_MECH, min(arc_nom, straight_nom),
        [("leg locator and window, X and Y", t_leg), ("skirt per side (INFERRED)", T_SKIRT)], worst=min(worst_shift, worst_offset), rss=rss_d, wc2=worst2)
    row("M21e", "leg pad fully under the ring (pad inner edge to the window edge)", 0.0, LEG_X[0] - wn, [("leg locator on the window", T_JIG)])
    row("M21f", "leg to B16's corner (165, 100) in Y", MIN_MECH, LEG_Y[0] - B_OUT[1], [("stack placement", T_STACK)] + LEG_IN_CASE)
    row("M21h", "leg column to the backer ring's outer edge (X 172, panel1450.py:93-95)", MIN_MECH, LEG_X[0] - 172.0,
        [("leg locator on the window", T_JIG), ("window per side (SHEET)", T_SHEET / 2), ("insert pattern per side (SHEET)", T_SHEET / 2),
         ("6-32 float in the plate", T_FLOAT), ("backer on the plate (INFERRED)", T_BACKER)])

    # ---------------- C3: the connector plate on the back wall, the full ruled set
    print("\n== (E) C3: the connector plate on the back wall with the full ruled set (V2-SPEC.md:11, ASSEMBLY.md:118-125 and :135)")
    FAIR_X, RIMLINE_X, AA_X = 58.93, 57.15, 87.34     # DXF top view: fairing base #4992/#5107 (#4985/#5116); rim-flange line #5071 to 57.15; A-A #3130
    OUT_FLAT_Z, OUT_FLANGE_Z = 15.9, 97.91            # DXF A-A #7590 (outer back wall flat from about Z 15.9); rim flange from Z 97.9 (#7866)
    P = dict(x0=-57.0, x1=57.0, z0=18.3, z1=86.6, t=5.0)
    STACK_OUT = 0.76 + P["t"] + 2.0 + 5.34             # 930-001 class flange gasket 0.030 in, plate, closed-cell gasket 2.0, wall 5.34 (DXF A-A)
    print("  free zone on the outside: between the hinge fairings' bases at |X| %.2f (the rim-flange line ends at %.2f); section A-A at X %.2f shows the" % (FAIR_X, RIMLINE_X, AA_X))
    print("  back wall plain from the outer bottom radius (flat from Z %.1f) to Z 93.6 there; the end view carries back features to Z 15.9 .. 30.5 at X no view gives" % OUT_FLAT_Z)
    print("  plate %.1f x %.1f x %.1f at X %.1f..%.1f, Z %.1f..%.1f; flange stack to the wall's inner face %.2f" % (
        P["x1"] - P["x0"], P["z1"] - P["z0"], P["t"], P["x0"], P["x1"], P["z0"], P["z1"], STACK_OUT))
    SHELL15_MATED = 32.51 / 2                          # GLN 233-340 G6 plug: 1.280 (32.51) max; AMPH p. 52 D38999/26 shell 15 Q max 1.280 (32.5)
    SHELL13_MATED = 29.4 / 2                           # AMPH p. 52 D38999/26 shell 13 Q max 1.157 (29.4); GLN M85049/38S13N E max 1.157 (29.4)
    # items: key, (x, z), footprint on the plate ('sq', side) or ('c', r), mated envelope r, wall hole d, inside top above the centre, what sets it
    ITEMS = [
        ("A sealed RJ45 (38999 shell 15 class)", (-28.5, 36.6), ("sq", 31.29), ("c", SHELL15_MATED), 29.0, 8.0, "patch plug body +-8 (INFERRED)"),
        ("C shore DC D38999/20 sh 13", (4.2, 34.0), ("sq", 28.9), ("c", SHELL13_MATED), 22.0, 5.0, "cores within the insert +-5 (INFERRED)"),
        ("B sealed USB-C (4000 series class)", (33.7, 36.6), ("c", 25.67 / 2), ("c", 13.0), 29.0, 3.5, "lead 7.0 (INFERRED)"),
        ("E pod over the M8 receptacle", (-30.0, 70.0), ("sq", 28.0), ("sq", 28.0), 18.0, 5.0, "M8 rear body 10 (INFERRED)"),
        ("D USB 233-370 sh 15", (4.6, 67.0), ("sq", 31.29), ("c", SHELL15_MATED), 29.0, 14.5, "rear body within the 29 hole"),
        ("F ground stud M6", (34.6, 64.5), ("c", 12.0), ("c", 12.0), 8.0, 6.0, "nut and washer 12 (INFERRED)"),
    ]   # the previous issue's X: A -29.3, C +3.0, B +32.0, D +3.5, F +33.5 (re-laid so that every pair keeps 1.0 with each part at its float)
    SCREWS = [(-51.1, 24.2), (-51.1, 50.1), (-51.1, 76.0), (51.1, 24.2), (51.1, 50.1), (51.1, 76.0)]   # M4 x 25: bonded sealing washer under the head, plain washer 9.0 and Nyloc inside
    SW_R, SW_IN_R, SH_R = 5.0, 4.5, 2.25      # bonded sealing washer 10 across (INFERRED class), plain washer 9.0 inside, 4.5 holes
    # each part's float on the plate: a part located by screws in clearance holes, or by its body in a hole, can sit anywhere the smallest
    # screw (or body) of its class lets it (STD); every machined place in the plate carries T_MACH besides
    M3_MIN, M4_MIN = 2.874, 3.838
    FLOAT = {"A": (3.35 - M3_MIN) / 2,      # 38999 shell 15 class as the 233-370 D0: 4x .124/.132 (3.15/3.35) holes (GLN) on M3 tapped in the plate
             "C": (3.45 - M3_MIN) / 2,      # D38999/20 shell 13: E .120/.136 (3.05/3.45) (GLN) on M3
             "B": 0.30,                      # the 4000 series body in its 19.2 D cut-out; the sheet gives the cut-out, not the body (INFERRED)
             "E": (10.5 - 9.838) / 2,        # the M8 receptacle's M10 x 0.75 body in a 10.5 plate hole, the pod located on it (INFERRED)
             "D": (3.35 - M3_MIN) / 2,      # 233-370 D0 (GLN)
             "F": (6.4 - 5.794) / 2,         # the M6 stud in a 6.4 plate hole (INFERRED)
             "screw": (4.5 - M4_MIN) / 2}    # an M4 x 25 in its 4.5 plate hole; the bonded washer under its head centres on it
    def fl(name): return FLOAT["screw"] if name.startswith("screw") else FLOAT[name[0]]
    def gap_fp(a, b):
        """Plan gap between two footprints ((x, z), shape): square or circle."""
        (pa, fa), (pb, fb) = a, b
        def box(p, f): return (p[0] - f[1] / 2, p[1] - f[1] / 2, p[0] + f[1] / 2, p[1] + f[1] / 2)
        if fa[0] == "sq" and fb[0] == "sq":
            A, B = box(pa, fa), box(pb, fb)
            dx = max(B[0] - A[2], A[0] - B[2], 0.0); dz = max(B[1] - A[3], A[1] - B[3], 0.0)
            return math.hypot(dx, dz) if (dx > 0 and dz > 0) else max(B[0] - A[2], A[0] - B[2], B[1] - A[3], A[1] - B[3])
        if fa[0] == "c" and fb[0] == "c": return math.hypot(pa[0] - pb[0], pa[1] - pb[1]) - fa[1] - fb[1]
        if fa[0] == "c": (pa, fa), (pb, fb) = (pb, fb), (pa, fa)
        A = box(pa, fa); cx = min(max(pb[0], A[0]), A[2]); cz = min(max(pb[1], A[1]), A[3])
        return math.hypot(pb[0] - cx, pb[1] - cz) - fb[1]
    def pairs(parts):
        """Every pair: (nominal gap, worst with two machined places and both floats, RSS low, name a, name b), tightest at the worst first."""
        out = []
        for i, a in enumerate(parts):
            for b in parts[i + 1:]:
                g, t = gap_fp(a[1], b[1]), (T_MACH, T_MACH, fl(a[0]), fl(b[0]))
                out.append((g, g - sum(t), g - math.sqrt(sum(x * x for x in t)), a[0], b[0]))
        return sorted(out, key=lambda r: r[1])
    fps = [(it[0], (it[1], it[2])) for it in ITEMS] + [("screw %+.1f,%.1f" % s, (s, ("c", SW_R))) for s in SCREWS]
    fp_pairs = pairs(fps)
    mated = [(it[0], (it[1], it[3])) for it in ITEMS]
    mated_pairs = pairs(mated)
    edge = []
    for name, (p, f) in fps:
        h = f[1] / 2 if f[0] == "sq" else f[1]
        edge.append((min(p[0] - h - P["x0"], P["x1"] - p[0] - h, p[1] - h - P["z0"], P["z1"] - p[1] - h), name))
    worst_edge = min(edge); worst_edge_item = min(e for e in edge if not e[1].startswith("screw")); worst_edge_washer = min(e for e in edge if e[1].startswith("screw"))
    holes = [(it[0], it[1], it[4] / 2) for it in ITEMS] + [("screw %+.1f,%.1f" % s, s, SH_R) for s in SCREWS]
    webs = [(math.hypot(a[1][0] - b[1][0], a[1][1] - b[1][1]) - a[2] - b[2], a[0], b[0]) for i, a in enumerate(holes) for b in holes[i + 1:]]
    bands = [(min(h[1][0] - h[2] - P["x0"], P["x1"] - h[1][0] - h[2], h[1][1] - h[2] - P["z0"], P["z1"] - h[1][1] - h[2]), h[0]) for h in holes]
    worst_web = min(webs, key=lambda t: t[0]); worst_band = min(bands, key=lambda t: t[0])
    worst_band_item = min((b for b in bands if not b[1].startswith("screw")), key=lambda t: t[0])
    print("  items (centre X, Z; footprint on the plate; mated envelope r; wall hole; top of the part inside):")
    for it in ITEMS:
        print("    %-38s (%6.1f, %5.1f)  %-11s mated %5.2f  hole %4.1f  inside top Z %5.1f (%s)" % (
            it[0], it[1][0], it[1][1], ("%.2f sq" % it[2][1]) if it[2][0] == "sq" else ("r %.2f" % it[2][1]), it[3][1], it[4], it[1][1] + it[5], it[6]))
    print("  mated envelopes: A and D the shell 15 plug class 32.51 across (GLN 233-340, AMPH p. 52), C the shell 13 plug and its strain relief 29.4 (AMPH p. 52, GLN M85049/38)")
    print("  six M4 x 25 at X +-51.1, Z 24.2 / 50.1 / 76.0: a bonded sealing washer 10 across under each head, a plain washer 9.0 and a Nyloc inside")
    print("  floats on the plate: %s; every machined place +-%.2f, two to a pair" % (
        ", ".join("%s %.2f" % (k, v) for k, v in FLOAT.items()), T_MACH))
    nm = lambda n: n.split(" ")[0] if not n.startswith("screw") else n
    print("  pairs on the plate face, the four tightest at the worst (nominal / worst): %s; to the plate edge: item %.2f (%s), screw washer %.2f (%s)" % (
        "; ".join("%.2f / %.2f (%s / %s)" % (g, w, nm(a), nm(b)) for g, w, _, a, b in fp_pairs[:4]),
        worst_edge_item[0], worst_edge_item[1], worst_edge_washer[0], worst_edge_washer[1]))
    print("  mated envelopes, the three tightest pairs at the worst (nominal / worst): %s" % "; ".join(
        "%.2f / %.2f (%s / %s)" % (g, w, nm(a), nm(b)) for g, w, _, a, b in mated_pairs[:3]))
    print("  tightest wall web: %.2f (%s / %s); tightest gasket band from a wall hole to the plate edge: %.2f (%s), of a connector hole %.2f (%s)" % (
        worst_web + worst_band + worst_band_item))
    # the X 0 rib, if the back wall carries it: what bears on the wall inside, and what only passes through a hole
    bear = [("screw %+.1f,%.1f" % s, s, SW_IN_R) for s in SCREWS] + [("F ground stud nut", ITEMS[5][1], 6.0)]
    rib_gap = min((abs(b[1][0]) - b[2] - 0.91, b[0]) for b in bear)
    crossing = [it[0] for it in ITEMS if abs(it[1][0]) < it[4] / 2]
    print("  X 0 rib (if the back wall carries it, half-width 0.91 on the wall): nearest bearing face %.2f off it (%s); holes that cut it, nothing bearing: %s" % (
        rib_gap[0], rib_gap[1], ", ".join(crossing)))
    print("  inner ribs at X +-76.2: the plate's nearest inside washer at |X| %.1f" % (51.1 + SW_IN_R))
    top_in = max(((it[1][1] + it[5]), it[0]) for it in ITEMS)
    top_hole_d = max((it[1][1] + it[4] / 2, it[0]) for it in ITEMS if it[0][0] in "D")
    top_screw = max(s[1] for s in SCREWS) + SW_IN_R
    print("  highest part inside: Z %.2f (%s); top screws' inside washers Z %.2f; highest wall hole whose body protrudes: Z %.2f (%s)" % (
        top_in[0], top_in[1], top_screw, top_hole_d[0], top_hole_d[1]))
    t_mark = [("hole marking", T_JACK)]
    row("M14a", "highest part inside the back wall below the frame skirt (D's body; the top screws' washers reach %.1f)" % top_screw, MIN_MECH,
        zb_nom - max(top_hole_d[0], top_screw), skirt_tols + t_mark)
    row("M14b", "connector plate bottom edge above the outer bottom radius", MIN_MECH, P["z0"] - OUT_FLAT_Z, [("case Z (INFERRED)", T_CASE_Z)] + t_mark)
    row("M14i", "connector plate edge to the hinge fairings' bases in X", MIN_MECH, FAIR_X - P["x1"],
        [("case per side (INFERRED)", T_WALL), ("plate marking", T_JACK), ("plate outline", T_OUTLINE)])
    for key, what, pp in (("M14j", "tightest pair on the plate face (flanges, pod, stud, screw washers), each at its float: %s / %s", fp_pairs),
                          ("M14k", "tightest pair of mated connectors (shell 15 plugs 32.51, shell 13 plug 29.4), each at its float: %s / %s", mated_pairs)):
        row(key, what % (nm(pp[0][3]), nm(pp[0][4])), MIN_MECH, min(r[0] for r in pp), [("machined positions, two, and both floats", pp[0][0] - pp[0][1])],
            worst=pp[0][1], rss=min(r[0] for r in pp) - min(r[2] for r in pp), wc2=pp[0][1])
    row("M14l", "tightest wall web between two holes (screw holes included)", MIN_WEB, worst_web[0], [("hole marking, two holes", 2 * T_JACK)])
    row("M14m", "tightest gasket band from a wall hole to the plate edge (screw holes included)", MIN_BAND, worst_band[0], [("hole marking", T_JACK), ("plate marking", T_JACK)])
    row("M14n", "nearest bearing face inside to the X 0 rib (if this wall carries it)", MIN_MECH, rib_gap[0],
        [("rib per wall", T_WALL), ("plate marking", T_JACK), ("its hole in the plate", T_MACH), ("its float", fl(rib_gap[1]))])
    row("M14o", "connector plate top below the outer rim flange", MIN_MECH, OUT_FLANGE_Z - P["z1"], [("case Z (INFERRED)", T_CASE_Z)] + t_mark)
    row("M14p", "screw washers (bonded, 10 across) fully on the plate (edge distance)", 0.0, worst_edge_washer[0],
        [("screw in its 4.5 hole", FLOAT["screw"]), ("machined positions (INFERRED)", T_MACH)], "a condition")
    # the inside of each mate
    y_in = lambda z: hy(z)
    usb_rear = 16.51                            # GLN 233-370 D0 side view: .650 (16.51) max behind the flange
    dc_rear = 31.50 - 19.58 - 2.11              # GLN D38999/20: 1.240 overall, H .771 min (shells 9-15), G .083 min
    face_w_delta = T_WALL + (STACK_OUT - (0.76 * 0.9 + P["t"] + 1.5 + 5.34 - T_SHEET))   # case -0.38, wall -0.76, gaskets compressed (INFERRED)
    xA, zA = ITEMS[0][1]; xB, zB = ITEMS[2][1]; xC, zC = ITEMS[1][1]; xD, zD = ITEMS[4][1]
    rearA = y_in(zA) - (usb_rear - STACK_OUT)   # A is a 38999 shell 15 class body: rear no deeper than the 233-370's
    rearD = y_in(zD) - (usb_rear - STACK_OUT)
    print("  233-370 class rear face %.2f inside the wall's inner face (%.2f at the worst); D38999/20 rear %.2f short of it" % (
        usb_rear - STACK_OUT, usb_rear - STACK_OUT + face_w_delta, STACK_OUT - dc_rear))
    b16_low = B_UNDER - (VHB_T + 2 * LAM)       # B16's underside at the worst (VHB and two laminates below it; spacers TBD)
    print("  B16's underside Z %.2f (%.2f at the worst); U51 hangs %.1f under it at Y 68.3..85.8; A22's edge Y %.1f" % (B_UNDER, b16_low, U51_H, A_EDGE_Y))
    # D: the straight plug that fails and the right-angle plug that fits
    y_str = rearD - 40.0
    print("  D at Z %.1f: a straight USB-A plug of 40 (INFERRED) ends at Y %.2f over the slot 2 heatsink (X -23..18, Y 32..88, top Z %.2f) with its body at Z %.1f..%.1f:"
          " %.2f outboard of it nominal, %.2f at the worst" % (zD, y_str, B_TOP + HEATSINK, zD - 4.5, zD + 4.5, y_str - 88.0, y_str - 88.0 - face_w_delta - T_STACK - 0.1))
    row("M14c", "D: right-angle (down) USB-A plug body, <= 20.0 from the 233-370 rear face, to B16's edge", MIN_MECH, rearD - 20.0 - B_OUT[1],
        [("rear face worst (case, wall, gaskets)", face_w_delta), ("stack placement", T_STACK), ("B16 outline", 0.1)])
    row("M14d", "C: shore DC cores (turned down within 12 of the rear) to B16's edge", MIN_MECH, y_in(zC) + (STACK_OUT - dc_rear) - 12.0 - B_OUT[1],
        [("case per wall", T_WALL), ("wall -0.76", T_SHEET), ("stack placement", T_STACK), ("B16 outline", 0.1)])
    row("M14e", "A: patch plug (straight or right-angle, +-8) under B16 and U51", MIN_MECH, (B_UNDER - U51_H) - (zA + ITEMS[0][5]),
        [("B16 underside (VHB, two laminates)", VHB_T + 2 * LAM), ("plate marking", T_JACK), ("A's tapped holes", T_MACH), ("A's float", FLOAT["A"])])
    row("M14f", "A: patch plug end (<= 40.0 from the rear face) outboard of A22's edge", MIN_MECH, rearA - 40.0 - A_EDGE_Y,
        [("rear face worst (case, wall, gaskets)", face_w_delta), ("stack placement", T_STACK), ("A22 outline", 0.1)])
    lead_r, lead_d, lead_R = 3.5, 7.0, 28.0     # INFERRED: a 7 mm lead bent at 4 x its diameter
    b_exit = y_in(zB) + 0.34                    # B's body ends 0.34 short of the wall's inner face (24.8 - 17.8 = 7.0 behind the plate's back)
    row("M14g", "B: USB-C lead (7.0, bent at R 28 into the case) under B16 and U51", MIN_MECH, (B_UNDER - U51_H) - (zB + lead_r),
        [("B16 underside (VHB, two laminates)", VHB_T + 2 * LAM), ("plate marking", T_JACK), ("B's cut-out", T_MACH), ("B's float (INFERRED)", FLOAT["B"])])
    row("M14h", "B: the lead's innermost point outboard of A22's edge", MIN_MECH, b_exit - lead_R - lead_r - A_EDGE_Y,
        [("case per wall", T_WALL), ("wall -0.76", T_SHEET), ("stack placement", T_STACK), ("A22 outline", 0.1)])
    print("  B's lead leaves the wall at Y %.2f and its innermost point is Y %.2f, under B16's back strip at Z %.1f and below" % (b_exit, b_exit - lead_R - lead_r, zB + lead_r))
    print("  E: the M8's rear (15 behind the plate's face, INFERRED) %.2f inside, its pigtail down within 12: to Y %.2f; F: nut, washer and lug 12 inside: to Y %.2f;"
          " screw tips to Y %.2f" % (15.0 - (P["t"] + 2.0 + 5.34), y_in(ITEMS[3][1][1]) - (15.0 - (P["t"] + 2.0 + 5.34)) - 12.0, y_in(ITEMS[5][1][1]) - 12.0,
                                     y_in(50.1) - (25.0 - (1.5 + P["t"] + 2.0 + 5.34))))
    m4 = 1.5 + P["t"] + 2.0 + 5.34 + 0.8 + 5.0
    print("  M4 plate screws: bonded washer (1.5, INFERRED), plate, gasket, wall, washer and an M4 Nyloc (DIN 985, 5.0, INFERRED) take %.2f: M4 x 25 protrudes %.2f" % (m4, 25.0 - m4))

    # ---------------- C2 and C4: the ruled arrestors are the antenna bulkheads, on one RF entry plate per end wall
    print("\n== (F) C2 and C4: the ruled gas-discharge arrestors (PolyPhaser GTH-SFF-AL) as the antenna bulkheads, on an RF entry plate per end wall")
    IN = 25.4
    A_ALL, A_THD, A_JIN, A_JOUT, T_POLY = 2.18 * IN, 0.47 * IN, 0.30 * IN, 0.35 * IN, 0.02 * IN   # POLY drawing rev B, inches leading, .XX +-.02
    A_W, A_H = 0.9 * IN, 1.2 * IN                                 # POLY: 2.2 x 0.9 x 1.2 in max
    A_R = A_W / 2; A_UPDN = A_H - A_R                              # the cap above and the lug below the axis: neither can exceed A_H - A_R
    A_OUT = A_ALL - A_THD - A_JIN                                  # body and outer jack beyond the plate's face
    NUT_R, NUT_T = 12.0, 5.0                                       # nut and lock washer within 24.0 across and 5.0 thick together (INFERRED class): drawn, not dimensioned, the nut 19.1
                                                                   # across its flats (3/4 in, 22.0 across its corners) and the washer 20.5, 4.7 thick together (POLY, scaled); the arrestor's
                                                                   # own if PolyPhaser's dimensions put them inside the class, else a 5/8-24 UNEF nut and lock washer inside it
    O_FREE = 0.63                                                  # the maker's O-ring on the thread's root, drawn 0.63 proud of the body's face, inside the .47 (POLY, scaled; not dimensioned)
    O_NOM, T_O = O_FREE / 2, O_FREE / 2                            # installed anywhere from fully seated to its drawn height (no gland is drawn and no torque stated): 0.32 +-0.32, unstated
    RFP_T, T_RFP = 6.0, 0.2                                        # the RF entry plate, 6.0 aluminium (EN 485 class, standard not held, INFERRED); 6.0 so that an M4 x 12 both engages and stays inside (M11d, M11g)
    GASK, T_GASK = 1.5, 0.5                                        # 2.0 closed-cell gasket, 1.5 compressed, anywhere between 1.0 and 2.0 (INFERRED)
    WALL_HOLE_R, PLATE_HOLE = 27.0 / 2, 16.3                       # wall hole saw 27 passes the nut and washer; plate hole 16.3 for the 5/8-24 thread (0.2 per side, INFERRED)
    F_THD = (PLATE_HOLE - 0.6167 * IN) / 2                         # the arrestor floats this far in its hole: 5/8-24UNEF-2A (POLY) major 0.6167 in min (ASME B1.1 class, INFERRED)
    SPOT_D, SPOT_DEPTH, T_SPOT = 26.0, 1.5, 0.10                   # C4: each 16.3 hole spot-faced 26.0 on the plate's back, its floor 4.5 from the outer face +-0.10 (drawing)
    PLUG_L, PLUG_R, PLUG_CABLE = 10.0, 5.0, 4.0                    # the jumper's right-angle SMA male, mated: 10.0 beyond the jack's end, 5.0 about the axis, its cable's axis within 4.0 of that end (INFERRED class)
    AX_Z = 59.0                                                    # the arrestors' axis, both end walls
    # five on the east wall (the three 5G jacks together, then IRIDIUM and LORA) and seven on the west (the tree's five, then the two WIFI P2P):
    # at |Y| 93 an east jumper cannot get inboard of a setting leg's column before it reaches it (part G, M17c), and the west wall has no pack under it
    SITES_E = [("5G MAIN", -62.0), ("5G DIV", -31.0), ("5G ANT3", 0.0), ("IRIDIUM", 31.0), ("LORA", 62.0)]
    SITES_W = [("VHF", -93.0), ("HF", -62.0), ("WIFI 2.4", -31.0), ("GNSS", 0.0), ("SDR", 31.0), ("WIFI P2P A", 62.0), ("WIFI P2P B", 93.0)]
    SITES_ALL = SITES_E + SITES_W                                  # the two plates share one outline and one screw pattern
    RFP = dict(y=110.1, z0=34.55, z1=83.45)                        # the plate: Y +-110.1, Z 34.55 .. 83.45, the same outline on both walls
    RFP_SCREWS = [(y, z) for y in (-100.0, -45.0, 45.0, 100.0) for z in (40.65, 77.35)]   # M4 x 12 button heads from inside, threads tapped through the plate; rows 0.25 in from the previous issue's for the 5.0 holes' band (M11c)
    HEAD_R, HEAD_IN, RFP_SH_R = 5.0, 1.5 + 2.2, 5.0 / 2           # sealing washer 10 across under an ISO 7380 M4 head 2.2 high (INFERRED class); 5.0 wall holes at the screws
    M4_MAJ = 3.98                                                  # M4 6g major diameter max (ISO 965 class, standard not held, INFERRED)
    SCREW_L, T_SCREW = 12.0, 0.35                                  # M4 x 12 ISO 7380, length js15 for 10 to 18 mm (standard not held, INFERRED)
    WASH_T, T_WASH, SEAL_D = 1.5, 0.10, 8.0                        # sealing washer 1.5 +-0.10 thick, its rubber face at least 8.0 across (INFERRED class)
    ENG_MIN = 2 * 0.7                                              # two pitches of M4 x 0.7 engaged in the plate at the least (INFERRED)
    n_e, n_w = len(SITES_E), len(SITES_W)
    print("  arrestor (POLY): body %.2f across, %.2f above or below its axis at most (cap up, ground lug down), %.2f beyond the plate's face with its outer jack;"
          " thread %.2f, inner jack %.2f; %.1f g each (0.25 lb)" % (A_W, A_UPDN, A_OUT, A_THD, A_JIN, 0.25 * 453.59))
    print("  the maker's O-ring, on the thread's root and drawn %.2f proud of the body's face, seals on the plate's machined outer face (installed %.2f +-%.2f, INFERRED);"
          " the lock washer and nut (within %.1f across and %.1f thick together, INFERRED) on the floor of a %.1f spot-face %.1f deep in the plate's back, standing %.1f"
          " proud of it; the arrestor floats %.2f in its %.1f hole" % (O_FREE, O_NOM, T_O, 2 * NUT_R, NUT_T, SPOT_D, SPOT_DEPTH, NUT_T - SPOT_DEPTH, F_THD, PLATE_HOLE))
    print("  plate %.1f x %.2f x %.1f (Y +-%.1f, Z %.2f..%.2f) on a 2.0 closed-cell gasket; wall holes %.1f at the arrestors, %.1f at the eight screws" % (
        2 * RFP["y"], RFP["z1"] - RFP["z0"], RFP_T, RFP["y"], RFP["z0"], RFP["z1"], 2 * WALL_HOLE_R, 2 * RFP_SH_R))
    print("  east (%d): %s; west (%d): %s; axis Z %.1f" % (n_e, ", ".join("%s %+.0f" % s for s in SITES_E), n_w, ", ".join("%s %+.0f" % s for s in SITES_W), AX_Z))
    in_jack = A_THD + A_JIN - O_NOM - RFP_T - GASK - WALL_T       # the inner jack's end past the wall's inner face (the O-ring holds the body off the plate)
    x_end = hx(AX_Z) - in_jack - PLUG_L
    t_end = [("case per wall", T_WALL), ("wall thickness (INFERRED)", T_SHEET), ("thread and inner jack (POLY .XX, reference only)", 2 * T_POLY),
             ("O-ring installed (INFERRED)", T_O), ("plate", T_RFP), ("gasket", T_GASK)]
    print("  inside: the inner jack ends %.2f past the wall's inner face; the plug reaches X %.2f at Z %.1f (the axis rises %.2f over that reach with the wall's 2 degree normal)" % (
        in_jack, x_end, AX_Z, TW * (in_jack + PLUG_L)))
    z_head_top = max(s[1] for s in RFP_SCREWS) + HEAD_R
    row("M10", "highest part inside an end wall (the entry plate's top screw heads, Z %.2f) below the frame skirt" % z_head_top, MIN_MECH, zb_nom - z_head_top, skirt_tols + t_mark)
    pitch = min(b[1] - a[1] for a, b in zip(SITES_W, SITES_W[1:]))
    rib_head = min(abs(abs(s[0]) - r) - HEAD_R - 0.91 for s in RFP_SCREWS for r in (0.0, 76.2))
    row("M11", "inside hardware bearing on an end wall to its ribs at Y 0, +-76.2 (the entry plate's screw heads)", MIN_MECH, rib_head,
        [("rib per wall", T_WALL), ("hole marking", T_JACK)])
    row("M11a", "wall web between neighbouring arrestor holes (27 at a %.0f pitch)" % pitch, MIN_WEB, pitch - 2 * WALL_HOLE_R, [("hole marking, two holes", 2 * T_JACK)])
    all_sites = [(y, AX_Z) for _, y in SITES_ALL]
    web_s = min((math.hypot(s[0] - a[0], s[1] - a[1]) - WALL_HOLE_R - RFP_SH_R, s, a) for s in RFP_SCREWS for a in all_sites)
    row("M11b", "wall web, arrestor hole to entry-plate screw hole (screw %+.0f, %.2f, beside the west wall's %+.0f site)" % (web_s[1][0], web_s[1][1], web_s[2][0]),
        MIN_WEB, web_s[0], [("hole marking, two holes", 2 * T_JACK)])
    band_r = min(min(RFP["y"] - abs(y) - WALL_HOLE_R, RFP["z1"] - AX_Z - WALL_HOLE_R, AX_Z - WALL_HOLE_R - RFP["z0"]) for _, y in SITES_ALL)
    band_s = min(min(RFP["y"] - abs(s[0]) - RFP_SH_R, RFP["z1"] - s[1] - RFP_SH_R, s[1] - RFP_SH_R - RFP["z0"]) for s in RFP_SCREWS)
    row("M11c", "gasket band from a wall hole to the entry plate's edge (arrestor holes %.2f, 5.0 screw holes %.2f)" % (band_r, band_s), MIN_BAND, min(band_r, band_s),
        [("hole marking", T_JACK), ("plate marking", T_JACK)])
    row("M12", "entry plate's top edge below the end-wall features at Y 0 and +-79.0 (Z %.2f)" % FEAT_Z_LOW, MIN_MECH, FEAT_Z_LOW - RFP["z1"], [("case Z (INFERRED)", T_CASE_Z), ("plate marking", T_JACK)])
    flat_y = HY0 + WALL_T + TW * RFP["z0"] - OUT_CORNER_R
    row("M12b", "entry plate's Y edge on the end wall's flat outer skin (flat to |Y| %.2f at Z %.2f)" % (flat_y, RFP["z0"]), MIN_MECH, flat_y - RFP["y"],
        [("case per wall", T_WALL), ("plate marking", T_JACK), ("plate outline", T_OUTLINE)])
    web = RFP_T - SPOT_DEPTH
    o_bound = A_THD - 2 * T_POLY - T_SPOT - web - NUT_T              # the installed O-ring M13 takes with the thread's allowance doubled
    print("  on the thread's .47 (%.2f): the O-ring %.2f +-%.2f, the %.1f web under the spot-face, then washer and nut %.1f; without the spot-face the 6.0 plate"
          " leaves %.2f nominal and %.2f at the worst" % (A_THD, O_NOM, T_O, web, NUT_T, A_THD - O_NOM - RFP_T - NUT_T, A_THD - O_NOM - RFP_T - NUT_T - T_POLY - T_O - T_RFP))
    row("M13", "arrestor nut fully on its thread (.47: O-ring %.2f, %.1f web under the spot-face, nut and washer %.1f)" % (O_NOM, web, NUT_T), 0.0,
        A_THD - O_NOM - web - NUT_T, [("thread (POLY .XX, reference only)", T_POLY), ("O-ring installed (INFERRED)", T_O), ("web under the spot-face (drawing)", T_SPOT)],
        "a condition", open_="the O-ring's height, drawn %.2f but not dimensioned, decides it; met with the thread's allowance doubled for one installed up to %.2f" % (
            O_FREE, o_bound))
    row("M13b", "nut and washer (%.1f, from the spot-face floor) inside the wall hole's depth (plate, gasket, wall)" % NUT_T, 0.0,
        RFP_T + GASK + WALL_T - web - NUT_T, [("plate", T_RFP), ("web under the spot-face (drawing)", T_SPOT), ("wall thickness (INFERRED)", T_SHEET), ("gasket", T_GASK)],
        "a condition")
    row("M13c", "nut and washer (%.1f) inside the 27 wall hole, radial" % (2 * NUT_R), 0.0, WALL_HOLE_R - NUT_R,
        [("hole marking", T_JACK), ("plate marking", T_JACK), ("plate hole position", T_MACH), ("arrestor in its 16.3 hole", F_THD)], "a condition")
    row("M13d", "nut and washer (%.1f) inside the %.1f spot-face, radial" % (2 * NUT_R, SPOT_D), 0.0, SPOT_D / 2 - NUT_R,
        [("spot-face on its hole (machined)", T_MACH), ("arrestor in its 16.3 hole", F_THD)], "a condition")
    band_sf = min(RFP["y"] - abs(y) for _, y in SITES_ALL) - SPOT_D / 2
    print("  the spot-faces keep %.2f of the plate's back to its Y edge at the outermost sites (%.2f at the worst of the machined place and the outline), the"
          " gasket's land on the plate; its land on the wall is M11c's" % (band_sf, band_sf - T_MACH - T_OUTLINE))
    tall = [((113.0, -99.0, 165.0, -43.0), 21.0, "RockBLOCK"), ((130.0, -43.0, 161.0, 45.0), 12.0, "LimeSDR"), ((125.5, 45.5, 162.0, 67.0), 5.0, "radio modules"),
            ((-162.0, 81.0, -142.0, 98.0), 14.0, "J_ETH"), ((-161.5, 58.5, -142.5, 77.5), 7.0, "T1 magnetics"), ((-152.0, -97.0, -116.0, -69.0), 10.0, "west headers")]
    plug_lo = AX_Z - PLUG_R
    hits = []
    for (x0, y0, x1, y1), h, name in tall:
        top = B_TOP + h
        edge_x = max(abs(x0), abs(x1))
        sites = SITES_E if x0 > 0 else SITES_W
        ys = [y for _, y in sites if y + PLUG_R > y0 - 2.0 and y - PLUG_R < y1 + 2.0]
        if not ys: continue
        z_clear = plug_lo - top
        hits.append((x_end - edge_x, name, top, z_clear, ys))
    for gx, name, top, zc_, ys in sorted(hits):
        print("  plug end X %.2f against %s (edge |X| %.1f, Z %.1f..%.1f) at Y %s: the plug's Z %.1f..%.1f overlaps it, X gap %.2f" % (
            x_end, name, x_end - gx, B_TOP, top, ", ".join("%+.0f" % y for y in ys), plug_lo, AX_Z + PLUG_R + TW * (in_jack + PLUG_L), gx))
    g_min = min(hits)
    row("M18", "jumper plug's inner end to B16's tall parts in X (tightest: %s, which it overlaps in Y and Z)" % g_min[1], MIN_MECH, g_min[0],
        t_end + [("stack placement", T_STACK), ("B16 outline", 0.1)])
    row("M18b", "neighbouring arrestor bodies outside (%.2f across at the %.0f pitch)" % (A_W, pitch), MIN_MECH, pitch - A_W,
        [("plate hole positions, two", 2 * T_MACH), ("arrestors in their 16.3 holes, two", 2 * F_THD)])
    y_plug = max(abs(y) for _, y in SITES_ALL) + PLUG_R
    row("M18c", "outermost plug (west wall) to the setting legs' inner face in Y (the plug's X range covers the column's)", MIN_MECH, LEG_Y[0] - y_plug,
        [("leg against the case centre", sum(t for _, t in LEG_IN_CASE)), ("plate marking", T_JACK), ("plate hole position", T_MACH),
         ("arrestor in its 16.3 hole", F_THD)])
    z_bot = min(s[1] for s in RFP_SCREWS) - HEAD_R
    head_in_x = hx(z_bot) - HEAD_IN
    row("M4c", "pack block's east face (X %.2f) to the entry plate's bottom screw heads (inner face X %.2f)" % (PACK_EAST, head_in_x), MIN_MECH,
        head_in_x - PACK_EAST, [("case per wall", T_WALL), ("web interior, against STEP", 9.68 - 8.38), ("pack placed by hand (INFERRED)", 1.0)])
    row("M21g", "setting leg's column (X %.2f) to the entry plate's screw heads at |Y| 100 (X %.2f), in X" % (LEG_X[1], head_in_x), MIN_MECH,
        head_in_x - LEG_X[1], LEG_IN_CASE + [("case per wall", T_WALL)])
    print("  entry-plate screw heads to the end-wall ribs at Y 0 and +-76.2 (half-width 0.91): %.2f; the arrestor holes cut ribs where they cross them, nothing bears there" % rib_head)
    to_rib = {abs(y): min(abs(abs(y) - r) for r in (0.0, 76.2)) - WALL_HOLE_R - 0.91 for _, y in SITES_ALL}
    print("  27 mm holes to the nearest rib's base (half-width 0.91), per |Y|: %s (negative: the hole cuts into the rib's base; the hole at Y 0 crosses its rib)" % ", ".join(
        "%.0f: %+.2f" % (y, g) for y, g in sorted(to_rib.items())))
    y_out = hx(AX_Z) + WALL_T + GASK + RFP_T + O_FREE + A_OUT + T_POLY
    print("  outside: the bodies reach X +-%.1f (the rim flange +-205.74, the drawing's exterior 411): the case is about %.0f mm longer over the arrestor rows" % (y_out, 2 * y_out - 411.0))
    blank = 2 * RFP["y"] * (RFP["z1"] - RFP["z0"]) * RFP_T; hole_v = math.pi / 4 * (PLATE_HOLE ** 2 * RFP_T + (SPOT_D ** 2 - PLATE_HOLE ** 2) * SPOT_DEPTH)
    print("  mass: the east plate (%d holes) about %.0f g, the west (%d holes) about %.0f g; twelve arrestors %.0f g" % (
        n_e, (blank - n_e * hole_v) * 2.70e-3, n_w, (blank - n_w * hole_v) * 2.70e-3, 12 * 0.25 * 453.59))
    # the eight M4 x 12 from inside: they must start in their wall holes, their washers must cover those holes, their tips must stay inside the plate
    # (at |Y| 100 beside the west wall's +-93 sites an arrestor body lies over them) and they must engage the thread
    float_m4 = (2 * RFP_SH_R - M4_MAJ) / 2                         # the largest M4 must start in its hole
    float_m4_min = (2 * RFP_SH_R - M4_MIN) / 2                     # the smallest can sit anywhere in it
    row("M11e", "each entry-plate M4 (%.2f) starts in its %.1f wall hole: float against hole marking and tapped position" % (M4_MAJ, 2 * RFP_SH_R), 0.0, float_m4,
        [("wall hole marked from the template", T_JACK), ("tapped hole position in the plate", T_MACH)], "a condition")
    row("M11f", "sealing washer's rubber face (%.1f across) covers its %.1f wall hole, the screw anywhere in its float" % (SEAL_D, 2 * RFP_SH_R), 0.0, SEAL_D / 2 - RFP_SH_R,
        [("screw in its float (smallest M4)", float_m4_min)], "a condition")
    eng = SCREW_L - WASH_T - WALL_T - GASK
    eng_tols = [("screw length (ISO 7380 js15, INFERRED)", T_SCREW), ("washer (INFERRED)", T_WASH), ("wall thickness (INFERRED)", T_SHEET), ("gasket", T_GASK)]
    print("  M4 x 12 entry-plate screws: washer %.1f, wall %.2f and gasket %.1f take %.2f, leaving %.2f of thread in the %.1f plate; %.2f to %.2f over the chain" % (
        WASH_T, WALL_T, GASK, WASH_T + WALL_T + GASK, eng, RFP_T, eng - sum(t for _, t in eng_tols), eng + sum(t for _, t in eng_tols)))
    row("M11d", "entry-plate screw tips inside the plate's outer face (M4 x 12: nothing stands out under an arrestor)", 0.0, RFP_T - eng,
        [("plate %.1f (INFERRED)" % RFP_T, T_RFP)] + eng_tols, "a condition")
    row("M11g", "entry-plate screws' thread engaged in the plate (at least two pitches, INFERRED)", ENG_MIN, eng, eng_tols)
    print("  a socket of 30 across (INFERRED, over the inner jack) on one nut, whose hex stands above the plate's back, clears its neighbour by %.2f on the bench" % (
        pitch - 15.0 - NUT_R))

    # ---------------- C2: the jumpers from the inner jacks to E6's float clamps
    print("\n== (G) C2: the jumpers from the arrestors' inner jacks to E6's float clamps (RG-316, ASSEMBLY.md:134)")
    CAB_D, R_B = 2.49, 12.5                  # RG-316 0.098 in over the jacket (MIL-DTL-17 class, standard not held, INFERRED); bend radius 12.5 (ASSEMBLY.md:108, :134)
    D_F, PHI = 16.0, math.radians(30.0)      # the plug's crimp ferrule ends within 16.0 of its mating axis (INFERRED class); each east plug turned 30 degrees below the wall's direction
    T_TIE = 0.5                              # a bundle laid by its ties within +-0.5 of its drawn place (INFERRED)
    BUNDLE = 2 * CAB_D                       # an east bundle: two RG-316 wide and two high, four cables at most
    R_C = R_B + CAB_D / 2                    # a two-wide bundle's centreline radius, so that its inner cable bends at R_B
    FRONT_E = ("5G MAIN", "5G DIV", "5G ANT3", "IRIDIUM"); BACK_E = ("LORA",)
    CLAMP_X = {"VHF": -52.0, "HF": -38.0, "WIFI 2.4": -24.0, "GNSS": -10.0, "SDR": 4.0, "WIFI P2P A": 18.0, "WIFI P2P B": 32.0,
               "5G MAIN": 60.0, "5G DIV": 74.0, "IRIDIUM": 88.0, "LORA": 102.0, "5G ANT3": 46.0}   # gen_pcb_e.py:16 RF_SITES; ANT3 at board A's X +46 (D-07)
    CLAMP_Y, STRIP_S, STRIP_N, Y_LANE_N = -66.0, -113.0, -45.0, -35.0   # clamps at Y -66 and the strip's edges (gen_pcb_e.py:15, :79); the west lane north of the strip (INFERRED)
    GROUP_END = 205.5 / 2                    # the pack group's ends in Y, centred (M5)
    t_leg = sum(t for _, t in LEG_IN_CASE); u_leg = sum(unstated(l, t) for l, t in LEG_IN_CASE)
    t_endw = sum(t for _, t in t_end); u_endw = sum(unstated(l, t) for l, t in t_end)
    zmid = (PACK_TOP + plug_lo) / 2
    band = (zmid - BUNDLE / 2, zmid + BUNDLE / 2)
    z_lo, z_up = band[0] + CAB_D / 2, band[1] - CAB_D / 2          # the centres of the band's lower and upper layers
    print("  east: every plug's cable leaves along the wall toward its bundle's end, the plug turned 30 degrees down; the cables run in a bundle %.2f x %.2f over the pack's" % (BUNDLE, BUNDLE))
    print("  outer strip in the slot under the plugs (Z %.2f..%.2f), in the lane between B16's edge and the legs' columns, and go down beyond the legs" % band)
    print("  front bundle: %s; back bundle: %s; west: every cable leaves downward and falls to the floor outboard of B16's edge" % (", ".join(FRONT_E), ", ".join(BACK_E)))
    row("M17a", "east bundle (two RG-316 high, %.2f) between the pack's top (Z %.2f) and the plugs' undersides (Z %.1f)" % (BUNDLE, PACK_TOP, plug_lo),
        2.0, plug_lo - PACK_TOP - BUNDLE, [("floor flatness under the pack (INFERRED)", T_FLOOR), ("plate marking", T_JACK), ("arrestor hole in the plate", T_MACH),
                                           ("arrestor in its 16.3 hole", F_THD)])
    # each cable's own path: body surface, ferrule at PHI, an arc of R_B to horizontal, then flat in the band; the neighbour's body is a circle r PLUG_R about its axis
    fer = (D_F * math.cos(PHI), AX_Z - D_F * math.sin(PHI))
    ctr = (fer[0] + R_B * math.sin(PHI), fer[1] + R_B * math.cos(PHI))
    land = (ctr[0], ctr[1] - R_B)
    path = [((PLUG_R + (D_F - PLUG_R) * i / 200.0) * math.cos(PHI), AX_Z - (PLUG_R + (D_F - PLUG_R) * i / 200.0) * math.sin(PHI)) for i in range(201)]
    path += [(ctr[0] - R_B * math.sin(PHI * (1 - i / 200.0)), ctr[1] - R_B * math.cos(PHI * (1 - i / 200.0))) for i in range(201)]
    d_drop = min(math.hypot(p[0] - pitch, p[1] - AX_Z) for p in path) - PLUG_R - CAB_D / 2    # the drop itself (ferrule and arc) to the next plug's body
    d_pass = plug_lo - band[1]                                       # a cable in the band's upper layer, under the next plug's body
    print("  each east cable (the class's reach %.1f, turned %.0f degrees): its ferrule ends at %.2f along the wall and Z %.2f, it lands at %.2f from its site, Z %.2f,"
          " the band's middle; the layers' centres are Z %.3f and %.3f; the neighbour's axis is at %.0f" % (D_F, math.degrees(PHI), fer[0], fer[1], land[0], land[1], z_lo, z_up, pitch))
    print("  the drop keeps %.2f from the next plug's body; a cable in the band's upper layer passes under that body with %.2f" % (d_drop, d_pass))
    row("M17b", "east cables under the next plug's body: the band's upper layer (the drop itself keeps %.2f)" % d_drop, MIN_MECH, min(d_drop, d_pass),
        [("bundle ties (INFERRED)", T_TIE), ("plate marking", T_JACK), ("arrestor hole in the plate", T_MACH), ("arrestor in its 16.3 hole", F_THD)])
    # the layering under a plug, as laid out: the cables passing it in the band's lower layer and its inner upper place (one cable inboard of the
    # plug's cable axis), the plug's own cable in the outer upper place; the tightest is the plug with the most cables passing under it
    passing = {}
    for name, y in SITES_E:
        grp = FRONT_E if name in FRONT_E else BACK_E
        passing[name] = [n for n, y2 in SITES_E if n in grp and ((y2 > y) if grp is FRONT_E else (y2 < y))]
    most = max(SITES_E, key=lambda s: len(passing[s[0]]))[0]
    d_f_fit = (AX_Z - z_up - R_B * (1 - math.cos(PHI))) / math.sin(PHI)       # the reach that lands the cable at its place at PHI
    lo_, hi_ = 0.0, PHI
    for _ in range(60):                                                          # the turn that lands the class's reach at its place
        mid_ = (lo_ + hi_) / 2
        if AX_Z - D_F * math.sin(mid_) - R_B * (1 - math.cos(mid_)) > z_up: lo_ = mid_
        else: hi_ = mid_
    fer_max = 2 * (math.hypot(CAB_D, fer[1] - z_up) - CAB_D / 2)                 # the widest ferrule the inner upper place clears at the ferrule's end
    print("  as laid out under %s (%d passing: %s): the passing cables in the band's lower layer and its inner upper place, %s's own cable in the outer upper place" % (
        most, len(passing[most]), ", ".join(passing[most]), most))
    print("  at the class's reach it lands %.2f below that place, onto the passing cable under it; it lands at its place for a reach of %.2f or less, or turned %.1f degrees;"
          " the inner upper place clears the ferrule's end only for a ferrule %.2f across or less (the class does not bound it)" % (
          z_up - land[1], d_f_fit, math.degrees(lo_), fer_max))
    lay_tols = [("bundle ties (INFERRED)", T_TIE), ("plate marking", T_JACK), ("arrestor hole in the plate", T_MACH), ("arrestor in its 16.3 hole", F_THD)]
    row("M17g", "east layering under %s (%d passing): its own cable at its place, clear of the cable below it" % (most, len(passing[most])),
        0.0, (land[1] - z_lo) - CAB_D, lay_tols, "a condition",
        open_="best +0.00 for a reach of %.2f or less or turned %.1f degrees; the plug's reach and ferrule decide it" % (d_f_fit, math.degrees(lo_)))
    # the inboard column under the plugs, one cable inboard of the plug's cable axis, against B16's edge: the class puts that axis anywhere within
    # PLUG_CABLE of the plug's inner end; the inner end is the worst
    col_in = x_end - CAB_D - CAB_D / 2
    x_tols = t_end + [("stack placement", T_STACK), ("B16 outline", 0.1)]
    wc_a0 = col_in - B_OUT[0] - sum(t for _, t in x_tols)
    a_min = MIN_MECH - wc_a0
    best_n = col_in + PLUG_CABLE - B_OUT[0]
    b16_lo = B_UNDER - (VHB_T + 2 * LAM)
    print("  the inboard column, with the plug's cable axis at its inner end (X %.2f): inner face X %.2f, %.2f from B16's edge (%.2f at the worst); with the axis %.1f"
          " from that end %.2f (%.2f); met at the worst for an axis %.2f or more from the end with a ferrule %.2f across or less (a wider one moves the column in by"
          " half its excess); B16's underside (Z %.2f at the worst) lies inside the band (Z %.2f..%.2f), so both layers meet its edge in plan" % (
          x_end, col_in, col_in - B_OUT[0], wc_a0, PLUG_CABLE, best_n, best_n - sum(t for _, t in x_tols), a_min, fer_max, b16_lo, band[0], band[1]))
    row("M17x", "east bundle's inboard column under the plugs to B16's edge (X %.1f), axis at the plug's inner end" % B_OUT[0], MIN_MECH, col_in - B_OUT[0],
        x_tols, open_="best +%.2f / +%.2f with the axis %.1f from the end, met for %.2f or more; the plug's axis and ferrule decide it" % (
            best_n, best_n - sum(t for _, t in x_tols), PLUG_CABLE, a_min))
    n_pass = {name: len([n for n, y2 in SITES_E if (n in BACK_E or n == "IRIDIUM") and y2 < y]) if (name in BACK_E or name == "IRIDIUM")
              else len([n for n, y2 in SITES_E if n in FRONT_E and n != "IRIDIUM" and y2 > y]) for name, y in SITES_E}
    print("  levers, each to be judged with the picked plug: %s turned less (no plug lies beyond it); a plug whose ferrule ends %.2f or less from its axis; IRIDIUM in the"
          " back bundle, which leaves at most %d cables passing under a plug (%s)" % (most, d_f_fit, max(n_pass.values()),
          ", ".join("%s %d" % (n, c) for n, c in n_pass.items() if c)))
    # the outermost east cable must be inboard of the legs' columns (in the lane) before it reaches the leg band; after its own cable lands, the
    # two-wide bundle bends, at the centreline radius R_C
    y_out_e = max(abs(y) for _, y in SITES_E)
    cab_x = x_end + PLUG_CABLE                                       # the plug's cable axis at the class's outboard end
    lane_out = LEG_X[0] - MIN_MECH - CAB_D / 2                       # the outer cable's axis at the leg band
    def shift(dx): return math.sqrt(4 * R_C * dx - dx * dx) if dx > 0 else 0.0     # the run an S-bend of R_C needs for an offset dx
    need = y_out_e + land[0] + shift(cab_x - lane_out)
    avail = LEG_Y[0] - MIN_MECH - CAB_D / 2
    need_w = y_out_e + T_JACK + T_MACH + F_THD + land[0] + shift(cab_x - lane_out + t_endw + t_leg)
    avail_w = avail - t_leg
    need_w2 = y_out_e + 2 * T_JACK + T_MACH + F_THD + land[0] + shift(cab_x - lane_out + t_endw + u_endw + t_leg + u_leg)
    avail_w2 = avail - t_leg - u_leg
    rss_x = math.sqrt(sum(t * t for _, t in t_end) + sum(t * t for _, t in LEG_IN_CASE))
    need_r = y_out_e + math.sqrt(T_JACK ** 2 + T_MACH ** 2 + F_THD ** 2) + land[0] + shift(cab_x - lane_out + rss_x)
    avail_r = avail - math.sqrt(sum(t * t for _, t in LEG_IN_CASE))
    print("  outermost east cable (|Y| %.0f): its axis at X %.2f at most, the lane's outer cable at X %.2f: the bundle's S-bend of %.2f in X at R %.3f needs %.2f of run;"
          " in the lane by |Y| %.2f (worst %.2f) against %.2f (worst %.2f)" % (y_out_e, cab_x, lane_out, cab_x - lane_out, R_C, shift(cab_x - lane_out), need, need_w, avail, avail_w))
    need_93 = 93.0 + land[0] + shift(cab_x - lane_out)
    print("  from |Y| 93, the previous issue's outermost east site, it would be in the lane only by |Y| %.2f, %.2f short of %.2f at nominal" % (need_93, need_93 - avail, avail))
    row("M17c", "outermost east cable (|Y| %.0f) and its bundle (R %.2f) inboard of the legs' columns before them, in Y" % (y_out_e, R_C), 0.0, avail - need, [],
        "a condition", worst=avail_w - need_w, rss=avail - avail_r + need_r - need, wc2=avail_w2 - need_w2)
    row("M17d", "east bundle (%.2f wide) in the lane, B16's edge (X %.1f) to the legs' columns (X %.2f): free width" % (BUNDLE, B_OUT[0], LEG_X[0]), 2.0,
        (LEG_X[0] - B_OUT[0]) - BUNDLE, [("stack placement", T_STACK), ("B16 outline", 0.1), ("leg against the case centre", t_leg)])
    U_V = 116.5                                                      # the bundle's inner cable on the way down, beyond the leg
    u_s = U_V - R_B
    z_c = band[0] + CAB_D / 2 - R_B
    u_leg = LEG_Y[1] + t_leg
    z_low = z_c + math.sqrt(R_B ** 2 - (u_leg - u_s) ** 2) - CAB_D / 2
    print("  the bundle bends down (inner cable R %.1f) from |Y| %.2f, %.2f beyond the pack group's end (%.2f; placed within 1.0) with its full height over it, and goes down"
          " at |Y| %.2f..%.2f; over the leg's outer face at the worst (|Y| %.2f) its underside is at Z %.2f, above the leg's gusset (below Z 30)" % (
        R_B, u_s, u_s - GROUP_END, GROUP_END, U_V - CAB_D / 2, U_V + CAB_D + CAB_D / 2, u_leg, z_low))
    row("M17e", "east bundle going down beyond the leg: its inner face (|Y| %.2f) to the leg's outer face (|Y| %.1f)" % (U_V - CAB_D / 2, LEG_Y[1]), MIN_MECH,
        U_V - CAB_D / 2 - LEG_Y[1], [("leg against the case centre", t_leg), ("bundle ties (INFERRED)", T_TIE)])
    row("M17f", "east front bundle on the floor beside the dock strip's south edge (|Y| %.0f, gen_pcb_e.py:15)" % -STRIP_S, 0.0, U_V - CAB_D / 2 + STRIP_S,
        [("strip placement", T_STACK), ("bundle ties (INFERRED)", T_TIE)], "a condition")
    row("M17w", "west cables (leaving downward, axis within %.1f of the plug's end) outboard of B16's edge" % PLUG_CABLE, MIN_MECH, x_end - CAB_D / 2 - B_OUT[0],
        t_end + [("stack placement", T_STACK), ("B16 outline", 0.1)])
    fil_h = lambda d: FIL_R - math.sqrt(max(FIL_R ** 2 - d * d, 0.0)) if d > 0 else 0.0     # the floor fillet's height d past its tangent
    z_turn_w = fil_h(x_end + PLUG_CABLE / 2 - FLAT_X) + CAB_D / 2 + R_B
    print("  west: the ferrule ends at Z %.1f, %.1f above where the turn onto the floor must start (Z %.2f); below the plugs the west end has no pack, and the drop zone"
          " X %.0f to the wall, |Y| up to %.0f, is the jumpers'" % (AX_Z - D_F, AX_Z - D_F - z_turn_w, z_turn_w, B_OUT[0], y_plug))
    # route lengths, connector axis to connector axis, on the route drawn here and an assumed floor run to each clamp (INFERRED)
    q = math.pi / 2
    x_lane = (B_OUT[0] + LEG_X[0]) / 2
    x_after = x_lane - R_C
    z_floor_c = fil_h(U_V + CAB_D / 2 - FLAT_Y) + CAB_D              # the bundle's centre on the long wall's floor fillet
    ang = math.acos(1 - (x_end + PLUG_CABLE / 2 - x_lane) / (2 * R_B))
    s_shift, a_shift = 2 * R_B * math.sin(ang), 2 * R_B * ang
    lengths = []
    for name, y in SITES_E:
        sg = -1.0 if name in FRONT_E else 1.0
        y1 = y + sg * (land[0] + s_shift)
        run = abs(sg * u_s - y1)
        L = D_F + R_B * PHI + a_shift + run + q * R_C + (zmid - R_C - (z_floor_c + R_C)) + q * R_C + (x_after - (CLAMP_X[name] + R_C)) + q * R_C
        L += abs(sg * (U_V + CAB_D / 2 - R_C) - CLAMP_Y)
        lengths.append((name, "east", "front" if sg < 0 else "back", L))
    z_start_w = AX_Z - D_F
    for name, y in SITES_W:
        xw = x_end + PLUG_CABLE / 2
        L = D_F + (z_start_w - z_turn_w) + q * R_B
        if y - CAB_D / 2 - MIN_MECH < STRIP_N:
            L += (Y_LANE_N - R_B) - (y + R_B) + q * R_B + ((CLAMP_X[name] - R_B) - (-xw + R_B)) + q * R_B + ((Y_LANE_N - R_B) - CLAMP_Y)
        else:
            L += (CLAMP_X[name] - R_B) - (-xw + R_B) + q * R_B + ((y - R_B) - CLAMP_Y)
        lengths.append((name, "west", "north of the strip", L))
    print("  route lengths, connector axis to connector axis (the floor run to each clamp assumed, INFERRED): %s" % "; ".join(
        "%s %.0f" % (n, L) for n, w, e, L in lengths))
    Ls = [L for _, _, _, L in lengths]
    print("  %d of %d within the 150 to 250 of ASSEMBLY.md:134; %.0f to %.0f, cut with a 20 mm service allowance (INFERRED): %.0f to %.0f" % (
        sum(1 for L in Ls if 150.0 <= L <= 250.0), len(Ls), min(Ls), max(Ls), min(Ls) + 20.0, max(Ls) + 20.0))

    print("\n  %-5s %-104s %6s %8s %8s %8s %9s  %s" % ("#", "margin", "min", "nominal", "worst", "RSS low", "worst x2", "verdict"))
    for r in ROWS:
        print("  %-5s %-104s %6.2f %+8.2f %+8.2f %+8.2f %+9.2f  %s%s" % (r["key"], r["label"][:104], r["min"], r["nom"], r["wc"], r["rss_low"], r["wc2"], r["ok"],
              ("  (" + r["note"] + ")") if r["note"] else ""))
    print("\n  %d rows: %d MET, %d OPEN, %d NOT MET. 'worst x2' is the worst case with every allowance no source states (the case's, and the build's) taken"
          " twice; a row below its minimum there is OPEN (the review's rule of 26 Sep 2026, section 4, read by the session as a sensitivity test)" % (
          len(ROWS), sum(r["ok"] == "MET" for r in ROWS), sum(r["ok"] == "OPEN" for r in ROWS), sum(r["ok"] == "NOT MET" for r in ROWS)))
