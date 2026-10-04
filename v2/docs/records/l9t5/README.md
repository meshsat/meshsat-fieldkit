**ROUND 4, PARTS 0 AND 1 DONE (4 October 2026 night):** the collaborator's targeted recheck V3 (an AI review) read round 3 and returned NOT CONFIRMED. **I-03 stays OPEN and is credited only with U7's load relief and the compositions.** Record l8r2's round 8 is merged (`927cdd1e`) and its dedicated-return drafts are composed on both boards. The connected path (the lead's pin 2 and the return between the boards) reads NOT MET as drawn (10.6376 A at 76.25 C, 12.0918 A at -20 C against the VH's printed 10 A) and CONDITIONAL with that return (at most 4.9277 A), on a draft no independent check has read; L8R2-F31 stays OPEN. Round 3's claim that the acceptance does not depend on L8R2-F31 is withdrawn, with its sequencing sentence; the AP2112K's requirement is 3.7674 V; the gauge's bound is 16.0718 V with the offset drift; the case file pinned is rev 3. F01 / D-17 stays OPEN; A1 is not drafted. Open `L9T5-CASES.md` section 0b, then the claim table below.

# l9t5: task T5, C-ALLTX rev 3 and C-DEV rev 1 (Layer 9's power author, MESHSAT-1357)

4 October 2026, worktree `l9t5` on branch `fnd/l9t5` from set 29's line `dc99897f`. Prototype design, desk arithmetic: nothing
has been built, powered or measured. This folder takes the case row C-ALLTX rev 2 from record l9pwr's budget (round 4, out 7b),
bounds the uncertainties the row names, compares three service-neutral approaches to F01 / D-17, and selects a correction for I-03
(C-DEV rev 1) and L9P-F04. It edits no generator, registry, requirement or other record's file, and it drafts nothing yet.

| File | What it is |
|---|---|
| `L9T5-CASES.md` | The page: the budget defect corrected, the case row and its parts, the uncertainty table, the three approaches, C-DEV's two options, the selection, what stays open |
| `l9t5_case.py` | The script, from the repository root: `python3 v2/docs/records/l9t5/l9t5_case.py` (stdlib, PyYAML, pdftotext). It imports `v2/docs/records/l9pwr/l9pwr_budget.py` unchanged, pins every input by sha256, parses every maker's figure from its sheet and refuses when one is not found |
| `l9t5_case.out` | Its output, committed, regenerated only through `_bin/regen_out.py`, after `l9pwr_budget.out` (0 the pins; 1 the case row; 2 the uncertainties; 3 the labelled scenarios; 4 the approaches; 5 C-DEV and L9P-F04; 6 the selection; 7 the predicates) |
| `inputs/` | The coordinator's case rows (rev 2 and, round 2, rev 3) and the collaborator's challenge cx40, filed as received; board B's round 1 draft text and both round 2 draft texts (the old states), each with its sha256 in `inputs/SOURCES.txt` |
| `apply_gen_sch_a_iocbuck.py`, `apply_gen_sch_b_iocbuck.py` | I-03's drafts for boards A and B (NOT RELEASED: each refuses the tree's generator until a `RELEASE.md` names an accepted check); round 3: the peaks declared from their basis, the lead named |
| `check_l9t5_netlist.py` | What the regenerated netlists must show (DRAWN, NOT DRAWN, FAIL), parsed with record l8p's reader; round 3: `decl()`, the declarations held to their basis |
| `l9t5_drafts.py`, `l9t5_drafts.out` | Rounds 2 and 3: each draft alone, the compositions in L4-E9's order (board B with record l8r2's round 7 drafts), the regeneration (record l8p's `gen_netlist.py`), the old states that must stop or fail, five mutations, the intent beside its basis, the acceptance on C-DEV rev 1 for both boards, L8R2-F35 answered, the state and the findings |
| `fetch_held_back.py`, `l9t5_a1.py`, `l9t5_a1.out` | Round 2: A1's detector survey over four makers' sheets held back by their terms (fetched and sha256-checked, never committed) |

Test: `v2/ecad/tools/tests/test_l9t5.py` (`env -C v2/ecad/tools python3 tests/run.py test_l9t5`).

## The result in short

- **C-ALLTX rev 3 from its text needs 15.5162 V** at 18 A (241.039 W at VBAT against the 240.747 W allowance: **+0.292 W**). Rev 2's
  quoted 16.214 V, withdrawn by rev 3, is D-11's basis, which keeps the non-transmit loads at HIGH.
- **The printed bounds dominate:** the gauge's uncalibrated error alone (0.8036 A) takes the need to 16.0546 V; combined with the
  dock contacts' printed maximum, 16.0718 V (round 4: the gauge's offset drift included; 16.0684 V before).
- **Selected for F01 / D-17: A1**, the VHF PA held to its 30 W service by a VGG loop on board D (the maker's own output control);
  with the loop at +-0.5 dB the case with the printed bounds needs 14.9616 V, at +-0.25 dB the 8 W modules and D-11's basis pass as
  well. CONDITIONAL on the PA's bench row and a detector with a printed accuracy; not drafted.
- **Selected for I-03: (b)**, the three supervisors' LDOs on their own TPS62933 buck: U7 at 6.0359 A against 7.0957 A. **L9P-F04
  closes with A1.**
- Reported for C-PROT: the gauge's uncalibrated error exceeds the 0.32 A between the service and the breaker's least limit.

## Round 4 in short

- **V3: NOT CONFIRMED.** Credit kept: U7's load relief (6.0359 A against 7.0957 A) and both compositions. Everything else is restated
  below or stays open.
- **The merge:** `fnd/l8r4` at `c935542f` into this branch at `927cdd1e`; one conflict, record l8r2's `l8r2_gndret.out`, taken from
  its side and regenerated (already identical). `gndrtn` is in both orders.
- **1a** the connected path: NOT MET as drawn, CONDITIONAL with record l8r2's unchecked return; the independence claim withdrawn.
  **1b** the AP2112K's requirement 3.7674 V, the allowed ground shift 0.9417 V. **1c** the enable relation is connectivity; the
  sequencing is an unverified bench item. **1d** the gauge's offset drift: 0.8036 A, 16.0718 V. **1e** the case file pinned and
  labelled rev 3.

## Round 3 in short

- **The merge:** `fnd/l8r4` at `04fa7a1d` into this branch at `43c9b49d`. One conflict, `l9pwr_budget.out`, kept from this side and
  regenerated; this record's three outputs and record l8r2's `l8r2_gndret.out` regenerated on the merged tree (finding L9T5-F05).
- **Board B's half:** composes with record l8r2's fandec and gndret; DRAWN; two mutations FAIL; HOLDS on C-DEV rev 1 for the draft's
  own parts and path (the LDOs' input 4.6580 V against 3.749 V; pin 1 at most 1.4749 A and pin 2 at most 9.404 A in record l8r2's
  rows, against the VH's 10 A). **L8R2-F31 stays OPEN beside it.**
- **L8R2-F35:** answered; the device lead's peak 6.0359 A, board A's rail 6.9501 A and +5V_IOC 1.4749 A are held to their basis by
  `decl()`; the lead is 16 AWG, 150 mm.

## The claim table for the independent recheck V3

Each claim rounds 1 to 3 changed or added, with its file, its source and its state. Labels (the round 3 brief's): the first is a
maker's limit printed in a minimum or maximum column (the outputs' PRINTED); **typical** a maker's typical figure; **declared** a
figure a generator, a contract or a record states (a SESSION choice included); **model** arithmetic of this or another record on the
figures named; **assumed** a figure no held document gives. "case" is `l9t5_case.out`, "drafts" `l9t5_drafts.out`, "a1"
`l9t5_a1.out`, "budget" `../l9pwr/l9pwr_budget.out`. Nothing is built or measured; no row is a measurement.

| Id | Claim | File | Source (document, revision, page) | Label | State |
|---|---|---|---|---|---|
| C01 | PS-ALLTX carries the standby WiFi card off | budget out 1 (C1), 7b | `pcb_requirements.yaml` REQ-018's acceptance; CONOPS 4a's PS-ALLTX row | declared | corrected in round 1 (l9pwr round 4); not independently checked |
| C02 | C-ALLTX rev 3 from its own text: 241.039 W at VBAT, 15.5162 V needed at 18 A; the script pins and labels the rev 3 case file (round 4, V3's blocker 5) | budget 7b; case 1 | the budget's loads (rv-pwr `pwr_budget.py`, each load's own source) at the case's VBAT 13.391 V; `inputs/coordinator-cases-2026-10-04-rev3.md` | model | F01 / D-17 OPEN (+0.0162 V over REQ-018's 15.5 V) |
| C03 | R_cell 0.06 Ohm in C02 | case 2 (U2) | Samsung INR18650-35E specification Ver. 1.1, 7.4 (p.5): 35 mOhm initial AC impedance only | assumed | open (U2); 0.07 / 0.08 Ohm shown as scenarios |
| C04 | the gauge's uncalibrated current error 0.8036 A at 18 A (0.7988 A before round 4's offset drift term, V3's blocker 4); alone the case then needs 16.0546 V | case 2 (U1) | TI BQ4050 SLUSC67B 6.14 (p.11): gain error 0.8 % FSR, INL 22.3 LSB, offset 10 uV, gain drift 150 ppm/K, offset drift 0.3 uV/K; R10's 1 % and the 32 K span | guaranteed (the five printed terms); assumed (R10's tolerance, the span) | bounded; with the dock contacts' maximum 16.0718 V (the case row's rev 3 quotes 16.0684 V: the coordinator's to restate) |
| C05 | L9T5-F04: that error exceeds the 0.32 A between the 18 A service and the breaker's least 18.32 A | case 6; page 0 | C04; record l9stk 15.4 (C-PROT rev 1) | model | finding for C-PROT's consumers; theirs to act on |
| C06 | L9P-F01 judged on the case; D-11's 16.214 V a labelled scenario; 16.1 V, 16.4 V and FAN_OK withdrawn | budget 10 | C02; the owner's positions of 4 October 2026 (the common brief) | model | restated in round 2 (l9pwr round 5); OPEN on the case |
| C07 | A1: the PA held to 30 W by a VGG loop closes the case with the printed bounds at +-0.5 dB (14.9616 V) | case 4 | Mitsubishi RA30H1317M1 (Oct. 2011): Pout 30 W min and total efficiency 40 % min (p.2), 45 W rating (p.2), output control by VGG and the heat-sink example (p.8) | model on guaranteed figures | SELECTED DIRECTION, not drafted; the bench row (drain current at the loop's high end) open |
| C08 | no detector sheet read prints its temperature deviation near 144 to 146 MHz as a limit | a1 2 to 4 | ADI ADL5902 Rev. B Table 1 (p.3); ADI ADL5513 Rev. B (p.3; supply p.6); TI LMH2110 SNWS022D (p.6); ADI LTC5582 Rev. D (p.2); held back, `fetch_held_back.py` | typical | A1 not drafted; V-A1 (UNSENT), P-A1, D-A1 named |
| C09 | board D's +5V_D8 floor 4.3408 V is under the ADL5902's 4.5 V minimum | a1 3 | record s99a `codec_floor.out` (its worst row); ADL5902 Rev. B (supply 4.5 to 5.5 V) | model; guaranteed (the supply range) | stands |
| C10 | C-DEV rev 1 before: U7 7.4717 A against its loop's least 7.0957 A; no 1 % R43 serves both the case and the VH's 10 A | case 5 | TI LM5176 SNVSAI1D (p.7): VSNS 43 / 50 / 57 mV; `gen_sch_a.py` R43 6 mOhm 1 %; JST VH catalogue (p.1) | model on guaranteed and declared figures | I-03 OPEN; option (b) selected |
| C11 | with the drafts U7 carries 6.0359 A against 7.0957 A (+1.0598 A), whatever the supervisors draw | drafts 6 (1), (B1) | C10; the composed netlists (no LDO input on +5V_DEV) | model | checked by its author on both boards; V3 owed |
| C12 | scenario, not the case: with the wall port at U32's limit 6.9501 A against 7.0957 A (+0.1456 A) | drafts 6 (1) | `gen_sch_a.py` VBUS_WALL 0.9142 A (TPS2596 equation 7, SLVSET8A p.28, nominal) | model on a declared figure | labelled scenario |
| C13 | the supervisors' HIGH: each H743 400 mA plus 60 mA; 1.3800 A of LDO current | drafts 6 (2) | ST DS12110 Rev 10 Table 30 (p.111): 400 MHz, VOS1, all peripherals enabled, maximum at TJ 85 C (840 mA at TJ 125 C); rv-pwr `pwr_budget.py` (the 60 mA) | guaranteed (by characterization, the table's note 2); declared (60 mA) | read this round; scenario and finding L9T5-F06 for the TJ 125 C row |
| C14 | U601 carries at most 1.4749 A (constant power at its own least load voltage 4.7719 V) against its 3 A | drafts 6 (2) | TI TPS62933 SLUSEA4D (p.1, 3 A); C13; C17 | model against a guaranteed rating | holds |
| C15 | U601's output is limited to about 5.15 A, under the lead's 10 A; hiccup on a short | drafts 6 (3) | SLUSEA4D 8.5 (pp.6 and 7): IHS_LIMIT 4.2 / 5.0 / 5.8 A, ILS_LIMIT 2.9 / 3.8 / 4.5 A; 9.3.12 and Equation 11 (pp.24 and 25, "approximately") | guaranteed (the limits); model (Equation 11) | holds |
| C16 | L601's Isat 9.2 A is over the 5.8 A limit | drafts 6 (4) | Coilcraft XAL60xx series sheet (p.1, note 5: a 30 % inductance drop, typ) | typical | holds; round 2's label corrected |
| C17 | +5V_IOC's set point 5.002 V nominal, 4.8719 to 5.1329 V | drafts 6 (5) | SLUSEA4D 8.5 (p.6): VFB 784 / 800 / 816 mV over TJ -40 to 150 C, IFB 0.15 uA maximum; the divider 56.2k over 10.7k at 0.1 %, 25 ppm/K over 65 K (stream s99a's pair) | model on guaranteed and declared figures | holds |
| C18 | RAIL_EN stays under EN's 5.5 V with U601's EN added (5.227 V at 18 V) | drafts 6 (6) | SLUSEA4D 8.5 (p.6): Ip 0.7 uA, Ih 1.4 uA, typical only; 8.3 and 8.1 (p.5): EN 5.5 V recommended, 6 V absolute; `gen_sch_a.py` R2 100k over R184 39k | typical (Ip, Ih); guaranteed (EN's limits); declared (the divider) | holds on typical pull-up currents |
| C19 | an enable RELATION: U601's EN is on RAIL_EN; U7's EN is pulled to +3V3, which U12 makes while RAIL_EN is high. Round 3 read it as "the supervisors are up whenever the device rail is": WITHDRAWN (V3's blocker 3) | drafts 4 (A EN), 6 (7) | the regenerated netlist of the composed board A | declared (generator text read on a netlist) | drawn; mutation 2 fails; the rails' start-up and recovery timing is UNVERIFIED, a bench item |
| C20 | C-ALLTX rev 3 is unchanged by the move at U601's declared 0.90; +0.0073 V at 0.85 | drafts 6 (8) | the draft's declared efficiency (as U41's); SLUSEA4D plots no 5 V curve for the TPS62933 | declared; assumed (the 0.85 bound) | holds; the 5 V efficiency a bench item |
| C21 | the composed netlists read DRAWN on both boards and the pair; five mutations FAIL | drafts 4 | record l8p's `gen_netlist.py` on the composed generators (no KiCad) | declared (generator text read on a netlist) | drawn; the box's KiCad export is the reading of record |
| C22 | board B composes only with record l8r2's fandec and gndret; the tree before them stops on GND's 21.0 A | drafts 3, 4 (O3) | record l8r2 round 7 (`04fa7a1d`, merged at `43c9b49d`) | declared | holds |
| C23 | the device lead's declared peak is 6.0359 A (29.5871 W at 4.9019 V, rounded up), not a typed 6.0 A | drafts 5, 6 (B2), 7 (c); both drafts | C11's basis; record l8r2's finding L8R2-F35 | model; declared (the draft) | corrected in round 3; held by `decl()` |
| C24 | board A's +5V_DEV peak is 6.9501 A (the lead plus the wall port's 0.9142 A) | drafts 5, 7 (c); board A's draft | stream s99's construction (`gen_sch_a.py` note); C23 | declared | corrected in round 3 |
| C25 | +5V_IOC's declared peak is 1.4749 A on both boards; 0.36 A typical; board A's share 0.5 of the 2 % | drafts 5; both drafts | C13, C17 | model; declared | corrected in round 3 (was 1.38 A) |
| C26 | the lead J_5V_IOC is 16 AWG, 150 mm, VH crimp both ends | drafts 6 (B4), 7 (b); both drafts | `v2/docs/ASSEMBLY.md` section 4 (the device lead's row); `pcb_interfaces.yaml` IF-AB-POWER's harness row | declared (SESSION) | named in round 3; its rows in ASSEMBLY.md and the contract are their owners' (L9T5-F07, F08) |
| C27 | the lead's pin 1 carries at most 1.4749 A, 5.15 A at the limit, against the VH's 10 A | drafts 6 (B4) | JST VH catalogue (p.1): 10 A with AWG #16 on the standard header | model against a guaranteed rating | holds |
| C28 | the LDOs' input is at least 4.7091 V before the ground shift; the AP2112K needs 3.7674 V (3.7495 V in round 3 was the simplified figure, V3's blocker 2); the ground shift allowed is 0.9417 V | drafts 6 (B3) | C17; the rail's 2 % budget; record l8r2 3c (2.520 mOhm at 76.25 C); JST VH catalogue (p.1): contact resistance 20 mOhm after test; Diodes AP2112 DS39724 Rev. 2-2 (p.8): VOUT +1.5 % at 1 to 30 mA, load regulation 1 %/A and line regulation 0.1 %/V maxima, dropout 400 mV at 600 mA; (p.3) VIN 6.0 V | model on guaranteed, declared and another record's model figures | holds: the return's shift is at most 0.0681 V as drawn and 0.0114 V with the return (record l8r2) |
| C29 | "J_5V_DEV's return falls by the same current" | drafts 7 (a); page 0 | record l8r2 rounds 7 and 8 (the return divides by resistance) | model | WITHDRAWN for pin 2 in round 3; holds for pin 1 |
| C30 | J_5V_IOC's pin 2 at its worst vertex on the case: 10.6376 A (76.25 C) and 12.0918 A (-20 C) as drawn; 2.9578 and 3.7056 A with record l8r2's dedicated return, 4.9277 A at most at the upper bound. Round 3's 9.404 A was a sampled figure: WITHDRAWN | drafts 6 (B5) | record l8r2 `l8r2_gndret.out` round 8, sections 3d, 6b and 7 (every vertex enumerated); JST VH catalogue (p.1): 10 A, contact resistance maxima, no minimum | model (another record's, on printed contact limits); assumed (its least reading 5.9948 A, the leads' lengths) | as drawn NOT MET; with the return CONDITIONAL on that unchecked draft; L8R2-F31 OPEN |
| C31 | the draft adds no load to board B's GND declaration and one lead contact; GND's derived peak 27.9108 A, its sources the six leads and the three return sockets | drafts 5 | the composed intent (record l8r2's gndret derives it; its round 8 prints the same 27.9108 A) | declared | holds |
| C32 | record l8r2's round 8 output reads its own copies of this record's round 3 files; merged here it regenerates identical | `../l8r2/l8r2_gndret.out` | record l8r2 round 8 (`c935542f`, merged at `927cdd1e`) | model (another record's) | L9T5-F05 answered by that round |
| C33 | the connected-path acceptance of I-03 holds only with a supported correction of the return between the boards; round 3's claim that the acceptance does not depend on L8R2-F31 is withdrawn | drafts 6 (the connected path, what it depends on), 8 | the recheck V3 (cx41, as received in `../l8r2/checks/astra-check-t5-recheck-cx41.md`); C30 | model | CONDITIONAL; never a pass on this record's evidence; the next independent check reads record l8r2's return with these drafts |
| C34 | which return row applies is read from the composed netlists: J_GR1 to J_GR3 with both contacts on GND on both boards (DRAWN), absent without the return drafts (old state O4) | drafts 4; `check_l9t5_netlist.py` `return_drawn()` | the regenerated netlists (record l8p's `gen_netlist.py`) | declared (generator text read on a netlist) | drawn on both boards |
| C35 | J_5V_DEV's pin 1 at 6.0359 A is inside the VH's printed 10 A and 0.0411 A over record l8r2's severest least reading (5.9948 A at the inside air); J_5V_IOC's pin 1 at 1.4749 A is inside both | drafts 6 (B4), 7 (e) | record l8r2 round 8 3f, its finding L8R2-F43; JST VH catalogue (p.1): no ambient, no derating printed | model against a guaranteed rating; assumed (the 25 C reading) | a condition of the device lead; the JST question is record l8r2's, UNSENT |

## Round 2 in short

- **I-03:** board A's half checked (composition, netlist with three failing mutations, acceptance on C-DEV rev 1: HOLDS); board B's half
  UNCHECKED, blocked by T5b; I-03 OPEN until T5b lands and V3 reads it. T5b's input: the draft adds 0.00 A to board B's GND loads and a
  fifth source J_5V_IOC carrying 0.36 A typical, 1.4358 A at C-DEV.
- **L9P-F01:** restated on C-ALLTX rev 3 in record l9pwr round 5 (15.5162 V against 15.5 V; D-11's 16.214 V a labelled scenario).
- **L9T5-F04 for C-PROT:** the gauge's 0.8036 A uncalibrated error against the 0.32 A between 18 A and the breaker's 18.32 A.
- **A1:** no detector sheet prints its temperature deviation as a limit; A1 stays a selected direction (V-A1 drafted UNSENT, P-A1, D-A1).

## What other authors own (reported, nothing of theirs edited)

- The coordinator: the case row C-ALLTX rev 2's quoted figure (16.214 V) against its text (15.5162 V on the text).
- Board D's generator (A1's loop), board A's and board B's generators (I-03's buck, its lead and the LDOs' inputs), Layer 5 (the PA's
  output-control contract; the buck's enable with RAIL_EN).
- Record l9stk and C-PROT's consumers: the gauge's calibration against the breaker's 0.32 A gap.
- L4-E9: D-17's figures follow the case row once its revision is fixed; R-214 (U5) is its bench row.
