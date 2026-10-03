# L9-STACKUPS: one stackup decision per board (Layer 9 item 9.12)

MESHSAT-1357, 3 October 2026, the Layer 9 author of item 9.12, worktree `l9stk` on branch `fnd/l9stk` from set 28's tip
`37bc2f1d`. **Prototype design: no V2 board has been fabricated, ordered, assembled or powered, no price has been quoted,
and nothing here was routed.** Every number on this page is either a measurement already in the tree (named with its
record), a bound derived by a stated method in `l9stk_stackups.py` (its output `l9stk_stackups.out`, cited by section),
or a dated public price reading (`inputs/price-readings-2026-10-03.json`). The decisions are written as
`apply_decisions_l9stk.py`, which the integrator runs once; nothing on this page edits `pcb_decisions.yaml`,
`stackup_write.STACKS`, a generator or a board file. **Section 14 (4 October 2026) answers the copper question on boards A
and E**: the pack path sized at the blades' 25 A with the faces' split derived, from `l9stk_copper.py` and its output; it
supersedes the 18 A widths of sections 3 and 7, and its energy chain texts are `apply_energy_chain_l9stk.py`.

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
25 A blades' rating, and 6.72 mm a face reads 12.39 K at the gauge's held 20 A and 19.52 K at 25 A.

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
generator-laid bands on both outer faces at the blades' 25 A with the faces' split derived (section 14.5): 12.26 mm a face
from the dock pins to F1, 14.60 mm a face for CELL_FUSED and the VBAT trunk with a transfer field at R17 and at the battery
FET pair. Two options stand (1 oz shared by two faces, 2 oz); the one taken spends nothing, keeps the class table, U3's
bridges and the solved USB geometry. **Reversal:** dc_drop on the routed board reads a face over its width's rating, or the transient
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
On each outer face, by section 14.5 (which supersedes the 18 A figures above): CELL+ 12.26 mm; CELL_F and the return 14.60 mm
with a transfer field at P_CP and P_CN; the shore input 8.15 mm (DC_IN) and 9.70 mm (DC_F, GND_V) at L4-E11's 20 A, 3.15 mm
behind R19; VIN_RAW 5.12 mm. No impedance target; no RF line.

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

**No new OWNER DECISION.** In every board where two options stand after the measurement (A's and E's copper weight, P's
inner weight), the option taken spends nothing beyond the board as declared or ruled, so the session takes it under the
26 September rule. The owner gates that stand, unchanged:

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

## 14. The pack path's copper on its basis (the copper question, 4 October 2026)

**The question** (the owner's, through the coordinator): resolve the copper of the pack path on boards A and E on its actual
basis, keeping apart the continuous load, the transient demand and the fault current until its protection clears; verify the
18 A against 25 A coordination, the temperature rise, the copper weight, the bottlenecks and the sharing between faces before
any quoted width is adopted. **The conflict:** this record's sections 3 and 7 sized the pack path at PWR-F12's 18 A (6.72 mm
on each of two 1 oz faces); Layer 8's round 3 (`fnd/l8r3` at `854a2bf5`, merged here for its drafts; `L8R2-KNOWN-DEFECTS.md`
section 3f, findings F3-06 and F3-07) found that the energy chain's 25 A coordination needs 12.26 mm a face and that board E's
DC_HS band as `gen_pcb_e3.py` lays it carries 8.07 / 7.13 A at 1 oz, under F1's 10 A.

Every figure in this section is printed by `l9stk_copper.py` into `l9stk_copper.out` ("out N" is its section) from inputs
pinned by sha256 in out 0; `test_l9stk.py` recomputes the arithmetic from the ruled method and holds this page to the output.
DERIVED BOUND unless labelled otherwise; nothing here was built, routed or measured.

### 14.1 In short

- **The continuous design current is 10 A** (the pack's declared continuous current; the drafted states' largest sustained
  PLAN at the gauge's 10.0 V floor is 9.63 A, PS-BUSY, and above 10 A a sustained state is held by the shedding control).
  **The transient demand is 18 A for at most 60 s** (PWR-F12, every transmitter keyed, ended early above 18 A), judged as if
  steady because no transient thermal credit is held. **The protection coordination current is the 25 A blades' rating**:
  `energy_chain.py` check 3 asks every conductor of the stage for it, at the 10 K every rating in the chain carries, and the
  gauge's OCD1 holds 20 A with no trip at all. On the shore input it is **L4-E11's 20 A to the clamps** (its D-06 selection,
  a Layer 9 layout constraint), and F1's 10 A behind R19. **The width each asks at 10 K** (two 1 oz faces at an even split /
  one face, out 6): the continuous 10 A 2.76 / 8.15 mm; the 18 A transient 6.72 / 23.91 mm; the gauge's held 20 A 8.15 / 28.99
  mm; the blades' 25 A 12.26 / 43.62 mm; their 110 % non-fuse current, 27.5 A, 14.60 / 51.93 mm. The coordination is judged at
  the rating, as the chain's check 3 asks; the non-fuse current, held only with the gauge failed, then reads 12.14 K, a backstop
  state judged against the blade's 125 C.
- **6.72 mm a face and 11.95 mm on one 2 oz face do not hold**: sized at 18 A, they read 12.39 and 12.38 K at the gauge's
  held 20 A and 19.52 and 19.46 K at the blades' 25 A, and with the gauge failed 6.72 mm reaches 159.4 C at the blade's 600 s
  window top, over the blade's printed 125 C (out 4, out 6).
- **12.26 mm a face holds only where both ends of the band are through-hole**: equal faces then share evenly (derived, not
  assumed). Where a one-face part ends the band (R17 and the battery FET pair on A, the 12 AWG lands P_CP and P_CN on E) that
  part's face carries more: **14.60 mm a face with a transfer field at the part**, sized so the part's face carries at most 0.55
  (out 3).
- **The copper decision:** 1 oz outer and 0.5 oz inner are kept on both boards (a SESSION decision, nothing spent); every
  width is in 14.5; no inner layer is counted as a conductor. **No new OWNER DECISION.** What no width settles: with the gauge
  failed (board P's FETs welded), the blade's intervals shorter than 600 s, from 50 A up, take every band in this record over the
  blade's 125 C by the tree's copper-only bounds; that is W4DP-F2's open residual, not a copper choice (14.9).

### 14.2 The currents by class (out 1)

| Class | Current | Duration | Source |
|---|---|---|---|
| continuous | 10.0 A declared; 9.63 A PS-BUSY PLAN at 10.0 V; 14.97 A at HIGH and 19.20 A with both outlets, each held under 10 A by the shedding and outlet controls | held | `pcb_pack_protection.yaml`; record l9pwr section 6 (Layer 8's copy) |
| transient | 18.0 A, every transmitter; the key-down rows reach 21.93 A at PLAN at 10.0 V and D-11's floors hold them under 18 A | at most 60 s | PWR-F12 (POWER-THERMAL.md) |
| transient | the PA's key-on step 6.4 to 9.6 A at the pack | inside the key-down | POWER-THERMAL.md 7.3 |
| transient | the docking pulse 242.9 A peak, I2t 0.9971 A2s | time constant 33.8 us, once per docking | L4-E11 E11-30 |
| fault, the gauge working | OCD1 20 A (held below it); OCD2 24 A; AOLD 30 A; ASCD 55.6 A | 2 s; 1 s; 20 ms; 244 us | the image, PRIMARY-CONFIGURATION.md |
| fault, the gauge failed | the 25 A MINI blades read monotone: up to 135 % (33.75 A) held; to 200 % (50 A) at most 600 s; to 350 % (87.5 A) at most 5 s; to 600 % (150 A) at most 0.5 s; to the prospective 480 A at most 0.1 s; typical I2t 625 A2s | as listed | Littelfuse 297 (the holder takes the MINI); F2 (Eaton SCF9550, 30 A) opens later at every current both tables state |
| shore, continuous | 6.15 A (_VEH_T, the hot-swap's limit at VCL max) | held | `gen_sch_e.py` |
| shore, fault | F1 10 A: up to 13.5 A held; to 20 A at most 600 s; to 35 A at most 5 s; to 60 A at most 0.5 s; a stiff source to 900 A at most 0.1 s, typical melting 93 A2s | as listed | L4-E11 section 6 |
| VIN_RAW | 14.10 A declared; the tracker's minimum valley limit 13.8 A held; with the hot-swap 19.95 A until its fault time | held | `gen_sch_e.py` |

### 14.3 The method and the criteria (out 2)

The rating is decision 35's model, `track_current.conservative` (the most conservative of the three ECSS-Q-ST-70-12C Annex D
fits at each area), outer copper at `EXTERNAL_FACTOR`; a width is `track_current.width_for_current` at its 10 K default; a
rise is the rise at which that model rates the conductor at the current. A timed event's rise is the smaller of its steady
rise and its adiabatic rise (Onderdonk's relation as `records/l7pwr/inputs` holds it, from the consolidation's +70 C mixed-air
line), because a constant current never takes copper past its steady rise and copper with no cooling bounds it from the other
side. **The criteria (SESSION):** the continuous load, the transient, every gauge level and the coordination current within the
ruled 10 K; the backstop's intervals and the hard short at or under 125 C from the air line, the blade's printed operating
maximum and the lowest printed limit of a part these bands join (the laminate's maximum is NOT HELD in this tree); and every
fault's I2t under the copper's own fusing I2t (the copper is not the fuse).

### 14.4 The split between the two faces (out 3)

- **Through-hole at both ends** (the dock pins to F1 on A; the XT60 to F3 on E; J_DCIN to F1): equal faces sit at one
  potential all along, so each carries half, and stitching along the band moves nothing. The widths are minimums: a face
  laid wider than its minimum takes more of the current by width and still reads at most 10.00 K at 25 A (scanned to three
  times the minimum), because the rating grows slower than the width.
- **A one-face part at one end**: the part's face carries (Rb + Rv) / (2 Rb + Rv), where Rb is one face's band and Rv the
  transfer field; at both ends (Rb + 2 Rv) / (2 Rb + 2 Rv). One 0.4 mm barrel at 18 um is worth 34.3 mm of a 14.60 mm band, so
  with one barrel the part's face carries 0.89 of a 5 mm band and still 0.59 of an 80 mm one. **Stitching along such a band
  moves current onto the part's face early** (that face sits lower all along), so the transfer barrels sit in a field at the part
  and nowhere else along the band.
- **The field** for the part's face to carry at most 0.55 (SESSION: a tenth of imbalance, which costs 19 % of width over an even
  split) is at least 14 barrels of 0.4 mm (the thermal count at half the 25 A) or the split count at the band's length, whichever
  is more: one end 30, 15, 8, 4 and 2 at 5, 10, 20, 40 and 80 mm on board A (31, 16, 8, 4, 2 on E). On E7's placement CELL_F runs
  5.65 mm from F3's pad to P_CP's land, so 28 barrels at P_CP; the return runs 40.60 mm to P_CN, so the thermal 14.
- **One-face hops between two one-face parts** (R17 to the pair on A; Q1 to R19 and R19 to Q7 on E) cannot be split: a few
  millimetres of one-face copper at least as wide as the larger land, whose I2R per millimetre (0.0917 W at 25 A on 3.35 mm) is
  under a tenth of the series part's own (R17 3.125 W); the part's thermal design governs there, and dc_drop's mesh on the routed
  board reads it.
- **The inner planes take a share and are not counted.** On board A, In1 and In4 beside 12.26 mm faces are over record l9stk's
  `plane_share` screen only when necked to 19.50 to 28.20 mm beside the return, so they stay at least 30 mm wide there. On board E
  the screen fails a single plane at every width over 13.50 mm, which is the screen's limit and not the plane's: it applies the
  internal fit to a plane's whole width, outside CNES's 8 A data, while a plane tied in parallel heats per square millimetre at
  0.43 of the bands it relieves (the thickness ratio, the current density being the same) and reads 0.092 A a 0.5 mm cell
  against dc_drop's per-cell bar of 0.395 A. The bands are sized to carry the whole current alone.

### 14.5 The conductors (out 5)

| Board | Conductor | Ends | Protection | Continuous / transient | Coordination | 1 oz, each face | Transfer field |
|---|---|---|---|---|---|---|---|
| A | CELL+, J_CP1 to J_CP4 to F1 | TH / TH | E's F3 (upstream), the gauge | 10 A / 18 A 60 s | 25 A | 12.26 mm | none |
| A | CELL_FUSED, F1 to R17 | TH / 1F | A's F1, the gauge | 10 A / 18 A 60 s | 25 A | 14.60 mm | at R17: 14 or the split count |
| A | CH_BATQ (drafted), R17 to Q39 and Q40 | 1F / 1F | A's F1, the gauge | 10 A / 18 A 60 s | 25 A | a one-face hop, at least 3.35 mm | none possible |
| A | VBAT trunk, the pair (R17 as drawn) to the first branch | 1F / loads | A's F1, the gauge | 10 A / 18 A 60 s | 25 A | 14.60 mm | at the pair: 14 or the split count |
| A | GND, J_CN1 to J_CN4 to the returns and planes | TH / planes | the loop's blades, the gauge | 10 A / 18 A 60 s | 25 A | 12.26 mm | none; In1 and In4 at least 30 mm beside it |
| A | VIN_RAW, J_VR1 to J_VR4 to the front end | TH / 1F | the sources' limits | 14.10 A | 14.10 A | 5.12 mm | at the front end: 8 or the split count |
| E | CELL+, J_BATT pin 2 to F3 | TH / TH | P's F1 (upstream), the gauge | 10 A / 18 A 60 s | 25 A | 12.26 mm | none |
| E | CELL_F, F3 to P_CP | TH / 1F | E's F3, the gauge | 10 A / 18 A 60 s | 25 A | 14.60 mm | 28 at P_CP (E7: 5.65 mm), or a plated-through land |
| E | GND, J_BATT pin 1 to P_CN | TH / 1F | the loop's blades, the gauge | 10 A / 18 A 60 s | 25 A | 14.60 mm | 14 at P_CN (E7: 40.60 mm) |
| E | DC_IN, J_DCIN pin 1 to F1 | TH / TH | the source's own; F1 behind it | 6.15 A | 20 A (L4-E11) | 8.15 mm | none |
| E | DC_F, F1 to Q1 and D10 | TH / 1F | E's F1 | 6.15 A | 20 A | 9.70 mm | 12 at Q1 and D10 (E7: 12.72 mm) |
| E | DC_P, Q1 to R19 and D1 | 1F / 1F | E's F1 | 6.15 A | 20 A | a one-face hop, at least 4.41 mm | none possible |
| E | HS_S, R19 to Q7 | 1F / 1F | E's F1 | 6.15 A | 10 A | a one-face hop, at least 3.81 mm | none possible |
| E | DC_HS, Q7 to L2 | 1F / 1F | the hot-swap; F1 with Q7 shorted | 6.15 A | 10 A | 3.15 mm, or 8.15 mm on one face | 6 at each end (E7: 55.38 mm) |
| E | GND_V, J_DCIN pin 2 to the clamps and L2 | TH / 1F | E's F1 (the clamp-fault loop) | 6.15 A | 20 A | 9.70 mm | at the clamps: 12 or the split count |
| E | VIN_RAW, L2 and Q2 to P_VR | 1F / 1F | the sources' limits | 14.10 A | 14.10 A | 5.12 mm | 8 or the split count at each end |

TH: through-hole (both faces); 1F: one face. Where E7's placement gives no length, the supplier's floor plan does, and the
field is read off out 3 at that length.

### 14.6 Each class on the decided bands (out 4; rise on the governing face, final temperature from +70 C)

| Event | 12.26 mm even (B1) | 14.60 mm at 0.55 (B2) | 6.72 mm even (A1, for comparison) |
|---|---|---|---|
| 10 A held | 1.59 K | 1.61 K | 3.02 K |
| 18 A for 60 s | 5.13 K | 5.13 K | 10.00 K |
| 20 A held (OCD1) | 6.35 K | 6.36 K | **12.39 K** |
| 24 A for 1 s (OCD2) | 4.67 K | 3.98 K | **15.83 K** |
| 25 A held (the blades' rating) | 10.00 K | 10.00 K | **19.52 K** |
| 33.75 A held (135 %, gauge failed) | 88.4 C | 88.4 C | 106.6 C |
| 50 A for 600 s (200 %, gauge failed) | 110.9 C | 110.9 C | **159.4 C** |
| 87.5 A for 5 s; 150 A for 0.5 s; 480 A for 0.1 s | **197.5, 175.5, 325.5 C** | **197.3, 158.0, 277.7 C** | over |
| hard short at the blade's typical I2t; at the gauge's ASCD | 75.1 C; 70.5 C | 74.3 C; 70.4 C | 87.2 C; 71.5 C |
| docking pulse | 70.0 C | 70.0 C | 70.0 C |

The 2 oz option at 7.30 mm a face (B3) reads as B2 at every row. The shore bands (S1 8.15 mm even, S2 9.70 mm at 0.55) hold
20 A at 10 K and every interval to 60 A for 0.5 s within 125 C (at most 104.6 C); only the stiff source's 900 A for the 0.1 s the
600 % row allows is unbounded, which F1's clearing I2t decides (E11-16; at its typical 93 A2s the bands reach 71.7 and 71.4 C).
DC_HS at 3.15 mm (S3) reads 10.00 K at F1's 10 A and, with Q7 shorted, 89.8 C held at 13.5 A and 118.3 C at 20 A for 600 s.
VIN_RAW at 5.12 mm reads 10.00 K at 14.10 A and 9.57 K at the tracker's 13.8 A; both sources together, 19.95 A, read at most
21.57 K for the hot-swap's fault time. The copper is never the fuse: the loosest hard-short bound (480 A for 0.1 s, 23,040 A2s)
puts 5,760 A2s on the governing face of B1 against its fusing I2t of 13,844 A2s.

### 14.7 The widths quoted, judged (out 6)

| Width | Basis it was sized on | Holds? | Why |
|---|---|---|---|
| 6.72 mm on each of two 1 oz faces (this record, sections 3 and 7) | 18 A at 10 K, an even split assumed | **no** | over 10 K at the gauge's held 20 A (12.39 K) and at the blades' 25 A (19.52 K); 159.4 C at the blade's 600 s window top |
| 11.95 mm on one 2 oz face (this record) | 18 A at 10 K | **no** | 19.46 K at 25 A; one 2 oz face needs 21.81 mm at 25 A |
| 12.26 mm on each of two 1 oz faces (Layer 8, F3-06) | 25 A at 10 K, an even split assumed | **yes, between two through-hole ends only** | the split is derived even there; at a one-face part the part's face needs 14.60 mm with a field |
| 23.44 mm a face (this record's board E bound) | every conductor at 18 A in one section | **superseded** | redone at the coordination currents: 57.02 mm a face of the 68 mm strip if every listed conductor crossed one section (a bound the floor plan avoids), 29.20 mm a face at the pack end alone |
| 2.76 mm a face for SHORE_INPUT (Layer 8's draft) | F1's 10 A, even | **no** for DC_IN to the clamps | L4-E11's D-06 asks 20 A there: 8.15 mm (through-hole ends) and 9.70 mm (with a field); behind R19 F1's 10 A at a 0.55 share: 3.15 mm |

### 14.8 The bottlenecks (out 7)

- **R17** (board A, 5 mOhm, 5 W, C20108830): 1.62 W at 18 A, 2.0 W at 20 A, 3.125 W at 25 A; its 5 W is reached at 31.62 A,
  inside the blade's held band with the gauge failed (5.695 W at 33.75 A held).
- **Q39 and Q40** (drafted, 21.136 mOhm each at L4-E11's 150 C bound): 4.23 W at 20 A, 6.61 W at 25 A, 12.04 W at 33.75 A;
  E11-29's bar covers the gauge's levels, not the blade's band.
- **The dock pins** (four Mill-Max, 9 A each at a 10 C rise): 6.25 A a pin at 25 A, 8.44 A at 33.75 A, 12.50 A at the 600 s
  window top (over 9 A).
- **The XT60** (30 A): over its rating from 30 A, inside the blade's held band (33.75 A).
- **R19** (board E, 10 mOhm, 3 W): its 3 W at 17.32 A, inside F1's 600 s window (13.5 to 20 A).
- **The Keystone 3568 holders** (A's F1, E's F3 and F1, P's F1): no current rating printed (L4-E11 section 6).
- **The lands**: every pack and shore pad through-hole except R17, the pair, P_CP, P_CN, Q1, R19, Q7 and L2 (out 7 lists each
  land); a one-face land takes its transfer field (14.4) or, for P_CP and P_CN, a plated-through land.
- **The transfer barrels**: one barrel of a 14-barrel field takes 0.0013 A2s of the docking pulse (+0.01 K) and 0.7972 A2s at the
  blade's typical melting (+8.58 K), and stays under its own fusing I2t (42.0 A2s) even at the 600 % bound (29.39 A2s).

### 14.9 The copper decision per board (SESSION, under the owner's standing rule of 26 September 2026)

**Board A: 1 oz outer, 0.5 oz inner; the pack path and its return on both outer faces at the blades' 25 A**, widths as 14.5
(12.26 mm a face between through-hole ends, 14.60 mm a face with a field at R17 and at the pair, the R17 to pair hop one face at
least 3.35 mm), In1 and In4 at least 30 mm wide beside the return, VIN_RAW 5.12 mm a face. **Margins:** 10.00 K at the
coordination current against the 10 K criterion (sized at it, no excess), 5.13 K at the 18 A transient, 6.36 K at the gauge's
held 20 A; with the gauge failed 14.1 K under the blade's 125 C at the 600 s window top (110.9 C).

**Board E: 1 oz outer, 0.5 oz inner; the pack path, its return, the shore input and VIN_RAW on both outer faces at their
coordination currents**, widths and fields as 14.5. **Margins:** as board A on the pack path; on the shore input 10.00 K at
L4-E11's 20 A and at most 104.6 C (20.4 K under 125 C) through F1's 0.5 s interval; DC_HS 10.00 K at F1's 10 A.

**Two options stand, and the one taken spends nothing:** 1 oz at 12.26 to 14.60 mm a face, or 2 oz at 6.13 to 7.30 mm a face
(the same margins, out 4's B3). The reasons of sections 3 and 7 for 1 oz stand (the class table, U3's and U10's solder-mask
bridges, the solved USB geometry); the board area the wider bands take is the floor plan's to show. **Reversal:** dc_drop on
the routed board reads a face over its rating at the coordination current, or the supplier's floor plan cannot lay the bands and
their fields; then 2 oz under its own decision and its price to the owner. Both are written into `apply_decisions_l9stk.py`'s
board A and board E entries, and `apply_energy_chain_l9stk.py` carries the widths into the energy chain's DOCK_ENTRY,
SHORE_INPUT and BOARD_A_NODE texts; it replaces record l8r2's `apply_energy_chain_e1oz.py` (run this one instead; if l8r2's
was already run, this one replaces its texts in turn).

### 14.10 What no width settles, and the owner

- **The backstop's intervals shorter than 600 s with the gauge failed** (board P's FETs welded, a fault from 50 A up): every
  band this record weighs, at either copper weight, reads over the blade's 125 C by the tree's copper-only bounds (out 4: 197.5 C
  at 87.5 A for 5 s on B1). A width that would hold them is out of proportion (the steady bound is past the fits at 43.75 A a
  face), so this is not a copper choice: it is **W4DP-F2's open residual** (no element that acts without firmware between the
  cells' 24 A and the blade), whose options are already with the battery reviewer and the owner (a fixed hardware over-current
  protector, or the owner accepting the residual). NO MEASUREMENT HELD: a coupon reading (a band specimen at 87.5 A behind a 25 A
  MINI until it opens) or a transient model crediting the laminate.
- **The laminate's maximum temperature** is NOT HELD; 125 C (the blade's) is the lowest printed limit used.
- **The blades' total clearing I2t** at the prospective fault is not printed (625 A2s and 93 A2s are typical melting figures).
- **No new OWNER DECISION.** The 2 oz option stays the reversal of sections 3, 7 and 11, the owner's only if it fires.

### 14.11 Findings for other authors

| Finding | Owner |
|---|---|
| L9C-F1: the energy chain's conductor texts: DOCK_ENTRY and SHORE_INPUT name 2 oz, BOARD_A_NODE names an In2 plane board A does not have; `apply_energy_chain_l9stk.py` writes the derived widths and replaces record l8r2's `apply_energy_chain_e1oz.py` (whose 12.26 and 2.76 mm assume an even split and leave out L4-E11's 20 A) | the integrator; the energy chain's writer |
| L9C-F2: the chain's BOARD_A_CONVERTERS row claims board A's own copper into each converter at 25 A; a branch is sized at its own load, so the claim holds for the VBAT trunk only, and a branch fault under OCD1's 20 A is cleared by nothing | the energy chain's writer; board A's generator owner |
| L9C-F3: series parts the chain does not list sit in the blade's held band with the gauge failed: R17 reaches its 5 W at 31.62 A, the XT60 its 30 A, the dock pins pass 9 A at the 600 s window top, Q39 and Q40 dissipate 12.04 W at 33.75 A; the Keystone 3568 prints no current rating | the battery stream (W4DP-F2), Layer 6 (the holder and R17), L4-E11 (E11-29) |
| L9C-F4: R19 (3 W) reaches its rating at 17.32 A, inside F1's 600 s window, in the loop of a fault behind it | L4-E11 (D-06's withstand list) |
| L9C-F5: P_CP and P_CN are one-face SMD lands for the 12 AWG wires; a plated-through land would give both faces the current (an even split, 12.26 mm a face) where the drawn land needs a 28 barrel field on E7 | board E's PCB generator owner |
| L9C-F6: the pack return on A and E is GND (record l8r2's packrtn drafts declare it a rail returning CELL+ and CELL_F); the return bands are sized as the forward ones, and the planes are not counted | the integrator (with l8r2's drafts) |
| L9C-F7: TRK_OUT and the solar input have no stage in the energy chain; their coordination currents (the tracker's limit is a minimum threshold, the panel's short-circuit current) are not declared, so this record carries TRK_OUT at its declared 10.33 A in the cross-section bound only | the energy chain's writer; L4-E7's owner |
| L9C-F8: `plane_share`'s screen (this record's own, section 8) cannot discriminate a single wide plane at these currents; it served board P's two planes and is not used to size any band here | this record |
| L9C-F9: the supplier's quotation should state the laminate's maximum operating temperature and the 2 oz price beside the 1 oz rows; the floor plan keeps the pack end and the shore chain of board E in separate sections of the strip | the supplier handover's author |
