# L4-E7: qualification of the 100 W bound (layer 4, MESHSAT-1357)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured. The owner's instruction of 1 October
2026: qualify the 96.25 W result precisely. Every figure here is printed by `l4e7_stage_settings.py`, section 9 of
`l4e7_stage_settings.out` (which reproduces `../l4e/l4e_replay.out` and `../l4e5/l4e5_source_control.out` byte for byte
first). The decisions and the corner check are on `L4E7-STAGE-SETTINGS.md`. Second round: after the focused check
`checks/astra-check-l4e7q-1.md` (NOT YET, B1, B2 and five minors; see the last section).

**What follows from it (L4-E7R, 1 October 2026): `L4E7-CONTROL-DECISION.md`.** The result below stays CONDITIONAL;
the control decision places a hardware trip under the limit whose bound needs none of the five values: it rests on
printed limits and two named assumptions about its own sensor, each carried past its physical meaning (third round,
2 October 2026).

## The sheet

The owner names https://www.analog.com/media/en/technical-documentation/data-sheets/8705af.pdf. The live site resets this
runner's connection; the Internet Archive's snapshot **20250322064938** of that exact URL, fetched with the id_ form, has
sha256 **8f552a0b57677bfa7e4a5d5d0fac56d56fbbd1a6f65a9ee7aaaf8743cd534ec3**, byte-identical to the held
`v2/vendor/power/lt8705a.pdf` (`inputs/ia-8705af-20250322064938.json`). The sheet prints its document code **8705af** on
each of its 44 pages and carries no revision table. Only its rows are used.

## The classification

"small" means a nonzero effect of the stated size.

| id | Unprinted value | Bound | Loop stability | Protection | Other |
|---|---|---|---|---|---|
| EA2 | EA2's gain and VC's operating range | **Y** | **Y** (no printed minimum gain or gm) | N (only under 4.68 V/V, and then a fault stops switching, the safe side) | energy, only when the limit binds |
| A7 | A7's gain outside its test point (50 mV differential, CSPIN at 5.025 V) | **Y** | **Y** (the sense path's gain enters the loop in proportion) | **Y** (the comparator's threshold voltage does not move; the input current at which it trips moves inversely with the effective gain) | energy, only when the limit binds |
| LINE | the IMON_IN reference's line regulation while switching and at temperature | **Y** | **small**: the setpoint moves with the source voltage, a feedforward path, over the envelope's 8.580 V swing at most 0.0429 % printed, 0.0858 % assumed | N (the fault would need 402 times the printed value) | energy, a fraction of a percent, only when it binds |
| TCR | RSENSE1's TCR below +25 C | **Y** | **small**: the sense-path loop gain moves with RSENSE1, -0.2255 % from 50 to 100 ppm/K at -20 C | **small**: the comparator's threshold voltage (IMON_IN 1.55 / 1.61 / 1.67 V, p.5) does not move; the input current at which it trips moves with 1 / RSENSE1 (p.31), +0.2260 % from 50 to 100 ppm/K | as LINE |
| HOLD | EA3's gain and the FBIN bias | N (they set the envelope's low end, 16.419845 V, where the matching stacks read 63.1883 W (A), 65.4106 W (C, the drifts included) and 65.5580 W (every conservative assumption) against 96.2474, 99.6739 and 99.8992 W at 25 V) | **Y** (the input-voltage loop) | N (a regulation, not a protection) | **energy (the hold band)** |
| TJ | U5's junction temperature | **Y**, as a condition only: every LT8705A row the corner uses is full range for the I grade, -40 to 125 C junction (p.6 Note 3) | N (inside EA2's and A7's rows) | **Y** (overtemperature at approximately 165 C, p.34) | lifetime (Note 3: derated above 125 C) |

The fault-to-limit ratio does not depend on RSENSE1. At its least it is 1.248653 under stack A (the regulation at most
1.241337312 V with the line and EA2 allowances) and **1.236365** with every conservative assumption (the regulation at most
1.253674623 V); 1.55 / 1.229 left those allowances out.

## Guaranteed limits searched, and what stands in where none exists

For every manufacturer row the qualification needed is a limit the manufacturer warrants, with the conditions it applies
to. Characterization over production lots is supporting evidence, not a production guarantee: each row stays CONDITIONAL
until a warranted limit exists.

| id | What the sheet gives | Conservative assumption | Qualification it requires | Margin kept, break-even |
|---|---|---|---|---|
| EA2 | p.5: gain 130 V/V and gm 185 umho, typical only; p.4: the IMON_IN regulation full range at VC = 1.2 V; p.2: VC's absolute maximum -0.3 to 2.2 V; p.7 and p.8 curves plot VC within 0.5 to 2.0 V (**TYPICAL**, TA = 25 C); p.31 names 1.208 V typical and no gain bound. **No guaranteed limit** | EA2 at least 65 V/V, VC anywhere in its absolute range | Analog Devices: EA2's minimum gain, or the IMON_IN regulation point's shift with VC, over -40 to 125 C junction, warranted. 7b.10 checks the design only | 2.8579 W under it alone; 25.026426 V/V (stack A, cold), 55.191656 V/V (stack C's other terms) |
| A7 | p.5: gm 0.95 / 1.05 mmho at 25 C and 0.94 / 1.06 mmho full range (E, I), each at VCSPIN - VCSNIN = 50 mV and VCSPIN = 5.025 V; 1.5 to 80 V common mode and -100 to 100 mV differential are operating ranges; p.8 "IMON Output Currents" plots the output current against the differential only (**TYPICAL**, TA = 25 C); no curve against common mode, no transfer-error or offset row. **No guaranteed limit at the design's 16.420 to 25 V common mode and up to 57.5 mV differential, or while switching** | the test-point limits apply there (an extrapolation, ASSUMPTION) | Analog Devices: A7's transfer error (gm and offset) over the common mode, differential, -40 to 125 C junction and switching the design uses, warranted | 3.7526 W (stack A); the effective gain may fall to 0.904726 mmho (3.7526 % under 0.94) under stack A, 0.936935 mmho (0.3261 %) under stack C and **0.939053 mmho (0.1008 %)** under every conservative assumption together, other terms fixed |
| LINE | p.4: 0.005 %/V maximum, 25 C, not switching; the regulation row itself is full range at VIN = 12 V (its temperature drift there is guaranteed); p.7 "Feedback Voltages" against temperature is **TYPICAL**. **The VIN dependence while switching and away from 25 C is not printed** | twice the printed maximum, either sign, at every temperature and while switching | Analog Devices: the line regulation while switching over -40 to 125 C junction, warranted | 3.6906 W under it alone; 61.6 times the printed maximum (stack A, cold), 47.1 with EA2 at 65 V/V |
| TCR | HoJLR2512 Ho-A0 p.2: +-50 ppm/K; p.4: tested +25 to +125 C only. **No guaranteed limit below +25 C** | +-100 ppm/K below +25 C (twice the printed value) | Milliohm: the TCR from -40 to +25 C, warranted. 7b.14 (R59 at -20 and +25 C) checks the design only | 3.5350 W under it alone; 882.027 ppm/K (stack A), 122.295 ppm/K (stack C) |
| HOLD | p.4: EA3 90 V/V and the FBIN bias 10 nA typical; FBIN regulation full range | EA3 at half with the drifts: the hold inside 16.420 to 18.813 V; the bias at ten times moves the lower corner by -9.2 mV | none for the bound; energy sensitivities on the page, 7b.12 reads the hold | does not move the bound |
| TJ | p.2: theta-JA 34 C/W (a package figure on the maker's board); p.3: the VIN quiescent maximum 4.2 mA, printed at 25 C, not switching, EXTVCC = 0; p.6 Notes 3 and 8; p.34 the CLKOUT method (+-10 C), shutdown at approximately 165 C | an INFERRED estimate, about 105.4 C (maximum gate charge at 10 V, highest oscillator frequency, the quiescent maximum extrapolated, EXTVCC at L4-E5's 30.15 V, board-dependent theta-JA, 62.1 C air); not a demonstrated upper bound | a design verification of board E's thermal path (7b.13 by p.34's method) | 19.6 K to 125 C |

The clarification requests are drafted for the owner to send; the session contacts no outside party:
`clarification/analog-devices-lt8705a.txt` (EA2's minimum gain and the VC dependence of the IMON_IN regulation point, the
line regulation while switching and over temperature, A7's transfer error over the design's common mode, differential,
temperature and switching) and `clarification/milliohm-hojlr2512.txt` (the HoJLR TCR from -40 to +25 C). Both ask for a
warranted limit and its conditions, and take lot characterization as supporting evidence only.

## The result: CONDITIONAL

**96.2474 W (cold end) and 96.2291 W (hot end), 96.2481 W with each resistor at its own worst end (the mixed envelope),
are calculated results, CONDITIONAL on EA2, A7, LINE, TCR and TJ.** Under each row's conservative assumption alone the cold
corner reads 97.1421 W (EA2), 96.3094 W (LINE) and 96.4650 W (TCR); A7 at its test-point limits is stack A itself, and TJ
moves no figure while the junction stays inside -40 to 125 C. All of them together with the resistors' soldering and life
drifts read **99.8992 W: margin 0.1008 W**, which A7 consumes at an effective gain 0.1008 % under its printed minimum. The
design floor stack C reads 99.6739 / 99.6549 W (cold / hot).

The assumptions of 96.25 W (stack A), in one list:

1. 8705af's full-range rows for the I grade (the IMON_IN regulation 1.187 / 1.229 V, A7's gm 0.94 / 1.06 mmho), with U5's
   junction inside -40 to 125 C (an INFERRED estimate of about 105.4 C, not a demonstrated bound).
2. A7's gm limits, printed at VCSPIN - VCSNIN = 50 mV and VCSPIN = 5.025 V, applied at the design's common mode 16.420 to
   25 V and up to 57.5 mV differential while switching (ASSUMPTION, condition A7).
3. The IMON_IN line regulation at its printed maximum (0.005 %/V, 25 C, not switching), applied while switching and at both
   ends (ASSUMPTION).
4. EA2's gain at its typical 130 V/V as its bound, with VC anywhere in its absolute maximum range (ASSUMPTION).
5. RSENSE1 15 mOhm +-1 % and +-50 ppm/K, the TCR printed for +25 to +125 C applied at -20 C (ASSUMPTION); its hot end 70.1 C
   by the derating line (INFERRED).
6. RIMON_IN 23.2k +-0.1 %, +-25 ppm/K (tested from -55 to +125 C); the resistors' drifts not stacked (they are in C and D).
7. Both resistors in the same inside air at each end (the paired ends' thermal coupling); the mixed envelope drops it.
8. The envelope: the input from the hold's lowest 16.420 V to REQ-016's 25 V, ambient -20 to +40 C (REQ-024), inside air at
   most 62.1 C.
9. Nothing in series with CSPIN or CSNIN (p.30): R59's pads are their Kelvin taps (a layout obligation).
10. Steady state; transients are 7b.9t's.
11. The setting realised as drafted (R59, R16 23.2k, C65).

## Why the corners bound the permitted range

- **The input voltage.** The power's slope in v is I_set [Vref (1 + ls lam (2v - 12)) + es dVC / G] / (Vref_typ gm r1 r2);
  its bracket is at least 1.173206 V (stack A) and 1.159412 V (stack C) at every vertex from 16.420 to 25 V, so the power
  rises with v and 25 V is the worst. No loaded voltage exceeds REQ-016's 25 V open circuit: the panel is PV_P's only source,
  and in discontinuous mode M4 is held off on reverse current (p.18). The dense 0.01 V check of every stack finds its worst
  at 25 V; the hold's lowest is the floor (65.4106 W under stack C with the drifts).
- **Every tolerance direction.** The power is monotonic in each term (up in Vref, in the line term above 12 V and in the EA2
  term; down in gm, RSENSE1 and RIMON_IN), so the 64 vertices an end hold the extremes. A resistor's low end 1 - a|T - 25| is
  least at the end of its temperature span farthest from 25 C.
- **Temperature and the thermal coupling.** The paired ends assume both resistors sit in the same inside air at each end:
  from -20 C (where self-heating only moves a part toward 25 C) to 62.1 C, RSENSE1 adding its own rise (70.1 C). Their worst
  distances from 25 C fall at different ends (RSENSE1 hot, RIMON_IN cold), so the mixed envelope lets each take its own:
  **96.248120559 W (A), 99.674651953 W (C), 99.899220557 W (every conservative assumption)**, against 96.247433497 /
  99.673940430 / 99.899220557 W paired. A dense air sweep from -20 to 62.1 C in 0.1 C steps, RSENSE1 with and without its
  rise, finds the paired values. The mixed envelope is the bound's figure. The LT8705A rows are full range, so U5's junction
  enters only as the condition. RSENSE1 would have to pass its 170 C rating (stack A) or reach 139.0 C (stack C) before the
  corner reaches 100 W, which covers a board hot spot beside L1 and the FETs.

## States outside the corners

| State | Treatment |
|---|---|
| Below -20 C ambient | Outside REQ-024's -20 to +40 C. Computed for information at -40 C: the candidate's open circuit reaches 25.23 V, outside REQ-016's window; the corner there with both resistors at -40 C reads 97.2744 W (stack A) |
| A source step (a panel plugged in live) | TRK_VIN's 224.8 uF charges through R59 at most at the panel's short circuit, 70.2 mJ at 25 V; start-up ramps VC by the soft start (p.15). Bench 7b.9t |
| An irradiance step, two scenarios of the candidate panel (100 W +6 %, -0.35 %/K, 1000 W/m2; INFERRED) | **110.2 W** with a cell warmed to 13.8 C by the NOCT model in -20 C air, and **122.7 W** with a cold-soaked -20 C cell. Either exceeds 100 W until the IMON_IN loop settles through CIMON_IN (tau 2.32 ms). Bench 7b.9t, both scenarios |
| The hold transition | VC passes between EA3 and EA2 (the diode-AND, p.14); each side's steady state is bounded. Bench 7b.9t |
| An unstable current loop | Would break the steady-state premise. Bench 7b.9t with p.33's load and line steps |

## The design option that removes an unknown (SESSION decision: not taken)

Of the stocked 15 mOhm 1 % 2512 parts read, only Vishay Dale's WSL2512R0150FEA (LCSC C844695; Document 30100, Revision
23-Nov-2023, p.2) states its TCR from -55 C: +-75 ppm/K (HoJLR, YAGEO PA V.10 p.9 and RALEC LR IE-SP-060 p.10 test only the
hot side). Its solder-heat and life limits each carry 0.5 mOhm (p.3): 3.83 % and 4.33 % of 15 mOhm. With it, stack A reads
96.4763 W, but the design floor reads 106.9760 W at 23.2k, and the same rule would move RIMON_IN to 24.9k (3.2343 A): 6.8 %
less input in every hour the limit binds. **Not taken:** the swap trades an unknown with a large margin (122.295 ppm/K under
stack C, 2.4 times the printed value) for a certain loss of setting. The recomputation of this round does not change it. No
part changes.

## Prototype measurements: downstream obligations, not blockers

No architecture decision depends on 7b.9 (the steady-state sweep), 7b.9t (transients, both panel scenarios, the loop),
7b.10 (EA2's gain), 7b.11 (the line row), 7b.12 (the hold), 7b.13 (U5's junction) or 7b.14 (R59 at -20 and +25 C). The
current-limit mechanism holds its bound under the conservative assumptions above; an adverse reading changes a value
(RIMON_IN, the compensation), not the mechanism or the architecture.

## The check, and what changed

| Item | Change |
|---|---|
| B1, A7's gm row is printed at 50 mV differential and CSPIN at 5.025 V; the design runs 16.4 to 25 V and about 57.5 mV | A7 is the fifth condition of the bound, with its break-evens (0.904726 / 0.936935 / 0.939053 mmho: stack A, stack C, every conservative assumption); the p.8 curve is cited as TYPICAL and against the differential only; the Analog Devices draft asks for A7's warranted transfer error over common mode, differential, temperature and switching; the result stays CONDITIONAL. Test `t_a7_is_a_condition_with_its_sensitivity` |
| B2, the cold TCR's "no effect" on protection and stability; the fault ratio; LINE's "no gain" | TCR now moves loop stability (-0.2255 %) and protection (+0.2260 % of the trip current; the comparator's threshold voltage unchanged) as small, nonzero effects; the ratio is 1.236365 with the line and EA2 allowances; LINE's stability is a small coupling of the source voltage into the setpoint. Test `t_tcr_and_line_carry_their_small_nonzero_effects` |
| M1, the paired temperature ends | The thermal coupling assumption is stated; the mixed envelope (96.248120559 / 99.674651953 W) and a dense air sweep are printed |
| M2, the hold floor's stack | Computed with matching stacks, the drifts included (65.4106 W C, 65.5580 W every conservative assumption) |
| M3, 105.4 C | Called an INFERRED estimate; the 4.2 mA maximum's conditions (25 C, not switching, EXTVCC = 0) stated |
| M4, 110.2 W | Labelled a scenario (a warmed 13.8 C cell); the cold-soaked 122.7 W case added; both in 7b.9t |
| M5, characterization as a guarantee | Both drafts and this page ask for a warranted limit and its conditions, lot characterization as supporting evidence only; Milliohm asked for -40 to +25 C |

Tests `t_thermal_coupling_hold_floor_junction_and_panel_scenarios` and the corrected predicates of
`t_a_row_that_moves_the_bound_has_an_assumption_a_qualification_and_a_margin` and
`t_clarification_texts_exist_and_contact_no_one` hold M1 to M5.
