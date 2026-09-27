# QMX lid tray r2: the tray, its retaining frame and its lid plate (supersedes `../lid-tray-qmx/` and sheet 14)

MESHSAT-1357, pre-PCB layer 7 (mechanical and enclosure), open item S-63 and ENGINEERING-QUESTIONS EQ-24. **Prototype design: nothing in
this folder has been made, printed, bought or fitted.** This set stands beside the case release of 27 September 2026 as a folder of its
own with its own `MANIFEST.sha256`. **No file of the release is edited for it:** `../README.md`, `../MANIFEST.sha256`, the r1 tray in
`../lid-tray-qmx/` and sheet 14 keep their bytes, and the release's manifest does not list this folder. The r1 tray and sheet 14 are
**superseded by this set and not to be printed**; the pages that say so are outside the release (`v2/cad/README.md`, and the registry
and document changes drafted in `v2/docs/records/w5tray/drafts/`). The editable sources govern: `v2/cad/lid_tray_qmx_r2.py` (the parts
and the one table of solids), `v2/cad/lid_tray_qmx_r2_check.py` (the record in `lid-tray-qmx-r2-check.out`),
`v2/cad/lid_tray_qmx_r2_drawing.py` (sheets 14r2-1 to 14r2-3).

## Why r1 is replaced, and why the first pass of r2 was not released

The r1 tray of 9 September 2026 (`../lid-tray-qmx/`, sheet 14) had its two cable notches in one end wall, while the QMX has jacks on
both end panels: Paddle, Audio and DC on the left, RF (BNC), PTT and USB-C on the right (operating manual 1_04_004 pages 7 and 8). Its
95 x 63 x 25 came from no maker document the tree held, it held the unit by one hook-and-loop strap threaded under a floor that lies on
the lid, it was PETG (heat deflection 68 C at 0.45 MPa, Prusament's sheet) under TEST-PLAN E3-S's +71 C storage, and its fixing named
PEM self-clinching nuts in a 2 mm ABS plate, a pairing that needs a metal host.

A first pass of r2 (27 September 2026, recovered in `v2/docs/records/w5tray/`) opened both end panels but held the unit under ledges and
end lintels that were part of the tray, the unit slid in from one end. Its checker (an AI review) judged it not mergeable on two items:

- **B1, the unit could not be fitted.** The lintel at the entry end stood at the height of the unit's top face, and the knobs, the
  encoder shafts and the button actuators stand above that face. The check had tested only the seated unit.
- **B2, the face-room limits were wrong.** The row for the face plate's three buttons measured their room from the unit's top face,
  29.30 below the lid ceiling, while all three stand under tray solids 31.30 below it; and the sensitivity column left out the set's own
  allowances.

This set answers both. The unit is now **lowered into an open pocket from above and a retaining frame is screwed over it**, and every
face-room row is **derived from the deepest solid over the part**. The record runs the first pass's tray through the same two checks as
controls, and both fail as they must.

## The unit, from the maker (`v2/vendor/qrp-labs/`)

| Fact | Value | Source |
|---|---|---|
| Enclosure | 95 x 63 x 25 mm without protrusions | `qmx-product-page-2026-09-27.txt` (qrp-labs.com/qmx.html, updated 24 Sep 2026); assembly manual 1.04r page 3 ("measuring just 95 x 63 x 25mm") |
| Mass | 220 g with the enclosure | the product page |
| Panels, fixings, feet, knobs | left and right end panels held by eight "small black countersunk screws"; four self-adhesive rubber feet (fitting optional); two knobs listed "15mm", held by grub screws with "a small gap" to the top face | assembly manual 1.04r pages 20, 21, 76 and 77 (`qmx-assembly-1_04r-pages-1-3-20-21-75-78.pdf`) |
| Jacks | left: Paddle, Audio (3.5 mm stereo), DC (2.1 mm barrel, centre positive); right: RF (BNC), PTT (3.5 mm), USB-C | operating manual 1_04_004 pages 7 and 8 |
| Controls | VOL and TUNE encoders with push, two buttons, the LCD window; the VOL knob is pressed to switch the radio on and off | operating manual 1_04_004 page 13 (section 4) |

Where each jack, knob, button and the LCD window sits is **scaled** from the maker's undimensioned figures, which come out at the maker's
63 x 25 within 0.4 percent, and cross-checked for the right panel on the maker's photograph (`measure_qmx_figures.py`,
`qmx-figures.out`). The RF jack reads 12.1 mm from the knob edge on the figure and 8.3 on the photograph; every jack is taken over the
range of both, widened by 0.5. **What stands proud of the enclosure is dimensioned by no maker document** and is read from the maker's
photographs (assembly manual page 77, photographs 13 and 15 of the sibling QCX-mini in the same enclosure family; the right-panel product
photograph), each INFERRED: the knobs 11.6 high and 18.0 across with their skirt, the button actuators about 2.0 high, the RF jack's nut
16.5 across its corners with its barrel 14 out of the panel, the 3.5 mm jacks' bushings 8.0 across and 3.0 out.

## What the set does (the session's choices under the owner's standing rule of 26 September 2026)

Each choice is the session's (`authority: SESSION`), never the owner's; its reason and what reverses it:

1. **Both end panels open over their whole height above a 1.5 mm sill; under the RF jack the sill is cut down to the floor.** Every
   jack takes its plug from any side, no uncertainty in the scaled jack places can put a jack behind a wall, and the long walls stop
   1.5 short of the end faces so that no wall stands beside a plug. The cut under the RF jack admits a plug body of d 20.0 where the
   first pass admitted d 16.0, less than the jack's own nut. Reverse by a maker's dimensioned panel drawing that shows an end wall can
   stand somewhere without meeting a jack's plug.
2. **The unit lies top face out, knob edge west, its right panel toward the hinge** (unchanged from the first pass). The LCD, both
   knobs and both buttons face the operator with the lid open; the RF and USB leads leave toward the lid harness at the hinge, the DC
   lead loops back. Reverse by a lead route that needs the other end at the hinge.
3. **The unit is lowered in from above and held by a screwed retaining frame.** The tray is an open pocket: a floor, two long walls
   buttressed by five posts each on a flange as thick as the sills, and a sill at each end. The frame is a flat printed ring, 3.0 thick,
   laid on the wall tops and held by six M3 x 10 button-head screws into square nuts in slots of the posts; its ledges reach 4.0 over
   the back edge, 3.0 over the knob edge in three stretches clear of both knobs with 6 mm of finger room, and 3.0 over each end. Two
   Rogers PORON 4701-30 pads press the unit up against the ledges, compressed by screwing the frame down. Reason: nothing of the tray
   stands in the unit's way in, the pads are never slid over, and the frame's bending lies in its printed layers. Reverse by E1 or E2
   showing a lighter retention holds, or by a unit without knobs above its top face.
4. **Printed in Prusament PC Blend** (heat deflection 113 C at 0.45 MPa and 93 C at 1.80 MPa, `v2/vendor/materials/`), not PETG
   (68 C), because TEST-PLAN E3-S stores the kit at +71 C. Neither printed part has an overhang; the only bridges are the six nut
   slots' roofs, 5.8 wide. Reverse by a material with a maker's heat deflection above the stored +71 C and a stated interlayer
   strength at least as high.
5. **Fixed through a 2.0 mm 5052-H32 aluminium lid plate tapped M3 through, bonded to the lid's unribbed inner face with 3M DP8005**
   (`v2/vendor/adhesives/`): no hole in the case (the ruling of 7 September 2026); ten flush countersunk M3 x 5, each tip 0.6 short of
   the plate's back face. Reverse by a bonded fixing whose strength on the case's polypropylene a maker states.
6. **All sixteen M3 tightened to 0.25 N m** (INFERRED), not the 0.4 N m of the r1 row, which would load 1.4 mm of thread in 5052 to
   67 percent of what it strips at. Reverse by a torque test on a coupon of the plate.
7. **The load case is stated: 100 g on the unit and its plugs, 235 N, in each of the six directions.** It is the peak CASE-MARGINS.md
   already assumes for the face under TEST-PLAN E1; it is an assumed peak, not a measured one. Reverse by E1 with an accelerometer on
   the lid.
8. **The place:** the east edge stays at X 171.0 (C5; M19 unchanged, 2.08 nominal, 1.70 at the worst); the set grows west to X 83.2
   for its posts, where the lid's ceiling is free (the tablet bracket keeps the west third); Y 10.0 as r1, so Y -45.9 to 65.9. Reverse
   by a lid item that needs X 83.2 to 102.0.

## Files

| File | What |
|---|---|
| `lid-tray-qmx-r2.step`, `.stl` | the tray, 111.8 x 87.8 x 27.1, 55798 mm3, 68.1 g in PC Blend |
| `lid-tray-qmx-r2-frame.step`, `.stl` | the retaining frame, 101.0 x 87.8 x 3.0, 10014 mm3, 12.2 g in PC Blend |
| `lid-plate-qmx-r2.step`, `.dxf` | the lid plate, 111.8 x 87.8 x 2.0, R6, ten M3 tapped through (layers OUTLINE, TAPPED_M3_THROUGH, NOTE), 52.2 g |
| `lid-tray-qmx-r2-drawing.pdf` | sheet 14r2-1 (the place on the lid, the section with the lid closed, both end panels and their plugs), sheet 14r2-2 (the three made parts dimensioned, the holes, hardware, masses, print) and sheet 14r2-3 (fitting, operation, what stays open, and the record's face-room and retention rows) |
| `lid-tray-qmx-r2-check.out` | the record: sections A to E and the checks on the solids |
| `MANIFEST.sha256` | the sha256 of every file of this folder (`sha256sum -c MANIFEST.sha256`, run here) |

The three sheets were rendered to images at 110 dpi and read back before this folder was written (an AI read-back of legibility and of
the figures against the sources). Notes are set at 7.4 pt, tables at 6.0 pt and more, labels in the views at 5.2 pt and more.

Hardware the set needs and does not contain: ten M3 x 5 countersunk hex socket screws (ISO 10642 class, A2), six M3 x 10 button-head
hex socket screws (ISO 7380-1 class, A2), six M3 square nuts (DIN 562 class, A2), two pads of PORON 4701-30 (320 kg/m3, 3.18 mm, 24 x
20), 3M DP8005. The three standards are not held; their head and nut sizes are class figures (INFERRED).

## What the record shows (`lid-tray-qmx-r2-check.out`)

- **A. Every jack is reachable with its plug.** The set admits, at the worst of each jack's scaled place: DC d 18.8, Audio and Paddle
  d 12.0, RF d 20.0, PTT d 10.8, USB-C 8.6 high. The right panel is 58.43 from the lid's flat ceiling edge: the RG-316 jumper turns at
  R 12.5 (the tree's figure) with its plug up to 42.9 long, the USB-C lead at R 20 with its plug up to 35.4. The left panel is 78.43
  from it: the DC lead loops back at R 20 west of the tray with its plug up to 55.4. The admitted bodies and R 20 are the requirement
  on the harness picks (not picked).
- **B. Face room with the lid closed, from the solid above each part.** Eighteen face parts lie under the set or its plugs; each row names the deepest
  solid over the part's footprint, its depth from the lid ceiling and the part's height above the face from its maker's sheet, and
  carries the set's own allowances (bond line 0.10, lid plate 0.13, printed height 0.20, on the frame also 0.20; none stated by a
  source, so the sensitivity reading takes each twice). **No row is NOT MET.** The three buttons stand under the frame, 32.30 below the
  ceiling, with heads of 3.50 (C&K ATP19, S actuator, head 2.00 on its 1.50 O-ring) and 2.50 (ATP16, 1.5 on 1.0): margins 12.12 and
  13.12 nominal, 7.96 and 8.96 at the worst, 5.05 and 6.05 at the sensitivity reading, MET. The eleven status light guides and the
  light sensor's stand 1.50 (Mentor 1282.5004) under the unit's top face, the frame's front-end bar or a sill: 7.05 and more at the
  sensitivity reading, MET.
  **The knob tips are the deepest solid, 40.90 below the ceiling, and their rows are OPEN:** over the flat face 7.02 nominal, 3.06 at
  the worst, 0.35 at the sensitivity reading; over the monitor's window, whose east edge the knobs' west rims overlap by 2.6 and whose
  glass may stand 0.8 proud at most, 6.22, 2.26 and -0.45. Both rest on the knob's INFERRED 11.6: they are MET at the sensitivity
  reading for a knob up to 10.15 and at the plain worst for a knob up to 12.86.
- **C. Pads:** PORON 4701-30 3.18 compressed 34 percent nominal, 13 to 51 percent over the tolerance corners: the unit always stands
  on them and never reaches the floor's stop (0.10 left at the lowest). The sheet states the pads' force at 25 percent only, 20 to 53 N.
- **D. Retention, designed to 100 g (235 N).** On the makers' typical figures less their stated spread every link holds 7.1 times
  the load case or more; the governing link is the back frame screws, prised by 3.67 on the posts' outer edge, where a button head
  bearing on the frame holds 1019 N: 707 g. The half-sine bound of E1's 1.22 m drop gives 958 g at 2 mm of stopping distance and 96 g
  at 20 mm, so the known links hold for 2.7 mm and more and the bound includes failure: **the verdict against E1 stays OPEN.** The lid
  plate's bond on the case's polypropylene is bounded by no held figure. Against E2 (MIL-STD-810H 514.8, composite wheeled vehicle,
  2.24 g rms, 6.72 g at 3 sigma at the case) the pads' preload keeps the unit seated up to 8.6 to 22.4 g, so it stays seated if the
  lid magnifies the case's vibration by less than 1.3 to 3.3; the lid's response is not known. The preload bends the frame's ledges all
  the time: 0.45 to 1.17 MPa at the sheet's 25 percent figures, between the loads of the material's two heat deflection figures, both
  of which are over +71 C; at the pads' real compression it is not bounded.
- **E. The fitting.** The unit at its largest (0.2 on each overall dimension, everything proud of it 0.5 wider and further out) keeps
  0.30 to every solid of the tray on its way down, and the frame keeps 4.15 to everything that stands proud of the unit; the stated
  minimum is 0.20, the printed parts' own tolerance. **Control 1:** the first pass's tray with its documented way in fails, its
  keeper-end lintel 2.50 inside the knobs. **Control 2:** the first pass's row for the buttons fails against the solids of its own
  tray, 2.00 too shallow for each of the three.
- **On the solids** (build123d 0.13.0): the table of solids is what was built (nothing of either part lies outside it, the bounding
  boxes are the same, and the deepest point of the built set over every face part is section B's); the unit, 24 plug bodies at the
  corners of their jacks' places, four USB overmolds and both knobs' finger room touch neither printed part; the unit and the frame
  meet nothing at any of 31 positions of their way in; three controls that must intersect do.

## What stays open (carried, not closed by this folder)

- **The lid harness's crossing of the sealed face plate is not designed anywhere in the tree.** The QMX's DC lead, USB-C lead and
  RG-316 jumper leave the tray for the hinge side and must reach board B's `J_QMX` and board A's `J_HF` and `J_RF2`, which sit under
  the face plate. The plate lies on the 1450PF frame over Peli's o-ring and covers the whole frame window; it has no pass-through, and
  ASSEMBLY.md ties the harness along the hinge side without saying where it crosses the face. Options: (a) a sealed panel-mount
  connector set in the plate's top strip near the hinge, the lid half of the harness plugging into it; (b) a sealed cable gland in the
  plate with the harness permanent through it. **It blocks:** the harness picks (lengths, the lid-side connectors), ASSEMBLY.md's lid
  harness steps, closing the lid on a wired QMX, and with it E6, E7 and E8 for a kit with its QMX connected; it needs a new face-plate
  version and a new case release. It does not block printing or fitting this set, and it moves no board connector. Not solved here.
- **Retention verification:** the bond (CASE-MARGINS T8, a pull test of the bonded plate on the case's polypropylene, after a thermal
  cycle) and the peak (TEST-PLAN E1 with an accelerometer on the lid). No board, interface or purchase depends on it: the remedy is a
  made part (the same parts machined in 6061, or a larger bonded plate).
- **The knob height** (T9, chalk on the knob tips with the lid closed, or the unit in hand): the two knob rows are OPEN. If the knob
  proves taller than 12.86 the remedy is a lower knob or a lid plate cut out under the unit, which lowers it by about 2.2 (not drawn).
- **E2:** the lid's response and the pads' preload at their real compression; the frame's and the tray's screws are checked for
  loosening, the unit's top edges for fretting. **E3-S and E4-S:** the frame flat on the wall tops and the unit still clamped after the
  soak (the pads' compression set, the screws' preload on printed seats), no crack at the ten tray screws (no expansion figure of PC
  Blend is held).
- **The unit's own heat in the pocket** is not assessed: the tray covers the enclosure's bottom and long sides, and no dissipation
  figure of the maker's is held.
- **The harness picks** against the admitted plug bodies and R 20, and **a threadlocker** its maker states compatible with
  polycarbonate: none is named.
- **`panel1450.QMX_TRAY_X` and `v2/cad/render/scene.py` still carry the r1 tray** (X 102.0 to 171.0): the r2 place lives in
  `lid_tray_qmx_r2.py`. `v2/vendor/peli/frame_seat.py` still subtracts the r1 tray's 28.0 in M3; the change that makes it read the r2
  stack is drafted (`v2/docs/records/w5tray/drafts/apply_frame_seat_r2.py`) and changes `frame_seat.out`, after which this record's
  first line and one sentence of section B read differently when regenerated.

## Source revision

Generated from commit `1f26c1f2` of branch `fnd/w5tray` (from main `c23c5e76`), on 27 September 2026 (21:45:52 to 21:46:18 UTC), by
`v2/cad/build_lid_tray_r2.sh` on the rented CAD box (Ubuntu 24.04.5 LTS, Python 3.12.3, x86_64), in a fresh venv whose `pip freeze`
equals `v2/cad/requirements-cad.lock` line for line (build123d 0.13.0). Inputs, sha256 first 16:

| File | sha256 (16) |
|---|---|
| `v2/cad/lid_tray_qmx_r2.py` | `f424d76a363fbf9a` |
| `v2/cad/lid_tray_qmx_r2_check.py` | `210d43d126fa1461` |
| `v2/cad/lid_tray_qmx_r2_drawing.py` | `61ee03392ae32a19` |
| `v2/cad/build_lid_tray_r2.sh` | `b7dc30eb5dd19349` |
| `v2/cad/drawing_kit.py` | `49e7f00d7d57893f` |
| `v2/ecad/tools/panel1450.py` | `3bdb88df98260244` |
| `v2/vendor/peli/1450/frame_seat.out` | `a65c0792a7a08c08` |
| `v2/vendor/qrp-labs/measure_qmx_figures.py` | `3edbc2f840becc81` |
| `v2/vendor/qrp-labs/qmx-figures.out` | `ec891c826be2d19b` |
| `v2/vendor/qrp-labs/qmx-operating-manual-1_04_004.pdf` | `7d2616cdcadd2f7c` |
| `v2/vendor/qrp-labs/qmx-assembly-1_04r-pages-1-3-20-21-75-78.pdf` | `ece9bed53713d5fa` |
| `v2/vendor/qrp-labs/qmx-product-page-2026-09-27.txt` | `ea72e0782d8ef822` |
| `v2/vendor/qrp-labs/qmx-product-photo-qmx4-right-panel.jpg` | `4eab70ca5c51f1d3` |
| `v2/vendor/materials/prusament-pc-blend-tds-v1.1-2022-02-16.pdf` | `25f7aa7b99cc24e5` |
| `v2/vendor/seals/rogers-poron-4701-30-very-soft.pdf` | `9567c83b0d8d9e97` |
| `v2/vendor/adhesives/3m-scotch-weld-dp8005.pdf` | `90fdb06a6289827e` |
| `v2/vendor/switches/ck-atp19-series-datasheet.pdf` | `ebf7ad2c6da083b2` |
| `v2/vendor/switches/ck-atp16-series-datasheet.pdf` | `fce6061e05364e61` |
| `v2/vendor/mentor/mentor-ll14-14-ip68-front-panel-light-guides.pdf` | `a07164ab7b6d31bf` |
| `v2/vendor/standards/mil-std-810h-method-514-8.md` | `2b63b2122fc00f8d` |
| `v2/vendor/standards/mil-std-810h-method-516-8.md` | `f6e0c9e663ae1e3d` |
| `v2/cad/requirements-cad.lock` | `32f887be3a68bb56` |

Regenerate: `PY=.venv-cad/bin/python v2/cad/build_lid_tray_r2.sh <out dir>` (v2/cad/README.md), then
`python3 v2/cad/case_manifest.py <out dir>/lid-tray-qmx-r2`. A second build of the same commit on the same box half a minute later
gave both STL files and the check record byte for byte; the three STEP files differ in their time stamp, the DXF in its dates and the
PDF in its creation date.

## Review

AI review only: the choices and checks here were made by an agent session, after an AI checker's findings on the first pass. No
qualified mechanical engineer has reviewed the set; the case release's review route (`../margins/CASE-FIT-UNCERTAINTIES.md` section 5)
covers it.
