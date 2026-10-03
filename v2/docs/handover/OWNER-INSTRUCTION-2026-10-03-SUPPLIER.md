# Owner instruction, 3 October 2026: the supplier engineering handover (an amendment to the running plan)

Received in the coordinating session on 3 October 2026, filed as received; it amends the plan of 2 October (`OWNER-INSTRUCTION-2026-10-02.md`) from this point.

## The covering note

Read the attached prompt and apply it as an amendment to the running plan. Preserve current workers, completed calculations and accepted baselines.

Continue set 27 and the ready subsequent layer deliverables. Prepare the supplier engineering handover and quotation request alongside that work. Do not make handover depend on physical tests that we are asking the supplier to perform.

Keep unresolved design and qualification conditions explicit. Proceed without restarting the planning cycle or waiting for another review from me.

## The amendment

# MeshSat: supplier engineering handover and autonomous layer completion

Apply this clarification to the running approved plan. Keep the current workers and valid calculations running; do not restart work or enter another planning cycle.

## 1. The actual situation

We have no in-house electronics engineer assigned to review or physically qualify this design. We intend to engage a supplier's engineers to do that work. NextPCB is our existing contact; Seeed is another possible provider. Neither should be assumed to have accepted the required engineering scope yet.

Our immediate target is a **supplier-ready engineering handover**. It must let their engineers understand the product, review and correct the design, finish outstanding layers, and construct and qualify appropriate prototypes. Physical qualification is part of the work we are asking them to undertake; completing it beforehand cannot be a prerequisite for approaching them.

Continue our own supported engineering work alongside that handover. Preserve Layers 1 to 3 and the current owner brief: battery and solar, no external battery, HF and tablet retained, the approved pack and solar rulings, and 48 to 72 hours as a stated design objective. Do not adopt a component proposal or change service requirements without the applicable authority.

## 2. Finish the recovery and set 27

Keep the two-worker limit and one author per branch. Finish L4-E7 round 5 and the GND-002/HOT-R1 composition work from their recovered state. Preserve successful regeneration and committed fixes. Integrate the remaining consolidation, QR01's evidence-transfer correction and QR02's pack-fit dependency.

Use the existing regeneration, targeted verification and promotion gates on the actual candidate. Retain Astra's original verdicts and label the coordinator's checks accurately. Promote a truthful, reviewable design candidate when its applicable gates pass; this does not declare power qualification or fabrication release complete.

## 3. Produce a handover that a supplier can act on

Curate the existing material into one concise entry document and a compact package containing:

- Product intent, accepted requirements, operating modes and constraints.
- Current architecture, power/heat budgets, interfaces, schematics, BOM and mechanical sources, each with its revision and maturity.
- A layer-by-layer index: completed deliverable, outstanding work, exact dependency and responsible party. Include unfinished layers explicitly.
- The remaining decision-critical power questions, each with its evidence, known failure or uncertainty, proposed correction or experiment, acceptance criterion and affected release.
- Test specimens, procedures, instrumentation requirements and the limits on transferring their results to the final kit.

Include editable sources and the small calculations needed to check the claims. Identify omitted material. Do not bundle full Git history or wait for the full seven-board design to become fabrication-ready. If set 27 is still integrating, issue a clearly labelled committed provisional snapshot and a later delta.

Prepare an unsent request for a phased engineering quotation:

1. **Design review and correction:** review the architecture, circuits, protection and thermal feasibility; return prioritised findings and corrected editable files or a scoped completion proposal.
2. **Prototype qualification:** select suitable evaluation hardware, test coupons or first prototypes; build fixtures, conduct the agreed tests, and return measurements, conditions, uncertainty and pass/fail results.
3. **Design completion and manufacturing release:** finish the contracted schematic, mechanical, layout and manufacturing work; return the revised sources and a release recommendation with remaining qualifications stated.

Ask the supplier to confirm a responsible engineering contact, capabilities, exclusions, deliverables, cost and schedule. Explicitly request electrical-design and qualification work beyond ordinary fabrication/assembly checks. If they cannot cover a task, ask them to identify that gap and any partner service; do not assume it is included. Sending requests and purchasing remain subject to existing authorisation.

## 4. Stop the power loop at the right boundary

Classify each remaining item in the existing register:

- **Known engineering defect:** fix it, or assign a specific design-correction task to the supplier. A future test does not erase it.
- **Physical uncertainty:** finish the executable test specification, identify what decision it settles, assign external execution, and continue unaffected work.
- **Uncertain design choice:** make one bounded comparison of qualifying the current choice versus a supported alternative that removes the dependency. Compare total effort, availability and effects on interfaces and service. Select within existing authority or present the smallest genuine owner decision.

Repeat analysis only when inputs, the diagnosis or the design change. Treat typical values and model assumptions according to their actual evidence. Sample measurements do not become universal component guarantees; coupon transfer requires justified equivalence. Keep the corrected connector-fault results and design-margin failures visible.

Prepare controlled prototype work under its own reviewed scope. Final-product release remains held where necessary. Do not require final qualification before permitting the evidence build that supplies it.

## 5. Continue the layers and deliver usable outputs

After set 27, dispatch the next ready set 28 task automatically. Prioritise the earliest unfinished layer and complete independent work when a specific external dependency blocks another item.

| Layer | Deliverable to finish or hand over |
|---|---|
| 4 | Whole-system architecture, coherent budgets and operating/fault behaviour, selected power candidate, remaining decisions and qualification route. Power alone is not the entire layer. |
| 5 | Consistent board/interface documents and HW/FW contract, including power, grounding, sequencing, SLOT_EN and fault states. |
| 6 | Exact component selections, packages, footprints, derating basis, alternatives and qualification status. |
| 7 | Editable mechanical design, tolerances, pack/harness fit and thermal arrangements; physical verification listed separately. |
| 8 | Composed schematics, generated netlists, ERC and cross-board consistency checks. |
| 9 | Supported analyses, verification procedures and external test assignments/results. |
| 10 to 11 | Layout for boards whose entry conditions pass; checked manufacturing and assembly files when release conditions pass. |
| 12 | Firmware, bring-up/test procedures and build documentation; measured product verification supplied through the agreed external work. |

Keep document completion, engineering decision closure and physical qualification distinct. Use the existing layer acceptance criteria; do not relabel an unresolved architecture condition as completed merely because it has an owner. Update only affected dependencies if a decision changes.

## 6. Execution and reporting

Use the existing plan and registers. Do not add another review framework or stop all work while waiting for a vendor response. Continue the existing compute policy: use rented machines for useful jobs, stop genuinely idle instances after two hours, and preserve their disks.

At the next milestone report briefly: committed artifacts, layers advanced, specific external dependencies, the supplier package/request's location, actual running tasks and the next deliverable with a measured or estimated ETA. Keep external waiting separate.

**Proceed now toward both outcomes: the strongest complete layer deliverables we can produce, and an actionable supplier handover for the engineering and physical work we cannot perform ourselves.**
