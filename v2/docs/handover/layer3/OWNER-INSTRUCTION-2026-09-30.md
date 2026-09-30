# The owner's instructions of 30 September 2026: finish layer 3 for the current target, and his review of the draft table

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

## How this work reads it (the session's reading, not the owner's words)

- **"Battery and solar remain mandatory"**: mission M1 is carried by the kit's own store and its solar input. An
  external DC source stays optional and is never M1's basis (D-20, 28 September 2026).
- **"the approved 72-hour mission"**: M1's 72 hours, first taken by the session as SC-21 and preserved with M1's
  duration and operating conditions by D-20, is read as approved by the owner.
- **"approved functions"**: every function the owner approved, among them the lid functions of appendix 32.50 item 16a
  (the QMX HF set in its lid tray) and item 16d (the lid tablet bracket), which D-01 defers from prototype 1's
  acceptance but does not withdraw. Removing one of them from the kit needs his explicit authorisation.
- **"Recommendations are not approvals"**: every session recommendation made since handover H3 is recorded as
  AWAITING until the owner's own words approve or reject it; the only statuses given here without his words are
  WITHDRAWN (a session's own edit reverted) and NOT A REQUIREMENT CHANGE.
- **"100%"**: the four conditions of the completion gate, each stated on `REQUIREMENTS-L3-R2.md` with its state. A
  planned test is never marked passed, and no circuit or physical test is made a condition of the requirements
  document.
- **The review of the draft table**: rows L3-OD1, L3-OD2 and L3-OD4 are held until the corrected, independently checked
  energy comparison is filed (open item S-127); no energy figure is shown as the design's before it; "typical" and
  "adverse" are not used until the energy basis names its cases by their exact weather and operating assumptions; every
  narrower angle, function or condition is a row the owner decides; and every option that moves an item out of the lid
  states where its function goes, a function leaving the kit being the owner's explicit decision.
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
