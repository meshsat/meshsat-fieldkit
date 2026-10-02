accepted: yes

# Layer 4, L4-E7R: Claude's closing check of the CS101 correction at 675b8068 (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026. Check 3 (`check-l4e7r-3.md`, at `237cd9be`) confirmed the static bound, the dynamic allowance and
the off-by-default threshold. It did not accept the decision, on one material defect: the backstop tripped under TEST-PLAN M2
(CS101) and stopped solar charging. The correction is `675b8068`, made under the owner's bounded comparison of 2 October. This
check independently recomputes the worst immunity case and the worst protection-response case.

- **The failure, reproduced in the record.** At round 3's setting the trip's lowest sat 0.0335 A above the regulation's
  highest, and round 3's circuit trips at all 121 frequencies. That breaks M2's "no upset of the kit's operation" (REQ-063),
  through solar charging stopping. It is not a reset and no bearer is lost. M2's wording is unchanged.
- **The correction:**
  - the 50 V bulk (C11, C12, C69) moves ahead of the sense bank;
  - five 100 nF C0G capacitors go across R66, for 3.960 to 4.496 ms;
  - R66 becomes 8.45k and RIMON_IN 31.6k.

  Neither remedy alone works. Filtering alone fails at the low end, because the charge it would have to hold exceeds check
  (b)'s budget. Capacitance ahead alone fails from 46 Hz up, because CS101 holds the voltage across J_SOLAR.
- **The worst protection-response case, recomputed by the coordinator.**
  - The filter holds at most 25 V x 3.7408 A x 4.496 ms = **0.4205 J** above the trip, for any waveform. The bound comes from
    integrating the first-order filter: the input's excess over the threshold integrates to at most tau x the threshold.
  - The window's 10 J, less 0.1 s at the 93.5521 W static bound, less the capacitors' 141.1 mJ, less that held charge,
    leaves 0.0832 J.
  - At the source's whole 6.802 A x 25 V = 170.05 W against the bound, that allows **1.087 ms** after the trip, 27 times
    the typical response. Equal to the record.
- **The worst immunity case, recomputed by the coordinator** from the model's bank currents with the bulk ahead:
  - at 2121 Hz, 3.0719 A peak through the filter at its least time constant (corner 40.19 Hz) gives **0.0582 A**; the record
    prints 0.0585 A;
  - at 30 Hz, 0.0231 A gives 0.0185 A;
  - both are under the 0.1130 A margin, the trip's lowest less the regulation's highest.
- **What the sensor does and does not see is stated.** The bulk's charge (96.5 mJ) is counted at J_SOLAR in check (b), so
  moving it ahead of the sensor hides no consumption.
- **Run by the coordinator at `675b8068`:** the output reproduced byte for byte; `test_l4e7` with `test_public_hygiene` 40
  passed, 0 failed, 0 skipped.

**Result: accepted.** L4-E7R's architecture criterion is met. The backstop on SWEN, off by default, holds REQ-016's 100 W at
the panel entry with a static bound of 93.5521 W, and does not trip under CS101 in the model. It carries these conditions,
none able to overturn the architecture:
- the converter's input-current loop under CS101 is modelled from typical rows; its ripple contribution can be 2.51 times the
  model before the margin is spent (M2 reads it);
- the bulk's temperature under CS101 is conditional (up to 4.45 times its ripple rating, read at M2);
- the bank's pulse capability is conditional (Vishay);
- the 0.1 s window is an interpretation for layer 8 (REQ-016 states none);
- G_CM and the INA169's VIN+ bias: break-evens 168.8 % and 22.0 mA.

Single faults (a shorted filter capacitor defeats the backstop) go to layer 8's fault analysis. Physical CS101 validation is
the downstream M2 procedure in the record.
