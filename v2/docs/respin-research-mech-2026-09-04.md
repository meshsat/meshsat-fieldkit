# Mechanical and RF parts for the A19 and dock respin: document findings

Date: 4 September 2026. Scope: the six research items of the respin brief (SMP-MAX blind-mate set, spring-loaded DC contacts for the new gap, Keystone 3568 height with a blade, MIL-DTL-38999 shore DC pair plus the Glenair 233-370 USB receptacle, Microchip USB2517 hub, APEM 5636ADKB-2V). Every figure below carries its document and page. Documents were fetched with curl from the maker or, where the maker refused, from a distributor copy; all copies are saved in this folder (`scratchpad/respin/`). Nothing in the repository was changed. Sizes in mm unless stated.

Fetch notes for the record: radiall.com product pages answer 404, but Radiall's data sheets are served from `radiall-files.s3.amazonaws.com/tds/coaxialconnectors/<PN>%20<rev>.pdf` (R222M80500 rev A and R222M00720 rev B found; R222M80400, R222M40010, R222M00700 and R222M00740 answer 403 for every revision letter tried). keyelco.com now serves its catalogue pages directly (`userAssets/file/M65p<NN>.pdf`) while refusing product pages; the Wayback Machine was offline (HTTP 503) during this session. microchip.com refuses curl (403); the full data sheet came from LCSC. littelfuse.com refuses curl; a distributor copy of the 297 data sheet was used. glenair.com serves everything.

## 1. Radiall SMP-MAX (series R222M)

Documents:
- `radiall-smp-max.txt`: text of the repo catalogue `v2/vendor/rf/radiall-smp-max-series-R222M-D1C004XEe.pdf` (8 pages, April 2011). Page renders `radiall-p-4.png` to `radiall-p-7.png`.
- `radiall-R222M00720-tds.pdf`: technical data sheet R222.M00.720, issue 1107 B, 2 pages, from `https://radiall-files.s3.amazonaws.com/tds/coaxialconnectors/R222M00720%20B.pdf` (drawing `tds-00720-1.png`).
- `radiall-R222M80500-tds.pdf`: technical data sheet R222.M80.500, issue 1115 A, 2 pages, from `https://radiall-files.s3.amazonaws.com/tds/coaxialconnectors/R222M80500%20A.pdf` (drawing `tds-80500-1.png`).
- Repo `v2/vendor/rf/radiall-R222M40050-tds.pdf` (adapter, issue 1122 A, 4 pages) for the interface conventions on its pages 3 and 4 (renders `tds-40050-1.png`, `-3.png`, `-4.png`).

### 1.1 Part numbers confirmed

| Part | What the catalogue says | Where |
|---|---|---|
| R222M00720 | straight slide-on male receptacle for PCB, solder legs, panel drilling P02, bulk 100, captive centre contact | catalogue p. 6, receptacle table, Fig. 2; TDS title "STRAIGHT MALE RECEPTACLE FOR PCB, SLIDE TYPE, SOLDER LEGS" |
| R222M80500 | right-angle female plug for flexible cable, cable group RG174/RG316 (2.6/50/S), captive centre contact, bulk 100 | catalogue p. 5, right-angle plug table; TDS title "RIGHT ANGLE FEMALE PLUG CRIMP TYPE, CABLE 2.6/50S", recommended cables RG 174, RG 316, KX 22A, ECO 316 (TDS p. 2) |
| R222M80400 | straight female plug for flexible cable, RG174/RG316, captive centre contact, bulk 100; body length 17.1, knurl diameter 5.5, cable entry diameters 2.95 / 1.65 / 0.6 | catalogue p. 5, straight plug drawing and table (its TDS was not obtainable, see fetch notes) |
| R222M40010, R222M40050 | in-series board-to-board adapters, SMP-MAX female / SMP-MAX female, length L 9.5 and 25.3 | catalogue p. 7, in-series adapter table |
| R222M00700 / R222M00740 | the SMT slide-on receptacles (tape and reel), heights 6.4 and 7.5 on the catalogue drawings | catalogue p. 6, Fig. 1 and Fig. 3 |
| R222M00080 / R222M10000 | snap-on receptacles (solder legs P02 / screw-on P01) | catalogue p. 6 |

### 1.2 R222M00720 dimensions (TDS issue 1107 B, page 1 drawing)

- Overall height 9.6 from the tip of the solder legs to the top of the funnel; solder legs 1.9 long; so the body stands 7.7 above the board surface. The 2011 catalogue drawing (p. 6, Fig. 2) shows 9.4 overall with the same 1.9 legs, so 7.5; the TDS is the part drawing and is used below, the 0.2 mm difference is noted.
- Interface reference plane ("Ref. plane") 2.68 above the board surface, inside the funnel.
- Funnel top diameter 8.3, funnel wall 1.8; square flange 5.9; four solder legs 0.8 square on 1.2 square pads; centre pin diameter 0.8.
- Panel (board) drilling, TDS table "PANEL CUT OUT": centre hole A 1.1 to 1.2, four leg holes B 1.3 to 1.4 on a square C 5.03 to 5.13. Catalogue p. 7 "P02" gives the same table.
- Electrical (TDS p. 2): 50 ohm, 0 to 6 GHz, VSWR 1.25 max to 3 GHz and 1.35 max 3 to 6 GHz, insertion loss 0.15 x sqrt(F) dB max, 335 V working, 1000 V withstand, mating life 100 cycles min, radial working angle 3 deg min, axial working range 2 mm, power over 300 W at 2.7 GHz (25 C), mass 1.31 g, temperature -55 to +165 C.

### 1.3 R222M80500 dimensions (TDS issue 1115 A, page 1 drawing)

- Height from the interface reference plane ("Ref.", at the tip of the outer-contact fingers) to the far face of the body: 10.7. Cable axis 7.98 above the reference plane. Length along the cable 13.4. Body 6.5 square. Crimp ferrule diameters 2.95 and 1.65; ferrule step 1.4 and 0.95.
- The plug has no flange, groove or thread. The only features a retainer can bear on are the 6.5 square body and its shoulder toward the fingers; the collar and finger diameters are not dimensioned on the sheet.
- Electrical (TDS p. 2): VSWR 1.05 + 0.045 x F(GHz) max, insertion loss 0.065 x sqrt(F) dB max, 750 V withstand, cable pull-off 53 N min, mating life 100 cycles, crimp dies R282.235.003 (M22520/5-03 hex 3.25) in tool R282.271.000 or R282.293.000 (M22520/5-01), stripping a 2.00, b 5.00, c 9.00, e 7.00, mass 2.24 g.

### 1.4 Interface figures (catalogue p. 4, "Characteristics" table)

- Mating cycles 100. Engagement force slide-on under 14 N (snap-on under 45 N). Disengagement force slide-on under 9 N (snap-on over 9 and under 45 N). Centre contact retention over 7 N.
- Axial misalignment tolerance 2.0 mm ("larger axial misalignment version available"); the VSWR and loss tables are given at axial 0 and +/-1 mm. Radial misalignment (tilt) 3 deg minimum. "Minimum distance between PCB 13 mm" (this is the receptacle-adapter-receptacle scheme, see 1.7).
- RF leakage -70 dB to 3 GHz at 0 mm axial. Temperature -55 to +165 C. Body brass / beryllium copper, insulator PTFE/PEEK.
- Adapter TDS p. 4 (repo file): "Axial working range +/-1", "Radial working angle 3 deg", the "Interface reference" is the distance between the two receptacles' reference planes; "Radial working range = (length of the adapter) x sin(radial working angle)". Adapter TDS p. 3: the connecting range is "the maximum misalignment during connection", "a blind assembly is guaranteed if radial misalignment is smaller than connecting range, otherwise a manual lead-in is necessary"; the sheet draws it but prints no value, and the swivelling angle in a snap receptacle is 6 deg.

### 1.5 Mated stack, receptacle under PCB-A plus right-angle cable plug (derived from 1.2 and 1.3)

Convention used: at full mate the receptacle's reference plane and the plug's reference plane coincide (that is what "Ref. plane" on both sheets and "Interface reference" on the adapter sheet mean). Datum: the underside surface of PCB-A, positive downward.

| Item | Position below PCB-A | Source |
|---|---|---|
| receptacle reference plane | 2.68 | 00720 TDS |
| receptacle funnel top | 7.7 (catalogue drawing: 7.5) | 00720 TDS (9.6 minus 1.9 legs) |
| plug cable axis | 2.68 + 7.98 = 10.66 | 80500 TDS |
| plug far face (toward the floor) | 2.68 + 10.7 = 13.38 | 80500 TDS |
| axial working range | plug far face anywhere in 12.38 to 14.38 keeps the RF figures | catalogue p. 4, adapter TDS p. 4 |

- Mated engagement depth: the plug's outer-contact fingers enter the funnel by 7.7 minus 2.68 = 5.02 at nominal (4.02 to 6.02 across the +/-1 mm working range). Neither sheet prints an engagement depth as such; this is the geometric consequence of the two reference-plane dimensions.
- Board-to-floor distance for the pair: PCB-A underside to the dock strip top = 13.4 nominal if the plug's far face rests on the strip (the strip then takes the engagement push, up to 14 N per joint, and a retainer plate around the 6.5 square body takes the extraction pull, up to 9 N per joint). Any value from 12.4 to 14.4 keeps the RF inside the working range. Add the strip (1.6) and the VHB pads to reach the case floor. The record's 13 mm (appendix 32.7, 32.14) is therefore 13.4 with the actual sheets, so the provisional Z figure of 32.14 moves by 0.4 mm (104.8 + 7.4 = 112.2 against the 114.1 panel underside, 1.9 mm spare, before the B12 changes of 32.17).
- The RG-316 exits sideways along the floor with its axis 10.66 below PCB-A; a full bend radius is never needed inside the gap (finding C of 32.15 confirmed by the right-angle plug).
- Float mount: the plug carries nothing to float on (1.3), so the dock-side retainer is a bespoke two-plate clamp with a window larger than the 6.5 square body by the wanted radial float; the funnel (8.3 diameter) and the 3 deg angle are the interface's own lead-in. No document in hand states the capture range for a cable plug; Radiall application support is the source if the design wants a number, the rods hold the stack to about 0.3 mm (32.7) which is far inside a funnel that large.
- Forces on the stack: seven slide-on joints, up to 98 N to seat and up to 63 N to lift (7 x 14 N, 7 x 9 N, catalogue p. 4). The slide-on receptacle is the lowest-retention SMP-MAX variant, as 32.14 asked for.

### 1.6 Are the in-series adapters needed?

No. The record is right. R222M40010 and R222M40050 are "SMP-MAX female / SMP-MAX female" (catalogue p. 7) and exist to join two male receptacles across a board-to-board gap. The dock-side part is a female plug (R222M80500, "RIGHT ANGLE FEMALE PLUG") and the PCB-A part a male receptacle (R222M00720, "STRAIGHT MALE RECEPTACLE"); they mate directly. The catalogue's "minimum distance between PCB 13 mm" belongs to the receptacle-adapter-receptacle scheme and does not bind the cable-plug arrangement.

### 1.7 Recommendation

Seven R222M00720 under PCB-A (TDS drilling table 1.2, legs on the 5.03 to 5.13 square, local ground pour per 32.15 D), seven R222M80500 crimped on RG-316 in a bespoke float clamp on the dock strip, PCB-A underside to strip top 13.4 nominal (spacers 13.4, tolerance window 12.4 to 14.4 from the RF side, but see 2.5 for the pogo-pin window). No adapter. Order the crimp die R282.235.003 or use the M22520/5-03 equivalent.

## 2. Spring-loaded DC contacts for the 13.4 mm gap

Documents:
- Preci-Dip catalogue, `scratchpad/parts/precidip.pdf` (text `precidip.txt`): general specifications p. 31, 2.54 mm solder-tail connectors p. 34, surface-mount p. 35 to 37, 8PM p. 38, pad connectors p. 39, contact technology p. 180.
- Mill-Max "Spring-loaded connectors" catalogue pages 4 to 22, metric edition 2021-02, `millmax-004M-022M-spring-loaded-connectors.pdf` from `https://www.mill-max.com/sites/default/files/external/catalog/2021-02/004M-022M.pdf` (65 pages); Mill-Max spring-loaded pins pages 23 to 28.6, `scratchpad/parts/mm-2019.pdf` (render `mmpower-07.png` = catalogue page 28).
- Harwin "Spring Loaded Contacts" catalogue section (ATE spring probes p. 289 and earlier, spring loaded contacts P70 p. 290 to 292), TTI-hosted copy `harwin-spring-loaded-contacts-catalog-tti.pdf` from `https://www.tti.com/content/dam/ttiinc/manufacturers/harwin/doc/harwin-spring-loaded-contacts-catalog.pdf` (cdn.harwin.com answers 404 for its former PDF paths).

### 2.1 Preci-Dip

- General specifications (p. 31): hollow-piston type minimum initial height 3 mm, stroke max 2 mm; shaped-piston (low resistance) type minimum 6 mm, stroke max 2 mm; clip in-line type minimum 10 mm, stroke max 1.5 mm; stroke/height ratio 0.3 / 0.2 / 0.15; minimum initial spring force 0.2 N; 100 V rms / 150 V DC on the 2.54 grid; -55 to +125 C (+85 C with music-wire springs).
- 2.54 mm solder-tail family (p. 34): 811-S1-NNN-10-XXX101 single row, 813-S1-NNN-10-XXX101 double row (4 to 72 contacts), shaped piston, music-wire spring, stroke 1.4 mm max, forces 0.25 N initial and 0.85 N at half stroke, 3.5 A max, 10 mohm, 50,000 cycles; heights code 014 = 6.0, 015 = 6.5, 016 = 7.0, 017 = 7.5 (plastic body 4 mm). The record's 813-S1-008-10-016101 is the 2 x 4, 7.0 mm member.
- Surface-mount families (p. 35 to 37): 4.5 to 7.5 (codes 001 to 007 and 021 to 027, hollow piston, 0.6 N at half stroke, 3.5 A; codes 014 to 017 shaped piston). 8PM parallel SMD (p. 38): 3 A, stroke 1.5 mm.
- No Preci-Dip 2.54 mm connector reaches 12 mm; the tallest is 7.5 (code 017). Pad connectors 800/802 (p. 39) are the fixed counterparts (contact area 1.5 mm, 3.5 A), not a height extender.

### 2.2 Mill-Max

- 2.54 grid strips (004M-022M pages 6 to 8 and the through-hole page): series 812/814 surface mount and 816/818 through-hole, "mid profile", contact styles 0 to 9 with initial heights 6.48, 6.99, 7.49, 8.0, 8.51, 8.89, 9.4, 9.91, 10.41, 10.92; stroke 1.4; rating "2 A continuous, 3 A peak per contact", 20 mohm, 100 V rms / 150 V DC, up to 1,000,000 cycles. Ordering 814-22-0XX-30-00X101 (double row, XX contacts 04 to 72, X style 0 to 9). Tallest 2.54 mm strip in the catalogue: 10.92, at 2 A.
- Other ratings in the same catalogue: 945 series (single-contact targets, 3.5 A continuous 5 A peak), 858 series 4 mm grid dual plunger (9 A at 10 C rise); neither is a 2.54 mm strip.
- Discrete power spring pins (mm-2019 page 28, order code 08XX-X-XX-20-8X-14-11-0): 9 A continuous at 10 C rise, springs 82/83 stroke 0.045 in mid / 0.090 in max (2.29 mm), 120 g at mid stroke, 25 g preload; 0858 (solder mount in a 0.045 in hole) stands 0.378 in (9.60) above the board with a 0.503 in (12.78) overall length; 0878 same head with a 0.657 in (16.69) overall length; flange 0.125 in (3.18) diameter, which is wider than the 2.54 pitch, so they cannot sit side by side on the record's 2 x 4 pattern.
- Standard 09xx discrete pins (mm-2019 page 25): 2 A continuous, 3 A peak; 0906 series heads 0.155 to 0.236 in; none near 12 mm.

### 2.3 Harwin

- P70 series spring loaded contacts (catalogue p. 290 to 292): free heights 2.4, 2.5, 2.8, 3.6, 4.8, 5.0, 5.5, 6.2, 6.3, 8.2 mm; 1 A or 2 A; 10,000 operations; the tallest, P70-2200045 (8.2 free height), is rated 2 A with 0.98 N at 7.10 working height. None reaches 12 mm and none reaches 3 A.
- ATE two-part spring probes P25 (p. 289): "long length probe bodies with 6.3 mm travel, for 2.54 mm minimum pitch", body 25.0 long, 1.36 diameter, full travel 6.30, 2.45 N at full travel and 1.67 N at 2/3, current for the two-part probes 3 A, 100,000 operations, sleeves S25-546 (solder barrel, 25.0 long, 1.90/1.80/1.66 diameters, 22 to 30 AWG) and S25-346 (wire-wrap). These bridge 13 mm with margin but are test-fixture parts 25 mm long with sleeves that must stand through the board; listed for completeness, not recommended for a field kit.

### 2.4 The raised-block alternative (recommended)

Keep the Preci-Dip 813-S1-008-10-016101 (2 x 4, 7.0 initial height, 3.5 A per contact, 1.4 stroke, p. 34) on PCB-A's underside as in A18 and raise the dock targets on a block so that the local gap is 6.0 (pins compressed 1.0 of 1.4, 0.85 N at half stroke per pin, 6.8 N for eight): block top = 13.4 minus 6.0 = 7.4 above the strip, for example the existing 2.0 mm ENIG target pattern on a 1.6 mm FR-4 pad board over 5.8 mm of standoff (M3 x 6 standoffs give 7.6 and 1.2 mm compression, still inside the 1.4 stroke). The 7.5 mm member (code 017) with a 6 mm standoff would compress 1.7 and bottom out, so stay with 7.0 or shim.

Why this and not a taller part: no documented 2.54 mm pitch spring-loaded connector reaches 12 mm (Preci-Dip 7.5, Mill-Max 10.92 at 2 A, Harwin 8.2 at 2 A); the only single parts that span the gap are ATE probes. The block keeps the owner's named part (32.10), the 3.5 A rating and the A18 drill (1.1 mm for the 0.8 mm tails), and it costs one small pad board and four standoffs.

### 2.5 The tolerance window is now the pogo pins', not the RF joint's

The SMP-MAX joint accepts +/-1 mm axially; the 813 pins accept only their 1.4 mm stroke (nominal 1.0 compression leaves +0.4 / -1.0 mm before the pins bottom or lift). The block height, the spacer length and the strip flatness must be held inside that, which the rod-and-spacer stack does; but the block should be shimmable at assembly. Record this in the A19 design rule.

## 3. Keystone 3568 mini blade fuse holder, height with a fuse

Documents:
- Keystone catalogue M65 page 42, "Mini automotive fuse clips and holders", `keystone/M65p42.pdf` from `https://www.keyelco.com/userAssets/file/M65p42.pdf` (render `keystone/p42-1.png`). Keystone's product page 306 (the 3568) answers 403.
- Littelfuse MINI blade fuse rated 32 V, 297 series data sheet, distributor copy `littelfuse-297-ficcorp.pdf` from `https://www.ficcorp.com/content/297-datasheet.pdf` (render `lf297-1.png`); older Littelfuse catalogue page (Farnell copy `littelfuse-blade-farnell.pdf`, p. 451) for the reference dimensions.

Values:
- 3568 "MINI FUSE HOLDER, for Littelfuse Mini 297 or 997 series / Bussmann ATM or equivalents" (M65 p. 42, right-hand middle drawing): insulator height 0.290 in (7.37) above the board, length 0.630 in (16.00), width 0.265 in (6.73), four PC pins 0.110 in (2.79) long on a 0.390 x 0.134 in (9.9 x 3.40) pattern, holes 0.063 in (1.60); contacts 0.016 in brass tin-nickel, nylon 4/6 UL 94V-0, UL current rating 30 A at 500 V AC, -50 to +145 C. The drawing shows no fuse.
- MINI (ATM) fuse (Littelfuse 297 data sheet, "Dimensions"): width 10.9, body height 8.8, blade length 7.5 (overall 16.3), thickness 3.8, blade 2.8 x 0.81. The older catalogue page gives 10.92 / 8.04 / 7.37 / 3.81 / 2.79 for the same fuse.
- Height with a blade fitted: the blade (7.5) is as long as the holder is tall (7.37), so the fuse body seats on the holder top: 7.37 + 8.8 = 16.2 (16.3 if the blades bottom 0.13 mm short). Report 16.3 mm above the dock strip surface. That is 2.9 mm more than the 13.4 mm gap of section 1, so F1 cannot stand under PCB-A at all: place it in the clear band (Y -95 to -80, appendix 32.18) or change the holder.
- Documented low alternative on the same catalogue page: horizontal fuse entry. Cat. No. 3549 clips (nickel plate, 30 A, 0.212 in = 5.4 tall, mounting 0.295 x 0.400 in) or the 3549-2 holder (tin plate, UL 20 A, drawing height 0.228 in = 5.8, footprint 0.394 x 0.700 in = 10.0 x 17.8) lay the mini fuse flat, so its 3.8 mm thickness is the vertical dimension inside the clip; the page prints no assembled height, but the clip height plus the fuse thickness is well under the gap. The 3557-2 low-profile holder needs the Littelfuse 897 low-profile mini, not the 297 in hand.

Recommendation: keep the 3568 for the fuse the owner buys (297 series, 7.5 A as designed) and move F1 into the clear band; if the band is full, the 3549-2 horizontal holder at 20 A UL is the documented low-height swap.

## 4. MIL-DTL-38999 Series III receptacle and plug for shore DC, and the Glenair 233-370 USB receptacle

Documents (all Glenair unless stated):
- `glenair-d38999-20.pdf`: D38999/20 wall-mount receptacle, catalogue "MIL-DTL-38999 Series III and IV" p. 30 (QPL, Rev 03.11.25) and p. 31 (233-105 COTS equivalent with the dimension table, Rev 03.12.25), from `https://www.glenair.com/mil-dtl-38999-connector-series-iii/pdf/mil-dtl-38999-series-iii-environmental/d38999-20.pdf` (renders `gl20-1.png`, `gl20-2.png`).
- `glenair-d38999-24.pdf`: D38999/24 jam-nut receptacle, p. 28 (Rev 07.17.26) and p. 29 (dimension table), same path with `d38999-24.pdf` (renders `gl24-1.png`, `gl24-2.png`).
- `glenair-d38999-26.pdf`: D38999/26 plug, p. 26 and 27.
- `glenair-series-iii-iv-panel-cutouts.pdf`: "Recommended panel cut-outs" p. 12 (Rev 09.01.20), `.../pdf/series-iii-and-iv-recommended-panel-cut-outs.pdf` (render `glcut-1.png`).
- `glenair-series-iii-iv-pin-contact-selection.pdf`: pin contact selection guide p. 17 (wire ranges per contact size).
- `glenair-series-iii-env-overview.pdf`: Series III environmental overview (IP statement).
- `glenair-mil-std-1560-standard-arrangements.pdf`: MIL-STD-1560 standard arrangements (drawings; the insert data below is read from the Amphenol chart, which is text).
- Amphenol Aerospace "MIL-DTL-38999 Series I LJT, II JT, III TV" catalogue, distributor-hosted copy `amphenol-d38999-iii-federal.pdf` from `https://d38999.federalconnectors.com/datasheets/Amphenol/Amphenol_D38999_Series_III.pdf` (80 pages; amphenol-aerospace.com answers 403).
- `glenair-233-370.pdf`: SuperSeal catalogue pages C-14 and C-15, 233-370 USB 2.0 Type A feed-through receptacle (already in the folder).

### 4.1 Contacts and insert arrangements

- Contact test current (Amphenol catalogue p. 28, "Contact Ratings / Service Ratings", crimp column): size 22D 5 A, size 20 7.5 A, size 16 13 A, size 12 23 A. Wire per Glenair p. 17: size 20 contact takes #20 to #24, size 16 takes #16 to #20 (M39029/58-363 and /58-364 pins).
- Four-contact arrangements available in Series III TV (Amphenol chart pp. 3 to 4, "Insert Arrangements", rows "Series III TV"): 11-2 (two size 16, service rating I), 11-4 (four size 20, I), 11-5 (five size 20, I), 13-4 (four size 16, I), 13-8 (eight size 20, I). Also 9-98 (three size 20) and 9-35 (six size 22D, rating M).
- Two 12 V, 5 A poles plus a spare pair means four contacts: 13-4 (four size 16 at 13 A, wire #16 to #20) or 11-4 (four size 20 at 7.5 A, wire #20 to #24).

### 4.2 Wall-mount receptacle D38999/20 (Glenair p. 30 and p. 31 table)

Part number build: D38999/20 + class (W cadmium olive drab -65 to +175 C; F electroless nickel; T nickel-PTFE; J or M composite) + shell letter (A 9, B 11, C 13, D 15, E 17) + insert + P pins / S sockets + N normal polarization. COTS equivalent 233-105-00 (slotted holes) or -D0 (round holes).

| Shell | A thread | B sq flange | C bsc holes (front) | D bsc holes (rear) | E hole dia | F slot | G flange | H nose | J rear thread |
|---|---|---|---|---|---|---|---|---|---|
| 11 (B) | .7500 | 26.49 / 25.88 | 20.62 | 18.26 | 3.45 / 3.05 | 5.13 / 4.72 | 2.49 / 2.11 | 20.83 / 19.58 | M15 |
| 13 (C) | .8750 | 28.91 / 28.30 | 23.01 | 20.62 | 3.45 / 3.05 | 5.13 / 4.72 | 2.49 / 2.11 | 20.83 / 19.58 | M18 |
| 15 (D) | 1.0000 | 31.29 / 30.68 | 24.61 | 23.01 | 3.45 / 3.05 | 4.60 / 4.19 | 2.11 | 19.58 | M22 |

Overall length 1.240 in (31.50) max; the drawing is marked "front or rear panel mount".

Panel cut-out (Glenair p. 12 table): shell 11 rear-mount hole A 20.22, front-mount hole AA 15.88, mounting holes T 3.25 +/-0.13 on R1 20.62 (front) or R2 18.26 (rear); shell 13: A 23.42, AA 19.05, R1 23.01, R2 20.62; shell 15: A 26.59, AA 23.01, R1 24.61, R2 23.01. Panel thickness for the wall-mount style: the Glenair 233-370 sheet gives ".0625/.250 panel accommodation" (1.59 to 6.35) and the Amphenol wall-mount table (catalogue p. 50, TVP00, column "AA max panel thickness") gives .234 in (5.94) for shells 9 to 19.

### 4.3 Jam-nut receptacle D38999/24 (Glenair p. 28 and p. 29 table)

| Shell | ØU jam nut | V | W flat | X thread | Y thread | Z panel thickness | ØAA hole | BB flat |
|---|---|---|---|---|---|---|---|---|
| 11 (B) | 35.20 / 34.59 | 32.21 / 31.39 | 19.18 / 18.92 | M20 | M15 | 3.10 / 2.11 | 21.21 / 20.96 | 19.58 / 19.33 |
| 13 (C) | 38.40 / 37.80 | 35.31 / 34.49 | 23.93 / 23.67 | M25 | M18 | 3.10 / 2.11 | 25.91 / 25.65 | 24.26 / 24.00 |
| 15 (D) | 41.61 / 41.00 | 38.51 / 37.69 | 27.08 / 26.82 | M28 | M22 | 3.10 / 2.11 | 29.08 / 28.83 | 27.56 / 27.30 |

Z applies to shells 9 to 19 (3.89 / 2.90 for 21 to 25). Amphenol's jam-nut page (catalogue p. 51) states "panel thickness .062 min .125 max" (1.57 to 3.18) and deep-reach shells up to .750 in. Overall 1.280 in (32.51) max, O-ring under the flange.

### 4.4 Plug D38999/26 (Glenair p. 26)

D38999/26 + class + shell + insert + S sockets (or P) + N; length 1.220 in (30.99) max, rear accessory thread EE; the 233-105-G6 is the COTS EMI-spring plug. Cycles: 500 (P/S) or 1500 (H/J).

### 4.5 IP rating

Glenair Series III environmental overview: "Environmental performance: interfacial and wire grommet seals deliver IP67 level sealing, even at high altitude". The 233-370 sheet (C-14) states "Meets IP67 in unmated condition, IP68 mated".

### 4.6 Glenair 233-370 USB receptacle (SuperSeal catalogue C-14 and C-15)

- Part number 233-370 + finish (NF cadmium olive drab, M electroless nickel, MT nickel-PTFE, ZR black zinc-nickel) + style (07 rear panel jam nut, 00 wall mount slotted holes, D0 wall mount round holes, CM wall mount with M3 x 0.5 clinch nuts) + shell 15 or 17 + 2 (USB 2.0) + A (front Type A) + A (rear Type A) + polarization (N) + H horizontal or V vertical USB orientation. Sample: 233-370NF00-17 2AANH. "All external dimensions, features, etc. compliant with D38999/20, /24 and /26".
- Wall mount cut-out (table "Wall mount", C-14): shell 15: A thread 1.0000, B sq 31.29 / 30.68, C bsc 24.61, D bsc 23.01, E 3.45 / 3.05, F 4.60 / 4.19, G holes 3.45; shell 17: B sq 33.60 / 32.99, C 26.97, D 24.61, E 3.05, F 5.13 / 4.72, G 3.05. Receptacle length 1.570 in (39.87) max, flange to nose .650 / .600 in (16.51 / 15.24), flange 2.49 / 2.11; ".0625/.250 panel accommodation (this side only)" = 1.59 to 6.35 mm; CM style has 4 x M3 x 0.5 clinch nuts; 00 style slotted 4.60 x 3.45 holes, D0 style 4 x 3.15 round holes.
- Jam nut style 07 (table "Jam nut mount"): shell 15 ØH 41.61 / 41.00, J 38.51 / 37.69, K flat 27.08 / 26.82, L thread M28 x 1.0-6G; shell 17 ØH 44.81 / 44.20, J 41.71 / 40.89, K flat 30.25 / 30.00, M32 x 1.0-6G; length 1.570 in max, .890 in (22.61) max behind.
- Wiring: pin 1 VBUS red 22 AWG, 2 D- white 28 AWG, 3 D+ green 28 AWG, 4 GND black 22 AWG.

### 4.7 Recommendation

Shore DC: shell 13, insert 13-4, four size 16 contacts (13 A each; the two live poles at 5 A run at 38 % of rating, the second pair is the spare), wall-mount receptacle D38999/20FC4PN (F = electroless nickel, RoHS; W if cadmium is acceptable) with mating plug D38999/26FC4SN, or the Glenair COTS pair 233-105-00 ME 13-4 P N and 233-105-G6 ME 13-4 S N. Cut-out per 4.2 (rear mount: Ø23.42 hole, four Ø3.25 holes on a 20.62 square; front mount: Ø19.05 on 23.01). Shell 11 with 11-4 (four size 20 at 7.5 A, Ø20.22 or Ø15.88 hole) is the compact fallback. Keep the 233-370 in shell 15 wall mount (same mounting method, Ø26.59 or Ø23.01 hole per 4.2) so both wall parts share one panel-plate design; the jam-nut styles need a 2.11 to 3.10 mm wall (4.3), which a machined pad on the Peli wall can provide but a plate does more simply. Bonding of the shells on a plastic case stays the open item of 32.15 G.

## 5. Microchip USB2517 / USB2517I

Documents:
- `usb2517-datasheet-DS00001598C-lcsc.pdf`: "USB2517/USB2517I Data Sheet", DS00001598C, 2013-2018, 59 pages, from `https://datasheet.lcsc.com/datasheet/pdf/91d9ee3f35bf91e09515bc08ab5bdea0.pdf` (linked from the LCSC page of C1521556). microchip.com refuses curl and the Wayback Machine was offline.
- `usb2517-databrief-lcsc.pdf`: the SMSC data brief (5 pages) from the same page.

Values (data sheet page numbers as printed):
- Package: 64-pin QFN, 9 x 9 mm body, 0.5 mm pitch, exposed slug is VSS (p. 1 features, Figure 10-1 p. 53 to 54).
- Supply rails (Table 5-1, p. 16): VDD33 pin 46 (3.3 V digital I/O), VDD33CR pin 24 (3.3 V, input of the internal 1.8 V core regulator), VDD33PLL pin 64 (3.3 V, input of the internal 1.8 V PLL regulator), VDDA33 pins 5, 10, 52, 57 (3.3 V filtered analog PHY, shared between adjacent ports); VDD18 pin 25 and VDD18PLL pin 62 are the regulated 1.8 V nodes, each needing a 1.0 uF (or larger) +/-20 % capacitor with ESR under 0.1 ohm to VSS. RBIAS pin 63: 12.0 kohm +/-1 % to ground (p. 12). VBUS_DET pin 44 tied to 3.3 V or 5 V for a self-powered hub with a permanently attached host (p. 10).
- Currents (DC characteristics, p. 50, "all supplies combined"): unconfigured 95 mA; configured with a Hi-Speed host: 1 port HS plus 1 port LS/FS 230 mA, 2 ports LS/FS 230 mA, 2 ports HS 270 mA, 4 ports HS 330 mA, 7 ports HS 420 mA typical / 460 mA max; Full-Speed host 205 to 235 mA typical (270 max at 7 ports); suspend 360 uA typical / 610 uA max; reset 110 / 400 uA.
- Crystal (p. 51, "Crystal: parallel resonant, fundamental mode, 24 MHz, 350 ppm"; external clock 24 MHz +/-350 ppm, 50 % +/-10 % duty; XTAL1/CLKIN pin 61, XTAL2 pin 60, Figure 9-1 gives the load-capacitor formula from CL, CB and CXTAL = 2 pF). On-chip crystal driver (p. 1).
- Configuration method (Table 5-2, p. 15): the three pins CFG_SEL[2:0] (CFG_SEL0 shared with SCL pin 41, CFG_SEL1 with HS_IND pin 42, CFG_SEL2 pin 13) are latched at RESET_N negation: 000 internal default with the strap options enabled; 001 SMBus slave at address 0101100 for register download; 010 internal default, straps enabled, bus-powered, LED mode USB; 011 2-wire I2C EEPROM; 100 / 101 / 110 / 111 internal default variants with straps disabled (dynamic power switching, LED mode, ganged power and over-current). So the hub runs from its internal default with pin straps, from an I2C EEPROM on SDA/SCL (pins 40, 41), or from an SMBus master; strap options (port disable, port swap, non-removable ports, boost, gang) are sampled on the port and LED pins at reset. RESET_N pin 43 pulled to VDD33 enables the internal POR.
- Per-port pins (Table 5-1, p. 10 to 12, listed for ports 7 down to 1): USBDN_DP pins 56, 54, 12, 9, 7, 4, 2 and USBDN_DM pins 55, 53, 11, 8, 6, 3, 1 (also the PRT_DIS straps, 10 k to 3.3 V to disable a port); PRTPWR pins 36, 39, 30, 20, 23, 26, 29 (active high, "active high power controllers only"); OCS_N pins 37, 38, 35, 21, 22, 27, 28 (internal pull-ups); LED_A_N pins 15, 17, 31, 33, 47, 49, 51 (also the port-swap straps); LED_B_N pins 14, 16, 18, 32 (ports 7 to 4), 34 (port 3, also GANG_EN), 48 and 50 (ports 2 and 1, also BOOST straps). Upstream USBUP_DP pin 59, USBUP_DM pin 58. SUSP_IND/LOCAL_PWR/NON_REM0 pin 45, TEST pin 19 (pull-down).
- Temperature: USB2517 0 to +70 C, USB2517I -40 to +85 C (p. 1).

Recommendation: USB2517I (industrial) in the 64-QFN, 3.3 V only with the two 1.0 uF regulator capacitors, 24 MHz crystal, internal default plus straps (no EEPROM) unless custom descriptors are wanted, one TPS2065 per PRTPWR/OCS_N pair as the four existing channels do, VBUS_DET to 3.3 V. Budget 460 mA max on the 3.3 V rail at seven HS ports.

## 6. APEM 5636ADKB-2V

Document: APEM toggle switch catalogue, `scratchpad/parts/apem-toggles.pdf` (text `apem-toggles.txt`), 5000 series section pages A23 to A40 (renders `apem-p-24.png`, `apem-p-28.png`, `apem-p-37.png`, `apem-p-40.png`).

Code build, from the "build your own switch" order format on page A35 (model structure and options boxes):
- 5 = series (5000 series miniature toggle);
- 6 = terminals and bushing: "solder lug terminals with 1/4-40 (6.35 mm) or 15/32-32 (11.9 mm) threaded bushings" (the 1/4-40 form; 15/32-32 is the M terminal code);
- 3 = single pole;
- 6 = electrical function ON - ON (ON-NONE-ON);
- AD = contact material "silver, gold plated" (A silver, AD gold-plated silver, CD gold-plated brass); page A23 rates gold-plated silver at 3 A 250 V AC, 6 A 125 V AC or 4 A 30 V DC, with the gold plating withstanding up to 100 mA at 30 V DC;
- K = "front panel sealing with o-ring and gasket", B = "epoxy sealed terminals", "KB both of above";
- -2V = locking actuator, 2 locked positions; page A37 "2V 2 locked positions (function 6)", page A28 lists 5636AB-2V under "single pole, locking actuator, 1/4-40 threaded bushing, solder lug terminals" with both ON positions locked (terminals 2-3 and 1-2).

Confirmed: the code assembles as the brief states, and the catalogue's own example of a completed number is 5636AB (page A35), so 5636ADKB-2V follows the format.

Dimensions:
- Bushing: 1/4-40 UNS, 9.00 (.354 in) long on all three locking actuators (page A37 drawings 1V, 2V, 3V); actuator height above the bushing base 14.75 (.580 in) for 2V (14.85 for 1V, 15.10 for 3V), lever tip 5.20 diameter; the standard (non-locking) 5636AB drawing on page A24 gives 10.50 (.413 in) and 8.00 (.314 in) for the body.
- Panel cut-out for 1/4 in bushings (page A40): standard, Ø6.50 (.255 in) plus a Ø2.20 (.086 in) anti-rotation hole at 5.20 (.204 in) from the centre; with the K sealing option, Ø6.50 with a keyway notch 2.70 (.106 in) wide and 1.10 (.043 in) deep (the K version uses the keyway bushing, page A35 option drawings "K with 1/4 in keyway bushing"). The 6.5 mm hole of the C4 panel matches.
- Panel thickness: the 5000 series pages state no panel thickness range. Hardware supplied (page A23): 2 hex nuts 8 mm across flats, 1 locking ring, 1 lockwasher; the K seal adds its o-ring and gasket. The 2.0 mm panel, gasket, lockwasher and one front nut must fit inside the 9.0 mm bushing with the rear nut backing the switch; the catalogue's only explicit thickness statement in this file (1.5 mm with two nuts, 3 mm with one nut, page A11) belongs to the ZL series and does not apply.

Recommendation: 5636ADKB-2V as ruled (32.13 item 1), no panel change; ask APEM for the panel thickness limit of the K-sealed 1/4-40 locking version when the parts are ordered, since the sheet does not print it.

## 7. What this does to the dock gap

The gap rule of 32.18 (larger of the RF stack and the tallest dock part plus margin) resolves as: RF stack 13.4 (section 1.5); TEN 40-2412WIN 10.2 (record) fits under PCB-A with 3.2 mm; the 3568 with a mini blade, 16.3 (section 3), does not fit at any gap the RF joint accepts (12.4 to 14.4), so F1 moves to the clear band or becomes a horizontal-entry holder; the DC joint keeps the 813 pins on a 7.4 mm target block (section 2.4), with the block height and shims setting the pin compression (section 2.5). Nominal spacer 13.4 mm.

## 8. Recommended parts

| Part | Function | Document file (this folder unless stated) |
|---|---|---|
| Radiall R222M00720 | SMP-MAX slide-on male receptacle, solder legs, seven under PCB-A | `radiall-R222M00720-tds.pdf` (issue 1107 B); catalogue `v2/vendor/rf/radiall-smp-max-series-R222M-D1C004XEe.pdf` p. 6 |
| Radiall R222M80500 | SMP-MAX right-angle female crimp plug for RG-316, seven in the dock float clamp | `radiall-R222M80500-tds.pdf` (issue 1115 A); catalogue p. 5 |
| Radiall R282.235.003 die (M22520/5-03) | crimp die for the plug | `radiall-R222M80500-tds.pdf` p. 2 |
| Preci-Dip 813-S1-008-10-016101 | 2 x 4 spring-loaded DC contacts, 7.0 mm, 3.5 A, on a 7.4 mm target block | `scratchpad/parts/precidip.pdf` p. 34 |
| Keystone 3568 | mini blade fuse holder (F1), in the clear band; 3549-2 as the horizontal-entry fallback | `keystone/M65p42.pdf`; fuse `littelfuse-297-ficcorp.pdf` |
| Glenair D38999/20FC4PN (or 233-105-00 ME 13-4 P N) | shore DC wall-mount receptacle, shell 13, four size 16 contacts | `glenair-d38999-20.pdf`, `glenair-series-iii-iv-panel-cutouts.pdf`, `amphenol-d38999-iii-federal.pdf` p. 28 |
| Glenair D38999/26FC4SN (or 233-105-G6 ME 13-4 S N) | mating shore DC plug | `glenair-d38999-26.pdf` |
| Glenair 233-370 M 00-15 2AANH | USB 2.0 Type A feed-through, shell 15, wall mount | `glenair-233-370.pdf` |
| Microchip USB2517I-JZX | seven-port USB 2.0 hub, 64-QFN 9 x 9 | `usb2517-datasheet-DS00001598C-lcsc.pdf` |
| APEM 5636ADKB-2V | locking sealed toggle, SOS / EMCON / ZEROIZE | `scratchpad/parts/apem-toggles.pdf` p. A28, A35, A37, A40 |

## 9. Not found or left open

- Radiall TDS for R222M80400 (straight plug) and R222M40010 (9.5 mm adapter): the S3 path refuses them; the catalogue page 5 and 7 entries stand. Not needed for the chosen arrangement.
- The SMP-MAX "connecting range" (blind-mate capture radius) is drawn but not valued on any sheet in hand.
- The Keystone 3568 drawing does not show a fuse; the 16.3 mm figure combines it with the Littelfuse 297 dimensions.
- APEM prints no panel thickness range for the 5000 series.
- The Glenair MIL-STD-1560 arrangement sheet is a drawing set; the insert data was read from the Amphenol chart (same MIL-STD-1560 arrangements).
