accepted: no

# CHECK-3: CHECK-2's minors (task 1) and the R11 dependency (task 2), streams l3plane and r11dep, MESHSAT-1357

**An AI check, not a qualified review.** 30 September 2026, 03:50 CEST. Branch `fnd/l3plane`, tip `4e9fa869`
(confirmed). It is four commits on `ec415c09`:
- `c915ce19`, `cf423519` and `868c321f` answer CHECK-2's minors;
- `4e9fa869` adds `v2/docs/records/r11dep/` and the Milliohm HoJLR2512 sheet.

The owner's addendum of 30 September to this check is folded in: sections 3 to 9 below. The checker wrote none of the
branch. Prototype design: nothing is built, powered or measured.

**Verdict.**
- **Task 1 is accepted.** All seven minors are answered, and the figures are confirmed.
- **Task 2 is not accepted, for two blocking items.**
  - B1: the record calls the VBUS20 bulk capacitors WITHIN on a method that the tree's own analysis contradicts.
  - B2: the record does not yet classify its findings, or give its corrections closure criteria, as the owner's
    instruction requires. Section 7 supplies both.

  Every other figure of task 2 was recomputed and holds.

**How it was checked.**
- **The clone.** A shared clone at the tip (`_scratch/chk-energy3`, removed after the check), with the int16
  worktree's held files copied in as ignored files and never committed.
- **What was read:** the diff, `R11-DEPENDENCY.md`, `r11_dep.py` and its `.out`, the LCSC reading, and board A's
  netlist (`v2/ecad/pcb-a-power-a23/out/pcb-a-power.net`, sha256/16 `6c40250c47195ebb`) for every reference named.
- **The LM5176 sheet** is the applicable one. The held `v2/vendor/ti/lm5176-datasheet.pdf` (SNVSAI1D, revised August
  2021) is byte identical, sha256 `98191bec...`, to what `https://www.ti.com/lit/ds/symlink/lm5176.pdf` served at
  03:45 today. Pages read: 3, 5, 6, 7, 17, 20, 24, and the layout section.
- **The other makers' pages read:**
  - HoJLR2512 pp.1 to 4;
  - BQ25731 p.1, 9.6.22, REGN, the switching-current rows and ILIM_HIZ;
  - Coilcraft XAL1010 and XAL1510;
  - CSD19532Q5B pp.1, 3 and 6 (Figure 8 read by eye);
  - CSD17577Q5A and CSD17578Q5A (held);
  - Panasonic EEHZK p.2;
  - the Mill-Max page and the 0858 product page;
  - LT8705A input voltage regulation.
- **The checker's arithmetic:** `indep_r11.py` and `indep_round3.py`, outputs beside them. The balance of CHECK-1 and
  CHECK-2 is used, and no record script is imported.
- **Reruns.** All eight committed outputs rerun byte identical: `vbus20_range`, `curve_readings`, `r11_dep`,
  `energy_basis`, `weather_basis`, `plane_grid`, `reconcile_lid_panel` and `energy_runs`.

## 1. Blocking items

### B1. The VBUS20 bulk capacitors are called WITHIN "in every case" on an even split and without U3's input ripple; the tree's own per-can figures put the worst can over its rating at the highest permitted current

`r11_dep.out` 4 and R11-DEPENDENCY sections 4 and 6 treat the six EEHZK1V331P (C163, C178 to C180, C199, C200;
NETLIST) as one 16.8 A pool (6 x 2.8 A at 100 kHz and 125 C, MAKER p.2), and call 7.37 A and 10.77 A WITHIN.

The generator's own analysis of this node, in `gen_sch_a.py` lines 697 to 720 of the committed tree, disagrees:
- it counts the front end's output ripple and U3's pulsed input current into the same bank;
- it gives the worst can 2.10 A at the held 5.7 A maximum (75 %), and 2.43 A at a 2:1 ESR spread (87 %);
- it gives 1.85 A at 5 A, so the figure is linear in the front end's current (1.85 x 5.7 / 5 = 2.11).

Scaled from those committed figures (INFERRED):

| Case | Worst can | At a 2:1 ESR spread |
|---|---|---|
| Proposed in service, 6.415 A | 2.36 A (84 %) | 2.73 A (98 %) |
| **At the highest permitted current, 9.370 A** | **3.45 A (123 %)** | **3.99 A (143 %)** |

**Needed:** the bulk restated per can from the generator's figures, classified (b) (section 7, item B-4), and added to
7a and 7b.

### B2. The record's findings are not classified, and its corrections carry no measurable closure criteria

The owner's instruction to this check says: separate confirmed existing defects, defects the proposal introduces, and
missing evidence; missing evidence is not a failure; record corrections with measurable closure criteria. The record
does not yet do this. Examples:
- **The FETs** read "past 150 C" on the maker's 1 in2 pad, while board A's thermal resistance is missing evidence. At the
  9 V fault maximum, on the other hand, no realistic copper suffices.
- **L1** reads "NOT WITHIN" in service at 9 V against a TYPICAL, soft-saturation Isat, while its part temperature,
  105 C, is under the 165 C maximum.
- **The 200 W stage** reads "OVER 200 W": an output compared with an input rating, for a stage that is not designed.
- **The held circuit's own findings** sit in 7a, the change's implementation list.
- **Several 7a items** close on no measurable figure ("L1 needs a decision", "needs its own RthetaJA", "must be designed
  against").

**Needed:** carry section 7's classification and closure criteria, or an equivalent, into R11-DEPENDENCY before it goes
to the owner.

## 2. Minors

1. **L1's ripple ignores the inductance drop under DC bias.** It is taken at L minus 20 %, but Coilcraft note 5 defines
   Isat as a 30 % drop. With both drops:
   - the held maximum at 9 V is 17.11 A, 98 % of the typical 25 C Isat;
   - the proposed in-service peak is 18.62 A.
2. **R11's power is DC only.** Most of the output ripple crosses R11 to VBUS20: three ceramics sit on FE_OUT against
   eighteen and six cans on VBUS20. The estimate is about 0.4 W in service and 0.9 W at the maximum. That is still within
   3 W, and 2.10 W at 100 C.
3. **The 0.060 A of other loads has the wrong parts but a safe total.**
   - It omits U3's own VBUS pin, which does not pass R16: REGN's gate drive of Q7 and Q8 at 6 V and 460 kHz, the 2.2 mA
     light-load current and the ILIM divider, about 0.019 A.
   - It counts the LM5176's gate charge for four FETs at 62 nC (10 V), where two switch in boost at VCC's 7.35 V: about
     0.032 A in all.
   - The total is about 0.051 A, so 0.060 A is conservative. Name U3's pin.
4. **"The ISNS filter: at most 100 Ohm (p.24)" misreads p.24.** That ceiling is for the CS and CSG lines (R150, R151).
   For ISNS the sheet shows Figure 8-1's network and asks for the filter capacitor close to the pins.
5. **The spring pins' rating is a sibling's.** J_VR1 to J_VR4 are "Mill-Max 0858 class". The cited page rates the 0850
   to 0853 at 9 A at a 10 C rise and does not list the 0858. The 0858 page says "Inner Spring Dependent" (spring 82,
   "12 Amp", no rise stated). 5.85 A is under both; name the basis.
6. **The Kelvin budget is at operating temperature.** 0.371 mOhm at the copper's working temperature is 0.29 to 0.32
   mOhm at 25 C. ENERGY-BASIS section 2 should add "with Kelvin taps on R11 (r11dep)" to its drafted-R11 sentence.
7. **The layout statement should name its revision** (section 6): A32, commit `b7e0d28f`. On that board the ISNS and CS
   pins sit directly on the power nets.

## 3. The elements, named (NETLIST unless stated; the maker's pages SNVSAI1D and SLUSE66A)

| Resistor | Pins it feeds, and their nets | What it sets |
|---|---|---|
| **R11** 10 mOhm 1 % 2512, pin 1 on FE_OUT, pin 2 on VBUS20 | **ISNS(+) = U2 pin 14** on FE_ISNS_P via R160 100 Ohm from FE_OUT (R11.1); **ISNS(minus) = U2 pin 13** on FE_ISNS_N via R161 100 Ohm from VBUS20 (R11.2); C128 1 nF across | the LM5176's **AVERAGE OUTPUT current** limit: a gm amplifier (1 mA/V, p.7) discharges SS when VSNS passes 43 / 50 / 57 mV (p.7, Equation 4 p.17), which lowers VBUS20 |
| **R12** 5 mOhm 1 % 2512, pin 1 on FE_CS (the sources of Q3 and Q4), pin 2 on GND | **CS = U2 pin 16** on FE_CSF via R150 100 Ohm from FE_CS; **CSG = U2 pin 15** on FE_CSGF via R151 100 Ohm from GND; C123 across | the **CYCLE-BY-CYCLE** limits on the inductor current: boost **PEAK** 100 / 120 / 140 mV = 20 / 24 / 28 A (Q4 conducting); buck **VALLEY** 66 / 80 / 94 mV = 13.2 / 16.0 / 18.8 A (Q3 conducting) (p.7) |
| R119 100k, MODE to FE_VCC | U2 pin 4 | **no hiccup** (p.20: "MODE to VCC, No Hiccup"); a sustained overload stays in the average or cycle-by-cycle limit |
| **R16** 10 mOhm (RAC), VBUS20 to CH_ACN | **ACP = U3 pin 3** on CH_ACP_F via R147 10 Ohm from VBUS20; **ACN = U3 pin 2** on CH_ACN_F via R146 10 Ohm from CH_ACN | U3's **AVERAGE INPUT current** limit IIN_DPM: IIN_HOST 6.2 A, maximum +100 mA (9.6.22) or +2.5 % (p.1); clamp 6.35 A |
| R17 5 mOhm (RSR), VBAT to CELL_FUSED | SRP and SRN | U3's charge current into the base pack only |
| R19 16.5k over R20 34.8k from REGN | ILIM_HIZ = U3 pin 6 | a hardware input limit of about 7.2 A at REGN's 5.7 V minimum. **Not dependable**: at REGN's 6.0 V typical the pin sits at 4.07 V, above the 4.0 V at which the maker says the pin is disabled (9.6.22) |

## 4. The currents, compared at the same node

- **R11's node.** The current through R11 is the front end's AVERAGE OUTPUT current, from FE_OUT into VBUS20. Its
  average is exactly the sum of the VBUS20 loads, since capacitor currents average to zero:
  - U3's average input current through R16, which IIN_DPM regulates;
  - U3's own VBUS pin;
  - U2's BIAS;
  - R197 and the R6 and R7 divider;
  - the bleed R202 to R205 (4 x 510 Ohm) is off while FE_RUN is high.

  No converter loss lies between R16 and R11, which sit on one node. **So the 0.378 A margin compares like with like:**
  6.793 A (R11's stacked minimum) against 6.355 A (U3's input maximum) plus about 0.05 to 0.06 A of other loads.
- **The front end's AVERAGE INPUT current** at VIN_RAW is P_out / (0.93 x VIN_RAW): 9.54 A at 15.1 V and 16.01 A at 9 V
  in service. No R11 limit applies to it.
- **The INDUCTOR current** in boost equals the input current on average; its peak adds half the ripple. The R12 limits
  act on it: peak in boost, valley in buck.

## 5. Both ends of the tolerance (the proposal: R11 6.2 mOhm, U3 IIN_HOST 6.2 A)

**The minimum end: enough current for the required load.**
- At R11's node: 6.793 A stacked minimum, against 6.415 A needed at most. **+0.378 A**, with Kelvin taps of at most
  0.371 mOhm. It holds at both ends of TJ, since VSNS is specified from minus 40 to 125 C.
- **At 9 V:** L1 averages 16.01 A. Its peak is 17.84 A, or 18.62 A with the bias drop, under the 20 A minimum
  cycle-by-cycle limit, so the front end can deliver. The limit would bind below about 8.0 V, under the 7.86 to 8.31 V
  latch.
- **At 15.1 V:** peak 11.04 A.
- **At 36 V:** in buck, L1 carries 6.42 A against the 13.2 A minimum valley limit.
- **Held, for comparison:** 4.212 A against 6.415 A needed (minus 2.203 A). At GEN's own setting it is 4.31 A (minus
  0.098 A).

**The maximum end: the whole path at the highest permitted current**, 9.370 A out: R11 at minus 1 %, TCR, the bias,
and VSNS 57 mV. At a part at the minimum cycle-by-cycle limit, 9 V limits the output to 7.28 A (typical 8.88 A); a part
at the maximum limit (28 A) reaches 9.37 A.

| Part (NETLIST) | Maker's rating | 36 V, the highest input (buck) | 15.1 V (boost) | 9 V, the floor (boost) |
|---|---|---|---|---|
| L1 XAL1010-103ME | Isat 17.5 A typical, 25 C, 30 % drop; Irms 15.5 A at 40 K; part at most 165 C | peak 12.50 A, 77 C: within | peak 15.43 A (16.07 A with the bias drop), 95 C: within | peak 25.21 A, 153 C: **past Isat**, under 165 C (core loss excluded) |
| Q2 CSD19532Q5B (buck top, on in boost) | 5.7 mOhm max at VGS 6 V; Figure 8 about 2.0 at 150 C; RthetaJA 50 C/W on 1 in2 2 oz; TJ at most 150 C | 1.41 W, TJ 132 C | 2.23 W at 150 C: needs RthetaJA of 39 C/W or less | 6.26 W: needs 14 C/W or less (3.78 W at the minimum peak limit, still under 24 C/W) |
| Q4, Q5 (boost switch, rectifier) | as Q2 | Q3 0.30 W, Q5 0.83 W | Q4 118 C, Q5 138 C | 4.36 and 2.70 W: need 20 and 33 C/W or less |
| Bulk, 6 x EEHZK1V331P | 2.8 A per can | within | about 1.9 to 2.2 A a can (INFERRED) | **about 3.45 to 3.99 A on the worst can (B1)** |
| C11, C12 FS32X106K101EGG | **no maker ripple rating held** | 4.97 A rms together | 0.86 A | 1.06 A |
| R11 HoJLR2512 (6.2 mOhm, same series) | 3 W to 70 C, 2.10 W at 100 C; 5 x P for 5 s | 0.55 W DC (about 0.9 W with ripple): within | within | within |
| J_VR1 to J_VR4 | 9 A at 10 C (085X page); 0858 "12 Amp" | 1.46 A a pin | 3.48 A | 5.85 A: within |
| Board A copper declarations | VBUS20 6.0 / 8.0 A; VIN_RAW 14.10 A | passed (9.37 A) | passed | VIN_RAW 23.38 A: passed |
| Board E, the source | the 200 W stage is **not designed**; the drawn E7 stage is a 100 W, 12 V panel stage (TRK_OUT declared 10.33 A; L1 XAL1510-103 Isat 26.3 A; R5 5 mOhm, VCS 13.8 to 20.4 A; Q3 and Q5 BSC028N06NS 60 V) | the vehicle can supply it: LM5069 6.15 A x 36 V = 221 W | TRK_OUT 13.94 A, at the drawn stage's minimum limit; the stage's input 226 W | only with the tracker in its limit and the vehicle together |

## 6. The layout, tied to the revision read

The only reading is `v2/ecad/pcb-a-power-a23/routed/kelvin_check.verdict.json`:
- kelvin_check, ADVISORY, verdict FAIL, 2026-09-20T05:58:19Z, tools tree `cb58607186f3fb15`;
- on board `v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb`, sha256/16 **`58e26c67987b1daa`**;
- **A32**, last committed `b7e0d28f` on 15 Sep 2026, routed: 4854 segments, 902 vias.

On that board, **U2 pin 14 (ISNS+) is on FE_OUT and pin 13 (ISNS minus) on VBUS20 directly**, as are CS on FE_CS and
CSG on GND: it has no FE_ISNS nets and no R160, R161, R150 or R151. The reading: 26.62 mV of copper drop from R11.1 to
U2.14 and 2.16 mV from R11.2 to U2.13, at dc_drop's solved current. That is 4.80 mOhm at 6.0 A, or 7.57 mOhm at 3.80 A.

This is a finding about A32 only. The current netlist has no layout, so its taps are missing evidence (section 7, C-1).

## 7. Classification, corrections and closure criteria

### (a) Confirmed existing defects of the circuit as drawn (board A generated, R11 10 mOhm)

**A-1. The front end cannot pass the charge current the design asks.**
- The stacked limit is 4.212 / 5.000 / 5.810 A. The generator's own VBUS20 intent declares R16 at 6.0 A ("BQ25731 up to
  8 A"), and M1 needs 6.1 to 6.355 A (M1 NOT MET by 326.6 to 522.4 Wh, GEN).
- Even GEN's own E1 setting (4.15 A, 4.25 A maximum, plus 0.06 A) is 0.098 A over the stacked minimum.
- **Correction.** For the drawn circuit, E1's IIN_HOST at 4.05 A nominal or less (4.05 x 1.025 + 0.06 = 4.21 A). For
  M1, the proposal with every B item closed.
- **Closure.** The stacked minimum of the fitted R11 is at least U3's maximum plus the other loads. The front end's CC
  onset, measured with an electronic load past U3 at minus 20, 25 and 62 C (7b.1), is above U3's maximum plus 0.06 A.

**A-2. A32's ISNS taps are not Kelvin connections** (section 6). On that layout the held limit is about 2.8 to 3.4 A
typical.
- **Correction:** Kelvin taps from R11's pads, per the maker's p.3 sensing-trace pad, into R160 and R161.
- **Closure:** kelvin_check on the regenerated board reads at most 0.29 mOhm at 25 C between the pads and the filter
  landings. On the bench, the voltage across the pads and at U2 pins 14 and 13 differ by at most 2.4 mV at 6.415 A
  (7b.3).

**A-3. VIN_RAW has no fixed input limit, so it collapses when the source is short.** The front end is a constant-power
load, and U3 holds VBUS20 at a fixed IIN. When the source gives less than U3 asks, the source sags: the vehicle entry's
LM5069, which FW-A16 names ("a limiting constant-power front end collapses the bus"), or the panel tracker's FBIN loop
(LT8705A: "VC will be reduced, thus reducing current draw from the input supply"; INFERRED). VIN_RAW then walks down to
the 7.86 to 8.31 V latch, through 9 V at full current.
- FW-A16 as written scales IIN_HOST with VIN_RAW, and so bounds it. The drafted fixed 6.2 A does not; see B-5.
- **Correction:** keep a VIN_RAW-dependent IIN_HOST rule for every source.
- **Closure:** on the bench, with the panel source (or a simulator) stepped below U3's demand, VIN_RAW settles above
  12 V and FE_PGOOD never drops.

### (b) Defects the resistor-only proposal introduces (R11 6.2 mOhm with IIN_HOST 6.2 A, nothing else changed)

**B-1. L1 runs past its typical Isat in service at the 9 V floor.** The peak is 17.84 A, or 18.62 A with the bias drop,
against 17.5 A typical at 25 C. The held maximum was 16.33 A (17.11 A).
- At the highest permitted current the peak is 25.21 A, below the 28 A peak limit of a maximum part. So the
  cycle-by-cycle limit, 20 A minimum, does not keep L1 out of saturation.
- It is not a demonstrated failure: the part is at 105 C, under 165 C, and saturation is soft. But the design runs past
  its saturation point.
- **Correction:** an inductor whose Isat at the part's temperature is above the peak at the highest permitted current
  at 9 V, with margin; or IIN_HOST scheduled on VIN_RAW so that the in-service peak stays under Isat at 9 V.
- **Closure:** L1's current waveform at 9 V with U3 at full draw shows no saturation knee, and its peak is at most 90 %
  of Isat at the part's temperature (7b.5).

**B-2. The FETs at the highest permitted current at 9 V.** Q2 dissipates 6.26 W (3.78 W at a minimum-limit part), Q4
4.36 W and Q5 2.70 W. That needs an RthetaJA of 14 to 33 C/W, beyond what copper alone gives a 5 x 6 mm SON (INFERRED).
In service at 9 V, Q2 needs 30 C/W and Q4 38 C/W or less: missing evidence, C-3.
- **Correction:**
  - bound the fault state, for example with hiccup (MODE 93.1 kOhm to AGND, p.20), which acts on cycle-by-cycle
    events, or an input-side limit at low VIN_RAW;
  - or FETs and cooling rated for it.
- **Closure:** TJ at most 150 C, or the project's derating, at the highest permitted current at 9, 15.1 and 36 V in
  62.1 C air, measured or from board A's own thermal resistance (7b.4).

**B-3. The copper declarations are passed.** VBUS20 and FE_OUT reach 6.415 A in service and 9.370 A at the maximum,
against 6.0 / 8.0 A. VIN_RAW reaches 16.01 A in service and 23.38 A at the maximum at 9 V, against 14.10 A.
- **Correction:** re-declare and regenerate (7a.4).
- **Closure:** the gates (dc_drop, derate, the track widths) read PASS on the regenerated board at the new declarations.

**B-4. The VBUS20 bulk at the highest permitted current** (B1). The worst can is about 3.45 to 3.99 A against 2.8 A;
in service it is 2.36 to 2.73 A (84 to 98 %).
- **Correction:** re-run the generator's node analysis at 9.37 A and 9 V, and enlarge or rebalance the bank.
- **Closure:** every can at most 2.8 A (the maker's figure at 125 C) over the ESR bands at 9.37 A. The bench ripple and
  temperature of the worst can agree with it.

**B-5. A fixed IIN_HOST of 6.2 A drops FW-A16's VIN_RAW scaling** (A-3). It is INFERRED: whenever the array gives less
than about 144 W, the bus collapses to the latch instead of settling at the available power.
- The energy model's `min(available, cap)` presumes the opposite.
- **Correction and closure:** as A-3, for the proposal's setting.

### (c) Missing evidence (not a demonstrated failure)

| Item | What is missing | What closes it |
|---|---|---|
| C-1 | a layout of the current netlist, so no Kelvin reading of it | kelvin_check PASS at 0.29 mOhm or less at 25 C (A-2) |
| C-2 | the 6.2 mOhm HoJLR2512 order code | a catalogue answer: 1 %, 50 ppm/K or better, 3 W |
| C-3 | board A's own RthetaJA for Q2 to Q5 | a figure from the laid copper: 30 C/W or less for Q2 and 38 C/W for Q4 (in service, 9 V); 39 C/W for Q2 at 15.1 V at the maximum |
| C-4 | C11 and C12's ripple rating and DC-bias derating at 36 V | the maker's figure, at least 2.5 A a part, or a part that has one (7b.8) |
| C-5 | L1's Isat against temperature (Coilcraft's derating page, not held) | the maker's derating page read at the part's temperature |
| C-6 | board E's 200 W stage (not designed) | a design that takes 226 W in at the maximum, or bounds the front end's demand |
| C-7 | U3's input-current minimum for 10 mOhm (no row printed; 6.1 A INFERRED) | the maker's figure, or a bench reading |
| C-8 | the three undocumented efficiencies (ENERGY-BASIS) | the maker's figures for these circuits, or measurement |

### Which corrections are the owner's

All of the above are engineering tasks, except where a remedy:
- **raises the 9 V service floor** (REQ-015), a requirement change, if chosen for B-1 or B-2;
- **does not fit board A's envelope** under the ruled stack (a larger L1, FETs or bank), an enclosure constraint;
- **reduces charge at low VIN_RAW** beyond what the source can give. Scheduling to the available power (A-3, B-5)
  does not reduce service.

## 8. The three cases, kept apart

**1. The circuit as drawn (GEN).**
- The front end limits first: 4.212 to 5.810 A.
- M1 NOT MET: 494.7 / 522.4 Wh (4S9P), 357.5 / 383.8 (4S14P), 326.6 / 352.8 (4S15P) unserved.
- Its defects: A-1 to A-3.

**2. The resistor-only proposal.**
- The minimum end holds: +0.378 A, conditional on Kelvin taps (C-1).
- The maximum end is not demonstrated: B-1 to B-5, and C-3 to C-6.

**3. The corrected power path the energy model assumes.** The NOM and WE results of ENERGY-BASIS are demonstrated
capability only with all of these:
- R11 at 6.2 mOhm with Kelvin taps (A-2, C-1, C-2);
- IIN_HOST 6.2 A with a VIN_RAW-dependent rule that makes the charge path take `min(available, cap)` (A-3, B-5);
- the 200 W stage (C-6);
- the power path rated or bounded at the highest permitted current (B-1 to B-4, C-3 to C-5);
- the three efficiencies established (C-8; WE is conditional on them).

Until then those results are conditional figures, not capability.

## 9. What holds

### Task 1: CHECK-2's minors

| Minor | Author | Checker |
|---|---|---|
| 1 | 0.9924 to 0.9937; 4S14P WE-MKR 216 / 213 / 147 | 0.9924 / 0.9925; 216 / 213 / 147 (4S15P 255 / 252 / 188) |
| 2 | TYP 128 / 172 / 220, WAB 136 / 184 / 228 cells, lids and masses | identical (count percentiles 4S25.16P, 4S36.70P, 4S48.43P; 4S27.63P, 4S39.37P, 4S50.64P) |
| 3 | 1.42 to 2.54 (Wh), 1.52 to 2.71 (cells) | 1.52 / 2.05 / 2.62, 1.62 / 2.19 / 2.71. **The author is right:** CHECK-2's 1.57 to 2.76 came from the old counts |
| 4 | 14.0 to 22.0 % STOP, 13.2 to 21.5 % COMB | confirmed |
| 5 | item 5: 12.2 to 12.6 Wh | confirmed |
| 6 | 8.2 against 8.7 A | 8.18 and 8.69 A |
| 7 | WE a case definition | done |

### Task 2: the figures

- The record's section 1 matches the netlist, and section 3 above adds the pin polarities.
- The stacked bands, the margins, the Kelvin budget and GEN's minus 0.098 A all reproduce.
- The L1, Q2, board E and R11 figures reproduce.
- The LM5176 settings, from pp.5, 7, 17, 20 and 24: R11 sets only the average output limit; the CC gain is 0.62 of the
  held loop's; slope compensation uses R12 and L1 (800 pF by Equation 26, against C147's 680 pF); the cycle-by-cycle
  limits and the sense range are unchanged; there is no hiccup.
- Held and conditional are kept apart in the record's section 6. 7a and 7b are separate. Nothing is implemented, and
  no file under `v2/ecad/` is changed.
- The 6.2 mOhm order code is stated NOT ESTABLISHED.

### Hygiene

- No U+2013 or U+2014, no host names and no user paths in the added lines.
- No ignored file is committed. The Milliohm sheet is 3976143 bytes, sha256 `3224518d...`, matching its `sources.txt`
  line, and carries no rights term.
- `pcb_requirements.yaml` is untouched.
- The four commits are in the owner's name with no trailer.

## 10. Figures beside theirs

| Figure | Theirs | Checker |
|---|---|---|
| Held / proposed stacked band | 4.212 / 5.000 / 5.810; 6.793 / 8.065 / 9.370 A | same |
| U3 maximum; demand at R11's node | 6.355; 6.415 A | same (other loads about 0.051 A by parts, 0.060 conservative) |
| Margin proposed; held; GEN | +0.378; minus 2.203; minus 0.098 A | same, like with like at R11's node |
| Kelvin budget | 0.37 mOhm | 0.371 mOhm working; 0.29 to 0.32 mOhm at 25 C |
| A32 tap copper | 4.8 to 7.6 mOhm | 4.80 to 7.57 mOhm, board `58e26c67`, A32 |
| L1 peak at 9 V: held max; in service; maximum | 16.33; 17.84; 25.21 A | same; 17.11; 18.62; 26.00 A with the bias drop |
| Minimum end at 9 V against the 20 A peak limit | not stated | 17.84 (18.62) A: the front end delivers |
| Q2 at 150 C: 15.1 V max; 9 V held max; 9 V in service; 9 V max | 2.23; 2.42; 2.95; 6.28 W | 2.23; 2.42; 2.95; 6.26 W (3.78 W at a minimum-limit part) |
| Bulk, worst can: in service; maximum | 7.37 A and 10.77 A of 16.8 A, WITHIN | 2.36 to 2.73 A (84 to 98 %); 3.45 to 3.99 A, over 2.8 A |
| R11 power: in service; maximum | 0.26; 0.55 W | about 0.4; 0.9 W with ripple, within |
| Board E at the maximum | 210.5 W "over 200 W" | 210.5 W out of the stage, 226.3 W into it; the 200 W stage is not designed (C-6) |
| E1 setting for the drawn circuit | not given | IIN_HOST at 4.05 A nominal or less |
| LM5176 sheet | SNVSAI1D | byte identical to TI's current symlink |

Rerun from this folder against a checkout of `fnd/l3plane` with the held files present: `python3 indep_r11.py` and
`python3 indep_round3.py <checkout>`.
