# CELL_BATPRESZ strap of board A (gen_sch_a.py:350 at 82dd1e4d; A23 netlist 0d1e2ef6):
# R26 from CH_VDDA to CH_CELL, R27 from CH_CELL to GND. Windows: SLUSE66A 8.5 (VCELL_xS, % of VDDA, REGN = 6 V).
W = {"1S": (18.4, 31.6), "2S": (35.0, 48.5), "3S": (51.7, 65.0), "4S": (68.4, 81.5), "5S": (90.0, 100.0)}
def pct(top, bot): return 100.0 * bot / (top + bot)
def span(top, bot, tol=0.01):
    v = [pct(top * a, bot * b) for a in (1 - tol, 1 + tol) for b in (1 - tol, 1 + tol)]
    return min(v), max(v)
def cls(p): return [k for k, (lo, hi) in W.items() if lo <= p <= hi] or ["none"]
for name, top, bot in (("as generated R26 60.4k / R27 40.2k", 60.4, 40.2),
                       ("values swapped R26 40.2k / R27 60.4k", 40.2, 60.4),
                       ("W2 proposal 13.3k over 40.2k", 13.3, 40.2)):
    lo, hi = span(top, bot)
    print("%-40s nominal %.2f %%  1%% extremes %.2f..%.2f %%  -> %s / %s" % (name, pct(top, bot), lo, hi, cls(lo), cls(hi)))
print("256 mA at pack 12.0 / 14.4 / 16.8 V = %.2f / %.2f / %.2f W" % (0.256 * 12, 0.256 * 14.4, 0.256 * 16.8))
print("2S BATOVP rising 104 %% of 8.400 V = %.3f V (min 102.3 %% = %.3f V)" % (8.4 * 1.04, 8.4 * 1.023))
