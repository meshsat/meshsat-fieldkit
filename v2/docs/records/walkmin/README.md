# Walk minors: the EMCON toggle's lugs and the board key (MESHSAT-1357, 29 September 2026)

The independent check of stream rf2walk, round 3 (set 12's CHECK-3, filed as `records/int13/checks/check-set12-3.md`),
accepted the walk with minors on `v2/ecad/tools/tx_inhibit.py`; this record answers its items 1 and 3. Its item 2 (the
SW-prefix contact rule) stays open and is not answered here. `apply_walk_minors.py` answers them. It asserts each
old text once and refuses a second run.

- **m1.** The toggle declaration named no lugs. A toggle wired across two throws that never close together (lugs 1 and 3
  of the APEM 5636ADKB-2V), or across the other lever position's contact (2 and 3), read as the line's source.
  - Every declaration now names its contact lug pair (`lugs`), with the maker's page (`lugs_src`: the APEM 5000 series
    sheet, page 6, the 5636 row: 1 and 2 closed in position I, 2 and 3 in position III, lug 2 the common).
  - `_is_toggle` requires the two live pins to be exactly that pair, the line on one and ground on the other, in either
    order (the contact is symmetric).
- **m2.** The board key defaulted to None, and a call without it matched a declaration on any board.
  - The key is now required by `_is_toggle`, `_switch_board`, `_source_output`, `drive_net` and `_line_sources`.
  - `_is_toggle` refuses a missing key, and a declaration without its lugs, with a ValueError.
  - Production code already passed the key everywhere; only tests did not, and they now do.

Tests:
- The new test `t_the_toggle_is_its_declared_contact_and_its_board_key_is_required` fails on the previous predicate (it
  stops at the first missing `lugs` key); taken one at a time on the previous predicate, each miswired case (lugs 1 and 3,
  3 and 1, 3 and 2, 2 and 3) is accepted there, as the independent check measured (`checks/check-walkmin-1.md`).
- After the check (its minor 2), a declaration's lug pair must be two distinct lugs; the test refuses `("1", "1")`.
- `test_tx_inhibit` reads 143 passed, 0 failed.

The kit's own toggle is wired lug 1 on TX_INHIBIT_n and lug 2 on GND (`gen_sch_c.py`), so no board's reading is expected
to move. The change stales RF-002's readings by the tool's digest, so the integrator re-takes them and compares them with
main's.
