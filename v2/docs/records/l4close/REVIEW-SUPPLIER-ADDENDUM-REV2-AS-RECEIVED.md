# MeshSat supplier addendum revision 2: focused review

Date: 4 October 2026, Europe/Amsterdam  
Reviewed: addendum revision 2 dated 12:50, quotation draft (7), their checksum companions, the reattached supplier ZIP and the supplied milestone update.

## Decision

**READY for an initial supplier engineering quotation. L4-RD02 and L4-RD03 are CLOSED as documentation findings. Power-design closure and fabrication release remain BLOCKED.**

The requested corrections are now in the delivered files. The tested ZIP is unchanged. A small residual current-figure inconsistency should be corrected in the covering material, but it does not justify delaying supplier engagement, rebuilding the archive or rerunning the engineering suite.

## Verification

| Item | Observed result |
|---|---|
| ZIP | 12,894,538 bytes; byte-identical by SHA-256 to the previously reviewed archive |
| ZIP SHA-256 | `29ed399ae8f7cb29801b9f6080725cc44cf06957430b8642440faf032e76cb7d` |
| Addendum | 12,180 bytes; changed from the prior delivery |
| Addendum SHA-256 | `6c337e1dbd184f39bde077bb99f32cddd7c0ef57c8afeede856d7223c3701156` |
| Companion files | ZIP size, ZIP checksum and addendum checksum match the supplied files |
| Quotation | Names revision 2 and the correct addendum checksum; ZIP filename, size, checksum and revision remain consistent |

I compared the revised documents with their predecessors and read the changed passages in context. The archive's prior integrity review remains applicable because its hash is unchanged. No full suite, fresh electrical solver, circuit generation or physical test was run for this editorial reassessment.

## Findings disposition

| Finding | Disposition | Evidence |
|---|---|---|
| L4-RD01: superseded fan direction, nonexistent package branch paths and understated Layer 5 delivery | CLOSED, correction retained | The dated addendum still explicitly overrides the obsolete entry-page rows and distinguishes the tested baseline from later drafts. |
| L4-RD02: withdrawn 16.1 V floor still presented as current | CLOSED | Addendum line 37 withdraws it, preserves REQ-018's 15.5 V acceptance threshold, leaves F01 OPEN and labels FAN_OK conditional/unimplemented. Line 55 likewise keeps FW-A05 at 15.5 V. The 15.374 V calculation is explicitly a design result, not a new requirement. |
| L4-RD03: gitignored evidence described as obtainable through a clone | CLOSED as an access-description correction | Lines 21–22 separate committed-but-omitted files from external evidence, say the latter is not supplied by a clone, and offer the evidence archive on request. Actual delivery of that archive and public availability of omitted committed files were not independently verified here. |

**L4-RD04 — P2, confirmed minor current-state inconsistency, high confidence.** Addendum line 43 still says I-03 is 7.181 A against 7.096 A and is “unchanged.” Line 47 gives the newer result as 7.472 A against 7.0957 A. Update the former to the current reported case, or clearly identify it as an earlier case. Both rows correctly leave the defect open; this is not a new electrical finding. If the addendum changes, refresh its checksum and the quotation reference together. No archive replacement or electrical rerun is warranted for this correction.

## What the new engineering information establishes

The reported protection work has responded to the repeated-heating question: the addendum now selects LM5069-1 latch-off, rejects LM5069-2 automatic retry, and adds a temperature-dependent restart inhibit. TI's datasheet confirms the distinction between those two device variants. This is a concrete change in the reported design direction.

However, the supplied package still does not contain the new breaker calculation, restart-inhibit design or its review records. I have not reproduced the claimed overheating, trip band, 1.29 ms clearance or restart temperature. The addendum properly labels these as later, unimplemented candidates. Rebinding E11-37 to three battery FETs updates the qualification scope; it does not close that qualification.

Primary reference checked: [TI LM5069 datasheet, description and section 5](https://www.ti.com/lit/ds/symlink/lm5069.pdf), which identifies `-1` as latch-off and `-2` as automatic retry. This source confirms device behavior, not the adequacy of MeshSat's selected circuit.

The current record still identifies F01/FAN_OK thermal feasibility, I-03, DD-3, DD-5, B-R2 and E11-37 as open. The previous focused R-213 coverage questions remain applicable; this delivery contains no new thermal proof answering them.

## Milestones and next action

- **Set 29 at 18:00–19:30 CEST:** an estimated integration/promotion milestone. It does not establish Layer 4 completion or power-design closure.
- **B-R2 at 17:00–19:00 CEST:** an estimated correction and check of that particular draft defect, followed by set 30. It does not close the other power issues.
- **Supplier delta this evening:** the useful next technical-review input, provided it includes the actual fan/breaker drafts, calculations, verdicts and proposed C4/E procedures from named commits.

The reported freeze, targeted-run and box-pass durations provide a basis for integration scheduling. The excerpt does not establish remaining author time or test outcomes, so these remain forecasts rather than verified completion dates.

Supplier engagement need not wait for those milestones. After filling the contact placeholders and removing owner-only notes, the quotation can request the existing phased engineering scope. Vendor clarification, cell sourcing and T-H1 procurement can be assigned and costed within that engagement; no purchase or external message is authorized by this review. Fabricator stackup feasibility and cost information should inform the eventual copper choice.

Both Vast instances are reported stopped with their disks retained, consistent with the agreed policy. Their quoted storage rates total about $1.68 per day. No new infrastructure change is needed for this review.

Continue the existing work. This reassessment credits the document corrections and a reported change in protection strategy; it does not credit another completed layer or accept the new circuit numerically.
