# H1, the heat-test face plate blank: its own manufacturing definition (beside the case release of 27 September 2026)

MESHSAT-1357, stream od01b, 29 September 2026. **Prototype design: nothing in this folder has been made, bought, cut or
fitted.** H1 serves only the empty-case heat-balance test (`v2/docs/records/od01/TEST-BRIEF.md`, test A, and
`TEST-PROCEDURE.md`). Until today the request for quote ordered it as "the face plate of sheet 1 without its openings",
with prose overriding sheet 1; the owner's instruction of 29 September 2026 (R6) asked for a distinct definition generated
from the same source geometry as C1. This folder is that definition.

**No file of the release is edited for it**, as with `../lid-tray-qmx-r2/`: `../README.md`, `../MANIFEST.sha256` and every
C1 file keep their bytes, and this folder carries its own `MANIFEST.sha256` (below). `v2/docs/records/od01/PACKAGE.md`
lists every file an engineer needs, this folder's included, by path and sha256.

## Files

| File | What it is |
|---|---|
| `h1-heat-test-plate-drawing.pdf` | Sheet H1-1, A3: plan with every dimension, the PEM nut section, material, thickness, finish, flatness, tolerances and notes. **It governs** over the DXF and STEP where they differ. |
| `h1-heat-test-plate.dxf` | The outline and every feature on its own layer, in the case frame (origin at the plate's centre): `OUTLINE`, `THROUGH` (ten 4.6), `REBATE_2MM_TOP`, `RELIEF_0.8MM_UNDERSIDE`, `PEM_S_M3` (four 4.2), `INFO` (one text line, not a feature) |
| `h1-heat-test-plate.step`, `.stl` | The solid, Z up from the underside |
| `h1-heat-test-plate-check.out` | The generator's check: H1's DXF parsed and compared with the released C1 DXF (`../face-plate/face-plate.dxf`): outline, rebate line, relief and the ten screw holes equal within 0.001 mm; each layer holds only its features; the four nuts on 37.0 (X) by 35.0 (Y) about (-45.0, 70.0); the resistor's footprint 2.92 mm inside the 1450PF window, 20.12 mm from the nearest screw hole; the nuts in the full-thickness face. **RESULT PASS: 15 checks, 0 failed.** |

## What H1 is

- **Outline and seal, the same as C1** (read from `v2/ecad/tools/panel1450.py`, the single source of C1): 377.2 x 263.0 x
  3.0, R16; the band outside 368.0 x 253.0 (R16) rebated 2.0 from the top, 1.0 left; the 44.0 x 9.0 x 0.8 relief in the
  underside over the 1450PF frame's lettering; ten 4.6 holes at Peli's insert bores for 6-32 UNC x 1/2 in A2 pan heads.
  It lies on the frame and covers Peli's o-ring as C1 does.
- **The one H1-only feature:** four PEM S-M3 self-clinching nuts in 4.2 holes on the Arcol HS100's fixing pattern, F 35.0
  by G 37.0 (Arcol "HS Aluminium Housed Resistors" sheet 12/14.08, page 2: F and G +-0.3, mounting holes L 4.4 +-0.25,
  mounting foot K 3.7 max; held as `v2/vendor/arcol/arcol-hs-datasheet-12-14-08.pdf`. The "3.2 max." on that page sits at
  the solder tag and is read here as the tag's hole, not the mounting hole, which corrects the independent check's reading
  of 28 September), centred on the PA flange site (X -45.0, Y 70.0,
  `panel1450.PA_MOUNT`), **G 37.0 along the plate's X and F 35.0 along its Y** (the owner's instruction), so the
  resistor's long axis runs along Y. Holes at X -63.50 and -26.50, Y 52.50 and 87.50. The nuts are pressed from the top
  face, flush on the underside, so the resistor's flange sits flat on the plate with compound between.
- **Omitted from C1, on purpose:** both windows and the e-paper pocket, every control, light-guide, sounder, headset and
  camera hole, the monitor frame's four 4.5 holes, the eight PEM SO-M3-10 standoffs, C1's two PA nuts 60 apart, and the
  marking. H1 is a closed skin.
- **Material, finish:** EN AW-5754 or 6061-T6, 3.0 +-0.13; black anodised all over, as C1, because the test measures the
  heat that leaves through the plate and the finish sets its emissivity (session choice of 28 September, `MACHINING-RFQ.md`
  section 5 note 1); the nuts pressed after anodising. Mass about 766 g (the solid's volume at 2.70 g/cm3).

## Choices taken here (`authority: SESSION`, under the owner's standing rule of 26 September 2026)

1. **PEM S-M3-2** (shank code 2). PEM's S-type bulletin is not held (pemnet.com's PDF and its Archive copies answered 404
   on 29 September 2026 at 01:30 CEST), so the code is the session's reading of PEM's S table for a 3.0 sheet (INFERRED),
   the hole stays at C1's 4.2, and the drawing asks the shop to follow PEM's installation data and say so where they differ.
   Reversal: PEM's bulletin, or the shop's statement.
2. **The pattern at C1's +-0.10** on position: an M3 in the HS100's 4.4 +-0.25 mounting holes floats at least 0.5
   (4.15 minimum hole, 3.0 screw), more than Arcol's +-0.3 on the pattern and H1's +-0.10 together, so M3 x 10 A2 pan
   heads with flat washers pass all four holes at every tolerance. Reversal: none needed unless the owner's M3 choice
   changes.
3. **Flatness 0.5** over the plate after anodising and nut insertion, and the measured value reported: a gap under the
   edge would open the o-ring seal the test relies on. Reversal: a shop's stated flatness with a reason.
4. **Its own manifest**, not lines appended to `../MANIFEST.sha256`, because the release README says a change makes a new
   folder and never edits the release, and `../lid-tray-qmx-r2/` set that convention. Reversal: the integrator appends
   this folder's lines to the release manifest (the check `case_geometry_check.manifest()` reads only listed files, so
   either way passes).

## Source revision

Generated on 29 September 2026 at 01:34 CEST (23:34 UTC on 28 September, the date the sheet's title block prints) on the
rented CAD box (Ubuntu 24.04, Python 3.12.3, x86_64) from branch `fnd/od01b` at `b8880536`
(`CASE_BASE_COMMIT=b8880536`; a first build at `c0ec7684` had the HS100's hole misread on the sheet's section and note 2,
with the same geometry: the STL bytes are identical), in a venv whose `pip freeze` equals `v2/cad/requirements-cad.lock` line for line
(build123d 0.13.0, cadquery-ocp-novtk 8.0.1.0.0, ezdxf 1.4.4, matplotlib 3.11.2). Commands, from the repository root:

    python v2/cad/h1_heat_test_plate.py <out>/h1-heat-test-plate
    python v2/cad/h1_heat_test_plate_drawing.py <out>/h1-heat-test-plate/h1-heat-test-plate-drawing.pdf <out>/h1.png
    python v2/cad/case_manifest.py <out>/h1-heat-test-plate --base b8880536     (after this README is written)

Inputs, sha256 first 16: `v2/ecad/tools/panel1450.py` 3bdb88df98260244 (the same file the release names);
`v2/release/case-2026-09-27/face-plate/face-plate.dxf` 19703fa5838f9e4a; `v2/vendor/arcol/arcol-hs-datasheet-12-14-08.pdf`
ec17870c5a92d11e. The sheet was rendered to an image and read back before this folder was written (AI read-back of
legibility and of the figures against the check record).

## Before cutting

H1 fits only a case and frame of the moulding the design assumes. **Do not release H1 for cutting before the receipt checks
R1 to R8 of `v2/docs/records/od01/MACHINING-RFQ.md` section 6 have passed** on the case and frame bought for the test.
Quotes may be asked before that.

## Review

AI read-back and the generator's own check only. No qualified mechanical engineer has reviewed this definition.
