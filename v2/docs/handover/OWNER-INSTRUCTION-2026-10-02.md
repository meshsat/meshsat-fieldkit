# Owner instruction, 2 October 2026 (late evening): continue autonomously through the layers

Received in the coordinating session on 2 October 2026 after the second external review of the Layer 4 checkpoint. Filed as received; it binds the execution plan from this point.

Continue autonomously from the current saved state through Layers 4, 5, 6 and the remaining project layers. Apply the following instructions to the existing execution plan once, then execute. Preserve useful work already running.

The objective is to deliver progressively complete, internally consistent engineering packages that another engineer can take over layer by layer, and advance toward a qualified prototype and fabrication release.

**1. Preserve the approved product and requirements**

Use the current owner brief and accepted requirements as authoritative. In particular:

- Battery and solar remain mandatory.
- Storage stays inside the Peli; no external battery.
- Keep HF and the tablet.
- The 48to72-hour endurance figure remains a design objective under its stated profile. Report the actual result honestly.
- Optional tablet charging reduces endurance.
- Preserve the retained solar-input requirements and other approved operating conditions.
- Do not silently change the ruled pack arrangement, adopt a proposed cell change, reduce service, or relax protection and temperature requirements.

Make routine engineering choices autonomously within these constraints. Prepare alternatives where necessary. Ask me only where an actual owner ruling or an action outside your existing authority is required.

**2. Converge on one connected power design**

Finish the current targeted work on CP01toCP03, the solar guard and the qualification route. Integrate the corrections into one candidate.

For each remaining power issue, distinguish:

- A demonstrated circuit or analysis defect: correct it.
- An unresolved design assumption: bound it with applicable evidence or select a less dependent design.
- A physical qualification question: define the specimen, measurement, acceptance criterion and consequence of failure.

Prefer adequate margins, supported component behaviour and fewer critical dependencies. Repeatedly adding compensating circuitry must trigger reconsideration of the affected stage.

Preserve the charging-heat, runtime and other corrections already accepted unless their inputs change.

For the solar guard, treat 0.240 V as a design target. Account for numerical error and component/parasitic uncertainty explicitly. Any required inductance must belong to a controlled hardware and fault envelope.

For the battery switch, address the complete operating and fault histories, including docking inrush. For the eFuse, distinguish operating overload, short applied while on, startup into short and retry.

Do not repeat an unsuccessful approach on unchanged evidence. At that point, choose a materially different remedy or issue a concrete experiment/vendor/engineer task. A review budget expiring never closes a finding.

**3. Keep completion claims precise**

Use the existing layer gates. Report these separately:

- Layer documents and editable artifacts complete.
- Design reviewed and accepted.
- Circuit/layout changes implemented.
- Physical qualification completed.
- Fabrication release approved.

An engineer handoff can be useful while the design remains conditional. A named future test does not establish feasibility. Software tests establish their tested behaviour, not hardware performance.

Credit 100% only against the named layer’s fixed completion criteria. Do not rename a blocked gate to make progress appear complete.

Preserve accepted earlier baselines. If a real change is necessary, revise only the affected requirements and dependent artifacts through change control.

**4. Advance by dependencies, with the earliest incomplete layer as the priority**

Continue automatically when a task’s entry conditions are met. An unresolved question blocks its actual dependants, not the whole project.

Deliver the following using the existing layer definitions:

- **L4:** one coherent system architecture, power diagram, operating/fault states, budgets, selected approaches and explicit remaining feasibility conditions.
- **L5:** board responsibilities and interface contracts covering electrical limits, startup, sequencing, faults, control, connectors and mechanical boundaries.
- **L6:** component selections and alternatives, exact parts/packages, applicable ratings, derating, source evidence and qualification obligations.
- **L7:** enclosure, fit, thermal paths, harnesses, sealing, tolerances, service access and required physical checks.
- **L8:** implement approved circuit changes in the generators and schematics; check cross-board connectivity and agreement with the interface contracts.
- **L9:** analyses tied to the implemented circuit, with assumptions, operating cases, margins and physical verification clearly identified.
- **L10:** layout only where the relevant schematic, stackup, interface and mechanical entry gates are satisfied.
- **L11:** manufacturing and assembly packages from the exact validated design revision.
- **L12:** firmware, bring-up procedures, test plans and build documentation in parallel wherever dependencies allow; physical results remain open until performed.

Work provisionally on stable portions of later layers when useful, keeping their assumptions and invalidation triggers visible. Avoid expensive routing on unstable circuits.

At each layer milestone, provide its editable artifacts, a concise summary, traceability and unresolved dependencies.

**5. Give physical verification a practical route**

For every required experiment, identify:

- The specimen: evaluation hardware, representative coupon, enclosure mock-up or controlled prototype.
- What it represents and what evidence can transfer to the final design.
- The procedure, measurable pass limits and consequence of failure.
- Any purchase, access or execution authorization still needed.

Separate permission to construct an evidence-gathering prototype from final design or fabrication release. Remove circular gates that require a finished board before permitting any representative prototype.

Prepare vendor questions and engineer briefs ready for action. Continue independent engineering while answers or measurements are pending.

**6. Use Claude and Astra deliberately**

Keep the existing authorized concurrency limit and one author per branch/artifact.

You own integration and the complete system model. Use available worker slots for independent tasks on the critical path or the next ready layer.

Use Astra to challenge decision-critical assumptions, calculations, datasheet conditions and cross-board consequences. Give it the exact candidate, relevant sources and a bounded question. Avoid having every session repeat the whole project history.

Normally use one focused independent review and one targeted recheck. Preserve unresolved findings honestly. Coordinator verification must be labelled as such and must not overwrite an independent rejection.

Allocate idle slots to useful work; do not require another review from this chat before continuing authorized tasks.

**7. Keep execution efficient and recoverable**

- Reuse the existing tools, worktrees, ledger and safe regeneration helper.
- Run targeted checks during changes and the required release suite on the exact integrated candidate.
- Regenerate artifacts in dependency order and promote outputs only after successful checks.
- Avoid repeated full suites and document rewrites without a concrete changed risk.
- Reuse authorized compute. Stop idle rented instances after about two hours while preserving their disks; follow existing spending authority.
- Package committed review snapshots promptly, clearly labelled. Packaging must not hold up independent engineering.
- Checkpoint commits, working changes, unresolved findings and the next executable action so interruption does not require reconstruction.

**8. Continue after each result**

Worker completion, test completion and review results are triggers for the next action. Waiting is appropriate only while relevant work is running or all currently runnable authorized work is exhausted.

At milestones, report briefly:

- What materially changed and its commit.
- Which layer criteria are satisfied and which remain open.
- What is actually running.
- The next critical milestone and its evidence-based ETA.
- Only the owner decisions genuinely needed.

Do not count more documents, tests or review rounds as hardware progress.

Execute now: finish and integrate the current corrections, obtain the focused check, deliver the coherent power package with its qualification route, and immediately continue the ready Layer 5 and Layer 6 work. Continue through subsequent layers under these rules without waiting for another instruction from me.
