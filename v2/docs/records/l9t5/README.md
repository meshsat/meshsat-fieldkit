SELECTION CORRECTED: after Astra's cx44 (NOT SUPPORTED, the first negative of (c), kept as given) correction (c) stays first-ranked as a PROVISIONAL choice: the PA drain-current cap 6.3521 to 6.9258 A (printed terms alone 6.3892 to 6.8940 A), U13's BIAS moved ahead of R55, C-ALLTX rev 3 at the cap's top needs 15.1308 V (MODEL margin 0.3692 V), the 30 W service under the cap rests on the maker's 6.0 A EXAMPLE and is the supplier's feasibility task B-PA1; F01 / D-17 PROVISIONAL, never closed on printed limits (l9t5_f01.out sections 4 to 7). DONE: 1a, 1b round 2. NOT DONE: 1c (the drafts and the check are being revised to round 2's design), 1d, parts 2 and 4 (part 3 moved to another author). NEXT: 1c on the corrected design. Carried from round 4 (T10 is Slot C's, on fnd/p0t10): T10 (L9T5-F06, the supervisors' regulators): STAYS OPEN, a DRAFTED CANDIDATE, unchecked; L9T5-F13, F16 and F17 OPEN; no case row is changed.

(Round 4's status line, kept:) **ROUND 4 DONE, PARTS 0 TO 3 (4 October 2026 night):** the collaborator's targeted recheck V3 (an AI review) read round 3 and returned NOT CONFIRMED. **I-03 stays OPEN and is credited only with U7's load relief and the compositions.** Record l8r2's round 8 is merged (`927cdd1e`) and its dedicated-return drafts are composed on both boards. The connected path (the lead's pin 2 and the return between the boards) reads NOT MET as drawn (10.6376 A at 76.25 C, 12.0918 A at -20 C against the VH's printed 10 A) and CONDITIONAL with that return (at most 4.9277 A), on a draft no independent check has read; L8R2-F31 stays OPEN. Round 3's claim that the acceptance does not depend on L8R2-F31 is withdrawn, with its sequencing sentence; the AP2112K's requirement is 3.7674 V; the gauge's bound is 16.0718 V with the offset drift; the case file pinned is rev 3. **T10 (L9T5-F06, the supervisors' regulators): STAYS OPEN.** Its conditions are verified from the sources (the supervisors' state is bounded by no document; the deficit is thermal, the AP2112K's junction passing its 150 C absolute maximum at 0.2187 A from the 5 V rail), three corrections are compared, one is selected as a DRAFTED CANDIDATE, unchecked (SESSION: U601 as a 4.18 V pre-regulator, with Layer 5's row bounding the state as its condition) with the acceptance criterion T10-A1 to A5, and its circuit half is drafted, composed and read on the netlists; no independent check has read it and Layer 5 has not accepted its row. The held-dominant and CAN-fabric-fault rows are judged on their own limits (125 C in a served state, 150 C in any; the typical 160 C shutdown never an acceptance; MODEL junctions) and all FAIL: L9T5-F13, F16 and F17 OPEN, F16 and F17 covered by no requirement (finished on 5 October 2026 in the morning by a fresh author, after the owner's instructions of that morning). **SDR3-F02 (the CM5's 2.5 A): confirmed as a finding;** a supply design figure, assessed as labelled scenarios and a bound on the slot stages (L9T5-F15); no case row is changed. F01 / D-17 stays OPEN; A1 is not drafted. Open `L9T5-CASES.md` sections 0d, 0c and 0b, then the claim table below (C36 onward is new for the next check).

## P0 round, Slot A (5 October 2026, branch `fnd/p0pwr` from `fnd/p0base` = e132db0e)

The owner's instruction of 5 October 2026 14:20 (P0 power closure) and the coordinator's common brief govern this round. Nothing is
built, bought, powered or measured; every circuit change below is a release-guarded draft.

**1a, reproduced.** `l9t5_case.py` run on this base prints byte-identical output: C-ALLTX rev 3 needs 15.5162 V nominal (241.039 W at
VBAT) and 16.0718 V with the printed uncertainties bounded, against REQ-018's 15.5 V. The PA's DC input the bounded case allows is
103.44 W (today's HIGH 113.0 W, the 45 W rating at the 40 % printed minimum): the deficit sits in the one number an open-loop VGG leaves
unbounded.

**1b, round 2 (after Astra's advisory challenge cx44 of 15:53, F01 SELECTION: NOT SUPPORTED, the first negative of (c), kept as given
in `inputs/cx44-astra-f01-selection-as-received.md`; its ten blockers answered one by one in `l9t5_f01.out` section 7).** The comparison
is redone on one standard: (a) and (c) each rest on an unprinted transfer of the PA's behaviour, so each is at most a PROVISIONAL choice
(the owner's part 19, amendment 1 point 2).

| Option | What it bounds | The case with the printed bounds | Verdict |
|---|---|---|---|
| (a) A1, the RF loop with a per-unit calibrated detector | RF output | rests on the PA's efficiency at the loop's high end (36.5 % at +-0.5 dB) and on a detector residual no sheet bounds: two supplier tasks, one on the failing case | ranked second |
| (b) the BQ4050 calibrated per pack | the gauge's term | a perfect gauge still needs 15.5342 V | cannot close alone |
| **(c) a PA drain-current cap** | **the case's quantity (DC watts at a regulated rail)** | **cap 6.3521 to 6.9258 A (MODEL on PRINTED terms with TYPICAL allowances; printed alone 6.3892 to 6.8940 A); the PA at most 97.24 W; 15.1308 V, MODEL margin 0.3692 V** | **SELECTED, PROVISIONAL on B-PA1 (the 30 W service) and B-PA2 (the dynamics)** |

Round 2's design changes (cx44): U13's BIAS (its gate drive bounded at 0.1141 A, more than the room under U13's limit) is re-tapped from
+13V8_PA to PA_OUT, ahead of R55; the set point carries a 1 mA preload (R551 2.80k over R552 549 Ohm, the TLV758P's IOUT = 1 mA test
condition); the set point is held at 0 V while OUTLET_OK is high and ramps at each key (R559 1k, C557 10 uF), so the RF drive (K1, 3 ms
maximum) arrives under a low set point and the current approaches the cap from below; R560 470k winds the held integrator down; board D's
VGG gets a 10k bleed (R58), because U15 cannot sink. The 6.0 A at 30 W is the maker's heat-sink EXAMPLE at the printed minimum efficiency
(25 C, 12.5 V, VGG 5 V, full drive); its transfer to the kit's terminals and envelope is an ASSUMPTION, and B-PA1 decides it.

**Selection (authority: SESSION; ruled_by: Slot A under the owner's standing rule of 26 September 2026, the ruling of 21 September 2026
and part 19; ruled_on: 5 October 2026).** (c), PROVISIONAL. Why: it bounds the failing case's own quantity on the labelled terms and
leaves the service on one supplier task; (a) leaves both the case and the service on unprinted behaviour. **L9P-F04** is corrected in the
steady state on bounded figures (the cap's top and R55's other loads 0.1076 A under U13's least 7.0338 A, the shunt hot at 105.0 C with
its printed TCR). **Withdrawn:** round 1's "lower-VGG-wins RF loop" fallback. **If B-PA1 fails** the arrangement fails, not a
requirement: routes R1 (U13's limit and the cap raised, the bounded case allows 7.3674 A) and R2 (the PA rail at 12.5 V with VGG to 5 V).
**Reversal:** not applying the drafts.

**Open after 1b (round 2):** F01 / D-17 PROVISIONAL on B-PA1 (feasibility of the 30 W service under the cap: specimen three RA30H1317M1, IDD at 30.0 W at most 6.352 A less the lab's expanded uncertainty, terminal VDD 13.17 and 14.04 V, 144 to 146 MHz, flange 25 and 85 C, air -20 C, 50 Ohm and 3:1) and B-PA2 (the loop's settling, excursions under a load step, the pack current against l9stk's E-10); 1c's draft, composition, mutations and acceptance owed; U5 (R-214) MISSING against a MODEL margin of 0.3692 V.
acceptance on C-ALLTX rev 3, and an independent check reads it; B-PA1 and B-PA2 (physical, confirm); U5 (R-214, the rest voltage's fall
in the 60 s) MISSING, against which the case has 0.2981 V.

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
| `l9t5_t10.py`, `l9t5_t10.out` | Round 4, task T10 (finding L9T5-F06): the supervisors' applicable operating conditions from the sources, the demand as a range, the regulator's thermal limit, three corrections compared, the selection with its acceptance criterion T10-A1 to A5, Layer 5's row text, the T10 drafts composed, read on the netlists and judged on C-DEV rev 1 (1 the pins; 2 the state; 3 ST's rows; 4 the junction; 5 the other parts; 6 the demand; 7 the regulator as drawn; 8 the corrections; 9 the draft; 10 the state and the findings; 11 the predicates) |
| `apply_gen_sch_a_iocpre.py`, `apply_gen_sch_b_iocpre.py` | T10's drafts (NOT RELEASED: each refuses the tree's generator until a `RELEASE-T10.md` names an accepted check; each applies only after I-03's draft): R602 13.3 k and the declarations at 4.18 V on board A, declarations only on board B |
| `l9t5_cm5.py`, `l9t5_cm5.out` | Round 4, part 3: finding SDR3-F02 assessed: the CM5 sheet's supply design figure read from the held file, the slot stages, C-ALLTX rev 3 and the budget's states at that figure as labelled scenarios; no case row changed |
| `l9t5_f01.py`, `l9t5_f01.out`, `l9t5_paloop.py` | P0 round (5 October 2026), part 1b round 2: F01 / D-17 reproduced and three corrections compared on C-ALLTX rev 3, (c) selected PROVISIONAL (1 the case; 2 (a); 3 (b); 4 (c); 4b the connected consequences; 5 the selection; 6 the supplier's tasks; 7 cx44's blockers; 8 the predicates); `l9t5_paloop.py` holds the cap's design values and its labelled band for every script |
| `apply_gen_sch_a_paloop.py`, `apply_gen_sch_d_paloop.py`, `check_f01_netlist.py` | P0 round, part 1c (IN PROGRESS at this checkpoint: being revised to round 2's design) |
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
- **Part 2, T10 (L9T5-F06): STAYS OPEN, first attempt at its correction.** The supervisors' state is bounded by no contract row,
  panel text or firmware; ST prints up to 840 mA (rev Y, 400 MHz, all peripherals, TJ 125 C), a state with no operating point at
  the 76.25 C inside air (the controller's own junction reaches 125 C at 0.328 A). The regulator's limit is thermal: 150 C at
  0.2187 A from the 5 V rail, so it is over its absolute maximum at the bounded demand (0.2291 A, 153.5 C) and at the case's own
  HIGH (0.46 A). Three corrections compared; **selected (SESSION), a DRAFTED CANDIDATE, unchecked: U601 as a 4.18 V pre-regulator
  (R602 13.3 k) with Layer 5's row bounding the state (VOS3, HCLK at most 144 MHz) as its condition**: 118.0 C bounded, 121.8 C
  at the declared peak (MODEL), against a 125 C criterion. The case's HIGH (160.1 C) is NOT COVERED. Rows judged on their own
  limits (125 C in a state the design must serve, 150 C in any; the typical 160 C shutdown never an acceptance), all MODEL
  junctions, all FAIL: both transceivers driving dominant, held, 132.6 C (**L9T5-F13 OPEN**); one CAN fabric faulted, 144.2 C on
  all three regulators, a served fault state no requirement covers (**L9T5-F16 OPEN**, Layer 5's owner); both faulted, 176.3 C,
  over the 150 C absolute maximum, no requirement covers it (**L9T5-F17 OPEN**, Layer 5's owner). T10-A5 no longer accepts the
  shutdown as a fault's end.
  Acceptance T10-A1 to A5; the two `iocpre` drafts compose after I-03's and read DRAWN; the state before them and an inverted
  divider FAIL.
- **Part 3, SDR3-F02: confirmed as a finding.** The CM5 sheet's "5 V at up to 2.5 A" is a supply design figure (appendix B.3), not
  a consumption limit; Table 9 prints typical figures only. At 12.5 W a module the slot stages hold steadily (+0.7441 A on slots 1
  and 3) and pass the loop's least when a cooler's bounded start coincides (-0.3546 A): L9T5-F15. C-ALLTX rev 3 at that figure is
  a labelled scenario (17.0148 V); **no case row is changed.**

## Round 3 in short

- **The merge:** `fnd/l8r4` at `04fa7a1d` into this branch at `43c9b49d`. One conflict, `l9pwr_budget.out`, kept from this side and
  regenerated; this record's three outputs and record l8r2's `l8r2_gndret.out` regenerated on the merged tree (finding L9T5-F05).
- **Board B's half:** composes with record l8r2's fandec and gndret; DRAWN; two mutations FAIL; HOLDS on C-DEV rev 1 for the draft's
  own parts and path (the LDOs' input 4.6580 V against 3.749 V; pin 1 at most 1.4749 A and pin 2 at most 9.404 A in record l8r2's
  rows, against the VH's 10 A). **L8R2-F31 stays OPEN beside it.**
- **L8R2-F35:** answered; the device lead's peak 6.0359 A, board A's rail 6.9501 A and +5V_IOC 1.4749 A are held to their basis by
  `decl()`; the lead is 16 AWG, 150 mm.

## The claim table for the independent recheck V3

Each claim rounds 1 to 3 changed or added, with its file, its source and its state; **round 4's parts 0 and 1 restated C02, C04, C07,
C19 and C28 to C32 and added C33 to C35; C36 onward are round 4's parts 2 (T10) and 3 (SDR3-F02), C56 to C60 the rows judged on their own limits, for the next independent check,
which reads the changed design.** Labels (the round 3 brief's): the first is a
maker's limit printed in a minimum or maximum column (the outputs' PRINTED); **typical** a maker's typical figure; **declared** a
figure a generator, a contract or a record states (a SESSION choice included); **model** arithmetic of this or another record on the
figures named; **assumed** a figure no held document gives. "case" is `l9t5_case.out`, "drafts" `l9t5_drafts.out`, "a1"
`l9t5_a1.out`, "t10" `l9t5_t10.out`, "cm5" `l9t5_cm5.out`, "budget" `../l9pwr/l9pwr_budget.out`. Nothing is built or measured; no row is a measurement.

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
| C36 | no contract row, panel text or firmware in the tree bounds a supervisor's run mode, clock or voltage scale; the architecture's 60 mA a supervisor is an intent | t10 2 | `HW-FW-CONTRACT.md` (11 rows name the supervisors, none bounds the state), `PANEL.md`, `ARCH-PCB-B-IOHA.md` (Power), `gen_sch_b.py`, `v2/firmware` (the panel's only) | declared | the state is UNBOUNDED; finding L9T5-F09 for Layer 5 |
| C37 | ST's run-mode maxima, both silicon revisions (the order code fixes neither): at 400 MHz with all peripherals rev Y 220, 400, 500, 840 mA and rev V 256, 327, 416, 536 mA at a junction of 25, 85, 105, 125 C; rv-pwr's HIGH (400 mA) is rev Y's row at 85 C | t10 3 | ST DS12110 Rev 10, Table 30 (p.111) and Table 129 (p.218) | guaranteed (maximum columns; the sheet's note: characterization results, two cells tested in production) | read; finding L9T5-F14 for Layer 6 (the revision) |
| C38 | the controller's own limit: LQFP100 45.0 C/W, junction 125 C; at 76.25 C inside air it reaches 125 C at 0.328 A; the 400 MHz states have no operating point at or under 125 C on either revision | t10 3, 4 | DS12110 Rev 10 Table 230 (p.346), Table 23 (p.105); L4-E12's E5 dwell for the air | guaranteed (thermal resistance, junction); model (the fixed point, the maxima interpolated between printed columns; the inside air) | the worst printed state is not one the controller can hold at this air |
| C39 | the demand on one regulator as a range: 0.1200 A declared typical; 0.2291 A bounded (VOS3, HCLK at most 144 MHz, 0.1691 A at the operating point of the larger revision, plus 0.060 A of other parts); 0.4600 A the case's HIGH; 0.9000 A the worst nothing forbids | t10 6 | as C37 and C38; `gen_sch_b.py` and rv-pwr for the other parts | model on guaranteed maxima; declared (the other parts' 60 mA) | a range, because nothing bounds the state |
| C40 | two TCAN334 on each regulator: 7.0 mA recessive, 120 mA while both drive dominant bits, 360 mA with both buses faulted, against the 60 mA declared for a supervisor's other parts | t10 5 | TI SLLSEQ7F section 5.5 | guaranteed | finding L9T5-F13 (a momentary and a fault figure the declarations do not carry) |
| C41 | the regulator as drawn is thermally limited: from +5V_IOC's 5.1329 V maximum its junction reaches 150 C at 0.2187 A and 125 C at 0.1445 A; 153.5 C at the bounded demand, 231.4 C at the case's HIGH | t10 7 | Diodes DS39724 Rev. 2-2 (p.3: SOT25 184 C/W with no heat sink, junction 150 C absolute maximum; thermal shutdown 160 C) | guaranteed (thermal resistance, junction); typical (shutdown); model (the junction at the inside air) | NOT MET as drawn; L9T5-F06 restated wider (thermal before the 600 mA limit) |
| C42 | three corrections compared: K1 a buck a supervisor (85.4 C bounded, 112.3 C at the worst; U601 0.5401 and 2.1218 A); K2 the contract row alone (153.5 C: does not hold); K3 U601 as a pre-regulator (118.0 C bounded) | t10 8 | Diodes DS41326 Rev. 3-2 (AP63203: 2 A, TSOT26 89 C/W); as C41 | model; declared (K1's efficiency 0.88, its 5 V curve not plotted) | compared; none holds without the state bounded |
| C43 | selected: K3 with K2's row as its condition, a DRAFTED CANDIDATE, unchecked; to reverse, drop the two `iocpre` drafts and take K1 | t10 8 | the comparison C42 | declared (a SESSION selection) | selected, not the owner's (no requirement changes, nothing bought); Layer 5's row is its owner's to accept |
| C44 | the set point: R602 13.3 k is the least E96 value that keeps each LDO's input over 3.7693 V at its full 600 mA with the return as drawn: 4.1805 V nominal, 4.0711 to 4.2907 V, at least 3.8428 V at the LDOs (+0.0735 V); 13.7 k falls under | t10 8; `test_l9t5.py` re-solves both values | TI SLUSEA4D (VFB band), DS39724 p.8 (VOUT +1.5 %, load regulation 1 %/A, dropout 400 mV at 600 mA); record l8r2 round 8 for the return's shift (0.0681 V) | guaranteed (VFB, VOUT, regulation, dropout); declared (the rail's 2 % budget, the resistors' tolerance); model (the return's shift) | holds (T10-A3) |
| C45 | with the pre-regulator (a drafted candidate, unchecked) the regulator's junction is 118.0 C at the bounded demand and 121.8 C at its declared peak 0.25 A, against a 125 C criterion; 160.1 C at the case's HIGH; every figure a MODEL junction | t10 8, 9 (4) | as C41; the criterion is 25 K under the absolute maximum | model on a guaranteed thermal resistance; declared (the 125 C criterion, SESSION) | holds only under T10-A1's bound; at the case's HIGH NOT COVERED; the held dominant and fabric-fault rows FAIL their bounds (C57 to C59) |
| C46 | the acceptance criterion T10-A1 to A5: the contract row and its firmware acceptance; the junction at the bounded demand; the LDOs' input; the composition, netlist and mutation; the first article's temperatures and currents | t10 8 | the owner's instruction of 4 October 2026, part 7 | declared | A2, A3 and A4 shown at the desk; A1 (Layer 5's row) and A5 (the bench) met by nothing in the tree |
| C47 | the T10 drafts: each refuses a target without I-03's draft, applies once after it, refuses twice and refuses the tree's generator; board A composes with 21 drafts (792 parts), board B with 13 (1479 parts); the netlist's divider is 56.2 k over 13.3 k; the state before the draft and the inverted divider FAIL | t10 9; `check_l9t5_netlist.py` `DIVS` | the regenerated netlists (record l8p's `gen_netlist.py`), the intent | declared (generator text read on a netlist) | composed and read by its author only; not released |
| C48 | on C-DEV rev 1 with the draft: U7 unchanged at 6.0359 A against 7.0957 A; U601 and the lead's pin 1 at 1.3800 A against 3 A and 10 A; the LDOs' input 3.8428 to 4.2907 V inside the AP2112's 2.5 to 6.0 V | t10 9 (1) to (3) | TI SNVSAI1D (VSNS), SLUSEA4D, JST VH catalogue, DS39724 | model against guaranteed limits; declared (the shunt, the loads) | holds |
| C49 | the AP2112's accuracy between its dropout and 4.3 V is not printed: the sheet tests VOUT at 4.3 V and prints line regulation from 4.3 V; the input here is 3.8428 to 4.2907 V | t10 8 (K3, physical) | DS39724 Rev. 2-2, the electrical characteristics' conditions | assumed (inside the printed supply range, outside the tested line range) | a physical item (T10-A5); a reason to reverse to K1 if the bench reads it out |
| C50 | U601 at 4.18 V out is inside the TPS62933's output range; its 6.8 uH inductor sits between the sheet's 3.3 V row (4.7 uH) and 5 V row (6.8 uH); its efficiency at this output is not plotted | t10 9 (2) | TI SLUSEA4D p.1, Table 10-2 | guaranteed (the output range); typical (the table's guidance) | holds on the range; the efficiency is a physical item |
| C51 | L9T5-F06 stays OPEN: conditions verified, correction selected with its criterion, circuit half drafted; no independent check, no Layer 5 acceptance, nothing applied; the first attempt at this correction | t10 10 | the constitution's sections 4 and 5 | declared | OPEN |
| C52 | the CM5 sheet prints 'Power supply designs should accommodate 5 V at up to 2.5 A' in appendix B.3 and typical figures only in Table 9 (idle 400 mA, operation 900 mA; no maximum column filled) | cm5 2 | Raspberry Pi CM5 datasheet, Release 3 (`v2/vendor/cm5/cm5-datasheet.pdf`) | typical (Table 9); assumed (B.3 read as an upper figure: printed advice, in no minimum or maximum column) | a supply design figure, not a consumption limit; SDR3-F02 confirmed as a finding |
| C53 | the slot stages with each module at 12.5 W: steady 6.3516 A against 7.0957 A on slots 1 and 3 (+0.7441 A), +1.5292 A on slot 2; with a cooler's bounded start 7.4503 A (-0.3546 A) on slots 1 and 3; with a degraded cooler +0.0251 A | cm5 3 | budget (the stage rows, L9P-F02); TI SNVSAI1D (VSNS 43 mV minimum) over the 6 mOhm shunt; record l8r2's start bound | model on a guaranteed VSNS and declared loads; assumed (the module's figure, C52) | a bound: steady inside, the start coinciding outside; finding L9T5-F15 |
| C54 | C-ALLTX rev 3 is not changed: the case 15.5162 V (modules at typical); labelled scenarios 16.1718 V at the budget's HIGH (8.0 W) and 17.0148 V at the maker's figure (12.5 W) | cm5 4 | budget 7b (`case_vals`, `case_row`, unchanged) | model; assumed (the module's figure, C52) | a labelled scenario; whether the row quotes it is the coordinator's |
| C55 | board B's slot branches sum to 4.751 A against a declared peak of 5.00 A (slot 2: 5.63 A); with the module at 2.5 A they sum to 5.651 A, over the 5.100 A that slots 1 and 3's declaration may carry | cm5 3 | `gen_sch_b.py` (`_SLOT_LOADS`, the slot rails' declaration) | declared | a finding for board B's generator owner; nothing drafted |
| C56 | three limits kept apart: 125 C T10's design criterion; 150 C the AP2112K's absolute maximum junction, never exceeded and never a target; 160 C its thermal shutdown, typical behaviour only, no maximum trip printed, never an acceptance. A row over 125 C in a state the design must serve, or over 150 C in any state, FAILS its thermal bound; every junction figure is a MODEL result | t10 7, 8 | Diodes DS39724 Rev. 2-2: Absolute Maximum Ratings (p.3), the AP2112-3.3 table (p.8); the owner's instruction of 5 October 2026 relayed by the coordinator | guaranteed (150 C); typical (160 C); declared (125 C, SESSION) | applied to every row below |
| C57 | (m) both transceivers driving dominant, held: 0.3091 A, 132.6 C MODEL with the pre-regulator (180.5 C as drawn); in T10's scope; FAILS 125 C at the held figure. The driver's dominant time-out ends a held TXD after 1.2 to 3.8 ms, but no row bounds a supervisor's transmit share (FW-B09 bounds the rate), and T10-A2 is judged at the declared 0.020 A a transceiver | t10 8 (m), 10 | TI SLLSEQ7F 5.5 (p.6), tTXD_DTO and its note 1, 6.3.7 (p.20); `HW-FW-CONTRACT.md` FW-B09 | guaranteed (the supply rows, the time-out); declared (the 0.020 A, the rate); model (the junction) | L9T5-F13 OPEN (Layer 5; board B's generator owner and rv-pwr) |
| C58 | (f1) one CAN fabric faulted, its transceiver driving dominant into the fault (TXD = 0 V, CANH = -12 V, RL open), the other recessive: 0.3726 A, 144.2 C MODEL on each of the three regulators (201.9 C as drawn); a fault state outside T10's scope that the design must serve (IOHA row 7, test A7); FAILS 125 C, under 150 C; no requirement covers this fault state (REQ-073 covers the other direction, REQ-004's acceptance does not name A7) | t10 8 (f1), 10 | SLLSEQ7F 5.5 (p.6); `ARCH-PCB-B-IOHA.md` sections 12 and 13; `pcb_requirements.yaml` REQ-004, REQ-073 | guaranteed (the fault row); declared (the requirements, the FMEA); model (the junction) | L9T5-F16 OPEN (Layer 5's owner); what closes it: the drive into the fault ended before 125 C with the service lost stated |
| C59 | (f2) both fabrics faulted: 0.5491 A, 176.3 C MODEL on each of the three regulators (261.4 C as drawn); a double fault outside T10's scope (IOHA row 8, A7); FAILS 150 C; no current reaches the 600 mA capability, the typical shutdown is no acceptance; no requirement covers this fault state | t10 8 (f2), 10 | as C58; DS39724 (p.3, p.8) | guaranteed (150 C, 600 mA); typical (160 C); model (the junction) | L9T5-F17 OPEN (Layer 5's owner); what closes it: each regulator's input held off or its current limited before 150 C with the service lost stated, or a correction that holds 150 C |
| C60 | T10-A5 restated: a supervisor forced out of its bound must be returned inside it by a response acting before the LDO's junction reaches 150 C, the voters at their default and the service lost stated; round 4's 'must end in the LDO's thermal shutdown' withdrawn (the shutdown is typical, no acceptance) | t10 8 | DS39724 (p.8); the owner's instruction of 5 October 2026 | declared | a condition for Layer 5's FMEA row; not met by anything in the tree |

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
- Round 4. The coordinator: C-ALLTX rev 3 quotes the printed bounds at 16.0684 V; with the BQ4050's offset drift it is 16.0718 V
  (case 2); whether the row quotes the CM5 scenario (17.0148 V at the maker's supply design figure) is the coordinator's as well.
- Round 4, T10. Layer 5 (L9T5-F09): the row that bounds the supervisors' state and its FMEA row, text in t10 8. Layer 6 (L9T5-F11,
  L9T5-F14): R602's order code; the H743's silicon revision. Boards A and B generator owners (L9T5-F10, L9T5-F13): the net's name
  at 4.18 V; the 60 mA declared for a supervisor's other parts. Layer 5 (L9T5-F13, F16, F17, all OPEN): a row bounding each
  supervisor's transmit share; the CAN fabric-fault rows, which no requirement covers, with the response each needs (t10 8).
  The budget's owner and rv-pwr's (L9T5-F12): the supervisors' HIGH.
- Round 4, SDR3-F02 (L9T5-F15). Record l8r2: L9P-F02's conditions on the coolers' start are stated with the module at 8.0 W.
  Board B's generator owner: the module's declared 1.6 A and the comment "no maximum given" against the sheet's appendix B.3.
