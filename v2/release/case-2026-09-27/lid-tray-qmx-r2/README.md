# QMX lid tray r2: the tray, its keeper and its lid plate (supersedes `../lid-tray-qmx/` and sheet 14)

MESHSAT-1357, pre-PCB layer 7 (mechanical and enclosure), open item S-63 and ENGINEERING-QUESTIONS EQ-24. **Prototype design: nothing in
this folder has been made, printed, bought or fitted.** Added to the case release of 27 September 2026 as a new versioned set beside the
tray it replaces; every file of the release as first built keeps its bytes, and `../README.md` and `../MANIFEST.sha256` mark the r1 tray
superseded. The editable sources govern: `v2/cad/lid_tray_qmx_r2.py` (the parts), `v2/cad/lid_tray_qmx_r2_check.py` (the record in
`lid-tray-qmx-r2-check.out`), `v2/cad/lid_tray_qmx_r2_drawing.py` (sheets 14r2-1 and 14r2-2).

## Why r1 is replaced

The r1 tray of 9 September 2026 (`../lid-tray-qmx/`, sheet 14) had its two cable notches in one end wall, while the QMX has jacks on
both end panels: Paddle, Audio and DC on the left, RF (BNC), PTT and USB-C on the right (operating manual 1_04_004 pages 7 and 8). Its
95 x 63 x 25 came from no maker document the tree held, it held the unit by one hook-and-loop strap threaded under a floor that lies on
the lid, it was PETG (heat deflection 68 C at 0.45 MPa, Prusament's sheet) under TEST-PLAN E3-S's +71 C storage, and its fixing named
PEM self-clinching nuts in a 2 mm ABS plate, a pairing that needs a metal host.

## The unit, from the maker (`v2/vendor/qrp-labs/`)

| Fact | Value | Source |
|---|---|---|
| Enclosure | 95 x 63 x 25 mm without protrusions | `qmx-product-page-2026-09-27.txt` (qrp-labs.com/qmx.html, updated 24 Sep 2026); assembly manual 1.04r page 2 |
| Mass | 220 g with the enclosure | the product page |
| Panels, fixings, feet, knobs | left and right end panels, eight M2.5 panel screws, four self-adhesive rubber feet (fitting optional), two knobs listed "15mm" | assembly manual 1.04r pages 20, 21 and 77 (`qmx-assembly-1_04r-pages-1-3-20-21-75-78.pdf`) |
| Jacks | left: Paddle, Audio (3.5 mm stereo), DC (2.1 mm barrel, centre positive); right: RF (BNC), PTT (3.5 mm), USB-C | operating manual 1_04_004 pages 7 and 8 |
| Controls | VOL and TUNE encoders with push, two buttons, the LCD window; the VOL knob is pressed to switch the radio on and off | operating manual 1_04_004 page 13 (section 4) |

Where each jack, knob, button and the LCD window sits is **scaled** from the maker's undimensioned figures, which come out at the maker's
63 x 25 within 0.4 percent, and cross-checked for the right panel on the maker's photograph (`measure_qmx_figures.py`,
`qmx-figures.out`). The RF jack reads 12.1 mm from the knob edge on the figure and 8.3 on the photograph; every jack is taken over the
range of both, widened by 0.5. The knob's height above the top face is not stated by the maker: 11.6 is scaled from the assembly
manual's photograph 15 of the sibling QCX-mini in the same enclosure family (INFERRED).

## What the tray does (the session's choices under the owner's standing rule of 26 September 2026)

Each choice is the session's, never the owner's; its reason and what reverses it:

1. **Both end panels open over their whole height above a 1.5 mm sill.** Every jack takes its plug from any side, and no uncertainty in
   the scaled jack places can put a jack behind a wall. Reverse by a maker's dimensioned panel drawing that shows an end wall can stand
   somewhere without meeting a jack's plug.
2. **The unit lies top face out, knob edge west, its right panel toward the hinge.** The LCD, both knobs (the VOL knob switches the
   radio) and both buttons face the operator with the lid open; the RF and USB leads leave toward the lid harness at the hinge, the DC
   lead loops back. Reverse by a lead route that needs the other end at the hinge.
3. **Retention by structure, not a strap:** two ledges over the long edges (4.0 over the back edge, full length; 3.0 over the knob edge
   in three segments clear of both knobs with 6 mm of finger room, the wall lowered to the unit's top face beside the knobs), a lintel
   across each open end at ledge level, gussets on both walls, an integral end block at the hinge end and a screwed keeper at the front
   end, and two Rogers PORON 4701-30 pads pressing the unit up against the ledges (the pads' own sheet, `v2/vendor/seals/`). The unit
   slides in from the front end with the lid open. Reverse by E1 or E2 showing a lighter retention holds.
4. **Printed in Prusament PC Blend** (heat deflection 113 C at 0.45 MPa, `v2/vendor/materials/`), not PETG (68 C), because TEST-PLAN
   E3-S stores the kit at +71 C. Reverse by a material with a maker's heat deflection above the stored +71 C and a stated interlayer
   strength at least as high.
5. **Fixed through a 2.0 mm 5052-H32 aluminium lid plate tapped M3 through, bonded to the lid's unribbed inner face with 3M DP8005**
   (`v2/vendor/adhesives/`): no hole in the case (the ruling of 7 September 2026); ten flush countersunk M3 x 5, each tip 0.6 short of
   the plate's back face. Reverse by a bonded fixing whose strength on the case's polypropylene a maker states.
6. **The place:** the east edge stays at X 171.0 (C5; M19 unchanged, 2.08 nominal, 1.70 at the worst); the tray grows west to X 83.4
   for its gussets, where the lid's ceiling is free (the tablet bracket keeps the west third); Y 10.0 as r1. Reverse by a lid item that
   needs X 83.4 to 102.0.

## Files

| File | What |
|---|---|
| `lid-tray-qmx-r2.step`, `.stl` | the tray, 111.6 x 87.6 x 29.1 over its base, 40184 mm3, 49.0 g in PC Blend |
| `lid-tray-qmx-r2-keeper.step`, `.stl` | the front-end keeper, 8.0 x 71.6 x 2.0, 1.3 g |
| `lid-plate-qmx-r2.step`, `.dxf` | the lid plate, 111.6 x 87.6 x 2.0, R6, ten M3 tapped through (layers OUTLINE, TAPPED_M3_THROUGH, NOTE), 52.0 g |
| `lid-tray-qmx-r2-drawing.pdf` | sheet 14r2-1 (the place on the lid, the section with the lid closed, both end panels and their plugs) and sheet 14r2-2 (the three parts dimensioned, the ten holes, print, fitting, retention) |
| `lid-tray-qmx-r2-check.out` | the record: each jack's admitted plug body and the leads' room, the face room rows, the pads, the retention links and the drop bound, and the boolean checks on the solids |

Both sheets were rendered to images at 110 dpi and read back before this folder was written (an AI read-back of legibility and of the
figures against the sources).

## What the record shows (`lid-tray-qmx-r2-check.out`)

- **Every jack is reachable with its plug.** The tray admits, at the worst of each jack's scaled place: DC d 18.8, Audio and Paddle d 12.0,
  RF d 16.0, PTT d 10.8, USB-C 8.6 high. Built on the solids, the unit, every admitted plug body at the four corners of its jack's place
  and each knob with its finger room intersect neither printed part; two controls that must intersect (the unit 1.0 higher, the RF plug
  1.0 fatter) do. The admitted bodies are the requirement on the harness picks and on the operator's 3.5 mm plugs.
- **Bend radii.** The right panel is 58.43 from the lid's flat ceiling edge: the RG-316 jumper turns at R 12.5 (the tree's figure) with
  its plug up to 42.9 long, the USB-C lead at R 20 with its plug up to 35.4. The left panel is 78.43 from it: the DC lead loops back
  at R 20 west of the tray with its plug up to 55.4. R 20 is the requirement on the DC and USB lead picks (not picked).
- **Face room with the lid closed** (from frame_seat.out's M3 room: 47.92 nominal, 44.39 worst, 42.11 with unstated allowances twice):
  under the walls and ledges 16.62 / 13.09 / 10.81, MET; over the buttons under the unit's top face 18.62 / 15.09 / 12.81 less the
  cap heights, OPEN on them (MET for caps up to 11.81); the knob tips 7.02 / 3.49 / 1.21 with the INFERRED 11.6 knob, MET, and
  OPEN on the knob's unstated height (MET for a knob up to 11.81).
- **Pads:** PORON 4701-30 3.18 compressed 34 percent nominal, 13 to 51 percent over the tolerance corners: the unit always stands on them.
- **Retention.** On the makers' typical figures the known links hold to 703 g (a wall pushed sideways, bending across the layers at its
  root); the ledges 756 g and more, the walls out of the pocket 2237 g, the keeper 854 g. TEST-PLAN E1's peak on the lid is not stated
  by MIL-STD-810H: a half-sine from 1.22 m gives 958 g at 2 mm of stopping distance and 96 g at 20 mm, so the bound includes failure.
  The lid plate's bond on the case's polypropylene is bounded by no held figure (DP8005's sheet gives a T-peel on HDPE only).

## What stays open (carried, not closed by this folder)

- **The lid harness's crossing of the sealed face plate is not designed anywhere in the tree**: the DC, USB and RF leads leave the tray
  for the hinge side and must reach B16 `J_QMX` and A22 `J_HF` and `J_RF2` under a face plate that covers the frame window and Peli's
  o-ring. A new open item (drafted with this set).
- **Retention verification:** the bond (CASE-MARGINS T8, a pull test of the bonded plate on the case's polypropylene) and the peak
  (TEST-PLAN E1 with an accelerometer on the lid; E2 for the pads' preload). No board, interface or purchase depends on it: the
  remedy is a made part (the same STEP machined in 6061, or a larger bonded plate).
- **The knob height** (T9, chalk on the knob tips with the lid closed) and **the button cap heights** (M3, T9).
- **The harness picks** against the admitted plug bodies and R 20.

## Source revision

Generated from tree `c23c5e76` (main on 27 September 2026) plus the r2 changes of worktree `fnd/w5tray`, on 27 September 2026
(17:31:15 to 17:31:30 UTC), on the rented CAD box (Ubuntu 24.04.5 LTS, Python 3.12.3, x86_64), in a fresh venv whose `pip freeze`
equals `v2/cad/requirements-cad.lock` line for line (build123d 0.13.0, cadquery-ocp-novtk 8.0.1.0.0, ezdxf 1.4.4, matplotlib 3.11.2,
numpy 2.5.3, Pillow 12.2.0); `measure_qmx_figures.py` gives the same `qmx-figures.out` byte for byte in that venv. Inputs, sha256 first 16:

| File | sha256 (16) |
|---|---|
| `v2/cad/lid_tray_qmx_r2.py` | `3e89a3ca4d3d1d3b` |
| `v2/cad/lid_tray_qmx_r2_check.py` | `78c625d64341bd6b` |
| `v2/cad/lid_tray_qmx_r2_drawing.py` | `21287961b3f5dd2a` |
| `v2/cad/drawing_kit.py` | `49e7f00d7d57893f` |
| `v2/ecad/tools/panel1450.py` | `3bdb88df98260244` |
| `v2/vendor/peli/1450/frame_seat.out` | `a65c0792a7a08c08` |
| `v2/vendor/qrp-labs/qmx-figures.out` | `ec891c826be2d19b` |
| `v2/vendor/qrp-labs/qmx-operating-manual-1_04_004.pdf` | `7d2616cdcadd2f7c` |
| `v2/vendor/qrp-labs/qmx-assembly-1_04r-pages-1-3-20-21-75-78.pdf` | `4ef0119f832677b2` |
| `v2/vendor/qrp-labs/qmx-product-page-2026-09-27.txt` | `ea72e0782d8ef822` |
| `v2/vendor/materials/prusament-pc-blend-tds-v1.1-2022-02-16.pdf` | `25f7aa7b99cc24e5` |
| `v2/vendor/seals/rogers-poron-4701-30-very-soft.pdf` | `9567c83b0d8d9e97` |
| `v2/vendor/adhesives/3m-scotch-weld-dp8005.pdf` | `90fdb06a6289827e` |
| `v2/cad/requirements-cad.lock` | `32f887be3a68bb56` |

Regenerate: `PY=.venv-cad/bin/python v2/cad/build_lid_tray_r2.sh <out dir>` (v2/cad/README.md). A rebuild on the same box two
minutes later gave both STL files and the check record byte for byte; the three STEP files differ only in their FILE_NAME time stamp,
the DXF only in its dates, and the PDF in two bytes of its creation date.

## Review

AI review only: the choices and checks here were made by an agent session. No qualified mechanical engineer has reviewed the tray; the
case release's review route (`../margins/CASE-FIT-UNCERTAINTIES.md` section 5) covers it.
