accepted: yes
scope: Layer 3 amendment l3am (L3-R01 to L3-R05)
reviewed-revision: cd2312604f6bb810176fc6ff7ed50281b67066b4

# Layer 3 amendment: Claude's verification of B1 and B2 at the integration candidate (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 1 October 2026. The amendment answers the independent engineering review of 1 October 2026 (L3-R01 to L3-R05;
`REVIEW-AS-RECEIVED.md`). The reviewed revision `cd231260` is integration set 19's candidate: `fnd/l3am` at `d3e3b415` merged with the Layer 4
records (`a789a6c2`), then the amendment's tests restated to hold before and after the findings close (`cd231260`).

## Attribution

- **Astra (the engineering collaborator)** checked the amendment twice, the owner's allowance of one assessment and one
  targeted follow-up: check 1 (`astra-check-l3am-1.md`, at `29947b27`) accepted L3-R01, L3-R02, L3-R05, the supplied
  binding tests and the scope, and found B1 (the requirements digest omitted normative content) and B2 (the findings-closing
  script accepted the pre-amendment check); check 2 (`astra-check-l3am-2.md`, at `932e0f7f`) accepted B2 and the scope and
  found B1 again, now in the opposite direction (closure progress in the digest). **Astra never examined `d3e3b415` or the
  reviewed revision.**
- **Claude (the coordinating session)** verified the final B1 (a principle: what is demanded or authorised IN, what changes
  legitimately with downstream progress OUT; mixed status values projected to their normative distinction) and B2 at the
  reviewed revision, by its own check `verify_l3am.py` (filed beside this record, written independently of the author's
  tests) and the author's tests, run by the coordinator.
- L3-R03 (the export) is the coordinator's and is verified in the corrected review package, not here.

## Evidence at the reviewed revision

- `verify_l3am.py`: 16 of 16 as the closure criteria require, at `a789a6c2` and again at `cd231260`. A layout-stage closure of FEA-003 made as `rules_lib`
  requires (status CLOSED, `closed_by`, the hold summary emptied) passes the registry's own validator with 0 errors and
  leaves the requirements digest unchanged, as do an added reading and note; six normative mutations change it (REQ-016's
  statement at 500 W, REQ-072's acceptance, owner ruling D-34's text, CON-012's accepted residual risk, a stage's
  `requires`, a record superseded). An acceptance bound at the reviewed revision validates; one at forty zeros, at
  `b4b199d0` (a commit holding other content), with REQ-016 changed afterwards, or without a manifest does not; one after a
  schema-valid downstream closure still validates. The pre-amendment `check-l3r5-3` is refused by the findings-closing
  verification for its missing scope line.
- The findings-closing verification probed with records the coordinator wrote and removed: the exact header at the reviewed
  revision is accepted; a padded first line and a missing scope line are refused, each for its stated reason; a record that
  reviewed `a789a6c2` is refused at `cd231260` because the amendment's test files changed after it (the binding working).
- Validators at the reviewed revision: `rules_lib` 145 requirement records, 0 errors, 0 warnings; the full render order
  reaches the same evidence page twice with nothing changed.
- The six test modules: at `a789a6c2`, run by the coordinator, 141 passed, 0 failed, 0 skipped (test_requirements 66,
  test_l3r2 27, test_l3r4 15, test_l3r5 21, test_l3am 8, test_public_hygiene 4); with the findings closed there, 138
  passed and 3 failed (three tests read the tree's OPEN state), restated at `cd231260`; at the content of `cd231260`, run
  by the author before the commit, 141 passed, 0 failed, 0 skipped. The coordinator's own run on the filed state follows
  in the set's integration record.

## Result

B1 and B2 are closed against the collaborator's own closure criteria. With check 1's acceptance of L3-R01, L3-R02, L3-R05
and the scope, every finding the amendment answers is closed except L3-R03, the coordinator's export, verified separately.
This record is evidence for closing the review findings; it is not the owner's acceptance of the amended baseline, which is
filed against the verified revision after the integration gates pass (D-39, a conditional authorisation).
