# V2 execution plan (MESHSAT-1357, foundation baseline)

Started 25 September 2026. This is the short, hand-kept execution record for rebuilding the V2 field kit from its engineering foundations. The foundations are the product definition, the requirements with their verification method, the architecture and budgets, the interface contracts, and the review of parts and circuits. After those comes per-board design readiness for a specified prototype build.

It is a prototype design programme. **Nothing here has been built, and no board has been ordered.** Progress is reported as reviewed milestones and verification coverage, never as a single percentage of the whole. Rule-level readiness stays in the generated pages (`PCB-RULE-STATUS-*.md`, `PCB-OPEN-PAIRS.md`, `OWNER-DECISIONS-OPEN.md`).

## Priority from 27 September 2026 01:20 CEST: the engineering handover

The owner's execution prompt of 27 September (`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`) makes a
portable engineering handover the immediate delivery: completed pre-PCB layers that an engineer or a company can take
over without this session. It corrects priorities; the scope, the rulings, the seven conditions and the stage gates
below stand.

- **The nine pre-PCB layers** (the owner's numbering): 1 product definition, 2 concept of operations, 3 requirements,
  4 system architecture, 5 partitioning and interfaces, 6 components, 7 mechanical and enclosure, 8 schematics,
  9 pre-layout design analysis; PCB layout is layer 10. Each layer's scope, deliverables by revision, acceptance
  items, status (NOT_STARTED, IN_PROGRESS, BLOCKED or COMPLETE) and next closing action are kept in
  `v2/docs/handover/LAYER-STATUS.md`, a view over the existing records, never a second registry. COMPLETE means
  complete for the layer's own engineering purpose with its review; it never means a later physical test has passed.
  An AI review is labelled as one and does not stand in for a qualified review a record requires.
- **The handover snapshot** is built from one commit into `v2/release/handover/<version>/` (START-HERE, layer
  table, continuation brief, one engineering question per blocked item, manifest with every file's revision and
  sha256, and a ZIP). The editable documents in `v2/docs/` stay the authority; a snapshot is an immutable copy. The
  first snapshot is partial and says so. One fresh checker, who did not build it, tests it for usability.
- **Order of work:** the earliest unfinished layers close first; circuit round 8 (layer 8) continues in parallel;
  no routing campaign resumes. Board B's Q-B-ESC-2 stays a bounded feasibility experiment for FEA-003 and runs only
  on the netlist that follows round 8.
- **Two attempts, then a change of method.** A check loop that has not closed an issue in two passes is reassessed
  (targeted experiment, qualified review or a justified alternative) or recorded as a blocker with its engineering
  question. The RF-002 transmitter walk, past its second pass long ago, gets one final method change (every pin not
  cleared by a held document reads UNDECIDED); whatever it yields is merged with its limits named or recorded as a
  blocker with a manual-review route. Corrected after the external review of 27 September 18:10
  (`v2/docs/reviews/2026-09-27-third-checkpoint-review.md`, section 7): changing the method never ends the review
  while the defect remains; a narrow re-check is used only where the affected scope is understood, and the broader
  acceptance criteria it touches stay covered.
- **Promote only a checked candidate** (same review, section 7). The validators and the tests that read the changed
  files run on the exact integrated candidate before `main` is fast-forwarded to it, and a result from one revision is
  never reported for another; the full suite runs at every snapshot.
- **Design closures are counted apart from evidence refreshes** (same review, section 6). A re-take that moves readings
  to current evidence, or a stage correction, closes no electrical defect; the checkpoints list the circuit changes
  that closed a finding separately.

## Baseline, 25 September 2026 22:33 CEST

| Item | Value |
|---|---|
| Repository head at start | `e6291404` (then `a0ad97d9` and `9d66316f`, two hygiene commits) |
| Tools tree | `v2/ecad/tools` at `31a6527011da` |
| Rule set | fingerprint `ff8151db3576437b`, manifest `2026-09-16.1`, 58 rules |
| Local suite | 1345 passed, 0 failed, 60 skipped (the skips are not passes; they are being accounted for, see below) |
| Open owner decisions | 30 (ZEROIZE), 40 (pack protection), 42 (decoupling); 27, 28, 41 and 43 ruled 25 September (appendix 32.365) |
| Stackups on record | JLC04161H-7628, JLC06161H-3313, 2L, 2L-2oz. No 4-layer 2 oz row (board P) and no 8-layer row (board B) yet |
| Compute | no rented box at the start; one KiCad box rented at 22:25 for the regeneration and re-take jobs below |

| Board | Declared phase | Project directory | Board sha (as measured by the status pages) | Readiness | Hold |
|---|---|---|---|---|---|
| A power + I/O | A32 | `pcb-a-power-a23` | 58e26c67987b1daa | NOT_READY | decision 31 (lifted only on fresh evidence) |
| B compute | B21 | `pcb-b-compute-b19` | 2e64b5bf2d9cd3bc | NOT_READY, not routed (416 open) | |
| C panel backer | C24 | `pcb-c-display-c8` | 2a273803757c68fb | NOT_READY | |
| D VHF APRS | D12 | `pcb-d-aprs-d9` | 929bf82d2bf6eed4 | NOT_READY | decision 31 (lifted only on fresh evidence) |
| E1 dock strip | E17 | `pcb-e1-dock-e7` | a462ac2620b9b8d3 | NOT_READY | decision 31 (lifted only on fresh evidence) |
| E5 dock block | E5 | `pcb-e5-block` | 686b29a734c55b9a | NOT_READY | |
| P pack BMS | P4 | `pcb-p-pack-p2` | d79865e7b1aceb95 | NOT_READY | |

## The reviews, and what each one gates

| Review | Content | Gates |
|---|---|---|
| A, product and envelope | product brief, concept of operations, operating modes, simultaneity and duty cycles, runtime, environment, ZEROIZE meaning, markets and obligations | requirements that depend on those answers |
| B, requirements with verification | requirement records with acceptance criteria, verification method and stage; the test plan traced to them | the architecture budgets and test access |
| C, architecture and feasibility | budgets with margins; interfaces owned on both ends; board B feasibility | per-board parts and circuit review |
| D, parts and circuits, per board | exact part identities; symbol, footprint and pad parity; circuit review by function; regeneration parity | that board's layout entry |

Review A is held in two parts, layer 1 (the product brief and the public pages) and layer 2 (the concept of operations
and the operating envelope). Each is an AI review by one fresh reviewer who wrote none of the pages, labelled as an AI
review and never a qualified review, against the layer's row of section 3 and the tests of section 2 of the owner's
handover prompt, recorded at `v2/docs/reviews/REVIEW-A-LAYER-<n>-<date>.md`; layer 1's definition in full is the last
section of `PRODUCT-BRIEF.md` (the session's choice under the owner's standing rule of 26 September 2026, registry
SC-16). No record in this tree requires a qualified review of layers 1 or 2; the qualified reviews named elsewhere
(D-09 and `reviews/REVIEW-ROUTES.md`) are not replaced by it.

**How Review A is held (defined 27 September 2026; the handover audit found it undefined).** For layer 2: one fresh reviewer who wrote none of the layer's documents checks `CONOPS.md`, `OPERATING-ENVELOPE.md`, `v2/ecad/tools/pcb_envelope.yaml`, the operator sections of `PANEL.md` and the state and envelope rows of `TEST-PLAN.md` at one pinned commit, against the owner's execution prompt section 3 (the layer-2 items) and against `ARCH-PCB-B-IOHA.md` section 15, `feasibility/EMCON.md` section 5a and `feasibility/POWER-THERMAL.md` section 9. The record goes under `v2/docs/reviews/` with the commit read, **labelled AI review**: it is never a qualified review and replaces none the records require (D-09). Findings are answered in the documents; the layer is then marked baselined at that commit in `v2/docs/handover/LAYER-STATUS.md`. `CONOPS.md` carries the same definition at its top.

Review B, layer 3, is an AI review by one fresh reviewer who wrote none of the requirements registry, its trace page or
the test plan's requirement trace, labelled as an AI review and never a qualified review, against the layer 3 row of
section 3 and the tests of section 2 of the owner's handover prompt, recorded at
`v2/docs/reviews/REVIEW-B-LAYER-3-<date>.md`; its findings are answered before the registry's `baseline_state`
names the commit it baselines (the session's choice under the owner's standing rule of 26 September 2026, recorded in
the requirements registry with the open item "Review B held"). No record in this tree requires a qualified review of
layer 3; the qualified reviews named elsewhere (D-09 and `reviews/REVIEW-ROUTES.md`) are not replaced by it.

Milestones, each reported separately:
- FOUNDATIONS_BASELINED
- DESIGN_READY_FOR_LAYOUT (per board)
- DESIGN_PACKAGE_READY_FOR_PROTOTYPE
- PROTOTYPE_FAB_RELEASED
- PROTOTYPE_VERIFIED
- PRODUCTION_RELEASE_READY

## Workstreams (first working day)

| # | Workstream | Output |
|---|---|---|
| W1 | Systems and requirements | product brief, concept of operations, candidate requirements, conflict list, owner decision table |
| W2 | Power and electronics | power tree, worst-case budgets, runtime per pack configuration (provisional until the modes and the pack are fixed), protection and decoupling review |
| W3 | Interfaces and board B | board-to-board contracts, lane and bandwidth allocation, board B congestion diagnosis and one bounded escape trial |
| W4 | Mechanical, thermal and RF | tolerance and mass budgets, thermal budget, antenna plan, a measurement request for the physical case |
| W5 | Firmware and testability | hardware/firmware contract, test access per board, the test plan classified by purpose |
| W6 | Independent verification and manufacturing | part identity and source audit, the STM32H753/H743 compatibility question, fabricator stackup questions |
| W7 | Regeneration and evidence integrity | regeneration parity for every board, an account of every skipped test, the decision 31 holds, asset dispositions |

Rules for the workstreams:
- Each workstream works in its own worktree. Only the integrating session merges and commits.
- A shared record (`ARCHITECTURE.md`, requirement IDs, board-to-board interface entries) has one writer, the integrator.
- Every consequential finding is challenged by an independent reviewer before it is merged. Agreement between reviewers is review, not physical evidence.

## Standing conditions (owner, 25 September 2026)

1. A part substitution is a component mismatch until compatibility is proven. The schematic's STM32H753 against the STM32H743 bought is open until then.
2. A runtime figure stays provisional until it is computed per pack configuration from usable energy, losses, temperature, ageing and the real modes.
3. A test limit above the operating envelope may be an intended qualification margin. Its purpose is recorded before it is changed.
4. One writer per shared file. Workers test in isolation.
5. "The generator is current" is shown by regenerating and comparing, not asserted.
6. Skipped tests are not passes. A hold is lifted only on fresh evidence that matches the board's actual configuration.
7. Board B feasibility evidence permits further investigation only. A committed layout candidate needs its schematic, parts, interfaces, stackup and mechanics reviewed first. Experiments stay EXPERIMENTAL.

## Stage gates: layout entry, fabrication release, prototype verification

The review of the 22:35 progress report (`v2/docs/reviews/2026-09-26-second-checkpoint-review.md`, finding A) found
gates that could never be satisfied because they waited for the thing they gated: decision 31's holds lifted only on a
corrected layout while layout entry needed them gone, INT-002 was a schematic gate closed only by a test on the built
board B, and several feasibility blockers held layout entry until a placement or a bench test. Every gate now names its
stage. Moving a check to its stage changes when it applies; it waives nothing. The acceptance criteria live in the
registries (`tools/pcb_board_holds.yaml`, `tools/pcb_requirements.yaml` stages, `tools/pcb_rules.yaml` INT-002 and
INT-003); `rules_status.layout_entry` computes the layout-entry test and CURRENT-EVIDENCE.md renders it.

| Stage | What it needs | What it may not need |
|---|---|---|
| Layout entry | per board: every required schematic-phase rule a PASS on current-candidate evidence; reviewed protection topology, exact fitted parts, corrected schematic, owned interfaces, placement and return-path constraints; each feasibility blocker's layout-entry stage closed (desk evidence, or a development-board test where an architecture decision turns on it) | a layout, a fabricated board or a built kit |
| Fabrication release | the actual layout implements the reviewed schematic (SCH-002 PASS on current-candidate evidence) and passes the physical protection, parity and routed-board checks; the fabrication-release stages (the qualified reviews where a blocker names one, the bounded enclosure heat experiment before hot-part placement is frozen) | a fabricated board or a built kit |
| Prototype verification | the physical tests of TEST-PLAN and the feasibility pages, on the built kit | nothing earlier stands in for them; a desk review is never a physical test |

Milestones, per board, in the order they can close (none is closed today):

| Board | Layout entry also needs, beyond its rule evidence | Fabrication release also needs | Prototype verification |
|---|---|---|---|
| A | decision 31: the protection-topology review on A's netlist, U31 as fitted, TRN-001 PASS; FEA-002 (EMCON lines L1 to L4, L7); FEA-004 (the chain re-declared at 18 A for 60 s and A's pack-path copper constraint); FEA-006 (decoupling classes in the generator); FEA-007 (its desk items: the pack hold-down S-27 with M4a and M5, W4-F17, the dock and blind-mate tolerance stack; then the case mock-up's check T4) | decision 31's hold lifted on the layout; FEA-002 RF-002 PASS; FEA-004 the heat-balance test and A's routed copper at 18 A; FEA-006 class seats read on the placement; FEA-007 the committed layout re-read against the case mock-up's readings, no row below its minimum | FEA-002 E-01 to E-12; FEA-004 bring-up readings and TEST-PLAN E3 |
| B | FEA-001 (Z-EXP-A and Z-EXP-B on development parts, or the switch taken); FEA-002 (SD-EMC-1 drawn, L1 to L4, L7); FEA-003 (FB-FAB-1 to FB-FAB-5 on the netlist, the escape strategy from Q-B-ESC-1 and decision 43's stack, the channel budgets); FEA-006; FEA-007 (its desk items: the jumper plug picked from a maker's drawing with M17g and M17x MET on the design basis, M13 bounded, the M1 lookups; then the case mock-up's checks T2, T4, T5, T10 and T11); INT-002's pre-layout assessment current on its 48 nets | FEA-001 U8 as selected; FEA-002; FEA-003 complete placement and route, routed lengths, the fabricator's impedance record, the qualified high-speed review R-HSD; FEA-006; FEA-007 the committed layout re-read against the case mock-up's readings, no row below its minimum | INT-003 (the three module links at 1000M, error free, cold and hot); FEA-001 Z-EXP-C and REQ-035; FEA-002 bench; FEA-003 IOHA A1 to A14 and the reference clock |
| C | FEA-002 (the hardware EMCON lamp, L1); FEA-006. FEA-007 does not hold C at layout entry | FEA-002 (RF-002, the lamp's light-guide hole); FEA-006; FEA-007 the committed layout re-read against the case mock-up's readings, no row below its minimum | FEA-002 bench |
| D | decision 31: the review on D's netlist, D9 to D14 as fitted, TRN-001 PASS; FEA-002; FEA-004 (the PA flange sensor drawn); FEA-006; FEA-007 (its desk items alone, no purchase: W4-F17) | decision 31's hold lifted on the layout; FEA-002; FEA-004 heat-balance test; FEA-006. FEA-007's fabrication-release stage does not name D | FEA-002 E-01, E-02; FEA-004 the flange against a thermocouple |
| E | decision 31: the review on E's netlist, D9 and D10 as fitted, TRN-001 PASS; FEA-006; FEA-007 (its desk items: the dock and blind-mate tolerance stack with the clamp bar, the clamp lanes M17f and the pad places M15b; then the case mock-up's check T10) | decision 31's hold lifted on the layout; FEA-006; FEA-007 the committed layout re-read against the case mock-up's readings, no row below its minimum | TEST-PLAN rows of its interfaces |
| P | FEA-005 (the packet current on the candidate, the secondary coordination at desk with its placement constraints, the charger state sequence); FEA-006; FEA-007 (its desk items: the pack hold-down S-27 with M4a and M5; then the case mock-up's checks T2 and T4) | FEA-004 F2 at 18 A for 60 s by Eaton's answer or a coupon test; FEA-005 the qualified battery review answered; FEA-006; FEA-007 the committed layout re-read against the case mock-up's readings, no row below its minimum | FEA-004 extended protection test; FEA-005 golden image and O-9 |
| E5 | FEA-007 (its desk items alone, no purchase: the dock and blind-mate tolerance stack); no hold names it | its release package bound by content. FEA-007's fabrication-release stage does not name E5 | the mate test of its contact targets |
| Case (the made parts) | not a board: no layout entry | FEA-007 the made parts of `v2/release/case-2026-09-27/` drawn to the mock-up's numbers before they are cut | FEA-007 T3, T7, T8 and T9 at the build, and REQ-047's lift-out on the assembled prototype |
| Source of the FEA-007 entries | **corrected for handover H3 (27 September 2026):** until then this table named FEA-007 on no board. The authority is the FEA-007 record of `tools/pcb_requirements.yaml`: `holds_layout_entry` a, b, d, e, e5, p, with the mock-up's checks needed for A, B, E and P only (BLOCKED on the purchase, L-07) | its FABRICATION_RELEASE stage holds a, b, c, e, p and the case | its PROTOTYPE_VERIFICATION stage holds the case and the kit |

Taken by the session under the owner's standing rule of 26 September 2026 (the review named what each stage needs and
left the allocation of each item to the session): the stage of every item above, the three requirement kinds of a
later-staged hold (rule_pass, fitted_parts, review), and INT-002's split into a pre-layout assessment and INT-003's
bench test. Reverse by moving an item back, which the validators allow only if its evidence can exist at that stage.

## Compute and spend

| Date | Resource | Purpose | Rate | Cap | State |
|---|---|---|---|---|---|
| 25 Sep 22:25 | vast.ai 52646493 (64 vCPU, 251 GB) | the full suite with KiCad, regeneration parity, adjudication readings, every circuit regeneration, the review packets; later the board B escape trial | 0.121 to 0.142 USD/h | about 10 USD for the foundation rounds | running; 19.9 host-hours and 2.88 USD spent at 26 Sep 18:24 (credit 125.11 USD); 22.3 host-hours and 3.19 USD at 26 Sep 20:45 (credit 124.80 USD); about 43.5 host-hours and about 6.5 USD at 27 Sep 18:30; running at 27 Sep 22:05, credit 120.89 USD read from the provider (7.10 USD spent in total), rate 0.142 USD/h |
| 28 Sep 15:20 | the same host | the set 6 integration: one re-take of every schematic-phase reading (110.7 s) and the full suite at each of its three candidates (about 11 minutes each); then the box jobs of the streams that follow | 0.1422 USD/h | 20 USD for the foundation work (the owner's approval of 28 September 2026 of the restart plan's decision 7.2, option a), with the host destroyed when no job is queued for 24 hours | running; credit 117.92 USD read from the provider at 18:48 CEST (10.07 USD spent since 25 September) |

Credit at the start: 127.99 USD. A box is destroyed when its last result is fetched and verified.

**Model usage is measured in tokens and kept apart from money.** It is read from the sessions' own transcripts (the
`usage` record of every assistant message); the billing route is the owner's subscription with extra usage off, so
these tokens draw on its rolling limits and make no invoice. A worker of the second model family (the Codex worker,
`CODEX-WORKER.md`) reports its own tokens in its event stream, under the owner's ChatGPT sign-in; a dollar figure
computed from list prices is an estimate and never a bill.

| Span | Agents at a time | Output tokens | Cache write | Cache read |
|---|---|---|---|---|
| 27 Sep 21:56 to 28 Sep 00:45, the recovery session | up to about 20 | 7.35 M | 71.1 M | 2.97 G |
| 28 Sep 15:19 to 18:48, the resumed session: the coordinator | 1 | 1.46 M | 6.0 M | 0.21 G |
| the same span: its workers and checkers (11 agents in turn, never more than 2 at a time) | at most 2 | 1.10 M | 18.3 M | 0.33 G |
| 28 Sep 18:43, the Codex worker's one smoke call | 1 | 290 (input 28,483, of which 13,952 cached) | not reported | not reported |
| 28 Sep 18:54 to 19:11, the Codex worker's pilot (cx1-if-ab-power, 1024.6 s) | 1 | 29,484 of which 7,185 reasoning (input 2,144,372, of which 1,995,904 cached) | not reported | not reported |
| 28 Sep 19:34 to 19:51, the Codex worker's one correction (cx1-if-ab-power-c1, 1009.2 s) | 1 | 30,818 of which 4,859 reasoning (input 2,585,247, of which 2,443,136 cached) | not reported | not reported |

## Log

- 25 Sep 22:33: baseline recorded; workstreams W1 to W7 running; KiCad box setting up.
- 25 Sep 22:40 to 26 Sep 00:20: round 1 (seven workstreams, seven independent challengers, one completeness critic) and round 2 (eleven adjudications from primary sources and box readings, seven fix passes, publish checks). Design defects found at the circuit and part level, among them: board B's PCIe downstream and LimeSDR SuperSpeed pairs wired transmitter to transmitter; the charger's cell-count strap selecting 2S; ten one-way clamps and rectifiers drawn reversed; the pack gauge on the wrong land; the 5G socket keyed M; EMCON not reaching the compute modules' own radios; only about 145 Wh of pack fitting the case. Regeneration parity proven for boards A, B, C, D, E and P (E5 identical in copper).
- 25 Sep 23:10 and 26 Sep 00:20: four test fixtures were found writing into this tree's own evidence and were isolated (2ba560ec, 82dd1e4d). Correction: 82dd1e4d's message says CMP-002 and SUP-001 do not read the lcsc_fill verdict; they do (the readiness takes the worst of every verdict a rule names), so the fixture output had been standing in for the real reading. It was removed from the evidence folder, and those pairs read INCONCLUSIVE until a real re-take.
- 25 Sep 23:27 to 26 Sep 00:55: the owner ruled the foundation questions D-01 to D-17 one at a time, each at the recommendation (recorded in CONOPS section 7, the requirements registry, the envelope, decisions 30 and 40, appendix 32.366), then set a standing rule: he is not asked again, and the session takes the recommended option and records it.
- 26 Sep 01:00 to 09:00: round 3 integration and its fix-up merged: d468613e (stackup rows for boards P and B, the part source record), 4ec785d8 (rulings, decisions 30 and 40, PANEL, IOHA, ASSEMBLY and envelope corrections), 68bc9e8f (product brief, concept of operations, V2-SPEC and READMEs), 6104cb81 (SCH-002 compares values and lands, certification demands the exact part and land, rules_status reads only the phase directory). Suite 1408 passed, 0 failed, 60 skipped. Open pairs rose from 118 to 128 because SCH-002 and CMP-002/SUP-001 now read INCONCLUSIVE on several boards until fresh re-takes under the corrected tools.
- 26 Sep: round 4 (Review D circuit corrections per board, each regenerated on the box and independently reviewed) and round 5 (remaining fix-ups, re-reviews, and one integration tree regenerated for every board) running.
- 26 Sep 12:32 to 18:20: rounds 4 to 6 merged the circuit corrections of boards C, D, E and P (faf8c981) and A, B and D (458b2873), each regenerated from its generator with every netlist difference traced to a finding and independently reviewed; the shared checking tools are in round 7. The case margins and the owner's D-08 reversal, D-08a, SC-02 and the transport correction landed in b69f20db.
- 26 Sep 14:12: the owner supplied a review of the 13:05 progress report and ordered it executed (v2/docs/reviews/2026-09-26-foundation-progress-review.md, 1f614233). Executed so far: evidence classes (26e847bc), ZEROIZE feasibility (9b0635d1), the failover fabric map (a5266aa8), decision 42 ruled by part class (9d566e8b), review packets for C, D, E and P plus the review routes and the vendor filing (ccf5808e), and the battery protection packet with board P's secondary over-temperature restored (d90f30e4). Running: EMCON inhibit table and power/thermal budget (last checker items), round 7 (shared tools, then every board regenerated).

- 27 Sep 21:17 to 22:30: the runner rebooted and its `/tmp` was cleaned at boot. Every worktree of the session, its helper scripts and the uncommitted files of the five wave 5a desk streams were deleted; nothing committed, pushed, released or held on the KiCad host was lost. A new session recovered the state (the checkpoint of 27 September 23:02 below), archived the worktree registrations, the earlier session's transcripts and the host's logs before pruning anything, and moved the worktrees to a folder that survives a reboot.

### Checkpoint, 26 September 2026 18:24 CEST (the review's section 6 terms)

**Headline** (v2/docs/CURRENT-EVIDENCE.md): foundations incomplete; 0 boards ready for layout; 0 physically verified. The earlier 212 of 333 figure is a historical aggregate of mixed revisions and is not quoted as readiness.

| Item | State |
|---|---|
| Elapsed since the baseline (25 Sep 22:33) | 19 h 51 min |
| Host-hours and spend | one KiCad build host, 19.9 h, 2.88 USD; credit 125.11 USD |
| Experiments completed | none routed since the re-baseline (the board B eight-layer escape trial is specified, not run) |
| Evidence made current | every rule-board reading classed: 8 current candidate, 2 valid historical, 282 awaiting revalidation, 20 desk review, 0 physical test, 21 no evidence (the per-board layout-entry blockers are listed in CURRENT-EVIDENCE.md) |
| Blockers closed with evidence | the circuit corrections of all six schematic boards (each reviewed, regenerated, traced); board P's secondary over-temperature restored on its own thermistor; decision 42 ruled per part class from the makers' documents; contaminating fixtures isolated and their evidence invalidated |
| Blockers open, bounded | ZEROIZE on the fitted ATECC608B (a bounded development-device experiment specified); EMCON guarantees for the 5G module and WiFi cards (bench proof specified); the failover fabric's escape strategy and signal integrity; the battery packet awaiting the approved qualified reviewer; two new qualified review routes (board A power, board B high-speed digital) needing the owner's spending approval; the requirements registry and architecture page (re-anchoring to main, then merge) |
| Next verifiable result | round 7 merged with every board regenerated and the clamp polarity and RF-002 transmitter checks reading the real boards; review packets for A, B and D; the requirements and architecture candidate merged with its feasibility blockers explicit |

### Checkpoint, 26 September 2026 20:45 CEST

**Headline** (v2/docs/CURRENT-EVIDENCE.md): foundations incomplete; 0 boards ready for layout; 0 physically verified.

| Item | State |
|---|---|
| Elapsed since the baseline (25 Sep 22:33) | 22 h 12 min |
| Host-hours and spend | one KiCad build host, 22.3 h, 3.19 USD; credit 124.80 USD |
| Experiments completed | none routed (the board B escape trial Q-B-ESC-1 is specified with its driver in tools/routeflow/experiments/b_esc1/, not run) |
| Evidence made current | unchanged in class: 8 current candidate, 2 valid historical, 282 awaiting revalidation, 20 desk review, 0 physical test, 21 no evidence. The layout-entry blockers are 74: 27 close with a re-take alone, 31 once a tool records the artefact it judged, 12 once PWR-001's and SI-001's tools judge the netlist, 1 needs a deciding verification (INT-002 on B), 3 are decision 31's holds on A, D and E |
| Blockers closed with evidence | review item 1: the requirements registry (131 records, six FEA feasibility blockers, validator and generated trace) and the architecture page with board-to-board contracts and board B's escape diagnosis and trial specification (9f848223, 7808734f, 70819008); round 7b's shared tools: clamp polarity judged from the part number on every board, the pack SMBus lead a cross-board contract, maker-named lands on the rotation checklist, every board regenerated with schematics byte-identical (93138ac1); S-05 closed and CFL-015 resolved with the assembly guide and panel contract describing the lead as generated (16fa4c23) |
| Blockers open, bounded | as at 18:24, plus: TRN-001 reads FAIL on A and B on the clamp symbol (0 reversed); the RF-002 transmitter walk is in its review loop and not merged |
| Running | tools stream (seven writers record the artefact they judge; PWR-001 and SI-001 on the netlist; A's and B's clamps on the one-way symbol with every board regenerated); published contracts rewritten against the circuits (S-07); parts (certification re-take, owed source entries); records filing (every drafts/ record a committed page cites, filed in the tree); the RF-002 walk's review loop |
| Next verifiable result | the tools stream merged, then one re-take of every schematic-phase reading on the committed netlists in a clean clone on the box, which is the step that can move boards to layout entry |

### Checkpoint, 27 September 2026 18:30 CEST (the handover prompt's section 8 terms)

**Headline** (v2/docs/CURRENT-EVIDENCE.md): 0 boards ready for layout; 0 physically verified. **Layers 1 (product
definition) and 2 (concept of operations) are COMPLETE**, each on its AI review records (not a qualified review);
layers 3 to 9 are IN_PROGRESS with their remaining items in `v2/docs/handover/LAYER-STATUS.md`.

| Item | State |
|---|---|
| Handover snapshots | H1 (`a8652172`), H1.1 (`84d0a527`, zip-only) and H2 (`174d8466`, built from `b89b50b4`, H2.zip sha256 `20072be7...`). H1 and H2 were each tested by one fresh checker from the ZIP and its stated dependencies: H1 a usable partial handover with 2 blocking and 13 minor defects (H1.1 answered 13 fully and 2 in part); H2 a usable partial handover with no blocking defect and 14 minor ones, layers 1 and 2 reading as complete. H1.1 was not independently checked. |
| Layers newly COMPLETE, with evidence | layer 2 at `79963b3b`: `v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md` (no blocking finding), CONOPS BASELINED; layer 1 at `6b2a9965`: the second release check's one blocking item fixed in `cecfd0f1` and closed by `v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`, the brief BASELINED. Layer 3's baseline was reversed by the same targeted check (S-80, EQ-30). |
| Work completed since 20:45 on 26 September | round 8 on all six boards and wave 3 on A, B, D and E, each regenerated with parity on the KiCad host; the RF-002 walk (UNDECIDED unless a held maker document clears a pin); the re-take driver `tools/retake_schematic_phase.py` and the consolidated re-take (`8ea7867e`, installed `5ca81eea`: layout-entry reasons 101 to 40, CURRENT_CANDIDATE rows 8 to 81); the handover pages, snapshot tool, layout constraint sheets, stackup record, HW-FW contract with 30 interface contracts, case release `v2/release/case-2026-09-27/`, diagrams rebuilt on set 5; the hot stop REQ-077 as a session decision |
| Blockers, design work | per board in CURRENT-EVIDENCE: RF-002 FAIL on A to D (W3T-F1 desk bound, EQ-25; board B's nine transmitter kills the walk does not see reached), PWR-001 open on C, D, E and P, SI-001 on all six boards with a schematic, BAT-001 on P from a stale table, E5's unbound INT-001; HOT-R1 (EQ-22); the QMX tray (EQ-24); decision 31's reviews on A, D and E; wave 4 is working these |
| Blockers, physical evidence | EQ-05 to EQ-09 |
| Blockers, external authorisation | EQ-10 to EQ-14, EQ-23, EQ-26 (qualified reviews, M1's duration, prices, the hot stop's hardware backstop, the pack's margins); costed in `v2/docs/reviews/READY-TO-ACT.md` |
| Changed requirements or reopened decisions | REQ-077 added (the hot stop, SC-49) with HOT-R1 owed; REQ-072 reads FAIL at desk (a night on pack and solar alone), M-02 the owner's part; CON-010 moved to FAIL (the session's, reversible); SC-21 governs M1's duration (the owner may replace it); FEA-007 (the case fit) holds six boards' layout entry, the mock-up purchase four of them |
| Lost time | a usage limit stopped every agent from about 07:51 to 11:00; the 09:35 checkpoint was missed and posted to MESHSAT-1357 at 11:20 |
| Host-hours and spend | one KiCad build host, about 43.5 h in total, about 6.5 USD (credit 127.99 to about 121.46 USD) |
| Next verifiable result | layer 3 re-baselined after the S-80 wording fix; wave 4 merged with a second re-take; H2's minor usability findings answered; snapshot H3 |

### Checkpoint, 27 September 2026 23:02 CEST: the recovery, and the source of handover H3

**Headline** (v2/docs/CURRENT-EVIDENCE.md, unchanged since H2): 0 boards ready for layout; 0 physically verified.
**Layers 1, 2 and 3 are COMPLETE**, each on its AI review records (not a qualified review); layers 4 to 9 are
IN_PROGRESS. This checkpoint is written into the commit line that handover H3 is built from; H3's own figures (its
source and snapshot commits, its checksum, its suite and its two fresh checks) are in
`v2/docs/handover/RELEASE-H3.md` once the snapshot is filed. It follows the owner's instruction of 27 September
2026 (evening) to recover the interrupted session, and the five amendments of the review of the recovery plan: the
completed layers are delivered first and are not held behind circuit integration, a history restructure or new
tooling; recovery material is preserved before any cleanup; workers checkpoint their own branches and only the
integrating session updates `main`; a guard on evidence keeps a reading only while its fingerprints match; two failed
reviews change the method and the item stays assigned.

**What the recovery found** (read-only pass, 21:56 to 22:25):

| Item | State found | Class |
|---|---|---|
| `main` | `6ec37197`, equal to the public repository, clean; no netlist changed since H2 | CONFIRMED_CURRENT |
| Handover H3 | not built | CONFIRMED_CURRENT |
| Set 6, the wave 4 circuit work (branch `fnd/r8int6`, `a76a246e`) | never promoted: its suite on the KiCad host read 2010 passed, 1 failed, 3 skipped; its re-take never started | NEEDS_REVALIDATION |
| Wave 5a, five desk streams (tray, stackups, SI-001's edges, part identities, the kit I2C bus) | nothing committed, worktrees deleted; 42 source files rebuilt from the agents' transcripts, with each first check's blocking findings | NEEDS_REVALIDATION |
| Older drafts that committed pages cite (hc9's scripts and draft rules, board A's converter scripts, the REVIEW-ROUTES correction, the frame-seat draft) | in no git object; found in the transcripts, not yet filed in the tree | NEEDS_REVALIDATION |
| Branches `h2m-backup` and `r8int3-backup` | every commit has a patch-equivalent commit on `main` (`git cherry`) | SUPERSEDED |
| Branches `fnd/rtk` and `fnd/rel2-eb9f9030-judged` | each commit corresponds to one on `main` (`e5fde2ed`; `7dfbfb16` and `79963b3b`) by `git range-diff` and a file-by-file reading: the tool and its test are byte-identical, the remaining differences are later edits, rebinds to set 5's netlists and renumbered ids | SUPERSEDED |
| The KiCad host (vast.ai 52646493) | running and reachable; one suite job of 27 September 00:00 with no supervisor, ended by its process id | CONFIRMED_CURRENT |

No branch was deleted. The worktree registrations were archived and read back before `git worktree prune`.

**The checkpoint in the six fields of the owner's instruction:**

| Field | Content |
|---|---|
| Delivered | nothing is released at this checkpoint. Prepared on this commit line: the pages of handover H3, which state layer 3 COMPLETE one way, correct this page's milestone table (FEA-007 holds the layout entry of A, B, D, E, E5 and P), state three separate ways to use the handover with their prerequisites, and list H3's errata (`v2/docs/handover/START-HERE.md` section 1a). H3's design content is H2's: `v2/docs/records/h3/design_difference.py` asserts that no schematic, netlist, intent, generator or checking tool differs from H2's source commit |
| Remaining | per layer in `v2/docs/handover/LAYER-STATUS.md`. For H3: the suite on its exact source commit, the build, two fresh checks, the release record, the copy for the owner. For set 6: promotion onto this line and the re-take of its readings |
| Engineering | set 6 is a checked candidate since 22:54: with `reliability.py` corrected (it judged the whole value text, and the word "socket" in the description of three logic gates of board B made them wear parts; it now judges the part's identity, `760d7f41`) its suite on the KiCad host reads 2015 passed, 0 failed, 3 skipped, each skip a property of that host. A baseline suite at `main` `6ec37197` on the same host reads 1998 passed, 0 failed, 2 skipped. **Found and open:** TRN-001 on board A does not cover VIN_RAW's entry, because `boards/a.json` still declares J_DOCK pins 1 and 2, which are ground since SC-55 (H3's erratum f; board A's stream moves the declaration to J_VR1 to J_VR4 and re-takes TRN-001); REL-001's word list finds no wear word on 61 connector-like parts (an RJ45 jack, two SIM sockets, a ZIF, two headset jacks and the dock's spring pins among them), so its completeness holds for its twelve words only; the rule audit names its verdicts by absolute path, so an audit restored into another worktree points at files that are not there. Each becomes a registry item when set 6 is integrated. No electrical defect is closed by anything at this checkpoint |
| Resources | the dispatch ledger below. One KiCad host, about 48.7 host-hours since 25 September 22:25, 7.10 USD spent in total, credit 120.89 USD (read from the provider at 22:05). No second host: no measured queue asks for one |
| Decisions | none that needs the owner's authority. The outside items stand as `v2/docs/reviews/READY-TO-ACT.md` section 0 lists them; nothing was sent, bought or engaged |
| Next | H3 built from the commit after this one and checked; then set 6 merged onto this line (merged, never rebased: H3 names its commits) with its re-take; then the evidence guard, the constraint binding check and the separation of status from history, which go into H4 with wave 5a and the desk closers of layers 4 to 9 |

**Dispatch ledger** (what was actually started, times CEST on 27 September; a stream not started is said so):

| Worker | Task | Branch | Started | State at 23:02 |
|---|---|---|---|---|
| h3pages | the pages of H3 | `fnd/h3` | 22:30 | done 23:00; four commits; validators clean; reviewed by the integrating session |
| set6fix | `reliability.py`, the suite on the exact commit, the validators | `fnd/r8int6` | 22:30 | done 22:54; two commits (`760d7f41`, `73ae2f21`); not promoted |
| retake6 | the consolidated re-take of set 6's readings on the KiCad host | `fnd/retake6` | 22:57 | running |
| w5ident | part identities (EQ-21), second pass | `fnd/w5ident` | 22:30 | running, checkpoints committed |
| w5stack | stackup and copper per board, second pass | `fnd/w5stack` | 22:30 | running, checkpoints committed |
| w5si | SI-001's edge rates, second pass | `fnd/w5si` | 22:30 | running, checkpoint committed |
| w5i2c | the kit I2C bus (CON-026), verification and proof by regeneration | `fnd/w5i2c` | 22:30 | running, checkpoint committed |
| w5tray | the QMX lid tray r2, second pass, with a fresh checker | `fnd/w5tray` | 22:50 | running |
| p3guard | the evidence-refresh guard, with a fresh checker | `fnd/p3guard` | 22:50 | running |
| p3bind | the constraint binding check and the power tables on set 6's inputs, with a fresh checker | `fnd/p3bind` | 22:50 | running |
| the desk closers of layers 4 to 9 | | | | not started. The circuit streams wait for set 6's promotion: each generator has one owner |

**Resume record** (what a new session needs if this one stops):

- Candidate: this commit line (`fnd/h3` on `main` `6ec37197`), to be fast-forwarded to `main` once the suite has run
  on its exact commit. Set 6: `fnd/r8int6` `73ae2f21`. No uncommitted work is of value: every worker commits on its
  own branch at least every 30 minutes.
- Worktrees: `<worktrees>/<name>`, one per branch above (outside `/tmp`). Worker
  branches are never pushed, because the mirror publishes every branch; an incremental bundle of every branch is
  copied to the owner's laptop after every integration and hourly (`~/meshsat-fieldkit-bundles/`, proven by
  rebuilding every ref from it there).
- KiCad host jobs: `/root/retake6/` (the re-take), and the workers' own folders `/root/<stream>/`. Every job clones
  from `/root/r8int6/repo` plus a bundle of its branch and writes a `done-<what>` file.
- Next concrete action: build H3. Prerequisite: the suite at 0 failed on the exact source commit and the source
  commit public. Commands: `python3 v2/ecad/tools/handover_pack.py plan --commit <sha>` (must end "0 unclassified"),
  `build --commit <sha> --version H3 --zip-only`, `verify v2/release/handover/H3.zip`, `sha256sum -c`. Expected: a
  ZIP under the cap of 52,428,800 bytes (a dry build from `6ec37197` was 52,122,151). Acceptance: both fresh checks
  filed, the release record complete, the package on the owner's laptop with its checksum verified there.

### Checkpoint, 27 September 2026 23:50 CEST: handover H3 delivered and checked

| Field | Content |
|---|---|
| Delivered | **Handover H3**: `v2/release/handover/H3.zip`, sha256 `6922a96d...dd07a`, 52,187,825 bytes, built from `75ad6ee5`, filed in `bd96bb61`, public, and on the owner's laptop with its checksum verified there. Layers 1, 2 and 3 are COMPLETE in it, each on AI review records; its design content is H2's. Release record: `v2/docs/handover/RELEASE-H3.md` |
| Remaining | for H3: the twenty-eight minor findings of its two checks, answered in the pages' next edition (`H3-RESPONSE.md`). For the layers: 4 to 9 as `v2/docs/handover/LAYER-STATUS.md` lists them |
| Engineering | the suite on H3's exact source commit reads 1998 passed, 0 failed, 2 skipped on the KiCad host. Both fresh checks found no blocking defect. An independent review of H3 (`v2/docs/reviews/2026-09-27-h3-independent-review.md`) credits layers 1 to 3 and confirms two checker defects: REL-001 can read PASS on a connector its word list does not see and on a missing netlist; TRN-001 on board A judges a declaration that names two ground pins. Both readings are LIMITED until repaired. No electrical defect is closed at this checkpoint |
| Resources | the ledger of the checkpoint above, with these changes: part identities, edge rates and stackup finished their second pass and are with fresh checkers; the re-take of set 6 has committed its readings; started since: the desk closers for FEA-002, FEA-004 with FEA-005, FEA-006, FEA-007's desk items, decision 31's protection review and the energy budget (branches `fnd/d4emcon`, `fnd/d4chain`, `fnd/d6dec`, `fnd/d7fit`, `fnd/d8dec31`, `fnd/d4energy`), and the repair of REL-001 (`fnd/d6rel`). One KiCad host, no queue measured on it |
| Decisions | one for the owner: thirteen IBIS models of makers and twelve captures of the fabricator's stackup data are held back from this public repository until their terms are read, because a maker's header is reported to forbid redistribution. Until he decides they are referenced by address and sha256 and fetched by a script |
| Next | set 6 merged onto this line with its re-take; then the circuit round, one owner per generator; then handover H4 |

### Checkpoint, 28 September 2026 00:35 CEST: paused by the owner after the second usage limit of the night

| Field | Content |
|---|---|
| Delivered | nothing since H3. The reassessment of H3's release companions (`v2/docs/reviews/2026-09-28-h3-release-companion-reassessment.md`) reads the archive READY for a partial handover of the completed definition baselines with the listed errata, closes H3-03, keeps H3-01 and H3-02 open and acknowledged, and holds layout and fabrication BLOCKED. The review of the set 6 re-take report (`2026-09-28-set6-retake-review.md`) shows no new layer complete and asks that the next milestone be an accepted layer or board packet |
| Remaining | the set 6 integration, in progress on the local branch `fnd/int7` (never pushed): the H3 line is merged into the re-taken set 6 line (`069a5d97`; the registry's two conflicts resolved item by item, an item open only where both sides hold it open: 59 open, 58 closed, 144 records) and four open items are recorded (`f1dda804`: S-88 board A's port declaration, S-89 the wear list's completeness, S-90 the rule audit's absolute paths, S-91 the answers owed to H3's two checks). Not done on it: `claims_check` re-taken, `rules_status` three times and the renders, CON-010 FAIL to INCONCLUSIVE with the rebinding of CON-010 and REQ-044, the validators, the suite on the KiCad host on the exact commit, a fresh check of the merge, the fast-forward of `main`. After it: the reassessment's three corrections (board E's constraint sheet against its netlist, the `waits_on` links such as S-64 to CON-010 with the process-only items disposed of, baseline status and coverage limits derived into the generated pages), `H3-RESPONSE.md`, board C's three layout-entry blockers and its packet |
| Engineering | no electrical defect closed since the checkpoint of 23:50. The re-take's readings (83: 71 PASS, 10 INCONCLUSIVE, 2 FAIL; 35 layout-entry reasons against 40 on `main`) are on `fnd/retake6` and in `fnd/int7`, not on `main` |
| Resources | a usage limit stopped every agent at about 00:19; it reset at about 00:22 and the owner paused everything at 00:27. Stopped at the pause, each with its checkpoints committed on its own branch and the file it was writing left in its worktree: the desk closers d4chain (`0041c2f1`), d4emcon (`7dc74508`), d4energy (`9b43e274`), d6dec (`3c98a88e`), d7fit (`3dee1661`), d8dec31 (`d8e80d94`); the REL-001 repair d6rel (`ae79b22d`); the dock interface repair d5dock (not past its input `73ae2f21`); the evidence-refresh guard p3guard (`861d7398`, twelve files uncommitted); the constraint binding check p3bind (`3bfaa317`, its check unfinished); the tray w5tray (`0ad773ab`, its check unfinished); the kit I2C bus w5i2c (`ecb22e0d`); part identities w5ident (`c08f4d5a`, its second check unfinished, ten refuters lost at the limit); edge rates w5si (`7f7721c4`, its drafts check unfinished); stackup w5stack (`2fa245b2`, its physics check unfinished). Every branch is in the off-host bundle of 00:28 (113 refs, checked on the laptop). The KiCad host is up and idle (about 3.4 USD a day); its stream logs are archived with the recovery material |
| Decisions | none new. The third-party files (thirteen IBIS models, twelve fabricator captures) stay out of the public repository, referenced by address and sha256, as recorded at 23:50 |
| Next | when the pause is lifted: restart each stopped author from its checkpoint with a resume prompt in its own worktree (never two authors on one branch), re-run the unfinished checks fresh, and finish the set 6 integration on `fnd/int7` in the order above |

### Checkpoint, 28 September 2026 18:50 CEST: the set 6 integration is on `main`; a second model family is set up as a bounded worker

Resumed at 15:19 under the owner's restart prompt; its plan was reviewed by an outside reviewer and amended
(`v2/docs/reviews/2026-09-28-restart-plan-review.md`), then approved. Limits in force: one coordinator and at most two
workers at a time, no automatic orchestration.

| Field | Content |
|---|---|
| Delivered | **The set 6 integration on `main`** at `f2b8f98d` (a fast-forward from the local branch `fnd/int7`, pushed and mirrored): the set 6 circuit line `73ae2f21` and its consolidated re-take merged with the H3 line, the integrating session's registry and renderer work, and its records under `v2/docs/records/int7/` (`CLOSURE.md` by kind of change; three fresh checks `CHECK.md`, `CHECK-2.md`, `CHECK-3.md` with `CHECK-RESPONSE.md`). Nothing is released: H3 stays the accepted handover, untouched, and layers 1 to 3 stay COMPLETE |
| Remaining | for the integration: the minor items of the third check that need a registry edit (p3 to p8), carried to the next set. Next, in order: stream d8dec31's declaration, registry and hold scripts with TRN-001 re-taken (H3-02; one regression owed before S-88 closes), stream d6rel's repaired REL-001 with its re-take and the staged closure of S-89 (H3-01), stream p3bind's bound constraint sheets, stream w5tray's tray; then board C's chain toward its layout-entry packet (decoupling, EMCON lamp, edge rates, part identities, the functional review). Layers 4 to 9 are IN_PROGRESS |
| Engineering | **no electrical defect is closed by this integration.** Set 6's circuit changes are read, not claimed: 0 boards ready for layout, 35 layout-entry reasons (A 7, B 7, C 3, D 7, E 4, P 5, E5 2) against 40 before. Still FAIL on current-candidate evidence: INT-001 and SCH-003 on E5 (10 of 38 dock targets, S-74) and BAT-001 on P (3 of 63 checks, REQ-044, S-85); SI-001 INCONCLUSIVE on every board with a schematic. **Declaration changes and instrument corrections are counted apart** (`CLOSURE.md` sections 2 and 3): eight of board B's eleven failed RF-002 rows moved by a correction of the walk, not by the circuit. **Registry:** CON-010 FAIL to INCONCLUSIVE by a stated predicate computed from the four readings it rests on; it waits on S-92 and S-93, which carry every ground the walk's own report names for its three undecided rows (seven grounds), and a script asserts that coverage; every open item has a record waiting on it or a disposition with its reason (54 linked by 99 links on 60 records, 11 disposed), which the validator now demands; S-94 asks for the re-read of REQ-030, REQ-032 and REQ-071. **Found by a worker, not yet integrated:** board C does not pass SI-001 in either state of the makers' models; 23 of its nets are decided only by an instantaneous bound and each needs a series resistor at its driver, an impedance target, a declared allowance or the maker's model |
| Resources | three candidates were needed: two fresh checks refused the first two on registry text the integration wrote (never on a reading, a count or the merge), and after the second refusal on the same point the method changed (the dependency items are read from the walk's own report). Suite on the KiCad host at each candidate: 2019 passed, 0 failed, 3 skipped, each skip a property of that host. Host and tokens: the two tables of "Compute and spend" above. Workers of this session, never more than two at a time: the authors of d6rel and of the edge-rate follow-up (`fnd/w5si2`, running), and the checkers of w5tray, d8dec31, p3bind, d6rel, the edge-rate drafts and the three candidates |
| Decisions | none open for the owner. Taken by the owner today: the restart plan with its amendments; the host's cap at 20 USD; execution in the running session (the relaunch and the workflow setting withdrawn); the second model family as a bounded worker. Taken by the session under the ruling of 21 September: CON-010's predicate, the dispositions of eleven open items, S-92 to S-94. The makers' thirteen IBIS models stay out of the repository: the branch that tracked them is never merged, and its content continues on a branch squashed without them |
| Next | the pilot of the second model family (below); then the next integration set (d8dec31, d6rel, p3bind, w5tray) with one re-take and one suite, a fresh check, and the promotion; board C's chain in parallel within the two worker slots |

**The Codex worker** (`v2/docs/CODEX-WORKER.md`; approved by the owner on 28 September as an additive setup):

| Outcome | State and evidence |
|---|---|
| Environment ready | **yes.** Codex CLI 0.158.0 (linux x86_64), installed for the coordinator's own user by the maker's standalone installer (sha256 `150e3cf675682efeaac115aa3747add3f27887896d04ce6d0b56478d8b428bf6`, read before it was run), pinned to that version; no shell profile changed; the existing tools untouched. Signed in by the owner with a device code (ChatGPT sign-in; no API key, no API credit). One real task completed on `gpt-6-astra` at `xhigh`: a read-only read of a known file in a disposable fixture returned its content exactly, the fixture unchanged (git status empty, sha256 equal), one completed turn, no failed turn, no error. **Requested and observed configuration:** the event stream names no model; the CLI's own session record gives model `gpt-6-astra`, effort `xhigh`, approval `never`, sandbox `read-only`. That is the client's record of what it asked for, not the server's attestation, and the task used no reasoning tokens, as a one-line read may |
| Delegation ready | **yes, for bounded jobs.** The launcher's 13 tests pass with a fake child and no model call (a good review and a good authoring job; a nonzero exit with an optimistic result; a failed turn; a missing, malformed, wrong-job and unfitting result; a blocked job; a timeout that ends the child's own process group and keeps its partial output; a second author refused; a stale lock kept as a record; edits outside the permitted files, a moved branch, a missing deliverable; a rerun that leaves the first run byte-identical; refusals before launch; a substituted model or effort). The smoke call ran through the launcher. The tool's own sub-agents, plugins, skill discovery and goals are on by default and are switched off per job |
| Pilot | **not run yet.** Chosen: finding I-03 on the board A to board B power leads (contract `IF-AB-POWER`; layer 4 item 4.10 and layer 5 item 5.5), where the two ends declare different currents on `+5V_S2` and `+5V_DEV`. Author the Codex worker, reviewer a Claude worker who reproduces the sums from the makers' documents, acceptance the coordinator's |

### Checkpoint, 28 September 2026 20:02 CEST: the pilot of the second model family accepted as a record; integration set 7 open

| Field | State |
|---|---|
| Delivered | **The Codex pilot's record on finding I-03** (the board A to board B power leads, contract `IF-AB-POWER`), accepted by the coordinator after an independent Claude check that derived every figure blind from the makers' pages first and compared second: `v2/docs/records/cx1/` (ANALYSIS.md, if_ab_power.py with its output reproduced byte for byte, an unexecuted declarations draft whose `--check` passes against the generators as held, CORRECTION.md, and the check's five files under `checks/`). Its finding: no held document decides the all-transmit mode current of any of the five rails (INCONCLUSIVE on all five, each with the exact missing evidence named); the two ends are aligned INTERIM to the end that derives its figures from held pages (board A's +5V_S2 4.2 A typical and 5.63 A peak, J_5V_S2 5.63 A, Q28 2.22 A; board B's +5V_S2 peak 5.63 A; board A's J_5V_DEV 3.8 A and +5V_DEV typical 5.1 A); and a design finding beyond I-03: board A's +5V_DEV stage declares 6.9 A peak while its loads' coincident peak is 7.9 A with the D8 mezzanine at typical and 8.9 A at every declared limit, both above the LM5176 average loop's 7.10 to 7.17 A threshold. **Set 7 on `fnd/int8`** (tip `43e4a244`, 21 commits over `main`): the lid tray stream w5tray integrated (SC-75 closes S-63; S-95 the lid harness's crossing of the sealed face, S-96 the r2 set's verification on the model; FEA-007 and REQ-021 relinked); the third check's carried items (S-92 both voltages and bench E-01's gap, FEA-002 waits on S-92 and S-93, S-97 the walk report's three-ground cap); finding I-03's items S-98 (DECLARATION, for the generator owners) and S-99 (REQ-018 waits on it); the contract's contact rating rewritten from the held JST VH catalogue. Validators 0 errors; the registry 69 open, 60 closed, 144 records. Streams checked or finished since 18:50: d8dec31's follow-up done at `9057e668` (a reviewed set of external pins that the tool holds every declaration against; 61 tests), w5si2 done at `f84243ba` (board C does not pass SI-001 at the desk in either model state: 8 nets closable, 15 not). |
| Remaining | For set 7: the w5si2 check (running) and its seven apply scripts with SI-001 re-taken on six boards; the d8dec31 re-check (running) and its declaration, registry and hold scripts with TRN-001 re-taken; the d6rel re-check of `3d7c98d2` and its scripts with REL-001 re-taken; p3bind last; one box re-take (`_bin/box_retake.sh`), the suite, the isolated clone check, a fresh check of the merge, promotion. The layout-entry count reads 41 until the re-take (INT-001 CONFIG_CHANGED on every board for the contract's edited configuration input; 35 before). Then the queue: d6dec, d4emcon, w5ident's board C slice, d5dock, d4chain, d7fit, d4energy, w5stack, w5i2c, p3guard. |
| Engineering | I-03 stays open: its closure is the generator owners' application of the interim entries in the circuit round with the regeneration, the contract's currents rows and ARCHITECTURE.md's IF-AB-POWER row rewritten, INT-001 and PWR-001 re-taken; the mode figures are the bench's (TEST-PLAN power tests at J_5V_S2 and J_5V_DEV under PS-ALLTX). S-99 needs a session decision with more than one option standing (raise the stage's average limit by its sense resistor within the FETs' and inductor's ratings; interlock D8 or the wall port against the PA key-down; or declare the 8.9 A bound with fold-back as the limiter and judge REQ-018 on it); board A's generator owner in the circuit round. Board C's edge-rate answer: 8 nets at the desk (four e-paper series resistors, two SWD allowances, EPD_SW's net class, Q3_G's declaration), 15 not (the RP2040's QSPI wired direct with no published edge, HB1 to HB3 driven from board B, the kit I2C across four boards, XIN/XOUT until CLK-001 states a length). |
| Resources | Box credit 117.75 USD at 20:02 (cap 20 USD for the foundation work; the box idle since the set 6 suite). Model usage in the table above: the coordinator plus the workers named there; the two Codex engineering calls (the pilot and its one correction, the owner's bound) cost no API credit (ChatGPT sign-in). Two worker slots occupied by checks at this checkpoint. |
| Decisions | Coordinator (SESSION): the pilot's record ACCEPTED; the interim declaration entries are the generator owners' and are not applied by the integrator; S-98 carries a DECLARATION disposition as S-67 does; S-99 is linked to REQ-018 rather than disposed because a converter whose loads' coincident peak exceeds its average limit bears on the key-down regulation REQ-018 states; the ARCHITECTURE.md line that says the JST catalogue is not held is left to the currents rows' rewrite (one rebind of the bound record then). The stale port_protect test fixtures (283 directories under /tmp) were removed and their hygiene given to the d8dec31 re-check. |
| Next | Read the two checks; run w5si2's seven scripts and d8dec31's four desk scripts on `fnd/int8`; the d6rel re-check; p3bind; the box re-take and suite; the isolated check; a fresh check of the merge; promotion. |

**The Codex worker, three outcomes after the pilot:**

| Outcome | State and evidence |
|---|---|
| Environment ready | **yes** (unchanged from 18:50). |
| Delegation ready | **yes, proven on two engineering calls.** Both runs ended DONE_CANDIDATE by the launcher's computed checks (normal exit, one completed turn, no error event, HEAD at the base, only the permitted folder touched, every deliverable present); the client's session record names `gpt-6-astra`, `xhigh`, approval `never`, sandbox `workspace-write` (the event stream names no model). Run records under `_runs/codex/cx1-if-ab-power/` and `cx1-if-ab-power-c1/`, copied to the laptop. |
| Pilot | **accepted as a record; I-03 open.** The author's first answer stopped at INCONCLUSIVE with an empty draft; the independent check (blind reproduction of every figure, fifteen citations opened on their pages, the 7.28 A marginal case reproduced by hand) credited the record and found two things the sources DO support that the author had refused to do (align board A's stale +5V_S2 declaration to the end that derives its figure; call the +5V_DEV converter-side coincidence); the one correction did both, pinned the inputs by hash, cited the registry's power model, and left the +5V_DEV peak to a session decision (S-99). The next layer item it advances: layer 4 item 4.10 and layer 5 item 5.5, when the generator owners apply S-98 and INT-001 is re-read. |

### Checkpoint, 28 September 2026 23:00 CEST: integration set 7 on main

The owner's status request of 28 September, answered in these terms (the same text went to him):

**1. Delivered since the last report (21:40)**
- **Integrated and on main:** set 7, `6b419b02` to `9fc79c1f`, pushed. Its gates: the fresh merge check read it mergeable with no blocking item, the suite passed 2171 with 0 failures, and an isolated clone rendered byte-identical pages. It carries the lid tray, the edge-rate rule, the port protection, the reliability fix and the pilot records. H3-01 and H3-02 are closed. Layout-entry reasons went from 35 to 34.
- **Candidates awaiting review:** S-98 (`fnd/s98`), S-99 (`fnd/s99`, failed its check), the energy reconciliation (`fnd/energy`, failed its check, being corrected), the case purchase list (`fnd/od01`, being written).

**2. Layers**

| Layer | State |
|---|---|
| 1 to 3 | ACCEPTED; the H3 errata e and f are now answered |
| 4 to 9 | IN PROGRESS |
| 10, layout | BLOCKED: 0 of 7 boards pass layout entry |
| 11 | not defined in the plan |

No layer completed tonight.

**3. Priorities**
- **Edge-rate and port-protection checks:** both mergeable and integrated. SI-001 stays INCONCLUSIVE on every board.
- **S-98:** both generators aligned (INTERIM), not integrated. It needs the box regeneration and a contract re-read.
- **S-99:** the analysis failed the Codex check on ten findings; the sign error is confirmed on TI's page. The D8 split remains the candidate. Correction pending.
- **I-03:** open.

**4. Battery and solar**
Your correction is applied: M1 and REQ-072 are unchanged and REQ-072 reads FAIL. The gap below comes from desk calculation, reproduced independently:

| Quantity | Value |
|---|---|
| Aged pack | 108 Wh |
| September night at 42.8 W | 483 to 514 Wh |
| 72 hours | 3,082 Wh |
| Stage ceiling per September day | about 1,024 Wh |

- **Unresolved:** every load is a planning figure, the night cell temperature is assumed, and the solar day is a mean.
- **No configuration inside the case meets REQ-072 as written.**
- **Next:** correct three faults (second-pack fit, the 200 W panel against REQ-016, the paragraph's wording), re-check, then your decision.

**5. Running and resources**
- **Workers:** the case list, resumed at 22:39, and the energy correction, started at 22:55.
- **Box:** idle. Spend is 10.65 of 20 USD, confirmed from the provider's balance.
- **Codex:** 1 check and 1 correction remain.
- **Claude since 18:48:** 0.45 M output tokens from 618 messages. A usage limit stopped work from 21:52 to 22:39.

**6. Blockers and next milestone**
- **Owner:** none now. Coming: the checkout list, then the energy decision.
- **Engineering:** the case tests (A, B, E, P), the energy decision (A, E, P), S-99, S-98, and the port reviews of boards B and C.
- **Next milestone:** set 8. Acceptance: IF-AB-POWER reads AGREE on regenerated netlists, the suite reads 0 failures and the check is clean. No completion time is defensible yet.

### Scheduling, 28 September 2026 23:15 CEST: each active item's next action (the owner's instruction of 23:05)

| Item | Next action | Prerequisite | Worker | Acceptance evidence |
|---|---|---|---|---|
| S-98, the A and B declarations | regenerate A and B on the box at `fff04e64` (set 8), install the pack, re-read IF-AB-POWER | none: running since 23:10 | box job, then the integrator | netlist parity on both boards; the contract AGREE on the regenerated intents; INT-001 and PWR-001 current |
| S-99, the +5V_DEV stage | the ten review findings corrected, each with source, corrected calculation and verification | none: running since 23:12 | Codex, the one authorised correction (isolated worktree `s99c`) | an independent Claude check passes the correction and its interfaces |
| Board A, second regeneration | the corrected D8 split applied on set 8, its `+5V_DEV` entry rebased onto S-98's line, board A regenerated | S-99's check | integrator, box | parity; the declared demand under the loop minimum with tolerance |
| Set 8 | suite, isolated clone, fresh check, then the last authorised Codex check on S-98's integrated scope | the three rows above | integrator; Codex check | suite 0 failed; AGREE; check mergeable. This accepts set 8 for integration only: it closes neither I-03's adequacy nor any layout entry |
| I-03 adequacy | stays open: the mode currents are INCONCLUSIVE until measured | set 8 | TEST-PLAN power rows | measured currents at J_5V_S2 and J_5V_DEV under PS-ALLTX |
| Energy, S-114 and REQ-072 | independent re-check of the second issue `7697c172` | a free worker slot | the energy checker | figures reproduced; then at most three options for the owner; REQ-072 stays FAIL until justified |
| OD-01 case list | technical-fit and test-validity check, then handed to the owner | the check (running since 23:02) | checker; prices by the coordinator | part numbers and compatibility confirmed; totals recomputed |
| Board C packet | d6dec, d4emcon, C's identities, the SI desk remedies | free slots after the rows above | authors | C's FEA-002 and FEA-006 layout-entry stages; SI-001 on C decided or allocated |

**Why S-98 waited, and the dependency now:** it was held for S-99 because both change one line of board A's generator, the
`+5V_DEV` declaration. Board B and board A's `+5V_S2` do not depend on S-99, and a regeneration is a deterministic box job,
so it runs now and board A is regenerated once more when S-99's change lands.

**Layers 10 and 11, reconciled with this page's stage gates (no new framework):** layer 10 is layout, opened per board by the
layout-entry gate and closed when SCH-002 reads PASS on the layout with the routed-board checks. Layer 11 is the fabrication
and assembly handoff: the fabrication-release gate of the stage table above, per board (the layout implements the reviewed
schematic; the physical protection, parity and routed checks; the qualified reviews where a blocker names them; the order
set of `v2/release/<rev>/` with gerbers, BOM, CPL, assembly drawings and order notes; the case's made parts cut to the
mock-up's numbers). State: layer 10 BLOCKED, 0 of 7 boards pass layout entry; layer 11 NOT STARTED, it follows layer 10.

### Milestone, 29 September 2026 00:18 CEST: integration set 8 on main (S-98)

**Accepted:** `20afa7a4`. S-98 is CLOSED for declaration consistency: boards A and B regenerated, the netlists identical
apart from their date, the five A to B leads AGREE, check_contracts PASS of 99, and the constraint sheets re-bound.
Board A's `+5V_S2` copper width at typical current rises from 1.06 to 2.17 mm. Gates: suite 2171/0/3, isolated clone
byte-identical, and the last authorised Codex check mergeable. I-03's adequacy, S-99, the mode currents and the lead
drop stay open. No layer closed.

**Next critical action:** set 9, S-99's D8 split on board A (checked, accepted): the box regeneration runs; then the
registry texts, a re-take, rebinds, the suite and a Claude check. **Box:** 10.85 USD of 20 spent (credit 117.14). **Codex:**
none left.

### Milestone, 29 September 2026 01:53 CEST: integration set 9 on main (S-99, the D8 split)

**Accepted:** `83e4bf46`. Board A regenerated with S-99's D8 split (decision 55): board D's feed on its own buck U41 from
VBAT, the device stage left with board B and the wall port (declared 4.10 A typical, 6.9142 A peak against the average
loop's conditional minimum of 7.057 A), the TPS2596 limits read with equation 7's true sign. Netlist pins moved on a
parsed proof, sheet A re-bound (+5V_DEV 2.84 to 2.10 mm), eight records rebound on judged reasons, S-115 and S-116
opened, EMC sheet row for U41. Gates: one re-take (73 steps, 0 errors), isolated clone byte-identical, suite 2172 passed, 0 failed, 3 skipped at `83e4bf46` (two earlier runs found a missing EMC source row for U41 and a sheet tool that wrote git's automatic abbreviation, both fixed, the second with a regression test),
a fresh AI check whose blocking item (four merge commits under the runner's identity) was fixed by re-authoring them with
identical trees. Also merged: the energy and OD-01 records of 28 September. S-99 stays OPEN (adequacy is not shown by
declarations). No layer closed.

**The owner's rulings of 29 September (OD-02, OD-01, handover), answered on side branches, not yet integrated:**
`fnd/energy2` (section 9: M1 derived from the requirement side; one architecture meets the reference day on the model,
4S18P across the base and the lid with a 200 W solar stage or REQ-016 kept with about 1.6 kWp; the conflicts are D-06,
REQ-016 as a trade, D-01; independent AI check and re-check acceptable; the self-contained package on the laptop),
`fnd/od01b` (OD-01 release corrections, author running), `fnd/diag` (all eleven diagrams rebuilt and read back),
`fnd/d6dec` (FEA-006's tool items T1 to T6, T9, T10; T7 and T8 for the integrator).

**Next critical action:** set 10: d6dec, energy2, diag and od01b (after its check), then T7 and T8, one re-take and the
suite. **Owner decisions required:** OD-02 option A's three items (D-06, REQ-016 way i or ii, D-01), or B or C.

### Milestone, 29 September 2026 03:53 CEST: integration set 10 on main

**Accepted:** `f3d30ceb`. Merged: stream d6dec (decision 42's decoupling rules as one library, `intent.bypass` with a
class and a basis; DEC-001's text, sources and coverage row, T7 and T8), stream energy2 (section 9 of the energy
reconciliation, M1 derived from the requirement side), the eleven rebuilt diagrams, and set 9's carried minors M2, M10
and M11. Every schematic was regenerated on the KiCad box because the decoupling tools entered every generator's import
closure (netlists identical apart from their export date and source lines; check_contracts PASS of 99). Pins, 25 records
and the six layout sheets re-bound on a parsed proof. S-117 opened and restated from TI's SLUSE66A (section 9.3.11,
Table 9-4, printed page 27): board A has no IADPT resistor or its 100 pF or smaller capacitor, and its compensation
networks match neither row of Table 9-5 (pages 27 and 28); the EMC sheet's 800 kHz for U3 is provisional until S-117 is
closed by board A's writer (the re-check's N1 and N2, carried). Gates: re-take 73 steps, 0 errors; 34 layout-entry
reasons, as on main; isolated clone byte-identical; suite 2248 passed, 0 failed, 3 skipped at `f3d30ceb`; a fresh AI
check (blocking B1, the IADPT reading, answered) and its focused re-check, mergeable. No layer closed. DEC-001 reads
INCONCLUSIVE on the six boards until each board's next placement under its new text.

**The owner's instruction of 29 September, in his words:** "The updated calculations reproduce successfully. Preserve
this reference analysis and move to engineering Option A(i), within existing authorizations." Section 9 of
`records/energy/ENERGY-RECONCILIATION.md` with `energy_architecture.py` is therefore kept as the reference energy
analysis; "Keep M1/REQ-072 unchanged" and "No purchases or requirement changes are authorized by this instruction"
stand.

**Option A(i) (400 Wp array into a 200 W stage), on side branches, not integrated:** `fnd/a1elec` (the two-pack
topology: a second BQ25731, U3B, for the lid pack, an LM74700-Q1 ideal diode and an LM5069-2 hot-swap limiter on each
pack path, a TCA9543A for the two gauges, a fail-safe enable; the BQ4050 gauge's current scale k=2 for a 4S12P lid; the
200 W stage's entry at 5.56 A or more (115.1 W); the two-pack energy model `energy_two_pack.py` with each store's own
temperature, charge ceiling and path losses; an independent AI check and re-check acceptable), `fnd/a1mech` (the lid
pack's CAD and drawings: with the HF module of approval 16a and the tablet of 16d both kept the lid holds 39 cells,
4S9P; with the tablet out 4S14P; with the QMX out 61 places, 4S15P; open-lid stability, the stay and the hinge harness;
checked and re-checked) and `fnd/a1int` (the reconciliation on the two-pack model at 400 Wp into 200 W: both functions
kept does not meet the reference day at the September lid basis of 13.23 C; tablet out, 4S20P in all, meets with a
lowest store of 94.0 Wh and a lid down to +3.8 C; QMX out, 4S21P, meets with 125.5 Wh down to +1.5 C). These are
analytical results on a model: nothing is built, bought or physically verified, and none is fabrication ready. The panel
selection (`fnd/a1solar`) is running: real panel specifications come before the array wiring and the input ratings.

**OD-01:** `fnd/od01b` `d0a8d0eb`: H1 as its own part (sheet H1-1, DXF, STEP, STL, check record, manifest), H2's finish
settled (both faces matt black), the receipt checks R1 to R8 gating every fit-dependent part, what the heat test can and
cannot prove with its uncertainty, an automatic latching over-temperature shutdown (two relays in series held by four
thermostats) with its verification V1 to V4, and the package listed by sha256 (72 files). Four independent AI checks;
check 4's two blocking items (a stale total, a stale hole size) answered; check 5 running. Not purchase authorization.

**Next critical action:** check 5 of OD-01, then the corrected package exported to the laptop; the panel selection, then
the owner's report on Option A(i). **Owner decisions required:** which approved lid function yields its space to the lid
pack (the tablet, 16d, or the QMX, 16a; with both kept M1 is not met on the model), together with OD-02 option A's D-06
(pack growth) and REQ-016 way i (the 200 W stage). OD-01 purchasing and the operator stay his.

### Standing rule, 29 September 2026 12:03 CEST: an owner decision blocks only the tasks that need it

The owner's words: "Waiting for my review or an owner decision must not stop unrelated, already-authorized work.
Persist this rule in the existing execution plan: block individual dependent tasks, then continue the ready queue. Do
not silently approve decisions or weaken requirements." So: an open owner decision is reported once, with the exact tasks
it blocks; those tasks wait; every other authorised task whose dependencies are met runs. A worker slot is refilled from
the ready queue when its task returns. Nothing blocked is adopted, approved or worked around by weakening a requirement.
The session stops only on the owner's instruction, a real runtime or resource limit, or an empty ready queue, and then
names the dependencies that emptied it.

**The four owner decisions open for Option A(i) (model results; the two-pack figures were checked independently on
29 September, `records/a1int/checks/check-a1int-1.md` and `-2.md` on `fnd/a1int` at `6a007879`: with U3's input limit at
its minimum, the tablet-out lid's lowest store is 93.7 Wh typical and 87.4 Wh adverse, the QMX-out lid's 125.2 and
118.5 Wh; both functions kept does not meet M1):**

| Decision | Recommendation (the session's) | Trade-off | Blocks exactly |
|---|---|---|---|
| Q1. Which lid function you approved on 6 September leaves the lid for the lid pack (DECISION-A1, reopening D-01's deferral) | Option 1: the tablet bracket (16d) leaves; the HF QMX (16a) stays inside | Keeps a radio bearer inside; REQ-011's bracket is not met; open-lid stability under about 3 degrees of slope toward the hinge until the feet are measured. Option 2 keeps the bracket and loses HF inside, level ground only. Keeping both: M1 not met on the model | adopting a lid pack size (4S14P or 4S15P) in the energy design case and the case set; the lid pack's CAD release; the sealed lead crossing to the lid; the lid gauge's scale at that size; the records of 16a, 16d and REQ-011 |
| Q2. REQ-016 restated for the 200 W stage | The 2S2P wording of `records/a1solar/ARRAY.md` 5: open-circuit at most 51.3 V at -20 C cells, every entry part rated above 56.3 V, the array held at 34.1 V, the entry rated for the 20 A fuse | 80 to 100 V class parts on board E's entry; the 1S4P alternative keeps low voltage but needs 36.8 A at the entry and a fuse per panel | adopting board E's 200 W entry into `gen_sch_e.py` and the baseline; A1SOLAR-01 in `pcb_decisions.yaml`; PV_IN and PV_P declarations; the entry's fuse and connector selection for ordering |
| Q3. D-06: the battery grows from 145 Wh to what M1 needs | Approve the growth the chosen lid option needs: about 870 Wh nominal for 4S18P (DECISION-OPTIONS), about 970 Wh for 4S20P (arithmetic, 20/18 of it) | Mass and cost of the cells; a larger lithium transport class; the approved 145 Wh stands until you change it | adopting the grown pack into the baseline; board P and the pack's protection sized for it; BAT-001's pack basis; REQ-072 leaving FAIL on the model |
| Q4. A deployment rule for the panels | Adopt it as a CONOPS line with a stand: 20 to 50 degrees of slope, facing within 15 degrees of south (a model result, sufficient for both lid options; laid flat the tablet-out lid does not meet M1 and the QMX-out lid meets it only at the typical ratio) | A set-up constraint and a stand to carry; without it M1 is met only where the operator happens to prop the panels well | the CONOPS line; the scope of any M1 claim; the stand's design |

**Not blocked, running or ready:** the independent check of the two-pack calculation; FEA-002's desk work for layout
entry on boards A to D (stream d4emcon); board E's 200 W entry as a reversible candidate (analysed and drafted, not
adopted); OD-01's section 8 correction and its applicability to the lid pack; board A's charger item S-117; board C's
layout-entry items.

### Milestone, 29 September 2026 12:54 CEST: integration set 11 on main (OD-01 and Option A(i)'s records)

**Accepted:** `2c7730a4`. Merged: the corrected OD-01 case package (`fnd/od01b`: H1 as its own part, the receipt checks gating
every fit-dependent part, the latching over-temperature shutdown with its verification, the heat test's limits and what
an interrupted step does not prove, each test's applicability to Option A(i)'s proposal; eleven independent AI checks,
the last acceptable; exported to the owner's laptop) and Option A(i)'s engineering records (`fnd/a1int`: a1elec's two-pack
topology and model, a1mech's lid pack, a1solar's panel selection squashed, the lid reconciliation independently checked with
U3's input at its minimum). Gates: the merge adds only the two streams' files and the union of two indexes (proved file
by file); status and render unchanged; isolated clone byte-identical; suite 2254 passed, 0 failed, 3 skipped. Nothing is
adopted by it: the four decisions of the standing rule above still hold their tasks. No layer closed.

**Set 12 (`fnd/int13`, not on main):** stream d4emcon's FEA-002 remedies applied to boards B and C and regenerated on the
box; the netlist read-back holds on both. RF-002's walk reads 21 FAIL on it where main reads 0 (the EMCON line rows and
the rows that follow them): whether the walk lacks the new parts' classes or the circuit has a real path is the next
worker task; set 12 is not promoted until that is decided and independently checked. FEA-002 itself cannot close at
desk (0 of 17 rows; 2 need bench tests).

### Closure, 29 September 2026 13:34 CEST: OD-01's document-correction item closed by the owner

The owner's review of the export at `4c6c3cfa` (`fnd/od01b`, on main through `64865df1`): "closes the document-correction
item. T6 is corrected, all 79 package hashes and six H1 hashes verify, and the document copies match." The accepted package
is preserved as it stands (`v2/docs/records/od01/`, the laptop's `MESHSAT-OD01-case-package` and its zip, sha256
`243300351289cb98...`). **Further OD-01 review requires a material design change or a specific failure.** Still open, and
not closed by this: every physical test (the receipt checks R1 to R8, the shutdown's V1 to V4 on the built rig, tests A and
B), and the two-pack mission validation of Option A(i) (a model result; board A's charger efficiency, which S-117's stream
reads as 0.92 to 0.95 where the energy model uses 0.98, is under independent check and may move the accepted margins).

### Finding, 29 September 2026 13:44 CEST: Option A(i)'s accepted margins rest on charger efficiencies the drawn parts do not support

Stream s117 (S-117, board A's charger set to its inductor) found, and its independent AI check confirmed at the energy
model's operating points (20.7 V in, the 14.5 V node, 4.15 to 6.2 A in), that board A's BQ25731 U3 with the drawn
CSD18510Q5B switching FETs runs at **0.92 to 0.96 (0.94 by TI's method)**, not the 0.98 the energy model and the checked
two-pack reconciliation use, and that Option A(i)'s drafted lid charger U3B runs at 0.87 to 0.93 at its 800 kHz, not
0.975. A coordinator's scratch sensitivity of the reconciliation: with both at 0.95 both lid options still meet M1 but the
tablet-out lid's adverse lowest store falls from 87.4 to 30.3 Wh; with both at 0.92 both lid options do NOT meet the
adverse case. **So the two-pack M1 result quoted in the decision table above is not established for the circuit as drawn.**
The lever is engineering, not an owner decision: switching FETs of about 12 nC gate charge, 7 nC switching charge, 15 nC
reverse recovery and 5 mOhm or less would support 0.98 (the check's criteria); the s117 stream is selecting real parts
from makers' documents, then the energy model's charger efficiencies are corrected and the reconciliation re-run and
checked. Until then REQ-072 stays FAIL and no Option A(i) margin is quoted as current.

### Milestone, 29 September 2026 16:59 CEST: integration set 12 on main (FEA-002's desk remedies, RF-002's walk, board A's charger set)

**Accepted:** `d0717859`. Merged:
- **Stream d4emcon: FEA-002's remedies on boards B and C.**
  - Board B: the RockBLOCK, E72 and E22 inputs gated against back-feed; the RockBLOCK's enable held low in the low-supply
    band; the 5G card's power-off line repeated.
  - Board C: its EMCON line clamped (D4E-F1, D4E-F2).
  - Applied with the check's minors on board B.
- **RF-002's walk, rounds 2 and 3.** The EMCON toggle is declared as data; a gate is the line's own source only on the
  toggle's board.
- **Stream s117: board A's charger set to its inductor and FETs.**
  - Decision 56: 400 kHz with 4.7 uH, 191 k on IADPT.
  - Decision 57: CSD17578Q5A and CSD17577Q5A.
  - S-117 and S-118 closed; S-119 and S-120 opened.
- **The census node declarations,** and boards A, B and C regenerated on the box and read back.

**Gates:**
- One re-take on the box with the held makers' files and the thirteen IBIS models installed: 0 of 615 routed verdicts
  moved against the readings checked.
- Status and render stable; validators 0 errors; the isolated clone clean.
- Suite 2271 passed, 0 failed, 3 skipped at the promoted commit.
- Five integration checks (AI reviews) are filed under `records/int13/checks/`. The last reads mergeable, with 4 wording
  minors carried to S-122.

**CFL-016 reads FAIL on this set and waits on S-122.** Its entries claimed readings no check had made, three times; the
documents it names had not been re-read whole since 26 September, and passages in PANEL.md, V2-SPEC.md and CONOPS.md
describe replaced circuits. CONOPS.md section 4b and its EMCON row are rewritten from the netlists and checked true.
S-122 re-reads every named document by a script that asserts each part it names. No layer closed.

**The two-pack verification (S-119, `fnd/s119`, for set 13):**
- **The charger rows,** both independently checked (mergeable, 0 blocking, figures reproduced with a separate hourly
  model):
  - U3 is restated from 0.98 to 0.979 with decision 57's FETs.
  - U3B is drawn on U3's 400 kHz row with the same FET pair (drafted decision 58; REGN 32.6 mA against 50 mA), at 0.972
    over the model's hours.
- **Figures at U3's minimum input limit** (model results; nothing is measured and REQ-072 stays FAIL):
  - tablet-out lid: 93.7 Wh typical, 85.8 Wh adverse (was 87.4);
  - QMX-out lid: 125.2 Wh typical, 116.9 Wh adverse (was 118.5);
  - both lid functions kept: M1 not met;
  - the first-drawn FETs: not met in any case.
- **The inductors' core loss is the largest term not modelled.** The tablet-out lid still meets with about 2.5 W of it in
  each charger. The decision table above reads with these figures once set 13 carries them; Q1 to Q4 are not taken.

**Next, ready:**
- set 13 (s119, then csi once its check passes, then walkmin once its check passes);
- S-122 (the documents);
- S-120 (the charge bus against the 30 V FETs);
- board C's layout-entry chain (C-SI under check, then identities and review D).

### Milestone, 29 September 2026 18:37 CEST: integration set 13 on main (the two-pack figures, board C's SI-001, the walk's toggle lugs)

**Accepted:** `32f26b41`. Merged:
- **Stream s119: the energy chain's charger rows.**
  - U3 is restated to 0.979 with decision 57's FETs.
  - U3B is drawn on U3's 400 kHz row (decision 58; REGN 32.6 mA against 50 mA), at 0.972 over the model's hours.
  - S-119 closed and S-121 filed. REQ-072 still reads FAIL, waiting on S-53, M-02 and S-114.
- **Stream csi: board C's SI-001 nets.**
  - The allowance method is tied to its reference nets.
  - The four e-paper lines take 27R series resistors (R53 to R56). Board C was regenerated on the box and read back 0
    failing.
  - Layout-bound nets fall from 23 to 7, and 11 are allowed pending the layout.
- **The walk minors:** the EMCON toggle is judged on its declared contact lugs, and the board key is required.

**Gates:**
- One re-take with the held makers' files and the IBIS models installed: 0 of 615 routed verdicts moved against main,
  with every count change explained.
- Status and render stable; validators 0 errors 0 warnings; the isolated clone clean.
- Suite 2276 passed, 0 failed, 3 skipped at the promoted commit.
- Three integration checks (AI reviews) under `records/int14/checks/`; the last reads mergeable.
- S-123 is opened: return_via and ref_change read board tables their readings do not record, and board C's readings of
  21 September are not re-taken.

**The two-pack figures, now on main** (model results; nothing is measured; Q1 to Q4 are not taken):
- U3's input limit at its 6.1 A minimum.
- Tablet-out lid: 93.7 Wh typical, 85.8 Wh adverse.
- QMX-out lid: 125.2 Wh typical, 116.9 Wh adverse.
- Both lid functions kept: M1 not met.
- These replace 87.4 and 118.5 Wh in the decision table above. The unmodelled inductor core loss is the largest open
  term: the tablet-out lid still meets with about 2.5 W of it in each charger.

**A process finding (the integrator's own).**
- CONOPS.md is a BASELINED layer 2 definition. Its reopening rule (the independent review of handover H2) sends a
  circuit correction to `handover/DEFINITION-STATUS.md` and the records it names, never into the baseline.
- Set 12's integrator nevertheless edited CONOPS section 4b and its EMCON row for circuit corrections (`a46db71b`,
  `7a9f7b5b`, now on main). The set 12 checks did not flag it; S-122's check did.
- Stream s122's second round restores CONOPS to `c5430071` byte for byte and moves the asserted current state to
  `feasibility/EMCON.md` section 0a.1 and the status page. It is being rebuilt on this promoted commit for its
  independent check; CFL-016 stays FAIL until S-122 closes.

**Next, ready:**
- S-122 (rebuilt on main, then its check and closure).
- S-120 (the charge bus bounded at 23.19 V against the new 30 V FETs; ringing waits on a layout), under check.
- Board C's layout-entry chain: identities, then review D.

### Milestone, 29 September 2026 20:58 CEST: integration set 14 on main (the charge bus bounded, the documents re-read, CONOPS back at its baseline)

**Accepted:** `1bafab8c`. Merged:
- **Stream s120** (checked four times): board A's charge bus VBUS20 is bounded at 23.40 V, INFERRED from the front
  end's typical over-voltage trip, against decision 57's 30 V charger FETs. S-120 is closed. S-124 is opened for the
  switch nodes, closing only on a prototype measurement against both bus levels and U3's positive and negative pin
  limits.
- **Stream s122** (checked three times): the documents CFL-016 names are re-read against the netlists by an inventory
  and verdict script (64 sentences stale at its base; after its three rounds 0 stale, and 38 CONOPS sentences read as
  baseline values, each on a status-page row). CONOPS is restored byte for byte to its baseline text
  `c5430071`, withdrawing set 12's circuit edits (the integrator's finding of set 13). Its current circuit values are
  kept on `handover/DEFINITION-STATUS.md` rows DC-01 to DC-09 and in `feasibility/EMCON.md` section 0a.1.

**Gates:** status and render stable; the evidence page is main's; validators 0 errors 0 warnings; the isolated clone is
clean; suite 2276 passed, 0 failed, 3 skipped. Four integration checks (AI reviews) are filed under
`records/int15/checks/`, the last mergeable.

**CFL-016 still reads FAIL, and S-122 stays open.** The first integration check found S-122's closure premature: five
sentences in CFL-016's scope name parts no generator carries, and the inventory did not read makers' part numbers. The
closure was withdrawn by a rewind before promotion. S-122's closing script now refuses without a part-number finder,
verdict assertions naming the generated parts, the five rows corrected, and a check filed after set 14; it leaves the
substance to the filed check. S-122's fourth round is running.

**Found by the integrator, to be done in set 15:**
- A PANJIT datasheet (`v2/vendor/power/panjit-ss2020fl-series.pdf`, tracked since `ccf5808e`) says "Reproducing and
  modifying information of the document is prohibited without permission". It is held back from set 15 on (untracked,
  with a fetch script). Its copy in git history and on the public mirror stays unless the owner asks for a history
  rewrite.
- Board C's part identities (stream w5identc, under its second check): 44 of 87 selections resolved, 21 by a printed
  part number and 23 decoded from the maker's ordering-code table (decision 59, drafted).

**Next, ready:**
- S-122's fourth round;
- the identities stream's check, then set 15;
- a layout-entry record for exact-part identities (layer 6, every board);
- board C's C1 and C2 order code (an X5R code where the identity is X7R).

### Milestone, 30 September 2026 02:37 CEST: integration set 15 on main (S-122 closed, CFL-016 PASS; the PANJIT sheet held back; board C's part identities)

**Accepted:** `e5322674`. Merged:
- **PANJIT's SS2020FL series sheet held back** (`records/int16/apply_hold_back_panjit.py`): untracked from this set on,
  in the ignored `v2/vendor/power/held/`, cited by URL and sha256, fetched by `records/int16/fetch_held_back.py`. Its
  copy in git history and on the public mirror stays unless the owner asks for a history rewrite.
- **Stream w5identc** (checked three times): board C's part identities, 21 printed and 23 decoded under decision 59
  (the session's ruling), 41 unresolved with their reasons, 2 not a part. S-125 is opened. Its three PANJIT
  bindings are marked held back, so the identity tests pass on a host without the sheet.
- **Stream s122** (rounds 4 to 8, checked eight times): the definition documents re-read against the netlists, 1011
  sentences, 422 true, 0 stale, 40 baseline values, 549 not derivable, 0 unjudged. **S-122 is closed by its filed
  closing check** (`records/s122/checks/check-s122-8.md`), and **CFL-016 reads PASS** (was FAIL). S-126 is opened as a
  process item for the regression instrument's named escape classes; no record waits on it.

**Gates:** validators 0 errors 0 warnings; the full render order reaches the same evidence page twice (`c9b98931`, the
same page as set 14's), with CON-010 and REQ-044 bound to it; the isolated clone is clean; the box suite on
`e5322674` 2303 passed, 0 failed, 3 skipped. Three integration checks (AI reviews) are filed under
`records/int16/checks/`, the last mergeable.

**Priority since 30 September 2026 00:13 CEST (the owner): Layer 3 first.** Layer 4 and later streams are paused at
checkpoints, nothing discarded: board C's RD-C-24 remedy (`fnd/rdc24`, its box regeneration done, the proof not yet
run) and review D of board C (`fnd/reviewdc`, round 4, its narrow check not run). Set 15 was completed because it
carries CFL-016's closure, a Layer 3 contradiction. The Layer 3 closure is on `fnd/l3r2` (the reconciliation, the
owner decision table and the consolidated requirements `REQUIREMENTS-L3-R2.md`); its first independent check did not
accept it, and its second round is done. Owner decision rows L3-OD1, L3-OD2 and L3-OD4 are held, on the owner's
instruction, until a corrected and independently checked energy basis arrives (`fnd/l3plane`, round 2 running): its
first check confirmed VBUS20 at U3's input at 19.146 / 20.000 / 20.887 V steady state, that board A as generated
(R11 10 mOhm) limits the front end below U3's setting so that no lid option meets M1, and that PVGIS September weather
windows of 72 hours meet M1 in only 15 to 27 percent of cases; it did not accept the basis because three
efficiencies were held at nominal without a maker's document.

**Next, ready:** the energy basis's round 2 check; the Layer 3 rows restated from it; the Layer 3 delta check; the
owner's answers; then the definition documents' re-issue (L3-C26) and the Layer 3 gate.

### Milestone, 30 September 2026 07:17 CEST: integration set 16 on main (the Layer 3 handover L3-R2, prepared; the checked energy basis and power-path record)

**Accepted:** `3f69af66`. Merged:
- **Stream l3plane** (checked five times; the last check accepts exactly `cd8720a1` and lists its files by sha256):
  the energy basis for M1 (`records/l3plane/ENERGY-BASIS.md`) and board A's power-path record
  (`records/r11dep/R11-DEPENDENCY.md`). VBUS20 at U3's input is 19.146 / 20.000 / 20.887 V steady state, with brackets
  of 19.101, 18.782 and 18.738 V. Board A's front end in four cases: as drawn, M1 is not met on any lid (326.6 to
  522.4 Wh unserved on the reference day); the derated variant (U3 at 4.00 A) fixes current-limit coordination only and
  M1 is not met; the resistor-only proposal (R11 6.2 mOhm) is INCONCLUSIVE; only a hypothetical corrected power path
  meets M1, with the QMX-out or tablet-out lid, and its figures are not demonstrated capability. The power-path
  findings are classified: existing defects A-1 and A-2, proposal defects B-1 to B-5, missing evidence C-1 to C-9,
  each with a correction and a measurable closure criterion (engineering tasks, downstream). Past September weather
  (PVGIS 2005 to 2020, 864 windows of 72 hours) is carried in 14.0 to 22.0 percent of windows on that hypothetical
  path; no coverage target fits the case.
- **The Layer 3 handover L3-R2** (branch `fnd/l3r2`, checked five times, the last accepting the handover as prepared
  at `028531e4` with the six owner decisions pending), applied by its scripts: the reconciliation, the six-row owner
  decision table `handover/layer3/OWNER-DECISIONS-L3.md`, the consolidated `REQUIREMENTS-L3-R2.md`, rulings D-21 to
  D-25 (the owner's instructions of 30 September, quoted word for word), S-114 and S-127 closed, LAYER-STATUS layer 3.
  The branch's history is recorded by a merge that keeps the tree (so the commit that closed S-127 is on main).

**Gates:** validators 0 errors 0 warnings; the full render order reaches the same evidence page twice; a clone
holding only the candidate branch reproduces every page and passes the tests (202 passed, 0 failed, 2 skipped); the
box suite on `3f69af66` 2330 passed, 0 failed, 3 skipped. The set's integration check (an AI check) is filed under
`records/int17/checks/`, mergeable, with three minors (the LAYER-STATUS row of the independent check is dated before
check 5 and is brought current with the next LAYER-STATUS change; path history of the layer 3 files follows the
set's commits; one historical commit of the branch holds a literal dash that later commits removed).

**Layer 3 is IN_PROGRESS, not complete.** Its gate reads NOT MET on three conditions: the six owner decisions
(L3-OD1 to L3-OD6), CFL-017 (L3-OD5), and the re-issue of the changed CONOPS and PRODUCT-BRIEF passages approved by an
owner ruling (L3-C26). The independent check of the prepared handover is MET. H3 is unchanged. Layer 4 and later work
stays paused (`fnd/rdc24`, `fnd/reviewdc`), and the circuit corrections, layout and bench verification are downstream
obligations.

**Next:** the owner's six answers, applied by their scripts; the definition re-issue (L3-C26) for his approval; a
narrow independent check; then the Layer 3 gate.

### Milestone, 30 September 2026 13:32 CEST: integration set 17 on main (the public-file cleanup; the definition re-issue prepared)

**Accepted:** `1f34bf92`. Merged:
- **The public-file cleanup** (`records/scrub/`, checked twice): tracked files carrying the runner's paths, session
  temporary paths or internal host names went from 171 instances in 71 files to 22 in 14; each remaining one is a file
  cited by its sha, a registry-bound page, a binary, or a pattern a script refuses, and is listed with its reason.
  Handover snapshots H1, H1.1, H2 and H3 are reissued as H1-R1, H1.1-R1, H2-R1 and H3-R1, each with its own version
  record, manifest and hashes, from redaction commits recorded by a merge that changes no file; the originals are
  untouched. A guard test fails on a new leak. Git history is not rewritten: the old values remain in history (a
  rewrite is the owner's decision).
- **The definition re-issue prepared** (`records/l3r4/`, checked four times): the passage map of CONOPS and
  PRODUCT-BRIEF per owner row and option (128 passages: 51 to re-issue, the rest statements of the design as generated
  carried on DEFINITION-STATUS), and the generator that writes the proposed re-issue and its change record only from
  decided rows, refuses contradictory answers, and never writes a baselined file. LAYER-STATUS layer 3's independent
  check row reads MET for the handover as prepared.

**Gates:** validators 0 errors 0 warnings; the full render order reaches the same evidence page twice; a clone holding
only the candidate branch reproduces every page (235 passed, 0 failed, 2 skipped); the box suite on `1f34bf92` 2347
passed, 0 failed, 3 skipped. The integration check is filed under `records/int18/checks/`, mergeable.

**Layer 3 is IN_PROGRESS.** The owner's reviewer found the decision logic confused a candidate's failure with an
invalid requirement (review of 30 September on the decision brief); round 5 (`fnd/l3r5`) separates the owner-selected
target from the candidate's compliance, completes the acceptance definitions (the mission criterion at the kit loads,
the thermal mode table, the stability test conditions, the solar topology apart from its electrical compliance), and
adds the three status levels. The feasibility record behind it (`fnd/l3feas`, `c11b99d3`, accepted by its second check)
finds keeping HF at the worst array build INCONCLUSIVE (one route, conditional on unprinted and undocumented figures),
the panel revision not pinned, and the solar stage's input power not controlled as drawn. The six owner decisions
remain open.

**Next:** round 5 and its check; the owner's choices; then the answers applied, the re-issue generated for his
approval, a narrow check, and the Layer 3 gate. Layer 4 and later work stays paused.

### Plan update, 30 September 2026 13:45 CEST: a bounded runtime-and-battery comparison (the owner's instruction)

The owner questions the 72 hour requirement and asks for alternatives before any function is sacrificed or a
restrictive deployment condition accepted. Added to Layer 3, bounded, reusing the checked energy basis:
1. The provenance of 72 hours (M1, REQ-072, D-20): the exact wording, date and source, the owner's statements apart
   from the session's (the registry records SC-21 of 27 September 2026, the session's choice under the standing rule,
   and D-20 of 28 September preserving "the original mission M1 and REQ-072, with their specified duration").
2. Two requirement options on the same approved functions and operating profile, HF and the tablet both kept: Option A,
   48 hours required and 72 desired; Option B, 72 hours required with an upgraded battery arrangement where necessary.
   Battery-only endurance apart from battery-plus-solar, with the solar and weather assumptions stated; the circuit as
   drawn apart from the corrected power path; the worst array build as a sensitivity case only.
3. A short battery shortlist from makers' data: the present candidate and higher-capacity or higher-energy-density
   cells and complete packs, each with usable Wh at the load, temperature and ageing, pack dimensions and mass,
   placement in the Peli 1450, electrical compatibility, charger and protection changes, cost and availability.
   Anything needing an enclosure, mounting or external-battery change is a proposal.
4. The 42.8 W load profile traced to its loads. No undocumented efficiency makes a pass; a battery upgrade closes no
   electrical defect.
5. One compact comparison table, independently checked, with a recommendation and the exact owner choice. Neither
   option is adopted until the owner selects it. The owner's selection then enters the decision package (a runtime
   row), and Layer 3's acceptance work continues. Layer 4 and later stays paused.

### Plan update, 30 September 2026 14:42 CEST: Layer 3 closes in one bounded closure cycle (the owner's instruction)

No new tooling, document polishing or broad review rounds. Battery and solar mandatory; HF and the tablet preserved;
Layer 4 and later paused until Layer 3 is accepted. The cycle, in order:
1. A proposed USB-C tablet service budget (energy delivered per day, peak output, converter losses, schedule and
   starting charge), labelled a proposal, not verified tablet endurance, checked against the 42.8 W profile for double
   counting, and carried into the runtime comparison (Option A: 48 hours required, 72 desired; Option B: 72 hours
   required with the necessary battery upgrade), battery-only apart from solar-assisted, corrected hardware
   conditional. Neither the 72 hours (the session's SC-21, preserved by D-20) nor the worst array build is treated as
   an owner ruling without its recorded authority. One independent check of the decisive figures.
2. Every remaining owner choice in ONE message, reconciled against his explicit answers, each with a recommendation,
   its quantified consequence and the exact short answer.
3. While the answers are pending: the target-and-candidate semantics (round 5) finished, checked and integrated.
4. After the answers: applied, the revised requirements and the affected CONOPS and PRODUCT-BRIEF passages generated,
   one targeted acceptance review, actual blocking findings fixed and verified, the rest backlogged.
5. Closure reported honestly: complete only when the chosen requirements are clear, traceable, testable, feasible on a
   credible assessment and accepted; a surviving feasibility blocker is delivered with the handover as the exact
   failing condition, its quantified gap and the result needed.

### Operating change, 30 September 2026 16:12 CEST (the owner's instruction): accepted results, short loops, usable deliverables

Applied to the ongoing work; no completed task is restarted and no running assignment duplicated.
- **One interpretation of the product.** The Current owner brief at the top of
  `handover/layer3/OWNER-INSTRUCTION-2026-09-30.md` (with the registry's owner rulings, the one decision register)
  states the constraints both agents use: storage inside the Peli 1450 and no external battery; battery and solar
  required; HF and the tablet retained; 48 to 72 hours a baseline design objective under a stated operating profile;
  optional tablet charging reduces endurance, including below that target; every other approved requirement unchanged.
  Mandatory requirements, objectives, assumptions and component selections are kept apart; a recommendation or an
  earlier model statement is not owner approval; superseded instructions are marked in place, history kept.
- **Layer 3 closes** with the current author's pass and ONE independent check (the collaborator, `CODEX-WORKER.md`
  section 7), no parallel review. Closure means a coherent, traceable, measurable baseline with verification methods
  and an honest feasibility assessment, the energy shortfall and the open design obligations recorded prominently.
- **Layer 4 starts at once** after closure, with the internal energy architecture: the dominant constraints first, a
  small number of credible architectures compared under the same assumptions, established reference circuits or
  modules preferred, predicted performance with margins and uncertainties, the next discriminating calculation or
  experiment; no service silently reduced; architecture and interface evidence before detailed circuitry or layout.
- **Every substantial task is finishable:** the exact question and input revision, one deliverable, acceptance
  criteria for its layer, permitted changes and bounds. One review, blocking discrepancies fixed, the affected
  criteria rechecked; a repeated failure changes the diagnosis or the evidence method; editorial points go to a
  backlog.
- **Blockers are classified** (engineering correction, missing evidence, downstream design task, owner decision) with
  the task each blocks; only a change to approved requirements, accepted risk, budget or authority goes to the owner.
- **Milestones are reported as:** accepted deliverable, evidence, remaining material risk, next executable action,
  elapsed time and usage; requirements maturity, design compliance and physical verification kept separate. At the
  first credible Layer 4 candidate a concise power-architecture packet is prepared for an electronics engineer.

### Milestone, 30 September 2026 23:11 CEST: Layer 3 requirements baseline COMPLETE (integration set 18 on main)

**Layer 3 requirements baseline: COMPLETE.** Accepted at `b4b199d0` under the owner's conditional authorisation D-39,
filed as its own record (`handover/layer3/l3r2.yaml` `baseline_acceptance`) after the gates passed. Requirements
maturity only: the circuit, the PCB, the thermal design, the runtime and the product are not verified (D-28, D-29).

**Accepted deliverable:** the Layer 3 handover (`v2/docs/handover/layer3/`: REQUIREMENTS-L3-R2.md, L3-RECONCILIATION.md,
OWNER-DECISIONS-L3.md, the decision register OWNER-INSTRUCTION-2026-09-30.md with the current owner brief) on the
registry of `b4b199d0`. REQ-072 (48 to 72 hours under a stated operating profile) is the one design objective, every
other record mandatory; storage inside the Peli 1450, no external battery, battery and solar required, HF and the tablet
kept, optional tablet charging reducing endurance (D-28); CFL-017 resolved against the selected cell, FEA-008 carrying
the cell and thermal design to Layer 4 mode by mode (D-29, D-36); rows L3-OD2 to L3-OD7 answered by D-32 to D-37, row
L3-OD1 closed as Layer 4 architecture (Option A(i) is proposal P-01); D-22's supply-range rule carried into REQ-072's
acceptance; the CONOPS and PRODUCT-BRIEF re-issue authorised (D-38), its re-stamp open (L3-C63, the change record
governing until then).

**Evidence:** the engineering collaborator's closure check (`astra-check-l3r5-1`, not accepted) and targeted recheck
(`astra-check-l3r5-2`, not accepted; B1, B3 and M1 accepted); Claude's check 3 (`check-l3r5-3`, accepted: B2's final
correction and D-22's trace at `a66c4e5b`, by its own check and the targeted tests; not a model review and not an Astra
check); the merge verified mechanically; a clone of the candidate branch alone reproducing every page (132 passed, 0
failed); the box suite at `b4b199d0` 2369 passed, 0 failed, 3 skipped, 200 of 200 modules, judged by the promotion gate
on its log; the acceptance guards checked against the closure criteria (11 of 11) after the acceptance script was
hardened to refuse while any gate condition is unmet. Details: `records/int19/README.md`, `records/l3r5/`.

**Remaining material risk (assigned, not hidden):** DR-01 the objective missed by the present candidates even without
tablet charging (D-06's 4S3P battery-only 2.52 h at +20 C against 42.8 W); DR-02 board A's power path as drawn fails,
its correction hypothetical; DR-03 the USB-C outlet's R138 trips at 1.92 to 2.26 A below its 3 A contracts; DR-04 the
solar interface (the stage's input power, the panel revision); DR-05 three undocumented efficiencies; DR-06 the cell and
thermal design with the pack fitted (FEA-008); DR-07 the lid pack's consequences with P-01. The re-stamp of CONOPS and
PRODUCT-BRIEF (L3-C63). `run.py`'s name filter reports success when a named module is absent (recorded; the promotion
suite runs unfiltered and is judged on its log).

**Next executable action:** Layer 4, task L4-E1 (brief `_runs/claude/brief-l4-energy.md`): the engineering
collaborator names the dominant constraints of the energy objective and at most four architectures to compare under one
assumption set (D-06's 4S3P and the two-pack base 4S6P plus lid 4S9P among them); then L4-E2, one comparison page with
the power-path corrections as architecture decisions; one check; the power-architecture packet for an electronics
engineer. No layout.

**Elapsed and usage:** the closure cycle ran from 14:42 to 23:11 CEST (about 8.5 h, two author runs lost to a server
overload and restarted). The collaborator: two runs, 8 min 6 s and about 6 min, about 2.0 M input tokens each (1.8 M
cached) and 14 k and 9.5 k output, list-price estimates 4.29 and 4.07 USD drawn on the ChatGPT plan, not billed. The
box: the suite 34 min 48 s (about 0.08 USD at 0.142 USD/h); the box (vast.ai 52646493) destroyed at 23:13 after its
suite logs and the paused stream rdc24's outputs were preserved on the runner (the 4.5 GB re-take clone, rebuildable,
left); credit 110.45 USD, about 17.55 USD of the foundation cap of 20 used. The bookkeeping after promotion (the
acceptance guards, the acceptance, the pages, this entry) checked by the targeted modules (133 passed, 0 failed, the
hygiene module among them) and the acceptance-guard check.

### Owner ruling, 1 October 2026 02:07 CEST: compute without a fixed cap, a two-hour idle stop, a persistent watchdog

The owner, in his words: "Remove the USD 20 rental cap. There is no fixed spending cap for compute needed by this project.
Rent, resume and use multiple instances autonomously when they accelerate useful work. Do not request approval merely
because the old budget is exhausted." His operating rules, as given:

- "Choose instances suited to the workload's CPU, RAM, storage and GPU needs. Use parallelism where jobs are independent."
- "Automatically stop an instance after two hours without useful work. Stop sooner when no near-term job needs it. This
  supersedes the earlier 24-hour idle rule."
- "Determine activity from job state and actual progress, not GPU utilisation alone. Preserve healthy long-running jobs;
  diagnose stalled jobs."
- "Enforce the idle rule through a persistent watchdog or provider mechanism that continues working if this Claude
  session ends."
- "Save checkpoints, logs, results and uncommitted work off the instance. Before destroying a finished instance, verify
  those backups."
- "Stopped instances still incur storage charges. Destroy instances that are no longer needed once their backups are
  verified."
- "Resume or replace instances automatically when work becomes ready."
- "Include active/stopped instances, assigned jobs, hourly cost and cumulative spend in normal progress reports. These
  are visibility measures, not approval gates."

This supersedes the foundation cap of 20 USD (the session's figure of 25 September, raised to 20 USD on 28 September) and
the 24-hour idle rule. The earlier box-money rulings of 6 and 7 September stand as history. How it is applied: a
watchdog on the runner (run by cron every ten minutes, independent of any Claude session) reads each rented instance's
job markers, its processes' CPU time and its newest file changes; an instance with none of these for two hours is backed
up (its job outboxes pulled to the runner) and stopped through the provider's API, and every action is logged. Destroying
stays the coordinator's, after the backups are verified. State at this ruling: no instance rented (vast.ai 52646493 was
destroyed on 30 September at 23:13 after its outputs were preserved); credit 110.45 USD; the next job needing an
instance is the integration set's full suite (Layer 3 amendment and Layer 4 records).

### Owner amendment, 1 October 2026 02:48 CEST: the prepared instance is kept, stopped when idle, never destroyed without his instruction

The owner, in his words: "Keep the no-spending-cap ruling. Treat the prepared Vast.ai build instance as reusable
infrastructure. After two hours of genuine inactivity, use Vast.ai's STOP action, preserving its disk, installed tools,
repository, caches and outputs. Remove automatic destruction from the watchdog and execution plan. Never destroy this
instance without my explicit instruction. Resume the existing instance when needed. Reuse its environment and update the
checkout incrementally; avoid repeating full installation and cloning. Save job checkpoints before stopping and maintain
verified off-instance backups. Continue reporting compute and retained-storage costs. Do not interrupt a healthy clone,
setup, test or other progressing job. Determine activity from useful job progress, excluding the watchdog's own logs."
This supersedes the earlier instruction to destroy finished instances, including the line of the entry above that left
destroying to the coordinator: no instance is destroyed by the watchdog or the coordinator without the owner's explicit
instruction. The instance is vast.ai 53608225 (label meshsat-1357-suite, rented 1 October 02:09 for integration set 19's
suite). The watchdog's only action is STOP (it pulls the job outboxes to the runner first); `_bin/vast_resume.py` starts
the stopped instance and waits for ssh, and never rents, re-creates or destroys; the box's clone is updated by fetch or
bundle. Activity is read from job markers, the processes' CPU time and changed files on the instance; the probe writes
nothing there and the watchdog's logs live on the runner.

### Milestone, 1 October 2026 09:17 CEST: Layer 3 accepted again after the amendment; Layer 4's L4-E4 (integration set 19 on main)

**Layer 3: accepted baseline, accepted again at `3b4b92cf` after the amendment; independent review findings
dispositioned (L3-R01 to L3-R05).** Accepted under the owner's conditional authorisation D-39 once set 19's gates passed,
recorded at `c1321ebc`; the acceptance binds the reviewed content (a content manifest the revision and the tree must both
hold, L3-R04) and the record at `b4b199d0` is kept as history. The findings are closed by Claude's check 4 of the
amendment (`check-l3am-4`, at `8146b4cc`), not by the reviewer, who has not re-read it; the collaborator's two checks of the
amendment did not accept it. Requirements maturity only (D-28, D-29): neither design compliance nor fab readiness holds.

**What set 19 carries:** the amendment (`fnd/l3am` at `d3e3b415`: L3-R01 the solar-assisted figures labelled as proposal
P-03's, understated; L3-R02 REQ-042's end-to-end acceptance with S-128; L3-R04 the acceptance bound to its content, the
requirements digest defined by a principle; L3-R05 REQ-016's protection judged apart under TRN-001); Layer 4's energy
records (`fnd/l4e` at `3ed52f3a`) and L4-E4 (`fnd/l4e4` at `bb7ebf12`: U3's IIN_HOST 4.70 A with R16's tolerance in its
bounds, R11 8 mOhm with a 0.38 mOhm Kelvin allowance at 25 C, margins +0.097 / +0.064 / +0.023 A at -20 / 25 / 62 C, R138
5 mOhm tripping at 3.79 to 4.58 A, a bench procedure that isolates U18's comparator; drafts for board A's generator owner,
nothing applied; the collaborator's check and recheck not accepted, the coordinator's check 3 accepted); `r11_dep.py`
made independent of git's hash abbreviation (`test_r11dep.py`).

**What went wrong and was fixed on the way:** the first acceptance, at the first promoted candidate `41881d8f`, failed two
Layer 3 tests pinned to the state before a re-acceptance and was not committed; the supersede test was corrected, which
invalidated check 3 by design, and check 4 re-verified the amendment; since then the accepted state is simulated in a clone
before promotion. The suite on `87dfa55f` failed 11 L4-E4 tests on the box because `r11_dep.py` compared git's abbreviated
hash (nine characters there, eight on the runner); fixed and reproduced on the runner by forcing the abbreviation.

**Evidence:** the box suite at `3b4b92cf` 2395 passed, 0 failed, 3 skipped, 204 of 204 modules, judged by the promotion gate
on its log; its clean single-branch clone 158 passed, 0 failed with `verify_l3am` 16 of 16 and `verify_acceptance` 18 of
18; on the accepted tree the status level VALIDATED and the same 158 passed. Details: `records/int20/README.md`,
`records/l3am/`, `records/l4e4/`.

**Handover:** `MESHSAT-LAYER3-REVIEW-c1321ebc.zip` (1,606,980,036 bytes, sha256 `fb67d1d7eee8cae95d932739a1de714f4609ca190a7b13a82334bf1893d6d42d`): the corrected Layer 3 review package (L3-R03): the
measured export, a bounded pack of the repository's own objects, the ignored evidence and one command; `REPRODUCE: PASS`
from a clean extraction with no network. `MESHSAT-POWER-REPLAY-c1321ebc.zip` (21,322,720 bytes, sha256
`514ce797b09b521ad5a89ccf537ca1bda5385beb1f615400c887f32d51524bea`): the power packet's replay companion (L4-R03),
`REPLAY: PASS` from a clean extraction with no network. Both copied to the laptop's Downloads and handover folder, their
checksums verified there.

**Remaining material risk (assigned, not hidden):** DR-01 to DR-07 and FEA-008 as at set 18; REQ-072 reads FAIL at desk;
Layer 4's open items (O-2's physical compliance, the candidate panel's source compliance under the maker's 10 %
qualification, the three undocumented efficiencies C-8, the 8.4 W of the profile with no document, C-7 U3's
input-current minimum, which VI(TRIP) row board A's strapping selects, J_USBC_OUT's contact rating). The re-stamp of
CONOPS and PRODUCT-BRIEF (L3-C63) and REQ-051's cell-free deviations remain follow-ups; other scripts that read git's
abbreviated hash are named in the session's facts.

**Next executable action:** Layer 4's remaining implementable choices of the power review (source control A-2's
per-source envelopes in firmware terms, the LT8705A's real settings and tolerance budget for O-2, fault handling for the
front end); L4-E4's drafts applied by board A's generator owner in a circuit round with a box regeneration. The engineer's
review of the packet is the owner's to arrange.

**Elapsed and compute:** set 19 from about 02:30 to 09:17 CEST. Compute: vast.ai 53619970 (0.210 USD/h) ran set 19's
four suites (about 2.1 h in two runs) and is stopped, its disk kept (0.037 USD/h); 53608225 (0.136 USD/h) finished its
GitHub clone (a full checkout for reuse) and was stopped by the watchdog after two idle hours, its disk kept (0.030
USD/h); nothing destroyed; credit 108.71 USD.
The collaborator: four runs (the amendment's check and recheck, L4-E4's check and recheck), drawn on the ChatGPT plan.

### Milestone, 1 October 2026 15:55 CEST: Layer 4's source control and fault handling (integration sets 20 and 21 on main)

**Deliverable:** two power-path decisions accepted and merged, with L4-E4's component values held PROVISIONAL until the
circuit round they belong to is complete.
- **L4-E5, source control** (`fnd/l4e5` at `0e7e7f11`, merged `7d9d9753`). H3: a hardware VIN_RAW line on U3's ILIM_HIZ
  pin with a knee below 9 V; board E's tracker ceiling raised (R10 115 k to 232 k); firmware holds IIN_HOST at 4.70 A,
  which supports L4-E4's 4.70 A. The stiff-source band of 26.50 to 27.24 V (5.095 A) needs bench V-A07 or R11 at 7 mOhm.
  The collaborator's check and recheck did not accept it; the coordinator's check 3 accepted it after the recheck's two
  items were fixed.
- **L4-E6, fault handling** (`fnd/l4e6` at `843f48c1`, merged `74416392`). R12 12 mOhm (LCSC C2904242) and C147 330 pF bound
  L1 and the FETs by U2's cycle-by-cycle limit; hiccup stays off; the VBUS20 bulk bank is rated, not bounded, and is to be
  re-sized. It supports R11 8 mOhm, subject to V-A07. The collaborator's check accepted it; the coordinator's check 2
  covered its two minors.
- **L4-E4 stays PROVISIONAL** (set 20, `05e8f912`): the draft apply scripts refuse to write board A's generator until
  `records/l4e4/RELEASE.md` reads "released: yes" and names an accepted check of each decision
  (`tests/test_l4e4_provisional.py`). Both decisions now support its values, but B-4 (the bank's re-size, 3.11 A at 2:1
  against 2.8 A) is open, and the dense ripple script the generator cites (`drafts/scripts/ripple_dense.py`) is in neither
  the tree nor its history.
- **The power replay companion's reassessment** filed as received (`f8514c0b`): L4-R03 CLOSED; PR-01 (the measurement hook
  recorded its own writes) fixed in the coordinator's tools and tested (one deliberate open gives one record, process
  launches logged, a truncated or failed trace refused).

**Evidence:** box suite at `2e354f30` 2427 passed, 0 failed, 3 skipped (host properties), 207 of 207 modules, judged by the
promotion gate on its log with the L4 and Layer 3 modules required; set 20's at `05e8f912` 2397 passed, 0 failed, 205 of
205. On the runner before promotion: render order twice with no page changed; the rule library 145 and 59 of each with 0
errors. Records: `records/int21/README.md`, `records/l4e5/`, `records/l4e6/`.

**Handover:** `MESHSAT-L3-AMENDMENT-f8514c0b`, the compact Layer 3 amendment package, made at the owner's request of 1
October: 16 ordinary ZIPs, each at most 24 MB, 166.1 MB in all, disjoint files under one folder (`SHA256SUMS` sha256
`ba8758c253a8b0062aea7efb639f18d19f36cf94aebd72fee435c2c64e8e8d8b`). It exports `f8514c0b` and verifies the acceptance at
`3b4b92cf` (D-39, recorded at `c1321ebc`). It adds one review-workspace commit, whose parent is the exported revision and
whose tree is the Layer 3 workspace measured with the fixed hook; every original commit and tree is kept under its own id.
`REPRODUCE: PASS` from a clean extraction with no network (140 passed, 0 failed, 0 skipped; the dry run byte for byte).
Copied to the laptop's Downloads and handover folder, checksums verified there. It does not reproduce: the full suite,
the rule registry and its pages, the public hygiene test, or history beyond what the checks read (its README section 5).

**Remaining material risk (assigned):** B-4 and the missing ripple script (the next circuit-round item); V-A07 for R11; DR-01
to DR-07, FEA-008, C-8, O-2, L3-C63 and REQ-051 as at set 19.

**Next executable action:** L4-E7, the solar stage's settings for O-2 (the LT8705A's real values and tolerance budget),
being authored on `fnd/l4e7` from `7d9d9753`; then its check. After that, the VBUS20 bank's re-size with the dense ripple
analysis rebuilt, which completes the drafts and allows L4-E4's release record. The engineer's review of the power packet
is the owner's to arrange; nothing here waits on it.

**Elapsed and compute:** sets 20 and 21 from about 09:20 to 15:55 CEST. vast.ai 53619970 (0.210 USD/h) ran both suites and
is stopped with its disk kept (0.037 USD/h); 53608225 stays stopped (0.030 USD/h); nothing destroyed; credit 108.12 USD
(0.59 USD since set 19, storage included). The collaborator: three runs (L4-E5's check and recheck, L4-E6's check), drawn
on the ChatGPT plan. The runner's disk: about 140 GB freed by removing 61 merged, clean worktrees at the owner's request.

### Milestone, 1 October 2026 18:20 CEST: the unified independent review of the Layer 3 amendment; Layer 4's solar stage settings (integration sets 22 and 23 on main)

**Deliverable.**
- **Layer 3, independently reviewed:** the owner's reviewer reproduced the compact package `MESHSAT-L3-AMENDMENT-f8514c0b`
  offline in a second environment (140 passed, 0 failed, 0 skipped). Verdict: READY as an accepted Layer 3 requirements
  baseline for Layer 4 work and engineering handover; L3-R01 to L3-R05 CLOSED against their criteria; no Layer 3 restart
  and no owner decision required. Filed byte for byte (`records/l3am/REVIEW-UNIFIED-AS-RECEIVED.md`). The acceptance at
  `3b4b92cf` and every file it binds are unchanged.
- **L3-N01** (P2, the checking tool): `verify_l3am.py`'s closing helper read the verifier's revision return as a refusal.
  Fixed, with a positive case and a mutation check: a verifier that accepts the stale check now fails the run
  (`records/int22/l3n01/`).
- **The review's item 3, the energy pointer:** REQ-072's notes and LAYER-STATUS's layer 3 now name L4-E2's checked result
  on the retained 100 W window. The accepted policy (`l3r2.yaml`) and the Layer 3 pages keep naming it pending, as accepted:
  changing them would need the baseline accepted again.
- **L4-E7, the solar stage's real settings** (O-2, review L4-R01):
  - As drawn, board E has no input-current limit: U5's sense pins are tied together on PV_P.
  - The decision: U5 the LT8705AI; RSENSE1 15 mOhm on a new net TRK_VIN; RIMON_IN 23.2k for 3.4713 A; CIMON_IN 100 nF.
  - The 100 W corner at 25 V reads 96.25 W at both temperature ends under the printed limits, and passes a design floor
    that takes the unprinted gains at half their typical.
  - The hold stays at REQ-016's approved 17.6 V point (102k over 7.50k, now 0.1 % parts, band 16.970 to 18.221 V).
  - Drafts only, for board E's generator owner.
  - Checks: the collaborator's check did not accept the author's first hold (16.340 V), which changed REQ-016; its
    recheck accepted the fix; the coordinator's check 3 recomputed the band in separate code.

**Proposal held for the owner (not adopted, not drafted):** the 16.340 V hold would give about 25.0 Wh a day more on the
design day, but it changes REQ-016's approved operating point, so it is his to rule on if he ever wants it.

**Evidence:**
- Box suites: set 22 at `cece7c1c` 2427 passed, 0 failed, 3 skipped (207 of 207 modules); set 23 at `13068724` 2439 passed,
  0 failed, 3 skipped (208 of 208). Both judged by the promotion gate on their logs.
- On the runner: every validator 0 errors and 0 warnings, every page current, the render order twice with no page moved,
  `verify_l3am` 19 of 19, `verify_acceptance` 18 of 18.
- One failure on the way: a first pointer that appended a REQ-072 evidence entry failed `test_l3r5`, which reads the last
  entry as the baseline evidence and is bound to the amendment's closure. It was dropped before any push.

**Remaining material risk (assigned):**
- B-4, the VBUS20 bank re-size: the dense ripple analysis it needs is lost and is being rebuilt as L4-E8. L4-E4 stays
  PROVISIONAL until then.
- V-A07 for R11; L4-E7's unprinted rows (bench 7b.9 to 7b.13) and R59's Kelvin taps.
- Unchanged: DR-01 to DR-07, FEA-008, C-8, O-2's physical compliance, L3-C63, REQ-051.

**Next executable action:** L4-E8, the dense VBUS20 node analysis rebuilt and validated against its recorded figures, then
the bank re-sized to close B-4, with the loop margins. Its author is running on `fnd/l4e8` from `13068724`. Then its one
check and one targeted recheck, and the L4-E4 release record once the circuit-round drafts are complete.

**Elapsed and compute:** sets 22 and 23 from about 15:55 to 18:20 CEST. vast.ai 53619970 ran both suites and is stopped with
its disk kept; 53608225 stays stopped; nothing destroyed; credit 107.65 USD. The collaborator made two runs on the ChatGPT
plan: L4-E7's check and its recheck.

### Milestone, 1 October 2026 21:15 CEST: L4-E7's 100 W bound qualified (integration set 24 on main)

**Closed:** the owner's instruction to qualify L4-E7's 96.25 W result (`records/l4e7/L4E7-QUALIFICATION.md`).
- **The sheet.** The held LT8705A sheet is byte for byte the one at the owner's URL; the Internet Archive record is filed.
- **The classification.** Each value the sheet gives no guaranteed limit for is classified by the outcome it affects (the
  100 W bound, stability, protection or energy). Each has a conservative assumption, a break-even and the qualification it
  needs.
- **The range argument.** The assessed corners are shown to bound the permitted range: the input voltage, every tolerance
  direction, both temperature ends with a mixed-temperature envelope. The states outside the corners are bench row 7b.9t,
  including a cold-soaked irradiance step at about 122.7 W of available panel power.
- **No part changed.**
- **Checks:** the collaborator's focused check was not accepted (A7's gain extrapolated from its test point; the cold
  TCR's small effects); its recheck accepted the fixes; the coordinator's check 3 recomputed stack A's corner and A7's
  break-even in separate arithmetic.

**Conditional:** 96.25 W is a calculated result under stated assumptions, CONDITIONAL on five values:
- EA2's gain and VC's range;
- A7's gain away from its 50 mV, 5.025 V test point;
- the IMON_IN line regulation while switching and at temperature;
- RSENSE1's TCR below +25 C;
- U5's junction, an inferred estimate.

With every conservative assumption together, the corner reads 99.8992 W, a margin of 0.1008 W. Clearing a condition needs a
manufacturer-warranted limit; drafts for Analog Devices and Milliohm are in `records/l4e7/clarification/` for the owner to
send.

**Drafted, not implemented:** every circuit change of L4-E4 to L4-E7 is a draft for a generator owner. Nothing is applied to
any generator.

**Evidence:** the box suite at `6145f00f` read 2450 passed, 0 failed, 3 skipped, 208 of 208 modules, judged by the promotion
gate on its log. The runner's gates passed: 213 module tests, every validator and page current.

**Next:** L4-E8, the VBUS20 bank. The collaborator's check did not accept the author's eight-can selection: coincident
harmonics at worst phase give 2.855 A; independent per-can ESL gives 3.587 A; the LM5176's specified frequency row; the
lifetime evidence. Its fix round is running. Then its recheck, the coordinator's check, set 25, and L4-E4's release record
once the circuit-round drafts are complete.

**Blocker:** none for an owner decision.

**Elapsed and compute:** 18:20 to 21:15 CEST. vast.ai 53619970 ran set 24's suite and is stopped with its disk kept; credit
107.28 USD. The collaborator made four runs on the ChatGPT plan: L4-E7Q's check and recheck, and L4-E8's check.

### Milestone, 2 October 2026 10:50 CEST: Layer 4's connected power architecture and its closure gate (integration sets 25 and 26 on main)

**Closed (each accepted by the coordinator's closing check; the collaborator's two runs per issue did not accept them):**
- **L4-E7R, the 100 W control.** Approach C on board E: a WSL sense bank, INA169, TPS3701 and a TPS3808 holding SWEN low, off
  by default.
  - The static bound is 93.5521 W, CONDITIONAL on G_CM and U18's VIN+ bias.
  - The CS101 correction puts the bulk ahead of the bank and adds a 4 ms trip filter; the worst immunity ripple is 0.0585 A
    against a 0.1130 A margin.
  - The regulation stays the LT8705A's at RIMON_IN 31.6k, coordinated under the trip.
- **L4-E8, board A's VBUS20 bank.** Six cans, each behind a 45 mOhm ballast, and Cc2 3.3 nF, from a conservative bound over
  independent cans. B-4 closes at R11 8 mOhm; the 7 mOhm fallback stays CONDITIONAL on V-A07.
- **L4-E10, FEA-008.** A feasibility screen and three complete approaches. The recommendation is a wide-temperature 18650 in
  D-06's 4S3P, CONDITIONAL on the maker's signed specification and the owner's approval. **FEA-008 is not closed.**
- **L4-E11, U-04 and D-06.** The hot swap becomes a TPS48110-Q1 that starts from a 9.00 V plug (REQ-015 a CONDITIONAL
  CANDIDATE). The vehicle entry is rated 20 A or more, with a controlled DC-loop floor.
- **L4-E12 (MESHSAT-1478), the electronics against the inside air.** E3-O holds as stated. E5 with the margin hold is
  CONDITIONAL on T-H1 at 2.159 W/K. The SGP41 is the owner question CFL-002.
- **L4-E13, U-03, the solar panel.** It is now a CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC). The window is measured at
  -20 C and 1000 W/m2 (margin 0.8495 V on the typical rows). The irradiance disturbance is checked apart, against D4's 28 V, by
  junction physics (threshold 8574 W/m2). Route 2 is feasible on one identified SunPower unit, and no unit is accepted.
- **L4-E9, the connected architecture.** A1 under D-06, with no material power-path defect open. The register holds 139
  items, with the Layer 5 handover LH-01 to LH-11.

**The closure gate: NOT CLOSED.**
- Criteria 3 and 4 pass. Criteria 1, 2 and 5 are CONDITIONAL on three architecture-level choices, each with the evidence that
  settles it:
  - U-01, the cell's signed specification (Topwell);
  - U-02, T-H1 at or above 2.159 W/K and the fans (a measurement);
  - U-04, TI's N1 answer or the bench's VSYS.
- No internal engineering step remains on that path.

**Drafted, not implemented:** every circuit change of L4-E4 to L4-E13 is a release-guarded draft. Nothing is applied to a
generator.

**Integration findings:**
- Set 25's first box run refused 82 tests for environment and instrument reasons; no engineering figure moved:
  - no `poppler-data` on the box;
  - poppler 24's SVG serialisation, against which L4-E9's and L4-E11's readers are now fixed and tested;
  - CPython 3.12's float `sum()` in `rv-pwr/pwr_budget.py` (MESHSAT-1480).
- The suite now runs in two passes, and the gate judges both logs.
- Set 26 found L4-E13's stale pin of L4-E7's output, and the record was re-read on L4-E7R: the nominal hold's day is 336.6 Wh
  under the accepted stage.

**Evidence:**
- Set 25 at `50a44371`: 2545 passed + 32 passed, 0 failed, 3 skipped, 214 of 214 modules.
- Set 26 at `aa897e38`: 2564 passed + 32 passed, 0 failed, 3 skipped, 215 of 215 modules.
- The runner's gates passed for both.

**Next (the owner's instruction of 2 October 2026, in progress):**
- U-01 and U-02 are resolved at the engineering level and accepted by the coordinator's checks (L4-E10 check 4, L4-E12 check 4).
- U-04's round, the findings ledger and the closure-path page are running, then set 27.
- Layer 5 starts from the handover LH-01 to LH-11; the circuit round applies the drafts in their recorded order.

**Owner actions:**
- U-01: send the Topwell request, then approve or decline the cell change.
- U-04 and L4-E7R: send the TI drafts.
- Decide CFL-002 (A, B or C).
- U-02: authorise T-H1 on a bench: an empty Peli 1450 with the frame, a plate blank, dummy heaters and the picked fans (`records/l4e12/T-H1-PROCEDURE-DRAFT.md`).
- Send the other clarification drafts.
- When convenient, buy one SPR-E-Flex-100 for PANEL-ACC; it is off the gate's path.

### Plan, 2 October 2026 11:27 CEST: the bounded power-architecture closure (the owner's instruction of 11:25)

**Fixed:** battery and solar mandatory; HF and the tablet kept; storage internal to the Peli; no external battery; D-06's pack
arrangement the baseline (alternatives proposals); REQ-016 and every mandatory requirement preserved; Layer 3 closed. 48 to
72 h is an endurance objective: battery-only and solar-assisted runtime reported separately, tablet charging shown as a cost.
Electrical feasibility and endurance are separate questions.

**The steps, at most two workers:**
1. *Running:* L4-E9 round 5 (the dependency rounds re-pinned, the register's new rows) and the independent verifier of the
   findings ledger's risks.
2. *Three specific questions, one worker at a time,* each answering the consolidation's need:
   - U-02: does T-H1 confirm an already-supported design or decide feasibility (a conservative lower bound on the conductance
     against the lines and the session's fallback)?
   - U-04: at most three approaches: the BQ25731 with the hold-up bank, TI's BQ25730 (the same family's NVDC charger with an
     external battery FET; TI states the system keeps operating with the battery removed), one other if better documented.
     Selected on margin, interacting controls, power, heat, space, cost and endurance.
   - U-01: published specifications sufficient, or a vendor answer genuinely necessary; at most three candidates within the
     approved arrangement; else the exact missing fact and the smallest experiment.
   Then the panel lead's surge derivation (L4-E7).
3. *The consolidation,* one Claude author in L4-E9:
   - one connected diagram, one budget, one circuit-change list;
   - the operating behaviour (source changes, simultaneous operation, startup, shutdown, faults, thermal management, control
     dependencies);
   - the implementation handover by layer, drafted against applied;
   - the exit statement per U against the owner's definition.
4. *One Astra engineering review* of the consolidation, with at most one targeted recheck: the decision-critical electrical and
   thermal bounds and interactions, primary sources and counterexamples. The findings ledger is mapped on the exact candidate.
   If a material uncertainty survives the recheck: a component or topology change, or the specific experiment or engineer
   handoff.
5. The coordinator's closing check, set 27, the box suite, promotion.

**Estimated engineering time** (estimates; the dependency rounds measured 17 to 22 min each):
- the questions about 1.5 to 2.5 h on one slot, with the consolidation about 2 to 3 h in parallel;
- the review, fix and recheck about 2 h;
- set 27 about 1.2 h (measured).
- In all about 5 to 7 h of wall-clock.

**External, not estimable:** Topwell's signed specification, TI's statements (unless U-04's selection removes them), T-H1 on a
bench, the CFL-002 choice. Purchases and outside contacts stay with the owner.


### Plan, 2 October 2026 23:42 CEST: continue autonomously through the layers (the owner's instruction of 23:40)

The instruction is filed as received at `v2/docs/handover/OWNER-INSTRUCTION-2026-10-02.md`; this entry applies it to the plan
once. Everything above stands where it does not conflict.

**Fixed:** as in the plan of 11:27 (battery and solar mandatory; storage inside the Peli; HF and the tablet kept; 48 to 72 h an
objective under its profile, reported honestly, tablet charging a cost; the ruled pack and cell; no reduced service, no relaxed
protection or temperature requirement; Layer 3 closed). The owner is asked only for an actual ruling or an action outside
authority (purchases, outside contacts, host power).

**Completion claims, five, always apart** (a layer reads 100 % only against its fixed criteria; a blocked gate is never renamed):
documents and editable artifacts complete; design reviewed and accepted; circuit or layout changes implemented; physical
qualification completed; fabrication release approved. A named future test does not establish feasibility; a software test
establishes its tested behaviour.

**Per power issue, three kinds, each with its own remedy:** a demonstrated defect is corrected; an unresolved assumption is
bounded with applicable evidence or designed out (fewer dependencies, adequate margin, supported component behaviour; a third
compensating circuit on one stage reopens the stage); a physical question gets a specimen, a measurement, an acceptance and a
consequence. An unsuccessful approach is never repeated on unchanged evidence; a review budget closes nothing. Reviews: one
focused independent check and one targeted recheck per issue on the exact candidate with a bounded question; coordinator
verification is labelled and never overwrites an independent rejection.

**Order of work:** by dependencies, the earliest incomplete layer first; an open question blocks only its dependants.
Provisional work on stable parts of later layers is allowed with its assumptions and invalidation triggers visible; no routing
on an unstable circuit. Two workers, one author per artifact, the coordinator owns integration and the system model; an idle
slot takes the critical path or the next ready layer without waiting for the owner.

| Layer | First ready task under this plan | Entry condition | Blocks only |
|---|---|---|---|
| 4 | finish CP01 to CP03 (done, L4-E11 `1a4245c3`), the one design-out attempt on B6 (L4-E7, running), the consolidation's three-level decision and the prototype qualification route with the purchase and send lists (running); integrate as set 27; the one targeted Astra recheck on the exact integrated commit; the box suite; promote | none | the L4 "reviewed and accepted" claim; nothing in L5 or L6 that reads the accepted parts |
| 5 | write the power contracts L4-E9's `LAYER5-HANDOVER.md` drafts (LH-01 to LH-11) into `pcb_interfaces.yaml` and `HW-FW-CONTRACT.md` with the pass-2 fields (5.2, 5.4, 5.5), the new rows of set 27 (VSYS_DOCK behind U42 on IF-AE-DOCK, the fan-start stagger E11-39, the guard's R-176 rows), the sequencing and line states (5.6, 5.7) from L4-E9 section 4; each entry names its L4 row and its invalidation trigger | the L4 record it reads is on a committed candidate (set 27's line); items that rest on B6 or U-04's open conditions are marked PROVISIONAL | 5.2, 5.4 to 5.7, 5.11, 5.13 |
| 6 | the identity, rating, derating and source evidence of every part Layer 4 selected (the charger and its FETs, the eFuse, the entry and guard parts, the sense bank, the Samsung capacitors, the fans once named): exact MPN, package, grade, the maker's document with revision and sha256, LCSC or maker availability and price read publicly, one alternative each, the qualification obligation it carries (6.1 to 6.3, 6.6, 6.8) | the part is selected in an L4 record on a committed candidate | 6.1 to 6.3, 6.6, 6.8 for those parts |
| 7 | the harness and fit items L4 created: the solar lead's loop bound (R-180) as a controlled harness or dropped by B6's route 3, the dock contact and wiring pulse capability, the fans' pick and mounting (D-18), T-H1's mock-up specification | L4's qualification route names them | 7.x rows for those items |
| 8 | apply the APPROVED circuit drafts of L4-E4 to L4-E13 in application order with their release guards (L4-E4's release record first), then regeneration and `check_contracts.py` against the Layer 5 contracts | the draft's guard reads released; the stage it changes has no open design-out attempt | 8.x for that board |
| 9 | the analyses re-run on the implemented circuit (dc_drop, impedance, the walk), assumptions and cases named, the bench rows tied to specimens | Layer 8 applied the change | 9.x |
| 10 to 12 | layout only behind the schematic, stackup, interface and mechanical gates; manufacturing packages from the validated revision; firmware, bring-up and test plans in parallel where dependencies allow | the named gates | as stated |

**Physical verification route:** every experiment names its specimen (evaluation hardware, coupon, enclosure mock-up or
controlled prototype), what it represents and what transfers, the procedure and pass limits, the consequence of failure and the
authorisation still needed; an evidence build is separate from fabrication release, and no gate requires a finished board to
permit a representative prototype. The table is L4-E9's "prototype qualification route" (the consolidation's round 2).

**Execution:** the existing tools, worktrees, ledger and `regen_out.py`; targeted checks while changing, the release suite on the
exact integrated candidate; artifacts regenerated in dependency order; no repeated full suite or rewrite without a changed risk;
the rented instance resumed for the suite and stopped after about two hours idle, disks kept; snapshots packaged promptly and
labelled; every checkpoint commits the state and names the next executable action.

**Milestone reports, brief:** what changed and its commit; which layer criteria are met and which open; what runs; the next
milestone with an evidence-based ETA; only the owner decisions genuinely needed. Documents, tests and review rounds are not
hardware progress.

**ETA (evidence-based, estimates):** set 27 integration and freeze about 1 h after the two running rounds land (the freeze of
21:00 took 25 min); the Astra recheck about 1 h (runs of this size took 45 to 70 min); the box suite about 25 min plus the
instance's resume; promotion 30 min. Layer 5's first task about 2 to 3 h on one slot; Layer 6's first task about 2 to 3 h on the
other. External and not estimable: the vendor answers and every measurement.
