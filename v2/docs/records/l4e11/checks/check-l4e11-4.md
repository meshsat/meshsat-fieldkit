accepted: yes

# Layer 4, L4-E11: Claude's check of the U-04 round at f9d9da33 (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026. On the owner's instruction of the same day, the round separates each specification the held
documents leave to TI, maps it to the engineering claim it affects, and states what a TI answer and what a one-sample bench
test could establish. It evaluates a bounded fallback (VSYS's hold-up) and restates U-04's class. It is section 11 of the page,
with the questions in `clarification/TI-QUESTIONS.md`.

**Verified by the coordinator:**
- *Reproduction:* `l4e11_power.py` re-run at `f9d9da33`, its output equal to the committed `.out` byte for byte; `test_l4e11`,
  `test_l4e_svg_readers` and `test_public_hygiene` 34 passed, 0 failed, 0 skipped. No em or en dash.
- *The table D1 to D10:* each row names the missing statement, the claim and its record line (a test checks the cited lines), a
  TI answer's reach (production-wide when stated as a limit) and a bench test's reach. A one-sample reading is never written as
  a guaranteed bound: it is evidence for that unit and revision, and it counts as a margin only where the margin is large against
  the plausible spread (D2's 5-fold, D7's 4.58-fold). D10's 1.346-fold is correctly called headroom, not a margin.
- *The fallback's energy, in separate arithmetic:*
  - the bank is 4 x 470 uF x 0.504 = 947.5 uF;
  - from 16.561 V to 12.95 V (VSYS_MIN plus D_H's 0.65 V) it stores 0.5 x C x (16.561^2 - 12.95^2) = 50.49 mJ, 48.26 mJ net of
    the diode's share;
  - the direct can's 90.72 uF from 16.716 V to 12.3 V gives 5.81 mJ;
  - 54.07 mJ in all, which is the USB-C PD outlet's 48.39 W for 1.117 ms;
  - the bank charges at most 16.884 / 330 = 51.2 mA, a peak of 0.864 W in the 1 W resistor.
  The 0.9 cold factor and the 1 ms converter response are labelled ASSUMPTION.
- *The correction found on the way:* ChargeCurrent()'s value at power-on is 256 mA, not 0 A. It is read on the cited TI E2E
  thread 1316778 ("The POR value is indeed 256mA", a TI expert, MAKER forum). The hold-persistence rule already covered it.
- *U-04's class stays ARCHITECTURE-LEVEL CHOICE, and that is right:* the fallback removes D2 and D5 from the dependence on TI,
  but D1 (VSYS's DC regulation with no battery) and D3 (VSYS with charging inhibited and no battery current) have no remedy
  inside arrangement (A). A negative answer to either leads to (B), a charger with a battery FET, which is an architecture change.

**Accepted** as the U-04 statement at the engineering level. The vendor answers (TI's D1 and D3 above all) stay open. The fallback
E11-24 is a register row, not applied.

**Noted, not this round's:** the cited E2E page and two others are tracked in `v2/vendor/` since earlier sessions (`d90f30e4`).
Whether forum pages may be republished is MESHSAT-1481.
