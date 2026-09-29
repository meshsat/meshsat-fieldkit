# Board B (compute): layout constraints

**Bound to the set 6 candidate (27 September 2026, read at `760d7f41`).** This sheet's inputs stand in the block below,
one to a line, each with its sha256/16 and the commit it last changed in, with the model and the stack the widths were
computed on; `v2/ecad/tools/constraints_bound.py` fails when a committed input, the calculation or this sheet's power
table moves without the others (README, "The bound block"). **Re-read on this candidate: section 2 alone.** Its power
table is `calc/rail_widths.py`'s output on the inputs below, and the widths, currents and barrel counts the text under
the table quotes were compared with the table and agree. **Not re-read on this candidate: sections 1 and 3 to 11**,
which are the readings at `e3aedb25` with the H2 line's changes marked where they stand (`ef144760`, the paragraph
below). Set 6 changed board B's netlist and intent file in `910da406` (EMCON forces the RockBLOCK's ENABLE low and
drives each card rail's enable from its slot's own 5 V): four decoupling entries (C607, C637, C667, C559), the gates
U116, U216, U316 and U536 entered as loads of 1 to 2 mA, and the switch and enable net of +5V_LORA, +5V_LIME and +5V_RB
declared. No rail's declared typical or peak current changed: **no row of the power table moved**. A line of the older
sections that names a part, a net, a current or a count is compared with the netlist and the intent file below before it
is followed, and where this sheet and a record disagree the record governs (README). Board B is not at layout entry: no
board is (`v2/docs/CURRENT-EVIDENCE.md`, which holds the reasons current on this candidate; a count of reasons in a
paragraph below is its own binding's).

```bound
sheet      B
board      b
read       2026-09-29 at 3d3e32d6
current    section 2: the power table, and the figures the text under it quotes from it
older      sections 1 and 3 to 11: read at e3aedb25, with the H2 line's changes marked at ef144760
netlist    v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net sha256/16 e7e683207d084d61 changed 3d3e32d6
intent     v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json sha256/16 65f525bb5ae37e0d changed 3d3e32d6
board_file v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_pcb sha256/16 2e64b5bf2d9cd3bc changed f2541bea
model      track_current.width_for_current decision 35 rise 10 K plating 18 um
stack      JLC06161H-3313 outer 0.0350 mm inner 0.0152 mm
```

**As re-bound to the H2 line (after H2, 27 September 2026), kept as that binding's record.** Candidate re-read at `ef144760`: phase B21, netlist
`v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net` sha256/16 `8b78c59754a6a0c7` (board B's round 8 at `b76c18cb`, last
changed by set 5 at `caba1876`), intent `pcb-b-compute-intent.json` `162fcb9b95f680a7`; the committed board file
`2e64b5bf2d9cd3bc` carries B21's older netlist (SCH-002 FAIL) and 416 unrouted connections. Section 2's table is
checked against `calc/rail_widths.py` on that intent: every rail it lists reads the same; the H2 intent declares seventeen
more supplies, each at most 0.3 A typical (the added row, marked **H2**). Board B is not at layout entry: **7 reasons at H2**
(`CURRENT-EVIDENCE.md`): SI-001 INCONCLUSIVE, RF-002 FAIL (EQ-25), FEA-001, FEA-002, FEA-003, FEA-006, FEA-007. Known
changes of the H2 line to the rest of this sheet: round 8 is merged (`b76c18cb`: the fabric's locked break-before-make,
FAB-01 to FAB-04, EMCON on each module's own rail, the 5G module's supply removed in hardware, the M.2 socket's
locating holes, F1 the MF-MSMF110), and set 5 declared every supply from its maker's sheet with decision 42's class on
every decoupling entry (`caba1876`); PANEL_5V's row is corrected below. Every other line below is the reading at `e3aedb25`, not re-read against the H2 netlist; where it and a record disagree, the record governs (README).

As first written: a view over the records at `main` `e3aedb25` (conventions and shared rules: [README.md](README.md)),
candidate then netlist `669d02d07aeaae4b`, intent `cf461c0b75ce368b`, 16 blocker lines, round 8 not yet integrated
(the lines below were to be re-read on its merge; FB-FAB-1 to FB-FAB-5 of `v2/docs/feasibility/FAILOVER-FABRIC.md`
closed on it first).

**Board B has no layout candidate yet and no layout should start from this sheet alone**: its stackup is undecided
(section 1) and its escape and placement strategy is FB-FAB-6, owed by Q-B-ESC-2 and decision 43's whole-board run.

## 1. Stackup and layer use: UNDECIDED

- **As built:** six layers, JLC06161H-3313, 1 oz outer, 0.0152 mm inner: F sig, In1 GND, In2 sig, In3 sig, In4 four
  split 5 V planes (+5V_DEV, +5V_S1, +5V_S2, +5V_S3), B sig (zone census of B21; `B-FEASIBILITY.md` section 3.2).
- **Candidates and what decides between them:** `v2/docs/STACKUP-DECISIONS.md` section 4. In short: option A2 (In3 to
  GND) gives three controlled routing layers on a board that did not route with four; eight layers (JLC08161H-2116,
  recorded in `STACKS`, owner decision 43's measurement) give four. **The session's recommendation for decision 43's
  run input, not a decision:** S G S G P S G S, 5 V domains on In4, pairs on In5 kept inside one 5 V region or with a
  stitching capacitor at every crossing (RET-003). Price: none; the eight-layer price goes to the owner before any
  order (decision 43).
- **Two sides assembled:** B21 carries 464 SMD footprints on its back; the underside rule is "never beneath a
  fine-pitch part whose escapes need the vias" (`gen_pcb_b3.py:155`, quoted in decision 42).

## 2. Power: band widths at the declared currents

From `calc/rail_widths.py` (decision 35, 10 K). Where a maker's figure exceeds the declaration (POWER-THERMAL PWR-F01,
F03, F05), the maker's figure is the one to size to: the first table is the declaration's, its row says so in its note,
and the second table sizes the same rail at the maker's figure.

The table is `calc/rail_widths.py`'s output on the inputs this sheet's `bound` block names, row for row in the tool's
own order and cell for cell, and `v2/ecad/tools/constraints_bound.py` fails when the two differ; the `note` column is
this sheet's and is not compared (README, "The bound block"). A width printed 0.00 is under 0.005 mm, a current of a few
milliamperes: the fabricator's floor governs there, not the current.

| rail | V (working) | typ / peak A | governing A | outer mm | two outer faces, each mm | inner mm | barrels at the larger of peak and governing, 0.3 / 0.4 / 0.5 mm drill | note |
|---|---|---|---|---:|---:|---:|---|---|
| +5V_S1 | 5.10 | 2.50 / 5.00 | 2.50, typical (PI-001) | 1.06 | 0.41 | 6.36 | 7 / 6 / 5 | a slot rail, a plane on In4 today |
| +5V_S2 | 5.10 | 4.20 / 5.63 | 4.20, typical (PI-001) | 2.17 | 0.84 | 13.64 | 8 / 7 / 6 | Moved at integration set 8 by S-98: board B's own peak call now declares the 5.63 A coincident peak its comment derived (5.00 before), and both ends of the lead declare 4.20 A typical and 5.63 A peak (IF-AB-POWER AGREE, INTERIM); the widths are unchanged (governing typical 4.20 A), the barrel counts follow the larger peak. Before: `typ / peak A` was 4.20 / 5.00; `barrels at the larger of peak and governing, 0.3 / 0.4 / 0.5 mm drill` was 7 / 6 / 5) the 5G slot; board A declares 2.5 A typical for the same conductor (`pcb_interfaces.yaml` IF-AB-POWER, status DISAGREE, I-03 open. |
| +5V_S3 | 5.10 | 2.50 / 5.00 | 2.50, typical (PI-001) | 1.06 | 0.41 | 6.36 | 7 / 6 / 5 | a slot rail, a plane on In4 today |
| +5V_DEV | 5.00 | 3.80 / 6.00 | 3.80, typical (PI-001) | 1.89 | 0.73 | 11.36 | 9 / 7 / 6 | the device rail; its declared children and its peak are the question of `boards/b.json` `_b_feeders_declared_and_the_device_rail_is_short_at_peak` |
| +3V3_DEV | 3.30 | 1.20 / 2.00 | 1.20, typical (PI-001) | 0.39 | 0.15 | 2.31 | 3 / 3 / 2 |  |
| +3V3_S1A | 3.30 | 0.50 / 1.50 | 0.50, typical (PI-001) | 0.12 | 0.04 | 0.69 | 3 / 2 / 2 | **declared below its maker's figure** (PWR-F01): size it by the second table |
| +3V3_M2C1 | 3.30 | 0.50 / 1.50 | 0.50, typical (PI-001) | 0.12 | 0.04 | 0.69 | 3 / 2 / 2 | **declared below its maker's figure** (PWR-F01): size it by the second table |
| +3V3_S1B | 3.30 | 0.90 / 1.80 | 0.90, typical (PI-001) | 0.26 | 0.10 | 1.56 | 3 / 3 / 2 |  |
| +1V0_S1 | 1.00 | 0.80 / 1.20 | 0.80, typical (PI-001) | 0.22 | 0.08 | 1.32 | 2 / 2 / 2 |  |
| +1V1_S1 | 1.10 | 0.40 / 0.70 | 0.40, typical (PI-001) | 0.08 | 0.03 | 0.51 | 1 / 1 / 1 | **its peak is declared below the maker's four-SS row** (PWR-F05): the second table |
| +3V3_CM1 | 3.30 | 0.10 / 0.20 | 0.10, typical (PI-001) | 0.01 | 0.00 | 0.08 | 1 / 1 / 1 |  |
| +1V8_CM1 | 1.80 | 0.02 / 0.05 | 0.02, typical (PI-001) | 0.00 | 0.00 | 0.01 | 1 / 1 / 1 |  |
| +3V3_S2A | 3.46 | 3.00 / 4.00 | 3.00, typical (PI-001) | 1.37 | 0.53 | 8.18 | 6 / 5 / 4 | the RM520N-GL socket |
| +3V3_M2C2 | 3.46 | 3.00 / 4.00 | 3.00, typical (PI-001) | 1.37 | 0.53 | 8.18 | 6 / 5 / 4 | the RM520N-GL socket, past its Kelvin shunt |
| +3V3_S2B | 3.30 | 0.90 / 1.80 | 0.90, typical (PI-001) | 0.26 | 0.10 | 1.56 | 3 / 3 / 2 |  |
| +1V0_S2 | 1.00 | 0.80 / 1.20 | 0.80, typical (PI-001) | 0.22 | 0.08 | 1.32 | 2 / 2 / 2 |  |
| +1V1_S2 | 1.10 | 0.40 / 0.70 | 0.40, typical (PI-001) | 0.08 | 0.03 | 0.51 | 1 / 1 / 1 | **its peak is declared below the maker's four-SS row** (PWR-F05): the second table |
| +3V3_CM2 | 3.30 | 0.10 / 0.20 | 0.10, typical (PI-001) | 0.01 | 0.00 | 0.08 | 1 / 1 / 1 |  |
| +1V8_CM2 | 1.80 | 0.02 / 0.05 | 0.02, typical (PI-001) | 0.00 | 0.00 | 0.01 | 1 / 1 / 1 |  |
| +3V3_S3A | 3.30 | 0.50 / 1.50 | 0.50, typical (PI-001) | 0.12 | 0.04 | 0.69 | 3 / 2 / 2 | **declared below its maker's figure** (PWR-F01): size it by the second table |
| +3V3_M2C3 | 3.30 | 0.50 / 1.50 | 0.50, typical (PI-001) | 0.12 | 0.04 | 0.69 | 3 / 2 / 2 | **declared below its maker's figure** (PWR-F01): size it by the second table |
| +3V3_S3B | 3.30 | 0.90 / 1.80 | 0.90, typical (PI-001) | 0.26 | 0.10 | 1.56 | 3 / 3 / 2 |  |
| +1V0_S3 | 1.00 | 0.80 / 1.20 | 0.80, typical (PI-001) | 0.22 | 0.08 | 1.32 | 2 / 2 / 2 |  |
| +1V1_S3 | 1.10 | 0.40 / 0.70 | 0.40, typical (PI-001) | 0.08 | 0.03 | 0.51 | 1 / 1 / 1 | **its peak is declared below the maker's four-SS row** (PWR-F05): the second table |
| +3V3_CM3 | 3.30 | 0.10 / 0.20 | 0.10, typical (PI-001) | 0.01 | 0.00 | 0.08 | 1 / 1 / 1 |  |
| +1V8_CM3 | 1.80 | 0.02 / 0.05 | 0.02, typical (PI-001) | 0.00 | 0.00 | 0.01 | 1 / 1 / 1 |  |
| +3V3_IOCA | 3.30 | 0.12 / 0.25 | 0.12, typical (PI-001) | 0.02 | 0.01 | 0.10 | 1 / 1 / 1 |  |
| +3V3_IOCB | 3.30 | 0.12 / 0.25 | 0.12, typical (PI-001) | 0.02 | 0.01 | 0.10 | 1 / 1 / 1 |  |
| +3V3_IOCC | 3.30 | 0.12 / 0.25 | 0.12, typical (PI-001) | 0.02 | 0.01 | 0.10 | 1 / 1 / 1 |  |
| +1V2_KSZ | 1.20 | 0.50 / 0.80 | 0.50, typical (PI-001) | 0.12 | 0.04 | 0.69 | 2 / 1 / 1 | **declared below its maker's figure** (PWR-F03): size it by the second table |
| +2V5_KSZ | 2.50 | 0.15 / 0.25 | 0.15, typical (PI-001) | 0.02 | 0.01 | 0.13 | 1 / 1 / 1 | **declared below its maker's figure** (PWR-F03): size it by the second table |
| +3V3_ZB | 3.30 | 0.10 / 0.30 | 0.10, typical (PI-001) | 0.01 | 0.00 | 0.08 | 1 / 1 / 1 |  |
| +5V_LORA | 5.00 | 0.15 / 0.70 | 0.15, typical (PI-001) | 0.02 | 0.01 | 0.13 | 1 / 1 / 1 |  |
| +5V_LIME | 5.00 | 1.20 / 3.00 | 1.20, typical (PI-001) | 0.39 | 0.15 | 2.31 | 5 / 4 / 3 | the SDR bay's eFuse; its peak with +5V_RB's is the fabric question of `_b_feeders_declared_and_the_device_rail_is_short_at_peak` |
| +5V_RB | 5.00 | 0.15 / 2.00 | 0.15, typical (PI-001) | 0.02 | 0.01 | 0.13 | 3 / 3 / 2 | the satellite modem: "burst current on a transmit attempt is the number the copper has to carry, not its average", so the peak sets the barrels |
| +5V_CAM | 5.00 | 0.25 / 0.50 | 0.25, typical (PI-001) | 0.04 | 0.02 | 0.27 | 1 / 1 / 1 |  |
| +5V_HDMI | 5.00 | 0.10 / 0.50 | 0.10, typical (PI-001) | 0.01 | 0.00 | 0.08 | 1 / 1 / 1 |  |
| +54V_POE | 54.00 | 0.30 / 0.60 | 0.30, typical (PI-001) | 0.06 | 0.02 | 0.34 | 1 / 1 / 1 | spacing governs, section 8 |
| GND | 0.00 | 10.00 / 21.00 | 10.00, typical (PI-001) | 8.15 | 2.76 | 66.76 (over 40 mm) | 29 / 24 / 20 | the return of the four input rails, carried by the In1 plane and the outer pours: the widths are what one conductor would need and no band is asked for; the barrels are per transition, at the 21 A peak |
| VBUS_FLASH1 | 5.00 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1 | **H2**, new in `caba1876`: "it feeds only the USBLC6-2SC6's VBUS reference (pin 5)"; nanoamperes, which print as 0.00 |
| SIM1_VCC | 3.00 | 0.01 / 0.05 | 0.01, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1 | **H2**, new in `caba1876`: "SIM 1's supply from the module's USIM1_VDD"; the 50 mA peak is INFERRED, the intent file says |
| SIM2_VCC | 3.00 | 0.01 / 0.05 | 0.01, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1 | **H2**, new in `caba1876`: "SIM 2's supply from the module's USIM2_VDD" |
| SIMC2_VCC | 3.00 | 0.01 / 0.05 | 0.01, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1 | **H2**, new in `caba1876`: "SIM 2's supply at the holder, past the 0 Ohm eSIM option link R272" |
| VBUS_FLASH2 | 5.00 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1 | **H2**, new in `caba1876`: as VBUS_FLASH1 |
| VBUS_FLASH3 | 5.00 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1 | **H2**, new in `caba1876`: as VBUS_FLASH1 |
| VBAT_RTC | 3.00 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1 | **H2**, new in `caba1876`: "the CR2032's 3 V to the three modules' RTC inputs (pin 76)"; microamperes, which print as 0.00 |
| POE_P | 54.00 | 0.30 / 0.60 | 0.30, typical (PI-001) | 0.06 | 0.02 | 0.34 | 1 / 1 / 1 | **H2**, new in `caba1876`: "a series segment of +54V_POE at the port's 0.60 A peak"; spacing governs, section 8 |
| MDI_A_P | 54.00 | 0.15 / 0.30 | 0.15, typical (PI-001) | 0.02 | 0.01 | 0.13 | 1 / 1 / 1 | **H2**, new in `caba1876`: "a series segment of POE_P carrying half its current, and a 1000BASE-T signal conductor"; spacing governs, section 8 |
| MDI_A_N | 54.00 | 0.15 / 0.30 | 0.15, typical (PI-001) | 0.02 | 0.01 | 0.13 | 1 / 1 / 1 | **H2**, new in `caba1876`: as MDI_A_P |
| MDI_B_P (return of +54V_POE) | 0.15 | 0.15 / 0.30 | 0.15, typical (PI-001) | 0.02 | 0.01 | 0.13 | 1 / 1 / 1 | **H2**, new in `caba1876`: "half the port's return from the jack's pin 3"; "up to 57 V with it off", so spacing governs, section 8 |
| MDI_B_N (return of +54V_POE) | 0.15 | 0.15 / 0.30 | 0.15, typical (PI-001) | 0.02 | 0.01 | 0.13 | 1 / 1 / 1 | **H2**, new in `caba1876`: as MDI_B_P |
| POE_DRAIN (return of +54V_POE) | 0.15 | 0.30 / 0.60 | 0.30, typical (PI-001) | 0.06 | 0.02 | 0.34 | 1 / 1 / 1 | **H2**, new in `caba1876`: "the port's return from T1's centre tap MCT2 (pin 21) to the drain of the port switch Q1"; "up to 57 V with it off" |
| POE_SEN (return of +54V_POE) | 0.15 | 0.30 / 0.60 | 0.30, typical (PI-001) | 0.06 | 0.02 | 0.34 | 1 / 1 / 1 | **H2**, new in `caba1876`: "the port's return from Q1's source to the 0.25 Ohm sense resistor R12" |
| GNSS_VDD_RF | 3.30 | 0.02 / 0.03 | 0.02, typical (PI-001) | 0.00 | 0.00 | 0.01 | 1 / 1 / 1 | **H2**, new in `caba1876`: "the active antenna's supply from the LG290P's VDD_RF to R23"; the currents are INFERRED, the intent file says |
| GNSS_BIAS | 3.30 | 0.02 / 0.03 | 0.02, typical (PI-001) | 0.00 | 0.00 | 0.01 | 1 / 1 / 1 | **H2**, new in `caba1876`: "a series segment of GNSS_VDD_RF" |
| GNSS_ANT | 3.30 | 0.02 / 0.03 | 0.02, typical (PI-001) | 0.00 | 0.00 | 0.01 | 1 / 1 / 1 | **H2**, new in `caba1876`: "a series segment of GNSS_VDD_RF" |
| VBUS_QMX | 5.00 | 0.30 / 0.30 | 0.30, typical (PI-001) | 0.06 | 0.02 | 0.34 | 1 / 1 / 1 |  |
| PANEL_5V | 5.00 | 0.60 / 0.60 | 0.60, typical (PI-001) | 0.15 | 0.06 | 0.89 | 1 / 1 / 1 | behind F1, an MF-MSMF110 (1.1 A hold, 2.2 A trip) since round 8, `b76c18cb` (`boards/b.json` `_panel_5v_fuse_r8_why`): the copper must clear the fuse's hold, which the width of this row does not say. The record's answer is the PANEL class at 0.8 mm in `gen_pcb_b3.py` for the next cut (`pcb_energy_chain.yaml` stage B_PANEL_5V); board C declares 1.0 A peak on the same conductor |

Sized at the maker's figure, above the declaration (`calc/rail_widths.py` SIZED_TO;
`v2/docs/feasibility/POWER-THERMAL.md` section 10). The declaration is unchanged and is board B's owner's to correct;
until it is, these are the widths and barrel counts to follow:

| rail | declared typ / peak A | sized at, A | outer mm | two outer faces, each mm | inner mm | barrels at the larger of the declared peak and the sized current, 0.3 / 0.4 / 0.5 mm drill | the maker's figure and its finding |
|---|---|---|---:|---:|---:|---|---|
| +3V3_S1A | 0.50 / 1.50 | 3.000 | 1.37 | 0.53 | 8.18 | 5 / 4 / 3 | PWR-F01: AsiaRF asks a 3.3 V supply of 3 A (2.5 A minimum) for the AW7915-AED |
| +3V3_M2C1 | 0.50 / 1.50 | 3.000 | 1.37 | 0.53 | 8.18 | 5 / 4 / 3 | PWR-F01, the same conductor past its Kelvin shunt |
| +3V3_S3A | 0.50 / 1.50 | 3.000 | 1.37 | 0.53 | 8.18 | 5 / 4 / 3 | PWR-F01 |
| +3V3_M2C3 | 0.50 / 1.50 | 3.000 | 1.37 | 0.53 | 8.18 | 5 / 4 / 3 | PWR-F01, the same conductor past its Kelvin shunt |
| +1V2_KSZ | 0.50 / 0.80 | 1.210 | 0.39 | 0.15 | 2.34 | 2 / 2 / 2 | PWR-F03: KSZ9897R at 1000 Mb/s draws 1.21 A typical on its 1.2 V rails |
| +2V5_KSZ | 0.15 / 0.25 | 0.330 | 0.07 | 0.03 | 0.39 | 1 / 1 / 1 | PWR-F03: 330 mA on AVDDH |
| +1V1_S1 | 0.40 / 0.70 | 0.778 | 0.21 | 0.08 | 1.27 | 2 / 1 / 1 | PWR-F05: TUSB8041's four-SS-devices row, 778 mA on VDD; the kit's mix uses the 395 mA row |
| +1V1_S2 | 0.40 / 0.70 | 0.778 | 0.21 | 0.08 | 1.27 | 2 / 1 / 1 | PWR-F05 |
| +1V1_S3 | 0.40 / 0.70 | 0.778 | 0.21 | 0.08 | 1.27 | 2 / 1 / 1 | PWR-F05 |

## 3. Pairs: targets, geometry, budgets

Targets and intra-pair bars from `pcb_interfaces.yaml` (the host's and the module's own clauses) and decision 36:

| Interface | Nets (board b assignments) | Class | Target | Intra-pair | Length limit |
|---|---|---|---|---|---|
| PCIE_CM5 | PCIE* | USB | 90 ohm plus or minus 10 % (CM5 2.3) | 0.10 mm | none published; pair-to-pair matching unnecessary |
| PCIE_M2_MODULE | NVME*, CARD* RX/TX/CLK | USB | 85 ohm plus or minus 10 % (RM520N-GL); 90 meets both ends | 0.70 mm | 200 mm |
| USB3_CM5 | HOST*, BANK*, MUX*, LIME_SS* | USB | 90 ohm plus or minus 10 % | 0.10 mm | none held |
| USB2_CM5 | USB*, HUB*, LIME_D*, CAM_D*, QMX_D* | USB | 90 ohm plus or minus 10 % | 0.15 mm | none held |
| ETHERNET_CM5 | ETH*, SWP* | DIFF100 | 100 ohm plus or minus 10 % | 0.15 mm | pair-to-pair differences under 50 mm |
| HDMI_CM5 | HDMI*_D*, HDMI*_CK_* | DIFF100 | 100 ohm plus or minus 10 % | 0.15 mm | none held |

- **Geometry on the six-layer stack as built** (`calc/stack_solves.out`): outer 0.130 / 0.127 mm for 90 ohm and
  0.098 / 0.127 or 0.125 / 0.200 for 100 ohm; the class table's USB 0.127 / 0.13 and DIFF100 0.127 / 0.20 meet them on
  the outer layers (90.7 and 99.2 ohm). **In2 and In3 do not:** B21's DIFF100 on In2 reads 110.5 ohm over In4's plane
  and 140.5 where In4 is split (`STACKUP-DECISIONS.md` section 4). So on six layers as built, **controlled pairs run on
  F.Cu and B.Cu only**, which is the pre-router's own layer set (`boards/b.json` pair_layers), and the router's pairs on
  In2 and In3 are out of tolerance.
- **On the eight-layer candidate:** one width per target on every routing layer, 0.148 / 0.127 mm for 90 ohm and
  0.112 / 0.127 for 100 ohm (section 1; `STACKUP-DECISIONS.md` section 4).
- **The transformerless module links** (INT-002, `reviews/INT-002-PRE-LAYOUT-ASSESSMENT.md` section 6, bound to 48 nets
  by digest `262e8b039e833d02`): 100 ohm differential; legs matched within 0.15 mm; pair-to-pair differences under
  50 mm; **one series 0.1 uF capacitor per conductor with nothing between the switch pin and the capacitor** (Microchip
  DS00004151A clause 6.6). The capacitors' voltage and dielectric are not in the netlist (INT-002 section 5 item 3).
- **Channel budgets: none held** (FB-FAB-7). The placement screen's lengths the layout must budget against
  (`FAILOVER-FABRIC.md` section 8.3, Manhattan between footprint origins on B21, so a routed run is longer): PCIe
  upstream 117.6 / 140.0 / 129.0 mm; switch to NVMe 53.9 / 44.5 / 57.7 and to card 81.1 / 70.7 / 88.5 mm (the RM520N's
  200 mm is met); USB home 185.2 / 117.9 / 196.6 mm; **USB failover up to 255.2 mm plus the TMUXHS4212's insertion loss
  (-1.3 dB at 5 GHz)**; **HDMI up to 396.2 mm through two TS3DV642**; LimeSDR 217.0 mm; Ethernet 92.8 / 162.8 / 232.8 mm.
  A per-link budget from a primary document is owed before the fabric's placement is frozen (FEA-003's layout-entry
  stage).
- **Reference clocks:** every clock output pair of the switch is AC coupled and source terminated on the corrected
  netlist, and the corrected slot 3 seats **18 parts beside U301** (six at its north-row pins, twelve at its east-row
  clock outputs) in a pocket that had 0.0 mm of room (FAB-08, `FAILOVER-FABRIC.md`; `B-FEASIBILITY.md` section 1).

## 4. Return paths

- Board B's signal table makes most nets strict (`boards/b.json` `signal_classes`, "most of this table is strict").
  On six layers as built, a B.Cu pair crossing between the slot rails' planes on In4 crosses a reference-plane split
  (`B-FEASIBILITY.md` section 3.2, INFERRED from the zone list): keep B.Cu pairs inside one In4 region, or carry a
  stitching capacitor at the crossing (RET-003).
- RET-004's 1.5 mm ground via applies outside the fine-pitch fans; the three CM5 receptacles' 0.4 mm rows are fans.

## 5. Decoupling (decision 42)

- **Other side allowed on board B** outside every fan box, never over a through-hole part, never for the STM32H743 in
  its LQFP or for a converter (`DECOUPLING.md` section 6), judged at in-plane distance plus 3.7 mm on the six-layer
  stack.
- **Class R:** the seven TPS62933, the AP64500 slot bucks, the AP63203 (U25) and the TPS23861's supply.
- **Generator items owed** (`DECOUPLING.md` section 8.3): G4 (the 0.1 uF at VIN on all seven TPS62933), G5 (C37 and C38
  re-declared against the TS3DV642 VCC pins), G6 (declare the STM32H743, PI7C9X2G404SL, TUSB8041, KSZ9897R, TMUXHS4212,
  TS3USB221A and CP2102N capacitors with classes; none is declared today), G7 (the STM32H743's VDDA 100 nF plus 1 uF,
  four more 0.1 uF on the TUSB8041 core, the KSZ9897R per the maker's example, the CP2102N's 4.7 uF plus 0.1 uF at
  VREGIN), G10 (U25's C4 at pin 3, C5 and C6 against the output loop; U27's C12 class L, C13 class D).
- **The PI7C9X2G404SL's requirement is TBD:** its datasheet gives none; the Diodes question is drafted, not sent
  (`records/rv-dec/dec-request-diodes-pi7c9x2g404sl.md`).
- DEC-001's PASS of 30 of 30 on B21 is 30 blanket allowances, not evidence (`DECOUPLING.md` section 9).

## 6. Placement

1. **The floor plan is the open question, not a setting** (`B-FEASIBILITY.md` sections 3.3 and 5): each slot's fabric
   sits 85 to 90 mm from its receptacle beyond the M.2 row; the three switch pockets have 0.0 mm of room; the room on the
   board is elsewhere (WIFISW 38.5 mm north, IOCA 19.0, S1_RAILB 19.0, S2_RAILB 16.0). The paper study of option A4 (each
   slot's switch, hub and muxes beside its receptacle's B half, north of the M.2 row) with A2 and A7 is owed; board B's
   rectangles were released by owner ruling 13, so this is the session's.
2. **Escape:** through vias only at the fabricator; via-in-pad (filled and capped, the default on six layers and up)
   has never been used for the fine-pitch signal escapes and needs an `escape.py` mode and a fabricator answer
   (`B-FEASIBILITY.md` option A3). Q-B-ESC-2 (section 7.9) tests the escape and placement remedy on the corrected
   netlist.
3. **Hot parts** (`POWER-THERMAL.md` 9.2): KSZ9897RTXI +28.7 K junction to air on a six-layer JESD51 board (11.3 C/W at
   2.54 W); PI7C9X2G404SL +16 to +27 K (25.5 C/W); the AP2112K supervisor LDOs U40, U50, U60 at 184 C/W: +43 K at PLAN,
   **+152 K at the STM32H743's 400 MHz maximum, past the part's 150 C absolute maximum at any inside air** (PWR-F04:
   bound the supervisor clock to 200 MHz VOS3, +63 K, or feed the LDOs from 3.3 V; board B's owner and the firmware
   contract); U27 (the KSZ's 2.5 V) +49 K. Each takes copper area and vias under its tab as its package allows.
4. **T1, the H5007NL magnetics, is rated 0 to +70 C** against the -20 to +40 C envelope (`boards/b.json`
   `_t1_magnetics_is_a_commercial_temperature_part_why`); keep it away from the hot parts above. The HX5004NL is the
   maker's extended-temperature part in the same mechanical group; pin compatibility is not claimed.
5. **INT-002's fallback made cheap (open, the board B stream's decision):** decision 29 keeps the three module links
   capacitive; its fallback is magnetics, today a respin. A DNP magnetics footprint on the three links would make it a
   population change (`CURRENT-EVIDENCE.md`; INT-002 section 5). Not decided here.
6. **U8, the secure element:** its part and land are FEA-001's layout-entry stage (the ATECC608B pass records, or the
   SLB 9673 or SE050E2HQ1 on the U8 site); nothing else on board B depends on it (`ZEROIZE.md` section 7).
7. **Case:** B is 330 x 200 mm; the stack lifts out through the frame window with 9.83 mm per side in X nominal and
   8.25 at the worst of Peli's figures (M7, MET); the setting legs keep 4.52 mm to B's corner at the worst (M21f); the
   east bundle's lane beside B's edge is M17d (OPEN) and M17x reads OPEN, FAILS AS ASSUMED at the worst (-0.38 against
   1.0) until the jumper plug is picked (`CASE-MARGINS.md` 3.2, finding 27). The monitor body over the CM5 heatsinks is
   M1, OPEN. Outline growth is bounded by those rows (`B-FEASIBILITY.md` option A6).
8. **Test access:** 88 test points; J_DBG1 to J_DBG3 (each module's console UART and I2C), J_RPIBOOT1 to J_RPIBOOT3
   with J_FLASH1 to J_FLASH3 (each module's eMMC over USB), J_ZBDBG1 and J_ZBDBG2 (the CC2652P cJTAG), and U42, U52,
   U62 (SWD pads of the three supervisors) on the committed netlist. The committed B21 board carries a through-hole SWD
   land where the netlist carries the SMD one (W7-R2-01, `ARCHITECTURE.md` line 194). Bring-up order:
   `PCB-BRING-UP.md` board B (8 inputs applied, 19 rails measured).

## 7. Protection placement (TRN-001)

| Port | Conductor | Part | Constraint |
|---|---|---|---|
| J_ETH (the internal RJ45 whose patch lead reaches the sealed wall jack) | the four MDI pairs, T1 to the jack | T1 (magnetics) | keep T1 at J_ETH; the MDI pairs have no entry in `pcb_interfaces.yaml` and no declared tolerance (decision 36's measurement found them judged by neither number), so an entry is owed before their geometry is judged |
| J_54V (PoE feed, leaves the case on the same wall jack) | +54V_POE | D2 SMBJ58A (intent clamps) | at the connector, ground return short and on the plane (decision 31's placement rule) |

The slot rails carry D101, D201, D301 SMBJ6.0A, +5V_DEV D1 SMBJ5.0A and +3V3_M2C2 D520 SMBJ5.0A (intent clamps).
TRN-001 reads FAIL on board B on the clamp symbol only (`PCB-RULE-STATUS-B.md` TRN-001 row); no decision 31 hold is on
board B.

## 8. Spacing (ISO-001)

+54V_POE (54 V): at least 0.160 mm outer coated, 0.150 mm inner, 0.500 mm where the coating is masked (the RJ45, the
M.2 and module receptacles, the test points). B21 reads PASS, closest 0.183 mm (`routed/spacing.verdict.json`).

## 9. Thermal

- The modules: three CM5 under coolers with their own fans (J_FAN1 to J_FAN3; fan picks are D-18), the TMP117 under
  the coolers reads the pocket (`gen_sch_b.py` line 1050). The inside-air bound includes failure for three loaded
  modules at +20 C on the independent bound (`POWER-THERMAL.md` 9.1 and 9.2; FEA-004), and three-module redundancy in the
  heat depends on the enclosure test.
- The AW7915-AED (0 to +70 C, 4 to 9 W own rise TBD, no heat path designed) and the LimeSDR Mini (0 to +70 C) are
  outside the envelope's cold end (PWR-F09); the RM520N-GL has up to 5.6 W of own rise TBD. Their sockets' copper and
  the airflow path are layout inputs the enclosure test decides.

## 10. Analyses that need placed or routed geometry, or hardware

| Stage | What | Needs |
|---|---|---|
| before layout (experiment) | Q-B-ESC-2 on the corrected netlist; decision 43's whole-board eight-layer route; the A4 / A2 / A7 paper study; per-link channel budgets (FB-FAB-7) | the round 8 merge; box time inside the existing allocation |
| PLACED_BOARD | SCH-002, DEC-001, GND-002, IMP-002, THM-001, PLC-001 (13 of 75 on B21), MEC-001 | a placement that seats every part (`region_room` read) |
| ROUTED_BOARD | PI-001 to PI-003 (section 2, PANEL_5V's 0.8 mm), RET-001 to RET-004, IMP-001 and PAIR-001 (section 3), RF-001 (the module radios' feeds), ISO-001, GND-001, STK-001, EMC-001, RTE, VIA, PLN | a complete route |
| FABRICATION_RELEASE | FEA-003 (routed-length extraction against each budget; the fabricator's impedance record for the chosen stack; R-HSD, the qualified high-speed review, not approved); FEA-001 (U8 on its land, Z-EXP-B maxima); FEA-002 (RF-002 on the current netlist); FEA-006 | the routed candidate; the owner's approval for R-HSD |
| PROTOTYPE | INT-003 (each module link up at 1000M full duplex with auto-negotiation, line rate, no error); IOHA A1 to A14; FB-FAB-8 (the reference clock at each socket, six downstream links at Gen 2); `TEST-PLAN.md` E3; `PCB-BRING-UP.md` board B | a built board |

## 11. Open items this sheet cannot close

- The stackup and layer use (decision 43's run; the price to the owner).
- FB-FAB-1 to FB-FAB-8 (`FAILOVER-FABRIC.md` section 10), the corrected netlist on `main` first.
- PWR-F01, F03, F04, F05 declarations (board B's owner).
- The coupling capacitors' rating and the magnetics-footprint fallback (INT-002 follow-ups).
