# Respin footprints (KiCad 9, format 20241229, generator "meshsat")

Files in this directory: five `.kicad_mod` footprints. Three of the eight requested parts are covered by KiCad's own library (9.0.9 on ankh, `/usr/share/kicad/footprints/`) and got no file; the reasoning is in sections 3, 7 and 8.

Conventions used: origin at the package centre, KiCad frame (x right, y down), pad numbers as the data sheet numbers them, SMD pads on F.Cu + F.Paste + F.Mask, through-hole pads as `thru_hole circle` with a ring of at least 0.25 mm, courtyard 0.25 mm outside the body on F.CrtYd, silk outline with a pin 1 mark on F.SilkS, fab outline on F.Fab, `descr` and `tags` on every file. Non-rectangular pads (the corner pads of the two TI VQFN-HR packages) are `custom` pads: one pad per pin, polygon primitive, `anchor rect` lying inside the polygon, `clearance outline`. Rectangular pads are `roundrect` with a 0.05 mm corner radius (TI's R0.05 TYP).

Generator: `../work/gen_footprints.py` (the numbers below are its inputs). Check: `../work/check_footprints.py footprints/`, a small s-expression reader that verifies balanced parentheses, that every pad has `at`, `size` and `layers`, that through-hole pads have a drill and a ring of at least 0.25 mm, that custom-pad anchors lie inside their polygons and that all copper lies inside the courtyard (true geometry, also for circular courtyards). Result on the final files: ALL PASS, pad counts 15 (11 copper + 4 paste-only), 29, 5, 1, 1. In addition the five files were loaded in KiCad 9.0.9 on the laptop through `pcbnew` (scratch directory `/tmp/respin-fp`, no repository touched, removed afterwards): all load, the custom pads produce the intended copper areas (RQQ pad 1 = 0.245 mm2, pad 3 = 0.92 mm2, RQM pad 1 = 0.29 mm2, pad 9 = 0.28 mm2), `kicad-cli pcb drc` on a scratch board holding the five footprints reports nothing except the scratch board's missing outline, and the SVG render was checked by eye.

For the two TI packages the pad outlines were not read off the callouts alone: the blue pad outlines of the "example board layout" pages were extracted as vectors with pdfplumber (`../work/pads.py`, `../work/pads2.py`; 1 mm = 20 x 72/25.4 pt at the page's 20X scale, 18X for the RQM) and every callout on the page was then matched against the extracted rectangles. Both agree to 0.001 mm.

## 1. Texas_RQQ0011A_VQFN-HR-11_2.5x3mm (written, 11 pads plus 4 paste-only pads)

Source: `tps61288.pdf` page 27 (package outline), page 28 (example board layout, scale 20X), page 29 (example stencil design); TI drawing 4225610/A 12/2019.

Package: body 3.1/2.9 x 2.6/2.4 (3.0 x 2.5 nominal, 3.0 along x), 1.0 mm max height, pin 1 identification at the top left corner of the top view; pins run counter-clockwise: 1, 2, 3 down the left, 4 at the bottom centre, 5, 6, 7 up the right, 8 to 11 along the top from right to left.

Land pattern (page 28, package centre at the origin, y down):

- pads 8, 9, 10, 11: 0.25 x 0.55 (6X (0.25), 6X (0.55)) at y = -1.175 ((1.175)), x = +0.75, +0.25, -0.25, -0.75 (3X (0.5), (1.5));
- pads 1 and 7: L shapes; leg 0.225 wide (2X (0.225)) x 0.70 tall (2X (0.7)) at x = -1.35..-1.125 (pad 1) and 1.125..1.35 (pad 7), y = -1.45..-0.75; bar 0.575 long (2X (0.575)) x 0.25 tall (2X (0.25)) at x = -1.70..-1.125 and 1.125..1.70, y = -1.00..-0.75; leg centre 0.4875 from the pad 8/11 centre (2X (0.4875));
- pads 2 and 6: 0.55 x 0.25 at (-1.425, -0.375) and (1.425, -0.375) (2X (0.375) below the centre line, 0.25 gap to the pad 3/5 bar ((0.25)));
- pad 4: 0.40 x 1.00 ((0.4), (1)) at (0, 0.25);
- pads 3 and 5: bar 1.25 long (2X (1.25)) x 0.40 tall (2X (0.2) to the centre line) at x = -1.70..-0.45 and 0.45..1.70, y = 0..0.40; leg 0.40 wide (4X (0.4)), centre 0.65 from the package centre line (2X (0.65)), x = -0.85..-0.45 and 0.45..0.85, y = 0..1.45 (2X (1.45));
- outer extents ±1.70 in x (2X (1.425) + (0.275)) and ±1.45 in y.

Stencil (page 29): identical to the copper except pads 3 and 5 at 89 percent: bar 0.35 tall (2X (0.175)), leg 0.35 wide (4X (0.35), leg centre 2X (0.625)). Implemented as four paste-only `rect` pads with an empty number: 1.25 x 0.35 at (±1.075, 0.175) and 0.35 x 1.10 at (±0.625, 0.90); the copper pads 3 and 5 therefore carry F.Cu and F.Mask only. All other pads have paste equal to copper (the sheet's stencil for them equals the land pattern).

Graphics: courtyard rectangle ±1.75 x ±1.50 (body + 0.25, it also encloses the pads with 0.05 to spare); fab outline 3.0 x 2.5 with a 0.25 chamfer at the pin 1 corner; silk corner brackets at ±1.91 x ±1.66 (0.15 clear of the pads plus half the 0.12 line) and a filled pin 1 dot at (-2.05, -0.875), level with the pad 1 bar.

## 2. Texas_RQM0029A_QFN-29_4x4mm (written, 29 pads)

Source: `bq25792.pdf` page 140 (package outline), page 141 (example board layout, scale 18X), page 142 (example stencil design); TI drawing 4225253/A 11/2019. `bq25798.pdf` pages 148 to 150 carry the same drawing 4225253/A, so one footprint serves both.

Package: body 4.1/3.9 square (4.0 nominal), 1.0 mm max height, pin 1 top left, counter-clockwise: 1 to 9 down the left, 10 to 15 along the bottom from left to right, 16 to 24 up the right, 25 to 29 along the top from right to left. The outline gives 23X 0.4 pitch on the sides and bottom, 6X 0.45 on the top row (2.7 span), 17X 0.5/0.3 and 4X 0.6/0.4 terminal lengths, 33X 0.25/0.15 terminal width.

Land pattern (page 141), all pads 0.20 wide (33X (0.2)); package centre at the origin:

- left column, pins 2 to 8: 0.60 x 0.20 (17X (0.6)) at x = -1.90 ((1.9)), y = -1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2 (2X (1.2), (0.8), (0.4));
- pin 1: bar x = -2.20..-1.25, y = -1.70..-1.50 (bar centre 2X (1.6), outer edge (1.7)); leg x = -1.45..-1.25 (leg centre 2X (1.35)), y = -2.20..-1.50 (leg centre (1.85));
- pin 9: bar x = -2.20..-1.30, y = 1.50..1.70; leg x = -1.50..-1.30 (leg centre 2X (1.4)), y = 1.50..2.20;
- pins 16 and 24: mirror images of 9 and 1 about the y axis;
- bottom row, pins 10 to 15: 0.20 x 0.60 at y = 1.90 ((1.9)), x = -1.0, -0.6, -0.2, 0.2, 0.6, 1.0 (2X (1), (0.6), (0.2));
- right column, pins 20 to 23: 0.60 x 0.20 at x = 1.90, y = 0, -0.4, -0.8, -1.2; pins 17, 18, 19 are longer, outer edge at 2.20: 0.70 long at y = 1.2 ((0.7)), 0.65 long at y = 0.8 ((0.65)), 0.675 long at y = 0.4 ((0.68), centre (1.8625));
- top row, pins 25 to 28: 0.20 x 1.00 (4X (1)) at y = -1.70, x = 0.90, 0.45, 0, -0.45 (2X (0.9), 2X (0.45)); pin 29: 0.20 x 0.95 ((0.95)) at (-0.90, -1.725) ((1.725));
- outer extents ±2.20 in both axes.

Stencil (page 142): the same outlines as the land pattern, so every pad carries paste equal to copper (the corner custom pads include F.Paste).

Graphics: courtyard ±2.25 square (body + 0.25, encloses the pads with 0.05 to spare); fab outline 4.0 square with a 0.5 chamfer at the pin 1 corner; silk brackets at ±2.41 and a pin 1 dot at (-2.55, -1.60), level with the pad 1 bar.

## 3. Microchip USB2517i, 64-QFN 9 x 9 mm 0.5 mm pitch (no file; KiCad library part matches)

Source: `usb2517-datasheet-DS00001598C-lcsc.pdf` page 53 (Figure 10-1, Microchip drawing 64QFN-4704-9x9B, title "64 PINS QFN-4704, 9x9mm BODY, 0.5mm PITCH, 4.7x4.7mm EXPOSED PAD, 0.4mm LEAD LENGTH"; common dimensions table: D/E 8.90/9.00/9.10, D1/E1 8.65/8.75/8.85, D2/E2 exposed pad 4.60/4.70/4.80, L 0.30/0.40/0.50, b 0.18/0.25/0.30, K 1.55 min, e 0.50 BSC, A 1.00 max) and page 54 (land pattern dimensions: GD/GE 8.00 min 8.10 max, GDs/GEs 8.05, D2'/E2' 4.70, pad X 0.28, pad Y 0.69, stencil Xs 0.23 to 0.25, Ys 0.62 to 0.64, e 0.50). The text layer of these two pages is empty; the tables were read from renderings.

The exposed pad is 4.70 nominal (4.60 to 4.80), so none of QFN-64-1EP_9x9mm_P0.5mm_EP3.4x3.4mm, EP3.8x3.8mm, EP4.1x4.1mm or EP4.35x4.35mm matches. KiCad's library does contain `Package_DFN_QFN:QFN-64-1EP_9x9mm_P0.5mm_EP4.7x4.7mm` (and `_ThermalVias`): exposed pad 4.7 x 4.7, perimeter pads 0.875 x 0.20 at ±4.4125 (inner edge 3.975, gap 7.95, outer edge 4.85) against Microchip's 0.69 x 0.28 with an 8.05 gap (inner edge 4.025, outer 4.715), pitch 0.50, pin 1 top left counter-clockwise, EP paste in 9 squares of 1.26 (65 percent). That is the part to use; no file was written. Page 54 shows a thermal via array under the pad; use the `_ThermalVias` variant or the board's own via pattern.

## 4. Radiall_SMPMAX_R222M00720 (written, 5 pads)

Source: `radiall-R222M00720-tds.pdf` page 1 (technical data sheet issue 1107 B, drawing) and page 2 (characteristics). Drawing: square body 5.9, four solder legs 0.8 square (4x 0.8) sitting in 1.2 corner recesses (4x 1.2), centre pin dia 0.8, funnel dia 8.3, overall height 9.6, legs 1.9 below the seating face, funnel 1.8 thick, reference plane 2.68 below the funnel face. Panel cut-out table (the PCB holes): A (centre hole) 1.1 min 1.2 max, B (four leg holes) 1.3 min 1.4 max, C (leg hole square, centre to centre) 5.03 min 5.13 max. Page 2: 50 ohm, 0 to 6 GHz, axial working range 2 mm, radial working angle 3 degrees min, 100 mating cycles, 1.31 g.

Footprint: pad 1 (centre contact, signal) `thru_hole circle` dia 1.8, drill 1.2; pads 2 (the four legs, ground, all numbered 2) at (±2.54, ±2.54), that is C = 5.08, the middle of 5.03 to 5.13 (0.200 in), dia 2.2, drill 1.4. Drill rule: the sheet gives finished hole ranges rather than pin sizes, and the sheet minimum plus 0.1 mm equals the sheet maximum in both cases (1.1 + 0.1 = 1.2, 1.3 + 0.1 = 1.4), so the drills sit at the sheet maxima. Rings 0.3 (centre) and 0.4 (legs). Fab: the 5.9 square, the dia 8.3 funnel circle, the four 0.8 leg squares, the dia 0.8 pin. Silk: the funnel circle (r 4.3) drawn as four 58 degree arcs centred on the axes, leaving ±16 degree gaps at the diagonals where the leg pads cross it (a full circle is clipped by the leg pads' mask openings, KiCad reported it), plus a tick at 12 o'clock as the 0 degree orientation mark; pin 1 is the centre pin, so there is no separate pin 1 mark. Courtyard: circle dia 9.9 (r 4.95). The funnel alone (dia 8.3) cannot be the courtyard: the leg pads reach 2.54 x sqrt(2) + 1.1 = 4.69 mm from the axis, beyond the funnel radius 4.15, so the courtyard is the pad reach plus 0.25. Adjacent receptacles therefore need at least 9.9 mm centre to centre for their courtyards, and the funnels (8.3) then clear each other by 1.6 mm.

## 5. Mill-Max_0858_power_pin (written, 1 pad)

Source: the discrete 0858 pin is on neither Mill-Max PDF in the folder. `millmax-thruhole-smt-spring-connectors.pdf` (5 pages) covers the 0.050 in pitch strips 854/855/856/857 (2 A), and `millmax-004M-022M-spring-loaded-connectors.pdf` (65 pages) is catalogue pages 4 to 22.9, connector strips only; neither contains the string 0858. The pin's own page is the catalogue's "Spring-Loaded Pins, discrete spring-loaded contacts, power spring pins" page 28, on file as the rendering `mmpower-07.png` (cited in `mech-findings.md` section 2.2 as "mm-2019 page 28"; the cell was re-read at 3x zoom, `../work/mm0858-cell.png`): 0858-0-15-20-82-14-11-0, power spring pin, solder mount in .045 in min mounting hole; plunger .050 in dia, (2X) .094 in dia, body .100 in dia, flange .125 in dia (3.175 mm, the "3.18 mm" quoted), collar .100 in dia, tail .040 in dia (1.016 mm) x .125 in (3.175 mm) long, .378 in +.007/-.004 (9.60 mm) from the flange seat to the plunger tip at free height, (.503 in) = 12.78 mm overall; further callouts .025, .046 and .066 in on the collar and flange heights. Spring 82 (page table): mid stroke .045 in (1.14 mm), max stroke .090 in (2.29 mm), 120 g at mid stroke, 25 g preload; rated 9 A continuous at 10 C rise, 20 mohm, 1,000,000 cycles.

The same contact in strips: `millmax-004M-022M-spring-loaded-connectors.pdf` pdf page 41 (catalogue page 19.75, series 858 4 mm grid rugged connectors, 9 A at 10 C rise): 4.0 mm grid, the through-hole version 858-22-00X-10-0X1101 "designed for manual placement into 1,32 +-0,076 dia plated through-holes", tail 1.02 dia, 3.18 tail length, 12.78 overall, 9.6 above the board, 2.29 max stroke, 1.14 mid stroke; pdf page 42 (19.76): the matching 858-10 flat-face target connectors, "2,54 dia minimum solder pads" for the surface-mount targets.

Footprint: pad 1 `thru_hole circle` dia 2.0, drill 1.3: the sheet's .045 in = 1.143 mm minimum hole plus 0.1 mm gives 1.243, rounded up to 1.3, which also lies inside the 1.32 +-0.076 mm (1.244 to 1.396) that the strip page specifies for the same contact; ring 0.35 mm. Courtyard: circle dia 3.7 (flange 3.175 + 2 x 0.25 = 3.675). Silk: circle dia 3.5, just outside the flange. Fab: the flange (dia 3.175) and the tail (dia 1.016). No pin 1 mark: a single round pin has no orientation. Recommended pitch between adjacent pins: 4.0 mm, the series 858 grid (flanges then clear each other by 0.82 mm, the courtyards by 0.3 mm). Heights for the mechanical stack: 9.60 mm free, 8.46 mm at mid stroke (the design point), 7.31 mm fully compressed, tail 3.18 mm below the board.

## 6. Mill-Max_0858_target (written, 1 pad)

Pad 1 `smd circle` dia 4.2 (flange 3.175 + 1.0 = 4.175, rounded to 4.2) on F.Cu and F.Mask, no paste. Silk circle dia 4.8, courtyard circle dia 4.7 (pad + 0.25), fab: the pad outline and the plunger tip dia 1.27 (.050 in). Attributes `smd exclude_from_bom exclude_from_pos_files`, since it is bare copper on the dock's raised block. With the 1.27 tip, a radial misalignment of up to 1.47 mm keeps the tip on the disc.

## 7. LTC2954 in TSOT-23-8 (no file; KiCad Package_TO_SOT_SMD:TSOT-23-8 matches)

Source: `ltc2954.pdf` page 16 (TS8 package, LTC DWG 05-08-1637 Rev A, JEDEC MO-193 per note 6): body 2.90 BSC x 1.50 to 1.75, height 1.00 max, lead span 2.80 BSC, pitch 0.65 BSC, lead width 0.22 to 0.36, foot 0.30 to 0.50 ref; recommended solder pads 0.40 max wide x 1.22 ref long, rows 2.62 ref apart (outer extent 3.85 max, inner gap 1.4 min).

KiCad TSOT-23-8 (descr: MO-193 variant BA, IPC gull-wing generator): eight pads 1.325 x 0.50 at x = ±1.1375, y = ±0.325 and ±0.975; pitch 0.65, rows 2.275 apart, outer extent 3.60, inner gap 0.95, pin 1 top left counter-clockwise (1 to 4 down the left, 5 to 8 up the right). Pitch, lead span and body match the LTC drawing. The pads differ from LTC's suggestion: 0.10 wider (0.50 against 0.40 max), inner edge 0.225 further under the body (0.475 against 0.70) and toe 0.125 shorter (1.80 against 1.925); both cover the 0.30 to 0.50 foot whose tip is at 1.40. Verdict: matches, use the library part, no file written.

## 8. TPS259571 in DSG0008A (no file; KiCad Package_SON:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm matches)

Source: `tps2595.pdf` page 46 (package outline DSG0008A, TI drawing 4218900/E 08/2022), page 47 (example board layout, 20X), page 48 (example stencil): body 2.1/1.9 square (2.0 nominal), 0.8 max height, eight terminals at 0.5 pitch, 0.4/0.2 long, 0.32/0.18 wide, exposed thermal pad 0.9 +-0.1 x 1.6 +-0.1 as pin 9, pin 1 ID at the bottom left of the bottom view (top left of the land pattern); land pattern: 8X (0.5) x (0.25) pads, 6X (0.5) pitch, pad centre lines (1.9) apart, exposed pad (0.9) x (1.6), dia 0.2 vias; stencil: the exposed pad as two openings 0.9 x 0.45 and 0.9 x 0.7 (87 percent). The `tps2596.pdf` on file is the TPS259620/21 revision in the DDA SO-PowerPAD package (its mechanical pages 44 to 46 show DDA only, no DSG drawing), and TPS259571 is not named in either file; the DSG0008A drawing of the TPS2595 sheet is the package drawing used.

KiCad footprint: pads 0.60 x 0.25 at x = ±0.95, y = ±0.25 and ±0.75 (pitch 0.5, centre lines 1.9 apart, 0.1 longer than TI's 0.5: inner edge 0.65 against 0.70, outer 1.25 against 1.20), pad 9 0.9 x 1.6, paste as two 0.73 x 0.64 openings (65 percent against TI's 87), pin 1 top left, 1 to 4 down the left, 5 to 8 up the right. Verdict: matches, use the library part (the `_ThermalVias` variant adds vias under pad 9), no file written.

## Summary

| Footprint | Source document, page | Pads | Status |
|---|---|---|---|
| Texas_RQQ0011A_VQFN-HR-11_2.5x3mm | tps61288.pdf p27 outline, p28 land pattern, p29 stencil (TI 4225610/A) | 11 copper + 4 paste-only | written |
| Texas_RQM0029A_QFN-29_4x4mm | bq25792.pdf p140 to 142 (TI 4225253/A; bq25798.pdf p148 to 150 identical) | 29 | written |
| (USB2517i QFN-64 9x9 P0.5) | usb2517-datasheet-DS00001598C-lcsc.pdf p53 outline, p54 land pattern | 64 + EP | KiCad library part matches: QFN-64-1EP_9x9mm_P0.5mm_EP4.7x4.7mm (none of EP3.4/3.8/4.1/4.35 does), no file |
| Radiall_SMPMAX_R222M00720 | radiall-R222M00720-tds.pdf p1 (issue 1107 B) | 5 (1 centre, 4 x pad 2) | written |
| Mill-Max_0858_power_pin | Mill-Max catalogue page 28 (mmpower-07.png) plus 004M-022M.pdf pdf p41/p42 (series 858) | 1 | written |
| Mill-Max_0858_target | derived from the 0858 flange (3.18 + 1.0) | 1 | written |
| (LTC2954 TSOT-23-8) | ltc2954.pdf p16 (LTC 05-08-1637 Rev A) | 8 | KiCad library part matches: Package_TO_SOT_SMD:TSOT-23-8, no file |
| (TPS259571 DSG0008A) | tps2595.pdf p46 to 48 (TI 4218900/E); tps2596.pdf on file has no DSG drawing | 8 + EP | KiCad library part matches: Package_SON:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm, no file |
