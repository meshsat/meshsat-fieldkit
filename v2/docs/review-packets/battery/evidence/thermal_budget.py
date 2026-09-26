#!/usr/bin/env python3
"""The pack's temperature thresholds and their error budget (MESHSAT-1357, round 8, stream r8bat, 26 September 2026; T3 and the mass sensitivity added on 27 September).

Proposed for filing as v2/docs/review-packets/battery/evidence/thermal_budget.py (the packet's evidence/ folder is not
this stream's to write this round). stdlib only, under a second. Every input is a published number or a figure of this
tree, named where it is used; every output is INFERRED arithmetic on them. Nothing here is measured.

Inputs:
  Semitec 103AT-2 (v2/vendor/battery/semitec-at-p12-13.pdf, sha256 389dc527...3262): the resistance table (the 103AT
    column), R25 +-1 %, B25/85 3435 K +-1 %, thermal time constant "approx. 15" s for AT-2 ("Time required to reach
    63.2% of temperature difference. Measured with sensor suspended in mid-air").
  BQ4050 (SLUSC67B, v2/vendor/battery/ti-bq4050.pdf) 6.22: RNTC(PU) 14.4 / 18 / 21.6 kohm, RNTC(DRIFT) -360 / -280 /
    -200 PPM/C. SLUUAQ3A (v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf) 5.2: readings every 250 ms, status decisions at
    1 s intervals in NORMAL; 14.9.12 / 14.9.13 / 14.9.15 / 14.9.16: OTC, OTD, UTC, UTD delay 2 s (default, written
    explicitly by the image); Sleep Voltage Time 5 s (Table 14-1, 0x4424).
  The heating rate (INFERRED, not a VERIFIED input): 3.2 K per minute, the adiabatic rate of the 12 cells at the
    chain's declared 18 A peak (POWER-THERMAL.md section 7.2, INFERRED there), computed on 600 g of cells, the Samsung
    sheet's MAXIMUM of 50 g each (Ver. 1.1 3.10, VERIFIED), at the lower of two specific heats, 0.8 J/gK (INFERRED
    there: "no Samsung figure"). The sheet gives no minimum mass, so this is NOT the fastest rate: lighter cells heat
    faster ("this is the smallest rise it allows", POWER-THERMAL.md section 7.2). The script prints the lightest cell
    for which each threshold still holds on the published terms. The charging case: 0.72 W of charge I2R
    (POWER-THERMAL.md section 9.2) into the same 600 g at 0.8 J/gK, adiabatic.
ASSUMPTION (TBD, stated): the gauge's pull-up is trimmed near 25 C (TI states "factory calibration", SLUUAQ3A
11.2.1.6.13, not its temperature), so its drift is counted from 25 C to the cell temperature.
NOT COUNTED, and TBD until the bench: the gauge's ADC and polynomial-fit error (not published), and the gradient from
the sensed cell to the hottest cell surface (the pack's thermal layout)."""
import math

T = [-50, -40, -30, -20, -10, 0, 10, 20, 25, 30, 40, 50, 60, 70, 80, 85, 90, 100, 110]
R = [329.5, 188.5, 111.3, 67.77, 42.47, 27.28, 17.96, 12.09, 10.00, 8.313, 5.827, 4.160, 3.020, 2.228, 1.668,
     1.451, 1.266, 0.9731, 0.7576]
R = [x * 1000.0 for x in R]
B = 3435.0
TOL_R25, TOL_B = 0.01, 0.01
TAU_S = 15.0                     # 103AT-2 in still air; taped to a cell the coupling is better, so an upper bound
DRIFT_PPM = 360.0                # the worst of RNTC(DRIFT), magnitude
RATE_DSG = 3.2 / 60.0            # K/s, adiabatic at 18 A on 50 g cells at 0.8 J/gK (INFERRED; lighter cells are faster)
RATE_CHG = 0.72 / (600 * 0.8)    # K/s, charge I2R alone, adiabatic
DECIDE_S, DELAY_S, SLEEP_S = 1.0, 2.0, 5.0


def ntc(t):
    k = max(i for i in range(len(T) - 1) if T[i] <= t) if t < T[-1] else len(T) - 2
    x0, x1 = 1 / (T[k] + 273.15), 1 / (T[k + 1] + 273.15); x = 1 / (t + 273.15)
    return math.exp(math.log(R[k]) + (math.log(R[k + 1]) - math.log(R[k])) * (x - x0) / (x1 - x0))


def beta(t):
    return -(math.log(ntc(t + 0.05)) - math.log(ntc(t - 0.05))) / 0.1


def ntc_tol_k(t):
    """R25 +-1 % and B +-1 %, added in the worse direction, as a temperature at the table's slope."""
    rel = math.log(1 + TOL_R25) + TOL_B * B * abs(1 / (t + 273.15) - 1 / 298.15)
    return rel / beta(t)


def pullup_k(t):
    """A pull-up drifted by DRIFT_PPM per C from 25 C reads R off by the same fraction (R_read = R * Rpu0 / Rpu)."""
    return abs(t - 25.0) * DRIFT_PPM * 1e-6 / beta(t)


def budget(name, limit, hazard, rate, mode_s):
    tol, pu = ntc_tol_k(limit), pullup_k(limit)
    lag, det = rate * TAU_S, rate * (mode_s + DELAY_S)
    tot = tol + pu + lag + det
    setp = limit - tot if hazard == "hot" else limit + tot
    print("%-34s limit %6.1f C  NTC %.2f  pull-up %.2f  lag %.2f  detect %.2f  = %.2f K  -> threshold %s %.1f C"
          % (name, limit, tol, pu, lag, det, tot, "<=" if hazard == "hot" else ">=", setp))
    return tot


print(__doc__.split("\n")[0])
print("103AT slope beta(T) per C: " + ", ".join("%d C %.4f" % (t, beta(t)) for t in (-10, 0, 45, 60, 70)))
print("103AT tolerance as temperature (R25 and B +-1 percent): " + ", ".join("%d C %.2f K" % (t, ntc_tol_k(t)) for t in (-10, 0, 45, 60, 65, 70)))
print()
print("Reading-low (hot side) and reading-high (cold side) budgets, hazard direction only:")
b_otd = budget("OTD, discharge, NORMAL", 60.0, "hot", RATE_DSG, DECIDE_S)
b_otc = budget("OTC, charge, NORMAL", 45.0, "hot", RATE_CHG, DECIDE_S)
b_utc = budget("UTC, charge, NORMAL", 0.0, "cold", RATE_CHG, DECIDE_S)
b_utd = budget("UTD, discharge, NORMAL", -10.0, "cold", RATE_CHG, DECIDE_S)
print()
print("Thresholds taken (0.1 C resolution, rounded toward the inside of the window):")
for n, v, b, hz in (("OTD", 57.5, b_otd, "hot"), ("OTC", 44.0, b_otc, "hot"), ("UTC", 1.0, b_utc, "cold"),
                    ("UTD", -9.0, b_utd, "cold")):
    if hz == "hot":
        print("  %s %.1f C: when it acts, the sensed cell is at most %.2f C (limit %.0f C), before the TBD terms"
              % (n, v, v + b, 60.0 if n == "OTD" else 45.0))
    else:
        print("  %s %.1f C: while it allows, the sensed cell is at least %.2f C (limit %.0f C), before the TBD terms"
              % (n, v, v - b, 0.0 if n == "UTC" else -10.0))
print()
print("Static reading-high error (NTC only; the pull-up drift reads LOW on the hot side), for the early edge of each trip:")
for n, v in (("OTD", 57.5), ("OTC", 44.0), ("SOT", 65.0)):
    print("  %s %.1f C: may act with the sensed cell as low as %.2f C" % (n, v, v - ntc_tol_k(v)))
print()
print("SOT (permanent, 5 s delay) upper edge in discharge: 65.0 + %.2f K = %.2f C"
      % (ntc_tol_k(65) + pullup_k(65) + RATE_DSG * (TAU_S + DECIDE_S + 5.0),
         65.0 + ntc_tol_k(65) + pullup_k(65) + RATE_DSG * (TAU_S + DECIDE_S + 5.0)))
print("Second level (U2) at its TS network, reading B: 62.7 to 77.5 C (candidate/ts_network.out); its own sensor lag "
      "and tOT_DELAY (4 s typ, +-10 %% drift, SLUSEG7D 6.6) add up to %.2f K at the 3.2 K per minute rate (50 g cells; more for lighter ones)"
      % (RATE_DSG * (TAU_S + 4.4)))
print("Mass sensitivity (the rate scales as 50 g over the real cell mass; tau 15 s, 1 s decision and 2 s delay = 18 s of")
print("rate-driven terms): the lightest cell for which each taken threshold still holds on the published terms:")
for n, v, lim, rate in (("OTD", 57.5, 60.0, RATE_DSG), ("OTC", 44.0, 45.0, RATE_CHG)):
    fixed = ntc_tol_k(lim) + pullup_k(lim)
    rate_max = (lim - v - fixed) / (TAU_S + DECIDE_S + DELAY_S)
    print("  %s %.1f C: in hand %.2f K on the published terms; holds up to %.2f K per minute, i.e. down to %.1f g per cell "
          "at 0.8 J/gK (the sheet: 50 g maximum, no minimum published)"
          % (n, v, lim - v - fixed - rate * (TAU_S + DECIDE_S + DELAY_S), rate_max * 60, 50.0 * rate / rate_max))
print("SLEEP adds (%.0f s - %.0f s) x rate of detection lag: %.2f K at the discharge rate (the pack is not discharging "
      "hard in SLEEP, so this bounds it)" % (SLEEP_S, DECIDE_S, RATE_DSG * (SLEEP_S - DECIDE_S)))


def window(thr, delay_s, rate, cold=False):
    """(low, high) of the true sensed-cell temperature at which a threshold on the gauge's reading acts.
    Hot side: it can act early by the thermistor's tolerance (the pull-up drift reads low there) and late by the
    tolerance, the drift, the lag and the detection time. Cold side: mirrored."""
    tol, pu = ntc_tol_k(thr), pullup_k(thr)
    late = tol + pu + rate * (TAU_S + DECIDE_S + delay_s)
    return (thr - late, thr + tol) if cold else (thr - tol, thr + late)


print()
print("True sensed-cell temperature when each threshold on the gauge's reading acts (the kit's controls read the same")
print("thermistors through the sensor controller; their SMBus polling interval is TBD and not counted):")
ROWS = [("UTD -9.0 C, 2 s", -9.0, 2.0, RATE_CHG, True), ("UTC 1.0 C, 2 s", 1.0, 2.0, RATE_CHG, True),
        ("C2 50 C (control)", 50.0, 0.0, RATE_DSG, False),
        ("T3 42 C (no charge start above)", 42.0, 0.0, RATE_CHG, False),
        ("T3 less hysteresis 41 C (start again)", 41.0, 0.0, RATE_CHG, False),
        ("T4 43 C (charge suspend)", 43.0, 0.0, RATE_CHG, False),
        ("OTC 44.0 C, 2 s", 44.0, 2.0, RATE_CHG, False), ("C1/K2 55 C (control)", 55.0, 0.0, RATE_DSG, False),
        ("OTD 57.5 C, 2 s", 57.5, 2.0, RATE_DSG, False), ("SOT 65.0 C, 5 s", 65.0, 5.0, RATE_DSG, False)]
for name, thr, d, rate, cold in ROWS:
    lo, hi = window(thr, d, rate, cold)
    print("  %-38s %6.2f to %6.2f C" % (name, lo, hi))
