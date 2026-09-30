# PLANES: M1's deployment condition on the full plane grid, for the two lid options (stream l3plane, MESHSAT-1357)

30 September 2026, branch `fnd/l3plane` from `fnd/int16` at `d2084904`. **Evidence for the owner's decision of M1's
deployment condition (which planes the operator may lay the array on), for closing layer 3. It is not a decision: no
requirement, record or decision is changed (`pcb_requirements.yaml` is untouched).** AI arithmetic on the record's model,
not a qualified review. Prototype design: nothing is bought, built, powered or measured. **Every figure on this page is
MODELED on the reference day of SC-37 (the September mean day at Leiden, PVGIS), and every condition is INFERRED from the
model's grid.** All figures are printed by `plane_grid.py` into `plane_grid.out` (section named); this page transcribes them.

**Second issue, 30 September 2026.** The word "adverse" is withdrawn from this page and from `plane_grid.out`: the case it
named is **WAB, the worst array build** (the worst panel fit, set point, cell heat and lead) on the SAME September mean day.
It is not a weather case, and no worse-weather case is established here. No figure moved. **The bus basis of this page
(the model's 20.7 V, and the V20 and V19 sensitivities) is superseded by `ENERGY-BASIS.md`**, which establishes the charge
bus's range from the design and the makers' pages and gives the corrected comparison table for the owner's decisions.

**Third issue, 30 September 2026 (CHECK-1 minor 7).** Every derived condition on this page (sections 2.4, 3.4 and 4) is
marked SUPERSEDED and was a proposal only: none may be read into the owner's table. At the established worst inputs the
4S14P lid has no band at all.

## 0. Tools, outputs and commands

| File | What it is |
|---|---|
| `plane_grid.py` (new) | runs the grid; imports `a1int/reconcile_lid_panel.py`, `a1solar/energy_runs.py`, `s119/reconcile_s119.py` and `a1elec/energy_two_pack.py`, each pinned by sha256; refuses (exit 4) unless section 0's reproductions hold |
| `plane_grid.out` (new) | its output, deterministic (no date, host or absolute path) |
| `a1int/reconcile_lid_panel.py` (changed) | `run()` takes an optional `prof`, the hourly irradiance of the day in place of the model's own 40/0 profile; `main()` does not pass it. sha256 `9ebb0e5a619dba98` to `031ab3f99779f657`. Nothing else in the file changed but one docstring paragraph saying so |

Commands, from the repository root (the three SunPower documents of `a1solar/fetch_held_back.py` present, ignored, under
`v2/vendor/solar/held/`; `array_calc.py` refuses one that is present and not the pinned file, and accepted them):

```
python3 v2/docs/records/l3plane/plane_grid.py > v2/docs/records/l3plane/plane_grid.out
python3 v2/docs/records/a1int/reconcile_lid_panel.py | cmp - v2/docs/records/a1int/reconcile_lid_panel.out
python3 v2/docs/records/a1solar/energy_runs.py | cmp - v2/docs/records/a1solar/energy_runs.out
```

**No committed output moved.** `reconcile_lid_panel.out` was re-run after the change and is byte identical (`cmp`
silent), as is `energy_runs.out` (whose script is not changed). `reconcile_s119.py` neither imports nor reads the changed
script (it reads `reconcile_lid_panel.out`, unchanged); its section 7 is reproduced by `plane_grid.out` 0c. And
`plane_grid.out` section 0 proves that the grid runs the committed model: **0a** the eight rows of
`reconcile_lid_panel.out` for 4S14P and 4S15P (B and C, U3 at 6.1 and 6.0 A) reproduced byte for byte through the new
`prof` on the 40/0 anchor; **0b** all 50 plane rows of `energy_runs.out` section 6 (the 4S12P lid) reproduced byte for
byte; **0c** all 13 plane rows of `reconcile_s119.out` section 7 reproduced byte for byte.

## 1. What is run

The model is `reconcile_lid_panel.py`'s: a1elec's `energy_two_pack.py` (second issue) with the lid's parallel count, the
ratio and U3's input limit set; 400 Wp (four Renogy RNG-100DB-H in 2S2P), the 200 W stage, entry E2's front end, the
base at +20 C, **the lid at 13.23 C** (the September mean day's minimum air), both start hours, 42.8 W, aged 80 percent,
U3 at 0.979 and U3B at code 62 (7.936 A) and 0.972 (stream s119's rows). Each of the 50 planes (slopes 0 to 70 degrees in
10 degree steps, azimuths 45 degrees east to 45 degrees west in 15 degree steps, flat once) runs on its own PVGIS DRcalc
September mean day, scaled by the model's factor 1.007820, with that plane's own ratios B (TYP, the typical array build) and C (WAB, the worst array build) from
`energy_runs.py`. A plane MEETS when both start hours end the 72 hours without a stop. The ratios are carried unrounded,
as `energy_runs.py` and `reconcile_s119.py` carry them; at 40/0 that reads 85.4 Wh (4S14P, C, case P) where
`reconcile_lid_panel.out`, which reads them rounded to four places, prints 85.5 Wh (4S15P: 116.6 Wh in both).

| Case | What changes |
|---|---|
| **P** (primary) | U3's input limit at its minimum 6.1 A, U3B at its carried 0.972: `reconcile_lid_panel.py`'s model as committed |
| I | U3 at the 6.0 A bracket |
| H | U3 at 6.1 A, U3B hour by hour on its TI curve (`reconcile_s119.py`'s `run()` and `curve()`), that record's most faithful reading of U3B |
| V20 | **a sensitivity this stream adds (INFERRED)**: U3 at 6.1 A with the charge bus at the front end's nominal regulation, 20.000 V (122.0 W into U3) |
| V19 | the same at the low end of the bus's DC band, 19.080 V (116.4 W) |

**Why V20 and V19.** `energy_two_pack.py` turns U3's input current limit into power at `V_BUS20` = 20.7 V (126.3 W at
6.1 A). Stream s120's `vbus20_bound.out` section 2 (parsed by the script) prints the front end's nominal regulation as
20.000 V and its DC band as 19.080 to 20.960 V (19.326 to 20.694 V with the printed 1 percent alone; that point is not
run). A current limit at a lower bus voltage is less power, so the model's 20.7 V is its most favourable bus. The model is
not edited: the case passes the current that gives the same power at 20.7 V (5.8937 A and 5.6226 A).

**The floor.** A conservative condition counts a grid point only if every lowest store in it is above 4.2 Wh, the larger
drop `reconcile_lid_panel.out`'s NOTES print for a 0.01 h step in place of the model's hourly one (its check, at 40/0 and
the second issue's settings; parsed by the script). It is a floor against the model's own step, not a bound.

## 2. 4S14P lid, the tablet out of the lid (4S20P in all)

### 2.1 The grid, case P (`plane_grid.out` 1.1 and 1.2): lowest store of both packs, B TYP / C WAB, Wh; bold = meets in both; azimuth negative east of south

| slope \ azimuth | -45 | -30 | -15 | +0 | +15 | +30 | +45 |
|---|---|---|---|---|---|---|---|
| 0 (flat) |  |  |  | NOT MET / NOT MET |  |  |  |
| 10 | 36.3 / NOT MET | 57.1 / NOT MET | 72.4 / NOT MET | 75.4 / NOT MET | 75.0 / NOT MET | 67.2 / NOT MET | 53.2 / NOT MET |
| 20 | 46.4 / NOT MET | **79.6 / 9.2** | **90.4 / 44.6** | **95.1 / 59.8** | **95.5 / 52.8** | **96.8 / 37.0** | **82.6 / 2.7** |
| 30 | 44.1 / NOT MET | **82.9 / 20.9** | **94.6 / 64.0** | **94.7 / 79.7** | **95.4 / 79.8** | **95.5 / 58.7** | **79.1 / 8.2** |
| 40 | 22.8 / NOT MET | **74.9 / 10.7** | **94.8 / 66.3** | **93.7 / 85.4** | **95.2 / 82.3** | **92.2 / 56.4** | **72.9 / 6.7** |
| 50 | NOT MET / NOT MET | 50.2 / NOT MET | **91.6 / 52.1** | **92.0 / 80.4** | **94.9 / 76.2** | **83.7 / 37.6** | 42.3 / NOT MET |
| 60 | NOT MET / NOT MET | 12.8 / NOT MET | **77.8 / 20.4** | **89.8 / 67.2** | **90.0 / 52.1** | 57.2 / NOT MET | NOT MET / NOT MET |
| 70 | NOT MET / NOT MET | NOT MET / NOT MET | 37.1 / NOT MET | **78.8 / 25.7** | **70.8 / 7.0** | 6.9 / NOT MET | NOT MET / NOT MET |

### 2.2 The grid, cases I and V20 (same layout)

Case I, U3 at the 6.0 A bracket:

| slope \ azimuth | -45 | -30 | -15 | +0 | +15 | +30 | +45 |
|---|---|---|---|---|---|---|---|
| 0 (flat) |  |  |  | NOT MET / NOT MET |  |  |  |
| 10 | 19.5 / NOT MET | 38.5 / NOT MET | 54.7 / NOT MET | 65.4 / NOT MET | 62.5 / NOT MET | 52.1 / NOT MET | 39.4 / NOT MET |
| 20 | 28.5 / NOT MET | 64.0 / NOT MET | **83.5 / 26.0** | **93.9 / 44.8** | **95.5 / 39.7** | **87.3 / 22.1** | 66.1 / NOT MET |
| 30 | 25.5 / NOT MET | **74.5 / 5.3** | **91.9 / 45.3** | **94.7 / 71.6** | **95.4 / 71.6** | **95.5 / 42.6** | 63.1 / NOT MET |
| 40 | 4.1 / NOT MET | 57.0 / NOT MET | **94.8 / 47.6** | **93.7 / 76.1** | **95.2 / 75.5** | **88.5 / 40.0** | 55.5 / NOT MET |
| 50 | NOT MET / NOT MET | 27.9 / NOT MET | **87.3 / 33.4** | **92.0 / 71.8** | **94.9 / 64.3** | **69.1 / 19.9** | 23.6 / NOT MET |
| 60 | NOT MET / NOT MET | NOT MET / NOT MET | **71.4 / 1.7** | **89.8 / 56.3** | **89.7 / 36.3** | 37.0 / NOT MET | NOT MET / NOT MET |
| 70 | NOT MET / NOT MET | NOT MET / NOT MET | 18.5 / NOT MET | **70.0 / 10.8** | 54.8 / NOT MET | NOT MET / NOT MET | NOT MET / NOT MET |

Case V20, U3 at 6.1 A with the bus at its nominal 20.0 V (122.0 W):

| slope \ azimuth | -45 | -30 | -15 | +0 | +15 | +30 | +45 |
|---|---|---|---|---|---|---|---|
| 0 (flat) |  |  |  | NOT MET / NOT MET |  |  |  |
| 10 | NOT MET / NOT MET | 18.6 / NOT MET | 34.8 / NOT MET | 47.7 / NOT MET | 46.7 / NOT MET | 37.5 / NOT MET | 23.5 / NOT MET |
| 20 | 8.6 / NOT MET | 44.1 / NOT MET | **72.9 / 6.1** | **82.7 / 28.9** | **83.3 / 23.8** | **75.9 / 6.2** | 48.9 / NOT MET |
| 30 | 2.0 / NOT MET | 54.4 / NOT MET | **85.0 / 25.5** | **94.4 / 57.2** | **93.3 / 51.3** | **86.8 / 22.8** | 41.1 / NOT MET |
| 40 | NOT MET / NOT MET | 33.2 / NOT MET | **87.2 / 27.8** | **93.7 / 66.4** | **95.2 / 56.5** | **74.7 / 20.1** | 31.7 / NOT MET |
| 50 | NOT MET / NOT MET | 4.1 / NOT MET | **80.0 / 13.6** | **92.0 / 61.2** | **94.9 / 45.8** | 50.6 / NOT MET | 3.8 / NOT MET |
| 60 | NOT MET / NOT MET | NOT MET / NOT MET | 52.6 / NOT MET | **78.2 / 36.4** | **80.2 / 16.7** | 13.2 / NOT MET | NOT MET / NOT MET |
| 70 | NOT MET / NOT MET | NOT MET / NOT MET | NOT MET / NOT MET | 59.4 / NOT MET | 38.0 / NOT MET | NOT MET / NOT MET | NOT MET / NOT MET |

### 2.3 Verdict maps of all five cases (`plane_grid.out` 1.3: BC both, B typical only, - neither)

```
case P (U3 6.1 A (minimum), U3B carried 0.972)
      slope    -45   -30   -15    +0   +15   +30   +45
          0      .     .     .     -     .     .     .
         10      B     B     B     B     B     B     B
         20      B    BC    BC    BC    BC    BC    BC
         30      B    BC    BC    BC    BC    BC    BC
         40      B    BC    BC    BC    BC    BC    BC
         50      -     B    BC    BC    BC    BC     B
         60      -     B    BC    BC    BC     B     -
         70      -     -     B    BC    BC     B     -
case I (U3 6.0 A (bracket), U3B carried)
      slope    -45   -30   -15    +0   +15   +30   +45
          0      .     .     .     -     .     .     .
         10      B     B     B     B     B     B     B
         20      B     B    BC    BC    BC    BC     B
         30      B    BC    BC    BC    BC    BC     B
         40      B     B    BC    BC    BC    BC     B
         50      -     B    BC    BC    BC    BC     B
         60      -     -    BC    BC    BC     B     -
         70      -     -     B    BC     B     -     -
case H (U3 6.1 A, U3B hour by hour (TI curve))
      slope    -45   -30   -15    +0   +15   +30   +45
          0      .     .     .     -     .     .     .
         10      B     B     B     B     B     B     B
         20      B    BC    BC    BC    BC    BC    BC
         30      B    BC    BC    BC    BC    BC    BC
         40      B    BC    BC    BC    BC    BC    BC
         50      -     B    BC    BC    BC    BC     B
         60      -     B    BC    BC    BC     B     -
         70      -     -     B    BC    BC     B     -
case V20 (U3 6.1 A at the bus's nominal 20.00 V (122.0 W))
      slope    -45   -30   -15    +0   +15   +30   +45
          0      .     .     .     -     .     .     .
         10      -     B     B     B     B     B     B
         20      B     B    BC    BC    BC    BC     B
         30      B     B    BC    BC    BC    BC     B
         40      -     B    BC    BC    BC    BC     B
         50      -     B    BC    BC    BC     B     B
         60      -     -     B    BC    BC     B     -
         70      -     -     -     B     B     -     -
case V19 (U3 6.1 A at the DC band's low end 19.08 V (116.4 W))
      slope    -45   -30   -15    +0   +15   +30   +45
          0      .     .     .     -     .     .     .
         10      -     -     -     -     B     -     -
         20      -     -     B     B     B     B     -
         30      -     -     B    BC     B     B     -
         40      -     -     B    BC    BC     B     -
         50      -     -     B    BC     B     -     -
         60      -     -     -     B     B     -     -
         70      -     -     -     -     -     -     -
```

**Meets in both cases (P):** 20, 30 and 40 degrees at every azimuth from 30 east to 45 west; 50 degrees from 15 east to
30 west; 60 degrees from 15 east to 15 west; 70 degrees at south and 15 west. **Typical only (P):** 10 degrees at every
azimuth; 20 to 40 degrees at 45 east; 50 degrees at 30 east and 45 west; 60 degrees at 30 east and 30 west; 70 degrees at
15 east and 30 west. **Neither:** flat; 50 degrees at 45 east; 60 degrees at 45 east and west; 70 degrees at 45 and 30
east and 45 west.

### 2.4 The conditions (`plane_grid.out` section 3): SUPERSEDED

> **SUPERSEDED (third issue, 30 September 2026).** Every condition in this section rests on the model's 20.7 V bus and was never more than a PROPOSAL; none is accepted. The owner's basis is `ENERGY-BASIS.md`, where the 4S14P lid has NO band at the established worst inputs (WE) and the 4S15P band is conditional on efficiencies no maker document establishes.


| Set | Largest rectangle (grid points; least store) | Within x of south |
|---|---|---|
| P | slope 20 to 40, azimuth 30 E to 45 W (18; least 2.7 Wh at 20/+45, C) | within 15: slope 20 to 60 (least 20.4 Wh at 60/-15); within 30: 20 to 40 (least 9.2 Wh at 20/-30) |
| **P, I and H at once, above the floor (conservative)** | **slope 20 to 50, azimuth 15 E to 30 W** (16; least 19.9 Wh at 50/+30, case I C) | **within 15: slope 20 to 50** (least 26.0 Wh at 20/-15, case I C); within 30: slope 30 only (least 5.3 Wh) |
| the same with V20 (bus at its nominal) | slope 20 to 40, azimuth 15 E to 30 W, or slope 20 to 50 within 15 of south (12 each; least 6.1 Wh at 20/-15, V20 C) | within 15: slope 20 to 50 (least 6.1 Wh) |
| V19 alone (the DC band's low end) | slope 30 to 50 at south only (3; least 2.5 Wh at 50/+0) | within 15: no slope |

**The derived condition, 4S14P (INFERRED on this model; SUPERSEDED, a proposal only; at WE the 4S14P has no band): the array's plane at a slope of 20 to 50 degrees, facing between
15 degrees east and 30 degrees west of south** (every one of its 16 grid points meets M1 in both B and C in cases P, I and
H, least store 19.9 Wh). Its symmetric subset, **20 to 50 degrees within 15 degrees of south**, is the old rule of
ARRAY.md section 7 and has the larger least store, 26.0 Wh. P alone would admit 60 degrees within 15 of south and every
azimuth from 30 east to 45 west at 20 to 40 degrees, but on points whose least store falls to 1.7 Wh (60/-15 in I) and
2.7 Wh (20/+45 in P), under or near the floor.

### 2.5 The lowest stores at the old rule's edges (`plane_grid.out` section 4)

Every one of the rule's twelve planes (20 to 50 degrees, 15 east to 15 west) meets in both cases in P, I, H and V20. The
lowest store inside the rule is at its corner **20/-15** in every case: **P 90.4 Wh (B) and 44.6 Wh (C, the lid at 1.4
Wh)**, I 83.5 and 26.0 Wh, H 90.7 and 44.8 Wh, V20 72.9 and 6.1 Wh. In V19 the rule fails in C at eight of its twelve
planes. One grid step outside the rule (case P, C WAB): 10 degrees NOT MET at every azimuth from 30 east to 30 west;
60 degrees 20.4 Wh at 15 E, 67.2 at south, 52.1 at 15 W, NOT MET at 30 E and 30 W; at 30 degrees east 9.2 Wh at slope
20, 20.9 at 30, 10.7 at 40, NOT MET at 50; at 30 degrees west 37.0 Wh at slope 20, 58.7 at 30, 56.4 at 40, 37.6 at 50.

**Laid flat (slope 0): NOT MET in either case, in every one of the five cases.**

## 3. 4S15P lid, the QMX out of the lid (4S21P in all)

### 3.1 The grid, case P (`plane_grid.out` 2.1 and 2.2): lowest store of both packs, B TYP / C WAB, Wh; bold = meets in both; azimuth negative east of south

| slope \ azimuth | -45 | -30 | -15 | +0 | +15 | +30 | +45 |
|---|---|---|---|---|---|---|---|
| 0 (flat) |  |  |  | 15.6 / NOT MET |  |  |  |
| 10 | 67.0 / NOT MET | 87.9 / NOT MET | **103.2 / 16.6** | **106.5 / 27.9** | **106.1 / 28.6** | **98.0 / 14.6** | 84.0 / NOT MET |
| 20 | 77.2 / NOT MET | **110.7 / 39.8** | **121.7 / 75.3** | **126.6 / 90.5** | **127.0 / 83.6** | **128.1 / 67.8** | **113.7 / 33.3** |
| 30 | 74.9 / NOT MET | **114.2 / 51.6** | **126.1 / 94.8** | **126.2 / 110.9** | **126.9 / 110.9** | **127.0 / 89.5** | **110.2 / 38.8** |
| 40 | 53.4 / NOT MET | **105.9 / 41.3** | **126.3 / 97.1** | **125.2 / 116.6** | **126.7 / 113.5** | **123.7 / 87.2** | **103.9 / 37.4** |
| 50 | 12.2 / NOT MET | **80.9 / 14.6** | **123.1 / 82.8** | **123.5 / 111.6** | **126.4 / 107.4** | **115.0 / 68.3** | **73.0 / 3.0** |
| 60 | NOT MET / NOT MET | 43.4 / NOT MET | **109.1 / 51.0** | **121.3 / 98.4** | **121.5 / 83.0** | **88.0 / 25.1** | 11.1 / NOT MET |
| 70 | NOT MET / NOT MET | NOT MET / NOT MET | 67.8 / NOT MET | **109.9 / 56.3** | **101.9 / 37.6** | 37.5 / NOT MET | NOT MET / NOT MET |

### 3.2 The grid, cases I and V20 (same layout)

Case I, U3 at the 6.0 A bracket:

| slope \ azimuth | -45 | -30 | -15 | +0 | +15 | +30 | +45 |
|---|---|---|---|---|---|---|---|
| 0 (flat) |  |  |  | 5.1 / NOT MET |  |  |  |
| 10 | 50.1 / NOT MET | 69.2 / NOT MET | **85.4 / 5.4** | **96.1 / 15.7** | **93.2 / 13.6** | **82.9 / 3.4** | 70.1 / NOT MET |
| 20 | 59.1 / NOT MET | **94.7 / 25.0** | **114.6 / 56.6** | **125.0 / 75.5** | **126.7 / 70.4** | **118.5 / 52.8** | **97.0 / 22.2** |
| 30 | 56.2 / NOT MET | **105.2 / 35.9** | **123.2 / 76.0** | **126.2 / 102.7** | **126.9 / 102.4** | **127.0 / 73.3** | **93.9 / 23.9** |
| 40 | 34.8 / NOT MET | **87.7 / 26.4** | **126.3 / 78.4** | **125.2 / 107.2** | **126.7 / 106.6** | **119.9 / 70.7** | **86.3 / 18.7** |
| 50 | NOT MET / NOT MET | 58.5 / NOT MET | **118.6 / 64.1** | **123.5 / 102.9** | **126.4 / 95.1** | **100.1 / 50.6** | 54.3 / NOT MET |
| 60 | NOT MET / NOT MET | 24.8 / NOT MET | **102.5 / 32.3** | **121.3 / 87.0** | **120.9 / 67.0** | **67.7 / 7.9** | NOT MET / NOT MET |
| 70 | NOT MET / NOT MET | NOT MET / NOT MET | 49.1 / NOT MET | **101.1 / 41.4** | **85.7 / 19.0** | 18.9 / NOT MET | NOT MET / NOT MET |

Case V20, U3 at 6.1 A with the bus at its nominal 20.0 V (122.0 W):

| slope \ azimuth | -45 | -30 | -15 | +0 | +15 | +30 | +45 |
|---|---|---|---|---|---|---|---|
| 0 (flat) |  |  |  | NOT MET / NOT MET |  |  |  |
| 10 | 30.3 / NOT MET | 49.3 / NOT MET | 65.5 / NOT MET | 78.4 / NOT MET | 77.5 / NOT MET | 68.3 / NOT MET | 54.2 / NOT MET |
| 20 | 39.3 / NOT MET | **74.8 / 6.9** | **103.6 / 36.8** | **113.9 / 59.6** | **114.5 / 54.5** | **106.8 / 36.9** | **79.6 / 8.9** |
| 30 | 32.7 / NOT MET | **85.1 / 16.2** | **116.1 / 56.2** | **125.5 / 88.0** | **124.5 / 82.1** | **118.0 / 53.4** | **71.8 / 8.1** |
| 40 | 15.0 / NOT MET | **63.8 / 8.1** | **118.4 / 58.5** | **125.2 / 97.5** | **126.7 / 87.4** | **105.7 / 50.8** | 62.4 / NOT MET |
| 50 | NOT MET / NOT MET | 34.7 / NOT MET | **111.2 / 44.2** | **123.3 / 92.0** | **126.3 / 76.6** | **81.4 / 26.8** | 34.4 / NOT MET |
| 60 | NOT MET / NOT MET | 2.7 / NOT MET | **83.4 / 12.5** | **109.4 / 67.1** | **111.4 / 47.3** | 43.8 / NOT MET | NOT MET / NOT MET |
| 70 | NOT MET / NOT MET | NOT MET / NOT MET | 29.3 / NOT MET | **90.4 / 24.7** | 68.7 / NOT MET | NOT MET / NOT MET | NOT MET / NOT MET |

### 3.3 Verdict maps of all five cases (`plane_grid.out` 2.3)

```
case P (U3 6.1 A (minimum), U3B carried 0.972)
      slope    -45   -30   -15    +0   +15   +30   +45
          0      .     .     .     B     .     .     .
         10      B     B    BC    BC    BC    BC     B
         20      B    BC    BC    BC    BC    BC    BC
         30      B    BC    BC    BC    BC    BC    BC
         40      B    BC    BC    BC    BC    BC    BC
         50      B    BC    BC    BC    BC    BC    BC
         60      -     B    BC    BC    BC    BC     B
         70      -     -     B    BC    BC     B     -
case I (U3 6.0 A (bracket), U3B carried)
      slope    -45   -30   -15    +0   +15   +30   +45
          0      .     .     .     B     .     .     .
         10      B     B    BC    BC    BC    BC     B
         20      B    BC    BC    BC    BC    BC    BC
         30      B    BC    BC    BC    BC    BC    BC
         40      B    BC    BC    BC    BC    BC    BC
         50      -     B    BC    BC    BC    BC     B
         60      -     B    BC    BC    BC    BC     -
         70      -     -     B    BC    BC     B     -
case H (U3 6.1 A, U3B hour by hour (TI curve))
      slope    -45   -30   -15    +0   +15   +30   +45
          0      .     .     .     B     .     .     .
         10      B     B    BC    BC    BC    BC     B
         20      B    BC    BC    BC    BC    BC    BC
         30      B    BC    BC    BC    BC    BC    BC
         40      B    BC    BC    BC    BC    BC    BC
         50      B    BC    BC    BC    BC    BC    BC
         60      -     B    BC    BC    BC    BC     B
         70      -     -     B    BC    BC     B     -
case V20 (U3 6.1 A at the bus's nominal 20.00 V (122.0 W))
      slope    -45   -30   -15    +0   +15   +30   +45
          0      .     .     .     -     .     .     .
         10      B     B     B     B     B     B     B
         20      B    BC    BC    BC    BC    BC    BC
         30      B    BC    BC    BC    BC    BC    BC
         40      B    BC    BC    BC    BC    BC     B
         50      -     B    BC    BC    BC    BC     B
         60      -     B    BC    BC    BC     B     -
         70      -     -     B    BC     B     -     -
case V19 (U3 6.1 A at the DC band's low end 19.08 V (116.4 W))
      slope    -45   -30   -15    +0   +15   +30   +45
          0      .     .     .     -     .     .     .
         10      -     -     B     B     B     B     B
         20      -     B     B    BC    BC     B     B
         30      -     B    BC    BC    BC    BC     B
         40      -     B    BC    BC    BC     B     B
         50      -     -     B    BC    BC     B     -
         60      -     -     B    BC     B     -     -
         70      -     -     -     B     B     -     -
```

**Meets in both cases (P):** 10 degrees from 15 east to 30 west; 20 to 50 degrees at every azimuth from 30 east to 45
west; 60 degrees from 15 east to 30 west; 70 degrees at south and 15 west. **Typical only (P):** flat; 10 degrees at 45
and 30 east and 45 west; 20 to 50 degrees at 45 east; 60 degrees at 30 east and 45 west; 70 degrees at 15 east and 30
west. **Neither:** 60 degrees at 45 east; 70 degrees at 45 and 30 east and 45 west.

### 3.4 The conditions (`plane_grid.out` section 3): SUPERSEDED

> **SUPERSEDED (third issue, 30 September 2026).** Every condition in this section rests on the model's 20.7 V bus and was never more than a PROPOSAL; none is accepted. The owner's basis is `ENERGY-BASIS.md`, where the 4S14P lid has NO band at the established worst inputs (WE) and the 4S15P band is conditional on efficiencies no maker document establishes.


| Set | Largest rectangles (grid points; least store) | Within x of south |
|---|---|---|
| P | slope 10 to 60, azimuth 15 E to 30 W (24; least 14.6 Wh at 10/+30); slope 20 to 50, azimuth 30 E to 45 W (24; least 3.0 Wh at 50/+45) | within 15: slope 10 to 60 (least 16.6 Wh at 10/-15); within 30: 20 to 50 (least 14.6 Wh at 50/-30) |
| **P, I and H at once, above the floor (conservative)** | **slope 20 to 60, azimuth 15 E to 30 W** (20; least 7.9 Wh at 60/+30, case I C); slope 10 to 60 within 15 of south (18; least 5.4 Wh at 10/-15, I C); slope 20 to 40, azimuth 30 E to 45 W (18; least 18.7 Wh at 40/+45, I C) | **within 15: slope 10 to 60** (least 5.4 Wh); within 30: 20 to 40 (least 25.0 Wh at 20/-30) |
| the same with V20 (bus at its nominal) | slope 20 to 50, azimuth 15 E to 30 W (16; least 26.8 Wh at 50/+30, V20 C) | within 15: slope 20 to 60 (least 12.5 Wh at 60/-15); within 30: 20 to 40 (least 6.9 Wh) |
| V19 alone (the DC band's low end) | slope 20 to 50, azimuth S to 15 W (8; least 9.1 Wh at 20/+0) | within 15: slope 30 to 40 (least 5.6 Wh at 30/-15) |

**The derived condition, 4S15P (INFERRED on this model; SUPERSEDED, a proposal only): the array's plane at a slope of 20 to 60 degrees, facing between
15 degrees east and 30 degrees west of south** (every one of its 20 grid points meets in both B and C in cases P, I and H,
least store 7.9 Wh at 60/+30 in case I). Its symmetric form **within 15 degrees of south** reaches **10 to 60 degrees**
(least 5.4 Wh at 10/-15 in case I, just above the floor). The two other maximal conservative rectangles are in the
table; the choice among them is the owner's, and a larger rectangle has a thinner least store.

### 3.5 The lowest stores at the old rule's edges (`plane_grid.out` section 4)

Every one of the rule's twelve planes meets in both cases in P, I, H and V20. The lowest store inside the rule is at
**20/-15** in every case: **P 121.7 Wh (B) and 75.3 Wh (C, the lid at 23.8 Wh)**, I 114.6 and 56.6 Wh, H 122.0 and 75.6
Wh, V20 103.6 and 36.8 Wh. In V19 the rule fails in C at 20/-15 and 50/-15. One grid step outside the rule (case P, C
WAB): 10 degrees 16.6 Wh at 15 E, 27.9 at south, 28.6 at 15 W, 14.6 at 30 W, NOT MET at 30 E; 60 degrees 51.0 at
15 E, 98.4 at south, 83.0 at 15 W, 25.1 at 30 W, NOT MET at 30 E; at 30 degrees east 39.8 Wh at slope 20, 51.6 at 30,
41.3 at 40, 14.6 at 50; at 30 degrees west 67.8 at slope 20, 89.5 at 30, 87.2 at 40, 68.3 at 50.

**Laid flat (slope 0): meets in the typical case only (P 15.6 Wh, the lid emptied to 0.0 Wh; I 5.1 Wh; H 15.6 Wh), NOT MET
in the WAB case, and NOT MET in either case at V20 and V19.**

## 4. The two options side by side (INFERRED on this model): SUPERSEDED, not for the owner's decision

> **SUPERSEDED (third issue, 30 September 2026).** Every condition in this section rests on the model's 20.7 V bus and was never more than a PROPOSAL; none is accepted. The owner's basis is `ENERGY-BASIS.md`, where the 4S14P lid has NO band at the established worst inputs (WE) and the 4S15P band is conditional on efficiencies no maker document establishes.


| | 4S14P (tablet out) | 4S15P (QMX out) |
|---|---|---|
| derived condition (P, I and H, above the floor) | **slope 20 to 50, azimuth 15 E to 30 W** (least 19.9 Wh) | **slope 20 to 60, azimuth 15 E to 30 W** (least 7.9 Wh) |
| its symmetric form | 20 to 50 within 15 of south (least 26.0 Wh) | 10 to 60 within 15 of south (least 5.4 Wh) |
| lowest store at the old rule's worst corner, 20/-15, case P (B / C) | 90.4 / 44.6 Wh | 121.7 / 75.3 Wh |
| laid flat | NOT MET in either case | typical only (15.6 Wh), WAB NOT MET |
| if the bus sits at its nominal 20.0 V (V20, with P, I and H) | 20 to 40 at 15 E to 30 W, or 20 to 50 within 15 of south (least 6.1 Wh) | 20 to 50 at 15 E to 30 W (least 26.8 Wh) |
| at the bus's DC band low end, 19.08 V (V19) | due south only, 30 to 50 (least 2.5 Wh, under the floor); the old rule fails at 8 of 12 planes | within 15 of south only 30 to 40 (least 5.6 Wh); the old rule fails at 2 of 12 |

**One condition written for either option (SUPERSEDED, a proposal only):** slope 20 to 50 degrees, azimuth 15 degrees east to 30 degrees west of south
meets in both cases for both options in P, I and H above the floor. With the bus at its nominal 20.0 V it still holds for
4S15P (least 26.8 Wh) and not for 4S14P, whose 50/+30 then meets in the typical case only.

**The bus finding.** The V20 and V19 rows move the answer more than any other case: 6.1 A into U3 at the bus's nominal
20.0 V is 122.0 W, not the model's 126.3 W at 20.7 V. On this model the 4S14P lid's margins at the old rule's worst corner
fall from 44.6 to 6.1 Wh (C), and at the DC band's low end it meets in both cases only at due south, 30 to 50
degrees. Which bus voltage the energy model should carry is not settled here (the model is not edited); it is listed
for the energy record's writer and bears on both options' conditions.

## 5. What the grid does not show, and the other limits

- **Resolution.** 10 degree slope and 15 degree azimuth steps. Every condition's edges are grid points that were run; the
  boundary between an edge point that meets and the next that does not is not located, and a plane between two meeting
  grid points is not run (nothing shows the store has no dip between them). Nothing steeper than 70 degrees or turned
  further than 45 degrees from south is run. A condition written to the grid's edges leaves the operator no angular
  tolerance beyond them: an array set 5 degrees outside an edge is on a plane the grid did not run.
- **One day.** The September mean day repeated for 72 hours (SC-37); no run of cloudy days, no other month (December's
  mean on 40/0 is about 1.1 kWh/m2 a day by SC-37, against 4.0).
- **The plane's losses.** PVGIS's 0.9417 (angle of incidence, spectrum, temperature) is the 40/0 plane's and is kept for
  every plane (energy_runs.py's convention). The angle-of-incidence loss differs from plane to plane and is not computed
  per plane here, so every plane other than 40/0 carries an error of unknown sign and size from it.
- **The four panels on one plane**, unshaded; PVGIS's own terrain horizon only. Mixed planes or partial shade are not run.
- **The lid at 13.23 C and the base at +20 C** for the whole 72 hours.
- **The chargers' efficiencies exclude their inductors' core loss** (s119), so they are high by it.
- **The hourly step.** The floor of 4.2 Wh was measured at 40/0 only and at the second issue's settings; it is applied to
  every plane as a floor, not re-measured per plane.
- **The bus voltage** (section 4): the conditions of cases P, I and H rest on the model's 20.7 V.

## 6. Another site

**The model's inputs do not allow another site.** `plane_grid.out` section 5 reads them: all 50 plane days are PVGIS
DRcalc for latitude 52.160, longitude 4.497 (Leiden), PVGIS-SARAH2 2005 to 2020; the monthly mean that scales the day
(`v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json`, 4.014 kWh/m2 a day in September on 40/0) is the same location;
the lid basis 13.23 C is the minimum of that site's September T2m; the ratio 0.9417 is PVGIS's for that site's 40/0
plane. **So every condition on this page is tied to Leiden and the reference day of SC-37 (the September mean day).** A
different site would need, for that site and month: (1) a PVGIS DRcalc mean-day profile for each grid plane (hourly
G(i) and T2m), which `energy_runs.py` pins by name and sha256; (2) the PVGIS-SARAH2 monthly mean that scales the day,
which `energy_inputs.yaml` pins and `energy_budget.py`'s `profile()` reads; (3) the PVGIS PVcalc losses behind the
performance ratio (`energy_inputs.yaml` `solar.panel.performance_ratio`); (4) the site's September T2m for the lid basis,
which `energy_two_pack.py` reads from the pinned 40/0 DRcalc file; and (5) SC-37 restated to that site, since the
reference day is SC-37's.
