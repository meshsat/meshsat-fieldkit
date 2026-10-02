accepted: yes

# Layer 4, L4-E10: Claude's check of the U-01 cell route at 6995697a (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026. The owner asked for a supported cell route within the approved arrangement, with charging,
discharging and storage evaluated separately, and for whether published specifications suffice. The round (section 15, output
section 10) answers with the suitability by mode of the ruled cell, the proposal and three candidates. It fixes the pocket-room
parser and carries U-02's conservative conductance bound into each row.

**Verified by the coordinator:**
- *Reproduction:* `l4e10_cell_thermal.py` re-run at `6995697a`, its output equal to the committed `.out` byte for byte;
  `test_l4e10` with `test_public_hygiene` pass. No em or en dash.
- *The parser fix (the verifier's item 3):* CASE-MARGINS row M5 now reads the chosen design's +3.65 mm, and the room as designed
  is 0.0865 L. The only rejection that moves is approach III's latent storage in E5 (0.102 L no longer fits), from INCONCLUSIVE to
  REJECTED. The verifier's lead is confirmed.
- *The Saft MP 176065 xtd, read on its held datasheet* (Saft doc 31109-2-0625, sha256 `8ca0a3e0...`, held back):
  - charge -30 to +85 C at up to 5.6 A ("~1C rate"), with a footnote that operation below 0 C is optimised by consulting Saft;
  - discharge -40 to +85 C, 11 A continuous, 22 A pulses with no duration stated;
  - storage "Allowable -40 C to +85 C" (recommended +15 to +30 C);
  - 5.6 Ah typical at 3.65 V, 135 g, 18.65 x 60.5 x 68.7 mm, with footnote 3: the thickness "Can increase with temperature and
    during battery life".
  4 x 3.65 V x 5.6 Ah = 81.8 Wh nominal; the round's usable 53.5 to 55.1 Wh gives 1.25 to 1.29 h at the 42.8 W profile.
- *The classification holds:* the Saft's cell-limit rows hold on published evidence. Two items need Saft or a bench: the 18 A for
  60 s peak (the pulse row states no duration), and the capacity recovery after storage at the allowable extremes (the
  "allowable" limit is not a recovery figure; the round reads it as covering 24 h at the stored charge, an interpretation it
  labels). The axial fit is open on the swelling footnote and on the pocket's open placement.
- *The ruled 35E is unsuitable on its own published evidence* for +71 C and -33 C storage, the E5 dwell and E3-O. The
  HL18650V's rows rest on a vendor answer or a soak test.

**Accepted** as U-01's statement: a supported route exists on published manufacturer evidence, at a cost of energy (about 145 to
about 82 Wh nominal) and money. Its adoption needs the owner's approval of D-06's cell, energy and spend. It stays CONDITIONAL on
the axial fit (a printed mock-up, no purchase), on the 18 A for 60 s (Saft or a one-day bench test), and on T-H1 for LO-01a's
complete pass and LO-01e.

**Carried to the consolidation:** on the conservative bound, a kit running the idle profile reaches the cells' 42 C charge start
only below -30.6 C ambient. Whether the pack can charge in normal operation therefore also rests on T-H1. That is a finding on the
power architecture (U-02's reach), not on the cell.
