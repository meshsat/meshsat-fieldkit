# Integration set 19 (MESHSAT-1357, branch `fnd/int20`, 1 October 2026): the Layer 3 amendment and the Layer 4 energy records

Prototype design: nothing is bought, built or measured. The integrating session's records for set 19, from main
`d841540d`, with main's later commits `964795c8` and `1b1fe7df` (the owner's compute rulings of 1 October 2026 in the
execution plan) merged in at step 5. Requirements maturity, design compliance and physical verification stay apart.

| Step | Commit | What it did |
|---|---|---|
| 1 | `d5dab19f` | merge of `fnd/l4e` at `3ed52f3a`: Layer 4's energy records (L4-E1, the comparison L4-E2 with its service ledger and O-2's enumerated bound, the independent power review's items L4-E3 on a nominally compatible candidate panel, the engineer's packet), their checks (two of the engineering collaborator's not accepted, the coordinator's verifications accepted) |
| 2 | `a789a6c2` | merge of `fnd/l3am` at `d3e3b415`: the Layer 3 amendment on the independent review (L3-R01 the solar case labelled, L3-R02 REQ-042's end-to-end acceptance, L3-R04 the acceptance bound to the reviewed content, L3-R05 REQ-016's protection judged apart), with the collaborator's two checks of it (not accepted) |
| 3 | `cd231260` | the amendment's tests restated to hold before and after the review findings close (copies built from the open state; the tree's own closing check is never a fixture) |
| 4 | `7a1523d0` | the coordinator's amendment check `check-l3am-3` (reviewed revision `cd231260`) filed, the review findings CLOSED by `apply_l3am_findings_closed.py`, the pages rendered |
| 5 | `8e4262ce` | merge of main at `1b1fe7df`: the execution plan's two entries of 1 October 2026 (the compute ruling and its amendment); no other file |
| 6 | this commit | this record |

**The amendment's checks, attributed.** The engineering collaborator (Astra, `gpt-6-astra` at `xhigh`, read-only)
checked the amendment twice, the owner's allowance of one assessment and one targeted follow-up: both read NOT
ACCEPTED (`../l3am/checks/astra-check-l3am-1.md`, `-2.md`), and each finding was answered on `fnd/l3am`. Check 3 is
Claude's (the coordinating session's) verification of B1 and B2 at `cd231260` by its own check
`../l3am/checks/verify_l3am.py` (16 of 16) and the refusal probes; it is not a model review and not an Astra check. A
first draft of check 3, written against `a789a6c2`, was discarded before commit when the test edits of step 3 changed
the amendment's files after it; it was re-issued against `cd231260`, so the closing check's reviewed revision holds the
amendment as it is promoted.

**Layer 4's checks, attributed.** The collaborator checked L4-E2 twice and L4-E3 once (none accepted); each was closed
by the coordinator's own verification of the corrected candidate (`../l4e/checks/check-l4e2-3.md`,
`../l4e/checks/check-l4e3-2.md`); the panel's source compliance stays INCONCLUSIVE under the maker's 10 % qualification.

**Acceptance.** The baseline accepted at `b4b199d0` stays filed until it is superseded. After this set's clean-clone
check and box suite pass on the candidate and the candidate is promoted, `../l3r5/apply_l3r5_accept.py --supersede`
files the acceptance against the promoted revision, with the content manifest the amendment added (L3-R04); the old
record is kept byte for byte in `baseline_acceptance_history`. The results are added below when they exist.
