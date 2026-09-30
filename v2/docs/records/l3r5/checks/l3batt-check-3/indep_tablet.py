#!/usr/bin/env python3
"""indep_tablet.py: CHECK-3 of fnd/l3batt (an AI check). The tablet budget on the checker's own balance
(../chk-energy/indep_balance.py with its hourly extra-load option; no record script imported). Usage: python3 indep_tablet.py <repo>"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "chk-energy"))
import indep_round2 as R2  # noqa: E402
B = R2.B
p40, r40, TL = R2.prof(40, 0), R2.RAT[(40, 0)], R2.TL
NOM, WE = R2.NOM, R2.WE
NOM90 = dict(NOM, e_st=0.90, e_fe=0.90, chg_eta=0.90)
DRAWN = dict(NOM, iin=4.15, e_u3=0.9810, fe_i=4.212 - 0.060)
TAB = 18.0 / 0.930
def win(h0):
    return lambda hh: TAB if hh in (h0, h0 + 1) else 0.0
ANY = lambda hh: 36.0 / 0.930 / 24.0 + 1.44
def both(n, c, bi, hours, extra, short_extra=False):
    rs = []
    for st in (6, 18):
        B.LOAD = 42.8 + c.get("drain", 0.0)
        tr = []
        r = B.run(n, p40, B.PR0 * r40[bi], c, st, TL, hours=hours, extra=extra, trace=tr, short_extra=short_extra)
        B.LOAD = 42.8
        stop = next((h for h, hh, eb, el, on, ps in tr if not on), None)
        rs.append((r, stop))
    return rs
def least(c, bi, hours, extra):
    def ok(x):
        return all(r["ok"] and r["lo_t"] > 4.2 for r, s in both(x, c, bi, hours, extra))
    lo, hi = 9.0, 40.0
    for _ in range(30):
        m = 0.5 * (lo + hi)
        if ok(m): hi = m
        else: lo = m
    return hi
def add(x):
    return B.usable(42.8 * x / (6 + x), TL, x) - B.usable(42.8 * 9 / 15, TL, 9)
print("tablet at VBAT in the window: %.3f W; a day %.2f Wh; ANY %.3f W, %.2f Wh a day" % (TAB, 2 * TAB, ANY(0), 24 * ANY(0)))
print("1. SCHEDULES, NOM TYP, least lid and added usable Wh")
for hours in (48, 72):
    for lab, ex in (("none", None), ("W13", win(13)), ("W10", win(10)), ("W19", win(19)), ("ANY", ANY)):
        x = least(NOM, 0, hours, ex)
        print("   %d h %-5s lid 4S%.2fP, +%.1f Wh" % (hours, lab, x, add(x)))
print("2. OPTIONS, W13")
for hours, lab, c, bi in ((72, "WE TYP", WE, 0), (72, "NOM90 TYP", NOM90, 0), (48, "NOM TYP", NOM, 0), (48, "WE TYP", WE, 0)):
    x = least(c, bi, hours, win(13))
    print("   %d h %-10s lid 4S%.2fP, +%.1f Wh" % (hours, lab, x, add(x)))
print("3. AS DRAWN with W13, present store (4S9P): unserved (the tablet not counted while stopped / counted)")
for hours in (48, 72):
    a = both(9, DRAWN, 0, hours, win(13)); b = both(9, DRAWN, 0, hours, win(13), True)
    print("   %d h: %.1f / %.1f Wh unserved, stops h %s/%s" % (hours, max(r["short"] for r, s in a), max(r["short"] for r, s in b), a[0][1], a[1][1]))
xd = least(DRAWN, 0, 72, win(13)); print("   as drawn least lid 72 h: 4S%.2fP, +%.1f Wh" % (xd, add(xd)))
xd = least(DRAWN, 0, 48, win(13)); print("   as drawn least lid 48 h: 4S%.2fP, +%.1f Wh" % (xd, add(xd)))
print("4. OPTION A's 48 h store run for 72 h, W13, TYP")
for lab, c in (("NOM", NOM), ("WE", WE)):
    x = least(c, 0, 48, win(13))
    rs = both(x, c, 0, 72, win(13))
    print("   %s: lid 4S%.2fP; 72 h: %s, unserved %.1f Wh, stops h %s/%s" % (lab, x, "ok" if all(r["ok"] for r, s in rs) else "NOT MET", max(r["short"] for r, s in rs), rs[0][1], rs[1][1]))
print("5. BATTERY ONLY with the window in the run: (544.4 - %.1f) / 42.825 = %.2f h; (224.5 - %.1f) / 42.825 = %.2f h" % (2 * TAB, (544.4 - 2 * TAB) / 42.825, 2 * TAB, (224.5 - 2 * TAB) / 42.825))
print("6. THE TRACE, NOM TYP 72 h W13 at the author's 4S11.79P, start 06, second day")
B.LOAD = 42.8
tr = []
B.run(11.79, p40, B.PR0 * r40[0], NOM, 6, TL, extra=win(13), trace=tr)
day2 = [x for x in tr if 24 <= x[0] < 48]
print("   node W at 08..17 UTC: %s" % " ".join("%.0f" % x[5] for x in day2 if 8 <= x[1] <= 17))
fb, fl = B.usable(42.8 * 6 / 17.79, 20.0, 6), B.usable(42.8 * 11.79 / 17.79, TL, 11.79)
print("   highest that day: base %.1f of %.1f, lid %.1f of %.1f Wh" % (max(x[2] for x in day2), fb, max(x[3] for x in day2), fl))
