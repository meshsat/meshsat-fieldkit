#!/usr/bin/env python3
"""indep_tablet2.py: CHECK-3 of fnd/l3batt (an AI check), part 2. The options table's remaining cells on the checker's own
balance (../chk-energy/indep_balance.py; no record script imported). Usage: python3 indep_tablet2.py <repo>"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "chk-energy"))
import indep_round2 as R2  # noqa: E402
B = R2.B
p40, r40, TL = R2.prof(40, 0), R2.RAT[(40, 0)], R2.TL
NOM, WE = R2.NOM, R2.WE
LO3 = dict(e_st=0.90, e_fe=0.90, chg_eta=0.90)
NOM90, WE90 = dict(NOM, **LO3), dict(WE, **LO3)
CASES = (("NOM", NOM), ("NOM90", NOM90), ("WE", WE), ("WE90", WE90))
TAB = 18.0 / 0.930
W13 = lambda hh: TAB if hh in (13, 14) else 0.0
HF = 1.14
def hf(c, on):
    return dict(c, drain=c.get("drain", 0.0) + (HF if on else 0.0))
def both(n, c, bi, hours, extra):
    rs = []
    for st in (6, 18):
        B.LOAD = 42.8 + c.get("drain", 0.0)
        tr = []
        r = B.run(n, p40, B.PR0 * r40[bi], c, st, TL, hours=hours, extra=extra, trace=tr)
        B.LOAD = 42.8
        stop = next((h for h, hh, eb, el, on, ps in tr if not on), None)
        rs.append((r, stop))
    return rs
def least(c, bi, hours, extra):
    def ok(x):
        return all(r["ok"] and r["lo_t"] > 4.2 for r, s in both(x, c, bi, hours, extra))
    lo, hi = 9.0, 60.0
    for _ in range(30):
        m = 0.5 * (lo + hi)
        if ok(m): hi = m
        else: lo = m
    return hi
def add(x, load=42.8):
    return B.usable(load * x / (6 + x), TL, x) - B.usable(load * 9 / 15, TL, 9)
print("1. LEAST STORE WITH W13, added usable Wh at the lid (share at 42.8 W / at the load with HF)")
res = {}
for on in (False, True):
    for hours in (48, 72):
        for lab, c in CASES:
            for bi, b in ((0, "TYP"), (1, "WAB")):
                x = least(hf(c, on), bi, hours, W13)
                a = add(x); a2 = add(x, 42.8 + (HF if on else 0.0))
                res[(on, hours, lab, b)] = (x, a)
                print("   HF %-9s %d h %-5s %s lid 4S%.2fP, +%.1f / +%.1f Wh" % ("listening" if on else "available", hours, lab, b, x, a, a2))
print("2. OPTION A's 48 h store (TYP, HF available) run for 72 h with W13")
for lab, c in CASES:
    x = res[(False, 48, lab, "TYP")][0]
    rs = both(x, c, 0, 72, W13)
    print("   %-5s lid 4S%.2fP: %s, unserved %.1f Wh, stops h %s/%s" % (lab, x, "met" if all(r["ok"] for r, s in rs) else "NOT MET", max(r["short"] for r, s in rs), rs[0][1], rs[1][1]))
print("3. PRESENT STORE 4S9P with W13, TYP, HF available: unserved and stop hours")
for hours in (48, 72):
    for lab, c in (("NOM", NOM), ("WE", WE)):
        rs = both(9, c, 0, hours, W13)
        print("   %d h %-3s unserved %.1f Wh, stops h %s/%s" % (hours, lab, max(r["short"] for r, s in rs), rs[0][1], rs[1][1]))
print("4. BATTERY ONLY, the window in the run (38.71 Wh), at 42.825 W, +20 C / -10 C")
def st(x, t):
    return B.usable(42.8 * 6 / (6 + x), 20.0 if t is None else t, 6) + B.usable(42.8 * x / (6 + x), 20.0 if t is None else t, x)
for lab, x in (("present 4S9P", 9.0), ("A NOM", res[(False, 48, "NOM", "TYP")][0]), ("A WE", res[(False, 48, "WE", "TYP")][0]),
               ("B NOM", res[(False, 72, "NOM", "TYP")][0]), ("B WE", res[(False, 72, "WE", "TYP")][0])):
    u20, um10 = st(x, 20.0), st(x, -10.0)
    print("   %-13s lid 4S%.2fP: %.1f / %.1f Wh -> %.2f / %.2f h (their +20 C form: (544.4 + add) -> %.2f h)" % (
        lab, x, u20, um10, (u20 - 2 * TAB) / 42.825, (um10 - 2 * TAB) / 42.825, (544.4 + add(x) - 2 * TAB) / 42.825))
