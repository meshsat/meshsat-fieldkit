#!/usr/bin/env python3
"""indep_extra.py: the checker's extra runs on its own balance (CHECK-1, an AI check): WE with each WA term alone, the
pack charge efficiency threshold at WE, and the excluded lid-path drain. Usage: python3 indep_extra.py <repo root>"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indep_balance as B
import indep_grid_weather as GW  # noqa: F401  (plane_rel, ratios)

ROOT = sys.argv[1]
import json
mj = json.load(open(os.path.join(ROOT, "v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json"), encoding="utf-8"))
hs = [r["H(i_opt)_m"] for r in mj["outputs"]["monthly"] if r["month"] == 9]
G40, T40 = B.day(GW.plane_rel(40, 0))
k = sum(hs) / len(hs) / 30.0 * 1000.0 / sum(G40)
tl = round(min(T40), 2)
R = GW.ratios_from_grid_out()
fe = 0.043 / 0.0062
nom = dict(vbus=20.000, iin=6.2, e_u3=0.9793, eta_b=0.972, e_st=0.93, e_fe=0.93, chg_eta=0.95, r_dsg=0.030, r_chg=0.023, v_ak=0.020, fe_i=fe)
we = dict(nom, vbus=19.146, iin=6.1, e_u3=0.9733, eta_b=0.963)
we60 = dict(we, iin=6.0, e_u3=0.9734)
prof = lambda sl, az: [k * g for g in B.day(GW.plane_rel(sl, az))[0]]
print("1. WE (and WE60) with each WA term alone, 40/0, TYP / WAB")
for base_n, base in (("WE", we), ("WE60", we60)):
    for lab, ov in (("none", {}), ("stage 0.90", dict(e_st=0.90)), ("front end 0.90", dict(e_fe=0.90)), ("charge eta 0.90", dict(chg_eta=0.90)),
                    ("lid loops 0.045/0.040", dict(r_dsg=0.045, r_chg=0.040)), ("V(AK) 29 mV", dict(v_ak=0.029))):
        c = dict(base, **ov)
        cells = []
        for n in (14, 15):
            cells.append("4S%dP %s / %s" % (n, B.fmt(B.both(n, prof(40, 0), B.PR0 * R[(40, 0)][0], c, tl)), B.fmt(B.both(n, prof(40, 0), B.PR0 * R[(40, 0)][1], c, tl))))
        print("   %-5s + %-22s %s" % (base_n, lab, "   ".join(cells)))
print("\n2. the pack charge efficiency at which the 4S15P WE band's points stop counting (both builds, above 4.2 Wh)")
for sl, az in ((40, 0), (30, 0), (50, 15)):
    lo, hi = 0.85, 0.98
    def counts(x):
        c = dict(we, chg_eta=x)
        return all(s["ok"] and s["both"] > 4.2 for s in (B.both(15, prof(sl, az), B.PR0 * R[(sl, az)][i], c, tl) for i in (0, 1)))
    if not counts(hi):
        print("   %d/%+d: does not count even at 0.98" % (sl, az)); continue
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if counts(mid): hi = mid
        else: lo = mid
    print("   %d/%+d: counts at a charge efficiency of %.3f and above" % (sl, az, hi))
print("\n3. the lid path's standby drain named in reconcile_lid_panel.out's NOTES (1.8 Wh over 72 h), as 0.025 W on the load, WE and WE60, 40/0 WAB")
for lab, c in (("WE", we), ("WE60", we60)):
    for n in (14, 15):
        a = B.both(n, prof(40, 0), B.PR0 * R[(40, 0)][1], c, tl)
        B.LOAD = 42.8 + 1.8 / 72.0
        b = B.both(n, prof(40, 0), B.PR0 * R[(40, 0)][1], c, tl)
        B.LOAD = 42.8
        print("   %-5s 4S%dP WAB: %s -> %s" % (lab, n, B.fmt(a), B.fmt(b)))
print("\n4. ONE AT A TIME FROM NOM AND FROM WE, 40/0: the change in the lowest store (NOT MET counts as minus the unserved)")
def metric(s):
    return s["both"] if s["ok"] else -s["short"]
terms = (("stage 0.90", dict(e_st=0.90)), ("front end 0.90", dict(e_fe=0.90)), ("charge eta 0.90", dict(chg_eta=0.90)),
         ("lid loops 0.045/0.040", dict(r_dsg=0.045, r_chg=0.040)), ("V(AK) 29 mV", dict(v_ak=0.029)), ("U3 0.9727 (lower)", dict(e_u3=0.9727)))
for base_n, base in (("NOM", nom), ("WE", we)):
    for b, bi in (("TYP", 0), ("WAB", 1)):
        for n in (14, 15):
            s0 = metric(B.both(n, prof(40, 0), B.PR0 * R[(40, 0)][bi], base, tl))
            parts = []
            for lab, ov in terms:
                parts.append("%s %+.1f" % (lab, metric(B.both(n, prof(40, 0), B.PR0 * R[(40, 0)][bi], dict(base, **ov), tl)) - s0))
            print("   %-4s %s 4S%dP (%.1f): %s" % (base_n, b, n, s0, "; ".join(parts)))
print("\n5. the stage's (or the front end's) efficiency at which the 4S15P WE band's points stop counting")
for sl, az in ((40, 0), (50, 15)):
    lo, hi = 0.80, 0.97
    def counts2(x):
        c = dict(we, e_st=x)
        return all(s["ok"] and s["both"] > 4.2 for s in (B.both(15, prof(sl, az), B.PR0 * R[(sl, az)][i], c, tl) for i in (0, 1)))
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if counts2(mid): hi = mid
        else: lo = mid
    print("   %d/%+d: counts at a stage efficiency of %.3f and above (front end at 0.93)" % (sl, az, hi))
print("\n6. U3B's efficiency and the lid's charge loop alone at WE, 40/0 (WE carries U3B 0.963)")
for lab, ov in (("U3B 0.972 (carried)", dict(eta_b=0.972)), ("U3B 0.963 (WE)", {}), ("charge loop 0.040", dict(r_chg=0.040)), ("discharge loop 0.045", dict(r_dsg=0.045))):
    cells = []
    for n in (14, 15):
        for bi, b in ((0, "TYP"), (1, "WAB")):
            cells.append("4S%dP %s %s" % (n, b, B.fmt(B.both(n, prof(40, 0), B.PR0 * R[(40, 0)][bi], dict(we, **ov), tl))))
    print("   %-22s %s" % (lab, "; ".join(cells)))
print("\n7. the bus (WE otherwise, U3 held at 0.9733) at which the 4S15P WE band's points stop counting")
for sl, az in ((40, 0), (50, 15)):
    lo, hi = 18.0, 20.0
    def counts3(x):
        c = dict(we, vbus=x)
        return all(s["ok"] and s["both"] > 4.2 for s in (B.both(15, prof(sl, az), B.PR0 * R[(sl, az)][i], c, tl) for i in (0, 1)))
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if counts3(mid): hi = mid
        else: lo = mid
    print("   %d/%+d: counts at a bus of %.3f V and above" % (sl, az, hi))
