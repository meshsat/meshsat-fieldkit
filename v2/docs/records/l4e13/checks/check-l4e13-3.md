accepted: yes

# Layer 4, L4-E13: Claude's closing check of the panel record at bbd3c82c (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026. Both collaborator runs on L4-E13 are spent:
- the focused check `astra-check-l4e13-1.md` on `b3e01e25`, NOT YET (B1 the acceptance contract, B2 the classification);
- the targeted recheck `astra-check-l4e13-2.md` on `4fb7d263`, NOT YET on B1 only (the irradiance bound, the slope
  extrapolation, A-2 not consuming the unit's measurements, A-3 without the enlarged irradiance).

The final round is `bbd3c82c`. **This check accepts the record: U-03 is a CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC),
with route 2 feasible on a unit equal to the typical rows and no physical unit accepted.** The final round answered B1 by
separating the owner's three checks, as REQ-016's own acceptance does ("Protection is judged apart from the window, under rule
TRN-001"), so that no irradiance maximum is a decision input. That was the coordinator's direction; this check verifies the
numbers and the evidence, not the direction's agreement with itself.

**Verified by the coordinator:**
- *Reproduction:* `l4e13_panel.py` re-run at `bbd3c82c`, its output equal to the committed `.out` byte for byte;
  `test_l4e13` with `test_public_hygiene` 22 passed, 0 failed, 0 skipped; no em or en dash in the page or the output.
- *The recheck is filed faithfully:* `astra-check-l4e13-2.md` carries the run's summary and every blocker and evidence item of
  `result.json` (run `20261002T054411Z-593913`) word for word.
- *The window (A-1):* Vm20 + U_V = 24.050 + 0.10 = 24.15 V on the typical rows, margin 0.85 V; the ceiling Vm20 24.900 V scales
  to Voc25 24.900 x 21.4 / 24.050 = 22.156 V. The window reads the makers' rated quantity, defined at 1000 W/m2 (SunPower
  523809 Rev D p.1, "Typical Electrical Data at STC: 25 C, 1000 W/m2 and AM 1.5"), moved to -20 C, and is measured directly
  (M2): no slope and no extrapolation enter it.
- *The disturbance check, in separate arithmetic:* with Ns 32 and kT/q at 253.15 K (0.021815 V), the slope bound is
  0.9075 / 1.3961 / 2.0942 V per e-fold for n 1.3 / 2 / 3; a unit at A-1's ceiling reaches D4's 28.0 V standoff at
  27,270 / 8,574 / 4,189 W/m2, that is 19.4 / 6.09 / 2.98 x the extraterrestrial 1407.6 W/m2 (the record's 27,401 W/m2 uses
  the fitted n 1.2981). The coldest cells are the worst case: at n 2 and ln(8.574) the irradiance term adds +0.01185 V/K against
  the sheet's -0.0589 V/K. The SMCJ28A row is read on the held Littelfuse sheet (VR 28 V; VBR's coefficient printed as
  "typical value is 0.1%", so the cold VBR 29.70 V is context only, not a limit the decision uses).
- *SunPower's own allowance, read on guide 524958 Rev F, section 3.0 (PDF p.2):* "the values of ISC and VOC marked on the
  modules should be multiplied by a factor of 1.25 when determining component voltage ratings, conductor capacities, fuse
  sizes and size of controls connected to the module output." Its voltage half is met on PV_P: 1.25 x 21.4 = 26.75 V and
  1.25 x 22.156 = 27.69 V at the window's ceiling, both under the lowest rating there, D4's 28 V (C11 and C12 35 V). The record
  states this cross-check. The author's correction of the section (3.0, not the 5.1 the coordinator's direction named) is right.
- *A-2, with an independent single-diode fit:* fitted to the sheet's Voc 21.4 V, Isc 6.3 A, Vmp 17.1 V, Imp 5.9 A at STC by
  the maximum-power condition (n 1.2984, Rs 0.2300 Ohm), with the sheet's coefficients and the 5 m lead's 0.0465 Ohm: at the
  offset corner (510.3 W/m2, 36.65 C) the current at 18.813 V is 1.5511 A and the power 29.181 W, against the record's
  1.5508 A and 29.176 W (0.02 %). U_P combines the voltage point (18.813 x 1.0674 A/V x 0.10 V = 2.008 W) and U_I
  (0.02 x 29.176 = 0.584 W) by root sum of squares: 2.091 W; lower bound 27.085 W, above 1.365591 W. The floor without the
  uncertainty term comes out at 0.9482 x rated (20.291 V); the record's 20.315 V with it lies above, as it must. At the corner
  18.813 V lies well above the maximum-power point (the curve's maximum near 50 W against 29 W there), so the offsets to lower
  irradiance and higher cell temperature lower the current: conservative.
- *A-3:* (a) 99.6739 W / 25.000 V = 3.9870 A, read on L4-E7's output (line 99, stack C's cold-end worst corner);
  (b) (6.3 + 0.0026 x 45) x 1.02 x 1.25 = 8.1817 A, under 10 A; (c) the same x 2.1114 = 13.820 A, and 20 / 6.5453 x 1000 =
  3,056 W/m2, 2.17 x E0. JST VH's held catalogue prints "Current rating: 10 A AC/DC" and no short-time overload: a
  COMPONENT_LIMITATION, carried as PANEL-ACC row A-3(c), at Layer 5/6.
- *The energy table:* the rated unit's rows are L4-E7's own (`l4e7_stage_settings.out` lines 127 and 132: 350.0 Wh at
  17.593 V, 240.0 Wh at 18.813 V); the script checks both.

**Why this cannot overturn the architecture:** REQ-016's window, the stage, its hold and the drafted limit stay. A unit that
passes A-1 also passes the disturbance check for any plane-of-array irradiance below 8.6 kW/m2 at the ideality's ceiling.
A-3(c) is a connector and conductor rating at Layer 5/6, and REQ-016's "rated 10 A" is a minimum. What remains is a
measurement on a bought unit, the owner's purchase.

**What stays open, by class:**
- MISSING_EVIDENCE: no unit is bought or measured. The purchase and the measurement (M1 to M3, A-2's reading at the
  specification) are the owner's actions.
- MODELLING_ASSUMPTION: n_max = 2, verified by M3's measured n.
- ASSUMPTION: plane-of-array irradiance stays below the threshold. If it does not, D4 sits above its standoff and below its
  breakdown, under 1 mA.
- COMPONENT_LIMITATION: J_SOLAR and PV_IN for A-3(c).
- CONDITIONAL: A-3(a) and A-4 on L4-E7's drafted input limit.
- For the owner to send: route 1's clarification drafts for SunPower and Solbian.

**Owner decision required:** none. REQ-016 is unchanged; buying the unit is an action under the owner's authority, not a
question.
