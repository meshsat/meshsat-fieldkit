# L7-R2: the Layer 7 items other layers assigned, on the makers' drawings (MESHSAT-1357, 3 October 2026)

Layer 7 record l7r2, round 2, written on branch `fnd/l7r2` from the integration candidate `fnd/int28` at `a1f696de`. **Prototype design,
desk arithmetic: nothing has been bought, built, powered or measured.** Every figure is printed by `l7r2_items.py` in `l7r2_items.out`
(its section in brackets): a maker's printed figure is MAKER (each transcribed with its document's URL and sha256 in
`inputs/makers-drawings-r2-2026-10-03.md`), this record's arithmetic MODELED, a reading not printed as such INFERRED, a stated
assumption ASSUMPTION, a figure no held document prints NOT READ. The inputs from other branches are copied into `inputs/` with their
commit, path and sha256 (Layer 5's TBD rows at `6902db8f`, record l8gnd's H1 row and F01, F07 at `226e9143`, record l8r2's cooler header
at `a441651a`). No generator, CAD file, registry or other record is edited: the CAD change is a release-guarded draft
(`apply_panel1450_coolers_r2.py`), the rest are FINDINGS naming their rows.

## In short

| Item (who assigned it) | Result | Class |
|---|---|---|
| The sealed RJ45 and its shield path (l8gnd F01; IF-EXT-ETH) | **FINDING with the exact missing facts.** No candidate read meets all three needs (a body or backshell that carries the shield to the plate, a rating for the PoE feed's 57 V, the plate's shell 15 envelope): Bulgin PX0833 with PX0888 carries the shield but is rated **42 V** and its 38.1 ring breaks the plate (worst pair -1.67); Glenair 233-330 (metal, shell 17 at least) **does not fit the plate even re-laid** (least spare -1.07 mm over every low-row layout searched); Amphenol LTW RCP-5SPFFH-SCM7001 prints **44 to 57 V** but its shield path, drawing and 5.0 mm panel are NOT READ. Decided meanwhile: the connector plate gets a conductive conversion coat, not anodise (F-R2-01); the questions to Glenair and LTW are drafted | open, two maker questions |
| The bonding strap, lugs and stud (l8gnd F07; IF-A-CHASSIS) | **DECIDED:** JST R5.5-4 (M4, B 9.5 on H1's 12.0 ring) and R5.5-6 (M6, B 12.0 on the stud), a 6 mm2 class tinned copper conductor; the stud an M6 A4 threaded stud of 45 with the stack computed (inside 10.2 of the 12 allowed with a thin Nyloc); the strap **363 mm** to H1 as drafted beside J_DOCK, **95 mm** if H1 moves to board A's north edge under the stud (F-R2-06) | decided; the length conditional on H1's site |
| The right-angle SMA plug (M17g, M17x; IF-AE-RF) | **DECIDED: Radiall R125.172.001** (RG 316 crimp): M17x **MET** (6.84 nominal, 2.57 at the worst); M17g met with **5G MAIN turned 26.5 degrees** (lands 0.37 above its place; at 30 degrees it lands 0.81 below) and **IRIDIUM moved to the back bundle** (the 3.275 ferrule cannot sit beside a passing cable). **FINDING:** M18 at the 5G MAIN site falls to -0.04 at the worst (the plug's inner end 13.4 beyond its reference plane against the class's 10.0); a plug 12.36 or less beyond meets it | decided with one finding |
| The fans' lead terminations (IF-E-FANS, IF-B-FANS) | **DECIDED: JST PH on both boards** (B4B-PH-K-S, PHR-4, SPH-002T-P0.5S: AWG 30 to 24, -40 to +105 C, 2 A): board B's SH takes only AWG 28 to 32 at -25 to +85 C and board E's 2.54 mm pin header is unkeyed. FINDINGS for Layer 8 boards B and E (the land) | decided; the fans' lead gauge NOT READ |
| The cooler fan's fit and bracket (l7pwr F-L7-03) | **DECIDED:** the fan flat on a 1.0 mm aluminium cap bracket over each cooler, at Y 46.745 to 86.745 between the Xenarc body and the backer's strip; top Z **90.16**: **3.46** under the PA's underside (slots 1, 2), **13.36** under the plate (slot 3); the heatsink envelope corrected to the maker's 12.7; the CAD change drafted | decided; the plan margins (1.0, 1.255) OPEN at the worst |
| The fans' mounting and leads, both sites | coolers: leads of about 97 mm to J_FAN1..3; mixers: their headers read on board E (J_FAN1 (-138, -49.3), J_FAN2 (-132, -49.3)), **their sites not drawn** (NOT READ): a CAD item | half decided |
| J_AB2 and the MAIN lead, W4-F17 (IF-AB-WALL, IF-AC-MAINSW) | W4-F17 re-measured: J_AB2 at (95, -11) inside D's rectangle, **3.10 mm** into D's underside before its socket; the decision is board A's placement (Layer 8, Layer 10). Lengths: J_AB2 ribbon **128 mm** (conditional on the move), MAIN lead **480 mm** on the drawn route | lengths decided on a stated route; W4-F17 a finding |

## 1. The sealed RJ45 and its shield path [1]

**The need**, from the records: a sealed RJ45 whose body or backshell carries the patch cable's shield to the connector plate (GND-002
point 3; record l8gnd F01: without it C33 and J_ETH's shell float and change 2 is inert), with a voltage rating that covers the PoE feed (+54V_POE; the PSE range
to 57 V), inside item A's envelope on the plate (MIL-DTL-38999 shell 15 class: flange 31.29 square, mated 32.51, wall hole 29).

**The method** is frame_seat.py's own (each part at its float on its fixings, two machined places to a pair, the 1.0 minimum, the
gasket band's 3.0, M14e's patch plug under B16 and U51), reimplemented on panel1450's `CONN_ITEMS`; it reproduces CASE-MARGINS' M14k at
the worst (D/F 1.11, A/C 1.12, C/B 1.13) before judging any candidate.

| Candidate (maker's document) | Shield to the plate | Voltage | Fit on the plate | Price read |
|---|---|---|---|---|
| Bulgin PX0833 coupler with the PX0888 backshell (PX0833 sheet held; PX0888 from the archive of Bulgin's own page) | yes: "PX0888 Shielding Backshell ... to maintain RJ45 coupler shielding directly to panel", SS 304 (MAKER); the PX0833/E's earth wire as an alternative | **42 V maximum** (MAKER): under the PoE feed, NOT ELIGIBLE | its 38.1 coupling ring at A's place: worst pair **-1.67** (A / C) | PX0833 EUR 78.22 at 1 (Farnell 9667725, stock 680); PX0888 EUR 2.81 at 50 (Heilind, stock 0) |
| Glenair 233-330 feed-through (an aluminium shell whose external dimensions the maker gives as those of D38999/20, /24 and /26; shell 17 or 19 only) | the shell is metal with conductive finishes; whether the jacks' shields join the shell: NOT READ | NOT READ (no rating printed) | shell 17: flange 33.60 max, mated plug 35.7 (Amphenol's D38999/26 table), rear thread 30.16: at A's place worst pair **-0.52** (A / C mated), gasket band 2.30 against 3.0; **every re-laid low row searched** (A, C and B moved on a 0.25 mm grid) leaves at least one row short: least spare **-1.07 mm** (A's flange against D's above, or the band) | no row served (NOT READ) |
| Amphenol LTW RCP-5SPFFH-SCM7001, middle size, screw thread (the maker's product page) | "Plastic, Shielded": the shield's way to the panel NOT READ | **44 to 57 V** (MAKER) | its drawing is behind the maker's download form (NOT READ); panel 3.00 max without the cap against the plate's 5.0 (a spot face would be needed) | EUR 6.77 at 1 (Farnell 2708703, stock 556) |
| Amphenol Socapex RJF / RJFTV (Amphenol's RJFIELD catalogue) | "metallized ... electrical continuity from the cordset to the panel" (MAKER) | not printed for RJF or RJFTV (only the ATEX range's 60 Veff) | RJF is MIL-DTL-26482 shell 18, RJFTV MIL-DTL-38999 shell 19: larger than the 233-330's shell 17, which already does not fit (not computed further) | not read |

**Result: no part read meets all three needs, so the coupler is not decided.** The exact missing facts: Glenair's voltage rating, its
jacks' shield-to-shell bond and whether a shell 15 RJ45 exists (`clarification/glenair-233-330.txt`); LTW's drawing, its shield's path
to the panel and a 5.0 mm panel (`clarification/amphenol-ltw-rcp-5spffh-scm7001.txt`). **What is decided now (SESSION):** the connector
plate's finish is a conductive chemical conversion coat (the MIL-DTL-5541 Type II Class 3 class, INFERRED: standard not held), with
no anodise or paint under any flange, the stud's washers or the RF entry plates' nuts, so that whichever metal or backshelled coupler
is picked bonds through its flange (F-R2-01). **Consequence:** until a coupler is picked, l8gnd's change 2 (C33 and J_ETH SH on
CHASSIS) stays inert, as l8gnd F01 says; the draft itself is right and is not touched. The fallback if both makers answer no: the PX0833/E
class with its earth wire to the stud F is the shield path, and the PoE port's voltage is the owner's question (it would change what
the port offers), which this record does not ask.

**What transfers to T-H1's mock-up:** none of the electrical path; the mock-up's plate blank should carry the same conversion coat if
it is to be the kit's plate, and the A hole is cut only once the coupler is picked.

## 2. The bonding strap, its lugs and the stud [2]

**DECIDED (SESSION):**
- **At H1** (record l8gnd's `ChassisLug_M4_CHASSIS`: ring 12.0, drill 4.3): **JST R5.5-4**, the non-insulated ring tongue for M4 (d2
  4.3, B 9.5, L 19.8, T 1.0, AWG 12 to 10 / 2.63 to 6.64 mm2, MAKER): 2.5 mm of the ring to spare, inside l8gnd's "up to 11 mm".
- **At the stud F**: **JST R5.5-6** (d2 6.4, B 12.0, L 25.8): the inside washer class of CASE-MARGINS item F (12).
- **The conductor**: a 6 mm2 class flexible tinned copper conductor (l8gnd F07's class), crimped in both barrels (the 5.5 barrel takes
  2.63 to 6.64 mm2). Its maker's sheet is owed (a Layer 6 pick of the cable; F-R2-07).
- **The stud**: an M6 A4 threaded stud of 45 (DIN 976-1 class, INFERRED), through the plate, its gasket and the wall (grip 12.34):
  outside a serrated washer, a hex nut clamping the plate, a serrated washer, three lugs (the external earth lead and the two RF entry
  plates' leads), a washer and a knurled nut (18.5); inside a washer, the strap's lug, a washer and a **thin** Nyloc (ISO 10512 class):
  **10.2** against the 12 CASE-MARGINS allows (a regular Nyloc takes it to 12.2, over). Dimensions of the standard parts INFERRED.
- **The length**, on a route drawn here (down the free band between B16's edge and the wall, at Z 30 over board A's top under B16,
  15 percent for the bends and barrels, ASSUMPTION): **363 mm** to H1 as l8gnd drafted it (beside J_DOCK on the back-wall side, about
  (-76, -50.5)); **95 mm** to an H1 at board A's north edge under the stud (about (34.6, 72.5)).

**FINDING F-R2-06** (Layer 8 board A, Layer 10, the GND-002 owner): GROUNDING-AND-SHIELDS asks for the strap "to board A's ground near
the dock"; the dock is at the front wall and the stud at the back, so as drafted the one bond is a 363 mm conductor across the case. A
site at A's north edge under the stud makes it 95 mm. Which the bond needs (a discharge path's inductance against the dock's proximity)
is the strategy's question, not a fit question; this record gives both lengths.

**Prices** (indicators): R5.5-4 EUR 0.17 at 1 (RS 6048373, stock 12,400); R5.5-6 USD 0.11 at 431 (TME). **T-H1:** no part of the bond
transfers to the mock-up.

## 3. The right-angle SMA plug at the arrestors [3]

**DECIDED (SESSION): Radiall R125.172.001**, SMA right-angle crimp plug for RG 316 (Radiall's technical data sheet, Issue 0122 R, read
off its drawing): reach from the mating axis to the ferrule's end **15.2**, ferrule **3.275** (crimp hexagon 3.25), the cable axis **3.3**
below the plug's inner end, the inner end **13.4** beyond the reference plane, 250 Veff, stainless body.

| Row | With the class (CASE-MARGINS) | With R125.172.001 | Lever taken |
|---|---|---|---|
| M17x (the inboard column to B16's edge) | -0.38 at the worst with the cable axis at the inner end | **6.84 nominal, 2.57 at the worst** by CASE-MARGINS' own relation (the axis offset, less half the ferrule's excess over 2.58) | none: **MET** |
| M17g (MAIN's own cable onto its place, Z 50.535) | -1.21 nominal at 16.0 reach | at 30 degrees it lands at 49.73, **0.81 below its place** | **5G MAIN turned 26.5 degrees** (CASE-MARGINS' lever): lands at 50.90, 0.37 above its place; the steepest turn that lands at or above it is 27.6 degrees |
| the inner upper place beside MAIN's ferrule | needs a ferrule of 2.58 or less | 3.275: no passing cable may sit there | **IRIDIUM moves to the back bundle** (CASE-MARGINS' lever): at most two cables pass under a plug (MAIN two, DIV and LORA one) |
| M18 (the plug's inner end to the RockBLOCK's box at 5G MAIN) | +3.36 at the worst with the class's 10.0 beyond the jack's end | **4.23 nominal, -0.04 at the worst** (the inner end 13.4 beyond the reference plane, taken as the jack's end, INFERRED) | **FINDING F-R2-03**: a plug 12.36 or less beyond its reference plane at that site meets it; R125.172.001 stands at the other eleven sites |

The worst-case values of M17g with the lever, and M18 at every site, are frame_seat.py part G's to recompute with these figures on the
box (F-R2-04, for v2/cad's owner). **Price** (indicator): USD 14.68 at 1 (Richardson RFPD, stock 0); Farnell EUR 15.63 at 50 (stock 0).
**T-H1:** none (no jumper is in the empty-case test).

## 4. The fans: terminations, the cooler fan's fit and bracket, the leads [4]

**Terminations, DECIDED (SESSION): JST PH 2.0 four-way on both boards** (B4B-PH-K-S header, PHR-4 housing, SPH-002T-P0.5S contacts for
AWG 30 to 24; 2 A at AWG 24, 100 V, **-40 to +105 C**, MAKER). Why: board B's JST SH (record l8r2 keeps BM04B-SRSS-TB) crimps only **AWG 28
to 32** and is rated **-25 to +85 C**, and the fans' lead gauge is NOT READ (Sanyo Denki's manual is behind a form): PH takes the whole
range small fans use; board E's key PH4 resolves to a **2.54 mm unkeyed pin header** (HF-F04's class), so a reversed fan plug puts 12 V
on its PWM or pulse lead. The fans' leads are cut to the lengths below and crimped (the fans' own length as supplied NOT READ,
`clarification/sanyo-denki-fan-leads.txt`). **FINDINGS F-R2-08 and F-R2-09** for Layer 8 boards B and E: J_FAN's land becomes
`Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical`, pin order kept (1 12 V, 2 GND, 3 tach, 4 PWM on B; 1 12 V, 2 GND, 3 PWM, 4 tach on E
as L4-E11 section 18 draws it). Prices (indicators): B4B-PH-K-S EUR 0.36 at 100 (Farnell), PHR-4 EUR 0.07 at 100, SPH-002T-P0.5S EUR
0.05 at 1.

**The cooler fan's fit (F-L7-03), DECIDED (SESSION):** the fan lies flat on a **cap bracket** over each Raspberry Pi CM5 cooler: a 1.0 mm
5052 aluminium frame bearing on the fin tips (the cooler 56 x 41 x 12.7, base 2.7 and fins 10 from its brief), with two legs down the
cooler's long sides hooking under its base, the fan on four M3 screws through its flange; nothing uses the module's four holes. The
stack: board B's top 50.60 + the module stack 5.86 (panel1450's figure) + the cooler 12.7 + the frame 1.0 + the fan 20 = **Z 90.16**.
Plan: X at the cooler's centre (the 40 inside the cooler's 41), **Y 46.745 to 86.745**: 1.0 north of the Xenarc body's edge (its body
hangs to Z 77.86) and 1.255 south of the backer's top strip (its underside at 91.92). Over the fan: **the PA's underside at 93.62 (slots
1 and 2): 3.46**; the e-paper module at 100.52 (slot 2); **the plate's underside at 103.52 (slot 3): 13.36**. The 1.0 and 1.255 plan
margins are nominal: at the worst (the plate's float 0.63, the stack's placement) they are OPEN, as the case's other face rows are; the
box run that re-reads zstack.json after `apply_panel1450_coolers_r2.py` decides them (F-R2-04). The draft also corrects the heatsink
envelope from the render's 21.0 to 18.56 (the maker's 12.7 on the module stack).

**Leads:** the cooler fans' leads to J_FAN1..3 ((-97.5, 45), (-27.5, 45), (92.5, 44)) about **97 mm** each (plan, rise and a 40 mm
service loop, MODELED). **The mixers:** their headers are on board E's dock strip (J_FAN1 (-138, -49.3), J_FAN2 (-132, -49.3)); their sites
"at the stack's ends" are not drawn anywhere (CASE-MARGINS section 7 lists them as owed), and the west end's free band is the RF jumpers'
drop zone: **FINDING F-R2-05**, the mixers' sites need the free-volume map over boards B, C, D and E (zstack over every board, a box run);
their leads follow from the sites.

**What transfers to T-H1's mock-up:** the brackets (the bill's "fan brackets", NOT READ in record l7pwr) are this part: three cap
brackets of 1.0 mm aluminium and the fans in the decided places; the mock-up then reads the conductance with the fans where the kit
has them.

## 5. J_AB2, the MAIN lead and W4-F17 [5]

**W4-F17, re-measured:** board A's J_AB2 is FIXED at (95, -11, rot 180) in `gen_pcb_a3.py`, inside D's rectangle (0, -40, 100, 40); the
2x5 header (9.1 by its class) stands from A's top at 17.70 to 26.80 against D's underside at 23.70: **3.10 into D before its socket**.
The remedy is board A's placement (moving the header out of D's rectangle; the east strip X 105 to 118 is full, `gen_pcb_a3.py`'s own
note) or D's standoff re-derived against D's tallest part, which no held reading gives (NOT READ): **FINDING F-R2-10** for Layer 8 board A
and Layer 10, unchanged in kind, now with the number.

**Lengths (MODELED, on stated routes; ASSEMBLY.md's leads table, the integrator's page):**
- **J_AB2 ribbon:** from A's header to B16's J_AB2 at (126, -70) on B's underside: plan 66.6, rise 31.30, two 15 mm folds: **128 mm**,
  2x5 1.27 mm flat cable, IDC both ends; conditional on W4-F17's move (a new site moves the plan distance).
- **MAIN lead:** from C7's land (-62, -108) under the backer's south strip, down outside B16's south edge to A's top, north along X -10
  (west of D8) to Y 75 and east to A's J_MAINSW (98, 75): **480 mm** with 15 percent, 24 AWG twisted, XH2.5 at A's end (ASSEMBLY.md's row).
  The face lifts with the lead unplugged at A (ASSEMBLY.md), so the length is the route's, not a service loop's.

## 6. The Layer 7 criteria moved (`LAYER-STATUS.md`, the integrator's page; proposed cell texts)

| Item | Proposed | Why |
|---|---|---|
| 7.4 mounting and retention | PARTLY: "the face's mounting drawn (C1); the cooler fans' cap bracket specified and their envelope drafted (record l7r2, `apply_panel1450_coolers_r2.py`); the pack hold-down (S-27), the stack's retention and the mixers' sites undesigned" | the fans' retention is specified; the rest is as before |
| 7.5 connector, cable and service access | PARTLY: "the connector plate (C3) drawn; the right-angle jumper plug picked (Radiall R125.172.001: M17x met, M17g met with 5G MAIN at 26.5 degrees and IRIDIUM in the back bundle, M18 at 5G MAIN -0.04 at the worst, F-R2-03); the bond's lugs and stud picked (JST R5.5-4, R5.5-6, M6 x 45); the fans' terminations on JST PH; the J_AB2 and MAIN lengths 128 and 480 mm; the sealed RJ45 open: no candidate read carries the shield, the PoE voltage and the plate's envelope together (record l7r2 section 1)" | three of the four connector items decided, one with a measured finding |
| 7.8 thermal interfaces specified | PARTLY: "...; the five fans picked (record l7pwr) and the cooler fans placed on their brackets over the coolers with 3.46 to the PA and 13.36 to the plate (record l7r2), the mixers' sites owed; the conductance waits on T-H1" | the cooler fans' interface is placed |
| 7.9 critical fit uncertainties resolved | OPEN: "...; new nominal fits awaiting the box: the cooler fans' plan margins 1.0 and 1.255 (F-R2-04), M18 at 5G MAIN (F-R2-03); W4-F17 re-measured at 3.10 into D" | findings added, none closed by evidence |

## 7. Findings for other layers

| Id | For | Finding |
|---|---|---|
| F-R2-01 | v2/cad's owner (the connector plate's and the RF entry plates' drawings), GROUNDING-AND-SHIELDS' owner | the plates' finish: a conductive chemical conversion coat (MIL-DTL-5541 Type II Class 3 class, INFERRED), no anodise or paint under flanges, washers and nuts; today no finish is stated anywhere |
| F-R2-02 | the owner's send list (the integrator) | `clarification/glenair-233-330.txt` and `clarification/amphenol-ltw-rcp-5spffh-scm7001.txt` decide the sealed RJ45; `clarification/sanyo-denki-fan-leads.txt` the fans' leads and PWM (with record l7pwr's F-L7-11, Layer 5's L5R2-F07) |
| F-R2-03 | v2/cad's owner (CASE-MARGINS M18) | at the 5G MAIN site R125.172.001's inner end (13.4 beyond its reference plane) leaves -0.04 at the worst against 1.0; a plug 12.36 or less beyond meets it, or the RockBLOCK's box moves (board B) |
| F-R2-04 | v2/cad's owner (the box) | run `apply_panel1450_coolers_r2.py` (release-guarded), re-take zstack.json and the gates that read B16_TALL, and frame_seat.py part G with R125.172.001's figures, 5G MAIN at 26.5 degrees and IRIDIUM in the back bundle |
| F-R2-05 | v2/cad's owner | the mixers' sites: a free-volume map over boards B, C, D and E (zstack over every board) |
| F-R2-06 | Layer 8 board A, Layer 10, the GND-002 owner | H1's site: beside J_DOCK the strap is 363 mm, at A's north edge under the stud 95 mm (section 2) |
| F-R2-07 | Layer 6 | the strap's conductor: a 6 mm2 class tinned copper flexible conductor's maker sheet (current, temperature, bend) |
| F-R2-08 | Layer 8 board B (record l8r2's `apply_gen_sch_b_fans12.py`) | J_FAN1..3 on JST PH B4B-PH-K-S instead of SH BM04B-SRSS-TB (AWG and temperature, section 4) |
| F-R2-09 | Layer 8 board E (L4-E11 section 18's draft; HF-F04) | J_FAN1, J_FAN2 on JST PH B4B-PH-K-S instead of the 2.54 mm unkeyed pin header |
| F-R2-10 | Layer 8 board A, Layer 10 | W4-F17: J_AB2 3.10 into D's underside before its socket; move the header out of D's rectangle, or read D's tallest part to re-derive the standoff |
| F-R2-11 | the integrator (`.gitignore`) | `v2/docs/records/l7r2/held/` (this record's `fetch_held_back.py` writes there) |
| F-R2-12 | ASSEMBLY.md's owner | "the CM5 Cooler clips on each module": the Raspberry Pi Cooler is screwed from beneath the carrier into its tapped holes (its brief); with the module on M2.5 standoffs from above, the module's four holes cannot also take the cooler's screws as written; the stack's fixing is to restate |

## 8. Decisions taken by the session (authority: SESSION, under the owner's standing rule of 26 September 2026)

| Decision | Why the session's | Reversed by |
|---|---|---|
| no sealed RJ45 is picked; the plates take a conductive conversion coat | no candidate read meets the shield, the voltage and the envelope together; a pick that fails one would be a guess or a requirement change | a maker's answer that closes the missing facts |
| the bond's lugs JST R5.5-4 and R5.5-6, a 6 mm2 class conductor, an M6 x 45 A4 stud with a thin Nyloc inside | the makers' printed rows fit H1's land and the stud's class, and the stack keeps inside the 12 | a land or a stud of another size; a lug maker's other part |
| the jumper plug Radiall R125.172.001, 5G MAIN at 26.5 degrees, IRIDIUM in the back bundle | the only right-angle RG 316 plug whose drawing was read; CASE-MARGINS' own levers | a plug whose inner end is 12.36 or less beyond its reference plane (then also M18 at 5G MAIN) |
| JST PH on both fan headers | it takes AWG 30 to 24 and -40 C, the fans' gauge being unread; SH does not, the pin header is unkeyed | the fans' lead gauge read as 28 or finer (then SH on board B stands) |
| the cooler fan flat on a cap bracket at Y 46.745 to 86.745 | the one band between the Xenarc and the strip where nothing hangs lower than the PA | the box's re-take of the face rows |
| route lengths with 15 percent | a stated allowance for bends, barrels and terminations | a drawn harness |

## 9. Files

`L7-R2-ITEMS.md` (this page); `l7r2_items.py` and `.out`; `apply_panel1450_coolers_r2.py` (the CAD draft); `fetch_held_back.py` (the
makers' documents into `held/`); `inputs/` (the copied inputs, the drawings' transcription, the price readings); `clarification/`
(Glenair, Amphenol LTW, Sanyo Denki); the test `v2/ecad/tools/tests/test_l7r2.py`.

## 10. Not claimed

Nothing is built, bought or measured; no fit is shown at the worst where this page says OPEN; the software test establishes this
record's own arithmetic and text, not any property of a part, a cable or the case.
