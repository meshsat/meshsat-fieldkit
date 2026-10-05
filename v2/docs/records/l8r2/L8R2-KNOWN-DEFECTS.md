# L8R2-KNOWN-DEFECTS: the known engineering defects corrected at the desk on printed parts (Layer 8 round 2, MESHSAT-1357)

Record `l8r2`, branch `fnd/l8r2` from `f294dc13` (the consolidation's round 5 at `a8888abc` with record l8gnd at `226e9143`), 3
October 2026, one Claude author. The MeshSat field kit V2 is a prototype design: nothing is built, powered or measured, and **nothing
here is applied to the tree**. Every correction is a DRAFT apply script that refuses the repository's own generator until a
`RELEASE.md` beside it names an accepted check of this record. Regeneration, parity and the gates are the rented box's (section 6).

The owner's rule of 3 October 2026: "A known engineering defect: fix it, or assign a specific design-correction task to the
supplier." L4-E9 round 5 classed the open items (its section 8f) and listed the supplier's phase 1 (8g: P1-1 the solar guard and
sense, P1-2 board B's coolers' feed, P1-3 VBUS20's single faults). This record corrects P1-2, P1-3 and Layer 5's round 2 circuit
findings L5R2-F03, F04 and F05 at the desk. **P1-1 (D-10's guard-on case, D-16, R-173, R-180, R-186, R-187) is not attempted**, as
the coordinator assigned it to the supplier's phase 1.

**Round 3 (3 October 2026, branch `fnd/l8r3` from set 28's `37bc2f1d`).** Two Layer 9 records answered this one. Record l9pwr's
L9P-F02 found item 1's step-ups taking slots 1 and 3 over their AP64500's 5 A at HIGH. Record l9stk found the pack path's return
undeclared on boards A and E, and the energy chain still naming board E 2 oz. Round 3 re-decides item 1 on those figures (section 1r:
the coolers keep their step-up, and the modules hold Fan_PWM at no more than 70 %). It drafts the return's declarations (section 3e)
and the chain's correction (section 3f). Both Layer 9 outputs are read from copies in `inputs/` and never merged.

**Round 4 (3 October 2026, the owner's focused check of L9P-F02, section 1s).** Round 3's 70 % Fan_PWM maximum is WITHDRAWN: its
+0.129 A held only at the nominal 5.1 V, the fan runs at full speed whenever its PWM lead is not driven (the maker), and the
AP64500 on slots 1 and 3 is over its junction limit at HIGH with any cooler option. Slots 1 and 3 move to slot 2's LM5176 stage
(`apply_gen_sch_a_slotlm.py`), and the coolers keep their step-up at full speed.

**Rounds 7 and 8 (4 October 2026 evening and night, task T5b and the recheck V3, branch `fnd/l8r4` from set 29's candidate
`aa76c894`, section 3g).** The owner's review (RSM-01): board B's generator declares its ground return with typed figures (10.0 A,
21.0 A), and with this record's own fans12 draft the composed generator stops, 21.51 A of loads against the 21.0 A peak. Round 7
reproduces the stop, reconciles the load basis and drafts two corrections: the return's figures derived from the leads it
returns (`apply_gen_sch_b_gndret.py`: 13.30 A typical, 26.40 A peak as an UPPER BOUND, 27.9108 A with Layer 9's round 3 draft) and
the decoupling class row the cooler step-ups lacked (`apply_gen_sch_b_fandec.py`, a second stop behind the first). Board B's
composition then runs to its end. **The return path itself is a known defect, L8R2-F31, and it is OPEN.** The two boards' grounds
are joined by lead contacts and seventeen signal-ribbon conductors in parallel and nothing sets the division. Round 7's
calculation of that division sampled six contact cases; the collaborator's targeted recheck V3 returned NOT CONFIRMED (a
permitted corner it had left out puts 10.6375 A in a lead's ground pin against the printed 10 A). Round 8 enumerates every
vertex of the contact-resistance box (as drawn, on C-DEV rev 1: 12.092 A in a lead's pin 2 and 2.672 A in a ribbon conductor)
and drafts the correction: a dedicated ground return of three XT60 leads between the boards (`apply_gen_sch_a_gndrtn.py`,
`apply_gen_sch_b_gndrtn.py`), with which every branch that has a printed rating is inside it at every vertex on the composed
netlists. No independent check has read round 8 and nothing is applied. Every figure is in `l8r2_gndret.out`.

Figures carry a class: **MAKER** (printed in a held sheet), **INFERRED** (derived from printed figures under a stated assumption),
**ASSUMPTION** (no held document gives it), **BOUND** (a limit this record states and holds the design to). Every figure is in
`l8r2_drafts.out`; this page quotes it.

| File | What it is |
|---|---|
| `apply_gen_sch_b_fans12.py` | DRAFT, board B, item 1 (E11-40, R-190): each cooler fan on a 12 V step-up with an eFuse, its control lines isolated |
| `apply_gen_sch_a_vbus20ov.py` | DRAFT, board A, item 2 (S-111, R-48): VBUS20's over-voltage cut-off in VIN_RAW |
| `apply_gen_sch_b_panel5v.py` | DRAFT, board B, item 3 (L5R2-F03): PANEL_5V behind an eFuse ahead of F1 |
| `apply_gen_sch_a_d8v3.py` | DRAFT, board A, item 3 (L5R2-F05): board D's 3.3 V behind an eFuse |
| `apply_gen_sch_b_ph4.py` | DRAFT, board B, item 3 (L5R2-F04): J_QMX and J_CAM on the JST PH 1x4 land |
| `apply_gen_sch_c_pibtn.py` | DRAFT, board C, item 4 (the panel firmware's F-01): the PI button on U1 P1.3 with its pull-up and debounce |
| `apply_gen_sch_a_packrtn.py`, `apply_gen_sch_e_packrtn.py` | DRAFT, boards A and E, item 5 (round 3, record l9stk's finding): GND declared as a rail returning the pack path, in each generator's intent table |
| `apply_gen_sch_a_slotlm.py` | DRAFT, board A, round 4 (L9P-F02): slots 1 and 3 on slot 2's LM5176 stage, the AP64500s U4 and U6 retired; round 5: the three slot leads at 5.63 A |
| `apply_gen_sch_b_rt500.py` | DRAFT, board B, round 5 (O-20, the collaborator's B2): the six AP64500 slot bucks' RT 68 k to 200 k, 1.47 MHz to the maker's 500 kHz |
| `checks/astra-check-l9pf02-1.md` | the collaborator's focused check of round 4 (cx38, at `7b9336d0`), filed as received; answered in section 1t |
| `checks/astra-check-l9pf02-2.md` | the collaborator's targeted recheck of round 5 (cx39, at `3cb3a676`, the last run), filed as received; answered in section 1u |
| `apply_gen_sch_a_fb01.py` | DRAFT, board A, round 6 (F5-03): both divider resistors of every LM5176 5.1 V stage at 0.1 % (5.0019 to 5.1744 V) |
| `apply_energy_chain_e1oz.py` | a text correction for the integrator, item 6 (round 3): `pcb_energy_chain.yaml`'s board E conductors at 1 oz, after l9stk's decision is in the register |
| `check_l8r2_netlist.py` | what the regenerated netlists must show, parsed; NOT DRAWN on the committed netlists today |
| `l8r2_drafts.py`, `l8r2_drafts.out` | every figure with its class, the composition on boards A and B (and E, round 3), the designator census, the netlist check; round 3: record l9pwr's figures parsed for item 1 (section 2b), the pack returns (section 9), the energy chain's texts (section 10) |
| `fetch_held_back.py` | TI's TPS4811-Q1 sheet (SLUSEE5E) and four pages of Sanyo Denki's San Ace catalogue C1152B001 '25.10 (round 4), held back by their terms, fetched from the makers and checked by sha256 |
| `inputs/` | Layer 7's cooler identity (`fnd/l7pwr` at `2087060b`) and Layer 5's round 2 findings (`fnd/l5r2` at `6902db8f`); round 3: record l9pwr's output (`fnd/l9pwr` at `38ef774c`) and record l9stk's output and page (`fnd/l9stk` at `7388a84b`); copied byte for byte, `inputs/SOURCES.txt` |
| `v2/ecad/tools/tests/test_l8r2.py` | the predicates (section 7) |

## 1. Item 1: board B's coolers need 12 V (E11-40, R-190, Layer 7's F-L7-02; supplier task P1-2)

**The defect as found.** Board B's `J_FAN1` to `J_FAN3` carry the slot rail `+5V_Sn` (5.1 V) on pin 1 (`gen_sch_b.py`, the slot
loop). The cooler Layer 7 selected, Sanyo Denki 9WPA0412P6G001, prints 12 V rated, an operating range of 10.8 to 13.2 V, 0.17 A and
2.0 W, with a pulse sensor and a PWM input (MAKER, `inputs/l7pwr-cooler-identity-2087060b.md`). No 5 V IP68 40 mm fan exists in the
lines Layer 7 read. The PWM input's level, the pulse output's type and the starting current are NOT READ (the maker's manual
M0011876C is behind a form).

**The comparison (at most two, per the brief).**

| | (a) a step-up per slot from +5V_Sn | (b) one 12 V feed from board A over the bay harness |
|---|---|---|
| Parts | per slot: a TPS61089 boost, an eFuse, two 2N7002 stages | a 12 V buck-boost on board A (VBAT runs 9.7 to 17.4 V, so a buck cannot make 12 V), a new harness and connectors on A and B, per-slot switching on B |
| Interfaces | none new: everything is inside board B | a new board-to-board power interface (a Layer 5 contract, a Layer 7 harness) |
| The fan follows its slot | yes: an empty or unpowered slot's fan is dark, as its rail is | only with per-slot switches added on board B |
| Power at VBAT, three fans at full speed | 7.56 W (2.353 W a slot on +5V_Sn at the step-up's 0.85, ASSUMPTION; behind each slot rail's own converter, record l9pwr's R9: 7.5638 W. Round 2 printed 7.84 W on a flat 0.90 for the slot converters, corrected in round 3) | 6.74 W (one converter at 0.89, ASSUMPTION) |
| Difference | | (b) is 0.82 W lower at full speed, 0.23 W at the budget's 0.56 W a fan |

**SELECTED (SESSION): (a).** It needs no new interface, no harness and no board A change, and it keeps each fan with its own slot.
The 0.82 W that (b) would save at full speed is under the controls' duty in practice (R-150). **Round 3 kept (a) with the modules'
70 % Fan_PWM maximum, on record l9pwr's figures (section 1r); round 4 withdraws the maximum and moves slots 1 and 3 to slot 2's
LM5176 stage on board A, so the step-up stays and the fan runs at full speed in every state (section 1s).** Reverse by (b) if the bay harness gains a 12 V
pair for another reason.

**The circuit drawn, per slot s** (designators in board B's unused 700 block, `700 + 30 (s - 1) + k`, registered in `SLOT_EXTRA[s]`
the way `_cx()` registers its capacitors):

| Ref | Part, value | Nets | Basis |
|---|---|---|---|
| U7x1 | TPS61089 boost (C165129; land `Package_DFN_QFN:Texas_VQFN-RNR0011A-11`, the land board A drew at A17, `b8cef471`, and the land `lcsc_fill.py`'s TPS61089 rule names) | VIN and EN on +5V_Sn, VOUT on CFANs_12V | TI SLVSD38C: VIN 2.7 to 12 V, VOUT 4.5 to 12.6 V, EN absolute 7 V |
| R7x3, R7x4 | 88.7 k, 10 k (1 %) | FB | VREF 1.188 / 1.212 / 1.236 V: **output 11.508 / 11.962 / 12.430 V**, inside the fan's 10.8 to 13.2 V (MAKER, FB leakage included) |
| R7x1 | 301 k | FSW to SW | Equation 3: 498.1 kHz at 5.1 V in |
| R7x2 | 127 k | ILIM | the printed row: 7.3 / 8.1 / 8.9 A |
| L7x1 | 4.7 uH XAL6060-472ME (Isat 11 A) | +5V_Sn to SW | board A's own inductor; Isat 11 A over ILIM's 8.9 A maximum (TI's rule, 9.2.2.5); the inductor peak 1.545 A at the rated 0.17 A and 2.713 A at the eFuse's highest limit (4.9 V in, L -30 %, fsw -10 % ASSUMPTION, efficiency 0.80) |
| R7x5, C7x8 | 23.7 k, 47 nF | COMP | Equation 17 gives 23.8 k at an effective 33 uF (ASSUMPTION: 3 x 22 uF 25 V X7R 1210 at 12 V, 50 % under bias, no curve held) and a 10 kHz crossover; Equation 18 gives 49.0 nF; Equation 19 gives C6 7.0 pF, under 10 pF, so open. The crossover is 5 to 15 kHz over 66 to 22 uF, under min(fsw/10, fRHPZ/5) = 49.8 kHz (RHP zero 313 kHz) |
| C7x1, C7x2 | 100 nF BOOT; 4.7 uF 25 V X7R 0805 (C354262) VCC | | VCC "more than 1.0 uF" (declared class L, floor 1 uF) |
| C7x3, C7x4 | 10 uF 25 V 1210 (C2918497); 100 nF at VIN | +5V_Sn | 9.2.2.6 (declared class D) |
| C7x5 to C7x7 | 3 x 22 uF 25 V 1210 (C2918511) | CFANs_12V | 9.2.2.7: "three 22-uF ceramic output capacitors work for most applications" |
| U7x2 | TPS259631 eFuse (board B's `efuse()` helper, C2155778) | CFANs_12V to CFANs_V | TI SLVSET8A: **0.448 / 0.494 / 0.538 A** (R7x6 1.87 k by Equation 7, the tolerance of the wider neighbouring printed row, INFERRED); OVLO 100 k over 10 k **cuts the fan at 12.64 to 13.67 V**, 0.21 V over the rail's highest; EN pulled to +5V_Sn through R7x10 100 k (note 2) |
| Q7x1, R7x11 | 2N7002 (C8545), 10 k | gate +3V3_CMs, source FAN_TACHOs, drain CFANs_TACH | board B's `level()` helper: the module's pin sees no more than its own rail whatever the fan's pulse output is (NOT READ) |
| Q7x2, R7x12 | 2N7002, 10 k to +5V_Sn | gate +3V3_CMs, source FAN_PWMs (R51 kept), drain CFANs_PWM | non-inverting; with the module's Fan_PWM released (boot, reset) the fan's PWM reads high, the four-wire convention's full speed (INFERRED; the maker's level NOT READ) |
| J_FANs | JST-SH 1x4 (C160390, land unchanged) | 1 CFANs_V, 2 GND, 3 CFANs_TACH, 4 CFANs_PWM | |

**The nets' names (corrected 3 October 2026).** The cooler's nets are CFANs_12V, CFANs_V, CFANs_SW, CFANs_TACH, CFANs_PWM and the boost's small nodes CFANs_*: the first issue named them FANs_*, and board E's committed netlist already carries FAN1_PWM, FAN1_SW, FAN1_TACH and FAN2_PWM, FAN2_SW, FAN2_TACH for its mixers (found by this record's test that every new net is new on every board, added after the bring-up author's +3V3_D8 finding, section 3b). The module's own FAN_TACHOs and FAN_PWMs and the designators J_FANs are unchanged.

**The slot budget.** `pwr_budget.py`'s cooler row is 0.36 / 0.51 / 0.56 W a slot: a representative 30 mm 5 V fan, not the pick
(INFERRED, records/rv-pwr). The pick prints 2.0 W at full speed. Choice (a) puts 2.353 W on +5V_Sn a slot (0.461 A at 5.1 V,
0.480 A at 4.9 V), which adds 0.353 W of conversion. Round 2's draft moved the slot rail's fan row from `J_FANs` 0.1 A to the boost
at 0.47 A, over the rail's declared 5.0 A peak on slots 1 and 3. Round 3 puts the row at 0.33 A, the fan at the modules' 70 % maximum
(section 1r). The rail's typical declaration is not changed, which is a FINDING for board B's owner and Layer 4 (F2-01).

**The acceptance.** The regenerated board B netlist shows, per slot, `J_FANs` pin 1 on `CFANs_V`, pin 3 on `CFANs_TACH` and pin 4 on
`CFANs_PWM`; the boost's pin 9 on `+5V_Ss` and pin 6 on `CFANs_12V`; the eFuse between `CFANs_12V` and `CFANs_V`; and each stage's
gate on `+3V3_CMs` (`check_l8r2_netlist.py` FANS: NOT DRAWN today). **Bench rows (Layer 9, R-190's acceptance):**
- each cooler's pin 1 at 11.5 to 12.4 V at full speed and at a 10 % duty;
- the fan's start current recorded against the eFuse's 0.448 A (E11-35's class), with the start not failed;
- the loop's load step at 0.17 A;
- the tach read by the module on each slot;
- the PWM released at boot giving full speed.

**Contract texts (Layer 5; not edits).** IF-BAY-FANS (or the slot-cooler rows of IF-B internal) reads: "J_FAN1..3: pin 1 the
cooler's 12 V (11.51 to 12.43 V) behind a 0.448 to 0.538 A eFuse; pins 3 and 4 the fan's pulse and PWM leads behind 2N7002
stages to the module's Fan_Tacho and Fan_PWM; a cable out leaves the fan dark and the module's pins at their own pull-ups."

## 1r. Round 3: item 1 re-decided on record l9pwr's figures (L9P-F02, L9P-F03)

**SUPERSEDED by section 1s (round 4): the 70 % Fan_PWM maximum is WITHDRAWN; slots 1 and 3 move to the LM5176 stage.** The text
below is round 3's record, kept as it was decided.

Round 3, branch `fnd/l8r3` from set 28's `37bc2f1d`, 3 October 2026, the record's only author since the round 2 author's context ran
out. Record l9pwr's output is copied byte for byte from `fnd/l9pwr` at `38ef774c` (`inputs/l9pwr_budget-38ef774c.txt`) and its
section 5 is parsed by `l8r2_drafts.py` (`l8r2_drafts.out` section 2b); none of its figures is typed here.

**What record l9pwr found.** L9P-F02, ASSUMPTION TO BOUND: with this draft's step-ups, the AP64500s of slots 1 and 3 (board A's U4 and
U6) reach **5.010 A against their 5 A** at HIGH in PS-BUSY and PS-ALLTX. HIGH stacks the CM5's declared 1.6 A (no maker maximum), the
card's 9.1 W, the NVMe's maximum and the cooler at full speed, which takes 0.461 A of the slot rail. Record l9pwr also found that round
2's 7.84 W for the three coolers at VBAT took board A's slot converters at a flat 0.90: its R9 reads **7.5638 W** on each slot rail's
own converter (the AP64500 curves at their operating point, the LM5176's declared 0.90). Section 1's table now carries 7.5638 W, and
the flat 0.90 (`eta_slot`) is retired from the figures.

**A defect of round 2's draft that the finding exposes** (section 2b). The draft put the fan's row on the slot rail at 0.47 A, so the
declared loads of slots 1 and 3 on board B summed to **5.121 A against their declared 5.0 A peak**. That is over `intent.rail`'s own
allowance (loads at most 1.02 times the peak): evaluated by intent.py itself, the regenerated generator would have stopped at
`+5V_S1` ("declares a 5.00 A peak and its loads sum to 5.12 A"). Round 2 filed the declarations as a finding for board B's owner
(F2-01); they were a refusal of the draft's own generator.

**The options at HIGH, every state** (section 2b's table; the least margin over the eleven states of record l9pwr):

| Option | AP64500, slots 1 and 3 (5 A) | LM5176, slot 2 (7.096 A) | Slot 1's declared loads (5.0 A peak) | Device rail (L9P-F03) | What it needs |
|---|---|---|---|---|---|
| (a) as round 2 drafted it, full speed | 5.010 A, **-0.010 A (-0.2 %)**, PS-BUSY and PS-ALLTX | 4.255 A, +2.841 A | 5.121 A: REFUSED by intent.rail | unchanged | nothing |
| (a) with the modules' 70 % Fan_PWM maximum, the linear bound, the step-up at 0.85 | 4.871 A, **+0.129 A (+2.6 %)** | 4.117 A, +2.979 A | 4.981 A: accepted | unchanged | a firmware rule; the fan's input at 70 % (vendor answer or bench) |
| the same with the step-up at its low 0.80 | 4.892 A, +0.108 A (+2.2 %) | 4.137 A, +2.959 A | | unchanged | |
| the same by the fan law (0.343 of full power) | 4.707 A, +0.293 A (+5.9 %) | 3.952 A, +3.144 A | | unchanged | |
| (b) the cooler off the slot rail: one 12 V feed from board A | 4.548 A, **+0.452 A (+9.0 %)** | 3.794 A, +3.302 A | 4.651 A: accepted | unchanged (its converter on VBAT) | a 12 V buck-boost on board A, a new A-to-B interface and harness; one converter common to the three modules' coolers |
| (b) per slot: three feeds from board A | as (b) | as (b) | as (b) | unchanged | three buck-boosts on board A, a third pin on each slot lead, Layer 5 and Layer 7 texts, three converters' quiescent at VBAT |
| a part change of U4 and U6 | no held sheet of a pin-compatible part above 5 A; slot 2's LM5176 pattern (F-PR-04) would be a new board A stage | | | unchanged | board A's I-03 owner; not drafted here |

**Full speed comes only with the card's supply off.** The PWM stage is non-inverting and its drain is pulled to +5V_Sn, so with the
module's Fan_PWM released (module off, in reset, booting) the fan runs at full speed, the cooling side of a fault. The card socket's
supply is enabled by S{s}A_EN = EMCON_HW AND PCIE_PWR_EN{s} (gen_sch_b.py, U{s}16), and R{s}06 holds PCIE_PWR_EN{s} low until the
module's software raises it. With the card's output off, the slot carries at most **3.225 A** at HIGH (section 2b's "released"
column; the card buck's loss kept). The firmware rule below therefore orders the two: PCIE_PWR_EN only after the fan control runs
with its maximum.

**If the bound fails open** (the fan uncapped with the card on, a firmware fault), the slot reads the drafted 5.010 A. The AP64500's
inductor peak is then 6.075 A at VSYS's 17.375 V (L 20 % low and fsw 10 % low, ASSUMPTION). That is 0.725 A under its least HS peak
current limit of 6.8 A (MAKER, Diodes DS41979), so no protection acts; the stress is 0.2 % over the continuous rating CMP-001 compares
against.

**The bound's own limit.** A fan's input at a duty D is taken as at most D times its full-speed input. This is the linear bound, an
ASSUMPTION: by the fan laws a fan's shaft power goes with the cube of its speed, and a four-wire fan's speed follows its duty. It
fails only if more than **54.3 %** of the fan's full-speed input did not fall with its speed (f + (1 - f) x 0.343 > 0.70). The maker's
manual M0011876C (behind a form, F2-09) or the bench row below settles it.

**Airflow at the maximum** (INFERRED, the speed following the duty): about 70 % of the pick's 13.4 CFM free air, against the 3.7 CFM
free air of the representative 30 mm fan that L4-E12's exhaust model takes ("the 30 mm fan's 3.7 CFM (Sunon p.1) at 50 %"). The
maximum leaves the thermal model's air in hand, and the hold's duty (Layer 7's F-L7-05) is a setting at or under it.

**L9P-F03, the device rail.** No option feeds a cooler from +5V_DEV, so item 1 leaves the device rail's LM5176 U7 as record l9pwr
prints it, in every option and every state. In PS-ALLTX at HIGH that is **7.181 A DRAFTED against its loop's least 7.096 A (-0.086 A,
-1.2 %)**, 7.155 A DRAWN. The 0.027 A between DRAWN and DRAFTED is all this record's item 3: U901's RON (at most 0.1434 Ohm) at the
panel's 0.980 A, 0.138 W on +5V_DEV. The overrun is the drawn design's (I-03); item 1 neither adds to it nor removes it. The maximum
does lower the coolers' power at VBAT, from 7.5638 W at full speed to at most 5.29 W, 2.27 W less at HIGH. That reaches the fans' share
of L9P-F01's all-transmit basis, which is L4-E9's (F3-04).

**The decision (SESSION, under the owner's standing rule of 26 September 2026): (a) kept, with the modules' 70 % Fan_PWM maximum.**
- It holds every slot converter under its limit at HIGH in every state (least +0.129 A, +2.6 %, with the step-up at 0.85; +0.108 A at
  its low 0.80), and slots 1 and 3's declared loads under their 5.0 A (4.981 A). It needs no new interface, no harness and no board A
  change, and each fan stays with its own slot and goes dark with it.
- (b) as one 12 V feed would make one converter and one lead common to the three modules' coolers. ASM-002 names the kit's shared
  elements (four), and NEED-03's failure set is the loss of one module, so a fifth is a requirement-level change that this record does
  not take; it would be the owner's, as a residual risk.
- (b) per slot designs F02 out with the most margin (+0.452 A). It costs three converters on board A, a third pin on each slot lead,
  new Layer 5 and Layer 7 texts, and three converters' quiescent at VBAT. It stays the reversal.
- The owner's instruction of 2 October 2026 allows one design-out attempt per item, then a named measurement. The maximum is the
  design measure, and the fan's input at 70 % is its named measurement or vendor answer.
- No option spends money beyond the existing authorisations (nothing is bought; every option is generator text), and an option that
  changes no requirement stands. This is therefore the session's decision, not an OWNER DECISION.
- **Reverse by (b) per slot** if the fan's input at 70 % duty reads over 1.40 W (the bench row or the maker's manual), or if Layer 5
  cannot hold the maximum and its order in HW-FW-CONTRACT.

**The draft as changed** (`apply_gen_sch_b_fans12.py`; the designators, the nets and the circuit are unchanged):
- the slot rail's fan row on U7x1 is now **0.33 A** (1.4 W over 0.85 at 5.0 V), written in the form Layer 7's reader parses (section 7);
- the generator's comments state the maximum and the released state;
- the 12 V rail's note gives 0.117 A at the maximum beside the fan's rated 0.17 A.

**Firmware and contract texts (Layer 5's files; not edits).**
- HW-FW-CONTRACT, a new FW row: "Each compute module drives its cooler's Fan_PWM (board B J_FANs pin 4 through Q7x2) at no more than
  70 % duty, and raises PCIE_PWR_EN only after its fan control runs with that maximum. Released (module off, in reset, booting), the
  cooler runs at full speed by board B's pull-up while the card socket's supply is off. Basis: record l8r2 round 3, L9P-F02 (slots 1
  and 3's AP64500 under 5 A at HIGH)."
- IF-BAY-FANS, or IF-B internal's slot-cooler rows: add "the module's Fan_PWM at no more than 70 % duty".

**Bench rows (Layer 9, added to R-190's acceptance):**
- the fan's input power at 12.0 V and 25 C at 70 % and at 100 % duty, on three samples of the 9WPA0412P6G001: accept the 70 % input
  at most 1.40 W; on failure, lower the maximum to the duty that reads 1.40 W, or take (b) per slot;
- slot 1's +5V_S1 current (INA226 0x40) with the module stressed, the card at its maximum, the NVMe writing and the fan at the
  maximum: at most 5.0 A;
- the fan at full speed with Fan_PWM released and PCIE_PWR_EN low at boot.

## 1s, L9P-F02 focused check (round 4: the owner's five questions, 3 October 2026)

Round 4, the same branch and author, 3 October 2026 (from 23:04 CEST). Every figure below is printed by `l8r2_drafts.py` in
`l8r2_drafts.out` section 2c ("2c.N" is its question N); record l9pwr's rails are parsed from `inputs/`, never typed. The cooler's
figures come from the maker's own San Ace general catalogue C1152B001 '25.10, pages 362, 616, 623 and 633, served one page at a
time by the catalogue viewer the product page links (publish.sanyodenki.com); no redistribution grant was readable (the maker's
conditions of use page answered HTTP 403), so the four pages are held back: `fetch_held_back.py` fetches them into
`v2/vendor/fans/held/` and checks each by sha256, and `test_l8r2` reads the rows off them. The product page itself was re-read
(sha256 `90a9c2d2fc1f7457`, unchanged since Layer 7's transcription). The AP64500 sheet at the URL the owner gave
(diodes.com/datasheet/download/AP64500.pdf) is byte for byte the held `v2/vendor/diodes/diodes-ap64500.pdf` (DS41979 Rev 5-2,
sha256 `d3bcdc7dd4ca44cb`); the TPS61089 sheet is the held SLVSD38C. The fan's manual M0011876C is still behind a form: NOT READ.

**Round 5 (4 October 2026, from 00:07 CEST): the collaborator's focused check** (job cx38, at `7b9336d0`, filed unchanged as
`checks/astra-check-l9pf02-1.md`) read L9P-F02 NOT CONFIRMED with three blockers: B1 the AP64500's drawn frequency, B2 the 5.3 A
declaration under its own envelope, B3 an incomplete conditional package. This section is corrected in place (the rows marked R5);
section 1t answers each item.

**Round 6 (4 October 2026, from 00:42 CEST): the collaborator's targeted recheck** (job cx39, at `3cb3a676`, the second and last run,
filed unchanged as `checks/astra-check-l9pf02-2.md`) read L9P-F02 RECHECK: NOT CLOSED, the steady arithmetic and declarations
reproduced, with B1, B2, B3 and F5-03 still open. This section is corrected again in place (R6) and section 1u answers each item;
the coordinator's closing check follows.

**The compact table** (as corrected in round 5; the rows the collaborator's check moved are marked R5). Classes as in this page's
head: MAKER, INFERRED (a reading off a maker's graph, or arithmetic on maker figures under a stated assumption), ASSUMPTION,
BOUND; UNRESOLVED where no held document prints the figure.

| # | Figure | State | Boundary | Source | Verdict |
|---|---|---|---|---|---|
| 1a | round 3's **+0.129 A**: 4.871 A against 5 A | PS-BUSY and PS-ALLTX at HIGH (every load at its maximum at once) | slot side, AP64500 U4's output: CM5 8.0 W, card 9.1 W, NVMe and switch 3.99 W, switch core 0.676 W through board B's bucks on their curves, the fan 1.4 W (70 % of 2.0 W, the linear bound) over the step-up's 0.85; 24.844 W over the nominal 5.1 V | 2c.1, "+0.129 A (round 3's margin)" | a HIGH model state at the nominal voltage only |
| 1b | the declared **4.981 A**: +0.019 A against 5.0 A | none: a declaration intent.rail judges | slot side, board B's `_SLOT_LOADS` rows on +5V_S1 (CM5 1.6, U103 2.2, U104 0.7, U105 0.15, U116 0.001 A) plus the fan's row 0.33 A (1.4 W / 0.85 / 5.0 V), against the rail's declared peak (refused over 5.10 A) | 2c.1, "+0.019 A" | the declaration's distance from the source's rating; its rows are not the HIGH (U103 2.2 A against 1.959 A, U104 0.7 A against 0.865 A), so neither sum bounds the other |
| 1c | 1a at the least voltage: **5.118 A, -0.118 A** | PS-BUSY at HIGH | the same 24.844 W over 4.854 V: VFB 0.792 V on the 1 % divider gives 4.953 V, less the rail's 2 % drop budget; every load sits behind a converter and draws its power | 2c.1, "the same state at the least voltage" | **NOT A MARGIN** |
| 2a | the fan at 70 %, 12 V, free air: **NOT PRINTED** | 70 % duty | the maker's rows (MAKER, p.362): 100 %: 0.17 A, 2.0 W, 13700 min-1; 25 %: 0.03 A, 0.36 W, 3000 min-1; the speed at 70 % read off the maker's duty to speed example, 10,400 +-400 min-1 (INFERRED) | 2c.2 | UNRESOLVED; two assumed models give 0.99 to 1.15 W (the fan law through both rows) and 1.43 to 1.56 W (the chord in speed), neither a bound the maker prints: the linear bound's 1.40 W lies between them, so it bounds nothing |
| 2b | the supply: **up to 1.73 W at 70 %, 2.22 W at 100 %** | 12.43 V, the step-up's highest | the step-up's 11.51 to 12.43 V sits inside the fan's 10.8 to 13.2 V (MAKER); the maker prints the input at 12 V only; x1.111 assumes speed in proportion to voltage (INFERRED) | 2c.2 | UNRESOLVED at the maker; the envelope takes 2.75 W (R5, B2) |
| 2c | the operating point: **not printed** | against the cooler's pressure | the maker's ratings are "at free air" (catalogue, How to Read Specifications) | 2c.2 | UNRESOLVED |
| 2d | the boost's loss: **0.21 / 0.27 / 0.39 W** | 1.56 W out | TI Figure 7-2 read at 0.1 A and 12 V out, about 0.88 typical, at 3.6 V in, not the slot's 4.829 to 5.252 V (INFERRED); the draft's 0.85 and the envelope's 0.80 are ASSUMPTIONS no held source makes a minimum (R5) | 2c.2 | the envelope takes 0.80; C4-3 measures the chain's input |
| 2e | the start: **not printed**; a current-limited power of 6.69 W on 12 V, **8.36 W on the slot rail** | any start: power-up, a duty from 0 % (this fan stops at 0 %), a locked-rotor retry | "current several times the rated current may flow" (p.633); a locked rotor "the coil current is cut off at regular cycles ... restarts automatically" (p.616); the eFuse U7x2's inferred highest limit 0.538 A at 12.43 V over the step-up's assumed 0.80; the limit's response time and the step-up's own start are finite (SLVSET8A pp.6 to 7, SLVSD38C 8.3.3) | 2c.2 | UNRESOLVED; a CONDITIONAL calculation, not an instantaneous bound (R5) |
| 2f | the slot's other loads: **23.197 W**; the fan input the AP64500's 5 A leaves: 1.96 W at 5.1 V, **0.91 W at 4.854 V** | PS-BUSY at HIGH | slot side | 2c.2 | the 70 % maximum fails at the least voltage under even the lower assumed model (0.99 W) |
| 3 (R5) | at the envelope **5.222 A at 5.1 V, 5.487 A at 4.854 V** (fan 100 %, card on); **6.501 A** in a start, the inductor's peak 6.762 A nominal and 6.886 A at the low corner against the 6.8 to 9.2 A limit; 6.213 A with a degraded fan | boot, reset or watchdog restart, the last duty held after a firmware fault (up to 100 %, no maximum), a fan driver absent or unbound, an open PWM lead, a start with the card on, a degraded fan (2c.3's eight rows) | Fan_PWM is an open collector, unpowered at the module's shutdown (CM5 datasheet 2.11, MAKER); R7x12 pulls the fan's lead to +5V_Sn; open terminal = 100 % (p.362, MAKER); PCIE_PWR_EN held low by R{s}06 100 k only while the module's 3.3 V is off; the bootloader's PCIe handling and the reset state of the pin are not stated (taken as the worse); the drawn AP64500 runs at 1470.6 kHz (68 k on DS41979 Eq. 7) | 2c.3 | full speed is the default in every state the firmware does not drive; with the card on the AP64500 is over 5 A in each; in a start its HS limit MAY act at the low corner and need not, and hiccup needs 512 consecutive cycles (0.348 ms) of a start whose size and duration are not printed: POSSIBLE, NOT ESTABLISHED |
| 4a | cooling at 70 %: **at least 42.6 Pa at every flow up to 3.7 CFM**, against the basis fan's 27.4 Pa at most; free air 0.277 to 0.300 m3/min | 70 % duty | the approved basis (record l4e12 2h, parsed): the representative 30 mm fan's 3.7 CFM free air at 50 % through the heatsink, 0.873 l/s, +5.64 K over the mixed air at the CM5's 4.5 W; that fan's 0.11 inch H2O (Sunon, MAKER); the pick's 100 % curve under the fan laws at the speed's least reading, inside its 80 Pa plateau, and an unchanged air path (INFERRED). D-18 (record l7pwr 2d) compared free air only (13.4 against 3.7 CFM) and T-H1's mock-up credits the coolers' 0.38 m3/min free air at 12.0 V; neither states a pressure, so l4e12's 0.873 l/s is the only flow the approval used | 2c.4 | **HOLDS** as a modeled result: the pick's curve lies over the basis fan's at every flow. Half duty is not claimed (the 50 % reading's 30 +-5 Pa straddles 27.4 Pa, R5). The SoC at 8 W: UNRESOLVED (C4-5) |
| 4b (R5, R6) | the AP64500's junction: **not computed for the drawn stage**: no Diodes curve at its 1470.6 kHz. At each option's current at the least load voltage: (a) at the envelope 5.487 A and the 70 % maximum 5.118 A, **over the 5 A rating** (MAKER, the rating, not the curve); (b) 4.779 A, the maker's typical Figure 24 (500 kHz, 12 V in) read **48.4 +- 2 C**, a CONDITIONAL screen | C1's +50 C inside air (CONOPS 4 as record l4e12 quotes it: the normal mode's ceiling) | DS41979 p.5 theta-JA 45 C/W, recommended junction +125 C, the 5 A rating; Figure 24 typical. No loss comparison at the drawn frequency covering VIN, inductance and the source is held, so the 500 kHz curve is NOT claimed as a bound on the drawn stage (R6, the recheck's B1; round 5's ripple-term argument is withdrawn). Record l4e12's method's 166.5 to 137.0 C stay a 500 kHz SCREEN, not a temperature of the drawn stage | 2c.4 | **NOT ADEQUATELY RATED** with the cooler on the rail (the 5 A rating); option (b)'s thermal reading is a CONDITIONAL screen, and (b) is rejected on its interfaces; the retired part needs no characterisation |

**5. The decision (SESSION, under the owner's standing rule of 26 September 2026): slots 1 and 3 move to slot 2's LM5176 stage
(F-PR-04's own pattern), the coolers keep their 12 V step-up at full speed, board B's slot bucks are set to the maker's 500 kHz
(round 5), and round 3's 70 % Fan_PWM maximum is WITHDRAWN.**
- Not the maximum: rows 1c, 2f and 3. It is a firmware rule that the hardware's own defaults defeat, and it holds only at the
  nominal voltage.
- Not (b) per slot alone: it takes the fan off the rail but costs three converters, a third lead pin and new Layer 5 and Layer 7
  texts, and the AP64500's 4.779 A at the least voltage reads past the typical derating at C1's air in a CONDITIONAL screen (row 4b).
- The LM5176 stage is the part this board already carries in five stages (C442493, every land in the library): no harness and no
  new interface. Its average loop limits at 7.096 A at its least (43 mV over the 6 mOhm ISNS shunt at +1 %, parsed from record
  l9pwr); its minimum buck valley threshold, about 12.7 A with the CS shunt's tolerance (the collaborator's arithmetic), is above
  every case below.
- Board B's six AP64500 slot bucks draw 68 k, which sets 1.47 MHz (open item O-20), while the envelope takes their input through
  the maker's 500 kHz curves: `apply_gen_sch_b_rt500.py` sets RT 200 k, O-20's own recommendation, so the curves apply (the 12 V
  curve taken for the 5.1 V input, rv-pwr's rule).
- Approved service is not reduced: the module's fan control may run the cooler to 100 % whenever the SoC asks.
- No requirement changes; nothing is bought (generator text only). The test of 21 September 2026 leaves it the session's.
- Reverse by (b) per slot together with a converter above the AP64500 on slots 1 and 3, if the LM5176 stage fails C4-1 or C4-6.

**The voltage window (R6, F5-03 corrected).** `apply_gen_sch_a_fb01.py` sets both divider resistors of every LM5176 5.1 V stage at
0.1 % (slot 2's R32 and R33, the device rail's R40 and R41, and slots 1 and 3's R501, R502, R531, R532 where slotlm is drawn), the
values unchanged (53.6 k over 10 k, the nominal 5.088 V and every loop design as before). On VREF 0.788 to 0.812 V (SNVSAI1D) with
IBIAS(FB) at most 25 nA through 53.6 k (1.34 mV) the output is **5.0019 to 5.1744 V**, inside the CM5's 4.75 to 5.25 V with 75.6 mV
to its top before the load's transient (C4-1 measures it); with the 1 % divider it was 4.928 to 5.252 V. The least voltage at the
loads with the rail's 2 % drop rises from 4.8295 to **4.9019 V**, and every current corner below is taken there.

**The envelopes (R5 steady, R6 start-up and fault, B2).** Every slot load at HIGH at once (record l9pwr's 23.197 W on S1 in PS-BUSY
and PS-ALLTX before the cooler, board B's bucks at 500 kHz) plus the cooler's branch:
- the steady envelope: the fan's 2.75 W bound at the step-up's 12.43 V top over the step-up's worst 0.80 (ASSUMPTION), 3.4375 W;
  26.635 W over 4.9019 V: **5.4336 A**;
- the bounded start: the cooler branch's input on +5V_Sn as a 100 us moving average at most **1.80 A**, and over the branch's
  steady current as measured on the specimen, plus its tolerance, for at most 1.0 s a start (BOUND, held by C4-3's waveform limits;
  the desk expects that steady current at 0.7013 A at 4.9019 V and 0.6643 A at 5.1744 V, 2.75 W over 0.80, an expected value and
  not the threshold; the eFuse-limited calculation, 0.538 A at 12.43 V over
  0.80, gives 1.7056 A inside it, and the eFuse's own response is 87 us typical, spanned by the 100 us average): 23.197 W over
  4.9019 V plus 1.80 A, **6.5323 A**;
- a degraded cooler held steady just under its eFuse's least limit (0.448 A at 12.43 V over 0.80, a fault): **6.1525 A**;
- slot 2 on its own HIGH with the cooler's bounded start: **5.7473 A**; its S-98 coincidence (5.63 A) lies inside; I-03's
  all-peak bound stays I-03's (F6-03).

Both boards declare **6.6 A** on the three slot leads (the largest need 6.5323 A); the conductor checks that read the declared peak
(dc_drop's density verdict, `via_current.py`, `rail_crossings.py`) then judge the copper at the start-up and fault envelope:

| Declaration | Round 4 | Round 5 | Now (round 6) |
|---|---|---|---|
| board A, `+5V_S1`, `+5V_S2`, `+5V_S3` peak and the `J_5V_Sn` load (slotlm) | 5.3 A (slots 1, 3), 5.63 A (slot 2) | 5.63 A | **6.6 A** on all three |
| board A, VBAT's entries Q501, Q28, Q531 (slotlm) | 2.09, 2.22, 2.09 A | 2.22 A | **2.60 A** each (6.6 x 5.1 / (0.90 x 14.4) = 2.597) |
| board A, GND's returns R506, R170, R536 (packrtn, any order with slotlm and fb01) | 2.09, 2.22, 2.09 A | 2.22 A | **2.60 A** each |
| board B, `+5V_S1`, `+5V_S2`, `+5V_S3` peak (fans12) | 5.3 A, 5.63 A | 5.63 A | **6.6 A**; slot 1's declared loads 5.341 A, accepted by intent.rail |
| board B, the fan's row on U7x1 (fans12; Layer 7's reader form) | 0.47 A | 0.69 A | 0.69 A (the steady envelope: 2.75 W over 0.80 at 5.0 V) |
| board B, CFANs_12V and CFANs_V typical (fans12) | 0.17 A | 0.22 A | 0.22 A |

**The margins in every state** (2c.5; slots 1 and 3 at HIGH on the LM5176 stage at 4.9019 V; the loop's least is 43 mV over 6 mOhm
at +1 %, **7.095710 A**, unrounded):

| State | A at 5.1 V | steady, at 4.9019 V | bounded start | degraded | margin: steady / start / degraded |
|---|---|---|---|---|---|
| PS-IDLE, PS-IDLE-SPEC, PS-RED-b (slot 3, the higher) | 3.5064 | 3.6481 | 4.7469 | 4.3671 | +3.4476 / +2.3489 / +2.7286 A |
| PS-TYP (slot 3) | 4.5362 | 4.7195 | 5.8183 | 5.4385 | +2.3762 / +1.2774 / +1.6572 A |
| PS-BUSY, PS-ALLTX (slots 1 and 3) | 5.2225 | **5.4336** | **6.5323** | 6.1525 | **+1.6622 (23.4 %) / +0.5634 / +0.9432 A** |
| PS-EMCON (slots 1 and 3) | 2.5776 | 2.6817 | 3.7805 | 3.4007 | +4.4140 / +3.3152 / +3.6950 A |
| PS-RED, PS-RED2, PS-SURV-R (slot 3 alone) | 2.0380 | 2.1203 | 3.2191 | 2.8393 | +4.9754 / +3.8766 / +4.2564 A |
| the declared peak | | 6.6 | | | +0.4957 A |

- The stage's hottest part, its buck-side high FET (CSD19532Q5B), screened over C4-1's whole steady matrix at 17.375 V in with the
  output at its highest 5.1744 V (estimates on typical charges and an assumed hot RDS(on), NOT bounds):

  | Steady point | Loss, Qrr scaled with current | Loss, the sheet's Qrr unscaled | RthJA for +125 C at C1's 50 C (unscaled) |
  |---|---|---|---|
  | 3.0 A | 0.890 W | 1.716 W | 43.70 C/W |
  | 4.1 A | 1.042 W | 1.804 W | 41.58 C/W |
  | 5.4336 A (the steady envelope) | 1.238 W | 1.921 W | 39.05 C/W |
  | 6.6 A (the declared peak; above the start's 6.5323 A and the degraded 6.1525 A) | 1.419 W | 2.033 W | **36.89 C/W** |

  The sheet's +150 C is an absolute maximum, so the acceptance is +125 C. The binding junction acceptance is C4-1's MEASURED bound
  (the stage's measured loss, which is at least any one FET's, times RthJC 0.8 C/W over each FET's measured case); the copper
  figure above is C4-6's desk screen.
- The cost: at PLAN, VBAT side, +0.373 W in the profile (PS-IDLE-SPEC), +0.730 W in PS-TYP, +0.872 W in PS-BUSY, +0.822 W in
  PS-ALLTX (the stages' declared 0.90, NOT PLOTTED by the maker, against the AP64500's curve point). The same watts are heat in the
  case. FW-A15's bench reading of the stage settles the figure (F4-05).

**The drafts as changed** (2c, sections 5 to 8 of the output):
- `apply_gen_sch_a_slotlm.py` (board A): the two buck5 calls become slot 2's lm5176 call for S1 and S3 with their SLOT_EN
  pull-downs (R30, R38 kept) and INA226 monitors (U8, U10 kept, now across the 6 mOhm ISNS shunts R505, R535); VBAT's U4 and U6
  become Q501 and Q531, and Q28 follows, at 2.60 A; the slot rails' shunts, switches (U501, U531) and the peak 6.6 A on all three
  slots, with slot 2's note; SECTIONS. Designators in the free 500 block (500 + k on slot 1, 530 + k on slot 3: U, Q 1 to 4, L, D 1
  and 2, R 1 to 12, C 1 to 19); retired U4, U6, L3, L5, C28 to C33, C40 to C45, C112, C114, R28, R29, R31, R36, R37, R39, R45, R47,
  R129, R131. It follows L4-E11's charger (its anchor names VBAT's "U4": 2.0), which L4-E9's order already gives; mainpb stays at
  R248 and C247. Where fb01's helper is present its stages carry fb01's keywords.
- `apply_gen_sch_a_fb01.py` (new in round 6, board A): the lm5176() helper gains `rfb_tol="1%"` (its default keeps every other
  stage) and writes the top resistor's tolerance from it; slot 2's and the device rail's calls pass `rfb_val="10k 0.1%",
  rfb_tol="0.1%"`, and slots 1 and 3's where slotlm is drawn. No designator, net or land; with packrtn and slotlm the three give one
  generator in all six orders.
- `apply_gen_sch_b_fans12.py`: the fan's row at the steady envelope, 0.69 A; the three slots declared at 6.6 A; the fan's rails at
  0.22 A typical; designators unchanged.
- `apply_gen_sch_b_rt500.py` (round 5, board B): buck33's RT 68 k to 200 k 1 % (the six slot bucks at 500 kHz); composes with this
  record's, record l8gnd's and Layer 6's board B drafts.
- `apply_gen_sch_a_packrtn.py`: where slotlm is applied first, slots 1 and 3's ground ends are their CS shunts R506 and R536 and
  slot 2's R170, at 2.60 A; any order gives one generator.
- `check_l8r2_netlist.py`: SLOTS and, in round 6, FB01 (the eight divider resistors' values naming 0.1 %): NOT DRAWN today, DRAWN on
  its fixture, FAIL with one resistor left at 1 %.

**What remains CONDITIONAL, each with its owner, specimen, numerical acceptance and failure action (R5 and R6, B3):**
- **C4-1, the stage over the envelopes (board A's owner, FW-A15's bench).** Specimen: board A's slot 1 or slot 3 stage as placed and
  routed, on board A's own copper, with the 0.1 % divider. Matrix: VIN 9.7, 14.4 and 17.4 V; IOUT 3.0, 4.1, 5.4336 and 6.6 A steady
  for 30 minutes each at 50 C ambient (6.6 A covers the bounded start's 6.5323 A and the degraded cooler's 6.1525 A); a step
  5.4336 to 6.6 A held 1 s and back. Measured: VOUT at J_5V_Sn, each of the four FETs' case on its drain tab by thermocouple, the
  controller's case, the stage's input and output power. Acceptance at every steady point: VOUT 5.00 to 5.18 V (the window) and at
  most 5.25 V and at least 4.90 V through the step at J_5V_Sn; no average-loop limiting at or under 6.6 A; each FET's junction,
  inferred as its measured case plus the stage's MEASURED loss (input less output power, which bounds any one FET's) times RthJC
  0.8 C/W, at most +125 C; the efficiency at least 0.90 at 3.0 and 4.1 A at 14.4 V (the budget's points) and recorded at every
  point. Failure: more copper or vias under the FETs (C4-6), a lower switching frequency, or the reversal.
- **C4-2, the loop and bulk ripple of slots 1 and 3 (board A's analysis and layout author).** Unchanged: the scripts re-run on the
  slot's own remote capacitance with phase margin at least 50 degrees, gain margin at least 10 dB on the narrow band and positive on
  the widened band, bulk ripple at most 1.8 A rms per EEHZK1E151XP; then C4-1's step. Failure: the compensation or the bulk redesigned.
- **C4-3, the actual cooler chain in a loaded slot (Layer 9, R-190 and E11-35).** Specimen: board B's drafted chain as built (U7x1
  TPS61089 with its parts, U7x2 eFuse at 1.87 k, Q7x1 and Q7x2, J_FANs) with three 9WPA0412P6G001 on their fitted CM5 coolers, fed
  from the slot rail at 4.90 V and 5.18 V (the window) while an electronic load draws the slot's other 23.2 W, at -20, +25 and +70 C.
  Measured at 1 MS/s or faster: the branch's input current on +5V_Sn (a shunt at U7x1's input), the slot rail's current, +5V_Sn at
  the CM5's receptacle, the eFuse's FLT, the tach. Events: steady at 25, 50, 70 and 100 % duty and released; cold start of the slot
  rail; a warm module reset with the card on; PWM release; the PWM lead opened; the rotor locked for 30 s and released; a duty step
  0 to 100 %. Acceptance, the WAVEFORM (R6): the branch's steady input at most 3.44 W at every point; in every event its 100 us
  moving average at most **1.80 A** at every instant; and the time it spends above I_SS plus its tolerance at most **1.0 s** per
  start (locked-rotor retries counted, each a start), where I_SS is the branch's steady current measured on that specimen at the
  event's own supply voltage, duty and temperature (the mean of the 100 us moving average over the last 10 s of a 60 s hold after
  the start settles) and the tolerance is 10 % of I_SS or 0.05 A, the larger (closing check, MINOR; the desk's 0.7013 A at 4.9019 V
  and 100 % duty is the expected I_SS, not the threshold); the slot rail's 100 us moving average at most 6.6 A throughout; the instantaneous peak recorded (the step-up's own
  switch limit, 7.3 to 8.9 A, bounds it, MAKER); +5V_Sn at the receptacle at least 4.75 V throughout; the start completes (the tach
  within 10 % of the commanded speed in 5 s) without the eFuse's FLT latching. Failure: a steady input over 3.44 W restates the
  steady envelope and the fan row, or rejects the fan; a waveform over 1.80 A or 1.0 s restates the start bound and both boards' 6.6 A
  (the loop's 7.0957 A least leaves 0.4957 A) or changes the eFuse's ILM or dVdT; a droop under 4.75 V changes the step-up's soft
  start or its enable. Until then the eFuse's 0.448 to 0.538 A (inferred between printed rows) and the step-up's 0.80 stay
  ASSUMPTIONS.
- **C4-4, the maker's answer (drafted, not sent; the owner's to send).** To Sanyo Denki, for 9WPA0412P6G001: the PWM input's levels
  and frequency range (the catalogue prints an example, VIH 4.75 to 5.25 V, VIL 0 to 0.4 V, 25 kHz, "differ with models"; with the
  0.1 % divider the draft's pull-up to +5V_Sn reaches 5.1744 V, inside the example), the starting current and its duration, the
  input at 70 % duty and against a static pressure, the pulse output's ratings. Failure (an answer that excludes the drafted
  interface): the interface corrected.
- **C4-5, the SoC at 8 W (Layer 7 and record l4e12 own the cooling basis; Layer 9 runs it).** Unchanged from round 5: the fitted CM5
  at 8 W in C1's +50 C inside air for 30 minutes: (1) at 100 % duty the SoC at most 85 C with no thermal throttling logged; (2) the
  fan control's policy no more throttled time than 100 %; (3) E3-O's line at +55 C. Failure: (1) a finding for Layer 7 and l4e12;
  (2) Layer 5's fan curve corrected.
- **C4-6, fit and copper (board A's layout owner, the box).** Acceptance: both stages placed in slot columns 1 and 3 of
  `gen_pcb_a3.py`'s template inside board A's outline, with `check_pcb_a.py` ALL PASS (outline, overlaps, the stack height map
  against the case) and 0 hard DRC (the hard set); the desk SCREEN: each buck-side high FET's drain tab on routed copper whose
  computed RthJA is at most **36.89 C/W**, the matrix's highest steady point (6.6 A at 17.375 V) with the sheet's Qrr unscaled. It is
  a screen on typical charges; C4-1's measured bound decides. Failure: copper or vias added, the stage's parts moved within the
  column, or the reversal.

**Rows owed to others (texts; not edits of their files):**
- Layer 5, HW-FW-CONTRACT: round 3's proposed FW row (the 70 % maximum and its PCIE_PWR_EN order) is WITHDRAWN before entry. New
  FW row: "Each compute module drives its cooler's Fan_PWM at 25 kHz (a 40000 ns period; the stock CM5 tree's 41566 ns is 24.06 kHz
  against the maker's printed 25 kHz) with a duty set by the SoC's temperature up to 100 %, never 0 % while the slot runs (this fan
  stops at 0 % and each restart is a start, catalogue p.362); a tach reading under the commanded speed is reported as a stalled
  fan or an open lead (V-E07)."
- Layer 5, IF-BAY-FANS or IF-B internal's slot-cooler rows: "J_FANs pin 4 is the fan's PWM input; open, the fan runs at full
  speed (the maker); pin 1 the cooler's 12 V (11.51 to 12.43 V) behind a 0.448 to 0.538 A eFuse; the branch at most 3.44 W steady on
  +5V_Sn and its start at most 1.80 A (100 us average) for at most 1.0 s"; the "no more than 70 %" text of section 1r is not entered.
- Layer 5, IF-AB (the slot leads): +5V_S1, +5V_S2 and +5V_S3 declared **6.6 A** at both ends (round 6; slots 1 and 3 were 5.0 A, slot
  2 5.63 A); the stages' output 5.0019 to 5.1744 V with the 0.1 % divider; the loop's least 7.0957 A.
- Layer 5, HW-FW-CONTRACT FW-A09 (the six INA226 on the kit bus), and the firmware that masters that bus (PANEL.md's address table):
  "U8 0x40 (+5V_S1, R505 6 mOhm) and U10 0x44 (+5V_S3, R535 6 mOhm), full scale 13.65 A each" in place of R31 and R39 at 5 mOhm
  (16.38 A); calibrate each for its shunt; set each slot's alert at the steady envelope's 5.43 A filtered over 1.0 s (the start
  bound's duration), so a degraded cooler's steady 6.15 A is reported; the stage's 7.0957 A loop stays the hard limit.
- Layer 6: the two stages' rows (2 x LM5176PWPR C442493, 8 x CSD19532Q5B C473333, 2 x XAL1010-682ME, 2 x 6 mOhm WSL2512 C843882,
  6 x EEHZK1E151XP C542453, 4 x BAT46W C83152 and the passives as slot 2's); retired 2 x AP64500SP-13, 2 x XAL6060-472ME and their
  passives; a 200 k 1 % code for board B's six RTs (R104, R109, R204, R209, R304, R309); 0.1 % codes for 53.6 k and 10 k on board
  A's R32, R33, R40, R41, R501, R502, R531, R532 (record l6r2's table keys the four drawn ones by their 1 % values and no longer
  applies to them, its own rule).

## 1t, answers to the collaborator's check (astra-check-l9pf02-1, cx38, at 7b9336d0; filed unchanged in `checks/`)

The check read L9P-F02 NOT CONFIRMED with three blockers and found no requirement change justified; its only owner item is sending
C4-4's question, which stays drafted and unsent. Each answer below is printed in `l8r2_drafts.out` section 2c (round 5) and held by
`test_l8r2`. L9P-F02 stays OPEN until the corrections are implemented and verified; the physical claims stay CONDITIONAL until
C4-1 to C4-6 pass.

| Item | The check's finding | The answer (round 5) | Where | Status |
|---|---|---|---|---|
| B1 | the drawn 68 k programs the AP64500 at about 1.47 MHz, not the 500 kHz of the efficiency, derating and ripple figures; a hiccup stated as certain and exact junction temperatures unsupported | 1470.6 kHz by DS41979 Eq. 7 (68 k), confirmed; no Diodes curve at that frequency, so no junction of the drawn stage is computed. The claim is restated on the maker's typical Figure 24 at each option's current at the least load voltage (5.487 and 5.118 A over the 5 A rating; (b)'s 4.779 A ends at 48.4 C, under C1's 50 C), an upper bound on the drawn stage's allowed air because its loss at 1.47 MHz is at least its 500 kHz loss less 5.3 mW; record l4e12's method's 166.5 to 137.0 C kept only as a 500 kHz screen. Hiccup restated: the start's inductor peak at the drawn frequency is 6.762 A nominal and 6.886 A at the low corner against the 6.8 to 9.2 A limit, so the limit may act and need not, and hiccup needs 512 cycles (0.348 ms) of a start whose size and duration are not printed: POSSIBLE, NOT ESTABLISHED. The conclusion holds: not adequately rated | 1s rows 3 and 4b; 2c.3, 2c.4 | ANSWERED |
| B2 | the 5.3 A declaration is exceeded by its own fan-voltage and loss cases; C4-3's 0.30 A permits about 5.768 A | the envelope first: every slot load at HIGH (23.197 W, board B's bucks at 500 kHz by `apply_gen_sch_b_rt500.py`, O-20) plus the fan's 2.75 W bound at 12.43 V over the step-up's 0.80 (3.4375 W): 5.515 A at the stage's least 4.829 V. Both boards declare 5.63 A on the three slot leads; VBAT's entries and GND's returns 2.22 A; board B's fan row 0.69 A (slot 1's loads 5.341 A, accepted). Margins to 7.096 A: +1.581 A (22.3 %) at the envelope, +0.562 A in a start (CONDITIONAL), +0.851 A with a degraded fan. C4-3's limit is now the envelope's branch, 3.44 W on +5V_Sn, and C4-1 runs at 5.63 A steady with 6.6 A and 6.3 A cases | 1s "the corrected envelope", the margins table, C4-1, C4-3; the drafts | CORRECTED |
| B3 | C4-3 must test the boost-powered, simultaneously loaded slot; C4-5 needs a measurable SoC criterion; C4-6 needs fit and copper acceptance; the start assumptions stay CONDITIONAL | C4-3 rewritten on the actual chain in a slot loaded to 23.2 W, with cold start, warm reset, PWM release, open lead, locked rotor and duty steps, and numeric limits (3.44 W steady, 8.36 W for at most 1 s, 4.75 V at the receptacle); C4-5 with a fitted CM5 at 8 W in C1's 50 C air, SoC at most 85 C and no throttling at 100 % duty, the policy costing no throttled time, E3-O's line at +55 C; C4-6 with check_pcb_a.py ALL PASS, 0 hard DRC and RthJA at most 38.9 C/W per buck-side high FET; the eFuse's window and the step-up's 0.80 named ASSUMPTIONS until C4-3 | 1s C4-1 to C4-6 | ANSWERED; the conditions stay OPEN |
| Point 3 | the firmware-failure row still assumed a 70 % last duty | the last duty is up to 100 % (no maximum): that row now reads the envelope, 5.487 A on the AP64500, +1.581 A on the stage | 2c.3 | CORRECTED |
| Point 4, minor | half-duty cooling has no reading margin (30 +-5 Pa against 27.4 Pa) | not claimed; only the 70 % comparison stands, as a modeled result under the fan laws and an unchanged air path | 1s row 4a; 2c.4 | CORRECTED |
| Point 5 | the FET's +150 C is an absolute maximum; the estimate rests on assumptions (hot RDS(on), plateau, Qrr scaling) | the acceptance is +125 C; the estimate is printed at the envelope (112.4 C) and the declared peak (113.3 C) with the unscaled-Qrr sensitivity (146.3 C) and the copper each needs (60.1 and 38.9 C/W): CONDITIONAL on C4-1 and C4-6 | 1s; 2c.5 | ANSWERED, CONDITIONAL |
| Point 5, device rail | 7.181 A exceeds the device rail's loop least by 0.085 A | carried as L9P-F03 (F3-05, board A's I-03); its FET at 7.181 A estimates 1.510 W, 125.5 C on 1 inch2 (F4-06) | 1s; F3-05, F4-06 | OPEN, not this item's |
| Point 2 | TI's Figure 7-2 is typical at 3.6 V in; 0.80 is not a held minimum; the start power is a conditional calculation | stated so in rows 2d and 2e; the envelope takes 0.80 as an ASSUMPTION and C4-3 measures the chain's input | 1s rows 2d, 2e; 2c.2 | ANSWERED |
| C4-1, C4-2, C4-4 | C4-1's 5.3 A misses the corners; C4-2 confirmed as conditional; C4-4 confirmed, the owner's contact | C4-1 extended to the envelope's matrix with case, regulation and efficiency limits; C4-2 and C4-4 kept, each with a failure action | 1s | ANSWERED |
| Not found by the check, found here | the drawn LM5176 5.1 V stages (slot 2, the device rail, now slots 1 and 3) reach 5.252 V at their reference and divider extremes, 2 mV over the CM5's 5.25 V input | a finding for board A's owner: 0.1 % divider parts give 5.003 to 5.173 V (the helper writes the 1 % suffix itself) | 2c.5; F5-03 | OPEN, a finding |


## 1u, answers to the recheck (astra-check-l9pf02-2, cx39, at 3cb3a676; filed unchanged in `checks/`)

The recheck reproduced round 5's steady arithmetic (23.197074 W, 26.634574 W, 5.514996 A at 4.829482 V), the VBAT bookkeeping and
the RT draft, and kept four items open. Each answer is printed in `l8r2_drafts.out` section 2c (round 6) and held by `test_l8r2`.
L9P-F02 stays OPEN until the corrections are implemented and verified; the physical claims stay CONDITIONAL until C4-1 to C4-6
pass. The only owner item remains sending C4-4's drafted question.

| Item | The recheck's finding | The answer (round 6) | Where | Status |
|---|---|---|---|---|
| B1 | the 500 kHz Figure 24 is not an upper bound on the drawn 1.47 MHz stage (the 5.3 mW ripple term varies to 11.1 mW over VIN and L, and the comparison would need the added switching loss bounded); the 48.4 C reading carries +-2 C | the strict upper-bound claim is REMOVED and round 5's ripple-term argument withdrawn. What stands: the fan-fed options exceed the AP64500's 5 A rating at the least load voltage (5.487 and 5.118 A, MAKER); option (b)'s 4.779 A reads 48.4 +- 2 C on the typical curve, a CONDITIONAL screen; (b) is rejected on its interfaces. The retired part is not characterised | 1s row 4b; 2c.4 | ANSWERED |
| B2 | the 5.63 A declaration is below the model's 6.534 A start and 6.245 A degraded case, which the conductor checks read through the declared peak; a 10 ms average does not bound the peak (12 W for 5 ms passes it) | the bounded start-up envelope is a BOUND with a waveform: the cooler branch at most 1.80 A as a 100 us moving average and over its measured steady current plus a stated tolerance for at most 1.0 s a start (restated after the closing check, below); at the corrected least load voltage 4.9019 V the slot needs 6.5323 A (start), 6.1525 A (degraded), 5.4336 A (steady), slot 2 5.7473 A. Both boards declare **6.6 A** on the three slot leads; VBAT's entries and GND's returns 2.60 A. C4-3 accepts the waveform (1 MS/s; 1.80 A at every instant of the 100 us average, at most 1.0 s over the measured steady current plus its tolerance, the slot at most 6.6 A) and records the instantaneous peak, bounded by the step-up's switch limit | 1s "the envelopes", the declarations table, C4-3; slotlm, fans12, packrtn | CORRECTED |
| B3 | C4-1's case limit covered 5.63 A only and C4-6's 38.9 C/W the envelope; the unscaled-Qrr estimate was called a bound; 6.3 A needs 37.48 C/W | C4-1 accepts at EVERY steady point of its matrix (3.0, 4.1, 5.4336, 6.6 A at 9.7, 14.4, 17.4 V) a junction inferred from the measured case plus the stage's MEASURED loss (input less output power, at least any one FET's) times RthJC 0.8 C/W, at most +125 C. C4-6's desk screen is taken at the matrix's highest steady point, 6.6 A at 17.375 V with the sheet's Qrr unscaled: at most **36.89 C/W**; it is named a screen on typical charges, not a bound | 1s C4-1, C4-6; 2c.5 | CORRECTED |
| F5-03 | recording the 5.252 V defect does not correct it | CORRECTED by `apply_gen_sch_a_fb01.py`: both divider resistors of slot 2's, the device rail's and slots 1 and 3's stages at 0.1 % through a helper keyword (`rfb_tol`, default 1 %), the values unchanged: **5.0019 to 5.1744 V** with IBIAS(FB), inside the CM5's 4.75 to 5.25 V; the least load voltage 4.9019 V carries every corner above; `check_l8r2_netlist.py` FB01 reads the eight values on the regenerated netlist | 1s "the voltage window"; 2c.5; F6-01 | CORRECTED (drafted) |
| Minor | +0.562 A came from rounded intermediates; 7.096 A is the window's minimum | the loop's least is computed from VSNS 43 mV over 6 mOhm at +1 %, 7.095710 A, and every margin is printed to four places | 2c.5 | CORRECTED |

**The coordinator's closing check (after the collaborator's two runs): L9P-F02 CLOSED AS CONDITIONAL**, with one MINOR item done
here on 4 October 2026 (01:07 CEST): C4-3's duration criterion named "above the steady 0.712 A", the branch's steady current at
round 5's least voltage (4.829 V). It now names the steady current I_SS MEASURED on the specimen at the event's own voltage, duty and
temperature, plus a tolerance of 10 % of I_SS or 0.05 A (the larger), for at most 1.0 s per start; the desk figure, 2.75 W over 0.80
at 4.9019 V, 0.7013 A (0.6643 A at 5.1744 V), is the expected value, not the threshold. The physical claims stay CONDITIONAL on
C4-1 to C4-6.

## 2. Item 2: VBUS20 against U2's single faults (S-111, R-48; supplier task P1-3)

**The defect as found** (records/s120 section 8). With U2's high side Q2 shorted, VBUS20 follows VIN_RAW less Q5's body diode:
35.2 V at 36 V in, 41.7 V at board E's lockout. With R6 open or FB shorted, nothing on board A bounds the bus. Either passes U3's
absolute 32 V and, while the charger still switches, Q7's 30 V. There is no clamp and no exemption.

**The two options, decided on the printed data.**
- **An SMCJ22A on VBUS20: REJECTED.**
  - Its standoff, 22.0 V, sits over the regulated band's 20.96 V.
  - Its breakdown, 24.40 to 26.90 V at 1 mA (MAKER, Littelfuse SMCJ, 11/20/15), lies inside REQ-015's 9 to 36 V in service. So a
    source holding VBUS20 there under board E's breaker trip (6.364 A) pushes amperes through it continuously.
  - That source can be a 24 V vehicle charging at 27 to 29 V, or the solar tracker's drafted ceiling of 28.28 to 30.15 V.
  - At the trip the clamp sits near 28.19 V and carries 179.4 W, 28 times its 6.5 W on an infinite heat sink. At 1 A it still
    carries 27.1 W. The maker prints "Typical failure mode is short from over-specified voltage or current".
- **An independent over-voltage trip: SELECTED (SESSION).**
  - A trip through U34's restart latch alone would not remove VIN_RAW. With Q2 shorted it would leave the latch's bleed (121 to
    134 Ohm) across a bus the solar source holds at up to 30 V, about 7.5 W in four 1 W parts.
  - The trip therefore cuts VIN_RAW itself at board A's entry, which removes the vehicle and the solar source together.

**The circuit drawn** (board A; designators after board A's power drafts and l8gnd's):

| Ref | Part, value | Nets | Basis |
|---|---|---|---|
| Q41 | CSD19532Q5B (C473333; PowerPAK land, board A's own 100 V FET) | drain VIN_RAW_IN, source VIN_RAW, gate VCO_GATE | in series at board A's VIN_RAW entry; off, it blocks forward |
| U45 | TPS48110AQDGXRQ1 (C17556513; land `meshsat:TI_DGX0019A_VSSOP-19_3x5.1mm_P0.5mm`, the land L4-E11's E11-01 owes) | VS on VIN_RAW_IN behind R245 100 R and C244 100 nF 100 V; SRC on VIN_RAW; PD on the gate | TI SLUSEE5E: VS 3.5 to 80 V (100 V absolute); the controller L4-E11 selected for board E's entry |
| R241, R242 | 200 k and 10.0 k, 0.1 % | OV on VBUS20 | V(OVR) 1.16 to 1.20 V, V(OVF) 1.10 to 1.13 V, I(OV) at most 300 nA: **cut at 24.25 to 25.31 V of VBUS20, back under 23.00 to 23.84 V**; OV to PD 2.6 to 4 us (tPD(OV_OFF)) |
| R239, R240 | 33.2 k, 10.0 k (1 %) | EN/UVLO on VIN_RAW_IN | V(UVLOR) 1.16 to 1.20 V: on at 4.93 to 5.26 V, under U34's 8.08 V UV |
| R243, R244 | 100 k, 39 k | INP | L4-E11's divider: high from 7.23 V, 18.1 V at the 64.5 V clamp, under the pin's 20 V |
| R246, R247, C245 | 36.5 k, 10 R, 10 nF C0G 100 V (C184799) | gate slew | L4-E11's network (17.3 to 24.7 V/ms) |
| C246 | 1 uF 25 V X7R | BST to SRC | Equation 4, as L4-E11 |
| (U45 pins) | IWRN, TMR, IMON, DIODE to GND; ISCP, CS+, CS- on VS | | over-current, short circuit and remote temperature unused: SLUSEE5E Table 5-1 ("Connect IWRN to GND", "Connect TMR to GND to disable", "Connect ISCP to CS-"); CS+ and CS- on VS with no shunt: INFERRED |

**What it protects, with its margins** (`l8r2_drafts.out` section 3):
- The cut sits 0.85 V over the bus's in-service bound of 23.40 V (s120, INFERRED), so it never trips in service. It sits 0.69 V
  under U3's recommended 26 V and ACOV's 26.0 V.
- With Q2 shorted, VIN_RAW's 32 uF dumps into the bank (1.267 mF at -20 %) with L1 at board E's 13.87 A, and the bus reaches at
  most **25.85 V**.
- With FB open, U2 pumps VIN_RAW's 32 uF down to U34's 8.08 V UV, and L1 adds s120's 12.57 mJ, so the bus reaches at most
  **26.49 V**.
- So U3 stays 5.51 V under its absolute 32 V, and Q7 stays 2.51 V under its 30 V (with Q8's 1.0 V). U3 goes at most 0.49 V over its
  recommended 26 V, for the event, in the open-FB fault only. (INFERRED; the bank's ceramics are not counted.)
- U34's UV then engages the bleed with no source behind it, so it drains only capacitors.
- With Q2 shorted, a re-close after the bus falls under 23.00 to 23.84 V meets board E's breaker, whose limits bound the pulse;
  **Q41's SOA under those retries is owed to Layer 9** (F2-04).

**The acceptance.** The regenerated board A netlist shows J_VR1 to J_VR4 on `VIN_RAW_IN`; Q41's drain on `VIN_RAW_IN`, its source
on `VIN_RAW` and its gate on `VCO_GATE`; U45's OV on `VCO_OV` from R241 on VBUS20; its SRC on `VIN_RAW`; and ISCP with CS-
(`check_l8r2_netlist.py` VCO: NOT DRAWN today). **Bench row (Layer 9):**
- VBUS20 driven through R241 at its divider: the cut between 24.25 and 25.31 V, the release between 23.00 and 23.84 V;
- Q2's fault simulated by a link across Q2 with a current-limited 36 V source: the bus at or under 26.0 V;
- FB's open simulated by lifting R6, with U2 running: the bus at or under 26.5 V and U3's VBUS at or under 26.5 V.

**Contract texts (Layer 5).**
- IF-AE-DOCK `vin_raw`: "board A's dock pins J_VR1..4 carry VIN_RAW_IN (the alias of board E's VIN_RAW); board A cuts it at Q41
  when VBUS20 passes 24.25 to 25.31 V (S-111)". `check_contracts.py` and `block_contract.py` need the alias VIN_RAW_IN / VIN_RAW
  (F2-03).
- HW-FW-CONTRACT: "a VBUS20 over-voltage cut is a hardware event: the charger reads VBUS low and the front end restarts through
  U34's guard; firmware logs a VBUS20 collapse with VIN present as a front-end fault".

## 3. Item 3: Layer 5's round 2 circuit findings (`inputs/l5r2-findings-and-rows-6902db8f.md`)

### 3a. L5R2-F03: PANEL_5V over the ribbon's 1 A conductors (board B)

**The defect as found.** PANEL_5V reaches board C on two conductors of the panel ribbon. The Wurth WR-CAB 63912615521CAB cable and
the WR-BHD 61202623021 sockets each print 1 A at most per conductor and contact (MAKER). Its only limit is F1, an MF-MSMF110-2 that
holds 1.10 A and trips at 2.20 A at 23 C, so a fault drawing up to 2.2 A puts up to 1.10 A on each conductor. The brief named board
A or C; the limiter is on board B (`gen_sch_b.py`'s F1, from +5V_DEV), so the correction is on board B.

**The options.**
- F1 one step lower would trip under board C's 1.0 A declared peak once derated at the inside air.
- A per-conductor split needs a ribbon conductor, and the 26 are allocated.
- A different cable is a Layer 6 pick that leaves the 2.2 A band in place.

**SELECTED (SESSION): an eFuse ahead of F1.** U901, a TPS259631 (C2155778, the part board B fits as U23 and U24), from +5V_DEV to a
new net PANEL_5V_EF, then F1 to PANEL_5V. F1 stays as the backstop, its 2.2 A trip coordinated behind the eFuse.
- R901 604 Ohm gives **1.375 / 1.506 / 1.614 A** (Equation 7; the tolerance of the wider neighbouring printed row, INFERRED).
- So a conductor carries at most **0.807 A** with an equal split and **0.880 A** with a 20 % resistance mismatch (ASSUMPTION),
  under the 1 A. The lowest limit, 1.375 A, sits over board C's 1.0 A peak.
- The current limit responds in 87 us typical, a short circuit in 5 us (SLVSET8A 7.6).
- OVLO 42.2 k over 10 k: the pin sits at 0.961 to 0.993 V on 5.1 V and cuts at 6.01 to 6.47 V. The helper's 100 k over 10 k would
  leave the pin at 0.46 V on 5 V, under SLVSET8A's 0.5 V recommended minimum: U23 and U24 carry that today (F2-06).
- EN goes to +5V_DEV through R905 100 k (note 2); FLT to +3V3_DEV.
- The draft re-keys `_DEV_LOADS` and `_GND_LOADS` from F1 to U901 and declares PANEL_5V_EF.

**Acceptance.** The netlist shows U901 between +5V_DEV and PANEL_5V_EF and F1 between PANEL_5V_EF and PANEL_5V (PNL: NOT DRAWN
today). Bench: a load stepped to a short on PANEL_5V at board C's end, with the current limited inside 1.375 to 1.614 A and each
conductor's current recorded.

**Contract text (Layer 5).** IF-BC-PANEL `protection`: "PANEL_5V behind board B's eFuse U901 (1.375 to 1.614 A) and the backstop F1
(MF-MSMF110-2); each of the two conductors at most 0.81 A (0.88 A with a 20 % mismatch), under the cable's and socket's 1 A".

### 3b. L5R2-F05: board A's +3V3 to board D with no branch limiter

**The defect as found.** Board A's +3V3 (U12, a 3 A TPS62933) reaches board D over one conductor of the mezzanine harness (J_MEZZ1
pin 13, 1 A at most) with no limiter. A second conductor (pin 16, AB_SPARE) would give 2 A, still under U12's limit.

**SELECTED (SESSION): an eFuse on the branch.** U44, a TPS259631 (board A's `efuse()` helper), from +3V3 to a new net +3V3_A2D on
J_MEZZ1 pin 13.
- R234 3.83 k is the **printed row, 0.224 / 0.247 / 0.269 A**: 2.2 times board D's 0.10 A declared peak, and 27 % of the
  conductor's 1 A at most.
- RON is at most 143.4 mOhm under 4 V, so the drop at the peak is 14.3 mV.
- OVLO 30.1 k over 10 k: the pin sits at 0.811 to 0.860 V and cuts at 4.62 to 4.97 V. EN goes to +3V3 through R238 100 k.
- The +3V3 rail's load row for J_MEZZ1 moves to U44.

**The branch's name (corrected 3 October 2026 after the bring-up author's finding).** The first issue of this draft named the new net +3V3_D8, which board D already uses for its OWN rail (`gen_sch_d.py`, made by D's U1; the committed board D netlist carries `/+3V3_D8`), so across the dock and the A-to-D harness one name would have denoted two rails and IF-AD-HARNESS's alias table could not say which. It is now **+3V3_A2D**, a name no committed netlist, generator, registry or draft of the tree uses (checked at `a441651a`); board D's side of pin 13 stays its +3V3, so the alias is +3V3_A2D / +3V3 and names one rail.

**Acceptance.** J_MEZZ1 pin 13 on +3V3_A2D behind U44 (D8V3: NOT DRAWN today). Bench: board D's 3.3 V shorted at the harness, with
the current inside 0.224 to 0.269 A and board A's +3V3 held.

**Contract text (Layer 5).** IF-AD-HARNESS pin 13: "+3V3_A2D (the alias of board D's +3V3) behind board A's eFuse U44, 0.224 to
0.269 A"; `check_contracts.py`'s alias table gains +3V3_A2D / +3V3.

### 3c. L5R2-F04: J_QMX's land (board B)

**The defect as found.** Board B's footprint table maps `PH1x4` to a 2.54 mm pin header, and J_QMX and J_CAM use it, while
ASSEMBLY.md section 4 ("QMX USB | B16 `J_QMX` (PH 1x4) | ... PH at B16"; "Camera | B16 `J_CAM` (PH 1x4) | ... PH both ends") and
IF-LID-HF name a JST PH 1x4. The same mismatch is recorded as HF-F04 for J_CAM.

**The evidence supports the land, not the texts.**
- Both texts name JST PH, and the leads are made to it.
- Boards A (J_USBW) and D (J_USB3) fit JST's B4B-PH-K-S for the same kind of USB lead (JST PH catalogue held).

**The correction drawn.** Board B's table gains `PH4` = `Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical` (board A's key),
and J_QMX and J_CAM take it with LCSC C131334. The pins and nets are unchanged.

**Acceptance.** J_QMX's and J_CAM's land is the JST PH (PH4: NOT DRAWN today). The contracts already say PH 1x4: no text changes.

## 3d. Item 4: board C's PI button reaches no controller pin (the panel firmware's F-01)

**The defect as found** (fnd/fw-panel at `42c27369`, `v2/firmware/panel/README.md` finding F-01, copied in
`inputs/fw-panel-F01-42c27369.md`). SW_PI's contacts (PIJ2_A, PIJ2_B) pass FB3 and FB4 to J_PIJ2's two lands (PIJ2_A2, PIJ2_B2) and
U11's clamps only: no RP2040 GPIO, no expander input, neither line on GND, no other board with a mating lead. All 30 GPIOs are used;
the expanders' port 1 spares are free.

**The decision: route it to the controller (SESSION), on the evidence.**
- PANEL.md section 5: "The PI button: short press = `PI_SHDN_REQ` (clean shutdown of every module), hold 8 s = `PI_KILL`. The MAIN PWR
  button is hardware to A22's power controller and the controller only sees its effect". HW-FW-CONTRACT FW-C03 says the same.
  Only the controller can tell a short press from an 8 s hold.
- ASSEMBLY.md's leads table (line 127): "PI button | SW_PI's contacts | C7 `J_PIJ2` lands (the panel controller reads it; nothing
  leaves the backer)". **ASSEMBLY.md is right.**
- The generator's own note (line 333: "PIJ2_A2 is the same part's open-drain INT output, held at +3V3 by R3 on board A") is the stale
  statement. No board carries that lead. Were it built, a press would pull PI_SHDN_REQ, which the controller reads as a MAIN tap
  (PANEL.md section 3, GPIO 18, and FW-A10: "it reads the pin as an input to see MAIN taps"), so the 8 s hold could not be told apart
  from MAIN. The LTC2954 path stays what PANEL.md says: MAIN alone, hardware to A22.
- The J_PIJ2 lands are kept (the switch's lead lands); only the stale note is corrected.

**The circuit drawn (`apply_gen_sch_c_pibtn.py`).**
- **The input:** PIJ2_A2 goes to U1 (PCA9555, 0x22) P1.3, pin 16, until now SPARE1. That is the inputs port, beside LIGHT_DAY_n and
  LIGHT_NIGHT_n. The bit is named **PI_BTN_n** (low = pressed).
- **The pull-up:** R57, 10 k (C25804) to +3V3.
- **The return:** PIJ2_B2 is tied to this board's GND (FB4 pin 2, C27, J_PIJ2 pin 2, U11's second channel), so a press pulls
  PIJ2_A2 low through FB3.
- **The debounce:** C27, the 100 nF already across the pair, now runs from PIJ2_A2 to GND. With R57 it gives **tau 1.00 ms**.
  - A release reaches VIH (2.31 V, 0.7 VCC, TI SCPS131J 6.3) after 1.20 ms.
  - A press pulls under VIL (0.99 V) through the contact, which carries 0.33 mA.
  - The board's other inputs use 10 k with 10 nF; the longer tau here suits a lead that passes the antenna feeds.
- **The interrupt:** the expander raises EXP_INT on the change (SCPS131J 8.4.1), the controller's GPIO24, which FW-C14 already
  services.
- **Kept and moved:** SPARE1's test point moves to PIJ2_A2, so the button keeps test access, and U11's clamp stays on the A line.

**The proof** (`l8r2_drafts.out` section 7b). Layer 6's `apply_gen_sch_c_lcsc.py`, the only other board C draft (fnd/l6r2 at
`7633ae0a`, copied in `inputs/` with the helper `l6r2_apply.py` it imports, run in a scratch git repository because the helper asks
git for its top level), and this draft give **the same generator in either order**. Layer 6's draft anchors on the layout's import
line and keys codes by designator and value, and touches none of these lines. Designators: this draft adds **R57**, Layer 6's adds
none; no literal designator is drawn twice.

**The acceptance.** The regenerated board C netlist shows U1 pin 16 on PIJ2_A2, R57 between PIJ2_A2 and +3V3, and C27, FB4 pin 2 and
J_PIJ2 pin 2 on GND (`check_l8r2_netlist.py` PIBTN: NOT DRAWN today, U1.16 on SPARE1). Bench (V-C03): a short press raises
PI_SHDN_REQ for at least 200 ms and the 8 s hold raises PI_KILL; U1 P1.3 reads 0 with the button held and 1 released, through EXP_INT.

**Texts for their owners (not edits).**
- **PANEL.md section 4, U1's port 1 row 3:** "PI_BTN_n: the PI button, low = pressed (PIJ2_A2; R57 10 k to +3V3, C27 100 nF to GND,
  tau 1.0 ms); raises EXP_INT on a change". The SPARE1 test point becomes the button's.
- **PANEL.md section 1, the switches row:** "`SW_PI` (16 mm, lead pads `PIJ2_A/B`, read by U1 P1.3)".
- **PANEL.md section 5:** add after the PI button's sentence "(read on U1 P1.3, PI_BTN_n, at every EXP_INT and the once-a-second
  poll)".
- **The firmware's hal.h:** the expander bit `U1 P1.3 = PI_BTN_n`, active low; `HAL_PI_BUTTON_WIRED` becomes 1 once the draft is
  released and board C regenerated.
- **The firmware's check:** "the PI button reaches no controller pin" is F-01's evidence and fails, as designed, on the regenerated
  netlist; replace it with the bit check against U1 pin 16.
- **ASSEMBLY.md line 127:** "(the panel controller reads it on U1 P1.3; nothing leaves the backer)". The row is already right in
  substance.
- **HW-FW-CONTRACT FW-C03:** "`C:J_PIJ2`" becomes "`C:U1` P1.3 (PI_BTN_n)".

## 3e. Item 5 (round 3): the pack path's return on boards A and E (record l9stk's finding)

**The finding as found.** Record l9stk at `7388a84b`, section 12, and its output's section 2 ("returns declared in the intents: board A
none; board E none"; both copied in `inputs/`). On boards A and E, GND carries the pack path's return:
- on board E, from the XT60's return pin J_BATT pin 1 to the 12 AWG return pad P_CN;
- on board A, from the four dock return contacts J_CN1 to J_CN4 to the stages that VBAT feeds.

Both boards declare GND only as a NODE ("the board's reference"). A node is judged by no power rule, so nothing solves the return's
copper, while every copper rule solves the forward half (CELL+ and CELL_F on E; CELL+, CELL_FUSED and VBAT on A). Record l9stk's
decision lays the pack path and its return as bands shared by both outer faces at 1 oz, 6.72 mm a face at the pack's 18 A.

**Drafted: GND declared as a rail on each board, in the generator's intent table** (`apply_gen_sch_a_packrtn.py`,
`apply_gen_sch_e_packrtn.py`, release-guarded like the other drafts). Each replaces the node declaration by a rail declaration of the
same net. The form is board B's (its GND has been a rail since 16 September 2026), with board P's `returns` (its PACK_N since 20
September 2026):

| | Board A | Board E |
|---|---|---|
| sources | J_CN1 to J_CN4, the dock return contacts | J_BATT, its pin 1 (the pack lead's return) |
| loads | the ground end of every load VBAT declares, at VBAT's figure: U4 2.0, U6 2.0, U12 0.2, U41 0.4, U21 0.69 and U22 0.65 A at their GND pins; the LM5176 stages at their CS shunts, through which their input current returns: R170 2.22 (S2, VBAT's Q28), R177 1.61 (the device rail, Q32), R56 1.5 (the PA, Q11), R122 0.3 A (HF, U15); 11.57 A | P_CN 10.0 A (the return pad to the dock block), the whole as the upper bound |
| typical, peak | 10.0, 18.0 A (the pack's) | 10.0, 18.0 A |
| returns | CELL+ (14.4 V) | CELL_F (14.4 V) |
| share | 0.5 %, the share the board's CELL+ declares | 0.5 % |
| volts | 0.0, as the node declared it | 0.0 |

**Why GND itself, and not a new net.** Board P's PACK_N is a net of its own because its shunt R10 separates it from the board's
ground. On A and E the return is the ground net, with no part in between, so a separate name would need a net tie: a netlist change
this record does not make for a declaration. Board B's GND rail is the precedent.
- `returns` makes dc_drop judge the drop against 14.4 V rather than the net's own 0 V, and keeps thermal.py from counting the loop's
  watts twice.
- check_contracts.py does not add GND's shares across boards, so the half percent is each board's own bar.
- A later draft that adds a VBAT load (L4-E11's U42, L4-E9's R227) does not add its return to board A's list. The copper at the dock
  contacts carries the whole either way, and the load can join the list in the same release.

**What intent.py says** (section 9). A fresh intent.py evaluates each board's declarations in the file's order (CELL+ or CELL_F
first). Each board's declaration is **accepted**, both alone and after the whole round of that board's drafts (board A's L4-E9 order
with l8gnd's and this record's drafts; board E's change list). Each source and load sits on GND in the committed netlist (board A:
J_CN1 to J_CN4 pin 1, U4 pins 7 and 9, R170 pin 2 and so on; board E: J_BATT pin 1, P_CN pin 1).

**The rules that then judge the return's copper** (pcb_rules.yaml):
- PI-001, conductor current capacity: dc_drop's density verdict at the declared 18 A, on the routed board;
- PI-002, the drop, judged against 0.5 % of 14.4 V (72.0 mV);
- PI-003, the barrels where the return changes layer (dc_drop's solved mesh, via_current.py);
- PWR-001, the rail's sources and loads on the regenerated netlist;
- THM-001, which counts no watts for it.

**Composition** (sections 5, 6b and 7). On board A it is OK at every step in L4-E9's order (packrtn after vbus20ov, mainpb last
still at R248 and C247), first in the order, and with each power draft alone after it. On board E it is OK after every prefix of the
change list's board E round (0 to 11 drafts), before it, and before d8dec31's cin. It shares no anchor with any draft and adds no
designator.

**Acceptance.** The regenerated intent files (`out/pcb-a-power-intent.json`, `out/pcb-e1-dock-intent.json`) carry GND under `rails`,
returning CELL+ and CELL_F; dc_drop reads GND's verdict on the routed boards (the box). No netlist changes: an intent declaration
draws nothing.

## 3f. Item 6 (round 3): the energy chain's board E texts at 1 oz (record l9stk's second finding)

**The finding as found.** `v2/ecad/tools/pcb_energy_chain.yaml` names 2 oz on board E in two stages:
- DOCK_ENTRY's conductor: "board E's 2 oz power bands to the dock block pads", basis "gen_pcb_e3.py bands; IPC-2221 at 2 oz";
- SHORE_INPUT's conductor: "board E's input bands at 2 oz".

Record l9stk decides board E at 1 oz outer, with the high-current conductors shared by both faces (its decision "(L9STK E)",
pending integration). The file's other 2 oz lines are board P's and E5's, which are 2 oz by owner ruling 7, and they stay.

**Drafted: `apply_energy_chain_e1oz.py`, for the integrator.** It rewrites the two conductors' `what` and `basis` to 1 oz on both
outer faces. Each basis gives the width its declared rating needs at 1 oz by decision 35's model (track_current.width_for_current,
10 K):
- DOCK_ENTRY's 25 A needs **12.26 mm on each of two 1 oz faces** (43.62 mm on one);
- SHORE_INPUT's 10 A needs **2.76 mm on each of two** (8.15 mm on one).

The ratings, every protective element and every other stage are unchanged. The script:
- refuses until the decision register carries l9stk's board E decision, ruled at 1 oz outer (a title carrying "(L9STK E)"), so the
  correction follows the decision and never comes before it;
- asserts each old text exactly once; when every new text is present and no old one is, it writes nothing and exits 0, so a second
  run is a no-op;
- re-parses the YAML and checks that every stage reads back identical except the two conductors' what and basis, which must read back
  as written; after a write it reads the file back and parses it again;
- takes `--chain` and `--registry` for copies; `--check`, the default, writes nothing.

**What section 10 shows.** On the tree's register the script refuses, because the register has no "(L9STK E)" decision yet. On a copy
of the register carrying one, it checks, writes, and a second run reports ALREADY CORRECTED. energy_chain.check reads the tree's chain
and the corrected copy as IDENTICAL: 0 fails, 0 coordination findings, 0 selection findings, 98 checks. After the correction, the only
lines naming 2 oz are board P's and E5's.

**The order for the integrator.** Run it after l9stk's `apply_decisions_l9stk.py` and `decisions_render.py`. It touches no pin line.

**What the 1 oz texts expose** (FINDINGS, section 10; laying the copper is not this record's job).
- **DOCK_ENTRY's bands are too narrow for the chain's coordination at 1 oz.** The chain's check 3 (energy_chain.py: the blade's
  rating at or below its conductor's) holds DOCK_ENTRY's 25 A only on bands of at least 12.26 mm on each of two 1 oz faces. Record
  l9stk's decided minimum, 6.72 mm on each of two, is sized at the path's 18 A, and by the same model it carries 18.00 A. The same
  holds on board A (BOARD_A_NODE, F1 25 A, whose text already reads 1 oz). This is F3-06.
- **Board E's input band carries less than its fuse at 1 oz.** gen_pcb_e3.py lays DC_HS as one B.Cu band (run 5.5 mm, leg 4.5 mm,
  read from the generator's rectangles). At 1 oz it carries 8.07 and 7.13 A (11.78 and 10.56 A at 2 oz), under SHORE_INPUT's F1 10 A.
  At 1 oz the band needs an F.Cu twin of at least 2.76 mm, or 8.15 mm on one face. This is F3-07.
- **Why the correction keeps the declared ratings.** It states the widths and keeps each rating as the coordination's requirement on
  the copper. It does not lower a rating to the copper as drawn, because that would turn a stage of BAT-002 and PWR-003 red on a board
  l9stk has not yet re-cut. That choice belongs to the energy chain's writer and l9stk's author (F3-06, F3-07).

## 3g. Item 7 (rounds 7 and 8): board B's ground return, its load basis, its capacity, and the dedicated return between boards A and B (the owner's review of 4 October 2026, RSM-01; the recheck V3)

Round 7 (4 October 2026 evening, task T5b) and round 8 (the same night), branch `fnd/l8r4` from set 29's candidate `aa76c894`.
Every figure is in `l8r2_gndret.out` (`l8r2_gndret.py` prints it; sections in brackets), with its label: PRINTED (a maker's limit
in a held sheet), DECLARED (a generator's or a record's declaration), MODEL (this record's arithmetic on labelled inputs),
INFERRED (from printed figures under a stated assumption), ASSUMPTION, BOUND. Case rows, cited by id and revision from
`inputs/coordinator-cases-2026-10-04-rev3.md`: **C-DEV rev 1** for the device rail, **C-ALLTX rev 3** for the state; the slots'
loads per state as record l9pwr prints them. The figures are the merged ones: Layer 9's budget and its round 3 drafts are read
from copies of `fnd/l9t5` at `841e6c7e` (record l9t5's finding L9T5-F05). Nothing is built, bought, powered or measured.

**Where this stands.** L8R2-F31 is **OPEN**. Round 7's return calculation was read by the collaborator's targeted recheck V3
(`checks/astra-check-t5-recheck-cx41.md`, filed as received): **NOT CONFIRMED**. It had sampled six contact cases and called
the largest a maximum; a permitted corner it left out puts 10.6375 A through `J_5V_IOC`'s ground pin on C-DEV rev 1 against the
contact's printed 10 A. Round 8 corrects the calculation (every vertex enumerated), drafts the correction of the circuit (a
dedicated ground return of three XT60 leads between the boards) and shows the recheck's closure criterion on it. **No
independent check has read round 8**, nothing is applied, and this is the first correction after the first negative check of
this path: it is not presented as closed.

**The owner's words.** Round 7: "Reconcile the load and current-capacity basis; do not simply increase the declaration to make
the generator pass." Round 8: "verify the dedicated return across the permitted aged-contact combinations"; "Compare every
calculated current against the actual connector, contact, wire and ribbon ratings under the applicable conditions. Include the
required contact combinations and fault cases. Scratch figures are provisional."

### The declaration (round 7, L8R2-F30)

**The defect as found.** `gen_sch_b.py` declares its return with typed figures: 10.0 A typical, 21.0 A peak, four leads, a note
of "19.4 A with all four at their declared peak". 21.0 A was the sum of the four leads' peaks on 13 September
(5.0 + 5.0 + 5.0 + 6.0). Slot 2's lead went to 5.63 A on 28 September (S-98) and the line did not move. This record's
`apply_gen_sch_b_fans12.py` then put each cooler's step-up on its slot rail, and the generator stops.

**Reproduced [1].** Board B's drafts applied one by one in L4-E9's change-list order (steps 63 to 65: gnd002, fans12, rt500, with
this record's panel5v and ph4 between), the generator run as record l8p's `gen_netlist.py` runs it, every `intent.rail` call
recorded before intent judges it:

| stage | GND's loads | intent's limit (1.02 x 21.0 A) | the generator |
|---|---|---|---|
| as committed, and with gnd002 | 19.743 A | 21.42 A | runs to its end |
| + fans12 | 21.513 A | 21.42 A | STOPS: "rail GND declares a 21.00 A peak and its loads sum to 21.51 A" |
| + panel5v, + ph4, + rt500 | 21.513 A | 21.42 A | stops, the same line |
| + Layer 9's I-03 draft (the copy at `841e6c7e`) | 21.513 A | 21.42 A | stops, the same line |

fans12 alone moves the sum, by +1.770 A (on each slot the fan header's 0.100 A leaves and the step-up's 0.690 A enters);
Layer 9's draft moves it by 0.000 A. Rounds 1 to 6 never saw the stop: their composition proof read generator text and did not
run the generator.

**The load basis [2].** `_GND_LOADS` is the union of the arriving 5 V rails' own allocations; no ampere is in it twice (the
cooler branch is counted once, as the step-up's 5 V input) and none returns elsewhere. One return was missing: the PoE port's
0.60 A, which enters GND at the sense resistor R12 and leaves on `J_54V` pin 2. The three figures the declaration could hold:

| | figure | value | label |
|---|---|---|---|
| (i) | the sum of the leads' declared peaks | 26.40 A composed; **27.9108 A** with Layer 9's round 3 draft (3 x 6.6 + 6.0359 + 1.4749 + 0.6); 22.23 A on the committed generator | DECLARED, an **UPPER BOUND** (every lead at its own peak at once) |
| (ii) | the largest state of Layer 9's budget | PS-BUSY: 14.465 A at PLAN, 21.944 A at HIGH, 22.832 A at HIGH at the least load voltage; with Layer 9's draft 22.8711 A, 26.166 A with every cooler start at once. C-DEV rev 1 (PS-ALLTX, HIGH, the least load voltage) with the draft: 20.9888 A | MODEL (record l9pwr 5b, record l9t5) |
| (iii) | what board A's stages can deliver | each LM5176 5.1 V stage's loop limits between 7.0957 and 9.5960 A: 38.38 A for the four leads, 43.53 A with U601, 44.13 A with the PoE lead | PRINTED VSNS over the DECLARED shunt: a fault bound |

The peak holds (i), named an upper bound in its note; the typical holds the sum of the leads' typicals (13.30 A); the loads
stay the union with the PoE return added (22.113 A). (i) is the only figure true by construction, and typed it went stale
twice. (ii) is inside it with Layer 9's draft, like for like on the 5 V leads (26.166 A against 27.3108 A); without that draft
it is over by 0.327 A, which is I-03 itself (Layer 9's). (iii) is a fault current, which `intent.py`'s own rule puts in a note.

**The drafts of round 7 [5].** `apply_gen_sch_b_gndret.py`: the head of the GND rail call becomes a helper `_gnd_return`
that sums the typical and peak currents of every rail arriving on one of the return's lead connectors, adds `J_54V` and the
PoE return at R12, and stops the generator if a lead connector carries no arriving rail or two.
`apply_gen_sch_b_fandec.py` (**L8R2-F32**, the second stop found behind the first): fans12 declares its two TPS61089
capacitors' class at the call, and board B's decision 42 block reads classes from its own table `_dec_rule`; one row hands the
entry's own class to the block. fans12 is left byte for byte (record l7pwr pins its sha256 and record l4e9 holds its bytes).
The declaration was not raised to make the generator pass: the same draft on the committed generator gives 22.23 A, and a lead
declared lower lowers it.

### The return path as drawn (L8R2-F31), the worst case found

**The conductors [3a].** Both committed netlists: the two boards' grounds are one net joined by **five lead contacts**
(`J_5V_S1`, `J_5V_S2`, `J_5V_S3`, `J_5V_DEV`, `J_54V`, pin 2 each; six with Layer 9's `J_5V_IOC`) and **seventeen ribbon
conductors** (`J_AB1` pins 3 to 8 and 22 to 24, `J_AB2` pins 3 to 10), in parallel. Nothing makes a lead's pin 2 carry its own
rail's current: the return divides by resistance.

**The makers' printed figures [3b].**

| part | PRINTED | not printed |
|---|---|---|
| JST VH (catalogue, revision not printed) | 10 A "when using AWG #16 with the standard type header"; 7 A with AWG 18 on the shrouded header only; range to +105 C including the rise; contact resistance 10 mOhm maximum initial, 20 mOhm after test; "Do not branch in parallel current which exceeds the rated current ... design the circuits without causing any imbalance and provide extra margin for each circuit" | a minimum contact resistance; the ambient of the rating; a derating curve; a rating for AWG 18 on the fitted standard header |
| Wurth WR-CAB ribbon, WR-BHD IDC socket | 1 A a conductor at 25 C ambient, "the current rating may decrease due to the derating effect at higher temperatures", operating to +105 C, "the operating temperature is comprised of ambient temperature and temperature rise"; 237 Ohm/km maximum; socket 1 A, 20 mOhm maximum | a minimum; a derating curve |
| Amass XT60 (XT60-F and XT60-M; the pack connector's make). V1.2, held: 30 A, 60 A momentary, 0.55 mOhm, 12 AWG, 1000 uses, -20 to 120 C. 2021V1, filed this round (`v2/vendor/battery/amass-xt60-spec-2021v1-lcsc-c98733.pdf`): 35 A MAX with 12 AWG at a rise under 85 C, contact resistance at most 1.0 mOhm, 100 times, the same range | as stated | a contact resistance after test; a minimum; a derating curve |

The rows take the lower XT60 current (30 A), the higher contact resistance (1.0 mOhm, a printed limit taken as the contact's
maximum over its printed life: INFERRED) and the shorter life. Where no derating curve is printed, each row carries beside
the PRINTED rating the **least rating consistent with the sheet at the inside air** (INFERRED: the part may add the range's
top less the air; heating as the current squared, ASSUMPTION): the ribbon at least 0.5995 A at 76.25 C; the XT60 at least
25.11 A; the VH at least 5.995 A if its rating is taken at 25 C (ASSUMPTION; 9.789 A on round 7's 30 K rise).

**The copper's temperature, both ends [3b].** 76.25 C, the inside air in E5's dwell (L4-E12, MODELED), and -20 C, the
envelope's cold end in use. A conductor's largest share falls as the copper warms and the ground shift rises, so each
maximum is at one end and both are enumerated.

**The calculation, corrected [3d, 3e] (L8R2-F38).** For this network of parallel contacts and conductors the extreme of any
one conductor's current lies at a vertex of the box of contact resistances (each contact at 0, no minimum being printed, or
at its after-test or printed maximum). `enumerate_vertices()` visits every vertex for every conductor (4^23 raw vertices as
drawn, 10773 distinct states once interchangeable conductors are counted together) and `extremes()` refuses unless the
largest lands on the vertex the monotone argument names: the conductor's own two contacts low, every other contact high.

| total | copper | a 5 V lead's pin 2 (printed 10 A) | `J_54V`'s pin 2 (no printed rating) | a ribbon conductor (printed 1 A) | ground shift |
|---|---|---|---|---|---|
| 20.9888 A, C-DEV rev 1 | 76.25 C | **10.6376 A** | 8.5041 A | **2.0747 A** | 51.24 mV |
| | -20 C | **12.0918 A** | 9.9501 A | **2.6716 A** | 46.96 mV |
| 22.8711 A, the largest state | 76.25 C | **11.5916 A** | 9.2668 A | **2.2607 A** | 55.84 mV |
| | -20 C | **13.1762 A** | 10.8424 A | **2.9112 A** | 51.17 mV |
| 27.9108 A, the declared upper bound | 76.25 C | **14.1458 A** | 11.3087 A | **2.7589 A** | 68.14 mV |
| | -20 C | **16.0796 A** | 13.2316 A | **3.5526 A** | 62.45 mV |

The recheck's corner is reproduced: 10.6376 A (V3: 10.6375 A) on C-DEV rev 1 and 14.1458 A (V3: 14.1458 A) at the upper bound.
**As drawn the return does not hold, on C-DEV rev 1 already.** Round 7's six sampled cases read 9.4036 A for a lead and 1.0364 A
for a ribbon conductor there: they had no vertex with one lead low against peers at the after-test maximum, and none with one
ribbon conductor low against every other contact high. Round 7's division table, its thresholds and its comparison of
corrections are **WITHDRAWN**, and with them Layer 9's acceptance of `J_5V_IOC`'s pin 2 on those rows.

### The correction drafted (round 8)

**The approaches compared [3j]** (every row a maximum over every vertex, both copper ends, the three totals; `J_54V`'s lead at
AWG 16 in each, so that its pin 2 has a printed rating):

| | approach | a VH pin 2 | a ribbon conductor | an XT60 contact | every row on the printed ratings / on the least ratings | |
|---|---|---|---|---|---|---|
| D1 | a dedicated ground return of n conductors, two a lead (an Amass XT60 pair with both contacts on GND, two 12 AWG conductors of 150 mm): 2 (one lead) | 9.163 A | 1.403 A | 18.110 A | no / no | |
| | 4 (two leads) | 6.408 A | 0.874 A | 13.711 A | yes / no | the least that hold the printed ratings |
| | **6 (three leads)** | 4.927 A | 0.635 A | 11.031 A | yes / yes | **SELECTED** |
| | 8 (four leads) | 4.002 A | 0.499 A | 9.228 A | yes / yes | |
| D2 | one return lead and 1 Ohm in series with each ribbon ground conductor | 10.963 A | 0.033 A | 20.640 A | no / no | REJECTED |
| D3 | one return lead as the only return (the VH leads' pin 2 off the ground, the ribbons ballasted) | none | 0.039 A | 22.190 A | yes / yes | REJECTED: every rail's return leaves its supply lead, and one open lead puts the whole return on the ribbons |

Three leads are the least that hold every row both on the printed ratings and, at the inside air, on the least rating
consistent with each sheet; two hold the printed ratings only. More VH contacts (round 7's A0) are not revisited: the lead
contacts' 20 mOhm after-test limit is what makes them unable to carry the return.

**What is drawn [5].** `apply_gen_sch_b_gndrtn.py` and `apply_gen_sch_a_gndrtn.py`: on each board three sockets `J_GR1` to
`J_GR3`, Amass **XT60-F**, pins 1 and 2 both on GND. Female on the boards and male on the leads: the pack lead carries an
XT60-F for board E's `J_BATT` (XT60-M), so it cannot enter a return socket, and a return lead cannot enter `J_BATT`. On board B
the helper `_gnd_return` names the three sockets beside the leads as the places the return leaves the board (the peak, the
typical and the loads are unchanged); the draft requires `gndret` first and refuses otherwise. On board A the sockets sit in
their own schematic block; board A's GND declaration is not changed (L8R2-F33). The land is KiCad's
`Connector_AMASS:AMASS_XT60-F_1x02_P7.20mm_Vertical`, NOT READ on this host; no LCSC code is carried (L8R2-F40).

**Composition, netlists, mutations [5].** Board B in four orders with Layer 9's draft and Layer 6's three: one generator byte
for byte, 1479 parts, none unplaced, GND 13.30 A typical and 27.9108 A peak. Board A in L4-E9's order (the power drafts,
record l8gnd's two, this record's five of rounds 1 to 6, record l8p's ptc, L4-E11's dd7, Layer 9's draft, mainpb last, Layer
6's table) with the return draft last or first: 792 parts, none unplaced, one netlist. `check_gndret_netlist.py` reads the
declaration DRAWN on board B and the dedicated return DRAWN on both boards (NOT DRAWN and NOT DRAWN on the committed boards);
the same netlists read DRAWN under `check_l8r2_netlist.py` (boards A and B) and record l8gnd's `check_gnd002_netlist.py`.
Thirteen mutations each stop the generator or fail a check: round 7's eight, and **the return removed** (the dedicated return
NOT DRAWN, and the acceptance on that census fails: 16.080 A and 3.553 A), **the return landed on the wrong net** (`J_GR2`'s
pin 1 on +5V_DEV: FAIL), **one termination dropped** (`J_GR3` absent on board B: FAIL; a pin of `J_GR1` absent on board A:
FAIL), and a socket the declaration does not name (FAIL). The netlists are the generators' own part tables, no KiCad: the
box's export is the reading of record.

### The acceptance (the recheck's closure criterion) [6]

The census is read on the composed netlists of both boards, not assumed: six lead contacts, seventeen ribbon conductors, three
return sockets whole on both boards, six return conductors. Every row below is a branch at its worst vertex (its own two
contacts at 0, every other contact at its maximum: VH 20 mOhm after test, IDC 20 mOhm, XT60 1.0 mOhm), found by enumeration.

| branch | rating and its condition | total | at 76.25 C | at -20 C | least at 76.25 C | verdict |
|---|---|---|---|---|---|---|
| each 5 V lead's pin 2 (`J_5V_S1`, `S2`, `S3`, `DEV`, `IOC`) | PRINTED 10 A, JST VH with AWG 16 on the standard header (the fitted B2P-VH, the leads' gauge); no ambient and no derating printed | C-DEV rev 1 | 2.9578 A | 3.7056 A | 5.9948 A | HOLDS |
| | | the upper bound | 3.9333 A | 4.9277 A | | HOLDS |
| each ribbon conductor (`J_AB1` x9, `J_AB2` x8) | PRINTED 1 A a conductor at 25 C ambient; a derating stated, no curve | C-DEV rev 1 | 0.3671 A | 0.4776 A | 0.5995 A | HOLDS |
| | | the upper bound | 0.4882 A | 0.6352 A | | HOLDS |
| each XT60 contact of the return and its 12 AWG conductor (`J_GR1` to `J_GR3`, two each) | PRINTED 30 A (V1.2, no condition) and 35 A MAX with 12 AWG at a rise under 85 C (2021V1); range -20 to 120 C; no derating curve; no wire sheet held | C-DEV rev 1 | 6.9915 A | 8.2964 A | 25.1101 A | HOLDS |
| | | the upper bound | 9.2972 A | **11.0326 A** | | HOLDS |
| the PoE lead's pin 2 (`J_54V`) | **NO RATING PRINTED** for AWG 18 on the standard header (7 A for the shrouded header, a comparator) | C-DEV rev 1 | 2.0611 A | 2.6152 A | none | not covered |
| | | the upper bound | 2.7408 A | 3.4777 A | | not covered |

The largest state of Layer 9's budget (22.8711 A) sits between the two totals in every row. The ground shift is at most
11.43 mV (68.14 mV as drawn) against the 0.9418 V the LDOs' input allows (the smaller of record l9t5's 0.960 V and the
recheck's 0.9418 V). `J_54V`'s pin 2 is covered only with its lead at AWG 16 (6e: it is then one more VH contact of the 5 V
leads' make, at most 4.9269 A against the printed 10 A, and no row is left without a printed rating); that is a harness row
for Layer 7, part of this correction.

**What the rows rest on that no maker prints [6d].**

- The XT60's contact resistance after ageing. Amass prints one limit, 1.0 mOhm, with a 100-cycle life and no separate
  after-test figure. Every row still holds on the printed ratings while each XT60 contact stays at or under 2.06 mOhm, and on
  the least ratings at or under 1.43 mOhm. A four-wire reading of the return leads at assembly and in service would show it.
- The contacts' minimum resistance: none is printed, so every row takes the branch's own contacts at 0.
- The derating at the inside air: none is printed; the least ratings are INFERRED, and the VH's rests on a 25 C ASSUMPTION.
- The wires' own resistance: MODEL figures from nominal sections and lengths (no wire part is named), and the ribbon's is its
  maker's maximum. With each branch's own wire at 0.82 of its figure (ASSUMPTION) the maxima are 5.7851 A, 0.7708 A and
  12.3801 A, and every row still holds.
- The lengths: the return leads at 150 mm and `J_AB2`'s ribbon at 80 mm are ASSUMPTIONS until Layer 7 routes them.

**The fault cases [6g]** (maxima over every vertex at both copper ends; the figures are those at the declared upper bound, 27.9108 A, unless a total is named; the verdict covers C-DEV rev 1 and the upper bound):

| case | a VH pin 2 | `J_54V` | a ribbon conductor | an XT60 contact | inside the printed / the least ratings | what protects or reveals it |
|---|---|---|---|---|---|---|
| F-1 one return lead absent or open (four conductors left) | 6.4094 A | 4.6107 A | 0.8746 A | 13.7130 A | yes / no at the upper bound (yes on C-DEV rev 1) | nothing interrupts, nothing signals: **LATENT** |
| F-2 one XT60 contact of one lead open (five left) | 5.5717 A | 3.9649 A | 0.7359 A | 12.2276 A | yes / yes | LATENT |
| F-3 one 5 V lead's pin 2 open | 4.9642 A | 3.5052 A | 0.6408 A | 11.1016 A | yes / yes | the rail works: LATENT |
| F-4a one 5.1 V stage in its current limit beside the largest state (25.1511 A) | 4.4404 A | 3.1339 A | 0.5724 A | 9.9417 A | yes / yes | the stage's own loop bounds it; its INA226 shows it; firmware's action is Layer 5's rule, not re-read |
| F-4b every source at its bound at once (44.1338 A) | 7.7919 A | 5.4992 A | **1.0044 A** | 17.4452 A | **no** / no | a four-fault bound: a ribbon conductor 0.44 % over its printed 1 A at -20 C; a fourth lead would read 0.7885 A; not drafted |
| F-5 every return lead absent (the board as drawn today) | 16.0796 A | 13.2316 A | 3.5526 A | none | **no** / no | LATENT; the state the correction removes |

Tolerated inside every printed rating: F-1, F-2, F-3, F-4a. Not tolerated: F-4b, F-5. Latent: F-1, F-2, F-3, F-5. The design
makes F-1 to F-3 harmless inside the printed ratings; it does not make them visible (L8R2-F39).

**The supply pins [3f]** carry their own rail and nothing else, against the printed 10 A: 5.4340 A on slots 1 and 3, 4.6480 A
on slot 2, 6.0359 A on `J_5V_DEV` with Layer 9's draft, 1.4749 A on `J_5V_IOC`. On the severest reading of JST's sheet (the
rating at 25 C, ASSUMPTION: at least 5.9948 A at 76.25 C) `J_5V_DEV`'s pin 1 is 0.0411 A over; it is inside the printed
rating (L8R2-F43, for Layer 9 and Layer 5).

**The ground copper where the return enters [6f]** (decision 35's function, 10 K, inner 0.5 oz; a layout constraint,
L8R2-F33): 69.41 mm of plane for an XT60 contact's 11.033 A, 15.87 mm for a VH pin 2's 4.928 A, shared by board B's three
ground planes or board A's two. Four 0.5 mm thermal-relief spokes a plane give 6.0 mm (B) and 4.0 mm (A): the return sockets'
and the VH leads' pin 2 lands join their planes solidly, or with spokes of the row's width.

**Credit, by the three criteria of the coordinator's brief**, for round 8's two drafts: (a) they compose in L4-E9's order on
both boards and the generators run: yes; (b) the changed nets are read on the regenerated netlists with mutations that fail:
yes; (c) electrical acceptance on the makers' printed figures: every branch with a printed rating is inside it at every
vertex, on the conditions of 6d, with `J_54V`'s pin unrated until its lead is AWG 16. **NOT CLOSED: L8R2-F31 stays OPEN until an
independent check has read the changed design.**

**What the independent check should read:** (1) `enumerate_vertices()`, `analytic()` and `extremes()` against its own
arithmetic for one corner; (2) `box()`: each contact's low and high end against the makers' sheets, the XT60's two
specifications above all; (3) the census of 6a on the regenerated netlists; (4) each row of 6b against its rating and
condition, and 6d's dependences; (5) the two return drafts and their land (NOT READ on this host); (6) the fault table 6g,
and whether three latent faults without a detect line are acceptable.

### Decisions, row texts, questions, findings

**The session's decisions** (authority: SESSION under the owner's standing rule of 26 September 2026; each reversible):

| id | decision | reason | to reverse |
|---|---|---|---|
| L8R2-D7-1 | the return's peak holds (i), the sum of the leads' declared peaks, derived in the generator | the only figure true by construction; typed, it went stale twice | declare a typed state figure and take the staleness back |
| L8R2-D7-2 | the PoE return is a load at R12 and `J_54V` a source | its pin 2 is on GND on both boards | drop the helper's two lines (the check then FAILS, by design) |
| L8R2-D7-3 | `_dec_rule` reads a TPS61089 entry's own class and clause | fans12 is pinned by other records | move the clauses into `_dec_rule` in a new fans12 |
| L8R2-D8-1 | the worst case is found by enumerating every vertex of the contact-resistance box, at both ends of the copper's temperature (-20 C and 76.25 C) | the recheck's blocker; a maximum over the box lies at a vertex; the largest share is at the cold end, the largest shift at the hot | none: a sampled list is what failed |
| L8R2-D8-2 | the dedicated return is XT60 leads, XT60-F on the boards | the pack connector's make, two Amass specifications held, a printed contact resistance limit in the right range; female sockets keep the pack lead out | another family whose maker prints an after-test resistance under about 1.4 mOhm a contact |
| L8R2-D8-3 | three leads (`N_RETURN` 3 in both drafts) | the least that hold every row on the least ratings at the inside air; two hold the printed ratings only; one lead out stays inside the printed ratings | `N_RETURN` 2 and regenerate: section 6 then says what no longer holds |
| L8R2-D8-4 | the XT60 box: 0 to 1.0 mOhm; rating 30 A; at the inside air at least 25.11 A | the higher printed resistance, the lower printed current, the 2021V1 rise criterion | edit `box()` and `rating()` |
| L8R2-D8-5 | the least rating consistent with a sheet stands beside each printed rating where no derating is printed; `T_RATING_REF` 25 C for the VH | a printed rating at an unprinted ambient is not a rating at 76.25 C | edit `least_rating()` |
| L8R2-D8-6 | `J_54V`'s lead at AWG 16 is part of the correction (a harness row, not a generator change) | its pin 2 has no printed rating at AWG 18 and stays in the return | keep AWG 18 and carry the row as not covered |
| L8R2-D8-7 | one budget is read, the copy of Layer 9's at `841e6c7e` | the merged figures; the output no longer moves with the tree's own copy at a merge | read the tree's file again |
| L8R2-D8-8 | the return leads at 150 mm, `J_AB2`'s ribbon at 80 mm, `WIRE_FLOOR` 0.82 | no held document gives them; each is labelled ASSUMPTION | edit the constant and regenerate |

Round 7's L8R2-D7-4 (a dedicated return as the direction, with its 0.53 mOhm figure) and L8R2-D7-5's ribbon share are
superseded by L8R2-D8-2 to D8-5; their figures came from the sampled calculation and are WITHDRAWN.

**Row texts proposed for Layer 7** (ASSEMBLY.md section 4; its file is its own): "Ground return, 3 x | A22 `J_GR1..3` (XT60-F)
| B16 `J_GR1..3` (XT60-F) | 2 x 12 AWG, 150 mm, both conductors ground | XT60-M both ends; marked as ground leads (never the
pack lead)"; "PoE feed (54 V) ... 16 AWG, 150 mm" in place of 18 AWG; the wire part and insulation class of every A to B lead.

**Row texts proposed for Layer 5** (its files are its own): IF-AB-POWER gains `ends` J_GR1..3 on both boards (Amass XT60-F,
both contacts GND), `harness` the three return leads, and a field `return`: "the 5 V and PoE returns share one ground: six VH
pin 2 contacts, seventeen ribbon ground conductors and six conductors of the dedicated return in parallel, divided by
resistance; maxima over every vertex of the contact resistances (record l8r2 round 8): a VH pin 2 4.93 A, a ribbon conductor
0.64 A, an XT60 contact 11.03 A at the declared upper bound 27.9108 A; L8R2-F31 OPEN until an independent check"; `tbd`: "an
absent or open return lead is latent (L8R2-F39)". IF-AB-RIBBON and IF-AB-WALL `current`: "the ground conductors carry a
share of the supply return, at most 0.64 A a conductor with the dedicated return, 2.67 A without it on C-DEV rev 1".

**Questions drafted for the makers (UNSENT; nothing was sent to anyone):**

- Q-JST-VH-1: for the VH series with SVH-41T-P1.1 contacts and AWG 16 on the B2P-VH header, the ambient temperature and the
  temperature rise at which the 10 A rating is stated, a derating curve to +105 C, the typical and the minimum contact
  resistance, and whether the 20 mOhm after-test figure is a limit over the product's life.
- Q-AMASS-XT60-1: for XT60-F and XT60-M with 12 AWG, the contact resistance at the end of the stated mating life and after
  the salt-spray item, the rise at 30 A and at 35 A, a derating curve to 120 C, and which of the two specifications (V1.2:
  30 A, 0.55 mOhm, 1000 uses; 2021V1: 35 A MAX, at most 1.0 mOhm, 100 times) governs parts bought today.
- Q-WE-CAB-1: for WR-CAB 63912615521CAB on WR-BHD sockets, the derating of the 1 A rating above 25 C, and the minimum
  conductor resistance.

**Findings of rounds 7 and 8.**

| id | state | what | owner |
|---|---|---|---|
| L8R2-F30 | CORRECTED BY DRAFT, not applied, unchecked | the typed, stale GND declaration | the integrator (release with R-190) |
| L8R2-F31 | **OPEN**, a known defect; correction DRAFTED in round 8, unchecked | the A to B return divided over VH contacts and signal ribbons with nothing setting its division; as drawn 12.092 A in a lead's pin 2 and 2.672 A in a ribbon conductor on C-DEV rev 1 | boards A and B, Layers 5 and 7; an independent check next |
| L8R2-F32 | CORRECTED BY DRAFT, not applied, unchecked | fans12's TPS61089 capacitors had no class board B's block reads | the integrator (with fans12) |
| L8R2-F33 | OPEN, a layout constraint | the return sockets' and the VH leads' pin 2 lands join their ground planes solidly (6f's widths); board A's intent cannot express the 5 V returns' loop | Layer 9 (layout constraints, record l9stk) |
| L8R2-F34 | OWED | the leads' wire parts and insulation classes; `J_54V`'s lead at AWG 16; the three return leads' row | Layer 7 |
| L8R2-F35 | ANSWERED by Layer 9's round 3 | its acceptance of `J_5V_IOC`'s pin 2 on round 7's sampled rows is WITHDRAWN with them and now rests on this correction | Layer 9's author |
| L8R2-F36 | for L4-E9 | board B rows for fandec, gndret and gndrtn (gndrtn after gndret), a board A row for gndrtn, one release; a register row for L8R2-F31 | L4-E9's author |
| L8R2-F37 | MINOR | the return places +5V_HDMI's 0.20 A at U3 and U4; the rail declares J_HDMI | board B's generator owner |
| L8R2-F38 | CORRECTED (this record's own defect, found by the recheck V3) | round 7's return calculation sampled six cases and called the largest a maximum | this record |
| L8R2-F39 | OPEN | an absent or open return lead, an open XT60 contact and an open VH pin 2 are LATENT; next action: a four-wire bond reading between the boards' grounds in the assembly and service procedures, or a detect line (not drafted) | Layer 12, Layer 5 |
| L8R2-F40 | for Layers 6 and 7 | the XT60-F's land is NOT READ on this host and no LCSC code is carried; a return lead's free XT60-M end could be mated to the pack lead by hand: mark the leads | Layers 6 and 7 |
| L8R2-F41 | for Layer 5 | IF-AB-POWER gains the return leads and the return's division | Layer 5 |
| L8R2-F42 | NOTED | the XT60's printed range starts at -20 C, the envelope's cold end in use: no margin | Layer 6 |
| L8R2-F43 | for Layers 9 and 5 | on the severest reading of JST's sheet `J_5V_DEV`'s pin 1 (6.0359 A) is 0.0411 A over at the inside air; inside the printed 10 A; Q-JST-VH-1 would settle it | Layer 9's author |

**What these rounds could not do.** Have round 8 read by an independent check (L8R2-F31 stays OPEN until one has). Read the
corrections on a KiCad export, read the XT60-F's land, or run a copper rule on a routed board (the box's). State any
maker's rating at 76.25 C from a printed curve, or bound any contact resistance from below (no sheet prints either). Draft the
harness and contract rows into Layer 7's and Layer 5's files (their owners'), or a detect line for the latent faults. Send any
question to a maker.

## 3h. P0 round (5 October 2026, Slot A): the independent check V6's findings on the dedicated return (`l8r2_p0.py`, `l8r2_p0.out`)

The owner's P0 instruction of 5 October 2026 and its part 19 (a bounded provisional choice with the validation task where a figure
can only come from a layout, a measurement or a vendor) govern this section. L8R2-F31 stays OPEN in the sense V6 left it: CONFIRMED AS
CONDITIONAL on the model's figures, now with its conditions named and bounded. Nothing is built, bought, powered or measured.

| V6 item | Failure case | Disposition | Evidence (l8r2_p0.out) |
|---|---|---|---|
| V6-B1, the plane copper in series with the return bundle | a ribbon conductor over its printed 1 A once the boards' planes add resistance in series with the six return conductors | PROVISIONAL for the service cases: the named layout condition **L8R2-F33a**, each return socket's land within 17 mm (the largest steady state; 30 mm on C-DEV rev 1, 36 mm on C-DEV rev 2) of the 5 V entries on both boards at 0.5 oz, every ground plane joined solidly; the Layer 10 task, the routed boards' extraction against each case's bound. **STILL OPEN:** the declared upper bound's printed row (0.3543 mOhm, 5.9 mm at 0.5 oz, not realisable; a fourth lead 9.1 mm, not a correction; 1 oz inner 23 to 47 mm, the owner's open copper decision) and every least-rating row at the inside air | section 2: V6's 0.3543 / 0.7747 / 0.1436 / 0.4386 mOhm reproduced |
| V6-B2, the indirect ground paths | the census counted only the leads, the ribbons and the return | the census completed for the paths V6 named, each bounded at its own worst vertex with the monitor's 1.00 A and the QMX's 2.00 A added to the totals; the counted rows hold with the shares on the printed ratings; the RF pigtails' U.FL outer contacts carry up to 2.1053 A with no printed rating and the HDMI receptacle's sheet is not held: PROVISIONAL, vendor tasks UNSENT (Hirose, Molex) and Layer 7's cable rows; the design change if the U.FL answer is lower: break the DC path at board A's RF jacks | section 3 |
| V6-m12, F-4b | every source at its bound puts a ribbon at 1.00418 A against 1 A | SESSION decision (authority: SESSION; ruled_by Slot A; ruled_on 5 October 2026): the design need not serve the five-overload coincidence inside the ribbons' printed rating; reverse by carrying the fourth lead (0.7884 A there) | section 4 |
| V6-m8, the XT60 rows | no XT60 sheet rates a board-soldered end | the rows' 11.0311 A is judged against the printed 30 A as the wire-to-wire rating, a 63 % margin; the board end's rating MISSING, a vendor task to Amass UNSENT; PROVISIONAL with that margin | section 5 |
| C-DEV rev 2 (conditional on FW-B20/B21) | the supervisors' term bounded | U601 0.9607 A in place of 1.4749 A; U7's device-rail demand unchanged at 6.0359 A; C-DEV rev 2 tolerates 0.8244 mOhm; rev 1's figures stay beside it as the labelled scenario | section 1, 2 |

**L8R2-F33a (new, a named condition of 6d and 6b):** the plane resistance between the return sockets' lands and the 5 V entries (the
leads' pin 2 lands on board B, the 5 V stages' outputs on board A), both boards together, at most each case's bound in `l8r2_p0.out`
section 2; the geometry it rests on is the spreading model on record l9stk's stackups (board A two ground planes, board B three, 0.5 oz,
15 % thin) with the lands solidly joined at L8R2-F33's widths. It is a layout condition, PROVISIONAL until the routed boards' extraction.
**On the placement as drawn (the owner's amendment 1; `l8r2_p0.out` 2b):** the 5 V entries' ground lands read from the placed boards
(board A's four at y 34.45 mm, x 101.2 to 149.2 mm; board B's J_5V_DEV at (36.48, 51.65) and J_5V_S1 to S3 along y 194 mm, 211 mm
apart at most; J_5V_IOC not yet placed on either board) cannot be reached by the three sockets as one cluster (the smallest circle
holding board B's has radius 105.3 mm, board A's 24.0 mm, against 16.6 mm). One socket a group, the same lead serving the same group on
both boards, holds every entry within 8.0 mm of its socket: J_GR1 beside J_5V_S1, J_GR2 by J_5V_S2 and J_5V_S3, J_GR3 by J_5V_DEV with
J_5V_IOC placed beside it. That is the condition's form (SESSION decision L8R2-D9: realisable on the drawn floor plans by placing
only the new parts; the sites' free area and each lead's 150 mm reach are Layer 10's placement facts). The fourth lead or a bar is
therefore not needed as the correction for the service cases; the declared upper bound's printed row stays STILL OPEN as before.

## 4. The composition proof and the designators (`l8r2_drafts.out` sections 5 to 7 and 6b)

**Board A.**
- L4-POWER-ARCHITECTURE.md section 3's order runs r12, guard, charger (3a), r11 (3b), bank (3c), r138 (3d), u17 (3e). Then come
  l8gnd's gnd002 and hotr1 (3g), this record's d8v3, vbus20ov and (round 3) packrtn, and d8dec31's mainpb last (3h): **OK at every
  step**.
- This record's three first, then every other draft in that order and mainpb: OK at every step, so **every anchor of theirs still
  applies after this record's**.
- Each power draft alone after this record's three: OK. The five Layer 8 drafts in reverse order: OK.
- mainpb, which takes the next free R and C at apply time, now takes **R248 and C247**, not the R233 and C241 L4-E9's 3h states
  (F2-02).
- Round 4: slotlm composes in that order after packrtn and before mainpb (mainpb still at R248 and C247: slotlm's designators are
  list elements of its lm5176 calls, which next_free does not read, in a block it never reaches). It must follow L4-E11's charger,
  whose anchor names VBAT's `"U4": 2.0`: slotlm then the charger is REFUSED, the charger then slotlm is OK (an order constraint,
  F4-02). packrtn and slotlm in either order give one generator. The six Layer 8 drafts apply in reverse order.

**Board B.** No power draft targets `gen_sch_b.py`. l8gnd's GND-002 draft (R-195) and this record's three apply forward, in reverse
and each alone: OK.

**Board E (round 3).** The change list's board E round, read from L4-POWER-ARCHITECTURE.md's change table (q1, u5_grade, hold,
input_limit, backstop, f1, hotswap, entry, solar_guard, aux, d8dec31's cin last), and this record's packrtn give OK at every step in
three orders: packrtn last, packrtn first, and packrtn before cin. packrtn also applies after every prefix of the round, 0 to 11
drafts. The round's drafts depend on one another, so none is applied alone. packrtn adds no designator, and no literal designator is
drawn twice in the composed generator.

**Designators.** Read from the text each draft writes: literal part calls, whole designator strings read with Python's tokenizer, and
each draft's own declared ADDS (the coolers' are computed per slot).
- Board A, this record: d8v3 C242, C243, R234 to R238, U44; vbus20ov C244 to C246, Q41, R239 to R247, U45; packrtn none (an intent
  declaration). Board E, this record: packrtn none.
- Board A, the other drafts: charger C236 to C239, D23, Q39, Q40, R228, U42; bank R221 to R226; u17 R227; l8gnd H1, R229, C240,
  R230 to R232, U43; mainpb C247, R248.
- Board A, round 4: slotlm U501, U531, Q501 to Q504, Q531 to Q534, L501, L531, D501, D502, D531, D532, R501 to R512, R531 to R542,
  C501 to C519, C531 to C549 (its U8, U10, R30 and R38 are kept parts, now drawn as literal calls). Board B, round 5: rt500 none (a
  value change); it composes with record l6r2's board B drafts (xal_land, lcsc, intent) in either order into one generator.
- Board B: fans12 U701, U702, U731, U732, U761, U762, L701, L731, L761, Q701, Q702, Q731, Q732, Q761, Q762, R701 to R712, R731 to
  R742, R761 to R772, C701 to C710, C731 to C740, C761 to C770; panel5v U901, R901 to R905, C901, C902.
- **Pairwise intersections: none on either board.** No literal designator is drawn twice in either composed generator.
- Board B's 700 and 900 blocks are free of every designator the generator builds from a base.
- Duplicate references built at run time are refused by `kisch.part()` on the box.

## 5. Findings for other owners

| id | finding | owner |
|---|---|---|
| F2-01 | Board B's slot rails. Round 6: the fan row is 0.69 A at the steady envelope and the three slots are declared at 6.6 A, the bounded start-up and fault envelope (5.341 A of loads, accepted; section 1s). Round 5: 5.63 A. Round 4: 0.47 A at full speed and 5.3 A. Round 3: the fan row is 0.33 A at the modules' 70 % maximum (it was 0.1 A as drawn, 0.47 A in round 2, whose 5.121 A on slots 1 and 3 intent.rail refuses against their 5.0 A peak); the declared loads are 4.981 A, under the peak. Still owed: `+5V_Sn`'s typical declarations (2.5 A on slots 1 and 3, 4.2 A on slot 2) re-derived with it; `pwr_budget.py`'s cooler row (0.36 to 0.56 W, a representative fan) to the pick at the controls' duty (R-150) | board B's owner, Layer 4 |
| F2-02 | d8dec31's mainpb moves to R248 and C247 once this record's drafts are in board A's round; L4-E9's step 3h text (R233, C241) and R-193 to be restated, or mainpb given fixed references above every draft's (R-194) | L4-E9's change-list owner |
| F2-03 | IF-AE-DOCK: board A's J_VR1..4 on VIN_RAW_IN, the alias of board E's VIN_RAW; `check_contracts.py`'s alias table and `block_contract.py`'s check 5 (E5's T_VR targets judged against board A's J_VR net name) read the new name; VIN_RAW_IN carries the cross-board share | Layer 5, the tools' owner |
| F2-04 | Q41's SOA (CSD19532Q5B, SLPS414B) under board E's breaker retries with Q2 shorted (at most 7.136 A for 0.49 ms, or 13.87 A filtered, at VDS up to 41.22 V, every 0.5 s) and in its slewed turn-on into VIN_RAW's 32 uF; and the drop it adds in VIN_RAW (at most 4.6 mOhm at 5.983 A, 28 mV) to L4-E11's 9 V-plug arithmetic (VIN_RAW 8.148 V) | Layer 9, L4-E11's owner |
| F2-05 | s120's VBUS20 membership gate (`vbus20_bound.py`) refuses a new part on VBUS20 until the list is re-read: R241 is one | s120's owner (the power review) |
| F2-06 | Board B's U23 and U24 (and every `efuse()` call on board B) carry OVLO 100 k over 10 k on a 5 V input: the pin at 0.46 V, under SLVSET8A's 0.5 V recommended minimum | board B's owner |
| F2-07 | The DGX-19 land (`meshsat:TI_DGX0019A_VSSOP-19_3x5.1mm_P0.5mm`) is owed for board A's U45 as for board E's U6 (E11-01); the TPS61089's KiCad land `Texas_VQFN-RNR0011A-11` to be read by `check_land` on the box | the box, the integrator |
| F2-08 | `lcsc_fill.py` rows owed for 127k, 88.7k, 23.7k, 1.87k, 604R, 42.2k, 33.2k, 3.83k and the 0.1 % 200k and 10.0k; the XAL6060-472ME carries no code on either board | Layer 6, the BOM re-take |
| F2-09 | Round 4 read the maker's catalogue (C1152B001 pp.362, 616, 623, 633: the open terminal is full speed, a PWM input example, "several times the rated current" at a start, no figure); still owed: the model's PWM input level, pulse output and starting current: the maker's manual M0011876C (a request) or the bench (Layer 5's L5R2-F07) | Layer 6, Layer 9 |
| F2-10 | L4-E9's supplier list 8g: P1-2 and P1-3 become "drafted (record l8r2), supplier review of the draft and its bench rows" rather than design-correction tasks; P1-1 stays the supplier's | the Layer 4 coordinator |
| F2-12 | Record l8gnd's `l8gnd_drafts.out` on this merged line pins two inputs that moved after `226e9143` (L4-POWER-ARCHITECTURE.md, now `dcd4f972d9e3cfc0`, and L4-E11's charger draft, now `d857a70256d1c77e`): its committed-output predicate fails on those two pin lines alone, while its composition and designator predicates pass against the new charger draft; regenerate it with `_bin/regen_out.py` at the merge | the integrator (or l8gnd's author) |
| F2-11 | `HW-FW-CONTRACT.md` and CONOPS: the coolers' PWM released at boot gives full speed (INFERRED), the module's fan control owns the duty; a VBUS20 cut is logged as a front-end fault | Layer 5, the firmware owner |
| F3-01 | (Round 4: superseded by F4-03 to F4-05, the 70 % maximum withdrawn.) Record l9pwr's reader of `l8r2_drafts.out` takes `eta_slot` (retired in round 3: the flat 0.90 its own R9 corrected) and the choice (a) line, which now reads the three coolers at 7.56 W (its R9) where it read 7.84 W; its HIGH for the coolers becomes the 70 % maximum's 1.4 W a fan (the linear bound), which moves L9P-F02's figure to 4.871 A (+0.129 A) and the fans' share of L9P-F01 | record l9pwr's author (its parse and its R9 and section 10 lines) |
| F3-02 | (Round 4: superseded by F4-03 to F4-05, the 70 % maximum withdrawn.) `HW-FW-CONTRACT.md`: a FW row for the coolers' Fan_PWM maximum (70 %) and its order (PCIE_PWR_EN only after the fan control runs with it); IF-BAY-FANS or IF-B internal's slot-cooler rows name the maximum (section 1r's texts) | Layer 5 |
| F3-03 | (Round 4: superseded by F4-03 to F4-05, the 70 % maximum withdrawn.) Record l7pwr's reader of this draft's slot row (`read_rails`) now reads 0.33 A, 1.4 W, 0.85 and 5.0 V, the fan at the maximum, and derives the step-up's loss there (0.25 W); its hold figure adds that loss to the cooler at full speed (2.0 W) and reads 7.05 W where it read 7.15 W, two states mixed: at full speed the loss is 0.353 W (released, the card off), at the maximum the fan is 1.4 W and the loss 0.247 W. Its committed output and page (7.15 W) move with this draft's pin (test_l7pwr reads 2 failures on this branch, the re-pin and the restatement being its author's). The hold's fan duty (F-L7-05) is a setting at or under the maximum; the airflow at the maximum (about 70 % of 13.4 CFM, INFERRED) against L4-E12's 3.7 CFM representative | record l7pwr's author, the integrator |
| F3-04 | (Round 4: superseded by F4-03 to F4-05, the 70 % maximum withdrawn.) L9P-F01 (D-11's all-transmit basis takes the fans at HIGH): the coolers at the maximum draw at most 5.29 W at VBAT against 7.5638 W at full speed (2.27 W less, the linear bound), a figure for the floor's re-derivation or FW-A05's key-down cap | L4-E9 (C05, FW-A05) |
| F3-05 | L9P-F03: item 1 leaves the device rail as drawn in every option; 0.027 A of its drafted 7.181 A in PS-ALLTX is this record's item 3 (U901's RON at the panel's 0.980 A, 0.138 W); the rest is the drawn design's (I-03) | board A's generator owner (I-03), the TEST-PLAN power rows |
| F3-06 | The energy chain's coordination (energy_chain.py check 3) holds DOCK_ENTRY's and BOARD_A_NODE's 25 A conductors at 1 oz only on bands of at least 12.26 mm on each of two faces; record l9stk's decided minimum (6.72 mm on each of two, sized at the path's 18 A) carries 18.00 A by the same model. Either the band rule rises to 12.26 mm a face where the chain claims 25 A, or the chain's ratings are restated as measured and the coordination answered | record l9stk's author (its decisions A and E, `layout-constraints/A.md` and `E.md`), the energy chain's writer |
| F3-07 | Board E's DC_HS band (gen_pcb_e3.py: one B.Cu band, run 5.5 mm, leg 4.5 mm) carries 8.07 and 7.13 A at 1 oz, under SHORE_INPUT's F1 10 A (11.78 and 10.56 A at 2 oz, over it): at 1 oz the band needs its F.Cu twin of at least 2.76 mm, or 8.15 mm on one face | board E's PCB generator owner (gen_pcb_e3.py), record l9stk's author |
| F3-08 | The order for the integrator: `apply_energy_chain_e1oz.py` after l9stk's `apply_decisions_l9stk.py` (it refuses before); the two packrtn drafts at any point of their boards' rounds (section 4), released with this record's other drafts | the integrator |
| F3-09 | The box re-takes once the packrtn drafts are applied: PWR-001 on boards A and E (GND's sources and loads), PI-001, PI-002 and PI-003 on GND (on board A a whole-board solve of In1, In4 and the pours), THM-001 (GND excluded as a return) | the box |
| F3-10 | L4-E9's change list: the two packrtn drafts (board A after 3g's l8gnd drafts and before mainpb; board E anywhere in its round) and R-190's row at 0.33 A with the 70 % maximum | L4-E9's change-list owner |

| F4-01 | The AP64500 on slots 1 and 3 is past its typical derating at C1's 50 C inside air at each option's current at the least load voltage (Figure 24 at 500 kHz: 5.487 and 5.118 A over the 5 A rating, 4.779 A to 48.4 C; round 5), and the drawn stage runs at 1.47 MHz with more loss; record l4e12's method's 166.5 to 137.0 C are a 500 kHz screen, not its temperature; designed out by `apply_gen_sch_a_slotlm.py` (section 1s) | board A's generator owner (I-03), released with this record |
| F4-02 | The order constraint: slotlm after L4-E11's charger (3a), whose anchor names VBAT's "U4": 2.0; with this record's other board A drafts before mainpb; released with fans12 and rt500 (board B's half of the 5.63 A peak and the slot bucks' 500 kHz) | L4-E9's change-list owner, the integrator |
| F4-03 | Record l9pwr: L9P-F02 is answered by slotlm (slots 1 and 3's limit becomes the LM5176 loop's 7.096 A at least, their efficiency the declared 0.90 as its M1 takes slot 2); its D4 model of the coolers at full speed stands; round 3's 70 % maximum, which F3-01 asked it to take, is withdrawn | record l9pwr's author |
| F4-04 | Record l7pwr: its reader of this draft's slot row reads 0.69 A, 2.75 W, 0.80 and 5.0 V (round 5's envelope: the fan's bound at 12.43 V over the step-up's worst efficiency), so its hold figure takes the envelope; its committed output moves with this draft's pin (test_l7pwr: 1 failure on this branch, the byte-for-byte output; the re-pin is its author's) | record l7pwr's author, the integrator |
| F4-05 | The energy and heat of the two stages at the declared 0.90 against the AP64500's curve point: +0.373 W at VBAT in the profile, +0.872 W in PS-BUSY, +0.822 W in PS-ALLTX (PLAN), heat in the case; FW-A15's bench reading of the LM5176 at 5.1 V settles it | L4-E9 (endurance), L4-E10, L4-E12 (the case heat) |
| F4-06 | The same FET arithmetic on the device rail's LM5176 stage at its drafted 7.181 A (PS-ALLTX): the buck-side high FET 1.510 W, 125.5 C at 50 C air on 1 inch2 of 2 oz copper, against +150 C | board A's generator owner (I-03, THM-001) |
| F4-07 | `gen_pcb_a3.py` places U4, U6, L3, L5 and the AP64500 stages' passives by name (the slot columns, SLOT, SLOT_CAPS, R1S and R3S): slots 1 and 3 take slot 2's column template; the stages' loop and bulk ripple re-run (C4-2); the regenerated netlist read by `check_l8r2_netlist.py` SLOTS | the box, board A's PCB generator owner |
| F4-08 | Record l8gnd's hotr1 draft names "U4, U5 and U6's enables" in a comment; with slotlm they are U501, U5 and U531 (its keeper's arithmetic already covers the LM5176's enable thresholds); prose, owed at release | this record's author (l8gnd), at release |
| F4-09 | The fan's PWM frequency: the stock CM5 tree drives 41566 ns (24.06 kHz) against the maker's printed 25 kHz; the catalogue warns that a frequency outside the specified range alters the duty to speed characteristic | Layer 5 (the FW row of section 1s), the module's software |
| F4-10 | The maker's questions for 9WPA0412P6G001 (C4-4), drafted, not sent | the owner (an outside contact) |
| F5-01 | O-20 on board B: the six AP64500 slot bucks draw 68 k, 1.47 MHz, not the 500 kHz of the maker's curves the budgets use; drafted by `apply_gen_sch_b_rt500.py` (200 k 1 %), released with this record's other drafts; O-20's row in records/r4b to be marked drafted | board B's generator owner, the integrator |
| F5-02 | O-20 on board A: buck5's 68 k on U4 and U6 sets 1.47 MHz while its value text says 500 kHz; retired with U4 and U6 by slotlm, so nothing is left on board A | board A's generator owner (closed by slotlm's release) |
| F5-03 | The LM5176 5.1 V stages (slot 2, the device rail, and slotlm's slots 1 and 3) reach 4.928 to 5.252 V on the 1 % divider, 2 mV over the CM5's 5.25 V input at the extremes. Round 6: CORRECTED in draft by `apply_gen_sch_a_fb01.py` (F6-01) | board A's generator owner, released with this record |
| F6-01 | `apply_gen_sch_a_fb01.py`: the eight divider resistors at 0.1 %, 5.0019 to 5.1744 V; released with slotlm and packrtn (any order); FB01 on the regenerated netlist | the integrator, the box |
| F6-02 | Layer 6: 0.1 % codes for 53.6 k and 10 k (R32, R33, R40, R41, R501, R502, R531, R532) | Layer 6 (the BOM re-take) |
| F6-03 | Slot 2: the cooler's bounded start (the branch's 1.80 A) adds to I-03's all-peak coincidence on slot 2, whose conditional bound already sits over the loop's least; I-03 stays its owner's, and this record's 6.6 A covers slot 2's own HIGH with the start (5.7473 A) | board A's generator owner (I-03) |
| F6-04 | The box: the conductor checks that read the slot leads' declared peak (dc_drop's density verdict, `via_current.py`, `rail_crossings.py`) re-taken at 6.6 A on boards A and B after release | the box |
| F5-04 | Layer 6: record l6r2's LCSC table keys board B's six RTs by "68k (RT: 500 kHz)" (C23231); after rt500 they keep no code (its own rule); a 200 k 1 % row is owed, and slotlm's new parts and retired ones as in section 1s | Layer 6 (the BOM re-take) |
| F5-05 | The slot monitors' alert (FW-A09) at the steady envelope's 5.43 A filtered over 1.0 s (round 6; the start bound's duration), so a degraded cooler's steady 6.15 A is reported; the stage's 7.0957 A loop stays the hard limit | Layer 5, the firmware that masters the kit bus |

**For the record (not this record's item):** R-176's Q12 figure is resolved to 63 A by L4-E7 at `d562e75a`, which is not in this branch's history and is cited by commit only.

## 6. Owed, with the next action each

| item | owner | next action |
|---|---|---|
| the release of the drafts | the integrator | an accepted check of this record and a `RELEASE.md` beside the drafts; `--write` in section 4's order (board A: after 3g, before mainpb; board B: any order) |
| regeneration and parity of boards A and B | the box | the generators with the drafts; `check_l8r2_netlist.py` on the regenerated netlists (every correction expected DRAWN); `check_gnd002_netlist.py` (l8gnd) the same |
| the gate re-takes | the box | PWR-001, CMP-001, the decoupling declarations (the boost's power loop, a class R entry owed), RET-001 (CFANs_* and VCO_* need signal classes), SCH-002, INT-001 (the aliases of F2-03), the energy chain's B_PANEL_5V stage with U901 ahead of F1 |
| the bench rows | Layer 9 | sections 1 to 3; round 3: the fan's input at 70 % and 100 % duty, slot 1's current with every load at its maximum and the fan at the maximum, full speed released at boot (section 1r) |
| the round 3 drafts' release | the integrator | `apply_gen_sch_a_packrtn.py` and `apply_gen_sch_e_packrtn.py` with this record's other drafts (RELEASE.md); `apply_energy_chain_e1oz.py` after l9stk's decisions (F3-08) |
| the Fan_PWM maximum | Layer 5 | WITHDRAWN in round 4: section 1s's FW and interface rows replace section 1r's (F3-02) |
| round 4's slot stages | the integrator, the box | release slotlm after the charger with fans12 and rt500 (F4-02); regenerate and place board A (F4-07); C4-1, C4-2 and C4-6 |
| round 5's answers | the collaborator, the coordinator | a targeted recheck of B1 to B3 against section 1t; L9P-F02 stays OPEN until the corrections are implemented and verified |
| round 4's bench and maker items (round 6's limits) | Layer 9, the owner | C4-1 (the stage over the matrix 3.0 to 6.6 A at 9.7 to 17.4 V, 50 C, the measured junction bound), C4-3 (the actual chain in a loaded slot, 3.44 W steady, the 1.80 A and 1.0 s waveform), C4-4 (the maker's answer, the owner sends it), C4-5 (the SoC at 8 W in 50 C air) |
| the return's copper and the chain's widths | the box, record l9stk's author, board E's PCB generator owner | F3-06, F3-07, F3-09 |
| rounds 7 and 8's four drafts | the integrator, the box | release `apply_gen_sch_b_fandec.py` and `apply_gen_sch_b_gndret.py` with fans12 (R-190's release; any place in board B's round), `apply_gen_sch_b_gndrtn.py` after gndret, and `apply_gen_sch_a_gndrtn.py` on board A before mainpb; the box's KiCad export of both boards read by `check_gndret_netlist.py` (expected: the declaration DRAWN, the dedicated return DRAWN); the XT60-F land read; the copper rules on the routed boards |
| L8R2-F31, the return between boards A and B | the coordinator; then boards A and B, Layers 5 and 7, L4-E9's register | one independent check of round 8 (section 3g lists what it should read); OPEN until then. After it: the harness and contract rows (L8R2-F34, L8R2-F41) and the change-list rows (L8R2-F36) |
| the latent faults of the return | Layer 12, Layer 5 | L8R2-F39: a four-wire bond reading between the two boards' grounds in the assembly and service procedures, or a detect line (not drafted) |
| rounds 7 and 8's layout, harness and part items | Layer 9, Layer 7, Layer 6 | L8R2-F33 (solid joins, section 3g's widths), L8R2-F34 (the wire parts; `J_54V` at AWG 16; the three return leads), L8R2-F40 (the XT60-F's land and LCSC code; the leads' marking), L8R2-F42 (the XT60's range ends at the envelope's cold end) |
| the makers' questions | the owner | Q-JST-VH-1, Q-AMASS-XT60-1 and Q-WE-CAB-1 are drafted in section 3g and UNSENT |

## 7. The tests (`v2/ecad/tools/tests/test_l8r2.py`)

- The committed .out is what the script prints, and the script writes nothing into the tree.
- Each draft checks without writing, applies once, refuses a second time and refuses the tree's own generator.
- Board A: the drafts compose in L4-E9's order with this record's after l8gnd's and mainpb last; every power draft's anchor still
  applies after this record's drafts, in sequence and each alone; the five Layer 8 drafts apply in reverse order.
- Board B composes forward, in reverse and each alone.
- The designators are disjoint on both boards and are exactly this record's sets, with mainpb at R248 and C247; no literal
  designator is drawn twice.
- Item 1's figures: the rail inside the fan's range, ILIM over the fault peak and Isat over ILIM, the crossover under its limit,
  OVLO over the rail.
- Item 2's figures: the clamp's fault power over ten times its rating; the cut between the bus bound and U3's recommended 26 V; the
  bus after the cut under U3's absolute 32 V and Q7's 30 V.
- Item 3's figures: each PANEL_5V conductor under 1 A with the limit over board C's peak; board D's branch inside its window.
- The netlist check: NOT DRAWN on the committed netlists, DRAWN on fixtures, FAIL on a mutated fixture.
- Board C: the PI button draft and Layer 6's give the same generator in either order; this one adds R57 alone; the button reaches
  U1 P1.3 with R57 and C27, and the stale note is gone.
- Every net the drafts add is new on every board.
- The page carries no em or en dash and no claim word.
- Round 3, item 1: record l9pwr's output parses (eleven states, R9, L9P-F02 and F03); the drafted coolers reproduce L9P-F02 (-0.010 A);
  the 70 % maximum holds every slot converter at HIGH in every state at the step-up's 0.85 and its low 0.80, (b) holds more, and the
  released state holds; the device rail is the same in every option, its DRAWN-to-DRAFTED step U901's; round 2's slot loads are
  refused by intent.rail itself and round 3's accepted, under the peak; the flat 0.90 is gone.
- Round 3, item 1: the slot row reads with Layer 7's two expressions (0.33 A, 1.4 W, 0.85, 5.0 V).
- Round 3, board E: the change list's round in the page's order is the script's, and packrtn applies after every prefix of it and
  before it.
- Round 3, item 5: each board's GND is a rail that intent.py accepts (returns, 18 A, the half percent, 0 V), the node gone, every
  source and load on GND in the committed netlist; record l9stk's finding reads as found.
- Round 3, item 6: the chain's correction refuses without l9stk's decision, checks, writes once and then does nothing; the corrected
  stages name 1 oz and the computed widths; energy_chain.check reads the same; a chain without the old text once is refused; the
  tree's chain is never written; the two findings' arithmetic holds.
- Round 4: round 3's margin reads +0.129 A at 5.1 V and negative at the least voltage, the declaration +0.019 A; the linear bound
  lies inside the fan's bracket; every state with the card on and the firmware not driving is over 5 A on the AP64500 and within
  the LM5176 loop with more than 0.5 A; every HIGH option is over +125 C at C1's air; the pick at 70 % holds more than 10 Pa over
  the basis fan's maximum; the stage's FET under +150 C on the sheet's copper; the drafts quote the figures the check derives; the
  catalogue rows and sentences read off the held pages (skipped where not held); slotlm's designators are exactly the 500 block;
  the order constraint and packrtn's order independence hold; SLOTS fails with slot 3's shunt off its rail.
- Rounds 5 and 6: the AP64500's drawn frequency is 100000 / 68 kHz and the start's peak straddles the HS limit's least (may act, need not);
  the fan-fed options exceed the 5 A rating at the least voltage and option (b)'s Figure 24 reading stays a CONDITIONAL screen;
  every corner is taken at the 0.1 % divider's least load voltage (4.9019 V) and the steady envelope, the bounded start, a degraded
  cooler and slot 2's start are all under both boards' 6.6 A and the loop's 7.095710 A with more than 0.49 A; the junction screen
  over C4-1's matrix is monotone with 36.0 to 37.5 C/W at 6.6 A; board B's declared loads are accepted at 6.6 A; the drafts quote
  6.532 A, 5.434 A and 4.902 V; the fan row reads 0.69 A, 2.75 W and 0.80 with Layer 7's expressions; rt500 changes two lines,
  adds no designator, composes with Layer 6's board B drafts in either order; fb01 sets four divider pairs with packrtn and slotlm
  in all six orders into one generator, its window 5.0019 to 5.1744 V; FB01 fails with one resistor left at 1 %; both of the
  collaborator's files are filed as received.

Rounds 7 and 8 (task T5b and the recheck V3): the old state stops on the typed return and the correction runs to its end (the
same test fails without the drafts and passes with them); each draft is guarded and board B's compose with Layer 9's draft in
any order to one generator; the return is derived (22.23 A on the committed generator), and a typed figure, a lead left off, a
lead reversed and a lead whose rail is elsewhere are refused; the worst case is found, not sampled (round 7's sampled maximum
sits under the printed 10 A where the enumerated maximum is over it; the recheck's corner is summed independently; a walk of
every raw vertex of a small network agrees with the enumeration); the two return drafts are guarded and compose on both
boards; the return removed, landed on the wrong net or with one termination dropped is refused; every branch with a printed
rating is inside it at every vertex with the return and outside it without; the committed `l8r2_gndret.out` is what
`l8r2_gndret.py` prints and its predicates hold; the page and the README carry the rounds with L8R2-F31 as OPEN.
