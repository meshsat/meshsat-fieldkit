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
supersedes the copper widths of sections 3 and 7. **Section 15 (4 October 2026, the owner's correction) designs W4DP-F2's
firmware-independent element** on a current-and-time criterion: an LM5069 breaker on board P (the -1, latch-off) with a make-last dock enable,
drafted, and the battery FETs' junction limit met by a third FET, from `l9stk_protection.py` and its output (revised after the
recheck PROTECTION: NOT CONFIRMED). **Round 3 (4 October 2026, the integration of set 29, a tool correction):** L4-E11's
round 9 drafts that third FET as Q42 and restates E11-29 as section 15.5's limit; a quoted sentence of its draft ("one of two
in parallel") stopped both scripts. They now parse the draft, the coordination table's battery FET rows are judged on the three
as drafted (14.6a lists each row that moved, with the pair's reading beside it), and no width, limit, split, barrel count,
breaker figure or junction-limit figure moved. No finding is closed by it.

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
- `python3 v2/docs/records/l9stk/fetch_held_back.py` once (it fetches TI's SLVA673A into the ignored `v2/vendor/ti/held/` and
  checks its sha256), then `python3 v2/docs/records/l9stk/l9stk_protection.py` from the repository root (PyYAML, pdftotext and
  the copper script); its committed output `l9stk_protection.out` is regenerated only through `_bin/regen_out.py`, after
  `l9stk_copper.out`, whose sha256 it pins.
- `env -C v2/ecad/tools/tests python3 run.py test_l9stk test_energy_chain test_public_hygiene` (the protection tests skip,
  named, where SLVA673A is not held).

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
  - The outer weight is the **OWNER DECISION (L9STK CU)**: 2 oz, or 1 oz with a layout change (14.7).
  - At 2 oz the band and its return take 39.14 mm a face.
- **The protection.** Parts, not copper, limit every overload row beyond the 25 A case.
  - The battery FETs as drafted now (Q39, Q40, Q42) meet their 150 C limit at 23.93 A from 76.25 C with the band and R17 in
    place; the pair the table was first judged on passed 150 C at 21.38 A held. R17 passes its 5 W at 31.62 A, the XT60 its 30 A.
  - These rows need **W4DP-F2's** firmware-independent element: section 15 designs it (an LM5069-1 breaker on board P with a
    make-last dock enable, drafted) and restates the battery FETs' target as a junction limit met by a third FET.

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
| A | CH_BATQ (drafted), R17 to Q39, Q40 and Q42 | 1F / 1F | 25 A | a one-face hop at the parts' lands | the same | none possible |
| A | VBAT trunk | 1F / loads | 25 A | 39.14 mm | 19.57 mm | at the FETs |
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
| 10 A continuous | declared; states held under it by shedding | none needed | not a fault | the XT60 at 0.33 of 30 A; copper 1.89 K; Q39, Q40, Q42 89.42 C | (a) copper, barrels, R17, XT60, pins at an even split; (c) the dock contacts' split; (b) the 3568 holder; (c) R17's sheet and derating |
| 18 A for 60 s | PWR-F12, every transmitter | the key-down limit K1 in firmware; no hardware element acts | none assured by hardware | the XT60 at 0.60 of 30 A; Q39, Q40, Q42 at 0.57 (118.00 C) | (a) copper 5.22 K; (c) E11-29's specimen measured with the band carrying its current and R17 dissipating; (c) the pins; (b) the holder; (c) R17's sheet |
| 25 A, the gauge working | a fault drawing the blades' rating | the gauge's OCD2, 24 A for 1 s (firmware-configured) | 1 s, the image's setting | the barrel field at 0.84 | (a) copper and barrels; (c) Q39, Q40, Q42: no timed target is held (L4-E11 19c withdrew the pair's), E11-29's specimen at the held limit, which governs behind the breaker (drafted); (c) the pins; (b) the holder |
| 25 A, the gauge failed | the same with board P's FETs welded; the rating is not a clamp (110 % holds 360,000 s) | none | none assured | **Q39, Q40, Q42 OVER, 156.72 C held** | (a) copper at 10 K; **(b) W4DP-F2**; (c) the pins; (b) the holder; (c) R17's sheet |
| 20 to 33.75 A sustained | the gauge holds just under 20 A; failed, no blade row opens below 135 % | the gauge when it works; none when failed | none assured | **Q39, Q40, Q42 OVER (150 C at 23.93 A from 76.25 C with the band and R17 in place, 24.93 A from the +70 C line; 222.97 C at 33.75 A); R17 OVER at 33.75 A (5.70 W of 5 W); the XT60 OVER (33.75 of 30 A)**; copper 94.55 C | **(b) W4DP-F2**; (b) the holder |
| FETs failed short, 33.75 to 50 A | the blade's monotone envelope | the 25 A MINI blades | at most 600 s | **Q39, Q40, Q42, R17 (12.5 W), the XT60 (50 A), the pins (12.5 A each) all OVER**; copper 116.60 C | **(b) W4DP-F2**; (a) copper with the plating pinned; (b) the plating pinned (as fitted, 105 C is passed) |
| FETs failed short, 50 to 87.5 A | as above | the blades | at most 5 s | **the barrel field OVER**; R17, XT60 and pins above their continuous ratings with no short-time rating held; copper 115.94 C | **(b) W4DP-F2**; (a) copper pinned; (b) the plating |
| FETs failed short, 87.5 to 150 A | as above | the blades | at most 0.5 s | **the barrel field OVER**; Q39, Q40, Q42 about 147.96 C (INFERRED estimate, 0.97 of the limit) | **(b) W4DP-F2**; (a) copper |
| FETs failed short, 150 to 480 A | as above | the blades | at most 0.1 s; 625 A2s is nominal melting, not a clearing figure | **the barrel field and Q39, Q40, Q42 OVER**; copper 99.56 C at the row's bound | **(b) W4DP-F2**; (a) copper; (c) the blade's total clearing I2t at 480 A and 16.8 V |
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
- **E11-29's specimen**, measured with the band carrying its current and R17 dissipating, because both heat the FETs' copper
  (L4-E11 19c: the three on one pour, R17 apart).
- **The blade's total clearing I2t at 480 A and 16.8 V.**
  - Specimen: the fitted lot in the 3568 holder on a band coupon.
  - Acceptance: at most 41,953 A2s, the governing 1 oz face to 120 C from 76.25 C.
  - Supplier task: Littelfuse's clearing data or a short-circuit test.
- **F1's total clearing I2t at 900 A and 58 V DC** (E11-16): acceptance at most 12,451 A2s, the governing face to 105 C.

**A coupon never stands in for a known rating violation:** those rows carry (b).

**W4DP-F2 stays open.** Its closure is a current-and-time criterion for every series part with board P's FETs welded and no
firmware (section 15.1), not one current: the pair it was found on, Q39/Q40 as L4-E11 drafted it until its round 9, passed
150 C at 21.38 A held from the +70 C air and 20.53 A from 76.25 C (derived on E11-29's 33.12 K/W target of then), under the
cells' 24 A, so a trip allowed at 24 A left them at 161.0 C at 22 A and 168.8 C at 23 A from 76.25 C. Section 15 selects the
element and the strengthening. The three drafted since meet their limit at 23.93 A from 76.25 C, under the blades' least
assured opening, 33.75 A: without the element the rows above stay OVER.

### 14.6a What moved in round 3: the battery FETs' rows (out 9a)

**Cause.** L4-E11's round 9 draft writes Q39, Q40 and Q42 where it wrote Q39 and Q40, and its section 19c restates E11-29: from
the pair's 33.12 K/W (the FETs' own heating, from the +70 C line) to 45.88 K/W a FET with R17 apart, the band and R17 in place,
from 76.25 C. Both columns are computed by `l9stk_copper.py` from the pinned files; the fraction is of the 150 C rise.

| Row | The pair, as first judged | Q39, Q40, Q42 as drafted now | Limiting component |
|---|---|---|---|
| 10 A continuous | 93.75 C [0.24] | 89.42 C [0.18] | unchanged: the XT60 at 0.33 |
| 18 A for 60 s | 132.95 C [0.77] | 118.00 C [0.57] | was the pair at 0.77; now the XT60 at 0.60 |
| 25 A, the gauge working, 1 s | L4-E11 15c's gauge levels at E11-29's bar | no timed target held (L4-E11 19c) | unchanged: the barrel field at 0.84 |
| 25 A, the gauge failed | 185.63 C [1.48] | 156.72 C [1.09] | the battery FETs, OVER before and now |
| 33.75 A sustained | 275.59 C [2.70] | 222.97 C [1.99] | the battery FETs, OVER before and now |
| 50 A, at most 600 s | 513.77 C [5.93] | 398.47 C [4.37] | the battery FETs, OVER before and now |
| 87.5 A, at most 5 s (estimate) | about 132.89 C [0.77] | about 101.42 C [0.34] | unchanged: the barrel field at 3.32 |
| 150 A, at most 0.5 s (estimate) | about 237.60 C [2.19] | about 147.96 C [0.97] | unchanged: the barrel field at 4.13 |
| 480 A, at most 0.1 s (estimate) | about 1728.43 C [22.40] | about 810.55 C [9.96] | was the pair at 22.40; now the barrel field at 11.08 |

**Not moved:** every width, limit, split, transfer field and barrel count of 14.3 to 14.5, and every copper, barrel, R17, XT60,
dock contact, R19 and J_DCIN reading of 14.6. No disposition changes class: the rows that were OVER are OVER, and each still
carries (b) W4DP-F2.

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
| (4) 1 oz with each return laid apart from its band | 22.01 mm each, 44.02 mm plus the gap, inside board E's 68 mm strip for a gap up to 23.98 mm (out 8) | no copper cost; **not credited**: decision 35's model holds no term for the distance between two conductors, so no gap is shown to be apart; it waits on a coupon (a board E strip at 1 oz with the band and its return at the gap carrying 25 A, each at most 10 K) |

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
| L9C-F3: W4DP-F2 stays open with section 15's current-and-time criterion (not one current); the pair Q39/Q40 passed 150 C held at 21.38 A (the three drafted since: 23.93 A from 76.25 C), R17 its 5 W at 31.62 A, the XT60 its 30 A, the dock contacts 9 A a pin above 36 A | W4DP-F2's owner (the battery stream) with L4-E11 |
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
| L9C-F16: W4DP-F2's element drawn into board P: the LM5069-1 breaker of 15.4 (DD-1), its layout (IF-2) and its energy chain stage (IF-3) | board P's generator; W4DP-F2's owner; the integrator |
| L9C-F17: E11-29 restated as a junction limit (DD-2, E-1): the hottest battery FET at most 150 C held at 23.93 A from 76.25 C with the band and R17 in place; a third BUK6Y10-30P (L4-E11's round 9 drafts it as Q42, not applied; Q41 is l8r2's VIN_RAW cut-off FET), (Zself + 2 Zmut) at most 45.88 K/W with R17 designed apart; the PTC thermal guard in the enable loop beside them; E11-37 with three (C3) | L4-E11; board A's generator (the PTC) |
| L9C-F18: board A's loads on VSYS held off during the breaker's start, at most 40.7 ms, or tied to its PGD (IF-1) | L4-E11; board A's generator |
| L9C-F19: the power limit's accuracy at 5.05 mV, the limits at VIN 10.6 to 16.8 V and VIN to SENSE in a hot short: Q-TI-L9S-1 (drafted, not sent) and the supplier's E-2, E-3, E-9, E-10 and E-11 | the battery stream; the supplier handover's author |
| L9C-F20: a live docking took the breaker past its SOA and VIN to SENSE's maximum; C-1b, the make-last enable loop into UVLO with its RC hold (DD-6, conditions C1 and C2) | board P's generator with the battery stream; board E's generator; Layer 7 with L4-E11 |
| L9C-F21: BAT-F20 at the breaker's held current: Q1's body diode 23.9 W at 23.93 A (DD-5) | the battery stream |
| L9C-F22: with C-1b the pack's terminal is live only while the enable is closed; board A's J_PRE1 and R1 are no longer exercised at docking; E11-30's docking waveform no longer arises (IF-5) | the battery stream (CONOPS); board A's generator; L4-E11 |

## 15. The pack path's protection: W4DP-F2's element (the owner's correction, 4 October 2026)

**Status.** A drafted protection design: desk arithmetic, not drawn into any generator, nothing built, bought or measured.
**Revised after the targeted recheck PROTECTION: NOT CONFIRMED** (the breaker's arithmetic reproduced, the copper corrections
B1 to B3 confirmed as conditional, board P's existing protection confirmed unable to meet the criterion). This revision
answers two blockers and the minors:
- **B-P1**: a live docking took the breaker past its own limits. The make-last enable contact C-1b corrects it (15.4).
- **B-P2**: the battery FETs' target counted the FETs' own heating only. It is restated as a junction limit, and a third FET
  is selected (15.5).

**Corrected after the recheck PROTECTION: CONFIRMED AS CONDITIONAL** (no blocker, every figure reproduced). The corrections:
- the docking's timing (the insertion time belongs to the gauge's FET start only; on the enable the gate rises 55 us typical
  after UVLO's threshold, so the grace is the RC hold now selected);
- the third FET's designator is left to L4-E11 (Q41 is l8r2's VIN_RAW cut-off FET);
- BAT-F20 on the 10 A and 18 A rows;
- D1 judged on I2t;
- the PTC thermal guard reconsidered and selected.

**Round 3 (4 October 2026, the integration of set 29).** L4-E11's round 9 answers two of this section's demands in its drafts,
not applied: the third battery FET is Q42 in `apply_gen_sch_a_charger.py`, and E11-29 is restated as 15.5's junction limit
(45.88 K/W a FET with R17 apart; 150 C held at 23.93 A from 76.25 C), the pair's 33.12 K/W target withdrawn. The scripts read
both from L4-E11's files and hold them equal to this section's own selection and allowance by predicates. No figure of the
breaker, its table, the junction limit or the series parts moved. 15.3 below is the pair the element was sized against, kept
as the basis of the criterion. DD-2 stays a design defect until the draft is applied and E-1 is read; C3 (E11-37 with three)
stays open.

The conditions C1 to C3 and the minors are written into 15.4 to 15.7.

**Checked for the owner's reviewer's retry question** (review of the d834e6a7 package, 4 October 2026, "Two precise checks",
item 1). The LM5069-2 retries while a fault remains (its sheet, sections 5 and 8.4.3), so 15.4b judges that repeated waveform
against every protected part.
- **The -2 does not meet the criterion.** Its repeated waveform takes the breaker FET past TI's margin in a hard short, and
  past 150 C in a resistive fault on VSYS.
- **SELECTED: the -1 (latch-off).** It matches the recovery policy the project already holds for an over-current backstop.
- **New items:** one new design defect (DD-7, the latch's reset when an input returns), IF-7, E-14, and a start-margin finding
  (15.4b).

**Revised after the recheck of 15.4b (PROTECTION: NOT CONFIRMED).** The retry arithmetic and the -1 reproduced.
- **B-R2** (charging through a latched breaker) goes to L4-E11's running round as a hardware charge inhibit.
- **B-R1** (a hot restart of the -1 past the margin the -2 was rejected on) is corrected here under one SOA criterion for both
  variants, by C-1c, a restart inhibit on the breaker pad. That is DD-8, owned by board P's generator (record l8p).
- **The minors** are folded into 15.4 and 15.4b.

Every figure is printed by `l9stk_protection.py` into `l9stk_protection.out` ("prot N" is its section) from 23 inputs pinned by
sha256. The calculation basis is TI's application report SLVA673A, "Robust Hot Swap Design" (equations 3 to 7, its 2.4 on
parallel FETs, its 3.1.2.2, 3.1.2.5 and 3.2.2.7 checks), applied to the LM5069's sheet (SNVS452G). SLVA673A carries no grant to
redistribute: it is held back in the ignored `v2/vendor/ti/held/`, and `fetch_held_back.py` fetches it and checks its sha256
(`ea1604c5...`). The CSD18510Q5B's safe operating area is read from its Figure 10 at 300 dpi
(`inputs/csd18510q5b-figure-readings-2026-10-04.json`, plus or minus 10 %).

### 15.1 The criterion (the owner's, replacing "at or below 24 A")

The element is judged on current AND time for every series part, not on one current:
- the service is never interrupted: 10 A held and 18 A for 60 s;
- every series part stays within its limits across the credible overload range, including any current under the trip held
  indefinitely;
- with board P's FETs welded and no firmware;
- with the tolerances, the detection and turn-off delays, the initial temperature (L4-E12's 76.25 C plus each part's own
  heating) and the retry's heating;
- the element itself within its voltage, current, thermal and SOA limits, **in every normal event, docking included**.

### 15.2 Board P's existing protection with its FETs welded (prot 1)

None meets it, as the recheck confirmed:
- The gauge's OCD1/OCD2, the AFE's AOLD/ASCD and the PTC act through the welded Q1/Q2.
- The second level U2 has no current input.
- F2's heater is fired by U2 or the gauge's FUSE output (firmware).
- F2's element assures no opening under 60 A, and the blades none under 33.75 A.

### 15.3 The limiting part's current and its uncertainty (prot 2)

Q39/Q40, board A's battery FET pair as L4-E11 drafted it until its round 9 (the part the element was sized against), FETs
only. **Derived, not a rating.**
- RDS(on) at L4-E11's 150 C bound, 21.136 mOhm each.
- The installed path at E11-29's **target** of then, 33.12 K/W (withdrawn in L4-E11's 19c), not a measurement.
- With both FETs at the bound, the even split gives each the largest loss.

| Installed path | From +70 C | From 76.25 C |
|---|---|---|
| 20 % lower (26.50 K/W) | 23.90 A | 22.95 A |
| as targeted (33.12 K/W) | **21.38 A** | **20.53 A** |
| 20 % higher (39.74 K/W) | 19.52 A | 18.74 A |

The 22 to 23 A exposure stands. A trip allowed at the cells' 24 A leaves these junction temperatures, held:

| Current | From +70 C | From 76.25 C |
|---|---|---|
| 22 A | 154.7 C | 161.0 C |
| 23 A | 162.6 C | 168.8 C |
| 24 A | 170.8 C | 177.1 C |

### 15.4 The selected element and the docking correction (prot 3 and 3a)

**C-1, an LM5069 circuit breaker on board P, the -1 (latch-off, 15.4b),** from Q2's source to PACK_P. It acts on current
alone, with no firmware and with Q1/Q2 welded. The parts are already in the kit:
- the controller's family, which board E's U6 uses (its -2 is LCSC C111822; Layer 6 files the -1's code, on the same VSSOP-10
  land);
- the FET board A's PA stage uses (C2876544);
- the clamp on board A's VBAT.

| Item | Value | From |
|---|---|---|
| Sense RS | 4 mOhm and 7.5 mOhm in parallel, 2.6087 mOhm, 1 % and at most 50 ppm/K: plus or minus 1.5 % for the parts only (the traces and Kelvin taps are E-9's) | its window 2.6015 to 2.6546 mOhm |
| Current limit | 18.32 least, 21.08 typical, **23.93 A largest**: 0.07 A under the cells' 24 A, 0.32 A over the 18 A service (VCL 48.5 to 61.5 mV, TJ -40 to 125 C) | **the table is printed at VIN 48 V and used at 10.6 to 16.8 V** (Q-TI-L9S-1, E-2, E-3, E-9) |
| Breaker | 30.21 to 50.59 A (VCB 80 to 130 mV), released 16.5 us after it (tCB 1.2 us, 690 nC at 45 mA) | the sheet's least sink |
| Power limit | RPWR 8.45 kOhm: 32.52 W, VSNS 5.05 mV; 24.71 to 40.32 W with the table's spread read as a ratio, 71.16 W read as an offset | relied on: without it 402.1 W (E-2, Q-TI-L9S-1) |
| Fault timer | 10 nF: 0.282 to 0.897 ms; the gate off 395 us later; **clearing at most 1.292 ms**; the insertion time 4.23 to 15.25 ms runs only when VIN passes PORIT (a start by the gauge's FET) | VTMRH, ITIMER, the insertion current at their limits |
| dv/dt start | 22 nF into 593 uF: **inrush at most 0.659 A** for at most 40.7 ms; 11.1 W, under the power limit's least 24.7 W | SLVA673A 2.2.2, 3.2.2.7 |
| The -2's timer ratio | at most 1.33 % (0.5 % typical), dwell at most 0.222 s; 15.4b judges the -2's whole cycle and rejects it | the timer at its limits |
| FETs | 2 x CSD18510Q5B, 40 V, VGS 20 V against the gate's 12.6 V, IDM 400 A against the breaker's 50.59 A | SLVA673A 3.1.2.2 |
| FETs held at 23.93 A | 0.247 W each; case 101.0 C with both losses through one pad, junction 101.2 C (TI asks under 125 C) | equation 4 |
| FET SOA at 16.8 V | case 103.0 C (the first revision's retry estimate, kept as a bound over the held 101.0 C), derating 0.376; fault pulse 40.32 W for 1.292 ms against 71.1 W: **0.57**; start 11.1 W for 20.3 ms against 19.0 W (DC line): **0.58**; with the figure's 10 % against them 0.63 and 0.65; TI asks at most 0.67 | equations 5 to 7 |
| Clamps | SMCJ18A on VIN (VR 18 V, VC 29.2 V at 51.4 A); D1 SMBJ20A on PACK_P carries the lead's freewheel at turn-off (LM5069 11.1.2 B), judged on I2t: its 100 A 8.3 ms half-sine is 41.5 A2s, which the freewheel at the pack's 480 A prospective stays within for any loop L/R up to 0.36 ms (12.6 uH in that loop) | IF-6: both return to PACK_N, so R10 sees a clamp short |
| Controller | VIN 9 to 80 V recommended, on from 9 V at most; the pack 10.6 to 16.8 V; OVLO to ground; UVLO from VIN through R_U 200 kOhm into C_U 3.3 uF (50 V), released by the enable loop | UVLOTH 2.45 to 2.55 V, UVLOHYS 12 to 30 uA, UVLODEL 55 us typical (no maximum) |

**B-P1, docking.** Without a correction the breaker is on when the dock's power pins mate, so a docking reaches E11-30's
242.9 A:
- VIN to SENSE reaches 0.634 V, against the controller's 0.3 V maximum;
- the 10 us line at 16.8 V, derated to the 103.0 C case, is 91.8 A: the peak is 2.64 times it, and 1.66 times at a 75 C case.

A known excursion in a normal event is a design correction, not a coupon.

**C-1b SELECTED: a make-last enable loop into UVLO, with an RC hold** (TI's remedy in the LM5069 sheet, 11.1.1 and Figure 45):
- **The circuit.** The loop leaves board P from VIN through 10 kOhm on one J_SMB contact, with a ground contact beside it, and
  crosses the dock on two contacts 1 mm short of the power pins. On board A it passes the chip PTC beside the battery FETs (the
  thermal guard, 15.5). It returns on a second J_SMB contact to a 22 kOhm divider on a first 2N7002's gate. That FET holds a
  second 2N7002's gate low; the second, when on, pulls UVLO itself.
- **The hold.** R_U, the series resistor (200 kOhm from VIN), charges C_U on a node H. H reaches UVLO through 150 ohm and a
  1N4148W. When the second inverter pulls UVLO, C_U drains behind it through the 150 ohm and the diode, so the turn-off no longer
  waits for C_U. The diode's peak, 107 mA, is 0.11 of its 1 A 1 ms surge rating and 0.71 of its 150 mA average rating.
- **The inverters' bounds.** The gates read at most 17.4 V under VIN's 29.2 V clamp against the 2N7002's 20 V. At the pack's
  10.6 V they read at least 2.95 V and 5.3 V, over its 2.5 V threshold. C_U's discharge peaks at 107 mA against its 115 mA.
  At 10.6 V, H settles at 4.6 V against the 30 uA hysteresis sink, over UVLO's 2.55 V and the diode's 0.715 V.
- **The timing, restated.** The insertion time runs only when VIN passes PORIT, so 4.23 to 15.25 ms applies to a start by the
  gauge's own FET, not to a docking. On the enable, the LM5069 raises the gate UVLODEL (55 us typical, no maximum printed) after
  UVLO passes its threshold. The RC hold, with the diode, makes that **0.110 to 0.907 s after the enable mates**. Then a dv/dt start follows:
  **0.659 A at most, VIN to SENSE 1.72 mV**.
- **Undocking.** The loop opens. The first inverter is off in 2.5 us and the second on in 16.0 us. UVLO falls at once, and the
  gate is low 395 us later (UVLODEL 11 us typical, no maximum printed): **0.41 ms in all**. That is before the pins part at a
  withdrawal under **2.42 m/s**. Through C_U, the first draft of the hold, it took 1.51 ms, or 0.66 m/s, which a hand can exceed.
  C_U now drains in 1.10 ms behind the turn-off.
- **The gauge's own FET.** Its turn-on is a start too, so E11-30's waveform no longer arises.

**Condition C1, the mating order** (owners: Layer 7 for the order, board P's generator for the hold). Every power pin mates
before the enable contacts at any angle the dock's guides allow.
- **Without a hold:** a reversed order of more than 1.88 ms lets OUT rise (at 1.111 V/ms) past 2.09 V and meet the breaker's
  30.21 A threshold through the 69.2 mOhm loop at mate.
- **SELECTED, the RC hold:** a reversed order up to 111.6 ms is tolerated. The order remains Layer 7's condition beyond that.

**Condition C2, a fault on the enable** (owners: board P's and board E's generators, Layer 7, the supplier for E-12). The enable
is a loop through board A, not a single wire to its ground.
- **A short to ground** on either conductor holds the breaker off: fail-safe, and revealed at the next docking because the kit
  does not start.
- **A short between the two conductors** is kept off by a ground contact between them in J_SMB and on the block.
- **The inverters' own failures** are the remaining latent faults. E-12 finds them at commissioning and at each service: PACK_P
  dead undocked, and each loop conductor shorted to ground in turn.

**Not taken: an inrush element at board A's dock entry.**
- Board A's pre-charge pin J_PRE1 (10 ohm into 593 uF, a 5.93 ms time constant) would need a lead over the power pins: 12.4 ms to
  keep the step under the breaker's least threshold, and 4.3 ms to keep VIN to SENSE under 0.3 V. A hand sets the lead.
- A series element in the 23.93 A path heats beside the battery FETs, whose junction is the binding limit (15.5).

**The charge direction.** The LM5069 limits no reverse current. A charge passes the FETs' channel while the breaker is on, and
their body diodes while it is off. The gauge's 1 A precharge in one diode is 1.00 W (VSD 1 V at most), TJ 126.2 C. The charger
bounds the charge current, the gauge's own levels protect it, and F1 and F2 back them, as before.

**Board P's area (IF-2).** The 0.376 derating rests on the FETs' installed path. TI's margin holds up to an installed RthJA of
**52.5 C/W per FET**. The sheet prints 50 C/W on 1 in2 of 2 oz and 125 on its least pad.
- Board P is 70 x 44 mm (3080 mm2 a face). The P2 placement uses 798 mm2 of the top face, and the holes 199. The bottom face is
  empty.
- Two 1 in2 pads take 1290 mm2 of the 2084 mm2 left. That leaves 793 mm2 for the round 4 parts, the breaker's other parts and
  the bands where they do not lie in the pads (the FETs' drain pads are the breaker's input band).
- This is an area budget, not a floor plan. The generator shows the plan, and E-11 measures the installed path.

**Also not taken (prot 3):**
- A breaker limited to the pair's 20.53 A: its least limit, 15.71 A, falls under the service.
- A blade opening under the pair's current: at most 15.21 A, and the service at 118 % of it is not assured.
- A single-wire enable to board A's ground: a short to ground, the commonest harness fault, would enable the breaker unseen (C2).
- No RC hold: a reversed mating order of 1.88 ms would bring B-P1 back (C1).
- A controller with a tighter limit tolerance now: the LM5066I of SLVA673A's examples, its sheet not held. It is E-5's fallback.

**The clamp failing resistive with board P's FETs welded** (two faults, 33.75 to 150 A). The breaker is downstream of the clamp
and cannot act. Board P's loop and the clamp itself then carry the current on F1's 600 s and 5 s rows, and F2's 200 % opens
within 60 s. Alone, the clamp's failure is cleared by the AFE's AOLD (30 A, 20 ms) through Q1/Q2. Disposition: a second fault,
stated, no new defect; the battery stream reviews it.

### 15.4b The retry: the -2's repeated waveform against every protected part, and the -1 (prot 3b)

**What the sheet says.** The -1 latches off on a fault; the -2 retries (section 5). On the -2, after the fault time the TIMER cycles
seven times between its restart threshold and VTMRH. The gate turns on at 0.3 V on the eighth fall, and the fault time and the
restart repeat while the fault remains (8.4.3).

**One cycle, with C_T at 10 nF plus or minus 10 %.**
- **On:** 1.076 to 1.227 ms (the fault time from 0.3 V, then the gate's turn-off).
- **Off:** 50.7 to 62.0 ms.
- **Ahead of it:** a ramp while the load lets the output rise, at 0.413 to 1.111 V/ms.

**The series current per cycle** never exceeds the largest limit (23.93 A), nor the power limit over VDS.
- Through the slowest ramp and the limited phase: at most 5.14 A2s and 0.351 As a cycle.
- Over the cycle: at most 55.6 A2 on average, 7.46 A RMS, which is 0.097 of the held 23.93 A's heating.

**Each protected part through a persistent fault on the -2, settled from the inside air's 76.25 C:**

| Part | Energy a cycle | Average | Settled | Limit | Verdict |
|---|---|---|---|---|---|
| board P's Q1/Q2, enhanced (each) | 6.4 mJ | 0.069 W | TJ 83.2 C (both losses through one pad) | 150 C | within |
| **board P's Q1 under BAT-F20** (its body diode) | 351 mJ | 3.80 W | **TJ 266 C** | 150 C (1.48 W on its pad) | **OVER**: DD-5, as in the held and service rows |
| the three battery FETs (each) | 12.1 mJ | 0.131 W | TJ 83.4 C | 150 C | within |
| R17 (5 W) | 25.7 mJ | 0.278 W | | 5 W | within (derating NOT HELD, E-6) |
| R10 (2 W) | 10.3 mJ | 0.111 W | | 2 W | within (E-6) |
| the breaker's sense | 13.4 mJ | 0.145 W | | 2 W each (a requirement) | within |
| the XT60 (30 A) | | 7.46 A RMS, 23.93 A peak | | 30 A | within |
| the dock contacts | | 1.86 A RMS a pin at an even split | | 9 A | within (E-4) |
| the pack path's copper | | | 0.89 K over the air | 10 K | within |
| the barrel field | | | 0.74 K | 10 K | within |
| the 25 A blades and F2 | | 7.46 A RMS | | 25 A, 30 A | within (E-7) |
| the Keystone 3568 holder | | 7.46 A RMS | | no rating printed | NOT HELD: DD-4 |
| the cells | | 7.46 A RMS | | 24 A | within |
| the enable loop's parts (2N7002s, PTC, R_U, C_U) | 0 | the loop's static 0.45 mA | | | not cycled by the -2's restart, which is internal |
| **the breaker FET, a hard short** | 43.4 mJ | 0.84 W | **case 118.1 C** | SOA with TI's 1.5x margin (0.67) | **OVER TI's margin: 0.79** (0.88 with the reading) |
| **the breaker FET, a resistive fault on VSYS** (0.915 ohm, just over the least limit at full voltage) | 174 mJ (130 in 5.6 ms of ramp) | 3.03 W | **case 228 C** | 150 C | **OVER** |

**So the -2 does not meet the criterion.**
- Its repeated waveform takes the breaker FET past TI's margin in a hard short, and past 150 C in a resistive fault on VSYS.
- No pad on board P's area brings the resistive case under 150 C.
- Every other protected part settles under its held reading (15.5). The exception is Q1 under BAT-F20 (DD-5), which is already
  over in the held and service rows.

**The -1 against the service and the recovery.**
- **The service.** The 10 A and the 18 A never reach the least limit, so neither variant trips in the service.
- **After a fault.** The -1 stays off; on battery the kit goes dark. CONOPS 4e already states this for the over-current backstop
  ("recovers only on an input"), and POWER-THERMAL 9.3 takes it as the safe state ("restarting into the same load would repeat
  it").
- **Recovery:**
  - by redocking, since the loop pulls UVLO low;
  - by an input's return (DD-7);
  - by the thermal guard's own cycle.
- **The restart condition.** The timer falls under its 0.3 V re-enable threshold in 34.0 ms at most, inside the RC hold's least
  0.110 s, so a redocking restarts the breaker.

**SELECTED: the -1 (latch-off).** Every protected part then meets one fault event, at the per-cycle energy above, with no
accumulation.

**A fault just under a unit's limit and over the service** is held and never trips, on either variant. Every part sits at its
held reading (15.5).
- **Loads IF-1 holds off:** the thermal guard bounds the battery FETs, tripping and restarting at the PTC's rate (E-13).
- **A resistive fault on VSYS,** which IF-1 cannot hold off, latches the -1 at the guard's first restart.
- **Q1 under BAT-F20** is OVER (DD-5).

**IF-1 is now critical to the service.** Under the -1, a start that meets the power limit runs the timer and latches the
breaker. The start leaves room for at most 0.81 A of load at full VDS: the power limit's least, less the inrush's 11.1 W.
L4-E11 owns the hold-off.

**Which UVLO edge.** The sheet asks for the timer under 0.3 V for a restart, but does not say at which edge.
- **Read at the falling edge:** a pulse within 34.0 ms of a latch does not restart. That fails safe: the breaker stays off, and a
  later pulse or a redocking restarts it.
- **Read at the rising edge:** the RC hold's least 0.110 s covers it.

**The -2's timer ratio** (1.33 % at most) is conservative: it pairs the slowest fault current (on) with the fastest sink (off).

**B-R1: a start into the worst resistive fault on VSYS** (0.915 ohm) is either variant's first event:
- 180 mJ, an equivalent 40.32 W for 4.46 ms (SLVA673A equation 7);
- from the inside air, 0.54 of the derated SOA (TI's start basis; 0.60 with the reading);
- **hot, 0.82 at the held 101.0 C case and 0.85 at 103.0 C.** That is past the 1.5x margin the -2 was rejected on, and hot
  restarts are credible: the guard's cycle, DD-7's pulse, a quick redock.

**ONE CRITERION FOR BOTH VARIANTS:** TI's 1.5x margin over the derated SOA for every event, at the case it can occur at.
- **The -2 fails it:** 0.79 in a hard short, 228 C in a resistive fault.
- **The -1 meets it only if** a restart happens at a case of 89.9 C at most (83.2 C with the reading allowance).

**C-1c SELECTED: a restart inhibit on the breaker pad** (DD-8, owner board P's generator, record l8p):
- **The sensor.** The kit's NTC sheet part, Murata NXRT15XH103FA1B (10 kOhm plus or minus 1 %, B25/85 3434 K, B plus or minus
  1 %), in a ratiometric bridge from VIN. The bridge has 150 kOhm over the NTC: 0.111 mA at most, against its 0.12 mA.
- **The action.** The bridge drives a comparator that pulls UVLO. It is gated so that it acts only while PGD is low: the breaker
  off, starting or in a fault (VDS over 1.62 to 3.4 V). It never acts on a running breaker, so the service is untouched.
- **The window.** Allow from 77.25 C (the inside air plus 1 K, since the pad nears the air only slowly); block from 83.20 C. The
  trip is 80.22 C plus or minus 2.97 K, with the NTC at 1653 ohm.
  - The NTC takes plus or minus 1.02 K (R 0.36, B 0.65, the B tolerance taken as printed at 25/50).
  - That leaves plus or minus 1.95 K for the comparator (1.59 mV of offset is 0.5 K at 0.116 V), the bridge, the hysteresis and
    the pad's gradient (E-15).
- **The margin.** The worst resistive start is 0.54 from the air and 0.57 at the trip (0.64 with the reading). At the block edge
  it is 0.60, or **0.67 with the reading**: every restart the inhibit lets through is within TI's margin.
- **A fault while hot.** PGD low lets the inhibit pull UVLO, which the -1 does not latch. The breaker restarts when the pad cools
  under the trip, so any further event starts at 83.2 C at most.
- **The cost.** A quick redock, or DD-7's pulse, after heavy use waits for the pad to cool. That time is NOT HELD (E-15).

**Not taken: one criterion at the SOA itself** (under 1 with the reading) instead of the inhibit. It would accept the -1's hot
restart at 0.95 but leave 5 % against a power limit whose spread at 5 mV is not printed (E-2).

E-3 now includes ten starts into the 0.915 ohm fault with the FETs' case at 103 C.

**New items from this check:**
- **DD-7** (owners: board A's generator with L4-E11; board P's generator for the -1). Board A opens the enable loop for a pulse
  when an input appears, so the latch resets and the breaker restarts within 0.948 s (the hold and the start), or later if the
  restart inhibit holds it. The charge through a latched breaker's body diodes until then is L4-E11's hardware charge inhibit
  (B-R2, their running round).
- **E-14.** The charge through a latched breaker, at the charger's largest current, until that restart.
- **DD-8** (owner: board P's generator, record l8p). The hot restart; C-1c, drafted here, not drawn. **E-15** measures it.
- **IF-7** (owner: the firmware owner). The bridge reports a tripped breaker and enables charging only after the breaker's
  restart.

### 15.5 B-P2: the battery FETs' junction limit, and the selection (prot 4)

**The limit (DD-2 and E-1, restated).** The hottest battery FET's junction stays at most 150 C, held at 23.93 A from 76.25 C,
with these in place:
- the band carrying the current (9.16 K at either weight, decision 35's model);
- R17 dissipating its 2.86 W.

That leaves 64.59 K for the FETs and R17's coupling.

**R17's coupling is bounded with no layout known.** In a passive thermal network the point heated is the hottest, and transfer
impedances are reciprocal. So R17's coupling into a junction is at most that FET's own Zself. Designed apart (off the FETs' pour),
it is held to 1 K/W, which E-1 reads by heating R17 alone.

| FETs | Loss each at 23.93 A | FETs only | R17 apart (1 K/W) | R17 anywhere |
|---|---|---|---|---|
| the pair, (Zself + Zmut) | 3.027 W | 21.34 K/W | **20.39 K/W** | 10.96 K/W |
| three, (Zself + 2 Zmut) | 1.345 W | 48.01 K/W | **45.88 K/W** | 15.34 K/W |

E11-29's target for the pair was 33.12 K/W, which L4-E11 judged of the order a board pour gives; its round 9 withdraws it and
restates E11-29 as this limit (45.88 K/W a FET with R17 apart). The first revision's 24.37 K/W
counted the FETs' heating only; with the band's 9.16 K it reaches 159.2 C.

**SELECTED: a third BUK6Y10-30P, with R17 designed apart.** L4-E11's round 9 drafts it as Q42 (not applied): Q41 is taken on
board A by record l8r2's VIN_RAW cut-off FET (CSD19532Q5B).
- **Why.** The path it asks is 1.39 times E11-29's former target, where the pair would need 0.62 of it.
- **Cost.** Ciss: three FETs are 7.08 nF typical at -15 V and about 8.61 near 0 V, against TI's 5 nF guidance (SLUSE65A p.92). The
  pair is already over that guidance near 0 V (5.74 nF), so E11-37's bench with three FETs decides, with Q-TI-17 extended to
  three. **Condition C3** (owner L4-E11): production conformance needs Q-TI-17's answer or E11-37's bench with three.
- **Fallback.** The pair at 20.39 K/W.

**THE THERMAL GUARD, reconsidered and SELECTED** (owners: board A's generator with L4-E11 for the PTC beside the battery FETs,
board P's generator for the divider). It guards against the 45.88 K/W path never being met, unit by unit, which a coupon
cannot.
- **The part.** The kit's PRF15BB103 chip PTC: 10 kOhm plus or minus 50 %, 47 kOhm at 130 C plus or minus 3 C, 32 V. It is
  already on board P as RT1.
- **Where.** In the enable loop on the battery FETs' copper.
- **The trip.** The first inverter stays on up to 47 kOhm at 10.6 V (its gate 2.95 V against 2.5 V) and is off from 338 kOhm at
  16.8 V. So the breaker opens between the PTC's 47 kOhm point (127 to 133 C) and its 338 kOhm point, which the sheet does not
  print (E-13).
- **Margins.** The service at the allowances reads 118.0 C, 9.0 to 15.0 K under the band. A junction leads its copper by 1.88 K
  at 23.93 A (Rth(j-mb) 1.4 K/W).
- **Restart.** After a trip the breaker restarts through the RC hold when the PTC cools.

At the allowances the junction reads:
- 89.4 C at 10 A;
- 118.0 C in the 18 A service;
- 150.0 C at 23.93 A, by construction.

**The other series parts at 23.93 A from 76.25 C:**

| Part | Reading | Fraction | Status |
|---|---|---|---|
| the cells, 3P of 8 A | 7.98 A a cell at an even split | 1.00 | printed; E-5: the groups must share within 0.28 %, so its **fallback is named now**: a controller whose limit spread with its sense is at most 1.270 (for a 5 % split; the LM5069's is 1.307) |
| **Q1 on board P under BAT-F20** (CHGIN = 1, the reading above T3) | **its body diode 23.9 W** (VSD 1 V at most); about 7 W at 10 A already | | **DESIGN DEFECT DD-5** (BAT-F20, EQ-15) |
| Q1/Q2 on board P, both enhanced | 0.711 W each; TJ 111.8 C on its own pad, 147.4 C with both losses through one pad | 0.96 | derived; the x1.8 is the CSD18510Q5B's (ASSUMPTION, E-8) |
| the breaker's FETs | TJ 101.2 C | 0.51 of TI's 125 C | derived (IF-2, E-11) |
| R17 (5 W) | 2.86 W | 0.57 | derating NOT HELD (E-6) |
| R10 on board P (2 W) | 1.15 W | 0.57 | derating NOT HELD (E-6) |
| the breaker's sense | 0.97 W in 4 mOhm, 0.52 W in 7.5 mOhm | | a requirement on Layer 6's parts: 2 W each at the band's temperature |
| the XT60 (30 A) | 23.93 A | 0.80 | printed |
| the dock contacts | 5.98 A a pin at an even split | 0.66 | the split NOT HELD (E-4) |
| the 25 A blades | 95.7 % of rating | 0.87 of the 110 % hold | E-7 |
| F2's element (30 A) | 79.8 % | 0.80 | printed |
| the copper | 9.16 K | 0.92 of 10 K | section 14 |
| the barrel field | 0.75 A a barrel, 7.62 K | 0.76 | section 14 |
| the 3568 holder | no current rating | | DESIGN DEFECT DD-4 |

### 15.6 The protection table (prot 5)

| Case | Current, duration | Largest actual trip threshold | Longest clearing time | Limiting component | Margin | Evidence |
|---|---|---|---|---|---|---|
| 10 A continuous | 10.0 A held | none reached (18.32 A least) | not a fault | **Q1's body diode under BAT-F20** (CHGIN = 1, above T3), 7 to 10 W against the 1.48 W its pad holds; with BAT-F20 closed, the XT60 at 0.33 | **Q1 OVER (4.7 x)** | **DESIGN DEFECT DD-5**; printed (VSD, RthJA) |
| 18 A for 60 s | 18.0 A, 60 s | none reached (18.32 A least; 21.08 A typical) | not a fault; firmware ends it | **Q1's body diode under BAT-F20, up to 18 W**; with BAT-F20 closed, the battery FETs at 118.0 C (the guard 9.0 to 15.0 K above) | **Q1 OVER**; 32.0 K at the battery FETs; the least limit 0.32 A over the service | **DESIGN DEFECT DD-5**; derived; E-1, E-10 (the key-down current), E-13 |
| an overload under the unit's limit, held | 18.00 to 23.93 A, indefinitely | 23.93 A (VCL 61.5 mV, RS -1.5 %) | none: held by design; the thermal guard trips and restarts at the PTC's rate (either variant) | the battery FETs at 150.0 C; the cells at 0.997 of 8 A; **Q1's body diode 23.9 W under BAT-F20** | 0 K at the allowances; 0.28 % split; **Q1 OVER** | **DESIGN DEFECTS DD-2, DD-5**; E-1, E-5 |
| an overload over the unit's limit | limited to 23.93 A, then off | 23.93 A | 1.29 ms from the onset (timer 0.897, gate 0.395); regulated after tCL (45 us typical, no maximum) | the breaker FET, 40.3 W for 1.29 ms against 71.1 W | 0.57 (TI at most 0.67) | derived: the power limit at 5 mV and 10.6 to 16.8 V not printed (E-2) |
| a hot short, board P's FETs welded | 240 to 480 A prospective | 50.59 A (VCB 130 mV) | 16.5 us to the release, then as above: 1.31 ms | the breaker FET: IDM 400 A against the breaker's threshold; VIN to SENSE over 0.3 V above 116.8 A | 0.13 of IDM | (c) MISSING: E-3; the 0.3 V to TI (Q-TI-L9S-1) |
| a start into a short | 2.40 A at most | the power limit | 1.29 ms | the breaker FET, as above | 0.57 | derived |
| a start (the gauge's FET on, a retry, assembly) | 0.659 A at most for 40.7 ms, from the insertion's end (4.23 to 15.25 ms after VIN passes PORIT) | none: 11.1 W under 24.7 W | not a fault | the breaker FET, 11.1 W for 20.3 ms against 19.0 W | 0.58 | derived; IF-1 |
| **docking, the make-last enable (C-1b)** | 0.659 A at most for 40.7 ms, from 0.110 to 0.907 s after the enable mates (the RC hold, then UVLODEL 55 us typical, no maximum) | none: a start | not a fault | the breaker FET as a start; VIN to SENSE 1.72 mV | **0.58** | derived; DD-6 until drawn; conditions C1, C2; E-3, E-12 |
| docking without the enable (the uncorrected design) | E11-30's 242.9 A with the breaker on | 50.59 A | 16.5 us to the release | the 10 us line derated to 103.0 C is 91.8 A; VIN to SENSE 0.634 V | **OVER**: 2.64 x the line (1.66 x at 75 C); 2.11 x 0.3 V | **DESIGN DEFECT DD-6**, corrected by C-1b (not a coupon) |
| a persistent fault on the -2 (rejected, 15.4b) | the restart cycle: 1.08 to 1.23 ms on, 50.7 to 62.0 ms off, repeated | as above | each cycle as above | the breaker FET: a hard short 0.84 W average, case 118.1 C; a resistive fault on VSYS 3.03 W, case 228 C | **OVER**: 0.79 of the derated SOA (TI at most 0.67); over 150 C | derived; the -2 rejected, corrected by selecting the -1 |
| **a persistent fault on the -1 (selected)** | one event, then latched until UVLO or VIN cycles | as above | 1.29 ms, once | the breaker FET at 0.57; every series part once, at its per-cycle energy (15.4b) | no accumulation | derived; recovery by redocking, the input's return (DD-7), the guard's cycle |
| a start into a resistive fault on VSYS (the worst, 0.915 ohm; either variant's first event) | 180 mJ: 5.6 ms of ramp, then the power limit | the power limit | 1.23 ms after the limit | the breaker FET, 40.32 W for 4.46 ms equivalent (SLVA673A equation 7) | 0.54 from the air; at most 0.60 at the restart inhibit's block (83.2 C), **0.67 with the reading**; without it 0.82 at the held 101.0 C | derived; C-1c (DD-8); E-3, E-15 |
| charging (the reverse direction) | the charger's current; 1 A precharge in a body diode while off | none: no reverse limit | not a fault | the breaker FET's body diode, 1.00 W, TJ 126.2 C | 23.8 K | printed (VSD); derived |
| the clamp shorted with board P's FETs welded (two faults) | 240 to 480 A prospective | F1, 25 A MINI | at most 0.1 s at 150 A and over | board P's bands (decision 28) | the clamp's short alone is cleared by the AFE's ASCD (R10 sees it, IF-6) | printed (F1's 600 % row); disposition stated, no new defect |
| the clamp failing resistive with board P's FETs welded (two faults) | 33.75 to 150 A | F1 and F2 | F1's 600 s and 5 s rows; F2's 200 % opens within 60 s | the clamp's own dissipation and board P's loop; the breaker is downstream and cannot act | alone, the AFE's AOLD (30 A, 20 ms) through Q1/Q2 | printed (F1's and F2's rows); a second fault: disposition stated, no new defect (the battery stream reviews) |
| the shore input, Q7 shorted | F1's envelope (not through board P) | F1, 10 A MINI | section 14.6 | J_DCIN, R19 | **OVER** | **DESIGN DEFECT DD-3** (L4-E11) |

**The supported operating envelope**, once DD-1, DD-2, DD-5 and DD-6 close:
- 10 A held and 18 A for 60 s from 76.25 C, with no trip on any unit;
- any current to 18.32 A held on every unit;
- between 18.32 and 23.93 A, a unit holds or clears by its own threshold;
- above 23.93 A, every unit clears within 1.29 ms of its limit's onset;
- a docking is a start;
- a fault latches the -1 once; recovery by redocking, an input's return or the thermal guard's cycle;
- no firmware and no working FET of board P in that path.

### 15.7 Design defects, interfaces and the evidence owed (prot 6)

**Design defects** (unresolved; a coupon never stands in for their correction):

| Defect | Owner |
|---|---|
| DD-1 W4DP-F2: no firmware-independent element with board P's FETs welded; the breaker of 15.4 is drafted here, not drawn | board P's generator, with W4DP-F2's owner (the battery stream) |
| DD-2 the battery FETs' junction limit (15.5): a third BUK6Y10-30P (L4-E11's round 9 drafts it as Q42, not applied), (Zself + 2 Zmut) at most 45.88 K/W with R17 apart, the thermal guard behind it; the pair would need 20.39; condition C3 | L4-E11 (E11-29 restated as the junction limit and the third FET drafted as Q42 in its round 9, not applied; E11-37 with three) |
| DD-3 R19 passes its 3 W and J_DCIN its VH rating inside F1's envelope on the shore input (section 14.6) | L4-E11 |
| DD-4 the Keystone 3568 holder prints no current rating | Layer 6/7 |
| DD-5 BAT-F20: with CHGIN = 1 above T3 the discharge runs through Q1's body diode, 23.9 W at the breaker's 23.93 A | the battery stream (BAT-F20, EQ-15) |
| DD-6 docking with the breaker on is past its SOA and VIN to SENSE's maximum; C-1b, the make-last enable loop with its RC hold and the thermal guard, is drafted here, not drawn; conditions C1 and C2 (15.4) | board P's generator with the battery stream (the UVLO circuit and the hold); board E's generator (two J_SMB contacts with a ground between); Layer 7 with L4-E11 (two make-last dock contacts, the loop and the PTC on board A) |
| DD-7 the -1 stays off after a trip until UVLO or VIN cycles: board A opens the enable loop for a pulse when an input appears, so the latch resets and the breaker restarts within 0.948 s, later if the restart inhibit holds it; the charge through a latched breaker until then is L4-E11's hardware charge inhibit (B-R2), E-14 | board A's generator with L4-E11; board P's generator (the -1) |
| DD-8 a hot restart of the -1 into the worst resistive fault on VSYS reaches 0.82 of the derated SOA at the held 101.0 C case, past TI's margin: C-1c, the restart inhibit on the breaker pad (block from 83.20 C, allow from 77.25 C, trip 80.22 C plus or minus 2.97 K), drafted here, not drawn | board P's generator (record l8p) |

**Interface demands:**
- **IF-1, CRITICAL TO THE SERVICE under the -1** (a start that meets the power limit latches the breaker): board A's loads on
  VSYS stay off, under 0.81 A at full VDS, until the breaker's start ends (at most 40.7 ms after the gate rises, which is up to
  0.907 s after the enable mates), or follow its PGD. Owners: L4-E11 with board A's generator.
- **IF-2** each breaker FET's installed RthJA at most 52.5 C/W; the area budget of 15.4; the controller beside RS, and VIN's
  bypass at RS (the sheet's 11.1). Owner: board P's generator.
- **IF-3** a stage for the breaker in the energy chain, between PACK_FETS and PACK_LEAD (its limit 23.93 A). Owner: the
  integrator.
- **IF-4** the gauge's levels stay the first level; no setting changes. Owner: the firmware owner.
- **IF-5** the pack's terminal is live only while the enable is closed; any other host closes it or gets a dead terminal
  (fail-safe). Board A's J_PRE1 and R1 are no longer exercised at docking, and E11-30's docking waveform no longer arises.
  Owners: the battery stream (CONOPS), board A's generator, L4-E11.
- **IF-6** the gauge's PACK and VCC taps stay on Q2's source node, and the clamp and the controller return to PACK_N. The
  breaker's output becomes the terminal PACK_P, with D1 on it (judged on I2t, 15.4). The enable circuit's parts and bounds are
  those of 15.4. Owner: board P's generator.
- **IF-7** the bridge reports a tripped breaker (the pack's terminal dead while the gauge's FETs are on) and enables charging only
  after the breaker's restart; recovery on battery is redocking. Owner: the firmware owner.

**Missing physical evidence** (specimen; acceptance; supplier task):

| Item | Specimen | Acceptance | Task |
|---|---|---|---|
| E-1 the battery FETs' junction limit | L4-E11 section 17's coupon with the three battery FETs, the band carrying 23.93 A and R17 dissipating in place | the hottest junction at most 150 C referred to 76.25 C; R17's coupling into each junction at most 1 K/W (heat R17 alone) | the body diode's VSD method |
| E-2 the power limit at its design point | six LM5069-1 on the board P specimen | the shorted-output current at 16.8 V and 10.6 V within 1.47 to 2.40 A at -40, 25 and 125 C (the table is printed at 48 V) | the supplier's bench |
| E-3 the hot short and the enabled docking | board P with Q1/Q2 bypassed, the 12 AWG lead, boards E and A as built, a charged block | 10 shorts, 10 starts into a 0.92 ohm fault on VSYS and 100 dockings with the FETs' case at 103 C: the gate low within 16.5 us of VCB; the -1 latched after each fault; the docking current at most 0.659 A; VIN to SENSE recorded; VCL within 48.5 to 61.5 mV; each FET's RDS(on) within +5 % | the supplier's fault bench |
| E-4 the dock contacts' split | the fitted lot's four-pin set | the lowest pin at least 0.593 of the highest, at the blades' 25 A (0.553 at the breaker's 23.93 A) | each pin at mid-stroke |
| E-5 the cells' parallel split | each series group of the built block | no cell over 8 A at 23.93 A (within 0.28 %); fallback: a controller whose limit spread is at most 1.270 | the pack builder; Layer 6 for the fallback's sheet |
| E-6 R17, R10 and the breaker's sense derated | the makers' sheets | each at its 15.5 reading at the band's temperature | Layer 6 |
| E-7 the blades at the inside air | the fitted lot in the 3568 holder | the service itself: 18 A for 60 s after 10 A held at 76.25 C, without opening | the supplier; Layer 6 reads the rerating curve |
| E-8 Q1/Q2's installed path and RDS(on) at temperature | board P's first specimen; the CSD17570Q5B's Figure 8 | TJ under 150 C at 23.93 A from 76.25 C, both enhanced | board P's generator; Layer 6 |
| E-9 the breaker's actual current limit | six board P specimens, the paralleled shunts' traces and Kelvin taps as built | between 18.32 and 23.93 A at -40, 25 and 125 C, at 10.6 and 16.8 V | the supplier's bench |
| E-10 the pack current at key-down | board A and the transmitters at the 18 A service | under 18.32 A, or excursions above it each under 0.282 ms and under 1.03 % of the time (the timer integrates them) | the supplier's bring-up bench |
| E-11 the breaker FETs' installed path | the board P specimen | RthJA at most 52.5 C/W per FET | the body diode's VSD method |
| E-12 the enable loop | the built kit at commissioning and at each service | undocked, PACK_P dead; each loop conductor shorted to ground in turn, the breaker stays off when docked; the release after the enable mates at least 0.110 s | the supplier's commissioning procedure |
| E-13 the thermal guard | the battery FETs' coupon (E-1) with the PTC in place, and one with a FET's thermal pad left unsoldered | no trip through the service (18 A for 60 s after 10 A held at 76.25 C); the breaker off before the hottest junction passes 150 C at 23.93 A held | the supplier's thermal bench |
| E-14 the charge through a latched breaker | the board P specimen latched, the charger at its largest charge current | the breaker FET's junction under 150 C until the input-return reset restarts it (0.948 s at most), behind L4-E11's charge inhibit | the supplier's bench |
| E-15 the restart inhibit | the board P specimen with the NTC on the breaker pad | a restart allowed with the pad at 77.25 C, blocked at 83.20 C; the pad-to-NTC gradient measured while the pad cools after 23.93 A held; the cooling time to the trip recorded | the supplier's thermal bench |

**Maker questions, drafted, not sent:**
- **Q-TI-L9S-1 (TI, the LM5069).** Three questions:
  - the power limit's accuracy at VSNS 5.05 mV;
  - every limit at VIN 10.6 to 16.8 V, since the table is printed at 48 V;
  - VIN to SENSE above its 0.3 V maximum in the microseconds before the gate is low in a hot short (above 117 A on this sense).
- **Q-TI-17 (L4-E11's).** The BATFET's 5 nF guidance, now with three FETs.

### 15.8 What the recheck covers, and the next deliverable

After the conditional confirmation the coordinator checks these corrections; no further independent recheck. The scope stays
the changed protection design and its affected interfaces only:
- `l9stk_protection.py` and its output;
- option (4) of (L9STK CU) in `l9stk_copper.py` (out 8) and `apply_decisions_l9stk.py`;
- the findings L9C-F16 to L9C-F22.

The copper sizing of section 14 is unchanged.

**Next deliverable**, in this order:
1. Board P's generator draft of the breaker, the -1, with its enable loop, its RC hold with the diode, and the restart
   inhibit (DD-1, DD-6, DD-8 in record l8p, IF-2, IF-3, IF-6).
2. Board E's two J_SMB contacts with a ground between, and Layer 7's two make-last dock contacts with the loop and the PTC on
   board A (DD-6, C1, C2).
3. L4-E11's third battery FET, its designator, and E11-29 restated as the junction limit (DD-2, C3), with IF-1; board A's
   input-return pulse on the enable loop (DD-7) and the firmware's IF-7. (Drafted in L4-E11's round 9, not applied: Q42, its
   section 19; E11-37 with three, C3, stays open.)
4. The battery stream's answer to BAT-F20 (DD-5).
5. Then the supplier's E-1, E-2, E-3, E-9, E-11 to E-15 on the first specimens.
