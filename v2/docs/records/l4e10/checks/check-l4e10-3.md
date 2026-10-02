accepted: yes

# Layer 4, L4-E10: Claude's closing check of the decision-ready comparison at 79b2f568 (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026. Both collaborator runs on L4-E10 are spent:
- the focused check `astra-check-l4e10-1.md` on `9fe3b632`, NOT YET;
- the targeted recheck `astra-check-l4e10-2.md` on `2316b107`, NOT YET; it confirmed the framing, with FEA-008 open and no owner
  decision forced.

The final round, `79b2f568`, applied the owner's instructions of 2 October: separate cases, usable energy on one boundary, the
actual profiles, and one bounded comparison of complete approaches. **This check accepts the record as a correct,
decision-ready comparison and recommendation. It does NOT close FEA-008, and the thermal architecture criterion is NOT met.**

**Verified by the coordinator:**
- *Reproduction:* `l4e10_cell_thermal.py` re-run at `79b2f568`, its output equal to the committed `.out` byte for byte.
  `test_l4e10` with `test_public_hygiene`: 20 passed, 0 failed, 0 skipped.
- *LO-01a's threshold and the conditioned corner, in separate arithmetic:*
  - The complete pass line, 1.6664 W/K, holds the inside air on shore at most 15 K over +40 C. The kit's heat into the
    case at that operating point is therefore about 25.0 W.
  - At the same conductance and heat, D-02a's +55 C operating margin gives 70.0 C inside air (E3-O), and E5's +60 C dwell
    gives 75.0 C. Both equal the record's figures.
- *The powered-cooling balance (3i):* the corrected form G_e a = q + G_b (a - d) / COP adds only the cooler's input to the
  sealed case's air, as the second check asked. The rejections and INCONCLUSIVE labels follow from it.
- *The framing:* each approach is read on the same profiles at the conditioned corner. A missing qualified part is
  recorded as a component limitation, not as a requirements conflict. The primary battery is recorded as added energy
  storage under D-06, a proposal, not adopted.

**The recommendation and why it needs the owner.** Approach (II): a wide-temperature 18650 (the HL18650V class) in D-06's
4S3P, with the pack's protection re-derived, needing no added subsystem. Its LO-01d to g rows rest on the maker's product
page, not a signed specification, so the recommendation is CONDITIONAL on that specification. It also needs, beyond the
session's authority:
- (1) an outside contact: the drafted request for the signed specification;
- (2) after the specification confirms, an approved-requirement and resource change:
  - D-06's "about 145 Wh" restated to about 121 Wh nominal;
  - REQ-046's cell windows and REQ-077's +60 C, which are the 35E's numbers, restated with the cell;
  - about USD 42 a pack.

These are genuine owner items under his rule. If he does not take them, the default is the existing state: LO-01d to g
open as a release gate.

**Thin margins carried as conditions, not hidden:**
- at LO-01e, (II)'s cells sit 1.06 K under the re-derived H1 and 0.97 K under U2's lowest trip;
- U2's 75.7 C trip is INFERRED, shifted by the present part's 7.3 K tolerance;
- every approach depends on T-H1 reading at least 1.666 W/K in both lid states.

**A kit-level finding outside FEA-008, raised as its own issue.** At the conditioned corner the inside air reaches 70.0 C in
E3-O and 75.0 C in E5's dwell, under every approach. Several electronics parts are rated +70 C:
- the SA868;
- the AW7915-AED cards;
- the LimeSDR;
- the Xenarc display.

D-02a's +55 C operating margin and the E5 dwell may therefore be out of reach for the electronics in the sealed case,
whatever the cell. That is an architecture-level thermal question, not a downstream test, and it is carried as such.
