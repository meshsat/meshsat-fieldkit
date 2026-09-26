# Board B feasibility: why B21 does not route, what could change that, and one bounded trial

MESHSAT-1357, workstream W3. Written 25 September 2026 at repo HEAD `e6291404`; revised 26 September 2026 at `82dd1e4d`
after review, again the same day at integration (the plan citations now point at `v2/docs/EXECUTION-PLAN.md` and
decision 43), against `main` at `d468613e`, which filed the fabricator transcription and TE's drawing and recorded the
eight-layer stackup row this page asked for, and against `main` at `6104cb81`. **Re-anchored the same evening to `main`
at `eadbe571`.** Since `458b2873` board B's generator and its committed netlist carry the corrections of Appendix A
(round 6 of Review D, regenerated with parity, RECORDED), so Appendix A now reads as the record of B21's netlist and
of what was corrected; the committed B21 **board** and its pre-route snapshot are unchanged since `82dd1e4d` and still
carry B21's netlist. The failover fabric's own review, `v2/docs/feasibility/FAILOVER-FABRIC.md` (`a5266aa8`), adds four
circuit findings in the same pockets (FAB-01 to FAB-04) and the placement item FAB-08, which this page's trial limits
now carry. Every citation below was re-read at `eadbe571`. The system view this page sits in is
`v2/docs/ARCHITECTURE.md` (its section 14 lists this page's open items as blocker FB-FAB). **Prototype design: no V2 board has been built, and board B has never been routed to
completion.** This
page is a diagnosis from existing artefacts and a specification of one experiment. It proposes no layout, adopts no
phase, and authorises nothing: under the owner's condition 7 of 25 September, feasibility evidence is separate from
layout authorisation.

Evidence labels: **VERIFIED** (read in the artefact cited), **RECORDED** (a measurement written into
`v2/ecad/tools/boards/b.json` or `pcb_decisions.yaml` whose underlying run is not in this tree, so it is cited, not
re-read), **INFERRED** (reasoned from verified facts, stated how), **TBD** (no source; effect stated).

## 1. The short answer

Board B's failure to route is **not shown to be physically impossible**, and **more layers alone would not remove the
part of it that is measured most directly**. Three things are tangled together:

1. **A floor plan that sends every slot's high-speed traffic 85 to 90 mm away and back.** Each module's receptacles sit
   at y 52.5, the M.2 socket row at y 87, and the slot's own PCIe switch, USB hub and host-select muxes at y 137 to 157,
   beyond the sockets. The display, Ethernet and USB failover buses of all three slots then cross the board to parts at
   its far edges. The three switch pockets have 0.0 mm of room on at least three sides (`S3_SWIC` has 1.0 mm west).
   (Section 3.3.)
2. **An escape method with one strategy.** The escape collisions that the placement predictor counts (about ten, under
   every lever tried) are collisions of `escape.py`'s own pattern: a surface stub to a through via outside the pad, at
   fixed via sizes. That pattern is independent of layer count. The fabricator's default via-in-pad process on six or
   more layers, which changes the pattern itself, has never been used for the fine-pitch signal escapes (`prefanout.py`
   already puts some plane-pad vias in the pad: 68 to 86 of them on board B, `b.json
   _the_fanout_in_pad_fix_measured_on_this_board`). (Sections 3.1, 3.2, 4.)
3. **A stackup used with two good signal layers out of four.** On the JLC06161H-3313 stack as board B uses it, the two
   inner signal layers sit 0.109 mm apart and 0.55 mm from their planes; pairs routed there solve to 140.5 ohm against
   the 100 asked. (Section 3.2.)

On top of that, **B21's netlist had schematic defects in exactly these pockets** (Appendix A): every PCIe downstream
link and the LimeSDR SuperSpeed link were wired transmitter to transmitter, 18 capacitors were missing (12 host-side AC
coupling capacitors on the downstream transmit pairs and 6 reference clock capacitors the switch's datasheet
recommends), and slot 2's 5G socket was a key M part for a key B module. For the 5G link Quectel's reference circuit
shows the host-side capacitor (220 nF on the host's transmit pair); for the NVMe and E-key links it is INFERRED from the
CM5 datasheet's statement of the convention, "external AC coupling capacitors are required ... close to the driving
source ... PCIe and NVMe cards include these capacitors on board" (section 2.3, before 2.3.1), which puts the capacitor
of each direction at its own transmitter; no PCIe or M.2 specification is held in this tree. **They are corrected in
the committed netlist since `458b2873`** (Appendix A; the fabric map reads 202 of 202 rows OK on it,
`ARCHITECTURE.md` section 5.2), and every reference clock output pair is now also coupled and source-terminated. The
correction grows the pockets: slot 3's block gains 32 parts against B21, 18 of them to be seated beside the switch U301
(`FAILOVER-FABRIC.md` FAB-08). No board file carries the corrected netlist yet, and the fabric review's FAB-01 (every
switch's `TEST2` strap) to FAB-04 are still open in it, so a route of the B21 board is evidence of routability only.

The recommendation (section 6) is to finish the schematic (Appendix A is done; FAB-01 to FAB-04 are not), to run the
bounded region trial of section 7 because it is cheap and separates "layers" from "geometry", and to study the floor
plan on paper in parallel. **What decides the order.**
Decision 43 (`v2/ecad/tools/pcb_decisions.yaml`, ruled by the owner on 25 September 2026) authorises one eight-layer
regeneration and route of board B, and its text does not make that run wait for this trial. The execution plan
(`v2/docs/EXECUTION-PLAN.md`, the reviews table) puts board B feasibility inside Review C, and the integrating session's
working plan answers this trial before any whole-board route. So the order is the integrating session's to set and
record in `EXECUTION-PLAN.md`; this page does not set it. Whatever order runs, the whole-board run's outputs are
EXPERIMENTAL.

## 2. What was read

| Artefact | Identity | What it gives |
|---|---|---|
| B21 board, schematic, netlist | `v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_pcb` sha256 `2e64b5bf...` (unchanged at `eadbe571`); B21's `.kicad_sch` `eac5845f...` and `out/pcb-b-compute.net` `0e72edb5...` (generator sha `66e68fe66ab81617`), as committed at `82dd1e4d` | placement, copper per layer, nets, pin functions |
| the corrected netlist | `out/pcb-b-compute.net` on `main` since `458b2873`, sha256 `6048ee56c48a028b...` at `eadbe571`, 1,103 parts against B21's 931 | Appendix A's corrections; what a regenerated placement must seat |
| B21 pre-route board | `routed/pcb-b-compute-preroute.kicad_pcb` sha256 `62facf09...`, **tracked in git** since commit `8c691891` (18 September 2026) | the placement `place_audit` measured, the escapes, 2,218 pre-route vias |
| `routed/place_audit.verdict.json` | ts 2026-09-21T12:48Z, writer sha `6e2f9bf7fe10fb15`, rule PLC-001 | 13 FAIL lines, 75 fine-pitch parts (taken without board B's declared `ESCAPE_SKIP`, section 3.1) |
| `routed/region_room.verdict.json` | ts 2026-09-17T15:06Z | INCONCLUSIVE: "no region table"; the room readings in b.json come from runs not in this tree |
| `routed/hardset-pre-route-drc.verdict.json` | ts 2026-09-16T04:51Z | pre-route hard 0 of 15 types, DRC unconnected list at its 499 cap |
| `tools/boards/b.json` `_*_why` fields | at `82dd1e4d` | B21/B22/B23 route history, margin and resize arms, room map (RECORDED) |
| `tools/pcb_decisions.yaml` decision 43 | ruled by the owner 2026-09-25 | the layer option authorised as one eight-layer regeneration and route |
| JLCPCB pages and order form | fetched 25 September 2026 (section 4); transcribed in `v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md` | stackups offered, via capabilities |
| Raspberry Pi CM5 IO board design | `v2/vendor/cm5/cm5io-kicad.zip` | how Raspberry Pi escapes one CM5 |
| Preparation smoke test of the trial | run on the rented box on 25 September 2026 22:03 UTC, no router started (section 7.6) | the arms agree, S3's size and its pass-0 count |

## 3. Diagnosis

### 3.1 Which parts' escapes fail

`place_audit` on B21 (VERIFIED, `routed/place_audit.verdict.json`), after the escape pass, pads without an escape:

| Part | What it is | Package, pitch | Pads without escape |
|---|---|---|---|
| U101 | slot 1 PCIe switch PI7C9X2G404SL | LQFP-128 14 x 14, 0.4 mm | 38 of 99 |
| U301 | slot 3 PCIe switch | LQFP-128, 0.4 mm | 34 of 99 |
| U102 | slot 1 USB 3 hub TUSB8041 | QFN-64 9 x 9, 0.5 mm | 21 of 41 |
| U202 | slot 2 hub | QFN-64, 0.5 mm | 17 of 35 |
| U302 | slot 3 hub | QFN-64, 0.5 mm | 14 of 35 |
| U209 | slot 2 SuperSpeed mux TMUXHS4212 | VQFN-20 2.5 x 4.5, 0.5 mm | 15 of 21 |
| U3, U4 | HDMI switches TS3DV642 | WQFN-42 3.5 x 9, 0.5 mm | 27 of 41 each (see the note below) |
| J_HDMI | HDMI receptacle | 0.5 mm row | 12 of 18 (see the note below) |
| U7 | PCA9555 expander | TSSOP-24, 0.65 mm | 12 of 24 |
| U19, U20 | 74LVC08 EMCON gates | TSSOP-14, 0.65 mm | 5 of 14, 3 of 11 |

Plus three plane pads with no path to their plane (U301.2 GND, U201.120 GND, U40.1 +5V_DEV). Board-wide on 17
September, 560 fine-pitch pads had no escape (RECORDED, `b.json _escape_gap_why`). The predictor has read about ten
collisions of 75 fine-pitch parts under every lever tried: the sixteen-rectangle resize (10 to 11), the fine-pitch
margin (10 to 12), three route methods and forty hours of router (RECORDED, decision 43 evidence).

**Note on U3, U4 and J_HDMI (VERIFIED, found in review).** Board B declares them as parts the escape pass leaves to the
router (`boards/b.json` `escape_env`: `ESCAPE_SKIP` U3, U4, J_HDMI), and the placement chain runs `place_audit` with
that environment (`tools/full.sh:27`). The committed PLC-001 verdict was taken by `gate_sweep.sh`'s pre-route placement-predictor step without it, so it
counts those three parts as three of its 13 collisions. Run with the declared environment on the same pre-route board,
`place_audit` reads 10 (the smoke test of section 7.6: 9 parts and the plane-pad line). The verdict stays FAIL either
way; the count the record should quote is 10, which is the "about ten" of decision 43. The fix is one argument in
`gate_sweep.sh` (the integrator's); it is still owed at `eadbe571`, whose `gate_sweep.sh` passes the board's `gen_env`
(line 78) but not its `escape_env` to the pre-route `place_audit` step (line 201).

Two readings of that list, both VERIFIED from the tools' own text:

- **The predictor measures the escape pass, not physics.** `place_audit.py`'s docstring: "No fitted constant: the escape
  pass itself is the measurement." `escape.py` lays, for every fine-pitch pad, a short surface track to a through via
  outside the pad (0.40/0.20 mm on 0.4 mm rows and long 0.5 mm rows, 0.45/0.25 mm on other rows up to 0.7 mm pitch),
  staggered at fixed depths (`escape.py:189-213`). It has no via-in-pad mode for signal pads (`prefanout.py` has an
  in-pad fallback for plane-net pads only). So a FAIL means "this pattern does not fit here", not "no legal escape
  exists".
- **The TSSOP failures are a crowding signal.** A 0.65 mm TSSOP escapes on any board that leaves it room; U7, U19 and U20
  failing says the parts around them are too close, which is placement.

### 3.2 On which layers

- **Escapes are surface stubs to through vias**, so the escape pattern, and therefore PLC-001, does not depend on the
  layer count. JLCPCB makes through holes only ("Blind/Buried Vias: Not supported", section 4), so every escape via on
  board B occupies all six layers, and it would occupy all eight on an eight-layer board. The pre-route board carries
  2,218 vias (VERIFIED count).
- **Stackup and layer use (VERIFIED).** JLC06161H-3313: F.Cu, 0.0994 prepreg, In1, 0.55 core, In2, 0.1088 prepreg, In3,
  0.55 core, In4, 0.0994 prepreg, B.Cu (`v2/vendor/fabricator/jlcpcb-impedance-stackups-2026-09-16.md`). Board B uses
  In1 as a GND plane and In4 as four split 5 V planes (+5V_DEV, +5V_S1, S2, S3; zone list of the B21 board), so the
  routing layers are F.Cu, In2, In3 and B.Cu. Copper on the routed B21 board, in segments: F.Cu 5,836, In2 4,087, B.Cu
  4,059, In3 3,379.
- **Only the outer two are controlled-impedance layers for pairs.** In2 and In3 are 0.109 mm apart (broadside to each
  other) and 0.55 mm from their planes; a 0.127/0.152 pair there solves to 140.5 ohm against 100, and making 100 would
  take about 0.40 mm tracks (RECORDED, `b.json _pair_inner_layer_why`, atlc field solver). The pair pre-router lays only
  on F.Cu and B.Cu and laid 31 of 68 pairs on B21 (34 to 36 on B22 and B23 pre-routes); the rest went where the router
  put them, 1,677 mm of pair copper on the inner layers (RECORDED). B.Cu pairs sit over four split power planes, so any
  B.Cu pair that crosses between slot rails crosses a reference-plane split (INFERRED from the zone list).
- **Pair failures die at the same places as the escape failures.** On B21 the pair pass's failures concentrate at U32B
  and U31B (12 each), U301 (12), U3, U4 and U1 (10 each), U30B and U209 (6 each), U302, U109 and U102 (4 each)
  (RECORDED, `b.json _floor_plan_targets_why`). Four parts are in both lists (U301, U302, U209, U102).

### 3.3 Why: the floor plan's topology

Placement read from the B21 board (VERIFIED, footprint origins, board x -15 to 315, y 10 to 210):

| What | Where |
|---|---|
| CM5 receptacle pairs (A, B halves) | slot 1 x 60.5 / 94.5, slot 2 x 130.5 / 164.5, slot 3 x 200.5 / 234.5, all at y 52.5 |
| M.2 row (NVMe M-key, card E-key/B-key) | y 87 (J_M2N1 x 65, J_M2C1 x 93, J_M2C2 x 130, J_M2N3 x 198, J_M2C3 x 229; J_M2N2 at x 123, y 195) |
| Slot fabric: PCIe switch, USB hub, muxes | slot 1 U101 (65, 141), U102 (84, 137), U109/U110 (58 to 66, 156); slot 2 U201 (123, 151), U202 (141, 147), U209 (153, 145); slot 3 U301 (194, 141), U302 (212, 137), U309/U310 (187 to 194, 156 to 157) |
| Ethernet switch KSZ9897R U1 and RJ45 J_ETH | west edge, x -1 and x 1.6 |
| HDMI switches U3, U4 and J_HDMI | east, x 251 to 267 at y 21; J_HDMI at (254.5, 201) |

So every slot's PCIe and both USB 3 ports leave the receptacle's high-speed half (the B connector, pins 101 to 200),
cross the M.2 row, and reach the fabric about 85 to 90 mm south; the switch's downstream PCIe then runs back north to the
M.2 sockets. The Ethernet pairs of all three slots run west to U1, the HDMI pairs east to U3/U4, and the failover ring's
slot 1 to bank 3 edge crosses slot 2's whole column (a three-slot ring always has one such edge, Appendix A.4).

A net-crossing screen on the B21 placement (INFERRED method: a net crosses a line if its footprints lie on both sides;
footprint origins stand for pads; a one-off read-only script, not a repo tool):

| Cut | Signal nets crossing | High-speed nets crossing (families) |
|---|---|---|
| y = 110 (between the M.2 row and the fabric row) | 334 | 170: HOST 36, PCIE 35, ETH 24, SWP 24, CARD 21, NVME 18, HDMIO 12 |
| x = 112.5 (slot 1 / slot 2) | 127 | 46: SWP 16, HDMI 14, HOST 12, LIME 4 |
| x = 182.5 (slot 2 / slot 3) | 123 | 50: HDMI 26, HOST 12, SWP 8, LIME 4 |
| x = 245 (east of slot 3) | 101 | 42: HDMI 38, LIME 4 |

The family counts include control nets of each family (the PCIE count holds reset, wake and clock-request lines), so
they overstate the pairs; the screen ranks buses, it does not size channels. The y = 110 line is 330 mm long on four
routing layers; about 85 pairs and 164 single nets would need roughly 120 mm of one layer at this board's class widths
(INFERRED arithmetic), so the global cut is not saturated. **The congestion is local**: it is where those buses start
and end, at the receptacles' high-speed halves and in the three switch pockets, which is exactly where both failure
lists sit.

The pockets themselves have no room: `S1_SWIC` 0.0 mm in all four directions (a fixed hole west, S1_SWE east, S1_RAIL
south, the M.2 socket north), `S2_SWIC` 0.0 in all four, `S3_SWIC` 1.0 west and 0.0 elsewhere; the room on the board is
elsewhere (WIFISW 38.5 mm north, IOCA 19.0 north, S1_RAILB 19.0 west, S2_RAILB 16.0 east) (RECORDED, `region_room` on
B23's placement, `b.json _b24_redistribution_room`; the verdict file in this tree is INCONCLUSIVE because its region
table is absent, so this cannot be re-read here).

### 3.4 Classification

| Cause | Evidence | Kind |
|---|---|---|
| Partition runs cut by their caps; one region lost to an importer defect (fixed); per-pass cost grows with every locked group (7.4 min for DEVW, over 4 h for S3's first pass) | RECORDED `b.json _b22_partition_why`, `_b23_pass_rate_why` | **tool / method**: B22 and B23 did not measure the partition method, they measured its caps and ordering |
| B21 routed 40 h with no supervisor and stopped at 416 unrouted, passes rising from 2.5 h to 4 h | RECORDED `b.json _phase_why`, `_b21_route_why` | **tool / method**: a plateau of one router is not a proof of infeasibility |
| One escape pattern, through vias only, fixed via sizes, no via-in-pad | VERIFIED `escape.py:189-213`; no in-pad mode for signal pads | **tool**: PLC-001 measures this pattern |
| Through holes only at the fabricator | VERIFIED JLCPCB capabilities page (section 4) | **physical constraint of the chosen fabricator** |
| Two of four routing layers usable for controlled-impedance pairs | VERIFIED stack and zones; RECORDED 140.5 ohm solve | **physical, fixable by stackup use** (section 5, options A1 and A2) |
| 0.4 mm receptacle rows: tip vias pass a 0.127 track at 0.137 mm spare | VERIFIED `escape.py:191-195` comment and rules | **physical, tight but proven**: Raspberry Pi escapes one CM5 this way (below) |
| Fabric 85 to 90 mm from its receptacle, beyond the M.2 row; buses to far-edge hubs; pockets at 0.0 mm | VERIFIED placement; RECORDED room map | **placement and partition** |
| PCIe and SuperSpeed TX/RX crossed; 18 capacitors missing in the pockets; 5G socket keyed M | VERIFIED on B21's netlist, datasheets and maker drawing, Appendix A | **schematic defect**, corrected in the netlist since `458b2873`; the corrected parts are not seated on any board (FAB-08), and FAB-01 to FAB-04 are open |

**What is not shown: that board B cannot be routed.** Raspberry Pi's own CM5 IO board escapes one module's HDMI0, HDMI1,
PCIe and both USB 3 ports on four layers whose two inner layers are typed power, with 705 vias of 0.45/0.20 mm and mostly
0.127 to 0.147 mm tracks on the outer layers, and only 298 track segments on the inner layers (In1 115, In2 183)
(VERIFIED, `CM5IO.kicad_pcb` layer table, via and segment census; the first version of this page said 256, which a
review census refuted). So the escape of one receptacle is feasible on two signal layers; what is unproven is three
modules plus their fabric at board B's density and floor plan. This also narrows decision 43's premise that "three CM5
receptacles at 0.4 mm pitch measurably need two inner signal layers": the measurement behind it (93 opens with a
board-wide In1 keep-out) is a statement about board B's routing, not about the receptacle escape.

## 4. Fabricator facts (JLCPCB, read 25 September 2026)

Pages and the order form are not controlled documents and can change; every reading below carries its date. The raw
responses and rendered views of the order form were captured by this review's fabricator re-read (25 September 2026,
21:24 to 21:38 UTC, anonymous public requests only). **The transcription is filed** as
`v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md` (on `main` since `d468613e`), beside the 16 September ones; the raw
captures stay with the session record, and that file gives each one's sha256.

| Source | What it says |
|---|---|
| https://jlcpcb.com/impedance, server-rendered default state (1.6 mm, 1 oz outer, 0.5 oz inner), read 20:40 UTC | Impedance stackups for **four layers** (17 distinct JLC04161H codes) and **six layers** (15 distinct JLC06161H codes, JLC06161H-3313 among them). The page component has only a four-layer and a six-layer form, so **the page has no eight-layer section**. Its selectors (0.8 to 2.0 mm; outer 1 or 2 oz; inner 0.5, 1 or 2 oz) serve further rows; at 1.6 mm with 2 oz outer it lists four four-layer stackups, JLC04162H-7628 the default. The code counts of the first version of this page describe the default view only. |
| https://cart.jlcpcb.com/quote, Layers 8, "Specify Stackup: Yes", 1.6 mm, 1 oz outer, 0.5 oz inner | **13 enabled eight-layer impedance stackups with full layer tables**: 12 codes plus a "No requirement" default that is JLC08161H-2116, 1.6 mm +-10 percent (JLC's impedance calculator names the same template "general free"; the order form's label is "No requirement"). JLC08161H-2116 is Cu 0.035 / 2116 prepreg 0.1164 / core 0.3 / 2 x 1080 prepreg 0.0764 / core 0.3 / 2 x 1080 / core 0.3 / 2116 0.1164 / Cu 0.035, inner copper 0.0152. Four of the 13 carry a fixed fee (JLC08161H-7628 and -1080 at 330, -1080A and -2116A at 550; the unit is not stated): money, so it goes to the owner with the quote. |
| JLCPCB's impedance calculator for the same codes | Per-layer dielectric constants 4.16 (2116), 3.91 (1080), 4.41 (0.3 mm core), against the single core value 4.6 on the impedance page. The two JLC sources disagree; the effect on stripline impedance is estimated at about 2 percent (INFERRED estimate, not an `impedance_2d.py` run), inside the +-10 percent tolerance. |
| https://jlcpcb.com/capabilities/pcb-capabilities, read 20:40 UTC | "Layer count: 1-32 Layers". "Blind/Buried Vias: Not supported. Currently we don't support Blind/Buried Vias, only make through holes." "Min. Via hole size/diameter 0.15mm / 0.25mm". Track and spacing at 1 oz: "Multilayer: 0.09 / 0.09 mm (3.5 / 3.5 mil). 3 mil is acceptable in BGA fan-outs." Via-in-pad: "Epoxy Filled & Capped" or "Copper paste Filled&Capped", "This process is the default for 6-layer and above multilayer boards", "Compatible with via diameters from 0.15 to 0.55 mm". Impedance "standard tolerance is ±10%", "±5% is available upon special request". Maximum size "FR4(6-layer and above): 656 × 586 mm". Inner copper "0.5 oz / 1 oz / 2 oz", 0.5 oz by default. Backdrill supported for 4 to 32 layers. |

So a manufacturer-supported eight-layer stackup exists, and it is recorded: `stackup_write.py`'s `STACKS` carries
JLC08161H-2116 since `d468613e`, equal layer by layer to the filed transcription, with the calculator's per-layer
dielectric constants (the four-layer 2 oz row JLC04162H-7628 for board P came in the same commit). A `STACKS` row is a
reserved-floor change (`v2/ecad/tools/reserved.json`, class "layer count and stackup"), made under decision 43's
authority. The first version of this page said the fabricator publishes no eight-layer impedance stackup; that was true
of the impedance page only.

The row as recorded at `eadbe571` (`stackup_write.py:53-69`, VERIFIED re-read; the fabricator's two 1080 plies between
L3 and L4 and between L5 and L6 are written as one 0.1528 mm prepreg at their common Dk, which is the same distance and
constant `impedance_check.geometry()` takes):

| Copper | Dielectric below it | Thickness (mm) | Dk |
|---|---|---|---|
| F.Cu (0.035) | prepreg 2116 | 0.1164 | 4.16 |
| In1.Cu (0.0152) | core | 0.3 | 4.41 |
| In2.Cu (0.0152) | prepreg 1080 x 2 | 0.1528 | 3.91 |
| In3.Cu (0.0152) | core | 0.3 | 4.41 |
| In4.Cu (0.0152) | prepreg 1080 x 2 | 0.1528 | 3.91 |
| In5.Cu (0.0152) | core | 0.3 | 4.41 |
| In6.Cu (0.0152) | prepreg 2116 | 0.1164 | 4.16 |
| B.Cu (0.035) | | | |

Which of its six inner and outer layers an eight-layer board B would spend on planes, and the pair widths each routing
layer then needs, are not chosen yet: they come from an `impedance_2d.py` solve on this row, owed with decision 43's
whole-board run (TBD). The trial of section 7 does not use the row (section 7.2).

Two cautions remain. The capabilities page's FAQ names "blind/buried vias, HDI (laser vias)" among "advanced options";
the capability table says not supported, and the table is taken as binding until JLCPCB says otherwise. The via-in-pad
price on a six- or eight-layer order is not stated on the page (TBD, an owner money item if it is not free).

## 5. Legal alternatives compared

No option below relaxes an electrical rule or extends route time.

| # | Option | What it changes | What it cannot change | Evidence and gaps | Who decides |
|---|---|---|---|---|---|
| A1 | **Eight layers** (decision 43) | Two more layers of routing channel; room for a plane beside every inner signal layer | The escape pattern and PLC-001's collisions (through vias block every layer); the floor plan | JLCPCB offers 13 eight-layer impedance stackups on its order form (section 4), default JLC08161H-2116, which `STACKS` records since `d468613e` (the layer table in section 4), so an eight-layer board B can be judged on STK-001 and IMP-001; the layer assignment and pair widths are TBD from a solve on that row; the core Dk question is open and not blocking; price TBD | Owner ruled the measurement (decision 43); the price goes to the owner before any order |
| A2 | **Six layers, re-assigned**: In3 becomes a GND plane (S / G / S / G / P / S) | In2 gets a plane 0.109 mm away (In3), like the outer layers get theirs at 0.0994 mm, so three routing layers become controlled-impedance layers instead of two | Loses In3 as a routing layer (3,379 segments on B21); does not touch escapes | Same published stack JLC06161H-3313, so no new fabricator record; In2's impedance at 0.109 mm to one plane and 0.55 mm to the other needs a solve with `impedance_2d.py` (TBD) | Session (engineering), after the solve |
| A3 | **Via-in-pad escapes** (filled and capped, the fabricator's default on 6 layers and up, vias 0.15 to 0.55 mm) | The escape pattern itself: a fine-pitch pad takes its via in the pad and needs no stub, which frees the band around LQFP-128, QFN-64 and TSSOP parts | Nothing about the floor plan | Needs a new mode in `escape.py` (tool work, not done here) and a fabricator DFM answer on in-pad vias under 0.2 x 0.7 mm connector pads and 0.25 mm QFP pads; price on a six-layer order TBD | Session for the tool; the price question to the owner only if it costs |
| A4 | **Floor plan**: each slot's switch, hub and muxes beside its receptacle's B half, north of the M.2 row; M.2 sockets south of the fabric; the KSZ9897R with its magnetics and J_ETH (a patch-lead jack, `ASSEMBLY.md` section 4, the Ethernet row) moved toward the board centre; U3/U4 and J_HDMI (a cable jack, the monitor HDMI row) toward the centre | Shortens the 85 to 90 mm receptacle-to-fabric runs and the bus runs of section 3.3; moves the fabric out of the boxed pockets | The failover ring's long edge (inherent, Appendix A.4) | Owner ruling 13 released board B's rectangles; the RM520N-GL allows up to 200 mm of PCIe trace (`pcb_interfaces.yaml` PCIE_M2_MODULE), so moving the sockets away from the switch is within the module's own limit; the case positions of the RJ45 and HDMI jacks are W4's to confirm | Session (engineering), W4 for the mechanical side |
| A5 | **Partition method**: more, smaller groups with cheap passes, fabric regions first | Makes a partition run measure the method rather than its caps | The placement | RECORDED pass costs (`_b23_pass_rate_why`) | Session |
| A6 | **Larger outline within the Peli 1450**: B is 330 x 200 mm; the frame window it lifts through is 349.65 x 233.83 (`ASSEMBLY.md` section 7; `panel1450.py` WINDOW) | The lift-out keeps 9.83 mm per side in x nominal and 8.25 at the worst of Peli's figures, and 16.91 in y nominal (`CASE-MARGINS.md` M7), so at a 1.0 mm minimum about 14 mm more in x at the worst (INFERRED arithmetic); any growth also meets the setting legs (M21f keeps 4.52 mm to B's corner at the worst) and the east jumpers' lane beside B's edge (M17d, M17x) | Nothing by itself: the pockets are boxed by other regions, so area helps only with A4 | `CASE-MARGINS.md` 3.2 gives the case side; growth in y and at the east edge is bounded by rows that are OPEN | the session; the owner if the case changes |
| A7 | **Pin mapping**: the CM5 datasheet allows USB 3 P/N swaps (section 2.4: "You may swap the positive (P) and negative (N) signals for USB 3.0 pairs"), and the switch supports PCIe lane polarity inversion (it has an `RXPOLINV_DIS` strap, pin 24); per slot, which module port is home and which is failover could be chosen by pin position | Removes pair crossings at the receptacle and the mux | The ring's topology | Pure schematic change; must follow the F-DAT-01 fix | Session |
| A8 | **Feature reductions**: 5G to USB 3 (IOHA open ruling 4, deletes one PCIe device path on slot 2); drop the second WiFi card; drop the IOHA fabric (3 x TMUXHS4212 and 3 x TS3USB221A in the front pockets, plus the three supervisors and the voters, whose control plane alone is about 2,400 mm2 of the underside by IOHA section 11); drop the per-slot NVMe | Parts and buses in exactly the congested pockets | | Decision 43 did not take "fewer parts in that fabric" now | Excluded by the owner's D-01 of 25 September 2026 (full design: every ruled function stays designed and fitted where copper exists), except 5G to USB 3, which moves a path rather than removing a function and is IOHA's open ruling 4 |

## 6. Recommendation (engineering, the session's; nothing here is applied)

1. **Fix the schematic first.** Appendix A.1 to A.3 and A.5 are done in the netlist since `458b2873` (the socket-side
   PCIe assignment on all six downstream links and the LimeSDR SuperSpeed pins, the downstream AC coupling and the
   reference clock coupling and termination, the key-B socket for slot 2 and SIM 2 on the module's pins, and a direction
   check in `check_pcb_b.py`). Still owed before a board B route is evidence of a working circuit: the key-B land's two
   locating holes (`gen_sch_b.py:639-640`), and the fabric review's FAB-01 (`TEST2` pulled low on every switch), FAB-02
   (back-power into unpowered modules), FAB-03 (the break-before-make order) and FAB-04 (the 23 safe-low pull-downs at
   10 k), all board B's writer's (`FAILOVER-FABRIC.md` section 9).
2. **Run the bounded trial of section 7 before the whole-board run**, because it is cheap (about 3.5 box-hours at most)
   and its reading tells the whole-board run where to look (which routing layers carry the region, and whether the
   pocket or the buses between regions bind). Decision 43's own text does not make the whole-board run wait for it; the
   execution plan's Review C carries board B feasibility, and the order is the integrating session's to set and record
   in `v2/docs/EXECUTION-PLAN.md` (section 1 of this page).
3. **In parallel, a paper floor-plan study of A4 with A2 and A7** (no compute): the cut screen of section 3.3 repeated on
   a proposed rectangle set, reporting the high-speed nets per cut before and after.
4. **The whole-board eight-layer experiment that decision 43 authorises runs within that authorisation, and its
   authorisation does not depend on what the trial reads** (decision 43 in `v2/ecad/tools/pcb_decisions.yaml`; the
   owner's condition 7 in `v2/docs/EXECUTION-PLAN.md`), with its own budget, a plateau rule it can enforce (the watcher
   of section 7 is reusable for it) and a journal. Its outputs are labelled EXPERIMENTAL in the journal, the run
   directory and every report; they are never adopted as board B's phase, never promoted and never counted as a layout candidate. If it
   stalls, the work goes back to the diagnosed constraints and the alternatives of section 5; route time is never
   extended and no electrical rule is relaxed. Decision 43's own text returns it to the owner if the eight-layer board
   does not route either; since the owner's standing rule of 26 September 2026, a choice that comes back that way is
   taken by the session on the evidence and recorded, and only a price goes to the owner with a quote (D-09). A
   region-trial reading on its own does not reopen it.
5. **A manufacturer-supported eight-layer stackup row** is recorded: `STACKS` carries JLC08161H-2116 since `d468613e`,
   from the filed transcription of section 4, under decision 43. The eight-layer price goes to the owner before any
   order.
6. **Ask JLCPCB** (W6's inquiry, reduced): the via-in-pad price on six and eight layers; whether in-pad vias are accepted
   under 0.2 mm wide connector pads; and, not blocking, which dielectric constants JLCPCB designs to when it controls
   impedance on the eight-layer code named on the order (the calculator's per-layer values or the page's core 4.6), and
   whether it supplies the coupon result. The session writes the inquiry text; the owner's ordering session sends it,
   because the session never logs into JLCPCB or writes to a supplier as the owner. Any price in the answer goes to the
   owner with a quote (D-09).

## 7. The bounded escape trial Q-B-ESC-1 (specification, box-ready, not run)

### 7.1 Question

In board B's hardest region (slot 3: the PCIe switch U301, the hub U302, the muxes U309 and U310, the receptacle pair
U32A/U32B and the sockets J_M2N3 and J_M2C3), is the failure to break out a **layer-capacity** limit that two more
routing layers remove, or a **geometric** limit of the escape field and the placement that layer count does not change?

Slot 3 is chosen because U301 carries 34 unescaped pads and U302 14, U32B is where 12 pair failures die, and S3 was the
group that could not complete one pass in four hours on B23 (RECORDED).

### 7.2 Inputs and arms

- **Scripts:** `v2/ecad/tools/routeflow/experiments/b_esc1/`: `run.sh` (the driver), `make_arm8.py`, `count_open.py`,
  `plateau_watch.py`, `judge.py`. Each states its contract in its header.
- **Repo:** a clean clone at the commit the driver records (`git rev-parse HEAD` and the tools tree sha go in the journal).
  At `eadbe571` the input board below is tracked with the same sha, and no tool the driver runs changed since the smoke
  test's `82dd1e4d` (section 7.6).
- **Input board:** `v2/ecad/pcb-b-compute-b19/routed/pcb-b-compute-preroute.kicad_pcb`, sha256
  `62facf0952ff4c01cb0a47698ec6870b5fae0f0d9b836bf95db6c3c7bae166dd`, tracked in git (the driver takes it with
  `git show HEAD:...` and stops if the sha differs). Beside it: `pcb-b-compute.kicad_pro` (sha256 `c2c6e771...`),
  `fp-lib-table`, and `v2/ecad/meshsat.pretty/` (linked where the library table expects it).
- **Netlist:** B21's, the one the input board carries, with the defects of Appendix A. The corrected netlist on `main`
  is not on any placed board, so the trial cannot route it (limit 1 below).
- **Box:** KiCad 9 (`kicad-cli`, `pcbnew` importable), Java, the project's Freerouting 1.9.0 build (it writes a session
  after every pass; `fr_jar.sh` refuses the stock jar), `xvfb-run`. Two cores do the routing; memory is not a constraint.
- **A6 (control):** the input board as is. Routing layers F.Cu, In2, In3, B.Cu.
- **A8 (EXPERIMENTAL, generous):** the same board with its copper layer count set to 8 in the trial tree only. KiCad 9
  keeps every item on its layer and enables In5 and In6 empty; In1 (GND) and In4 (the 5 V planes) keep their zones, so
  the routing layers are F.Cu, In2, In3, In5, In6, B.Cu. A real eight-layer board B would spend at least one added layer
  on a plane (section 4 lists the stackups), so A8 has more routing than any real eight-layer B: a reading that layers do
  not help is strong evidence, a reading that they help is only permission to look further. **A8 does not use the
  recorded JLC08161H-2116 row** (section 4): `SetCopperLayerCount(8)` adds two empty copper layers and the trial reads
  connectivity only, so neither the row's dielectric distances nor any layer assignment enter the reading, and A8's
  layer order is not a stackup proposal. The row is what decision 43's whole-board run and its STK-001 and IMP-001
  readings are judged against. No `STACKS` row is added, no generator is touched, and impedance is not judged.
- **One job per arm.** Freerouting is deterministic ("N attempts with identical parameters are one attempt run N times",
  `v2/ecad/tools/tests/test_driver_hygiene.py:846`, measured 5 September 2026), and `route_part.sh` runs it single-threaded. The first
  version of this page ran two identical repeats per arm and read the scatter between them; that scatter is always zero,
  so the repeats and the scatter test are gone. A real perturbation the router honours exists (via and rip-up costs
  through `fr_rules.py`, as `route_parallel.sh` uses them), but `route_part.sh` takes no rules file today; adding one is a
  tool change outside this trial, and the outcome table below does not rely on it.

### 7.3 Command

From `v2/ecad` of the clean clone on the box, with the box's hourly rate:

```bash
BOX_USD_PER_H=<rate> bash tools/routeflow/experiments/b_esc1/run.sh
```

The driver runs, in order (every tool that writes a verdict points at the trial directory through `VERDICT_DIR`,
because a gate run from `v2/ecad` by hand writes that tree's own evidence; `T=out/routeflow/b-esc1`, gitignored, never
reused):

1. Provenance into `$T/JOURNAL.md`: commit, tools tree, jar sha, Java, KiCad, host, caps, the computed deadline.
2. `git show HEAD:v2/ecad/pcb-b-compute-b19/routed/pcb-b-compute-preroute.kicad_pcb > $T/a6/pcb-b-compute.kicad_pcb`,
   the sha check, and the project file and library table beside each arm.
3. `python3 tools/routeflow/experiments/b_esc1/make_arm8.py $T/a6/pcb-b-compute.kicad_pcb $T/a8/pcb-b-compute.kicad_pcb $T/arm8.json`:
   `SetCopperLayerCount(8)`, then the saved file is read back and compared with A6 layer by layer (tracks, zones and zone
   nets, vias, pads, footprints, nets; In5 and In6 empty).
4. `ESCAPE_SKIP=U3,U4,J_HDMI VERDICT_DIR=$T/<arm>/pa python3 tools/place_audit.py $T/<arm>/pcb-b-compute.kicad_pcb`
   on both arms, with board B's declared escape environment read from `tools/boards/b.json`.
5. `bash tools/dsn_export.sh $T/<arm>/pcb-b-compute.kicad_pcb $T/<arm>/raw.dsn "GND" "In1.Cu In4.Cu"` and
   `python3 tools/dsn_partition.py $T/<arm>/pcb-b-compute.kicad_pcb $T/<arm>/raw.dsn $T/<arm>/part.dsn $T/<arm>/part.json`
   (board B's routeflow settings; the default regions put every slot-3 part in group S3).
6. Integrity (`$T/integrity.json`): the two arms' `place_audit` verdict, counts and evidence equal, their partition
   groups equal, and `make_arm8.py` agreeing; any difference prints `STOP-ARMS-DIFFER` and the driver stops before a
   router starts.
7. Pass 0: `python3 tools/routeflow/experiments/b_esc1/count_open.py $T/<arm>/pcb-b-compute.kicad_pcb $T/<arm>/part.json S3 --json $T/<arm>/base.json`.
8. Both jobs at once, each under its own watcher:
   `CONFINE=1 CONFINE_LAYERS="<the arm's routing layers>" bash tools/route_part.sh $T/<arm>/run $T/<arm>/part.dsn S3 20 9000 $T/<arm>/part.json`
   and `python3 tools/routeflow/experiments/b_esc1/plateau_watch.py --job-pid <its pid> --ses $T/<arm>/run/S3/route.ses --out $T/<arm>/watch --count-cmd "<count_open.py on the arm's board with --ses {ses}>" --plateau 3 --first-pass-max 5400 --deadline <route deadline> --stop-file $T/STOP`.
9. The final reading of each arm, from its last observed session:
   `python3 tools/ses_import_lock.py $T/<arm>/pcb-b-compute.kicad_pcb <last session> $T/<arm>/part.json S3 $T/<arm>/s3.kicad_pcb`;
   the project file copied to `s3.kicad_pro` (`drc.sh` refuses a board without its own project file, which the first
   version of this page did not provide); `VERDICT_DIR=$T/<arm>/v bash tools/drc.sh $T/<arm>/s3.kicad_pcb $T/<arm>/s3-drc.json`;
   `VERDICT_DIR=$T/<arm>/v python3 tools/hardset.py measure $T/<arm>/s3-drc.json post --label ... --board $T/<arm>/s3.kicad_pcb --counts $T/<arm>/s3-counts.txt`;
   and `count_open.py` on `s3.kicad_pcb` into `final.json`.
10. `python3 tools/routeflow/experiments/b_esc1/judge.py $T` writes `outcome.json` by the table of section 7.5, and the
    driver lists the files to fetch.

**The decisive number** is the S3 open count: the sum, over the 146 nets of group S3, of the ratsnest edges KiCad's own
connectivity reports for each net alone (one missing connection between two copper clusters of a net is one). It comes
from `pcbnew` connectivity, never from the DRC report, whose unconnected list is capped on this board (RECORDED). How it
is read per net, given what the KiCad 9 Python binding does and does not expose, is written in `count_open.py`'s header.
Beside it: the pads of U301, U302, U309, U310 and U32B left outside their net's main cluster (the residue), the region's
copper per layer, and the via count.

### 7.4 Caps and stop rule, each one enforced by a named mechanism

| Cap | Value | Enforced by |
|---|---|---|
| Passes per job | 20 | `route_part.sh` (`-mp`) |
| Wall time per job | 9,000 s (150 min) | `route_part.sh`'s own `timeout` |
| Plateau | three consecutive observed per-pass sessions with no new minimum of the S3 open count | `plateau_watch.py` kills the job's process tree |
| First pass | no session within 90 min | `plateau_watch.py` kills that job; if it is A6, the driver writes `$T/STOP` and the A8 job is killed too (the tool cannot answer at this cap; the cap is never extended) |
| Whole trial | the smaller of 6 box-hours and 10 USD at `BOX_USD_PER_H`, counted from the driver's start, less 45 min kept for the final readings | the driver computes the route deadline and refuses to start without the rate; `plateau_watch.py` kills at the deadline |
| Arms differ | any integrity difference | the driver stops before a router starts |

How the plateau is observed: our Freerouting build rewrites one session file after every pass, through a temporary file
and an atomic rename (`tools/freerouting/README.md`). The first version of this page asked for per-pass counts from
commands that would only have seen the last pass. `plateau_watch.py` copies every new session the moment it appears,
reads it with `count_open.py` (an import without a zone fill, about 20 s on this board), and records `passes.csv`. A
pass that ends while the previous one is being read is overwritten unseen, so the plateau is counted over observed
sessions, and the file says how many there were. The watcher kills only the process it was given and that process's
descendants, found through `/proc` parent links (GNU `timeout` puts the router in a process group of its own, so killing
the driver's group would not reach it); no name pattern is used.

Expected spend (INFERRED): the two jobs end at the latest after 150 minutes, so the whole trial is about 3.5 box-hours
at most, about 4 USD at 1.2 USD an hour for a CPU box. On a dearer box the credit cap binds sooner, by the formula
above. After the driver ends: fetch the files it lists one by one, check them, destroy the box, and read the instance
list to confirm zero running. That is the operator's act; the driver cannot destroy the box it runs on, and the API key
never goes on the box.

### 7.5 What each outcome means

An arm **closes** when its S3 open count is 0 and its hard count is 0 (the fifteen types of `tools/hardset.py`). An arm
is **settled** when it closed, stopped on the plateau, or ended by itself with its last reading not a new minimum; an arm
cut by a cap while still falling is not settled, and its count is only an upper bound.

| Outcome | Condition | Meaning |
|---|---|---|
| REGION-CLOSES-ON-6 | A6 closes | The pocket routes on six layers in isolation, within the limits of section 7.7: board B's failure is between regions (the cross-board buses of section 3.3), a floor-plan and partition result rather than a layer result. |
| LAYERS-HELP | A8 closes; A6 does not and is settled | Layer count is a lever for this region's breakout. It informs how the whole-board eight-layer run is set up; it does not show that board B routes, gives no impedance-judgeable board, and authorises no layout. |
| LAYERS-PARTIAL | A6 settled; A8 does not close and leaves at most half of A6's count | Layers help but do not close; the residue's pads say what else binds, and are read before the whole-board run is configured. |
| LAYERS-NOT-THE-LEVER | Both settled; A8 leaves more than half of A6's count, with at least half of A8's residue pads also in A6's | The region's limit is the escape field and the placement, which supports the diagnosis and options A3 and A4 (the session's engineering). It does not reopen decision 43: the ruling's own text returns it if the eight-layer board does not route (section 6, item 4), and this reading would be reported with that result. |
| INCONCLUSIVE | Anything else: the arms differ, A6 has no reading inside 90 minutes, a count was still falling at its cap, the residue sits at different pads, or both arms reach 0 open while carrying hard DRC items | No conclusion; nothing is extended. |

"Still falling" is judged over the pass-0 count and every observed session, so a job that ends after one observed pass
below its pass-0 count is not settled. LAYERS-PARTIAL needs A6's count above 0. Both rules were added to `judge.py` at
integration (26 September 2026): the first version read one observed pass as settled, and read two arms at 0 open with
hard items as LAYERS-PARTIAL. The factor of one half is this page's convention, not a measured constant. A reading of any kind reduces one
uncertainty. It proves neither the whole board nor readiness for layout (owner condition 7).

### 7.6 Preparation smoke test (25 September 2026, 22:03 UTC; no router started)

To prove the commands, the driver ran on the rented box with `PREPARE_ONLY=1` (steps 1 to 7, stopping before any router
starts) in a private clone at `82dd1e4d`. VERIFIED from its journal and files, which are kept with the review's working
files and are not in this tree. **Provenance limit:** at `82dd1e4d` the trial scripts were not yet committed, and that
revision of `run.sh` (sha256 `fc26919c838f1445...`) did not write its own scripts' hashes into the journal, so the smoke
run is tied to the published scripts by content comparison only. The published `run.sh` adds exactly that: the journal
now records the sha256 of every script in the trial directory and whether `run.sh` is tracked at the recorded commit.
`count_open.py`, `make_arm8.py` and `plateau_watch.py` are byte for byte the versions the smoke run used;
`judge.py`, which the smoke run did not reach, was corrected at integration for two edge cases (section 7.5), and at
the fix-up of 26 September its INCONCLUSIVE reason was reworded to name an arm that ended by itself while still falling
as well as one cut by a cap (its outcomes are unchanged on the synthetic cases of every row of section 7.5).

- The input board's sha matched; `make_arm8.py` read the saved A8 back with F.Cu, In1 to In6 and B.Cu enabled and every
  A6 layer's tracks, zones, vias and pads unchanged (tracks F.Cu 2,606, In2 220, In3 135, B.Cu 1,244 in both arms).
- The integrity check passed: both arms read the same `place_audit` result (10 collisions of 75 fine-pitch parts with
  board B's `ESCAPE_SKIP`) and the same partition (S3 146 nets, S1 158, S2 157, DEVW 116, DEVE 84, GLOBAL 183).
- The pass-0 S3 open count is **290 on both arms**, 135 of the 146 nets not yet joined, with residue pads on U301 (36),
  U302 (8), U309 (5) and U32B (11). One count took about 20 s.
- The first attempt stopped on a wrong key for board B's `ESCAPE_SKIP` in the driver; it was fixed and the run repeated.
- **Still valid at `eadbe571` (re-read for this revision):** between `82dd1e4d` and `eadbe571` git shows no change to
  `place_audit.py`, `escape.py`, `prefanout.py`, `dsn_export.sh`, `dsn_partition.py`, `route_part.sh`,
  `ses_import_lock.py`, `drc.sh`, `hardset.py`, `verdict.py`, `fr_jar.sh`, the Freerouting build, `boards/b.json`, the
  board's project file and library table, or the input board; the only changes under the paths the driver touches are
  three new footprints in `meshsat.pretty` (the Eaton SCF9550 land, a WSON-6 and the RSM0032A, which the B21 board does
  not use; a board file embeds its own footprints) and `tools/routeflow/cloud/onstart.sh` (the box installs
  `pdftoppm`). So the smoke run's readings stand for the trial at `eadbe571`; the trial's own scripts are unchanged
  (`judge.py` sha256/16 `0d849b2577171e79`).
  The watcher's stop paths (plateau, first-pass timeout, trial stop, job ended) were exercised on the runner with a
  stand-in job that rewrites a session file and starts a grandchild in its own process group; every stop killed the
  whole tree and left nothing behind.

### 7.7 Limits of the reading, stated so that none is read as a result

1. **The trial routes B21's netlist, not the corrected one.** The corrected netlist on `main` since `458b2873` adds
   173 parts to board B and removes one (R240); in slot 3's block that is 32 parts against B21: 18 to be seated beside
   U301 (the AC coupling capacitors C353 to C356, C395, C396 and the twelve reference clock resistors R375 to R386, whose
   place the HCSL rule ties to the source), and 14 elsewhere in the block (U311, Q309 to Q311, R362 to R365, R373, R374,
   C397, TP301 to TP303), plus the pair swap at J_M2N3 and J_M2C3 (`FAILOVER-FABRIC.md` FAB-08, VERIFIED there by
   netlist difference). The pockets had 0.0 mm of room before them (section 3.3). The trial routes the easier circuit,
   so it is optimistic for the corrected design: a LAYERS-NOT-THE-LEVER reading is strong, a REGION-CLOSES-ON-6 reading
   is weaker still.
2. **Only the S3 group is routed.** Nets of the GLOBAL group that end in slot 3 (HDMI3 to U3/U4, ETH3 to U1, and the
   slot 1 to bank 3 failover edge HOST1_1 into U309/U310) are not routed, so the copper they need through the pocket is
   absent; their pads and pre-laid escapes stay as obstacles. This is optimistic again: a LAYERS-NOT-THE-LEVER reading is
   strong, a REGION-CLOSES-ON-6 reading is weak. Routing and locking the GLOBAL group first, as B22 and B23 did, would
   remove the limit at the cost of a GLOBAL route (RECORDED pass costs, `b.json _b23_pass_rate_why`); it is outside this
   budget.
3. **One sample per arm**, because the router is deterministic; the factor of one half is a convention.
4. **Per-pass sessions can be missed** while the previous one is read; the plateau is over observed sessions.
5. **A8 is more routing than any real eight-layer board B** (section 7.2).

## 8. What this page does not claim

- It does not claim board B is feasible, or infeasible, on any layer count.
- It does not claim that decision 43 requires the trial before the whole-board eight-layer experiment; that order is
  the integrating session's (section 1).
- It re-reads B21's own artefacts; the B22 and B23 runs and the `region_room` readings are cited from `b.json`, whose
  runs are not in this tree.
- Its cut screen uses footprint origins, not pads or copper; it ranks buses, it does not size channels.
- The fabricator facts are a page and order-form read on one date, not a quotation.

## Appendix A. The schematic defects in board B's switch pockets

Read on B21's netlist (`v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net` as committed at `82dd1e4d`, schematic sha256
`eac5845f...`, generator sha `66e68fe66ab81617`) against the parts' own documents. Every IC-to-IC high-speed link on the
board is wired correctly; the defects are at connectors whose pin names are given from the host's side, and in one
socket's part. **State at `eadbe571`:** A.1, A.2, A.3 and A.5 are corrected in the committed netlist since `458b2873`
(round 6 of Review D, board B; each subsection says where), and `check_pcb_b.py` asserts lane direction, clock
termination and the enable pull-downs at the pad. The generator line numbers below are B21's; the corrected lines are
given at `eadbe571`. No board file carries the corrections yet.

**A.1 PCIe downstream, all six links (critical, VERIFIED).** The switch's transmitter reaches the socket pins on which
the module also transmits: `NVME1_RX_P` joins U101.100 (`PETP1`, an output in the PI7C9X2G404SL pin list, DS40068
Rev 5-2) to J_M2N1.43 (`PERp0`); `CARD2_RX_P` joins U201.106 (`PETP2`) to J_M2C2.43. Four primary sources agree:
Quectel's RM520N-GL pin table gives M.2 pins 41/43 as the module's `PCIE_TX` (AO) and 47/49 as its `PCIE_RX` (AI)
(hardware design V1.0); Raspberry Pi's CM5 IO board wires its M.2 pins 41/43 to the CM5's receive pins and 47/49 to its
transmit pins (`cm5io-kicad.zip`); and the CM5 datasheet, section 2.3.1, states the convention for every PCIe connector:
"If using a PCIe connector, the signals are labelled from the host's point of view, so TX and RX lines don't need to be
swapped." That clause covers the E-key sockets of slots 1 and 3 as well, which the first version of this page left
INFERRED. The upstream link to each CM5 is correct. No downstream transmit pair has an AC coupling capacitor; the
Quectel reference circuit places 220 nF on the host's transmit pair. That gap was first recorded in
`ARCH-PCB-B-IOHA.md` section 2 on 9 September ("There is no AC coupling on any PCIe lane or on the reference clock
tree"), and only the upstream half was fixed on 16 September. `check_pcb_b.py:126-127` checks only that each net
reaches the switch and a socket. Fix in `gen_sch_b.py` (socket maps at lines 461, 469, 477 and 495 of B21's generator): the switch's
transmit pair to the socket's `PETp0/PETn0`, a series 220 nF on each, and a direction check. **Corrected at
`458b2873`** (`gen_sch_b.py:538-543` at `eadbe571`, "the two downstream transmit pairs, each through its own 220 nF at
the switch"); the fabric map reads every downstream lane OK on the committed netlist (`FAILOVER-FABRIC.md` section 4.4,
re-read on `main`, `ARCHITECTURE.md` section 5.2).

**A.2 LimeSDR SuperSpeed (major, VERIFIED).** The hub's SuperSpeed transmitter U102.3 reaches J_LIME.6 (`SSRX+`) through
C161, and J_LIME.9 (`SSTX+`) reaches the hub's receiver U102.6 (`gen_sch_b.py:519` and `:529`). Raspberry Pi's CM5 IO
board wires its USB 3 Type-A pins 5/6 to the host's receive pair and 8/9 to its transmit pair (J12). As generated in B21,
the LimeSDR could not link at SuperSpeed. **Corrected at `458b2873`** (`gen_sch_b.py:941` and the hub port map at
`:762-764` at `eadbe571`; `check_pcb_b.py:164-167`).

**A.3 The switch's reference clock input (major, VERIFIED text).** `REFCLKO_P0` (U101.85) joins `REFCLKP` (U101.110)
directly, on all three slots (`gen_sch_b.py:428`). The switch datasheet, section 3.1: "The input clock signals must be
delivered to the clock buffer cell through an AC-coupled interface ... It is recommended that a 0.1uF be used in the
AC-coupling." **Corrected at `458b2873`:** every used REFCLKO pair coupled and source-terminated (`gen_sch_b.py:549-564`
at `eadbe571`; `FAILOVER-FABRIC.md` section 4.3); the clock's quality at the endpoints is unvalidated (FB-FAB-8).

**A.4 The failover ring (a document contradiction, resolved).** `ARCH-PCB-B-IOHA.md` section 4, `gen_sch_b.py:543`
of B21 (`:788` at `eadbe571`, `f = s % 3 + 1`), `check_pcb_b.py:109` (`:112-115` at `eadbe571`) and both netlists all
give bank 1 to slot 2, bank 2 to slot 3 and bank 3 to
slot 1 (bank 1's mux U109.15 `C0p` is on U31B.171, slot 2's `USB3-1-TX_P`), and `PANEL.md` (its hardware-record
paragraph) gives the same for bank 1, the only bank it names. Section 15 of the IOHA note gave the reverse ring until
26 September 2026 and is corrected on `main` since `4ec785d8`, so every source now agrees. With three slots in a row either ring direction has one edge from slot 1 to slot 3; today it is
slot 1's USB 3 port 1 running from U30B (x 94.5) to bank 3's muxes (x 187 to 194) across slot 2's column.

**A.5 Slot 2's 5G socket and SIM 2 (critical for the 5G module, VERIFIED; found in review).** In B21 J_M2C2 was drawn as
"M.2 B-key 3052 socket, TE 1-2199119-5" (LCSC C574849, `gen_sch_b.py:479`). TE's customer drawing C-2199119 rev F,
sheet 2, lists 1-2199119-5 as KEY M, and TE's product page says the same (read by this review on 25 September 2026; the
drawing is filed as `v2/vendor/m2/te-2199119-customer-drawing-revF.pdf` since `d468613e`, beside the older
`te-2199119-m2-b-key.pdf`, which is TE's Quick Reference Guide 1-1773702-1, not the drawing); the RM520N-GL is a
key-B-only 3052 module
(`v2/vendor/quectel/quectel-rm520n-series-hardware-design-v1.1.pdf`: "M.2 Key-B", and pins 12 to 19 drawn as the notch in
Figure 2), so it cannot be inserted as drawn. A key-B replacement is
TE 2199119-3 (same drawing, 3.2 mm), which stays a mismatch until its land (pad rows, anchors, the locating holes of
drawing sheet 3 and the 3052 standoff) is proven against the maker's drawing. B21's generator also wired SIM 2 to the
wrong module pins (`gen_sch_b.py:474-477` of B21: clock on 40, data on 42, reset on 44, supply on 46; the module has 40
USIM2_DET, 42 USIM2_DATA, 44 USIM2_CLK, 46 USIM2_RST and 48 USIM2_VDD, and pin 48 was unconnected). **Corrected at
`458b2873`** (S-12, S-13: `gen_sch_b.py:623-644` at `eadbe571`): J_M2C2 is TE 2199119-3 (JLCPCB C590866), its pad field
checked pad by pad against sheet 3, **except the two locating holes**, which the footprint generator does not draw, so
the land stays a mismatch until it carries them (`:639-640`); SIM 2 is on the module's USIM2 pins 40 to 48.

The key-B replacement is the session's, either way, not part of the owner's ruling (`CONOPS.md` section 7, D-07:
"(session)"). What the owner's D-07 of 26 September 2026 rules is the jacks: three (ANT0, ANT2, ANT3) at board A's free
site (X +46) if the case measurement confirms that site and the board E clamp fit, otherwise two (ANT0, ANT2). **The
owner reversed D-08 the same day, so no case measurement will come;** the condition is judged on paper against the
worst of Peli's own figures (`ARCHITECTURE.md` section 9.2, the session's reading under the owner's standing rule): the
case half is laid out in `CASE-MARGINS.md` section 3.4 (ANT3 is the east wall's arrestor bulkhead at Y 0, Z 59; no
case row is NOT MET; the east jumpers' layering under the plugs, M17g and M17x, is OPEN until the jumper plug is
picked), and the board half, a board A site at X +46 and a board E clamp there, is in no generator yet. The three-jack
branch stands unless the picked plug or board E's clamp bar makes a row NOT MET that no lever closes. None of this is
in slot 3, so none of it changes the trial of section 7.
