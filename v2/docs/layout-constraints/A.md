# Board A (power and I/O): layout constraints

**Bound to the set 6 candidate (27 September 2026, read at `760d7f41`).** This sheet's inputs stand in the block below,
one to a line, each with its sha256/16 and the commit it last changed in, with the model and the stack the widths were
computed on; `v2/ecad/tools/constraints_bound.py` fails when a committed input, the calculation or this sheet's power
table moves without the others (README, "The bound block"). **Re-read on this candidate: section 2 alone.** Its power
table is `calc/rail_widths.py`'s output on the inputs below, and the widths, currents and barrel counts the text under
the table quotes were compared with the table and agree. **Not re-read on this candidate: sections 1 and 3 to 11**,
which are the readings at `e3aedb25` with the H2 line's changes marked where they stand (`ef144760`, the paragraph
below). Set 6 changed board A's netlist in `c4ad8350` (the hot stop line HOT-R1 drawn) and nothing of its intent file
but the `written` stamp: **no row of the power table moved**. A line of the older sections that names a part, a net, a
current or a count is compared with the netlist and the intent file below before it is followed, and where this sheet
and a record disagree the record governs (README). Board A is not at layout entry: no board is
(`v2/docs/CURRENT-EVIDENCE.md`, which holds the reasons current on this candidate; a count of reasons in a paragraph
below is its own binding's).

```bound
sheet      A
board      a
read       2026-09-27 at 760d7f41
current    section 2: the power table, and the figures the text under it quotes from it
older      sections 1 and 3 to 11: read at e3aedb25, with the H2 line's changes marked at ef144760
netlist    v2/ecad/pcb-a-power-a23/out/pcb-a-power.net sha256/16 0a2b59087bcc2678 changed c4ad8350
intent     v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json sha256/16 3422910a15c4d145 changed c4ad8350
board_file v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb sha256/16 58e26c67987b1daa changed b7e0d28f
model      track_current.width_for_current decision 35 rise 10 K plating 18 um
stack      JLC06161H-3313 outer 0.0350 mm inner 0.0152 mm
```

**As re-bound to the H2 line (after H2, 27 September 2026), kept as that binding's record.** Candidate re-read at `ef144760`: phase A32, netlist
`v2/ecad/pcb-a-power-a23/out/pcb-a-power.net` sha256/16 `da05dc02bc1e612f` (last changed at `b7f96784`, set 5), intent
`pcb-a-power-intent.json` `92dd3b1cda9046b8`; the committed board file `58e26c67987b1daa` predates the netlist (SCH-002
FAIL). Section 2's power table is regenerated from `calc/rail_widths.py` on that intent; its moved and new rows are
marked **H2**. Board A is not at layout entry: **7 reasons at H2** (`CURRENT-EVIDENCE.md`): SI-001 INCONCLUSIVE,
RF-002 FAIL (EQ-25), decision 31's protection review, FEA-002, FEA-004, FEA-006, FEA-007. What the H2 line changes in
the rest of this sheet, known and marked where it stands: the PA and HF rails gated on both EMCON lines (round 8,
`c0133147`), the EMCON gates behind their own eFuse U39 and the PoE and USB-C enables on their own EN/UVLO node
(`ffca0771`), VIN_RAW onto four 9 A dock power pins J_VR1 to J_VR4 with J_VN1 to J_VN4 (SC-55, `b7f96784`), TRN-001
PASS on current evidence (section 7). Every other line below is the reading at `e3aedb25`, not re-read against the
H2 netlist; where it and a record disagree, the record governs (README).

As first written: a view over the records at `main` `e3aedb25` (conventions and shared rules: [README.md](README.md)).
Candidate then: phase A32, netlist sha256/16 `7b08510106687b3d`, intent `83ba5e43a6fbcccb`; 16 blocker lines then.
Round 8 (`fnd/r8int1`, on `main` as `53a98a71` since this sheet was first written) changes board A's netlist but
declares the same rails at the same currents (its intent file compared rail by rail for this sheet), so section 2
stands through that merge unless the merge itself says otherwise.

## 1. Stackup and layer use

- **Six layers, JLC06161H-3313, 1.6 mm; outer 0.035 mm (1 oz), inner 0.0152 mm.** Count DECIDED on measurement (the
  four-layer arm left 345 unrouted, `LAYER-DECISIONS-2026-09-11.md`); **copper weight UNDECIDED**
  (`v2/docs/STACKUP-DECISIONS.md` section 3.1). No price.
- Layer use (A32 as committed): F.Cu signals and generator-laid power bands; **In1 GND plane, no tracks**; In2 routing
  plus a VBAT pour and GND pours; In3 routing plus power pours (the VIN_RAW dive under the VBAT trunk, `gen_pcb_a3.py`,
  `LAYER-DECISIONS-2026-09-11.md`); **In4 GND plane, no tracks**; B.Cu power bands and the underside through-hole parts.
- **Single-sided SMD assembly.** Board A's back carries only its 21 through-hole parts (the SMP-MAX receptacles, the
  spring pins and the dock pogo block); decision 42 does not allow a decoupling seat on the other side of board A
  because it would add an assembly side (`pcb_decisions.yaml` n 42, authority_why).
- If 2 oz outer is taken, every 0.127 mm clearance in the class table moves to the 2 oz multilayer floor of 0.15 mm,
  including the USB class (`STACKUP-DECISIONS.md` section 3.1).

## 2. Power: band widths at the declared currents

From `calc/rail_widths.py` (decision 35's model, 10 K; barrels at 18 um plating). "Governing" is the current the rule
judges the conductor at (README, "Current"). Widths are the minimum at the narrowest point that carries a meaningful
share of the rail's current (PI-001's own wording, `pcb_rules.yaml`).

The table is `calc/rail_widths.py`'s output on the inputs this sheet's `bound` block names, row for row and cell for
cell in the intent file's own order, and `v2/ecad/tools/constraints_bound.py` fails when the two differ; the `note`
column is this sheet's and is not compared (README, "The bound block"). A width of 0.00 is a current under 5 mA at two
decimals: the fabricator's floor governs there, not the current.

| rail | V (working) | typ / peak A | governing A | outer mm | two outer faces, each mm | inner mm | barrels at the larger of peak and governing, 0.3 / 0.4 / 0.5 mm drill | note |
|---|---|---|---|---:|---:|---:|---|---|
| CELL+ | 14.4 (16.8) | 10.00 / 18.00 | 18.00, PWR-F12 18 A / 60 s | 23.91 | 6.72 | 195.80 (over 40 mm) | 25 / 21 / 18 | the pack path; the inner width is not a practical conductor, so outer copper only (item 1) |
| CELL_FUSED | 14.4 (16.8) | 10.00 / 18.00 | 18.00, PWR-F12 18 A / 60 s | 23.91 | 6.72 | 195.80 (over 40 mm) | 25 / 21 / 18 | the pack path |
| VBAT | 14.4 (16.8) | 10.00 / 18.00 | 18.00, PWR-F12 18 A / 60 s | 23.91 | 6.72 | 195.80 (over 40 mm) | 25 / 21 / 18 | the pack path |
| VIN_RAW | 12.0 (36.0) | 14.10 / 14.10 | 14.10, typical (PI-001) | 15.29 | 4.43 | 125.22 (over 40 mm) | 20 / 16 / 14 | **H2**: 14.10 A since `b7f96784`; at `e3aedb25` it was 12.31 A, which is 11.92 mm on one outer face and 17 / 14 / 12 barrels. The intent file: "declared at board E's 14.10 A since R8E-N01 (27 September 2026: this board's front end at its ISNS limit drawing from a 9.0 V bus, R4A-N12)", "crossing the dock on the Mill-Max power pins J_VR1 to J_VR4 (EQ-16)". The inner width is not a practical conductor (item 4) |
| VBUS20 | 20.00 | 6.00 / 8.00 | 6.00, typical (PI-001) | 3.55 | 1.37 | 26.20 | 11 / 9 / 8 |  |
| +5V_S1 | 5.10 | 2.50 / 5.00 | 2.50, typical (PI-001) | 1.06 | 0.41 | 6.36 | 7 / 6 / 5 | slot 1's rail runs at 4.65 A in PS-ALLTX PLAN (PWR-F02, item 5) |
| +5V_S2 | 5.10 | 2.50 / 5.00 | 2.50, typical (PI-001) | 1.06 | 0.41 | 6.36 | 7 / 6 / 5 |  |
| +5V_S3 | 5.10 | 2.50 / 5.00 | 2.50, typical (PI-001) | 1.06 | 0.41 | 6.36 | 7 / 6 / 5 |  |
| +5V_DEV | 5.00 | 4.00 / 6.90 | 4.00, typical (PI-001) | 2.03 | 0.78 | 12.47 | 10 / 8 / 7 |  |
| +3V3 | 3.30 | 0.30 / 0.60 | 0.30, typical (PI-001) | 0.06 | 0.02 | 0.34 | 1 / 1 / 1 |  |
| +13V8_PA | 13.80 | 5.00 / 6.00 | 5.00, typical (PI-001) | 2.76 | 1.06 | 18.77 | 9 / 7 / 6 |  |
| +12V_HF | 12.00 | 1.00 / 2.00 | 1.00, typical (PI-001) | 0.30 | 0.12 | 1.80 | 3 / 3 / 2 |  |
| +54V_POE | 54.00 | 0.30 / 0.60 | 0.30, typical (PI-001) | 0.06 | 0.02 | 0.34 | 1 / 1 / 1 |  |
| +5V_D8 | 5.00 | 1.00 / 2.00 | 1.00, typical (PI-001) | 0.30 | 0.12 | 1.80 | 3 / 3 / 2 |  |
| PRECHG | 14.4 (16.8) | 0.00 / 1.68 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 3 / 2 / 2 | **H2**, new in `ffca0771`: "the pre-charge pin's conductor to R1 (10 Ohm) and CELL+: 1.68 A at most". The typical current is nil, so the widths are; the barrels are at the 1.68 A peak |
| FE_OUT | 20.0 (20.0) | 6.00 / 8.00 | 6.00, typical (PI-001) | 3.55 | 1.37 | 26.20 | 11 / 9 / 8 |  |
| CH_ACN | 20.0 (20.0) | 6.00 / 8.00 | 6.00, typical (PI-001) | 3.55 | 1.37 | 26.20 | 11 / 9 / 8 |  |
| S1_OUT | 5.1 (5.1) | 2.50 / 5.00 | 2.50, typical (PI-001) | 1.06 | 0.41 | 6.36 | 7 / 6 / 5 |  |
| S3_OUT | 5.1 (5.1) | 2.50 / 5.00 | 2.50, typical (PI-001) | 1.06 | 0.41 | 6.36 | 7 / 6 / 5 |  |
| S2_OUT | 5.1 (5.1) | 2.50 / 5.00 | 2.50, typical (PI-001) | 1.06 | 0.41 | 6.36 | 7 / 6 / 5 |  |
| SD_OUT | 5.0 (5.0) | 4.00 / 6.90 | 4.00, typical (PI-001) | 2.03 | 0.78 | 12.47 | 10 / 8 / 7 |  |
| PA_OUT | 13.8 (13.8) | 5.00 / 6.00 | 5.00, typical (PI-001) | 2.76 | 1.06 | 18.77 | 9 / 7 / 6 |  |
| HF_OUT | 12.0 (12.0) | 1.00 / 2.00 | 1.00, typical (PI-001) | 0.30 | 0.12 | 1.80 | 3 / 3 / 2 |  |
| POE_OUT | 54.0 (54.0) | 0.30 / 0.60 | 0.30, typical (PI-001) | 0.06 | 0.02 | 0.34 | 1 / 1 / 1 |  |
| PD_VPWR | 15.0 (15.0) | 3.00 / 3.00 | 3.00, typical (PI-001) | 1.37 | 0.53 | 8.18 | 5 / 4 / 3 |  |
| PD_SW | 15.0 (15.0) | 3.00 / 3.00 | 3.00, typical (PI-001) | 1.37 | 0.53 | 8.18 | 5 / 4 / 3 |  |
| PD_VBUS | 15.0 (15.0) | 3.00 / 3.00 | 3.00, typical (PI-001) | 1.37 | 0.53 | 8.18 | 5 / 4 / 3 |  |
| PD_OUT | 15.0 (15.0) | 3.00 / 3.00 | 3.00, typical (PI-001) | 1.37 | 0.53 | 8.18 | 5 / 4 / 3 |  |
| VMON | 14.4 (16.8) | 0.69 / 1.00 | 0.69, typical (PI-001) | 0.18 | 0.07 | 1.08 | 2 / 2 / 1 | **H2**, new in `ffca0771`: "the Xenarc 709GNK monitor's supply behind the eFuse U21 (limit 1.2 A, MON_EN)" |
| VHEAT_IN | 14.4 (16.8) | 0.58 / 0.90 | 0.58, typical (PI-001) | 0.14 | 0.05 | 0.85 | 2 / 2 / 1 |  |
| VHEAT | 12.00 | 0.63 / 0.63 | 0.63, typical (PI-001) | 0.16 | 0.06 | 0.95 | 1 / 1 / 1 |  |
| +3V3_EMCON_EF | 3.30 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1 | **H2**, new in `ffca0771`: "the EMCON gates' supply behind the eFuse U39"; declared at 0.4 mA typical and 2 mA peak, which print as 0.00 |
| +3V3_EMCON | 3.30 | 0.00 / 0.00 | 0.00, typical (PI-001) | 0.00 | 0.00 | 0.00 | 1 / 1 / 1 | **H2**, new in `ffca0771`: "the four SN74AUP1G08 EMCON gates' own supply behind R213"; declared at 0.4 mA typical and 2 mA peak, which print as 0.00 |
| VBUS_WALL | 5.00 | 0.50 / 0.90 | 0.50, typical (PI-001) | 0.12 | 0.04 | 0.69 | 2 / 2 / 1 |  |

What the table asks of the layout, each line with its source:

1. **The pack path (CELL+, CELL_FUSED, VBAT) is generator-laid outer copper, 23.91 mm on one 1 oz face, or two faces
   each at least 6.72 mm with a per-face share dc_drop confirms, stitched at each end by at least 21 barrels of
   0.4 mm drill (or 18 of 0.5 mm) at every layer transition** (PWR-F12 at 18 A; `calc/rail_widths.out`). Inner layers
   carry none of it. Until the 60 s transient analysis PWR-F12 names exists, this steady-state width is the constraint;
   the copper weight is open (`STACKUP-DECISIONS.md` section 3.1).
2. **R17, the 5 mOhm charge shunt, is in the pack's discharge path** since `458b2873` (S-04): 1.62 W at 18 A against
   a 3 W part whose maker's sheet is not held (`POWER-THERMAL.md` PWR-F12; `records/rv-pwr/pwr-chain-redeclaration.yaml`
   `declared_only`). Its lands sit on the pack path's bands with copper on both terminals for its heat; its derating at
   the board's temperature is board A's owner's open item.
3. **The charger's output conductors** (CH_SRP on the A32-era netlist; on the committed netlist the same current
   runs from the charger block through R17 into VBAT) get islands and bands of their own: on A32 a 0.500 mm In3
   conductor carried 6.26 A against 0.40 A for its cross-section (`boards/a.json`
   `_ch_srp_carries_ten_amps_through_a_conductor_rated_under_one`).
4. **VIN_RAW at 14.10 A is the second-widest band on the board** (15.29 mm on one face at 1 oz; **H2**: it was 12.31 A
   and 11.92 mm at `e3aedb25`, and since SC-55, `b7f96784`, it reaches the dock on four 9 A power pins); it dives under the
   VBAT trunk on an inner layer only as a crossing, never as a run (the rule of appendix 32.39, `LAYER-DECISIONS`).
5. **Slot 1's 5 V rail runs at 4.65 A in PS-ALLTX PLAN against the AP64500's 5 A** (PWR-F02, 7 percent margin); its
   band and barrels are sized at the 5.0 A peak for the barrels (7 of 0.3 mm) and 2.5 A typical for the band (1.06 mm)
   as the rules state, and PWR-F02 stays board A's owner's item.
6. **Mezzanine 5 V drop share: board A holds 4 points of the codec's 6 percent** (decision 33; PCM2912A VBUS 4.35 V
   minimum), judged by PI-002 on the routed board.

## 3. Pairs and RF lines

| Class / nets | Target (source) | Geometry on JLC06161H-3313 outer | Intra-pair bar |
|---|---|---|---|
| USB: USB_D8, USB_E6, USB_WALL (the ribbon pairs to boards B and E and the wall port) | 90 ohm plus or minus 10 percent (`pcb_interfaces.yaml` USB2_CM5, CM5 datasheet 2.4) | class 0.127 / 0.13 mm (project file); atlc 90.7 ohm at 0.127 / 0.127 and 0.130 / 0.127 for 90.0 (`calc/stack_solves.out`, 6L-out) | 0.15 mm (decision 36; USB_D8 read 0.23 on A32, 0.08 mm of meander owed on its 139 mm leg) |
| RF: the eleven RF drops J_RF<k> to J_BM<k> | 50 ohm single-ended (intent `pair_classes` RF) | F.Cu, 0.14 mm reads 50.1 ohm by `rf_line.py`'s form and 52.5 by atlc; atlc gives 50.0 at 0.155 mm (`stack_solves.out`, se-6L); both inside 10 percent | n/a |

- **Pairs on the outer layers only.** Board A's `pair_layers` is F.Cu, B.Cu (`boards/a.json`); the inner layers of this
  stack solve high (`STACKUP-DECISIONS.md` section 4, the 6L In2 row).
- **The RF drops are laid by the generator, locked, on F.Cu, straight from the SMA centre pin to the blind-mate
  receptacle's centre pin with a single via into its pad**, clear of every other net, over the unbroken In1 plane;
  A32's router had put all eleven on In2 at 0.35 mm, a 26 ohm stripline (`boards/a.json` `_rf_line_why`; RF-001
  remediation in `pcb_rules_coverage.yaml`).

## 4. Return paths

- Board A's classes are in `boards/a.json` `signal_classes` (USB at 0.5 ns, the switch and boot nodes of every
  converter strict). RET-002 read 3 of 197 nets over the screen on A34 by 10 to 16 mm (`OWNER-DECISIONS-2026-09-11.md`,
  decision 27 table); the return-via fixer closes RET-004's 1.5 mm at the finish.
- Every fast net runs adjacent to In1 or In4 (both solid GND). A fast net routed on In2 or In3 has a GND plane on one
  side only at 0.55 mm through the core; keep USB and RF off In2 and In3 (section 3).

## 5. Decoupling (decision 42)

- **Class R at every converter:** the LM5176 stages (U2, U5, U7, U13, U15, U16, U19), the AP64500 slot bucks (U4, U6)
  and the TPS62933 bucks (U12, U33): the input capacitor on the IC's side across VIN and power ground, no via in the
  loop, rail pad within 3.0 mm; outputs declared against the output loop; never on the other side
  (`DECOUPLING.md` section 6; `pcb_emc.yaml` board a for the part list).
- **Generator items owed before a placement is read** (`DECOUPLING.md` section 8.3): G1 (remove the VISNS
  declarations; a 0.1 uF VIN-pin capacitor to AGND at pin 2 of the S2, SD, POE and PD stages, class D; CIN declared
  against the power loop; VCC class L), G2 (U12's 0.1 uF at VIN, class R; U33's C160 class R), G3 (C190 and C191 class
  R against the BQ25731 input loop).
- The committed intent's 55 bypass entries carry no class field (T1 to T10 not landed).

## 6. Placement

1. **Each LM5176 stage laid out as TI's own checklist asks** (TI SNVSAI1D, section 10.1 and Figure 10-1, VERIFIED in
   `v2/vendor/ti/lm5176-datasheet.pdf`): CIN, QL1, QH1 and RSENSE close together (the buck input loop); COUT, QL2, QH2
   and RSENSE close together (the boost output loop); SW1 and SW2 loops minimal; the gate-drive traces and their returns
   "as directly as possible ... close together, either running side by side or on top of each other on adjacent
   layers"; Kelvin connections to RSENSE for CS and CSG run in parallel to the IC, away from SW1, SW2 and the high-side
   gate drives; the VCC (1 uF) and BIAS (0.1 uF) capacitors close to the IC to PGND; BOOT1 and BOOT2 capacitors close to
   the IC and direct to their SW pins; the VIN 0.1 uF to AGND close to the IC; the ISNS filter capacitor close to the IC
   between ISNS(+) and ISNS(-); no power current through AGND. TI's layout example seats the controller below the
   power stage, between its two FET pairs.
   **Decision 46** accepted 13.5 to 28.9 mm gate drives for the revision cut from A98 (session, 21 September 2026),
   and its own reversal names "the controller seated between its own FET pair, which is TI's own layout section" for
   the next revision. The next board A layout is a new placement of the corrected netlist, so **the session recommends
   the TI checklist above as the constraint for it** (reason: no layout of the corrected netlist exists, so the A98
   measurement does not bind it; reversal: re-rule decision 46 for the new placement with the numbers it measures).
   Seating it needs each stage's region re-ordered, which `part_room.py` found necessary on A98 (U13 and U2 had 0.08 mm
   free to the south; `boards/a.json` `_every_lm5176_stage_drives_its_fets_from_thirteen_to_twenty_nine_millimetres_away`);
   board A's region rectangles are the region owner's to change, and the decision 46 entry is the place its authority
   is written.
2. **Current-sense and feedback nodes** (`pcb_sensitive.yaml` board a): fourteen Kelvin taps (the charger's CH_ACP_F,
   CH_ACN_F, CH_SRP_F, CH_SRN_F across R16 and R17 at 50 to 60 mV full scale; each LM5176 stage's ISNS pair across R11,
   R55, R65, R71 and R81 at 50 mV), each from its shunt's pad centre, the pair routed together; every CSF, CSGF, FB and
   ISNS node at least 0.5 mm from the declared switching nets (`*_SW`, `*_SW1`, `*_SW2`, `B33_SW` and the stages' CS
   nodes). Gate-drive rows are reported beside them (decision 45: 88 close approaches on A98 with the gate drives
   named, 64 on the declaration alone).
3. **Hot parts and exposed pads:** every exposed pad carries thermal vias of its own net (escape.py since
   17 September 2026: 103 vias in 31 coarse tabs on a copy of A32, hard 0 before and after; `boards/a.json`
   `_thermal_pads_why`); the PowerPAK SO-8 drains are carried by the top-side islands and bands; R17 as in section 2.
4. **Exposed ports first on their edge** (section 7).
5. **Case and neighbours:** the 4S3P pack block's west face sits 2.0 mm from board A's edge and the pocket is bounded
   by that edge and Peli's R 15.88 fillet (`CASE-MARGINS.md` finding 12; M4a OPEN until the pack's hold-down, check
   T4); the dock block E5 sits under board A's spring pins and the SMP-MAX blind-mates on board A's underside
   (`v2/docs/layout-constraints/E5.md`); outline and connector positions are frozen for routing only after the
   targeted checks of `CASE-MARGINS.md` finding 28, or with the OPEN rows named.
6. **Test access:** 25 test points on the committed netlist; no in-circuit programmable device on board A. Bring-up
   order and measurement points: `PCB-BRING-UP.md` board A (VIN_RAW applied first at 12 V, 14.10 A limit at H2, 12.31 A at `e3aedb25`; CELL+ and
   CELL_FUSED at 14.4 V, 10 A; then 23 derived rails measured in order). The W5 per-board access list REQ-048 names
   is not in the tree (README).

## 7. Protection placement (decision 31, TRN-001)

| Port (`boards/a.json` external_ports) | Conductor | Part at the entry (committed netlist) | Constraint |
|---|---|---|---|
| J_DOCK: shore and vehicle DC over the dock | VIN_RAW (36 V working) | D2 SMCJ40A (intent clamps; netlist VIN_RAW: J_DOCK 1 to 4, D2, C11, C12, Q2) | clamp at the dock pins, ground return short and on the plane; `boards/a.json` declares pins 1 and 2 only, where the netlist carries VIN_RAW on pins 1 to 4 (the declaration is the board stream's to update; the same clamp serves all four) |
| J_USBW: the wall USB host port | VBUS_WALL, USB_WALL_P, USB_WALL_N | U29 USBLC6-2SC6 (pins 1/6 and 3/4 on the pair, 5 on VBUS; committed netlist) | at the connector, between it and U32 and the ribbon |
| J_USBC_OUT: the USB-C outlet | PD_VBUS | D4 SMBJ18A | at the connector, ahead of the controller |
| J_USBC_OUT pins 2, 3 | PD_CC1, PD_CC2 | U31 TPD2E2U06QDBZRQ1 (LCSC C488151, owner D-17) | at the connector (`pcb_board_holds.yaml` board a, fitted_parts) |

- Internal rails also carry clamps (intent clamps: D1 SMCJ18A on VBAT, D3 SMBJ5.0A on +3V3); they are not exposed ports and decision 31 sets no placement for them. USB_E6 and SHORE_INHIBIT reach J_DOCK too, but they are board A to board E inside the case (`boards/a.json` external_ports J_DOCK note).
- **TRN-001 reads FAIL on board A** on the clamp symbol only (`PCB-RULE-STATUS-A.md` TRN-001 row; the clamps drawn
  one-way through `kisch.tvs()` since 26 September); the decision 31 hold gates fabrication release, and its review
  record `v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md` is owed at layout entry (`CURRENT-EVIDENCE.md` line 77).
  **H2:** TRN-001 reads PASS on current evidence (the consolidated re-take, `8ea7867e`); decision 31's review record is
  still owed and is one of board A's seven layout-entry reasons.

## 8. Spacing (ISO-001)

- **VIN_RAW (36 V working), +54V_POE and POE_OUT (54 V):** at least **0.160 mm** from every other net on the outer
  layers (coated), **0.150 mm** on the inner layers, and **0.500 mm** where the coating is masked (J_DOCK, the test
  points, the spring-pin targets). The committed A32 has 5 pairs under the limit, the closest 0.129 mm, VIN_RAW to
  FE_LDRV1, FE_SW1 and GND (`pcb-a-power-a23/routed/spacing.verdict.json`). The project file's HV class carries
  0.18 mm; these three nets belong in it.
- **VBUS20, FE_OUT, CH_ACN (20 V):** 0.120 mm outer coated, 0.104 mm inner, 0.300 mm where masked; the class
  clearance of 0.127 mm meets the first two.

## 9. Thermal

- THM-001 is a PLACED_BOARD rule and reads INCONCLUSIVE with no verification on every board; `thermal.py` computes no
  junction temperature (`CURRENT-EVIDENCE.md`; audit). What the record gives for board A: R17 at 1.62 W (section 2);
  the eFuses and bucks with exposed pads (section 6.3); PWR-F02's slot 1 margin.
- The inside air is not bounded at desk: PS-TYP's rise is 22.5 to 52.7 K on the independent bound (`POWER-THERMAL.md`
  9.1). The heat-balance test of `POWER-THERMAL.md` section 10 is allocated before the placement of the hot parts is
  frozen (FEA-004's FABRICATION_RELEASE stage) and needs a purchase the owner has not authorised
  (`READY-TO-ACT.md` section 5).

## 10. Analyses that need placed or routed geometry, or hardware

| Stage | What | Needs |
|---|---|---|
| PLACED_BOARD | SCH-002, DEC-001, GND-002, IMP-002, ANA-001, THM-001, PLC-001, MEC-001 | a placement of the merged netlist; T1 to T10 and G1 to G3 for DEC-001; junction estimates for THM-001 |
| ROUTED_BOARD | PI-001 (the pack path at 18 A, the per-face share), PI-002 (A's 4 point mezzanine share), PI-003 (the barrel counts of section 2), RET-001 to RET-004, IMP-001 and PAIR-001 (USB), RF-001 (the eleven drops), ISO-001 (section 8), GND-001, STK-001, EMC-001, RTE, VIA, PLN | a routed candidate |
| FABRICATION_RELEASE | decision 31 hold; FEA-004 (board A's routed pack-path copper judged at 18 A; the empty-case heat-balance test before hot-part placement is frozen); FEA-006 (placement read under the class rules); FEA-002 (RF-002 on the current netlist) | the routed candidate; the owner's purchase for the heat-balance test |
| PROTOTYPE | `PCB-BRING-UP.md` board A; FEA-004's bring-up readings; `TEST-PLAN.md` E3 and M7; the converter loop and ripple measurements the board A records owe (`records/r4a/r4-decisions.md`) | a built board |
| Review | R-PWR, the qualified power review (`reviews/REVIEW-ROUTES.md` line 22): not approved; its staging differs between REVIEW-ROUTES ("before board A enters layout"), ARCHITECTURE.md 14.2 and EXECUTION-PLAN.md, which the integrator reconciles | the owner's spending approval |

## 11. Open items this sheet cannot close

- The pack path's copper weight and the 60 s transient analysis (board A's stream; `STACKUP-DECISIONS.md` 3.1).
- R17's rating at temperature (a maker's sheet; board A's stream).
- Decision 46 re-ruled for the next placement with the region authority named (section 6.1).
- The W5 test access list (REQ-048).
