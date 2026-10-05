### 15.9 The guard round: three approaches on printed figures, the selection and its correction scope (round 4; guard)

Every figure is printed by `l9stk_guard.py` into `l9stk_guard.out` ("guard N" is its section) from inputs pinned by sha256,
`l9stk_protection.out` among them. Three makers' sheets are held back by their terms and fetched by `fetch_held_back.py`:
TI's LM26LV (SNIS144G) and TPS709 (SBVS186H), and TDK's PTC sheet of August 2019. Labels: PRINTED (a maker's printed limit),
TYPICAL, ASSUMED, DERIVED, RECORD (another record's figure). Nothing was built, bought or measured.

**What a guard must hit on C-PROT rev 1 (guard 3).**
- **No trip:** 10 A held and 18 A for 60 s read as held. The hottest junction at the allowances reads 89.4 C and 118.0 C; it
  is taken for the guard's own temperature, the hot side.
- **Trip:** the breaker off before the hottest battery FET's junction passes 150 C at any current to 23.93 A held. On the
  worst split of three the junction leads its mounting base by 2.12 K; with two FETs carrying all (E-13's second specimen)
  by 4.24 K. The mounting base leads the guard's site by a gradient no record bounds (the check V2's minor m5).
- **So the window is 118.0 C to 147.88 C less the gradient, 29.87 K in all,** to be shared by the guard's own band, both
  margins and the gradient.

**The loop's levels as drawn (guard 2)**, with 1 % resistors (assumed) at their worse sign and board A's loads; they
reproduce record l8p's 12j:

| BRK_VIN | No trip while the element is under | Surely off from | A held DOCK_EN_OUT reads powered from |
|---|---|---|---|
| 7.6 V | 33.0 kOhm | 136.8 kOhm | 3.574 kOhm |
| 10.6 V | 58.4 kOhm | 203.4 kOhm | 2.327 kOhm |
| 16.8 V | 110.9 kOhm | 341.2 kOhm | 1.352 kOhm |

Board A reads the return held under 0.7755 V and the loop powered over 1.981 V, and a ramping closed loop is never read held
while the element is under 25.8 kOhm (L4-E11 20c at `6ca1646e`, a copy).

**The guard as drafted, on its printed points (guard 4).**

| Side | On the PRF15BB103's printed points | Verdict |
|---|---|---|
| the trip | over 4.7 MOhm from 133 C, against the 341.2 kOhm sure-off at 16.8 V; 14.88 K left for the gradient (12.76 K with two FETs) | PRINTED |
| no trip at 10 A | under 100 kOhm to 110 C, which the loop tolerates only from a pack of 15.51 V | NOT PRINTED under 15.51 V |
| no trip in the 18 A service | the service reads 118.0 C, over the 110 C bound; nothing is printed between 110 and 127 C | NOT PRINTED at any pack voltage |
| the window and the held reading | only the 25 C row (5 to 15 kOhm) is printed | NOT PRINTED away from 25 C |

**Three approaches (guard 5).**

| | G1: a PTC that prints both points, the two-wire loop rescaled, a series resistor for the held reading | G2: an active guard with a printed trip accuracy, on the loop's own supply | G3: no element in the trip path |
|---|---|---|---|
| Parts read | Murata PRF15BA102RB6RC (at most 10 kOhm to 120 C, at least 100 kOhm from 143 C); TDK B59721A0130A062 (at most 5.5 kOhm to 125 C, at least 40 kOhm from 145 C) | TI LM26LV, a factory-set temperature switch: trip point accuracy plus or minus 2.2 C from 0 to 150 C at a 5 V supply; hysteresis 4.5 to 5.5 C; 16 uA at most; specified to 150 C | a fixed resistor; E-1's bar read on every unit at commissioning |
| No-trip margin at 10 A, at 18 A | 30.6 K, 2.0 K (Murata); 35.6 K, 7.0 K (TDK) | 38.4 K, 9.8 K (the 130 C preset); 33.4 K, 4.8 K (125 C) | nothing can interrupt the service |
| Left for the gradient, worst split (two FETs) | 4.88 K (2.76 K) Murata; 2.88 K (0.76 K) TDK | 15.68 K (13.56 K) at 130 C; 20.68 K (18.56 K) at 125 C | no trip side at all |
| Does a loop exist on printed figures | **No.** Of every E24 triple from 1 kOhm to 1 MOhm, none keeps the four readings for either part: the window needs the cold resistance bounded, and the sheets print it only as "under the no-trip point". With the window read on the 25 C row (assumed): 1084 loops (Murata), 45 (TDK) | **Yes.** With a fixed 15 kOhm in RT1's place every reading holds at 7.6, 10.6, 16.8 and 29.2 V (below) | yes, trivially |
| Cost | board P's R106 and R107 change and every level of L4-E11 20c with them; 0.92 mA of static draw (Murata's least-draw loop) or 3.72 mA with 15.60 mW in the part against TDK's 6 mW note; the drafted loop draws 0.45 mA | about nine small parts on board A against one; two new part types; 0.387 mA closed, 0.702 mA tripped; board P unchanged; an open shunt, a dead switch or a dead regulator removes the guard unseen, as a shorted PTC would, so E-13b checks it in place | no part; the unit-by-unit protection is gone |
| Verdict | **NOT SELECTED**: no loop on printed figures, and the 20 to 23 K a PTC's printed transition spans leaves the gradient under 5 K | **SELECTED** | **NOT SELECTED**: it removes the protection 15.5 selected; an assigned test is not a protection |

G2's variant, the kit's NTC bridge and zero-drift comparator (C-1c's pattern), is NOT TAKEN: the NXRT15XH103 prints operation
to 125 C only and its B constants above 25/50 as reference values, so near 130 C neither side is printed.

**G2 in detail (guard 5).**
- **The switch.** LM26LV presets, each on its printed plus or minus 2.2 C:

  | Preset | No trip under | Surely tripped from | Resets between | TI's orderable table |
  |---|---|---|---|---|
  | 125 C | 122.8 C | 127.2 C | 117.3 and 122.7 C | LM26LVCISD-125/NOPB Active |
  | **130 C** | **127.8 C** | **132.2 C** | 122.3 and 127.7 C | LM26LVQISDX-130/NOPB Active (the -Q1 grade, large reel); the small reel Obsolete |
  | 135 C | 132.8 C | 137.2 C | 127.3 and 132.7 C | LM26LVCISD-135/NOPB Active |

  Its own heating is 0.008 K. Its thermal pad may float, so it sits on an island at the battery FETs' pour.
- **The supply.** A 5 V regulator fed from DOCK_EN_OUT, so the guard holds the breaker off while hot with the kit dark: the
  loop is powered whenever the pack is docked. TI TPS70950: input 2.7 to 30 V (absolute 32 V) against the loop's 29.2 V clamp;
  plus or minus 1 %; 2.25 uA at most; EN floats to enable. The switch and the regulator draw 18.25 uA at their printed
  maxima, against the 30 uA this round allows the guard.
- **The action.** The kit's AO3400A from DOCK_EN_RET to ground, its gate on OVERTEMP (active high, push-pull; at least 4.75 V
  of drive against the 4.5 V its 32 mOhm is printed at). L4-E11's Q44 already pulls the return for the input-return reset, and
  board P's detector pulls it too: **no new loop state.** Board A's DD-7 reads the guard's trip as it reads those pulls (the
  return held, the loop powered).
- **The loop with the fixed 15 kOhm plus or minus 1 %:**

  | BRK_VIN | First inverter's gate, closed | DOCK_EN_OUT, closed | Tripped: the return | Tripped: DOCK_EN_OUT (the supply's input) | Tripped: the shunt |
  |---|---|---|---|---|---|
  | 7.6 V | 2.82 to 3.60 V | 5.47 to 6.00 V | 0.010 mV | 4.32 V | 0.31 mA |
  | 10.6 V | 4.20 to 5.01 V | 7.81 to 8.37 V | 0.014 mV | 6.09 V | 0.43 mA |
  | 16.8 V | 7.05 to 7.95 V | 12.64 to 13.26 V | 0.022 mV | 9.76 V | 0.68 mA |
  | 29.2 V | 12.74 to 13.81 V | 22.30 to 23.05 V | 0.038 mV | 17.09 V | 1.18 mA |

  Against: the gate over 2.5 V to stay on and under 20 V; the return under 0.7755 V (board A's held reading) and 1 V (the
  first inverter); DOCK_EN_OUT over 1.981 V read powered; RET/OUT closed 0.590 against 0.4603. The regulator is in
  regulation from BRK_VIN 9.68 V with the return at ground (taking its 500 mV dropout printed at 50 mA as a bound). Under
  that the switch runs on less than 5 V, where its trip accuracy is not printed; the pack's service starts at 10.6 V.

**SELECTED (SESSION): G2 with the 130 C preset; the 125 C preset is the reversal.**
- **Why.** It is the one approach whose two sides are both printed. It restores the margins 15.5 believed it had: 9.8 K over
  the 18 A service (15.5 read 9.0 to 15.0 K on the misread column) and 15.68 K for the gradient on the worst split (the
  drafted PTC's printed trip left 14.88 K).
- **Why 130 C and not 125 C.** At the gauge's uncalibrated true current (an indicated 18 A may be a true 18.80 A, condition
  C4) the junction reads 121.8 C held: the 130 C preset is left 6.0 K, the 125 C preset 1.0 K. Both leave the gradient more
  than the drafted PTC did. Under 0 C the trip accuracy is not printed; the trip is 130 K above.
- **Authority.** SESSION: an engineering choice inside the task. No requirement, limit or service is lowered. Its parts are
  small catalogue parts whose order codes are Layer 6's.
- **Reversed by** E-13 reading a gradient over 15.68 K (then the 125 C preset: 4.8 K and 20.68 K), or by a check of the
  drafts that refuses the loop's levels.

**The acceptance on C-PROT rev 1, for the drafts and their check (guard 6).**
- **(a) Composition.** The board A draft replaces record l8p's RT1 and composes with L4-E11's DD-7 draft in L4-E9's order;
  board P's and board E's drafts compose unchanged; the generators run to their end.
- **(b) Netlist, with mutations that fail.** The fixed resistor between DOCK_EN_OUT and DOCK_EN_RET; the regulator's input on
  DOCK_EN_OUT and its output on the switch's supply only; OVERTEMP to the shunt's gate; the shunt's drain on DOCK_EN_RET and
  its source on ground. Mutations: the shunt on DOCK_EN_OUT, the open-drain output used, the regulator fed from VBAT, the
  resistor outside 3.574 to 25.8 kOhm.
- **(c) Electrical.** No trip under 127.8 C and tripped from 132.2 C at the switch; the gate at least 2.82 V closed and the
  return under 1 V tripped at every voltage above; the supply in regulation from 9.68 V; the guard's draw at most 30 uA; the
  shunt's gate filtered over the switch's 2.3 ms and the regulator's 1.5 ms start, so a ramping loop (a docking, the gauge's
  wake, a back-fed precharge) is never read held.
- **Physical, apart.** E-13 on the coupon; E-13b in place (TRIP_TEST pulled high opens the breaker; released, it restarts).

**The correction scope (drafted by their owners; nothing of theirs is edited here).**

| Owner | What changes |
|---|---|
| Board A: L4-E11 with board A's generator (record l8p's `apply_gen_sch_a_ptc.py` draws RT1 today) | RT1 becomes the fixed 15 kOhm; the switch on an island at the battery FETs' pour's centroid; the regulator, its two capacitors, the shunt, its gate filter and pull-down; test points on TRIP_TEST and VTEMP; L4-E11 20c's rows restated for the fixed resistor and 20f's docking row for the guard's start |
| Board P: record l8p | no part changes (R106 10 kOhm, R107 22 kOhm, the inverters and the detector stay); its 12j finding is answered by this selection once drafted and checked; its Murata question (unsent) is no longer needed for the guard |
| Layer 5 | DOCK_EN_OUT's load on board A gains 30 uA; DOCK_EN_RET may be held at ground by board A's guard as by board P's detector |
| Layer 6; Layer 9 layout | the order codes and filed sheets of the switch and the regulator; the switch's island and its distance to each FET's tab |
| This record | E-13 restated and E-13b added (15.7) |

**L8P-F07 STAYS OPEN** until those drafts compose, read DRAWN with mutations failing and pass an independent check on this
acceptance. The Murata question drafted in record l8p stays unsent; with this selection the guard no longer rests on it.
