# ENERGY-BASIS: the energy basis of layer 3's decisions L3-OD1, L3-OD2 and L3-OD4 (stream l3plane, MESHSAT-1357)

**Second issue, 30 September 2026**, branch `fnd/l3plane` (from `fnd/int16` at `d2084904`). It answers the independent
check `CHECK-1` of the first issue (`6a283b25`, accepted: no), which found two blocking items (B1, B2) and ten minors
(section 11 maps each to its answer). It also answers the owner's instruction of the same day on the weather basis: the
modelled historical coverage of all three lids on the corrected inputs (section 8), decision L3-OD6 as a quantified choice
(section 8a), and a bounded table of credible improvements (section 8b). **Third issue, 30 September 2026:** the
independent check `CHECK-2` of `ec415c09` accepted the second issue with seven minors; this issue answers them (section 11),
and three change figures the owner sees: the cell counts and multiples of section 8a, and one coverage row of section 8.
**Fourth issue, 30 September 2026:** it carries the owner's amendments of that day and CHECK-3 of `4e9fa869` (stream r11dep).
- **Three power-path cases are kept apart:** AS DRAWN, RESISTOR-ONLY and the CORRECTED PATH, with the DERATED VARIANT beside
  AS DRAWN (section 0).
- **Every Option A(i) figure of the earlier issues is the CORRECTED PATH's, and HYPOTHETICAL.** Its required corrections are
  listed prominently in section 0, and its tables are labelled so.
- **New figures:** `three_cases.py` gives M1 and the coverage for the other cases. No other output of this folder moves.

**What this page is.** It is the stream's own analysis for the owner's decisions, AI arithmetic, not a qualified review and
not the independent check. It is not a decision:
- no requirement, record or decision is changed (`pcb_requirements.yaml` is untouched);
- every operating condition below is PROPOSED, or CONDITIONAL where it rests on an undocumented figure, and none is accepted;
- nothing is bought, built, powered or measured.

**Labels.** Every figure carries its basis:
- **MAKER**: a maker's document and page, read by the script from its text layer;
- **NETLIST**: board A's or board E's committed netlist;
- **MODELED**: the energy model's arithmetic;
- **INFERRED**: derived from a maker's figures by a stated method, or a reading of a typical curve;
- **DECLARED** or **ESTIMATE**: a figure the records carry with no maker document behind it for this circuit.

**Where the figures come from.** The scripts in this folder print them; this page transcribes them:
- `vbus20_range.py` into `vbus20_range.out`;
- `curve_readings.py` into `curve_readings.out`;
- `energy_basis.py` into `energy_basis.out` (section numbers below are that file's unless another is named);
- `weather_basis.py` into `weather_basis.out` (sections 8, 8a and 8b);
- `three_cases.py` into `three_cases.out` (section 0: the power-path cases, fourth issue).

## 0. The three power-path cases (the owner's amendments of 30 September 2026; r11dep's R11-DEPENDENCY.md)

**What is kept apart.** The owner asked to distinguish "the circuit as drawn; the resistor-only proposal; any hypothetical
corrected power path used for feasibility calculations", and not to count "energy available only through an inadequate power
path as demonstrated capability". The electrical findings behind the cases are r11dep's. They are provisional until
independently checked.

| Case | What it is | M1 on the reference day at 40/0, TYP / WAB (MODELED, `three_cases.out` 2) | Coverage of 864 past September windows, TYP, no STOP (`three_cases.out` 3) |
|---|---|---|---|
| **(i) AS DRAWN** | R11 10 mOhm, U3 at 4.15 A (entry E1): the front end limits at 4.212 to 5.810 A | every lid NOT MET: 4S9P 494.7 / 522.4, 4S14P 357.5 / 383.8, 4S15P 326.6 / 352.8 Wh unserved (NOM inputs; at WE 422.1 to 616.7) | 0 for every lid |
| **(i') DERATED VARIANT** of (i) | U3 at 4.05 A: fixes the current-limit coordination ONLY; resolves nothing else | every lid NOT MET: 4S9P 523.7 / 551.5, 4S14P 386.5 / 412.7, 4S15P 355.5 / 381.7 Wh unserved (NOM; at WE 449.3 to 644.1) | 0 for every lid |
| **(ii) RESISTOR-ONLY** | R11 6.2 mOhm and U3 6.2 A, nothing else changed | **INCONCLUSIVE:** the path is not shown to carry the current. The result lies between a lower bound that takes r11dep B-5's inferred bus collapse (every lid NOT MET, 622.1 to 1079.9 Wh unserved at NOM) and case (iii) | between 0 to 2 windows and case (iii)'s figures |
| **(iii) CORRECTED PATH, HYPOTHETICAL** | the path the NOM and WE cases assume: `min(available, cap)` at U3's 6.2 A, with every correction below closed | the table of section 1: 4S14P and 4S15P meet at NOM; at WE conditionally | 4S14P 19.2 to 24.0 %, 4S15P 22.0 to 27.2 % (WE to NOM); 4S9P 0 |

**The corrections case (iii) assumes, none of them closed** (r11dep R11-DEPENDENCY.md section 2):
- Kelvin taps on R11 with at most 0.29 mOhm of shared copper at 25 C (C-1), and the 6.2 mOhm part's order code (C-2);
- a VIN_RAW-dependent IIN_HOST rule for every source, so the charge path takes what the source gives (A-2, B-5);
- L1 at the 9 V floor: a part rated for the peak, or the charge limit scheduled on VIN_RAW (B-1, C-5);
- the FETs' thermal path at the highest permitted current (B-2, C-3);
- VBUS20's bulk capacitors, over their rating at the highest permitted current (B-4);
- the copper declarations re-declared and the board regenerated (B-3);
- C11 and C12's ripple rating (C-4);
- board E's 200 W stage, not designed (C-6);
- the three undocumented efficiencies of section 3 (C-8): WE is conditional on them.

**So no result on this page is demonstrated capability.**
- Cases (i) and (i') fail M1.
- Case (ii) is inconclusive.
- Every table from section 1 on is case (iii) unless it names case (i).

## 1. What the owner is told, and the corrected comparison table

**In one paragraph.**
- **As drawn, no lid option meets M1**, and neither does the derated variant. Neither carries any past September window.
- **The resistor-only proposal is inconclusive** (section 0).
- **Everything that follows is the CORRECTED PATH, HYPOTHETICAL.** It holds only once r11dep's corrections listed in section
  0 are closed.

On that hypothetical path, with the charge bus, U3's limit and both chargers' efficiencies taken at their established worst,
M1 rests on three efficiencies that no maker document establishes for this circuit:
- board E's tracker stage and board A's front end, both DECLARED at 0.93 and "NOT PLOTTED" at these ratios;
- the pack's charge efficiency, INFERRED at 0.95 with "no held document".

Held at those values:
- **The QMX-out lid (4S15P)** meets on the 40 degree south plane and over a band of 30 to 50 degrees facing south to 15
  degrees west. But the band's edge holds only while the charge efficiency stays at or above 0.949 and the stage and the
  front end at or above 0.929, within about 0.1 of a percentage point of the declared figures. The whole band needs
  0.936 to 0.949 and 0.907 to 0.929.
- **The tablet-out lid (4S14P)** meets only if those efficiencies are better than declared: at 40 degrees south, a charge
  efficiency of 0.964 or a stage or front end efficiency of 0.952. So **the choice between the two lids at the worst
  inputs turns on figures no maker document supports.**
- **Keeping both functions (4S9P)** does not meet M1 in any case.
- **If each pack must stay above its own shutdown line**, rather than the two together, no band exists for either lid
  at the worst inputs.

The makers' own curves for similar circuits read higher than the declared figures (stage about 0.965, front end about
0.978, INFERRED). The cell sheet bounds the charge efficiency's resistive part at about 0.99 from above. But none of these
is a figure for this kit. **So M1 on Option A(i), even on the corrected path, depends on efficiencies no maker
document establishes. A band built on them is conditional, not a basis for a requirement.** It becomes one only when those efficiencies are established
on the prototype or by the makers' figures for these circuits. All of this is on one mean September day at Leiden.

**On the weather** (case (iii), the corrected path, HYPOTHETICAL). Every past September 72 hour window of 2005 to 2020 was
run on the corrected inputs. At WE:
- the 4S15P lid carries 22.0 percent of them (TYP) and 17.5 percent (WAB);
- the 4S14P lid carries 19.2 and 14.0 percent;
- the 4S9P lid carries none.

That is the MODELLED HISTORICAL COVERAGE, not a probability of success, with the kit counted as failing when it stops. On
the stricter lines the figures fall (section 8). Covering 50, 80 or 95 percent of those windows with today's array, loads
and inputs would need 1.4 to 2.5 times the 4S21P kit's usable store, and 1.5 to 2.7 times its cells: 128 to 228 cells
against at most 84 in any established arrangement. **So none of those targets fits the Peli 1450 as the mechanical records establish it** (section 8a).
**"Several times more energy" is withdrawn and replaced by these figures.** The one credible input that moves coverage most
is the load: the link-off variant of PS-IDLE-SPEC more than doubles it, but it reduces the approved service (section 8b).

**The table.** Every row is case (iii), the CORRECTED PATH, HYPOTHETICAL, except GEN, which is case (i), AS DRAWN. All energy
figures are MODELED on SC-37's reference day (section 6a), on the 40 degree south plane unless a band is named.
- Each cell gives the lowest store of both packs in Wh, with the base's and the lid's own lowest in brackets; "NOT MET"
  gives the energy left unserved.
- TYP and WAB are the two array builds on the same mean day (section 6b).
- The cases are defined exactly in section 6c. **WE is CONDITIONAL** on the three undocumented efficiencies (section 3).
- The pass lines are COMB (both packs together above 4.2 Wh) and EACH (each pack above 4.2 Wh) (section 6d).

| | 4S9P lid: both lid functions kept (4S15P in all) | 4S14P lid: the tablet bracket out (4S20P in all) | 4S15P lid: the QMX HF set out (4S21P in all) |
|---|---|---|---|
| **Displaced lid function** (section 9) | none displaced | **leaves the kit unless a location is found**; the tablet itself can be used outside the case over WiFi and USB-C | **leaves the kit unless a location is found**; the base has no volume for it and the connector plate carries no lead for it outside |
| **NOM**, nominal inputs: TYP / WAB | NOT MET, 165.7 / 172.6 Wh unserved | 93.7 (49.0, 44.6) / 75.7 (48.2, 27.5) | 125.2 (57.1, 68.1) / 106.8 (56.3, 50.5) |
| **WE**, the established worst, CONDITIONAL: TYP / WAB | NOT MET, 169.2 / 176.1 Wh unserved | 44.0 (44.0, **0.0**) / **NOT MET, 10.8 Wh unserved** | 74.3 (52.4, 19.4) / 19.5 (19.5, **0.0**) |
| WE at 40/0, pass lines COMB / EACH: TYP; WAB | N / N; N / N | Y / N; N / N | Y / Y; Y / N |
| WE60, U3's limit at the 6.0 A bracket: TYP / WAB | NOT MET | 23.9 (23.9, 0.0) / NOT MET, 30.9 | 54.1 (48.9, 5.2) / NOT MET, 0.6 |
| WEL, the bus at its endurance bracket 18.782 V: TYP / WAB | NOT MET | 20.8 (20.8, 0.0) / NOT MET, 34.0 | 51.0 (48.0, 3.1) / NOT MET, 3.7 |
| WA, the three undocumented efficiencies at 0.90 as well | NOT MET | NOT MET, 71.8 / 122.0 | NOT MET, 41.5 / 93.2 |
| GEN, board A **as generated** (R11 10 mOhm): **case (i), AS DRAWN** | NOT MET, 494.7 / 522.4 | NOT MET, 357.5 / 383.8 | NOT MET, 326.6 / 352.8 |
| **Case (i'), the DERATED VARIANT** (U3 at 4.05 A; `three_cases.out`) | NOT MET, 523.7 / 551.5 | NOT MET, 386.5 / 412.7 | NOT MET, 355.5 / 381.7 |
| **Case (ii), RESISTOR-ONLY: INCONCLUSIVE**, its lower bound under the inferred collapse, NOM (`three_cases.out`) | NOT MET, 805.5 / 1079.9 | NOT MET, 652.9 / 926.5 | NOT MET, 622.1 / 895.7 |
| **Band at WE, pass line COMB** (both builds pass; `energy_basis.out` 6) | none | **none** | **slope 30 to 50, south to 15 W, CONDITIONAL**; least combined 5.3 Wh at 50/+15 WAB; the lid empties at 30/0 WAB |
| Band at WE, pass line EACH | none | none | **none** |
| Band at WE60 (either line) | none | none | none |
| **Thresholds at WE, pass line COMB** (section 7; each input alone): charge; stage or front end; bus; U3's limit | not applicable | at 30/0, 40/0, 40/+15, 50/0: **0.964 to 0.971**; **0.952 to 0.963**; 19.377 to 19.488 V; 6.174 to 6.209 A | at the band's six points: **0.936 to 0.949**; **0.907 to 0.929**; 18.910 to 19.125 V; 6.025 to 6.093 A |
| Thresholds at WE, pass line EACH | not applicable | none reach it at 1.00 (the bus 20.220 to 20.417 V) | 0.981 to 0.995; 0.980 to 0.995, or none; 19.663 to 20.034 V; 6.265 to 6.344 A, or none |
| WE's own values of those inputs | | 0.95; 0.93; 19.146 V; 6.1 A | 0.95; 0.93; 19.146 V; 6.1 A |
| Band at NOM, for reference: COMB; EACH | none | 20 to 50, 15 E to 30 W (least combined 18.3 Wh); 30 to 50, S to 15 W (least lid 17.1 Wh) | 20 to 60, 15 E to 30 W (least combined 6.6 Wh); 20 to 50, 15 E to 30 W (least lid 4.8 Wh) |
| MODELLED HISTORICAL COVERAGE, case (iii), 864 September 72 h windows at 40/0 (section 8): WE TYP / WE WAB, the kit never stops; the same on COMB; on EACH | 0 in every case | 19.2 / 14.0 %; 19.0 / 13.2 %; 13.3 / 9.8 % | 22.0 / 17.5 %; 21.5 / 16.9 %; 16.3 / 12.5 % |

### 1a. PROPOSED for the owner's approval (nothing accepted, nothing applied)

1. **The case M1's energy claim is judged on.** WE as restated: every term with a maker's document at its worst. This is a
   case DEFINITION, not an established basis: every result on it is conditional (items 3 and 5, section 7).
   - WE holds the three undocumented efficiencies at their declared values and names them as conditions.
   - It replaces SC-76's 19.08 V session choice with the established steady-state minimum, 19.146 V.
   - The endurance bracket, 18.782 V, is a bound at test stress. It is shown (WEL) and not taken.
2. **Whether REQ-072's pass line is the two packs together or each pack.**
   - Under EACH, neither lid has a band at WE.
   - L3-OD1's drafted ruling on `fnd/l3r2` would read "the pack" in a requirement as each pack.
   - This is the owner's reading, and it decides whether any band survives.
3. **No deployment condition is proposed as established.**
   - For the QMX-out lid, "slope 30 to 50 degrees, facing south to 15 degrees west" is CONDITIONAL. It holds on the model
     only with the charge efficiency at 0.949 or better and the stage and the front end at 0.929 or better. It holds only
     on the COMB line and only at U3's 6.1 A: at 6.0 A it vanishes.
   - For the tablet-out lid there is no band unless those efficiencies are better than declared.
   - A condition can be written as a requirement only once the three efficiencies are established, on the prototype or by
     the makers' figures for these circuits, with margin over the thresholds of section 7.
4. **The displaced function.** Either Option A(i) lid removes an approved function from the kit unless a location is
   found (section 9). Keeping both does not carry M1. The owner's authorisation is needed for whichever function leaves.
5. **The weather basis (L3-OD6).** Section 8a sets out the options: SC-37's mean day against illustrative coverage
   targets, with the store each would need. **Every store size there rests on case (iii), the CORRECTED PATH,
   HYPOTHETICAL**; the sizing is not run on case (i). Only the mean day fits an established arrangement with today's array, loads
   and inputs. Section 8b lists the inputs that would move coverage, and marks which reduce the approved service. The
   choice is the owner's, and nothing here adopts a target.

## 2. VBUS20 at U3's input: the steady-state range and its brackets (`vbus20_range.out`)

**The circuit (NETLIST, board A, sha256/16 `6c40250c47195ebb`).**
- U2 regulates VBUS20 itself: R6 240k 1 % runs from VBUS20 to FE_FB, and R7 10k 1 % runs to GND.
- R11 (FE_OUT to VBUS20) is inside the loop.
- R16 runs from VBUS20 to CH_ACN, and U3's pin 1 is on VBUS20.

**The parts (MAKER):**
- R6 is YAGEO RC0603FR-07240KL: 100 ppm/K from +25 C (RC_L V.12 p.5 Table 2 and p.8). The sheet is filed.
- R7 is UNI-ROYAL 0603WAF1002T5E: 100 ppm/K from +25 C (V.3 p.6). The sheet is held back and read, not committed.

| Term, at the regulation point | Low / high, V | Basis | Kind |
|---|---|---|---|
| VREF 0.788 / 0.800 / 0.812 V, TJ -40 to 125 C | -0.300 / +0.300 | MAKER SNVSAI1D p.6; no reference curve on pp.9 to 12 | part to part and temperature, not separated by TI |
| R6, R7 at 1 %, opposite directions | -0.380 / +0.388 | MAKER; NETLIST values | part to part |
| R6, R7 at 100 ppm/K over 45.0 K, opposite directions | -0.172 / +0.174 | MAKER; the directions INFERRED | temperature |
| IBIAS(FB) at most 25 nA through R6 | -0.006 / +0.006 | MAKER p.6 | part to part and temperature |
| the amplifier's finite gain, COMP up to VCC's 7.88 V | -0.008 / +0.008 | INFERRED from TYPICAL gm 1.31 mS and ROUT 20 MOhm | load and line |

**The steady-state range:**
- The envelope (-20.0 to +62.1 C at the divider): **min 19.146 V, nominal 20.000 V, max 20.887 V**.
- M1's reference day: 19.205 / 20.000 / 20.823 V.

**Brackets beside it** (not in it):

| Bracket | Min | Max | Basis |
|---|---|---|---|
| The divider 20 K above the inside air | 19.101 V | 20.936 V | an ASSUMPTION: no layout. It warms the hot end only (the board starts unpowered at the cold end), so it adds 12.1 K to the envelope's 45.0 K. CHECK-1's 19.072 V added the full 20 K |
| Both resistors at their endurance limits | **18.782 V** | 21.293 V | MAKER: YAGEO p.8 and UNI-ROYAL p.7, +-(1 % + 0.05 Ohm) after 1000 h at 70 C at rated voltage. A test limit at far more stress than the divider's 80 uA: a bound, not an expectation |
| Both brackets together | 18.738 V | 21.342 V | as above |

**Outside the steady state, named:**
- The soft start: C7 4.7 uF on FE_SS (NETLIST), charged at ISS 3.75 / 5 / 6.35 uA (p.6): 0.59 to 1.00 s after each enable.
- Load steps and a line transient: TI Figures 6-15 to 6-18, p.11, plotted at 500 us and 1 ms per division.
- Neither moves an hourly energy balance.
- Not established: the ground offset between R7's return and U2's AGND, and the copper from R6's tap to R16 (6.3 mV per
  mOhm at 6.3 A). Both are layout terms; board A has no layout of this netlist.

**U3's limit.** SLUSE66A prints only the maximum for the 10 mOhm sense: 100 mA above the setting (9.6.22 p.80). The records'
6.1 A minimum is INFERRED (the maximum mirrored), with 6.0 A as a bracket. The front page's +-2.5 % input current regulation
(p.1) gives 6.045 A at 6.2 A, inside that bracket.

**As generated (GEN).** R11 is 10 mOhm, so the front end's constant-current loop holds 4.30 / 5.00 / 5.70 A (VSNS
43 / 50 / 57 mV, p.7). That is below U3's 6.1 A, and the bus leaves regulation. Entry E1 sets U3 at 4.15 A. Its 4.25 A
maximum is only 50 mA under the front end's 4.30 A minimum, and R11 also carries VBUS20 currents that do not pass R16
(U2's BIAS, R197, the divider). r11dep (fourth issue) quantifies them at 0.060 A, and stacks R11's tolerance, TCR and the
ISNS bias: the front end then limits at 4.212 A, and GEN's U3 exceeds that by 0.098 A (r11dep A-1). Every Option A(i)
figure uses the drafted R11 6.2 mOhm (6.94 / 8.06 / 9.19 A printed, 6.793 A stacked minimum), **with Kelvin taps on R11
(r11dep)**. Without them the stacked margin of 0.378 A over U3 does not hold: the copper shared with the taps may be at most
0.29 mOhm at 25 C. That figure, and every other correction of section 0, make these results case (iii), HYPOTHETICAL.

## 3. The three undocumented efficiencies: what the makers' documents give (`energy_basis.out` 2; `curve_readings.out`)

| Efficiency | Carried | The maker's document | Reading | Established? |
|---|---|---|---|---|
| board E's stage (LT8705A) | 0.93 DECLARED, bracket 0.90 to 0.97, "NOT PLOTTED at this ratio" | 8705af p.41: the "12V, 15A Output Converter", whose M1 BSC028N06NS and M2 BSC039N06NS **are board E's Q3 and Q4 as generated** (NETLIST); the 35 V curve | 96.5 to 96.8 % at 6 to 12 A; 92.0 % at 1 A, 96.0 % at 3 A (TYPICAL, 25 C, a pixel reading: INFERRED) | **No**: another circuit (35 to 12 V, not 34.3 to 15.1 V), typical, not weighted over the day. ARRAY.md's draft also moves Q3 and Q4 to 80 or 100 V parts for 2S2P |
| board A's front end (LM5176) | 0.93 DECLARED, bracket 0.90 to 0.97, "NOT PLOTTED at 20 V out" | SNVSAI1D p.9 Figure 6-2: the 9 V curve, a boost of ratio 1.33 (board A 1.32), VOUT 12 V, 300 kHz, 4.7 uH | 97.8 to 97.9 % at 5.5 to 6 A (TYPICAL, 25 C, INFERRED) | **No**: 12 V out, not 20 V; other frequency, inductor and FETs. The plot's load current is its output current: at 6 A out its 9 V curve draws about 8.2 A in, close to board A's 8.7 A in at 6.1 A out, so the currents are alike and the voltages and circuit are not |
| the pack's charge efficiency | 0.95 INFERRED, bracket 0.90 to 0.98, "no held document gives it" | Samsung SDI INR18650-35E (`v2/vendor/battery/samsung-35e-conrad.pdf`, pinned by `energy_inputs.yaml`): p.3 0.2C discharge 3.482 Ah, 12.62 Wh (mean 3.624 V); p.7 one storage sample's initial DC-IR 34.5 mOhm (AC-IR 19.8) | the resistive part alone, (OCV - I_dis R) / (OCV + I_chg R): 0.9924 and 0.9925 (base, 0.661 A a cell, discharging at the 4S20P and 4S21P kits' 0.148 and 0.141 A a cell), 0.9933 (4S14P lid), 0.9937 (4S15P lid); INFERRED | **No**: the sheet gives no charged energy, charge curve, coulombic efficiency or hysteresis; the resistive part is an UPPER bound |

## 4. Sensitivity, corrected: one input at a time from WE and from NOM WAB (`energy_basis.out` 4; case (iii), HYPOTHETICAL)

The first issue moved each input from NOM with the TYP build. There both packs fill before dusk, so every charge-side loss
was hidden (CHECK-1 B1). That table is withdrawn.

From WE on 40/0, the change in the lowest combined store (a NOT MET row counts minus its unserved energy, so a change across
the verdict still reads). The unfavourable ends:

| Input, unfavourable end (from WE) | 4S14P TYP | 4S14P WAB | 4S15P TYP | 4S15P WAB | Basis |
|---|---|---|---|---|---|
| the pack's charge efficiency 0.90 (0.95) | -55.7 Wh | -53.1 | -55.7 | -53.1 (NOT MET, 33.6 unserved) | INFERRED, no document |
| the array build, the other one | -54.8 | (WAB is the worse) | -54.8 | | a1solar |
| the bus at the endurance bracket 18.782 V | -23.2 | -23.2 | -23.3 | -23.2 (NOT MET) | MAKER bound |
| the stage 0.90 (0.93) | -21.8 | -20.1 | -22.0 | -20.1 (NOT MET, 0.6 unserved) | DECLARED |
| the front end 0.90 (0.93) | -21.8 | -20.1 | -22.0 | -20.1 (NOT MET, 0.6 unserved) | DECLARED |
| U3's limit 6.0 A (6.1) | -20.1 | -20.1 | -20.2 | -20.1 (NOT MET, 0.6 unserved) | INFERRED bracket |
| the bus at the divider-rise bracket 19.101 V | -2.8 | -2.8 | -2.8 | -2.8 | ASSUMPTION |

The favourable ends, which show what WE's worst-case terms cost:
- U3B carried 0.972 against 0.963: +6.5 to +6.9 Wh;
- U3 at TI's reading: +12.2 to +12.6;
- the lid loops nominal: +4.7 to +5.2;
- no standby drain: +1.5;
- V(AK) typical: +0.7;
- the bus at nominal 20.000 V: +38.1 to +52.3;
- U3's limit at 6.2 A: +20.0 to +20.2.

From NOM with the WAB build, the unfavourable ends:
- the charge efficiency 0.90: -47.2 (4S14P) and -47.6 Wh (4S15P);
- the bus at 19.146 V: -40.1 and -40.5;
- U3's limit at 6.0 A: -26.3 and -26.6;
- the stage or the front end at 0.90: -16.5 and -16.8 each;
- U3's limit at 6.1 A: -8.9;
- U3 at the makers' maxima: -6.8;
- U3B at 0.963: -3.5 and -3.6;
- the lid loops at their worse end: -3.1 and -3.2;
- the standby drain: -0.9;
- V(AK) at 29 mV: -0.5.

**Which input dominates, restated.** At the proposed basis, in order:
1. The pack's charge efficiency: about 55 Wh for five points, the largest single input, with no document behind it.
2. The array build: about 55 Wh.
3. The power into U3, through the bus and U3's limit together: about 20 Wh for 0.1 A, and about 23 Wh from the endurance
   bracket.
4. The stage's and the front end's efficiencies: about 20 to 22 Wh each for three points, both undocumented.
5. U3's own efficiency bracket: 12.2 to 12.6 Wh between the makers' maxima (in WE) and TI's reading.
6. U3B, the lid loops, the drain and V(AK): each 7 Wh or less, together about 14 Wh.

Two of the three largest inputs are the undocumented efficiencies. Beyond the mean day, the weather dominates every one of
them (section 8).

**The knee** (`energy_basis.out` 4b, every other input at NOM, 40/0):
- With the TYP build, the store rises steeply from 110 to 122 W into U3 and is flat above: the packs fill before dusk.
- With the WAB build it keeps rising to 128 W (4S15P: 106.8, 115.4, 122.4 Wh at 124, 126, 128 W).
- The bus's steady-state range is 116.8 to 127.4 W at 6.1 A, and 114.9 to 125.3 W at 6.0 A.

## 5. U3's efficiency against the bus (`energy_basis.out` 3)

Recomputed by stream s117's method at each bus and limit (INFERRED). The method reproduces the carried 0.972 / 0.979 / 0.983
at 20.7 V and 6.2 A exactly (check 0b). TI's reading is 0.9796 at 19.146 V and 0.9790 at 20.887 V (6.1 A), and the makers'
maxima 0.9733 and 0.9722. The bus acts almost wholly through the power U3 may take, not through U3's efficiency.

## 6. The cases, exactly

### 6a. The weather: SC-37's reference day, and nothing worse

- PVGIS 5.2, PVGIS-SARAH2 monthly means 2015 to 2020 at Leiden (52.160, 4.497) on the 40 degree, azimuth 0 plane
  (PVGIS's optimum): **4.014 kWh/m2 a day** in September.
- The shape is PVGIS DRcalc's September mean-day profile, SARAH2 2005 to 2020, hourly, UTC, on that plane (3.983 kWh/m2),
  **scaled by 1.007820**.
- The same 24 hours are repeated for 72 hours, run from 06 and 18 UTC from a full pack.
- The air is 13.23 to 18.33 C. The lid pack is held at 13.23 C and the base pack at +20 C.
- Other planes: each plane's own DRcalc September mean day, scaled by the same factor.
- **No worse-weather case is established by these runs.** Section 8's historical coverage is informative.

### 6b. The array build (both on the same mean day)

400 Wp in 2S2P. The ratio multiplies PVGIS's 0.9417, the 40/0 plane's losses, for every plane.

- **TYP:** fit "Rs 0", the FBIN point at 34.29 V, NOCT 45 C, a 5 m lead (0.0465 Ohm loop). At 40/0, 0.9903.
- **WAB, the worst array build:** the earlier records' case C, called "adverse" there. It is **not a weather case**. It
  takes the worst of the three fits (Rs 0, 0.1 and 0.2 Ohm), the FBIN point at 33.05 or 35.57 V, cells 10 K above the NOCT
  model, a 10 m lead, and the hotter cells' own maximum-power loss. At 40/0, 0.9103.

### 6c. The electrical and loss inputs

| Case | Bus | U3's limit | U3 | U3B | Stage, front end, charge | Lid loops | V(AK) | Standby drain |
|---|---|---|---|---|---|---|---|---|
| NOM | 20.000 V | 6.2 A | 0.9793 (TI, INFERRED) | 0.972 (INFERRED) | 0.93, 0.93 (DECLARED), 0.95 (INFERRED) | 0.030 / 0.023 Ohm (ESTIMATE) | 20 mV (MAKER typical) | none |
| **WE (restated)** | **19.146 V** (steady-state minimum) | **6.1 A** (INFERRED minimum) | **0.9733** (makers' maxima, INFERRED) | **0.963** (lower bracket, INFERRED) | **0.93, 0.93, 0.95: CONDITIONAL** | **0.045 / 0.040 Ohm** (ESTIMATE's worse end) | **29 mV** (MAKER maximum) | **1.8 Wh over 72 h** as load |
| WE60 | 19.146 V | 6.0 A | 0.9734 | 0.963 | as WE | as WE | as WE | as WE |
| WEL | **18.782 V** (endurance bracket) | 6.1 A | makers' maxima there | 0.963 | as WE | as WE | as WE | as WE |
| WA | 19.146 V | 6.0 A | 0.9734 | 0.963 | **0.90, 0.90, 0.90** | as WE | as WE | as WE |
| WE1 (the first issue's WE) | 19.146 V | 6.1 A | 0.9733 | 0.963 | 0.93, 0.93, 0.95 | nominal | 20 mV | none |
| GEN | 20.000 V | 4.15 A, the front end at 4.30 A | 0.9810 | 0.972 | nominal | nominal | nominal | none |
| M207, SC76 (for comparison) | 20.7 V; 19.08 V | 6.1 A | 0.979 carried | 0.972 | nominal | nominal | nominal | none |

**Common to every case:**
- a 200 W stage window;
- the drafted entry R11 6.2 mOhm, as case (iii) with its corrections (GEN, case (i), excepted);
- U3B at code 62 (7.936 A);
- PS-IDLE-SPEC 42.8 W at the pack terminals;
- cells aged to 80 percent, with the 3.00 V line and the 5 percent reserve;
- charge, discharge and the drain split between the packs by capacity.

Check 0e reproduces the first issue's WE rows from WE1.

### 6d. The pass lines, and each pack's own store

M1 is MET when neither start stops the kit. Beside it, against the floor of 4.2 Wh: the model's hourly-step sensitivity as
`reconcile_lid_panel.out` prints it, measured at 40/0 at an earlier issue's settings. CHECK-1 measured at most 0.1 Wh at WE.

- **COMB:** the lowest store of both packs together is above the floor.
- **EACH:** the base's and the lid's own lowest stores are each above the floor.

A pack at 0.0 Wh has reached its own 3.00 V line with the reserve, and the kit runs on the other pack. On the reference
plane at WE, the lid pack empties with the WAB build for the 4S15P lid and with the TYP build for the 4S14P lid (the table's
bold zeros); the 4S14P lid with the WAB build does not meet at all. **Which line REQ-072 needs is the owner's reading** (section 1a item 2). Every table on this page gives both.

## 7. What each undocumented figure must reach (`energy_basis.out` 7; case (iii), HYPOTHETICAL)

Each input is moved alone from WE, the rest held as WE. The table gives the least value at which both builds still pass the
line. "none" means the input fails even at the search's best end (1.00, 22 V, 6.35 A).

| Lid, point | Line | Charge efficiency | Stage | Front end | VBUS20 | U3's limit |
|---|---|---|---|---|---|---|
| (WE's values) | | 0.95 | 0.93 | 0.93 | 19.146 V | 6.1 A |
| 4S15P 30/0 | COMB / EACH | 0.941 / 0.987 | 0.917 / 0.989 | 0.917 / 0.989 | 19.002 / 19.830 V | 6.054 / 6.318 A |
| 4S15P 30/+15 | COMB / EACH | 0.945 / 0.991 | 0.922 / 0.995 | 0.922 / 0.995 | 19.061 / 19.911 V | 6.073 / 6.344 A |
| 4S15P 40/0 | COMB / EACH | 0.936 / 0.981 | 0.907 / 0.980 | 0.907 / 0.980 | 18.910 / 19.663 V | 6.025 / 6.265 A |
| 4S15P 40/+15 | COMB / EACH | 0.940 / 0.986 | 0.916 / 0.986 | 0.916 / 0.986 | 18.981 / 19.808 V | 6.047 / 6.311 A |
| 4S15P 50/0 | COMB / EACH | 0.942 / 0.988 | 0.917 / 0.991 | 0.917 / 0.991 | 19.016 / 19.770 V | 6.059 / 6.299 A |
| **4S15P 50/+15** | COMB / EACH | **0.949** / 0.995 | **0.929** / none | **0.929** / none | 19.125 / 20.034 V | 6.093 / none |
| 4S14P 30/0 | COMB / EACH | 0.970 / none | 0.962 / none | 0.962 / none | 19.488 / 20.417 V | 6.209 / none |
| 4S14P 40/0 | COMB / EACH | 0.964 / none | 0.952 / none | 0.952 / none | 19.377 / 20.220 V | 6.174 / none |
| 4S14P 40/+15 | COMB / EACH | 0.968 / none | 0.958 / none | 0.958 / none | 19.464 / 20.361 V | 6.201 / none |
| 4S14P 50/0 | COMB / EACH | 0.971 / none | 0.963 / none | 0.963 / none | 19.484 / 20.349 V | 6.208 / none |

**Reading it.**
- On the COMB line the 4S15P band's least point, 50/+15, needs a charge efficiency of 0.949 against WE's 0.95, and a stage
  or front end efficiency of 0.929 against 0.93. The margins are 0.001 each, and 0.021 V on the bus and 0.007 A on U3's
  limit. The reference plane itself needs 0.936 and 0.907.
- Every band point holds within 0.1 to 2.3 percentage points of an undocumented figure, and the edge within 0.1. By
  the rule of this round, **the band is conditional on those figures and is not a basis for a requirement.**
- The 4S14P lid needs each of them above its declared value.
- The makers' readings (section 3) lie above every COMB threshold for the stage (0.965) and the front end (0.978), and the
  cell's resistive bound (0.99) above the charge thresholds. That makes the conditions plausible; it does not establish
  them.

## 8. The modelled historical coverage of the three lids (`weather_basis.out` A; case (iii), HYPOTHETICAL)

**Not a success probability, and not a requirement proposal.** It is the share of past September windows the model
carries. Whether M1 must hold in worse weather than SC-37's mean day is the owner's call (L3-OD6, section 8a).
`weather_basis.py` reproduces `energy_basis.out` sections 5 and 8 before it prints anything.

**Exactly what is run:**

| Item | Value |
|---|---|
| Dataset | PVGIS 5.2, the seriescalc API (`https://re.jrc.ec.europa.eu/api/v5_2/seriescalc`); radiation PVGIS-SARAH2, meteorology ERA5, horizon DEM-calculated; hourly averages, UTC, stamped at HH:11. Filed as `v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json` by `fetch_pvgis_series.py`, whose `--check` re-fetches and compares. Its mean September day equals the DRcalc profile the reference day is built from, hour by hour |
| Years | 2005 to 2020, 16 Septembers |
| Windows | 864 windows of 72 hours: one starting at 06:00 and one at 18:00 UTC on each of 1 to 27 September of each year. They OVERLAP (starts 12 h apart). None crosses the month's end (the last window's last hour is 30 September 17:11 UTC). The series is used unscaled |
| Initial charge | both packs full (their aged usable energy) at each window's start; no carry-over between windows |
| Ageing and temperature | REQ-014's 80 percent of the cells' specification minimum; the 3.00 V line with the 5 percent reserve; the base pack at +20 C; the lid pack at the window's own minimum air |
| Load | PS-IDLE-SPEC 42.8 W at the pack terminals (POWER-THERMAL.md section 4). In every WE case the lid path's standby drain, 1.8 Wh over 72 h, is added. Both are split between the packs by capacity |
| Array and orientation | 400 Wp, four Renogy RNG-100DB-H in 2S2P, into a 200 W stage window; slope 40 degrees, facing south, at Leiden (52.160, 4.497); each calendar day's own TYP or WAB ratio |
| Failure criteria (all reported) | **STOP**: the kit stops, both packs at their 3.00 V line (the model's M1 verdict). **COMB**: the combined lowest store at or under 4.2 Wh. **EACH**: either pack's own lowest store at or under 4.2 Wh |
| Cases | **WE** as restated, conditional on the stage 0.93, the front end 0.93 and the charge efficiency 0.95. **WE-LO**: those three at their brackets' lower ends, 0.90 each. **WE-MKR**: those three at the makers' readings, stage 0.965, front end 0.978 and charge 0.9924 (INFERRED readings of other circuits and an upper bound, not established). **NOM**: nominal inputs |

| Lid | Case | Kept, no STOP | COMB | EACH |
|---|---|---|---|---|
| 4S9P both kept | WE TYP, WE WAB, WE-LO, WE-MKR, NOM | 0 of 864 in every case | 0 | 0 |
| 4S14P tablet out | WE TYP | 166 (19.2 %) | 164 (19.0 %) | 115 (13.3 %) |
| | WE WAB | 121 (14.0 %) | 114 (13.2 %) | 85 (9.8 %) |
| | WE-LO TYP | 118 (13.7 %) | 114 (13.2 %) | 79 (9.1 %) |
| | WE-MKR TYP | 216 (25.0 %) | 213 (24.7 %) | 147 (17.0 %) |
| | NOM TYP | 207 (24.0 %) | 200 (23.1 %) | 145 (16.8 %) |
| 4S15P QMX out | WE TYP | 190 (22.0 %) | 186 (21.5 %) | 141 (16.3 %) |
| | WE WAB | 151 (17.5 %) | 146 (16.9 %) | 108 (12.5 %) |
| | WE-LO TYP | 139 (16.1 %) | 136 (15.7 %) | 104 (12.0 %) |
| | WE-MKR TYP | 255 (29.5 %) | 252 (29.2 %) | 188 (21.8 %) |
| | NOM TYP | 235 (27.2 %) | 232 (26.9 %) | 177 (20.5 %) |

**The other cases** (`three_cases.out` 3, TYP, the same windows):
- case (i) AS DRAWN and case (i') the DERATED VARIANT carry 0 of 864 windows for every lid, on every line;
- case (ii) RESISTOR-ONLY's lower bound carries 2 windows (0.2 %) for the 4S14P and 4S15P lids at NOM, and 0 at WE. Its
  upper bound is the table above.

**What the coverage shows:**
- The corrected inputs move the first round's figures only a little: 4S15P WE WAB went from 18.2 to 17.5 percent. CHECK-2
  counts 152 windows there against 151, one window at the margin.
- The three undocumented efficiencies alone span 16.1 to 29.5 percent for the 4S15P lid.
- The per-pack line takes off a quarter to a third of the windows the kit carries.
- The 72 hour irradiation over the windows is 3.17 kWh/m2 at the lowest, 7.36 at the 10th percentile and 11.45 at the
  median, against the reference day's 12.04 (`energy_basis.out` 8).
- One dark day in a window leaves a night the packs cannot bridge. That is INFERRED from the model's structure, not traced
  window by window.

**Limits of the coverage:**
- PVGIS's 0.9417 is an average loss, applied to single days;
- one plane only;
- the base pack at +20 C;
- a full pack at each window's start;
- overlapping windows, which are not independent trials.

## 8a. L3-OD6, the weather basis, as a quantified choice (`weather_basis.out` B; case (iii), HYPOTHETICAL)

**Every store size in this section rests on case (iii), the CORRECTED PATH, HYPOTHETICAL.** It needs every correction of
section 0. The sizing is not run on case (i), the circuit as drawn.

The targets below are ILLUSTRATIVE, not proposals. For each window, `weather_basis.py` finds by bisection the least lid pack
that carries the window on the COMB line at WE, with the base held at 4S6P and U3B's charge current unchanged. The lid's
parallel count is treated as a real number, so the store is continuous. The store is the two packs' usable energy at the
window's own lid temperature. A target of X percent takes the X-th percentile of those stores over the 864 windows. The
mean-day basis (SC-37) uses the same bisection on the reference day. Cells, mass and volume are the cells' own, from Samsung
SDI's sheet (Ver. 1.1, `samsung-35e-orbtronic.pdf`, MAKER):
- 3.35 Ah minimum at 3.60 V, 12.06 Wh a cell;
- 50 g maximum;
- 65.25 mm by 18.55 mm: 17.63 cm3 as a cylinder, 22.45 cm3 as its square footprint.

Holders, protection boards, wiring and enclosures are not counted. The established places come from a1mech README section 2's
table: base 4S6P (24 cells), plus a lid of 39, 56 or 61 places. That is at most 60, 80 or 84 cells in 4S groups.

**The allowances from nominal to usable**, taken from the 4S21P kit at WE on the mean day (the model's own factors):
- **Base 4S6P at +20 C:** at 0.141 A a cell, rate 1.000, temperature 1.000, mean voltage 3.624 V (1.007 of 3.60 V), the
  3.00 V line or the 5 % reserve 0.937, ageing 0.80. That is 0.755 of nominal.
- **Lid 4S15P at 13.23 C:** the same, with temperature 0.867 (INFERRED: a linear lower bound between -10 and 20 C). That is
  0.655 of nominal.
- **The kit:** 692.1 Wh usable of 1013.0 Wh nominal (0.683).
- **Cell limits:** the charge per cell stays under REQ-075's 1.02 A (U3 3.968 A over 6 cells; U3B 7.936 A over 15 or more
  cells). The discharge is far under the sheet's 8 A.

The cells are the percentile of each window's own cell count, the least 4S group that carries it (CHECK-2 minor 2). The
multiples are given in usable Wh, against the 4S21P kit at the reference lid temperature, and in cells, against its 84
cells, which is the physical quantity (minor 3).

| Basis | Build | Usable needed | Lid | Cells | Nominal | Cells' mass | Cells' volume (cylinders / footprint) | Times the 4S21P: Wh; cells | Fits an established arrangement? |
|---|---|---|---|---|---|---|---|---|---|
| (i) SC-37's mean day, 40/0 | TYP | 619.0 Wh | 4S13P | 76 | 916.6 Wh | 3.80 kg | 1.3 / 1.7 l | 0.89; 0.90 | yes: tablet out, QMX out |
| (ii) 50 % of the windows | TYP | 981.8 Wh | 4S26P | 128 | 1543.7 Wh | 6.40 kg | 2.3 / 2.9 l | 1.42; 1.52 | no |
| (ii) 80 % | TYP | 1331.0 Wh | 4S37P | 172 | 2074.3 Wh | 8.60 kg | 3.0 / 3.9 l | 1.92; 2.05 | no |
| (ii) 95 % | TYP | 1688.9 Wh | 4S49P | 220 | 2653.2 Wh | 11.00 kg | 3.9 / 4.9 l | 2.44; 2.62 | no |
| (i) SC-37's mean day, 40/0 | WAB | 676.2 Wh | 4S15P | 84 | 1013.0 Wh | 4.20 kg | 1.5 / 1.9 l | 0.98; 1.00 | yes: QMX out only |
| (ii) 50 % | WAB | 1055.5 Wh | 4S28P | 136 | 1640.2 Wh | 6.80 kg | 2.4 / 3.1 l | 1.53; 1.62 | no |
| (ii) 80 % | WAB | 1420.6 Wh | 4S40P | 184 | 2219.0 Wh | 9.20 kg | 3.2 / 4.1 l | 2.05; 2.19 | no |
| (ii) 95 % | WAB | 1760.5 Wh | 4S51P | 228 | 2749.7 Wh | 11.40 kg | 4.0 / 5.1 l | 2.54; 2.71 | no |

**Option (i)'s actual limitations.** It is one mean September day repeated for three days, not a weather case:
- at WE, the two Option A(i) lids carry 14.0 to 22.0 percent of the past windows on STOP, and 13.2 to 21.5 percent on COMB,
  the line the sizing uses (section 8). Option (i)'s own TYP store, 4S13P, is smaller than either lid and carries fewer still;
- its store is set by the day's night, not by dark days;
- it holds only at the reference site and plane.

The store needed per window has a median of 982.4 Wh and a largest of 2174.5 Wh (TYP), against the 4S21P kit's 692.1 Wh.

**"Several times more energy" is withdrawn.** In usable Wh the numbers give 1.4 to 1.5 times the 4S21P kit's store for 50
percent of the windows, 1.9 to 2.1 times for 80 percent and 2.4 to 2.5 times for 95 percent. In cells, against its 84, they
give 1.5 to 1.6, 2.0 to 2.2 and 2.6 to 2.7 times. The cell multiple is the larger because the added cells sit in the colder
lid (0.655 of nominal against the kit's 0.683). With today's array, loads and inputs,
every coverage target above the mean day exceeds every established arrangement of the Peli 1450.

Assumptions: WE's inputs (conditional on the three undocumented efficiencies); 400 Wp; the load as in section 8; the store
grown on the lid's side; a full store at each window's start; percentiles over overlapping windows, not independent trials.

## 8b. Credible improvements, each alone from WE (`weather_basis.out` C; case (iii), HYPOTHETICAL)

Nothing here is designed or adopted: these are inputs for the owner's choice. Coverage is taken on the COMB line at WE TYP.
The mean-day margin is the lowest combined store on 40/0, TYP / WAB.

| Improvement | Basis | 4S14P coverage | 4S15P coverage | Mean-day margin, 4S14P; 4S15P | Service |
|---|---|---|---|---|---|
| WE as restated (the reference) | | 19.0 % | 21.5 % | 44.0 / NOT MET; 74.3 / 19.5 | |
| PS-IDLE-SPEC with both WiFi link cards held off: 36.9 W, 5.9 W less | record: POWER-THERMAL.md section 4 (the same model as the 42.8 W) | 45.6 % | 48.4 % | 175.4 / 172.6; 206.9 / 204.1 | **REDUCES** the approved service: the kit-to-kit link card is off (valid only while no peer kit is linked). A proposal |
| The array at 600 Wp (2S3P, six panels) | MODELED; each day's 2S2P ratio kept (INFERRED) | 41.0 % | 43.5 % | 109.3 / 105.1; 140.8 / 136.6 | **PRESERVES** the service. Outside the owner's stated "about 400 Wp into a 200 W stage": his call |
| U3's input limit set to its 6.35 A clamp (6.25 A minimum, INFERRED as for 6.1 A) | MAKER clamp (energy_two_pack.py `u3_iin_max_a`, SLUSE66A 9.3.5) | 20.1 % | 23.6 % | 70.7 / 19.4; 101.6 / 49.5 | **PRESERVES** the service. A register setting inside the drafted entry |
| Board E's stage at its maker curve's reading, 0.965 | INFERRED (curve_readings.out 2) | 19.7 % | 23.6 % | 69.3 / 12.7; 99.9 / 42.9 | **PRESERVES** the service. A figure to establish, not an improvement to apply |

Not in the table: PS-IDLE-SPEC's documented LOW, 33.1 W (POWER-THERMAL.md section 4). It is a bound from the loads' lowest
documented figures, not an established idle load, and no measured load exists.

**Reading it.**
- The load moves coverage most, because M1's nights are carried by the store. On this model the link-off variant more than
  doubles coverage, but it reduces the approved service.
- A larger array moves coverage nearly as much while keeping the service, but it is outside the owner's stated array.
- U3's limit and the stage efficiency move the mean-day margin by 23 to 30 Wh, and each makes the 4S14P lid meet with the
  WAB build. But they move coverage by only 0.7 to 2.1 points: the dark days, not the power limit, decide most windows.

## 9. The displaced lid function (the records; nothing designed here)

The source is a1mech's README section 3 and `DECISION-A1.md`, with CASE-MARGINS and appendix 32.60.

- **QMX out (4S15P):** "HF inside (16a) is lost, because the base has no volume for it (appendix 32.60: no bay on B16 cleared
  the unit ...); outside the case it would need a lead through the back wall, which the ruled connector plate does not
  carry." **No location is established: the HF function leaves the kit unless a location is found.**
- **Tablet bracket out (4S14P):** "the tablet is carried outside the case and still works on the kit's WiFi and the USB-C
  outlet; REQ-011's bracket is not met." **No location for the bracket is established: its function leaves the kit unless
  a location is found.** How the tablet travels with the kit is not established by any record read.
- **Both kept (4S9P):** nothing displaced, and M1 is NOT MET in every case.

## 10. Limits

- **The three undocumented efficiencies:** sections 3 and 7. They are the conditions of every WE result.
- **The grid:** 10 degree slope and 15 degree azimuth steps. Band edges are grid points that were run, with no angular
  tolerance beyond them, and nothing between grid points is run.
- **The floor:** the 4.2 Wh floor is the model's step sensitivity at an earlier issue's settings.
- **One site and one day:** Leiden, SC-37's mean September day. Another site needs its own grid of days, monthly mean,
  PVcalc losses and air temperature (PLANES.md section 6).
- **The model:**
  - hourly steps;
  - the base at +20 C and the lid at the day's minimum air;
  - PVGIS's 40/0 losses carried to every plane;
  - the chargers' figures exclude their inductors' core loss, so they are high by it;
  - the standby drain is carried as load split by capacity, not on the lid alone;
  - board PL's own supply is not read.
- **The bus:** the copper and the ground offset are not established. The divider's rise and the endurance drift are
  brackets. TI's amplifier gain is typical only.
- **The entry:** every Option A(i) figure is case (iii), HYPOTHETICAL. It needs R11 re-rated with Kelvin taps and every
  other correction of section 0 (r11dep R11-DEPENDENCY.md).
- **The coverage and the sizing** (sections 8 and 8a): one plane, a full store at each window's start, overlapping windows,
  PVGIS's average loss on single days, the store grown on the lid's side, and cells only in the mass and volume.

## 11. The independent check's items, and where each is answered

| CHECK-1 item | Answer |
|---|---|
| B1, sensitivity at a saturated point | section 4: from WE (TYP, WAB) and from NOM WAB; the NOM TYP table withdrawn; dominance restated |
| B2, WE's undocumented efficiencies | sections 3 (the makers' documents and readings), 6c (WE restated, named CONDITIONAL), 7 (thresholds per lid and band point), 1 and 1a (what the owner is told; the band conditional) |
| 1, endurance drift | section 2 and case WEL: 18.782 V; at WE the 4S15P WAB fails on 40/0 by 3.7 Wh |
| 2, the divider's rise | section 2: 19.101 V (the rise warms the hot end only); -2.8 Wh at WE |
| 3, a DC range | section 2: named a steady-state range; the soft start, transients and ground offset named |
| 4, per pack | sections 1, 6d, 7: each pack's lowest store in every table; the EACH pass line; the lid empties at WE WAB |
| 5, labels | section 2 (U3's 6.1 A INFERRED, the front page's 2.5 %) and 6c (U3 and U3B INFERRED) |
| 6, the knee | section 4: TYP flat above 122 W, WAB rising to 128 W |
| 7, PLANES.md | its conditions marked SUPERSEDED, proposals only, 4S14P without a band at WE (third issue) |
| 8, the standby drain | included in WE as 1.8 Wh of load (6c); its effect 0.9 to 1.5 Wh (section 4) |
| 9, self-description | the header: the stream's own analysis, not the independent check |
| 10, GEN's margin | section 2: the 50 mA margin and R11's other currents named |
| Owner's addendum A, coverage on the corrected inputs | section 8: all three lids, the dataset, windows, charge, ageing, temperatures, load, orientation and three failure criteria stated |
| Owner's addendum B, L3-OD6 | section 8a: the mean day against 50, 80 and 95 % targets, with store, cells, mass, volume and fit; "several times" withdrawn |
| Owner's addendum C, improvements | section 8b: one table, each row's service effect named |
| CHECK-2 minor 1, the base's resistive bound | section 3: 0.9924 and 0.9925 at the kit's own discharge current; WE-MKR moves by one window (section 8) |
| CHECK-2 minor 2, cells by the count's percentile | section 8a: 128 / 172 / 220 cells (TYP), 136 / 184 / 228 (WAB) |
| CHECK-2 minor 3, the multiples in cells | section 8a and section 1: 1.5 to 2.7 times the 84 cells beside 1.4 to 2.5 times the usable Wh |
| CHECK-2 minor 4, option (i) for both lids | section 8a: 14.0 to 22.0 % on STOP, 13.2 to 21.5 % on COMB |
| CHECK-2 minor 5, U3's bracket in the dominance list | section 4, item 5: 12.2 to 12.6 Wh |
| CHECK-2 minor 6, the LM5176 currents | section 3 and `curve_readings.out` 1: output against output current |
| CHECK-2 minor 7, WE as a case definition | section 1a, item 1 |
| Owner's amendments of 30 Sep 2026: three power-path cases, corrections stated prominently, inadequate-path energy not counted | section 0, and every table labelled by case |
| CHECK-3 minor 6, the Kelvin taps in the drafted-R11 sentence | section 2: "with Kelvin taps on R11 (r11dep)" |
| CHECK-3 B1, B2 and minors 1 to 5, 7 (the electrical record) | r11dep's R11-DEPENDENCY.md, second issue |

## 12. Tools, outputs and commands

**Files in this folder:**
- `vbus20_range.py` and `vbus20_range.out` (second issue): regenerated for the brackets, the names and the labels; the
  range's figures are unchanged.
- `curve_readings.py` and `curve_readings.out` (second issue): the makers' curves read by pixel; they need pdftoppm and
  Pillow. Regenerated for CHECK-2 minor 6: one sentence changed, every reading unchanged.
- `energy_basis.py` and `energy_basis.out` (third issue): regenerated in the second issue because WE is restated and the
  sensitivity, pass lines and thresholds are new, and in the third for CHECK-2 minor 1 (the base's resistive bound only). It pins its imports by sha256 and refuses (exit 4) unless checks 0a to 0e hold.
- `weather_basis.py` and `weather_basis.out` (second issue): sections 8, 8a and 8b; regenerated for CHECK-2 minors 1 to 3. It imports `energy_basis.py` (pinned) and
  refuses unless it reproduces `energy_basis.out` sections 5 and 8.
- `plane_grid.out` and PLANES.md: the figures are unchanged; PLANES.md's conditions are marked superseded.
- `three_cases.py` and `three_cases.out` (fourth issue): the cases of section 0. It imports `energy_basis.py` (pinned) and
  reads r11dep's `r11_dep.out` for the bands. It refuses unless it reproduces `energy_basis.out` section 5's NOM, WE and GEN
  rows, and `weather_basis.out`'s NOM and WE coverage of the 4S14P and 4S15P lids.

**Commands, from the repository root.** The held UNI-ROYAL and SunPower sheets must be present (ignored, never committed).

```
python3 v2/docs/records/l3plane/vbus20_range.py > v2/docs/records/l3plane/vbus20_range.out
python3 v2/docs/records/l3plane/curve_readings.py > v2/docs/records/l3plane/curve_readings.out
python3 v2/docs/records/l3plane/energy_basis.py > v2/docs/records/l3plane/energy_basis.out
python3 v2/docs/records/l3plane/weather_basis.py > v2/docs/records/l3plane/weather_basis.out
python3 v2/docs/records/l3plane/three_cases.py > v2/docs/records/l3plane/three_cases.out
python3 v2/docs/records/l3plane/plane_grid.py | cmp - v2/docs/records/l3plane/plane_grid.out
python3 v2/docs/records/a1int/reconcile_lid_panel.py | cmp - v2/docs/records/a1int/reconcile_lid_panel.out
python3 v2/docs/records/a1solar/energy_runs.py | cmp - v2/docs/records/a1solar/energy_runs.out
```

**No committed output of another stream moved.** `plane_grid.out`, `reconcile_lid_panel.out` and `energy_runs.out` rerun
byte identical. `vbus20_range.out`, `curve_readings.out`, `energy_basis.out` and `weather_basis.out` rerun byte identical
to their committed issues; the fourth issue changes none of them.
