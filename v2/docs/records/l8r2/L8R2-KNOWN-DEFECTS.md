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
| `apply_gen_sch_a_slotlm.py` | DRAFT, board A, round 4 (L9P-F02): slots 1 and 3 on slot 2's LM5176 stage, the AP64500s U4 and U6 retired |
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

**The compact table.** Classes as in this page's head: MAKER, INFERRED (a reading off a maker's graph, or arithmetic on maker
figures under a stated assumption), ASSUMPTION, BOUND; UNRESOLVED where no held document prints the figure.

| # | Figure | State | Boundary | Source | Verdict |
|---|---|---|---|---|---|
| 1a | round 3's **+0.129 A**: 4.871 A against 5 A | PS-BUSY and PS-ALLTX at HIGH (every load at its maximum at once) | slot side, AP64500 U4's output: CM5 8.0 W, card 9.1 W, NVMe and switch 3.99 W, switch core 0.676 W through board B's bucks on their curves, the fan 1.4 W (70 % of 2.0 W, the linear bound) over the step-up's 0.85; 24.844 W over the nominal 5.1 V | 2c.1, "+0.129 A (round 3's margin)" | a HIGH state at the nominal voltage only |
| 1b | the declared **4.981 A**: +0.019 A against 5.0 A | none: a declaration intent.rail judges | slot side, board B's `_SLOT_LOADS` rows on +5V_S1 (CM5 1.6, U103 2.2, U104 0.7, U105 0.15, U116 0.001 A) plus the fan's row 0.33 A (1.4 W / 0.85 / 5.0 V), against the rail's declared peak (refused over 5.10 A) | 2c.1, "+0.019 A" | the declaration's distance from the source's rating; its rows are not the HIGH (U103 2.2 A against 1.959 A, U104 0.7 A against 0.865 A), so neither sum bounds the other |
| 1c | 1a at the least voltage: **5.118 A, -0.118 A** | PS-BUSY at HIGH | the same 24.844 W over 4.854 V: VFB 0.792 V on the 1 % divider gives 4.953 V, less the rail's 2 % drop budget; every load sits behind a converter and draws its power | 2c.1, "the same state at the least voltage" | **NOT A MARGIN** |
| 2a | the fan at 70 %, 12 V, free air: **NOT PRINTED** | 70 % duty | the maker's rows (MAKER, p.362): 100 %: 0.17 A, 2.0 W, 13700 min-1; 25 %: 0.03 A, 0.36 W, 3000 min-1; the speed at 70 % read off the maker's duty to speed example, 10,400 +-400 min-1 (INFERRED) | 2c.2 | UNRESOLVED; bracketed 0.99 to 1.15 W (the fan law through both rows) and 1.43 to 1.56 W (the chord in speed, the upper bound while the input is convex in speed): the linear bound's 1.40 W lies inside, so it bounds nothing |
| 2b | the supply: **up to 1.73 W at 70 %, 2.22 W at 100 %** | 12.43 V, the step-up's highest | the step-up's 11.51 to 12.43 V sits inside the fan's 10.8 to 13.2 V (MAKER); the maker prints the input at 12 V only; x1.111 by the fan laws (INFERRED) | 2c.2 | UNRESOLVED at the maker |
| 2c | the operating point: **not printed** | against the cooler's pressure | the maker's ratings are "at free air" (catalogue, How to Read Specifications) | 2c.2 | UNRESOLVED |
| 2d | the boost's loss: **0.21 / 0.27 / 0.39 W** | 1.56 W out | TI Figure 7-2 read at 0.1 A, 12 V out, about 0.88 typical (INFERRED); the draft's 0.85 (ASSUMPTION); TI's design 0.80 | 2c.2 | carried at 0.85, 0.80 for the inductor |
| 2e | the start: **not printed**; bounded at 6.69 W on 12 V, **8.36 W on the slot rail** | any start: power-up, a duty from 0 % (this fan stops at 0 %), a locked-rotor retry | "current several times the rated current may flow" (p.633); a locked rotor "the coil current is cut off at regular cycles ... restarts automatically" (p.616); bound: the eFuse U7x2's highest limit 0.538 A at 12.43 V, the step-up at 0.80 | 2c.2 | UNRESOLVED, bounded |
| 2f | the slot's other loads: **23.197 W**; the fan input the AP64500's 5 A leaves: 1.96 W at 5.1 V, **0.91 W at 4.854 V** | PS-BUSY at HIGH | slot side | 2c.2 | the 70 % maximum fails at the least voltage under even the most favourable model (0.99 W) |
| 3 | **5.010 A at 5.1 V, 5.264 A at 4.854 V** (fan 100 %, card on); **6.501 A** with a start, inductor peak 7.566 A over the 6.8 A limit | boot, reset or watchdog restart, a fan driver absent or unbound, an open PWM lead, a start with the card on (2c.3's seven rows) | Fan_PWM is an open collector, unpowered at the module's shutdown (CM5 datasheet 2.11, MAKER); R7x12 pulls the fan's lead to +5V_Sn; open terminal = 100 % (p.362, MAKER); PCIE_PWR_EN held low by R{s}06 100 k only while the module's 3.3 V is off; the bootloader's PCIe handling and the reset state of the pin are not stated (taken as the worse); the stock CM5 tree's fan node is disabled, its levels reach 250/255, at 24.06 kHz | 2c.3 | full speed is the default in every state the firmware does not drive; the 70 % maximum is enforced in none of boot with the card on, reset, a driver fault or an open lead; the AP64500 is over 5 A in each, and a start drives it into its cycle limit and hiccup (DS41979 7): the slot drops |
| 4a | cooling at 70 %: **at least 42.6 Pa at every flow up to 3.7 CFM**, against the basis fan's 27.4 Pa at most; free air 0.277 to 0.300 m3/min | 70 % duty | the approved basis (record l4e12 2h, parsed): the representative 30 mm fan's 3.7 CFM free air at 50 % through the heatsink, 0.873 l/s, +5.64 K over the mixed air at the CM5's 4.5 W; that fan's 0.11 inch H2O (Sunon, MAKER); the pick's 100 % curve under the fan laws at the speed's least reading, inside its 80 Pa plateau (INFERRED) | 2c.4 | **HOLDS**: the pick's curve lies over the basis fan's at every flow, so it moves more air through any heatsink (the maker's 50 % curve reads about 30 Pa at 3.7 CFM: about half duty meets it). The SoC at 8 W: no held document gives the cooler's thermal resistance, UNRESOLVED (T-H2) |
| 4b | the AP64500's junction: **166.5 / 161.9 / 151.1 C** at HIGH (full speed, the 70 % maximum, (b) without a cooler), **137.0 C** at PLAN in PS-BUSY, at 14.4 V in; +125 C holds only to 3.731 A | C1's +50 C inside air (CONOPS 4 as record l4e12 quotes it: the normal mode's ceiling), VIN 14.4 and 17.375 V | record l4e12's method: the converter's loss at its point (rv-pwr's curves on the maker's Figures 4 and 5) times theta-JA 45 C/W (MAKER, four-layer 2 oz, the minimum pad); the maker's Figure 24 read (typical, 12 V in): 4.679 A at 50 C; 5.010 A to 44.8 C, 4.871 A to 47.0 C, 4.548 A to 52.0 C | 2c.4 | **NOT ADEQUATELY RATED** in any option at HIGH: every row over +125 C, the full-speed and 70 % rows past the +160 C shutdown; (b) is 2 K inside the typical curve at 12 V in only |

**5. The decision (SESSION, under the owner's standing rule of 26 September 2026): slots 1 and 3 move to slot 2's LM5176 stage
(F-PR-04's own pattern), the coolers keep their 12 V step-up at full speed, and round 3's 70 % Fan_PWM maximum is WITHDRAWN.**
- Not the maximum: rows 1c, 2f and 3. It is a firmware rule that the hardware's own defaults defeat, and it holds only at the
  nominal voltage.
- Not (b) per slot alone: it takes the fan off the rail (4.548 A at HIGH, 4.779 A at the least voltage), but the AP64500 stays over
  +125 C by row 4b's method and at the edge of its typical curve, and it costs three converters, a third lead pin and new Layer 5
  and Layer 7 texts.
- The LM5176 stage is the part this board already certifies five times (C442493, every land in the library): no board B change
  beyond the declared peak, no harness, no new interface. Its average loop limits at 7.096 A at its least (43 mV over the 6 mOhm
  ISNS shunt at +1 %, parsed from record l9pwr).
- Approved service is not reduced: the module's fan control may run the cooler to 100 % whenever the SoC asks; the airflow basis
  holds from about half duty.
- No requirement changes; nothing is bought (generator text only). The test of 21 September 2026 leaves it the session's.
- Reverse by (b) per slot together with a converter above the AP64500 on slots 1 and 3, if the LM5176 stage fails its bench row
  (C4-1) or its area on board A (C4-6).

**The margins in every state** (2c.5; slot 1 and 3 at HIGH on the LM5176 stage; the stage's least output 4.928 V, 4.829 V at the
load with the 2 % drop; "start" adds the cooler's start through its eFuse's highest limit):

| State | A at 5.1 V | at 4.829 V | with a start | margin to 7.096 A, steady / start |
|---|---|---|---|---|
| PS-IDLE, PS-IDLE-SPEC, PS-RED-b (slot 3, the higher) | 3.294 | 3.478 | 4.722 | +3.618 / +2.374 A |
| PS-TYP (slot 3) | 4.324 | 4.566 | 5.810 | +2.530 / +1.286 A |
| PS-BUSY, PS-ALLTX (slots 1 and 3) | 5.010 | 5.290 | 6.534 | **+1.806 (25.4 %) / +0.562 A** |
| PS-EMCON (slots 1 and 3) | 2.365 | 2.497 | 3.741 | +4.599 / +3.355 A |
| PS-RED, PS-RED2, PS-SURV-R (slot 3 alone) | 1.825 | 1.928 | 3.171 | +5.168 / +3.925 A |
| row 3's states: module off; boot, reset, driver fault, open lead (card on); the last duty held; a start with the card on | 3.225; 5.010; 4.871; 6.188 | 3.406; 5.290; 5.144; 6.534 | | +3.690; +1.806; +1.952; +0.562 A |

- The stage's hottest part, its buck-side high FET (CSD19532Q5B), at 5.290 A and 17.375 V in: conduction 0.094 W, the edges
  0.293 W (18.0 and 9.5 ns from the LM5176's drivers and the FET's gate charge), Coss 0.516 W, the body diode's recovery 0.312 W:
  **1.215 W, 110.7 C at C1's 50 C air on the sheet's 1 inch2 of 2 oz copper (RthJA 50 C/W at most) against +150 C**; 201.9 C on
  the minimum pad. +125 C holds to 61.7 C/W: CONDITIONAL on board A's copper (C4-1). The low FET 0.336 W, the boost-side high FET
  0.319 W. The AP64500 by the same kind of arithmetic: 166.5 C in one package.
- The declared peak, both ends of the lead: 5.290 A needed, **5.3 A** declared (as slot 2 declares 5.63 A); VBAT's entry per stage
  2.086 A, declared **2.09 A** (the S-98 method of Q28's 2.22 A). Board B with round 4's draft: slot 1's declared loads 5.121 A
  against 5.3 A, accepted by intent.rail.
- The cost: at PLAN, VBAT side, +0.373 W in the profile (PS-IDLE-SPEC), +0.730 W in PS-TYP, +0.872 W in PS-BUSY, +0.822 W in
  PS-ALLTX (the stages' declared 0.90, NOT PLOTTED by the maker, against the AP64500's curve point). The same watts are heat in the
  case. FW-A15's bench reading of the stage settles the figure (F4-05).

**The drafts as changed** (2c, sections 5 to 8 of the output):
- `apply_gen_sch_a_slotlm.py` (new, board A): the two buck5 calls become slot 2's lm5176 call for S1 and S3 with their SLOT_EN
  pull-downs (R30, R38 kept) and INA226 monitors (U8, U10 kept, now across the 6 mOhm ISNS shunts R505, R535); VBAT's U4 and U6
  become Q501 and Q531 at 2.09 A; the slot rails' shunts, switches (U501, U531) and peak (5.3 A); SECTIONS. Designators in the free
  500 block (500 + k on slot 1, 530 + k on slot 3: U, Q 1 to 4, L, D 1 and 2, R 1 to 12, C 1 to 19); retired U4, U6, L3, L5, C28 to
  C33, C40 to C45, C112, C114, R28, R29, R31, R36, R37, R39, R45, R47, R129, R131. It follows L4-E11's charger (its anchor names
  VBAT's "U4": 2.0), which L4-E9's order already gives; mainpb stays at R248 and C247.
- `apply_gen_sch_b_fans12.py`: the fan's row back to 0.47 A (2.0 W over 0.85 at 5.0 V, the form Layer 7's reader parses), slots 1
  and 3 declared at 5.3 A, round 3's text withdrawn; designators unchanged.
- `apply_gen_sch_a_packrtn.py`: where slotlm is applied first, slots 1 and 3's ground ends are their CS shunts R506 and R536;
  either order gives one generator.
- `check_l8r2_netlist.py`: SLOTS, what the regenerated board A netlist must show (NOT DRAWN today, DRAWN on its fixture, FAIL with
  slot 3's ISNS shunt off +5V_S3).

**What remains CONDITIONAL, each with its specimen and acceptance:**
- **C4-1, the stage on board A's copper.** Specimen: board A's slot 1 and slot 3 stages as placed and routed (the box's thermal
  pass), then one built stage on FW-A15's bench. Acceptance: at 50 C ambient, 17.4 V in, 5.3 A out for 30 minutes, the buck-side
  high FET's case at most 120 C, and the stage's efficiency at least 0.90 at 5.3 A (the figure the budget uses). On failure: more
  copper under the FETs, or the reversal above.
- **C4-2, the loop and bulk ripple of slots 1 and 3.** Slot 2's design is copied; board B's remote capacitance on slots 1 and 3
  (the WiFi card's socket) differs from slot 2's. Acceptance: the stage's loop and bulk scripts re-run on the slot's remote
  capacitance with phase margin at least 50 degrees, gain margin at least 10 dB on the narrow band and positive on the widened band
  (slot 2's 9.4 dB), bulk ripple at most 1.8 A rms per EEHZK1E151XP.
- **C4-3, the fan (R-190, E11-35).** Specimen: three 9WPA0412P6G001 on the fitted CM5 cooler, fed at 11.5 and 12.43 V through
  the drafted eFuse. Acceptance: at 100 % the input at most 0.30 A (under the eFuse's least limit 0.448 A); the start completes
  (tach at the rated speed +-10 % within 5 s) at -20, +25 and +70 C without the eFuse's fault latching; the input logged at 25, 50,
  70 and 100 % duty for the case heat (L4-E12, L7). The supply's margin no longer depends on these figures.
- **C4-4, the maker's answer (drafted, not sent; the owner's to send).** To Sanyo Denki, for 9WPA0412P6G001: the PWM input's levels
  and frequency range (the catalogue prints an example, VIH 4.75 to 5.25 V, VIL 0 to 0.4 V, 25 kHz, "differ with models"), the
  starting current and its duration, the input at 70 % duty and against a static pressure, the pulse output's ratings.
- **C4-5, the SoC at 8 W (T-H2).** The airflow basis holds; the module's temperature against the cooler is not computed by any
  record. T-H1 and T-H2 log the coolers' speed with the readings.
- **C4-6, the area.** Two more LM5176 stages in board A's slot columns (16 mm pitch; slot 2's and the device rail's stages already
  stand in theirs): `gen_pcb_a3.py`'s slot column template for slots 1 and 3 (the box).

**Rows owed to others (texts; not edits of their files):**
- Layer 5, HW-FW-CONTRACT: round 3's proposed FW row (the 70 % maximum and its PCIE_PWR_EN order) is WITHDRAWN before entry. New
  FW row: "Each compute module drives its cooler's Fan_PWM at 25 kHz (a 40000 ns period; the stock CM5 tree's 41566 ns is 24.06 kHz
  against the maker's printed 25 kHz) with a duty set by the SoC's temperature up to 100 %, never 0 % while the slot runs (this fan
  stops at 0 % and each restart is a start, catalogue p.362); a tach reading under the commanded speed is reported as a stalled
  fan or an open lead (V-E07)."
- Layer 5, IF-BAY-FANS or IF-B internal's slot-cooler rows: "J_FANs pin 4 is the fan's PWM input; open, the fan runs at full
  speed (the maker)"; the "no more than 70 %" text of section 1r is not entered.
- Layer 5, IF-AB (the slot leads): +5V_S1 and +5V_S3 declared 5.3 A at both ends (was 5.0 A, the AP64500's rating), as +5V_S2's
  5.63 A; the stages' loop least 7.096 A.
- The module's monitor software and the panel firmware, wherever the INA226 at 0x40 and 0x44 is read: the shunt is 6 mOhm (was
  5 mOhm), so the calibration and the current LSB change, as F-PR-04 noted for slot 2's U9.
- Layer 6: the two stages' rows (2 x LM5176PWPR C442493, 8 x CSD19532Q5B C473333, 2 x XAL1010-682ME, 2 x 6 mOhm WSL2512 C843882,
  6 x EEHZK1E151XP C542453, 4 x BAT46W C83152 and the passives as slot 2's); retired 2 x AP64500SP-13, 2 x XAL6060-472ME and their
  passives.

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
  C501 to C519, C531 to C549 (its U8, U10, R30 and R38 are kept parts, now drawn as literal calls).
- Board B: fans12 U701, U702, U731, U732, U761, U762, L701, L731, L761, Q701, Q702, Q731, Q732, Q761, Q762, R701 to R712, R731 to
  R742, R761 to R772, C701 to C710, C731 to C740, C761 to C770; panel5v U901, R901 to R905, C901, C902.
- **Pairwise intersections: none on either board.** No literal designator is drawn twice in either composed generator.
- Board B's 700 and 900 blocks are free of every designator the generator builds from a base.
- Duplicate references built at run time are refused by `kisch.part()` on the box.

## 5. Findings for other owners

| id | finding | owner |
|---|---|---|
| F2-01 | Board B's slot rails. Round 4: the fan row is 0.47 A at full speed and slots 1 and 3 are declared at 5.3 A (5.121 A of loads, accepted; section 1s). Round 3: the fan row is 0.33 A at the modules' 70 % maximum (it was 0.1 A as drawn, 0.47 A in round 2, whose 5.121 A on slots 1 and 3 intent.rail refuses against their 5.0 A peak); the declared loads are 4.981 A, under the peak. Still owed: `+5V_Sn`'s typical declarations (2.5 A on slots 1 and 3, 4.2 A on slot 2) re-derived with it; `pwr_budget.py`'s cooler row (0.36 to 0.56 W, a representative fan) to the pick at the controls' duty (R-150) | board B's owner, Layer 4 |
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

| F4-01 | The AP64500 on slots 1 and 3 is over +125 C at C1's 50 C inside air at HIGH with every cooler option and at PLAN in PS-BUSY (record l4e12's method: 166.5, 161.9, 151.1 and 137.0 C at 14.4 V in; Figure 24's typical curve ends at 44.8, 47.0 and 52.0 C); designed out by `apply_gen_sch_a_slotlm.py` (section 1s) | board A's generator owner (I-03), released with this record |
| F4-02 | The order constraint: slotlm after L4-E11's charger (3a), whose anchor names VBAT's "U4": 2.0; with this record's other board A drafts before mainpb; released with fans12 (board B's half of the 5.3 A peak) | L4-E9's change-list owner, the integrator |
| F4-03 | Record l9pwr: L9P-F02 is answered by slotlm (slots 1 and 3's limit becomes the LM5176 loop's 7.096 A at least, their efficiency the declared 0.90 as its M1 takes slot 2); its D4 model of the coolers at full speed stands; round 3's 70 % maximum, which F3-01 asked it to take, is withdrawn | record l9pwr's author |
| F4-04 | Record l7pwr: its reader of this draft's slot row reads 0.47 A, 2.0 W, 0.85 and 5.0 V again (round 2's figures), so its hold figure returns to the fans at full speed; its committed output moves with this draft's pin (test_l7pwr: 1 failure on this branch, the byte-for-byte output; the re-pin is its author's) | record l7pwr's author, the integrator |
| F4-05 | The energy and heat of the two stages at the declared 0.90 against the AP64500's curve point: +0.373 W at VBAT in the profile, +0.872 W in PS-BUSY, +0.822 W in PS-ALLTX (PLAN), heat in the case; FW-A15's bench reading of the LM5176 at 5.1 V settles it | L4-E9 (endurance), L4-E10, L4-E12 (the case heat) |
| F4-06 | The same FET arithmetic on the device rail's LM5176 stage at its drafted 7.181 A (PS-ALLTX): the buck-side high FET 1.510 W, 125.5 C at 50 C air on 1 inch2 of 2 oz copper, against +150 C | board A's generator owner (I-03, THM-001) |
| F4-07 | `gen_pcb_a3.py` places U4, U6, L3, L5 and the AP64500 stages' passives by name (the slot columns, SLOT, SLOT_CAPS, R1S and R3S): slots 1 and 3 take slot 2's column template; the stages' loop and bulk ripple re-run (C4-2); the regenerated netlist read by `check_l8r2_netlist.py` SLOTS | the box, board A's PCB generator owner |
| F4-08 | Record l8gnd's hotr1 draft names "U4, U5 and U6's enables" in a comment; with slotlm they are U501, U5 and U531 (its keeper's arithmetic already covers the LM5176's enable thresholds); prose, owed at release | this record's author (l8gnd), at release |
| F4-09 | The fan's PWM frequency: the stock CM5 tree drives 41566 ns (24.06 kHz) against the maker's printed 25 kHz; the catalogue warns that a frequency outside the specified range alters the duty to speed characteristic | Layer 5 (the FW row of section 1s), the module's software |
| F4-10 | The maker's questions for 9WPA0412P6G001 (C4-4), drafted, not sent | the owner (an outside contact) |

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
| round 4's slot stages | the integrator, the box | release slotlm after the charger with fans12 (F4-02); regenerate and place board A (F4-07); C4-1, C4-2 and C4-6 |
| round 4's bench and maker items | Layer 9, the owner | C4-1 (the stage at 5.3 A, 50 C), C4-3 (the fan, R-190), C4-4 (the maker's answer, the owner sends it), C4-5 (T-H2) |
| the return's copper and the chain's widths | the box, record l9stk's author, board E's PCB generator owner | F3-06, F3-07, F3-09 |

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
