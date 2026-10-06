# Layer 4's DESK gate (the owner's part 19): the assessment text, DRAFTED for the coordinator (MESHSAT-1357, 6 October 2026)

**Status: DRAFT. This file is not the assessment.** It drafts the text and the evidence of Layer 4's DESK-gate assessment so that the
coordinator adopts, edits or rejects it at promotion, with the final integrated sha bound where it reads `<INTEGRATED-SHA>`. The
verdict word is the coordinator's and stands below as the literal placeholder `[COORDINATOR: DESK-gate verdict]`. Nothing here accepts,
closes, verifies or promotes anything; it designs nothing, runs no generator or suite and consumes no review. Written by the DESK-gate
draft worker on branch `fnd/dgate` from set 30's integration commit 2a, `bbba3e53e396d3fe0f8ddd2f38d0c169bcc99c45` (the base), read from
01:54 CEST on 6 October 2026. Prototype framing: nothing in the kit has been built, bought, powered or measured; a MODEL figure is desk
arithmetic, never a measurement.

**Two gates, never one.** The DESK gate is the owner's part 19: each layer's handover "must contain coherent editable sources,
calculations/simulations, review evidence and clearly scoped outstanding supplier work" [OWN:476], with "Do not claim unconditional
completion of a design that still depends on an unknown." and "Do not park a solvable circuit defect in the supplier list to make a desk
gate pass." [OWN:478]. The DESIGN gate is L4-E9's criteria 1 to 5 in its section 8, a different gate: "The DESIGN gate (criteria 1 to 5
below) is not the DESK handover gate of the owner's part 19" [PAGE31:965]. The coordinator's words for the DESIGN gate are written in
section 7 only, labelled as the design gate's, and are not this gate's. Physical qualification and fabrication release are separate
gates again: "Keep physical qualification and fabrication-release gates separate and honest; do not relabel them as passed." [OWN:476].

**Citation form.** `[ALIAS:N]` is line N, `[ALIAS:N-M]` lines N to M, `[ALIAS]` the whole file, of the file the alias names at the
revision the alias table gives. Revision `base` is `bbba3e53` (this branch changes no existing file, so the working tree reads the same).
A row with another commit is a file on another branch, cited as text only (the worker rule that a record reads its inputs from its own
tree): those lines were read with `git show <commit>:<path>` in this session. A path in backticks with no line is a repository path;
`<worktrees>/...` is the coordinator's run folder outside the repository, named and never read as evidence. The module
`v2/ecad/tools/tests/test_dgate.py` holds every base citation against the base commit, every quotation against the file its citation
names, every count this file states, and each other-branch citation where that commit is in the object store.

| Alias | Revision | File |
|---|---|---|
| OWN | base | `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md` |
| CONST | base | `v2/docs/EXECUTION-CONSTITUTION.md` |
| PAGE | base | `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md` |
| REG | base | `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md` |
| L4O | base | `v2/docs/records/l4e9/l4e9_power_path.out` |
| L4PY | base | `v2/docs/records/l4e9/l4e9_power_path.py` |
| LH | base | `v2/docs/records/l4e9/LAYER5-HANDOVER.md` |
| CLP | base | `v2/docs/records/l9t5/apply_l4e9_changelist_p0.py` |
| REM | base | `v2/docs/records/l4close/REMAINING-ENGINEERING.md` |
| ANX | base | `v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md` |
| P0L | base | `v2/docs/records/l4close/P0-POWER-LIST.md` |
| V6 | base | `v2/docs/records/l4close/CHECK-V6-POWER-DRAFTS-7a82e82a-AS-RECEIVED.md` |
| CX44 | base | `v2/docs/records/l4close/CHECK-CX44-F01-SELECTION-8c7c335f-AS-RECEIVED.md` |
| CX45 | base | `v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md` |
| CX46 | base | `v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md` |
| T5R | base | `v2/docs/records/l9t5/README.md` |
| CON | base | `v2/docs/records/l9t5/l9t5_connected.out` |
| F01 | base | `v2/docs/records/l9t5/l9t5_f01.out` |
| T10 | base | `v2/docs/records/l9t5/l9t5_t10.out` |
| T10R | base | `v2/docs/records/l9t5/T10-ROUND5.md` |
| HWFW | base | `v2/docs/records/l9t5/apply_hw_fw_contract_t10.py` |
| FHB | base | `v2/docs/records/l9t5/fetch_held_back.py` |
| CASC | base | `v2/docs/records/l9t5/stability/regen_cascade.sh` |
| STAB | base | `v2/docs/records/l9t5/stability/DIGESTS-cr3.txt` |
| RUN2 | base | `v2/docs/records/l9t5/stability/RUN-cr3-pass2.log` |
| RUN4 | base | `v2/docs/records/l9t5/stability/RUN-4d0ff8a2-pass2.log` |
| SOLO | base | `v2/docs/records/l4e7/l4e7_p0sol.out` |
| P0SOL | base | `v2/docs/records/l4e7/L4E7-P0SOL.md` |
| P11 | base | `v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md` |
| B2 | base | `v2/docs/records/l4e7/B2-PRESENCE.md` |
| E11 | base | `v2/docs/records/l4e11/l4e11_power.out` |
| E11R | base | `v2/docs/records/l4e11/README.md` |
| BRK | base | `v2/docs/records/l8p/L8P-BREAKER.md` |
| BRKP | base | `v2/docs/records/l8p/apply_gen_sch_p_breaker.py` |
| GNL | base | `v2/docs/records/l8p/gen_netlist.py` |
| L8R2 | base | `v2/docs/records/l8r2/L8R2-KNOWN-DEFECTS.md` |
| DIST | base | `v2/docs/records/l8r2/l8r2_dist.out` |
| P0R | base | `v2/docs/records/l8r2/l8r2_p0.out` |
| EFS | base | `v2/docs/records/efuse/EFUSE-SETTINGS.md` |
| TP29 | base | `v2/docs/test-procedures/TP-E11-29.md` |
| HAR | base | `v2/ecad/tools/tests/harness.py` |
| EVD | 7930ae68 | `v2/docs/records/l4close/L4-DESK-GATE-EVIDENCE.draft.md` (Slot D, `fnd/int30rec`) |
| P0L3 | 7930ae68 | `v2/docs/records/l4close/P0-POWER-LIST.rev3.draft.md` (Slot D) |
| I30 | 7930ae68 | `v2/docs/records/int30/RESULT.draft.md` (Slot D) |
| H31 | 17ce29d5 | `v2/docs/records/l4e9/SET31-CHANGES.md` (Slot H, `fnd/l4e9s31`) |
| PAGE31 | 17ce29d5 | `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md` (Slot H: section 8 as it will read) |
| LS31 | 87c5fb08 | `v2/docs/handover/LAYER-STATUS.md` (Slot I, `fnd/lstat31`) |
| LS30 | 4d84794a | `v2/docs/handover/LAYER-STATUS.set30.draft.md` (the draft Slot I folded, `fnd/lstat30`) |
| S8 | f47d1fc4 | `v2/docs/records/l4e9/L4E9-SECTION8-SET30.draft.md` (Slot F, `fnd/l4e9s8`) |
| PC | 8282895e | `v2/docs/records/l4e9/L4E9-PAGE-CONSISTENCY-SET30.draft.md` (Slot G, `fnd/l4e9pc`) |

## 0. The candidate this draft reads, and what moved after it

- The base `bbba3e53` is the P0 candidate after cx46 ("CANDIDATE READY 3: ac8efbca (the claim-and-handover disposition after cx46"
  [T5R:1]) with the remaining-engineering ledger merged and L4-E9's change-list rows R-220 to R-245 applied to the change list
  ("the drafted change list carries rows R-220 to R-245 (no R-241: route B2 out)" [CON:365]).
- After the base, on `fnd/p0pwr`: the merge `6fe398e9` of Slot H's set 31 (`fnd/l4e9s31`: `bca7b0dc`, `14082416`, `17ce29d5`; read
  with `git log`). The coordinator's note of 01:56 CEST (`<worktrees>/_runs/claude/dgate/INBOX.md`, outside the repository) says the
  candidate merged it because the release suite on the applied change list needs its page, generator data and `test_l4e9`
  expectations, so set 31 is part of THIS candidate and its commits are intervening commits to classify (class (b), claim-narrowing
  record text). The coordinator's commit 2b (the regenerated cascade outputs) is not committed at the base (Slot H: "commit 2b (the
  cascade outputs this branch's output pins)" [H31:1]); the final integrated sha is not known when this is written (the cascade
  regenerates again and a re-key follows, the same note). Citations stay at the base; where the merge `6fe398e9` changes a statement,
  both readings are given, at the base and on the candidate.
- The reviewed revision is `4d0ff8a2` (cx46, [CX46:8]); no check has read the base or anything after `4d0ff8a2` ([P0L3:11-12]).

## 1. Part one: coherent editable sources

**For acceptance at the desk gate (6).**

- F1.1 The editable sources are the generators and the release-guarded drafts: "None is APPLIED: every apply script refuses the tree's
  own generator until its release record reads" [PAGE:401]; L4-E9's change list orders them and the P0 rows are on it [PAGE:422].
- F1.2 The drafts compose on the four boards in L4-E9's order and regenerate: "board A composes in L4-E9's change-list order with every
  draft, every one with a row, and regenerates" [CON:366], the same for boards B, D and E [CON:367-369], route B2 out of the baseline
  [CON:370], "every record check reads DRAWN on the composed candidate" [CON:373] and "every mutation fails its check" [CON:374].
- F1.3 The independent checks read the composition as passing in their stated scope: cx45, "Boards A, B, D and E composed. All 16
  connected netlist checks read DRAWN." with "This checks connectivity and intent, not routed layout or KiCad ERC." [CX45:28]; cx46,
  "Board E baseline orders agree and exclude B2." [CX46:60].
- F1.4 Set 31, merged on the candidate at `6fe398e9`, brings L4-E9's page, register and generator data to the candidate's state (27 changes, each with its source item and
  class [H31:28-58]) and takes the narrower claim where its two input drafts overlap [H31:68-98]; it states the design gate apart from
  this gate [PAGE31:965].
- F1.5 The withdrawn items are withdrawn in the records that a receiving company reads first: route B2 "is UNSELECTED and WITHDRAWN
  AS DRAFTED" [B2:4]; FAN_OK's rows R-210 to R-212 read WITHDRAWN in the register [REG:304-306].
- F1.6 One ledger gathers every handed-over item with its sources, and states that it settles no contradiction it lists: "where this
  ledger notes a gap or a contradiction between two records it settles neither" [REM:12-13].

**Against (6).**

- A1.1 No circuit change is in a generator: "no circuit change is applied (every change in section 3 is a draft, APPLIED 0), no board
  of the set has a layout" [PAGE:884]. A receiving company edits the generators plus drafts that refuse until released, not one
  composed source; this is coherent as a draft set and is not an implemented design.
- A1.2 The P0 list in the tree is "revision 2, 5 October 2026, 16:50 CEST" [P0L:1] with superseded row states [P0L:18-24], which cx46
  named ("lines 18 to 24 do not reflect the corrected candidate" [CX46:81]); revision 3 is a draft on another branch [P0L3:1-12].
- A1.3 At the base, L4-E9's section 8 is set 29's text and contradicts itself on criterion 2 ("three material defects are open"
  [PAGE:967] against "criterion 2 has no open defect" [PAGE:979]); set 31 corrects it [PAGE31:1007], merged on the candidate at
  `6fe398e9`.
- A1.4 Seventeen of the twenty-eight contradictions of section 5 would still stop a receiving company in the candidate as the merge
  `6fe398e9` leaves it (the column Stumble of section 5).
- A1.5 Two drafts carry text the records withdrew: route B2 called "an unapproved PARTIAL interface proposal" and "an owner item"
  [L4PY:4293-4294] against "no owner action rests on B2" [B2:27]; Layer 5's handover row LH-12 still puts "the fans' supplies through
  FAN_OK, R-210 to R-212" [LH:28], left by set 31 ("LAYER5-HANDOVER.md is not this author's file" [H31:117]).
- A1.6 Record pins of L4-E9's page and register are owed at the freeze ("records l4e10 and l4e11 pin this page's sha256 and l6r2 the
  register (the coordinator's at the freeze)" [H31:118]).

## 2. Part two: calculations and simulations

**For acceptance at the desk gate (6).**

- F2.1 Each record's script and output is in the tree, and the P0 cascade of eighteen outputs [CASC:9-11] ran twice for CANDIDATE
  READY 3, each pass exiting 0 [STAB:1-2], the record noting that the "second pass changed no byte" [STAB:3]; the second pass printed "already identical"
  for every output and "exit 0" [RUN2:1-20]. Every one of the eighteen digests equals its file at the base (read by this draft's test).
- F2.2 The same stability was recorded at the reviewed revision `4d0ff8a2` [RUN4:1-19], and cx46 reads it "CLOSED AS CONDITIONAL"
  with the condition "retain or reproduce successful byte-identical repeated output runs on these inputs" [CX46:181-183].
- F2.3 The netlists need no KiCad: `gen_netlist.py` runs a generator's part table into a KiCad-form netlist "on a host without KiCad"
  [GNL:1-2].
- F2.4 Every figure carries its label (PRINTED, TYPICAL, MODEL, ASSUMPTION, INFERRED, DECLARED, DERIVED, MISSING, PROVISIONAL)
  [REM:15-17], and the connected output states that "every figure below is a MODEL reading on the composed candidate" [CON:6].
- F2.5 Each remaining-engineering item names its reproduction command (the column Reproduce [REM:587-617]), and the order of the
  cascade is the script's [REM:645-646].
- F2.6 Record l4e7's cached results apply to the base although its key does not hold: the figures it reads are "EQUAL in both, so the
  cached results are this base's results" [SOLO:35], and "render(cache) against the committed l4e7_stage_settings.out:
  BYTE-IDENTICAL" [SOLO:38].

**Against (7).**

- A2.1 The repository alone does not reproduce the calculations: the makers' sheets are held back and fetched by sha256 by each
  record's `fetch_held_back.py` [REM:646-647] (seventeen such scripts in the tree); for example "l9t5_a1.py reads the printed rows
  from them and refuses without them" [FHB:9], and F01's INA250 sheet "is held back, fetched and checked by record l4e7's
  fetch_held_back.py, never committed" [F01:5].
- A2.2 Record l4e7's results cache KEY does not hold on the tree [SOLO:31]; its recompute is "30 to 50 core-minutes" on a rented box
  [SOLO:36]. The re-key is a box job in the coordinator's runbook (`<worktrees>/_runs/int30/PLAN.md` section 0) and is not
  committed at the base: the results file's last commit is `69921ce8`, set 29's freeze, and the rendered output's `914a2f5a`,
  earlier the same day (read with `git log`).
- A2.3 L4-E9's own output does not reproduce from the base: it pins four cascade outputs at digests that are not the base's files
  [L4O:55], [L4O:64], [L4O:67], [L4O:106] (the coordinator's 2b bytes; Slot H: "The generator on this branch alone refuses at its
  pins of four cascade outputs" [H31:20]), while the connected output still reads "L4-E9's own output refuses on this tree at its
  L4-E11 pin" [CON:362].
- A2.4 KiCad is needed for the reading of record and for everything after the schematic: "the KiCad export on the box (kicad-cli sch
  export netlist) is the reading of record" [GNL:14-15]; no ERC is run by the netlist tool [GNL:13]; no board has a layout
  [PAGE:884]; tests that need pcbnew or kicad-cli skip on a host without them [HAR:7].
- A2.5 Several calculations are withdrawn as bounds and owed as engineering: "the universal sustained bound and its positive margin
  are WITHDRAWN" [T10:620]; the connected verdict is "REMAINING ENGINEERING. No row of sections 5 to 10 is a positive electrical
  acceptance" [CON:336].
- A2.6 The stability record predates the integration: the cr3 runs are of 22:26 to 22:45 on 5 October [STAB:1]; integration 2a, 2b
  and set 31 change outputs after them, and stability on the integrated revision is an empty gate line in Slot D's draft [I30:116].
- A2.7 Two pins outside P0's cascade are stale in the tree, in paused Layers 7 and 8 (`l7pwr_fans_th1.out` and `l8gnd_drafts.out`,
  as Slot D read them at `1c6d56f5` [I30:80-82]); this draft did not re-read them at the base.

## 3. Part three: review evidence

**For acceptance at the desk gate (6).**

- F3.1 The four checks of the P0 round are filed as received under `v2/docs/records/l4close/`, each labelled an AI review: V6
  [V6:3], cx44 [CX44:3], cx45 [CX45:3], cx46 [CX46:3].
- F3.2 Their verdicts stand as given, the negative ones preserved: V6, items A to F each "CONFIRMED AS CONDITIONAL" with "The affected
  supply path is not complete" [V6:18-28]; cx44, "F01 SELECTION: NOT SUPPORTED" [CX44:10]; cx45, "P0 CANDIDATE: NOT CONFIRMED."
  [CX45:10]; cx46, "P0 RECHECK: CORRECTIONS NOT CLOSED." [CX46:10].
- F3.3 The method ended on the second negative, as the constitution requires ("After two negative checks of the same proposed
  solution, end that correction loop." [CONST:49]): cx46 is "the second negative on the method, which ends it" [CX46:3] and asks "Do
  not repeat this review method or relabel these tasks as qualification only." [CX46:206].
- F3.4 No self-signing: the records carry the twelve findings NOT CLOSED as remaining engineering and the four closed and two
  conditional findings in their stated scope only [REM:555-564]; the constitution's rule stands ("cannot turn a material unresolved
  rejection into an independently accepted design by self-signing" [CONST:56]).
- F3.5 Every commit between the reviewed revision and Slot D's base is classified from its diff, five bindings or presentation and
  six substantive, every substantive one narrowing a claim [I30:36-56], as part 25 asks [OWN:844].
- F3.6 The supplier annex's revised scope was accepted by the owner's reviewer, "not independent approval of the circuitry" [OWN:502].

**Against (5).**

- A3.1 No independent check accepts any P0 correction; the last verdict is negative and no further check of this method may run
  ("End this correction loop" [CX46:113]).
- A3.2 The disposition after cx46 was read by no check ("no disposition below has been read by an independent check" [P0L3:12]), and
  the substantive changes after `4d0ff8a2` owe a targeted verification before any credit [I30:124], as part 25 says: "the affected
  result needs targeted verification before being credited" [OWN:844].
- A3.3 Integration 1 and 2a (`7070f106`, `bbba3e53`) and set 31's claim changes [H31:32-55], merged at `6fe398e9`, come after Slot
  D's classification, which binds `1c6d56f5` only [I30:25]; the coordinator's note classes set 31's commits (b), claim-narrowing record
  text (`<worktrees>/_runs/claude/dgate/INBOX.md`), and part 25 owes each substantive change its targeted verification before credit.
- A3.4 Five checks the records cite are not filed in the tree: V2RG, V2RF and V2R are "the integrator's" to file [E11R:7], [E11R:23],
  [E11R:38]; record l8p's V1 and V2 are read only through its own text [BRK:778-779].
- A3.5 The eFuse record's round 2 says it has no independent check ("round 2 has none" [EFS:213]) while the P0 row that carries round 2
  reads "CONFIRMED AS CONDITIONAL" in cx45 [CX45:10] and cx46 [CX46:191]; a reader cannot tell from the tree which drafts the two
  checks read.

## 4. Part four: outstanding supplier work clearly scoped

**For acceptance at the desk gate (7).**

- F4.1 The annex hands U-01, U-02, U-04 and E11-29 to the receiving company with specimen, measured quantity, pass limit, capability
  and the outputs kept PROVISIONAL [ANX:3-10], and asks the owner for nothing ("Asked of the owner: nothing." [ANX:113]).
- F4.2 Each annex item carries its limits: U-02's per-mode lines and what each reading decides [ANX:28-37]; U-04's routes (R1) and (R2)
  with what transfers and what stays open [ANX:71-74], and R-161's pass limits [ANX:77-79]; U-01's routes (a) to (d) [ANX:89-94]
  with request, experiment and adoption kept apart [ANX:96]; E11-29's targets and its two preconditions [ANX:103-105].
- F4.3 The ledger scopes every remaining-engineering item with the fields part 24 names (failed cases, attempted correction,
  unresolved fact or decision, affected outputs, task, reproduction) [REM:85-519]: "Counts: remaining engineering 19; qualification
  1; external architecture fact 3; closed 4; conditional 2." [REM:585]. The 19 are twelve cx46 findings (RE-1, RE-2, RE-4 to RE-10,
  RE-13, RE-17, RE-18) and seven handed-over cases (HO-A to HO-G) [REM:589-607].
- F4.4 The records' own supplier tasks carry specimen, quantity and limit: B-PA1, B-PA2 and V-PA-REF under "THE SUPPLIER'S
  VALIDATION TASKS" [F01:221-239]; P1-1 for E-1 with S1 to S3, a draft, UNSENT [P11:1].
- F4.5 Desk-solvable defects are kept out of the supplier annex: "A desk-fixable defect is never parked here." [ANX:16] and "a
  desk-solvable defect is never moved into this annex" [ANX:121]; the remaining engineering is a separate ledger [REM:3-10].
- F4.6 A failed arrangement is written as a design failure, not a requirements conflict: "demonstrates that THAT arrangement fails
  under those conditions, nothing more" [ANX:43], as the owner corrected [OWN:483].
- F4.7 The residual owner-role wording part 20 named [OWN:523] is gone from the tree's annex: route (R1)'s bench is "the receiving
  company's or a nominated laboratory's bench (engagement unconfirmed; nobody in house)" [ANX:73] and Saft's request "is sent by
  whichever party engages Saft" [ANX:91].

**Against (6).**

- A4.1 The two owner texts meet here and this draft does not reconcile them (as Slot D did not [EVD:91-94]): part 19 forbids parking
  a solvable circuit defect in the supplier list [OWN:478]; part 24 says "A review-count limit does not establish that a defect is
  fixed, unfixable at the desk, or dependent only on physical evidence." [OWN:784] and directs that an unsupported correction is
  handed over as remaining engineering [OWN:786]. Some of the nineteen are desk work by their own text (RE-2's task begins "At the
  desk: extend the bounded analysis" [REM:145]; RE-9 is a replay of rows at a restated allowance [REM:336-338]; RE-6 asks for a
  corrected response mechanism and its network calculation [REM:252]). Whether handing them over as remaining engineering, apart from
  the supplier annex, honours part 19 is the coordinator's judgement.
- A4.2 No supplier is engaged and none has confirmed it takes engineering, not only validation: "No supplier is assumed engaged; its
  engineering and laboratory capability remain to be confirmed." [ANX:9-10]; the constitution asks suppliers to confirm their scope
  and not to assume that fabrication includes circuit design [CONST:94].
- A4.3 TP-E11-29 cannot run as written: "NOT EXECUTABLE. Two things must happen first" [TP29:19]; set 31 keeps it so until its
  re-take and a supplier's written agreement [H31:80-81].
- A4.4 P0-8, E11-37 (the charger's gate drive into three FETs), is scoped only in the P0 list and L4-E11: "E11-37 STAYS OPEN"
  [E11:1459]; its row names TI's answer Q-TI-17, UNSENT [P0L:25]; the annex names E11-37 only as left open after route (R1) [ANX:73],
  and the ledger has no item for it.
- A4.5 The lower-source back-feed is placed two ways (section 5, K-24): cx46 counts it among E-1's retained cases [CX46:95]; the
  records carry it as S1's added row (b), a validation run [P11:120-123], while part 23 asks S1 to carry D-10's engineering, not to
  present it as an unperformed test [OWN:680].
- A4.6 Three items leave a choice the package does not make: HO-E's task is "a hardware bar on VOS0 or its acceptance" [REM:478],
  the second branch a limit question; RE-5's attribution circuit is "NOT DRAFTED here" [T10:602]; HO-G applies "only if a
  presence-pair route is ever taken up again" [REM:426].

**What a receiving company could not scope from the package as it stands at the base:** E11-37's task (A4.4); whether the back-feed
is engineering or validation (A4.5); HO-E's choice between a bar and an acceptance (A4.6); the reproduction of L4-E9 and of record
l4e7's cache until 2b and the re-key land (A2.2, A2.3); the verdicts of the five unfiled checks (A3.4); and Slot I's four
disagreements, which no committed file holds (section 5, left out).

## 5. The contradictions still standing between records (K-01 to K-28)

The list has 28 entries; 17 read YES in the column Stumble (would a receiving company stumble on it in the candidate as the merge
`6fe398e9` of set 31 leaves it: an instruction, a state, a limit or an identifier that two records give differently). This draft settles none. Sources: Slot F's
C1 to C9 [S8:466-488]; Slot G's C-1 to C-5 [PC:292-296] (its PC-01 to PC-16 are in the table after this one); Slot H's
not-reconciled list, which holds five bullets [H31:105-113] (the brief counted four); Slot D's four [I30:94-109]; the draft Slot I
folded [LS30:135-169]; the ledger's section 6, A to F [REM:621-639].

| Id | Sources | The contradiction (both citations) | At the base | On the candidate (set 31 merged, `6fe398e9`) | Stumble |
|---|---|---|---|---|---|
| K-01 | S8 C1; I30 4; LS30 2 | criterion 2: "three material defects are open" [PAGE:967] against "criterion 2 has no open defect" [PAGE:979] | stands | corrected in the text [PAGE31:1007] | NO |
| K-02 | S8 C2 | the register's count: 209 items [REG:59] and 186 [PAGE:969] against its rows | stands | recounted, 235 items [H31:46] | NO |
| K-03 | S8 C3; PC-01; PC-08; LS30 1 | FAN_OK: R-210 to R-212 WITHDRAWN [REG:304-306] against R-28 with FAN_OK [REG:132], R-213 OWED [REG:307] and LH-12 [LH:28] | stands | R-28 and R-213 restated [H31:40], [H31:47]; LH-12 left [H31:117] | YES (LH-12, Layer 5's row) |
| K-04 | S8 C4; H31 C | R-227's band 6.3522 to 6.9257 A [REG:321], [P0L:18] against 6.3518 to 6.9259 A [F01:132]; the case at the cap 15.1307 V [P0L:18] against 15.1308 V [F01:145] | stands | R-227 restated [H31:56]; the P0 list left [H31:109-110] | YES (the P0 list's row) |
| K-05 | S8 C5; PC-09 | R-242, R-244, R-245 class SETTLED WORK [REG:335] against their acceptance REMAINING ENGINEERING | stands | classed KNOWN ENGINEERING DEFECT [H31:48] | NO |
| K-06 | S8 C6; PC-05; LS30 9 | R-159's 45.88 K/W per FET [REG:253] against TP-E11-29's target and NOT EXECUTABLE until R-159 is restated [ANX:103-105] | stands | R-159 restated [H31:44]; 45.88 K/W left in D-14's rows, U-04's row and UDC-1's comparison [H31:120-122] | YES (the per-FET bar) |
| K-07 | S8 C7; PC-16 | set 29's P1-2 and P1-3 corrected at the desk [L8R2:10-12] against R-48 and R-190 assigned to the supplier [REG:152], [REG:284] | stands | restated to the check of record l8r2's drafts [H31:55] | NO |
| K-08 | S8 C8; PC-12; H31 C | E-1 is record l9stk's junction limit [PAGE:1097], [REG:253] and D-10's remaining engineering [P0SOL:101-102] | stands | named where PC-12 names its places [H31:51]; not reconciled [H31:111-112] | YES (one identifier, two items) |
| K-09 | S8 C9; H31 C | D-06 the decision ("D-06's pocket" [ANX:81]) and D-06 the defect [PAGE:1003] | stands | kept, not renamed [H31:111-112] | YES (one identifier, two items) |
| K-10 | PC C-1; LS30 1 | D-16 reads OPEN [PAGE:1012] against "D-16 corrected in draft" [PAGE:488] in R-240 | stands | ADDRESSED IN DRAFTS, PROVISIONAL [H31:70-72] | NO |
| K-11 | PC C-2 | `test_l4e9.py` holds D-16 OPEN against the generator's data [PC:293] | stands | test expectations changed with their basis [H31:60-66] | NO |
| K-12 | PC C-3; H31 C | R17's design target "R17's coupling at most 0.29 K/W" [E11:500] against "R17 at most 0.294 K/W" [ANX:105] and [TP29:729] | stands | not reconciled [H31:105-106] | YES (a pass limit) |
| K-13 | PC C-4; H31 C | "Completed independently of E-1" for D-16's correction [P11:89] against the crediting rule (composition, mutation and electrical acceptance) | stands | read as ADDRESSED IN DRAFTS, PROVISIONAL; not reconciled [H31:113] | YES (the supplier-facing request) |
| K-14 | PC C-5; H31 C | record l8p's one release of "five drafts" [BRK:265] against the register's R-206 to R-208 and R-222, R-244, R-246 | stands | one release named [H31:52]; membership record l8p's [H31:107-108] | YES (a release instruction) |
| K-15 | LS30 3; REM F; RE-1 | the P0 list is revision 2 of 16:50 [P0L:1] against the records' states after cx46 [REM:98-108] | stands | unchanged (revision 3 drafted [P0L3:1-12]) | YES (until revision 3 is adopted) |
| K-16 | LS30 4 | eFuse round 2 "has none" [EFS:213] against P0-4 "CONFIRMED AS CONDITIONAL" [CX46:10] | stands | unchanged | YES (which drafts were checked) |
| K-17 | LS30 5; REM C | the ledger reads a stale stability digest [REM:626-630]; at the base every DIGESTS-cr3 digest equals its file [STAB:15] | the ledger's item C is out of date | unchanged | YES (the ledger reports a gap that is closed) |
| K-18 | LS30 6 | cx45's `base_commit` names `e132db0e` [CX45:8] against the HEAD it read, `06077cee` [CX45:20] | stands | unchanged | NO (the file states both) |
| K-19 | LS30 7; PC-04 | R-206 "U101 LM5069MM-2" [PAGE:517] against the draft's "U101 LM5069MM-1, the latch-off variant" [BRKP:11] | stands | R-206 restated [H31:43] | NO |
| K-20 | REM A | L9T5-F26 is J_PA's VH derating [T5R:194-196] and the connected verdicts' inheritance [T10R:227-229] | stands | unchanged | YES (one finding identifier, two findings) |
| K-21 | REM B | the declared upper bound of the return: 27.8159 A [DIST:86] against 27.9108 A [P0R:21], [T5R:59] | stands | unchanged | YES (a bound value) |
| K-22 | REM D | V-B23's response 0.9259 s [CX46:89] against about 0.98 s [T10:584-586]; the countermodel's peak 127.55 C [CX46:91] against 127.54 C [T10:620] | stands | unchanged | NO (no state changes: both over 125 C and over 0.2 s [REM:633-634]) |
| K-23 | REM E | the lower-source back-feed among E-1's retained cases [CX46:95] against S1's added row (b) [P11:120-123] | stands | unchanged | YES (engineering or validation) |
| K-24 | I30 1; PC-15 | route B2 "an unapproved PARTIAL interface proposal" and "an owner item" [L4PY:4293-4294], the change-list draft's text [CLP:23] and the heading "(a partial proposal)" [P0SOL:99] against "UNSELECTED and WITHDRAWN AS DRAFTED" [B2:4] | stands | the generator's data restated [H31:54]; the heading [P0SOL:99] and [CLP:23] unchanged | YES (cx46 asked "throughout" [CX46:203]) |
| K-25 | I30 2 | R-240 named D-10's item S1 against E-1 [P11:19] | resolved at the base: R-240 names E-1 and S1 as its later validation step [REG:334] | resolved | NO |
| K-26 | I30 3 | the connected output's T10 row, "rev X on V-B20" and "CORRECTED IN DRAFT, UNCHECKED" [CON:350-351], against revision X HELD with no admission route [T10:645-647] and "cx45's Q3 NOT CLOSED" [T10:662] | stands | unchanged | YES (a part admission) |
| K-27 | S8 head; PAGE31 | Slot F frames criteria 1 to 5 as "the Layer 4 DESK gate assessed in record l4e9" [S8:12-14] against "The DESIGN gate (criteria 1 to 5 below) is not the DESK handover gate" [PAGE31:965] | not in the tree | set 31's text governs | NO (S8 is not merged; the coordinator keeps the gates apart) |
| K-28 | this draft | the connected output: "L4-E9's own output refuses on this tree at its L4-E11 pin" [CON:362] against L4-E9's output regenerated at the base with four pins at bytes not in the tree [L4O:55], [L4O:64], [L4O:67], [L4O:106] | stands | unchanged until 2b | YES (a reproduction instruction) |

**Slot G's PC-01 to PC-16 as Slot H applied or left them** (set 31's table [H31:40-56], its left-out list [H31:115-125]; on the
candidate since the merge `6fe398e9`):

| Item | Applied in set 31 | Left |
|---|---|---|
| PC-01 FAN_OK withdrawn | yes [H31:40] | none |
| PC-02 D-16 ADDRESSED IN DRAFTS | yes [H31:41] | none |
| PC-03 the open defects counted | yes [H31:42] | none |
| PC-04 R-206 LM5069MM-1 | yes [H31:43] | the re-take of L4-E9's three l8p copies [H31:119] |
| PC-05 R-159 from E11-29's row | yes [H31:44] | 45.88 K/W elsewhere (K-06) [H31:120-122] |
| PC-06 R-246, board P's ideal diode | yes [H31:45] | none |
| PC-07 the counts | yes [H31:46] | none |
| PC-08 R-28 without FAN_OK | yes [H31:47] | LH-12 (K-03) [H31:117] |
| PC-09 the P0 rows' classes | yes [H31:48] | none |
| PC-10 R-236, R-237 with cx46 item 16 | yes [H31:49] | none |
| PC-11 In short quotes cx45, cx46 | yes [H31:50] | none |
| PC-12 E-1 and D-16 named apart | where it names its places [H31:51] | elsewhere (K-08) [H31:111-112] |
| PC-13 one release | yes [H31:52] | the membership (K-14) [H31:107-108] |
| PC-14 IF-01, IF-02 figures | yes, both figures printed [H31:53] | none |
| PC-15 D-10 and route B2 | yes [H31:54] | [P0SOL:99], [CLP:23] (K-24) |
| PC-16 R-48, R-190 | yes [H31:55] | none |

## 6. The proposed verdict text, for the coordinator

**Layer 4's DESK gate (the owner's part 19 [OWN:476]), assessed on `<INTEGRATED-SHA>`: [COORDINATOR: DESK-gate verdict].**

**What acceptance at the desk gate with every dependant PROVISIONAL would require to be true** (each condition with its source; the
state at the base or on the candidate in brackets):

- Y1. The editable sources compose and regenerate on the integrated revision as on the base [CON:365-374] (true at the base; owed on
  `<INTEGRATED-SHA>`).
- Y2. Each contradiction of section 5 that reads YES is either resolved or carried in the package with both citations, so that a
  receiving company meets it as a named item and not as a silent difference [CONST:21] (17 stand at YES on the candidate; none is
  carried in a page a receiving company reads first).
- Y3. The calculations reproduce from the repository plus the named fetches and the named box jobs, with every pin current: L4-E9's
  four pins [L4O:55] and record l4e7's key [SOLO:31] (both owed at the base).
- Y4. The review evidence is complete as given: the four checks filed, their negative verdicts kept [CX46:10], the method ended
  [CX46:206], every change after `4d0ff8a2` classified, and every substantive one verified or not credited [OWN:844] (Slot D's
  classification binds `1c6d56f5` only [I30:25]; integration 1 and 2a and the set 31 merge `6fe398e9` are not yet in a classification
  record).
- Y5. The outstanding work is clearly scoped: the annex's four items [ANX:111-119] and the ledger's nineteen remaining-engineering
  items, one qualification and three external architecture facts [REM:585], with E11-37 placed (A4.4) and the back-feed placed
  (A4.5) (both unplaced at the base).
- Y6. No solvable circuit defect is parked in the supplier list [OWN:478]: the coordinator judges that the ledger's handover after
  the ended method [OWN:786] is not that parking, item by item for the desk-solvable ones (A4.1).
- Y7. No unconditional completion is claimed: every dependant stays PROVISIONAL or OPEN as the records say [CON:336-340], [F01:212-214],
  and power-design closure and fabrication release are reported apart [CONST:23] (true in the records at the base).

**What would deny it** (any one is enough):

- N1. A desk-solvable circuit defect found in the supplier annex, or handed over without its failed cases, attempted correction and
  affected outputs [OWN:786].
- N2. A contradiction left on the promoted revision that changes an instruction, a state, a limit or a part (the YES rows of section
  5), with no entry that names it [CONST:21].
- N3. A result credited on `<INTEGRATED-SHA>` that a substantive change after `4d0ff8a2` altered, without its targeted verification
  [OWN:844].
- N4. A calculation of the package that a receiving company cannot reproduce from the repository, the named held documents and the
  named box jobs on the promoted revision (A2.2, A2.3).
- N5. Any wording that the power design is accepted, closed, qualified or released (the owner's part 24: the gate "must not claim
  technical closure of open defects" [OWN:788]).

**The completion claims, each reported apart** (the constitution [CONST:23]; Slot I's fold carries the same six lines [LS31:355-365]):

- documents and editable artifacts: on main as a DESK candidate (the coordinator's promotion of `<INTEGRATED-SHA>`; at the base the
  candidate is on its own branch);
- design reviewed and accepted: NO (cx45 and cx46, [CX45:10], [CX46:10]);
- implemented: NONE ([PAGE:401], [PAGE:884]);
- physical qualification: NONE ([REM:15-16]);
- fabrication release: BLOCKED ([PAGE:884], [CON:4]);
- power-design closure: BLOCKED ([PAGE:972], [CON:4]).

## 7. The DESIGN gate, the coordinator's words (not this gate's)

As the brief gives them, and as set 31's page writes them [PAGE31:1003] (on the candidate since the merge `6fe398e9`): criterion 1 CONDITIONAL, criterion 2 FAIL (open material
defects after cx46, carried as REMAINING ENGINEERING), criterion 3 PASS, criterion 4 PASS, criterion 5 CONDITIONAL. Set 31's page
says a PASS there is "the DESIGN gate's reading of that criterion on the desk package, never a closure, a qualification or a release"
[PAGE31:1003]. None of these words is the DESK gate's verdict, and none is restated in sections 1 to 6.

## 8. What Layer 5's first task would inherit as PROVISIONAL inputs

Layers 5 to 12 stay paused until the coordinator's DESK-gate verdict lets them advance ("After that scoped desk gate passes, advance to
the next layer." [OWN:476];
part 15 keeps Layers 5 to 12 paused except its named prerequisites [OWN:169]). Its first task would inherit, PROVISIONAL or OPEN:

- the PA interface texts IF-A-PA and IF-AD-HARNESS and the firmware row of the cap [T5R:51-56], on F01 / D-17 "PROVISIONAL" [F01:212-214];
- the contract rows FW-B20 to FW-B22 and V-B20 to V-B23, a draft "UNAPPLIED: the integrator runs it" [HWFW:2], with "FW-B22
  PROVISIONAL" and "V-B23's 0.2 s withdrawn" [HWFW:10];
- CON-004's quorum service OPEN and L9T5-F21 in IOHA section 12 [T10R:201-202], [T10:662-667];
- the DOCK_EN_OUT allowance still 30 uA in Layer 5's row, "their restatement is the owners'" [E11:2044];
- LH-12 with the withdrawn FAN_OK (K-03) [LH:28];
- U-04's mode table and IF-10, "(B1)'s mode table (E11-31), D2's step margin and the held pack current stay PROVISIONAL" [ANX:76];
- U-02's dependants, L4-E12's selection (c), the fan duty rows, the hot-stop lines and REQ-024's and REQ-052's acceptance rows [ANX:60];
- C-PROT rev 1 for the guard, "C-PROT rev 1 for the guard PROVISIONAL" [BRK:1398-1400];
- IF-01's protection claim for D-10, PROVISIONAL until E-1's correction and S1 [P11:85-86].

## 9. For the coordinator: what to check before adopting this text

- Slot D's evidence draft cites L4-E9's page at `1c6d56f5` lines (criteria at 937 to 943 [EVD:39-43]); at the base the same rows are
  [PAGE:966-970] and at set 31 [PAGE31:997-1001].
- The counts of sections 1 to 5 and the list K-01 to K-28 are held by `test_dgate.py`; a change of either changes the test's reading.
- The verdict placeholder appears once; the five completion claims are written as briefed; the design-gate words appear in section 7
  only.

## 10. Left out, and why

- **Slot I's four disagreements.** They are in Slot I's final message, not in any file of `fnd/lstat31` at `87c5fb08` (its page and
  `test_lstat31.py` hold none by that name); this draft lists the contradictions of the draft Slot I folded instead [LS30:133-169].
- **A re-read of the two stale pins outside P0's cascade at the base** (A2.7): not in the brief's scope; cited from Slot D.
- **A verdict word, a percentage, or any reading of a criterion as passed:** the coordinator's, by the brief.
- **The owner's part 26** (on main, `b0a67a45`, after the base): not in this branch's history; not cited.
- **No generator, suite, candidate_guard or sweep was run.** The pin comparison of A2.3, the digest comparison of F2.1 and the
  cache file's commit of A2.2 were read with `git` and `sha256sum` in the session and are held by the test at the base commit.
