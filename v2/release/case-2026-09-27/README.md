# Case set 2026-09-27: the Peli 1450 arrangement C1 to C6, CAD, drawings and 1:1 templates

MESHSAT-1357, pre-PCB layer 7 (mechanical and enclosure). **Prototype design: nothing in this folder has been made, bought, cut, fitted or
powered.** This folder is an immutable copy of what the editable sources produced on 27 September 2026; the sources govern, and a change
makes a new folder, never an edit here (`MANIFEST.sha256` names every file's sha256; `v2/ecad/tools/tests/test_case_geometry.py` checks it).
It was built three times on 27 September 2026 before it was committed: the second build follows the second review of the case release (AI
review), which changed no geometry but made the board reading required (`panel1450.ZstackMissing`), carried U51's maximum body height from
ST's sheet onto the board reading, and allocated the mock-up before the layout entry of the boards it can move. The third (the layer 7 fixer
c7, 11:27 CEST) adds the one made part the set had not drawn, the QMX lid tray: its STEP and STL (`lid-tray-qmx/`) and sheet 14, the part
and its place on the lid; every other file carries the same geometry as the second build (the STL bytes are identical, STEP differs only in
its FILE_NAME time stamp, DXF only in its dates, GUIDs and object-table order, and every drawing sheet is pixel-identical outside its title
block, where the source line and "Sheet n of 14" changed).

## What it is

The kit's physical integration in the Peli 1450 of the current moulding (drawing 1451-931 of 15 January 2025, D-08a) with the 1450PF frame,
as the session chose it on 26 September 2026 under the owner's standing rule (SC-07; `v2/docs/CASE-MARGINS.md` section 4):

- **C1** the 3 mm face plate lies on the frame and covers Peli's o-ring, ten 6-32 UNC x 1/2 in from above into Peli's brass inserts;
  377.2 x 263.0 R16, the band outside 368.0 x 253.0 rebated 2.0 from the top, a 0.8 relief in the underside over the frame's lettering.
- **C6** four 6061-T6 setting legs bonded under the frame's ring give the frame a floor-referenced height: pad top 94.13, frame bottom 86.00,
  face top 106.52 (104.77 to 108.27 at the stated allowances).
- **C2** the ruled PolyPhaser GTH-SFF-AL arrestors are the twelve antenna bulkheads, axis Z 59, a 31 pitch, five on the east wall and seven
  on the west.
- **C3** one 114.0 x 68.3 x 5.0 connector plate between the back wall's hinge fairings carries the six ruled items.
- **C4** one 6.0 RF entry plate per end wall carries its arrestors, each nut on a 26.0 x 1.5 spot-face in the plate's back.
- **C5** the QMX lid tray at X 102.0 to 171.0 (Y -51.5 to 71.5 over its tabs), four M3 into nuts bonded to the lid (sheet 14).

## Contents

| Folder | Files | Made by |
|---|---|---|
| `face-plate/` | `face-plate.step`, `.stl`, `.dxf` (layers OUTLINE, THROUGH, POCKET_1MM, REBATE_2MM_TOP, RELIEF_0.8MM_UNDERSIDE, STANDOFF_M3), `face-plate-marking.svg` | `v2/cad/face_plate.py` |
| `frame-legs/` | `frame-leg.step`, `.stl`, `.dxf` (the profile, 4 off), `frame-legs-4.step` (all four in place), `leg-locator.step`/`.stl`, `wedge.step`/`.stl` (printed) | `v2/cad/frame_leg.py` |
| `connector-plate/` | `connector-plate.step`, `.stl`, `.dxf` (seen from outside), `connector-plate-gasket.dxf` | `v2/cad/connector_plate.py` |
| `rf-entry-plates/` | `rf-entry-plate-east.step`/`.stl`/`.dxf`, `rf-entry-plate-west.*`, `rf-entry-gasket-east.dxf`, `rf-entry-gasket-west.dxf` | `v2/cad/rf_entry_plate.py` |
| `lid-tray-qmx/` | `lid-bracket-qmx.step`, `.stl` (the printed QMX lid tray of 9 September 2026, unchanged: 123.0 x 69.0 x 28.0 over its tabs, 24864 mm3, the same solid as `v2/release/revA/case/lid-bracket-qmx/`: 3260 facets, the same bounding box and volume) | `v2/cad/lid_bracket_qmx.py` |
| `drawings/` | sheet 1 `face-plate-drawing.pdf`; sheets 2 to 6 `frame-and-legs-drawing.pdf`, `connector-plate-drawing.pdf`, `rf-entry-plates-drawing.pdf`, `z-stack-drawing.pdf`, `case-plan-drawing.pdf`; sheets 7 to 13 `board-envelope-{a,b,c,d,e,e5,p}.pdf` (outline, both sides' parts by height, and a table of every hole of 2.0 or more with its centre in the case frame); sheet 14 `lid-tray-qmx-drawing.pdf` (the QMX lid tray: its place on the lid in plan, X 102.0 to 171.0 and Y -51.5 to 71.5 with the four M3 hole centres, a section with M3 and M19, the part's plan and elevations); `case-drawings-2-to-14.pdf` (sheets 2 to 14 in one file) | `v2/cad/plate_drawing.py`, `v2/cad/case_drawings.py` |
| `templates/` | `case-templates-1to1.pdf` (A4: back wall, east wall, west wall marking templates; connector plate and both entry plates as check prints), `face-plate-1to1-A3.pdf` | `v2/ecad/tools/case_wall_cutouts.py` |
| `zstack/` | `zstack.json` (the committed boards read: outlines, holes, parts with their heights and sources, the bays), `zstack-models.json` (the KiCad 9.0.9 library models' boxes), `zstack-report.txt`, `z-budget.txt` | `v2/cad/zstack.py`, `v2/cad/model_bbox.py`, `v2/ecad/tools/z_budget.py` |
| `margins/` | `frame_seat.out` (the 70 case margins and their verdicts the drawings label), `CASE-FIT-UNCERTAINTIES.md` (a snapshot of `v2/docs/CASE-FIT-UNCERTAINTIES.md`: every OPEN row, the check it is allocated to and the board decision that waits on it) | copies, by `build_case_release.sh` |
| `MANIFEST.sha256` | the sha256 of every other file here (`sha256sum -c MANIFEST.sha256`) | `v2/cad/case_manifest.py`, written last |

Every drawing sheet states its tolerances, names its inputs by sha256 and labels the margin rows its features enter: MET in green, OPEN in red,
the two that fail with the geometry as assumed (M17g, M17x) as OPEN, FAILS AS ASSUMED. All 70 rows of `frame_seat.out` appear on at least one
sheet. Every sheet and template page was rendered to an image and read back before this folder was written (an AI read-back of legibility and
of the figures against `panel1450.py` and `frame_seat.out`); the 1:1 templates measure 1:1 on their 100 mm bars and plate outlines at 254 dpi.
In the third build sheet 14 was rendered and read back the same way (AI read-back), and sheets 1 to 13, the combined file and the template
pages were compared by pixel with the second build's at 50 dpi: identical outside the title block (the templates identical everywhere, so
their 1:1 scale is the one measured before).

## Source revision

Generated from tree `a8652172` (main on 27 September 2026, the H1 handover) plus the layer 7 changes (branch `fnd/hc7`, MESHSAT-1357: the
closer's and the fixer c7's), on 27 September 2026 (the build of 11:26:47 to 11:27:36 CEST, `CASE_BASE_COMMIT=a8652172`), on the rented CAD
box (Ubuntu 24.04, Python 3.12.3, x86_64), in a fresh venv whose `pip freeze` equals `v2/cad/requirements-cad.lock` line for line (build123d
0.13.0, cadquery-ocp-novtk 8.0.1.0.0, ezdxf 1.4.4, matplotlib 3.11.2, numpy 2.5.3, reportlab 5.0.1). The branch started at `e3aedb25`; every
case input outside the branch (the seven board files, `frame_seat.out`, `CASE-MARGINS.md`, Peli's files, the QMX manual) is byte-identical at
`e3aedb25`, `84e52461` and `a8652172`. The inputs, sha256 first 16:

| File | sha256 (16) |
|---|---|
| `v2/ecad/tools/panel1450.py` (the single geometry source) | `3bdb88df98260244` |
| `v2/cad/zstack.json` (the board reading) | `b4fb79d90d2f3ee1` |
| `v2/cad/zstack-models.json` | `3fad2fb95f584782` |
| `v2/vendor/peli/1450/frame_seat.out` (the margins) | `214e915b985518cb` |
| `v2/docs/CASE-MARGINS.md` (the tolerance analysis) | `275a3083db30a7bf` |
| `v2/docs/CASE-FIT-UNCERTAINTIES.md` (the allocation; copied into `margins/`) | `efc66afe9140e022` |
| `v2/cad/lid_bracket_qmx.py` (the QMX lid tray and its place along Y) | `67ee747c97d3cf67` |
| `v2/vendor/qrp-labs/qmx-operating-manual-1_04_004.pdf` (the unit's panels, sheet 14 note 4) | `7d2616cdcadd2f7c` |
| `v2/cad/requirements-cad.lock` | `32f887be3a68bb56` |
| `v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb` (A32) | `58e26c67987b1daa` |
| `v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_pcb` (B21) | `2e64b5bf2d9cd3bc` |
| `v2/ecad/pcb-c-display-c8/pcb-c-display.kicad_pcb` (C24) | `2a273803757c68fb` |
| `v2/ecad/pcb-d-aprs-d9/pcb-d-aprs.kicad_pcb` (D12) | `929bf82d2bf6eed4` |
| `v2/ecad/pcb-e1-dock-e7/pcb-e1-dock.kicad_pcb` (E17) | `a462ac2620b9b8d3` |
| `v2/ecad/pcb-e5-block/pcb-e5-block.kicad_pcb` (E5) | `686b29a734c55b9a` |
| `v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_pcb` (P4) | `d79865e7b1aceb95` |

The full board hashes are in `zstack/zstack.json`. The KiCad library models came from https://gitlab.com/kicad/libraries/kicad-packages3D at
tag 9.0.9; ten model files the footprints name are missing there and the same body's model stands in (SUBSTITUTE), nine take a declared class
or a maker's figure (`zstack-models.json`, `v2/cad/zstack.py` HEIGHT_CLASSES), and U51 carries ST's maximum body height beside its model's
(`MAKER_MAX`). Nothing else outside the repository was read; no host of this project is needed to regenerate (`v2/cad/README.md`).

**The board reading is required.** `panel1450.B16_TALL` is loaded from `v2/cad/zstack.json`; without it `panel1450` raises `ZstackMissing`
and board C's gate reads INCONCLUSIVE rather than passing on a weaker list. A tree a gate runs in carries the file.

Board C's gate was re-taken on this geometry with the reading recorded by sha (`check_pcb_c.py` with the layer 7 closer's patch, on the
committed C24 file, MEC-001): PASS of 48, the same as on the geometry of `e3aedb25`, with the monitor body now 6.3 mm over the CM5 heatsinks
against the rule's 2.0 (2.2 before); the same run without `zstack.json` reads INCONCLUSIVE. A scratch reading on the CAD box, not recorded
evidence (`v2/docs/CASE-FIT-UNCERTAINTIES.md` section 4).

The margins here are `frame_seat.out` of a6f87e9d, in which `frame_seat.py` still types two board inputs: U51's height as 1.6 from the LQFP
class, which is ST's maximum 1.60 (DS12117 Rev 9, Table 217), and a six-part hand list of board B's east-end parts. Its draft of the same day
reads every design number from `panel1450.py`, U51 at its maker's maximum and the east-end parts from `zstack.json`; when it lands,
`frame_seat.out` changes only in M18's printed part list (the E72 module U14 at 7.76 joins it; the RockBLOCK still governs at 7.63), and no
figure or verdict moves. A case release after that carries its record; this folder is not edited.

## What this supersedes

`v2/release/revA/case/` (face plate 365.5 x 249.5 under the frame's ring on M3 from below with a PORON ring, the face top on a "base 109.4, lip
8" datum no Peli file supports, a 54 x 82 x 3 connector plate between ribs Peli's files do not have, eleven Amphenol 132170 couplers at Z 88,
the rigid pack box that fits no pocket). That folder is kept as history and marked so.

## What is still open (read `margins/CASE-FIT-UNCERTAINTIES.md`)

- 35 of the 70 margins are OPEN; two of them (M17g, M17x) fail with the jumper plug laid out at the limit of its class until the plug is
  picked, and that pick is a prerequisite of board B's layout entry. MET rows are sensitivity readings, not bounds on the case's unpublished
  tolerance. None of this CAD establishes a fit, a seal or an alignment: checks T1 to T11 on a new case of the current moulding do
  (CASE-MARGINS.md sections 5 and 7).
- Eleven OPEN rows would, if their check failed, move a board outline, a connector or a board part of boards A, B, E or P, so their checks
  (T1, T2, T4, T5, T10, T11 on the mock-up) are required before those boards enter layout. Buying the case and the mock-up's parts is the
  owner's decision (D-09): until he makes it, the layout entry of A, B, E and P is BLOCKED on it. `margins/CASE-FIT-UNCERTAINTIES.md`
  section 2 names the rows per board and section 7 is the compact engineering question. Boards C, D and E5 are not held by it.
- Not designed yet: the pack's hold-down (S-27, CON-006), the rod stack's retention (W4-F7), the dock and blind-mate tolerance stack, the
  fans and the floor plan, board E's clamp bar (R4E-07). `v2/cad/pack_4s.py` is superseded and is not in this folder.
- Picks the connector plate's cut-outs wait on: the sealed RJ45 (the PX0833 fails the envelope and 54 V), the PXP4043/C panel drawing, the
  M8 receptacle, the pod, the stud. Their cut-outs are PROVISIONAL (red on sheet 3).
- The thermal interfaces rest on an enclosure conductance whose desk bounds include failure; the empty-case heat-balance test settles it.
- The QMX lid tray is drawn as generated, and **its fit to the unit is OPEN**: the held QMX operating manual (1_04_004, pages 7 to 9) puts
  the Paddle, Audio and DC jacks on the unit's left panel and RF, PTT and USB-C on its right, while the tray is notched at one end only, so
  the lid harness's three leads cannot all leave it; the notches' heights and the unit's 95 x 63 x 25 are not checked against a maker's
  drawing. A made-part item that moves no board: the tray is revised from the unit's drawing before it is printed
  (`margins/CASE-FIT-UNCERTAINTIES.md` section 3; sheet 14 note 4).
- The face plate carries sixteen LED light-guide holes (D1 to D16) and the light sensor's (seventeen 2.6 H7 holes, sheet 1). The guide
  over the hardware EMCON lamp D22 that board C's round 8 draws beside `SW_EMCON` is placed at board C's next layout and joins the plate
  in a later case release.

## Review

AI review only: the checks behind this set and behind CASE-MARGINS.md's revisions were made by agent sessions. No qualified mechanical or
thermal engineer has reviewed it; the session recommends a mechanical review route before any case part is ordered
(`margins/CASE-FIT-UNCERTAINTIES.md` section 5).
