# MeshSat field kit V2 handover: glossary

MESHSAT-1357, added in handover H1.1 (27 September 2026) because the usability check of H1 found these names used
without definition, and extended after H2 (the same day) with the overloaded families, the evidence classes and their
causes, the power states and the design items the H2 usability check found unglossed (`H2-RESPONSE.md`). One line per
term; the page named after a term is where it is defined in full. Prototype framing: nothing named here has been built
or measured.

## Process and people

| Term | Meaning |
|---|---|
| owner | the project owner, who alone decides money, outside contact, publication and promotion (START-HERE section 4, "Who decided what") |
| session | the design session (AI agent sessions working for the owner); a SESSION decision names its reason and how to reverse it |
| integrator | the single writer who merges and commits; one writer per shared file (standing condition 4 of `v2/docs/EXECUTION-PLAN.md`) |
| closer, hc1 to hc9 | the *handover closers* of 27 September 2026: one agent per pre-PCB layer, named hc plus the layer number (hc1 layer 1, ..., hc9 layer 9), each asked to close its layer's open items and hand its work to a fresh checker |
| fresh checker | an agent or person who did not write what it checks; an AI checker's result is labelled AI review |
| AI review | a review by such an agent; never electrical sign-off (`v2/docs/reviews/REVIEW-ROUTES.md`) |
| PASS, FAIL, PASS_WITH_FIXES | a review's verdict: no blocking finding; at least one blocking finding; acceptable once the listed blocking fixes are made (the work is not accepted until they are) |
| blocking, minor | a finding that stops acceptance of the reviewed work, and one that does not |
| candidate | work in a branch or patch that is not merged: not design until the integrator merges it with its evidence (`candidates/README.md`) |
| worktree, `fnd/<name>` | a git worktree of the session and its branch, never pushed by the session. At H2 no candidate is left in one: the H1.1 patches under `v2/docs/handover/candidates/` are superseded, each merged from a later state (`candidates/README.md` names the commit), and H2 references them rather than bundling them. H2's own commits on `fnd/h2` after `62f26a44` are not on the public repository (the `public` column of `SOURCE.txt`'s timeline); REGENERATE.md section 9 gives the routes that work without them |
| round 4, 5, 6, 7, 8 | the numbered rounds of circuit and tool corrections of 25 to 27 September 2026, in order; round 8 is the latest, merged for all six boards with a schematic (board B at `b76c18cb`, after H1.1) |
| set 1 to set 5, wave 3 | the integration batches of 26 and 27 September 2026: sets 1 and 2 round 8 on A, C, D, E and P (H1); set 3 board B's round 8; set 4 the layer 2, 3, 5 and 7 closers, the re-take driver and the case release (`f2b7fa66`); set 5, called wave 3, the streams w3a, w3b, w3de, w3t and w3g on boards A, B, D and E, the RF-002 tool row and the diagrams (`a7b5872e`) |
| consolidated re-take | one run of `retake_schematic_phase.py` that re-took every schematic-phase reading on the committed netlists (`8ea7867e`, 27 September 2026; REGENERATE.md section 9) |
| release check, targeted fix, narrow verification | a fresh reviewer's judgement of a layer against the owner's COMPLETE test; after two attempts on the same cause, one fix limited to named items and a check limited to those items by a session that wrote none of them (the owner's execution prompt, section 4) |
| c23, c5, c7 | the targeted fixers that answered the closers' second-review findings on layers 2 and 3, 5, and 7 before their merge |
| H1, H1.1, H2 | the handover snapshots of 27 September 2026 under `v2/release/handover/`, in order; each is an immutable copy of one commit (`SOURCE.txt`) |
| streams r8a, r8b, r8c, r8d, r8e, r8p | round 8's author per board (letter = board) |
| r8bat, r8cert, ts-net, ts-rec, ts-tvs | the battery stream; the certification tool stream; the tools streams (ts-net: PWR-001 and SI-001 on the netlist; ts-rec: recording readings by sha; ts-tvs: clamp symbols) |
| W1 to W7 | the foundation workstreams of 25 September 2026 (W1 systems and requirements, W2 power and electronics, W3 interfaces and board B, W4 mechanical, thermal and RF, W5 firmware and testability, W6 independent verification and manufacturing, W7 regeneration and evidence integrity; `v2/docs/EXECUTION-PLAN.md`, the workstream table) |
| rv-bat, rv-dec, rv-emc, rv-fab, rv-pkt, rv-pwr, rv-zer, rv-ev | the review streams of 26 September 2026, named for their subject (BAT battery and protection, DEC decoupling placement, EMC the per-transmitter EMCON table, PKT the packet's cited vendor files, PWR power and thermal, ZER ZEROIZE; FAB and EV as their records say); their records are under `v2/docs/records/` |
| adjudications A01 to A11 | the eleven adjudications of 25 September 2026 (`v2/docs/records/adj/`) |
| box, box-hours | a rented build host with KiCad 9.0.9 (the session used vast.ai CPU hosts); a box-hour is one hour of such a host, the unit the routing experiments are capped in |
| appendix 32.nn | a numbered entry of `v2/docs/MESHSAT-709-geometry-appendix.md`, the dated design record (history: trace a ruling there, never take it as current state) |
| MESHSAT-nnn | an issue of the project's tracker, which is outside this repository |

## Identifiers

| Pattern | Meaning and where defined |
|---|---|
| NEED-nn | a need of `v2/docs/CONOPS.md` (NEED-01 to NEED-19), mirrored in `pcb_requirements.yaml` `needs` |
| REQ, CON, ASM, CHO, SPD, CFL, FEA-nnn | requirement, constraint, assumption, choice, specification detail, conflict and feasibility records of `pcb_requirements.yaml` (view: `v2/docs/REQUIREMENTS-TRACE.md`) |
| D-nn (D-01 to D-18, D-02a to D-02e) | an owner ruling of 25 and 26 September 2026 (`pcb_requirements.yaml` `owner_rulings`, `CONOPS.md` section 7) |
| SC-nn | a session choice under the owner's standing rule (`pcb_requirements.yaml` `session_choices`); SC-L2-nn, SC-HF-nn are a closer's own drafts of such choices, and a draft a page still cites is entered in the registry under its own SC-nn with the draft's name as `drafted_as` (SC-HF-01 to SC-HF-06 are SC-58 to SC-63 since 27 September 2026); `rules_lib.py requirements` refuses an SC- id cited in the registry or a page of `v2/docs/` or `v2/docs/handover/` that no entry defines |
| S-nn, L-nn, M-nn | open items of the registry (`open_items`; an M-nn is an owner action, such as M-02); closed ones move to `closed_items` |
| decision nn | an entry of `v2/ecad/tools/pcb_decisions.yaml` (page: `v2/docs/OWNER-DECISIONS-OPEN.md`) |
| EQ-nn | a blocked engineering question of `ENGINEERING-QUESTIONS.md` (EQ-01 to EQ-30 in H2) |
| rule ids (PWR-001, SI-001, RF-002, TRN-001, SCH-002, STK-001, ...) | a rule of `v2/ecad/tools/pcb_rules.yaml`; its status per board is `v2/docs/PCB-RULE-STATUS-<x>.md` |
| INT-001, INT-002 | the interface rule of the registry, and the pre-layout assessment of board B's 48 critical nets (`v2/docs/reviews/INT-002-PRE-LAYOUT-ASSESSMENT.md`) |
| R-BAT, R-PWR, R-HSD, R-SEC, R-EMC | the qualified human reviews the records require (battery, power, high-speed digital, security, EMC; `v2/docs/reviews/REVIEW-ROUTES.md`); none engaged |
| Reviews A, B, C, D | the stage reviews of the foundation plan: A layers 1 and 2, B requirements, C architecture and interfaces, D parts and circuits (`EXECUTION-PLAN.md`) |
| Q-B-ESC-1, Q-B-ESC-2 | board B's bounded escape-routing trials: the first ran on 26 September 2026 (INCONCLUSIVE), the second is specified (`v2/docs/B-FEASIBILITY.md` sections 7.8 and 7.9) |
| Z-EXP-A, Z-EXP-B; E-01 to E-12; T1 to T11 | the ZEROIZE bench experiments (`feasibility/ZEROIZE.md`); the EMCON bench rows (`feasibility/EMCON.md`); the case mock-up checks (`CASE-MARGINS.md` section 5) |
| PS-IDLE, PS-IDLE-SPEC, PS-TYP, PS-RED2, PS-RED-b, PS-SURV, PS-SURV-R, PS-HOLD, PS-OFF, PS-ALLTX | the power states the power model computes (`feasibility/POWER-THERMAL.md` sections 4 to 6; `ARCHITECTURE.md` section 8.1; `v2/docs/records/rv-pwr/pwr_budget.py`): PS-IDLE-SPEC three modules idle with the monitor on (the first runtime mode of SC-05) and PS-TYP three typical modules with the monitor on (the second); PS-RED2 the closed-lid reduced mode (`CONOPS.md` section 4c, slots 2 and 3) and PS-RED-b its three-idle variant; PS-SURV and PS-SURV-R the heat stage's one module (as generated, and after BANK-R1); PS-HOLD the hot stop's first step (not computed) and PS-OFF its second; PS-ALLTX every transmitter at once. `POWER-THERMAL.md`'s own PS-RED is its one-module case, not the reduced mode (`ARCHITECTURE.md` section 8.1 says so) |
| HOT-R1 | the hot stop's signal path independent of the compute modules: the sensor controller on board E (which reads the pack's cell temperatures) drives the dock's spare contact (IF-AE-DOCK pin 12) into an input of board A's expander U27, whose interrupt reaches the panel controller on board C (`CONOPS.md` section 4c). A design item of boards A and E, in neither generator at H2 (S-57, EQ-22), so REQ-077 reads FAIL on the generated boards |
| BANK-R1 | board B's bank reallocation that lets one compute module carry the owner's D-02b set with the SOS path in the heat stage (slot 3 alone with banks 3 and 2 and the LoRa module); a board B design item, not in its generator at H2 (S-54; `CONOPS.md` sections 4 and 4c) |
| SD-EMC-1, SD-EMC-2, SD-EMC-6 | EMCON's supply-disconnect items (`feasibility/EMCON.md` section 5): SD-EMC-1 the 5G module's firmware-independent inhibit by removing its supply (SC-11; drawn on board B in round 8 as SD-EMC-1r8, `b76c18cb`), SD-EMC-2 back-feed through lines that stay live, SD-EMC-6 the hardware EMCON lamp's light guide in the face plate |
| IF-XX-NAME (IF-BC-PANEL, IF-AE-DOCK, IF-PE-PACK, ...) | a board-to-board or board-to-device contract of `v2/ecad/tools/pcb_interfaces.yaml` `board_to_board` (30 at H2): `IF-` then the two boards' letters in the order the pin map is written (B to C for IF-BC-PANEL), or one letter and the device for a contract with a device (IF-A-PA, IF-D-FLANGE, IF-B-RB9704), or `EXT` for a wall port (IF-EXT-USB, IF-EXT-DC, IF-EXT-ETH), then the cable or function. Each names both ends, the pin map, the idle state of every control line, the power carried, whether it may be mated live and which tool judges which part (`ARCHITECTURE.md` section 12; `HW-FW-CONTRACT.md` for the firmware side) |
| FW-A01 to FW-A16, FW-B01 to FW-B19, FW-C01 to FW-C14, FW-D01 to FW-D03, FW-E01 to FW-E10, FW-P01 to FW-P03, FW-K01 to FW-K05; V-nn; HF-Fnn | the firmware obligations that affect hardware, of `v2/docs/HW-FW-CONTRACT.md` section 3 (the letter is the board or controller: A, B, C the panel controller, D, E the sensor controller, P the pack, K the kit I2C bus); V-nn its verification items (section 5); HF-Fnn its findings |

**Finding ids.** A finding is named `<source>-<letter><number>`: the source is the stream, review or page that found it
and the letter its kind (F finding, N note or open item, E error, D decision, B blocking). Examples used in the pages:
PWR-F12 (the power review's finding 12, `feasibility/POWER-THERMAL.md`); BAT-F20 (the battery review, `review-packets/battery/`);
R4A-N13 and R4A-N12 (board A's round 4 author, open items; `records/r4a/`); R8E-N01 (board E's round 8 author);
W4-F17 (workstream W4); I3-F01 (a round 3 interface finding, supervisor addresses); HC9-E1 (the layer 9 closer's error
finding, board E's current sense); A04-D2 (adjudication A04, its second item); FB-FAB-1 to FB-FAB-5 (the failover
fabric's findings, `feasibility/FAILOVER-FABRIC.md`); SD-EMC-1 and SD-EMC-2 (the EMCON study's supply-disconnect items,
`feasibility/EMCON.md`); P2-B1 (a review's pass 2, blocking item 1); HF-Fnn (the hardware and firmware contract).

**Decoupling G1 to G14 and T1 to T10.** In `v2/docs/feasibility/DECOUPLING.md`: G1 to G14 are the numbered gaps
between each board's fitted decoupling and what its makers ask for (one row per gap, the boards affected and the fix),
and T1 to T10 the numbered checks of the decoupling test that judges them (T10 is the "own via" check). Elsewhere T1
to T11 are the case mock-up checks and T1, T3, T4 the charger's temperature thresholds (`TEST-PLAN.md`); the page
says which.

## The same letters in different families (read each by the page that uses it)

| Name | Family 1 | Family 2 (and more) |
|---|---|---|
| C1 to C6, C1 to C4 | **case choices** C1 to C6 of `CASE-MARGINS.md` section 4, taken as SC-07: C1 the face plate on the 1450PF frame over Peli's o-ring, C2 the twelve arrestor bulkheads at Z 59, C3 the connector plate, C4 one RF entry plate per end wall, C5 the QMX tray moved 1.5 mm west, C6 the four setting legs | **power and thermal controls** C1 to C4 of `feasibility/POWER-THERMAL.md` section 9.3 (firmware, PROVISIONAL): C1 module shedding to the reduced mode on inside air +50 C or any cell +55 C, C2 the outlet budget, C3 a current trigger for C1, C4 the in-key guard (with K1 to K5, the key-down rules of its section 7.2). "C1 defined one way" (`7dfbfb16`, the second release attempt) is the thermal control C1; "C1 to C6" and "case choice C2" are always the case |
| M1 to M5, M1 to M18, M-02 | **missions** M1 to M5 of `CONOPS.md` section 3 (M1 the 72-hour remote relay on pack and solar, M2 the vehicle move, M3 two kits linked, M4 the emission-controlled posture, M5 degraded operation); "M1's energy balance" is REQ-072 | **case margins** M1 to M18 of `CASE-MARGINS.md` section 3.2, some with a letter (M1 the monitor body over the heatsinks, M4a the pack block's east corner, M5 the pack group in Y, M13 the bulkhead clamp, M17g and M17x the east jumpers under their plugs), the rows FEA-007 names; and **M-02**, with a hyphen and two digits, an owner action of the registry (`open_items`, class OWNER_ACTION: accepting or not M1's failing energy balance, EQ-13) |
| E1 to E8, E3-H, E3-L, E4-S | **environmental test rows** of `TEST-PLAN.md` section 2 (MIL-STD-810 methods: E1 the 26-drop transit shock, E2 vibration, E3 high temperature with E3-S storage, E3-A operation, E3-L lid closed and E3-H the stepped run beyond the envelope, E4 low temperature, E5 humidity, E6 immersion, E7 rain, E8 sand and dust); "SC-03 E5 humidity cycle" is this E5 | **boards**: board E is E1, the dock strip (project `pcb-e1-dock-e7`, declared phase E17), and E5 is the dock block (project `pcb-e5-block`); "board E5", "E5's INT-001" and FEA-007's "boards D and E5" are the board. **E-01 to E-12** (hyphen, two digits) are EMCON's bench rows (`feasibility/EMCON.md` section 6) |
| T1 to T11, T1 to T10, T1, T3, T4 | the case mock-up checks (`CASE-MARGINS.md` sections 5 and 7; FEA-007's YES rows) | the decoupling test's checks (`feasibility/DECOUPLING.md` section 8) and the charger's temperature thresholds (`TEST-PLAN.md`); the section "Decoupling G1 to G14 and T1 to T10" above |
| A01 to A11, A32, A65 | the adjudications of 25 September 2026 (`records/adj/`) | board A's declared phase (A32) and its schematic's title-block label (A65) |

## Evidence classes and their causes (`v2/docs/CURRENT-EVIDENCE.md`, generated by `v2/ecad/tools/rules_status.py`)

Every rule-board reading is put in one **class**, and a class that does not count names its **cause** in brackets:
"SI-001 INCONCLUSIVE on VALID_HISTORICAL evidence (RATIONALE)" reads: the newest SI-001 reading says INCONCLUSIVE, the
reading counts as current, and it counts through a recorded rationale. Two classes count as current evidence,
CURRENT_CANDIDATE and VALID_HISTORICAL, so a page calling SI-001 "a current reading" and CURRENT-EVIDENCE calling it
VALID_HISTORICAL agree: the result is current, it rests on a rationale for a tool change that does not touch it.

| Class | Meaning |
|---|---|
| CURRENT_CANDIDATE | taken on the board's current candidate by content (its netlist and board file by sha; for a release-package rule the declared phase's folder with its BOM), under the current rule digest and the byte-identical tool code, with every configuration input its writer reads unchanged since. Counts as current |
| VALID_HISTORICAL | an older artefact, tool or configuration, reused only through a recorded compatibility rationale that pins both versions (`v2/docs/evidence/COMPATIBILITY.md`). Counts as current |
| AWAITING_REVALIDATION | any other reading; it does not count, whatever its result says |
| DESK_REVIEW | a document check bound like any reading (a manually verified record, or a PROTOTYPE-phase rule's reading, which can only be a desk check while nothing is built); never a physical test |
| PHYSICAL_TEST | a measurement on built hardware bound to the candidate; none exists |
| NO_EVIDENCE | no reading at all (no verdict, no implementation, a waiver), and the rows that do not apply |

| Cause | Meaning |
|---|---|
| BOUND | the reading is tied to the current candidate and its configuration (the cause of a CURRENT_CANDIDATE row) |
| RATIONALE | reused under a recorded compatibility entry (the cause of a VALID_HISTORICAL row) |
| UNBOUND | the reading records no artefact by content, so it cannot be tied to the candidate (E5's INT-001: the set verdict it is read from records no file of E5) |
| TOOL_CHANGED, TOOL_UNKNOWN | the code that wrote it (its entry script or a local module it imports) changed since, or cannot be identified |
| NOT_CURRENT_EVIDENCE | the reading itself is stale: an older rule digest or rule set, another board, or a tool meaning change |
| NETLIST_MISMATCH, BOARD_MISMATCH, LAYOUT_NOT_CURRENT, PREDATES_ARTEFACT | taken on another netlist or board file than the candidate's, on a layout that does not carry the candidate's netlist, or before the current netlist was committed |
| OTHER_DESIGN, OTHER_BOARD | a cross-board reading that also judged another board's netlist or board file which is no longer that board's candidate |
| CONFIG_CHANGED, CONFIG_UNDECLARED | a configuration input its writer reads (`rules_status.CONFIG_INPUTS`) changed since the reading, or the writer has no audited list of inputs |
| TEMP_INPUT | it judged files in a temporary directory (`/tmp`), not this tree: a fixture's world or another checkout. Why the re-take runs in a clone outside `/tmp` |
| PROTOTYPE_DESK_CHECK | a current reading of a PROTOTYPE-phase rule, classed DESK_REVIEW because nothing is built |
| NO_VERDICT | no reading on this board (a NO_EVIDENCE row) |

## Boards, phases and labels

| Term | Meaning |
|---|---|
| declared phase (A32, B21, C24, D12, E17, E5, P4) | the `phase` field of `v2/ecad/tools/boards/<x>.json`, the name every current page uses for a board |
| project directory suffix (`-a23`, `-b19`, `-c8`, `-d9`, `-e7`, `-p2`) | historical: the directory's name from an earlier phase; the declared phase is what counts |
| title-block label (A65, B21, C24, D37P, E42P, P4) | the text after "Phase" in a schematic's title block: the value of the environment variable `PHASE` of the run that generated the committed schematic (`gen_sch_<x>.py` writes it into title-block comment 1; `full.sh` sets it from the board table, `gate_sweep.sh` from its label argument). It is a run label and carries no design meaning. A65 is board A's run label, D37P and E42P board D's and E's; the `P` suffix is not documented in the tree (INFERRED: a label variant of the run that wrote them) |
| B12 to B15 | the single-module board B generation (history); "board B" means the three-module board, B16 onward |
| IOHA | I/O high availability: board B's voted hub-bank failover fabric (`v2/docs/ARCH-PCB-B-IOHA.md`) |
| HAL | the hardware abstraction layer of the MeshSat software, which shares every radio and sensor over the network (software, outside this repository) |
| EMCON, ZEROIZE, SOS | the hardware transmit-silence line, the secure-element erase line, and the distress function (`v2/docs/PANEL.md`, `feasibility/EMCON.md`, `feasibility/ZEROIZE.md`) |
| PARITY, PARITY_AFTER_NOISE, DIFFERENT | regeneration results of `regen_compare.py`: identical; identical after the known noise (dates, generated ids); a real difference (REGENERATE.md) |
| VERIFIED, RECORDED, INFERRED, TBD, PROVISIONAL | the evidence labels (START-HERE section 4) |
| NOT_YET_TESTED | a fitted function outside prototype 1's accepted core, reported as untested, never as a pass (D-01) |
| layout entry | the stage gate a board must pass before layout starts (`CONTINUATION-BRIEF.md` section 5.1) |
| layout-entry reason | one line of `CURRENT-EVIDENCE.md`'s section "Layout entry, per board": a required schematic-phase rule not a PASS on evidence that counts, a hold's unmet layout-entry requirement, or a feasibility blocker's open layout-entry stage (40 at H2) |
