# Layout constraint sheets, one per board

MESHSAT-1357, pre-PCB layer 9 of the handover (`v2/docs/reviews/2026-09-27-handover-execution-prompt.md`, sections 3
and 5: "Layout entry requires the reviewed schematic, parts, interfaces, geometry, stackup and electrical
constraints"). Written 27 September 2026 against `main` at `e3aedb25`, and **re-bound to the H2 line after H2 (the
same day, at `ef144760`)**: the table below names the candidate each sheet is now read against, `calc/rail_widths.py`
was re-run on those intent files (its output names each netlist and intent by sha256/16), and each sheet's opening
lines say what was re-read at the H2 line and what stays as read at `e3aedb25`. **Prototype design: no V2 board has
been fabricated, ordered, assembled or powered. No board is ready for layout: 0 of 7 pass the staged layout-entry
test (`v2/docs/CURRENT-EVIDENCE.md`).** A sheet here is an input a layout needs, never an admission to layout.

| Board | Sheet | Candidate it is read against at the H2 line (`CURRENT-EVIDENCE.md`); at `e3aedb25` (history) |
|---|---|---|
| A power | [A.md](A.md) | phase A32; netlist `pcb-a-power-a23/out/pcb-a-power.net` da05dc02bc1e612f, intent 92dd3b1cda9046b8; was netlist 7b08510106687b3d |
| B compute | [B.md](B.md) | phase B21; netlist 8b78c59754a6a0c7, intent 162fcb9b95f680a7; was 669d02d07aeaae4b |
| C panel backer | [C.md](C.md) | phase C24; netlist 11eabc2dddca5161, intent 854436c729322993; was 2834f0d8c4071d56 |
| D APRS | [D.md](D.md) | phase D12; netlist 76700a687eb6187f, intent 443fd745879d3022; was f13d8b70099ab03e |
| E1 dock | [E.md](E.md) | phase E17; netlist d6137f50059e5cbc, intent 5913e38b20333d35; was d910e49c5f5f50b2 |
| P pack BMS | [P.md](P.md) | phase P4; netlist 085f833362fbbda8, intent 6ff1b8129a5c5aff; was 4342c4cbe1b43dc4 |
| E5 dock block | [E5.md](E5.md) | board file 686b29a734c55b9a (no schematic), unchanged |

## What a sheet is, and what it is not

- **A view over the records, never a new authority.** Every constraint names the record it is read from: a registry
  in `v2/ecad/tools/` (`pcb_rules.yaml`, `pcb_decisions.yaml`, `pcb_interfaces.yaml`, `pcb_sensitive.yaml`,
  `pcb_emc.yaml`, `pcb_energy_chain.yaml`, `pcb_board_holds.yaml`, `pcb_requirements.yaml`, `boards/<letter>.json`, the
  board's intent file), a feasibility page (`v2/docs/feasibility/`), a review, a maker's document, or this layer's own
  calculations in `calc/`. Where a sheet and its source disagree, **the source governs** and the sheet is wrong.
- **A sheet adds no rule.** Where the record has a gap, the sheet says so and names who closes it. The one kind of
  line a sheet writes on its own authority is an INFERRED reading of the record (marked so) or a recommendation of the
  session (marked so, with its reason and reversal), under the owner's standing rule of 26 September 2026.
- **Bound to the H2 line since after H2** (the table above), and before that to the committed candidates at
  `e3aedb25`, which the text below describes. At the H2 line `calc/rail_widths.py` changed 41 lines of its output
  against the `e3aedb25` one: board A's VIN_RAW from 12.31 A and 11.92 mm to 14.10 A and 15.29 mm on one outer face,
  rails new on A (PRECHG, VMON, +3V3_EMCON_EF, +3V3_EMCON), B (seventeen, each at most 0.3 A), D (+5V_TX) and E
  (SGP_VDD), board E's VIN_RAW and TRK_OUT at 14.10 A and 10.33 A, and every intent's sha. As first written: Round 8's
  circuit streams change boards A, B, C, D, E and P.
  At the time of writing `fnd/r8int1` (commit `53a98a71`) integrates A, D and E and changes their intent files; its
  rail deltas that move a width are quoted in the sheets as "round 8". That branch reached `main` as `53a98a71` before
  this layer was integrated. **Every sheet is re-read against the netlist and intent file of the merge commit before a
  layout starts** (`calc/rail_widths.py` regenerates the power tables in under a second).

## The rules every sheet applies, and where each comes from

### Current (PI-001, PI-003; decision 35; PWR-F12)

- **Model:** `v2/ecad/tools/track_current.width_for_current`, decision 35 (session, 21 September 2026): the most
  conservative of the three ECSS-Q-ST-70-12C Annex D fits at each area, 10 K rise, an outer conductor at twice the
  internal fit (IPC-2221's own two curves, `track_current.EXTERNAL_FACTOR`).
- **Which current:** a conductor at the rail's TYPICAL current (`dc_drop.py` lines 258 to 264: a 10 K rise is a
  steady-state limit); a via barrel at the PEAK current (`via_current.py`: 18 um hole plating, the fabricator's
  figure); **the pack path at 18 A** (the session's ruling PWR-F12, `v2/docs/feasibility/POWER-THERMAL.md` section 10:
  18 A for 60 s is a service current for every PA key-down) until a transient analysis of that copper at 60 s says
  otherwise. PWR-F12 names board A's pack path; the same chain stages cross E, E5 and P (`pcb_energy_chain.yaml`), so
  their sheets carry it too.
- **Rail current comes from generator-laid copper, never from router tracks** (`v2/ecad/tools/power_copper.py`,
  appendix 32.67 rule 3).
- **The two-face column** of each power table assumes the two outer faces share the current equally; it is INFERRED,
  because the fit is a single-conductor curve and two stacked bands heat each other. It holds only where dc_drop on the
  routed board reads the per-layer share.

### Spacing (ISO-001; decision 34)

ECSS-Q-ST-70-12C Table 13-3 as `v2/ecad/tools/spacing.py` transcribes it (the larger of the per-volt figure and the
floor), judged at each rail's WORKING voltage, for every rail at or above 20 V:

| Working voltage | outer, conformally coated | inner | outer, bare (where the coating is masked) |
|---|---|---|---|
| up to 10 V | 0.120 mm | 0.104 mm | 0.200 mm |
| over 10 to 30 V | 0.120 mm | 0.104 mm | 0.300 mm |
| over 30 V | the larger of 0.002 mm/V and 0.160 mm | the larger of 0.001 mm/V and 0.150 mm | the larger of 0.005 mm/V and 0.500 mm |

The coating is masked at the connector faces, the spring-pin and pack targets, the RF bodies, the module and M.2
receptacles and the test points (`spacing.py` header, citing `ASSEMBLY.md` section 5), so a high-voltage conductor
there takes the bare column. Boards A, B, D, E and E5 declare `conformal_coated: true`; C and P declare false
(`boards/<letter>.json`).

### Return path (RET-001 to RET-004; decision 27)

- Every signal net carries a class and its basis (`boards/<letter>.json` `signal_classes`; an unmatched net is judged
  at the strictest bar). A fast net needs an uninterrupted reference plane on an adjacent layer, with a return
  transition at every reference change (RET-001, RET-003).
- Screens (project calibrations, recorded as such in `pcb_rules.yaml`): uncovered length at most the larger of 10 mm
  or 5 percent of a net (RET-002); a ground via within 1.5 mm of every signal via outside a fine-pitch fan, the fan
  exempt at 0.5 mm (RET-004). Boards C, D and E declare `return_reach_mm: 3.0`.
- A reference change between planes at different potentials takes a stitching capacitor (RET-003).

### Pairs (IMP-001, PAIR-001; decision 36)

- Targets from the part that defines the interface (`v2/ecad/tools/pcb_interfaces.yaml`), never a house number.
- Intra-pair tolerance: the tighter of the interface's own number and the owner's 1.00 mm of 5 September 17:00, which
  stays the floor (decision 36, `interfaces.bar_for`).
- Geometry on each stack: `v2/docs/STACKUP-DECISIONS.md` section 4 and `calc/stack_solves.out` (atlc, calibrated
  against the tree's two recorded solves). Impedance tolerance at the fabricator: plus or minus 10 percent; track
  width tolerance plus or minus 20 percent (`v2/vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md`).

### Decoupling (DEC-001; decision 42, session, 26 September 2026)

The class is the capacitor's role as its maker describes it, never its value (`v2/docs/feasibility/DECOUPLING.md`
section 6):

| Class | What it is | Seat |
|---|---|---|
| R | a converter's own power-stage capacitors | input capacitor on the IC's side across VIN and power ground, no via in the loop, rail pad within 3.0 mm; outputs against the output loop; never on the other side |
| D | a capacitor a maker ties to a supply pin | in the part's own-pin window inside the escape fan, rail pad within 3.0 mm, ground pad to the plane by its own via; a maker's own number is a hard limit (TPA6132A2: within 5 mm, SLOS597B section 9) |
| L | a regulator's output or VCAP capacitor | as D, with the maker's value floor and ESR bound checked |
| A | a supply pin behind a series resistor | the nearest free seat outside the fan at the pin end of its RC, no high-current conductor between |
| B1 | rail bulk the maker calls rail bulk | value and count, no distance |
| B2 | microfarad bulk no maker places | the gate's 6.0 mm |

The fan is the courtyard grown by 2.2 mm (a project number) around every part the escape pass escapes or that has
eight or more copper pads at 1.0 mm pitch or less. The other side is a seat only on boards B, C and D (already
assembled on both sides), never inside a fan box, never over a through-hole part, never for a part whose maker names
its side, judged by in-plane distance plus 3.7 mm (six-layer 3313) or 2.3 mm (JLC04161H-7628). Nothing of this is
implemented at `e3aedb25`: T1 to T10 (tools) and G1 to G14 (generators) are specified in `DECOUPLING.md` section 8,
and the committed intent files carry no class field on any bypass entry.

### Exposed-port protection (TRN-001; decision 31)

The clamp at the entry, between the connector and the first part the conductor meets (after a fuse where a fuse is
in the path, so a sustained overvoltage opens the fuse rather than the clamp), its ground return short and on the
plane (`pcb_board_holds.yaml` `layout_entry_requires`, boards A, D and E; decision 31's executed record). The review
record decision 31 needs at layout entry, `v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md`, does not exist at
`e3aedb25`; the hold itself gates fabrication release.

### Sensitive nodes (ANA-001; decision 45)

`pcb_sensitive.yaml` per board: each node's reference, filter, Kelvin partner and clearance (`keep_mm`) from the
declared switching nets. Kelvin taps leave the shunt's own pad centres as their own conductors, routed together.
Gate-drive rows are reported beside the declared switching nets and not judged (decision 45).

### Fabricator floors (RTE-001, VIA-001, VIA-002)

JLCPCB, read 16 and 25 September 2026 (`v2/vendor/fabricator/`): track and space 0.09 / 0.09 mm multilayer at 1 oz,
0.15 / 0.15 multilayer at 2 oz, 0.16 / 0.16 two-layer at 2 oz; via hole 0.15 mm minimum, diameter 0.25 mm; PTH
annular ring on a multilayer at 1 oz recommended 0.20 mm and at least 0.15, at 2 oz 0.254 mm; solder-mask bridge
0.10 mm at 1 oz and 0.20 mm at 2 oz; through holes only (no blind or buried vias); via-in-pad filled and capped is
the default on six layers and up. The class table in each project file is on the reserved floor
(`v2/ecad/tools/reserved.json`).

### Case and mechanics (MEC-001)

`v2/docs/CASE-MARGINS.md` is the case's record against Peli's own figures. Since 27 September 2026 the targeted
mock-up's checks of the rows that can move a board are **required before the layout entry of boards A, B, E and P**,
and that layout entry is **BLOCKED** on the purchase (FEA-007; `CASE-FIT-UNCERTAINTIES.md` sections 1, 2 and 7;
`CASE-MARGINS.md` section 7 and finding 28). No board of the four enters layout on the nominal geometry in their
place; boards C, D and E5 are not held by it. **Restated at H2:** FEA-007's layout-entry stage holds A, B, D, E, E5 and
P: D and E5 on its desk items alone (D: W4-F17; E5: the dock and blind-mate tolerance stack), A, B, E and P on their
desk items and the mock-up's checks; C is not held by it at layout entry, only at fabrication release. The sheets name
the rows that bear on each board.

### Test access (REQ-048, TST-001)

REQ-048's acceptance is "a per-board test access list (W5) checked against the placed boards before layout entry"
(`pcb_requirements.yaml`). **That list is not in the tree at `e3aedb25`.** Each sheet names what the committed netlist
carries (test points, programming interfaces, arming and boot jumpers) and the bring-up order `v2/docs/PCB-BRING-UP.md`
generates from the intent files; the list itself is owed by the W5 writer.

## Stages every analysis is allocated to

The stage names are the registry's (`pcb_rules.yaml` `verification_phase`; `pcb_requirements.yaml` FEA stages):

- **LAYOUT ENTRY**: what this layer hands over; the sheet's sections 1 to 8.
- **PLACED_BOARD**: SCH-002, DEC-001, GND-002, IMP-002, ANA-001, THM-001, PLC-001, MEC-001, on the placed candidate.
- **ROUTED_BOARD**: SCH-003, PI-001 to PI-003, GND-001, STK-001, RET-001 to RET-004, IMP-001, PAIR-001, RF-001,
  ISO-001, PLC-002, RTE-001, RTE-002, VIA-001, VIA-002, PLN-001, EMC-001, on the routed candidate.
- **FABRICATION_RELEASE**: the holds of `pcb_board_holds.yaml` and each FEA blocker's release stage
  (`CURRENT-EVIDENCE.md`, "Held at later stages").
- **PROTOTYPE**: INT-003, REL-001, the FEA blockers' prototype stages, `TEST-PLAN.md` and `PCB-BRING-UP.md`.

Each sheet's last section lists the ones that apply to its board, with what each needs.

## Files

- `calc/rail_widths.py` and `calc/rail_widths.out`: the power tables (stdlib, any host, under a second); the output is
  the run at the H2 line (after H2), each table headed by the netlist and intent it read.
- `calc/stack_solves.py` and `calc/stack_solves.out`: the pair and RF line solves (atlc 4.6.1; run on the rented box,
  30 s on 12 workers). They depend on the stacks' geometry and the pair classes' widths, not on a netlist, so they
  were not re-run at the H2 line.
- `v2/docs/STACKUP-DECISIONS.md`: the per-board stackup record the sheets' section 1 summarises.
