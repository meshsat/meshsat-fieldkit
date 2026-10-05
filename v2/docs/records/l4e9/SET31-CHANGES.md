**DONE:** section 8 (blocks 8 and 8a to 8g) and PC-01 to PC-16 applied to the page, the register, the generator's data and renderers, its output (regenerated through `_bin/regen_out.py`) and `test_l4e9.py`'s expectations; the overlaps reconciled to the narrower claim; `run.py test_l4e9. test_public_hygiene.` 68 passed, 0 failed, 0 skipped. **NOT DONE:** the re-pins owed at the freeze (records l4e10 and l4e11 pin this page, l6r2 the register; L4-E9's three l8p copies, PC-04), LH-12 (not this record's file), the 45.88 K/W statements outside PC-05's scope (list C). **NEXT:** the coordinator integrates after commit 2b (the cascade outputs this branch's output pins) and re-pins at the freeze.

# Set 31: L4-E9's page, register and generator brought to the set 30 candidate (MESHSAT-1357, 6 October 2026)

**Base.** `fnd/l4e9s31` from `bbba3e53e396d3fe0f8ddd2f38d0c169bcc99c45` (set 30's integration 2a on `fnd/p0pwr`: the generator re-pinned,
its D-10/D-16 citation check reading L4-E7's P0 output too). **Inputs** (read with `git show`, not in this branch): the section 8
restatement `v2/docs/records/l4e9/L4E9-SECTION8-SET30.draft.md` at `fnd/l4e9s8` f47d1fc4 ("s8" below: blocks 8 and 8a to 8g, its
sections A to D) and the page consistency draft `v2/docs/records/l4e9/L4E9-PAGE-CONSISTENCY-SET30.draft.md` at `fnd/l4e9pc` 8282895e
("PC" below: PC-01 to PC-16 and its contradictions C-1 to C-5). Both drafts were written on 7070f106; the page and the register are
unchanged between 7070f106 and bbba3e53, so their line citations hold; the generator's lines after its PINS table moved by two.

**What this is.** The record of every change of set 31, its source item and its class. It designs nothing, consumes no review and
changes no verdict of a check. The criteria's verdict words are the coordinator's (the set 31 brief), written where s8 left
`[COORDINATOR: criterion N]`. Classes as PC defines them: PRESENTATION OR BINDING (the text says what its cited record already says,
or a count, a pin or a regeneration follows from data in the tree) and CLAIM CHANGE (what the page or the register asserts about the
design changes; every one here narrows a claim or states an open state). No figure a record computes was changed; where a printed
figure differs between records both are printed with their bases. Prototype framing: nothing in the kit is built, bought, powered
or measured.

**How it was run.** The generator on this branch alone refuses at its pins of four cascade outputs (l4e10, l4e11, l4e12 and L4-E7's
P0 output) that 2a pinned at the bytes of the coordinator's commit 2b, not yet committed. For the regeneration and the tests only,
those four outputs were placed in the working tree at exactly the pinned digests (aab5ae6b, 1938c400, 31883eca, 28a5b9fd; read from
the coordinator's uncommitted 2b bytes), and restored to this branch's bytes before every commit; no commit of this branch carries
them. The committed `l4e9_power_path.out` (regen_out: replaced, twice byte-identical, every printed pin current) therefore pins 2b's
digests, as 2a's generator already did. Tests: `python3 -u v2/ecad/tools/tests/run.py test_l4e9. test_public_hygiene.` printed
"tests: 68 passed, 0 failed, 0 skipped" (on the base with the same four outputs: 55 passed, 13 failed).

## A. The changes

| # | Change | Files | Source item | Class |
|---|---|---|---|---|
| 1 | Section 8's head: the DESIGN gate stated apart from the DESK handover gate of part 19, the five states stated once, the citation alias table (lines at 7070f106), the criteria table with the coordinator's verdicts (1 CONDITIONAL, 2 FAIL, 3 PASS, 4 PASS, 5 CONDITIONAL) and their bases as the brief gives them, "closes: NO", set 29's inconsistency, what the P0 round changed | page; generator `GATE` (criteria 1, 2 and 5's constraint and overturn texts) | s8 block 8 | CLAIM CHANGE (criterion 2 CONDITIONAL to FAIL; the verdicts the coordinator's) |
| 2 | 8a: D-10, D-16 and D-17 restated; the P0 round's Layer 8 and 9 findings table; the history note over set 27 to 29's paragraphs | page; `DEFECTS` (D-10, D-16, D-17: state, options, resolution; D-16's constraint) | s8 block 8a; PC-01, PC-02, PC-15 | CLAIM CHANGE |
| 3 | 8b: the cell "Who supplies it" of U-01, U-02 and U-04 (the receiving company since part 19); the set 30 paragraph | page; `CHOICES` supplier fields | s8 block 8b | PRESENTATION OR BINDING (the annex's footing) |
| 4 | 8c: the added paragraph; set 29's paragraph split at the coordinator's sentence | page | s8 block 8c (reconciled, B4) | PRESENTATION OR BINDING |
| 5 | 8d: part 19's footing; OW-4's document cell gains P0-7's two drafts (sha256/16 f3adcf9cebc9655d, 43c524c32e68c085, read on this tree) | page | s8 block 8d | PRESENTATION OR BINDING |
| 6 | 8e: the four checks of the P0 candidate as filed, the method ended, cx46's eighteen items and where each is carried; astra-check-l4close-2 kept as history; the proposed heading; output section 28 gains the checks | generator `cons_check2`, `cons_check2_lines` and their data; page | s8 block 8e (A3) | PRESENTATION OR BINDING (verdicts quoted as filed) |
| 7 | 8f: the ledger's classes after cx46, the withdrawn items, the register's own classes recounted, the D-10, D-16, D-17 and U-01 rows, UDC-2's last cell | generator `cons_class_block`, `D_CLASS`, `D_NEXT`, `U_CLASS`, `cons_comparisons`; page | s8 block 8f (A4); PC-09 | CLAIM CHANGE |
| 8 | 8g: the receiving company's task list; set 29's phase 1 tasks restated (P1-1 narrowed to E-1; P1-2 and P1-3 corrected at the desk by record l8r2); set 29's phase 2 lists rendered from the register | generator `cons_supplier_block`, `cons_p1_tasks`; page | s8 block 8g (B4, B5) | CLAIM CHANGE |
| 9 | FAN_OK withdrawn everywhere: D-17's state, resolution and next action; In short; 1c's C05; 1d's IF-10 cells; R-28's change-list text; R-213 WITHDRAWN; IF-10's check label and the FAN_OK order constraint labelled as a withdrawn row (arithmetic unchanged) | generator; page; register | PC-01 (a) to (f) | CLAIM CHANGE; (f) PRESENTATION OR BINDING |
| 10 | D-16 ADDRESSED IN DRAFTS in In short, the exit row, the decisions, section 12; R-189 restated as S4 and S3 (set 29's acceptance kept for the RSENSE1 arrangement only if restored); R-186 WITHDRAWN and out of `KED_ROWS` | generator; page; register | PC-02 | CLAIM CHANGE |
| 11 | Section 6's 1d counts and its defects paragraph; the exit table's D-17 row; section 12's open defects with D-17 | page; generator `cons_exit_defects` | PC-03 | CLAIM CHANGE |
| 12 | R-206 names U101 LM5069MM-1, the latch-off variant; R-206 to R-208's From name record l8p in the tree | register | PC-04 | PRESENTATION OR BINDING |
| 13 | R-159 restated from E11-29's row word for word (in its Acceptance), its Item summarising it; 5d's E11-29 row, In short and section 6's U-04 row at 40.78 K/W without m, the design target and round 13's method; the generator reads E11-29's row from L4-E11's pinned output (`z3m`, `zw`, `r17t`) | register; generator; page | PC-05 | CLAIM CHANGE |
| 14 | R-246, board P's ideal diode (DD-5), in the register, `CHANGE_ORDER`, `ORDER_CONSTRAINTS` and `CHANGE_SCRIPTS`; `G_L8P` names record l8p's one release | register; generator | PC-06 | CLAIM CHANGE |
| 15 | The counts regenerated (In short, 5b); section 11's counts (235 items); dated paragraphs in section 11 and the register; WITHDRAWN in the register's States legend | page; register | PC-07 | PRESENTATION OR BINDING |
| 16 | R-28: K4's off-list without the fans; its acceptance without FAN_OK | register | PC-08 | CLAIM CHANGE |
| 17 | R-225, R-227, R-232, R-238, R-242, R-244 and R-245 classed KNOWN ENGINEERING DEFECT, ASSIGNED to the ledger's RE-2, RE-4, RE-5 to RE-7 and RE-10 (`RE_ROWS`, `RE_TASK`) | generator; register's Class and Next action (the script's rule) | PC-09 | CLAIM CHANGE |
| 18 | R-236 and R-237 with cx46 item 16's conditions (CO-16) | register | PC-10 | CLAIM CHANGE |
| 19 | In short quotes cx45 and cx46 and keeps astra-check-l4close-2 as history | generator `cons_in_short`; page | PC-11 | CLAIM CHANGE |
| 20 | "l9stk's E-1" (R-159), "l4e7's E-1" (R-240), "decision D-16" (section 12) | register; page | PC-12 | PRESENTATION OR BINDING |
| 21 | R-206 to R-208 in one release with R-222, R-244 and R-246 (record l8p's drafts) | register; generator `G_L8P` | PC-13 | PRESENTATION OR BINDING |
| 22 | IF-01's status on D-10's port-level defect; IF-02 and section 12 with P0-7's figures beside the output's | page | PC-14 (reconciled, B6) | CLAIM CHANGE |
| 23 | D-10 as P0-7 states it (E-1, F1 to F4, the lower-source back-feed) in In short, the exit row, section 6 and section 12; route B2 UNSELECTED and WITHDRAWN AS DRAFTED with no owner item in the data and the `OUT_OF_BASELINE` comment | generator; page | PC-15 | CLAIM CHANGE |
| 24 | R-48 and R-190: FIX, CHECK and APPLY record l8r2's desk drafts (R-221; R-190 with R-228), the receiving company's task only if that check refuses them (`DESK_ROWS`); section 6's list and section 12 | generator; register; page | PC-16 | CLAIM CHANGE |
| 25 | R-227's band 6.3518 to 6.9259 A as `l9t5_f01.out` prints it after cx46 | register | s8 section C, C4 | PRESENTATION OR BINDING |
| 26 | The class rule reads WITHDRAWN first (R-213 is a TEST row, R-186 an EVIDENCE row) | generator `cons_classes` | PC-01 (e), PC-02 (e) | PRESENTATION OR BINDING |
| 27 | `l4e9_power_path.out` regenerated | output | all | PRESENTATION OR BINDING |

**The test expectations changed, each with its evidence basis in a comment** (`v2/ecad/tools/tests/test_l4e9.py`): a WITHDRAWN register
row is admitted when it names its withdrawal (the register's R-210 "WITHDRAWN 5 October 2026: FAN_OK is rejected"; L4E7-P0SOL.md
section 5 for R-186); route B2's draft is exempt from the register and change-list completeness checks through the script's
`OUT_OF_BASELINE` (B2-PRESENCE.md; L4E7-P0SOL.md section 4); D-10 reads OPEN with E-1 and F1 instead of set 29's opening words (L4E7-P0SOL.md
section 4; cx46 item 15); the open defects are D-10 and D-17 and D-16 reads ADDRESSED IN DRAFTS with R-240 (L4E7-P0SOL.md section 5;
cx45's summary; cx46 item 2 for D-17) in five places; D-16 is a PHYSICAL UNCERTAINTY (S3 and S4, SUPPLIER-P1-1-P0SOL.md); D-17's next
action may start ASSIGN (cx46 item 2; the ledger's RE-2). No test was removed; each changed assertion still fails on the old state.

## B. The reconciliations (the narrower claim taken where the drafts overlap)

1. **D-16's state.** s8 8a: "CORRECTED IN DRAFT by P0-7" with S3 and S4 PROVISIONAL; PC-02: "ADDRESSED IN DRAFTS", PROVISIONAL on S3.
   Taken: ADDRESSED IN DRAFTS (the page's own word, never RESOLVED, PC C-1) with both S3 and S4 PROVISIONAL and "not independently
   accepted as closing D-16"; class PHYSICAL UNCERTAINTY (s8 A4).
2. **D-17's state.** s8 8a: "PROVISIONAL, REMAINING ENGINEERING"; PC-01: "OPEN: a correction DRAFTED and PROVISIONAL". Taken: OPEN
   (REMAINING ENGINEERING, RE-2) with its correction PROVISIONAL; it keeps criterion 2 from PASS under the gate's own rule.
3. **The P0 rows' classes in 8f.** s8 8f: "the 25 rows R-220 to R-245, none R-241, are all SETTLED WORK" ([REG:314-338]); PC-09: seven
   of them KNOWN ENGINEERING DEFECT. Taken: PC-09; 8f's counts are recomputed from the register after set 31 (SETTLED WORK 138, PHYSICAL
   UNCERTAINTY 78, KNOWN ENGINEERING DEFECT 13, UNCERTAIN DESIGN CHOICE 6), not s8's base counts (142, 79, 7, 6).
4. **8c and 8g against PC's register restatements.** s8 8c and 8g item 2 name the restatements as owed; PC-05, PC-07, PC-08, PC-09,
   PC-16 and s8's C4 make them. Taken: the texts say they are made in set 31 and that R-48 and R-190 stay OPEN, nothing credited.
5. **8g item 4.** s8: TP-E11-29 NOT EXECUTABLE until L4-E9 restates R-159; PC-05 restates R-159. Taken: still NOT EXECUTABLE until
   its quotation and check are re-taken against the restatement and a supplier agrees the fixture requirement.
6. **IF-02's figures.** PC-14 replaces the output's 2.5485 A and 93.5521 W with P0-7's 2.5378 A and 93.5783 W; this record's output
   computes the former on the drafted RSENSE1 sense (out 4). Taken: both printed, each with its basis (no computed figure changed).
7. **R-159.** PC-05 restates it from E11-29's row word for word; set 29's row also carried the block's transfer rule after the owner's
   L4-QR01 and the superseded 34.42 C/W bar, which E11-29's row does not repeat. Taken: E11-29's row plus those kept obligations.
8. **D-17's What and constraint cells.** s8 replaces the constraint with C-ALLTX rev 3's figures (15.5162 and 16.0718 V); the
   script refuses D-17 without Layer 9's round 2 basis (16.214 V) in its constraint and options, and requires every constraint
   figure printed by its output. Taken: set 29's constraint kept; C-ALLTX rev 3's figures carried in the page's State cell.
9. **D-10's and D-16's options.** s8 replaces set 29's text; the script's citation check, the tests and the history rule hold set
   29's analysis. Taken: s8's text first, then "set 29's options, kept as history". s8's "U5 0.956 V resistive at 3.30 uH" is written
   without the figure: L4-E7's pinned sources do not print 0.956 (the citation check refuses it); L4E7-P0SOL.md section 2 does.
10. **Criterion 2's constraint.** s8's text, prefixed by "two material defects are open: D-10 (E-1) and D-17 (RE-2)" and the
    coordinator's list of open remaining engineering, and followed by set 29's other rows (D-13, D-14, D-15 with its status, D-11,
    R-175), which s8 points to by line only.
11. **Set 29's names kept as history.** D-10's state and In short keep "set 29's B6-ENG-1 as P0-7 restates it" and "round 2's 3.30
    uH loop stays WITHDRAWN as a passing floor" (true on L4E7-P0SOL.md section 4: F3 reads at that loop as a reference).
12. **The five states once.** s8 states them in its head and again under the table; set 31 states them once, in the head, beside the
    DESIGN and DESK gates, as the brief asks.

## C. Not reconciled (both citations; this record settles none)

Citations `[ALIAS:N]` are lines at 7070f106 as in the alias table at the head of the page's section 8; TP29 is
`v2/docs/test-procedures/TP-E11-29.md`.

- **R17's design target:** 0.29 K/W in E11-29's row ([E11:500] at 7070f106) against 0.294 K/W in the annex ([ANX:105]) and
  TP-E11-29's table ([TP29:729]); R-159 prints L4-E11's and names the other (PC C-3).
- **Record l8p's one release:** "five drafts" ([BRK:265]) against the register's R-206, R-207, R-208, R-222, R-244 and R-246; the
  exact membership is record l8p's (PC C-5).
- **The case at the cap:** 15.1307 V in the P0 list ([P0L:18]) against 15.1308 V in the F01 output ([F01:145]); the page uses F01's;
  the P0 list is the coordinator's (s8 C4).
- **One identifier, two items:** E-1 in D-14's row and data (record l9stk's junction limit, kept as s8 keeps D-14) against l4e7's E-1
  (D-10); D-06 the decision against D-06 the defect (s8 C8, C9); PC-12 applied only where it names its places.
- **"Completed independently"** ([P11:89]) against the crediting rule of the common brief; read as ADDRESSED IN DRAFTS, PROVISIONAL (PC C-4).

## D. Left out, and why

- **LH-12** (PC-08): `LAYER5-HANDOVER.md` is not this author's file; PC says its owner record restates it.
- **The re-pins:** records l4e10 and l4e11 pin this page's sha256 and l6r2 the register (the coordinator's at the freeze); L4-E9's
  pins of the three l8p copies at 515f6cf2 (PC-04 assigns their re-take to the coordinator; R-206's From now calls them superseded).
- **45.88 K/W outside PC-05's stated places:** 8a's D-14 row and data, the exit table's D-14 row, U-04's choice row, UDC-1's
  comparison and the 8a history paragraph still state set 29's per-FET bar; s8 keeps D-14 and U-04 unchanged and PC-05 names four
  places; the next set restates them from E11-29's row (40.78 K/W without m).
- **R-176 row 3:** L4E7-P0SOL.md section 5 replaces U5's +-0.240 V line by U5 under 10 mV; neither draft carries it (a finding for the next set).
- **The output's alias citations:** section 8's texts keep s8's `[ALIAS:N]` citations (lines at 7070f106, the alias table at the head of
  section 8); the output prints the same texts without the table.

## E. SESSION decisions (under the owner's standing rule of 26 September 2026)

- **E1. The four cascade outputs placed for the regeneration and tests only.** Reason: 2a's generator refuses this branch's committed
  outputs; the brief says the work does not depend on 2b. Reverse: regenerate after 2b lands; the output then reproduces byte for byte.
- **E2. s8's citations kept**, with an alias table bound to 7070f106, rather than converted to section references (s8's fold-in note
  allows either). Reverse: convert at the next set.
- **E3. s8's proposed 8e heading taken** (s8 A3's reversal). Reverse: restore the old heading.
- **E4. R-48 and R-190 under FIX** (CHECK and APPLY the desk drafts), the class's verb, rather than PC-16's bare "CHECK and APPLY".
- **E5. Set 29's options and names kept as labelled history** in D-10 and D-16 rather than deleted (B9, B11). Reverse: delete them
  with the tests that hold them.
