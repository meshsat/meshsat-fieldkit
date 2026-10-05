# MeshSat field kit V2: execution constitution

Adopted 4 October 2026 (Europe/Amsterdam) by the owner's instruction of that day, filed as received at
`v2/docs/handover/OWNER-INSTRUCTION-2026-10-04.md`. It governs process: where an earlier process instruction conflicts, this
text applies. It amends no product requirement, grants no fabrication release and overrides no platform permission.
The text below is the owner's Part A as received, with one typographic dash written out under the repository's rule; live
task detail is in `v2/docs/EXECUTION-PLAN.md`. Prototype framing: no V2 board has been built, ordered or measured.

## Standing constitution

Purpose: complete coherent, reviewable layer deliverables and resolve engineering defects efficiently. This constitution replaces conflicting process instructions when adopted; it does not amend product requirements, grant fabrication release or override platform permissions. Adopt it through the plan below.

### 1. Preserve owner intent and accepted work

- The current owner brief and explicit rulings control product scope. Battery and solar remain required; storage stays inside the Peli, with no external battery; HF and tablet remain; optional tablet charging reduces endurance. The 48 to 72 hour runtime is an objective under a stated profile. Existing pack, input, thermal and service rulings remain until explicitly changed.
- Distinguish a requirement from an engineering selection, assumption and objective. A failed implementation does not invalidate a well-defined requirement. Change affected baseline passages through controlled amendments only when necessary; preserve prior accepted revisions.
- Continue authorised engineering and reversible design work. Owner decisions concern actual requirement changes, purchases, commitments and other reserved actions. Developing and costing an alternative is not permission to adopt or buy it. External correspondence remains unsent without authorisation.

### 2. Use one current record; report distinct completion states

- Maintain the existing owner brief, execution plan, findings register and layer-status record. Store current values once and reference them. Superseded values belong in dated history. Archive reviews unchanged; clearly separate their historical statements from current assertions.
- For each deliverable distinguish document acceptance, supported design, implementation and physical qualification. Use existing schema fields; these distinctions do not require a new status engine. An unmet condition stays visible even when its desk analysis is complete.
- Report engineering-handover readiness, power-design closure and fabrication release separately. A promoted integration set is none of those by itself. “100%” requires a named scope, its satisfied criteria, revision and evidence; never use a blended percentage to hide blocked criteria.

### 3. Establish the system basis before refining parts

- Use one revisioned operating envelope for connected analyses: source states, loads, concurrent service, tolerances, temperature, ageing, startup, docking, faults, recovery and repeated operation. State boundaries and units. Different cases may differ deliberately; identify why.
- Before a component fix expands, check its effect on the complete connected path and adjacent boards. Do not solve a current limit by silently reducing cooling, transmit service or another mandatory function.
- Derive results from the actual circuit and primary manufacturer sources. Label guaranteed limits, typical data, measurements and assumptions separately. Explain corner coverage, uncertainty and available margin. Historical numbers are consistency checks, never calibration targets.
- A prototype measurement has a defined specimen, conditions and transfer scope. It does not automatically establish a population guarantee or qualify a different layout.

### 4. Give every engineering task a bounded closure contract

Before dispatch, put one short entry in the existing register: defect or question; authoritative inputs; affected requirement; smallest deliverable; acceptance check; owner; dependency; and next checkpoint.

| Type | Required action | What can close it |
|---|---|---|
| Demonstrated design defect | Correct it locally or give the supplier a specific correction scope | Checked correction against the same failure case; physical qualification remains separate where required |
| Missing physical/vendor evidence | Finish the minimum executable qualification/request and transfer it | The required evidence, or a supported design change that removes that dependency |
| Unresolved design choice | Compare at most three materially different approaches | Supported selection within authority, or one concise owner decision |
| Tool/integration defect | Reproduce and correct the failure mechanism | A meaningful regression plus the affected real workflow passing |

An assigned test is not a corrected circuit. Missing evidence is not automatically a demonstrated failure. Block only the decisions and descendants that actually depend on an item.

### 5. Stop repeated attempts that do not change the evidence

- Review progress at the planned checkpoint, normally within 90 minutes. Long calculations may continue when their expected duration and actual progress justify it. A quiet buffered log alone is not a stall.
- A repeated run must name the changed design, input, diagnosis or verification method and the question it will settle. Rewording the same unsupported claim is not another engineering attempt.
- After two negative checks of the same proposed solution, end that correction loop. The coordinator performs one bounded diagnosis and chooses a simpler supported design, a materially different method or an external qualification/correction task. Preserve the open finding.
- If one workday produces no verified closure or usable engineering deliverable on the critical path, explicitly reassess scope and method at the next checkpoint. A changed priority or qualification route is an outcome; more scheduling documents are not.

### 6. Make independent checking decisive and proportionate

- Use Astra through the existing launcher to challenge decision-critical assumptions before expensive downstream work, and to check material corrections independently. The checker must see the owner brief, exact candidate, relevant sources and acceptance criteria.
- Default to one focused check and one targeted recheck for a candidate, within authorised usage. Further checking requires a materially changed approach and an explicit bounded reason in the existing task record; do not invent a new issue ID to reset a limit.
- Exhausting review calls never changes a verdict. The coordinator may verify clerical/integration fixes, but cannot turn a material unresolved rejection into an independently accepted design by self-signing. Record the actual checker's role and retain previous verdicts.
- A changed design or new material evidence can justify another check under the applicable authorisation. Otherwise retain UNVERIFIED/CONDITIONAL status and the dependent release hold. Do not reopen previously accepted work solely because this process policy changed.

### 7. Keep execution bounded and autonomous

- The owner authorises up to three author/reviewer workers across Claude and Codex/Astra, plus the coordinator. One writer owns a branch at a time. Scheduling a checker consumes a worker slot. Use the third slot for ready independent work or a ready review; do not hold it idle for a review whose inputs are unfinished.
- The coordinator owns integration, scheduling and small verified record corrections. Do not occupy an engineering worker merely to copy a checked status or checksum. Coordinate ownership before editing an active author's files.
- Preserve healthy jobs, successful outputs and uncommitted work. Before replacing a failed/context-exhausted worker, check whether its child calculation survived. Resume one writer from its checkpoint with a concise brief, not the entire accumulated transcript.
- Continue the next ready item without waiting for this chat's review. When an external dependency blocks one item, dispatch independent work. If no authorised task is ready, report that fact precisely and retain a recoverable checkpoint.

### 8. Keep tests meaningful and recomputation selective

- Engineering checks exercise the failure mode, limits and interfaces. Software regressions should fail against the old defect and pass against the correction where feasible. Changed expectations need an independent requirements/evidence basis; do not change a test merely to obtain green.
- Use affected tests during authoring and the established release suite for a frozen candidate. Do not rerun the full suite for isolated editorial corrections outside its dependency boundary. Do not remove a required gate to save time.
- Separate numerical computation, rendering and release evidence. Numerical inputs flow into results, then into views; rendered summaries and status counts must not create cycles back into numerical inputs. Remove a demonstrated dependency cycle with one bounded fix, preserving coverage of every actual input.
- Cache keys cover model code, relevant inputs and dependencies, and material tool versions. Reuse only matched results. A changed numerical input invalidates dependent results; unrelated prose need not. Label cached validation separately from fresh solver execution.
- Reuse safe regeneration: validate exit status and expected complete output before replacing a prior artifact. Refused or partial output remains diagnostic evidence only.

### 9. Freeze once per stable candidate

The required order is: **finish intended merges and input changes → install matching external evidence → regenerate in dependency order → verify stability → commit the candidate → bind its manifest → run required checks on that candidate → promote that candidate.**

- Preserve the current freeze's usable outputs. Later changes require an impact check: regenerate and revalidate affected dependencies before finalising; do not blindly repeat the entire chain.
- Keep the candidate immutable during its release checks. Later independent work belongs in the next set. A necessary correction creates a new candidate with the affected checks and required release gate rerun.
- Retain real process exit codes. The existing promotion gate must check candidate identity, expected module coverage, failures/load errors, explained skips, evidence identity and consistency of totals. “Exited 0” alone is insufficient.
- Repeated integration failure from the same cause becomes a bounded tooling correction before another expensive suite. Keep useful engineering workers moving where possible; introduce no new scheduler or general workflow framework.

### 10. Advance layers through explicit dependencies

- Prioritise the earliest incomplete layer and design decisions that affect several descendants. Parallelise independent interface, component, mechanical, schematic, analysis and firmware work. A cross-layer correction must identify every affected contract and generator.
- A layer deliverable contains editable sources, its acceptance evidence and scoped remaining obligations. Finish schematic work through draft composition, generation and consistency checks when authorised prerequisites permit; do not stop forever at prose proposals.
- Physical uncertainty may allow conditional downstream preparation where interfaces are bounded. A known defect remains open and holds its affected release. Start layout only where that board's entry conditions pass; final fabrication requires its release criteria.
- The immediate external target is a useful engineering handover. Prototype evidence builds have their own supplier-reviewed scope; they do not require the final-product qualification they exist to produce. They still require the applicable purchase and execution authorisation.

### 11. Deliver evidence without another packaging project

- Keep a compact supplier baseline and small committed deltas. Include changed sources, calculations, verdicts and procedures needed for the review; identify omissions and their retrieval route. No full history unless a demonstrated replay dependency requires it.
- State tested revision, packaged revision and any difference. Generate file sizes/checksums from the delivered bytes. Verify the actual exported copy and its covering references. Bind a dated addendum to an immutable ZIP when editorial corrections suffice.
- Ask suppliers to confirm engineering scope, responsible personnel, deliverables, exclusions, cost and schedule. Do not assume ordinary fabrication/assembly includes circuit design or qualification. Supplier engagement proceeds alongside authorised desk work.

### 12. Measure progress and conserve resources

- At milestones and roughly every two hours during active execution, report: layer artifacts accepted; defects corrected and verified; new/regressed defects; external dependencies; active jobs with progress evidence; next critical-path milestones; and resource use. Counts of commits, tests and sets are supporting evidence, not substitutes for those outcomes.
- Give measured and estimated durations separately. Exclude unknown vendor/physical waiting from desk-work ETA and label what the ETA actually delivers. Use Europe/Amsterdam time. Keep the human update about 300 words with links to existing detail.
- Use rented compute for ready jobs and keep simultaneous heavy jobs within available CPU, memory and disk capacity. No total rental-spend cap is reinstated. Stop genuinely idle instances after two hours, preserving disks; do not destroy them without authority. Track compute and storage cost separately.
- Keep this constitution stable. Put task-specific changes in the existing plan/register. Use short persistent instructions and explicit worker briefs; memory is not the sole record of an owner ruling. Prompt rules shape behaviour; the existing executable guards must continue to enforce checkable release conditions.
