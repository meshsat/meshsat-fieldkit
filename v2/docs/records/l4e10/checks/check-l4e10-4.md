accepted: yes

# Layer 4, L4-E10: Claude's check of the U-01 round at 4d5271eb (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026. On the owner's instruction of the same day, the round establishes the proposed cell's charging,
discharging and storage limits separately with their conditions, the charging constraints, and usable energy. It is section 14
of the page and section 9 of the output. FEA-008 stays open, and no cell is adopted.

**Verified by the coordinator:**
- *Reproduction:* `l4e10_cell_thermal.py` re-run at `4d5271eb`, its output equal to the committed `.out` byte for byte;
  `test_l4e10` with `test_public_hygiene` pass. No em or en dash.
- *The limits by mode come from the maker's page and are classed MAKER-PAGE, not as a specification.* The pinned transcription
  (`inputs/topwell-hl18650v-page-2026-10-01.json`, page sha256 `25dd8ee2...`) reads:
  - charge -20 to 60 C, in bands of 0.1C to 4.1 V, 0.2C to 4.2 V and 0.5C to 4.2 V (the coldest band's edge printed garbled);
  - discharge -40 to 85 C, end voltages 2.75 / 2.5 / 2.0 V by band, 10 A continuous, 1.4 A maximum charge;
  - storage rows by duration, with no state of charge.

  The round's table carries exactly these, and names for each row what the signed specification must confirm.
- *The charging constraints are drafts:* 0.84 A and 1.68 A are 0.1C and 0.2C of the 3P pack at 2.8 Ah; 3.00 A is 0.357C,
  inside 0.5C; 16.40 and 16.80 V are 4.1 and 4.2 V a cell. The cold charge stop moves to -9 C. Below it no charge starts and the
  heater warms the block, from the pack under the discharge limit or from the input subject to U-04.
- *Usable energy in separate arithmetic:* 107.9 Wh for the 35E at +25 C is the replay's figure (`l4e_replay.out` line 39), and
  107.9 x 2.8 / 3.35 = 90.19 Wh for the HL18650V, on the stated assumption that its curve shape is the 35E's. The sensitivity is
  3.221 Wh per 100 mAh a cell. The cold figures are ranges built from the 35E's and the 30Q6's own points, labelled ASSUMPTION.
- *The heater's energy:* the round's figures (1.6 to 2.8, 3.4 to 12.3 and 5.7 Wh) lie at or above the cells' own sensible heat
  with no losses (12 x 47 g at 0.9 J/(g K): 1.55, 2.96 and 4.37 Wh), as a figure that adds the block and its losses must.
- *What the signed specification would change:* each row carries the threshold at which the architecture is affected, and its
  fallback: (I) the 35E with powered cooling, (III) a primary-fed storage heater needing an owner ruling on D-06, or a
  requirement change, which is the owner's. With no answer, every row stays CONDITIONAL and U-01 a release gate.

**Accepted** as the U-01 statement at the engineering level. The vendor question (the signed specification) and the adoption
(the owner's approval of the cell change) stay open. L4-E9 must re-pin L4-E10's output, page and Topwell draft.
