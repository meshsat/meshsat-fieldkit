# JLCPCB rigid PCB manufacturing capabilities

**Source.** https://jlcpcb.com/capabilities/pcb-capabilities, fetched 16 September 2026 by the runner and
transcribed row by row. This replaces `v2/vendor/seals/jlcpcb-pcb-capabilities-page.txt` of 4 September 2026,
which is a JavaScript-blocked page scrape carrying no capability data at all, filed in the wrong folder and
read by nothing.

**What it is for.** Rules VIA-001 and VIA-002 (via and annular ring), RTE-001 (geometry a fabricator will
build), STK-001 (the stackup is declared and feasible) and IMP-001 (an impedance target is feasible) all
depend on numbers that until today lived nowhere in this tree. Every limit either of those rules enforces must
cite a row of this file.

**Caution that belongs with it.** This is a fabricator's own marketing-side capability page, not a controlled
document with a revision number. It is the best authority this project can obtain without a quotation, it can
change without notice, and a rule that depends on a row here records the date it was read. Where a row does
not cover our case, the rule stays unverified rather than borrowing the nearest number.

## Layers, material and size

| item | value |
|---|---|
| layer count | 1 to 32 |
| FR-4 | Grade A laminates (Nan Ya, KB, Shengyi and others) |
| FR-4 dielectric constant | 4.5 (2-layer), 4.4 (7628 prepreg), 4.1 (3313 prepreg), 4.16 (2116 prepreg) |
| maximum size, 4-layer | 663 x 593 mm standard, 1016 x 596 mm extended |
| maximum size, 6+ layers | 656 x 586 mm |
| minimum size | 3 x 3 mm |
| thickness | 0.4 to 4.5 mm |
| thickness tolerance | +-10% at 1.0 mm and above, +-0.1 mm below |
| dimension tolerance | +-0.1 mm standard; +-0.2 mm regular CNC; +-0.4 mm V-scoring |

## Copper weight

| item | value |
|---|---|
| finished outer copper, 2-layer | 1 oz / 2 oz / 2.5 oz / 3.5 oz / 4.5 oz |
| finished outer copper, multilayer | 1 oz / 2 oz |
| finished inner copper | 0.5 oz / 1 oz / 2 oz |

## Track width and spacing, by copper weight

| item | value |
|---|---|
| 1 oz, 1 and 2 layer | 0.10 / 0.10 mm (4 / 4 mil) |
| 1 oz, multilayer | 0.09 / 0.09 mm (3.5 / 3.5 mil) |
| 2 oz, 2-layer | 0.16 / 0.16 mm (6.5 / 6.5 mil) |
| 2 oz, multilayer | 0.15 / 0.15 mm (6 / 6 mil) |
| 2.5 oz, 2-layer | 0.20 / 0.20 mm (8 / 8 mil) |
| 3.5 oz, 2-layer | 0.25 / 0.25 mm (10 / 10 mil) |
| 4.5 oz, 2-layer | 0.30 / 0.30 mm (12 / 12 mil) |
| track width tolerance | +-20% |

## Holes and vias

| item | value |
|---|---|
| drill diameter, 2+ layers | 0.15 to 6.3 mm |
| drill diameter, 1 layer | 0.30 to 6.3 mm |
| minimum via hole, 2+ layers | 0.15 mm |
| minimum via diameter, 2+ layers | 0.25 mm |
| minimum non-plated hole | 0.50 mm |
| hole size tolerance, through hole | +0.13 / -0.08 mm |
| hole position tolerance | +-0.05 mm |
| average hole plating thickness | 18 um |
| via hole to via hole spacing | 0.20 mm |
| pad hole to pad hole spacing | 0.45 mm |
| **blind and buried vias** | **not supported** |
| backdrill | 4 to 32 layers, thickness 0.8 mm and above, 0.2 to 0.5 mm |

## Annular ring

| item | value |
|---|---|
| PTH annular ring, general | >= 0.20 mm |
| **PTH annular ring, 2-layer 1 oz** | **recommended 0.25 mm or above; absolute minimum 0.18 mm** |
| **PTH annular ring, multilayer 1 oz** | **recommended 0.20 mm or above; absolute minimum 0.15 mm** |
| NPTH pad annular ring | >= 0.45 mm |

**NOT STATED FOR 2 oz.** The annular rows above are given for 1 oz. Boards E5 and P are ordered at 2 oz by
owner ruling 7, so their annular floor is NOT established by this document and their VIA-002 result stays
INCONCLUSIVE until it is asked of the fabricator directly.

## Clearances

| item | value |
|---|---|
| pad to track | 0.10 mm |
| via hole to track | 0.20 mm |
| PTH to track | 0.28 mm |
| NPTH to track | 0.20 mm |
| SMD pad to pad, different nets | 0.15 mm |
| minimum SMD pad | 0.25 x 0.25 mm |
| inner layer via hole to copper | 0.20 mm |
| inner layer PTH pad hole to copper | 0.30 mm |
| same-net track spacing | 0.25 mm |
| BGA pad diameter | 0.20 mm |
| BGA pad to trace | >= 0.10 mm (0.09 mm multilayer) |
| routed board edge to copper | >= 0.20 mm |
| V-cut copper clearance | >= 0.40 mm |

## Solder mask, legend and via treatment

| item | value |
|---|---|
| solder mask | LPI; expansion 1:1; dielectric constant 3.8; ink >= 10 um |
| solder mask opening to neighbouring trace | >= 0.09 mm |
| solder mask bridge, 1 oz | 0.10 mm pad spacing (green, red, yellow, blue, purple); 0.13 mm (black, white) |
| solder mask bridge, 2 oz | 0.20 mm pad spacing, any colour |
| plugged vias | filled with solder mask, up to 0.5 mm diameter, >= 0.35 mm from other openings |
| **via in pad** | **epoxy filled and capped, or copper paste filled and capped; via diameters 0.15 to 0.55 mm** |
| legend line width | >= 0.15 mm |
| legend text height | >= 1.0 mm (40 mil) |
| legend pad to silkscreen | 0.15 mm |
| surface finish | HASL leaded or lead-free, ENIG, OSP |

## Impedance

| item | value |
|---|---|
| impedance control tolerance | +-10% |
| impedance control layer counts | 4, 6, 8, 10 ... 32 |
