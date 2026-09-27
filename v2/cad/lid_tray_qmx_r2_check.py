#!/usr/bin/env python3
"""The QMX lid tray r2, checked (MESHSAT-1357, 27 Sep 2026, S-63, EQ-24; worktree fnd/w5tray). Reads v2/cad/lid_tray_qmx_r2.py (its
numbers) and v2/vendor/peli/1450/frame_seat.out (the room between the face and the lid ceiling that M3 and M19 were computed with) and
prints, as a record for the r2 release and its placement sheet:

  A. every jack's plug: the largest plug body the tray admits about each jack's axis at the worst of its scaled place (the tray is open
     across each end panel above a 1.5 mm sill), and the leads' room to the lid's flat ceiling edge for their bend radius;
  B. the face room: the r2 stack from the lid ceiling (bond, lid plate, floor, pad gap, unit, ledge) against frame_seat.out's M3 room,
     at the ledges, over the unit's top face (the buttons) and at the knob tips, and the knob height at which the knobs would reach the
     1.0 minimum at the worst; M19 unchanged;
  C. the pads: PORON 4701-30 compression over the tolerance corners;
  D. retention: the load a peak acceleration puts on each link of each load path (unit to ledges to walls to screws to the lid plate
     to the bond; unit to the end block and keeper; unit to the walls sideways), each link's capacity in g on the makers' typical figures,
     and TEST-PLAN E1's drop as a peak-acceleration bound over the stopping distance, which no held document states.

Stdlib only; runs anywhere. With --solids (needs build123d, v2/cad/requirements-cad.lock) it also builds the tray and the keeper and
proves by boolean intersection, on the solids themselves, that the unit, every admitted plug envelope at every corner of its jack's
scaled place, and each knob's envelope with its finger room touch neither part. Usage: lid_tray_qmx_r2_check.py [--solids] [out file]"""
import os, sys, math, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lid_tray_qmx_r2 as Q

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
# Prusament PC Blend, technical data sheet v1.1 of 16 Feb 2022 (v2/vendor/materials/prusament-pc-blend-tds-v1.1-2022-02-16.pdf): typical
# values of specimens printed at 100 % infill, 0.20 mm layers; the design takes each typical value less its stated spread
PC = dict(interlayer=21.0 - 2.0, flexural=88.0 - 1.0, tensile=63.0 - 1.0, density=1.22, hdt045=113.0)
AL5052_SHEAR = 100.0                  # MPa, the lid plate's thread shear used for stripping (INFERRED class figure; no 5052 sheet is held)
DP8005_TPEEL = 9 * 4.448 / 25.4       # N/mm: 9 lb/in T-peel on 0.5 mm HDPE (3m-scotch-weld-dp8005.pdf page 2); the only strength the sheet gives
DROP_H = 1.22                         # m, TEST-PLAN E1 (MIL-STD-810H 516.8 Procedure IV, Table 516.8-IX first row)
G0 = 9.80665
MASSES = dict(tray=0.0490, keeper=0.0013, plate=0.0520)   # kg, from the solids (lid_tray_qmx_r2.py prints them; --solids re-checks)


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


def peak_g(s_mm):
    """Half-sine deceleration from the drop's impact velocity over a stopping distance s: a = pi v^2 / (4 s), v^2 = 2 g h, so a/g = pi h / (2 s)."""
    return math.pi * DROP_H * 1000.0 / (2.0 * s_mm)


def wall_section():
    """One gusset pitch of a long wall at its root (the floor joint, an interlayer plane): the wall strip and the gusset's foot.
    Returns area, centroid distance from the inner face, second moment about the centroid (mm2, mm, mm4) and the pitch."""
    xs = sorted(Q.GUSSET["x"]); pitch = min(b - a for a, b in zip(xs, xs[1:]))
    parts = [(pitch * Q.WALL, Q.WALL / 2, pitch * Q.WALL ** 3 / 12.0),
             (Q.GUSSET["t"] * Q.GUSSET["depth"], Q.WALL + Q.GUSSET["depth"] / 2, Q.GUSSET["t"] * Q.GUSSET["depth"] ** 3 / 12.0)]
    A = sum(a for a, _, _ in parts); c = sum(a * y for a, y, _ in parts) / A
    I = sum(i + a * (y - c) ** 2 for a, y, i in parts)
    return A, c, I, pitch


def report():
    R = frame_seat_rows()
    L = []
    L.append("QMX lid tray r2: the fit, the face room and the retention, from v2/cad/lid_tray_qmx_r2.py and frame_seat.out (%s)." % (
        "M3 nominal %+.2f, worst %+.2f for a tray %.2f from the ceiling" % (R["M3"]["nom"], R["M3"]["worst"], m3_tray(R))))
    L.append("Prototype design: nothing made, printed or fitted. SCALED and INFERRED inputs are marked; the makers' figures are named.")
    L.append("")
    # ---- A
    L.append("A. JACKS AND PLUGS (tray open across both end panels above the sill; sill and keeper top %.1f above the unit's bottom face)" % Q.SILL_H)
    L.append("   jack    panel  v from knob edge  height (scaled)   admitted plug body   who and what")
    worst_r = {}
    for nm, j in Q.JACKS.items():
        r = Q.admitted_radius(nm); worst_r[nm] = r
        L.append("   %-7s %-5s  %5.1f .. %5.1f     %5.1f .. %5.1f     d %5.1f (r %4.1f)    %s" % (
            nm, j["panel"], min(j["v"]) - Q.JACK_RANGE, max(j["v"]) + Q.JACK_RANGE, min(j["h"]) - Q.JACK_RANGE, max(j["h"]) + Q.JACK_RANGE,
            2 * r, r, j["use"]))
    L.append("   USB-C: the admitted envelope is a height, %.1f above and below the axis; an overmold %.2f wide (a class, INFERRED) is the other" % (
        worst_r["USB"], Q.USBC_OVERMOLD_W))
    L.append("   bound, and the unit's own panel sets it against the PTT plug: PTT to USB centres %.1f .. %.1f apart, so a PTT plug beside a %.2f" % (
        min(Q.JACKS["USB"]["v"]) - max(Q.JACKS["PTT"]["v"]), max(Q.JACKS["USB"]["v"]) - min(Q.JACKS["PTT"]["v"]), Q.USBC_OVERMOLD_W))
    L.append("   overmold may be %.1f across at most (the unit's panel, not the tray). Nothing of the tray lies within an end panel's outline above" % (
        2 * (min(Q.JACKS["USB"]["v"]) - max(Q.JACKS["PTT"]["v"]) - Q.USBC_OVERMOLD_W / 2)))
    L.append("   the sill; each end's lintel lies above the unit's top face (%.1f to %.1f above the plate) and %.1f wide beyond the end face, over" % (Q.Z_UT, Q.Z_TOP, Q.LINTEL_W))
    L.append("   every plug body; beyond the end faces only the sill or keeper (top %.1f above the plate) and the lid plate lie under the plugs." % Q.Z_SILL)
    room_r = LID_FLAT_HALF_Y - (Q.PLACE_Y + Q.U0); room_l = LID_FLAT_HALF_Y - (Q.U0 - Q.PLACE_Y)
    L.append("   Leads (permanent: DC, RF, USB; the operator's Paddle, Audio and PTT plugs come out before the lid closes, the case closes sealed):")
    L.append("   right panel to the flat ceiling's edge (case Y %.2f): %.2f; the RF jumper turns at R %.1f (RG-316, the tree's figure), so its" % (
        LID_FLAT_HALF_Y, room_r, RG316_R))
    L.append("     BNC plug may reach %.1f from the panel before its cable turns; the USB-C lead, turning at R %.1f, %.1f." % (
        room_r - RG316_R - MARGIN, LEAD_R, room_r - LEAD_R - MARGIN))
    L.append("   left panel to the flat ceiling's edge (case Y %.2f): %.2f; the DC lead loops back toward the hinge at R %.1f west of the tray," % (
        -LID_FLAT_HALF_Y, room_l, LEAD_R))
    L.append("     so its plug may reach %.1f from the panel. R %.1f is the requirement on the DC and USB lead picks (not picked)." % (
        room_l - LEAD_R - MARGIN, LEAD_R))
    L.append("")
    # ---- B
    stack_top = Q.BOND + Q.PLATE_T + Q.Z_UT; stack_ledge = Q.BOND + Q.PLATE_T + Q.Z_TOP
    tray = m3_tray(R)
    room_nom, room_worst, room_wc2 = R["M3"]["nom"] + tray, R["M3"]["worst"] + tray, R["M3"]["wc2"] + tray
    L.append("B. FACE ROOM with the lid closed (frame_seat.out M3's room between the face top and the lid ceiling: %.2f nominal, %.2f at the worst," % (room_nom, room_worst))
    L.append("   %.2f at the worst with every unstated allowance taken twice, the case margins' sensitivity reading that decides MET)" % room_wc2)
    L.append("   r2 stack from the ceiling: bond %.2f + lid plate %.1f + floor %.1f + pad gap %.1f + unit %.1f = %.2f to the unit's top face; + ledge %.1f = %.2f" % (
        Q.BOND, Q.PLATE_T, Q.FLOOR, Q.G_B, Q.UNIT[2], stack_top, Q.LEDGE_T, stack_ledge))
    if abs(tray - R1_TRAY) < 1e-9:
        L.append("   (the r1 tray's %.1f counted no lid plate; its ASSEMBLY.md row names a 2 mm nut plate the M3 row left out)" % R1_TRAY)
    L.append("   key    min   nominal   worst  unstated x2")
    rows = [("M3r2a", "under the walls and ledges (the flat face, the light guides 0.2 proud)", stack_ledge, None),
            ("M3r2b", "under the unit's top face, over SW_MAIN, SW_PI, SW_TEST (cap heights TBD, C&K)", stack_top, "caps"),
            ("M3r2k", "the knob tips over the flat face (knob %.1f above the top face, INFERRED)" % Q.KNOB_H, stack_top + Q.KNOB_H, "knob")]
    for key, label, used, dep in rows:
        nom, worst, wc2 = room_nom - used, room_worst - used, room_wc2 - used
        verdict = "MET" if wc2 >= MIN_MECH else ("OPEN" if worst >= MIN_MECH else "NOT MET")
        if dep == "caps":
            verdict = "OPEN on the cap heights (MET for caps up to %.2f, %.2f at the worst)" % (wc2 - MIN_MECH, worst - MIN_MECH)
        if dep == "knob":
            verdict = "%s on the INFERRED knob; OPEN on its unstated height: MET for a knob up to %.2f (%.2f at the plain worst)" % (
                verdict, room_wc2 - stack_top - MIN_MECH, room_worst - stack_top - MIN_MECH)
        L.append("   %-6s %.2f  %+7.2f  %+7.2f  %+7.2f  %s: %s" % (key, MIN_MECH, nom, worst, wc2, label, verdict))
    L.append("   M19 (east edge at X %.1f inside the flat ceiling): unchanged, nominal %+.2f, worst %+.2f, %s" % (Q.EAST_EDGE_X, R["M19"]["nom"], R["M19"]["worst"], R["M19"]["verdict"]))
    L.append("   place: X %.1f .. %.1f (grown %.1f west of r1's 102.0 for the gussets; the lid ceiling is free there), Y %.1f .. %.1f" % (
        Q.SPAN_X[0], Q.SPAN_X[1], 102.0 - Q.SPAN_X[0], Q.SPAN_Y[0], Q.SPAN_Y[1]))
    L.append("   knobs at case (X %.1f, Y %.1f) and (X %.1f, Y %.1f), each d %.1f: west of the buttons' column (X 140.4 .. 159.6) and of the light guides (X 126.4)" % (
        Q.PLACE_X + Q.KNOB_Y, Q.PLACE_Y - Q.KNOB_X, Q.PLACE_X + Q.KNOB_Y, Q.PLACE_Y + Q.KNOB_X, Q.KNOB_D))
    L.append("")
    # ---- C
    t0, t1 = Q.PAD["t"] * (1 - Q.PAD["t_tol"]), Q.PAD["t"] * (1 + Q.PAD["t_tol"])
    gb0, gb1 = Q.Z_UB - 2 * PRINT_TOL, Q.Z_UB + 2 * PRINT_TOL          # the unit's bottom above the plate: ledge height +-0.2, unit height +-0.2
    area = 2 * Q.PAD["size"][0] * Q.PAD["size"][1]
    L.append("C. PADS (%s; standing on the plate in two floor windows %.0f x %.0f, %.0f mm2)" % (Q.PAD["material"], Q.PAD["size"][0], Q.PAD["size"][1], area))
    L.append("   compression: nominal %.2f (%.0f %%), least %.2f (%.0f %%, thin pad, unit high), most %.2f (%.0f %%, thick pad, unit low)" % (
        Q.PAD["t"] - Q.Z_UB, 100 * (Q.PAD["t"] - Q.Z_UB) / Q.PAD["t"], t0 - gb1, 100 * (t0 - gb1) / t0, t1 - gb0, 100 * (t1 - gb0) / t1))
    L.append("   so the unit always stands on the pads, pressed up against the ledges; at 25 %% the sheet gives %.0f to %.0f kPa, %.0f to %.0f N" % (
        Q.PAD["cfd25_kpa"][0], Q.PAD["cfd25_kpa"][1], Q.PAD["cfd25_kpa"][0] * area / 1000, Q.PAD["cfd25_kpa"][1] * area / 1000))
    L.append("   (the sheet states 25 %% only: the preload at the least and most compression is not stated). Floor top %.1f: the hard stop toward the lid." % Q.FLOOR)
    L.append("")
    # ---- D
    m_u = Q.UNIT_MASS + PLUG_MASS
    m_all = m_u + sum(MASSES.values())
    w = m_u * G0
    L.append("D. RETENTION. Unit and mated plugs %.3f kg (maker's 220 g + %.0f g INFERRED): %.2f N per g. With the tray, keeper and plate %.3f kg." % (m_u, 1000 * PLUG_MASS, w, m_all))
    L.append("   Material: Prusament PC Blend (TDS v1.1): interlayer %.0f, flexural %.0f, tensile %.0f MPa taken (typical less spread); printed" % (
        PC["interlayer"], PC["flexural"], PC["tensile"]))
    L.append("   floor down, 100 percent infill, 0.20 mm layers as the sheet's specimens; walls and gussets vertical, so wall tension crosses the layers.")
    A, c, I, pitch = wall_section()
    n_pitch = 2 * Q.FACE_X / pitch
    links = []
    # out of the pocket (toward the face with the lid closed): ledges, walls, screws, the bond
    for side, ov, length in (("back", Q.LEDGE_BACK, Q.BACK_LEDGE[1] - Q.BACK_LEDGE[0]),
                             ("knob-edge", Q.LEDGE_FRONT, sum(b - a for a, b in Q.FRONT_SEGMENTS))):
        lever = (Q.CLR + EDGE_R + ov) / 2
        q = PC["flexural"] * Q.LEDGE_T ** 2 / (6 * lever)
        links.append(("out", "%s ledge, root bending (%.1f long, lever %.2f)" % (side, length, lever), 2 * q * length, "half the load on each side"))
        e = lever + c
        n = PC["interlayer"] / (1.0 / A + e * c / I)
        links.append(("out", "%s wall, tension and bending across the layers at its root (%.1f pitches)" % (side, n_pitch), 2 * n * n_pitch, "half the load on each wall"))
    engage = 5.0 - Q.Z_SILL                                             # M3 x 5 flush at the boss top: its tip 5.0 below it
    strip = math.pi * 3.0 * engage * 0.75 * AL5052_SHEAR
    links.append(("out", "M3 threads in the 2.0 lid plate, four boss screws (engagement %.1f, tip %.1f short of the bond)" % (engage, Q.PLATE_T - engage), 4 * strip, "INFERRED shear"))
    pull = math.pi / 4 * (Q.CSK["d_head"] ** 2 - Q.CSK["hole"] ** 2) * PC["tensile"]
    links.append(("out", "countersunk heads pulling through the 3.6 bosses, four", 4 * pull, ""))
    perim = 2 * (2 * Q.BASE_X + 2 * Q.BASE_Y) - (8 - 2 * math.pi) * 6.0
    links.append(("out*", "the lid plate's DP8005 bond on the lid's polypropylene: SCOPING ONLY (T-peel of 0.5 mm HDPE x perimeter %.0f)" % perim,
                  DP8005_TPEEL * perim, "no held figure bounds it"))
    # along the length: the end block and the keeper
    band = Q.SILL_H - 2 * PRINT_TOL
    links.append(("x", "bearing of the left or right panel's bottom band on the sill or keeper (%.1f x %.0f at the loose corner)" % (band, Q.UNIT[1] - 2 * EDGE_R),
                  band * (Q.UNIT[1] - 2 * EDGE_R) * PC["tensile"], ""))
    links.append(("x", "three M3 through the keeper and deck (or the end block), bearing on the printed holes over %.1f" % Q.Z_SILL,
                  3 * 3.0 * Q.Z_SILL * PC["tensile"], "friction not counted"))
    # across: a wall as a cantilever pushed outward by the unit's side (the lintels' share with the other wall not counted)
    lever_y = Q.Z_UB + Q.UNIT[2] / 2 - Q.FLOOR
    n = PC["interlayer"] * I / (c * lever_y)
    links.append(("y", "one wall pushed outward, bending across the layers at its root (resultant %.1f above it, %.1f pitches)" % (lever_y, n_pitch), n * n_pitch,
                  "lintels not counted"))
    L.append("   %-4s %-112s %8s %8s" % ("dir", "link", "N", "g"))
    known = []
    for d, label, F, note in links:
        g = F / (m_all * G0) if d == "out*" else F / w
        if d != "out*":
            known.append((g, d, label))
        L.append("   %-4s %-112s %8.0f %8.0f  %s" % (d, label[:112], F, g, note))
    gmin = min(known)
    L.append("   Governing link on the makers' typical figures: %.0f g (direction %s: %s). The bond is not bounded by any held figure: its" % (gmin[0], gmin[1], gmin[2].split(" (")[0]))
    L.append("   T-peel scoping number (%.0f g) is for a flexible strip, not a rigid 2 mm plate, and is no bound; it goes to CASE-MARGINS T8 as a" % (
        [DP8005_TPEEL * perim / (m_all * G0)][0]))
    L.append("   pull test on the case's polypropylene.")
    L.append("   E1's peak on the lid is not stated by MIL-STD-810H (it sets the drop, not a pulse). Half-sine from %.2f m over a stopping distance s:" % DROP_H)
    L.append("   " + ";  ".join("s %4.1f mm: %4.0f g" % (s, peak_g(s)) for s in (2.0, 5.0, 10.0, 20.0)))
    L.append("   The known links hold to %.0f g, which the bound passes for s >= %.1f mm and fails below: a bound that includes failure. No board," % (
        gmin[0], math.pi * DROP_H * 1000 / (2 * gmin[0])))
    L.append("   interface or purchase depends on it (the remedy, a machined 6061 tray from the same STEP or a larger bonded plate, moves no board),")
    L.append("   so the retention verdict stays OPEN, allocated to E1 with an accelerometer on the lid and to T8 for the bond. E2 (MIL-STD-810H")
    L.append("   514.8, composite wheeled vehicle): its levels are not held here; the pads' preload and E2's 'no loosened fastener' line are the check.")
    L.append("   The r1 tray it replaces held the unit by one hook-and-loop strap (no figure stated) and a 6 mm lip, in PETG (HDT 68 C).")
    return "\n".join(L) + "\n"


def solids_check():
    """Boolean checks on the built solids: the unit's box, each plug envelope (a cylinder about the jack's axis at the four corners of its
    scaled place, from 0.5 beyond the panel face to 60 mm out) and each knob with its finger room, against the tray and the keeper."""
    import build123d as bd
    tray, keeper = Q.build_tray(), Q.build_keeper()
    parts = [("tray", tray), ("keeper", keeper)]
    out = ["", "SOLIDS (build123d %s): intersection volumes in mm3, every one must be 0.000" % bd.__version__]
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
    # controls that MUST intersect, so a check that cannot fail is seen: the unit 1.0 higher (into the ledges) and the RF plug 1.0 fatter
    j = Q.JACKS["RF"]; r = Q.admitted_radius("RF") + 1.0
    controls = [("CONTROL: the unit 1.0 higher, into the ledges", bd.Box(*Q.UNIT).moved(bd.Location(bd.Vector(0, 0, Q.Z_UB + 1.0 + Q.UNIT[2] / 2)))),
                ("CONTROL: the RF plug 1.0 fatter at its lowest", bd.Cylinder(r, 59.5, rotation=(0, 90, 0)).moved(bd.Location(bd.Vector(
                    Q.U0 + 0.5 + 59.5 / 2, -Q.UNIT[1] / 2 + min(j["v"]) - Q.JACK_RANGE, Q.Z_UB + min(j["h"]) - Q.JACK_RANGE))))]
    worst, broke = 0.0, False
    for label, solid in checks + controls:
        vols = [(p & solid).volume for pn, p in parts]                  # an exception here fails the run: no silent zero
        if label.startswith("CONTROL"):
            broke = broke or sum(vols) <= 1e-3
        else:
            worst = max([worst] + vols)
        out.append("   %-58s tray %.3f  keeper %.3f%s" % (label[:58], vols[0], vols[1], ("  (must be > 0)" if label.startswith("CONTROL") else "")))
    vt, vk = tray.volume * PC["density"] / 1000 / 1000, keeper.volume * PC["density"] / 1000 / 1000
    out.append("   masses: tray %.4f kg, keeper %.4f kg (MASSES %.4f, %.4f)" % (vt, vk, MASSES["tray"], MASSES["keeper"]))
    assert abs(vt - MASSES["tray"]) < 0.05 * MASSES["tray"] and abs(vk - MASSES["keeper"]) < 0.10 * MASSES["keeper"], "MASSES are stale"
    ok = worst < 1e-3 and not broke
    out.append("   RESULT: %s" % ("PASS: no intersection, and both controls intersect" if ok else "FAIL: largest intersection %.3f mm3, controls %s" % (
        worst, "broken" if broke else "intersect")))
    return "\n".join(out) + "\n", ok


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    txt = report()
    ok = True
    if "--solids" in sys.argv:
        s, ok = solids_check(); txt += s
    sys.stdout.write(txt)
    if args:
        open(args[0], "w", encoding="utf-8").write(txt)
    sys.exit(0 if ok else 1)
