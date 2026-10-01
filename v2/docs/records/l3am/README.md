# Layer 3 amendment: the independent review the owner relayed on 1 October 2026

MESHSAT-1357, branch `fnd/l3am` from main `b45d1705` (the acceptance of the Layer 3 baseline at `b4b199d0`, recorded
under the owner's conditional authorisation D-39). The owner relayed an independent engineering review of that handover
(`REVIEW-AS-RECEIVED.md`, the coordinator's abridged copy, filed byte for byte). This amendment answers its findings
L3-R01, L3-R02, L3-R04 and L3-R05 and the finding carried from the engineering collaborator's layer 4 check of 30
September 2026; L3-R03 (the export) is the coordinator's. `DISPOSITIONS.md` has one row per finding: what was done or
why not, the files and the closure criterion, and the follow-ups. Prototype design: nothing is bought, built or
measured; no owner-approved number changes.

Status until the amendment is checked and the baseline accepted again: **Layer 3 accepted baseline; independent review
findings open (L3-R01 to L3-R05)**, kept apart from "design compliance verified" and "fab-ready". The amendment changes
the requirements registry, and the acceptance of `b4b199d0` carries no content manifest, so the tree's status level reads
"requirements drafted / decisions recorded" until the re-acceptance below.

## Files here

| File | What it is |
|---|---|
| `REVIEW-AS-RECEIVED.md` | the review as the coordinator abridged it, byte for byte (its own dash characters kept as filed) |
| `DISPOSITIONS.md` | the findings' dispositions and the follow-ups |
| `l3amlib.py` | the scripts' shared helpers: each edit located by its own words, asserted once, re-parsed and compared (only the named keys, entries and fields may change) |
| `apply_l3am_findings.py` | files `l3r2.yaml` `review_findings` (the review at its sha, the findings, state OPEN, the status wording) and adds the content binding to the VALIDATED level's wording |
| `apply_l3am_r01.py` | L3-R01 and the carried finding: `l3r2.yaml` `solar_case` (the case the figures were computed with), REQ-072's notes, the owner brief's honest state, `DEFINITION-STATUS.md` (CFL-016 rebound) |
| `apply_l3am_r02.py` | L3-R02: REQ-042's acceptance (end to end, channel by channel), its history and waits_on, S-49's title (the selection only), the open item S-128 (layer 4), `l3r2.yaml`'s impacts and open-item layers |
| `apply_l3am_r05.py` | L3-R05: REQ-016's acceptance (protection judged apart from the window under TRN-001), history, source and satisfied_by; `l3r2.yaml`'s impacts entry |
| `apply_layer_status_l3am.py` | `LAYER-STATUS.md`'s layer 3: the status wording, the status level and completion status restated, the solar figures labelled |
| `apply_l3am_findings_closed.py` | the coordinator's, after the amendment's check: `review_findings` CLOSED, naming the check, only with a new accepted check of this amendment (the record format below); its `verify` is what `apply_l3r5_accept.py` runs again |
| `checks/astra-check-l3am-2.md` | the collaborator's targeted recheck (job `cx12-l3am-recheck`, run `20261001T003321Z-1017926`, on `932e0f7f`; accepted: no), filed byte for byte: B2 and the scope PASS; B1 failed a second time, the other way (closure progress kept in the digest), with two minors on B2 (the exact header, the test files compared); answered by the principle above |
| `checks/astra-check-l3am-1.md` | the engineering collaborator's one check of the amendment (job `cx10-l3am-check`, run `20260930T235755Z-972100`, on `29947b27`; accepted: no), filed byte for byte: L3-R01, L3-R02, L3-R05 and the supplied binding tests PASS; B1 (the requirements digest omitted the owner rulings, the session choices, the accepted exceptions and the stage conditions) and B2 (the findings could be closed with the pre-amendment check-l3r5-3) answered in the fix round below |
| `checks/check-l3am-3.md` | the amendment's check (accepted: yes; the three header lines of the format above; reviewed revision the integration candidate `cd231260`): Claude's verification of B1 and B2 after the collaborator's checks 1 and 2; not a model review and not an Astra check |
| `checks/verify_l3am.py` | the coordinator's check behind check-l3am-3, written independently of the author's tests: the digest under schema-valid closures and normative mutations, the bound acceptance, the closing verification; every expected outcome a literal |
| `apply_l3am_check3.py` | files check-l3am-3 as the newest ACCEPTED `independent_check`, after verifying its header; a second run is refused |

Changed elsewhere: `v2/docs/handover/layer3/render_l3r2.py` (the solar case, its labels and guard; the acceptance's
content binding, `acceptance_ok`, `content_manifest`, `manifest_at`; the review's and the acceptance record's lines),
`v2/docs/records/l3r5/apply_l3r5_accept.py` (the manifest, `--supersede`, the refusal while the findings are OPEN),
the tests `v2/ecad/tools/tests/test_l3am.py` (new), `l3amfix.py` (fixture commits: unreferenced objects, no ref) and
`test_l3r5.py` (three tests restated as properties that hold before and after a re-acceptance), and the generated pages
(`REQUIREMENTS-L3-R2.md`, `OWNER-DECISIONS-L3.md`, `L3-RECONCILIATION.md`, `v2/docs/REQUIREMENTS-TRACE.md`) through their
renderers. `DEFINITION-REISSUE-DRAFT.md` and `DEFINITION-CHANGE-RECORD-L3.md` do not move.

## Run order (on the integration set)

```
git merge --no-ff fnd/l3am
python3 v2/docs/records/l3am/apply_l3am_findings.py --check      (refused once applied: "has run")
python3 v2/docs/records/l3am/apply_l3am_r01.py --check           (refused once applied: "has run")
python3 v2/docs/records/l3am/apply_l3am_r02.py --check           (refused once applied: "has run")
python3 v2/docs/records/l3am/apply_l3am_r05.py --check           (refused once applied: "has run")
python3 v2/docs/handover/layer3/render_l3r2.py --check
python3 v2/docs/records/l3am/apply_layer_status_l3am.py --check  (refused once applied: "has run")
env -C v2/ecad/tools python3 rules_lib.py requirements
env -C v2/ecad/tools python3 rules_render.py --requirements --check
python3 v2/docs/records/l3r4/reissue.py --check
python3 v2/docs/records/l3r4/reissue.py --map --check
python3 v2/docs/records/l3r2/dryrun.py | cmp - v2/docs/records/l3r2/dryrun.out
python3 v2/docs/records/l3r5/checks/verify_b2.py . --fixture
env -C v2/ecad/tools/tests python3 run.py test_requirements test_l3r2 test_l3r4 test_l3r5 test_l3am test_public_hygiene
```

If the set's files are not this branch's, apply the scripts on the set in this order instead of taking the files:
`apply_l3am_findings.py`, `apply_l3am_r01.py`, `apply_l3am_r02.py`, `apply_l3am_r05.py`, `render_l3r2.py`,
`apply_layer_status_l3am.py`, `rules_render.py --requirements`. CFL-016's binding to `DEFINITION-STATUS.md` is carried by
`apply_l3am_r01.py`; `rules_render.py` re-renders the evidence pages on the set's evidence afterwards, as for any
registry change.

## The fix round on the amendment's check (1 October 2026)

- **B1, after the recheck (`checks/astra-check-l3am-2.md`).** The requirements digest of the acceptance's manifest is
  `render_l3r2.requirements_projection`, defined by a principle (`REQUIREMENTS_PRINCIPLE`), not field by field:
  **IN is whatever states what is demanded or authorised**: the statements, the acceptance, the applicability, the
  verification method and phase, the allocation, the owner's and the session's authority, the accepted risks and
  exceptions, and the stage requirements (`requires`, `needs`, `holds`). **OUT is any field that legitimately changes when
  downstream work progresses while the demand is unchanged**: closure state, closure evidence, derived summaries of stage
  state (`holds_layout_entry`), and readings; and commentary, provenance and bookkeeping, which demand nothing. Each field
  is placed in a category of the principle (`IN_CATEGORIES`, `OUT_CATEGORIES`, `REQUIREMENTS_FIELDS`; a field placed in
  none binds). A record's status is projected to its normative distinction only (`STATUS_PROJECTION`): DEFINED and TBD to
  LIVE, SUPERSEDED to SUPERSEDED, CONFLICT_OPEN and CONFLICT_RESOLVED to CONFLICT, FEASIBILITY_OPEN and FEASIBILITY_CLOSED
  to FEASIBILITY; a stage's status (OPEN, CLOSED) and its `closed_by` are out. The positive fixtures are closures the
  registry's own validator (`rules_lib.validate_requirements`) accepts with 0 errors: FEA-003's layout stage closed
  (status CLOSED, `closed_by`, `holds_layout_entry` emptied), FEA-003 closed altogether, CFL-006 between open and
  resolved, S-128 closed by a commit; each leaves the digest and a bound acceptance unchanged.
- **B2.** `apply_l3am_findings_closed.py` closes the findings only with a new accepted check of this amendment, in the
  format below, bound to a reviewed revision that is the tip or its ancestor, with the amendment unchanged since; the
  checks filed before the amendment (check-l3r5-3 among them) are refused. `apply_l3r5_accept.py` verifies the same check
  again against the revision it accepts, so a hand edit of the state does not open the acceptance.

## The record format of the amendment's check (B2)

The record's first three lines, exactly, then a blank line and the check's own text:

```
accepted: yes
scope: Layer 3 amendment l3am (L3-R01 to L3-R05)
reviewed-revision: <the full 40-hex commit the check read>
```

It is filed in `v2/docs/records/l3am/checks/` and listed as the newest entry of `l3r2.yaml`'s `independent_check`:
`{record: <path>, sha16: <its sha256/16>, verdict: ACCEPTED, scope: "..."}`. The reviewed revision must be a commit that is
the branch's tip or its ancestor, and the amendment must be unchanged since it: the requirements, the owner brief and the
change record as the acceptance's manifest hashes them, `l3r2.yaml` as its policy hashes it (also without
`independent_check` and `review_findings`), and every file of `l3amlib.AMENDMENT_FILES` byte for byte. The three lines
are compared exactly: no leading or trailing space and no carriage return.

## The re-acceptance (the coordinator's; D-39 remains a conditional authorisation)

1. The amendment's independent check, written in the format above and filed as the newest `independent_check` of
   `l3r2.yaml` (ACCEPTED only over a record whose first line reads "accepted: yes").
2. `python3 v2/docs/records/l3am/apply_l3am_findings_closed.py --check-record <that record>`, committed: the findings
   CLOSED (the acceptance script refuses while they are OPEN).
3. The gates and the suite on the revision that holds that content (its clean-clone check and box suite, as for
   `b4b199d0`).
4. `python3 v2/docs/records/l3r5/apply_l3r5_accept.py --supersede --revision <that revision> --evidence <paths> --date
   <YYYY-MM-DD>`: the record carries the content manifest the revision holds; the record of `b4b199d0` is kept in
   `baseline_acceptance_history`. Then `render_l3r2.py` and the layer status (a script of the coordinator's, as
   `apply_layer_status_l3_accept.py` was).
