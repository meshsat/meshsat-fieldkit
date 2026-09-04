# ORDER-LOG.md: JLCPCB ordering of the MeshSat field-kit carrier boards (MESHSAT-709)

Order session started 2026-09-03. Operator: Claude Code on the laptop via the Chrome extension, JLCPCB account already logged in. Nothing is paid by this session; every board stops at the cart. The order gate is the 12 Sep review with Nick and the owner's "order now".

## 1. Intake checks (step 1 of the method), 2026-09-03

Inputs read: all six ORDER-NOTES.txt, README.md, ASSEMBLY.md section 9 (bench-fit lists). Gerber zips in `JLCPCB/` are byte-identical to the ones in the deliverable folders (cmp).

### 1.1 BLOCKING: the three 4-layer zips contain no inner copper layers

| Board | Notes say | Zip contains | KiCad board |
|---|---|---|---|
| PCB-A-POWER-A15 | 4 layers, JLC04161H-7628 | F_Cu, B_Cu only (no In1/In2) | 4 copper layers, 463 items reference In1.Cu, 306 reference In2.Cu |
| PCB-B-COMPUTE-B10 | 4 layers, JLC04161H-7628 | F_Cu, B_Cu only | 4 copper layers, 582 on In1.Cu, 520 on In2.Cu |
| PCB-D-APRS-D5 | 4 layers, JLC04161H-7628 | F_Cu, B_Cu only | 4 copper layers, 229 on In1.Cu, 169 on In2.Cu |

Every zip holds exactly 11 files: F/B copper, mask, paste, silk, Edge_Cuts, .drl and the drill map. The inner layers were not exported. Uploading these three zips as 4-layer would order boards without their planes and inner routing. NOT uploaded. The gerbers must be re-exported with In1.Cu and In2.Cu included (kicad-cli is on this laptop at /usr/bin/kicad-cli; the session rule "never touch the KiCad projects or the generators" means the re-export is the owner's or the design session's call). The 2-layer boards (C3, E1, E2) are complete and proceed.

Also noted: `meshsat-pcb-a-revA-A15/README-fab.txt` carries the PCB-B text (title, size, connector). Cosmetic, the ORDER-NOTES.txt for A15 is correct and wins.

### 1.2 BOM designator format (fixed in upload copies, originals untouched)

JLC's BOM parser expects comma-separated designators. The generated BOMs use range notation (`C34-C37`, `R16-R22`) and KiCad's unannotated marker `?` on every non-numeric reference (`J_DOCK?`, `SW_MAIN?`), while the CPL carries the expanded plain names. Left as is, every such line would fail to pair with its CPL row. Cleaned copies were written to `<board>/upload/` with: ranges expanded, `?` stripped, solder-jumper lines (JPx: pads, no part, absent from the CPL) dropped, and the bench-fitted items from ORDER-NOTES / ASSEMBLY.md section 9 removed from BOM and CPL. After cleaning, the BOM designator set equals the CPL designator set on every board.

### PCB-A-POWER-A15
- Upload copies written to `PCB-A-POWER-A15/upload/` (originals untouched).
- Designator ranges expanded (4 BOM lines): C18,C20,C22,C24,C26,C28,C30,C32,C34-C37; R12,R20-R23,R26,R28,R30,R32,R34; R35-R38; R39-R43
- Trailing "?" stripped (KiCad unannotated marker on non-numeric references, the CPL carries the plain name): J_DOCK?, J_PACK?, J_X1202BAT?, J_X1202DC?
- Solder-jumper lines dropped from the BOM (PCB features, no part, not in the CPL): JP1
- Bench-fitted lines removed from BOM: J_DOCK; from CPL: J_DOCK
- Result: 30 BOM lines (13 with LCSC), 79 CPL placements (top 79, bottom 0); BOM refs == CPL refs: True

### PCB-B-COMPUTE-B10
- Upload copies written to `PCB-B-COMPUTE-B10/upload/` (originals untouched).
- Designator ranges expanded (4 BOM lines): C6,C8,C11,C29-C32; R3-R6,R13,R15,R17,R20,R25,R28,R29; R9-R12; R27,R30-R35
- Trailing "?" stripped (KiCad unannotated marker on non-numeric references, the CPL carries the plain name): J_PANEL?
- Solder-jumper lines dropped from the BOM (PCB features, no part, not in the CPL): JP1, JP3, JP4
- Bench-fitted lines removed from BOM: none; from CPL: none
- Result: 41 BOM lines (16 with LCSC), 113 CPL placements (top 112, bottom 1); BOM refs == CPL refs: True

### PCB-C-DISPLAY-C3
- Upload copies written to `PCB-C-DISPLAY-C3/upload/` (originals untouched).
- Designator ranges expanded (8 BOM lines): C3,C4,C11-C13; C5-C10; Q2-Q4; R1-R5,R7,R8; R11,R34-R38; R13-R15,R23,R28,R32; R16-R22,R24-R27; U5-U8
- Trailing "?" stripped (KiCad unannotated marker on non-numeric references, the CPL carries the plain name): J_EPD?, J_PANEL?, J_X1202SW?, SW_EMCON?, SW_LIGHT?, SW_MAIN?, SW_PI?, SW_SOS?, SW_TEST?, SW_ZERO?
- Solder-jumper lines dropped from the BOM (PCB features, no part, not in the CPL): JP1, JP2
- Bench-fitted lines removed from BOM: SW_EMCON, SW_LIGHT, SW_MAIN, SW_PI, SW_SOS, SW_TEST, SW_ZERO; from CPL: EPD1, SW_EMCON, SW_LIGHT, SW_MAIN, SW_PI, SW_SOS, SW_TEST, SW_ZERO
- Result: 40 BOM lines (19 with LCSC), 88 CPL placements (top 18, bottom 70); BOM refs == CPL refs: True

### PCB-D-APRS-D5
- Upload copies written to `PCB-D-APRS-D5/upload/` (originals untouched).
- Designator ranges expanded (3 BOM lines): C4-C7,C10,C13,C14,C31; C8,C9,C12,C15-C18,C25,C32; C26-C29
- Trailing "?" stripped (KiCad unannotated marker on non-numeric references, the CPL carries the plain name): none
- Solder-jumper lines dropped from the BOM (PCB features, no part, not in the CPL): JP1, JP2, JP3, JP4, JP5
- Bench-fitted lines removed from BOM: none; from CPL: none
- Result: 39 BOM lines (21 with LCSC), 77 CPL placements (top 76, bottom 1); BOM refs == CPL refs: True

### PCB-E1-DOCK-E1
- Upload copies written to `PCB-E1-DOCK-E1/upload/` (originals untouched).
- Designator ranges expanded (0 BOM lines): none
- Trailing "?" stripped (KiCad unannotated marker on non-numeric references, the CPL carries the plain name): J_AUX?, J_DCIN?, J_DOCK?
- Solder-jumper lines dropped from the BOM (PCB features, no part, not in the CPL): none
- Bench-fitted lines removed from BOM: F1, J_DOCK, U1; from CPL: F1, J_DOCK, U1
- Result: 12 BOM lines (9 with LCSC), 12 CPL placements (top 12, bottom 0); BOM refs == CPL refs: True

Consequence for A15: with J_DOCK (the only bottom-side part, bench-fitted spring pins) removed, A15 is top-side-only for assembly, which is what the session prompt asked for if two-sided costs extra.
Consequence for C3: the seven panel switches were the bulk of the top-side placements; assembly stays two-sided (18 top, 70 bottom).

### 1.3 Part-count reconciliation against the notes

The "Parts on the TOP/BOTTOM side" counts in ORDER-NOTES count every footprint (mounting holes, test points, jumper pads, fiducials). The CPL only lists BOM parts, so its row count is lower by exactly those non-parts. Checked per board: no BOM part is missing from a CPL and no CPL row lacks a BOM line after the cleaning above.

### 1.4 LCSC numbers to verify at matching time (same number on two different values)

- E1: D1 "SMCJ33A" and D3 "SMBJ15A" both carry C118172. One of them is wrong.
- E1: C1 "10u 50V 1206" and C3 "22u 25V 1206" both carry C13585. One of them is wrong.
- PCA9555PW is C5626 on A15/B10 and C50993 on C3. Both are checked at matching time.
- D5: "100n 25V" lines use C14663 (the 50 V 0603 part), acceptable.

## 2. Site work, per board

## Design session response, 3 Sep 2026 02:40 (runner session, not the ordering session)

- Inner layers: confirmed and fixed at the source. build_pcb.sh named the copper layers explicitly (F.Cu, B.Cu); it now reads the copper count from each board. All six gerber zips were re-exported and overwritten in JLCPCB/<board>/ and in the deliverable folders; A15, B10 and D5 now carry In1_Cu.g1 and In2_Cu.g2 (verified by listing the zips). Use the top-level zips, not any earlier copy.
- BOM normalisation moved into make_handoff.py (ranges expanded, ? stripped, JP/TP/H/mounting refs dropped, bench-fitted refs excluded per board: A15 J_DOCK; C3 the seven switches and EPD1; E1 U1, F1, J_DOCK). The top-level BOM/CPL in each folder are now equivalent to your upload/ copies; either set is valid. A15 is top-only assembly in the notes.
- E1 LCSC codes: C118172 and C13585 were copy errors in the generator. They are removed from the E1 BOM (C1, C3, D1, D3 now match by value: 10u 50V, 22u 25V, SMCJ33A, SMBJ15A). C14663 on C2 (100n 0603) stands.
- ORDER-NOTES.txt were regenerated with the corrected gerber description; no fab or assembly option changed.

## 1.5 Re-check after the design session response, 3 Sep 2026 (ordering session, laptop)

- Gerber zips re-listed from JLCPCB/<board>/ (the 02:33 to 02:40 exports). A15, B10 and D5: 14 files each, copper F_Cu.gtl, In1_Cu.g1, In2_Cu.g2, B_Cu.gbl. C3, E1, E2: 12 files each, copper F_Cu.gtl and B_Cu.gbl only. Every zip carries both masks, both silks, Edge_Cuts and the Excellon drill. Finding 1.1 is closed; the earlier zips are discarded and only the top-level zips are used from here.
- Top-level BOM and CPL versus upload/ copies: designator sets identical on all five assembled boards (A15 79, B10 113, C3 88, D5 77, E1 12 refs); file content identical on A15, B10, C3, D5. E1 differs only in the four LCSC codes removed from C1, C3, D1, D3. The top-level files are used from here; upload/ is left in place as the record of the first pass.
- E1 C1 (10u 50V 1206), C3 (22u 25V 1206), D1 (SMCJ33A, SMC), D3 (SMBJ15A, SMC) are matched by value on the site; choices logged in section 2.
- Lines without an LCSC number, to be matched on the site: A15 17 of 30, B10 25 of 41, C3 21 of 40, D5 18 of 39, E1 7 of 12.
- ORDER-NOTES.txt regenerated 02:33 to 02:40 by the design session; options unchanged.

## 2. Site work, per board (order: E2, E1, D5, C3, B10, A15)

### PCB-E2-RFJUNCTION-E2 (bare board), saved to cart 3 Sep 2026

- Gerber upload: pcb-e2-rfjunction-gerbers.zip; site detected "2 layer board of 32x330mm" (notes: 330.1 x 32.1, 2 layers). Match.
- Options as set: Standard PCB, FR-4, 2 layers, 330 x 32 mm, qty 5, Industrial/Consumer electronics, single PCB, thickness 2.0 mm, colour Black, silkscreen White, material FR4 TG135, surface finish ENIG (gold 1 U", site default), outer copper 1 oz, via covering Tented (site default), min via 0.3 mm (default), outline tolerance +-0.2 mm (default), confirm production file No, Mark on PCB = Remove Mark (the order-number removal, no fee shown), electrical test flying probe, gold fingers No, castellated holes No, edge plating No, blind slots No, UL marking No, humidity card No, build time 3 days. No matte/gloss selector exists on the site for the black mask; "Black" is the only black option and was taken as the notes' matte black.
- Site prompt "Change Black to Green" (uncommon combination 2 layer / 2.0 mm / Black / ENIG, extra charge, longer panel wait) answered "No, thanks" twice (it reappears after the ENIG click). Owner confirmed black in the session.
- Price: Calculated $57.50 for 5 pcs = engineering fee $33.00 (was $4.00 before the black + 2.0 mm + ENIG combination), surface finish $17.70, board $6.80. Shipping estimate shown separately, FedEx Express $25.21, 0.35 kg (whole-cart figure, not per board).
- Cart line: "pcb-e2-rfjuncti..." 5 pcs $57.50. Screenshot: PCB-E2-RFJUNCTION-E2/jlcpcb-cart-added-2026-09-03.jpg. Not paid.

### PCB-E1-DOCK-E1, PCB options and part matching, 3 Sep 2026

- Site switched its display currency from USD to EUR on its own after the E2 save (a Country/Language/Currency popup opened uninvited; dismissed without saving, the header stayed EUR). E2 is logged in USD, everything from E1 on in EUR.
- Gerber upload: site detected "2 layer board of 44x250mm" (notes 250.1 x 44.1, 2 layers). Match.
- PCB options as set: FR-4, 2 layers, qty 5, 1.6 mm, Black, White silk, FR4 TG135, ENIG 1 U", 1 oz, tented vias, 0.3 mm min via, +-0.2 mm outline, confirm production file No, Mark on PCB = Remove Mark, flying probe, no gold fingers, no castellated holes, no edge plating, no blind slots, no UL, no humidity card. No "change black to green" prompt this time (1.6 mm black is a common combination). PCB-only price at that point EUR 23.31 (engineering 3.45, ENIG 15.28, board 4.58).
- Assembly: PCBA toggled on. PCBA type Standard (Economic greyed out by the site for this board, not chosen by me). Assembly side Top, qty 5, edge rails/fiducials "Added by JLCPCB" (site default; note from the site: production size becomes 250 x 70 mm with two 5 mm rails on the short sides; JLC offers a paid depaneling service to remove them, NOT selected: rails are broken off at the bench or delivered removed per JLC's normal PCBA handling, to be confirmed at checkout). Confirm parts placement No, stencil storage No, fixture storage No, parts selection By Customer (self-service), bake No, board cleaning No, conformal coating No (coating is applied at the bench per ASSEMBLY.md section 5), packaging antistatic bubble (default). Build time flipped to "24 hours PCBA only" by the site.
- BOM + CPL uploaded (top-level pcb-e1-dock-bom.csv / -cpl.csv). Site result: 12 parts detected, 6 auto-confirmed, 2 inventory shortage, 4 not selected. After matching: 12 of 12 confirmed.

| Ref | BOM line | Chosen LCSC | Part | Why |
|---|---|---|---|---|
| C1 | 10u 50V 1206 | C13585 (site auto-match) | Samsung CL31A106KBHNNNE 10 uF 50 V X5R 1206, Basic | matches value, rating and package; this is the code the design session had removed as a copy error, it was right for C1 and wrong for C3 |
| C2 | 100n 0603 | C14663 (BOM) | CC0603KRX7R9BB104 100 nF 50 V X7R, Basic | as given |
| C3 | 22u 25V 1206 | C12891 (site auto-match) | Samsung CL31A226KAHNNNE 22 uF 25 V X5R 1206, Basic | matches value, rating, package |
| D1 | SMCJ33A, SMC | C438109 | SMCJ33A (DO-214AB), Extended, stock 28844 | exact part; five SMCJ33A listings exist, took the one with the largest stock and lowest price |
| D2 | "12 V zener gate clamp", SOD-123, BOM code C8074 | C43491 | BZT52C12 12 V 500 mW SOD-123, Extended, stock 28909 | FLAG: C8074 is ZMM24-M, a 24 V zener in MiniMELF (LL-34): wrong voltage AND wrong package for this line, and it was out of stock (15 shortfall). Replaced by value and package from the BOM text. The generator's C8074 is a copy error of the same class as C118172/C13585; design session to correct the source |
| D3 | SMBJ15A, SMC | C2760888 (site auto-match) | SMBJ15A, Extended | exact part (footprint is D_SMC; SMBJ in an SMC pad is the schematic's choice, unchanged) |
| J_AUX | JST XH B2B-XH-A 2P | C265283 | JST B2B-XH-A-GU (gold), Extended, stock 24529 | genuine B2B-XH-A (C19272845) shows inventory shortage (1 pc); -GU is the same connector with gold contacts; the XY clone (C51940134) was not taken |
| J_DCIN | JST VH B2P-VH 2P 3.96 mm, "10 A" | C265357 | JST B2P-VH-R(LF)(SN), 10 A, Extended, stock 11595 | genuine JST, 10 A as the BOM asks; the XY-B2P-VH clone is rated 3 A and was not taken |
| LED1 | green 0603, BOM code C72043 | C12624 | KT-0603G green 0603 (513 nm, 430 mcd, 3.1 V), Extended, stock 160299 | C72043 (Everlight 19-217/GHC-YR1S2/3T) has 1 pc in stock, 19 shortfall. Note the site now lists C72043 as Extended, not Basic |
| Q1 | "AO4409 SO-8 P-FET -60 V 4 A (alt DMP4015SSS)" | C347462 | AO4409 SOIC-8, Extended, stock 18213 | exact MPN as the BOM names it. FLAG for the design review: the real AO4409 is a -30 V / 15 A part, not -60 V / 4 A as the BOM comment says; on a 9 to 36 V shore input behind a 33 V TVS a -30 V Vds is under-rated. The named alternative DMP4015SSS is -40 V. Not changed here (notes win), reported |
| R1 | 100k 0603 | C25803 (BOM) | Basic | as given |
| R2 | 2.2k 0603 | C4190 (BOM) | Basic | as given |

- Extended parts on this board: 8 (D1, D2, D3, J_AUX, J_DCIN, LED1, Q1 plus none other); each Extended line carries JLC's per-line feeder fee, shown at the quote step.
- Placement preview (Component Placements tab, 2D and 3D): D1, D2, D3 cathode band on the left in JLC's preview and in the KiCad assembly drawing (Review/PCB-E1-DOCK-E1/pcb-e1-dock-assembly-top.pdf). C1, C2, C3, R1, R2 non-polar. LED1 too small to judge in the preview. **Q1 (AO4409, SOIC-8): JLC's pin-1 dot sits at the BOTTOM-left of the package while the KiCad drawing has pin 1 TOP-left.** A 180 degree rotation error would put the dot bottom-RIGHT, so this may be JLC's own marker convention rather than a rotation error, but it is not settled. Not changed on the site (the rotation is design data). A remark was put on the order asking JLC to confirm Q1's orientation in DFM; the owner should check the DFM analysis in Order History 4 to 6 hours after paying, before production starts. J_AUX / J_DCIN are keyed THT connectors, orientation follows the silk.
- INCIDENT, corrected: while the Q1 area was zoomed, a click intended for the NEXT button rotated Q1 by 90 degrees in JLC's placement editor (undo arrow lit up). Undone immediately with the viewer's Undo; undo went grey again and Q1 shows the uploaded orientation (vertical pad columns, dot bottom-left). The saved cart item was created after the undo. Lesson for the remaining boards: never click by element reference on the placement page; use the tab headers.
- Quote step: PCB EUR 26.68 (engineering 3.45, ENIG 15.97, board 7.25) + Standard PCBA EUR 54.10 (setup 22.07, stencil 7.09, components 12 items 7.50, feeders loading 13.21, SMT 0.41, hand-soldering 3.09, manual assembly 0.31, packaging 0.43). **Total EUR 80.78 for 5 assembled E1 boards.** Build time PCB 24 h + assembly 4 to 5 days. Weight shown 1.37 kg.
- Product Description (customs field, mandatory): set to "Research/Education/DIY/Entertainment > Development Board, HS Code 847330". Other choices offered: DIY Hobby Circuit Board 902300, Programmable Controller 853890, plus Sensor/Controller, Office, Audio/Video, Smart Product, Household, Others categories. Owner may prefer another; editable in the cart via Edit Order.
- Remark on the order: "MeshSat PCB-E1 DOCK Rev A. Q1 (AO4409 SOIC-8): pin 1 is top-left per the KiCad footprint; please confirm orientation in DFM. Diode cathodes as in the silkscreen."
- Cart lines: pcb-e1-dock-gerbers_Y3, PCB prototype Y3-11651261A (Black, 1.6, ENIG) 5 pcs EUR 26.68, 24 hours; Standard PCBA SMT026090360135-116... assemble top side 5 pcs EUR 54.10, 4 to 5 days. E2 line now reads EUR 49.64 (was USD 57.50). Screenshots: PCB-E1-DOCK-E1/jlcpcb-placement-preview-2026-09-03.jpg, jlcpcb-cart-added-2026-09-03.jpg. Not paid.

### PCB-D-APRS-D5, PCB options and part matching, 3 Sep 2026

- Gerber upload: site detected "4 layer board of 62x80mm" (notes 80.1 x 62.1, 4 layers). Match. Inner layers present (In1_Cu.g1, In2_Cu.g2 in the zip).
- PCB options as set: FR-4, 4 layers, qty 5, 1.6 mm, Black (colour fee EUR 6.91), White silk, FR4 TG135, ENIG 1 U", outer copper 1 oz, inner copper 0.5 oz (site default; the notes only state 1 oz outer), Specify Layer Sequence No, Specify Stackup No (JLC's default 4-layer 1.6 mm stackup is JLC04161H-7628, the one the notes name; no controlled impedance ordered, as the notes say none for D5), via covering Plugged (site default for 4-layer), 0.3 mm min via, +-0.2 mm outline, Mark on PCB = Remove Mark, flying probe, no gold fingers, no castellations, no press-fit, no edge plating, no blind slots, no UL, no backdrill, no humidity card. PCB-only price EUR 27.63 (special offer 6.04, ENIG 14.68, colour 6.91).
- Assembly: Standard (Economic greyed out), BOTH sides as the notes say (R36 on the bottom), qty 5, edge rails Added by JLCPCB (production size 80 x 72 mm, two 5 mm rails on the short sides), confirm placement No, parts selection self-service, no extras.
- BOM + CPL uploaded (top-level files). Site: 39 lines, 26 auto-confirmed, 3 shortage, 10 unmatched, plus 8 lines the site left unticked as "multiple lines matched to the same part" or "comment does not match": all reviewed and ticked where correct (100n / 100n 25V both C14663 as the BOM gives; 4.7n NP0 / 4.7n both C53987 as the BOM gives, note C53987 is X7R not NP0, taken as given; R30 C2933194 301k, R33 C2933128 105k confirmed).

| Ref | BOM line | Chosen LCSC | Part | Why |
|---|---|---|---|---|
| C23,C24 | 22u 10V X7R 1210 | C2918511 | Samsung CS3225X7R226K250NRL 22 uF 25 V X7R 1210, Extended, stock 136954 | site auto-picked C52306 (X5R); replaced by an X7R as the BOM asks ("Replace All" applied to both 22u lines) |
| C26..C29 | 22u 25V X7R 1210 | C2918511 | same | same |
| L1 | 1.5 uH Coilcraft XAL6030-152MEB, Isat 12 A | NONE, line unticked | | site auto-matched C139207, a 0603 25 mA inductor: WRONG package and rating, removed. No XAL6030 and no 6030-footprint 1.5 uH part with 12 A saturation in JLC's library. LEFT UNFITTED, FLAG: bench-fit the Coilcraft part (Mouser/Digikey) or the design session picks a JLC-stocked equivalent and changes the footprint |
| R31 | 100k 1% (ILIM) | C25803 | 0603WAF1003T5E 100k 1%, Basic | site auto-picked C2961368 (0.1 % thin film, Extended); the BOM asks 1 %, the Basic part matches and is already on the board (R35, R38, R39) |
| R32 | 17.4k | C304711 | RS-03K1742FT 17.4k 1% 0603, Extended, stock 7848 | C22819 (BOM auto-match) had 8 in stock, 12 short |
| R34 | 20k 1% | C4184 | 0603WAF2002T5E 20k 1%, Basic | site auto-picked C863663 thin film, 10 short; Basic part matches |
| D1 | green 0603, BOM C72043 | C12624 | KT-0603G green 0603, Extended | C72043 19 short (same as on E1) |
| D2 | red 0603, BOM C2286 | C2286 | KT-0603R, Basic | as given |
| J_HARN1 | IDC 2x8 2.54 mm vertical | C18202144 | XDFH-0254-2*8P shrouded box header, through hole, 3 A, Extended, stock 1060 | value/footprint match |
| J_PWR1 | JST VH B2P-VH 2P | C265357 | JST B2P-VH-R(LF)(SN) 10 A, Extended | same as E1 J_DCIN |
| J_SWD1 | pin header 1x7 1.27 mm vertical | C22438104 | HX PZ1.27-1x7P ZZ straight, Extended, stock 10073 | value/footprint match (WZ variant is right-angle, not taken) |
| Q1, Q2 | BC847 SOT-23 | C8664 | Nexperia BC847C,215, Extended (site now lists it Extended), stock 1019246 | BC847C is the C gain bin of the same part |
| Q3 | 2N7002 SOT-23 | C8545 | 2N7002, Basic | exact |
| Q4 | BC857 SOT-23 | C8666 | Nexperia BC857C,215, Extended, stock 30835 | C gain bin |
| U1 | TPS61089 VQFN-11 | C165129 | TI TPS61089RNRR, Extended, stock 2644, EUR 0.43 each | exact; the RNRT reel (C131352) is out of stock |
| U3, U4 | AP2112K-3.3 SOT-23-5 | C51118 | Diodes AP2112K-3.3TRG1, Extended, stock 67479 | exact |
| U5 | STM32F302CBT6 | C94046 (BOM) | Extended, EUR 29.50 for 5 | as given |
| U6 | USBLC6-2SC6 | C7519 (BOM) | Extended | as given |
| Y1 | 8 MHz 20 pF 5032 | C115962 (BOM) | Basic | as given |

- Result: 38 of 39 lines matched, L1 deliberately unfitted. Extended lines carry a feeder fee each.
- Site-side hiccup, no effect: one search click landed on a table header while the rows had just re-flowed; a ctrl+a then selected the page text and the typed search string went nowhere. Deselected and redone.
- Placement preview (3D, top and bottom), compared with Review/PCB-D-APRS-D5/pcb-d-aprs-assembly-top.pdf:
  - **J_HARN1 (IDC 2x8 box header, C18202144): ROTATION MISMATCH.** JLC renders the shrouded header body HORIZONTAL (2 rows of 8 along X) across the top of the pad field and hanging off the board's west edge; the KiCad footprint is VERTICAL (8 rows of 2 along Y, pin 1 top-left). 90 degrees off.
  - **U5 (STM32F302CBT6, LQFP-48): pin-1 dot at the BOTTOM-left in JLC's preview, KiCad drawing has pin 1 TOP-left.** Same pattern as Q1 (SOIC-8) on E1. On a square LQFP this is invisible in the pad pattern and would be a real 90 degree placement error if JLC's preview reflects production. This looks like the well-known KiCad-vs-JLC rotation-origin difference (JLC's library zero for LQFP/QFN/SOIC is 90 degrees from KiCad's); the CPL exporter did not apply JLC rotation offsets.
  - U3, U4, U6 (SOT-23-5/6): JLC pin-1 marks top-left, KiCad triangle top-left. Match.
  - U1 (TPS61089, VQFN-11): too small to judge in the preview; same package class as the LQFP risk.
  - Q1..Q4 (SOT-23): JLC marks at the top-left of each; KiCad triangles top-left. Match.
  - Y1 (5032 crystal): 2-pin, non-polar in this footprint. C, R, FB: non-polar. D1, D2 (0603 LEDs): too small to judge.
  - J_PWR1 (JST VH): body along X at the bottom-left, pins side by side, consistent with the drawing.
  - Bottom side: R36 only, fine.
  - NOT rotated on the site (design data). **This is a stop item for the owner / design session before payment:** either the CPL exporter applies JLC's rotation table (LQFP, QFN, SOIC and the 2x8 IDC header at least) and the CPL is re-uploaded, or the parts are rotated in JLC's placement editor and the result is re-checked, and E1's Q1 gets the same treatment. JLC's DFM/engineering review may also query it, but do not rely on that.
- "Project has unselected parts" dialog at NEXT (because of L1): answered "Do not place".
- Quote step: PCB EUR 27.71 (special offer 6.04, ENIG 14.76, colour 6.91) + Standard PCBA EUR 165.82 (setup 44.13 for two sides, stencil 14.18, components 32 items 47.42, feeders loading 38.30, SMT 2.31, hand-soldering 3.09, manual assembly 1.80, PCB assembly fixture 14.18, packaging 0.42). **Total EUR 193.54 for 5 assembled D5 boards.** Build time PCB 3 days + assembly 5 to 6 days (faster options offered at +42.53 / +85.04, not taken). Weight 618 g. Note for the owner: the single bottom-side part (R36, a 10k 0603) is what makes this a two-sided assembly (second setup, fixture); moving R36 to the top in Rev A2 would cut roughly EUR 35 to 40 per run.
- Product Description: Development Board, HS Code 847330 (same as E1). Assembly remark: "MeshSat PCB-D APRS Rev A. Please confirm orientation in DFM: U5 (LQFP-48) pin 1 top-left per silkscreen; U1 (VQFN) pin 1 per silkscreen; J_HARN1 (2x8 box header) is VERTICAL, key notch to the west edge, pin 1 top-left. L1 not placed (customer fits it)."
- Cart lines: pcb-d-aprs-gerbers_Y4, PCB prototype Y4-11651261A (Black, 1.6, ENIG) 5 pcs EUR 27.71, 3 days; Standard PCBA SMT026090360173-116... assemble both sides 5 pcs EUR 165.82, 5 to 6 days. Screenshots: PCB-D-APRS-D5/jlcpcb-placement-preview-top-2026-09-03.jpg, jlcpcb-cart-added-2026-09-03.jpg. Not paid.

### PCB-C-DISPLAY-C3 (control panel), PCB options and part matching, 3 Sep 2026

- Gerber upload: site detected "2 layer board of 311x442mm" (notes 442.1 x 311.1, 2 layers). Match. A "Large Size" fee applies (EUR 55.25 before, 59.05 with assembly).
- PCB options as set: FR-4, 2 layers, qty 5, 2.0 mm, Black, White silk, FR4 TG135, ENIG 1 U", 1 oz, tented vias, 0.3 mm min via, +-0.2 mm outline, Mark on PCB = Remove Mark, flying probe, no gold fingers, no castellations, no edge plating, no blind slots, no UL, no humidity card. "Change Black to Green" prompt (2 layer / 2.0 mm / Black / ENIG) answered "No, thanks" twice. PCB-only price EUR 187.85 (engineering 28.49, large size 55.25, ENIG 27.88, board 76.23).
- Assembly: Standard (Economic greyed out), BOTH sides (18 top, 70 bottom per the CPL), qty 5, edge rails Added by JLCPCB (production size 442 x 321 mm), confirm placement No, self-service parts, no extras. Assembly accepted at this size.
- BOM + CPL uploaded (top-level). Site: 40 lines, 16 auto-confirmed, 1 shortage, 23 unmatched. **The generator's LCSC codes on this board contain five wrong-package or wrong-part codes** (all corrected by value and package, see table; design session to fix the source): FB1..FB4 C1017 is an 0805 ferrite on an 0603 footprint; R10 C25118 is an 0402 47R; R16..R27 C25270 is an 0805 180R; R29 C11702 is an 0402 1k; D17 C2166 is a 5 mm THT LED, not a BAT54.

| Ref | BOM line | Chosen LCSC | Part | Why |
|---|---|---|---|---|
| FB1..FB4 | ferrite 600R 0603 | C1002 | GZ1608D601TF 600R@100MHz 0603, Basic | BOM code C1017 is the 0805 version |
| R10 | 47R 0603 | C23182 | 0603WAF470JT5E, Basic | BOM code C25118 is 0402 |
| R16..R27 (11 pcs) | 180R 0603 | C22828 | 0603WAF1800T5E, Extended | BOM code C25270 is 0805; no Basic 180R 0603 listed |
| R29 | 1k 0603 | C21190 | 0603WAF1001T5E, Basic | BOM code C11702 is 0402 |
| D17 | BAT54 SOD-123 | C915628 | BAT54W SOD-123, Extended, stock 11396 | BOM code C2166 is a THT LED (10 short anyway) |
| D1, D3, D4 | 3 mm red, sunlight viewable | C90771 (site code for 204-10SURD/S530-A3-L) | Everlight 204-10SURD/S530-A3-L 3 mm super red 624 nm, 25 mA, Extended, stock ~49500 | brightest 3 mm red in stock |
| D5..D9, D13..D16 (9 pcs) | 3 mm green | C2927624 | Everlight 204-10SUGC/S400-A5 3 mm emerald green 525 nm, 3.2 cd typ, Extended, stock 38122 | brightest 3 mm green in stock |
| D2, D12 | 3 mm amber | C282137 | Everlight 204-10UYT/S530-A3 3 mm yellow 589 nm, 500 mcd, Extended, stock 5104 | brightest 3 mm yellow in stock (JLC has no "amber" 3 mm; 589 nm is the amber-yellow used for CAUTION lamps) |
| D10, D11 | 3 mm white | NONE, left unmatched (D10) / matched by mistake then un-ticked (D11) | | JLC's parts search returned no 3 mm through-hole white LED under any query tried ("LED 3mm white plugin", "3mm white", "White" + LED filters, package filter D=3mm); LEFT UNFITTED, bench-fit two 3 mm white LEDs. NOTE: D11 shows PCA9555PWR in the table because a search modal opened on the wrong row after the list re-flowed; the line is UN-TICKED (qty 0) so nothing is placed there, and U1/U2 qty is back to 10. If the site re-ticks it on re-processing, un-tick again |
| J_EPD | pin header 1x8 2.54 vertical | C32713274 | HX PZ2.54-1x8P ZZ straight, Extended, stock 28559 | value/footprint match |
| J_PANEL | IDC 2x10 2.54 vertical (bottom side) | C18202145 | XDFH-0254-2*10P shrouded box header, THT, Extended, stock 1689 | same family as D5's 2x8 |
| J_PIJ2, J_X1202SW | JST XH 2P | C265283 | JST B2B-XH-A-GU, Extended | as on E1 |
| U1, U2 | PCA9555PW TSSOP-24 (BOM code C50993 not recognised by the site) | C2864778 | TI PCA9555PWR, Extended, stock 15582, EUR 0.79 each | genuine TI; NXP PCA9555PW,118 (C128392) costs EUR 1.33; XL9555 clone not taken |
| Q1 | AO3401A | C15127 (BOM) | Basic | as given |
| Q2..Q4 | 2N7002 | C8545 (BOM) | Basic | as given |
| U5..U8 | USBLC6-2SC6 | C7519 (BOM) | Extended | as given |
| C, R (other lines) | as BOM | as BOM | Basic | as given |
- BZ1: C96093, TMB12A05 12 mm 5 V active buzzer 85 dB, 9.8 mm high, 7.6 mm pitch, Extended, stock 133971 (value/footprint match).
- Result: 38 of 40 lines placed; D10 unmatched and D11 un-ticked (the two white LEDs, bench-fit). "Project has unselected parts" answered "Do not place".
- Placement preview (top and bottom, 3D): the 11-LED column on the top side renders with the LED bodies in place; the buzzer and the seven switch pad sets read correctly. Bottom side: **J_PANEL (2x10 box header, C18202145) renders with its shroud body extending beyond the west board edge**, pads on the board; KiCad has the header horizontal and fully inside the outline (bottom mirrored drawing, pin 1 bottom-left, key notch south). Same box-header family as D5's J_HARN1, so treat as the same rotation/origin problem. The SMD cluster (U1, U2 TSSOP-24; U5..U8 SOT-23-6; D17; FB; R; C) is too small at this board size for the viewer's maximum zoom to show pin-1 marks; **not verified**, listed for the DFM check and for the design session's rotation fix (TSSOP is in the same JLC rotation class as SOIC/LQFP).
- Quote step: PCB EUR 194.50 (engineering 28.49, large size 59.05, ENIG 28.32, board 78.65) + Standard PCBA EUR 174.38 (setup 44.13, stencil 7.09, large size 49.61, components 25 items 25.53, feeders loading 23.78, SMT 1.85, hand-soldering 3.09, manual assembly 4.67, fixture 14.18, packaging 0.46). **Total EUR 368.88 for 5 assembled C3 panels.** Build time PCB 24 h + assembly 4 to 5 days. Weight 7.06 kg (shipping will be significant).
- Product Description: Development Board, HS Code 847330. Assembly remark: "MeshSat PCB-C CONTROL PANEL Rev A. Please confirm in DFM: U1/U2 (TSSOP-24) pin 1 per silkscreen; J_PANEL (2x10 box header, bottom side) horizontal, key notch per silkscreen; LED cathodes per silkscreen flat. D10, D11 not placed (customer fits)."
- Cart lines: pcb-c-display-gerbers_Y5, PCB prototype Y5-11651261A (Black, 2.0, ENIG) 5 pcs EUR 194.50, 24 hours; Standard PCBA SMT026090360217-116... assemble both sides 5 pcs EUR 174.38, 4 to 5 days. Screenshots: PCB-C-DISPLAY-C3/jlcpcb-placement-preview-top-2026-09-03.jpg, -bottom-, jlcpcb-cart-added-2026-09-03.jpg. Not paid.

### PCB-B-COMPUTE-B10, PCB options and part matching, 3 Sep 2026

- Gerber upload: site detected "4 layer board of 170x245mm" (notes 245.1 x 170.1, 4 layers). Match. Inner layers present.
- PCB options as set: FR-4, 4 layers, qty 5, 1.6 mm, Black (colour fee 6.91), White silk, FR4 TG135, ENIG 1 U", outer 1 oz, inner 0.5 oz (default), Specify Layer Sequence No, Specify Stackup No (default = JLC04161H-7628), **impedance control NOT ordered** (the notes ask to have JLC tune the USB pairs for 90 ohm on the 7628 stackup; the session brief says only if the owner wants the extra cost, so left at the default, owner to decide; USB 2.0 full/high speed on a few cm of 0.2/0.15 mm pairs works in practice), plugged vias (default), 0.3 mm min via, +-0.2 mm outline, Remove Mark, flying probe, no gold fingers, castellations, press-fit, edge plating, blind slots, UL, backdrill, humidity card. PCB-only price EUR 68.89 (engineering 21.58, ENIG 18.39, colour 6.91, board 22.01).
- Assembly: Standard (Economic greyed out), BOTH sides (J_AB1 on the bottom), qty 5, edge rails Added by JLCPCB (production size 245 x 180 mm), confirm placement No, self-service parts, no extras.
- BOM + CPL uploaded (top-level). Site: 41 lines, 23 auto-confirmed, 1 shortage, 17 unmatched. **Two more wrong generator codes:** U5/U8/U11/U14/U16/U19 "INA219AIDCN" carried C138024 = a 0402 25.5 ohm resistor; U20 "PCA9555PW" carried C5626 = 74HC245PW (TSSOP-20). Both replaced. (C5626 is also on A15's BOM for the same part, to be corrected there too.) LED2 "amber hub" auto-matched to a RED 0603 (C965799), replaced.

| Ref | BOM line | Chosen LCSC | Part | Why |
|---|---|---|---|---|
| C1, C2 | 100u 10V 1206 | C312983 (site auto) | Murata GRM31CR61A107ME05L 100 uF 10 V X5R 1206, Extended | matches; EUR 3.01 for 10 |
| C20, C23, C27, C28 | 1n 0603 | C1588 (site auto) | CL10B102KB8NNNC 1 nF 50 V X7R, Basic | ticked (comment-mismatch warning only) |
| D1 | SMBJ5.0A SMB | C19077558 (site auto) | SMBJ5.0A DO-214AA, Extended | exact |
| LED1 | green 0603, BOM C72043 | C12624 | KT-0603G | C72043 short (as on E1/D5) |
| LED2 | amber 0603 | C2287 | KT-0603Y yellow 584 to 596 nm, Extended, stock 30936 | site had auto-picked a red; yellow is the closest 0603 to amber in the KT family |
| R2 | 2.7k 1% (REXT) | C13167 | 0603WAF2701T5E, Basic | site auto-picked an Extended 2.7k |
| R14, R16 | 0.1R 1% 1206 | C2934287 (site auto) | FRL1206FR100TS 100 mR 250 mW, Extended | ticked |
| R18, R21, R22, R24 | 0.05R 1% 1206 | C912751 (site auto) | RLM12FTSMR050 50 mR 500 mW current sense, Extended | ticked |
| F2, F4, F5 | 2 A hold 1812 PPTC | C20812 | SMD1812P200TF16 2 A hold 16 V, Extended, stock 35071 | value/package |
| F3 | 1.1 A hold 1812 PPTC | C20998 | SMD1812P110TF 1.1 A hold, Extended, stock 7273 | value/package |
| F6 | 0.5 A hold 1812 PPTC | C12559 | SMD1812P050TF/30 0.5 A hold 30 V, Extended, stock 82174 | value/package |
| U4, U7 | TPS2065CDBV | C353882 (site auto) | TI TPS2065CDBVR SOT-23-6, Extended | exact, ticked |
| U5..U19 (6) | INA219AIDCN SOT-23-8 | C87469 | TI INA219AIDCNR, Extended, stock 3949, EUR 0.76 each | exact part (BOM code C138024 was a resistor) |
| U10..U18 (4) | TPS22810DRV WSON-6 | C527679 (site auto) | TI TPS22810DRVR, Extended | exact |
| U20 | PCA9555PW | C2864778 | TI PCA9555PWR, Extended | BOM code C5626 is a 74HC245PW |
| U1 | FE1.1s SSOP-28 (BOM C2848 not accepted by the site) | C9359 | FE1.1S-BSOP28BCN SSOP-28 150 mil, Extended, stock 36593 | genuine FE1.1S in the SSOP-28 package; all other SSOP-28 listings out of stock, the QFN24 variant not taken (different package) |
| Y1 | 12 MHz 3225 | C5160137 (selected from the search list by its MPN; the code was first mis-transcribed as C5160127, see the A15 note) | YXC XXHCELNANF-12MHZ 12 MHz 20 pF +-20 ppm SMD3225-4P, Extended, stock 3000 | crystal (not oscillator), 20 pF suits the 22 pF load caps; VERIFY the code in the cart BOM before paying |
| Q1 | 2N7002 | C8545 | Basic | exact |
| J_5V_IN1, J_5V_IN2, J_TD2 | JST XH 2P | C265283 | B2B-XH-A-GU | as before |
| J_DCF77 | JST XH 4P | C144395 | JST B4B-XH-A(LF)(SN), Extended, stock 118556 | exact |
| J_TBEAM1, J_TCALL1, J_XIAO1 | JST PH 4P | C131334 | JST B4B-PH-K-S(LF)(SN), Extended, stock 206282 | exact |
| J_AB1 | IDC 2x7 (bottom) | C19193808 | XDFH-0254-2*7P, Extended, stock 2816 | family |
| J_GPIO1 | IDC 2x20 | C19193815 | XDFH-0254-2*20P, Extended, stock 1986 | family |
| J_PANEL | IDC 2x10 | C18202145 | XDFH-0254-2*10P | as on C3 |
| J_RB9704 | IDC 2x8 | C18202144 | XDFH-0254-2*8P | as on D5 |
| J_RB9603 | Molex PicoBlade 53047-1010 | C505021 | Molex 530471010 1x10 1.25 mm, Extended, stock 7599 | exact (genuine Molex) |
| J_RTL1, J_ZB1 | USB-A Stewart SS-52100-001 | C3197637 | Stewart SS-52100-001 right-angle USB-A receptacle, Extended, stock 116 | exact MPN; stock is thin (116) |
| J_USB_UP1, J_USB_UP2 | USB-C TYPE-C-31-M-12 | C165948 (BOM) | Extended | as given |
| others (C, R, U2.., etc.) | as BOM | as BOM | | as given |

- Result: 41 of 41 lines matched.
- Placement preview, top (3D): **J_GPIO1 (2x20 box header, C19193815) renders HORIZONTAL across the board centre while its pad field is a vertical 2x20 column** (KiCad: vertical). **J_RB9704 (2x8, C18202144) likewise renders with the body at 90 degrees to its pad field** at the north-east. Same box-header rotation/origin defect as D5's J_HARN1 and C3's J_PANEL. The USB-C receptacles (J_USB_UP1/2) sit on the south edge with the opening outward; the two USB-A receptacles (J_RTL1, J_ZB1) at the north edge; the JST XH/PH headers read as keyed housings in their pad outlines. The SSOP-28 hub (U1), the six INA219 (SOT-23-8), the four TPS22810 (WSON-6) and the TSSOP-24 expander (U20) are too small at this zoom to confirm pin 1; they are in the same JLC rotation class as the LQFP/SOIC finding on D5/E1 and are listed for the DFM check and the CPL rotation fix.
- Placement preview, bottom: J_AB1 (2x7) is the only bottom part; its pad field renders on the south edge, no 3D body shown for it in this view.
- Quote step: PCB EUR 70.36 (engineering 21.58, ENIG 18.56, colour 6.91, board 23.31) + Standard PCBA EUR 197.52 (setup 44.13, stencil 7.09, components 39 items 76.27, feeders loading 39.63, SMT 3.10, hand-soldering 3.09, manual assembly 9.60, fixture 14.18, packaging 0.44). **Total EUR 267.88 for 5 assembled B10 boards.** Build time PCB 3 days + assembly 5 to 6 days. Weight 2.58 kg.
- Product Description: Development Board, HS Code 847330. Assembly remark: "MeshSat PCB-B COMPUTE Rev A. Please confirm in DFM: all 2xN box headers (J_GPIO1 2x20, J_RB9704 2x8, J_PANEL 2x10, J_AB1 2x7 bottom) oriented per silkscreen outline and key notch; U1 SSOP-28, U20 TSSOP-24, U5..U19 SOT-23-8 and WSON-6 pin 1 per silkscreen."
- Cart lines: pcb-b-compute-gerbers_Y6, PCB prototype Y6-11651261A (Black, 1.6, ENIG) 5 pcs EUR 70.36, 3 days; Standard PCBA SMT026090360247-11... assemble both sides 5 pcs EUR 197.52, 5 to 6 days. Screenshots: PCB-B-COMPUTE-B10/jlcpcb-placement-preview-top-2026-09-03.jpg, -bottom-, jlcpcb-cart-added-2026-09-03.jpg. Not paid.

### PCB-A-POWER-A15, PCB options and part matching, 3 Sep 2026

- Gerber upload: site detected "4 layer board of 160x285mm" (notes 285.1 x 160.1, 4 layers). Match. Inner layers present.
- PCB options as set: FR-4, 4 layers, qty 5, 1.6 mm, Black (6.91), White silk, FR4 TG135, ENIG 1 U", outer 1 oz, inner 0.5 oz, no layer sequence / stackup specification (default JLC04161H-7628), **impedance control NOT ordered** (same reasoning as B10, owner to decide), plugged vias, 0.3 mm via, +-0.2 mm, Remove Mark, flying probe, all other options No. PCB-only price EUR 71.39 (engineering 21.58, ENIG 18.73, colour 6.91, board 24.17).
- Assembly: Standard (Economic greyed out), TOP side only (J_DOCK spring pins are bench-fitted, so no bottom part remains, as the session brief wanted), qty 5, edge rails Added by JLCPCB (production size 285 x 170 mm), confirm placement No, self-service parts, no extras.
- BOM + CPL uploaded (top-level). Site: 30 lines, 19 auto-confirmed, 11 unmatched. Same generator code errors as B10: U8/U11/U14/U17 "INA219AIDCN" carried C138024 (0402 resistor), U19 "PCA9555PW" carried C5626 (74HC245PW); LED2 auto-matched red. All corrected.

| Ref | BOM line | Chosen LCSC | Part | Why |
|---|---|---|---|---|
| C13 | 100u 10V 1206 | C312983 (site auto) | Murata GRM31CR61A107ME05L, Extended | as on B10 |
| D2 | SMBJ5.0A | C19077558 (site auto) | Extended | exact |
| LED2 | amber 0603 | C2287 | KT-0603Y yellow | as on B10 |
| R19 | 2.7k 1% | C13167 | 0603WAF2701T5E Basic | as on B10 |
| R27, R29, R31, R33 | 0.1R 1% 1206 | C2934287 (site auto) | FRL1206FR100TS, Extended | ticked |
| U5 | AMS1117-3.3 SOT-223 | C6186 (site auto) | AMS1117-3.3, Basic | exact |
| U7, U10, U13, U16 | TPS2065CDBV | C353882 (site auto) | TI TPS2065CDBVR, Extended | exact, ticked |
| U8, U11, U14, U17 | INA219AIDCN | C87469 | TI INA219AIDCNR | BOM code was a resistor |
| U19 | PCA9555PW (0x21) | C2864778 | TI PCA9555PWR | BOM code was a 74HC245PW |
| U6 | FE1.1s SSOP-28 | C9359 | FE1.1S-BSOP28BCN | as on B10 |
| Y1 | 12 MHz 3225 | C5160137 | YXC XXHCELNANF-12MHZ 12 MHz 20 pF | INCIDENT, corrected: the code was first typed as C5160127, which the site resolved to OVETDLJANF-32.768KHZ (a 32.768 kHz 5032 oscillator); caught on the zoom check of the matched row and replaced by the 12 MHz crystal before NEXT. B10 was matched by clicking the MPN row, not by code, and is to be verified in the cart |
| J_AB1 | IDC 2x7 (top) | C19193808 | XDFH-0254-2*7P | as on B10 |
| J_MEZZ1 | IDC 2x8 | C18202144 | XDFH-0254-2*8P | as on D5 |
| J_MEZZ_PWR1 | JST VH 2P | C265357 | B2P-VH-R(LF)(SN) 10 A | as on E1 |
| J_LEDS1 | JST XH 10P | C144400 | JST B10B-XH-A(LF)(SN), Extended, stock 14048 | exact |
| J_X1202DC | JST XH 2P | C265283 | B2B-XH-A-GU | as before |
| J_GPS1, J_WIFI1 | USB-A Stewart SS-52100-001 | C3197637 | exact MPN, stock 116 (shared with B10's two: 20 pcs needed across both boards against 116 in stock) | |
| J_PACK, J_X1202BAT | AMASS XT60-M vertical | C98733 | Amass XT60-M. male plug, 3.5 mm banana, Extended, stock 10905 | the cable-type XT60 male the KiCad AMASS_XT60-M vertical footprint is drawn for; XT60PW-M (horizontal PCB plug) not taken, different footprint |
| others (C, R, U9.., etc.) | as BOM | as BOM | | as given |

- Result: 30 of 30 lines matched.
- Placement preview, top (3D): **J_AB1 (2x7 box header, C19193808) renders HORIZONTAL while its pad field is a vertical 2x7 column**, the same box-header rotation defect as on D5, C3 and B10. The two XT60 (J_PACK, J_X1202BAT) render as upright orange plug bodies on the west side of the hub region. USB-A (J_GPS1, J_WIFI1) at the north edge, the 10-pin XH (J_LEDS1) and the VH (J_MEZZ_PWR1) read as keyed housings. SSOP-28 hub (U6), TSSOP-24 expander (U19), SOT-23-8 INA219 too small to confirm pin 1; same class as the D5/E1 finding.
- Quote step: PCB EUR 73.12 (engineering 21.58, ENIG 18.99, colour 6.91, board 25.64) + Standard PCBA EUR 120.71 (setup 22.07 single side, stencil 7.09, components 28 items 53.90, feeders loading 27.74, SMT 2.11, hand-soldering 3.09, manual assembly 4.27, packaging 0.44). **Total EUR 193.83 for 5 assembled A15 boards.** Build time PCB 3 days + assembly 5 to 6 days. Weight 2.81 kg.
- Product Description: Development Board, HS Code 847330. Assembly remark: "MeshSat PCB-A POWER Rev A. Please confirm in DFM: J_AB1 (2x7 box header) and J_MEZZ1 (2x8) oriented per silkscreen outline and key notch; U6 SSOP-28, U19 TSSOP-24, U8..U17 SOT-23-8 pin 1 per silkscreen; XT60 (J_PACK, J_X1202BAT) polarity per silkscreen + and -."
- Cart lines: pcb-a-power-gerbers_Y7, PCB prototype Y7-11651261A (Black, 1.6, ENIG) 5 pcs EUR 73.12, 3 days; Standard PCBA SMT026090360270-11651261A assemble top side 5 pcs EUR 120.71, 5 to 6 days. Screenshots: PCB-A-POWER-A15/jlcpcb-placement-preview-top-2026-09-03.jpg, jlcpcb-cart-added-2026-09-03.jpg. Not paid.

## 3. Cart state at the end of the session, 3 Sep 2026 ~04:06 CEST (screenshot cart-all-six-boards-2026-09-03.jpg)

All six boards are in the JLCPCB cart of the owner's account, 11 lines, nothing selected, nothing paid. Prices in EUR as the site shows them (its display currency switched itself to EUR after the first save; E2 was quoted at USD 57.50 and now shows EUR 49.64).

| Board | PCB line | PCB EUR | PCBA line | PCBA EUR | Board total EUR |
|---|---|---|---|---|---|
| A15 POWER | Y7-11651261A, 3 days | 73.12 | SMT026090360270-11651261A, top side, 5 to 6 days | 120.71 | 193.83 |
| B10 COMPUTE | Y6-11651261A, 3 days | 70.36 | SMT026090360247-11651261A, both sides, 5 to 6 days | 197.52 | 267.88 |
| C3 CONTROL PANEL | Y5-11651261A, 24 h | 194.50 | SMT026090360217-11651261A, both sides, 4 to 5 days | 174.38 | 368.88 |
| D5 APRS | Y4-11651261A, 3 days | 27.71 | SMT026090360173-11651261A, both sides, 5 to 6 days | 165.82 | 193.53 |
| E1 DOCK | Y3-11651261A, 24 h | 26.68 | SMT026090360135-11651261A, top side, 4 to 5 days | 54.10 | 80.78 |
| E2 RF JUNCTION | Y2-11651261A, 3 days | 49.64 | none (bare board) | 0 | 49.64 |
| **Sum** | | **442.01** | | **712.53** | **1154.54** |

Sum excludes shipping (FedEx Express was estimated at EUR 25.52 for a single small board; the C3 panel alone weighs 7 kg, so expect a much higher figure at checkout), import VAT/duties into NL, and any JLC coupons (two were offered on the quote page: "Save EUR 30.22" and "Save EUR 25.90"; not applied, coupons are applied at checkout by the owner). Every line is qty 5.

### 3.1 Parts left unfitted (bench-fit)
- D5 L1: Coilcraft XAL6030-152MEB 1.5 uH, no JLC equivalent in that footprint.
- C3 D10, D11: 3 mm white LEDs, none found in JLC's THT LED stock.
- All bench-fit items from ORDER-NOTES / ASSEMBLY.md section 9 were excluded from the BOMs by the design session (J_DOCK on A15, the seven switches and EPD1 on C3, U1/F1/J_DOCK on E1) and are not in the JLC quotes.

### 3.2 Stop items for the owner before paying (in order of consequence)
1. **CPL rotations for JLC.** JLC's placement preview shows every 2xN shrouded box header rotated 90 degrees to its pad field (D5 J_HARN1, C3 J_PANEL, B10 J_GPIO1 + J_RB9704, A15 J_AB1), a pin-1 corner mismatch on the LQFP-48 (D5 U5) and the SOIC-8 (E1 Q1), and the small SSOP/TSSOP/SOT-23-8/WSON/QFN parts could not be checked at the viewer's zoom. This is the usual KiCad-to-JLC rotation-origin difference; the exporter (`make_handoff.py` / `export_jlc.sh`) should apply JLC's rotation table and the CPLs be re-uploaded (Edit Order on each PCBA line, or re-create the assembly), OR the parts get rotated in JLC's placement editor and re-checked. JLC's DFM after payment may query some of these, but production is not guaranteed to stop for them. Remarks asking JLC to confirm orientation are on every assembled line.
2. **Generator LCSC codes.** Seven wrong codes were found and worked around on the site; the source BOMs still carry them: E1 D2 (C8074 = 24 V MiniMELF for a 12 V SOD-123), C3 FB1..4 (C1017 = 0805), C3 R10 (C25118 = 0402), C3 R16..27 (C25270 = 0805), C3 R29 (C11702 = 0402), C3 D17 (C2166 = a THT LED for a BAT54), B10/A15 U5.. / U8.. INA219 (C138024 = 0402 resistor), B10 U20 / A15 U19 PCA9555 (C5626 = 74HC245PW), plus C3 U1/U2 C50993 not recognised. Fix in the generators before any re-export, otherwise the same lines mis-match again.
3. **E1 Q1 Vds rating.** The BOM names AO4409 "-60 V 4 A"; the real AO4409 is -30 V. The shore input is 9 to 36 V. Design review item.
4. **Impedance control** not ordered on A15/B10 (USB pairs). Owner decision, extra cost if wanted; re-quote via Edit Order.
5. **Two-sided assembly on D5 exists only because of R36** (one 10k on the bottom): about EUR 35 to 40 per run.
6. **Product Description** on all five PCBA lines is "Development Board, HS 847330" (customs). Change via Edit Order if another classification is preferred.
7. B10 Y1 verified in the cart as XXHCELNANF-12MHZ C5160137 (3.4); A15 corrected on the page. Closed.
8. Stock-thin parts: Stewart SS-52100-001 USB-A (116 in stock, 20 needed), TPS61089RNRR (2644), B4B-XH-A-GU... fine. Order soon or re-check stock at payment.

### 3.3 What the owner does next
- Sat 12 Sep: design review with Nick (agenda = the six order-gate items in Review/README.md plus the items in 3.2).
- If "order now": in the cart, tick all 11 lines, Secure Checkout, address + shipping + coupons + payment. Then post the order numbers on MESHSAT-709 and append them to each ORDER-NOTES.txt (step 5 of the method, still open).
- 4 to 6 hours after paying: check the DFM analysis in Order History for every PCBA line (rotation confirmations from the remarks).

### 3.4 Post-save verification, 3 Sep 2026 ~04:08
- B10 PCBA line, Product Details > Bill of Material (39 selected items): Y1 = XXHCELNANF-12MHZ, C5160137 (correct 12 MHz crystal). Item 7 of 3.2 is closed for B10; A15 was corrected on the page before saving (C5160137 on its Y1 row).
- Same dialog also confirms on B10: U20 PCA9555PWR C2864778, U5..U19 INA219AIDCNR C87469, U1 FE1.1S-BSOP28BCN C9359, LED2 KT-0603Y C2287, R2 0603WAF2701T5E C13167, F2/F4/F5 C20812, F3 C20998, F6 C12559, all connectors as logged.
- Session closed with the cart untouched beyond the saves above: no line ticked, no checkout opened, no payment.

### 3.5 Coupons, checked 3 Sep 2026 (jlcpcb.com/coupon-center)
- Rule on the page: "Each coupon collected can only be used once. Only one coupon can be applied to any order." So one coupon per checkout, whatever the cart holds.
- Web-order coupons that fit this cart: "PCBA Special Offer" USD 9 (orders over USD 1, valid until 29 Sep 2026) and USD 6 (same terms); "Stencil Coupon" USD 5 (only if a stencil is ordered as a separate line, ours are inside the PCBA lines). Not applicable: the EasyEDA USD 10 pair (EasyEDA designs only), "6-Layer PCB Special" USD 20 (our boards are 2 and 4 layer), parts/CNC/3DP/MC coupons.
- JLCONE desktop-app coupons (the same account cart, ordered through JLC's desktop client instead of the browser): "JLCONE Batch PCBA" USD 30 (orders over USD 1000, ours qualifies), "JLCONE Batch PCB" USD 15 (over USD 1000), "JLCONE PCBA" USD 20 (over USD 100), "JLCONE 4-Layer PCB" USD 5, "JLCONE PCB" USD 5, plus the app's advertised "random USD 1 to 20 off every order" and "USD 104 first-download coupons" (unverified, app marketing).
- The quote page had shown two coupons already on the account, "Save EUR 30.22" and "Save EUR 25.90" (about USD 35 and USD 30); their terms could not be read because jlcpcb.com's "My Coupons" page needs the main-site sign-in, which this browser tab no longer has (cart.jlcpcb.com is still signed in). Owner to sign in and read them; nothing was claimed by this session.
- Realistic saving on a single combined order: one coupon, EUR 25 to 30. Splitting the cart into several orders allows one coupon each but each coupon type only once and shipping is charged per order, so it is unlikely to beat one Batch PCBA coupon on one combined order.

## 4. Second pass, 3 Sep 2026 from 10:00 CEST: rotation fix, LCSC-coded BOMs, both free confirmations (owner instruction: do not count on the 12 Sep review, switch on Confirm Production File and Confirm Parts Placement)

Method: `JLCPCB/jlc_final.py` builds, per board, `final/*-bom-final.csv` (the top-level BOM with the LCSC codes chosen in section 2 filled in; blank for the bench-fit lines L1, D10, D11) and `final/*-cpl-jlc.csv` (the top-level CPL with the rotation offsets of `JLCPCB/jlc-rotations.csv` added). Offsets, derived from JLCPCB's own placement preview: IDC-Header_2xN +90; SOIC-8, SSOP-28, TSSOP-24, LQFP-48, Texas VQFN, WSON-6 +270. Everything else 0 (SOT-23 family, diodes, JST, XT60, USB, crystals were consistent with KiCad in the first-pass previews). The KiCad projects and the ECAD generators were not touched; the design session should carry the same table into `make_handoff.py`.

Site flow that works: cart > PCB line > Edit Order reopens the quote with the assembly attached and the part matching intact; "Confirm Production file = Yes" and "Confirm Parts Placement = Yes" each open a dialog with a "Do not confirm automatically" box, which was TICKED (production waits for the owner's explicit approval instead of auto-starting after 48 h / 72 h). Bill of Materials > "Upload BOM/CPL" replaces both files; with the LCSC column filled the site confirms every line instantly.

### E1 (rebuilt 10:03 to 10:06)
- Confirm Production file Yes (+EUR 0.90), Confirm Parts Placement Yes (+EUR 0.39), both with "do not confirm automatically".
- Uploaded final/pcb-e1-dock-bom-final.csv + final/pcb-e1-dock-cpl-jlc.csv: 12 of 12 confirmed at once, same parts as section 2.
- Placement preview after the fix: **Q1 (SOIC-8) pin-1 dot now TOP-left, matching KiCad**; D1, D2, D3 cathode left as before. The +270 offset for SOIC is confirmed by the preview.
- Quote: PCB 27.53 + PCBA 54.40 = **EUR 81.92** (was 80.78; the two confirmations add 1.29, small rounding on the rest). Description Development Board 847330; remark re-entered.

### D5 (rebuilt 10:07 to 10:25): offsets verified part by part
- Both confirmations on with "do not confirm automatically".
- Method that finally worked: JLCPCB's 2D view (not 3D), zoomed with the mouse over the canvas (hover, then wheel). It draws KiCad's silkscreen pin-1 triangle (from the gerbers) next to JLC's own pin-1 mark (pink), so both are in one image. The 3D view orbits on drag and loses zoom on toggles; not reliable for this.
- First guess table was wrong for two families (owner spotted it): SOT-23 needed 180 and SOT-23-5/6 needed 270, not 0; the VQFN needed 0, not 270.
- Verified on D5 after three uploads (jlc-rotations.csv is the record): SOIC-8 270 (E1 Q1), LQFP-48 270 (U5), Texas VQFN 0 (U1), SOT-23 180 (Q1..Q4), SOT-23-5 and SOT-23-6 270 (U3, U4, U6), LED_0603 180 (D1, D2: pink mark on the cathode end), IDC box header 270 (key side: at 90 the JLC body's key sat on the side opposite KiCad's silk notch). Diodes SOD-123/SMB/SMC 0 (E1). Unverified so far, applied from the same family logic: SOT-23-8 270, SSOP-28/TSSOP-24 270, WSON-6 270, SOT-223 180, USB-C 180 (checked on the boards that carry them, below).
- Reload trap: re-opening the BOM page re-runs the duplicate-part check and unticks 12 lines; they must be re-ticked in the same sitting before NEXT (done by script), and L1 must be unticked again (the LCSC-less line auto-matches to a 0603 inductor every time).
- D5 quote after the rebuild: PCB 28.56 (incl. Confirm Production file 0.90) + PCBA 165.93 (incl. Confirm Parts Placement 0.39) = EUR 194.49. JLC lists the assembly remark under "Advanced Options, quote after review" (no cost shown; the remark is informational only).
- D5 cart lines after the rebuild: pcb-d-aprs-gerbers_Y9, PCB Y9-11651261A EUR 28.56 (3 days); Standard PCBA SMT026090361211-11651261A both sides EUR 165.93 (5 to 6 days). Old Y4 lines replaced. Remark: "MeshSat PCB-D APRS Rev A. Orientation per silkscreen pin-1 marks. L1 not placed (customer fits). Please flag any doubt in the placement confirmation."

### C3 (rebuilt 10:27 to 10:32)
- Both confirmations on with "do not confirm automatically". final BOM + CPL uploaded (offsets: J_PANEL IDC 90->0, U1/U2 TSSOP-24 +270, Q1..Q4 SOT-23 +180, U5..U8 SOT-23-6 +270); 38 lines matched, D10/D11 unmatched and "Do not place". 18 duplicate-part lines re-ticked by script.
- Preview: at 442 x 311 mm the viewer's maximum zoom leaves the bottom-side SMD cluster at about 20 px per TSSOP, too small to read the marks; the package classes are the ones verified on D5 (SOT-23, SOT-23-6, SOD-123) and B10 (TSSOP/SSOP, checked next). J_PANEL now horizontal (as in KiCad) at the west edge in the bottom view. **Design note for the review: the J_PANEL shroud outline extends about 3.5 mm beyond the board edge in JLC's render (header centred 13 mm from the edge with a 33 mm shroud)**; check against the frame's 10.9 mm bearing ring in the appendix.
- Quote: PCB 195.06 + PCBA 174.45 = EUR 369.52 (was 368.88; confirmations +1.29, rounding on the rest).
- C3 cart lines after the rebuild: pcb-c-display-gerbers_Y10, PCB Y10-11651261A EUR 195.06 (24 h); Standard PCBA SMT026090361227-11651261A both sides EUR 174.45 (4 to 5 days). Old Y5 lines replaced.

### B10 (rebuilt 10:32 to 10:38)
- Both confirmations on with "do not confirm automatically". final BOM + CPL uploaded (29 rotated lines: the four box headers, USB-C x2 180, LEDs 180, SOT-23/SOT-23-6/SOT-23-8, SSOP-28, TSSOP-24, WSON-6). 5 duplicate-part lines re-ticked by script.
- On re-upload the site swapped U1 to FE1.1S-BSOP28BPTR C6706491 (out of stock, "5 shortfall") although the BOM carries C9359; re-selected C9359 (FE1.1S-BSOP28BCN, 33658 in stock) by hand. Watch for this again if the assembly is ever rebuilt.
- Preview (2D): J_GPIO1 (2x20) vertical over its vertical pad column, J_RB9704 (2x8) horizontal over its horizontal pads, J_PANEL (2x10) horizontal at the south edge, all three now consistent with KiCad (the first pass had every one 90 degrees off). The 0.65 mm-pitch ICs and SOT-23-8 are below the crop resolution at 245 x 170 mm; they follow the D5-verified families (SOIC/LQFP 270 -> SSOP/TSSOP 270; SOT-23-5/6 270 -> SOT-23-8 270). USB-C 180, 3225 crystal 0 and the keyed JST/PicoBlade/USB-A housings 0 are unverified in the viewer and rely on JLC's parts-placement confirmation images before soldering.
- B10 quote after the rebuild: PCB 71.13 + PCBA 197.57 = EUR 268.70 (was 267.88). Remark: "MeshSat PCB-B COMPUTE Rev A. Orientation per silkscreen pin-1 marks and key notches (J_GPIO1 2x20, J_RB9704 2x8, J_PANEL 2x10, J_AB1 2x7 bottom). Please flag any doubt in the placement confirmation."
- B10 cart lines after the rebuild: pcb-b-compute-gerbers_Y11, PCB Y11-11651261A EUR 71.13 (3 days); Standard PCBA SMT026090361254-11651261A both sides EUR 197.57 (5 to 6 days). Old Y6 lines replaced.

### A15 (rebuilt 10:38 to 10:43)
- Both confirmations on with "do not confirm automatically". final BOM + CPL uploaded (18 rotated lines: J_AB1 90->0 and J_MEZZ1 0->270 for the box headers, LED2 180, U5 SOT-223 180, U6 SSOP-28 270, U19 TSSOP-24 270, the SOT-23-6 and SOT-23-8 lines 270). 4 duplicate-part lines re-ticked by script. Same U6 FE1.1S swap to the out-of-stock C6706491 as on B10; re-selected C9359 by hand.
- Preview (2D): J_AB1 (2x7) vertical over its vertical pad column (first pass had it horizontal); the XT60s upright on the west side of the hub region.
- A15 preview at zoom (2D): U6 SSOP-28 (270) and U19 TSSOP-24 (270) show JLC's pin-1 mark on the silk-triangle corner; U7 SOT-23-6 (270), U8 SOT-23-8 (270) and U9 SOT-23-6 (270) likewise. That closes the SSOP/TSSOP/SOT-23-8 families that were only inferred on B10 and C3.
- A15 quote after the rebuild: PCB 73.89 + PCBA 120.88 = EUR 194.77 (was 193.83). Remark: "MeshSat PCB-A POWER Rev A. Orientation per silkscreen pin-1 marks and key notches (J_AB1 2x7, J_MEZZ1 2x8); XT60 polarity per silkscreen. Please flag any doubt in the placement confirmation."
- A15 saved to cart 10:47 as pcb-a-power-gerbers_Y12: PCB Y12-11651261A EUR 73.89 (5 pcs, 3 days), PCBA SMT026090361274-11651261A EUR 120.88 (top side, 5 to 6 days). Old A15 lines (Y7) are gone from the cart; Edit Order replaced them.

E1 (second re-upload 10:45 to 10:50)
- Reason: jlc-rotations.csv gained LED_0603 180 after E1's rebuild, so E1's LED1 was still uploaded at 0. Re-opened Y8 with Edit Order (all options intact: black, ENIG, both confirmations, assembly remark), re-uploaded final/pcb-e1-dock-bom-final.csv and final/pcb-e1-dock-cpl-jlc.csv (LED1 180, Q1 270). 12 of 12 lines confirmed with the same LCSC parts as before, no swaps this time.
- Preview (2D, zoomed): Q1 pin-1 mark top-left on the silk pin-1 corner (as verified in the first rebuild); LED1 now shows the same JLC mark pattern as D5 D1/D2 (LED_0603 at 180, verified on D5); C2/R1/R2 unpolarised.
- E1 quote unchanged at PCB 27.53 + PCBA 54.40 = EUR 81.92. Remark: "MeshSat PCB-E1 DOCK Rev A. Polarity per silkscreen: Q1 SOIC-8 pin 1 top-left, LED1 and diode cathode bands as marked. Please flag any doubt in the placement confirmation." Saved to cart 10:50 as pcb-e1-dock-gerbers_Y13: PCB Y13-11651261A EUR 27.53 (5 pcs, 24 h), PCBA SMT026090361312-11651261A EUR 54.40 (top side, 4 to 5 days). Y8 lines replaced.

E2 (bare board, edited 10:51)
- Edit Order on Y2: only change is Confirm Production file = Yes with "Do not confirm automatically" ticked (+EUR 0.90). No assembly on E2, so Confirm Parts Placement does not apply. All other options untouched (black, 2.0 mm, ENIG, 1 oz, tented, 3 days). Quote EUR 49.55 to EUR 50.45.

### 4.1 Cart state after the second pass, 3 Sep 2026 10:52 CEST (no screenshot file this pass; the table below is read from the cart page)

Eleven lines, every one qty 5, nothing ticked, no checkout opened, nothing paid. All five PCBA lines were rebuilt from the `final/` BOM (LCSC coded) and CPL (JLC rotation offsets applied) with Confirm Production File and Confirm Parts Placement on, both with "Do not confirm automatically" ticked, so nothing goes to production until the owner approves the file and the placement in Order History. E2 carries Confirm Production File only.

| Board | PCB line | PCB EUR | PCBA line | PCBA EUR | Board total EUR |
|---|---|---|---|---|---|
| A15 POWER | Y12-11651261A, 3 days | 73.89 | SMT026090361274-11651261A, top side, 5 to 6 days | 120.88 | 194.77 |
| B10 COMPUTE | Y11-11651261A, 3 days | 71.13 | SMT026090361254-11651261A, both sides, 5 to 6 days | 197.57 | 268.70 |
| C3 CONTROL PANEL | Y10-11651261A, 24 h | 195.06 | SMT026090361227-11651261A, both sides, 4 to 5 days | 174.45 | 369.51 |
| D5 APRS | Y9-11651261A, 3 days | 28.56 | SMT026090361211-11651261A, both sides, 5 to 6 days | 165.93 | 194.49 |
| E1 DOCK | Y13-11651261A, 24 h | 27.53 | SMT026090361312-11651261A, top side, 4 to 5 days | 54.40 | 81.93 |
| E2 RF JUNCTION | Y2-11651261A, 3 days | 50.45 | none (bare board) | 0 | 50.45 |
| **Sum** | | **446.62** | | **713.23** | **1159.85** |

Change against section 3: +EUR 5.31, which is the two confirmations on every line (6 x 0.90 + 5 x 0.39 = 7.35) less small component-price movements on the re-match. Shipping, import VAT and coupons still excluded, as in section 3.

Old lines Y3 to Y8 no longer exist; Edit Order replaced them. The screenshots in section 3 show the old Y numbers.

### 4.2 Rotation table status (jlc-rotations.csv)

Verified in JLC's 2D placement view against KiCad's silkscreen pin-1 marks: SOIC-8 270 (E1 Q1), SSOP-28 270 (A15 U6), TSSOP-24 270 (A15 U19), LQFP-48 270 (D5 U5), Texas VQFN 0 (D5 U1), SOT-23 180 (D5 Q1 to Q4), SOT-23-5/6/8 270 (D5 U3 U4 U6, A15 U7 U8 U9), LED_0603 180 (D5 D1 D2, E1 LED1 same pattern), IDC 2xN 270 (box headers aligned with their pad fields on D5, B10, A15; key side inferred from the pad-1 square).

Not verifiable at the viewer's zoom, left at the table value or 0 and covered by Confirm Parts Placement: WSON-6 270, SOT-223 180, USB-C receptacle 180, crystal 3225 0, JST XH/VH/PicoBlade 0, XT60 0, USB-A 0. These are the ones to look at first when JLC's parts-placement confirmation request arrives.

### 4.3 Still open for the owner (unchanged from 3.2 unless noted)
- 3.2 item 1 (CPL rotations) is now handled on the site for every polarised SMD family listed in 4.2; the source exporter still emits KiCad rotations, so the offsets in jlc-rotations.csv should go into make_handoff.py before any re-export (design session).
- 3.2 item 2 (generator LCSC codes) unchanged: the `final/` BOMs carry the corrected codes, the generators do not.
- 3.2 items 3 to 8 unchanged.
- FE1.1S trap: on every re-upload the site replaced C9359 (in stock) with C6706491 (out of stock) on B10 U1 and A15 U6; both were put back by hand and the cart lines show C9359. Anyone who re-uploads must re-check that row.
- Fewer than 5 assembled boards: the PCBA qty field on the assembly step accepts 2 to 5, so 5 bare PCBs with 2 or 3 assembled is possible via Edit Order. PCB qty cannot go below 5.

## Design session update, 3 Sep 2026 14:55: PCB-C is now C4, plus a new tiny board

- PCB-C C3 is superseded by C4 (owner request): the WeAct 3.7 e-paper module now hangs under the panel with its glass in a recessed 94.19 x 53.6 mm window (no standoffs), the MeshSat logo is on the face silk, two ring resistors moved beside their switches. Routed 0 hard / 0 open, 226 vias. Discard the C3 cart and re-upload from JLCPCB/PCB-C-DISPLAY-C4/ (regenerated gerbers, BOM, CPL, ORDER-NOTES; EPD1 is no longer a part). The C3 folder is deleted.
- New bare board PCB-C-RING-R1 (JLCPCB/PCB-C-RING-R1/): 1.0 mm FR-4 spacer frame, no copper, black, 5 pcs, no assembly. Same batch.
- The handoff folders are being rebuilt now (a few minutes); wait for JLCPCB/PCB-C-DISPLAY-C4/ORDER-NOTES.txt to exist before reading.

## Design session update, 3 Sep 2026 15:20: PCB-A is now A16, E1 regenerated

- Owner rulings on audit round 8: two fuses on the pack node (F1 15 A mini blade to the X1202 lead, F2 10 A mini blade to the 8 V boost feed, both in Keystone 3568 holders, JLC-fitted holders, fuses bench-fitted) and a shore charge inhibit: spring pin 8 is now SHORE_INHIBIT (was GND), driven by the expander, and on E1 an EL817 / PC817 optocoupler (U2, SOP-4) with R3 330R and R4 100k switches the Traco remote pin. A16 routed 0 hard / 0 open, 219 vias. E1 re-spun with the opto, 0 hard / 0 open, 19 vias, same deliverable name.
- Discard the A15 cart and any E1 cart made before 15:15; re-upload from JLCPCB/PCB-A-POWER-A16/ and JLCPCB/PCB-E1-DOCK-E1/ once the handoff rebuild finishes (ORDER-NOTES.txt timestamps after 15:20). A15 folders are deleted.
- Unchanged: B10, C4, C-RING-R1, D5, E2.
- 15:30 correction: the A16 files exported at 15:16 had a bar defect; valid A16 files carry ORDER-NOTES timestamps after 15:35. E1 files from 15:15 stand.

## 5. Third pass, 3 Sep 2026 from 16:20 CEST: A16, C4, E1 (opto) re-uploaded, C-RING-R1 added (owner instruction 16:15)

Inputs checked first: all seven ORDER-NOTES.txt carry 16:05 to 16:15 timestamps (A16 16:05, B10 16:06, C4 16:08, R1 16:10, D5 16:11, E1 16:13, E2 16:15), so every folder is the post-15:35 export. Zips: A16, B10, D5 carry In1_Cu.g1 + In2_Cu.g2; C4, R1, E1, E2 carry F_Cu/B_Cu only. Matches the README layer counts. B10 and D5: the regenerated BOM and CPL are identical to the copies uploaded this morning (designators, footprints, rotations), so their carts stand as the owner ruled; the regenerated zips could not be compared to the uploaded ones (the earlier zips were overwritten in place), noted only.
- jlc_final.py remapped from A15/C3 to A16/C4 (designators unchanged between A15 and A16 and between C3 and C4, apart from the new F1/F2 on A16 and the removed EPD1 on C4); E1 gained R3 C23138, R4 C25803 and U2 (EL817, SOP-4, blank, matched on the site). jlc-rotations.csv gained ^SOP-4,270 (assumed same class as SOIC, to be verified in the preview). Rebuilt final/ sets: A16 32 lines (F1, F2 blank), C4 40 lines (D10, D11 blank), E1 14 lines (U2 blank).
- Cart lines deleted (owner: discard): pcb-e1-dock-gerbers_Y13 (PCB + PCBA), pcb-a-power-gerbers_Y12 (PCB + PCBA), pcb-c-display-gerbers_Y10 (PCB + PCBA). Standing: E2 Y2, B10 Y11, D5 Y9.

### A16 (new upload, 16:25 onward)
- Gerber: site detected "4 layer board of 160x285mm" (notes 285.1 x 160.1, 4 layers). Options as on A15: FR-4, 4 layers, qty 5, 1.6 mm, Black, white silk, FR4 TG135, ENIG 1 U", 1 oz outer / 0.5 oz inner, no layer sequence or stackup spec (default JLC04161H-7628), impedance control not ordered (as before, owner decision), plugged vias, 0.3 mm via, +-0.2 mm, Remove Mark, flying probe, Confirm Production file YES with "Do not confirm automatically", everything else No. PCB-only EUR 72.17 before assembly, 73.89 with the assembly rails (production size 285 x 170 mm).
- Assembly: Standard (Economic greyed), TOP side, qty 5, edge rails by JLCPCB, Confirm Parts Placement YES with "Do not confirm automatically", self-service parts, no extras.
- BOM/CPL: final/pcb-a-power-bom-final.csv + final/pcb-a-power-cpl-jlc.csv. Site: 32 lines, 29 confirmed, 1 shortage, 2 unmatched. Reload trap again: J_GPS1/J_WIFI1 (C3197637) and J_PACK/J_X1202BAT (C98733) came in unticked as duplicate-code lines, re-ticked (qty 10 each pair). FE1.1S trap again: U6 came in as C6706491 (5 shortfall), re-selected C9359 FE1.1S-BSOP28BCN (stock 33632). All other lines matched the codes from the A15 table (section 2) unchanged.
- F1, F2 (Keystone 3568 mini-blade fuse holders): the exact part exists at JLC as C5249699 "3568 Blade Clip Plugin Fuseholders" but stock is 2 against 10 needed (inventory shortage; the only other option the site offers is Pre-order via global sourcing). No other listing carries the Keystone 3568 footprint (searches: "3568", "mini blade fuse holder", "Fuseholders", "Fuseholders Blade"; the hits are 5x20 cylindrical clips and unrelated parts), and a different package is not allowed. LEFT UNFITTED: bench-fit two Keystone 3568 per board together with the bench-fit fuses. Owner may instead pick Pre-order on those two rows before paying.
- Placement preview (2D): J_MEZZ1 (2x8) and J_AB1 (2x7) vertical over their pad columns, XT60 bodies upright over their pads, U6/U19 pin-1 marks top-left as on A15, hub SOT-23 cluster marks as on A15. Same footprint classes and offsets as the verified A15 upload, no new rotation classes on this board apart from the unplaced fuse holders.
- Quote: PCB 73.89 + Standard PCBA 120.88 (setup 22.03, stencil 7.08, components 28 items 53.81, feeders 27.69, SMT 2.10, confirm placement 0.39, hand-soldering 3.09, manual 4.27, packaging 0.44) = EUR 194.77, identical to the A15 figure. Build PCB 3 days + assembly 5 to 6 days, weight 2.81 kg. Product Description: Development Board, HS 847330. Assembly remark: "MeshSat PCB-A POWER Rev A (A16). Orientation per silkscreen pin-1 marks and key notches (J_AB1 2x7, J_MEZZ1 2x8); XT60 polarity per silkscreen. F1, F2 fuse holders not placed (customer fits). Please flag any doubt in the placement confirmation."
- Saved to cart 16:32 as pcb-a-power-gerbers_Y14: PCB Y14-11651261A EUR 73.89 (5 pcs, 3 days), PCBA SMT026090362637-11651261A EUR 120.88 (top side, 5 to 6 days).

### C4 (new upload, 16:33 onward)
- Gerber: site detected "2 layer board of 311x442mm" (notes 442.1 x 311.1, 2 layers). Options as on C3: FR-4, 2 layers, qty 5, 2.0 mm, Black ("Change Black to Green" answered No, thanks), white silk, FR4 TG135, ENIG 1 U", 1 oz, tented vias, 0.3 mm via, +-0.2 mm, Remove Mark, flying probe, Confirm Production file YES with "Do not confirm automatically", rest No. Large-size fee applies (EUR 55.16 before assembly, 58.95 with rails). PCB-only EUR 188.42 before assembly.
- Assembly: Standard (Economic greyed), BOTH sides (18 top, 70 bottom), qty 5, edge rails by JLCPCB (production size 442 x 321 mm), Confirm Parts Placement YES with "Do not confirm automatically", self-service parts, no extras.
- BOM/CPL: final/pcb-c-display-bom-final.csv + final/pcb-c-display-cpl-jlc.csv (the C3 codes from section 2, EPD1 gone). Site: 40 lines, 38 confirmed, 2 unmatched (D10, D11 white 3 mm LEDs, bench-fit as before). Reload trap: 18 rows came in unticked because they share a code with another row (D1/D3/D4 C99771, D2/D12 C282137, D5..D9 + D13..D16 C2927624, J_PIJ2/J_X1202SW C265283, U1/U2 C2864778); all re-ticked, quantities now 15 / 10 / 45 / 10 / 10. Correction to section 2: the red 3 mm LED code is C99771 (204-10SURD/S530-A3-L), not C90771 as typed there.
- No new parts on C4 against C3; all matches identical to the C3 table, including D17 BAT54W C915628, FB C1002, R10 C23182, R16..R27 C22828, R29 C21190, U1/U2 PCA9555PWR C2864778, BZ1 C96093, J_EPD C32713274, J_PANEL C18202145.
- Placement preview (2D, bottom): J_PANEL (2x10) horizontal over its pad field at the west edge, shroud body still extends past the board edge exactly as on C3 (design item, unchanged in C4); U1/U2 TSSOP-24 pin-1 marks top-left, Q1..Q4 SOT-23 marks as on the verified D5 class, U5..U8 SOT-23-6 as verified. Top side: 16 THT LEDs, buzzer, J_EPD, J_PANEL not affected. Same classes and offsets as the second-pass C3 upload.
- Quote: PCB 195.06 (engineering 28.44, large size 58.95, ENIG 28.27, board 78.51, confirm file 0.90) + Standard PCBA 174.45 (setup 44.06, stencil 7.08, large size 49.52, components 25 items 25.48, feeders 23.73, SMT 1.85, confirm placement 0.39, hand-soldering 3.09, manual 4.66, fixture 14.15, packaging 0.46) = EUR 369.52 (C3 second pass was 369.51). Build PCB 24 h + assembly 4 to 5 days, weight 7.06 kg. Product Description: Development Board, HS 847330.
- Assembly remark: "MeshSat PCB-C CONTROL PANEL Rev A (C4). U1/U2 TSSOP-24 pin 1 per silkscreen; J_PANEL 2x10 box header (bottom side) horizontal, key notch per silkscreen; LED cathodes per silkscreen flat. D10, D11 not placed (customer fits). Please flag any doubt in the placement confirmation." Saved to cart 16:39 as pcb-c-display-gerbers_Y15: PCB Y15-11651261A EUR 195.06 (5 pcs, 24 h), PCBA SMT026090362659-11651261A EUR 174.45 (both sides, 4 to 5 days).

### E1 (new upload with the optocoupler, 16:40 onward)
- Gerber: site detected "2 layer board of 44x250mm" (notes 250.1 x 44.1, 2 layers). Options as before: FR-4, 2 layers, qty 5, 1.6 mm, Black, white silk, FR4 TG135, ENIG 1 U", 1 oz, tented vias, 0.3 mm via, +-0.2 mm, Remove Mark, flying probe, Confirm Production file YES with "Do not confirm automatically", rest No. PCB-only EUR 23.27 before assembly, 27.53 with rails (production size 250 x 70 mm).
- Assembly: Standard, TOP side, qty 5, rails by JLCPCB, Confirm Parts Placement YES with "Do not confirm automatically", self-service parts, no extras.
- BOM/CPL: final/pcb-e1-dock-bom-final.csv + final/pcb-e1-dock-cpl-jlc.csv (14 lines; new R3 330R C23138, R4 100k on the R1 line C25803, U2 blank). Site: 14 lines, 13 confirmed, U2 unmatched. LED1: the source BOM now carries C72043 again (Everlight 19-217/GHC-YR1S2/3T); kept KT-0603G C12624 from the first pass (C72043 had 1 pc in stock this morning), same value and package.

| Ref | BOM line | Chosen LCSC | Part | Why |
|---|---|---|---|---|
| U2 | EL817S / PC817 optocoupler, SOP-4 3.8x4.1 P2.54 | C63268 | Everlight EL817S1(B)(TU)-F, SOP-4-2.54mm, Extended, stock 371814, EUR 0.0397 | exact family the BOM names, in stock. Not taken: EL817SC C2912101 (0 stock, 342 idle), EL817S1(B)(TU)-FV C2922457 (stock 10015, VDE variant, dearer), EL817S1(B)(TU)-FG C42381181 (0 stock), PC817C C22447129 (stock 154605, Sharp-compatible clone, same package; second choice if the Everlight runs out) |

- Result: 14 of 14 matched, nothing left unfitted on E1.
- Placement preview, first attempt with SOP-4 at 270 (the SOIC assumption): U2's body rendered vertical across a horizontal pad pair, i.e. 90 degrees off. JLC's SOP-4 zero is the same as KiCad's (pins left and right), unlike SOIC-8. Corrected jlc-rotations.csv to ^SOP-4,0, rebuilt final/, re-uploaded BOM + CPL through Upload BOM/CPL (U2 now carries C63268 in the BOM, so no re-matching; 14 of 14 confirmed, no reload swaps this time). Second preview (2D, zoomed): U2 horizontal over its pads with JLC's pin-1 dot at the top-left corner next to KiCad's silk triangle; Q1 SOIC-8 dot top-left as before; LED1 as before; D1/D2/D3 cathode bands left. Verified.
- Quote: PCB 27.53 + Standard PCBA 57.54 (setup 22.03, stencil 7.08, components 14 items 7.89, feeders 15.82, SMT 0.51, confirm placement 0.39, hand-soldering 3.09, manual 0.31, packaging 0.43) = EUR 85.07 (was 81.92 before the opto: +2 feeders, +3 parts). Build PCB 24 h + assembly 4 to 5 days, 1.37 kg. Product Description: Development Board, HS 847330. Assembly remark: "MeshSat PCB-E1 DOCK Rev A (opto spin). Polarity per silkscreen: Q1 SOIC-8 pin 1 top-left, U2 SOP-4 optocoupler pin 1 per silkscreen mark, LED1 and diode cathode bands as marked. Please flag any doubt in the placement confirmation."
- Saved to cart 16:46 as pcb-e1-dock-gerbers_Y16: PCB Y16-11651261A EUR 27.53 (5 pcs, 24 h), PCBA SMT026090362701-11651261A EUR 57.54 (top side, 4 to 5 days).

### C-RING-R1 (new bare board, 16:47)
- Gerber: site detected "2 layer board of 56.65x108.64mm" against the notes' 105.9 x 53.9 mm. The 0.75 mm / 2.7 mm difference is the alignment tabs outside the nominal frame outline (the notes say holes, window, tabs); the site measures the bounding box of the edge cuts. Noted, not a stop item; the owner can compare against the 1:1 print in the deliverable folder.
- Options: FR-4, 2 layers, qty 5, 1.0 mm, Black, white silk, FR4 TG135, ENIG 1 U", 1 oz, tented, 0.3 mm via, +-0.2 mm, Remove Mark, flying probe, Confirm Production file YES with "Do not confirm automatically", rest No. No "change to green" prompt at 1.0 mm. No assembly (PCB only, as the notes say). Quote: engineering 3.45 + ENIG 14.82 + board 2.59 + confirm file 0.90 = EUR 21.75, 3 days, 0.19 kg. ENIG is two thirds of the price of this copper-less spacer; the notes ask for ENIG on all boards, so it stays, but the owner could drop this one to HASL or OSP via Edit Order if they want (there is nothing to plate).
- Saved to cart 16:47 as pcb-c-ring-gerbers_Y17: PCB Y17-11651261A EUR 21.75 (5 pcs, 3 days). No PCBA line.

### 5.1 Cart state after the third pass, 3 Sep 2026 16:48 CEST (read from the cart page; no screenshot file)

Seven boards, twelve lines, every line qty 5, nothing ticked, no checkout opened, nothing paid. All five PCBA lines carry Confirm Production File and Confirm Parts Placement with "Do not confirm automatically"; the two bare boards carry Confirm Production File.

| Board | PCB line | PCB EUR | PCBA line | PCBA EUR | Board total EUR |
|---|---|---|---|---|---|
| A16 POWER | Y14-11651261A, 3 days | 73.89 | SMT026090362637-11651261A, top side, 5 to 6 days | 120.88 | 194.77 |
| B10 COMPUTE (standing) | Y11-11651261A, 3 days | 71.13 | SMT026090361254-11651261A, both sides, 5 to 6 days | 197.57 | 268.70 |
| C4 CONTROL PANEL | Y15-11651261A, 24 h | 195.06 | SMT026090362659-11651261A, both sides, 4 to 5 days | 174.45 | 369.51 |
| C-RING-R1 SPACER | Y17-11651261A, 3 days | 21.75 | none (bare board) | 0 | 21.75 |
| D5 APRS (standing) | Y9-11651261A, 3 days | 28.56 | SMT026090361211-11651261A, both sides, 5 to 6 days | 165.93 | 194.49 |
| E1 DOCK (opto) | Y16-11651261A, 24 h | 27.53 | SMT026090362701-11651261A, top side, 4 to 5 days | 57.54 | 85.07 |
| E2 RF JUNCTION (standing) | Y2-11651261A, 3 days | 50.45 | none (bare board) | 0 | 50.45 |
| **Sum** | | **468.37** | | **716.37** | **1184.74** |

Change against section 4.1 (1159.85): +24.89 = ring 21.75 + E1 opto parts 3.15 (+2 feeder lines, +3 parts) - 0.01 rounding. Shipping (the C4 panel alone is 7.06 kg), import VAT and coupons still excluded, as in section 3.

### 5.2 Substitutions and unfitted parts in this pass
- A16 F1, F2 Keystone 3568 fuse holders: NOT placed (JLC C5249699 has 2 in stock, 10 needed, no other listing in that footprint). Bench-fit with the fuses, or choose Pre-order on those two BOM rows via Edit Order before paying.
- A16 U6 FE1.1S: site swapped to C6706491 again on upload, put back to C9359 by hand (third time today; anyone re-uploading must re-check this row).
- E1 U2 optocoupler: EL817S1(B)(TU)-F C63268 chosen (in stock); rotation class SOP-4 verified at offset 0 (not 270 as first assumed).
- E1 LED1: kept KT-0603G C12624 although the regenerated BOM carries C72043 (stock 1 this morning).
- C4 D10, D11 (3 mm white LEDs): still unmatched, bench-fit as in section 3.1. D5 L1 unchanged (section 3.1).
- Everything else matched the codes chosen in sections 2 and 4 unchanged; no new package substitutions.

### 5.3 Still open for the owner
- Section 3.2 items 2 to 8 unchanged (generator LCSC codes, E1 Q1 rating, impedance control not ordered on A16/B10, D5 two-sided because of R36, product description, stock-thin USB-A C3197637: 20 needed across A16 + B10 against the 116 seen this morning).
- Rotation table jlc-rotations.csv now verified for: IDC 2xN 270, SOIC-8 270, SSOP-28 270, TSSOP-24 270, LQFP-48 270, Texas VQFN 0, SOT-23 180, SOT-23-5/6/8 270, LED_0603 180, SOP-4 0. Unverified and covered by Confirm Parts Placement: WSON-6 270, SOT-223 180, USB-C 180, crystal 3225 0, JST/XT60/USB-A/Keystone 0. These offsets still need to go into make_handoff.py (design session).
- B10, D5, E2 carts stand on this morning's uploads; their 16:06 to 16:15 regenerated files were checked identical in BOM/CPL content, the regenerated zips could not be compared (earlier zips overwritten).
- Ring board: JLC reads the outline as 56.65 x 108.64 mm (notes 105.9 x 53.9), presumably the tabs; ENIG on a copper-less spacer costs EUR 14.82 of its 21.75.

## Design session update, 3 Sep 2026 17:50: legend (silkscreen text) corrections on all seven boards

- Owner request after the JLCPCB 2D preview of the panel: every board's silk legends repositioned or reworded (panel labels off the display frame, toggle labels beside their switches, battery bar numbers under their LEDs, nameplate text clear of the data-matrix square, assembly notes moved to the underside; A16/B10/D5/E1/E2 banners and wall labels moved off parts and edges; stale phase tags updated). Copper, BOM and CPL are unchanged; only the gerber zips differ.
- Action for the ordering session: re-upload the gerber zip of every line (all seven) from JLCPCB/<board>/ once the handoff rebuild finishes (ORDER-NOTES.txt timestamps after 17:55). BOM/CPL files can stay as uploaded. No option changes.
- 18:00: C4 face reference designators hidden as well; take the C4 zip and all CPL files from the rebuild finishing after 18:10 (CPL rotations now carry the JLC offsets from jlc-rotations.csv at the source; your final/ CPLs and these should agree).

## 6. Fourth pass, 3 Sep 2026 from 18:15 CEST: silk-only gerber re-upload of all seven boards (owner instruction 18:12)

- Inputs: all seven ORDER-NOTES.txt at 17:59 to 18:09, every zip changed against the 16:05 set (md5), layer sets unchanged (A16/B10/D5 with In1/In2, the rest F/B only). The regenerated top-level CPLs are byte-identical (after sorting) to the final/ CPLs uploaded in pass 3, and the BOM designator/footprint sets are identical, which confirms the source now carries the same JLC offsets. jlc_final.py not run.
- Method finding: JLCPCB cannot replace the gerber of an existing cart line. The "Re-Upload" link on the Edit Order quote page is a plain link to a fresh /quote (it drops cartAccessId, i.e. a new order with no BOM/CPL), and the smt-order PCB/BOM tabs have no gerber control (checked in the DOM: zero file inputs). So every line is rebuilt as a new order: new zip, same options, same final/ BOM + CPL files as pass 3 (identical content to the regenerated top-level files), then the old line deleted. The A16 Edit Order session opened for this check was abandoned without saving.

### A16 (silk rev 2, rebuilt 18:20 to 18:27)
- New zip (17:59 export): site detected "4 layer board of 160x285mm", same as before. Options identical to pass 3 (black, ENIG, 1.6 mm, plugged vias, Remove Mark, Confirm Production file YES + do-not-confirm-automatically; assembly Standard, top side, qty 5, rails by JLCPCB, Confirm Parts Placement YES + do-not-confirm-automatically). The browser extension dropped out once in the middle of the production-file dialog; the dialog was redone (No, then Yes, box ticked, confirmed) before going on.
- BOM/CPL: the pass-3 final/ files again (identical to the 17:59 top-level files). 32 lines: 4 duplicate-code rows re-ticked (J_GPS1/J_WIFI1, J_PACK/J_X1202BAT), U6 swapped by the site to C6706491 again and put back to C9359, F1/F2 left unplaced (Do not place). 30 confirmed + 2 unplaced, as in pass 3.
- Quote: PCB 73.89 + PCBA 120.87 = EUR 194.75 (2 cents under pass 3, component price drift). Description Development Board 847330. Remark as pass 3 with "(A16, silk rev 2)".
- Saved to cart 18:27 as pcb-a-power-gerbers_Y18: PCB Y18-11651261A EUR 73.89, PCBA SMT026090363057-11651261A EUR 120.87. Old Y14 (PCB + PCBA) deleted 18:29; cart back to 7 items.

### B10 (silk rev 2, rebuilt 18:30 onward)
- New zip (18:01 export): site detected "4 layer board of 170x245mm", as this morning. Options as in section 2 (black, ENIG, 1.6 mm, 1 oz / 0.5 oz inner, plugged, impedance not ordered, Remove Mark, Confirm Production file YES + do-not-confirm-automatically; assembly Standard, BOTH sides, qty 5, rails by JLCPCB (245 x 180 mm), Confirm Parts Placement YES + do-not-confirm-automatically). PCB-only 71.13 with rails, same as the standing Y11 line.
- BOM/CPL: pass-2 final/ files (identical to the 18:01 top-level files). 41 lines; 5 duplicate-code rows re-ticked; U1 FE1.1S swapped by the site to C6706491 again, put back to C9359; Y1 = C5160137 (12 MHz) confirmed. 41 of 41 confirmed.
- Quote: PCB 71.13 + PCBA 197.55 (39 items) = EUR 268.68 (pass-2 line was 268.70). Description Development Board 847330. Remark: "MeshSat PCB-B COMPUTE Rev A (B10, silk rev 2). Orientation per silkscreen pin-1 marks and key notches (J_GPIO1 2x20, J_RB9704 2x8, J_PANEL 2x10, J_AB1 2x7 on the bottom side); U1 SSOP-28, U20 TSSOP-24, SOT-23-8 and WSON-6 parts pin 1 per silkscreen; USB-C receptacles per footprint. Please flag any doubt in the placement confirmation."
- Saved to cart 18:32 as pcb-b-compute-gerbers_Y19: PCB Y19-11651261A EUR 71.13, PCBA SMT026090363076-11651261A EUR 197.55. Old Y11 (PCB + PCBA) deleted right after.

### C4 (silk rev 2 with hidden face designators, rebuilt 18:33 onward)
- New zip (18:03 export): site detected "2 layer board of 311x442mm", as in pass 3. Options as in pass 3 (2.0 mm, black with "No, thanks" to the green prompt, ENIG, 1 oz, tented, Remove Mark, Confirm Production file YES + do-not-confirm-automatically; assembly Standard, BOTH sides, qty 5, rails by JLCPCB (442 x 321 mm), Confirm Parts Placement YES + do-not-confirm-automatically). PCB-only 195.06 with rails, same as Y15.
- BOM/CPL: pass-3 final/ files (identical to the 18:03 top-level files). 40 lines; 18 duplicate-code rows re-ticked; D10/D11 white LEDs unmatched, Do not place; U1/U2 C2864778, D1/D3/D4 C99771 as before. 38 placed + 2 unfitted, as in pass 3.
- Placement preview (3D top): face silk now shows the legend without reference designators and the moved labels, as the 18:00 note describes. Quote: PCB 195.06 + PCBA 174.45 (25 items) = EUR 369.51, identical to Y15. Description Development Board 847330. Remark as pass 3 with "(C4, silk rev 2)".
- Saved to cart 18:36 as pcb-c-display-gerbers_Y20: PCB Y20-11651261A EUR 195.06, PCBA SMT026090363087-11651261A EUR 174.45. Old Y15 (PCB + PCBA) deleted right after.

### C-RING-R1 (silk rev 2, rebuilt 18:37)
- New zip (18:05 export): site detected "2 layer board of 56.65x108.64mm", as in pass 3. First option clicks landed before the upload had finished and were reset by the site (it showed 1.6 mm / HASL); re-set to 1.0 mm, Black, ENIG, Confirm Production file YES + do-not-confirm-automatically, no assembly. Quote EUR 21.75 as before.
- Saved to cart 18:38 as pcb-c-ring-gerbers_Y21: PCB Y21-11651261A EUR 21.75. Old Y17 deleted right after.

### D5 (silk rev 2, rebuilt 18:39 onward)
- New zip (18:06 export): site detected "4 layer board of 62x80mm", as this morning. Options as in section 2 (black, ENIG, 1.6 mm, plugged, Remove Mark, Confirm Production file YES + do-not-confirm-automatically; assembly Standard, BOTH sides (R36), qty 5, rails by JLCPCB, Confirm Parts Placement YES + do-not-confirm-automatically). PCB-only 28.56 with rails, same as the standing Y9 line.
- BOM/CPL: pass-2 final/ files (identical to the 18:06 top-level files). 39 lines; 12 duplicate-code rows re-ticked; L1 (Coilcraft, blank code) auto-matched by the site to C139207 again and un-ticked (bench-fit, section 3.1); no shortages. 38 placed + L1 unfitted, as before.
- Quote: PCB 28.56 + PCBA 165.84 (32 items) = EUR 194.40 (Y9 was 194.49). Description Development Board 847330. Remark: "MeshSat PCB-D APRS Rev A (D5, silk rev 2). Orientation per silkscreen pin-1 marks and key notch (J_HARN1 2x8); U5 LQFP-48, U1 VQFN, SOT-23 parts and LEDs pin 1 / cathode per silkscreen. L1 not placed (customer fits). Please flag any doubt in the placement confirmation."
- Saved to cart 18:43 as pcb-d-aprs-gerbers_Y22: PCB Y22-11651261A EUR 28.56, PCBA SMT026090363099-11651261A EUR 165.84. Old Y9 (PCB + PCBA) deleted right after. (The cart page rendered empty for a moment after the save while the badge showed 8; a reload showed all lines.)

### E1 (silk rev 2, rebuilt 18:44 onward)
- New zip (18:08 export): site detected "2 layer board of 44x250mm", as before. Options as in pass 3 (black, ENIG, 1.6 mm, tented, Remove Mark, Confirm Production file YES + do-not-confirm-automatically; assembly Standard, top side, qty 5, rails by JLCPCB, Confirm Parts Placement YES + do-not-confirm-automatically). PCB-only 27.53 with rails, same as Y16.
- BOM/CPL: pass-3 final/ files (identical to the 18:08 top-level files, SOP-4 at 0). 14 of 14 confirmed straight away (U2 C63268, LED1 C12624), no re-ticks, no swaps. Quote: PCB 27.53 + PCBA 57.54 (14 items, confirm file 0.90, confirm placement 0.39) = EUR 85.07, identical to Y16. Description Development Board 847330. Remark as pass 3 with "(opto spin, silk rev 2)".
- Saved to cart 18:48 as pcb-e1-dock-gerbers_Y23: PCB Y23-11651261A EUR 27.53, PCBA SMT026090363115-11651261A EUR 57.54. Old Y16 (PCB + PCBA) deleted right after.

### E2 (silk rev 2, rebuilt 18:49)
- New zip (18:09 export): site detected "2 layer board of 32x330mm", as this morning. Options as in section 2 (2.0 mm, black with "No, thanks" to the green prompt, ENIG, 1 oz, tented, Remove Mark, Confirm Production file YES + do-not-confirm-automatically, no assembly). Quote EUR 50.45, same as the standing Y2 line.
- Saved to cart 18:50 as pcb-e2-rfjunction-gerbers_Y24: PCB Y24-11651261A EUR 50.45. Old Y2 deleted right after.

### 6.1 Cart state after the fourth pass, 3 Sep 2026 18:51 CEST (read from the cart page)

Seven boards, twelve lines, every line qty 5, nothing ticked, no checkout opened, nothing paid. Every line now carries the 17:59 to 18:09 silk-revision gerbers. All five PCBA lines carry Confirm Production File and Confirm Parts Placement with "Do not confirm automatically"; the two bare boards carry Confirm Production File. BOM and CPL content is unchanged from pass 3 (same final/ files; the regenerated top-level files are identical).

| Board | PCB line | PCB EUR | PCBA line | PCBA EUR | Board total EUR |
|---|---|---|---|---|---|
| A16 POWER | Y18-11651261A, 3 days | 73.89 | SMT026090363057-11651261A, top side, 5 to 6 days | 120.87 | 194.76 |
| B10 COMPUTE | Y19-11651261A, 3 days | 71.13 | SMT026090363076-11651261A, both sides, 5 to 6 days | 197.55 | 268.68 |
| C4 CONTROL PANEL | Y20-11651261A, 24 h | 195.06 | SMT026090363087-11651261A, both sides, 4 to 5 days | 174.45 | 369.51 |
| C-RING-R1 SPACER | Y21-11651261A, 3 days | 21.75 | none (bare board) | 0 | 21.75 |
| D5 APRS | Y22-11651261A, 3 days | 28.56 | SMT026090363099-11651261A, both sides, 5 to 6 days | 165.84 | 194.40 |
| E1 DOCK (opto) | Y23-11651261A, 24 h | 27.53 | SMT026090363115-11651261A, top side, 4 to 5 days | 57.54 | 85.07 |
| E2 RF JUNCTION | Y24-11651261A, 3 days | 50.45 | none (bare board) | 0 | 50.45 |
| **Sum** | | **468.37** | | **716.25** | **1184.62** |

Change against section 5.1 (1184.74): -0.12, component price drift on A16, B10 and D5. Shipping (C4 alone 7.06 kg), import VAT and coupons still excluded, as in section 3. Old lines Y2, Y9, Y11, Y14, Y15, Y16, Y17 no longer exist.

### 6.2 Notes from this pass
- Re-uploading a gerber on JLCPCB means a new order line every time (section 6 method finding). Any further gerber revision costs the full rebuild again: five assembled boards with the reload traps (duplicate-code rows unticked, FE1.1S swapped to the out-of-stock C6706491 on A16 and B10, D5 L1 auto-matched to C139207). All three traps hit again in this pass and were handled the same way.
- Unfitted parts unchanged: A16 F1/F2 (Keystone 3568, JLC stock 2), C4 D10/D11 (3 mm white LEDs), D5 L1 (Coilcraft). Section 3.2 items unchanged.
- The bare boards save from the quote page without a product description; the assembled boards carry "Development Board, HS 847330" as before.

## 4 Sep 2026 00:20: A16 and B10 superseded by A17 and B11 (appendix 32)

The cart lines for PCB-A and PCB-B were prepared from A16 and B10 and must be rebuilt from `PCB-A-POWER-A17/` and `PCB-B-COMPUTE-B11/` when the owner says so; the other five lines stand. The A16 and B10 folders with the `upload/` and `final/` copies of what went into the cart are kept under `superseded/` as the record of those lines. Reasons: the X1202's real outline (the Geekworm DXF) and the 5 V module rail ruling, appendix 32.2 to 32.4.

## 4 Sep 2026 afternoon: A17 and E2 superseded by A18 and E3 (appendix 32.10)

The dock connector is now the Preci-Dip 813-S1-008-10-016101 (solder tails 0.8 mm), so the eight `J_DOCK` holes went from 1.5 to 1.1 mm on the routed board (no part moved): **A18** replaces A17. The junction strip's D-hole flat follows the Amphenol Connex 132170 drawing (6.00 across instead of 6.25): **E3** replaces the strip's E2 issue. The cart lines for PCB-A and PCB-E2 must be rebuilt from `PCB-A-POWER-A18/` and `PCB-E2-RFJUNCTION-E3/` when the owner says so, together with PCB-B from `PCB-B-COMPUTE-B11/`. C4's schematic PDF carries the switch part numbers now; its gerbers, JLC BOM (same row set) and CPL are unchanged, the panel line stands. `PCB-A-POWER-A17/` and `PCB-E2-RFJUNCTION-E2/` are under `superseded/`.

## 4 Sep 2026 evening: the deferral list moved into this build (appendix 32.13, 32.14)

Owner rulings: TPS61288 boost, heating-pad output and SMP-MAX blind-mate on a PCB-A respin (A19); dock respin with the MPPT carrier and a 13 mm gap; MIL-DTL-38999 wall connector; APEM 5636ADKB-2V locking toggles (bench part swap, C4 unchanged). Cart consequences: line A is not rebuilt from A18 (A19 supersedes), line E2 is deleted (E3 retired), line E1 is rebuilt after the dock respin, line B is rebuilt from B12 after the PCB-B respin of 32.17; C4, R1 and D5 stand.

**Owner, 4 Sep 2026 evening, on the order split:** no edits to the JLCPCB cart now; everything is prepared in the repository first (A19, the dock respin, the retired wall strip, the case connector) and the cart is rebuilt once, when the whole set is final.

## 5 Sep 2026 night: A19 pass 5, the sealed panel C5, the spacer ring R1 retired (appendix 32.33, 32.34)

PCB-A A19 was rerouted on locked fine-pitch escapes (0 hard, 0 unrouted); `PCB-A-POWER-A19/` is rebuilt from it, `PCB-E5-BLOCK-E5/` from the rebuilt block. The control panel is respun as **C5**, the case's sealed weather face: `PCB-C-DISPLAY-C5/` replaces `PCB-C-DISPLAY-C4/` (now under `superseded/`), and `PCB-C-RING-R1/` moves under `superseded/` with no replacement. What changes for the cart when the owner declares the set final: line Y20 (C4 PCB and PCBA) is deleted and rebuilt from `PCB-C-DISPLAY-C5/` with the via covering set to **plugged** (JLCPCB plugs holes up to 0.5 mm; every via on C5 is 0.3 or 0.4) and the outline's four keyed switch holes (three 2.70 x 1.10 keyway notches and one D flat, routed over the drilled holes); the assembly has fewer through-hole rows (the sounder and every connector left the JLC BOM or became SMD on the underside); line Y21 (R1, EUR 21.75) is deleted. The die-cut seal outlines (`pcb-c-display-seals.dxf` in the deliverable folder) are not a JLC file. No cart edit was made (owner, 4 and 5 Sep: the cart is rebuilt once, when the whole set is final).
