# MeshSat field kit V2: start here

**Engineering handover, first and partial edition.** Written 27 September 2026 from the repository at commit
`e3aedb25` (`e3aedb25c849dbda931888b27093ac6c444621cb`, 27 September 2026 01:17 CEST), under tracker issue
MESHSAT-1357. Every path below is a path in this repository at that commit, written from the repository root. When
you read this page inside a handover snapshot (`v2/release/handover/<version>/`), the snapshot keeps every file under
the same path and its manifest names the commit, each file's revision and each file's sha256.

**Prototype framing.** The MeshSat field kit V2 is an unbuilt prototype design. No V2 board has been fabricated,
ordered, assembled, powered or measured, and no kit has been deployed. Every number in this handover is a design
figure, a datasheet figure or a desk calculation unless a page says otherwise. Every review of the current design so
far was done by AI agent sessions (an author and a separate refuting checker), and each such review is labelled as an
AI review; none of it is electrical sign-off (`v2/docs/reviews/REVIEW-ROUTES.md`, opening paragraphs).

**What this edition is.** The owner asked for the pre-PCB work to be transferable to an outside engineer or company
even if PCB layout stalls (`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`). **This is handover H1, the first
snapshot, and it is partial: no layer is COMPLETE**, and the pages say exactly what each layer still lacks. It is a
usable map of an unfinished design, not a claim that the engineering is done. The four pages were written from the
audit at `e3aedb25` and brought to the H1 source commit by the handover's integrator: section 3a below, LAYER-STATUS's
"Status at handover H1" and each layer's `INTEGRATOR LINE`, CONTINUATION-BRIEF section 0 and ENGINEERING-QUESTIONS
EQ-15 to EQ-21 carry what changed; the rest of each page is the `e3aedb25` record they build on. The snapshot's
`SOURCE.txt` names the one commit every file of it comes from.

## 1. The five handover pages

| Page | Read it for |
|---|---|
| `v2/docs/handover/START-HERE.md` (this page) | what is being built, how the repository is organised, the reading order, what you need outside the repository |
| `v2/docs/handover/LAYER-STATUS.md` | the nine pre-PCB layers: scope, deliverables by revision, every acceptance item met or not with its evidence, unresolved decisions, gate cycles, the next closing actions, per-board lines |
| `v2/docs/handover/CONTINUATION-BRIEF.md` | the decisions an incoming PCB engineer must preserve, the remaining work in dependency order, the constraints known today, the approaches that failed and why, the experiments already specified |
| `v2/docs/handover/ENGINEERING-QUESTIONS.md` | every blocked question, one compact block each: issue, evidence, attempts, options, recommendation, expertise, cost and lead time |
| `v2/docs/handover/REGENERATE.md` | how to regenerate the schematics and re-run the checks, and which host each step needs (written separately from these four pages) |

## 2. What is being built, and for whom

**The problem** (`v2/docs/PRODUCT-BRIEF.md`, "The problem"). When the internet and the cellular network are down or
absent, people nearby can still talk over local off-grid networks (Meshtastic LoRa handhelds, Zigbee and Thread
devices, WiFi), but their messages cannot leave the area. MeshSat's software (the MeshSat Bridge, in the separate
repository `github.com/meshsat/meshsat`) takes a message off a local network and routes it out over whichever
long-range bearer is still up, preferring free bearers to metered ones. The V2 field kit is the hardware that carries
that software into the field.

**Who it is for** (`v2/docs/PRODUCT-BRIEF.md`, "Who it is for"; `v2/docs/CONOPS.md` section 1). A non-commercial
prototype, operated in the Netherlands and the EU by a licensed radio amateur (owner ruling D-04). No CE or RED
conformity marking and no EMC claim is made for it; the design keeps a route to the EU market open. No target
organisation is named. The roles the design implies are the kit operator, a second crew member on a second headset,
local end users with their own devices and a lid tablet, and remote correspondents reached over Iridium, cellular,
HF, VHF APRS or a second kit.

**What the kit is** (`v2/docs/PRODUCT-BRIEF.md`, "What the V2 kit is"; `v2/docs/V2-SPEC.md`). A sealed Peli 1450 case
with a 3 mm aluminium face plate in the 1450PF panel frame, holding seven carrier boards and a pack built for the kit:

| Board | Role | Project directory | Declared phase |
|---|---|---|---|
| A, power and I/O | the 4S pack node, SMBus charger, slot and device rails, the PA and HF rails, PoE and USB-C outlets, the RF blind-mate sites, the dock contacts | `v2/ecad/pcb-a-power-a23/` | A32 |
| B, compute | three Raspberry Pi Compute Module 5 slots, each with a PCIe switch, NVMe and card slot and a USB 3 hub; the hub-bank failover fabric under three voting STM32H743 supervisors; Ethernet switch with PoE; HDMI switching; the radios (5G, Iridium, LoRa, Zigbee and Thread, GNSS, SDR, WiFi link cards); the secure element | `v2/ecad/pcb-b-compute-b19/` | B21 |
| C, panel backer | the RP2040 panel controller under the face (hardware EMCON and ZEROIZE lines, indicators, e-paper) | `v2/ecad/pcb-c-display-c8/` | C24 |
| D, VHF APRS | the SA868 exciter, the 30 W amplifier's control, the audio path for two headsets | `v2/ecad/pcb-d-aprs-d9/` | D12 |
| E (E1), dock strip | the 9 to 36 V vehicle and shore front end, the solar tracker, the pack entry, the sensor controller | `v2/ecad/pcb-e1-dock-e7/` | E17 |
| E5, dock block | the raised contact block the stack lands on (no schematic by construction) | `v2/ecad/pcb-e5-block/` | E5 |
| P, pack BMS | the BQ4050 gauge and protection, a second-level protector and a chemical fuse inside the pack | `v2/ecad/pcb-p-pack-p2/` | P4 |

The pack is one 4S3P block of Samsung INR18650-35E cells, about 145 Wh, shrink-wrapped in the case's east pocket
(owner ruling D-06). The project directory names (`-a23`, `-b19`, ...) are historical; the declared phase in
`v2/ecad/tools/boards/<x>.json` is the one every current page uses. Three committed schematics also print a different
title-block label (A65, D37P, E42P); see LAYER-STATUS layer 8.

**What prototype 1 is accepted against** (owner ruling D-01, `v2/docs/CONOPS.md` section 2a). Full design, staged
acceptance: every ruled function stays designed and fitted where copper exists; prototype 1 is accepted on a named
core, which is messaging over Iridium, 5G, LoRa and APRS, the three-slot failover fabric, pack, vehicle and solar
charging, hardware EMCON, ZEROIZE of the secure element, pack safety, service and programming access, and SOS (added
by the session under the owner's standing rule, SC-01). Everything else (Geiger counter, lightning detector, DCF77,
outside sensor pod, camera, net audio recording, tablet bracket, the NVG claim, HF, a second pack) is built where
possible and reported NOT_YET_TESTED, never as a pass. Two bearers, LoRa and cellular data, are named exceptions to
the compute-redundancy need NEED-03 for prototype 1 (SC-02); that is a scope exception, not settled design, and
reversing it reopens board B's floor plan.

**Operating conditions** (`v2/docs/OPERATING-ENVELOPE.md`, decision 34 and owner rulings D-02a to D-02e):
-20 to +40 C in use, -20 to +45 C in storage, with TEST-PLAN's +55 C operation, +71 C and -33 C storage as
qualification margins judged "survive and recover"; operated shaded; no cold start from a pack below about -10 C at
the cells; a closed-lid reduced mode (still to be defined, LAYER-STATUS layer 2). The hot end is not established: the
sealed case's heat path is known only as a bound that includes failure (ENGINEERING-QUESTIONS EQ-05).

**What it is not, today** (`v2/docs/PRODUCT-BRIEF.md`, "What it is not, today"): not built, powered or measured; not
rated (Peli's case is IP67, the face is designed to an IP67-class construction and carries no rating); not certified
and no certification claimed; no vehicle surge claim (D-16); no finished runtime figure.

## 3. Where the design stands at `e3aedb25`

- **Headline** (`v2/docs/CURRENT-EVIDENCE.md` line 6, generated): foundations incomplete; 0 boards ready for layout;
  0 physically verified. The computed layout-entry test lists 92 blocker lines across the seven boards (A 16, B 16,
  C 10, D 15, E 15, P 14, E5 6). An older figure of 74 in `v2/docs/EXECUTION-PLAN.md` (checkpoint of 26 September
  20:45) predates the re-classing at `b9600c4a`; CURRENT-EVIDENCE is the current count. Historical aggregate
  percentages that appear in older pages mix revisions and are not readiness.
- **Layers.** All nine pre-PCB layers are IN_PROGRESS; none is BLOCKED as a whole and none is COMPLETE. The earliest
  three (product, concept of operations, requirements) can close with desk work under existing authority; layers 4
  to 9 each contain items that need a purchase, a bench, an outside reviewer or an outside answer. Details:
  `v2/docs/handover/LAYER-STATUS.md`.
- **Milestones.** `v2/docs/EXECUTION-PLAN.md` lines 65 to 71 list FOUNDATIONS_BASELINED, DESIGN_READY_FOR_LAYOUT
  (per board), DESIGN_PACKAGE_READY_FOR_PROTOTYPE, PROTOTYPE_FAB_RELEASED, PROTOTYPE_VERIFIED and
  PRODUCTION_RELEASE_READY. None is reached. FOUNDATIONS_BASELINED keeps its recorded scope (the product definition,
  the requirements with their verification method, the architecture and budgets, the interface contracts and the
  review of parts and circuits, `v2/docs/EXECUTION-PLAN.md` line 3, gated by Reviews A to D, lines 58 to 63); it is
  not used here, or anywhere, to imply that all nine layers or a fabrication package are complete.
- **Circuit work in flight.** A round of circuit corrections on every board ("round 8") and several tool changes were
  being authored in parallel branches when this edition was written. They are not in `e3aedb25` and nothing on these
  pages counts them. LAYER-STATUS carries one marked line per layer for the integrator to update as they land.
- **Layout.** Every committed board layout predates its corrected netlist (CURRENT-EVIDENCE.md, "The candidate each
  board is judged against": SCH-002 FAIL on A and B, INCONCLUSIVE on C, D, E and P). The three-module board B has
  never been routed to completion (B12 to B15 were an earlier single-module generation). The order folder is rebuilt and quarantined (decision 41): nothing is to be ordered from it.

## 3a. Where the design stands in H1

- **Source.** Main `84e52461` (circuit round 8, sets 1 and 2: boards A, C, D, E and P regenerated with parity; the
  netlist checks PWR-001, SI-001 and RF-002; the pack's temperature ladder) plus the handover branch: the layer 1, 4,
  6 and 9 closers' work (product brief through Review A's second pass, readable diagrams, part records, layout
  constraint sheets and the stackup record), the packer, the exports, these pages. Last design change `99cde56b`.
- **Headline** (`v2/docs/CURRENT-EVIDENCE.md`, generated): foundations incomplete; 0 boards ready for layout; 0
  physically verified. Layout-entry reasons A 17, B 16, C 11, D 15, E 16, P 15, E5 5.
- **Layers.** All nine are IN_PROGRESS; none is COMPLETE and none is BLOCKED as a whole. Layer 1 is the nearest: its
  review (an AI review) has no blocking finding and it waits on layer 2's EMCON and face text. LAYER-STATUS says what
  remains per layer, and which closers' work is a candidate in a worktree rather than in H1.
- **Board B's round 8 is not in H1** (EQ-20); every other board carries its round 8 netlist.
- **Readable exports.** `v2/release/handover/_generated/<board>/`: an A3-paged schematic PDF, two BOMs named
  NOT_FOR_FAB, the ERC report, the netlist's parity with its schematic and `provenance.json`, for all six boards with a
  schematic, made at `99cde56b` on KiCad 9.0.9; regeneration from a clean extraction read PARITY on all six.
- **Diagrams** (`v2/docs/diagrams/`) were drawn at `e3aedb25`, before round 8; their README says what that means.
- **Known gaps of H1.** (1) The readings behind `CURRENT-EVIDENCE.md` and `PCB-RULE-STATUS-*.md` live in the
  gitignored `v2/ecad/out/` and each board's `out/` folder and are not in the snapshot; the rendered pages are, so a
  recipient re-takes a reading rather than reading it back. (2) The test suite needs a git checkout of the repository
  for `test_netlist_provenance` and for the registry's closed-by-commit checks; from the ZIP alone those fail
  (REGENERATE.md section 7). (3) The ZIP is deterministic per host: two builds of one commit on one host are byte for
  byte equal, on another host compare `MANIFEST.tsv`, not the ZIP's sha256. (4) Maker documents are referenced by
  sha256, not bundled, except the eight the energy chain cites and seven the requirements registry cites (`pack.yaml`);
  CON-017's three ST documents (about 21 MB compressed) stay referenced under the 50 MB cap, so the registry validates
  from the ZIP only once `v2/vendor/st/` is restored from the repository.

## 4. How the repository is organised (only what a newcomer needs)

| Path | What it holds | Authority |
|---|---|---|
| `README.md`, `v2/README.md` | public overviews | public text; parts of both are stale at `e3aedb25` (LAYER-STATUS layer 1 lists the lines) |
| `v1/` | the two V1 kits as built (tesseract, parallax) | out of scope for this handover |
| `v2/docs/` | the engineering documents: product brief, concept of operations, envelope, specification, architecture, interfaces summary, panel contract, assembly, case margins, test plan, execution plan | the editable working documents are the authority; a snapshot is an immutable copy |
| `v2/docs/feasibility/` | the six architecture feasibility studies' pages: ZEROIZE, EMCON, FAILOVER-FABRIC, POWER-THERMAL, DECOUPLING (battery: `v2/docs/review-packets/battery/`), plus `fab/` scripts | desk studies, labelled PROVISIONAL or with evidence labels |
| `v2/docs/reviews/` | the owner's reviews of 26 September and his execution prompt of 27 September (verbatim), the review routes, the costed ready-to-act packet, the INT-002 assessment | the owner's reviews govern execution |
| `v2/docs/records/` | session records that committed pages cite (scripts, outputs, decision logs), filed byte for byte with sha256 (`v2/docs/records/README.md`) | records, not tools and not authorities |
| `v2/docs/review-packets/battery/` | the packet for the qualified battery review R-BAT, with its manifest check | review input |
| `v2/docs/MESHSAT-709-geometry-appendix.md` | the design record, about 19,000 lines of dated entries (rulings, measurements, audit rounds) | history; use it only to trace a ruling another page cites |
| `v2/ecad/tools/pcb_requirements.yaml` | the requirements registry: 19 needs, 132 records (REQ, CON, ASM, CHO, SPD, CFL, FEA), 28 owner rulings, 11 session choices, 35 open and 38 closed items | the single authority for requirements; `v2/docs/REQUIREMENTS-TRACE.md` is its generated view |
| `v2/ecad/tools/pcb_decisions.yaml`, `pcb_rules.yaml`, `pcb_interfaces.yaml`, `pcb_envelope.yaml`, `pcb_board_holds.yaml`, `pcb_energy_chain.yaml`, `pcb_pack_protection.yaml`, `pcb_part_temps.yaml`, `reserved.json` | the decision, rule, interface, envelope, hold, energy-chain, pack-protection and part-temperature registries | machine-read authorities for the tools; some are stale at `e3aedb25` (LAYER-STATUS says which) |
| `v2/ecad/tools/gen_sch_<x>.py`, `boards/<x>.json`, `kisch.py`, `intent.py`, `schlayout.py`, `gen_footprints_*.py`, `v2/ecad/meshsat.pretty/` | the schematic generators and their shared inputs: the boards are generated by scripts, not drawn | the source of truth for each circuit |
| `v2/ecad/pcb-*/` | per board: the generated `.kicad_sch`, the committed netlist `out/<board>.net` with its provenance sidecar `.net.prov.json` and intent file `-intent.json`, allow lists; also the historical layouts | schematic and netlist current; layouts historical |
| `v2/ecad/tools/` (the rest) | the checking tools, the pipeline and its tests (`tests/run.py`) | tools; a tool's verdict is evidence only when bound to the current candidate |
| `v2/vendor/` | makers' documents and CAD, with `SOURCES.yaml` (identity, revision, source and sha256 per critical part), `sources.txt`, `vendor-status.txt`, `open-picks.txt` | reference material under the makers' own terms; a held document does not validate a part |
| `v2/cad/` | CAD generators of the made parts (face plate, pack box, lid tray, float clamp) and the render scene | predates the current case choices (LAYER-STATUS layer 7) |
| `v2/release/revA/` | deliverable folders, review prints and case templates of earlier layout phases, and the order set | historical; the order set was rebuilt and quarantined (decision 41), and nothing is to be ordered from it |
| `v2/release/review-packets/` | review packets of boards C, D, E and P at `1f614233`; D and P superseded, C and E to be rebuilt (`v2/release/review-packets/README.md`) | review input, with the README's labels |

**Generated pages: never hand-edit.** `v2/docs/CURRENT-EVIDENCE.md`, `v2/docs/PCB-RULE-STATUS-*.md`,
`v2/docs/REQUIREMENTS-TRACE.md`, `v2/docs/OWNER-DECISIONS-OPEN.md`, `v2/docs/PCB-OPEN-PAIRS.md` and
`v2/docs/PCB-GOLDEN-RULES.md` are rendered from the registries; each carries its renderer's name in its first lines,
and the renderer's `--check` refuses a hand-edited copy.

**Evidence labels used across the pages.** VERIFIED (read in the artefact cited), RECORDED (a measurement written
into a registry whose run is not in the tree), INFERRED (reasoned from verified facts, and says how), TBD (no source;
the effect of not knowing is stated), PROVISIONAL (arithmetic over declarations and datasheets, nothing measured).

**Who decided what.** Every decision carries its authority. OWNER means the project owner ruled it (the rulings of
25 and 26 September are in `v2/docs/CONOPS.md` section 7, `pcb_requirements.yaml` `owner_rulings`, and
`pcb_decisions.yaml` with `authority: OWNER`). SESSION means the design session took it, either under the owner's
ruling of 21 September 2026 that engineering decisions are the session's (appendix 32.362 onward; summarised in
`v2/docs/PRODUCT-BRIEF.md` lines 101 to 110) or under his standing rule of 26 September 2026 (`pcb_requirements.yaml`
`owner_rulings` entry `standing-rule`): where a choice is left, the session takes the option the evidence recommends
and records it with its reason and how to reverse it (`session_choices` SC-01 to SC-11). Money, outside contact,
publication and promotion stay with the owner. A new team taking over should state its own authority model; every
SESSION choice names how to reverse it.

## 5. Reading order through the nine layers

Read in order; each layer's authoritative files first, then its status in LAYER-STATUS.

| Layer | Authoritative files (read first) | Supporting |
|---|---|---|
| 1. Product definition | `v2/docs/PRODUCT-BRIEF.md` | `v2/docs/V2-SPEC.md` (the device set with dated corrections 1 to 19), `pcb_requirements.yaml` `owner_rulings` |
| 2. Concept of operations | `v2/docs/CONOPS.md` (needs NEED-01 to NEED-19, missions, modes, power states, rulings), `v2/docs/OPERATING-ENVELOPE.md`, `v2/ecad/tools/pcb_envelope.yaml` | `v2/docs/PANEL.md` (operator-facing behaviour), `v2/docs/TEST-PLAN.md` (envelope limits) |
| 3. Requirements | `v2/ecad/tools/pcb_requirements.yaml`, its generated view `v2/docs/REQUIREMENTS-TRACE.md` | `v2/ecad/tools/rules_lib.py` (the validator), `v2/ecad/tools/pcb_rules.yaml` (the board rules records name) |
| 4. System architecture | `v2/docs/ARCHITECTURE.md` (sections 14 and 15 first: the feasibility blockers and the stale siblings) | `v2/docs/feasibility/*.md`, `v2/docs/B-FEASIBILITY.md`, `v2/docs/ARCH-PCB-B-IOHA.md`, `v2/docs/review-packets/battery/` |
| 5. Partitioning and interfaces | `v2/ecad/tools/pcb_interfaces.yaml` (`board_to_board`), `v2/docs/ARCHITECTURE.md` sections 3, 10 and 12 | `v2/docs/PANEL.md`, `v2/docs/ASSEMBLY.md` section 4, `v2/docs/GROUNDING-AND-SHIELDS.md`, `v2/ecad/tools/check_contracts.py` |
| 6. Components | `v2/vendor/SOURCES.yaml` (read each entry's update blocks, not only its top-level fields), `v2/release/revA/order/JLC-CERTIFIED.tsv` | `v2/docs/evidence/WRONG-MODEL-RECONCILIATION.md`, `v2/ecad/tools/pcb_part_temps.yaml`, `v2/vendor/open-picks.txt` |
| 7. Mechanical and enclosure | `v2/docs/CASE-MARGINS.md` (sections 4 and 7), `v2/vendor/peli/frame_seat.py` and its output | `v2/vendor/peli/1450/` (Peli STEP, DXF, drawing), `v2/docs/ARCHITECTURE.md` sections 7 to 9 and 11, `v2/docs/ASSEMBLY.md` |
| 8. Schematics | per board: `v2/ecad/pcb-*/pcb-*.kicad_sch` and `out/*.net`, generated by `v2/ecad/tools/gen_sch_<x>.py` | `v2/docs/CURRENT-EVIDENCE.md`, `v2/docs/PCB-RULE-STATUS-<x>.md`, `v2/docs/records/r4a`, `r4b`, `r4e`, `r4p`, `r6d` |
| 9. Pre-layout design analysis | `v2/docs/feasibility/POWER-THERMAL.md` and `v2/docs/records/rv-pwr/pwr_budget.py`, `v2/docs/feasibility/DECOUPLING.md`, `v2/docs/B-FEASIBILITY.md`, `v2/docs/reviews/INT-002-PRE-LAYOUT-ASSESSMENT.md` | `v2/docs/LAYER-DECISIONS-2026-09-11.md` (stale on B, C and P), `v2/ecad/tools/stackup_write.py`, `v2/vendor/fabricator/` |

Then read `v2/docs/EXECUTION-PLAN.md` (the seven standing conditions, lines 90 to 98, and the stage gates, lines 100
to 131), the owner's two reviews of 26 September in `v2/docs/reviews/`, and `v2/docs/reviews/READY-TO-ACT.md` (the
costed external and bench work).

## 6. Regenerating and verifying

The full instructions are `v2/docs/handover/REGENERATE.md`. In short:

- **Runs anywhere with Python 3.11 and PyYAML 6, no KiCad** (each re-run on a plain export of `e3aedb25` by the layer
  audit behind these pages; the validator's figures are H1's): `python3 v2/ecad/tools/rules_lib.py requirements` (the requirements validator: 132
  records, 0 errors in a checkout; from the H1 ZIP alone 4 errors and 16 warnings: the errors are CON-017's three ST
  documents, referenced rather than bundled for size, and the warnings are closed-by-commit checks that need git
  history and the gitignored readings; REGENERATE.md section 7); `python3 v2/ecad/tools/rules_render.py --requirements --check` (the trace is current); the case
  margin scripts `v2/vendor/peli/frame_seat.py` and `v2/vendor/peli/case_margins.py` (outputs byte-identical to
  `v2/vendor/peli/1450/*.out`); the power model `v2/docs/records/rv-pwr/pwr_budget.py` (output byte-identical to
  `pwr_budget.json`); `v2/docs/review-packets/battery/evidence/check_manifest.py` (RELEASE CHECK PASS);
  `v2/ecad/tools/check_contracts.py` on the committed netlists, with `VERDICT_DIR` pointed outside the tree (PASS 96
  of 96 cross-board checks; they judge pin-map identity and presence, not currents, levels, timing or mating).
- **Needs a KiCad 9.0.9 host:** schematic regeneration and parity (`gen_sch_<x>.py`, `build_sch.sh`,
  `regen_compare.py`), ERC (`erc_gate.py --run`), paged PDFs and BOMs, every tool that reads a board file, review
  packets (`review_packet.py`), and the E5 contract (`block_contract.py`).
- **Never run a gate inside your working tree without an output directory.** A verdict goes to `out/` under the
  process's working directory unless `VERDICT_DIR` is set (`v2/ecad/tools/verdict.py`, `write()`); four test
  fixtures once wrote into this tree's own evidence and had to be invalidated
  (`v2/docs/evidence/INVALIDATED-2026-09-26.md`). Set `VERDICT_DIR` (or the tool's `--out-dir`) to a scratch folder.
- **Regeneration parity is shown, not asserted** (standing condition 5): regenerate, then compare with
  `regen_compare.py` against the committed netlist sha in each board's `.net.prov.json`.

## 7. What is excluded, and why

The repository at `e3aedb25` is the whole design record; a snapshot bundles the engineering files and lists what it
leaves out. What a reader will not find, or should not use:

| Excluded or not usable | Why | Where the fact lives instead |
|---|---|---|
| The V1 kits (`v1/`) | built, separate from V2, out of this handover's scope | `v1/README.md` |
| Committed board layouts, their verdicts, DRC reports, Gerbers, order folders, deliverable folders under `v2/release/revA/`, EasyEDA conversions | every layout predates its corrected netlist; the order set is quarantined (decision 41); `v2/BUILD.md` is the 7 September ordering guide and is not to be used for ordering | `v2/docs/CURRENT-EVIDENCE.md` (candidate table) |
| Review packets D-D12 and P-P4 at `1f614233` | superseded (`v2/release/review-packets/README.md`) | the battery packet `v2/docs/review-packets/battery/` for P |
| Concept renders and board images | presentation, not engineering input; the renders show the 7 September arrangement | `v2/docs/CASE-MARGINS.md` for the current arrangement |
| Schematic-phase readings that the status pages render | they sit in gitignored `out/` folders on the build host (`.gitignore`); the committed `routed/*.verdict.json` are 21 September readings of older netlists | CURRENT-EVIDENCE.md classes every reading; a consolidated re-take is a closing action |
| Q-B-ESC-1's final boards, DRC reports and 26 per-pass sessions | kept on the rented build host and in a session record outside the tree, named only by sha256 | `v2/ecad/tools/routeflow/experiments/b_esc1/results/2026-09-26/README.md`, `v2/docs/B-FEASIBILITY.md` section 7.8 |
| Round 8 circuit drafts, W1, W3, W5 and W7 workstream drafts, adjudications A01 to A11, board A's converter calculation scripts, the RF-002 walk tool `tx_inhibit.py`, the mismatch input `jlc-mismatch.yaml` | uncommitted session worktree drafts at `e3aedb25`; committed pages cite some of them (LAYER-STATUS lists each gap). In H1: round 8 of boards A, C, D, E and P, `tx_inhibit.py`, `jlc-mismatch.yaml`, W1's records (`v2/docs/records/w1/`) and the adjudications (`v2/docs/records/adj/`) are committed; board B's round 8 and the W3, W5 and W7 drafts are not | filing the rest is a closing action; until then, the citing page's own summary |
| The session's chat, memory and local instruction files | never part of the design record by rule | the rulings they carried are in the registries; gaps are named in LAYER-STATUS |
| The issue tracker (MESHSAT-nnn ids) and the MeshSat Bridge software | outside this repository; `v2/docs/PANEL.md` is the only software contract held here, and the panel's wire format is deferred to MESHSAT-837 | `github.com/meshsat/meshsat` for the Bridge |
| Maker documents in a snapshot | cited by path and sha256, not bundled for size | `v2/vendor/SOURCES.yaml` and the repository at the snapshot commit |

## 8. What you need from outside the repository

| Need | Used for | Notes |
|---|---|---|
| KiCad 9.0.9 with its standard libraries and `kicad-packages3d`, `kicad-cli`, `pcbnew` importable from Python 3 | schematic regeneration, ERC, PDFs, BOMs, every board-file tool | the generators and the parity baselines were produced with 9.0.9 (`v2/README.md` line 48; `v2/ecad/tools/netlist_parts.py` line 7); `pin_map_lands.py` also reads the host's KiCad footprint library |
| `mupdf-tools` | paged schematic PDFs (`build_sch.sh`) | |
| Python 3.11 with PyYAML 6; `numpy`, `scipy` | validators, renderers, analysis tools | the stdlib-only scripts of section 6 need nothing else |
| Java, Xvfb and the Freerouting 1.9.0 per-pass build | routing experiments only (Q-B-ESC-2, decision 43's run) | built from source by `v2/ecad/tools/routeflow/cloud/onstart.sh`; the stock jar is refused (`v2/README.md` line 48) |
| `build123d` (with OCP), `ezdxf`, `matplotlib` | the CAD generators under `v2/cad/` and the Peli STEP and DXF readers | versions are not pinned in the repository (a gap, LAYER-STATUS layer 7) |
| Blender 4.2 on a GPU host | concept renders only | presentation; not needed for engineering |
| JLCPCB's public parts API (`https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`, `v2/ecad/tools/jlc_certify.py` line 66) | part identity and stock readings (`jlc_certify.py`, `lcsc_fill.py`) | network access, no login; every reading is dated and true only at its time; the certify cache is not in the repository |
| A fabricator quote per board and layer count | the stackup price decision (STK-002, decisions 27 and 43) | JLCPCB publishes no PCB price endpoint; a quote needs an account session (EQ-14) |
| Makers' documents | part identity, ratings, lands | held under `v2/vendor/` with sha256 in `SOURCES.yaml`, `sources.txt` and `vendor-status.txt`; several vendor sites refuse automated clients, so some copies are Internet Archive captures, which `sources.txt` says |
| Documents the repository does not hold | named where they are needed | Microchip's full ATECC608B data sheet (NDA); Broadcom BCM54210PE (not published); the Mill-Max 0858 data sheet (only its product page and catalogue page 28 are held); binder M8 sheet; RG-316 sheet; MIL-STD-810 (only a transcription of Method 516.8, Table 516.8-IX, is held) and MIL-STD-461; the ADR text for the pack's classification; USB 3, PCIe CEM and HDMI channel specifications; the Xenarc 709GNK body drawing; a Raspberry Pi CM5 cooler drawing; Delta's 40 mm IP68 fan drawing |

## 9. Conventions of these pages

- No completion percentages. A layer is COMPLETE only when every acceptance item is met with its review; otherwise its
  remaining items are listed.
- A desk review, an AI review, clean ERC or passing software fixtures do not establish that a circuit is correct, and
  a desk review is never a physical test.
- Where the records disagree at `e3aedb25`, CONTINUATION-BRIEF section 8 says which one to follow; for what changed
  since, section 0 of the same brief is the newer.
- Where these pages recommend an option, it is a recommendation. A closer who takes an engineering choice records it
  in `pcb_requirements.yaml` `session_choices` in the SC-nn form (the question, what was taken, why, and "Reverse by
  ..."), never as the owner's.
