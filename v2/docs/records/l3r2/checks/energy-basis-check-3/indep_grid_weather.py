#!/usr/bin/env python3
"""indep_grid_weather.py: the checker's plane grid and weather windows for CHECK-1 of stream l3plane (an AI check).

Uses indep_balance.py's own balance (beside this file). Plane days from v2/vendor/solar/pvgis-planes/ (40/0 from the
a1solar anchor), each scaled by the 40/0 factor; per-plane TYP / WAB ratios read as printed in plane_grid.out 1.1
(four places; a1solar's figures, taken as inputs). The weather part builds its own 72 h windows from the filed series.
Per-day array ratios: mode 'fixed' holds the 40/0 mean-day ratios on every day (the checker's approximation); mode
'perday' takes a1solar's array model for each day's ratio (array_calc.py, imported ONLY to supply that input).

Usage: python3 indep_grid_weather.py <repo root> [perday]"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import indep_balance as B  # noqa: E402

ROOT = sys.argv[1]
MODE = sys.argv[2] if len(sys.argv) > 2 else "fixed"
SL = (0, 10, 20, 30, 40, 50, 60, 70)
AZ = (-45, -30, -15, 0, 15, 30, 45)
FLOOR = 4.2


def plane_rel(sl, az):
    if (sl, az) == (40, 0):
        return "v2/docs/records/a1solar/inputs/pvgis-leiden-daily-profile-2005-2020.json"
    return "v2/vendor/solar/pvgis-planes/pvgis-leiden-drcalc-2005-2020-slope%d-aspect%d.json" % (sl, az)


def ratios_from_grid_out():
    txt = open(os.path.join(ROOT, "v2/docs/records/l3plane/plane_grid.out"), encoding="utf-8").read()
    sec = txt.split("   1.1 Case P", 1)[1].split("   1.2 ", 1)[0]
    r = {}
    for m in re.finditer(r"^\s+(\d+)\s+([+-]\d+)\s+([\d.]+)\s+(0\.\d{4})\s+(0\.\d{4})", sec, re.M):
        r[(int(m.group(1)), int(m.group(2)))] = (float(m.group(4)), float(m.group(5)), float(m.group(3)))
    return r


def main():
    mj = json.load(open(os.path.join(ROOT, "v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json"), encoding="utf-8"))
    hs = [r["H(i_opt)_m"] for r in mj["outputs"]["monthly"] if r["month"] == 9]
    G40, T40 = B.day(plane_rel(40, 0))
    k = sum(hs) / len(hs) / 30.0 * 1000.0 / sum(G40)
    tl = round(min(T40), 2)
    fe = 0.043 / 0.0062
    nom = dict(vbus=20.000, iin=6.2, e_u3=0.9793, eta_b=0.972, e_st=0.93, e_fe=0.93, chg_eta=0.95,
               r_dsg=0.030, r_chg=0.023, v_ak=0.020, fe_i=fe)
    we = dict(nom, vbus=19.146, iin=6.1, e_u3=0.9733, eta_b=0.963)
    we60 = dict(we, iin=6.0, e_u3=0.9734)
    cases = (("NOM", nom), ("WE", we), ("WE60", we60))
    if MODE == "fixed":
        R = ratios_from_grid_out()
        print("GRID (checker's balance; per-plane ratios from plane_grid.out 1.1). BW = TYP and WAB both meet with the")
        print("lowest combined store above %.1f Wh; T = TYP meets only; - neither." % FLOOR)
        for n in (14, 15):
            for cn, c in cases:
                print("\n4S%dP case %s" % (n, cn))
                print("   slope " + "".join("%6s" % ("%+d" % a) for a in AZ))
                cells = {}
                for sl in SL:
                    row = []
                    for az in AZ:
                        if sl == 0 and az != 0:
                            row.append("%6s" % ".")
                            continue
                        G, _T = B.day(plane_rel(sl, az))
                        rt, rw, _kwh = R[(sl, az)]
                        s_t = B.both(n, [k * g for g in G], B.PR0 * rt, c, tl)
                        s_w = B.both(n, [k * g for g in G], B.PR0 * rw, c, tl)
                        cells[(sl, az)] = (s_t, s_w)
                        cnt = s_t["ok"] and s_w["ok"] and s_t["both"] > FLOOR and s_w["both"] > FLOOR
                        row.append("%6s" % ("BW" if cnt else ("T" if s_t["ok"] else "-")))
                    print("   %5d %s" % (sl, "".join(row)))
                if n == 15 and cn in ("WE", "WE60"):
                    pts = [(30, 0), (30, 15), (40, 0), (40, 15), (50, 0), (50, 15), (20, 0), (60, 0), (30, -15), (30, 30), (40, -15), (40, 30)]
                    print("   spot values TYP/WAB: " + "; ".join("%d/%+d %s/%s" % (sl, az, B.fmt(cells[(sl, az)][0]), B.fmt(cells[(sl, az)][1])) for sl, az in pts))
                if n == 14 and cn == "WE":
                    pts = [(30, 0), (30, 15), (40, 0), (40, 15), (50, 0), (20, 0), (20, 15)]
                    print("   spot values TYP/WAB: " + "; ".join("%d/%+d %s/%s" % (sl, az, B.fmt(cells[(sl, az)][0]), B.fmt(cells[(sl, az)][1])) for sl, az in pts))
        for az in (-45, 45):
            G, _T = B.day(plane_rel(40, az))
            print("   peak hour 40/%+d: %02d UTC (40/0: %02d UTC)" % (az, G.index(max(G)), G40.index(max(G40))))
    # the weather windows
    sj = json.load(open(os.path.join(ROOT, "v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json"), encoding="utf-8"))
    rows = sj["outputs"]["hourly"]
    years = sorted({r["time"][:4] for r in rows})
    by = {}
    for r in rows:
        y, dd, hh = r["time"][:4], int(r["time"][6:8]), int(r["time"][9:11])
        by[(y, dd, hh)] = r
    assert len(by) == len(rows) == 16 * 30 * 24
    mean = [sum(by[(y, d, h)]["G(i)"] for y in years for d in range(1, 31)) / (16 * 30) for h in range(24)]
    print("\nWEATHER: %d rows, %d Septembers; mean day %.4f kWh/m2 (DRcalc 40/0 %.4f); largest hourly difference %.3f W/m2" % (
        len(rows), len(years), sum(mean) / 1000, sum(G40) / 1000, max(abs(mean[h] - G40[h]) for h in range(24))))
    if MODE == "perday":
        rel = os.path.join(ROOT, "v2/docs/records/a1solar")
        sys.path.insert(0, rel)
        import array_calc as AC  # noqa: E402  a1solar's array model, the per-day ratio INPUT only
        import energy_runs as ER  # noqa: E402

        def dayrat(y, d):
            G = [by[(y, d, h)]["G(i)"] for h in range(24)]
            T = [by[(y, d, h)]["T2m"] for h in range(24)]
            if sum(G) <= 0:
                return (1.0, 1.0)
            Rp = ER.Ratios(AC, G, T)
            return (Rp.typical(), Rp.adverse()[0])
    else:
        def dayrat(y, d):
            return (0.9903, 0.9103)
    DR = {(y, d): dayrat(y, d) for y in years for d in range(1, 31)}
    wins = []
    for y in years:
        for d in range(1, 28):
            for st in (6, 18):
                seq = []
                for i in range(72):
                    hh = st + i
                    dd = d + hh // 24
                    seq.append((y, dd, hh % 24))
                wins.append((y, d, st, seq))
    print("windows: %d" % len(wins))
    irr = sorted(sum(by[t]["G(i)"] for t in w[3]) / 1000.0 for w in wins)
    print("72 h irradiation: lowest %.2f, 10th percentile %.2f, median %.2f kWh/m2" % (irr[0], irr[len(irr) // 10], irr[len(irr) // 2]))
    for n in (14, 15):
        for cn, c, bi in (("NOM TYP", nom, 0), ("WE TYP", we, 0), ("WE WAB", we, 1)):
            met = 0
            for y, d, st, seq in wins:
                vals = [by[t]["G(i)"] * DR[(t[0], t[1])][bi] for t in seq]
                t_l = round(min(by[t]["T2m"] for t in seq), 2)
                r = B.run(n, vals, B.PR0, c, st, t_l)
                met += 1 if r["ok"] else 0
            print("   4S%dP %-8s %d of %d (%.1f %%)  [ratios %s]" % (n, cn, met, len(wins), 100.0 * met / len(wins), MODE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
