#!/usr/bin/env python3
"""indep_round5.py: CHECK-5 (an AI check): the derated variant at 4.00 A (NOM) and 3.90 A (WE) on the checker's balance, its
coverage, and L1's peak at the 5.05 A setting. U3's efficiency at these settings is not recomputed; a bracket is shown.
Usage: python3 indep_round5.py <repo root>"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import indep_round2 as R2  # noqa: E402
B = R2.B
p40, r40 = R2.prof(40, 0), R2.RAT[(40, 0)]
fe_held = 4.212 - 0.060
for lab, base, iin, etas in (("DERATED NOM 4.00 A", R2.NOM, 4.00, (0.9810, 0.9815)), ("DERATED WE 3.90 A", R2.WE, 3.90, (0.9740, 0.9750))):
    for e in etas:
        c = dict(base, iin=iin, e_u3=e, fe_i=fe_held)
        print("%s, U3 %.4f: %s" % (lab, e, "; ".join("4S%dP %s / %s" % (n, B.fmt(R2.both(n, p40, B.PR0 * r40[0], c)), B.fmt(R2.both(n, p40, B.PR0 * r40[1], c))) for n in (9, 14, 15))))
sj = json.load(open(os.path.join(R2.ROOT, "v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json")))
by = {(x["time"][:4], int(x["time"][6:8]), int(x["time"][9:11])): x for x in sj["outputs"]["hourly"]}
DR = {tuple((k.split("|")[0], int(k.split("|")[1]))): tuple(v) for k, v in json.load(open(os.path.join(HERE, "dayratios.json"))).items()}
years = sorted({k[0] for k in by})
c = dict(R2.NOM, iin=4.00, e_u3=0.9810, fe_i=fe_held)
for n in (9, 14, 15):
    k = [0, 0, 0]
    for y in years:
        for d in range(1, 28):
            for st in (6, 18):
                seq = [(y, d + (st + i) // 24, (st + i) % 24) for i in range(72)]
                r = R2.one(n, [by[t]["G(i)"] * DR[(t[0], t[1])][0] for t in seq], B.PR0, c, st, round(min(by[t]["T2m"] for t in seq), 2))
                k[0] += r["ok"]; k[1] += r["ok"] and r["lo_t"] > 4.2; k[2] += r["ok"] and r["lo_b"] > 4.2 and r["lo_l"] > 4.2
    print("coverage DERATED NOM 4.00 A, 4S%dP TYP: %d / %d / %d of 864" % (n, k[0], k[1], k[2]))
VB, E = 20.887, 0.93
mx = max(5.05 + 0.1, 5.05 * 1.025)
iin = (mx + 0.060) * VB / E / 9.0
rip = 9.0 * (1 - 9.0 / VB) / (10e-6 * 0.8 * 0.7 * 175e3)
print("L1 at the 5.05 A setting: U3 max %.3f A, front end in %.2f A, peak %.2f A, %.1f %% of 17.5 A; 5.20 / 1.025 = %.3f; the exact 90 %% input %.4f / 1.025 = %.4f" % (
    mx, iin, iin + rip / 2, (iin + rip / 2) / 17.5 * 100, 5.20 / 1.025, (15.75 - rip / 2) * E * 9 / VB - 0.060, ((15.75 - rip / 2) * E * 9 / VB - 0.060) / 1.025))
print("4.00 A: max %.3f, margins %+.3f / %+.3f; 4.05 A: %+.3f / %+.3f" % (max(4.1, 4.0 * 1.025), 4.212 - 4.1 - 0.060, 4.212 - 4.1 - 0.079, 4.212 - 4.15125 - 0.060, 4.212 - 4.15125 - 0.079))
