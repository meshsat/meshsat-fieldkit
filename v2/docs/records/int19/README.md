# Integration set 18 (MESHSAT-1357, branch `fnd/int19`, 30 September 2026): the Layer 3 closure

Prototype design: nothing is bought, built or measured. The integrating session's records for set 18, from main
`6582bd41`. Layer 3's requirements completion is kept apart from circuit, PCB, thermal, runtime and product
verification (D-28, D-29).

| Step | Commit | What it did |
|---|---|---|
| 1 | `faf3a67b` | merge of `fnd/l3feas` at `c11b99d3`: the Layer 3 feasibility record (CHECK-2 accepted) |
| 2 | `5edb03c8` | merge of `fnd/l3batt` at `63897fc3`: the runtime-and-battery comparison and the illustrative tablet service budget (CHECK-3 accepted) |
| 3 | `302fff6d` | merge of `fnd/l3r5` at `72fec7fd`: the closure pass on the owner's clarifications D-26 to D-37 |
| 4 | `020669a7` | merge of `fnd/l3r5` at `c183c086`: the first fix round on the engineering collaborator's closure check (B1 to B3, M1; D-38) |
| 5 | `b3b0a0ad` | merge of `fnd/l3r5` at `d08929ea`: the second fix round (B2 held to the rulings structurally, the owner's clarification of history against current status), D-22 carried into REQ-072's acceptance, D-39 (the owner's conditional authorisation) and check 3 |
| 6 | this commit | `apply_rebind_page_set18.py`: CON-010 and REQ-044 rebound to the evidence page the set renders (`85256b70`, stable over two full render orders; FEA-008 is its change), `dryrun.out` regenerated (its only change is the validator's warning count, 2 to 0, on each chain: the two warnings were these bindings) |

**The closure's checks, attributed.** The engineering collaborator (Astra, `gpt-6-astra` at `xhigh`, read-only)
checked the closure twice, the owner's allowance of one assessment and one targeted follow-up: check 1 (`72fec7fd`)
and check 2 (`c183c086`) read NOT ACCEPTED; check 2 accepted B1, B3 and M1. Check 3 is Claude's (the coordinating
session's) verification of B2's final correction and D-22's trace at `a66c4e5b`, by its own check `verify_b2.py` and
the targeted tests; it is not a model review and not an Astra check, and Astra never examined those revisions. All
three are in `../l3r5/checks/`. M2 (a citation of `CODEX-WORKER.md` section 7) closes here: main carries that section.

**Acceptance.** D-39 authorises the baseline's acceptance once the gates pass and is not itself evidence that they
did. The acceptance is its own record (`baseline_acceptance` in `handover/layer3/l3r2.yaml`, `../l3r5/apply_l3r5_accept.py`),
filed against the promoted revision after this set's clean-clone check and box suite pass; the results are added
below when they exist.
