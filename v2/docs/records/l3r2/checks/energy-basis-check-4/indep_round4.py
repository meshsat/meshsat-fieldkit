#!/usr/bin/env python3
"""indep_round4.py: CHECK-4 (an AI check): the three power-path cases on the checker's balance (indep_balance.py with its
COLLAPSE switch), and the electrical figures of r11dep's second issue. U3's efficiency for the 4.15 / 4.05 / 3.95 A settings
is not recomputed (s117's method); 0.9810 (GEN's printed figure) and a bracket are used. Usage: python3 indep_round4.py <repo>"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import indep_round2 as R2  # noqa: E402
B = R2.B
p40, r40, TL = R2.prof(40, 0), R2.RAT[(40, 0)], R2.TL
held_min, other = 4.212, 0.060
fe_held = held_min - other
NOM, WE = R2.NOM, R2.WE
cases = {
    "DRAWN NOM": dict(NOM, iin=4.15, e_u3=0.9810, fe_i=fe_held),
    "DERATED NOM (U3 0.9810)": dict(NOM, iin=4.05, e_u3=0.9810, fe_i=fe_held),
    "DERATED NOM (U3 0.9815)": dict(NOM, iin=4.05, e_u3=0.9815, fe_i=fe_held),
    "DRAWN WE (U3 0.9740)": dict(WE, iin=4.05, e_u3=0.9740, fe_i=fe_held),
    "DERATED WE (U3 0.9740)": dict(WE, iin=3.95, e_u3=0.9740, fe_i=fe_held),
}
print("1. MEAN DAY 40/0, TYP ; WAB")
for nm, c in cases.items():
    for n in (9, 14, 15):
        print("   %-26s 4S%dP: %s ; %s" % (nm, n, B.fmt(R2.both(n, p40, B.PR0 * r40[0], c)), B.fmt(R2.both(n, p40, B.PR0 * r40[1], c))))
B.COLLAPSE = True
for nm, c in (("RESISTOR-LB NOM", NOM), ("RESISTOR-LB WE", WE)):
    for n in (9, 14, 15):
        print("   %-26s 4S%dP: %s ; %s" % (nm, n, R2.fmt(R2.both(n, p40, B.PR0 * r40[0], c)), R2.fmt(R2.both(n, p40, B.PR0 * r40[1], c))))
    hrs = [h for h in range(24) if min(400 * p40[h] / 1000 * B.PR0 * r40[0], 200) * 0.93 * 0.93 >= c["iin"] * c["vbus"]]
    hrs2 = [h for h in range(24) if min(400 * p40[h] / 1000 * B.PR0 * r40[1], 200) * 0.93 * 0.93 >= c["iin"] * c["vbus"]]
    print("   %s: hours at the cap TYP %s, WAB %s" % (nm, hrs, hrs2))
B.COLLAPSE = False
sj = json.load(open(os.path.join(R2.ROOT, "v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json")))
by = {(x["time"][:4], int(x["time"][6:8]), int(x["time"][9:11])): x for x in sj["outputs"]["hourly"]}
DR = {tuple((k.split("|")[0], int(k.split("|")[1]))): tuple(v) for k, v in json.load(open(os.path.join(HERE, "dayratios.json"))).items()}
years = sorted({k[0] for k in by})
print("2. COVERAGE, TYP, STOP / COMB / EACH")
for lab, c, col in (("RESISTOR-LB NOM", NOM, True), ("RESISTOR-LB WE", WE, True), ("DERATED NOM", cases["DERATED NOM (U3 0.9810)"], False), ("DRAWN NOM", cases["DRAWN NOM"], False)):
    B.COLLAPSE = col
    for n in (9, 14, 15):
        k = [0, 0, 0]
        for y in years:
            for d in range(1, 28):
                for st in (6, 18):
                    seq = [(y, d + (st + i) // 24, (st + i) % 24) for i in range(72)]
                    r = R2.one(n, [by[t]["G(i)"] * DR[(t[0], t[1])][0] for t in seq], B.PR0, c, st, round(min(by[t]["T2m"] for t in seq), 2))
                    k[0] += r["ok"]; k[1] += r["ok"] and r["lo_t"] > 4.2; k[2] += r["ok"] and r["lo_b"] > 4.2 and r["lo_l"] > 4.2
        print("   %-16s 4S%dP: %d / %d / %d" % (lab, n, k[0], k[1], k[2]))
B.COLLAPSE = False
print("3. ELECTRICAL")
for s, lab in ((4.05, "4.05"), (4.00, "4.00")):
    mx = max(s + 0.1, s * 1.025)
    print("   derated %s A: U3 max %.3f; margin with 0.060 %+.3f, with 0.079 %+.3f" % (lab, mx, held_min - mx - 0.060, held_min - mx - 0.079))
print("   proposed margin with 0.060 %+.3f, with 0.079 %+.3f" % (6.793 - 6.355 - 0.060, 6.793 - 6.355 - 0.079))
for i in (5.81, 6.415, 9.37):
    print("   bank at %.3f A: from 5.7 A point %.2f / %.2f / %.2f; from 5.0 A point %.2f / %.2f / %.2f" % (i, 2.10 / 5.7 * i, 2.11 / 5.7 * i, 2.43 / 5.7 * i, 1.85 / 5 * i, 1.86 / 5 * i, 2.14 / 5 * i))
print("   generator rounding: per-ampere ratios 5.7 A %.4f / %.4f, 5.0 A %.4f / %.4f; +-0.005 A on 1.85 is %.2f %%" % (2.10 / 5.7, 2.43 / 5.7, 1.85 / 5, 2.14 / 5, 0.005 / 1.85 * 100))
VB, E = 20.887, 0.93
def pk(iout, vin, l):
    iin = iout * VB / E / vin; d = 1 - vin / VB; return iin, iin + vin * d / (l * 175e3) / 2
for u3 in (5.20, 5.05 * 1.025, 5.30, 5.20 * 1.025):
    iin, p = pk(u3 + 0.060, 9.0, 10e-6 * 0.8 * 0.7)
    print("   U3 input %.3f A at 9 V: front end in %.2f A, L1 peak with both drops %.2f A (%.1f %% of 17.5)" % (u3, iin, p, p / 17.5 * 100))
lo, hi = 9.0, 20.0
for _ in range(40):
    m = 0.5 * (lo + hi)
    if pk(6.415, m, 10e-6 * 0.8 * 0.7)[1] <= 15.75: hi = m
    else: lo = m
print("   the lowest VIN_RAW at which 6.415 A out keeps L1 at 90 %% of 17.5 A: %.2f V" % hi)
print("   Kelvin: 0.371 mOhm working; at 25 C: %.3f (copper 100 C), %.3f (62.1 C); bench 0.29 x 6.0 A = %.2f mV" % (0.371 / (1 + 0.00393 * 75), 0.371 / (1 + 0.00393 * 37.1), 0.29 * 6.0))
