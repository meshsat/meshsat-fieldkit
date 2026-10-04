# L9T5: C-ALLTX rev 2 and C-DEV rev 1, the uncertainty, three approaches and the selection (task T5, MESHSAT-1357)

4 October 2026, Layer 9's power author, worktree `l9t5` on branch `fnd/l9t5` from set 29's line `dc99897f`. **Status: a desk
selection, not reviewed, nothing drafted.** Prototype design: nothing in this kit has been built, powered or measured, and no
figure on this page is a measurement. Every figure is printed by `l9t5_case.py` into `l9t5_case.out` ("out N" is its section),
which takes the case row from record l9pwr's budget (round 4, its out 7b) and every maker's figure from its pinned sheet. Labels:
PRINTED (a maker's limit), TYPICAL, MODEL, ASSUMPTION, MISSING. Case rows cited by id: **C-ALLTX rev 2**, **C-DEV rev 1**
(`inputs/coordinator-cases-2026-10-04.md`); the collaborator's challenge cx40 (`inputs/astra-challenge-f01-1.md`) is an advisory
AI review and accepts nothing. The owner's standing decisions of 4 October hold: FAN_OK is rejected and not revived; REQ-018's
15.5 V, the 60 s key-down, the 18 A service, the pack and every protection stay.

## 1. The budget defect, corrected (record l9pwr round 4)

- **C1:** rv-pwr's PS-ALLTX powered the standby WiFi card (1.0 W PLAN, 9.1 W HIGH); REQ-018's acceptance and CONOPS 4a's row
  define the state with it off. The raw PS-ALLTX HIGH row on DRAFTED goes from **276.373 W (17.4792 V)** to **265.274 W
  (16.8626 V)**; PS-ALLTX at the pack from 174.23 / 209.89 / 292.03 W to 174.23 / 208.47 / 279.63 W.
- **Out 7b of the budget computes C-ALLTX rev 2 from its text**, each pack-fed converter at the VBAT the case sets (13.391 V at
  18 A; the budget's convention had been rv-pwr's 16.8 V).

## 2. The case row (out 1)

| | W | |
|---|---|---|
| the cells' EMF at 18 A from 15.5 V rest | 279.000 | |
| the cells, R_cell 0.060 Ohm (ASSUMPTION), 0.0800 Ohm | 25.920 | MODEL |
| the pack path, 0.038064 Ohm | 12.333 | R_DIST 7.290, R17 1.620, the breaker 1.140, the battery FETs 2.283 |
| **the allowance at VBAT** | **240.747** | the challenge's 240.747 W, reproduced |
| the load pins | 220.741 | |
| conversion | 20.298 | the 5.1 V LM5176 stages 9.160, the PA and HF stages 2.245, LDOs 1.229, the fans' converters 2.997, the rest 4.667 |
| **the case at VBAT** | **241.039** | |
| **the deficit** | **+0.292 W, +0.0162 V** | **needs 15.5162 V rest at 18 A** |

**The row's quoted figure is not its text.** "On Layer 9's final drafts this case needs 16.214 V rest (253.61 W at VBAT)" is
D-11's basis on rv-pwr's `typ_nontx` (16.2145 V, 253.608 W), which puts only the compute modules and the NVMe at typical. The
row's text puts every other non-transmit load at typical too; the loads that differ are listed in record l9pwr's out 7b (the
supervisors, the hubs' cores, the QMX's USB and HDMI, board E's controller, the Geiger). This page computes the text and keeps
the basis beside it as a labelled scenario; **a revision of the row is the coordinator's**.

## 3. The uncertainties the row names (out 2)

| Item | Label | Its bound | Needs |
|---|---|---|---|
| U1 the gauge's indication against the indicated 18 A (BQ4050 SLUSC67B 6.14: gain error 0.8 % FSR, INL 22.3 LSB, offset 10 uV, drift 150 ppm/K; R10's 1 % an ASSUMPTION) | PRINTED and ASSUMPTION | 0.7988 A one-sided uncalibrated (the gain error alone 0.4860 A, the challenge's figure); 0.1688 A calibrated | 16.0512 V; 15.8348 V; 15.6245 V |
| U2 R_cell (35E Ver. 1.1 7.4 prints 35 mOhm INITIAL AC only) | ASSUMPTION | the row covers 0.0593 Ohm | 15.7562 V at 0.070, 15.9962 V at 0.080 |
| U3 the path (the dock's contacts at their printed 20 mOhm are 10.0 mOhm forward and return, against W2's 9 mOhm inferred for every lead and contact) | PRINTED and MISSING | +1.0 mOhm at least; 18.0 mV a mOhm | 15.5342 V |
| U4 the PA stage at 13.8 V and the 5.1 V stages' 0.90 | NOT PLOTTED | the PA at 0.95; the 5.1 V stages at 0.85 | 15.7479 V; 15.8190 V |
| U5 the rest voltage's fall during the 60 s (0.30 Ah, 2.99 % of a cell's 3.35 Ah) | MISSING (R-214) | no curve held | not bounded |

**Combined**, U1 uncalibrated with U3 and R_cell 0.060 Ohm: 241.168 W at 17.2012 A, **needs 16.0684 V (+0.5684 V)**; with R_cell
0.070 Ohm and U4's lower efficiencies also, 16.8498 V. The printed gauge bound alone moves the case further than its deficit.

**Labelled scenarios (out 3):** the compute modules at 8 W, 252.840 W and 16.1718 V; D-11's basis at the case's VBAT, 253.032 W
and 16.1825 V.

## 4. Three service-neutral approaches (out 4)

| | What it changes | The case with the printed bounds (U1, U3) | Touches | Evidence owed |
|---|---|---|---|---|
| **A1** the VHF PA held to its 30 W service by its maker's own output control | a forward-power detector and a VGG loop on board D (today VGG is set open-loop to 4.30 to 4.68 V, so nothing holds Pout under the module's 45 W rating; the budget's 113 W is 45 W at the printed minimum 40 %) | at +-0.25 dB the PA 84.15 W: 14.3465 V; at +-0.5 dB 94.42 W: **14.9585 V**; at +-1 dB 118.87 W: 16.4195 V (fails) | board D, Layer 5's PA contract, the PA's RF checks; L9P-F04 closes with it | the module's drain current at the loop's high end at VDD 13.8 V (the maker prints 40 % at 30 W only as its heat-sink design condition at 12.5 V, IDD 0.84 + 5.16 A, 75.0 W); the detector's printed accuracy |
| **A2** the pack path's resistance | copper, contacts, a fourth battery FET | the whole path is worth 0.6852 V; the nominal deficit is 0.901 mOhm; the printed bound needs 33.047 mOhm, more than the path can lose | boards A, E, P, the energy chain | the leads' and bands' resistance (MISSING) |
| **A3** the LDO-fed rails onto bucks | the supervisors, the KSZ's 2.5 V, board E's 3.3 V | 15.4674 V nominal; 16.0173 V with the bound | boards B and E, the supervisors' supply | the bucks' points (NOT PLOTTED at 3.3 V) |

**T6's copper in volts:** the two options carry the same section (2.74 mm2 a band: 39.14 mm a face at 1 oz, 19.57 mm at 2 oz),
so either is worth 0 V against the other as sized; each 100 mm of band, forward and return, hot, is 1.582 mOhm, 28.5 mV at 18 A
(MODEL); the lengths are the layout's. A fourth BUK6Y10-30P is worth 31.7 mV (and Ciss, E11-37). The 5.1 V stages' efficiency is
not an approach: no maker figure supports a better one.

**A1's acceptance (the loop's accuracy binds):** half-tolerance at most 0.5 dB over temperature closes the case with the printed
bounds (R_cell to about 0.084 Ohm); at most 0.25 dB also covers the 8 W modules (15.0314 V), D-11's basis (15.0425 V) and R_cell
0.080 Ohm with U4's lower efficiencies (15.3067 V).

## 5. C-DEV rev 1 and L9P-F04 (out 5)

The case: U7 at 7.4717 A at 4.9019 V (every load at constant power) against 7.0957 A (R43 6 mOhm at +1 %, VSNS 43 mV); the loop's
highest 9.5960 A against J_5V_DEV's JST-VH 10 A.

- **(a) a re-rated path:** R43 at most 5.6981 mOhm supplies the case and at least 5.7576 mOhm keeps the loop's highest at 10 A:
  no value does both (the challenge's Q4, reproduced). It needs a single contact over the loop's highest and a lead whose rating
  covers it; **the lead's rating is not held**.
- **(b) the load split:** the three supervisors' LDOs (U40, U50, U60, board B) move from +5V_DEV to a new always-on 5.1 V buck on
  board A (a TPS62933, 3 A PRINTED, high-side limit 4.2 / 5.0 / 5.8 A PRINTED) on its own JST-VH lead. U7's case becomes
  **6.0359 A against 7.0957 A (+1.0598 A)**; the buck carries 1.4358 A; its limit stays under the lead's 10 A.
- **SELECTED (SESSION): (b)**, every figure printed, U7's limit and lead unchanged. Its condition: the buck follows RAIL_EN as U7
  does (L4-E11's U46 hold), so the supervisors are up whenever +5V_DEV is.
- **L9P-F04:** the PA rail at 8.1884 A against U13's 7.0957 A; with A1 at +-0.5 dB or tighter it is 6.842 A or less, no shunt or
  lead change.

## 6. The selection

- **F01 / D-17: A1** (SESSION, within authority: no requirement, money or claim changes; the kit's VHF stage is a 30 W stage).
  It is the only one of the three that closes the case with the printed bounds. **CONDITIONAL** on the PA's bench row and on a
  detector whose sheet prints the loop's accuracy; **not drafted** (no detector part is held, the loop is not designed). No
  owner decision is needed.
- **I-03: (b)**; **L9P-F04: with A1.**
- **For C-PROT (record l9stk's, reported only):** the gauge's uncalibrated one-sided error (0.7988 A) exceeds the 0.32 A between
  the 18 A service and the breaker's least limit 18.32 A; an under-reading gauge lets the true current reach that limit while it
  indicates under 18 A. Calibrated (0.1688 A) it is under the gap.
- **Open:** F01 / D-17 and I-03 until a draft composes with its board's pending drafts, its nets are read in the regenerated
  netlist with a mutation that fails, its acceptance holds on its case, and the collaborator's targeted check (V3) reads it;
  U5 (R-214); the PA's bench row; the case row's quoted figure.

## 7. Reproduce

`python3 v2/docs/records/l9t5/l9t5_case.py` from the repository root (stdlib, PyYAML, pdftotext; it imports record l9pwr's budget,
pinned). The output is regenerated only through `_bin/regen_out.py`, after record l9pwr's. Test: `v2/ecad/tools/tests/test_l9t5.py`.
