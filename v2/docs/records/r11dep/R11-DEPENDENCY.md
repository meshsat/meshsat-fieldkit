# Board A's charge path: the circuit as drawn, the resistor-only proposal, and the corrected path (stream r11dep, MESHSAT-1357)

**Third issue, 30 September 2026:** CHECK-4 of `06b8ecea` accepted the second issue with five minors, answered here
(section 9): the derated setting is 4.00 A, L1's schedule is written as a register setting, the collapse bound's other
sources of pessimism are named, A-2's status is stated, and B-2's remedies are named concretely.

**Second issue, 30 September 2026.** It answers the independent check CHECK-3 of `4e9fa869`, which read "accepted: no" on
two blocking items and seven minors (section 9 maps each to its answer). It also carries the owner's amendments of the same
day. They are quoted here because they set what this page is:

> "The reported findings make this a power-path correction, potentially involving components, sensing, layout and thermal
> design. Stop presenting the 6.2 mOhm substitution as a sufficient solution. Keep findings provisional until independently
> checked, and distinguish: the circuit as drawn; the resistor-only proposal; any hypothetical corrected power path used for
> feasibility calculations."

> "Classify findings accurately. Separate confirmed existing defects, defects introduced by the proposal, and missing
> evidence. [...] Record necessary engineering corrections with measurable closure criteria. Component selection and Kelvin
> routing are engineering tasks."

**Every finding here is PROVISIONAL until the next independent check.** This page is the author's record, AI arithmetic, not
a qualified review. It is **prototype design**: nothing is built, powered or measured. No generator is edited, no requirement
is changed, and nothing is implemented.

**Labels.** Every figure carries its basis:
- **MAKER (page)**: a maker's document in `v2/vendor/`;
- **NETLIST**: board A's or board E's committed netlist;
- **MODELED**: the energy model;
- **INFERRED**: a stated method applied to the above;
- **ASSUMPTION**: a figure no document gives.

**Sources.**
- `r11_dep.py` prints `r11_dep.out`: the electrical figures. Section numbers `.out N` below are that file's.
- `../l3plane/three_cases.py` prints `three_cases.out`: the energy of each case. It reads this stream's bands.

## 0. In short

- **The circuit as drawn cannot deliver what its own charge design asks, and it fails M1.** R11 is 10 mOhm and the charger
  U3 is set to 4.15 A. The front end's current limit then sits at 4.21 to 5.81 A. M1 fails on every lid option by 326.6 to
  522.4 Wh on the reference day, and the model carries none of 864 past September windows.
- **The derated variant fixes one thing.** It sets U3 at 4.00 A so that the two current limits agree, whatever the other
  loads turn out to be. It fixes nothing else, and M1 still fails on every lid, by 369.9 to 566.0 Wh.
- **The resistor-only proposal (R11 6.2 mOhm, U3 6.2 A, nothing else changed) is not a solution.** It clears the front end's
  limit above U3 by 0.378 A, as CHECK-3 closed it. But it introduces five defects in the power path (section 2b), and several
  pieces of evidence are missing (section 2c).
  - **Its energy is INCONCLUSIVE.** It lies somewhere between two bounds:
    - **failing by 622 to 1080 Wh**, if the input bus collapses whenever the sun gives less than U3 asks;
    - **the corrected path's figures.**
- **The corrected path is HYPOTHETICAL.** With every correction of section 2 closed, the model passes the tablet-out and
  QMX-out lids on the mean day at nominal inputs, and at the worst inputs only conditionally. It carries 19 to 27 percent of
  past Septembers. **None of this is demonstrated capability.**
- **No owner decision is needed now.** Every correction is engineering work. Three remedies would change a requirement if an
  engineer chose them; they are named with their consequences in section 6.

## 1. The three cases, and the derated variant

| Case | What it is | Its standing |
|---|---|---|
| **AS DRAWN** | R11 10 mOhm (NETLIST), U3 IIN_HOST 4.15 A (entry E1, board A as generated) | the circuit of record; its defects are 2a |
| **DERATED VARIANT** | AS DRAWN with U3 at 4.00 A | fixes the current-limit coordination (2a A-1) ONLY; M1 fails |
| **RESISTOR-ONLY** | R11 6.2 mOhm and U3 6.2 A, nothing else changed | the proposal as drafted in a1elec's E2; INCONCLUSIVE; its own defects are 2b |
| **CORRECTED PATH** | R11 6.2 mOhm with Kelvin taps, U3 6.2 A under a VIN_RAW-dependent rule, and every 2a, 2b and 2c item closed | HYPOTHETICAL: the path the energy model's NOM and WE cases assume; used for feasibility only |

## 2. The findings, classified

Each defect carries its correction and a measurable closure criterion. All corrections are engineering tasks. Section 6
names the few remedies that would change a requirement.

### 2a. Existing defects of the circuit as drawn

A-1 is confirmed on the makers' figures. A-2 is established from the netlist and the makers' documented behaviour, with its
mechanism INFERRED; bench row 7b.7 confirms it.

**A-1. The front end limits below what the charge design asks.**
- **Finding.** The stacked limit is **4.212 / 5.000 / 5.810 A** (`.out` 3).
  - The generator declares VBUS20 at 6.0 A typical ("BQ25731 up to 8 A").
  - M1's design needs 6.1 to 6.355 A into U3.
  - At the drawn setting, U3's maximum of 4.25 A plus 0.060 A of the other loads is 4.310 A through R11: **0.098 A over the
    stacked minimum**, so even there the front end can limit first. The record's 50 mA margin was taken against the printed
    4.30 A.
- **Evidence.** LM5176 p.7 (VSNS 43 / 50 / 57 mV); HoJLR2512 pp.1 to 2 (the part, 1 %, 50 ppm/K); BQ25731 p.1 and p.80
  (U3's maximum). These are MAKER figures; the stack is INFERRED.
- **Correction, for the drawn circuit: the DERATED VARIANT, U3 at 4.00 A.**
  - U3's maximum is then 4.100 A. With the carried 0.060 A that is 4.160 A, against 4.212 A: **+0.052 A**.
  - With C-9's four-FET 0.079 A it is **+0.033 A**, so 4.00 A closes whatever C-9 finds (`.out` 3).
  - **4.05 A was not chosen:** it clears by +0.001 A on 0.060 A and fails by minus 0.018 A on 0.079 A. The step is 50 mA
    (INFERRED from CHARGER.md's code 124 for 6.2 A).
  - This fixes the coordination only. It does not resolve A-2, and it does not meet M1 (section 4).
- **Closure.**
  - The stacked minimum of the fitted R11 is at least U3's maximum plus the other loads.
  - On the bench, the front end's constant-current onset, measured with an electronic load past U3 at -20, 25 and 62 C, lies
    above U3's maximum plus 0.06 A (7b.1).

**A-2. With E1's fixed setting, the input bus collapses on a short source.**
- **Status.** Established from the netlist and the makers' documented behaviour; the mechanism is INFERRED; bench row 7b.7
  confirms it.
  - The netlist fixes the structure: no input-power bound, and U3's VINDPM on the regulated VBUS20 (U3 pin 1).
  - The makers fix the behaviour: the LM5069's current limit, and the LT8705A's input regulation ("VC will be reduced").
  - The tree's own FW-A16 and gen_sch_a.py name the collapse for the vehicle entry.
- **Where the defect sits.** In the **E1 setting** (a fixed 4.15 A), not in FW-A16 as written, which scales IIN_HOST with
  VIN_RAW and so bounds it.
- **The mechanism.**
  - The front end is a constant-power load: U3 draws a fixed current from VBUS20, and the LM5176 holds VBUS20 at 20 V.
  - When a source gives less than U3 asks, VIN_RAW sags. The vehicle entry's LM5069 limits, or the panel tracker's input loop
    cuts its current.
  - VIN_RAW then walks down to the stage's latch, 7.86 to 8.31 V falling (gen_sch_a.py U34).
  - U3's own VINDPM watches VBUS20, which stays regulated, so it does not act.
- **What bounds it today.** FW-A16 as written (HW-FW-CONTRACT.md) scales IIN_HOST with VIN_RAW against the vehicle entry and
  names this failure ("a limiting constant-power front end collapses the bus").
  - With the panel alone it caps charge at about 54 W (the recorded reduction O-33).
  - E1's fixed 4.15 A has no such scaling, so on the panel the drawn circuit collapses whenever the array gives less than
    U3 asks, about 83 W at VBUS20 (89 W at the front end's input).
- **Correction.** A VIN_RAW-dependent IIN_HOST rule for every source: firmware that lowers U3's input limit as VIN_RAW falls,
  so the charge path takes what the source gives. This is an engineering choice while REQ-072 is met (the owner's amendment).
- **Closure.** On the bench, with the panel source (or a simulator) stepped below U3's demand, VIN_RAW settles above 12 V and
  FE_PGOOD never drops (7b.7).

**Not an existing defect: the ISNS taps.** CHECK-3's A-2 read revision A32's taps. Per the owner's amendment, that reading is
historical evidence, tied to A32 (section 2d). The current netlist shows no tap error (`.out` 1):
- R160 runs from FE_OUT and R161 from VBUS20 into U2 pins 14 and 13.
- Their values carry the intent: "Kelvin from the shunt's output pad" and "Kelvin from the shunt's rail pad".
- R150 and R151 bring CS and CSG the same way.

A netlist names the net a tap lands on, not the point on that net. The Kelvin connection is therefore a layout property, and
it is an implementation requirement: C-1.

### 2b. Defects the resistor-only proposal introduces (R11 6.2 mOhm, U3 6.2 A, nothing else changed)

**B-1. L1 runs past its TYPICAL saturation current at the 9 V floor, in service.**
- **Finding** (`.out` 4). With U3 at its maximum and VIN_RAW at 9 V:
  - L1's peak is 17.84 A, or 18.62 A with Isat's own 30 % inductance drop on top of the minus 20 % tolerance;
  - the typical Isat is 17.5 A, at 25 C (Coilcraft p.1, note 5);
  - the rms is 16.04 A, against the 15.5 A Irms at a 40 K rise.
- **How serious.** It is not a demonstrated failure: saturation is soft, and the part runs at about 105 C against its 165 C
  maximum. But the design runs past its saturation point, and the held circuit did not (16.33 A, or 17.11 A with the drop).
- **At the highest permitted current** (9.370 A out, 9 V), the peak is 25.21 A (26.00 A with the drop), with the part at
  153 C. The cycle-by-cycle limit (20 / 24 / 28 A, LM5176 p.7) sits above Isat even at its minimum, so it does not keep L1
  out of saturation.
- **Correction, either of:**
  - an inductor whose Isat at its operating temperature exceeds the peak at the highest permitted current at 9 V, with margin;
  - IIN_HOST scheduled on VIN_RAW. At 9 V the **register setting is 5.05 A** (the 50 mA step at or under 5.20 / 1.025).
    Its maximum, 5.18 A, puts the peak at 15.68 A, 89.6 % of the typical Isat (`.out` 6); 5.20 A is U3's actual input at 90 %,
    not a setting. The front end then draws about 13 A at 9 V, above the vehicle entry's 6.15 A. In service no source gives
    more at 9 V (the tracker holds 15.1 V at U3's full demand), so this charges below no source's available power: an
    engineering choice. **The figure rests on Isat at 25 C and is recomputed once L1's temperature derating is held (C-5).**
- **Closure.**
  - Analysis: the peak at the highest permitted current is at most 90 % of Isat at the part's temperature, using the maker's
    derating (C-5).
  - Bench: L1's current waveform at 9 V with U3 at full draw shows no saturation knee (7b.5).

**B-2. The FETs at the highest permitted current at 9 V.**
- **Finding.** Q2 dissipates 6.28 W, Q4 4.36 W and Q5 2.70 W at 150 C. Holding 150 C in 62.1 C air needs an RthetaJA of 14,
  20 and 33 C/W. For a 5 x 6 mm SON that is beyond what board copper alone gives (INFERRED).
  - At a part at the minimum cycle-by-cycle limit, the output at 9 V is bounded at 7.28 A (`.out` 4).
  - In service at 9 V (Q2 30, Q4 38 C/W) and at 15.1 V at the maximum (Q2 39 C/W), the figures are within reach of copper.
    Those cases are MISSING EVIDENCE (C-3), not defects.
- **Correction, one or both of:**
  - **hiccup** (MODE to AGND through 93.1 kOhm, p.20), which shuts down after 128 consecutive cycle-by-cycle limit cycles
    (p.17). It is **partial**: it catches only parts whose peak limit sits under the fault's peak;
  - **FETs and cooling rated for the fault**, for example FETs in parallel, with board A's copper and any heat path sized for
    the dissipation above.

  An input-side average limit is not available: the LM5176's one average loop senses input or output, and R11 must sense
  the output. A firmware schedule does not bound this fault either, since the fault is the front end at its own limit.
  **Neither remedy, nor B-4's, is yet shown to fit on board A.**
- **Closure.** TJ at most 150 C, or the tree's derating where one applies, at the highest permitted current at 9, 15.1 and
  36 V in 62.1 C air. The figure comes from board A's own thermal resistance or from a measurement (7b.4).

**B-3. The copper declarations are passed.**
- **Finding.**
  - VBUS20 and FE_OUT reach 6.415 A in service and 9.370 A at the maximum, against the declared 6.0 / 8.0 A.
  - VIN_RAW reaches 16.01 A in service and 23.38 A at the maximum at 9 V, against the declared 14.10 A. _FE_A's own formula
    at the proposed printed maximum gives 22.74 A.
- **What the conservative model asks** (decision 35, external layer, 10 K rise):
  - VBUS20 at 9.37 A: 7.2 mm at 1 oz or 3.6 mm at 2 oz;
  - VIN_RAW at 9 V: 19.3 mm at 1 oz or 9.6 mm at 2 oz in service; 38.6 mm or 19.3 mm at the maximum.
- **Correction.** Re-declare VBUS20, FE_OUT, VIN_RAW, _FE_A, _VIN_T and TRK_OUT (7a.4), and regenerate.
- **Closure.** dc_drop, derate and the track-width gates read PASS on the regenerated board at the new declarations.

**B-4. VBUS20's bulk capacitors at the highest permitted current** (CHECK-3 B1, recomputed).
- **The method.** The generator's own node analysis (gen_sch_a.py, the third fix-up of 26 September 2026) counts the front
  end's output ripple and U3's pulsed input current together, over dense bands. Its worst can is:
  - at 5.7 A: 2.10 A matched, 2.11 A at a 1.5:1 ESR spread, 2.43 A at 2:1;
  - at 5.0 A: 1.85 / 1.86 / 2.14 A.

  These are scaled here in proportion to the front end's current, taking the larger of the two points (INFERRED, `.out` 4).
- **The worst can:**

| Current | Matched | 1.5:1 | 2:1 | Against 2.8 A a can (Panasonic p.2) |
|---|---|---|---|---|
| held maximum 5.810 A | 2.15 A | 2.16 A | 2.49 A | 77 / 77 / 89 %: within |
| proposed in service 6.415 A | 2.37 A | 2.39 A | 2.75 A | 85 / 85 / 98 %: within, at the edge |
| **proposed maximum 9.370 A** | **3.47 A** | **3.49 A** | **4.01 A** | **124 / 124 / 143 %: OVER** |

  CHECK-3's figures are 2.36 to 2.73 A and 3.45 to 3.99 A, scaled from the 5.7 A point alone; the 5.0 A point is slightly
  steeper. The first issue's pooled 16.8 A figure is withdrawn.
- **Correction.** Re-run the generator's node analysis at 9.37 A and 9 V, and enlarge or rebalance the bank. The worst can
  must fall by 1.24 to 1.43 times, matched to 2:1 (`.out` 6). Or bound the fault current (B-2).
- **Closure.** Every can at most 2.8 A (the maker's figure at 125 C) over the ESR bands at the highest permitted current. On
  the bench, the worst can's ripple and temperature agree with it (7b.8).

**B-5. A fixed IIN_HOST of 6.2 A drops FW-A16's VIN_RAW scaling** (INFERRED; the proposal's form of A-2).
- **Finding.** Whenever the array gives less than U3 asks (124 W at VBUS20 at 6.2 A and 20 V; up to 144 W at the front end's
  input at U3's maximum and the bus's maximum), the bus collapses to the latch instead of settling at the available power.
  The energy model's `min(available, cap)` presumes the opposite.
- **Its cost as a bound** (MODELED, `three_cases.out`). If a collapsed hour delivers nothing, every lid fails by 622 to 1080
  Wh on the mean day, and the model carries 0 to 2 of 864 past windows.
- **How far the bound is from the truth.**
  - It is pessimistic in hours where the packs are full, when U3 asks less than its cap.
  - It is also pessimistic because the restart latch brings the front end back within about 1 to 2.5 s (gen_sch_a.py: "a
    dip under 8 V interrupts charging for about 1 to 2.5 s").
  - And because U3 resets its input limit to 3.25 A at every bus drop (SLUSE66A pp.26 and 80; FW-A16 (b)), so after a
    collapse it asks about 65 W until the host rewrites it.
  - The other way, on real weather a dip inside an hour whose mean clears the cap can also collapse the bus. So on the
    series it is a bound on hourly means only, not a strict one.
- **Correction and closure.** As A-2, for the proposal's setting.

### 2c. Missing evidence (not a demonstrated failure)

| Item | What is missing | What closes it |
|---|---|---|
| **C-1** | A layout of the current netlist, and so a Kelvin reading of R11's taps. **IMPLEMENTATION REQUIREMENT:** the copper R11's current shares with the two taps, both sides together, at most 0.371 mOhm at its working temperature: 2.38 mV at 6.415 A, 4.8 % of 50 mV. That is **0.29 mOhm at 25 C** with the copper at 100 C, or 0.32 mOhm at 62.1 C (copper 0.00393 /K, INFERRED). The round's brief labels 0.371 mOhm a 25 C figure. It is the working-temperature figure (CHECK-3 minor 6: 0.29 to 0.32 mOhm at 25 C), so the 25 C criterion is 0.29 mOhm | (1) Layout extraction: dc_drop's mesh with kelvin_check on FE_ISNS_P and FE_ISNS_N (declared in pcb_sensitive.yaml) reads at most 0.29 mOhm for the two together. kelvin_check's own 1 % per tap is stricter and closes it too. (2) Bench at 25 C: the DC voltage across U2 pins 14 and 13 exceeds I x R11, with R11 measured four-wire at its pads, by at most 0.29 mOhm x I (1.7 mV at 6.0 A) (7b.3) |
| **C-2** | The 6.2 mOhm part's order code. The HoJLR2512-3W-6.2mR-1% is named by the maker's scheme, not by a catalogue answer | A catalogue answer for a 2512 part: 1 %, 50 ppm/K or better, 3 W, with its sheet filed |
| **C-3** | Board A's own RthetaJA for Q2 to Q5. The maker's 50 C/W is for a 1 in2 2 oz pad. On that figure the held circuit's Q2 and Q4 already pass 150 C at 9 V at its limit's maximum (they need 36 and 44 C/W) | A figure from the laid copper: at most 30 C/W for Q2 and 38 C/W for Q4 (in service, 9 V), and 39 C/W for Q2 at 15.1 V at the maximum; or a measurement |
| **C-4** | C11 and C12's ripple rating and DC-bias derating at 36 V (FS32X106K101EGG): 3.65 A rms in service and 4.97 A at the maximum for the two, in buck | The maker's figure, at least 2.5 A a part, or a part that has one (7b.8) |
| **C-5** | L1's Isat against temperature. Coilcraft's derating page is not held, and the 17.5 A is typical at 25 C | The maker's derating read at the part's temperature (feeds B-1's closure) |
| **C-6** | Board E's 200 W stage: not designed. The front end's input is the stage's OUTPUT: 144.1 W in service, 210.5 W at the proposed maximum. Into the stage at the declared 0.93 that is 154.9 and 226.3 W. The model's 200 W is a window on the stage's INPUT | A stage design that takes 226.3 W in at the maximum, or a bound on the front end's demand in a fault |
| **C-7** | U3's input-current minimum at 10 mOhm. SLUSE66A prints only the maximum, 100 mA above the setting (p.80); the 6.1 A minimum is INFERRED | The maker's figure, or a bench reading |
| **C-8** | The three undocumented efficiencies: board E's stage, board A's front end and the pack's charge efficiency (ENERGY-BASIS section 3) | The makers' figures for these circuits, or measurement |
| **C-9** | The VBUS20 loads besides U3. By parts they are 0.051 A with two FETs switching (CHECK-3) and 0.079 A with four; the sheet does not say which switch in its transition region. U3's own VBUS pin, about 0.019 A by CHECK-3, rests on held FET sheets not in this tree. 0.060 A is carried | A bench reading of R11's current minus R16's at U3's full draw |

### 2d. Historical evidence, revision A32 only

- **The board.** `v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb` is revision A32: last commit `b7e0d28f` of 15 September
  2026, routed, sha256/16 `58e26c67987b1daa`. On it, U2 pins 13 to 16 sit on VBUS20, FE_OUT, GND and FE_CS, the power nets
  themselves, with no R160, R161, R150 or R151 (`.out` 3, read from the board file).
- **The reading.** kelvin_check (ADVISORY, 20 September 2026) read two copper drops at dc_drop's solved current:
  - 26.62 mV between R11.1 and U2.14;
  - 2.16 mV between R11.2 and U2.13.

  Together that is 4.8 to 7.6 mOhm, as large as R11 itself.
- **What it shows.** How large a tap error has been on this board. It is not a finding about the current netlist, which has
  no layout, and it is not an existing defect of the circuit as drawn.

## 3. The electrical figures behind the classes

**The limit bands** (`.out` 3). VSNS 43 / 50 / 57 mV (LM5176 p.7) over R11, with the stack:
- ±1 % (HoJLR2512 p.1);
- 50 ppm/K over 75 K, with R11 between -20 C and an ASSUMED 100 C;
- ±0.3 mV of ISNS bias over the 100 Ohm filter (INFERRED).

| | Printed | Stacked min / typ / max | Through R11 in service | Margin |
|---|---|---|---|---|
| held, 10 mOhm | 4.30 / 5.00 / 5.70 A | 4.212 / 5.000 / 5.810 A | U3's 6.355 A maximum plus 0.060 A = 6.415 A asked | minus 2.203 A |
| proposed, 6.2 mOhm | 6.94 / 8.06 / 9.19 A | 6.793 / 8.065 / 9.370 A | 6.415 A | **+0.378 A, as CHECK-3 closed it**; it holds only with C-1 closed |

**R11 itself** (HoJLR2512, MAKER): 3 W, derated linearly from 70 C to zero at 170 C (p.2); 5 x P for 5 s (p.4).
- **Power at the proposed maximum,** with all the output ripple taken through R11 as an upper bound (minor 2): 0.76 W at
  15.1 V, 1.28 W at 9 V and 0.57 W at 36 V. In service it is 0.36 / 0.60 / 0.28 W. Both are within 3 W (2.10 W at 100 C).
- **R11's own temperature** by the derating line's 33.3 K/W (INFERRED):
  - at most 84 C where the band's minimum is set, which supports the ASSUMED 100 C;
  - up to 105 C at the maximum, which only lowers that end of the band.

**The power path at the three currents** (`.out` 4; worst inside air 62.1 C):

| Part | Held maximum 5.810 A | Proposed in service 6.415 A | Proposed maximum 9.370 A | Class |
|---|---|---|---|---|
| L1 peak (with the 30 % drop), 15.1 / 9 / 36 V | 10.14 (10.78) / 16.33 (17.11) / 8.94 A | 11.04 (11.68) / **17.84 (18.62)** / 9.55 A | 15.43 (16.07) / **25.21 (26.00)** / 12.50 A | B-1 |
| L1 part temperature, worst | 97 C | 105 C | 153 C | against 165 C |
| FETs' RthetaJA needed at 9 V (Q2, Q4) | 36, 44 C/W | 30, 38 C/W | 14, 20 (Q5 33) C/W | C-3; B-2 at the maximum |
| Bulk, worst can at 2:1 | 2.49 A | 2.75 A | **4.01 A** | B-4 |
| C11, C12 at 36 V, together | 3.39 A | 3.65 A | 4.97 A | C-4 |
| J_VR1 to J_VR4, a pin, at 9 V | 3.62 A | 4.00 A | 5.85 A | within the sibling's 9 A (minor 5) |
| VIN_RAW at 9 V (declared 14.10 A) | 14.50 A | 16.01 A | 23.38 A | B-3 |
| Board E's stage output / input | 130.5 / 140.3 W | 144.1 / 154.9 W | 210.5 / 226.3 W | C-6 |

**The spring pins' basis** (minor 5). J_VR1 to J_VR4 are "Mill-Max 0858 class" (NETLIST).
- The cited page rates the 0850 to 0853 at 9 A at a 10 C rise and does not list the 0858, so the 9 A is a sibling's figure.
- The 0858's own page is not held here. CHECK-3 read it: "Inner Spring Dependent", spring 82 "12 Amp", no rise stated.
- 5.85 A is under both.

## 4. The energy of each case (MODELED, `../l3plane/three_cases.out`)

**The conditions.** SC-37's mean September day at Leiden on the 40 degree south plane. Each cell gives both packs' lowest
store in Wh, or the energy left unserved. TYP / WAB are the two array builds. NOM and WE are ENERGY-BASIS's input sets.

| Case | 4S9P, both lid functions kept | 4S14P, tablet out | 4S15P, QMX out |
|---|---|---|---|
| **AS DRAWN**, NOM (the model's min(available, cap) kept: an upper bound, A-2) | NOT MET, 494.7 / 522.4 unserved | NOT MET, 357.5 / 383.8 | NOT MET, 326.6 / 352.8 |
| AS DRAWN, WE (U3 at its INFERRED 4.05 A minimum) | NOT MET, 589.3 / 616.7 | NOT MET, 452.9 / 478.9 | NOT MET, 422.1 / 448.0 |
| **DERATED VARIANT** (U3 4.00 A), NOM | NOT MET, 538.3 / 566.0 | NOT MET, 400.9 / 427.2 | NOT MET, 369.9 / 396.2 |
| DERATED VARIANT, WE (3.90 A) | NOT MET, 630.4 / 657.8 | NOT MET, 493.7 / 519.7 | NOT MET, 462.9 / 488.9 |
| **RESISTOR-ONLY: INCONCLUSIVE**, between its lower bound under B-5's collapse (NOM) and the corrected path | NOT MET, 805.5 / 1079.9, up to NOT MET, 165.7 / 172.6 | NOT MET, 652.9 / 926.5, up to 93.7 / 75.7 | NOT MET, 622.1 / 895.7, up to 125.2 / 106.8 |
| RESISTOR-ONLY, WE: the same bounds | NOT MET, 900.9 / 900.9, up to NOT MET, 169.2 / 176.1 | NOT MET, 749.9 / 749.9, up to 44.0 / NOT MET, 10.8 | NOT MET, 719.4 / 719.4, up to 74.3 / 19.5 |
| **CORRECTED PATH, HYPOTHETICAL**, NOM | NOT MET, 165.7 / 172.6 | 93.7 (49.0, 44.6) / 75.7 (48.2, 27.5) | 125.2 (57.1, 68.1) / 106.8 (56.3, 50.5) |
| CORRECTED PATH, HYPOTHETICAL, WE (CONDITIONAL on C-8) | NOT MET, 169.2 / 176.1 | 44.0 (44.0, 0.0) / NOT MET, 10.8 | 74.3 (52.4, 19.4) / 19.5 (19.5, 0.0) |

**Reading the table:**
- The AS DRAWN rows at NOM equal ENERGY-BASIS's GEN: U3's 4.15 A binds either way.
- The proposed front end's stacked minimum, fed as the corrected path's cap, moves no cell. That is checked in
  `three_cases.out`.
- The resistor-only lower bound's TYP and WAB agree at WE because both builds reach U3's cap in the same six hours of the
  mean day.

**The modelled historical coverage** (864 September windows of 2005 to 2020, TYP; kept / COMB / EACH):

| Case | 4S9P | 4S14P | 4S15P |
|---|---|---|---|
| AS DRAWN, NOM (upper bound) | 0 | 0 | 0 |
| DERATED VARIANT, NOM | 0 | 0 | 0 |
| RESISTOR-ONLY lower bound, NOM; WE | 0; 0 | 2 / 2 / 0 (0.2 %); 0 | 2 / 2 / 2 (0.2 %); 0 |
| CORRECTED PATH, HYPOTHETICAL, NOM | 0 | 207 / 200 / 145 (24.0 / 23.1 / 16.8 %) | 235 / 232 / 177 (27.2 / 26.9 / 20.5 %) |
| CORRECTED PATH, HYPOTHETICAL, WE | 0 | 166 / 164 / 115 (19.2 / 19.0 / 13.3 %) | 190 / 186 / 141 (22.0 / 21.5 / 16.3 %) |

**The corrections the CORRECTED PATH rows assume.** None is closed:
- Kelvin taps on R11 (C-1) and the 6.2 mOhm part (C-2);
- a VIN_RAW-dependent IIN_HOST rule, so the charge path takes `min(available, cap)` (A-2, B-5);
- L1 at 9 V (B-1, C-5);
- the FETs' thermal path (B-2, C-3);
- the bulk bank (B-4);
- the copper declarations (B-3);
- C11 and C12 (C-4);
- board E's 200 W stage (C-6);
- the three efficiencies (C-8; WE is conditional on them).

## 5. The LM5176's other settings and R11 (`.out` 5, the maker's equations)

| Setting | Tied to R11? | Consequence of 6.2 mOhm |
|---|---|---|
| Average current limit, ICL(AVG) = 50 mV / RSNS (Eq. 4, p.17) | **yes, the one setting R11 sets** | the bands of section 3 |
| The CC loop: gm 1 mS (p.7) discharging SS (C7 4.7 uF) above 50 mV (7.3.6, p.17) | its gain per ampere scales with R11 | 0.62 of the held loop's gain (INFERRED); its response is a bench row |
| The ISNS filter: R160, R161 100 Ohm, C128 1 nF across. This is Figure 8-1's network (p.17), and the sheet asks for the capacitor close to the IC between the pins (p.30) | no | unchanged. **p.24's 100 Ohm ceiling is for CS and CSG** (R150, R151 sit at it), not ISNS (minor 4). The bias offset of 0.3 mV is 48 mA at 6.2 mOhm, against 30 mA at 10 mOhm |
| The sense amplifier's range: common mode 0 to 55 V; differential ±0.3 V (p.5) | differential only | VBUS20 is at most 23.40 V (s120's bound): unchanged. 0.3 V is 48 A |
| Slope compensation, Eq. 26 (p.24): CSLOPE = gmSLOPE x L1 / (RSENSE x ACS) | **no**: RSENSE is R12 | 800 pF against C147's 680 pF: unchanged. If L1 runs near Isat, its inductance and the dead-beat value fall (INFERRED) |
| Cycle-by-cycle limits over R12: boost peak 20 / 24 / 28 A, buck valley 13.2 / 16.0 / 18.8 A (p.7) | no | unchanged; above Isat (B-1) |
| Hiccup: MODE to VCC selects none (p.20); when enabled it acts on 128 consecutive cycle-by-cycle limits (p.17) | no | a sustained overload stays in a limit indefinitely, now at the higher currents of section 3 |

## 6. Owner questions: only remedies that change a requirement

By the owner's amendment, a remedy that charges below a source's available power is an engineering choice while the approved
requirements stay met. Component selection and Kelvin routing are engineering tasks. **Every correction in section 2 has an
engineering form that changes no requirement, so no question is asked now.** Three remedies would change one if an engineer
chose them:

| Remedy, if chosen instead of the engineering form | Requirement it changes | Consequence |
|---|---|---|
| Raise the input floor so L1 needs no new part or schedule (B-1) | **REQ-015**: "A 9 to 36 V vehicle and shore input runs the kit and charges the pack" | Full charge current needs VIN_RAW of **11.0 V** or more (`.out` 6). Inputs from 9.0 to 11.0 V (a 12 V system's low end) would leave REQ-015. No energy is lost on the reference day, where the tracker holds 15.1 V |
| Cap U3 below 6.2 A permanently for B-1 to B-4 | **REQ-072** (M1) | About 20 Wh of lowest store per 0.1 A at WE (ENERGY-BASIS section 4). At the derated 4.00 A every lid fails by 369.9 to 566.0 Wh (section 4) |
| A part or bank that does not fit board A's place (B-1, B-2, B-4) | **CON-006** (the pack pocket bounded by board A's east edge at X +120), or **REQ-019** (the case never changes) if it went further | Not quantified: no part is selected. The question arises only if no fitting part exists |

**Already the owner's, not new here.** Option A(i)'s 200 W stage exceeds **REQ-016**, which allows at most 100 W into the
stage and 25 V open circuit (a1elec CHARGER.md section 2: "a requirement the owner rules on (9i of the energy record)"). The front end's demand puts 154.9 W into the stage in
service and 226.3 W at the maximum.

## 7. Downstream obligations (named, not done)

### 7a. Implementation: engineering tasks, each closing a class item

1. **R11 at 6.2 mOhm** in gen_sch_a.py and lcsc_fill.py, with an order code (C-2).
2. **U3's IIN_HOST.**
   - For the drawn circuit: the derated 4.00 A (A-1).
   - With the change: 6.2 A, only with item 3 and the VIN_RAW rule (A-2, B-5).
3. **Kelvin taps on R11 in the layout,** with kelvin_check PASS at 0.29 mOhm or less at 25 C (C-1).
4. **Re-declarations:** VBUS20 and FE_OUT (6.415 A typical, 9.370 A peak); VIN_RAW's _VIN_RAW_A with board E's _FE_A and
   _VIN_T (22.74 A at 9 V by the printed maximum); TRK_OUT; and pcb_sensitive.yaml's FE_ISNS text, which still names 3.80 A
   (B-3).
5. **L1:** a part rated for the highest permitted current at 9 V, or the schedule's 5.05 A setting at 9 V, recomputed once
   C-5 is held (B-1).
6. **The FETs:** hiccup (partial), or FETs and cooling rated for the fault, and board A's own RthetaJA (B-2, C-3); their fit
   on board A to be shown.
7. **VBUS20's bank,** re-sized by the generator's node analysis at 9.37 A, its fit on board A to be shown (B-4).
8. **C11 and C12:** a part with a maker's ripple rating (C-4).
9. **Board E's stage,** designed for 226.3 W in at the maximum or with the demand bounded (C-6).
10. **Regeneration of board A** (and of board E where re-declared), the gates and the evidence re-take.

### 7b. Physical verification: bench rows on a built board

1. **The front end's CC onset** with an electronic load past U3, at -20, 25 and 62 C. It must lie above U3's maximum plus
   0.06 A (A-1). Expected: the stacked band.
2. **In service,** with U3 at its setting and VIN_RAW at 9, 15.1, 24 and 36 V: the front end is not in CC (VSNS under
   43 mV; SS not pulled).
3. **R11's Kelvin error:** the voltage at U2 pins 14 and 13 against I x R11 four-wire, at most 0.29 mOhm x I (C-1).
4. **Temperatures at a forced limit** at 15.1 and 9 V: L1, Q2 to Q5, R11, the spring pins, C11 and C12, at or corrected to
   62.1 C air (B-2, C-3).
5. **L1's current waveform at 9 V** with U3 at full draw: no saturation knee, peak at most 90 % of Isat (B-1).
6. **The CC loop's step response** into the limit at 0.62 of the held gain: VBUS20 and the current, with no oscillation.
7. **A source stepped below U3's demand,** the panel or a simulator: VIN_RAW settles above 12 V and FE_PGOOD never drops
   (A-2, B-5).
8. **The bulk bank's worst can,** and C11 and C12 at 36 V: ripple current and temperature (B-4, C-4).
9. **Board E's tracker** at the front end's demand, once the stage exists (C-6).

## 8. What this rests on

- **ASSUMPTION:** R11's own temperature at most 100 C. The derating line supports it where the band's minimum is set (84 C).
- **The ISNS bias,** 3 uA, is TI's typical; no limit is printed.
- **Isat,** 17.5 A, is Coilcraft's typical figure at 25 C.
- **Figure 8's rise** is a pixel reading, taking the higher of the two gate-drive curves.
- **The bank's per-can figures** are the generator's, scaled in proportion to the current: INFERRED.
- **B-5's collapse** is INFERRED from the circuit and FW-A16's own words. Its energy bound takes a collapsed hour as zero.

## 9. CHECK-3's items and the owner's amendments, and where each is answered

| Item | Answer |
|---|---|
| B1, the bulk capacitors | 2b B-4: per can from the generator's analysis, U3's pulses included; 2.37 to 2.75 A in service, 3.47 to 4.01 A at the maximum (over). The pooled figure is withdrawn |
| B2, classification and closure | section 2: existing defects, proposal defects and missing evidence, each with its correction and closure; section 7 maps the implementation and the bench |
| 1, L1's bias drop | section 3 and `.out` 4: the peak with the 30 % drop on top of the minus 20 % tolerance, 17.11 / 18.62 / 26.00 A at 9 V |
| 2, R11's power with the ripple | section 3: 0.76 W at 15.1 V and 1.28 W at 9 V at the maximum, as an upper bound; within |
| 3, the parts of the 0.060 A | 2c C-9 and `.out` 3: U2's BIAS and gate charge, U3's own VBUS pin, R197 and the divider; the margin stays as closed |
| 4, p.24's filter limit | section 5: it is for CS and CSG; ISNS follows Figure 8-1 (p.17) and p.30 |
| 5, the spring pins' basis | section 3: the 0850 to 0853 sibling figure, and the 0858 page read by CHECK-3 |
| 6, the Kelvin budget at 25 C, and ENERGY-BASIS section 2 | 2c C-1: 0.29 mOhm at 25 C. ENERGY-BASIS section 2's drafted-R11 sentence now reads "with Kelvin taps on R11 (r11dep)" |
| 7, the layout statement's revision | 2d: revision A32, `b7e0d28f`, its pins read from the board file |
| Owner: three cases kept apart | sections 1 and 4 |
| Owner: the Kelvin classification | 2a (not an existing defect), 2c C-1 (implementation requirement and verification), 2d (A32 historical) |
| Owner: the derated setting | 2a A-1: coordination only, shown as the DERATED VARIANT beside the actual AS DRAWN case |
| CHECK-4 minor 1, the derated setting | 2a A-1 and section 4: 4.00 A (+0.052 / +0.033 A); its energy re-run; 4.05 A kept as the reason it was not chosen |
| CHECK-4 minor 2, L1's schedule | 2b B-1 and `.out` 6: the setting 5.05 A (maximum 5.18 A, 89.6 % of Isat), recomputed once C-5 is held |
| CHECK-4 minor 3, the collapse bound | 2b B-5: the restart latch, U3's 3.25 A reset, and the sub-hour dip named beside the bound |
| CHECK-4 minor 4, A-2's status | 2a: established from the netlist and the makers' documented behaviour, mechanism INFERRED, 7b.7 confirms; the defect sits in E1's setting |
| CHECK-4 minor 5, B-2's mechanism | 2b B-2: hiccup (partial) or FETs and cooling rated for the fault; B-2's and B-4's fit on board A not yet shown |
| Owner: questions only for requirement changes | section 6 |
| Owner: energy only through an adequate path counts | section 4: nothing is demonstrated capability; each row names its case |

**This is not the independent check.** The next check follows it.
