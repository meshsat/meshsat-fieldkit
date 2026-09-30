<!-- ABRIDGED by the coordinating session (1 October 2026). Verbatim: the header, the verdict and its table, the findings
table, each finding's smallest correction and closure, the bounded next action and the status wording. Condensed: the
reviewer's section on what was independently checked, the tables inside L3-R03 and L3-R04, the explanation paragraphs of
L3-R01 and L3-R05, the sources' web links (Sensirion SGP41 datasheet; Littelfuse SMCJ datasheet), and the section on items
that should not restart Layer 3. The full text was relayed by the owner to the coordinating session. The review's own
dash characters are kept as written. -->

# MeshSat V2 — independent Layer 3 engineering review

**Reviewed baseline:** `b4b199d0ceee6d7a632b85090fbf3bf95a602758`  
**Acceptance revision:** `b45d1705c816b5f9bc6bf9d14f4409545047ebd6`  
**Input:** `MESHSAT-LAYER3-REVIEW-b45d1705.zip`, including its post-acceptance solar addendum.  
**Scope:** requirements quality, engineering consistency, evidence, acceptance logic and handover reproducibility. This is not a security audit or a fabrication approval.

## Verdict

**A substantial, accepted requirements baseline exists. I do not endorse an unqualified “100% complete and correct” claim for this package.** The requirements are useful enough for Layer 4 and for an electronics engineer to review, but there are specific acceptance-criteria defects and an incomplete reproduction package.

The earlier statement that Layer 3 was complete relied on Claude’s status report. This review examines the supplied files and code directly. The distinction matters: recorded acceptance is demonstrable; universal correctness is not.

**Keep Layer 4 running.** Correct the items below through a bounded Layer 3 amendment and an export repair. These findings do not justify repeating the battery trade-off discussion, reopening the whole foundation, or waiting for hardware measurements before doing architecture work.

| Question | Independent conclusion |
|---|---|
| Is there a real requirements baseline and acceptance record? | Yes. The supplied revisions, registry, rulings, reviews and acceptance record are consistent about which baseline was accepted. |
| Do the principal current owner instructions appear correctly? | Yes: internal storage, battery and solar, HF and tablet retained, optional tablet charging, and 48–72 hours as an objective. |
| Does the successful full-suite claim have supporting evidence? | Yes. Every declared test is accounted for in the supplied candidate log. I audited that log; I did not rerun the full suite. |
| Are all acceptance conditions adequate? | No. REQ-042 contains a demonstrably insufficient completion condition. REQ-016 also needs clearer separation of operating-window verification from protection verification. |
| Can this ZIP reproduce closure by itself? | No. Four referenced files and required Git history are absent. A restored copy fails validation and cannot render the handover. |
| Are the design, runtime, thermal performance or boards verified? | No. The baseline generally states those limitations honestly. |

## Prioritized findings

P1 means a correction is needed before presenting this as an unqualified, complete requirements handover. P2 means a bounded reliability or clarity improvement. Neither label below calls for restarting Layer 3.

| ID | Priority | Finding | Effect |
|---|---|---|---|
| L3-R01 | P1 | Solar-assisted headline uses an unapproved input configuration | The handover’s numerical baseline is not the retained REQ-016 configuration. |
| L3-R02 | P1 | Hydrogen-sensing acceptance can be satisfied by naming a part | A component-selection milestone substitutes for the required detection-and-shutdown outcome. |
| L3-R03 | P1 for handover | Export cannot reproduce the requirements validation | Independent review cannot rerun the claimed closure from this ZIP alone. |
| L3-R04 | P2 | Acceptance verification does not bind approval to reviewed content | Later changes or a wrong revision can retain a superficially valid acceptance record. |
| L3-R05 | P2 | Solar protection wording relies on breakdown onset | The stated check does not establish protected-node voltage under the relevant disturbance. |

### L3-R01 — the accepted solar-assisted headline has the wrong configuration basis

`v2/docs/handover/layer3/REQUIREMENTS-L3-R2.md:53` quotes solar-assisted stopping times and energy shortfalls without identifying the array/stage used. The source output, `v2/docs/records/l3batt/runtime.out:27–32`, explicitly uses **400 Wp in 2S2P into a 200 W stage**. Retained `REQ-016` specifies **at most 100 W into the stage, 17.6 V regulation and at most 25 V cold open-circuit voltage** (`pcb_requirements.yaml:7679–7689`).

**Smallest correction:** label the existing numbers explicitly as historical proposal P-03 results at every current headline that uses them. State that the retained-window result awaits the existing Layer 4 replay, then link that result when available. Keep the original evidence immutable. Do not describe the 400 Wp/200 W run as the current approved configuration.

**Closure:** the current summary and machine-readable case identify the same pack, load profile, array, voltage window and stage limit. No new owner decision is needed to correct this attribution. A change to the retained input requirement would still need its normal authority.

### L3-R02 — REQ-042’s hydrogen acceptance is not an outcome test

`v2/ecad/tools/pcb_requirements.yaml:12904–12912` requires water, hydrogen or VOC detection to raise an alarm and shut the pack down, but concludes that the hydrogen portion is met once `S-49` names its part. `S-49`, at lines 3139–3146, is explicitly a sensor-selection task or a request for manufacturer confirmation.

The VOC portion specifies a shutdown after crossing a bring-up threshold, but does not define a repeatable gas stimulus or a bounded method for choosing that threshold. Thus it tests the response to a selected reading more clearly than it tests the required detection behaviour.

**Smallest correction:** make S-49 close component selection only. Give REQ-042 a controlled end-to-end verification specification: stimulus and threshold basis, applicable environmental and power states, timing start point, alarm, opening of both FETs and persistence until service. Allocate any remaining detection-limit derivation to the responsible engineering layer explicitly; do not mark functional compliance when a part is selected.

**Closure:** the requirement cannot read satisfied solely because S-49 is closed, and its eventual test can distinguish a sensor that merely exists from a working detection-and-shutdown function. Physical testing remains a downstream obligation.

### L3-R03 — the review export is incomplete for standalone replay

Validation returned **five errors and 33 warnings**. The five errors refer to four files absent from the entire archive: `v2/vendor/st/st-stm32h743xi-datasheet-rev11.pdf` (CON-017), `v2/vendor/st/st-rm0433-rev8.pdf` (CON-017), `v2/vendor/rockblock/rb9704-sch-2B1.pdf` (REQ-071 and FEA-002), `v2/cad/pack_4s.py` (CFL-006). The renderer refused on the same validation errors. The warnings concern historical commits that the export cannot resolve. `basis_binding.py` reads earlier checked versions with `git show`.

**Smallest correction:** add the four exact, hash-matching files and a documented way to resolve the required source revisions. Prefer a bounded dependency export or the necessary Git objects over requiring an engineer to reconstruct the working environment. Do not invent replacement commit identities or bypass the binding checks.

**Closure:** unpack into a clean directory and successfully run the advertised Layer 3 reproduction checks with every dependency either supplied or explicitly obtained and verified. Distinguish a truly standalone package from a package that requires a repository clone.

### L3-R04 — acceptance is checked as metadata, not as a binding to reviewed content

`render_l3r2.py:384–404`, `acceptance_ok()`, verifies the revision’s 40-hex syntax, authorization, evidence-path existence and the newest review’s recorded verdict/hash. It does not verify that the revision exists or that the current requirements are the content that was accepted. Read-only probes on in-memory copies: original data True; revision replaced with 40 zeroes True; revision replaced with 40 `a` characters True; REQ-016 statement changed to allow 500 W, old approval retained True.

**Smallest correction:** bind acceptance to a compact manifest of the reviewed requirements, owner brief, governing definition changes and applicable acceptance policy, plus the candidate revision. Verify that binding when rendering acceptance. Keep the acceptance record itself outside the content it hashes to avoid a circular hash.

**Closure:** a nonexistent/wrong revision and a material requirement change invalidate current acceptance; the unchanged accepted content remains valid when ordinary downstream implementation work changes unrelated files. Add focused positive and negative tests at this boundary.

### L3-R05 — REQ-016 needs to separate operating limits from protection proof

`pcb_requirements.yaml:7684–7686` names SMCJ28A and its 31.1 V conduction onset as being below the 35 V bulk capacitors. The generator repeats the explanation at `gen_sch_e.py:440–448` and places two 35 V capacitors on the protected node at line 479. The manufacturer specifies **31.1–34.4 V breakdown at 1 mA** and **45.4 V maximum clamping at 33.1 A** for SMCJ28A. Breakdown onset is not the maximum protected-node voltage. Existing evidence: the generator acknowledges the higher clamp voltage, and `DECISION-31-PROTECTION-TOPOLOGY.md:504–513` includes an ESD charge/capacitance analysis and a reversed-panel limitation; rule `TRN-001` requires actual clamping voltage to be assessed against protected-part limits.

**Smallest correction:** remove the implication that the breakdown comparison establishes protection. Keep the approved operating window, and explicitly trace protection acceptance to the applicable disturbance, source impedance/current, duration, tolerances and protected-node limit. Use the existing TRN-001 work; do not invent an unrelated qualification standard or silently adopt a larger input window.

**Closure:** distinguish the verified normal operating envelope, any bounded ESD result, and unresolved surge/overvoltage obligations. A part number alone must not close them.

## Items that should not restart Layer 3

Runtime arithmetic (107.9 Wh / 42.8 W = 2.521 h; 544.4 Wh / 42.825 W = 12.712 h) is correct; thermal requirements (D-29/D-36, FEA-008) are a defensible requirements-level disposition, but REQ-051's acceptance text and TEST-PLAN still describe the old cell-free deviations, so their next controlled issue should clearly separate diagnostic test IDs from final pack-fitted acceptance; definitions awaiting re-stamp are governed by D-38's change record (an external handover must include that amendment prominently, preferably with a consolidated reading copy); Astra attribution is accurate.

## Bounded next action for Claude and Astra

1. Correct the solar case labels immediately; link the existing Layer 4 replay when it is ready.
2. Fix REQ-042’s selection-versus-compliance criterion and clarify REQ-016’s protection criterion. Preserve the owner’s scope. Keep physical verification downstream.
3. Repair the export dependencies and bind acceptance to the reviewed content.
4. Have the independent checker review these changed claims and the binding tests once. Recheck changed sections after any correction; do not repeat a full battery study or review the entire project again without a concrete reason.
5. Run the relevant deterministic checks and any existing required integration gate on the actual amendment revision. Publish the amendment, a corrected review ZIP and a short dispositions table against L3-R01 to L3-R05.

For status reporting, use **“Layer 3 accepted baseline; independent review findings open”** until the amendment is checked. Keep that distinct from **“design compliance verified”** and **“fab-ready.”**
