# Integration set 12 (MESHSAT-1357, 29 September 2026)

Branch `fnd/int13`. The integrator's scripts, read-backs and checks for set 12. Nothing here is built. The checks filed under
`checks/` are AI reviews, not a qualified engineering review.

## What the set carries

- **Stream d4emcon: FEA-002's remedies at desk.**
  - Board B: back-feed gates for the RockBLOCK, both E72 and the E22; U543 on the RockBLOCK enable; U554 on the 5G card's
    power-off line.
  - Board C: R52 and D23 on EMCON_HW (D4E-F1).
- **RF-002's walk, rounds 2 and 3 (stream rf2walk).** The EMCON toggle is declared as data, and the check's minors are applied
  to board B (`apply_b_chk12.py`, `apply_b_chk12_led.py`).
- **Stream s117: board A's charger set to its inductor and FETs.** Decisions 56 and 57; S-117 and S-118 closed; S-119 and
  S-120 opened.
- **Census node declarations** (`apply_emcon_hw_node_c.py`, `apply_census_nodes_set12.py`, `apply_census_nodes2_set12.py`):
  EMCON_HW on C; IADPT and CH_COMP1 on A; ZBA_RXD, ZBB_RXD and LED_ACT_A1 to A3 on B.
- **Boards A, B and C regenerated on the box** (`box_regen_bc.sh` with `REGEN_BOARDS`).
  - Read back: `readback-*.txt`.
  - Pins and sheets moved on parsed proofs: `apply_repin_*`, `apply_sheets_set12.py`.
  - Registry rebinds with reasons read by hand: `apply_rebind_*`, `rebind_reasons_set12.py`.
  - The page rebind: `apply_rebind_page_set12.py`.

## Checks and answers

| Check | Result | Answered by |
|---|---|---|
| `checks/check-set12-1.md` (the substance check), `checks/check-set12-2.md` and `-3.md` (its re-checks on rf2walk2 and rf2walk3) | remedies hold; B1 the walk; rf2walk3 accepted | streams rf2walk2 and rf2walk3 |
| `checks/check-int13-1.md` (the integration check at `005e5f5e`) | not mergeable: B1, and minors m1 to m9 | `apply_check13_fixes.py` (B1, m1, m2, m3, m6, m8, m9), this README (m4, m5, m7), the re-take at the corrected commit (m5) |
| `checks/check-int13-2.md` (the focused re-check at `69156cad`) | not mergeable: B1 carried (the first answer claimed rows it had not read), and five minors | `apply_conops_4b_set12.py` (section 4b and the EMCON row rewritten whole from the netlists, B1 and minors 1 to 3), this README (minors 4 and 5) |
| `checks/check-int13-3.md` (the targeted re-check at `7a9f7b5b`) | not mergeable: the rewrite true pin by pin, but CFL-016's entry claimed a reading of the other documents that no check made | `apply_cfl016_set12.py` (a change of diagnosis: CFL-016 reads FAIL and waits on S-122, the documents re-read whole) |
| `checks/check-int13-4.md` (the re-check at `d0717859`, the promoted commit) | mergeable: 0 blocking, 4 wording minors | carried to S-122's stream |

The suite at `005e5f5e` failed 3 tests:
- a 191k resistor with no order code;
- two census tests that need the held FET datasheets.

Both were answered by `58d2ea3f`: an order code row in `lcsc_fill.py`, and the two datasheets as pin-out drawings in the
census test.

## Notes the check asked for

- **m4, line citations.** The generator entries of set 12 do not state the line shifts.
  - `gen_sch_a.py` moved by +35 lines from main's line 860 and by +55 from main's line 910 (the focused re-check's measure; the first note said after 857 and 907).
  - Older registry citations of `gen_sch_a.py` lines are dated to the sha they were read at, so read them there. Examples:
    CON-019 `:1237-1245` and `:1291-1304`, CON-018 `:1200-1210`, and REQ-077 lines 1262 and 1267.
  - The second-pass `gen_sch_b.py` entries also cover the LED feed loads of `apply_b_chk12_led.py`.
- **m5, a precondition of every re-take.**
  - Install the held-back makers' documents first: `v2/docs/records/s117/fetch_held_back.py`. The box receives them appended
    to the evidence archive.
  - Without them, board A's PWR-001 reading records no sha for the CSD17577Q5A and CSD17578Q5A sheets, and the census test
    fails.
  - The re-take at the corrected commit is taken with them installed.
- **m7, carried.** Two wording points go to the next regeneration of board B:
  - the LED_ACT_A1 to A3 node basis says no part takes its supply from the net;
  - the ZB and LED nodes take v_max from the rail's nominal 3.3 V rather than 3.46 V.

  Neither changes a reading. Correcting either means regenerating board B's intent file.
