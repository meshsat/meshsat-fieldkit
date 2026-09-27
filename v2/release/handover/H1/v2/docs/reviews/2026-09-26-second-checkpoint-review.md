<!-- Review of the progress report of 26 September 2026 22:35 CEST (MESHSAT-1357), supplied by the owner on
     26 September 2026 about 22:48 CEST. Recorded verbatim below, except that its em dashes are replaced by colons and
     its en dashes by "to" (house style). The report it reviews is kept in the project's internal record. Its execution
     is logged in v2/docs/EXECUTION-PLAN.md, as the first review's was. -->

# MeshSat V2 progress review: second checkpoint, 26 September 2026

**Reviewed:** `MESHSAT-V2-progress-and-methodology-2026-09-26-2235.md`, status 22:35 CEST, reported public commit `2aaa7b7f`. Compared with the 13:05 report, the preceding review, and the foundation-first plan of 25 September.

## Assessment

**The layered approach is producing useful engineering progress. Continue it, with changes to how work is scheduled and gates are applied.** During this 9½-hour reporting interval, Claude reports further circuit corrections, restored secondary temperature sensing, a requirements/architecture candidate, and a much more honest separation of historical results from current evidence.

Those are material improvements. They have also exposed the real remaining work: thermal feasibility, hardware radio inhibition, failover circuitry, part compatibility, and current verification. The project remains in design recovery: **0 of 6 architecture blockers closed, 0 boards ready for layout, 0 physically verified.**

The next improvement should be shorter paths from known findings to reviewed circuit fixes. Section 8 unnecessarily places several independent electrical tasks behind a long tool-integration queue. Some gates also form a circular dependency that prevents the work needed to satisfy them.

**Scope:** this is a review of the supplied report, its internal consistency, and progress against our plan. Retrieval of the cited GitHub revision failed; I have not independently audited its schematics, commits, test logs or calculations. Targeted TI and Eaton documents were checked. Reported corrections remain reported, rather than independently verified here. This review does not approve a board or pack for fabrication.

## 1. Progress since the previous checkpoint

| Area | Reported change | Assessment |
|---|---|---|
| Circuit correction | A, B and D corrections merged and regenerated; B grows from 931 to 1,103 components | Substantial engineering work. A correction stream's approval must remain distinct from approval of the entire board while functional defects remain. |
| Battery protection | Fixed resistor withdrawn; separate secondary thermistor restored | Necessary improvement. Temperature thresholds and protection coordination remain unresolved. |
| Requirements and architecture | 131 records and architecture candidate merged; 36 open items | Useful foundation for consistent decisions. Draft acceptance and feasibility remain open. |
| Evidence integrity | Mixed-revision 212/333 headline replaced by explicit evidence classes | Major reporting improvement. Per-board pages still need the same labeling. |
| Power budget | Unsupported share of typical load reportedly falls from 49% to 19% | Meaningful reduction in uncertainty. Thermal sensitivity still changes the feasibility conclusion. |
| Board B experiment | Six- and eight-layer arms running on the same older region | Useful bounded learning. It is not a route of the corrected whole board. |
| Parallel execution | Separate authors/checkers and one integrator are active | Agent parallelism is now evident. Current scheduling still serializes work unnecessarily. |
| Physical and external work | Review packets and experiments specified; no review contracted or bench hardware bought | These dependencies are visible but have not advanced into execution. |

The public evidence page still has only eight current-candidate readings: six registry-completeness checks and two on E5. The proposed 49 current-candidate readings in the integration tree are **not yet public results and are not 49 passes**; four reportedly identify real design failures.

## 2. Priority findings

### A. Separate layout-entry holds from fabrication-release holds

**Report references:** sections 3.1, 4.8 and 5.

Decision 31's proposed hold requires a corrected layout and SCH-002 PASS before lifting. Layout entry requires that hold to be absent. This is an explicit deadlock for A, D and E.

Use stage-specific acceptance:

- **Layout entry:** reviewed protection topology, exact fitted parts, corrected schematic, owned interfaces, and placement/return-path constraints.
- **Fabrication release:** the actual PCB implements that schematic and passes the applicable physical protection and parity checks.
- **Prototype verification:** the specified physical tests demonstrate the required behavior.

Keep the fabrication hold until its evidence exists. Permit the work necessary to produce that evidence once its own prerequisites are satisfied. This changes when a check applies; it does not waive protection.

INT-002 has a related problem: it is classified as a schematic gate but is expected to close through a test on the first built B. Separate a defensible pre-layout assessment of the proposed Ethernet connection from its later physical verification. Moving the test to a later phase does not, by itself, establish that the proposed circuit is viable.

Review all six feasibility blockers for the same distinction. A development-board test can legitimately gate a risky architecture decision. A test requiring the final PCB cannot also prevent designing that PCB. Record the acceptance criteria in the existing authoritative plan/registry; the report says some currently exist only in this narrative.

### B. Restored temperature sensing does not close the battery/thermal problem

**Report references:** sections 4.2 and 4.3.

The secondary protection's reported trip window is **62.7 to 77.5°C**, while the report uses a **60°C cell limit**. Its pessimistic thermal model reaches **81°C at +20°C ambient**.

This does not prove every pack state is unsafe: the primary protection and PTC may act earlier, and a secondary emergency threshold can serve a different purpose from an operating limit. It does mean that this secondary circuit has not been shown to enforce the stated cell limit. The review must establish coordinated thresholds, tolerances, sensor placement/lag, operating mode, and behavior when the primary path fails.

TI documents thermistor-based over-temperature protection and threshold accuracy for BQ77207 [R1]. That supports the sensing mechanism, not the adequacy of this complete pack design.

Eaton lists operation at −20 to +60°C, storage at −10 to +40°C, and a separate +105°C/1,000-hour environmental test [R2]. The report appropriately labels its shelf-storage interpretation as an inference. The conclusion that the fuse is suitable whenever the cells meet their rating is still unsupported: the report itself leaves the fuse's local hot condition and current behavior unresolved.

Prioritize the qualified battery review and the bounded enclosure heat experiment before freezing affected placement and pack design. The proposal to remove the pack for the +71°C storage test changes the tested configuration and operating procedure; reconcile it explicitly with the intended product requirement. Do not select a qualification condition merely because the current circuit can pass it.

### C. Hardware EMCON remains an unresolved architecture requirement

**Report references:** sections 4.3 and 4.8.

The report describes MCU pins capable of overriding the shared inhibit line. It also describes a 5G shutdown path with at least 15.9 seconds plus software reaction time. A lower bound plus an unbounded software response is not a guaranteed maximum shutdown time under controller failure.

Define the required maximum latency and fault conditions, then establish a dominant hardware inhibit path for each transmitter. Verify reset, unpowered-controller and back-powering states. If the proposed shutdown mechanism still requires functioning firmware in the failure case, it does not satisfy the stated hardware-only requirement.

A hardware supply switch may be part of the remedy, but its presence alone does not establish a complete solution: control authority, remaining energy, alternate supply paths and shutdown behavior must be accounted for.

The “30 W PA closed at desk” statement also needs scope clarification: a local PA circuit can be correct while its upstream shared enable line remains defective. Report local and end-to-end conclusions separately.

### D. Two evidence defects can recreate false confidence on the next run

**Report references:** sections 2, 3.2, 3.5 and 3.6.

1. **Known part mismatches are corrected manually in output.** Fourteen rows were marked WRONG_MODEL, but `jlc_certify.py` would certify them again. Put the exact known mismatches and supported compatibility decisions into authoritative machine-readable inputs consumed by the checker. Re-running certification must preserve their unresolved status.

2. **Tool provenance omits imported helpers.** Hashing only the verdict-writing script, with a commit-date fallback for older results, does not establish that the calculation or matching logic is unchanged. Fingerprint the relevant checking code, including local helpers, rules, configuration and tool versions. A conservative code-bundle hash is sufficient initially; a new dependency platform is unnecessary.

Add focused regression checks for these actual failure modes: an unresolved mismatch survives regeneration, and a changed helper invalidates an affected prior verdict.

The latest runner suite skipped KiCad-dependent tests. The cited host suite ran on an earlier mixed tree. After merging the relevant changes, run the affected KiCad checks and final acceptance gates on one identified integrated candidate. The report's proposed clean-clone re-take is appropriate; do not describe the earlier host result as validation of the latest commit.

### E. Board B has promising experimental evidence with a narrow scope

**Report references:** sections 1, 4.5 and 4.9.

At equal pass count:

| Comparison | Six layers | Eight layers |
|---|---:|---:|
| Initial open connections | 290 | 290 |
| After pass 3 | 84 | 40 |
| After pass 5 | 66 | 29 |

This supports continuing the bounded eight-layer investigation. It does not establish completion, equal-runtime performance, or feasibility of the corrected full board:

- The trial uses pre-correction B21, while the new schematic has 1,103 components instead of 931.
- Eight layers is approaching a plateau around 28 open connections.
- The diagnosed floor-plan detours and escape collisions are separate obstacles; more layers need not remove them.
- The six-layer inner-pair impedance result is already outside the stated target.

Finish the capped experiment and record its limited conclusion. Then test the actual critical escape/placement remedy against corrected inputs and an acceptable stackup. Do not multiply expensive whole-board jobs before identifying which remaining connections fail and why.

The 57-minute modal stall also means the old “no pass in four hours” observation cannot automatically be treated as algorithmic difficulty. Separate input loading, blocked UI time and active routing time in future comparisons.

### F. Fix unattended routing without blindly accepting import warnings

**Report reference:** section 4.9.

Matching the modal window is an improvement over assuming an idle JVM has stopped accumulating CPU time. However, automatically pressing Return on a “DSN file reader” warning should require understanding that warning.

Capture its exact content, allow only a known harmless continuation, and confirm that required connectivity and constraints survived import. Fail or escalate unknown import failures. Validate the recovery against the reproduced stall and use stage progress/timeouts as well as process liveness.

This is a concrete reliability fix with an immediate payoff. It is more useful than adding hosts that reproduce the same blocked import.

### G. Reorder execution around real dependencies

**Report reference:** section 8.

The listed sequence waits for the tool streams and RF-002, performs a full re-take, fixes holds, builds packets, and only then starts several already identified circuit corrections. RF-002 is on its tenth pass.

Continue parallel work within file ownership and integration constraints:

| Workstream | Work that can proceed | Real dependency |
|---|---|---|
| Evidence/tools | Provenance, mismatch persistence, phase/hold corrections | Final acceptance depends on a trustworthy result or an approved, pinned review method |
| Electrical circuits | EMCON remedies, FAB-01 to 04, address conflict, E corrections | Shared generator edits require one owner or coordinated patches |
| Decoupling/stackups | Per-part requirements, generator corrections, C/P stack definitions | Final placement checks need regenerated geometry |
| Feasibility | Conclude B trial; prepare ZEROIZE and thermal experiments | Running physical experiments needs devices, equipment and authorization |
| External review | Complete current review packets and costed requests | Contact and spending remain outside Claude's stated authority |

Authoring an electrical correction need not wait for a general-purpose checker to converge. A source-backed, pinned circuit review can support authoring and, where the agreed criteria allow it, acceptance. It must not be relabeled as an automated PASS.

Use targeted checks while iterating and the required integrated gates on the candidate. Avoid repeated broad re-takes of revisions already scheduled for immediate replacement.

The report does not establish a shortage of compute: utilization is unmeasured, spending is about $3.48, and a significant delay was a UI stall. Increase compute where a measured independent workload benefits. Complete a costed, ready-to-act packet for the reviewer engagements and development hardware; then request only the authorization still genuinely missing. Continue unrelated engineering meanwhile.

## 3. Other corrections worth making now

- **Mechanical margins:** doubling an assumed allowance is a sensitivity test, not proof that an unspecified manufacturing tolerance is bounded. Keep that qualification attached to the 35 MET rows. The two negative margins should explicitly say that the currently assumed geometry fails, with final plug selection pending. Perform the targeted mock-up before affected PCB outlines and connector placements become expensive to change, rather than waiting until boards are ready for population.
- **Part sources:** 42 cited maker documents still need to be filed. Prioritize sources needed to reproduce critical circuit and rating reviews; the source index itself does not validate a part.
- **Review packets:** D and P packets are already superseded. Issue the packet for each actual review candidate and label obsolete versions clearly. The current battery candidate is the relevant P input.
- **Reporting:** label the historical percentages on every generated board page. Preserve the distinction between a current reading, a passing reading, a desk review and a physical result.
- **Forecast:** about one week to the first eligible C is an unvalidated planning judgment. Show its actual dependency chain and the revised parallel schedule. External review and hardware lead times must remain visible in any end-to-end forecast, even when reported separately from internal engineering time.

## 4. Responses to the report's seven reviewer questions

These are directions for the next engineering step, not approval of unseen circuits.

| Question | Review response |
|---|---|
| Pack protection and fuse interpretation | Restoring the thermistor is appropriate. Adequacy remains unproven given the temperature window, shared protection elements and fuse uncertainties. Resolve through the actual candidate review and targeted evidence. |
| Charger with a crashed host | Do not adopt “charges safely” as a verified result. TI documents the watchdog-current behavior and host-controlled termination [R3]; the complete protection/configuration sequence remains a project obligation. A prototype may deliberately stop charging after controller failure if that meets its requirements. Continued autonomous charging needs its own demonstrated protection behavior. |
| Hardware EMCON | Require a bounded hardware path under the specified fault states. Software-dependent reaction is insufficient for the hardware-only claim. Choose the circuit from that requirement, then test its end-to-end behavior. |
| Failover fabric | Correct the reported strap, back-powering, switching-order and pull-down defects. A 2-of-3 concept can be considered, but 202 correct endpoint mappings and a voting truth table do not establish fault tolerance. Check the defined fault model and shared dependencies. |
| ZEROIZE | The bounded development-device experiment is the right next step. Nine software fixtures do not prove silicon permissions, interrupted-power behavior or the quoted worst-case timing. Do not switch parts solely to escape uncertainty without checking the alternative's documentation, interfaces and availability. The 1,000-trial statistical bound assumes the sampled failure model; it is not proof against every interruption timing. |
| Board B | Complete the current capped comparison; use the remaining failures to choose the next experiment. Correct known floor-plan/escape problems, and confirm the stackup. Consider via-in-pad only if the identified bottleneck calls for it and the manufacturing process supports it. |
| Decoupling | Per-part and per-class treatment is the appropriate direction. Absence of a universal 3 mm rule is not permission for arbitrary placement. Retain source-backed capacitance, loop/return geometry and connection requirements, followed by placement checks. |

## 5. What the next checkpoint should deliver

1. **A committed, current evidence re-take** with known mismatch persistence and helper provenance addressed, or their affected results explicitly held.
2. **No circular layout-entry gates:** decision 31 and INT-002 allocated to appropriate stages without weakening their technical requirements.
3. **Reviewed circuit fixes moving in parallel** for EMCON, failover, address conflicts, E and decoupling; each tied to the regenerated candidate.
4. **A concluded B experiment** stating what it establishes, what it does not, and the single next useful feasibility test.
5. **A ready-to-act external/bench packet:** current design files, review scope, supplier/reviewer options, costs, lead times and exact authorization needed.
6. **A per-board path into layout** ranked by genuine dependencies. E5, E and C should be assessed individually; an unrelated Board B problem must not automatically hold them.
7. **Measured progress:** critical blockers closed, current evidence obtained, useful experiments completed, active compute time and spend.

The reset has already improved the design review and exposed faults before fabrication. The remaining risk is allowing verification-tool development and procedural holds to dominate the schedule. Continue the layered work while making every gate stage-appropriate and every independent circuit task runnable.

## Official references checked

- **R1: Texas Instruments, BQ77207, SLUSEG7D, May 2026:** thermistor-based temperature protection, device options and accuracy. https://www.ti.com/lit/gpn/BQ77207
- **R2: Eaton, SCF9550, ELX1135, January 2022:** general specifications, page 4. https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-scf9550-self-control-fuse-data-sheet-elx1135-en.pdf
- **R3: Texas Instruments, BQ25731, SLUSE66A:** sections 9.3.21.1 and 9.4.1, watchdog and host charging control. https://www.ti.com/lit/ds/symlink/bq25731.pdf
