<!-- Filed by the integrating session on 27 September 2026 (MESHSAT-1357) from the checker's own working folder, byte for byte below this line (sha256/16 of the checker's file: d31614bf871e5346). The checker worked from its own extraction of H3.zip and the dependencies the package declares, in workflow run wf_7bec9c82-e4c. An AI check, never a qualified engineering review. -->

# AI check

## Usability check of handover snapshot H3, MeshSat field kit V2 (MESHSAT-1357)

**This is an AI check. It is not a qualified engineering review, and it judges usability, not whether any circuit,
requirement or calculation is right.** The checker built nothing of H3 and wrote none of its pages. Nothing of this
kit has been built, ordered or measured.

| Item | Value |
|---|---|
| Package | `H3.zip`, 52,187,825 bytes |
| sha256 | `6922a96d732442e99a65d8db3f0734378bd7ea636894fca283a4b3ca424dd07a` |
| Commit (`SOURCE.txt`, `commit:`) | `75ad6ee5bc98d7213b9a61d1f64cfa7ea19cc669`, of `https://github.com/meshsat/meshsat-fieldkit` |
| Date of this check | 27 September 2026, 21:20 to 21:45 UTC (`date -u`: Sun Sep 27 09:40:24 PM UTC 2026 when this record was written) |
| Working folder | `/home/claude-runner/worktrees/meshsat-fieldkit/_h3check/usability` (extraction `H3/`, scratch copies under `work/`) |
| KiCad host folder | `/root/h3check-usability/`, removed at the end; nothing of this check is left running there |
| Hosts | this host: Python 3.11.2, PyYAML 6.0.3, no KiCad. KiCad host: Ubuntu 24.04, KiCad 9.0.9 (`kicad-cli` and `pcbnew`), Python 3.12.3, PyYAML 6.0.1, Pillow 10.2.0 |

**Result in one sentence.** H3 is usable as it says for route A (read and continue) and route B (the calculation and
one schematic reproduced, every command of the page working as written with `H3` read for `H2`); route C is stated
as not expected to pass from the ZIP and the measurement agrees; I found no blocking defect and fifteen minor ones.

**The rule I worked under.** The package and its declared dependencies alone: the ZIP, its `.sha256`, the public
repository at commits `SOURCE.txt` marks public (section 1a's fetch, and one file of my own choosing named below),
Python modules and KiCad 9.0.9 on the rented host. I did not read the project's working repository, another worktree,
the tracker or any memory file.

## 1. What I read

- In full: `START-HERE.md`, `REGENERATE.md`, `v2/docs/handover/RELEASE-H3.md`, `SOURCE.txt` (head, timeline, tail).
- `LAYER-STATUS.md`: lines 1 to 170 (head, "Status at handover H3", "Status at handover H2") and the acceptance
  tables of layers 1 to 3 (lines 241 to 297). Appendix A (history) was not read.
- `CONTINUATION-BRIEF.md`: lines 1 to 337 (sections 0, 0a, 1, 2, 3, 4, 5.1) and its FEA-007 lines.
- `ENGINEERING-QUESTIONS.md`: head, index, and the blocks EQ-25, EQ-08 and EQ-10 in full.
- `v2/docs/EXECUTION-PLAN.md`: head, the stage gate table (lines 127 to 160), the checkpoint of 27 September 23:02.
- `v2/docs/CONOPS.md` head and section 4; `v2/docs/CURRENT-EVIDENCE.md` head and its FEA-007 rows;
  `v2/docs/REQUIREMENTS-TRACE.md` head; `v2/docs/layout-constraints/README.md`, `A.md` (head, sections 1, 2, 7),
  `P.md` (head, sections 1, 2), `E.md` and `E5.md` (heads and dock rows); `v2/docs/records/w3t/HANDOFF.md` section 2;
  `v2/docs/handover/candidates/README.md` head.
- By script: `v2/ecad/tools/pcb_requirements.yaml`, `pcb_interfaces.yaml`, `pcb_decisions.yaml`, `pcb_rules.yaml`
  (REL-001), `boards/<x>.json` (`external_ports`), the six committed netlists, `MANIFEST.tsv`, `EXCLUDED.tsv`,
  `REFERENCED-SOURCES.tsv`.

## 2. What I ran, with the exact result

### B. Verifying the package

| Command | Result |
|---|---|
| `sha256sum -c H3.zip.sha256` | `H3.zip: OK` |
| `python3 v2/ecad/tools/handover_pack.py verify .` (from `H3/`) | `handover_pack: verify .: OK` |
| `python3 H3/v2/ecad/tools/handover_pack.py verify H3.zip` | `handover_pack: verify H3.zip: OK` |
| `python3 v2/ecad/tools/sch_prov.py read v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net p` | `sch_prov: pcb-p-pack.net was written by this tree's own generator (ee62fdb195a9f217)` |
| my own script: `MANIFEST.tsv` rows against the files on disk, sha256 of every file | 2274 rows, 2275 files on disk, the one file not in the manifest is `MANIFEST.tsv` itself; 0 sha256 mismatches; `unzip -l` reads 2275 files, 108,055,561 bytes |
| four hashes I picked, `sha256sum` against the manifest row | `v2/ecad/pcb-a-power-a23/out/pcb-a-power.net` `da05dc02...32e01`; `v2/docs/PRODUCT-BRIEF.md` `85513b92...0e4c`; `v2/ecad/tools/pcb_requirements.yaml` `6eb35694...392d`; `v2/docs/handover/RELEASE-H3.md` `f23cbd8e...4624`: each equal to its row |
| root handover pages against `v2/docs/handover/` copies, `cmp` | the six are byte-identical |

`SOURCE.txt` counts agree: included 2265, plus 6 root pages and 4 generated files, is 2275.

### C. Route B, the representative calculation (this host, a second extraction under `work/calc/`)

As `REGENERATE.md` section 6 is written, `HO` the extraction:

1. `cd "$HO/v2/ecad/tools"; VERDICT_DIR="$HO/../verdicts" python3 energy_chain.py --ecad ..` printed
   `energy_chain: 12 stage(s), 98 check(s)`, fifteen `note` lines (the three the page quotes among them, word for
   word), one finding `FAIL DOCK_BLOCK: the conductor names
   v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf, which is not in this tree`, and
   `verdict: energy_chain FAIL of 98 {"checks": 98, "citations_unjudged": 0, "coordination_findings": 0, "fail": 1,
   "selection_findings": 0, "stages": 12}`, `energy_chain exit 1`. Verdict files: `_a` and `_e5` FAIL, `_b`, `_e`
   and `_p` PASS. **Exactly what the page says to expect.**
2. Section 1a's `REF` line gave `REF=75ad6ee5` (the build commit, marked `public yes`). `fetch
   v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf` printed `OK ...` (3,850,294 bytes, sha256
   `8ef40cd9...82d6`, equal to `REFERENCED-SOURCES.tsv`).
3. The chain again: the same fifteen notes (`diff` of the note lines: identical), no finding,
   `verdict: energy_chain PASS of 98 {"checks": 98, "citations_unjudged": 0, "coordination_findings": 0, "fail": 0,
   "selection_findings": 0, "stages": 12}`, `energy_chain exit 0`; all five per-board verdicts PASS. **As expected.**

`python3 v2/docs/records/h3/handover_counts.py` from `H3/`: exit 0, 86 lines, **byte-identical** to the filed
`v2/docs/records/h3/handover_counts.out` (`cmp`). The extraction still verified OK afterwards.

Also run on this host, each light, none asked of me but each named by START-HERE section 6 as "not run again on H3":

| Command | Result on H3 | What the pages say |
|---|---|---|
| `python3 tools/rules_lib.py requirements` from `v2/ecad`, ZIP alone | `144 requirement record(s), 13 error(s), 20 warning(s)` | H2 read 13 and 17; REGENERATE "Edition H3" infers 20 for H3, not run. The inference holds |
| section 1a's whole block (third extraction, `work/val/`) | `REF=75ad6ee5`; 29 lines `OK`, none `FETCH FAILED` or `DIFFERS`; `checked 139 rows of MANIFEST.md`, `RELEASE CHECK PASS`; `144 requirement record(s), 0 error(s), 20 warning(s)`; `v2/docs/REQUIREMENTS-TRACE.md is current` | as the page says, with 20 for 17 |
| `rules_render.py --requirements --check`, ZIP alone | `REQUIREMENTS-TRACE.md REFUSED` (13 errors) | as START-HERE section 6 says |
| `pwr_budget.py`, `frame_seat.py`, `case_margins.py` | each exit 0, each output byte-identical to its filed reference | as the page says |
| `VERDICT_DIR=<scratch> python3 v2/ecad/tools/check_contracts.py v2/ecad` | `ALL CONTRACTS PASS`, `verdict: check_contracts PASS of 99` | PASS 99 of 99 |
| `python3 v2/docs/diagrams/tools/build.py --check` | `diagrams: 5 of 11 current against MANIFEST.json`; `extract_mermaid.py --check`: `mermaid sources: current` | LAYER-STATUS expects the ZIP to read as the repository, 5 of 11 |
| `python3 v2/docs/layout-constraints/calc/rail_widths.py --markdown` | byte-identical to `calc/rail_widths.out` | the sheets' power tables' source |

### D. Route B, a schematic: board P on the KiCad host, from the ZIP alone

The ZIP and its `.sha256` were copied to `/root/h3check-usability/regen/`, and sections 2 and 3 of `REGENERATE.md`
were run as written, one command per line, `H3` for `H2` (21:30:11 to 21:30:21 UTC; the log is
`work/box/regen.log`). **Every command worked as written. No line of the page had to be changed.**

| Step | Result | Page's expectation |
|---|---|---|
| `sha256sum -c`, `verify .`, `sch_prov.py read` | `OK`; `verify .: OK`; generator `ee62fdb195a9f217` | the same |
| `gen_footprints_idc.py` | `gen_footprints_idc: 7 footprint(s)` | the same |
| `PHASE=P4 gen_sch_p.py` | `wrote pcb-p-pack.kicad_sch parts: 95 lib symbols: 21`; `lands: 21 footprint(s) judged, 0 pin(s) on a pad the land does not carry, 0 land(s) unreadable`; `layout: 2 A3 pages ...`; `nets: 51 single-pin nets (should be empty or intentional): []` | the same |
| `build_sch.sh` | ERC line, `netlist: out/pcb-p-pack.net`, `sch_prov: ... generator ee62fdb195a9f217 (... 60 land(s) ...)`, `sch_pages: 2 x 1 cells, 2 pages kept of 2 tiles`, `bom: out/pcb-p-pack-bom.csv` | the same |
| `erc_gate.py --run` | 106 `lib_symbol_issues`, 17 `unconnected_wire_endpoint`, `no blocking error (123 violations ...)`, `verdict: erc_gate PASS of 123` | the same |
| netlist | `PARITY_AFTER_NOISE`, `content_hash` `efe60479293f0004` on both sides | the same |
| schematic | `PARITY_AFTER_NOISE` (N1 once, N2 twice) | the later-day case, as written |
| intent | `PARITY_AFTER_NOISE`, `keys_changed: []` | the same |
| provenance | `DIFFERENT`, `keys_changed: ["schematic_sha256"]`, exit 1 | the later-day case, as written |
| `sha256sum`, `grep schematic_sha256` | committed `47e0bc19e8e18cf0...`, regenerated `a58d0eecc7abe768...`; each sidecar names the first 32 hex digits of its own schematic | the same two values the page prints |
| BOM | `PARITY`, 38 rows each side | the same |
| ERC comparison | `PARITY_AFTER_NOISE`, 123 and 123 | the same |
| second `verify .` | 13 problems: five differ (intent, netlist size and sha256, provenance, schematic), eight new files under `out/` | "13 after" the commit's day |

**Parity as the page defines it: reached.** The design regenerated from the ZIP alone is the committed design; the
only differences are the date noise the page names.

### E. Route C from the ZIP alone

`REGENERATE.md` section 7's block as written, in `/root/h3check-usability/suite/`, in the background with a done
file (21:22:17 to 21:29:44 UTC):

- **Measured on H3: `suite exit 1`, `tests: 1957 passed, 20 failed, 23 skipped`.**
- The 20 failures are the 20 of section 7's table, test for test (4 `test_requirements`, `test_layout_entry_stages`,
  `test_interfaces`, `test_emc_sheet`, 3 `test_rails_census`, `test_evidence_class`, `test_energy_chain`, 2
  `test_case_geometry`, 3 `test_block_contract`, `test_doc_provenance`, `test_order_readiness`,
  `test_netlist_provenance`), and each failure line names the input the snapshot leaves out.
- Against the pages: H2's figure is 1956, 20, 23, labelled as H2's in START-HERE section 1a and in REGENERATE (route
  C's row and section 7); REGENERATE "Edition H3" says H3 raises the totals by the packer's new test. 1957 is 1956
  plus one. **The expectation holds.**
- `python3 run.py test_handover_pack`: `tests: 15 passed, 0 failed, 1 skipped` (H2: 14 and 1).
- **No page advertises a full-suite PASS from the ZIP.** I searched every suite count in the handover pages, the
  two release records, H2-RESPONSE and EXECUTION-PLAN: each names the snapshot, commit or branch it was measured on.
  START-HERE, REGENERATE and RELEASE-H3 each say the suite is not expected to pass from the ZIP alone.

### F. Layout constraint sheets and the FEA-007 holds

- Six sheets (A, B, C, D, E, P) each name, in their first lines, the netlist and the intent their power table was
  computed from by sha256/16. I hashed the netlist and intent files inside the package: **all twelve equal.** E5's
  sheet names its board file `686b29a734c55b9a`, which is the packaged file's hash.
- A.md's and P.md's power rows agree with `calc/rail_widths.out` (A: CELL+ 23.91, VIN_RAW 14.10 A and 15.29,
  VBUS20 3.55, +13V8_PA 2.76, +5V_DEV 2.03; P: the pack path 11.95 and 3.36).
- **FEA-007 at layout entry, one statement everywhere I looked:** A, B, D, E, E5 and P are held; D and E5 on desk
  items alone; A, B, E and P on desk items and the mock-up; C is not held at layout entry, only at fabrication
  release. Sources: the registry's FEA-007 record (`holds_layout_entry: a, b, d, e, e5, p`; FABRICATION_RELEASE
  `a, b, c, e, p, case`); `CURRENT-EVIDENCE.md` lines 63 to 96 and 134; LAYER-STATUS layer 7 row and the
  layout-entry table; CONTINUATION-BRIEF sections 0, 1 step 5, 5.1 and 8; EXECUTION-PLAN's per-board table (rows A
  to E5 and its "Source of the FEA-007 entries" row) and its checkpoints; also READY-TO-ACT line 56 to 63,
  ARCHITECTURE line 775, PRODUCT-BRIEF line 305. START-HERE itself gives no per-board FEA-007 statement, only
  "21 layout-entry stages of FEA-001 to FEA-007" and the per-board totals; 21 is 4 + 5 + 2 + 4 + 2 + 3 + 1 from the
  table, so it agrees.
- Three interface contracts against the packaged netlists (my script): IF-AE-DOCK (A `J_DOCK` and E `J_BLK` pin for
  pin; A `J_VR1` to `J_VR4` and E `P_VR` on VIN_RAW; `J_VN`, `P_VN` on GND), IF-AB-RIBBON (A `J_AB1` and B `J_AB1`,
  26 pins, no pin differs), IF-BC-PANEL (B and C `J_PANEL`, 26 pins, pins 1 and 2 differ by net name only,
  `PANEL_5V` and `+5V`). **The contracts describe the netlists.**
- Erratum f checked: `boards/a.json` declares `J_DOCK` pins 1 and 2; both are GND in the packaged netlist; VIN_RAW
  is on `J_VR1` to `J_VR4` pin 1 and D2 pin 1. It is the only `external_ports` entry of any board that names pins.

### H3's design content against H2's (my own comparison)

`design_difference.py` needs git, so I fetched `v2/release/handover/H2.MANIFEST.tsv` from the public repository at
`75ad6ee5` (git blob sha `c880d0f4...`, equal to its row in `EXCLUDED.tsv`) and compared it with H3's manifest by
sha256: 2233 rows against 2274; 0 removed, 41 added, 41 changed. Under `v2/ecad/` five files changed (the packer,
its test, the two registries, E5's tracked `interfaces_e5` reading); under `v2/cad/` one added (`render/scene.py`);
no file under `v2/vendor/` or `v2/release/` changed; `REFERENCED-SOURCES.tsv` is unchanged. **No schematic, netlist,
intent, provenance sidecar, land, generator, board table, checking tool, export or maker document differs.** The
claim holds for the files the two snapshots carry.

### Other

- Every 8-hex commit id in the eleven handover pages is a row of `SOURCE.txt`'s timeline (145 rows; 8 marked
  `public no`, each a branch commit outside H3).
- Every `v2/...` path the handover pages cite is in the package, in `REFERENCED-SOURCES.tsv` or in `EXCLUDED.tsv`,
  except names of things that are not files of the commit (`v2/ecad/out`, `H3.zip` itself, one experiment folder).
- The six schematic PDFs have 16, 43, 5, 7, 4 and 2 pages (`pdfinfo`), as the page says.

## 3. The six questions (part A)

Times are my reading time from opening START-HERE, approximate.

**1. The product, its users, its modes.** About 6 minutes, no guess. START-HERE section 2: a sealed Peli 1450
holding seven carrier boards and a 4S3P pack of about 145 Wh, which carries the MeshSat Bridge software so messages
from local off-grid networks leave over whichever long-range bearer is up (Iridium, 5G, LoRa, APRS, HF). Users: a
non-commercial prototype operated in the Netherlands and the EU by a licensed radio amateur; roles are the
operator, a second crew member, local end users, remote correspondents. The modes are not in START-HERE; its
reading order sends the reader to `v2/docs/CONOPS.md` section 4, one table: Transport, Deploy, Startup, Normal,
Reduced, Heat stage, Hot stop, Charging, Degraded, EMCON, Blackout, NVG, SOS, ZEROIZE, Shutdown, Storage, Service,
Commissioning, each with entry, exit, what runs and what guarantees it; power states in section 4a.

**2. What is settled, and the authority for each kind.** About 12 minutes, one small guess. START-HERE section 4
("Who decided what") and CONTINUATION-BRIEF section 2 (tables with "Recorded in" and "Authority"). Owner rulings:
`pcb_requirements.yaml` `owner_rulings`, 29 entries (D-01 to D-17, decisions 27, 28, 41, 43, `public-docs`,
`standing-rule`), and CONOPS section 7. Session choices: `session_choices` SC-01 to SC-63, each with its reversal.
Requirements: the registry, 144 records, `baseline_state: BASELINED at a54b793b`, with `REQUIREMENTS-TRACE.md` its
generated view. Decisions: `pcb_decisions.yaml`, 25 entries, 21 ruled and 4 closed, none open
(`OWNER-DECISIONS-OPEN.md`: 0 open). The guess: five of the 25 carry no `authority` field (minor 11).
CONTINUATION-BRIEF section 3 lists what must not be read as settled.

**3. The seven boards and three interfaces.** About 10 minutes, no guess. Boards: START-HERE section 2 (A power
and I/O, B compute, C panel backer, D VHF APRS, E1 dock strip, E5 dock block, P pack BMS, with project folder and
declared phase). Contracts: `v2/ecad/tools/pcb_interfaces.yaml`, `board_to_board.contracts`, 30 entries, with
`v2/docs/HW-FW-CONTRACT.md` and ARCHITECTURE section 3's diagram.

| Contract | Connector | Signals | Judged by |
|---|---|---|---|
| IF-BC-PANEL | B `J_PANEL` IDC 2x13 box header to C `J_PANEL` IDC 2x13 SMD, a ribbon | PANEL_5V, the kit I2C, the safety lines, USB | `check_contracts.py` (pin-map identity) |
| IF-AB-RIBBON | A `J_AB1` IDC 2x13 top to B `J_AB1` underside | USB_D8, PI_SHDN_REQ, PI_KILL, SDA, SCL, EXP_INT, TR_APRS, EMCON_HW, TX_INHIBIT_n, SLOT_EN1 to 3, ZEROIZE_HW, SHORE_INHIBIT, USB_E6, grounds | the same |
| IF-AE-DOCK | A `J_DOCK`, 12 Preci-Dip 813 spring pins, on E5's targets, to E `J_BLK`; Mill-Max power pins A `J_CP1-4`, `J_CN1-4`, `J_PRE1`, `J_VR1-4`, `J_VN1-4` to E `P_CP`, `P_CN`, `P_VR`, `P_VN` | pins 1 to 7 and 11 GND, 8 SHORE_INHIBIT, 9 and 10 USB_E6, 12 DOCK_SPARE; CELL+ (10 A typical, 18 A peak), VIN_RAW (14.10 A) | `check_contracts.py` sections 4 and 5; `block_contract.py` for E5 (needs the excluded board A file) |

The contracts exist as YAML only; I read them with a ten-line script.

**4. Which layers are COMPLETE, on what evidence; what the others lack.** About 5 minutes, no guess. START-HERE
section 1a, LAYER-STATUS "Status at handover H3" and "Status at handover H2", RELEASE-H3. COMPLETE: layer 1
(definition baselined at `6b2a9965`, re-stamped at `a9f212c7`), layer 2 (`79963b3b`, re-stamped the same way),
layer 3 (registry BASELINED at `a54b793b`, written in `2c12be91`, COMPLETE since `24e7bf5a`), each on AI review
records listed by sha256/16, which `handover_counts.py` re-prints from the files. IN_PROGRESS: layers 4 to 9; the H2
table's last column lists per layer what remains, and the layout-entry table lists the 40 reasons per board. One
reservation: layer 3's item 3.15 (minor 3).

**5. The blockers today, in three kinds.** About 10 minutes, no guess, some filtering. ENGINEERING-QUESTIONS
groups them: A design work (18, desk), B physical evidence (5, hardware and so a purchase), C external
authorisation (7, the owner's money, outside contact or a value only he sets); `READY-TO-ACT.md` section 0 lists
the authorisations. Six of the thirty are answered in whole or in part and stay in the index (EQ-04, EQ-18, EQ-27,
EQ-28, EQ-29, EQ-30), so the reader filters by the last column. Two blockers checked field by field, and a third:

| Block | Issue | Evidence | Attempts | Options | Recommendation | Expertise or equipment | Cost | Dependent work |
|---|---|---|---|---|---|---|---|---|
| EQ-25 (desk) | yes, with the arithmetic (1.09 V against 0.8 V) | yes, files present in the package (`records/w3t/`) | yes | three, each computed | (a), one resistor changed and one added on board C | yes | yes | yes ("Affected"; the index: RF-002 on A to D, CON-010) |
| EQ-10 (outside reviewer, owner) | yes | yes | yes, with a correction marked for H3 | one, and why no other | yes, four steps in order | yes, with a shortlist | TBD by quote, said so | yes (P's fabrication release, the pack build) |
| EQ-08 (hardware, purchase) | yes | yes | yes | three | yes | yes | yes, dated prices | yes, but see minor 5 |

**6. First, second and third tomorrow.** About 10 minutes, part of it inferred. CONTINUATION-BRIEF section 4, the
paragraph "At H2", gives the order: first the desk items that need no purchase (EQ-25 on board C, PWR-001's
declarations on C and P, the diode sheets on D and E, HOT-R1 on A and E, the pack-protection table on P, SI-001's
edge rates); second decision 31's protection reviews on A, D and E (with erratum f's declaration moved) and the
feasibility blockers' desk stages; third the owner's authorisations from READY-TO-ACT section 0. For the first,
the input and the expected result are written (which parts change, 0.24 V failed safe, the walk reads PASS). The
commands exist in pieces (REGENERATE sections 3 and 9); no page gives a circuit round as one procedure (minor 9).
START-HERE also says a candidate, set 6, already draws several of these remedies on a branch that is not public, so
an outside engineer will redo work that exists; the page says so plainly (erratum e).

## 4. The errata of START-HERE section 1a, judged as a reader (part G)

| # | Misled without it? | Still misled with it? |
|---|---|---|
| a | Yes. A sheet's placement and protection lines read as current | Partly. It is a general warning; stale lines are not listed. I found one the erratum does not cover (minor 4) |
| b | No, slowed | No. The two sections named are enough |
| c | Yes, for route C's third route | No |
| d | Yes | Partly. EQ-08 is not among the five corrected and still names board C at layout entry (minor 5) |
| e | Yes. I would have started drawing EQ-25's remedy | No, but it leaves the reader with a choice the package cannot settle |
| f | Yes, and it matters: TRN-001's PASS on board A reads as if VIN_RAW's entry were judged | No, if START-HERE is read first. `PCB-RULE-STATUS-A.md` prints the PASS with no mark, being generated |

The errata are accurate where I could test them (a for board A section 7, f against the netlist and the board
table, d's five marks are present). **They are incomplete** against the package itself: minors 1 and 2.

## 5. Findings

### Blocking

None.

### Minor

1. **`CURRENT-EVIDENCE.md` says the requirements baseline is still open, unmarked.** Lines 8 and 9: "The
   foundations are incomplete because the requirements and architecture baselines are still open (review of 26
   September 2026, section 6 item 1)". The sentence is typed into the renderer (`v2/ecad/tools/rules_render.py`
   line 1409), so the page is the same file as in H2. H3 says the registry is BASELINED at `a54b793b` and layer 3
   COMPLETE (START-HERE section 1a; `REQUIREMENTS-TRACE.md`: "Registry state **BASELINED at a54b793b**"). No
   erratum names it (`grep` finds the sentence only there and in the review it quotes). **My decision on
   severity:** it is not marked, so it does not fit the description of a marked stale sentence; I class it minor
   because the registry, which START-HERE section 4 names the single authority for requirements, its generated
   trace page and five handover pages (START-HERE, LAYER-STATUS, CONTINUATION-BRIEF, ENGINEERING-QUESTIONS,
   RELEASE-H3) state the baseline, the clause cites a review dated the day before it, and it errs toward caution. It is the nearest to blocking of the fifteen. An erratum line answers it without touching
   the page or the renderer.
2. **The errata omit two items the package itself calls found and open.** `v2/docs/EXECUTION-PLAN.md`, checkpoint
   of 27 September 23:02, field "Engineering": REL-001's word list "finds no wear word on 61 connector-like parts
   (an RJ45 jack, two SIM sockets, a ZIF, two headset jacks and the dock's spring pins among them), so its
   completeness holds for its twelve words only", and the rule audit names its verdicts by absolute path.
   `PCB-RULE-STATUS-A.md` line 85 (and B, C, D, E, E5, P) prints REL-001 **PASS** ("reliability PASS of 45" on A).
   REL-001 is verified at PROTOTYPE and is no layout-entry reason. The same paragraph's third item is erratum f.
3. **Layer 3's acceptance item 3.15 is unquantified at H3.** LAYER-STATUS, layer 3 table: "MET in substance; the
   letter is not met (n7: open items in no record's `waits_on`)", on the release check's count of ten
   (`REVIEW-LAYER-3-RELEASE-2-2026-09-27.md` line 135). In the registry H3 carries I count **24 of 58** open items
   in no record's `waits_on` (L-01, S-13, S-23, S-47, S-56, S-60 to S-76, S-79, S-81), 21 of them named by no
   record in any field (S-13, S-47 and S-64 are named in a record's text). START-HERE section 9 says a layer is
   COMPLETE only when every acceptance item is met. The table discloses the state; it does not give the number, and
   fifteen of the 24 (S-64 to S-76, S-79, S-81) are not among the ten the release check counted.
4. **Board E's sheet names J_BLK for VIN_RAW.** `v2/docs/layout-constraints/E.md` line 73, in the power table
   erratum a calls current: "VIN_RAW (the input filter's output to J_BLK; **H2**: 14.10 A committed)"; line 272
   lists "J_DCIN, J_BLK and the test points" as the masked 36 V sites. In the packaged netlist board E's VIN_RAW
   is on `P_VR` pin 1 and `J_BLK` pins 1 to 7 and 11 are GND. The numbers are right and the sheet's head states
   SC-55; the connector named is the old one, and `P_VR` and `P_VN` appear nowhere in the sheet.
5. **EQ-08 names board C at layout entry.** Index row "Boards: A, B, C, E, P"; option (a) "before layout entry of
   A, B, C, E and P". FEA-007 holds A, B, D, E, E5 and P there and not C. The block's recommended action names A,
   B, E and P and omits D's and E5's desk items.
6. **RELEASE-H3's build rows do not resolve for a recipient.** Seven rows read `TBD-BY-INTEGRATOR` inside the ZIP,
   as the page says. START-HERE section 1 says to read them "beside the ZIP", and REGENERATE's route C row says
   "H3's own result is in `RELEASE-H3.md`". Beside the ZIP the recipient holds the checksum only; the suite on the
   source commit and the two fresh checks are in nothing he holds.
7. **`public_check.py` cannot answer from an extraction.** RELEASE-H3 ("Public" row) and REGENERATE section 7
   name it. Run as `python3 v2/docs/records/h3/public_check.py 75ad6ee5bc98d7213b9a61d1f64cfa7ea19cc669` from
   `H3/` it printed "not in this clone" and "-" for the commit page: it asks GitHub only about a commit the local
   clone holds. Its docstring says it needs git; the pages do not say it needs a clone.
8. **The suite writes into the tree it runs in.** After section 7's block, `verify .` read 6 problems, each
   `v2/ecad/tools/out/energy_chain*.verdict.json: in the snapshot, not in the manifest`. Section 7 does not say so,
   and START-HERE section 6 warns against a gate writing into a tree.
9. **No circuit round procedure.** REGENERATE reproduces the committed design, where `DIFFERENT` is a failure;
   `v2/README.md` "Regenerating a board" describes the layout pipeline the handover says not to start. For the
   first desk tasks the reader assembles edit, regenerate, accept, re-take and re-render from sections 3 and 9.
10. **Two stale pointers.** START-HERE section 1's row for LAYER-STATUS says to read "its section 'Status at
    handover H2' first"; at H3 the H3 section is first. ENGINEERING-QUESTIONS keeps six questions answered in
    whole or in part among its thirty, with no separate list of the open ones.
11. **`pcb_decisions.yaml`: 5 of 25 decisions carry no `authority` field** (23, 24, 25, 26, 38), and decisions 1 to
    22 are in `v2/docs/OWNER-DECISIONS-2026-09-11.md`, not in the file. START-HERE section 4 says every decision
    carries its authority.
12. **`SOURCE.txt` labels the five candidate patches** "UNACCEPTED work exported from unpushed worktrees" and does
    not say they are superseded and referenced, not bundled, as `candidates/README.md` and START-HERE do.
13. **`design_difference.out` compares `b89b50b4` with `089f7f27`**, the commit before the snapshot's `75ad6ee5`,
    which files that record. A record cannot name the commit that files it; the page does not say the gap. My
    manifest comparison covers it.
14. **START-HERE section 4 lists an "interfaces summary"** among the documents of `v2/docs/`; no page of that name
    exists (ARCHITECTURE section 3 is the nearest, naming 27 of the contract ids), and the 30 contracts' pin
    tables are in the YAML only.
15. **REGENERATE section 3's expected generator lines** are in another order than printed and omit two lines
    (`schlayout verify: 216 pins in 179 nets, every component one name`; `intent: ... (4 bypass, 5 rails, 2 nodes,
    5 pair classes)`); `build_sch.sh` also prints `sheet pdf:` and `pdf:`. Nothing differs in substance.

## 6. What I did not check

- Whether any circuit, requirement, calculation or review conclusion is right. This is a usability check.
- Route C in a git checkout: the suite with history, the re-take of section 9 by any of its three routes,
  `handover_pack.py repo`, `design_difference.py`.
- Sections 4 and 5 of REGENERATE: only board P was regenerated; no export was re-made.
- The suite in the form `cd v2/ecad/tools && python3 tests/run.py`; I ran the page's form (`cd .../tests`,
  `python3 run.py`), once. Another suite, not mine, was running on the KiCad host at the time; I did not touch it.
- `RELEASE-H3.md` as filled in after the build: I did not fetch it, the package names no commit that holds it.
- Whether `75ad6ee5` is an ancestor of the public `main`; only that GitHub serves its files (29 fetches, each OK,
  and H2's manifest).
- The content of the review records of layers 1 to 3, beyond the two lines quoted; their hashes only as
  `handover_counts.py` prints them.
- LAYER-STATUS Appendix A; ENGINEERING-QUESTIONS blocks other than EQ-25, EQ-08 and EQ-10; GLOSSARY beyond a scan;
  DEFINITION-STATUS; H1.1-RESPONSE and H2-RESPONSE beyond their FEA-007 line.
- Sheets B, C and D beyond their heads and hashes; sections 3 to 11 of any sheet against the netlists, except A
  section 7 and E's dock rows.
- The maker documents' content, and any Python or KiCad version other than those named above.
