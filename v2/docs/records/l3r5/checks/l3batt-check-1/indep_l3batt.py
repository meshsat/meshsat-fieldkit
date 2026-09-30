#!/usr/bin/env python3
"""indep_l3batt.py: CHECK-1 of fnd/l3batt (an AI check). The checker's own two-pack balance (../chk-energy/indep_balance.py,
indep_round2.py; no record script imported) on the both-kept store (base 4S6P + lid 4S9P of 35E). Usage: python3 indep_l3batt.py <repo>"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "chk-energy"))
import indep_round2 as R2  # noqa: E402
B = R2.B
p40, r40, TL = R2.prof(40, 0), R2.RAT[(40, 0)], R2.TL
NOM, WE = R2.NOM, R2.WE
NOM90 = dict(NOM, e_st=0.90, e_fe=0.90, chg_eta=0.90)
WE90 = dict(WE, e_st=0.90, e_fe=0.90, chg_eta=0.90)
DRAWN = dict(NOM, iin=4.15, e_u3=0.9810, fe_i=4.212 - 0.060)
print("1. BATTERY ONLY (the checker's usable, no path loss on the lid share)")
for lab, parts in (("4S3P alone", ((42.8, 3),)), ("base 4S6P + lid 4S9P", ((42.8 * 6 / 15, 6), (42.8 * 9 / 15, 9)))):
    for t in (20.0, -10.0):
        u = sum(B.usable(p, t, n) for p, n in parts)
        print("   %-22s %+5.0f C: %.1f Wh, %.2f h at 42.8 W" % (lab, t, u, u / 42.8))
ub, ul = B.usable(42.8 * 6 / 15, 20.0, 6), B.usable(42.8 * 9 / 15, TL, 9)
print("2. THE DUSK STORE: base %.1f Wh (+20 C) + lid %.1f Wh (%.2f C) = %.1f Wh" % (ub, ul, TL, ub + ul))
dark = [h for h in range(24) if p40[h] <= 60.0]
node = [min(400 * p40[h] / 1000 * B.PR0 * r40[0], 200) * 0.93 * 0.93 * 0.9793 for h in range(24)]
need = sum(max(0.0, 42.8 - node[h]) for h in dark)
print("   hours at or under 60 W/m2: %s (%d); the night's deficit at the node, TYP NOM: %.1f Wh (%.1f Wh at 42.8 W flat)" % (dark, len(dark), need, 42.8 * len(dark)))
def runs(n, c, bi, hours):
    out = []
    for st in (6, 18):
        B.LOAD = 42.8 + c.get("drain", 0.0)
        tr = []
        r = B.run(n, p40, B.PR0 * r40[bi], c, st, TL, trace=tr, hours=hours)
        B.LOAD = 42.8
        stop = next((h for h, hh, eb, el, on, ps in tr if not on), None)
        out.append((r, stop, (st + stop) % 24 if stop is not None else None))
    return out
print("3. BATTERY PLUS SOLAR, 4S9P lid")
for hours in (48, 72):
    for lab, c in (("DRAWN", DRAWN), ("NOM", NOM), ("NOM90", NOM90), ("WE", WE), ("WE90", WE90)):
        cells = []
        for bi, b in ((0, "TYP"), (1, "WAB")):
            o = runs(9, c, bi, hours)
            ok = all(x[0]["ok"] for x in o)
            cells.append("%s %s" % (b, ("MEETS %.1f" % min(x[0]["lo_t"] for x in o)) if ok else "NOT MET %.1f, stops h %s/%s (UTC %s)" % (
                max(x[0]["short"] for x in o), o[0][1], o[1][1], "/".join("%02d" % x[2] for x in o))))
        print("   %d h %-6s %s" % (hours, lab, "; ".join(cells)))
print("4. THE LEAST LID (base 4S6P), COMB and no stop, both starts")
def least(c, bi, hours):
    def ok(x):
        o = runs(x, c, bi, hours)
        return all(r["ok"] and r["lo_t"] > 4.2 for r, s, u in o)
    lo, hi = 9.0, 30.0
    for _ in range(30):
        m = 0.5 * (lo + hi)
        if ok(m): hi = m
        else: lo = m
    return hi
for hours, lab, c, bi in ((48, "NOM TYP", NOM, 0), (72, "NOM TYP", NOM, 0), (48, "WE TYP", WE, 0), (72, "WE TYP", WE, 0), (72, "NOM90 TYP", NOM90, 0), (72, "WE WAB", WE, 1), (48, "WE WAB", WE, 1)):
    x = least(c, bi, hours)
    add = B.usable(42.8 * x / (6 + x), TL, x) - B.usable(42.8 * 9 / 15, TL, 9)
    print("   %d h %-10s lid 4S%.2fP: +%.1f cells, +%.1f Wh usable at the lid (at 4S9P's share: +%.1f Wh)" % (
        hours, lab, x, 4 * (x - 9), add, B.usable(42.8 * 9 / 15, TL, 9) / 9 * (x - 9)))
print("5. COVERAGE, 4S9P lid, TYP, NOM (864 windows; 48 h = the first 48 h of each)")
sj = json.load(open(os.path.join(R2.ROOT, "v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json")))
by = {(x["time"][:4], int(x["time"][6:8]), int(x["time"][9:11])): x for x in sj["outputs"]["hourly"]}
DR = {tuple((k.split("|")[0], int(k.split("|")[1]))): tuple(v) for k, v in json.load(open(os.path.join(HERE, "..", "chk-energy", "dayratios.json"))).items()}
years = sorted({k[0] for k in by})
for hours in (48, 72):
    k = 0
    for y in years:
        for d in range(1, 28):
            for st in (6, 18):
                seq = [(y, d + (st + i) // 24, (st + i) % 24) for i in range(72)]
                r = B.run(9, [by[t]["G(i)"] * DR[(t[0], t[1])][0] for t in seq], B.PR0, NOM, st, round(min(by[t]["T2m"] for t in seq[:hours]), 2), hours=hours)
                k += r["ok"]
    print("   %d h: kept %d of 864" % (hours, k))
print("6. HF RECEIVING (+1.14 W), 72 h WE TYP, the least lid")
B.LOAD = 42.8
WEH = dict(WE, drain=WE["drain"] + 1.14)
x = least(WEH, 0, 72)
print("   lid 4S%.2fP (+%.1f cells over 4S9P; +%.1f Wh usable at the lid)" % (x, 4 * (x - 9), B.usable(43.94 * x / (6 + x), TL, x) - B.usable(43.94 * 9 / 15, TL, 9)))
