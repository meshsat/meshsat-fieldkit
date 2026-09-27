# Reassessment of handover H3's release companions, 28 September 2026

<!-- Saved on 28 September 2026 as the owner pasted it (MESHSAT-1357): the outside reviewer's addendum to the independent review of H3 of 27 September (v2/docs/reviews/2026-09-27-h3-independent-review.md), written after the finalized release record and the two fresh check records were supplied. The reviewer's own title is kept as the first heading below. 7 en dashes are written as "to" and 2 curly quotation marks as straight ones (the repository's no-dash rule); every other word is as pasted. Decision: READY for a partial handover of the completed definition baselines with the listed errata; H3-03 closed; H3-01 and H3-02 open and acknowledged; layout and fabrication blocked. It is executed as the earlier reviews were: its three corrections are carried into the set 6 integration (S-88 to S-91 already record two of them) and its five directions into the execution plan. -->

# MeshSat H3: release-companion reassessment

28 September 2026, Europe/Amsterdam. Addendum to the independent H3 review of 27 September.

## Decision

**READY for partial handover of the completed definition baselines, with the listed errata.** The supplied finalized release note and two fresh check records close H3-03, the missing release-documentation finding. Layers 1 to 3 remain credited within their recorded acceptance scope: product definition, concept of operations and requirements. Another engineer can receive this bundle and continue without recovering the previous conversation.

**Layout and fabrication remain BLOCKED.** H3 is the same design snapshot previously reviewed, with zero boards ready for layout. Layers 4 to 9 remain incomplete. Set 6 and the newer circuit changes described in the progress message are outside this archive; this submission does not independently demonstrate their integration or correctness.

The useful advance is release assurance and transferability. It is not another completed engineering layer or an increase in verified PCB completion. Three completed definition layers do not represent one-third of the project's engineering effort.

## What I verified this time

| Check | Result |
|---|---|
| Newly supplied H3 ZIP versus the previously reviewed H3 ZIP | Byte-identical by SHA-256 and size: 52,187,825 bytes |
| Supplied ZIP checksum | Matches |
| Manifest sizes and SHA-256 values | All 2,274 rows match the archive |
| Git blob hashes | All 2,271 applicable entries match |
| New external manifest versus archive manifest | Byte-identical |
| Archive entries outside the manifest | Only MANIFEST.tsv itself, as expected |
| COMPANIONS.sha256 | All four companion documents match |
| Fresh checks' recorded original-body hashes | Both match after excluding the filing wrapper |
| Attached copy of my previous review | Meaning preserved; filing comment and disclosed punctuation substitutions only |
| Finalized release note | Identifies this exact archive and source commit, supplies suite results, records both fresh checks and carries the known defects |
| Selected new findings | Confirmed E's obsolete connector reference against the packaged netlist; confirmed CON-010 remains FAIL and has no waits_on field |

Archive SHA-256: `6922a96d732442e99a65d8db3f0734378bd7ea636894fca283a4b3ca424dd07a`.

Source commit: `75ad6ee5bc98d7213b9a61d1f64cfa7ea19cc669`.

I read the finalized release note, coherence check, usability check and previous review. This was a focused reassessment. I did not repeat the earlier checker fixtures or calculations on unchanged code, run KiCad, rerun the full suite, inspect live worker branches, or independently establish public publication of the companion files.

The supplied usability check reports successful representative calculation and board-P regeneration, and a ZIP-only suite result of 1,957 passed, 20 failed and 23 skipped. The finalized release note reports 1,998 passed, zero failed and two skipped on the source checkout with KiCad and history. These are different execution environments and dependency sets. The documents explicitly explain the ZIP-only failures; they must not be relabelled as passes. I verified the supplied records and their identity, not the remote executions themselves.

## Closure of the previous findings

| Finding | Status | Evidence and remaining work |
|---|---|---|
| H3-03: missing final release note and fresh-check records | **CLOSED for the evidence-delivery requirement** | RELEASE-H3.md is completed and both check records identify the exact archive/source. No archive rebuild is needed. |
| H3-01: REL-001 silently omits parts and accepts a missing netlist | **OPEN in H3; acknowledged** | Identical checker bytes remain. Release erratum h records the defect and proposed repair. Assignment to a worker is not proof of closure. |
| H3-02: A's external-port declaration omits its actual VIN_RAW entry | **OPEN in H3; acknowledged** | Identical declaration remains. Erratum f is extended to explain that the apparent PASS is limited. A corrected declaration, coverage regression and refreshed result are still needed. |
| Preserve and deliver completed Layers 1 to 3 | **ACHIEVED within their documented scope** | Definition baselines, editable sources, acceptance records, continuation instructions and the release companions are available together. |
| Complete Layers 4 to 9 / authorize layout | **NOT ACHIEVED by this submission** | Neither the design nor its layout-entry status changed. |

## Corrections to carry into the next engineering candidate

### 1. Board E's layout instructions name the wrong power connection

**P1 for use in layout; confirmed documentation defect.** The usability check's finding 4 and RELEASE-H3 erratum i identify this correctly. In `v2/docs/layout-constraints/E.md:73`, VIN_RAW still exits through J_BLK; line 272 also names J_BLK among the relevant exposed 36 V locations. The packaged netlist instead places `/VIN_RAW` on `P_VR` pin 1 (`v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net:3895 to 3908`).

The current input hashes and correct current calculation do not make the connector labels current. The risk is applying layout constraints at the wrong physical connection. This is not proof that a fabricated board has inadequate clearance; no such board is established here.

**Fix and acceptance:** update E's affected placement, protection and clearance references against its actual netlist and the mating interface. Review all related A/E/E5 interface references affected by the same pin migration. Before layout entry, check that each constrained connector/pin/net exists in the selected design revision. Record which physical connection each constraint covers, rather than relying only on a document-wide input hash.

### 2. Requirements completion retains a traceability exception

**P2 for the accepted definition handover; confirmed traceability gap.** Both fresh checks report 24 of 58 open items absent from all records' `waits_on` fields. Some open items concern process or packaging, so a missing link does not automatically constitute an engineering dependency. However, S-64 affects CON-010's result, and the packaged CON-010 has no `waits_on` field. Its FAIL remains visible.

Layer 3 acceptance item 3.15 says "MET in substance" and explicitly carries this as a minor exception. Therefore retain the accepted requirements baseline, but describe it as **complete with documented minor corrections**, not as literally free of every acceptance exception.

**Fix and acceptance:** classify the unlinked items, add actual requirement dependencies such as S-64, and explicitly dispose of process-only items. Verify that every unresolved item capable of changing a requirement verdict is linked or has a justified disposition. Update the affected acceptance row and count without rewriting settled requirements or reopening unrelated layers.

### 3. Current status must show known coverage limitations

**P2 for handover clarity, alongside the existing P1 checker defects.** The release note now discloses the issues, but the immutable archive still contains unqualified REL-001 and A TRN-001 PASS statements at some points of use. CURRENT-EVIDENCE also retains a fixed sentence saying the requirements baseline is open.

**Fix and acceptance:** in the next candidate, derive baseline status from the registry and propagate coverage limitations to the generated views. Once checker/declaration fixes land, regenerate affected readings on the integrated revision. A warning in the release note is useful disclosure; it is not a repaired checker.

## Direction for the next Claude session

1. Preserve H3 and distribute its finalized companion documents with it. Keep Layers 1 to 3 credited. Do not restart a general review of those baselines.
2. Finish Set 6 integration and verify the actual integrated revision. Distinguish circuit changes, declaration corrections, checker fixes and evidence refreshes in the closure record.
3. Close H3-01 and H3-02 with targeted coverage and missing-input regressions; correct E's layout constraints before its layout entry. Apply the bounded requirements-link correction alongside that work.
4. Continue the existing Layer 4 to 9 engineering streams. Package each genuinely completed scope when its dependencies and acceptance criteria are satisfied; unrelated unfinished boards need not hold that handover.
5. Make the next release add accepted engineering work. Avoid another documentation-only release unless a concrete handover defect requires it.

The boundary to preserve is explicit: H3 gives the owner transferable product intent, operating scenarios and requirements. It also gives useful but unfinished implementation material. It does not yet give a complete, reviewed pre-layout design package.

## Supplied evidence

- RELEASE-H3.md: package table, fresh checks, errata f through m.
- H3-COHERENCE-CHECK.md: sections 2, 6 and 9; particularly m6 and m11.
- H3-USABILITY-CHECK.md: sections 2 and 5; particularly findings 3, 4 and 6.
- H3.MANIFEST(1).tsv, H3.zip(1).sha256 and COMPANIONS.sha256.
- 2026-09-27-h3-independent-review.md, compared with the original locally delivered review.

The supplied check records identify themselves as AI checks. Neither their conclusions nor this reassessment constitute qualified electrical sign-off or physical verification.
