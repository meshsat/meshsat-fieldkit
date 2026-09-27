# H2 usability check (fresh checker, 27 September 2026)

**AI usability check, not an engineering or electrical review.** One fresh checker who built none of the package was given
`v2/release/handover/H2.zip` (sha256 `20072be74852ec56d818d094d150a382143d95527dd28599b22eee84c3a5cf35`, snapshot commit
`174d8466`, source commit `b89b50b4`) and the dependencies it names, and asked the owner's six questions of the handover
prompt's section 7. This file is the checker's returned result, filed verbatim by the integrating session from the
workflow journal (run `wf_ed7dada2-f27`, agent label "H2 usability checker"); nothing in it was edited except that a "|" inside a table cell is written as "/".

## Verdict

- Usable handover: **True**
- Its COMPLETE layers read as complete: **True**

This is a usability check of the H2 handover package, not an engineering or electrical review. I judged whether an outside engineer can understand, reproduce and continue the work from the package and the dependencies it names, not whether the circuits are correct.

Verdict: H2 is a usable partial handover. The four questions an incoming engineer needs answered (what, for whom, which conditions; what is settled; how the boards fit; what blocks each layer) are answered from the bundled pages with traceable citations.

The documented calculation and regeneration paths reproduce exactly:
- the energy chain, FAIL from the ZIP alone and PASS of 98 once the Mill-Max page is restored;
- the byte-identical power and case scripts;
- board P's regeneration, line for line;
- PARITY on all six boards;
- the exports and BOMs;
- the 20 suite failures, each with the stated cause;
- the 29 referenced files fetched and checked against their git blob sha.

Layers 1 and 2 read as COMPLETE for their own purpose. Their baselined documents, hashes and review chain are in the package and agree with the pages. They are AI reviews only, labelled as such. Layer 2 openly carries REQ-072's FAIL and the owner action M-02, with a stated reopen condition.

No blocking defect was found. The most material minor defects:
- The re-take route (s9) cannot be followed as written, because H2's commits are not on the public repository. The only working route, a repository built from the ZIP, needs an undocumented 'git add -f'. Once that was done, board P's re-take matched the expected results.
- s1a's code sets REF to an unpublished commit.
- The layout constraint sheets are stale against the H2 netlists (board A's VIN_RAW 12.3 A becomes 14.1 A), with no H2 page saying so.
- The pages contradict each other on which boards FEA-007 holds.
- The diagram check reads 4 of 11 current, not the documented 6 of 11.
- Several EQ and brief rows are stale, and the glossary lacks several overloaded names.

All working files are under /tmp/claude-1000/-home-claude-runner-gitlab-products-meshsat-meshsat-fieldkit/3744628d-5552-4a03-8300-e043b6cdc9c8/scratchpad/h2check/. The box directory /root/h2check was deleted.

## Answers to the six questions

### Question 1 (adequate: True)

What: the MeshSat field kit V2, an unbuilt prototype go-box. It takes messages from local off-grid networks (Meshtastic LoRa, Zigbee/Thread, WiFi) and routes them out over whichever long-range link is up (Iridium RockBLOCK 9704, 5G RM520N-GL, VHF APRS SA868 with a 30 W PA, HF QMX, kit-to-kit WiFi), using the separate MeshSat Bridge software. Physically it is a sealed Peli 1450 with a 3 mm aluminium face in the 1450PF frame, seven carrier boards and a 4S3P Samsung 35E pack of about 145 Wh (D-06). The boards: A power and I/O; B compute (three CM5 slots, voted hub-bank failover, radios, secure element); C panel backer (RP2040, EMCON and ZEROIZE lines); D VHF APRS; E1 dock strip (9 to 36 V vehicle/shore input, solar, sensor controller); E5 dock block; P pack BMS (BQ4050, BQ7720700, chemical fuse). Prototype 1 is accepted on a named core (D-01, SC-01); the other functions are fitted and reported NOT_YET_TESTED.
For whom: a non-commercial prototype run in the NL/EU by a licensed radio amateur (D-04). No CE, RED or EMC claim. No target organisation. Roles: operator, second crew member, local users, remote correspondents.
Conditions: -20 to +40 C in use and -20 to +45 C in storage. +55 C operation and +71/-33 C storage are qualification margins ('survive and recover'). Operated shaded. No cold start from cells below about -10 C. A closed-lid reduced mode (CONOPS 4c). 26 drops from 1.22 m, a wheeled-vehicle profile, and 0 to 3000 m in use (4500 m in transport). No vehicle-surge claim (D-16). The hot end is NOT established (FEA-004, EQ-05).
Files: START-HERE.md s2; v2/docs/PRODUCT-BRIEF.md ('The problem', 'Who it is for', 'What the V2 kit is', 'What it is not, today'); v2/docs/CONOPS.md s1, 2a, 7; v2/docs/OPERATING-ENVELOPE.md; CONTINUATION-BRIEF.md s2.1; README.md.

### Question 2 (adequate: True)

Settled (CONTINUATION-BRIEF s2, each with its authority):
- Owner rulings D-01 to D-17, D-02a to D-02e and D-08a.
- The Peli 1450 case, never changed; no vent anywhere; the aluminium face plus backer; case arrangement C1 to C6 (SC-07).
- The device set (appendix 32.49/32.50).
- Three identical CM5 slots with 2-of-3 voted hub-bank switching in hardware.
- EMCON as a hardware line (D-05; SC-11 for the 5G supply removal).
- ZEROIZE as a crypto-erase on the ATECC608B (D-03, decision 30, SC-08).
- The pack (D-06); SC-10's key-down thresholds; D-15/decision 40; decision 31's clamp at the entry.
- Layout rules: the P0 layer-count rule, decisions 27/28/43, In1 as solid ground, pair matching (decision 36), no uncoupled pair at release, decisions 35/39/42/46/47, and decision 41 (order set quarantined).
- 63 session choices (SC-01 to SC-63), each with its reversal.
Not settled:
- The requirements baseline (layer 3 is READY_FOR_REVIEW_B pending S-80/EQ-30).
- Board B's stackup (6 or 8 layers), escape method and routability (EQ-01, Q-B-ESC-2 specified).
- Board A's copper weight; fabricator prices (EQ-14).
- All seven feasibility blockers FEA-001 to FEA-007 (ZEROIZE bench, EMCON per transmitter, failover fabric, power/thermal, battery protection R-BAT, decoupling, case fit).
- M1's night energy balance (REQ-072 FAIL; the owner action M-02).
- HOT-R1, which is in no generator (EQ-22); TX_INHIBIT_n's fail-safe level (EQ-25).
- The PWR-001 declarations on C and P; the SI-001 edge rates; the MPN/order codes (EQ-21).
- The AW7915-AED and LimeSDR cold carve-out (PWR-F09); D-18 (the fans).
- SC-02's NEED-03 exceptions and the D-01 deferrals are flagged as scope exceptions, not settled design (s3).
Files: CONTINUATION-BRIEF.md s2, s3, s4 ('At H2'), s5.2; START-HERE.md s2-3; LAYER-STATUS.md 'Status at handover H2'; ENGINEERING-QUESTIONS.md index; v2/ecad/tools/pcb_requirements.yaml (checked with handover_counts.py: 144 records, 29 owner rulings, 63 SCs, 60 open items).

### Question 3 (adequate: True)

How the boards connect:
- P feeds E over an XT60 lead, with SMBus/PRES on a JST (IF-PE-PACK).
- E feeds the stack through the E5 block into board A's spring pins (IF-AE-DOCK): four 9 A VIN_RAW pins, four CELL+ pins, pre-charge, USB, SHORE_INHIBIT.
- 11 SMP-MAX RF blind-mates run between E and A (12 under D-07).
- A makes every rail: the slot rails +5V_S1..3, +5V_DEV and 54 V PoE go to B (IF-AB-POWER), with a control/USB ribbon and the wall USB.
- A to D is a harness (USB, inhibit, PA_EN, I2C, 3.3 V, +5V_D8). A feeds the 30 W PA (13.8 V) and the lid QMX (12 V).
- B to C (IF-BC-PANEL) carries PANEL_5V, the kit I2C and the hardware safety lines (SLOT_EN1..3, PI_KILL, EMCON_HW, TX_INHIBIT_n, ZEROIZE_HW). C drives A's main switch.
- C is the only path to slot power (the D-03 boot order).
Failure boundaries per board are in ARCHITECTURE s3.2. There are 30 board_to_board contracts in pcb_interfaces.yaml, and the firmware obligations are in HW-FW-CONTRACT.md. I ran check_contracts.py: PASS 99 of 99. It judges pin-map identity only, not levels, timing or mating, as the pages say.
Caveats: the pcb_interfaces.yaml read_at header and ARCHITECTURE s3.1's netlist hashes are still anchored at eadbe571.
Files: v2/docs/ARCHITECTURE.md s3.1, s3.2 (Mermaid plus diagrams/svg/arch-3-2-board-interconnect.svg), s5, s12; v2/ecad/tools/pcb_interfaces.yaml; v2/docs/HW-FW-CONTRACT.md; v2/docs/diagrams/ (power-tree, control-lines); START-HERE s5 layer 5.

### Question 4 (adequate: True)

COMPLETE:
- Layer 1: PRODUCT-BRIEF BASELINED in 6b2a9965. Review A layer 1 (two passes); release check FAIL B1-B3, fixed; second release check FAIL on R2-B1 only; narrow verification TARGETED-CHECK-LAYERS-1-3 closed R2-B1 and R2-m1 (its sha256/16 ae70b1a7811ecea1 matches).
- Layer 2: CONOPS BASELINED at 79963b3b. Review A layer 2 (pass 1 FAIL, then P2-B1/B2 answered); release check FAIL B1-B4, answered; second release check with no blocking finding. OPERATING-ENVELOPE, TEST-PLAN and pcb_envelope.yaml sha256/16 43361b02, 4f15bd02, bbcc2b5c match what the page says was reviewed.
- All of these are AI reviews. Carried without holding layer 2: M-02, REQ-072 FAIL, FEA-004, HOT-R1, BAT-F19, with stated reopen conditions.
IN_PROGRESS:
- Layer 3: S-80/EQ-30, a wording fix to CON-010's newest entry and the header naming 79963b3b; then a fresh re-check, the re-baseline (S-51, S-78) and a snapshot from a pushed commit (S-79).
- Layer 4: FEA-001 to FEA-007 open; Review C not held.
- Layer 5: pass-2 contract fields, the SLOT_EN hold, GND-002, E5's INT-001 UNBOUND, HOT-R1's pin.
- Layer 6: no MPN field; 1630 of 2393 BOM rows have no LCSC code; U8; R-PWR.
- Layer 7: mock-up purchase L-07 and heat test; QMX tray; jumper plug; pack hold-down.
- Layer 8: 40 layout-entry reasons, confirmed by handover_counts.py: A 7, B 7, C 5, D 8, E 5, P 6, E5 2. That is 15 current non-PASS readings (SI-001 on all six boards; RF-002 on A-D; PWR-001 on C/D/E/P; BAT-001 on P), E5's INT-001, decision 31's review on A/D/E, and 21 feasibility layout-entry stages. Then the functional review per board (Review D).
- Layer 9: SI-001 edge rates, heat test, F2, prices, channel budgets.
The questions are EQ-01 to EQ-30: 18 desk, 5 physical, 7 external authorisation.
Files: LAYER-STATUS.md 'Status at handover H2' and the H2 steps of each integrator line; START-HERE s3; v2/docs/CURRENT-EVIDENCE.md; v2/docs/records/h2/handover_counts.py; v2/docs/reviews/*.md; ENGINEERING-QUESTIONS.md.

### Question 5 (adequate: True)

Representative calculation (energy_chain.py, REGENERATE s6):
- From the ZIP alone: '12 stage(s), 98 check(s)', the same 15 notes, then FAIL DOCK_BLOCK on the missing Mill-Max page 28, exit 1, exactly as stated.
- After s1a's fetch: PASS of 98, exit 0; _a/_b/_e/_e5/_p all PASS.
- I followed the arithmetic by hand from pcb_energy_chain.yaml. F1 is 25 A with I2t 1000 A2s: 1000/480^2 = 4.3 ms, and 240/25 = 9.6 times the rating (3 required). 65% of 25 A = 16.25 A, which is at least the 10 A continuous. The fault range comes from 4 x 35/3 mOhm + 15 mOhm, about 270 A. Shore F1: 115/200^2 = 2.9 ms. All reproduce.
- Other stdlib runs matched byte for byte: pwr_budget.py (JSON and stdout), frame_seat.py, case_margins.py, handover_counts.py. check_contracts read PASS 99/99.
Regeneration (rented Ubuntu host, KiCad 9.0.9):
- s2: verify OK; sch_prov ee62fdb195a9f217.
- s3, board P: every expected line reproduced. 7 IDC lands, 95 parts/21 symbols, ERC PASS of 123 (106+17), netlist PARITY_AFTER_NOISE efe60479293f0004, schematic PARITY_AFTER_NOISE, provenance DIFFERENT only on schematic_sha256 (a58d0eecc7abe768..., the same value the page gives for 27 September), BOM PARITY 38/38, ERC PARITY_AFTER_NOISE. The second verify lists 13 problems.
- s4, all six boards: PARITY, with netlist hashes equal to the table.
- s5: six ': OK' lines with the stated pages, rows and ERC counts, and 12 'same:' BOM lines.
- s7 suite: exit 1 with 1956 passed, 20 failed, 23 skipped; the 20 failures are exactly the table's.
- s1a: 29 files OK with REF=62f26a44; RELEASE CHECK PASS on 139 rows; validator 144 records, 0 errors, 17 warnings; REQUIREMENTS-TRACE current. The code block's own REF line (the snapshot commit b89b50b4) returns 404.
Re-take (s9): it cannot be run as written. The snapshot commit and its fnd/h2 parents are not public, and an extraction without .git is refused. I made a one-commit git repo from the extraction outside /tmp. The driver refused board P until the gitignored out/ netlists were force-added (git add -f). Then --run --in-place --routed --board p gave exit 0 and 14 readings, matching the consolidated re-take's P row (intent_rails FAIL, pack_protection FAIL, edge_length INCONCLUSIVE, the rest PASS). The one exception is energy_chain FAIL, from the unbundled Mill-Max page, the documented cause. rules_status run 3 times was stable; P read 7 layout-entry reasons (the 6 of the page plus BAT-002 from that citation).
Files: REGENERATE.md s1a-s9, SOURCE.txt, REFERENCED-SOURCES.tsv, v2/ecad/tools/*, v2/docs/records/rv-pwr/, v2/vendor/peli/, pcb_energy_chain.yaml.

### Question 6 (adequate: True)

Next, in order:
1. Desk items that need no purchase:
- EQ-25: change one resistor and add one on board C (TX_INHIBIT_n fail-safe; clears RF-002 on A-D).
- PWR-001 rail declarations on C and P; S-76's diode sheets on D and E.
- HOT-R1 into A's and E's generators (EQ-22).
- Update pcb_pack_protection.yaml to P's generated circuit (BAT-001, REQ-044).
- SI-001 edge-rate bounds per signal class.
- Decision 31's protection-topology reviews on A, D and E.
- Layer 3's S-80 fix and re-check.
2. Board B:
- impedance_2d solves for the 6-layer re-assignment and the 8-layer stack;
- then Q-B-ESC-2 (cap 5 USD / 4 box-hours) before any whole-board route, and never a routing campaign just because a host is free.
3. Re-read the layout constraint sheets against the H2 netlists. My run shows they are stale, e.g. A's VIN_RAW is now 14.1 A and 15.29 mm.
4. Get the owner's authorisations (READY-TO-ACT s0): heat-balance test, then mock-up L-07 in the same case, ZEROIZE bench, R-BAT, R-PWR, R-HSD, fabricator quotes (EQ-14).
5. Enter layout per board only when its computed layout-entry test and the hand checks of CONTINUATION-BRIEF s5.1 pass. C is closest.
Preserve:
- Owner rulings D-01 to D-17 (D-01 staged acceptance, D-04 no CE claim, D-05 EMCON meaning, D-03/decision 30 ZEROIZE, D-06 pack, D-07 5G jacks, D-10 SOS, D-12 service port, D-14 dock lift, D-16 no surge claim).
- The Peli 1450 forever, no vents, C1 to C6, the device set, three identical CM5 slots with a hardware-enforced single owner per peripheral.
- The EMCON hardware line, SC-08, SC-10, decision 31, the P0 layer rule, decisions 27/28/43/35/36/42/41, In1 as ground, no uncoupled pair.
- Process rules: two attempts then change method; AI review labelled as AI review; every SESSION choice recorded with its reversal; money, contact, publication and promotion stay with the owner.
Files: CONTINUATION-BRIEF.md s1, s2, s4 ('At H2'), s5, s6, s7; LAYER-STATUS.md H2 table; v2/docs/reviews/READY-TO-ACT.md s0; v2/docs/layout-constraints/ (calc/rail_widths.py re-run).

## What was run

All on H2.zip, copied with H2.zip.sha256 into scratchpad/h2check/; sha256 OK (20072be7...cf35).
Runner (Python 3.11.2, PyYAML 6.0.3, stdlib only):
- handover_pack verify: OK. sch_prov: ee62fdb195a9f217.
- pwr_budget.py, frame_seat.py, case_margins.py and handover_counts.py: byte-identical to their reference outputs.
- check_contracts: PASS 99/99.
- rules_lib requirements from the ZIP: 144 records, 13 errors, 17 warnings; rules_render --requirements --check: REFUSED (as documented).
- energy_chain from the ZIP: FAIL of 98 on the Mill-Max citation (as documented).
- Second extraction, section 1a: with the literal REF (b89b50b4, not public) every fetch 404s. With REF=62f26a44, 29 of 29 files OK; check_manifest RELEASE CHECK PASS (139 rows); validator 0 errors, 17 warnings; REQUIREMENTS-TRACE current; energy_chain PASS of 98, all per-board chains PASS.
- diagrams build.py --check: 4 of 11 current (the pages say 6 of 11; scene.py is excluded). extract_mermaid --check: current.
- layout-constraints/calc/rail_widths.py --markdown: 41 lines differ from the committed rail_widths.out (sheets stale against the H2 intents).
Rented host (/root/h2check only; df first: 48 GB free; KiCad 9.0.9, Python 3.12.3; deleted afterwards and checked for leftover processes):
- Sections 2 and 3 (board P regeneration): every expected line matched, 13 verify problems.
- Section 4: PARITY on A, B, C, D, E and P, netlist hashes 2c5c1d5a..., 39d83d25..., 96c2678f..., ecc07f38..., b8d237f0..., efe60479..., as tabled.
- Section 5: six OK lines, pages 16/43/5/7/4/2, BOM rows 586/1179/167/218/174/69, ERC counts as tabled; 12 'same:' lines.
- Section 7 suite: exit 1, 1956 passed, 20 failed, 23 skipped; failure list identical to the table.
- Section 9: refused on the extraction and in a git repo built with plain 'git add -A'. With git add -f, board P's re-take ran (exit 0, 14 readings, 15 files copied to routed/, results as expected except energy_chain FAIL from the missing Mill-Max page). rules_status x3 stable (the 2nd and 3rd runs matched); rules_render --check REFUSED the trace page (30 closed-by-commit errors in a history-less repo). 'sed -n 5p' printed a blank line.

## Defects found

| Rank | Where | Problem | Suggested fix |
|---|---|---|---|
| MINOR | REGENERATE.md s9 (re-take) and s7 (repository route); SOURCE.txt timeline | The snapshot commit b89b50b4 and the fnd/h2 commits cecfd0f1, 3e4799eb, 6b2a9965, 763bccdf and c5d09c78 are marked 'public no', so 'git clone <repository>; git checkout <commit>' cannot reach H2's source. Section 7's claim that 'a full clone has them' is false for cecfd0f1 (S-77's closing commit), so the registry cannot validate that closure from any public clone. The only route that runs, a repository built from the ZIP, is undocumented. | Push fnd/h2 before issuing the snapshot, or state in s9 the public fallback (62f26a44 plus what differs) and the build-a-repo-from-the-ZIP route. |
| MINOR | REGENERATE.md s9, run from a repository built from the extraction | retake_schematic_phase.py REFUSES every board ('out/<board>.net not tracked'), because the snapshot's .gitignore ignores out/ where the committed netlists live. It works only with 'git add -A -f'. In such a history-less repo the validator also turns the 17 closed-by-commit warnings into errors (30), and rules_render --check REFUSES REQUIREMENTS-TRACE. Re-taking one board re-renders every other board's page from NO_EVIDENCE. | Document the 'git add -f' step and the expected refusals, or ship a script that builds the repository from the ZIP. |
| MINOR | REGENERATE.md s1a code block | The block sets REF from SOURCE.txt's commit line, which for H2 is the unpublished b89b50b4. Pasted as written, every fetch returns 404 ('FETCH FAILED'). The prose says to use the newest public commit, but the code does not. | Compute REF as the newest 'public yes' commit of the timeline, or state REF=62f26a44 for H2 in the block. |
| MINOR | v2/docs/layout-constraints/*.md and calc/rail_widths.out; CONTINUATION-BRIEF s5.3; LAYER-STATUS layer 9 H2 row | The sheets are bound to e3aedb25's netlists and intents. Re-running calc/rail_widths.py --markdown on H2 changes 41 lines: board A's VIN_RAW goes from 12.31 A / 11.92 mm to 14.10 A / 15.29 mm on the outer layer, the rails PRECHG, VMON, +3V3_EMCON_EF and +3V3_EMCON are new, and board B's intent has changed. The brief still calls the sheets 'the constraint record to follow', and no H2 page says they are stale. | Regenerate the calc outputs and sheets at H2, or flag them as stale in START-HERE s3 and LAYER-STATUS layer 9. |
| MINOR | CONTINUATION-BRIEF s1 step 5, s5.1, s8 'Mock-up timing' vs pcb_requirements.yaml FEA-007, LAYER-STATUS H2 table, CURRENT-EVIDENCE | Which boards FEA-007 holds is contradictory. The registry holds a, b, d, e, e5 and p, and the computed page lists FEA-007 for D and E5. The brief says 'boards C, D and E5 not held', and its s5.1 omits FEA-007 entirely ('E5: its rule evidence alone'). | State that desk items hold D and E5 and the mock-up holds A, B, E and P, and add FEA-007 (and E5's INT-001) to s5.1. |
| MINOR | START-HERE s3 known gap 6; LAYER-STATUS 'Known gaps of H2' | The pages say 'python3 v2/docs/diagrams/tools/build.py --check' reads 6 of 11 current. From the ZIP it reads 4 of 11, because case-plan and case-zstack depend on v2/cad/render/scene.py, which pack.yaml excludes as 'presentation'. Two engineering drawings, and layer 7's open item (scene.py's typed QY), rest on that excluded file. | Bundle scene.py, or record its exclusion and the 4-of-11 result. |
| MINOR | ENGINEERING-QUESTIONS EQ-20, EQ-01, EQ-02; GLOSSARY 'worktree' row | Stale text: - EQ-20 is still titled 'not merged', and its Evidence row sends the reader to candidates/r8b.patch, which H2 references rather than bundles. The same files are bundled under v2/docs/records/r8b/ (r8-decisions.md, tools/bbm_sim_r8b.py, evidence/bbm-sim-*.txt). - EQ-01's 'After round 8's board B netlist merges' and EQ-02's 'Draw (a) in round 8 now' are not updated for H2. - The glossary says the handover carries the worktrees as patches. | Restate these rows at H2 and point EQ-20 at v2/docs/records/r8b/. |
| MINOR | CONTINUATION-BRIEF s2.1 D-02 row, s8 (several rows), s5.3 | Unmarked stale statements: - 'a closed-lid reduced mode (to be defined)', while START-HERE says it is defined in CONOPS 4c (SC-17). - s8's 'Pack' row still says pcb_energy_chain.yaml carries 4S4P / about 200 Wh, which its header has since corrected. - Many s8 rows read 'edit owed' with no H2 status. - s5.3's B_PANEL_5V line has since been closed by b76c18cb. | Add Superseded marks, or restate the brief's s2 and s8 at H2. |
| MINOR | GLOSSARY.md | Overloaded and undefined identifiers: - C1 to C6 are case choices, while C1 to C4 are thermal controls ('C1 defined one way'). - M1 to M5 are missions, while M1, M4a, M5, M13 and M17g/x are case margins and M-02 is an owner action. - E1 to E8 and E3-H are test rows, while E1 is also a board. - The evidence classes CURRENT_CANDIDATE, VALID_HISTORICAL and AWAITING_REVALIDATION, and the causes BOUND, UNBOUND, RATIONALE, CONFIG_CHANGED, TEMP_INPUT and OTHER_DESIGN, are defined only in CURRENT-EVIDENCE. - PS-IDLE-SPEC, PS-TYP, PS-RED, HOT-R1, BANK-R1, SD-EMC-1 and the IF-* contract names are not glossed. - CURRENT-EVIDENCE says 'SI-001 INCONCLUSIVE on VALID_HISTORICAL evidence' while the pages call it a current reading, which needs these definitions to reconcile. | Add these families to the glossary, with their disambiguation. |
| MINOR | LAYER-STATUS.md (251 KB), per-layer sections | The page is written in four strata: the e3aedb25 audit with file:line anchors at e3aedb25, then H1, H1.1 and H2. Integrator lines are single paragraphs of thousands of words. The per-layer acceptance tables are at e3aedb25, so an unmarked 'no' may or may not still be open. Only the top H2 table is reliably current. | Add a short H2-only acceptance table per layer and move the audit and edition history to an appendix. |
| MINOR | LAYER-STATUS H2 row, layer 3 vs REGENERATE s1a and s7 | The layer 3 row says the registry validates with '0 errors, 0 warnings'. REGENERATE and START-HERE give 0 errors and 17 warnings (closed-by-commit checks that need git history). | State under which conditions each count holds. |
| MINOR | pcb_interfaces.yaml board_to_board.read_at; ARCHITECTURE.md s3.1 | Both carry eadbe571 anchors: the old netlist hashes, 'check_contracts PASS 91 of 91', 'AWAITING_REVALIDATION (TOOL_CHANGED)' and '8 of 333 pairs current'. These contradict the H2 state (99/99, 62 of 338 current, the new netlist hashes). | Re-anchor both at H2, or label them historical at the point of use. |
| MINOR | REGENERATE s9 command list; START-HERE s8; handover_counts.py output | Small instruction and output defects: - 'sed -n 5p ../docs/CURRENT-EVIDENCE.md' prints a blank line; the headline is on line 6. - START-HERE s8 omits poppler-utils and Pillow, which REGENERATE lists. - handover_counts.py truncates a row label ('the hold itself stays until:'). - gen_sch_p prints 'nets: 51 single-pin nets ...: []', a count with an empty list. | Use sed -n 6p, add the two dependencies to START-HERE s8, and fix the two outputs. |
| MINOR | README.md, v2/README.md in the snapshot | The image links (v2/images/) and the v1 links are broken inside the ZIP because those files are excluded. START-HERE s7 states the exclusion, but the READMEs do not. The READMEs also still carry the known carried minor 'eleven blind-mate clamps' (R2-m6). | Add a note, or strip the links in the snapshot copy. |
