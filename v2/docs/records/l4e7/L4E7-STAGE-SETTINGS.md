# L4-E7: real component settings for board E's solar stage (layer 4, MESHSAT-1357)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured. Implementable choice 3 of
`../l4e/L4-ENERGY-ARCHITECTURE.md` (finding O-2, "the stage's input power is not controlled"; review L4-R01). Every figure
below is printed by `l4e7_stage_settings.py` into `l4e7_stage_settings.out`, which first reproduces `../l4e/l4e_replay.out`
and `../l4e5/l4e5_source_control.out` byte for byte in child processes and runs the replay's `main()` in-process with its
locals captured, so section 11's own `i_factor`, the replay's `hold()` and `trace()`, and its `meanday()` and `least()` do
the arithmetic. Bases: MAKER (document, revision, page), NETLIST, CATALOGUE (filed under `inputs/`), MODELED, INFERRED,
ASSUMPTION, SESSION.

## As drawn (NETLIST)

U5's CSPIN, CSNIN and VIN all sit on PV_P and IMON_IN has R16 10k alone: the input-current sense is tied off (8705af p.12),
so no input limit acts on the board today. O-2's 3.548 A was a setting on a 1 mA grid with no parts behind it. U5's LCSC
field is C674164, LT8705AEUHF#TRPBF: the E grade. R8 102k over R9 7.50k at 1 % hold the panel at 16.695 / 17.593 / 18.490 V.

## The decisions (SESSION, engineering, with reasons)

| Item | Choice | Tolerance and TCR, with source | Reason |
|---|---|---|---|
| U5 grade | **LT8705AI**, LT8705AIUHF#PBF, LCSC C674169 (C674170 on reel) | A7 gm 0.94 / 1.06 mmho, FBIN 1.184 / 1.226 V, both full range (MAKER 8705af pp.4, 5) | The drawn land is the QFN, offered only in E and I (p.3); H and MP are TSSOP only. Only I is guaranteed below 0 C junction (p.6 Note 3); the kit starts at -20 C (REQ-024, D-02a). Junction -20 to 105.4 C (INFERRED: 2 x 49 + 2 x 32 nC max gate charge, Infineon BSC028N06NS Rev.2.1 p.3 and BSC039N06NS Rev.2.4 p.4, at 235 kHz, 4.2 mA, EXTVCC at L4-E5's 30.15 V, theta-JA 34 C/W, 62.1 C air), inside I's -40 to 125 C. LCSC held no stock on 1 October 2026; U5 is bench-fitted |
| RSENSE1 (new R59) | **15 mOhm**, Milliohm HoJLR2512-3W-15mR-1%, LCSC C2903494 | +-1 % (CATALOGUE; MAKER Ho-A0 p.1, F); +-50 ppm/K (p.2), tested +25 to +125 C only (p.4); soldering < +-0.5 %, load life < +-1 % (p.4) | The family value that puts the limit nearest A7's printed 50 mV test point (p.5; no A7 offset row is printed): 52.1 mV at the setting |
| RIMON_IN (R16) | **23.2k**, YAGEO RT0603BRD0723K2L, LCSC C861244 | +-0.1 %, +-25 ppm/K (MAKER RT series V.16, May 06 2025, p.2 codes B and D; CATALOGUE); TCR tested +25/-55 and +25/+125 C (p.7); life and soldering +-(0.5 % + 0.05 Ohm) (pp.7, 8) | The largest stocked setting whose 25 V corner stays at or under 100 W at both ends under the design floor (below). Setting 1.208 V / (1 mmho x 15 mOhm x 23.2k) = **3.4713 A** |
| CIMON_IN (new C65) | 100 nF X7R 0603, LCSC C14663 | | Above p.31's 100 / (f x RIMON_IN) = 25.4 nF at the slowest oscillator, at the 0.1 uF end p.31 asks for in a current loop; tau 2.32 ms |
| R8 / R9 (the hold) | **94.2k** RT0603BRD0794K2L (C861602) over **7.5k** RT0603BRD077K5L (C728597) | as RIMON_IN (same sheet, same codes) | Of 97 stocked pairs with a nominal from 15.5 to 17.5 V, the one whose band's worse end gives the most energy on SC-37's day (the model's hourly maximum-power voltage there is 16.34 to 16.70 V). Nominal **16.340 V** |

**The design floor (SESSION).** EA2's and EA3's gains are printed TYP only and the references' line regulation only at
25 C, not switching. The setting is chosen so that the 25 V corner passes with EA2 at half its typical (65 V/V) over VC's
whole absolute range, the line regulation at twice its printed maximum, and the resistors' printed soldering-heat and
load-life limits stacked on their tolerance and TCR. The next larger stocked setting, 22.6k (3.5634 A), passes at the
typical rows (98.80 W) but fails this floor (102.32 W).

## The 100 W corner check on the achieved values, both temperature ends

Envelope 15.538 V (the hold's lowest) to REQ-016's 25 V; I grade; 60,736 corners an end. Cold end: every part at -20 C.
Hot end: RIMON_IN at the 62.1 C worst inside air, RSENSE1 at 70.1 C (0.24 W at the limit's highest current, by the derating
line's 33.3 K/W, INFERRED). The worst corner is 25 V at both ends.

| Stack | Cold end | Hot end |
|---|---|---|
| A. The check: printed limits, EA2 at 130 V/V, line at its printed maximum | **96.2474 W** (margin 3.75 W) | **96.2291 W** |
| B. Printed rows alone (EA2 and line left out) | 95.2909 W | 95.2727 W |
| C. The design floor (EA2 65 V/V, line x2, drifts) | 99.6739 W | 99.6549 W |
| D. Drifts at the typical rows | 98.6931 W | 98.6743 W |

The script refuses above 100 W. For comparison, O-2's 3.548 A on these parts takes 98.375 W. The conditions hold: 57.5 mV
across RSENSE1 at the limit's highest (100 mV range, p.5), IMON_IN 60.9 uA (at least 100 uA), the fault at up to 76.7 mV,
and the candidate panel's hot short circuit 97.4 mV.

## What stays INCONCLUSIVE, and the measurement for each

| Row (no printed bound) | Break-even for this setting | Measurement |
|---|---|---|
| EA2's voltage gain (130 V/V TYP, p.5) and VC's operating range | the corner passes down to **25.0 V/V** (cold), 24.9 (hot); with the drifts and line x2, 55.2 / 54.7 V/V | In input-current limit at 25 V, move VC across its range by the load; the gain is dVC / dV(IMON_IN). Accept at or above 65 V/V |
| IMON_IN line regulation while switching and at temperature (printed 25 C, not switching, p.4) | up to 61.6 times its printed maximum (47.1 at EA2 65 V/V) | the limit's current at VIN 16 and 25 V, switching, at both ends |
| RSENSE1's TCR below +25 C (HoJLR p.4 tests +25 to +125 C; the cold end applies it, ASSUMPTION) | up to 882 ppm/K | R59 at -20 and +25 C |
| EA3's gain (90 V/V TYP) and the FBIN bias (10 nA TYP) | energy only: band 15.538 to 17.148 V at EA3 half | the hold read at both ends |
| U5's junction (INFERRED) | 105.4 C against 125 C | CLKOUT duty cycle, p.34 (+-10 C) |

A design margin answers the review's question: with no printed EA2 minimum, the corner passes for any EA2 gain at or above
25 V/V, a fifth of the typical, at a cost of 0.0 Wh a day on the design day (below). The source's own compliance (O-1) and
the efficiencies (C-8) are not changed by this record.

## The energy (MODELED: the replay's trace, SunPower SPR-E-Flex-100 1S1P, SC-37's mean September day)

| Hold | As drawn (no limit) | Chosen, limit lowest / nominal / highest | Zero-margin 22.6k, same |
|---|---|---|---|
| lower corner 15.763 V | (16.695 V: 373.5) | 372.0 / 371.9 / 371.9 | 371.9 / 371.9 / 371.9 |
| nominal 16.340 V | (17.593 V: 350.0) | 375.0 / 375.0 / 375.0 | 375.0 / 375.0 / 375.0 |
| upper corner 16.921 V | (18.490 V: 280.6) | 370.6 / 370.6 / 370.6 | 370.6 / 370.6 / 370.6 |
| EA3 at half: 15.538 / 17.148 V | | 369.8 / 365.8 (lowest) | 369.4 / 365.8 |

**The hold's cost.** Against PVGIS's maximum-power 378.0 Wh a day, the band gives up 3.0 to 7.4 Wh (12.2 Wh at EA3's
floor), where the drawn band gave up 4.5 to 97.4 Wh. **The margin's cost.** 0.0 Wh a day at every cell of SC-37's day: the
limit's lowest binds only above 520 to 537 W/m2 (the day peaks at 520.7), and where it binds below the panel's
maximum-power point the voltage rides up toward it (+0.0 to +0.4 Wh). On a brighter hour that binds, the stage's input falls
2.6 % against the zero-margin setting.

A2 (base 4S6P plus lid 4S9P) on the new nominal trace, 375.0 Wh a day: unserved 944.3 / 1131.8 Wh at 48 h and 1677.2 /
1864.7 at 72 h, least addition +936.7 / +1656.0 Wh (was 986.9 / 1196.1, 1741.4 / 1950.7, +979.2 / +1719.7 at O-2 nominal).
At the new least-energy corner (370.6 Wh): +944.3 / +1667.4 Wh (was +1097.1 / +1896.6 at 280.6 Wh). A1: +1319.3 / +2030.8 Wh
nominal (was +1361.5 / +2094.1). The gap to the profile stays open on this panel; the new hold lowers the least additions by 42.2 to 229.2 Wh.

## The interaction with L4-E5

No contradiction. The three drafts touch neither R10 nor C26 and C27, apply in either order and on top of L4-E5's R10
change (tested), and leave R10's line intact. U5's junction is taken at L4-E5's raised EXTVCC, 30.15 V: 105.4 C, where the
drawn output's 15.56 V gave 84.5 C. The stage's input stays under REQ-016's window, which L4-E5's line was sized for. L4-E5's
energy figures were computed on the drawn hold; this record does not re-run them.

## Bench rows

- **7b.9, steady state:** a PV emulator puts the loaded input at the limit from 15.763 V to 25 V, at the load's maximum,
  cold-soaked at -20 C and in 62.1 C air: V_in x I_in at or under 100 W at every point (at 25 V, at most 4.000 A).
- **7b.9t, transients, recorded apart:** a source step and an irradiance step; peak and time above 100 W. SESSION limit: no
  fault trip (IMON_IN under 1.55 V) and no more than five time constants, 11.6 ms, above 100 W.
- **7b.10** EA2's gain, **7b.11** the line row, **7b.12** the hold (15.763 to 16.921 V at both ends), **7b.13** U5's
  junction by CLKOUT, as in the table above.

## For board E's generator owner (drafts, nothing applied)

`apply_gen_sch_e_u5_grade.py` (U5 to C674169), `apply_gen_sch_e_hold.py` (R8, R9, the panel entry's declared 16.3 V) and
`apply_gen_sch_e_input_limit.py` (R59 and the new net TRK_VIN behind it, carrying U5's VIN and CSNIN, C11 to C15, C64 and
Q3's drain; R16 23.2k; C65; the declarations). Each asserts its old text once and new text different, refuses a second
application, and refuses the tree's own generator until a `RELEASE.md` names an accepted check. Owed beside them: R59's
Kelvin taps and placement, the regeneration and its gates, the section title's "FBIN 17.6 V", and the requirement records
that name the 225 uF "on PV_P" (behind R59 after the change). After any application l4e_replay.py section 11, l4e5 and this
record refuse by design: they record the circuit before it.
