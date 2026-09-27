# MeshSat field kit V2: start here

**Engineering handover, edition H3, partial.** First written 27 September 2026 from the repository at commit
`e3aedb25` (`e3aedb25c849dbda931888b27093ac6c444621cb`, 27 September 2026 01:17 CEST), under tracker issue
MESHSAT-1357, brought to H2 the same day and to H3 after it; section 1a is H3's, and section 3 is H2's, whose design
H3 keeps. Every path below is a path in this repository,
written from the repository root. When you read this page inside a handover snapshot (the `<version>/` folder of
`v2/release/handover/<version>.zip`; H1 was also committed unzipped, H1.1, H2 and H3 only as the ZIP with its manifest
beside it), the snapshot keeps every file under the same path and its manifest names the commit, each file's revision
and each file's sha256.

**Prototype framing.** The MeshSat field kit V2 is an unbuilt prototype design. No V2 board has been fabricated,
ordered, assembled, powered or measured, and no kit has been deployed. Every number in this handover is a design
figure, a datasheet figure or a desk calculation unless a page says otherwise. Every review of the current design so
far was done by AI agent sessions (an author and a separate refuting checker), and each such review is labelled as an
AI review; none of it is electrical sign-off (`v2/docs/reviews/REVIEW-ROUTES.md`, opening paragraphs).

**What this edition is.** The owner asked for the pre-PCB work to be transferable to an outside engineer or company
even if PCB layout stalls (`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`). **This is handover H3, the
fourth snapshot (after H1, H1.1 and H2), and it is partial: layers 1 (product definition), 2 (concept of operations)
and 3 (requirements) are COMPLETE for their own engineering purpose, with their review records; layers 4 to 9 are
IN_PROGRESS**, and the pages say exactly what each still lacks. COMPLETE never means a physical test has passed:
nothing is built. H3 is a usable map of a design whose first three layers are released and whose other six are not,
not a claim that the engineering is done. **H3's design content is H2's:** no schematic, netlist, generator or
checking tool changed between them (section 1a). The pages were written from the audit at `e3aedb25` and brought
forward edition by edition: section 1a below, LAYER-STATUS's "Status at handover H3" and `RELEASE-H3.md` carry H3;
section 3 below, LAYER-STATUS's "Status at handover H2" and the **H2** step of each layer's `INTEGRATOR LINE`,
CONTINUATION-BRIEF section 0 and the ENGINEERING-QUESTIONS index carry H2, corrected where a sentence is marked
**H3**; the H1 sections (3a here, "Status at handover H1" there, the brief's section 0a) and the `e3aedb25` record
are kept as history beneath them. The snapshot's `SOURCE.txt` names the one commit every file of it comes from.

**Which commit is which.** Four commits anchor these pages: `e3aedb25` (27 September 2026 01:17 CEST), the audit the
pages were first written from; main `84e52461` plus the handover branch, whose last design change is `99cde56b`, the
design H1 carries; main `62f26a44` plus branch `fnd/h2`, whose last design change is `b7f96784`, the design H2 carries
and H3 keeps (H2's source commit is `b89b50b4`; H3 is cut from main `6ec37197` plus the branch that carries these
pages); and the build commit that `SOURCE.txt` names, the commit every file of a snapshot is copied from.
`SOURCE.txt` also carries a generated commit timeline: every commit id these pages name, with its date, its subject,
whether it is in the snapshot's history and whether it was on the public repository
(`https://github.com/meshsat/meshsat-fieldkit`) when the snapshot was built. The snapshot carries no git history, so
use that table (or a clone of the public repository) to place a commit id.

**Edition H1.1** (27 September 2026) answers the usability check of H1 (two blocking and thirteen minor findings): the
unpushed candidates are bundled as patches (`v2/docs/handover/candidates/`), the re-take of the schematic-phase
readings has a stated procedure (REGENERATE.md), the vendor files some checks need have a fetch route (REGENERATE.md
section 1a), and a glossary is added (`v2/docs/handover/GLOSSARY.md`). **H1.1 is still partial: no layer is
COMPLETE.** The design files are H1's; only the handover pages, the candidate patches, four filed records
(`v2/docs/records/handover/`), the case scripts' reference outputs and the packer changed. Each of the fifteen
findings, where it is answered and in which commit, is in `v2/docs/handover/H1.1-RESPONSE.md`, which also names the
parts left open.

**Edition H2** (27 September 2026) carries board B's round 8, sets 4 and 5 (the layer 2, 3, 5 and 7 closers, the
re-take driver, the case release, wave 3 on boards A, B, D and E, the diagrams rebuilt), the consolidated re-take of
every schematic-phase reading (layout-entry reasons 101 to 40), the release of layers 1 and 2, and new exports of the
four boards whose schematics changed, with regeneration PARITY on all six. The candidate patches of H1.1 are
superseded (each merged from a later state) and are referenced rather than bundled; `candidates/README.md` stays and
names the commit that merged each. **H2 is partial:** layers 3 to 9 are IN_PROGRESS.

**After H2** (27 September 2026, not a snapshot): the fresh usability check of H2 (an AI check, not an engineering
review) found no blocking defect and fourteen minor ones; `v2/docs/handover/H2-RESPONSE.md` answers each, with where
and in which commit. No design file changed. The layout constraint sheets are re-bound to the H2 line's netlists and
intents; `pcb_interfaces.yaml`'s `read_at` and `ARCHITECTURE.md` section 3.1 are re-anchored at `ef144760`; REGENERATE
section 9 gives three routes to the re-take, one of them a repository built from the snapshot (`handover_pack.py
repo`), with board P's run; LAYER-STATUS opens each layer with an acceptance table at H2; the glossary names the
overloaded families and the evidence classes. The next snapshot carries these pages; H2's ZIP keeps its own.

**Edition H3** (prepared 27 September 2026; `SOURCE.txt` gives the build). H3 is H2's design with layer 3 released. It
adds to H2: the pages of "After H2" above; layer 3's re-baseline and its re-check (`a54b793b`, `2c12be91`, `24e7bf5a`);
the restructure of the two definition documents, which changes no definition, with their status page
`v2/docs/handover/DEFINITION-STATUS.md` (`fa89c7c6`, `a9f212c7`, `edd3c848`); the release record of H2, its usability
check, and two outside reviews saved as the owner pasted them, of the 18:00 progress report and of H2 itself
(`v2/docs/reviews/2026-09-27-third-checkpoint-review.md`, `2026-09-27-h2-independent-review.md`); and the corrections
and errata of section 1a. `v2/docs/handover/RELEASE-H3.md` is its release record.

## 1. The handover pages

| Page | Read it for |
|---|---|
| `v2/docs/handover/START-HERE.md` (this page) | what is being built, how the repository is organised, the reading order, what you need outside the repository |
| `v2/docs/handover/LAYER-STATUS.md` | the nine pre-PCB layers (its section "Status at handover H2" first, then each layer's acceptance table at H2, item by item, since after H2); its Appendix A keeps, per layer, the audit at `e3aedb25` (scope, deliverables by revision, every acceptance item met or not with its evidence, unresolved decisions, gate cycles, the next closing actions, per-board lines) and the integrator line |
| `v2/docs/handover/CONTINUATION-BRIEF.md` | the decisions an incoming PCB engineer must preserve, the remaining work in dependency order, the constraints known today, the approaches that failed and why, the experiments already specified |
| `v2/docs/handover/ENGINEERING-QUESTIONS.md` | every blocked question, one compact block each: issue, evidence, attempts, options, recommendation, expertise, cost and lead time |
| `v2/docs/handover/REGENERATE.md` | how to regenerate the schematics and re-run the checks, and which host each step needs (written separately from these four pages) |
| `v2/docs/handover/GLOSSARY.md` | every internal name the pages use: closers and streams, rounds, finding-id schemes, evidence labels, the title-block labels A65, D37P and E42P |
| `v2/docs/handover/H1.1-RESPONSE.md` | the usability check of H1, finding by finding: where each is answered, in which commit, and what is left open |
| `v2/docs/handover/H2-RESPONSE.md` | the usability check of H2 (no blocking finding, fourteen minor ones), finding by finding: where each is answered and in which commit (after H2) |
| `v2/docs/handover/RELEASE-H3.md` | the release record of H3: the layers it delivers as COMPLETE with their baseline commits and review records by sha256, what was and was not repeated independently, and its errata. Inside the ZIP its build figures are blank, because a snapshot cannot carry its own checksum: read them beside the ZIP |
| `v2/docs/handover/RELEASE-H2.md` | the release record of H2, kept as written |
| `v2/docs/handover/DEFINITION-STATUS.md` | the running status of layers 1 and 2: which commit each definition is baselined at, the restructure of 27 September 2026 and its check, and where each dependency's current state lives. The product brief and the concept of operations point to it and carry no changing result themselves |
| `v2/docs/handover/candidates/README.md` | the candidates of H1.1 (board B's round 8, the layer 2, 3, 5 and 7 closers), SUPERSEDED since, each merged from a later state; the README names each merging commit, and since H2 the patches are referenced, not bundled |

## 1a. Handover H3: what it delivers, three ways to use it, and its errata

**What H3 delivers.** Every review named is an AI review or an AI check, labelled as one in its own heading; none is
a qualified engineering review, and nothing has been built. `RELEASE-H3.md` gives each record's sha256.

| Layer | Status in H3 | Baseline |
|---|---|---|
| 1. Product definition | **COMPLETE** | `v2/docs/PRODUCT-BRIEF.md`, definition baselined at `6b2a9965`; re-stamped BASELINED at `a9f212c7` by an editorial restructure with no definition change (`v2/docs/reviews/DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md`, CONTENT_PRESERVED) |
| 2. Concept of operations | **COMPLETE** | `v2/docs/CONOPS.md`, definition baselined at `79963b3b`; re-stamped BASELINED at `a9f212c7` the same way |
| 3. Requirements | **COMPLETE** since commit `24e7bf5a` | `v2/ecad/tools/pcb_requirements.yaml`, `baseline_state` BASELINED at `a54b793b`, written in `2c12be91`; the re-check `v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md` finds B-1 CLOSED at `2c12be91`, and S-51, S-78 and S-80 are closed. H3 is its versioned package (acceptance item 3.18). The registry H3 carries still lists S-79, the item that waits for this package, as open: it is closed in the commit that files the snapshot, after the build |
| 4 to 9 | IN_PROGRESS | as in H2: LAYER-STATUS, sections "Status at handover H3" and "Status at handover H2" |

The three complete layers state what the kit is for, how it is used and what it must do. They do not claim that the
design meets a requirement: where it does not (REQ-072 reads FAIL at desk, for one), the registry says so.

**What changed since H2, and what did not.** Compared with H2's source commit `b89b50b4`, no design file differs: no
schematic, netlist, intent, land, generator, board table, checking tool, export, CAD file, diagram or maker document.
Under `v2/ecad/` eleven files differ: the packer and its test, the requirements registry (its baseline, open and
closed items, and the readings and notes of four records; no record's statement, acceptance, allocation, verification
or release effect), the interfaces registry (its `read_at` block) and INT-001's seven tracked readings, each PASS as
before. `v2/docs/records/h3/design_difference.py` prints and asserts this, and needs a git checkout. The headline and
the layout-entry reasons are H2's: 0 boards ready for layout, 40 reasons (`v2/docs/CURRENT-EVIDENCE.md`, the same file
by sha256). The counts of H3 are printed by `v2/docs/records/h3/handover_counts.py`, which reads only files the snapshot carries.

**Three ways to use this handover.** They are separate, and only the first needs nothing but the ZIP.
`REGENERATE.md` gives each route's prerequisites and expected results in full.

| Route | Needs |
|---|---|
| A. Read the handover and continue from it | the ZIP and a reader for Markdown and PDF |
| B. Reproduce a calculation (the stored-energy chain) or a schematic (one board regenerated and compared) | Python 3 with PyYAML, and one maker document restored first (Mill-Max's catalogue page 28, fetched and checked by REGENERATE section 1a); for a schematic also KiCad 9.0.9 |
| C. Run the test suite and re-take the readings | a git checkout with history, outside `/tmp`, and KiCad 9.0.9. **From the ZIP alone the suite is not expected to pass:** H2 read 1956 passed, 20 failed and 23 skipped from its ZIP, each failure caused by an input a snapshot leaves out |

**Errata of H3: what it knowingly does not fix.** Each is known and stated here; none changes the status of layers 1
to 3.

| # | What is not fixed | Effect on a reader | Where it will be fixed |
|---|---|---|---|
| a | Each layout constraint sheet's sections other than its power table are readings at `e3aedb25`, as the sheet's own head says; the power tables are current on H3's netlists | a placement, protection or test-access line of a sheet may describe an older netlist; where it and a record disagree, the record governs. One such row was found and corrected for H3 (board A, section 7) | each board's sheet re-derived on its netlist by the board stream, before that board's layout entry |
| b | `LAYER-STATUS.md` mixes status with history: its Appendix A holds the audit at `e3aedb25` and every integrator line | the page is long (about 290 KB); read its sections "Status at handover H3" and "Status at handover H2" and each layer's acceptance table, and use Appendix A only to trace an item | a restructure of the page after H3 |
| c | Re-taking one board in a repository built from the ZIP re-renders every other board's page as NO_EVIDENCE (REGENERATE section 9) | compare only the re-taken board's rows; the other boards' pages in that repository are not evidence | the readings bundled with a later snapshot, or a re-take of every board |
| d | `ENGINEERING-QUESTIONS.md` was not re-read row by row for H3. Five rows found stale against later records were corrected in place, each marked **Corrected for H3**: EQ-01, EQ-04, EQ-10, EQ-16 and EQ-17 | another row's options or recommended action may predate its own attempts row; the attempts row is the newer, and the record it cites governs | the page's next edition |
| e | The set 6 circuit candidate is not in H3 | H3 lists as open several items for which a drawn candidate exists outside it (next paragraph) | the snapshot after set 6 is promoted |
| f | Board A's external-port declaration (`v2/ecad/tools/boards/a.json`) still names J_DOCK pins 1 and 2, which are ground since SC-55 moved VIN_RAW to J_VR1 to J_VR4 | TRN-001's PASS on board A does not judge VIN_RAW's entry (read in `port_protect.py`'s code, not re-run; `v2/docs/layout-constraints/A.md` section 7); the clamp D2 is on VIN_RAW in the netlist | board A's stream: the declaration moved, TRN-001 re-taken |

**What exists outside H3.** A circuit candidate called set 6 stands on branch `fnd/r8int6`, not promoted and not in
this snapshot: remedies for EQ-25 on board C, HOT-R1 on boards A and E, the undeclared supplies and flyback diodes
behind PWR-001 on boards C, D, E and P, board P's protection table, the RockBLOCK's ENABLE under EMCON on board B and
E5's INT-001. The integrating session reports its suite on the KiCad host at 2010 passed, 1 failed, 3 skipped, the
failure a checker's false positive under repair; that record is not in H3. Five desk streams called wave 5a (branches
`fnd/w5tray`, `fnd/w5stack`, `fnd/w5si`, `fnd/w5ident` and `fnd/w5i2c`: the lid tray, the stackups, the signal rules,
the parts and the I2C work of layer 5) are being recovered from their transcripts, as unchecked checkpoints on four
of the five branches when this was written. None of
this changes a statement of H3, and none of it is evidence until it is checked and promoted.

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
the cells; a closed-lid reduced mode (defined in `CONOPS.md` section 4c since the layer 2 closer, and baselined with layer 2 after its second release check, LAYER-STATUS layer 2). The hot end is not established: the
sealed case's heat path is known only as a bound that includes failure (ENGINEERING-QUESTIONS EQ-05).

**What it is not, today** (`v2/docs/PRODUCT-BRIEF.md`, "What it is not, today"): not built, powered or measured; not
rated (Peli's case is IP67, the face is designed to an IP67-class construction and carries no rating); not certified
and no certification claimed; no vehicle surge claim (D-16); no finished runtime figure.

## 3. Where the design stands in H2

The counts of the design's state in this section (the layout-entry reasons, the registry's counts, the BOM rows) are
printed by `v2/docs/records/h2/handover_counts.py` from the snapshot's own files (its output is `handover_counts.out`
beside it; re-run it from the snapshot's root to check them); every other figure names the commit or the run it comes
from. **H3:** this section is H2's and its design statements hold in H3. What H3 changes in it is marked **H3**; H3's
counts are `v2/docs/records/h3/handover_counts.out`, which differs from H2's in the registry's state and its open and
closed items, in the two definition documents' hashes and in the review records listed, and in no count of the design.

- **Source.** Main `62f26a44` plus branch `fnd/h2` (the targeted fix and narrow verification of layers 1 and 3, the
  claims screen re-taken after them, the H2 exports, these pages). Last design change `b7f96784` (set 5); last tool
  change `7dfbfb16` (the requirements validator refusing an undefined SC- id).
- **Headline** (`v2/docs/CURRENT-EVIDENCE.md`, generated): foundations incomplete; 0 boards ready for layout; 0
  physically verified. Layout-entry reasons A 7, B 7, C 5, D 8, E 5, P 6, E5 2, 40 in all (101 before the consolidated
  re-take of `8ea7867e`): 15 current readings that are not a PASS, 1 deciding verification (E5's INT-001), 3 decision
  31's protection review (A, D, E), 21 layout-entry stages of the feasibility blockers FEA-001 to FEA-007. Every
  schematic-phase reading is current on the committed netlists except E5's INT-001; LAYER-STATUS lists each reason.
- **Layers.**

  | Layer | Status in H2 | Evidence |
  |---|---|---|
  | 1. Product definition | **COMPLETE** | `v2/docs/PRODUCT-BRIEF.md` BASELINED (`6b2a9965`); Review A layer 1, two release checks and the narrow verification `v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md` (AI reviews). **H3:** re-stamped BASELINED at `a9f212c7`, an editorial restructure with no definition change (section 1a) |
  | 2. Concept of operations | **COMPLETE** | `v2/docs/CONOPS.md` BASELINED (`79963b3b`); Review A layer 2 and the second release check `v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md`, no blocking finding (AI reviews). **H3:** re-stamped BASELINED at `a9f212c7` the same way |
  | 3. Requirements | IN_PROGRESS in H2. **H3: COMPLETE** since commit `24e7bf5a` | the registry validates (144 records, 0 errors and 0 warnings in a git checkout holding its closing commits and the gitignored readings; from the ZIP alone 13 errors and 17 warnings, and in a repository built from the ZIP 30 errors: REGENERATE.md section 7 gives each count's condition). In H2 it stood at READY_FOR_REVIEW_B and its baseline waited on S-80's wording fix and its re-check (EQ-30). **H3:** both are done: `baseline_state` reads BASELINED at `a54b793b`, written in `2c12be91`, and the re-check `v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md` (an AI check) finds B-1 CLOSED at `2c12be91`; S-51, S-78 and S-80 are closed, and nothing of layer 3 waits on S-80 |
  | 4 to 9 | IN_PROGRESS | LAYER-STATUS, section "Status at handover H2": what landed since H1 and what remains, per layer |

  None is BLOCKED as a whole. Layer 3 closed with desk work, after H2; layers 4 to 9 each hold items that need a purchase, a
  bench, an outside reviewer or an outside answer (ENGINEERING-QUESTIONS groups B and C). A board's layout entry
  also needs its own reasons closed; completing one board would not complete the schematic layer.
- **Readable exports.** `v2/release/handover/_generated/<board>/`: an A3-paged schematic PDF, two BOMs named
  NOT_FOR_FAB, the ERC report, the netlist's parity with its schematic and `provenance.json`. Boards A, B, D and E
  were re-exported for H2 at `763bccdf` (their schematics changed in board B's round 8 and set 5); C and P keep their
  `99cde56b` exports, whose provenance names the schematic sha256 the snapshot still holds. Regeneration from a clean
  archive read PARITY on all six on KiCad 9.0.9 (REGENERATE.md sections 4 and 5).
- **Diagrams** (`v2/docs/diagrams/`) are drawn at `b7f96784` (committed at `730f8489`), on set 5's netlists of all six
  boards.
- **Known gaps of H2, and their effect.**
  (1) **Readings outside the snapshot.** The readings behind `CURRENT-EVIDENCE.md` and `PCB-RULE-STATUS-*.md` live in
  the gitignored `v2/ecad/out/` and each board's `out/` folder. The consolidated re-take also copied its readings (89
  files: the verdicts and SI-001's tables) into each phase's tracked `routed/` folder, but `pack.yaml` leaves `routed/` out with the
  stale layout verdicts beside them. Effect: a recipient reads the rendered pages, and re-takes a reading
  (`retake_schematic_phase.py`, REGENERATE.md section 9) or reads the tracked copy in the repository, rather than
  reading it back from the ZIP.
  (2) **The test suite needs a git checkout** for `test_netlist_provenance` and for the registry's closed-by-commit
  checks; from the ZIP alone those fail (REGENERATE.md section 7 lists every failure and its missing input).
  (3) **The ZIP is deterministic per host**: two builds of one commit on one host are byte for byte equal; on another
  host compare `MANIFEST.tsv`, not the ZIP's sha256.
  (4) **Referenced, not bundled**: maker documents (except the eight the energy chain cites and the seven the
  requirements registry cites, `pack.yaml`) and, since H2, the five superseded candidate patches. CON-017's three ST
  documents stay referenced for size, so the requirements validator reads its four CON-017 citations missing from the
  ZIP alone until `v2/vendor/st/` is restored (REGENERATE.md section 1a fetches any referenced file by its git blob sha).
  (5) **SI-001's edge-rate declarations are owed.** SI-001 reads INCONCLUSIVE on all six boards with a schematic,
  because most signal classes have no driver edge rate: their makers publish none (`v2/docs/PCB-GAP-REGISTER.md`,
  SI-001). Effect: SI-001 is a layout-entry reason on every one of those boards until each class carries a stated
  bound with its source, or a bring-up measurement decides it.
  (6) **The diagrams' manifest check** (`python3 v2/docs/diagrams/tools/build.py --check`) reads 6 of 11 current in
  the repository at H2, because `ARCHITECTURE.md` changed outside its Mermaid blocks at `7dfbfb16` (section 8's C1
  text); `extract_mermaid.py --check` reads the Mermaid sources current, so the drawings' content is unchanged.
  **Corrected after H2:** from the H2 ZIP it reads 4 of 11, because the case plan and Z-stack drawings also read
  `v2/cad/render/scene.py` (the Z of boards E5, A and D in the render stack), which H2's `pack.yaml` excluded as
  presentation; after H2 `pack.yaml` bundles that one file, so the next snapshot reads as the repository does. After H2
  the repository reads 5 of 11: `pcb_interfaces.yaml`, an input of the control-lines drawing, changed in its `read_at`
  header only, and `control_lines.py --check` reads that drawing current. Effect: none on the drawings' content; a
  rebuild (it needs Node and a Chromium) re-stamps `MANIFEST.json` (the diagrams' writer).
  (7) **Q-B-ESC-1's final boards** stay outside the package (section 7).
  (8) **The layout constraint sheets were stale in H2** (added after H2): `v2/docs/layout-constraints/` was bound to
  `e3aedb25`'s netlists and intents, and `calc/rail_widths.py` on H2 changed 41 lines of its output (board A's VIN_RAW
  12.31 A and 11.92 mm became 14.10 A and 15.29 mm on one outer face; rails PRECHG, VMON, +3V3_EMCON_EF and +3V3_EMCON
  new on A, seventeen on B, +5V_TX on D; board E's VIN_RAW and TRK_OUT at 14.10 A and 10.33 A). After H2 the power
  tables are regenerated and every sheet is re-bound to the H2 line's netlist and intent; what a sheet still reads at
  `e3aedb25` is said at its top. Effect in H2: read H2's sheets' power tables through `calc/rail_widths.py`, not as
  written.

## 3a. Where the design stands in H1 (history since H2)

- **Source.** Main `84e52461` (circuit round 8, sets 1 and 2: boards A, C, D, E and P regenerated with parity; the
  netlist checks PWR-001, SI-001 and RF-002; the pack's temperature ladder) plus the handover branch: the layer 1, 4,
  6 and 9 closers' work (product brief through Review A's second pass, readable diagrams, part records, layout
  constraint sheets and the stackup record), the packer, the exports, these pages. Last design change `99cde56b`.
- **Headline** (`v2/docs/CURRENT-EVIDENCE.md`, generated): foundations incomplete; 0 boards ready for layout; 0
  physically verified. Layout-entry reasons A 17, B 16, C 11, D 15, E 16, P 15, E5 5.
- **Layers.** All nine are IN_PROGRESS; none is COMPLETE and none is BLOCKED as a whole. Layer 1 is the nearest: its
  review (an AI review) has no blocking finding and it waits on layer 2's EMCON and face text. LAYER-STATUS says what
  remains per layer, and which closers' work is a candidate in a worktree rather than in H1.
- **Board B's round 8 is not in H1's design** (EQ-20); every other board carries its round 8 netlist. Board B's round
  8, and the layer 2, 3, 5 and 7 closers' work, are bundled as UNACCEPTED candidate patches with their bases, sha256
  and last reviews (`v2/docs/handover/candidates/README.md`); a recipient can apply, review or redo them.
- **Readable exports.** `v2/release/handover/_generated/<board>/`: an A3-paged schematic PDF, two BOMs named
  NOT_FOR_FAB, the ERC report, the netlist's parity with its schematic and `provenance.json`, for all six boards with a
  schematic, made at `99cde56b` on KiCad 9.0.9; regeneration from a clean extraction read PARITY on all six.
- **Diagrams** (`v2/docs/diagrams/`) are drawn at `b7f96784` (committed at `730f8489`), with round 8 on all six boards and set 5 on
  boards A, B, D and E; their README says how they were made and checked, and what the power tree's attribution check
  does not cover.
- **Known gaps of H1 and H1.1.** (1) The readings behind `CURRENT-EVIDENCE.md` and `PCB-RULE-STATUS-*.md` live in the
  gitignored `v2/ecad/out/` and each board's `out/` folder and are not in the snapshot; the rendered pages are, so a
  recipient re-takes a reading rather than reading it back. REGENERATE.md section 9 states the re-take procedure,
  which H1.1 carries in words only. **Since the set 4 branch after H1.1 (`e5fde2ed`) the driver exists:**
  `v2/ecad/tools/retake_schematic_phase.py` plans every schematic-phase writer per board from the registries
  (`--plan`) and runs them on the committed netlists (`--run --in-place --routed` in a throwaway git clone outside
  `/tmp` on a KiCad 9.0.9 host), then `rules_status.py` three times and `rules_render.py`; its trial on `a8652172`
  took the layout-entry reasons from 95 to 37 with no board ready (REGENERATE.md section 9). It is in no snapshot
  before H2.
  (2) The test suite needs a git checkout of the repository
  for `test_netlist_provenance` and for the registry's closed-by-commit checks; from the ZIP alone those fail
  (REGENERATE.md section 7). (3) The ZIP is deterministic per host: two builds of one commit on one host are byte for
  byte equal, on another host compare `MANIFEST.tsv`, not the ZIP's sha256. (4) Maker documents are referenced by
  sha256, not bundled, except the eight the energy chain cites and seven the requirements registry cites (`pack.yaml`);
  CON-017's three ST documents (about 21 MB compressed) stay referenced under the 50 MB cap, so the registry validates
  from the ZIP only once `v2/vendor/st/` is restored from the repository.

## 3b. Where the design stands at `e3aedb25` (the audit; history)

- **Headline** (`v2/docs/CURRENT-EVIDENCE.md`, its opening line, generated): foundations incomplete; 0 boards ready for layout;
  0 physically verified. The computed layout-entry test lists 92 blocker lines across the seven boards (A 16, B 16,
  C 10, D 15, E 15, P 14, E5 6). An older figure of 74 in `v2/docs/EXECUTION-PLAN.md` (checkpoint of 26 September
  20:45) predates the re-classing at `b9600c4a`; CURRENT-EVIDENCE is the current count. Historical aggregate
  percentages that appear in older pages mix revisions and are not readiness.
- **Layers.** All nine pre-PCB layers are IN_PROGRESS; none is BLOCKED as a whole and none is COMPLETE. The earliest
  three (product, concept of operations, requirements) can close with desk work under existing authority; layers 4
  to 9 each contain items that need a purchase, a bench, an outside reviewer or an outside answer. Details:
  `v2/docs/handover/LAYER-STATUS.md`.
- **Milestones.** `v2/docs/EXECUTION-PLAN.md`, section "The reviews, and what each one gates" (the paragraph
  "Milestones, each reported separately"), lists FOUNDATIONS_BASELINED, DESIGN_READY_FOR_LAYOUT
  (per board), DESIGN_PACKAGE_READY_FOR_PROTOTYPE, PROTOTYPE_FAB_RELEASED, PROTOTYPE_VERIFIED and
  PRODUCTION_RELEASE_READY. None is reached. FOUNDATIONS_BASELINED keeps its recorded scope (the product definition,
  the requirements with their verification method, the architecture and budgets, the interface contracts and the
  review of parts and circuits, `v2/docs/EXECUTION-PLAN.md`, its opening paragraph, gated by Reviews A to D in the
  table of its section "The reviews, and what each one gates"); it is
  not used here, or anywhere, to imply that all nine layers or a fabrication package are complete.
- **Circuit work in flight.** A round of circuit corrections on every board ("round 8") and several tool changes were
  being authored in parallel branches when this edition was written. They are not in `e3aedb25` and nothing in this
  section counts them. LAYER-STATUS carries one marked line per layer for the integrator to update as they land;
  section 3a says where each stands in H1.
- **Layout.** Every committed board layout predates its corrected netlist (CURRENT-EVIDENCE.md, "The candidate each
  board is judged against": SCH-002 FAIL on A and B, INCONCLUSIVE on C, D, E and P). The three-module board B has
  never been routed to completion (B12 to B15 were an earlier single-module generation). The order folder is rebuilt and quarantined (decision 41): nothing is to be ordered from it.

## 4. How the repository is organised (only what a newcomer needs)

| Path | What it holds | Authority |
|---|---|---|
| `README.md`, `v2/README.md` | public overviews | public text; parts of both are stale at `e3aedb25` (LAYER-STATUS layer 1 lists the lines) |
| `v1/` | the two V1 kits as built (tesseract, parallax) | out of scope for this handover |
| `v2/docs/` | the engineering documents: product brief, concept of operations, envelope, specification, architecture, interfaces summary, panel contract, hardware and firmware contract (`HW-FW-CONTRACT.md`), assembly, case margins and case-fit uncertainties, test plan, execution plan | the editable working documents are the authority; a snapshot is an immutable copy |
| `v2/docs/feasibility/` | the six architecture feasibility studies' pages: ZEROIZE, EMCON, FAILOVER-FABRIC, POWER-THERMAL, DECOUPLING (battery: `v2/docs/review-packets/battery/`), plus `fab/` scripts | desk studies, labelled PROVISIONAL or with evidence labels |
| `v2/docs/reviews/` | the owner's reviews of 26 September and his execution prompt of 27 September (verbatim), the review routes, the costed ready-to-act packet, the INT-002 assessment | the owner's reviews govern execution |
| `v2/docs/records/` | session records that committed pages cite (scripts, outputs, decision logs), filed byte for byte with sha256 (`v2/docs/records/README.md`) | records, not tools and not authorities |
| `v2/docs/review-packets/battery/` | the packet for the qualified battery review R-BAT, with its manifest check | review input |
| `v2/docs/MESHSAT-709-geometry-appendix.md` | the design record, about 19,000 lines of dated entries (rulings, measurements, audit rounds) | history; use it only to trace a ruling another page cites |
| `v2/ecad/tools/pcb_requirements.yaml` | the requirements registry: 19 needs, 144 records (REQ 77, CON 26, CFL 18, ASM 7, FEA 7, SPD 6, CHO 3), 29 owner rulings, 63 session choices (SC-01 to SC-63), 58 open and 53 closed items, counted for H3 (60 open and 50 closed at H2, the rest the same; 132 records and 16 session choices at H1); `SOURCE.txt` prints the counts at the snapshot's build commit, and those govern | the single authority for requirements; `v2/docs/REQUIREMENTS-TRACE.md` is its generated view |
| `v2/ecad/tools/pcb_decisions.yaml`, `pcb_rules.yaml`, `pcb_interfaces.yaml`, `pcb_envelope.yaml`, `pcb_board_holds.yaml`, `pcb_energy_chain.yaml`, `pcb_pack_protection.yaml`, `pcb_part_temps.yaml`, `reserved.json` | the decision, rule, interface, envelope, hold, energy-chain, pack-protection and part-temperature registries | machine-read authorities for the tools; some are stale at `e3aedb25` (LAYER-STATUS says which) |
| `v2/ecad/tools/gen_sch_<x>.py`, `boards/<x>.json`, `kisch.py`, `intent.py`, `schlayout.py`, `gen_footprints_*.py`, `v2/ecad/meshsat.pretty/` | the schematic generators and their shared inputs: the boards are generated by scripts, not drawn | the source of truth for each circuit |
| `v2/ecad/pcb-*/` | per board: the generated `.kicad_sch`, the committed netlist `out/<board>.net` with its provenance sidecar `.net.prov.json` and intent file `-intent.json`, allow lists; also the historical layouts | schematic and netlist current; layouts historical |
| `v2/ecad/tools/` (the rest) | the checking tools, the pipeline and its tests (`tests/run.py`) | tools; a tool's verdict is evidence only when bound to the current candidate |
| `v2/vendor/` | makers' documents and CAD, with `SOURCES.yaml` (identity, revision, source and sha256 per critical part), `sources.txt`, `vendor-status.txt`, `open-picks.txt` | reference material under the makers' own terms; a held document does not validate a part |
| `v2/cad/` | CAD generators of the made parts (face plate, pack box, lid tray, float clamp) and the render scene | carries the case choices C1 to C6 since `c351115d` (the pack box still draws the older 4S4P block, S-27; the render scene is presentation) |
| `v2/release/case-2026-09-27/` | the case release for C1 to C6: the made parts' STEP and DXF, dimensioned drawings (sheets 1 to 14, the QMX lid tray on sheet 14), templates, the stack report, `MANIFEST.sha256` | current; the lid tray is not to be printed before S-63 (EQ-24) |
| `v2/release/handover/` | the snapshots (`H1/` unzipped; `H1.zip`, `H1.1.zip`, `H2.zip` and `H3.zip` with their sha256 and manifests) and `_generated/`, the readable exports of the schematics | a snapshot is an immutable copy; `_generated/` is regenerated when a schematic changes (H3 keeps H2's exports: no schematic changed) |
| `v2/release/revA/` | deliverable folders, review prints and case templates of earlier layout phases, and the order set | historical; the order set was rebuilt and quarantined (decision 41), and nothing is to be ordered from it. One file is the exception: `v2/release/revA/order/JLC-CERTIFIED.tsv` is bundled and current (section 5, layer 6) |
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
`v2/docs/PRODUCT-BRIEF.md`, section "Constraints fixed by owner rulings") or under his standing rule of 26 September 2026 (`pcb_requirements.yaml`
`owner_rulings` entry `standing-rule`): where a choice is left, the session takes the option the evidence recommends
and records it with its reason and how to reverse it (`session_choices` SC-01 to SC-16 in H1, SC-01 to SC-63 in H2). Money, outside contact,
publication and promotion stay with the owner. A new team taking over should state its own authority model; every
SESSION choice names how to reverse it.

## 5. Reading order through the nine layers

Read in order; each layer's authoritative files first, then its status in LAYER-STATUS.

| Layer | Authoritative files (read first) | Supporting |
|---|---|---|
| 1. Product definition (COMPLETE since H2) | `v2/docs/PRODUCT-BRIEF.md` (BASELINED) | `v2/docs/handover/DEFINITION-STATUS.md` (the running status of layers 1 and 2), `v2/docs/V2-SPEC.md` (the device set with dated corrections 1 to 19), `pcb_requirements.yaml` `owner_rulings` |
| 2. Concept of operations (COMPLETE since H2) | `v2/docs/CONOPS.md` (BASELINED; needs NEED-01 to NEED-19, missions, modes, power states, rulings), `v2/docs/OPERATING-ENVELOPE.md`, `v2/ecad/tools/pcb_envelope.yaml` | `v2/docs/PANEL.md` (operator-facing behaviour), `v2/docs/TEST-PLAN.md` (envelope limits) |
| 3. Requirements (COMPLETE in H3) | `v2/ecad/tools/pcb_requirements.yaml` (BASELINED at `a54b793b`), its generated view `v2/docs/REQUIREMENTS-TRACE.md` | `v2/ecad/tools/rules_lib.py` (the validator), `v2/ecad/tools/pcb_rules.yaml` (the board rules records name) |
| 4. System architecture | `v2/docs/ARCHITECTURE.md` (sections 14 and 15 first: the feasibility blockers and the stale siblings) | `v2/docs/feasibility/*.md`, `v2/docs/B-FEASIBILITY.md`, `v2/docs/ARCH-PCB-B-IOHA.md`, `v2/docs/review-packets/battery/` |
| 5. Partitioning and interfaces | `v2/ecad/tools/pcb_interfaces.yaml` (`board_to_board`, 30 contracts; its `read_at` names the H2 line's netlists since after H2, and each contract's `src` lines stay as that contract states them), `v2/docs/HW-FW-CONTRACT.md` (the firmware obligations that affect hardware), `v2/docs/ARCHITECTURE.md` sections 3, 10 and 12 | `v2/docs/PANEL.md`, `v2/docs/ASSEMBLY.md` section 4, `v2/docs/GROUNDING-AND-SHIELDS.md`, `v2/ecad/tools/check_contracts.py` |
| 6. Components | `v2/vendor/SOURCES.yaml` (read each entry's update blocks, not only its top-level fields), `v2/release/revA/order/JLC-CERTIFIED.tsv` (bundled and current: it is the one file of the quarantined order folder that is not historical, the dated catalogue reading `jlc_certify.py` writes; a `pack.yaml` rule carves it out of the folder's exclusion) | `v2/docs/evidence/WRONG-MODEL-RECONCILIATION.md`, `v2/ecad/tools/pcb_part_temps.yaml`, `v2/vendor/open-picks.txt` |
| 7. Mechanical and enclosure | `v2/docs/CASE-MARGINS.md` (sections 4 and 7), `v2/docs/CASE-FIT-UNCERTAINTIES.md`, the case release `v2/release/case-2026-09-27/`, `v2/vendor/peli/frame_seat.py` and its output `v2/vendor/peli/1450/frame_seat.out` (bundled since H1.1) | `v2/vendor/peli/1450/` (Peli STEP, DXF, drawing), `v2/docs/ARCHITECTURE.md` sections 7 to 9 and 11, `v2/docs/ASSEMBLY.md` |
| 8. Schematics | per board: `v2/ecad/pcb-*/pcb-*.kicad_sch` and `out/*.net`, generated by `v2/ecad/tools/gen_sch_<x>.py` | `v2/docs/CURRENT-EVIDENCE.md`, `v2/docs/PCB-RULE-STATUS-<x>.md`, `v2/docs/records/r4a`, `r4b`, `r4e`, `r4p`, `r6d` |
| 9. Pre-layout design analysis | `v2/docs/feasibility/POWER-THERMAL.md` and `v2/docs/records/rv-pwr/pwr_budget.py`, `v2/docs/feasibility/DECOUPLING.md`, `v2/docs/B-FEASIBILITY.md`, `v2/docs/reviews/INT-002-PRE-LAYOUT-ASSESSMENT.md` | `v2/docs/LAYER-DECISIONS-2026-09-11.md` (stale on B, C and P), `v2/ecad/tools/stackup_write.py`, `v2/vendor/fabricator/` |

Then read `v2/docs/EXECUTION-PLAN.md` (the seven standing conditions, section "Standing conditions (owner, 25 September
2026)", and the stage gates, section "Stage gates: layout entry, fabrication release, prototype verification"), the
owner's two reviews of 26 September in `v2/docs/reviews/`, and `v2/docs/reviews/READY-TO-ACT.md` (the
costed external and bench work).

## 6. Regenerating and verifying

The full instructions are `v2/docs/handover/REGENERATE.md`. In short:

- **Runs anywhere with Python 3.11 and PyYAML 6, no KiCad, from the ZIP alone** (each run from a fresh extraction of
  H2, and not run again on H3, whose inputs to these commands are H2's but for the registry: REGENERATE.md, "Edition
  H3", says what is expected to differ): the power model `v2/docs/records/rv-pwr/pwr_budget.py <out.json>` (the JSON it writes byte-identical to
  `pwr_budget.json` and its stdout to `pwr_budget.out`, both beside it); the case margin scripts
  `v2/vendor/peli/frame_seat.py` and `v2/vendor/peli/case_margins.py` (stdout byte-identical to
  `v2/vendor/peli/1450/frame_seat.out` and `case_margins.out`); `v2/ecad/tools/check_contracts.py v2/ecad` on the
  committed netlists, with `VERDICT_DIR` pointed outside the tree (PASS 99 of 99 cross-board checks; they judge pin-map
  identity and presence, not currents, levels, timing or mating); `v2/docs/records/h2/handover_counts.py`, which prints
  every count these pages quote (for H3, `v2/docs/records/h3/handover_counts.py`). `python3 v2/ecad/tools/rules_lib.py requirements` reads 144 records with 13 errors and
  17 warnings from the ZIP: every error is a maker document the registry cites and the snapshot references rather than
  bundles (CON-017's three ST documents and eight cited since H1), and the warnings are closed-by-commit checks that
  need git history and the gitignored readings (REGENERATE.md section 7, whose table gives the condition of every
count: 0 errors and 0 warnings in a git checkout holding the history and the readings). The representative calculation,
  `energy_chain.py`, reads FAIL from the ZIP alone on one referenced citation, Mill-Max's catalogue page 28 (3.8 MB),
  and PASS of 98 once it is restored (REGENERATE.md section 6).
- **Runs once referenced files are restored** (REGENERATE.md section 1a fetches each from the public repository's raw
  files and checks it against its git blob sha in `REFERENCED-SOURCES.tsv`; in the H2 run 29 files, every one OK):
  `python3 v2/ecad/tools/rules_lib.py requirements` then reads 144 records, 0 errors, and `python3
  v2/ecad/tools/rules_render.py --requirements --check` reads "REQUIREMENTS-TRACE.md is current" (from the ZIP alone it
  prints REFUSED); `v2/docs/review-packets/battery/evidence/check_manifest.py` reads RELEASE CHECK PASS on its 139
  manifest rows (from the ZIP alone it prints RELEASE CHECK FAIL with each missing document named; the packet is
  R-BAT's review input, so never send it from the ZIP alone); `energy_chain.py` reads PASS of 98.
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
| Committed board layouts, their verdicts, DRC reports, Gerbers, order folders, deliverable folders under `v2/release/revA/`, EasyEDA conversions | every layout predates its corrected netlist; the order set is quarantined (decision 41); `v2/BUILD.md` is the 7 September ordering guide and is not to be used for ordering. The order folder's `JLC-CERTIFIED.tsv` is not excluded: it is bundled and current (section 5, layer 6) | `v2/docs/CURRENT-EVIDENCE.md` (candidate table) |
| Review packets D-D12 and P-P4 at `1f614233` | superseded (`v2/release/review-packets/README.md`) | the battery packet `v2/docs/review-packets/battery/` for P |
| Concept renders and board images | presentation, not engineering input; the renders show the 7 September arrangement. So `README.md`'s and `v2/README.md`'s image links (`v2/images/`) and their links into `v1/` do not resolve inside a snapshot; both READMEs say so since after H2. One file under `v2/cad/render/`, `scene.py`, is bundled since after H2, because the case drawings read the boards' Z from it | `v2/docs/CASE-MARGINS.md` for the current arrangement |
| Schematic-phase readings that the status pages render | they sit in gitignored `out/` folders on the build host (`.gitignore`); since the consolidated re-take (`8ea7867e`) each phase's tracked `routed/` folder also holds a copy of the current schematic-phase readings, beside older layout readings, and `pack.yaml` leaves `routed/` out as a whole (known gap 1 of section 3) | CURRENT-EVIDENCE.md classes every reading; REGENERATE.md section 9 re-takes them with `retake_schematic_phase.py` |
| Q-B-ESC-1's final boards, DRC reports and 26 per-pass sessions | kept on the rented build host and in a session record outside the tree, named only by sha256; the host was a rented one and the files are not recoverable from this package (a known gap, not fixed in H1.1) | `v2/ecad/tools/routeflow/experiments/b_esc1/results/2026-09-26/README.md`, `v2/docs/B-FEASIBILITY.md` section 7.8 |
| Round 8 circuit drafts, W1, W3, W5 and W7 workstream drafts, adjudications A01 to A11, board A's converter calculation scripts, the RF-002 walk tool `tx_inhibit.py`, the mismatch input `jlc-mismatch.yaml` | uncommitted session worktree drafts at `e3aedb25`; committed pages cite some of them (LAYER-STATUS lists each gap). In H1: round 8 of boards A, C, D, E and P, `tx_inhibit.py`, `jlc-mismatch.yaml`, W1's records (`v2/docs/records/w1/`) and the adjudications (`v2/docs/records/adj/`) are committed; board B's round 8 and the W3, W5 and W7 drafts are not. In H1.1: board B's round 8 and W5's contract draft ride in the candidate patches `r8b.patch` and `hc5.patch` (`v2/docs/handover/candidates/`), and hc4's and hc6's reviews, `3a1f6576`'s parity report and the H1 filing commit's message are filed in `v2/docs/records/handover/` | filing the rest is a closing action; until then, the citing page's own summary |
| The session's chat, memory and local instruction files | never part of the design record by rule | the rulings they carried are in the registries; gaps are named in LAYER-STATUS |
| The issue tracker (MESHSAT-nnn ids) and the MeshSat Bridge software | outside this repository; `v2/docs/PANEL.md` is the only software contract held here, and the panel's wire format is deferred to MESHSAT-837 | `github.com/meshsat/meshsat` for the Bridge |
| Maker documents in a snapshot | cited by path and sha256, not bundled for size, except those `pack.yaml` bundles for the energy chain and the requirements registry | `v2/vendor/SOURCES.yaml`, `REFERENCED-SOURCES.tsv` and the repository at the snapshot commit (REGENERATE.md section 1a) |
| The five candidate patches of H1.1 (`v2/docs/handover/candidates/*.patch`) | superseded since H1.1, each merged from a later state; referenced rather than bundled in H2 to keep the ZIP under its cap | `candidates/README.md` (bundled) names each merging commit; `REFERENCED-SOURCES.tsv` and REGENERATE.md section 1a fetch a patch |

## 8. What you need from outside the repository

| Need | Used for | Notes |
|---|---|---|
| KiCad 9.0.9 with its standard libraries and `kicad-packages3d`, `kicad-cli`, `pcbnew` importable from Python 3 | schematic regeneration, ERC, PDFs, BOMs, every board-file tool | the generators and the parity baselines were produced with 9.0.9 (`v2/README.md`, section "Regenerating a board"; the module docstring of `v2/ecad/tools/netlist_parts.py`); `pin_map_lands.py` also reads the host's KiCad footprint library |
| `mupdf-tools` | paged schematic PDFs (`build_sch.sh`) | |
| `poppler-utils` (`pdftoppm`, `pdftotext`, `pdfinfo`) | paged schematic PDFs and the exports' read-back (`sch_pages.py`, REGENERATE.md section 1); `pack_protection.py` reads the cell sheet through `pdftotext` | 24.02.0 in the H2 run (REGENERATE.md section 1; added here after H2) |
| Pillow | `sch_pages.py`, which cuts each schematic into A3 pages | 10.2.0 in the H2 run (REGENERATE.md section 1; added here after H2) |
| Python 3.11 with PyYAML 6; `numpy`, `scipy` | validators, renderers, analysis tools | the stdlib-only scripts of section 6 need nothing else |
| Java, Xvfb and the Freerouting 1.9.0 per-pass build | routing experiments only (Q-B-ESC-2, decision 43's run) | built from source by `v2/ecad/tools/routeflow/cloud/onstart.sh`; the stock jar is refused (`v2/README.md`, section "Regenerating a board") |
| `build123d` (with OCP), `ezdxf`, `matplotlib` | the CAD generators under `v2/cad/` and the Peli STEP and DXF readers | versions are not pinned in the repository (a gap, LAYER-STATUS layer 7) |
| Blender 4.2 on a GPU host | concept renders only | presentation; not needed for engineering |
| JLCPCB's public parts API (`https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`, the endpoint constant of `v2/ecad/tools/jlc_certify.py`) | part identity and stock readings (`jlc_certify.py`, `lcsc_fill.py`) | network access, no login; every reading is dated and true only at its time; the certify cache is not in the repository |
| A fabricator quote per board and layer count | the stackup price decision (STK-002, decisions 27 and 43) | JLCPCB publishes no PCB price endpoint; a quote needs an account session (EQ-14) |
| Makers' documents | part identity, ratings, lands | held under `v2/vendor/` with sha256 in `SOURCES.yaml`, `sources.txt` and `vendor-status.txt`; several vendor sites refuse automated clients, so some copies are Internet Archive captures, which `sources.txt` says |
| Documents the repository does not hold | named where they are needed | Microchip's full ATECC608B data sheet (NDA); Broadcom BCM54210PE (not published); the Mill-Max 0858 data sheet (only its product page and catalogue page 28 are held); binder M8 sheet; RG-316 sheet; MIL-STD-810 (only a transcription of Method 516.8, Table 516.8-IX, is held) and MIL-STD-461; the ADR text for the pack's classification; USB 3, PCIe CEM and HDMI channel specifications; the Xenarc 709GNK body drawing; a Raspberry Pi CM5 cooler drawing; Delta's 40 mm IP68 fan drawing |

## 9. Conventions of these pages

- No completion percentages. A layer is COMPLETE only when every acceptance item is met with its review; otherwise its
  remaining items are listed.
- A desk review, an AI review, clean ERC or passing software fixtures do not establish that a circuit is correct, and
  a desk review is never a physical test.
- Where the records disagree at `e3aedb25`, CONTINUATION-BRIEF section 8 says which one to follow; for what changed
  since, sections 0 (H1.1 to H2) and 0a (`e3aedb25` to H1) of the same brief are the newer, section 0 the newest.
- Citations name a file and its section heading. Where these handover pages cite a code or data file by line
  (`file:line`), the line is at `e3aedb25`: open that file at `e3aedb25` on the public repository (REGENERATE.md
  section 1 gives the URL pattern) to follow it. A `file:line` in a `source` field of the requirements registry
  (`v2/ecad/tools/pcb_requirements.yaml`) is at the commit the registry's `sources_read_at` names, unless the entry
  names its own commit ("as read at ..."); since the release check of layers 1 to 3 that commit is `08f3665a`
  (`v2/docs/records/r8int4/citations-reread-release.md`).
- Where these pages recommend an option, it is a recommendation. A closer who takes an engineering choice records it
  in `pcb_requirements.yaml` `session_choices` in the SC-nn form (the question, what was taken, why, and "Reverse by
  ..."), never as the owner's.
