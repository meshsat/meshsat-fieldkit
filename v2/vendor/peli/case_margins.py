#!/usr/bin/env python3
"""MESHSAT-1357 case margins: every case-dependent margin of the V2 kit in the Peli 1450, computed at Peli's own figures, with a
worst case (linear sum) and a root-sum-square (each bound taken as three sigma) over the published and the stated allowances.

Stdlib only, sub-second, runner-safe. Every Peli number below was read in this session from the files named beside it:
  STEP  = v2/vendor/peli/1450/1451-931-bottom.STEP, -top.STEP, 1450-panel-frame.STEP (unit INCH, x 25.4; faces by entity #id),
          read with v2/vendor/peli/step_faces.py (face type, plane normal, vertex box); readings in v2/vendor/peli/1450/*.faces.txt.
  DXF   = v2/vendor/peli/1450/1451-931-customer-drawing.dxf (sheet at 1:3, $DIMLFAC 3.0), section B-B hatch #7866 and the
          dimension entities _D_2.._D_8, read with v2/vendor/peli/dxf_read.py.
  SHEET = Peli 1450 panel frame instruction sheet 1453-314-000 rev A (v2/vendor/peli/1450/1450_pf.pdf, from
          media.pelican.com/cad/protector-panel-frames/1450/1450_pf.pdf, fetched 26 Sep 2026, sha256 first 16 hex 4681c0525a3cf605),
          tolerance block: one-decimal mm +-0.76, two-decimal mm +-0.25.
  INST  = Peli panel frame mounting instructions (v2/vendor/peli/panel-frame-inst.pdf, from
          business.pelican.com/storage/docs/cad-downloads/panel-frame-inst.pdf, fetched 26 Sep 2026, sha256 first 16 hex 797a2ed6f9809d0b).
  WEB   = pelican.com 1450 product page, Wayback capture 2026-03-29 04:10:54 UTC (the live page answered HTTP 403 on 26 Sep 2026).
Design numbers come from v2/ecad/tools/panel1450.py and the generators (file:line in the comments).
This script's C1 rows put the frame on Peli's rib seat (face top 105.10), which frame_seat.py shows is not a defined height;
the arrangement taken (C1 on the setting legs of C6, face top 106.52) and its margins, the connector plate and the arrestors'
RF entry plates on the end walls among them, are computed in frame_seat.py. The M7 to M9 rows here are the tree's Amphenol
132170 couplers as designed at 29f00554; this issue retires them for the ruled arrestors (frame_seat.py part F)."""
import math

# ---------------------------------------------------------------- Peli geometry (case frame: X long axis, Y to the back wall, Z from the cavity floor)
TAN = 0.0349 / 0.9994                     # STEP wall normals (0.9994, 0.0349): a 2.0 degree draft on every inner wall
HX0, HY0 = 186.97, 129.82                 # STEP planes #1193/#1922 and #172/#1851 extended to Z 0 (loc x 186.97, z 129.82)
FIL_R, FIL_T = 15.88, 15.32               # STEP floor fillet cylinders #355/#1295/#1211/#2244 r 0.625 in; tangent to the wall at Z 15.32
FLAT_X, FLAT_Y = 171.64, 114.49           # STEP floor plane #1321: the flat floor ends at the fillet tangents
SHOULDER, RIM = 101.04, 108.97            # STEP #776 (up-facing ledge, 0.51 wide) and #1637 (rim face); DXF _D_7 = 108.97
RIMZ_X, RIMZ_Y = 191.01, 133.86           # STEP #850/#1324: the rim zone's inner faces at the shoulder (191.29 / 134.14 at the rim)
RIB_TOP, RIB_R0, RIB_HA = 84.58, 0.76, 0.0218   # STEP cones r 0.03 in at Y 3.33 in, half-angle 0.0218 rad, down to Z 26.42
RIBS_END_Y = (0.0, 76.2, -76.2)           # STEP #957/#1035, #609/#1356 etc. at X +-189.93
RIBS_LONG_X = (0.0, 76.2, -76.2, 152.4, -152.4)  # one long wall carries X 0 as well (STEP #229/#950), the other only +-76.2, +-152.4
WALL_T = 195.38 - 190.04                  # DXF B-B hatch #7866 at Z 88: inner 190.04, outer 195.38 (end wall, Y 0 section)
OUT_FLANGE_Z = 97.91                      # DXF #7866: the outer rim flange starts at Z 97.9 (arc c 198.21, 97.82 r 2.48)
OUT_FILLET_TOP = 15.14                    # DXF #7866: outer bottom arc r 21.21 about (171.64, 15.88) meets the flat outer wall at Z 15.14
NUB = dict(y=(0.0, 79.0, -79.0), z=92.4, hz=4.47, hy=3.05)   # DXF end view: ellipses centred Y 0, +-79.0, Z 92.4, semi-axes 4.47 x 3.05
LID_STEP, LID_WEB = 45.47, 44.45          # STEP top #736 (and DXF _D_6 45.47); WEB lid depth 1.75 in
LID_OPEN_X = 186.94                       # STEP top #410/#540 at the parting plane; flat ceiling to X +-173.08 (#736)
LID_CEIL_FLAT_X = 173.08
WEB_INT = (372.4, 260.1)                  # WEB interior 14.66 x 10.24 in
# the 1450PF frame (STEP, frame z from -8.76 to 8.76)
FH = 17.52; FH_SHEET = 17.5               # STEP #1 and #5527; SHEET .69 in [17.5]
F_RING_UNDER = 8.76 - 0.63                # the ring's underside (#1703) is 8.13 above the frame bottom
F_OUT_BOT, F_OUT_0 = (189.18, 131.27), (189.48, 131.57)      # #3683/#7251 at z -8.76, and at z 0
F_FLANGE = (184.35, 126.44)               # #3095/#3162, the top flange above the gasket step (z 5.46)
F_STEP = 8.76 + 5.46                      # the gasket step is 14.22 above the frame bottom (3.30 under the top)
F_SKIRT_IN = (183.34, 125.42); F_WINDOW = (174.83, 116.91)   # #4475/#3645 and #1928/#1818
LETTERING = 9.27 - 8.76                   # "1450 FRONT" raised 0.51 on the top face (64 small faces z 8.76..9.27)
T_PELI = 0.76                             # SHEET tolerance, one-decimal mm

# ---------------------------------------------------------------- design numbers (v2/ecad/tools/panel1450.py unless stated)
FACE_TOP_Z = 101.4                        # panel1450.py:26
PLATE = (365.5, 249.5, 3.0)               # panel1450.py:16
B_TOP_Z = 49.5                            # panel1450.py:23
XEN_H = 28.66                             # panel1450.py:44
HEATSINK = 21.0                           # panel1450.py:36
SMA_Z = 88.0                              # panel1450.py:116
B_OUT = (165.0, 100.0)                    # panel1450.py:22
A_EDGE_X = 120.0                          # gen_pcb_a.py:16-17 (240 long from X -120)
E_STRIP = (-149.0, 118.0, -113.0, -45.0)  # gen_pcb_e.py:15
RODS = (110.5, 73.0)                      # gen_pcb_a.py:18, gen_pcb_b.py:22
VHB, LAM = 1.1, 1.6                       # ASSEMBLY.md:47 (VHB 5952 pads under the strip; 3M 1.1 +-10 %); JLC +-10 % on 1.6

# hardware from its maker's drawing
SMA_WASHER_R, SMA_NUT_AC_R = 10.20 / 2, 8.0 / math.cos(math.radians(30)) / 2      # Amphenol 132170: lock washer 10.20, 8 hex nut
SMA_HEX_AC_R, SMA_ORING_R = 9.5 / math.cos(math.radians(30)) / 2, (6.5 + 2 * 1.0) / 2   # 9.5 hex flange; NBR O-ring 6.5 x 1.0 (ASSEMBLY)
SMA_PANEL_MAX = 6.5                       # Amphenol 132170 note 1

MIN_MECH, MIN_FACE = 1.0, 2.0             # the stated minimums: 1.0 mm rigid-to-rigid (above T_PELI); 2.0 mm the C gate (z_budget.py:16)

def hx(z): return HX0 + TAN * z            # inner half-length at height z (above the fillet tangent)
def hy(z): return HY0 + TAN * z

def rib(z):
    """(protrusion from the wall, half-width on the wall) of a Peli inner rib at height z (26.42 <= z <= 84.58)."""
    dz = RIB_TOP - z; r = RIB_R0 + dz * math.tan(RIB_HA); d = TAN * dz
    return r - d, math.sqrt(max(0.0, r * r - d * d))

def stack(label, nominal, tols):
    wc = nominal - sum(t for _, t in tols); rss = math.sqrt(sum(t * t for _, t in tols))
    return dict(label=label, nom=nominal, wc=wc, rss_low=nominal - rss, rss=rss)

def show(r, minimum):
    ok = lambda v: "MET" if v >= minimum - 1e-9 else "BELOW"
    print("  %-78s nominal %+7.2f  worst %+7.2f (%s)  RSS low %+7.2f  [min %.1f]" % (r["label"], r["nom"], r["wc"], ok(r["wc"]), r["rss_low"], minimum))

if __name__ == "__main__":
    print("== (1) case geometry read from Peli's files")
    for z in (0.0, 2.5, FIL_T, 54.5, 59.0, 88.0, SHOULDER):
        print("  inside at Z %6.2f: %7.2f x %7.2f%s" % (z, 2 * hx(z), 2 * hy(z), "  (wall planes extended; flat floor %.2f x %.2f)" % (2 * FLAT_X, 2 * FLAT_Y) if z == 0 else ""))
    z = 2.5; fx = FLAT_X + math.sqrt(FIL_R ** 2 - (FIL_R - z) ** 2); fy = FLAT_Y + math.sqrt(FIL_R ** 2 - (FIL_R - z) ** 2)
    print("  on the fillet at Z 2.50: %.2f x %.2f (32.42's '360 x 246 at the floor')" % (2 * fx, 2 * fy))
    print("  rim zone Z %.2f..%.2f: %.2f x %.2f at the shoulder, %.2f x %.2f at the rim" % (SHOULDER, RIM, 2 * RIMZ_X, 2 * RIMZ_Y, 2 * 191.29, 2 * 134.14))
    print("  lid: parting plane %.2f x %.2f, at 39.19 up %.2f x %.2f, flat ceiling %.2f x %.2f, depth STEP %.2f / WEB %.2f" % (2 * 186.94, 132.08 + 129.79, 2 * 185.58, 130.84 + 128.43, 2 * 173.08, 2 * 115.93, LID_STEP, LID_WEB))
    print("  end wall thickness at Z 88 (DXF B-B): %.2f; outer rim flange from Z %.2f" % (WALL_T, OUT_FLANGE_Z))
    for zz in (26.42, 50.0, 76.0, 84.58):
        p, w = rib(zz); print("  inner rib at Z %5.2f: %.2f proud, %.2f half-width" % (zz, p, w))

    print("\n== (2) margins")
    print(" M1 monitor body bottom against the CM5 heatsink top (floor 2.0, z_budget.py:16)")
    tol_common = [("laminate E", 0.16), ("laminate A", 0.16), ("laminate B", 0.16), ("VHB 5952 +-10 %", 0.11), ("B bow 0.75 % over 40 mm (INFERRED)", 0.30)]
    heat = B_TOP_Z + HEATSINK
    show(stack("(0) as coded: FACE_TOP_Z 101.4 (109.4 - 8), no VHB in the chain [W4]", FACE_TOP_Z - XEN_H - heat,
               tol_common + [("W4 depth spread 109.4 against 109", 0.40)]), MIN_FACE)
    f_flush = RIM - (FH - F_RING_UNDER) - 0.53   # frame top at the rim, plate under the ring with the 0.53 PORON (ASSEMBLY.md:29)
    tol_a = tol_common + [("rim Z, Peli one-decimal band applied to the case (INFERRED)", T_PELI), ("frame height, SHEET +-0.76", T_PELI)]
    show(stack("(A1) plate under the ring, frame top flush with the rim: FACE %.2f, VHB as written" % f_flush, f_flush - XEN_H - (heat + VHB), tol_a), MIN_FACE)
    f_seat_a = RIB_TOP + FH - (FH - F_RING_UNDER) - 0.53
    show(stack("(A2) plate under the ring, frame seated on the ribs (INST step 3): FACE %.2f" % f_seat_a, f_seat_a - XEN_H - (heat + VHB), tol_a), MIN_FACE)
    f_b = RIB_TOP + FH + 0.0 + PLATE[2]
    tol_b = tol_common + [("rib top Z, Peli one-decimal band applied to the case (INFERRED)", T_PELI), ("frame height, SHEET +-0.76", T_PELI), ("plate 3.0, EN 485 class (INFERRED)", 0.13)]
    show(stack("(B) C1: plate ON the frame over the o-ring (INST step 4): FACE %.2f, VHB as written" % f_b, f_b - XEN_H - (heat + VHB), tol_b), MIN_FACE)
    show(stack("(B) C1, VHB not lifting the stack (W4 F5 option b)", f_b - XEN_H - heat, tol_b), MIN_FACE)
    b_low = RIB_TOP - T_PELI + FH - T_PELI + PLATE[2] - 0.13
    b_high = RIB_TOP + T_PELI + FH + T_PELI + PLATE[2] + 0.13
    print("  C1 face top range at Peli's figures: %.2f .. %.2f (plate underside %.2f .. %.2f)" % (b_low, b_high, b_low - 3.0 + 0.13, b_high - 3.0 - 0.13))

    print(" M2 plate against the lid's wall where the lid overhangs the rim zone (plate top <= rim - 1.0)")
    rim_low = RIM - T_PELI
    print("  C1 full-thickness edge: %.2f;  with the lettering under it (no relief): %.2f;  with a 2.0 mm top rebate on the edge band: %.2f" % (
        rim_low - b_high, rim_low - (b_high + LETTERING), rim_low - (b_high - 2.0)))
    print("  generic PF detail (1400/1450/1520 sheets, 'do not scale'), frame top about 2.8 below the rim (INFERRED): full edge %.2f, rebated edge %.2f" % (
        rim_low - (RIM - 2.8 + T_PELI + PLATE[2] + 0.13), rim_low - (RIM - 2.8 + T_PELI + PLATE[2] + 0.13 - 2.0)))

    print(" M3 lid space above the face (lid ceiling = rim + lid depth)")
    print("  as coded: %.2f nominal (ASSEMBLY.md:66 states 46.5)" % (RIM + LID_STEP - FACE_TOP_Z))
    print("  C1: nominal %.2f; worst (WEB lid %.2f, rim -0.76, face high %.2f) %.2f; QMX tray 28.0 leaves %.2f for the parts under it" % (
        RIM + LID_STEP - f_b, LID_WEB, b_high, rim_low + LID_WEB - b_high, rim_low + LID_WEB - b_high - 28.0 - MIN_MECH))
    tray_e = 172.5
    print("  QMX tray east edge %.1f against the lid's flat ceiling edge %.2f: %.2f; shifted 1.5 west: %.2f (worst -0.38: %.2f)" % (
        tray_e, LID_CEIL_FLAT_X, LID_CEIL_FLAT_X - tray_e, LID_CEIL_FLAT_X - tray_e + 1.5, LID_CEIL_FLAT_X - tray_e + 1.5 - T_PELI / 2))

    print(" M4 pack block (4S3P 18650, 3 x 2, 56.65 x 133.5 x 38.1 wrapped, A06) in the east pocket")
    D, WRAP, BASE = 18.55, 0.5, 1.4
    r = D / 2 + WRAP
    for tag, inset in (("Peli STEP/DXF", 0.0), ("case -0.38 per wall (INFERRED)", T_PELI / 2), ("WEB interior 372.4 applied at the fillet (worst)", (2 * hx(FIL_T) - WEB_INT[0]) / 2)):
        fcx, fcz = FLAT_X - inset, FIL_R
        arc = [(fcx + FIL_R * math.sin(math.radians(t / 10.0)), FIL_R - FIL_R * math.cos(math.radians(t / 10.0))) for t in range(0, 901)]
        arc = [q for q in arc if q[1] >= BASE]                     # the fillet only stands above the pack's base plane beyond this x
        def corner_gap(west):
            cx = west + WRAP + 2 * D + D / 2; cz = BASE + WRAP + D / 2
            return min(math.hypot(ax - cx, az - cz) for ax, az in arc) - r, cx
        west = A_EDGE_X + 2.0
        gap, cx = corner_gap(west)
        wall_gap = hx(BASE + WRAP + D * 2) - inset - (cx + r)
        w_max = west
        while corner_gap(w_max + 0.05)[0] >= MIN_MECH: w_max += 0.05
        print("  %-48s west face %.2f (%.1f from A's edge), east face %.2f: corner to the fillet %.2f, east face to the wall %.2f; the block can move %.2f further east at 1.0 mm" % (
            tag, west, west - A_EDGE_X, cx + r, gap, wall_gap, w_max - west))
    print("  A06 reported X spare 1.35 against a pocket bound X 178 (appendix 32.62), which is not Peli's wall")
    print("  length: flat floor %.2f against block + board P 205.5: %.2f (worst %.2f)" % (2 * FLAT_Y, 2 * FLAT_Y - 205.5, 2 * FLAT_Y - 205.5 - T_PELI))

    print(" M5 lift-out through the frame window (B 330 x 200)")
    print("  per side %.2f / %.2f; frame -0.76: %.2f / %.2f" % (F_WINDOW[0] - B_OUT[0], F_WINDOW[1] - B_OUT[1], F_WINDOW[0] - T_PELI / 2 - B_OUT[0], F_WINDOW[1] - T_PELI / 2 - B_OUT[1]))

    print(" M6 face plate fit")
    print("  as coded (under the ring, in the skirt %.2f x %.2f): %.2f / %.2f per side; frame -0.76: %.2f / %.2f" % (
        2 * F_SKIRT_IN[0], 2 * F_SKIRT_IN[1], F_SKIRT_IN[0] - PLATE[0] / 2, F_SKIRT_IN[1] - PLATE[1] / 2,
        F_SKIRT_IN[0] - T_PELI / 2 - PLATE[0] / 2, F_SKIRT_IN[1] - T_PELI / 2 - PLATE[1] / 2))
    head = 2.4
    print("  as coded, Peli's frame screw heads on the skirt's inside at Y +-%.2f (No. 6 pan head about %.1f tall, INFERRED): plate edge overlap %.2f" % (
        F_SKIRT_IN[1], head, (PLATE[1] / 2) - (F_SKIRT_IN[1] - head)))
    for pw, pl in ((379.0, 264.0), (378.0, 263.0), (377.2, 263.0)):
        zb = b_low - 3.0 + 0.13
        cx_, cy_ = hx(zb) - pw / 2, hy(zb) - pl / 2
        print("  C1 plate %.1f x %.1f, underside as low as Z %.2f: %.2f / %.2f per side; case -0.38: %.2f / %.2f" % (
            pw, pl, zb, cx_, cy_, cx_ - T_PELI / 2, cy_ - T_PELI / 2))
    # corner of the C1 plate against the drafted vertical corner R 15.88 at the plate's lowest Z
    pw, pl, rp = 377.2, 263.0, 16.0
    zb = b_low - 3.0 + 0.13; ccx, ccy = hx(zb) - FIL_R, hy(zb) - FIL_R
    pcx, pcy = pw / 2 - rp, pl / 2 - rp
    g = min(FIL_R - math.hypot(pcx + rp * math.cos(a) - ccx, pcy + rp * math.sin(a) - ccy)
            for a in [math.radians(t / 10.0) for t in range(0, 901)] if pcx + rp * math.cos(a) > ccx and pcy + rp * math.sin(a) > ccy)
    print("  C1 plate %.1f x %.1f R16 corner against the case corner R15.88 at Z %.2f: %.2f (case -0.38: %.2f)" % (pw, pl, zb, g, g - T_PELI / 2))
    print("  o-ring channel (flange to wall at the step): X %.2f, Y %.2f; the %.1f x %.1f plate edge covers %.2f / %.2f of it" % (
        hx(RIB_TOP + F_STEP) - F_FLANGE[0], hy(RIB_TOP + F_STEP) - F_FLANGE[1], pw, pl, pw / 2 - F_FLANGE[0], pl / 2 - F_FLANGE[1]))

    print(" M7 wall jacks (inner lock washer r %.2f, outer hex r %.2f, O-ring r %.2f) against the frame skirt" % (SMA_WASHER_R, SMA_HEX_AC_R, SMA_ORING_R))
    for tag, skirt in (("A1 frame top at the rim", RIM - FH), ("as coded re-derived (plate 101.4 under the ring + PORON)", FACE_TOP_Z + 0.53 + (FH - F_RING_UNDER) - FH),
                       ("C1 frame seated on the ribs", RIB_TOP)):
        print("  %-58s skirt bottom %.2f: jack Z 88 -> %.2f; jack Z 76 -> %.2f (worst -0.76: %.2f)" % (
            tag, skirt, skirt - (SMA_Z + SMA_WASHER_R), skirt - (76.0 + SMA_WASHER_R), skirt - T_PELI - (76.0 + SMA_WASHER_R)))
    print(" M8 jacks at |Y| 72 against the inner ribs at Y +-76.2 and the outer features at Y +-79.0")
    for jz, jy in ((88.0, 72.0), (76.0, 72.0), (76.0, 68.0), (88.0, 68.0)):
        zr = min(jz, RIB_TOP); p, w = rib(max(zr, 26.42))
        inner = (76.2 - w) - (jy + SMA_WASHER_R)
        outer_y = (NUB["y"][1] - NUB["hy"]) - (jy + SMA_HEX_AC_R); outer_z = (NUB["z"] - NUB["hz"]) - (jz + SMA_HEX_AC_R)
        print("  jack Y %.0f Z %.0f: inner washer to rib %+.2f (rib -0.38: %+.2f); outer hex to feature: Y %+.2f, Z %+.2f -> %s" % (
            jy, jz, inner, inner - T_PELI / 2, outer_y, outer_z, "clear" if (outer_y > 0 or outer_z > 0) else "OVERLAP"))
    print(" M9 coupler clamp stack: wall %.2f + O-ring 0.75 (INFERRED compressed) = %.2f against %.1f: %.2f; wall +0.76: %.2f" % (
        WALL_T, WALL_T + 0.75, SMA_PANEL_MAX, SMA_PANEL_MAX - WALL_T - 0.75, SMA_PANEL_MAX - WALL_T - 0.75 - T_PELI))
    print(" M10 connector plate (case_wall_cutouts.py:25-29, outside the back wall)")
    p, w = rib(54.0)
    print("  as coded: bottom Z 13.0 against the outer fillet end %.2f: %.2f; west M4 column X -79 washer r 4.5 against the rib at -76.2 (half-width %.2f at Z 54): %.2f" % (
        OUT_FILLET_TOP, 13.0 - OUT_FILLET_TOP, w, (79.0 - 4.5) - (76.2 + w)))
    print("  under C1: top row Z 82 + 4.5 against the skirt %.2f: %.2f; USB body r 14.5 (29 mm wall hole) at Z 74: %.2f" % (RIB_TOP, RIB_TOP - 86.5, RIB_TOP - 88.5))
    print("  C3 as chosen (the plate at X -57..57 with the full ruled set): frame_seat.py part E")
    print(" M11 floor items against the fillet tangents (flat floor %.2f x %.2f)" % (2 * FLAT_X, 2 * FLAT_Y))
    print("  dock strip south edge Y %.1f: %.2f (case -0.38: %.2f); west end X %.1f: %.2f" % (E_STRIP[2], FLAT_Y + E_STRIP[2], FLAT_Y + E_STRIP[2] - T_PELI / 2, E_STRIP[0], FLAT_X + E_STRIP[0]))
    print("  rods at (+-%.1f, +-%.1f): %.2f / %.2f" % (RODS[0], RODS[1], FLAT_X - RODS[0], FLAT_Y - RODS[1]))
    print(" M12 east-wall lead band between B's edge X 165 and the wall: Z 50 %.2f, Z 76 %.2f (case -0.38: %.2f)" % (hx(50) - 165, hx(76) - 165, hx(50) - 165 - T_PELI / 2))
    print(" M13 frame in the case (Peli's own interface): bottom edge %.2f / %.2f per side, at z 0 %.2f / %.2f; RSS of +-0.38 frame and +-0.38 case: %.2f" % (
        hx(RIB_TOP) - F_OUT_BOT[0], hy(RIB_TOP) - F_OUT_BOT[1], hx(RIB_TOP + 8.76) - F_OUT_0[0], hy(RIB_TOP + 8.76) - F_OUT_0[1], math.sqrt(2) * T_PELI / 2))
    print("  rib reach against the frame's bottom outer edge: end walls %+.2f, long walls %+.2f (positive = the rib catches the frame)" % (
        F_OUT_BOT[0] - (hx(RIB_TOP) - RIB_R0), F_OUT_BOT[1] - (hy(RIB_TOP) - RIB_R0)))

if __name__ == "__main__":
    def rr_area(w, h, r): return w * h - (4 - math.pi) * r * r
    old = rr_area(365.5, 249.5, 12.0) * 3.0
    new = rr_area(377.2, 263.0, 16.0) * 3.0 - (rr_area(377.2, 263.0, 16.0) - 368.0 * 253.0) * 2.0 - 44.0 * 9.0 * 0.8
    print(" C1 plate blank volume %.0f -> %.0f mm3: %+.1f g at 2.70 g/cm3 (cut-outs equal in both)" % (old, new, (new - old) * 2.70e-3))
    fs = RIB_TOP + F_RING_UNDER - 4.85 + (8.76 - F_RING_UNDER) * 0   # frame mid-plane is 8.76 above its bottom
    print(" frame mounting screws under C1 at Z %.2f; plan distance from the backer edge (Y 114) to the skirt face (Y %.2f): %.2f" % (
        RIB_TOP + 8.76 - 4.85, F_SKIRT_IN[1], F_SKIRT_IN[1] - 114.0))
    print(" 6-32 x 1/2 in: bore %.2f - insert 6.3 = %.2f empty; screw below the plate %.2f; engagement %.2f" % (
        FH - F_RING_UNDER, FH - F_RING_UNDER - 6.3, 12.7 - 3.0, min(6.3, 12.7 - 3.0 - (FH - F_RING_UNDER - 6.3))))
