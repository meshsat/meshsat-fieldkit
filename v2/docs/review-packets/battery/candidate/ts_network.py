#!/usr/bin/env python3
"""The second-level protector's TS network, board P (MESHSAT-1357 review stream BAT, 26 September 2026; second cycle).

Every input is a published number:
  - Semitec 103AT-2 resistance table and tolerances: v2/vendor/battery/semitec-at-p12-13.pdf
    (sha256 389dc527...3262): R25 10.0 kohm +-1 %, B25/85 3435 K +-1 %, the table rows used below.
  - BQ77207, SLUSEG7D (Rev. D, May 2026) section 6.5 (v2/vendor/battery/ti-bq77207.pdf, sha256 45c1c99e...):
      ROT_EXT_NTC 2195 ohm for the BQ7720700's 70 C (section 4); TOT_ACC "OT Detection Accuracy (NTC)" -5 to +5 C;
      RUT_EXT_NTC 111100 / 68900 / 42200 / 26700 ohm; RUT_ACC "UT Detection External Resistance Accuracy" -2 to +2 %;
      TUT_ACC "UT Detection Accuracy (NTC)" -5 to +5 C; RTC 19.4 / 20 / 20.6 kohm.
      Footnote (1) on TOT_ACC and TUT_ACC: "Assured by design. This accuracy assumes the external resistance is within
      +-2% of the R_OT_EXT values for the corresponding temperature threshold."
  - UNI-ROYAL 0603WAF thick film: +-1 %, +-100 ppm/C (JLC API record, review-packets/battery/evidence/jlc-queries-bat.json).

THE ACCURACY MODEL (second cycle; the first cycle read RUT_ACC as the chip's UT accuracy, which it is not: RUT_ACC is the
EXTERNAL resistance accuracy footnote (1) assumes, and the chip's own UT accuracy is TUT_ACC, +-5 C). The chip compares the
external resistance with a threshold; its own error, expressed as a resistance, is taken from the +-5 C at the NTC slope
beta(T) = -d ln R / dT of the 103AT at that threshold, the SAME way for OT and for UT:
  reading A (the footnote's words): the +-5 C includes an external resistance within +-2 %, so the chip's own share is
            5 * beta - ln(1.02);
  reading B (conservative): the +-5 C is the chip's alone, 5 * beta.
Every margin below is stated under reading B, the worse one for both the UT ceiling and the OT window.

CROSS-CHECK ON TI'S OWN THRESHOLDS (third cycle). The UT floor above uses the 103AT's slope at 0.5 C. TI's own two warmest
UT thresholds (42.2 kohm at -10 C, 26.7 kohm at 0 C) give a chord slope of ln(42.2/26.7)/10 = 0.0458 per C, which is the
slope of TI's curve at about -5 C. Applied unchanged over the 0 to +5 C that TUT_ACC's +5 C spans, it gives a lower floor;
a B-parameter fit through the same two points, evaluated at +5 C, follows the slope's fall with temperature. Both are
printed, so the conservative bound does not rest on one curve.

The network is Rp || (Rs + NTC): Rp from TS to VSS on the board, Rs from TS to the connector, the NTC off board.
Run: python3 ts_network.py [Rs Rp]   (with no arguments: the options table and the taken network, 270 / 18000)."""
import math, sys

T = [-50, -40, -30, -20, -10, 0, 10, 20, 25, 30, 40, 50, 60, 70, 80, 85, 90, 100, 110]
R = [329.5, 188.5, 111.3, 67.77, 42.47, 27.28, 17.96, 12.09, 10.00, 8.313, 5.827, 4.160, 3.020, 2.228, 1.668,
     1.451, 1.266, 0.9731, 0.7576]            # kohm, the 103AT column
R = [x * 1000.0 for x in R]
ROT = 2195.0
RUT = [26700.0, 42200.0, 68900.0, 111100.0]
TOL = 0.01            # the 0603WAF resistors
TCR = 100e-6          # per C, the same parts
B = 3435.0            # B25/85 of the 103AT, +-1 %
T_BOARD_MIN = -40.0   # the lowest board temperature considered (BQ77207 TA minimum, SLUSEG7D 6.3)
T_BOARD_OT = 70.0     # board temperature taken at the OT trip (the board sits on the pack)
ACC_C = 5.0           # TOT_ACC and TUT_ACC


def ntc(t):
    """Interpolate ln R linearly in 1/T between table rows (the table's own shape)."""
    k = max(i for i in range(len(T) - 1) if T[i] <= t) if t < T[-1] else len(T) - 2
    x0, x1 = 1 / (T[k] + 273.15), 1 / (T[k + 1] + 273.15); x = 1 / (t + 273.15)
    return math.exp(math.log(R[k]) + (math.log(R[k + 1]) - math.log(R[k])) * (x - x0) / (x1 - x0))


def beta(t):
    """-d ln R / dT of the 103AT at t, per C (central difference on the table's interpolation)."""
    return -(math.log(ntc(t + 0.05)) - math.log(ntc(t - 0.05))) / 0.1


def temp_at(r_target, f, lo=-50.0, hi=110.0):
    for _ in range(80):
        mid = (lo + hi) / 2
        if f(mid) > r_target: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def par(a, b): return a * b / (a + b)


def chip_share(t, reading):
    """The chip's own threshold error as a ln-resistance, from the +-5 C at the 103AT's slope at t."""
    e = ACC_C * beta(t)
    return e - math.log(1.02) if reading == "A" else e


T_UT = temp_at(RUT[0], ntc)                       # the bare 103AT's temperature at the lowest UT resistance
RUT_LOW = {rd: RUT[0] * math.exp(-chip_share(T_UT, rd)) for rd in ("A", "B")}
RUT_LOW_OLD = RUT[0] * 0.98                       # the first cycle's reading (RUT_ACC taken as the chip's), withdrawn
CHORD_TI = math.log(RUT[1] / RUT[0]) / 10.0       # TI's chord slope between its -10 C and 0 C thresholds, per C
B_TI = math.log(RUT[1] / RUT[0]) / (1 / 263.15 - 1 / 273.15)     # a B fit through the same two thresholds
RUT_LOW_TI = {"chord, reading B": RUT[0] * math.exp(-ACC_C * CHORD_TI),
              "B fit, reading B": RUT[0] * math.exp(B_TI * (1 / 278.15 - 1 / 273.15))}


def analyse(Rs, Rp, verbose=True):
    net = lambda t, rs=Rs, rp=Rp, k=1.0: par(rp, rs + k * ntc(t))
    t_trip = temp_at(ROT, net)
    n = ntc(t_trip); rn = net(t_trip)
    s = (rn / (Rs + n)) * (n / (Rs + n)) if Rs + n else 1.0
    # the network's own tolerance at the trip: NTC R25 +-1 %, B +-1 %, Rs and Rp +-1 % and TCR over 25..70 C
    dt_board = abs(T_BOARD_OT - 25.0) * TCR
    worst = []
    for kR in (0.99, 1.01):
        for dB in (-0.01, 0.01):
            kB = math.exp(B * dB * (1 / (t_trip + 273.15) - 1 / 298.15))
            for ks in (1 - TOL - dt_board, 1 + TOL + dt_board):
                for kp in (1 - TOL - dt_board, 1 + TOL + dt_board):
                    worst.append(par(Rp * kp, Rs * ks + kR * kB * n) / rn)
    e_lo, e_hi = min(worst), max(worst)
    win = {}
    for rd in ("A", "B"):
        c = chip_share(t_trip, rd)
        # lowest trip: chip threshold high (exp(+c)) and network low (e_lo); highest: the reverse
        win[rd] = (temp_at(ROT * math.exp(c) / e_lo, net), temp_at(ROT * math.exp(-c) / e_hi, net))
    ceil = Rp * (1 + TOL) * (1 + (25.0 - T_BOARD_MIN) * TCR)      # NTC open, Rp at +1 % and cold
    below = {rd: (1 - ceil / RUT_LOW[rd]) * 100 for rd in ("A", "B")}
    r = dict(Rs=Rs, Rp=Rp, trip=t_trip, slope=s, net_tol=(e_lo - 1, e_hi - 1), window=win, ceiling=ceil, below=below,
             net_m50=net(-50), net_25=net(25),
             rs_short=temp_at(ROT, lambda t: par(Rp, ntc(t))), rp_open=temp_at(ROT, lambda t: Rs + ntc(t)),
             ntc_short=par(Rp, Rs), open_reads=temp_at(Rp, ntc),
             frac_plug=net(25) / (net(25) + 20000.0), frac_open=Rp / (Rp + 20000.0))
    if verbose:
        print("NETWORK Rp || (Rs + NTC), Rs = %.0f ohm, Rp = %.0f ohm:" % (Rs, Rp))
        print("  OT trip at %.2f C nominal; d ln(network) / d ln(NTC) at the trip %.3f (1.000 for a bare NTC)" % (t_trip, s))
        print("  network tolerance at the trip (NTC R25 and B +-1 %%, Rs and Rp +-1 %% and 100 ppm/C to %.0f C): %+.2f %% to %+.2f %%"
              % (T_BOARD_OT, (e_lo - 1) * 100, (e_hi - 1) * 100))
        for rd in ("A", "B"):
            print("  OT window, reading %s: %.1f to %.1f C" % (rd, win[rd][0], win[rd][1]))
        print("  highest resistance TS can see: NTC open, Rp +1 %% and %.0f C: %.0f ohm (network at -50 C with the NTC in: %.0f ohm)"
              % (T_BOARD_MIN, ceil, net(-50)))
        for rd in ("A", "B"):
            print("  lowest UT resistance, reading %s: %.0f ohm; the ceiling is %.1f %% below it" % (rd, RUT_LOW[rd], below[rd]))
        print("  an open NTC reads as a bare 103AT at %.1f C" % r["open_reads"])
        print("  Rs shorted: trip %.1f C; Rp open: trip %.1f C; NTC shorted: %.0f ohm (reads over-temperature)"
              % (r["rs_short"], r["rp_open"], r["ntc_short"]))
        print("  TS fraction of the internal reference (RTC 20 kohm): J_TS2 plugged at 25 C %.3f, unplugged %.3f"
              % (r["frac_plug"], r["frac_open"]))
    return r


if __name__ == "__main__":
    print("103AT-2 at 70 C: %.0f ohm (table 2228); at 0 C %.0f (table 27280)" % (ntc(70), ntc(0)))
    print("slope beta: %.4f /C at 70 C, %.4f /C at %.1f C" % (beta(70), beta(T_UT), T_UT))
    print("\nBARE NTC on TS (TI Figure 8-1): OT trip at %.1f C nominal" % temp_at(ROT, ntc))
    for r_ in RUT:
        print("  UT resistance %6.0f ohm is reached at %.1f C" % (r_, temp_at(r_, ntc)))
    print("  open NTC: infinite resistance, above every UT resistance (reads as UT if UT is enabled)")
    print("\nTHE LOWEST UT RESISTANCE THE CHIP MAY APPLY (26.7 kohm, the 103AT at %.1f C, moved by TUT_ACC +5 C):" % T_UT)
    print("  reading A (the +-5 C includes a +-2 %% external resistance): %.0f ohm" % RUT_LOW["A"])
    print("  reading B (the +-5 C is the chip's alone):                     %.0f ohm" % RUT_LOW["B"])
    print("  the first cycle's figure, 26.7 kohm less RUT_ACC's 2 %% (WITHDRAWN: RUT_ACC is the external resistance): %.0f ohm" % RUT_LOW_OLD)
    print("\nCROSS-CHECK ON TI'S OWN UT THRESHOLDS (42.2 kohm at -10 C, 26.7 kohm at 0 C), no 103AT data used:")
    print("  chord slope %.4f /C (the slope at about -5 C); B fit %.0f K" % (CHORD_TI, B_TI))
    ceil_taken = 18000.0 * (1 + TOL) * (1 + (25.0 - T_BOARD_MIN) * TCR)
    for k, v in RUT_LOW_TI.items():
        print("  %-17s lowest UT resistance %.0f ohm; the taken network's ceiling (%.0f ohm) is %.1f %% below it"
              % (k, v, ceil_taken, (1 - ceil_taken / v) * 100))
    if len(sys.argv) > 2:
        print(); analyse(float(sys.argv[1]), float(sys.argv[2])); sys.exit(0)
    print("\nOPTIONS (reading B throughout):")
    print("  %-14s %-8s %-7s %-15s %-12s %-9s %-11s" % ("Rs / Rp", "trip C", "slope", "window C", "ceiling", "below UT", "frac 25/open"))
    for rs, rp, tag in ((200, 22000, "withdrawn"), (240, 20000, ""), (270, 18000, "TAKEN"), (330, 15000, "")):
        a = analyse(rs, rp, verbose=False)
        print("  %-14s %-8.2f %-7.3f %-15s %-12.0f %-9s %.3f/%.3f %s" % ("%d / %d" % (rs, rp), a["trip"], a["slope"],
              "%.1f to %.1f" % a["window"]["B"], a["ceiling"], "%+.1f %%" % a["below"]["B"], a["frac_plug"], a["frac_open"], tag))
    print()
    analyse(270.0, 18000.0)
    print()
    print("FOR THE RECORD, the withdrawn network:")
    analyse(200.0, 22000.0)
