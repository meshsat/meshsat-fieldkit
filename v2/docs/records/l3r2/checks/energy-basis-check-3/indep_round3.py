#!/usr/bin/env python3
"""indep_round3.py: CHECK-3 task 1 (an AI check): WE-MKR coverage at the corrected charge bound 0.9924, all three lines, on
the checker's balance. Usage: python3 indep_round3.py <repo root>"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import indep_round2 as R2  # noqa: E402
B = R2.B
sj = json.load(open(os.path.join(R2.ROOT, "v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json")))
by = {(x["time"][:4], int(x["time"][6:8]), int(x["time"][9:11])): x for x in sj["outputs"]["hourly"]}
DR = {tuple((k.split("|")[0], int(k.split("|")[1]))): tuple(v) for k, v in json.load(open(os.path.join(HERE, "dayratios.json"))).items()}
years = sorted({k[0] for k in by})
for n in (14, 15):
    c = dict(R2.WE, e_st=0.965, e_fe=0.978, chg_eta=0.9924)
    k = [0, 0, 0]
    for y in years:
        for d in range(1, 28):
            for st in (6, 18):
                seq = [(y, d + (st + i) // 24, (st + i) % 24) for i in range(72)]
                r = R2.one(n, [by[t]["G(i)"] * DR[(t[0], t[1])][0] for t in seq], B.PR0, c, st, round(min(by[t]["T2m"] for t in seq), 2))
                k[0] += r["ok"]; k[1] += r["ok"] and r["lo_t"] > 4.2; k[2] += r["ok"] and r["lo_b"] > 4.2 and r["lo_l"] > 4.2
    print("4S%dP WE-MKR TYP, charge 0.9924: STOP %d (%.1f %%), COMB %d (%.1f %%), EACH %d (%.1f %%)" % (n, k[0], k[0] / 8.64, k[1], k[1] / 8.64, k[2], k[2] / 8.64))
print("cell multiples with the corrected counts: TYP %s; WAB %s" % (", ".join("%.2f" % (c / 84.0) for c in (128, 172, 220)), ", ".join("%.2f" % (c / 84.0) for c in (136, 184, 228))))
print("with CHECK-2's old counts: %s" % ", ".join("%.2f" % (c / 84.0) for c in (132, 168, 228, 136, 192, 232)))
