# Integration sets 20 and 21 (MESHSAT-1357, branch `fnd/int21`, 1 October 2026): Layer 4's source control and fault handling

Prototype design: nothing is bought, built or measured. The integrating session's records, from main `e3c99df8`.

| Step | Commit | What it did |
|---|---|---|
| 1 | `05e8f912` | set 20: L4-E4's component values marked PROVISIONAL by the owner's instruction of 1 October 2026; the draft apply scripts refuse to write board A's generator until `records/l4e4/RELEASE.md` reads "released: yes" and names an accepted check of the source-control and the fault-handling decision (`tests/test_l4e4_provisional.py`). Box suite 2397 passed, 0 failed, 205 of 205; promoted |
| 2 | `f8514c0b` | the independent reassessment of the power replay companion filed as received (`records/l4e/REVIEW-POWER-REPLAY-REASSESSMENT-AS-RECEIVED.md`): L4-R03 CLOSED; PR-01 fixed in the coordinator's tools; promoted |
| 3 | `7d9d9753` | merge of `fnd/l4e5` at `0e7e7f11`: L4-E5 source control, H3 (a hardware VIN_RAW line on U3's ILIM_HIZ pin with a knee below 9 V, board E's tracker ceiling raised, firmware IIN_HOST constant at 4.70 A); the collaborator's check and recheck not accepted, the coordinator's check 3 accepted |
| 4 | `74416392` | merge of `fnd/l4e6` at `843f48c1`: L4-E6 fault handling (R12 12 mOhm and C147 330 pF bound L1 and the FETs by U2's cycle-by-cycle limit, hiccup off, the bulk bank to be re-sized); the collaborator's check accepted, the coordinator's check 2 on its minors |
| 5 | this commit | this record |

**L4-E4 stays PROVISIONAL.** Both decisions now support L4-E4's values (IIN_HOST 4.70 A, R11 8 mOhm subject to bench V-A07,
R138 5 mOhm), but the circuit round they belong to is not complete: B-4, the VBUS20 bank's re-size, is open, and the dense
ripple analysis it needs (`drafts/scripts/ripple_dense.py`, cited by `gen_sch_a.py` near line 706) is in neither the tree
nor its history, only described there and in recovered transcripts. The release record is filed only when the round's
drafts (R11, R138, R12, C147, the ILIM_HIZ network, board E's R10, C26 and C27, the bank) are complete and consistent,
because the order constraint of L4-E6 forbids R12 without L4-E5's line and an R11 change without IIN_HOST's rule.
