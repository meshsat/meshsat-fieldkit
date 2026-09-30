#!/usr/bin/env python3
"""indep_round2.py: the checker's runs for CHECK-2 of stream l3plane (an AI check), on the checker's own balance
(indep_balance.py beside this file; no record script imported except a1solar's array model, used ONLY to supply each
day's TYP / WAB ratio as an input, as in CHECK-1).

Usage: python3 indep_round2.py <repo root>"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import indep_balance as B  # noqa: E402

ROOT = sys.argv[1]
sys.argv = [sys.argv[0], ROOT]
import indep_grid_weather as GW  # noqa: E402

FLOOR = 4.2
DRAIN = 1.8 / 72.0
mj = json.load(open(os.path.join(ROOT, "v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json"), encoding="utf-8"))
hs = [r["H(i_opt)_m"] for r in mj["outputs"]["monthly"] if r["month"] == 9]
G40, T40 = B.day(GW.plane_rel(40, 0))
K = sum(hs) / len(hs) / 30.0 * 1000.0 / sum(G40)
TL = round(min(T40), 2)
RAT = GW.ratios_from_grid_out()
FE = 0.043 / 0.0062
NOM = dict(vbus=20.000, iin=6.2, e_u3=0.9793, eta_b=0.972, e_st=0.93, e_fe=0.93, chg_eta=0.95, r_dsg=0.030, r_chg=0.023,
           v_ak=0.020, fe_i=FE, drain=0.0)
WE = dict(NOM, vbus=19.146, iin=6.1, e_u3=0.9733, eta_b=0.963, v_ak=0.029, r_dsg=0.045, r_chg=0.040, drain=DRAIN)


def prof(sl, az):
    return [K * g for g in B.day(GW.plane_rel(sl, az))[0]]


def both(n, pf, pr, c, t_l=TL, wp=400.0):
    B.LOAD = 42.8 + c.get("drain", 0.0)
    B.WP = wp
    try:
        rs = [B.run(n, pf, pr, c, st, t_l) for st in (6, 18)]
    finally:
        B.LOAD, B.WP = 42.8, 400.0
    return {"ok": all(r["ok"] for r in rs), "both": min(r["lo_t"] for r in rs), "base": min(r["lo_b"] for r in rs),
            "lid": min(r["lo_l"] for r in rs), "short": max(r["short"] for r in rs)}


def one(n, vals, pr, c, st, t_l, wp=400.0):
    B.LOAD = 42.8 + c.get("drain", 0.0)
    B.WP = wp
    try:
        return B.run(n, vals, pr, c, st, t_l)
    finally:
        B.LOAD, B.WP = 42.8, 400.0


def fmt(s):
    return ("%.1f (base %.1f, lid %.1f)" % (s["both"], s["base"], s["lid"])) if s["ok"] else ("NOT MET %.1f" % s["short"])


def metric(s):
    return s["both"] if s["ok"] else -s["short"]


def passes(n, c, sl, az, line):
    for i in (0, 1):
        s = both(n, prof(sl, az), B.PR0 * RAT[(sl, az)][i], c)
        if not s["ok"]:
            return False
        if line == "COMB" and not s["both"] > FLOOR:
            return False
        if line == "EACH" and not (s["base"] > FLOOR and s["lid"] > FLOOR):
            return False
    return True


def thresh(n, sl, az, line, key, lo, hi, extra=None):
    def ok(x):
        c = dict(WE, **{key: x})
        if extra:
            c.update(extra(x))
        return passes(n, c, sl, az, line)
    if not ok(hi):
        return None
    if ok(lo):
        return lo
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi


def main():
    print("CHECK-2 RUNS (checker's balance). drain %.4f W; lid %.2f C; ratios 40/0 TYP %.4f WAB %.4f" % (DRAIN, TL, RAT[(40, 0)][0], RAT[(40, 0)][1]))
    p40 = prof(40, 0)
    r40 = RAT[(40, 0)]
    print("\n1. WE RESTATED AND ITS NEIGHBOURS ON 40/0 (TYP ; WAB)")
    cases = [("NOM", NOM), ("WE", WE), ("WE60", dict(WE, iin=6.0, e_u3=0.9734)), ("WEL", dict(WE, vbus=18.782, e_u3=0.9735)),
             ("WA", dict(WE, iin=6.0, e_u3=0.9734, e_st=0.90, e_fe=0.90, chg_eta=0.90))]
    for n in (9, 14, 15):
        for nm, c in cases:
            print("   4S%dP %-5s %-36s ; %s" % (n, nm, fmt(both(n, p40, B.PR0 * r40[0], c)), fmt(both(n, p40, B.PR0 * r40[1], c))))
    print("\n2. ONE AT A TIME FROM WE, 40/0: change in the lowest combined store (NOT MET = minus unserved)")
    terms = [("charge 0.90", dict(chg_eta=0.90)), ("bus 18.782 (U3 0.9735)", dict(vbus=18.782, e_u3=0.9735)),
             ("bus 19.101 (U3 0.9733)", dict(vbus=19.101, e_u3=0.9733)), ("stage 0.90", dict(e_st=0.90)), ("front end 0.90", dict(e_fe=0.90)),
             ("U3 6.0 A (0.9734)", dict(iin=6.0, e_u3=0.9734)), ("U3B 0.972", dict(eta_b=0.972)), ("no drain", dict(drain=0.0)),
             ("V(AK) 20 mV", dict(v_ak=0.020)), ("loops nominal", dict(r_dsg=0.030, r_chg=0.023))]
    for n in (14, 15):
        for bi, b in ((0, "TYP"), (1, "WAB")):
            s0 = both(n, p40, B.PR0 * r40[bi], WE)
            parts = ["%s %+.1f" % (lab, metric(both(n, p40, B.PR0 * r40[bi], dict(WE, **ov))) - metric(s0)) for lab, ov in terms]
            if b == "TYP":
                parts.append("WAB build %+.1f" % (metric(both(n, p40, B.PR0 * r40[1], WE)) - metric(s0)))
            print("   4S%dP %s (%s): %s" % (n, b, fmt(s0), "; ".join(parts)))
    print("\n3. THRESHOLDS FROM WE (each alone; both builds pass the line)")
    for n, sl, az, line in ((15, 50, 15, "COMB"), (15, 40, 0, "COMB"), (15, 40, 0, "EACH"), (15, 30, 0, "COMB"), (14, 40, 0, "COMB"), (14, 50, 0, "COMB"), (14, 40, 0, "EACH")):
        tc = thresh(n, sl, az, line, "chg_eta", 0.85, 1.0)
        ts = thresh(n, sl, az, line, "e_st", 0.80, 1.0)
        ti = thresh(n, sl, az, line, "iin", 5.8, 6.35)
        print("   4S%dP %d/%+d %s: charge %s; stage %s; U3 limit (eta held) %s" % (n, sl, az, line,
              "none" if tc is None else "%.3f" % tc, "none" if ts is None else "%.3f" % ts, "none" if ti is None else "%.3f" % ti))
    print("\n4. THE WE BAND ON COMB AND EACH, 4S15P and 4S14P (B = both builds pass)")
    for n in (14, 15):
        for line in ("COMB", "EACH"):
            rows = []
            for sl in GW.SL:
                row = ""
                for az in GW.AZ:
                    if sl == 0 and az != 0:
                        row += "    ."
                        continue
                    row += "%5s" % ("B" if passes(n, WE, sl, az, line) else "-")
                rows.append("      %2d %s" % (sl, row))
            print("   4S%dP %s\n%s" % (n, line, "\n".join(rows)))
    # weather
    sj = json.load(open(os.path.join(ROOT, "v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json"), encoding="utf-8"))
    by = {}
    for r in sj["outputs"]["hourly"]:
        by[(r["time"][:4], int(r["time"][6:8]), int(r["time"][9:11]))] = r
    years = sorted({k[0] for k in by})
    cache = os.path.join(HERE, "dayratios.json")
    if os.path.exists(cache):
        DR = {tuple((k.split("|")[0], int(k.split("|")[1]))): tuple(v) for k, v in json.load(open(cache)).items()}
    else:
        sys.path.insert(0, os.path.join(ROOT, "v2/docs/records/a1solar"))
        import array_calc as AC  # noqa: E402
        import energy_runs as ER  # noqa: E402
        DR = {}
        for y in years:
            for d in range(1, 31):
                G = [by[(y, d, h)]["G(i)"] for h in range(24)]
                T = [by[(y, d, h)]["T2m"] for h in range(24)]
                Rp = ER.Ratios(AC, G, T)
                DR[(y, d)] = (Rp.typical(), Rp.adverse()[0])
        json.dump({"%s|%d" % k: v for k, v in DR.items()}, open(cache, "w"))
    wins = []
    for y in years:
        for d in range(1, 28):
            for st in (6, 18):
                seq = [(y, d + (st + i) // 24, (st + i) % 24) for i in range(72)]
                wins.append((y, d, st, seq, round(min(by[t]["T2m"] for t in seq), 2)))
    last = wins[-1][3][-1]
    print("\n5. WEATHER: %d windows; the last window ends %s-09-%02d %02d:11 UTC" % (len(wins), last[0], last[1], last[2]))
    wcases = [("WE TYP", WE, 0, 400.0), ("WE WAB", WE, 1, 400.0), ("NOM TYP", NOM, 0, 400.0),
              ("WE-LO TYP", dict(WE, e_st=0.90, e_fe=0.90, chg_eta=0.90), 0, 400.0),
              ("WE-MKR TYP", dict(WE, e_st=0.965, e_fe=0.978, chg_eta=0.9915), 0, 400.0),
              ("WE TYP link off", dict(WE, drain=DRAIN - 5.9), 0, 400.0), ("WE TYP 600 Wp", WE, 0, 600.0)]
    for n in (9, 14, 15):
        for lab, c, bi, wp in wcases:
            if n == 9 and lab not in ("WE TYP", "WE WAB", "NOM TYP", "WE-MKR TYP"):
                continue
            if lab in ("WE TYP link off", "WE TYP 600 Wp") and n == 9:
                continue
            k = [0, 0, 0]
            for y, d, st, seq, t_l in wins:
                vals = [by[t]["G(i)"] * DR[(t[0], t[1])][bi] for t in seq]
                r = one(n, vals, B.PR0, c, st, t_l, wp)
                k[0] += r["ok"]
                k[1] += r["ok"] and r["lo_t"] > FLOOR
                k[2] += r["ok"] and r["lo_b"] > FLOOR and r["lo_l"] > FLOOR
            print("   4S%dP %-16s STOP %3d (%.1f %%)  COMB %3d (%.1f %%)  EACH %3d (%.1f %%)" % (
                n, lab, k[0], 100.0 * k[0] / 864, k[1], 100.0 * k[1] / 864, k[2], 100.0 * k[2] / 864))
    for n in (14, 15):
        for lab, c, wp in (("link off", dict(WE, drain=DRAIN - 5.9), 400.0), ("600 Wp", WE, 600.0)):
            print("   mean-day margin 4S%dP %s: TYP %s ; WAB %s" % (n, lab, fmt(both(n, p40, B.PR0 * r40[0], c, wp=wp)), fmt(both(n, p40, B.PR0 * r40[1], c, wp=wp))))
    # sizing
    print("\n6. SIZING: least lid parallel count per window passing COMB at WE (base 4S6P), by bisection; usable at the window's lid temperature")

    def bis(ok):
        lo, hi = 1.0, 400.0
        if ok(lo):
            return lo
        if not ok(hi):
            return None
        for _ in range(20):
            mid = 0.5 * (lo + hi)
            if ok(mid):
                hi = mid
            else:
                lo = mid
        return hi

    def store(x, t_l):
        B.LOAD = 42.8 + DRAIN
        try:
            nt = 6 + x
            return B.usable(B.LOAD * 6 / nt, 20.0, 6) + B.usable(B.LOAD * x / nt, t_l, x)
        finally:
            B.LOAD = 42.8
    base21 = store(15, TL)
    print("   the 4S21P kit's usable at WE on the mean day: %.1f Wh (nominal %.1f Wh)" % (base21, 84 * 3.35 * 3.6))
    for bi, b in ((0, "TYP"), (1, "WAB")):
        def okm(x, bi=bi):
            return all((lambda r: r["ok"] and r["lo_t"] > FLOOR)(one(x, p40, B.PR0 * r40[bi], WE, st, TL)) for st in (6, 18))
        xm = bis(okm)
        um = store(xm, TL)
        res = []
        for y, d, st, seq, t_l in wins:
            vals = [by[t]["G(i)"] * DR[(t[0], t[1])][bi] for t in seq]

            def okw(x, vals=vals, st=st, t_l=t_l):
                r = one(x, vals, B.PR0, WE, st, t_l)
                return r["ok"] and r["lo_t"] > FLOOR
            x = bis(okw)
            res.append((store(x, t_l), x))
        by_u = sorted(res, key=lambda z: z[0])
        by_x = sorted(res, key=lambda z: z[1])
        print("   %s mean day: lid 4S%.2fP -> 4S%dP, %d cells, usable %.1f Wh (%.2f x)" % (b, xm, math.ceil(xm - 1e-9), 24 + 4 * math.ceil(xm - 1e-9), um, um / base21))
        for tgt in (50, 80, 95):
            k = int(math.ceil(tgt / 100.0 * 864)) - 1
            u, x = by_u[k]
            xs = by_x[k][1]
            cells, cells_x = 24 + 4 * math.ceil(x - 1e-9), 24 + 4 * math.ceil(xs - 1e-9)
            print("   %s %d %%: usable %.1f Wh (%.2f x 4S21P), its lid 4S%.2fP -> %d cells (%.2f x 84, %.2f kg); percentile of the count itself 4S%.2fP -> %d cells" % (
                b, tgt, u, u / base21, x, cells, cells / 84.0, cells * 0.05, xs, cells_x))
        cov84 = sum(1 for u, x in res if x <= 15.0 + 1e-9)
        print("   %s: windows whose need fits 4S15P (84 cells): %d (%.1f %%); median need %.1f Wh, largest %.1f Wh" % (
            b, cov84, 100.0 * cov84 / 864, by_u[432][0], by_u[-1][0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
