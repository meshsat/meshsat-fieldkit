# Board A's R11: the held circuit and the change Option A(i) depends on (stream r11dep, MESHSAT-1357)

The owner's instruction of 30 September 2026: "Keep the current-limit resistor dependency explicit. Check the proposed
setting, tolerances and consequences for the affected power path, component ratings and thermal margins using manufacturer
sources. Distinguish performance of the held circuit from performance conditional on the proposed change. Track
implementation and physical verification separately."

**Prototype design, desk arithmetic.** Nothing here is built, powered or measured. No generator is edited, no requirement
changes, nothing is implemented. Every number comes from `r11_dep.py` and its output `r11_dep.out` (section numbers below
are the output's), and carries its basis:
- **MAKER (page)**: a maker's document in `v2/vendor/`, read from its text layer, or by pixel for a plotted curve;
- **NETLIST**: board A's or board E's committed netlist;
- **MODELED**: the energy model's records;
- **INFERRED**: a stated method applied to the above;
- **ASSUMPTION**: a figure no document gives.

This page is the author's record. It is **not** the independent check, which follows it.

Run from the repository root: `python3 v2/docs/records/r11dep/r11_dep.py > v2/docs/records/r11dep/r11_dep.out`.
It is deterministic, and it refuses with exit 3 if any pinned input differs.

## 1. What R11 is (NETLIST, `.out` 1)

- **R11** is 10 mOhm, 1 %, 2512, between FE_OUT and VBUS20. It is the LM5176 U2's **average** current sense (ISNS), in
  series with the front end's output.
- **The ISNS filter:** R160 and R161 (100 Ohm) and C128 (1 nF) take it to U2 pins 14 and 13.
- **R12** (5 mOhm) is a different resistor: the cycle-by-cycle CS sense.
- **The switching parts:** L1 is an XAL1010-103ME. Q2 to Q5 are CSD19532Q5B.
- **VIN_RAW's parts:** C11 and C12 (10 uF 100 V X7R 1210) and the spring pins J_VR1 to J_VR4. Board A's VIN_RAW has **no fuse**.
- **Other R11 facts:**
  - U2's BIAS pin is on VBUS20, so its supply current also passes R11.
  - MODE is strapped to VCC, which gives no hiccup.
- **Board E's sources:**
  - the vehicle entry: F1 and the LM5069 U6;
  - the LT8705A tracker: R5 5 mOhm, its F2 on the panel input.
  - They are ORed through U4 and Q2.
- 13 of 13 netlist facts hold.

**The part (MAKER).** The held R11 is bought as C2903468. LCSC's answer (`inputs/lcsc-C2903468-2026-09-30.json`) names it
Milliohm **HoJLR2512-3W-10mR-1%**. The maker's sheet (`v2/vendor/passives/milliohm-hojlr2512-series.pdf`, filed with this
record) gives:
- 3 W from 0.5 to 500 mOhm (p.1);
- TCR +-50 ppm/K from 2 to 500 mOhm (p.2);
- a range of -50 to +170 C, derated linearly from 70 C (100 %) to 170 C (0 %) (p.2);
- rated current sqrt(P/R) (p.3);
- a short-time overload of 5 x rated power for 5 s, and a load life of 1000 h at rated power and 70 C, each within +-1 % (p.4);
- a pad drawing that shows separate sensing traces (p.3).

The proposed 6.2 mOhm is rated here as the same series (HoJLR2512-3W-6.2mR-1% by the maker's part-number scheme).
**Its order code is not established.**

## 2. The limit bands (`.out` 3)

The limit is ICL(AVG) = VSNS / R11: LM5176 Equation 4 (p.17), with VSNS **43 / 50 / 57 mV** over TJ -40 to 125 C (p.7).

The stack adds four tolerances:
- R11's own +-1 % (MAKER);
- its TCR of 50 ppm/K over 75 K. R11 sits between the in-use minimum of -20 C and an **ASSUMED** 100 C: the worst inside
  air of 62.1 C plus its own heating, 0.26 to 0.55 W in a 3 W part;
- the ISNS pin bias of 3 uA (typical; **no limit is printed**) over the 100 Ohm filter: +-0.3 mV, INFERRED;
- what else passes R11 besides U3: 0.060 A (INFERRED; U2's BIAS current and gate charge, R197 and the divider).

| | printed band (VSNS / R11) | stacked band, min / typ / max | through R11 in service | margin, stacked minimum over service |
|---|---|---|---|---|
| **held**, R11 10.0 mOhm | 4.30 / 5.00 / 5.70 A | **4.212 / 5.000 / 5.810 A** | U3's 6.355 A maximum + 0.060 = 6.415 A asked | **-2.203 A: the front end limits first** |
| **proposed**, R11 6.2 mOhm | 6.94 / 8.06 / 9.19 A | **6.793 / 8.065 / 9.370 A** | 6.415 A | **+0.378 A** |

**U3's maximum is 6.355 A.** It is the larger of two errors on the 6.2 A setting: 100 mA (BQ25731 p.80) and +-2.5 % (p.1).
The energy model's entry E2 carries the printed minimum, 6.94 A. The stacked 6.79 A is still above U3, so **no energy
result moves**.

**The held circuit at its own generated setting.** GEN sets U3 to 4.15 A, maximum 4.25 A. With the other loads, 4.310 A
passes R11, against the stacked minimum of 4.212 A: **-0.098 A**. The record's 50 mA margin was taken against the printed
4.30 A. With the other loads and the stacked band it is gone, so even at GEN the held front end can limit first.

**The taps, a condition of every band above.** VSNS over R11 alone holds only for a Kelvin connection.
- **The last reading.** kelvin_check read the routed board in the tree (sha256/16 58e26c67, ADVISORY, 20 Sep 2026). That
  board was laid before the ISNS filter entered the netlist. It found:
  - 26.62 mV of copper drop between R11.1 and U2.14;
  - 2.16 mV between R11.2 and U2.13.
- **Both drops add to the sensed voltage** (INFERRED): R11.1 is FE_OUT's only sink and R11.2 is VBUS20's only source.
- **Their size.** At dc_drop's solved current they are 4.8 to 7.6 mOhm together, as large as R11 itself. The solved
  current is FE_OUT's declared 6.0 A; pcb_sensitive.yaml's text names 3.80 A.
- **The limits on that board** would be about 2.8 to 3.4 A (held) and 3.6 to 4.5 A (proposed), typical. **Both are under U3.**
- **The proposed margin tolerates at most 0.37 mOhm** between R11's pads and its two taps together: 2.4 mV at 6.415 A,
  4.8 % of the 50 mV scale.

**Kelvin taps on R11 are therefore a condition of the change, not a refinement.**

## 3. M1, the held circuit against the change (MODELED, `v2/docs/records/l3plane/energy_basis.out` section 5, 40/0)

| lid | held (GEN), TYP / WAB | conditional, NOM TYP / WAB (COMB/EACH) | conditional, WE TYP / WAB (COMB/EACH) |
|---|---|---|---|
| 4S9P | NOT MET, 494.7 / 522.4 Wh unserved | NOT MET, 165.7 / 172.6 Wh unserved | NOT MET, 169.2 / 176.1 Wh unserved |
| 4S14P | NOT MET, 357.5 / 383.8 Wh unserved | 93.7 (Y/Y) / 75.7 (Y/Y) Wh | 44.0 (Y/N) / NOT MET, 10.8 unserved |
| 4S15P | NOT MET, 326.6 / 352.8 Wh unserved | 125.2 (Y/Y) / 106.8 (Y/Y) Wh | 74.3 (Y/Y) / 19.5 (Y/N) Wh |

**Every case of that file except GEN presumes the change.** WE is itself conditional on three undocumented efficiencies
(ENERGY-BASIS 1a).

## 4. The power path at the new currents (`.out` 4)

**The three currents:**
- the held limit's maximum, 5.810 A;
- the proposed in service, 6.415 A;
- the proposed limit's maximum, 9.370 A.

**The conditions:**
- The front end's output is taken at VBUS20's 20.887 V maximum, efficiency 0.93 DECLARED.
- VIN_RAW is taken at three points:
  - 15.1 V, the tracker's output, the lowest bus a source holds at full power;
  - 9.0 V, REQ-015's service floor and the basis of board E's _FE_A. It is above the stage's UVLO (7.86 to 8.31 V
    falling). At these currents it is reached only with the tracker in its limit and the vehicle together;
  - 36 V (buck).
- The air is the worst inside air in use, 62.1 C (pcb_envelope.yaml).

**The methods (INFERRED):**
- L1's rise is the maker's 40 K at 15.5 A scaled by the square of the rms current; core loss is excluded.
- The FETs use RDS(on) at its maximum times Figure 8's rise, iterated to TJ on RthetaJA 50 C/W.
- The ripple is taken at L -20 % and fSW 175 kHz.

**The makers' ratings:**

| Part | Rating |
|---|---|
| L1 | Isat 17.5 A (typical, 25 C, 30 % drop); Irms 15.5 A at a 40 K rise; at most 165 C (Coilcraft p.1) |
| FETs | RDS(on) 5.7 mOhm maximum at VGS 6 V; RthetaJA 50 C/W on a 1 in2 2 oz pad; TJ at most 150 C (TI p.1, p.3) |
| Figure 8 (p.6) by pixel | the higher of the VGS 6 V and 10 V curves: 1.18 / 1.36 / 1.56 / 1.76 / 2.01 at 50 / 75 / 100 / 125 / 150 C |
| Bulk | 6 x EEHZK1V331P, 2.8 A rms each at 100 kHz, 125 C (Panasonic p.2) |
| Spring pins | 9 A at a 10 K rise (Mill-Max p.28) |

| Part | held, 5.810 A | proposed in service, 6.415 A | proposed maximum, 9.370 A |
|---|---|---|---|
| **L1 at 15.1 V** (peak / rms / part) | 10.14 / 8.68 A / 75 C: within | 11.04 / 9.58 A / 77 C: within | 15.43 / 13.96 A / 95 C: within |
| **L1 at 9 V** | 16.33 / 14.54 A / 97 C: within | **17.84 / 16.04 A: NOT within** (peak over Isat, rms over 15.5 A) | **25.21 / 23.41 A / 153 C: NOT within** |
| **L1 at 36 V** (buck) | 8.94 / 6.08 A: within | 9.55 / 6.67 A: within | 12.50 / 9.54 A: within |
| **FETs at 15.1 V** (TJ) | Q2 95, Q4 95, Q5 84 C | Q2 104, Q4 98, Q5 90 C | **Q2 past 150 C** (needs RthetaJA <= 39 C/W); Q4 118, Q5 138 C |
| **FETs at 9 V** | **Q2, Q4 past 150 C** (need <= 36, 44 C/W); Q5 103 C | **Q2, Q4 past 150 C** (need <= 30, 38 C/W); Q5 115 C | **Q2, Q4, Q5 past 150 C** (need <= 14, 20, 33 C/W) |
| **FETs at 36 V** (buck) | Q2 108, Q3 68, Q5 77 C | Q2 112, Q3 69, Q5 80 C | Q2 132, Q3 77, Q5 103 C |
| **R11** (I2R at +1 %) | 0.34 W | 0.26 W | 0.55 W |
| **input caps C11, C12** (rms, 15.1 / 9 / 36 V) | 0.86 / 1.06 / 3.39 A | 0.86 / 1.06 / 3.65 A | 0.86 / 1.06 / 4.97 A |
| **bulk on VBUS20** (worst, at 9 V) | 6.68 A | 7.37 A | 10.77 A |
| **J_VR1 to J_VR4** (a pin, even share, worst at 9 V) | 3.62 A | 4.00 A | 5.85 A |
| **front end's input power** | 130.5 W | 144.1 W | 210.5 W |

**How to read the table:**
- **R11.** Its 3 W is not derated at 62.1 C (2.10 W at an assumed 100 C). The 5 s overload is 49 A at 6.2 mOhm. It is
  WITHIN in every case.
- **The input capacitors (C11, C12).** No maker ripple rating is held for FS32X106K101EGG, so every figure for them is
  **NOT ESTABLISHED**.
- **The bulk on VBUS20:** WITHIN in every case. The six parts' 16.8 A is shared with C13 to C15 on FE_OUT.
- **The spring pins:** WITHIN in every case.
- **The FETs.** At the 9 V floor they are past 150 C on the maker's 50 C/W pad figure **already in the held circuit at its
  limit's maximum**, so this is not new with the change. What the change adds: at 9 V the in-service current (U3 at its
  maximum) puts Q2 and Q4 past it, and at the new maximum Q2 is past it at 15.1 V too. The maker's RthetaJA is for a
  1 in2 2 oz pad, not board A's copper. The board's own figure is **not established**.
- **L1.** At the 9 V floor the change puts L1 **past its typical Isat in service**, and past its 40 K Irms. The held
  circuit's own limit kept L1 at 16.33 A peak there. At the new maximum and 9 V, the cycle-by-cycle boost limit (20 / 24 /
  28 A peak over R12, LM5176 p.7) may end the cycle first:
  - L1's average is then at most 18.2 / 22.2 / 26.2 A;
  - the output is then 7.28 / 8.88 / 10.49 A (INFERRED);
  - **even at its minimum the peak passes Isat**, so the peak limit does not protect L1 from saturation.

**The copper** (decision 35's conservative model, `track_current.width_for_current`, external, 10 K rise):

| Conductor | held | proposed in service | proposed maximum |
|---|---|---|---|
| FE_OUT and VBUS20 | 3.4 mm at 1 oz / 1.7 mm at 2 oz | 3.9 / 1.9 mm | 7.2 / 3.6 mm |
| VIN_RAW at 15.1 V | 6.2 / 3.1 mm | 7.5 / 3.7 mm | 15.0 / 7.5 mm |
| VIN_RAW at 9 V | 16.1 / 8.0 mm | 19.3 / 9.6 mm | 38.6 / 19.3 mm |

The generators lay copper and rate parts to these declarations (INFERRED comparison):
- **VBUS20 (6.0 A typical, 8.0 A peak).** The held maximum, 5.810 A, is under both. The proposed in-service current,
  6.415 A, **passes the typical**. The proposed maximum, 9.370 A, **passes the peak**.
- **VIN_RAW (14.10 A,** board E's _FE_A = 5.7 A x 20.7 V / 0.93 / 9 V):
  - the held circuit, stacked, reaches 14.50 A at 9 V;
  - the proposed reaches 16.01 A in service and 23.38 A at the maximum;
  - _FE_A's own formula at the proposed printed maximum, 9.19 A, gives 22.74 A.
- **TRK_OUT (10.33 A).** At 15.1 V the proposed draws 9.54 A in service and 13.94 A at the maximum.

**VIN_RAW's sources:**
- **Board E's 200 W stage** belongs to Option A(i). It is **not designed** (a1elec CHARGER.md 2: its owner's). In service
  the front end asks 144.1 W: **within 200 W**. At the proposed maximum it asks 210.5 W, **over 200 W**. So in a fault where
  U3 does not limit, the stage or the array bounds the draw, not R11.
- **The tracker's own buck limit** (VCS over R5, LT8705A p.3) is 13.8 / 17.2 / 20.4 A, against 13.94 A at 15.1 V.
- **The panel fuse F2** sees about 6.6 A at the array's 34.3 V: under its 10 A.
- **The vehicle entry alone** passes at most its LM5069's 6.15 A, under F1's 8 A at 65 C (gen_sch_e.py). Below 23.4 V a
  vehicle alone cannot carry the proposed in-service 144.1 W; below 21.2 V it cannot carry the held maximum's 130.5 W
  either. On the vehicle alone, the front end's draw is bounded by the entry **whatever R11 is**.

## 5. The LM5176's other settings and R11 (`.out` 5, the maker's equations)

| Setting | Tied to R11? | Consequence of 6.2 mOhm |
|---|---|---|
| Average current limit, ICL(AVG) = 50 mV / RSNS (Eq. 4, p.17) | **yes, the one setting R11 sets** | the bands of section 2 |
| The CC loop: gm 1 mS (p.7) discharging SS (C7 4.7 uF) above 50 mV (7.3.6, p.17) | its gain per ampere scales with R11 | 0.62 of the held loop's gain (INFERRED); its response is a bench row |
| The ISNS filter: at most 100 Ohm (p.24); R160, R161 sit at it | no | unchanged; the bias offset of 0.3 mV is 48 mA at 6.2 mOhm, against 30 mA at 10 mOhm |
| The sense amplifier's range: common mode 0 to 55 V; differential +-0.3 V (p.5) | differential only | VBUS20 at most 23.40 V (s120's bound): unchanged; 0.3 V is 48 A, far beyond the path |
| Slope compensation, Eq. 26 (p.24): CSLOPE = gmSLOPE x L1 / (RSENSE x ACS) | **no**: RSENSE is R12, the CS resistor | 800 pF with p.24's example gm and gain, against C147's 680 pF: unchanged. If L1 runs near Isat its inductance falls, and so does the dead-beat value (INFERRED) |
| Cycle-by-cycle limits over R12: boost peak 20 / 24 / 28 A, buck valley 13.2 / 16.0 / 18.8 A (p.7) | no | unchanged; with the average limit raised, they bound L1 in an overload at a low VIN_RAW, and they sit above Isat |
| Hiccup: MODE to VCC selects none (p.20) | no | a sustained overload stays in the average or the peak limit indefinitely, now at section 4's higher currents |

s120's bus bound (23.40 V) rests on the peak limit and L1's energy, not on R11. It does not move.

## 6. Held against conditional, in one table

| | Held circuit (R11 10 mOhm, board A as generated) | Conditional on the change (R11 6.2 mOhm, U3 IIN_HOST 6.2 A) |
|---|---|---|
| Front end's limit (stacked) | 4.212 / 5.000 / 5.810 A | 6.793 / 8.065 / 9.370 A |
| Who limits the charge current | **the front end** (margin -2.203 A; -0.098 A even at GEN's own setting) | U3 (margin +0.378 A), **only with Kelvin taps on R11 of at most 0.37 mOhm** |
| M1, 4S14P / 4S15P, TYP | NOT MET, 357.5 / 326.6 Wh unserved | NOM 93.7 / 125.2 Wh; WE 44.0 / 74.3 Wh |
| M1, 4S14P / 4S15P, WAB | NOT MET, 383.8 / 352.8 Wh unserved | NOM 75.7 / 106.8 Wh; WE NOT MET 10.8 unserved / 19.5 Wh |
| M1, 4S9P | NOT MET | NOT MET |
| L1 at the 9 V floor | within (16.33 A peak) | **past typical Isat in service** (17.84 A); 25.21 A at the maximum |
| FETs on the maker's 50 C/W | past 150 C at 9 V (Q2, Q4) at the limit's maximum | past 150 C at 9 V in service; Q2 at 15.1 V at the maximum |
| R11's own power | 0.34 W of 3 W | 0.26 W in service, 0.55 W at the maximum, of 3 W |
| Input capacitors' ripple | not established | not established (up to 4.97 A at 36 V) |
| VBUS20 declaration (6.0 / 8.0 A) | inside | **passed** in service and at the maximum |
| VIN_RAW declaration (14.10 A) | passed at 9 V by the stacked band (14.50 A) | **passed** at 9 V (16.01 A in service) |
| Board E's 200 W stage | 130.5 W at most | 144.1 W in service; 210.5 W at the maximum |

## 7. Downstream obligations (named here, done by none of this)

### 7a. Implementation: the generator edit and the regeneration

1. **R11 in gen_sch_a.py and lcsc_fill.py.** R11 becomes 6.2 mOhm, a 3 W 2512 of +-1 % and 50 ppm/K or better, with an
   **order code established** from a catalogue answer.
2. **U3's IIN_HOST at 6.2 A** (entry E2, CHARGER.md) with the change, never without it. The held circuit keeps GEN's
   setting, and even that is 0.098 A over the stacked minimum.
3. **R11's taps as Kelvin connections**, at most 0.37 mOhm of copper between its pads and the ISNS filter, as the maker's
   p.3 pad drawing shows. kelvin_check must read PASS on the regenerated board.
4. **The re-declarations the new currents pass:**
   - VBUS20 and FE_OUT (6.415 A typical, 9.370 A peak);
   - VIN_RAW's _VIN_RAW_A with board E's _FE_A and _VIN_T (the printed maximum gives 22.74 A at 9 V);
   - TRK_OUT (13.94 A at the maximum; 12.3 A at the 200 W stage by CHARGER.md);
   - pcb_sensitive.yaml's FE_ISNS text (3.80 A).
5. **L1 at the 9 V floor.** L1 needs a decision:
   - an inductor with a higher Isat and Irms;
   - U3's input limit scheduled on VIN_RAW by the host;
   - or a service floor above 9 V for full charge current.

   The peak limit over R12 does not protect it (20 A minimum, above 17.5 A).
6. **The FETs' thermal path.** Board A needs its own RthetaJA for Q2 to Q5, from its laid copper. The maker's 1 in2 figure
   puts Q2 and Q4 past 150 C at 9 V even in the held circuit.
7. **The input capacitors' ripple rating.** The maker's figure is needed for FS32X106K101EGG, or a part that has one:
   3.65 A in service and 4.97 A at the maximum, for two parts at 36 V. Its DC-bias derating at 36 V is needed too.
8. **Board E's 200 W stage** (not designed) must be designed against the front end's 210.5 W maximum demand.
9. **The host's IIN_HOST per source.** On the vehicle alone below about 23 V, the entry, not R11, bounds the power.
10. **Regeneration of board A** (and of board E where re-declared), the gates and the evidence re-take. The energy model's
    E2 may carry the stacked 6.79 A minimum; no result moves.

### 7b. Physical verification: the bench rows, on a built board

1. **The front end's CC limit.** Measure it with VBUS20 loaded past U3, at -20 C, at 25 C and at the worst inside air.
   Expected: the stacked band, 6.79 to 9.37 A, and above 6.415 A.
2. **In service,** with U3 at 6.2 A and VIN_RAW at 9, 15.1, 24 and 36 V: confirm the front end is not in CC (VSNS under
   43 mV; SS not pulled). Record the current through R11.
3. **R11's Kelvin error.** Compare the voltage across R11's pads with the voltage at U2 pins 14 and 13, at a known current.
4. **Temperatures at a forced limit** (the proposed maximum) at 15.1 V and at 9 V: L1, Q2 to Q5, R11, the spring pins and
   C11 and C12, at or corrected to the worst inside air.
5. **L1's current waveform at 9 V** with U3 at full draw: the peak against Isat, and any saturation.
6. **The CC loop's step response** into the limit at 0.62 of the held gain: VBUS20 and the current, with no oscillation.
7. **The vehicle entry's interplay** at 9 to 24 V with U3 at 6.2 A: the LM5069's limit, its retry, and the stage's UVLO
   latch.
8. **The input capacitors at 36 V:** ripple current and temperature rise.
9. **Board E's tracker** at the front end's demand, once the 200 W stage exists.

## 8. What this rests on, and what it is not

- **ASSUMPTION:** R11's own temperature at most 100 C.
- **ISNS bias:** its 3 uA is TI's typical figure; no limit is printed.
- **Isat:** 17.5 A is Coilcraft's typical figure at 25 C.
- **Figure 8:** its rise is a pixel reading. It takes the higher of the two gate-drive curves.
- **The Kelvin reading** is on a routed board that predates the current netlist's ISNS filter. It shows how large a tap
  error has been on this board. It is not a reading of the next layout.
- **This is the author's record, not its check.** The independent check follows.
