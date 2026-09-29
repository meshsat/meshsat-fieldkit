# Integration set 13 (MESHSAT-1357, 29 September 2026)

Branch `fnd/int14`, from main `e57a7365`. The integrator's scripts, read-back and checks for set 13. Nothing here is built.
The checks under `checks/` are AI reviews, not a qualified engineering review.

## What the set carries

- **Stream s119: the energy chain's charger rows.**
  - U3 is restated to 0.979, and U3B is drawn on U3's 400 kHz row (decision 58).
  - Its scripts ran in the order its second check confirmed: `records/s119/`, then `apply_rebind_decisions_set13.py`.
- **Stream csi: board C's SI-001 nets.**
  - The allowance method is tied to its reference nets.
  - The four e-paper series resistors R53 to R56 are applied to `gen_sch_c.py`.
  - Board C was regenerated on the box and read back: `readback-C-epd.txt`, HOLDS.
- **The walk minors (`fnd/walkmin`):** the EMCON toggle is judged on its declared contact lugs, and the board key is
  required.
- **Board C's pin and sheet,** moved on parsed proofs: `apply_repin_c_set13.py`, `apply_sheets_set13.py`.
- **One consolidated re-take,** with the held makers' files and the IBIS models installed.
- **Board C's four records rebound** (`apply_rebind_after_circuit_set13.py`), and the evidence page
  (`apply_rebind_page_set13.py`).

## Checks and answers

| Check | Result | Answered by |
|---|---|---|
| `checks/check-int14-1.md` (the integration check at `a906b932`) | not mergeable: B1, the hand reason for CFL-016 claimed no named document describes the e-paper driver side, where PANEL.md section 3 does; eight minors | `apply_check14_fixes.py` (B1: the clause withdrawn with the rows read, the rows added to S-122; m2 as S-123; m4, m5, m8), this README (m1, m3, m6, m7) |
| `checks/check-int14-2.md` (the re-check of the first answer) | not mergeable: S-122's added sentence did not make the rows part of its closing condition; S-123 said via_audit reads signal classes and that nothing flags the readings | the same script, corrected (S-122's closing clause; S-123 reworded from the code; the rules from the coverage map; S-123 names return_stitch; csi's README line) and re-run once on `a906b932` |
| `checks/check-int14-3.md` (the re-check at `32f26b41`, the promoted commit) | mergeable: 0 blocking, 1 minor (S-123 says CONFIG_UNDECLARED where TOOL_CHANGED shows first today) | carried to S-123's next edit |

## Carried from check-int14-1

- **m1, ERC.** H1's `lib_symbol_issues` warning is absent from board C's report while H1 is unchanged. The check found
  the same omission for six parts on main (boards A, B and D), so it reads as the ERC tool's reporting, not a circuit
  change. The gate's blocking count is 0 on both sides.
- **m3, lug check.** `tx_inhibit._is_toggle` still accepts a lug pair given as the string "12", or as integers. The
  kit's declaration is a tuple of two strings. A type check is owed at the tool's next change.
- **m6, stream s119's check minors N2 to N5 and N7.** These are wording and citation points in `records/a1elec/`
  (`CHARGER.md` line 101 "the balance that meets M1" without "on the model", the fault bounds' reliance on ACX_OCP at
  its default, the ILIM_HIZ spread, and the table cited for the 6.35 A clamp) and decision 58's "one option stands
  clear". They are owed to the stream's next round.
- **m7, the circuit rebind comparator.** It lists parts added, removed or changed in value or footprint, but not parts
  whose pins moved (U3 here). The three records that name U3 rest on pin 32, which did not move.
