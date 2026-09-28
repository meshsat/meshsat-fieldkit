# OD-01: request for quote, the made parts of the heat test and the case mock-up (NOT SENT)

MESHSAT-1357, stream od01, 28 September 2026. Prepared by an AI session for the owner's ruling D-19 ("Obtain machining
quotes separately"). **NOT SENT: no shop has been contacted, no file uploaded, no account opened.** Sending it,
choosing a shop and paying are the owner's. The parts are for a prototype design that has not been built; nothing here
has been made or fitted.

## 1. What is asked, in the order the tests need it

The heat-balance test runs first on the sealed, undrilled case, so its two parts (H1 and C6) are the critical path; the
mock-up follows in the same case. Every drawing states its tolerances, material and finish; the release folder's
`MANIFEST.sha256` was verified on 28 September 2026 at 20:51 UTC (`sha256sum -c` in `v2/release/case-2026-09-27/`: all
files OK). Sheet numbers are those of the release.

| Line | Part | Qty | Material, thickness | Finish | Made how | Needed for | Stage |
|---|---|---|---|---|---|---|---|
| H1 | Heat-test face plate blank: C1's outline and fixings only | 1 | 5754 or 6061 aluminium, 3.0 | black anodised, the same as C1 (see note 1) | CNC or laser plus a rebate pass | heat test | **first** |
| C6 | Setting legs | 4 (two mirror images: cut the profile, flip it) | 6061-T6, 6.0 | edges broken, no finish | waterjet or laser from the profile | heat test and mock-up (T2) | **first** |
| C1 | Face plate, complete | 1 | 5754 or 6061, 3.0 | black anodised | CNC | mock-up T2 and T4 | second |
| C4-E, C4-W | RF entry plates, east (5 arrestors) and west (7) | 1 each | 6061 (or 5052) aluminium, 6.0 | edges broken | CNC (spot-faces) | mock-up T11 (one plate, or a coupon), build T6 and T7 | second (east plate only), rest at build |
| C3 | Connector plate | 1 | 5052-H32 or 6061-T6, 5.0 | edges broken | CNC | build (T6 runs on the paper templates) | quote now, **do not release for cutting** (note 3) |
| G1 to G3 | Gaskets: connector plate, east and west entry plates | 1 each | 2.0 closed-cell EPDM or neoprene | none | knife or waterjet | build (T7) | optional on this quote |
| H2 | Dummy stack plate for the heaters: 200 x 150 x 3.0 at least, the three HS50 heaters bolted to it with compound (each 21.2 W exceeds the HS50's 14 W rating without a heatsink) | 1 | aluminium, 3.0 (any alloy) | none | shear or saw | heat test | first, may be the operator's |
| H3 | Dummy pack block | 1 | aluminium block | none | saw | heat test and mock-up T4 | first, size owed (note 4) |
| L1 | QMX lid plate r2 | 1 | 5052-H32, 2.0 | none | laser plus tapping | build (T8, T9) | optional |

**Not machined, not on this request:** the QMX lid tray r2 and its retaining frame are **printed** in Prusament PC
Blend (`v2/release/case-2026-09-27/lid-tray-qmx-r2/README.md`, choice 4; STL `lid-tray-qmx-r2.stl`
`b5c817fbe08b6d2e7789978310babfa35cf9694dc5846f92602e9b625e655346` and `lid-tray-qmx-r2-frame.stl`
`9494a91024d4fc96ebbde26244bf57055e7e90db1b23be3692fe17895d0f5c3a`), for the build-stage checks T8 and T9 only; the
four leg locators and the two wedge pairs are printed (PETG or PLA, sheet 2); the monitor stand-in for T4 is printed at
the Xenarc drawing's body outline and its 28.66 mm depth (`v2/vendor/xenarc/xenarc-709gnk-dimensional-drawing-v3.pdf`,
`3949bd9f618bbda8522c6df19cdfefc5effcd6d37666e14818466927e7f47f73`); the board stand-ins are cut from the envelope
sheets 7 to 13. These are the operator's or a print service's.

## 2. The files the owner uploads, by path and sha256

All under `v2/release/case-2026-09-27/` (paths relative to it). Upload the drawing PDF with every part: it carries the
tolerances and notes a DXF or STEP does not.

| Line | Upload | sha256 |
|---|---|---|
| H1, C1 | `face-plate/face-plate.step` (CNC) | `48343402a8370f36eb8a0474de6eb3cdee50e1df127c515781736e2ada8ca696` |
| H1, C1 | `face-plate/face-plate.dxf` (layers OUTLINE, THROUGH, POCKET_1MM, REBATE_2MM_TOP, RELIEF_0.8MM_UNDERSIDE, STANDOFF_M3) | `19703fa5838f9e4acbe0dc4021a77ca34b38e8b3c2fbe840678c53dfc6e3c551` |
| H1, C1 | `drawings/face-plate-drawing.pdf` (sheet 1) | `ef9a2fb1df36deef74b5959633dd15583ea7388d8e48bd0f087f9f086fa4d061` |
| C1 | `templates/face-plate-1to1-A3.pdf` (1:1 check print, optional) | `4cf3f68b88d8af9ea47b3c25473e72c52ad62484c7b5aa1e3ddf12a5253f7ee1` |
| C6 | `frame-legs/frame-leg.dxf` (the profile, 4 off) | `68a33b0a6a46d51cff61db70436aa908f943296f5cc78982bf9a13d2e516dc04` |
| C6 | `frame-legs/frame-leg.step` | `2c23e390147fe8e56f6d03852b4c329be9edd9181577431d37227ccc314e3711` |
| C6 | `drawings/frame-and-legs-drawing.pdf` (sheet 2) | `792143ed01c0be6b29c4627fc2470014844fb22fe473e41182ad27239c45dd46` |
| C4-E | `rf-entry-plates/rf-entry-plate-east.step`, `.dxf` | `0d2652add80c7f206240f74e9fcddd040b11ed29bd7e41b6271c1a43b1f801aa`, `97cb168a79c6b37feee6fab2d6865913f48d45250eeadeb75c393b42d2466307` |
| C4-W | `rf-entry-plates/rf-entry-plate-west.step`, `.dxf` | `bfb47212c0606870166168806fac40f9d7619ada3b7205acdaaf7b828697ae10`, `088b58c8347e2839599f1db0c1942511dbe7d1c92718927fd2aecc25c9170a56` |
| C4 | `drawings/rf-entry-plates-drawing.pdf` (sheet 4) | `81379c5092c1646d99b91b919b7eb94fb4da88fa3faf17c06f997e634ec0110c` |
| C3 | `connector-plate/connector-plate.step`, `.dxf` | `fe4af0f61d5446ad8dd495dd5e1fdef73af9cd7904db39852a0c5280fc079717`, `4b838b95ceb7dadbce590953223d0174280a947ca7070a06422765c393d5853f` |
| C3 | `drawings/connector-plate-drawing.pdf` (sheet 3) | `94d6561a437a6412ee8958073cabf27adaa51b1183b1b022d3695e20eadec7d2` |
| G1 | `connector-plate/connector-plate-gasket.dxf` | `e316017eba5b6b29ab1fb0f7a0c171e77805456fa4742e6fa15fd3f71982ee99` |
| G2, G3 | `rf-entry-plates/rf-entry-gasket-east.dxf`, `rf-entry-gasket-west.dxf` | `b5b1532e0c8f324775b5a8730dff2f76f5f1925acba086c22b9fd270975d0158`, `8a92c75721efd029a9147595866f79dba6b23b569af5e8d1d8a5a56c3a4db4d0` |
| L1 | `lid-tray-qmx-r2/lid-plate-qmx-r2.step`, `.dxf`, sheet `lid-tray-qmx-r2-drawing.pdf` | `a292846b390f7193aa3bf82b82b7b1c66281e7455c81f50c92220c1275160601`, `b0b61b1402f620988715a66b44236a1df64a1a799580e5366239aabc91d2b7fc`, `17cad64bc581548aefa3acdc827e371fbce7df59912834b20f39084048b08d35` |

## 3. The request text (NOT SENT)

> Request for quote: aluminium parts for one prototype enclosure, quantity 1 set, delivered to the Netherlands.
>
> Parts and files as in the attached table (lines H1, C6, C1, C4-E, C4-W, C3, optional G1 to G3, H2, H3, L1). Units are
> millimetres. Each part has a drawing PDF; where a DXF or STEP and the PDF differ, the PDF governs and we ask you to
> tell us.
>
> - **H1** is the face plate of sheet 1 without its openings: machine only the outline 377.2 x 263.0 x 3.0 with R16
>   corners, the rebated band (outside 368.0 x 253.0, 2.0 deep from the top face, 1.0 left), the 0.8 relief on the
>   underside, the ten 4.6 holes at the insert pattern and FOUR PEM S-M3 self-clinching nuts in 4.2 holes on a 35.0 x 37.0
>   pattern centred on the PA flange site (they take the heat test's Arcol HS100 patch resistor: its four fixing holes,
>   3.2 maximum, on 35.0 x 37.0, Arcol HS datasheet 12/14.08, page 2). C1 keeps its two nuts 60 apart for the real flange. Omit both windows and their 1.0 pocket, the seventeen 2.6 H7 holes, the eight PEM SO-M3-10 standoffs and
>   the four 4.5 holes for the monitor frame. Black anodised as C1.
> - **C1** is sheet 1 complete: the H1 features plus the monitor window 205.75 x 140.09 R15 at (0, -24), the e-paper
>   window 94.19 x 53.6 at (0, 83) with its 1.0 pocket, seventeen 2.6 H7 holes, eight PEM SO-M3-10 standoffs, two PEM
>   S-M3 nuts and four 4.5 holes. Black anodised; please state whether you insert the PEM hardware before or after anodising.
> - **C6**: four legs from the profile `frame-leg.dxf`, 6.0 6061-T6, two of them mirror images, edges broken. The pad
>   height 94.13 is held to +-0.10 (sheet 2).
> - **C4-E, C4-W**: 220.2 x 48.9 x 6.0 plates, 16.3 through holes (5 east, 7 west) each with a 26.0 x 1.5 spot-face on
>   the back, eight M4 tapped through (drill 3.3), edges broken (sheet 4).
> - **C3**: 114.0 x 68.3 x 5.0, R3 corners, M3 tapped (drill 2.5) and the cut-outs of sheet 3. Quote only; we will
>   confirm the cut-outs before release.
>
> Tolerances (sheets 1 to 4): machined positions and outlines +-0.10; plate thickness +-0.13 (3.0) and +-0.20 (6.0);
> rebate depth and line +-0.10; spot-face floors +-0.10; 2.6 H7 as stated.
>
> Please state, per line: material and temper you will use (no substitution without asking); the finish (anodising type,
> colour, masking); the tolerance you hold on outlines, holes and the leg's pad height; the flatness of the 377 x 263 x 3
> plates after anodising; whether PEM insertion is in house; unit price, set-up or tooling cost, shipping to the
> Netherlands, VAT or import charges and who pays them; lead time to dispatch; and whether a dimensional report on the
> dimensions named above comes with the parts.

## 4. The two routes

- **JLCCNC, online upload** (read 28 September 2026 at 20:56 UTC, https://jlccnc.com/, runner sha256
  `ec2997121c2cc07a`): "Aluminum 6061", "Aluminum 7075" for CNC, "Aluminum 5052" for sheet metal; "Lead time from 3
  business days" (CNC) and "Lead time from 2 days" (sheet metal); "Upload a 3D CAD file (STEP/STP format)" for an
  instant quote; home page prices "From $5.00" and lower, which are not quotes for these parts. The upload is a
  quote only until paid, but it is the owner's account and the owner's action. Upload the STEP per part, choose 6061
  and black anodising for H1 and C1, attach the sheet PDF in the notes, and paste the request text's bullet for that
  part. Import VAT and the carrier's clearance on a shipment from China are the owner's to read at checkout.
- **A local workshop** (a CNC, laser or waterjet shop in the Netherlands, none named: the session has read no
  workshop's page). Send the request text of section 3 with the files of section 2. A local shop suits H2, H3, the
  legs by waterjet and the gaskets, and a caliper report is easier to agree face to face.

A mixed route is reasonable: H1, C1 and the C4 plates from the CNC service, the legs, H2, H3 and the gaskets from a
local shop.

## 5. Notes the quote does not settle

1. **H1's finish matters to the reading.** The heat test measures how much heat leaves through the plate; a bare
   aluminium plate radiates far less than an anodised one, so a blank in another finish would read a different
   conductance from the prototype's plate. H1 is therefore black anodised like C1 (session choice under the standing
   rule of 26 September 2026; reversal: a measured emissivity of both finishes).
2. **Why H1 and not C1 for the heat test.** The heat test needs the sealed skin; C1 is sealed only with the monitor in
   its window, and the monitor is deferred (`CHECKOUT-LIST.md` section 4). H1 keeps C1 undrilled for the mock-up
   (session choice; reversal: buy the monitor early and run the heat test on C1).
3. **C3's cut-outs A, B, E and F are PROVISIONAL** (sheet 3: the sealed RJ45, the USB-C, the M8 receptacle and the
   stud are open picks). Only C and D are picked. Quote it now; release it for cutting only after the picks close.
   T6 on the mock-up uses the 1:1 paper templates, not the plate.
4. **H3's size is owed.** The dummy pack block stands for the 4S3P pack group in its hold-down, which is not designed
   yet (S-27, CON-006; the pocket is X 122.0 to 178.65, Y +-102.75, under Z 39.9 in `zstack/zstack.json`). Until S-27
   fixes the outline, H3 cannot be quoted to a drawing; for the heat test a block of the pack's mass in the pocket is
   the stand-in, and T4 waits on the real outline.
5. **C1 will gain one hole.** The next case release adds a 2.6 H7 light-guide hole for the hardware EMCON lamp D22
   (release README, "What is still open"). A C1 made now for the mock-up lacks it; it can be drilled and reamed later.
6. Every made part is the prototype's own if its checks pass (`READY-TO-ACT.md` section 8), except H1, H2 and H3, which
   serve only the heat test.
