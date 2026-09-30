#!/usr/bin/env python3
"""indep_l3feas.py: CHECK-1 of fnd/l3feas (an AI check). The checker's own two-pack balance (../chk-energy/indep_balance.py
and indep_round2.py, no record script imported) for Task 1, and the checker's arithmetic for Task 3.
U3's efficiency at 6.25 and 6.191 A is not recomputed (s117's method); 0.9730 and 0.9731 are used, beside a bracket.
Usage: python3 indep_l3feas.py <repo root>"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "chk-energy"))
import indep_round2 as R2  # noqa: E402  (reads sys.argv[1])
B = R2.B
p40, r40, TL = R2.prof(40, 0), R2.RAT[(40, 0)], R2.TL
WE = R2.WE
routes = [("WE", dict(WE)), ("R1 6.25 A (U3 0.9730)", dict(WE, iin=6.25, e_u3=0.9730)),
          ("R1 6.25 A (U3 0.9733)", dict(WE, iin=6.25, e_u3=0.9733)),
          ("R1lo 6.191 A (U3 0.9731)", dict(WE, iin=6.35 * 0.975, e_u3=0.9731)),
          ("R2 stage 0.965", dict(WE, e_st=0.965))]
def lines(s):
    return "STOP %s, COMB %s, EACH %s" % ("kept" if s["ok"] else "FAILS", "Y" if s["ok"] and s["both"] > 4.2 else "N",
                                         "Y" if s["ok"] and s["base"] > 4.2 and s["lid"] > 4.2 else "N")
print("1. 4S14P, mean day 40/0, WE restated (drain, loops worse end, V(AK) 29 mV)")
res = {}
for nm, c in routes:
    for bi, b in ((0, "TYP"), (1, "WAB")):
        s = R2.both(14, p40, B.PR0 * r40[bi], c)
        res[(nm, b)] = s
        print("   %-26s %s: %-34s %s" % (nm, b, R2.fmt(s), lines(s)))
print("   R1 gain over WE at WAB: %+.1f Wh" % (res[("R1 6.25 A (U3 0.9730)", "WAB")]["both"] + res[("WE", "WAB")]["short"]))
print("2. HOUR BY HOUR, WAB")
for nm, c in (routes[0], routes[1]):
    for st in (6, 18):
        tr = []
        B.LOAD = 42.8 + c["drain"]
        r = B.run(14, p40, B.PR0 * r40[1], c, st, TL, trace=tr)
        B.LOAD = 42.8
        cap = min(c["fe_i"], c["iin"]) * c["vbus"]
        caph = sorted({hh for h, hh, eb, el, on, ps in tr if abs(ps - cap * c["e_u3"]) < 1e-6})
        lid0 = [(h, hh) for h, hh, eb, el, on, ps in tr if el <= 1e-9]
        base_lo = min(tr, key=lambda x: x[2])
        stop = next(((h, hh) for h, hh, eb, el, on, ps in tr if not on), None)
        print("   %-24s start %02d: cap %.1f W at VBUS20 (%.1f at the node), cap hours UTC %s; lid at its line %s; base lowest %.1f Wh at hour %d (UTC %02d); stop %s" % (
            nm, st, cap, cap * c["e_u3"], caph, lid0[:3], base_lo[2], base_lo[0], base_lo[1], stop))
print("   largest hour into the stage: TYP %.1f W, WAB %.1f W" % tuple(max(min(400 * g / 1000 * B.PR0 * r40[i], 200) for g in p40) for i in (0, 1)))
print("3. THRESHOLDS at WAB, each alone (search 0.80 to 1.00)")
def thr(c, key, line):
    def ok(x):
        s = R2.both(14, p40, B.PR0 * r40[1], dict(c, **{key: x}))
        return s["ok"] if line == "STOP" else (s["ok"] and s["both"] > 4.2)
    lo, hi = 0.80, 1.00
    if not ok(hi): return None
    for _ in range(30):
        m = 0.5 * (lo + hi)
        if ok(m): hi = m
        else: lo = m
    return hi
for nm, c in (routes[1], routes[3], routes[0]):
    print("   %-26s charge STOP %.3f COMB %.3f; stage STOP %.3f COMB %.3f; front end COMB %.3f" % (
        nm, thr(c, "chg_eta", "STOP"), thr(c, "chg_eta", "COMB"), thr(c, "e_st", "STOP"), thr(c, "e_st", "COMB"), thr(c, "e_fe", "COMB")))
def thr_i(line):
    def ok(x):
        s = R2.both(14, p40, B.PR0 * r40[1], dict(WE, iin=x))
        return s["ok"] if line == "STOP" else (s["ok"] and s["both"] > 4.2)
    lo, hi = 6.0, 6.35
    for _ in range(30):
        m = 0.5 * (lo + hi)
        if ok(m): hi = m
        else: lo = m
    return hi
print("   U3's least input limit (U3 held at 0.9733): STOP %.3f A, COMB %.3f A" % (thr_i("STOP"), thr_i("COMB")))
print("4. R1 AGAINST THE ELECTRICAL RECORD")
mx = max(6.35 + 0.1, 6.35 * 1.025)
for lab, o in (("0.060", 0.060), ("0.079", 0.079)):
    print("   U3 at 6.35 A: max %.3f A; through R11 %.3f A; margin to 6.793 A %+.3f A" % (mx, mx + o, 6.793 - mx - o))
print("   bank worst can at %.3f A: matched %.2f A (%.1f %%), 2:1 %.2f A (%.1f %%)" % (mx + 0.060, 0.370 * (mx + 0.06), 0.370 * (mx + 0.06) / 2.8 * 100, 0.428 * (mx + 0.06), 0.428 * (mx + 0.06) / 2.8 * 100))
print("   stage input in service at R1: %.1f W (at 6.415 A: %.1f W)" % ((mx + 0.060) * 20.887 / 0.93 / 0.93, 6.415 * 20.887 / 0.93 / 0.93))
print("   ILIM_HIZ: pin at REGN 5.7 V %.3f V -> %.2f A nominal at 10 mOhm" % (5.7 * 34.8 / 51.3, (5.7 * 34.8 / 51.3 - 1) / 0.4))
print("5. SOLAR")
voc, isc, a_voc, a_isc = 22.5, 5.75, -0.0031, 0.0005
for v, lab in ((22.5, "held"), (24.4, "current page")):
    print("   %s: 2S Voc -20 C %.2f, -40 C %.2f, 1.25 clause %.2f V" % (lab, 2 * v * (1 - a_voc * 45), 2 * v * (1 - a_voc * 65), 2 * 1.25 * v))
ih = isc * (1 + a_isc * 45)
print("   Isc string %.2f / %.2f / %.2f A; array %.2f / %.2f / %.2f A; F2 1.25 x %.2f = %.2f A" % (isc, ih, 1.25 * ih, 2 * isc, 2 * ih, 2.5 * ih, 2.5 * ih, 3.125 * ih))
print("   power: -20 C %.1f W, x1.25 %.1f W; stage ceiling %.1f W out, %.1f W in" % (400 * (1 + 0.0042 * 45), 1.25 * 400 * (1 + 0.0042 * 45), 20.4 * 15.1, 20.4 * 15.1 / 0.93))
print("6. THE KELVIN BUDGET UNDER R1 (R11 at its stacked maximum 6.2855 mOhm, VSNS 43 mV less 0.3 mV)")
Rmax = 6.2 * 1.01 * (1 + 50e-6 * 75)
for lab, i in (("drafted 6.2 A, 0.060 A", 6.355 + 0.060), ("R1, 0.060 A", mx + 0.060), ("R1, 0.079 A", mx + 0.079)):
    cu = 0.0427 / i * 1000 - Rmax
    print("   %-24s %.3f A through R11: copper %.3f mOhm working; at 25 C %.3f (copper at 100 C) to %.3f (62.1 C)" % (lab, i, cu, cu / 1.29475, cu / (1 + 0.00393 * 37.1)))
print("   R1 at 6.569 A with C-1's 0.29 mOhm at 25 C (copper at 100 C): sensed %.2f mV against 42.7 mV" % (6.569 * (Rmax + 0.29 * 1.29475)))
