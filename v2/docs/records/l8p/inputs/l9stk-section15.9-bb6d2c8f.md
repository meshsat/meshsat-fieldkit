### 15.9 The guard round: three approaches on printed figures, the selection and its correction scope (round 4; guard; restated in round 5 after L8P-F08)

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
| Does a loop exist on printed figures | **No.** Of every E24 triple from 1 kOhm to 1 MOhm, none keeps the four readings for either part: the window needs the cold resistance bounded, and the sheets print it only as "under the no-trip point". With the window read on the 25 C row (assumed): 1084 loops (Murata), 45 (TDK) | **Yes.** With a fixed 15 kOhm in RT1's place the closed, held and tripped readings hold at 7.6, 10.6, 16.8 and 29.2 V (below); the window only with a low-leakage shunt (round 5, L8P-F08) | yes, trivially |
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
- **The action (round 4; WITHDRAWN in round 5 by L8P-F08).** The kit's AO3400A from DOCK_EN_RET to ground, its gate on
  OVERTEMP (active high, push-pull; at least 4.75 V of drive against the 4.5 V its 32 mOhm is printed at). L4-E11's Q44 already
  pulls the return for the input-return reset, and board P's detector pulls it too: **no new loop state.** Board A's DD-7 reads
  the guard's trip as it reads those pulls (the return held, the loop powered). Round 5 replaces the AO3400A by a 2N7002 (below).
- **The loop with the fixed 15 kOhm plus or minus 1 % (round 4's figures, the AO3400A's 43.6 uA counted on the return):**

  | BRK_VIN | First inverter's gate, closed | DOCK_EN_OUT, closed | Tripped: the return | Tripped: DOCK_EN_OUT (the supply's input) | Tripped: the shunt |
  |---|---|---|---|---|---|
  | 7.6 V | 2.82 to 3.60 V | 5.47 to 6.00 V | 0.010 mV | 4.32 V | 0.31 mA |
  | 10.6 V | 4.20 to 5.01 V | 7.81 to 8.37 V | 0.014 mV | 6.09 V | 0.43 mA |
  | 16.8 V | 7.05 to 7.95 V | 12.64 to 13.26 V | 0.022 mV | 9.76 V | 0.68 mA |
  | 29.2 V | 12.74 to 13.81 V | 22.30 to 23.05 V | 0.038 mV | 17.09 V | 1.18 mA |

  Against: the gate over 2.5 V to stay on and under 20 V; the return under 0.7755 V (board A's held reading) and 1 V (the
  first inverter); DOCK_EN_OUT over 1.981 V read powered. The regulator is in regulation from BRK_VIN 9.68 V with the return
  at ground (taking its 500 mV dropout printed at 50 mA as a bound). Under that the switch runs on less than 5 V, where its
  trip accuracy is not printed; the pack's service starts at 10.6 V. Round 4 also read the window here, as the closed loop's
  RET/OUT of 0.590 against 0.4603. That is a ratio at the pack's voltages, not a ramp's reading, and it is **WITHDRAWN**
  (L8P-F08, below).

**SELECTED (SESSION), round 4: G2 with the 130 C preset; the 125 C preset is the reversal.** The preset stands in round 5;
the shunt and the fixed resistor are re-selected below.
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

**Round 4's acceptance (c) on the window and its correction scope are WITHDRAWN; round 5 restates both below.**

**Round 5 (5 October 2026): the first negative check of the selection, L8P-F08, answered (guard 5b; guard 6 restated).**
Board P's author checked G2 on the makers' sheets before drafting it (record l8p round 7, `fnd/l8p2` at `bab66e6b`, its page
12k and `l8p_guard.out`, copied into `inputs/` with sha256). Every figure reproduced but one, finding **L8P-F08**. This is the
first negative check of G2 as selected; a second negative check of the same selection ends that loop (constitution section 5).
Case row C-PROT rev 1.

**L8P-F08 reproduced (guard 5b (1)).**
- **The window**, as L4-E11 20c defines it (copy at `08f7e38a`, the same bytes record l8p read at `4def5975`): a ramping closed
  loop is never read held, because "a trigger there stops a dead pack's precharge". Board A may read the loop powered from
  DOCK_EN_OUT 1.825 V and reads the return closed only over 0.84 V. So the window holds only if the return stays over 0.84 V
  wherever DOCK_EN_OUT reaches 1.825 V, with the fixed resistor at +1 % and R107 at -1 %.
- **The allowance.** With the fixed 15 kOhm the return may carry at most **26.45 uA** there (DERIVED).

| The return's sinks (record l8p's count) | Sinks | The return at DOCK_EN_OUT 1.825 V | Window |
|---|---|---|---|
| SENSE1 (RECORD) and board P's Q107 at its printed 25 C row | 2.08 uA | 1.058 V | holds |
| those and the AO3400A at the 76.25 C air | 23.89 uA | 0.863 V | holds |
| those and the AO3400A at round 4's 86.25 C site | 45.70 uA | 0.668 V | **FAILS** |
| SENSE1, Q44 and Q107 at the air on the doubling, no guard | 7.58 uA | 1.009 V | holds |
| those and the AO3400A at the air | 29.39 uA | 0.814 V | **FAILS** |

- **Even the most favourable corner fails.** At DOCK_EN_OUT 1.981 V with every part nominal the return reads 0.770 V, under
  0.7755 V: read held. A closed loop ramping through DOCK_EN_OUT 1.825 to 2.12 V may read held.
- **The site.** The AO3400A keeps the window only under 77.9 C. With Q44 and Q107 on the same doubling the limit is 74.2 C,
  under the 76.25 C air itself.
- **Labels.** The leakage rows are PRINTED: the AO3400A's 5 uA at 55 C and 30 V, the 2N7002's 80 nA at 25 C and 60 V. The
  doubling every 10 K and every site temperature are ASSUMED. SENSE1 is RECORD.
- **Why round 4 did not see it.** It compared the closed loop's ratio, RET/OUT 0.590 against 0.4603, at the pack's voltages.
  A constant sink on the return weighs most at the ramp's 1.825 V, where that ratio bounds nothing. Round 4's window predicate
  and its acceptance (c) on the window are **WITHDRAWN**. Every figure of record l8p above reproduces within its printed
  rounding.

**The three relabellings (guard 5b (2)); none moves a verdict.**
- **The trip accuracy** is printed at one condition only, VDD = 5 V. The closed loop brings the regulator to its table's input
  (VIN 6.0 V) from BRK_VIN 8.28 V, under the pack's least 10.6 V, so every trip is judged at VDD 5 V. Tripped, the loop keeps
  that input from 10.45 V. Below that a tripped switch holds on under 5 V and its reset point is not printed: a restart point,
  not the protection.
- **The regulator's 2.25 uA ground current** is printed at VIN 6.0 V and IOUT 1 mA only, TYPICAL elsewhere. The guard's
  18.25 uA is therefore a figure at that condition, inside the 30 uA allowance with 11.75 uA to spare.
- **Its plus or minus 1 % accuracy** is printed at IOUT 1 mA, its load regulation from 100 uA. At the switch's 16 uA the
  output's accuracy is NOT PRINTED; the trip accuracy's VDD = 5 V is taken as the regulator's plus or minus 1 % (ASSUMED at
  16 uA).
- **Read with them.** TI describes the regulator's UVLO and prints no threshold. The LM26LV's Figure 1 defines tEN and draws
  OVERTEMP low before it; that is a definition figure, not a limit.

**The corrections, judged on one count (guard 5b (3)).** Every off FET on DOCK_EN_RET is counted on the doubling at board A's
parts' 86.25 C (round 4's site):
- board A's Q44 (2N7002, drain on the return; Q45 and Q46 act on Q44's gate): 5.58 uA;
- board P's Q107 over Q108 (2N7002 in series, taken as one, counted warmer than record l8p's air): 5.58 uA;
- U48's SENSE1 (RECORD): 2.00 uA;
- the first inverter Q103's gate at its printed IGSS: 0.08 uA (an oxide leakage, ASSUMED not to double; 5.58 uA if it does,
  the "all doubled" figures).

That is 13.25 uA before the shunt (18.75 uA all doubled).

| Key | Correction | Shunt's leakage at 86.25 C | Allowance | Sinks (all doubled) | The return at 1.825 V (all doubled) | Window | Shunt's site limit (every FET at one temperature) |
|---|---|---|---|---|---|---|---|
| C1 | record l8p's (i): a 2N7002 shunt, one 15 kOhm | 5.58 uA | 26.45 uA | 18.83 (24.33) uA | 0.908 (0.859) V | holds | 98.7 C (91.7 C) |
| C2 | record l8p's (ii): the AO3400A, one 11 kOhm | 43.62 uA | 50.09 uA | 56.87 (62.37) uA | 0.790 (0.750) V | **FAILS** | 83.8 C (84.3 C) |
| C2 | the AO3400A, one 10 kOhm | 43.62 uA | 58.96 uA | 56.87 (62.37) uA | 0.854 (0.816) V | holds; fails all doubled | 86.9 C (86.8 C) |
| C3 | record l8p's (iii): the AO3400A, one 15 kOhm, its site bounded | 43.62 uA | 26.45 uA | 56.87 (62.37) uA | 0.568 (0.519) V | **FAILS**: its limit, 69.0 C, is under the air | 69.0 C (74.6 C) |
| C4 | this round's: C1 with the fixed resistor as two 7.5 kOhm in series | 5.58 uA | 26.45 uA | 18.83 (24.33) uA | 0.908 (0.859) V | holds | 98.7 C (91.7 C) |

Record l8p printed 7.7 uA for (i) (13.2 uA with Q44 and Q107 at the air) and a site to 103.8 C; on this round's warmer count
the 2N7002 carries 18.83 uA and its site runs to 98.7 C.

**Round 4's acceptance on each correction (guard 5b (3)).**
- **No-trip and trip sides.** They are the switch's and no correction moves them: 38.4 K at 10 A, 9.8 K in the 18 A service,
  6.0 K at condition C4; 15.68 K (13.56 K) left for the gradient.
- **The loop's readings**, each at 1 % at its worse sign, with the guard's 30 uA and the full count:

| Key | First inverter's gate closed, least, at 7.6 / 10.6 / 16.8 V (over 2.5 V) | Held DOCK_EN_OUT at 7.6 V (over 1.981 V) | Tripped return at 29.2 V (under 775.5 mV) | Regulator's 6.0 V input reached closed / tripped |
|---|---|---|---|---|
| C1 and C4 | 3.13 / 4.51 / 7.36 V | 4.32 V | 20.31 mV | from 8.12 V / 10.45 V |
| C2, 11 kOhm | 3.06 / 4.57 / 7.68 V | 3.77 V | 0.09 mV | from 8.59 V / 11.93 V |
| C2, 10 kOhm | 3.16 / 4.71 / 7.90 V | 3.59 V | 0.09 mV | from 8.66 V / 12.49 V |
| C3 | 2.69 / 4.07 / 6.92 V | 4.32 V | 0.08 mV | from 8.34 V / 10.45 V |
| C4 with one of the pair shorted | 3.81 / 5.46 / 8.85 V | 3.08 V | 29.01 mV | from 8.57 V / 14.53 V |

- **The 2N7002 on.** Its RDS(on) is printed at VGS 5 V (7 ohm at 50 mA) and 10 V only, at 25 C. The gate network drives at
  least 4.53 V: 17.2 ohm ASSUMED (the 5 V row scaled by the drive over its 2.5 V highest threshold, times 2 hot). The tripped
  return needs at most 657 ohm at the 29.2 V clamp (1.18 mA): 38 times that bound.
- **The 2N7002 off.** The switch's VOL (at most 0.2 V) reaches its gate as 0.195 V, against its least threshold of 1 V
  (PRINTED at 25 C; hot not printed). Its current at that gate voltage is not printed; IDSS at VGS 0 is the row counted, as
  for the AO3400A.

**The two failure modes the checker named for E-13b (guard 5b (4)).**
- **FM1, the fixed resistor shorted, with one resistor (C1, C2, C3).** DOCK_EN_OUT and the return become one node. A trip pulls
  both to ground and takes the guard's supply with it; the switch browns out and releases, the loop recovers and, still hot,
  trips again: the guard cycles. Each closed phase lasts about 39.8 ms (the regulator's 1.5 ms start, tEN 2.3 ms, the gate to
  2.5 V in 36.0 ms: DERIVED) against the RC hold's least 0.110 s, so the breaker is not restarted while the switch reads hot.
  The regulator's input capacitor, charging to its 2.7 V through R106 and R107, adds 5.00 ms per uF at 7.6 V: the cycle stays
  under the hold for an input capacitor under 14.1 uF (DERIVED). DD-7 reads the loop unpowered in each pull, not held and
  powered. E-13b's tripped DOCK_EN_OUT reads near 0 V: found at the
  next check.
- **FM1 with two in series (C4).** One short leaves 7.5 kOhm. The guard still trips with its supply in regulation (closed from
  8.57 V) and holds on its own supply when tripped: DOCK_EN_OUT is at least 3.08 V at 7.6 V, over the regulator's 2.7 V least
  input and board A's 1.981 V, so DD-7 reads held and powered. The window and every reading hold (allowance 91.47 uA). E-13b's
  tripped DOCK_EN_OUT tells it from the intact pair:

  | BRK_VIN | Tripped DOCK_EN_OUT, intact pair | With one shorted |
  |---|---|---|
  | 7.6 V | 4.32 to 4.57 V | 3.08 to 3.28 V |
  | 10.6 V | 6.09 to 6.37 V | 4.34 to 4.57 V |
  | 16.8 V | 9.76 to 10.10 V | 6.96 to 7.25 V |

  Both shorted is a double fault and returns to the cycle.
- **FM2, the regulator's pass element shorted.** The switch's VDD is then the closed DOCK_EN_OUT, over its 6 V absolute rating
  from BRK_VIN 7.60 V, the whole service. Its state after that is NOT PRINTED. An output held high holds the breaker off (found
  at once); held low or open, the guard is LATENT until E-13b, and the junction limit rests meanwhile on E-1's bar (G3's
  state). No correction here changes it.
- **The clamp considered for FM2, NOT TAKEN.** From the kit's zener sheet (Diodes DS18004 Rev 38): the BZT52C5V6 (5.2 to 6.0 V
  at 5 mA) sits 0.15 V over the regulator's 5.05 V and prints its reverse current at 2 V only, so its draw is not bounded
  against the 30 uA allowance; the BZT52C6V2 reaches 6.6 V, over the switch's 6 V. A clamp that prints both is Layer 6's
  search.

**The state before tEN, the window's other half (guard 5b (5)).** OVERTEMP before tEN is not printed; it is taken high, the
worse side, as record l8p does.
- **The gate network sized here (SESSION):** 47 kOhm from OVERTEMP, 1 uF and 1 MOhm to ground (44.9 ms, a divider of 0.955).
- OVERTEMP held at 5.05 V through the regulator's 1.5 ms start and tEN's 2.3 ms leaves the gate at 0.391 V, under the 2N7002's
  least 1 V. A trip reaches 2.5 V in 36.0 ms and the drive settles at 4.53 V.
- This bounds a ramp whose regulator output steps at its UVLO's release. A ramp held longer inside that unprinted band rests on
  TI's description and Figure 1: bench item E-13b (b2), not a desk result.

**SELECTED (SESSION), round 5: C4.**
- **The guard.** G2 with the LM26LV 130 C preset (LM26LVQISDX-130/NOPB), supplied by a TPS70950 from DOCK_EN_OUT. The shunt
  on DOCK_EN_RET is a 2N7002 (the kit's part, Q44's and Q107's) through the gate network above. The fixed resistor in RT1's
  place is two 7.5 kOhm 1 % in series. Round 4's AO3400A and single 15 kOhm are **WITHDRAWN** (L8P-F08).
- **Why the 2N7002, not C2 or C3.** At the same site on the same assumption its leakage is 7.8 times under the AO3400A's. So
  the window holds on every count read here: 0.908 V at the corner on the full count (0.859 V all doubled) against 0.84 V,
  with its site free to 98.7 C (91.7 C with every FET on the return at one temperature). C2 holds only at 10 kOhm, by 2.09 uA;
  it fails all doubled, and below 12.49 V it leaves a tripped switch under 5 V. C3 is not available.
- **Why the pair, not one resistor (C1).** C4 reads as C1 in every figure while intact. For one more resistor it turns FM1
  into a degraded state that still trips and holds, and that E-13b finds.
- **Authority.** SESSION: an engineering choice inside the task. No requirement, limit or service is lowered; the shunt adds
  no part type.
- **Reversed by:** C1 (one 15 kOhm) if the drafts' check finds the pair not worth its part; the 125 C preset as in round 4
  (E-13 reading a gradient over 15.68 K); or a check that refuses the count (the 2N7002's leakage printed or measured over the
  doubling's 5.58 uA at 86.25 C, or a site over 98.7 C).

**The acceptance on C-PROT rev 1, for the drafts and their check (guard 6, restated in round 5).**
- **(a) Composition.** The board A draft replaces record l8p's RT1 and composes with L4-E11's DD-7 draft in L4-E9's order;
  board P's and board E's drafts compose unchanged; the generators run to their end.
- **(b) Netlist, with mutations that fail.**
  - The two fixed resistors in series between DOCK_EN_OUT and DOCK_EN_RET, their midpoint on nothing else.
  - The regulator's input on DOCK_EN_OUT and its output on the switch's supply only.
  - OVERTEMP (pin 5, the push-pull) through the series resistor to the shunt's gate, with the capacitor and the pull-down
    from that gate to ground.
  - The shunt's drain on DOCK_EN_RET and its source on ground.
  - Mutations: the shunt on DOCK_EN_OUT; the open-drain output used; the regulator fed from VBAT; the pair's sum outside
    3.574 to 25.8 kOhm; one resistor in place of the pair; the shunt drawn as an AO3400A; the gate capacitor removed.
- **(c) Electrical.**
  - No trip under 127.8 C and tripped from 132.2 C at the switch (VDD 5 V, reached closed from 8.12 V).
  - The first inverter's gate at least 3.13 V closed; the return at most 20.3 mV tripped (the shunt's on-resistance assumed
    as above).
  - **The window as a ramp's reading:** the return at least 0.84 V at DOCK_EN_OUT 1.825 V with every off FET on the return
    counted (18.83 uA, 0.908 V; 24.33 uA, 0.859 V all doubled).
  - The gate under 1 V through 3.8 ms of OVERTEMP high, and over 2.5 V within 36.0 ms of a trip.
  - The guard's draw at most 30 uA; the regulator's input capacitor under 14.1 uF (FM1's cycle).
  - Board A's DD-7 reads the guard's trip as it reads board P's own pull (the return held, the loop powered), with one of the
    pair shorted too.
  - Not counted: the loop's surface and contact leakage (no figure is held); E-13b (b2) reads the built loop.
- **Physical, apart.** E-13 on the coupon; E-13b in place, as below.

**The correction scope, restated (drafted by their owners; nothing of theirs is edited here).**

| Owner | What changes |
|---|---|
| Board A: L4-E11 with board A's generator (record l8p's `apply_gen_sch_a_ptc.py` draws RT1 today) | RT1 becomes two 7.5 kOhm 1 % in series; the switch on an island at the battery FETs' pour's centroid; the regulator and its two capacitors; the 2N7002 shunt beside Q44, off the battery FETs' pour (counted at 86.25 C, free to 98.7 C), with its 47 kOhm, 1 uF and 1 MOhm; test points on TRIP_TEST, VTEMP and the pair's midpoint; L4-E11 20c's rows restated for the pair, with its load on the return counted with Q44, Q107 and the shunt (20c counts SENSE1 alone); 20f's docking row for the guard's start |
| Board P: record l8p | no part changes (R106 10 kOhm, R107 22 kOhm, the inverters and the detector stay); its draft of G2 reads this section; its Murata question (unsent) is no longer needed for the guard |
| Layer 5 | DOCK_EN_OUT's load on board A gains 30 uA; DOCK_EN_RET may be held at ground by board A's guard as by board P's detector |
| Layer 6; Layer 9 layout | the order codes and filed sheets of the switch and the regulator (the shunt is the kit's 2N7002); a supply clamp that prints both its voltage under 6 V and its current at 5.05 V, if one exists (FM2); the switch's island and its distance to each FET's tab |
| This record | E-13 restated (15.7). E-13b at commissioning and each service: (a) TRIP_TEST pulled high opens the breaker, released it restarts; (b) DOCK_EN_OUT read tripped within its band by BRK_VIN (FM1); (b2) the loop ramped slowly with the guard cold, the return never under 0.84 V while DOCK_EN_OUT is over 1.825 V (the state before tEN); (c) VTEMP with TRIP_TEST high reads 0.958 V for the 130 C preset (record l8p, Table 1). FM2 stays latent between checks |

**L8P-F07 STAYS OPEN, and L8P-F08 with it:** L8P-F07 and L8P-F08 stay OPEN until those drafts compose, read DRAWN with
mutations failing and pass an independent check on this acceptance. The Murata question drafted in record l8p stays unsent;
the guard no longer rests on it.
