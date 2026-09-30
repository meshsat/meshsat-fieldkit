#!/usr/bin/env python3
"""indep_r11.py: the checker's own arithmetic for CHECK-3 task 2 (an AI check). Figures typed from the makers' pages the
checker read: LM5176 SNVSAI1D p.7 (VSNS 43/50/57 mV, ISNS bias 3 uA typ, boost peak 100/120/140 mV), p.6 (fSW 175/200/225 kHz,
VIN operating current 4 mA max); HoJLR2512 p.2 (TCR 50 ppm/K, derating from 70 C to 0 at 170 C); BQ25731 p.1 (2.5 %) and
p.80 (+100 mA); Coilcraft XAL1010-103ME (10 uH +-20 %, Isat 17.5 A typ 25 C 30 % drop, Irms 15.5 A at 40 K, DCR 14.75 max);
CSD19532Q5B p.3 (5.7 mOhm max at VGS 6 V, Qg 62 nC max at 10 V, RthetaJA 50 C/W), p.6 Figure 8 (read by eye: 1.17 / 1.55 /
2.0 at 50 / 100 / 150 C); CSD17578Q5A / CSD17577Q5A (Qg 10.3 / 17 nC max at 4.5 V, 22.3 / 35 nC max at 10 V); BQ25731
IAC_SW_LIGHT_buck 2.2 mA typ. Netlist: R11 10 mOhm FE_OUT to VBUS20, R12 5 mOhm, R197 100k, R6 + R7 250k."""
import math
V43, V50, V57 = 0.043, 0.050, 0.057
OFFS = 3e-6 * 100.0
TCR, DT = 50e-6, max(abs(-20 - 25), abs(100 - 25))


def band(r):
    return (V43 - OFFS) / (r * 1.01 * (1 + TCR * DT)), V50 / r, (V57 + OFFS) / (r * 0.99 * (1 - TCR * DT))


u3max = max(6.2 + 0.1, 6.2 * 1.025)
fe_other_paper = 0.004 + 4 * 62e-9 * 225e3 + 21 / 100e3 + 21 / 250e3
fe_two_fets = 0.004 + 2 * 62e-9 * 225e3 + 21 / 100e3 + 21 / 250e3
qg6_78 = 10.3 + (22.3 - 10.3) * 1.5 / 5.5
qg6_77 = 17 + (35 - 17) * 1.5 / 5.5
u3_vbus = 0.0022 + (qg6_78 + qg6_77) * 1e-9 * 460e3 + 6.3 / 51.3e3
for lab, r in (("held 10 mOhm", 0.010), ("proposed 6.2 mOhm", 0.0062)):
    print("%-18s stacked band %.3f / %.3f / %.3f A" % ((lab,) + band(r)))
print("U3 maximum %.3f A" % u3max)
print("other loads, the record's composition (4 FETs x 62 nC x 225 kHz + 4 mA + R197 + divider): %.4f A" % fe_other_paper)
print("  the LM5176 with two FETs switching (boost: Q4, Q5): %.4f A; U3's own VBUS pin (REGN gate drive of Q7, Q8 at 6 V, 460 kHz,"
      " light-load 2.2 mA, ILIM divider): %.4f A; together %.4f A" % (fe_two_fets, u3_vbus, fe_two_fets + u3_vbus))
serv = u3max + fe_other_paper
lo = band(0.0062)[0]
print("in service %.3f A; margin proposed %+.3f A; held %+.3f A" % (serv, lo - serv, band(0.010)[0] - serv))
print("GEN: 4.25 + %.3f = %.3f A against %.3f: %+.3f A" % (fe_other_paper, 4.25 + fe_other_paper, band(0.010)[0], band(0.010)[0] - 4.25 - fe_other_paper))
rmax = 0.0062 * 1.01 * (1 + TCR * DT)
rcu = (V43 - OFFS) / serv - rmax
print("Kelvin: copper allowed %.3f mOhm (%.2f mV at %.3f A, %.1f %% of 50 mV); at 25 C if the copper sits at 62.1 / 100 C: %.3f / %.3f mOhm" % (
    rcu * 1e3, rcu * serv * 1e3, serv, rcu * serv / 0.05 * 100, rcu / (1 + 0.00393 * 37.1) * 1e3, rcu / (1 + 0.00393 * 75) * 1e3))
print("routed board (26.62 + 2.16 mV): at 6.0 A %.2f mOhm, at 3.80 A %.2f mOhm" % (28.78 / 6.0, 28.78 / 3.8))
VB, ETA = 20.887, 0.93
def boost(iout, vin, l=10e-6 * 0.8, f=175e3):
    iin = iout * VB / ETA / vin
    d = 1 - vin / VB
    rip = vin * d / (l * f)
    return iin, d, rip, iin + rip / 2, math.sqrt(iin ** 2 + rip ** 2 / 12)
held, prop = band(0.010)[2], band(0.0062)[2]
for lab, i in (("held max", held), ("proposed in service", serv), ("proposed max", prop), ("GEN in service", 4.25 + fe_other_paper)):
    for vin in (15.1, 9.0):
        iin, d, rip, pk, rms = boost(i, vin)
        _, _, rip2, pk2, _ = boost(i, vin, l=10e-6 * 0.8 * 0.7)
        print("L1 %-20s %4.1f V: in %.2f A, D %.3f, ripple %.2f A, peak %.2f A (with L a further 30 %% down at Isat: peak %.2f A), rms %.2f A, 40 K Irms 15.5" % (lab, vin, iin, d, rip, pk, pk2, rms))
def k(tc):
    pts = [(25, 1.0), (50, 1.18), (75, 1.36), (100, 1.56), (125, 1.76), (150, 2.01)]
    for (t0, k0), (t1, k1) in zip(pts, pts[1:]):
        if tc <= t1:
            return k0 + (k1 - k0) * (tc - t0) / (t1 - t0)
    return 2.01
for lab, i, vin in (("Q2 proposed max", prop, 15.1), ("Q2 held max", held, 9.0), ("Q2 proposed in service", serv, 9.0), ("Q2 proposed in service", serv, 15.1), ("Q2 GEN in service", 4.25 + fe_other_paper, 9.0)):
    rms = boost(i, vin)[4]
    tj = 62.1
    for _ in range(100):
        p = rms ** 2 * 0.0057 * k(tj)
        tn = 62.1 + 50 * p
        if tn > 150:
            break
        tj = tn
    p150 = rms ** 2 * 0.0057 * 2.01
    print("%-24s %4.1f V: rms %.2f A, P at 150 C %.2f W, %s; needs RthetaJA <= %.1f C/W" % (lab, vin, rms, p150,
          ("TJ past 150 C" if tn > 150 else "TJ %.0f C (P %.2f W)" % (tj, p)), (150 - 62.1) / p150))
for lab, i in (("held max", held), ("proposed in service", serv), ("proposed max", prop)):
    pfe = i * VB / ETA
    print("board E: front end input %-20s %.1f W; stage input at 0.93 %.1f W; R11 I2R %.3f W" % (lab, pfe, pfe / 0.93, i * i * (0.0062 if lab.startswith("proposed") else 0.010) * 1.01))
print("R11 derated allowance at 62.1 C %.2f W, at 100 C %.2f W; 5 s overload at 6.2 mOhm %.1f A" % (3.0, 3.0 * (170 - 100) / 100.0, math.sqrt(15 / 0.0062)))
print("cycle-by-cycle over R12: boost peak %s A, buck valley %s A" % ("/".join("%.1f" % (v / 0.005) for v in (0.100, 0.120, 0.140)),
      "/".join("%.1f" % (v / 0.005) for v in (0.066, 0.080, 0.094))))
print("slope Eq. 26: 2 uS x 10 uH / (5 mOhm x 5) = %.0f pF" % (2e-6 * 10e-6 / (0.005 * 5) * 1e12))
print("CC loop gain ratio 6.2 / 10 = %.2f; bias offset in amperes %.0f / %.0f mA" % (0.62, OFFS / 0.0062 * 1e3, OFFS / 0.010 * 1e3))
print("vehicle alone: 144.1 W / 6.15 A = %.1f V; 130.5 W / 6.15 A = %.1f V" % (serv * VB / ETA / 6.15, held * VB / ETA / 6.15))
