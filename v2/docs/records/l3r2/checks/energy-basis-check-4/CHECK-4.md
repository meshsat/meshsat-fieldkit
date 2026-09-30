accepted: yes

# CHECK-4: energy round 4 and r11dep's second issue against CHECK-3 and the owner's corrections (MESHSAT-1357)

**An AI check, not a qualified review.** 30 September 2026, 04:23 CEST. Branch `fnd/l3plane`, tip `06b8ecea` (confirmed),
on `3ef5987e` and the prior tip `4e9fa869`. **Scope: `git diff 4e9fa869..06b8ecea` only**, against CHECK-3 (B1, B2,
minors 1 to 7, section 7) and the owner's three corrections of 30 September. The checker wrote none of it. Prototype
design: nothing is built, powered or measured.

**How it was checked.**
- **The clone.** A shared clone at the tip (`_scratch/chk-energy4`, removed after the check), with the int16
  worktree's held files copied in as ignored files, never committed.
- **What was read:**
  - the diff, and `R11-DEPENDENCY.md` whole;
  - `r11_dep.out` sections 1 to 6;
  - `three_cases.py` and its `.out`;
  - the changed parts of `ENERGY-BASIS.md`;
  - board A's netlist (sha256/16 `6c40250c47195ebb`, unchanged);
  - `gen_sch_a.py` (the bank note at lines 697 to 720; the restart latch at lines 783 to 822);
  - LM5176 SNVSAI1D 7.1;
  - the requirement sentences of REQ-015, REQ-016, CON-006 and REQ-019.
- **The checker's own figures:** `indep_round4.py`, output beside it. It runs on the checker's balance with a new
  collapse switch, and imports no record script.

## Blocking items

None.

## Minors

1. **The derated setting closes by 1 mA on the carried load figure.** 4.05 A clears the stacked minimum by +0.001 A on
   0.060 A, and misses it by -0.018 A on C-9's four-FET 0.079 A. 4.00 A clears both (+0.052 and +0.033 A).
   - A-1's correction names 4.05 A first, and 7a.2 says "4.05 A, or 4.00 A".
   - State 4.00 A as the setting that closes whatever C-9 finds, or state that 4.05 A holds only if C-9 closes at 0.061 A
     or less.
   - The energy variant is unaffected: it fails M1 at either setting.
2. **B-1's 5.20 A is an input current, not a setting.** The page reads "At 9 V, U3's input at 5.20 A keeps the peak at
   90 % of Isat"; `.out` 6 makes clear it is U3's actual input. A register written at 5.20 A lets U3 reach 5.33 A (2.5 %),
   and then the peak is 16.06 A, 91.8 % of Isat.
   - The schedule's setting at 9 V is 5.05 A (the 50 mA step at or under 5.20 / 1.025 = 5.073 A), whose maximum is 5.18 A
     (15.68 A, 89.6 %).
   - The figure also rests on the typical 25 C Isat. B-1's closure already defers to C-5; say that 5.20 A is recomputed
     there.
3. **The collapse bound's pessimism has two more sources, and one exception.** The bound, "a collapsed hour delivers
   nothing", is pessimistic for more reasons than the packs being full.
   - **The restart latch.** It restarts the front end once VBUS20 is bled (gen_sch_a.py: "a dip under 8 V interrupts
     charging for about 1 to 2.5 s").
   - **U3's reset.** U3 resets IIN_HOST to 3.25 A at every VBUS removal (SLUSE66A 9.6.22; FW-A16 (b)), so after a collapse
     it asks 65 W until the host rewrites it.
   - **The exception.** On real weather, a sub-hour dip inside an hour whose mean clears the cap can also collapse the bus.
     So on the series the bound is a bound on hourly means, not a strict one.

   The framing, INCONCLUSIVE between two stated bounds, is fair. These three sentences belong beside it.
4. **A-2 is an existing defect of the E1 setting, not of the hardware alone or of FW-A16 as written.** It is classified
   (a) and labelled INFERRED. That is defensible: the netlist fixes the structure, with no input-power bound and U3's
   VINDPM on the regulated VBUS20 (U3 pin 1), and the makers fix the behaviour:
   - LM5069 current limit;
   - LT8705A input regulation, "VC will be reduced";
   - the tree's own FW-A16 and gen_sch_a.py note name the collapse for the vehicle entry.

   The heading reads "Confirmed". Word A-2 as "established from the netlist and the makers' documented behaviour (the
   mechanism INFERRED); 7b.7 confirms it". The page already says FW-A16 as written bounds it and E1's fixed setting does
   not.
5. **B-2's "an input-side limit at low VIN_RAW" names no mechanism.** The LM5176's one average loop senses input OR output,
   and R11 is needed on the output. A firmware schedule does not bound the fault B-2 is about, since U3's DAC clamp keeps
   firmware under 6.45 A. The concrete engineering forms are hiccup (partial, as the page says) or FETs and cooling for
   the fault, for example FETs in parallel. The page is honest that the CON-006 or REQ-019 question arises only if no
   fitting part exists. Say that the fit of B-2's and B-4's remedies on board A is not yet shown.

## What holds

**1. B1, the bulk capacitors: the author's method is right, and so was CHECK-3's.**
- **The shared basis.** Both scale the generator's per-can figures in proportion to the front end's current. That is
  right physically: the output ripple and U3's input pulses are both proportional to it.
- **The two points agree within their rounding.** 5.7 A gives 0.3684 and 0.4263 A a can per ampere; 5.0 A gives 0.3700
  and 0.4280. The difference is inside the generator's two-decimal rounding (±0.005 A on 1.85 A is ±0.27 %).
- **The author's choice.** Taking the steeper point is the conservative choice. Its figures reproduce: in service 2.37 /
  2.39 / 2.75 A; at the maximum 3.47 / 3.49 / 4.01 A, OVER 2.8 A; the held maximum 2.15 / 2.16 / 2.49 A. The per-point
  thresholds also reproduce: 7.57 A and 6.54 A, and a fall of 1.24 to 1.43 times.
- **The pooled 16.8 A figure** is withdrawn.

**2. B2, the classification.**
- **The classes.** (a) A-1 and A-2; (b) B-1 to B-5; (c) C-1 to C-9. Each (a) and (b) item carries a correction and a
  measurable closure:
  - A-1: CC onset above U3's maximum plus 0.06 A at -20, 25 and 62 C;
  - A-2 and B-5: VIN_RAW settles above 12 V and FE_PGOOD never drops;
  - B-1: peak at most 90 % of Isat at the part's temperature, and no knee;
  - B-2: TJ at most 150 C at 9, 15.1 and 36 V in 62.1 C air;
  - B-3: the gates PASS at the new declarations;
  - B-4: every can at most 2.8 A over the ESR bands.
- **Missing evidence** (board A's thermal resistance, C11 and C12, the order code, L1's derating, U3's minimum, the
  other loads) is class (c), not failure, as the owner asked.
- **The held FETs at 9 V** moved to C-3, which is right given the missing thermal resistance.
- On A-2, see minor 4. On B-5's framing and B-1's 5.20 A, see minors 3 and 2.

**3. Kelvin.**
- **The netlist** (sha `6c40250c`) reads:
  - R160 "100R 1% (ISNS+ filter, Kelvin from the shunt's output pad)", from FE_OUT to FE_ISNS_P (U2 pin 14);
  - R161 "(ISNS- filter, Kelvin from the shunt's rail pad)", from VBUS20 to FE_ISNS_N (U2 pin 13).
- **No netlist error is established.** A netlist names the net, not the point on it, so Kelvin sensing is correctly
  implementation requirement C-1, not a defect.
- **A32** is historical evidence tied to its revision: the board file, commit `b7e0d28f`, sha256/16 `58e26c67987b1daa`,
  and the ADVISORY verdict of 20 Sep.
- **The budget.** 0.371 mOhm is the working-temperature figure. At 25 C it is 0.287 mOhm with the copper at 100 C, or
  0.324 mOhm at 62.1 C. The 25 C criterion of 0.29 mOhm is the conservative one. The bench figure, 0.29 mOhm x 6.0 A,
  is 1.74 mV.

**4. The 0.378 A margin stays closed.**
- The note is accurate. With four FETs switching and U3's pin at 0.019 A, the other loads are 0.079 A and the margin is
  +0.359 A.
- SNVSAI1D 7.1 says only that near VIN = VOUT "the device operates in a proprietary transition buck or boost mode"; it
  does not say which switches run.
- The closed comparison on 0.060 A is kept, and the bound is shown beside it (C-9). That is honest, and both figures are
  positive.

**5. The derated variant.**
- The margins reproduce: 4.05 A gives +0.001 A (0.060) and -0.018 A (0.079); 4.00 A gives +0.052 and +0.033 A.
- It is labelled "coordination only" in R11-DEPENDENCY 0, 1 and 2a, in `three_cases.py`, `three_cases.out` and
  ENERGY-BASIS section 0, and its energy is shown as a separate variant.
- The as-drawn case (i) is preserved beside it. See minor 1 on the setting.

**6. The three cases.**
- **Recomputed on the checker's balance:**
  - (i) at NOM: 326.7 / 352.9, 357.6 / 383.9 and 494.8 / 522.5 Wh;
  - (i') at NOM: 355.6 / 381.9, 386.6 / 412.9 and 523.9 / 551.6 Wh;
  - (ii)'s lower bound at NOM: 622.1 / 895.6, 652.8 / 926.5 and 805.4 / 1079.8 Wh;
  - (ii)'s lower bound at WE: 719.3, 749.8 and 900.8 Wh, TYP equal to WAB, because both builds reach the cap in the same
    six hours, 09 to 14 UTC;
  - coverage: (i) and (i') 0 on every lid and line; (ii)'s lower bound at NOM 2 / 2 / 0 (4S14P), 2 / 2 / 2 (4S15P) and
    0 (4S9P), and 0 at WE.
- **The (i) and (i') WE rows** read 1.3 to 2.2 Wh above the page's figures, because the checker does not recompute U3's
  efficiency at 4.05 and 3.95 A. Every verdict agrees.
- **The (ii) lower bound's assumption** is stated in `three_cases.py`, `.out` and R11-DEPENDENCY 0 and 4; see minor 3.
- **Case (iii)** is energy_basis's NOM and WE unchanged. `three_cases.out` 0 reproduces them, and both runs rerun byte
  identical.
- **L3-OD6's sizes** are labelled as resting on case (iii), HYPOTHETICAL, with "the sizing is not run on case (i)"
  (ENERGY-BASIS 8a).

**7. The owner questions meet the owner's test.** No question is asked now. Each correction has an engineering form that
changes no requirement:
- the VIN_RAW rule charges AT the available power;
- L1's schedule at 9 V charges below no source's available power, since the vehicle entry gives at most 6.15 A (55 W
  at 9 V) against the schedule's about 104 W;
- component selection and Kelvin routing are engineering tasks.

The three conditional consequences each name the requirement and quantify the consequence where a figure exists:
- **REQ-015**, quoted exactly: the floor moves to 11.00 V, recomputed;
- **REQ-072:** about 20 Wh per 0.1 A (ENERGY-BASIS section 4: -20.1 Wh);
- **CON-006 and REQ-019:** only if no fitting part exists.

REQ-016's 100 W, which Option A(i)'s 200 W stage exceeds, is correctly marked as already the owner's. On B-2's
unnamed mechanism, see minor 5.

**8. CHECK-3's minors 1 to 7 are answered:**
1. L1's bias drop is in every table.
2. R11 with ripple: 0.36 / 0.60 / 0.28 W in service, and 0.76 / 1.28 / 0.57 W at the maximum. 0.356 W at 15.1 V and
   1.276 W at 9 V are recomputed.
3. The other loads, C-9.
4. p.24's 100 Ohm is for CS and CSG.
5. The spring pins: a sibling's rating, named.
6. The Kelvin criterion at 25 C, and ENERGY-BASIS section 2 now says "with Kelvin taps on R11".
7. A32 is named with its commit and sha.

**Hygiene.**
- **Reruns.** All nine committed outputs rerun byte identical in the clone: `r11_dep`, `three_cases`, `vbus20_range`,
  `curve_readings`, `energy_basis`, `weather_basis`, `plane_grid`, `reconcile_lid_panel` and `energy_runs`.
- **The added lines** carry no U+2013 or U+2014, no host names and no user paths.
- **No ignored file is committed.** The diff touches only `v2/docs/records/`, and nothing under `v2/ecad/` (so
  `pcb_requirements.yaml` is untouched).
- **The two commits** are in the owner's name with no trailer.

## Figures beside theirs

| Figure | Theirs | Checker |
|---|---|---|
| Bank, worst can at 9.370 A (matched / 1.5:1 / 2:1) | 3.47 / 3.49 / 4.01 A | 3.47 / 3.49 / 4.01 (5.0 A point); 3.45 / 3.47 / 3.99 (5.7 A point) |
| Bank in service | 2.37 / 2.39 / 2.75 A | 2.37 / 2.39 / 2.75; 2.36 / 2.37 / 2.73 |
| Proposed margin, 0.060 A; 0.079 A | +0.378; +0.359 A | +0.378; +0.359 A |
| Derated 4.05 A, 0.060 A; 0.079 A | +0.001; -0.018 A | +0.001; -0.018 A |
| Derated 4.00 A | +0.052; +0.033 A | +0.052; +0.033 A |
| Kelvin, working; at 25 C | 0.371; 0.29 mOhm | 0.371; 0.287 (copper 100 C) to 0.324 (62.1 C) mOhm |
| L1 at 9 V with U3 at 5.20 A | 90 % of Isat | 15.74 A, 89.9 %; with a 5.20 A setting's 5.33 A maximum 16.06 A, 91.8 % |
| VIN_RAW for full current at 90 % of Isat | 11.00 V | 11.00 V |
| (i) NOM, 4S15P / 4S14P / 4S9P, TYP; WAB | 326.6 / 357.5 / 494.7; 352.8 / 383.8 / 522.4 | 326.7 / 357.6 / 494.8; 352.9 / 383.9 / 522.5 |
| (i') NOM | 355.5 / 386.5 / 523.7; 381.7 / 412.7 / 551.5 | 355.6 / 386.6 / 523.9; 381.9 / 412.9 / 551.6 |
| (i') WE, 4S15P TYP / WAB | 449.3 / 475.3 | 451.5 / 477.5 (U3 not recomputed) |
| (ii) lower bound NOM | 622.1 / 895.7; 652.9 / 926.5; 805.5 / 1079.9 | 622.1 / 895.6; 652.8 / 926.5; 805.4 / 1079.8 |
| (ii) lower bound WE | 719.4, 749.9, 900.9 (TYP = WAB) | 719.3, 749.8, 900.8 (TYP = WAB, cap hours 09 to 14) |
| Coverage (ii) lower bound NOM: 4S14P; 4S15P; 4S9P | 2 / 2 / 0; 2 / 2 / 2; 0 | same |
| Coverage (i), (i') | 0 everywhere | 0 everywhere |

Rerun from this folder against a checkout of `fnd/l3plane` with the held files present: `python3 indep_round4.py <checkout>`
(it uses `indep_balance.py`, `indep_round2.py`, `indep_grid_weather.py` and `dayratios.json` beside it).
