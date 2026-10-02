# The independent verification of the findings ledger's concrete remaining risks (MESHSAT-1357, 2 October 2026)

Prototype design, desk records: nothing is bought, built, powered or measured. This page changes no engineering record. It
settles items of `FINDINGS-LEDGER.md`, section "Concrete remaining risks", by reading the cited sources and recomputing in
separate code: `verify_risks.py` beside this page (numpy, pdftotext and mutool). It reruns no record's script and imports
none of the records it checks. Its one imported input is Layer 3's accepted power model (`records/rv-pwr/pwr_budget.py`
through `records/hc2/pwr_red2.py`), used for the kit's heat in item 3. Every figure below is printed in `verify_risks.out`.
The verifier authored none of the records it checks. Where a record's figure or carrier is wrong, it is reported here and not
fixed.

**Basis.** Set 27, `fnd/int27` at `7037d714`, which carries the checkpoint `08841dfa` (items 2, 4 and 5) and L4-E10's parser
fix, L4-E7's surge round, L4-E11's charger selection and L4-E12's thermal bound. Items 3, 6, 7, 9 and 11 were paused at the
checkpoint and are settled here on that state. Items 2 and 4 were re-read on it, and item 5's last gap was re-read against
L4-E9's round 5. The held makers' sheets were read from the ignored `held/` folders (`--held-root`; the BQ25730's sha256 is
checked against L4-E11's pin).

| Item | Ledger rows | Verdict |
|---|---|---|
| 2 | L4-E10:1.2, L4-E10:2.1 | CONFIRMED |
| 3 | L4-E10:1.3, L4-E10:2.3 | CONFIRMED |
| 4 | L4-E11:1.5, L4-E11:2.5 | CONFIRMED |
| 5 | L4-E12:1.3, L4-E12:2.2 | DIFFERS |
| 6 | L4-E7R:2.5 | CONFIRMED |
| 7 | L4-E9:1.1, L4-E9:2.1, L4-E11:2.2 | CONFIRMED |
| 9 | L4-E8:2.2 | CONFIRMED |
| 11 | L4-E12:2.1 | CONFIRMED |

Tolerance for CONFIRMED: the record's printed figure to its last printed digit, or within 1 % where the two integrations
differ. Each case is stated below.

## Item 2

**Verdict:** CONFIRMED

**What was read.** `v2/docs/TEST-PLAN.md` (sha256 `42a3dff3`, L4-E10's pin, unchanged on set 27): E3-L (line 145), E3-H (line
146), E3-P (line 149), E4-T (line 152), E4-P (line 153) and P15 (line 173). The screen rows C01, C04, C05 and C16 to C18 of
`v2/docs/records/l4e10/l4e10_cell_thermal.out` and their summary in `L4E10-CELL-THERMAL.md`. The recheck
`checks/astra-check-l4e10-2.md`, blocker R2 and its closure criterion.

**What was computed and how.** `verify_risks.py` item 2: each item the recheck lists, located verbatim in TEST-PLAN.md and
verbatim in the screen row that maps it (17 pairs).

**Against the record.** 17 of 17 mapped and read at the source:
- C05: E3-H's +40 C lid-closed level held until the hot stop acts or 4 h pass; the repeat with the sensor controller in reset;
  the TMP117 fallback at +55.0 C and +56.0 C, released at +45.0 C (P15); the restart at +46.5 C or less after 30 minutes; the
  stepped run.
- C04: E3-L's lid-closed start (its +40 C level is C01's).
- C17: OTD's recovery at or below +52.5 C.
- C16 and C18: the return to 25 C with full function and capacity within 5 % (PROVISIONAL).
- The unstated charge states are named as missing inputs.

**Observation (no state change).** E3-P's "the second level does not fire" and "capacity recovery at least 95 % as E3-T" are
cited in C17 only through MAKER 7.10. They are pass items, not thermal gaps.

**Ledger.** L4-E10:2.1 and L4-E10:1.2: CLOSED.

Printed figures: `17 of 17`

## Item 3

**Verdict:** CONFIRMED

**What was read.**
- Rubitherm RT57HC (2026-01-21, "Typical Values", "a non-binding planning aid"): melting 55 to 58 C, congealing 53 to 57 C,
  240 kJ/kg ±7.5 % ("combination of latent and sensible heat" over 49 to 64 C), cp 2 kJ/kgK, 0.9 kg/l solid.
- MIL-STD-810H Method 507.6, as transcribed: Table 507.6-IX and Step 1's 23 C.
- POWER-THERMAL.md: the cells 480 to 660 J/K, the block 56.65 x 133.5 x 38.1 mm. Appendix 32.53: the kit 8 to 10 kJ/K.
- CASE-MARGINS.md section 3.2 and SHORTLIST.md (the pocket).
- L4-E10's section 4b, 4c and 15a and its out 3n and 3o.

**What was computed and how.** A two-node enthalpy model of my own: the kit, and the block of cells plus material. It is
integrated exactly piece by piece: in a sensible phase the 2 x 2 linear system under a chamber linear in time, by its matrix
exponential; while melting, the kit alone with the block held at the melting point. Each phase change and each interior
maximum is located by bisection on the closed form.
- Inputs: the kit's heat from Layer 3's model (24.996383 W, SURV-R on shore; the T-H1 floor 24.996383 / 15 = 1.666426 W/K,
  which L4-E10 prints as 1.6664); the corners as L4-E10 states them.
- The least mass that keeps the cells at or under +60 C is found by bisection, at 60 s substeps; 10 s gives the same mass to
  1e-6 kg.
- The record's reading of the material is kept: 258 kJ/kg, all of it latent at 58 C, the solid density, no container.

**Against the record.**

| Exposure | Volume | The record |
|---|---|---|
| E3-O, conditioned corner | 0.1621 L | 0.162 L |
| E5, conditioned corner | 1.4879 L | 1.489 L |
| E3-S, best corner | 0.2750 L | 0.275 L |
| E3-S, worst corner | 1.1735 L | 1.175 L (0.13 %, the explicit integration's step) |
| E5, best corner | 0.1019 L | 0.102 L |

- The no-store peaks agree to 0.01 C (68.85, 74.72, 70.65, 71.00 and 66.71 C).
- The latent heat each store must hold: 37.6 kJ (10.46 Wh), 345.5 kJ, 63.9 to 272.5 kJ and 23.7 kJ.
- The pocket: 0.0559 L at the worst stack and 0.0865 L as designed, on CASE-MARGINS' chosen column throughout. This agrees with
  L4-E10's corrected 0.0865 L (my checkpoint's interim reading, now applied by the record).
- Every case needs more than 0.0865 L, so approach (III)'s rejection on volume holds. E5 needs more than the pocket even at
  the best corner (0.1019 L), and E3-S at both corners, so those rejections do not depend on the conductance.

**Physical reasoning.** The record's material figures are favourable, and the check shows the direction. Melting at 55 C with
222 kJ/kg (the low tolerance) needs 0.2513 L for E3-O and 0.3823 L for E3-S's best corner, both more. The model also counts the
sensible heat over 49 to 64 C twice and refreezes at 58 C rather than at the congealing 53 to 57 C, both in the material's
favour. So a "does not fit" holds.

**Ledger.** L4-E10:2.3: CLOSED. L4-E10:1.3, whose other remainders (2.2 and 2.4) were already CLOSED: CLOSED.

Printed figures: `0.1621 L`, `1.4879 L`, `0.2750 L`, `1.1735 L`, `0.1019 L`, `0.0865 L as designed`, `0.2513 L`, `0.3823 L`, `1.666426 W/K`

## Item 4

**Verdict:** CONFIRMED

**What was read.**
- TI SLUSE66A (BQ25731, revised January 2021), p.10, section 8.5:
  - the table's condition "TJ = -40°C to +125°C, and TJ = 25°C for typical values (unless otherwise noted)";
  - ICHRG_REG_ACC with a 5 mOhm RSR, "VBAT above VSYS_MIN (0°C to 85°C)": 0x0200 (1024 mA) at -18 % / +21.5 %;
  - ICLAMP: 384 mA, typical only.
- Board A's R17, "5mOhm 1% 2512" (`gen_sch_a.py`).
- L4E11 section 4 (R-b and its three cases) and register row R-136.
- On set 27, L4-E11 section 14 selects TI's BQ25730 (a draft, not applied). Its sheet, SLUSE65A (revised January 2024, held,
  sha256 pinned), prints the same p.10 row under the same TJ table, with the same clamp (typical only).

**What was computed and how.** 1.024 A x 1.215 / 0.99 and 1.024 A x 0.82 / 1.01; Q2's diode at 1 V and 50 C/W over the 62.1 C
air; R-b's charge power at 16.884 V.

**Against the record.** 0.8314 to 1.2567 A (the record 0.8314 to 1.2567 A); Q2 at TJ 124.936 C (the record 124.9 C), against
150 C; 21.22 W (the record 21.22 W).
- R-b's bound holds only inside the row's condition. Outside it, case (ii) (outside 0 to 85 C, the charger's own rise counted)
  and case (iii) (under VSYS_MIN) are INCONCLUSIVE, and R-136 carries both with Q2's acceptance.
- Under the BQ25730, case (i) and case (ii)'s gap carry over unchanged. Case (iii) moves to R-b' (E11-28, R-158), which is
  outside this item.

**Observation (no state change).** R17's temperature coefficient is not in the bound. At 75 ppm/K over 60 K the bound is
1.2624 A and Q2 125.22 C; at 200 ppm/K, 1.2720 A and 125.70 C. Both are far under 150 C. R-136's re-derivation should carry
R17's part and its coefficient.

**Ledger.** L4-E11:2.5 and L4-E11:1.5: CLOSED AS CONDITIONAL (R-136).

Printed figures: `0.8314 to 1.2567 A`, `124.936 C`, `21.22 W`, `1.2624 A, Q2 at 125.22 C`, `1.2720 A, Q2 at 125.70 C`

## Item 5

**Verdict:** DIFFERS

**What was read.**
- TI SNOSD82D (TMP117, revised September 2022):
  - p.1: ±0.15 °C maximum from -40 to 70 C;
  - p.6, section 6.5: the same MAX row over free-air temperature at 8 averages, a 1-Hz cycle, the DRV pad unsoldered and I2C
    inputs near the rails. The N grade prints ±0.2 °C and no ±0.15 °C row. Board B's part is TMP117AIDRVR.
- L4-E12's section 5d and its constants READ_S 1 s and TAU_S 60 s, "a sensor's thermal time constant in the case's moving air"
  (`l4e12_thermal.py`).
- Register rows R-138, R-139 (L4-E9 round 5) and R-146.

**What was computed and how.**
- The lag: 15.0 K/h x (1 + 60) s.
- The thresholds: 55 - 0.15 - 0.5 - lag and 50 - 0.15 - 0.5 - lag.
- The break-even time constant of the 54.0 C setting.

**Against the record.** The row and the arithmetic are CONFIRMED:
- the lag is 0.254167 K;
- the SGP41 switches off at a reading of 54.095833 C, set at 54.0 C, and reaches at most 54.904167 C;
- it switches on and is used at 49.095833 C, set at 49.0 C, and reaches at most 49.904167 C;
- the setting holds while the time constant is at most 83.0 s (71.0 s on the N grade).

**What DIFFERS: the lag's new carrier.** R-139 now names the lag. Its acceptance reads: "the SGP41's shutdown lag measured on
the bench, from the TMP117's reading crossing 54.0 C to the part's off state, at most the 61 s assumed".
- That interval holds the reading period and the firmware's and switch's response, about 1 s of the 61 s.
- The 60 s thermal time constant lies before the reading crosses 54.0 C. The reading already lags the SGP41 by 15 K/h x 60 s =
  0.25 K at that moment.
- So the measurement cannot see the time constant. It would pass while the assumption that carries 60 of the 61 s goes
  untested.
- **Consequence:** the 54.0 C setting stays unverified against a slow sensor. A time constant over 83.0 s lets the SGP41 pass
  its absolute +55 C before it is switched off.
- **The carrier that would close it:** R-139's or R-146's acceptance measures the TMP117's reading against a reference
  thermocouple at the SGP41, on a ramp of at least 15 K/h. The reading must be at most 0.254167 K behind at 54.0 C, which is a
  time constant of at most 60 s; the setting holds to 83.0 s.

**Ledger.** L4-E12:2.2 and L4-E12:1.3 stay STILL OPEN, with this consequence named.

Printed figures: `0.254167 K`, `54.095833 C`, `54.904167 C`, `49.095833 C`, `49.904167 C`, `83.0 s`, `71.0 s`, `about 1 s of the 61 s`


**RESOLVED by correction at set 27 (the coordinator, 2 October 2026).** The DIFFERS above stands as filed. Its correction is applied:
R-139 in L4-E9's register (`DOWNSTREAM-REGISTER.md`, the round at `42f3a98e`) now reads "the TMP117 reading's lag behind a reference
thermocouple at the SGP41, on a ramp of at least 15 K/h, at most 0.254167 K at 54.0 C", which tests the sensor's time constant this
item found untested. The coordinator read the restated row against this item's specification. The ledger's rows L4-E12:1.3 and 2.2
are therefore CLOSED AS CONDITIONAL on that bench test.
## Item 6

**Verdict:** CONFIRMED

**What was read.**
- The drafted entry: `apply_gen_sch_e_input_limit.py` and `apply_gen_sch_e_backstop.py`.
  - PV_P carries the three 33 uF 50 V bulk cans.
  - The bank R60 to R64 (five 70 mOhm WSL2512, 14 mOhm) runs from PV_P to TRK_VS.
  - TRK_VS carries D4 (SMCJ28A) and C71 to C74.
  - R59 (15 mOhm HoJLR2512) runs from TRK_VS to TRK_VIN, which carries C13 to C15 and C64.
- 8705af p.2: VCSPIN-VCSNIN -0.3 to 0.3 V.
- Littelfuse SMCJ28A, p.2: VBR 31.10 to 34.40 V, VC 45.4 V at IPP 33.1 A.
- Figure 3 (page rendered and read): 100 % to 25 C, then straight to 60 % at 150 C, which gives 0.8813 at 62.1 C.
- Figure 4: tf 10 µs drawn to the peak, td 1000 µs.
- Panasonic ZA EEHZA1H330XP: 40 mOhm, ±20 %, endurance ±30 % and 200 %, 0.8 Ohm at -40 C.
- HoJLR2512 p.4: life 1 %, solder 0.5 %. Vishay WSL p.2 and p.3: 75 ppm/K, (1.0 % + 0.5 mOhm) and (0.5 % + 0.5 mOhm).
- L4E7-CONTROL-DECISION.md check (c), and on set 27 the panel lead's derivation (CS116 and CS115).

**What was computed and how.**
- My own nodal model of that network, integrated by the trapezoidal rule (implicit), with D4 as a piecewise-linear branch
  solved each step. The record's integrator is explicit.
- The resistor bands are mine from the sheets: R59 at most 15.447 mOhm (the record's 100 ppm/K over 45.1 K); the bank 13.412
  to 14.606 mOhm.
- The capability pulse uses the record's 10/1000 µs double exponential: peak at 20.61 µs, a 1.25 x (t90 - t10) front of
  8.95 µs, half value 1022 µs.
- As a check of the waveform, the same pulse with its peak at 10 µs, Figure 4's "tf" read as the time to peak.
- M7 is the 150 pF and 330 Ohm discharge with Table IX's +30 %.
- CS116 is a 1 MHz damped sine of 10 A, Q 10 and 20, both polarities, from both of the record's starts.

**Against the record.**

| Case | U5 here | The record |
|---|---|---|
| Capability, cold end | 0.2094 V | 0.2094 V |
| Capability, hot end | 0.1441 V and 0.1613 V | the same |
| M7, 15 kV | 0.1967 V | 0.1973 V |
| M7, 8 kV | 0.1319 V | 0.1322 V |
| CS116 bound (the whole current in R59) | 0.2123 V (U18 0.2007 V) | 0.2123 V (0.2007 V) |
| CS116 in the network | 0.1235 V, least -0.0059 V | 0.1238 V |

- M7 at 15 kV: 0.1967 V is the step-converged value (0.1964 V at 0.25 ns). The difference from 0.1973 V is 0.0006 V, the
  explicit step's.
- CS116 in the network: D4 carries nothing.

Every figure is under the 0.3 V rating. The worst case is the capability scenario's cold end, at 0.0906 V margin.

**Observation (no state change).** If Figure 4's "tf = 10 µs" is read as the time to peak, the cold end reads 0.2292 V, still
under 0.3 V. The record's shape has its peak at 20.6 µs.

**What stays downstream.** The lumped model stops at the board's parasitics: the first nanoseconds of M7, and CS116 above
1 MHz. These, the bench row 7b.18 and Vishay's pulse capability remain R-99, R-101, M3 and M7.

**Ledger.** L4-E7R:2.5 stays OPEN DOWNSTREAM, now with a targeted verification of its figure.

Printed figures: `U5 0.2094 V`, `0.1967 V extrapolated`, `0.1319 V extrapolated`, `= 0.2123 V`, `U5 at most 0.1235 V`, `U5 0.2292 V`, `0.015447 Ohm`

## Item 7

**Verdict:** CONFIRMED

**What was read.**
- TI SLPS540C (CSD19536KTT, revision C, May 2025):
  - p.6, Figure 4-10, read from the page's vector drawing (mutool's trace), with the frame, the tick labels, the 400 A IDM line
    and the 100 V edge as anchors, and each line taken by its legend colour;
  - p.1: TJ to 175 C;
  - p.3: gfs 329 S, typical only.
- TI SLUSEE5E (TPS4811-Q1):
  - p.23, Equation 7;
  - p.9, the TMR rows: 73 / 82 / 91 µA and 1.112 / 1.2 / 1.3 V;
  - p.10, the loaded tOC row: 370 µs typical at CTMR 22 nF;
  - p.20, Equation 3 (the slew).
- L4E11 section 3c and L4-E9's derating (A-25).

**What was computed and how.**
- At 43.18 V the chart reads 100 µs 221.7 A, 1 ms 20.02 A, 10 ms 6.229 A and DC 3.177 A (the record: 221.7 / 20.02 / 6.228 A).
- The record's derating of 0.4454 is (150 - 94.32) / 125. On this part's 175 C it is conservative while the case stays under
  108.19 C; its own derating at 94.3 C would be 0.5380.
- The breaker:
  - Equation 7 with the record's CTMR band gives 0.2471 / 0.3220 / 0.4262 ms;
  - the loaded row is 1.1492 times the typical, so the maximum is 0.4898 ms;
  - the slew is 17.28 to 24.65 V/ms.
- My own time-stepped fault scan (the gate-following output, the overcurrent timer, the short-circuit filter, tSC 5 µs) covers
  0.1 to 1000 Ohm, both slews, 22.1 and 49.5 uF, refined to 0.1 µs near the worst case. Each point is held against the chart
  for the whole pulse, as the record does.
- The hard-short start: gfs x the highest slew.

**Against the record.**

| Case | Here | The record |
|---|---|---|
| Resistive fault | 0.7043 at 1.223 Ohm, 0.9632 ms, ended by the short-circuit trip | 0.704 at 1.21 Ohm, 0.954 ms |
| Hard-short start | 73.36 A at 9.044 µs, 0.7429 | 73.4 A, 9.04 µs, 0.743 |
| Overcurrent delay maximum | 0.4898 ms | 0.49 ms |

The resistive fault's maximum is flat: the finer grid moves the resistance and duration, not the fraction.

**Physical reasoning.** Figure 4-10's grey RDS(on) line is a conduction limit, not a thermal one. Derating it would be
meaningless, and the fault scan near a completed start (VDS under 2 V) sits under the 400 A corner. The record skips VDS under
2.2 V to the same effect.

**What stays conditional or downstream.** The typical transconductance taken as a bound (A11-10, E11-17, R-118); the hard short
in service, which rests on the loop inductance (R-134); the case staying under 108.19 C for the derating.

**Ledger.** L4-E9:1.1, L4-E9:2.1 and L4-E11:2.2 stay OPEN DOWNSTREAM, now with a targeted verification of their figures.

Printed figures: `100 us 221.7 A, 1 ms 20.02 A, 10 ms 6.229 A`, `0.4898 ms`, `0.7043 of the derated chart`, `0.7429 of the derated 100 us line`, `108.19 C`

## Item 9

**Verdict:** CONFIRMED

**What was read.**
- TI SNVSAI1D (LM5176, revision D):
  - p.6: gmEA 1.31 mS and ROUT 20 MOhm, both typical only; VREF 0.800 V;
  - p.24: ACS 5;
  - pp.26 to 28, Equations 38 to 46: the boost output pole at Rout / 2, the RHP zero Rout (1 - D)^2 / L, and the type II
    compensator with Cc2.
- `gen_sch_a.py`: the front end at 240k over 10k (20 V), with L1 10 uH.
- L4E8-BANK.md and `ripple_dense.out` out 7: the plant's corners and bands. B3's envelope is 171.763 to 227.078 kHz. The
  ceramic band is r4-decisions' 60 to 102 uF for fifteen parts. HoJLR's 50 ppm/K gives the ballast's ±1.375 %.

**What was computed and how.**
- My own loop model: T = kFB gmEA g Zc Gc Zout.
- Its phase is the sum of each factor's own angle, so no unwrapping is needed.
- Every |T| = 1 and every -180 degree crossing is located by bisection on the closed form, not read at a grid point.
- The corners are the record's: three modes, two ceramic ends, four loads to 8.300 A, Q 0.4 / 0.8 (widened 0.4 / 1.5 with L
  x0.8 / x1.2), both frequency ends, gmEA x0.8 / x1.2, and the bank at 0.56 / 1.56 x 330 uF with the ballast at either end.
- The sampling double pole at Fsw / 2 is the standard current-mode term. The sheet's equations do not print it; it is kept, as
  the record keeps it.

**Against the record.**

| Case | Here | The record |
|---|---|---|
| Cold corner (every can at 300 mOhm, Cc2 3.3 nF) | PM 86.1 deg, GM 15.79 dB, widened 14.38 dB | 86.1 / 15.8 / 14.4 |
| Cc2 x0.75 at the cold corner | GM 13.71 / 12.28 dB | 13.7 / 12.3 |
| Cc2 x1.25 at the cold corner | PM 81.5 deg, GM 17.42 / 16.01 dB | 81.5 / 17.4 / 16.0 |
| Cc2 x1.25, e 0 | PM 57.0 deg | 57.0 |
| Cc2 3.3 nF, e 0 | PM 61.4 deg | 61.4 |
| Drawn 680 pF at the cold corner | GM 4.96 / 3.14 dB, a margin missed | 5.0 / 3.1 |

- In every Cc2 3.3 nF row, |1+T| is at least 0.74, the crossover stays at most 2.55 kHz (under Fsw / 20 and fRHP / 3), and
  |Zout| stays at most 220 mOhm against Middlebrook's 803 mOhm.
- The ledger's "worst PM 61.4 degrees" is the nominal Cc2. Over Cc2's tolerance the worst are PM 57.0 deg and widened GM
  12.28 dB, both inside the 50 deg and 10 dB criteria.

**What stays conditional.** The bank's ESR envelope at -20 C over life, at or under 300 mOhm per can (R-68); gmEA's ±20 % and
the sampling pole's Q band (assumptions the record names).

**Ledger.** L4-E8:2.2 stays CLOSED AS CONDITIONAL, now with a targeted verification.

Printed figures: `PM 86.1 deg, GM 15.79 dB (widened 86.1 deg, 14.38 dB)`, `PM 88.7 deg, GM 13.71 dB (widened 88.7 deg, 12.28 dB)`, `PM 57.0 deg`, `GM 4.96 dB`

## Item 11

**Verdict:** CONFIRMED

**What was read.** L4-E12's out 0f lists the 22 statements whose heading the record checked. The SGP41's four were read by check
3. The other 18, on 13 parts, were each found on its own sheet's page, and the nearest heading before each row was read on that
page. A heading is matched only where it stands as a heading (at a line start or a column start), not in a sentence. The
category compared is the record's own (`CAT` in `l4e12_thermal.py`).

**Against the record.** 18 of 18 match.
- Under "Recommended Operating Conditions", the record says recommended: PCM2912A TA (p.5), TLV755P TJ (p.4), TLV758P TJ (p.5),
  TUSB8041 TJ (p.9), SN74LVC2G07 TA (p.5), SN74LV1T08 TA (p.5) and AP64500 TJ (p.5).
- Under "Absolute Maximum Ratings", the record says absolute: PCM2912A's bias and storage rows (p.5), TLV755P TJ (p.4), TLV758P
  TJ (p.4), TPS62933 TJ (p.5), AP64500 and AP63200 TJ (pp.5 and 4), AP2112 TJ (p.3), and CSD17577Q5A and CSD17578Q5A (p.1).
- BME688 storage sits under Table 11, "Absolute maximum ratings" (p.15).

**Ledger.** L4-E12:2.1 stays CLOSED, its remaining reading now done.

Printed figures: `18 of 18 statements on 13 parts`

## Reproduce

`python3 v2/docs/records/l4close/verify_risks.py --held-root <a checkout with the held sheets> > v2/docs/records/l4close/verify_risks.out`.
It needs numpy, pdftotext and mutool. It is read-only and single-threaded, and takes about 90 s. It exits 1 if a source line
is not where it reads it. Two runs give the same bytes.
