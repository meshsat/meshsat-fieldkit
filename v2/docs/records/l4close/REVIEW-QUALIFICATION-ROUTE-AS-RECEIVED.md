# MeshSat: qualification-route review and continuation prompt

Reviewed 3 October 2026. Engineering scope: correctness, useful handover, dependency management and efficient continuation after the usage-limit interruption.

## Review conclusion

**The snapshot improves the route forward, but it does not establish power-design closure.** It gives an engineer concrete experiments instead of asking another model to manufacture physical evidence. The next step is to recover the interrupted work, consolidate its actual results, and finish the layer deliverables that those results support.

The status supported by this snapshot is:

| Decision | Assessment |
|---|---|
| Start an engineer's review | Yes, as a provisional package with omissions declared |
| Selected power architecture | Conditional |
| Power-design closure | Blocked by the stated protection and feasibility conditions |
| Fabrication release | Blocked |
| Continue independent interface, component, mechanical and schematic work | Yes, within their dependencies and existing authorisations |

This is not a recommendation to repeat the completed investigations or to wait for every physical measurement before producing any further design.

## What I verified

Archive: `MESHSAT-L4-QUALIFICATION-ROUTE-SNAPSHOT-2c240414.zip`.

SHA-256: `9d67e3a9bae90aca34ab0518c9b4fcd5abc00e091afdeaaf6ee25724e3d2ea28`.

- All **149 manifest entries match**; the extraction has 150 files including the manifest.
- All **9 supplied Python files parse**. This is syntax verification, not execution or electrical validation.
- I read the qualification route, relevant power and protection sections, downstream register, findings ledger and affected draft scripts, and compared them with the preceding external reviews.
- The README identifies a **provisional, unreviewed integration snapshot**, `2c240414`, cut at 00:15 CEST on 3 October. It predates the later fixes in your interruption transcript.
- The main numerical producers, their tests, release records, current interface registry and `LAYER5-HANDOVER.md` are absent. I did not replay the power models, run the project suite, verify Git ancestry or inspect today's live branches.

All file-and-line references below are relative to the archive root. Later commits are identified from your transcript, not independently inspected here.

## Progress and remaining findings

| Item | What the supplied files establish | What the resumed session should do |
|---|---|---|
| Prototype/release circularity | `l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md:1425–1440` now permits scoped evidence builds separately from final release. `l4e9/L4-POWER-ARCHITECTURE.md:661–688` names specimens, decisions and dependencies. | Use this route; verify that the working release process distinguishes a prototype from a production release. Do not bypass existing guards. |
| L4-CP03: withdrawn FET claims | The actual `_PAIR` text in `l4e11/apply_gen_sch_a_charger.py:50–66` now states an allowance, a self-plus-mutual target, and no diode-sharing credit. | Textual correction confirmed in this snapshot. Verify composition with the latest drafts rather than commissioning another broad review. |
| L4-CP01: eFuse fault envelope | Section 17a adds the four fault cases, but still calls 566 A a ceiling and carries a broad 1.5 s claim (`l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md:1374–1395`). | Your transcript reports these corrected at `b929d8be`, including intermittent shorts and contact temperature. Confirm those changes reached the integrated candidate; do not redo them from this older ZIP. |
| L4-CP02: docking pulse | Section 17b explicitly withdraws temperature-only permission and selects a six-sample waveform qualification, with a precharge alternative (`:1398–1415`). | This defines work; it is not a passed experiment. Preserve its sample-limited scope and the fallback. |
| Solar guard | The snapshot retains a 3.30 µH loop condition and a 0.240 V target; lower-inductance examples fail its model (`l4e7/L4E7-CONTROL-DECISION.md:580–639`). | Recover round 5's newer connector-fault and sense-model work. Neither the old floor nor a cable-spacing estimate qualifies a different source/fault arrangement. |
| Thermal wording and e-paper soak | The snapshot still contains the earlier escalation wording and +55/+60 °C specimen (`l4e9/L4-POWER-ARCHITECTURE.md:687,728`). | Your transcript reports `22cb4c16` correcting escalation and specifying +70 °C on the glass. Check propagation, not another restart. |
| Findings count | `l4close/FINDINGS-LEDGER.md:38–48,203–221` distinguishes 22 closed, 21 closed as conditional, 11 open downstream and 4 still open, out of 58 rows. | Those are snapshot counts. Report current dispositions; never interpret “58 inventory items” as 58 unresolved blockers or “conditional” as verified hardware. |

Paths in this table sit under `v2/docs/records/`.

### L4-QR01 — Tighten what an experiment can qualify

**P1; high confidence in the written overreach, no claim of hardware failure.**

The E11-29 transfer rule says a coupon's thermal result transfers when the final board has at least its copper area, layer count, copper weight and via field. See `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:676` and `l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md:1433`.

Those quantities alone do not establish an equivalent thermal environment. Device spacing, copper connectivity, neighbouring heat sources, airflow and enclosure coupling can change the installed result. TI's [Semiconductor and IC Package Thermal Metrics, §1](https://www.ti.com/lit/an/spra953c/spra953c.pdf) supports this distinction: junction-to-ambient performance depends on the board and environment, not just the device.

Also, the docking row describes pulse capability as layout-independent, whereas section 17b correctly says a sample result is not a production limit (`L4-POWER-ARCHITECTURE.md:677`; `L4E11-SOURCE-ONLY-AND-ENTRY.md:1410–1414,1434`). The broad transfer wording needs the same qualification. Nexperia's [AN11158, §2.4](https://assets.nexperia.com/documents/application-note/AN11158.pdf) explains that limiting values apply under their stated conditions; a prototype test does not extend the manufacturer's guarantee.

**Correction and acceptance:** the test owner records the specimen, lot, waveform, mounting and thermal boundaries, measurement uncertainty, permitted extrapolation and what requires re-test. A final-board comparison must justify any claimed conservative equivalence. Keep the six-sample proposal as prototype evidence unless a separately justified qualification basis supports more. This correction blocks unsupported acceptance, not preparation of the coupon or unrelated layers.

### L4-QR02 — Fix the pack-fit dependency

**P2; confirmed internal inconsistency.**

The Saft qualification row says adoption also needs the fit mock-up. The fit row then says it blocks nothing: `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:684,686`.

**Correction and acceptance:** R-167 blocks adoption of that proposed pack arrangement and dependent mechanical release; it does not block baseline A1 work or unrelated interfaces. Represent that edge consistently in the existing register. No new scheduling framework is needed.

### Handover limitation

The architecture page points to `LAYER5-HANDOVER.md` at lines 584–586, but that file is absent. Its absence from this ZIP is **not proof it is absent from the repository**. It does mean this snapshot alone is insufficient for a new engineer to take over the interface work or reproduce the numerical outputs.

The next small handover should include the current Layer 5 contract, selected component table, referenced local calculations and inputs, and an omissions list. It does not need the entire Git history. The included September battery packet should remain labelled with its own revision and applicability, rather than appearing to prove the latest charger/pack integration.

## Prompt to paste into the existing Claude Code session

Resume the approved MeshSat plan now. The usage limit is resolved. Continue the existing work into concrete, reviewable layer deliverables; do not restart the project, open another planning cycle, or wait for a further review from this chat.

### 1. Recover the actual state, then dispatch

Read the current execution plan, owner brief, integration notes and stopped authors' checkpoints. Verify branch tips, uncommitted files and live child processes. The supplied qualification snapshot `2c240414` is older than the latest transcript; use the repository as the authority.

Preserve completed work reported at `6a1b6851`, `b929d8be` and `22cb4c16`. Confirm their presence and propagation instead of reimplementing their corrections.

Keep the two-worker limit and one author per branch. Verify the effective model for newly resumed workers; do not assume changing the coordinator's model revived failed children.

- **Slot A:** recover L4-E7 round 5, including the connector fault, margin claim, sense-model rectification and R96. Check whether the numerical subprocess survived the agent's quota failure. Keep a healthy run; reuse completed results only when input fingerprints and exit status match. Resume from the last valid checkpoint otherwise. Preserve failed and partial outputs as diagnostics, never accepted evidence.
- **Slot B:** recover the interrupted `l8gnd` work on GND-002 and HOT-R1's SLOT_EN hold. Preserve its edits and finish the composition checks against the current power drafts. These are schematic changes supporting Layer 5 interfaces; they are not permission to begin general PCB routing.

If either task has already finished, take its next dependent task. If the harness cannot resume a dead worker safely, start one replacement from its checkpoint after confirming no other author owns that branch.

### 2. Finish set 27 without another general review loop

Integrate the remaining L4-E9 consolidation and ledger work after L4-E7 lands. Use the existing safe regeneration helper; never overwrite an accepted output with a refused or partial run. Keep each result tied to its actual inputs and revision.

Apply this snapshot review narrowly:

- Make coupon-to-board transfer depend on justified electrical and thermal equivalence. A larger copper area alone is insufficient. Keep sample results scoped to their specimens, lots and conditions.
- Make R-167 block the proposed pack's adoption and dependent mechanical release, not unrelated work.
- Confirm the later eFuse target wording, fan designators, +70 °C glass soak, escalation rule and provenance fixes are present. Do not reopen already-corrected history.
- Preserve the new connector-fault result if design margins remain NOT MET. Separate a missed design target from an absolute-rating violation; neither becomes PASS by renaming it.

Use the targeted verification already authorised, including the coordinator's explicitly labelled check where that is the approved next step. Preserve Astra's original verdicts. A quota reset or exhausted review allowance does not close a finding or authorise unlimited new reviews. If a material correction remains unsupported, state the exact blocked decision and hand it to the engineer or named experiment.

Run affected checks during integration and the required suite on the frozen release candidate. Reuse valid unchanged evidence; repeat tests only for a changed dependency or required gate. Promote the truthful candidate under the existing authority, keeping prototype, conditional-design and fabrication statuses separate.

### 3. Continue naturally through the layer deliverables

The purpose of the layered approach is a design an engineer can take over. Finish the earliest ready deliverable in the existing layer plan. When an external dependency blocks one item, immediately work on an independent item, preferably in the earliest unfinished layer.

| Layer | Required next deliverable |
|---|---|
| **4 — System architecture** | A coherent architecture, operating/fault states, connected power diagram, consistent energy and heat budgets, selected changes, qualification route and exact unresolved decisions. Check the whole layer's existing scope: the power packet alone does not complete system architecture. |
| **5 — Partitioning and interfaces** | Finish the actual interface documents and HW/FW contract: both ends of each changed power/control interface, limits, grounding, startup/shutdown, SLOT_EN, fault behaviour and ownership. Carry implementation obligations into Layer 8; do not require built boards merely to finish a supported interface specification. |
| **6 — Component selection** | Complete the decision-critical selections and BOM evidence first: exact parts/packages, pin maps, operating envelopes, derating, alternatives and qualification dependencies. Separate selected, proposed and qualified. Keep pack substitutions subject to existing owner rulings. |
| **7 — Mechanical** | Produce the editable enclosure, pack, harness, cooling and specimen drawings with dimensions and tolerances. Separate supported design from fit/thermal measurements still owed. |
| **8 — Schematics** | Compose the authorised drafts, generate the affected schematics and netlists, and check cross-board electrical consistency and ERC. Prioritise the changes needed by Layer 5 and the qualification specimens. |
| **9 onward** | Complete supported analyses and test procedures; prepare controlled evidence prototypes where permitted. Begin final layout only when the relevant board's entry conditions pass, then manufacturing-package checks. |

Use the existing acceptance criteria. A handed-off condition is not a verified result. Mark a layer COMPLETE only when its defined deliverable is complete and its material decision conditions are satisfied; otherwise state precisely what is complete and what remains conditional. Do not hold every later work item behind a global Layer 4 flag.

### 4. Keep autonomy and evidence disciplined

Preserve Layers 1–3 and the owner brief: battery and solar, no external battery, HF and tablet retained, and 48–72 hours as an objective under its stated profile. Optional tablet charging reduces endurance. Do not silently change the solar window, service profile, enclosure or pack ruling to manufacture a pass.

For a missing physical fact, finish its practical specimen/procedure and decision consequence, then stop repeating desk analysis on unchanged inputs. New desk work must correct a specific error, add relevant evidence or evaluate a defined design change. A failed candidate does not prove every compliant architecture impossible.

Prepare the prototype route under its own existing authorisation; retain final-release holds. Purchases, vendor contact and physical tests need their applicable permissions. Ask only for an action that truly needs the owner, with its consequence, while continuing unaffected work.

Keep one current execution plan and the existing registers. Avoid new ledgers, repeated prose and heavyweight exports. Each completed layer needs a concise handover index, editable sources, supporting evidence and explicit remaining dependencies. Export compact review files without full repository history.

Reuse paused compute when useful; stop instances after two hours of genuine idle time and preserve their disks. Do not treat a healthy long calculation as idle. No new spend cap is introduced.

Give a short recovery update once both slots are assigned: actual task/process, recovered revision, next artifact and measured or estimated time. Subsequently report artifacts completed, decisions changed and the next critical dependency. Separate engineering ETA from vendor/bench waiting. Continue automatically after set 27 into the next ready layer task.

**The next milestone is a committed set 27 with honest dispositions and useful Layer 5/6 deliverables progressing—not another assertion that power is solved.**
