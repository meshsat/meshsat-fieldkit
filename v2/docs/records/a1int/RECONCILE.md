# Option A(i): the electrical and mechanical packages reconciled (MESHSAT-1357, 29 September 2026)

Prototype design: nothing bought, built or measured. AI engineering analysis; each package has its own independent AI check
(running at the time of writing). M1 and REQ-072 are unchanged; REQ-072 stays FAIL until a design is built and tested.

**The two packages meet here.** Stream a1elec (`records/a1elec/`) modelled the two packs separately and found A(i) meets
M1 on the reference day with a 4S12P lid, but by 0.7 Wh in the lid. Stream a1mech (`records/a1mech/`) found that a 4S12P
lid does not fit with both owner-approved lid functions kept: 35 cells (4S8P) with the HF set (16a) and the tablet bracket
(16d) both in the lid, 56 places with the tablet out (B), 58 with the QMX out (C). `reconcile_lid.py` re-runs a1elec's own
model, unchanged but for the lid's parallel count and its charge current per string, for the lids that fit
(`reconcile_lid.out`):

| Lid (in all) | Result at the lid's 13.23 C | Lowest point, base and lid | Lowest lid temperature that meets |
|---|---|---|---|
| 4S8P, both functions kept (4S14P) | NOT MET: stops at hours 22 and 10, 258.9 Wh unserved | 0.0 and 0.0 Wh | none, not even at +40 C |
| 4S9P, both kept with P2 under the tablet (the mechanical check's 39 places; 4S15P) | NOT MET at 400, 650 and 1000 Wp (164.8, 110.9 and 41.7 Wh unserved) | 0.0 and 0.0 Wh | meets only with the lid at +20 C AND 650 Wp or more (2.0 Wh left at 650 Wp, 29.4 at 1000 Wp); fails at 400 Wp even at +20 C |
| 4S12P, a1elec's assumption (4S18P) | MEETS | 30.3 and 0.7 Wh | +9.6 C |
| 4S14P, the tablet out (B, 56 places; 4S20P) | MEETS | 49.1 and 44.9 Wh (94.0 together) | +3.8 C |
| 4S15P, the QMX out (C, 61 places after the mechanical check; 4S21P) | MEETS | 57.2 and 68.3 Wh (125.5 together) | +1.5 C |

**The conflict, stated for the owner.** With both approved lid functions kept, the lid holds at most 39 cells (4S9P, the mechanical check's
arrangement), and that carries M1 on this model only with the lid's cells as warm as the base's (+20 C) and an array of
650 Wp or more; at the lid's basis temperature, or at A(i)'s 400 Wp, it does not. With one of them out of the lid, a 4S14P lid carries it with margin (94 Wh at the
lowest point, down to a +3.8 C lid). The choice of which function leaves the lid, and where it goes, is the owner's:
`records/a1mech/DECISION-A1.md` (B, the tablet out, is the engineering recommendation there; the corrected counts are A 39, B 56, C 61).

**After the electrical check's corrections (29 September 2026 03:17).** a1elec now takes every limit at its minimum: board A
as generated (E1) does not meet M1 at all, the model needs at least 5.56 A (115.1 W) into U3, and the drafted entry E2 (R11
6.2 mOhm, U3 IIN_HOST 6.2 A, under the front end's 6.94 A minimum) is the design case above. Re-run on the corrected model,
every figure of the table is unchanged (`reconcile_lid.out`). A 4S14P lid needs its BQ4050 calibrated at k = 3, not k = 2
(at k = 2 its cWh word would be 33,768, above the 32,767 the gauge holds; a1elec's GAUGE.md).

**The electrical package's independent check** (`records/a1elec/checks/check-a1elec-1.md`, acceptable no; the focused
re-check `check-a1elec-2.md`, acceptable yes): its minor items N1 to N4 stay open as wording in a1elec's pages (the
charge-order sentence of TOPOLOGY 3b, the 13 UTC in CHARGER.md, a doubled table header, a heat column's sum), and
`gauge_scale.py` hard-codes k = 2 and a 4S12P table, so a 4S14P lid needs it edited, not re-run.

**With the chosen panel (stream a1solar, integrated 29 September 2026; second issue after the independent check
`checks/check-a1int-1.md`).** `reconcile_lid_panel.py` (output `reconcile_lid_panel.out`) re-runs the three lid options
with the performance ratios of four Renogy RNG-100DB-H in 2S2P at the drafted fixed input point, read from
`records/a1solar/energy_runs.out` section 2: A 0.9417 (the pinned MPPT ratio, which reproduces the table above), B 0.9326
typical, C 0.8573 with everything adverse at once. **U3's input limit is taken at its minimum**, as CHARGER.md's rule asks:
6.1 A (SLUSE66A prints no 10 mOhm accuracy row; its 5 mOhm rows and 9.6.22 read so), with 6.0 A as the bracket and the
6.2 A nominal shown; U3B charges at its recorded code 62, 7.936 A, for every lid (the first issue scaled it per string,
above the gauge's limits, which moved no figure because the entry sets the lid current). On the 40 degree south plane at
the lid basis of 13.23 C (model results; the check's independent balance reproduces every one to 0.05 Wh at a 1 h step):

| Lid | Ratio B, typical (U3 at 6.2, 6.1 or 6.0 A) | Ratio C, adverse, U3 at its minimum 6.1 A | Ratio C, U3 at 6.0 A |
|---|---|---|---|
| 4S9P, both lid functions kept | NOT MET (not even with the lid at +40 C) | NOT MET | NOT MET |
| 4S14P, the tablet out (4S20P in all) | MEETS, lowest 93.7 Wh, lid down to +3.8 C | MEETS, 87.4 Wh, lid down to +5.9 C | MEETS, 77.6 Wh, +6.1 C |
| 4S15P, the QMX out (4S21P in all) | MEETS, 125.2 Wh, lid down to +1.5 C | MEETS, 118.5 Wh, lid down to +2.2 C | MEETS, 108.7 Wh, +4.0 C |

The model needs at least 5.57 A (4S14P) and 5.43 A (4S15P) into U3 at ratio C to meet M1 at the basis (the check). The
lid thresholds are not stable to better than about 1.5 K with the model's hourly taper (at 0.1 h the 4S14P C threshold at
6.1 A reads about +4.6 C); a 0.01 h step lowers the lowest stores by about 1.2 to 1.9 Wh (B) and 3.3 to 4.2 Wh (C). U3B at its 0.96
efficiency bracket costs 6.0 and 6.2 Wh at C with U3 at 6.1 A (`checks/check-a1int-2.md`). **Both 4S14P and 4S15P need the lid gauge calibrated at k = 3** (at k = 2
their cWh words would be 33,768 and 36,180, above the gauge's 32,767; GAUGE.md), and `gauge_scale.py` is written for 4S12P.
**The planes:** `records/a1solar/ARRAY.md` 7's rule (20 to 50 degrees within 15 degrees of south) was computed for a 4S12P
lid; for these lids it is sufficient, and the check's own runs found both meet over a wider range and the 4S15P lid meeting
laid flat in the typical case only (4S14P laid flat does not). A plane grid for the chosen lid is re-run when the owner
decides which function leaves the lid. Nothing is measured.

**What this does not show.** The circuits are drafts (a second charger, the ideal-diode join, the lid gauge's k = 3
calibration, board A's entry re-rated with its inductor, board E's 200 W stage); the lid pack's heater, its temperature in
use and the case's stability with a heavier lid (a stay at 100 degrees) are findings; the panel is selected on its maker's figures and a model (`records/a1solar/`), not measured, and board E's
entry is not yet re-rated for it (REQ-016 is the owner's). Nothing here is physical verification or fabrication readiness.
