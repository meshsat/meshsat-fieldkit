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
| 4S14P, the tablet or the QMX out (4S20P) | MEETS | 49.1 and 44.9 Wh (94.0 together) | +3.8 C |

**The conflict, stated for the owner.** With both approved lid functions kept, the lid holds at most 39 cells (4S9P, the mechanical check's
arrangement), and that carries M1 on this model only with the lid's cells as warm as the base's (+20 C) and an array of
650 Wp or more; at the lid's basis temperature, or at A(i)'s 400 Wp, it does not. With one of them out of the lid, a 4S14P lid carries it with margin (94 Wh at the
lowest point, down to a +3.8 C lid). The choice of which function leaves the lid, and where it goes, is the owner's:
`records/a1mech/DECISION-A1.md` (B, the tablet out, is the engineering recommendation there).

**What this does not show.** The circuits are drafts (a second charger, the ideal-diode join, the lid gauge's k = 2
calibration, board A's entry re-rated with its inductor, board E's 200 W stage); the lid pack's heater, its temperature in
use and the case's stability with a heavier lid (a stay at 100 degrees) are findings; the panel is not yet selected
(`records/a1solar/`). Nothing here is physical verification or fabrication readiness.
