# L4-E7R: the control decision for REQ-016's 100 W (layer 4, MESHSAT-1357)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured. The owner's instruction of 1 October
2026: establish whether the proposed control supports REQ-016's retained limit, "at most 100 W into the stage", across the
permitted operating range, and if it does not do so on warranted evidence, choose a defensible approach. His decision
process of 2 October 2026 shapes the third round: three separate checks with their own results, one error budget for the
whole limiting chain, a margin justified by what it must absorb, the circuit corrections, one coherent candidate and a
decision. It follows the targeted recheck `checks/astra-check-l4e7r-2.md` (NOT YET) and carries the **CS101 correction**
after the coordinator's closing check `checks/check-l4e7r-3.md` (not accepted on one defect: the backstop tripped under
TEST-PLAN M2's CS101) and the owner's CS101 instruction of the same day, the **panel lead's surge and sustained
over-voltage derived** for REQ-016 (the coordinator's surge round, the findings ledger's item 1) and the **solar-fault
remedies** (the owner's amendment of 2 October 2026, item 3), with **the guard already on** bounded after the consolidation
review's B6 (`v2/docs/records/l4close/checks/astra-check-l4close-1.md`); the last section maps each item to its change.
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

**The derivation (B6).** TRN-001's port table (DECISION-31) lists J_SOLAR as EXTERNAL, a long outdoor lead; the records
give a 5 m lead (a1solar's array record, ESTIMATE; the next section derives the panel lead's own disturbances), and
the approved test plan's levels for power leads do not depend on its length:

- **M2, MIL-STD-461G CS101** on DC input power leads, curve 2 (sources of 28 V or below): 126 dBuV, 2.00 V rms, at the
  EUT's input to the knee (read from Figure CS101-1 at 5 kHz), then the straight line to 96.5 dBuV at 150 kHz; or the
  source set to Figure CS101-2's 80 W into 0.5 Ohm, with Figure CS101-4's 10 uF return capacitor and the LISNs of Figure 6;
- **M3, CS114**: the current induced on the lead at most curve 4's 103 dBuA (141 mA rms; Table VI, ground, Army: curves 3
  and 4);
- **M7**: the discharge at decision 34's level, 8 kV contact and 15 kV air, through CS118's 150 pF and 330 Ohm (Table
  IX's +30 % on the contact current; the air level scaled from it);
- surge and sustained over-voltage on the panel lead: derived in "The panel lead's surge and sustained over-voltage" below
  (MIL-STD-461G CS116 and CS115, the row REQ-063 commits to, and the sustained sources); D4's own 10/1000 us rating stays
  here as a **capability scenario, labelled**, the entry's margin beyond that derived basis: 33.1 A at an initial junction
  of 25 C or below, derated to 88.1 % (29.2 A) at the hot end's 62.1 C (Littelfuse Figure 3 as drawn, INFERRED from the
  figure).

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

## The panel lead's surge and sustained over-voltage, derived (REQ-016; R-156)

REQ-016's acceptance gives layer 4 the derivation (the disturbance, its source impedance or current, its duration and the
limit) and layer 8 the judgement under TRN-001. It also states the pass criterion: a disturbance passes only when **D4's
clamping voltage at that disturbance's current, with the part's tolerance, is at or below the lowest limit on PV_P**. This
section answers the findings ledger's item 1 (L4-E7R's checks 1.6 and 2.4; the collaborator's B6 R5: D4's own rating "a
component-capability test, not a derivation of the panel-entry disturbance"). Section 10 of the .out prints every figure
under THE PANEL LEAD'S DISTURBANCES, DERIVED.

**The exposure.** J_SOLAR is EXTERNAL in TRN-001's port table, a long outdoor lead by definition: PV_IN on pin 1 and the
return on pin 2, which is board E's GND (DECISION-31). The records give the lead: a1solar's **5 m one way of 4 mm2 copper**
(`array_calc.py`, ESTIMATE), **0.0465 Ohm in loop** (the replay's own figure). It is unshielded and laid on the ground from
the panel to the case (SESSION reading: a panel's own leads and an extension of their class carry no shield). There is no
earth bond: the case is plastic and no board has a chassis net (GROUNDING-AND-SHIELDS.md). So the kit floats, a
common-mode transient on the lead closes only through stray capacitance, and the high side lead against its return, through
the entry, is the path that loads D4. The lead's quarter wave is 15.0 MHz in free space (half wave 30.0 MHz), lower on soil:
inside CS116's flat band, so it is added to the test frequencies as an installation resonance (461G 5.14.2).

**The basis (SESSION: the reading of what the requirements commit to).** REQ-063 commits the kit's EMC characterisation to
MIL-STD-461G (11 December 2015) and the "Ground, Army" row of its Table V (held; transcribed in
`v2/vendor/standards/mil-std-461g-requirement-matrix.md` from the same file). That row marks:
- CS116 **A** (5.14): damped sinusoids from 10 kHz to 100 MHz on every interconnecting cable, power cables included, and on
  each individual high side power lead;
- CS115 **A** (5.13): an impulse on every interconnecting cable;
- CS117 **S** (5.15): lightning induced, for the procuring activity to specify.

TEST-PLAN.md runs M1 to M5, and no row runs CS115, CS116 or CS117. The derivation takes **CS116 and CS115** as the panel
lead's surge:
1. they are the transients of the one edition and row the requirements commit to;
2. the standard's appendix says that "for most equipment, testing with some combination of CS116 and CS115 may provide
   sufficient coverage to address the environment for nearby lightning called out in MIL-STD-464" (A.5.15), which is the
   exposure an outdoor lead adds;
3. IEC 61000-4-5 is neither held in this tree nor freely published, and the envelope's surge row (decision 34) and CHO-003
   decline to constrain the long leads to it;
4. CS117 is not taken: its levels "were derived from general and civil aviation experience" for aircraft equipment
   (A.5.15), it applies to safety-critical equipment (5.15.1), and the row leaves it to the procuring activity.

**Not covered**, a residual for layer 8 and the register: a direct strike, or one nearer than MIL-STD-464's nearby
lightning (CS117 covers neither, and CS116 with CS115 only "may"). The kit's posture there is REQ-041's mast-down alarm.

**The disturbances.**

| | Disturbance | Source and waveform | Duration |
|---|---|---|---|
| D1 | CS116 on PV_IN alone and on the J_SOLAR cable (461G 5.14, Figures CS116-1 and CS116-2) | each pulse e^(-pi f t / Q) sin(2 pi f t), Q 15 +- 5 (10 and 20 both run), at 0.01, 0.1, 1, 10, 30 and 100 MHz and the lead's 15.0 MHz; Ip from Figure CS116-2 as drawn (INFERRED from the figure): 0.1 A at 10 kHz rising 20 dB a decade to 10 A at 1 MHz, flat to 30 MHz, 3 A at 100 MHz. A generator of at most 100 Ohm through the injection probe; the current is the test's controlled quantity ("Reduce the signal, if necessary, to produce the required current", 5.14.3.4c(3)), so the port sees a current source of Ip | one pulse every 1 to 2 s for five minutes |
| D2 | CS115 on the J_SOLAR cable (461G 5.13, Figure CS115-1) | 5 A, 30 ns at least, edges at most 2 ns; a 50 Ohm charged-line generator through the probe, set at least to the calibration's drive (500 V across the fixture's 100 Ohm loop, A.5.13); the cable's peak current is recorded, not limited | 30 Hz for one minute |
| D3 | the panel's own cold open circuit | REQ-016's window, 25 V at most at -20 C, current-limited (L4-E13's check against D4's standoff holds below 8574 W/m2) | held for hours |
| D4 | a stiff source on the port by mistake (a vehicle or shore lead wired to the panel's receptacle) | the kit's declared source range, 9 to 36 V (V2-SPEC line 21), through the lead's 0.0465 Ohm loop and F2 (10 A) | held |
| D5 | a reversed panel (DECISION-31, note E-N1) | the panel's short-circuit current, 6.802 A (check (b)'s, with the sheet's power tolerance), forward through D4 | held |

**D1, frequency by frequency.** The bound puts the disturbance's whole current in D4 (REQ-016's criterion) and in R59 and
the bank on top of the operating current, 3.7408 A, with no capacitor credited. The loaded network is check (c)'s corrected
entry (MODELED, lumped, to 1 MHz; above it the board's parasitics decide). It is run from two starts: operating at the
hold, and open at 25 V at the cold end with the stage off. Each start runs each bulk (the cold end's aged -40 C row and the
new 20 C row), each bias factor, both polarities and both Q ends. The trip filter's excursion is bounded by 2 x Ip / (pi f)
/ tau, the first half cycle's charge over the filter's least time constant (3.960 ms).

| f MHz | Ip A | D4 at Ip, 25 C / hot end | U5 bound | U18 bound | U5, loaded | U18, loaded | TRK_VS, loaded | PV_P, loaded | D4, loaded | trip filter | D4 energy bound |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.01 | 0.10 | 34.43 / 35.71 V | 0.0593 V | 0.0561 V | 0.0582 V | 0.0555 V | 25.05 V | 25.05 V | 0 A | 0.00161 A | 2.27 mJ (0.13 % of its scaled rating) |
| 0.1 | 1.00 | 34.73 / 36.01 V | 0.0732 V | 0.0692 V | 0.0648 V | 0.0672 V | 25.10 V | 25.11 V | 0 A | 0.00161 A | 2.29 mJ (0.41 %) |
| 1 | 10.00 | 37.72 / 39.00 V | 0.2123 V | 0.2007 V | 0.1238 V | 0.1860 V | 25.16 V | 25.24 V | 0 A | 0.00161 A | 2.48 mJ (1.42 %) |
| 10 | 10.00 | 37.72 / 39.00 V | 0.2123 V | 0.2007 V | (layout) | | | | | 0.00016 A | 0.25 mJ (0.45 %) |
| 14.9896 | 10.00 | 37.72 / 39.00 V | 0.2123 V | 0.2007 V | (layout) | | | | | 0.00011 A | 0.17 mJ (0.37 %) |
| 30 | 10.00 | 37.72 / 39.00 V | 0.2123 V | 0.2007 V | (layout) | | | | | 0.00005 A | 0.08 mJ (0.26 %) |
| 100 | 3.00 | 35.40 / 36.67 V | 0.1041 V | 0.0985 V | (layout) | | | | | 0.00000 A | 0.01 mJ (0.04 %) |

- D4 at Ip: the highest part (34.40 V breakdown, the printed slope to 45.4 V at 33.1 A, INFERRED straight line), at 25 C
  and at the hot end's 62.1 C with the sheet's typical coefficient, 0.1 %/C. The worst is **39.00 V**, under the drafted
  entry's 50 V parts and over the drawn C11 and C12's 35 V.
- The ratings: U5's 0.3 V sense differential, U18's 2 V differential, and U18's 75 V common mode and supply.
- The trip filter's excursion stays under the immunity margin, 0.1130 A.
- D4's energy: the bound with the whole current in D4, against the 10/1000 us row's energy (VC x IPP over the shape's
  integral) scaled by the square root of the event's duration (INFERRED: the junction heats adiabatically).
- In the loaded network D4 carries nothing: the entry's capacitors take the pulse, and TRK_VS peaks at 25.16 V, under D4's
  least breakdown at the cold end, **29.70 V** (the sheet's 31.10 V moved by its typical coefficient to -20 C; L4-E13's
  figure). U5's VIN sees at most the TRK_VS figure, against 80 V.

**D2.** D4 at 5 A reads 36.06 V at 25 C and 37.34 V at the hot end. The bound reads U5 0.1350 V and U18 0.1277 V; the
loaded network reads U5 0.0766 V, TRK_VS 25.02 V, PV_P 25.08 V and D4 0 A. The pulse's charge is 0.160 uC, the trip filter's
excursion at most 0.000081 A, and D4's energy with the whole pulse in it 0.0060 mJ. The standard does not limit the loop
current the test drives. U5's rating is reached at **15.7 A** with the whole current through R59 (the bound) and at 64 A in
the loaded network; D4's clamp reaches the drafted entry's 50 V at 43.1 A.

**D4, with the drafted SMCJ28A.** A stiff 36 V source drives the lead's loop into the clamp (INFERRED straight line from
each breakdown at the printed slope). D4's continuous capability on the board, from TJ 150 C and RthJA 75 C/W (typical, 8 x
8 mm pads), is **1.17 W** at the hot end's air and 2.27 W at the cold end's; the sheet's 6.5 W is on an infinite heat sink.

| D4 part and temperature | Breakdown | Current | Power |
|---|---|---|---|
| the least part at the cold end | 29.70 V | 16.63 A | 585.8 W |
| the least part at 25 C | 31.10 V | 12.94 A | 457.9 W |
| the highest part at 25 C | 34.40 V | 4.22 A | 151.2 W |
| the least part at the junction's maximum | 34.99 V | 2.67 A | 95.9 W |

D4 conducts amps at any junction temperature it can reach, two orders of magnitude over its rating. The sheet's typical
failure mode is a short, which F2 then clears. Every other part of the drafted entry is rated above 36 V: the bulk and C71
to C74 at 50 V, U18 at 75 V, U5 at 80 V and Q3 at 60 V. As drawn, C11 and C12 are 35 V, under it. The largest sustained
source the drafted entry holds is D4's least breakdown at the cold end, 29.70 V; below it D4 carries less than its 1 mA
test current.

**The TVS-only change for D4, evaluated and not taken** (superseded by "The solar-fault remedies" below), read from the held
series (Littelfuse SMCJ p.2). The least row that stands off 36
V and does not break down at the cold end is **SMCJ36A**: VR 36.0 V, VBR 40.00 to 44.20 V (38.20 V at the cold end), VC
58.1 V at 25.9 A.
- **Alone it does not hold the derived set on the drafted entry.** Under REQ-016's criterion, D1's 10 A plateau puts its
  clamp at 49.57 V at 25 C and **51.21 V** at the hot end (typical coefficient), against the 50 V parts. Those parts are
  reached at 10.81 A (25 C) and 7.75 A (hot end), and Q3's 60 V at 29.4 A.
- **So the change that holds every derived disturbance is SMCJ36A with the entry's 50 V parts at the 63 V class.** The
  bulk C11, C12 and C69 go to EEHZA1J220XP: 22 uF 63 V in the same 6.3 x 7.7 mm D8 land, ESR 80 mOhm against 40 (ZA p.2).
  That takes the bulk ahead of the bank from 99 uF to 66 uF and so re-opens the CS101 correction, which is re-run with it.
  C71 to C74 go to 63 V or more (no ceramic's sheet is held).
- With the change, a 36 V source runs the stage. Its input is then the regulation's 105.73 W to the trip's 135.26 W at 36
  V, outside REQ-016's window: a single fault for layer 8.
- The alternative that also closes D5 is an input over-voltage and reverse disconnect ahead of PV_P (a series FET with its
  controller): more parts, and no sheet for one is held.

It was carried as a register row, not drafted; the owner's amendment of the same day asked for a selected remedy instead,
which the section below gives.

**D5.** D4's forward path carries 6.802 A, held. On the board D4 can dissipate 1.17 W at the hot end, so it holds only
below a forward drop of 0.172 V, which no silicon junction has at that current (INFERRED; the sheet prints the forward drop
at 100 A only). It is NOT MET as DECISION-31 recorded (E-N1, board E's owner); the keyed receptacle is the barrier against
it.

**The verdicts**, each against REQ-016's criterion on the drafted entry (50 V); as drawn, the lowest limit on PV_P is C11
and C12 at 35 V:

| | Disturbance | D4 at its current | Drafted entry | As drawn |
|---|---|---|---|---|
| D1 | CS116, PV_IN and the cable | 39.00 V (10 A, hot end); D4 off in the loaded network | **MEETS** | NOT MET (39.00 > 35 V) |
| D2 | CS115, the cable | 37.34 V (5 A, hot end); D4 off in the loaded network | **CONDITIONAL**: the loop current under 15.7 A (U5's bound) | NOT MET (37.34 > 35 V) |
| D3 | the panel's cold open circuit | 25 V, under D4's 28 V standoff | **MEETS** (CONDITIONAL on PANEL-ACC) | MEETS |
| D4 | a 36 V source on the port | D4 conducts 2.7 to 16.6 A | **NOT MET** on the drafted entry: remedied below (the over-voltage cut-off) | NOT MET |
| D5 | a reversed panel (E-N1) | D4 forward, 6.802 A held | **NOT MET** on the drafted entry: remedied below (the return switch) | NOT MET |

**For L4-E9's register** (R-156 and its companions; the register is L4-E9's to write):
- (a) R-156's input is this derivation: D1 and D3 MEET, D2 is CONDITIONAL on the recorded loop current, D4 and D5 are NOT
  MET. R-156's text names the INA250's 40 V; the drafted U18 is the INA169 (75 V).
- (b) A TEST row owed at layer 8: CS116 on PV_IN alone and on the J_SOLAR cable at the six frequencies and the lead's 15.0
  MHz, and CS115 on the cable, recording the cable's peak current. TEST-PLAN runs M1 to M5 only, though the row REQ-063
  commits to marks both A.
- (c) The remedies for D4 and D5: "The solar-fault remedies" below.
- (d) The residual beyond the basis: a direct or nearer strike. With the remedies the entry's margin there is the port
  clamp's own rating (D4's without them, check (c)'s capability rows).

## The solar-fault remedies (the owner's amendment of 2 October 2026, item 3)

The owner's words: "The 36 V source and reversed-panel findings are open engineering defects while their remedies are still
being selected. Give each a selected remedy, its circuit changes, and a bounded analysis against the approved fault exposure and
component ratings. Check affected interfaces and calculations, including interactions with the selected charger and backstop.
Include both remedies and their evidence in the consolidated candidate. Preserve the approved normal solar-input window; fault
protection does not extend the permitted operating range." The two defects are D4 and D5 of the derivation above (L4-E9's D-10
and D-11, R-173). Section 10 of the .out prints every figure under THE SOLAR-FAULT REMEDIES.

**The comparison, three implementations, each on its held sheet:**

| | Implementation | What the sheets say | Verdict |
|---|---|---|---|
| (1) | The TPS48110-Q1 alone driving back-to-back FETs (SLUSEE5E: "Drives external back-to-back N-channel MOSFETs") | TI draws it (Figure 9-14) with VS, CS+ and ISCP on the input, rated -1 V to GND (6.1): a reversed panel takes them to -25 V. Rearranged (VS behind a diode, the sense behind the pair), the reversal lands on SRC, rated -30 V (6.1; 8.3.7 prints that state). The reversed panel's -25 V fits with 5 V to spare, but a reversed connection's ring is bounded only by the input clamp. That clamp must stand off 36 V both ways, so it breaks down no lower than -42.4 V at the cold end. The diode's drop (at most 0.715 V, no minimum printed) also enters the cut-off's reference, inside a room of 1.88 V | not taken |
| (2) | The LM74700-Q1 ideal diode ahead of the TPS48110-Q1 (the vehicle entry's pair, L4-E9's suggestion) | Its reverse comparator (V(AK REV) -17 to -2 mV) blocks every reverse current. CS116's negative lobes then find only the input clamp, and CATHODE to ANODE (75 V) carries the clamp plus up to 25 V held behind it. With the SMCJ36CA at 10 A that is 74.57 V at 25 C and **76.21 V at the hot end**; with the SMCJ40CA, 82.53 V. It also rectifies CS101's ripple wherever the input falls faster than the stage drains the 226 uF behind it: above about 733 Hz at the regulation's highest current, inside the 2 to 5 kHz band where the accepted M2 immunity is decided | not taken |
| (3) | **Selected (SESSION)**: one remedy for each fault, from parts already in the design | For D4, the TPS48110-Q1 over-voltage cut-off on the high side, in TI's own topology with the vehicle entry's network (L4-E11) and one CSD19532Q5B. For D5, a CSD19532Q5B in the panel's return, its gate from the input through a divider and a BZT52C12 clamp: it blocks a reversal with its 100 V rating and no controller. The path is linear when on, and no control acts on a reverse current | **selected** |

**The cut-off's band decides the clamp D4.** The band must meet three conditions:
- it sits over CS101's peak at the input, 27.82 V, so M2 never trips it;
- it sits under D4's least breakdown at the cold end, so a sustained source never reaches the clamp;
- it falls back over 25 V, so a panel inside the window is never locked out after a cut.

The comparator prints OV at 1.16 / 1.18 / 1.20 V rising and 1.10 / 1.11 / 1.13 V falling, with the pin's leakage up to 300
nA either way through the top resistor. The divider is built from stocked YAGEO RT 0.1 % 25 ppm/K parts, aged by their printed
load-life and solder-heat limits (the record's convention for a protection threshold).

- **With the drafted SMCJ28A (29.70 V at the cold end) the band does not fit.** New parts leave 0.275 V on the worst side
  (L4-E9's "about 0.4 V each side" less the leakage and the drift); aged parts leave **-0.282 V**: NOT MET.
- So D4 becomes the next held row, **SMCJ30A**: VR 30.0 V, VBR 33.30 to 36.80 V (31.80 V at the cold end), VC 48.4 V at 31.0 A.
- The divider is **R98 90.9k + R99 95.3k over R100 7.68k** (C728600, C861605, C375517). Aged, the cut-off rises at **28.55 to
  31.06 V** and falls back at **27.07 to 29.26 V** (29.11 to 30.47 V rising when new). That leaves 0.731 V over CS101's peak,
  0.737 V under the clamp and 2.07 V over 25 V on the fall.
- Under REQ-016's criterion the SMCJ30A clamps D1's 10 A plateau at **41.91 V** at the hot end and D2's 5 A at 40.04 V, under the
  drafted entry's 50 V parts. It stands off CS101's peak by 2.18 V, where the SMCJ28A did by 0.18 V.

**The circuit changes** (`apply_gen_sch_e_solar_guard.py`, drafted, never applied; it applies after this record's hold, input
limit and backstop drafts, L4-E9's hot swap and L4-E11's entry draft, and refuses a generator without them):
- J_SOLAR.2 becomes **PV_RTN**, and F2 feeds **PV_F**.
- **D11** SMCJ40CA (C80273, the vehicle entry's D10 part) across PV_F and PV_RTN at the connector; the port bank **C131**,
  **C132**, **C135** and **C136**, four Samsung CL32B225KCJSNNE (2.2 uF 100 V X7R 1210, LCSC code owed), on PV_F (one 1 uF
  before B6; two 10 uF in round 1).
- **U21** TPS48110AQDGXRQ1 (C17556513). **R87** 4.5 mOhm (C2985708) from PV_F to PV_SNS and **Q12** CSD19532Q5B (C473333) from
  PV_SNS to PV_P.
- U21's network is L4-E11's vehicle-entry network except the OV divider, R97 and C126:
  - RSET R88 100R 0.1 %, and RISCP R89 3.01k with C126 **330 pF** C0G 100 V (1 nF before B6);
  - the gate slew R90 36.5k, R91 10R and C127 10 nF C0G 100 V (C184799), and CBST C128 1 uF;
  - CTMR C129 22 nF C0G (C97929) with RIWRN R92 39.7k 0.1 % (C861872);
  - the VS filter R93 100R and C130 100 nF 100 V;
  - UVLO R94 59.0k over R95 10.0k, and INP R96 100k over R97 **28.0k** (39k before B6; 30.0k in round 1), R97 at 0.1 % 25 ppm/K (YAGEO RT0603BRD0728KL, code owed; round 4, L6P-F04: the draft had written 1 % while this record's divider is taken at 0.1 %);
  - the OV divider R98, R99 and R100 above.
- **Q13** CSD19532Q5B (C473333) from PV_RTN to GND. Its gate PV_RG comes from PV_F through **R101** 100k and goes to GND through
  **R102** 100k, with **D12** BZT52C12-7-F (C124196) from gate to source.
- **C133** and **C134** on PV_P beside the bulk, and C71 to C74 on TRK_VS (the backstop draft's, edited here), all Samsung
  CL32B106KBJNNNE (10 uF 50 V X7R 1210, LCSC code owed): the part whose DC-bias curve the record bounds (B6 round 2).
- **D4** becomes the SMCJ30A; its LCSC code is owed (no catalogue reading is filed).
- PV_P's declaration is now switched by U21 through PV_UVLO; PV_F and PV_SNS are segments of PV_P, and PV_RTN returns PV_P.

Placement on board E: at J_SOLAR, ahead of the bulk, the sense bank and D4; Q13 in the return pin's copper. Owed with it: U21's
DGX-19 land (as L4-E11's E11-01), the nodes, the regeneration and its gates. Read back here on a scratch copy after the five
drafts: 8 edits, every check yes (B6's parts included), R10 untouched.

**The bounded analysis** (the drafted entry with the block and D4 SMCJ30A, each against the parts' printed ratings):

| Exposure | Result | Verdict |
|---|---|---|
| **D4: a stiff 36 V source** through the 0.0465 Ohm lead, **connected cold** (the block off) | The block never turns on. The gate cannot rise before BST charges, at least 50.0 ms (1 uF -10 % to 7.0 V at 126 uA), while the OV pin follows the input at once. The cut-off's highest, 31.06 V, is 4.94 V under the source. Ratings: Q12 holds 36 V of 100 V; U21's VS 36 V of 80 V, EN/UVLO 5.31 V of 15 V, INP 8.00 V of 20 V; D11 sits under its 40 V standoff. The connection's ring (MODELED, any source loop from 0.30 uH, below): PV_F at most 84.6 V, its slew 56.1 V/us of 60, INP 18.54 V (the worst of both fault positions, round 5) and EN/UVLO 10.97 V of 20 V, D11 at most 16.2 mJ; Q13's body diode carries the ring, at most 173.4 A. D4 and the bulk see nothing | MEETS the absolute ratings; **NOT MET** on the 10 % margin lines at a connector fault near 0.30 uH (round 5: no lead resistance credited there; PV_F's slew 56.1 V/us against 54, INP 18.54 V against 18; the margins hold from 0.53 uH; with the lead's resistance credited, round 2's case, 74.4 V, 45.7 V/us and 16.30 V) |
| **D5: a reversed panel** (6.802 A short circuit with tolerance, 25 V open circuit) | Q13 is off and its body diode reverse biased: no current. It holds 25 V of 100 V, and a reversed connection's ring at most D11's 64.5 V. The high side's pins stay within 1 V of GND while Q13 leaks under 32.1 uA (the dividers' conductance), against 1 uA printed at 80 V and 25 C; on a fast ring the port bank holds them within 0.007 V. D4 and the stage see no reversal | **MEETS**, CONDITIONAL on Q13's leakage above 25 C (no row; 32 times the printed one) |
| **CS116 and CS115, the block on** | The short-circuit trip's sense, filtered by RISCP x CSCP (330 pF, at its shortest), reaches at most 7.15 A against its least 10.36 A. The overcurrent timer reaches 0.037 V against 1.112 V. The input reaches at most 25.59 V against the cut-off's least 28.55 V. Q12 and Q13 carry at most 13.74 A against 400 A. D4 (SMCJ30A) at the disturbance's current reads 41.91 V, under 50 V, and stays off in the loaded network. U5, with CS116's whole 10 A on the trip's highest current (the conservative screen): 0.2123 V of 0.3 V. CS115's 5 A is the generator's calibration level, not a bound on the cable's current: U5 reads 0.1350 V at 5 A, and reaches 0.3 V only 15.680 A over the operating current | **MEETS** for CS116; CS115 **CONDITIONAL** on R-174 (the cable's recorded loop current under 15.68 A, or U5's differential measured under 0.3 V) |
| **CS116 and CS115, the block off** (night, after a cut) | D11 clamps the port at 57.53 V at 10 A at the hot end (54.23 V at 5 A), which Q12 holds against 100 V and U21's VS against 80 V (EN/UVLO 8.48 V, INP 12.78 V). D11 takes at most 3.7 mJ a pulse. The port bank holds PV_F within 0.007 V of GND against Q13's 918 pF | **MEETS** |
| **A stiff 36 V source arriving with the block on** (B6: a step from every state the guard is on in, and ramps) | MODELED below (rounds 2 to 5), every ceramic bank its maker's curves bounded on its own, both fault positions (at the connector with no lead resistance credited; at the lead's far end). Round 2's 3.30 uH is WITHDRAWN as a passing floor (round 5, the recheck): there a fault at the connector reads U5 0.2493 V resistive and, with RSENSE1's 5 nH and the Kelvin pair, the pins -0.3021 to +0.2591 V against +-0.240 V; Q12 turns off at most 62.7 A within 11.38 us; D4 carries no current; a rising source is cut with D4's room at least 0.060 V at any rate. At 1.00 uH U5 reads 0.5858 V, over its absolute maximum. No approach within the makers' printed rules removes the dependency; no loop is claimed to pass | **NOT MET**: no passing loop is claimed; the complete stage question is the engineer's (B6-ENG-1 with B6-ENG-2's stage-level note) |
| **Quiescent and conduction loss** in normal operation | The series path is at most 25.23 mOhm (Q12 9.56, Q13 11.12 at VGS 8.5 V or more, R87 4.56; the FETs at their 150 C reading). That is 0.217 W at the regulation's highest 2.934 A and 0.353 W at the trip's highest 3.741 A. The block draws 1.75 mA around the bank at 25 V (43.7 mW). On SC-37's day it costs 1.32 Wh of 336.6 Wh (0.39 %); on the bright day 1.78 Wh of 431.9 Wh | the energy budget's entry (an endurance cost) |

**The window kept.** REQ-016's normal window is unchanged: open circuit at most 25 V at the panel's coldest, the hold at 17.6
V, at most 100 W.
- The cut-off rises at 28.55 V at the least and falls back at 27.07 V at the least, both over 25 V with their tolerance and
  drift. Its highest, 31.06 V, is under every rating on the entry, and above it the stage is off, not running.
- U21 turns on at 9.16 V at the most (INP through R96 over R97 28.0k at 0.1 % at V(INP_H)'s 2.0 V; the UVLO by 8.44 V, L4-E11's figure
  for the same divider) and off at 7.46 V at the least. That is under the stage's own enable (R14 and R15, about 9.5 V), so it
  narrows nothing.
- The hold: the panel sits at most 0.074 V above PV_P at the regulation's highest current.
- 100 W: the static bound at the panel entry is **93.5957 W** (93.5521 W without the block). It counts the block's own currents
  around the bank, with the trip read at both ends of its 0.094 V drop.
- **Not claimed**, a residual named for layer 8: a stiff source between 25 V and the cut-off (outside the window, so a fault)
  runs the stage under the backstop's current trip, at most 116.5 W at the cut-off's highest. No protection here extends the
  permitted range.

**The interactions, and what was re-run.**
- **The backstop.** The sense bank, U18, U19, U20 and SWEN are behind the block and see its cut as the panel's absence (as at
  dusk). A connection now rises at the gate's slew, 17.28 to 24.65 V/ms (L4-E11), so the bank carries at most 1.760 A into the
  capacitors behind it, under the trip's least 3.0468 A, and U20 holds SWEN low for 180 ms anyway.
- **The start through Q12.** Q12 carries at most 6.109 A into every capacitor behind it (C133 and C134 included, each at its
  largest) at the gate's fastest slew, under U21's overcurrent least 6.364 A, so the start never runs the breaker's timer.
- **CS101 (M2), re-run** with the block's series resistance ahead of the bulk, the port bank across the input, and C133 and
  C134 beside the bulk (absent or at their largest). The filtered peak is
  **0.0591 A** at 2121 Hz (0.0589 A at the least resistance; the accepted 0.0585 A is reproduced with none), against the margin
  0.1130 A. The series element lifts the bank's share by at most 1.42 %, where the entry's impedance has a negative real part
  (the converter's constant power). The loop branch's room is read at M2 as accepted.
- **Check (b), re-run.** The capacitors at the entry hold 161.0 mJ (the port bank, C133, C134 and U21's filter added, at their
  largest). The response allowance is **0.771 ms** against ten times the typical sum (0.401 ms); the accepted figure was
  1.087 ms.
- **The LT8705A.** Its own enable, the hold (FBIN on PV_P) and the IMON_IN regulation (R59 behind the block) are unchanged.
- **The BQ25730 on VBUS20.** No path couples. The stage's output reaches it only through U4 and Q2 into VIN_RAW and board A's
  front end, and the block's cut is the panel's absence.
- **TRN-001's port table.** J_SOLAR's pin 2 becomes PV_RTN (switched by Q13), the first parts at the port are D11 and the port bank, and
  note E-N1 is closed.
- **Staying valid unchanged:** check (a)'s chain and its 93.5521 W at the stage; the supply sequencing; check (c)'s loaded
  network (D4 off, its breakdown now higher; C133 and C134 beside the bulk only take current from the paths it bounds); the M7
  figures (the port bank ahead, at its least at 25 V, takes a discharge's 2.25 uC as about 0.44 V); L4-E13's
  standoff check (now 30 V).
- **Changed:** D1 and D2 under REQ-016's criterion (SMCJ30A, 41.91 and 40.04 V). The margin beyond the basis is now D11's own
  rating, 23.3 A at 10/1000 us, since a pulse over the cut-off turns the block off within 4 us.

### The guard already on (B6): round 1, and round 2 after the external review (L4-F01)

**Round 1** (`11339ec7`) modelled a stiff 36 V source stepping onto the port with the guard on, found the drafted network
over U21's slew and INP ratings and U5's sense limit, and added C131 and C132 (two 10 uF 100 V), C133 and C134 (two 10 uF on
PV_P), C126 330 pF and R97 30.0k. With one bias factor shared by every ceramic bank it held U5 at 0.2991 V of 0.3 V for a
lead of at least 2.47 uH. **The external review (2 October 2026, L4-F01, P1)** found that not demonstrated: 0.3 % headroom, one
bias factor for three banks with no maker basis, a numerical error of the same size as the margin, and a margin resting on
the harness. Section 10 of the .out now prints round 2 (THE GUARD ALREADY ON, ROUND 2).

**The margin, decided before any value (SESSION):** U5's CSPIN to CSNIN differential within **+-0.240 V**, 20 % under its
+-0.3 V absolute maximum (8705af p.2). The bounded numerical error is added to the computed value; every other rating stays
10 % clear of its limit. The 0.060 V covers what the lumped model leaves out at U5's pins: RSENSE1's own inductance and its
Kelvin traces, the ceramics' ESL, the straight-line clamps, and the typical (not warranted) curves outside their bounds.

**The review's witnesses**, rebuilt on this record's own function and parameters (`guard_event`, the round-1 network, one
constant bias factor per bank; a 36 V step from U21's least turn-off at 7.46 V, idle, 2.47 uH, the bulk aged at -40 C; a test
pins them):

| Witness | U5's positive differential |
|---|---|
| 20 ns, one bias factor 1 | 0.299119 V (the review: 0.299128 V) |
| 1 ns, the same | 0.299589 V (0.299598 V) |
| 20 ns, TRK_VS 0.99, PV_P and TRK_VIN 1.00 | 0.300209 V (0.300218 V) |
| 20 ns, TRK_VS 0.95, PV_P and TRK_VIN 1.00 | 0.304653 V (0.304662 V) |
| 20 ns, PV_P and TRK_VS 0.25, TRK_VIN 1.00 | 0.500874 V |
| The round-2 network at the same case | 0.292716 V |

**The parts and their bounds** (Samsung's typical characteristic data). The excerpts are held back from the public tree:
each page carries "Copyright. SAMSUNG ELECTRO-MECHANICS All rights reserved." and grants no right to redistribute.
`fetch_maker_curves.py` fetches them into the ignored `v2/vendor/passives/held/`, and the record pins each excerpt's
sha256. Each bank is bounded on its own, at the side its bound needs:

| Bank | Parts | Bound used | Effective C |
|---|---|---|---|
| PV_F, the port bank | C131, C132, C135, C136: four CL32B225KCJSNNE (2.2 uF 100 V X7R 1210) | least for the guard-on step, largest for the cold ring | 3.98 uF at 36 V, 1.68 uF at 75 V (least) |
| PV_P | C133, C134: CL32B106KBJNNNE (10 uF 50 V X7R 1210) | least | 12.88 uF at 7.46 V, 5.07 uF at 30 V |
| TRK_VS | C71 to C74: the same part | least | 25.76 uF at 7.46 V, 10.14 uF at 30 V |
| TRK_VIN | C13, C14: the drawn CL31B106KBHNNNE (C89632, 10 uF 50 V X7R 1206); C15 (C132170, YAGEO) and C64 at +10 % with no derating (no curve held) | largest | 23.51 uF at 7.46 V, 9.54 uF at 30 V |

Each bound combines:
- the part's K tolerance, +-10 %;
- the typical curve's spread, +-15 % (ASSUMPTION: the maker prints no spread);
- the change under bias over -20 to +62.1 C, from the bias-TCC curve: CL31B106KBHNNN 0.943 to 1.053, CL32B106KBJNNN 0.965 to
  1.000, CL32B225KCJSNN 0.981 to 1.000;
- a cap at +10 % with no derating.

The model takes 10 mOhm ESR a part, against the maker's typical 5.5, 4.2 and 16.0 mOhm at 100 kHz. The higher value sends more
of the event downstream.

**The envelope and the model** (MODELED, `guard_event_b`: round 1's nodes, parts and U21's latest commands, every ceramic
bank its curves at its own voltage, the chord capacitance iterated in each step):
- a stiff 36 V source, no source impedance credited;
- its loop from 0.30 to 10.20 uH (38 values 10 % apart; round 2's bisected floor is WITHDRAWN in round 5), whether the fault
  sits at the connector (the loop is the source's own and NO lead resistance is credited: a connector fault has no lead in
  series, and no document bounds the source's own resistance) or at the lead's far end (the lead and its resistance added);
- the lead's resistance at the cold end, 0.0363 Ohm (0.0465 Ohm at a1solar's 40 C), for the far-end fault only;
- every start the guard is on in, the three bulk corners, D11 at both ends.

**The timestep**, on the worst case near round 2's loop (7.46 V, 0.0000 A): 40 ns 0.247894 V, 20 ns 0.248500 V, 10 ns 0.248803 V, 5 ns 0.248843 V, 2 ns 0.248868 V, 1 ns 0.248876 V, 0.5 ns 0.248891 V. The error bound added to U5 is twice
the largest difference from the 0.5 ns value at 20 ns or less: **0.000781 V**.

**The drafted network (A) at 3.30 uH** (round 2's reference loop, WITHDRAWN as a passing floor in round 5), the worst over every
start, bulk corner, D11 end and both fault positions; each resistive rating alone, with the least loop on the grid it holds
from (a property of that rating, not a floor):

| Rating, with its margin | Worst | Limit | Holds from |
|---|---|---|---|
| PV_F (U21's VS, CS+, CS-, ISCP; the port bank) | 83.47 V | 90 V (the exclusion line: 100 V absolute maximum less 10 %); the TPS4811-Q1's RECOMMENDED operating VS row is 80 V (SLUSEE5E 6.2), exceeded here by 3.47 V: OPEN (round 4, L6P-F10) | 2.44 uH (90 V); 4.03 uH (80 V) |
| PV_F's slew at CS-, CS+ and ISCP | 26.61 V/us | 54 V/us | 1.52 uH |
| Q12's VDS (and VS, CS+, CS- to SRC) | 74.84 V | 90 V | 1.83 uH |
| **U21's INP (R96 over R97 28.0k, both at 0.1 %; rounds 4 and 5)** | **18.29 V** (a fault at the connector; over the 18 V margin line, inside the 20 V absolute maximum) | 18 V | 3.58 uH |
| U21's EN/UVLO | 12.31 V | 18 V | 1.04 uH |
| PV_F's least | 7.46 V | -1 V | under 0.30 uH |
| **U5's CSPIN to CSNIN, positive (+ numerical error), the worst of both fault positions** | **0.2493 V** (a fault at the connector; 0.2395 V at the lead's far end) | **0.240 V** | **3.58 uH (the resistive peak alone; no passing floor is claimed)** |
| U5's CSPIN to CSNIN, negative (- numerical error) | -0.0591 V | -0.240 V | 0.48 uH |
| D4's current (the SMCJ30A, its least at the cold end) | none | none | 1.04 uH |
| U18's differential | 0.479 V | 1.8 V | 0.58 uH |
| PV_P (the bulk, C133, C134, U18's common mode) | 29.28 V | 45 V | under 0.30 uH |
| TRK_VS (C71 to C74), under D4's least breakdown | 29.15 V | 31.80 V | 1.04 uH |

**The corner search** at 3.30 uH. No correlation between the four banks is supported, so each is bounded on its own and every
one of the 16 combinations of their bounds runs over every start, bulk corner and D11 end. C15 and C64 carry no maker curve:
+10 % on their bank's upper side, a quarter of nominal on its lower (ASSUMPTION). 7 of 16 hold every rating with its margin
(round 5: with the connector case U5's positive peak is over the line at the selected corner). U5 reads 0.1074 to 0.2485 V before the
numerical error, the worst at the selected corner (the port bank, PV_P and TRK_VS at their least, TRK_VIN at its largest);
over the 16, PV_F reaches at most 83.55 V and TRK_VS 29.90 V.

- **No loop is claimed to pass (round 5).** At 3.30 uH U5's resistive peak alone reads 0.2493 V at a fault at the connector
  (round 2's 0.2395 V was the far-end case, the lead's resistance credited), and the complete budget with RSENSE1's inductance is
  in round 3's parasitics' budget below, outside +-0.240 V in both polarities. At 1.00 uH PV_F, its slew, Q12's VDS, INP and
  U5 exceed their margins, and U5 reads 0.5858 V, over its 0.3 V absolute maximum. At 0.30 uH U5 reads 1.4059 V and PV_F 321.6 V.
- At 3.30 uH (the worst of both fault positions):
  - **Q12** uses 0.241 of its derated chart (TI's Figure 10, the 10 us line for its 11.38 us; derated 0.650 for a case at
    68.8 C) and turns off at most 62.7 A.
  - **Q13** carries 75.0 A in the third quadrant, 0.293 of its chart (the channel's row taken, INFERRED).
  - **D11** takes 51.7 A and 20.0 mJ against 462 mJ.
  - **R87's** 0.285 V reaches CS+ through RSET, 2.86 mA against 100 mA for 1 ms.
- **The reviewed case** (from 25 V): Q12 turns off at 32.6 A; TRK_VS stays 2.648 V under D4.
- **Ramps** at 3.30 uH (48 rates, 0.01 to 10 V/us): the closest TRK_VS comes to D4 is **31.742 V** at 0.137 V/us, **0.060 V**
  under it; D4 never conducts; U5 at most 0.2026 V.
- **The cold connection**, over the whole envelope from 0.30 uH: PV_F at most 84.6 V, its slew 56.1 V/us, INP 18.54 V;
  Q13's body diode at most 200.1 A; D11 at most 17.7 mJ. **The start**: 6.109 A through Q12, under U21's overcurrent least
  6.364 A.

**The three approaches:**

| | Approach | Result | Verdict |
|---|---|---|---|
| (A) | **Drafted, no passing loop**: round 1's guard with parts a maker characterises, bounded bank by bank | round 2's **3.30 uH** reference loop (two conductors 6.09 mm apart over 5 m) is WITHDRAWN as a passing floor (round 5): there a fault at the connector reads the pins -0.3021 to +0.2591 V with the parasitics, against +-0.240 V | no passing loop is claimed |
| (B) | A pin-level limiter: series resistors into CSPIN and CSNIN with a clamp or capacitor across the pins (the coordinator's steer), which would bound the pins' differential whatever the loop | 8705af p.30: "all four of the current sense pins can draw bias current under normal operating conditions. As such, do not place resistors in series with any of the CSxIN or CSxOUT pins". CSNIN also feeds the boost capacitor charge control, which "can draw current in certain conditions" (no figure). p.4 prints only a typical sum of the two pins' bias, 31 uA, with no maximum and no split; 10 Ohm a pin on that sum alone is 0.68 % of the sense at the regulation's highest current, and the boost block's draw has no bound, so the 100 W bound's chain would rest on an unprinted current. The filter p.34 shows is for CSP and CSN only (10 Ohm at most, RC under 30 ns) | **not taken**; the question is drafted for Analog Devices (`clarification/analog-devices-lt8705a.txt`, item 6) |
| (D) | The TPS48111-Q1: short-circuit propagation 1.60 us at most against the TPS48110-Q1's 5 us | the loop where D's resistive peak alone meets the line falls to 1.64 uH (3.06 mm; no floor claimed for D either), and at 1.00 uH U5 still reads 0.3262 V. Its pin 2 is INP_G, so it has no OV input; the cut-off would move to INP (1 us) through a reference whose response no held sheet prints | not taken |

**The engineer's row B6-ENG-1** (restated in round 5 after the recheck: no approach within the makers' printed rules holds the
margin independent of the source's loop, and no passing loop is claimed):

| Field | Entry |
|---|---|
| Affected circuit | board E's solar guard (U21, Q12, the port bank) and U5's input sense (RSENSE1, CSPIN, CSNIN, C13 to C15) |
| Evidence and failed condition | no passing loop is claimed. At round 2's 3.30 uH the pins' complete budget (the resistive peak, RSENSE1's inductance at the WSL's printed bound 5 nH, the Kelvin pair's 1 nH, the numerical error) reads -0.3021 to +0.2591 V at a fault at the connector (no lead resistance credited) and -0.2884 to +0.2486 V at the lead's far end, against +-0.240 V: outside the line in both polarities, inside the +-0.3 V absolute maximum only on the positive side. At 1.00 uH U5's resistive peak alone reads 0.5858 V, over the absolute maximum, because any guard that is closed when a stiff source arrives charges the stage's capacitance at a rate only the loop sets; the source's own resistance is bounded by no document. INP reads 18.29 V there at a fault at the connector, over its 18 V margin line (inside the 20 V absolute maximum; the margin holds from 3.58 uH). PV_F 83.47 V at that loop exceeds the TPS4811-Q1's recommended operating VS row of 80 V (OPEN, round 4: under the row from 4.03 uH; the 90 V line above it is the exclusion line only) |
| Decision or measurement needed | the stage's current-sense arrangement itself (where the input current is sensed and with what; B6-ENG-2's stage-level note), with RSENSE1's inductance (unprinted for the chosen part; 5 nH taken) and the source's loop and resistance bounded by the kit's rules and measured before any step is applied; a sense-pin filter only if Analog Devices permits it with a bounded error (clarification item 6) |
| Pass criterion | U5's differential within +-0.240 V at the IC pins for the declared envelope, both fault positions, captured at layer 9 with the guard on and a 36 V supply stepped on from about 7.5 V and from 25 V |
| Consequence of failure | U5's sense pins over their absolute maximum; the LT8705A possibly damaged and the solar stage lost (the 100 W bound and the backstop rest on it) |
| Work blocked | D-10's closure and R-176's step row; board E's other drafts are not blocked |

### Round 3: the sense moved off the stage's input capacitance (route 3), result (ii)

The coordinator's one design-convergence attempt (2 October 2026, evening): B6-ENG-1's third route, worked to the
circuit. What RSENSE1 carries is the current into whatever sits behind it: the guard-on transient charges that
capacitance at a rate the loop sets (B6), and in operation M1 draws its pulsed current from it (8705af p.27:
"Discontinuous input current is highest in the buck region due to the M1 switch toggling on and off"). The sheet places
the input ceramics at the MOSFETs (p.36: "These capacitors carry the MOSFET AC current in the boost and buck regions"),
asks for at least 1 uF at the VIN pin (p.27), routes the sense pair together with Kelvin taps (p.36), and rates the sense
differential's **operating** range at -100 to +100 mV (p.5, the full-range row; p.31: it "should be kept below 100mV due
to the limited amount of current that can be driven out of IMON_IN", and the input current "often has ripple and
discontinuities" that CIMON_IN averages). So the capacitance behind RSENSE1 is bounded from above by the transient and
from below by the operating range, and route 3 is the question whether any split of the input ceramics satisfies both.

**The operating model** (MODELED, `sense_ripple` in the record): the buck region's corner, 25 V in (REQ-016's open
circuit) delivering into the bus at 12.0 V (VIN_RAW's declared nominal) and at the drawn 15.1 V setpoint; the input
current at the regulation's highest 2.9337 A and at the trip's 3.7408 A; the oscillator at its least 170 kHz; L1 at
the XAL1510's -20 % (8.0 uH; its row 10 uH, 6.80 uH typical and 9.00 uH at the saturation current); M1's edges
20 ns (p.26: 20 to 40 ns typical, no minimum printed); RSENSE1 at its highest with 5 nH (Vishay's WSL prints 0.5 to
5 nH; the Milliohm part prints none: ASSUMPTION at that bound); each ceramic's ESR the maker's typical at that frequency
and its ESL from its self-resonance (CL31B106KBHNNN 1.06 nH at 1.54 MHz, CL32B106KBJNNN 1.06 nH at 1.54 MHz, CL32B225KCJSNN 0.90 nH at 3.57 MHz); the taps 0.5 nH each (a layout obligation, declared); the bulk new at 20 C
ahead of the bank. The pins read the node difference across RSENSE1 and its inductance over the last of 25 periods. Its
limits: a huge bank behind reads the flat average (0.0447 to 0.0456 V), a huge bank ahead and none behind reads M1's
peak (0.1299 V = 8.41 A x RSENSE1).

**The splits** (the ceramics ahead of RSENSE1 at their largest and behind it at their least for the operating range, the
reverse for the transient; U5 resistive with the numerical error, then the pins with RSENSE1's 5 nH and the Kelvin pickup
from the rise to Q12's turn-off, the worst of both fault positions (round 5); the operating figures at the 25 V corner over both bus voltages):

| Split | Ahead, uF at 25 V | Behind, uF | Transient at 0.30 uH, U5 (the pins) | At 1.00 uH | At 3.30 uH | In operation: resistive peak at the regulation's / the trip's current | The pins in operation | The monitor's average, regulation / trip (positive: high; MODELED) | Holds |
|---|---|---|---|---|---|---|---|---|---|
| A, as drafted: C71 to C74 ahead, C13 to C15 and C64 behind | 21.42 | 8.16 | 1.4059 V (-3.463 to +1.447 V) (fails d4, en, inp, pvf, slew, trkvs, u18, u5n, u5p, vds) | 0.6013 V (-0.802 to +0.625) (fails inp, pvf, slew, u5p, vds) | 0.2493 V (-0.302 to +0.259) (fails inp, u5p) | 0.1174 V / 0.1421 V | -0.1866 to +0.1863 V | +7.9 % / -10.2 % | neither |
| route 3: everything ahead, C64 alone behind | 31.90 | 0.11 | 0.0684 V (-0.164 to +0.073 V) (fails d4, en, inp, pvf, slew, trkvs, u18, vds) | 0.0625 V (-0.036 to +0.064) (fails d4, inp, pvf, slew, trkvs, vds) | 0.0600 V (-0.013 to +0.061) (fails inp) | 0.1297 V / 0.1556 V | -1.2092 to +0.9118 V | +20.3 % / -12.8 % | U5 yes, the port's ratings no, the operating range no |
| route 3: one CL32B225KCJSNNE (2.2 uF) and C64 behind | 31.90 | 1.38 | 0.2932 V (-1.480 to +0.302 V) (fails d4, en, inp, pvf, slew, trkvs, u18, u5p, vds) | 0.1359 V (-0.404 to +0.140) (fails inp, pvf, slew, vds) | 0.0883 V (-0.143 to +0.090) (fails inp) | 0.1280 V / 0.1538 V | -0.3270 to +0.2702 V | +21.2 % / -9.6 % | neither |
| route 3: two CL32B225KCJSNNE and C64 behind | 31.90 | 2.66 | 0.5501 V (-1.913 to +0.565 V) (fails d4, en, inp, pvf, slew, trkvs, u18, u5p, vds) | 0.2027 V (-0.499 to +0.210) (fails inp, pvf, slew, vds) | 0.1141 V (-0.181 to +0.117) (fails inp) | 0.1265 V / 0.1524 V | -0.2329 to +0.2172 V | +18.8 % / -8.4 % | neither |
| route 3: one CL32B106KBJNNNE (10 uF) and C64 behind | 31.90 | 3.23 | 0.6839 V (-1.955 to +0.703 V) (fails d4, en, inp, pvf, slew, trkvs, u18, u5p, vds) | 0.3169 V (-0.515 to +0.331) (fails en, inp, pvf, slew, u5p, vds) | 0.1344 V (-0.195 to +0.138) (fails inp) | 0.1244 V / 0.1497 V | -0.2910 to +0.2432 V | +17.7 % / -8.2 % | neither |
| route 3: two CL32B106KBJNNNE and C64 behind | 31.90 | 6.36 | 1.2778 V (-1.973 to +1.309 V) (fails d4, en, inp, pvf, slew, trkvs, u18, u5p, vds) | 0.5580 V (-0.499 to +0.586) (fails en, inp, pvf, slew, u5p, vds) | 0.2178 V (-0.194 to +0.228) (fails inp) | 0.1212 V / 0.1465 V | -0.2163 to +0.2047 V | +11.8 % / -9.6 % | neither |
| Figure 1: nothing ahead but the bank, everything behind | 0.00 | 20.66 | 3.4902 V (-9.303 to +3.570 V) (fails d4, en, inp, pvf, slew, trkvs, u18, u5n, u5p, vds) | 1.5310 V (-2.722 to +1.605) (fails inp, pvf, slew, u5p, vds) | 0.6086 V (-0.992 to +0.636) (fails inp, u5p) | 0.0983 V / 0.1213 V | -0.1552 to +0.1658 V | +0.7 % / -5.7 % | neither |

**The floors** of the splits that hold U5 at 0.30 uH, rating by rating (the least loop each holds from, both fault positions): route 3: everything ahead, C64 alone behind: pvf 2.44 uH, slew 1.52 uH, vds 1.83 uH, inp 3.58 uH, en 1.04 uH, d4 1.14 uH, u18 0.48 uH, trkvs 1.14 uH; route 3: one CL32B225KCJSNNE (2.2 uF) and C64 behind: pvf 2.44 uH, slew 1.52 uH, vds 1.83 uH, inp 3.58 uH, en 1.04 uH, u5p 0.44 uH, d4 1.04 uH, u18 0.53 uH, trkvs 1.04 uH; Figure 1: nothing ahead but the bank, everything behind: pvf 2.44 uH, slew 1.52 uH, vds 1.83 uH, inp 3.58 uH, en 1.04 uH, u5p none, u5n 0.86 uH, d4 0.78 uH, u18 0.71 uH, trkvs 0.78 uH.

**The as-drafted split at the hold** (16.97 V in, 15.1 V out, 2.9337 A): RSENSE1's resistive peak 0.0585 V, the pins
-0.0713 to +0.0815 V: inside the operating range there. **Sensitivities** at the 25 V corner, 12.0 V out, the regulation's
current: M1's edges at 10 ns, the pins -0.4329 to +0.2552 V; every inductance zero, 0.0036 to +0.1178 V (the resistive
share alone, 0.1178 V peak); the edge's inductive step at the pins, INFERRED as the ceramics' ESL and tap times the valley
current over the edge: 0.299 V. In operation RSENSE1's inductance sets the pins' swing at M1's edges for the as-drafted
split: 1 nH: -0.0625 to +0.1210 V; 2 nH: -0.1116 to +0.1259 V; 5 nH: -0.1556 to +0.1295 V.

**The parasitics' budget** at round 2's reference loop (3.30 uH, WITHDRAWN as a passing floor in round 5), the worst over both
fault positions, linear worst case, the pins reading R i + L di/dt with RSENSE1's inductance at the WSL's printed bound 5 nH
and the Kelvin pair's loop 1 nH (the layout obligation: the pair from the pad centres, together, over the ground return):
- RSENSE1's current rises at most 2.64 A/us during the charging (RSENSE1's inductance +0.0132 V, the pair +0.0026 V) and
  falls at most 70.0 A/us when Q12 turns off within its 243 ns gate fall (-0.3498 V and -0.0700 V);
- **the pins**, the worst of both fault positions: at most **+0.2591 V** on the rise (resistive 0.2485, numerical 0.000781) and
  **-0.3021 V** at the turn-off. Against the 0.240 V margin line the rise is over it by 0.0191 V (its inductive and Kelvin
  terms 0.0098 V at 5 nH) and the turn-off is past it by 0.0621 V;
- **by fault position**: at the connector (no lead resistance credited) the pins read **-0.3021 to +0.2591 V**, and the
  turn-off's -0.3021 V is **PAST the -0.3 V absolute maximum**; at the lead's far end they read -0.2884 to +0.2486 V, and the
  turn-off's -0.2884 V is inside the absolute maximum but past the -0.240 V margin line;
- over RSENSE1's inductance at this loop (0.5 nH -0.129 to +0.253 V OUT; 1.0 nH -0.130 to +0.253 V OUT; 1.5 nH -0.130 to +0.254 V OUT; 2.0 nH -0.138 to +0.255 V OUT; 3.0 nH -0.193 to +0.256 V OUT; 5.0 nH -0.302 to +0.259 V OUT; OUT: a polarity outside the line): no inductance tried brings both polarities inside the line at this loop (information, not a search for a passing value);
- the ceramics' ESL and tap (1.06 nH a part at most, 0.5 nH tap) move the node, not the pin difference, and are in the
  operating model above.

So RSENSE1's inductance, printed by no maker for the chosen part, is part of the stage question handed to the engineer.

**The verdict on route 3 (SESSION): it does NOT hold over the whole envelope, result (ii).** No split of the input
ceramics holds both duties: the splits that hold U5's transient at 0.30 uH leave at most a few microfarads behind RSENSE1,
so in operation M1's pulses flow through it and the sense differential leaves its +-100 mV operating range at the 25 V
corner; the splits that keep more behind it bring the transient back. The port's own ratings keep their floors whatever
the split (at 0.30 uH PV_F reads at least 321 V against 90 V, Q12's VDS and INP with it), and that floor is the **source**
loop's (the panel lead and whatever a stiff source arrives through), not one the kit's harness from J_SOLAR to the stage
controls. **B6-ENG-1 is restated in round 5** (the recheck): no passing loop is claimed; the pins' complete budget at round
2's 3.30 uH, both polarities and both fault positions, is handed to the engineer with the stage question, RSENSE1's
inductance (unprinted for the chosen part; 5 nH taken) inside it. No further desk round on B6 without new evidence.

**A new finding, independent of B6: the as-drafted split's sense in operation (B6-ENG-2).** At the 25 V corner the sheet's
CIN placement cannot be met with these parts: at 25 V bias the 50 V X7R ceramics hold 8.2 uF of their 24.8 uF
nominal behind RSENSE1 and 21.4 uF of 40.0 uF ahead, and even with everything behind (the sheet's Figure 1) the
resistive peak is 0.0983 V at the regulation's current. For the as-drafted split the pins read -0.1866 to +0.1863 V in
operation and the monitor, limited to 100 mV and producing no current for a negative differential (8705af p.31), reads the
average **+7.9 %** at the regulation's highest current (-10.2 % at the trip's; positive: HIGH, the limit then regulating BELOW
its setting). MODELED: both the direction and the size rest on this model of the amplifier, clipped at 100 uA above 100 mV,
which the sheet does not print (clarification item 7); round 3's "5.7 % low" averaged the negative half-cycles as negative
monitor current, which the sheet excludes, and is withdrawn. The 100 W bound rests on the backstop (U18, U19, the bank),
which does not read RSENSE1 and is unaffected; the regulation of L4-E7R is NOT MET at that corner on the
sheet's operating range until the pulse share is measured or the sense arrangement changes.

| Field | Entry (B6-ENG-2) |
|---|---|
| Affected circuit | U5's input sense: RSENSE1, CSPIN, CSNIN, C13 to C15 behind it, C71 to C74 ahead of it |
| Evidence and failed condition | the periodic model above against 8705af p.5 (the +-100 mV operating range) and p.31: at 25 V in and a 12.0 V bus the resistive peak across RSENSE1 is 0.1174 V at the regulation's highest current, the pins -0.1866 to +0.1863 V with RSENSE1's 5 nH; the monitor's average +7.9 % (MODELED; positive: high) |
| Decision or measurement needed | the pins' waveform in operation at 25 V in and the lowest bus (the regulation's error measured against its setting); or Analog Devices' statement of what the amplifier delivers above 100 mV (clarification item 7); or enough low-derating capacitance behind RSENSE1 (which worsens B6's guard-on transient); and RSENSE1's inductance bounded or measured |
| Pass criterion | the pins within +-100 mV at every operating point, or the regulated input current measured within check (a)'s error budget at the 25 V corner |
| Consequence of failure | the input limit regulating off its setting at high input and a low bus (this model: below it, by the figure above), and a possible stress on the sense pins at the switching edges: the sensitivity at 10 ns edges reaches -0.4329 V at the pins, beyond the -0.3 V absolute maximum (round 3's unconditional "no damage" is withdrawn); the 100 W bound rests on the backstop |
| Correction candidates already measured here | the sheet's own Figure 1 arrangement (nothing ahead of RSENSE1 but the bank, everything behind): resistive peak 0.0983 V at the regulation's highest current, the pins -0.1552 to +0.1658 V with 5 nH, the monitor's average +0.7 %, but U5's transient then fails at every loop on the grid (u5p none); the splits that hold the sense's transient at 0.30 uH (C64 alone, one 2.2 uF behind) leave the operating range by more (0.1297 and 0.1280 V resistive). No split measured here holds both |
| Stage-level note (the owner's rule) | this is the third compensating change asked of the solar input stage's sense and guard (L4-E7R's C71 to C74 ahead of RSENSE1, B6 round 1's port bank and C133/C134, B6 round 2's part bounds and floor). The stage's current-sense arrangement itself (where the input current is sensed and with what) is handed to the engineer for reconsideration, the wider form of B6-ENG-1's route 3; no further split is tried at the desk |
| Work blocked | the regulation's acceptance row at layer 9; not the drafts |

**For L4-E9's register** (its D-10, D-11, D-12, R-173, R-174 and R-176; text for L4-E9's author, nothing of L4-E9's is edited
here):
- **D-10 and D-11**: a selected remedy, drafted and not applied: the cut-off U21 with Q12, the return switch Q13, D11, the
  port bank (C131, C132, C135, C136, Samsung CL32B225KCJSNNE), C133 and C134 on PV_P and C71 to C74 on TRK_VS (Samsung
  CL32B106KBJNNNE), D4 to the SMCJ30A, R97 28.0k and C126 330 pF. **D-10's source arriving with the guard on is NOT CLOSED**:
  no passing loop is claimed (round 5, the recheck): at round 2's 3.30 uH a fault at the connector, no lead resistance
  credited, reads the pins -0.3021 to +0.2591 V with RSENSE1's inductance against +-0.240 V, and the complete stage question is the
  engineer's (B6-ENG-1, with B6-ENG-2's stage-level note); INP reads 18.29 V there, over its 18 V margin line. Round 3 (route 3, the sense moved off the stage's input
  capacitance) does not remove it, result (ii); RSENSE1's inductance (unprinted) is part of the stage question. **New, B6-ENG-2**: the
  as-drafted sense leaves its +-100 mV operating range in operation at the 25 V corner (the regulation's acceptance row,
  not D-10).
- **D-12** (L4-POWER-ARCHITECTURE.md's row, now "MEETS with the block on and off"): CS116 MEETS with the block on and off;
  CS115 MEETS with the block off and, with it on, is **CONDITIONAL on R-174** (the cable's recorded loop current under
  15.68 A, or U5's differential measured under 0.3 V; U5 reads 0.1350 V at CS115's 5 A calibration level).
- **R-176's acceptance, revised again** (round 2):
  1. the cut-off's rise and fall on a ramped supply: 28.55 to 31.06 V rising, 27.07 V or more falling;
  2. a 36 V supply connected cold: Q12 never conducts, D4 carries nothing, PV_F at most 85 V, its slew and INP inside their
     absolute ratings (their 10 % margin lines are not held at a connector fault near the envelope's least loop, round 5);
  3. at layer 9, the waveforms at the IC pins: a 36 V supply stepped onto the port with the guard on, from about 7.5 V and
     from 25 V, through a loop measured first. U5's CSPIN to CSNIN within +-0.240 V, U21 turning Q12 off (at most 63 A,
     within 12 us; the computed 62.7 A within 11.4 us at round 2's loop, rounded up; this list read 61 A until set 28),
     D4 carrying nothing, PV_P under 31.80 V, PV_F under the TPS4811-Q1's recommended operating 80 V row (OPEN
     at round 2's loop: 83.47 V, under the row from 4.03 uH; round 4, L6P-F10). No loop is claimed to pass (round 5): at 3.30 uH
     the pins' complete budget is outside +-0.240 V and B6-ENG-1 decides;
  4. a reversed bench panel's curve: no current, the high side's pins against GND;
  5. Q13's leakage at the hot end, under 32.1 uA;
  6. no short-circuit trip with C126 at 330 pF in operation and under CS116 (R-174).
- Owed with it: the LCSC codes of D4 and of the Samsung parts, U21's DGX-19 land, the regeneration and its gates.

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
| R-156 (register): the panel lead's surge and sustained over-voltage | PENDING on this round | derived: CS116 MEETS, CS115 CONDITIONAL (the loop current under 15.7 A), the panel's cold open circuit MEETS, a 36 V source on the port and a reversed panel NOT MET; remedied by the over-voltage cut-off U21 with Q12, D4 to the SMCJ30A and the return switch Q13 (drafted), the TVS-only change SMCJ36A with the 63 V class parts, or an over-voltage and reverse disconnect; a CS116 and CS115 test row owed (see the panel lead's section) |

## The series disconnect: evaluated, not taken (SESSION)

The LM5069 class hot-swap controller prints its current limit (VCL 48.5 / 55 / 61.5 mV) at VIN = 48 V, not at the
panel's 17 to 25 V, and its 12 % spread would push the regulation further down than C's; SWEN already removes the path
from the panel to the pack, and the input capacitors' charge is bounded in check (b). A series FET would cover a shorted
switch of the LT8705A, a single fault layer 8 judges. The solar-fault remedies select a series element for another reason:
the TPS48110-Q1 over-voltage cut-off (U21, Q12) for a 36 V source on the port, beside a return switch (Q13) for a reversed
panel. It is not a current limit for the stage, and the LM5069's row does not enter it.

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

`apply_gen_sch_e_backstop.py`, ten edits on the text the hold and input limit drafts leave (it refuses a generator
without them): the bank on PV_P to TRK_VS; the 50 V bulk (C11, C12, C69, EEHZA1H330XP) on PV_P ahead of it; R59 and CSPIN
behind it, nothing in series with CSPIN or CSNIN; U18 with R65 16.9k, R66 8.45k (C861590) and the INB filter, C70 and C75
to C78, five 100 nF NP0 50 V 1206 (C170182); U19 with R67 and R68; U20 with R69; SWEN on TRK_SWEN with R70 8.06k and R71
6.04k (C728595); C66 to C68; C71 to C74 and D4 and R14 on TRK_VS; R16 31.6k (C705766); the declarations; C66, C67 and
C68 class D in the generator's G14 table (round 6, below). Read back on a scratch copy; never applied to the tree; R10
untouched.

`apply_gen_sch_e_solar_guard.py` (the solar-fault remedies), eight edits after the backstop's, L4-E9's hot swap and L4-E11's
entry drafts (it refuses a generator without them): J_SOLAR.2 to PV_RTN and F2 to PV_F; D11, the port bank C131, C132, C135
and C136 (Samsung CL32B225KCJSNNE), U21 with R87 to R100 (R97 28.0k) and C126 (330 pF) to C130, Q12; Q13 with R101, R102 and
D12; C133 and C134 on PV_P and C71 to C74 on TRK_VS, Samsung CL32B106KBJNNNE; D4 to the SMCJ30A (codes owed); PV_P switched by U21, the rails PV_F, PV_SNS and PV_RTN; the schematic section. Read back on a scratch copy; never applied to the tree; R10 untouched.

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
- **The solar-fault remedies** (with the block fitted; R-176 as revised by B6 round 2):
  - the cut-off's rise and fall on a supply ramped through 25 to 32 V, against 28.55 to 31.06 V rising and 27.07 V
    falling at the least;
  - a 36 V supply connected cold: Q12 never conducts, D4 carries nothing, PV_F at most 85 V, its slew and INP inside their
    absolute ratings (round 5: the 10 % margin lines are not held at a connector fault near the envelope's least loop);
  - **at layer 9, the waveforms at the IC pins**: the 36 V supply stepped onto the port with the guard on, from about 7.5 V
    and from 25 V, through a loop measured first: U5's differential (at CSPIN and CSNIN) within +-0.240 V, Q12 off at most
    63 A within 12 us, D4 carrying nothing, PV_P under 31.80 V; no loop is claimed to pass (round 5), B6-ENG-1 decides;
  - a reversed bench panel curve: no current, and the high side's pins within 1 V of GND;
  - CS116 and CS115 on the port with the block on and off (R-174), no short-circuit trip with C126 at 330 pF;
  - Q13's leakage at 25 V across it at the hot end, against the 32.1 uA break-even.
- **B6 round 3, the sense in operation and RSENSE1's inductance** (B6-ENG-2 and B6-ENG-1's added item; board E's first
  prototype, since the LT8705A demonstration board has another sense arrangement and does not transfer):
  - the waveform at U5's CSPIN and CSNIN (a differential probe at the pins, at least 200 MHz) with the stage regulating at
    25 V in and the bus at its lowest, and at the hold: the peaks against +-100 mV, the average against the setting (the
    model: 0.1174 V resistive peak and -0.1866 to +0.1863 V at the pins at 25 V in and a 12.0 V bus, the monitor's average +7.9 %, MODELED);
  - RSENSE1's inductance on the fitted part (an impedance analyser or the step response at the pads), against the 5 nH the
    budget takes (no bound is claimed).

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
| (c) the panel lead, derived | CS116 MEETS (D4 at 10 A 39.00 V against 50 V; D4 off in the loaded network); the panel's cold open circuit MEETS | CS115 CONDITIONAL on the loop current (U5's bound reached at 15.7 A) | a 36 V source on the port and a reversed panel NOT MET on the drafted entry |
| the solar-fault remedies | the cut-off U21 with Q12 (D4 to the SMCJ30A) and the return switch Q13: the 36 V source connected cold, the reversed panel, CS116 with the block on and off, CS115 with it off, the window all MEET; the source arriving with the guard on holds every rating with its margin only for a source loop of at least 3.30 uH (B6 round 2: NOT MET under it) | the cut-off 0.731 V over CS101's peak and 0.737 V under D4 (aged); U5 0.2396 V of the 0.240 V margin at 3.30 uH; the static bound 93.5957 W | B6-ENG-1 (the source loop's floor, or Analog Devices' answer on a sense-pin filter), CS115's cable current or U5 measured (R-174), Q13's leakage above 25 C, D4's LCSC code, U21's land, the bench rows |

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
- `vishay-wsl2512.txt`: the bank's pulse capability at D4's own rating (the capability scenario, beyond the derived surge).

## The checks, and what changed

| Item of Layer 8's record l8p (`L8P-BREAKER.md` section 8 at `fnd/l8p` `b1295c1e`), finding L8P-F01; round 6, 4 October 2026 | Change |
|---|---|
| Composed in L4-E9's change-list order, board E's generator stops at its G14 table: "decoupling entry C66 -> U18.5 carries no class (G14)"; the same without l8p's draft | Reproduced on scratch copies (every board E draft in L4-E9's order, the generator run to its end with record l8p's stand-in layout step): the refusal as read, with and without l8p's enable draft. The backstop draft's tenth edit gives C66 (U18's V+, pin 5), C67 (U19's VDD, pin 5) and C68 (U20's VDD, pin 6) class D in `_DEC_CLASS`, a capacitor a maker ties to a supply pin (DECOUPLING.md section 6), each with its maker's clause: SBOS181F section 9, "TI recommends placing a 0.1-uF capacitor near the V+ pin" (p.18) and 10.1 (p.19); SBVS240C pin 5 VDD, "a 0.1-uF ceramic capacitor close to this pin" (p.3) and 10.1 (p.19); SBVS050N pin 6 VDD, the same (p.4) and 8.4.1 (p.15). The class's two rules hold as drafted: D1, the maker's value, 0.1 uF, is the 100n drawn; D2, the own-pin window, is the layout's (each maker's "close to this pin"). U19's VDD is TRK_LDO33, a regulated 3.3 V, so SBVS240C section 9's RC filter (for a VDD supply with transients over 40 V or slewing above 1 V/us) does not apply. No value, net or other edit changes |
| The composed generator after the correction | Runs past G14 in L4-E9's order, with and without l8p's enable draft; it stops next at `intent.write`: "+12V_FAN names source L4, which is not on that net", L4-E11's aux draft (L8P-F03, that record's). With record l8p's own scratch stand-in for L8P-F03 it runs to its end (295 parts, the intent written), C66 to C68 class D. The drafts up to the backstop alone run to the end. `test_l4e7` holds both on scratch copies, the order read from L4-E9's CHANGE_ORDER |
| The results cache | The output's edit count and the new read-back ("C66 to C68 class D in G14's table") change it, so it was recomputed once through regen_out. The KEY did not record the drafts compute() reads back (importlib's own reader is not open()), so a changed draft would have left the cache standing: `load()` now reads each module's source through open(), and the drafts enter the KEY |

| Item of the external review of the provisional fixes, L4-F01 (P1), and the coordinator's round-2 instruction | Change |
|---|---|
| Decide the intended margin first, and why | U5 within +-0.240 V (20 % under the 0.3 V absolute maximum), the numerical error added to the computed value, every other rating 10 % clear; the 0.060 V covers the lumped model's omissions at U5's pins; decided before any value |
| Actual capacitors, bounded at their voltage and temperature from the maker's data, banks independent | Samsung CL32B225KCJSNNE (the port bank), CL32B106KBJNNNE (PV_P and TRK_VS), the drawn CL31B106KBHNNNE (TRK_VIN), their typical DC-bias, bias-TCC and ESR curves (held back by their terms, fetched by `fetch_maker_curves.py`, sha256 pinned); each bank bounded on its own (K +-10 %, a +-15 % spread on the typical curve, the temperature at bias), the capacitance a function of each bank's own voltage in the solver; the corner search over the 16 combinations of the four banks' bounds at 3.30 uH: all hold, the selected corner the worst on U5 (0.1050 to 0.2387 V before the numerical error) |
| Numerical error in the margin | a timestep study from 40 ns to 0.5 ns on the switched, loaded network's worst case: 0.000882 V added to U5; the review's 1 % RLC tolerance stays a check of the solver only |
| The complete fault envelope, from zero length | a stiff 36 V source, no source impedance credited, its loop from 0.30 uH (a fault at the connector) to 10.2 uH; every rating with the least loop it holds from |
| A minimum inductance made a controlled part, or the protection network changed; at most three approaches | (A) maker-bounded parts on round 1's guard: floor 3.30 uH; (B) a pin-level limiter: excluded by 8705af p.30 (no series resistors at CSxIN; the pins' bias printed only as a typical sum), its question drafted for Analog Devices; (D) the TPS48111-Q1: floor 1.57 uH, no OV pin. An on-board series inductance was set aside before the comparison: it puts an L-C resonance inside M2's 30 Hz to 150 kHz band, where the accepted CS101 margin is decided. No approach removes the floor: the engineer's row B6-ENG-1 |
| Preserve CS115's interpretation; the bench confirmation at the IC pins a layer 9 acceptance | kept; R-176 row 3 is the layer 9 acceptance with its criterion (+-0.240 V at CSPIN and CSNIN) |
| The review's witnesses | rebuilt on the record's function (0.299119 to 0.500874 V) and pinned by a test |

| Item of the coordinator's round-3 brief (the one design-convergence attempt) | Change |
|---|---|
| Route 3 worked to a drafted circuit holding at any loop from 0.30 uH, the parasitics budgeted, the sheet's sense-network rules respected, the regulation re-derived | seven splits of the input ceramics on the record's solver and a periodic model of the sense in operation; none holds both the transient and the sheet's +-100 mV operating range, and the port's own ratings keep their floors (PV_F from 2.02 uH, INP from 3.25 uH): result (ii), nothing drafted, B6-ENG-1 stands with RSENSE1's inductance added to its decision |
| The parasitics as voltages at the critical di/dt | RSENSE1's inductance (5 nH, the WSL's printed bound; the chosen part prints none), the Kelvin pair (1 nH, declared), the ceramics' ESL (from the makers' self-resonance) and tap (0.5 nH, declared): the rise +0.2487 V and Q12's turn-off -0.2885 V at the pins at the floor, both inside +-0.3 V; the turn-off stays inside the 0.240 V margin line for an inductance at most 3.0 nH |
| The 100 W bound and the regulation | the bound unchanged (the backstop does not read RSENSE1); the regulation re-derived: the sense leaves its operating range at the 25 V corner with a 12.0 V bus, the average read 5.7 % low at the regulation's highest current, B6-ENG-2 |
| The bench criterion and specimen | not selected (result ii); what the bench owes is in B6-ENG-1 and B6-ENG-2: the pins' waveform in operation at 25 V in and the lowest bus, and RSENSE1's inductance measured, on board E's first prototype (the LT8705A demonstration board has another sense arrangement and does not transfer) |

| Item of the Layer 6 author's findings on the drafts (L6-POWER-PARTS.md L6P-F04 and L6P-F10, round 4) | Change |
|---|---|
| L6P-F04: R97 drafted at 1 % where the analysis relies on 0.1 % | the draft's R97 is 28.0k 0.1 % 25 ppm/K, YAGEO RT0603BRD0728KL (code owed); the record's INP divider is taken at 0.1 % (TOL_INP) and prints it; a test asserts the draft's tolerance equals the record's; INP reads 17.66 V at the floor against 18 V (holds from 3.25 uH) and U21 turns on at 9.16 V at the most |
| L6P-F10: PV_F's 80.6 V judged against the absolute maximum less 10 % | the basis stated: the 90 V line is the exclusion line (an absolute rating only excludes); the TPS4811-Q1's RECOMMENDED operating row for VS, CS+ and CS- is 80 V (SLUSEE5E 6.2), which the floor's 80.58 V exceeds: OPEN on the guard, under the row from 3.44 uH, carried in R-176 row 3 and B6-ENG-1; no part change made (a larger port bank is the bounded candidate, not tried at the desk) |

| Item of the engineering collaborator's targeted recheck of set 27 (astra-check-l4close-2.md: B6 / L4-F01, the B6-ENG-2 model defect, the first MINOR; round 5) | Change |
|---|---|
| B6 / L4-F01: the 3.30 uH "passing floor" overclaimed; a connector fault credited the lead's 36.3 mOhm | the envelope's connector case takes zero lead resistance (no source resistance is bounded) and every evaluation runs both fault positions; round 2's 3.30 uH is kept only as the reference loop and WITHDRAWN as a passing floor wherever it stood (D-10's text, R-176 row 3, B6-ENG-1, the approaches table, the verdict row); the pins' complete budget there, both polarities, is stated: -0.3021 to +0.2591 V at the connector, -0.2884 to +0.2486 V at the far end, against +-0.240 V (the connector case's negative excursion beyond the -0.3 V absolute maximum); with the connector case INP reads 18.29 V at that loop, over the 18 V margin line (inside 20 V; it holds from 3.58 uH), and PV_F 83.47 V against the recommended 80 V row (under it from 4.03 uH); no search for a passing inductance was made; the complete stage question goes to the engineer with that budget |
| B6-ENG-2: sense_ripple kept negative monitor current | the model now produces no monitor current for a negative differential (8705af p.31) and clips at 100 uA above 100 mV: the monitor's average at the 25 V corner reads +7.9 % at the regulation's highest current (positive: high, the limit then regulating below its setting), -10.2 % at the trip's; stated as MODELED with that qualification; the unconditional "no damage" consequence is withdrawn: the 10 ns edge sensitivity reaches -0.4329 V at the pins, a possible stress named; the operating-range exceedance stands |
| Consequence of the corrected envelope on the cold connection (D4) | with no lead resistance credited at a connector fault, the cold ring near 0.30 uH takes PV_F's slew to 56.1 V/us against the 54 V/us margin line and INP to 18.54 V against 18 V, inside the 60 V/us and 20 V absolute ratings; D4's verdict becomes NOT MET on the margin lines there (the margins hold from 0.53 uH; round 2's far-end case still holds them); stated, not re-opened otherwise |
| MINOR: R96 drafted at 1 % while both divider resistors are taken at 0.1 % | the draft's R96 is 100k 0.1 % 25 ppm/K, YAGEO RT0603BRD07100KL (code owed), the same series as R97; the test reads both resistors' tolerances from the draft and asserts each equals the record's TOL_INP |

| Item of the consolidation review's B6 (`astra-check-l4close-1.md`, set 27) | Change |
|---|---|
| The guard's already-on over-voltage transient was not bounded (L4E7-CONTROL-DECISION.md's turn-off row; the script's turn-off predicate) | One loaded-network transient (`guard_event`, MODELED): a stiff 36 V source through the 0.0465 Ohm lead (0.0363 Ohm at the cold end, used) and its inductance stepping onto the port from every state the guard is on in, rising at 0.01 to 10 V/us, and connected cold; C131 and C132, the bulk with its ESR at three corners, D4 and D11 at both ends, U21's latest OV and short-circuit delays and the gate's fall, the stage's input; every node against its printed rating with its margin (THE GUARD ALREADY ON). The turn-off predicate is replaced by these ratings |
| The lead's inductance, its value and source | Printed nowhere: a1solar leaves the lead unspecified, and the two-wire value is zero for bare conductors touching. Classified as unprinted; each rating stated with the least inductance it holds at; the binding one, U5's positive differential, at 2.47 uH (conductors 4.21 mm apart); the verdict CONDITIONAL on R-176's measurement |
| If NOT MET, the smallest change | NOT MET as drafted (PV_F 102.1 V, its slew 397.7 V/us, INP 29.07 V, U5 0.4218 V at 2.47 uH): C131 and C132 two 10 uF 100 V (faster turn-off energy absorbed at the port), C133 and C134 two 10 uF 50 V ceramics ahead of D4 on PV_P (more input capacitance ahead of D4), C126 330 pF (a faster short-circuit path) and R97 30.0k (INP's 20 V); each shown necessary by reverting it alone; D4's rating unchanged (it never conducts) |
| R-176's zero-current acceptance | Revised: the lead's inductance measured; the source connected cold (no current in Q12 or D4) and stepped on with the guard on (Q12 off at most 76 A within 11 us, D4 nothing, PV_P under 31.80 V, U5 within +-0.3 V); the C126 nuisance-trip row |
| CS115's 5 A is a calibration level | Carried consistently: CS116 MEETS; CS115 MEETS with the block off and is CONDITIONAL with it on, on R-174's recorded loop current (under 15.68 A) or U5's measured differential (under 0.3 V; 0.2123 V is the conservative CS116 screen); the verdict table, the remedies' verdicts and the text for L4-E9's D-12 say so |

| Item of the owner's amendment of 2 October 2026, item 3 (the solar-fault remedies) | Change |
|---|---|
| A selected remedy for each open defect, its circuit changes | Three implementations compared on held sheets; selected: the TPS48110-Q1 over-voltage cut-off (U21, Q12) for the 36 V source and a CSD19532Q5B return switch (Q13) for the reversed panel, with D11, C131 and D4 to the SMCJ30A (C131 and C132, C133 and C134, R97 30.0k and C126 330 pF since B6); drafted in `apply_gen_sch_e_solar_guard.py` |
| A bounded analysis against the fault exposure and the ratings | The 36 V source, the reversed panel, CS116 and CS115 with the block on and off, the turn-off against D4 and the bulk (replaced by B6's transient), the loss and its energy: each with its margin |
| The interfaces and calculations, the charger and the backstop | The backstop (the slew's bank current), CS101 re-run (0.0591 A against 0.1130 A), check (b) re-run (1.021 ms; 0.670 ms since B6), the static bound (93.5954 W; 93.5957 W since B6), the LT8705A, the BQ25730 (no coupling), TRN-001's port table; what stays valid named |
| The window kept, protection never extending the range | The cut-off over 25 V and CS101's peak, falling back over 25 V, under every rating; above it the stage off; the gap from 25 V to the cut-off named as a residual |
| L4-E9's input (its 0.4 V margins) | Verified on the sheets: with the SMCJ28A, 0.275 V new and -0.282 V aged: NOT MET, which is why D4 becomes the SMCJ30A |

| Item of the coordinator's surge round (the findings ledger's item 1: L4-E7R's checks 1.6 and 2.4; `checks/astra-check-l4e7r-2.md` B6 R5) | Change |
|---|---|
| The record stopped at "no level is ruled" and took D4's own pulse rating as a capability scenario | The panel lead's disturbances derived from the exposure (the 5 m lead the records give, unshielded, on the ground, no earth bond) and the basis the requirements commit to (MIL-STD-461G's Ground, Army row: CS116 and CS115 marked A, CS117 S and not taken; A.5.15's nearby-lightning statement); the sustained sources (the panel's cold open circuit, a stiff source of the kit's declared range, a reversed panel); each judged by REQ-016's own criterion with the part's tolerance and its typical temperature coefficient, the energy into D4, U18's limits and U5 in the loaded network from the cold end; the D4 capability rows kept as the margin beyond the basis |
| For a NOT MET, the smallest change | A 36 V source: SMCJ36A with the entry's 63 V class parts (EEHZA1J220XP for the bulk), or the over-voltage and reverse disconnect that also closes E-N1; register rows for L4-E9 (R-156's input, a CS116 and CS115 test row, the change), not drafted (no catalogue reading filed, no one contacted) |
| The statements resting on "no level is ruled" | Check (c)'s derivation and bullet, the decision table, the Vishay draft's closing sentence and its pulse wording, the README |

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
