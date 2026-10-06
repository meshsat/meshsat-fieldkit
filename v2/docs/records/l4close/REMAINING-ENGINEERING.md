# REMAINING-ENGINEERING: the Layer 4 power candidate's remaining engineering after cx46, for the receiving company (MESHSAT-1357, 5 October 2026)

**What this file is.** A ledger of record text for the company that receives the desk engineering package: for every finding the
targeted recheck cx46 left NOT CLOSED, for every case the authors handed over, and for the findings cx46 closed or closed as
conditional, it gathers what the candidate's own records and the filed checks already say: the failed cases, the attempted
correction, the unresolved fact or design decision, the affected provisional outputs and their downstream dependency, the
receiving company's task with its acceptance limit, and how to reproduce. Every statement cites a file and a line (the citation
form is below). Written by the remaining-engineering ledger worker on branch `fnd/remeng` from `1c6d56f5` (the disposition
checkpoint of the connected P0 candidate on `fnd/p0pwr`), read from 22:46 CEST on 5 October 2026.

**What it is not.** It is not an acceptance, a closure, a verdict, a check, a qualification or a release of anything. It designs
nothing, computes no new figure, consumes no review and changes no verdict: the state of each item is whatever the cited record
says on this tip, and where this ledger notes a gap or a contradiction between two records it settles neither (section 6), apart
from the reading section 6's item E states for this ledger's own classification (the records' texts unchanged). It does
not revise the P0 list, which is the coordinator's. Power-design closure and fabrication release stay BLOCKED ([T5R:1]).
Prototype framing: nothing in the kit has been built, bought, powered or measured; every figure is quoted with its source's own
label (PRINTED, TYPICAL, MODEL, ASSUMPTION, INFERRED, DECLARED, DERIVED, MISSING, PROVISIONAL), and a MODEL figure is a desk
calculation, never a measurement.

**Amendment of 6 October 2026.** Made by the ledger-fix worker on branch `fnd/ledgerfix` from the candidate commit `6fe398e9`, read
from 02:35 CEST, on the two findings the DESK-gate draft named as unplaced: E11-37 is added as the handed-over item HO-L with its rows
in sections 4 and 5 (and section 6, item G), and the lower-source back-feed is settled in HO-F to the narrower reading, with the
disagreement kept named in section 6, item E. Every other line stands as written on `1c6d56f5`; nothing here accepts, closes or
promotes anything, and the class each added row carries is this ledger's reading (SESSION), never a revision of the P0 list.

**The owner's words that define an item** ([OWN:787]): "If a correction remains unsupported, hand it over as **remaining
engineering**, with the failed cases, attempted correction, unresolved fact or design decision, and affected provisional outputs.
Preserve the receiving company's ability to reproduce and change the design. Qualification-only items remain separately
identified." And ([OWN:849]): "The receiving company can take over genuinely unresolved engineering. Keep each affected guarantee
open or provisional and identify the downstream dependency. In particular, the reported handover of latent guard and CAN cases
must preserve any resulting limits on protection, thermal and service claims." And ([OWN:799]): "If cx46 remains negative, retain
the affected defects and transfer them as remaining engineering, not as qualification-only tasks or accepted corrections."

**The recheck as filed** ([CX46:10]): "P0 RECHECK: CORRECTIONS NOT CLOSED." Its next action ([CX46:113]): "End this correction loop,
reconcile the unsupported claims and governing records, and transfer each unresolved circuit or model issue to the receiving
company as a bounded REMAINING ENGINEERING task with its failed cases, attempted correction and affected provisional outputs." Its
own instruction about this ledger's subject ([CX46:206]): "Do not repeat this review method or relabel these tasks as qualification
only." It is the second negative on the method, which ends it ([CX46:3]).

**Classes used in the summary (section 5):** REMAINING ENGINEERING (a design or analysis task: a defect, an unsupported correction
or a missing bound the desk could not close); QUALIFICATION (a test of a design that is otherwise complete); EXTERNAL ARCHITECTURE
FACT (a vendor or physical fact that could change the selected architecture, the supplier validation annex's ARCH rows); CLOSED
(cx46's "CLOSED BY THE CORRECTION", in its stated scope only); CONDITIONAL (cx46's "CLOSED AS CONDITIONAL", with its conditions).

**Citation form.** `[ALIAS:N]` is line N, `[ALIAS:N-M]` lines N to M, `[ALIAS]` the whole file, of the file the alias names below;
a path in backticks is a repository path from the root. Line numbers are those of the tip read (`1c6d56f5`). The citations the
amendment of 6 October 2026 added (HO-L, its rows in sections 4 and 5, HO-F's back-feed reading, section 6's items E and G) are at
`6fe398e9`: under the aliases CX46, P0L, ANX, OWN, E11, E11P, TIQ, P11, B2 and SOLO the files are byte-identical at `1c6d56f5` and
`6fe398e9`, so either revision reads the same lines; under L4E9 and REG (both changed by set 31 between the two) the line numbers
are those of `6fe398e9` only. On set 31 (6 October 2026) the citations under BRK, B2, P11 and P0SOL are re-cited to their lines at `a6e3a066`, where set 31's merges of records l8p and l4e7 moved them, apart from [P11:89-92], which still names the lines of `1c6d56f5` (the passage it cited is rewritten at `a6e3a066`; on set 31's Q-40, 6 October 2026, HO-F's line is restated to W4's passage, [P11:119-126], and keeps the old citation only to mark the pre-W4 reading). On set 32 (6 October 2026) the citation under PAL is re-cited to its lines on `fnd/w34pdftext`, where W34's edit of the generator moved them by 15 lines, the cited words unchanged; the line numbers inside cx46's quoted words (RE-2, RE-6 and RE-7) are cx46's own, of the candidate it read, `4d0ff8a2`, and stay as quoted. The module
`v2/ecad/tools/tests/test_remeng.py` holds every citation to an existing file and range and every quoted verdict to its filed text.

At the adoption of the P0 list's revision 3 (6 October 2026, 11:23 CEST) revision 3 took the list's path and revision 2 stayed at its dated name, `P0-POWER-LIST.rev2-2026-10-05.md`, byte-identical to the list at `1c6d56f5` and at `dd1aed00`; this ledger's statements about the list describe revision 2 as it stood, so they cite P0L2 (revision 2) and the lines are revision 2's.

| Alias | File |
|---|---|
| CX46 | `v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md` |
| CX45 | `v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md` |
| CX44 | `v2/docs/records/l4close/CHECK-CX44-F01-SELECTION-8c7c335f-AS-RECEIVED.md` |
| V6 | `v2/docs/records/l4close/CHECK-V6-POWER-DRAFTS-7a82e82a-AS-RECEIVED.md` |
| P0L | `v2/docs/records/l4close/P0-POWER-LIST.md` |
| P0L2 | `v2/docs/records/l4close/P0-POWER-LIST.rev2-2026-10-05.md` |
| ANX | `v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md` |
| OWN | `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md` |
| T5R | `v2/docs/records/l9t5/README.md` |
| CASES | `v2/docs/records/l9t5/L9T5-CASES.md` |
| F01 | `v2/docs/records/l9t5/l9t5_f01.out` |
| PAL | `v2/docs/records/l9t5/l9t5_paloop.py` |
| CON | `v2/docs/records/l9t5/l9t5_connected.out` |
| T10R | `v2/docs/records/l9t5/T10-ROUND5.md` |
| T10 | `v2/docs/records/l9t5/l9t5_t10.out` |
| HWFW | `v2/docs/records/l9t5/apply_hw_fw_contract_t10.py` |
| PALA | `v2/docs/records/l9t5/apply_gen_sch_a_paloop.py` |
| PALD | `v2/docs/records/l9t5/apply_gen_sch_d_paloop.py` |
| STAB | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` |
| L8R2 | `v2/docs/records/l8r2/L8R2-KNOWN-DEFECTS.md` |
| DIST | `v2/docs/records/l8r2/l8r2_dist.out` |
| P0R | `v2/docs/records/l8r2/l8r2_p0.out` |
| BRK | `v2/docs/records/l8p/L8P-BREAKER.md` |
| C4 | `v2/docs/records/l8p/l8p_c4.out` |
| E11 | `v2/docs/records/l4e11/l4e11_power.out` |
| E11P | `v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` |
| TIQ | `v2/docs/records/l4e11/clarification/TI-QUESTIONS.md` |
| L4E9 | `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md` |
| REG | `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md` |
| P0SOL | `v2/docs/records/l4e7/L4E7-P0SOL.md` |
| P11 | `v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md` |
| B2 | `v2/docs/records/l4e7/B2-PRESENCE.md` |
| SOLO | `v2/docs/records/l4e7/l4e7_p0sol.out` |
| EFS | `v2/docs/records/efuse/EFUSE-SETTINGS.md` |
| EFO | `v2/docs/records/efuse/efuse_check.out` |

## 0. Where the candidate stands on the tip read

- The candidate cx46 read is `4d0ff8a2` ([CX46:8]); the tip read here, `1c6d56f5`, carries the disposition after cx46 (text and
  predicates, no new design: [T5R:1], [T5R:107-110]) and is a checkpoint whose own commit subject ends with the words outputs
  regenerating (the commit `1c6d56f5`, read with `git show`; see section 6, item C).
- The connected electrical verdict reads ([CON:336]) "REMAINING ENGINEERING. No row of sections 5 to 10 is a positive electrical
  acceptance", on seven open fault rows ([CON:320-335]).
- The P0 list on this tip is still "revision 2, 5 October 2026, 16:50 CEST" ([P0L2:1]); its row states are the coordinator's
  ([T5R:1]). This ledger cites the current state from the records, never from that list's 16:50 column (RE-1).

## 1. The twelve cx46 findings NOT CLOSED, each a REMAINING ENGINEERING item

Identifier RE-n carries cx46's item number n. The field **Check's words** holds cx46's classification entry and its blocker, quoted
as filed.

### RE-1 (cx46 item 1): the governing inputs and the twelve-row states

- **Check's words.** "1. Missing governing inputs and twelve-row states: NOT CLOSED" ([CX46:116]); evidence: "The added owner file
  ends at part 22, line 663; the added P0 list at lines 18-24 retains earlier candidate states. Install the missing exact
  instructions and reconcile the list. REMAINING ENGINEERING." ([CX46:118]). Blocker ([CX46:100]): "1.
  v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:663 and v2/docs/records/l4close/P0-POWER-LIST.md:18-24: the supplied governing file
  stops at part 22 and the current list is stale. Smallest correction: install the exact missing owner instructions and reconcile all
  twelve states against this verdict. REMAINING ENGINEERING must remain visible for unresolved design rows."
- **Failed cases.** No electrical case: a record defect. The list's rows P0-1 to P0-7 ([P0L2:18-24]) carry the 16:50 states cx46
  names ([CX46:81]).
- **Attempted correction and the disposition.** Main `0d5f855e` merged into the candidate: parts 23 to 25 and the four checks filed
  ([T5R:1]); the owner file now holds part 23 ([OWN:671]), part 24 ([OWN:735]) and part 25 ([OWN:808]).
- **Unresolved.** The list's reconciliation: [P0L2:1] still reads revision 2 and its rows [P0L2:18-24] are unchanged on this tip.
- **Affected outputs.** Any reader of [P0L2:18-24] reads superseded states (for example P0-2 "NEXT for Slot A" at [P0L2:19] against
  V6-B1 OPEN at [CON:174]).
- **Receiving company's task.** None of engineering: read each row's state from the records this ledger cites (sections 1 to 4),
  not from [P0L2:18-24]. The list's revision is the coordinator's ([T5R:1]).
- **Reproduce.** Not applicable (text).
- **State on this tip.** Half done: the governing instructions are in the tree; the twelve-row reconciliation is not.

### RE-2 (cx46 item 2): F01's reference loading, the resistor corners and the acceptance limits

- **Check's words.** "2. Q1 reference loading, resistor corners and propagation: NOT CLOSED" ([CX46:121]); evidence:
  "l9t5_paloop.py:193-245 reproduces the revised steady-state MODEL band, but omits the held Q551 load from its actual-load envelope
  and retains nominal resistor-dependent residual terms. l9t5_f01.out:215 rounds the acceptance above the calculated floor. Extend
  the bounded analysis and supplier tasks; retain REMAINING ENGINEERING." ([CX46:123]). Blocker ([CX46:101]): "2.
  v2/docs/records/l9t5/l9t5_paloop.py:198-205,224-245 and l9t5_f01.out:215-224: complete reference loading and the complete-band
  description are unsupported. Smallest correction: include Q551's held and release loads in V-PA-REF/B-PA2, propagate
  resistor-dependent residual corners, correct the printed-only label, and round the B-PA1 acceptance conservatively. Keep F01 and
  dependent service claims PROVISIONAL as REMAINING ENGINEERING."
- **Failed cases.** C-ALLTX rev 3 (every transmitter keyed 60 s from a 15.5 V rest, fans running) needs 15.5162 V nominal and
  16.0718 V with the printed bounds against REQ-018's 15.5 V before any correction ([P0L2:18], [F01:31]). With the PA drain-current
  cap the case reads 15.1308 V, MODEL on PRINTED bounds, margin 0.3692 V ([CON:123-124]). The defect cx46 names inside that
  correction: Q551 holding PA_ISP near ground loads the reference U552 through R559, "approximately 0.55/549 + 3.3551/1000 =
  4.3569 mA, MODEL" against the sheet's accuracy printed at IOUT = 1 mA only and a load regulation of 0.030 V/A TYPICAL
  ([CX46:82]); the record's bound is "up to 4.4791 mA" (MODEL, an upper bound) ([F01:103-104]).
- **Attempted correction.** The cap, correction (c), selected PROVISIONAL (SESSION) ([F01:209-211]): `apply_gen_sch_a_paloop.py` and
  `apply_gen_sch_d_paloop.py`, composed with every pending draft of boards A and D, 11 of 11 mutations fail ([T5R:43-49]); the cx45
  corrections (R553 and R559 at their corners, the reference's load residual, V-PA-REF) in `0fb441b1` and `4d0ff8a2`
  ([T5R:136-141]); the disposition after cx46 in `9cc6725d` and `0b33a1f9`: the held load and its release carried to V-PA-REF and
  B-PA2, R553's top corner in the IB and leakage terms, the PRINTED-rows band 6.3888 to 6.8945 A labelled "NOT a bound on the cap",
  B-PA1's limit rounded down to 6.351 A ([T5R:111-117], [F01:103-109], [F01:128], [F01:132-134], [F01:226]).
- **What the recheck said does not stand.** The complete reference loading and the complete-band description ([CX46:101]); the
  steady MODEL band itself reproduces, "6.351818778797002 to 6.925911926857548 A. This verifies its arithmetic, not complete loading
  coverage or RF service." ([CX46:36]).
- **Unresolved fact or design decision.** The reference's output at the held load and through the release: "its load regulation at
  that load is TYPICAL only: REMAINING ENGINEERING (the reference's loading through the hold and the release), with the acceptance
  limits below" ([F01:107-108]); cx44's finding 3 reads "STILL AN OPEN DESIGN DEFECT for the reference's loading (cx46)" ([F01:254]).
  Beside it, the 30 W service under the cap rests on the maker's EXAMPLE of 6.00 A at 30 W, whose transfer is an ASSUMPTION
  ([F01:155-164]).
- **Affected provisional outputs.** "F01 / D-17 and every dependant (C-ALLTX rev 3 at the cap, U13's room, B-PA1's limit, the PA
  rail's rows) stay PROVISIONAL" ([F01:212-214]); L9P-F04's closure claim and board D's loop R57, R58, R83 ([F01:209-211]); the
  connected row ([CON:334-335]); L4-E9 change-list rows R-227 (board A) and R-238 (board D) ([T5R:48-49]); the Layer 5 texts IF-A-PA
  and IF-AD-HARNESS and the firmware row, and Layer 12's build check ([T5R:51-56]); the lost PA_ILIM conductor's single-failure row
  (Layer 8) and REQ-059's thermal row ([F01:280-282]); J_PA's lead (finding L9T5-F26, [T5R:194-196]).
- **Receiving company's task.** At the desk: extend the bounded analysis of the reference to its held load and its release, as cx46
  asks ([CX46:123]). Then the validation the records name (UNSENT): V-PA-REF, three TLV75801P of the fitted lot at their drawn load
  0.989 and 1.018 mA, -40, 25 and 85 C, VFB within 0.5445 to 0.5555 V, and at Q551's held load (up to 4.479 mA) and through the
  release within the set point's 30.5 ms ramp ([F01:235-239]); B-PA1, the module's drain current at 30.0 W at most 6.351 A less the
  lab's expanded uncertainty (k = 2), every point of the stated envelope ([F01:222-230]); B-PA2, no overshoot over 6.926 A at each key,
  the pack current under 18.32 A or excursions under 0.282 ms each and 1.03 % of the time, and the release from the hold
  ([F01:231-234]). If B-PA1 fails the arrangement fails, not a requirement: routes R1 and R2 ([F01:215-220]). U5 (R-214) is MISSING
  against the 0.3692 V MODEL margin ([F01:240]).
- **Reproduce.** From the repository root `python3 v2/docs/records/l9t5/l9t5_f01.py` (output `v2/docs/records/l9t5/l9t5_f01.out`; the
  band in `v2/docs/records/l9t5/l9t5_paloop.py` cap(), [PAL:201-270]); the composition and mutations
  `python3 v2/docs/records/l9t5/l9t5_f01_drafts.py` with `v2/docs/records/l9t5/check_f01_netlist.py`; the case
  `python3 v2/docs/records/l9t5/l9t5_case.py` (its section 8 in `v2/docs/records/l9t5/l9t5_case.out`). The INA250 sheet is held back
  and fetched by sha256, never committed ([F01:5]).
- **State on this tip.** NOT CLOSED: F01 / D-17 PROVISIONAL, the reference's loading REMAINING ENGINEERING ([CON:334-335],
  [CASES:62-64]).

### RE-4 (cx46 item 4): the dedicated return between boards A and B (V6-B1)

- **Check's words.** "4. Q2 return placement and distributed solution: NOT CLOSED" ([CX46:131]); evidence: "The new l8r2_dist.py and
  output provide a substantive placement study, but use XT60-M geometry for selected XT60-F sockets, assumed source locations and
  plane fill, and an averaged LDO ground probe. l8r2_dist.out:119-125 therefore overstates V6-B1's correction. Keep it OPEN as
  REMAINING ENGINEERING." ([CX46:133]). Blocker ([CX46:102]): "4. v2/docs/records/l8r2/l8r2_dist.py:478-479,590-614 and
  l8r2_dist.out:119-125: actual XT60-F geometry, stage placement, individual LDO ground shifts and complete tolerance coverage are not
  established. Smallest correction: keep V6-B1 OPEN as REMAINING ENGINEERING; the receiving scope must use the selected female lands,
  real source/load sites and a justified distributed resistance envelope."
- **Failed cases.** V6-B1: "the acceptance assumes each board is one node; the boards' own plane resistance can consume the whole
  margin, and it is not among the conditions." ([V6:34-35]); the list's case: 0.62 mOhm cold puts a ribbon conductor at 1.218 A
  against 1 A ([P0L2:19]). On the study, at +76.25 C, the declared upper bound 27.8159 A puts the ribbon at 0.6299 A against its least
  rating 0.5995 A and a VH pin 2 at 6.4485 A against 5.9948 A, both least ratings INFERRED; every printed row holds and the service
  cases (C-DEV rev 2 20.4746 A, the largest steady state 22.8711 A) hold on the least ratings ([CON:163-176], [DIST:112-123]).
- **Attempted correction.** Record l8r2's dedicated-return drafts (`v2/docs/records/l8r2/apply_gen_sch_a_gndrtn.py`,
  `v2/docs/records/l8r2/apply_gen_sch_b_gndrtn.py`, round 8, [L8R2:876]); after cx45, `v2/docs/records/l8r2/l8r2_dist.py` (added in `0fb441b1`) places the
  three return sockets and J_5V_IOC on the drawn boards A23 and B19 (SESSION L8R2-D10) and solves the return as a distributed
  network ([DIST:26-45], [DIST:46-55], [L8R2:1076-1086]); the group-centre claim and SESSION L8R2-D9 withdrawn ([T5R:142-143]).
- **What the recheck said does not stand.** The study as a correction: XT60-M geometry for the XT60-F sockets, uniform fill an
  ASSUMPTION, injection at connector lands, an averaged LDO probe, a local vertex search ([CX46:85-86]).
- **Unresolved fact or design decision.** The receiving scope as the record states it: "the selected female lands, the real source
  and load sites, a justified distributed resistance with tolerance coverage, each LDO's own shift; the declared upper bound's least
  rows with L8R2-F43 and L8R2-F44" ([DIST:125-134], [L8R2:1087-1094]). The fourth lead (SESSION L8R2-D11) is a route only, NOT
  drafted ([DIST:108-111], [DIST:133]).
- **Affected provisional outputs.** The return's rows ([CON:163-176]); T10-A3's shift with the dedicated return ([CON:332-333]); the
  averaged 0.0205 V the T10-A3 chain uses ([CON:224-227], [DIST:123-124]); V6-B2's indirect paths PROVISIONAL on vendor tasks
  (Hirose U.FL, Molex HDMI, UNSENT) ([L8R2:1063], [CON:175], [CON:343-345]); V6-m8, the XT60 board end MISSING ([L8R2:1065]); P0-2's row
  ([P0L2:19]); Layer 10 places from the reserved sites ([DIST:26-27]).
- **Receiving company's task.** The scope above, with the requirement as the list states it: "every ground branch inside its
  printed rating over every permitted aged-contact corner" ([P0L2:19]), on the service cases and the declared upper bound
  ([CON:166-169]); the vendor curves L8R2-F43 (JST VH) and L8R2-F44 (Wurth WR-CAB) ([L8R2:1046], [DIST:117-122]).
- **Reproduce.** `python3 v2/docs/records/l8r2/l8r2_dist.py` (output [DIST]), with `v2/docs/records/l8r2/l8r2_p0.py` and
  `v2/docs/records/l8r2/l8r2_gndret.py`; tests `test_l8r2` (`v2/docs/records/l8r2/README.md`).
- **State on this tip.** NOT CLOSED: "V6-B1: OPEN, REMAINING ENGINEERING for the receiving company" ([CON:174]).

### RE-5 (cx46 item 5): the CAN schedule, containment, quorum and recovery

- **Check's words.** "5. Q3 CAN schedule, containment, quorum and recovery: NOT CLOSED" ([CX46:136]); evidence: "FW-B22's traffic
  arithmetic is supportable as a MODEL, and hardware containment is drafted. l9t5_t10.out:576-591 admits service-defeating GPIO and
  latent comparator cases. Complete independent containment and recovery remain REMAINING ENGINEERING." ([CX46:138]). Blocker
  ([CX46:103]): "5. v2/docs/records/l9t5/l9t5_t10.out:562-591,639-640: general quorum containment is not corrected by a limiter that
  admits the GPIO jammer and undiagnosed comparator failures. Smallest correction: propagate OPEN/PROVISIONAL to CON-004, L9T5-F21 and
  FW-B22, and hand over the independent peer-silence/diagnostic circuit and recovery proof as REMAINING ENGINEERING."
- **Failed cases.** The fault table of the quorum (two of three controllers serving; IOHA rows 3, 7 and 8) ([T10:587-597]); the
  admitted counterexamples: "a TX pin repurposed as a GPIO and toggled under the limiter's least 4.7 % share disrupts the bus without
  tripping it" and "a latent stuck comparator in either bound, found only on the bench (V-B22, V-B23), with no service interval
  bounding that" ([T10:599-603]); a babbling supervisor is in no FMEA row and can stop the quorum (L9T5-F21, [T10R:201-202]).
- **Attempted correction.** FW-B22, the quorum's message schedule (822 dominant bit-times against FW-B21's 1000 at 500 kbit/s, a
  traffic MODEL) ([T10:554-561], [HWFW:76-82]); the containment `v2/docs/records/l9t5/apply_gen_sch_b_iocguard.py` (Slot C's
  `8d7be89c`, merged at `7f7a53ae`, change-list row R-245): a transmit-share limiter per transceiver and a rail trip per supervisor,
  composed on board B, read by pin, six mutations FAIL ([T10:562-583], [T10:650-660], [T5R:159]); SESSION L9T5-D10 ([T10R:175],
  [T10R:226]).
- **What the recheck said does not stand.** Fault-contained quorum service: the schedule "establishes that particular traffic model,
  not fault-contained quorum service. The GPIO jammer and latent comparator cases remain admitted counterexamples." ([CX46:87]).
- **Unresolved fact or design decision.** Attributing a GPIO-toggled TX "needs each controller's TXD read by the other two and a
  2-of-2 vote of the other two on its SHDN or its LDO's EN (twelve observation inputs and six vote outputs, a pin plan for the three
  H743s): NOT DRAFTED here" ([T10:600-602]); a diagnostic for a latent comparator with a bounded interval.
- **Affected provisional outputs.** "CON-004's quorum verdict (OPEN), FW-B22 (PROVISIONAL), L9T5-F21 (OPEN) and this section's quorum
  rows" ([T10:603-604]); L9T5-F16 PROVISIONAL ([T10:683-686]); the connected row ([CON:328-329]) and the CAN service row
  ([CON:130-139]); the contract rows FW-B22 and V-B22 ([HWFW:76-86]); Layer 5's IOHA section 12 ([T10R:201-202]).
- **Receiving company's task.** "the peer-silence or diagnostic circuit and the recovery proof" ([T10R:219]); acceptance: CON-004's
  quorum service held under every row of the fault table including the GPIO-toggled TX and the latent comparators, with any
  automatic diagnostic carrying "a bounded detection/response interval, including faults that arise after startup and faults
  affecting the diagnostic itself" (the owner's part 24, [OWN:777]). Validation after it: V-B21, V-B22 ([HWFW:71-86]).
- **Reproduce.** `python3 v2/docs/records/l9t5/l9t5_t10.py` (about 20 s, temporary directories) ([T10R:233-236]); output [T10].
- **State on this tip.** NOT CLOSED: CON-004's quorum service OPEN, FW-B22 PROVISIONAL, L9T5-F21 OPEN ([T10:662-667], [T10R:1]).

### RE-6 (cx46 item 6): the independent clock, share and excess-current protection (the rail trip's response)

- **Check's words.** "6. Q3 independent clock/share/excess-current protection: NOT CLOSED" ([CX46:141]); evidence:
  "apply_gen_sch_b_iocguard.py adds independent circuits, but their response proof is incomplete; V-B23 at
  apply_hw_fw_contract_t10.py:80-81 fails the candidate's own RC arithmetic. VOS0 below trip remains uncontrolled. REMAINING
  ENGINEERING." ([CX46:143]). Blocker ([CX46:104]): "6. v2/docs/records/l9t5/apply_hw_fw_contract_t10.py:80-81 and
  l9t5_t10.py:1176-1188: V-B23's response is incompatible with the drafted RC network; maximum response also lacks guaranteed
  comparator timing. Smallest correction: withdraw the unsupported response claim and hand over a corrected response mechanism and
  complete network calculation as REMAINING ENGINEERING, without relaxing protection to obtain a pass."
- **Failed cases.** V-B23's drafted acceptance, EN low within 0.2 s of a 0.30 A load, against the drafted network: cx46's MODEL
  0.9259 s from 0.1739 A and 1.8888 s from discharged, on the 100 kohm filter resistor alone, cx46 noting that the network's
  5.76 kohm load resistance also lies in the charging path ([CX46:89]); the record's
  own MODEL, about 0.98 s from the bounded state, the comparator's delay not counted ([T10:584-586]); the comparator's propagation
  and start-up delays are TYPICAL only in SBVS240C ([T10:566-567], [CX46:88]).
- **Attempted correction.** The rail trip per controller: 0.3 ohm sense, INA169 into 5.76 kOhm, a 1.17 s average, a TPS3701 holding
  the LDO's EN low, 0.2183 to 0.2452 A at the tolerances ([T10:578-583]), in `apply_gen_sch_b_iocguard.py` (RE-5); V-B23 as drafted
  ([HWFW:87-90]).
- **What the recheck said does not stand.** The response claim and a maximum response on guaranteed timing ([CX46:104]).
- **Unresolved fact or design decision.** A response mechanism whose maximum response is bounded on printed timing, and the complete
  network calculation ([T10:584-586], [T10R:220]).
- **Affected provisional outputs.** V-B23's 0.2 s WITHDRAWN ([HWFW:11], [HWFW:87-90]); the rail trip's response times PROVISIONAL
  ([T10:662-667]); the latent rail-trip row "removes or weakens: T10's thermal bound and T10-A3's hardware bound" ([CON:322-323]);
  L9T5-D6 reversed onto the rail trip ([T10R:172]); the containment's change-list row R-245 ([T5R:159]) and Layer 5's
  contract row V-B23 ([HWFW:87-90]).
- **Receiving company's task.** "a corrected rail-trip response mechanism and the complete network calculation, protection not
  relaxed" ([T10R:220]); acceptance on the record's criteria: "125 C for every sustained state, 150 C only for a transient hardware
  ends" ([T10R:3]); the transient rule needs the LDO's Zth at the trip's time on board B's copper at most 105 C/W, NOT PRINTED by Diodes
  ([T10:634-637]). Validation after it: V-B23 restated ([HWFW:87-90]).
- **Reproduce.** As RE-5.
- **State on this tip.** NOT CLOSED: "V-B23's response (WITHDRAWN)", the response times PROVISIONAL ([T10:662-667]).

### RE-7 (cx46 item 7): the sustained peak junction and the qualification envelope

- **Check's words.** "7. Q3 sustained peak junction and qualification envelope: NOT CLOSED" ([CX46:146]); evidence:
  "l9t5_t10.py:1181-1191 and l9t5_t10.out:598-620 continue to convert filtered average current into a peak bound. The periodic-load
  countermodel satisfies the proposed qualification envelope but exceeds the sustained criterion. REMAINING ENGINEERING."
  ([CX46:148]). Blocker ([CX46:105]): "7. v2/docs/records/l9t5/l9t5_t10.out:598-620 and l9t5_connected.out:282-301: the universal
  sustained temperature bound and positive worst-case margin do not follow from average current. Smallest correction: mark them
  PROVISIONAL/OPEN and hand over peak-current containment or a complete periodic electrothermal solution with uncertainty as
  REMAINING ENGINEERING."
- **Failed case.** cx46's diagnostic countermodel, all ASSUMPTION inputs: 0.50 A for 0.40 s every 1.50 s, a single pole of 184 K/W
  and 0.25 s, 0.020 V of extra drop, the 0.3 ohm sense; MODEL filtered peak 0.212185 A (under the trip's least), Zth(171 ms)
  91.155 K/W (inside the proposed 105 K/W), periodic peak junction 127.55 C ([CX46:91]); the record's reproduction reads 127.54 C,
  over the 125 C criterion ([T10:616-621], [CON:308]).
- **Attempted correction.** The rail trip's average bound and the constant-current figure 115.4 C at 0.2452 A (MODEL) ([T10:615]);
  the qualification limits (junction-to-air at most 229 C/W, Zth(181 ms) at most 105 C/W, the INA169 under 85 C) ([T10:638-642]).
- **What the recheck said does not stand.** A constant-current MODEL "does not bound the peak of a periodically varying current
  monitored through an RC filter" ([CX46:90]).
- **Unresolved fact or design decision.** "peak-current containment or a complete periodic electrothermal solution with uncertainty
  is REMAINING ENGINEERING. A latent rail trip removes even the average bound" ([T10:620-621]).
- **Affected provisional outputs.** "the universal sustained bound and its positive margin are WITHDRAWN" ([T10:620]); the worst-case
  margin row "PROVISIONAL/OPEN" ([CON:314-317]); every final T10 figure a MODEL reading, PROVISIONAL/OPEN ([CON:293-312]); T10-A3 at a
  peak PROVISIONAL ([T10:611-613]); L9T5-F13 and the babbling row PROVISIONAL ([T10:678-690]); T10-A5's limits "measurements, NOT an
  acceptance" ([T10R:153]); a rev X part's admission resting on it ([T10R:224]); Layer 5's contract row V-B20, whose readings are "measurements, NOT an
  acceptance of a sustained bound" ([HWFW:64-70]).
- **Receiving company's task.** As [T10:620-621]; acceptance on the unchanged criterion: "125 C for every sustained state, 150 C only for a
  transient hardware ends" ([T10R:3]), "over tolerances and repeated faults, including
  measurement uncertainty where evidence is physical" ([CX46:207]). The first-article measurement (T10-A5 restated) informs it and is
  not an acceptance ([T10R:153]).
- **Reproduce.** `python3 v2/docs/records/l9t5/l9t5_t10.py` (section 10j (e)) and `python3 v2/docs/records/l9t5/l9t5_connected.py`
  (section 10).
- **State on this tip.** NOT CLOSED: "the sustained thermal bound (WITHDRAWN as a bound, PROVISIONAL)" ([T10:664-665]).

### RE-8 (cx46 item 8): the T10 rows made to agree (revision V, the set point, the admission route)

- **Check's words.** "8. Q3 consistency across active rows: NOT CLOSED" ([CX46:151]); evidence: "The new contract and final model
  select revision V and the final set point, but T10-ROUND5.md:50-56,205-209 retains contradictory admission instructions. Explicitly
  supersede these and align current acceptance references. Dependent acceptance remains REMAINING ENGINEERING." ([CX46:153]).
  Blocker ([CX46:106]): "8. v2/docs/records/l9t5/T10-ROUND5.md:50-56,205-209 still contains the old revision-X admission route and
  set-point shortcut; l9t5_t10.out:642-647 retains earlier acceptance references. Smallest correction: explicitly supersede those
  actionable passages and point all current procurement, contract and inspection instructions to revision V, the final set point and
  the actual held qualification limits. The dependent unsupported acceptance remains REMAINING ENGINEERING."
- **Failed case.** Rev Y's rows, the cover for a rev X part, miss 125 C at the drop's worst corner (125.2 C bounded) ([T10R:44-46]);
  round 5's admission route at 0.2318 A and L9T5-F22's "admits any revision" shortcut ([T10R:224]) would have admitted it ([T10R:51-54]).
- **Attempted correction and the disposition.** Slot C's `6b768b1e`: the old route "SUPERSEDED (round 6, and the recheck cx46's item
  8), kept as written only as history, not an instruction" with the current instruction "revision V only; revision X HELD with no
  admission route; R602 14.0 k is the final set point" ([T10R:51-56]); L9T5-F23's consequence "SUPERSEDED in its admission clauses"
  ([T10R:205-209]); the rows made to agree ([T10:645-649], [HWFW:41-51]).
- **Unresolved, of substance.** "a rev X part's admission, its own qualification, and the sustained thermal acceptance it would rest
  on are REMAINING ENGINEERING" ([T10:647-648]).
- **Affected provisional outputs.** Revision X HELD ([T10R:144-145]); the procurement and inspection rows (L9T5-F23, Layer 6)
  ([T10R:205-209]).
- **Receiving company's task.** A rev X part's qualification: "V-B20 in its bounded state at most 0.2183 A (the rail trip's least) and
  its rows re-solved" ([T10R:144-145]), resting on RE-7's bound ([T10R:224]).
- **Reproduce.** As RE-5.
- **State on this tip.** The text defect is disposed of in the cited passages; the dependent acceptance stays REMAINING ENGINEERING
  ([T10:647-648]). The record makes no closure claim for item 8.

### RE-9 (cx46 item 9): the replacement guard's propagation into L4-E11 and its allowance consumers

- **Check's words.** "9. Q5 guard propagation into L4-E11 and dependents: NOT CLOSED" ([CX46:156]); evidence: "New L4-E11 section 28
  traces both replacement-guard states and capacitance using changed allowances. It does not execute the named earlier allowance case,
  and L8P-R9-F2 remains open in L8P-BREAKER.md:1376-1378 and connected.out:316-318. Complete propagation remains REMAINING
  ENGINEERING." ([CX46:158]). Blocker ([CX46:107]): "9. v2/docs/records/l4e11/l4e11_power.out:2036-2060 and
  v2/docs/records/l8p/L8P-BREAKER.md:1376-1378: section 28 evaluates the replacement guard's new allowances, while Layer 5 and record
  l9stk's allowance remain unrestated. Smallest correction: state the changed circuit/case explicitly, reconcile the allowance
  consumers and regenerate affected startup/protection rows. Until then this propagation is REMAINING ENGINEERING."
- **Failed case.** The guard's draw on DOCK_EN_OUT rises from 18.25 uA to at most 36.00 uA cold and 47.02 uA tripped (PRINTED maxima,
  the worst single fault) against the 30 uA row of Layer 5 and record l9stk 15.9 (L8P-R9-F2) ([BRK:1407-1409]); cx46's DC check at
  180 uA gives about 3.447 V on DOCK_EN_OUT at the low-source corner, MODEL ([CX46:92]).
- **Attempted correction and the disposition.** L4-E11 section 28 states the changed circuit and executes both allowance cases, 40
  and 50 uA and the first form's 50 and 180 uA ([E11:2036-2054]); its disposition: "these rows hold on the delta's intact circuit at
  both allowance cases; PROVISIONAL, not closed" ([E11:2066-2071]); the consumers drafted for their owners, not applied
  ([BRK:1409-1413]).
- **Unresolved.** The owners' restatement of the allowance (Layer 5's row, record l9stk 15.9: still 30 uA, [E11:2043-2044]) and "the
  replay of the dependent start-up and protection rows (20f's timing against U47's and U48's tSD at the owners' restated allowance,
  22's bleed with path 2's VBAT load)" ([E11:2068-2071]).
- **Affected provisional outputs.** Every row resting on the allowance ([BRK:1413-1414]); the connected guard row ([CON:201-203]).
- **Receiving company's task.** The replay named above, against L4-E11's own windows (the held reading under 0.7755 V, the powered
  reading at most 1.981 V, RET/OUT at 0.4707 or more, the breaker's start no sooner than the RC hold's least 0.110 s)
  ([E11:2046-2065]).
- **Reproduce.** `python3 v2/docs/records/l4e11/l4e11_power.py` (section 28) and `python3 v2/docs/records/l8p/l8p_c4.py` (10c).
- **State on this tip.** NOT CLOSED: L8P-R9-F2 OPEN ([BRK:1407], [BRK:1420-1422]).

### RE-10 (cx46 item 10): the guard's common-path faults and an automatic diagnostic (L8P-R9-F1, the retry heating)

- **Check's words.** "10. Q5 common-path faults and automatic diagnostic: NOT CLOSED" ([CX46:161]); evidence: "The second path is a
  real drafted correction, with recorded pin checks and mutations. Nevertheless, retry heating after loss of path 1 is unbounded, and
  a latent first failure followed by a second still removes protection without bounded detection. l8p_c4.out:278-282,332-339.
  REMAINING ENGINEERING." ([CX46:163]). Blocker ([CX46:108]): "10 and 17. v2/docs/records/l8p/l8p_c4.out:278-282,332-339,358-362 and
  v2/docs/records/l8p/L8P-BREAKER.md:1350-1375: single-path retry heating is unbounded and the latent double failure removes the
  trip, despite broad positive C-PROT language. Smallest correction: qualify every such verdict as OPEN/PROVISIONAL and transfer
  bounded retry-energy analysis plus automatic diagnostic or fault-tolerant redesign as REMAINING ENGINEERING."
- **Failed cases.** The three latent single failures of round 8's guard with UNBOUNDED intervals ([BRK:1350-1355]); the exposure
  while the guard is lost: the battery FETs reach 150 C held at 20.53 A from the 76.25 C air (DERIVED), a held current from 20.53 A
  to the breaker's limit puts a series part over its limit below the trip ([BRK:1345-1349]); with path 1 lost, path 2's relaxation
  lets the FETs carry current at most 43.8 ms in every 0.154 s or more, "the junction's rise in each on-time NOT BOUNDED here"
  ([C4:283-286]); a latent first failure followed by a second removes the trip ([C4:332-338]).
- **Attempted correction.** `v2/docs/records/l8p/apply_gen_sch_a_thgfs.py`, two guard paths sharing only the pour and the loop (Slot
  C's `f04aa0b4`, merged at `64a65943`; change-list row R-244), composed (731 parts), seven mutations FAIL ([BRK:1356-1367],
  [C4:342-354], [T5R:172]); SESSION L8P-D10 ([BRK:1391-1395]).
- **What the recheck said does not stand.** Protection after a latent first failure and under path 2's retries ([CX46:93]).
- **Unresolved fact or design decision.** "the bounded retry-energy analysis of path 2 alone after path 1 is lost, and an AUTOMATIC
  diagnostic with a bounded detection and response interval covering faults after start-up and faults of the diagnostic itself (the
  owner's part 24), or a fault-tolerant redesign" ([BRK:1402-1406]); why no diagnostic is drafted: "one that tests a shunt opens the
  breaker in service, and a cross-check of the two VTEMP outputs sees the switches, not the gate networks or the shunts"
  ([BRK:1400-1402]).
- **Affected provisional outputs.** "C-PROT rev 1 for the guard is PROVISIONAL at every claim that rests on this" ([C4:274-275]);
  "L8P-R9-F1 weakens every C-PROT claim for the guard" ([BRK:1406]); L4-E11 section 28 ([E11:2066-2068]); the connected guard row
  ([CON:194-203], [CON:326-327]); E-13b (e) ([BRK:1417-1419]).
- **Receiving company's task.** As stated above ([BRK:1402-1406]); acceptance: C-PROT rev 1, every series part within its limits below
  and above the trip ([BRK:1343-1344]), the FETs' 150 C behind the guard ([CON:199]).
- **Reproduce.** `python3 v2/docs/records/l8p/l8p_c4.py` (sections 10b, 10c; output [C4]); `v2/docs/records/l8p/check_l8p_fs.py`
  reads the composed delta ([C4:345-347]).
- **State on this tip.** NOT CLOSED: "C-PROT rev 1 for the guard PROVISIONAL; L8P-R9-F1, F2 and F3 OPEN" ([BRK:1420-1422]).

### RE-13 (cx46 item 13): the connected coordination and service claims

- **Check's words.** "13. Q7 connected coordination and service claims: NOT CLOSED" ([CX46:176]); evidence: "connected.out sections 5
  and 8 now describe service conditions, downstream ratings and the replacement guard; the U7 predicate at line 343 names C-DEV rev 2.
  However, lines 282-301 and 350-352 still credit unsupported universal thermal bounds. Dependent electrical acceptance remains
  REMAINING ENGINEERING." ([CX46:178]). Blocker ([CX46:109]): "13 and 17. v2/docs/records/l9t5/l9t5_connected.out:193-199,282-301,350-352:
  improved coordination tables still inherit unsupported guard and thermal closure. Smallest correction: make the connected verdict
  predicates depend on the unresolved fault rows, including latent rail-trip failure and sustained peaks, and retain REMAINING
  ENGINEERING rather than a positive electrical acceptance."
- **Failed cases.** Those of RE-2, RE-4, RE-6, RE-7, RE-10, HO-C and HO-E, on which the connected rows rest ([CON:320-335]).
- **Attempted correction and the disposition.** `l9t5_connected.out` section 11 lists the seven fault rows, each with the cx46 item that
  holds it, read from the filed record, all OPEN ([CON:319-335], [T5R:122-128]); the verdict "REMAINING ENGINEERING" ([CON:336-340]);
  the predicate "the connected electrical verdict reads REMAINING ENGINEERING, never a positive acceptance, while any fault row it
  depends on is open (cx46 items 13, 17)" ([CON:391]).
- **Unresolved, of substance.** Nothing beyond the seven rows: the connected acceptance follows when they close ([CON:336-340]).
- **Affected provisional outputs.** Sections 5 to 10 of [CON], each a MODEL reading ([CON:336-337]).
- **Receiving company's task.** Re-run the connected trace after each of the seven rows is closed by its own task.
- **Reproduce.** `python3 v2/docs/records/l9t5/l9t5_connected.py` (output [CON]).
- **State on this tip.** NOT CLOSED in substance; the verdict text no longer credits a positive acceptance ([CON:336]).

### RE-17 (cx46 item 17): the handed-over cases propagated to every affected claim

- **Check's words.** "17. Handed-over cases propagated to every affected claim: NOT CLOSED" ([CX46:196]); evidence: "L8P-R9-F1 weakens
  guard C-PROT; L9T5-F21's GPIO jammer weakens quorum and FW-B22; latent share-comparator failure weakens service and latent rail-trip
  failure removes thermal protection; VOS0 below trip weakens controller survival and service. Some prose marks these provisional, but
  positive guard and connected thermal predicates still exclude their consequences. REMAINING ENGINEERING." ([CX46:198]). Blockers
  ([CX46:108]) and ([CX46:109]), quoted under RE-10 and RE-13.
- **Failed cases.** The handed-over cases HO-A to HO-E (section 2), with cx46's statement of their effects ([CX46:97]).
- **Attempted correction and the disposition.** The effects written at each claim: [CON:320-335], [T10:662-667], [C4:355-358],
  [BRK:1369-1422], [E11:2066-2071]; section 4 of this ledger lists each claim with the row that names it.
- **Unresolved, of substance.** The cases themselves (HO-A to HO-E).
- **Affected provisional outputs.** Section 4.
- **Receiving company's task.** Those of HO-A to HO-E.
- **Reproduce.** As RE-5, RE-10 and RE-13.
- **State on this tip.** NOT CLOSED in substance; the records now mark each affected claim OPEN or PROVISIONAL (section 4).

### RE-18 (cx46 item 18): route B2 marked unselected and withdrawn throughout

- **Check's words.** "18. B2 uniformly unselected and withdrawn outside baseline: NOT CLOSED" ([CX46:201]); evidence: "Baseline
  exclusion and P2/P3 disclosure are correct. B2-PRESENCE.md:3-4,10-11,45-49 still carries selected/prevention/decision/recommendation
  wording. Remove it and retain B2 solely as an unselected, withdrawn draft with explicit REMAINING ENGINEERING; no current owner action
  should rest on it." ([CX46:203]). Blocker ([CX46:111]): "18. v2/docs/records/l4e7/B2-PRESENCE.md:3-4,10-11,45-49 still says
  selected, describes prevention, asks a decision and recommends adoption, despite the withdrawal at lines 13-23 and 57-60. Smallest
  correction: mark B2 UNSELECTED and WITHDRAWN AS DRAFTED throughout and remove the pending owner request. Its defects remain explicit
  REMAINING ENGINEERING outside the baseline."
- **Failed case.** A wording defect; the engineering defects of the draft are HO-G.
- **Attempted correction and the disposition.** The solar author's `4d1d02de`: "Route B2 is UNSELECTED and WITHDRAWN AS DRAFTED" and
  the page "asks no decision, recommends nothing for adoption and credits B2 with no protection" ([B2:4-6]); no owner item, the
  approved interface stands ([B2:39-41]); the baseline does not depend on B2 ([B2:34-37]); the same in [P0SOL:176-188] and [P11:91-99].
- **Unresolved, of substance.** P2 and P3 (and the latent P1) as REMAINING ENGINEERING outside the baseline ([B2:157-164],
  [B2:193-194]): HO-G.
- **Affected provisional outputs.** None in the baseline ([B2:34-37]).
- **Receiving company's task.** HO-G, only if a presence-pair route is ever taken up again as a new route with its own check
  ([B2:157-164]).
- **Reproduce.** `python3 v2/docs/records/l4e7/l4e7_p0sol.py` (section 5, the separate composition `ORDER_E_B2`) ([B2:36-37]).
- **State on this tip.** The wording defect is disposed of in the cited passages; HO-G stays REMAINING ENGINEERING outside the
  baseline.

## 2. The cases the authors handed over

### HO-A: L8P-R9-F1, the guard's latent first failure followed by a second (REMAINING ENGINEERING; inside RE-10)

- **Failed case.** "a first failure that silently removes ONE path is found only by E-13b, each path on its own, and no service
  interval bounds that; a second failure in the other path before it is found removes the trip" ([BRK:1398-1401]); no approved
  requirement permits a latent state ([BRK:1339-1344]).
- **Attempted correction.** The two-path delta (RE-10): "this delta (single failures survived at once)" ([BRK:1402]).
- **Unresolved.** An automatic diagnostic with a bounded interval, or a fault-tolerant redesign ([BRK:1403-1406]).
- **Affected outputs.** "10c's disposition, C-PROT rev 1 for the guard (every claim), L4-E11 section 28" ([BRK:1402-1403]).
- **Task and acceptance.** As RE-10. **Reproduce.** As RE-10.

### HO-B: the single-path retry heating after path 1 is lost (REMAINING ENGINEERING; inside RE-10)

- **Failed case.** With path 1 lost, path 2 relaxes: the FETs carry current at most 43.8 ms in every 0.154 s or more (DERIVED), the
  junction's rise per on-time NOT BOUNDED ([C4:281-286]); "with path 1 lost the protection under those retries is NOT shown (cx46 item
  10, the retry-energy analysis REMAINING ENGINEERING)" ([BRK:1381-1384]).
- **Unresolved.** "the bounded retry-energy analysis of path 2 alone" ([C4:339]).
- **Affected outputs.** "every claim resting on path 2 alone is PROVISIONAL" ([C4:285-286]).
- **Task and acceptance.** The analysis, against C-PROT rev 1 and the FETs' 150 C ([BRK:1343-1344], [CON:199]). **Reproduce.** As RE-10.

### HO-C: L9T5-F21, a TX pin toggled as a GPIO under the limiter's share (REMAINING ENGINEERING; inside RE-5)

- **Failed case.** "a TX pin repurposed as a GPIO and toggled under the limiter's least 4.7 % share disrupts the bus without tripping
  it" ([T10:599-600]); a babbling supervisor can stop the quorum ([T10R:201-202]).
- **Attempted correction.** The transmit-share limiter (RE-5) ([T10:568-577]).
- **Unresolved.** The 2-of-2 peer observation and vote, NOT DRAFTED ([T10:600-602]).
- **Affected outputs.** CON-004's quorum (OPEN), FW-B22 (PROVISIONAL) ([T10:603-604], [CON:328-329]).
- **Task, acceptance, reproduce.** As RE-5.

### HO-D: a latent stuck comparator in either CAN bound (REMAINING ENGINEERING; inside RE-5 and RE-6)

- **Failed cases.** The fault-table row "a limiter's OUTB stuck low" reads "that transceiver's share no longer bounded: LATENT, a second
  fault (a babbler) needed" ([T10:593]); the row "the rail trip's monitor dead or its OUTB released" reads "no current bound for that
  controller: LATENT, a second fault needed" ([T10:595]); each found only on the bench (V-B22, V-B23) with no service interval ([T10:602-603]).
- **Unresolved.** A diagnostic with a bounded interval covering faults after start-up and in the diagnostic itself ([OWN:777]).
- **Affected outputs.** The service's containment (limiter) and "T10's thermal bound and T10-A3's hardware bound" (rail trip)
  ([T10:576-577], [CON:322-323]).
- **Task, acceptance, reproduce.** As RE-5 and RE-6.

### HO-E: VOS0 below the trip, the controller past its 105 C VOS0 limit (REMAINING ENGINEERING)

- **Failed case.** "VOS0 at a current under the trip takes the H743 past its own 105 C VOS0 limit at this air (112.7 C at 0.2452 A):
  the LDO is held, the controller is not; a VOS0 entry no hardware prevents (Layer 5 and Layer 6)" ([T10:643-644]); cx46: "the MCU
  reaches its 105 C VOS0 PRINTED LIMIT at approximately 0.1936 A, MODEL, below the trip band" ([CX46:97]); the sheet's VOS0 junction
  limit 105 C ([T10:65]).
- **Unresolved.** "a hardware bar on VOS0 or its acceptance" ([T10R:221]).
- **Affected outputs.** "controller survival, FW-B20 and FW-B22 service" ([CON:330-331]); cx46: "It does not by itself prove the LDO
  exceeds its criterion." ([CX46:97]).
- **Task and acceptance.** The bar, with the controller inside its printed VOS0 junction limit in every state the design serves.
  **Reproduce.** As RE-5.

### HO-F: D-10 / E-1, the solar guard-on failing cases F1 to F4 and the lower-source back-feed (REMAINING ENGINEERING)

- **Failed cases (MODEL, record l4e7's own transient model on the C2 circuit, a stiff 36 V source, no source resistance credited).**
  F1 at 0.30 uH: PV_F 321.9 V, Q12's VDS 307.4 V, INP 64.3 V, against U21's 100 V and 20 V absolute, the port bank's 100 V, Q12's
  100 V; F2 at about 1.04 uH: PV_F 118.5 V; F3 at the 3.30 uH reference loop: PV_F 83.48 V over the TPS4811-Q1's recommended 80 V row;
  F4 with the guard off at the least loop: slew 56.10 V/us over the 54 V/us SESSION line ([P11:42-51]). The lower-source back-feed: a
  stiff source below the stage's voltage arriving after a withdrawal draws the stage's charge back through Q12's body diode, "Not
  computed here" ([B2:181-190], [SOLO:399-404]). It is an open case, not a failed one: no record computes it, so it neither fails
  nor passes; cx46 counts it inside E-1: "D-10's E-1 retains F1-F4 and the lower-source back-feed case." ([CX46:95], [CX46:188]).
- **Requirements, unchanged, no new exclusion.** REQ-015's 9 to 36 V source class, REQ-016's window, every part inside its absolute
  maximum, the controller inside its recommended conditions while it must act, the SESSION 10 % lines ([P11:68-77]).
- **Attempted correction.** P0-7's sense arrangement C2 (D-16 corrected in draft; U5's sense retired) ([P0SOL:121-162]); the desk's
  alternatives: B1 rejected, B2 withdrawn ([P11:87-99]).
- **Unresolved.** "something must bound the current the source drives into the stage's capacitance through the closed guard, or the
  energy and voltage it delivers to the port when Q12 opens, at every loop" ([P0SOL:156-161]); the routes open to a supplier's
  investigation ([P11:79-109]).
- **Affected outputs.** PROVISIONAL until E-1's correction and S1: IF-01's D-10 claim, R-173 as a protection, R-176 rows 2 and 3, R-180,
  the port's parts and their Layer 6 rows, board E's port layout and Layer 8 fault table, the guard's Layer 9 rows ([P11:114-119]);
  independent of E-1 and "ADDRESSED IN DRAFTS, PROVISIONAL, not completed": D-16's correction and its rows ([P11:119-126]; set 31, 6 October 2026: restated to W4's passage at `786aed2f`; the pre-W4 reading, "Completed independently of E-1", stood at [P11:89-92] on `1c6d56f5`).
- **Task and acceptance.** The correction or a model revision on measured loops only, then S1 on the corrected circuit: PV_F under
  80 V and under 90 V always, INP under 18 V, slew under 54 V/us, Q12 inside its derated SOA, TRK_VS under 31.8 V, the bank under
  1.8 V ([P11:79-85], [P11:144-154]); S1's added rows (a) a source in parallel with a connected panel and (b) the back-feed
  ([P11:154-160]).
- **The back-feed, this ledger's reading (the narrower one; section 6, item E; SESSION).** The lower-source back-feed is REMAINING
  ENGINEERING inside E-1: its model is not computed ([B2:181-190], [SOLO:401-402]), so the receiving company computes it on E-1's
  corrected circuit as part of E-1's correction, against E-1's own requirements, "every part within its makers' absolute maximum
  ratings during the fault" ([P11:72]), with S1's own criterion for the case, "Q12's body-diode current inside its pulsed rating"
  ([P11:160]); S1's row (b) is the later validation of that computation, not a substitute for it. Grounds: the owner's part 23,
  "Supplier item S1 must carry that engineering problem, rather than presenting it solely as an unperformed validation test."
  ([OWN:681]) and "A planned measurement alone does not establish that the selected protection works." ([OWN:702]); part 24, the
  handover of an unsupported correction "not as qualification-only tasks or accepted corrections" ([OWN:799]); part 25, "D-10 remains
  receiving-company engineering item E-1." ([OWN:826]); cx46, "S1 is expressly subsequent qualification of a correction, not closure
  of the current circuit." ([CX46:95]). E-1's acceptance as filed names the cases F1 to F4 ([P11:186-191]); this reading adds the
  back-feed to the cases E-1's correction answers, sets no new limit and, as written, changes no record's text (6 October 2026: once `fnd/w4l4e7` at `786aed2f` is adopted, record l4e7's own page places the back-feed the same way, "It is REMAINING ENGINEERING inside E-1" ([P0SOL:144-145] at `786aed2f`)). Why the narrower reading (SESSION,
  under the coordinator's brief of 6 October 2026): it claims less, since a validation row alone would present an uncomputed case
  as if only a test were missing. Reversed by: a record that computes the back-feed on the present circuit inside its limits, or the
  coordinator's revision of record l4e7's placement.
- **Reproduce.** `python3 v2/docs/records/l4e7/l4e7_p0sol.py` (about 70 s; output [SOLO]) ([P0SOL:233]); its results cache key does
  not hold on this tree ([SOLO:31]) and the long L4-E7 cache recompute is the box's ([CX46:68]).

### HO-G: route B2's own defects P2 and P3 (REMAINING ENGINEERING, outside the baseline)

- **Failed cases.** P2, INP's core shorted to a positive core of the lead: INP at PV_F, over its 20 V absolute maximum from PV_F
  20.0 V (84.62 V at the arriving ring's worst); P3, R96's core shorted to a positive core: as P2; P1, the two presence cores shorted:
  B2's function lost, LATENT ([B2:148-152]).
- **Unresolved.** "monitored or fault-tolerant presence detection" and "INP held inside its absolute maximum", then the timing proof
  ([B2:157-164]); neither is drafted ([B2:163]).
- **Affected outputs.** None in the baseline ([B2:34-37]). **Task.** Only for a presence-pair route taken up again ([B2:157-164]).
  **Reproduce.** As RE-18.

### HO-H: E11-29, the three paralleled battery FETs' sharing (QUALIFICATION, kept apart)

- **The item.** TP-E11-29 (`v2/docs/test-procedures/TP-E11-29.md`) is "written and NOT EXECUTABLE until L4-E9 restates R-159 and a
  supplier agrees in writing to the fixture requirement": at most 10 mW net heat at each heating lead's joint; targets Zw at most
  37.59 K/W, R17 at most 0.294 K/W, the pours 0.1 mOhm; specimen the FET pair and Q42 on a coupon ([ANX:101-109], [P0L2:29]).
- **Class.** "(a QUALIFICATION, kept apart from the architecture blockers)" ([ANX:101]); "3 (qualification, not ARCH)" ([P0L2:29]).
- **Fallback if the sharing fails.** "lower-resistance FETs or a fourth, a design change inside UDC-1, not an architecture change"
  ([ANX:108-109]).

### HO-I: U-01, the cell (EXTERNAL ARCHITECTURE FACT)

- **The fact.** The kit needs 10 A continuous, 18 A for 60 s and 20 A for 2 s at -20 to +80 C plus the storage dwell and recovery; the
  ruled 35E is unsuitable on its own published rows; Saft MP 176065 xtd guarantees the windows, and its 11 A and 22 A are "Recommended,
  not guaranteed at temperature" ([ANX:83-87]).
- **Routes.** (a) Saft's statement (UNSENT), (b) the one-cell screen, (c) the mock-up fit, (d) the HL18650V alternative; adoption of a
  4S1P Saft pack is a separate owner decision, NOT requested; the pack baseline stands ([ANX:89-99]).
- **Affected outputs.** The cell-limit rows LO-01d to g and the dependents PROVISIONAL ([P0L2:26]).

### HO-J: U-02, the sealed case's heat rejection (EXTERNAL ARCHITECTURE FACT)

- **The fact.** Each mode's need against a modelled 1.22 to 2.85 W/K (a MODEL range, not a physical bound) ([ANX:28-37]); T-H1
  (`v2/docs/records/l4e12/T-H1-PROCEDURE-DRAFT.md`) is the receiving company's validation task ([ANX:45-60]).
- **Disposition rule.** A measured failure "demonstrates that THAT arrangement fails under those conditions, nothing more" ([ANX:43]).
- **Affected outputs.** "L4-E12's selection (c) and the hold's trigger window, the fan duty rows (L7), the hot-stop lines of CONOPS 4c's
  reduced mode, and REQ-024's and REQ-052's acceptance rows" ([ANX:60]).

### HO-K: U-04, the charger (B1) on the battery FET pair (EXTERNAL ARCHITECTURE FACT)

- **The fact.** The held pack current with CHRG_INHIBIT set through the drawn pair, and D2's load-step response against the 2.054 V
  margin with the drawn parts, are not printed ([ANX:64-66]).
- **Routes.** (R1) TI's evaluation module, (R2) a coupon of the drafted block (it can carry TP-E11-29's fixture) ([ANX:71-76]); pass
  limits R-161's as printed ([ANX:77-79]).
- **Affected outputs.** "(B1)'s mode table (E11-31), D2's step margin and the held pack current stay PROVISIONAL in L4-E11's page and
  L4-E9's rows IF-10 and U-04" ([ANX:76]).

### HO-L: E11-37, the charger's gate drive into three battery FETs (REMAINING ENGINEERING; the P0 list's row P0-8)

- **Class, and why (SESSION, this ledger's reading).** The P0 list files the row as "E11-37, the charger's gate drive into three FETs",
  its class 2 ([P0L2:25]), "missing evidence boundable at the desk" ([P0L2:11]); L4-E9 reads it as "a qualification gap, not a
  demonstrated failure of the battery FETs" ([L4E9:1134-1135]). This ledger classes it REMAINING ENGINEERING by its own definition
  above (a missing bound the desk could not close): "E11-37 STAYS OPEN: no printed figure decides a three-device gate load against
  TI's 5 nF" ([E11:1459]), and its answer decides a design choice rather than testing a finished one, the evidence blocking only
  "the choice between (S1) and (S2) for the final design" ([E11P:1551]), with a draft owed on a negative answer ([E11:1462-1463]).
  It is NOT a demonstrated failure: no record computes a failing case. Reversed by: TI's answer stated as a limit that admits the
  three, or the coordinator's P0 list classing the row otherwise (section 6, item G).
- **The open case.** BATDRV, the BQ25730's battery-FET gate drive, into the three-device network Q39, Q40 and Q42 on one node
  (rebound from the pair in round 9: [E11:1110-1116], [E11P:1871-1886]): supplement entry, the ideal diode's 30 mV regulation, LDO
  mode at VSYS_MIN, each FET's share of the current and each junction on the shared pour, at -20, 25 and 70 C ([E11:508]).
- **What is bounded, and from which printed figure.** TI prints a selection rule without a drain-source voltage, "the Ciss of
  P-channel MOSFET should be chosen less than 5 nF" (SLUSE65A p.92, [TIQ:74], [TIQ:118]). Nexperia prints the BUK6Y10-30P's Ciss as a
  typical only, 2.36 nF at -15 V, no maximum ([E11:942]): the three are 7.08 nF typical at -15 V and about 8.61 nF near 0 V, 1.416
  and 1.722 times TI's 5 nF ([E11:1111-1112]). From printed maxima: QG(tot) at most 64 nC each at -10 V, 192 nC for the three
  ([TIQ:100-102]); RBATDRV_ON at most 6 kOhm and RBATDRV_OFF at most 2.1 kOhm ([E11:944]), so BATDRV's time constants into the three
  are 42.48 us on at -15 V, 51.66 us on near 0 V and 18.08 us off (MAKER, INFERRED) ([E11:1111-1112]); the charge inhibit's Q49
  moves at most 192 nC and BATDRV sinks at most 3.83 mA while it holds ([E11:1450-1451]). Not bounded by any printed figure: what
  TI's 5 nF protects, and so whether the three's gate load is inside it ([E11:944], [E11:1459-1461]). The P0 list's row says
  "bounded from the printed limit (V2R); the third FET and E11-37 rebound (L4-E11 round 16)" ([P0L2:25]); on this tree the bound
  is in L4-E11's rounds 9 and 11 (section 6, item G).
- **Attempted correction (the desk's comparison).** Round 11 compared three approaches ([E11:1418-1447]): (i)(a) the three kept,
  SELECTED (SESSION) with E-1's bar 40.78 K/W; (ii) two FETs, the BUK6Y10-30P pair the only one under 5 nF, and only on a TYPICAL
  figure (4.72 nF at -15 V, about 5.74 nF near 0 V, over it), its bar 20.39 K/W; (iii) a buffer on BATDRV, no printed basis
  ([E11:1432-1447], [E11:1453-1463]). The check V2 "confirmed round 11's item A (the worst split, the 40.78 K/W bar, E11-37 open) as
  conditional" ([E11P:2465-2467]). Round 11 changed no net: its correction is E-1's acceptance alone ([E11:1464-1465]).
- **The vendor question, drafted and UNSENT.** Q-TI-17 ([TIQ:74-78]), extended to the three devices with its items (a) to (d)
  ([TIQ:96-110]) and given (e) and (f) in round 11 ([TIQ:112-125]); the file's own words: "Nothing here has been sent, and no
  answer is assumed." ([TIQ:3-4]), and "an answer stated as a limit settles the row for production, a typical figure does not"
  ([TIQ:6-7]). The P0 list: "TI's answer Q-TI-17, UNSENT (vendor)" ([P0L2:25]); the annex keeps OW-7's questions to TI "drafted and
  UNSENT" ([ANX:76]).
- **Affected provisional outputs.** D-14, "CONDITIONAL on E11-29, E11-30 and E11-36 with E11-37 OPEN" ([L4E9:1134]); UDC-1's
  selection (S1), reversed by "a negative Ciss answer or bench (R-183)" ([L4E9:1401]); R-183, OWED ([REG:279]); E-1's installed
  acceptance (i)(a), reversed by "a negative answer to Q-TI-17 (E11-37): then (ii), a draft owed" ([E11P:2416]); the charger
  draft's release (E11-27) ([E11P:1455]); the three's production conformance, which "needs one of them (record l9stk's C3)"
  ([E11P:1885-1886]); U-04's route (R1), after which E11-37 stays open ([ANX:73]), and E11-31, whose specimen is E11-37's
  ([L4E9:754]). Not affected by the count: IF-1's hold and DD-7's inhibit ([E11:1450-1451]). The supplier validation annex carries
  no row for E11-37 of its own; it names it only among what stays open after route (R1) ([ANX:73]).
- **Receiving company's task and acceptance.** One of the two routes the records state ([E11:508], [REG:279]): TI's statement of
  what the 5 nF bounds for three P-channel FETs on one BATDRV, stated as a limit ([TIQ:6-7]); or the bench of block E11-37
  ([E11P:1673-1690]) on TI's BQ25730 evaluation hardware modified as drafted or the controlled first prototype of board A, at -20,
  25 and 70 C, each drain's current and each junction read, its pass criterion "supplement entry, the 30 mV ideal-diode regulation
  without oscillation, LDO mode inside its printed band" ([E11P:1455]), where "a result with the pair does not transfer to the three,
  nor the three's to the pair." ([E11P:1688-1689]). On a negative answer the engineer's choice and its draft: "the pair, its bar
  20.39 K/W measured on the coupon, Q42 removed (a draft then owed)" ([E11:1462-1463]), or (S2), one BUK6Y10-30P with a heat path
  through the case ([L4E9:1401]); the pair is itself under 5 nF only on a typical figure, so that fallback also rests on Q-TI-17 (e)
  ([E11:1439-1440]). Nothing here is bought, sent or measured.
- **Reproduce.** `python3 v2/docs/records/l4e11/l4e11_power.py` (sections 16c, 19d and 21; output [E11]), the held makers' sheets
  fetched by sha256 by `v2/docs/records/l4e11/fetch_held_back.py`; the record's tests `t_round11_*` in
  `v2/ecad/tools/tests/test_l4e11.py`.
- **State on this tip.** OPEN: "E11-37 OPEN (TI or the bench)" ([E11:1465]).

## 3. Closed by the correction (four) and closed as conditional (two), each in its stated scope only

| Id | cx46's words, as filed | The scope it states (never widened here) | What stays open beside it |
|---|---|---|---|
| CL-3 | "3. Q1 obsolete draft-script texts: CLOSED BY THE CORRECTION" ([CX46:126]) | "apply_gen_sch_a_paloop.py:29-36,98-107 and apply_gen_sch_d_paloop.py:43-48 replace the obsolete band and printed-corner guarantee with the MODEL band and PROVISIONAL status. No additional blocker for this textual correction." ([CX46:128]); on this tip [PALA:33-35], [PALD:46-52] | RE-2 (F01 PROVISIONAL) |
| CL-11 | "11. Q6 cold-connection guarantee: CLOSED BY THE CORRECTION" ([CX46:166]) | "This closes the unsupported guarantee's disposition, not B2's engineering." ([CX46:168]); [B2:122-141] | HO-G; HO-F |
| CL-12 | "12. Q6 presence-pair short and protection credit: CLOSED BY THE CORRECTION" ([CX46:171]) | "Protection credit is removed; baseline ORDER_E excludes B2. No claim that B2 closes D-10 survives in those corrected disposition rows." ([CX46:173]); [B2:143-164] | HO-G (P2, P3); HO-F |
| CL-15 | "15. D-10 retained as remaining engineering: CLOSED BY THE CORRECTION" ([CX46:186]) | "This disposition is correct; D-10 itself remains OPEN REMAINING ENGINEERING." ([CX46:188]); [P11:33-126] | HO-F (D-10 / E-1 itself) |
| CO-14 | "14. Q7 regeneration and stable bindings: CLOSED AS CONDITIONAL" ([CX46:181]) | Condition: "retain or reproduce successful byte-identical repeated output runs on these inputs. Fresh stability replay was not performed here; the explicitly identified long L4-E7 cache recompute was skipped and remains the box's task." ([CX46:183]); kept in `v2/docs/records/l9t5/stability/` ([T5R:129-132]); blocker ([CX46:110]): "14. v2/docs/records/l9t5/README.md:130 claims identical second-pass outputs. Input identity is verified, but fresh stability execution is not established by this review. Smallest evidence step: retain the two pinned-run outputs and successful process records or reproduce their byte identity through the coordinator's authorised workflow; the long cache recompute remains separately identified." | the condition on the tip read: section 6, item C |
| CO-16 | "16. P0-4 eFuse conditions retained: CLOSED AS CONDITIONAL" ([CX46:191]) | "Those conditions must be fulfilled before the affected design claims become unconditional." ([CX46:193]); the conditions: the connector contacts at the inside air PROVISIONAL with the supplier's 76 C chamber task (pass at or under 85 C for J_LIME, 105 C for the IDC socket and cable) ([EFS:150-161], [EFO:425-431]); the RockBLOCK charge pads OPEN as a build condition ([EFS:162-165], [EFO:432-434]); the exact part and value obligations ([EFO:621-622]) | EF-F01 to EF-F03 each read as a DESIGN DEFECT, OPEN, corrected by a DRAFTED change, in the register ([EFO:614-617]); round 2 has no independent check of its own ([EFS:213-214]) |

## 4. The claims a remaining item weakens, and the state each reads on this tip

| Claim | Where the candidate states it | Weakened by | State it reads (cited) |
|---|---|---|---|
| The thermal guard's C-PROT rev 1 verdict | [CON:194-203]; [C4:271-275] | HO-A, HO-B (RE-10); L8P-R9-F2 (RE-9) | PROVISIONAL: "C-PROT rev 1 for the guard PROVISIONAL" ([BRK:1420-1422]); the connected row "reads REMAINING ENGINEERING" ([CON:199-200]) |
| The supervisors' LDOs' 125 C sustained bound (rev V, R602 14.0 k) | [CON:213-216]; [CON:293-317]; [T10:614-633] | RE-7 (the periodic peak); RE-6 and HO-D (the latent rail trip) | the universal sustained bound WITHDRAWN, PROVISIONAL ([T10:620], [T10:664-665]); the worst-case margin row PROVISIONAL/OPEN ([CON:314-317]) |
| CON-004's quorum service | [T10:587-606]; [CON:130-139] | HO-C, HO-D (RE-5) | OPEN ([T10:603], [T10R:221]) |
| FW-B22, the quorum's schedule | [HWFW:76-82]; [T10:554-561] | HO-C, HO-D; HO-E (service) | PROVISIONAL, a traffic MODEL ([T10:560-561], [HWFW:11]) |
| FW-B20 and the controller's survival | [T10:605-606]; [T10:643-644] | HO-E | PROVISIONAL ([CON:330-331], [T10:605-606]) |
| T10-A3, the LDO input headroom at the hardware bound (+0.1311 V as drawn) | [CON:248]; [CON:313-317]; [T10:611-613] | RE-6, RE-7, RE-4 (the shift) | PROVISIONAL at a peak ([T10:611-613]); on an INFERRED dropout, V-T10-DROP ([CON:283-286]) |
| F01's 15.5 V case (C-ALLTX rev 3 at the cap, 15.1308 V) | [CON:123-124]; [F01:209-214] | RE-2; B-PA1, B-PA2 | PROVISIONAL ([F01:212-214], [CON:334-335]) |
| The return's ratings (the distributed study) | [CON:163-176]; [DIST:112-124] | RE-4 (V6-B1); L8R2-F43, L8R2-F44 (vendor curves) | V6-B1 OPEN, REMAINING ENGINEERING ([CON:174], [DIST:125]) |
| J_PA's VH lead at the cap's top 6.9259 A | [CON:157-161] | RE-2 (the cap); L8R2-F43 (JST's curve MISSING) | PROVISIONAL ([CON:160-161], [T5R:194-196]) |
| L4-E11 section 28's 20c and 20f rows with the guard | [E11:2036-2065] | HO-A, HO-B; RE-9 | PROVISIONAL, not closed ([E11:2066-2071]) |
| IF-01's protection of the solar entry against D-10; R-173 as a protection | [P11:46-51] | HO-F | PROVISIONAL until E-1's correction and S1 ([P11:114-119]) |
| The eFuses' downstream contacts at the inside air | [CON:179-186]; [EFS:143-161] | CO-16's conditions | PROVISIONAL at the inside air ([EFO:425-431]) |
| The battery switch's gate drive: D-14 with UDC-1's (S1), the three BUK6Y10-30P on one BATDRV, and E-1's installed acceptance at (i)(a) (cited at `6fe398e9`) | [L4E9:1131-1135]; [L4E9:1401]; [E11:1453-1458] | HO-L (E11-37) | OPEN: "E11-37 OPEN (TI or the bench)" ([E11:1465]); D-14 "CONDITIONAL on E11-29, E11-30 and E11-36 with E11-37 OPEN" ([L4E9:1134]); R-183 OWED ([REG:279]) |

## 5. Summary

Counts: remaining engineering 20; qualification 1; external architecture fact 3; closed 4; conditional 2.

| Item | Class | Receiving company's task | Affected outputs | Reproduce |
|---|---|---|---|---|
| RE-1 | remaining engineering | none of engineering; read states from the records (the list is the coordinator's) | P0 list rows P0-1 to P0-7 ([P0L2:18-24]) | text |
| RE-2 | remaining engineering | bound the reference at its held load and release; then V-PA-REF, B-PA1, B-PA2 | F01 / D-17, C-ALLTX rev 3 at the cap, U13's room, PA rail rows, R-227, R-238 | `v2/docs/records/l9t5/l9t5_f01.py` |
| RE-4 | remaining engineering | XT60-F lands, real sites, justified distributed resistance, each LDO's shift | the return's rows, T10-A3's shift, P0-2 | `v2/docs/records/l8r2/l8r2_dist.py` |
| RE-5 | remaining engineering | peer-silence or diagnostic circuit and recovery proof | CON-004, FW-B22, L9T5-F21, L9T5-F16, R-245 | `v2/docs/records/l9t5/l9t5_t10.py` |
| RE-6 | remaining engineering | a rail-trip response on printed timing and its full network | V-B23 (withdrawn), T10 thermal and T10-A3 bounds | `v2/docs/records/l9t5/l9t5_t10.py` |
| RE-7 | remaining engineering | peak-current containment or a periodic electrothermal solution with uncertainty | the sustained bound, the worst-case margin row, T10-A5 limits | `v2/docs/records/l9t5/l9t5_t10.py` |
| RE-8 | remaining engineering | a rev X part's qualification (V-B20 at most 0.2183 A) on RE-7's bound | revision X HELD; L9T5-F23 rows | `v2/docs/records/l9t5/l9t5_t10.py` |
| RE-9 | remaining engineering | replay 20f and 22 at the owners' restated allowance | rows resting on the DOCK_EN_OUT allowance | `v2/docs/records/l4e11/l4e11_power.py` |
| RE-10 | remaining engineering | retry-energy analysis; automatic diagnostic or fault-tolerant redesign | C-PROT for the guard, L4-E11 28, R-244 | `v2/docs/records/l8p/l8p_c4.py` |
| RE-13 | remaining engineering | re-run the connected trace after the seven rows close | `l9t5_connected.out` sections 5 to 10 | `v2/docs/records/l9t5/l9t5_connected.py` |
| RE-17 | remaining engineering | HO-A to HO-E | section 4 | as RE-5, RE-10, RE-13 |
| RE-18 | remaining engineering | HO-G, only if a presence-pair route is taken up again | none in the baseline | `v2/docs/records/l4e7/l4e7_p0sol.py` |
| HO-A | remaining engineering | automatic diagnostic with a bounded interval, or a redesign | C-PROT for the guard, L4-E11 28 | `v2/docs/records/l8p/l8p_c4.py` |
| HO-B | remaining engineering | bounded retry-energy analysis of path 2 alone | claims on path 2 alone | `v2/docs/records/l8p/l8p_c4.py` |
| HO-C | remaining engineering | 2-of-2 peer observation and vote (not drafted) | CON-004, FW-B22 | `v2/docs/records/l9t5/l9t5_t10.py` |
| HO-D | remaining engineering | a diagnostic for the latent comparators | service containment; T10 thermal and T10-A3 bounds | `v2/docs/records/l9t5/l9t5_t10.py` |
| HO-E | remaining engineering | a hardware bar on VOS0 or its acceptance | controller survival, FW-B20, FW-B22 | `v2/docs/records/l9t5/l9t5_t10.py` |
| HO-F | remaining engineering | E-1's correction or a measured model revision, the lower-source back-feed computed inside it; then S1 (its row (b) the later validation of that computation, not a substitute), S2 | IF-01, R-173, R-176, R-180, the port's parts and layout | `v2/docs/records/l4e7/l4e7_p0sol.py` |
| HO-G | remaining engineering | monitored detection, INP's protection, the timing proof (outside the baseline) | none in the baseline | `v2/docs/records/l4e7/l4e7_p0sol.py` |
| HO-H | qualification | TP-E11-29 on a coupon, after R-159's restatement | UDC-1's sharing rows | `v2/docs/test-procedures/TP-E11-29.md` |
| HO-I | external architecture fact | Saft's statement and/or the one-cell screen; the fit | LO-01d to g and dependents | `v2/docs/records/l4e10/clarification/saft-mp176065xtd.txt` |
| HO-J | external architecture fact | T-H1 per mode | L4-E12's selection, fan duty, hot-stop lines, REQ-024, REQ-052 | `v2/docs/records/l4e12/T-H1-PROCEDURE-DRAFT.md` |
| HO-K | external architecture fact | route (R1) and/or (R2) to R-161's limits | (B1)'s mode table, D2's margin, the held pack current | `v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md` |
| HO-L | remaining engineering | TI's statement as a limit, or block E11-37's bench with the three; on a negative answer the pair (a draft owed) or (S2) | D-14 and UDC-1's (S1), R-183, E-1's (i)(a), the charger draft's release (E11-27) | `v2/docs/records/l4e11/l4e11_power.py` |
| CL-3 | closed | none (textual correction) | none beyond RE-2 | text |
| CL-11 | closed | none (the guarantee's disposition) | none beyond HO-F, HO-G | text |
| CL-12 | closed | none (the credit's removal) | none beyond HO-F, HO-G | text |
| CL-15 | closed | none (the disposition; D-10 itself is HO-F) | none beyond HO-F | text |
| CO-14 | conditional | byte-identical repeated runs bound to the candidate | every output of the cascade | `v2/docs/records/l9t5/stability/regen_cascade.sh` |
| CO-16 | conditional | the contacts at the inside air, the pads OPEN, the part obligations | the eFuse rows at the inside air | `v2/docs/records/efuse/efuse_check.py` |

## 6. Gaps and contradictions found while reading (named with both citations; this ledger settles none, apart from item E's reading for its own classification)

- **A. One finding identifier, two findings.** Slot A's L9T5-F26 is J_PA's VH derating ([T5R:194-196], [CON:356-358]); Slot C's
  `T10-ROUND5.md` names "L9T5-F26 (Slot A, its `l9t5_connected.out` 193-199, 282-301, 350-352)" for the connected verdicts inheriting
  its OPEN claims ([T10R:227-229]). L9T5-F27 settled a similar collision for the decisions D9 and D10 ([T5R:174-176]).
- **B. Two figures for the declared upper bound of the return.** 27.8159 A with J_5V_IOC at 1.3800 A in the study ([DIST:86]) and
  27.9108 A in the one-node model and the README ([P0R:21], [T5R:59]), whose J_5V_IOC term is the declared peak 1.4749 A ([CON:151]).
- **C. The stability condition on the tip read (CO-14).** `stability/DIGESTS-cr3.txt` records `l9t5_f01.out` at a sha256 that differs
  from the file on `1c6d56f5`, and `l9t5_connected.out` pins `l9t5_f01.out` as `2c590640a2f7322b` ([CON:21]) while the file on this
  tip begins `2aa78a95`; the checkpoint changed only the label of that output's PRINTED-rows band, which now reads "NOT a bound on the cap"
  ([F01:132-134]), and its commit subject ends with the words outputs regenerating. The other seventeen outputs of the cascade equal their DIGESTS-cr3
  digests on this tip ([STAB]).
- **D. The response time and the countermodel's peak, two MODEL readings each.** V-B23's response: 0.9259 s (cx46, from 0.1739 A)
  ([CX46:89]) and about 0.98 s (the record, from the bounded state) ([T10:584-586]). The countermodel's peak: 127.55 C ([CX46:91])
  and 127.54 C (the record's reproduction) ([T10:619-620]). Neither difference changes a state: both sides read over 125 C and over
  0.2 s.
- **E. The lower-source back-feed's placement.** cx46 counts it among E-1's retained cases ([CX46:95], [CX46:188]); the records list it
  as "not computed here" and carry it as an added row (b) of S1, a validation run ([B2:181-190], [SOLO:399-404], [P11:154-160]), while
  E-1's failing-case table lists F1 to F4 only ([P11:46-51]). Part 23 asks S1 to carry D-10's engineering, not to present it as an
  unperformed test ([OWN:681]). **The ledger's reading (amendment of 6 October 2026) is the narrower one** (HO-F): the back-feed is
  REMAINING ENGINEERING inside E-1, computed by the receiving company as part of E-1's correction, and S1's row (b) is the later
  validation of that computation, not a substitute for it. Record l4e7's own text stands as written ([B2:181-190],
  [SOLO:399-404], [P11:154-160]): it is not this ledger's file, and the contradiction between that text and this reading is the
  coordinator's to carry to the next set. (6 October 2026: once `fnd/w4l4e7` at `786aed2f` is adopted, record l4e7's L4E7-P0SOL.md
  section 4 (a) carries this reading ([P0SOL:141-149] at `786aed2f`), which answers the contradiction on record l4e7's side.)
- **F. The P0 list is revision 2 (RE-1)** ([P0L2:1]) while the records carry the cx46 disposition ([T5R:1]).
- **G. E11-37's references and class (added 6 October 2026, cited at `6fe398e9`).** The P0 list's row P0-8 cites "(V2R)" and
  "(L4-E11 round 16)" for the bound and the rebinding ([P0L2:25]); L4-E11's rounds 14 to 16, which answer V2R, V2RF and V2RG, are
  TP-E11-29's fixture and heavy leads and name no E11-37 ([E11:1749-1998]); the rebinding to the three devices is round 9's 19d
  ([E11:1110-1116]) and the three approaches round 11's section 21 ([E11:1405-1466]), the round the check V2 read
  ([E11P:2465-2467]). The class: the P0 list's 2, "missing evidence boundable at the desk" ([P0L2:11], [P0L2:25]), and L4-E9's
  "a qualification gap, not a demonstrated failure of the battery FETs" ([L4E9:1134-1135]), against this ledger's REMAINING
  ENGINEERING (HO-L), the narrower claim about the design (it does not treat the three-device network as a finished design awaiting
  a test). The list and L4-E9 are the coordinator's; this ledger edits neither.

## 7. Reproducing the records (common to every item)

From the repository root, each record script runs with `python3` and writes its `.out` beside it; the committed outputs were
regenerated only through the coordinator's tool, which runs a generator twice and keeps an output only when both runs exit 0 and
agree byte for byte ([T5R:129-132], `v2/docs/records/l9t5/stability/regen_cascade.sh`). The dependency order of the P0 cascade is the
order in `v2/docs/records/l9t5/stability/regen_cascade.sh`. Makers' sheets held back by their terms are fetched and checked by
sha256 by each record's `fetch_held_back.py` and never committed ([F01:5]). No KiCad is needed for the netlists
(`v2/docs/records/l8p/gen_netlist.py`). The record tests run with `env -C v2/ecad/tools/tests python3 run.py <module>`
(`v2/docs/records/l8r2/README.md`).
