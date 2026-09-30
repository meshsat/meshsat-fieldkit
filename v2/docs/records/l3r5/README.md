# Layer 3, round 5: the owner's target apart from the candidate's compliance (D-26), and M1's runtime first (D-27)

MESHSAT-1357, 30 September 2026, branch `fnd/l3r5` from `fnd/l3r4` at `a547fe1d` (round 4d, an ancestor of main
`00bba92a`), not from main's tip: the re-issue generator of round 4 is adjusted here, and main's later commits (the
round 4 checks, the public-file scrub, set 17's milestone) touch none of this branch's files. Preparation only: no owner
answer to `v2/docs/handover/layer3/OWNER-DECISIONS-L3.md` is recorded, and nothing here changes a requirement or a
baselined document. Prototype design: no V2 board has been fabricated, ordered or powered, and no kit has been field
deployed.

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
| `apply_layer_status_l3_r5.py` | `LAYER-STATUS.md`'s layer 3: the first gate condition on requirements that do not contradict, the independent check's re-check once a row is decided, the fifth condition, the round 3b rules followed by those that replace them, row L3-OD7 in the first two conditions and in the page's description, and the status level; refuses unless D-26 and D-27 are recorded; `--page` runs it on a copy; a second run is refused |
| `checks/l3feas-check-1/` | CHECK-1 of stream l3feas (not accepted) with `indep_l3feas.py` and its output, filed byte for byte |
| `checks/l3feas-check-2/CHECK-2.md` | CHECK-2 of stream l3feas (accepted: yes, of `c11b99d3`), filed byte for byte |
| `checks/l3batt-check-1/` | CHECK-1 of stream l3batt (accepted with minors, of `05ba0cf0`) with `indep_l3batt.py` and its output, filed byte for byte |
| `checks/l3batt-check-2/CHECK-2.md` | CHECK-2 of stream l3batt (accepted: yes, of `83577a13`), filed byte for byte |

Changed elsewhere: `v2/docs/handover/layer3/l3r2.yaml` and `render_l3r2.py` (the semantics, items, definitions, levels,
the gate and the three pages), `../l3r2/conditional/` (the scripts, `od_l3_7.py` new), `../l3batt/` (stream
l3batt's comparison at `83577a13`, filed byte for byte), `../l3r2/dryrun.py` and `dryrun.out`,
`../l3r4/reissue.py` and `PASSAGE-MAP.md`, `v2/ecad/tools/pcb_requirements.yaml` (D-26 and D-27 only),
`v2/ecad/tools/claims-allow.txt` (the reviewer's level name "Design and hardware compliant"), and the tests
`test_l3r2.py`, `test_l3r4.py` and the new `test_l3r5.py`.

## Run order on the integration set (the integrator)

```
git merge --no-ff fnd/l3r5        (or: git checkout fnd/l3r5 -- <the files above>, then the two scripts below on the set)
python3 v2/docs/records/l3r5/apply_l3r5_d26.py --check          (refused once applied: "has run")
python3 v2/docs/records/l3r5/apply_l3r5_d27.py --check          (refused once applied: "has run")
python3 v2/docs/records/l3r5/fill_l3r7_from_comparison.py --check   (refused once filled: "has run")
python3 v2/docs/records/l3r5/apply_layer_status_l3_r5.py --check (refused once applied: "has run")
python3 v2/docs/handover/layer3/render_l3r2.py --check
python3 v2/docs/records/l3r4/reissue.py --map --check
python3 v2/docs/records/l3r2/dryrun.py | cmp - v2/docs/records/l3r2/dryrun.out
env -C v2/ecad/tools python3 rules_lib.py requirements
env -C v2/ecad/tools python3 rules_render.py --requirements --check
env -C v2/ecad/tools/tests python3 run.py test_requirements test_l3r2 test_l3r4 test_l3r5 test_public_hygiene
```

If the set's registry is not this branch's, apply D-26, D-27 and the layer status by their scripts on the set (in that order)
instead of taking the two files, then re-render.
