# The owner's instructions of 5 October 2026: the recovery review, the 160 C correction, the review of the 13:55 report, and the P0 instruction with its two plan reviews

Filed as received (MESHSAT-1357), byte for byte inside each part below, including the owner's own typography (the saved copies'
one-line filing headers removed; the texts themselves untouched). Nothing here is edited. Parts 1 to 11 are in
`OWNER-INSTRUCTION-2026-10-04.md`. The live plan that applies these parts is `v2/docs/EXECUTION-PLAN.md`, entry of 5 October 2026
14:48 CEST; the compact blocker list part 15 asks for is `v2/docs/records/l4close/P0-POWER-LIST.md`. Part 15 made Layer 4's power architecture the only active layer; part 19 narrows that: the
deliverable is the desk engineering package for a receiving company, each layer accepted at its DESK gate in order, with physical
qualification and fabrication release as separate gates and the supplier's validation scope written down, not awaited. Prototype framing: nothing is built, bought or measured.

| Part | Received | sha256 of the part's text |
|---|---|---|
| 12. Review of the morning's recovery: the CAN fault phrase clarified (an open defect if over the limit, else the applicable requirement named) | 5 October 2026, about 10:30 CEST | `f6afeceae0c19ea7d50d9ad686288cfd1958eb3208f02e3640588518680880d7` |
| 13. Correction: 160 C typical shutdown is not a permitted temperature limit (125 C the criterion, 150 C the absolute maximum, 176.3 C a model result that fails) | 5 October 2026, about 11:00 CEST | `1d2391b5b8bf3de31d85c4193ce833f02c7abec488e1e6056eec6314ee83e493` |
| 14. Review of the 13:55 status report: continue under three workers; T11 states apart; firmware escalation not assumed; copper comparison with quoted or estimated cost; F13, F16, F17 not corrected; set 30's bounded scope | 5 October 2026, about 14:05 CEST | `d7aadb430e574c733b3afff675005b76298d3d94ee0bf07c834e16dd3cb00268` |
| 15. P0 power closure and strict layer-by-layer execution (supersedes the permission to keep later layers moving; stop and preserve; one connected power correction with three workers; the Layer 4 exit gate; convergence; layer order; checkpoints) | 5 October 2026, 14:20 CEST | `91c55cc21c8152c33213b2938330d8ebd874a08b035b0f55de7f381a909c5bee` |
| 16. Review of the P0 execution plan: proceed after four targeted amendments (calibration and layout bounds need a feasibility basis; the integration order and one combined base; preserve work and start engineering beside the clerical work; the external closure path made actionable) | 5 October 2026, about 14:45 CEST | `a80ab901ae447f789bc74ec0cfbfc0103725c44d73c4282764908d02c489f726` |
| 17. Second review of the revised plan: READY to approve for execution; the baseline watchpoint; 14 to 18 h is a desk candidate, not Layer 4's closure | 5 October 2026, about 14:55 CEST | `14f5dcc8fc2aacc4a5a9e33a06b321021651889cf5d7b6dfeee12bc3776d8b8d` |
| 18. Review of P0 checkpoint 1: continue the authors; finish the external decision packet (U-02's per-mode reconciliation and the mock-up's sum, U-04's evidence route apart from the whole-kit release, U-01's two kinds of evidence) | 5 October 2026, about 15:30 CEST | `62351f9c8ca4a11b1328b5fcfb161c680b17701335242d8a3d505b5c900085a2` |
| 19. Handover scope amendment and review of the external packet: the deliverable is the desk engineering package for a receiving company; sequential DESK acceptance per layer; the packet reframed as the supplier validation annex with three corrections (a failed arrangement is not a requirements conflict; the mock-up sum; investigating the Saft option apart from adopting it) | 5 October 2026, about 15:45 CEST | `d448616ce3607d9653fe47efea771aa9a68e31198ec943bf52a9f4bf8262b02a` |


---

## 12. Review of the morning's recovery: the CAN fault phrase clarified (an open defect if over the limit, else the applicable requirement named) (as received)

**The reported recovery looks properly controlled:** staged work is backed up, three authors resumed from checkpoints, and the rented boxes are stopped with disks retained. No new broad prompt is needed.

One phrase needs clarification in Slot C’s report: **“junction temperatures under CAN-bus faults, outside the criterion.”**

- If temperatures **exceed the permitted limit**, retain an open defect.
- If the fault case is **outside T10’s scope**, identify the applicable requirement and where that case is handled.

The 4.18 V pre-regulator remains a drafted candidate until checked. The next useful milestones are Slot C’s completed report and V5’s firmware verdict.


---

## 13. Correction: 160 C typical shutdown is not a permitted temperature limit (125 C the criterion, 150 C the absolute maximum, 176.3 C a model result that fails) (as received)

**One correction: 160 °C typical shutdown must not be treated as a permitted temperature limit.**

Keep these separate:

- **125 °C:** T10’s stated design criterion.
- **150 °C:** the manufacturer’s absolute maximum junction temperature—not an operating target.
- **160 °C typical:** shutdown behavior, with no guaranteed maximum trip temperature stated. It cannot prove protection below the absolute maximum. [diodes.com](https://www.diodes.com/assets/Datasheets/AP2112.pdf?utm_source=chatgpt.com)

The reported **176.3 °C is a model result**, not a measured temperature. It fails the stated thermal bounds; the real device might shut down or cycle, but that does not establish acceptable fault behavior.

Claude should retain the applicable fault finding until a supported correction or protective response meets the required temperature and service criteria. This clarification can join the current author’s work.


---

## 14. Review of the 13:55 status report: continue under three workers; T11 states apart; firmware escalation not assumed; copper comparison with quoted or estimated cost; F13, F16, F17 not corrected; set 30's bounded scope (as received)

(The owner's review of the 5 October 13:55 status report, as pasted in the session at about 14:00 CEST; full text kept in the session
log's source. Its continuation prompt, binding:)

Continue the current work under the three-worker limit; do not restart it or add another broad review.

Finish V5F, V2RG and V6 against their actual candidate revisions. Report active versus queued jobs accurately, and preserve every review verdict. Then define and execute set 30's bounded integration scope under the existing gates, with explicit open and conditional items. Give the candidate, remaining prerequisites and next completion checkpoint.

Make these small reporting/decision corrections in the normal update:
- T11: distinguish research delivered, review corrections open and three-radio fit not demonstrated. Provide the plan, Astra's recheck and O-1a–O-7 table for the SDR decision. A one-radio pilot is not approval of the final architecture.
- Firmware escalation: do not assume an engaged supplier firmware engineer. If escalation becomes necessary, preserve the reproducer and unresolved defect, specify the capability needed and identify who must secure it. A review limit does not close a software defect.
- Copper: finish the viable-options comparison with technical basis, recommendation and quoted or explicitly estimated cost; disclose any pricing unknown.
- Keep CAN fault findings F13/F16/F17 out of the list of corrected defects while they remain open.

No new purchase, vendor contact or requirement change is authorised by this clarification. Continue all independently eligible layer work and keep fabrication release blocked until its own criteria are met.


---

## 15. P0 power closure and strict layer-by-layer execution (supersedes the permission to keep later layers moving; stop and preserve; one connected power correction with three workers; the Layer 4 exit gate; convergence; layer order; checkpoints) (as received)

# Owner instruction: P0 power closure and strict layer-by-layer execution

This instruction supersedes earlier permission to keep later layers moving, fill spare worker slots with unrelated tasks, or leave current workers running because they are busy. Preserve existing work and evidence. Change the execution priority now.

Prepare a short executable plan, then execute it through the normal plan-mode handoff. Do not respond with another general constitution or research programme. My objective is the earliest defensible completion of the power architecture, followed by each remaining layer in order. P0 is the execution priority; retain the actual engineering severity of each finding separately.

## 1. Stop the current allocation and preserve the work

- Interrupt all currently assigned Claude and Codex/Astra workers. Cancel their current assignments and queued continuations, including SDR research and unrelated firmware, mechanical, component and documentation work. Do not wait for their current rounds to finish.
- Capture each branch tip, staged and unstaged changes, relevant untracked files, logs, and a short resume note. Preserve incomplete work explicitly as incomplete. If an agent cannot respond, the coordinator captures its worktree.
- Stop project-owned child jobs and monitors that would continue these assignments. Preserve partial outputs separately from previously valid outputs. Do not kill unrelated processes, discard changes, reset branches, delete worktrees or overwrite accepted evidence.
- Verify that no stopped assignment can continue writing or relaunch itself. Report any process you cannot stop and what it can affect. Target a brief recovery checkpoint, not an hour of packaging.
- Stop rented compute that is no longer useful; retain disks and prepared environments. Nothing is destroyed. Existing compute spending authority remains; hardware purchases and external messages remain subject to their existing authorisation boundaries.

If active plan-mode restrictions prevent these actions, state that they have not happened, identify what remains running, and make this the first execution step. Do not claim workers are stopped merely because a plan says to stop them.

## 2. Establish the current baseline and the actual power blockers

Read the owner brief, accepted requirements, current main, and the latest relevant branches and review records. The 13:55 report named main `aa32332c`; verify the live state rather than assuming it remains current. Preserve already supported corrections instead of repeating their derivation without cause.

Use the existing findings register. Produce one compact current list with: finding, failing operating/fault case, requirement or limit, correction needed, owner, evidence needed, dependency and closure test. Distinguish:

1. A desk-fixable circuit, calculation, firmware/protection or interface defect.
2. Missing evidence that can still be obtained or bounded at the desk.
3. A genuine external dependency: a manufacturer statement, measurement, supplier engagement or owner decision.

Start with the remaining power defects, including F01/all-transmit, CAN fault findings F13/F16/F17, I-03 and its ground return, T10, eFuse settings and their coupled protection/thermal effects. Check the current disposition of solar protection, battery FET sharing, thermal protection and coupon-method findings. Do not reopen corrected items merely because their identifiers occur in old reviews; do not omit an open item because it belongs to another layer's record.

F01 must receive an author and a next engineering action immediately. It must not remain undrafted while all available slots work on secondary reporting or review tasks.

## 3. Keep the approved requirements fixed

Retain the current owner-approved baseline: internal battery and solar, no external battery, HF and tablet retained, the approved enclosure and pack ruling, optional tablet charging, and the 48–72-hour runtime objective correctly distinguished from mandatory service.

Use the exact repository requirements for all-transmit operation, starting voltage, fans, compute loads, source windows, temperature modes and fault service. Retain REQ-016's approved solar window. Do not solve a mandatory power defect by silently raising the operating floor, reducing service, turning off required fans, relying on typical compute consumption in a different case, or changing thermal requirements.

The three-SDR proposal is paused and unadopted. Keep its loads and fit assumptions separate from the approved baseline. Preserve the study for a later owner decision.

Leave Layers 1–3 accepted unless a specific, evidenced contradiction actually requires an amendment. If a change of requirement, pack, enclosure, service or spending authority becomes necessary, present the smallest concrete decision with consequences. Do not make that change yourself or conceal it in an engineering assumption.

## 4. One connected power correction, with three workers maximum

The coordinator remains accountable for convergence and integration. Assign fresh, bounded briefs using the recovered work:

| Slot | Responsibility |
|---|---|
| A | One power-design author owns the connected candidate and all its operating/fault cases. |
| B | Astra or another independent checker challenges the assumptions, calculations and complete candidate. It does not author the correction it accepts. |
| C | One clearly scoped P0 supporting task, such as the CAN fault correction or a source/thermal bound, coordinated with the power author and on separate files. |

The three-worker limit includes all active authors and reviewers; the coordinator is additional. There must be one writer for each owned file. Leave a slot unused if no independent P0 task is ready. Do not resume the old allocation automatically.

Keep one authoritative operating envelope and budget. It must connect sources, charging, storage, converters, loads, feed and return conductors, connectors and protection. Use consistent boundaries for voltage, current, losses and heat. Cover required simultaneous operation, startup, docking, charging, all-transmit, relevant temperatures and component tolerances, and the required fault combinations. Do not stack mutually exclusive states or omit permitted combinations.

For every correction, trace its effects through that complete path before calling it a candidate. Recheck changed load, voltage drop, ground current, protection coordination, thermal limits and required service together. A typical value or typical thermal shutdown is not a guaranteed protective limit. Keep model results, printed guarantees and measurements distinct.

Use existing later-layer drafts as inputs. A narrowly necessary circuit edit, component check, fit check, interface correction or composition test may be brought forward solely as a named prerequisite of the current power gate. It must have a stated reason and acceptance check. This is not permission to restart general work in Layers 5–12 or to count those layers as complete.

## 5. Define and enforce the Layer 4 exit gate before redesigning

Use the existing acceptance criteria and make their power implications explicit. Do not weaken them to produce a completion label. Layer 4 cannot be declared complete while an unresolved fact could overturn the selected architecture, its mandatory service, its safe operating envelope or its physical feasibility.

The power portion of the exit gate requires:

- One coherent selected design, with precise circuit/generator changes and compatible interfaces. Separate uncomposed drafts are insufficient.
- Every current desk-fixable power defect corrected and verified against its actual failure case, including the connected consequences of each correction.
- Reproducible calculations tied to the actual candidate and source inputs; explicit margins, uncertainty and applicable operating conditions.
- Independent acceptance of the decision-critical corrected design. Preserve every earlier negative verdict. A coordinator sign-off or an exhausted review allowance does not resolve an outstanding independent blocker.
- No architecture-defining dependency hidden under "conditional", "supplier test", "closed on paper" or a later layer number.
- A stable candidate that passes the applicable existing integration gates on the revision being accepted.

Separate later qualification from unresolved feasibility. A later test may confirm a design already supported by conservative evidence, where the existing layer criteria permit this. If its outcome decides whether the architecture works at all, it is still a current blocker. Identify the specimen, measured quantity, pass limit, required capability and owner; do not claim a planned test has passed.

We have no in-house electronics engineer, and supplier engineering or firmware support has not been secured. Prepare a concrete request when external work is essential. Do not assume NextPCB, Seeed or an unnamed engineer has accepted it. Do not contact anyone or buy hardware without the required authorisation.

## 6. Converge quickly without forcing a pass

- Reproduce each material failing case before changing the design. Prefer the simplest supported correction with useful margin and the fewest new uncertain dependencies. Do not tune a model to match historical numbers.
- When a component's missing guarantee is the obstacle, first make a bounded comparison of practical design alternatives. Select a route within the approved requirements where evidence supports one. Endless searches for the same unavailable limit are not progress.
- Give the independent checker the complete candidate and its assumptions, not a request to confirm the author's conclusion. Use one focused review and a targeted recheck of substantive corrections and their affected interactions.
- If the same failure survives two attempts, stop repeating that method. State the counterexample and change the circuit approach or identify the exact external action needed. A changed design still needs independent checking; do not convert a failed review into acceptance to honour a run budget.
- Generate and bind documentation after the technical inputs stabilise. Use the existing tools and registers; do not create another governance framework. Preserve required evidence without adding cosmetic work to the critical path.
- Freeze one coherent candidate, run affected checks and the required suite, and integrate without concurrent edits to its bound inputs. Reuse valid evidence only where its assumptions and content bindings remain valid. Never relax a test to make the candidate green.

## 7. Restore strict layer order

Layer 4 is the active layer. Layers 5–12 remain paused except for the explicitly bounded prerequisites above. Existing work is retained as provisional evidence, not lost or accepted by implication.

After the full Layer 4 gate passes, proceed to Layer 5; after Layer 5 passes, proceed to Layer 6, then 7, 8, 9, 10, 11 and 12. Keep the repository's firmware/documentation and physical subgates visible. Do not skip a blocked layer merely to keep workers busy. Worker parallelism is within the active layer and its indispensable prerequisites.

For each layer, name its inputs, scope, exit criteria and accepted revision. Check relevant downstream feasibility constraints before accepting an upstream choice. Detailed design can reveal new evidence later: if it invalidates an accepted assumption, reopen the affected gate and pause dependent progression while correcting it. Do not leave upstream acceptance unchanged while patching around a contradiction downstream.

A set number, promoted commit, test count or completed document is not a completed layer. Report "100%" only when that layer's actual scoped acceptance criteria are met. Fabrication release remains a separate gate.

## 8. First checkpoint and reporting

Your first useful checkpoint should be within 30 minutes of execution starting, subject to actual recovery constraints. Report:

1. Which old workers and processes are stopped, where their work is saved, and any exception.
2. The verified baseline and the short P0 blocker list.
3. The author, independent checker and supporting assignment.
4. The first circuit correction/reproduction being worked and the next concrete artifact.
5. The critical path and an evidence-based time range, separating desk execution from external waiting.

Thereafter give a brief checkpoint at least every 45 minutes or at a material result. State defects actually eliminated, new failures discovered, current critical-path work and the next deliverable. Label measured durations and estimates. If a checkpoint slips, identify the cause and change the execution approach where needed; do not simply move the finish time again.

ASAP means prioritising a defensible engineering result and removing avoidable work. Do not promise that every physical unknown can be solved by tonight, and do not trade correctness for a deadline. If desk work reaches a real external blocker, deliver the exact bounded decision or experiment immediately and say the layer remains blocked. Continue other P0 work in the same layer; do not restart downstream work.

Deliver one connected, independently checked power candidate and its honest gate verdict. Then advance layer by layer under these rules.


---

## 16. Review of the P0 execution plan: proceed after four targeted amendments (calibration and layout bounds need a feasibility basis; the integration order and one combined base; preserve work and start engineering beside the clerical work; the external closure path made actionable) (as received)

# MeshSat P0 execution plan — targeted review and amendment

## Decision

**Proceed after the targeted amendments below. Keep the P0 plan; do not start another planning cycle.**

The proposed allocation follows the owner's intent: stop current assignments, preserve their work, give F01 an author, confine three workers to the connected power design, retain independent checking, and pause downstream layers.

The source is still an approval-stage plan. It explicitly says nothing has been stopped yet. This review does not establish that any worker has stopped or any circuit has been corrected.

## Evidence and scope

Reviewed the active plan in `Pasted text(20261005-123653).txt`, lines 11–169, dated 5 October 2026, 14:35 CEST. The superseded appendix is historical context, not an active task queue.

Source SHA-256: `771502d31632d84d60e57b65994f30e80151a7b0c016a9f2563fe68c5de82cff`.

This is a dependency and execution-plan review. I have not independently inspected the named branches, component specifications, calculations, command implementations or V6 report. The numerical margins and proposed circuit alternatives remain unverified here.

## Required amendments

### 1. Calibration and layout targets need a supported feasibility basis

**P1 — verification gap.** P0-1 proposes replacing a detector's missing printed accuracy with per-unit calibration and a Layer 12 test row (lines 60–68). P0-2 similarly proposes plane-resistance bounds, and section 7 carries a layout bound as a condition (lines 69–73, 153–156).

These can be legitimate engineering routes, but writing a calibration procedure or a resistance target does not demonstrate that the design can meet it. Before crediting a correction, establish the calibration uncertainty and applicable operating envelope, and the realizability of the proposed conductor geometry. Account for relevant drift, temperature, tolerances and interconnections in the actual acceptance bound.

If a measurement is needed to decide whether the architecture is feasible, retain the architecture blocker. If conservative evidence already establishes feasibility and a later test merely verifies production implementation, record that narrower qualification obligation. Do not reject calibration as a method; do not treat a future calibration as a completed proof.

**Acceptance:** the author and checker can identify the evidence establishing the claimed bound and which remaining tests confirm implementation rather than decide feasibility.

### 2. Correct the integration order and align the authors' inputs

**P1 — confirmed ordering inconsistency, plus an input-consistency risk.** P0-6 is described as final composition on the frozen candidate (lines 85–86), while Slot A is assigned P0-1, P0-2, P0-6 and then P0-7 (lines 113–115). This places the final composition before the solar-guard work it must include. Slot C also starts from a different branch base (lines 123–128).

Complete the selected solar-guard correction and all other material P0 changes before final composition, independent acceptance and freeze. Perform useful composition checks incrementally, but call only the complete result final. Give both authors the same verified combined baseline, including round 16, or explicitly bring the required selected inputs into each branch before editing them. Keep the shared case definitions under one writer with clear handoffs.

**Acceptance:** the final candidate contains every selected correction, the check evaluates that combined state, and no technical correction is scheduled after its final composition or acceptance.

### 3. Preserve actual work and shorten the administrative critical path

**P2 — checkpoint and scheduling gap.** The recovery step lists tips, statuses and untracked files without explicitly backing up the modified file contents. The serial estimates are 20 minutes for stopping, 25 for the list and 15 for briefs, while the first checkpoint at 30 minutes promises assignments and a reproduction (lines 38–49, 160–166).

Save staged/unstaged diffs and relevant untracked contents, in addition to metadata. Stop the relevant parent/launcher processes as well as their children so they cannot relaunch work. Record the observed state at the time of stopping.

After the safe checkpoint and essential baseline verification, launch the first F01 reproduction and CAN task. The coordinator can finish register formatting alongside that work. Use the 30-minute checkpoint to report what has actually happened; do not wait an hour to start engineering merely to finish administrative text.

**Acceptance:** interrupted work is recoverable, no cancelled assignment is running or scheduled to relaunch, and the first checkpoint distinguishes completed recovery from active engineering and remaining setup.

### 4. Make the external closure path actionable immediately

**P2 — completion dependency.** The plan explicitly expects U-01, U-02 and U-04 to keep Layer 4 blocked even after its estimated 12–16 hours of desk work (lines 94–99, 134–142, 163–167). That is honest, but it is not an ETA for full Layer 4 closure.

At the first checkpoint, state for each claimed architecture blocker: the exact missing fact; why existing evidence does not establish it; the concrete owner decision or specimen/measurement needed; expected cost if known, or how the quote will be obtained; and who must provide the capability. Reuse the existing engineering work. Do not assume a supplier has accepted the job, and do not send requests or make purchases without authorisation.

Include P0-7 in the remaining desk schedule. Keep the estimate for a checked desk candidate separate from the unknown date for full closure. Strict layer order means downstream layers remain paused if an architecture-defining external fact remains unresolved.

## Paste into Claude's plan feedback

```text
Keep this P0 plan and make only these bounded amendments before the normal execution handoff. Do not start another broad planning round.

1. Calibration and layout bounds are proposed means of correction, not evidence by themselves. For P0-1, establish the calibration uncertainty and valid operating envelope before claiming an accuracy bound. For P0-2, demonstrate that the resistance bound is physically realizable with the selected geometry and tolerances. If a measurement decides feasibility, the Layer 4 blocker remains open; a Layer 12 row or layout constraint cannot close it by declaration.

2. Correct Slot A's order: P0-7 and every other selected technical correction must precede final P0-6 composition, independent acceptance and freeze. Both authors must use the same verified combined inputs, including round 16, before editing. Keep one writer for the common operating-case definitions. Early composition checks are useful; only the complete candidate is final.

3. The stop checkpoint must preserve modified file contents and staged/unstaged diffs, not just tips/status lists. Stop launchers as well as children. Once that checkpoint and the essential baseline verification are complete, start F01 and the CAN correction while the coordinator finishes clerical register work. The first checkpoint reports actual progress; it is not a reason to delay engineering for a full hour.

4. At the first checkpoint, make U-01/U-02/U-04 actionable: exact missing fact, existing evidence gap, concrete decision or measurement, required capability, and cost/quote status. Keep correspondence unsent and purchases unauthorised. Include P0-7 in the estimate. State clearly that 12–16 hours estimates a checked desk candidate, not full Layer 4 closure while external architecture blockers remain.

Then execute the approved stop-and-preserve step and the P0 assignments. Preserve the three-worker limit, strict layer order, independent acceptance and the original owner requirements. Do not soften any gate or restart the cancelled queue.
```


---

## 17. Second review of the revised plan: READY to approve for execution; the baseline watchpoint; 14 to 18 h is a desk candidate, not Layer 4's closure (as received)

# MeshSat P0 — revised plan check

## Decision

**READY to approve for execution.** The revised plan addresses the four requested amendments. No further planning round is needed on those points.

This verdict concerns the execution plan. It does not accept the power design, verify the proposed calculations or authorise fabrication, purchases or external messages. Power closure remains blocked as the plan reports.

## Scope

Reviewed the active plan in `Pasted text(20261005-124452).txt`, particularly its revised recovery, correction, assignment and timing sections. The superseded appendix remains historical context.

Source SHA-256: `39fe02a9a439f023529b6877b821e331fc96de3584176f825e3927b9a06dec15`.

Method: compared the revised text with the four amendments in the preceding plan review. No repository operations, hardware calculations, test runs, vendor claims or process states were independently verified here.

## Amendment check

| Requested change | Revised evidence | Result |
|---|---|---|
| Calibration and layout targets need a supported feasibility basis. | Lines 76–92 require calibration uncertainty and operating-envelope evidence, realizable conductor geometry and hot-corner resistance. A measurement that decides feasibility keeps the Layer 4 finding open. | Addressed in the plan; engineering proof still owed. |
| Solar correction must precede final composition, with consistent author inputs. | Lines 104–112 make P0-6 final only after P0-7 and all selected corrections. Lines 132–160 establish a common combined baseline and one writer for shared case definitions. | Addressed in the plan; integration still owed. |
| Preserve actual unfinished work and start engineering alongside clerical work. | Lines 43–60 explicitly preserve staged/unstaged diffs and untracked contents, stop parents/children, check for relaunches, and start F01/CAN work after the checkpoint and essential baseline preparation. | Addressed in the plan; checkpoint and launch evidence still owed. |
| Make external closure dependencies actionable and distinguish desk work from full closure. | Lines 188–205 require missing facts, specimens/limits, capability, owner and cost/quotation status at the first checkpoint. The revised estimate includes P0-7 and labels the result a desk candidate. | Addressed in the plan; decision packets and external evidence still owed. |

## What should happen next

Approve execution through Claude's existing handoff. The first checkpoint, about 30 minutes after approval, should show:

1. Which old assignments are stopped and where their recoverable work is saved.
2. The verified combined baseline and actual status of the F01 and CAN tasks.
3. The next concrete engineering artifact, with any setup delay identified.
4. Actionable U-01, U-02 and U-04 dependencies, with E11-29's qualification obligation kept distinct.

The first checkpoint is an observation of progress, not a promise that every preparation step must already be finished. The plan itself estimates about 40 minutes for stopping, baseline preparation and launch.

One execution watchpoint: if baseline checks fail on a known defect that the P0 authors are assigned to fix, distinguish that from a new merge regression. Preserve the failing result and its owner; do not weaken a test or let the need for an initially green baseline create a circular wait for its own correction. Investigate this only if it actually occurs.

## Timing and remaining limits

The estimate is now **14–18 hours for a connected, independently checked desk candidate**, conditional on the anticipated review outcome. That estimate has not been validated by this review.

Full Layer 4 closure has no supported completion date in the plan: U-01, U-02 and U-04 are still identified as architecture-level external dependencies. Under the owner's strict sequence, Layers 5–12 stay paused while such blockers remain unresolved, except for explicitly named prerequisites of the active gate.

The report says the firmware box jobs finished, but their review remains incomplete. Saving those results preserves work; it does not produce a firmware verdict or justify restarting that cancelled task now.

The next useful evidence is execution and a corrected circuit candidate, rather than another revision of this plan.

---

## 18. Review of P0 checkpoint 1: continue the authors; finish the external decision packet (U-02's per-mode reconciliation and the mock-up's sum, U-04's evidence route apart from the whole-kit release, U-01's two kinds of evidence) (as received)

# MeshSat P0 checkpoint 1 — review

## Decision

**Continue the current P0 authors. No new plan or worker restart is needed.** The checkpoint reports the intended change in allocation: previous work preserved, rented compute stopped, a common power baseline established, and two authors on F01/all-transmit and CAN fault corrections. Astra is correctly shown as queued until there is a selection to assess.

No new power correction is yet reported as independently accepted. Power-design closure and fabrication release remain BLOCKED.

## Evidence and scope

Source: `MESHSAT-P0-CHECKPOINT-1-2026-10-05-1530.md`.

SHA-256: `270de3a1e12283bd057d61dc2b7653497aa7da4b41888856942170385bcbc846`.

I reviewed the checkpoint against the approved execution plan. I did not inspect the remote processes, backups, repository, V6 report, datasheets or test procedures. Process states and test results below are the coordinator's reported evidence, not independently observed execution.

## Execution follow-through

| Commitment | Checkpoint evidence | Assessment |
|---|---|---|
| Stop and preserve previous work | Lines 6–15 report saved outputs, worktree snapshots, dirty-worktree diffs/untracked files, no remaining jobs or relaunches, and the box stopped with its disk retained. | Reported complete. |
| Use a common power baseline | Lines 19–21 identify `e132db0e`, the merged inputs and 227 passing tests with one known failure. | Suitable as an explicitly imperfect working baseline; it is not an accepted release. The assigned failure must be corrected before the applicable acceptance gate. |
| Prioritise actual power corrections | Lines 27–42 assign F01 first to Slot A and CAN faults first to Slot C. Both are reported active from 15:20. | Matches the approved priority. |
| Preserve independent review | Slot B is not launched because it awaits a committed selection. | Matches the plan; no reason to create unrelated work to fill the slot. |
| Separate desk progress from closure | Lines 44–50 retain external blockers and distinguish the 14–18-hour desk estimate. | Honest distinction; the estimate is not a Layer 4 completion date. |

The next substantive artifacts are the F01 comparison/selection and CAN fault analysis. The reported two-to-three-hour estimates place those around **17:20–18:20 CEST on 5 October**, subject to actual progress.

## Finish the external decision packet alongside the engineering

### Thermal: show what the proposed measurement can resolve

**Verification gap in the decision packet; not a new confirmed circuit defect.** U-02 reports a modelled conductance range of 1.22–2.85 W/K, mode thresholds up to 2.905 W/K, a 7.758 W/K e-paper line, and four lines above modelled capacity (line 57).

A measurement can test that model, but the packet does not demonstrate that the proposed case will pass every required mode. The model's upper estimate is not a proven physical maximum, so these figures also do not establish impossibility.

Before asking the owner to fund the mock-up, point to the existing per-mode reconciliation: the applicable requirement and component limit, the assumed heat path, the predicted result, what T-H1 would decide, and the next action if it fails. Distinguish a missing storage specification from a heat-rejection design problem. Reuse the existing analysis; do not reopen an already resolved row without evidence.

**Decision check:** the owner understands whether the spend confirms a supported route, screens an uncertain route, or measures a design currently predicted to miss a limit.

### Charger: separate a controlled evidence build from whole-kit release

**P1 completion risk.** U-04 says a prototype board A could supply the required evidence, while also saying its fabrication is blocked by the gate that evidence supports (line 58). The evaluation-module alternative is named but not yet costed or established as representative in this checkpoint.

Select and specify a suitable evaluation-module arrangement or limited prototype/coupon route. State what it represents, what evidence transfers to the final circuit, what remains layout-specific, and what supplier capability and owner authorisation are needed. A limited evidence build needs its own engineering review and controlled test plan; it does not authorise whole-kit fabrication or energising an unresolved hazardous path.

**Decision check:** at least one concrete evidence route can be authorised without first requiring the whole-kit release it is intended to inform. Procurement and physical work remain unauthorised until the owner approves them.

### Costs and the cell experiment still need decision preparation

**P2 preparation gap.** The U-02 parts are not summed and the text offers a desk quote "on request"; the U-04 evaluation-module price has not been read. Preparing those figures was already part of the approved checkpoint. The coordinator should finish the public-source estimates without another owner prompt, marking estimates and unknown lab costs explicitly. Requests to outside organisations remain unsent.

Keep the U-01 routes distinct: a manufacturer's warranted operating envelope and an experiment on one cell provide different evidence. A single-cell result is scoped to that specimen and its tested conditions. It does not by itself establish pack-level behaviour, fit, production variation or a manufacturer guarantee. State exactly which architecture decision the limited sample run can support and which conditions remain.

## Optional short message to the coordinator

```text
Continue Slots A and C unchanged; keep Astra queued for the committed selection. Do not restart the plan or the cancelled work.

Alongside the engineering, finish the external decision packet already requested:
- U-02: cite the existing per-mode thermal reconciliation. Explain what T-H1 can establish and what happens if it fails, especially for the four lines above modelled capacity. Sum the mock-up parts and give a dated estimate without waiting for another request.
- U-04: specify and cost a representative evaluation-module or controlled prototype/coupon route. Separate its authorisation from whole-kit fabrication release so the test does not depend on the release it is intended to support. Keep the required engineering review, test controls and owner approval explicit.
- U-01: distinguish manufacturer-guaranteed limits from evidence on one tested cell, and state what remains unproven at pack level.

These are coordinator follow-ups within the existing P0 scope. No purchase or external contact is authorised. The next engineering milestone remains F01's selection and the corrected CAN fault analysis.
```

---

## 19. Handover scope amendment and review of the external packet: the deliverable is the desk engineering package for a receiving company; sequential DESK acceptance per layer; the packet reframed as the supplier validation annex with three corrections (a failed arrangement is not a requirements conflict; the mock-up sum; investigating the Saft option apart from adopting it) (as received)

# MeshSat — handover scope amendment and external packet review

## Decision

**Keep this packet as a draft supplier-validation annex. Update its purpose and owner-action section to reflect the owner's clarified goal. Continue the current P0 authors.**

The project deliverable is the most complete, internally consistent engineering package achievable through desk engineering, modelling, simulation and review, for a receiving company to complete, test and qualify. The owner is not commissioning these experiments as a prerequisite to receiving that package.

The packet follows the earlier brief asking for owner decisions and costs. That earlier instruction needs a narrow amendment. Physical evidence remains necessary for the claims it supports, but obtaining it must not be a blanket condition for completing the engineering handover.

## Scope and evidence

Reviewed `MESHSAT-EXTERNAL-DECISION-PACKET-2026-10-05.md`.

SHA-256: `7b123e7ee479ac8358dcbead5f76dabb8276c78c9198ff00cedadce79cc89241`.

Checked its scope against the owner's clarification, its decision logic, and the arithmetic of its mock-up table. I have not independently verified the datasheets, market prices, exchange rate, thermal calculations, coupon design or executable test procedures. No physical work or external contact was performed.

## Findings and corrections

### 1. Reframe the packet as company handover work

**P1 — scope/gate correction.** Sections 1–5 repeatedly assign purchases, a bench and physical work to the owner, while section 5 explicitly asks for test/build authorisations. Under the clarified mission, these become proposed receiving-company activities, with capability and engagement still to be confirmed.

Retain the specimens, limits, dependencies, estimates and possible evidence routes. Present them as the supplier's review and validation scope, not actions the owner must complete before desk deliverables can progress. Cost estimates are supporting information; they are not an acceptance gate for the handover.

Maintain separate states:

- **Layer desk package:** whether its editable design, analysis, internal consistency, reviews and supplier handover are complete within the declared scope.
- **Design/qualification:** open defects, provisional choices, unverified assumptions and supplier validation still required.
- **Fabrication release:** the separate approval gate, which remains blocked where its criteria are unmet.

Do not erase architecture uncertainty by changing a label. Where a future measurement could change a component, topology, mechanical arrangement or layout, identify the affected outputs and keep them provisional. Complete stable work and document the remaining decision. A known desk-fixable failure still needs correction; the supplier annex is not a way to close it.

### 2. A failed arrangement does not establish a requirements conflict

**P1 — confirmed decision-logic defect.** The M1/M2 discussion and the paragraph at lines 29–35 say a measured over-temperature with the heat-rejection route fitted becomes a demonstrated conflict and an owner requirement question.

Such a result would demonstrate that the tested arrangement fails the applicable limit under those conditions. It would not, by itself, establish that the owner's requirements are mutually incompatible or that every permitted engineering route is exhausted.

Correct the disposition to: reject or revise that arrangement, assess the remaining permitted routes, and request a requirement change only when the evidence shows why one is necessary or the owner is being offered an explicit trade-off. Keep modelled shortfalls, missing vendor specifications and measured failures distinct.

### 3. Correct the mock-up subtotal

**P2 — confirmed arithmetic inconsistency.** Using the table's own rounded EUR figures, with stand-in fans and two loggers:

| Listed items | EUR |
|---|---:|
| Panel frame | 37.08 |
| Plate | 30–60 |
| Stack heaters | 15–30 |
| PA patch block | 10–20 |
| Stand-in fans | 199 |
| Two loggers | 820 |
| Thermocouples | 80–160 |
| **Subtotal** | **1,191.08–1,326.08** |

This differs from the packet's EUR 1,100–1,250. With one logger, the same arithmetic gives **EUR 781.08–916.08**, rather than EUR 700–850.

These are internal arithmetic corrections, not independently verified quotations. They exclude the already-paid case, any missing bench instruments, labour, delivery and unresolved tax treatment. Equipment substitutions also need a stated effect on what the test represents; a cheaper fan is not automatically equivalent for thermal evidence.

### 4. Separate investigating the Saft route from adopting it

**P2 — decision ambiguity.** Section 3 identifies a proposed 4S1P route and refers to adoption under OW-3; section 5 asks for OW-3 while also saying no pack change is requested.

State separately whether an action authorises a request for evidence, a limited experiment, or adoption of a different pack configuration. The handover may contain the Saft option as a proposal without treating it as adopted. Preserve the existing owner-approved pack baseline until an actual change is authorised.

The revised distinction between one-cell screening and a manufacturer guarantee is useful and should remain. Likewise, retain the charger evaluation-module/coupon alternatives and their transfer limits; this review does not certify either setup as executable.

## Ready-to-paste scope amendment for Claude Code

```text
Clarification of the project's deliverable: prepare the most complete, internally consistent engineering files and analysis we can hand to a company for completion, physical validation and manufacturing. We are not undertaking or funding the physical validation now.

This supersedes the earlier blanket instruction to pause all later layers until supplier-only measurements or vendor replies have arrived. It does not authorise a requirement change, a purchase, outside contact, fabrication or energisation.

Continue the current P0 authors and their independent checks. Do not restart them or the cancelled queue. Fix every remaining desk-solvable power defect and check the connected design. Keep P0 as the priority.

Keep sequential layer-by-layer DESK acceptance. Each layer's handover must contain coherent editable sources, calculations/simulations, review evidence and clearly scoped outstanding supplier work. After that scoped desk gate passes, advance to the next layer. Keep physical qualification and fabrication-release gates separate and honest; do not relabel them as passed.

For an unresolved measurement or vendor fact, identify the claim it supports, the affected files/decisions, a bounded provisional choice where possible, and the supplier's validation or redesign task. Complete stable portions; mark dependent portions provisional. Do not claim unconditional completion of a design that still depends on an unknown. Do not park a solvable circuit defect in the supplier list to make a desk gate pass.

Reframe MESHSAT-EXTERNAL-DECISION-PACKET as the SUPPLIER VALIDATION AND REMAINING ENGINEERING annex. Remove the expectation that I supply a bench, buy test equipment, book tests or answer procurement questions before handover. Retain the useful specimens, acceptance limits, dependencies and labelled estimates for the receiving company. Its engineering and lab capabilities remain to be confirmed; no supplier is assumed engaged.

Correct these specific points in the normal coordinator update:
1. A thermal failure of the tested arrangement is a design failure, not automatically a conflict in my requirements. Assess compliant alternatives before requesting a requirement change.
2. Recalculate the mock-up total from the listed items: approximately EUR 1,191–1,326 with two loggers, or EUR 781–916 with one, before the stated exclusions. Preserve the estimates/quotation distinction.
3. Distinguish investigating or testing the Saft option from adopting its 4S1P pack. No pack change has been approved by this clarification.

Apply this as a narrow scope amendment in the existing plan, records and worker briefs. No new constitution, general review round or laboratory procurement workstream. The next engineering deliverables remain the F01 correction and CAN fault analysis.
```
