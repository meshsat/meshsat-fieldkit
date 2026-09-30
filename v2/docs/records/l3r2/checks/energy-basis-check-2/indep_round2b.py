#!/usr/bin/env python3
"""indep_round2b.py: two small follow-ups for CHECK-2 (an AI check): the Samsung resistive bound with each kit's own
discharge current, and WE-MKR's coverage with it. Usage: python3 indep_round2b.py <repo root>"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import indep_round2 as R2  # noqa: E402  (reads sys.argv[1])
B = R2.B
v02 = 12.62 / 3.482; r = 0.0345; ocv = v02 + 0.2 * 3.482 * r
print("OCV %.4f V" % ocv)
for lab, ichg, nt in (("base 4S6P in 4S20P", 3.968 / 6, 20), ("base 4S6P in 4S21P", 3.968 / 6, 21), ("base, the page's 12 parallel", 3.968 / 6, 12),
                      ("lid 4S14P", 7.936 / 14, 20), ("lid 4S15P", 7.936 / 15, 21)):
    idis = 42.8 / (4 * v02) / nt
    print("   %-30s charge %.3f A, discharge %.3f A: %.4f" % (lab, ichg, idis, (ocv - idis * r) / (ocv + ichg * r)))
sj = json.load(open(os.path.join(R2.ROOT, "v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json")))
by = {(x["time"][:4], int(x["time"][6:8]), int(x["time"][9:11])): x for x in sj["outputs"]["hourly"]}
DR = {tuple((k.split("|")[0], int(k.split("|")[1]))): tuple(v) for k, v in json.load(open(os.path.join(HERE, "dayratios.json"))).items()}
years = sorted({k[0] for k in by})
for n in (14, 15):
    for ce in (0.9915, 0.9925):
        c = dict(R2.WE, e_st=0.965, e_fe=0.978, chg_eta=ce)
        k = 0
        for y in years:
            for d in range(1, 28):
                for st in (6, 18):
                    seq = [(y, d + (st + i) // 24, (st + i) % 24) for i in range(72)]
                    rr = R2.one(n, [by[t]["G(i)"] * DR[(t[0], t[1])][0] for t in seq], B.PR0, c, st, round(min(by[t]["T2m"] for t in seq), 2))
                    k += rr["ok"]
        print("   4S%dP WE-MKR TYP, charge %.4f: STOP %d (%.1f %%)" % (n, ce, k, 100.0 * k / 864))
print("step error at WE restated (1 h against 0.01 h), lowest combined / lid:")
for n, sl, az, bi in ((15, 40, 0, 1), (15, 50, 15, 1), (15, 40, 0, 0), (14, 40, 0, 0)):
    pf = R2.prof(sl, az); pr = B.PR0 * R2.RAT[(sl, az)][bi]
    out = []
    for sub in (1, 100):
        B.LOAD = 42.8 + R2.DRAIN
        rs = [B.run(n, pf, pr, R2.WE, st, R2.TL, sub=sub) for st in (6, 18)]
        B.LOAD = 42.8
        out.append("%s %.1f / %.1f" % ("ok" if all(x["ok"] for x in rs) else "NOT", min(x["lo_t"] for x in rs), min(x["lo_l"] for x in rs)))
    print("   4S%dP %d/%+d %s: %s" % (n, sl, az, "TYP" if bi == 0 else "WAB", "  ->  ".join(out)))
