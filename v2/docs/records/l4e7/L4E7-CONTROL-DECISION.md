# L4-E7R: the control decision for REQ-016's 100 W (layer 4, MESHSAT-1357)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured. The owner's instruction of 1 October
2026: establish whether the proposed control supports REQ-016's retained limit, "at most 100 W into the stage", across the
permitted operating range, and if it does not do so on warranted evidence, choose a defensible approach. His decision
process of 2 October 2026 shapes the third round: three separate checks with their own results, one error budget for the
whole limiting chain, a margin justified by what it must absorb, the circuit corrections, one coherent candidate and a
decision. It follows the targeted recheck `checks/astra-check-l4e7r-2.md` (NOT YET) and carries the **CS101 correction**
after the coordinator's closing check `checks/check-l4e7r-3.md` (not accepted on one defect: the backstop tripped under
TEST-PLAN M2's CS101) and the owner's CS101 instruction of the same day; the last section maps each item to its change.
Every figure below is printed by section 10 of `l4e7_stage_settings.out` (the script `l4e7_stage_settings.py`, after its
reproductions of section 0); the sheet values in the verdict's table are section 9's. Evidence classes: **warranted** (a
limit the maker prints for the condition it is used at, with its page; "printed test limits" for a passive's drift rows),
**documented dependency** (a row at another condition carried by a printed curve or typical row), **typical**,
**inferred**, **assumption** (named, with its break-even), **requirement**, **MODELED**. The decision is the session's,
taken under the owner's standing rule of 26 September 2026 (`ruled_by: SESSION`): it changes no requirement, spends no
money and buys nothing.

## What is bounded (item 1)

- **The measurement boundary**: board E's panel entry, J_SOLAR and PV_IN (REQ-016's acceptance names the panel entry,
  PV_IN and PV_P). Everything behind it is the stage: F2, the bulk, the sense bank, the ceramics and the LT8705A stage.
- **The operating conditions**: a panel inside REQ-016's window (open circuit at most 25 V at its coldest, held at 17.6 V
  by the stage), the envelope's -20 to 62.1 C; the prototype measurement is a bench supply on a 100 W panel's curve
  (SC-36).
- **The averaging window**: REQ-016 states none, and neither of its verification methods (calculation, prototype
  measurement) names one. The interpretation (SESSION, CONDITIONAL for layer 8 to confirm): the mean power over any
  0.1 s, the shortest window a bench power reading forms. The parts the limit protects heat over seconds and longer; the
  excess the window admits after a trip (the response allowance of check (b) at the source's whole current) puts 0.15 mJ
  into one bank part and 0.76 mJ into RSENSE1, against the 100 mJ and 300 mJ their continuous ratings carry in one window.
  A longer window would be easier to meet and is not taken.
- **Three checks, each with its own result**: (a) normal operation; (b) startup, shutdown and the fault response; (c) the
  parts' ratings during the specified disturbances, and M2's immunity (the CS101 correction). An averaged pass never
  excuses an absolute maximum.

## The verdict on the present control: NOT SHOWN on warranted limits alone

The LT8705A's input-current limit as set (RIMON_IN 23.2k, RSENSE1 15 mOhm, `L4E7-STAGE-SETTINGS.md`) holds 100 W only
under values no maker warrants. Each is classified in `L4E7-QUALIFICATION.md`; the break-even is how far it may move
before the 25 V corner reaches 100 W:

| Value | What 8705af (or Milliohm) prints | Break-even |
|---|---|---|
| EA2 | voltage gain 130 V/V, typical only (p.5) | 25.026426 V/V (stack A, cold); 55.191656 V/V (stack C's other terms) |
| A7 | gm 0.94 / 1.06 mmho, only at 50 mV differential and CSPIN = 5.025 V (p.5) | 0.904726 mmho (stack A), 0.936935 (stack C), 0.939053 (every conservative assumption together) |
| LINE | 0.005 %/V at 25 C, not switching (p.4) | 61.6 times the printed maximum (stack A); 47.1 with EA2 at 65 V/V |
| TCR | HoJLR2512: +-50 ppm/K tested +25 to +125 C only (Ho-A0 pp.2, 4) | 882.027 ppm/K (stack A), 122.295 ppm/K (stack C) |
| TJ | the I grade's -40 to 125 C (p.3); U5's junction is an INFERRED estimate | 125 C junction, 19.6 K above the estimate |

Under all their conservative assumptions together the corner reads **99.8992 W (margin 0.1008 W)**: CONDITIONAL.

## The comparison (three approaches)

Each bound is the highest static input power the approach lets through, at 25 V. The energy is the stage's input on
SC-37's mean September day on the pinned SunPower SPR-E-Flex-100 through the replay's `trace()`, at the kept hold's lower,
nominal and upper corners, and on the check's own bright day (a twelve-hour sine to 1000 W/m2, 18.1 C air, the nominal
hold; this model reproduces the check's 495.3165 Wh at 26.1k and 465.6367 Wh at 28.7k), the regulation at its lowest;
hours the limit binds in brackets. "Noon" is the reduction against 23.2k at bright noon: the regulating current's, then
the input power's.

| | (A) present control, argued margins | (B) INA250A2 sensor, the trip chain of C | (C) WSL bank, INA169, TPS3701, TPS3808 |
|---|---|---|---|
| Bound | 97.8269 W | 98.2217 W (every row at its printed value) | **93.5521 W** |
| Status | CONDITIONAL | CONDITIONAL | **CONDITIONAL** on two named assumptions about its own sensor |
| Evidence | warranted: IMON_IN fault maximum 1.67 V, RSENSE1 1 %, RIMON_IN 0.1 %, the drifts; **assumption**: A7 away from its test point, the fault threshold's line dependence at twice the reference's, RSENSE1's cold TCR at 100 ppm/K, the fault's timing | warranted: the TPS3701, TPS3808 and RT rows, the offset's supply and common-mode rows at 0 A; **conditional**: the gain error and offset at VS = 3.3 V and VREF = 0 V (printed at 5 V and 2.5 V), the CMR away from 0 A, the shunt's stress rows (typical, 0.425 %), the nonlinearity and output impedance (typical), the VIN+ bias across temperature (25 C row) | warranted, every term at its own condition; **assumption**: U18's gain move at the trip's own sense voltage (G_CM) and its VIN+ bias, each with its break-even; documented dependency: the load against the gain row's 25 kOhm; requirement: 25 V |
| Regulating setting | 31.6k (C705766), 2.5485 A | 28k (C705756), 2.8762 A | 31.6k (C705766), 2.5485 A |
| SC-37 Wh, lower / nominal / upper (h) | 344.0 (5) / 336.6 (5) / 307.9 (0) | 361.2 (4) / 349.8 (2) / 307.9 (0) | 344.0 (5) / 336.6 (5) / 307.9 (0) |
| Bright day Wh (h) | 431.9 (9) | 473.2 (7) | 431.9 (9) |
| Noon, current / power | -26.6 / -24.6 % | -17.1 / -15.6 % | -26.6 / -24.6 % |
| Parts and board E | none added; R16 to 31.6k | U18 INA250A2PWR, the trip chain of C, R60 28k, R61 7.87k; R16 to 28k | five WSL2512R0700FEA, INA169NA/3K, TPS3701DDCR, TPS3808G33DBVR, seven RT resistors (R65 to R71), three 100n, five 100 nF C0G (the INB filter), C71 to C74 10u 50V, the 50 V bulk moved ahead of the bank; R16 to 31.6k |
| New failure mode | limiting past the fault minimum becomes the fault's hiccup (energy) | as C | a hiccup if the regulation's unprinted values exceed the joint assumptions (energy); the single faults below |
| Depends on a maker's answer | Analog Devices (A7, the fault threshold, its timing), Milliohm (the cold TCR) | Texas Instruments (the rows at its own supply and reference, the stress rows); the coordination on Analog Devices and Milliohm | **none for the bound**; the coordination and the energy on Analog Devices and Milliohm |
| The disturbances (check (c)) | no part added; the entry needs C's correction | **fails** the capability scenario: U18's inputs are rated 40 V, the clamp reaches 45.4 V | every part inside its rating; the backstop holds through M2's CS101 |

With 23.2k the day reads 369.7 / 350.0 / 307.9 Wh and the bright day 534.7 Wh (594.4 Wh with no limit at all). (B)'s
unprinted gain terms together may add 0.384 % before 100 W with the capacitor charge (they print 0.459 % typical, not a
limit); the conduction of its 4.5 mOhm package path, the shunt included, at its own regulation is 0.1853 Wh on SC-37's day
and 0.3111 Wh on the bright day.

## The choice: (C), CONDITIONAL on two named assumptions (SESSION)

R60 to R64, five WSL2512R0700FEA (C2076144) in parallel, 14 mOhm, carry everything entering the stage but the bulk
(ahead of them on PV_P, the CS101 correction), R8, R9 and U18's VIN+ pin. U18 INA169 (SBOS181F) turns their voltage into a
current into R65 16.9k and R66 8.45k (25.35k together, 25.04k to 25.66k with tolerance, drift and aging, beside the
25 kOhm of its gain row), with five 100 nF C0G across R66 (C70 and C75 to C78: the INB filter, 3.960 to 4.496 ms). U19
TPS3701 trips at INB on R66 and watches TRK_VS at INA (R67 110k over R68 9.53k); either output pulls U20 TPS3808G33's MR,
whose RESET holds SWEN low; R70 8.06k from TRK_LDO33 over R71 6.04k set SWEN when released and hold it low with no supply.
The LT8705A's own limit stays as the regulation, coordinated under the trip: RIMON_IN 31.6k (C705766), 2.5485 A nominal.

Why (C): its bound needs no maker's answer; it rests on printed limits at their own conditions plus two assumptions about
one part, each carried past its physical meaning (check (a)). (A)'s four assumptions set the bound itself; (B) rests on
rows printed at another supply, reference or current and on typical-only rows, and its sensor's inputs fail the capability
scenario. The second round called (C) UNCONDITIONAL: that is withdrawn.

## Check (a): normal operation, one error budget

Every term at its end that raises the trip, at the static bound's point (25 V, parts aged):

| Term | Value | Class, source |
|---|---|---|
| U19 TPS3701 INB rising threshold, TJ -40 to 125 C, VDD 1.8 to 36 V | 397 to 403 mV | warranted, SBVS240C p.5 |
| U19 input current at INB, through R66 | +-25 nA | warranted, p.5 |
| U18 transconductance, VSENSE 10 to 150 mV, at V+ = 5 V, VIN+ = 12 V, ROUT = 25 kOhm | 990 to 1010 uA/V | warranted, SBOS181F p.6 |
| its nonlinearity | +-0.1 % | warranted, p.6 |
| its offset referred to the input, at the same point | +-1 mV | warranted, p.6 |
| its output's move from VIN+ = 12 V to 25 V, at VSENSE = 50 mV (CMR 100 dB) | 130 uV | warranted at 50 mV, p.6 |
| its output's move from V+ = 5 V to 25 V, at VSENSE = 50 mV (PSR 10 uV/V) | 200 uV | warranted at 50 mV, p.6 |
| the same move at the trip's own sense voltage (44.502 to 50.169 mV): G_CM x \|VSENSE - 50 mV\| | G_CM 1 %: 1.7 uV | **assumption**, no row |
| the load R65 + R66 against the gain row's 25 kOhm, through the 1 GOhm output impedance | 0.0021 uV | documented dependency (typical row), p.6 |
| R66 8.45k, 0.1 %, 25 ppm/K over 45 K, solder-heat and life | +-(0.5 % + 0.05 Ohm) each | warranted (printed test limits), YAGEO RT V.16 |
| the bank: 1 %, 75 ppm/K from -55 to +155 C; solder-heat and load-life | 14 mOhm; +-(0.5 % + 0.5 mOhm), +-(1.0 % + 0.5 mOhm) | warranted, WSL 30100 pp.1 to 3 |
| R8 and R9 across 25 V, bypassing the bank | 5.78 mW | warranted, YAGEO RT V.16 |
| U18's VIN+ pin, its output current, bypassing the bank | 1.27 mW at 25 V | warranted (from the rows above) |
| U18's VIN+ input bias (10 uA typical, no maximum) | 1 mA: 25 mW at 25 V | **assumption**, no row |
| the bulk's DC leakage, bypassing the bank (it is ahead of it) | 1.24 mW at 25 V | warranted, ZA p.1 (0.01 CV after 2 minutes) |
| the input voltage | at most 25 V | requirement, REQ-016 |

- **The chain together**: the trip's nominal current is 3.3812 A (47.337 mV over the bank's nominal). The trip current at
  which 25 V reaches 100 W, the bypass included, is 3.9987 A: the combined error the setting can tolerate before 100 W is
  **18.26 %** of nominal. The supported bound, every term together (the bank alone 4.39 %), is **10.63 %**: the trip at
  most 3.7408 A at 25 V (50.169 mV), the static bound **93.5521 W**, the margin 7.63 % of nominal, **6.4479 W**. The
  second round's multiplier on the rejection rows (printed 1.0507, applied 1.0240) is withdrawn.
- **The two assumptions** (each alone, the other at its stated value): G_CM reaches 100 W only over 500 % on the static
  bound alone and at **168.8 %** once check (b)'s capacitor charge, the INB filter's held charge and ten typical responses
  are taken from the headroom; the VIN+ bias at 258.9 mA and **22.0 mA**. G_CM at 100 % would be a gain change the size of
  the gain itself; a bias of 10 mA is the pin's absolute maximum, a stress the maker calls damaging (p.4), so past it the
  part is in a fault. Neither is a maker's limit; `clarification/texas-instruments-ina169.txt` asks for the envelope.

**The setting (SESSION; the margin decided by what it must absorb, no percentage).** Round 3 took the least energy cost
for which (i) check (b)'s response allowance covers the response chain's typical sum with every typical-only link at ten
times its typical value at once, and (ii) with that response spent, both assumptions are carried past their meaning: R66
8.25k with RIMON_IN 30k (8.06k carries G_CM only to 7.3 %). Why ten: the largest maximum-to-typical ratio among the timing
rows these makers print for the chain's parts is 1.4. The CS101 correction adds a third condition, M2's immunity, and
searches the bulk's position, R66, RIMON_IN and the INB filter together; the least energy cost that holds all three is
**R66 8.45k (C861590) with RIMON_IN 31.6k (C705766)**, the bulk ahead of the bank and five 100 nF across R66 (the section
"The backstop under CS101" below). Round 3's table, for the record (C70 1 nF only, the regulation at its least
coordinated value):

| R66 | Trip mV (highest) | Bound W | R16, nominal A | SC-37 nominal Wh | Bright Wh | Noon P | Allowance ms | G_CM be | VIN+ bias be mA | |
|---|---|---|---|---|---|---|---|---|---|---|
| 8.06k (C861587) | 52.5549 | 97.9977 | 29.4k, 2.7392 | 345.5 | 457.4 | -19.4 % | 0.820 | 7.3 % | 12.8 | |
| 8.2k (C861589) | 51.6724 | 96.3527 | 30k, 2.6844 | 343.4 | 450.1 | -20.8 % | 3.034 | 63.6 % | 78.3 | |
| 8.25k (C705798) | 51.3645 | 95.7788 | 30k, 2.6844 | 343.4 | 450.1 | -20.8 % | 3.783 | 100.5 % | 101.2 | round 3's choice |
| 8.45k (C861590) | 50.1693 | 93.5508 | 30.9k, 2.6063 | 339.6 | 439.7 | -23.0 % | 6.585 | over 500 % | 190.0 | meets |
| 8.66k (C861591) | 48.9941 | 91.3602 | 31.6k, 2.5485 | 336.6 | 431.9 | -24.6 % | 9.186 | 365.6 % | 277.2 | meets |

The trip in normal operation: its lowest at the hold's voltages is 3.0562 A with the parts aged (3.0468 A at 25 V;
3.1695 A new), against the panel's highest current on SC-37's day at any hold corner, 2.8779 A: it never acts that day.
One bank part carries at most 0.040 W at the highest trip (rated 1 W to 70 C).

**Can a conditional term overturn the solar architecture: no.** Each, past its break-even, is answered by a stocked
setting (the search's costs) or by a part, on the same topology.

## Check (b): startup, shutdown and the fault response

The energy into the stage over any 0.1 s, at most 10 J:

- **The capacitor input energy** of one charge from zero to 25 V, C x Vmax^2 (half stored, half lost in the charging
  path), every capacitor on the entry at its largest: the 50 V bulk 154.4 uF (+20 % and the endurance row's +30 %), C66,
  C71 to C74 and C13 to C15 with C64 at +10 % and no bias derating, 225.83 uF in all: **141.1 mJ**. The bulk is now ahead of
  the sensor; its charge is still energy into the stage at the boundary and is counted here.
- **The source**: REQ-016's window bounds the open circuit (25 V); the current is the panel the window was ruled with,
  its short circuit at 1000 W/m2 and the trace's hottest cell, 70 C, 6.417 A, with the sheet's +6 % power tolerance:
  **6.802 A**, 170.05 W with 25 V (not the generator's 1.1 x 5.68 A).
- **The fault response** (a trip): the stage at the static bound before it, the source's whole power while the chain
  responds, then one full capacitor charge (a deliberate over-count). Before the chain, the **INB filter holds at most
  0.4205 J above the trip**: a first-order filter can hold at most tau x I_trip of charge above the trip before it crosses,
  whatever the waveform (a step, or a slow ramp just over the trip), here the trip's highest (3.7408 A) times its largest
  time constant (4.496 ms) at 25 V. The chain after it prints only typical rows: U18 5 us, U19's INB rising edge 28.1 us
  (10 mV overdrive), U20's MR to RESET 0.15 us, RESET pulling SWEN under 1 us (INFERRED), one switching period at the
  lowest printed frequency 5.88 us (INFERRED: no SWEN timing row): 40.1 us. The window holds its 10 J for a response up
  to **1.087 ms** after the filter's held charge (round 3: 3.78 ms with no filter), 27 times the typical sum; at the
  typical sum it reads 9.9199 J. On a step to the source's whole current the filter crosses after 3.590 ms from zero and
  1.052 ms from the regulation's highest (2.9337 A); those crossings are inside the held-charge bound.
- **Startup**: U20 holds SWEN low at least 180 ms after TRK_LDO33 passes its threshold (SBVS050N p.7, full range), longer
  than the window, so the connection's charge and switching never share a window: at most 0.1465 J.
- **Shutdown and repeated events**: after a trip SWEN stays low at least 180 ms, so one window holds one trip at most;
  each restart goes through the soft start.
- **Repeated source steps with SWEN low**: the capacitors take energy again only after giving it up, to the quiescent
  loads or back into the panel (energy that leaves the stage). Each full swing between the hold's lowest corner and 25 V
  loses at most C x dV^2 = 14.56 mJ inside the stage, so the window holds 3.6 such swings after the trip, its charge and the
  filter's held charge. No document bounds how often a panel's open circuit swings in 0.1 s: CONDITIONAL, bench row 7b.16.

## Check (c): the parts' ratings during the specified disturbances

**The derivation (B6).** TRN-001's port table (DECISION-31) lists J_SOLAR as EXTERNAL, a long outdoor lead; no document
of the tree states its length or routing, so the levels are the approved test plan's for power leads, which do not
depend on them:

- **M2, MIL-STD-461G CS101** on DC input power leads, curve 2 (sources of 28 V or below): 126 dBuV, 2.00 V rms, at the
  EUT's input to the knee (read from Figure CS101-1 at 5 kHz), then the straight line to 96.5 dBuV at 150 kHz; or the
  source set to Figure CS101-2's 80 W into 0.5 Ohm, with Figure CS101-4's 10 uF return capacitor and the LISNs of Figure 6;
- **M3, CS114**: the current induced on the lead at most curve 4's 103 dBuA (141 mA rms; Table VI, ground, Army: curves 3
  and 4);
- **M7**: the discharge at decision 34's level, 8 kV contact and 15 kV air, through CS118's 150 pF and 330 Ohm (Table
  IX's +30 % on the contact current; the air level scaled from it);
- surge and sustained over-voltage: no level is ruled (REQ-016, DECISION-31 section 3), so D4's own 10/1000 us rating
  stays a **capability scenario, labelled**: 33.1 A at an initial junction of 25 C or below, derated to 88.1 % (29.2 A) at
  the hot end's 62.1 C (Littelfuse Figure 3 as drawn, INFERRED from the figure).

**The corrected network.** The 50 V bulk on PV_P ahead of the bank (the CS101 correction); four 10 uF 50 V ceramics, C71
to C74 (the value text and land of C13 and C14), on TRK_VS at RSENSE1's pad, so a fast edge reaches R59 only through C13
to C15's share; nothing in series with CSPIN or CSNIN, which the maker forbids (8705af p.30); the INB filter across R66.
The model (MODELED, lumped): the stage's operating current superposed at the trip's highest, 3.741 A; RSENSE1 at its
highest; the bank at its least (more current on toward R59); the bulk new, after endurance at 200 % of its 20 C ESR, and
after endurance at its -40 C row (0.8 Ohm a can); the ceramics ahead at -10 % times a bias factor 1, 0.5 or 0.25 (C13 and
C14 the same factor), each at most 10 mOhm (SESSION assumption), those behind with none; D4 off below its highest
breakdown, then the straight line to its clamping point.

| Case (worst of the bias factors and bulks) | U5 sense V | D4 A | TRK_VS V | Bank A | U18 V | Bank part mJ |
|---|---|---|---|---|---|---|
| capability, cold end (D4 at its full rating, the bulk aged, -40 C row) | 0.2094 | 28.62 | 43.91 | 32.49 | 0.4746 | 3.5108 |
| capability, hot end (D4 derated, the bulk new) | 0.1441 | 24.79 | 42.64 | 28.66 | 0.4186 | 2.8669 |
| capability, hot end (D4 derated, the bulk aged) | 0.1613 | 25.43 | 42.85 | 29.32 | 0.4283 | 2.8669 |
| M7, discharge 8 kV contact | 0.1322 | 0 | 17.64 | 33.52 | 0.4896 | 0.0001 |
| M7, discharge 15 kV air | 0.1973 | 0 | 17.72 | 59.57 | 0.8701 | 0.0003 |

- **U5's sense differential**: at most **0.2094 V** (the capability scenario, cold end), 0.1973 V at the approved
  discharge, 0.1013 V under CS101 (the IMON_IN loop's branch included) and 0.0609 V under CS114, against 0.3 V (8705af p.2).
  The operating current's own drop is 0.0578 V; the margin, 0.0906 V, would take a further 5.86 A of converter current at
  the event's peak. With two ceramics instead of four the approved 15 kV discharge reads 0.2821 V: four is the least count
  that keeps the margin over the operating drop. The negative differential stays at 0.0533 V or above.
- **Every other part**: TRK_VS 44.25 V against the ceramics' 50 V, U5's VIN 80 V and Q3's 60 V; PV_P 44.74 V against the
  bulk's 50 V (now on PV_P) and U18's 75 V; U18's differential 0.870 V against 2 V; U19's INB 4.218 V (the filter holding a
  discharge's charge to 0.09 mV) and INA 3.528 V against 7 V; FBIN 3.06 V and SHDN 5.77 V against 30 V; D4 carries less
  than the scenario's whole current (at most 29.64 A of 33.1 A); a bulk can 10.6 A at the pulse's peak (no single-pulse row
  is printed; its voltage stays under its rating); one bank part 3.51 mJ over the capability pulse, CONDITIONAL: Vishay
  prints its pulse capability only through an online calculator whose chart it marks illustrative
  (`clarification/vishay-wsl2512.txt`).
- **CS101's ratings**: the input reaches 27.82 V at most, under D4's 28 V stand-off; a bank part dissipates 0.104 W at most
  against 1 W (the bulk's ripple no longer crosses the bank). The bulk's ripple: with the voltage limit at the input (any
  test source) a can carries up to 4.45 times its ripple rating at that frequency (ZA p.2's frequency table, at 4972 Hz);
  with Figure CS101-4's setup as drawn, 2.66 times. The rating is the 10000 h endurance figure at 105 C, not an absolute
  maximum: CONDITIONAL, M2 records the cans' temperature (a larger or a fourth can is the remedy, on the same topology).
- **Beyond the lumped model** (the discharge's first nanoseconds, CS114 at MHz) the board's parasitics decide, a layout
  matter (C71 to C74 at R59's pad, R59's Kelvin taps), judged by M3, M7 and bench row 7b.18 at layer 8. A reversed panel
  conducts through D4 as DECISION-31's note E-N1 records.

## The backstop under CS101 (the closing check's defect, corrected)

**The exposure.** M2's own: MIL-STD-461G CS101 on the DC input power leads, curve 2, its Figure CS101-4 setup (the coupling
transformer in the high lead, the 10 uF across the leads, the LISNs of Figure 6), the kit charging from the panel lead
with the regulation at its highest current. Two setups, each frequency apart: **(S1)** the voltage limit across J_SOLAR,
the test's own controlled quantity whatever the source; **(S2)** the setup as drawn, the source an ideal EMF at the
calibrated power into 0.5 Ohm, the loop closed through the 10 uF, the two LISNs and the power source (stiff, and absent),
capped at the voltage limit. The stage behind the bank: the capacitors at their largest, and the converter, whose input
with VC fixed draws constant power (dI/dV = -I/V), inside its IMON_IN loop, which holds R59's current (that branch divided
by 1 + T; T from A7, RIMON_IN, CIMON_IN, EA2's gm 185 umho and gain, R13, C21, C22, A5's 150 mV/V over R5 and the duty:
typical rows, a documented dependency). The trip acts when the filtered bank current reaches the trip's **lowest** (aged),
so the margin is the trip's lowest less the regulation's highest, at every input voltage.

**What it violates.** M2's line is "no upset of the kit's operation, no reset, no loss of a bearer" (REQ-063;
characterisation under D-04, no claim). Each trip stops the stage's switching for td, at least 180 ms, so solar charging
stops while the test runs: an **upset of the kit's operation** (its charging function). It is not a reset of the kit
(U20's RESET acts on SWEN only) and not a lost bearer. M2's scope and line stay as written.

**Frequency by frequency** (the bank's current, A peak, S1 / S2, then the filtered peak against the margin; y: under it,
the trip does not act; N: it acts):

| f Hz | Failing case (round 3) | (a) alone, its most filter | (b) alone, bulk ahead | Selected: (a) + (b) + margin |
|---|---|---|---|---|
| 30 | 0.105 / 0.105 -> 0.1052 N | 0.105 / 0.105 -> 0.1010 N | 0.023 / 0.023 -> 0.0231 y | 0.023 / 0.023 -> 0.0185 y |
| 61 | 0.214 / 0.214 -> 0.2139 N | 0.214 / 0.214 -> 0.1840 N | 0.047 / 0.047 -> 0.0469 N | 0.047 / 0.047 -> 0.0258 y |
| 124 | 0.435 / 0.435 -> 0.4348 N | 0.435 / 0.435 -> 0.2776 N | 0.095 / 0.095 -> 0.0951 N | 0.095 / 0.095 -> 0.0294 y |
| 252 | 0.882 / 0.882 -> 0.8820 N | 0.882 / 0.882 -> 0.3332 N | 0.191 / 0.191 -> 0.1915 N | 0.192 / 0.192 -> 0.0302 y |
| 513 | 1.776 / 1.776 -> 1.7752 N | 1.776 / 1.776 -> 0.3492 N | 0.372 / 0.372 -> 0.3719 N | 0.373 / 0.373 -> 0.0291 y |
| 972 | 3.223 / 3.223 -> 3.2202 N | 3.223 / 3.223 -> 0.3394 N | 0.567 / 0.567 -> 0.5665 N | 0.570 / 0.570 -> 0.0236 y |
| 2121 | 8.574 / 7.136 -> 8.5443 N | 8.574 / 7.136 -> 0.4155 N | 3.082 / 2.476 -> 3.0719 N | 3.090 / 2.476 -> 0.0585 y |
| 4972 | 19.902 / 3.102 -> 19.5347 N | 19.902 / 3.102 -> 0.4119 N | 6.564 / 1.018 -> 6.4427 N | 6.565 / 1.017 -> 0.0531 y |
| 10110 | 19.284 / 2.649 -> 17.9292 N | 19.284 / 2.649 -> 0.1963 N | 6.427 / 0.854 -> 5.9755 N | 6.427 / 0.854 -> 0.0255 y |
| 38942 | 13.145 / 2.656 -> 7.2064 N | 13.145 / 2.656 -> 0.0347 N | 6.214 / 0.902 -> 3.4064 N | 6.213 / 0.902 -> 0.0064 y |
| 150000 | 4.732 / 2.604 -> 0.7939 N | 4.732 / 2.604 -> 0.0032 y | 4.643 / 1.157 -> 0.7789 N | 4.642 / 1.157 -> 0.0012 y |

Margins: the failing case 0.0335 A (R66 8.25k, RIMON_IN 30k, C70 1 nF); (a) alone 0.0335 A (2 x 100 nF, the most check
(b)'s energy allows there); (b) alone 0.0335 A; the selection **0.1130 A** (R66 8.45k, RIMON_IN 31.6k, 5 x 100 nF, the
bulk ahead of the bank). The script evaluates 121 frequencies from 30 Hz to 150 kHz; the table shows eleven.

- **The failing case, reproduced** (round 3's circuit): the bank carries 0.105 A at 30 Hz rising to 19.97 A at 5337 Hz
  against a margin of 0.0335 A; the trip acts at all 121 frequencies.
- **(a) alone fails at the low end**: the bulk behind the bank puts 0.105 A through it at 30 Hz, three times the margin, and
  a filter slow enough to cut 30 Hz holds more charge above the trip than check (b) allows (its most, 2 x 100 nF, still
  leaves 0.101 A at 30 Hz and 0.421 A at 2625 Hz).
- **(b) alone fails from 46 Hz up**: with the bulk ahead the bank's 30 Hz current falls to 0.0231 A, under the margin, but
  the ceramics and the converter behind it carry 6.56 A at 4972 Hz unfiltered. No capacitance ahead can lower S1 at all,
  because the voltage across J_SOLAR is what the test holds: 2.2 mF added on PV_P leaves S1 at 3.223 A at 1 kHz and lowers
  S2 there from 3.223 A to 1.239 A only.
- **The coordinator's starting estimate, tested**: a single pole at 180 Hz (0.884 ms) on round 3's circuit passes 0.104 A
  at 30 Hz (98.6 % of it) and 0.735 A at its worst frequency, against the margin 0.0335 A. Its crossing time on a full
  step from the regulation's highest, 0.196 ms, is confirmed. But it used the trip's highest less the regulation's,
  0.740 A, as the margin; the trip acts at its lowest, so the low-frequency end decides.
- **The controlling trade-off**: a first-order filter of time constant tau holds at most tau x I_trip of charge above the
  trip before it crosses, whatever the waveform, and that charge comes out of check (b)'s headroom. The ripple it passes,
  at the high end about V x C_behind / tau, must stay under the margin between the regulation's highest and the trip's
  lowest. With the bulk behind the bank C_behind is 199 uF; ahead of it, 44 uF. So the correction is both remedies
  together, with the margin bought with the regulation:
  - the bulk ahead of the bank (no part added);
  - the filter on INB;
  - the setting the search takes with the least energy cost among 154 candidates that hold all three conditions.

  At that cost the filter's size trades two quantities no row bounds: the IMON_IN loop branch's room in the immunity and
  the response's room in check (b). The choice takes the largest of the smaller of the two:
  - 3 x 100 nF: the loop branch 1.28 times, the response 8.19 times;
  - 4 x 100 nF: 1.91 and 5.45 times;
  - **5 x 100 nF: 2.51 and 2.71 times (chosen)**.

**The three conditions, at once:**

| Condition | Result | Margin, and what remains |
|---|---|---|
| (i) no upset under M2 | the filtered peak at most 0.0585 A at 2121 Hz (S1), at the filter's least time constant (3.960 ms) and every capacitor at its largest | against the margin 0.1130 A; the IMON_IN loop's branch (typical rows) may be 2.51 times its model before the margin is spent: CONDITIONAL, M2 reads it |
| (ii) protection under REQ-016's boundary and the 0.1 s window | the filter's held charge at most 0.4205 J; the static bound 93.5521 W with the bulk's printed leakage (1.24 mW) counted as bypassing the bank; the capacitor charge (141.1 mJ, the bulk's included); the chain at ten times typical | the window leaves 1.087 ms for the response (round 3: 3.78 ms); the step crosses after 3.590 ms from zero and 1.052 ms from the regulation's highest, inside the held-charge bound |
| (iii) ratings and behaviour | check (c) re-run on the corrected entry; the sequencing unchanged; the filter's capacitors at INB's 4.22 V at most against their 50 V | as check (c) above |

**What the sensor sees, and what it does not.** It sees everything into TRK_VS: D4, C71 to C74, C66, U18's supply, R14
and R67, and R59 to the converter, C13 to C15 and C64. It does not see the bulk's charge, ripple and leakage, R8 and R9,
U18's VIN+ pin, or TP5. Moving the capacitance ahead hides nothing from the compliance calculation:
- its charge at connection, at most 96.5 mJ (C x V^2 at its largest), is counted at the boundary (J_SOLAR, PV_IN) in check (b);
- the inrush is the panel's own current, 6.802 A at most (a current-limited source, through F2);
- its leakage is in the static bound;
- its CS101 ripple against its rating is check (c)'s CONDITIONAL item;
- its parasitics, the cans' and the bank's inductance (a few nH, about 4.7 mOhm at 150 kHz for 5 nH), are small against
  the stage's impedance over CS101's range, and decide only the fast edges (layout, M7).

**The cost** against round 3: 8.0 / 6.7 / 0.0 Wh on SC-37's day (lower, nominal, upper hold) and 18.2 Wh on the bright
day; the static bound falls to 93.5521 W.

## The supply sequencing (B3): SWEN off by default, on printed rows

R71 6.04k holds SWEN to ground and R70 8.06k feeds it from TRK_LDO33 only, so SWEN is at most 0.4343 x TRK_LDO33 (both at
their worst ends, aged). Below **2.662 V** on TRK_LDO33 SWEN cannot reach its least rising threshold, 1.156 V (8705af
p.4), whatever the ramp, the delays or U20's state; 2.662 V is above every sensing part's least supply (U19 1.8 V, U20
1.7 V; U18 sits on TRK_VS, watched by U19's INA from 4.870 V). Above it U19 and U20 are inside their ranges: U20 holds
RESET at its VOL, 0.4 V at 1 mA (SBVS050N p.6; RESET sinks at most 0.528 mA here), while TRK_LDO33 is under its threshold
(3.024 to 3.116 V; it releases at 3.194 V at most) and for td after; U19's outputs reach U20's MR at 0.25 V at most
against MR's 0.54 V. So SWEN can rise only while the sensing chain is supplied and armed, with no condition on TRK_LDO33's
ramp or sag rate and no use of U20's power-up row. Released, at LDO33's least (3.23 V) SWEN reads 1.364 V against its
highest threshold 1.256 V. The one unprinted figure is SWEN's own pin current: it could enable the stage below 1.80 V
on TRK_LDO33 only by sourcing 107 uA (189 uA with TRK_LDO33 floating), keep it off only by sinking 31 uA, and RESET's VOL
fails to disable it only if the threshold's hysteresis (22 mV typical) reached 0.756 V; the Analog Devices draft asks.
TRK_LDO33 carries at most 338 uA of the arrangement; U18's output at the highest trip, 1.301 V, stays under its
compliance where the chain is armed, 3.67 V.

## The coordination and the energy

The smallest stocked RIMON_IN whose regulation at its highest under the joint assumptions stays at or under C's lowest
trip with its parts aged, at every input voltage, is 30.9k; the CS101 correction takes **31.6k**, one step lower, for M2's
margin: 2.9337 A at 25 V against 3.0468 A. Past the joint assumptions the overlap would be a hiccup (each trip stops the
stage 180 to 420 ms and restarts it through the soft start); the bright day's hours at risk are 09 to 15, 462.4 Wh.

On SC-37's day 344.0 / 336.6 / 307.9 Wh at the lower, nominal and upper hold corners (5 / 5 / 0 h bound) against 369.7 /
350.0 / 307.9 Wh with 23.2k (13.4 Wh less at the nominal hold, 25.7 Wh at the lower corner); on the bright day 431.9 Wh
(9 h bound) against 534.7 Wh (102.8 Wh less); at bright noon the input power falls 24.6 % (the current 26.6 %). The bank's
conduction at the selected regulation's own currents costs 0.5262 Wh on SC-37's day and 0.7978 Wh on the bright day.

## L4-E9's figures this round sets

From L4-E9's power-path output at fnd/l4e9 539dc57c (read only; `inputs/l4e9-power-path-539dc57c-excerpt.json`):

| L4-E9 line | Now | This round |
|---|---|---|
| 86, 109: the input limit | 3.4713 A | the regulation at RIMON_IN 31.6k: 2.5485 A nominal, 2.9318 A at its highest on the hold's corners (44.84 W at the nominal hold, 53.42 W at most there) |
| 86, 109, 113: the 25 V corner | 96.2474 W, 99.8992 W | the backstop's static bound 93.5521 W (CONDITIONAL on G_CM and the VIN+ bias); the regulation's own 25 V corner 73.3436 W |
| 97: the panel's hot short circuit | 6.42 A | 6.802 A with the sheet's power tolerance (still under J_SOLAR's nearest stated 7 A) |
| 99, 105, 115: the entry's protection and the backstop | PENDING | the drafted bank, the 50 V bulk on PV_P ahead of it, D4 and C71 to C74 on TRK_VS, the INB filter and the backstop (drafts, not applied) |
| 119: 93 W out at the window | 4.216 A at 22.06 V | a ceiling, not an expectation: the stage takes 53.42 W in at most at the hold |
| 307: L4-E7's settings, 350 Wh a day | 350 Wh | 344.0 / 336.6 / 307.9 Wh (SC-37) and 431.9 Wh on the bright day |

## The series disconnect: evaluated, not taken (SESSION)

The LM5069 class hot-swap controller prints its current limit (VCL 48.5 / 55 / 61.5 mV) at VIN = 48 V, not at the
panel's 17 to 25 V, and its 12 % spread would push the regulation further down than C's; SWEN already removes the path
from the panel to the pack, and the input capacitors' charge is bounded in check (b). A series FET would cover a shorted
switch of the LT8705A, a single fault layer 8 judges.

## The single faults (assigned to layer 8)

- **Defeat the backstop**: U18's output stuck low or open, or R65 open; R66 shorted; U19's OUTB stuck open; U20's RESET
  stuck open, or its MR stuck high; a short across the sense bank; U5's SWEN input failed active; a capacitor of the INB
  filter shorted (INB held at ground).
- **Remove the supply guard only**: R71 open (the trip still acts through RESET).
- **Stop charging**: U19's OUTA or OUTB stuck low; U20's RESET stuck low; R70 open; U18's output stuck high; the whole
  bank open; TRK_LDO33 lost; a ceramic of C71 to C74 shorted; a capacitor of the INB filter open (less filtering: the trip
  may act under CS101's ripple; the bound is unchanged); a bulk can shorted (PV_P to ground ahead of the bank; F2 above
  the panel's current).
- **Acceptance**: no single fault both defeats the backstop and removes the LT8705A's own limit, and every fault that
  defeats the backstop or its supply guard is found by the commissioning and periodic trip test (7b.15).

## Board E changes (drafted, nothing applied)

`apply_gen_sch_e_backstop.py`, nine edits on the text the hold and input limit drafts leave (it refuses a generator
without them): the bank on PV_P to TRK_VS; the 50 V bulk (C11, C12, C69, EEHZA1H330XP) on PV_P ahead of it; R59 and CSPIN
behind it, nothing in series with CSPIN or CSNIN; U18 with R65 16.9k, R66 8.45k (C861590) and the INB filter, C70 and C75
to C78, five 100 nF NP0 50 V 1206 (C170182); U19 with R67 and R68; U20 with R69; SWEN on TRK_SWEN with R70 8.06k and R71
6.04k (C728595); C66 to C68; C71 to C74 and D4 and R14 on TRK_VS; R16 31.6k (C705766); the declarations. Read back on a
scratch copy; never applied to the tree; R10 untouched.

## Prototype measurements (the exact downstream verification)

- **7b.15** on each built board, the input current at which SWEN falls, at 17.6 V and 25 V, against 3.0468 to 3.7408 A
  at 25 V, at commissioning and at layer 8's interval;
- **7b.16** the response from a current step over the trip to the last switching edge, against 1.087 ms after the
  filter's crossing; with R16 shorted, the energy over every 0.1 s at or under 10 J through a trip, a panel connection and
  the bench supply's curve stepped with SWEN held low, each restart through the soft start;
- **7b.17** the regulation at 31.6k on a bench panel curve does not trip at 25 C and at the cold end;
- **7b.18** R59's differential (Kelvin at U5's pins) under the M7 discharge at J_SOLAR and under a 10/1000 us pulse at
  D4's rating, against 0.3 V;
- **7b.19** SWEN at TRK_LDO33's power-up, sag and loss, against 1.156 V while TRK_LDO33 is under 2.66 V and U20's VOL
  above it;
- **M2, the laboratory validation of CS101** (downstream, characterisation under D-04): the kit charging from a bench
  panel curve at the regulation's highest current; Figure CS101-4's setup on the solar lead; curve 2 or the calibrated
  power at every frequency of 30 Hz to 150 kHz at Table III's rate. Record:
  - the voltage across J_SOLAR;
  - the lead's current (a current probe);
  - SWEN;
  - the stage's input current and charge rate;
  - the bulk cans' case temperature.

  The pass line is M2's own: SWEN never falls and charging never stops (no upset), no reset, no lost bearer. The least
  margin read at the worst frequency (the model puts it near 2121 Hz) is stated beside the model's 0.0545 A.

## The decision (item 5)

**Selected**: (C) at R66 8.45k and RIMON_IN 31.6k, with the corrected entry (the bulk ahead of the bank), the INB filter
(five 100 nF C0G across R66) and SWEN off by default. It is the one arrangement whose bound needs no maker's answer, whose
two assumptions are carried past their physical meaning and whose backstop holds through M2's CS101, at an energy cost of
6.7 Wh a day at the nominal hold against round 3.

| Check | Supported bound | Margin | Remaining assumptions |
|---|---|---|---|
| M2 immunity | the filtered ripple at most 0.0585 A at 2121 Hz | 0.1130 A margin (0.0545 A left) | the IMON_IN loop's typical model (its branch may be 2.51 times it), read at M2 |
| (a) normal operation | 93.5521 W | 6.4479 W (7.63 % of nominal against 18.26 % tolerable) | G_CM (break-even 168.8 %) and the VIN+ bias (22.0 mA) |
| (b) startup, shutdown, fault response | at most 10 J in any 0.1 s for a response up to 1.087 ms after the filter's held charge | 27 times the typical sum | the 0.1 s interpretation (layer 8), the typical rows (7b.16), the panel's swing rate with SWEN low (3.6 swings) |
| (c) the disturbances | every part inside its rating; U5's sense differential at most 0.2094 V | 0.0906 V (5.86 A of further converter current) | the lumped model (layout, M3, M7, 7b.18), the bulk's heating under CS101 (M2), the bank's pulse capability in the capability scenario (Vishay) |

Drafted: the board E edits and four clarification texts. Implemented: nothing in the tree. **L4-E7R's architecture
criterion: MET, CONDITIONAL on the named items**, none of which can overturn the architecture: each resolves by a stocked
setting or a part on the same topology. If the coordinator's closing check finds otherwise, the engineering alternative is
the next stocked RIMON_IN for M2's margin and the next R66 for (a) and (b) (the search's costs), and a larger or added
bulk can for (c)'s heating, before any change of arrangement.

## The clarification drafts

The texts are for the owner to send; the session contacts no one, and no answer moves C's bound to or past 100 W.
- `clarification/texas-instruments-ina169.txt`: the warranted error envelope at V+ = VIN+ of 9 V to 25 V and the trip's
  sense voltage, the VIN+ current and the output past 150 mV (retiring both assumptions);
- `analog-devices-lt8705a.txt`: the coordination's and energy's rows and SWEN's input current, falling threshold and delay;
- `milliohm-hojlr2512.txt`: the cold TCR;
- `vishay-wsl2512.txt`: the bank's pulse capability (the capability scenario only).

## The checks, and what changed

| Item of `checks/check-l4e7r-3.md` (the coordinator's closing check) | Change |
|---|---|
| The backstop trips under M2's CS101 (the one material defect) | M2's exposure modelled through Figure CS101-4's setup and the voltage limit, over 30 Hz to 150 kHz, with the converter in its IMON_IN loop and every tolerance; the failing case reproduced and kept (it trips at all 121 frequencies); (a) alone and (b) alone shown failing, each with where; the correction: the bulk ahead of the bank, five 100 nF C0G across R66 and RIMON_IN one step lower (31.6k), R66 8.45k: no trip at the regulation's highest at any frequency in either setup; check (b) recomputed with the filter's held charge (1.087 ms left); check (c) re-run on the corrected entry; M2's laboratory procedure stated downstream |
| The coordinator's estimate (a corner near 180 Hz, about 0.2 ms) | tested: the crossing time is confirmed; the corner is refuted, because the trip acts at its lowest, which sits 0.0335 A over the regulation at round 3's setting |

| Item of `checks/astra-check-l4e7r-2.md` | Change |
|---|---|
| B1/B5, UNCONDITIONAL not justified | Withdrawn: (C) is CONDITIONAL on two named assumptions (G_CM, the VIN+ bias) with their break-evens; one error budget for the whole chain (check (a)); the absolute maximum is no longer a current ceiling; the margin chosen against what it must absorb, the cost of each step printed; the Texas Instruments draft asks the warranted envelope |
| B2, the dynamic bound | The capacitor input energy C x Vmax^2 with C66, the four new ceramics and the bulk's +30 % (141.1 mJ); the source current from REQ-016 and the panel (6.802 A); repeated source steps bounded by their count's break-even; the 0.1 s window an interpretation for layer 8, supported by the parts' energies; 7b.16 revised |
| B3, sequencing | SWEN off by default: R71 to ground, R70 from TRK_LDO33, so SWEN cannot reach its threshold below 2.662 V, above every sensing part's least supply; no ramp, sag or power-up row used; SWEN's pin current the one unprinted figure, with its break-even |
| B6, the disturbance | Derived from TRN-001's port table and the approved test plan (CS101, CS114, the M7 discharge); D4's pulse kept as a labelled capability scenario, derated at the hot end; the operating current superposed; D4's current apart from the bank's; the bank's pulse capability CONDITIONAL; the corrected network keeps U5 at most 0.2094 V; no series resistor at CSPIN or CSNIN (8705af p.30) |
| Minors | The multiplier withdrawn (no 1.0507 or 1.0240); "it releases at 3.194 V at most"; R65 + R66 described as 25.35k with its range, beside the gain row's 25 kOhm; the bank's conduction at the selected regulation's own currents |

The first check, `checks/astra-check-l4e7r-1.md`, and the second round's changes, kept for the record (superseded where the
tables above differ):

| Item of `checks/astra-check-l4e7r-1.md` | Change |
|---|---|
| B1, the margin | No common multiplier: each term is a printed limit at its own condition (the table above); a term with no printed limit is CONDITIONAL and named ((B)'s list), never multiplied; U18's VIN+ current is carried at its absolute maximum, classed as such |
| B5, the comparison | (C) replaces the old (C), a scenario: a sense bank read by an INA169 whose rows cover the operating condition, a TPS3701 and a TPS3808; its bound rests on printed limits only; chosen on that evidence |
| B3, supply sequencing | A TPS3808 supervisor on TRK_LDO33 holds the stage off whenever the sensing chain is unsupplied, on its printed rows; the LDO33 lockout row of 8705af is no longer used |
| B2, dynamics | The rising INB edge (28.1 us typical); no capacitor on SWEN or on an output (U20's own 180 ms off-time, warranted); the sequence, the capacitors' 45.7 mJ and the 0.1 s basis bounded; bench row 7b.16 with its 0.867 ms tolerance |
| B4, coordination | One basis at both corners (C's lowest with its parts aged against the regulation's highest under the joint assumptions): 29.4k; the bright-day exposure stated |
| B6, the surge | The disturbance derived from TRN-001 and D4's rating; D4 and a 50 V bulk behind the bank; every part on the entry against 45.4 V; R59's share MODELED |
| Minors | The INA250's 4.5 mOhm is the package total: 0.1855 Wh; the noon reductions printed as current and power (A 24.6 %, B at 26.1k 10.06 %); "the smallest stocked RIMON_IN"; the single faults assigned to layer 8 with an acceptance |
