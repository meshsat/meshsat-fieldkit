# Battery shortlist: the present cell against higher-energy cells and a complete smart pack (stream l3batt, MESHSAT-1357)

30 September 2026. **Prototype design:** nothing is bought, built or measured. Every figure is labelled:
- **MAKER (page or section):** a maker's sheet, filed in `v2/vendor/battery/` or held back by its terms and fetched by
  `fetch_held_back.py`, each with its line in `v2/vendor/sources.txt`;
- **MODELED:** a1elec's energy model;
- **INFERRED:** a stated method.

Sources: `runtime.out` (usable energy), `lid_21700.out` (lid places) and `load_trace.out` (the load). The kit's
constraints are unchanged throughout: the Peli 1450, HF and the tablet kept (a1mech arrangement A), and the 4S node.

## 1. The makers' cell figures, against what an assembled pack gives

| Cell | Sheet | Capacity and energy, minimum | Nominal V | Size (max), mass (max) | Discharge / charge temperature | Cold figure used |
|---|---|---|---|---|---|---|
| **Samsung SDI INR18650-35E** (present) | Ver. 1.1, filed (`samsung-35e-orbtronic.pdf`) | 3.35 Ah at 0.2C to 2.65 V; **12.06 Wh** at 3.60 V | 3.60 V | 18.55 x 65.25 mm, 50 g | the model's window | -10 C: 0.4124 at 1C (spec 7.5: 40 / 97 %), a lower bound at the kit's 0.2 A a cell |
| **Molicel INR-21700-P45B** | Version 1.2, **filed** | 4300 mAh, **15.5 Wh** | 3.6 V | 21.55 x 70.15 mm, 70 g | -40 to 60 C / 0 to 60 C | about 0.91, read by eye from the Discharge Temperature Characteristics at 4.5 A (about 4.2 Ah at -20 C against 4.6 Ah at 23 C, to 2.5 V; no -10 C curve) |
| **Samsung SDI INR21700-50E** | V1.0 of 11 Jul 2018, **held back** ("Confidential Proprietary") | 4,900 mAh standard (7.2); **17.79 Wh** at 3.63 V; 4,753 mAh rated at 1C | 3.63 V | 21.25 x 70.80 mm, 69.5 g | -20 to 60 C / 0 to 45 C | 0.722 (7.5: -10 C 70 %, 23 C 97 % at 1C) |
| **LG INR21700M50LT** | 2020-LSD-MBD-b00082 of 27 Aug 2020, **held back** (a pre-discussion customer copy) | **17.6 Wh** (2.1) | 3.69 V | 21.44 x 70.60 mm, 68.2 g (TBD) | -20 to 55 C | 0.70 (4.2: -10 C at least 70 % of Whmin, 0 C 80 %) |

**Cell energy is not pack energy.** The present pack's 60 cells hold 723.6 Wh at their minimum (12.06 Wh a cell). What
reaches the kit, aged to 80 % and at +20 C, is **544.4 Wh**: 9.07 Wh a cell, 75 % (MODELED). The losses are:
- the 3.00 V graceful line with its 5 % reserve (0.937 of the cell's capacity at the kit's current);
- ageing (0.80);
- the lid path's small loss.

At -10 C the same pack gives 224.5 Wh (the 35E's 0.4124 lower bound).

**Not included in this pass:**
- **A higher-capacity 18650:** no maker's sheet above the 35E's 3.35 Ah minimum was read.
- **A LiFePO4 pack:** the brief marked it optional. At 3.2 V a cell it would also not suit the 4S node's charger settings.

## 2. Each candidate in the kit (HF and the tablet kept), at PS-IDLE-SPEC 42.8 W, aged 80 %, to the kit's shutdown

| Candidate | Arrangement | Placement (records) | Usable Wh, +20 C / -10 C | Battery-only hours, +20 C / -10 C | Mass | Electrical compatibility | Charger and protection changes | Cost and availability (30 Sep 2026, a distributor page) |
|---|---|---|---|---|---|---|---|---|
| **35E, D-06's pack alone** | 4S3P, 12 cells, the east pocket | ESTABLISHED: the ruled block, CON-006 | 107.9 / 44.5 | **2.52 / 1.04** | 0.60 kg of cells | the node's 12.0 to 16.8 V | none (D-06 as ruled) | Battery Junction: USD 8.25 a cell (7.65 at 100+), In Stock |
| **35E, Option A(i) with both functions kept** | base 4S6P (both base pockets) + lid 4S9P: 60 cells | lid: a1mech arrangement A, 39 places (36 used), module 24.0 mm one layer, 40.06 two; lid 4.53 kg in all with the QMX set, the tablet and the shell. Base: M4a, M5 and M6w OPEN, the rest MET (a1mech 6) | **544.4 / 224.5** | **12.71 / 5.24** | 3.0 kg of cells | as the node's | as a1elec drafts: board PL, U3B, the lid path (LM74700-Q1 and LM5069, 8.7 to 11.0 A) | as above |
| **P45B in the lid** | base 4S6P of 35E + lid 4S6P of P45B | lid: 27 places, 24 used (`lid_21700.out`, INFERRED: the generator with only the cell's size changed). Two layers need 45.66 mm against the lid's 44.39 at the worst, so the second layer is refused. Base: see the note below | 496.0 / 342.7 | 11.58 / 8.00 | lid 4.46 kg in all | 4.2 V NMC-class, 2.5 V floor: as the node's | the lid gauge's chemistry and capacity data for a new cell (BQ4050 image, GAUGE.md); U3B's 7.936 A is 1.32 A a cell over 6P, inside its 4.5 A standard charge; REQ-075's 1.02 A a cell is written for the 35E's block | Battery Junction: USD 8.75 (7.05 at 400+), "EXTENDED MANUFACTURER DELAYS" |
| **50E in the lid** | the same, lid 4S6P of 50E | 27 places, 24 used (INFERRED as above) | 537.0 / 320.0 | 12.54 / 7.47 | lid 4.44 kg | as above | as above; its standard charge 0.5C (2,450 mA), maximum 4,900 mA, window 0 to 45 C | Battery Junction: USD 7.59 (6.77 at 400+), In Stock |
| **M50LT in the lid** | the same, lid 4S6P of M50LT | 27 places, 24 used (INFERRED) | 533.6 / 310.7 | 12.46 / 7.26 | lid 4.44 kg | as above | as above. LG's sheet: "LGC strongly prohibits the sale or distribution of the product ... to any individual end-users or open markets that were not approved by LGC" | IMR Batteries: USD 4.99, "Sold out"; Voltaplex: "In stock", no price shown |
| **Inspired Energy NH2054HD34, a complete smart pack: PROPOSAL** (outside the case) | 4S2P of 18650 (3.4 Ah typical cells), 14.4 V; one or two packs beside the kit | **no place in the Peli 1450** with both functions kept: an external battery arrangement | 67.2 a pack at +20 C (rated 6.136 Ah x 14.4 V to 11.0 V, 3.1.2, x 0.80 x 0.95); at -10 C 27.7 (the 35E's bound; no cold figure in its text). The kit's 3.00 V line (12.0 V) ends before the pack's 11.0 V: about 66 Wh at the 35E's 0.937 fraction (INFERRED) | A(i) + 1 pack: 14.28 / 5.89; + 2 packs: 15.85 / 6.54 | 0.435 kg a pack; 150.37 x 77.39 x 22.51 mm (p.24 drawing) | a 4S Li-ion pack, 16.8 V charge, SMBus SBS 1.1; **discharge over-current trips at 8.25 A**: it cannot carry a PA key-down alone (the kit then draws 8.5 to 11.3 A at 14.4 V, pwr_budget.out, the PA at 75 to 113 W over PS-IDLE-SPEC) | a way into the kit (a wall connector); a join at VBAT limited under 8.25 A, or the 9 to 36 V DC entry, which **meets D-20's "requiring it overnight is not an acceptable substitute"**; a charge path that follows its SMBus requests; the host's SMBus reading | no public price; distributors quote on request (Onrion, Ontrium listings); resale listings exist |

**The loads' minimum inputs.** Every candidate is a 4S pack ending at the kit's 12.0 V line (3.00 V a cell under load),
above the gauge's 2.50 V CUV, the second level's 2.25 V and the lid path's 9 V floor. Whether every load converter runs
down to 12.0 V at the node is **not established** by any record read here: the same obligation as condition 4 of
l3feas's pass line. It is the same for every candidate.

**The base pockets and 21700 cells (INFERRED, not shown).** The ruled base block is 4S3P: two cells along the axis, three
across, two layers. In 21700 cells it grows by about:
- 9.8 mm along the axis (2 x 70.15 + 3.0 against 133.5);
- 9.0 mm across (3 x 21.55 + 1.0 against 56.65);
- 6.0 mm in height.

Three of a1mech's base rows (section 6, at the worst, less their 1.0 minimum) leave less room than that:

| Row | Room left | Growth needed |
|---|---|---|
| M5 east, along the axis | 0.77 mm | 9.8 mm |
| M4b, across | 6.38 mm | 9.0 mm |
| M6 east, height | 2.66 mm | 6.0 mm |

**So a 21700 block in the ruled orientation does not fit the base pockets.** Another orientation is not examined; that
would be a mechanical task.

## 3. What the shortlist shows

- **No cell change adds energy inside the Peli 1450 with HF and the tablet kept.**
  - The 21700 cells hold more energy each (15.5 to 17.8 Wh against 12.06 Wh). But the lid takes only one layer of them:
    24 cells against the 35E's 36.
  - At +20 C every 21700 lid gives less than the present 35E lid: 496 to 537 Wh against 544 Wh for the kit (MODELED and
    INFERRED).
  - They do better only at -10 C, where the 35E's sheet gives just one conservative 1C point.
- **A complete smart pack fits only outside the case** (a PROPOSAL). Each adds about 58 to 67 Wh usable, depending on
  its temperature. It needs a connector, a join, a charge path and the D-20 clause resolved, and its 8.25 A trip keeps
  it from carrying transmit peaks alone.
- **The present cell (35E) stays the best in-case choice on the evidence held.** The upgrade that a 72 hour (or a 48
  hour) requirement asks for is therefore a question of arrangement, not of cell: see `COMPARISON.md`.

The author's analysis, AI arithmetic. Not a qualified review and not the independent check.
