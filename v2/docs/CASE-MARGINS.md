# Case margins: the V2 kit held against Peli's own figures (Peli 1450 with the 1450PF frame)

MESHSAT-1357, written 26 September 2026 and revised six times the same day after independent checks, the fifth to
apply the review of that day (section 1, Verdicts) and the sixth to correct two chains the last check found short
(finding 25). Prototype design: nothing in this kit has been built, fitted to a
case or field deployed, and no V2 board has been made. Every number
here is read from a Peli file or page named in section 1, from a maker's sheet in `v2/vendor/`, from a file in this
tree (file:line, at main `29f00554`), or derived from those by the arithmetic shown. A number that rests on an
assumption is marked INFERRED; one that no held source gives is TBD.

**Why this document exists.** The first ruling D-08 answered a request the session had written (workstream W4): the
owner was to measure his used case and build a cardboard mock-up. On 26 September 2026 at about 09:30 CEST he
declined it: "you have the CAD files and all the measurements why do you need from me to measure an old case?" D-08
is reversed and nothing is asked of him. Ruling D-08a stands as the design basis: the current moulding of Peli's
1451-931 customer drawing dated 15 January 2025, and a new case if the one used for the build is older. The design
therefore takes Peli's own figures and the tolerances a source states as its basis, and computes every
case-dependent margin against the worst of them, plus a stated minimum. Where a margin rests on a tolerance no source
states, on a TBD or on a part still to be picked, it is OPEN, not met: nominal CAD establishes no physical fit, no
blind-mate alignment and no seal (section 1, Verdicts). Section 7 lists what closes each OPEN item; most of it is a
targeted, unpowered mock-up that the session recommends for the build stage, on the new case of the current moulding
bought for the prototype. Nothing here asks the owner to measure or build anything. Every change below is **the
session's choice under the owner's standing rule of 26 September 2026** (never ask the owner; take the recommended
option; record it as taken and reversible).

**What reading Peli's files properly changed.** Peli publishes more than the tree had used: a 1450 panel frame
instruction sheet with a tolerance block, and mounting instructions that say where the frame sits and which way a
panel goes. Read face by face, the STEP bodies and the drawing also contradict several numbers the tree carries
(section 2.6). Two consequences dominate. First, the face plate's height of 101.4 mm, on which the tightest margin
of the kit depends (the monitor over the Compute Module 5 heatsinks), cannot be derived from any Peli file. Second,
the seat Peli describes for its frame, "fully seated on the internal ribs", is not a defined height at the current
moulding: the ribs catch the frame by 0.012 mm at nominal, and over the frame's published tolerance alone it can come
to rest anywhere in a band 11.9 mm deep (section 2.7). So the design gives the frame a height of its own: four setting
legs fixed under the frame's ring and standing on the case floor (C6), with the face plate on the frame the way Peli
documents it (C1). With them the monitor's margin over the heatsinks computes to 6.26 mm nominal and 3.62 mm at the
worst of the stated allowances, against a 2.0 floor; it stays OPEN, because three of its contributors have no source
yet (section 3.1). The back wall is laid out the same way: the connector plate places all six items the tree rules
for it, inside the part of the wall Peli's drawing shows free (section 3.3, C3). The end walls carry the ruled
gas-discharge arrestors as the antenna bulkheads themselves, bodies outside, on one aluminium RF entry plate per wall,
five on the east wall and seven on the west so that every jumper inside has a planned route past the pack and the
setting legs (section 3.4, C2 and C4); the tree's Amphenol couplers retire. Of the 70 margins `frame_seat.py`
computes for this arrangement, 35 are MET and 35 OPEN, and none is NOT MET. Two of the OPEN rows fall below their
minimum at the limit of the jumper plug's class: how the east jumpers lie under the plugs (M17g, M17x). They stay
OPEN until the plug is picked (sections 3.2 and 3.4).

## 0. Findings and decisions at a glance

| # | Finding | Status | Decision (session's choice, standing rule of 26 Sep 2026) |
|---|---|---|---|
| 1 | Peli mounts the frame "fully seated on the internal ribs" and the panel **on top of the frame, covering the o-ring**, screwed from above into brass inserts pressed in from below. The tree clamps the plate **under** the frame's ring from below (`ASSEMBLY.md:29`). | VERIFIED (Peli instructions, product page) | C1: the face plate goes on the frame as Peli documents |
| 2 | The as-coded face top Z 101.4 comes from "base 109.4, lip 8" (`panel1450.py:26`). Peli's STEP and drawing give a base of **108.97**; the frame's ring is **9.39** thick, and nothing on the frame is a ledge 8 mm below its top. | VERIFIED | C1 with C6 derives the face height: 106.52 nominal, 104.77 to 108.27 at the worst |
| 3 | **The rib seat is a knife edge.** In Peli's envelope the end-wall ribs catch the frame's bottom edge by 0.012 mm and the long-wall ribs miss it by 0.75. The ribs stand 0.76 proud; the frame outline and the case interior each move the frame's edge by 0.38 per side. Over the frame sheet's tolerance alone the frame rests anywhere from Z 72.70 to 84.58 (11.88 mm); with the rib-top allowance up to 85.34, and with the case interior allowance down to 54.51. | VERIFIED geometry; seat range INFERRED from it | C6: four setting legs, fixed to the frame's ring and placed by the frame's own centring, give the frame a floor-referenced height; the ribs can then only lift an oversize frame, by at most 0.76 over their nominal top |
| 4 | Monitor body over the heatsinks, floor 2.0 mm: as coded +2.24 nominal and +0.95 worst on an unreproduced datum; plate under the ring with the frame on the ribs, -8.08 nominal; plate on a frame resting where Peli's ribs put it, anywhere from -25.23 to +5.60; **with C1 on the C6 legs, +6.26 nominal, +3.62 worst, +5.09 RSS low**. | INFERRED arithmetic on VERIFIED inputs | C1 and C6; the dock strip's VHB pads lift the whole stack as `ASSEMBLY.md:47` has it. M1 stays OPEN: three contributors are TBD (section 3.1) |
| 5 | The floor fillet is **R 15.88 mm** (5/8 in) on all four floor edges, tangent to the walls at Z 15.32, not "about 10". | VERIFIED | Pocket and wall numbers recomputed |
| 6 | The inner ribs are **15** small tapered ribs: on the end walls at **Y 0 and +-76.2** (six), on one long wall at **X 0, +-76.2, +-152.4** (five), on the other at **X +-76.2, +-152.4** (four); Z 26.42 to 84.58, 0.76 proud at the top. Not five ribs at X -170, -95, -18, +60, +137. | VERIFIED | C4: nothing of the antenna bulkheads bears on the end walls' ribs; C3 moves the connector plate |
| 7 | With the frame near Peli's seat its skirt covers the walls from about Z 84 upward, and the jacks at Z 88 sit inside it. | INFERRED from VERIFIED geometry | C2: the bulkheads' axis to **Z 59**; the highest thing inside an end wall stays 1.73 under the skirt at the worst (M10, OPEN) |
| 8 | Jacks at Y +-72 put their inner lock washer on the ribs at Y +-76.2 and their outer hex on moulded features at Y +-79.0 (DXF end view). | VERIFIED positions; interference INFERRED | C4: nothing of the bulkheads bears on the wall inside; the entry plate's screw heads keep 17.21 from the ribs and its top 3.42 under the features at the worst (M11, M12) |
| 9 | End and long walls are **5.34 mm** thick (DXF sections A-A and B-B). Wall plus the coupler's NBR O-ring leaves 0.41 mm of the Amphenol 132170's 6.5 mm range, -0.35 at a +0.76 wall. | VERIFIED; worst INFERRED | C4: the 132170 retires; each arrestor clamps on the 6.0 entry plate, its own O-ring on the plate's outer face and its nut in a 26.0 spot-face 1.5 deep in the plate's back, with 1.20 of thread to spare at the worst (M13, OPEN until the O-ring's height is dimensioned; finding 25) |
| 10 | The as-coded connector plate starts 2.9 mm inside the outer bottom radius, its west screw column lands on the rib at X -76.2, it lies in the X span of the hinge fairings (bases from \|X\| 58.93 in the drawing's top view), and it carries two of the six items the tree rules for it (`V2-SPEC.md:11`, `ASSEMBLY.md:135`: shore DC, USB, sealed RJ45 with PoE out, sealed USB-C, the pod's M8 receptacle, the ground stud). | VERIFIED sheets and drawing views; INFERRED class envelopes | C3: one 114.0 x 68.3 x 5.0 plate between the fairings carrying all six; the mates of the RJ45 and the USB-C pass under B16, the others turn down outboard of it |
| 11 | The QMX tray's east edge lies 0.58 mm inside the lid's flat ceiling. | VERIFIED geometry; margin INFERRED | C5: tray 1.5 mm west |
| 12 | The pack pocket is bounded by board A's edge and Peli's fillet, not by the X 178 of appendix 32.62: the 4S3P block keeps 1.85 mm to the fillet and 7.38 mm to the wall at the worst. | INFERRED | No change; `ASSEMBLY.md:48` pocket text to be corrected. M4b is MET; M4a is OPEN until the pack's hold-down fixes its place |
| 13 | Until its four screws are driven the frame floats about 0.8 mm in X and 1.55 mm in Y per side; pushed against a wall, with the plate floated the same way on its screws, the plate can touch the case in Y (-0.21 at the worst). | VERIFIED geometry | C6 includes a centring step before Peli's screws are driven, and the legs, fixed to the frame, are placed by that same step |
| 14 | The shoulder at Z 101.04 carries the case's height allowance like every other case height. At the first issue's pad height the plate's rebated band could face the cavity below the shoulder, 1.02 mm narrower in X than the rim zone, where M8x falls to 0.68. | INFERRED from VERIFIED geometry | C6's pad top is 94.13, the lowest that keeps the plate's underside above the highest the shoulder can stand (M8z, OPEN: its 0.10 at the worst rests on the case's height, which Peli does not state) |
| 15 | The sealed RJ45 recommended on 11 September (Bulgin PX0833, `v2/vendor/open-picks.txt:13`) is 38.1 mm over its coupling ring and needs a wall hole of about 36 for its nut, so with it the six items and the plate's fixings do not fit the free part of the back wall (section 3.3), and its own sheet rates it 42 V against the kit's 54 V PoE feed (`ASSEMBLY.md:104`). | VERIFIED (maker's sheet); fit INFERRED | C3 lays the RJ45 out as a MIL-DTL-38999 shell 15 wall-mount body, as the Glenair 233-370 is; the pick must meet that envelope and the voltage (section 6) |
| 16 | The ruled gas-discharge arrestors (appendix 32.50 item 4, "end walls"; `V2-SPEC.md:51`; decision 31, `pcb_decisions.yaml:281-282`, declares for board D "the same PolyPhaser GTH-SFF-AL at the antenna bulkhead that J_ANT already declares" and TRN-001 passes on it; `open-picks.txt:20`, one per bulkhead) have no place: the tree's bulkheads are Amphenol 132170 couplers (`ASSEMBLY.md:134`, `:192`). The GTH-SFF-AL is itself an SMA bulkhead on a 5/8-24 thread, 55 x 23 x 31 mm at most: at the previous issue's 20 mm jack pitch neighbours collide, and a body inside the case meets the frame skirt, the legs' zone and B16's RockBLOCK and LimeSDR. | VERIFIED (maker's sheet); fit INFERRED | C2 and C4: the arrestors are the bulkheads, bodies outside, five on the east wall and seven on the west at a 31 pitch and Z 59, each through a 6.0 aluminium RF entry plate sealed over 27 mm wall holes (section 3.4) |
| 17 | D's mate is the Glenair 233-340 plug of `ASSEMBLY.md:144`, **32.51** across on its own sheet, not the INFERRED 30; C's is a D38999/26 shell 13 plug, 29.4 (Amphenol's Series III catalogue, page 52; its M85049/38S13N strain relief the same). At the previous issue's centres D's and C's mates were 0.65 apart (0.95 with C at its held 29.4). | VERIFIED (makers' sheets) | C3 re-laid: C lower, on a 22 mm wall hole, D above it; the tightest mated pair keeps 1.11 at the worst with each connector at its float on its screws (M14k; finding 25) |
| 18 | Peli's insert pattern carries the frame sheet's +-0.38 per side; the previous issue's 3.8 mm plate holes let a 6-32 float only 0.15, so the plate was not sure to go on. | VERIFIED tolerance; fit INFERRED | C1: 4.6 mm holes (0.55 of clearance for the largest 6-32, 0.07 to spare at the worst, M8f), the plate 0.8 narrower (377.2) to pay in M8x for the 0.63 the smallest 6-32 lets it float, the full-thickness face 368.0 x 253.0 so the 6-32 pan heads keep 0.77 (M8h) |
| 19 | The connector plate's six M4 screw holes broke the 3.0 gasket band (1.95 at the worst) and their 9.0 washers came within 0.30 of the plate's edge. | INFERRED from VERIFIED geometry | C3: the columns at X +-51.1 and the rows at Z 24.2, 50.1, 76.0 meet the band with the screw holes included (3.05 at the worst, M14m, OPEN), under bonded sealing washers 10 across that stay on the plate (M14p) |
| 20 | The leg column's outer-back corner lies in the skirt's R 17.53 corner arc, and the locator places a leg in X and Y at once: at the previous issue's column the Euclidean worst was 0.95. | INFERRED from VERIFIED geometry | C6: the column 0.20 inboard (X 175.40 to 180.17): 1.14 at the worst (M21d, OPEN) |
| 21 | The previous issue's jumper plug sent every east cable down from Z 54.0 onto the pack (top Z 44.58, X 122 to 178.65, under every east site), where RG-316 cannot turn at R 12.5; the C6 legs close the corridors at the pack group's ends (1.77 at the worst against a 2.49 cable); its M17 measured a clearance at Z 50, not a route. Round the pack's ends, a cable from an east site at \|Y\| 93 meets a leg's column before it can move inboard of it (22.32 short at nominal). | INFERRED from VERIFIED geometry | C2: each east plug's cable leaves along the wall, the plug turned 30 degrees down, into a bundle over the pack's outer strip under the plugs, inboard of the legs' columns and down beyond the legs; the two WIFI P2P bulkheads move to the west wall, whose cables fall straight to the floor; each jumper cut to its route, 232 to 412 mm. This is a planned route, not a closed one: every jumper row is OPEN, and how the east cables lie under the plugs turns on the plug still to be picked (M17g, M17x; finding 24) |
| 22 | The RF entry plate's M4 screws in 4.5 wall holes, into threads tapped in the plate, floated 0.26 against 0.40 of hole marking and thread position, so not all eight were sure to start; the previous M11d left out the plate's own +-0.20 and the screw's length tolerance, and at the worst the tips stood outside, where an arrestor body lies over the screws at \|Y\| 100. | INFERRED from the stated allowances and classes | C4: 5.0 wall holes (0.11 to spare, M11e) under sealing washers whose rubber face covers them (M11f), the screw rows 0.25 further in (M11b, M11c), and a 6.0 plate on which an M4 x 12 stays inside (0.43, M11d) and engages 1.95 at the least (M11g). M11d, M11e and M11g are OPEN: they rest on the wall's thickness, the gasket's compression and the hole marking, which T5 and T6 measure |
| 23 | The review of 26 September 2026 (`v2/docs/reviews/2026-09-26-foundation-progress-review.md:79`): Peli geometry and stated tolerances are the design basis; a margin whose tolerances or frame seating are not specified is unknown; nominal CAD establishes no physical fit, blind-mate alignment or sealing; a targeted unpowered mock-up can resolve expensive mechanical uncertainties earlier than a populated build. Peli states no tolerance for the case, and the kit's build allowances are assumptions. | VERIFIED (the review's text) | Every margin carries MET, NOT MET or OPEN (section 1, Verdicts). A row is MET only if it still meets its minimum with every unstated allowance taken twice; 35 of the 70 computed rows are OPEN, and section 7 names what closes each, chiefly a targeted unpowered mock-up recommended for the build stage |
| 24 | The last independent check found that the east bundle's layering under the plugs does not close as laid out. Under 5G MAIN, which three cables pass, MAIN's own cable at the class's 16.0 reach lands 1.21 into the passing cable below its place. With the plug's cable axis at its inner end, which the class allows, the bundle's inboard column comes to -0.38 from B16's edge at the worst. | INFERRED from the plug class | No simple change closes either on held evidence: both turn on the plug's reach, its ferrule's diameter and the offset of its cable axis, which no held sheet gives. Both are OPEN rows with their bounds (M17g, M17x) and named levers, and the claim that the bundle closes is withdrawn (section 3.4) |
| 25 | The next independent check found two rows stated MET that fail at the worst. M13 left out the arrestor's O-ring, which the held drawing (page 3, rendered and read) shows on the thread's root, about 0.63 proud of the body's face, inside the .47 the chain counted as free thread; with it the thread on the full 6.0 plate leaves 0.62 nominal and -0.40 at the worst, and the drawing's note that every dimension on it is for reference only makes its +-0.51 an unstated allowance besides. M14j left out each part's float on its fixings, A's flange 0.24 on its M3 screws and a bonded washer 0.33 on its M4 (the term M14p carries), and counted one machined place for a pair: at the previous layout that pair came to 0.39 at the worst, A's and D's flanges to 0.83, and C's and B's mated plugs to 0.63 (M14k). The same float was missing wherever an arrestor's place enters a chain (each floats 0.32 in its 16.3 hole), and the floats that were carried had been taken at a screw's largest or nominal major, not at its smallest. | VERIFIED (the drawings and the classes); margins INFERRED | C4: each arrestor hole spot-faced 26.0 x 1.5 on the entry plate's back, so the nut sits 1.5 lower on its thread: M13 keeps 1.20 at the worst and 0.38 with the unstated allowances doubled, OPEN only on the O-ring's height; the nut and washer class narrowed to 24.0 x 5.0 from the drawing's 3/4 in hex (M13b to M13d). C3: A, C, B, D and F moved 0.8 to 1.7 mm east, so that every pair on the plate's face and every mated pair keeps 1.0 with each part at its float and at its machined place (M14j 1.13, M14k 1.11). C1: the face plate 0.2 narrower, 377.2 (M8x). Every row that carries the O-ring (M18, M17c, M17w, M17x) or a float (M2b, M8, M8h, M11f, M13c, M14e, M14g, M14n, M14p, M17a, M17b, M17g, M18b, M18c, M21h) now carries it at its worst; M17a falls to OPEN (1.90 with the unstated allowances doubled, against its 2.0) |

## 1. Sources and method

| Source | Identity | What it gives |
|---|---|---|
| Peli 1451-931 customer drawing, dated 1.15.25 | `v2/vendor/peli/1450/1451-931-customer-drawing-2025-01-15.pdf` and its DXF `1451-931-customer-drawing.dxf` (sheet drawn at 1:3, header `$DIMLFAC` 3.0) | the dimensioned views and sections; the top view's hinge fairings and the end view's back features; note 1 "dimensions are for reference only; typical industry-standard tolerances apply" |
| Peli 1451-931 base and lid STEP | `v2/vendor/peli/1450/1451-931-bottom.STEP` ("1451-931 Bottom PID", 2025-08-08) and `1451-931-top.STEP` ("1451-931T Top 7-24-2025"), unit INCH | the cavity: floor, drafted walls, fillets, inner ribs, rim zone, lid cavity (the outer skin is an envelope block, not the real skin) |
| Peli 1450PF frame STEP | `v2/vendor/peli/1450/1450-panel-frame.STEP` (2015-08-06), unit INCH | the frame: skirt, ring, gasket step, window, insert bores, mounting-screw holes, notches, lettering |
| 1450 panel frame instruction sheet 1453-314-000 rev A (05-27-09) | filed with this document at `v2/vendor/peli/1450/1450_pf.pdf` (the tree's name for the 1400 and 1520 sheets), from https://media.pelican.com/cad/protector-panel-frames/1450/1450_pf.pdf, fetched 26 Sep 2026, sha256 (first 16 hex characters) 4681c0525a3cf605 | 378.4 x 263.1 x 17.5, window 349.7 x 233.8, ten inserts 5.18 +-0.13 on 358.1 x 242.3; **tolerance block: one-decimal mm +-0.76, two-decimal mm +-0.25**; the assembly detail (gasket, frame, screw) |
| Pelican panel frame mounting instructions | filed at `v2/vendor/peli/panel-frame-inst.pdf`, from https://business.pelican.com/storage/docs/cad-downloads/panel-frame-inst.pdf, fetched 26 Sep 2026, sha256 (first 16) 797a2ed6f9809d0b | steps 1 to 4, quoted in section 2.5; brass inserts "6-32 X 1/4 Thread (M3.5 x 6.3mm)", 4-40 only for the 1120 and 1150 |
| Pelican 1450PF product page | Wayback capture of 7 Feb 2025, https://web.archive.org/web/20250207101614/https://www.pelican.com/us/en/accessory/cases/special-application-panel-frame/1450PF/ (sha256 of the capture, first 16: 44d406227add356c) | "Mount most interface panels (customer supplied) flush with the rim"; "A polymer o-ring seals the panel so the base of the case remains watertight, even with the lid open"; kit: frame, o-ring, 10 inserts, 4 self-tapping screws |
| Pelican 1450 product page | https://www.pelican.com/us/en/product/cases/protector/1450 answered HTTP 403 on 26 Sep 2026 at 09:37 CEST (peli.com EU likewise); read from the latest Wayback capture, 29 Mar 2026 04:10:54 UTC, https://web.archive.org/web/20260329041054/https://www.pelican.com/us/en/product/cases/protector/1450 (sha256 first 16: 85cc10b72a93bab6) | interior 14.66 x 10.24 x 6.12 in (37.24 x 26.01 x 15.54 cm), lid depth 1.75 in (4.45 cm), bottom depth 4.37 in (11.1 cm), exterior 16.44 x 13 x 6.82 in, 2.5 kg without foam, -40 to +87 C |
| Glenair 233-370 feed-through | `v2/vendor/d38999/glenair-233-370.pdf`, page C-15; flange and hole figures as `case_wall_cutouts.py:13-14` quotes them | D0 wall mount: 39.87 max overall, **16.51 max behind the flange** (".650 (16.51)"), flange 2.11 to 2.49 thick and 31.29 square, four holes of .124/.132 (3.15/3.35) diameter on 24.61 (D0 face view), plate hole 23.01, panel .0625 to .250 in; note 4: front and rear USB female |
| Glenair D38999/20 wall-mount receptacle | `v2/vendor/d38999/glenair-d38999-20.pdf`, page 30; `case_wall_cutouts.py:10-12` | 1.240 (31.50) overall; for shells 9 to 15, H .771 to .820 (19.58 to 20.83) front of the flange, G .083 to .098 (2.11 to 2.49) flange: **at most 9.81 behind the flange**; shell 13 flange 28.9 square, four holes of .120/.136 (3.05/3.45, column E) on 23.01, plate hole 19.05 |
| Bulgin PX0833 (Standard Buccaneer RJ45 coupler) | `v2/vendor/bulgin/bulgin-px0833-sealed-rj45-coupler.pdf` (in the tree since 11 Sep 2026) | 38.1 mm over the coupling ring, panel 0.8 to 5.2, 24.5 behind the panel's front face, D cut-out 27.18 to 27.70, **42 V** and 1.5 A maximum |
| Bulgin PXP4043 (4000 series micro-B, rear panel mount) | filed with this document at `v2/vendor/bulgin/bulgin-pxp4043-micro-usb-rear-panel.pdf`, from https://www.bulgin.com/pdf/pdf.php?sku=PXP4043, fetched 26 Sep 2026, sha256 (first 16) 245d895c678995b2 | the 4000 series rear-panel body, read from the sheet's 310-pixel drawing: hex 22.23 A/F, cut-out 18.9/19.2 with a 9.0/9.1 flat, 17.8 from the front to the panel's rear face, 24.8 overall, 6.2 maximum panel; 19.7 over the coupling ring |
| Bulgin PXP4043/C (4000 series C-type, rear panel mount) | filed at `v2/vendor/bulgin/bulgin-pxp4043c-usb-c-rear-panel.pdf`, from https://www.bulgin.com/pdf/pdf.php?sku=PXP4043/C, fetched 26 Sep 2026, sha256 (first 16) cce556227a71f895; the series sheet `v2/vendor/bulgin/bulgin-4000-series-sealed-usb-c.pdf` | rear panel mount, a lead of 150 +-10 to a 2 x 12 header; 5 A, 30 V or less; **no panel dimension in either sheet** |
| Amphenol Connex 132170 drawing | `v2/vendor/rf/amphenol-connex-132170-sma-bulkhead-ff-drawing.pdf` (rev D) | panel 2.0 to 6.5 mm, 8 hex nut 1.60, lock washer 10.20, 9.5 hex flange, overall 22.10; no mounting torque given. The tree's coupler at `29f00554`; C4 retires it |
| PolyPhaser GTH-SFF-AL sheet | `v2/vendor/polyphaser/polyphaser-gth-sff-al-sma-surge-protector.pdf` (in the tree since 11 Sep 2026, sha256 first 16 ae3f031d7ecb8783) | gas discharge tube, SMA female to female bulkhead, DC to 6 GHz, 150 W, 10 kA; **2.2 x 0.9 x 1.2 in (55 x 23 x 31 mm) max**, 0.25 lb; its drawing (rev B, page 3; leading dimensions in inches, .XX +-.02, and in the title block **"ALL DIMENSIONS SHOWN ARE FOR REFERENCE ONLY"**): 2.18 overall, **.47 of 5/8-24UNEF-2A thread** from the body's face, with the O-ring on the thread's root, drawn about 0.63 proud of that face and so inside the .47, a .30 SMA jack beyond the thread, a .35 SMA jack at the body's far end, a split lock washer and a hex nut, a crimp ring terminal for the ground wire, the gas tube under a .528 (13.4) cap. The O-ring, the nut and the washer are drawn, not dimensioned: scaled from the page rendered at 600 dpi (20.95 px/mm on the 2.18), the O-ring stands 0.63 proud, the nut is 19.1 across its flats (3/4 in, 22.0 across its corners) and the washer 20.5 across, about 4.7 thick together. No ingress rating and no panel range are given |
| Glenair 233-340 coupler plug | `v2/vendor/d38999/glenair-233-340.pdf`, page C-4 | G6 plug with accessory threads (the kit's USB host lead, `ASSEMBLY.md:144`): **diameter 1.280 (32.51) max**, 1.935 (49.15) max long |
| Glenair M85049/38 strain relief | `v2/vendor/d38999/glenair-as85049-38.pdf`, Table I | shell 13 (the DC lead's M85049/38S13N, `ASSEMBLY.md:143`): **E max (diameter) 1.157 (29.4)**, self-locking |
| Amphenol MIL-DTL-38999 Series III catalogue | `v2/vendor/d38999/amphenol-d38999-iii-federal.pdf`, catalogue page 52 (the PDF's page 51) | D38999/26 straight plug, **Q dia max 1.157 (29.4) for shell 13 and 1.280 (32.5) for shell 15** |
| Review of the progress report of 26 September 2026 | `v2/docs/reviews/2026-09-26-foundation-progress-review.md` (in the tree at main `1f614233`), section 4, line 79 | the rule for this document's verdicts: "Use Peli geometry and stated tolerances as a design basis. If tolerances or frame seating are not specified, mark the margin unknown. Do not claim that nominal CAD establishes physical fit, blind-mate alignment or sealing. A targeted unpowered mock-up can resolve expensive mechanical uncertainties earlier than a fully populated seven-board build." |

**Method.** The STEP files were read face by face with a small stdlib reader (`v2/vendor/peli/step_faces.py`:
surface type, plane normal and the box of each face's vertices, inch to mm; readings in
`v2/vendor/peli/1450/*.faces.txt`); each number below names its face entity (`#id`) so anyone can re-read it. The
DXF was read the same way (`v2/vendor/peli/dxf_read.py`): dimension entities `_D` to `_D_10` (their extension points
put each dimension at a height), the hatch boundaries of section B-B (entity 7866, the end walls; datum: cavity
floor at sheet y 95.295, centre at sheet x 169.114) and section A-A (entity 7590, the long walls; datum from `_D_3`),
and, with `--backwall`, the back wall's outside: the top view's fairing lines, the A-A cut line and the end view's
back features, each by its index in the ENTITIES section (reading in `v2/vendor/peli/1450/dxf_backwall.out`).
No OpenCASCADE is present on the runner or the rented box, so no B-rep evaluation was made: a face's extent is the
box of its edge vertices, exact for the planar and ruled faces used here. The margins are computed by two stdlib
scripts beside the reader: `v2/vendor/peli/case_margins.py` (the case geometry and the as-designed figures) and
`v2/vendor/peli/frame_seat.py` (where the frame can rest, the setting legs, every margin of the chosen arrangement,
the connector plate, the end walls' RF entry plates and the jumpers' route from them to the dock strip); their
outputs are `v2/vendor/peli/1450/case_margins.out` and `frame_seat.out`.

**Case frame.** X along the long axis from the case centre (+X east end wall), +Y toward the back (hinge) wall,
Z up from the cavity floor, as `v2/ecad/tools/panel1450.py:1-3`. The frame's lettering "1450 FRONT" sits at the
case front (-Y), as Peli's instruction step 1 requires, so the frame STEP's x and y map to case X and Y.

**Tolerance model.**
- Published by Peli: the frame sheet's +-0.76 mm on one-decimal dimensions (its 17.5 height, 378.4 x 263.1
  outline, 349.7 x 233.8 window, 358.1 x 242.3 insert pattern), so +-0.38 per side on the outline, the window and
  the pattern. VERIFIED.
- The case drawing publishes none. Where a case dimension enters a chain, Peli's frame class is applied to it
  (INFERRED, a stated allowance, not a Peli tolerance): +-0.76 to a case height against the floor under the stack
  (rib top, rim, shoulder), +-0.76 between two points of the floor (a leg's foot against the stack's pads), +-0.38
  per wall to a width or to a feature's position. The frame ring's 9.39, the skirt's 8.13 and the skirt's inner
  face, which the sheet does not dimension, take the same class (INFERRED).
- The kit's own parts carry drawing tolerances: setting leg height +-0.10, plate outline and hole positions +-0.10,
  rebate depth and line +-0.10, the entry plates' spot-face floors +-0.10, positions machined into the connector plate
  and the RF entry plates +-0.10 (INFERRED);
  the face plate's 3.0 takes +-0.13 and the entry plates' 6.0 +-0.20 (EN 485-4 class, standard not held, INFERRED);
  a 2.0 closed-cell gasket compresses to 1.5, anywhere from 1.0 to 2.0 (INFERRED); a sealing washer is 1.5 +-0.10
  thick (INFERRED); a bundle of cables lies within +-0.5 of its drawn place, set by its ties (INFERRED).
- Bought parts by their makers' tolerance blocks. The arrestor's drawing gives .XX inch dimensions +-0.51 but marks
  every dimension "for reference only", as Peli's drawing does, so its +-0.51 is carried as an unstated allowance
  (Verdicts, below). By the classes of standards not held (INFERRED): an ISO 7380 button head's length +-0.35 (js15,
  10 to 18 mm); the 6g majors of M3 (2.874 to 2.980), M4 (3.838 to 3.978), M6 (5.794 at least) and M10 x 0.75 (9.838
  at least); the 2A majors of 6-32 UNC (0.1312 in, 3.332, at least) and of the arrestor's 5/8-24UNEF (0.6167 in,
  15.66, at least; ASME B1.1); RG-316 2.49 over its jacket (MIL-DTL-17, 0.098 in). A screw's largest major (for the
  6-32 the basic 3.505) decides whether it passes its hole; its smallest decides how far the part it holds can float.
  A part whose sheet gives no size is laid out as a class the pick must meet, marked INFERRED (section 6 lists each).
- A part held by screws in clearance holes, or by its body in a hole, can sit anywhere its fixings let it, and every
  chain in which its place counts carries that float: the face plate 0.63 on its 6-32 screws in 4.6 holes; each
  arrestor 0.32 in its 16.3 hole; on the connector plate, A's and D's flanges 0.24 on M3 in the 233-370 class's 3.35
  holes, C's 0.29 in the D38999/20's 3.45, B's body 0.30 in its 19.2 cut-out, E's M8 receptacle 0.33 in a 10.5 hole
  and F's stud 0.30 in a 6.4 hole (the last three INFERRED), and each M4 x 25 0.33 in its 4.5 hole, which its bonded
  washer follows. A pair on one plate carries both floats and both machined places. The O-ring under each arrestor's
  body is installed anywhere from fully seated to the 0.63 its drawing shows: 0.32 +-0.32 (INFERRED; no gland is
  drawn and no torque stated).
- Build allowances (INFERRED): the frame centred to +-0.20 by the wedges of C6; a leg placed on the frame by its
  printed locator within +-0.30 of the window's edges, so a leg sits within 0.88 of its drawn place against the
  case centre (centring 0.20, window per side 0.38, locator 0.30) and within 1.26 against a case feature (plus 0.38
  per wall); the locator registers on both window faces, so a leg moves by up to 0.68 in X and in Y at once against
  the frame's own features, and M21d is taken in two dimensions; the largest 6-32 screw (major 3.505) has 0.55 of
  clearance in the face plate's 4.6 mm hole, which must take Peli's insert pattern (+-0.38 per side) and the hole's
  own place (+-0.10); the closed lid sits within +-0.38 of the base; the backer ring sits within +-0.20 on its
  standoffs; the stack is placed within +-1.0 in plan (the dock strip is laid on its VHB pads by hand) and so is the
  pack; a wall hole is marked from the 1:1 template within +-0.3, and so are the connector plate and the RF entry
  plates.
- JLCPCB board thickness +-10 % (1.6 +-0.16, `v2/vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md:29`),
  3M VHB 5952 1.1 +-10 % (`v2/vendor/seals/3m-vhb-tapes-family-2018.pdf`), VERIFIED; board B bow 0.3 over 40 mm
  (IPC-6012 class, not held), INFERRED.
- Where Peli's own figures disagree (drawing, STEP, web page), the one that hurts the margin is taken as the worst,
  unless it contradicts Peli's own parts fitting (section 2.1 explains the one case).
- **Worst case** is the linear sum of every bound in the direction that hurts; **RSS** treats each bound as three
  sigma. Contributors with no number (TBD) are listed and left out, so both figures are optimistic bounds.

**Minimums.** 2.0 mm for a face part over a board part, the C gate's floor (`v2/ecad/tools/z_budget.py:16`,
`check_pcb_c.py`). 1.0 mm for every other rigid-to-rigid clearance: the largest tolerance Peli publishes (0.76)
rounded up. 2.0 for a web of case wall between two holes and 3.0 for a hole's gasket band to the edge of a plate
sealed on a gasket, the connector plate and the RF entry plates, every screw hole included (INFERRED: twice the
rigid minimum, and one and a half times the 2.0 gasket). For a cable bundle between two rigid parts, 2.0 of free
width or height, which its ties share (the rigid minimum on each side); every cable bent at R 12.5 or more
(`ASSEMBLY.md:108`, `:134`). 1.4 of thread engaged, two pitches of M4 (INFERRED). Zero where the requirement is a
condition rather than a gap: a nut fully on its thread, a screw passing its hole, a screw's tip inside its plate, a
washer or a head fully on the face it bears on, a washer's seal over its hole, a bearing face on Peli's flat floor,
a leg's pad fully under the frame's ring, the plate's underside above the shoulder, a cable inboard of an obstacle
before it meets it, a bundle off the dock strip, two cables of one bundle side by side.

**Verdicts (the review's rule).** The review of 26 September 2026 (sources, above) sets the rule this document
follows. Peli's geometry and the tolerances a source states are the design basis, and a margin whose tolerances are
not specified is unknown. An allowance is **stated** when a source gives it: the frame sheet's +-0.76, a maker's
sheet, the kit's own drawing tolerances, or the class a pick is bought to (section 6 lists each class). It is
**unstated** when no source gives it:
- every allowance on Peli's case, since the drawing says only "typical industry-standard tolerances apply";
- the frame's ring and skirt, which the sheet does not dimension;
- every build allowance: placement by hand, marking from the template, the frame's centring, the legs' locator, a
  bundle's ties, a gasket's compression and board bow;
- the arrestor's .XX lengths, whose drawing marks every dimension for reference only, and the installed height of its
  O-ring, which the drawing shows but does not dimension.

Each row of section 3.2 carries one verdict, which `frame_seat.py` prints for every row it computes (M9 and M20 are
statements, judged in the table):
- **MET**: at or above its minimum at the linear worst case, and still there with every unstated allowance in its
  chain taken twice (the column "Worst, unstated x2"). The factor is the session's sensitivity test, not a tolerance:
  a row that survives it does not hinge on the number assumed for what no source states.
- **OPEN**: one of two cases.
  - It meets its minimum at the worst case but not with the unstated allowances doubled.
  - Something no held source gives decides it: a TBD contributor, or a pick whose class admits parts on both sides
    of the minimum.

  An OPEN row gives its computed bound and what closes it (section 7).
- **NOT MET**: below its minimum at the worst case, with nothing still to be picked that could lift it.

MET is a verdict on the design basis only. It says the drawings should leave room; it does not say that a part fits,
that a joint seals or that a blind-mate aligns. Those are shown only on hardware (sections 5 and 7).

## 2. The case, source by source (deliverable 1)

### 2.1 Inside dimensions

| Where | Drawing 1451-931 | STEP (base #1321, #1193/#1922, #172/#1851, lid #410, #1467, #1744, #736) | Web page (capture 29 Mar 2026) | Worst used, and for what |
|---|---|---|---|---|
| Floor, Z 0 | not dimensioned | flat floor 343.28 x 228.98 (#1321, bounded by the fillet tangents X +-171.64, Y +-114.49); the drafted wall planes meet Z 0 at 373.94 x 259.64 | none | flat floor less the allowance, 342.52 x 228.22, for floor items |
| Z 2.5, on the fillet | | 360.39 x 246.09 (this is appendix 32.42's "360 x 246 at the floor") | | not used |
| Z 15.32, fillet tangent | **375 x 261**: `_D_5` measures 375.01 at sheet y 100.40 (Z 15.32) in section B-B, `_D_3` 260.71 at Z 15.32 in section A-A | 375.01 x 260.71 | interior 372.4 x 260.1, **height not stated** | web 372.4 x 260.1 for the pack's east corner (M4a) |
| Z 54.5, mid-height | | 377.75 x 263.45 | | |
| Z 59 (the arrestors' axis, C2) | | 378.06 x 263.76 | | |
| Z 88 (jacks as coded) | | 380.09 x 265.79; DXF B-B inner at +-190.04, A-A at +-132.89 | | |
| Z 101.04, shoulder | | 381.00 x 266.70 below it; the rim zone above it: 382.02 x 267.72 at the shoulder to 382.58 x 268.28 at the rim (#850, #1508, #1324, #1689) | | the allowance, for the face plate edge (M8) and the shoulder's height (M8z) |
| Lid, at the parting plane | | 373.88 x 261.87 (#410/#540, #1467/#1744; in the lid's own model the cavity sits 1.15 mm off centre toward one long wall, INFERRED to hold when closed) | | |
| Lid, 37 to 39 mm above the parting line | **371 x 259**: `_D_4` measures 371.15 at sheet y 144.68 (39.19 above the parting line) in B-B; `_D_2` 259.26 in A-A at a similar height | 371.16 x 259.27 at 39.19 | | |
| Lid, flat ceiling | | 346.16 x 231.86 (#736), R 16.26 fillets to the walls | | for the lid tray (C5) |

The web page's interior (372.4 x 260.1) is smaller than Peli's CAD base interior at every height above Z 15.3
and larger than the lid's at 39 mm. Applied at the frame's height it would leave Peli's own frame (378.4 x 263.1)
no room to fit, so it is used as a worst case only where a smaller interior hurts a margin and does not
contradict Peli's parts (the pack's east corner).

### 2.2 Depths

| Dimension | Drawing | STEP | Web page | Tree | Worst used |
|---|---|---|---|---|---|
| Base: floor to the rim face | 109 (`_D_7`: 108.97 on the sheet) | **108.97** (#1321 at 0.000 to #1637 at 4.290 in) | bottom depth 4.37 in = 111.0 | 109.4 (`panel1450.py:26`, `scene.py:19`); not reproduced by any Peli file | 108.97 -0.76 (INFERRED allowance) for anything referenced to the rim |
| Lid: parting line to the inner ceiling | 45 (`_D_6`: 45.47) | 45.47 (#712 to #736) | lid depth 1.75 in = 44.45 | 45.5 | **44.45** (web) for the space above the face |
| Floor to the lid's inner ceiling | 154 (`_D_8`: 154.43) | 108.97 + 45.47 = 154.44 | total depth 6.12 in = 155.4 | "154.9 to the closed lid's top" (appendix 32.42): the 154 is the inner ceiling, not the lid's top | 152.66 (rim 108.97 -0.76, plus the web lid 44.45) |
| Exterior | 411 x 329 | envelope block only | 417.6 x 330.2 x 173.2 | 411 x 329 | not load-bearing |

### 2.3 Walls, fillets, ribs, rim

| Feature | Peli figure | Source | Status |
|---|---|---|---|
| Wall draft | 2.0 degrees on every inner wall (normal 0.9994, 0.0349) and on the outer skin | STEP #1193, #1922, #172, #1851; DXF #7866 lines (187.51, 15.32) to (190.50, 101.04) inner and (192.84, 15.14) to (195.73, 97.91) outer | VERIFIED |
| Floor fillet | **R 15.88** (0.625 in) on all four floor edges, spherical at the corners; it leaves the flat floor at X +-171.64 and Y +-114.49 (15.3 mm inboard of the wall line) and meets the wall at **Z 15.32** | STEP cylinders #355, #1295, #1211, #2244 and spheres #912, #1645, #1904, #1994; DXF #7866 arc r 15.87 about (171.64, 15.88) | VERIFIED. The tree reads "about 10" (`case_wall_cutouts.py:31`) |
| Vertical corners | R 15.88, drafted | STEP #241, #1024, #595, #1345 | VERIFIED |
| Wall thickness at the jack line | **5.34** on the end walls (inner 190.04, outer 195.38 at Z 88) and **5.33 to 5.34** on the long walls (A-A at Z 50 to 88), constant with height since both faces draft 2 degrees | DXF #7866 (B-B: the end walls, cut at a Y the hatch shows as plain wall, 188.72 at Z 50, so clear of the ribs at Y 0 and +-76.2) and #7590 (A-A: the long walls at X +87.34, the cut line #3130) | VERIFIED at those sections; elsewhere INFERRED the same |
| Outer bottom radius | r 21.21 about the fillet centre; the outer wall is flat from Z 15.14 (end walls) and about Z 15.9 (long walls) | DXF #7866, #7590 | VERIFIED |
| Outer rim flange | starts at **Z 97.9** and stands to X 205.74 at the rim (about 10.4 beyond the wall skin) | DXF #7866 (arcs about (198.21, 97.82) and (202.98, 98.93)) | VERIFIED |
| **Inner ribs** | **15** tapered half-round ribs, tops at **Z 84.58**, running out at Z 26.42: six on the end walls at **Y 0, +-76.2** (both ends); five on one long wall at **X 0, +-76.2, +-152.4** (STEP z -132.78) and four on the other at **X +-76.2, +-152.4** (STEP z +132.78); which long wall carries X 0 is INFERRED to be the front (the wall with five in B-B, whose cut looks at the front). Proud of the wall 0.76 at the top, 0.65 at Z 76, 0.31 at Z 50; half-width on the wall 0.76 to 0.91 | STEP cones r 0.03 in with a 0.0218 rad half-angle (two half-cone faces each, e.g. #229 and #950 at X 0) and 15 up-facing top caps: end walls #29, #609, #957, #1035, #1784, #1991; STEP z -132.78 #28, #1504, #1876, #300, #1109; STEP z +132.78 #1118, #1751, #1016, #1572 | VERIFIED geometry. The tree's ribs at X -170, -95, -18, +60, +137 (`case_wall_cutouts.py:16`, `:29`; `ASSEMBLY.md:34`) are not in any Peli file |
| Outer features on the end walls | elliptical features centred **Y 0 and +-79.0, Z 92.4**, about 6.1 wide and 8.9 tall (semi-axes 3.05 x 4.47) | DXF end view (ellipses at sheet (390.4, 261.41), (364.0, 261.41), (416.6, 261.41); feet line at sheet y 227.815 = Z -8.38 from #7866) | positions VERIFIED; whether they stand proud or are recessed is not in the file, INFERRED as the "nubs" of `case_wall_cutouts.py:144` (which places them at +-83.5 on the jack line) |
| **Back wall outside** | the hinge fairings at the parting line: bases (sheet y 482.693) from **\|X\| 58.93 to 181.58** on both sides, outer faces 13.97 further out (sheet y 487.350, which the end view shows at about Y 164) from \|X\| 72.90 to 167.61; between them only the rim-flange line, to \|X\| 57.15. At X +87.34 (section A-A, inside the east fairing's span) the back wall is plain from the outer bottom radius to **Z 93.57**, with the hinge lug above it. The end view shows back features reaching Y 148.41 from Z 15.88 and Y 164.05 from Z 30.49, and a full-height band 3.05 proud of the skin, at X positions no view gives | DXF top view #4931, #4966, #4983, #4985, #4991, #4992, #5071, #5107, #5116; cut line #3130; A-A #7590; end view #7018, #7072, #7105, #7106, #7110, #6704 (`dxf_backwall.out`) | positions VERIFIED; the fairings' extent below the parting line between \|X\| 58.93 and 87.34 is in no view, so C3 keeps inside \|X\| 57.0 |
| Shoulder and rim zone | an up-facing ledge 0.51 wide at **Z 101.04**, then 382.0 x 267.7 widening to 382.6 x 268.3 at the rim face **Z 108.97**; the tongue for the lid seal stands outboard of the rim face (X 195.56 to 201.96, to Z 114.56, bead to 115.85) | STEP #776, #850, #1637; DXF #7866 | VERIFIED |

### 2.4 The 1450PF frame

| Dimension | Sheet 1453-314-000 rev A | STEP | Worst used |
|---|---|---|---|
| Height | 17.5 (.69) | 17.52 (#1 at z -8.76 to #5527 at +8.76), plus the raised lettering 0.51 (z 8.76 to 9.27) | 17.52 +-0.76 |
| Outline | 378.4 x 263.1 | outer face drafted 2 degrees out going up (#3683, #7251): 378.36 x 262.54 at the skirt's bottom edge, **378.96 x 263.14 at its widest (the mid-plane, z 0)**, 378.58 x 262.76 at the gasket step (#6617, #7853) | +-0.76 |
| Window | 349.7 x 233.8 | 349.66 x 233.82 (#1928, #1818), through the ring; corners R 6.35 | -0.76 for the lift-out; +-0.38 per side for the legs' locator |
| Ring (window to outer edge, top face down to its underside) | | **9.39** thick (top z 8.76 to the flat underside #1703 at z -0.63, which spans the whole ring) | 9.39 +-0.76 (INFERRED) |
| Skirt | | 8.13 tall below the ring, inner 366.68 x 250.84 (#4475, #3645; corners R 17.53, #494), 5.84 thick at the bottom | 8.13 +-0.76; inner face +-0.38 per side (INFERRED) |
| Gasket step (o-ring seat) | assembly detail | top flange 368.70 x 252.88 (#3095, #3162) above a step 3.30 under the top (#1488 at z 5.46); outside it, the channel to the case wall is about 6.1 wide in X and 6.9 in Y with the frame on the C6 legs | |
| Inserts | 10 x 5.18 +-0.13, 1 degree draft, on 358.1 x 242.3 | 10 bores through the ring at (+-179.07, +-75.95), (0, +-121.16), (+-139.45, +-121.16) | pattern +-0.38 per side |
| Frame mounting screws | assembly detail | four horizontal 3.66 holes through the skirt, 4.85 below the frame's mid-plane (3.91 above its bottom): **front pair X +-113.03, back pair X +-98.04** (#530, #1357, #3347, #4481 and twins) | the tree reads "four 3.66 mm slots at (+-113, +-128.4)" (appendix 32.42) |
| Notches | | two, 12.7 wide and 5.08 deep, in the front skirt's bottom edge at X +-139.19 to 151.89 | |
| Lettering "1450 FRONT" | | 0.51 high on the top face, **X -108.99 to -68.80, Y -123.64 to -118.32** (103 faces above z 9.0) | C1's relief pocket |

### 2.5 How Peli mounts the frame and a panel

The mounting instructions, verbatim:
1. "The frame must be correctly oriented prior to installation. Check for the model identifier and the word
   'front' (i.e.1450 front)... (If the frame is installed in reverse, the mounting screws will protrude through
   the case as they are oriented to match the external ribs)."
2. "To install the brass inserts, place the frame face down (model identifier facing down, see step 1). Place the
   non-shoulder small end of the insert into the hole and push in with a Phillips screwdriver until fully seated
   on the shoulder."
3. "To secure the frame to the case, install the frame into the case until **fully seated on the internal
   ribs**. Next, insert a mounting screw... press firmly as you turn the screwdriver to start self-tapping."
4. "Install the o-ring into the channel between the frame and the case... Install your custom panel. **Your panel
   should completely cover the o-ring** for maximum fluid and dust resistance. Install the screws (into brass
   inserts) by hand, DO NOT APPLY PRESSURE... Excess pressure will push the brass inserts back out the other side."

What follows from Peli's figures (INFERRED where marked):
- Peli means the ribs to set the frame's height. At the current moulding they cannot (section 2.7): the frame STEP
  is dated 2015 and the base STEP 2025, and in Peli's own envelope the frame's bottom edge lands 0.012 mm onto the
  end-wall ribs and misses the long-wall ribs. A panel of about 6.9 mm on the nominal rib seat would be flush with
  the rim, consistent with "flush with the rim" for most panels (INFERRED).
- The panel lies **on** the frame: it covers the o-ring, which sits in the channel between the frame's top flange
  and the case wall; its screws go in from above. The inserts enter from the frame's underside and stop on their
  shoulder there, so a screw from above pulls the shoulder against the ring (the strong direction) and a screw from
  below pulls the insert away from its shoulder, held only by a press fit Peli designed to be pushed in by hand
  (INFERRED).
- The frame's own four screws self-tap from inside the skirt into the long walls; their heads sit on the skirt's
  inner face at Y +-125.42.

### 2.6 Records in this tree that Peli's files do not support

| Record | Where | Peli's files |
|---|---|---|
| base 109.4 deep, rim at 109.4 | `panel1450.py:26`; `scene.py:19`; appendix 32.41 table (line 2598) | 108.97 (STEP #1637; drawing `_D_7`) |
| "panel lip 8 mm below its top face" | appendix 2603; `panel1450.py:26` | the ring is 9.39 thick and has no up-facing ledge; 8.13 is the skirt's height |
| "floor 371 x 259 at the rim" | `case_wall_cutouts.py:15`; appendix 2611; `scene.py:21` | 371 x 259 is the **lid** interior 37 to 39 mm above the parting line; the base is 375 x 261 at Z 15.3 and 382.0 x 267.7 in the rim zone |
| floor fillet about 10 mm | `case_wall_cutouts.py:31`, `:74`, `:92` | R 15.88, tangent at Z 15.32 |
| five inner ribs at X -170, -95, -18, +60, +137 | `case_wall_cutouts.py:16`, `:29`; `ASSEMBLY.md:34` | fifteen ribs at X 0, +-76.2, +-152.4 and Y 0, +-76.2 (section 2.3) |
| hinge clusters outside at X -167 to -74 and +58 to +160 | `case_wall_cutouts.py:16` | the fairings are symmetric: bases from \|X\| 58.93 to 181.58, outer faces \|X\| 72.90 to 167.61 (section 2.3) |
| nubs at Y 0 and +-83.5 on the jack line; frame-leg bosses at Y +-76 near the rim | `case_wall_cutouts.py:139`, `:144` | outer features at Y 0, +-79.0, Z 92.4; the inner ribs at Y +-76.2 end at Z 84.58 |
| frame skirt at Z 100 to 109 | appendix 2611; `case_wall_cutouts.py:75`, `:139` | the frame rests somewhere from Z 54.5 to 85.3 on Peli's ribs (section 2.7); on the C6 legs at 84.38 to 87.62 |
| panel clamped under the ring from below with M3 screws and a PORON ring | appendix 2611; `ASSEMBLY.md:29` | panel on the frame over Peli's o-ring; 6-32 brass inserts |
| 46.5 mm between the plate and the lid | `ASSEMBLY.md:66` | as coded, 53.04 at Peli's nominal figures; under C1 on the legs, 47.92 nominal and 44.39 worst |
| east pack pocket X +120 to +178 | `ASSEMBLY.md:48`; appendix 32.62 | X 178 is not a Peli surface; the pocket is bounded by the fillet and the wall (M4a, M4b) |
| connector plate screws M4 x 16 | `ASSEMBLY.md:34` | head washer, plate, gasket, wall, washer and an M4 Nyloc (DIN 985 height 5.0, INFERRED) take 16.94 on the as-coded 3 mm plate: the nylon ring is not reached; C3's 5 mm plate, with a bonded sealing washer of 1.5 (INFERRED) under the head, takes 19.64 and M4 x 25 |

### 2.7 What can stop the frame going lower, and where it then rests

Every surface that could meet the 1450PF on its way down was checked against the STEP faces (`frame_seat.py`,
part A):

| Feature | Can it carry the frame? | Figures |
|---|---|---|
| Rib top caps (15, Z 84.58) | only by a knife edge | at nominal the end-wall ribs reach 0.012 mm under the frame's bottom edge (189.18 against the rib's innermost 189.168) and the long-wall ribs miss by 0.748. A rib stands 0.76 proud of its wall, so the edge must land in a band 0.76 wide; the frame outline (+-0.38 per side) and the case interior (+-0.38 per wall, INFERRED) move it by up to 0.76 each way, so no frame size is caught by the ribs across both |
| Rib flanks (cones, 1.25 degrees) | yes, as a wedge, at an undefined height | the frame's skirt flares 0.306 over its lower 8.76 (2 degrees, #3683) and a rib widens inward 0.0218 per mm going down, so a frame too small for the rib tops slides down until its skirt, or below 8.76 its widest line, meets the flanks |
| Drafted walls | far below the ribs at nominal sizes; near the rib tops only for a large frame in a small case | the frame's widest line (378.96 x 263.14, z 0) meets the end walls with its bottom at Z 63.12 and the long walls at 41.35 (nominal sizes); with a frame at +0.76 in a case at -0.76 the end walls wedge it at Z 85.04 |
| Vertical corners | no | case R 15.88 (#595) against the frame's R 16.51 (#3257): 2.26 on the diagonal, more than at the sides |
| Shoulder (0.51 ledge at Z 101.04) | no | the cavity below it is 381.00 x 266.70; the frame's widest at +0.76 is 379.72 x 263.90, clear by 0.26 and 1.02 per side at the worst |
| Rim face and the lid's seal tongue | no | nothing on the frame reaches outboard of 378.96 x 263.14 (+0.76: 379.72 x 263.90); the rim zone is 382.02 x 267.72 |
| The frame's own lip, ring and flange | no | the ring and the top flange face inward (window 349.66 x 233.82, flange 368.70 x 252.88); the frame has no outward lip |
| O-ring channel and gasket step (#1488) | no | the step is on the frame; the o-ring goes in after the frame's screws (instruction step 4) |
| Peli's four self-tapping screws | they fix the frame where it already rests | driven horizontally from inside the skirt |

Where the frame then rests, lowered as Peli instructs (geometric, sharp edges; `frame_seat.py` part B):

| Frame outline | Case | Rib tops | Frame bottom Z | Face top, plate on the frame |
|---|---|---|---|---|
| +0.76 | nominal | +0.76 | **85.34** (highest) | 105.86 |
| +0.76 or nominal | nominal | nominal | 84.58 | 105.10 |
| -0.10 | nominal | nominal | 83.46 | 103.98 |
| -0.20 | nominal | nominal | 82.00 | 102.52 |
| -0.40 | nominal | nominal | 79.08 | 99.60 |
| -0.76 | nominal | nominal | 72.70 | 93.22 |
| -0.76 | nominal | -0.76 | 71.94 | 92.46 |
| -0.76 | +0.76 | nominal | 55.27 | 75.79 |
| -0.76 | +0.76 | -0.76 | **54.51** (lowest) | 75.03 |

A moulded edge does not hold 0.012 mm: with an edge allowance of only 0.10 mm (INFERRED) the nominal frame rests at
Z 82.00, not on the rib tops. The monitor (M1 needs the worst face top at or above 103.15) and the lid (M2, with the
plate's 2.0 mm rebate, needs it at or below 109.11) leave a window 5.96 mm wide. Peli's rib seat spans 11.88 mm on
the frame sheet's tolerance alone, 12.64 with the rib-top allowance and 30.83 with every case allowance. **No face
mounting referenced to where the frame comes to rest can hold M1 and M2 together, so the frame gets a designed
height (C6).**

With the C6 legs (`frame_seat.py` part C) the frame's bottom sits at **86.00** nominal, 84.38 to 87.62 over the
floor, leg and skirt allowances, and the face top at **106.52**, 104.77 to 108.27, inside the window by 1.62 below and
0.84 above. The legs set the lowest the frame can go. Only an oversize frame can rest higher than the legs put it,
on the rib tops (at most Z 85.34, when the legs sit at their lowest and the feet then clear the floor by at most
0.96) or wedged between the end walls (85.04), and both are inside the legs' own range. The plate's underside is then
at least at Z 101.90, and the shoulder, carrying the case's height allowance like every other case height, stands
between 100.28 and 101.80: at the stated allowances the plate's rebated edge faces the rim zone at every seat (M8z,
0.10 at the worst; OPEN, since that 0.10 rests on the case's height allowance, which Peli does not state).

## 3. Margins at Peli's figures (deliverable 2)

### 3.1 The face: monitor body over the Compute Module 5 heatsinks

The tightest chain in the kit. Body bottom = face top - 28.66 (`panel1450.py:44`); heatsink top = B's top
copper + 21.0 (`panel1450.py:23`, `:36`). Floor 2.0 mm.

| Arrangement | Face top Z | Nominal | Worst | RSS low | Verdict |
|---|---|---|---|---|---|
| (0) as coded: 101.4, VHB pads not in the chain (`z_budget.py` prints the +2.24) | 101.40 | +2.24 | +0.95 | +1.66 | NOT MET at the worst; the datum is not Peli's |
| (A1) plate under the ring (as coded), frame top flush with the rim, VHB as written (`ASSEMBLY.md:47`) | 108.97 - 9.39 - 0.53 PORON = 99.05 | -1.21 | -3.62 | -2.37 | NOT MET |
| (A2) plate under the ring, frame on the rib tops | 84.58 + 17.52 - 9.39 - 0.53 = 92.18 | -8.08 | -10.49 | -9.24 | NOT MET |
| (B) plate on the frame, frame resting where Peli's ribs put it (section 2.7) | 75.03 to 105.86 | -25.23 to +5.60 across the seat range | | | NOT MET |
| **(C1 on C6) plate on the frame, frame on the setting legs, VHB lifting the stack** | 94.13 + 9.39 + 3.00 = **106.52** | **+6.26** | **+3.62** | **+5.09** | OPEN: three contributors TBD (below) |

C1 on C6, floor up. Face side: the floor under a leg (+-0.76 against the floor under the stack, INFERRED), the leg's
pad 94.13 (+-0.10, drawing), the frame's ring 9.39 (+-0.76, INFERRED), the plate 3.00 (+-0.13, INFERRED): 106.52,
104.77 to 108.27. Board side: VHB 1.1 (+-0.11), dock strip 1.6, blind-mate gap 13.4, A 1.6, bay 31.3, B 1.6 (each
laminate +-0.16), heatsink 21.0, bow 0.3: heatsink top 71.60 nominal. Worst case: 6.26 - (0.76 + 0.10 + 0.76 +
0.13) - (0.11 + 3 x 0.16 + 0.30) = 3.62. RSS: sqrt(0.76^2 + 0.10^2 + 0.76^2 + 0.13^2 + 0.11^2 + 3 x 0.16^2 + 0.30^2) =
1.17, so 5.09. The floor term replaces the rib-top term the first issue carried: the frame is referenced to the same
floor as the stack, through a part the kit makes. A leg's placement in plan does not enter this chain: its foot
stays on the flat floor at the worst (M21a, M21b).

TBD, left out of every figure above and each widening them: the Xenarc body's 28.66 (read from its drawing at 400
dpi, no tolerance), the heatsink's 21.0 (from the render scene, not a Raspberry Pi drawing), the gap and bay spacers
(no parts named), the Xenarc steel rear frame's drawing (owed). The worst figure keeps 1.62 mm over the 2.0 floor
for them. **M1 is therefore OPEN.** Its chain also carries 1.82 mm of unstated allowances (the floor under a leg,
the frame's ring and the board's bow), and with those taken twice it keeps 1.80, below the floor, before any TBD is
counted. It closes on the Xenarc's drawing, a Raspberry Pi drawing of the heatsink and the named spacers (lookups),
and then on T4 with the real monitor and heatsink on the mock-up (section 7).

Every other deep face part rises with the plate by the same amount: face top 106.52 against 101.4 is +5.12, less the
1.1 by which the VHB pads lift B16, so **+4.02 net** on each clearance that `clearance_report()` in `panel1450.py`
prints, and the PA flange over the fans goes from 9.0 to 13.0 mm.

### 3.2 All case-dependent margins

"As designed" is the tree at main `29f00554` (for M1, M10 and M14a with the frame where Peli puts it); "chosen" is
C1 on the C6 legs with C2 to C5. Every chosen figure is printed by `frame_seat.py` (parts D to G and the table), and
so are the column "Worst, unstated x2" and each verdict (section 1, Verdicts). For an OPEN row the last cell says
what the row rests on and which check of sections 5 and 7 closes it.

| # | Margin | Min | As designed: nominal / worst | As designed | Chosen: nominal | Worst | RSS low | Worst, unstated x2 | Chosen |
|---|---|---|---|---|---|---|---|---|---|
| M1 | Monitor body over the heatsinks (3.1) | 2.0 | +2.24 / +0.95 on 101.4; -8.08 / -10.49 on the rib tops | NOT MET | +6.26 | +3.62 | +5.09 | +1.80 | OPEN: three contributors TBD (3.1); the floor, ring and bow allowances; T4 |
| M2 | Rebated plate band below the rim, under the lid's wall (lid opening 373.88 x 261.87 against the rim zone's 382.0) | 1.0 | n/a: the plate sits inside the skirt | n/a | +4.45 | +1.84 | +3.12 | -0.44 | OPEN: the floor, ring and rim heights; T3, T9 |
| M2b | Full-thickness face (368.0 x 253.0) inside the lid's opening at the parting plane (X 186.94; the nearer long wall 129.79 in Y), so no full-thickness edge sits under the lid's wall | 1.0 | n/a | n/a | +2.94 in X (+3.29 in Y) | +1.25 | +2.08 | +0.29 | OPEN: the lid's cavity and its place on the base; T3, T9 |
| M3 | Space under the QMX tray (28.0, `v2/cad/lid_bracket_qmx.py:13-16`) for the face parts; lid STEP 45.47, web 44.45 in the worst | 1.0 plus the parts (TBD) | +25.04 / +23.26 (`ASSEMBLY.md:66` states 46.5 above the face) | MET | +19.92 | +16.39 | +18.25 | +14.11 | OPEN: the button and lever heights TBD; T9 |
| M4a | Pack block's east corner (4S3P 18650, 56.65 x 133.5 x 38.1 wrapped, A06, west face at X 122.0, 2.0 from board A's edge `gen_pcb_a.py:16-17`) to Peli's R 15.88 fillet | 1.0 | +3.71 / +2.85 | MET | +3.71 | +1.85 | +2.39 | +0.85 | OPEN: the pack placed by hand; T4 |
| M4b | Pack block's east face to the east wall | 1.0 | +9.68 / +8.38 | MET | +9.68 | +7.38 | +8.04 | +6.38 | MET |
| M4c | Pack block's east face (X 178.65) to the east RF entry plate's bottom screw heads inside (Z 35.65 to 45.65, inner face X 184.51) | 1.0 | n/a | n/a | +5.86 | +3.18 | +4.18 | +1.80 | MET |
| M5 | Pack group (block + board P + 2 = 205.5) in Y: as designed on the flat floor, chosen between the east legs (inner faces at \|Y\| 106.4, each placed within 0.88), per side | 1.0 | +11.74 / +11.36 | MET | +3.65 | +1.77 | +2.52 | +0.27 | OPEN: the pack placed by hand, the legs' locator; T4 |
| M6 | Pack top under B16's underside (A06 3.32 at its pessimistic base; chosen adds the 1.1 VHB lift) | 1.0 | +3.32 / +2.56 | MET | +4.42 | +3.66 | +3.66 | +2.90 | MET |
| M7 | Stack lift-out through the frame window, per side in X (B 330 x 200, `panel1450.py:22`; 16.91 in Y) | 1.0 | +9.83 / +9.45 | MET | +9.83 | +8.25 | +8.74 | +7.05 | MET |
| M8 | Face plate edge to the case: as designed in the skirt (366.68 x 250.84); chosen 377.2 x 263.0 against the rim zone, frame centred (C6), the plate floating 0.63 on its 6-32 screws | 1.0 | X +0.59 / +0.21, Y +0.67 / +0.29 | NOT MET | X +2.41, Y +2.36 | X +1.10, Y +1.05 | X +1.64, Y +1.59 | X +0.52, Y +0.47 | OPEN: the case's width, the frame's centring; T3 |
| M8f | Every 6-32 (3.505 at the largest) passes its 4.6 plate hole with Peli's inserts at the pattern's worst: its clearance 0.55 against the pattern's 0.38 per side and the hole's own 0.10 | 0 | n/a: M3 from below into Peli's 6-32 inserts | n/a | +0.55 | +0.07 | +0.15 | +0.07 | MET |
| M8h | 6-32 pan heads (6.86 across, ASME B18.6.3 class, INFERRED) on the full-thickness face: the end inserts to the rebate line in X (the long-wall inserts 1.91 in Y), the screw anywhere in its 0.63 float | 0 | n/a | n/a | +1.50 | +0.77 | +0.86 | +0.77 | MET |
| M8z | Plate underside above the shoulder, so the plate edge faces the rim zone and not the 1.02 narrower cavity below it (pad 94.13 + ring 9.39 against the shoulder 101.04 +-0.76) | 0 | n/a: the plate sits inside the skirt | n/a | +2.48 | +0.10 | +1.16 | -2.18 | OPEN: the shoulder's and the ring's heights; T2 |
| M9 | Peli's frame-screw heads against the as-coded plate edge (No. 6 pan head about 2.4 tall, INFERRED) | 1.0 | overlap 1.73 | NOT MET | n/a: the plate lies above the ring | | | | MET, a condition: the plate lies on the ring's top face, and the heads sit under the ring at \|Y\| 123.0 (the skirt's inner face 125.42 less the head's 2.4), 6.1 outboard of the window's 116.91 |
| M10 | Highest part inside an end wall below the frame skirt: as designed the 132170's inner lock washer (r 5.10); chosen the RF entry plate's top screw heads on their sealing washers (Z 77.35 + 5.0) | 1.0 | jacks at Z 88: -8.52 with the frame on the rib tops (+0.70 only with the frame hung to suit the as-coded plate) | NOT MET | +3.65 | +1.73 | +2.53 | -0.09 | OPEN: the floor, skirt and marking allowances; T2, T6 |
| M11 | Inside hardware bearing on an end wall to its ribs at Y 0, +-76.2: as designed the 132170 washers; chosen only the entry plate's screw heads bear there (the arrestor holes cut a rib where they cross it) | 1.0 | at Y +-72: -1.66 / -2.04 | NOT MET | +17.89 | +17.21 | +17.41 | +16.53 | MET |
| M11a | Wall web between neighbouring bulkhead holes: chosen 27 at a 31 pitch | 2.0 | the ruled arrestors had no place | OPEN | +4.00 | +3.40 | +3.40 | +2.80 | MET |
| M11b | Wall web between an arrestor hole and an entry-plate 5.0 screw hole (the screw at \|Y\| 100, Z 77.35, beside the west wall's +-93 site) | 2.0 | n/a | n/a | +3.64 | +3.04 | +3.04 | +2.44 | MET |
| M11c | Gasket band from a wall hole to the entry plate's edge, the arrestor holes and the 5.0 screw holes alike | 3.0 | n/a | n/a | +3.60 | +3.00 | +3.18 | +2.40 | OPEN: holes and plate marked by hand; T6 |
| M11d | Entry-plate screw tips inside the plate's outer face, where an arrestor body lies over the screws at \|Y\| 100 beside the west wall's +-93 sites: M4 x 12 on a 1.5 washer, through the wall (5.34) and the gasket (1.5) into the 6.0 plate; the plate's +-0.20, the screw's +-0.35 and the washer's +-0.10 in the chain with the wall's and the gasket's | 0 | n/a | n/a | +2.34 | +0.43 | +1.34 | -0.83 | OPEN: the wall's thickness, the gasket; T5 |
| M11e | Every entry-plate M4 (3.98 at most) starts in its 5.0 wall hole: its float, 0.51, against the hole's marking (0.3) and the tapped hole's place (0.10), the method of M8f | 0 | n/a | n/a | +0.51 | +0.11 | +0.19 | -0.19 | OPEN: the hole marked by hand; T6 |
| M11f | The sealing washer's rubber face (8.0 across or more, INFERRED class) covers its 5.0 wall hole with the screw anywhere in its float (0.58, the smallest M4) | 0 | n/a | n/a | +1.50 | +0.92 | +0.92 | +0.92 | MET |
| M11g | Entry-plate screws' thread engaged in the 6.0 plate (the chain of M11d without the plate's own tolerance) | 1.4 | n/a | n/a | +3.66 | +1.95 | +2.68 | +0.69 | OPEN: the wall's thickness, the gasket; T5 |
| M12 | End-wall features at Y 0, +-79.0 (lowest Z 87.93): as designed the 132170's outer hex (r 5.48); chosen the entry plate's top edge | 1.0 | at Y +-72, Z 88: overlap 1.53 in Y | NOT MET | +4.48 | +3.42 | +3.66 | +2.36 | MET |
| M12b | Entry plate's Y edge on the end wall's flat outer skin (flat to \|Y\| 115.15 at the plate's lowest Z, the outer corner R 21.22 INFERRED concentric with Peli's inner R 15.88) | 1.0 | n/a | n/a | +5.05 | +4.27 | +4.55 | +3.59 | MET |
| M13 | Bulkhead clamp: as designed the 132170's stack against its 6.5; chosen the arrestor's nut fully on its thread. Of its .47 in (11.94, +-0.51 unstated) from the body's face, the O-ring takes 0.32 +-0.32 (drawn 0.63 free), the plate 4.5 under the 26.0 x 1.5 spot-face on its back (+-0.10), then a nut and washer of 5.0 | 0 | wall 5.34 + O-ring about 0.75 compressed (INFERRED): +0.41 / -0.35 | NOT MET | +2.12 | +1.20 | +1.52 | +0.38 | OPEN: the O-ring's height, drawn but not dimensioned; met with the thread's allowance doubled for one installed up to 1.32, more than twice its drawn height; PolyPhaser's dimension, T11 |
| M13b | The arrestor's nut and washer (5.0, on the spot-face's floor 4.5 from the plate's outer face) inside the wall hole's depth (plate 6.0, gasket 1.5 and wall 5.34) | 0 | n/a | n/a | +3.34 | +1.78 | +2.40 | +0.52 | MET |
| M13c | The arrestor's nut and washer (24.0 across) inside the 27 wall hole, radial, the arrestor anywhere in its 0.32 float | 0 | n/a | n/a | +1.50 | +0.48 | +0.96 | -0.12 | OPEN: holes and plate marked by hand; T6 |
| M13d | The arrestor's nut and washer (24.0 across) inside the 26.0 spot-face, radial, the arrestor anywhere in its float and the spot-face within 0.10 of its hole | 0 | n/a | n/a | +1.00 | +0.58 | +0.67 | +0.58 | MET |
| M14a | Highest part inside the back wall below the frame skirt: as designed the top-row M4 nuts, chosen D's body in its 29 mm hole (top Z 81.5; the top screws' inside washers reach 80.5) | 1.0 | as coded Z 82 + 4.5: -1.92 with the frame on the rib tops | NOT MET | +4.50 | +2.58 | +3.38 | +0.76 | OPEN: the floor, skirt and marking allowances; T2, T6 |
| M14b | Connector plate's bottom edge above the outer bottom radius (flat from about Z 15.9 on the long walls) | 1.0 | as coded Z 13: -2.9; west screw column on the rib at X -76.2: -2.65 | NOT MET | +2.40 (Z 18.3) | +1.34 | +1.58 | +0.28 | OPEN: the case's height, the marking; T6 |
| M14c | D: the 233-370's internal lead, a right-angle (down) USB-A plug within 20.0 of the rear face, to B16's edge (section 3.3) | 1.0 | not checked in the first issue | OPEN | +8.75 | +5.93 | +6.76 | +3.22 | MET |
| M14d | C: shore DC cores, turned down within 12 of the receptacle's rear, to B16's edge | 1.0 | not checked in the first issue | OPEN | +22.30 | +20.06 | +20.98 | +17.92 | MET |
| M14e | A: the Cat 5e patch plug in the sealed RJ45 (body +-8 about the coupler's centre, INFERRED) under B16 and U51, the coupler at its float and its machined place | 1.0 | the RJ45 had no place | OPEN | +2.80 | +1.73 | +2.22 | +1.43 | MET |
| M14f | A: the patch plug's end (within 40.0 of the coupler's rear face, INFERRED) outboard of A22's edge | 1.0 | the RJ45 had no place | OPEN | +7.69 | +4.87 | +5.70 | +2.16 | MET |
| M14g | B: the USB-C lead (7.0, bent at R 28 into the case, INFERRED) under B16 and U51, the body at its float and its machined place | 1.0 | the USB-C had no place | OPEN | +7.30 | +6.17 | +6.69 | +5.87 | MET |
| M14h | B: the lead's innermost point outboard of A22's edge | 1.0 | the USB-C had no place | OPEN | +19.94 | +17.70 | +18.62 | +15.56 | MET |
| M14i | Connector plate's edge to the hinge fairings' bases (\|X\| 58.93) | 1.0 | as coded the plate spans X -83 to -29, inside the west fairing's span below a parting-line feature whose extent down the wall no view gives | OPEN | +1.93 | +1.15 | +1.44 | +0.47 | OPEN: the fairings' place, the marking; T1, T6 |
| M14j | Tightest pair on the plate's face (flanges, pod, stud, screw washers), each part at its float on its fixings and two machined places to a pair: at the worst A's and D's flanges (A's flange and the left column's two lower washers 1.19) | 1.0 | two items 36 apart, not checked | OPEN | +1.81 | +1.13 | +1.44 | +1.13 | MET |
| M14k | Tightest pair of mated connectors (A's and D's shell 15 plugs 32.51, C's shell 13 plug 29.4 from the held sheets), each at its float, two machined places to a pair: at the worst D's and F's (A's and C's 1.12, C's and B's 1.13) | 1.0 | not checked | OPEN | +1.85 | +1.11 | +1.44 | +1.11 | MET |
| M14l | Tightest wall web between two holes, screw holes included (C's and B's) | 2.0 | not checked | OPEN | +4.11 | +3.51 | +3.51 | +2.91 | MET |
| M14m | Tightest gasket band from a wall hole to the plate's edge, screw holes included (the bottom-left screw; of a connector hole, A's 3.80) | 3.0 | not checked (the previous issue's screw holes: 1.95 at the worst) | OPEN | +3.65 | +3.05 | +3.23 | +2.45 | OPEN: holes and plate marked by hand; T6 |
| M14n | Nearest face bearing on the wall inside to the X 0 rib, if the back wall carries it (F's nut) | 1.0 | n/a: the plate does not reach X 0 | n/a | +27.69 | +26.61 | +27.11 | +25.93 | MET |
| M14o | Connector plate's top below the outer rim flange (Z 97.9) | 1.0 | not checked | OPEN | +11.31 | +10.25 | +10.49 | +9.19 | MET |
| M14p | Bonded sealing washers under the plate's screw heads (10 across, INFERRED) fully on the plate, the smallest M4 anywhere in its 4.5 hole (0.33) | 0 | the previous issue's 9.0 washers came within 0.30 of the edge | n/a | +0.90 | +0.47 | +0.55 | +0.47 | MET |
| M15a | Dock strip's underside (on 1.1 pads; south edge Y -113, `gen_pcb_e.py:15`) to the front floor fillet, which reaches Z 1.1 at 5.81 past its tangent | 1.0 | +7.30 / +6.92 | MET | +7.30 | +5.92 | +6.23 | +4.54 | MET |
| M15b | Dock strip's corner pads on Peli's flat floor (edge to the tangent) | 0 | +1.49 / +1.11 | MET | +1.49 | +0.11 | +0.42 | -1.27 | OPEN: the strip placed by hand; T4, T8 |
| M16 | Rods (+-110.5, +-73) to the long-wall fillet tangents (61.14 to the end walls) | 1.0 | +41.49 / +41.11 | MET | +41.49 | +40.11 | +40.42 | +38.73 | MET |
| M17a | East jumpers' bundle, two RG-316 wide and two high (4.98), in the slot between the pack's top (Z 44.58) and the plugs' undersides (Z 54.0): free height, each plug's arrestor anywhere in its 0.32 float | 2.0 | not checked: the previous issues' M17 measured the band between B's edge and the east wall at Z 50 (23.72, 23.34 at the worst), a clearance, not a route; it is retired | OPEN | +4.44 | +2.96 | +3.56 | +1.90 | OPEN: the floor under the pack, the plate's marking; T6, T8, T10 |
| M17b | East cables under the next plug's body: a cable in the band's upper layer (its centre Z 50.535) to the body's underside (Z 54.0); the drop from the plug itself (ferrule to 16.0 from the axis at 30 degrees down, then R 12.5 to level) keeps 8.32 | 1.0 | n/a | n/a | +2.22 | +1.00 | +1.55 | +0.20 | OPEN: the ties, the marking; T10 |
| M17g | East layering under 5G MAIN, which three cables pass (IRIDIUM, ANT3, DIV), as laid out: the passing cables in the band's lower layer and its inner upper place, MAIN's own cable in the outer upper place (Z 50.535); at the class's 16.0 reach and 30 degrees it lands at Z 49.33, onto the passing cable in the outer lower place: centre distance less one cable | 0 | n/a | n/a | -1.21 | -2.43 | -1.88 | -3.23 | OPEN: best +0.00 for a reach of 13.58 or less, or 5G MAIN turned 26.5 degrees; the plug's reach and ferrule; T10 |
| M17x | East bundle's inboard column under the plugs (one cable, 2.49, inboard of the plug's cable axis; B16's underside, Z 48.57 at the worst, lies inside the band) to B16's edge (X 165), with the plug's cable axis at its inner end (X 172.63), which the class allows | 1.0 | n/a | n/a | +3.89 | -0.38 | +2.12 | -4.35 | OPEN: best +7.89 nominal, +3.62 worst with the cable axis 4.0 from the plug's inner end, met for 1.38 or more with a ferrule 2.58 across or less; the plug's axis and ferrule; T10 |
| M17c | The outermost east cable (\|Y\| 62) inboard of the legs' columns before it reaches them: from its plug's cable axis (X 176.63 at the class's limit, 179.80 at the worst) by an S-bend of the two-wide bundle, its centreline at R 13.745 so that its inner cable bends at R 12.5, into the lane, against the leg's inner face (\|Y\| 106.4) less 1.0 and the cable's radius, in Y | 0 | n/a (from \|Y\| 93: 22.32 short at nominal) | n/a | +8.68 | +1.56 | +5.23 | -2.34 | OPEN: the wall, the gasket, the O-ring, the marking, the locator; T5, T10, T11 |
| M17d | East bundle (4.98 wide) in the lane between B16's edge (X 165) and the legs' columns (X 175.40): free width | 2.0 | n/a | n/a | +5.42 | +3.44 | +4.08 | +1.94 | OPEN: the stack's placement, the locator; T10 |
| M17e | East bundle going down beyond the leg: its inner face (\|Y\| 115.25) to the leg's outer face (\|Y\| 112.4) | 1.0 | n/a | n/a | +2.85 | +1.47 | +1.84 | +0.47 | OPEN: the locator, the ties; T10 |
| M17f | East front bundle on the floor fillet beside the dock strip's south edge (\|Y\| 113) | 0 | n/a | n/a | +2.25 | +0.75 | +1.14 | -0.75 | OPEN: the strip's placement, the ties; T10 |
| M17w | West cables, leaving downward within 4.0 of the plug's inner end, outboard of B16's edge (X 165) as they fall to the floor | 1.0 | n/a | n/a | +6.38 | +2.11 | +4.61 | -1.86 | OPEN: the wall, the gasket, the O-ring, the stack's placement; T5, T10, T11 |
| M18 | Jumper plug's inner end to B16's tall parts it overlaps in Y and Z, in X (the tightest: the RockBLOCK's box at the 5G MAIN site; the LimeSDR's 11.63, the radio modules' and J_ETH's 10.63, T1's 11.13) | 1.0 | the ruled arrestors had no place | OPEN | +7.63 | +3.36 | +5.85 | -0.61 | OPEN: the wall, the gasket, the O-ring, the stack's placement; T4, T5, T11 |
| M18b | Neighbouring arrestor bodies outside (22.86 across at the 31 pitch), each anywhere in its 0.32 float | 1.0 | at the tree's 24 mm pitch 1.14 (0.54 at the worst, two holes marked from the template); at the previous issue's 20 mm, -2.86 | NOT MET | +8.14 | +7.30 | +7.47 | +7.30 | MET |
| M18c | Outermost jumper plug (the west wall's, \|Y\| 93 + 5.0) to the setting legs' inner face, where the plug's X range covers the column's, the arrestor anywhere in its float | 1.0 | n/a | n/a | +8.40 | +6.80 | +7.41 | +6.00 | MET |
| M19 | QMX tray's east edge (X 172.5, `ASSEMBLY.md:46`) inside the lid's flat ceiling edge (X 173.08) | 1.0 | +0.58 / +0.20 | NOT MET | +2.08 (C5) | +1.70 | +1.70 | +1.32 | MET |
| M20 | The frame's seat (Peli's own interface) | stated | anywhere from Z 54.51 to 85.34 on the ribs (2.7) | OPEN | bottom 86.00, 84.38 to 87.62 on the legs; the ribs or walls can only lift an oversize frame, to at most 85.34 | | | | OPEN: the legs define the seat at the stated allowances; the floor and ring allowances are unstated; T2 |
| M21a | Leg foot's bearing face on the flat floor: foot end X +-169.0 to the fillet tangent (the leg placed within 1.26 of the case's features) | 0 | new part | n/a | +2.64 | +1.38 | +1.99 | +0.50 | MET |
| M21b | Leg foot's bearing face on the flat floor: \|Y\| 112.4 to the long-wall fillet tangent | 0 | new part | n/a | +2.09 | +0.83 | +1.44 | -0.05 | OPEN: the locator, the centring; T2 |
| M21c | Leg underside relieved over the floor fillet (normal offset 2.5) | 1.0 | new part | n/a | +2.50 | +1.24 | +1.85 | +0.36 | OPEN: the locator, the centring; T2 |
| M21d | Leg column to the frame skirt's inner face, Euclidean: the column's outer-back corner (180.17, 112.4) against the skirt's R 17.53 corner arc about (165.81, 107.90); the leg moved 0.68 in X and in Y at once (locator 0.30, window 0.38), the skirt's 0.38 taken as a shift of the arc's centre (1.24 as a profile offset) | 1.0 | new part (the previous issue's column: 2.29 nominal, 0.95 at the worst) | n/a | +2.48 | +1.14 | +1.87 | +0.26 | OPEN: the locator, the skirt's face; T2 |
| M21e | Leg pad fully under the frame's ring (pad's inner edge to the window edge, where the locator registers) | 0 | new part | n/a | +0.57 | +0.27 | +0.27 | -0.03 | OPEN: the locator; T2 |
| M21f | Leg to B16's corner (165, 100) in Y | 1.0 | new part | n/a | +6.40 | +4.52 | +5.27 | +3.02 | MET |
| M21g | East and west legs' columns (outer face X 180.17) to the entry plates' screw heads at \|Y\| 100 (inner face X 184.51), in X | 1.0 | new part | n/a | +4.34 | +3.08 | +3.70 | +2.20 | MET |
| M21h | Leg column to the backer ring's outer edge (X +-172, `panel1450.py:93-95`; the leg on the window, the plate on the inserts) | 1.0 | new part | n/a | +3.40 | +1.51 | +2.49 | +1.01 | MET |

As designed, eleven rows fall below their minimum (M1, M8, M9, M10, M11, M12, M13, M14a, M14b, M18b, M19). Four are
OPEN because they are undefined (M14i and M20, and M11a and M18 because the twelve ruled arrestors have no place), and
the connector plate's other rows and M17a are OPEN because they were never checked. Four of the six items ruled for
the connector plate have no place either. The jumpers' route, the entry plates' screws and the arrestor's nut in its
spot-face are new rows (M11e to M11g, M13d, M17a to M17x).

With the chosen arrangement, `frame_seat.py` computes 70 rows: 35 are MET, 35 are OPEN and none is NOT MET. Here M8x
and M8y are one row, M8; M9 is added as MET (a condition) and M20, the seat, as OPEN.
- At the stated allowances, only two rows fall below their minimum: M17g and M17x, how the east jumpers lie under the
  plugs. Both sit at the limit of the jumper plug's class, where a pick inside the class meets them, so both are OPEN
  until the plug is picked.
- M1, M3 and M13 are OPEN on their TBD contributors (M13: the height of the arrestor's O-ring, which its drawing shows
  but does not dimension).
- The other 30 OPEN rows meet their minimum at the stated allowances but not with every unstated allowance taken
  twice. They rest on the case's own tolerance, which Peli does not publish, or on the kit's build allowances: the
  hand placement of the pack, the dock strip and the stack, the marking of holes and plates, the legs' locator and the
  frame's centring, the gasket's compression, and the bundles' ties.

Every leg's placement is in its chain (in two dimensions where it matters, M21d), and so is every tolerance this
document states for the entry plates' screws and the jumpers (M11d to M11g, M17a to M17x), and so is every part's
float on its fixings wherever its place counts (section 1). Section 7 names what closes each OPEN row. Without C6's
centring step, with the frame pushed against a wall at -0.76 and the plate floated the same way on its 4.6 mm holes,
M8 would fall to 0.60 in X and -0.21 in Y: the plate could touch the case, which is why the step is part of C6.

### 3.3 The back wall, outside and inside, at the connector plate (C3)

**What the plate carries.** The tree rules six items for it: the shore DC receptacle and the Glenair 233-370 USB
feed-through (`ASSEMBLY.md:135`), the sealed Gigabit RJ45 with PoE out and the sealed USB-C 45 W outlet
(`V2-SPEC.md:11`, `ASSEMBLY.md:118` to `:120`), the outside pod on its M8 receptacle (`ASSEMBLY.md:125`; ruling of 7
September 2026, "no holes anywhere") and the ground stud (`V2-SPEC.md:11`). `GROUNDING-AND-SHIELDS.md:50-56` makes
the plate the kit's cable-entry reference, joined to board A's ground by one strap. Four of the six had no part and
no place.

**Where the plate can go.** Outside, the drawing shows the back wall free only between the hinge fairings: their
bases start at \|X\| 58.93 at the parting line, and although section A-A shows the wall plain up to Z 93.57 at X
+87.34, the end view carries back features down to Z 15.88 at X positions no view gives (section 2.3). The plate
therefore stays within \|X\| 57.0 (M14i). Below it the outer bottom radius ends at about Z 15.9 (M14b); above it the
rim flange starts at Z 97.9 (M14o). Inside, every part must stay 1.0 under the frame skirt's lowest edge, Z 84.38
(M14a); B16's edge runs the whole wall at Y +100 with its underside at Z 49.00 (48.57 at the worst) and U51 hanging
1.6 below it at Y 68.3 to 85.8 (INFERRED, the LQFP class); A22 ends at Y 80 (`gen_pcb_a.py:16`); nothing may bear on
the X 0 rib if this wall carries it (M14n); the ribs at X +-76.2 are 19.7 mm beyond the nearest inside washer.

**The class envelopes** (where the part is picked, its sheet; where not, the class the pick must meet):

| Item | Envelope and source | Wall hole | Inside, and what its mate must do |
|---|---|---|---|
| A sealed RJ45, PoE out | MIL-DTL-38999 shell 15 wall-mount class, as the 233-370: flange 31.29 square, four holes of 3.35 or less on 24.61 (a float of 0.24 on M3), rear no more than 16.51 behind the flange (GLN); mated envelope 32.51 across, the shell 15 plug class (the 233-340 plug's diameter 1.280 (32.51) max, GLN; the D38999/26 shell 15 plug's Q max 32.5, Amphenol catalogue page 52). The recommended PX0833 is 38.1 over its coupling ring with a 27.7 cut-out and a nut about 33 across (INFERRED from its drawing's proportions), and rated 42 V (BUL) | 29 | rear face 3.41 inside the wall's inner face (5.13 at the worst); the Cat 5e patch plug, straight or right-angle, within 40.0 of that face and +-8 about the centre (INFERRED), runs under B16 and U51 and stops outboard of A22's edge (M14e, M14f); the patch then runs west under B16's back strip, outboard of A22, and up past B16's west edge to `J_ETH` (X -162 to -142, Y 81 to 98, `panel1450.py` B16_TALL), a route drawn with the lead |
| B sealed USB-C, power only (D-12) | the 4000 series rear-panel body as the PXP4043 sheet draws it: hex 22.23 A/F (25.67 across corners), cut-out 18.9/19.2 with a 9.0 flat, 24.8 overall of which 7.0 behind the panel, panel up to 6.2 (BUL, INFERRED to hold for the C-type, whose own sheets give no panel dimension); the body within 0.30 of the cut-out's centre (INFERRED: the sheet gives the cut-out, not the body); rear flange 26 across or less and the lead 7.0 or less (INFERRED); mated 26 across (INFERRED). The sheet also draws a panel seal 22.5 across, without its face or thickness | 29 | the body ends 0.34 short of the wall's inner face (a panel seal behind the plate would move it in by at most 1.2, the 6.2 panel range less the 5.0 plate, which M14h's 15.56 with the unstated allowances doubled takes); the lead goes straight into the case and bends down at R 28 (four times its diameter, INFERRED), its top at Z 40.1 under B16 and U51 and its innermost point at Y 99.94, outboard of A22's edge (M14g, M14h); the held series sheet gives 5 A and 30 V, which covers the 45 W outlet (15 V at 3 A, `PARTS.md:238`) |
| C shore DC | D38999/20 shell 13: flange 28.9 square, four holes of 3.45 or less on 23.01 (a float of 0.29 on M3), rear 9.81 behind the flange (GLN); mated 29.4 across, the D38999/26 shell 13 plug's Q max 1.157 (29.4) (Amphenol catalogue page 52) and its M85049/38S13N strain relief's E max 1.157 (29.4) (GLN) | 22: its body behind the flange passes the plate's 19.05 cut-out (`case_wall_cutouts.py:10-12`), so a 22 mm hole clears it by 1.47 per side, 0.78 at the worst of the two markings and the cut-out's machined place | rear 3.29 short of the wall's inner face; the cores turn down within 12 of it (M14d) |
| D USB host (console, key fill) | Glenair 233-370 shell 15: flange 31.29 square, four holes of 3.35 or less (a float of 0.24 on M3), rear 16.51 behind the flange (GLN); mated 32.51 across, the Glenair 233-340 plug of `ASSEMBLY.md:144` (G6, diameter 1.280 (32.51) max, GLN) | 29 | rear face 3.41 inside; a right-angle USB-A plug, cable down, body within 20.0 of the rear face (M14c). A straight USB-A plug of 40 (INFERRED) from D's position ends at Y 88.75 over the slot 2 heatsink (X -23 to 18, Y 32 to 88, top Z 71.60) with its body at Z 62.5 to 71.5: 0.75 outboard nominal, 2.07 inside at the worst |
| E pod on its M8 receptacle | the pod 28 x 28 on the plate and 30 proud (INFERRED class; undrawn); the M8 receptacle as recommended (binder 86 6618 1121 00004, `open-picks.txt:15`, M10 x 0.75 rear-fastened, sheet not held): nut 13 A/F, rear 15 behind the plate's face, its body in a 10.5 plate hole, a float of 0.33 that the pod follows (INFERRED) | 18 | rear 2.66 inside; the pigtail turns down within 12, to Y 117.60 |
| F ground stud | M6 class (INFERRED), the stud in a 6.4 plate hole (a float of 0.30): outside washers, lugs and a knurled nut within 24 across, the lugs being the external earth lead's and the two RF entry plates' leads (C4; their stack is owed, section 6); inside a washer of 12, the ring lug of the one bonding strap of `GROUNDING-AND-SHIELDS.md` item 4, and a Nyloc, within 12 of the wall | 8 | to Y 120.07; the only part besides the plate's screws that bears on the wall inside |

**The layout** (centres, case X and Z; the plate 114.0 x 68.3 x 5.0 at X -57.0 to +57.0, Z 18.3 to 86.6):

| Item | Centre | Row |
|---|---|---|
| A sealed RJ45 | (-28.5, 36.6) | low: its patch plug passes under B16 |
| C shore DC | (+4.2, 34.0) | low, 2.6 below A and B, on its 22 mm hole: D's 32.51 plug above it keeps 2.05 to C's 29.4 plug |
| B sealed USB-C | (+33.7, 36.6) | low: its lead passes under B16 |
| E pod over the M8 | (-30.0, 70.0) | high |
| D USB host | (+4.6, 67.0) | high: its body's top at Z 81.5 sets M14a |
| F ground stud | (+34.6, 64.5) | high |
| six M4 x 25 | X +-51.1, Z 24.2, 50.1, 76.0 | two columns, each screw hole 3.65 from the plate's edges (M14m) under a bonded sealing washer 10 across that stays 0.90 inside them (0.47 at the worst, the screw at its float, M14p); inside, a plain washer 9.0 and a Nyloc, ending at Z 80.5 |

The screw holes are sealed by design like every other hole: the gasket band applies to them (3.0 at the worst of the
stated allowances, M14m, OPEN), and the bonded washer under each head is meant to seal the screw's own path through
the plate; only T7 shows whether either seals. No screw fits between the columns, which are
102.2 apart, so the plate is 5.0 mm thick (INFERRED: a 3.0 plate would
leave the gasket's middle to the plate's stiffness, which goes as the cube of the thickness); the Glenair panel
range (.250 in), the 4000 series' 6.2 and the RJ45 class all take 5.0, and the M8's sheet is owed (section 6). The
flanges' M3 screws go into threads tapped in the plate, so nothing stands proud of its back. Every margin of the
plate is a row of section 3.2 (M14a to M14p); `frame_seat.py` part E prints each part's float and, at the worst, the
four tightest pairs on the face (A's and D's flanges 1.13, A's flange and each of the left column's two lower washers
1.19, E's pod and the top-left washer 1.24) and the three tightest mated pairs (D's and F's 1.11, A's and C's 1.12,
C's and B's 1.13). Every pair is taken with each part at its float on its fixings and at its machined place. At the
previous issue's centres (A at X -29.3, C +3.0, B +32.0, D +3.5, F +33.5), which M14j and M14k had judged without
either, A's flange came to 0.39 from the two lower washers of the left column at the worst, A's and D's flanges to
0.83 and C's and B's mated plugs to 0.63; so A, C, B, D and F move 0.8, 1.2, 1.7, 1.1 and 1.1 mm east. Holes C
and D cut the X 0 rib if this wall carries it; neither body bears on the wall, and the rib is a stiffener at most
0.75 mm proud that the frame's long-wall seat misses anyway (INFERRED harmless; T1 photos tell which wall carries it).

The recommended PX0833 does not fit this plate. Its nut needs a wall hole of about 36 (INFERRED from its drawing's
proportions); the hole's gasket band to the plate's bottom edge puts the coupler's centre at Z 39.9 or higher
(18.3 + 3.0 + 0.6 marking + 18), where its patch plug's top, 47.9, is above U51's underside at 47.4 (M14e would be
-0.50 nominal); and its 38.1 flange takes the place of the left column's two lower screws.

### 3.4 The end walls: the ruled arrestors as the antenna bulkheads, on an RF entry plate per wall (C2, C4)

**What is ruled.** Gas-discharge arrestors at the antenna bulkheads are an owner-approved item placed on the end
walls (appendix 32.50 item 4; `V2-SPEC.md:51`). Decision 31 routes board D's `J_PAOUT` path through "the same
PolyPhaser GTH-SFF-AL at the antenna bulkhead that J_ANT already declares" (`pcb_decisions.yaml:281-282`, appendix
lines 18121 to 18125), and TRN-001 passes on that declaration; `open-picks.txt:20` recommends one GTH-SFF-AL per
antenna bulkhead. The tree at `29f00554` places none: its bulkheads are Amphenol 132170 couplers (`ASSEMBLY.md:134`,
`:192`), and D-07 makes them twelve (east ANT3).

**The part** (POLY, section 1): an SMA female to female bulkhead on a 5/8-24 thread, 55.4 overall (2.18 in), at most
2.2 x 0.9 x 1.2 in (55.9 x 22.86 x 30.48 mm) and 113.4 g. From the body's face at the thread's root the thread runs
11.94 (.47 in) and a jack 7.62 (.30 in) beyond it; the other way the body and its outer jack run 35.81. The O-ring
sits on the thread's root against that face, drawn about 0.63 proud of it, so it takes part of the 11.94; the drawing
shows no gland and states no torque, so installed it stands anywhere from 0 to 0.63 (0.32 +-0.32 here, INFERRED),
which also sets how far the inner jack reaches into the case. Its gas tube sits under a cap on one side and its ground
lug hangs on the other, so neither reaches more than 30.48 - 11.43 = 19.05 from the axis. The nut is drawn 19.1 across
its flats (3/4 in, so 22.0 across its corners) and the lock washer 20.5 across, about 4.7 thick together, scaled and
not dimensioned: the class here is 24.0 across and 5.0 thick (INFERRED; section 6), which the arrestor's own nut and
washer meet as drawn and which a 5/8-24 UNEF nut and lock washer can meet in their place. The drawing says every
dimension on it is for reference only, so its .XX +-0.51 is taken here as an unstated allowance, as Peli's figures
are. Until its nut is tightened each arrestor floats 0.32 in its 16.3 hole (its 2A thread's smallest major is 15.66).

**Why the bodies go outside.** A body inside the case would reach 35.81 plus its jumper's plug in from the wall. At
the east wall that is over B16's edge band, where the RockBLOCK's box stands to Z 71.6 and the LimeSDR's to 62.6
(`panel1450.py` B16_TALL) and the right strip's buttons hang to Z 76.5; above it the frame skirt comes down to Z 84.38
at the worst, and below B16 the pack fills X 122 to 178.65. Outside is also where an arrestor belongs: it diverts a
surge before the conductor enters the case, and its own O-ring is what is meant to seal the weather side (only T7
shows whether it does).

**Why a plate, and not a hole per arrestor.** With each arrestor's nut on the case wall, the inner jack ends 11.94 +
7.62 - 0.32 (the O-ring) - 5.34 = 13.90 past the wall's inner face, and a right-angle plug of the class of section 6
reaches 10.0 further. At Z 66, about the highest the end-wall features allow a body there (66 + 19.05 under 87.93 less
the 1.0 minimum and 1.06 of allowances), that is X 189.27 - 23.90 = 165.37, 0.37 outboard of the RockBLOCK's box, and
at the worst (wall per side 0.38, wall thickness 0.76, the arrestor's two .XX lengths 1.02, the O-ring 0.32) 2.48
further in. The nuts would also bear on the wall inside wherever a site meets a rib at Y 0 or +-76.2, and each would
be tightened inside the case beside its neighbours. A 6.0 aluminium plate on a 2.0 gasket moves every arrestor 7.5
outward, so at the chosen Z 59 the plug ends at X 172.63 and keeps 3.36 to the RockBLOCK at the worst (M18, OPEN); the
arrestors are fitted and their nuts tightened on the bench, where a socket of 30 across on one nut clears the next by
4.00 (each nut stands 3.5 proud of the plate's back, its washer in a 1.5 spot-face); the nuts sit in the wall's 27 mm
holes and nothing of them bears on the wall; and the plate is the arrestors' common ground.

**The layout** (both end walls; case Y, the axis at Z 59.0; `frame_seat.py` part F):

| Wall | Arrestors, south to north | Pitch |
|---|---|---|
| East (5) | 5G MAIN -62, 5G DIV -31, 5G ANT3 (D-07) 0, IRIDIUM +31, LORA +62 | 31 |
| West (7) | VHF -93, HF -62, WIFI 2.4 -31, GNSS 0, SDR +31, WIFI P2P A +62, WIFI P2P B +93 | 31 |
| Entry plate | 6.0 x 220.2 x 48.9 aluminium at Y +-110.1, Z 34.55 to 83.45, on a 2.0 closed-cell gasket of the same outline, cut with the wall's 27 mm holes at the sites and 5.0 at the screws (the nuts and washers stand from the spot-faces into the gasket's thickness and the wall's, M13b), one per wall and both alike; 16.3 holes at the sites (the east plate's +-93 left undrilled), each spot-faced 26.0 on the plate's back to a floor 4.5 from its outer face (+-0.10), which leaves 4.10 of the back face to the plate's Y edge at the outermost sites for the gasket | |
| Wall holes | a 27 mm hole saw at each site; 5.0 at eight screws | |
| Screws | eight M4 x 12 A2 button heads (ISO 7380) from inside, each on a sealing washer 10 across whose rubber face (8.0 across or more) covers its 5.0 wall hole, into threads tapped through the plate at Y +-45 and +-100, Z 40.65 and 77.35: 3.66 of thread (1.95 at the worst, M11g), the tips 2.34 inside the plate's outer face (0.43 at the worst, M11d) | |

The order along each wall is the tree's with two moves: the third 5G jack sits at Y 0, between 5G DIV and IRIDIUM, and the two
WIFI P2P bulkheads move from the east wall's north end to the west wall's, because from an east site at \|Y\| 93 a
jumper cannot get inboard of a setting leg's column before it reaches it (the jumpers, below). The spacing and the
height are new. Every row of the end walls is in section 3.2: M10 to M13d, M17a to M17x, M18 to M18c, M4c and M21g.
Where it counts, at the stated allowances (the verdicts are section 3.2's; M10, M11c, M11d, M11e, M11g, M13, M13c,
M18 and every jumper row are OPEN):
- Inside, the highest part is a top screw head, 1.73 under the frame skirt at the worst (M10); only the screw heads
  bear on the wall, 17.21 from its ribs (M11). The 27 mm holes at Y 0 cross the rib there, and those at +-62 cut 0.21
  into the bases of the ribs at +-76.2 (part F); nothing bears on a rib. The plugs keep 3.36 to the RockBLOCK's box
  and more to the LimeSDR, the radio modules, J_ETH and T1 (M18), 6.80 to the legs (M18c); the bottom screw heads keep
  3.18 to the pack (M4c) and all of them 3.08 to the legs' columns (M21g).
- In the wall, the 27 mm holes keep 4.00 of wall between them (3.40 at the worst, M11a) and 3.64 to the 5.0 screw
  holes (M11b), and every hole a gasket band of 3.60 to the plate's edge (3.00 at the worst, M11c). Each M4 starts in
  its hole with 0.11 of its float to spare at the worst (M11e), and its washer's rubber face covers the hole wherever
  the screw sits in it (M11f).
- Outside, the plate's top stays 3.42 under the end-wall features at Y 0 and +-79.0 at the worst, whether they stand
  proud or are recessed (M12), and its ends 4.27 inside the end wall's flat skin (M12b); neighbouring bodies keep
  8.14, and 7.30 with each at its float (M18b). With the plate spot-faced under each nut, the arrestor's thread takes
  the O-ring, the plate and the nut with 1.20 to spare at the worst (M13, OPEN on the O-ring's height; on the full 6.0
  it would leave -0.40), and the nut and washer sit inside the spot-face and the wall hole (M13b to M13d). The screws'
  tips stay 0.43 inside the plate's outer face at the worst (M11d), where an arrestor body lies over the screws at
  \|Y\| 100 beside the west wall's +-93 sites, with 1.95 of thread engaged (M11g).

**The plate's place.** The plate goes on with its arrestors fitted, each nut into its 27 mm hole, and its screws are
started. At the stated allowances a place where both hold exists: the screws let the plate sit within 0.41 of each
screw hole's mark (the float 0.51 less the tapped hole's 0.10) and the nuts within 1.08 of each 27 mm hole's (1.5 less
the 16.3 hole's 0.10 and the arrestor's float of 0.32), and with every hole within 0.3 of its drawn place the drawn
place lies inside both, with 0.11 and 0.78 to spare. M13c keeps the more cautious reading, the plate marked to its
outline within 0.3 (0.48 at the worst).

**The jumpers inside** (`frame_seat.py` part G). Each jumper runs from an arrestor's inner jack to its float clamp on
E6 at Y -66 (`ASSEMBLY.md:134`; the clamps at the X of `gen_pcb_e.py:16`, the third 5G jack's at board A's X +46),
in RG-316 bent at R 12.5 or more (`ASSEMBLY.md:108`, `:134`), with a right-angle SMA male at the jack of the class of
section 6: at most 10.0 beyond the jack's end and 5.0 about its axis, its cable's axis within 4.0 of its inner end,
its crimp ferrule ending within 16.0 of its mating axis.
- **What the previous issue left.** It sent every cable down from the plug's underside at Z 54.0. Below the east
  plugs the pack fills X 122 to 178.65 up to Z 44.58 (M6), under every east site: 9.42 of fall, 8.26 at the worst,
  where RG-316 needs 12.5 and its own radius to turn, and the C6 legs close the corridors at the pack group's ends (M5,
  1.77 at the worst against a 2.49 cable). Its M17 measured the room between B's edge and the east wall at Z 50, a
  clearance at a height the plugs sit just above; it did not show that a jumper could bend or pass, and it is retired.
- **East.** Each plug is turned 30 degrees below the wall's direction toward its bundle's end. At the class's 16.0
  reach its ferrule ends at Z 51.00, and its cable lands 20.11 along the wall from its site, at Z 49.33. That is the
  middle of a band two RG-316 high over the pack's outer strip (Z 46.80 to 51.78), whose layers are centred at Z 48.045
  and 50.535.
  - The band has 2.96 of free height between the pack and the plugs at the worst, each plug's arrestor at the bottom
    of its float (M17a, OPEN: 1.90 with the unstated allowances doubled, against its 2.0).
  - A cable in its upper layer passes under the next plug's body with 1.00 at the worst (M17b); the drop from the plug
    itself keeps 8.32.
  - The bundle runs along the wall in a lane between B16's edge and the legs' columns (3.44 of free width at the worst,
    M17d) and passes each leg inboard of its column and above its gusset (its underside at Z 42.67 over the leg's outer
    face at the worst; the gusset is below Z 30).
  - It bends down 1.25 beyond the pack group's end, goes down at \|Y\| 115.25 to 120.23 (1.47 clear of the leg at the
    worst, M17e), and turns onto the long wall's floor fillet beside the dock strip's south edge (M17f).

  The front bundle carries 5G MAIN, 5G DIV, 5G ANT3 and IRIDIUM, the back bundle LORA. Four is the most a bundle
  carries: two wide in the lane, and two high under the plugs. Every one of these rows is OPEN (section 3.2). Each
  rests on an allowance no source states: the bundles' ties, the hand placement of the stack and the dock strip, the
  marking, the floor under the pack, the case's wall or the legs' locator.
- **Under the east plugs: OPEN, and the previous issue's claim that the bundle closes there is withdrawn.** The previous
  issue laid it out like this: the cables passing a plug in the band's lower layer and in its inner upper place, one
  cable (2.49) inboard of the plug's cable axis, and the plug's own cable in the outer upper place. That layout does not
  close at the limits of the plug's class, and no held source says where in the class the pick will fall.
  - **M17g.** Three cables pass under 5G MAIN (IRIDIUM, ANT3 and DIV). At the class's 16.0 reach, MAIN's own cable
    lands 1.21 below its place, onto the passing cable there: -1.21 nominal, -2.43 at the worst. It lands at its place
    with a reach of 13.58 or less, or with MAIN turned 26.5 degrees instead of 30 (no plug lies beyond it). The inner
    upper place clears MAIN's ferrule only for a ferrule 2.58 across or less. A crimp ferrule sleeves the braid over the
    plug's body, so it is wider than the 2.49 cable (INFERRED; no held sheet gives one).
  - **M17x.** The inboard column runs beside B16's edge and at its height: B16's underside is at Z 48.57 at the worst,
    inside the band. The class allows the plug's cable axis to sit at the plug's inner end. There, the column's inner
    face is 3.89 outboard of B16's edge at nominal and 0.38 inboard of it at the worst (-0.38). With the axis 4.0 from
    that end, it is 7.89 outboard (3.62 at the worst). It meets the 1.0 minimum at the worst for an axis 1.38 or more
    from the plug's inner end, with a ferrule 2.58 across or less; a wider ferrule moves the column in by half its
    excess.
  - **Levers**, each to be judged with the picked plug's drawing:
    - 5G MAIN turned less.
    - A plug whose ferrule ends 13.58 or less from its axis.
    - IRIDIUM in the back bundle. That leaves at most two cables passing under a plug (MAIN two, DIV and LORA one), so
      no passing cable needs the inner upper place beside a ferrule.

    None is taken here. Each moves a bound, but the ferrule's diameter and the cable axis's place, which decide both
    rows, are on no held sheet.
  - **What closes it:** the plug's drawing (the offset of its cable axis from its inner end, and its ferrule's reach
    and diameter), then T10 on the mock-up with the picked plug and RG-316 (sections 5 and 7).
- **Why five sites east.** A cable must be inboard of a leg's column (X 175.40) before it reaches the leg (\|Y\|
  106.4). From its plug's cable axis (X 176.63 at the class's limit, 179.80 at the worst) that takes an S-bend after
  the cable has landed. The two-wide bundle bends, so its centreline runs at R 13.745 and its inner cable at R 12.5.
  From a site at \|Y\| 62 the cable is in the lane by \|Y\| 95.48 (101.72 at the worst) against 104.16 (103.28),
  M17c. M17c is OPEN: with the unstated allowances taken twice, the cable comes 2.34 short. From \|Y\| 93, the previous
  issue's outermost east site, it would be 22.32 short at nominal.
  Five east sites at a 31 pitch put the outermost at \|Y\| 62, so two of the seven move west: the WIFI P2P pair,
  whose clamps (X 18 and 32) lie nearest the west wall of the east group's.
- **West.** No pack stands under the west plugs. Each cable leaves its plug downward, its ferrule ending at Z 43.0,
  29.0 above where its turn onto the floor must start, and falls outboard of B16's edge (2.11 at the worst, M17w,
  OPEN). The drop zone, X -165 to the west wall at \|Y\| up to 98 from the floor to Z 54, is the jumpers'. The shore
  lead is tied along the same west wall (`ASSEMBLY.md:92`), and its lane beside the drops belongs to the floor plan
  (section 6).
- **To the clamps.** From the corners (east) and the wall's foot (west) the route to each clamp crosses the floor
  plan, which is not drawn: the four east front jumpers reach their clamps from the south across E6's south part;
  LORA's and the seven west jumpers reach theirs from the north along the floor under A22, VHF's and HF's first
  along the west wall's foot to Y -35. Those lanes and the way each clamp's cable leaves are E6's and the floor plan's
  (section 6).
- **Lengths**, connector axis to connector axis on that route (the floor runs to the clamps INFERRED): 5G MAIN 250,
  5G DIV 267, 5G ANT3 326, IRIDIUM 315, LORA 340, VHF 253, HF 236, WIFI 2.4 232, GNSS 277, SDR 322, WIFI P2P A 367,
  WIFI P2P B 412. Three of the twelve fall inside the 150 to 250 that `ASSEMBLY.md:134` states. Each jumper is cut
  to its route plus a 20 mm service allowance (INFERRED), 252 to 432 mm, and each link budget takes its own length
  (section 6).

**What changes outside.** The bodies stand 43.9 from the wall's skin (gasket, plate, the O-ring at its drawn height,
body and outer jack), so the case is about 67 mm longer over the arrestor rows (X +-238.8 against the drawing's
exterior of 411, whose widest part is the rim flange at X +-205.74), it can no longer stand on an end wall, and
TEST-PLAN E1's drops onto an end wall land on the arrestors (section 6). The twelve arrestors add 1361 g (their
sheet's 0.25 lb each) and the plates about 151 g (east, five holes and spot-faces) and 142 g (west, seven).

**The ground.** Each arrestor's thread and nut clamp it to the aluminium plate, so the plate joins the five or seven
bodies; one lead from each plate, on the lug of its arrestor nearest the back wall, goes round the case to the ground
stud F on the connector plate, outside, so a surge is diverted to the kit's earth point without entering the case.
`GROUNDING-AND-SHIELDS.md:39` ("Every SMA jack grounds its body to the wall it is clamped in, which is plastic") no
longer holds; the lead, its route round the back corners and the bond it adds are that document's items (section 6).

## 4. The changes (deliverable 3)

Each is **the session's choice under the owner's standing rule of 26 September 2026**. None changes a printed
circuit board, a ruled device or anything bought; the face plate, the legs, the connector plate and the RF entry
plates have not been ordered, so no sunk work is lost. C3 constrains two open picks (the sealed RJ45 and the sealed
USB-C), which were recommendations, not rulings; C2 and C4 place the ruled arrestors, which the tree had not placed,
as the part `open-picks.txt:20` recommends, and constrain its nut, the jumpers' plug and their route (section 6).

### C1. The face plate goes on the frame, the way Peli documents it

- **What.** The 3 mm aluminium plate lies on the 1450PF's top face and covers Peli's o-ring in the channel between the
  frame and the case (instruction step 4, product page). Ten 6-32 UNC x 1/2 in A2 pan-head screws go in from above, by
  hand, into Peli's brass inserts (the ring's bore is 9.39 deep and the insert 6.3 long, so 3.09 mm of it is empty
  above the insert, and 1/2 in gives the full 6.3 mm of engagement with its tip 0.31 below the ring, INFERRED from
  those figures; the instructions name 6-32 for every frame but the 1120 and 1150); plate holes **4.6 mm** at Peli's
  insert bores, X +-179.07 at Y +-75.95 and X 0 and +-139.45 at Y +-121.16 (the frame STEP; the sheet's pattern is
  358.1 x 242.3), which `FRAME_BOSSES` (`panel1450.py:18`) rounds to 0.1 mm and is to carry at the STEP's figures. The
  largest 6-32 (3.505 major) has 0.55 of clearance in them, which takes Peli's insert pattern at the frame sheet's
  +-0.38 per side and the hole's own +-0.10 with 0.07 to spare at the worst (M8f); the earlier 3.8 mm holes (0.15) did
  not. The smallest (class 2A, 3.332) lets the plate float 0.63, which every chain of the plate's place carries (M2b,
  M8, M8h, M21h). The PORON 4701-30 ring is dropped; Peli's o-ring is the intended seal (T3 and T7 show whether it
  seals). The frame rests on the C6 legs.
- **Numbers.** Plate **377.2 x 263.0 x 3.0, R16 corners**: 0.8 narrower than the 378.0 first chosen, which pays in X
  for the float the 4.6 mm holes give the smallest 6-32 (M8x 1.10, M8y 1.05 at the worst; at the previous issue's
  377.4, M8x came to 0.996 at the worst, just under its 1.0). The band outside **368.0 x 253.0** is rebated 2.0 mm
  from the top, leaving it 1.0 mm thick with its underside unchanged, so the o-ring sees the same plate while the edge
  under the lid's wall sits 2.0 mm lower (M2). The full-thickness face stays 2.94 mm inside the lid's opening in X and
  3.29 in Y (1.25 at the worst, M2b). A 6-32 pan head is up to 6.86 across (ASME B18.6.3 class, INFERRED): the heads
  keep 1.50 mm to the rebate line at the end inserts and 1.91 at the long-wall inserts, 0.77 and 1.18 with the screw
  anywhere in its hole (M8h); at the previous issue's 367.0 x 251.0 the long-wall heads kept 0.91 nominal (0.87 at
  `FRAME_BOSSES`' 121.2), not the "about 1.0" it stated, and less with the float. A relief pocket **44.0 x 9.0 x 0.8
  mm** in the underside over the frame's raised lettering, at X -110.9 to -66.9 and Y -125.4 to -116.4 (the lettering
  spans X -108.99 to -68.80 and Y -123.64 to -118.32, section 2.4; the first issue of this document gave 20 x 7, less
  than half of it), which leaves 2.2 mm of plate there and stays inside the full-thickness face; it clears the
  lettering by 1.76 in Y and 1.90 in X, 0.65 and 0.79 at the worst (the plate's float 0.63, the lettering's place on
  the frame 0.38, the pocket's 0.10). **`FACE_TOP_Z` becomes 106.52**, derived in the file from the leg's pad, the
  ring and the plate (104.77 to 108.27 at the worst); everything hanging from the plate keeps its offsets to it.
- **Why this and not the alternative.** Keeping the plate under the ring means hanging the frame 9 mm above any seat
  Peli describes, loading the inserts away from their shoulder (a screw from below pulls each insert out against
  its press fit, section 2.5), notching the plate round Peli's four frame-screw heads (M9), and leaving the o-ring
  uncovered, the path the product page says keeps the base watertight with the lid open. C1 follows Peli's
  documented interface and, on the C6 legs, is the only arrangement found in which M1 stays above its floor at the
  worst of the stated allowances (M1 is still OPEN on its TBD contributors).
- **Files.** `v2/ecad/tools/panel1450.py` (`FACE_TOP_Z` derivation, `PLATE`, `PLATE_R`, the band as a rebate, the
  comments at lines 14 to 19 and 26, `FRAME_BOSSES` at the STEP's bores), `v2/cad/face_plate.py` and
  `plate_drawing.py` (outline, rebate, relief, 4.6 mm holes), `v2/ecad/tools/z_budget.py` (the datum rows: floor,
  leg, ring, plate, VHB), `v2/cad/render/scene.py` (lines 19 to 23: rim 108.97, the Peli cavity, the frame on its
  legs), `v2/docs/ASSEMBLY.md` (rows at lines 29 and 66 and the lift-out order at 162: the frame and legs stay, the
  plate lifts off), `v2/BUILD.md:35` and `:57`, `v2/README.md:52`, the regenerated `release/revA/case/face-plate/`.
  `check_pcb_c.py` reads `panel1450.py` and needs no number of its own.
- **Cost.** About +31.5 g of aluminium (a larger outline less the rebated band and the relief), one extra CNC pass
  for the rebate and the relief, ten 6-32 screws instead of M3. The space above the face falls from 53.04 to 47.92 mm
  nominal (44.39 worst; M3 counts it under the tray).
- **Follow-on decision, also the session's.** The dock strip's 1.1 mm VHB 5952 pads lift the whole stack, as
  `ASSEMBLY.md:47` has it (option a); the A-to-B bay spacer keeps its 31.3 mm, the D8 mezzanine loses nothing and the
  pack gains the 1.1 mm (M6). Option (b), a bay spacer 1.1 mm shorter, is not taken.

### C6. Four setting legs, fixed to the frame's ring, give the frame its height; the frame's centring places them

- **What.** Four aluminium legs are bonded under the frame's ring, near its corners, before the frame goes into the
  case; their bare feet stand on Peli's flat floor. The frame is lowered on its legs, centred, and then fixed with
  Peli's four self-tapping screws as Peli instructs. The legs stay in as the frame's supports, and the frame's
  centring is what places them on the floor, so no template is registered to the walls.
- **Numbers** (`frame_seat.py` part C). Each leg is a profile cut from 6.0 mm 6061-T6 plate, lying in the X-Z plane
  at **|Y| 106.4 to 112.4**:
  - the foot bears on the flat floor over **|X| 156.0 to 169.0** (2.64 inside the fillet tangent), bare, so the
    feet slide while the frame is centred;
  - beyond the foot its underside follows Peli's R 15.88 floor fillet at a 2.5 mm normal offset (5.57 above the
    floor under the column's outer face);
  - the column runs up at **|X| 175.40 to 180.17** to a pad whose top is **94.13 +-0.10** above the foot's bearing
    face, under the frame's ring (the ring spans |X| 174.83 to 182.75 over the leg's Y); a gusset joins the
    column to the foot below Z 30. The column stands 0.20 inboard of the previous issue's: its outer-back corner lies
    in the skirt's R 17.53 corner arc, and there it keeps 1.14 at the worst with the leg placed in X and Y at once
    (M21d), against 0.95 before; the pad keeps 0.27 under the ring (M21e).

  **Placement:** with the frame face down on the bench, a printed locator drops into each corner of the window and
  registers on both window faces; it holds the leg's column at its drawn place on the ring's underside, and the leg
  is bonded there by a VHB 5952 pad in a 0.9 mm pocket of its pad top, so the aluminium rim, not the tape, meets the
  ring and sets the height. A leg then sits within 0.30 of its place against the window (INFERRED), and since the
  locator registers on both window faces it moves in X and in Y at once, by up to 0.68 against the frame's own
  features; within 0.88 against the case centre once the frame is centred, and within 1.26 against a case feature.
  Every M21 row and M5 carry that allowance, M21d in two dimensions. **Centring:** two pairs of printed tapered
  wedges (0 to 2.0 mm over 40 mm), one pair per axis, pushed into the gap between the skirt and the walls at the
  middle of opposite walls to equal depth marks; Peli's four screws are driven; the wedges come out; the o-ring goes
  into the channel. The frame is then centred to +-0.20 (INFERRED).

  The pad (4.77 x 6.00 = 28.6 mm2) puts the frame's bottom at Z 86.00 nominal, 1.42 above Peli's rib tops. A face of
  about 25 N shared by the four legs bears 0.22 MPa on each pad; at an assumed 100 g shock on a 2.5 kg face
  (INFERRED; TEST-PLAN E1 sets the drops, not a peak) each pad bears 21.4 MPa, which the frame's polymer (not stated
  by Peli, TBD) is to carry. A column buckles at 4652 N (pinned, E 69 GPa). Each leg is about 11.8 g.
- **Why this height.** Section 2.7: Peli's ribs cannot set the frame's height at the current moulding. The floor
  is the stack's own datum, so a floor-referenced stop removes the rib's height from M1. The pad top of 94.13 is the
  lowest that keeps the plate's underside 0.10 above the highest the shoulder can stand (shoulder 101.04 + 0.76 +
  0.10 - ring 9.39 + the floor, leg and ring allowances 1.62; M8z); the first issue's 93.53 left the rebated band
  able to face the cavity below the shoulder, where M8x falls to 0.68. It keeps M1 1.62 mm above its 2.0 floor at the
  worst for the TBDs of 3.1, and leaves M2 and M3 at 1.84 and 16.39; a higher pad takes the same millimetres from M2
  and M3.
- **Why fixed to the frame.** A leg bonded to the floor by hand has nothing to locate it, and its placement
  (+-1.0, the stack's own allowance) breaks five M21 rows at the worst. Bonded to the frame by a locator on the
  window, a leg is placed to 0.30 against the frame and follows the frame's centring against the case: at the worst of
  the stated allowances its foot stays on the flat floor, its relief clears the fillet and its column clears the
  skirt (M21a to M21e; M21b to M21e are OPEN on the locator's and the centring's allowances, which T2 measures). The
  frame's own screws hold the frame; the legs carry it in compression.
- **What the legs claim.** The four zones |X| 156.0 to 180.17, |Y| 106.4 to 112.4, from the floor to Z 94.2, each
  within 0.88 of its place, are the legs'. The pack group keeps 1.77 mm to them per side at the worst (M5); the
  mixer fans at the stack's ends (positions not yet drawn), the water electrodes ("the low corner", `ASSEMBLY.md`
  section 4) and the shore lead's route along the west end wall keep out of them (the lead passes between a leg and
  the wall in 7.33 mm, 5.69 at the worst); the RF entry plates' screw heads and jumper plugs keep 3.08 and 6.80 to
  them (M21g, M18c), and the east jumpers pass them inboard of their columns and above their gussets (M17c to M17e).
- **Files.** New `v2/cad/frame_leg.py` (profile, drawing and STEP, the locator and the wedge set);
  `v2/ecad/tools/panel1450.py` (the leg constants and the `FACE_TOP_Z` derivation), `z_budget.py`,
  `v2/cad/render/scene.py`; `v2/docs/ASSEMBLY.md` section 1 (a fastener row for the legs and the frame's screws),
  section 2 (the legs on the frame on the bench, then the frame, the centring and Peli's screws before the stack
  goes in), section 3 (the pack group centred between the legs), section 7 (the frame and legs stay in the case)
  and section 9 (the bench list); `v2/BUILD.md:57`.
- **Cost.** About 48 g of aluminium, four profile cuts, four VHB pads, a printed locator and a printed wedge set.

### C2. The antenna bulkheads are the ruled arrestors: twelve at Z 59, five on the east wall and seven on the west

- **Numbers.** `SMA_Z` 88.0 to **59.0**, the arrestors' axis (the reason for 88, "above the battery row",
  `case_wall_cutouts.py:118`, retired with the west battery row). East, south to north: 5G MAIN **-62**, 5G DIV
  **-31**, the ruled third 5G jack (D-07, ANT3) **0**, IRIDIUM **+31**, LORA **+62**. West: VHF **-93**, HF **-62**,
  WIFI 2.4 **-31**, GNSS **0**, SDR **+31**, WIFI P2P A **+62**, WIFI P2P B **+93**. A 31 pitch on both walls, the
  tree's order kept but for two moves: ANT3 at Y 0, between 5G DIV and IRIDIUM, and the WIFI P2P pair from the east wall's
  north end to the west wall's. Twelve bulkheads, each a PolyPhaser GTH-SFF-AL on its wall's RF entry plate (C4).
  **The jumpers:** a right-angle SMA male of the class of section 6 on each inner jack. On the east wall each plug is
  turned 30 degrees below the wall's direction toward its bundle's end; 5G MAIN, 5G DIV, 5G ANT3 and IRIDIUM run in a
  front bundle and LORA in a back one, each over the pack's outer strip under the plugs, in the lane inboard of the
  legs' columns, and down beyond the legs to the floor. On the west wall each cable goes straight down to the floor.
  Every bend is planned at R 12.5 or more, and each jumper is cut to its route of section 3.4 plus 20 mm. How the east
  cables lie under the plugs is OPEN until the plug is picked (M17g, M17x), and so is every other jumper row.
- **Why.** Section 3.4. The 31 pitch keeps 4.00 of wall between the 27 mm holes (3.40 at the worst, M11a), 8.14
  between the bodies outside (M18b) and room for a socket on each nut on the bench. Z 59 puts the plate's top
  screw heads 1.73 under the frame skirt at the worst (M10, OPEN) and the plate's top 3.42 under the end-wall features
  (M12), keeps the jumper plugs 3.36 outboard of the RockBLOCK's box (M18, OPEN), and keeps the plate's bottom screw
  heads 3.18 clear of the pack's east face (M4c). Under the east plugs the pack leaves a cable no room to turn
  downward, so the east cables go along the wall and round the pack's ends, where the legs stand; a cable gets inboard
  of a leg's column in time only from a site at \|Y\| 62 or less (M17c), so the east wall takes five and the west,
  with no pack under it, seven. The P2P pair moves because its clamps lie nearest the west wall of the east group's.
  The case half of D-07 is these rows: the east wall takes the three 5G jacks, IRIDIUM and LORA.
- **Files.** `panel1450.py:115-118` (`SMA_Z`, `WALL_WEST`, `WALL_EAST` and the comment); `case_wall_cutouts.py` sheets
  3 and 4 (lines 115 to 147: seven 27 mm holes on the west wall and five on the east, the eight 5.0 mm holes per end
  wall, the notes' "nine" jacks, the battery row and the 6.5 D-hole, the rib and feature positions of section 2.3);
  `scene.py` (the plates, the arrestors and the jumpers' routes); `ASSEMBLY.md` :22 (eleven to twelve), :63 (the
  pigtails to the arrestors' inner jacks), :134 (the jumpers' row: the arrestors at the new Y, Z 59, the plug's class
  and turn, the route and the lengths of section 3.4 in place of "150 to 250 mm"), :158 (the legend strips gain ANT3,
  the WIFI P2P labels move to the west wall's, "RF HAZARD DURING TX" beside the VHF arrestor), :162 and :192 (eleven
  couplers to twelve arrestors); `v2/BUILD.md:58` ("eleven 6.5 mm D-holes at Z 88"); `v2/README.md:3` and `:52`
  ("eleven antenna couplers ... at 88 mm"); `v2/docs/V2-SPEC.md:10` (the end walls row: five east, seven west), `:42`
  (kit-to-kit WiFi: "B16 PCIe, two east jacks" becomes two west jacks) and `:51` (the arrestors placed). Board A's
  blind-mate X sites and E's clamps do not move; the D-07 site at board A X +46 is inside the flat floor and far from
  every case surface. The way each clamp's cable leaves and the lanes the jumpers need on E6 and under A22 are E6's
  and the floor plan's (section 6).
- **Cost.** None beyond C4 but the jumpers' length: cut to their routes, 252 to 432 mm, where the tree states 150 to
  250 (each link budget takes its own, section 6).

### C3. One connector plate between the hinge fairings carries the full ruled set

- **Numbers.** 114.0 wide x 68.3 tall x **5.0** mm aluminium (5052 or 6061, as `case_wall_cutouts.py` sheet 2 has it),
  outside the back wall, **centred at X 0, Z 18.3 to 86.6**, on a 2 mm closed-cell gasket of the same outline. Items
  at the centres of section 3.3: A sealed RJ45 (-28.5, 36.6), C shore DC (+4.2, 34.0), B sealed USB-C (+33.7, 36.6), E
  pod over its M8 receptacle (-30.0, 70.0), D USB host 233-370 (+4.6, 67.0), F ground stud (+34.6, 64.5). Six **M4 x
  25** at X +-51.1 in rows Z 24.2, 50.1 and 76.0, a bonded sealing washer 10 across under each head (INFERRED class),
  a plain washer and a Nyloc inside. The Glenair flanges (and the RJ45's, of the same class) on their 930-001 gaskets
  with M3 into threads tapped in the plate. Wall holes: three 29 mm hole-saw holes (A, B, D), one 22 (C), one 18 (E),
  one 8 (F) and six 4.5. Plate holes besides the Glenair and Bulgin cut-outs: E's receptacle in 10.5, F's stud in 6.4
  and the six screws in 4.5 (INFERRED); each part floats in them, and on its M3 in its flange's holes, by the figures
  of section 1, which M14j and M14k carry.
- **The mates inside.** A: the Cat 5e patch plug, straight or right-angle, within 40.0 of the coupler's rear face
  and +-8 about its centre, under B16 and U51 and outboard of A22 (M14e, M14f). B: the lead straight into the case,
  bent down at R 28 or more, under B16 and outboard of A22 (M14g, M14h). C: the cores turned down within 12 of the
  receptacle's rear (M14d). D: a right-angle USB-A plug, cable down, body within 20.0 of the rear face (M14c). E:
  the pigtail turned down within 12. F: the bonding strap to board A's ground near the dock
  (`GROUNDING-AND-SHIELDS.md` item 4) on the stud's inside end.
- **The picks it constrains** (section 6): the sealed RJ45 inside the shell 15 envelope (its flange's holes 3.35 or
  less) and rated for the 54 V PoE feed, which the recommended PX0833 is not on either count; the sealed USB-C inside
  the 4000 series body as drawn for the PXP4043; the M8 receptacle taking the 5.0 plate (or a counterbore to 3.0
  behind it); the pod and the stud inside their classes, the stud's outside end taking the external earth lead and the
  two RF entry plates' leads (C4).
- **Why.** Outside, the plate stays 1.15 mm inside the fairings' bases at the worst (M14i), 1.34 above the outer
  radius (M14b) and 10.25 under the rim flange (M14o); every flange, the pod, the stud and the screw washers keep 1.13
  or more between them at the worst, each at its float on its fixings (M14j), and the mated connectors 1.11 with D's
  and A's plugs at their sheets' 32.51 and C's at 29.4 (M14k): C sits 2.6 lower than A and B so that D's plug clears
  C's by 2.05. In the wall, webs keep 3.51 at the worst (M14l) and every hole, the screw holes included, a gasket band
  of 3.05 to the plate's edge (M14m), and the bonded washers stay 0.47 inside it (M14p). Inside, D's body tops out
  2.58 under the skirt at the worst (M14a); the two deep mates pass under B16 and U51 with 1.73 and 6.17 to spare
  (M14e, M14g), the others turn down outboard of B16's edge. The frame's back screws (X +-98.04) are 41 mm from the
  plate's edge. M14a, M14b, M14i and M14m are OPEN on the case's unstated heights and the hand marking of holes and
  plate (section 3.2). A plate that kept only the two picked receptacles would leave four ruled items without a place;
  one that reached the fairings' span would rest on geometry no view gives.
- **Files.** `v2/ecad/tools/case_wall_cutouts.py` (:10 to :17 and :25 to :29, sheets 1 and 2: the plate, the six
  items, the wall holes, the notes' "two receptacles", the rib and hinge text of section 2.6); `ASSEMBLY.md` :34 (M4
  x 25 at the new positions, a bonded sealing washer under each head), :118 (the patch plug within 40.0), :119 and
  :120 (the USB-C lead), :121 (the right-angle USB-A plug at the feed-through, cable down), :125 (the pod), :135 (the
  plate row with all six items placed), :139 (more than two cables leave through the plate), :192; `V2-SPEC.md:11`;
  `v2/BUILD.md:51` and `:59` (the window "between the ribs at X -95 and -18"); `v2/vendor/open-picks.txt:13` to `:16`
  (the RJ45's envelope and voltage, the USB-C's drawing, the M8's panel, the stud's class);
  `GROUNDING-AND-SHIELDS.md:13` (the plate also carries the M8 and the stud) and `:55` (the strap lands on the stud);
  `v2/cad/render/scene.py:228`, `:252`, `:539` (the plate and its camera).
- **Cost.** The plate is 105 g before its cut-outs (114 x 68.3 x 5.0 at 2.70 g/cm3), 69 g more than the 54 x 82 x 3
  plate; sixteen tapped M3 holes; the RJ45 part is re-picked, its price TBD.

### C4. One RF entry plate per end wall carries the arrestors; the Amphenol 132170 retires

- **Numbers.** A **6.0 mm** 6061 (or 5052) aluminium plate **220.2 x 48.9** at Y +-110.1, Z 34.55 to 83.45, outside
  the end wall on a 2.0 mm closed-cell gasket of the same outline, cut with the wall's 27 mm holes at the sites and
  5.0 mm holes at the screws; the same outline on both walls, with five 16.3 mm holes on the east plate and seven on
  the west at the C2 sites, each **spot-faced 26.0 on the plate's back** to a floor 4.5 from the outer face (+-0.10).
  Each arrestor goes through its hole with its own O-ring on the plate's machined outer face and its lock washer and
  nut on the spot-face's floor, cap up and ground lug down, and is tightened on the bench before the plate goes on (a
  socket of 30 across clears the next nut by 4.00). The arrestor's 11.94 of thread takes the O-ring (0.32 +-0.32,
  drawn 0.63 on the thread's root), the 4.5 under the spot-face and a nut and washer of up to 5.0 with 1.20 to spare
  at the worst and 0.38 with the unstated allowances doubled (M13, OPEN until PolyPhaser dimensions the O-ring); on
  the full 6.0 it would leave -0.40 at the worst. The nut and washer keep 0.58 inside the spot-face at the worst
  (M13d). **Wall holes:** a 27 mm hole saw at each site, in which the nut and washer sit with 3.34 of depth and 1.50
  of radius to spare (1.78 and 0.48 at the worst, M13b, M13c), and **5.0 mm** at eight screws. **Screws:** eight M4 x
  12 A2 button heads (ISO 7380) from inside, each on a sealing washer 10 across and 1.5 thick whose rubber face (8.0
  across or more) covers its hole on the wall's inner face, into threads tapped through the plate at Y +-45 and +-100,
  Z 40.65 and 77.35: each starts in its hole with 0.11 of its float to spare at the worst (M11e), its washer covers
  the hole wherever the screw sits in it (M11f), 3.66 of thread is engaged (1.95 at the worst, M11g) and the tips stay
  2.34 inside the plate's outer face (0.43 at the worst, M11d); the heads keep 17.21 from the ribs (M11), 1.73 under
  the skirt (M10), 3.18 from the pack (M4c) and 3.08 from the legs (M21g) at the worst. M10, M11d, M11e, M11g and M13c
  are OPEN on the wall's thickness, the gasket's compression and the marking, and M13 on the O-ring's height (section
  3.2). No tightening torque is stated for the M4 x 12 (section 6).
- **Why these holes, this thickness and these screws.** The previous issue's 4.5 holes let an M4 float 0.26 against
  0.40 of hole marking and thread position, so not every screw was sure to start; 5.0 holes give 0.51, and the screw
  rows move 0.25 inward so that the larger holes keep their 3.0 band (M11c). Its M11d left out the plate's own +-0.20
  and the screw's length tolerance: on a 5.0 plate the chain of the wall (0.76), the gasket (0.5), the screw (0.35),
  the washer (0.10) and the plate (0.20) lets neither an M4 x 10 engage two pitches nor an M4 x 12 stay inside, and
  the tips must stay inside, because an arrestor body lies over the screws at \|Y\| 100 beside the west wall's +-93
  sites. On a 6.0 plate an M4 x 12 does both (M11d, M11g), and each inner jack sits 1.0 further out, which M18 gains;
  the arrestor's thread takes that plate, its own O-ring and its nut only with the plate spot-faced under the nut
  (M13), which leaves the screws' thread in the full 6.0.
- **The ground.** The plate joins its arrestors' bodies through their threads and nuts; one lead from each plate, on
  the lug of its arrestor nearest the back wall, goes round the case to the ground stud F, outside, so a surge leaves
  by the kit's earth point without entering the case. The lead, its route and the bond it adds are owed to
  `GROUNDING-AND-SHIELDS.md` (section 6).
- **Why a plate.** Section 3.4: with each nut on the case wall the jumper plugs reach the RockBLOCK's box at the
  worst, the nuts bear on the ribs where a site meets one, and each is tightened inside the case beside its
  neighbours; on the plate the plugs keep 3.36 to the box at the worst, nothing of the arrestors bears on the wall,
  the nuts are tightened on the bench, and the arrestors share one ground.
- **Files.** `case_wall_cutouts.py` (the 6.0 entry plate's drawing with its 16.3 holes, their 26.0 x 1.5 spot-faces on
  the back, and tapped M4 holes beside the end-wall templates of sheets 3 and 4, whose screw holes are 5.0; the
  coupler note at line 145 retires); `ASSEMBLY.md` section 1 (a fastener row for the entry plates in place of the
  couplers': M4 x 12 on rubber-faced sealing washers), section 3 (the arrestors on the plates on the bench, the plates
  on the end walls; `BUILD.md:58` likewise), :192 (the bench list: twelve GTH-SFF-AL, two 6.0 plates and gaskets,
  eight M4 x 12 with sealing washers per plate); `v2/cad/render/scene.py`; `GROUNDING-AND-SHIELDS.md:15` ("the nine
  SMA bulkhead jacks") and `:39` to `:40`; `open-picks.txt:20` (twelve, on the entry plates); the plates' drawing in
  `release/revA/case/`.
- **Cost.** Two plates (about 151 and 142 g) with twelve spot-faces, two gaskets, sixteen M4 screws and sealing
  washers, and the twelve arrestors themselves (1361 g; the price is the pick's, TBD), which were ruled and
  recommended but never placed; twelve 27 mm and sixteen 5.0 mm holes in the case. The case becomes about 67 mm longer
  over the arrestor rows and can no longer stand on an end wall.

### C5. The QMX tray moves 1.5 mm west

- **Numbers.** Tray at X 102.0 to 171.0 (was 103.5 to 172.5): 2.08 mm inside the lid's flat ceiling, 1.70 at the
  worst (M19). It still covers the buttons at X 150.
- **Files.** `ASSEMBLY.md:46`; the lid bracket's docstring. **Cost.** None.

### No change needed, but the records are wrong

At the stated allowances the pack pocket (M4a to M6), the lift-out (M7) and the floor items (M15a to M16) meet their
minimums at the worst case. M4b, M6, M7, M15a and M16 are MET; M4a, M5 and M15b are OPEN, resting on the pack's and
the dock strip's placement by hand; the east lead band of the previous issues (M17) is retired for the jumpers' own
rows (M17a to M17x). The pack text (`ASSEMBLY.md:48`, "X +120 to +178") and `pack_4s.py`'s redesign (a session item of
D-06) should take the pocket as bounded by board A's edge at X 120 and by Peli's R 15.88 fillet and wall, with the
block's west face at X 122, the group centred in Y so that each end keeps 3.65 mm to the frame's setting legs (1.77 at
the worst, M5), and the heater mat (50 wide) at X 122.3 to 172.3, whose east edge lies 0.66 mm past the fillet tangent
where the fillet is 0.01 mm high (0.12 mm at the web's worst interior). The edits that record the owner's D-08
reversal and D-08a in the other documents are listed for their writer; this document changes none of them.

## 5. What only hardware can show (the checks)

Each runs on the new case of the current moulding bought for the prototype (D-08a), done by the assembler as
`ASSEMBLY.md` section 8 is. Section 7 recommends running them first on a targeted, unpowered mock-up, before any
board is populated. A check either confirms the OPEN rows it names, or sends them back to this document with a
measured number; a check that fails stops the build. No row of section 3 stands in for any of these checks.

| # | Check | Why no drawing settles it | Pass |
|---|---|---|---|
| T1 | Record the case's date wheel and moulded markings at purchase, and photograph the inside of both long walls and the outside of the back wall | D-08a: the design is the 2025 moulding; which long wall carries the X 0 rib and what stands on the back wall below the fairings are in no view | matches the current moulding; otherwise a new case |
| T2 | With the legs bonded to the frame and the frame on them, centred and screwed, and later the plate on it: the frame's bottom at each leg and the face top at four corners, from the floor with a height gauge; each foot against the fillet's tangent line | the floor, the ring and the rib heights carry INFERRED allowances, and the locator's 0.30 is INFERRED | frame bottom Z 84.38 to 87.62 at every leg (or at most 85.34 on the rib tops with the feet clear of the floor by at most 0.96), face top 104.77 to 108.27 at every point (two-sided); every foot on the flat floor |
| T3 | Dry-fit the plate: every 6-32 started by hand, the gap to the case wall all round, the o-ring covered all round, the lid closing over it | the kit's o-ring cross-section is in no held Peli source; the plate edge covers about 4.25 of the 6.1 mm channel in X and 5.1 of 6.9 in Y | every screw starts without forcing the plate; every gap 1.05 or more; even contact; the lid latches without load |
| T4 | Stack-up at first assembly: the monitor body to the heatsinks with a feeler; B's top copper from the floor; the pack group and the dock strip in their places against the floor fillet, the legs and the east wall; the jumper plugs' inner ends against B16's tall parts | the TBD rows of 3.1 (Xenarc depth, heatsink height, spacers); the pack, the strip and the stack are placed by hand | at least 2.0 mm at the monitor (M1); M4a, M5, M15b and M18 at or above their minimums |
| T5 | Wall thickness at each drilled hole in the end walls and the back wall (read from the hole) | Peli's sections give 5.34 at two stations only | 4.58 to 6.10 mm, the range every row of 3.2 assumes (M11d, M11g, M13b, M17c, M17w, M17x and M18 on the end walls; M14c, M14d, M14f and M14h through the connector plate's rear faces) |
| T6 | The connector plate's footprint (X -57.0 to +57.0, Z 18.3 to 86.6) on the back wall's outside and each RF entry plate's (Y -110.1 to +110.1, Z 34.55 to 83.45) on its end wall's; Peli's four frame-screw points against the outside features; the open lid against the mated plugs | the base STEP's outer skin is an envelope block; the end view shows a full-height band 3.05 proud of the skin at an X no view gives, and the end-wall features at Y 0 and +-79.0 only in outline; the screws were placed by Peli to meet the external ribs at a frame height 1.42 lower | every plate and gasket on plain skin all round; each screw into an external rib; the lid opens without touching a plug |
| T7 | Seals: TEST-PLAN E6 (immersion, closed) and E7 (driven rain, deployed, lid open), the twelve arrestors and the two entry plates included | a seal is proved only by water, and the arrestor's sheet gives no ingress rating | no water inside |
| T8 | Floor flatness under the pack, the dock strip and the four feet; a VHB 5952 bond test on the case's polypropylene with and without primer, and on the 1450PF's polymer under a leg's pad | the STEP floor is an ideal plane; 3M lists polypropylene as low surface energy; the frame's polymer is not stated | pads hold through E1 and E2 |
| T9 | Lid closure over the tray, the buttons and the toggles (chalk on their tops) | the buttons' height above the face and the tablet bracket are TBD | no mark on the lid |
| T10 | The jumpers, crimped on the picked right-angle plug and cut to their routes, laid and tied. Under the east plugs: each plug's turn, the place of its own cable and of the cables passing it (M17g), and the inboard column against B16's edge (M17x). Then the bundles past the next plugs, through the lane, past the legs and onto the floor (M17b to M17f), and the west drops (M17w) | the plug's cable axis, ferrule reach and ferrule diameter are on no held sheet, and a bundle's place is set by hand and by its ties | every bend at R 12.5 or more by gauge; every cable 1.0 or more from B16's edge and tall parts, the plug bodies and the legs, and off the dock strip; none pinched or pulling on its plug |
| T11 | One arrestor tightened on the bench with its O-ring, lock washer and nut on the RF entry plate, or on a 6.0 coupon spot-faced as drawn: the thread's end against the nut's outer face, the O-ring's installed height, the nut and washer across and thick | the O-ring, the washer and the nut are drawn but not dimensioned, and the drawing says all its dimensions are for reference only | the thread's end at or beyond the nut's outer face (M13); the nut and washer within 24.0 across and 5.0 thick, inside the 26.0 spot-face (M13b to M13d); the O-ring compressed evenly all round |

## 6. Carried TBDs

| Item | Enters | Closes by |
|---|---|---|
| Xenarc 709GNK body depth tolerance; its steel rear frame | M1 | the maker's drawing (lookup) |
| CM5 heatsink height from a Raspberry Pi drawing (21.0 is the render scene's) | M1 | lookup |
| Gap and bay spacer parts and tolerances | M1, M6, M14e, M14g | the session names the parts |
| C&K ATP19/ATP16 height above the panel; APEM 5636 lever height | M3, T9 | the makers' sheets |
| The sealed RJ45 coupler: a MIL-DTL-38999 shell 15 wall-mount envelope (flange 31.29 square or less, four holes of 3.35 or less on 24.61, body through a 29 mm hole, rear 16.51 or less behind the flange, mated 32.51 across or less, the shell 15 plug class) rated for the 54 V PoE feed (`ASSEMBLY.md:104`); the recommended PX0833 fails both on its own sheet | C3, M14a, M14e, M14f, M14j to M14m | a maker's drawing, before the plate is cut (`open-picks.txt:13`) |
| The Cat 5e patch plug inside: straight or right-angle, body within 40.0 of the coupler's rear face and +-8 about its centre | M14e, M14f | the lead's part, before it is made |
| The sealed USB-C: the PXP4043/C's own panel drawing (neither held Bulgin sheet gives one) within the 4000 series body the PXP4043 sheet draws (hex 22.23 A/F, cut-out 19.2, 24.8 overall, 7.0 behind the panel, panel 6.2), its rear flange 26 or less and its lead 7.0 or less and bendable at R 28; its body's diameter in the 19.2 cut-out (0.30 of float assumed); on which face of the plate the panel seal the PXP4043 sheet draws (22.5 across) sits, and how thick it is (behind the plate at most 1.2, the 6.2 panel range less the 5.0 plate) | C3, M14g, M14h, M14j, M14k | the maker's drawing (lookup), before the plate is cut |
| The right-angle USB-A plug for the 233-370's internal lead (body within 20.0 of the feed-through's rear face, cable down) | M14c | a maker's drawing, before the lead is made |
| The M8 pod receptacle (binder 86 6618 1121 00004 recommended, sheet not held): a panel of 5.0 or a counterbore to 3.0 behind it, a nut of 13 A/F or less, a rear of 15 or less behind the plate's face, its M10 x 0.75 body in a 10.5 plate hole (0.33 of float, which the pod follows) | C3, M14j, M14k | the maker's sheet (lookup) |
| The pod: 28 x 28 on the plate, 30 proud or less (INFERRED class) | C3, M14j | the pod's drawing |
| The ground stud: M6 class, the stud in a 6.4 plate hole, outside hardware within 24 across, inside within 12 (INFERRED) | C3, M14j, M14k, M14n | the part (`open-picks.txt:16`) |
| The hinge fairings' extent down the back wall between \|X\| 58.93 and 87.34, and the back features the end view shows at X no view gives (#7072, #7105, #6704) | M14i (C3 stays inside \|X\| 57.0) | T1 photos, T6 |
| The open lid's position against the mated plugs on the back wall (Peli gives no open-lid geometry) | C3 | T6 |
| The 1450PF's polymer: its bearing strength under a leg's pad and a VHB 5952 bond on it | C6 | Peli (lookup), or a pad test with T2 and T8 |
| The legs' printed locator: 0.30 against the window assumed, in X and in Y at once | M5, M21a to M21h | T2 |
| Peli o-ring cross-section | T3 | the kit, at the build |
| Whether the Y +-79.0 end-wall features stand proud or are recessed | M12 (the entry plate's top clears them either way) | T1 photos |
| Which long wall carries the X 0 rib | M14n (C3's holes C and D cut it if the back wall carries it; nothing bears on it) | T1 photos |
| Moulding tolerances of the case itself (the drawing says only "typical industry-standard tolerances apply") | every row that carries a case allowance: the allowances used are INFERRED, and a row that does not survive them doubled is OPEN (section 1, Verdicts) | the mock-up (T2 to T6, T8), section 7 |
| Positions of the mixer fans, the water electrodes and the sensor modules | the legs' zones (C6); the jumpers' routes (section 3.4): the slot over the pack's outer strip and the lanes past the legs, the east corners beyond them, the west drop zone (X -165 to the wall, \|Y\| up to 98, floor to Z 54) and the floor runs to the clamps | the floor plan when they are drawn |
| The arrestor's O-ring, lock washer and nut, which its sheet draws but does not dimension, on a drawing whose dimensions are all for reference only. The O-ring sits on the thread's root, about 0.63 proud of the body's face (scaled), and is installed anywhere from seated to that height (no gland is drawn, no torque stated). The nut is 19.1 across its flats and the washer 20.5 across, about 4.7 thick together (scaled): the class is 24.0 across and 5.0 thick, which a 5/8-24 UNEF nut and lock washer can meet if PolyPhaser's do not. Its panel range | M13 (OPEN on the O-ring: met with the thread's allowance doubled for one installed up to 1.32), M13b to M13d, M11a (the 27 mm holes), and through where the O-ring puts the inner jack M18, M17c, M17w, M17x | PolyPhaser (a lookup by the session; polyphaser.com refused the runner's request on 26 Sep 2026), before the plates are drilled; then T11 |
| The jumpers' right-angle SMA male crimp plug for RG-316 (`ASSEMBLY.md:134`): mated, at most 10.0 beyond the arrestor's inner jack and 5.0 about its axis; its cable leaving square to that axis, the cable's axis within 4.0 of the plug's inner end; its crimp ferrule ending within 16.0 of the mating axis; free to be turned about the jack before its nut is tightened (east: 30 degrees below the wall's direction toward the bundle's end; west: cable downward). Not in the class, and deciding how the east cables lie under the plugs: the ferrule's diameter and the offset of the cable's axis from the plug's inner end. M17g and M17x are met for a reach of 13.58 or less (or 5G MAIN turned 26.5 degrees) and an offset of 1.38 or more with a ferrule 2.58 across or less; the class as written admits picks on both sides | M18, M18c, M17b, M17c, M17g, M17x, M17w | the part's drawing (lookup), before the jumpers are made; then T10 |
| The jumpers' way to E6's clamps: which way each clamp's cable leaves (south for the four east front jumpers, north for LORA's and the seven west jumpers); a lane across E6's south part at each front clamp's X (X 46, 60, 74 and 88) whose parts let the jumper pass over them and still enter A22's 13.4 mm gap at R 12.5; the lanes on the floor under A22 north of E6 and along the west wall's foot to Y -35, clear of the rods, the sensor modules, the fans and their leads. The jumpers share the west wall's foot and the front wall's floor with the shore lead, which is tied along the back, west and front walls (`ASSEMBLY.md:92`), and with the pack's power lead along the front wall (`:70`, `:90`) and its SMBus lead (`:91`) | M17f, the lengths of section 3.4 | E6's placement (`gen_pcb_e3.py`) and the floor plan, before the jumpers are cut |
| The jumpers' lengths, 232 to 412 mm on the route (252 to 432 cut) against the 150 to 250 of `ASSEMBLY.md:134`: the RG-316 loss each link budget takes at its own length and band (no RG-316 sheet is held) | C2 | the link budgets, recorded elsewhere, with a cable sheet (lookup) |
| The east bundles' ties: what holds each bundle in the slot and the lane within +-0.5 (INFERRED), for example tie bases bonded to the pack's wrap or to the end wall | M17a, M17b, M17d to M17f | `ASSEMBLY.md`, when the route is drawn |
| The RF entry plates' ground: one lead from each plate to stud F outside, its route round the back corners, the lug stack on F, and the bond it adds beside the one strap of `GROUNDING-AND-SHIELDS.md` item 4 (whose line 39 has every SMA body on plastic) | C4, F's outside hardware | `GROUNDING-AND-SHIELDS.md`, before the plates are made |
| TEST-PLAN E1's drops onto an end wall land on the arrestor bodies, 43.9 mm off the skin: a guard on each entry plate or a stated exclusion, and the arrestors' own ingress rating (none on their sheet) | C4, T7 | the session, before E1 runs |
| The entry plates' M4 sealing washers (10 across, 1.5 +-0.10 thick, a rubber face at least 8.0 across that covers a 5.0 hole: the rubber-faced type, not a bonded seal whose rubber stops near the thread) and ISO 7380 button heads (2.2 high, length js15); the connector plate's bonded sealing washers (10 across, 1.5); the 6-32 pan heads (6.86 across, ASME B18.6.3 class) on the face plate; no tightening torque is stated for the entry plates' M4 x 12, which engage 1.95 of tapped aluminium at the worst (M11g, against an INFERRED minimum of two pitches) | M11d to M11g, M14p, M4c, M21g, M8h | the parts (lookup), the torque from the sealing washer's maker |
| RG-316's jacket: 2.49 is MIL-DTL-17's nominal 0.098 in; if its +-0.004 in applies (INFERRED, standard not held), a cable is up to 2.59 across, which no chain carries | M17a to M17x | a cable sheet (lookup), with the link budgets' |
| The two WIFI P2P antennas, moved to the west wall's +62 and +93 sites beside the SDR's and the GNSS's (C2): their placement against the other west antennas; `V2-SPEC.md:42` still gives the kit-to-kit link two east jacks | C2 | the RF budget, recorded elsewhere, before the plates are drilled |
| How the shrink-wrapped pack is held against E1 and E2 | M4a to M6 (placement +-1.0 assumed) | the pack redesign of D-06 |

This document covers the case geometry only. The A-to-D8 bay, A's J_AB2 header under D8, the LoRa blind-mate X
on board E and the thermal and RF budgets are board and integration items recorded elsewhere. No row here judges the
blind-mate between board A and the dock strip or its alignment: its 13.4 mm gap enters M1 only as a height.

## 7. Closing the OPEN mechanical items

Every OPEN row of section 3.2 and every TBD of section 6 is listed below with the evidence that closes it. Two kinds
of evidence close them:
- a maker's drawing or a pick, which the session looks up before the part is made or bought;
- measurement on hardware: the checks T1 to T10 of section 5.

For the second, the session recommends a **targeted, unpowered mock-up** for the build stage. It would be built when
the new 1450 of the current moulding is bought for the prototype (D-08a), before any board is populated. The review
of 26 September 2026 notes that such a mock-up "can resolve expensive mechanical uncertainties earlier than a fully
populated seven-board build" (`v2/docs/reviews/2026-09-26-foundation-progress-review.md:79`).

This is the session's recommendation for the build stage, not a request. The owner withdrew the earlier request that
he measure his old case (D-08, reversed on 26 September 2026), and nothing in this document asks him to measure or
build anything now. Buying the case and the mock-up's parts stays his decision at the build.

**What the mock-up holds.** Nothing in it is powered, so a check that fails costs no board.
- The case itself (T1 at purchase), its 1450PF frame and o-ring, with the holes drilled from the 1:1 templates.
- The parts this document specifies, made to their drawings: the four setting legs with their locator and wedge set
  (C6), the face plate (C1), the connector plate and the two RF entry plates with their gaskets (C3, C4), and the lid
  tray (C5).
- The bought parts whose geometry decides a row, each a part the prototype needs anyway: the twelve arrestors with
  their nuts, the jumpers' right-angle plugs crimped on RG-316 and cut to their routes, the connector plate's six
  items and their mates, the Xenarc 709GNK and a Compute Module 5 heatsink.
- Stand-ins for what is not yet made: blanks at the outlines and stack heights of A22, B16 and E6 (on the named
  spacers and the dock strip's VHB pads), blocks at the envelopes of B16's tall parts (the RockBLOCK, the LimeSDR,
  the heatsinks, U51), and a block of the 4S3P pack group's outline in its planned hold-down.

**What closes each OPEN row** (the verdicts and bounds are section 3.2's):

| OPEN rows | What they rest on | Closing evidence |
|---|---|---|
| M1 | the Xenarc body's tolerance and rear frame, the heatsink's height and the spacers (TBD); the floor under a leg, the frame's ring and the board's bow | lookups: the Xenarc's drawing, a Raspberry Pi drawing of the heatsink, the spacer parts; then T4 with the real monitor and heatsink |
| M3 | the C&K button and APEM lever heights under the tray (TBD); the rim, floor and ring heights | the makers' sheets (lookup); then T9 |
| M2, M2b | the rim, floor and ring heights; the lid's cavity and its place on the base | T3 and T9: the plate dry-fitted, the lid closed over it |
| M8 (M8x, M8y), M8z | the case's width in the rim zone and the shoulder's height; the ring; the frame's centring | T2 and T3 |
| M20, M21b, M21c, M21d, M21e | the floor under each leg and the ring (the seat); the legs' locator and the frame's centring | T2: the frame on its legs, centred and screwed, measured from the floor, each foot against the fillet's tangent |
| M4a, M5, M15b | the pack's and the dock strip's placement by hand | the pack's hold-down (D-06's redesign) and the strip's locating (the floor plan); then T4 |
| M14a, M14b, M14i, M14m | the case's heights at the back wall, the fairings' extent down it (TBD), and holes and plate marked by hand | T1 photos and T6; a drilling jig in place of the 1:1 template would make the marking a stated tolerance |
| M10, M11c, M11e, M13c | the skirt's height over the floor; holes and plates marked by hand | T2 and T6 |
| M11d, M11g | the end wall's thickness at the holes; the gasket's compression | T5, the wall read from each hole; a gasket with compression limiters would make its thickness a stated tolerance |
| M13 | the installed height of the arrestor's O-ring, which its drawing shows on the thread's root, about 0.63 proud, but does not dimension (its dimensions are all for reference only) | PolyPhaser's dimensions (lookup); then T11, one arrestor tightened on a spot-faced coupon |
| M18 | the wall, the gasket and the O-ring in the plug's reach; the stack's placement | T4, T5 and T11 |
| M17g, M17x | the jumper plug's reach, ferrule diameter and cable-axis offset, which no held sheet gives (the bounds are in section 3.4) | the plug's drawing (lookup), which sets each east plug's turn and the layering under the plugs; then T10 with the picked plug |
| M17a, M17b, M17c, M17d, M17e, M17f, M17w | the bundles' ties; the floor under the pack and the plates' marking; the stack's and the strip's placement; the wall and the gasket; the legs' locator | T10 with the picked plug and RG-316, on the floor T8 reads and the plates T6 places |

**Section 6's TBDs** close the same two ways:
- **By lookup or a pick** (the session, before the part is made or bought): the Xenarc's drawing, the heatsink's, the
  spacers, the C&K and APEM sheets, the sealed RJ45 and USB-C drawings, the patch plug, the right-angle USB-A plug,
  the M8 receptacle, the pod, the ground stud, the arrestor's O-ring, nut and washer, the jumper plug, the fasteners
  and washers with the entry plates' torque, the 1450PF's polymer (Peli), RG-316's sheet with the link budgets, and
  the RF placement of the WIFI P2P antennas.
- **By the floor plan and the drawings still owed:** the positions of the fans, water electrodes and sensor modules;
  the jumpers' way to E6's clamps and the floor lanes they share with the shore lead and the pack's leads; the
  bundles' ties; the entry plates' ground lead; the pack's hold-down; and the guard or exclusion for TEST-PLAN E1's
  end-wall drops.
- **By the mock-up:**
  - the fairings' extent down the back wall and the back features (T1, T6);
  - the open lid against the mated plugs (T6);
  - the legs' locator (T2) and Peli's o-ring (T3);
  - one arrestor on its plate or a spot-faced coupon (T11);
  - whether the end-wall features stand proud, and which long wall carries the X 0 rib (T1);
  - the case's own moulding tolerances (T2 to T6, T8).

**What the mock-up cannot show.** It shows fit, seating and clearance on one case, and it does not qualify the kit.
- Seals are shown only by T7's water tests (TEST-PLAN E6 and E7). Those can run on the mock-up with nothing inside
  that a leak can harm.
- Every electrical, thermal and RF item is outside this document.
- One case is one sample of Peli's moulding. For the prototype, the measured case is the case it is built in. For
  further kits, a row the mock-up shows to be thin needs more room in the design, or more cases measured.
