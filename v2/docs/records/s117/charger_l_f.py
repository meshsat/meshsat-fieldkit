#!/usr/bin/env python3
"""S-117 (MESHSAT-1357, stream s117, 29 September 2026): board A's charger U3 (BQ25731), its inductor and its switching
frequency, from the makers' own figures. Desk arithmetic, not a measurement: nothing here is built. Stdlib only, no KiCad.

WHAT IT ANSWERS. Which inductor and which of TI's two rows (SLUSE66A 9.3.11 Table 9-4 and 9.3.12 Table 9-5, printed pages
27 and 28) board A's charger should carry, from (1) the inductor the generator draws today, L2 "3.3uH XAL6030-332ME
(Isat 12.2 A)" on the XAL60xx land, (2) the currents the charger's hardware lets through that inductor, and (3) the losses
each frequency implies with the power FETs the generator draws (Q7 to Q10, CSD18510Q5B).

EVERY INPUT IS NAMED BELOW WITH ITS SOURCE. A number read off a maker's CURVE (not a table) is marked INFERRED: the reading
is the author's, to about a tenth of a microhenry or a tenth of a volt. A figure no document gives is not used.

Usage: python3 charger_l_f.py > charger_l_f.out   (the committed .out is this script's output, byte for byte)."""
import math

# ------------------------------------------------------------------------------------------------ the makers' figures
# TI SLUSE66A (BQ25731, June 2020, revised January 2021), v2/vendor/ti/bq25731-datasheet.pdf. Printed pages.
FSW = {"800": (680e3, 800e3, 920e3), "400": (340e3, 400e3, 460e3)}   # 8.5 FSW, p.16: Reg0x01[1] = 0 / = 1
REGN = 6.0            # 8.5 VREGN_REG, p.11: 5.7 / 6.0 / 6.3 V (typ used; the gate figures below are typical too)
R_HI_ON = 6.0         # 8.5 RDS_HI_ON_Q1, p.16: 6 Ohm typ, the turn-on path of Q1's driver (VBTST1 - VSW1 = 5 V)
R_HI_OFF = 1.3        # 8.5 RDS_HI_OFF_Q1, p.16: 1.3 typ / 2.2 max Ohm, the turn-off path
T_DEAD_RISE, T_DEAD_FALL = 40e-9, 30e-9   # 10.2.2.6, p.88: "around 40 ns" and "around 30 ns"

# TI SLPS632 (CSD18510Q5B, March 2017), v2/vendor/battery/ti-csd18510q5b.pdf, 5.1 p.3 (typical, 25 C) and figures p.5.
QGD, QGS, QG_TH = 21e-9, 28e-9, 15e-9     # Qgd at VDS 20 V, ID 32 A; Qgs; Qg(th)
QOSS = 35e-9                              # at VDS 20 V
QRR = 31e-9                               # at VDS 20 V, IF 32 A, 300 A/us (the maker's only condition)
RG = 0.9                                  # series gate resistance, typ (1.8 max)
VF = 0.8                                  # body diode at 32 A, typ (1.0 max); lower at this stage's currents
QG_45 = 58e-9     # table, Qg total at VGS 4.5 V (typ): a floor for the 6 V drive
QG_6V = 75e-9     # INFERRED: Figure 4 (ID 32 A, VDS 20 V) read at VGS = 6 V; the table gives 58 nC at 4.5 V, 118 at 10 V
VPLT = 2.6        # INFERRED: Figure 4's plateau spans about 2.5 to 3.0 V at 32 A; Figure 3 gives about 2.45 V at 12 A, 25 C
RDS_6V = 1.1e-3   # INFERRED: Figure 2 (25 C) read at VGS = 6 V: about 0.11 V at 100 A. Table: 1.2 / 1.6 mOhm at 4.5 V

# Coilcraft Document 887-1 (XAL60xx) and 804-1 (XAL1010), both revised 02/25/26, v2/vendor/coilcraft/ and v2/vendor/power/.
# L nominal (+-20 %), DCR typ / max (mOhm), Isat (A, 30 % drop, typ, 25 C), Irms (A) at 20 C and 40 C rise from 25 C.
# The L-versus-current points are INFERRED readings of the makers' typical curves (887-2 and 887-3; 804-2), in uH.
PARTS = {
    "XAL6030-332ME": dict(L=3.3e-6, dcr=(19.92e-3, 20.81e-3), isat=12.2, irms=(6.0, 8.0), land="XAL60xx (drawn today)",
                          curve=[(0, 3.0), (4, 2.87), (8, 2.72), (12, 2.48), (16, 2.2), (20, 1.72)]),
    "XAL6060-472ME": dict(L=4.7e-6, dcr=(13.10e-3, 14.40e-3), isat=10.5, irms=(8.0, 11.0), land="XAL60xx (same land)",
                          curve=[(0, 4.65), (4, 4.35), (6, 4.1), (8, 3.8), (10, 3.5), (12, 2.95)]),
    "XAL1010-332ME": dict(L=3.3e-6, dcr=(3.70e-3, 4.10e-3), isat=27.4, irms=(18.2, 25.0), land="XAL1010 (L1 and L8's land)",
                          curve=[(0, 3.35), (5, 3.25), (10, 3.07), (15, 2.85), (20, 2.52), (25, 2.28), (30, 2.07)]),
    "XAL1010-472ME": dict(L=4.7e-6, dcr=(5.20e-3, 5.70e-3), isat=25.4, irms=(17.5, 24.0), land="XAL1010 (L1 and L8's land)",
                          curve=[(0, 4.75), (5, 4.58), (10, 4.3), (15, 3.95), (20, 3.6), (25, 3.3), (30, 2.95)]),
}

# ------------------------------------------------------------------------------------------------ the charger's currents
# The charger is in BUCK mode throughout: VBUS20 (20.0 V nominal, 20.7 V at the front end's corners, gen_sch_a.py) is above
# every system voltage the 4S pack gives (16.8 V full). Q4 (board A's Q10) is on, Q1 and Q2 (Q7, Q8) switch (Table 9-3,
# p.27). The inductor's average current is the converter's output current, bounded by its input power: IL = VIN x IIN x
# eta / VSYS, taken here at eta = 1 so the current is an upper bound. With no BATFET (Figure 10-1) the system node is the
# pack's voltage, down to 10.0 V at the primary protector's CUV (review-packets/battery/FUSE-INTERPRETATION.md, "Pack voltage
# per state": 16.8 full, 14.4 nominal, 10.6 at the 2.65 V cut-off, 10.0 at the primary's CUV, 9.0 at the secondary's UV).
# The input bound AS GENERATED: the front end's constant-current loop, VSNS 43 / 50 / 57 mV over R11 10 mOhm = 4.3 / 5.0 /
# 5.7 A (TI SNVSAI1D 6.5; gen_sch_a.py's front-end comment "VSNS 57 mV over R11's 10 mOhm; the charger can ask for it"),
# under U3's own IIN_HOST clamp of 6.35 A at RSNS_RAC = 0b (SLUSE66A 9.3.5 p.25; 9.6.22 p.80 adds 100 mA for the maximum).
# Option A(i) (fnd/a1int, records/a1elec/CHARGER.md, not on main) re-rates R11 to 6.2 mOhm (6.94 / 8.06 / 9.19 A), so U3's
# own clamp becomes the bound: 6.35 A + 0.1 A = 6.45 A; its drafted setting is IIN_HOST 6.2 A.
POINTS = [
    # name, VIN, IIN, VSYS, what it is
    ("G1", 20.7, 5.7, 10.0, "as generated: the front end's 5.7 A maximum into a pack at its 10.0 V CUV (the bound)"),
    ("G2", 20.7, 5.7, 10.6, "as generated: the same input, the pack at its 2.65 V a cell cut-off"),
    ("G3", 20.7, 5.7, 14.4, "as generated: the same input, the pack at its 14.4 V nominal"),
    ("G4", 20.0, 5.0, 14.4, "as generated: the front end's 5.0 A typical limit, 20.0 V, nominal pack"),
    ("G5", 20.7, 4.15, 14.5, "as generated with FW-A16 revised (a1elec E1): IIN_HOST 4.15 A"),
    ("A1", 20.7, 6.2, 14.5, "Option A(i) drafted (a1elec E2): IIN_HOST 6.2 A at the model's 14.5 V node"),
    ("A2", 20.7, 6.45, 10.0, "Option A(i) bound: U3's 6.35 A clamp plus 0.1 A, pack at 10.0 V"),
    ("S1", 20.7, 5.7, 9.0, "sensitivity only: the secondary protector's 9.0 V UV (the primary has failed)"),
]


def l_at(part, amps):
    """The part's typical inductance at a DC current, as a fraction of its own zero-current reading (INFERRED curve)."""
    pts = PARTS[part]["curve"]
    if amps <= pts[0][0]: return 1.0
    for (a0, l0), (a1, l1) in zip(pts, pts[1:]):
        if amps <= a1: return (l0 + (l1 - l0) * (amps - a0) / (a1 - a0)) / pts[0][1]
    return pts[-1][1] / pts[0][1]


def ripple(vin, vsys, f, L):
    """SLUSE66A 10.2.2.3 Equation 3, p.85: IRIPPLE_BUCK = VIN x D x (1 - D) / (fS x L), D = VOUT / VIN."""
    d = vsys / vin
    return vin * d * (1 - d) / (f * L)


def stage(part, fkey, vin, iin, vsys, worst):
    """Inductor and FET figures at one point. worst=True: L at -20 % and its DC-bias fall, fS at the table minimum."""
    p = PARTS[part]
    il = vin * iin / vsys
    frac = l_at(part, il)
    L = p["L"] * frac * (0.8 if worst else 1.0)
    f = FSW[fkey][0] if worst else FSW[fkey][1]
    di = ripple(vin, vsys, f, L)
    ipk = il + di / 2
    irms = math.sqrt(il ** 2 + di ** 2 / 12)                  # Equation 8, p.87
    return dict(il=il, L=L, frac=frac, f=f, di=di, ipk=ipk, irms=irms, d=vsys / vin)


def fet_losses(vin, s, f, qsw):
    """SLUSE66A 10.2.2.6 Equations 6 to 22, pp.86 to 88, buck mode, with the CSD18510Q5B's figures above."""
    d, irms, il, di = s["d"], s["irms"], s["il"], s["di"]
    iv, ip = il - di / 2, il + di / 2                         # Equations 11 and 12
    ion = (REGN - VPLT) / (R_HI_ON + RG)                      # Equation 15
    ioff = VPLT / (R_HI_OFF + RG)
    ton, toff = qsw / ion, qsw / ioff                         # Equation 13
    p = {}
    p["Q7 conduction"] = d * irms ** 2 * RDS_6V               # Equation 7
    p["Q7 V-I overlap"] = 0.5 * vin * iv * ton * f + 0.5 * vin * ip * toff * f   # Equation 10
    p["Q7 Qoss"] = 0.5 * vin * QOSS * f                       # Equation 16
    p["Q7 gate"] = vin * QG_6V * f                            # Equation 17 (VIN, not 6 V: REGN is an LDO from VIN)
    p["Q8 conduction"] = (1 - d) * irms ** 2 * RDS_6V         # Equation 19
    p["Q8 reverse recovery"] = vin * QRR * f                  # Equation 21
    p["Q8 dead time"] = VF * iv * f * T_DEAD_RISE + VF * ip * f * T_DEAD_FALL   # Equation 22
    p["Q8 gate"] = vin * QG_6V * f
    p["Q10 conduction (on)"] = irms ** 2 * RDS_6V             # Table 9-3: Q4 ON in buck mode
    return p, ton, toff


def main():
    print("S-117: board A's charger U3 (BQ25731), inductor and frequency. MESHSAT-1357, stream s117. Desk arithmetic on the")
    print("makers' figures; nothing is built or measured. INFERRED: curve readings (inductance under current; the FET's gate")
    print("charge at 6 V, plateau and RDS(on) at 6 V). Currents at eta = 1 (an upper bound).")
    print()
    print("1. THE CHARGER'S CURRENTS (buck mode; IL = VIN x IIN / VSYS)")
    print("%-3s %6s %6s %6s %8s  %s" % ("pt", "VIN", "IIN", "VSYS", "IL (A)", "what"))
    for n, vin, iin, vsys, what in POINTS:
        print("%-3s %6.2f %6.2f %6.2f %8.2f  %s" % (n, vin, iin, vsys, vin * iin / vsys, what))
    print()
    print("2. THE INDUCTOR AT EACH POINT: ripple (Equation 3), peak, RMS (Equation 8), against the maker's Isat and Irms")
    print("   nominal = L nominal x its DC-bias fall, fS typical; worst = L at -20 % x its fall, fS at the table minimum.")
    print("   Equation 2 (p.85): ISAT >= ICHG + IRIPPLE / 2, read at the worst ripple. Irms: the maker's 40 C rise figure.")
    combos = [("XAL6030-332ME", "800"), ("XAL6030-332ME", "400"), ("XAL6060-472ME", "400"),
              ("XAL1010-332ME", "800"), ("XAL1010-472ME", "400")]
    for part, fk in combos:
        p = PARTS[part]
        print()
        print("   %s at %s kHz: L %.1f uH +-20 %%, DCR %.2f / %.2f mOhm, Isat %.1f A, Irms %.1f / %.1f A (20 / 40 C rise); land %s"
              % (part, fk, p["L"] * 1e6, p["dcr"][0] * 1e3, p["dcr"][1] * 1e3, p["isat"], p["irms"][0], p["irms"][1], p["land"]))
        print("   %-3s %7s %9s %9s %8s %8s %9s %9s %10s %9s" % ("pt", "IL", "L nom", "L worst", "dI nom", "dI wst", "Ipk wst",
                                                             "Irms", "Eq.2", "Irms/40C"))
        for n, vin, iin, vsys, _ in POINTS:
            sn = stage(part, fk, vin, iin, vsys, False); sw = stage(part, fk, vin, iin, vsys, True)
            eq2 = "PASS" if p["isat"] >= sw["ipk"] else "FAIL"
            print("   %-3s %7.2f %8.2fu %8.2fu %8.2f %8.2f %9.2f %9.2f %10s %8.0f%%"
                  % (n, sn["il"], sn["L"] * 1e6, sw["L"] * 1e6, sn["di"], sw["di"], sw["ipk"], sw["irms"], eq2,
                     100 * sw["irms"] / p["irms"][1]))
    print()
    print("3. THE LOSSES EACH FREQUENCY IMPLIES WITH THE DRAWN FETS (Q7 to Q10 CSD18510Q5B), SLUSE66A Equations 6 to 22")
    print("   Qsw two ways: TI's Equation 14, Qgd + Qgs = %.0f nC (the maker's method when no Qsw is given), and Qgd + Qgs -"
          % ((QGD + QGS) * 1e9))
    print("   Qg(th) = %.0f nC (the charge past the threshold only; INFERRED as the lower bound). Ion = (REGN - Vplt) / (%.1f + %.1f),"
          % ((QGD + QGS - QG_TH) * 1e9, R_HI_ON, RG))
    print("   Ioff = Vplt / (%.1f + %.1f): Ion %.3f A, Ioff %.3f A. Inductor copper at DCR max, 25 C. Core loss: NOT COMPUTED (Coilcraft"
          % (R_HI_OFF, RG, (REGN - VPLT) / (R_HI_ON + RG), VPLT / (R_HI_OFF + RG)))
    print("   publishes it through its web calculator only, which is not held): INCONCLUSIVE, and it too rises with frequency.")
    for part, fk in (("XAL1010-472ME", "400"), ("XAL1010-332ME", "800"), ("XAL6030-332ME", "800")):
        print()
        print("   %s at %s kHz (typical fS, nominal L with its fall)" % (part, fk))
        print("   %-3s %8s %8s %8s %8s %8s %8s %9s %9s %8s" % ("pt", "Pin W", "Q7 sw", "Q7 all", "Q8 all", "Q10", "L2 Cu",
                                                          "stage", "sw part", "eta"))
        for n, vin, iin, vsys, _ in POINTS:
            s = stage(part, fk, vin, iin, vsys, False)
            for qsw, tag in ((QGD + QGS, "Eq14"), (QGD + QGS - QG_TH, "Qgs2")):
                pl, ton, toff = fet_losses(vin, s, s["f"], qsw)
                q7sw = pl["Q7 V-I overlap"] + pl["Q7 Qoss"] + pl["Q7 gate"]
                q7 = q7sw + pl["Q7 conduction"]
                q8 = pl["Q8 conduction"] + pl["Q8 reverse recovery"] + pl["Q8 dead time"] + pl["Q8 gate"]
                q10 = pl["Q10 conduction (on)"]
                lcu = s["irms"] ** 2 * PARTS[part]["dcr"][1]
                sw = q7sw + pl["Q8 reverse recovery"] + pl["Q8 dead time"] + pl["Q8 gate"]
                tot = q7 + q8 + q10 + lcu
                pin = vin * iin
                print("   %-3s %8.1f %8.2f %8.2f %8.2f %8.2f %8.2f %9.2f %9.2f %8.3f  %s (ton %.0f ns, toff %.0f ns)"
                      % (n, pin, q7sw, q7, q8, q10, lcu, tot, sw, (pin - tot) / pin, tag, ton * 1e9, toff * 1e9))
    print()
    print("   'stage' is Q7 + Q8 + Q10 + L2's copper; 'sw part' is every term that scales with fS. Not in 'stage': the core")
    print("   loss (not held), R16 and R17, the controller's own quiescent draw, and the FETs' rise in RDS(on) with temperature")
    print("   (Figure 2 is 25 C). eta here is therefore an upper figure for the stage, not the charger's efficiency.")
    print()
    print("4. THE 400 kHz ROW AGAINST THE 800 kHz ROW ON THE SAME LAND (XAL1010), switching terms only, both Qsw readings")
    print("   %-3s %14s %14s %14s" % ("pt", "400k 4.7uH", "800k 3.3uH", "800k extra"))
    for n, vin, iin, vsys, _ in POINTS:
        row = []
        for part, fk in (("XAL1010-472ME", "400"), ("XAL1010-332ME", "800")):
            s = stage(part, fk, vin, iin, vsys, False)
            vals = []
            for qsw in (QGD + QGS - QG_TH, QGD + QGS):
                pl, _, _ = fet_losses(vin, s, s["f"], qsw)
                vals.append(pl["Q7 V-I overlap"] + pl["Q7 Qoss"] + pl["Q7 gate"] + pl["Q8 reverse recovery"]
                            + pl["Q8 dead time"] + pl["Q8 gate"])
            row.append(vals)
        print("   %-3s %6.2f to %4.2f %6.2f to %4.2f %6.2f to %4.2f W"
              % (n, row[0][0], row[0][1], row[1][0], row[1][1], row[1][0] - row[0][0], row[1][1] - row[0][1]))
    print()
    print("5. THE GATE DRIVE THE CHARGER'S OWN 6 V REGULATOR MUST SUPPLY (REGN feeds both low-side drivers and, through the")
    print("   bootstrap capacitors, both high-side drivers). In buck mode Q1 and Q2 (board A's Q7 and Q8) switch every cycle and")
    print("   Q4 is held on (Table 9-3, p.27), so IREGN = (Qg(Q7) + Qg(Q8)) x fS. SLUSE66A 8.5, p.11: VREGN_REG 5.7 / 6.0 / 6.3 V")
    print("   is specified for 0 to 60 mA; IREGN_LIM, the current limit with the converter enabled, is 50 min / 65 typ mA.")
    print("   Qg at 6 V: %.0f nC INFERRED (Figure 4); the table's %.0f nC at 4.5 V is a floor for a 6 V drive." % (QG_6V * 1e9, QG_45 * 1e9))
    print("   %-10s %12s %12s   %s" % ("fS", "Qg 58 nC", "Qg 75 nC", "against 60 mA spec / 50 mA minimum limit"))
    for fk in ("400", "800"):
        for k, f in zip(("min", "typ", "max"), FSW[fk]):
            lo, hi = 2 * QG_45 * f * 1e3, 2 * QG_6V * f * 1e3
            verdict = ("inside both" if hi <= 50 else "OVER the 50 mA minimum limit" if lo > 50 else
                       "straddles the 50 mA minimum limit")
            print("   %-10s %9.1f mA %9.1f mA   %s" % ("%s %s kHz" % (k, fk) if k != "typ" else "%s kHz" % fk, lo, hi, verdict))
    print("   In BUCK-BOOST mode all four FETs switch (Table 9-3) and the demand doubles; the maker states the three modes by")
    print("   the VBUS and VBAT combination and gives no threshold for the transition (9.3.10, p.27), so whether U3 enters it")
    print("   near a full pack (16.8 V against 20 V in) is not stated. Four CSD18510Q5B switching:")
    for fk in ("400", "800"):
        f = FSW[fk][1]
        print("   %s kHz typical: %.1f to %.1f mA against the 50 mA minimum limit" % (fk, 4 * QG_45 * f * 1e3, 4 * QG_6V * f * 1e3))
    print("   The same current is drawn from VBUS20 through REGN's linear regulator: at 20.7 V and the typical fS the gate")
    for fk in ("400", "800"):
        f = FSW[fk][1]
        i = 2 * QG_6V * f
        ldo = (20.7 - REGN) * i
        print("   drive takes %.2f W at %s kHz, of which the regulator's own drop, %.2f W, is dissipated inside U3; with the"
              % (20.7 * i, fk, ldo))
        print("   JEDEC RthJA of 37.2 C/W (8.4, p.9) that drop alone is a %.0f K rise of U3's junction over its surroundings."
              % (ldo * 37.2))
    print("   (JEDEC's board is not board A; the figure orders the two rows, it does not predict U3's temperature.)")


if __name__ == "__main__":
    main()
