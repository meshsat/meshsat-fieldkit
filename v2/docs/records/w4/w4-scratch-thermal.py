#!/usr/bin/env python3
"""W4 scratch (MESHSAT-1357, round 2): a lumped, steady-state estimate of the sealed Peli 1450's conductance from
inside air to ambient, with LOW and HIGH bounds, compared with appendix 32.53; the inside-air rise per power state
(32.53's watts and adjudication A05's PROVISIONAL battery-side watts); the solar load split between the aluminium,
the monitor glass and the e-paper lens; and the parts against the envelope's ambient edges. Stdlib only, sub-second.

THIS IS AN INFERRED ESTIMATE FROM TEXTBOOK FILM COEFFICIENTS, NOT A MEASUREMENT AND NOT A MODEL OF THE KIT.
Nothing has been built or powered. Its only purpose is to show how sensitive the inside-air rise is to the
assumptions, so that TEST-PLAN E3 measures the right things. Every input is listed with its basis.

Usage: python3 w4-scratch-thermal.py
"""

# Areas (m2). Face = the 1450PF plate outline 365.5 x 249.5 (panel1450.py PLATE). Side walls and floor of the
# BASE only (the lid is hinged away when open): inner 371 x 259 x 109 (1451-931 drawing) up to the outer
# 411 x 329 footprint plus an allowance for the moulded ribs, which is how 32.53 reached 0.22 m2.
A_FACE = 0.3655 * 0.2495
A_SIDE = (2 * (0.371 + 0.259) * 0.109, 0.22)          # (low, high)
A_FLOOR = (0.371 * 0.259, 0.411 * 0.329)
A_LID = 0.411 * 0.329 + 2 * (0.411 + 0.329) * 0.045    # lid top plus lid skirt, lid closed only

# Film coefficients (W/m2K). Natural convection plus linearised radiation (4 eps sigma T^3 at about 310 K,
# eps 0.85 to 0.9 for black anodised aluminium and polypropylene) outside; inside with and without the
# mixer fans. Wall conduction: polypropylene k about 0.22 W/mK over 3 to 4 mm (32.53), so t/k about 0.018.
H_OUT_FACE = (9.5, 11.5)      # up-facing plate, 10 to 30 K rise, still air, indoors or shaded
H_OUT_WALL = (8.0, 10.0)      # vertical PP wall, still air
H_OUT_FLOOR = (3.0, 8.0)      # floor on a table (poor) up to floor on ground or a metal deck (better)
H_IN_FANS = (10.0, 25.0)      # low-velocity forced flow from the mixer and cooler fans, plus internal radiation
H_IN_STILL = (4.0, 6.0)       # natural convection plus internal radiation, fans off or absent
T_OVER_K_WALL = 0.018         # m2K/W
H_GAP_LID = 6.0               # plate to lid across the 46.5 to 53.5 mm enclosed gap: conv about 1.4 + rad about 4.6

def series(*g):
    return 1.0 / sum(1.0 / x for x in g)

def conductance(fans, lid_open, bound):
    i = 0 if bound == "low" else 1
    h_in = (H_IN_FANS if fans else H_IN_STILL)[i]
    wall_u = 1.0 / (1.0 / h_in + T_OVER_K_WALL + 1.0 / H_OUT_WALL[i])
    floor_u = 1.0 / (1.0 / h_in + T_OVER_K_WALL + 1.0 / H_OUT_FLOOR[i])
    g_walls = A_SIDE[i] * wall_u + A_FLOOR[i] * floor_u
    g_face_in = A_FACE * h_in
    if lid_open:
        g_face = series(g_face_in, A_FACE * H_OUT_FACE[i])
    else:
        g_face = series(g_face_in, A_FACE * H_GAP_LID, A_LID * H_OUT_WALL[i])
    return g_walls + g_face, g_walls, g_face

# Heat per state (W). Two sets. (1) Appendix 32.53's own figures, as in round 1. (2) Adjudication A05's PROVISIONAL
# battery-side watts per power state (adj/A05-modes-and-runtime-basis, section 2 table): the heat inside is taken
# as the battery-side watts, which slightly overstates it by what the antennas radiate and the monitor's glass
# sheds outward; A05's states are PROVISIONAL (owner condition 2) and carry a large T share.
MODES_3253 = [("32.53 one module, lid open", 30.0, True),
              ("32.53 two modules, lid open", 38.0, True),
              ("32.53 three modules loaded, lid open", 50.0, True)]
MODES_A05 = [("A05 PS-RED (one module, monitor off), lid closed", 19.7, False),
             ("A05 PS-RED-b (cluster idle, monitor off), lid closed", 25.4, False),
             ("A05 PS-IDLE (three idle, monitor dimmed), lid open", 29.4, True),
             ("A05 PS-IDLE-SPEC (monitor on, beacons), lid open", 32.4, True),
             ("A05 PS-EMCON as generated, lid open", 47.6, True),
             ("A05 PS-TYP (three typical, monitor on), lid open", 60.1, True)]
REF_3253 = {30.0: (10, 14), 38.0: (12, 18), 50.0: (16, 24)}   # (fans, still) rises quoted in 32.53

# Solar. MIL-STD-810H Method 505 uses a peak of 1120 W/m2 (the standard is not filed in v2/vendor/standards/, so the
# figure is INFERRED). Areas from panel1450.py: the frame window 349.65 x 233.83 is what the sun sees of the plate; inside
# it the monitor window 205.75 x 140.09 (glass level with the plate) and the e-paper lens 107.19 x 66.6; the 8 mm band of
# the plate under the frame ring is shaded by the ring, which takes that sun itself (ring colour TBD).
E_SUN = 1120.0
A_WINDOW = 0.34965 * 0.23383
A_MON = 0.20575 * 0.14009
A_EPD = 0.10719 * 0.0666
A_AL = A_WINDOW - A_MON - A_EPD                   # sunlit aluminium (small holes and light guides ignored)
A_RING = A_FACE - A_WINDOW                        # the plate band under the 1450PF ring
ALPHA_AL = (0.85, 0.9)                            # black anodised aluminium, textbook range, INFERRED
ALPHA_GLASS = (0.80, 0.95)                        # a display stack under glass absorbs what it does not reflect: TBD, no maker figure
G_PLATE_OUT = (1.0, 1.5)                          # 32.53's plate surface to ambient, W/K, at a 30 to 40 K plate rise

ENV_ONE_MODULE_MAX_AMBIENT = 40.0                 # OPERATING-ENVELOPE.md:94 and :100, pcb_envelope.yaml carve-out above +35 C
ENV_THREE_MODULES_MAX_AMBIENT = 35.0
SGP41_MAX = 55.0                                  # OPERATING-ENVELOPE.md:82-83

def rise(q, fans, lid):
    return q / conductance(fans, lid, "high")[0], q / conductance(fans, lid, "low")[0]

if __name__ == "__main__":
    print("CONDUCTANCE inside air -> ambient, W/K (low bound .. high bound)")
    for fans in (True, False):
        for lid in (True, False):
            lo, hi = conductance(fans, lid, "low"), conductance(fans, lid, "high")
            print("  fans %-3s lid %-6s total %.2f .. %.2f   (walls+floor %.2f .. %.2f, face path %.2f .. %.2f)" % (
                "on" if fans else "off", "open" if lid else "closed", lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    print("  appendix 32.53 quotes: lid open about 3.0 to 3.3 with fans, about 2.1 still; lid closed about 1.5 to 2 with fans")
    print()
    print("INSIDE-AIR RISE, K (this estimate, high G .. low G)")
    for name, q, lid in MODES_3253 + MODES_A05:
        for fans in (True, False):
            a, b = rise(q, fans, lid)
            ref = REF_3253.get(q) if name.startswith("32.53") else None
            r = ("" if ref is None else "   32.53: %d" % (ref[0] if fans else ref[1]))
            print("  %-55s %5.1f W fans %-3s  %5.1f .. %5.1f%s" % (name, q, "on" if fans else "off", a, b, r))
    print()
    print("INSIDE AIR AT THE ENVELOPE'S EDGES (fans on, lid open), C, against the SGP41's +%.0f C" % SGP41_MAX)
    for name, q, amb in (("one module (32.53, 30 W, monitor on)", 30.0, ENV_ONE_MODULE_MAX_AMBIENT),
                         ("PS-IDLE-SPEC (A05, 32.4 W)", 32.4, ENV_ONE_MODULE_MAX_AMBIENT),
                         ("three loaded (32.53, 50 W)", 50.0, ENV_THREE_MODULES_MAX_AMBIENT),
                         ("PS-TYP (A05, 60.1 W)", 60.1, ENV_THREE_MODULES_MAX_AMBIENT)):
        a, b = rise(q, True, True)
        print("  %-40s at +%.0f C ambient: %5.1f .. %5.1f C %s" % (name, amb, amb + a, amb + b, "(exceeds 55 at the upper end)" if amb + b > SGP41_MAX else ""))
    a, b = rise(19.7, True, False)
    print("  %-40s at +%.0f C ambient: %5.1f .. %5.1f C (lid closed, the envelope's reduced mode above +35 C)" % ("PS-RED (A05, 19.7 W)", 40.0, 40.0 + a, 40.0 + b))
    print()
    print("SOLAR at %.0f W/m2 (areas from panel1450.py)" % E_SUN)
    print("  sunlit aluminium %.4f m2: %4.1f .. %4.1f W absorbed" % (A_AL, A_AL * E_SUN * ALPHA_AL[0], A_AL * E_SUN * ALPHA_AL[1]))
    print("  monitor glass    %.4f m2: %4.1f .. %4.1f W absorbed (absorptance TBD 0.80 to 0.95)" % (A_MON, A_MON * E_SUN * ALPHA_GLASS[0], A_MON * E_SUN * ALPHA_GLASS[1]))
    print("  e-paper lens     %.4f m2: %4.1f .. %4.1f W absorbed (absorptance TBD 0.80 to 0.95)" % (A_EPD, A_EPD * E_SUN * ALPHA_GLASS[0], A_EPD * E_SUN * ALPHA_GLASS[1]))
    print("  frame ring band  %.4f m2: %4.1f .. %4.1f W if the ring is black (colour TBD)" % (A_RING, A_RING * E_SUN * ALPHA_AL[0], A_RING * E_SUN * ALPHA_AL[1]))
    tot_lo = A_AL * E_SUN * ALPHA_AL[0] + (A_MON + A_EPD) * E_SUN * ALPHA_GLASS[0] + A_RING * E_SUN * ALPHA_AL[0]
    tot_hi = A_AL * E_SUN * ALPHA_AL[1] + (A_MON + A_EPD) * E_SUN * ALPHA_GLASS[1] + A_RING * E_SUN * ALPHA_AL[1]
    print("  whole face %.4f m2: %4.1f .. %4.1f W (round 1 quoted 87 to 92 W for the whole face at the aluminium's absorptance)" % (A_FACE, tot_lo, tot_hi))
    q_al = (A_AL * E_SUN * ALPHA_AL[0], A_AL * E_SUN * ALPHA_AL[1])
    print("  aluminium's own share into 32.53's plate conductance %.1f to %.1f W/K: plate rise %.0f .. %.0f K over ambient before any heat from inside" % (
        G_PLATE_OUT[0], G_PLATE_OUT[1], q_al[0] / G_PLATE_OUT[1], q_al[1] / G_PLATE_OUT[0]))
    print("  (a plate warmer than the inside air also drives heat INTO the case: the solar load raises the inside-air rise; not modelled)")
    for name, area, alpha in (("lid top, lid closed, black case", 0.411 * 0.329, (0.85, 0.95)),
                              ("lid top, lid closed, light case colour", 0.411 * 0.329, (0.4, 0.6))):
        print("  %-42s %5.0f .. %5.0f W absorbed" % (name, area * E_SUN * alpha[0], area * E_SUN * alpha[1]))
    print()
    # PA key-down into the plate: RA30H1317M1 30 W out at a 40 percent minimum total efficiency (datasheet) is at most
    # 75 W in and 45 W of heat. Plate heat capacity from panel1450.py's plate (448 g of aluminium at 0.90 J/gK).
    c_plate = 448 * 0.90
    print("PA key-down: 45 W into a %.0f J/K plate is %.1f K per minute before any loss (whole plate, spreading ignored)" % (c_plate, 45 * 60 / c_plate))
