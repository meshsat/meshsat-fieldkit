# L4-E9 round 2, part A: Q1, F1 and U17 as datasheet-backed circuit proposals (with the fix round's B1 to B3)

MESHSAT-1357, Layer 4 task L4-E9, round 2, 2 October 2026. **Prototype design, desk arithmetic: nothing has been bought,
built, powered or measured, and no kit has been field deployed.** Round 1 named three entry parts by their headline
figure (Q1's 100 V, F1's specification, U17's move). This page checks each against the conditions that apply to it:
normal operation, a reversed input, the transients of the approved test plan, the faults, and the drive, land and holder.
Every figure is printed in `l4e9_power_path.out` section 11, which `l4e9_power_path.py` reproduces byte for byte from
pinned inputs. Classes: MAKER (a maker's row, page or table named), NETLIST, INFERRED (method stated), CONDITIONAL,
ASSUMPTION, PENDING. The fix round (2 October 2026) answers the collaborator's focused check (`checks/astra-check-l4e9-1.md`,
NOT YET): B1 (Q7's power limit and the complete hot-short pulse), B2 (what F1 protects, traced without an exemption) and B3
(R227's transients), with its minors.

## The makers' documents read

| Document | Revision | Address read | sha256 | Where it is |
|---|---|---|---|---|
| TI CSD19532Q5B | SLPS414B | https://www.ti.com/lit/ds/symlink/csd19532q5b.pdf | 353ce937cff0b719e730010829720d25c2ece3637ed92fb7ad8cc370438559d1 | in the tree, `v2/vendor/power/ti-csd19532q5b-n-fet.pdf`, byte-identical to ti.com on 2 October 2026 |
| TI LM74700-Q1 | SNOSD17G | https://www.ti.com/lit/ds/symlink/lm74700-q1.pdf | e16b3a8c0023201fafa5825436f5f2dd6f885b92b84e65602b3f50d741c58b6f | in the tree, `v2/vendor/ti/ti-lm74700-q1.pdf`, byte-identical |
| TI INA226 | SBOS547C | https://www.ti.com/lit/ds/symlink/ina226.pdf | c9b67f886d4a5241a5e070723f7b61867409eeb27eed768b9cdd9cb17e03ca2d | in the tree, `v2/vendor/ti/ti-ina226.pdf`, byte-identical |
| TI LM5069 | SNVS452G | as held | d60d8106a6e8113900ff8b9576dd959942fa7169742baf0beeb30684d4d64681 | in the tree, `v2/vendor/ti/ti-lm5069.pdf` |
| TI LM5176 | SNVSAI1D | as held | 98191bec36d43771affa3e1540f6e1737347c19a1602747ffb4327509550a820 | in the tree, `v2/vendor/ti/lm5176-datasheet.pdf` |
| Littelfuse MINI Series Blade Fuses, Rated 58V (0997) | revised 11/18/2025 | the maker's address `littelfuse.com/assetdocs/littelfuse-datasheet-997-mini58v`, through the Internet Archive's snapshot 20251210045250 (the maker's site refuses this runner) | 437b1fd2c8cb3ef16107ec14d096b31ef3c3cb83893325234e880deb7540393e | **held back** (the maker's copyright and disclaimer, no grant to redistribute; the owner's rule of 27 September 2026): `fetch_held_back.py` puts it in the ignored `v2/vendor/power/held/` and checks the sha256 |
| Keystone catalogue M65, p.42 (the 3568 holder) | as held | as held | caa141ea51ac68cf80ab6e14ad2075fcfc76206451f4bfe45330005c0deaf395 | in the tree, `v2/vendor/keystone/M65p42.pdf` |
| Amphenol MIL-DTL-38999 III catalogue (the contact rating table) | as held | as held | 13a19268ba5939d9e4df5a20f9db84bb72e86525b82f0586c85696e42c126a2b | in the tree, `v2/vendor/d38999/amphenol-d38999-iii-federal.pdf` |
| Milliohm HoJLR2512 series | as L4-E4 read it | L4-E4's record (`records/l4e4/l4e4_limits.out`, pinned) | the record's pin | through L4-E4 (+-1 %, TCR +-50 ppm/K) and L4-E8 (3 W derated from 70 C to zero at 170 C) |

Provenance: `inputs/ti-sheets-2026-10-02.json`, `inputs/ia-littelfuse-997-mini58v-20251210045250.json`.

## 1. Q1, board E's vehicle-entry ideal-diode FET: TI CSD19532Q5B, LCSC C473333 (chosen)

Why it is needed (round 1, IF-04): on a reversed 36 V input DC_P is back-fed from the raised tracker ceiling (30.15 V)
through Q7's body diode, so Q1 holds 66.15 V, over the drawn BSC039N06NS's 60 V.

| Condition | Applicable value | The part's limit | Verdict | Class |
|---|---|---|---|---|
| normal: current | 6.15 A, the entry's highest limit | ID 17 A (1 in2 2 oz) | MEETS | MAKER |
| normal: dissipation and junction | 0.361 W at RDS(on) 4.9 mOhm times 1.95 (Figure 8 at 150 C); TJ at most 80.2 C in the 62.1 C inside air | 150 C | MEETS | INFERRED (RthetaJA 50 C/W on 1 in2 2 oz; board E's copper an ASSUMPTION) |
| normal: hot plug | the body diode carries the hot swap's limited current for at most 0.131 ms (ENTDLY 110 us plus Qg 62 nC at 3 mA): 0.804 mJ | no linear dwell (fully enhanced or off) | MEETS | INFERRED |
| reverse: drain to source | 66.15 V (REQ-015's -36 V plus the ceiling) | 100 V | MEETS | INFERRED |
| reverse: the controller | cathode to anode 66.15 V; ANODE -36 V | 70 V recommended, 75 V absolute; -65 V | MEETS | MAKER |
| reverse: which body diodes conduct | Q1's blocks; Q7's conducts the back-feed (DC_P's own milliamps); D10 off (36 V under 44.4 V); D1 reverse-biased; E-F1's capacitor at -36 V on 100 V | | as stated | INFERRED |
| transient: CS101 (M2), curve 2, 2 V rms | Q1 blocks at most 5.66 V; at REQ-015's top the input peaks at 38.83 V, past the OVLO's 37.78 V minimum; at curve 2's 28 V boundary 30.83 V | the OVLO window | NOT MET as drawn at a 36 V source (D-02, below); MEETS with the selected OVLO's 39.71 V minimum, and at 28 V | INFERRED |
| transient: CS114 (M3), curve 4, 141 mA rms | 3.17 V peak into E-F1's 1 uF at 10 kHz; Q1 blocks at most 6.35 V | 100 V | MEETS | INFERRED |
| transient: M7 at decision 34's level | DC_F moves 2.25 V; Q1 at most 38.25 V | 100 V | MEETS | INFERRED |
| capability scenario (D10 at its rated pulse; no surge level is ruled, D-16, CHO-003) | negative: Q1 at 100.5 V with DC_P at 36 V; avalanche energy at most 83.6 mJ | 100 V; EAS 274 mJ | NOT MET by 0.5 V, outside every requirement (DECISION-31) | INFERRED |
| fault: the power limit's sense voltage at 43.18 V (B1) | drawn R24 20k: 4.7429 mV nominal; R24 22k 1 %: 5.06 mV at its low corner (Equation 9's least RPWR there 21443 Ohm) | SNVS452G 9.2.1.2.3: under 5 mV is not recommended (the PWRLIM rows are tested at 48 V and 150 kOhm) | NOT MET as drawn; MEETS with R24 22k | MAKER |
| fault: the complete hot-short pulse (B1), by TI's procedure 9.2.1.2.5 | the breaker's event (13 A for at most 1.2 us), then the power limit at R24 +1 % and R19 -1 %, 22.412 W, times TI's 1.3: 29.14 W, 0.675 A at 43.18 V for the timer's maximum 8.16 ms; retry at 0.5 % duty | Figure 10 read from TI's vector drawing at 43.18 V: 10 ms 1.879 A, 1 ms 5.055 A, so 2.05 A at 8.16 ms (Equations 15 to 18); derated to Q7's case at most 94.3 C (Equation 19, 0.4454): 0.913 A; the 10 us line derated, 30.7 A, for the breaker's event | MEETS, CONDITIONAL on board E's copper under Q7 (RthetaJA an ASSUMPTION) | INFERRED |
| fault: a short at DC_P, ahead of the hot swap (it needs a prior short of D10, D1, E-F1's capacitor or C4) | only F1 limits: at most 569.8 A from a stiff source; 0.286 ms is an illustration from the typical melting I2t (arcing excluded), not a clearing time | IDM 400 A for 100 us | no figure shows Q1 holds it; Q1 is not a conductor or connector of REQ-045 and the entry is already failed; traced under F1 (section 2); no exemption is claimed | INFERRED |
| gate drive | VGS 10.8 to 13.9 V (the charge pump's window) | +-20 V; TI asks a 15 V rating | MEETS | MAKER |
| threshold | Vth at most 3.2 V | TI recommends 2.5 V | NOT MET as a recommendation (the drawn part's 3.3 V misses it too; effect on turn-on time and light-load regulation, bench R-112) | MAKER |
| RDS(on) window | 5.68 mOhm typical near 80 C | TI's 20 to 50 mV over H3's 4.629 A: 4.32 to 10.8 mOhm | MEETS (typical) | INFERRED |
| voltage class | 100 V | TI recommends parts to 60 V with the LM74700-Q1 | a deliberate departure (SESSION): the reason is the controller's own pins, checked above | MAKER |
| land | PowerPAK SO-8 / 5x6 SON | Q7 carries the same part on board E | MEETS | NETLIST |

**The CS101 finding on the vehicle entry (new; defect D-02, resolved in design).** TEST-PLAN M2 states no source voltage. With
a 36 V source, CS101's 2.83 V peak takes DC_P to 38.83 V, past the drawn OVLO minimum 37.78 V, so the hot swap may switch off
and the vehicle stops charging for the test, the same kind of upset as L4-E7R's backstop trip. Two resolutions on the same
topology: (i) M2 run at the source's nominal (at curve 2's 28 V boundary the peak is 30.83 V, 6.95 V under the drawn minimum);
(ii) the OVLO raised: the 1 % window for R23 is 6.346k to 6.458k with R22 100k, no E96 value inside, E192's 6.42k giving 39.04
to 43.92 V (0.21 V and 0.48 V of margin); with R22 and R23 both 0.1 % it gives 39.71 / 41.44 / 43.18 V, 0.88 V over the CS101
peak and 1.22 V under D10's 44.4 V breakdown minimum at 25 C. D10's breakdown falls 0.1 %/K (typical, the Littelfuse sheet):
42.4 V at -20 C, under the drawn OVLO maximum already, so steady inputs above it reach D10 when cold; REQ-015 admits steady
inputs to 40 V, under it; that cold figure rests on a typical coefficient, so the check is CONDITIONAL. **SESSION: (ii) at
0.1 % selected** (it removes the finding whatever M2's source voltage; register R-94, drafted with R24 in
`apply_gen_sch_e_hotswap.py`); (i) not taken, since a test condition is not changed to fit the design. The selected OVLO maximum, 43.18
V, is what F1, U2, Q2, U4, C26 and C27 and D10 are checked against in the interface rows. It does not move a block.

**Q7's power limit (B1, defect D-07, SESSION).** At the selected OVLO maximum the drawn R24 20k gives 4.7429 mV of sense
voltage, under the 5 mV TI does not recommend going below, and round 2 compared the hot-short with Figure 10 at 36 V, read by
eye (3 A; the drawing reads 2.52 A there) and with an assumed 100 C case. R24 becomes 22k 1 %: 5.06 mV at its low corner, a
limit of 22.018 W nominal and 22.412 W at the corners. The complete pulse at 43.18 V, with TI's own 1.3 margin, is 0.675 A for
8.16 ms against 0.913 A, Figure 10's line read from the sheet's vector drawing and derated by TI's Equation 19 to Q7's case at
most 94.3 C (the hottest inside air the record holds, 76.25 C, plus Q7's own 0.361 W at 6.15 A on 50 C/W). A higher limit only
shortens the start into the bus, so the timer's minimum keeps its margin. Bench R-118 measures it.

Drafts: `apply_gen_sch_e_q1.py` (round 1) and `apply_gen_sch_e_hotswap.py` (R22, R23, R24 and U6's value text); both
release-guarded and composing with d8dec31's input capacitor and L4-E7R's drafts.

## 2. F1, board E's vehicle-entry fuse: Littelfuse 0997010.WXN, MINI 58 V (chosen)

| Condition | Applicable value | The part's limit | Verdict | Class |
|---|---|---|---|---|
| DC voltage rating | 43.18 V, the selected OVLO maximum (the highest steady input the entry admits; 42.49 V as drawn) | 58 V DC | MEETS | MAKER |
| interrupting rating | 569.8 A at 43.18 V: the kit's cable and lead, copper at -20 C, the source stiff (REQ-015 states no source impedance; a vehicle battery and its wiring only lower it); by voltage 9 V 118.8 A, 12 V 158.4 A, 24 V 316.7 A, 36 V 475.1 A | 1000 A at 58 V DC | MEETS | MAKER, INFERRED |
| no nuisance opening, hottest air | 6.15 A, the entry's highest limit, in 62.1 C inside air | the derating table's next higher column, 80 C: 7.3 A (the project's rule: never interpolated) | MEETS | MAKER |
| hot-swap start-up | 6.15 A for at most 8.16 ms: 0.309 A2s | melting I2t 93 A2s (typical) | MEETS | INFERRED |
| time-current against what it protects | the lowest stiff-source fault, 9 V with the copper at 62.1 C: 85.9 A, 8.6 times the rating | the 600 % row: at most 0.1 s | MEETS | MAKER |
| a stiff source's short behind F1: the conductors' withstand (B2) | F1's let-through at 569.8 A (623.9 A with R-29's AWG 16 lead) | the conductors' short-time withstand; the sheet prints the typical melting I2t only | CONDITIONAL on Littelfuse's total clearing I2t at 43 V DC (R-115) | MAKER |
| a weak source, F1's long-time band (B2) | under 30 A available (ECSS 6.17.3c's three times the rating, the project's fuse criterion): 10 to 11 A may flow indefinitely, 13.5 A up to 600 s, 20 A up to 5 s | J_DCIN's VH 10 A (AWG 16, standard header), the D38999 size 16 contact 13 A (Amphenol's test current), board E's input bands 10 A; the kit's cable and the inside lead have no held current rating; the 0997's own test cable for 10 A is 1 mm2 | NOT ESTABLISHED: an OPEN engineering question, defect D-06 (no exemption; ASM-001 is the LoRa and cellular exception) | MAKER |
| against Q1 | the stiff-source bound above | IDM 400 A for 100 us | see Q1's DC_P short | INFERRED |
| holder | Keystone 3568: "For Littelfuse Mini 297 or 997 series"; the sheet: the same blade size and pitch | | MEETS | MAKER |
| the rejection feature | works only in a 58 V keyed holder; the 3568 also takes a 32 V MINI | | the BOM, label and ASSEMBLY.md name the 0997 (R-18) | MAKER |

Draft: `apply_gen_sch_e_f1.py` (F1's value text names the part and its ratings; release-guarded; composes with the Q1 draft,
d8dec31's input capacitor and L4-E7R's four drafts at `237cd9be`). Stale configuration found: `pcb_energy_chain.yaml`'s
SHORE_INPUT stage still names a 10 A ATOF blade on the 287 table at 56 C with a 200 A prospective current (569.8 A at the
selected OVLO maximum, 623.9 A with an AWG 16 lead), and `pcb_fuse_derating.yaml` holds no 0997 table (register R-95, R-96).

**What F1 protects, traced (B2).** REQ-045 asks that "the maximum fault current is bounded at each stage by a protective
element sized for that stage's conductors and connectors, coordinated with what it protects"; PWR-003 carries the stage
SHORE_INPUT with a 10 A conductor (board E's bands), no stage named downstream and its prospective low "not established". For
a stiff source F1 interrupts and the conductors' withstand waits on the total clearing I2t. For a weak source the elements F1
protects carry 10 to 20 A for up to 600 s, and no held sheet gives their time-current limit: defect D-06, an open engineering
question. Alternatives: an interconnect rated to the fuse's 20 A point (MIL-DTL-38999 size 12 contacts, 23 A; a 30 A board
connector such as the Amass XT60-M board E already carries; a cable whose maker rates it, with the stiff-source current
re-checked, since a heavier cable raises it toward the 1000 A interrupting rating); the source's capability stated in REQ-015
(ECSS 6.17.3c, an owner's requirement); or the makers' overload data (Lapp, JST, Amphenol), R-113. None is selected this
round: the receptacle's contacts and the external cable are the case's and the harness's (Layer 7), not board E's.

## 3. U17, board A's PoE monitor: the INA226 on R227, 5 mOhm in the PoE stage's input (chosen)

As drawn (HF-F02, S-60) U17's IN+ and IN- sit on the 54 V rail, against the INA226's 40 V absolute: NOT MET in normal
operation. The resolution moves the monitor to the stage's input: R227 (HoJLR2512-3W-5mR-1%, LCSC C2903482, the part L4-E4
chose for R138) from VBAT to a new rail POE_VIN; U16's VIN and BIAS on POE_VIN; U17 IN+ on VBAT, IN- and VBUS on POE_VIN;
R71 stays U16's own ISNS shunt, so U16's average limit does not move. 5 mOhm, not round 1's 20 mOhm: the stage's input at
its fault bound is 14.33 A, which a 20 mOhm shunt would read past full scale and dissipate 4.1 W in.

| Condition | Applicable value | The part's limit | Verdict | Class |
|---|---|---|---|---|
| common mode, regulated | VBAT at most 16.884 V | 36 V (CMRR row, bus range) | MEETS | MAKER |
| common mode, faults | 20 V at SYSOVP, 20.135 V at the pack-open bound, 29.2 V at D1's rated pulse | 36 V; 40 V absolute | MEETS | MAKER |
| differential, normal | the stage's input at 0.6 A out at a 10 V stack: 3.682 A, 18.59 mV | 81.92 mV full scale | MEETS | INFERRED |
| differential, the stage's fault bound | U16's boost peak limit (140 + 1.9) mV over R72 10 mOhm at -1 %: 14.33 A, 72.38 mV | 81.92 mV | MEETS | INFERRED |
| a PoE fault, steady buck operation (B3) | the valley at VCS(BUCK) 94 mV over R72 (9.69 A); the ripple VIN D (1 - D) T / L at most 2.02 A (D = 0.5, 16.884 V, T 5.743 us at fSW(1)'s minimum, L 12 uH at -20 %); peak 11.71 A, RMS at most 10.71 A | R227 0.58 W against 3 W; 59.12 mV against 81.92 mV; L10's Isat 15.5 A | MEETS | INFERRED |
| a PoE fault, a hard output short (B3) | one on-time can last a full period: the peak reaches 17.77 A (past L10's Isat, so a lower bound there), R227 89.7 mV, 9.15 uJ a period; then the average output loop holds 2.879 A at most (VSNS 57 mV over R71) | the ADC's full scale: a saturated sample, not damage (40 V differential absolute) | CONDITIONAL on L10's L(I) above Isat (R-65 extended) | INFERRED |
| transients behind R227 (B3) | the draft puts C81, C82 (10 uF each), U16's VIN and BIAS capacitors behind R227: 20.2 uF. A VBAT step: the differential is at most the step, POE_VIN rings to at most its start plus twice the step (undamped). A hard connect 0 to 16.884 V: 16.884 V and 33.77 V, 2.879 mJ; the pack opening: 3.251 V and 23.39 V, 0.107 mJ; D1's rated pulse (capability, D-16): 12.316 V and 41.52 V, 1.532 mJ | the INA226's +-40 V differential and -0.3 to 40 V pins (SBOS547C 6.1); R227's pulse rating (not printed) | MEETS for every required event; the capability pulse past 40 V only in the undamped ideal-step limit (its 10 us rise is slower than the loop's ringing; R-117); the pulse energy CONDITIONAL on Milliohm (R-101) | INFERRED |
| R227's dissipation | 1.037 W at 14.33 A | 3 W at 62.1 C (derated from 70 C) | MEETS | MAKER |
| U16's own input | VIN and BIAS at most 0.072 V under VBAT at the fault bound | its UVLO and BIAS window read against VBAT less that drop | MEETS | INFERRED |
| startup | "the bus voltage can be present with the supply voltage off, and reciprocally" | | MEETS | MAKER |
| a load dump | the vehicle reaches VBAT only through the front end and the charger | VBAT's bounds above | MEETS | INFERRED |
| accuracy | VOS 10 uV (2 mA); gain 0.1 % with R227's 1 % and 50 ppm/K over 75 K: 1.475 % plus 2 mA at 25 C; with SBOS547C's drift rows (50 ppm/C, 0.1 uV/C) over the IC's -20 to 76.25 C: 1.731 % plus 3.025 mA (at -20 C the drift alone is 0.225 % and 0.9 mA) | | stated | INFERRED |

What the readings mean for the firmware (FW-A09, Layer 5 handover LH-06): the PoE stage's INPUT current and POE_VIN (the
VBUS pin is on POE_VIN; VBAT is POE_VIN plus the shunt's drop), not the 54 V output; full scale 16.384 A, Current_LSB 0.5 mA,
CAL 2048; a full-scale sample is a saturated transient, not a current reading; the output power is inferred as the input
power times the stage's efficiency (0.88, the generator's figure, undocumented). Moving C81, C82 and the bypass capacitors
ahead of R227 was not taken: they close U16's input loop, and the bounds above hold with them behind it.

Draft: `apply_gen_sch_a_u17.py` (five edits on disjoint lines of `gen_sch_a.py`; release-guarded; composes with L4-E6's R12,
L4-E4's R11 and R138 and L4-E8's bank; order step 3e). Owed with it: R227's Kelvin taps (Layer 9), its line in the LCSC fill.

## 4. What this part changes in the connected record

Round 1 carried Q1 and U17 as session choices on a headline figure and F1 as a specification with no part. All three are
now datasheet-backed proposals with drafts; IF-04, IF-05 and IF-13 read them (section 4 of the output), and the register
carries their drafts, the stale configuration, the CS101 finding (D-02), the hot-swap settings (D-07), the open interconnect
question (D-06) and the transient conditions (D-08). Nothing here is applied to the tree.
