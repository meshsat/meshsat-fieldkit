# Integration set 22 (MESHSAT-1357, branch `fnd/int22`, 1 October 2026): the unified independent review of the requirements amendment

Prototype design: nothing is bought, built or measured. The integrating session's records, from main `548ad56a`.

The owner relayed the independent reviewer's unified review of the Layer 3 amendment
(`v2/docs/records/l3am/REVIEW-UNIFIED-AS-RECEIVED.md`, sha256 `1a8d728ad6fabf2d...`). It read the compact package
`MESHSAT-L3-AMENDMENT-f8514c0b` and reproduced it offline in a second environment (Python 3.12.14, Git 2.51.1; 140 passed,
0 failed, 0 skipped; `REPRODUCE: PASS`). **Decision: READY as an accepted Layer 3 requirements baseline for Layer 4 work
and engineering handover; L3-R01 to L3-R05 CLOSED against their stated criteria; no Layer 3 restart and no owner decision
required.** The acceptance at `3b4b92cf` and every file it binds are unchanged by this set.

| Step | Commit | What it did |
|---|---|---|
| 1 | `01d25c62` | the review filed byte for byte (its own dash characters kept), with a row in `records/l3am/README.md` |
| 2 | `6e5a71ba` | **L3-N01** (P2, nonblocking, the checking tool): `records/l3am/checks/verify_l3am.py`'s closing helper `ver()` read only None, True or a tuple as success, while `apply_l3am_findings_closed.verify` returns the reviewed revision, so it read the valid check as refused and its one negative probe could not fail. Fixed: a 40-hex revision return is success; a positive case (the newest accepted check, check-l3am-4, returns the revision its third line names) and the probe's own sensitivity added (19 rows, from 16). `l3n01/`: the reproduction on the old helper (`reproduction.out`: the verifier returned `8146b4cc...`, the old helper read it and a wrongly accepting verifier both as False), the old run (`verify_l3am-before.out`, 16 of 16), and `l3n01_mutation.py`, the review's acceptance check: a copy of the script whose verifier accepts any record exits 1 with exactly the pre-amendment probe WRONG. `verify_l3am.py` is not among the amendment's bound files (`l3amlib.AMENDMENT_FILES`), so the findings' closing check still verifies |
| 3 | `3da8c711` | **the review's item 3, the energy-evidence pointer** (`apply_energy_pointer.py`): REQ-072's notes name L4-E2's checked result on REQ-016's retained 100 W window (`records/l4e/L4-ENERGY-ARCHITECTURE.md`, its figures in `l4e_replay.out`, the coordinator's `checks/check-l4e2-3.md`, the replay companion reproduced offline by the owner's reviewer) and `LAYER-STATUS.md`'s layer 3 gains one paragraph. The historical results of proposal P-03's array keep their label. Not as an evidence entry: REQ-072's last evidence entry is its baseline evidence, which `test_l3r5` (a file the amendment's closure binds) reads, and the notes call it "this record's latest evidence entry"; a first version that appended an entry failed that test and was dropped before any push (kept as the local branch `fnd/int22-pointer-v1`). The script refuses unless the registry differs only in REQ-072's notes, the requirements digest is unchanged and the acceptance validates before and after. `l3r2.yaml`'s `solar_case` and the three Layer 3 pages keep naming the result pending, as accepted: they are the acceptance's policy and its views, and changing them would need the baseline accepted again. `REQUIREMENTS-L3-R2.md` changes only in the registry's sha |
| 4 | this commit | this record |

**Not changed:** `l3r2.yaml`, `render_l3r2.py`, the amendment's bound files, `check-l3am-4.md` (it records the 16 of 16 it ran
at `8146b4cc`), the requirements' normative content. The review's items 1, 2 and 4 are standing practice: Layer 4
continues, the controlling documents are handed over together, and REQ-042's and REQ-016's verification stays downstream.

**Gates on the runner, at `3da8c711`:** the registry 145 records and 59 rules, 0 errors and 0 warnings; every page current
(`render_l3r2 --check` 3 of 3, `rules_render` 16 documents and the trace, `decisions_render`, the re-issue and its passage
map); the decision-chain dry run byte for byte; `verify_l3am` 19 of 19, `verify_acceptance` 18 of 18, `l3n01_mutation`
PASS; the Layer 3 modules with hygiene and the Layer 4 modules 190 passed, 0 failed, 0 skipped; the render order twice with
no page moved. The box suite on the set's tip is the promotion gate.
