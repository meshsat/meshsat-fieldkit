# L4-E9 round 2, part A: Q1, F1 and U17 as datasheet-backed circuit proposals

MESHSAT-1357, Layer 4 task L4-E9, round 2, 2 October 2026. **Prototype design, desk arithmetic: nothing has been bought,
built, powered or measured, and no kit has been field deployed.** Round 1 named three entry parts by their headline
figure (Q1's 100 V, F1's specification, U17's move). This page checks each against the conditions that apply to it:
normal operation, a reversed input, the transients of the approved test plan, the faults, and the drive, land and holder.
Every figure is printed in `l4e9_power_path.out` section 11, which `l4e9_power_path.py` reproduces byte for byte from
pinned inputs. Classes: MAKER (a maker's row, page or table named), NETLIST, INFERRED (method stated), CONDITIONAL,
ASSUMPTION, PENDING.

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
| transient: CS101 (M2), curve 2, 2 V rms | Q1 blocks at most 5.66 V; at REQ-015's top the input peaks at 38.83 V, past the OVLO's 37.78 V minimum; at curve 2's 28 V boundary 30.83 V | the OVLO window | **OPEN finding** at a 36 V source (see below); MEETS at 28 V | INFERRED |
| transient: CS114 (M3), curve 4, 141 mA rms | 3.17 V peak into E-F1's 1 uF at 10 kHz; Q1 blocks at most 6.35 V | 100 V | MEETS | INFERRED |
| transient: M7 at decision 34's level | DC_F moves 2.25 V; Q1 at most 38.25 V | 100 V | MEETS | INFERRED |
| capability scenario (D10 at its rated pulse; no surge level is ruled, D-16, CHO-003) | negative: Q1 at 100.5 V with DC_P at 36 V; avalanche energy at most 83.6 mJ | 100 V; EAS 274 mJ | NOT MET by 0.5 V, outside every requirement (DECISION-31) | INFERRED |
| fault: an output short behind the hot swap | Q7 limits at 4.85 to 6.15 A, power limit 19.63 W at 36 V, 20.4 W at the OVLO maximum (25.29 W with PWRLIM-1's spread), at most 8.16 ms, restart at 0.5 % duty; Q1 at most 6.15 A, 13 A for at most 1.2 us at the breaker | Q7's 10 ms SOA at 36 V: 108 W at TC 25 C, 43.2 W at a 100 C case (Figure 10, read) | MEETS | INFERRED |
| fault: a short at DC_P, ahead of the hot swap (a single fault) | only F1 limits: at most 560.7 A for about 0.296 ms | IDM 400 A for 100 us | no figure shows Q1 holds it; outside every requirement (ASM-001) | INFERRED |
| gate drive | VGS 10.8 to 13.9 V (the charge pump's window) | +-20 V; TI asks a 15 V rating | MEETS | MAKER |
| threshold | Vth at most 3.2 V | TI recommends 2.5 V | NOT MET as a recommendation (the drawn part's 3.3 V misses it too; effect on turn-on time and light-load regulation, bench R-80) | MAKER |
| RDS(on) window | 5.68 mOhm typical near 80 C | TI's 20 to 50 mV over H3's 4.629 A: 4.32 to 10.8 mOhm | MEETS (typical) | INFERRED |
| voltage class | 100 V | TI recommends parts to 60 V with the LM74700-Q1 | a deliberate departure (SESSION): the reason is the controller's own pins, checked above | MAKER |
| land | PowerPAK SO-8 / 5x6 SON | Q7 carries the same part on board E | MEETS | NETLIST |

**The CS101 finding on the vehicle entry (new, OPEN).** TEST-PLAN M2 states no source voltage. If M2 is run with a 36 V
source, CS101's 2.83 V peak takes DC_P to 38.83 V, past the OVLO minimum, so the hot swap may switch off and the vehicle
stops charging for the test, the same kind of upset as L4-E7R's backstop trip. Resolutions on the same topology:
(i) M2 run at the source's nominal, stated by TEST-PLAN's owner (at curve 2's 28 V boundary the peak is 30.83 V, 6.95 V
under the OVLO minimum); (ii) R23 moved so the OVLO's minimum clears 38.83 V while its maximum stays under D10's 44.4 V
breakdown minimum: the window is R23 6.346k to 6.458k with R22 100k at 1 %, no E96 value inside, E192's 6.42k giving
39.04 to 43.92 V, 0.21 V and 0.48 V of margin at 25 C with D10's breakdown falling when cold. SESSION: (i) recommended
(register R-94), (ii) kept as the fallback. It does not move a block.

Draft: `apply_gen_sch_e_q1.py` (round 1; release-guarded; composes with d8dec31's input capacitor and L4-E7's drafts).

## 2. F1, board E's vehicle-entry fuse: Littelfuse 0997010.WXN, MINI 58 V (chosen)

| Condition | Applicable value | The part's limit | Verdict | Class |
|---|---|---|---|---|
| DC voltage rating | 42.49 V, the OVLO maximum (the highest steady input the entry admits) | 58 V DC | MEETS | MAKER |
| interrupting rating | 560.7 A: the kit's cable and lead, copper at -20 C, the source stiff (REQ-015 states no source impedance; a vehicle battery and its wiring only lower it); by voltage 9 V 118.8 A, 12 V 158.4 A, 24 V 316.7 A, 36 V 475.1 A | 1000 A at 58 V DC | MEETS | MAKER, INFERRED |
| no nuisance opening, hottest air | 6.15 A, the entry's highest limit, in 62.1 C inside air | the derating table's next higher column, 80 C: 7.3 A (the project's rule: never interpolated) | MEETS | MAKER |
| hot-swap start-up | 6.15 A for at most 8.16 ms: 0.309 A2s | melting I2t 93 A2s (typical) | MEETS | INFERRED |
| time-current against what it protects | the lowest stiff-source fault, 9 V with the copper at 62.1 C: 85.9 A, 8.6 times the rating | the 600 % row: at most 0.1 s | MEETS | MAKER |
| a weak-source fault of 13.5 to 20 A | may take up to 600 s (the 135 % and 200 % rows) | J_DCIN's stated VH rating 7 A (AWG 18, shrouded), 10 A (AWG 16) | NOT MET for the contact in that band: a residual of a single fault (ASM-001), narrowed by R-29's lead change | MAKER |
| against Q1 | the stiff-source bound above | IDM 400 A for 100 us | see Q1's DC_P short | INFERRED |
| holder | Keystone 3568: "For Littelfuse Mini 297 or 997 series"; the sheet: the same blade size and pitch | | MEETS | MAKER |
| the rejection feature | works only in a 58 V keyed holder; the 3568 also takes a 32 V MINI | | the BOM, label and ASSEMBLY.md name the 0997 (R-18) | MAKER |

Draft: `apply_gen_sch_e_f1.py` (F1's value text names the part and its ratings; release-guarded; composes with the Q1 draft,
d8dec31's input capacitor and L4-E7R's four drafts at `237cd9be`). Stale configuration found: `pcb_energy_chain.yaml`'s
SHORE_INPUT stage still names a 10 A ATOF blade on the 287 table at 56 C with a 200 A prospective current, and
`pcb_fuse_derating.yaml` holds no 0997 table (register R-95, R-96).

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
| a PoE fault (overload or short on +54V_POE) | U16 leaves boost; the buck valley is held at VCS(BUCK) 94 mV maximum over R72 (9.69 A) and the input current is that times the duty | under the boost bound | MEETS | INFERRED (SNVSAI1D 7.3.1, 7.3.5) |
| R227's dissipation | 1.037 W at 14.33 A | 3 W at 62.1 C (derated from 70 C) | MEETS | MAKER |
| U16's own input | VIN and BIAS at most 0.072 V under VBAT at the fault bound | its UVLO and BIAS window read against VBAT less that drop | MEETS | INFERRED |
| startup | "the bus voltage can be present with the supply voltage off, and reciprocally" | | MEETS | MAKER |
| a load dump | the vehicle reaches VBAT only through the front end and the charger | VBAT's bounds above | MEETS | INFERRED |
| accuracy | VOS 10 uV (2 mA); gain 0.1 % with R227's 1 % and 50 ppm/K over 75 K: 1.475 % plus 2 mA | | stated | INFERRED |

What the readings mean for the firmware (FW-A09, Layer 5 handover LH-06): the PoE stage's INPUT current and VBAT, not the
54 V output; full scale 16.384 A, Current_LSB 0.5 mA, CAL 2048; the output power is inferred as the input power times
the stage's efficiency (0.88, the generator's figure, undocumented).

Draft: `apply_gen_sch_a_u17.py` (five edits on disjoint lines of `gen_sch_a.py`; release-guarded; composes with L4-E6's R12,
L4-E4's R11 and R138 and L4-E8's bank; order step 3e). Owed with it: R227's Kelvin taps (Layer 9), its line in the LCSC fill.

## 4. What this part changes in the connected record

Round 1 carried Q1 and U17 as session choices on a headline figure and F1 as a specification with no part. All three are
now datasheet-backed proposals with drafts; IF-04 and IF-13 read them (section 4 of the output), and the register carries
their drafts, the stale configuration and the new CS101 finding. Nothing here is applied to the tree.
