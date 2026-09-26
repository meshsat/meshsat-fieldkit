# V2 execution plan (MESHSAT-1357, foundation baseline)

Started 25 September 2026. This is the short, hand-kept execution record for rebuilding the V2 field kit from its engineering foundations. The foundations are the product definition, the requirements with their verification method, the architecture and budgets, the interface contracts, and the review of parts and circuits. After those comes per-board design readiness for a specified prototype build.

It is a prototype design programme. **Nothing here has been built, and no board has been ordered.** Progress is reported as reviewed milestones and verification coverage, never as a single percentage of the whole. Rule-level readiness stays in the generated pages (`PCB-RULE-STATUS-*.md`, `PCB-OPEN-PAIRS.md`, `OWNER-DECISIONS-OPEN.md`).

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

## Compute and spend

| Date | Resource | Purpose | Rate | Cap | State |
|---|---|---|---|---|---|
| 25 Sep 22:25 | vast.ai 52646493 (64 vCPU, 251 GB) | the full suite with KiCad, regeneration parity, adjudication readings, every circuit regeneration, the review packets; later the board B escape trial | 0.121 to 0.142 USD/h | about 10 USD for the foundation rounds | running; 19.9 host-hours and 2.88 USD spent at 26 Sep 18:24; credit 125.11 USD |

Credit at the start: 127.99 USD. A box is destroyed when its last result is fetched and verified.

## Log

- 25 Sep 22:33: baseline recorded; workstreams W1 to W7 running; KiCad box setting up.
- 25 Sep 22:40 to 26 Sep 00:20: round 1 (seven workstreams, seven independent challengers, one completeness critic) and round 2 (eleven adjudications from primary sources and box readings, seven fix passes, publish checks). Design defects found at the circuit and part level, among them: board B's PCIe downstream and LimeSDR SuperSpeed pairs wired transmitter to transmitter; the charger's cell-count strap selecting 2S; ten one-way clamps and rectifiers drawn reversed; the pack gauge on the wrong land; the 5G socket keyed M; EMCON not reaching the compute modules' own radios; only about 145 Wh of pack fitting the case. Regeneration parity proven for boards A, B, C, D, E and P (E5 identical in copper).
- 25 Sep 23:10 and 26 Sep 00:20: four test fixtures were found writing into this tree's own evidence and were isolated (2ba560ec, 82dd1e4d). Correction: 82dd1e4d's message says CMP-002 and SUP-001 do not read the lcsc_fill verdict; they do (the readiness takes the worst of every verdict a rule names), so the fixture output had been standing in for the real reading. It was removed from the evidence folder, and those pairs read INCONCLUSIVE until a real re-take.
- 25 Sep 23:27 to 26 Sep 00:55: the owner ruled the foundation questions D-01 to D-17 one at a time, each at the recommendation (recorded in CONOPS section 7, the requirements registry, the envelope, decisions 30 and 40, appendix 32.366), then set a standing rule: he is not asked again, and the session takes the recommended option and records it.
- 26 Sep 01:00 to 09:00: round 3 integration and its fix-up merged: d468613e (stackup rows for boards P and B, the part source record), 4ec785d8 (rulings, decisions 30 and 40, PANEL, IOHA, ASSEMBLY and envelope corrections), 68bc9e8f (product brief, concept of operations, V2-SPEC and READMEs), 6104cb81 (SCH-002 compares values and lands, certification demands the exact part and land, rules_status reads only the phase directory). Suite 1408 passed, 0 failed, 60 skipped. Open pairs rose from 118 to 128 because SCH-002 and CMP-002/SUP-001 now read INCONCLUSIVE on several boards until fresh re-takes under the corrected tools.
- 26 Sep: round 4 (Review D circuit corrections per board, each regenerated on the box and independently reviewed) and round 5 (remaining fix-ups, re-reviews, and one integration tree regenerated for every board) running.
- 26 Sep 12:32 to 18:20: rounds 4 to 6 merged the circuit corrections of boards C, D, E and P (faf8c981) and A, B and D (458b2873), each regenerated from its generator with every netlist difference traced to a finding and independently reviewed; the shared checking tools are in round 7. The case margins and the owner's D-08 reversal, D-08a, SC-02 and the transport correction landed in b69f20db.
- 26 Sep 14:12: the owner supplied a review of the 13:05 progress report and ordered it executed (v2/docs/reviews/2026-09-26-foundation-progress-review.md, 1f614233). Executed so far: evidence classes (26e847bc), ZEROIZE feasibility (9b0635d1), the failover fabric map (a5266aa8), decision 42 ruled by part class (9d566e8b), review packets for C, D, E and P plus the review routes and the vendor filing (ccf5808e), and the battery protection packet with board P's secondary over-temperature restored (d90f30e4). Running: EMCON inhibit table and power/thermal budget (last checker items), round 7 (shared tools, then every board regenerated).

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

