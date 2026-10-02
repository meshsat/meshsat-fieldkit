accepted: yes

# Layer 4, L4-E12: Claude's check of the heat-rejection comparison at 8dfaa311 (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026. The consolidation (L4-E9 at `a0212d9e`) found that the approved PS-IDLE-SPEC profile, 43.413 W into
the case, needs 1.447 W/K at REQ-024's +40 C, against a conservative bound of about 0.6 W/K. Under the owner's rule for a function
still failing, the round (section 15, output section 10) compares three heat-rejection approaches inside the rulings (no vent, the
Peli 1450 kept, a 3 mm aluminium face):
- (a) fins on the face's free 0.0552 m2;
- (b) the large loads (23.641 W) conducted into the plate;
- (c) the open lid as a second radiator through a braid.

**Verified by the coordinator:**
- *Reproduction:* `l4e12_thermal.py` re-run at `8dfaa311`, its output equal to the committed `.out` byte for byte;
  `test_l4e12` with `test_public_hygiene` 27 passed, 0 failed. No em or en dash.
- *The needs:* 43.413 W over the 30 K from +40 C to the +70 C class is 1.447 W/K. Charging with the profile running, the cells'
  42 C charge start over the design day's 13.2 to 18.3 C air, is 43.413 / 28.8 to 43.413 / 23.7 = 1.507 to 1.832 W/K.
- *Route (b) in a separate estimate:* the plate alone, with an up-facing natural-convection film and radiation (emissivity 0.70,
  view 0.70), rejects the 23.641 W led into it at about 71.1 C at +40 C. The round's two-node model gives the plate 70.08 C with the
  inside air's share added, consistent within about 1 K. Fins alone barely help because the plate's inside film limits them;
  leading the loads into the plate bypasses that film. The physics of the ranking is right.
- *The result is stated as a shortfall, not as a pass:* all three together give 1.384 W/K (42.161 W rejected against 43.413 W at
  the +70 C line, 1.252 W short). Charging with the profile running is 0.153 to 0.472 W/K short. The conservative bound credits the
  fans' inside airflow at zero, and no held document bounds it, so the fact that decides it is a reading.

**Accepted** as U-02's statement: a closure condition. The missing fact is the sealed case's conductance lid open with the fans
running, read by one bench point: lid open, fans at full duty, 42.4 W spread as the boards dissipate, room air, steady state.
- At 1.509 W/K or more, the profile works at +40 C with no route.
- At 1.575 W/K or more, charging works on the design day's cold end; at 1.930 W/K or more, on its warm end.
- Below 1.509 W/K, the combined route is built and measured at the same point. If it still reads short, the owner's options remain: an
  alternative duty cycle at +40 C, labelled (PS-IDLE's 40.242 W fits the combined route with 1.919 W to spare), or a requirement
  change.
