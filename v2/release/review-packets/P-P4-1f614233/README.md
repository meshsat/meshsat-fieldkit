# Review packet: board P (pcb-p-pack) at 1f614233

**UNBUILT PROTOTYPE DESIGN. No board of this set has been fabricated, assembled or tested; nothing in this packet is physical evidence. A review packet is a review input: it does NOT release this board to fabrication, layout or ordering, and it approves nothing.**

**READINESS OF THIS PACKET: QUARANTINED, NOT_FOR_FAB.** No file here is an order file; the two BOM files carry NOT_FOR_FAB in their names.

| | |
|---|---|
| Board | P, `v2/ecad/pcb-p-pack-p2` |
| Source revision | `1f614233998c3087a53abfa977be134465ce9f47` (docs(review): the review of the 26 September progress report is recorded, to be executed item by item [MESHSAT-1357]), 2026-09-26T14:13:16+02:00 |
| Compared with | `82dd1e4dc44efabeee1164a995cda4e866610f3d` (fix(tests): the blocked-land fixture no longer overwrites the lcsc_fill evidence rules CMP-002 and SUP-001 read [MESHSAT-1357]) |
| Declared phase | P4, from `tools/boards/p.json`: the phase of the board's committed LAYOUT. The layout is not part of this packet and is not judged by it (rule SCH-002 decides whether it carries this netlist). The schematic's own title-block label is P4 |
| Complete | yes |
| Built | 2026-09-26T15:55:55Z with KiCad 9.0.9, tool sha256 `7913d0a57567d896` |
| Part sources read | a SOURCES.yaml supplied with --sources, identified by its sha256, sha256 `2b192f2bb8ded051` |

## What this packet is, and is not

- It is a review input for a qualified reviewer: the schematic of one board exactly as committed at the source revision, with what changed since the previous revision and why, the parts and their primary sources, and the interfaces it shares with other boards.
- It is NOT a release. No layout, fabrication, order or approval follows from it. Hardware state: unbuilt prototype design.
- It is desk material only: no bench measurement, EMC, thermal or environmental test exists for this board.
- The review of 26 September 2026 (`v2/docs/reviews/2026-09-26-foundation-progress-review.md`, section 5) asked for it.

## Contents

| File | What | sha256 (first 16) |
|---|---|---|
| `bom/NOT_FOR_FAB-parts-identity.csv` | the part identity and footprint map, one row per BOM line (NOT_FOR_FAB: a review input, never an order file) | `073618fd942da1aa` |
| `bom/NOT_FOR_FAB-pcb-p-pack-bom.csv` | the BOM exported from the committed schematic (build_sch.sh's own fields and grouping), byte for byte as KiCad wrote it; NOT_FOR_FAB in its name because it is a review input, never an order file | `8947bbd655fb5b60` |
| `bom/parts-identity.json` | machine-readable record, see README.md | `5ba58546067c077c` |
| `bom/sources-coverage.json` | machine-readable record, see README.md | `b72bb32d8d576973` |
| `changes/attribution-read-by-hand.yaml` | the reading of every changed reference by hand: IDs, the generator lines that carry them, the reason in words; the build checked every ID against its lines | `91e14f52288281a2` |
| `changes/changes.json` | machine-readable record, see README.md | `c1d3c6e631f113ed` |
| `changes/gen_sch_p.diff` | the generator diff between the two revisions | `4f7ba91659dc43a7` |
| `changes/prev-82dd1e4d-gen_sch_p.py` | the generator at the previous revision | `0d2b0aae207a8656` |
| `changes/prev-82dd1e4d.net` | the committed netlist at the previous revision | `ab2dc5662cb4eb44` |
| `contracts/check_contracts.log` | the revision's check_contracts.py output in the packet's work copy | `23c3d126284b1d3b` |
| `contracts/contracts.json` | machine-readable record, see README.md | `6e86c5edaf071dda` |
| `interfaces/interfaces.json` | machine-readable record, see README.md | `6403e8fb40740889` |
| `native/boards-p.json` | the board declaration (declared phase, classes) | `fb26e422307afb21` |
| `native/fp-lib-table` | the project's footprint library table | `9c2d14bd7a666d84` |
| `native/gen_sch_p.py` | the generator that writes the schematic: the design's source of truth, with the finding IDs in its comments | `d66ae0a15be1dc4e` |
| `native/meshsat.pretty/Eaton_SCF9550_9.5x5.0mm.kicad_mod` | project footprint used by this board | `9ae65da606637469` |
| `native/meshsat.pretty/Texas_RSM0032A_VQFN-32-1EP_4x4mm_P0.4mm_EP1.4x1.4mm.kicad_mod` | project footprint used by this board | `fd01a6538a531602` |
| `native/netlist/pcb-p-pack-intent.json` | the generator's intent file (rails, nodes, bypass declarations) | `1ef6daa83319ac15` |
| `native/netlist/pcb-p-pack.net` | the committed netlist (KiCad s-expression) the change report reads | `3c925191447136ac` |
| `native/netlist/pcb-p-pack.net.prov.json` | the netlist's provenance sidecar (generator identity, schematic sha) | `8680ff98d5f54d28` |
| `native/pcb-p-pack.kicad_pro` | its KiCad project file | `9c9da1f900f7ef59` |
| `native/pcb-p-pack.kicad_sch` | the committed schematic at the source revision (KiCad 9 native) | `547541cdcbd5fdb7` |
| `open/holds-and-decisions.json` | machine-readable record, see README.md | `861c4da9979fb6aa` |
| `schematic/pcb-p-pack-erc.json` | KiCad ERC of the committed schematic, every severity; a report, not a verdict | `dd52c85579130c68` |
| `schematic/pcb-p-pack-schematic-sheet.pdf` | the whole schematic as one sheet | `010ead990a085180` |
| `schematic/pcb-p-pack-schematic.pdf` | the schematic, paged into A3 blocks by the revision's own sch_pages.py (what build_sch.sh publishes) | `d9355b00f54ba411` |

Verify: `python3 v2/ecad/tools/review_packet.py verify <this folder>` or `sha256sum -c SHA256SUMS` inside it. `MANIFEST.json` carries the full record.

## Schematic exports

- KiCad 9.0.9 exported the PDFs, BOM, ERC and netlist from the committed schematic.
- The exported netlist against the committed netlist: **PARITY_AFTER_NOISE** (regen_compare; PARITY_AFTER_NOISE means only the export's own path, date and tool differ).
- At the previous revision, the same comparison: **PARITY_AFTER_NOISE**, so both ends of the change report are schematic content.
- ERC, every severity, as a report and not a verdict (the project's gate `erc_gate.py` applies the board's allow list): warning:lib_symbol_issues 103, warning:unconnected_wire_endpoint 17.
- kicad-cli printed "schematic has annotation errors" on the bom and netlist exports. KiCad does not say which symbol it means. A text reading of the committed schematic finds no repeated (reference, unit) and no unannotated reference among 103 symbol instances, so the cause is NOT ESTABLISHED; the exported netlist's parity above is what shows the export carries the committed circuit.

## Changes against `82dd1e4d`

Components 56 to 82, nets 39 to 54: 30 added, 4 removed, 9 changed. Generator lines added or changed: 346. Details per reference, with the generator lines and the comment each ID was read from, are in `changes/changes.json`.

**How each row was read.** Every changed reference was read by hand (`changes/attribution-read-by-hand.yaml`, the session (review stream PKT), 26 September 2026, from gen_sch_p.py at both revisions and the round-4 board P record): the IDs, the generator lines at `1f614233` that carry them, and the reason in words. The build refused the file unless every ID is written on its cited lines and every cited range is tied to the change (it names the reference or one of its nets, is the statement's own comment or its section header, or the row states the tie). The mechanical reading stays in `changes/changes.json` (`evidence.automatic`) beside each row, with `agrees` saying whether it matches; it differs on 38 of 43 rows, mostly because it credits every ID written in a part's own comment, including IDs cited there as context.

**Counts.** 43 changes: 17 carry a finding ID; 24 carry only an owner ruling, a decision or a rule ID; 2 carry no ID of any kind; 0 are UNVERIFIED_ATTRIBUTION. So **26 changes have no finding ID**. Finding IDs include the round records' own item IDs (R4D-1, R4E-02, RP-17), which are the session's records of that round.

| Ref | Kind | What changed | Finding IDs | Rulings and decisions | Rules | Status | Read | Generator lines (cited) |
|---|---|---|---|---|---|---|---|---|
| C10 | REMOVED | 100n, Capacitor_SMD:C_0603_1608Metric, no LCSC code | F-PK-02 |  |  | TRACED | hand | gen_sch_p.py 542 |
| C11 | CHANGED | pin 2: PACK_N -> PACK_MID | O-12, RP-22 |  |  | TRACED | hand | gen_sch_p.py 285-290 |
| C12 | CHANGED | pin 1: PACK_P -> PACK_MID | O-12, RP-22 |  |  | TRACED | hand | gen_sch_p.py 285-290 |
| C13 | ADDED | 100n, Capacitor_SMD:C_0603_1608Metric, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 226-232 |
| C14 | ADDED | 100n, Capacitor_SMD:C_0603_1608Metric, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341 |
| C15 | ADDED | 100n, Capacitor_SMD:C_0603_1608Metric, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341 |
| C16 | ADDED | 100n, Capacitor_SMD:C_0603_1608Metric, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341 |
| C17 | ADDED | 100n, Capacitor_SMD:C_0603_1608Metric, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341 |
| C18 | ADDED | 100n, Capacitor_SMD:C_0603_1608Metric, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341 |
| C19 | ADDED | 100n, Capacitor_SMD:C_0603_1608Metric, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341-345 |
| D1 | CHANGED | value: SMBJ20A -> SMBJ20A (pack terminal clamp, unidirectional: cathode on PAC; lcsc:  -> C364296; pin 1: PACK_N -> PACK_P; pin 2: PACK_P -> PACK_N | A03, F-IN-01, S-09 |  |  | TRACED | hand | gen_sch_p.py 297 |
| D2 | CHANGED | value: USBLC6-2SC6 ESD clamp on the SMBus pair -> PESD5V0S1BA (SMBC ESD clamp to the pack side of the shunt); footprint: Package_TO_SOT_SMD:SOT-23-6 -> Diode_SMD:D_SOD-323; lcsc: C7519 -> C19224; pin 2: GND -> PACK_N; pin 3: SMBD -> None; pin 4: SMBD -> None; pin 5: VCC_F -> None; pin 6: SMBC -> None | F-BP-01 |  |  | TRACED | hand | gen_sch_p.py 192-193 |
| D3 | ADDED | PESD5V0S1BA (SMBD ESD clamp to the pack side of the shunt), Diode_SMD:D_SOD-323, C19224 | F-BP-01 |  |  | TRACED | hand | gen_sch_p.py 192-193 |
| F2 | ADDED | SCF9550-30-05 self-control fuse (Eaton, 30 A, 4-5 cells): 1 and 2 the fuse, 3 th, meshsat:Eaton_SCF9550_9.5x5.0mm, C3670061 | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 245 |
| JP1 | ADDED | fuse arming jumper: open as built, closed at commissioning, Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341-345, 418-421 |
| J_SMB | CHANGED | value: SMBus lead to E6 J_SMB (JST-XH 1x4): SMBC SMBD GND PRES -> SMBus lead to E6 J_SMB (JST-XH 1x4): SMBC SMBD GND(pack side; pin 3: GND -> PACK_N; pin 4: PRES -> PRES_J | A07, S-05 |  |  | TRACED | hand | gen_sch_p.py 472 |
| J_TS | CHANGED | value: JST-PH 1x2 socket for the cell thermistor lead (the 10k NTC, -> JST-PH 1x5 socket for the four cell thermistors (Semitec 103; footprint: Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical -> Connector_JST:JST_PH_B5B-PH-K_1x05_P2.00mm_Vertical; lcsc: C5251182 -> C157993; pin 2: GND -> TS2; pin 3: None -> TS3; pin 4: None -> TS4; pin 5: None -> GND | F-PK-02 |  |  | TRACED | hand | gen_sch_p.py 208 |
| Q1 | CHANGED | pin 1: FUSED -> SCP_OUT; pin 2: FUSED -> SCP_OUT; pin 3: FUSED -> SCP_OUT | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 65-66 |
| Q3 | ADDED | AO3400A 30 V N-FET, chemical fuse heater switch, Package_TO_SOT_SMD:SOT-23, C20917 | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341-345 |
| Q5 | ADDED | 2N7002 60 V N-FET: the second level's under-voltage holds the discharge FET off, Package_TO_SOT_SMD:SOT-23, C8545 | RP-02 | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341-345, 451-462 |
| R11 | REMOVED | 10k, Resistor_SMD:R_0603_1608Metric, no LCSC code | F-PK-02 |  |  | TRACED | hand | gen_sch_p.py 208 |
| R12 | REMOVED | 10k, Resistor_SMD:R_0603_1608Metric, no LCSC code | F-PK-02 |  |  | TRACED | hand | gen_sch_p.py 208 |
| R13 | REMOVED | 10k, Resistor_SMD:R_0603_1608Metric, no LCSC code | F-PK-02 |  |  | TRACED | hand | gen_sch_p.py 208 |
| R17 | CHANGED | pin 2: FUSED -> SCP_OUT | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 65-66 |
| R22 | ADDED | 1k, Resistor_SMD:R_0603_1608Metric, no LCSC code | S-05 |  |  | TRACED | hand | gen_sch_p.py 222 |
| R23 | ADDED | 300R, Resistor_SMD:R_0603_1608Metric, C23025 | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341 |
| R24 | ADDED | 1k, Resistor_SMD:R_0603_1608Metric, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341 |
| R25 | ADDED | 1k, Resistor_SMD:R_0603_1608Metric, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341 |
| R26 | ADDED | 1k, Resistor_SMD:R_0603_1608Metric, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341 |
| R27 | ADDED | 1k, Resistor_SMD:R_0603_1608Metric, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341 |
| R28 | ADDED | 100k, Resistor_SMD:R_0603_1608Metric, no LCSC code | RP-02 | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341-345, 462 |
| R29 | ADDED | 20k, Resistor_SMD:R_0603_1608Metric, C4184 | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341-345 |
| R30 | ADDED | 5.1k, Resistor_SMD:R_0603_1608Metric, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341-345 |
| R31 | ADDED | 51k, Resistor_SMD:R_0603_1608Metric, C23196 | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341-345 |
| R32 | ADDED | 1M, Resistor_SMD:R_0603_1608Metric, no LCSC code | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341-345 |
| R33 | ADDED | 10k, Resistor_SMD:R_0603_1608Metric, no LCSC code | RP-17 |  |  | TRACED | hand | gen_sch_p.py 363-383 |
| RT1 | ADDED | PRF15BB103RB6RC chip PTC 10k, 4.7M at 130 C (Murata): the BQ4050 PTC element bes, Resistor_SMD:R_0402_1005Metric, C443668 | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 226 |
| TP11 | ADDED | FUSE_G, TestPoint:TestPoint_Pad_D1.5mm, no LCSC code | O-9 | D-15 |  | TRACED | hand | gen_sch_p.py 382, 421-423 |
| TP12 | ADDED | SEC_DOUT, TestPoint:TestPoint_Pad_D1.5mm, no LCSC code | none |  |  | NO_ID_OF_ANY_KIND | hand | gen_sch_p.py 482 |
| TP13 | ADDED | SCP_OUT, TestPoint:TestPoint_Pad_D1.5mm, no LCSC code | none |  |  | NO_ID_OF_ANY_KIND | hand | gen_sch_p.py 482 |
| TP14 | ADDED | FUSE_GQ, TestPoint:TestPoint_Pad_D1.5mm, no LCSC code | none | D-15 |  | TRACED | hand | gen_sch_p.py 421-423 |
| U1 | CHANGED | value: BQ4050RSMR: SMBus 1.1 gas gauge, primary protection, 4S bala -> BQ4050RSMR: SMBus 1.1 gas gauge, primary protection, 4S bala; footprint: Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm -> meshsat:Texas_RSM0032A_VQFN-32-1EP_4x4mm_P0.4mm_EP1.4x1.4mm; pin 23: GND -> PTC; pin 24: GND -> BAT_F | W6-F2 | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 160 |
| U2 | ADDED | BQ7720700DSSR: second-level cell OV 4.325 V / UV 2.25 V / open wire, TS on a fix, Package_SON:WSON-12-1EP_3x2mm_P0.5mm_EP1x2.65, C3681715 | none | D-15, decision 40 |  | TRACED | hand | gen_sch_p.py 341 |

**The 26 changes with no finding ID, and their reason**

- C13 (ruling, decision or rule only: D-15, decision 40): the capacitor across the PTC element (TI Figure 21)
- C14 (ruling, decision or rule only: D-15, decision 40): U2's supply capacitor CVD, 0.1 uF (inline at 390)
- C15 (ruling, decision or rule only: D-15, decision 40): U2's CIN ladder, cell 1 (inline at 394)
- C16 (ruling, decision or rule only: D-15, decision 40): U2's CIN ladder, cell 2
- C17 (ruling, decision or rule only: D-15, decision 40): U2's CIN ladder, cell 3
- C18 (ruling, decision or rule only: D-15, decision 40): U2's CIN ladder, cell 4
- C19 (ruling, decision or rule only: D-15, decision 40): the fuse drive: the gate node's capacitor
- F2 (ruling, decision or rule only: D-15, decision 40): the Eaton SCF9550-30-05 chemical fuse between the blade and the charge FET, as TI places it
- JP1 (ruling, decision or rule only: D-15, decision 40): the fuse arming jumper, open as built and closed at commissioning after the gauge's data flash is written and read back (the verification D-15 names)
- Q1 (ruling, decision or rule only: D-15, decision 40): the charge FET's source moves from FUSED to SCP_OUT, behind the new chemical fuse
- Q3 (ruling, decision or rule only: D-15, decision 40): the AO3400A that switches the chemical fuse's heater
- R17 (ruling, decision or rule only: D-15, decision 40): the charge FET's gate-source resistor follows its source to SCP_OUT (inline at 281)
- R23 (ruling, decision or rule only: D-15, decision 40): U2's supply resistor RVD, 300 ohm (inline at 390; SLUSEG7D Table 8-1)
- R24 (ruling, decision or rule only: D-15, decision 40): U2's cell 1 input resistor RIN, 1k (inline at 392)
- R25 (ruling, decision or rule only: D-15, decision 40): U2's cell 2 input resistor RIN, 1k
- R26 (ruling, decision or rule only: D-15, decision 40): U2's cell 3 input resistor RIN, 1k
- R27 (ruling, decision or rule only: D-15, decision 40): U2's cell 4 input resistor RIN, 1k
- R29 (ruling, decision or rule only: D-15, decision 40): the fuse drive: U2's COUT into the heater FET's gate through 20k (SLUSC67B 8.2.2.2.5)
- R30 (ruling, decision or rule only: D-15, decision 40): the fuse drive: the gauge's FUSE output into the heater FET's gate through 5.1k
- R31 (ruling, decision or rule only: D-15, decision 40): the fuse drive: the gate node's 51k to ground
- R32 (ruling, decision or rule only: D-15, decision 40): holds the heater FET's gate low while JP1 is open
- RT1 (ruling, decision or rule only: D-15, decision 40): the PRF15BB103 PTC element beside the protection FETs, the PTC input of the D-15 floor
- TP12 (no ID of any kind; round record: round-4 board P record, section 3: 'TP11 FUSE_G, TP12 SEC_DOUT, TP13 SCP_OUT / D-15 commissioning (O-9)'; no ID beside TP12 in the generator): a test point on U2's under-voltage output SEC_DOUT for the commissioning checks (inline at 482)
- TP13 (no ID of any kind; round record: round-4 board P record, section 3: 'TP11 FUSE_G, TP12 SEC_DOUT, TP13 SCP_OUT / D-15 commissioning (O-9)'; no ID beside TP13 in the generator): a test point on the protected cell node SCP_OUT for the commissioning checks (inline at 482)
- TP14 (ruling, decision or rule only: D-15): a test point on the FET side of JP1, so the arming is verified by continuity TP11 to TP14
- U2 (ruling, decision or rule only: D-15, decision 40): the BQ7720700 second-level protector (cell over-voltage, under-voltage, open wire), the owner's D-15 floor

IDs found only on unchanged lines are listed in `changes/changes.json` as `context` and never counted as the change's. The generator diff is `changes/gen_sch_p.diff`.

## Part identity and footprints

49 BOM lines. 14 carry an entry in `v2/vendor/SOURCES.yaml` (identity, grade and the held documents with revision and sha256): 12 joined by the exact LCSC code of the line, and 2 lines that carry NO LCSC code, joined because the entry names this board and either its `where`, read at the revision its line number was written against, points at the line's defining statement while naming the reference or the part, or its fitted order code is written in the line's value. The other 35 lines carry no entry. SOURCES.yaml's own header says which parts it covers (its criteria (a) to (c)) and its `owed` list names the entries still owed; this packet does not judge criticality. `jlc_certified_row` is the certification table's row where it has one: that table was cut from older deliverables and a CERTIFIED there is not proof of identity (SOURCES.yaml header). Full map: `bom/NOT_FOR_FAB-parts-identity.csv` and `bom/parts-identity.json`; which entries name this board and what each joined: `bom/sources-coverage.json`.

**Joined by the line's LCSC code**

| Refs | Value | Footprint | LCSC | SOURCES.yaml | Documents |
|---|---|---|---|---|---|
| D1 | SMBJ20A (pack terminal clamp, unidirectional: cathode on PAC | `Diode_SMD:D_SMB` | C364296 | tvs-surge-clamps | `v2/vendor/power/mdd-smbj-series-tvs.pdf` (Rev:2025A7) |
| D2 | PESD5V0S1BA (SMBC ESD clamp to the pack side of the shunt) | `Diode_SMD:D_SOD-323` | C19224 | esd-headset-clamps | `v2/vendor/nexperia/nexperia-pesd5v0s1ba.pdf` (PESD5V0S1BA v.6, 26 April 2024 (revision) |
| D3 | PESD5V0S1BA (SMBD ESD clamp to the pack side of the shunt) | `Diode_SMD:D_SOD-323` | C19224 | esd-headset-clamps | `v2/vendor/nexperia/nexperia-pesd5v0s1ba.pdf` (PESD5V0S1BA v.6, 26 April 2024 (revision) |
| F2 | SCF9550-30-05 self-control fuse (Eaton, 30 A, 4-5 cells): 1  | `meshsat:Eaton_SCF9550_9.5x5.0mm` | C3670061 | pack-chemical-fuse | `v2/vendor/battery/eaton-scf9550-elx1135.pdf` (effective December 2021 (page 1), Januar) |
| J_TS | JST-PH 1x5 socket for the four cell thermistors (Semitec 103 | `Connector_JST:JST_PH_B5B-PH-K_1x05_P2.00mm_Vertical` | C157993 | jst-ph-headers | `v2/vendor/connectors/jst-ph-catalogue.pdf` (not printed; PDF of 27 January 2026 per ) |
| Q1 | CSD17570Q5B 30 V N-FET, charge switch | `Package_SO:PowerPAK_SO-8_Single` | C529279 | pack-fets | `v2/vendor/battery/ti-csd17570q5b.pdf` (Rev. D, February 2014, revised May 2017) |
| Q2 | CSD17570Q5B 30 V N-FET, discharge switch | `Package_SO:PowerPAK_SO-8_Single` | C529279 | pack-fets | `v2/vendor/battery/ti-csd17570q5b.pdf` (Rev. D, February 2014, revised May 2017) |
| Q3 | AO3400A 30 V N-FET, chemical fuse heater switch | `Package_TO_SOT_SMD:SOT-23` | C20917 | fuse-heater-fet | `v2/vendor/power/aos-ao3400a-n-mosfet.pdf` (Rev 3.1, July 2023) |
| Q5 | 2N7002 60 V N-FET: the second level's under-voltage holds th | `Package_TO_SOT_SMD:SOT-23` | C8545 | logic-nfet-2n7002 | `v2/vendor/power/jscj-2n7002-c8545.pdf` (J, Sep 2016 (as printed)) |
| RT1 | PRF15BB103RB6RC chip PTC 10k, 4.7M at 130 C (Murata): the BQ | `Resistor_SMD:R_0402_1005Metric` | C443668 | pack-ptc-element | `v2/vendor/battery/murata-prf-series.pdf` (Rev.1 201608); `v2/vendor/battery/ti-sluuav7c-bq40z50evm.pdf` (Rev. C, December 2013, revised November ) |
| U1 | BQ4050RSMR: SMBus 1.1 gas gauge, primary protection, 4S bala | `meshsat:Texas_RSM0032A_VQFN-32-1EP_4x4mm_P0.4mm_EP1.4x1.4mm` | C157570 | pack-gauge-protection | `v2/vendor/battery/ti-bq4050.pdf` (Rev. B, March 2016, revised October 2017); `v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf` (Rev. A, April 2016, revised October 2022); `v2/vendor/battery/ti-sluubf9-bq4050evm.pdf` (March 2016 (no revision letter)) |
| U2 | BQ7720700DSSR: second-level cell OV 4.325 V / UV 2.25 V / op | `Package_SON:WSON-12-1EP_3x2mm_P0.5mm_EP1x2.65` | C3681715 | pack-secondary-protector | `v2/vendor/battery/ti-bq77207.pdf` (Rev. D, December 2021, revised May 2026); `v2/vendor/battery/ti-sffs317a-bq77207-fusa.pdf` (SFFS317A, December 2021, revised April 2) |

**Lines with no LCSC code, joined to the entry that covers them.** No order code fixes the maker of such a line, so the entry's identity verdict speaks for the part it names, not for a purchase; the entry says what the line's order code is, or that it is not pinned.

| Refs | Value | Footprint | LCSC | SOURCES.yaml | Joined by | Documents |
|---|---|---|---|---|---|---|
| J_CELL | cell tap sense wires from the 4S block (JST-XH 1x5): B- C1 C | `Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical` | none | pack-and-lid-leads-jst-xh | where gen_sch_p.py:159 at 1f614233 (names J_CELL) | `v2/vendor/connectors/jst-xh-catalogue.pdf` (not printed; the catalogue as served on ) |
| J_SMB | SMBus lead to E6 J_SMB (JST-XH 1x4): SMBC SMBD GND(pack side | `Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical` | none | pack-and-lid-leads-jst-xh | where gen_sch_p.py:481 at 1f614233 (names J_SMB) | `v2/vendor/connectors/jst-xh-catalogue.pdf` (not printed; the catalogue as served on ) |

Every entry of SOURCES.yaml that names board P (and is on this revision's generators) joined at least one BOM line here (11 entries).

Entries that name board P for a part placed on no schematic (by their own `placed_part: false`), so they join no BOM line by design: `pack-cells`.

## Cross-board and harness contracts that touch this board

The revision's own `check_contracts.py`, run in this packet's work copy (never in the repository), traced so each contract carries the boards it names: 4 name board P: **4 PASS, 0 FAIL, 0 UNJUDGED**.

| Result | Contract | Boards | Where |
|---|---|---|---|
| PASS | P: the pack leads are the pack's own two nets, W_P on the positive and W_N on the return | P | `check_contracts.py:368` |
| PASS | E: the XT60 carries the pack on pin 2 and the return on pin 1, which is what P's leads land on | E, P | `check_contracts.py:371` |
| PASS | the pack pair is not crossed between board P's leads and board E's XT60 | E, P | `check_contracts.py:378` |
| PASS | P: the pack's blade fuse is on the netlist and carries a net | P | `check_contracts.py:382` |

## Interfaces declared for this board (`tools/pcb_interfaces.yaml`)

- **SMBUS_GAUGE**: the pack gauge's SMBus, board P's only bus and the one conductor pair that leaves its board. Impedance not stated (tolerance not stated), intra-pair not stated, maximum length not stated. Nets here: SMBC, SMBC_I, SMBD, SMBD_I. Source: TI BQ4050 datasheet, SMBus timing, fSMB (`v2/vendor/battery/ti-bq4050.pdf`).

## Holds and open decisions

- No hold in `tools/pcb_board_holds.yaml` names this board.
- Open decision 42: a decoupling capacitor cannot be both within 3 mm of a fine-pitch pin and outside that part's escape fan (boards: not declared; the text names them).

## Not in this packet

- A layout. The board file of the declared phase is not included and nothing here judges it; whether it carries this netlist is rule SCH-002's question.
- Change marks on the schematic sheets. The PDFs are plain exports of the committed schematic; what changed is marked in the change table above, by reference, with the generator lines that carry each finding ID.
- Calculations and fault-state diagrams. Where the review asks for them (battery protection, board P; the charger state sequence, board A) they are separate work items with their own owner; this packet carries the circuit they will be judged against.
- Physical evidence of any kind.
