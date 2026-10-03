# L9-POWER-BUDGET: Layer 9 item 9.1, the power budget on the current design (MESHSAT-1357, 3 October 2026)

**Status: PROVISIONAL desk calculation, not reviewed.** Prototype design: nothing in this kit has been built, powered or
measured, and no figure on this page is a measurement. Every figure is printed by `l9pwr_budget.py` into `l9pwr_budget.out`
("out N" is its section) from files pinned by sha256 in out 0; the page restates them and the test
`v2/ecad/tools/tests/test_l9pwr.py` holds the page to the output. The drafts of Layers 4 and 8 are modelled as drafts: they
are printed DRAFTED, none is applied to a generator, and their release guards stand.

## In short

- **Three trees, one evaluator.** RV is record rv-pwr's model as committed (the boards as generated at `1f614233`); DRAWN is the
  generators in this tree (main since `1f614233`: the LM5176 stages on slot 2 and the device rail, slot 2's 3.456 V card rail,
  board D's own buck U41, EMCON with the link cards unpowered, R17 in the pack path, the regulated heater); DRAFTED is DRAWN
  plus the five release-guarded drafts that move a power figure (L4-E11's battery FET pair and VSYS_E with the mixers on U22's
  12 V rail, l8r2's cooler step-ups and PANEL_5V eFuse, all with Layer 7's D-18 fan picks). The evaluator reproduces rv-pwr on
  rv-pwr's own tree within 1e-9 W and rv-pwr's committed headline table at 0.1 W (out 2).
- **The profile moves from 42.8 W to 43.3 W as drawn and 44.2 W as drafted** (PS-IDLE-SPEC at the pack side, PLAN). At PLAN
  the fans keep rv-pwr's duty figures, so the drafts add their converters' losses (U22 0.50 W, the step-ups 0.29 W, the pair
  0.10 W) and M1's unplotted LM5176 efficiency adds 0.43 W. At HIGH the drafts move every state by 4.3 to 13.6 W, mostly the
  picked fans at full speed (out 3, out 4).
- **Six margin findings** (out 10): one demonstrated analysis defect (L9P-F01, D-11's all-transmit floor does not cover its
  own basis on the drafted design), one physical question (L9P-F04, the PA's drain current at 13.8 V), four assumptions to
  bound (L9P-F02 new; L9P-F03, F05 and F06 carried). No converter is over its limit at PLAN in any state.
- **Every Layer 4 figure this budget overlaps is reproduced from its own inputs** (out 8): L4-E9's modes, the review's and
  L4-E12's B4 (50.043663 W) and B7 (2.06349 h), L4-E11's VSYS_E (1.3208 A) and pair loss, L4-E12's fans' share and heat
  stage, Layer 7's fan heat, l8r2's choice (a) and rv-pwr's D-11 margin on main. The current design's figure stands beside
  each, with the difference explained.

## 1. The pack-side totals per state (out 3)

LOW / PLAN / HIGH in W at the pack terminals (rv-pwr's battery W: VBAT plus the pack path's I2R at 14.4 V). HIGH puts every
load at its maximum at once: an upper bound, not a scenario.

| State | RV | DRAWN | DRAFTED | DRAFTED at VBAT (PLAN) |
|---|---|---|---|---|
| PS-IDLE | 30.94 / 39.73 / 81.67 | 31.21 / 40.21 / 81.91 | 31.81 / 41.09 / 90.75 | 40.78 |
| PS-IDLE-SPEC (the profile) | 33.07 / 42.82 / 82.77 | 33.34 / 43.30 / 83.01 | 33.96 / 44.20 / 91.87 | 43.85 |
| PS-TYP | 46.94 / 62.96 / 120.58 | 47.74 / 63.84 / 121.37 | 48.46 / 64.91 / 130.91 | 64.13 |
| PS-BUSY | 54.64 / 92.01 / 134.40 | 55.72 / 93.09 / 135.18 | 56.49 / 94.42 / 145.00 | 92.78 |
| PS-RED (slot 3 alone) | 12.66 / 22.21 / 45.86 | 12.82 / 22.61 / 45.94 | 13.24 / 23.24 / 50.26 | 23.14 |
| PS-RED-b | 26.91 / 35.70 / 71.50 | 27.18 / 36.16 / 71.70 | 27.77 / 37.04 / 80.43 | 36.78 |
| PS-EMCON | 37.33 / 53.06 / 103.27 | 37.85 / 47.78 / 81.04 | 38.52 / 48.75 / 89.79 | 48.31 |
| PS-ALLTX | 168.93 / 203.82 / 272.03 | 170.87 / 205.65 / 274.29 | 173.20 / 209.01 / 287.91 | 200.99 |
| PS-RED2 (the reduced mode) | 17.62 / 31.38 / 55.56 | 17.86 / 31.98 / 55.80 | 18.36 / 32.74 / 62.23 | 32.55 |
| PS-SURV (slot 2 alone) | 12.45 / 21.73 / 42.00 | 12.66 / 22.29 / 42.26 | 13.08 / 22.92 / 46.66 | 22.83 |
| PS-SURV-R (the heat stage) | 12.78 / 23.27 / 46.94 | 12.94 / 23.68 / 47.03 | 13.36 / 24.31 / 51.36 | 24.21 |

Out 3 also prints the pack current at 14.4 V and DRAFTED's PLAN split by tier (S, R, D, T) and the share on DRAFTED rows.
PS-EMCON falls on main because EMCON removes both WiFi link cards' supplies (M4), which rv-pwr still carried at 5.0 W.

## 2. What differs from rv-pwr's model, and how the budget takes it (out 1, out 4)

Applied in this order; out 4 prints the pack side after each step for every state, at PLAN and at HIGH. The deltas at PLAN for
the profile (PS-IDLE-SPEC) and for PS-ALLTX:

| Step | Status | What | Profile | PS-ALLTX |
|---|---|---|---|---|
| M1 | ON MAIN (`458b2873`, F-PR-04) | slot 2 and the device rail on LM5176 stages; 5.1 V NOT PLOTTED, so the generator's declared 0.90 replaces rv-pwr's AP64500 curve (rv-pwr's own rule for an unplotted point) | +0.432 W | +0.755 W |
| M2 | ON MAIN (O-17) | slot 2's card rail at 3.456 V | 0 | +0.008 W |
| M3 | ON MAIN (S-99) | board D on its own TPS62933 U41 from VBAT at the declared 0.90 | 0 | 0 |
| M4 | ON MAIN (`458b2873`) | EMCON with both link cards unpowered (record hc2) | 0 (PS-EMCON -5.979 W) | 0 |
| M5 | ON MAIN (`458b2873`, S-04, F-PR-06) | board A's 5 mOhm R17 in the pack path; the heater regulated to 12 V (cold overlay only) | +0.046 W | +1.067 W |
| D1 | DRAFTED (L4-E11 15c) | the battery FET pair Q39, Q40 at L4-E11's 150 C bound, 10.568 mOhm | +0.097 W | +2.333 W |
| D2 | DRAFTED (L4-E11 15a) | board E's auxiliary domain on VSYS_E behind U42 (0.1359 Ohm from L4-E11's drop) | +0.001 W | +0.001 W |
| D3 | DRAFTED (L4-E11 18a, D-18) | the mixers 9WL0612P4H001 on U22's 12.0 V rail, 0.85 and 16 mA quiescent | +0.498 W | +0.530 W |
| D4 | DRAFTED (l8r2 item 1, D-18) | the coolers 9WPA0412P6G001 on a per-slot TPS61089 step-up, 0.85 | +0.294 W | +0.326 W |
| D5 | DRAFTED (l8r2 item 3) | PANEL_5V behind U901, its RON | +0.014 W | +0.166 W |

**Not modelled, each with its reason (out 1):** l8gnd's GND-002 and HOT-R1 hold (no load), l8r2's VBUS20 cut-off and PH land,
board D's 3.3 V eFuse (under a milliwatt), the source and charge path records L4-E4 to L4-E8 and L4-E13 (no battery-side
load; L4-E8's ballasts enter B4), U17 on R227 (the PoE stage is off in every state), the INA226 shunts (bounded per state in
out 5), the charger's own quiescent (no figure read), board E's CELL_F loads ahead of R17 as drawn (under a milliwatt), and
source-only operation (L4-E11's section 3; the system-node demand per state is printed for it).

**The pack and the states.** The pack is unchanged: `pcb_pack_protection.yaml` declares 4S3P Samsung INR18650-35E and rv-pwr
already models it. The states are rv-pwr's eight and record hc2's three (the reduced mode PS-RED2, the heat stage PS-SURV as
board B is generated and PS-SURV-R after BANK-R1); charging on shore is the B4 balance (section 4).

## 3. Converters against their limits (out 5)

For every converter, in every state, out 5 prints the current at PLAN and at HIGH against the maker's rated output (AP64500
5 A, AP6320x 2 A, TPS62933 3 A, AP2112K 0.6 A, TLV755P 0.5 A, read from the pinned datasheets), an LM5176 stage's average
loop at its least (VSNS 43 mV over its ISNS shunt at +1 %), or a draft's limit (U42 1.4713 A at VBAT's 9.688 V floor, U22
about 1.2 A, the coolers' eFuse 0.448 A, U901 1.375 A), with the margin at HIGH. The rule is CMP-001's acceptance: the applied
stress against the datasheet maximum for every part in a current path above 1 A. The tightest per state (DRAFTED, margin at
HIGH):

| State | Tightest | Next |
|---|---|---|
| PS-IDLE-SPEC | the monitor's eFuse U21, 1.032 A at the floor against 1.2 A nominal, +14.0 % | the supervisors' AP2112K, 0.460 A against 0.6 A, +23.3 % |
| PS-TYP | the device rail's LM5176, 7.032 A against 7.096 A, +0.9 % | slot 3's AP64500, 4.324 A against 5 A, +13.5 % |
| PS-BUSY | slots 1 and 3's AP64500, 5.010 A against 5 A, **-0.2 %** (L9P-F02) | the device rail, +0.9 % |
| PS-ALLTX | the PA's LM5176, 8.188 A against 7.096 A, **-15.4 %** (L9P-F04) | the device rail, 7.181 A, **-1.2 %** (L9P-F03); slot 1, **-0.2 %** (L9P-F02) |
| PS-SURV-R | the supervisors' AP2112K, +23.3 % | the device rail, +23.9 % |

## 4. The reconciliation with Layer 4 (out 8)

| Line | Their figure | Reproduced from their inputs | DRAWN | DRAFTED | The difference |
|---|---|---|---|---|---|
| R1 L4-E9 1d's modes | 42.8, 203.8, 272.0, 162.3 W | equal | 43.301, 205.652, 274.291, 163.465 | 44.205, 209.007, 287.912, 165.760 | the steps of section 2 |
| R2 B4, the charging heat | 50.043663 W (52.133663 with the ballasts) | equal, and L4-E12's 3.17382 W source path and 3.44629 W charge path | 50.5563 W (52.6463) | 51.5273 W (53.6173) | dP of the profile over 0.931: dP itself plus the source path's 0.0741 W per watt; on shore the profile does not cross the pack path, so the pack-side figure is the conservative side by its I2R |
| R3 B7, battery-only to C1 | 43.413 W, 2.06349 h, 54.467 C unshed at 2.52 h | equal (the review's rounded heat; the unrounded 43.41314 W gives 2.06348 h, the rounding and nothing else) | 2.03164 h | 1.97401 h, 55.595 C at 2.52 h | the case heat follows the profile; the energy-only run on L4-E10's 107.9 Wh becomes 2.492 h (DRAWN) and 2.441 h (DRAFTED), a consequence for item 9.2 and L4-E12 |
| R4 L4-E11 18b, VSYS_E | 1.3208 A at the floor, 0.9942 A at the plan's duty, 89.8 % of U42 | equal | | 0.2139 A (PLAN, 14.4 V), 0.4323 A (HIGH, 16.8 V), 0.7402 A at 9.688 V with every load at HIGH | L4-E11's figure is a declaration with U12 at its declared 0.8 A; U12's input at the profile's board E loads is 0.0802 A |
| R5 L4-E11 15c, the pair | 2.972 A, 0.0934 W; 4.375 A, 0.2023 W | equal (L4-E11 divides the rounded 42.8 and 63.0 W by 14.4 V) | | 3.0698 A, 0.0996 W; 4.5074 A, 0.2147 W | this record solves the pack current with the whole pack path and the drafted profile |
| R6 L4-E12 8c, the fans' share | 3.128 W of the profile, 2.000 W of the heat stage | equal | 3.134, 2.001 | 3.932, 2.593 | the drafted step-ups' and U22's losses |
| R7 L4-E12, the heat stage | 23.272 W | equal | 23.681 | 24.315 | the steps of section 2 |
| R8 Layer 7, fans and converters at full speed | 11.85 W against 2.970 W | equal | | 11.8588 W | Layer 7 rounds each step-up's loss to 0.35 W (0.3529 W); U22's 16 mA quiescent (0.2304 W at 14.4 V) is in neither heat figure |
| R9 l8r2's choice (a) | 2.353 W a slot, 0.461 A, 7.84 W at VBAT | equal | | 7.5638 W | l8r2 takes the slot converters at a flat 0.90; this record uses the slot rails' own converters |
| R10 rv-pwr's D-11 on main (R17) | 240.83 W, 13.87 V, 15.31 V, +0.19 V | equal | 15.34 V, +0.16 V | 15.99 V, **-0.49 V** | L9P-F01 |

## 5. Sensitivities (out 9)

Each state's headline is the pack side at PLAN at 14.4 V (DRAFTED). Each load is moved alone over its LOW to HIGH, each
assumption over its stated range, the others at PLAN. The five that move it most (swing in W):

| State | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| PS-IDLE | WiFi card 2 (standby, T) +10.80 | the supervisors +6.34 | Xenarc (T) +6.10 | WiFi card 1 +4.72 | panel board C +4.09 |
| PS-IDLE-SPEC | WiFi card 2 (T) +10.81 | the supervisors +6.35 | WiFi card 1 +4.73 | panel board C +4.10 | Xenarc (T) +4.07 |
| PS-TYP | WiFi card 2 (T) +11.07 | 5G RM520N-GL +6.69 | the supervisors +6.40 | WiFi card 1 +4.85 | Xenarc (T) +4.10 |
| PS-BUSY | WiFi card 2 (T) +11.59 | WiFi card 1 +6.54 | the supervisors +6.47 | 5G +5.07 | Xenarc (T) +4.15 |
| PS-RED | the supervisors +6.30 | panel board C +4.07 | the two mixers (DRAFTED) +3.94 | LoRa +3.57 | the hubs' 1.1 V +3.27 |
| PS-RED-b | WiFi card 2 (T) +10.78 | the supervisors +6.33 | WiFi card 1 +4.72 | panel board C +4.09 | the two mixers +3.96 |
| PS-EMCON | the supervisors +6.36 | Xenarc (T) +4.08 | the two mixers +3.98 | NVMe slot 2 +3.30 | the hubs' 1.1 V +3.30 |
| PS-ALLTX | VHF PA 75 to 113 W +42.19 | WiFi card 2 (T) +12.22 | the supervisors +6.77 | QMX HF +5.20 | the pack voltage 12.0 to 16.8 V -4.64 |
| PS-RED2 | the supervisors +6.32 | panel board C +4.08 | the two mixers +3.95 | LoRa +3.58 | the hubs' 1.1 V +3.28 |
| PS-SURV | the supervisors +6.30 | panel board C +4.07 | the two mixers +3.94 | the hubs' 1.1 V +3.27 | CM5 slot 2 +2.80 |
| PS-SURV-R | the supervisors +6.30 | panel board C +4.07 | the two mixers +3.94 | LoRa +3.57 | the hubs' 1.1 V +3.27 |

The assumptions in every state (out 9's "every assumption" line): the LM5176 5.1 V stages' unplotted efficiency (the AP64500
curve at their point to the declared 0.90) moves the headline 0.38 to 0.89 W; the pack voltage 0.01 to 0.45 W (4.64 W in
PS-ALLTX, where the pack path's I2R dominates); U22's efficiency (0.93 read on TA04b to L4-E11's 0.85) 0.15 to 0.16 W; the cooler
step-ups' (0.85 to l8r2's 0.80) 0.04 to 0.14 W; the pack path's resistance (F2 at 1.0 to 2.5 mOhm, the pair at 25 C to its
150 C bound) 0.01 to 1.13 W. None of them reaches a state's top five but PS-ALLTX's. Out 9 also prints the headline at the
pack's 12.0, 13.2, 14.4, 15.6 and 16.8 V and every converter's efficiency over that range: the pack-fed AP64500 slot rails lose
1.4 to 2.0 points from 12.0 to 16.8 V at their PLAN current, and each declared efficiency's weight in W at the pack per point.

## 6. Margin findings (out 10)

The rules: CMP-001's acceptance (the applied stress against the datasheet maximum for every part in a current path above 1 A);
the pack's declared continuous 10 A and peak 18 A (`pcb_pack_protection.yaml`); D-11's floors, set from the gauge's 20 A trip
with 10 percent margin and the cells' 60 C window (`pcb_requirements.yaml`). Classes per the owner's instruction of 2 October
2026; the class and the owner are this record's reading (SESSION).

| Id | Class | New or carried | Finding | Owner |
|---|---|---|---|---|
| L9P-F01 | DEMONSTRATED ANALYSIS DEFECT | new | D-11's all-transmit basis needs a rest voltage of 15.99 V at the worst cell resistance on the drafted design, 0.49 V over the 15.5 V floor (DRAWN 15.34 V, 0.16 V under it). The drafted pair adds 0.190 V at 18 A and the picked fans and their converters at HIGH 0.458 V (8.25 W at VBAT). The floor covers a cell resistance of at most 0.0397 Ohm, under rv-pwr's PLAN 0.050. Correction: re-derive the floor on the drafts (at least 15.99 V, 3.997 V a cell, plus the stated margin), or cap the fans' duty during a key-down in FW-A05 and take the basis at that duty | L4-E9 (C05: K1 to K5, C4, FW-A05, the floors), with L4-E11 (the pair) and the fans' feeds (L4-E11 18a, l8r2 item 1); FW-A05's text is Layer 5's |
| L9P-F02 | ASSUMPTION TO BOUND | new | slots 1 and 3's AP64500 at 5.010 A against 5 A in PS-BUSY and PS-ALLTX at HIGH (PLAN at most 4.666 A; DRAWN 4.658 A); the step-up takes 0.461 A of the slot rail at full speed. HIGH stacks the CM5's declared 1.6 A (no maker maximum), the card's 9.1 W, the NVMe's maximum and the fan at full speed. Bound or design out: l8r2's alternative (b), one 12 V fan feed from board A, or the module's fan duty limited above a slot current, else a bench reading | l8r2 (item 1, choice (a) against (b)), with board A's generator owner (I-03) |
| L9P-F03 | ASSUMPTION TO BOUND | carried (I-03) | the device rail's LM5176 in PS-ALLTX at HIGH, 7.181 A DRAFTED and 7.154 A DRAWN against 7.0957 A; the loop limits, the rail droops | board A's generator owner under I-03, with the TEST-PLAN power rows |
| L9P-F04 | PHYSICAL QUESTION | carried (rv-pwr; F-PR-01) | the PA rail at the PA's 113 W bound, 8.188 A against 7.0957 A, which F-PR-01 set on purpose. Specimen: one RA30H1317M1 at 13.8 V with the design's VGG into 50 Ohm at 144 to 146 MHz; measure the drain current at 30 W out; accept at most 7.10 A; on failure the rail limits and the PA gives less than 30 W (no damage) | the TEST-PLAN power rows, with board A's F-PR-01 and POWER-THERMAL 7.2 |
| L9P-F05 | ASSUMPTION TO BOUND | carried (rv-pwr 7.1), moved | sustained states over 10 A at HIGH at the gauge's 10.0 V: PS-TYP 13.47 A (rv-pwr 12.24), PS-BUSY 14.97 A (13.66), PS-TYP with the heater 14.40 A (13.80); PS-BUSY's PLAN margin at 10.0 V falls from 0.70 to 0.37 A. Bounded by rv-pwr 9.3's current trigger of the module shedding, whose setting is re-read on these figures | L4-E9 (C02, C06), POWER-THERMAL 9.3 |
| L9P-F06 | ASSUMPTION TO BOUND | carried (rv-pwr 7.1), moved | the outlets over PS-TYP and PS-BUSY at PLAN at 10.0 V: PoE 10.52 A, USB-C 11.78 A, both 15.90 A, PS-BUSY with both 19.20 A (rv-pwr 10.17, 11.38, 15.30, 18.39). Bounded by rv-pwr 9.3's outlet budget (and the tablet's 18 W cap, a proposal) | L4-E9 (C03, C04, the tablet budget) |

Within their rules: every other converter in every state; U42, U22, the coolers' eFuses and U901; D-11's PA-alone floor on
every tree (DRAFTED 12.23 V against 12.4 V, +0.17 V, down from rv-pwr's +0.45 V). The heater rows are over the all-transmit
floor on every tree, which is why rv-pwr 7.2's rule holds the heater off during any key-down; they are not a finding.

## 7. What other records' authors own (reported here, nothing of theirs edited)

1. **L4-E9 (C05, FW-A05):** L9P-F01, the all-transmit floor on the drafted design; its 1d still quotes rv-pwr's 42.8 W profile
   and 203.8 / 272.0 W, which become 44.205 W and 209.007 / 287.912 W with the drafts (R1).
2. **L4-E12 (12b, 12c, 8c):** B4's heat becomes 51.527 W (53.617 W with the ballasts), B7's C1 comes at 1.974 h on the review's
   constant conductance, the fans' share 3.932 W and the heat stage 24.315 W on the drafted design (R2, R3, R6, R7); its lines
   rest on rv-pwr's profile, which its own pins keep.
3. **L4-E11 (18a):** U22's heat into the case (0.72 W) leaves out the 16 mA quiescent its own input current carries, 0.15 to
   0.28 W over VSYS_E's 9.5 to 17.4 V (R8); its declarations of 18b reproduce exactly (R4).
4. **l8r2 (item 1):** L9P-F02, choice (a) takes slots 1 and 3 to the AP64500's 5 A at HIGH; its 7.84 W at VBAT is 0.28 W over
   this record's 7.56 W because it takes the slot converters at a flat 0.90 (R9), the conservative side.
5. **Item 9.2 (energy):** the profile at the pack moves to 43.30 W (DRAWN) and 44.20 W (DRAFTED); the energy-only run on
   L4-E10's 107.9 Wh at 20 C becomes 2.49 h and 2.44 h. `energy_budget.py` and L4-E9's endurance still rest on 42.8 W.
6. **rv-pwr:** nothing; its committed outputs are history and stay as they are.

## 8. Decisions taken (SESSION, under the owner's standing rule of 26 September 2026)

- **The fans' three values.** HIGH is the picked fan's maker figure at full speed; LOW and PLAN keep rv-pwr's duty figures,
  because the duty the controls set (R-150) is unset and L4-E11 18b and Layer 7 carry the same PLAN. Why: PLAN at full speed
  would replace an unset duty by its maximum and hide the duty's effect in the headline instead of showing it as a
  sensitivity. Reverse once R-150 sets a duty or T-H1 logs the fans' drawn power.
- **The LM5176 5.1 V stages at the declared 0.90.** rv-pwr's own rule for a point its maker does not plot; the AP64500 curve
  rv-pwr used at `1f614233` is kept as the other end of the sensitivity. Reverse on a bench reading (FW-A15).
- **Three trees, not one.** The drafts are not the circuit; showing DRAWN beside DRAFTED keeps each draft's effect visible and
  lets a later application of a draft be checked against its line here.
- **The margin rules.** The requirements and the rules registry carry no percentage derating for converter current; CMP-001's
  comparison against the maker's maximum (zero allowance) is the rule, a programmed limit's least value stands for it, and
  every margin is printed so a planning allowance can be applied by a reader.

## 9. Reproduce

`python3 v2/docs/records/l9pwr/l9pwr_budget.py` from the repository root (stdlib and pdftotext, about a second); the committed
output is regenerated only through `_bin/regen_out.py`, which runs it twice and refuses unless both runs are byte-identical and
every pin matches. Test: `env -C v2/ecad/tools/tests python3 run.py test_l9pwr test_public_hygiene`.
