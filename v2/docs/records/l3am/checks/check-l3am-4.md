accepted: yes
scope: Layer 3 amendment l3am (L3-R01 to L3-R05)
reviewed-revision: 8146b4cc09223c5486e7d553d8711854a3d7678c

# Layer 3 amendment, check 4: Claude's re-verification after a test of the amendment was corrected (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 1 October 2026. Check 3 (`check-l3am-3.md`, reviewed revision `cd231260`) closed the review findings and
held while every file of the amendment stayed byte for byte as it read them. Set 19 was promoted at `41881d8f` and the
baseline was accepted again there in the coordinator's worktree; the Layer 3 modules then read 142 passed and 2 failed on
that accepted tree, so nothing was committed. Both failures were tests pinned to the state before the re-acceptance:

- `t_l3am_the_acceptance_script_files_a_bound_record_and_supersedes` built its copy from the tree's `l3r2.yaml` and
  expected the history after `--supersede` to hold only the record it superseded; once the tree's own acceptance has been
  superseded the copy already holds the earlier record, so the history read `[b4b199d0's record, the new one]`. The
  property the test states ("--supersede keeps the filed record, as parsed, at the end of baseline_acceptance_history")
  holds; the expectation was wrong.
- `t_l3am_status_reads_the_review_until_it_is_closed` expected the amendment's status script to refuse a second run
  saying it has run, which it detects by the open status on LAYER-STATUS.md; the re-acceptance's page edit had removed it.
  Not a test change: the re-acceptance's status script (`apply_layer_status_reaccept.py`, not an amendment file) keeps the
  open status on the page once, as what the layer read until the acceptance.

**What changed since `cd231260`.** Among `l3amlib.AMENDMENT_FILES`, the registry, the owner brief and the definition change
record, only `v2/ecad/tools/tests/test_l3am.py`, by commit `8146b4cc`: the supersede test reads the history its copy holds
after filing without `--supersede` (`hist0`, asserted unchanged by the first filing) and expects `hist0` plus the superseded
record after `--supersede`, and the legacy-record branch expects the copy's history plus the tree's record. No assertion
was removed and none was weakened: an empty prior history gives the expectations of before.

**Verified at `8146b4cc`:**
- `checks/verify_l3am.py`: 16 of 16 (B1, the requirements digest by its principle on schema-valid fixtures; B2, the
  findings-closing verification).
- `test_l3am`: 7 passed, 1 failed, the failure being `t_l3am_findings_close_only_with_a_check_of_the_amendment` on the
  tree's own closure ("the amendment changed since the reviewed revision cd2312604f6b: v2/ecad/tools/tests/test_l3am.py"):
  the binding refusing check 3 for the changed file, as designed, until this check closes the findings.
- The corrected test holds in both states: it passes on the tree before the re-acceptance (no history) and its expectation
  is the one the acceptance script's own read-back enforces (`hist_before + [filed]`).

The post-acceptance state is verified by the integration set's simulation before promotion (`records/int20/README.md`),
not by this check. Result: the amendment at `8146b4cc` is the amendment check 3 reviewed, with one test's expectation
corrected; check 4 closes the findings in its place.
