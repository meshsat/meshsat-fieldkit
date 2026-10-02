accepted: yes

# Layer 4, L4-E12: Claude's closing check of the electronics' thermal record at a86be47b (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1478 under MESHSAT-1357, 2 October 2026. Both collaborator runs on L4-E12 are spent:
- the focused check `astra-check-l4e12-1.md` on `bcd23532`, NOT YET; the hold changed E3-O's configuration;
- the targeted recheck `astra-check-l4e12-2.md` on `39fe74c4`, NOT YET; the SGP41's path and the rating categories.

The final round is `a86be47b`. **This check accepts the record as a correct statement: U-02 is CONDITIONAL, and one genuine owner
question remains, CFL-002 (the SGP41).**

**Verified by the coordinator:**
- *Reproduction:* `l4e12_thermal.py` re-run at `a86be47b`, its output equal to the committed `.out` byte for byte;
  `test_l4e12` with `test_public_hygiene` 20 passed, 0 failed, 0 skipped.
- *The conductance arithmetic (separate arithmetic, earlier round, unchanged):*
  - E3-O with everything on, 27.086 W: needs 27.086 / 15 = 1.806 W/K for +70 C mixed air;
  - E5 under the hold, 21.587 W at 2.159 W/K: 70.00 C;
  - E3-O at that line: 67.55 C.
- *E3-O's configuration:* kept as TEST-PLAN line 26 states, with the monitor and radios on and C1's shedding the only control
  action. The hold acts only in E5, whose configuration requires logging and not the radios. That holds once its reference is
  placed in the mixed air or calibrated to ±0.899099 K; with the TMP117 where it is, the window does not exist.
- *The SGP41's maker limits, read on the sheet* (Sensirion SGP41, v1.0, section 2.3, Table 4, p.6):
  - "Gas Sensing Specifications ... are guaranteed only when the sensor is stored and operated under the recommended conditions":
    operating -10 to +50 C, storage 5 to 30 C;
  - Table 5 (absolute): operating -20 to +55 C, short-term storage -40 to +70 C.
- *The SGP41's location route was bounded before any owner question.*
  - The coolest spot that still samples the bay air is the inside face of the east wall in the pack pocket. It needs 2.535 W/K
    lid closed, above every conductance the record carries; at 2.0 W/K the wall reads 50.58 C.
  - Storage fails at any location, against the envelope's -20 to +45 C.
  - The question is therefore genuine: CHO-001's owner pick against REQ-042's VOC channel under D-02a's envelope, which is CFL-002
    as Layer 3 recorded it.
- *The rating provenance:* every judged limit names its category, and absolute ratings only exclude. 33 lines stay INCONCLUSIVE
  on an absolute rating alone, as they should until a maker statement covers them.

**U-02's conditions (none closed here):**
- T-H1, lid open with fans, at or above 2.159 W/K (E3-O alone needs 1.806);
- the hold's reference placed in the mixed air, or calibrated;
- the SGP41's protective shutdown (TMP117 at ±0.15 C maximum, the switch and its own bus) and Sensirion's duration answer;
- the owner's answer on CFL-002;
- the +85 C pushbuttons and PDi's storage statement;
- the TLV75533 regulators (MESHSAT-1479);
- the +70 C parts kept out of the cooler exhaust;
- the fans' rating (architecture-level: they carry the conductance);
- the other unrated lines and the absolute-only lines, as Layer 6 evidence.
