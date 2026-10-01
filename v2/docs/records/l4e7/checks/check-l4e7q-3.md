accepted: yes

# Layer 4, L4-E7Q: Claude's verification of the qualification of the 100 W bound (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 1 October 2026. The owner asked for L4-E7's 96.25 W result to be qualified precisely. The author's answer is
`L4E7-QUALIFICATION.md` (`ee9909a8`). The collaborator's focused check (`astra-check-l4e7q-1.md`, on `ee9909a8`) read NOT
YET on B1 (A7's gm extrapolated from its test point) and B2 (the cold TCR's effects, the fault-to-limit ratio). The fixes
are `fac796e4`. Its targeted recheck (`astra-check-l4e7q-2.md`, on `fac796e4`) read ACCEPT with two wording residues,
fixed at `7f6eeda7`.

- **B1, read at the source.** 8705af p.5: the A7 gm row (0.94 / 1 / 1.06 mmho, E and I grades, full range) carries the
  conditions VCSPIN minus VCSNIN = 50 mV and VCSPIN = 5.025 V. The CSPIN and CSNIN common-mode range of 1.5 to 80 V is an
  operating range, not a gm guarantee. The page now carries A7's applicability as the fifth condition of the bound.
- **Stack A, recomputed by the coordinator in separate arithmetic** from p.4 and p.5's rows and the parts' sheets, at the
  cold end:
  - the regulation point is 1.229 V x (1 + 0.005 %/V x 13 V) + 1.5 V / 130 V/V = 1.241337 V;
  - RSENSE1 is 15 mOhm x 0.99 x (1 - 50 ppm/K x 45 K);
  - RIMON_IN is 23.2k x 0.999 x (1 - 25 ppm/K x 45 K);
  - with gm 0.94 mmho the limit is 3.84990 A, so **96.2474 W** at 25 V;
  - the gm at which the corner reaches 100 W is **0.904726 mmho**.

  Both equal the script's figures.
- **The wording residues.** The output calls the junction "TJ estimated about 105.4 C (INFERRED)", and a predicate holds
  that no page or output line calls it a bound. "No gain of its own" is gone; the line coupling is quantified.
- **Run by the coordinator at `7f6eeda7`:** `l4e7_stage_settings.py` re-run, its output equal to the committed `.out` byte
  for byte; `test_l4e7` with `test_public_hygiene` 27 passed, 0 failed, 0 skipped.

**Result: the qualification is accepted. The 96.25 W corner stays a calculated result under its stated assumptions and is
CONDITIONAL** on five unresolved values: EA2's gain and VC's range; A7's gain away from its test point; the IMON_IN line
regulation while switching and at temperature; RSENSE1's TCR below +25 C; U5's junction, an inferred estimate inside the
I grade's full range.
- With every conservative assumption together and the resistors' drifts, the corner reads 99.8992 W, a margin of 0.1008 W.
- Clearing a condition needs a manufacturer-warranted limit and its conditions. Lot characterization is supporting
  evidence only.
- The drafts for Analog Devices and Milliohm are in `clarification/`, for the owner to send.
- The bench rows 7b.9 to 7b.14, including the cold-soaked irradiance step, are downstream obligations; none blocks an
  architecture decision.
- No part changed: the HoJLR stays over the Vishay WSL, which fails the design floor at 23.2k.
