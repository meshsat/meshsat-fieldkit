accepted: no

# CHECK-1 of fnd/l3feas: the Layer 3 feasibility record (stream l3feas, MESHSAT-1357)

**An AI check, not a qualified review.** 30 September 2026, 13:02 CEST.
- **The branch** is `fnd/l3feas`, tip `24942a5fed1936b01b569b4ac319ae0bc8265e6b` (confirmed). It is two commits,
  `231b59db` and `24942a5f`, on main `8fec0733`.
- **The files** are all in `v2/docs/records/l3feas/`:
  - `L3-FEASIBILITY.md`, sha256 `27a2b3b4...`;
  - `hf_wab.py` `22d7d495...` and `hf_wab.out` `175dc3e1...`;
  - `solar_interface.py` `d38df87f...` and `solar_interface.out` `7f8dbcd5...`.
- **The clone.** A `--no-local --single-branch` clone (`_scratch/chk-l3feas1`, removed after the check), with
  `int17-evidence-de11cc4e.tar` extracted and int16's held sheets added. All of them are ignored files: `git status`
  stayed clean.
- **The author** is the energy basis author. The checker wrote none of it. Prototype design: nothing is built, bought,
  powered or measured.

**What the checker used.**
- **Its own balance:** `indep_l3feas.py` beside this file, output `indep_l3feas.out`. It uses the checker's
  `indep_balance.py` and `indep_round2.py` from `../chk-energy/`, and imports no record script. The array ratios are
  a1solar's inputs, and U3's efficiency at 6.25 and 6.191 A is bracketed.
- **The makers' pages read:**
  - BQ25731 SLUSE66A 9.3.5 (p.25), Table 9-1 (p.26), 9.3.6, Table 9-4 (p.27) and 9.6.22 (p.80);
  - LT8705A 8705af pp.2, 11 and 12;
  - the held Renogy sheet.
- **The netlists:** board A (`6c40250c`) and board E (`2ed95a0e`).
- **The records:** TOPOLOGY.md 3c, REQUIREMENTS-TRACE (REQ-002, REQ-014, REQ-072, REQ-075), and a1solar
  `array_calc.out` and `ARRAY.md`.

## Blocking item

### B1. Route R1 raises the current through R11, and the Kelvin criterion it rests on is left at the drafted 6.2 A value

R1's front-end margin, +0.224 A (+0.205 A with four FETs), is stated "with Kelvin taps on R11 (r11dep C-1)". C-1's
criterion is the one CHECK-3 to CHECK-5 accepted for the drafted setting: at most 0.371 mOhm of shared copper at working
temperature, 0.29 mOhm at 25 C, for 6.415 A through R11.

R1 puts 6.569 A through R11 (6.588 A with four FETs). The same stack (R11 at its 6.2855 mOhm maximum, 42.7 mV) then
allows only:

| Current through R11 | Copper, working temperature | At 25 C, copper at 100 C | At 25 C, copper at 62.1 C | Bench figure at 6.0 A |
|---|---|---|---|---|
| 6.569 A (0.060 A of other loads) | **0.215 mOhm** | **0.166 mOhm** | 0.188 mOhm | about 1.0 mV |
| 6.588 A (four FETs) | 0.196 mOhm | 0.152 mOhm | 0.171 mOhm | about 0.9 mV |

**Counter example.** A layout that closes C-1 exactly at its stated 0.29 mOhm (25 C) senses 43.76 mV at 6.569 A with the
copper at 100 C. That is over the 42.7 mV minimum, so the front end can limit first and R1's gain is not assured.

Section 1c's path to disposition (a) lists U3's minimum, the three efficiencies, and "the corrected path's corrections,
closed as r11dep lists them. R1 adds the bank's in-service case to B-4". It does not add R1's tighter Kelvin criterion,
so it would admit R1 on evidence that does not support it.

**Needed:** state C-1's criterion for R1: at most 0.215 mOhm working, 0.17 mOhm at 25 C (0.15 mOhm with four FETs).
Add it to 1b's "front-end limit margin" and to 1c item 3, beside the bank.

## Minors

1. **O-1 has no closure criterion.** O-2 to O-7 each have one. O-1, pinning the panel revision, is named in 3a but closes
   on nothing. Suggested: the maker's sheet for the revision actually bought is filed with its revision mark and sha256,
   and a1solar's ratios, the 34.29 V set point and the voltage basis are re-run on it.
2. **The (c) trigger is stated per input alone** ("charge efficiency under 0.936 (0.947), or stage and front end under
   0.911 (0.925)"). The thresholds are each input alone with the others at the route's values, and inputs combine: a
   measured stage above 0.93 offsets a charge figure under its threshold. State (c) as a re-run of the combination on all
   the measured values (R1 and R2 together included), finding no route that meets.
3. **"The kit-level line ... is met by R1 and R2 on the model"** (1a) covers only conditions 1 and 2 of section 2's line.
   Condition 3 is INFERRED and condition 4 is NOT ESTABLISHED. Say so where the word "met" appears.
4. **R1 moves the stage's in-service input from 154.9 W to 158.6 W** (6.569 A at 20.887 V, over 0.93 twice). That
   deepens REQ-016's already open exceedance (at most 100 W into the stage), which is the owner's. Name it beside "No
   approved requirement moves".
5. **The basis of the 6.35 A setting needs precise citation.**
   - SLUSE66A 9.3.5's sentence covers RAC and RSR both at 10 mOhm, but board A has RSR 5 mOhm (R17).
   - Table 9-1 (p.26) has no row for board A's 4.7 uH (IADPT 191 k, Table 9-4).
   - The setting stands on 9.6.22 (p.80: with 10 mOhm, "50 mA to 6350 mA ... implemented through DAC clamp", no
     inductance condition) and on 6.35 A in every RSNS_RAC=0b row of Table 9-1. Cite those.
   - Also state that ILIM_HIZ does not bind (9.3.6: "the lower setting of IIN_DPM and ILIM_HIZ pin"). At REGN's 5.7 V
     minimum the R19/R20 divider gives 3.87 V, about 7.2 A, above the setting's 6.509 A maximum; above 4.0 V the pin is
     disabled.
6. **"The 60 V ceiling" is unlabelled** (3a, 3b). It is the coordinator's safety-extra-low-voltage ceiling, and a1solar
   says "the standard behind it is not held". Label it so beside the 61.0 V finding.
7. **The page citation is short by one page.** CSNOUT's "Connect this pin to VOUT when not in use" is on 8705af p.11;
   CSPOUT, CSNIN and CSPIN are on p.12. Cite pp.11 and 12.

## What holds

**Task 1.**
- **The reference.** 4S14P WAB at WE is NOT MET by 10.8 Wh (the checker 10.7 Wh); the kit stops at hour 71 (UTC 05)
  from 06 UTC and at hour 60 from 18 UTC.
- **The routes**, recomputed on the checker's balance:

  | Route | TYP | WAB |
  |---|---|---|
  | R1, U3 minimum 6.25 A | 70.6 to 70.9 (base 48.8, lid 17.9) | 19.2 to 19.8 Wh (the author's 19.4) |
  | R1lo, 6.191 A | 62.2 | 7.4 Wh (7.5) |
  | R2, stage 0.965 | 69.4 | 12.7 Wh |

  Every route keeps STOP and COMB, and fails EACH at WAB.
- **Thresholds, identical:**
  - R1: charge 0.932 / 0.936, stage 0.906 / 0.911 (STOP / COMB);
  - R1lo: 0.943 / 0.947 and 0.919 / 0.925;
  - WE: 0.960 / 0.964 and 0.946 / 0.952;
  - U3's least minimum on COMB at the drafted setting: 6.173 A (the author's 6.174).
- **Timing.**
  - U3's cap binds UTC 09 to 14, 18 of 72 hours; it rises from 116.8 to 119.7 W.
  - R1's gain is 29.9 to 30.2 Wh.
  - The lid is at its line at UTC 05 (hour 71 from 06; hours 59 and 60 from 18).
  - The base's lowest is 19.2 to 19.4 and 20.9 to 21.0 Wh.
  - The largest hour into the stage is 194.2 W (TYP) and 178.6 W (WAB), so the 200 W window never binds.
- **R1 against the electrical record.**
  - U3's maximum is 6.509 A.
  - Through R11: 6.569 A, or 6.588 A with four FETs.
  - Margins: +0.224 A and +0.205 A.
  - Bank worst can: 2.43 A matched (86.8 %), 2.81 A at 2:1 (100.4 %).
- **The 6.35 A clamp is a real register setting** within 10 mOhm sensing (see minor 5). It changes no charge-current
  setting, so REQ-075 and REQ-002 hold, as do the array, the installation and REQ-072's day, load and duration.
- **Disposition (b) is right.**
  - Not (c): a route meets on the model at both readings of U3's minimum.
  - Not (a): at 6.191 A the margins over undocumented figures are 0.3 and 0.5 points on COMB, the whole result is case
    (iii), HYPOTHETICAL, and U3's minimum is INFERRED.
  - The quantified trade-off rows are the energy basis's own and are not proposed.

**Task 2.**
- The table's elements and labels check against their sources:
  - REQ-072 reads "starting from a full, aged pack (REQ-014)"; REQ-014 gives +20 C;
  - POWER-THERMAL gives 33.1 / 42.8 / 82.8 W for PS-IDLE-SPEC;
  - CONOPS 4c's line is per cell;
  - TOPOLOGY.md 3c holds the host rule ("turns the lid path off when the lid reaches it, and shuts the kit down when the
    base reaches it"), the join rule (0.20 V, 2.5 A) and the path defaulting ON;
  - the LM5069 limit is 48.5 / 55 / 61.5 mV over 5.6 mOhm = 8.7 / 9.8 / 11.0 A;
  - PS-IDLE-SPEC is 42.8 W / 13 V = 3.3 A.
- Established, assumed, drafted, modeled and inferred are labelled correctly, and the join is plainly a DRAFT ("None is
  drawn in a generator").
- **The pass line follows from the drafted join.** Conditions 1 and 3 need one pack to carry when the other is at its
  line, which the join provides within the LM5069's 8.7 A minimum. Condition 4 is honestly NOT ESTABLISHED.
- 12.0 V at 4S is the balanced-cell case. The per-cell line triggers at or above it, so condition 4 at 12.0 V is the
  conservative reading.

**Task 3.**
- **The held sheet.**
  - sha256 `8891821cf70f4124fdb1f02e2fbc7a4a0f4102c51f33ad39c2bfa32e6b60a29f`, tracked, 2 pages, title "RNG-100DB-H spec";
  - created 2018-08-17, modified 2020-08-06 (UTC-7 stamps);
  - no revision mark in its text layer;
  - a retailer's copy (the thdstatic URL in `sources.txt`).
- **Its figures, as read:** 22.5 V, 5.75 A, 18.9 V, 5.29 A, 15 A series fuse, 600 V system voltage, 1219 x 549 x 2 mm,
  -0.42 / -0.31 / +0.05 %/K, NOCT 45 C.
- **The current revision** is compared and not substituted, as the owner required.
- **The derivations, identical:**
  - cold Voc 51.28 / 54.07 / 56.25 V (held), and 55.61 / 58.63 / 61.00 V (the current page's 24.4 V);
  - Isc 5.75 / 5.88 / 7.35 A a string and 11.50 / 11.76 / 14.70 A for the array;
  - F2 1.25 x 14.70 = 18.37 A, so 20 A;
  - 475.6 W at -20 C, 594.5 W transient, and 329.9 W as in `array_calc.out`;
  - the stage ceiling 308.0 W out and 331.2 W in.
- **The converter input is not controlled as drawn: confirmed.**
  - On the netlist, U5 pins 30 and 31 (CSNOUT, CSPOUT) are on TRK_OUT with pin 29, and pins 32 and 33 (CSNIN, CSPIN) are
    on PV_P with pin 34, VIN. No sense resistor sits between them.
  - The maker's text reads "Connect this pin to VIN [VOUT] when not in use".
- **The back-feed path (c) is traced correctly on board E's netlist:**
  - Q2 has its drain on VIN_RAW and its source on TRK_OUT, gated by the LM74700 U4;
  - Q6 (M4) runs from TRK_OUT to TRK_SW2;
  - L1 sits between TRK_SW2 and TRK_SW1;
  - Q3 (M1) has its body diode from TRK_SW1 to PV_P;
  - F2 runs from PV_IN to PV_P;
  - J_SOLAR is a JST-VH 10 A.
- **String against combined-feed protection:**
  - (Np - 1) x 7.35 A is under 15 A, so no string fuse is needed;
  - F2 is in the combined feed;
  - the argument for the remaining string after one disconnects is sound, and rests on O-4.
- **The obligations.** O-2 to O-7 each carry a closure criterion; O-4 closes by filing (O-1: minor 1).
- **Section 3c separates approval of the topology from verification**, as the reviewer asked.

**Hygiene and reruns.**
- `hf_wab.out` and `solar_interface.out` rerun byte identical at the tip.
- The added lines carry no U+2013 or U+2014, no host names and no user paths.
- Nothing under `v2/ecad/` or `v2/vendor/` changed, so `pcb_requirements.yaml` is untouched and no held file is
  committed.
- Both commits are in the owner's name with no trailer.

## Figures beside theirs

| Figure | Theirs | Checker |
|---|---|---|
| 4S14P WE WAB | NOT MET, 10.8 Wh; stop at hour 71 | NOT MET, 10.7 Wh; stop at hour 71 (UTC 05) and hour 60 |
| R1 (6.25 A) TYP; WAB | 70.7 (48.8, 18.1); 19.4 | 70.6 to 70.9; 19.2 to 19.8 (U3 0.9730 to 0.9733) |
| R1lo (6.191 A) TYP; WAB | 62.3; 7.5 | 62.2; 7.4 |
| R2 (stage 0.965) TYP; WAB | 69.3; 12.7 | 69.4; 12.7 |
| R1 gain; cap; cap hours | 30.2 Wh; 116.8 to 119.7 W; UTC 09 to 14 | 29.9 Wh; 116.8 to 119.7 W; UTC 09 to 14 |
| Thresholds R1 / R1lo (charge COMB, stage COMB) | 0.936, 0.911 / 0.947, 0.925 | 0.936, 0.911 / 0.947, 0.925 |
| U3's least minimum at 6.2 A, COMB | 6.174 A | 6.173 A |
| R1 margin, 0.060 / 0.079 A | +0.224 / +0.205 A | +0.224 / +0.205 A |
| R1 Kelvin budget | not restated (C-1's 0.29 mOhm at 25 C) | 0.215 mOhm working, 0.166 mOhm at 25 C (0.152 with four FETs) |
| Bank in service at R1, 2:1 | 100.4 % | 2.81 A, 100.4 % |
| Stage input in service at R1 | not stated | 158.6 W (154.9 W at 6.2 A) |
| Largest hour into the stage | 194.3 / 178.6 W | 194.2 / 178.6 W |
| Cold Voc, held; current page | 51.28 / 54.07 / 56.25; 55.61 / 58.63 / 61.00 V | same |
| Isc string / array; F2 | 7.35 / 14.70 A; 18.37 so 20 A | same |
| Stage ceiling | 308.0 W out, 331.2 W in | same |

Rerun from this folder against a checkout of the tip with the evidence archive and held sheets present:
`python3 indep_l3feas.py <checkout>` (it uses `../chk-energy/indep_balance.py`, `indep_round2.py`,
`indep_grid_weather.py` and `dayratios.json`).
