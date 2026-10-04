# L9-POWER-BUDGET: Layer 9 item 9.1, the power budget on the current design (MESHSAT-1357, 3 October 2026; round 2, 4 October 2026)

**Status: PROVISIONAL desk calculation, not reviewed.** Prototype design: nothing in this kit has been built, powered or
measured, and no figure on this page is a measurement. Every figure is printed by `l9pwr_budget.py` into `l9pwr_budget.out`
("out N" is its section) from files pinned by sha256 in out 0; the page restates them and the test
`v2/ecad/tools/tests/test_l9pwr.py` holds the page to the output. The drafts of Layers 4, 8 and 9 are modelled as drafts: they
are printed DRAFTED, none is applied to a generator, and their release guards stand.

## Round 2 in short (4 October 2026)

- **What moved.** Set 28 was promoted to main (`d834e6a7`, record `64cd25ee`); this round runs on main. Record l8r2's rounds 4 to
  6 (`fnd/l8r3` at `89924e40`) put slots 1 and 3 on board A's LM5176 stage, keep the coolers at full speed with no Fan_PWM maximum
  and declare their slot row at the envelope (0.69 A), set board B's six slot bucks to RT 200 k and every LM5176 5.1 V divider to
  0.1 %. Record l9stk's section 15 (`fnd/l9stk` at `2c8b29fb`) drafts board P's breaker C-1 (LM5069-2, two CSD18510Q5B, a
  2.6087 mOhm sense) and a third battery FET on board A. Each source is read from a copy in `inputs/` that `git show` made at that
  commit, pinned by sha256 and listed in `inputs/SOURCES.txt`; the test compares every copy with its source.
- **The DRAFTED tree now carries ten drafts (D1 to D10, out 1 and out 4);** round 1's DRAFTED tree is rebuilt beside it as
  DRAFTED-R1, so every figure another record took from round 1 is reproduced on the same evaluator (out 8: L4-E9 round 7's R1c and
  R11, record l8r2's R9, all EQUAL). Two parser lines of round 1 are set aside because their figure was removed or superseded:
  l8r2's `eta_slot` and its round 3 "choice (a)" line (out 1).
- **The profile at the pack, PLAN: 44.20 W (round 1) to 44.58 W; HIGH moves by 1.2 to 4.5 W per state** (out 3b). At PLAN the move
  is D6, the LM5176 stages' declared 0.90 against the AP64500's curve point (+0.37 W in the profile, +0.88 W in PS-ALLTX); at HIGH
  it is mostly D4, the coolers at l8r2's envelope (2.75 W at the step-up's 12.43 V top over its 0.80, against the maker's 2.0 W
  over 0.85).
- **L9P-F01 (D-11's all-transmit floor) is OPEN again.** L4-E9 round 7 re-derived the floor at 16.1 V rest on round 1's drafts
  (15.986 V needed, reproduced here exactly, R11). On this round's drafts the basis needs **16.214 V**, 0.114 V over 16.1 V; by round
  7's own rule the floor becomes **16.4 V** (4.100 V a cell), and the all-transmit window to ChargeVoltage's 16.884 V shrinks from
  0.784 V to 0.484 V. The coolers' envelope alone takes round 1's basis to 16.188 V. With the coolers at the maker's 2.0 W instead
  (should l8r2's C4-3 read them there) the need is 16.014 V and the rule gives 16.2 V (out 7).
- **L9P-F02 is resolved in the drafts, CONDITIONAL on l8r2's C4-1 to C4-6:** slots 1 and 3 sit within their LM5176 loop (7.0957 A)
  in every state, least +1.8732 A at HIGH at 5.1 V, +1.6621 A at the least load voltage 4.9019 V, +0.5634 A in the cooler's
  bounded start and +0.9432 A with a degraded cooler (PS-ALLTX, out 5b).
- **L9P-F03 (the device rail) stands, and is wider at the least load voltage:** 7.181 A against 7.0957 A in PS-ALLTX at HIGH at
  5.1 V; at fb01's least load voltage 4.9019 V, if every load draws constant power, 7.472 A, and PS-TYP and PS-BUSY at HIGH reach
  7.316 A (-0.2204 A). The three slot stages beside it keep 1.87 to 2.63 A in hand in PS-ALLTX (out 5b).
- **Board P's breaker and the third FET nearly cancel** in the pack path: +3.5186 mOhm and -3.5227 mOhm, net -0.0041 mOhm
  (0.038068 to 0.038064 Ohm); the third FET is in parallel, so it lowers the battery FETs' share (out 6b, R12).

## 1. The pack-side totals per state (out 3, out 3b)

LOW / PLAN / HIGH in W at the pack terminals (rv-pwr's battery W: VBAT plus the pack path's I2R at 14.4 V). HIGH puts every
load at its maximum at once: an upper bound, not a scenario. DRAFTED-R1 is round 1's DRAFTED, the "before" of this round.

| State | RV | DRAWN | DRAFTED-R1 (round 1) | DRAFTED (round 2) | DRAFTED at VBAT (PLAN) |
|---|---|---|---|---|---|
| PS-IDLE | 30.94 / 39.73 / 81.67 | 31.21 / 40.21 / 81.91 | 31.81 / 41.09 / 90.75 | 32.24 / 41.47 / 95.26 | 41.15 |
| PS-IDLE-SPEC (the profile) | 33.07 / 42.82 / 82.77 | 33.34 / 43.30 / 83.01 | 33.96 / 44.20 / 91.87 | 34.38 / 44.58 / 96.37 | 44.21 |
| PS-TYP | 46.94 / 62.96 / 120.58 | 47.74 / 63.84 / 121.37 | 48.46 / 64.91 / 130.91 | 49.21 / 65.65 / 135.14 | 64.86 |
| PS-BUSY | 54.64 / 92.01 / 134.40 | 55.72 / 93.09 / 135.18 | 56.49 / 94.42 / 145.00 | 57.43 / 95.31 / 148.88 | 93.65 |
| PS-RED (slot 3 alone) | 12.66 / 22.21 / 45.86 | 12.82 / 22.61 / 45.94 | 13.24 / 23.24 / 50.26 | 13.30 / 23.40 / 51.71 | 23.30 |
| PS-RED-b | 26.91 / 35.70 / 71.50 | 27.18 / 36.16 / 71.70 | 27.77 / 37.04 / 80.43 | 28.20 / 37.41 / 84.91 | 37.15 |
| PS-EMCON | 37.33 / 53.06 / 103.27 | 37.85 / 47.78 / 81.04 | 38.52 / 48.75 / 89.79 | 38.98 / 49.11 / 94.18 | 48.67 |
| PS-ALLTX | 168.93 / 203.82 / 272.03 | 170.87 / 205.65 / 274.29 | 173.20 / 209.01 / 287.91 | 174.23 / 209.89 / 292.03 | 201.80 |
| PS-RED2 (the reduced mode) | 17.62 / 31.38 / 55.56 | 17.86 / 31.98 / 55.80 | 18.36 / 32.74 / 62.23 | 18.42 / 32.90 / 64.92 | 32.71 |
| PS-SURV (slot 2 alone) | 12.45 / 21.73 / 42.00 | 12.66 / 22.29 / 42.26 | 13.08 / 22.92 / 46.66 | 13.08 / 22.92 / 47.89 | 22.83 |
| PS-SURV-R (the heat stage) | 12.78 / 23.27 / 46.94 | 12.94 / 23.68 / 47.03 | 13.36 / 24.31 / 51.36 | 13.42 / 24.47 / 52.81 | 24.36 |

The change from round 1 at PLAN is +0.16 to +0.89 W in every state but PS-SURV (slot 2 alone, where slots 1 and 3 are off and
the pack path's net -0.0041 mOhm leaves it at -0.0000 W); at HIGH +1.23 W (PS-SURV) to +4.51 W (the profile). Out 3 also prints
the pack current at 14.4 V and DRAFTED's PLAN split by tier (S, R, D, T).

## 2. What differs from rv-pwr's model, and how the budget takes it (out 1, out 4)

Applied in this order; out 4 prints the pack side after each step for every state, at PLAN and at HIGH. The deltas at PLAN for
the profile (PS-IDLE-SPEC) and for PS-ALLTX:

| Step | Status | What | Profile | PS-ALLTX |
|---|---|---|---|---|
| M1 | ON MAIN (`458b2873`, F-PR-04) | slot 2 and the device rail on LM5176 stages; 5.1 V NOT PLOTTED, the generator's declared 0.90 | +0.432 W | +0.755 W |
| M2 | ON MAIN (O-17) | slot 2's card rail at 3.456 V | 0 | +0.008 W |
| M3 | ON MAIN (S-99) | board D on its own TPS62933 U41 from VBAT at the declared 0.90 | 0 | 0 |
| M4 | ON MAIN (`458b2873`) | EMCON with both link cards unpowered (record hc2) | 0 (PS-EMCON -5.979 W) | 0 |
| M5 | ON MAIN (`458b2873`, S-04, F-PR-06) | board A's 5 mOhm R17 in the pack path; the heater regulated to 12 V (cold overlay only) | +0.046 W | +1.067 W |
| D1 | DRAFTED (L4-E11 15c) | the battery FET pair Q39, Q40 at L4-E11's 150 C bound, 10.568 mOhm | +0.097 W | +2.333 W |
| D2 | DRAFTED (L4-E11 15a) | board E's auxiliary domain on VSYS_E behind U42 | +0.001 W | +0.001 W |
| D3 | DRAFTED (L4-E11 18a, D-18) | the mixers on U22's 12.0 V rail | +0.498 W | +0.530 W |
| D4 | DRAFTED (l8r2 item 1 to round 6, D-18) | the coolers on a per-slot TPS61089 step-up, full speed, no Fan_PWM maximum; HIGH the envelope (2.75 W over 0.80, the row 0.69 A), PLAN at 0.85 | +0.294 W (HIGH +9.978 W) | +0.326 W (HIGH +10.891 W) |
| D5 | DRAFTED (l8r2 item 3) | PANEL_5V behind U901, its RON | +0.014 W | +0.166 W |
| D6 | DRAFTED (l8r2 rounds 4 to 6) | slots 1 and 3 on the LM5176 stage (U501, U531, 6 mOhm ISNS), the declared 0.90; the AP64500s U4, U6 retired | +0.372 W | +0.884 W |
| D7 | DRAFTED (l8r2 round 5) | board B's six slot bucks at RT 200 k, 500 kHz: the frequency of the curves rv-pwr uses (68 k drawn sets 1471 kHz, where no curve is printed) | 0 | 0 |
| D8 | DRAFTED (l8r2 round 6) | the 5.1 V stages' dividers at 0.1 %: 5.0019 to 5.1744 V, the least at the loads 4.9019 V (drawn 1 %: 4.9267 to 5.2536 V, 4.8282 V) | 0 | 0 |
| D9 | DRAFTED (l9stk 15.4) | board P's breaker C-1 in the pack path: the sense at its window's highest 2.6546 mOhm and two CSD18510Q5B at 1.728 mOhm each (150 C) in parallel, 3.5186 mOhm | +0.034 W | +0.816 W |
| D10 | DRAFTED (l9stk 15.5) | a third BUK6Y10-30P beside Q39, Q40: three at 21.136 mOhm each, 7.0453 mOhm against the pair's 10.568 | -0.034 W | -0.817 W |

**Not modelled, each with its reason (out 1):** l8gnd's GND-002 and HOT-R1 hold, l8r2's VBUS20 cut-off and PH land, its board D
3.3 V eFuse, its pack return and energy chain texts, the slot leads' 6.6 A and VBAT's 2.60 A entries (declarations, printed
beside the stage currents in out 5b), the stages' CS shunts and the breaker's enable loop, RC hold and PTC guard (milliwatts, no
figure read), l9stk's copper decision and its fault items, the source and charge path records L4-E4 to L4-E8 and L4-E13, U17 on
R227, the INA226 shunts (bounded per state in out 5; slots 1 and 3 on 6 mOhm with D6), the charger's quiescent, board E's CELL_F
loads as drawn, and source-only operation.

**The pack and the states** are unchanged: 4S3P Samsung INR18650-35E as rv-pwr models it; rv-pwr's eight states and record hc2's
three; charging on shore is the B4 balance (section 4).

## 3. Converters against their limits (out 5, out 5b)

Every converter, in every state, at PLAN and HIGH against the maker's rated output, an LM5176 stage's average loop at its least
(VSNS 43 mV over its ISNS shunt at +1 %, 7.0957 A on 6 mOhm), or a draft's limit, with the margin at HIGH (CMP-001's acceptance:
the applied stress against the datasheet maximum for every part in a current path above 1 A). The tightest per state (DRAFTED,
margin at HIGH):

| State | Tightest | Next |
|---|---|---|
| PS-IDLE-SPEC | the monitor's eFuse U21, 1.032 A at the floor against 1.2 A nominal, +14.0 % | the supervisors' AP2112K, 0.460 A against 0.6 A, +23.3 % |
| PS-TYP, PS-BUSY | the device rail's LM5176, 7.032 A against 7.0957 A, +0.9 % (at 4.9019 V: 7.316 A, -0.2204 A) | U21, +14.0 % |
| PS-ALLTX | the PA's LM5176, 8.188 A against 7.0957 A, **-15.4 %** (L9P-F04) | the device rail, 7.181 A, **-1.2 %** (L9P-F03) |
| PS-SURV-R | the supervisors' AP2112K, +23.3 % | the device rail, +23.9 % |

**The four LM5176 5.1 V stages side by side in PS-ALLTX at HIGH (out 5b, DRAFTED):**

| Stage | At 5.1 V | At the least load voltage 4.9019 V | Bounded start | Degraded cooler | Round 1 at 5.1 V |
|---|---|---|---|---|---|
| slot 1, U501 | 5.2225 A (+1.8732) | 5.4336 A (+1.6621) | 6.5323 A (+0.5634) | 6.1525 A (+0.9432) | 5.010 A on the AP64500's 5 A (-0.010) |
| slot 2, U5 | 4.4679 A (+2.6278) | 4.6485 A (+2.4473) | 5.7472 A (+1.3485) | 5.3674 A (+1.7283) | 4.255 A |
| slot 3, U531 | 5.2225 A (+1.8732) | 5.4336 A (+1.6621) | 6.5323 A (+0.5634) | 6.1525 A (+0.9432) | 5.010 A on 5 A (-0.010) |
| device rail, U7 | 7.1814 A (**-0.0857**) | 7.4717 A (**-0.3760**) | | | 7.181 A |

The start and the degraded cooler are l8r2's bounds (the cooler branch at 1.80 A as a 100 us average; its eFuse at its least
0.448 A at 12.43 V over 0.80), CONDITIONAL on l8r2's C4-3. The least load voltage takes every load as constant power.

## 4. The pack path's elements (out 6b, R12)

DRAFTED's pack path is rv-pwr's R_DIST 22.5 mOhm, board A's R17 5 mOhm, board P's breaker 3.5186 mOhm (D9) and the three
battery FETs 7.0453 mOhm (D10): 38.064 mOhm against round 1's 38.068. Per state at the pack current at 14.4 V (PLAN / HIGH):

| State | Pack current (A) | Breaker (W) | Three battery FETs (W) | Round 1's pair (W) |
|---|---|---|---|---|
| PS-IDLE-SPEC | 3.096 / 6.692 | 0.0337 / 0.1576 | 0.0675 / 0.3156 | 0.0996 / 0.4301 |
| PS-TYP | 4.559 / 9.385 | 0.0731 / 0.3099 | 0.1464 / 0.6205 | 0.2147 / 0.8734 |
| PS-BUSY | 6.619 / 10.339 | 0.1542 / 0.3761 | 0.3087 / 0.7531 | 0.4544 / 1.0715 |
| PS-ALLTX | 14.576 / 20.280 | 0.7475 / 1.4471 | 1.4968 / 2.8975 | 2.2263 / 4.2246 |
| PS-SURV-R | 1.700 / 3.667 | 0.0102 / 0.0473 | 0.0204 / 0.0948 | 0.0301 / 0.1344 |

l9stk's own figures at the breaker's largest limit 23.93 A are reproduced from its inputs (R12): the sense 2.6087 mOhm (4 and 7.5
mOhm in parallel), a breaker FET 1.728 mOhm and 0.247 W, a battery FET 1.345 W with three, the sense 0.97 and 0.52 W.

## 5. The reconciliation with Layer 4 and the other records (out 8)

| Line | Their figure | Reproduced from their inputs | DRAWN | DRAFTED (round 2) | The difference |
|---|---|---|---|---|---|
| R1 L4-E9 1d's modes | 42.8, 203.8, 272.0, 162.3 W | equal | 43.301, 205.652, 274.291, 163.465 | 44.576, 209.89, 292.027, 166.149 | the steps of section 2 |
| R1c L4-E9 round 7's restated modes | 44.205, 209.007, 287.912, 165.76 W | equal, on DRAFTED-R1 | | 44.576, 209.89, 292.027, 166.149 | D4's envelope at HIGH and D6 to D10 |
| R2 B4, the charging heat | 50.043663 W (52.133663 with the ballasts) | equal, and L4-E12's 3.17382 and 3.44629 W | 50.5563 W (52.6463) | 51.9264 W (54.0164) | dP of the profile over 0.931 |
| R3 B7, battery-only to C1 | 43.413 W, 2.06349 h, 54.467 C unshed at 2.52 h | equal (the unrounded 43.41314 W gives 2.06348 h) | 2.03164 h | 1.95127 h, 55.898 C at 2.52 h | the energy-only run on L4-E10's 107.9 Wh becomes 2.421 h, a consequence for item 9.2 and L4-E12 |
| R4 L4-E11 18b, VSYS_E | 1.3208 A at the floor, 0.9942 A at the plan's duty, 89.8 % of U42 | equal | | 0.2139 A (PLAN), 0.4323 A (HIGH), 0.7402 A at 9.688 V | unchanged by this round |
| R5 L4-E11 15c, the battery FETs | 2.972 A, 0.0934 W; 4.375 A, 0.2023 W | equal | | three FETs: 3.0956 A, 0.0675 W; 4.5591 A, 0.1464 W (round 1's pair 0.0996 and 0.2147 W) | D10 lowers each FET's share |
| R6 L4-E12 8c, the fans' share | 3.128 W of the profile, 2.000 W of the heat stage | equal | 3.134, 2.001 | 3.961, 2.607 | the step-ups', U22's and the slot stages' losses |
| R7 L4-E12, the heat stage | 23.272 W | equal | 23.681 | 24.475 | the steps of section 2 |
| R8 Layer 7, fans and converters at full speed | 11.85 W against 2.970 W | equal | | 11.8588 W at the maker's 2.0 W; 15.1125 W at the coolers' envelope | the envelope is l8r2's bound at 12.43 V over 0.80 |
| R9 l8r2 round 6 (2c.5) | the slot's other loads 23.197 W; the window 5.0019 to 5.1744 V, least 4.9019 V; the loop 7.09571 A; slot 2's start 5.7473 A; +0.4957 A at 6.6 A; 17 rows; the energy line | equal, re-run on round 1's rails as printed (l8r2 parsed them at 3 places) | | unrounded within 0.0001 A of its rows; D6's cost +0.3656 W in the profile (l8r2: +0.373) | the rounding of round 1's printed rails |
| R10 rv-pwr's D-11 on main (R17) | 240.83 W, 13.87 V, 15.31 V, +0.19 V | equal | 15.34 V, +0.16 V | 16.21 V, **-0.71 V** | L9P-F01 |
| R11 L4-E9 round 7's D-17 | 15.986 V needed on round 1's drafts, the floor 16.1 V (+0.114 V), R_cell 0.0647 Ohm; the heater row 16.449 V; the PA row 12.227 V | equal, on DRAFTED-R1 at its printed watts | | **16.214 V**, -0.114 V against 16.1 V, the rule gives 16.4 V; heater 16.677 V; PA 12.268 V | L9P-F01 |
| R12 l9stk 15.4 and 15.5 | 2.6087 mOhm, 1.728 mOhm and 0.247 W, 1.345 W, 0.97 and 0.52 W | equal | | +3.5186 and -3.5227 mOhm in the pack path | the third FET is in parallel |

The lines that moved in round 2: R1, R1b, R2, R3, R5, R6, R7, R8 and R10 (their DRAFTED figures), R9 (replaced: round 1's line
reproduced l8r2's round 2 choice (a) on its flat `eta_slot`, which l8r2 removed), and the new R1c, R11 and R12. R4 did not move.

## 6. Sensitivities (out 9)

Each state's headline is the pack side at PLAN at 14.4 V (DRAFTED). Each load is moved alone over its LOW to HIGH, each
assumption over its stated range, the others at PLAN. The five that move it most (swing in W):

| State | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| PS-IDLE-SPEC | WiFi card 2 (standby, T) +11.30 | the supervisors +6.35 | WiFi card 1 +4.91 | panel board C +4.10 | Xenarc (T) +4.07 |
| PS-TYP | WiFi card 2 (T) +11.39 | 5G RM520N-GL +6.69 | the supervisors +6.40 | WiFi card 1 +4.94 | Xenarc (T) +4.10 |
| PS-BUSY | WiFi card 2 (T) +11.52 | the supervisors +6.47 | WiFi card 1 +6.40 | 5G +5.07 | Xenarc (T) +4.15 |
| PS-EMCON | the supervisors +6.36 | Xenarc (T) +4.08 | the two mixers +3.98 | NVMe slot 1 +3.30 | NVMe slot 2 +3.30 |
| PS-ALLTX | VHF PA 75 to 113 W +42.20 | WiFi card 2 (T) +12.05 | the supervisors +6.77 | the pack voltage 12.0 to 16.8 V -5.40 | QMX HF +5.21 |
| PS-SURV-R | the supervisors +6.30 | panel board C +4.07 | the two mixers +3.94 | LoRa +3.57 | the hubs' 1.1 V +3.27 |

The assumptions in every state: the LM5176 5.1 V stages' unplotted efficiency (now four stages: slots 1 to 3 and the device
rail; the AP64500 curve at their point to the declared 0.90) 0.54 to 1.78 W; the pack voltage up to 1.08 W (5.40 W in PS-ALLTX);
U22's efficiency 0.15 to 0.16 W; the cooler step-ups' (0.85 to 0.80 at PLAN) 0.04 to 0.14 W; the pack path's resistance (F2 at 1.0
to 2.5 mOhm, the three FETs at 25 C to their 150 C bound, the breaker's sense over its window and its FETs at 25 C to 150 C) 0.01 to
0.98 W.

## 7. Margin findings (out 10)

The rules: CMP-001's acceptance; the pack's declared continuous 10 A and peak 18 A (`pcb_pack_protection.yaml`); D-11's floors,
set from the gauge's 20 A trip with 10 percent margin and the cells' 60 C window (`pcb_requirements.yaml`); L4-E9 round 7's rule
for the re-derived floor. Classes per the owner's instruction of 2 October 2026; the class, the status and the owner are this
record's reading (SESSION).

| Id | Class | Status | Finding | Owner |
|---|---|---|---|---|
| L9P-F01 | DEMONSTRATED ANALYSIS DEFECT | **OPEN** (carried, moved) | D-11's all-transmit basis needs **16.214 V** rest at the worst cell resistance on this round's drafts, 0.114 V over L4-E9 round 7's 16.1 V (round 1's drafts: 15.986 V). From round 1: the coolers' envelope at HIGH +0.2019 V, slots 1 and 3 on the LM5176 +0.0264 V, the breaker +0.0633 V, the third FET -0.0634 V. By round 7's rule the floor becomes **16.4 V** (4.100 V a cell), the window to 16.884 V 0.484 V; at 16.1 V the basis is covered to R_cell 0.0552 Ohm, under rv-pwr's HIGH 0.06. With the coolers at the maker's 2.0 W: 16.014 V, the rule gives 16.2 V. A Fan_PWM cap during a key-down is not available (l8r2 round 4: the fan runs full whenever its PWM lead is not driven) | L4-E9 (D-17, R-28, LH-12: FW-A05's floor), with l8r2 (C4-3, the envelope) and Layer 5 (FW-A05's text) |
| L9P-F02 | ASSUMPTION TO BOUND | **RESOLVED IN THE DRAFTS**, CONDITIONAL on l8r2's C4-1 to C4-6 | round 1: the AP64500 at 5.010 A against 5 A (PS-BUSY, PS-ALLTX). Now slots 1 and 3 on the LM5176, least margins over every state +1.8732 A (5.1 V), +1.6621 A (4.9019 V), +0.5634 A (bounded start), +0.9432 A (degraded cooler) | l8r2 (C4-1 to C4-6), with board A's and board B's generator owners |
| L9P-F03 | ASSUMPTION TO BOUND | OPEN (carried, I-03) | the device rail's LM5176 at 7.181 A DRAFTED, 7.154 A DRAWN, against 7.0957 A in PS-ALLTX at HIGH; at fb01's least load voltage 4.9019 V with every load at constant power 7.472 A (-0.376 A), and PS-TYP and PS-BUSY at HIGH 7.316 A (-0.220 A); the slot stages beside it +1.87 to +2.63 A | board A's generator owner under I-03, with the TEST-PLAN power rows |
| L9P-F04 | PHYSICAL QUESTION | OPEN (carried, F-PR-01) | the PA rail at the PA's 113 W bound, 8.188 A against 7.0957 A. Specimen: one RA30H1317M1 at 13.8 V with the design's VGG into 50 Ohm at 144 to 146 MHz; measure the drain current at 30 W out; accept at most 7.10 A; on failure the rail limits and the PA gives less than 30 W (no damage) | the TEST-PLAN power rows, with board A's F-PR-01 and POWER-THERMAL 7.2 |
| L9P-F05 | ASSUMPTION TO BOUND | OPEN (carried, moved) | sustained states over 10 A at HIGH at the gauge's 10.0 V: PS-TYP 13.92 A (round 1 13.47), PS-BUSY 15.38 A (14.97), PS-TYP with the heater 14.85 A (14.40); PS-BUSY's PLAN margin at 10.0 V 0.28 A (round 1 0.37). Bounded by rv-pwr 9.3's current trigger of the module shedding, whose setting is re-read on these figures | L4-E9 (C02, C06), POWER-THERMAL 9.3 |
| L9P-F06 | ASSUMPTION TO BOUND | OPEN (carried, moved) | the outlets over PS-TYP and PS-BUSY at PLAN at 10.0 V: PoE 10.60 A, USB-C 11.86 A, both 15.98 A, PS-BUSY with both 19.30 A (round 1: 10.52, 11.78, 15.90, 19.20). Bounded by rv-pwr 9.3's outlet budget | L4-E9 (C03, C04, the tablet budget) |

Within their rules: every other converter in every state; U42, U22, the coolers' eFuses and U901; slots 1 and 3 on the LM5176;
D-11's PA-alone floor on every tree (DRAFTED 12.268 V against 12.4 V, +0.132 V). The heater rows stay over the floor on every
tree, which is why rv-pwr 7.2's rule holds the heater off during any key-down; they are not a finding.

## 8. What other records' authors own (reported here, nothing of theirs edited)

1. **L4-E9 (D-17, R-28, LH-12, C05, FW-A05):** L9P-F01. Round 7's 16.1 V rest floor does not hold on this round's drafts: the
   basis needs 16.214 V and round 7's own rule gives 16.4 V (4.100 V a cell), with the all-transmit window 0.484 V. The figure
   falls to 16.014 V (rule: 16.2 V) if l8r2's C4-3 reads the coolers at the maker's 2.0 W. The modes it restated (R1c: 44.205,
   209.007 / 287.912, 165.76 W) become 44.576, 209.890 / 292.027, 166.149 W. L9P-F05 and F06 move as printed; the shedding
   trigger and the outlet budget are re-read on them.
2. **Layer 5 (FW-A05's text, HW-FW-CONTRACT):** the all-transmit floor text L4-E9 drafted for 16.1 V follows L4-E9's new figure;
   the Fan_PWM maximum is not a remedy (l8r2 round 4 withdrew it), so no fan-duty clause enters FW-A05 for the floor.
3. **L4-E12 (12b, 12c, 8c, the heat):** B4's heat becomes 51.926 W (54.016 W with the ballasts), B7's C1 comes at 1.951 h on the
   review's constant conductance (55.898 C unshed at 2.52 h), the fans' share 3.961 W and the heat stage 24.475 W on the drafted
   design (R2, R3, R6, R7). Two heat sources are new to it: the slot stages' declared 0.90 (D6, +0.37 W in the profile, +0.74 to
   +0.89 W in PS-TYP to PS-ALLTX, all inside the case) and board P's breaker (0.034 W in the profile, 0.75 W in PS-ALLTX at PLAN,
   1.45 W at HIGH), while the third battery FET removes about as much from the pair (out 6b). At HIGH the coolers' envelope adds
   9.98 W at the pack in the profile over the drawn representative fan (D4), 3.80 W of it over round 1's maker figure (1.17 to
   4.04 W by state, out 3b).
4. **l8r2:** nothing owed to this record; its round 6 figures reproduce here (R9). Its own parser of this record's output reads
   round 1's format from its `inputs/` copy; a re-copy of this round's output would meet a changed R9 line and L9P-F02's status.
5. **L4-E11:** the battery FETs at three (D10) lower their loss to 0.0675 W in the profile (R5); its Ciss question (C3, Q-TI-17,
   E11-37) is l9stk's and L4-E11's, unchanged here.
6. **Item 9.2 (energy):** the profile at the pack moves to 44.58 W (DRAFTED); the energy-only run on L4-E10's 107.9 Wh at 20 C
   becomes 2.421 h. `energy_budget.py` and L4-E9's endurance still rest on 42.8 W.

## 9. Decisions taken (SESSION, under the owner's standing rule of 26 September 2026)

- **The coolers' HIGH is l8r2's envelope** (2.75 W at the step-up's 12.43 V top over its 0.80, the slot row 0.69 A the draft
  declares), replacing round 1's maker figure (2.0 W at 12 V over 0.85). Why: the maker prints only 12 V and free air, the
  step-up's output reaches 12.43 V, and the draft sizes its rows and leads on this bound; HIGH is every load at its maximum. The
  step-up's efficiency is therefore taken per scenario: 0.85 at LOW and PLAN (the draft's declared figure), 0.80 at HIGH. Reverse
  when C4-3 measures the branch's steady input; the maker's figure is printed as the other end (out 7, DRAFTED-MK).
- **LOW and PLAN of every fan keep rv-pwr's duty figures** (round 1's decision, unchanged): the duty the controls set (R-150) is
  unset and no Fan_PWM maximum exists any more.
- **The breaker's sense at its window's highest, its FETs and the battery FETs at their 150 C bounds**, the conservative side
  for every limit this budget judges, as rv-pwr takes F2 at its maximum; the 25 C ends are the sensitivity's low end.
- **Round 1's DRAFTED tree is rebuilt, not quoted,** so that what other records took from round 1 is reproduced on the same
  evaluator and every move this round makes is a printed step.
- **The margin rules** are unchanged: CMP-001's comparison against the maker's maximum (zero allowance), a programmed limit's
  least value standing for it, every margin printed.

## 10. Reproduce

`python3 v2/docs/records/l9pwr/l9pwr_budget.py` from the repository root (stdlib and pdftotext, about a second); the committed
output is regenerated only through `_bin/regen_out.py`, which runs it twice and refuses unless both runs are byte-identical and
every pin matches. Test: `env -C v2/ecad/tools/tests python3 run.py test_l9pwr test_public_hygiene`.
