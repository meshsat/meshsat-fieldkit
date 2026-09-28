#!/usr/bin/env python3
"""Stream od01b (MESHSAT-1357, 29 Sep 2026): correct MACHINING-RFQ.md in place. Each replacement asserts its old text is
present exactly once, the result differs, carries no em or en dash, and a second run is refused (the marker line)."""
import sys, os
FN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MACHINING-RFQ.md")
s = open(FN, encoding="utf-8").read(); s0 = s
MARK = "> **Revised 29 September 2026 (stream od01b)**"
if MARK in s: sys.exit("already applied")

R = []
R.append(("""# OD-01: request for quote, the made parts of the heat test and the case mock-up (NOT SENT)

""", """# OD-01: request for quote, the made parts of the heat test and the case mock-up (NOT SENT)

> **Revised 29 September 2026 (stream od01b)** after the owner's instruction of that day and an outside AI review: H1 is
> now ordered to its own definition (sheet H1-1, DXF, STEP in `h1-heat-test-plate/`), not as "C1's CAD plus prose that
> overrides the drawing" (R6); H2's finish is one instruction (R6); the HS100's mounting holes are Arcol's L 4.4 +-0.25,
> not the "3.2 max" the first issue and the check read (that figure is the solder tag's hole); a new section 6 states
> which case the design targets, how the received case is identified and the receipt checks R1 to R8 that must pass
> before any fit-dependent part is released for cutting (R6). Quotes may be asked now; cutting may not.

"""))
R.append(("""| H1 | Heat-test face plate blank: C1's outline and fixings only | 1 | 5754 or 6061 aluminium, 3.0 | black anodised, the same as C1 (see note 1) | CNC or laser plus a rebate pass | heat test | **first** |""",
"""| H1 | Heat-test face plate blank, its own part: sheet H1-1 (`h1-heat-test-plate/`): C1's outline, rebate, relief and ten screw holes, plus four PEM S-M3-2 nuts on the HS100 pattern 37.0 (X) x 35.0 (Y) at the PA flange site; no other feature | 1 | 5754 or 6061-T6 aluminium, 3.0 | black anodised all over, nuts pressed after anodising (note 1) | CNC or laser plus a rebate pass | heat test | **first**; cut only after R1, R2, R3, R5 and R6 of section 6 |"""))
R.append(("""| C6 | Setting legs | 4 (two mirror images: cut the profile, flip it) | 6061-T6, 6.0 | edges broken, no finish | waterjet or laser from the profile | heat test and mock-up (T2) | **first** |""",
"""| C6 | Setting legs | 4 (two mirror images: cut the profile, flip it) | 6061-T6, 6.0 | edges broken, no finish | waterjet or laser from the profile | heat test and mock-up (T2) | **first**; cut only after R1, R3, R4 and R5 |"""))
R.append(("""| C1 | Face plate, complete | 1 | 5754 or 6061, 3.0 | black anodised | CNC | mock-up T2 and T4 | second |
| C4-E, C4-W | RF entry plates, east (5 arrestors) and west (7) | 1 each | 6061 (or 5052) aluminium, 6.0 | edges broken | CNC (spot-faces) | mock-up T11 (one plate, or a coupon), build T6 and T7 | second (east plate only), rest at build |""",
"""| C1 | Face plate, complete | 1 | 5754 or 6061, 3.0 | black anodised | CNC | mock-up T2 and T4 | second; cut only after R1, R2, R3, R5 and R6 |
| C4-E, C4-W | RF entry plates, east (5 arrestors) and west (7) | 1 each | 6061 (or 5052) aluminium, 6.0 | edges broken | CNC (spot-faces) | mock-up T11 (one plate, or a coupon), build T6 and T7 | second (east plate only), rest at build; cut only after R1, R7 and R8 |"""))
R.append(("""| H2 | Dummy stack plate for the heaters: 330 x 200 x 3.0, the stack's outline (board B's in zstack.json), matt black anodised or painted (a bare or smaller plate passes H2's 100 C stop limit at 42 and 64 W: the check's estimate, INFERRED), the three HS50 heaters bolted to it with compound (each 21.2 W exceeds the HS50's 14 W rating without a heatsink) | 1 | aluminium, 3.0 (any alloy) | none | shear or saw | heat test | first, may be the operator's |""",
"""| H2 | Dummy stack plate for the heaters: 330 x 200 x 3.0, the stack's outline (board B's in zstack.json), four 4.5 holes 10 from each corner's two edges for the M4 stand-offs; the heaters' M3 holes are drilled and tapped by the operator, marked from the parts (`TEST-PROCEDURE.md` section 4). A bare or smaller plate passes H2's 100 C stop limit at 42 and 64 W (check-2's estimate, INFERRED); each 21.2 W heater exceeds the HS50's 14 W rating without a heatsink, so they are bolted to it with compound | 1 | aluminium, 3.0 (any alloy) | **both faces painted matt black with a heat-resistant paint rated to 200 C or more** (note 7) | shear or saw | heat test | first, may be the operator's |"""))
R.append(("""| H1, C1 | `face-plate/face-plate.step` (CNC) | `48343402a8370f36eb8a0474de6eb3cdee50e1df127c515781736e2ada8ca696` |
| H1, C1 | `face-plate/face-plate.dxf` (layers OUTLINE, THROUGH, POCKET_1MM, REBATE_2MM_TOP, RELIEF_0.8MM_UNDERSIDE, STANDOFF_M3) | `19703fa5838f9e4acbe0dc4021a77ca34b38e8b3c2fbe840678c53dfc6e3c551` |
| H1, C1 | `drawings/face-plate-drawing.pdf` (sheet 1) | `ef9a2fb1df36deef74b5959633dd15583ea7388d8e48bd0f087f9f086fa4d061` |""",
"""| H1 | `h1-heat-test-plate/h1-heat-test-plate-drawing.pdf` (sheet H1-1; governs) | `0cb0c51bce23f67bbb03bd2840c5c4f9f5916a70c132e1abd5eaaa9a49e29e89` |
| H1 | `h1-heat-test-plate/h1-heat-test-plate.step` (CNC) | `122a1eff47f0d189ca5a311791994569cb6872cbff31043753fd83e6f4932f1b` |
| H1 | `h1-heat-test-plate/h1-heat-test-plate.dxf` (layers OUTLINE, THROUGH, REBATE_2MM_TOP, RELIEF_0.8MM_UNDERSIDE, PEM_S_M3) | `7708c746b13efe94b40c3a83f5ab2f81e00b824230db2a791aa96d4c9ca44a0e` |
| C1 | `face-plate/face-plate.step` (CNC) | `48343402a8370f36eb8a0474de6eb3cdee50e1df127c515781736e2ada8ca696` |
| C1 | `face-plate/face-plate.dxf` (layers OUTLINE, THROUGH, POCKET_1MM, REBATE_2MM_TOP, RELIEF_0.8MM_UNDERSIDE, STANDOFF_M3) | `19703fa5838f9e4acbe0dc4021a77ca34b38e8b3c2fbe840678c53dfc6e3c551` |
| C1 | `drawings/face-plate-drawing.pdf` (sheet 1) | `ef9a2fb1df36deef74b5959633dd15583ea7388d8e48bd0f087f9f086fa4d061` |"""))
R.append(("""> Parts and files as in the attached table (lines H1, C6, C1, C4-E, C4-W, C3, optional G1 to G3, H2, H3, L1). Units are
> millimetres. Each part has a drawing PDF; where a DXF or STEP and the PDF differ, the PDF governs (for H1, this text governs over sheet 1) and we ask you to
> tell us.
>
> - **H1** is the face plate of sheet 1 without its openings: machine only the outline 377.2 x 263.0 x 3.0 with R16
>   corners, the rebated band (outside 368.0 x 253.0, 2.0 deep from the top face, 1.0 left), the 0.8 relief on the
>   underside, the ten 4.6 holes at the insert pattern and FOUR PEM S-M3 self-clinching nuts in 4.2 holes on a 35.0 x 37.0
>   pattern centred on the PA flange site, 37.0 along the plate's X axis and 35.0 along Y (they take the heat test's Arcol HS100 patch resistor: its four fixing holes,
>   3.2 maximum, on 35.0 x 37.0, Arcol HS datasheet 12/14.08, page 2). C1 keeps its two nuts 60 apart for the real flange. Omit both windows and their 1.0 pocket, the seventeen 2.6 H7 holes, the eight PEM SO-M3-10 standoffs and
>   the four 4.5 holes for the monitor frame. Black anodised as C1.""",
"""> Parts and files as in the attached table (lines H1, C6, C1, C4-E, C4-W, C3, optional G1 to G3, H2, H3, L1). Units are
> millimetres. Each part has a drawing PDF; where a DXF or STEP and the PDF differ, the PDF governs and we ask you to
> tell us. Please quote now; **we will confirm the release for cutting part by part** after our checks on the case the
> parts fit (the fit-dependent parts are H1, C6, C1, C4 and C3).
>
> - **H1** is its own part, drawn on sheet H1-1 with its own DXF and STEP: the outline 377.2 x 263.0 x 3.0 with R16
>   corners, the rebated band (outside 368.0 x 253.0, 2.0 deep from the top face, 1.0 left), the 44.0 x 9.0 x 0.8 relief
>   in the underside, ten 4.6 holes, and four PEM S-M3-2 self-clinching nuts in 4.2 holes on 37.0 along X by 35.0 along
>   Y about X -45.0, Y 70.0, pressed from the top face after anodising, flush on the underside. Nothing else. EN AW-5754
>   or 6061-T6, black anodised all over; flatness 0.5 after anodising and insertion, please report it."""))
R.append(("""1. **H1's finish matters to the reading.** The heat test measures how much heat leaves through the plate; a bare
   aluminium plate radiates far less than an anodised one, so a blank in another finish would read a different
   conductance from the prototype's plate. H1 is therefore black anodised like C1 (session choice under the standing
   rule of 26 September 2026; reversal: a measured emissivity of both finishes).""",
"""1. **H1's finish matters to the reading.** The heat test measures how much heat leaves through the plate; a bare
   aluminium plate radiates far less than an anodised one, so a blank in another finish would read a different
   conductance from the prototype's plate. H1 is therefore black anodised like C1 (session choice under the standing
   rule of 26 September 2026; reversal: a measured emissivity of both finishes). The PEM nuts go in after anodising so the
   clinch is not coated over."""))
R.append(("""6. Every made part is the prototype's own if its checks pass (`READY-TO-ACT.md` section 8), except H1, H2 and H3, which
   serve only the heat test.""",
"""6. Every made part is the prototype's own if its checks pass (`READY-TO-ACT.md` section 8), except H1, H2 and H3, which
   serve only the heat test.
7. **H2's finish, one instruction (revised 29 September 2026).** The first issue said "matt black anodised or painted" in
   the part's description and "none" in its finish column. It is now: both faces painted matt black with a
   heat-resistant paint rated to 200 C or more, by the maker or the operator. H2 radiates to the case like the boards it
   stands in for, so what matters is an emissivity near 0.9, which a matt black paint gives (INFERRED; check-2's estimate
   used about 0.9); paint needs no shop and no lead time. (Session choice under the standing rule of 26 September 2026;
   reversal: a shop quoting black anodising together with H1 at no extra lead time, which serves equally.)
8. **The HS100's mounting holes.** Arcol's page 2 (sheet 12/14.08, held in `v2/vendor/arcol/`) dimensions the mounting
   hole as L, 4.4 +-0.25 for the HS100 and 3.2 +-0.25 for the HS50; the "3.2 max." beside the HS75 to HS150 view sits at
   the solder tag. The first issue and check-1 read the HS100's mounting holes as 3.2 max; with 4.4 an M3 floats at
   least 0.5, more than the pattern's +-0.3 and H1's +-0.10 together, so the nuts stay M3 as the owner asked.

## 6. The case the design targets, and the checks on the received case before any cutting

**Which case.** The design targets the current moulding of the Peli 1450, Peli's customer drawing 1451-931 dated 15
January 2025 (`v2/vendor/peli/1450/1451-931-customer-drawing-2025-01-15.pdf`; D-08a), fitted with the 1450PF Special
Application Panel Frame. In the EU Peli sells that case as the **1450EU** (Peli's EU page, made in Germany), and Peli
states the 1450PF is "for 1450EU Protector Case" (its EU and GB pages; `CHECKOUT-LIST.md` section 1, O4 to O7). The list
carries `1450-001-110E` (1450EU, empty, black) and `1450-300-110E` (the 1450PF kit). No Peli page read says in words that
the 1450EU is the moulding of drawing 1451-931; R1 below settles it on the received case, and the seller's 60-day return
covers a case of another moulding (it goes back; it is not adapted).

**Which checks, and what each gates.** Each figure is Peli's (drawing, STEP or the 1450PF sheet 1453-314-000 rev A,
`v2/docs/CASE-MARGINS.md` sections 2.1 to 2.4); the tolerance is Peli's where Peli states one (the frame sheet: +-0.76 on
one-decimal figures) and otherwise the allowance the margins assume (+-0.76, INFERRED, because drawing 1451-931 states
none). **A reading inside the range lets the named parts be released for cutting. A reading outside it is not adapted
around: it goes back to `CASE-MARGINS.md` with the measured number, and the named parts wait.** Quotes may be prepared
before these checks; cutting may not.

| Check | What is read | Value, and the range the design assumes | Gauge | Gates the cutting of |
|---|---|---|---|---|
| R1 | Identity (T1): the carton label (Peli part number `1450-001-110E`, the EAN); "1450" and the country of origin moulded on the base; the date wheel's month and year (photograph); the inner ribs: six on the end walls at Y 0 and +-76.2, five on one long wall at X 0, +-76.2, +-152.4 and four on the other at X +-76.2, +-152.4, tops about Z 84.6; the frame: kit label `1450-300-110E`, "1450 FRONT" moulded on its top face, the kit's 1 frame, 1 o-ring, 10 inserts, 4 screws | a 1450EU of the 2025 moulding (drawing 1451-931), the 1450PF for it | eyes, camera, steel rule (rib positions to +-2) | everything below (H1, C6, C1, C4, C3) |
| R2 | The rim zone's inside length and width at the rim face, mid-length and mid-width, 2 mm below the rim face | 382.58 x 268.28 (STEP #1324, #1689), range 381.82 to 383.34 and 267.52 to 269.04 | 500 mm caliper with inside jaws, or a rod gauge and feeler | H1, C1 (the plate edge to the rim zone, M8x and M8y) |
| R3 | Floor to the shoulder ledge and floor to the rim face, at the middle of each of the four walls | shoulder 101.04 (range 100.28 to 101.80); rim face 108.97 (range 108.21 to 109.73; the drawing says 109) | height gauge or depth rod on the floor, straightedge across the rim | C6 (the legs' pad height 94.13 is derived from the shoulder's highest), H1 and C1 (M8z), the Z of C3 and C4 |
| R4 | The flat floor under the four feet: the fillet's tangent line and the floor's flatness over each foot's place (|X| 156.0 to 169.0, |Y| 106.4 to 112.4) | tangent at |X| 171.64, |Y| 114.49 (so each foot is 2.64 inside it); flat within 0.5 under a straightedge over each foot's place (the session's figure) | steel rule, straightedge, feeler gauges | C6 |
| R5 | The 1450PF frame: its height, the ring's thickness (the top face to the ring's flat underside), its outline and its window | height 17.5, ring 9.39, outline 378.4 x 263.1, window 349.7 x 233.8, each +-0.76 (sheet 1453-314-000 rev A; the ring's 9.39 from Peli's STEP) | 300 mm caliper (height, ring), 500 mm caliper (outline, window) | C6 (the ring sets the face height, M20 and M21; the window places the locators), H1 and C1 (they lie on the ring) |
| R6 | The insert pattern, the ten brass inserts pressed in (Peli's step 2): centre distances in X across the ends and the long-side pairs, and in Y | 358.14 and 278.90 in X, 242.32 and 151.90 in Y (Peli's STEP; the sheet's 358.1 x 242.3), each within +-0.38 per side, the range at which a 4.6 hole passes the largest 6-32 (M8f) | 500 mm caliper over two bores, edge to edge plus one bore | H1 and C1 (their ten 4.6 holes) |
| R7 | The end walls' and the back wall's thickness at the plates' places | 5.34 on Peli's sections; the design's range 4.58 to 6.10 (T5) | ultrasonic thickness gauge (borrowed), or a caliper through the first drilled hole (T5) | C4 (M11d, M11g, M13b to M17x), C3 (M14c to M14h) |
| R8 | The outside skin at the connector plate's footprint (X -57.0 to +57.0, Z 18.3 to 86.6) and each entry plate's (Y -110.1 to +110.1, Z 34.55 to 83.45) (T6) | plain skin all round each footprint | the 1:1 check prints of `templates/case-templates-1to1.pdf` | C3, C4 and their gaskets G1 to G3 |

Parts that fit nothing on the case (H2, H3 and the lid plate L1) wait on none of these. The results go into
`od01-results/checks.csv` (`TEST-PROCEDURE.md` section 9); the session reads them and writes the release for cutting
part by part."""))

for a, b in R:
    n = s.count(a)
    assert n == 1, ("expected once", n, a[:80])
    s = s.replace(a, b)
assert s != s0
assert "—" not in s and "–" not in s
open(FN, "w", encoding="utf-8").write(s)
t = open(FN, encoding="utf-8").read()
assert t.startswith("# OD-01: request for quote") and MARK in t and t.count("## 6.") == 1
print("MACHINING-RFQ.md patched: %d replacements, %d -> %d chars" % (len(R), len(s0), len(t)))
