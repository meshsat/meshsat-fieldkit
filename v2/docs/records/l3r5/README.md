# Layer 3, round 5: the target apart from the candidate (D-26), M1's runtime first (D-27), and the closure (D-28 to D-31)

MESHSAT-1357, 30 September 2026, branch `fnd/l3r5` from `fnd/l3r4` at `a547fe1d` (round 4d, an ancestor of main
`00bba92a`), not from main's tip: the re-issue generator of round 4 is adjusted here, and main's later commits (the
round 4 checks, the public-file scrub, set 17's milestone) touch none of this branch's files. The round ends in layer 3's
closure: the owner's clarifications D-28 and D-29 are applied to the registry (`apply_l3r5_closure.py`), and the
definition re-issue is drafted for his approval; `CONOPS.md` and `PRODUCT-BRIEF.md` themselves are not edited. Prototype
design: no V2 board has been fabricated, ordered or powered, and no kit has been field deployed.

## The closure (D-28 to D-31)

- **The owner's words**, quoted word for word in `v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md` and recorded
  by `apply_l3r5_d28_d29.py`, `apply_l3r5_d30.py` and `apply_l3r5_d31.py`: D-28, the energy and runtime requirement
  (no external battery; storage inside the Peli 1450; battery and solar required; HF and the tablet kept; 48 to 72 hours
  a design objective under a stated profile; optional tablet charging reducing endurance, accepted); D-29, CFL-017
  (product requirements apart from the current cell); D-30, the Codex worker and one decision register; D-31, one
  authoritative interpretation, kept as the **current owner brief** at the top of that file, each line naming the
  ruling that carries it, the superseded instructions marked in place.
- **Applied** (`apply_l3r5_closure.py`): rows L3-OD2 to L3-OD7 answered by rulings D-32 to D-37 (both lid items kept,
  REQ-016 unchanged, no deployment condition, CFL-017 a layer 4 obligation, SC-37's mean day in TYP, M1's runtime the
  objective); row L3-OD1 closed as layer 4 architecture (the session's, under D-21 and D-28: D-06 stands, Option A(i) a
  layer 4 proposal needing the owner's ruling there). REQ-072 becomes the registry's only **design objective**
  (`obligation: OBJECTIVE`, its `objective_profile`, MUST_JUSTIFY), its modelled baseline read from the bound
  `runtime.out`: it reads FAIL, design risk DR-01. REQ-014 carries the store inside the Peli 1450; REQ-011 the tablet's
  charging as a capability at the outlet; REQ-017 R138's trip (CHECK-3 of stream l3batt); CFL-017 is resolved and
  FEA-008 carries the cell and thermal design mode by mode (`l3r2.yaml` `cell_modes`, LO-01a to LO-01h); M-02 is closed
  by D-28. The validator (`rules_lib.py`) holds the obligation field; the trace page and the requirements page mark each
  record mandatory or objective.
- **The cell's provenance** (`l3r2.yaml` `cell_provenance`): the Samsung 35E is named in the owner's pack rulings as the
  pack's content, D-06 was ruled at the session's recommendation, and no ruling states the model as a product
  requirement; D-29 itself calls it "the currently selected Samsung 35E cells". So CFL-017 is a collision between the
  requirements and the current component; no owner decision remains.
- **The handover package**: `REQUIREMENTS-L3-R2.md` section 2 (the owner's closure, mandatory and objective, the modelled
  baseline, the design risks DR-01 to DR-07, CFL-017 by mode, the completion statuses kept apart), the decision page
  (the closure, the consolidated message Q1 to Q10 reconciled, the rows answered), `LAYER-STATUS.md`
  (`apply_layer_status_l3_r5b.py`), and the definition re-issue drafted (`handover/layer3/DEFINITION-REISSUE-DRAFT.md`
  and `DEFINITION-CHANGE-RECORD-L3.md`, by `../l3r4/reissue.py` in its settled mode) for the owner's approval.
- **The runtime comparison** is filed at its final tip `63897fc3` with CHECK-3 (the tablet's service budget, R138's
  finding); PROVENANCE.md and SHORTLIST.md stay bound by CHECK-2, which lists them (`runtime_provenance_basis`).
- **The prepared scripts' dry runs and tests** start from the registry as it stood before the closure (`l3r2.yaml`
  `closure_cycle.pre_closure_commit`, read from git; `v2/ecad/tools/tests/l3pre.py`), since the tree's rows are decided.

## The fix round on the collaborator's closure check (30 September 2026)

The engineering collaborator's read-only closure check of `72fec7fd` (`checks/astra-check-l3r5-1.md`, "accepted: no")
found three blocking discrepancies and two minors; no owner decision was required. Answered here, each at its source:
**B1**, the current owner brief no longer places the registry's ASM and CHO records under two blanket lines; it names
REQ-072's profile as the modelling assumptions and the Samsung INR18650-35E as the one replaceable selection, and lists
the ASM and CHO records one by one with the owner rulings that bind them (ASM-006's "operate shaded" under D-02e,
ASM-002's D-03 residual, CHO-001's device set, CHO-003's D-16). **B2**, `l3r2.yaml`'s classification rows for "72 hours
in PS-IDLE-SPEC" and for the deployment conditions keep their place marked SUPERSEDED by D-28 (applied as D-32 and
D-35) with what holds now beside them, the registry's SC-21 is marked superseded in place (`apply_l3r5_supersede_sc21.py`;
the trace page and the operating-conditions table print the mark), D-21's quoted "approved 72-hour mission" carries its
mark in that table (`superseded_marks`), proposal P-17 and acceptance definition 1b carry theirs. **B3**, the owner's
closure instructions are recorded word for word as D-38, which decides the definition re-issue; the draft and the change
record are regenerated once at the decided state with the approval route that holds (authority D-38, acceptance the
targeted independent review), `definition_reissue` is filed, `CONOPS.md` and `PRODUCT-BRIEF.md` are not edited (their
re-stamp is closure item L3-C63, the integrator's), and `DEFINITION-STATUS.md`, the requirements page and the owner
brief say that the change record governs where a document differs until then. **M1**, DR-03 names the 15 V contract.
**M2** (D-30's citation of `CODEX-WORKER.md` section 7, on main since `7e4b7a87` and not on this branch) is the
integrator's. The gate's fourth condition reads NOT MET until the targeted recheck is filed.

What else moved, and why: `../l3r4/apply_layer_status_l3_r4.py` verifies the newest ACCEPTED check (CHECK-5) rather
than the newest check, which is now the collaborator's NOT_ACCEPTED one; `render_l3r2.py` prints the classification
rows' supersession, the operating conditions' marks (`l3r2.yaml` `superseded_marks`, the registry's `superseded_by` on
SC-21), the acceptance definitions' marks and the re-issue's state; `rules_render.py` prints a superseded session
choice (its bundle is `rules_complete`'s and `rules_status`'s, which judge the registry and are re-taken by the full
render, as after the closure); `../l3r4/reissue.py` states the approval route that holds once a ruling decides the
re-issue; `../l3r2/l3edit.py` gains `rebind_to_tree`, which `../l3r2/dryrun.py` and the tests' `l3pre.py` apply to the
pre-closure registry so that CFL-016's PASS, rebound in the tree to the status page as it now stands, still validates
there; `dryrun.out` is refreshed, and differs from the one filed at `e5286397` only in its warning counts (2 where it
read 0: CON-010 and REQ-044, bound to the `CURRENT-EVIDENCE.md` render before that commit's, as in the tree); the tests
`test_l3r2.py` (the verdict test follows the newest check), `test_l3r4.py` (its fixtures generate on a copy of
`l3r2.yaml` with `definition_reissue` null, the pre-approval state) and `test_l3r5.py` (the brief's line bound, and two
tests of this round).

## What the review found, and the ruling

The owner's reviewer reviewed the decision brief `MESHSAT-L3-OWNER-DECISIONS-2026-09-30.md` (sha256/16
`ca4a9dcfa2e076ff`, a laptop file) and read it "CONDITIONAL for individual owner choices; BLOCKED for blanket approval
or a claim that the revised Layer 3 baseline is fully validated". Its central finding: the decision logic confused a
candidate's failure with an invalid owner requirement. Six of its passages are quoted word for word in
`v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md` and recorded as owner ruling D-26 (`apply_l3r5_d26.py`).

## The owner's addendum (D-27)

During round 5 the owner questioned the 72-hour requirement. Relayed by the coordinating session and quoted word for word
in the instruction file: "Evaluate alternatives before asking me to sacrifice functions or accept restrictive deployment
conditions." and, as relayed, "He also said to preserve HF and the tablet functionality." It is recorded as owner ruling
D-27 (`apply_l3r5_d27.py`). What it changes here:

- **Row L3-OD7, M1's runtime and its store**, joins the table ahead of the others, filled from stream l3batt's bounded
  runtime and battery comparison (`../l3batt/`, filed byte for byte at its checked tip `83577a13`, accepted by CHECK-2;
  CHECK-1, accepted with minors, beside it) and bound in `l3r2.yaml` `runtime_comparison`. The owner's four choices:
  `72-required` (Option B) or `48-required-72-desired` (Option A); `--hf available|listening` (the receiver's 1.14 W);
  `--external authorise-vbat|authorise-dc-entry|no` (a separately protected external pack joined at VBAT, which reopens
  D-06; through the DC entry, which revisits D-20; or none, M1 recorded as not met with HF and the tablet kept, M-02);
  `--tablet-charging no|yes` (unquantified until a tablet model is named, SC-45). Its table (`runtime_table`) is filled by
  `fill_l3r7_from_comparison.py` from `runtime.out` by exact keys (`runtime_reader.py`) and read back; `od_l3_7.py`
  verifies it again before it writes. The checked facts: with HF and the tablet kept the studied store (Option A(i)'s
  base 4S6P and lid 4S9P, 544.4 Wh usable aged at +20 C) stops the kit at 05 UTC of the first night in every case, 0 of
  864 windows, at 48 and at 72 hours; the addition it needs is +68.1 Wh at NOM TYP, +79.6 (48 h) and +116.2 (72 h) at WE
  TYP, +84.2 to +187.1 with the receiver on, up to +188.7 with WAB; no in-case upgrade is found. The session's
  recommendation, the comparison's: A is no relief; B only with an authorised external store (about 120 Wh at TYP, about
  190 Wh with the receiver on or WAB); otherwise M1 recorded as not met.
- **Feasibility items FI-07 to FI-09**: the external store authorised (CONDITIONAL on its size, FI-07), none (NO_ROUTE,
  M1 recorded as not met, FI-08), the tablet charged (INCONCLUSIVE until a tablet model is named, FI-09). FI-04 (both
  lid items kept) now says it is carried only with an external store.
- **Rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6 wait on it.** Their scripts refuse while row L3-OD7 is unanswered
  (`cond.runtime_first`); then rows L3-OD1, L3-OD2 and L3-OD4 carry its answer (`cond.runtime_phrases`: REQ-072's
  duration, load and store in row L3-OD1's restatement), and row L3-OD6, whose table sizes the store for 72-hour windows
  at the approved profile, refuses after 48 hours or HF listening until it is restated from the comparison (closure
  item L3-C56). The pages read the four HELD (D-27) with their recommendations stated only for the case row L3-OD7 is
  answered as prepared. **Both lid items kept, the owner's stated wish, is never refused**: without an external store it
  records FI-04, with one its candidate is FI-07's. Two contradiction rules join: row L3-OD6 beside 48 hours or HF
  listening, and row L3-OD2's `qmx-out` beside HF listening (a receiver cannot listen in a kit with no HF set).
- **Provenance** (`l3r2.yaml` `runtime_provenance`, closure item L3-C57, CLOSED on the bound record): the 72 hours are
  SC-21, the session's choice under the standing rule, first appearing as SC-L2-05 at `de59686e`; D-20 preserved M1 and
  REQ-072 "with their specified duration and operating conditions" and states no figure; D-21 is the owner's first use
  of the figure; its provenance as the owner's is UNVERIFIED (`../l3batt/PROVENANCE.md`). Each clause is read by
  `test_l3r5.py`. Proposal P-12 (a shorter mission) is AWAITING again, on row L3-OD7.
- **The re-issue generator** maps `72-required` with HF available, no external store and the tablet not charged (the 72
  hours named as the owner's: CONOPS lines 163 to 165, 1019 to 1024 and 1101, the brief's line 309) and refuses every
  other answer of row L3-OD7 until its passages are mapped with the comparison's figures.

## What changes (D-26)

**Semantics.** An answer records the owner's REQUIREMENT TARGET. Beside every option stands the studied candidate's
status (PASS on a named case, FAIL by how much, INCONCLUSIVE with what is missing, CONDITIONAL on which corrections) and
its feasibility disposition (CREDIBLE, CONDITIONAL, INCONCLUSIVE with the evidence named, NO_ROUTE with a quantified
trade-off returned to the owner, or OWED). A target the candidate does not meet is valid and records a feasibility item
(`l3r2.yaml` `feasibility_items`, FI-01 to FI-06), written by the prepared script as a feasibility record in the
registry (kind feasibility, FEASIBILITY_OPEN, a BLOCKER on the requirement it blocks, reading FAIL or INCONCLUSIVE,
never PASS, bound to its evidence files by sha). Now valid, each with its item: row L3-OD1 `reject` (FI-01: battery and
solar stay mandatory, D-06's one pack kept, REQ-072 unchanged, the other rows still answerable), a lid that does not
carry row L3-OD6's store in its build, HF kept with WAB among them (FI-02), a coverage target (FI-03), both lid items
kept (FI-04), the open kit's push (FI-05) and the solar interface's compliance under any row L3-OD3 answer (FI-06). Row
L3-OD4's adopt no longer waits on row L3-OD6 or on a particular array or lid. Still refused, as requirements that cannot
both hold (`l3r2.yaml` `contradictions`): row L3-OD2 answered while row L3-OD1 stands rejected (every row L3-OD2 option
sets a lid pack, a reject keeps D-06's one pack); a plane band adopted for another array or weather basis than it was
derived for (no band exists, so it binds nothing today); and one ruling on the array (row L3-OD3 alone). The flags
"CANNOT MEET" are candidate statements scoped to the studied architecture and its established arrangements.

**Acceptance definitions**, each written into the prepared restatement: 1b, REQ-072 at the kit loads with the exact
reference case of stream l3feas's record (`od_l3_1.py --pass-line kit-loads|each-pack`, the owner's sub-choice 1b); 3,
REQ-016's topology apart from its electrical compliance, with the obligations O-1 to O-7 (`od_l3_3.py`, FI-06); 4b,
REQ-078's full test conditions with the push as a design target the owner chooses, not a standard (`od_l3_4.py adopt
--push-n N`, FI-05); 5, CFL-017's mode-specific environment table and its operational consequence
(`od_l3_5.py reading-c`, REQ-051's notes). They are shown on `OWNER-DECISIONS-L3.md`.

**Status levels and the gate.** The reviewer's three levels (`l3r2.yaml` `status_levels`) are stated on
`REQUIREMENTS-L3-R2.md` section 2, `OWNER-DECISIONS-L3.md` and `LAYER-STATUS.md`; none holds today. The completion gate
gains its fifth condition, every recorded target with a feasibility disposition that is not OWED on the feasibility
record bound to its checked tip (closure item L3-C54), and its fourth reads NOT MET once a row is decided while the last
accepted check covers the handover with the decisions pending (the decided issue is checked again).

**The feasibility record.** Stream l3feas's bounded record is filed byte for byte at its checked tip `c11b99d3` under
`../l3feas/` (`L3-FEASIBILITY.md`, `hf_wab.py` and `.out`, `solar_interface.py` and `.out`) and named in `l3r2.yaml`
`feasibility_basis`; the renderer and the scripts verify it by `basis_binding.py` (every file identical to the tip's,
the check reading "accepted: yes", naming the tip and listing each file's sha256). Its two checks are filed byte for
byte: `checks/l3feas-check-1/` (CHECK-1 of `24942a5f`, not accepted, with its independent script and output) and
`checks/l3feas-check-2/CHECK-2.md` (CHECK-2 of `c11b99d3`, accepted).

**The re-issue generator** (`../l3r4/reissue.py`) refuses only the contradictions, writes the re-issue for a reject
(D-06's one pack kept with FI-01, row L3-OD2 not applicable), and reads its PACK and CELL patterns across line breaks
and punctuation (CHECK-4 of round 4d: CONOPS lines 233 to 234 exempted, 322, 323, 580 to 582, 646 to 648, 727 to 732,
885 and 1112 in PACK, 341 to 342 in CELL).

## Files here

| File | What it is |
|---|---|
| `apply_l3r5_d26.py` | records D-26 once; every quote asserted in the instruction file first; a second run is refused |
| `apply_l3r5_d27.py` | records D-27 once, the same way; refuses unless D-26 is recorded |
| `runtime_reader.py` | reads stream l3batt's `runtime.out` by exact keys; a section short of its lines is refused, never read in part |
| `fill_l3r7_from_comparison.py` | fills row L3-OD7's `runtime_table` from the bound `runtime.out`, reads it back, refuses a second run |
| `apply_l3r5_d28_d29.py`, `apply_l3r5_d30.py`, `apply_l3r5_d31.py` | record the owner's clarifications D-28 and D-29, his instruction on the Codex worker D-30 and his operating instruction D-31, each once, every quote asserted in the instruction file first |
| `apply_l3r5_closure.py` | applies D-28 and D-29 to the registry: the rows' rulings D-32 to D-37, REQ-072 the design objective, REQ-014, REQ-011, REQ-017, REQ-002, REQ-016 and REQ-051, CFL-017 resolved, FEA-008, M-02 closed; refuses a second run |
| `apply_layer_status_l3_r5b.py` | `LAYER-STATUS.md`'s layer 3 at the closure: the closure paragraph, the gate and status level, the completion statuses, the owner's part of the remaining items; `--page` runs it on a copy; a second run is refused |
| `checks/l3batt-check-3/` | CHECK-3 of stream l3batt (accepted with minors, of `63897fc3`; minor 1 the R138 finding) with `indep_tablet.py`, `indep_tablet2.py` and their outputs, filed byte for byte |
| `tool_compat_l3r5.out` | `../rel2/tool_compat.py a547fe1d` over the 39 verdicts of `derate.py`, `intent_checks.py`, `edge_length.py` and `emc_sheet.py` that carry a code bundle: the obligation field's edit of `rules_lib.py` changes `validate_requirements` and adds `OBLIGATION`, and no file of the four bundles reaches either; the evidence of the four `kind: tool` entries of 30 September 2026 in `v2/docs/evidence/COMPATIBILITY.md` |
| `apply_layer_status_l3_r5.py` | `LAYER-STATUS.md`'s layer 3: the first gate condition on requirements that do not contradict, the independent check's re-check once a row is decided, the fifth condition, the round 3b rules followed by those that replace them, row L3-OD7 in the first two conditions and in the page's description, and the status level; refuses unless D-26 and D-27 are recorded; `--page` runs it on a copy; a second run is refused |
| `checks/l3feas-check-1/` | CHECK-1 of stream l3feas (not accepted) with `indep_l3feas.py` and its output, filed byte for byte |
| `checks/l3feas-check-2/CHECK-2.md` | CHECK-2 of stream l3feas (accepted: yes, of `c11b99d3`), filed byte for byte |
| `checks/l3batt-check-1/` | CHECK-1 of stream l3batt (accepted with minors, of `05ba0cf0`) with `indep_l3batt.py` and its output, filed byte for byte |
| `checks/l3batt-check-2/CHECK-2.md` | CHECK-2 of stream l3batt (accepted: yes, of `83577a13`), filed byte for byte |
| `checks/astra-check-l3r5-1.md` | the engineering collaborator's closure check of `72fec7fd` (accepted: no; read-only, job cx5-l3-closure-check), filed byte for byte and named in `l3r2.yaml` `independent_check` as NOT_ACCEPTED: B1 (the owner brief's blanket ASM and CHO lines), B2 (superseded conditions classified as requirements, SC-21 reading "GOVERNS"), B3 (the definition re-issue unfinished), minors M1 (15 V) and M2 (D-30's section 7 citation); B1 to B3 and M1 answered by the fix round below |
| `apply_l3r5_supersede_sc21.py` | the fix round, B2: marks SC-21 superseded in place by D-28 (applied as D-32) with `superseded_on`, `superseded_by` and `superseded_why` and one dated sentence closing `why`; `taken` and `closes` unchanged; refuses a second run |
| `apply_l3r5_d38.py` | the fix round, B3: records the owner's closure instructions (three messages, quoted word for word in the instruction file) as D-38, the ruling that decides the definition re-issue (`decides: definition_reissue`); the session's reading labelled as such; refuses a second run |
| `apply_definition_status_l3r5.py` | the fix round, B3: adds to `handover/DEFINITION-STATUS.md`, from the change record and the draft, one row in "Where the current state lives" and the section stating that the re-issue is authorised by D-38 and accepted by the targeted review, that neither document is re-stamped yet, that until then the approved change record governs where a document differs, and the rows the draft proposes (DC-L3-M1); refuses unless `definition_reissue` is filed, and a second run |
| `apply_layer_status_l3_r5c.py` | the fix round, B3: `LAYER-STATUS.md`'s layer 3 no longer says the re-issue waits on the owner's approving ruling (the closure paragraph, the gate's third and fourth rows, the status level, whose each item is); the third row's state is read from `REQUIREMENTS-L3-R2.md`'s live gate; refuses a second run |
| `checks/astra-check-l3r5-2.md` | the engineering collaborator's targeted recheck of `c183c086` (accepted: no; job cx6-l3-closure-recheck, read-only): B1, B3 and M1 accepted, B2 not, filed byte for byte |
| `apply_l3r5_d22_req072.py` | carries owner ruling D-22 (an energy claim holds across the charge bus's supply range) into REQ-072's desk acceptance from the checked energy basis's figures; no new requirement; a second run is refused |
| `apply_l3r5_d39.py` | records the owner's conditional closure authorisation as D-39 (`decides: layer3_baseline`), his words quoted; not evidence that any gate passed; a second run is refused |
| `apply_l3r5_accept.py` | files `baseline_acceptance` (the verified revision, D-39, the evidence) once the gates have passed; run by the integrator after the set's clean-clone check and suite, never before |
| `checks/check-l3r5-3.md` | check 3: Claude's (the coordinator's) verification of B2's final correction against check 2's own criterion as the owner clarified it, and of D-22's trace, at `a66c4e5b` (accepted: yes); not a model review and not an Astra check |
| `checks/verify_b2.py` | the coordinator's own check behind check 3, written independently of the author's tests; reads the files, writes nothing; `--fixture` runs its three fixture cases |
| `apply_l3r5_check3.py` | files check 3 in `independent_check` as ACCEPTED after the two NOT_ACCEPTED Astra checks; the record's first line is verified; a second run is refused |

Changed elsewhere: `v2/docs/handover/layer3/l3r2.yaml` and `render_l3r2.py` (the semantics, items, definitions, levels,
the gate, the closure's sections and the three pages), `OWNER-INSTRUCTION-2026-09-30.md` (the current owner brief at
its top, D-26 to D-31 quoted, the superseded instructions marked in place, the session's reading),
`DEFINITION-REISSUE-DRAFT.md` and `DEFINITION-CHANGE-RECORD-L3.md` (new, generated), `v2/docs/handover/LAYER-STATUS.md`,
`../l3r2/conditional/` (the scripts, `od_l3_7.py` new), `../l3batt/` (stream l3batt's comparison at `63897fc3`, filed
byte for byte), `../l3r2/dryrun.py` and `dryrun.out`, `../l3r4/reissue.py` (its settled mode) and `PASSAGE-MAP.md`,
`v2/ecad/tools/pcb_requirements.yaml` (D-26 to D-37 and the closure's records), `rules_lib.py` and `rules_render.py`
(the `obligation` field and `objective_profile`), `v2/docs/REQUIREMENTS-TRACE.md` (regenerated),
`v2/docs/evidence/COMPATIBILITY.md` (four `kind: tool` entries, so CMP-001, PWR-001 and SI-001 keep their current
readings, VALID_HISTORICAL by rationale, instead of reading TOOL_CHANGED after the `rules_lib.py` edit),
`v2/docs/CURRENT-EVIDENCE.md` and `v2/docs/PCB-OPEN-PAIRS.md` (rendered on this branch's copy of the evidence: FEA-008
among the feasibility records, the 19 readings through the entries, SGN-001 re-taken by the render),
`v2/ecad/tools/claims-allow.txt` (the reviewer's level name "Design and hardware compliant" and the owner's two quoted
sentences), and the tests `test_l3r2.py`, `test_l3r4.py`, the new `test_l3r5.py` and its helper `l3pre.py`, and
`test_requirements.py` (its blocker test states the scope as a property: a feasibility record blocking a core record is
a core BLOCKER, one blocking only deferred records, FEA-008, may be deferred; the review's six pages keep their core
BLOCKERs).

## Run order on the integration set (the integrator)

```
git merge --no-ff fnd/l3r5        (base a547fe1d, an ancestor of main; or the scripts on the set, below)
python3 v2/docs/records/l3r5/apply_l3r5_d26.py --check          (refused once applied: "has run")
python3 v2/docs/records/l3r5/apply_l3r5_d27.py --check          (refused once applied: "has run")
python3 v2/docs/records/l3r5/fill_l3r7_from_comparison.py --check   (refused once filled: "has run")
python3 v2/docs/records/l3r5/apply_l3r5_d28_d29.py --check      (refused once applied: "has run")
python3 v2/docs/records/l3r5/apply_l3r5_d30.py --check          (refused once applied: "has run")
python3 v2/docs/records/l3r5/apply_l3r5_d31.py --check          (refused once applied: "has run")
python3 v2/docs/records/l3r5/apply_l3r5_closure.py --check      (refused once applied: "has run")
python3 v2/docs/records/l3r5/apply_layer_status_l3_r5.py --check (refused once applied: "has run")
python3 v2/docs/records/l3r5/apply_layer_status_l3_r5b.py --check (refused once applied: "has run")
python3 v2/docs/records/l3r5/apply_l3r5_supersede_sc21.py --check (refused once applied: "has run")
python3 v2/docs/records/l3r5/apply_l3r5_d38.py --check          (refused once applied: "has run")
                                  (then, once only, before definition_reissue is filed: python3 v2/docs/records/l3r4/reissue.py)
python3 v2/docs/records/l3r5/apply_definition_status_l3r5.py --check (refused once applied: "has run")
python3 v2/docs/records/l3r5/apply_layer_status_l3_r5c.py --check (refused once applied: "has run")
python3 v2/docs/handover/layer3/render_l3r2.py --check
python3 v2/docs/records/l3r4/reissue.py --check
python3 v2/docs/records/l3r4/reissue.py --map --check
python3 v2/docs/records/l3r2/dryrun.py | cmp - v2/docs/records/l3r2/dryrun.out
env -C v2/ecad/tools python3 rules_lib.py requirements
env -C v2/ecad/tools python3 rules_render.py --requirements --check
env -C v2/ecad/tools python3 rules_status.py; env -C v2/ecad/tools python3 rules_render.py --no-refresh
                                  (on the set's evidence; then rules_render.py --check reads 0 out of date)
env -C v2/ecad/tools/tests python3 run.py test_requirements test_l3r2 test_l3r4 test_l3r5 test_public_hygiene
```

If the set's registry is not this branch's, apply by their scripts on the set, in this order, instead of taking the files:
D-26, D-27, the row 7 fill, D-28 and D-29, D-30, D-31, the pages rendered once (the closure's FEA-008 names blocker ids
the requirements page carries), the closure, the two layer status scripts, then `reissue.py` (the draft) and the pages
again. The dry run reads the pre-closure registry from git at `2cd18f6d`, a commit of this branch.
