## 15. The pack path's protection: W4DP-F2's element (the owner's correction, 4 October 2026)

**Status.** A drafted protection design: desk arithmetic, not drawn into any generator, nothing built, bought or measured.
**Revised after the targeted recheck PROTECTION: NOT CONFIRMED** (the breaker's arithmetic reproduced, the copper corrections
B1 to B3 confirmed as conditional, board P's existing protection confirmed unable to meet the criterion). This revision
answers two blockers and the minors:
- **B-P1**: a live docking took the breaker past its own limits. The make-last enable contact C-1b corrects it (15.4).
- **B-P2**: the battery FETs' target counted the FETs' own heating only. It is restated as a junction limit, and a third FET
  is selected (15.5).

**Corrected after the recheck PROTECTION: CONFIRMED AS CONDITIONAL** (no blocker, every figure reproduced). The corrections:
- the docking's timing (the insertion time belongs to the gauge's FET start only; on the enable the gate rises 55 us typical
  after UVLO's threshold, so the grace is the RC hold now selected);
- the third FET's designator is left to L4-E11 (Q41 is l8r2's VIN_RAW cut-off FET);
- BAT-F20 on the 10 A and 18 A rows;
- D1 judged on I2t;
- the PTC thermal guard reconsidered and selected.

The conditions C1 to C3 and the minors are written into 15.4 to 15.7.

Every figure is printed by `l9stk_protection.py` into `l9stk_protection.out` ("prot N" is its section) from 21 inputs pinned by
sha256. The calculation basis is TI's application report SLVA673A, "Robust Hot Swap Design" (equations 3 to 7, its 2.4 on
parallel FETs, its 3.1.2.2, 3.1.2.5 and 3.2.2.7 checks), applied to the LM5069's sheet (SNVS452G). SLVA673A carries no grant to
redistribute: it is held back in the ignored `v2/vendor/ti/held/`, and `fetch_held_back.py` fetches it and checks its sha256
(`ea1604c5...`). The CSD18510Q5B's safe operating area is read from its Figure 10 at 300 dpi
(`inputs/csd18510q5b-figure-readings-2026-10-04.json`, plus or minus 10 %).

### 15.1 The criterion (the owner's, replacing "at or below 24 A")

The element is judged on current AND time for every series part, not on one current:
- the service is never interrupted: 10 A held and 18 A for 60 s;
- every series part stays within its limits across the credible overload range, including any current under the trip held
  indefinitely;
- with board P's FETs welded and no firmware;
- with the tolerances, the detection and turn-off delays, the initial temperature (L4-E12's 76.25 C plus each part's own
  heating) and the retry's heating;
- the element itself within its voltage, current, thermal and SOA limits, **in every normal event, docking included**.

### 15.2 Board P's existing protection with its FETs welded (prot 1)

None meets it, as the recheck confirmed:
- The gauge's OCD1/OCD2, the AFE's AOLD/ASCD and the PTC act through the welded Q1/Q2.
- The second level U2 has no current input.
- F2's heater is fired by U2 or the gauge's FUSE output (firmware).
- F2's element assures no opening under 60 A, and the blades none under 33.75 A.

### 15.3 The limiting part's current and its uncertainty (prot 2)

Q39/Q40, board A's battery FETs (L4-E11), FETs only. **Derived, not a rating.**
- RDS(on) at L4-E11's 150 C bound, 21.136 mOhm each.
- The installed path at E11-29's **target** of 33.12 K/W, not a measurement.
- With both FETs at the bound, the even split gives each the largest loss.

| Installed path | From +70 C | From 76.25 C |
|---|---|---|
| 20 % lower (26.50 K/W) | 23.90 A | 22.95 A |
| as targeted (33.12 K/W) | **21.38 A** | **20.53 A** |
| 20 % higher (39.74 K/W) | 19.52 A | 18.74 A |

The 22 to 23 A exposure stands. A trip allowed at the cells' 24 A leaves these junction temperatures, held:

| Current | From +70 C | From 76.25 C |
|---|---|---|
| 22 A | 154.7 C | 161.0 C |
| 23 A | 162.6 C | 168.8 C |
| 24 A | 170.8 C | 177.1 C |

### 15.4 The selected element and the docking correction (prot 3 and 3a)

**C-1, an LM5069-2 circuit breaker on board P,** from Q2's source to PACK_P. It acts on current alone, with no firmware and with
Q1/Q2 welded. The parts are already in the kit:
- the controller board E's U6 uses (LCSC C111822);
- the FET board A's PA stage uses (C2876544);
- the clamp on board A's VBAT.

| Item | Value | From |
|---|---|---|
| Sense RS | 4 mOhm and 7.5 mOhm in parallel, 2.6087 mOhm, 1 % and at most 50 ppm/K: plus or minus 1.5 % for the parts only (the traces and Kelvin taps are E-9's) | its window 2.6015 to 2.6546 mOhm |
| Current limit | 18.32 least, 21.08 typical, **23.93 A largest**: 0.07 A under the cells' 24 A, 0.32 A over the 18 A service (VCL 48.5 to 61.5 mV, TJ -40 to 125 C) | **the table is printed at VIN 48 V and used at 10.6 to 16.8 V** (Q-TI-L9S-1, E-2, E-3, E-9) |
| Breaker | 30.21 to 50.59 A (VCB 80 to 130 mV), released 16.5 us after it (tCB 1.2 us, 690 nC at 45 mA) | the sheet's least sink |
| Power limit | RPWR 8.45 kOhm: 32.52 W, VSNS 5.05 mV; 24.71 to 40.32 W with the table's spread read as a ratio, 71.16 W read as an offset | relied on: without it 402.1 W (E-2, Q-TI-L9S-1) |
| Fault timer | 10 nF: 0.282 to 0.897 ms; the gate off 395 us later; **clearing at most 1.292 ms**; the insertion time 4.23 to 15.25 ms runs only when VIN passes PORIT (a start by the gauge's FET) | VTMRH, ITIMER, the insertion current at their limits |
| dv/dt start | 22 nF into 593 uF: **inrush at most 0.659 A** for at most 40.7 ms; 11.1 W, under the power limit's least 24.7 W | SLVA673A 2.2.2, 3.2.2.7 |
| Retry (-2) | duty at most 1.33 % (0.5 % typical), dwell at most 0.222 s, 0.53 W average | the timer at its limits |
| FETs | 2 x CSD18510Q5B, 40 V, VGS 20 V against the gate's 12.6 V, IDM 400 A against the breaker's 50.59 A | SLVA673A 3.1.2.2 |
| FETs held at 23.93 A | 0.247 W each; case 101.0 C with both losses through one pad, junction 101.2 C (TI asks under 125 C) | equation 4 |
| FET SOA at 16.8 V | case 103.0 C retrying, derating 0.376; fault pulse 40.32 W for 1.292 ms against 71.1 W: **0.57**; start 11.1 W for 20.3 ms against 19.0 W (DC line): **0.58**; with the figure's 10 % against them 0.63 and 0.65; TI asks at most 0.67 | equations 5 to 7 |
| Clamps | SMCJ18A on VIN (VR 18 V, VC 29.2 V at 51.4 A); D1 SMBJ20A on PACK_P carries the lead's freewheel at turn-off (LM5069 11.1.2 B), judged on I2t: its 100 A 8.3 ms half-sine is 41.5 A2s, which the freewheel at the pack's 480 A prospective stays within for any loop L/R up to 0.36 ms (12.6 uH in that loop) | IF-6: both return to PACK_N, so R10 sees a clamp short |
| Controller | VIN 9 to 80 V recommended, on from 9 V at most; the pack 10.6 to 16.8 V; OVLO to ground; UVLO from VIN through R_U 200 kOhm into C_U 3.3 uF (50 V), released by the enable loop | UVLOTH 2.45 to 2.55 V, UVLOHYS 12 to 30 uA, UVLODEL 55 us typical (no maximum) |

**B-P1, docking.** Without a correction the breaker is on when the dock's power pins mate, so a docking reaches E11-30's
242.9 A:
- VIN to SENSE reaches 0.634 V, against the controller's 0.3 V maximum;
- the 10 us line at 16.8 V, derated to the 103.0 C case, is 91.8 A: the peak is 2.64 times it, and 1.66 times at a 75 C case.

A known excursion in a normal event is a design correction, not a coupon.

**C-1b SELECTED: a make-last enable loop into UVLO, with an RC hold** (TI's remedy in the LM5069 sheet, 11.1.1 and Figure 45):
- **The circuit.** The loop leaves board P from VIN through 10 kOhm on one J_SMB contact, with a ground contact beside it, and
  crosses the dock on two contacts 1 mm short of the power pins. On board A it passes the chip PTC beside the battery FETs (the
  thermal guard, 15.5). It returns on a second J_SMB contact to a 22 kOhm divider on a first 2N7002's gate. That FET holds a
  second 2N7002's gate low; the second, when on, discharges UVLO through 150 ohm. UVLO charges from VIN through R_U, the
  series resistor, into C_U.
- **The inverters' bounds.** The gates read at most 17.4 V under VIN's 29.2 V clamp against the 2N7002's 20 V. At the pack's
  10.6 V they read at least 2.95 V and 5.3 V, over its 2.5 V threshold. The UVLO discharge peaks at 107 mA against its 115 mA.
  UVLO passes 2.55 V at 10.6 V against the 30 uA hysteresis sink (4.6 V).
- **The timing, restated.** The insertion time runs only when VIN passes PORIT, so 4.23 to 15.25 ms applies to a start by the
  gauge's own FET, not to a docking. On the enable, the LM5069 raises the gate UVLODEL (55 us typical, no maximum printed) after
  UVLO passes its threshold. The RC hold makes that **0.110 to 0.593 s after the enable mates**. Then a dv/dt start follows:
  **0.659 A at most, VIN to SENSE 1.72 mV**.
- **Undocking.** The loop opens. The first inverter is off in 2.5 us and the second on in 16.0 us. UVLO falls under its
  threshold in 1.097 ms, and the gate is low 395 us later: 1.51 ms in all. That is before the pins part at a withdrawal under
  0.66 m/s.
- **The gauge's own FET.** Its turn-on is a start too, so E11-30's waveform no longer arises.

**Condition C1, the mating order** (owners: Layer 7 for the order, board P's generator for the hold). Every power pin mates
before the enable contacts at any angle the dock's guides allow.
- **Without a hold:** a reversed order of more than 1.88 ms lets OUT rise (at 1.111 V/ms) past 2.09 V and meet the breaker's
  30.21 A threshold through the 69.2 mOhm loop at mate.
- **SELECTED, the RC hold:** a reversed order up to 111.6 ms is tolerated. The order remains Layer 7's condition beyond that.

**Condition C2, a fault on the enable** (owners: board P's and board E's generators, Layer 7, the supplier for E-12). The enable
is a loop through board A, not a single wire to its ground.
- **A short to ground** on either conductor holds the breaker off: fail-safe, and revealed at the next docking because the kit
  does not start.
- **A short between the two conductors** is kept off by a ground contact between them in J_SMB and on the block.
- **The inverters' own failures** are the remaining latent faults. E-12 finds them at commissioning and at each service: PACK_P
  dead undocked, and each loop conductor shorted to ground in turn.

**Not taken: an inrush element at board A's dock entry.**
- Board A's pre-charge pin J_PRE1 (10 ohm into 593 uF, a 5.93 ms time constant) would need a lead over the power pins: 12.4 ms to
  keep the step under the breaker's least threshold, and 4.3 ms to keep VIN to SENSE under 0.3 V. A hand sets the lead.
- A series element in the 23.93 A path heats beside the battery FETs, whose junction is the binding limit (15.5).

**The charge direction.** The LM5069 limits no reverse current. A charge passes the FETs' channel while the breaker is on, and
their body diodes while it is off. The gauge's 1 A precharge in one diode is 1.00 W (VSD 1 V at most), TJ 126.2 C. The charger
bounds the charge current, the gauge's own levels protect it, and F1 and F2 back them, as before.

**Board P's area (IF-2).** The 0.376 derating rests on the FETs' installed path. TI's margin holds up to an installed RthJA of
**52.5 C/W per FET**. The sheet prints 50 C/W on 1 in2 of 2 oz and 125 on its least pad.
- Board P is 70 x 44 mm (3080 mm2 a face). The P2 placement uses 798 mm2 of the top face, and the holes 199. The bottom face is
  empty.
- Two 1 in2 pads take 1290 mm2 of the 2084 mm2 left. That leaves 793 mm2 for the round 4 parts, the breaker's other parts and
  the bands where they do not lie in the pads (the FETs' drain pads are the breaker's input band).
- This is an area budget, not a floor plan. The generator shows the plan, and E-11 measures the installed path.

**Also not taken (prot 3):**
- A breaker limited to the pair's 20.53 A: its least limit, 15.71 A, falls under the service.
- A blade opening under the pair's current: at most 15.21 A, and the service at 118 % of it is not assured.
- A single-wire enable to board A's ground: a short to ground, the commonest harness fault, would enable the breaker unseen (C2).
- No RC hold: a reversed mating order of 1.88 ms would bring B-P1 back (C1).
- A controller with a tighter limit tolerance now: the LM5066I of SLVA673A's examples, its sheet not held. It is E-5's fallback.

**The clamp failing resistive with board P's FETs welded** (two faults, 33.75 to 150 A). The breaker is downstream of the clamp
and cannot act. Board P's loop and the clamp itself then carry the current on F1's 600 s and 5 s rows, and F2's 200 % opens
within 60 s. Alone, the clamp's failure is cleared by the AFE's AOLD (30 A, 20 ms) through Q1/Q2. Disposition: a second fault,
stated, no new defect; the battery stream reviews it.

### 15.5 B-P2: the battery FETs' junction limit, and the selection (prot 4)

**The limit (DD-2 and E-1, restated).** The hottest battery FET's junction stays at most 150 C, held at 23.93 A from 76.25 C,
with these in place:
- the band carrying the current (9.16 K at either weight, decision 35's model);
- R17 dissipating its 2.86 W.

That leaves 64.59 K for the FETs and R17's coupling.

**R17's coupling is bounded with no layout known.** In a passive thermal network the point heated is the hottest, and transfer
impedances are reciprocal. So R17's coupling into a junction is at most that FET's own Zself. Designed apart (off the FETs' pour),
it is held to 1 K/W, which E-1 reads by heating R17 alone.

| FETs | Loss each at 23.93 A | FETs only | R17 apart (1 K/W) | R17 anywhere |
|---|---|---|---|---|
| the pair, (Zself + Zmut) | 3.027 W | 21.34 K/W | **20.39 K/W** | 10.96 K/W |
| three, (Zself + 2 Zmut) | 1.345 W | 48.01 K/W | **45.88 K/W** | 15.34 K/W |

E11-29's present target is 33.12 K/W, which L4-E11 judged of the order a board pour gives. The first revision's 24.37 K/W
counted the FETs' heating only; with the band's 9.16 K it reaches 159.2 C.

**SELECTED: a third BUK6Y10-30P, with R17 designed apart.** Its designator is L4-E11's to give: Q41 is taken on board A by
record l8r2's VIN_RAW cut-off FET (CSD19532Q5B).
- **Why.** The path it asks is 1.39 times E11-29's present target, where the pair would need 0.62 of it.
- **Cost.** Ciss: three FETs are 7.08 nF typical at -15 V and about 8.61 near 0 V, against TI's 5 nF guidance (SLUSE65A p.92). The
  pair is already over that guidance near 0 V (5.74 nF), so E11-37's bench with three FETs decides, with Q-TI-17 extended to
  three. **Condition C3** (owner L4-E11): production conformance needs Q-TI-17's answer or E11-37's bench with three.
- **Fallback.** The pair at 20.39 K/W.

**THE THERMAL GUARD, reconsidered and SELECTED** (owners: board A's generator with L4-E11 for the PTC beside the battery FETs,
board P's generator for the divider). It guards against the 45.88 K/W path never being met, unit by unit, which a coupon
cannot.
- **The part.** The kit's PRF15BB103 chip PTC: 10 kOhm plus or minus 50 %, 47 kOhm at 130 C plus or minus 3 C, 32 V. It is
  already on board P as RT1.
- **Where.** In the enable loop on the battery FETs' copper.
- **The trip.** The first inverter stays on up to 47 kOhm at 10.6 V (its gate 2.95 V against 2.5 V) and is off from 338 kOhm at
  16.8 V. So the breaker opens between the PTC's 47 kOhm point (127 to 133 C) and its 338 kOhm point, which the sheet does not
  print (E-13).
- **Margins.** The service at the allowances reads 118.0 C, 9.0 to 15.0 K under the band. A junction leads its copper by 1.88 K
  at 23.93 A (Rth(j-mb) 1.4 K/W).
- **Restart.** After a trip the breaker restarts through the RC hold when the PTC cools.

At the allowances the junction reads:
- 89.4 C at 10 A;
- 118.0 C in the 18 A service;
- 150.0 C at 23.93 A, by construction.

**The other series parts at 23.93 A from 76.25 C:**

| Part | Reading | Fraction | Status |
|---|---|---|---|
| the cells, 3P of 8 A | 7.98 A a cell at an even split | 1.00 | printed; E-5: the groups must share within 0.28 %, so its **fallback is named now**: a controller whose limit spread with its sense is at most 1.270 (for a 5 % split; the LM5069's is 1.307) |
| **Q1 on board P under BAT-F20** (CHGIN = 1, the reading above T3) | **its body diode 23.9 W** (VSD 1 V at most); about 7 W at 10 A already | | **DESIGN DEFECT DD-5** (BAT-F20, EQ-15) |
| Q1/Q2 on board P, both enhanced | 0.711 W each; TJ 111.8 C on its own pad, 147.4 C with both losses through one pad | 0.96 | derived; the x1.8 is the CSD18510Q5B's (ASSUMPTION, E-8) |
| the breaker's FETs | TJ 101.2 C | 0.51 of TI's 125 C | derived (IF-2, E-11) |
| R17 (5 W) | 2.86 W | 0.57 | derating NOT HELD (E-6) |
| R10 on board P (2 W) | 1.15 W | 0.57 | derating NOT HELD (E-6) |
| the breaker's sense | 0.97 W in 4 mOhm, 0.52 W in 7.5 mOhm | | a requirement on Layer 6's parts: 2 W each at the band's temperature |
| the XT60 (30 A) | 23.93 A | 0.80 | printed |
| the dock contacts | 5.98 A a pin at an even split | 0.66 | the split NOT HELD (E-4) |
| the 25 A blades | 95.7 % of rating | 0.87 of the 110 % hold | E-7 |
| F2's element (30 A) | 79.8 % | 0.80 | printed |
| the copper | 9.16 K | 0.92 of 10 K | section 14 |
| the barrel field | 0.75 A a barrel, 7.62 K | 0.76 | section 14 |
| the 3568 holder | no current rating | | DESIGN DEFECT DD-4 |

### 15.6 The protection table (prot 5)

| Case | Current, duration | Largest actual trip threshold | Longest clearing time | Limiting component | Margin | Evidence |
|---|---|---|---|---|---|---|
| 10 A continuous | 10.0 A held | none reached (18.32 A least) | not a fault | **Q1's body diode under BAT-F20** (CHGIN = 1, above T3), 7 to 10 W against the 1.48 W its pad holds; with BAT-F20 closed, the XT60 at 0.33 | **Q1 OVER (4.7 x)** | **DESIGN DEFECT DD-5**; printed (VSD, RthJA) |
| 18 A for 60 s | 18.0 A, 60 s | none reached (18.32 A least; 21.08 A typical) | not a fault; firmware ends it | **Q1's body diode under BAT-F20, up to 18 W**; with BAT-F20 closed, the battery FETs at 118.0 C (the guard 9.0 to 15.0 K above) | **Q1 OVER**; 32.0 K at the battery FETs; the least limit 0.32 A over the service | **DESIGN DEFECT DD-5**; derived; E-1, E-10 (the key-down current), E-13 |
| an overload under the unit's limit, held | 18.00 to 23.93 A, indefinitely | 23.93 A (VCL 61.5 mV, RS -1.5 %) | none: held by design; the thermal guard | the battery FETs at 150.0 C; the cells at 0.997 of 8 A; **Q1's body diode 23.9 W under BAT-F20** | 0 K at the allowances; 0.28 % split; **Q1 OVER** | **DESIGN DEFECTS DD-2, DD-5**; E-1, E-5 |
| an overload over the unit's limit | limited to 23.93 A, then off | 23.93 A | 1.29 ms from the onset (timer 0.897, gate 0.395); regulated after tCL (45 us typical, no maximum) | the breaker FET, 40.3 W for 1.29 ms against 71.1 W | 0.57 (TI at most 0.67) | derived: the power limit at 5 mV and 10.6 to 16.8 V not printed (E-2) |
| a hot short, board P's FETs welded | 240 to 480 A prospective | 50.59 A (VCB 130 mV) | 16.5 us to the release, then as above: 1.31 ms | the breaker FET: IDM 400 A against the breaker's threshold; VIN to SENSE over 0.3 V above 116.8 A | 0.13 of IDM | (c) MISSING: E-3; the 0.3 V to TI (Q-TI-L9S-1) |
| a start into a short | 2.40 A at most | the power limit | 1.29 ms | the breaker FET, as above | 0.57 | derived |
| a start (the gauge's FET on, a retry, assembly) | 0.659 A at most for 40.7 ms, from the insertion's end (4.23 to 15.25 ms after VIN passes PORIT) | none: 11.1 W under 24.7 W | not a fault | the breaker FET, 11.1 W for 20.3 ms against 19.0 W | 0.58 | derived; IF-1 |
| **docking, the make-last enable (C-1b)** | 0.659 A at most for 40.7 ms, from 0.110 to 0.593 s after the enable mates (the RC hold, then UVLODEL 55 us typical, no maximum) | none: a start | not a fault | the breaker FET as a start; VIN to SENSE 1.72 mV | **0.58** | derived; DD-6 until drawn; conditions C1, C2; E-3, E-12 |
| docking without the enable (the uncorrected design) | E11-30's 242.9 A with the breaker on | 50.59 A | 16.5 us to the release | the 10 us line derated to 103.0 C is 91.8 A; VIN to SENSE 0.634 V | **OVER**: 2.64 x the line (1.66 x at 75 C); 2.11 x 0.3 V | **DESIGN DEFECT DD-6**, corrected by C-1b (not a coupon) |
| a persistent fault, retrying | the power limit at 1.33 % duty at most | as above | each try as above | the breaker FET, 0.53 W average, case 103.0 C | inside the derating | derived |
| charging (the reverse direction) | the charger's current; 1 A precharge in a body diode while off | none: no reverse limit | not a fault | the breaker FET's body diode, 1.00 W, TJ 126.2 C | 23.8 K | printed (VSD); derived |
| the clamp shorted with board P's FETs welded (two faults) | 240 to 480 A prospective | F1, 25 A MINI | at most 0.1 s at 150 A and over | board P's bands (decision 28) | the clamp's short alone is cleared by the AFE's ASCD (R10 sees it, IF-6) | printed (F1's 600 % row); disposition stated, no new defect |
| the clamp failing resistive with board P's FETs welded (two faults) | 33.75 to 150 A | F1 and F2 | F1's 600 s and 5 s rows; F2's 200 % opens within 60 s | the clamp's own dissipation and board P's loop; the breaker is downstream and cannot act | alone, the AFE's AOLD (30 A, 20 ms) through Q1/Q2 | printed (F1's and F2's rows); a second fault: disposition stated, no new defect (the battery stream reviews) |
| the shore input, Q7 shorted | F1's envelope (not through board P) | F1, 10 A MINI | section 14.6 | J_DCIN, R19 | **OVER** | **DESIGN DEFECT DD-3** (L4-E11) |

**The supported operating envelope**, once DD-1, DD-2, DD-5 and DD-6 close:
- 10 A held and 18 A for 60 s from 76.25 C, with no trip on any unit;
- any current to 18.32 A held on every unit;
- between 18.32 and 23.93 A, a unit holds or clears by its own threshold;
- above 23.93 A, every unit clears within 1.29 ms of its limit's onset;
- a docking is a start;
- no firmware and no working FET of board P in that path.

### 15.7 Design defects, interfaces and the evidence owed (prot 6)

**Design defects** (unresolved; a coupon never stands in for their correction):

| Defect | Owner |
|---|---|
| DD-1 W4DP-F2: no firmware-independent element with board P's FETs welded; the breaker of 15.4 is drafted here, not drawn | board P's generator, with W4DP-F2's owner (the battery stream) |
| DD-2 the battery FETs' junction limit (15.5): a third BUK6Y10-30P (its designator L4-E11's), (Zself + 2 Zmut) at most 45.88 K/W with R17 apart, the thermal guard behind it; the pair would need 20.39; condition C3 | L4-E11 (E11-29 restated as the junction limit; the third FET, its designator and land; E11-37 with three) |
| DD-3 R19 passes its 3 W and J_DCIN its VH rating inside F1's envelope on the shore input (section 14.6) | L4-E11 |
| DD-4 the Keystone 3568 holder prints no current rating | Layer 6/7 |
| DD-5 BAT-F20: with CHGIN = 1 above T3 the discharge runs through Q1's body diode, 23.9 W at the breaker's 23.93 A | the battery stream (BAT-F20, EQ-15) |
| DD-6 docking with the breaker on is past its SOA and VIN to SENSE's maximum; C-1b, the make-last enable loop with its RC hold and the thermal guard, is drafted here, not drawn; conditions C1 and C2 (15.4) | board P's generator with the battery stream (the UVLO circuit and the hold); board E's generator (two J_SMB contacts with a ground between); Layer 7 with L4-E11 (two make-last dock contacts, the loop and the PTC on board A) |

**Interface demands:**
- **IF-1** board A's loads on VSYS stay off until the breaker's start ends (at most 40.7 ms after the gate rises, which is up to
  0.593 s after the enable mates), or follow its PGD. Owners: L4-E11 with board A's generator.
- **IF-2** each breaker FET's installed RthJA at most 52.5 C/W; the area budget of 15.4; the controller beside RS, and VIN's
  bypass at RS (the sheet's 11.1). Owner: board P's generator.
- **IF-3** a stage for the breaker in the energy chain, between PACK_FETS and PACK_LEAD (its limit 23.93 A). Owner: the
  integrator.
- **IF-4** the gauge's levels stay the first level; no setting changes. Owner: the firmware owner.
- **IF-5** the pack's terminal is live only while the enable is closed; any other host closes it or gets a dead terminal
  (fail-safe). Board A's J_PRE1 and R1 are no longer exercised at docking, and E11-30's docking waveform no longer arises.
  Owners: the battery stream (CONOPS), board A's generator, L4-E11.
- **IF-6** the gauge's PACK and VCC taps stay on Q2's source node, and the clamp and the controller return to PACK_N. The
  breaker's output becomes the terminal PACK_P, with D1 on it (judged on I2t, 15.4). The enable circuit's parts and bounds are
  those of 15.4. Owner: board P's generator.

**Missing physical evidence** (specimen; acceptance; supplier task):

| Item | Specimen | Acceptance | Task |
|---|---|---|---|
| E-1 the battery FETs' junction limit | L4-E11 section 17's coupon with the three battery FETs, the band carrying 23.93 A and R17 dissipating in place | the hottest junction at most 150 C referred to 76.25 C; R17's coupling into each junction at most 1 K/W (heat R17 alone) | the body diode's VSD method |
| E-2 the power limit at its design point | six LM5069-2 on the board P specimen | the shorted-output current at 16.8 V and 10.6 V within 1.47 to 2.40 A at -40, 25 and 125 C (the table is printed at 48 V) | the supplier's bench |
| E-3 the hot short and the enabled docking | board P with Q1/Q2 bypassed, the 12 AWG lead, boards E and A as built, a charged block | 10 shorts and 100 dockings with the FETs' case at 103 C: the gate low within 16.5 us of VCB; the docking current at most 0.659 A; VIN to SENSE recorded; VCL within 48.5 to 61.5 mV; each FET's RDS(on) within +5 % | the supplier's fault bench |
| E-4 the dock contacts' split | the fitted lot's four-pin set | the lowest pin at least 0.593 of the highest, at the blades' 25 A (0.553 at the breaker's 23.93 A) | each pin at mid-stroke |
| E-5 the cells' parallel split | each series group of the built block | no cell over 8 A at 23.93 A (within 0.28 %); fallback: a controller whose limit spread is at most 1.270 | the pack builder; Layer 6 for the fallback's sheet |
| E-6 R17, R10 and the breaker's sense derated | the makers' sheets | each at its 15.5 reading at the band's temperature | Layer 6 |
| E-7 the blades at the inside air | the fitted lot in the 3568 holder | the service itself: 18 A for 60 s after 10 A held at 76.25 C, without opening | the supplier; Layer 6 reads the rerating curve |
| E-8 Q1/Q2's installed path and RDS(on) at temperature | board P's first specimen; the CSD17570Q5B's Figure 8 | TJ under 150 C at 23.93 A from 76.25 C, both enhanced | board P's generator; Layer 6 |
| E-9 the breaker's actual current limit | six board P specimens, the paralleled shunts' traces and Kelvin taps as built | between 18.32 and 23.93 A at -40, 25 and 125 C, at 10.6 and 16.8 V | the supplier's bench |
| E-10 the pack current at key-down | board A and the transmitters at the 18 A service | under 18.32 A, or excursions above it each under 0.282 ms and under 1.03 % of the time (the timer integrates them) | the supplier's bring-up bench |
| E-11 the breaker FETs' installed path | the board P specimen | RthJA at most 52.5 C/W per FET | the body diode's VSD method |
| E-12 the enable loop | the built kit at commissioning and at each service | undocked, PACK_P dead; each loop conductor shorted to ground in turn, the breaker stays off when docked; the release after the enable mates at least 0.110 s | the supplier's commissioning procedure |
| E-13 the thermal guard | the battery FETs' coupon (E-1) with the PTC in place, and one with a FET's thermal pad left unsoldered | no trip through the service (18 A for 60 s after 10 A held at 76.25 C); the breaker off before the hottest junction passes 150 C at 23.93 A held | the supplier's thermal bench |

**Maker questions, drafted, not sent:**
- **Q-TI-L9S-1 (TI, the LM5069).** Three questions:
  - the power limit's accuracy at VSNS 5.05 mV;
  - every limit at VIN 10.6 to 16.8 V, since the table is printed at 48 V;
  - VIN to SENSE above its 0.3 V maximum in the microseconds before the gate is low in a hot short (above 117 A on this sense).
- **Q-TI-17 (L4-E11's).** The BATFET's 5 nF guidance, now with three FETs.

### 15.8 What the recheck covers, and the next deliverable

After the conditional confirmation the coordinator checks these corrections; no further independent recheck. The scope stays
the changed protection design and its affected interfaces only:
- `l9stk_protection.py` and its output;
- option (4) of (L9STK CU) in `l9stk_copper.py` (out 8) and `apply_decisions_l9stk.py`;
- the findings L9C-F16 to L9C-F22.

The copper sizing of section 14 is unchanged.

**Next deliverable**, in this order:
1. Board P's generator draft of the breaker with its enable loop and RC hold (DD-1, DD-6, IF-2, IF-3, IF-6).
2. Board E's two J_SMB contacts with a ground between, and Layer 7's two make-last dock contacts with the loop and the PTC on
   board A (DD-6, C1, C2).
3. L4-E11's third battery FET, its designator, and E11-29 restated as the junction limit (DD-2, C3), with IF-1.
4. The battery stream's answer to BAT-F20 (DD-5).
5. Then the supplier's E-1, E-2, E-3, E-9, E-11, E-12 and E-13 on the first specimens.
