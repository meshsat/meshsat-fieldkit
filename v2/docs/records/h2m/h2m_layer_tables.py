#!/usr/bin/env python3
"""LAYER-STATUS.md after H2: a short acceptance table at H2 opens each layer, and each layer's audit at e3aedb25 with its
integrator line moves, byte for byte, into Appendix A (the H2 usability check's minor finding 10). Session tool of the H2
minor-findings editor (MESHSAT-1357, 27 September 2026); asserts that every moved line survives and that the text
changes."""
import re, sys

P = sys.argv[1]
src = open(P, encoding="utf-8").read()
lines = src.split("\n")

H = "At H2"
# layer -> (status sentence, rows [(items, item text, state at H2, evidence or what remains)])
T = {
1: ("**COMPLETE** since `6b2a9965` (the brief BASELINED after the narrow verification). The states below are those of "
    "the second release check (`v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md`, section 4, which maps its rows "
    "to these items) with the targeted fix and its narrow verification "
    "(`v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`); every one is an AI review",
  [("1.1", "clear product purpose", "MET", "the release check's row 1"),
   ("1.2", "users stated", "MET", "row 2 (D-04; four roles; no target organisation, stated)"),
   ("1.3", "prototype scope stated", "MET", "row 3 (D-01, SC-01, SC-04, CONOPS 2a)"),
   ("1.4", "exclusions stated", "MET", "row 4; minor R2-m2 carried"),
   ("1.5", "intended outcome stated", "MET", "row 5 was NOT MET on R2-B1 (FEA-007 missing from the core feasibility blockers); closed by the targeted fix `cecfd0f1`, verified CLOSED at `3e4799eb`"),
   ("1.6", "report and deck commitments tracked separately", "MET", "row 6"),
   ("1.7", "claims agree with the engineering baseline", "MET", "row 7 (B1 to B3 of the first check closed, R2-B1 closed as for 1.5); README.md's \"eleven blind-mate clamps\" (R2-m6's m6) corrected after H2"),
   ("1.8", "every owner ruling of 25 and 26 September recorded", "MET", "row 8; minor R2-m4"),
   ("1.9", "the owed stale texts of BUILD.md and both READMEs closed", "MET", "row 9, at `eb9f9030` (R2-m1, R2-m6)"),
   ("1.10", "SIM description (CFL-010, S-13)", "MET", "row 10 (SC-13); the eSIM variant's order code is on layer 6's list"),
   ("1.11", "required review held (Review A)", "MET", "Review A layer 1 (two passes), two release checks and the narrow verification, all AI reviews, labelled"),
   ("1.12", "versioned package another engineer can use", "MET", "the H2 snapshot (`v2/release/handover/H2.zip`)"),
   ("rows 11, 12, 15 of the release check", "carried-mass limit (REQ-023); records filed; section 2 of the owner's prompt", "MET", "SC-14; `v2/docs/records/w1/`; nothing lowered, dropped, weakened or narrowed (row 15 met once R2-B1 closed)")]),
2: ("**COMPLETE** at `79963b3b` (recorded in `62f26a44`). The states below are those of the second release check "
    "(`v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md`, section 4, items 2.1 to 2.17), an AI review with no "
    "blocking finding",
  [("2.1 to 2.10", "the normal, degraded, startup, charging, shutdown, storage, service and fault scenarios; the envelope; simultaneous modes and duty", "MET", "section 4 of the release check: met as the first release check found, with B1's and B2's edits"),
   ("2.11", "explicit behaviour of the core functions", "MET", "B1 closed; minor m12"),
   ("2.12", "product decisions settled under existing authority", "MET", "inside the layer; M-02 is the owner's action, recorded and not holding the layer (SC-21 sets M1's duration)"),
   ("2.13", "every owner ruling recorded", "MET", ""),
   ("2.14", "consistent with the current analyses", "MET", "for C1 and EMCON (B1, B4 (a)); the lags in other layers' texts are tracked there (n4, n10)"),
   ("2.15", "TEST-PLAN envelope limits consistent with the rulings", "MET", "B2 closed; minor m2"),
   ("2.16", "every source the CONOPS cites is in the repository", "MET", "B3 closed"),
   ("2.17", "Review A held and recorded", "MET", "passes 1 and 2, the first release check and the second, all AI reviews")]),
3: ("IN_PROGRESS. The states below are those of the second release check "
    "(`v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md`, section 4, at `eb9f9030`, the content landed at "
    "`79963b3b`) and the narrow verification of the targeted fix (B-1 NOT_CLOSED at `3e4799eb`); AI reviews",
  [("3.1 to 3.8", "records trace to needs; source-linked; citations resolvable; measurable acceptance; applicability; allocation; verification method and phase; no check needs a later stage's product", "MET", "section 4 of the release check; minors n1, m5 carried"),
   ("3.9", "contradictions resolved", "MET", "M1 stated one way (R2); CFL-017's routes in EQ-26; minors n4, m1, m2 carried"),
   ("3.10 to 3.13", "needs, choices, assumptions and history kept apart; TBDs with their effect; every critical mission outcome measurable; REQ-050's trace of TEST-PLAN", "MET", "minor n3 carried"),
   ("3.14", "Review B held and the registry baselined", "OPEN", "B-1: S-80 and EQ-30 (CON-010's newest entry against its FAIL, and the header naming `79963b3b`'s re-take), a re-check of that fix, then the re-baseline (S-51, S-78)"),
   ("3.15", "every open item carried by a record", "MET in substance", "the letter is not met (n7: open items in no record's `waits_on`)"),
   ("3.16, 3.17", "every BLOCKER or MUST_JUSTIFY rule has a parent record; the trace generated and current", "MET", "59 of 59 rules named; `rules_render.py --requirements --check` current in a git checkout"),
   ("3.18", "versioned, portable layer package", "OPEN", "B-2: S-79 and EQ-29, a snapshot cut from a pushed commit carrying the re-baseline; H2 carries layer 3 IN_PROGRESS")]),
4: ("IN_PROGRESS. No release check has judged this layer; the states below are this page's reading of what landed "
    "since `e3aedb25` (the integrator line in Appendix A.4 and the H2 table above), each naming its commit or record. "
    "\"As at `e3aedb25`\" means nothing since changes the audit's answer",
  [("4.1", "functional diagrams current (power, data, control)", "MET", "`v2/docs/diagrams/`: context, interconnect, power tree, power-up, lanes and fabric, control lines, battery states, case; drawn on set 5's netlists at `b7f96784` (`730f8489`), SVG and PDF; hc4's two AI reviews; the manifest check's count is START-HERE known gap 6"),
   ("4.2", "physical diagrams current", "PARTLY", "the case drawings and the case release carry C1 to C6 (`c351115d`); `v2/cad/pack_4s.py` still draws the 4S4P block (S-27) and `scene.py`'s QY is a typed copy"),
   ("4.3", "diagrams and architecture reviewed, AI review labelled", "PARTLY", "hc4's AI reviews of the diagrams; Review C not held"),
   ("4.4", "power and data paths documented on the committed design", "PARTLY", "documented at `eadbe571` (ARCHITECTURE sections 4 and 5, cited to generator lines); the diagrams are on set 5's netlists; ARCHITECTURE's text is not re-read on the H2 netlists (its section 3.1 re-anchored after H2 only)"),
   ("4.5", "control paths consistent and complete", "PARTLY", "supervisor addresses 0x34 to 0x36 everywhere (hc5, `0da2778b`); the control-lines drawing; open: the SLOT_EN hold in no generator, EMCON's shared-line items L1 to L4 and L7 (FEA-002), TX_INHIBIT_n's fail-safe level (EQ-25)"),
   ("4.6", "mode behaviour defined", "PARTLY", "the reduced mode (SC-17), the heat stage and the hot stop defined in CONOPS 4c and baselined with layer 2; the restrictions stated as controls; open: HOT-R1 in the generators (EQ-22), BANK-R1 (S-54), the SDR limiter as at `e3aedb25`"),
   ("4.7", "energy and runtime budget with margin", "OPEN", "PROVISIONAL runtime; no runtime value set, so no margin; REQ-072 FAIL at desk (S-53, M-02, EQ-13)"),
   ("4.8", "thermal budget with margin", "OPEN", "conductance unmeasured; the bound includes failure (FEA-004, EQ-05)"),
   ("4.9", "lane budgets with margin", "OPEN", "as at `e3aedb25` (FEA-003, EQ-01, EQ-12)"),
   ("4.10", "rail and interconnect margins", "PARTLY", "PWR-003 PASS on B (`b76c18cb`: F1 the MF-MSMF110); the dock's VIN_RAW on four 9 A pins (SC-55, EQ-16's supply side); board B's supplies declared from the makers' sheets (`caba1876`, PWR-001 PASS on A and B); not re-checked at H2: R17's rating, IF-AB-POWER's two ends (I-03), PWR-F02"),
   ("4.11", "mass, dimension and cost budgets", "PARTLY", "a mass limit set (SC-14, REQ-023); dimensions: 35 of 70 case rows OPEN, M17g and M17x failing as assumed (FEA-007); cost TBD (EQ-14)"),
   ("4.12", "trade decisions recorded", "PARTLY", "SC-01 to SC-63 with their reversals; open: board B's stackup and escape method (EQ-01), the layer counts, U8 (EQ-06), F2 (EQ-07), the fans (D-18)"),
   ("4.13 to 4.18", "feasibility demonstrated; ZEROIZE, EMCON, failover, power and thermal, battery questions resolved", "OPEN", "FEA-001 to FEA-007 all FEASIBILITY_OPEN: EMCON 15 of 17 local at desk and 0 of 17 end to end (EQ-02 the RockBLOCK row); FAB-01 to FAB-04 drawn (`b76c18cb`) with EQ-20's residual; the flange sensor drawn on D (`76235aad`); ZEROIZE's bench (EQ-06); R-BAT (EQ-10)"),
   ("4.19", "Review C held", "OPEN", ""),
   ("4.20", "no feasibility stage waits for what it gates", "OPEN", "the misplacements of CONTINUATION-BRIEF section 5.1 stand"),
   ("4.21", "qualified review routes named and costed", "MET", "as at `e3aedb25`; none engaged"),
   ("4.22", "sibling records consistent with the architecture", "PARTLY", "IOHA, ZEROIZE, CONOPS, OPERATING-ENVELOPE and `pcb_pack_protection.yaml`'s topology line brought in line (CONTINUATION-BRIEF section 8, H2 marks); open: FAILOVER-FABRIC's Q-B-ESC-1 text, ARCHITECTURE 13.1's F-CH-04 row, POWER-THERMAL's pack-path widths")]),
5: ("IN_PROGRESS. No release check has judged this layer; the states below are this page's reading of what landed "
    "since `e3aedb25` (Appendix A.5's integrator line and the H2 table above)",
  [("5.1", "board responsibilities and partition settled", "OPEN", "board B's outline and floor plan (EQ-01)"),
   ("5.2", "every interface owned at both ends with its connector", "PARTLY", "30 contracts (hc5, `0da2778b`); the first twelve lack the pass-2 fields; the board-to-board IDC headers carry no MPN (EQ-21)"),
   ("5.3", "pinouts identical at both ends", "MET", "`check_contracts.py` PASS 99 of 99 on the H2 netlists (map identity and presence only); INT-001 current on the six boards with a schematic, E5's UNBOUND"),
   ("5.4", "electrical levels stated per interface", "PARTLY", "the kit I2C budget computed (CON-026 FAIL at desk; three segments owed, SC-59, S-59); `HW-FW-CONTRACT.md`; the rest as at `e3aedb25`"),
   ("5.5", "power capacity of each power interface with margin", "PARTLY", "IF-AE-DOCK answered at desk for the supply (SC-55); IF-BC-PANEL's PWR-003 PASS (`b76c18cb`); open: E5's targets and the ground share (S-74, S-75), IF-AB-POWER (I-03), the ribbon and SMP-MAX ratings TBD"),
   ("5.6", "sequencing across interfaces", "OPEN", "the SLOT_EN hold in no generator; HOT-R1 (S-57, EQ-22)"),
   ("5.7", "reset, default and cable-out states for every control line", "PARTLY", "HOT-R1's four line states in `HW-FW-CONTRACT.md`; TX_INHIBIT_n's fail-safe level found failing (EQ-25); the rest as at `e3aedb25`"),
   ("5.8", "communications and addressing consistent", "PARTLY", "supervisor addresses reconciled (0x34 to 0x36); the panel USB wire format outside the repository (MESHSAT-837)"),
   ("5.9", "harnesses defined and consistent", "PARTLY", "ASSEMBLY section 4 carries C2 to C4 (`c351115d`); the touch USB's board end (SC-63); open: the jumper plug (M17g, M17x), J_AB2's lead"),
   ("5.10", "mechanical mating of every interface", "OPEN", "W4-F17; the clamp bar replaces the nests (`45f6d83f`); D-07's site on A in no generator; E5 generated from A32's board file (S-74)"),
   ("5.11", "firmware obligations affecting hardware explicit", "PARTLY", "`HW-FW-CONTRACT.md` version 1 (heartbeat resolved; FW-C13, FW-C14, FW-E10 for the hot stop); PANEL.md's reduced-mode and hot-stop duties owed (layer 2's m13)"),
   ("5.12", "GND-002 implemented everywhere", "OPEN", "none of the four board changes in a generator"),
   ("5.13", "interface contracts consistent with the tree", "PARTLY", "`read_at` re-anchored at `ef144760` after H2; the contracts' generator lines are as each contract states them; the pass-2 fields owed"),
   ("5.14", "Review C over the interfaces", "OPEN", "EQ-12 for R-HSD"),
   ("5.15", "INT-002 pre-layout assessment", "MET", "PASS as a desk review (the session's AI review) on board B's current nets (`PCB-RULE-STATUS-B.md`); INT-003 at prototype")]),
6: ("IN_PROGRESS. No release check has judged this layer; the states below are this page's reading of what landed "
    "since `e3aedb25` (Appendix A.6's integrator line); hc6's records were reviewed once (AI review, no blocking item)",
  [("6.1", "exact manufacturer, MPN, package and grade per fitted part", "OPEN", "no MPN field; 1630 of 2393 per-reference BOM rows without an LCSC code (EQ-21); grades in `v2/docs/parts/GRADE-CHECK.md`, AW7915-AED and LimeSDR OUTSIDE"),
   ("6.2", "supporting documents with revision, source and currency", "PARTLY", "fourteen SOURCES entries added (hc6); the documents START-HERE section 8 names are not held"),
   ("6.3", "selection rationale recorded", "PARTLY", "for critical parts (hc6); not for the passive and connector majority"),
   ("6.4", "compatibility findings; mismatches stay mismatches", "PARTLY", "`jlc_certify.py` reads the declared mismatches (`661ca3a4`); the standing wrong models not re-checked at H2"),
   ("6.5", "STM32H753 against STM32H743", "MET at desk", "`v2/docs/parts/STM32H743-COMPATIBILITY.md` (`99cde56b`); the firmware obligations it names are S-41"),
   ("6.6", "procurement constraints and alternatives", "PARTLY", "`PROCUREMENT.md` with dated readings; HX6096NL's readings not filed"),
   ("6.7", "regenerated outputs preserve part decisions", "PARTLY", "regeneration PARITY on all six at H2; codes the certification refuses still typed in generators, not re-checked at H2"),
   ("6.8", "a current, versioned BOM with identity per board", "PARTLY", "the H2 NOT_FOR_FAB BOMs of all six boards; identity only where an LCSC code is chosen (EQ-21)"),
   ("6.9", "CMP-001", "MET", "PASS on every board on evidence that counts as current (`CURRENT-EVIDENCE.md`); its DC-bias gap is 9.18"),
   ("6.10", "CMP-002 and SUP-001", "OPEN", "INCONCLUSIVE: the certification readings predate the tool's change"),
   ("6.11", "Review D per board and R-PWR before A's layout entry", "OPEN", "EQ-11")]),
7: ("IN_PROGRESS. No release check has judged this layer; the states below are this page's reading of what landed "
    "since `e3aedb25` (Appendix A.7's integrator line: hc7 and its targeted fixer c7, `c351115d`, with the fresh "
    "verifier's AI check)",
  [("7.1", "editable CAD current", "PARTLY", "C1 to C6 in `panel1450.py`, `z_budget.py`, `case_wall_cutouts.py` and the CAD (`c351115d`); `scene.py` and `v2/images/face-section.png` draw the superseded face; the pack box draws 4S4P (S-27)"),
   ("7.2", "dimensioned drawings of every made part and templates", "MET", "`v2/release/case-2026-09-27/` sheets 1 to 14; the QMX tray not to be printed before S-63 (EQ-24)"),
   ("7.3", "board envelopes and the Z stack", "PARTLY", "the Z stack drawn (`zstack.json`, the case-zstack drawing); W4-F17 open"),
   ("7.4", "mounting and retention", "OPEN", "the pack hold-down (S-27) and the stack's retention undesigned; the face's mounting drawn (C1)"),
   ("7.5", "connector, cable and service access", "PARTLY", "the connector plate (C3) drawn; the jumper plug (M17g, M17x) and the sealed RJ45 open"),
   ("7.6", "tolerance analysis reproducible", "MET", "as at `e3aedb25`; `frame_seat.py` and `case_margins.py` reproduce byte for byte from the ZIP (the H2 usability check)"),
   ("7.7", "blind-mate and dock tolerance stack closed on paper", "OPEN", "FEA-007's desk item for A, E and E5 (the clamp bar and an ANT3 clamp at X +46)"),
   ("7.8", "thermal interfaces specified", "PARTLY", "the PA flange sensor drawn on D (`76235aad`); the fans unsettled (D-18); the conductance (EQ-05)"),
   ("7.9", "critical fit uncertainties resolved by suitable evidence", "OPEN", "FEA-007: the mock-up (L-07, EQ-08) and the desk items"),
   ("7.10", "later physical checks allocated, deferral justified", "PARTLY", "FEA-007 stages the YES rows at layout entry on the decision they move; FEA-004's heat-test staging stays in CONTINUATION-BRIEF 5.1's misplacements"),
   ("7.11, 7.12", "REQ-019 (every case margin MET); CON-006 (a named pack build with its hold-down)", "OPEN", "35 rows OPEN, 2 failing as assumed; S-27"),
   ("7.13", "MEC-001 on the current case geometry", "PARTLY", "board C's gate reads the Z stack (`c351115d`); MEC-001 reads FAIL on A and PASS on B to P and E5 (`PCB-RULE-STATUS-*.md`); the case rows remain FEA-007's"),
   ("7.14", "session engineering choices recorded with authority", "MET", "SC-07 and the case choices, SESSION under the standing rule"),
   ("7.15", "no contradictory live specifications; superseded artefacts labelled", "PARTLY", "ASSEMBLY, V2-SPEC, BUILD, the READMEs and REQ-047 carry C1 to C6; `release/revA/case/` labelled HISTORICAL; `scene.py` and `face-section.png` superseded"),
   ("7.16", "review labelled; no qualified route pretended", "PARTLY", "the agent checks are labelled AI; no qualified mechanical route exists (FEA-007)"),
   ("7.17", "portable regeneration of the mechanical outputs", "PARTLY", "`v2/cad/requirements-cad.txt` and `.lock` pin the CAD's Python packages; the margin scripts reproduce; renders need Blender 4.2 on a GPU host")]),
8: ("IN_PROGRESS on every board. No release check has judged this layer; the states below are this page's reading "
    "of what landed since `e3aedb25` (Appendix A.8's integrator line and the H2 table above). Per board, the "
    "layout-entry reasons are the H2 section's table",
  [("8.1", "current native schematic per board", "MET", "round 8 on all six, set 5 on A, B, D and E; regeneration PARITY on all six"),
   ("8.2", "readable PDFs", "MET", "`v2/release/handover/_generated/` (A, B, D, E at `763bccdf`; C, P at `99cde56b`)"),
   ("8.3, 8.4", "generator inputs and source; netlists", "MET", "title-block labels keyed in the glossary"),
   ("8.5", "BOMs", "PARTLY", "two NOT_FOR_FAB BOMs per board; the identity gap is layer 6's (EQ-21)"),
   ("8.6", "functional circuit reviews completed", "OPEN", "Review D per board; R-BAT, R-PWR, R-HSD (EQ-10 to EQ-12)"),
   ("8.7", "exact part and land mapping", "PARTLY", "SCH-005 PASS on current evidence on all six; the WRONG_MODEL rows of condition 1 not re-checked at H2"),
   ("8.8", "relevant ERC completed", "MET", "SCH-001 PASS on current evidence on all six (the re-take); board B's errors allow-listed with reasons"),
   ("8.9", "regeneration shown by regenerating and comparing", "MET", "PARITY on all six from a clean archive (REGENERATE.md section 4), reproduced by the H2 usability check"),
   ("8.10", "known schematic-affecting defects closed per board", "OPEN", "TRN-001 and PWR-003 now PASS; open: EQ-25 on C (RF-002 on A to D), PWR-001 on C, D, E, P, BAT-001 on P (REQ-044), HOT-R1 on A and E (EQ-22), the FEA items per board"),
   ("8.11", "board-specific completion marked", "MET", "per board in the H2 section and `CURRENT-EVIDENCE.md`"),
   ("8.12", "Review D per board gates layout entry", "OPEN", ""),
   ("8.13", "schematic-phase rules PASS on current-candidate evidence", "OPEN", "every schematic-phase reading current but E5's INT-001; 15 current readings are not a PASS"),
   ("8.14", "decision 31's layout-entry requirements on A, D, E", "PARTLY", "fitted parts and TRN-001 PASS on current evidence; the review record owed"),
   ("8.15", "INT-002 on board B's current nets", "MET", "desk review, AI, bound (`PCB-RULE-STATUS-B.md`)"),
   ("8.16", "review packet at each board's candidate", "OPEN", "the packets are at `1f614233`; A and B never packaged"),
   ("8.17", "condition 1: substitutions stay mismatches until proven", "PARTLY", "declared mismatches read by the certification (`661ca3a4`); not re-checked at H2"),
   ("8.18", "STM32H743 alignment", "MET", "the generator and netlist; V2-SPEC's corrections name the H743")]),
9: ("IN_PROGRESS. No release check has judged this layer; the states below are this page's reading of what landed "
    "since `e3aedb25` (Appendix A.9's integrator line and the H2 table above)",
  [("9.1", "current power calculations with margins and sensitivities", "OPEN", "`pwr_budget.py` reproduces from the ZIP, but models the `1f614233` boards; not re-run on the H2 line"),
   ("9.2", "current energy calculations with sensitivities", "OPEN", "PROVISIONAL; REQ-072 FAIL at desk"),
   ("9.3", "protection coordination on the current design", "PARTLY", "`energy_chain.py` PASS of 98 on the H2 netlists once Mill-Max's page 28 is restored (REGENERATE.md section 6); PWR-003 PASS on A, B, E, P, E5; BAT-001 FAIL on P (REQ-044); decision 31's review owed"),
   ("9.4", "thermal analysis current", "OPEN", "FEA-004, EQ-05; THM-001 INCONCLUSIVE on every board"),
   ("9.5", "signal analysis pre-layout", "OPEN", "SI-001 INCONCLUSIVE on all six (edge rates owed, START-HERE known gap 5); IMP-001 INCONCLUSIVE; channel budgets (EQ-12)"),
   ("9.6", "timing analysis", "PARTLY", "PWR-002 PASS on A, B, E, P and CLK-001 PASS where it applies; FB-FAB-4's break-before-make drawn (`b76c18cb`) with EQ-20's residual; EMCON latency end to end open (FEA-002)"),
   ("9.7", "placement constraints analysed", "PARTLY", "the per-board sheets (re-bound to the H2 line after H2); board B's floor plan (EQ-01); PLC-001 FAIL on A and B reads their historical layouts"),
   ("9.8", "constraints handed to layout written per board", "MET", "`v2/docs/layout-constraints/`, re-bound to the H2 line after H2 (known gap 8); each sheet's open items named"),
   ("9.9", "analyses needing routed geometry named and allocated", "MET", "as at `e3aedb25`"),
   ("9.10", "analyses needing hardware in the test plan", "PARTLY", "TEST-PLAN traces its tests to requirements (3.13) and carries P15, E3-L and E3-H; the heat-balance test is in POWER-THERMAL section 10 and READY-TO-ACT, not re-checked in TEST-PLAN at H2"),
   ("9.11", "pre-layout portion without claiming post-layout or physical verification", "MET", ""),
   ("9.12", "stackup decided per board with measurement and cost", "OPEN", "board B undecided; board A's copper weight; no price (EQ-14)"),
   ("9.13", "every board passes the staged layout-entry test", "OPEN", "0 of 7; 40 reasons"),
   ("9.14 to 9.16", "FEA-004 (A, D), FEA-006 (A to P), FEA-003 (B) and FEA-005 (P) layout-entry stages", "OPEN", "each is among its boards' layout-entry reasons at H2"),
   ("9.17", "INT-002 current on its 48 nets", "MET", "as 8.15"),
   ("9.18", "CMP-001 with DC-bias derating", "OPEN", "as at `e3aedb25`"),
   ("9.19", "qualified reviews preserved; AI review labelled", "PARTLY", "labelling met; R-PWR and R-HSD unapproved (EQ-11, EQ-12)"),
   ("9.20", "a representative calculation re-runs from the repository alone", "MET", "`energy_chain.py` (REGENERATE.md section 6) and `pwr_budget.py` from the ZIP; most other tools need `pcbnew`")]),
}

# locate the sections
heads = [i for i, l in enumerate(lines) if re.match(r"^## Layer [1-9]\. ", l)]
assert len(heads) == 9, heads
first = heads[0]
assert lines[first - 2] == "---", lines[first - 2]
pre = lines[:first - 2]          # up to (not including) the '---' before Layer 1
bodies = []
for k, h in enumerate(heads):
    end = heads[k + 1] - 2 if k + 1 < 9 else len(lines)
    sec = lines[h:end]
    if k + 1 < 9:
        assert lines[end] == "---" and lines[end + 1] == "", (k, lines[end:end + 2])
    bodies.append(sec)

out = list(pre)
out += ["---", ""]
appendix = ["---", "", "## Appendix A. The audit at `e3aedb25` and each layer's edition history",
            "",
            "Moved here after H2 (27 September 2026, the H2 usability check's minor finding 10), byte for byte, from the "
            "layer sections above: for each layer its status at `e3aedb25`, scope, prerequisites, deliverables by "
            "revision, the acceptance items as judged at `e3aedb25` (with their inline **Superseded in H1** marks), the "
            "unresolved decisions, the stage-gate cycles, the next closing actions, the per-board lines and the "
            "`INTEGRATOR LINE` with its steps H1 to H2. Its file:line citations are lines at `e3aedb25`. Other pages cite "
            "these by layer and item (\"LAYER-STATUS layer 3, item 3.4\", \"layer 8 actions 1 to 3\"), which are here "
            "under the same numbers. The acceptance table at H2 that opens each layer section above is the current "
            "reading; where it and this record differ, it is the newer.", ""]
for k, sec in enumerate(bodies):
    n = k + 1
    head = sec[0]
    title = head[len("## "):]
    status, rows = T[n]
    out.append(head)
    out.append("")
    out.append("**%s: %s.** The audit of this layer at `e3aedb25` and its edition history (the integrator line) are "
               "Appendix A, section A.%d, unchanged." % (H, status, n))
    out.append("")
    out.append("| Item | Acceptance item (short) | At H2 | Evidence, or what remains |")
    out.append("|---|---|---|---|")
    for it, txt, st, ev in rows:
        out.append("| %s | %s | %s | %s |" % (it, txt, ("**%s**" % st) if st.startswith("OPEN") else st, ev))
    out.append("")
    out.append("---")
    out.append("")
    body = sec[1:]
    while body and body[0] == "":
        body = body[1:]
    appendix.append("### A.%d %s (the audit at `e3aedb25` and the edition history)" % (n, title))
    appendix.append("")
    appendix += body
    if appendix[-1] != "":
        appendix.append("")
# drop the trailing separator of the last layer section before the appendix
while out and out[-1] == "":
    out.pop()
if out[-1] == "---":
    out.pop()
while out and out[-1] == "":
    out.pop()
out.append("")
new = "\n".join(out + appendix).rstrip("\n") + "\n"
# every original line survives
old_set = {}
for l in lines:
    old_set[l] = old_set.get(l, 0) + 1
new_lines = new.split("\n")
new_set = {}
for l in new_lines:
    new_set[l] = new_set.get(l, 0) + 1
lost = [l for l, c in old_set.items() if new_set.get(l, 0) < c and not l.startswith("## Layer ") and l not in ("---", "")]
assert not lost, lost[:3]
assert new != src
open(P, "w", encoding="utf-8").write(new)
print("layer tables written; lines %d -> %d" % (len(lines), len(new_lines)))
