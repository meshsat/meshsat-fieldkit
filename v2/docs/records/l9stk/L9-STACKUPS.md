# L9-STACKUPS: one stackup decision per board (Layer 9 item 9.12)

MESHSAT-1357, 3 October 2026, the Layer 9 author of item 9.12, worktree `l9stk` on branch `fnd/l9stk` from set 28's tip
`37bc2f1d`. **Prototype design: no V2 board has been fabricated, ordered, assembled or powered, no price has been quoted,
and nothing here was routed.** Every number on this page is either a measurement already in the tree (named with its
record), a bound derived by a stated method in `l9stk_stackups.py` (its output `l9stk_stackups.out`, cited by section),
or a dated public price reading (`inputs/price-readings-2026-10-03.json`). The decisions are written as
`apply_decisions_l9stk.py`, which the integrator runs once; nothing on this page edits `pcb_decisions.yaml`,
`stackup_write.STACKS`, a generator or a board file. **Section 14 (revised 4 October 2026 after the check COPPER: NOT CONFIRMED)
answers the copper question on boards A and E** as a candidate copper-sizing result, not completed fault-protection
verification: the pack path sized at the blades' 25 A with a band's faces and its adjacent return rated as one conductor, the
coordination table and the open owner decision (L9STK CU) on the outer copper weight, from `l9stk_copper.py` and its output; it
supersedes the copper widths of sections 3 and 7.

**What this page is for.** The supplier does the layout (`v2/docs/handover/supplier/SUPPLIER-HANDOVER.md` section 8,
phase 3), so each decision below is the stackup design input that supplier receives: layer count, layer roles, copper
weights, the fabricator stack it maps to, the impedance targets with the trace geometry on that stack, and the
measurement or bound behind the count. `v2/docs/STACKUP-DECISIONS.md` (27 September 2026) stays the summary of the
record before this one; where it says UNDECIDED (board A's copper weight, board B, board P's inner weight) this record
decides, once applied.

## 1. The rule and how each decision is classed

- **The P0 rule** (owner, 11 September 2026, the handover's section 5a): every board's layer count needs its own written
  decision carrying the measurement that forced it and the cost it adds; a stackup is never inherited from a sibling and
  never promoted silently when a route fails; a session decision is marked as the session's.
- **Who decides** (owner rulings of 21 and 26 September 2026): the stackup is a reserved class
  (`v2/ecad/tools/reserved.json`, "layer count and stackup"), so where more than one option still stands after the
  measurement the choice would be the owner's; his standing rule of 26 September has the session take the recommended
  option and record it, never one that spends money, orders or changes what the kit is claimed to be. **An OWNER
  DECISION** in this record is one where more than one option stands AND the choice spends money beyond the existing
  authorisations (section 11).
- **Labels** on every measurement: MEASURED (a route or reading already in the tree, named), DERIVED BOUND (computed here
  by a stated method), NO MEASUREMENT HELD (said so where the tree has none), INFERRED (reasoned, the reasoning given).

## 2. The seven decisions in one table

| Board | Layers and fabricator row | Roles | Copper outer / inner | What forces the count | Price | Decision and authority |
|---|---|---|---|---|---|---|
| A power and I/O, 240 x 160 | 6, JLC06161H-3313, 1.6 mm | F sig and bands, In1 GND, In2 sig, In3 sig, In4 GND, B sig and bands | 1 oz / 0.5 oz | MEASURED: four layers 345 unrouted, six 0 and 0 | NOT READ at the outline (section 10) | 1 oz with two-face bands; SESSION |
| B compute, 330 x 200 | 8, JLC08161H-2116, 1.5996 mm | S G S G P S G S (In4 the four 5 V domains) | 1 oz / 0.5 oz | MEASURED: 93 opens without two inner signal layers; 416 open on six; six cannot hold one width per class; NO MEASUREMENT HELD of a route at eight | NOT READ; owner's before any order (decision 43) | eight as the design input, conditional on decision 43's route; SESSION |
| C panel backer, 344 x 228 | 6, JLC06161H-3313 | F sig, In1 GND, In2 sig, In3 sig, In4 GND, B sig | 1 oz / 0.5 oz | MEASURED: RET-001/002 fail with In2 routing beside B.Cu; 14 to 35 open on two routing layers; six 0 and 0 | NOT READ; owner's before payment (decision 27) | count OWNER (27); copper and no controlled pair SESSION |
| D APRS, 100 x 80 | 4, JLC04161H-7628, 1.6 mm | F sig and RF, In1 GND, In2 plane, B sig | 1 oz / 0.5 oz | MEASURED: four with In2 a plane routes 0 and 0; DERIVED BOUND: two layers cannot give a plane beside both routing faces; NO MEASUREMENT HELD of a two-layer route | NOT READ | four; SESSION |
| E dock strip, 267 x 68 | 4, JLC04161H-7628 | F sig and bands, In1 GND (no tracks), In2 power pours and GND fill, B sig and bands | 1 oz / 0.5 oz | MEASURED: end-to-end opens on a two-routing-layer strip, the tracker maker's plane; DERIVED BOUND: the bands fit only on both faces | NOT READ | 1 oz with two-face bands; SESSION |
| P pack BMS, 70 x 44 | 4, JLC04162H-7628, 1.6562 mm | F sig and pack bands, In1 GND, In2 GND, B sig and pack bands | 2 oz / 0.5 oz | MEASURED: two layers 43 to 47 open, four 0 and 0; DERIVED BOUND: the inner planes' share | NOT READ | count and 2 oz OWNER (28, ruling 7); 0.5 oz inner with planes kept 16 mm wide SESSION |
| E5 dock block, 43 x 26 | 2, 2L-2oz, Dk 4.5 | contact targets and wire lands on both faces | 2 oz / none | DERIVED BOUND: a plated board needs two layers; NO MEASUREMENT HELD (no routing to measure) | NOT READ | count and 2 oz OWNER (ruling 7); Dk and widths SESSION |

Outlines are the Edge.Cuts bounding boxes of the committed board files (`l9stk_stackups.out` section 1); the copper
layers in those files are the boards as built (A 6, B 6, C 4, D 4, E 4, P 2, E5 2), not the decisions.

## 3. Board A

**The measurement (MEASURED).** The four-layer arm of 12 September 2026, the same tools, router and settings as the
six-layer A24, ended 0 hard and **345 unrouted** with its autoroute completed in 51 minutes; six layers closed 0 and 0
(`v2/docs/LAYER-DECISIONS-2026-09-11.md`, "THE ROUTE IS RUN AND THE ANSWER IS NO"). Six is the smallest count a
measurement does not refuse. The arm ran on A24's circuit; the changes recorded since (`layout-constraints/A.md`: the
hot stop line HOT-R1, the EMCON gates behind their own eFuse U39, VIN_RAW onto four dock power pins) add nets and remove
no stage, so they cannot make four layers easier (INFERRED).

**The copper weight (DERIVED BOUND, NO MEASUREMENT HELD of the share).** At PWR-F12's 18 A for 60 s the pack path
(CELL+, CELL_FUSED, VBAT) needs **23.91 mm on one 1 oz face, 6.72 mm on each of two 1 oz faces, 11.95 mm on one 2 oz
face, 3.36 mm on each of two 2 oz faces**, and 195.80 mm on a 0.5 oz inner layer, which is not a conductor; VIN_RAW at
14.1 A needs 15.29 / 4.43 mm at 1 oz and 7.64 / 2.22 mm at 2 oz; every transition of the pack path takes 21 barrels of
0.4 mm whatever the weight (`l9stk_stackups.out` section 2). The pack path's return (GND) is declared on neither board A's
nor board E's intent; on board A's In1 and In4 alone it would need 55.05 mm of each plane at 0.5 oz, inside the board's
160 mm. Neither the per-face share on a routed board nor the 60 s transient PWR-F12 names is held. **Superseded as the band
width by section 14:** 18 A is the transient demand, not the coordination current; the energy chain asks the copper for the
25 A blades' rating, and with a band's faces and its adjacent return rated as one conductor 6.72 mm a face reads 69.59 K at 25 A.

**What 2 oz would cost besides money (DERIVED, section 3 of the output).** The fabricator's 2 oz track and space floor
reads 0.15 mm on its capability page (transcribed 25 September 2026) and **0.16 mm** on its copper weight guide (last
updated 9 September 2026, read 3 October 2026); the stricter governs. Board A's class table is 0.127 mm, its USB class
0.127 / 0.13 mm. U3, the BQ25731 charger's 0.4 mm pitch QFN-32, leaves a 0.200 mm copper gap between pads, exactly
the 0.20 mm 2 oz solder-mask bridge, so its bridges would survive only with no mask expansion at all. And no six-layer 2 oz row is
transcribed or solved: at 0.16 / 0.16 mm the 1 oz solve reads 86.9 ohm for the USB pair, the 2 oz copper unsolved.

**The stackup.** JLC06161H-3313, 1.6 mm: F.Cu 0.035, 3313 prepreg 0.0994 (Dk 4.1), In1 0.0152 GND, core 0.55 (Dk 4.6),
In2 0.0152, 2116 prepreg 0.1088 (Dk 4.16), In3 0.0152, core 0.55, In4 0.0152 GND, 3313 0.0994, B.Cu 0.035. Roles as in
the table; In3 carries the VIN_RAW dive under the VBAT trunk as a crossing only. **Impedance** (atlc solves,
`stack_solves.out` 6L-out and se-6L): the USB2_CM5 ribbon pairs (USB_D8, USB_E6, USB_WALL) 90 ohm on F.Cu and B.Cu only,
**0.130 mm at a 0.127 mm gap (90.0 ohm)**, the class 0.127 / 0.13 reading 91.1; the eleven RF drops 50 ohm single-ended
on F.Cu at **0.155 mm**. No controlled pair on In2 or In3.

**The decision (SESSION, under the 26 September rule).** 1 oz outer, 0.5 oz inner, the pack path and its return as
generator-laid bands on both outer faces at the blades' 25 A, a band's faces and its adjacent return rated as one conductor
(section 14.4: 38.79 to 39.14 mm a face at 1 oz, a 78.29 mm corridor for a band and its return; 19.39 to 19.57 mm at 2 oz).
**The outer copper weight is the owner's open decision (L9STK CU, section 14.7)**: 1 oz is the design input until he rules,
but its corridor is not shown on the floor plan; 2 oz spends a surcharge and moves the class table, U3's bridges and the USB
geometry. **Reversal:** dc_drop on the routed board reads a face over its width's rating, or the transient
analysis or the supplier's floor plan refuses the two-face bands; then JLCPCB's six-layer 2 oz row is transcribed and
solved under its own decision and its price goes to the owner (section 11).

## 4. Board B

**The measurements (MEASURED).** A board-wide In1 keep-out left **93 opens at eight passes** (5 September 2026): the
three receptacles' 0.4 mm escape needs two inner signal layers. B21 on six layers left **416 open after forty hours**
(decision 43's evidence). The region trial Q-B-ESC-1 (26 September 2026, EXPERIMENTAL, INCONCLUSIVE by its own table,
`v2/docs/B-FEASIBILITY.md` 7.8) read **33 open** with four routing layers when its cap cut it and **18 open** with six
routing layers on eight, 38 against 18 at matched routing time; its residue sits at the switch's and hub's unescaped
pad rows, a band two more layers did not clear and which that page reads as bounded by placement. Every one of these
ran on the pre-correction B21; the corrected netlist AC couples and source terminates the switch's clock outputs and
seats 18 parts beside U301 in a pocket that had 0.0 mm of room (`layout-constraints/B.md` section 3), so the demand has
grown since (INFERRED). **NO MEASUREMENT HELD** of a
whole-board route at eight.

**The controlled pairs (MEASURED, atlc, `l9stk_stackups.out` section 4).** On six layers as built the outer layers need
0.130 mm for 90 ohm at a 0.127 mm gap, In2 needs 0.208 mm for 90 ohm and never reaches 85 in the solved widths, and
reads 140.5 ohm where In4 splits between the 5 V domains (`boards/b.json` `_pair_inner_layer_why`): one class width cannot
serve the outer and inner layers. On eight layers, **one width per class on all four routing layers: 0.148 / 0.127 mm
reads 89.9 ohm outer and 90.1 inner; 0.112 / 0.127 mm reads 98.8 outer and 100.1 inner**. The 90 ohm class also meets the
M.2 module's 85 ohm within its 10 percent.

**The stackup.** JLC08161H-2116, 1.5996 mm, layer use S G S G P S G S: F.Cu 0.035 signals; 2116 0.1164 (Dk 4.16); In1
GND; core 0.3 (Dk 4.41); In2 signals; 2 x 1080 0.1528 (Dk 3.91); In3 GND; core 0.3; **In4 the four 5 V domains**
(+5V_DEV, +5V_S1, +5V_S2, +5V_S3; at 0.5 oz each region needs 11.36, 6.36, 13.64 and 6.36 mm along its current path,
section 2 of the output); 2 x 1080 0.1528; In5 signals; core 0.3; In6 GND; 2116 0.1164; B.Cu 0.035 signals. Impedance:
class USB 0.148 / 0.127 mm (PCIE_CM5, USB3_CM5, USB2_CM5, PCIE_M2_MODULE), class DIFF100 0.112 / 0.127 mm (ETHERNET_CM5,
HDMI_CM5), 50 ohm single-ended 0.181 mm on the outer layers. A pair on In5 references In4 at 0.1528 mm, so it stays inside
one 5 V region or carries a stitching capacitor where it crosses between two (RET-003). Through vias only; via-in-pad
filled and capped is the fabricator's default at six layers and above.

**The decision (SESSION).** Eight layers as the design input. After the measurements one option is not refused for the
controlled pairs: six as built (one width cannot serve both layer kinds, and In4's splits remove the inner reference),
option A2 (In3 to ground: three controlled routing layers where four left 416 open), and S G S G S G G S (the 5 V domains
as bands on routing layers, which the floor plan has no room for, `B-FEASIBILITY.md` 3.3) are each refused by a
measurement or the floor plan. **Conditional:** the whole-board route at eight is decision 43's measurement, now the
supplier's layout phase (with Q-B-ESC-2's escape and placement remedy, `B-FEASIBILITY.md` 7.9); if it does not close,
decision 43 returns to the owner by its own text. Taking eight as the design input spends nothing now: decision 43 keeps
the eight-layer price for the owner before any order. **Reversal:** the supplier closes B on six with every controlled
pair in tolerance.

## 5. Board C

**The measurement (MEASURED, owner decision 27).** C24's eighteen B.Cu nets fail RET-001 and RET-002 with only In2, a
routing layer, beside them (the longest 172.9 mm of SCL); two routing layers left 14 to 35 open in the driver cluster
(6 September 2026), the same two routing layers four layers with two planes would leave (INFERRED); the six-layer arm
routed 0 and 0 in 14.7 minutes (16 September 2026). **The copper (DERIVED BOUND):** board C's largest rail is +5V at
0.60 A, 0.15 mm of 1 oz; no interface on C asks an impedance (`pcb_interfaces.yaml`: USB_FULL_SPEED only).

**The stackup.** JLC06161H-3313 as board A's row; F sig, In1 GND, In2 sig, In3 sig, In4 GND, B sig (decision 27, option 1
as written); 1 oz outer, 0.5 oz inner; no controlled pair (USB_PNL runs coupled over a plane for its return); In2 and In3
are 0.1088 mm apart, so long runs on both cross at right angles. At 784.32 cm2 one board exceeds the fabricator's 650 cm2
large board threshold, whose fee the public page does not print.

**The decision.** The count and the layer use are the OWNER's (decision 27, 25 September 2026). The copper weights and
"no controlled pair" are the SESSION's, one option standing.

## 6. Board D

**The measurement.** MEASURED: the In2-as-plane arm routed 0 hard and 0 unrouted over three rounds (15 September 2026,
decision 27's D measurement), so two routing layers carry D. **NO MEASUREMENT HELD** of a two-layer route. **DERIVED
BOUND by the required planes:** RET-001 and RET-002 ask a reference plane beside every routing layer and D routes on both
faces (4,332 mm on its outer layers), which a two-layer board cannot give; the RF line needs its ground 0.2104 mm under
F.Cu. Board D's largest rail is +5V_D8 at 1.0 A (0.30 mm of 1 oz); the 30 W PA module bolts to the plate and is fed off
the board.

**The stackup.** JLC04161H-7628, 1.6 mm: F.Cu 0.035, 7628 prepreg 0.2104 (Dk 4.4), In1 0.0152 GND, core 1.065 (Dk 4.6),
In2 0.0152 a plane (GND and the +5V_D8 pour), 7628 0.2104, B.Cu 0.035. **Impedance:** the RF path RF_PAOUT to J_ANT
50 ohm single-ended on F.Cu over In1 at **0.332 mm** (atlc se-4L; the RF class 0.35 mm reads 48.5); USB at full speed has
no target.

**The decision (SESSION).** Four layers, one option standing; it is the row D's board file already carries.

## 7. Board E

**The measurement.** MEASURED (`LAYER-DECISIONS-2026-09-11.md`): the routing half, a 267 mm strip whose open nets were
end-to-end (USB_E6_P 196 mm, GEIGER_IN 214 mm) on two routing layers; the LT8705A maker's checklist asks a ground plane
layer with no traces next to the FET layer, which In1 is; the power half of the old argument is refuted (In2's 5,500 mm2
of pour worth 13 and 28 mV on E7). **DERIVED BOUND** (`l9stk_stackups.out` section 2): the pack path at 18 A needs 23.91 mm
on one 1 oz face or 6.72 mm on each of two. With VIN_RAW (14.1 A), TRK_OUT (10.33 A), the inlet chain (6.15 A), the solar
input (5.68 A) and the pack return side by side, the bands take **78.72 mm on one 1 oz face, more than the 68 mm strip,
and 23.44 mm on each of two faces (34 percent)**; at 2 oz, 39.36 and 11.72 mm. That sum assumes every conductor crosses
one section of the strip, which the floor plan may avoid, so it bounds and does not measure. The pack return on In1
alone would need 195.80 mm at 0.5 oz and 85.03 mm at 1 oz, so at either inner weight it rides outer bands. **NO
MEASUREMENT HELD** of the per-face share; on E7 B.Cu carried 97 percent of CELL_F once In2 was emptied, so an equal share is
a layout duty.

**The stackup.** JLC04161H-7628 as board D's row; F.Cu signals and bands; In1 solid GND with no tracks; In2 the power pours
(CELL_F, PV_P, TRK_OUT, VIN_RAW) and a GND fill, cut back from under the tracker's switch nodes; B.Cu signals and bands.
On each outer face, by section 14.4 (which supersedes the 18 A figures above; a band's faces and its adjacent return as one
conductor): the pack path 38.79 to 39.14 mm at 1 oz or 19.39 to 19.57 mm at 2 oz, its band and return together 78.29 mm at 1 oz,
more than the strip, or 39.14 mm at 2 oz; the shore input including DC_HS 25.78 to 26.02 mm at L4-E11's 20 A (12.89 to 13.01 mm
at 2 oz); VIN_RAW 13.72 mm (6.86 mm). The outer copper weight is the owner's open decision (L9STK CU). No impedance target; no RF
line.

**The decision (SESSION, under the 26 September rule).** 1 oz outer, 0.5 oz inner, the high-current conductors shared by
both faces. Two options stand (1 oz two-face, 2 oz on JLC04162H-7628); the one taken spends nothing and keeps the 0.09 mm
floor the routing half needs and U10's bridges (U10, the RP2040's 0.4 mm QFN-56, leaves a 0.200 mm gap, the 2 oz bridge
exactly). **Reversal:** dc_drop on the routed strip reads a face over its rating at its coordination current or the floor
plan refuses the two-face bands; then 2 oz, its price to the owner. The energy chain's "board E's 2 oz power bands"
(`pcb_energy_chain.yaml` DOCK_ENTRY) contradicts this; section 12, and `apply_energy_chain_l9stk.py` (section 14.9).

## 8. Board P

**The measurement (MEASURED, owner decision 28).** Two layers left 43, 45 and 47 open at the fabricator's 0.16 mm floor;
four layers 0 and 0 (P8, 18 September 2026).

**The inner copper weight (DERIVED BOUND).** The pack return runs from R10 to the cell block's lead on GND, which In1 and
In2 also are, so the inner planes take a share. `plane_share` models the planes and the outer 2 oz bands as parallel
conductors tied at both ends, sharing by cross-section (one copper, so conductance follows area); it neglects crowding at
the via fields. With the outer bands at their two-face minimum of 3.36 mm: **at 0.5 oz a plane is over its rating only
when necked to 2.80 to 15.45 mm beside the run**; at the board's own 42 mm each plane carries 6.58 A against 7.76 A, and
the planes' share needs 15 barrels of 0.4 mm at each end; at 1 oz the band is 1.25 to 6.70 mm. **NO MEASUREMENT HELD**
of the share dc_drop solves on a routed four-layer P.

**The stackup.** JLC04162H-7628, 1.6562 mm: F.Cu 0.070, 7628 0.2104 (Dk 4.4), In1 0.0152 GND, core 1.065 (Dk 4.38), In2
0.0152 GND, 7628 0.2104, B.Cu 0.070. Pack bands 3.36 mm on each face or 11.95 mm on one. Floors at 2 oz: 0.16 mm track
and space (the stricter printed figure), 0.20 mm solder-mask bridge, 0.254 mm annular ring. **U1 (the BQ4050 gauge, RSM0032A, 0.4 mm
pitch) leaves exactly 0.200 mm between pads**, so its bridges hold only with no mask expansion; the supplier confirms that
with the fabricator or accepts a gang opening. No impedance target (SMBus).

**The decision.** Count and 2 oz outer: OWNER (decision 28, ruling 7). **Inner 0.5 oz: SESSION**, on a layout constraint:
In1 and In2 each stay at least 16 mm wide wherever they run beside the pack return between R10 and the cell block lead.
Two inner weights stand; the one taken is the row decision 28 recorded and spends nothing. **Reversal:** dc_drop on the
routed four-layer P with GND declared as the return of PACK_P reads a plane over its rating, or the layout cannot keep
16 mm; then JLC041621-7628 (1 oz inner) under its own decision, its price to the owner.

## 9. Board E5

**The measurement.** NO MEASUREMENT HELD of a route, and none is needed: E5 carries no signal routing (112 mm of copper).
**DERIVED BOUND:** its plated contact targets and the wire lands beneath them need copper on both faces joined through
plated holes, so two layers is the least it can be. At 18 A (the dock block's stage) CELL+ and CELL_N each need 11.95 mm
on one 2 oz face or 3.36 mm on each of two, 21 barrels of 0.4 mm where a face changes.

**The stackup.** 2L-2oz: F.Cu 0.070, FR-4 core 1.44 (Dk 4.5, the fabricator's two-layer figure), B.Cu 0.070. The board
file's Dk 4.6 is STK-001's residue and closes with its next re-cut.

**The decision.** Count and 2 oz: OWNER (ruling 7). Dk and widths: SESSION, one option standing.

## 10. Prices: what was read, what applies, and what is not read

All readings are public pages fetched from the runner on 3 October 2026 between 21:17 and 21:21 CEST, with no login, no
account, no quote form and no request (`inputs/price-readings-2026-10-03.json` holds each URL, the read time, the page's
own date where it prints one, the sha256/16 of the page as fetched, and the sentence carrying each figure verbatim).

| Reading | Page date | What it prints (USD) |
|---|---|---|
| JLC-1 jlcpcb.com/features/prototype-pcb-way | none printed | 4 layers 10 x 10 cm from 7; 6 layers 10 x 10 cm from 35; quantity not printed |
| JLC-2 jlcpcb.com/resources/multilayer-pcb | none printed | 6 layers 50 x 50 mm ENIG, 5 pcs, from 2; 6 layers 100 x 100 mm, 5 pcs, from 35.1 |
| JLC-3 jlcpcb.com/blog (8 to 20 layer) | 2 December 2022 | 4 layers: small batch about 65.67 per m2 plus about 20.52 per design; 8 layers within 10 cm, 5 pcs, about 82.09; small batch about 116.30 per m2 plus about 82.09 per design; no six-layer rate |
| JLC-4 jlcpcb.com/news (4-layer discount) | 6 March 2024 | 4 layers small batch board charge 70.6 per m2 (100 x 100 mm, 100 pcs: board 70.60, total 106.30) |
| JLC-5 jlcpcb.com/help (extra charges) | last updated 9 September 2026 | special price only for a single board within 102 x 102 mm; a large board fee above 650 cm2 a board, per 50 cm2, amount not printed; 3.0 to 3.5 mil on 4 to 8 layers adds 20 percent |
| JLC-6 jlcpcb.com/help (copper weight) | last updated 9 September 2026 | outer 1 or 2 oz, inner 0.5 (default), 1 or 2 oz; 2 oz any layer 0.16 mm track and space; no price |
| JLC-7 jlcpcb.com/blog (custom PCB cost) | none printed | 2 oz incurs raw material and processing surcharges; no amount |
| JLC-8 jlcpcb.com/resources/pcb-layers | none printed | 6 layers 50 x 50 mm ENIG, 5 pcs, from 2 (as JLC-2) |
| NXP-1 nextpcb.com/pcb-prototype | none printed | 2 layers from 5 (up to 100 x 100 mm); 4 layers from 30; 6 layers from 60; 8 to 32 layers Custom; quantities not printed |

Per board, at the project's quantity of five:

| Board | Outline, order area | Candidates priced | Readings that touch it | Delta at the printed conditions | Price at the real outline |
|---|---|---|---|---|---|
| A | 240 x 160, 0.192 m2 | 1 oz against 2 oz outer, six layers | none at this size; no six-layer rate; 2 oz surcharge not printed (JLC-7) | none | **NOT READ** |
| B | 330 x 200, 0.330 m2 | six against eight layers | 660 cm2 exceeds JLC-5's 650 cm2 threshold (fee not printed); JLC-2 6L 100 x 100 from 35.1; JLC-3 8L within 10 cm about 82.09 and about 116.30 per m2 (2022); NXP-1 6L from 60, 8L Custom | none like for like (JLC-2 and JLC-3 differ in date and conditions) | **NOT READ** |
| C | 344 x 228, 0.392 m2 | four against six (ruled six) | 784.32 cm2 exceeds the 650 cm2 threshold; JLC-1 and NXP-1 start prices | +28 (JLC-1, 10 x 10 cm) and +30 (NXP-1, size not printed), start prices only | **NOT READ** |
| D | 100 x 80, 0.040 m2 | two against four | within JLC-5's 102 x 102 class; NXP-1 2L from 5 (up to 100 x 100), 4L from 30; JLC-1 4L 10 x 10 from 7 | +25 (NXP-1), start prices only | **NOT READ** |
| E | 267 x 68, 0.091 m2 | 1 oz against 2 oz, four layers | none at this size; 2 oz surcharge not printed | none | **NOT READ** |
| P | 70 x 44, 0.015 m2 | 0.5 oz against 1 oz inner (2 oz outer ruled) | within the 102 x 102 class; 4L start prices; no inner or outer copper surcharge printed | none | **NOT READ** |
| E5 | 43 x 26, 0.006 m2 | none open (ruled) | within the 102 x 102 class; NXP-1 2L from 5; no 2 oz surcharge printed | none | **NOT READ** |

**NOT READ, and why:** a price at any board's real outline (no public table prints one, and the fabricators' instant quote
forms were not used, by this task's rule: no quote request); any six-layer per-area rate; the 2 oz outer and 1 or 2 oz
inner surcharges; the large board fee's amount; Seeed (not read). **Every price figure the decisions need is left to the
supplier's quotation** (EQ-14 stays open for it); the lines the quotation should carry are in section 12.

## 11. Owner decisions

**One new OWNER DECISION since the copper question's revision: (L9STK CU), the outer copper weight of boards A and E's pack
path and shore input (section 14.7).** What follows was written before it: where two options stand after the measurement (P's inner weight, and before the revision
A's and E's copper weight), the option taken spends nothing beyond the board as declared or ruled, so the session takes it under
the 26 September rule. The owner gates that stand, unchanged:

1. **Board B, decision 43:** before any order, the owner receives the eight-layer price; if eight does not route, the
   decision returns to him. Options and costs: eight layers JLC08161H-2116 (the design input) or six layers
   JLC06161H-3313 (if the supplier closes six), at 330 x 200 mm, five boards, each **NOT READ** (the large board fee
   applies to both; no public six- or eight-layer price at this size).
2. **Board C, decision 27:** the six-layer price at 344 x 228 mm, five boards, before anything is paid; NOT READ.

And three that open only if a reversal fires (each is money, so each would be his): **A to 2 oz** (JLCPCB's six-layer
2 oz row, surcharge NOT READ), **E to 2 oz** (JLC04162H-7628, surcharge NOT READ), **P to 1 oz inner** (JLC041621-7628,
surcharge NOT READ).

## 12. Findings for other authors

| Finding | Owner |
|---|---|
| The pack path's return (GND between the pack lead and the dock block, and on A to its loads) is declared as a return on neither board A's nor board E's intent, so no rule judges its copper; it needs the pack path's bands (6.72 mm a face at 1 oz). Board P declares PACK_N; A and E should declare theirs the same way | board A and board E streams (the intents' generators) |
| `pcb_energy_chain.yaml` DOCK_ENTRY says "board E's 2 oz power bands"; board E is 1 oz by this decision. Drafted: `apply_energy_chain_l9stk.py` (section 14.9, L9C-F1), which replaces record l8r2's draft | the energy chain's writer; the integrator |
| The 2 oz multilayer track and space floor: the tree's transcription and `layout-constraints/P.md` say 0.15 mm, JLCPCB's copper weight guide (updated 9 September 2026) says 0.16 mm; take 0.16 | the fabricator transcription's owner; the constraint sheets' writer |
| U1 on board P (and U3 on A, U10 on E if they ever go to 2 oz) leaves a 0.200 mm copper gap at 0.4 mm pitch, the 2 oz bridge exactly | board P stream; the supplier |
| `STACKUP-DECISIONS.md` rows for A (copper), B and P (inner weight) say UNDECIDED; `layout-constraints/A.md`, `B.md`, `E.md` and `P.md` section 1 follow them; `boards/a.json` and `boards/c.json` `_copper_layers_why` are stale (named there already) | the integrator, after the apply |
| The supplier's quotation should carry, per board at its real outline and five boards: A six layers at 1 oz and at 2 oz outer; B six and eight layers (the large board fee shown); C four and six layers (the fee shown); D two and four layers; E four layers at 1 oz and 2 oz; P four layers 2 oz with 0.5 oz and 1 oz inner; E5 two layers 2 oz | the supplier handover's author (`QUOTATION-REQUEST-DRAFT.md`) |
| STK-003 (a layout-entry check that the stackup is decided) and IMP-003 (pre-layout impedance feasibility), named in `STACKUP-DECISIONS.md` section 7, are not in `pcb_rules.yaml` | the registry writer |

## 13. How to re-run

- `python3 v2/docs/records/l9stk/l9stk_stackups.py` from the repository root (stdlib plus `track_current.py` and
  `via_current.py`, under a second, no KiCad). Its committed output is regenerated only through `_bin/regen_out.py`.
- `python3 v2/docs/records/l9stk/apply_decisions_l9stk.py --check` (PyYAML); the integrator runs it without `--check`,
  then `python3 v2/ecad/tools/decisions_render.py`.
- The atlc solves this page reads are `v2/docs/layout-constraints/calc/stack_solves.out` (27 September 2026, rented box);
  the runner has no atlc and none was run for this record.
- `python3 v2/docs/records/l9stk/l9stk_copper.py` from the repository root (PyYAML, pdftotext and the tool modules, under two
  seconds, no KiCad); its committed output `l9stk_copper.out` is regenerated only through `_bin/regen_out.py`.
- `python3 v2/docs/records/l9stk/apply_energy_chain_l9stk.py --check` (it refuses until the register carries this record's
  board A and board E decisions); the integrator runs it with `--write` after `apply_decisions_l9stk.py`, instead of record
  l8r2's `apply_energy_chain_e1oz.py`.
- `env -C v2/ecad/tools/tests python3 run.py test_l9stk test_public_hygiene`.

## 14. The pack path's copper on its basis (the copper question, revised 4 October 2026)

**Status.** A candidate copper-sizing result, **not completed fault-protection verification** (the owner's framing). The first
version of this section (`f76564eb`) was checked independently and read **COPPER: NOT CONFIRMED**: every figure reproduced, and
three blockers stood. B1, the two outer faces of a band were rated each alone at its share, though they share one footprint and
heat each other, and the adjacent return was not modelled. B2, DC_HS was carried at 3.15 mm while its failing rows went unquoted.
B3, the limit was taken as 125 C, while the XT60 prints 120 C and the tin-plated blade 105 C. This revision answers all three
and the checker's minors. Every figure is printed by `l9stk_copper.py` into `l9stk_copper.out` ("out N" is its section) from
inputs pinned by sha256; `test_l9stk.py` re-solves its arithmetic from the ruled method. DERIVED BOUND unless labelled
otherwise; nothing here was built, routed or measured.

**The question** (the owner's): resolve the copper of the pack path on boards A and E on its actual basis. Keep the continuous
load, the transient demand and the fault current until its protection clears apart. Verify the 18 A against 25 A coordination,
the temperature rise, the copper weight, the bottlenecks and the sharing between faces before adopting any width. Layer 8's
round 3 (`fnd/l8r3` at `854a2bf5`, merged here for its drafts) raised the conflict (findings F3-06 and F3-07).

### 14.1 In short

- **The currents.** The continuous design current is 10 A. The transient is 18 A for at most 60 s, judged as if steady. The
  gauge holds 20 A with no trip. The coordination current is the 25 A blades' rating, which the energy chain's check 3 asks
  every pack conductor for. On the shore input it is L4-E11's 20 A to the clamps (its D-06 selection).
- **The method (B1).** A band's two outer faces are one conductor of their combined section: two 1 oz faces make a 2 oz
  conductor of the band's width. A band and its adjacent return are one conductor of twice the width carrying their combined
  dissipation. Decision 35's model is applied to that conductor, its external factor once.
- **The widths at 10 K** (each face, two 1 oz faces with the return apart / with the return adjacent at 1 oz / at 2 oz, out 6):

  | Current | Return apart, 1 oz | Return adjacent, 1 oz | Return adjacent, 2 oz |
  |---|---|---|---|
  | the continuous 10 A | 4.08 | 7.25 | 3.62 mm |
  | the transient 18 A | 11.95 | 21.26 | 10.63 mm |
  | the gauge's held 20 A | 14.50 | 25.78 | 12.89 mm |
  | the blades' 25 A | 21.81 | 38.79 | 19.39 mm |
  | the blades' 27.5 A, no opening assured | 25.97 | 46.18 | 23.09 mm |

- **The quoted widths do not hold.**
  - 6.72 mm and 11.95 mm were sized at 18 A, each face alone.
  - f76564eb's 12.26 mm, rated as one conductor, reads 18.92 K at 25 A and 12.03 K at 20 A. Its 600 s point reaches 147.1 C from
    the +70 C line (153.33 C from 76.25 C), and with its return adjacent it reads 35.66 K at 25 A.
  - 14.60, 23.44 and 2.76 mm rest on the same single-face basis.
- **The copper decision: 1 oz is not shown to be layable at these widths.** On board E the pack band and its return need
  78.29 mm a face, more than the 68 mm strip. Board A needs a 78.29 mm corridor its floor plan has not shown.
  - The outer weight is the **OWNER DECISION (L9STK CU)**: 2 oz, or 1 oz with a layout change (14.9).
  - At 2 oz the band and its return take 39.14 mm a face.
- **The protection.** Parts, not copper, limit every overload row beyond the 25 A case.
  - Q39/Q40 pass 150 C held at 21.38 A, R17 its 5 W at 31.62 A, the XT60 its 30 A.
  - These rows need **W4DP-F2's** firmware-independent element (14.7).

### 14.2 The currents by class (out 1)

| Class | Current | Duration | Source |
|---|---|---|---|
| continuous | 10.0 A declared; 9.63 A PS-BUSY PLAN at 10.0 V; 14.97 A at HIGH and 19.20 A with both outlets, each held under 10 A by the shedding and outlet controls | held | `pcb_pack_protection.yaml`; record l9pwr section 6 |
| transient | 18.0 A every transmitter (rows to 21.93 A at PLAN at 10.0 V held under 18 A by D-11's floors); the PA's key-on step 6.4 to 9.6 A; the docking pulse 242.9 A peak, I2t 0.9971 A2s | at most 60 s (firmware); 33.8 us time constant once per docking | PWR-F12; POWER-THERMAL.md 7.3; L4-E11 E11-30 |
| fault, the gauge working | OCD1 20 A (held below it with no trip), OCD2 24 A, AOLD 30 A, ASCD 55.6 A | 2 s; 1 s; 20 ms; 244 us, each firmware-configured | the image, PRIMARY-CONFIGURATION.md |
| fault, board P's FETs failed short | the 25 A MINI blades read monotone: up to 135 % (33.75 A) no opening assured; to 50 A at most 600 s; to 87.5 A at most 5 s; to 150 A at most 0.5 s; to 480 A at most 0.1 s; 625 A2s is a nominal melting figure, no clearing I2t printed | as listed | Littelfuse 297; F2 (30 A) opens later at every current both tables state |
| shore input | 6.15 A continuous; F1 10 A: up to 13.5 A no opening assured; to 20 A at most 600 s; to 35 A at most 5 s; to 60 A at most 0.5 s; a stiff source to 900 A at most 0.1 s | as listed | `gen_sch_e.py`; L4-E11 section 6 |
| VIN_RAW | 14.10 A declared; the tracker's minimum valley limit 13.8 A held; with the hot-swap 19.95 A until its fault time | held | `gen_sch_e.py` |

**The inside air:** every final temperature starts from 76.25 C. That is L4-E12's E5 dwell without the hold (E3-O 71.25 C).
The +70 C line is the consolidation's with the hold, so it is not the worst air (the checker's minor).

### 14.3 The method, the limits and the barrels (out 2, out 3)

- **Stacked faces as one conductor.** A band's two outer faces sit over one footprint and cool through its two surfaces.
  Decision 35's model (`track_current.conservative`, the external factor once) is therefore applied to their combined section,
  and the width is `width_for_current(I, oz = twice the face weight)`. A band and its adjacent return run side by side at both
  connector ends: the XT60's pins are 7.2 mm apart, the dock contacts 6 mm, J_DCIN's 3.96 mm. So the pair is one conductor of
  twice the width carrying their combined dissipation. That conductor is rated at the current I sqrt(2 (kf^2 + kr^2)), and each
  band takes half the width.
- **An uneven split** between the faces dissipates k^2 = 2 (s^2 + (1 - s)^2) of an even one: 1.0100 at a 0.55 share.
  - With one barrel at the part, the part's face carries 0.95 of a 5 mm band (k 1.347) and still 0.68 of an 80 mm one, so the
    transfer field stays.
  - Stitching along a band that ends at a one-face part moves current onto that face early. The field therefore sits at the part.
- **No credit for laying the return apart.** The tree holds no separation rule, so the "apart" widths are for comparison only;
  a separation reading is a qualification the layout could bring.
- **The limit of a band** is the lowest printed limit of the parts it joins. The laminate's limit is NOT HELD.

  | Band | Limit as fitted | With the blade's plating pinned | Governing part |
  |---|---|---|---|
  | board A's pack bands | 105 C | 125 C | the blade (the 3568 holder 145 C) |
  | board E's pack bands | 105 C | 120 C | the blade, then the XT60's 120 C |
  | board E's shore bands | 105 C | 105 C | J_DCIN's JST VH as drawn |

  - The fitted element is named "0297025" in `v2/vendor/SOURCES.yaml`. The 297 sheet prints -40 to +125 C for the
    silver-plated terminals and -40 to +105 C for the tin-plated ones.
  - **0297025.WXNV pins silver** (.U, .H and .L are the same part in smaller packs); the tin part is 0297025.WXT. The pin is
    drafted as `apply_blade_plating_l9stk.py` for Layer 6.
- **The barrel annulus, two conventions** (via_current's 18 um average plating):

  | Convention | Annulus | Rating at 10 K | Pack count | Shore count | VIN_RAW count |
  |---|---|---|---|---|---|
  | outward, via_current's pi (d + t) t (the 0.4 mm the finished hole) | 0.02364 mm2 | 0.900 A | 14 | 12 | 8 |
  | inward, pi (d - t) t (the 0.4 mm the drill) | 0.02160 mm2 | 0.843 A | 15 | 12 | 9 |

  Counts are at half the coordination current. The field takes the inward count until the fabricator states which. It also
  holds every interval the copper is asked to, which brings the pack to 16 (through the blade's 600 s point) and the shore to 15
  (through F1's 0.5 s interval). Where it is more, the split count governs: at 39.14 mm, 81 / 41 / 21 / 11 / 6 barrels for a
  5 / 10 / 20 / 40 / 80 mm band with one one-face end. On E7's placement CELL_F runs 5.65 mm to P_CP, so 74 barrels; a
  plated-through land avoids them.

### 14.4 The widths per conductor (out 5)

| Board | Conductor | Ends | Coordination | 1 oz, each face | 2 oz, each face | Field |
|---|---|---|---|---|---|---|
| A | CELL+, the dock contacts to F1 | TH / TH | 25 A | 38.79 mm | 19.39 mm | none |
| A | CELL_FUSED, F1 to R17 | TH / 1F | 25 A | 39.14 mm | 19.57 mm | 16 or the split count, at R17 |
| A | CH_BATQ (drafted), R17 to Q39 and Q40 | 1F / 1F | 25 A | a one-face hop at the parts' lands | the same | none possible |
| A | VBAT trunk | 1F / loads | 25 A | 39.14 mm | 19.57 mm | at the pair |
| A | GND, the pack return | TH / planes | 25 A | 38.79 mm | 19.39 mm | none at the pins; In1 and In4 at least 30 mm beside it |
| E | CELL+, J_BATT to F3 | TH / TH | 25 A | 38.79 mm | 19.39 mm | none |
| E | CELL_F, F3 to P_CP | TH / 1F | 25 A | 39.14 mm | 19.57 mm | 74 on E7, or a plated-through land |
| E | GND, J_BATT to P_CN | TH / 1F | 25 A | 39.14 mm | 19.57 mm | 16 on E7 |
| E | DC_IN | TH / TH | 20 A | 25.78 mm | 12.89 mm | none |
| E | DC_F, GND_V | TH / 1F | 20 A | 26.02 mm | 13.01 mm | 22 at Q1 and D10 on E7 |
| E | DC_P, HS_S | 1F / 1F | 20 A | one-face hops at the lands | the same | none possible |
| E | DC_HS (carried at the shore's family, B2) | 1F / 1F | 20 A | 26.02 mm | 13.01 mm | 15 at each end |
| E | VIN_RAW | 1F / 1F | 14.10 A | 13.72 mm | 6.86 mm | at each end |

**The cross-sections** (out 8):

| Section | 1 oz, each face | 2 oz, each face | Room |
|---|---|---|---|
| board E's pack end, the band and its return | 78.29 mm | 39.14 mm | 68 mm strip |
| board E's shore chain and VIN_RAW in one section | 79.47 mm | 39.74 mm | 68 mm strip |
| board A's pack corridor | 78.29 mm | 39.14 mm | 160 mm short side |

### 14.5 Each class on the decided bands (out 4)

Every row, failing ones included, on D1 (39.14 mm, 1 oz) and D2 (19.57 mm, 2 oz), which read alike. Final temperatures are from
76.25 C. "Steady" is overheating that persists; "before clearance" is the temperature reached before a timed clearance, the
smaller of the steady and the adiabatic rise.

| Event | Reading | As fitted (105 C) | Pinned (120 C) |
|---|---|---|---|
| 10 A held | 1.89 K steady | within 10 K | within 10 K |
| 18 A for 60 s | 5.22 K steady | within 10 K | within 10 K |
| 20 A held under OCD1 | 6.38 K steady | within 10 K | within 10 K |
| 25 A held | 10.00 K steady | within 10 K | within 10 K |
| 33.75 A held (gauge failed) | 94.55 C steady | within | within |
| 50 A for 600 s (gauge failed) | 116.60 C steady, reached before clearance | **OVER** | within |
| 87.5 A for 5 s | 115.94 C before clearance | **OVER** | within |
| 150 A for 0.5 s | 87.42 C before clearance | within | within |
| 480 A for 0.1 s (the 600 % row's bound) | 99.56 C before clearance | within | within |
| the hard short at the 625 A2s nominal melting figure; at the gauge's ASCD; the docking pulse | 76.86, 76.30 and 76.25 C | within | within |

- **The shore family** (26.02 mm 1 oz, 13.01 mm 2 oz, limit 105 C):
  - 20 A held reads 10.00 K.
  - 13.5 A held reaches 80.85 C, 20 A for 600 s 86.25 C, 35 A for 5 s 90.08 C, 60 A for 0.5 s 80.25 C.
  - **OVER only at 900 A for the 0.1 s the 600 % row allows (318.21 C)**, which F1's clearing I2t decides (E11-16). At 93 A2s
    nominal melting it is 76.46 C.
- **DC_HS (B2)** is now in that family. f76564eb's 3.15 mm read 242.3 and 494.8 C (from +70 C) at 35 A for 5 s and 60 A for 0.5 s with Q7
  shorted, and those rows are carried here.
- **VIN_RAW at 13.72 mm** reads 10.00 K at 14.10 A, and 20.16 K at most with both sources' 19.95 A for the hot-swap's fault time.

### 14.6 The coordination table (out 9)

Each row's components are read at their printed ratings from 76.25 C. Copper at 1 oz and 2 oz reads alike. A continuous rating
covers any shorter time; above it, a time under 60 s needs a short-time rating no held sheet prints.

| Case | Current's basis | Protective device | Assured maximum clearing | Limiting component (reading) | Disposition |
|---|---|---|---|---|---|
| 10 A continuous | declared; states held under it by shedding | none needed | not a fault | the XT60 at 0.33 of 30 A; copper 1.89 K; Q39/Q40 93.8 C | (a) copper, barrels, R17, XT60, pins at an even split; (c) the dock contacts' split; (b) the 3568 holder; (c) R17's sheet and derating |
| 18 A for 60 s | PWR-F12, every transmitter | the key-down limit K1 in firmware; no hardware element acts | none assured by hardware | Q39/Q40 at 0.77 (132.95 C; L4-E11's 126.7 C from +70 C) | (a) copper 5.22 K; (c) E11-29's specimen measured with the band carrying its current; (c) the pins; (b) the holder; (c) R17's sheet |
| 25 A, the gauge working | a fault drawing the blades' rating | the gauge's OCD2, 24 A for 1 s (firmware-configured) | 1 s, the image's setting | the barrel field at 0.84 | (a) copper and barrels; Q39/Q40 as L4-E11 15c (CONDITIONAL on E11-29); (c) the pins; (b) the holder |
| 25 A, the gauge failed | the same with board P's FETs welded; the rating is not a clamp (110 % holds 360,000 s) | none | none assured | **Q39/Q40 OVER, 185.6 C held** | (a) copper at 10 K; **(b) W4DP-F2**; (c) the pins; (b) the holder; (c) R17's sheet |
| 20 to 33.75 A sustained | the gauge holds just under 20 A; failed, no blade row opens below 135 % | the gauge when it works; none when failed | none assured | **Q39/Q40 OVER (150 C at 21.38 A from +70 C, 20.53 A from 76.25 C); R17 OVER at 33.75 A (5.70 W of 5 W); the XT60 OVER (33.75 of 30 A)**; copper 94.55 C | **(b) W4DP-F2**; (b) the holder |
| FETs failed short, 33.75 to 50 A | the blade's monotone envelope | the 25 A MINI blades | at most 600 s | **Q39/Q40, R17 (12.5 W), the XT60 (50 A), the pins (12.5 A each) all OVER**; copper 116.60 C | **(b) W4DP-F2**; (a) copper with the plating pinned; (b) the plating pinned (as fitted, 105 C is passed) |
| FETs failed short, 50 to 87.5 A | as above | the blades | at most 5 s | **the barrel field OVER**; R17, XT60 and pins above their continuous ratings with no short-time rating held; copper 115.94 C | **(b) W4DP-F2**; (a) copper pinned; (b) the plating |
| FETs failed short, 87.5 to 150 A | as above | the blades | at most 0.5 s | **the barrel field OVER**; Q39/Q40 about 237.6 C (INFERRED estimate) | **(b) W4DP-F2**; (a) copper |
| FETs failed short, 150 to 480 A | as above | the blades | at most 0.1 s; 625 A2s is nominal melting, not a clearing figure | **Q39/Q40 and the barrel field OVER**; copper 99.56 C at the row's bound | **(b) W4DP-F2**; (a) copper; (c) the blade's total clearing I2t at 480 A and 16.8 V |
| shore, Q7 shorted (or a clamp failed short), to 13.5 A | F1's envelope; the hot-swap's limit lost | F1, 10 A MINI | none assured | **J_DCIN's VH OVER (13.5 of 10 A)**; R19 at 0.61; copper 80.85 C | **(b) J_DCIN to L4-E11's D-06 30 A class connector**; (b) the holder |
| shore, 13.5 to 20 A | as above | F1 | at most 600 s | **J_DCIN OVER (20 of 10 A); R19 OVER (4.0 W of 3 W from 17.32 A)**; copper 86.25 C | **(b) J_DCIN; (b) R19 to a shunt whose rating covers 20 A held**; (b) the holder |
| shore, 20 to 35 A and 35 to 60 A | as above | F1 | at most 5 s; at most 0.5 s | R19 and J_DCIN above their continuous ratings, no short-time rating held; copper 90.08 and 80.25 C; barrels within | (b) J_DCIN and R19 as above; (b) the holder |
| shore, 60 to 900 A | a stiff source | F1 | at most 0.1 s; 93 A2s is nominal melting | **copper 318.21 C and the barrel field OVER at the row's bound** | (b) J_DCIN, R19; **(c) F1's total clearing I2t at 900 A and 58 V DC (E11-16)** |

**The qualification gaps, each with its specimen, acceptance and supplier task:**

- **The dock contacts' split.** The sheet prints 20 mOhm maximum and no minimum, so the split is unbounded.
  - Specimen: the four-pin set of the fitted lot (and E5's targets).
  - Acceptance: the lowest pin resistance at least 0.593 of the highest, so that no pin passes 9 A at 25 A.
  - Supplier task: each pin's contact resistance at mid-stroke.
- **R17's maker sheet and its derating at the band's temperature** (ROHM GMR100HJAAFD5L00): owed, Layer 6.
- **E11-29's specimen**, measured with the band carrying its current, because the band heats the pair's copper (L4-E11).
- **The blade's total clearing I2t at 480 A and 16.8 V.**
  - Specimen: the fitted lot in the 3568 holder on a band coupon.
  - Acceptance: at most 41,953 A2s, the governing 1 oz face to 120 C from 76.25 C.
  - Supplier task: Littelfuse's clearing data or a short-circuit test.
- **F1's total clearing I2t at 900 A and 58 V DC** (E11-16): acceptance at most 12,451 A2s, the governing face to 105 C.

**A coupon never stands in for a known rating violation:** those rows carry (b).

**W4DP-F2 stays open.** Its closure criterion is a firmware-independent element that opens the discharge path at or below the
cells' 24 A at 3P even with board P's FETs welded. It must also open before Q39/Q40 pass 150 C: 21.38 A held from the +70 C air
on E11-29's 33.12 K/W, or 20.53 A from 76.25 C.

### 14.7 The copper decision, and the OWNER DECISION

**SESSION (unchanged in kind):**
- The counts, the layer roles and the impedance geometry of A and E.
- Every band sized at its coordination current at 10 K, with the faces and the adjacent return as one conductor.
- Transfer fields at every one-face part, and no stitching along a band ending at one.
- No inner layer counted.
- The blade's plating pinned to silver (drafted for Layer 6).

**OWNER DECISION (L9STK CU), appended open by `apply_decisions_l9stk.py`.** 1 oz is the design input until the owner rules, but
it is not shown to be layable: board E's strip cannot take its 78.29 mm pair, and board A's 78.29 mm corridor is not shown.

| Option | What it is | Costs |
|---|---|---|
| (1) 2 oz on A and E | the band and its return 39.14 mm a face | surcharge NOT READ; A's six-layer 2 oz row not transcribed, its 0.127 mm class table to the 0.16 mm floor, the USB geometry solved again, U3's bridges at 0.20 mm; E's routing floor 0.09 to 0.16 mm, U10's bridges at 0.20 mm |
| (2) 1 oz with a layout change | on E, the pack current taken off the strip by an in-line MINI holder on the pack lead; on A, the 78 mm corridor shown by the supplier's floor plan | an in-line holder and its harness (NOT READ); the energy chain's DOCK_ENTRY becomes a harness stage; board A's area |
| (3) 2 oz on E, 1 oz on A with the corridor | **the session's recommendation** (2 oz on A too if the corridor cannot be shown) | the costs of (1) on E only, and of (2) on A |

`apply_energy_chain_l9stk.py` writes the widths at both weights and leaves the weight to this decision.

### 14.8 The drafts for the integrator (none applied)

**Order:** `apply_decisions_l9stk.py --write` (it checks by default now), then `decisions_render.py`, then
`apply_energy_chain_l9stk.py --write` (instead of record l8r2's `apply_energy_chain_e1oz.py`), then Layer 6's
`apply_blade_plating_l9stk.py --write`.

- **`apply_decisions_l9stk.py`** appends the seven stackup decisions and the open (L9STK CU).
- **`apply_energy_chain_l9stk.py`** writes ten edits, after which `energy_chain.check` reads its 98 checks unchanged:
  - DOCK_ENTRY's, SHORE_INPUT's and BOARD_A_NODE's conductor texts at the revised widths;
  - the 25 A blade's citation in six stages, from the ATOF sheet and 1000 A2s to the MINI 297 sheet and 625 A2s labelled as
    nominal melting;
  - PACK_CELLS' cold resistance (2.36 mOhm) and note.
- **`apply_blade_plating_l9stk.py`** names 0297025.WXNV in the pack-blade-fuse-holder entry.

### 14.9 Findings for other authors (design corrections routed, nothing of theirs edited)

| Finding | Owner |
|---|---|
| L9C-F1: the energy chain's conductor texts and the 25 A blade's ATOF citation; `apply_energy_chain_l9stk.py` replaces record l8r2's draft | the integrator; the energy chain's writer |
| L9C-F2: BOARD_A_CONVERTERS claims board A's own copper into each converter at 25 A; a branch is sized at its load, and a branch fault under OCD1's 20 A is cleared by nothing | the energy chain's writer; board A's generator owner |
| L9C-F3: W4DP-F2 stays open with the closure criterion of 14.6; Q39/Q40 pass 150 C held at 21.38 A, R17 its 5 W at 31.62 A, the XT60 its 30 A, the dock contacts 9 A a pin above 36 A | W4DP-F2's owner (the battery stream) with L4-E11 |
| L9C-F4: R19 (3 W) passes its rating at 17.32 A inside F1's 600 s interval; a shunt whose rating covers 20 A held | L4-E11 |
| L9C-F5: J_DCIN's JST VH prints 10 A (AWG 16) and 105 C under L4-E11's 20 A; D-06's 30 A class connector | L4-E11, Layer 7 |
| L9C-F6: the Keystone 3568 prints no current rating; a MINI 297/997 holder whose maker prints at least the coordination current | Layer 6/7 |
| L9C-F7: the blade's plating is not pinned (0297025 names neither terminal); pin 0297025.WXNV (drafted) | Layer 6 |
| L9C-F8: R17's maker sheet (GMR100HJAAFD5L00) and its derating at the band's temperature | Layer 6 |
| L9C-F9: E11-29's specimen measured with the band carrying its current | L4-E11 |
| L9C-F10: board E's 25 A F3 and 10 A F1 have no SOURCES.yaml entry | Layer 6 |
| L9C-F11: P_CP and P_CN as plated-through lands (74 transfer barrels on E7's 5.65 mm otherwise) | board E's PCB generator owner |
| L9C-F12: the dock contacts' split is unbounded (20 mOhm maximum, no minimum); the pin measurement of 14.6 | Layer 7 (the dock), the supplier |
| L9C-F13: the blades' total clearing I2t (25 A at 16.8 V, and F1's at 58 V, E11-16) | the battery stream; L4-E11 |
| L9C-F14: TRK_OUT and the solar input have no stage in the energy chain; VIN_RAW's return path on board E is not declared | the energy chain's writer; L4-E7's owner |
| L9C-F15: the supplier's quotation states the laminate's maximum operating temperature and the 2 oz price beside the 1 oz rows | the supplier handover's author |
