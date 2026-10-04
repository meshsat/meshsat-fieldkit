# L9T5: C-ALLTX rev 3 and C-DEV rev 1, the uncertainty, three approaches and the selection (task T5, MESHSAT-1357)

4 October 2026, Layer 9's power author, worktree `l9t5` on branch `fnd/l9t5` from set 29's line `dc99897f`. **Status (round 1): a desk
selection, not reviewed, nothing drafted; round 2 in section 0.** Prototype design: nothing in this kit has been built, powered or measured, and no
figure on this page is a measurement. Every figure is printed by `l9t5_case.py` into `l9t5_case.out` ("out N" is its section),
which takes the case row from record l9pwr's budget (round 4, its out 7b) and every maker's figure from its pinned sheet. Labels:
PRINTED (a maker's limit), TYPICAL, MODEL, ASSUMPTION, MISSING. Case rows cited by id: **C-ALLTX rev 2**, **C-DEV rev 1**
(`inputs/coordinator-cases-2026-10-04.md`); the collaborator's challenge cx40 (`inputs/astra-challenge-f01-1.md`) is an advisory
AI review and accepts nothing. The owner's standing decisions of 4 October hold: FAN_OK is rejected and not revived; REQ-018's
15.5 V, the 60 s key-down, the 18 A service, the pack and every protection stay.

## 0d. Round 4, part 3: finding SDR3-F02, the Compute Module 5's supply design figure

Figures: `l9t5_cm5.out` ("cm5 N"), printed by `l9t5_cm5.py`, which reads the sheet held in the tree
(`v2/vendor/cm5/cm5-datasheet.pdf`, Release 3) and imports record l9pwr's budget unchanged. **No case row is changed here: a case
row's change is the coordinator's.**

**What the sheet prints (cm5 2).** Appendix B, "CM4 and CM5 differences", B.3 "Power budget": "CM5 delivers significantly more
performance than CM4, and therefore consumes more power. Power supply designs should accommodate 5 V at up to 2.5 A. If this
creates an issue with an existing board design, lowering the CPU clock rate can reduce the peak power consumption." Table 9
(section 4.3.3) prints idle 400 mA and operation 900 mA as TYPICAL figures and leaves its minimum and maximum columns empty.

**What kind of figure it is.** A supply design figure: the maker's advice to a carrier's designer, tied by its own next sentence to
the module's peak consumption. It is not a row of the consumption table, not a printed maximum and not a typical; the sheet prints
no consumption limit at all. It is the nearest figure the maker gives to an upper figure of a module's draw. Board B's generator
declares a module at 1.6 A and says "no maximum given", which is true of Table 9 and silent on B.3; rv-pwr and record l9pwr take
4.5 W typical and 8.0 W HIGH; the maker's figure is 12.5 W.

| What it is owed by | What it owes | The figures (MODEL on the budget's rows; the loop's least PRINTED VSNS over the DECLARED shunt) |
|---|---|---|
| the slot stages (L9P-F02) | **a bound, and a finding (L9T5-F15)** | steady, each module at 12.5 W: 6.3516 A against 7.0957 A on slots 1 and 3 (**+0.7441 A**), +1.5292 A on slot 2. With a cooler's bounded start coinciding (record l8r2, a 100 us average): 7.4503 A, **-0.3546 A** on slots 1 and 3 (+0.4305 A on slot 2). With a degraded cooler: +0.0251 A |
| C-ALLTX rev 3 ("the compute modules at typical") | **a labelled scenario, nothing in its definition** | the case 15.5162 V; at the budget's HIGH (8.0 W) 16.1718 V; at the maker's figure 268.014 W at VBAT, **17.0148 V** (+1.5148 V over REQ-018's 15.5 V rest). The row's unsettled item on the modules (nothing drawn holds them at typical) gains the maker's upper figure |
| the budget's states | **a labelled scenario row beside HIGH, in the budget's next round** | HIGH for a module (8.0 W) is the generator's allowance, not a maker's bound; the maker's figure is 4.5 W more a module, 13.5 W for three. HIGH is not changed here: L9P-F02's rows and D-11's scenario are stated on it |
| board B's slot rails (the generator's declaration) | **a finding for the generator's owner** | the slot branches sum to 4.751 A against a declared peak of 5.00 A (slot 2: 5.63 A); with the module at 2.5 A they sum to 5.651 A, over the 5.100 A that slots 1 and 3's declaration may carry |

**The assessment (cm5 6).** SDR3-F02 is confirmed as a finding. It bounds what the supply should carry, and the slot stages do
carry it steadily; they do not carry it together with a cooler's start on slots 1 and 3. What would settle it: the modules' measured
peak input current under the kit's own workload (a bench row), or a firmware ceiling on the CPU clock, which the maker's sentence
names as the lever. Neither exists in the tree. Nothing is drafted: the declaration is board B's generator owner's, L9P-F02's
conditions are record l8r2's, the case row is the coordinator's.

## 0c. Round 4, part 2: task T10, the supervisors' 3.3 V regulators (finding L9T5-F06)

The owner's instruction of 4 October 2026, part 7, on L9T5-F06: "verify its applicable operating conditions and give it a named
correction and acceptance criterion. Adding a dedicated ground return does not address that separate deficit." Figures:
`l9t5_t10.out` ("t10 N"), printed by `l9t5_t10.py` from the makers' sheets held in the tree. **L9T5-F06 STAYS OPEN:** the
conditions are verified, a correction is selected with its acceptance criterion and its circuit half is drafted; no independent
check has read it, Layer 5 has not accepted its row, nothing is applied. This is the first attempt at this correction.

**2a. The applicable operating conditions (t10 2 to 7).**

- **The state is unbounded.** Eleven rows of `HW-FW-CONTRACT.md` name the supervisors (U41, U51, U61, STM32H743VIT6); none bounds
  a run mode, a clock or a voltage scale. `PANEL.md` bounds nothing either, and `v2/firmware` holds the panel's firmware only.
  `ARCH-PCB-B-IOHA.md`'s "roughly 60 mA each" is an intent with no clock, no voltage scale and no acceptance (DECLARED).
- **ST's rows** (DS12110 Rev 10, run mode from ITCM, PRINTED maxima; the order code does not fix the silicon revision, so both
  tables apply: rev Y Table 30, p.111; rev V Table 129, p.218). At 400 MHz with all peripherals enabled: rev Y 220, 400, 500 and
  840 mA at a junction of 25, 85, 105 and 125 C; rev V 256, 327, 416 and 536 mA. rv-pwr's HIGH, 400 mA, is rev Y's row at 85 C.
- **The controller's own limit.** LQFP100 45.0 C/W junction to ambient (Table 230, p.346), junction 125 C at most (Table 23,
  p.105), PRINTED. At L4-E12's inside air, 76.25 C (MODELED), the junction reaches 125 C at 0.328 A. Each state's operating point
  is the fixed point TJ = air + 45.0 C/W x 3.3 V x Imax(TJ), the maxima interpolated between their printed columns (MODEL): the
  400 MHz states have NO operating point at or under 125 C on either revision. Above 0.328 A the controller itself is outside its
  rating at this air, whatever regulator feeds it.
- **The other parts on each regulator.** Two TCAN334 (TI SLLSEQ7F 5.5, PRINTED): 7.0 mA recessive, 120 mA while both drive
  dominant bits, 360 mA with both buses faulted, against the 60 mA DECLARED for a supervisor's other parts.
- **The regulator as drawn**, AP2112K-3.3 (Diodes DS39724 Rev. 2-2): 600 mA capability, SOT25 184 C/W with no heat sink, junction
  150 C absolute maximum (PRINTED), thermal shutdown 160 C (TYPICAL). It drops its whole input to 3.3 V, so from +5V_IOC's 5.1329 V
  maximum its junction reaches 150 C at **0.2187 A** and 125 C at 0.1445 A. **The deficit is thermal before it is a current limit**,
  and wider than L9T5-F06 stated it in round 3.

| The demand on one regulator | A | Label | Junction as drawn (from 5.1329 V) | Junction with the pre-regulator (from 4.2907 V) |
|---|---|---|---|---|
| declared typical | 0.1200 | DECLARED | 116.7 C | 98.1 C |
| bounded: VOS3, HCLK at most 144 MHz, the larger revision at its operating point (0.1691 A at 101.4 C) plus the declared auxiliaries | 0.2291 (0.3091 while both transceivers drive dominant bits) | MODEL on PRINTED maxima and DECLARED auxiliaries | **153.5 C**, over the 150 C absolute maximum | **118.0 C** |
| the declared peak | 0.2500 | DECLARED | 160.6 C | 121.8 C |
| the case's HIGH (C-DEV rev 1's supervisors, rv-pwr) | 0.4600 | PRINTED row at TJ 85 C plus DECLARED auxiliaries; no operating point at this air | 231.4 C | 160.1 C, NOT COVERED |
| the worst nothing forbids (rev Y, 400 MHz, all peripherals, TJ 125 C) | 0.9000 | PRINTED row; no operating point at this air | 379.8 C, over the 600 mA capability as well | not covered |

**2b. Three corrections compared (t10 8).**

| | K1: a regulator per supervisor (a buck in place of each LDO, the AP63203WU-7 board B already fits as U25) | K2: a contract row that bounds the state (Layer 5's), the circuit as drawn | K3: the supervisors fed differently (U601 as a pre-regulator for the LDOs) |
|---|---|---|---|
| board A | none | none | one resistor value (R602 13.3 k) and the rail's declarations |
| board B | three bucks with an inductor, a bootstrap and two output capacitors each in the supervisors' pockets; switching ripple on each controller's VDD and VDDA | none | declarations only: no part, no net |
| U601's load | 0.5401 A bounded, 2.1218 A at the worst, against its 3 A (PRINTED) | as I-03's draft | the LDOs' own current: 1.3800 A at the case's HIGH |
| the lead's pin 1 | the same as U601's load | as I-03's draft | the same as U601's load |
| the regulator's junction at 76.25 C | 85.4 C bounded, 112.3 C at the worst (MODEL; efficiency 0.88 DECLARED, its 5 V curve NOT PLOTTED) | 153.5 C bounded: over the 150 C absolute maximum | 118.0 C bounded, 121.8 C at the declared peak, 160.1 C at the case's HIGH |
| what stays physical | the pockets' placement and routing, the ripple, the start | a firmware acceptance and a measured current | the LDOs' thermal resistance on board B's copper, U601's efficiency at this output, the LDOs' accuracy between dropout and 4.3 V (the sheet tests VOUT at 4.3 V and prints line regulation from 4.3 V) |
| does it hold alone | no: the controller has no operating point in the unbounded state, so K2's row is needed with it | no: the bound is needed and is not enough | no: it needs K2's row; with it, yes at the bounded state and the declared peak |

**2c. Selected (SESSION): K3 with K2's row as its condition.** The state must be bounded under every option, because the controller
itself has no operating point above it; with the bound the demand is 0.2291 A, which K2 alone does not hold (153.5 C) and K3
holds at 118.0 C on a one-resistor change in a draft this record already owns; K1 covers currents the controller cannot draw at
this air and costs three switching stages in board B's tightest area. To reverse: drop the two `iocpre` drafts (they are separate
from I-03's) and take K1; that becomes necessary if Layer 5 cannot bound the state or the bench reads the LDOs hotter than the
printed figure. Not the owner's: no requirement changes and nothing is bought. Layer 5's row is its owner's to accept.

The set point: R602 13.3 k is the least E96 value (R601 kept) that holds each LDO's input over its requirement at its full 600 mA
(3.7693 V: VOUT +1.5 %, load regulation 1 %/A, dropout 400 mV; PRINTED) after the rail's 2 % budget, the lead at three times
600 mA and the return's shift as drawn (0.0681 V, record l8r2): 4.1805 V nominal, 4.0711 to 4.2907 V, the LDOs' input at least
3.8428 V. The next value, 13.7 k, falls under the requirement (the test re-solves both).

**The acceptance criterion (T10), every condition required:**

1. **T10-A1** the contract carries a row that bounds each supervisor to VOS3 and HCLK at most 144 MHz (the least printed row over
   the 64 MHz the part is taken to start at, an ASSUMPTION: RM0433 is not held; the row's owner confirms the reset state is inside
   the bound), with only the peripheral clocks the board uses enabled, and a firmware acceptance: the clock tree and the voltage
   scale read back at start and refused otherwise; the printed figure for that state with the enabled set's own currents summed, or
   the supply current measured on the first article at a junction of at least 105 C. The row's text for its owner is in t10 8.
2. **T10-A2** at 76.25 C inside air and that state's demand (0.2291 A here) each regulator's junction is at most 125 C (SESSION
   criterion, 25 K under the absolute maximum) on its printed thermal resistance, and at its declared peak 0.25 A as well.
3. **T10-A3** each LDO's input stays over its requirement at its full 600 mA at the least set point with the return as drawn:
   3.8428 V against 3.7693 V (+0.0735 V).
4. **T10-A4** the draft composes in L4-E9's order after I-03's, its divider is read in the regenerated netlist with a mutation that
   fails, and the declarations it writes are read in the intent.
5. **T10-A5** PHYSICAL, on the first article: each LDO's case temperature at the bounded state in a 76 C chamber and each
   supervisor's supply current in that state; a supervisor forced out of the bound must end in the LDO's thermal shutdown or the
   controller's reset with the voters at their default (Layer 5's FMEA row, not shown here).

**The draft (t10 9).** `apply_gen_sch_a_iocpre.py` and `apply_gen_sch_b_iocpre.py`, release-guarded by `RELEASE-T10.md` (absent),
applied after I-03's drafts. Each refuses a target without I-03's draft, applies once after it, refuses a second application and
refuses the tree's generator. Composition in L4-E9's order: board A 21 drafts (792 parts), board B 13 drafts (1479 parts), every
step OK, the generators run to their end. Netlist: every check DRAWN with the T10 divider, the declarations DRAWN on their basis
(+5V_IOC 4.18 V, 1.3800 A peak; the three +3V3_IOCx at efficiency 0.79); the divider read as 56.2 k over 13.3 k, 4.1805 V. The
old state (board A composed without the T10 draft) FAILS the pre-regulator's check, and so does the mutation (the divider
inverted). Judged on C-DEV rev 1:

| Item | The figure | Against | The row |
|---|---|---|---|
| U7 | 6.0359 A, unchanged (the supervisors are on +5V_IOC either way) | 7.0957 A (PRINTED VSNS over the DECLARED shunt) | HOLDS |
| U601 and the lead's pin 1 | 1.3800 A at the case's HIGH (an LDO passes its output current) | 3 A and the VH's 10 A (PRINTED) | HOLDS |
| the LDOs' input | at least 3.8428 V; at most 4.2907 V | 3.7693 V; the AP2112's 6.0 V | HOLDS |
| the regulators' junctions at 76.25 C | 118.0 C bounded, 121.8 C at the declared peak; 160.1 C at the case's HIGH | 125 C (SESSION) | HOLDS only under T10-A1's bound; at the case's HIGH **NOT COVERED** |
| the return between the boards | the draft adds no load and no contact | section 0b, 1a | unchanged: CONDITIONAL on record l8r2's return |

T10-A1 (Layer 5's row) and T10-A5 (the bench) are met by nothing in this tree. U601 at 4.18 V is inside the TPS62933's printed
output range; its 6.8 uH inductor sits between the sheet's 3.3 V and 5 V rows (TYPICAL guidance) and its efficiency at this output
is not plotted.

**Findings for other authors (t10 10):** L9T5-F09 (Layer 5: the row and the FMEA row), L9T5-F10 (the net keeps the name +5V_IOC at
4.18 V), L9T5-F11 (Layer 6: R602's order code), L9T5-F12 (the budget's HIGH for the supervisors is a state with no operating point
at the hot stop's air; once Layer 5 accepts T10-A1 it is the bounded figure; a case row's input, not changed here), L9T5-F13 (the
declared 60 mA for a supervisor's other parts against two TCAN334's printed 120 mA dominant and 360 mA bus-fault currents),
L9T5-F14 (Layer 6: the order code admits silicon revisions Y and V).

## 0b. Round 4 (4 October 2026 night, from 23:15 CEST): the recheck V3's corrections, the return drafts composed

**The collaborator's targeted recheck V3 (cx41, an AI review of round 3 at `841e6c7e`): NOT CONFIRMED.** I-03 / L9P-F03 stays OPEN
and is credited only with U7's load relief and the compositions. Record l8r2's round 8 (`fnd/l8r4` at `c935542f`, merged here at
`927cdd1e`) enumerates every vertex of the contact-resistance box and drafts a dedicated return of three XT60 leads between boards
A and B; its two `gndrtn` drafts are in both orders of `l9t5_drafts.py` (board B's after `gndret`, board A's before `mainpb`).
This issue's two collaborator checks (cx40, cx41) are used: the next check reads the changed design. Figures: `l9t5_drafts.out`
("drafts N") and `l9t5_case.out` ("case N").

**1a. The connected path (drafts 6, B5): WITHDRAWN and restated.** Round 3 accepted `J_5V_IOC`'s pin 2 on record l8r2's round 7
rows (9.404 A, a sampled list whose largest was not the maximum) and said the acceptance did not depend on L8R2-F31. Both are
withdrawn. Read from record l8r2's round 8 output at its worst vertex (MODEL on PRINTED contact limits):

| The return | `J_5V_IOC`'s pin 2 on C-DEV rev 1 (76.25 C / -20 C) | At the declared upper bound | Against the VH's printed 10 A | The row |
|---|---|---|---|---|
| as drawn (old state O4) | **10.6376 / 12.0918 A** (the recheck's corner, 10.6375 A) | 14.1458 / 16.0796 A | over | **NOT MET** |
| with record l8r2's dedicated return composed | 2.9578 / 3.7056 A | 3.9333 / 4.9277 A | inside, and inside that record's least reading 5.9948 A at the inside air (ASSUMPTION) | **CONDITIONAL** |

Which row applies is read from the composed netlists (the sockets `J_GR1` to `J_GR3`, both contacts on GND, on both boards), never
typed. **The connected-path acceptance holds only with that return correction, whose drafts no independent check has read;
L8R2-F31 stays OPEN until its independent check**, and the conditions of that record's section 6d (the XT60's aged contact
resistance, no printed minimum resistances, no printed derating curves, the leads' assumed lengths) are its own. It is never a pass
on this record's evidence alone.

**1b. The AP2112K's requirement (drafts 6, B3).** Its +1.5 % output maximum is printed at 1 to 30 mA; with its printed load
regulation (+1 %/A maximum, at 0.46 A) and line regulation (+0.1 %/V maximum, from 4.3 V to U601's 5.1329 V) added, and the dropout
400 mV at 600 mA: **3.7674 V** (DS39724 Rev. 2-2 p.8; round 3's 3.7495 V was the simplified figure). The LDOs' input before the
ground shift is 4.7091 V, so the ground shift they allow is **0.9417 V**; the return's shift is at most 0.0512 V on the case and
0.0681 V at the upper bound as drawn, 0.0114 V with the dedicated return (record l8r2, MODEL).

**1c. Sequencing (drafts 6, item 7).** The netlist shows an enable RELATION: U601's EN is on RAIL_EN, and U7's EN is pulled to
+3V3, which U12 makes while RAIL_EN is high. That is connectivity, not timing. Round 3's "the supervisors are up whenever the
device rail is" is WITHDRAWN as stated. U601's and U7's starts, the LDOs' start into their loads and the recovery after a hiccup or
a brown-out are UNVERIFIED: a bench item (both rails and the three +3V3_IOCx captured at power-on, at RAIL_EN's release, and after
a short on +5V_IOC is removed).

**1d. The gauge's offset drift (case 2, U1).** TI BQ4050 SLUSC67B 6.14 (p.11) prints an offset error drift of 0.3 uV/K maximum
beside the gain drift; rounds 1 to 3 left it out. Over the same assumed 32 K it is 0.0048 A on the 2 mOhm shunt: the uncalibrated
sum is **0.8036 A** (was 0.7988 A), the case with the printed bounds needs **16.0718 V** (was 16.0684 V, the figure the case row's
rev 3 quotes: the row's quoted bound is the coordinator's to restate). F01 / D-17 is OPEN on either figure.

**1e. The case file.** `l9t5_case.py` pins `inputs/coordinator-cases-2026-10-04-rev3.md` and labels the computation C-ALLTX rev 3;
it reads rev 3's own printed case (241.039 W, 15.5162 V, +0.0162 V) and holds them equal to what it computes. Record l9pwr's out
7b carries the same label (its round 6, labels only). The load selection did not change.

**L8R2-F43 (drafts 6, B4):** JST prints no ambient and no derating for the VH's 10 A. On record l8r2's severest reading (the rating
taken at 25 C, an ASSUMPTION: 5.9948 A at the inside air) `J_5V_DEV`'s pin 1 at 6.0359 A is 0.0411 A over it and inside the printed
10 A (before the draft it carried 7.4717 A); `J_5V_IOC`'s pin 1 at 1.4749 A is inside both. It stays a named vendor item (record
l8r2's question to JST, UNSENT).

## 0a. Round 3 (4 October 2026 evening, from 20:15 CEST): board B's half composed with T5b, and L8R2-F35 answered

Record l8r2's round 7 (task T5b, `fnd/l8r4` at `04fa7a1d`) is in this tree since the merge at `43c9b49d`. Its two drafts `fandec`
and `gndret` let board B's composition run to its end, so board B's half of I-03 is composed, read and judged here as board A's
was. Every figure is printed by `l9t5_drafts.py` (`l9t5_drafts.out`, "drafts N"). Case rows: **C-DEV rev 1**, **C-ALLTX rev 3**.
**I-03 stays OPEN until the independent recheck V3 has read it; F01 / D-17 stays OPEN; A1 stays a selected direction.**
**Round 4 (section 0b) withdraws from this section:** B5's acceptance of pin 2 (9.404 A was a sampled figure, not the maximum),
the paragraph on what the acceptance depends on (its claim of no dependence on L8R2-F31), B3's 3.749 V requirement (3.7674 V with
the regulation terms) and the reading of the enable relation as sequencing. The text below is round 3's, kept as dated history.

| | (a) composes in L4-E9's order, the generator runs | (b) changed nets read, mutations fail | (c) electrical acceptance on C-DEV rev 1 |
|---|---|---|---|
| Board A (5 edits) | YES, in its place, first and last (drafts 3) | YES: DRAWN, three mutations FAIL; its declarations DRAWN on their basis (drafts 4) | **HOLDS** (drafts 6, items 1 to 8) |
| Board B (13 edits) | YES, with record l8r2's fandec and gndret, in its place, first and last; the tree before T5b still stops on GND's declared peak (old state O3) | YES: DRAWN, the pair with board A DRAWN, two mutations FAIL; its declarations DRAWN; record l8r2's own check of the return reads DRAWN on the same netlist and intent | **HOLDS for the draft's own parts and path** (drafts 6, B1 to B5); the shared return, record l8r2's finding **L8R2-F31, is OPEN beside it** |

**Board B's half on C-DEV rev 1 (drafts 6):**

- **B1** the move is drawn: no LDO input left on +5V_DEV, none allocated on the device lead, so U7's **6.0359 A against 7.0957 A**
  is the case with this board composed.
- **B2** the declarations stand on their basis: the device lead 6.0359 A declared against its own 6.035894 A; +5V_IOC 1.4749 A against
  1.474896 A (MODEL; round 2 declared a typed 6.0 A and 1.38 A, old state O2).
- **B3** the LDOs' input at the least: U601's 4.8719 V, less the rail's whole 2 % copper budget (0.100 V, DECLARED), less the lead's
  supply side at 1.4749 A (its conductor 2.520 mOhm at 76.25 C, MODEL, record l8r2 3c; two VH contacts at the after-test 20 mOhm,
  PRINTED: 0.0627 V), less the ground shift between the boards (record l8r2 3d's largest row at the case's total, 0.0512 V, MODEL on
  PRINTED maxima): **4.6580 V against the AP2112K-3.3's 3.749 V need, +0.9085 V**. It holds for any ground shift under 0.960 V.
- **B4** the lead, named: **16 AWG, 150 mm, VH crimp both ends**, the device lead's make (SESSION; `v2/docs/ASSEMBLY.md` section 4 and
  IF-AB-POWER's harness row). Its pin 1 carries 1.4749 A at most on the case and 5.15 A at U601's limit, against the VH's 10 A with
  AWG 16 on the standard header (PRINTED, JST VH catalogue p.1).
- **B5** its pin 2 is not its own rail's return: the whole A to B return divides by resistance over six VH contacts and seventeen
  ribbon conductors. Record l8r2's division at the case's total (MODEL at 76.25 C, scaled by 1.0019 for this round's figure): 2.793,
  1.748 and 1.205 A a lead with equal contacts; **9.404 A** at most in one lead (a BOUND: that lead's contacts at 0, the others at their
  initial maximum), within the VH's 10 A (PRINTED) and within record l8r2's 9.789 A comparator at the inside air (its 30 K
  ASSUMPTION). At the declared upper bound the same row reads 12.446 A and the ribbons pass their 1 A: that is L8R2-F31.

**What the acceptance depends on, and what it does not.** It depends on the LM5176's printed VSNS with R43's declared tolerance, the
TPS62933's printed rating and limits, the VH's printed 10 A at AWG 16 for the supply pin, the AP2112K's printed dropout, rv-pwr's
HIGH loads, the lead as named, and record l8r2's model of the return for pin 2 and the ground shift. It does **not** depend on, and
does not close, **L8R2-F31** (the A to B return is branched in parallel with nothing that sets its division; JST's note forbids
parallel branching above the rating). The draft adds a sixth VH contact to that return and no load to it; whatever corrects
L8R2-F31 changes pin 2's share and the ribbons', not items 1 to 8 or B1 to B4. L8R2-F31 is record l8r2's and stays OPEN.

**L8R2-F35, answered (drafts 7).** (a) "J_5V_DEV's return falls by the same current" (round 2) is **WITHDRAWN for pin 2**; it holds
for pin 1 only. (b) The lead is named in both drafts (B4). (c) The device lead's typed 6.0 A peak is corrected **from its basis**:
the case's own figure for the lead (Layer 9's budget at HIGH, every load at constant power at the least load voltage, the
supervisors gone: 29.5871 W at 4.9019 V), rounded up to 0.1 mA, **6.0359 A**; `check_l9t5_netlist.py`'s `decl()` refuses any other
figure, a typed 6.04 A included (it also refused this round's first +5V_IOC figure, typed 1.4750 A against 1.474896 A). Board A's
rail follows by stream s99's own construction, the lead plus the wall port's 0.9142 A: **6.9501 A**, 0.1456 A under U7's least loop
limit. +5V_IOC's peak by the same method at its own least load voltage 4.7719 V: **1.4749 A**. (d) fandec and gndret are in board
B's order.

**What round 3 corrects in rounds 1 and 2:** the return sentence; the two typed peaks ("the peak 6.0 A stays (it now overstates)"
was wrong: the lead's own case is 6.0359 A); U601's load is also judged at its own least load voltage (1.4749 A), where round 2
printed only what leaves U7 (1.4358 A at U7's 4.9019 V) and the LDOs' own 1.3800 A; the supervisors' 400 mA is ST DS12110 Rev 10
Table 30's maximum **at TJ 85 C** (p.111, read this round; the same row prints 840 mA at TJ 125 C); L601's Isat is a TYPICAL figure
(Coilcraft: the current for a 30 % inductance drop), which round 2 labelled PRINTED; board A's +5V_IOC allocation at `J_5V_IOC` is the
typical 0.36 A (it was the peak) and carries board A's 0.5 share of the rail's 2 %.

**Findings (drafts 8):** L9T5-F01 closed by record l8r2's round 7 drafts. **L9T5-F05** (record l8r2's author): on this merged tree
`l8r2_gndret.out` is regenerated, because it reads the tree's budget, which is now Layer 9's rounds 4 and 5 (the largest state
PS-BUSY 22.832 A, C-DEV's total 20.950 A); its page's section 3g still prints the earlier tree's figures, and its copy of this
record's draft is round 2's (the upper bound 27.78 A there, 27.9108 A with round 3's declarations); L8R2-F31 is unchanged.
**L9T5-F06** (Layer 5 and board B's owner): the supervisors' HIGH is the TJ 85 C figure; at TJ 125 C the row's 840 mA is over each
AP2112K's 600 mA; what bounds the H743's junction temperature, clock and peripheral state is not stated in a record read here.
**L9T5-F07** (Layer 7): an `ASSEMBLY.md` section 4 row for the new lead. **L9T5-F08** (Layer 5): IF-AB-POWER gains `J_5V_IOC` and the
device rail's rows restate (A 6.9501 A peak; B 6.0359 A peak arriving).

**SESSION decisions of round 3** (under the owner's standing rule of 26 September 2026; each with how to reverse it):
(1) `l8r2_gndret.out` regenerated through `regen_out` in the merge commit: record l8r2's own test requires the output to be what its
script prints on the tree; nothing else of record l8r2 is edited (reverse: take the file from `04fa7a1d`; its test then fails here).
(2) A declared peak is the case's own figure by the case's own method, rounded up to 0.1 mA, and is held to it by `decl()`
(reverse: change the basis in `l9t5_drafts.py` and the drafts' constants together). (3) Board A's device rail keeps stream s99's
construction (reverse: `DEV_PEAK` in the draft). (4) The lead is the device lead's make. (5) T5b's report is not filed in this
folder (it names a private path); the record's source is record l8r2 in this tree. (6) The README's claim table uses the brief's
label word for a maker's limit, which the record's hygiene test otherwise refuses as a claim word: the test exempts that label
cell only.

## 0. Round 2 (4 October 2026 evening, task T5 continued): I-03 checked on board A, A1's detector, L9P-F01 and C-PROT

Case rows: **C-ALLTX rev 3** (`inputs/coordinator-cases-2026-10-04-rev3.md`: rev 2's definition stands, its quoted 16.214 V is
withdrawn as D-11's basis; the case is this record's 15.5162 V, 16.0684 V with the printed bounds as rev 3 quotes it, 16.0718 V since round 4) and **C-DEV rev 1**. Every figure
below is printed by `l9t5_drafts.py` (`l9t5_drafts.out`, "drafts N") or `l9t5_a1.py` (`l9t5_a1.out`, "a1 N").

**I-03 (L9P-F03) on C-DEV rev 1: board A's half checked, board B's half UNCHECKED (round 2's state; round 3, section 0a, composes
board B and corrects the peaks and the return sentence below).** The three credit criteria, per board:

| | (a) composes in L4-E9's order, the generator runs | (b) changed nets read, mutations fail | (c) electrical acceptance on C-DEV rev 1 |
|---|---|---|---|
| Board A (`apply_gen_sch_a_iocbuck.py`, 4 edits) | YES: after 3g, before 3h's mainpb; first and last compose too (drafts 3) | YES: U601, L601, the divider, J_5V_IOC, the enable on RAIL_EN read DRAWN; three mutations FAIL (the lead reversed, EN on SS, the divider inverted) (drafts 4) | **HOLDS** (drafts 6) |
| Board B (`apply_gen_sch_b_iocbuck.py`, 13 edits) | **BLOCKED by T5b**: the composed generator stops on GND's declared 21.0 A peak against 21.51 A after record l8r2's fans12, with and without this draft | alone and in the composition without fans12 (DIAGNOSTIC, no credit): DRAWN, the pair with board A DRAWN; two mutations FAIL | UNCHECKED (the figures below are board B's too) |

Board A's acceptance, each figure labelled (drafts 6): U7 at **6.0359 A against its loop's least 7.0957 A, +1.0598 A** (MODEL load at
4.9019 V; VSNS 43 mV PRINTED; R43 6 mOhm +1 % DECLARED); U601 at **1.4358 A against its 3 A** (PRINTED, SLUSEA4D); its high-side
limit 4.2 / 5.0 / 5.8 A and low-side 2.9 / 3.8 / 4.5 A (PRINTED), the output at most about 5.15 A (Equation 11) and hiccup on a short,
under J_5V_IOC's VH **10 A** (PRINTED); L601's Isat 9.2 A over 5.8 A (PRINTED); +5V_IOC 5.002 V nominal, **4.872 to 5.133 V**, at least
4.701 V at the LDOs after the declared 2 % and 1.5 % budgets against the AP2112K-3.3's 3.749 V need and under its 6.0 V maximum (PRINTED,
DS39724); RAIL_EN with U601's EN pull-up added 4.890 V at 16.8 V and 5.227 V at 18 V against EN's 5.5 V recommended maximum (Ip and Ih
TYPICAL only, U601 adds 0.0589 V); the enable relation read in the netlist (+5V_DEV is up only while +3V3 is, and U601 is on RAIL_EN);
the upstream path: VBAT's declared loads unchanged in sum, C-ALLTX rev 3 unchanged at the declared 0.90 for U601 as for U7 (the
TPS62933's own 5 V curve is NOT PLOTTED), +0.0073 V if U601 were at 0.85 (a bound shown).

Negative checks of this solution: **one** (board B's round 1 text, kept in `inputs/apply_gen_sch_b_iocbuck-bdbed9bb.py`, refused alone:
"intent: bypass C400 -> U40.1: the capacitor is not on that pin's net +5V_DEV"; round 2 adds the missed edit). **I-03 stays OPEN**
until T5b's branch lands; then drafts 4 runs the full composition again with no other change, and V3 reads the completed correction.

**What T5b needed (round 2's text, corrected):** the lead J_5V_IOC's pin 1 carries the three LDOs' rail: 0.36 A typical (DECLARED),
1.4358 A of U7's case (MODEL, constant power at U7's least voltage) or 1.3800 A (the LDOs' own current at rv-pwr's HIGH), 0.3930 A at
C-ALLTX rev 3. Round 2 said the same current returns through its pin 2 instead of J_5V_DEV's: **WITHDRAWN in round 3** (section 0a,
B5: the return divides by resistance over every ground conductor between the boards). GND's declared loads change by **0.00 A** (the
three allocations leave +5V_DEV's derived ground loads and return as `_IOC_LOADS`); GND gains J_5V_IOC as a source.

**L9P-F01, restated** (record l9pwr round 5, its out 10): OPEN on the case, 15.5162 V against REQ-018's 15.5 V; D-11's 16.214 V a
labelled scenario; L4-E9 round 7's 16.1 V, its rule's 16.4 V and FAN_OK printed as withdrawn.

**L9T5-F04, for C-PROT rev 1's consumers** (record l9stk, T1, T2, T4, V1, V2; reported, nothing of theirs edited): the gauge's
uncalibrated one-sided current error, **0.8036 A** (BQ4050 SLUSC67B 6.14's gain error, INL and offset PRINTED; R10's 1 % an ASSUMPTION;
the drift over an assumed 32 K span; out 2), exceeds the **0.32 A** between the indicated 18 A service and the breaker's least trip
**18.32 A** (C-PROT rev 1, record l9stk 15.4). An under-reading gauge at an indicated 18 A lets the true current reach 18.80 A, inside
the breaker's band, so C-PROT's "18 A for 60 s never interrupted" holds for the true current only if the gauge is calibrated (0.1736 A,
with a 0.2 % reference, an ASSUMPTION, fits the gap) or the firmware's indicated limit sits the gauge's error under 18 A. Which one is
C-PROT's owners' choice (record l9stk with Layer 5's FW-A05).

**A1's detector (a1 2 to 4): none prints a limit, so A1 stays a SELECTED DIRECTION, not drafted.** Four makers' sheets were read,
held back by their terms (`fetch_held_back.py`, sha256-checked, never committed): ADI ADL5902 (Rev. B), ADI ADL5513 (Rev. B), TI
LMH2110 (SNWS022D), ADI LTC5582 (Rev. D). Every temperature row near 144 to 146 MHz sits in the Typ column; none is printed at the
band. On typical data the ADL5902 takes 0.30 dB of the 0.5 dB tier (the worse of its 100 and 700 MHz rows, an ASSUMPTION that it holds
between them) and runs from 4.5 V, over board D's +5V_D8 floor 4.3408 V (record s99a); the ADL5513 runs from 3.3 V and takes 0.43 dB,
leaving 0.07 dB for the sampler, the set point and the amplifier; the LMH2110 takes 0.5 dB; the LTC5582 prints nothing below 450 MHz;
none fits the 0.25 dB tier. **SESSION decision:** "a printed accuracy that supports the tolerance" is read as a printed LIMIT, because a
typical figure says nothing of a unit's spread and the loop exists to bound the case's power (reverse: if typical data is read as
enough, the ADL5513 on +3V3_D8, or the ADL5902 with D-A1's supply, is drafted TYPICAL and CONDITIONAL on P-A1). The named items:

- **V-A1 (vendor question, drafted, UNSENT):** to Analog Devices, product support for the ADL5902: "For the ADL5902 (data sheet Rev. B),
  Table 1 gives the deviation vs. temperature at 100 MHz and 700 MHz as typical values (-0.11/+0.25 dB and +0.3/-0.2 dB at 0 dBm,
  -40 C to +85 C). We intend to use the part in a closed power-control loop at 144 to 146 MHz with about 0 dBm at the input. (1) Is
  there a specified limit (a minimum and a maximum), or a characterized distribution (mean and standard deviation, or a 3-sigma bound), of the deviation vs.
  temperature at that frequency and level? (2) Is the part characterized for operation at a 4.34 V supply? (3) If neither, which ADI
  RF power detector specifies its temperature deviation at 144 to 146 MHz as a limit?" (sent only by the owner).
- **P-A1 (physical):** the loop's specimen over the kit's temperature range, its output deviation measured against a reference power
  meter, the detector's drift tabulated per unit if firmware is to compensate it (board D already reads the PA's flange temperature,
  U22); with the bench row already owed, the module's drain current at the loop's high end at 13.8 V.
- **D-A1 (design, after V-A1 or P-A1):** a supply of at least 4.5 V for a 5 V detector on board D, or a 3.3 V part with the margin.
- **For the coordinator, not drafted (materially different):** the loop could sense the PA's DC input on board A, where U14 (an INA226
  on +13V8_PA) gives gain error and offset as maximum values; it bounds the case's own quantity, needs a path from board A to VGG on board
  D, and leaves the RF output to the module's efficiency.

F01 / D-17 stays **OPEN** on C-ALLTX rev 3; L9P-F04 stays with A1.

**Other findings (drafts 8):** L9T5-F01 (T5b): board B's composition stops on GND's declared peak, the same stop without this
record's draft. L9T5-F02 (d8dec31's mainpb, R-194; L4-E9's row 33): with this draft before it, mainpb takes R603 and C607, after it
R248 and C247; row 33's text names R233 and C241, which set 29's tree already moves; fixed references would remove the dependency.
L9T5-F03 (board B's generator owner, cosmetic): U40, U50 and U60's value text still reads "its own branch off the device rail"; left,
because the z-stack tables key on value texts.

**SESSION decisions of round 2** (under the owner's standing rule of 26 September 2026; each reversible by editing the named line):
(1) board A's draft after L4-E9's 3g and before 3h's mainpb (the docstring's place; first and last also compose); (2) record l8r2's
d8v3 and vbus20ov compose in board A's round in l8r2's own order, as records l8r2 and l8p compose them, though L4-E9's list does not
name them; (3) the TPS62933's IFB taken either way in the set-point band (its sign is not printed; stream s99a's method); (4) U601's
efficiency at the board's declared 0.90 (as U41), 0.85 shown as a bound; (5) the printed-limit reading above; (6) the four detector
sheets held back (a `.gitignore` line for `v2/vendor/adi/held/`); (7) board B's LDO value text left unchanged (L9T5-F03).

## 1. The budget defect, corrected (record l9pwr round 4)

- **C1:** rv-pwr's PS-ALLTX powered the standby WiFi card (1.0 W PLAN, 9.1 W HIGH); REQ-018's acceptance and CONOPS 4a's row
  define the state with it off. The raw PS-ALLTX HIGH row on DRAFTED goes from **276.373 W (17.4792 V)** to **265.274 W
  (16.8626 V)**; PS-ALLTX at the pack from 174.23 / 209.89 / 292.03 W to 174.23 / 208.47 / 279.63 W.
- **Out 7b of the budget computes C-ALLTX rev 2 from its text**, each pack-fed converter at the VBAT the case sets (13.391 V at
  18 A; the budget's convention had been rv-pwr's 16.8 V).

## 2. The case row (out 1)

| | W | |
|---|---|---|
| the cells' EMF at 18 A from 15.5 V rest | 279.000 | |
| the cells, R_cell 0.060 Ohm (ASSUMPTION), 0.0800 Ohm | 25.920 | MODEL |
| the pack path, 0.038064 Ohm | 12.333 | R_DIST 7.290, R17 1.620, the breaker 1.140, the battery FETs 2.283 |
| **the allowance at VBAT** | **240.747** | the challenge's 240.747 W, reproduced |
| the load pins | 220.741 | |
| conversion | 20.298 | the 5.1 V LM5176 stages 9.160, the PA and HF stages 2.245, LDOs 1.229, the fans' converters 2.997, the rest 4.667 |
| **the case at VBAT** | **241.039** | |
| **the deficit** | **+0.292 W, +0.0162 V** | **needs 15.5162 V rest at 18 A** |

**The row's quoted figure is not its text.** "On Layer 9's final drafts this case needs 16.214 V rest (253.61 W at VBAT)" is
D-11's basis on rv-pwr's `typ_nontx` (16.2145 V, 253.608 W), which puts only the compute modules and the NVMe at typical. The
row's text puts every other non-transmit load at typical too; the loads that differ are listed in record l9pwr's out 7b (the
supervisors, the hubs' cores, the QMX's USB and HDMI, board E's controller, the Geiger). This page computes the text and keeps
the basis beside it as a labelled scenario; **a revision of the row is the coordinator's**.

## 3. The uncertainties the row names (out 2)

| Item | Label | Its bound | Needs |
|---|---|---|---|
| U1 the gauge's indication against the indicated 18 A (BQ4050 SLUSC67B 6.14: gain error 0.8 % FSR, INL 22.3 LSB, offset 10 uV, gain drift 150 ppm/K and, since round 4, offset drift 0.3 uV/K; R10's 1 % an ASSUMPTION) | PRINTED and ASSUMPTION | 0.8036 A one-sided uncalibrated (the gain error alone 0.4860 A, the challenge's figure); 0.1736 A calibrated | 16.0546 V; 15.8348 V; 15.6276 V |
| U2 R_cell (35E Ver. 1.1 7.4 prints 35 mOhm INITIAL AC only) | ASSUMPTION | the row covers 0.0593 Ohm | 15.7562 V at 0.070, 15.9962 V at 0.080 |
| U3 the path (the dock's contacts at their printed 20 mOhm are 10.0 mOhm forward and return, against W2's 9 mOhm inferred for every lead and contact) | PRINTED and MISSING | +1.0 mOhm at least; 18.0 mV a mOhm | 15.5342 V |
| U4 the PA stage at 13.8 V and the 5.1 V stages' 0.90 | NOT PLOTTED | the PA at 0.95; the 5.1 V stages at 0.85 | 15.7479 V; 15.8190 V |
| U5 the rest voltage's fall during the 60 s (0.30 Ah, 2.99 % of a cell's 3.35 Ah) | MISSING (R-214) | no curve held | not bounded |

**Combined**, U1 uncalibrated with U3 and R_cell 0.060 Ohm: 241.169 W at 17.1964 A, **needs 16.0718 V (+0.5718 V)** (16.0684 V before round 4's offset-drift term, the figure the case row's rev 3 quotes); with R_cell
0.070 Ohm and U4's lower efficiencies also, 16.8532 V. The printed gauge bound alone moves the case further than its deficit.

**Labelled scenarios (out 3):** the compute modules at 8 W, 252.840 W and 16.1718 V; D-11's basis at the case's VBAT, 253.032 W
and 16.1825 V.

## 4. Three service-neutral approaches (out 4)

| | What it changes | The case with the printed bounds (U1, U3) | Touches | Evidence owed |
|---|---|---|---|---|
| **A1** the VHF PA held to its 30 W service by its maker's own output control | a forward-power detector and a VGG loop on board D (today VGG is set open-loop to 4.30 to 4.68 V, so nothing holds Pout under the module's 45 W rating; the budget's 113 W is 45 W at the printed minimum 40 %) | at +-0.25 dB the PA 84.15 W: 14.3494 V; at +-0.5 dB 94.42 W: **14.9616 V**; at +-1 dB 118.87 W: 16.4195 V (fails) | board D, Layer 5's PA contract, the PA's RF checks; L9P-F04 closes with it | the module's drain current at the loop's high end at VDD 13.8 V (the maker prints 40 % at 30 W only as its heat-sink design condition at 12.5 V, IDD 0.84 + 5.16 A, 75.0 W); the detector's printed accuracy |
| **A2** the pack path's resistance | copper, contacts, a fourth battery FET | the whole path is worth 0.6852 V; the nominal deficit is 0.901 mOhm; the printed bound needs 33.253 mOhm, more than the path can lose | boards A, E, P, the energy chain | the leads' and bands' resistance (MISSING) |
| **A3** the LDO-fed rails onto bucks | the supervisors, the KSZ's 2.5 V, board E's 3.3 V | 15.4674 V nominal; 16.0207 V with the bound | boards B and E, the supervisors' supply | the bucks' points (NOT PLOTTED at 3.3 V) |

**T6's copper in volts:** the two options carry the same section (2.74 mm2 a band: 39.14 mm a face at 1 oz, 19.57 mm at 2 oz),
so either is worth 0 V against the other as sized; each 100 mm of band, forward and return, hot, is 1.582 mOhm, 28.5 mV at 18 A
(MODEL); the lengths are the layout's. A fourth BUK6Y10-30P is worth 31.7 mV (and Ciss, E11-37). The 5.1 V stages' efficiency is
not an approach: no maker figure supports a better one.

**A1's acceptance (the loop's accuracy binds):** half-tolerance at most 0.5 dB over temperature closes the case with the printed
bounds (R_cell to about 0.084 Ohm); at most 0.25 dB also covers the 8 W modules (15.0345 V), D-11's basis (15.0456 V) and R_cell
0.080 Ohm with U4's lower efficiencies (15.3095 V).

## 5. C-DEV rev 1 and L9P-F04 (out 5)

The case: U7 at 7.4717 A at 4.9019 V (every load at constant power) against 7.0957 A (R43 6 mOhm at +1 %, VSNS 43 mV); the loop's
highest 9.5960 A against J_5V_DEV's JST-VH 10 A.

- **(a) a re-rated path:** R43 at most 5.6981 mOhm supplies the case and at least 5.7576 mOhm keeps the loop's highest at 10 A:
  no value does both (the challenge's Q4, reproduced). It needs a single contact over the loop's highest and a lead whose rating
  covers it; **the lead's rating is not held**.
- **(b) the load split:** the three supervisors' LDOs (U40, U50, U60, board B) move from +5V_DEV to a new always-on 5.1 V buck on
  board A (a TPS62933, 3 A PRINTED, high-side limit 4.2 / 5.0 / 5.8 A PRINTED) on its own JST-VH lead. U7's case becomes
  **6.0359 A against 7.0957 A (+1.0598 A)**; the buck carries 1.4358 A; its limit stays under the lead's 10 A.
- **SELECTED (SESSION): (b)**, every figure printed, U7's limit and lead unchanged. Its condition: the buck follows RAIL_EN as U7
  does (L4-E11's U46 hold), so the supervisors are up whenever +5V_DEV is.
- **L9P-F04:** the PA rail at 8.1884 A against U13's 7.0957 A; with A1 at +-0.5 dB or tighter it is 6.842 A or less, no shunt or
  lead change.

## 6. The selection

- **F01 / D-17: A1** (SESSION, within authority: no requirement, money or claim changes; the kit's VHF stage is a 30 W stage).
  It is the only one of the three that closes the case with the printed bounds. **CONDITIONAL** on the PA's bench row and on a
  detector whose sheet prints the loop's accuracy; **not drafted** (no detector part is held, the loop is not designed). No
  owner decision is needed.
- **I-03: (b)**; **L9P-F04: with A1.**
- **For C-PROT (record l9stk's, reported only):** the gauge's uncalibrated one-sided error (0.8036 A) exceeds the 0.32 A between
  the 18 A service and the breaker's least limit 18.32 A; an under-reading gauge lets the true current reach that limit while it
  indicates under 18 A. Calibrated (0.1736 A) it is under the gap.
- **Open:** F01 / D-17 and I-03 until a draft composes with its board's pending drafts, its nets are read in the regenerated
  netlist with a mutation that fails, its acceptance holds on its case, and the collaborator's targeted check (V3) reads it;
  U5 (R-214); the PA's bench row; the case row's quoted figure.

## 7. Reproduce

`python3 v2/docs/records/l9t5/l9t5_case.py` from the repository root (stdlib, PyYAML, pdftotext; it imports record l9pwr's budget,
pinned). Round 2: `python3 v2/docs/records/l9t5/l9t5_drafts.py` (record l8p's `gen_netlist.py`, no KiCad; about ten seconds) and,
after `python3 v2/docs/records/l9t5/fetch_held_back.py`, `python3 v2/docs/records/l9t5/l9t5_a1.py`. Each output is regenerated only
through `_bin/regen_out.py`, in the order l9pwr_budget, l9t5_case, l9t5_drafts, l9t5_t10, l9t5_cm5, l9t5_a1. Round 4:
`python3 v2/docs/records/l9t5/l9t5_t10.py` (it imports `l9t5_drafts.py` and composes both boards with the T10 drafts) and
`python3 v2/docs/records/l9t5/l9t5_cm5.py`. Test: `v2/ecad/tools/tests/test_l9t5.py` (the A1 survey's test needs the four held
sheets).
