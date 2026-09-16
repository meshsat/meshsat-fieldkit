# JLCPCB impedance-controlled stackups

**Source.** https://jlcpcb.com/impedance, fetched 16 September 2026 by the runner and transcribed. This is the
document the two stackups `tools/stackup_write.py` writes come from; the numbers had been in a code comment
citing a reading of 8 September 2026 with no file behind it.

**What it is for.** Rules STK-001 (the stackup is declared and feasible) and IMP-001 (an impedance target is
feasible). Every dielectric constant and every layer thickness this project's stackups use must be a row here
or a row of the capability document beside it.

**The same caution as its companion.** A fabricator's stackup page is not a controlled document and can change
without notice. The date it was read travels with every number taken from it, and a board ordered on these
numbers should have them confirmed on the order.

## JLC04161H-7628, four layers, 1.6 mm

| layer | material | thickness (mm) | Dk |
|---|---|---|---|
| top | copper | 0.035 | |
| prepreg | 7628 | 0.2104 | 4.4 |
| inner L2 | copper | 0.0152 | |
| core |  | 1.065 | 4.6 |
| inner L3 | copper | 0.0152 | |
| prepreg | 7628 | 0.2104 | 4.4 |
| bottom | copper | 0.035 | |

## JLC06161H-3313, six layers, 1.6 mm

| layer | material | thickness (mm) | Dk |
|---|---|---|---|
| top | copper | 0.035 | |
| prepreg | 3313 | 0.0994 | 4.1 |
| inner L2 | copper | 0.0152 | |
| core |  | 0.55 | 4.6 |
| inner L3 | copper | 0.0152 | |
| prepreg | 2116 | 0.1088 | 4.16 |
| inner L4 | copper | 0.0152 | |
| core |  | 0.55 | 4.6 |
| inner L5 | copper | 0.0152 | |
| prepreg | 3313 | 0.0994 | 4.1 |
| bottom | copper | 0.035 | |

## The two-layer case

This page carries no two-layer impedance stackup, because impedance control is offered on four layers and
above (the capability document's "impedance control layers" row). The two-layer boards in this project take
their core dielectric constant from the capability document's own FR-4 row, **4.5**, and neither of them
declares an impedance target.
