# v2/cad: the case set's editable sources and how to regenerate them

MESHSAT-1357, 27 September 2026. Prototype design: nothing in this folder has been made, bought or fitted. The released copies are
`v2/release/case-2026-09-27/`; the files here are the authority, the release folder is an immutable copy of what they produced.

## What is here, and what is current

| File | What it is | Current? |
|---|---|---|
| `../ecad/tools/panel1450.py` | **The single geometry source** of the case set: Peli's figures the arrangement derives from, the face plate (C1), the setting legs (C6), the stack, the connector plate and its six items (C3), the RF entry plates and the twelve arrestor sites (C2, C4), the QMX tray's place (C5), the pack block's place. Plain Python; board C's gate, the face budget and every file below read it. | current |
| `zstack.py` | Reads the committed KiCad boards (the file each board's routeflow profile names, and board E5) with the standard library: outlines, holes, thickness, and every footprint's side, plan rectangle and height (its own library model's, from `zstack-models.json`, or a declared class). A library model is a nominal body, so where a worst-case chain takes a part's height the maker's maximum is read off its sheet and carried beside it (`MAKER_MAX`: U51, STM32H753VITx in LQFP-100, 1.60 by ST's DS12117 Rev 9 Table 217, whose typical 1.50 is the model's). Writes `zstack.json`; prints the Z stack and the bays. | current |
| `zstack.json` | The board reading: each board file with its sha256, its parts with heights and their sources (and `height_max` where `MAKER_MAX` gives one), the bays, and `b16_envelopes`, which `panel1450.B16_TALL` loads for the face gates on first use. **Required, never replaced:** without it `panel1450.B16_TALL` raises `ZstackMissing`, so board C's gate reads INCONCLUSIVE instead of passing on a weaker list; a tree a gate runs in must carry it (`drafts/hc7/stage_chain.sh.patch` stages it into chain trees). | current (regenerate when a board changes: the test says so) |
| `zstack-models.json` | The KiCad 9 library models the boards name (kicad-packages3D tag 9.0.9): sha256 and bounding box of each, SUBSTITUTE where the named file is missing from the library, the error where neither exists. | current |
| `model_bbox.py` | Writes `zstack-models.json` (needs the network and the CAD set below). | current |
| `face_plate.py`, `plate_drawing.py` | The face plate (C1): STEP, STL, DXF (layers OUTLINE, THROUGH, POCKET_1MM, REBATE_2MM_TOP, RELIEF_0.8MM_UNDERSIDE, STANDOFF_M3), marking SVG; its dimensioned drawing (sheet 1). | current |
| `frame_leg.py` | The four setting legs (C6), their printed locator and the centring wedges: STEP, STL, the leg's DXF profile. | current |
| `connector_plate.py` | The back wall's connector plate (C3) and its gasket: STEP, STL, DXF (seen from outside). | current |
| `rf_entry_plate.py` | The two end walls' RF entry plates (C4) and their gaskets: STEP, STL, DXF per wall (seen from outside). | current |
| `case_drawings.py`, `drawing_kit.py` | Sheets 2 to 14: frame and legs, connector plate, RF entry plates, the Z stack, the case in plan, the seven board envelopes, and the QMX lid tray with its place on the lid (sheet 14, added 27 September 2026 by the layer 7 fixer c7). Every sheet names its inputs by sha256 and labels the margin rows its features enter (MET or OPEN, read from `../vendor/peli/1450/frame_seat.out`). | current |
| `../ecad/tools/case_wall_cutouts.py` | The 1:1 marking templates (back wall, east wall, west wall) and check prints (connector plate, both entry plates, the face plate on A3). | current |
| `case_geometry_check.py` | The drift checks `../ecad/tools/tests/test_case_geometry.py` runs: board identity, the face gates' coverage of board B, the face basis against `frame_seat.out`, `frame_seat.py` against its record, the makers' maxima on board parts, the worst-case reads of `frame_seat.py` (a worst-case chain takes `height_max`, never a model's nominal height), a release folder against its manifest. | current |
| `build_case_release.sh` | Regenerates the whole case set into a folder, copies the margins it is labelled with and writes its manifest. | current |
| `case_manifest.py` | Writes a release folder's `MANIFEST.sha256` (stdlib); run it again after the folder's README.md is written. | current |
| `lid_bracket_qmx.py` | **Superseded by the r2 tray below.** The QMX lid tray (C5) of r1: STEP and STL of the part of 9 September 2026, unchanged; its numbers are module constants and its place across the case (`PLACE_Y`, Y -51.5 to 71.5) sits beside them, so sheet 14 reads the part and `panel1450.QMX_TRAY_X` (X 102.0 to 171.0) instead of retyping them. Importing it builds nothing. **Its fit to the unit is OPEN** (the QMX's jacks are on both end panels and the tray is notched at one end only; `v2/docs/CASE-FIT-UNCERTAINTIES.md` section 3). | superseded (27 Sep 2026) by `lid_tray_qmx_r2.py`; kept because the released r1 files and sheet 14 were made from it |
| `lid_tray_qmx_r2.py` | The QMX lid tray r2 (S-63, EQ-24; 27 Sep 2026): the tray, its keeper and its aluminium lid plate from the maker's dimensions (`../vendor/qrp-labs/`), open at both end panels, the unit top face out with its right panel toward the hinge; STEP, STL, the plate's DXF. Its jack, knob and LCD places are the scaled figures of `../vendor/qrp-labs/qmx-figures.out` (`measure_qmx_figures.py`); its east edge stays at `panel1450.QMX_TRAY_X[1]` (C5, M19 unchanged) and its place (`PLACE_X`, `PLACE_Y`, `SPAN_X`, `SPAN_Y`) sits beside the part. Importing it builds nothing. | current |
| `lid_tray_qmx_r2_check.py`, `lid_tray_qmx_r2_drawing.py`, `build_lid_tray_r2.sh` | The r2 record (each jack's admitted plug body and the leads' room, the face room against `frame_seat.out`'s M3 room, the pads, the retention links and the drop bound; with `--solids`, boolean checks of the unit, the plug bodies and the knobs against the built parts, with two controls that must intersect), sheets 14r2-1 and 14r2-2, and the script that builds all of it into `lid-tray-qmx-r2/` of a release. `../ecad/tools/tests/test_lid_tray_qmx_r2.py` checks the numbers without the CAD set. | current |
| `pack_4s.py` | The rigid 4S pack box of 7 September 2026. **Superseded**: it fits no pocket (adjudication A06, W4-F3); the ruled pack is a shrink-wrapped 4S3P block (D-06) whose hold-down is not designed (S-27, CON-006). Kept for the record only. | superseded |
| `battery_module.py` | The retired twelve-cell module. | superseded |
| `float_clamp.py` | The dock's float nest for the SMP-MAX plugs: its 16 mm nests overlap at the 14 mm site pitch; one clamp bar (R4E-07) is owed. | not current |
| `render/` | The concept render scene of 5 to 9 September 2026 (Blender 4.2 on a GPU host). It draws the superseded face (rim 109.4, plate under the ring), the Amphenol couplers at Z 88 and the old connector plate; its images are illustrations of that state, not of this set. Not regenerated here. | superseded for measurement |
| `stack-heightmap.json` | The height map of 5 September 2026 (from the render scene). Superseded by `zstack.json`. | superseded |

## Regenerate

Host: any Linux x86_64 (the release was made on Ubuntu 24.04.5 LTS with Python 3.12.3). No KiCad, no Blender, no GPU and no particular
host is needed; only `model_bbox.py` needs the network.

```
python3 -m venv .venv-cad
.venv-cad/bin/pip install -r v2/cad/requirements-cad.lock      # the exact set; requirements-cad.txt names the six top-level pins
v2/cad/build_case_release.sh /tmp/case-out                      # PY=.venv-cad/bin/python by default
REFETCH_MODELS=1 v2/cad/build_case_release.sh /tmp/case-out     # also re-fetch the KiCad library models (network)
```

The standard-library parts run on any Python 3.8 or later without the venv:

```
python3 v2/cad/zstack.py --report                 # the Z stack and the bays, from the committed boards
python3 v2/ecad/tools/z_budget.py                 # the face budget (M1), from panel1450.py
python3 v2/vendor/peli/frame_seat.py              # every case margin (70 rows) and its verdict
python3 v2/cad/case_geometry_check.py             # the drift checks
python3 v2/ecad/tools/tests/run.py case_geometry  # the same, with the defective fixtures
python3 v2/cad/lid_tray_qmx_r2_check.py           # the QMX lid tray r2's record (add --solids in the venv for the checks on the solids)
python3 v2/ecad/tools/tests/run.py lid_tray_qmx_r2
```

The QMX lid tray r2 alone, into `<out>/lid-tray-qmx-r2/` (with the venv): `PY=.venv-cad/bin/python v2/cad/build_lid_tray_r2.sh <out>`;
read the two page images it leaves in `<out>/.lid-tray-qmx-r2-readback/` before a release takes the folder.

STEP and PDF files carry time stamps: two builds of the same sources differ in those bytes. Compare geometry (the printed sizes and
volumes, the DXF entities) and the drawings, not the file hashes; the release's `MANIFEST.sha256` identifies the files as released.

## How a change flows

1. Change a number in `panel1450.py` (or a board file, then run `zstack.py --json v2/cad/zstack.json`).
2. Run `frame_seat.py`; if a figure or verdict moves, update `v2/docs/CASE-MARGINS.md` and commit the new `frame_seat.out` with it.
   `frame_seat.py` reads its design numbers from `panel1450.py` and its board inputs from `zstack.json` from the change that follows this
   release (the frame_seat.py draft of MESHSAT-1357, 27 September 2026); until that lands it types them, and `case_geometry_check.py`'s
   `literal_inputs` and `worst_case_reads` name the two typed inputs (U51's height, typed as 1.6 from the LQFP class, which is ST's
   maximum 1.60 the draft reads from `zstack.json`; and a six-part hand list of B16's tall parts, which misses the E72 module U14).
3. Run the drift checks, then `build_case_release.sh` into a NEW release folder `v2/release/case-<date>/`, write its README.md (source
   revision, inputs by sha256, what it supersedes, what is open), run `python3 v2/cad/case_manifest.py v2/release/case-<date>/` last, and
   mark the previous folder superseded in its README. A release folder is never edited in place.
