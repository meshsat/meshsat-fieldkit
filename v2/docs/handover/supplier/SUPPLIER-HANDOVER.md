# MeshSat field kit V2: engineering handover for a supplier's engineers

Written 3 October 2026 under MESHSAT-1357, on the owner's instruction of the same day
(`v2/docs/handover/OWNER-INSTRUCTION-2026-10-03-SUPPLIER.md`). This page is the entry point of the supplier package. Every
path below is a path in the public repository `https://github.com/meshsat/meshsat-fieldkit`, from its root; the package's
`SOURCE.txt` names the commit every file was taken from, and its `MANIFEST.sha256` lists every file with its sha256.

**Brought to set 32: read section 0 first.** It names this revision, its states and what it adds; sections 1
to 10 are the page of 3 October 2026 with its later corrections, kept where still true and marked as history where set 30 differs.

**What the kit is, and what it is not yet.** The MeshSat field kit V2 is an **unbuilt prototype design**: no V2 board has been
fabricated, assembled, powered or measured, and no kit has been deployed. Every number here is a design figure, a maker's
printed figure or a desk calculation, and each record says which. The design and every review of it so far were done by AI
agent sessions under one owner: an author session per question, a separate checking session, and a second model family as
collaborator for one focused check and one targeted recheck per issue; **none of that is electrical sign-off**, and nobody with an electronics engineer's responsibility has
reviewed it. That is the work this package asks a supplier to quote for.

**What we ask of you, in three phases** (section 8 and the separate quotation request): (1) review and correct the design;
(2) build and run the prototype qualification it needs; (3) complete the design and the manufacturing release. Physical
qualification is part of the work requested; nothing in this package waits for it.

## 0. This revision: set 32 over set 31 and set 30

Added 6 October 2026 under MESHSAT-1357. Where this section and a later one disagree, this section is the current statement.
`path:N` is line N of that file at commit `6fe398e9` (`6fe398e9f624160429411e975c26564e553714d3`), the commit this section was written
from; `:N` repeats the path cited just before it; a path beginning `records/` is under `v2/docs/records/`. The owner-instruction file
is cited as `dd1aed00:v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:N`, line N at set 30's tested revision `dd1aed00`: part 26's row, filed after
`6fe398e9`, moved every later line of that file by one (dated note, W33, 6 October 2026). `dd1aed00d0a0a521063b5792550bc510c4707c59` is set 30's
promoted commit (main was fast-forwarded to it on 6 October 2026), filled in at the adoption. Prototype
framing: nothing in the kit has been built, bought, powered or measured.

**Set 31 over set 30 (6 October 2026).** This section was written for set 30. Set 31 is an adoption of record text over it: the
restatements its authors wrote during set 30's integration, the filed patch rows applied to L4-E9's page, register and generator, and
the citation re-takes, regenerated to convergence. It changes the Tested and Adopted revisions of 0a, adds its integration record to
0c, and changes none of the states of 0b: "Set 31 closes NO power item." (`records/int31/RESULT.md`, section 6). Its classification
counts 25 commits that change what cx46 read or carry another row's change into a file of the reviewed tree (set 30's rule, reading A), each "UNREVIEWED since cx46" (`records/int31/CLASSIFICATION.md`, section 2).

**Set 32 over set 31.** Set 32 is an adoption of record text and record tooling over set 31: 26 record generators read their makers'
PDF text from committed verbatim extractions (a held-back sheet's text is held back with the sheet and re-taken after the fetch,
as section 7 gives it: 57 texts), and the tests' own reads of it are declared; each verdict word is attributed to its check; the handover ZIP's cap is raised to 100 MiB; N1a's phrase is carried into V-E16 row 3 of the firmware contract; record l4e7's
results cache is keyed on the sixteen numbers the record reads of `l4e11_power.out`, with ONE re-key; the outputs these move are
regenerated. It changes the Tested and Adopted revisions of 0a, adds its integration record to 0c, and changes none of the states of
0b: "Set 32 closes NO power item." (`records/int32/RESULT.md`, section 6). The DESK gate and the three completion claims, in the
assessment's words, unchanged: "Layer 4's DESK gate: NOT PASSED"; "Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN
ITEMS"; "Power-design closure: BLOCKED. Fabrication release: BLOCKED." (`records/l4close/L4-DESK-GATE-ASSESSMENT.md`, section 6). Set
31's known item, record l4e7's paragraph 0a's history sentence (`records/int31/RESULT.md`, section 4a), is corrected by set 32's one
re-key and the regeneration of its dependents (paragraph 0a at the candidate no longer names set 30's integrator: read at the adoption, after these rows were written); the regenerated
`records/l4e7/l4e7_p0sol.out` at the candidate prints in its paragraph 0a: `its key field is the key of its own parts and no part differs from this tree's`.

### 0a. The revisions

| Revision | Commit | What it is |
|---|---|---|
| Tested | `f08e3961` | set 32's promoted revision (set 31's was `5f25daf3` and set 30's `dd1aed00d0a0a521063b5792550bc510c4707c59`, each kept as dated history): the commit the gated release suite and the promotion gate ran on; the package's `README.md`, section "What was tested, and how", gives the suite's line and, where the packaged commit differs, every file changed between them (section 7, item 4) |
| Adopted | `9a0a0f6a` | set 32's adoption commit, to which main was fast-forwarded after the promotion: the first revision of main that holds these pages and the set 32 records as adopted (set 31's was `73941afc`, 6 October 2026, pushed 23:43:17 CEST, kept as dated history; set 30's was `836f711b406be48d9eb58c9cf6f7491fbcf7c5ec`, 6 October 2026, 11:25 CEST, kept as dated history) |
| Packaged | the commit the supplier delta's README names in its header | cut after the adoption; the README states its difference from the tested revision and which checks cover it |
| Reviewed | `4d0ff8a2` (`4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e`) | the candidate the one targeted recheck cx46 read (`records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:8`); its verdict as given: "P0 RECHECK: CORRECTIONS NOT CLOSED." (`:10`), "the second negative on the method, which ends it" (`:3`); unchanged in set 31 and in set 32: no independent check of the engineering read a later revision (`records/int31/RESULT.md`, section 1; `records/int32/RESULT.md`, section 1: "no independent check of its engineering") |
| Earlier reviewed | `06077cee` (`06077cee85d0ed44c74c2a06c9fbb2030a0dedbc`) | the candidate the one focused check cx45 read (`records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md:20`); its verdict as given: "P0 CANDIDATE: NOT CONFIRMED." (`:10`) |

**The reviewed revision is not the packaged revision, and no verdict moves between them by itself.** The records adopted after the promotion (RESULT.md, CLASSIFICATION.md, the P0 list revision 3, the assessment, LAYER-STATUS and these pages) are committed on main after the tested commit, first as adopted in set 30's adoption commit `836f711b` (the Adopted row's dated history) and, for set 31's records, in set 31's adoption commit (the Adopted row's dated history) and, for set 32's records, in set 32's adoption commit (the Adopted row); a page cannot carry the sha of the commit that packages it, so the supplier delta's README.md names the packaged commit (the Packaged row) and states its difference from the tested revision (6 October 2026). Dated note (W33, 6 October 2026): the Packaged row named `dd1aed00` until W32's read of the adoption, which found RESULT.md and these pages' section 0 first in the adoption's commits, not at `dd1aed00`. The owner's binding rule (part 25,
`dd1aed00:v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:845`): "Use the existing integration gate to record the reviewed and integrated
revisions and the intervening changes. If changes are only verified bindings or presentation, record that equivalence. If they change a
circuit, assumption, model, limit or substantive claim, the affected result needs targeted verification before being credited. Passing
the software suite alone cannot transfer an engineering verdict to altered claims." The integration record `records/int30/RESULT.md`
binds `4d0ff8a2` and `dd1aed00d0a0a521063b5792550bc510c4707c59`, and `records/int30/CLASSIFICATION.md` classifies every commit between them. Read each verdict
as applying to the revision its checker read.

**What set 30's promoted revision is, and is not**, in the integration record's words (`records/int30/RESULT.md`, sections 1, 2 and 6):
"a DESK candidate, not an accepted power design"; "Set 30 closes NO power item."; and after cx46 "the promoted revision carries 14 UNREVIEWED CHANGES", "never as checked, never credited, each owing its own targeted verification before any credit" (14 over the 45 commits of `4d0ff8a2..dd1aed00`; 13 of them in W15's range `4d0ff8a2..6bc4424e`). Set 31 adds its own: 25 commits that change what cx46 read or carry another row's change into a file of the reviewed tree (set 30's rule, reading A) over the 106 commits of `dd1aed00..5f25daf3`, each "UNREVIEWED since cx46" (`records/int31/CLASSIFICATION.md`, section 2); the candidate commit `5f25daf3` is one of the 106, that file's row 36. Set 32 adds its own: of the 34 commits of its five branches, 12 touch a file cx46 read, 2 of them REVIEWED-INPUT CHANGED under set 30's rule (reading A), each "UNREVIEWED since cx46" (`records/int32/CLASSIFICATION.md`, section 2), counted over the branch commits alone; the integration's own commits are that file's rows 31 to 33, the candidate commit `f08e3961` its row 33, classed at the adoption (its row 31 expects the regenerated outputs that carry row 14's lines to be REVIEWED-INPUT CHANGED too), unlike set 31's 25, counted over all 106 of its commits.

### 0b. The states, each apart

| What | State |
|---|---|
| Documents and editable artifacts | on main as a DESK candidate (`f08e3961`, set 32) |
| Design reviewed and accepted | NO |
| Implemented | NONE |
| Physical qualification | NONE |
| Fabrication release | BLOCKED |
| Power-design closure | BLOCKED |

The Layer 4 record states five of the six apart: "power-design closure BLOCKED, fabrication release BLOCKED, design accepted NO,
implemented NONE, physical qualification NONE" (`records/l4e9/L4-POWER-ARCHITECTURE.md:965`); every circuit change is a release-guarded
draft: "None is APPLIED" (`:401`). The constitution keeps them apart: "A promoted integration set is none of those by itself."
(`v2/docs/EXECUTION-CONSTITUTION.md:23`). **Two gates, not one.** Layer 4's DESK gate (the owner's part 19: sequential desk acceptance
per layer) is assessed by the coordinator in `records/l4close/L4-DESK-GATE-ASSESSMENT.md`, which records the coordinator's judgement on set 30's
promoted revision, dated 6 October 2026, 10:45 CEST: the gate and the three completion claims of the constitution's section 2, each
apart and in the coordinator's words:

- "Layer 4's DESK gate: NOT PASSED"
- "Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS"
- "Power-design closure: BLOCKED."
- "Fabrication release: BLOCKED."

The readiness word carries its own limit: ""Ready" here means complete and internally consistent as a package of open items, not that any item is resolved." (quoted in `records/int30/RESULT.md`, section 6).
The DESIGN gate, L4-E9's criteria 1 to 5 (`records/l4e9/L4-POWER-ARCHITECTURE.md`, section 8), is a different gate, and its words on
the set 30 candidate are "**Layer 4's power architecture closes: NO**: on the set 30 candidate **the power-design closure gate is
BLOCKED**" (`:1005`), with the coordinator's readings "criterion 1 CONDITIONAL", "criterion 2 FAIL", "criterion 3 PASS", "criterion 4
PASS" and "criterion 5 CONDITIONAL", and "A PASS here is the DESIGN gate's reading of that criterion on the desk package, never a
closure, a qualification or a release." (`:1003`).

### 0c. What set 30 adds to the package

| File | What it is |
|---|---|
| `v2/docs/records/l4close/REMAINING-ENGINEERING.md` | the remaining-engineering ledger: each finding cx46 left NOT CLOSED (its section 1, the RE- items) and each case the authors handed over (its section 2, the HO- items), with the failed cases, the attempted correction, the affected provisional outputs, the receiving company's task and its acceptance; in its own words it "is not an acceptance, a closure, a verdict, a check, a qualification or a release of anything" (`:11`) |
| `v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md` | the supplier validation annex: U-02, the sealed case's heat rejection (section 1); U-04, the charger on the battery FET pair (section 2); U-01, the cell (section 3); E11-29, the three paralleled battery FETs, a qualification kept apart (section 4); each with the claim, the specimen, the measured quantity, the pass limit, the capability and the outputs kept PROVISIONAL |
| `v2/docs/records/l4close/P0-POWER-LIST.md` | the P0 list, the power architecture's current blockers in one table; revision 3, adopted on 6 October 2026, which replaces revision 2 of 5 October 2026, 16:50 CEST (`:1`), kept as `v2/docs/records/l4close/P0-POWER-LIST.rev2-2026-10-05.md` |
| `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`, section 8 | the DESIGN gate's criteria 1 to 5 read on the set 30 candidate, with the gate's words (section 0b) |
| `v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md` | the coordinator's assessment of Layer 4's DESK gate; its contradictions list K-01 to K-28 is the register of known differences between records |
| `v2/docs/handover/LAYER-STATUS.md`, the blocks headed "After set 30" | per layer, the items set 30's records move; a row not listed there keeps its earlier text |
| `v2/docs/records/int30/RESULT.md`, with `v2/docs/records/int30/CLASSIFICATION.md` | the integration record: the reviewed and the integrated revisions bound, every intervening commit classified (the classification), the gate lines |
| `v2/docs/records/int31/RESULT.md`, with `v2/docs/records/int31/CLASSIFICATION.md` | set 31's integration record: set 30's promoted revision and set 31's bound, every intervening commit classified, the gate lines |
| `v2/docs/records/int32/RESULT.md`, with `v2/docs/records/int32/CLASSIFICATION.md` and `v2/docs/records/int32/ENTRY-PAGES.patch.md` | set 32's integration record: set 31's promoted revision and set 32's bound, every commit of its five branches classified and the integration's rows, the gate lines, and the rows that brought these pages to set 32 |
| `v2/docs/records/l4close/CHECK-V6-POWER-DRAFTS-7a82e82a-AS-RECEIVED.md`, `v2/docs/records/l4close/CHECK-CX44-F01-SELECTION-8c7c335f-AS-RECEIVED.md`, `v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md`, `v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md` | the four independent checks of 5 October 2026, each an AI review filed as received, every negative verdict kept |
| `v2/docs/records/l9t5/`, `v2/docs/records/l8r2/`, `v2/docs/records/l8p/`, `v2/docs/records/efuse/`, `v2/docs/records/l4e11/`, `v2/docs/records/l4e7/` | the records the P0 round changed (each with its `README.md`), with their scripts, committed outputs and tests; `v2/docs/records/l9t5/stability/` keeps the cascade's two passes and their digests |
| `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md` | the owner's instructions of 5 October 2026 as received, from part 12 (part 19: the deliverable is the desk package; part 24: an unsupported correction is handed over as remaining engineering; part 25: the binding rule of section 0a) |

The findings ledger of section 3 (`records/l4close/FINDINGS-LEDGER.md`) covers "every rejected collaborator finding of L4-E7 to L4-E13"
(`:1`); the P0 round's findings and their checks are in the P0 list, in L4-E9's section 8e and in the remaining-engineering ledger.

### 0d. What we ask of you, and what we do not

We ask you, as the constitution's section 11 says ("Ask suppliers to confirm engineering scope, responsible personnel, deliverables,
exclusions, cost and schedule. Do not assume ordinary fabrication/assembly includes circuit design or qualification.",
`v2/docs/EXECUTION-CONSTITUTION.md:94`):

1. to confirm the engineering scope, the responsible personnel, the deliverables, the exclusions, the cost and the schedule for the
   work of section 8;
2. to take over the remaining engineering as the ledger scopes it: each RE- and HO- item's task and acceptance
   (`records/l4close/REMAINING-ENGINEERING.md`, sections 1, 2 and 5);
3. to validate the annex's four items, U-01, U-02, U-04 and E11-29, to the specimens, quantities and pass limits it states
   (`records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md`, sections 1 to 4).

Nothing is ordered or funded: "We are not undertaking or funding the physical validation now." (the owner's part 19,
`dd1aed00:v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:471`); "no supplier is assumed engaged" (`dd1aed00:v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:481`); and the annex says "Nothing here is a
request for a requirement change, a purchase, an outside contact, fabrication or energisation." (`records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:10`).

We do NOT ask you:

- to fabricate, assemble or order any board from this package: fabrication release is BLOCKED (section 0b), and the 2026-09 `revA`
  order set is an obsolete earlier generation (section 4, Layer 11);
- to read a desk check, an AI review or a passing suite as sign-off or as qualification (the preamble above; section 0a);
- to run the proposed experiments and procedures unchanged: they are PROPOSED, for you to review and agree before execution (section 8);
- to treat a remaining-engineering item as a qualification-only task (the owner's part 24: "If a correction remains unsupported, hand it
  over as **remaining engineering**", `dd1aed00:v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:787`), or a measured failure of a tested
  arrangement as a change of the owner's requirements ("A thermal failure of the tested arrangement is a design failure, not
  automatically a conflict in my requirements.", `dd1aed00:v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:484`);
- to change a requirement or a fixed constraint of section 2, or to adopt the Saft MP 176065 xtd pack, which is a PROPOSAL under
  investigation ("Distinguish investigating or testing the Saft option from adopting its 4S1P pack. No pack change has been approved by
  this clarification.", `dd1aed00:v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:486`), without the owner's ruling.

### 0e. How to reproduce set 32's figures

From a full git checkout at `f08e3961` (section 7, item 2 says why the ZIP alone does not suffice):

1. **The makers' sheets held back by their terms.** A record that reads one fetches it with its own script (`fetch_held_back.py`, or
   a `fetch_*.py`, section 7 item 2), run from the repository root, for example `python3 v2/docs/records/l9t5/fetch_held_back.py` ("exit 0: present and checked; 3: a mismatch",
   `records/l9t5/fetch_held_back.py:11`); the sheets land in gitignored `held/` folders, are checked by sha256 and are never committed. Where a record reads a held-back sheet as its extracted text rather than as the PDF, that text is held back with the sheet and is re-taken after the fetch, before the record's script runs; section 7, item 2 gives the command and the tool versions it needs.
2. **A record's figures.** `python3 v2/docs/records/<record>/<script>.py` prints the output; compare it byte for byte with the committed
   `.out` beside the script. A record's `README.md` states its own commands, and the ledger's section 7, "Reproducing the records",
   gathers the common ones. The P0 cascade's dependency order is the list in `v2/docs/records/l9t5/stability/regen_cascade.sh`
   (`records/l9t5/stability/regen_cascade.sh:9-11`); that script drives the coordinator's `regen_out.py`, "outside the tree" (`:7`), so
   a recipient runs the same scripts in that order directly. The project's two passes and their digests are filed beside it
   (`records/l9t5/README.md:129-132`).
3. **Netlists without KiCad.** `python3 v2/docs/records/l8p/gen_netlist.py GENERATOR OUT.net` (`records/l8p/gen_netlist.py:5`) writes a
   generator's part table as a KiCad-form netlist; "It is not KiCad's netlist" (`:15`), and KiCad's own export is the reading of record
   (`:17`). A schematic regenerates with KiCad 9.0.9 (`v2/docs/handover/REGENERATE.md`).
4. **Tests.** `python3 v2/ecad/tools/tests/run.py <name substring>` runs the house fixtures; a test that needs `pcbnew` reports SKIP on a
   host without KiCad. The gated release suite's line for `f08e3961` is in the package's `README.md` and in
   `records/int32/RESULT.md` (set 31's, for `5f25daf3`, in `records/int31/RESULT.md`; set 30's, for `dd1aed00`, in `records/int30/RESULT.md`).

## 1. The product

A sealed go-box that keeps a small team connected when terrestrial networks are down: satellite (Iridium RockBLOCK 9704),
cellular (5G module), LoRa mesh (1 W), Zigbee and Thread, Wi-Fi including a kit-to-kit link, VHF APRS with a 30 W PA, HF (a
QMX-class transceiver), a software-defined receiver, multi-band GNSS, a sensor suite, a panel with an e-paper display and a
sunlight-readable monitor, three Raspberry Pi Compute Module 5 slots run as a redundant cluster, and a lid-mounted tablet. One
Peli 1450 case, no vent anywhere (the case stays sealed; internal fans move heat to the face plate and walls), an internal
4S3P Li-ion pack (Samsung INR18650-35E), solar input through an MPPT stage, and a 9 to 36 V vehicle or shore input.

Seven boards (`v2/ecad/tools/readiness_manifest.json`):

| Board | Title | Current schematic and netlist |
|---|---|---|
| A | power and I/O (charger, converters, protection, dock) | `v2/ecad/pcb-a-power-a23/` |
| B | compute (three CM5 slots, PCIe switches, USB hubs, Ethernet switch) | `v2/ecad/pcb-b-compute-b19/` |
| C | control panel backer (RP2040 panel controller, e-paper, toggles) | `v2/ecad/pcb-c-display-c8/` |
| D | APRS and the VHF PA | `v2/ecad/pcb-d-aprs-d9/` |
| E | dock strip (solar MPPT stage, vehicle entry, auxiliary feed) | `v2/ecad/pcb-e1-dock-e7/` |
| E5 | dock block (a bare contact board, no schematic) | `v2/ecad/pcb-e5-block/` |
| P | pack protection and gauge | `v2/ecad/pcb-p-pack-p2/` |

Each schematic is generated by a Python script (`v2/ecad/tools/gen_sch_<board>.py`) and regenerated with KiCad 9.0.9; the
`.kicad_sch`, `.kicad_pro` and `out/*.net` are committed, editable in KiCad, and reproduce from the generator
(`v2/docs/handover/REGENERATE.md`). The `routed/` folders hold EARLIER layout experiments on earlier circuits: they are not a
layout of the current design and not for fabrication.

## 2. Requirements, operating modes and fixed constraints

- **Accepted requirements (Layer 3, accepted twice, last at `3b4b92cf`):** `v2/docs/handover/layer3/REQUIREMENTS-L3-R2.md`
  and the machine-readable `v2/ecad/tools/pcb_requirements.yaml`; the owner's decisions behind them
  `v2/docs/handover/layer3/OWNER-DECISIONS-L3.md`.
- **Operating envelope and modes:** `v2/docs/OPERATING-ENVELOPE.md`, `v2/docs/CONOPS.md` (section 4: the reduced mode, the heat
  stage, the hot stop, lid closed), the test plan `v2/docs/TEST-PLAN.md` (based on MIL-STD-810 and MIL-STD-461G; approved by the owner).
- **Fixed by the owner, not open to the supplier without his ruling:** battery and solar are mandatory; no external battery;
  storage inside the Peli; HF and the tablet stay; the Peli 1450 case at any cost and no vent; the pack arrangement D-06 (4S3P
  Samsung INR18650-35E) is the baseline, other cells are proposals; the solar input window REQ-016; **48 to 72 hours of
  endurance at the approved 42.8 W profile is a design OBJECTIVE, and it is NOT met** (section 5, row P9); optional tablet
  charging reduces endurance.

## 3. The design as it stands, with its maturity

Maturity words used throughout: **ACCEPTED** (reviewed and accepted against its layer's criteria), **SELECTED** (chosen and
recorded, not yet accepted), **DRAFTED** (a circuit change written as a release-guarded apply script against a generator, NOT
applied to the schematic), **PROVISIONAL** (stated with an open condition named), **OPEN** (not resolved).

| What | Where | Maturity |
|---|---|---|
| Architecture overview, diagrams (power tree, power-up, control lines, lanes, case) | `v2/docs/ARCHITECTURE.md`, `v2/docs/diagrams/` (Mermaid sources and PDFs) | drawn on the September netlists; not re-read on the Layer 4 drafts |
| The connected power architecture: one diagram, one budget, the change list in application order, operating and fault behaviour, the qualification route, the exit statement | `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`, `L4-POWER-DIAGRAM.svg`, `DOWNSTREAM-REGISTER.md` (every downstream item with one owner and an acceptance) | SELECTED candidate, CONDITIONAL; power-design closure BLOCKED (section 5) |
| The records behind it, one per question, each with its script, output and test | `v2/docs/records/l4e4/` to `l4e13/` (charger limits, source control, fault handling, the solar stage, the bank, the cells and heat, source-only operation and the entry, the electronics against the inside air, the panel) | each record's own state; drafts not applied |
| Every review finding and its state | `v2/docs/records/l4close/FINDINGS-LEDGER.md`; the collaborator's checks under `records/*/checks/`; the owner's external reviews `records/l4close/REVIEW-*-AS-RECEIVED.md` | the ledger is the authority on what is closed |
| Interfaces and the hardware/firmware contract | `v2/ecad/tools/pcb_interfaces.yaml` (30 contracts), `v2/docs/HW-FW-CONTRACT.md`, `v2/docs/PANEL.md`, `v2/docs/GROUNDING-AND-SHIELDS.md` | Layer 5's power pass and its second pass are on branches (section 4, the delta) |
| Schematics and netlists | section 1's table | generated, ERC per board, regeneration parity on KiCad 9.0.9; the Layer 4 and Layer 8 drafts are NOT applied |
| Parts | `v2/ecad/tools/pcb_part_identities.yaml`, `v2/vendor/SOURCES.yaml`, `v2/docs/parts/PROCUREMENT.md`, the power parts' record (Layer 6, section 4) | partial: no MPN on most passive rows; the power parts identified with document revisions |
| BOM per board | generated in this package from each committed netlist (`bom/<board>-bom.csv`, NOT_FOR_FAB) | a reading of the netlist; drafted changes not in it |
| Mechanical | `v2/cad/` (Python CAD scripts, build123d), `v2/release/case-2026-09-27/` (the case release C1 to C6), `v2/docs/CASE-MARGINS.md`, `CASE-FIT-UNCERTAINTIES.md`, `ASSEMBLY.md` | case geometry released as a prototype drawing set; the fit mock-up not built |

## 4. Layer by layer: what is done, what is outstanding, who does it

The project works in layers with fixed acceptance criteria (`v2/docs/handover/LAYER-STATUS.md`, the per-item rows; its rows for
Layers 4 to 9 date from the September handovers and are brought forward by the records named here). "Supplier" means work this
package asks you to quote for (section 8); "owner" means a decision or purchase only he can make.

| Layer | Done | Outstanding | Depends on | Responsible |
|---|---|---|---|---|
| 1 Product definition | COMPLETE | none | none | owner |
| 2 Concept of operations | COMPLETE | none | none | owner |
| 3 Requirements | ACCEPTED (`3b4b92cf`) | none | none | owner |
| 4 System architecture | the power architecture selected and documented end to end; the qualification route | power closure (section 5); whole-system items still open: lane budgets with margin (4.9), mass and cost (4.11), EMCON, ZEROIZE and failover feasibility (4.13 to 4.18), the architecture review (4.19) | section 5's rows; the review | us (documents), supplier phase 1 (review), supplier phase 2 (measurements) |
| 5 Interfaces | power contracts (46 entries, 21 PROVISIONAL with their triggers); the SLOT_EN hold and GND-002's four board changes DRAFTED | the eight older contracts' full fields (running), board B's partition (5.1), the remaining sequencing and line states | Layer 4's provisional rows | us; supplier phase 1 reviews |
| 6 Components | 28 power parts identified with document revisions, grades, prices, alternatives and their qualification obligations | exact MPN for most passive rows; footprint verification; the parts' review | Layer 8's application | us; supplier phase 3 for the full BOM |
| 7 Mechanical | the case release (C1 to C6); fans selected (Sanyo Denki San Ace, IP68, -20 to +70 C); the heat-test mock-up specified with its bill | the fit mock-up, the fan mounting, the pack hold-down, the strap and lug picks | purchases (owner) | us; supplier phase 2 builds the mock-ups |
| 8 Schematics | six boards generated with parity; every Layer 4 and Layer 8 change drafted against its generator with composition proofs | APPLY the drafts in the change list's order, regenerate, ERC, cross-board checks; the change list names the changes that still need a draft | Layer 4's release guards; section 5's design corrections | supplier phase 1 corrects, phase 3 completes (or us under phase 1's findings) |
| 9 Pre-layout analysis | per-board constraint sheets and the earlier SI, PWR and return-path readings | analyses re-run on the applied circuit | Layer 8 | us and supplier phase 3 |
| 10 Layout | NOT STARTED for the current circuits (the `routed/` folders are earlier experiments) | per board, once its schematic, stackup, interface and mechanical entry gates pass | Layers 5, 7, 8, 9 | supplier phase 3 |
| 11 Manufacturing and assembly | NOT STARTED (the 2026-09 `revA` order set is an obsolete earlier generation) | from the validated revision only | Layer 10 | supplier phase 3 |
| 12 Firmware, bring-up, test | the contract (`HW-FW-CONTRACT.md`), the panel duties (`PANEL.md`), the bring-up page (`PCB-BRING-UP.md`), the test plan | the panel controller's firmware; the bring-up and test procedures run on hardware | prototypes | us (firmware), supplier phase 2 (measurements) |

## 5. The decision-critical power questions

**Selected power-architecture candidate. Known design defects and qualification gaps remain open. Changes are drafts, not an
implemented or qualified circuit. Power-design closure and fabrication release are blocked.** Rows P1, P2 and P8 are design
DEFECTS of the drafted circuit that need a supported circuit correction (P1 and P2) or an actual supply change with its
consequences verified (P8); they are not missing bench evidence for an otherwise finished design. Row P10 is a design defect too.
Rows P3 to P7 are qualification gaps or design choices resting on unprinted or unmeasured facts. Row P9 is an objective shortfall. The collaborator's targeted
recheck of this candidate read NOT YET (`records/l4close/checks/astra-check-l4close-2.md`); later corrections rest on the
coordinator's checks, which are labelled as such and are not an independent review. The
rows below are the ones a reviewer should start with; each names its record.
**History, 3 October 2026.** This paragraph and the table under it are this page's text of 3 October 2026, kept as written. On set 30
the table after it, "Set 30: where each row stands", gives each row's state from its record and governs where they differ; the
collaborator's recheck that read NOT YET is history, and the P0 candidate's own checks are cx45 and cx46 (section 0a).

| # | Circuit or function | Evidence and the failed or uncertain condition | Proposed correction or experiment | Acceptance criterion | Affects |
|---|---|---|---|---|---|
| P1 | Board E's solar input guard (U21 TPS48110-Q1 cut-off, Q12/Q13, D4, the sense resistor RSENSE1 into the LT8705A U5) | A stiff 36 V source arriving with the guard already on: at a fault AT THE CONNECTOR (no lead resistance) and a 3.30 uH reference loop the LT8705A's sense pins reach **-0.3021 V, past the -0.3 V absolute maximum**; INP 18.29 V over its 18 V margin line; PV_F 83.47 V over the TPS4811-Q1's recommended 80 V row; D4's cold-connection ring misses its margin lines near 0.30 uH. No passing inductance was found; three alternatives were tried (`records/l4e7/L4E7-CONTROL-DECISION.md`, B6 rounds 2 to 5, handoff B6-ENG-1) | Rearrange the stage's input current sense and guard so the sense pins are independent of the source loop (B6-ENG-1's three routes: a maker-permitted sense filter, a controlled source loop at J_SOLAR, the sense moved off the input capacitance), or a different protection topology | U5's sense pins within +-0.240 V at the IC pins over the declared envelope (stiff 36 V, loop 0.30 to 10.2 uH, fault at the connector or the lead's far end); PV_F under 80 V; INP under 18 V; measured on board E's first prototype | board E's schematic; fabrication release |
| P2 | The same stage in normal operation | The drafted sense exceeds the LT8705A's +-100 mV operating range at the 25 V corner (resistive peak 0.1174 V); the monitor's error is MODELED at +7.9 % at the regulation's current (the input limit regulates below its setting) and -10.2 % at the trip, on a clipping model the sheet does not print (D-16, B6-ENG-2) | as P1 (the same rearrangement); Analog Devices question 7 (drafted) | the sense within +-100 mV in operation over the panel window; the regulation error measured (R-189) | board E; the solar stage's regulation |
| P3 | Board A's battery switch Q39/Q40 (two Nexperia BUK6Y10-30P under the TI BQ25730's BATDRV) | RDS(on) at the -8.5 V drive and hot is not printed (21.136 mOhm is an allowance); the installed transient coupling; Ciss is printed typical only, 4.72 nF for the pair at -15 V, about 5.74 nF near 0 V, against TI's "below 5 nF" (OPEN); the 242.9 A, 33.8 us docking inrush taken in one FET (`records/l4e11/` sections 16, 17b, 17d) | the specimens of section 6 (E11-29, E11-30, E11-36, E11-37); or one FET with a heat path through the case; or a precharge or slew limit on board P | RDS(on) at most 21.136 mOhm at -8.5 V and 150 C; self-plus-mutual impedance at most 33.12 / 10.753 / 3.785 / 0.703 K/W; BATDRV regulates without oscillation; the six-sample pulse test passes | board A |
| P4 | The auxiliary feed to board E over one dock contact (TI TPS16630 eFuse U42, R228 11.0k) | Sustained overload is bounded (limit 1.471 to 1.802 A, at most 51.5 % of the contact's 3.5 A); the fault envelope is not: the 566 A short peak is an extrapolation, the start into a short has no printed total duration, intermittent shorts are open (`records/l4e11/` 17a, E11-38) | bench E11-38 cases (a) to (h) | the limit inside 1.471 to 1.802 A; the contact at or under 85 C and its resistance within +10 %; the IN pin at most 60 V | boards A and E |
| P5 | Source-only start and held states on the BQ25730 (U-04) | The first start with no usable pack is not bounded by printed figures; the held pack current through the body diodes is unprinted (E11-31; TI questions Q-TI-15, 16, 17, 18 drafted) | bench E11-31 on the first board A; TI's answers | VSYS at or over 12.054 V with no pack; the held pack current at or under 1 mA; the start succeeds at every corner | board A's charger release |
| P6 | Heat rejection of the sealed case (U-02) | A conservative bound of 0.566 to 0.673 W/K lid open (fans' airflow credited at zero) against lines of 1.447 W/K (the profile at +20 C) up to 2.025 to 2.525 W/K (charging while running); the SGP41's lid-closed line is a modelled shortfall of the analysed arrangement; the e-paper's unpowered storage at +70 C is unqualified (`records/l4e12/`) | T-H1 on an empty-case mock-up with the frame, plate, fans and dummy heaters (`records/l4e12/T-H1-PROCEDURE-DRAFT.md`, the bill in Layer 7's record); the e-paper soak at +70 C on the glass | per point, G_measured - U_G >= G_required, with U_G the expanded (k = 2) uncertainty in W/K (the procedure's section 6 prints each mode's need and the reading that passes once U_G is taken off: M2 as ruled needs 2.709 W/K and passes at a reading of at least 3.081 W/K); example: a 2.0 W/K need, a 1.9 W/K reading and a 0.1 W/K uncertainty give a lower bound of 1.8 W/K, a FAIL; the soaked sample functional | the thermal design; the test plan's E3 and E5 rows |
| P7 | The cell (U-01) | The ruled 35E's printed limits do not cover the +71 C and -33 C storage rows; a Saft MP 176065 xtd route is a PROPOSAL (temperature windows supported, current at temperature, storage recovery and fit awaited) (`records/l4e10/`) | Saft's answers or a one-cell qualification; the fit mock-up (R-167, which blocks only the proposal's adoption) | as the record states; the owner's approval for any cell change | the pack, board P |
| P8 | Board B's fans | Board B's fan headers carry 5.1 V; the selected 12 V fans need 10.8 to 13.2 V (E11-40, R-190: a draft is owed) | a 12 V feed on board B: DRAFTED as a per-slot step-up (TPS61089 with a TPS259631 per slot; record l8r2, in the package's `branches/`, integrating in the next set); the supplier reviews the draft | the coolers' window met | board B |
| P10 | Board A's VBUS20 against the 20 V bus converter's single faults (S-111) | A Q2 short or an FB open puts VIN_RAW on VBUS20, past U3's 32 V, with no clamp and no exemption claimed (register R-48, a KNOWN DEFECT) | DRAFTED: a series cut-off at board A's VIN_RAW entry (CSD19532Q5B under a TPS48110-Q1, its over-voltage window on VBUS20 24.25 to 25.31 V; the SMCJ22A rejected because its breakdown sits inside the 9 to 36 V service range); record l8r2 in the package's `branches/`; the supplier reviews the draft (task P1-3) | U3's input under its absolute maximum through each single fault | board A |
| P9 | Endurance (an objective, not a defect) | Battery-only 2.52 h on energy alone at 42.8 W (the case sheds the profile at 2.01 to 2.51 h on the thermal bound); solar-assisted, the 48 and 72 h horizons carry 8.0 W steady | none within the fixed constraints today: any change of the profile, the storage or the objective is the owner's decision; a supplier may propose architecture options | the owner's | the claim made for the kit |

**Set 30: where each row stands** (6 October 2026; quoted from the records in section 0's citation form; the P0 round's own rows,
P0-1 to P0-8 with U-01, U-02, U-04 and E11-29, are the P0 list's, section 0c).

| Row | State on set 30, in its record's words | Where |
|---|---|---|
| P1 | "D-10 is OPEN, an UNRESOLVED PROTECTION DEFECT in the present model, the receiving company's remaining engineering item E-1"; the ledger carries it as HO-F | `records/l4e9/L4-POWER-ARCHITECTURE.md:37`; `records/l4close/REMAINING-ENGINEERING.md`, section 2 |
| P2 | "D-16 is ADDRESSED IN DRAFTS: corrected in draft by P0-7 (R-240, not applied;" and "PROVISIONAL in A7's zero-differential output (S3) and in the regulation at 25 V (S4)" | `records/l4e9/L4-POWER-ARCHITECTURE.md:37` |
| P3 | "the battery FETs, R-157 with Q42 since L4-E11's round 9 (R-209)"; "D-14 CONDITIONAL on E11-29, E11-30 and E11-36 with the three's Ciss against TI's 5 nF OPEN, E11-37"; E11-29 is the annex's qualification item | `records/l4e9/L4-POWER-ARCHITECTURE.md:37`; the annex, section 4 |
| P4 | "the eFuse U42, R-181, 1.4713 to 1.8018 A, sustained-overload remedy drafted; fault qualification open, E11-38" | `records/l4e9/L4-POWER-ARCHITECTURE.md:37` |
| P5 | U-04, an architecture-level item of the receiving company's validation scope | the annex, section 2 |
| P6 | U-02, an architecture-level item of the same scope | the annex, section 1 |
| P7 | U-01, an architecture-level item of the same scope; the Saft MP 176065 xtd stays a PROPOSAL (section 0d) | the annex, section 3 |
| P8 | superseded on 4 October 2026 by the addendum (`v2/docs/handover/supplier/CURRENT-STATE-ADDENDUM-d834e6a7.md:33`); drafted, not applied: "board B's coolers on a per-slot 12 V step-up with an eFuse (E11-40, R-190)" and "Set 29: board A's slots 1 and 3 on slot 2's LM5176 stage with the coolers at full speed (L9P-F02, `apply_gen_sch_a_slotlm.py`)" | `v2/docs/handover/LAYER-STATUS.md:476` |
| P9 | "The objective of 48 to 72 h is NOT MET" | `records/l4e9/L4-POWER-ARCHITECTURE.md:38` |
| P10 | its `branches/` wording superseded on 4 October 2026 (`v2/docs/handover/supplier/CURRENT-STATE-ADDENDUM-d834e6a7.md:34`); drafted, not applied: "VBUS20's over-voltage cut-off in VIN_RAW (S-111, R-48)" | `v2/docs/handover/LAYER-STATUS.md:476` |
| section 10's L9P-F01, the all-transmit case | "D-17, decision D-11's all-transmit basis on the final drafts (Layer 9's L9P-F01), is OPEN"; "round 7's raised floor is withdrawn as a correction (it narrowed the requirement)"; "round 8's fan design-out (R-210 to R-212) is WITHDRAWN (FAN_OK rejected)"; its correction, the PA drain-current cap, "with cx46 item 2 NOT CLOSED (remaining engineering RE-2)" | `records/l4e9/L4-POWER-ARCHITECTURE.md:37`; the ledger, section 1 |

**Every open item, classified.** `records/l4e9/L4-POWER-ARCHITECTURE.md` section 8f gives each open register item and design
row exactly one class (KNOWN ENGINEERING DEFECT, PHYSICAL UNCERTAINTY, UNCERTAIN DESIGN CHOICE with its one bounded comparison,
or SETTLED WORK) and its next action; section 8g is the task list this package asks you to quote for: phase 1 the design
corrections P1-1 (the solar input's guard and sense: P1, P2), P1-2 (board B's 12 V fan feed: P8) and P1-3 (VBUS20: P10); phase 2
the experiments, the first prototype's verification rows and the makers' statements to obtain or replace by measurement.

Where a row cites a measurement, the measurement is evidence for its specimen, lot and conditions only, and it transfers to
the final kit only under the rule its specimen row states (section 6).

## 6. Specimens, procedures, instruments, and what transfers

The full table is `records/l4e9/L4-POWER-ARCHITECTURE.md` section 5d ("The prototype qualification route", 14 experiments:
specimen, what it represents, what transfers, the decision it resolves, what it blocks, the performer type, the authorisation
needed), with each board A specimen's own block in `records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md` section 17d (lot, operating
point, mounting, thermal boundaries, uncertainty, permitted extrapolation, the comparison rule, the re-test triggers). The
thermal procedure is `records/l4e12/T-H1-PROCEDURE-DRAFT.md` (sixteen channels, the run order, the endpoint, the reduction and
the pass lines). Two rules bind every result: **an evidence build is separate from the final release** (a coupon, an evaluation
board or a controlled first prototype may be built to supply evidence; the design and production release stay held until the
measurements pass), and **a sample measurement is not a component guarantee** (it stands for the tested lot and conditions; a
coupon's thermal result transfers only where the final board's thermal boundaries are each no worse, justified, never from
copper area alone).

## 7. How to check the claims

Three levels, and what each needs:

1. **Directly from the ZIP (no tools beyond a text reader, a spreadsheet and KiCad 9):** every record's page and its committed
   output (`<record>/<script>.out`, the figures the page quotes), the register, the interface contracts, the schematics and
   netlists (open in KiCad 9.0.9), the BOMs, the mechanical sources and the case drawings, the test procedures. A reviewer can
   check every claim against the printed output and the cited maker document from here.
2. **Re-computing a record's figures needs a full git checkout at the exact commit, not this ZIP.** The records' scripts locate
   the repository with `git rev-parse --show-toplevel` and several read earlier committed versions of their inputs with
   `git show <commit>:<path>` (for example `v2/docs/records/l4e9/l4e9_power_path.py`); they refuse when a pinned input differs.
   They also read makers' documents that are not redistributed: each record's `fetch_held_back.py` (or `fetch_*.py`) fetches them
   from the makers' sites into ignored `held/` folders and checks their sha256 (`SOURCES-HELD-BACK.md` lists them). The records
   read a maker's PDF as its extracted text, a committed input beside the PDF (`v2/docs/records/_lib/pdftext.py`), never by running
   `pdftotext` themselves; a held-back sheet's text is held back with the sheet, so after the fetch it is re-taken:
   `python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/<record>`, on a host with poppler's `pdftotext` 22.12.0 and the
   `poppler-data` package (the versions every text was taken with; each text's `.meta.json` sidecar names them), before the record's
   script runs. A record whose text is absent refuses and names the fetch script and this command; the fetch script is not always
   the reading record's own. The committed outputs print each text's sha256, so a text taken with another poppler makes the output
   differ from the committed `.out` and the records that pin that output refuse it: a refusal, not a silent change. Then
   `python3 v2/docs/records/<record>/<script>.py` prints the output byte for byte and `python3 v2/ecad/tools/tests/run.py
   <module>` runs the tests (Python 3.11, PyYAML, numpy, poppler's `pdftotext` for some readers). The schematics regenerate from
   their generators with KiCad 9.0.9 in a full checkout (`v2/docs/handover/REGENERATE.md` describes the September handover
   formats; the generator command per board is unchanged).
3. **How to get that checkout.** The repository is public (`https://github.com/meshsat/meshsat-fieldkit`). The package's
   `SOURCE.txt` names its commit; from a RELEASE-CANDIDATE package that commit is on the public main branch: `git clone`,
   `git checkout <commit>`, the records' fetch scripts, then the commands above. Work carried in the package's `branches/`
   folders is NOT on that commit (it integrates in the next set): it can be read, is not covered by the release suite's results,
   and can be re-computed only once it is published. **History, 3 October 2026:** superseded on 4 October 2026 by the addendum
   (`v2/docs/handover/supplier/CURRENT-STATE-ADDENDUM-d834e6a7.md:35`): the package carried no `branches/` folder.
4. **What the project tested, at which commit and how** (corrected after the release-candidate review of 3 October 2026,
   finding L4-RC02). The package's `README.md`, section "What was tested, and how", names the commit the gated release suite
   ran on and the packaged commit. When they are the same commit it says so; when they differ it lists every file changed
   between them and the checks that cover those changes. The suite runs every record's script afresh and compares its output
   byte for byte, with one exception: L4-E7's solver is not re-run in the suite. The suite validates L4-E7's committed results
   cache (a KEY over its source, the files it read, its document scans, the solver and the tool versions) against the tree and
   renders the committed output from it; a fresh solver run is the opt-in test `t_recompute_reproduces_the_committed_output`
   (`L4E7_RECOMPUTE=1`), and the cache is written by a full recompute on the integration line. All of this is the project's own
   check. A recipient's numerical replay has not been verified by anyone outside the project; the release-candidate review
   states it as unverified.

## 8. What we ask a supplier to quote for

1. **Design review and correction:** review the architecture, the circuits, the protection and the thermal feasibility; return
   prioritised findings and corrected editable files, or a scoped proposal to complete the corrections.
2. **Prototype qualification:** select suitable evaluation hardware, test coupons or first prototypes; build the fixtures; run
   the agreed tests (section 6); return measurements with their conditions, uncertainty and pass or fail.
3. **Design completion and manufacturing release:** finish the contracted schematic, mechanical, layout and manufacturing work;
   verify the final revision and repeat the affected qualification tests where design changes invalidate earlier evidence (a
   coupon's result does not qualify a changed production layout); return the revised sources and a release recommendation that
   states any remaining qualification.

Phases 1 and 2 include the circuit, layout and fixture work needed to build suitable test specimens. The experiments of
section 6 are PROPOSED procedures for the supplier to review and agree before execution, not instructions to run unchanged.
Estimates for phases 2 and 3 may be indicative and conditional on phase 1's findings, with the assumptions stated.

We ask for electrical design and qualification work beyond ordinary fabrication and assembly checks. Where a task is outside
your services, please say so and name a partner if you have one; we will not assume it is included.

## 9. What this package leaves out

- Git history (clone the public repository for it); earlier generations of the boards, their order sets and renders; the
  `routed/` layout experiments of earlier circuits.
- Makers' documents whose terms forbid redistribution (listed by URL and sha256 in the records' fetch scripts and in
  `SOURCES-HELD-BACK.md`); the makers' CAD under `v2/vendor/` (in the repository, large).
- The September battery review packet (`v2/docs/review-packets/battery/`) keeps its own revision and describes the charger and
  pack integration as of 26 September 2026, before the BQ25730 selection; it is not evidence for the current integration.
- Anything not committed on the named commit, including work running on branches when the package was cut (the package's
  README names those branches and their tips). The parenthesis is history of 3 October 2026, superseded on 4 October 2026 by the
  addendum (`v2/docs/handover/supplier/CURRENT-STATE-ADDENDUM-d834e6a7.md:36`): the README names the later findings, not branches.

## 10. Changes since the release-candidate package (the delta)

The release-candidate review of 3 October 2026 (`v2/docs/records/l4close/REVIEW-SUPPLIER-RELEASE-CANDIDATE-AS-RECEIVED.md`)
read the package cut from `761677ca` READY for an initial supplier engineering review and quotation, with power-design
closure and fabrication release BLOCKED. Its two findings, and the two later findings it asked to see, stand as follows. A
known circuit defect stays OPEN until it is corrected and verified; an unsuccessful design-out attempt does not turn a defect
into a measurement gap.

| Finding | What it is | State at this package | Where |
|---|---|---|---|
| L4-RC01 | L4-E7's sentence-keyed panel-lead scan let an approved sentence exempt a second, unreviewed statement in the same table cell | The scan is replaced by a numeric guard: every panel-lead length stated in the design documents is compared with the derivation's input (a1solar's 5 m) and a differing one refuses. Preserved review texts are skipped only when named with their sha256 in `v2/docs/records/ARCHIVED-REVIEWS.yaml`; any other file is scanned whatever its name. The reviewer's same-cell counterexample is a regression test. The register row's state is the integration's (R-197) | `v2/docs/records/l4e7/`, `v2/ecad/tools/tests/test_l4e7.py`, register R-197 |
| L4-RC02 | The replay wording did not identify the tested revision and the execution mode | Section 7 item 4 above and the package's README name the commit the gated release suite ran on and the packaged commit, list any file changed between them, and keep L4-E7's cached render apart from a fresh solver run. CLOSED | register R-198 |
| L9P-F01 | Layer 9's power budget: D-11's all-transmit basis needs a 15.99 V rest voltage on the drafted design, 0.49 V over its 15.5 V floor (the battery FET pair adds 0.190 V, the fans and their converters at full speed 0.458 V) | **History, 3 October 2026; the 16.1 V floor WITHDRAWN on 4 October 2026** (`v2/docs/handover/supplier/CURRENT-STATE-ADDENDUM-d834e6a7.md:38`; set 30: section 5, the last row of "Set 30: where each row stands"). A demonstrated analysis defect, OPEN. A correction is drafted on a branch that is not part of this package's commit (L4-E9's round 7): the floor rises to 16.1 V rest from the release that applies those drafts (+0.114 V), the all-transmit window shrinks from 1.384 V to 0.784 V of rest voltage, and the firmware contract owes the matching FW-A05 sentence. Not reviewed, not integrated | the next integration set |
| L9P-F02 | Layer 9's power budget: the drafted per-slot cooler step-ups take slots 1 and 3's AP64500 to 5.010 A against its 5 A at the highest bound | **History, 3 October 2026; the 70 % cap WITHDRAWN on 4 October 2026** (`v2/docs/handover/supplier/CURRENT-STATE-ADDENDUM-d834e6a7.md:37`; set 30: section 5, row P8 of "Set 30: where each row stands"). A defect in a draft, OPEN. A correction is drafted on a branch that is not part of this package's commit (Layer 8's round 3): the per-slot step-up stays with each cooler fan's PWM capped at 70 % by a firmware rule (+0.129 A at the worst state), a 12 V feed per slot as the fallback; the firmware contract owes the cap's row. Not reviewed, not integrated | the next integration set |

The two later rounds also expose findings for the next set (the stackup record's copper widths at 1 oz against the 25 A
coordination, the device rail's 7.181 A against 7.096 A as before); they are carried in those rounds' records and are open. The
device rail's figure is history of 3 October 2026: the addendum of 4 October 2026 states I-03 at 7.472 A against its 7.0957 A loop
minimum (`v2/docs/handover/supplier/CURRENT-STATE-ADDENDUM-d834e6a7.md:44`).

**Later entries, dated** (each is history once a later entry stands; the newest is last).

- **4 October 2026: the current-state addendum to the package cut from `d834e6a7`** (`v2/docs/handover/supplier/CURRENT-STATE-ADDENDUM-d834e6a7.md`, revision 3). It
  supersedes the rows of this page that its section 2 lists (`:27-38`), among them L9P-F01's 16.1 V
  floor ("WITHDRAWN", `:38`) and L9P-F02's cap (`:37`). The package's review reads "READY for an initial supplier engineering
  quotation, accompanied by a short current-state correction sheet. Power-design closure and fabrication release remain BLOCKED."
  (`v2/docs/records/l4close/REVIEW-SUPPLIER-D834E6A7-AS-RECEIVED.md:11`); the review of the addendum's revision 2 is
  `v2/docs/records/l4close/REVIEW-SUPPLIER-ADDENDUM-REV2-AS-RECEIVED.md`.
- **4 October 2026: the delta `aa76c894` over `d834e6a7`** (set 29). Its review reads "READY for supplier engineering review and
  quotation, with this review attached. Power-design closure and fabrication release remain BLOCKED."
  (`v2/docs/records/l4close/REVIEW-SUPPLIER-DELTA-AA76C894-AS-RECEIVED.md:5`); its two P1 findings, DELTA-01 and DELTA-02, are mapped in
  `v2/docs/EXECUTION-PLAN.md`, "Register additions, 4 October 2026 21:05 CEST".
- **6 October 2026: set 30, the revision `dd1aed00d0a0a521063b5792550bc510c4707c59`** (section 0). The P0 power candidate after cx46: the findings cx46 left NOT
  CLOSED and the cases the authors handed over carried as remaining engineering (`v2/docs/records/l4close/REMAINING-ENGINEERING.md`),
  U-01, U-02, U-04 and E11-29 in the supplier validation annex, the P0 list, the DESIGN gate's reading ("closes: NO",
  `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:1005`) and the DESK-gate assessment kept apart from it. No circuit change is applied, and nothing in it accepts, closes or promotes a design claim.
- **6 October 2026: set 31, the revision `5f25daf3`** (section 0). An adoption of record text over set 30: the authors'
  restatements written during set 30's integration, the filed patch rows applied, the citations re-taken, regenerated to convergence
  (`v2/docs/records/int31/RESULT.md`). No circuit change is applied, and nothing in it accepts, closes or promotes a design claim;
  Layer 4's DESK gate and the three completion claims stand as set 30's assessment gives them.
- **Set 32, the revision `f08e3961`, dated by its adoption commit** (section 0). An adoption of record text and record tooling
  over set 31: the makers' PDF text as committed verbatim inputs of 26 record generators (a held-back sheet's text held back with the
  sheet and re-taken after the fetch: 57 texts), the verdict words attributed to their checks, the ZIP's cap, N1a's phrase in V-E16
  row 3, record l4e7's cache KEY on the sixteen numbers it reads, ONE re-key, regenerated
  (`v2/docs/records/int32/RESULT.md`). No circuit change is applied, and nothing in it accepts, closes or promotes a design claim;
  Layer 4's DESK gate and the three completion claims stand as set 30's assessment gives them.
