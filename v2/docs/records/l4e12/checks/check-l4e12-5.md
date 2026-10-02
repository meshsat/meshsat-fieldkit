accepted: yes

# Layer 4, L4-E12: Claude's check of the U-02 bound at aab69775 (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026. The owner asked whether T-H1 confirms an already-supported design or decides whether it can work.
The round answers with a conservative first-principles lower bound on the sealed case's conductance (section 14, output
section 9): **T-H1 decides; U-02 stays a closure condition.**

**Verified by the coordinator:**
- *Reproduction:* `l4e12_thermal.py` re-run at `aab69775`, its output equal to the committed `.out` byte for byte;
  `test_l4e12` with `test_public_hygiene` 26 passed, 0 failed, 0 skipped. No em or en dash.
- *The bound, in separate code (a series model, lid open, E5's +60 C ambient):*
  - inside, a natural-convection film of 3.85 to 4.13 W/m2K (the fans' airflow credited at zero);
  - the polypropylene wall, 0.12 W/mK over 5.34 mm;
  - outside, natural convection about 3.3 W/m2K plus radiation at emissivity 0.85 on the walls, and 0.70 on the plate with a 0.70 view past the open lid;
  - the floor taken as adiabatic.
  The coordinator's model gives 0.569 to 0.596 W/K, against the round's 0.566 to 0.607 W/K. With a perfect inside film it gives
  about 1.72 W/K (the round's 1.540 to 1.571). Either way, the outside surfaces cannot pass E5's 2.159 W/K or E3-O's 1.806 W/K.
- *The reconciliation with the budget's 1.22 W/K is right:* that figure is W4's sensitivity estimate, whose low end already
  assumes a 10 W/m2K inside film from the fans. No held document bounds the fans' film, so it cannot be credited in a
  conservative bound.
- *The consequence:*
  - With every session measure (plate coupling, the deeper hold in E5, board B's +80 C connectors to +85 C parts, the HX
    magnetics, the wider buttons), the binding limit becomes the module's +85 C intake.
  - E5 needs 0.621 W/K and the bound gives 0.671 W/K: it holds.
  - E3-O needs 0.903 W/K against 0.691 W/K: a gap of 0.212 W/K, the intake at 92.61 C.
  - The credits that could close the gap (the mixers' airflow, the boards' radiation, the floor's support) are exactly what
    T-H1 measures.
- *The experiment is bounded and decides:*
  - one lid-open, fans-on point at 21.2 W spread as E5's hold;
  - room temperature, eight thermocouple channels;
  - run until the air drifts at most 0.1 K per hour (5.9 to 21.1 h);
  - acceptance bands at 2.462 / 1.516 / 0.951 W/K, each including the expanded uncertainty;
  - below 0.951 W/K, E3-O as stated cannot hold on the session's means, and the owner decides (a deviation of E3-O or a
    device-set re-pick).

**Accepted** as a correct statement: U-02 is a closure condition, decided by one bounded experiment. The bound also lies far under
LO-01a's 1.6664 W/K lid closed; that is carried to U-01.
