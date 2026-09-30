# The owner's instructions of 30 September 2026: finish layer 3 for the current target, and his review of the draft table

MESHSAT-1357. Filed on 30 September 2026 by the author of layer 3's second requirements issue (L3-R2, branch
`fnd/l3r2`), so that the registry's owner rulings D-21 and D-22 and the pages of this folder cite a file rather than
a conversation. Prototype design: no V2 board has been fabricated, ordered, assembled or powered, and no kit has been field
deployed.

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
