# AI check (not a qualified engineering review)

## Narrow verification of the targeted fix of layers 1 and 3, 27 September 2026

MESHSAT-1357. **Commit checked: `3e4799ebe0376addb80209b191ca4dbbcd1ce588`**, branch `fnd/h2` (two commits on main
`62f26a44`: `cecfd0f1` the targeted fix, `3e4799eb` the baseline; not pushed), read in its worktree at 16:10 to 16:55
CEST. `git status` was clean before and after every check; nothing in the tree was edited except this record.

Checker: one AI session that wrote none of the lines checked, took no part in the fix, and did not hold either release
check. This is an **AI check of named items only**. It is not a full layer review, not a qualified engineering review,
and stands in for no qualified review the records require (D-09, `v2/docs/reviews/REVIEW-ROUTES.md`). Prototype design:
nothing in this kit has been built, ordered, powered or measured.

**Scope (the owner's execution prompt, section 2 and section 4's targeted fix and narrow verification).** Only these
items:
- Layer 1, `REVIEW-LAYER-1-RELEASE-2-2026-09-27.md`: R2-B1 and R2-m1, and no new contradiction in the lines touched.
- Layer 3, `REVIEW-LAYER-3-RELEASE-2-2026-09-27.md`: B-1, with these conditions:
  - `baseline_state` names this branch's commit and the review records;
  - S-51 is closed by commit, with evidence;
  - the registry at the head equals the one the reviewer judged at `eb9f9030`, except for (a) the renumbering (SC-51 to
    SC-56 as SC-58 to SC-63, EQ-25 as EQ-26), which must be mechanical and complete, and (b) the changes of set 5, the
    consolidated re-take and this fix, each typed correctly and contradicting nothing the reviewer relied on.

## 1. What was read

| File at `3e4799eb` | sha256/16 |
|---|---|
| `v2/docs/PRODUCT-BRIEF.md` | `c1bb3fe5e082b57e` |
| `v2/BUILD.md` | `c92843ea1bf351b2` |
| `v2/ecad/tools/pcb_requirements.yaml` (and the same file at `953f5658`, `eb9f9030`, `a7b5872e`, `8ea7867e`, `5ca81eea`, `91894cd7`, `7dfbfb16`, `79963b3b`, `62f26a44`, `cecfd0f1`) | `58b77b5d15b2fc7d` |
| `v2/docs/REQUIREMENTS-TRACE.md` | `7d2d682cae5297bc` |
| `v2/docs/CURRENT-EVIDENCE.md` | `7a834fe55aea6ccd` |
| `v2/docs/CASE-FIT-UNCERTAINTIES.md` (sections 2, 6, 7) | `efc66afe9140e022` |
| `v2/docs/CASE-MARGINS.md` (rows M17g, M17x) | `0fc449b72532ba7c` |
| `v2/docs/PANEL.md` (section 9, line 195) | `7bb905740ddaebb9` |
| `v2/docs/ASSEMBLY.md` (step 7, line 208) | `b49f853f450d49ee` |
| `v2/docs/HW-FW-CONTRACT.md` (sections 6.5 and 8, line 413) | `a20eea9fe2234f86` |
| `v2/docs/handover/LAYER-STATUS.md` | `1805e7c87278263e` |
| `v2/docs/handover/ENGINEERING-QUESTIONS.md` | `0b6bf5fe88386792` |
| `v2/docs/handover/GLOSSARY.md` | `4823b467207fb759` |
| `v2/docs/feasibility/EMCON.md` (section 0a counts, section 4b) | `1d4a491d9718e6d3` |
| `v2/docs/CONOPS.md` | `4483209659dc391c` |
| `v2/docs/records/h2/registry_difference.py`, `.out` | `42568994b6ecf2bc`, `a7424cf46db5e00e` |
| `v2/docs/records/README.md` | `bfd2b77bcde84848` |

**Checks run** (read-only; scripts and outputs in the session scratch `rv-h2/`, not filed):

1. An independent comparison of the registry along the chain from base `953f5658`, through the reviewed `eb9f9030`, to
   the head. It covers every section: needs, owner rulings, session choices, open items, closed items, records and the
   top-level keys. Each difference from the reviewed file (with the reviewed file renumbered) is attributed to the commit
   that made it.
2. A merge check of every record that both the reviewed attempt and main changed.
3. A diff of the YAML comment lines, which a YAML parse does not see.
4. A scan of every tracked file outside `release/handover`, `reviews/` and `records/` for SC-51 to SC-63 and EQ-25/26,
   at `eb9f9030` and at the head, with each citation read in its context.
5. In a `git archive` export of the head: `rules_lib.py requirements` gave 144 records and 0 errors. Its 19 warnings are
   all "git cannot say here" warnings, which come from the export. `rules_render.py --requirements --check` reports the
   trace page current.
6. The fixer's `registry_difference.py` re-run at the head. It adds to its committed output (taken at `cecfd0f1`) only
   the baseline commit's own changes.
7. The sha256/16 of the three review records and of the brief.
8. `gen_sch_b.py` at `e3aedb25`: lines 257, 764 to 766 and 822.

## 2. Layer 1

### R2-B1: CLOSED

- **The count and list.** Brief line 256 reads "Seven feasibility blockers on the core are not closed (FEA-001 ...
  FEA-007 the kit's fit in the Peli 1450 on the case choices C1 to C6, core as a condition of every core function under
  the session's SC-04; ...)", in the reviewer's words.
  - The registry holds exactly seven `kind: feasibility` records, FEA-001 to FEA-007, each `prototype_1: core` and
    `release_effect: BLOCKER`.
  - FEA-007 has `prototype_1_basis: SESSION` and `prototype_1_choice: SC-04`.
  - `CURRENT-EVIDENCE.md`'s feasibility-blocker table lists the same seven.
- **FEA-007's open-items row.** It is present above the D-07 row, and every figure agrees with its source:
  - 35 of 70 margins OPEN (CASE-FIT-UNCERTAINTIES section 7, from CASE-MARGINS 3.2);
  - M17g and M17x "FAILS AS ASSUMED" until the plug is picked (section 2 rows, CASE-MARGINS rows 498 and 499);
  - M4a and M5 OPEN on the hold-down S-27 (section 2; S-27 open);
  - layout entry held for A, B, D, E, E5 and P (FEA-007 `holds_layout_entry`);
  - the mock-up BLOCKED on L-07 or the owner's acceptance of the residual (section 6's reversal (2), section 7's
    options);
  - the reason layer 1 can close (32.62, every failing branch moves a board) and the reissue rule through D-06.

  FEA-007's state (`FEASIBILITY_OPEN`, INCONCLUSIVE, BLOCKER, waiting on S-27 and L-07) is stated as the registry holds
  it. The cited anchors in "What the V2 kit is" exist: the pack in the east pocket (lines 76 to 80) and D-07's jack count
  (lines 90 to 92).
- **The D-07 row** names the east plug layout (M17g, FEA-007) beside the board E clamp fit. Its description of M17g (the
  layering under 5G MAIN that IRIDIUM, ANT3 and DIV pass) matches CASE-MARGINS row M17g. It agrees with
  CASE-FIT-UNCERTAINTIES section 7 ("D-07's third 5G jack through the east plug layout").
- **Lines touched, no new contradiction.** The open-items paragraph now says four items could change a stated line
  (REQ-072 and FEA-007 on the pack line). This agrees with the rows, which each say how that is handled. The status
  paragraph keeps the brief a CANDIDATE until this re-check, and says so correctly.

### R2-m1: CLOSED

`v2/BUILD.md` line 113 now reads "the lamp test lights all seventeen controller-lit indicators (corrected 27 September
2026: not `D22` ...; `docs/PANEL.md` section 9)". This agrees with PANEL.md line 195, which says `D22` "is not among these
seventeen ... setting EMCON is its test", and with ASSEMBLY.md line 208. Line 49 of the same page, "a seventeenth" light
guide for `D22`, counts light guides, not lamp-test indicators, so the two lines do not conflict.

## 3. Layer 3

### B-1: NOT_CLOSED

Five of the six conditions pass:

| Condition | Result |
|---|---|
| `baseline_state` names this branch's commit | "BASELINED at cecfd0f1". `cecfd0f1` is on `fnd/h2`, and the registry there is sha256/16 `f25e17d7d698ecf8`. Naming the content commit from the commit after it is the form B-1 allows ("identify it by content if the branch is rebased"). PASS |
| ... and the review records | `baseline_reviews` names `REVIEW-B-LAYER-3-2026-09-27.md@7a6c679f446b1baa`, `REVIEW-LAYER-3-RELEASE-2026-09-27.md@1c3bc2d99f9efb51` and `REVIEW-LAYER-3-RELEASE-2-2026-09-27.md@cf8c73fb288be2fb`. All three hashes match the files at the head and at `cecfd0f1`. PASS |
| S-51 closed by commit, with evidence | In `closed_items`, `closed_by: commit cecfd0f1`, with closing evidence naming the three records and their hashes. PASS |
| (a) the renumbering is mechanical | Under the map SC-51..56 to SC-58..63 and EQ-25 to EQ-26, every entry the reviewed attempt changed landed identical to the reviewed text. The exceptions are the readings of the seven records main also changed (below), plus n1's " as read at e3aedb25" on SC-58 and SC-63, which holds at `e3aedb25`: line 257 is `CM5_PINS` with pin 29 GPIO16, line 822 is the level stage, and lines 764 to 766 are `PORTS`. SC-58 to SC-63 carry `drafted_as` SC-HF-01 to 06. No entry changed at landing that the reviewed attempt had not changed. PASS |
| (a) the renumbering is complete | Every citation on a live page of the reviewed SC-51..56 or EQ-25 at `eb9f9030` reads SC-58..63 or EQ-26 at the head: HW-FW-CONTRACT lines 299, 377, 381 to 386 and 413; ENGINEERING-QUESTIONS line 8, the index and the heading (now line 448); GLOSSARY line 38; LAYER-STATUS lines 49, 101, 359, 513 and 834; registry S-59, S-61 and CFL-017. Set 5's own citations keep their meaning: SC-55 (the dock crossing), SC-56 (the tracker), SC-57 (PWR-001 on D and E) and EQ-25 (TX_INHIBIT_n). PASS |
| (b) every other difference typed correctly and contradicting nothing | **FAIL on one record** (below). The rest pass: <br>- Set 5 adds SC-51 to SC-57: `authority: SESSION`, `under: standing-rule`, dated, sourced, each `why` giving its reversal. <br>- Set 5 adds S-64 to S-76 (SESSION, OPEN) and extends S-47's title with progress, leaving it open. <br>- Set 5 rebinds readings (`evidence` and `evidence_bound_to` only) on 27 records. <br>- The re-take moves CON-010 to FAIL, labelled the session's, with its reversal, and adds REQ-044's note. <br>- The finalizer (`62f26a44`) adds S-77 to S-79. Its needs pin equals CONOPS at the head (`4483209659dc391c`). Its three CONOPS rebinds are header-only; CONOPS differs from `eb9f9030` only at lines 3 and 48 to 49. <br>- The baseline commit changes only `baseline_state`, `baseline_reviews`, the header paragraph, S-51, S-77 and S-78 closed, and S-79's title. <br>No record's `kind`, statement, acceptance, `prototype_1`, allocation, verification method or phase, or `release_effect` differs from the reviewed file. The seven records both sides changed (CFL-014, CFL-016, CON-018, REQ-072 and REQ-077 are exact unions of the two sides' readings) keep their reviewed fields. |

**The finding (B-1 remains).** A difference that the header does not state, and that contradicts the record it sits in:
- **What changed.** When the reviewed attempt landed on main (`79963b3b`, the rebased `eb9f9030`), its own
  CURRENT-EVIDENCE re-read on **CON-010** and **REQ-044** was replaced:
  - removed: the reviewed note "re-read at the second release attempt ... (fnd/rel2, d535c17e)", bound to
    `CURRENT-EVIDENCE.md@6351a72c7966c4b9`;
  - added: a new note "re-read at the rebase of the second release attempt ... onto main 91894cd7", bound to
    `@7a834fe55aea6ccd`.
- **Why it is unstated.** The header attributes the rest of the difference to set 5, the re-take (`8ea7867e` to
  `91894cd7`), the finalizer (`62f26a44`) and this fix. `79963b3b` is none of them. The `.out` lists both records as
  changed in `evidence` but gives no cause.
- **Why it matters.** On REQ-044 the new note is consistent: it stays INCONCLUSIVE. On CON-010 it is not:
  - CON-010's evidence entry 26 (the re-take) moved the reading "from INCONCLUSIVE to FAIL" on W3T-F1;
  - `evidence_result` is FAIL, and `history` ends "so it reads FAIL";
  - the landed entry 28, the record's newest, ends "board D's RF-002 and SCH-004 rows keep the class and cause read
    above, so this constraint's own reasons are unchanged and **it stays INCONCLUSIVE**, on the file at
    7a834fe55aea6ccd".

  The generated trace page shows the contradiction at line 1976: "*Evidence (FAIL, DESK_REVIEW):* ... it stays
  INCONCLUSIVE". S-78's closing evidence ("differs from the one that record read only as its header states") is
  therefore not accurate.
- **Consequence under the registry's own rule.** The header paragraph on the baseline says that if the narrow
  verification "finds a registry difference the paragraph above does not state, baseline_state returns to
  READY_FOR_REVIEW_B and S-51 and S-78 reopen". This record finds one.
- **What closes it (wording only; no statement, acceptance or verification changes):**
  1. CON-010's entry 28 ends with the record's actual state: its reasons unchanged, it stays FAIL on W3T-F1, on the
     file at `7a834fe55aea6ccd`.
  2. The header's difference paragraph names `79963b3b`'s re-take of the reviewed attempt's own CURRENT-EVIDENCE re-read
     on CON-010 and REQ-044.
  3. The trace page is re-rendered.
  4. `baseline_state` and S-51/S-78 are handled as the reversal says, then re-baselined in the commit that files a
     re-check of those two edits.

  Everything else B-1 asks for is in place, so a re-check can be limited to those edits.

B-2 (the package) is outside this check. S-79 correctly stays open.

## 4. Observations (not findings; for the integrator)

- **S-77's early closure.** S-77 was closed on the fix alone, before its own stated conditions: this re-check and the
  brief set to BASELINED. The closure says so, keeps its reopen rule, and carries the remaining steps in LAYER-STATUS
  layer 1 item (1) and EQ-27. With R2-B1 CLOSED here, what remains for layer 1 is the brief's BASELINED state. The
  release-2 reviewer also asked for one of the method remedies before that, and LAYER-STATUS item (3) carries it.
- **The fixer's comparison has gaps.** `registry_difference.out` is taken at `cecfd0f1`, not the head. The script does
  not see YAML comments, asserts nothing on open items or session choices, and does not attribute causes. That is how
  the finding above passed its check.
- **Set 5 postdates the layer 1 check.** It reached main after the layer 1 check read `eb9f9030`. The brief's FEA-002
  row agrees with EMCON.md's counts at the head (local 15 of 17, end to end 0 of 17), but it does not name W3T-F1 (S-64,
  EQ-25), under which RF-002 reads FAIL on boards A and D and CON-010 reads FAIL. This is for the layer 1 writer before
  the brief is BASELINED.
- **Brief lines that name only the clamp fit.** Lines 90 to 92 ("the case half of the condition is laid out") and line
  254 name only the board E clamp fit for D-07. The rows now add the east plug layout. "Laid out" is not "met", so this
  is not a contradiction; it is wording for a later revision.
- **Other layers' pages.** LAYER-STATUS line 70 (layer 4's row) and REGENERATE.md line 430 still say "FEA-001 to
  FEA-006".
- **Items not in any `waits_on`.** None of S-64 to S-79 is in any record's `waits_on`. S-64 decides CON-010's verdict and
  is carried only in its evidence text: the letter of 3.15, as in the release-2 reviewer's n7.

## 5. Result

| Item | Result |
|---|---|
| Layer 1 R2-B1 | **CLOSED** |
| Layer 1 R2-m1 | **CLOSED** |
| Layer 3 B-1 | **NOT_CLOSED**: one unstated registry difference, CON-010's landed reading, contradicts its `evidence_result` FAIL; under the registry's reversal rule, `baseline_state` returns to READY_FOR_REVIEW_B and S-51 and S-78 reopen until the wording fix in section 3 and a re-check of it |
