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
- Worktrees: `/home/claude-runner/worktrees/meshsat-fieldkit/<name>`, one per branch above (outside `/tmp`). Worker
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
