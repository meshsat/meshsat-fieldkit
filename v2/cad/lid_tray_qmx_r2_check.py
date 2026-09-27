#!/usr/bin/env python3
"""The QMX lid tray r2, checked (MESHSAT-1357, S-63, EQ-24; stream w5tray, second pass of 27 to 28 Sep 2026). Reads
v2/cad/lid_tray_qmx_r2.py (its numbers and its one table of solids), v2/ecad/tools/panel1450.py (the face plate's parts) and
v2/vendor/peli/1450/frame_seat.out (the room between the face and the lid ceiling that M3 and M19 were computed with) and prints, as a
record for the r2 set and its sheets:

  A. every jack's plug: the largest plug body the set admits about each jack's axis at the worst of its scaled place, and the leads'
     room to the lid's flat ceiling edge for their bend radius;
  B. the face room, row by row FROM THE SOLID ABOVE EACH PART: for every part of the face plate whose footprint in plan lies under any
     solid of the set (the tray, the frame, its screw heads, the unit and what stands proud of it, the permanent plugs), the deepest
     solid over that footprint, its depth from the lid ceiling, the part's height above the face from its maker's sheet, and the margin
     with the set's own allowances in it; and the same for the flat face under the deepest solid of all, the knob tips;
  C. the pads: PORON 4701-30 compression over the tolerance corners;
  D. retention: the load case the set is designed to, each link of each load path with its capacity and its factor on that load, the
     pads' preload against TEST-PLAN E2's vibration, the sustained stress the preload puts on the frame, and TEST-PLAN E1's drop as a
     peak-acceleration bound over the stopping distance, which no held document states;
  E. the fitting: the unit with everything that stands proud of it, at its largest, swept along its way into the tray, and the frame
     swept along its way over the unit, each against every solid it passes, with the least clearance to each; and two CONTROLS that
     must fail: the first pass's tray with its documented way in (the checker's blocking item B1), and the first pass's face-room rows
     against the solids of its own tray (B2).

Sections A to E are stdlib only and run anywhere. With --solids (needs build123d, v2/cad/requirements-cad.lock) the check also builds
the tray and the frame and proves ON THE SOLIDS that the table sections B and E were computed from is what was built, that the unit, the
admitted plugs and the knobs' finger room touch nothing when everything is in place, and that the unit and the frame meet nothing at any
of the positions of their way in. The exit status is 1 if a clearance of E is under its minimum, a row of B is NOT MET, a control does
not fail, or a solid check fails. Usage: lid_tray_qmx_r2_check.py [--solids] [out file]"""
import os, sys, math, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ecad", "tools"))
import lid_tray_qmx_r2 as Q
import panel1450 as L

V2 = os.path.normpath(os.path.join(HERE, ".."))
FRAME_SEAT_OUT = os.path.join(V2, "vendor", "peli", "1450", "frame_seat.out")
R1_TRAY = 28.0                        # the r1 tray's depth frame_seat.py's M3 subtracts (TRAY = 28.0, frame_seat.py line 141 at c23c5e76);
                                      # a frame_seat.py that reads the r2 stack prints it in M3's label as "(<depth> from the ceiling)"
LID_FLAT_HALF_Y = 231.86 / 2          # the lid's flat ceiling, 346.16 x 231.86 (CASE-MARGINS.md section 2.1, Peli STEP #736)
MIN_MECH = 1.0                        # the case margins' minimum (frame_seat.py MIN_MECH)
RG316_R = 12.5                        # RG-316 bend radius the tree already applies (ASSEMBLY.md lead table, CASE-MARGINS.md part G)
LEAD_R = 20.0                         # the bend radius the tray's lanes give the DC and USB leads: the requirement on their picks
MARGIN = 3.0                          # kept between a lead's bend and the lid's flat ceiling edge
PLUG_MASS = 0.020                     # kg: the three mated harness plugs' share on the unit (INFERRED, no pick)
EDGE_R = 1.0                          # the enclosure's long-edge radius where the ledges bear (INFERRED from the maker's photographs)
PRINT_TOL = 0.2                       # printed part tolerance (INFERRED, FFF)
MIN_INSERT = PRINT_TOL                # the least clearance the unit AT ITS LARGEST and the frame must keep to every solid they pass on
                                      # their way in: the printed parts' own tolerance, so a part printed at its limit still lets them by
SWEEP = 60.0                          # how far outside its place each way in starts
STEP = 2.0                            # with --solids, the spacing of the positions along each way in
# the set's own allowances between the lid ceiling and a solid's face toward the face plate; none is stated by a source, so the
# sensitivity column takes each twice, as frame_seat.py does with every unstated allowance of the case
OWN_TOLS = [("bond line (INFERRED)", 0.10), ("lid plate 2.0 thickness (INFERRED, EN 485-4 class as frame_seat.py's plate)", 0.13),
            ("printed height of the tray (INFERRED)", PRINT_TOL)]
FRAME_TOL = ("printed thickness of the frame (INFERRED)", PRINT_TOL)
# Prusament PC Blend, technical data sheet v1.1 of 16 Feb 2022 (v2/vendor/materials/prusament-pc-blend-tds-v1.1-2022-02-16.pdf): typical
# values of specimens printed at 100 % infill, 0.20 mm layers; the design takes each typical value less its stated spread
PC = dict(interlayer=21.0 - 2.0, flexural=88.0 - 1.0, tensile=63.0 - 1.0, density=1.22, hdt045=113.0, hdt180=93.0)
INTERLAYER_SHEAR = 0.5 * PC["interlayer"]   # MPa: the sheet states no shear figure; half the interlayer tension is taken (INFERRED)
AL5052_SHEAR = 100.0                  # MPa, the lid plate's thread shear used for stripping (INFERRED class figure; no 5052 sheet is held)
A2_70_RP02 = 450.0                    # MPa, an A2-70 screw's 0.2 percent proof stress (ISO 3506-1 class; standard not held, INFERRED)
M3_STRESS_AREA = 5.03                 # mm2 (ISO 898-1 class; INFERRED)
DP8005_TPEEL = 9 * 4.448 / 25.4       # N/mm: 9 lb/in T-peel on 0.5 mm HDPE (3m-scotch-weld-dp8005.pdf page 2); the only strength the sheet gives
DROP_H = 1.22                         # m, TEST-PLAN E1 (MIL-STD-810H 516.8 Procedure IV, Table 516.8-IX first row)
DESIGN_G = 100.0                      # the load case: the peak CASE-MARGINS.md section 3 already assumes for E1 on the face ("an assumed 100 g
                                      # shock", INFERRED: TEST-PLAN E1 sets the drops, not a peak), applied in each of the six directions
E2_GRMS = 2.24                        # MIL-STD-810H 514.8 Annex C, composite wheeled vehicle, the envelope for an unknown orientation
                                      # (page 514.8C-13; v2/vendor/standards/mil-std-810h-method-514-8.md), "drive limiting to 3 sigma"
E3S_STORAGE = 71.0                    # C, TEST-PLAN E3-S
G0 = 9.80665
MASSES = dict(tray=0.0747, frame=0.0083, plate=0.0522)   # kg, from the solids (lid_tray_qmx_r2.py prints them; --solids re-checks)

# the face plate's parts: height above the plate's top face, and where that height is read. A seal under a head is taken as if it did
# not compress at all, which is a bound; no sheet states a tolerance on a head, so none is subtracted twice.
FACE_HEIGHT = {
    "XENARC_WINDOW": (L.PROUD_LIMIT, "a bound: panel1450 sets the glass level with the plate; the ruling of 2 Sep 2026 (appendix 14.6) lets a display surface stand %.1f proud at most" % L.PROUD_LIMIT),
    "XFRAME": (4.00, "a bound: ASSEMBLY.md names M4 x 8 and no head; the tallest class is taken, a cap head (ISO 4762 class, 4.00; standard not held, INFERRED)"),
    "SW_MAIN": (2.00 + 1.50, "C&K ATP19 sheet (Littelfuse, revised 02/05/25) page 2: S standard actuator, head 2.00; page 4: O-ring ATP19-OR 1.50 under it"),
    "SW_PI": (1.5 + 1.0, "C&K ATP16 sheet (5 Jul 22) page A-132: S standard/flat, head 1.5; page A-134: O-ring ATP16-OR 1 under it"),
    "SW_TEST": (1.5 + 1.0, "as SW_PI"),
    "LIGHT_GUIDE": (9.0 - 7.5, "Mentor sheet ll14-14, 1282.5004: A 7.5, B 9, so the head stands B - A = 1.5"),
}


def frame_seat_rows():
    out = {}
    pat = re.compile(r"^  (M\w+)\s+(.+?)\s+(\d+\.\d\d)\s+([+-]\d+\.\d\d)\s+([+-]\d+\.\d\d)\s+([+-]\d+\.\d\d)\s+([+-]\d+\.\d\d)\s+(OPEN, FAILS AS ASSUMED|NOT MET|OPEN|MET)")
    for line in open(FRAME_SEAT_OUT, encoding="utf-8"):
        m = pat.match(line.rstrip("\n"))
        if m:
            out[m.group(1)] = dict(nom=float(m.group(4)), worst=float(m.group(5)), wc2=float(m.group(7)), verdict=m.group(8), label=m.group(2))
    return out


def m3_tray(R):
    """The tray depth frame_seat.out's M3 row subtracted from the room: the r2 stack when its label states it, else the r1 tray's 28.0."""
    m = re.search(r"\(([\d.]+) from the ceiling\)", R["M3"]["label"])
    return float(m.group(1)) if m else R1_TRAY


def room(R=None):
    """The room between the face plate's top and the lid ceiling: nominal, at the worst, at the worst with unstated allowances twice."""
    R = R or frame_seat_rows(); t = m3_tray(R)
    return R["M3"]["nom"] + t, R["M3"]["worst"] + t, R["M3"]["wc2"] + t


def peak_g(s_mm):
    """Half-sine deceleration from the drop's impact velocity over a stopping distance s: a = pi v^2 / (4 s), v^2 = 2 g h, so a/g = pi h / (2 s)."""
    return math.pi * DROP_H * 1000.0 / (2.0 * s_mm)


# ---------------------------------------------------------------- boxes
def clearance(a, b):
    """Two boxes (x0, x1, y0, y1, z0, z1): their distance when apart, 0 when they touch, and when they overlap the least depth by which
    one would have to move to come free, as a negative number."""
    g = [max(a[2 * i] - b[2 * i + 1], b[2 * i] - a[2 * i + 1]) for i in range(3)]
    if max(g) > 1e-9:
        return math.sqrt(sum(max(x, 0.0) ** 2 for x in g))
    return min(0.0, max(g))


def swept(box, axis, travel):
    """The box and every place it passes through when it comes in along `axis` from `travel` away (negative: from the low side)."""
    b = list(box); i = "xyz".index(axis)
    if travel >= 0: b[2 * i + 1] += travel
    else: b[2 * i] += travel
    return tuple(b)


def grown(box, d, faces="x0 x1 y0 y1 z0 z1"):
    b = list(box)
    for k, f in enumerate(("x0", "x1", "y0", "y1", "z0", "z1")):
        if f in faces.split(): b[k] += d if f.endswith("1") else -d
    return tuple(b)


def plan_overlap(a, b):
    return min(a[1], b[1]) - max(a[0], b[0]) > 1e-9 and min(a[3], b[3]) - max(a[2], b[2]) > 1e-9


# ---------------------------------------------------------------- E: the fitting
def unit_at_its_largest(E, top_at=None, lower=0.0, grow=True):
    """The unit and what stands proud of it as the moving boxes of a way in: the body with the maker's unstated tolerance on each overall
    dimension, every proud item wider and further out by PROUD_TOL. top_at fixes the top face (in place the pads press it against the
    frame, so the unit's height tolerance moves its bottom); lower drops the whole unit (onto the floor, for the first pass's way in)."""
    t = Q.UNIT_TOL / 2 if grow else 0.0; p = Q.PROUD_TOL if grow else 0.0
    out = []
    for e in Q.parts(E, "unit", "proud"):
        b = e["box"]
        if e["part"] == "unit":
            b = grown(b, t)
            if top_at is not None: b = b[:5] + (top_at,)
        elif b[4] >= Q.Z_UT - 1e-9:                      # it stands on the top face
            b = grown(b, p, "x0 x1 y0 y1 z1")
        else:                                            # it stands on an end panel
            b = grown(b, p, ("x1" if b[0] > 0 else "x0") + " y0 y1 z0 z1")
        out.append(dict(e, box=tuple(round(v - (lower if k > 3 else 0.0), 4) for k, v in enumerate(b))))
    return out


def way_in(moving, fixed, axis, travel):
    """Every fixed solid against everything that moves: (solid, least clearance, the moving item that comes nearest, designed contact?)."""
    rows = []
    for f in fixed:
        best = None
        for m in moving:
            c = clearance(swept(m["box"], axis, travel), f["box"])
            seat = (f["part"] in m["seat"] or m["part"] in f["seat"]) and c < 1e-9       # meant to touch, and touching (or overlapping)
            if best is None or (c, m["name"]) < (best[0], best[1]): best = (c, m["name"], seat)
        rows.append(dict(solid=f["name"], part=f["part"], clearance=best[0], by=best[1], seat=best[2]))
    return rows


def judge(rows):
    """A designed contact (two solids meant to touch, which do) may touch and may not overlap; everything else keeps MIN_INSERT."""
    bad = [r for r in rows if (r["clearance"] < -1e-9 if r["seat"] else r["clearance"] < MIN_INSERT - 1e-9)]
    free = [r for r in rows if not r["seat"]]
    return bad, (min(free, key=lambda r: (r["clearance"], r["solid"])) if free else None)


def fitting(E=None):
    """The two ways in of the r2 set. 1: the unit, at its largest, lowered from above into the tray (the frame off, the pads in their
    windows). 2: the frame lowered over the unit in its place onto the wall tops."""
    E = E or Q.elements()
    tray = Q.parts(E, "tray")
    one = way_in(unit_at_its_largest(E), tray, "z", SWEEP)
    two = way_in(Q.parts(E, "frame"), tray + unit_at_its_largest(E, top_at=Q.Z_UT), "z", SWEEP)
    return [("1. the unit lowered into the tray, from %.0f above its place (the frame off)" % SWEEP, one),
            ("2. the frame lowered over the unit onto the wall tops, from %.0f above its place" % SWEEP, two)]


def pass1_elements():
    """CONTROL. The first pass's tray as recovered (v2/docs/records/w5tray/, lid_tray_qmx_r2.py sha256 3e89a3ca4d3d1d3b): ledges and end
    lintels that are part of the tray, at the height of the unit's top face, and the keeper off while the unit goes in. Its numbers are
    typed here because they are history: a fixture of what was judged NOT mergeable, never an input of the r2 set."""
    clr, wall, z_ut, z_top, z_sill, floor = 0.3, 4.0, 27.1, 29.1, 3.6, 1.6
    side_in, face_x = 31.5 + clr, 47.5 + clr
    side_out, base_x, base_y = side_in + wall, face_x + 8.0, side_in + wall + 8.0
    e = Q._e
    E = [e("tray", "floor", -base_x, base_x, -base_y, base_y, 0.0, floor, seat=("unit",)),
         e("tray", "back wall", -face_x, face_x, side_in, side_out, 0.0, z_top),
         e("tray", "knob-edge wall", -face_x, face_x, -side_out, -side_in, 0.0, z_ut),
         e("tray", "back ledge", -46.5, 46.5, side_in - 4.0, side_in, z_ut, z_top, seat=("unit",)),
         e("tray", "end block (hinge end)", face_x, base_x, -base_y, base_y, 0.0, z_sill)]
    for k, (x0, x1) in enumerate([(-46.5, -41.1), (-11.1, 11.1), (41.1, 46.5)]):
        E.append(e("tray", "knob-edge ledge %d" % (k + 1), x0, x1, -side_out, -side_in + 3.0, z_ut, z_top, seat=("unit",)))
    for sx, nm in ((-1, "keeper end"), (1, "hinge end")):
        E.append(e("tray", "lintel at the %s" % nm, sx * 47.5, sx * 50.5, -side_out, side_out, z_ut, z_top))
    for gx in (-44.0, -22.0, 0.0, 22.0, 44.0):
        for sy in (-1, 1):
            E.append(e("tray", "gusset at (%+.0f, %s)" % (gx, "back" if sy > 0 else "knob edge"), gx - 1.25, gx + 1.25, sy * side_out, sy * base_y, floor, 25.0))
    for u in Q.parts(Q.elements(), "unit", "proud"):
        E.append(dict(u, seat=()))
    return E, dict(place_x=171.0 - base_y, place_y=10.0, g_b=0.5)


PASS1_ROWS = [("M3r2b", ("SW_MAIN", "SW_PI", "SW_TEST"), 0.20 + 2.0 + 27.1, "under the unit's top face, over SW_MAIN, SW_PI, SW_TEST")]   # the first pass's record, section B


def pass1_way_in():
    """The first pass's documented way in: slid in from the keeper end, right panel first, under both ledges and that end's lintel. The
    unit is taken at its most generous: nominal, nothing widened, and lowered onto the floor with the pads fully yielded."""
    E, P = pass1_elements()
    return way_in(unit_at_its_largest(E, lower=P["g_b"], grow=False), Q.parts(E, "tray"), "x", -200.0)


# ---------------------------------------------------------------- B: the face room
def face_parts():
    """The face plate's parts that stand on its top face, from panel1450: (ref, footprint in the case frame, height, where it is read).
    Laser marking has no height and is left out; the light sensor's light guide is not in FACE_ITEMS and is added with the LEDs' collar."""
    out = []
    items = [(n, c, s) for n, c, s, kind in L.FACE_ITEMS if kind == "hw"]
    items.append((L.LIGHT_SENSOR[0], L.LIGHT_SENSOR[1], (L.LED_HOLE + 1.4, L.LED_HOLE + 1.4)))
    leds = {r for r, _, _ in L.STATUS_LEDS + L.BAR_LEDS} | {L.LIGHT_SENSOR[0]}
    for n, c, (w, h) in items:
        key = "LIGHT_GUIDE" if n in leds else ("XFRAME" if n.startswith("XFRAME") else n)
        if key not in FACE_HEIGHT: continue                                   # a part with no height stated here: it is reported apart
        out.append((n, (c[0] - w / 2, c[0] + w / 2, c[1] - h / 2, c[1] + h / 2), FACE_HEIGHT[key][0], key))
    return out


def unread_face_parts():
    """Face parts this file holds no height for: each is named with whether any solid of the set stands over it."""
    return [n for n, c, s, kind in L.FACE_ITEMS if kind == "hw" and not (n in FACE_HEIGHT or n.startswith("XFRAME") or n in {r for r, _, _ in L.STATUS_LEDS + L.BAR_LEDS})]


def plug_envelopes():
    """The admitted bodies of the three permanent leads' plugs (DC, RF, USB), which stay in when the lid closes, as boxes."""
    room_r = LID_FLAT_HALF_Y - (Q.PLACE_Y + Q.U0); room_l = LID_FLAT_HALF_Y - (Q.U0 - Q.PLACE_Y)
    reach = {"RF": room_r - RG316_R - MARGIN, "USB": room_r - LEAD_R - MARGIN, "DC": room_l - LEAD_R - MARGIN}
    out = []
    for nm in ("DC", "RF", "USB"):
        j = Q.JACKS[nm]; r = Q.admitted_radius(nm); sx = 1 if j["panel"] == "R" else -1
        ry = max(r, Q.USBC_OVERMOLD_W / 2) if nm == "USB" else r
        out.append(Q._e("plug", "%s plug, the body the set admits" % nm, sx * Q.U0, sx * (Q.U0 + reach[nm]),
                        -Q.UNIT[1] / 2 + min(j["v"]) - Q.JACK_RANGE - ry, -Q.UNIT[1] / 2 + max(j["v"]) + Q.JACK_RANGE + ry,
                        Q.Z_UB + min(j["h"]) - Q.JACK_RANGE - r, Q.Z_UB + max(j["h"]) + Q.JACK_RANGE + r))
    return out, reach


def over(E, foot_case, place):
    """The solids of E over a footprint given in the case frame: the deepest first."""
    px, py = place
    f = (foot_case[2] - py, foot_case[3] - py, foot_case[0] - px, foot_case[1] - px)       # part x = case Y - PLACE_Y, part y = case X - PLACE_X
    hit = [e for e in E if e["part"] != "plate" and plan_overlap(e["box"], f)]
    return sorted(hit, key=lambda e: (-e["box"][5], e["name"]))


def own_tols(e):
    t = list(OWN_TOLS)
    if e["part"] in ("frame", "screw"): t.append(FRAME_TOL)
    return t


def face_rows(E=None, place=None, R=None):
    """One row per face part under the set, and one for the flat face under the deepest solid of all."""
    E = (E or Q.elements()) + ([] if E else plug_envelopes()[0]); place = place or (Q.PLACE_X, Q.PLACE_Y)
    nom, worst, wc2 = room(R)
    rows = []
    def row(ref, foot, height, key, e, n_over):
        depth = Q.BOND + Q.PLATE_T + e["box"][5]
        own = sum(t for _, t in own_tols(e))
        r = dict(ref=ref, foot=foot, height=height, key=key, solid=e["name"], part=e["part"], n_over=n_over, depth=depth,
                 nom=nom - depth - height, worst=worst - own - depth - height, wc2=wc2 - 2 * own - depth - height)
        r["verdict"] = "NOT MET" if r["worst"] < MIN_MECH - 1e-9 else ("OPEN" if r["wc2"] < MIN_MECH - 1e-9 else "MET")
        r["inferred"] = e["part"] == "proud"
        rows.append(r)
    for ref, foot, height, key in face_parts():
        hit = over(E, foot, place)
        if hit: row(ref, foot, height, key, hit[0], len(hit))
    deepest = sorted((e for e in E if e["part"] != "plate"), key=lambda e: (-e["box"][5], e["name"]))[0]
    b = deepest["box"]
    row("FACE", (place[0] + b[2], place[0] + b[3], place[1] + b[0], place[1] + b[1]), 0.0, "FACE", deepest, 1)
    return rows


def claimed_depth_problems(E, place, claims):
    """A record's face-room rows against the solids: a row that measures a part's room from a solid that is not the deepest over it."""
    probs = []
    feet = {n: f for n, f, _, _ in face_parts()}
    for key, refs, depth, label in claims:
        for ref in refs:
            hit = over(E, feet[ref], place)
            true = Q.BOND + Q.PLATE_T + hit[0]["box"][5] if hit else None
            if true is not None and true > depth + 1e-9:
                probs.append("%s takes %s's room from %.2f below the ceiling (%s); the %s stands over it at %.2f, %.2f deeper" % (
                    key, ref, depth, label, hit[0]["name"], true, true - depth))
    return probs


# ---------------------------------------------------------------- D: retention
def wall_section():
    """One post pitch of a long wall at its root (the floor joint, an interlayer plane): the wall strip and the post's foot.
    Returns area, centroid distance from the inner face, second moment about the centroid (mm2, mm, mm4) and the pitch."""
    xs = sorted(Q.POST["x"]); pitch = min(b - a for a, b in zip(xs, xs[1:]))
    parts = [(pitch * Q.WALL, Q.WALL / 2, pitch * Q.WALL ** 3 / 12.0),
             (Q.POST["w"] * Q.POST["depth"], Q.WALL + Q.POST["depth"] / 2, Q.POST["w"] * Q.POST["depth"] ** 3 / 12.0)]
    A = sum(a for a, _, _ in parts); c = sum(a * y for a, y, _ in parts) / A
    I = sum(i + a * (y - c) ** 2 for a, y, i in parts)
    return A, c, I, pitch


def retention():
    """The links of each load path: (direction, link, capacity N, note). The capacity is the whole load the path holds when this link
    is the one that gives."""
    links = []
    n_side = len(Q.FRAME_SCREWS) // 2
    head = math.pi / 4 * (Q.BH["d_head"] ** 2 - Q.BH["hole"] ** 2) * PC["tensile"]
    nut = (Q.NUT["s"] ** 2 - math.pi / 4 * Q.BH["hole"] ** 2) * PC["tensile"]
    slot_area = Q.NUT["slot_w"] * (Q.BASE_Y - (Q.POST_Y - Q.NUT["slot_w"] / 2))
    post = (Q.POST["w"] * (Q.POST["depth"] + Q.WALL) - slot_area) * PC["interlayer"]
    screw = M3_STRESS_AREA * A2_70_RP02
    per_screw = min(head, nut, post, screw)
    for side, ov, length in (("back", Q.LEDGE_BACK, Q.UNIT[0] - 2 * EDGE_R),
                             ("knob-edge", Q.LEDGE_FRONT, sum(min(b, Q.U0 - EDGE_R) - max(a, -Q.U0 + EDGE_R) for a, b in Q.FRONT_SEGMENTS))):
        lever = (Q.CLR + EDGE_R + ov) / 2
        q = PC["flexural"] * Q.FRAME_T ** 2 / (6 * lever)
        links.append(("out", "frame, %s ledge bending at the wall's inner face (%.1f long, lever %.2f)" % (side, length, lever), 2 * q * length, "half the load on each side"))
        arm = Q.POST_Y - (Q.SIDE_IN - lever)                       # from the screw line to the ledge's load
        pry = (Q.BASE_Y - (Q.SIDE_IN - lever)) / (Q.BASE_Y - Q.POST_Y)   # the rail is a lever on the post's outer edge
        w_eff = min(2 * arm + Q.BH["d_head"], Q.POST["x"][2] - Q.POST["x"][0])
        links.append(("out", "frame, %s rail bending between its screws and its ledge (arm %.1f, %.1f wide at each of %d screws)" % (side, arm, w_eff, n_side),
                      2 * n_side * PC["flexural"] * w_eff * Q.FRAME_T ** 2 / 6 / arm, "half the load on each side"))
        links.append(("out", "%s frame screws, %d, prised by %.2f: the least of head through the frame %.0f, nut on its slot's roof %.0f, post at the slot %.0f, screw %.0f N" % (
            side, n_side, pry, head, nut, post, screw), 2 * n_side * per_screw / pry, "half the load on each side"))
    engage = 5.0 - Q.Z_SILL                                             # M3 x 5 flush at the boss top: its tip 5.0 below it
    strip = math.pi * 3.0 * engage * 0.75 * AL5052_SHEAR
    links.append(("out", "M3 threads in the 2.0 lid plate, the four screws between the posts (engagement %.1f, tip %.1f short of the bond)" % (engage, Q.PLATE_T - engage),
                  4 * strip, "INFERRED shear; the six end screws not counted"))
    pull = math.pi / 4 * (Q.CSK["d_head"] ** 2 - Q.CSK["hole"] ** 2) * PC["tensile"]
    links.append(("out", "countersunk heads pulling through the %.1f flange, the same four" % Q.Z_SILL, 4 * pull, ""))
    fl_arm = (Q.POST["x"][1] - Q.POST["x"][0]) / 2 - Q.POST["w"] / 2    # from a post's side to the screw between two posts
    fl = PC["flexural"] * Q.POST["depth"] * Q.Z_SILL ** 2 / 6 / fl_arm
    links.append(("out", "tray flange bending between a post and the screw beside it (%.1f x %.1f, arm %.2f), eight places" % (Q.POST["depth"], Q.Z_SILL, fl_arm), 8 * fl,
                  "the floor under the unit not counted"))
    perim = 2 * (2 * Q.BASE_X + 2 * Q.BASE_Y) - (8 - 2 * math.pi) * 6.0
    links.append(("out*", "the lid plate's DP8005 bond on the lid's polypropylene: SCOPING ONLY (T-peel of 0.5 mm HDPE x perimeter %.0f)" % perim,
                  DP8005_TPEEL * perim, "no held figure bounds it"))
    band = Q.SILL_H - 2 * PRINT_TOL
    n0, n1 = Q.rf_notch()
    for end, length in (("left", Q.UNIT[1] - 2 * EDGE_R), ("right", (Q.UNIT[1] / 2 - EDGE_R) - n1)):
        links.append(("x", "the %s panel's bottom band bearing on its sill (%.1f x %.1f at the loose corner)" % (end, band, length), band * length * PC["tensile"],
                      "the sill cut away under the RF jack" if end == "right" else ""))
    links.append(("x", "the hinge-end sill sheared off the floor (%.1f x %.1f)" % (Q.END_L, Q.BASE_Y - n1), Q.END_L * (Q.BASE_Y - n1) * INTERLAYER_SHEAR, "INFERRED shear"))
    links.append(("x", "ten M3 through the flange and both sills, bearing on the printed holes over %.1f" % Q.Z_SILL, 10 * 3.0 * Q.Z_SILL * PC["tensile"], "friction not counted"))
    A, c, I, pitch = wall_section()
    n_pitch = 2 * Q.WALL_X / pitch
    lever_y = Q.Z_UB + Q.UNIT[2] / 2 - Q.FLOOR
    links.append(("y", "one wall pushed outward, bending across the layers at its root (resultant %.1f above it, %.1f post pitches)" % (lever_y, n_pitch),
                  PC["interlayer"] * I / (c * lever_y) * n_pitch, "the frame's tie to the other wall not counted"))
    return links


# ---------------------------------------------------------------- the record
def report():
    R = frame_seat_rows(); E = Q.elements()
    L_ = []
    ok = True
    L_.append("QMX lid tray r2: the fit, the face room, the retention and the fitting, from v2/cad/lid_tray_qmx_r2.py, panel1450.py and frame_seat.out (%s)." % (
        "M3 nominal %+.2f, worst %+.2f for a tray %.2f from the ceiling" % (R["M3"]["nom"], R["M3"]["worst"], m3_tray(R))))
    L_.append("Prototype design: nothing made, printed or fitted. SCALED and INFERRED inputs are marked; the makers' figures are named.")
    L_.append("")
    # ---- A
    L_.append("A. JACKS AND PLUGS (the set open across both end panels above the sills; sill top %.1f above the unit's bottom face; under the RF jack the" % Q.SILL_H)
    n0, n1 = Q.rf_notch()
    L_.append("   hinge-end sill is cut down to the floor from y %.1f to %.1f, %.1f across)" % (n0, n1, n1 - n0))
    L_.append("   jack    panel  v from knob edge  height (scaled)   admitted plug body   who and what")
    worst_r = {}
    for nm, j in Q.JACKS.items():
        r = Q.admitted_radius(nm); worst_r[nm] = r
        L_.append("   %-7s %-5s  %5.1f .. %5.1f     %5.1f .. %5.1f     d %5.1f (r %4.1f)    %s" % (
            nm, j["panel"], min(j["v"]) - Q.JACK_RANGE, max(j["v"]) + Q.JACK_RANGE, min(j["h"]) - Q.JACK_RANGE, max(j["h"]) + Q.JACK_RANGE,
            2 * r, r, j["use"]))
    L_.append("   USB-C: the admitted envelope is a height, %.1f above and below the axis; an overmold %.2f wide (a class, INFERRED) is the other" % (
        worst_r["USB"], Q.USBC_OVERMOLD_W))
    L_.append("   bound, and the unit's own panel sets it against the PTT plug: PTT to USB centres %.1f .. %.1f apart, so a PTT plug beside a %.2f" % (
        min(Q.JACKS["USB"]["v"]) - max(Q.JACKS["PTT"]["v"]), max(Q.JACKS["USB"]["v"]) - min(Q.JACKS["PTT"]["v"]), Q.USBC_OVERMOLD_W))
    L_.append("   overmold may be %.1f across at most (the unit's panel, not the tray). Nothing of the tray lies within an end panel's outline above" % (
        2 * (min(Q.JACKS["USB"]["v"]) - max(Q.JACKS["PTT"]["v"]) - Q.USBC_OVERMOLD_W / 2)))
    L_.append("   the sills, and the long walls stop %.1f short of the end faces; the frame's end bars lie above the unit's top face (%.1f to %.1f" % (Q.WALL_END, Q.Z_UT, Q.Z_TOP))
    L_.append("   above the plate), over every plug body. The RF jack's own nut (%.1f across corners, INFERRED) stands %.2f above the floor at its lowest." % (
        Q.BNC["across_corners"], Q.Z_UB + min(Q.JACKS["RF"]["h"]) - Q.JACK_RANGE - Q.BNC["across_corners"] / 2 - Q.FLOOR))
    plugs, reach = plug_envelopes()
    room_r = LID_FLAT_HALF_Y - (Q.PLACE_Y + Q.U0); room_l = LID_FLAT_HALF_Y - (Q.U0 - Q.PLACE_Y)
    L_.append("   Leads (permanent: DC, RF, USB; the operator's Paddle, Audio and PTT plugs come out before the lid closes, the case closes sealed):")
    L_.append("   right panel to the flat ceiling's edge (case Y %.2f): %.2f; the RF jumper turns at R %.1f (RG-316, the tree's figure), so its" % (
        LID_FLAT_HALF_Y, room_r, RG316_R))
    L_.append("     BNC plug may reach %.1f from the panel before its cable turns; the USB-C lead, turning at R %.1f, %.1f." % (reach["RF"], LEAD_R, reach["USB"]))
    L_.append("   left panel to the flat ceiling's edge (case Y %.2f): %.2f; the DC lead loops back toward the hinge at R %.1f west of the tray," % (
        -LID_FLAT_HALF_Y, room_l, LEAD_R))
    L_.append("     so its plug may reach %.1f from the panel. R %.1f is the requirement on the DC and USB lead picks (not picked)." % (reach["DC"], LEAD_R))
    L_.append("")
    # ---- B
    nom, worst, wc2 = room(R)
    L_.append("B. FACE ROOM with the lid closed, each row from the solid above the part (frame_seat.out M3's room between the face top and the lid")
    L_.append("   ceiling: %.2f nominal, %.2f at the worst, %.2f at the worst with every unstated allowance taken twice, the sensitivity reading)" % (nom, worst, wc2))
    L_.append("   stack from the ceiling: bond %.2f + lid plate %.1f = %.2f to the tray's mounting face; + floor %.1f + pad gap %.1f + unit %.1f = %.2f to the unit's" % (
        Q.BOND, Q.PLATE_T, Q.BOND + Q.PLATE_T, Q.FLOOR, Q.G_B, Q.UNIT[2], Q.BOND + Q.PLATE_T + Q.Z_UT))
    L_.append("   top face; + frame %.1f = %.2f; + screw head %.2f = %.2f; the knob tips %.2f (knob %.1f, INFERRED)" % (
        Q.FRAME_T, Q.BOND + Q.PLATE_T + Q.Z_TOP, Q.BH["k"], Q.BOND + Q.PLATE_T + Q.Z_HEAD, Q.BOND + Q.PLATE_T + Q.Z_UT + Q.KNOB_H, Q.KNOB_H))
    L_.append("   the set's own allowances, none stated by a source, in the worst once and in the sensitivity reading twice:")
    for l, t in OWN_TOLS: L_.append("      %.2f  %s" % (t, l))
    L_.append("      %.2f  %s, on the frame and its screw heads only" % (FRAME_TOL[1], FRAME_TOL[0]))
    L_.append("   (the r1 tray's %.1f counted no lid plate; its ASSEMBLY.md row names a 2 mm nut plate the M3 row left out)" % R1_TRAY if abs(m3_tray(R) - R1_TRAY) < 1e-9 else
              "   (frame_seat.out's M3 reads the r2 stack)")
    L_.append("   %-19s %-32s %6s  %-44s %6s  %7s %7s %7s  %s" % ("row and part", "footprint, case X and Y", "height", "the deepest solid over it (of how many)", "depth", "nominal", "worst", "twice", "verdict, min %.2f" % MIN_MECH))
    rows = face_rows(E + plug_envelopes()[0], None, R)
    for r in rows:
        v = r["verdict"]
        if r["inferred"]:
            v += ", on an INFERRED height of the unit's"
        if r["verdict"] == "NOT MET": ok = False
        L_.append("   %-19s X %6.1f..%6.1f Y %6.1f..%6.1f %6.2f  %-44s %6.2f  %+7.2f %+7.2f %+7.2f  %s" % (
            "M3r2." + r["ref"], r["foot"][0], r["foot"][1], r["foot"][2], r["foot"][3], r["height"], ("%s (%d)" % (r["solid"], r["n_over"]))[:44], r["depth"],
            r["nom"], r["worst"], r["wc2"], v))
    knob = [r for r in rows if r["solid"].endswith("knob")]
    kw = min(r["worst"] for r in knob); k2 = min(r["wc2"] for r in knob)
    L_.append("   The knob rows rest on the knob's height, which the maker does not state: %.1f is INFERRED. They are MET at the sensitivity reading for a" % Q.KNOB_H)
    L_.append("   knob up to %.2f and at the plain worst for a knob up to %.2f; the check is T9 (chalk on the knob tips, the lid closed) or the unit in hand." % (
        Q.KNOB_H + k2 - MIN_MECH, Q.KNOB_H + kw - MIN_MECH))
    L_.append("   heights above the face, and where each is read (a seal under a head is taken as if it did not compress, a bound):")
    for k, v in FACE_HEIGHT.items(): L_.append("      %-14s %5.2f  %s" % (k, v[0], v[1]))
    unread = [n for n in unread_face_parts() if over(E + plug_envelopes()[0], [f for f in [(c[0] - s[0] / 2, c[0] + s[0] / 2, c[1] - s[1] / 2, c[1] + s[1] / 2)
              for m, c, s, k in L.FACE_ITEMS if m == n]][0], (Q.PLACE_X, Q.PLACE_Y))]
    L_.append("   face parts with no height read here and a solid of the set over them: %s" % (", ".join(unread) if unread else "none"))
    if unread: ok = False
    L_.append("   M19 (east edge at X %.1f inside the flat ceiling): unchanged, nominal %+.2f, worst %+.2f, %s" % (Q.EAST_EDGE_X, R["M19"]["nom"], R["M19"]["worst"], R["M19"]["verdict"]))
    L_.append("   place: X %.1f .. %.1f (grown %.1f west of r1's 102.0 for the posts; the lid ceiling is free there), Y %.1f .. %.1f" % (
        Q.SPAN_X[0], Q.SPAN_X[1], 102.0 - Q.SPAN_X[0], Q.SPAN_Y[0], Q.SPAN_Y[1]))
    L_.append("   knobs at case (X %.1f, Y %.1f) and (X %.1f, Y %.1f), each d %.1f: west of the buttons' column (X 137.4 .. 162.6 with its collars); their west" % (
        Q.PLACE_X + Q.KNOB_Y, Q.PLACE_Y - Q.KNOB_X, Q.PLACE_X + Q.KNOB_Y, Q.PLACE_Y + Q.KNOB_X, Q.KNOB_D))
    L_.append("   rims stand %.1f over the monitor's window (its east edge X %.3f)" % (L.XENARC["c"][0] + L.XENARC["window"][0] / 2 - (Q.PLACE_X + Q.KNOB_Y - Q.KNOB_D / 2),
                                                                                         L.XENARC["c"][0] + L.XENARC["window"][0] / 2))
    L_.append("")
    # ---- C
    t0, t1 = Q.PAD["t"] * (1 - Q.PAD["t_tol"]), Q.PAD["t"] * (1 + Q.PAD["t_tol"])
    gb0, gb1 = Q.Z_UB - PRINT_TOL - Q.UNIT_TOL, Q.Z_UB + PRINT_TOL + Q.UNIT_TOL      # the unit's bottom above the plate: wall height +-0.2, unit height +-0.2
    area = 2 * Q.PAD["size"][0] * Q.PAD["size"][1]
    L_.append("C. PADS (%s; standing on the plate in two floor windows %.0f x %.0f, %.0f mm2)" % (Q.PAD["material"], Q.PAD["size"][0], Q.PAD["size"][1], area))
    L_.append("   compression: nominal %.2f (%.0f %%), least %.2f (%.0f %%, thin pad, unit high), most %.2f (%.0f %%, thick pad, unit low)" % (
        Q.PAD["t"] - Q.Z_UB, 100 * (Q.PAD["t"] - Q.Z_UB) / Q.PAD["t"], t0 - gb1, 100 * (t0 - gb1) / t0, t1 - gb0, 100 * (t1 - gb0) / t1))
    f25 = (Q.PAD["cfd25_kpa"][0] * area / 1000, Q.PAD["cfd25_kpa"][1] * area / 1000)
    L_.append("   so the unit always stands on the pads, pressed up against the frame's ledges; at 25 %% the sheet gives %.0f to %.0f kPa, %.0f to %.0f N" % (
        Q.PAD["cfd25_kpa"][0], Q.PAD["cfd25_kpa"][1], f25[0], f25[1]))
    L_.append("   (the sheet states 25 % only: the preload at the nominal, the least and the most compression is not stated). The unit's bottom at its")
    L_.append("   lowest stands %.2f above the floor top (%.1f), the hard stop toward the lid. The pads are compressed by screwing the frame down, not by" % (gb0 - Q.FLOOR, Q.FLOOR))
    L_.append("   pushing the unit past them. The sheet: constant use to 90 C, compression set 10 %% at most at 70 C, so a pad may lose up to %.2f of its" % (0.10 * (t1 - gb0)))
    L_.append("   compression in storage at +%.0f C, which the least compression above does not cover: the pads are renewed if T9 finds the unit loose." % E3S_STORAGE)
    L_.append("")
    # ---- D
    m_u = Q.UNIT_MASS + PLUG_MASS
    m_all = m_u + sum(MASSES.values())
    w = m_u * G0
    load = DESIGN_G * w
    L_.append("D. RETENTION. Unit and mated plugs %.3f kg (maker's 220 g + %.0f g INFERRED): %.2f N per g. With the tray, frame and plate %.3f kg." % (m_u, 1000 * PLUG_MASS, w, m_all))
    L_.append("   LOAD CASE the set is designed to: %.0f g on the unit and its plugs, %.0f N, in each of the six directions, held still. It is the peak" % (DESIGN_G, load))
    L_.append("   CASE-MARGINS.md already assumes for the face under TEST-PLAN E1 (INFERRED: E1 sets 26 drops from %.2f m, not a peak), not a measured one." % DROP_H)
    L_.append("   Material: Prusament PC Blend (TDS v1.1): interlayer %.0f, flexural %.0f, tensile %.0f MPa taken (typical less spread); printed" % (
        PC["interlayer"], PC["flexural"], PC["tensile"]))
    L_.append("   floor down (the frame flat), 100 percent infill, 0.20 mm layers as the sheet's specimens; walls and posts vertical, so their tension")
    L_.append("   crosses the layers, and the frame's bending lies in its layers. Heat deflection %.0f C at 0.45 MPa and %.0f C at 1.80 MPa, over E3-S's +%.0f C." % (
        PC["hdt045"], PC["hdt180"], E3S_STORAGE))
    links = retention()
    L_.append("   %-4s %-150s %8s %7s %7s" % ("dir", "link", "N", "g", "factor"))
    known = []
    for d, label, F, note in links:
        g = F / (m_all * G0) if d == "out*" else F / w
        if d != "out*":
            known.append((g, d, label))
        L_.append("   %-4s %-150s %8.0f %7.0f %7s  %s" % (d, label[:150], F, g, "" if d == "out*" else "%.1f" % (F / load), note))
    gmin = min(known)
    perim = 2 * (2 * Q.BASE_X + 2 * Q.BASE_Y) - (8 - 2 * math.pi) * 6.0
    L_.append("   Governing link on the makers' typical figures: %.0f g, %.1f times the load case (direction %s: %s)." % (gmin[0], gmin[0] / DESIGN_G, gmin[1], gmin[2].split(" (")[0]))
    L_.append("   The bond is not bounded by any held figure: its T-peel scoping number (%.0f g) is for a flexible strip, not a rigid 2 mm plate, and is" % (
        DP8005_TPEEL * perim / (m_all * G0)))
    L_.append("   no bound; it goes to CASE-MARGINS T8 as a pull test on the case's polypropylene, after a thermal cycle (the plate and the lid expand")
    L_.append("   differently between -33 and +71 C, and no expansion figure of Peli's polypropylene is held).")
    lev_b = (Q.CLR + EDGE_R + Q.LEDGE_BACK) / 2; lev_f = (Q.CLR + EDGE_R + Q.LEDGE_FRONT) / 2
    len_b = Q.UNIT[0] - 2 * EDGE_R; len_f = sum(min(b, Q.U0 - EDGE_R) - max(a, -Q.U0 + EDGE_R) for a, b in Q.FRONT_SEGMENTS)
    s_per_n = max(0.5 * lev_b * 6 / (len_b * Q.FRAME_T ** 2), 0.5 * lev_f * 6 / (len_f * Q.FRAME_T ** 2))
    L_.append("   SUSTAINED: the pads' preload bends the frame's ledges all the time, +%.0f C storage included: %.4f MPa at the knob-edge ledges' root per" % (E3S_STORAGE, s_per_n))
    L_.append("   newton of preload, so %.2f to %.2f MPa at the sheet's 25 %% figures, and the preload would have to reach %.0f N to load the root to the" % (
        s_per_n * f25[0], s_per_n * f25[1], 0.45 / s_per_n))
    L_.append("   0.45 MPa of the sheet's %.0f C heat deflection figure, %.0f N for the 1.80 MPa of its %.0f C figure. Both figures are over +%.0f C. The" % (
        PC["hdt045"], 1.80 / s_per_n, PC["hdt180"], E3S_STORAGE))
    L_.append("   preload at the nominal %.0f %% and the most %.0f %% compression is higher than at 25 %% and not stated, so the stress there is not bounded:" % (
        100 * (Q.PAD["t"] - Q.Z_UB) / Q.PAD["t"], 100 * (t1 - gb0) / t1))
    L_.append("   OPEN, read after E3-S (the frame flat on the wall tops, the unit still clamped) and by T9.")
    L_.append("   E2 (MIL-STD-810H 514.8 Annex C, composite wheeled vehicle, 40 minutes an axis in the standard, 1 hour in TEST-PLAN): %.2f g rms in the" % E2_GRMS)
    L_.append("   envelope for an unknown orientation, %.2f g at the 3 sigma the standard limits the drive to, AT THE CASE. The pads' preload keeps the unit" % (3 * E2_GRMS))
    L_.append("   against the ledges up to %.1f to %.1f g (the sheet's 25 %% figures over %.2f N per g), so it stays seated if the lid passes the case's" % (f25[0] / w, f25[1] / w, w))
    L_.append("   vibration on magnified by less than %.1f to %.1f. The lid's own response is not known: OPEN, read in E2 (the unit is looked at for" % (
        f25[0] / w / (3 * E2_GRMS), f25[1] / w / (3 * E2_GRMS)))
    L_.append("   fretting on its top face's edges, the six frame screws and the ten tray screws for loosening). A unit that leaves the ledges for an")
    L_.append("   instant is still held: it moves %.1f at most toward the lid, onto the pads and then the floor." % (Q.Z_UB - Q.FLOOR + PRINT_TOL + Q.UNIT_TOL))
    L_.append("   E1's peak on the lid is not stated by MIL-STD-810H (it sets the drop, not a pulse). Half-sine from %.2f m over a stopping distance s:" % DROP_H)
    L_.append("   " + ";  ".join("s %4.1f mm: %4.0f g" % (s, peak_g(s)) for s in (2.0, 5.0, 10.0, 20.0)))
    L_.append("   The known links hold to %.0f g, which that bound passes for s >= %.1f mm and fails below: a bound that includes failure. No board," % (
        gmin[0], math.pi * DROP_H * 1000 / (2 * gmin[0])))
    L_.append("   interface or purchase depends on it (the remedy, the same parts machined in 6061 or a larger bonded plate, moves no board), so the")
    L_.append("   retention is DESIGNED to the load case above and its verdict against E1 stays OPEN, allocated to E1 with an accelerometer on the lid")
    L_.append("   and to T8 for the bond.")
    L_.append("")
    # ---- E
    L_.append("E. THE FITTING. The unit is taken at its largest: the body %.1f larger on each overall dimension (the maker states no tolerance, INFERRED)," % Q.UNIT_TOL)
    L_.append("   and everything that stands proud of it %.1f wider and further out: the knobs d %.1f and %.1f high, the button actuators d %.1f and %.1f high, the" % (
        Q.PROUD_TOL, Q.KNOB_D, Q.KNOB_H, Q.BUTTON_ACT["d"], Q.BUTTON_ACT["h"]))
    L_.append("   RF jack's nut %.1f across corners with its barrel %.0f out of the right panel, the 3.5 mm jacks' bushings d %.1f and %.1f out (all INFERRED from" % (
        Q.BNC["across_corners"], Q.BNC["out"], Q.BUSHING["d"], Q.BUSHING["out"]))
    L_.append("   the maker's photographs; the encoder shafts d %.1f stand inside the knobs); the panel screws are countersunk and the four feet are NOT fitted." % Q.SHAFT["d"])
    L_.append("   Each moving item is taken with every place it passes through on a straight way in; a designed contact (the unit on the floor's stop,")
    L_.append("   the frame on the wall tops and on the unit's top face) may touch and may not overlap; everything else keeps %.2f, the printed parts' own" % MIN_INSERT)
    L_.append("   tolerance.")
    for title, rows_ in fitting(E):
        bad, least = judge(rows_)
        L_.append("   %s" % title)
        L_.append("      %-46s %9s  %s" % ("solid", "clearance", "nearest to it"))
        for r in rows_:
            L_.append("      %-46s %9.2f  %s%s" % (r["solid"], r["clearance"], r["by"], "  (designed contact)" if r["seat"] else ""))
        if bad: ok = False
        L_.append("      RESULT: %s; the least clearance %.2f, %s to the %s" % ("PASS" if not bad else "FAIL (%s)" % ", ".join(b["solid"] for b in bad),
                                                                          least["clearance"], least["by"], least["solid"]))
    L_.append("   CONTROL 1, which must FAIL: the first pass's tray (ledges and end lintels part of the tray) and its documented way in, the unit slid")
    L_.append("   in from the keeper end under the ledges and that end's lintel, taken at its most generous (nominal, nothing widened, lowered %.1f onto" % pass1_elements()[1]["g_b"])
    L_.append("   the floor):")
    p1 = pass1_way_in(); bad1, _ = judge(p1)
    for r in sorted(bad1, key=lambda r: (r["clearance"], r["solid"])):
        L_.append("      %-46s %9.2f  %s" % (r["solid"], r["clearance"], r["by"]))
    L_.append("      RESULT: %s" % ("FAILS as it must: %d solids of that tray stand in the unit's way" % len(bad1) if bad1 else "PASSES: THE CHECK IS BROKEN"))
    if not bad1: ok = False
    E1, P1 = pass1_elements()
    probs = claimed_depth_problems(E1, (P1["place_x"], P1["place_y"]), PASS1_ROWS)
    L_.append("   CONTROL 2, which must FAIL: the first pass's face-room row M3r2b against the solids of its own tray:")
    for p in probs: L_.append("      " + p)
    L_.append("      RESULT: %s" % ("FAILS as it must: %d parts stand under a deeper solid than the row measured from" % len(probs) if probs else "PASSES: THE CHECK IS BROKEN"))
    if not probs: ok = False
    L_.append("")
    L_.append("RESULT of sections B and E: %s" % ("PASS (no row NOT MET, both ways in clear, both controls fail)" if ok else "FAIL"))
    return "\n".join(L_) + "\n", ok


# ---------------------------------------------------------------- the same on the solids
def solids_check():
    """Boolean checks on the built solids. 1: the table is what was built (each part's volume and bounding box against the table's own
    solids, and the deepest point of the built set over every face part against section B's). 2: in place, the unit, every admitted plug
    body at the four corners of its jack's scaled place, and each knob with its finger room touch neither printed part. 3: on their way
    in, the unit at its largest and the frame meet nothing at any position, and keep their distance."""
    import build123d as bd
    E = Q.elements()
    tray, frame = Q.build_tray(), Q.build_frame()
    out = ["", "SOLIDS (build123d %s)" % bd.__version__]
    good = True
    # 1. the table is what was built
    out.append("1. THE TABLE IS WHAT WAS BUILT")
    for nm, s, part in (("tray", tray, "tray"), ("frame", frame, "frame")):
        u = Q._union(bd, Q.parts(E, part))
        outside = (s - u).volume; bb, ub = s.bounding_box(), u.bounding_box()
        same_box = all(abs(a - b) < 1e-6 for a, b in zip((bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z), (ub.min.X, ub.min.Y, ub.min.Z, ub.max.X, ub.max.Y, ub.max.Z)))
        out.append("   %-6s built %9.1f mm3, the table's solids %9.1f, holes and windows cut %8.1f; outside the table %.3f; bounding box %s" % (
            nm, s.volume, u.volume, u.volume - s.volume, outside, "the same" if same_box else "DIFFERENT"))
        good = good and outside < 1e-3 and same_box
    rest = Q._union(bd, Q.parts(E, "screw", "unit", "proud") + plug_envelopes()[0])
    whole = tray + frame + rest
    rows = face_rows(E + plug_envelopes()[0])
    worst_d = 0.0
    for r in rows:
        f = r["foot"]; x0, x1, y0, y1 = f[2] - Q.PLACE_Y, f[3] - Q.PLACE_Y, f[0] - Q.PLACE_X, f[1] - Q.PLACE_X
        col = Q._box(bd, x0, x1, y0, y1, -1.0, 80.0) & whole
        z = col.bounding_box().max.Z
        d = abs(Q.BOND + Q.PLATE_T + z - r["depth"]); worst_d = max(worst_d, d)
        out.append("   %-15s the built set's deepest point over it %6.2f from the ceiling, section B's %6.2f%s" % ("M3r2." + r["ref"], Q.BOND + Q.PLATE_T + z, r["depth"], "" if d < 1e-3 else "  DIFFERENT"))
    good = good and worst_d < 1e-3
    # 2. in place
    out.append("2. IN PLACE: intersection volumes in mm3, every one must be 0.000")
    parts = [("tray", tray), ("frame", frame)]
    unit = bd.Box(*Q.UNIT).moved(bd.Location(bd.Vector(0, 0, Q.Z_UB + Q.UNIT[2] / 2)))
    checks = [("the unit at its nominal place", unit)]
    for nm, j in Q.JACKS.items():
        r = Q.admitted_radius(nm)
        sx = 1 if j["panel"] == "R" else -1
        for v in (min(j["v"]) - Q.JACK_RANGE, max(j["v"]) + Q.JACK_RANGE):
            for h in (min(j["h"]) - Q.JACK_RANGE, max(j["h"]) + Q.JACK_RANGE):
                y = -Q.UNIT[1] / 2 + v; z = Q.Z_UB + h
                cyl = bd.Cylinder(r, 59.5, rotation=(0, 90, 0)).moved(bd.Location(bd.Vector(sx * (Q.U0 + 0.5 + 59.5 / 2), y, z)))
                checks.append(("%s plug d %.1f at v %.1f h %.1f" % (nm, 2 * r, v, h), cyl))
                if nm == "USB":                                          # the overmold as a box, the class width across, the admitted height
                    box = bd.Box(59.5, Q.USBC_OVERMOLD_W, 2 * r).moved(bd.Location(bd.Vector(sx * (Q.U0 + 0.5 + 59.5 / 2), y, z)))
                    checks.append(("USB overmold %.2f x %.1f at v %.1f h %.1f" % (Q.USBC_OVERMOLD_W, 2 * r, v, h), box))
    for sx in (-1, 1):
        knob = bd.Cylinder(Q.KNOB_D / 2 + Q.FINGER, Q.KNOB_H + 20.0).moved(bd.Location(bd.Vector(sx * Q.KNOB_X, Q.KNOB_Y, Q.Z_UT + (Q.KNOB_H + 20.0) / 2)))
        checks.append(("knob at x %+.1f with %.0f mm finger room, to %.0f above its top" % (sx * Q.KNOB_X, Q.FINGER, Q.KNOB_H + 20.0), knob))
    # controls that MUST intersect, so a check that cannot fail is seen: the unit 1.0 higher (into the frame) and the RF plug 1.0 fatter
    j = Q.JACKS["RF"]; r = Q.admitted_radius("RF") + 1.0
    controls = [("CONTROL: the unit 1.0 higher, into the frame", bd.Box(*Q.UNIT).moved(bd.Location(bd.Vector(0, 0, Q.Z_UB + 1.0 + Q.UNIT[2] / 2)))),
                ("CONTROL: the RF plug 1.0 fatter at its lowest", bd.Cylinder(r, 59.5, rotation=(0, 90, 0)).moved(bd.Location(bd.Vector(
                    Q.U0 + 0.5 + 59.5 / 2, -Q.UNIT[1] / 2 + min(j["v"]) - Q.JACK_RANGE, Q.Z_UB + min(j["h"]) - Q.JACK_RANGE))))]
    worst, broke = 0.0, False
    for label, solid in checks + controls:
        vols = [(p & solid).volume for pn, p in parts]                  # an exception here fails the run: no silent zero
        if label.startswith("CONTROL"):
            broke = broke or sum(vols) <= 1e-3
        else:
            worst = max([worst] + vols)
        out.append("   %-58s tray %.3f  frame %.3f%s" % (label[:58], vols[0], vols[1], ("  (must be > 0)" if label.startswith("CONTROL") else "")))
    good = good and worst < 1e-3 and not broke
    # 3. the way in, position by position
    out.append("3. THE WAY IN, position by position (every %.1f from %.0f outside to the place): the largest intersection and the least distance" % (STEP, SWEEP))
    n = int(round(SWEEP / STEP))
    big = Q._union(bd, unit_at_its_largest(E))
    inter, dist = 0.0, None
    for k in range(n + 1):
        m = big.moved(bd.Location(bd.Vector(0, 0, k * STEP)))
        inter = max(inter, (tray & m).volume)
        d = tray.distance_to(m)
        dist = d if dist is None else min(dist, d)
    out.append("   the unit at its largest into the tray, %d positions: intersection %.3f mm3, least distance %.2f (section E: %.2f, on boxes)" % (
        n + 1, inter, dist, judge(fitting(E)[0][1])[1]["clearance"]))
    good = good and inter < 1e-3 and dist >= MIN_INSERT - 1e-6
    proud = Q._union(bd, [e for e in unit_at_its_largest(E, top_at=Q.Z_UT) if e["part"] == "proud"])
    inter2, dist2 = 0.0, None
    for k in range(n + 1):
        m = frame.moved(bd.Location(bd.Vector(0, 0, k * STEP)))
        inter2 = max(inter2, (proud & m).volume, (tray & m).volume, (unit & m).volume)
        d = proud.distance_to(m)
        dist2 = d if dist2 is None else min(dist2, d)
    free2 = min(r["clearance"] for r in fitting(E)[1][1] if r["part"] == "proud")
    out.append("   the frame over the unit, %d positions: intersection with the tray, the unit and what stands proud %.3f mm3, least distance to what" % (n + 1, inter2))
    out.append("   stands proud %.2f (section E: %.2f, on boxes)" % (dist2, free2))
    good = good and inter2 < 1e-3 and dist2 >= MIN_INSERT - 1e-6
    E1, P1 = pass1_elements()
    t1 = Q._union(bd, Q.parts(E1, "tray"))
    u1 = Q._union(bd, unit_at_its_largest(E1, lower=P1["g_b"], grow=False))
    inter1 = max((t1 & u1.moved(bd.Location(bd.Vector(-k * STEP, 0, 0)))).volume for k in range(int(round(200.0 / STEP)) + 1))
    out.append("   CONTROL: the first pass's tray and way in, %d positions: intersection %.3f mm3  (must be > 0)" % (int(round(200.0 / STEP)) + 1, inter1))
    good = good and inter1 > 1e-3
    vt, vf = tray.volume * PC["density"] / 1000 / 1000, frame.volume * PC["density"] / 1000 / 1000
    out.append("   masses: tray %.4f kg, frame %.4f kg (MASSES %.4f, %.4f)" % (vt, vf, MASSES["tray"], MASSES["frame"]))
    assert abs(vt - MASSES["tray"]) < 0.05 * MASSES["tray"] and abs(vf - MASSES["frame"]) < 0.10 * MASSES["frame"], "MASSES are stale"
    out.append("   RESULT: %s" % ("PASS: the table is what was built, nothing intersects in place or on the way in, and every control fails as it must" if good
                                  else "FAIL"))
    return "\n".join(out) + "\n", good


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    txt, ok = report()
    if "--solids" in sys.argv:
        s, ok2 = solids_check(); txt += s; ok = ok and ok2
    sys.stdout.write(txt)
    if args:
        open(args[0], "w", encoding="utf-8").write(txt)
    sys.exit(0 if ok else 1)
