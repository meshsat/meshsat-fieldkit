# MeshSat V2 — supplier handover review

Date: 3 October 2026  
Scope: engineering correctness, handover usability, layer progression and execution efficiency.

## Verdict

**The package is useful for an initial supplier engineering discussion and quotation. Power-design closure and fabrication release remain blocked.** The provisional label is appropriate. The supplier does not need a falsely “completed” design before assessing and quoting the work needed to finish it.

This is tangible progress toward the intended handover: editable designs, calculations, a layer index, explicit defects, proposed experiments and separately labelled unfinished branches are now together. However, the package still contains genuine unresolved circuit problems as well as missing qualification evidence. These need different actions.

I found three bounded handover corrections. They do not require another general circuit review or a restart of Layer 3. Correct them in a small delta, or supply explicit errata with the provisional package. Initial supplier discussions need not wait for set 27's full suite.

## What I checked

Reviewed the uploaded quotation draft and `MESHSAT-SUPPLIER-HANDOVER-PROVISIONAL-44353098.zip`, including its entry page, source index, layer table, thermal procedure, selected model code, downstream register and specimen-transfer rules.

- ZIP: 16,105,276 bytes. SHA-256 matches the companion file and quotation draft: `35d97170e53121a4f77f4a7691d6e37cce3e169fa52b811c7bfb68fbb6fd5c22`.
- Extracted: 613 files; all 612 listed file hashes match the manifest. The manifest itself is the remaining file.
- Parsed 120 Python files: no syntax errors.
- The two copies of `SUPPLIER-HANDOVER.md` are identical.
- Verified that the extracted package is not a Git checkout; a read-only Git root probe returns exit 128.

**Limits:** I did not execute the numerical models, generate schematics, run the project suite or independently recompute the electrical and thermal results. File hashes establish archive integrity, not that every file came from the stated Git revision. This is a bounded handover review, not electrical approval or a fresh review of every layer.

## Findings

### L4-SH01 — P1: thermal acceptance summary puts uncertainty on the wrong side

**Confirmed documentation defect.** `SUPPLIER-HANDOVER.md:111`, row P6, says the mode's reading must be “at or over its line less its uncertainty.” That lowers the threshold as uncertainty grows.

The detailed procedure says the opposite: `v2/docs/records/l4e12/T-H1-PROCEDURE-DRAFT.md:149–152` requires the reading **less its expanded uncertainty** to meet the required conductance.

Use this unambiguous condition in the summary:

```text
G_measured − U_G ≥ G_required
```

Here `U_G` is the expanded uncertainty expressed in W/K. Use the detailed procedure's mode-specific thresholds where uncertainty is calculated as a percentage of the reading.

For example, with a 2.0 W/K requirement, a 1.9 W/K reading and 0.1 W/K uncertainty, the current summary could admit the result; the required lower bound is only 1.8 W/K and does not pass.

**Correction:** update the source entry page and its packaged copy to match the detailed procedure. Check the text and a simple pass/fail example. This finding does not require recomputing the thermal model or changing the procedure's numerical thresholds.

### L4-SH02 — P2: replay instructions omit required Git context

**Confirmed reproducibility-instruction gap.** Section 7 of the entry page presents a Python invocation and package dependencies as the route to reproducing each record. Section 9 separately says Git history is omitted, but does not connect that omission to the replay commands.

For example, `v2/docs/records/l4e9/l4e9_power_path.py:52` requires `git rev-parse --show-toplevel` at import time. Lines 250 and 257 can read historical files with `git show`. That script cannot run directly from this plain ZIP extraction. The package's older `REGENERATE.md` also contains instructions for earlier handover/source formats; it is not a complete recipe for this provisional export.

**Correction:** provide a short, package-specific distinction:

1. What can be reviewed directly from the ZIP.
2. Which calculations require a checkout at an exact full commit, historical objects and separately obtained maker documents.
3. How the recipient obtains those inputs, including any unpromoted branch needed for this snapshot.

Verify one representative replay in that documented environment. If access to the unpromoted revision is unavailable, mark replay pending and provide the relevant inputs separately when ready. Do not rebuild a gigabyte archive merely to make an initial quotation possible, and do not claim offline replay has passed when it has not.

### L4-SH03 — P2: the headline overstates defect closure

**Confirmed status inconsistency.** Section 5 begins with “known defects addressed in drafts; feasibility conditions remain open.” Its own table then identifies:

- P1: the latest model predicts −0.3021 V at the solar sense pins against the record's −0.3 V absolute limit; a satisfactory protection arrangement remains unresolved.
- P2: normal-operation sensing exceeds the stated operating range, with an unvalidated clipping model used to estimate the effect.
- P8: the existing fan supply does not match the selected fans; the correction is still owed.

These are not all missing bench evidence for an otherwise completed design. P1 and P2 require a supported circuit correction; P8 requires an actual supply change and verification of its consequences.

**Replace the headline with:**

> Selected power-architecture candidate. Known design defects and qualification gaps remain open. Changes are drafts, not an implemented or qualified circuit. Power-design closure and fabrication release are blocked.

Keep Astra's NOT YET and the coordinator's later checks separately attributed. Promotion of set 27 may establish a controlled engineering baseline; it must not imply that the design or outstanding findings have passed independent review.

## Prior review items

| Item | Disposition in this package | What remains |
|---|---|---|
| L4-QR01: coupon thermal equivalence and sample scope | Documentation materially corrected. L4-E11 section 17d explicitly withdraws the copper-area-only and layout-independent claims, and names specimen, lot, boundaries, uncertainty and retest triggers. | A supplier engineer must assess the proposed transfer rules and test setup. This review does not certify the thermal-equivalence argument or qualify the components. |
| L4-QR02: R-167 blocks the proposed pack's adoption | Corrected. `DOWNSTREAM-REGISTER.md:255` limits the dependency to adopting the Saft proposal and the mechanical work that depends on it. | The mock-up remains outstanding; unrelated baseline work can proceed. |
| Solar guard B6 / D-10 | Open and more clearly exposed. The package withdraws the earlier passing-inductance conclusion. | An engineering correction and subsequent verification, not a status relabel. |
| Previously missing Layer 5 handover material | `v2/docs/records/l4e9/LAYER5-HANDOVER.md` is present. Separate Layer 5–8 branch snapshots and diffs are included. | Integration and acceptance of those deliverables. Their inclusion is not proof that the layers are complete. |

The reported worsening of B6 is a changed model result, not an observation of physical hardware becoming worse. It is still an important reason to keep the design gate blocked.

## Quotation request

**The draft asks for the right kind of service:** engineering review and correction, controlled prototype qualification, then design completion. It explicitly asks about capabilities, exclusions and partners, so it does not assume a PCB manufacturer automatically supplies all the necessary engineering.

Make these small changes before sending:

- Add a plain sentence to the introduction: “The design and its reviews to date were AI-assisted; no hardware engineer has independently reviewed the complete design.” The entry page already discloses this.
- Clarify that Phase 1/2 includes the circuit, layout and fixture work needed to create suitable test specimens. Otherwise, placing all application of circuit drafts in Phase 3 creates a circular dependency with Phase 2 testing.
- Describe the fourteen experiments as **proposed procedures for the supplier to review and agree**, not approved instructions that must be executed unchanged.
- Ask Phase 3 to include final-revision verification and any affected qualification tests that must be repeated after changes. Coupon results do not automatically qualify a changed production layout.
- Permit indicative Phase 2/3 estimates with assumptions, refined after Phase 1. Ask for a bounded initial engineering scope and named responsible engineer.

Suggested addition:

> Please include the design and fixture work needed to build suitable test specimens in Phases 1–2. Review and agree the proposed test procedures before execution. Phase 3 should include verification of the final revision and repetition of affected tests where design changes invalidate earlier evidence. Estimates for later phases may be conditional on Phase 1 findings, with those assumptions stated explicitly.

The owner still chooses when to send the request and whether to accept a quote. No supplier capability or commitment is established by this package. Nothing has been sent as part of this review.

## Execution efficiency and layer continuation

The reported 50-minute numerical regeneration for two sentence corrections is avoidable coupling. `l4e7_stage_settings.py:4686–4688` calls `compute()` and then `render(R)` on every invocation, including changes that affect only presentation. I confirmed that structure, not the reported runtime.

Let the current healthy run finish. For subsequent wording-only changes, introduce the smallest separation between validated numerical results and rendering. Retained results must be bound to the numerical inputs, equations/solver version and tolerance assumptions. A numerical change invalidates them; a presentation-only change need not rerun the solver. Preserve the atomic-output and provenance checks. Do not hand-edit generated output or build a new orchestration framework before delivering the handover.

Continue by actual dependency:

| Work | Next useful action | What must not be claimed |
|---|---|---|
| Set 27 | Finish the named residue corrections, classify real defects separately from missing evidence, run the required integration gate once on the frozen candidate and publish the delta. | Promotion does not close power-design approval. |
| Layers 5–7 | Integrate and finish interfaces, component evidence and mechanical definitions that have stable inputs. Carry unresolved power-dependent choices explicitly. | First passes or branch snapshots are not 100% completion. |
| Layer 8 | Continue supported, reversible circuit work and composition checks. Obtain an engineering correction for the solar sense/guard problem before releasing that part of the design. | A draft or composition proof is not an electrically qualified implementation. |
| Layers 9–11 | Prepare constraints and release tooling; perform analysis and layout on boards whose actual entry dependencies pass. | An unresolved material power defect cannot be passed through to fabrication by calling it a downstream test. |
| Firmware and test documentation | Continue work against stable contracts and prepare supplier-executable procedures. | Hardware verification remains unperformed until actual results exist. |

The practical next milestone is **a supplier-ready engineering baseline with explicit unfinished work, followed by a supplier-agreed correction and qualification scope**. It is achievable before every PCB is finished. The immediate remedies here are small: correct the thermal summary, make replay instructions accurate and state the remaining design defects plainly. None justifies another broad review loop.
