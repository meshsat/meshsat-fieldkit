accepted: yes

# Layer 4, L4-E2, B2: Claude's verification of O-2's final bound (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 1 October 2026. Scope: B2 only, the one item the engineering collaborator's targeted recheck left open
(`astra-check-l4e2-2.md`, run 20260930T224030Z-833954 on `21a9a6fe`), at the revision `197350a7`. B1, M1 and the Layer 3
recount were accepted by that recheck. Astra never examined `197350a7`; the owner's rule allows one assessment and one
targeted follow-up per issue, both used. B2 failed twice; the method changed from a hand-picked tolerance list to every
row of the maker's table that moves the input-current limit, stacked worst case, with a refusal above 100 W.

## The criterion

The recheck's closure criterion: "The corrected calculation must show VIN x IIN,max <= 100 W throughout the stated voltage
and tolerance envelope, including line regulation and setting rounding. Dependent replay rows must reproduce the revised
settings. The planned bench sweep must cover the actual lower hold corner through the maximum permitted loaded voltage at
the temperature ends, retaining separate steady-state and transient records."

## Evidence at `197350a7`

- The rows, read by the coordinator from `v2/vendor/power/lt8705a.pdf` (8705af) with pdftotext: p.31 the limit
  I = 1.208 V / (1 mA/V x R_SENSE1 x R_IMON_IN); p.4 IMON_IN regulation voltage 1.187 / 1.208 / 1.229 V over temperature;
  p.4 line regulation of the IMON error amplifier 0.002 typ, 0.005 max %/V (VIN 12 V to 80 V); p.5 the A7 gm 0.95 / 1.05
  (all grades, 25 C), 0.94 / 1.06 (E, I), 0.93 / 1.07 (H, MP); p.5 EA2 voltage gain 130 V/V (typical only).
- The coordinator's own computation, not the author's code: the high corner at 25 V,
  3.548 A x (1.229 x (1 + 0.00005 x 13) + 1.5 / 130) / 1.208 / 0.93 / 0.99^2 = 3.99994 A, so V x I = 99.9984 W, under
  100 W; the low corner at the lower hold 16.695 V, 3.548 A x (1.187 x (1 - 0.00005 x 4.695) - 1.5 / 130) / 1.208 / 1.07 /
  1.01^2 = 3.1622 A, 52.79 W. Both equal the replay's printed figures (99.9984 W, margin 0.0016 W; 52.8 W).
- `l4e_replay.py` re-run by the coordinator: its output identical to the committed `l4e_replay.out`; `l3batt/runtime.out`
  reproduced byte for byte; only `v2/docs/records/l4e/` changed since `b45d1705`.
- The author's refusal tests (reported, not re-run here): the run exits 4 at 100.0548 W when the line-regulation row is
  classified as moving nothing, and exits 3 when that row is removed from the table.
- The bench sweep on the page runs from 16.695 V to 25 V at both temperature ends, steady state and transients apart.

## Result and residuals

B2 is closed against the recheck's own criterion. Residual assumptions, labelled on the page and not removed by this
check: the EA2 allowance (a typical gain only; VC taken over its absolute maximum range, which lowers the setting) and
1 % sense and setting resistors (no parts chosen). The stage's actual operating point between 52.8 W and 100 W stays
INCONCLUSIVE until a panel is pinned (O-1), its resistors chosen and the sweep run. Nothing here is hardware compliance.
