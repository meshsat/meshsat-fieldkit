# MeshSat field kit V2: continuation brief for an incoming engineer

Written 27 September 2026 (MESHSAT-1357) from the repository at commit `e3aedb25`. Paths are repository paths.
Citations of a Markdown page name its section heading (since H1.1); a citation of a code or data file by line is a
line at `e3aedb25`, which the public repository serves at
`https://raw.githubusercontent.com/meshsat/meshsat-fieldkit/e3aedb25/<path>`. Internal names are defined in
`v2/docs/handover/GLOSSARY.md`. Read `v2/docs/handover/START-HERE.md` first; the per-layer detail behind
every line below is in `v2/docs/handover/LAYER-STATUS.md`, and each blocked question is written out in
`v2/docs/handover/ENGINEERING-QUESTIONS.md` (EQ-01 to EQ-30 in H2).

**Handover H2.** The snapshot carries this brief as written at `e3aedb25` plus section 0 (what changed from H1.1 to
H2, the newest) and section 0a (what changed from `e3aedb25` to H1: main `84e52461`, circuit round 8 sets 1 and 2, and
the handover branch, last design change `99cde56b`). Where section 0 or 0a and a later section disagree, section 0 is
the newest; the sentences of later sections they supersede carry an inline **Superseded in H1** or **Superseded in
H2** mark.

## 0. What changed between H1.1 and H2

The newest section of this brief; section 0a below is the step from `e3aedb25` to H1. The counts of the design's state
here are printed by `v2/docs/records/h2/handover_counts.py` from the snapshot's files, and the others name their
commit; `LAYER-STATUS.md`, section "Status at handover H2", gives each layer's evidence and remaining items.

- **Layers 1 and 2 are COMPLETE** for their own engineering purpose, each with its review records (AI reviews, none a
  qualified review): the product brief BASELINED in `6b2a9965` after the narrow verification
  (`v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`), CONOPS BASELINED at `79963b3b` after the second
  release check (`v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md`). H2 is their versioned package. What they
  carry without being held by it (M-02 and S-53, BAT-F19, HOT-R1, S-58, FEA-004, BANK-R1, S-55, the minors) is listed
  in LAYER-STATUS.
- **Layer 3 is IN_PROGRESS**: the registry validates (144 records, 0 errors) but its baseline was reversed by the
  narrow verification on one unstated registry difference (S-80, EQ-30), a wording fix and a re-check away from the
  re-baseline; a snapshot cut from the pushed commit that carries it closes S-79. Layers 4 to 9 are IN_PROGRESS.
- **Circuits.** Board B's round 8 is merged (`b76c18cb`): the fabric's locked break-before-make, per-slot EMCON and
  the 5G supply removed in hardware; its residual is EQ-20. Set 5 (wave 3) regenerated A (the EMCON gates behind their
  own eFuse, EQ-17 closed at desk with a bound; PoE and USB-C enable nodes), B (every supply declared, W3B-F1 and
  W3B-F2), D and E (supplies declared; board E's tracker senses on its bottom leg, S-47's core; VIN_RAW across the
  dock on four 9 A power pins with board A's half, EQ-16). Section 0a's "board B's round 8 is not merged" is
  superseded.
- **Readings.** The consolidated re-take (`8ea7867e`, REGENERATE.md section 9) re-took every schematic-phase reading on
  the committed netlists: 83 readings on seven boards, layout-entry reasons 101 to 40, no board ready for layout. Per
  board: A 7, B 7, C 5, D 8, E 5, P 6, E5 2 (LAYER-STATUS gives each reason). The only schematic-phase reading still
  AWAITING_REVALIDATION is E5's INT-001.
- **New findings since H1.1:** W3T-F1 (EQ-25: TX_INHIBIT_n's fail-safe level with board C unpowered, the RF-002 FAIL
  on boards A to D; one resistor changed and one added on board C is the recommended remedy); PWR-001 FAIL on C and P
  (power nets no rail declares, EQ-19); S-64 to S-76 in the registry; the hot stop past the heat stage (REQ-077) with
  HOT-R1 owed on A and E (EQ-22); FEA-007, the kit's fit in the Peli 1450, holding the layout entry of six boards: D
  and E5 on its desk items alone (D: W4-F17; E5: the dock and blind-mate tolerance stack), A, B, E and P on their desk
  items and the mock-up's checks (EQ-08); board C is not held by it at layout entry, only at fabrication release.
- **Delivered since H1.1:** the hardware and firmware contract (`v2/docs/HW-FW-CONTRACT.md`) with 30 interface
  contracts; the case release for C1 to C6 (`v2/release/case-2026-09-27/`, `v2/docs/CASE-FIT-UNCERTAINTIES.md`); the
  re-take driver (`v2/ecad/tools/retake_schematic_phase.py`); the diagrams on set 5's netlists; the H2 exports of A,
  B, D and E with regeneration PARITY on all six (`v2/release/handover/_generated/`).
- **The candidate patches of H1.1 are superseded** (every one merged from a later state; `candidates/README.md` names
  each commit) and are referenced rather than bundled in H2, to keep the ZIP under its cap.
- **Known gaps of H2** (START-HERE section 3): the readings the pages render are outside the snapshot; the suite needs
  a git checkout; the ZIP is deterministic per host; maker documents and the superseded patches are referenced; SI-001's
  edge-rate declarations are owed on every board; the diagrams' manifest reads 6 of 11 current by file hash in the
  repository at H2 and 4 of 11 from the H2 ZIP, because `v2/cad/render/scene.py`, an input of the two case drawings,
  was excluded as presentation (bundled after H2); Q-B-ESC-1's final boards are not in the package.

**After H2 (27 September 2026, the H2 usability check's minor findings; `v2/docs/handover/H2-RESPONSE.md` gives each
finding, where it is answered and the commit).** No design file changed. The layout constraint sheets and their power
tables are re-bound to the H2 line's netlists and intents (`v2/docs/layout-constraints/`; board A's VIN_RAW is 14.10 A
and 15.29 mm there, not 12.31 A); `pcb_interfaces.yaml` `board_to_board.read_at` and `ARCHITECTURE.md` section 3.1 are
re-anchored at `ef144760` (INT-001's readings re-taken after the edit of their configuration input, the evidence pages
unchanged); `handover_pack.py repo` builds a repository from a snapshot for the re-take route (REGENERATE.md section
9); section 1a computes its `REF`; `scene.py` is bundled; FEA-007's boards are stated one way; this brief's sections
2.1, 5.1, 5.3 and 8 carry H2 marks.

## 0a. What changed between `e3aedb25` and H1

- **Circuits (round 8).** Boards A, C, D, E and P were regenerated with parity: A gates its PA and HF rails on both
  EMCON lines; C reads EMCON one way and has a hardware EMCON lamp; D powers its transmit chain only while its EMCON
  gates are in range and reads the PA flange temperature; E declares its raw bus from both feeds and fits the
  decoupling its makers ask for; P orders the JST headers the catalogues list. **Board B's round 8 is not merged**
  (worktree `fnd/r8b`, EQ-20; bundled since H1.1 as the UNACCEPTED candidate patch
  `v2/docs/handover/candidates/r8b.patch` on base `fc144600`): H1's board B is still B21's pre-round-8 netlist. Step
  3 of section 1 therefore remains for board B only. **Superseded in H2:** merged at `b76c18cb` (section 0).
- **SIM.** Session choice SC-13 (27 September 2026, `pcb_requirements.yaml`) takes Quectel's compatible design for
  USIM2, which `gen_sch_b.py` already carries: two nano-SIM holders, the second behind four 0 ohm links, so one board
  also builds the eSIM-plus-nano-SIM configuration the owner approved. CFL-010 stays open only for the SIM TVS array
  (at most 10 pF) and the eSIM variant's order code; section 8's SIM row is superseded.
- **Checks.** PWR-001 and SI-001 are judged on the committed netlists and PWR-001 fails closed on every undeclared
  supply (EQ-19); RF-002 walks every transmitter's hardware inhibit path and cannot yet decide TX_INHIBIT_n through
  board C's SN74LVC1G57 (EQ-18). No board is ready for layout: reasons A 17, B 16, C 11, D 15, E 16, P 15, E5 5.
- **New open findings:** BAT-F20 (EQ-15), R8E-N01 (EQ-16), board A's +3V3 window (EQ-17), and HC9-E1 (S-47): board E's
  LT8705A current-sense resistor sits in the inductor's leg, so CSP and CSN would see up to the 15.1 V output against
  a 3 V rating; the maker places it between the joined sources of the bottom FETs and GND. It blocks board E's layout
  entry (`v2/docs/layout-constraints/E.md` section 6.1).
- **Delivered by the handover closers:** the product brief and public overviews through Review A layer 1 (layer 1,
  still a candidate for BASELINED), readable diagrams (`v2/docs/diagrams/`, drawn at `b7f96784` with round 8 and set 5), the layer 6 part
  records (`v2/docs/parts/`), and one layout constraint sheet per board with the stackup record
  (`v2/docs/layout-constraints/`, `v2/docs/STACKUP-DECISIONS.md`): step 4's constraint sheets exist; the stackup
  decisions they record still carry the cost half owed (EQ-14).
- **Exports.** Paged schematic PDFs, NOT_FOR_FAB BOMs, ERC and netlist parity of every board at `99cde56b`, with
  regeneration PARITY on all six (`v2/release/handover/_generated/`, REGENERATE.md).
- **Not in H1's design** (**superseded in H2** for the closers' work and board B's round 8, merged since, section 0;
  hc9's and hc6's drafts for other owners remain outside the design): the layer 2, 3, 5 and 7 closers' work (candidates in worktrees, LAYER-STATUS "Candidates
  left in worktrees"), board B's round 8, and hc9's and hc6's drafts for other owners. Since H1.1 the first two are
  bundled as UNACCEPTED candidate patches (`v2/docs/handover/candidates/`: `hc2.patch`, `hc3.patch`, `hc5.patch`,
  `hc7.patch`, `r8b.patch`), each with its base, sha256 and last review's blocking findings in the folder's README.
- **Known gaps of H1.** The readings behind `CURRENT-EVIDENCE.md` and `PCB-RULE-STATUS-*.md` live in the gitignored
  `v2/ecad/out/` and each board's `out/` folder and are not in the snapshot; the rendered pages are. REGENERATE.md
  section 9 states the re-take procedure that reproduces and updates them, in words in H1.1; **its driver,
  `v2/ecad/tools/retake_schematic_phase.py`, landed after H1.1** (`e5fde2ed`, branch `fnd/r8int4`): `--plan` lists
  every schematic-phase writer per board from the registries, `--run --in-place --routed` takes them on the committed
  netlists in a throwaway git clone outside `/tmp` on a KiCad 9.0.9 host, then `rules_status.py` three times and
  `rules_render.py` (REGENERATE.md section 9, with its trial on `a8652172`: 73 commands, reasons 95 to 37). The test suite
  needs a git checkout for `test_netlist_provenance` and for the registry's closed-by-commit checks (REGENERATE.md
  section 7). The ZIP's bytes are deterministic per host only: compare `MANIFEST.tsv`, not the ZIP's sha256, across
  hosts.

**Prototype framing.** Nothing of the V2 kit has been built, ordered, powered or measured. All reviews of the current
design are AI reviews, labelled as such; the qualified human reviews the records require (R-BAT, R-PWR, R-HSD, and
R-SEC and R-EMC in their turn) have not been engaged.

## 1. What to do first

If you are taking over the design, in this order:

1. Read the product brief, the concept of operations and the operating envelope (layers 1 and 2), then this brief's
   section 2 (what must be preserved) and section 8 (which records disagree and which one to follow).
2. Close layers 1 to 3 at desk: they need no purchase, no bench and no outside contact (LAYER-STATUS, layers 1 to 3).
   The earliest open decisions with hardware consequences are the reduced-mode host set, the SIM description, the
   storage and transport configuration of the pack, and the core requirement limits. **Superseded in H2:** layers 1
   and 2 are COMPLETE; layer 3 needs S-80's wording fix, its re-check and the re-baseline (EQ-30, EQ-28).
3. Integrate the circuit corrections that were in flight at `e3aedb25` (round 8, on every board), one board at a time,
   with regeneration parity, then take one consolidated re-take of every schematic-phase reading on a KiCad 9.0.9 host
   (layer 8 actions 1 to 3; the procedure is REGENERATE.md section 9). **Superseded in H1:** round 8 is merged for A,
   C, D, E and P; for board B, apply `v2/docs/handover/candidates/r8b.patch` to `fc144600`, re-derive its drafted
   page patches on the current text, and merge it with parity. **Superseded in H2:** board B's round 8 is merged
   (`b76c18cb`), set 5 regenerated A, B, D and E with parity, and the consolidated re-take is done (`8ea7867e`); the
   next circuit step is each board's remaining layout-entry reasons (LAYER-STATUS, section "Status at handover H2").
4. Decide the stackups per board with a written measurement and cost (P0 rule), and write one layout constraint sheet
   per board (layer 9 actions 6 and 8). **Superseded in H1:** the sheets and the stackup record exist
   (`v2/docs/layout-constraints/`, `v2/docs/STACKUP-DECISIONS.md`); the cost half of each stackup decision is owed
   (EQ-14). Run board B's bounded experiment Q-B-ESC-2 before any whole-board route.
5. Ask the owner for the authorisations on the critical path: the empty-case heat test and the case mock-up (the
   heat test before hot-part placement freezes; the mock-up before the layout entry of boards A, B, E and P, which is BLOCKED on the purchase since 27 September 2026
   (FEA-007, L-07; `v2/docs/CASE-FIT-UNCERTAINTIES.md` sections 1, 2 and 7), after the heat test in the same case; FEA-007
   also holds boards D and E5 on its desk items, which need no purchase), the ZEROIZE bench (before board B's layout entry), R-BAT (before board P's
   release and the pack build), and the R-PWR and R-HSD decisions (ENGINEERING-QUESTIONS, groups B and C;
   `v2/docs/reviews/READY-TO-ACT.md` section 0).
6. Enter layout per board only when its computed layout-entry test and the hand checks of section 5.1 are met. Do not
   start a routing campaign because a host is available (the owner's prompt, section 4).

## 2. Settled decisions to preserve

These are ruled. Changing one needs the authority that made it (OWNER rulings: the owner; SESSION choices: the
reversal each names). "Recorded in" names where the ruling is authoritative.

### 2.1 Product and scope

| Decision | What it fixes | Recorded in | Authority |
|---|---|---|---|
| D-01 full design, staged acceptance | every ruled function designed and fitted where copper exists; prototype 1 accepted on the named core (messaging over Iridium, 5G, LoRa and APRS; the three-slot failover fabric; pack, vehicle and solar charging; hardware EMCON; ZEROIZE; pack safety; service and programming access); the rest reported NOT_YET_TESTED | `pcb_requirements.yaml` `owner_rulings` D-01; `v2/docs/CONOPS.md` section 2a | OWNER |
| SC-01 SOS in the core | NEED-19 added to the core as D-10 defines it | `session_choices` SC-01 | SESSION (standing rule) |
| SC-04 how D-01 applies record by record | core or deferred per requirement | SC-04; CONOPS 2a | SESSION |
| D-04 markets and obligations | non-commercial prototype in the Netherlands and the EU, operated by a licensed radio amateur; no CE, RED or EMC claim; every MIL-STD-461 run is characterisation | D-04; CONOPS section 7 | OWNER |
| D-02a to D-02e envelope | -20 to +40 C in use, -20 to +45 C storage; +55 C, +71 C and -33 C are qualification margins with two pass lines (in specification inside the envelope, survive and recover at the margin); a closed-lid reduced mode (to be defined; **superseded in H2:** defined by SC-17 in `v2/docs/CONOPS.md` section 4c, baselined with layer 2); E1 26 drops from 1.22 m and E2 composite wheeled vehicle; altitude 0 to 3000 m in use, 4500 m in transport; no cold start from a pack below about -10 C; operate shaded | D-02a to D-02e; `v2/docs/OPERATING-ENVELOPE.md` section 8; `pcb_envelope.yaml`; decision 34 | OWNER; decision 34 SESSION |
| SC-03 E5 humidity cycle | a qualification margin judged like E3 and E4 | SC-03 | SESSION |
| D-16 no vehicle surge claim | the vehicle and shore entry is not qualified; not for 24 V military buses | D-16 | OWNER |
| D-09 qualified reviews | the SIDN voucher goes to a ZEROIZE and key-fill security review (R-SEC); a paid battery and protection review happens before the pack is built (R-BAT); EMC pre-compliance once a prototype exists (R-EMC) | D-09; `v2/docs/reviews/REVIEW-ROUTES.md` | OWNER |

### 2.2 Case and mechanics

| Decision | What it fixes | Recorded in | Authority |
|---|---|---|---|
| The case is the Peli 1450, never changed | the enclosure | appendix 32.62 (line 3054) | OWNER |
| The current moulding of Peli drawing 1451-931 (15 January 2025); the owner's case measurement withdrawn | the design targets Peli's own figures; an older case is replaced, not designed for | D-08a; D-08-reversal | OWNER |
| No vent opening anywhere in the case, plate or connector plate; IP68 fans inside; Peli's pressure valve stays | the sealed thermal path | appendix 32.53 (line 2856); REQ-020 | OWNER |
| The face is a 3 mm aluminium plate with a backer board, in the 1450PF frame | face construction | appendix 32.40 items 4 and 5 (line 2576) | OWNER |
| Case arrangement C1 to C6: face plate 377.2 x 263.0 on Peli's ten 6-32 inserts from above over Peli's o-ring; twelve gas-discharge arrestor bulkheads at Z 59 on two RF entry plates (the third 5G jack conditional on D-07); connector plate 114.0 x 68.3 x 5.0; the QMX lid tray; four setting legs | every case-dependent outline and connector place | SC-07; `v2/docs/CASE-MARGINS.md` section 4; CONOPS 7a | SESSION |
| D-07 three 5G jacks (ANT0, ANT2, ANT3) at the board A site X +46, if the board E clamp fit is shown; otherwise two | A's RF row, E's clamps, the east wall | D-07 | OWNER |
| D-14 dock lift: kit off, pack XT60 unplugged, shore removed, and an insulating cap over E5 while the stack is out | service procedure; the E5 cap (not yet drawn, S-22) | D-14; `v2/docs/ASSEMBLY.md` section 7 | OWNER |

### 2.3 Architecture and functions

| Decision | What it fixes | Recorded in | Authority |
|---|---|---|---|
| The V2 device set: RockBLOCK 9704 with a Maxtena helical; Quectel RM520N-GL 5G on M.2 key B; E22-900M30S 1 W LoRa, EU power capped; two E72 CC2652P (Zigbee coordinator, Thread RCP); two AsiaRF AW7915-AED link cards; LimeSDR Mini 2.4; NiceRF SA868 with the RA30H1317M1 30 W amplifier; QRP Labs QMX HF; Quectel LG290P GNSS; Xenarc 709GNK monitor; PDi wide-temperature e-paper | parts of the core and deferred functions | appendix 32.49 and 32.50 (lines 2752, 2779); `v2/docs/V2-SPEC.md` with corrections | OWNER |
| Three identical CM5 slots; every radio and sensor a USB device shared by the HAL (with named exceptions); k3s across the modules; hub banks switched in hardware under 2-of-3 voted supervisors; hardware, not firmware, prevents two modules owning one peripheral | the compute and failover architecture | appendix 32.52 (line 2827); `v2/docs/ARCH-PCB-B-IOHA.md` section 1 | OWNER |
| SC-02 NEED-03 exceptions | LoRa (slot 3's SPI) and cellular data (slot 2's PCIe lane) go with their module; NEED-03 acceptance stays IOHA A1 to A14 | SC-02; CONOPS 2a; IOHA 15a | SESSION. Reverse by naming either bearer critical, which reopens board B's floor plan |
| EMCON is a hardware line from a locking panel toggle, plus a software hold | the inhibit architecture | appendix 32.50 item 3; `v2/docs/PANEL.md` section 6 | OWNER |
| D-05 what EMCON means | every radio with an emission path powered off or RF-disabled in hardware; the VHF receiver keeps listening behind its transmit-only gate; GNSS, DCF77 and the lightning sensor continue | D-05; EMCON.md | OWNER |
| SC-11 SD-EMC-1 | the 5G module's firmware-independent inhibit is removal of its supply, staged in the maker's order | SC-11; EMCON.md section 5 | SESSION |
| D-03 and decision 30 ZEROIZE | a crypto-erase through the secure element: drive and eMMC keys wrapped by a key the secure element holds; ZEROIZE destroys it, then modules drop RAM keys, then the slots are cut | D-03; decision 30 | OWNER |
| SC-08 ZEROIZE on the ATECC608B | two key-encryption keys (slots 0 and 1, SlotConfig 0x2084, KeyConfig 0x0013), both destroyed by GenKey mode 0x04; proposed pass lines 1.5 s and 3.0 s; the SLB 9673 TPM is the fallback if the bench fails | SC-08; `v2/docs/feasibility/ZEROIZE.md` sections 3 and 9 | SESSION (physical demonstration open, EQ-06) |
| D-10 SOS | a distress message with position over the available bearers (Iridium first when nothing else is up) to a configured list; never through EMCON (queued, and the operator told); firmware only | D-10 | OWNER |
| D-12 service port | the wall USB data path goes to the sealed Glenair 233-370 receptacle (console and key fill); the USB-C is power only | D-12 | OWNER |
| D-13 firmware integrity | software-verified boot on the STM32H743 supervisors for the prototype; a hardware root of trust at a production trigger | D-13 | OWNER |
| The panel is driven per `v2/docs/PANEL.md` | panel behaviour and firmware contract | PANEL.md | OWNER (the contract), SESSION (its revisions) |
| Decision 29 | board B's three CM5 Ethernet links stay capacitively coupled, no magnetics (verification at INT-003; EQ-09) | `pcb_decisions.yaml` 29 | SESSION |

### 2.4 Power and pack

| Decision | What it fixes | Recorded in | Authority |
|---|---|---|---|
| D-06 the pack | one 4S3P block of Samsung INR18650-35E, about 145 Wh, shrink-wrapped in the east pocket; missions longer than the pack rely on vehicle or solar input; runtime stated as battery-only hours in two modes at +20 C for an aged pack. D-06's text still says "subject to the case measurement (D-08)"; D-08 is reversed and D-06 stands without it | D-06 | OWNER |
| SC-05 the runtime modes | PS-IDLE-SPEC and PS-TYP | SC-05 | SESSION |
| D-11 all transmitters at once | allowed for a declared key-down time above a declared state of charge, with the outlets at their minimum contract | D-11 | OWNER |
| SC-10 D-11's thresholds (PROVISIONAL) | all-transmit only above 15.5 V rest; the PA alone only above 12.4 V; every PA key-down at most 60 s, started only with every cell at most +55 C and the flange at most +75 C, outlets, heater and standby WiFi card off, ended early above 18 A, at a low cell or at +85 C on the flange | SC-10; POWER-THERMAL section 7.2 | SESSION |
| D-15 and decision 40 cell protection | a 4S secondary protector independent of software; cell under-voltage in hardware if a part at similar cost covers it, else in the gauge's firmware with a data-flash verification at commissioning | D-15; decision 40 | OWNER |
| SC-09 the secondary over-temperature stays active | the BQ7720700 on its own thermistor (J_TS2); the pack's margins are its cells' limits | SC-09; `v2/docs/review-packets/battery/SECONDARY-OT-DECISION.md` | SESSION (coordination against 60 C still open, EQ-10) |
| D-17 ESD at A's USB-C CC pins | an external low-capacitance ESD array by the connector | D-17 | OWNER |
| Decision 31 clamp at the entry | protection at the conductor where it leaves the case, with fitted parts named per board; the fabrication hold on A, D, E stays until its evidence exists | decision 31; `v2/ecad/tools/pcb_board_holds.yaml` | SESSION |

### 2.5 Layout rules already ruled

| Decision | What it fixes | Recorded in |
|---|---|---|
| The P0 rule (owner, 11 September 2026) | every board's layer count needs its own written decision with the measurement that forced it and the cost it adds; a stackup is never inherited from a sibling or promoted silently when a route fails; layer count and stackup are on the "never automatic" floor of `v2/ecad/tools/reserved.json` | `v2/docs/LAYER-DECISIONS-2026-09-11.md` opening; appendix 32.106 |
| Decisions 27, 28, 43 (owner, 25 September) | board C six layers; board P four layers at 2 oz outer; board B measured on eight layers first, EXPERIMENTAL, never adopted as a phase | `pcb_decisions.yaml`; appendix 32.365 |
| Decision 7 | two-layer boards (E5) are 2 oz | `v2/docs/OWNER-DECISIONS-2026-09-11.md` section 7 |
| In1 a solid ground plane (owner, 5 September) | a board-wide In1 rule area forbidding tracks and permitting vias, except the window the CM5 receptacles' 0.4 mm breakout needs | appendix 32.40 item 3 (line 2580) |
| Pair matching (owner, 5 September; decision 36) | a differential pair is judged at the tighter of 1.00 mm and its part's own number; the owner's ruling is the floor | decision 36 |
| No uncoupled differential pair at release (owner, 10 September) | the impedance gate has no per-pair exception | appendix 32.94 (line 3640) |
| Decision 35 | copper is judged against the most conservative of the three ECSS-Q-ST-70-12C Annex D fits, in one place (`track_current.conservative`) | decision 35 |
| Decision 39 | a break in a signal's reference is judged against the project's per-class criterion as a declared calibration | decision 39 |
| Decision 42 | decoupling ruled per capacitor class from the makers' documents; the 3 mm number is a heuristic | decision 42; `v2/docs/feasibility/DECOUPLING.md` |
| Decision 47 | the 1 mm length rule applies to pairs whose class declares an impedance target, not to Kelvin taps | decision 47 |
| Decision 46 | board A's LM5176 gate-drive lengths accepted for the A98 revision and carried to the next as a finding (reopen for the next layout; layer 9 action 14) | decision 46 |
| Decision 41 | the order set is rebuilt and quarantined; nothing is ordered | decision 41 |

### 2.6 Process rules

- The owner's seven standing conditions (`v2/docs/EXECUTION-PLAN.md` section "Standing conditions (owner, 25 September 2026)"): a part substitution is a mismatch
  until proven; a runtime figure stays provisional until computed properly; a test limit above the envelope may be a
  qualification margin; one writer per shared file; "the generator is current" is shown by regenerating and comparing;
  skipped tests are not passes and a hold lifts only on fresh evidence; board B feasibility evidence permits further
  investigation only, and experiments stay EXPERIMENTAL.
- Stage-specific gates (EXECUTION-PLAN section "Stage gates: layout entry, fabrication release, prototype verification"; section 5.1 below).
- Two attempts, then a change of method (EXECUTION-PLAN section "Priority from 27 September 2026 01:20 CEST: the engineering handover"; the owner's prompt, section 4).
- AI review is labelled AI review and never stands in for a qualified review a record requires.
- Decision authority: money, outside contact, publication and promotion are the owner's. Engineering choices were the
  session's under the owner's rulings of 21 and 26 September 2026 (appendix 32.362 onward; `owner_rulings`
  `standing-rule`); each SESSION choice records its reason and how to reverse it. A team taking over should state its
  own authority model.

## 3. Scope exceptions and deferrals, not to be read as settled design

- **SC-02**: LoRa and cellular data are exceptions to NEED-03 for prototype 1. The public requirement (V2-SPEC section "Compute, storage, expansion (B16, about 330 x 200 mm; the distributed fabric of 32.52)",
  "every device visible to all modules") names no exception; SC-02 narrows it, reversibly.
- **D-01's deferred functions** (Geiger, lightning, DCF77, the outside pod, camera, net audio recording, the tablet
  bracket, the NVG claim, HF, a second pack) stay designed and fitted; only their tests are deferred. Their parts,
  interfaces and protection must still be settled before layout (LAYER-STATUS layer 3, item 3.4 and the deferred TBDs).
- **The second pack** has no location: no pack is expected to fit the west pocket (CONOPS 2a). It stays a deferred
  function, not withdrawn.
- **Cold start and full sun** are stated out of scope for the prototype (D-02d, D-02e), not solved.
- **The hot end** of the envelope is adopted but not established (EQ-05); the +35 C and +25 C restrictions are
  proposed controls.
- **AW7915-AED and LimeSDR Mini 2.4** are rated only from 0 C, outside the -20 C end; a carve-out or a replacement is
  owed (PWR-F09); lowering the kit envelope is not an option.

## 4. Remaining work, in dependency order

The full action lists are in LAYER-STATUS. The order below is by genuine dependency; items on one line can run in
parallel with isolated owners.

| Step | Work | Depends on | Needs outside authorisation |
|---|---|---|---|
| 0 | Layer 1 corrections and Review A (L1); layer 2 decisions (reduced mode, storage and transport, duty profile, hot-end restatement, missing scenarios) and Review A (L2); layer 3 limit settlements, conflicts made true, TEST-PLAN traced, Review B (L3); records filing (W1, W3, W5, W7 drafts, adjudications A01 to A11, board A's converter scripts, the FW-A01 to FW-A16 contract, the Peli page captures) | nothing | no |
| 0 | Contradiction fixes that need no circuit (supervisor addresses 0x34 to 0x36; H743 texts; stale siblings; section 8 below) | nothing | no |
| 0 | Case geometry: C1 to C6 into `panel1450.py` and the CAD; the jumper plug and RJ45 picks; the Z stack drawn; pack hold-down and stack retention designed; the blind-mate tolerance stack (L7 actions 1 to 10) | nothing (board C regenerates only if the backer offsets change) | no |
| 0 | Desk analyses: `impedance_2d` solves for board B's six-layer re-assignment and eight-layer stack; board A's pack-path copper at 18 A under decision 35; a lumped thermal model with sensitivities; channel budgets from primary documents; RF coexistence budget | nothing | no |
| 1 | Round 8 circuit corrections merged board by board with parity (in H1 only board B's remains: `candidates/r8b.patch`, UNACCEPTED) (EMCON remedies, FAB-01 to FAB-04, SD-EMC-1, the SLOT_EN hold, the flange sensor, decoupling classes G1 to G14, VIN_RAW, SIM, U9, U.FL codes, GND-002, the monitor touch USB port, decided since as SC-HF-06 on board D's `J_USB3` with HF-F06 owed on D); the tools merges (PWR-001 and SI-001 on the netlist; mismatch persistence) | step 0 decisions that change circuits (reduced mode, SIM, touch USB) | no |
| 2 | One consolidated re-take of every schematic-phase reading in a clean clone on a KiCad 9.0.9 host with `retake_schematic_phase.py --run --in-place --routed`, its `routed/` copies committed; CURRENT-EVIDENCE re-rendered (procedure: REGENERATE.md section 9) | step 1 | no |
| 3 | ARCHITECTURE.md and `pcb_interfaces.yaml` re-anchored; contracts for the uncovered interfaces; Review C (L4, L5); FEA-003 and FEA-004 restaged | step 2 | no |
| 3 | Parts: certification re-take, per-board BOMs with identity, review packets for A and B (first), D, P, C, E; functional circuit review per board; decision 31 protection-topology review for A, D, E (L6, L8) | step 2 | no |
| 4 | Stackup decision table per board; per-board layout constraint sheets; PWR-F12 in the registries; TEST-PLAN additions (L9) | steps 2 and 3 | prices per layer count (EQ-14) |
| 4 | Board B: Q-B-ESC-2 on the post-round 8 netlist, then decision 43's capped whole-board eight-layer run (EXPERIMENTAL) | step 1 for board B; the router's import handling fix | no (within the box allocation) |
| parallel | Heat-balance test; ZEROIZE bench Z-EXP-A and B; case mock-up T1 to T11; F2 coupon test or Eaton's answer; R-BAT engagement; R-PWR and R-HSD decisions; maker questions | the drawings (mock-up); round 8 packets (reviews) | yes |
| 5 | Layout entry per board, as each board's computed test and hand checks close. The second review asks that C, E and E5 be assessed individually and not held by board B's problems; C is closest | steps 2 to 4 and the board's own external items | per board |

**At H2 (superseding parts of the table above):** step 1 is done (round 8 on all six boards, board B at `b76c18cb`,
and set 5 on A, B, D and E, each with parity) and step 2 is done (`8ea7867e`, reasons 101 to 40). In step 0, layers 1
and 2 are COMPLETE and layer 3 waits on S-80 (EQ-30); the case geometry's C1 to C6 are in the generators and the case
release (`c351115d`), the jumper plug, the RJ45 and the pack hold-down still open. In step 3 the contracts for the
uncovered interfaces exist (`0da2778b`, 30 contracts and `HW-FW-CONTRACT.md`); Review C is not held. The next work
per board is its layout-entry reasons (LAYER-STATUS, section "Status at handover H2"): first the desk items that need
no purchase (EQ-25's two resistors on board C; the PWR-001 declarations on C and P and S-76's diode sheets on D and E;
HOT-R1 on A and E; the pack-protection table on P; the SI-001 edge-rate declarations), then decision 31's reviews on
A, D and E and the feasibility blockers' layout-entry stages, several of which need the owner's authorisation
(`v2/docs/reviews/READY-TO-ACT.md` section 0).

## 5. Constraints for the PCB engineer known today

### 5.1 Stage gates (`v2/docs/EXECUTION-PLAN.md`, section "Stage gates: layout entry, fabrication release, prototype verification")

| Stage | Needs | May not need |
|---|---|---|
| Layout entry | per board: every required schematic-phase rule a PASS on current-candidate evidence; reviewed protection topology, exact fitted parts, corrected schematic, owned interfaces, placement and return-path constraints; each feasibility blocker's layout-entry stage closed (desk evidence, or a development-board test where an architecture decision turns on it) | a layout, a fabricated board or a built kit |
| Fabrication release | the layout implements the reviewed schematic (SCH-002 PASS) and passes the physical protection, parity and routed-board checks; the fabrication-release stages (qualified reviews where a blocker names one, the enclosure heat experiment before hot-part placement is frozen) | a fabricated board or a built kit |
| Prototype verification | the physical tests of TEST-PLAN and the feasibility pages on the built kit | nothing earlier stands in for them |

Per board, beyond its rule evidence, layout entry also needs (EXECUTION-PLAN, the per-board table of that section): A: decision 31's review
on A's netlist with U31 fitted and TRN-001 PASS, FEA-002 (EMCON lines), FEA-004 (the chain re-declared at 18 A for 60
s and A's pack-path copper constraint), FEA-006. B: FEA-001 (Z-EXP-A and B, or the switch taken), FEA-002 (SD-EMC-1,
L1 to L4, L7), FEA-003 (FB-FAB-1 to 5 on the netlist, the escape strategy and stack, channel budgets), FEA-006,
INT-002 current on its 48 nets. C: FEA-002 (the hardware EMCON lamp, L1), FEA-006. D: decision 31, FEA-002, FEA-004
(the flange sensor), FEA-006. E: decision 31, FEA-006. P: FEA-005 (the packet current, the secondary coordination at
desk with its placement constraints, the charger state sequence), FEA-006. E5: its rule evidence alone. **Restated at
H2** (the computed test, `v2/docs/CURRENT-EVIDENCE.md`, adds what the list above predates): FEA-007, the kit's fit in
the Peli 1450, holds A, B, D, E, E5 and P, with D and E5 on its desk items alone (D: W4-F17; E5: the dock and
blind-mate tolerance stack) and A, B, E and P on their desk items and the mock-up's checks of their YES rows; C is not
held by it at layout entry. E5's rule evidence is INT-001, which reads PASS but AWAITING_REVALIDATION (UNBOUND) until
the coverage map names `check_contracts_e5` (the registry writer). A's and B's lists gain SI-001 and RF-002, C's
PWR-001, SI-001 and RF-002, D's PWR-001, SI-001 and RF-002, E's PWR-001 and SI-001, and P's PWR-001, SI-001 and
BAT-001: the current readings that are not a PASS (LAYER-STATUS, section "Status at handover H2").

**Known misplacements to repair before relying on the computed test** (LAYER-STATUS, cycles of layers 4, 5, 7, 9):
- FEA-003's layout-entry stage runs `check_pcb_b.py`, which loads a board file; its text names Q-B-ESC-1 where the
  corrected-input test is Q-B-ESC-2; decision 43's run has no recorded cap.
- FEA-004 stages the heat test at fabrication release although placement freezes inside layout, does not hold board
  B, and stages F2's identity after P's layout entry.
- No layout-entry item checks case geometry, a decided stackup, or pre-layout impedance feasibility.
- The `board_to_board` contracts are read by no tool; open contract findings (I-03, R4A-N13, W4-F17, the SLOT_EN hold)
  must be checked by hand at layout entry.
- R-PWR's timing disagrees between records (before A's layout entry in REVIEW-ROUTES section "Summary", L-04 and ARCHITECTURE
  14.2; not gated in EXECUTION-PLAN or FEA-004). Until reconciled, treat it as required before A's layout is committed.
- PWR-001 and SI-001 read only board files at `e3aedb25`; their readings become current only once the netlist tools
  merge. **Superseded in H1:** both are judged on the committed netlists since round 8 (section 0a; LAYER-STATUS layer 9
  integrator line); their readings still await the consolidated re-take. **Superseded in H2:** the re-take made them
  current on every board (`8ea7867e`): PWR-001 PASS on A and B, INCONCLUSIVE on D and E, FAIL on C and P; SI-001
  INCONCLUSIVE on all six, its edge-rate declarations owed.

### 5.2 Stackups, decided and undecided (all 1.6 mm)

| Board | Stackup | State | Record |
|---|---|---|---|
| A | six layers, JLC06161H-3313 as committed | measured (the four-layer arm left 345 unrouted, 12 September); **copper weight open**: the pack path at 18 A for 60 s needs 23.91 mm of outer copper at 1 oz or 11.95 mm at 2 oz under decision 35, and an inner layer cannot carry it (85 to 170 mm); a transient calculation may relax it; no price | `v2/docs/LAYER-DECISIONS-2026-09-11.md`; decision 35; `boards/a.json` (`_a_copper_weight_is_the_unasked_lever`); LAYER-STATUS layer 9 |
| B | six (JLC06161H-3313: In1 GND, In4 the split 5 V planes) or eight (JLC08161H-2116) | **undecided**. On six as used, inner pairs solve to 140.5 ohm against 100, so pairs can meet impedance only on F.Cu and B.Cu, and B.Cu's reference In4 is split; the re-assigned six (In3 as GND, option A2) is unsolved; decision 43 orders an eight-layer measurement, EXPERIMENTAL, not started | `v2/docs/B-FEASIBILITY.md` sections 3.2, 4, 5; decision 43 |
| C | six, JLC06161H-3313 | ruled (decision 27, from RET-001 and RET-002 failing on 15 B.Cu nets at four layers); not regenerated; price to be quoted before anything is paid | decision 27 |
| D | four, JLC04161H-7628 | kept on the RF ground-plane reason; the rationale is to be written | LAYER-DECISIONS-2026-09-11 |
| E | four, JLC04161H-7628 | kept on routing and In1 (the In2 experiment showed its pours worth little) | LAYER-DECISIONS-2026-09-11 |
| E5 | two, 2 oz (2L-2oz) | decision 7; the board file's Dk 4.6 differs from the record's 4.5 (STK-001 FAIL) | decision 7 |
| P | four at 2 oz outer, JLC04162H-7628 | ruled (decision 28); inner copper weight not chosen; not regenerated | decision 28; `v2/ecad/tools/stackup_write.py` |

No board has a like-for-like price at its alternative layer counts (EQ-14). `v2/docs/LAYER-DECISIONS-2026-09-11.md`
predates decisions 27, 28 and 43; follow the decisions.

### 5.3 Placement, current and return-path constraints known today

**Superseded in H1:** the per-board sheets exist, `v2/docs/layout-constraints/<A|B|C|D|E|E5|P>.md` with their
calculations, and they are the constraint record to follow. **After H2:** they were written against `e3aedb25`'s
netlists and intents and were stale against H2's (board A's VIN_RAW 12.31 A against 14.10 A, rails added on A, B, D and
E); their power tables are regenerated and every sheet is re-bound to the H2 line's netlist and intent (each sheet's
opening lines say what was re-read and what stays as read at `e3aedb25`). The list below is the `e3aedb25` summary they were
written from, kept for its reasoning. At `e3aedb25` the sheets were written nowhere (layer 9 action 8 owed them). What
was known:

- **Board A.** The pack node (CELL+, CELL_FUSED, VBAT) carries 18 A for 60 s on every PA key-down (PWR-F12): width per
  section 5.2, on outer copper; R17 (5 mOhm charge shunt) dissipates 1.62 W at 18 A on a 3 W part with no maker sheet
  held. The eleven RF drops from the SMA jacks to the SMP-MAX blind-mate receptacles are laid by the generator on F.Cu
  at 0.14 mm (about 50 ohm on this stack; 0.35 mm reads about 23 ohm), not left to the router on an inner layer
  (`boards/a.json` `_rf_line_why`). The LM5176 controllers are to sit between their FETs per TI's layout guidance
  (SNVSAI1D), which decision 46 accepted as unmet on A98 and which is to be written as a constraint. J_AB2 must leave
  board D's mezzanine rectangle or D's standoff be re-derived (W4-F17). The third 5G site at X +46 (D-07). Decision 31:
  the clamp (U31 TPD2E2U06QDBZRQ1) at the conductor's entry with a short ground return. ISO-001 creepage on its
  high-voltage nets (the 54 V PoE rail among them).
- **Board B.** The switch pockets of each slot have no room on three sides (B-FEASIBILITY section 3). For slot 3, the
  specification of Q-B-ESC-2 sets the placement conditions, and the same diagnosis applies to the slot 1 and slot 2
  pockets (section 3.1): before any routing the escape pass must escape every connected pad of the switch U301 and the
  hub U302, the band north of U301 must be free of back-side pads under the tip-via line, the AC coupling capacitors C353 to C356 and the clock capacitors C395 and
  C396 sit at their pins, the HCSL resistors R375 to R386 at the east-row clock outputs, C351 and C352 beside pins 123
  and 124, the hub crystal Y301 with C364 and C365 beside U302's XI and XO, R317 beside U301.86 and R342 beside
  U302.64 (`v2/docs/B-FEASIBILITY.md` section 7.9 input 2; FAILOVER-FABRIC FAB-08). Pairs on F.Cu and B.Cu only on the
  six-layer stack as used, and a B.Cu pair crossing between slot rails crosses a reference split. The CM5 receptacles'
  0.4 mm breakout needs both inner signal layers within its In1 window (appendix 32.40). Per-interface pair targets are
  in `v2/ecad/tools/pcb_interfaces.yaml` `interfaces` (for example 0.15 mm intra-pair on the CM5's USB 2.0 and
  Ethernet links, 85 ohm and 0.7 mm on the RM520N-GL's PCIe), judged at the tighter of 1.00 mm and the part's number
  (decision 36). B_PANEL_5V needs at least 0.78 mm at 1 oz, or F1 changes to MF-MSMF110 (PWR-003; **superseded in H2:** closed on the part
by board B's round 8, `b76c18cb`, whose F1 is the MF-MSMF110, 1.1 A hold under the 1.23 A track, `pcb_energy_chain.yaml`
`known_findings`). Long
  runs with no channel budget yet: PCIe upstream 118 to 140 mm, USB 3 failover up to 255 mm plus a mux, HDMI up to 396
  mm through two switches, LimeSDR 217 mm. The supervisor LDOs (AP2112K) overheat at the H743's full clock (PWR-F04):
  a firmware clock bound or a 3.3 V feed.
- **Board C.** Six layers per decision 27; the hardware EMCON lamp's light-guide hole in the face plate (SD-EMC-6).
- **Board D.** The PA flange site is a thermal constraint (a 60 s key-down from a +50 C plate reaches 95 to 118 C
  against the maker's 90 C reliability and +100 C case ratings) and needs a flange temperature sensor (PWR-F15). The
  TPA6132A2 needs 2.2 uF within 5 mm (G12). Decision 31 clamps D9 to D14 at the entry.
- **Board E.** The float-clamp nests overlap at the 14 mm site pitch (a clamp bar, R4E-07); LORA must read board A's
  X; ISO-001 read 92 below limit on 8 high-voltage nets on E17 and PI-001 FAIL, to be written as constraints; decision
  31 clamps D9 and D10 at the entry.
- **Board P.** Thermistor and sense placement for the secondary protector (O-11 re-placement with J_TS2, R34, TP15);
  F2 at the cell block's temperature; four layers at 2 oz.
- **Board E5.** Generated from board A's board file, so it follows A's placement; it carries the pack current through
  its contacts (18 A for 60 s applies); the D-14 insulating cap.
- **All boards.** Decoupling seats per decision 42's classes (G1 to G14 in the generators, T1 to T10 in the tools); the
  sensitive-node keep-outs of `v2/ecad/tools/pcb_sensitive.yaml` and the EMC entries of `pcb_emc.yaml`; the chassis
  bond of GND-002 once drawn; `rise_ns` per signal class still undeclared on A, E and P.

### 5.4 Mechanical interfaces the layout must respect

Board outlines are fixed by the placement generators (A 240 x 160, B 330 x 200, C ring 344 x 228 with a 240 x 176
void, D 100 x 80, E 267 x 68, E5 43 x 26, P 70 x 44) and agree with `v2/ecad/tools/pcb_board_facts.yaml`. Board B's east
edge (X 165) and east-end tall parts depend on the jumper plug pick (M17g, M17x); its stack height under the monitor on
M1; board A's east edge on the pack pocket (M4a); board P's place on the pack hold-down. Every case number the layout
reads must come from CASE-MARGINS C1 to C6, not from `panel1450.py` until that file is regenerated.

## 6. Known failed approaches, and why they failed

### 6.1 Three weeks of whole-board automated routing (3 to 21 September 2026)

**What was done.** From the first commit of the carrier set (`8c57d215`, 3 September) to 21 September, the work was a
generate, route and finish pipeline: each board was generated by its scripts, routed with Freerouting under
`v2/ecad/tools/routeflow.py` on rented hosts, finished by a chain of guarded post-route passes, judged by a growing set
of routed-board gates, and cut into deliverable folders under `v2/release/revA/boards/` (the pipeline is described in
`v2/README.md`, "Regenerating a board"). Deliverable folders were cut for successive phases (the latest A24, C24,
D11, E9, E5 and P4; for the three-module board B only the quote folder B19, since B12 to B15 belong to an earlier
single-module generation).

**Why it failed.** The circuits under the copper had not been reviewed against written requirements. When the
foundation re-baseline of 25 and 26 September checked the generators against requirements, it found design defects at
circuit and part level (`v2/docs/EXECUTION-PLAN.md` section "Log"): board B's PCIe downstream and LimeSDR SuperSpeed pairs
wired transmitter to transmitter; the charger's cell-count strap selecting 2S; ten one-way clamps and rectifiers drawn
reversed; the pack gauge on the wrong land; the 5G socket keyed M; EMCON not reaching the compute modules' own radios;
and only about 145 Wh of pack fitting the case. Every routed layout therefore implements a superseded netlist
(CURRENT-EVIDENCE, candidate table), and the order set built from them is quarantined (decision 41). Clean DRC and
routed-board gates had measured the copper against the netlist they were given, not the circuit against the need.
Layer counts had been inherited from the first board rather than decided (`v2/docs/LAYER-DECISIONS-2026-09-11.md`,
opening), and readiness had been reported as percentages that mixed revisions (the 212 of 333 figure, withdrawn by the
owner's review of 26 September, section 1). The owner's first review put it plainly: "More router capacity will not
resolve those particular questions" (`v2/docs/reviews/2026-09-26-foundation-progress-review.md` section "Assessment").

**What it leaves that is useful.** The generators, the placement and escape tooling, the gate library, measured facts
about each board's routability on its stack, and the method's own lessons in the appendix. None of the layouts is a
layout candidate.

### 6.2 Board B's unrouted escapes

**What was done.** Board B (three CM5 on 0.4 mm receptacles, three PCIe switches, three USB 3 hubs, the failover muxes,
HDMI switching) was routed as B19 to B23: B21 ran about 40 hours of router and stopped at 416 open connections; B22 and
B23 tried further levers (RECORDED in `v2/ecad/tools/boards/b.json`). The placement predictor read about ten escape
collisions among 75 fine-pitch parts under every lever tried: a sixteen-rectangle resize, a fine-pitch margin, three
route methods and forty hours of router (`v2/docs/B-FEASIBILITY.md` section 3.1). On 17 September 560 fine-pitch pads
had no escape.

**Why it failed** (`v2/docs/B-FEASIBILITY.md` section 1). Three tangled causes: a floor plan that sends every slot's
high-speed traffic 85 to 90 mm away and back (receptacles at y 52.5, M.2 sockets at y 87, the slot's switch, hub and
muxes at y 137 to 157, beyond the sockets), with the switch pockets at 0.0 mm of room on three sides; an escape method
with one strategy (a surface stub to a through via outside the pad at fixed sizes), independent of layer count; and a
stack used with two good signal layers of four (inner pairs 140.5 ohm). On top of that, B21's netlist had schematic
defects in exactly those pockets (B-FEASIBILITY Appendix A), corrected since `458b2873`, which adds parts to the same
pockets (1,103 components against B21's 931). More layers alone do not remove the part measured most directly.

### 6.3 The bounded trial Q-B-ESC-1 (26 September 2026, EXPERIMENTAL, INCONCLUSIVE)

`v2/docs/B-FEASIBILITY.md` section 7.8; files in `v2/ecad/tools/routeflow/experiments/b_esc1/results/2026-09-26/`.
One region (slot 3, group S3) of the pre-correction B21 board, routed alone in two arms: A6 (F.Cu, In2, In3, B.Cu) and
A8 (plus In5, In6). Both started at 290 open. A6 was cut by its 9,000 s job cap at 33 open while still falling; A8
stopped on its plateau rule at 18 open (minimum 16). By its pre-registered table the outcome is INCONCLUSIVE.

- Nine connections in both arms could not be closed by any router in this configuration: their far pads lie inside
  another region's confinement keep-out.
- Eight of A8's nine in-region connections end at a north-row pad of the switch U301 or hub U302 that carried no
  escape on the input board; the band there is bounded by placement (INFERRED: U301's north pad tips face a 5.0 mm
  standoff pad 2.5 mm away, and four back-side capacitors sit under the tip-via line), which two more layers did not
  change. U301.124 never connected in any of 26 observed sessions.
- About 56 minutes of each arm's wall time was a modal "DSN file reader" warning, not routing; the old record that a
  first pass "takes more than four hours" cannot be read as algorithmic difficulty.
- It is not a route of the corrected board, not equal-runtime evidence, not whole-board feasibility, and it neither
  satisfies nor reopens decision 43.

**Conclusion recorded in the page:** test the escape and placement remedy on the corrected netlist (Q-B-ESC-2), not
more layers.

### 6.4 Verification-tool loops

**What happened.** From 11 September a large share of the work went into an automated control plane, a rule registry
and its checkers (`v2/docs/CONTROL-PLANE.md`, `v2/docs/AGENTIC-SYSTEM.md`, `v2/ecad/tools/pcb_rules.yaml`), built and
rebuilt while the designs they judged kept changing. Recorded instances:
- The RF-002 transmitter walk was on its tenth pass when the owner's second review noted it (review of 26 September,
  second checkpoint, section 2G); its tool `tx_inhibit.py` is still uncommitted, and RF-002's PASS on B and D comes
  from contract readings while EMCON is closed end to end for 0 of 17 transmitters.
- Four test fixtures wrote into the tree's own evidence and had to be invalidated
  (`v2/docs/evidence/INVALIDATED-2026-09-26.md`).
- Readiness aggregates mixed revisions and stages (the 212 of 333 figure).
- `jlc_certify.py` would re-certify the fourteen mismatches marked by hand (second review, section 2D item 1), and tool
  provenance hashed only the writing script, not its helpers (item 2); after code-bundle provenance (`b9600c4a`) most
  readings are AWAITING_REVALIDATION.
- Two schematic-phase rules (PWR-001, SI-001) have tools that read only a board file, so they can never be current
  before a layout exists (CURRENT-EVIDENCE section "Layout entry, per board: the exact remaining blockers").
- The EMCON page is in its sixth revision after four checker cycles (EMCON.md sections 9 to 9d), and POWER-THERMAL
  went through five checker cycles; both are useful, and both still leave their core questions open.

**Why it failed.** Author and check loops ran without a stage-appropriate criterion or a change of method after
repeated failure, and checkers were bound to artefacts (board files, older netlists) that were not the design being
decided. The owner's second review: "The remaining risk is allowing verification-tool development and procedural holds
to dominate the schedule" (section 5, closing).

**What to do instead** (EXECUTION-PLAN section "Priority from 27 September 2026 01:20 CEST: the engineering handover"; the owner's prompt, section 4): after two unsuccessful attempts
on the same issue, change method (a targeted experiment, a qualified review, or a justified alternative) or record a
blocker with its engineering question; a source-backed manual review is acceptable where the criteria allow it and is
labelled as such, never as an automated PASS; apply each check at the stage where its evidence can exist.

## 7. Useful experiments already specified, with their caps

| Experiment | Question it answers | Specification | Caps and cost | Prerequisites |
|---|---|---|---|---|
| **Q-B-ESC-2** (EXPERIMENTAL) | on the corrected netlist, with slot 3's block placed so every connected pad of U301 and U302 escapes before routing, does group S3 route to zero in-region opens on the six-layer stack with every pair on F.Cu and B.Cu? | `v2/docs/B-FEASIBILITY.md` section 7.9 | 20 passes; 9,000 s per job; import must start routing within 600 s; plateau after three sessions with no new minimum; 90 min for the first pass; whole test the smaller of 4 box-hours and 5 USD; about 3 box-hours, about 0.43 USD at 0.142 USD an hour; nothing extended when a cap fires | the post-round 8 board B netlist; a pre-route board written by B's own generators meeting three placement conditions; the router import handling of review finding F; a reviewed driver in `v2/ecad/tools/routeflow/experiments/b_esc2/` |
| **Decision 43's whole-board eight-layer run** (EXPERIMENTAL) | does board B route on eight layers at all? | `pcb_decisions.yaml` decision 43 | **no cap recorded**: record one (box-hours and USD) before it runs; outputs never adopted as a phase; when read on 21 September JLCPCB published controlled-impedance stacks for four and six layers only, so impedance cannot yet be judged on eight (`boards/b.json`) | after Q-B-ESC-2 |
| **Empty-case heat-balance test** | the sealed Peli 1450's inside-air-to-ambient conductance (lid open and closed, fans on and off) and the PA flange patch rise | `v2/docs/feasibility/POWER-THERMAL.md` section 10; `v2/docs/reviews/READY-TO-ACT.md` section 5 | case EUR 168.90 and frame EUR 29.66 excl. VAT, logger GBP 349 (all VERIFIED at the READY-TO-ACT reading); plate blank, heaters, fans, thermocouples, supply TBD; 1 to 2 days bench; runs in the same case as the mock-up, heat test first while undrilled | the owner's purchase authorisation; a person to run it (EQ-05) |
| **ZEROIZE bench Z-EXP-A, B, C** | GenKey mode 0x04 on the fitted ATECC608B-SSHDA-T after lock (A, about 2 h, three parts); power cut during GenKey 1,000 times on each of two parts (B); the panel's own wipe with power cuts (C, needs the panel firmware) | `v2/docs/feasibility/ZEROIZE.md` section 5; READY-TO-ACT section 3 | VERIFIED parts USD 8.09 + USD 2.95 + GBP 3.80, USD 58.00 more for the MikroE socket board if obtainable; DM320118 and instruments TBD | L-06 purchase; someone to wire the rig; a reachable lab host (EQ-06) |
| **EMCON early bench rows** | E-01 row 5 (the SA868 PTT pin's threshold, bare module into a dummy load); E-05 (the RM520N-GL's W_DISABLE1# on an evaluation board); E-12's early parts (T_off, T_cut, T_boot for SD-EMC-1) | `v2/docs/feasibility/EMCON.md` section 6; READY-TO-ACT section 4 | analyser EUR 159.46 excl. VAT (tinySA Ultra+) or EUR 6,509 (bench tier); module, evaluation board, SA868, SIM, RF parts TBD | the RM520N-GL and SA868 order codes pinned first; a licensed operator for the SA868; purchase authorisation. Not a layout-entry gate if SD-EMC-1's fallback (iii) is drawn in circuit |
| **F2 coupon test** | does the SCF9550-30-05 chemical fuse stay inside its rating at 18 A for 60 s from a +55 C block? | POWER-THERMAL section "11. Closed, open, and the handover"; `v2/docs/review-packets/battery/FUSE-INTERPRETATION.md` | a supply or load of at least 20 A, a temperature-controlled block, a thermocouple; part cost and time TBD | purchase; or Eaton's written answer instead (EQ-07) |
| **Case mock-up T1 to T11** | the case margins resting on Peli's unpublished tolerances, the frame seat, the jumper route, the arrestor o-ring | `v2/docs/CASE-MARGINS.md` sections 5 and 7; READY-TO-ACT section 6 | arrestors 12 x USD 78.99, monitor USD 569.00, CM5 passive cooler GBP 4.80 (VERIFIED); made parts by quote once drawn (JLCCNC from 3 business days) | the made parts' drawings (L7 action 1); purchase authorisation (EQ-08) |
| **Ethernet link test on development hardware** (optional) | does the CM5's PHY accept a capacitively coupled PHY-to-PHY gigabit link with the KSZ9897? | `v2/docs/reviews/INT-002-PRE-LAYOUT-ASSESSMENT.md` sections 5 and 7 | a CM5 IO board, a KSZ9897 evaluation board, a traffic generator; not priced | purchase; otherwise INT-003 on the built board (EQ-09) |
| Desk experiments (no cost) | impedance solves for B's A2 six-layer re-assignment and the eight-layer stack; A's 18 A copper under a 60 s transient; a lumped thermal model with sensitivities | B-FEASIBILITY sections 4 and 5; POWER-THERMAL; `v2/ecad/tools/impedance_2d.py`, `track_current.py` | none | none |

## 8. Records that disagree at `e3aedb25`, and which one to follow

**Restated at H2 (after the H2 usability check).** Every row whose State read "edit owed" or similar now ends with its
state at H2, marked **At H2**, read in the files it names at `ef144760`; a row with an earlier Superseded mark and no H2
mark is as that mark says.

| Topic | Follow | Stale or conflicting | State |
|---|---|---|---|
| Supervisor kit-bus addresses | 0x34 to 0x36 (`v2/docs/ARCHITECTURE.md` sections "1.2 Still open, and the choices the session took" and "5.5 Ethernet, display, the kit I2C bus and the supervisor fabric"; finding I3-F01: 0x30 is the TPS23861 PoE controller's broadcast address) | PANEL.md section "7. The kit I2C bus (the controller is the master; the modules read everything over USB)", ZEROIZE.md sections "2. What D-03 needs from the part, as checkable properties" and "3.1 Slot map" and "9. Recommendation (taken by the session under the owner's standing rule of 26 September 2026)", CON-020, S-41, IOHA section "6. The control plane" say 0x30 to 0x32 | propagation owed. **At H2: done.** PANEL.md section 7's table, ZEROIZE.md sections 2, 3.1 and 9 (which name 0x30 to 0x32 only as the earlier value and as addresses never to use), CON-020 and S-41 name 0x34 to 0x36, and IOHA section 6 no longer names 0x30 to 0x32 |
| Supervisor MCU | STM32H743VIT6 on PB6/PB7 (`gen_sch_b.py` lines 281 to 289; netlist U41, U51, U61) | V2-SPEC sections "Boards of this generation (as generated on 7 September 2026; the owner's layer rulings of 25 September 2026 are noted in the rows, correction 11)" and "Corrections, 26 September 2026", IOHA sections 6 and 10a, EXECUTION-PLAN section "Standing conditions (owner, 25 September 2026)" describe an H753 | the peripheral compatibility matrix (condition 1) is still owed. **At H2:** the matrix exists, `v2/docs/parts/STM32H743-COMPATIBILITY.md` (layer 6 records, `99cde56b`), and IOHA and V2-SPEC's corrections name the H743 with the H753 kept as history; EXECUTION-PLAN's condition 1 quotes the owner's standing condition and stays as written; the firmware obligations the matrix names are open item S-41 |
| Runtime | POWER-THERMAL section 0 and 6: 2.5 h (PS-IDLE-SPEC) and 1.7 h (PS-TYP) aged, bounds 1.3 to 3.3 h and 0.9 to 2.3 h, PROVISIONAL | CONOPS sections "4a. Power states" and "6. Runtime and endurance" and V2-SPEC section "Power" carry 3.4 h and 1.8 h | **Superseded after H1.1 (the release check of 27 September 2026):** CONOPS sections 4a and 6 carry PWR-F07's figures since the layer 2 merge (`95e078a1`), and V2-SPEC line 23 says so (correction 30) |
| Inside-air rise and the +35 C and +25 C restrictions | POWER-THERMAL 9.1 to 9.3: per-state bounds; the restrictions are proposed controls | OPERATING-ENVELOPE sections "3. The inside is not the outside" and "4. The envelope this proposes", `pcb_envelope.yaml` lines 33 and 36 to 38, V2-SPEC section "Thermal and environment" (10 K and 16 K; stated as design) | **Superseded after H1.1 (the release check of 27 September 2026):** OPERATING-ENVELOPE sections 3 and 4 and `pcb_envelope.yaml` carry the per-state bounds and the restrictions as controls on measured temperatures since the layer 2 merge (`95e078a1`), V2-SPEC line 73 since correction 23; the numbers still wait on EQ-05 |
| Antenna bulkheads | CASE-MARGINS C2: twelve arrestor bulkheads at Z 59 on two RF entry plates (the third 5G jack conditional) | `README.md`, `v2/README.md`, V2-SPEC section "Case and construction", `v2/BUILD.md`, `panel1450.py` lines 116 to 118, ASSEMBLY section "4. Leads" (eleven couplers at Z 88); GROUNDING-AND-SHIELDS section "What the kit is made of, which is what makes this decision what it is" (nine) | **Superseded after H1.1 (the release check of 27 September 2026):** `panel1450.py`, `case_wall_cutouts.py` and the case set `v2/release/case-2026-09-27/` carry C2 since `c351115d`, ASSEMBLY section 4 since the same commit, and both READMEs, V2-SPEC and `v2/BUILD.md` since the release check; the committed board files and the revA deliverable folders predate it |
| Face plate and connector plate | C1 (377.2 x 263.0 on ten 6-32 from above, face top 106.52) and C3 (114.0 x 68.3 x 5.0) | `panel1450.py` lines 16 to 26 (365.5 x 249.5 on M3 from below, 101.4), ASSEMBLY sections "1. Fasteners" and "4. Leads", REQ-047 ("ten M3"), `case_wall_cutouts.py` | **Superseded after H1.1 (the release check of 27 September 2026):** `panel1450.py`, `v2/cad/face_plate.py`, `case_wall_cutouts.py`, ASSEMBLY and REQ-047 (6-32) carry C1 and C3 since `c351115d`, with the made parts in `v2/release/case-2026-09-27/` |
| The pack | D-06: one 4S3P, about 145 Wh, shrink-wrapped | `v2/BUILD.md` section "2. Everything else to buy", `pcb_pack_protection.yaml` line 24, `pcb_energy_chain.yaml` lines 19, 46, 53, `pcb_board_facts.yaml` line 259 (4S4P or about 200 Wh); `gen_sch_a.py` line 1228 and `gen_sch_e.py` lines 192 to 193 (the withdrawn BB-2590/U) | edits owed; the checker inputs make BAT-001 read FAIL on P. **At H2:** the size is corrected where the checkers read it: `pcb_energy_chain.yaml`'s header states 4S3P and names its own correction (4S4P stays only as the low end of the fault-current range it derives), `pcb_pack_protection.yaml` `pack.topology` reads "4S3P Samsung INR18650-35E, about 145 Wh", and `pcb_board_facts.yaml` and `v2/BUILD.md` carry no 4S4P or 200 Wh; `gen_sch_e.py` names the BB-2590/U only in comments recording its withdrawal, while `gen_sch_a.py`'s title-block comment (its line 1614 at `ef144760`) still says "the BB-2590/U node": a text edit owed at board A's next circuit change (it re-dates A's schematic). BAT-001 still reads FAIL on P, for the next row's reason |
| Pack protection parts | board P's netlist: F2 SCF9550-30-05, U2 BQ7720700DSSR, RT1 | `pcb_pack_protection.yaml` lines 33 to 34 ("no chemical fuse, no second protector") | edit owed. **At H2: still owed:** the table's `secondary_protection` block still reads `present: false` with the older generator's words, so BAT-001 reads FAIL on P on current evidence, one of P's six layout-entry reasons (REQ-044; section 4, "At H2") |
| Storage with or without the pack | open (CFL-017): CONOPS section "4. Operating modes" and TEST-PLAN section "1. Test articles and conditions" (pack out) against REQ-025 and OPERATING-ENVELOPE section "4. The envelope this proposes" (pack fitted) | | **Superseded after H1.1 (the release check of 27 September 2026):** stored and carried with the pack fitted in the gauge's shutdown, session choice SC-19 (CONOPS section 4's Storage and Transport rows, TEST-PLAN section 1, `95e078a1`); CFL-017 stays open as BAT-F19, the margins with the pack fitted (layer 4 and the owner) |
| SIM | SC-13 (SESSION, 27 September 2026): Quectel's compatible design for USIM2 as `gen_sch_b.py` draws it, two nano-SIM holders with the second behind four 0 ohm links, so the same board builds the owner-approved eSIM-plus-nano-SIM configuration; prototype 1 is built with two nano-SIMs | V2-SPEC section "Bearers and radios" (eSIM plus nano-SIM, as the default) | **Superseded in H1:** decided by SC-13; CFL-010 stays open only for the SIM TVS array (at most 10 pF) and the eSIM variant's order code (layers 6 and 8) |
| 5G socket | key B, TE 2199119-3, since `458b2873` (V2-SPEC correction 9); the maker's two locating holes are missing (S-12) | PRODUCT-BRIEF section "What the V2 kit is" ("wrong key") | **Superseded after H1.1 (the release check of 27 September 2026):** the land carries the two locating holes since board B's round 8 (`b76c18cb`, V2-SPEC correction 28), and the brief says so since the release check |
| EMCON gaps | the compute modules' radios and the WiFi card supplies are on the line since `458b2873`; the open gap is the 5G module's supply removal, SD-EMC-1 (CONOPS section "4b. What EMCON does to each radio, as generated", PANEL section "6. Hardware lines (work with the controller dead)", V2-SPEC section "Corrections, 26 September 2026") | PRODUCT-BRIEF section "What the V2 kit is", `v2/README.md` section "V2: the Peli 1450 carrier set (MESHSAT-830 generation)" | **Superseded after H1.1 (the release check of 27 September 2026):** board B's round 8 removes the 5G module's supply by hardware at once (SD-EMC-1r8, `b76c18cb`): `feasibility/EMCON.md` section 0a reads 15 of 17 closed locally at desk and 0 of 17 end to end; the brief, both READMEs, `v2/BUILD.md`, V2-SPEC, CONOPS (4b, 4b.1, 4f, M4) and OPERATING-ENVELOPE section 4 say so since the release check |
| Q-B-ESC-1 | it ran on 26 September (B-FEASIBILITY 7.8, `4cd20d54`) | ARCHITECTURE section "15. What this page does not claim, and what is still owed"; FAILOVER-FABRIC sections 1, 8.2, 10; FEA-003's text | edit owed. **At H2:** ARCHITECTURE section 14's FB-FAB row says it ran (INCONCLUSIVE); `feasibility/FAILOVER-FABRIC.md` sections 1 and 8.2 still call it not run (edit owed, the fabric page's writer), and FEA-003 still names Q-B-ESC-1's reading where the corrected-input test is Q-B-ESC-2 (the registry writer, section 5.1) |
| Pack SMBus lead check | it exists (`check_contracts.py` lines 486 to 534, since `93138ac1`) | `pcb_interfaces.yaml` line 474, ARCHITECTURE section "12. Interface contracts" | edit owed. **At H2:** `pcb_interfaces.yaml` lists the pack SMBus lead among the checks `check_contracts.py` holds (its item 15c); `ARCHITECTURE.md` section 13.1's F-CH-04 row still says "no check judges the lead yet": edit owed there |
| Panel heartbeat source | undecided between PANEL section "3. Controller pin map (RP2040 `U3`)" (the supervisor) and ARCHITECTURE section "10.1 Who owns what" (the CM5 bridge on GPIO16) | | resolve in the hardware and firmware contract (layer 5). **At H2: resolved** in `v2/docs/HW-FW-CONTRACT.md` section 2, "The heartbeat, resolved" (merged at `0da2778b`) |
| Panel LED count | sixteen indicators D1 to D16 (PANEL section 1, the generator); the lamp test's "17" is open item S-39, and the hardware EMCON lamp (CON-021) may add one | PANEL section "9. Indicator semantics, controls and the e-paper" | **Superseded after H1.1 (the release check of 27 September 2026):** S-39 closed by SC-30; board C's round 8 draws the hardware EMCON lamp `D22`, so PANEL section 1 counts seventeen LEDs on the face and section 9's lamp test seventeen controller-lit indicators, which leave `D22` out and add the PI ring; V2-SPEC line 59 since correction 30 |
| Layout-entry blocker count | CURRENT-EVIDENCE at `b9600c4a`: 92 lines | EXECUTION-PLAN checkpoint of 26 September 20:45: 74 (before the re-classing) | none; the generated page is current. **At H2:** 40 reasons after the consolidated re-take (`8ea7867e`): A 7, B 7, C 5, D 8, E 5, P 6, E5 2 |
| Board revisions | declared phases A32, B21, C24, D12, E17, E5, P4 (`boards/*.json`) | `README.md` and `v2/README.md` revision rows (A24, B19, D11, E9); title-block labels A65, D37P, E42P | edit owed; document the label key. **At H2: done.** Both READMEs show each deliverable folder's revision (A24, B19, D11, E9) beside the declared phase (A32, B21, D12, E17) since the layer 1 closer (`2ef6aa2a`), and the glossary keys the title-block labels ("Boards, phases and labels") |
| Pack-path width at 18 A | decision 35's model: 23.91 mm at 1 oz outer, 11.95 mm at 2 oz | POWER-THERMAL section "10. Findings, the proposed experiment and prepared questions" (16.18 and 8.09 mm from IPC-2221A) | edit owed. **At H2: still owed** in POWER-THERMAL section 10, which quotes appendix 32.244's widths; section 5.2 here and the layout constraint sheets carry decision 35's 23.91 and 11.95 mm |
| Mock-up timing | before the layout entry of boards A, B, E and P, which is BLOCKED on the purchase since 27 September 2026 (FEA-007, L-07; `v2/docs/CASE-FIT-UNCERTAINTIES.md` sections 1, 2 and 7); boards C, D and E5 not held by the mock-up (**restated at H2:** FEA-007's layout-entry stage still holds D and E5 on its desk items, D on W4-F17 and E5 on the dock and blind-mate stack, and does not hold C, which it holds at fabrication release; CASE-MARGINS section 7 since the layer 7 merge; the seventh revision's "before outlines freeze" and its fabrication-release fallback are withdrawn) | none: CONOPS section "4a. Power states", READY-TO-ACT 6.1 and S-8, ARCHITECTURE section 7, the layout-constraint README, OPERATING-ENVELOPE's pack row and REQ-019 carry it since the layer 7 merge | done at the layer 7 merge |
| E5 test with a vent | no vent anywhere (appendix 32.53, REQ-020) | TEST-PLAN section "2. MIL-STD-810 methods, as applied" (CFL-008) | edit owed. **At H2: done.** TEST-PLAN's E5 reads "no vent opening" and E8 names Peli's pressure valve (corrected 27 September 2026, CFL-008) |
| Resolved conflicts that still fail | CFL-006, CFL-009, CFL-007 read CONFLICT_RESOLVED but their sources still contradict | | make the sources true (layer 3 action 6). **At H2:** read in the sources each names, they now agree: CFL-006's pack headers name 4S3P, about 145 Wh; CFL-007's TEST-PLAN limits are D-02a's qualification margins (E3-S, E3-A, E4-S); CFL-009's closed-lid state is tested by TEST-PLAN's E3-L. A reading here, not a review |
| Stackup records | decisions 27, 28, 43 | `v2/docs/LAYER-DECISIONS-2026-09-11.md`; `boards/a.json` and `boards/c.json` rationales; STK-002's "an owner decision is open" | edit owed. **At H2: still owed:** LAYER-DECISIONS predates decisions 27, 28 and 43, and STK-002 still reads INCONCLUSIVE with "an owner decision is open" on B, C and D (`PCB-RULE-STATUS-B.md`, `-C.md`, `-D.md`); follow the decisions (section 5.2) |
| Board C Q2 to Q4 | 2N7002 C8545, CERTIFIED in `JLC-CERTIFIED.tsv` (the committed netlist) | a WRONG_MODEL row for an "Si1308EDL class" switch in the same table dates from a board C generator before 12 September and does not apply | none for the design; the stale row can be dropped at the next certification |
| Publication of board E's files | decision 31's hold on E forbids "any publication of the board file or its evidence" (`pcb_board_holds.yaml` line 160) | the repository is public on its GitHub mirror (REVIEW-ROUTES section "How the owner would engage a reviewer (every route)") | publication is the owner's to decide |

## 9. What this brief does not settle

It rules nothing. Every recommendation above is the session's, not the owner's. A closer who takes an engineering
choice records it in `v2/ecad/tools/pcb_requirements.yaml` `session_choices` in the SC-nn form (question, taken, why,
"Reverse by ...") or in `pcb_decisions.yaml` with `authority` and `reversed_by`, and never lowers a requirement, drops a
function, weakens protection or narrows scope to close an item.
