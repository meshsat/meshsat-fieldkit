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
| 25 Sep 22:25 | vast.ai 52646493 (32 threads, 125 GB) | regeneration parity, KiCad-dependent skipped tests, decision 31 re-takes; later the board B escape trial | 0.121 USD/h | about 10 USD for the day-1 jobs | setting up |

Credit at the start: 127.99 USD. A box is destroyed when its last result is fetched and verified.

## Log

- 25 Sep 22:33: baseline recorded; workstreams W1 to W7 running; KiCad box setting up.
