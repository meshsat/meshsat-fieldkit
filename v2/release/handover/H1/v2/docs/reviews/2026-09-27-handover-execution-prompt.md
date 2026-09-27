# Claude Code execution prompt: complete the foundations and deliver an engineering handover

Prepared 27 September 2026. Paste this entire prompt into the existing MeshSat project session with execution enabled.

<!-- Saved verbatim on 27 September 2026 01:20 CEST as the owner pasted it (MESHSAT-1357). The title's em dash is
written as a colon (the repository's no-em-dash rule); every other word is as pasted. It governs execution from this point: v2/docs/EXECUTION-PLAN.md records how. -->

## Objective and authority

My purpose in adopting a layered approach is to obtain completed, reusable engineering foundations before committing to PCB layout. If you cannot finish the PCB phase, I must still be able to give an engineer or company the completed preceding layers and have them understand what we are building, why, the settled design, and how to continue.

Make that handover outcome your immediate delivery priority. This is a correction to execution priorities and acceptance criteria, not an instruction to restart the project. Preserve the approved product scope, decisions, useful work, existing foundation-first plan, seven binding conditions, and permission boundaries.

Briefly update the existing execution plan and then perform the work. Do not respond with only another proposal, another general methodology document, or an offer to start later. If the session is in read-only Plan Mode, state that implementation needs the normal mode transition; do not claim execution has begun.

## 1. Establish the actual state once

Read the current repository and authoritative records. Use the latest progress reports as leads, not proof of current state. Preserve the source revision and identify material working changes and active jobs.

Map the existing nine pre-PCB layers to their actual deliverables. Reuse existing IDs and files; do not create a second requirements registry or parallel authority.

For each layer record:

- Scope and prerequisites.
- Existing deliverables and exact revisions.
- Completion criteria and evidence needed.
- Status: NOT_STARTED, IN_PROGRESS, BLOCKED, or COMPLETE.
- Unresolved decisions and their actual downstream impact.
- The next concrete closing action, responsible worker and dependency.

Prioritize completing and releasing the earliest unfinished layers. Check whether the product brief, CONOPS and requirements can close now. Do not keep these open merely because a later board remains unverified; identify any specific upstream decision that genuinely depends on it.

## 2. Define COMPLETE honestly

COMPLETE means complete for that layer's agreed engineering purpose. It requires current, internally consistent deliverables, satisfied acceptance criteria, the required review, and a versioned package another engineer can use.

It does not mean that a future physical prototype has already passed its tests. Requirements can be complete when their scope, limits and verification methods are settled. Schematics can complete their circuit review while the specified post-layout and prototype checks remain outstanding.

However:

- A missing decision that can change the required architecture, interface, component, board outline or protection strategy keeps the affected layer open.
- A feasibility uncertainty whose plausible bounds include failure cannot be dismissed merely by labeling it PROVISIONAL.
- A later physical test may remain planned only where it is not required to establish feasibility or make the current stage's design decision. State why deferral is justified.
- A document's existence, clean ERC, passing software fixtures, or another agent's agreement does not establish the underlying circuit's correctness.
- Preserve mandatory qualified review requirements and label AI review as AI review.
- Do not achieve completion by lowering requirements, dropping core functions, weakening protection, hiding a blocker as a future task, or silently narrowing the layer's scope.

Do not invent completion percentages. If a layer is not COMPLETE, show its remaining acceptance items.

## 3. Close these layers with concrete deliverables

Retain the project's existing layer numbering and agreed scope. Use this as a minimum acceptance map, adding only requirements already applicable to the project or justified by an identified engineering finding.

| Layer | Deliverable and completion condition |
|---|---|
| 1. Vision / product definition / pitch | Clear product purpose, users, prototype scope, exclusions and intended outcome. Existing report/deck commitments remain separately tracked; presentation polish must not delay technical closure. Claims agree with the engineering baseline. |
| 2. Concept of operations | Normal, degraded, startup, charging, shutdown, storage, service and fault scenarios; operating envelope; simultaneous modes; explicit behavior of retained core functions. Product decisions are settled under existing authority. |
| 3. Requirements | Source-linked, measurable requirements with acceptance conditions, applicability, allocation and verification stage/method. Resolve contradictions. Distinguish needs, design choices, assumptions and historical decisions. |
| 4. System architecture | Reviewed functional and physical diagrams, power/data/control paths, mode behavior, budgets with margins, trade decisions and demonstrated feasibility at this stage. Resolve design-critical ZEROIZE, EMCON, failover, power/thermal and battery questions before declaring the affected architecture complete. |
| 5. Partitioning and interfaces | Board responsibilities and owned interfaces at both ends: connectors, pinouts, electrical levels, power capacity, sequencing, reset/default states, communications, harnesses and mechanical mating. Firmware obligations affecting hardware are explicit. |
| 6. Components | Exact manufacturer/MPN/package/grade, supporting documents, selection rationale, compatibility findings, procurement constraints and supported alternatives. Known mismatches remain mismatches until proven compatible. Regenerated outputs preserve those decisions. |
| 7. Mechanical / enclosure | Editable CAD and dimensioned drawings, board envelopes, mounting, connector/cable/service access, tolerance and thermal interfaces. Critical fit uncertainties resolved by suitable evidence; later tests clearly allocated. |
| 8. Schematics | Current native schematics, readable PDFs, generator inputs/source, netlists and BOMs. Functional circuit reviews, exact part/land mapping, relevant ERC and regeneration checks completed. Known schematic-affecting defects closed per board. |
| 9. Pre-layout design analysis | Current calculations/models for relevant power, energy, protection, thermal, signal, timing and placement constraints; assumptions, margins and sensitivities. Define constraints handed to layout and the analyses/tests that require routed geometry or hardware. Complete the pre-layout portion without pretending post-layout SI or physical verification is already done. |

Release completed layers progressively. Preserve completed work if another layer becomes blocked. Mark board-specific completion explicitly; completing one board does not complete the entire schematic layer.

Keep existing milestones precise: FOUNDATIONS_BASELINED must retain its recorded scope. Do not use it to imply that all nine pre-PCB layers or the fabrication package are complete.

## 4. Control PCB work and preserve useful parallelism

Focus resources on closing the upstream layers and producing the handover. Committed PCB work requires its applicable upstream inputs to be complete; do not resume a routing campaign simply because a host is available.

Allow bounded PCB, development-device and mechanical feasibility experiments when they answer a named upstream question. Each needs pinned inputs, an acceptance criterion, a time/cost cap and a decision it will inform. Keep experimental results separate from accepted design artifacts. Preserve or finish already authorized, useful capped runs; checkpoint obsolete work through the existing process.

Use available parallel workers on independent closing tasks, with isolated worktrees/disjoint ownership and one integrator. Avoid simultaneous edits to shared generators and registers.

Known circuit corrections may be authored while their checking tools are being improved. Use source-backed review where the agreed criteria permit it. An automated checker is not mandatory for every rule, and a manual review must never be labeled an automated PASS.

After two unsuccessful attempts to close the same issue, reassess the cause and method. Choose a targeted experiment, qualified review, or justified alternative within the requirements. Record a genuine external blocker and continue independent work. Do not continue an unbounded author/check loop or declare success to escape it.

## 5. Repair stage gates that prevent their own satisfaction

Apply checks at the stage where their evidence can exist:

- Layout entry requires the reviewed schematic, parts, interfaces, geometry, stackup and electrical constraints.
- Fabrication release requires the actual layout to implement those inputs and pass its applicable checks.
- Prototype verification requires the specified physical evidence.

Decision 31 must not require a completed corrected layout before allowing that layout to be created. Preserve the fabrication protection hold until its evidence exists.

Likewise, a bench-only INT-002 result cannot be a prerequisite for designing the board needed to run that test. Preserve the pre-layout feasibility assessment and allocate the physical check correctly.

Check the six feasibility blockers for similar cycles. Do not move a decisive uncertainty to a later phase merely to unblock a status.

## 6. Produce a portable handover now and improve it incrementally

Create a versioned handover snapshot using the existing release structure, with a ZIP and a START-HERE index. The first snapshot may be partial; say so explicitly. Do not wait for PCB completion or every blocker to close before making completed work transferable.

Include:

- A concise project overview and the current layer-status/acceptance table.
- The completed layers and clearly separated incomplete candidates.
- Readable documents, diagrams, schematic PDFs and dimensioned drawings, plus editable/native originals.
- Requirements, architecture, interfaces, decisions, exact BOM/part identities, calculations and supporting sources.
- Necessary generator/source files, configurations, dependency/tool versions and working regeneration/verification instructions.
- Current verification results tied to the actual inputs, including relevant checking helpers; obsolete results labeled and separated.
- A manifest tying artifacts to one coherent source snapshot and identifying every included revision.
- A focused continuation brief: settled decisions, remaining work, constraints for the PCB engineer, known failed approaches and useful experiments.

The recipient must not need this chat, hidden session memory, thousands of historical rulings, or access to one particular running host to understand the design. Where a source or tool needs separate access, identify it and its effect explicitly.

Keep the editable working documents authoritative. Release snapshots are immutable copies; do not maintain contradictory live specifications.

For every BLOCKED item supply a compact engineering question: exact issue, affected decisions/boards, evidence, attempts and results, viable options, recommended next action, required expertise/equipment, and cost/lead time where known.

## 7. Verify that the handover actually works

Use one fresh checker who did not assemble the package. Give them the package and its stated dependencies, without relying on conversation history.

Have them determine:

1. What is being built, for whom, and under which operating conditions?
2. Which requirements and design choices are settled?
3. How do the boards and interfaces fit together?
4. Which layers are complete, and what precisely blocks the others?
5. Can they follow a representative calculation or regeneration path using the included instructions?
6. What should an incoming PCB engineer do next, and which decisions must they preserve?

Resolve material missing information and contradictions. An agent can check handover usability; it does not replace the qualified electrical reviews already required.

A partial package that passes this usability review is a usable partial handover, not a claim that the engineering is complete.

## 8. Report outcomes and continue

At the next checkpoint provide:

- The handover snapshot and its source revision.
- Each layer's status, with evidence for every newly COMPLETE layer.
- The exact remaining blockers, grouped by design work, physical evidence and genuinely external authorization.
- Actual work completed, next closing actions, useful experiments and spend.
- Any changed requirement or reopened decision, its evidence and affected scope.

Give concrete costed requests for purchases or external review only where existing authority is insufficient. Do not repeat previously delegated product questions or suspend unrelated work while waiting.

Preserve completed releases when later evidence requires a change. Reopen only affected current items, explain the impact, and issue a new version.

Start by auditing and closing the earliest layers, assembling the first handover snapshot, and dispatching independent closing tasks. Continue until every currently achievable completion criterion is met and every genuine blocker has a usable specialist handover. The owner must receive durable engineering deliverables even if PCB layout later stalls.
