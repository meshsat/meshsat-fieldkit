#!/usr/bin/env python3
"""Track current rating from a published standard, and what this project's own bar is worth against it.

MESHSAT-862, 16 September 2026, rule PI-001. `dc_drop.py` has judged every rail on all seven boards against
`I = k dT^0.44 A^0.725` with k 0.024 internal and 0.048 external, carried in a comment as "IPC-2221" with no
document behind it anywhere in this tree: the rule has read SOURCE_UNVERIFIED since the registry was written,
which is the honest reading of a number nobody can look up.

ECSS-Q-ST-70-12C (14 July 2014, Annex D) publishes closed-form curve fits of three current-rating models with
their constants, their validity ranges and a worked example. It is free, it is a standard, and the clauses this
project cites are transcribed in `v2/vendor/standards/ecss-q-st-70-12c-2014-07-14.md`. This module implements
its formula, proves itself against its worked example, and prints what the three models say side by side.

    I = k0 * dT^k1 * (c1 * A)^(m0 * dT^m1)          c1 = 1550 mil2 per mm2, A in mm2, dT in K, I in A

Usage:
  track_current.py selftest                      the standard's own worked example, and this project's bar against it
  track_current.py rating <width mm> <thickness mm> [dT K]     all three models for one conductor
  track_current.py width <current A> <thickness mm> [dT K]     the width each model asks for
"""
import sys, os

C1 = 1550.0            # ECSS D.1.2 item 5: the conversion factor mm2 -> mil2 the formula is written in

# ECSS-Q-ST-70-12C Annex D. The name is the clause, because a constant whose provenance is its variable name
# is how this project got here in the first place.
MODELS = {
    "IPC-2152":  (0.0756, 0.4375, 0.5000, 0.0301),   # D.2, curve fit of IPC-2152 figure 5-14 (vacuum and space chart)
    "CNES":      (0.0594, 0.4800, 0.5420, 0.0034),   # D.3, curve fit of CNES/QFT/IN.0113, about 10 percent under IPC-2152
    "IPC-2221A": (0.0240, 0.4393, 0.7252, 0.0002),   # D.4, curve fit of IPC-2221A figure 6-4 curve C, INTERNAL conductors
}
# D.4 a: the conditions the IPC-2221A fit is stated as valid within. Outside them the standard makes no claim,
# and this project's rails run to 18 A, which is fifteen times the largest of these.
IPC2221A_VALID = {1.0: 0.7, 2.0: 0.9, 5.0: 1.0, 10.0: 1.2}


def rating(area_mm2, dT=10.0, model="IPC-2221A"):
    """Amps for a cross-section in mm2 at a temperature increment dT in K, by one of the Annex D models."""
    k0, k1, m0, m1 = MODELS[model]
    return k0 * (dT ** k1) * ((C1 * area_mm2) ** (m0 * (dT ** m1)))


def area_for(current_a, dT=10.0, model="IPC-2221A"):
    """The cross-section in mm2 a current needs, the inverse of rating() and ECSS D.1.2 item 7."""
    k0, k1, m0, m1 = MODELS[model]
    return (1.0 / C1) * (current_a / (k0 * (dT ** k1))) ** (1.0 / (m0 * (dT ** m1)))


def crossover(dT=10.0, lo=1e-4, hi=10.0):
    """The cross-section in mm2 at which the IPC-2221A fit stops being the conservative one.

    Both models are functions of area alone, so this is a single area per temperature rise. It matters because
    the project's rails are wide pours: below it the bar this project uses is the safe reading and above it the
    bar is the optimistic one, and nothing in the tool said which side of the line a given rail was on."""
    f = lambda a: rating(a, dT, "IPC-2221A") - rating(a, dT, "IPC-2152")
    if f(lo) > 0 or f(hi) < 0: return float("nan")
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def valid_for_ipc2221a(current_a, dT):
    """(ok, why) against ECSS D.4 a. The fit is published with a ceiling and this project runs past it."""
    keys = sorted(IPC2221A_VALID)
    near = min(keys, key=lambda k: abs(k - dT))
    cap = IPC2221A_VALID[near]
    if current_a <= cap:
        return True, "within D.4 a (%.1f A at %.0f K, the published ceiling is %.1f A)" % (current_a, near, cap)
    return False, ("OUTSIDE the range ECSS D.4 a publishes this fit for: %.2f A at %.0f K against a ceiling of "
                   "%.1f A. The standard's own remark is that inside the range IPC-2221A reads about 70 percent "
                   "of IPC-2152, and it says nothing at all above it" % (current_a, near, cap))


def _dc_drop_bar(area_mm2, dT=10.0, internal=False):
    """What this project's own tool says, for the comparison. Imported rather than retyped."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import dc_drop
    return dc_drop.ipc_limit(area_mm2, dT, internal=internal)


def selftest():
    bad = 0
    # 1. THE STANDARD'S OWN WORKED EXAMPLE (D.1.3): 1 A at 5 K on 0.925 mm by 0.025 mm under the IPC-2152 fit.
    a = 0.925 * 0.025
    got = rating(a, 5.0, "IPC-2152")
    ok = abs(got - 1.0) < 0.002
    print("D.1.3  0.925 x 0.025 mm at 5 K, IPC-2152 fit: %.4f A against the standard's 1 A   %s"
          % (got, "OK" if ok else "MISMATCH"))
    bad += 0 if ok else 1
    # and the inverse, from the same numbers
    w = area_for(1.0, 5.0, "IPC-2152") / 0.025
    ok = abs(w - 0.925) < 0.002
    print("D.1.2  the width 1 A asks for at 5 K on 25 um: %.4f mm against the standard's 0.925   %s"
          % (w, "OK" if ok else "MISMATCH"))
    bad += 0 if ok else 1
    # 2. THIS PROJECT'S OWN BAR against the published IPC-2221A fit, over the range the boards actually use.
    worst = (0.0, None)
    for w_mm in (0.2, 0.25, 0.4, 0.5, 1.0, 2.0, 3.0, 6.0):
        for t_mm in (0.0152, 0.0175, 0.035, 0.070):          # 0.5 oz inner plating, 18 um, 1 oz, 2 oz
            for dT in (5.0, 10.0, 20.0):
                a = w_mm * t_mm
                mine, theirs = _dc_drop_bar(a, dT, internal=True), rating(a, dT, "IPC-2221A")
                rel = abs(mine - theirs) / theirs
                if rel > worst[0]: worst = (rel, (w_mm, t_mm, dT, mine, theirs))
    w_mm, t_mm, dT, mine, theirs = worst[1]
    print("dc_drop's internal bar against ECSS D.4 over 96 geometries: worst deviation %.2f percent "
          "(%.2f mm x %.4f mm at %.0f K: %.3f A against %.3f A)" % (100 * worst[0], w_mm, t_mm, dT, mine, theirs))
    ok = worst[0] < 0.01
    print("        %s" % ("OK: this project's internal-conductor constants are the published ones to within 1 percent"
                          if ok else "MISMATCH: the tool and the standard do not agree"))
    bad += 0 if ok else 1
    # 3. WHAT THE OLD MODEL COSTS, in the direction that matters: it is conservative, and by how much.
    for w_mm, t_mm, dT in ((0.5, 0.035, 10.0), (3.0, 0.035, 10.0), (6.0, 0.070, 20.0)):
        a = w_mm * t_mm
        old, new = rating(a, dT, "IPC-2221A"), rating(a, dT, "IPC-2152")
        print("%.1f mm x %.3f mm at %.0f K: IPC-2221A %.2f A, IPC-2152 %.2f A, CNES %.2f A (the old model is "
              "%.0f percent of the new one)" % (w_mm, t_mm, dT, old, new, rating(a, dT, "CNES"), 100 * old / new))
    # 4. WHERE THE OLD MODEL STOPS BEING CONSERVATIVE. Both fits are functions of cross-sectional AREA alone,
    # so the crossover is one area per temperature rise and not a width, and above it the model this project
    # judges its rails with is the LESS conservative of the two. It is not a small band of geometry: a 2 oz
    # pour wider than 3.8 mm at 10 K is past it, and boards P and E5 are 2 oz.
    for dT in (5.0, 10.0, 20.0):
        print("at %2.0f K the two fits cross at %.3f mm2 of copper (%.2f mm wide on 1 oz, %.2f mm on 2 oz): "
              "above that IPC-2221A, which is the bar this project uses, reads HIGHER than IPC-2152"
              % (dT, crossover(dT), crossover(dT) / 0.035, crossover(dT) / 0.070))
    # 5. AND WHERE THIS PROJECT STANDS OUTSIDE THE PUBLISHED RANGE.
    ok2, why = valid_for_ipc2221a(10.0, 10.0)
    print("the pack node at 10 A, 10 K: %s" % why)
    print("track_current: %s" % ("3 of 3 checks pass" if not bad else "%d check(s) FAILED" % bad))
    return 1 if bad else 0


def main(a):
    if not a or a[0] == "selftest": return selftest()
    if a[0] == "rating" and len(a) >= 3:
        w, t = float(a[1]), float(a[2]); dT = float(a[3]) if len(a) > 3 else 10.0
        for m in ("IPC-2221A", "CNES", "IPC-2152"):
            print("%-10s %.3f A for %.3f mm x %.4f mm at %.0f K" % (m, rating(w * t, dT, m), w, t, dT))
        return 0
    if a[0] == "width" and len(a) >= 3:
        i, t = float(a[1]), float(a[2]); dT = float(a[3]) if len(a) > 3 else 10.0
        for m in ("IPC-2221A", "CNES", "IPC-2152"):
            print("%-10s %.3f mm for %.2f A on %.4f mm of copper at %.0f K" % (m, area_for(i, dT, m) / t, i, t, dT))
        print(valid_for_ipc2221a(i, dT)[1])
        return 0
    print(__doc__); return 2


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
