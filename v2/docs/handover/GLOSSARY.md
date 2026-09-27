# MeshSat field kit V2 handover: glossary

MESHSAT-1357, added in handover H1.1 (27 September 2026) because the usability check of H1 found these names used
without definition. One line per term; the page named after a term is where it is defined in full. Prototype framing:
nothing named here has been built or measured.

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
| worktree, `fnd/<name>` | a git worktree of the session and its branch; never pushed, so the handover carries them as patches under `v2/docs/handover/candidates/` |
| round 4, 5, 6, 7, 8 | the numbered rounds of circuit and tool corrections of 25 to 27 September 2026, in order; round 8 is the latest, merged for boards A, C, D, E and P, a candidate for board B |
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
| SC-nn | a session choice under the owner's standing rule (`pcb_requirements.yaml` `session_choices`); SC-L2-nn, SC-HF-nn are a closer's own drafts of such choices |
| S-nn, L-nn | open items of the registry (`open_items`); closed ones move to `closed_items` |
| decision nn | an entry of `v2/ecad/tools/pcb_decisions.yaml` (page: `v2/docs/OWNER-DECISIONS-OPEN.md`) |
| EQ-nn | a blocked engineering question of `ENGINEERING-QUESTIONS.md` (EQ-01 to EQ-21) |
| rule ids (PWR-001, SI-001, RF-002, TRN-001, SCH-002, STK-001, ...) | a rule of `v2/ecad/tools/pcb_rules.yaml`; its status per board is `v2/docs/PCB-RULE-STATUS-<x>.md` |
| INT-001, INT-002 | the interface rule of the registry, and the pre-layout assessment of board B's 48 critical nets (`v2/docs/reviews/INT-002-PRE-LAYOUT-ASSESSMENT.md`) |
| R-BAT, R-PWR, R-HSD, R-SEC, R-EMC | the qualified human reviews the records require (battery, power, high-speed digital, security, EMC; `v2/docs/reviews/REVIEW-ROUTES.md`); none engaged |
| Reviews A, B, C, D | the stage reviews of the foundation plan: A layers 1 and 2, B requirements, C architecture and interfaces, D parts and circuits (`EXECUTION-PLAN.md`) |
| Q-B-ESC-1, Q-B-ESC-2 | board B's bounded escape-routing trials: the first ran on 26 September 2026 (INCONCLUSIVE), the second is specified (`v2/docs/B-FEASIBILITY.md` sections 7.8 and 7.9) |
| Z-EXP-A, Z-EXP-B; E-01 to E-12; T1 to T11 | the ZEROIZE bench experiments (`feasibility/ZEROIZE.md`); the EMCON bench rows (`feasibility/EMCON.md`); the case mock-up checks (`CASE-MARGINS.md` section 5) |

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
