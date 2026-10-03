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
| `check_l8r2_netlist.py` | what the regenerated netlists must show, parsed; NOT DRAWN on the committed netlists today |
| `l8r2_drafts.py`, `l8r2_drafts.out` | every figure with its class, the composition on boards A and B, the designator census, the netlist check |
| `fetch_held_back.py` | TI's TPS4811-Q1 sheet (SLUSEE5E), held back by its terms, fetched from ti.com and checked by sha256 |
| `inputs/` | Layer 7's cooler identity (`fnd/l7pwr` at `2087060b`) and Layer 5's round 2 findings (`fnd/l5r2` at `6902db8f`), copied byte for byte, `inputs/SOURCES.txt` |
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
| Power at VBAT, three fans at full speed | 7.84 W (2.353 W a slot on +5V_Sn at efficiency 0.85, behind the slot converters at 0.90, both ASSUMPTION) | 6.74 W (one converter at 0.89, ASSUMPTION) |
| Difference | | (b) is 1.10 W lower at full speed, 0.31 W at the budget's 0.56 W a fan |

**SELECTED (SESSION): (a).** It needs no new interface, no harness and no board A change, and it keeps each fan with its own slot.
The 1.10 W that (b) would save at full speed is under the controls' duty in practice (R-150). Reverse by (b) if the bay harness gains a 12 V
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
0.480 A at 4.9 V), which adds 0.353 W of conversion. The draft moves the slot rail's fan row from `J_FANs` 0.1 A to the boost at 0.47 A.
The rail's own typical and peak declarations are not changed: a FINDING for board B's owner and Layer 4 (F2-01).

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

## 4. The composition proof and the designators (`l8r2_drafts.out` sections 5 to 7)

**Board A.**
- L4-POWER-ARCHITECTURE.md section 3's order runs r12, guard, charger (3a), r11 (3b), bank (3c), r138 (3d), u17 (3e). Then come
  l8gnd's gnd002 and hotr1 (3g), this record's d8v3 and vbus20ov, and d8dec31's mainpb last (3h): **OK at every step**.
- This record's two first, then every other draft in that order and mainpb: OK at every step, so **every anchor of theirs still
  applies after this record's**.
- Each power draft alone after this record's two: OK. The four Layer 8 drafts in reverse order: OK.
- mainpb, which takes the next free R and C at apply time, now takes **R248 and C247**, not the R233 and C241 L4-E9's 3h states
  (F2-02).

**Board B.** No power draft targets `gen_sch_b.py`. l8gnd's GND-002 draft (R-195) and this record's three apply forward, in reverse
and each alone: OK.

**Designators.** Read from the text each draft writes: literal part calls, whole designator strings read with Python's tokenizer, and
each draft's own declared ADDS (the coolers' are computed per slot).
- Board A, this record: d8v3 C242, C243, R234 to R238, U44; vbus20ov C244 to C246, Q41, R239 to R247, U45.
- Board A, the other drafts: charger C236 to C239, D23, Q39, Q40, R228, U42; bank R221 to R226; u17 R227; l8gnd H1, R229, C240,
  R230 to R232, U43; mainpb C247, R248.
- Board B: fans12 U701, U702, U731, U732, U761, U762, L701, L731, L761, Q701, Q702, Q731, Q732, Q761, Q762, R701 to R712, R731 to
  R742, R761 to R772, C701 to C710, C731 to C740, C761 to C770; panel5v U901, R901 to R905, C901, C902.
- **Pairwise intersections: none on either board.** No literal designator is drawn twice in either composed generator.
- Board B's 700 and 900 blocks are free of every designator the generator builds from a base.
- Duplicate references built at run time are refused by `kisch.part()` on the box.

## 5. Findings for other owners

| id | finding | owner |
|---|---|---|
| F2-01 | Board B's slot rails: the fan row now 0.47 A at full speed (it was 0.1 A); `+5V_Sn`'s typical and peak declarations (2.5 / 5.0 A on slots 1 and 3, 4.2 / 5.63 A on slot 2) to be re-derived with it, slot 2's peak against the LM5176's 7.10 A loop minimum; `pwr_budget.py`'s cooler row (0.36 to 0.56 W, a representative fan) to the pick's 2.0 W at the controls' duty (R-150) | board B's owner, Layer 4 |
| F2-02 | d8dec31's mainpb moves to R248 and C247 once this record's drafts are in board A's round; L4-E9's step 3h text (R233, C241) and R-193 to be restated, or mainpb given fixed references above every draft's (R-194) | L4-E9's change-list owner |
| F2-03 | IF-AE-DOCK: board A's J_VR1..4 on VIN_RAW_IN, the alias of board E's VIN_RAW; `check_contracts.py`'s alias table and `block_contract.py`'s check 5 (E5's T_VR targets judged against board A's J_VR net name) read the new name; VIN_RAW_IN carries the cross-board share | Layer 5, the tools' owner |
| F2-04 | Q41's SOA (CSD19532Q5B, SLPS414B) under board E's breaker retries with Q2 shorted (at most 7.136 A for 0.49 ms, or 13.87 A filtered, at VDS up to 41.22 V, every 0.5 s) and in its slewed turn-on into VIN_RAW's 32 uF; and the drop it adds in VIN_RAW (at most 4.6 mOhm at 5.983 A, 28 mV) to L4-E11's 9 V-plug arithmetic (VIN_RAW 8.148 V) | Layer 9, L4-E11's owner |
| F2-05 | s120's VBUS20 membership gate (`vbus20_bound.py`) refuses a new part on VBUS20 until the list is re-read: R241 is one | s120's owner (the power review) |
| F2-06 | Board B's U23 and U24 (and every `efuse()` call on board B) carry OVLO 100 k over 10 k on a 5 V input: the pin at 0.46 V, under SLVSET8A's 0.5 V recommended minimum | board B's owner |
| F2-07 | The DGX-19 land (`meshsat:TI_DGX0019A_VSSOP-19_3x5.1mm_P0.5mm`) is owed for board A's U45 as for board E's U6 (E11-01); the TPS61089's KiCad land `Texas_VQFN-RNR0011A-11` to be read by `check_land` on the box | the box, the integrator |
| F2-08 | `lcsc_fill.py` rows owed for 127k, 88.7k, 23.7k, 1.87k, 604R, 42.2k, 33.2k, 3.83k and the 0.1 % 200k and 10.0k; the XAL6060-472ME carries no code on either board | Layer 6, the BOM re-take |
| F2-09 | The fan's PWM input level, pulse output and starting current: the maker's manual M0011876C (a request) or the bench (Layer 5's L5R2-F07) | Layer 6, Layer 9 |
| F2-10 | L4-E9's supplier list 8g: P1-2 and P1-3 become "drafted (record l8r2), supplier review of the draft and its bench rows" rather than design-correction tasks; P1-1 stays the supplier's | the Layer 4 coordinator |
| F2-12 | Record l8gnd's `l8gnd_drafts.out` on this merged line pins two inputs that moved after `226e9143` (L4-POWER-ARCHITECTURE.md, now `dcd4f972d9e3cfc0`, and L4-E11's charger draft, now `d857a70256d1c77e`): its committed-output predicate fails on those two pin lines alone, while its composition and designator predicates pass against the new charger draft; regenerate it with `_bin/regen_out.py` at the merge | the integrator (or l8gnd's author) |
| F2-11 | `HW-FW-CONTRACT.md` and CONOPS: the coolers' PWM released at boot gives full speed (INFERRED), the module's fan control owns the duty; a VBUS20 cut is logged as a front-end fault | Layer 5, the firmware owner |

**For the record (not this record's item):** R-176's Q12 figure is resolved to 63 A by L4-E7 at `d562e75a`, which is not in this branch's history and is cited by commit only.

## 6. Owed, with the next action each

| item | owner | next action |
|---|---|---|
| the release of the five drafts | the integrator | an accepted check of this record and a `RELEASE.md` beside the drafts; `--write` in section 4's order (board A: after 3g, before mainpb; board B: any order) |
| regeneration and parity of boards A and B | the box | the generators with the drafts; `check_l8r2_netlist.py` on the regenerated netlists (every correction expected DRAWN); `check_gnd002_netlist.py` (l8gnd) the same |
| the gate re-takes | the box | PWR-001, CMP-001, the decoupling declarations (the boost's power loop, a class R entry owed), RET-001 (CFANs_* and VCO_* need signal classes), SCH-002, INT-001 (the aliases of F2-03), the energy chain's B_PANEL_5V stage with U901 ahead of F1 |
| the bench rows | Layer 9 | sections 1 to 3 |

## 7. The tests (`v2/ecad/tools/tests/test_l8r2.py`)

- The committed .out is what the script prints, and the script writes nothing into the tree.
- Each draft checks without writing, applies once, refuses a second time and refuses the tree's own generator.
- Board A: the drafts compose in L4-E9's order with this record's after l8gnd's and mainpb last; every power draft's anchor still
  applies after this record's drafts, in sequence and each alone; the four Layer 8 drafts apply in reverse order.
- Board B composes forward, in reverse and each alone.
- The designators are disjoint on both boards and are exactly this record's sets, with mainpb at R248 and C247; no literal
  designator is drawn twice.
- Item 1's figures: the rail inside the fan's range, ILIM over the fault peak and Isat over ILIM, the crossover under its limit,
  OVLO over the rail.
- Item 2's figures: the clamp's fault power over ten times its rating; the cut between the bus bound and U3's recommended 26 V; the
  bus after the cut under U3's absolute 32 V and Q7's 30 V.
- Item 3's figures: each PANEL_5V conductor under 1 A with the limit over board C's peak; board D's branch inside its window.
- The netlist check: NOT DRAWN on the committed netlists, DRAWN on fixtures, FAIL on a mutated fixture.
- The page carries no em or en dash and no claim word.
