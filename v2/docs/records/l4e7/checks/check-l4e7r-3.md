accepted: no

# Layer 4, L4-E7R: Claude's closing check of the control decision at 237cd9be (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026. Both collaborator runs on L4-E7R are spent:
- the independent check `astra-check-l4e7r-1.md` on `26cdf5bd`, NOT YET, six blockers;
- the targeted recheck `astra-check-l4e7r-2.md` on `6fca30d3`, NOT YET.

The third round, `237cd9be`, applied the owner's decision process of 2 October. This is the coordinator's closing check. It
challenges the critical calculations and the failure behaviour independently.

**Verified, in the coordinator's own arithmetic from the printed rows (section 10 of the output):**

*Check (a), the static bound.* The trip's highest sense voltage at 25 V is built up as follows:
- R66 at its aged lowest: 8.25k x 0.999 x (1 - 25 ppm/K x 45 K) x (1 - 0.005006)^2 = 8150.26 Ohm.
- U18's lowest transconductance: 990 uA/V less the 0.1 % nonlinearity.
- U19's highest threshold: 403 mV, plus 25 nA through R66.
- Together these give 50.0210 mV, and adding the following gives 51.3645 mV:
  - the 1 mV offset;
  - the rejection rows, 130 + 200 uV;
  - G_CM's 13.5 uV;
  - the load term, which is negligible.
- Over the bank's aged lowest it trips at 3.8299 A. The bank's aged lowest is 14 mOhm x 0.99 x (1 - 75 ppm/K x 45 K) x
  0.98786 x 0.98286 = 13.4116 mOhm.
- So 95.747 W at 25 V, plus 32 mW bypassing the bank, gives **95.7788 W**, equal to the record.

The record's classification stands: CONDITIONAL on G_CM and on U18's VIN+ bias, each with its break-even printed and an
answer on the same topology past it.

*Check (b), the dynamic bound.*
- The capacitor input energy is 225.83 uF x 25 V squared = 141.1 mJ.
- The window's 10 J, less 0.1 s at the 95.78 W bound and less that charge, leaves 0.281 J for the response.
- At the source's 6.802 A x 25 V that allows **3.78 ms**, equal to the record.
- The averaging window (0.1 s) is the stated interpretation for layer 8 (REQ-016 states none).

*Sequencing.*
- R70 8.06k over R71 6.04k, at their aged extremes, against SWEN's 1.156 V threshold: SWEN cannot rise while TRK_LDO33 is
  under **2.661 V**, above every sensing part's 1.8 V minimum supply. Off by default on printed rows; the record says 2.662 V.
- SWEN's own pin current is the one unprinted figure: break-evens printed, an Analog Devices draft asks for it.

*Check (c), the disturbance.*
- Derived from the approved test plan (M2 CS101, M3 CS114, M7 discharge). D4's pulse is kept as a labelled capability
  scenario.
- U5's worst sense differential is 0.2144 V against 0.3 V. This figure was reproduced from the record's model, not recomputed
  separately; it is MODELED, with bench row 7b.18 and M3 and M7 at layer 8.

*Run by the coordinator at `237cd9be`:* the output reproduced byte for byte; `test_l4e7` with `test_public_hygiene` 39 passed,
0 failed, 0 skipped.

**Not accepted, one material defect: the backstop's susceptibility under CS101.**
- The page (section "The backstop under CS101") records that CS101's injected current, 1.91 A rms at 1 kHz and above, crosses
  the bank. The peaks above the trip less the operating current stop the stage for td (at least 180 ms) each time.
- Solar charging therefore stops for the test. TEST-PLAN M2's line is "no upset of the kit's operation, no reset, no loss
  of a bearer" (REQ-063).
- This is a susceptibility the design itself introduces. Noting that M2 will read it is not a resolution, and an acceptance
  criterion is not changed to fit it.
- The page states that an INB filter slow enough to ride through the ripple would exceed check (b)'s allowance at the
  regulation's highest current, but gives no figure. The coordinator's estimate points the other way:
  - the ripple current is small at low frequency: about 85 mA at 30 Hz into 226 uF;
  - at 400 Hz it is about 1.6 A peak, which needs about 2.2 times attenuation of the excursion above the regulation's
    highest (3.09 A) to stay under the trip (3.83 A): a corner near 180 Hz;
  - such a filter crosses the trip in about 0.2 ms on a step to the source's whole current, inside the 3.78 ms allowance.

  The estimate needs the record's full analysis to confirm it.
- A second engineering option: a ripple-shunt capacitor ahead of the bank. Its charge is bounded once by C x V squared in
  check (b) and it must be surge-rated; U18 is now the INA169, so the reason that moved the parts behind the bank (the
  INA250's 40 V) no longer applies.

**Next bounded action (the author):**
- quantify both options against CS101's whole curve (30 Hz to 150 kHz, both of Figure CS101-1's and CS101-4's setups) and
  check (b)'s allowance;
- select one and draft it;
- show the backstop does not trip at the regulation's highest current under CS101, with the static and dynamic bounds kept.

This does not overturn the architecture. The backstop on SWEN stands, and the fix is a filter or a capacitor on the same
topology. Until it lands, L4-E7R's criterion is met for checks (a) and (b) and the sequencing. It is NOT met for the
interaction between the protection and the approved test: material defect open.
