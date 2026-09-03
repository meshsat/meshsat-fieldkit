# MeshSat field-kit carrier boards, review prints (generated)

Print everything at 100 % scale (no fit-to-page). The 1:1 sheets are for laying the real devices on paper; the copper sheets and the assembly drawings are for the design review (appendix section 21.3 / 22.4: the six order-gate items are the agenda).

## PCB-A POWER + I/O Rev A (A17), folder `PCB-A-POWER-A17/`, 285 x 160 mm, 4 layers

- `pcb-a-power-1to1-top.pdf`, `pcb-a-power-1to1-bottom-mirrored.pdf`: 1:1 device-layout sheets (bottom is mirrored so it reads through the paper); lay the real devices on them
- `pcb-a-power-assembly-top.pdf`, `pcb-a-power-assembly-bottom-mirrored.pdf`: fab drawings with reference designators, pad outlines and pad numbers; DNP parts crossed out
- `pcb-a-power-copper-layers.pdf`: one page per copper layer (F.Cu, In1.Cu, In2.Cu, B.Cu) with the outline; check the planes, the USB pairs, the cell straps and the boost loop here
- `pcb-a-power-render-top-A4.png`, `pcb-a-power-render-bottom-A4.png`: 3D renders at A4 300 dpi; the small `-render-*.png` are the originals
- `pcb-a-power-schematic.pdf`: full schematic; `pcb-a-power-drc.rpt`: the DRC report of the exported board

## PCB-B COMPUTE Rev A (B11), folder `PCB-B-COMPUTE-B11/`, 245 x 170 mm, 4 layers

- `pcb-b-compute-1to1-top.pdf`, `pcb-b-compute-1to1-bottom-mirrored.pdf`: 1:1 device-layout sheets (bottom is mirrored so it reads through the paper); lay the real devices on them
- `pcb-b-compute-assembly-top.pdf`, `pcb-b-compute-assembly-bottom-mirrored.pdf`: fab drawings with reference designators, pad outlines and pad numbers; DNP parts crossed out
- `pcb-b-compute-copper-layers.pdf`: one page per copper layer (F.Cu, In1.Cu, In2.Cu, B.Cu) with the outline; check the planes, the USB pairs, the cell straps and the boost loop here
- `pcb-b-compute-render-top-A4.png`, `pcb-b-compute-render-bottom-A4.png`: 3D renders at A4 300 dpi; the small `-render-*.png` are the originals
- `pcb-b-compute-schematic.pdf`: full schematic; `pcb-b-compute-drc.rpt`: the DRC report of the exported board

## PCB-C CONTROL PANEL Rev A (C4), folder `PCB-C-DISPLAY-C4/`, 442 x 311 mm, 2 layers

- `pcb-c-display-1to1-top.pdf`, `pcb-c-display-1to1-bottom-mirrored.pdf`: 1:1 device-layout sheets (bottom is mirrored so it reads through the paper); lay the real devices on them
- `pcb-c-display-assembly-top.pdf`, `pcb-c-display-assembly-bottom-mirrored.pdf`: fab drawings with reference designators, pad outlines and pad numbers; DNP parts crossed out
- `pcb-c-display-copper-layers.pdf`: one page per copper layer (F.Cu, B.Cu) with the outline; check the planes, the USB pairs, the cell straps and the boost loop here
- `pcb-c-display-render-top-A4.png`, `pcb-c-display-render-bottom-A4.png`: 3D renders at A4 300 dpi; the small `-render-*.png` are the originals
- `pcb-c-display-schematic.pdf`: full schematic; `pcb-c-display-drc.rpt`: the DRC report of the exported board

### Official Raspberry Pi documents for the Touch Display 2 (7-inch), kept in `v2/vendor/td2/` (not copied into this folder)

Raspberry Pi publishes no schematic for the Touch Display 2 (the driver board is closed) and no separate mechanical-drawing PDF; the drawing is a page inside the 2024 and 2025 product-brief editions, and the 3D geometry is the STEP model. The 2026 editions ("7-inch Portrait") carry photos, specification and safety text only.

- `raspberry-pi-touch-display-2-7inch-RP-009154-DD-1.step`: the official 7-inch STEP model. PCB-C is derived from it (appendix 14.1, 14.5, 14.6).
- `RPi-Touch-Display-2-product-brief-2025-08-(design-source).pdf`: the edition whose page 4 drawing was read with the STEP.
- `RP-008387-DS-1-touch-display-2-product-brief.pdf` (November 2024): the original edition, same drawing numbers.
- `RP-009106-MM-8-touch-display-2-product-brief.pdf` (June 2026), `RP-010429-MM-1-touch-display-2-7-inch-product-brief.pdf` (August 2026) and `RPi-Touch-Display-2-product-brief-2026-08-datasheets.raspberrypi.com.pdf`: current editions, no drawing.

Sources: https://pip.raspberrypi.com/categories/1083-raspberry-pi-touch-display-2 and https://datasheets.raspberrypi.com/display/touch-display-2-product-brief.pdf (checked 2 Sep 2026).

## PCB-C SPACER RING Rev A (R1), folder `PCB-C-RING-R1/`, 106 x 54 mm, 2 layers

- `pcb-c-ring-1to1-top.pdf`, `pcb-c-ring-1to1-bottom-mirrored.pdf`: 1:1 device-layout sheets (bottom is mirrored so it reads through the paper); lay the real devices on them
- `pcb-c-ring-assembly-top.pdf`, `pcb-c-ring-assembly-bottom-mirrored.pdf`: fab drawings with reference designators, pad outlines and pad numbers; DNP parts crossed out
- `pcb-c-ring-copper-layers.pdf`: one page per copper layer (F.Cu, B.Cu) with the outline; check the planes, the USB pairs, the cell straps and the boost loop here
- `pcb-c-ring-render-top-A4.png`, `pcb-c-ring-render-bottom-A4.png`: 3D renders at A4 300 dpi; the small `-render-*.png` are the originals
- `pcb-c-ring-drc.rpt`: DRC report (mechanical board, no schematic)

## PCB-D APRS Rev A (D5), folder `PCB-D-APRS-D5/`, 80 x 62 mm, 4 layers

- `pcb-d-aprs-1to1-top.pdf`, `pcb-d-aprs-1to1-bottom-mirrored.pdf`: 1:1 device-layout sheets (bottom is mirrored so it reads through the paper); lay the real devices on them
- `pcb-d-aprs-assembly-top.pdf`, `pcb-d-aprs-assembly-bottom-mirrored.pdf`: fab drawings with reference designators, pad outlines and pad numbers; DNP parts crossed out
- `pcb-d-aprs-copper-layers.pdf`: one page per copper layer (F.Cu, In1.Cu, In2.Cu, B.Cu) with the outline; check the planes, the USB pairs, the cell straps and the boost loop here
- `pcb-d-aprs-render-top-A4.png`, `pcb-d-aprs-render-bottom-A4.png`: 3D renders at A4 300 dpi; the small `-render-*.png` are the originals
- `pcb-d-aprs-schematic.pdf`: full schematic; `pcb-d-aprs-drc.rpt`: the DRC report of the exported board

## PCB-E1 DOCK Rev A (E1), folder `PCB-E1-DOCK-E1/`, 250 x 44 mm, 2 layers

- `pcb-e1-dock-1to1-top.pdf`, `pcb-e1-dock-1to1-bottom-mirrored.pdf`: 1:1 device-layout sheets (bottom is mirrored so it reads through the paper); lay the real devices on them
- `pcb-e1-dock-assembly-top.pdf`, `pcb-e1-dock-assembly-bottom-mirrored.pdf`: fab drawings with reference designators, pad outlines and pad numbers; DNP parts crossed out
- `pcb-e1-dock-copper-layers.pdf`: one page per copper layer (F.Cu, B.Cu) with the outline; check the planes, the USB pairs, the cell straps and the boost loop here
- `pcb-e1-dock-render-top-A4.png`, `pcb-e1-dock-render-bottom-A4.png`: 3D renders at A4 300 dpi; the small `-render-*.png` are the originals
- `pcb-e1-dock-schematic.pdf`: full schematic; `pcb-e1-dock-drc.rpt`: the DRC report of the exported board

## PCB-E2 RF JUNCTION Rev A (E2), folder `PCB-E2-RFJUNCTION-E2/`, 330 x 32 mm, 2 layers

- `pcb-e2-rfjunction-1to1-top.pdf`, `pcb-e2-rfjunction-1to1-bottom-mirrored.pdf`: 1:1 device-layout sheets (bottom is mirrored so it reads through the paper); lay the real devices on them
- `pcb-e2-rfjunction-assembly-top.pdf`, `pcb-e2-rfjunction-assembly-bottom-mirrored.pdf`: fab drawings with reference designators, pad outlines and pad numbers; DNP parts crossed out
- `pcb-e2-rfjunction-copper-layers.pdf`: one page per copper layer (F.Cu, B.Cu) with the outline; check the planes, the USB pairs, the cell straps and the boost loop here
- `pcb-e2-rfjunction-render-top-A4.png`, `pcb-e2-rfjunction-render-bottom-A4.png`: 3D renders at A4 300 dpi; the small `-render-*.png` are the originals
- `pcb-e2-rfjunction-drc.rpt`: DRC report (mechanical board, no schematic)

## Review agenda (appendix 21.3 / 22.4)

1. PCB-A: BQ25601 pin map (PSEL on R45/R46, /QON on TP11), 103AT-2 thermistor network, CSD17303Q5 cell switches, boost/buck chain on shore power.
2. PCB-B: no F1 (both XH inputs on +5V), 2 A polyfuse + TPS22810 per channel, T-Beam 1W strip and the dual SDR bay, USB pairs.
3. PCB-D: STM32F302CBT6 (128 KB) for the AIOC firmware, TPS61089 boost at 7.6 V with the 100k ILIM, DMR858M site on sockets and M2.5 x 11 standoffs (rows 36.15 mm, pin 1 north-east), heatsink clearance in the bottom bay (about 35 mm).
4. PCB-C: window and tab positions against the Touch Display 2.

