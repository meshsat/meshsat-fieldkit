#!/usr/bin/env python3
"""Option A(i) mechanical work package (MESHSAT-1357, stream a1mech, 29 September 2026): the lid battery module, its clearances over the
face, the hinge harness, the mass and the open-lid stability, and the base pockets' 4S6P, all at the worst of Peli's figures.

Plain Python (no CAD import): every number printed comes from a constant below, which names its source, or from the arithmetic shown.
The drawing set is v2/cad/lid_pack_a1_drawing.py, which imports this module. Usage: lid_pack_a1.py [out file]  (default: stdout).

Frame: case X along the long axis (east +), Y toward the hinge (back) wall, Z up from the base floor, the lid closed. A lid item is
placed by its plan rectangle and its DEPTH below the lid's inner ceiling. Prototype design, AI review: nothing built, bought or fitted.

Status words: VERIFIED (read from a maker's file), INFERRED (derived, or a class figure), ESTIMATE (a stated guess), ASSUMPTION (a
figure another stream owns, carried until it reports), TBD (no source). Verdicts follow CASE-MARGINS.md section 1: MET only if the
row meets its minimum with every unstated allowance taken twice (a sensitivity test, not a bound); OPEN if it meets at the worst only
or rests on a TBD; NOT MET if it fails at the worst.
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ecad", "tools"))
import panel1450 as P   # the face positions (plain Python)

# ---------------------------------------------------------------- the lid (Peli 1451-931 top STEP, CASE-MARGINS.md 2.1, 2.2; r2 record)
ROOM_NOM, ROOM_WORST, ROOM_X2 = 47.92, 44.39, 42.11   # face top Z 106.52 to the ceiling 154.44; worst 108.27 to 152.66; x2 (r2 record B)
CEIL_Z_NOM = P.PELI["rim_z"] + P.PELI["lid_z"]       # 154.44
FACE_Z_NOM = P.FACE_TOP_Z                             # 106.52
CEIL_FLAT = (173.08, 115.93)      # flat ceiling half extents, STEP #736 (346.16 x 231.86)
CEIL_FILLET_R = 16.26             # ceiling-to-wall fillets, STEP #594/#1539/#644/#1432, centres 16.26 below the ceiling
LID_STEP = 1.27                   # the small R 1.27 step where the fillet meets the drafted wall (#135, #1222, #1680, #1697)
LID_WALL_AT_PART = (186.94, 130.935)   # lid cavity half extents at the parting plane (#410/#540, #1467/#1744: 373.88 x 261.87)
LID_RIBS = 0                      # the lid STEP's cavity faces are walls, fillets, the R 1.27 step and the ceiling: no rib (VERIFIED, faces list)
MIN_CLEAR = 1.0                   # the stated minimum of every face-room row (r2 record B)
PLAN_ALLOW = 0.76 + 0.30          # lid's place on the base (the case class, INFERRED) + a bonded plate placed by a printed locator (INFERRED)


def fillet_depth(d_out):
    """Depth below the ceiling of the lid's inner surface at a distance d_out (mm) outboard of the flat ceiling's edge."""
    if d_out <= 0: return 0.0
    if d_out >= CEIL_FILLET_R: return None
    return CEIL_FILLET_R - math.sqrt(CEIL_FILLET_R ** 2 - d_out ** 2)


# ---------------------------------------------------------------- face parts standing into the lid (plan rect, height above the face top)
def rect_c(cx, cy, w, h): return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)

FACE = []   # (ref, rect, height or None for TBD, source)
xw = P.XENARC["window"]
FACE.append(("XENARC_WINDOW", rect_c(P.XENARC["c"][0], P.XENARC["c"][1], xw[0], xw[1]), 0.80,
             "a bound: the glass level with the plate, the ruling of 2 Sep 2026 (appendix 14.6) lets a display stand 0.8 proud (r2 record B)"))
for i, (x, y) in enumerate(P.XENARC["frame_holes"]):
    FACE.append(("XFRAME_%d" % (i + 1), rect_c(x, y, 7.0, 7.0), 4.00, "M4 cap head class 7.0 x 4.00 (ISO 4762 class, INFERRED; r2 record B)"))
FACE.append(("EPAPER_LENS", rect_c(P.EPAPER["c"][0], P.EPAPER["c"][1], *P.EPAPER["lens"]), 0.05, "panel1450 EPAPER: ends 0.05 proud"))
for ref, c, hole, _d in P.BUTTONS:
    d = 25.2 if ref == "SW_MAIN" else 22.2
    FACE.append((ref, rect_c(c[0], c[1], d, d), 3.50 if ref == "SW_MAIN" else 2.50,
                 "C&K ATP19 (02/05/25) p2 and p4: head 2.00 on O-ring 1.50" if ref == "SW_MAIN" else "C&K ATP16 (5 Jul 22) pA-132, A-134: head 1.5 on O-ring 1.0"))
for ref, c, _n in P.STATUS_LEDS + P.BAR_LEDS:
    FACE.append((ref, rect_c(c[0], c[1], 4.0, 4.0), 1.50, "Mentor 1282.5004 (sheet ll14-14): B 9 - A 7.5"))
FACE.append(("U_LIGHT", rect_c(P.LIGHT_SENSOR[1][0], P.LIGHT_SENSOR[1][1], 4.0, 4.0), 1.50, "Mentor 1282.5004 light guide"))
FACE.append(("CAM1_WINDOW", rect_c(P.CAMERA[1][0], P.CAMERA[1][1], 12.0, 12.0), 0.05, "an 8 mm sealed window, taken as the e-paper's 0.05 (INFERRED)"))
for ref, c in P.TOGGLES:
    # APEM 5000 series (RS copy) p13: lever -2V 14.75 above a 9.00 bushing; less the 3.0 plate, 20.75 over the face with no guard.
    # Guard: APEM switch guards series p2 (for 12000/3500/600H/6000; the CSG for the 5000 is not held): closed 22.00 (series 20) to
    # 28.00 (20PN) from the panel, cap 14.00 wide, support plate 17.00, 39.40 to 44.00 tall, 49.00 open arc: the class bound taken.
    FACE.append((ref + "_GUARD", rect_c(c[0], c[1], 14.0, 49.0), 28.00, "APEM guard class p2: 28.00 closed (20PN), cap 14.00 x 49.00 arc (INFERRED for the CSG)"))
    FACE.append((ref + "_PLATE", rect_c(c[0], c[1], 17.0, 49.0), 2.00, "guard support plate 17.00 wide, 2.00 high (INFERRED)"))
FACE.append(("SW_LIGHT", rect_c(P.LIGHT[1][0], P.LIGHT[1][1], 8.0, 20.0), 20.75, "NKK M2044 lever not read: bounded by the APEM figure (INFERRED)"))
# Floyd Bell MC-09-530-Q spec page 2: thread 0.46 in (11.7) through a panel up to 6.35, ring 0.31 in (7.9) thick, d 1.41 in (35.8), gasket
# 0.062 in (1.57); tolerance +-0.03 in (0.76): max(11.7 - 3.0 plate, 7.9 + 1.57) + 0.76 = 10.23
FACE.append(("BZ1", rect_c(P.SOUNDER[1][0], P.SOUNDER[1][1], 35.8, 35.8), 10.23, "Floyd Bell MC-09-530-Q p2: ring d 35.8; max(11.7-3.0, 7.9+1.57)+0.76"))
for ref, c in P.HEADSETS:
    FACE.append((ref, rect_c(c[0], c[1], 30.0, 30.0), None, "U-174/U panel jack: drawing owed (panel1450); 30 x 30 plan INFERRED, height TBD: nothing may stand over it"))
for i, (x, y) in enumerate(P.FRAME_BOSSES):
    FACE.append(("PLATE_SCREW_%d" % (i + 1), rect_c(x, y, 6.86, 6.86), 2.40, "6-32 pan head 6.86 x 2.4 (ASME B18.6.3 class, INFERRED)"))

# ---------------------------------------------------------------- the QMX set on the lid (r2 record, lid_tray_qmx_r2.py; unchanged here)
QMX = dict(rect=(83.2, -45.9, 171.0, 65.9), unit_face=29.30, frame=32.30, knobs=40.90, mass=0.372,
           right_panel_y=57.5, left_panel_y=-37.5, plug_rf=42.9, plug_usb=35.4, plug_dc=55.4, lead_r=20.0, rf_r=12.5)
# the DC lead of the r2 set looped back toward the hinge at R 20 WEST of the tray, where the lid pack now lies: it is re-routed EAST (SESSION,
# section 3 of the README): from the plug's end (Y -92.9) an R 20 turn east along Y -112.9, then R 20 north in the fillet lane X 174..184 to the hinge
DC_ROUTE = [(94.5, -37.5), (94.5, -92.9), (114.5, -112.9), (158.0, -112.9), (178.0, -92.9), (178.0, 100.0)]

# ---------------------------------------------------------------- the cell and the block (Samsung INR18650-35E spec Ver. 1.1; A06 block basis)
CELL_D, CELL_L, CELL_M = 18.55, 65.25, 0.050   # spec 3.10 and the drawing: diameter max 18.55, height max 65.25, weight 50 g max
CELL_AH, CELL_V = 3.35, 3.60                   # minimum capacity, nominal voltage (spec; ENERGY-RECONCILIATION section 8)
WRAP = 0.5                    # A06's wrap per side (pack_fit.py: 3 x 18.55 + 1.0 = 56.65)
END_GAP = 1.0                 # A06's joint: n cells along the axis take n x 65.25 + (n + 1) x 1.0 (133.5 for two)
NEST_DZ = math.sqrt(CELL_D ** 2 - (CELL_D / 2) ** 2)   # 16.065: a second layer in the grooves of the first
# module stack from the ceiling (the r2 lid plate's recipe): DP8005 bond 0.20, 5052-H32 plate 2.0, the block, a PORON 4701-30 pad 1.0
# (compressed from 1.59), a cover 1.25 (printed UL94 V-0 class shell 1.0 + 0.25 insulation, INFERRED) held by standoffs from the plate
BOND, PLATE, PAD, COVER = 0.20, 2.00, 1.00, 1.25
SIDE = COVER + 0.5            # cover wall and clearance beside the block, per side in Y
BAY = 7.0                     # each X end: the cover's flange on four M3 standoffs, the group links and the balance taps leave here
DEPTH1 = BOND + PLATE + (CELL_D + 2 * WRAP) + PAD + COVER               # one layer: 24.00
DEPTH2 = BOND + PLATE + (CELL_D + NEST_DZ + 2 * WRAP) + PAD + COVER     # two nested layers: 40.07
OWN = dict(bond=0.10, plate=0.13, standoff=0.10, cover=0.10)             # the module's own allowances, none stated by a source (INFERRED)
OWN_SUM = sum(OWN.values())
# the lid pack's protection board: ASSUMPTION, board P's own outline and tallest part until the electrical stream (fnd/a1elec) reports
P2 = dict(w=70.0, h=44.0, parts=16.17, standoff=3.0, board=1.6, mass=0.080)
P2_DEPTH = BOND + PLATE + P2["standoff"] + P2["board"] + P2["parts"]    # 22.97

# ---------------------------------------------------------------- the tablet (appendix 32.50 16d; REQ-011; SC-45: the model is a pick)
TABLET_8 = dict(name="8 inch rugged class", w=214.0, h=127.0, t=10.1, mass=0.44)   # INFERRED class envelope, no maker sheet held
TABLET_10 = dict(name="10 inch rugged class", w=243.0, h=170.0, t=10.2, mass=0.68)  # INFERRED class envelope, no maker sheet held
LIP, BRACKET_BACK, TAB_OWN = 3.0, 1.0, 0.40   # bracket lip over each edge (plan) and its thickness 1.5 below the screen; back plate 1.0
TAB_LIP_T = 1.5


def tablet_depth(t):
    return DEPTH1 + BRACKET_BACK + t["t"] + TAB_LIP_T


def overlap(a, b, grow=0.0):
    return a[0] - grow < b[2] and b[0] - grow < a[2] and a[1] - grow < b[3] and b[1] - grow < a[3]


def margins(depth, h, own):
    """nominal, worst, sensitivity margin of a lid item at `depth` over a face part of height h."""
    return ROOM_NOM - h - depth, ROOM_WORST - h - depth - own, ROOM_X2 - h - depth - 2 * own


def verdict(w, x2, tbd=False):
    if w < MIN_CLEAR: return "NOT MET"
    if tbd or x2 < MIN_CLEAR: return "OPEN"
    return "MET"


# ---------------------------------------------------------------- arrangements
def one_layer_fails(fr_h):
    h = fr_h
    return h is None or margins(DEPTH1, h, OWN_SUM)[1] < MIN_CLEAR


def slice_south(x0, x1, y_n):
    """The lowest south edge a slice's one-layer zone may take: the ceiling's flat edge less 1.0, or the north side (with the plan
    allowance) of any face part under the slice that the one-layer depth does not clear, or whose height is TBD."""
    lim = -(CEIL_FLAT[1] - 1.0)
    for ref, fr, h, _s in FACE:
        if one_layer_fails(h) and fr[0] - PLAN_ALLOW < x1 and x0 < fr[2] + PLAN_ALLOW and fr[3] + PLAN_ALLOW < y_n:
            lim = max(lim, fr[3] + PLAN_ALLOW)
    return lim


def cell_fp(c):
    return (c["x0"] - END_GAP, c["yc"] - CELL_D / 2 - WRAP, c["x1"] + END_GAP, c["yc"] + CELL_D / 2 + WRAP)


def l2_fp(c):
    reach = CELL_D / 2 + WRAP + COVER                  # the cover's step around a layer-2 cell
    return (c["x0"] - END_GAP, c["yc"] - reach, c["x1"] + END_GAP, c["yc"] + reach)


def lay(x_w, n_slices, y_n, tablet_rect):
    """Layer 1 across Y at the cell pitch from the north (hinge) side down to each slice's south limit; layer 2 in the grooves wherever
    its column meets every face row at the two-layer depth and does not overlap the tablet's bracket."""
    bx0 = x_w + BAY
    cells, dropped, south = [], [], []
    for s in range(n_slices):
        x0 = bx0 + END_GAP + s * (CELL_L + END_GAP)
        ys = slice_south(x0 - END_GAP, x0 + CELL_L + END_GAP, y_n)
        j_max = int((y_n - ys - 2 * SIDE - 2 * WRAP) // CELL_D)
        by0 = y_n - SIDE - WRAP - j_max * CELL_D
        south.append((x0 - END_GAP, x0 + CELL_L + END_GAP, by0 - WRAP - SIDE, j_max))
        for j in range(j_max):
            cells.append(dict(layer=1, s=s, j=j, x0=x0, x1=x0 + CELL_L, yc=by0 + CELL_D / 2 + j * CELL_D))
        for j in range(j_max - 1):
            c = dict(layer=2, s=s, j=j, x0=x0, x1=x0 + CELL_L, yc=by0 + CELL_D + j * CELL_D)
            fp = l2_fp(c)
            if tablet_rect and overlap(fp, tablet_rect):
                continue
            bad = [f for f in FACE if overlap(fp, f[1], PLAN_ALLOW) and (f[2] is None or margins(DEPTH2, f[2], OWN_SUM)[1] < MIN_CLEAR)]
            if bad:
                dropped.append((c, bad[0][0])); continue
            cells.append(c)
    return cells, dropped, south


def p2_candidates(x_w, x_e, y_n, south, tablet_rect):
    """P2 at a corner of the module, either way round, inside the module's outline and off the tablet's bracket."""
    out = []
    ys_min = min(s[2] for s in south)
    for (w, h) in ((P2["w"], P2["h"]), (P2["h"], P2["w"])):
        for cx in ("w", "e"):
            for cy in ("n", "s"):
                x0 = x_w + BAY if cx == "w" else x_e - BAY - w
                if cy == "n":
                    y1 = y_n - SIDE; y0 = y1 - h
                else:
                    sl = south[0] if cx == "w" else south[-1]
                    y0 = sl[2] + SIDE; y1 = y0 + h
                r = (x0, y0, x0 + w, y1)
                if tablet_rect and overlap(r, tablet_rect, 1.0): continue
                if any(overlap(r, f[1], PLAN_ALLOW) and (f[2] is None or margins(P2_DEPTH, f[2], OWN_SUM)[1] < MIN_CLEAR) for f in FACE): continue
                out.append(r)
    return out


def build(name, x_w, x_e, y_n, n_slices, tablet=None, tablet_rect=None, qmx=True):
    block_len = n_slices * CELL_L + (n_slices + 1) * END_GAP
    assert x_e - x_w >= block_len + 2 * BAY - 1e-9, (name, x_e - x_w, block_len + 2 * BAY)
    cells0, dropped, south = lay(x_w, n_slices, y_n, tablet_rect)
    best = None
    for r in p2_candidates(x_w, x_e, y_n, south, tablet_rect):
        keep = [c for c in cells0 if not overlap(cell_fp(c) if c["layer"] == 1 else l2_fp(c), r, 2.0)]
        if best is None or len(keep) > len(best[1]):
            best = (r, keep)
    if best is None:
        return None                                   # no corner of the module can take P2 with this tablet place
    p2_rect, cells = best
    removed = [c for c in cells0 if c not in cells]
    return dict(name=name, x_w=x_w, x_e=x_e, y_s=min(s[2] for s in south), y_n=y_n, n_slices=n_slices, south=south,
                block_len=block_len, cells=cells, dropped=dropped, removed=removed, tablet=tablet, tablet_rect=tablet_rect,
                p2_rect=p2_rect, qmx=qmx)


def zones(a):
    """The module's plan zones with their depth: each slice's one-layer zone, each layer-2 column's zone, P2, the tablet."""
    z = []
    for s, (x0, x1, ys, j) in enumerate(a["south"]):
        xa = a["x_w"] if s == 0 else x0
        xb = a["x_e"] if s == len(a["south"]) - 1 else x1
        z.append(("module, one layer", (xa, ys, xb, a["y_n"]), DEPTH1, OWN_SUM))
    for c in a["cells"]:
        if c["layer"] == 2:
            z.append(("module, two layers", l2_fp(c), DEPTH2, OWN_SUM))
    z.append(("P2 board", a["p2_rect"], P2_DEPTH, OWN_SUM))
    if a["tablet"]:
        z.append(("tablet " + a["tablet"]["name"], a["tablet_rect"], tablet_depth(a["tablet"]), OWN_SUM + TAB_OWN))
    return z


def check(a, out):
    """Every lid zone against every face part it stands over; the plan checks against the lid's ceiling, the QMX set and the tablet."""
    rows = []
    for zn, zr, depth, own in zones(a):
        for ref, fr, h, src in FACE:
            if not overlap(zr, fr, PLAN_ALLOW): continue
            if h is None:
                rows.append((zn, ref, None, None, None, None, "NOT MET (a part of TBD height under a lid item)")); continue
            n, w, x2 = margins(depth, h, own)
            rows.append((zn, ref, h, n, w, x2, verdict(w, x2)))
    plan = []
    plan.append(("module inside the flat ceiling, X", CEIL_FLAT[0] - max(abs(a["x_w"]), abs(a["x_e"])), 1.0))
    plan.append(("module inside the flat ceiling, Y", CEIL_FLAT[1] - max(abs(a["y_s"]), abs(a["y_n"])), 1.0))
    if a["qmx"]:
        plan.append(("module east edge to the QMX tray's west edge (both on the ceiling)", QMX["rect"][0] - a["x_e"], 1.0))
        if a["tablet_rect"]:
            plan.append(("tablet bracket east edge to the QMX tray (the tray reaches 29.30 deep, the tablet from %.2f)" % DEPTH1, QMX["rect"][0] - a["tablet_rect"][2], 1.0))
    if a["tablet_rect"]:
        tr = a["tablet_rect"]
        l2 = [l2_fp(c) for c in a["cells"] if c["layer"] == 2]
        gaps = []
        for f in l2:
            if f[0] < tr[2] and tr[0] < f[2]:
                gaps.append(tr[1] - f[3] if f[3] <= tr[1] else f[1] - tr[3])
        plan.append(("tablet bracket to the nearest two-layer zone, in Y", min(gaps) if gaps else 99.0, 0.0))
        cap = [f[1] for f in FACE if f[0] == "SW_SOS_GUARD"][0]; bz = [f[1] for f in FACE if f[0] == "BZ1"][0]
        if tr[0] < cap[2] + PLAN_ALLOW + 20.0:
            plan.append(("tablet bracket west edge to the guard caps (X -143.0) with the plan allowance", tr[0] - (cap[2] + PLAN_ALLOW), 0.0))
        if tr[0] < bz[2] + PLAN_ALLOW:
            plan.append(("tablet bracket south edge to the sounder ring (Y -79.1) with the plan allowance", tr[1] - (bz[3] + PLAN_ALLOW), 0.0))
    return rows, plan


def best_tablet(name, x_w, x_e, n_slices, t, qmx):
    """The tablet's bracket tried landscape and portrait, at every X (1.0 mm steps) and Y (0.5 mm) inside the free plan (west of the QMX tray
    when it is kept, east of the guard caps, inside the flat ceiling, 0.5 clear of the sounder ring or north of it); the place that
    keeps the most cells is taken (the tablet under the one-layer zone costs the two-layer places above its band). Every face row of
    the chosen place is then checked like any other zone."""
    y_n = CEIL_FLAT[1] - 1.0
    x_lim = (QMX["rect"][0] - 1.0) if qmx else (CEIL_FLAT[0] - 1.0)
    x_min = -143.0 + PLAN_ALLOW                      # east of the guard caps with the plan allowance
    best, tried = None, 0
    def steps(lo, hi, d):
        v, out = lo, []
        while v <= hi + 1e-9:
            out.append(v); v += d
        if out and hi - out[-1] > 1e-6: out.append(hi)          # the far bound itself is always tried
        return out
    for tw, th in ((t["w"] + 2 * LIP, t["h"] + 2 * LIP), (t["h"] + 2 * LIP, t["w"] + 2 * LIP)):
        for x0 in steps(x_min, x_lim - tw, 1.0):
            for y0 in steps(-y_n, y_n - th, 0.5):
                tr = (x0, y0, x0 + tw, y0 + th)
                if any(overlap(tr, f[1], PLAN_ALLOW) and (f[2] is None or margins(tablet_depth(t), f[2], OWN_SUM + TAB_OWN)[1] < MIN_CLEAR) for f in FACE):
                    continue
                a = build(name, x_w, x_e, y_n, n_slices, tablet=t, tablet_rect=tr, qmx=qmx)
                if a is None:
                    continue
                under = [sl[2] for sl in a["south"] if sl[0] < tr[2] and tr[0] < sl[1]]
                if tr[0] < x_w - 10.0 or tr[2] > x_e + 10.0 or tr[1] < max(under) - 10.0:
                    continue                                  # the bracket overhangs the module's cover by more than 10 (INFERRED limit)
                tried += 1
                if best is None or len(a["cells"]) > len(best["cells"]):
                    best = a
    if best:
        best["tablet_places_tried"] = tried
    return best


def arrangements():
    y_n = CEIL_FLAT[1] - 1.0                         # north (hinge) edge 1.0 inside the flat ceiling
    x_w = -141.0                                     # west edge 2.0 east of the guard caps (checked in the face rows)
    x_e3 = x_w + 3 * CELL_L + 4 * END_GAP + 2 * BAY  # three slices: 72.75, 10.45 short of the QMX tray
    x_e4 = CEIL_FLAT[0] - 1.0
    out = [build("B: HF kept, no tablet in the lid", x_w, x_e3, y_n, 3),
           best_tablet("A: HF kept, 8 inch tablet kept", x_w, x_e3, 3, TABLET_8, True),
           best_tablet("C: 8 inch tablet kept, HF out of the lid", x_w, x_e4, 4, TABLET_8, False),
           best_tablet("C10: 10 inch tablet kept, HF out of the lid", x_w, x_e4, 4, TABLET_10, False),
           build("D: HF and tablet both out of the lid", x_w, x_e4, y_n, 4, qmx=False)]
    return [a for a in out if a]


# ---------------------------------------------------------------- the hinge harness
HINGE = dict(y=155.0, z=111.0, dy=8.0, dz=5.0)   # ESTIMATE: inside the fairings (bases |X| 58.93..181.58, outer faces at about Y 164), near the parting plane Z 108.97
T_LID = (128.0, 111.5)     # the lid-side tie: a bonded tie mount on the lid's inner back wall, 2.5 above the parting plane (cavity wall at Y 130.9)
T_PLATE = (122.0, 106.52)  # the plate-side tie: on the face plate's full-thickness face near its back edge (126.5), clear of the 6-32 heads at X 0, +-139.45 (the 5.0 rebated band beyond it cannot take a 4.4 lead under the lid wall at 130.9)
HARNESS = dict(current_cont=10.0, current_peak=18.0, peak_s=60.0, charge=8.6, awg=12, ohm_per_m=5.21e-3, od=4.4, run_lid=0.45, run_base=0.35,
               span_x=150.0)
# ASSUMPTION (for the electrical stream): the lid pack carries the kit's whole 10 A continuous and 18 A for 60 s with the base pack
# isolated (PWR-F12, ENERGY-RECONCILIATION 8a), and up to 8.6 A of charge (section 9g: 123.5 W at 14.4 V); 12 AWG as the pack lead
# (ASSEMBLY.md section 3); OD 4.4 for a fine-strand silicone 12 AWG (INFERRED class, no wire sheet held).


def rot(p, phi_deg):
    """A lid point (Y, Z) with the lid closed, turned open by phi about the hinge axis."""
    dy, dz = p[0] - HINGE["y"], p[1] - HINGE["z"]
    f = math.radians(phi_deg)
    return (HINGE["y"] + dy * math.cos(f) + dz * math.sin(f), HINGE["z"] - dy * math.sin(f) + dz * math.cos(f))


# ---------------------------------------------------------------- mass and stability
FOOT_Z = -8.38        # the feet line (DXF end view, CASE-MARGINS.md 2.3 row "Outer features")
Y_TIP = 114.49        # the back tipping line: the outer flat bottom's edge (the fillet tangent, #1321; the outer radius is concentric, INFERRED)
CASE_M = 2.5          # Peli 1450 without foam (product page, Wayback 29 Mar 2026)
LID_SHARE = 0.397     # the lid's share of the shell by inside area (382 x 268 open boxes 109 and 45 deep), ESTIMATE


def mass_items(a, base_m, base_cg):
    n = len(a["cells"])
    mx = a["x_e"] - a["x_w"]; my = a["y_n"] - a["y_s"]
    plate = mx * my * PLATE * 2.68e-6
    cover = (mx * my + 2 * (mx + my) * 40.0) * 1.0 * 1.25e-6
    nick = n * 0.0012 + 0.030
    wrap = n * 0.0015 + 0.030
    ncells = [c for c in a["cells"]]
    zc = CEIL_Z_NOM - (sum((BOND + PLATE + WRAP + CELL_D / 2 + (NEST_DZ if c["layer"] == 2 else 0.0)) for c in ncells) / max(n, 1))
    xc = sum((c["x0"] + c["x1"]) / 2 for c in ncells) / max(n, 1)
    yc = sum(c["yc"] for c in ncells) / max(n, 1)
    mid = ((a["x_w"] + a["x_e"]) / 2, (a["y_s"] + a["y_n"]) / 2)
    items = [("lid pack cells, %d x 50 g max (spec 3.10)" % n, "lid", n * CELL_M, (xc, yc, zc)),
             ("lid plate 5052-H32 2.0 (2.68 g/cm3)", "lid", plate, (mid[0], mid[1], CEIL_Z_NOM - 1.2)),
             ("cover, printed V-0 class 1.0 (1.25 g/cm3, ESTIMATE)", "lid", cover, (mid[0], mid[1], CEIL_Z_NOM - 25.0)),
             ("nickel strip and group links (ESTIMATE)", "lid", nick, (xc, yc, zc)),
             ("wrap, fish paper, cell glue, pad, standoffs, bond (ESTIMATE)", "lid", wrap, (xc, yc, zc)),
             ("P2 protection board (ASSUMPTION, board P class)", "lid", P2["mass"] if a["p2_rect"] else 0.0,
              ((a["p2_rect"][0] + a["p2_rect"][2]) / 2 if a["p2_rect"] else 0, (a["p2_rect"][1] + a["p2_rect"][3]) / 2 if a["p2_rect"] else 0, CEIL_Z_NOM - 12.0)),
             ("lid harness to the hinge: 2 x 12 AWG 0.45 m, sense leads, connector (ESTIMATE)", "lid", 0.080, (mid[0], 110.0, CEIL_Z_NOM - 20.0))]
    if a["qmx"]:
        items.append(("QMX set r2: unit and plugs 0.240, tray, frame, plate (r2 record D)", "lid", QMX["mass"], (127.1, 10.0, CEIL_Z_NOM - 15.0)))
    if a["tablet"]:
        tr = a["tablet_rect"]
        items.append(("tablet, %s (INFERRED) and bracket 0.10 (ESTIMATE)" % a["tablet"]["name"], "lid", a["tablet"]["mass"] + 0.10,
                      ((tr[0] + tr[2]) / 2, (tr[1] + tr[3]) / 2, CEIL_Z_NOM - DEPTH1 - 6.0)))
    items.append(("lid shell, %.1f percent of %.1f kg (ESTIMATE)" % (100 * LID_SHARE, CASE_M), "lid", CASE_M * LID_SHARE, (0.0, 0.0, 146.0)))
    items.append(("base shell and latches (ESTIMATE)", "base", CASE_M * (1 - LID_SHARE), (0.0, 0.0, 40.0)))
    items.append(("base contents incl. the 4S6P pack (ESTIMATE, swept)", "base", base_m, base_cg))
    return items


def cg(items, part=None, phi=0.0):
    m = sx = sy = sz = 0.0
    for _n, where, mi, (x, y, z) in items:
        if part and where != part: continue
        if where == "lid" and phi:
            y, z = rot((y, z), phi)
        m += mi; sx += mi * x; sy += mi * y; sz += mi * z
    return m, sx / m, sy / m, sz / m


def critical_slope(items, phi, tip_y=Y_TIP):
    m, x, y, z = cg(items, phi=phi)
    arm = tip_y - y
    return math.degrees(math.atan2(arm, z - FOOT_Z)), y, z


# ---------------------------------------------------------------- the base pockets (section 8's 4S6P) against the same figures
BLOCK = (56.65, 133.5, 38.1)     # A06's 4S3P block (panel1450.PACK_BLOCK)


def base_rows():
    """The east rows as frame_seat.out prints them and their mirror at the west, which holds only because Peli's cavity is symmetric
    in X (the end-wall ribs at Y 0, +-76.2 on both walls, the R 15.88 fillet on all four floor edges: VERIFIED, CASE-MARGINS 2.3)."""
    east = [("M4a", "block corner to Peli's R 15.88 fillet (web interior 372.4 at the corner)", 1.0, 3.71, 1.85, 0.85, "OPEN: placed by hand; T4"),
            ("M4b", "block end face to the end wall", 1.0, 9.68, 7.38, 6.38, "MET"),
            ("M4c", "block end face to the RF entry plate's bottom screw heads inside", 1.0, 5.86, 3.18, 1.80, "MET"),
            ("M5", "pack group in Y between the east legs (block + 2.0 + board P = 205.5); west: the block alone, 133.5", 1.0, 3.65, 1.77, 0.27, "OPEN: placed by hand, the legs' locator; T4"),
            ("M6", "block top under B16's underside (A06 at the pessimistic base, +1.1 VHB)", 1.0, 4.42, 3.66, 2.90, "MET")]
    rows = []
    for r in east:
        rows.append(("east " + r[0],) + r[1:])
        if r[0] == "M5":
            rows.append(("west M5w", "west block alone in Y between the west legs (inner faces |Y| 106.4), per side", 1.0, 39.65, 37.77, 36.89,
                         "MET (the block's Y place is not ruled; centred here)"))
            continue
        if r[0] == "M6":
            rows.append(("west M6w", "block top under B16's underside parts (C33, A06's tool: packfit_west.out)", 1.0, 5.20, 3.99, None,
                         "OPEN: the x2 reading is not computed by A06's tool; T4"))
        else:
            rows.append(("west " + r[0] + "w",) + r[1:-1] + (r[-1] + " (mirror: Peli's cavity and the RF entry plates are the same at both ends)",))
    return rows


def west_jumpers():
    """Section 8b's conflict made numeric: which west arrestor sites lie over the west block, and whether a drop past it exists."""
    sites = [y for _n, y in P.WALL_WEST]
    half = BLOCK[1] / 2
    over = [y for y in sites if abs(y) - 2.49 / 2 < half + 1.0]
    gap_to_a = 2.0          # the block's east face 2.0 from board A's west edge (panel1450 PACK_WEST_X mirrored)
    return sites, over, gap_to_a


def L_BAYS_AREA(a):
    """The two end bays' plan area (they carry the plate too)."""
    ys = min(s[2] for s in a["south"])
    return BAY * (a["y_n"] - ys)


def harness_numbers():
    """The harness figures section 3 prints (for the drawing set)."""
    H = HARNESS
    offs = [math.hypot(rot(T_LID, p)[0] - T_PLATE[0], rot(T_LID, p)[1] - T_PLATE[1]) for p in (0, 30, 60, 90, 100, 110, 120, 135, 150, 180)]
    c0, c1 = math.hypot(min(offs), H["span_x"]), math.hypot(max(offs), H["span_x"])
    lead = 1.05 * c1
    sag = math.sqrt(3.0 * c0 * (lead - c0) / 8.0)
    return dict(rad=math.hypot(T_LID[0] - HINGE["y"], T_LID[1] - HINGE["z"]), c0=c0, c1=c1, lead=lead, sag=sag,
                r_bow=c0 ** 2 / (8 * sag) + sag / 2, off=max(offs), r_s=H["span_x"] ** 2 / (4 * max(offs)))


def main(fp):
    w = lambda s="": fp.write(s + "\n")
    w("Option A(i) lid pack, hinge harness, mass and stability, base pockets: v2/cad/lid_pack_a1.py (MESHSAT-1357, stream a1mech, 29 Sep 2026)")
    w("Prototype design, AI review: nothing built, bought or fitted. Analytical success is not physical verification or fabrication readiness.")
    w()
    w("1. THE LID, at Peli's figures")
    w("   face top Z %.2f nominal (104.77 to 108.27), ceiling Z %.2f nominal (152.66 at the worst: rim 108.97 - 0.76 + web lid 44.45)" % (FACE_Z_NOM, CEIL_Z_NOM))
    w("   room face top to ceiling: %.2f nominal, %.2f worst, %.2f with every unstated allowance taken twice (frame_seat.out M3; r2 record B)" % (ROOM_NOM, ROOM_WORST, ROOM_X2))
    w("   flat ceiling %.2f x %.2f (STEP #736); fillets R %.2f to the walls, then an R %.2f step; lid cavity %.2f x %.2f at the parting plane" % (
        2 * CEIL_FLAT[0], 2 * CEIL_FLAT[1], CEIL_FILLET_R, LID_STEP, 2 * LID_WALL_AT_PART[0], 2 * LID_WALL_AT_PART[1]))
    w("   ribs in the lid cavity: %d (the top STEP's cavity faces are the drafted walls, the fillets, the R 1.27 step and the ceiling)" % LID_RIBS)
    w("   gasket land: the lid's seal seats on the base's tongue outboard of the cavity (X 195.56..201.96, CASE-MARGINS 2.3); every lid item here")
    w("   stays inboard of the cavity walls, so none bears on the seal; the fillet's depth below the ceiling at 2, 5, 8, 12 mm outboard of the")
    w("   flat edge: " + ", ".join("%.2f" % fillet_depth(d) for d in (2, 5, 8, 12)))
    w("   plan allowance between a lid item and a face part: %.2f (lid place 0.76 + bonded plate 0.30, INFERRED); minimum clearance %.1f" % (PLAN_ALLOW, MIN_CLEAR))
    w()
    w("   FACE PARTS standing into the lid (height above the face top, from the maker's sheet where held)")
    seen = set()
    for ref, r, h, src in FACE:
        key = ref.rstrip("0123456789").rstrip("_") if ref.startswith(("D", "PLATE_SCREW", "XFRAME")) else ref
        if key in seen and ref.startswith(("D", "PLATE_SCREW", "XFRAME")): continue
        seen.add(key)
        w("   %-16s X %7.1f..%7.1f Y %7.1f..%7.1f  h %6s  %s" % (ref if key == ref else key + "*", r[0], r[2], r[1], r[3], "TBD" if h is None else "%.2f" % h, src))
    w("   (* one row for the set: D1..D16 status and bar LEDs, the four XFRAME screws, the ten plate screws)")
    w()
    w("2. THE LID MODULE")
    w("   cell: Samsung INR18650-35E, d %.2f max, L %.2f max, %.0f g max (spec Ver. 1.1, 3.10 and the drawing); %.2f Ah min, %.2f V" % (CELL_D, CELL_L, CELL_M * 1000, CELL_AH, CELL_V))
    w("   block: A06's construction (the ruled base block's): cells touching at %.2f, wrap %.1f a side, %.1f at each end joint along the axis;" % (CELL_D, WRAP, END_GAP))
    w("   cells lie with their axis along X, three or four end to end (series joints at the end gaps), one layer across Y, and a second layer")
    w("   nested in the grooves of the first, %.3f further from the ceiling (toward the face), wherever the face under it allows" % NEST_DZ)
    w("   stack from the ceiling: bond %.2f + 5052-H32 plate %.2f + block (%.2f one layer, %.2f two) + PORON pad %.2f + cover %.2f" % (
        BOND, PLATE, CELL_D + 2 * WRAP, CELL_D + NEST_DZ + 2 * WRAP, PAD, COVER))
    w("   module depth: one layer %.2f, two layers %.2f; own allowances %s = %.2f (INFERRED, none stated by a source)" % (DEPTH1, DEPTH2, OWN, OWN_SUM))
    w("   P2 (ASSUMPTION until fnd/a1elec reports): board P's outline %.0f x %.0f, tallest part %.2f (Keystone 3568 with its blade, packfit_west.out)," % (P2["w"], P2["h"], P2["parts"]))
    w("   on %.1f standoffs: depth %.2f, inside the one-layer depth" % (P2["standoff"], P2_DEPTH))
    w("   venting: the maker's sheet names venting as a failure outcome (8.1.2) and states no clearance; every cell end faces its 1.0 joint, the")
    w("   cover's X-end bays are open slots, so gas from a cell is not sealed in the module: it enters the closed case, which Peli's pressure valve")
    w("   relieves (ruling 7 Sep 2026 00:52). Heat: the sheet asks the pack away from heat sources (page 17); the lid is away from the PA and CM5s.")
    w()
    arr = arrangements()
    best = {}
    for a in arr:
        rows, plan = check(a, fp)
        n = len(a["cells"]); n1 = sum(1 for c in a["cells"] if c["layer"] == 1); n2 = n - n1
        par = n // 4
        fails = [r for r in rows if r[6].startswith("NOT MET")]
        pfails = [p for p in plan if p[1] < p[2]]
        opens = [r for r in rows if r[6] == "OPEN"]
        best[a["name"].split(":")[0]] = (n, par, a)
        w("   ARRANGEMENT %s" % a["name"])
        w("     module X %.2f..%.2f, north edge Y %.2f; %d slices of %.2f along X (block %.2f + two %.1f bays); per slice (X, south edge, cells across):" % (
            a["x_w"], a["x_e"], a["y_n"], a["n_slices"], CELL_L, a["block_len"], BAY))
        w("       " + "; ".join("X %.2f..%.2f from Y %.2f, %d" % sl for sl in a["south"]))
        w("     P2 at X %.2f..%.2f, Y %.2f..%.2f (the corner that costs the fewest cells)" % (a["p2_rect"][0], a["p2_rect"][2], a["p2_rect"][1], a["p2_rect"][3]))
        if a["tablet"]:
            w("     tablet places tried (landscape and portrait, 1.0 mm in X and 0.5 mm in Y and both bounds, every face row met at the worst): %d; the best kept" % a.get("tablet_places_tried", 0))
            t = a["tablet"]; tr = a["tablet_rect"]
            w("     tablet %s %.0f x %.0f x %.1f in a bracket %.0f x %.0f (lips %.1f), X %.2f..%.2f, Y %.2f..%.2f, depth %.2f from the ceiling" % (
                t["name"], t["w"], t["h"], t["t"], tr[2] - tr[0], tr[3] - tr[1], LIP, tr[0], tr[2], tr[1], tr[3], tablet_depth(t)))
        w("     cells: %d (layer 1 %d, layer 2 %d); layer-2 places refused by the face: %d (%s); cells under P2 removed: %d" % (
            n, n1, n2, len(a["dropped"]), ", ".join(sorted(set(d[1] for d in a["dropped"]))) or "none", len(a["removed"])))
        w("     => 4S%dP (%d cells used, %.1f Wh nominal at %.2f Ah min); with the base 4S6P: 4S%dP" % (par, 4 * par, 4 * par * CELL_AH * CELL_V, CELL_AH, par + 6))
        w("     face rows (lid zone over face part): %d rows, %d NOT MET, %d OPEN; plan rows %d, %d below their minimum" % (len(rows), len(fails), len(opens), len(plan), len(pfails)))
        agg = {}
        for zn, ref, h, nn, ww, xx, v in rows:
            k = (zn.split(" s")[0], ref.rstrip("0123456789").rstrip("_") if ref.startswith(("D", "XFRAME", "PLATE_SCREW")) else ref)
            if k not in agg or (ww is not None and agg[k][3] is not None and ww < agg[k][3]) or ww is None:
                agg[k] = (h, nn, ww, xx, v)
        for (zn, ref), (h, nn, ww, xx, v) in sorted(agg.items(), key=lambda kv: (kv[1][2] if kv[1][2] is not None else -99)):
            if h is None:
                w("       %-28s over %-14s h TBD                                   %s" % (zn, ref, v))
            else:
                w("       %-28s over %-14s h %5.2f  nominal %6.2f  worst %6.2f  x2 %6.2f  %s" % (zn, ref, h, nn, ww, xx, v))
        for pn, pv, pm in plan:
            w("       plan: %-100s %7.2f (min %.1f) %s" % (pn, pv, pm, "ok" if pv >= pm else "BELOW"))
        w()
    nB, pB, aB = best["B"]; nA, pA, aA = best["A"]; nC, pC, aC = best["C"]; nD, pD, aD = best["D"]
    n10, p10, a10 = best.get("C10", (0, 0, None))
    w("   RESULT: 48 cells (4S12P) with HF and the tablet bracket both preserved: %s. Arrangement A holds %d cells (4S%dP) at its best tablet" % (
        "FITS" if pA >= 12 else "DOES NOT FIT", nA, pA))
    w("   place (%d short of 48; %d short in whole groups of four). B (HF kept, no tablet in the lid) holds %d (4S%dP); C (8 inch tablet kept, HF out of the" % (48 - nA, 48 - 4 * pA, nB, pB))
    w("   lid) %d (4S%dP); C10 (10 inch tablet kept, HF out) %d (4S%dP); D (both out) %d (4S%dP)." % (nC, pC, n10, p10, nD, pD))
    t10 = TABLET_10
    w("   With HF in the lid, the 10 inch class (%.0f x %.0f + lips) needs %.0f in X between the guard caps (%.2f) and the QMX tray (%.2f less 1.0), %.2f available:" % (
        t10["w"], t10["h"], t10["w"] + 2 * LIP, -143.0 + PLAN_ALLOW, QMX["rect"][0], QMX["rect"][0] - 1.0 - (-143.0 + PLAN_ALLOW)))
    w("   it does not fit beside the QMX set in any arrangement, pack or no pack; the 8 inch class is the one that fits with HF.")
    w()
    # ---------------------------------------------------------------- retention
    items = mass_items(aB, 9.0, (0.0, 0.0, 55.0))
    mod_m = sum(i[2] for i in items if i[0].startswith(("lid pack cells", "lid plate", "cover", "nickel", "wrap", "P2")))
    area = sum((x1 - x0) * (aB["y_n"] - ys) for (x0, x1, ys, j) in aB["south"]) + 2 * L_BAYS_AREA(aB)
    F = mod_m * 100.0 * 9.81
    w("   RETENTION of the module (arrangement B, every place filled: %d cells), to the r2 set's load case: 100 g in each direction" % len(aB["cells"]))
    w("     module %.2f kg (cells at 50 g max, the rest ESTIMATE): %.0f N at 100 g. Bond area under the lid plate about %.0f mm2 (the slices and bays):" % (mod_m, F, area))
    w("     mean stress %.3f MPa in tension (a drop on the base pulls the module off the ceiling) or shear (on an end). DP8005's sheet gives no" % (F / area))
    w("     strength on polypropylene (its 0.3 MPa is the overlap shear at which a part may be handled, a cure milestone, not a rating) and no")
    w("     peel figure but T-peel on 0.5 mm HDPE: the bond is bounded by no held figure, OPEN at T8 (a pull test of a bonded plate on Peli's")
    w("     polypropylene after a thermal cycle) and E1 with an accelerometer on the lid, as the r2 set's bond is.")
    w("     the block to the plate: cell glue between cells and a fillet to the plate (adhesive TBD): %.0f N per cell at 100 g (%.1f N/mm on a" % (
        CELL_M * 100 * 9.81, CELL_M * 100 * 9.81 / CELL_L))
    w("     cell's %.2f mm contact line); the cover on eight M3 standoffs in the end bays catches the block if the glue lets go: %.0f N each" % (
        CELL_L, len(aB["cells"]) * CELL_M * 100 * 9.81 / 8))
    w("     at 100 g, against the r2 record's 1019 N for a button head on a 3.0 printed part (a 1.0 cover takes less; the cover's spans of")
    w("     65 to 200 between bays are not a beam that carries the block: the glue is the primary hold, the cover a catch). OPEN at E1.")
    w("     Peli states no load for its hinges or the lid's stop; the lid grows from about 1.0 to %.1f kg: T-A1-4 (and the lid stay, section 4)." % (
        sum(i[2] for i in items if i[1] == "lid")))
    w("     heater: the lid pack's own mat (9h: the charge window starts at 0 C) is not placed; a 1.0 mat between the plate and the block")
    w("     deepens both depths by 1.0: the tightest rows (the window 3.10, the LED bar 2.40 at the worst) still meet 1.0.")
    w()
    # ---------------------------------------------------------------- harness
    w("3. THE HINGE HARNESS (the lid pack to the base), for arrangement B")
    H = HARNESS
    w("   current (ASSUMPTION for fnd/a1elec): %.0f A continuous, %.0f A for %.0f s with the base pack isolated, %.1f A of charge" % (H["current_cont"], H["current_peak"], H["peak_s"], H["charge"]))
    rl = (H["run_lid"] + H["run_base"]) * 2 * H["ohm_per_m"]
    w("   conductor: %d AWG fine-strand silicone, %.2f mOhm/m (annealed copper), OD %.1f (INFERRED class); run %.2f m in the lid + %.2f m in the base;" % (
        H["awg"], H["ohm_per_m"] * 1e3, H["od"], H["run_lid"], H["run_base"]))
    w("   loop %.2f mOhm: at %.0f A %.0f mV and %.2f W; at %.0f A %.0f mV and %.2f W; adiabatic rise over %.0f s at %.0f A: %.1f K (copper 3.31 mm2, 385 J/kgK)" % (
        rl * 1e3, H["current_cont"], rl * H["current_cont"] * 1e3, rl * H["current_cont"] ** 2, H["current_peak"], rl * H["current_peak"] * 1e3,
        rl * H["current_peak"] ** 2, H["peak_s"], H["current_peak"], (H["current_peak"] ** 2 * H["ohm_per_m"] * H["peak_s"]) / (3.31e-6 * 8960 * 385)))
    w("   hinge axis (ESTIMATE, no Peli figure): Y %.1f +-%.1f, Z %.1f +-%.1f; lid tie T_L %s on the lid's inner back wall; plate tie T_P %s" % (
        HINGE["y"], HINGE["dy"], HINGE["z"], HINGE["dz"], T_LID, T_PLATE))
    w("   T_L and T_P are %.0f apart in X, so the lead between them runs along the back channel and the lid's travel moves one end sideways" % H["span_x"])
    w("   opening   T_L (Y, Z)            Y-Z offset T_L..T_P   chord T_L..T_P")
    rad = math.hypot(T_LID[0] - HINGE["y"], T_LID[1] - HINGE["z"])
    offs = []
    for phi in (0, 30, 60, 90, 100, 110, 120, 135, 150, 180):
        p = rot(T_LID, phi); o = math.hypot(p[0] - T_PLATE[0], p[1] - T_PLATE[1]); offs.append(o)
        w("   %5.0f deg  (%7.2f, %7.2f)   %7.2f               %7.2f" % (phi, p[0], p[1], o, math.hypot(o, H["span_x"])))
    c0, c1 = math.hypot(min(offs), H["span_x"]), math.hypot(max(offs), H["span_x"])
    lead = 1.05 * c1
    sag = math.sqrt(3.0 * c0 * (lead - c0) / 8.0)
    r_bow = c0 ** 2 / (8 * sag) + sag / 2
    r_s = H["span_x"] ** 2 / (4 * max(offs))
    w("   T_L turns at R %.1f about the axis. Lead between the ties: %.1f (the longest chord, %.1f at 180 degrees, plus 5 percent)." % (rad, lead, c1))
    w("   Closed, the lead bows %.1f (in the X-Z plane of the back channel, which is about 14 wide in Y and 40 tall), radius about %.0f; fully" % (sag, r_bow))
    w("   open it is an S across an offset of %.1f over %.0f, radius about %.0f. Requirement on the pick (INFERRED class): a flexing radius of" % (max(offs), H["span_x"], r_s))
    w("   10 x OD = %.0f or less, met by both figures above: %s." % (10 * H["od"], "yes" if min(r_bow, r_s) >= 10 * H["od"] else "NO"))
    p2 = aB["p2_rect"]
    w("   route (B): from P2 (X %.0f..%.0f, Y %.0f..%.0f) through the module's west bay (X %.0f..%.0f) north to the back channel (Y %.2f to the lid's" % (
        p2[0], p2[2], p2[1], p2[3], aB["x_w"], aB["x_w"] + BAY, aB["y_n"]))
    w("   back wall, about %.1f at the parting plane), east along it on bonded tie mounts to T_L at X %.0f, then the free lead to T_P at X %.0f on" % (
        LID_WALL_AT_PART[1], aB["x_w"] + 20.0, aB["x_w"] + 20.0 + H["span_x"]))
    w("   the plate's full-thickness face near its back edge (Y 122), then to the crossing. About %.2f m in the lid, as assumed above." % H["run_lid"])
    w("   strain relief: a bonded tie mount at T_L and at T_P and every 60 mm or less along both runs (the r2 set's tie-mount rule), and a")
    w("   printed guide on the lid's back wall that keeps the free lead inboard of the cavity wall (Y < %.1f) so that closing folds it toward" % LID_WALL_AT_PART[1])
    w("   the face and never over the rim or the seal.")
    w("   disconnect: at the lid side beside P2, an XT60 pair (Amass XT60, the tree's pack connector, v2/vendor/battery/amass-xt60-spec-tme.pdf)")
    w("   and a JST XH 1x4 for SMBus, so that the lid comes off its hinge as ASSEMBLY.md section 7 has it; fused at P2 (the string fuse of 8a's class).")
    w("   crossing the sealed face: NOT designed; it is S-95's crossing (EQ-31), which the QMX leads already need. This harness adds to it: two")
    w("   power poles of 25 A or more and four signal contacts, sealed mated and unmated, on the plate's back band or at a site outside every")
    w("   lid item's plan; on the plate it must clear the frame's ring, the backer's top strip and B16's tall parts. Until it is designed, the")
    w("   lid pack cannot be connected with the lid closed and sealed.")
    w("   the QMX's DC lead (r2: looped back at R 20 WEST of the tray) is re-routed EAST because the pack now lies west of the tray: %s" % (
        " -> ".join("(%.1f, %.1f)" % p for p in DC_ROUTE)))
    w()
    # ---------------------------------------------------------------- mass and stability
    w("4. MASS AND STABILITY (arrangement B, which holds 48 cells or more with HF; A for comparison)")
    for a in (aB, aA):
        items = mass_items(a, 9.0, (0.0, 0.0, 55.0))
        lid_m = sum(i[2] for i in items if i[1] == "lid")
        w("   %s: lid %.2f kg in all" % (a["name"], lid_m))
        for nm, wh, mi, (x, y, z) in items:
            if wh == "lid":
                w("     %-86s %6.3f kg at (%7.1f, %7.1f, %6.1f)" % (nm, mi, x, y, z))
        added = sum(i[2] for i in items if i[1] == "lid" and not i[0].startswith(("QMX", "lid shell")))
        w("     added to the lid by the pack (cells, plate, cover, strip, wrap, P2, harness%s): %.2f kg" % (", tablet" if a["tablet"] else "", added))
    w("   base: shell %.2f kg; contents swept 7 to 14 kg (ARCHITECTURE.md 11: sourced floor about 7.0 with 12 cells; +0.75 for section 8's 4S6P;" % (CASE_M * (1 - LID_SHARE)))
    w("   the CM5s, coolers, cards, drives, fans, PA, frame, legs, harness have no sourced mass) at Z 45 to 65, Y -20 to +20 (ESTIMATE)")
    w("   tipping line: Y %.2f (the outer flat bottom's edge, INFERRED), feet at Z %.2f; hinge axis Y %.1f, Z %.1f (ESTIMATE); the lid's stop angle" % (Y_TIP, FOOT_Z, HINGE["y"], HINGE["z"]))
    w("   is stated by no held Peli file (TBD): swept 90 to 180 degrees; each row is the worst over base 7 to 14 kg, CG Y -20..+20, Z 45..65")
    w("   and the hinge axis Y 147..163")
    w("   arrangement  lid open   worst CG Y   level ground   worst critical back slope (tips beyond)")
    lim = {}
    for a in (aB, aA):
        for phi in (0, 90, 100, 110, 120, 135, 150, 180):
            worst = (99.0, None)
            for hy in (HINGE["y"] - HINGE["dy"], HINGE["y"], HINGE["y"] + HINGE["dy"]):
                h0 = HINGE["y"]; HINGE["y"] = hy
                for bm in (7.0, 9.0, 14.0):
                    for by in (-20.0, 0.0, 20.0):
                        for bz in (45.0, 65.0):
                            sl, y, z = critical_slope(mass_items(a, bm, (0.0, by, bz)), phi)
                            if sl < worst[0]: worst = (sl, y)
                HINGE["y"] = h0
            lim[(a["name"][0], phi)] = worst[0]
            w("   %-12s %5.0f deg   %8.2f     %-12s   %5.1f deg" % (a["name"].split(":")[0], phi, worst[1], "stands" if worst[1] < Y_TIP else "TIPS", worst[0]))
    for ty in (100.0,):
        wst = min(critical_slope(mass_items(aB, bm, (0.0, by, bz)), 100, tip_y=ty)[0] for bm in (7.0, 9.0, 14.0) for by in (-20.0, 0.0, 20.0) for bz in (45.0, 65.0))
        lvl = [p for p in (90, 100, 110, 120, 135) if min(critical_slope(mass_items(aB, bm, (0.0, by, bz)), p, tip_y=ty)[0] for bm in (7.0, 9.0, 14.0) for by in (-20.0, 0.0, 20.0) for bz in (45.0, 65.0)) <= 0]
        w("   sensitivity: the feet's place is not in Peli's files; with the tipping line at Y %.0f (feet inboard, INFERRED bound) B at 100 degrees" % ty)
        w("   stands on a back slope of %.1f deg at the worst, and tips on level ground from %s degrees (hinge axis Y 155)" % (wst, lvl[0] if lvl else "beyond 135"))
    tip_phi = min([p for p in (90, 100, 110, 120, 135, 150, 180) if lim[("B", p)] <= 0] or [999])
    w("   verdict (B): the open case stands on level ground up to a lid opening of %s degrees in every swept case; beyond it a light base with" % (
        "%d" % max(p for p in (90, 100, 110, 120, 135, 150) if lim[("B", p)] > 0)))
    w("   its CG back and high tips on level ground (first at %s degrees swept). Fix, the session's (authority SESSION, reversible): a lid stay" % tip_phi)
    w("   that stops the lid at 100 degrees (a webbing strap between two bonded anchors, one on the lid's inner back wall, one on the face")
    w("   plate's rebated back band; no hole in the case or the plate; about EUR 10, ESTIMATE; it folds into the back channel when the lid")
    w("   closes), which also carries the lid's added mass off Peli's hinge stop. With it the")
    w("   worst back slope the open case stands on is %.1f deg (B) and %.1f deg (A); the operator's sheet states: open the lid only on ground" % (lim[("B", 100)], lim[("A", 100)]))
    w("   sloping less than %d degrees toward the hinge side. If Peli's own stop is at or under 100 degrees the stay is not needed for" % math.floor(lim[("B", 100)]))
    w("   stability; the stop angle and the hinge axis are read on the mock-up (T-A1-3).")
    w()
    w("5. THE BASE POCKETS: section 8's 4S6P (east block as ruled, west block mirrored) at the same worst figures")
    w("   row      margin                                                                 min  nominal  worst  x2     verdict")
    for r in base_rows():
        w("   %-8s %-72s %4.1f %7.2f %6.2f %6s  %s" % (r[0], r[1], r[2], r[3], r[4], "n/a" if r[5] is None else "%.2f" % r[5], r[6]))
    sites, over, gap = west_jumpers()
    w("   west RF jumpers (CASE-MARGINS 3.4 West, M17w): sites at Y %s; with the west block centred (Y +-%.2f), %d of 7 cables fall onto it (%s)." % (
        sites, BLOCK[1] / 2, len(over), over))
    w("   The slot over the block to B16's underside is 7.19 at the worst less C33's zone (packfit_west.out 3.99), and the only drop east of the")
    w("   block is its %.1f gap to board A, under one RG-316 (2.49): FAILS AS ASSUMED, held OPEN as section 8b has it (the M17 class; the west RF" % gap)
    w("   entry must be re-planned before the west block is taken). Hold-down: S-27 open for both blocks; the heater mat and board P's additions: 8a, 8d.")
    return best


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w") as f: main(f)
    else:
        main(sys.stdout)
