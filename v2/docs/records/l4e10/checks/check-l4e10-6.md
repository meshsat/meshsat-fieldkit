accepted: yes

# Layer 4, L4-E10: Claude's check of the battery comparison at 166b9fe9 (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026. The owner (item 2 of the 14:20 amendment) asked for one compact comparison between the approved pack and
the Saft route on the same profile and energy boundary. The round (section 16, output section 11) gives it, with every cell of the table
classed GUARANTEED (a maker's printed limit), MODELLED or AWAITING.

**Verified by the coordinator:**
- *Reproduction:* `l4e10_cell_thermal.py` re-run at `166b9fe9`, its output equal to the committed `.out` byte for byte; `test_l4e10`
  with `test_public_hygiene` pass. The claim-word test of `test_l4e10` accepts only the exact uppercase class label GUARANTEED, which
  the owner asked for, and `test_public_hygiene` is unchanged.
- *The nominal energies, in separate arithmetic:*
  - D-06's figure is 12 x 3.35 Ah (Ver. 1.1's printed minimum) x 3.60 V = 144.72 Wh, and with the 35E's typical 3.45 Ah it is
    149.04 Wh;
  - the Saft pack is 4 x 5.60 Ah (typical; Saft prints no minimum) x 3.65 V = 81.76 Wh;
  - the ratio is 0.565 against the 35E's minimum (43.5 % less) and 0.5486 typical against typical (45.1 % less), as the round states.
- *The runtimes on one boundary* (the 42.8 W profile, the 3.00 V graceful shutdown, 0.80 ageing, +20 C):
  - the 35E's usable fraction is 107.9 / 144.72 = 0.7456;
  - the Saft's 0.6735 follows from one parallel string carrying 3.08 A a cell, against 0.99 A in the 3P block, on the 35E's borrowed
    curves (MODELLED: Saft prints no discharge curve), giving 81.76 x 0.6735 = 55.07 Wh and 1.287 h;
  - at the same C-rate it would be 1.33 to 1.37 h. Only Saft's curve settles it, which is AWAITING.
- *Compatibility:* the Saft keeps the 16.8 V strap, the 3.0 A charge setting and the 2.50 V cutoff, which carry to the selected
  BQ25730 (whose ChargeVoltage and cell strap rows match the BQ25731's, L4-E11 check 5). Using its +85 C range needs U2's 83 C variant,
  a re-derived network and new gauge data, which are stated.

**Accepted** as the comparison. The recommendation is held to the evidence:
- the Saft is the one route whose maker prints limits for every margin row;
- it costs about 45 % of the nominal energy, about half the battery-only runtime, and about ten times the money;
- the evidence does not yet support adopting it: the fit mock-up, 18 A for 60 s, Saft's missing figures, the gauge data and T-H1 are
  AWAITING;
- the HL18650V and the 35E as ruled keep their stated standing;
- the owner's approval of the cell change and of any purchase is required and is not given;
- the 48 to 72 h objective is reported apart.
L4-E9 and L4-E12 must re-pin L4-E10's output and page.
