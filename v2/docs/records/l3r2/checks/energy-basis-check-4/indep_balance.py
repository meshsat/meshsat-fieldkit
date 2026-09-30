#!/usr/bin/env python3
"""indep_balance.py: the checker's own two-pack hourly balance for CHECK-1 of stream l3plane (an AI check).

Written from the model's stated rules and the data files, without importing any record script. Inputs read directly:
energy_inputs.yaml (pack and chain), the PVGIS monthly file (the scale), the DRcalc September day of each plane, the
filed PVGIS seriescalc September rows. The array ratios (TYP, WAB) are a1solar's figures, taken as inputs (printed per
plane to four places in plane_grid.out; the 40/0 pair as energy_basis.out prints it). U3's efficiency per case is taken
from energy_basis.out section 1c/2 (s117's method, not recomputed here).

Usage: python3 indep_balance.py <repo root>   (pure Python, sequential, small)"""
import json
import math
import os
import sys

import yaml

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
Y = yaml.safe_load(open(os.path.join(ROOT, "v2/docs/records/energy/energy_inputs.yaml"), encoding="utf-8"))
PK = Y["pack"]
NS = PK["series"]
CMIN = PK["capacity_min_ah"]["value"]
RATE = PK["rate_factor"]["points"]
TEMP = PK["temperature_factor"]["points"]
VMEAN = PK["mean_v_points"]["points"]
F300 = PK["end_of_discharge"]["fraction_at_3v00"]["points"]
RSOC = PK["end_of_discharge"]["graceful"]["rsoc_reserve"]
AGE = PK["ageing"]["aged_80"]["factor"]
TAPER = PK["charge"]["taper_from_soc"]
CWIN = (PK["charge_window_c"]["low"], PK["charge_window_c"]["high"])
PR0 = Y["solar"]["panel"]["performance_ratio"]["typ"]
LOAD = 42.8
NB = 6
CHG_B = 3.968      # U3 ChargeCurrent code 31
CHG_L = 7.936      # U3B ChargeCurrent code 62
IIN_L = 6.2        # U3B input limit from VBAT
WP, WINDOW = 400.0, 200.0
COLLAPSE = False


def lerp(pts, x):
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def i_cell(p, npar):
    v = NS * 3.6
    for _ in range(3):
        i = p / v / npar
        v = NS * lerp(VMEAN, i)
    return i


def usable(p, t, npar):
    i = i_cell(p, npar)
    return NS * npar * CMIN * lerp(RATE, i) * lerp(TEMP, t) * lerp(VMEAN, i) * min(lerp(F300, i), 1.0 - RSOC) * AGE


def quad_pos(a, b, c):
    """positive root of a x^2 + b x + c = 0 (c <= 0)"""
    if a == 0.0:
        return -c / b
    return (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)


def run(n_lid, prof, pr, case, start, t_l, t_b=20.0, sub=1):
    """One 72 h run; prof is either a 24 value day (repeated) or a 72 value series from the start hour."""
    nt = NB + n_lid
    pb, pl = LOAD * NB / nt, LOAD * n_lid / nt
    fb, fl = usable(pb, t_b, NB), usable(pl, t_l, n_lid)
    vb = NS * lerp(VMEAN, i_cell(pb, NB))
    vl = NS * lerp(VMEAN, i_cell(pl, n_lid))
    capb, capl = CHG_B * vb, CHG_L * vl
    canb = CWIN[0] <= t_b <= CWIN[1]
    canl = CWIN[0] <= t_l <= CWIN[1]
    c = case
    u3cap = c["iin"] * c["vbus"]
    fecap = c["fe_i"] * c["vbus"]
    eb, el = fb, fl
    lo_b, lo_l, lo_t = eb, el, eb + el
    run_on, stop, short = True, None, 0.0
    dt = 1.0 / sub
    k2c = c["r_chg"] / vl ** 2
    k2d = c["r_dsg"] / vl ** 2
    for h in range(72):
        g = prof[(start + h) % 24] if len(prof) == 24 else prof[h]
        p_in = min(WP * g / 1000.0 * pr, WINDOW)
        if COLLAPSE:   # CHECK-4: the collapse bound, the cap or nothing
            psun = min(fecap, u3cap) * c["e_u3"] if p_in * c["e_st"] * c["e_fe"] >= min(fecap, u3cap) else 0.0
        else:
            psun = min(p_in * c["e_st"] * c["e_fe"], fecap, u3cap) * c["e_u3"]
        for _s in range(sub):
            if not run_on and (psun >= LOAD or eb + el >= 0.5 * (fb + fl)):
                run_on = True
            load = LOAD if run_on else 0.0
            if not run_on:
                short += max(0.0, LOAD - psun) * dt
            if psun >= load:
                s = (psun - load) * dt
                socb = eb / fb
                cb = (capb if socb < TAPER else capb * max(0.0, (1 - socb) / (1 - TAPER))) * dt if canb else 0.0
                if canl:
                    socl = el / fl
                    tcap = (capl if socl < TAPER else capl * max(0.0, (1 - socl) / (1 - TAPER))) * dt
                    # node energy U3B draws to put tcap into the lid terminals: (t + t^2 r / v^2 / dt) / eta
                    node_need = (tcap + (tcap / dt) ** 2 * k2c * dt) / c["eta_b"]
                    cl = min(node_need, IIN_L * vb * dt)
                else:
                    cl = 0.0
                ab = min(s * NB / nt, cb)
                al = min(s * n_lid / nt, cl)
                rest = s - ab - al
                ab += min(rest, cb - ab)
                rest = s - ab - al
                al += min(rest, cl - al)
                eb = min(fb, eb + ab * c["chg_eta"])
                if al > 0:
                    # terminal power t from node power a: k2c t^2 + t - a eta = 0 (powers, per hour)
                    tw = quad_pos(k2c, 1.0, -(al / dt) * c["eta_b"]) * dt
                    el = min(fl, el + tw * c["chg_eta"])
            else:
                need = (load - psun) * dt
                # lid energy available at the node over dt: k2d p^2 + (1 + vak/vl) p - el/dt = 0
                avl = quad_pos(k2d, 1.0 + c["v_ak"] / vl, -el / dt) * dt if el > 0 else 0.0
                avb = eb
                db = dl = 0.0
                if avb > 0 and avl > 0:
                    db, dl = min(need * NB / nt, avb), min(need * n_lid / nt, avl)
                else:
                    db = min(need, avb)
                rest = need - db - dl
                x = min(rest, avb - db); db += x; rest -= x
                x = min(rest, avl - dl); dl += x; rest -= x
                if rest > 1e-9:
                    short += rest
                    eb = el = 0.0
                    run_on = False
                    if stop is None:
                        stop = h
                else:
                    eb -= db
                    if dl > 0:
                        pdl = dl / dt
                        el = max(0.0, el - (pdl + pdl * c["v_ak"] / vl + pdl * pdl * k2d) * dt)
            lo_b, lo_l, lo_t = min(lo_b, eb), min(lo_l, el), min(lo_t, eb + el)
    return {"ok": stop is None, "short": short, "lo_b": lo_b, "lo_l": lo_l, "lo_t": lo_t}


def both(n, prof, pr, case, t_l, sub=1):
    rs = [run(n, prof, pr, case, st, t_l, sub=sub) for st in (6, 18)]
    return {"ok": all(r["ok"] for r in rs), "both": min(r["lo_t"] for r in rs), "lid": min(r["lo_l"] for r in rs),
            "base": min(r["lo_b"] for r in rs), "short": max(r["short"] for r in rs)}


def fmt(s):
    return ("%.1f" % s["both"]) if s["ok"] else ("NOT MET %.1f" % s["short"])


def day(rel):
    dj = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
    rows = [r for r in dj["outputs"]["daily_profile"] if r["month"] == 9]
    return [r["G(i)"] for r in rows], [r["T2m"] for r in rows]


def main():
    mj = json.load(open(os.path.join(ROOT, "v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json"), encoding="utf-8"))
    hs = [r["H(i_opt)_m"] for r in mj["outputs"]["monthly"] if r["month"] == 9]
    mean_day = sum(hs) / len(hs) / 30.0
    G40, T40 = day("v2/docs/records/a1solar/inputs/pvgis-leiden-daily-profile-2005-2020.json")
    k = mean_day * 1000.0 / sum(G40)
    prof40 = [k * g for g in G40]
    tl = round(min(T40), 2)
    ch = Y["solar"]["chain"]
    ce = PK["charge"]["energy_efficiency"]
    print("INDEPENDENT BALANCE (checker, AI check). mean day %.4f kWh/m2, scale %.6f, lid at %.2f C, base +20 C" % (mean_day, k, tl))
    print("pack: 4S, Cmin %.2f Ah, aged %.2f, reserve %.2f, taper %.2f, charge eta %.2f; chain %.2f / %.2f" % (
        CMIN, AGE, RSOC, TAPER, ce["value"], ch[0]["eta"], ch[1]["eta"]))
    fe_draft = 0.043 / 0.0062
    nom = dict(vbus=20.000, iin=6.2, e_u3=0.9793, eta_b=0.972, e_st=0.93, e_fe=0.93, chg_eta=0.95,
               r_dsg=0.030, r_chg=0.023, v_ak=0.020, fe_i=fe_draft)
    we = dict(nom, vbus=19.146, iin=6.1, e_u3=0.9733, eta_b=0.963)
    we60 = dict(we, iin=6.0, e_u3=0.9734)
    wa = dict(we60, e_st=0.90, e_fe=0.90, chg_eta=0.90, r_dsg=0.045, r_chg=0.040, v_ak=0.029)
    gen = dict(nom, iin=4.15, e_u3=0.9810, fe_i=0.043 / 0.010)
    m207 = dict(nom, vbus=20.7, iin=6.1, e_u3=0.979)
    sc76 = dict(m207, vbus=19.08)
    cases = [("NOM", nom), ("WE", we), ("WE60", we60), ("WA", wa), ("GEN", gen), ("M207", m207), ("SC76", sc76)]
    RAT = {"TYP": 0.9903, "WAB": 0.9103}
    print("\n1. 40/0 CASES (ratios TYP 0.9903, WAB 0.9103 to four places): lowest store both / lid / base, or NOT MET unserved")
    res = {}
    for n in (9, 14, 15):
        for nm, c in cases:
            row = []
            for b in ("TYP", "WAB"):
                s = both(n, prof40, PR0 * RAT[b], c, tl)
                res[(n, nm, b)] = s
                row.append(("%s (lid %.1f, base %.1f)" % (fmt(s), s["lid"], s["base"])) if s["ok"] else fmt(s))
            print("   4S%dP %-5s TYP %-32s WAB %s" % (n, nm, row[0], row[1]))
    print("\n1b. STEP SENSITIVITY at 40/0: hourly vs 0.1 h and 0.01 h sub-steps (same hourly irradiance)")
    for n in (14, 15):
        for nm, c in (("NOM", nom), ("WE", we), ("WE60", we60)):
            for b in ("TYP", "WAB"):
                a1 = both(n, prof40, PR0 * RAT[b], c, tl)
                a10 = both(n, prof40, PR0 * RAT[b], c, tl, sub=10)
                a100 = both(n, prof40, PR0 * RAT[b], c, tl, sub=100)
                print("   4S%dP %-5s %s: 1 h %-14s 0.1 h %-14s 0.01 h %-14s" % (n, nm, b, fmt(a1), fmt(a10), fmt(a100)))
    print("\n2. POWER INTO U3 (bus x limit), NOM otherwise, 40/0")
    for pw in range(108, 132, 2):
        cells = []
        for n in (14, 15):
            for b in ("TYP", "WAB"):
                c = dict(nom, iin=pw / 20.0)
                cells.append("%-14s" % fmt(both(n, prof40, PR0 * RAT[b], c, tl)))
        print("   %5.1f W  %s" % (pw, " ".join(cells)))
    print("\n3. ONE AT A TIME FROM NOM, TYP, 40/0")
    for n in (14, 15):
        b0 = both(n, prof40, PR0 * RAT["TYP"], nom, tl)["both"]
        for lab, c in (("bus 19.146 (U3 0.9796)", dict(nom, vbus=19.146, e_u3=0.9796)), ("limit 6.0 (U3 0.9795)", dict(nom, iin=6.0, e_u3=0.9795)),
                       ("chg eta 0.90", dict(nom, chg_eta=0.90)), ("stage 0.90", dict(nom, e_st=0.90)), ("U3B 0.963", dict(nom, eta_b=0.963))):
            s = both(n, prof40, PR0 * RAT["TYP"], c, tl)
            print("   4S%dP %-26s %-14s delta %+.1f" % (n, lab, fmt(s), (s["both"] if s["ok"] else -s["short"]) - b0))
        s = both(n, prof40, PR0 * RAT["WAB"], nom, tl)
        print("   4S%dP %-26s %-14s delta %+.1f" % (n, "WAB build", fmt(s), (s["both"] if s["ok"] else -s["short"]) - b0))
    print("\n3b. WHERE THE PACK CHARGE EFFICIENCY BINDS: WE, both builds, chg eta 0.90 / 0.95 / 0.98")
    for n in (14, 15):
        for b in ("TYP", "WAB"):
            print("   4S%dP %s: %s" % (n, b, " / ".join(fmt(both(n, prof40, PR0 * RAT[b], dict(we, chg_eta=x), tl)) for x in (0.90, 0.95, 0.98))))
    print("\n3c. THE BUS BELOW THE FILED RANGE (WE otherwise; U3 held at 0.9733): 19.072 V (a 20 K board rise at the divider) and 18.782 V (the endurance limits added)")
    for n in (14, 15):
        for b in ("TYP", "WAB"):
            print("   4S%dP %s: %s" % (n, b, " / ".join(fmt(both(n, prof40, PR0 * RAT[b], dict(we, vbus=v), tl)) for v in (19.146, 19.072, 18.782))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
