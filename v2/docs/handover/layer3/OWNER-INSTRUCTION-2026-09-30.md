# The owner's instructions of 30 September 2026: finish layer 3 for the current target, and his review of the draft table

## Current owner brief (read this first; kept under D-31)

The one authoritative interpretation both agents read first (D-30, D-31); each line names the ruling that carries it,
quoted below and recorded in `v2/ecad/tools/pcb_requirements.yaml` (`owner_rulings`). Recommendations and earlier model
statements are not owner approval (D-31).

**Constraints.** (1) Battery storage inside the Peli 1450; NO external battery (D-28; row L3-OD7, D-32; REQ-014).
(2) Battery and solar required (D-20, D-21, D-28; REQ-014, REQ-016). (3) HF and the tablet functions kept, the QMX set
and the tablet bracket in the lid (D-28; row L3-OD2, D-33; REQ-002, REQ-011). (4) 48 to 72 hours is a baseline design
objective under a stated operating profile, not a mandatory minimum (D-28; D-32; REQ-072, the only design objective).
(5) Optional tablet charging consumes the kit's energy and reduces endurance, below the target included; no daily
schedule is mandatory, the 36 Wh a day illustrative (D-28; REQ-011). (6) Every other explicitly approved requirement
unchanged, REQ-016's solar window among them (D-28; row L3-OD3, D-34); a proposed change to approved operating
conditions stays an owner decision (D-31).

**Mandatory requirements:** every requirement record but REQ-072, the constraints above and CFL-017's temperature
requirements among them, unchanged (D-28, D-29; row L3-OD5, D-36). **Design objectives:** REQ-072 (D-28).
**Modelling assumptions, not operating restrictions:** those of REQ-072's stated profile, and only those: PS-IDLE-SPEC,
42.8 W over 39 loads; HF available, not receiving; the tablet not charged; a full store aged to 80 percent; SC-37's
September mean day at Leiden on one plane, 40 degrees facing south, TYP, WAB a sensitivity (D-28; row L3-OD6, D-37); no
deployment condition, the single plane a benchmark (row L3-OD4, D-35). The registry's ASM records are not covered by
this line, each judged on its own record: ASM-006 carries owner ruling D-02e's operating condition "operate shaded",
which binds; ASM-002 carries D-03's accepted residual risk (the drive unlock's common modes); ASM-005 is a technical
assumption about the secure element written from D-03; ASM-007 is the session's reading (SC-04) of the owner's "MIL-STD
if possible" for the pack; ASM-001 (SC-02), ASM-003 and ASM-004 are the session's or the model's; none of these four is
an owner-approved operating restriction. **Component selections, not owner requirements:** the Samsung INR18650-35E cell
that D-06's pack carries (D-29; D-36), the one replaceable selection these rulings establish. The registry's CHO records
are not covered by this line: CHO-001, the device set, is the owner's ruling of 6 September 2026 and binds ("Owner
rulings bind the picks; changing one is an owner decision"); CHO-003 rests on owner ruling D-16 (no vehicle surge
claim), its clamp part an engineering pick; CHO-002, the duplicated WiFi link card, cites no owner ruling, an
engineering selection. D-06's one 4S3P pack stands; Option A(i)'s two packs and the 2S2P solar stage are layer 4
proposals (row L3-OD1 closed as layer 4 architecture under D-21 and D-28).

**The honest state (D-28, D-31).** The present candidates miss the 48 to 72 hour objective even without tablet
charging: the studied in-case store stops the kit at 05 UTC of the first night (11 to 23 hours), as drawn and on the
hypothetical corrected path, and D-06's pack alone runs 2.52 h on battery; REQ-072 reads FAIL, design risk DR-01, layer
4. Open design obligations, all layer 4's: board A's power path as drawn fails, its corrections hypothetical and not
implemented (DR-02); the outlet's R138 trips below its 3 A contracts (DR-03); the solar interface (DR-04); three
undocumented efficiencies (DR-05); the cell and thermal design against the temperature requirements with the pack
fitted (FEA-008, DR-06); Option A(i)'s lid consequences (DR-07); each on `REQUIREMENTS-L3-R2.md` section 2.
Requirements completion stays apart from circuit, PCB, thermal, runtime and product verification (D-28, D-29).
**Owner decisions open:** none (D-29). **Owner approvals open:** the definition re-issue (L3-C26) and his acceptance
of the baseline, after the independent check.

**Superseded, kept in place below and marked there.** 72 hours as a mandatory minimum (SC-21, D-21's reading, D-27's
options), external battery options and the comparison's Options A and B, the ten-row recommendation string, rows
L3-OD1, L3-OD2 and L3-OD4 held (D-22 to D-24), and removing HF or the tablet bracket from the lid: by D-28. The
`reading-c` default for CFL-017: by D-29.

## This file

MESHSAT-1357. Filed on 30 September 2026 by the author of layer 3's second requirements issue (L3-R2, branch
`fnd/l3r2`), so that the registry's owner rulings D-21 and D-22 and the pages of this folder cite a file rather than
a conversation, and owner rulings D-23, D-24 and D-25 (the owner's instructions later the same day, the third to fifth
sections below).
Prototype design: no V2 board has been fabricated, ordered, assembled or powered, and no kit has been field deployed.

## Provenance

The text below is the owner's instruction of 30 September 2026 **as the coordinating session quoted it, in part, in the
brief it gave this work** ("The owner's instruction of 30 Sep 2026 is binding and is quoted in part here"). The three
elisions (`...`) are the coordinator's; nothing was added, reworded or reordered here. The full instruction is not held
in the repository. Where the part quoted here and the full text differ, the full text governs, and the registry's D-21
is re-read against it.

## The instruction, as quoted

**Superseded in part by D-28:** its "approved 72-hour mission" is a design objective of 48 to 72 hours, not a mandatory minimum.

> finish Layer 3, Requirements for the current target configuration before advancing Layer 4 ... Reconcile the actual
> target. Read the accepted H3 requirements, subsequent owner decisions and current proposals. For every
> requirement-changing proposal, record whether it is approved, rejected or awaiting a decision. Resolve REQ-016,
> battery/solar operating requirements, mission conditions, deployment restrictions and any affected functionality.
> Distinguish requirements from implementation choices that properly belong in later layers. Battery and solar remain
> mandatory. Preserve the approved 72-hour mission and approved functions unless I explicitly authorize a change.
> Recommendations are not approvals ... Deliver the consolidated, versioned requirements, with stable IDs, approved
> sources, operating conditions, measurable acceptance criteria, verification methods and traceability. Include the
> change record and downstream impacts. Preserve the original H3 release. An engineer must understand what to build
> and how success will be judged without reconstructing our conversations ... Layer 3 reaches 100% only when the target
> is unambiguous, requirement-changing owner decisions are resolved, contradictions and requirement-level TBDs are
> closed, and an independent check accepts the handover. Completed circuits and physical test results belong to later
> verification stages; do not make them prerequisites for completing the requirements document or mark planned tests
> as passed.

## The owner's review of the draft decision table (30 September 2026), as quoted

**Superseded in part by D-28:** the holds on rows L3-OD1, L3-OD2 and L3-OD4 end with the closure, the rows answered or closed.

Relayed by the coordinating session with the independent check of the first draft of L3-R2 (branch `fnd/l3r2` at
`9c26a641`, "accepted: no"), introduced as "the owner's review of the draft table (30 Sep 2026), which is binding". The
five paragraphs below are as quoted there, word for word; the registry records them as owner ruling D-22.

> "The voltage is an engineering input, not an author's preference. Establish the applicable supply range under load
> and temperature. If 19.08 V is permitted, mission claims must account for it. Independently check how voltage, current
> limits and losses affect the energy calculation."

> "Preserve your mission requirements. Narrower deployment angles, reduced functionality or different operating
> conditions must be proposed explicitly for your approval. They cannot become accepted requirements simply because they
> make this candidate pass."

> "Define 'adverse.' A model based on a September average day does not establish performance across unspecified adverse
> weather. The corrected table must identify the exact weather and operating assumptions."

> "Hold decisions 1, 2 and 4 until the corrected, independently checked comparison arrives. Battery and solar remain
> mandatory; moving equipment out of the lid must not silently remove its function from the kit."

> "The next useful result is one consistent decision table and an updated requirements package."

## The owner's instruction on the six-row decision table (30 September 2026), as quoted

**Superseded in part by D-28:** the rows it set out are answered or closed; the weather basis is D-28's stated profile.

Relayed by the coordinating session during the third round of L3-R2, introduced as "A correction to your round 3a, from
the owner's newest instruction (30 Sep 2026). It is binding." The four paragraphs below are as quoted there, word for
word; the two elisions (`...`) are the coordinator's. The registry records them as owner ruling D-23.

> "Changes to weather coverage, deployment restrictions, functionality or enclosure constraints remain proposals
> requiring my explicit decision. An average-day benchmark may be an option; do not select it automatically because the
> current design passes it."

> "Make weather decision 6 a quantified choice ... Substantiate 'several times more energy' before recommending against
> an option."

> "Update the existing six-row decision table with options, your recommendation, quantified consequences and
> dependencies. Put detailed calculations in the existing evidence package, linked from the table. Flag any option that
> cannot meet the stated mission plainly."

> "Keep the current-limit resistor dependency explicit ... Distinguish performance of the held circuit from performance
> conditional on the proposed change. Track implementation and physical verification separately."

## The owner's addendum on the power path and the decision package (30 September 2026), as quoted

Relayed by the coordinating session during round 3b of L3-R2, introduced as "An addendum to round 3b, from the owner (30
Sep 2026). It is binding". The paragraphs below are as quoted there, word for word; the one elision (`...`) is the
coordinator's, and the fourth paragraph is three quotations as the coordinator gave them. The registry records them as
owner ruling D-24.

> "Update decision 1's premise. The reported findings make this a power-path correction, potentially involving
> components, sensing, layout and thermal design. Stop presenting the 6.2 mOhm substitution as a sufficient solution. Keep
> findings provisional until independently checked, and distinguish: the circuit as drawn; the resistor-only proposal; any
> hypothetical corrected power path used for feasibility calculations."

> "Correct the energy claims ... Where a supportable power envelope is not established, label the result conditional or
> inconclusive. Preserve useful hypothetical calculations, but state the required circuit corrections prominently. Do not
> count energy available only through an inadequate power path as demonstrated capability."

> "Finish the concise decision package. Keep the existing six-row owner table. Show each option's checked figures,
> limitations, required changes and remaining uncertainties, with links to evidence. Retain the weather-coverage choices
> and quantified capacity/fit comparisons. Do not recommend an option as feasible solely because its idealised energy
> balance passes."

> "Close requirements without confusing them with implementation. Complete only the bounded feasibility work necessary for
> informed requirements decisions. Full circuit correction, layout and bench testing belong to subsequent layers." "Bring
> me decisions only when the proposed remedy changes mission requirements, functions, deployment conditions, enclosure
> constraints or approved resources." "Component selection and Kelvin routing are engineering tasks."

## The owner's corrections to round 3b (30 September 2026), as quoted

Relayed by the coordinating session during round 3b of L3-R2, introduced as "Three owner corrections for round 3b (30 Sep
2026). They are binding." The three paragraphs below are as quoted there, word for word. The registry records them as owner
ruling D-25.

> "Correct the Kelvin classification. The inspected A32 layout is historical evidence. It cannot establish a routing defect
> in the current board, which has no layout yet. Keep the A32 finding tied to that revision. Unless current
> schematic/netlist evidence independently establishes an error, record Kelvin sensing and the permitted shared resistance
> as implementation requirements with measurable verification criteria."

> "Describe the 4.05 A proposal accurately. Reducing the charger's input-current limit addresses current-limit
> coordination. It does not establish that the other electrical defects are resolved or that the mission succeeds. Show its
> energy consequence as a clearly labelled derated variant; preserve the actual as-drawn case. Keep the independently
> checked 0.378 A comparison closed unless relevant inputs change."

> "Restrict owner decisions to actual requirement changes. Charging below a source's available power is an engineering
> choice when approved requirements remain satisfied. Ask me only when the remedy changes an agreed mission condition,
> charging time, functionality, enclosure constraint or approved resources. Each such question must name the affected
> requirement and quantify the consequence. Component selection and sensing implementation remain engineering tasks."

## The owner's reviewer's review of the decision brief (30 September 2026), as quoted

**Superseded in part:** the third passage's environment table as CFL-017's route by D-29; the fourth and fifth passages go with Option A(i) to layer 4 (D-28).

The owner's reviewer reviewed the decision brief `MESHSAT-L3-OWNER-DECISIONS-2026-09-30.md` (sha256/16
`ca4a9dcfa2e076ff`, a laptop file, not in this tree), and the review is relayed as the owner's by the coordinating
session. Its verdict, as relayed: "CONDITIONAL for individual owner choices; BLOCKED for blanket approval or a claim
that the revised Layer 3 baseline is fully validated". No owner answer to the six rows has been given. The six
paragraphs below are as quoted there, word for word. The registry records them as owner ruling D-26.

> "Separate owner-selected requirements from candidate compliance. A combination can be a valid target and have a FAIL
> or INCONCLUSIVE implementation. Retain rejection of genuinely contradictory requirements and all release gates. Verify
> that recording HF retention plus WAB does not fabricate a PASS or silently change the requirement."

> "Define the criterion at the kit loads: the specified service continues for 72 hours within voltage, power and pack
> limits. Combined stored Wh alone is insufficient. Reference exact initial state, load profile, panel orientation,
> installation, cutoff and power-path case. State whether a single exact orientation is the benchmark when no deployment
> band is established."

> "Supply the selected cell/pack limits and a mode-specific environment table. Distinguish battery-fitted operation from
> cell-free qualification/storage. Owner acceptance must cover the operational consequence. 'No cost' should not conceal
> reduced claimed capability."

> "A 10 N requirement can be proposed as a chosen design target. Specify application point, force direction/duration,
> slope, support surface, lid angle and load configuration. Cite the matching mechanical result before calling the
> candidate a modelled PASS."

> "Approve topology separately from electrical compliance. Pin the panel revision and datasheet; distinguish available
> array power, controlled converter input power, cold open-circuit exposure, short-circuit/fault currents and string
> versus combined-feed protection. Provide the rating derivation or an explicit engineering obligation rather than
> treating owner approval as verification."

> "Requirements drafted / decisions recorded: the intended product and its acceptance criteria are explicit.
> Requirements baseline validated and accepted: the chosen constraints have a credible feasibility basis, the identified
> gaps are resolved to the agreed review scope, and the owner has accepted the baseline. Design and hardware compliant:
> later circuit, layout and physical evidence demonstrate those requirements."

## The owner's addendum to round 5 (30 September 2026), as quoted

**Superseded by D-28:** the runtime is answered (48 to 72 hours, a design objective; no external battery; HF and the tablet kept).

Relayed by the coordinating session during layer 3's round 5, after the review above and before any owner answer to
the rows. The three paragraphs below are as quoted there, word for word; the first and the third are the coordinating
session's own words relaying the owner, the second is the owner's, quoted by it. The registry records them as owner
ruling D-27.

> "Round 5 addendum from the owner (30 Sep 2026). The owner is questioning the 72-hour requirement:"

> "Evaluate alternatives before asking me to sacrifice functions or accept restrictive deployment conditions."

> "He also said to preserve HF and the tablet functionality."

## The owner's clarification of the energy and runtime requirement (30 September 2026), as quoted

Relayed by the coordinating session to redirect layer 3's round 5 into its closure cycle, introduced as the owner's
clarification, "binding", which "supersedes earlier interpretations of the energy and runtime requirement". The five
paragraphs below are as quoted there, word for word, their omission marks included. The registry records them as owner
ruling D-28.

> "NO external battery. Battery storage stays inside the Peli 1450. Battery and solar remain required. Keep both HF
> and tablet functions. Optional tablet charging consumes the kit's available energy and reduces remaining runtime.
> That reduction is acceptable, including runtime falling below the baseline target. I am NOT requiring unchanged
> runtime while charging the tablet, a full tablet recharge every day, or an additional battery to compensate. The
> previous 36 Wh/day charging case can remain an illustrative calculation. It is not an approved mandatory daily
> charging schedule. Do not reopen external storage or removal of either function as the recommended solution."

> "Treat 48-72 hours as the baseline design target under an explicitly stated operating profile, not an unconditional
> guarantee under every combination of loads and weather. Do not elevate 72 hours into a mandatory minimum. Identify
> the essential loads, radio duty cycles, starting charge, battery assumptions and solar conditions used. Separate
> battery-only and solar-assisted results. Keep modelling assumptions distinct from owner-approved operating
> restrictions. State plainly that optional charging and additional use reduce endurance. Define charging capability
> within electrical and protection limits; a particular tablet model is not required merely to specify that
> capability. Report the actual modelled baseline runtime honestly. If the present candidate misses the target even
> without tablet charging, record that shortfall prominently. Do not hide it, invent a passing configuration, or
> describe hypothetical circuit corrections as implemented."

> "Layer 3 is complete when the requirements package is coherent, traceable, measurable, internally consistent and
> ready for an engineer to use. Every mandatory requirement and design objective must be distinguishable and have
> acceptance conditions and a verification method. Include the available feasibility evidence and clearly assigned
> unresolved design risks. A failed current implementation is not automatically a defective requirement. Conversely,
> do not conceal a demonstrated incompatibility between mandatory requirements by calling it downstream work. Layer 3
> completion does not mean the circuit, PCB, thermal performance, runtime or physical product has passed verification.
> Keep those statuses separate."

> "Use the existing analysis and records. Have the author reconcile the affected requirements, decision register,
> acceptance criteria and handover package. Preserve other approved requirements; do not silently adopt the earlier
> ten-row recommendation string. ... Do not restart broad reviews or commission another battery comparison merely
> because optional charging reduces runtime."

> "If a genuine unresolved owner decision prevents closure, finish everything else and identify only the exact
> conflicting requirement and decision needed. Do not manufacture 100% completion, but do not keep us in review loops
> over an ordinary, explicitly accepted runtime trade-off."

## The owner's clarification of CFL-017 (30 September 2026), as quoted

Relayed by the coordinating session into the same closure pass. The two paragraphs below are as quoted there, word
for word, their omission mark included. The registry records them as owner ruling D-29.

> "For CFL-017, distinguish mandatory product requirements from the limitations of the currently selected Samsung 35E
> cells. 1. Establish whether that exact cell model is an owner-mandated constraint or an engineering selection. A
> mismatch with a replaceable component does not, by itself, prove that the product requirements contradict each
> other. 2. Separate charging, battery-powered operation and storage. Use the project's exact manufacturer
> specification and distinguish ambient temperature, cell temperature, storage duration and whether batteries are
> fitted. Do not treat one temperature limit as applying to every mode. 3. Do not automatically adopt 'the extremes
> apply without cells,' reduce an approved temperature requirement, or reclassify it as an objective. Those would
> change the product requirements and need my explicit decision. 4. Where the requirements are coherent but the
> current component cannot meet them, record a Layer 4 component-selection/thermal-design obligation with its
> feasibility uncertainty and measurable closure criterion. Do not claim that an alternative component or thermal
> solution has already been proven."

> "If a genuine contradiction between mandatory owner requirements remains, name the exact conflicting requirements
> and ask only the decision needed to resolve it. Otherwise, close the Layer 3 requirements baseline, preserve all
> unresolved engineering obligations explicitly ... Requirements completion must remain separate from demonstrated
> hardware compliance."

## The owner's instruction on the Codex worker and the decision register (30 September 2026), as quoted

Relayed by the coordinating session into layer 3's closure pass, to be recorded in the decision register; it changes
no requirement. The paragraph below is as quoted there, word for word, its omission marks included. The registry
records it as owner ruling D-30. From this instruction on, this file together with the registry's `owner_rulings`
(`v2/ecad/tools/pcb_requirements.yaml`) is the one decision register both agents consult; the Codex worker's side of it
is `v2/docs/CODEX-WORKER.md` section 7 (on main since `7e4b7a87`).

> "Upgrade the existing Codex/GPT-6-Astra integration from a limited pilot to a standing engineering collaborator. ...
> This authorises further bounded Astra assignments through the existing ChatGPT authentication and available
> subscription allowance. It replaces the exhausted pilot-call count. Preserve existing spending, sandbox and
> publication limits; no automatic paid-API fallback. Claude remains the coordinator and integrator. ... Both agents
> must consult the same authoritative decision register. Record my latest instructions there so I do not have to relay
> them repeatedly. ... Astra cannot change my requirements or approve its own authored work. Agreement between agents
> is not a substitute for calculations, sources or tests. Keep at most two active workers across Claude and Codex,
> with one author per worktree."

## The owner's operating instruction: one authoritative interpretation (30 September 2026), as quoted

Relayed by the coordinating session into layer 3's closure pass as binding. The two paragraphs below are as quoted
there, word for word. The registry records them as owner ruling D-31. The current owner brief at the top of this
file is kept under it.

> "Maintain one authoritative interpretation of the product. Keep a concise current owner brief in the existing
> decision register, with links to the original decisions. Both Claude and Astra must use it. The current constraints
> are: Battery storage inside the Peli 1450; NO external battery. Battery and solar required; HF and tablet retained.
> 48-72 hours is a baseline design objective under a stated operating profile. Optional tablet charging consumes
> available energy and reduces endurance, including below that target. All other explicitly approved requirements
> remain unchanged. Separate mandatory requirements, objectives, assumptions and component selections. Recommendations
> and previous model statements are not owner approval. Resolve superseded operational instructions in place while
> preserving decision history."

> "Requirements closure means a coherent, traceable, measurable baseline with verification methods and an honest
> feasibility assessment. Record the current energy shortfall and other unresolved design obligations prominently. Do
> not describe hypothetical corrections as implemented or verified. For CFL-017, distinguish selected-cell limitations
> from mandatory product constraints, and charging from operation and storage. Any proposed change to approved
> operating conditions remains an owner decision."

## How this work reads it (the session's reading, not the owner's words)

- **"Battery and solar remain mandatory"**: mission M1 is carried by the kit's own store and its solar input. An
  external DC source stays optional and is never M1's basis (D-20, 28 September 2026).
- **"the approved 72-hour mission"**: M1's 72 hours, first taken by the session as SC-21 and preserved with M1's
  duration and operating conditions by D-20, is read as approved by the owner. **Superseded by D-28.**
- **"approved functions"**: every function the owner approved, among them the lid functions of appendix 32.50 item 16a
  (the QMX HF set in its lid tray) and item 16d (the lid tablet bracket), which D-01 defers from prototype 1's
  acceptance but does not withdraw. Removing one of them from the kit needs his explicit authorisation.
- **"Recommendations are not approvals"**: every session recommendation made since handover H3 is recorded as
  AWAITING until the owner's own words approve or reject it; the only statuses given here without his words are
  WITHDRAWN (a session's own edit reverted) and NOT A REQUIREMENT CHANGE.
- **"100%"**: the conditions of the completion gate, each stated on `REQUIREMENTS-L3-R2.md` with its state (four,
  and a fifth since D-26: every recorded target has a feasibility disposition). A planned test is never marked passed,
  and no circuit or physical test is made a condition of the requirements document.
- **The review of the draft table**: rows L3-OD1, L3-OD2 and L3-OD4 are held until the corrected, independently checked
  energy comparison is filed (open item S-127); no energy figure is shown as the design's before it; "typical" and
  "adverse" are not used until the energy basis names its cases by their exact weather and operating assumptions; every
  narrower angle, function or condition is a row the owner decides; and every option that moves an item out of the lid
  states where its function goes, a function leaving the kit being the owner's explicit decision. **Superseded by D-28 (the closure).**
- **The instruction on the six-row table (D-23)**: weather coverage, deployment restrictions, functionality and
  enclosure constraints change only by the owner's explicit decision, each a row or an option he answers. Row L3-OD6
  (M1's weather basis) is a quantified choice between the average-day benchmark, its limitations stated, and
  historical-coverage targets, each with the store it needs, its mass and volume and whether it fits; its recommendation
  and figures are held until the checked energy basis gives them, and the benchmark is never taken because the current
  design passes it. Each row carries its options, the recommendation, quantified consequences with links to the
  evidence, and its dependencies, and an option that cannot meet M1 says so in plain words. Board A's current-limit
  resistor R11 is carried as two results: the circuit as generated (R11 10 mOhm) and the result conditional on the
  drafted 6.2 mOhm; the change's implementation (layer 8) and its physical verification (prototype) are tracked as two
  downstream items, neither a layer 3 prerequisite.
- **The addendum on the power path (D-24)**: every result that depends on board A's front end is stated in three cases,
  never merged: (a) the circuit as drawn (R11 10 mOhm), where no lid meets M1; (b) the resistor-only proposal (R11 6.2
  mOhm), which is not presented as a sufficient solution and whose result reads CONDITIONAL or INCONCLUSIVE until the
  electrical check says otherwise; (c) a hypothetical corrected power path used for the feasibility figures, with the
  corrections it assumes listed beside every figure that rests on it. Energy available only through (c) is hypothetical,
  never demonstrated capability. The corrections (component selection, Kelvin routing, the inductor, the thermal path, the
  200 W stage, the input limit per source) are engineering tasks, tracked as downstream closure items with measurable
  criteria; a row goes to the owner only where a remedy would change a mission requirement, a function, a deployment
  condition, an enclosure constraint or an approved resource. No option is recommended as feasible because its idealised
  energy balance passes.
- **The corrections to round 3b (D-25)**: Kelvin sensing at R11 and the permitted shared resistance are implementation
  requirements with measurable verification criteria; the A32 layout reading stays tied to that revision and establishes
  no defect of the current board, which has no layout, and the current netlist shows none. Board A's front end is stated in
  four cases: (a) as drawn; (a') a derated variant with U3's input limit at 4.05 A or less, labelled as fixing current-limit
  coordination only, never as resolving the other findings or meeting M1; (b) the resistor-only proposal, conditional; (c) a
  hypothetical corrected power path. The independently checked 0.378 A comparison stays closed unless its inputs change.
  Each owner row names the requirement it changes and quantifies the consequence; charging below a source's available
  power, component selection and sensing implementation are engineering tasks while the approved requirements hold.
- **The review (D-26)**: a row's answer records the owner's REQUIREMENT TARGET; the studied candidate's COMPLIANCE is
  shown beside it (PASS on a named case, FAIL by how much, INCONCLUSIVE with what is missing, CONDITIONAL on which
  corrections), and a target the candidate does not meet records an open feasibility item instead of being refused. Only
  requirements that cannot both hold are refused. Mission M1's pass line is at the kit loads, with the reference case
  stated exactly; the push and the slope of the open kit are design targets with their test conditions; the solar
  topology is approved apart from its electrical compliance, which carries its derivations or obligations; and the pages
  say which of the reviewer's three status levels holds.
- **The addendum (D-27)**: M1's runtime and its store are themselves a row the owner answers, L3-OD7, before rows
  L3-OD1 (the store), L3-OD2 (the lid item), L3-OD4 (the deployment condition) and L3-OD6 (the weather basis), which
  depend on it, with HF and the tablet kept: 72 hours required (Option B) or 48 hours required with 72 desired (Option
  A); HF available or listening; an external battery arrangement joined at VBAT (reopening D-06) or through the DC entry
  (revisiting D-20), or none, M1 then recorded as not met; the tablet charged or not. No row asks him to remove a
  function or to accept a deployment condition before row L3-OD7 is answered, and the scripts of those four rows refuse
  until it is. Its figures are the bounded runtime and battery comparison of stream l3batt, filed with its accepted
  check. The 72 hours are the session's SC-21 (27 September 2026, under the standing rule), first appearing as SC-L2-05,
  which D-20 preserved with M1's specified duration without setting the figure, and which the reading of "the approved
  72-hour mission" above took as approved; the comparison's provenance record (`v2/docs/records/l3batt/PROVENANCE.md`)
  finds their provenance as the owner's UNVERIFIED, and the owner now questions them. **Superseded by D-28.**
- **The clarification of the energy and runtime requirement (D-28)**: mandatory, each with its acceptance and
  verification: the store inside the Peli 1450 with no external battery (REQ-014), battery and solar both present and
  working, the HF and tablet functions kept with the QMX set and the tablet bracket in the lid, and every other
  explicitly approved requirement unchanged, REQ-016 among them. A design objective: M1's 48 to 72 hours under REQ-072's
  stated profile, the registry's one record with `obligation: OBJECTIVE`, never a mandatory minimum; the tablet's
  charging is a capability at the USB-C outlet within its electrical and protection limits, optional, reducing
  endurance. The modelled baseline misses the objective's lower end even without tablet charging; it is stated as
  design risk DR-01 to layer 4 beside the others (DR-02 to DR-07), and the hypothetical power path corrections are never
  described as implemented. The earlier recommendations (the ten-row string, the consolidated message's Q1 to Q10) are
  not adopted: rows L3-OD2 to L3-OD7 are answered from his words (D-32 to D-37), row L3-OD1 is closed as layer 4
  architecture (D-06 stands, Option A(i) a layer 4 proposal needing his ruling there), and the open kit's stability
  (REQ-078 as drafted) goes with Option A(i)'s lid pack to layer 4.
- **The clarification of CFL-017 (D-29)**: the Samsung 35E is the current engineering selection, not an owner-mandated
  constraint (D-06 was ruled at the session's recommendation, and no ruling names the model as a product requirement;
  the quotes are in `l3r2.yaml`'s `cell_provenance`). The maker's limits are judged mode by mode (charging, discharge,
  storage by duration) against D-02, D-02a and TEST-PLAN E5 with the pack fitted, as cell temperature against ambient
  plus the inside-air rise. No temperature requirement is reduced or reclassified and reading (c) is not adopted; the
  collisions are between the requirements and the current cell, so CFL-017 closes as a requirements conflict and
  FEA-008 carries the layer 4 component-selection and thermal-design obligation, each mode with its gap, its
  uncertainty and its closure criterion (`cell_modes`, LO-01a to LO-01h). No genuine contradiction between mandatory
  requirements remains, so no owner decision is asked.
- **The Codex worker (D-30)**: it changes no requirement; this file and the registry's `owner_rulings` are the one
  decision register both agents consult, and nothing either agent authors is an approval.
- **One authoritative interpretation (D-31)**: the current owner brief at the top of this file is that interpretation;
  every line of it names the ruling that carries it, and an instruction a later ruling supersedes stays in place with a
  one-line mark naming that ruling.
