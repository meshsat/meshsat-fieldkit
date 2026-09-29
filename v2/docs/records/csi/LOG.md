# Stream csi, log (29 September 2026, CEST; `date` read before each label)

## Round 1

- 14:38 Brief read. Worktree `csi` under the stream worktrees, branch `fnd/csi` from `fnd/int13` (`e553e43a`). The
  thirteen IBIS models copied from `w5si2` as ignored files; `ibis_fetch.py --check`: 13 present.
- 14:40 SI-001 on board C re-taken in scratch with the base tool: the committed reading reproduced exactly (23
  layout-bound, all BOUND_DECIDES, 1 undecided: EMCON_HW_DRV, no class entry). Per net, its governing drivers listed.
- 14:42 Read `edge_length.py` (what answers a net: an impedance target, a 10 to 150 ohm series resistor between two
  signal nets, an `edge_allow` entry), `pcb_edge_rates.yaml`, w5si2's README section 6 and finding F-Q1 (W5SI-D3).
- 14:45 The makers searched (`readings/maker-search-2026-09-29.txt`): no RP2040 IBIS model anywhere Raspberry Pi
  publishes; no Diodes 74LVC1G34 model. Raspberry Pi's minimal KiCad design fetched to scratch (MIT, not committed).
- 14:48 The hardware design guide read (p. 10 QSPI, p. 11 crystal, p. 12 USB 27 ohm) and the datasheet's SWD section.
- 14:50 Decided: QSPI takes an allowance (a series resistor is against the maker's guidance); the tool is changed to
  hold an allowance's basis (CSI-D1) and its length (CSI-D2). EPD_SW stays open under W5SI-D3; HB1 to HB3, SCL, SDA
  and EXP_INT are not closable on board C.
- 14:52 to 14:59 Tool, tests, `measure_minimal.py`, board C's declarations, the apply script, read-back and stand-in.
- 15:00 Commit `a18e90e9`; readings: C 23, 11 and 7 layout-bound; B identical.
- 15:04 README, LOG and readings; commit `a2d9bd32`.

## Round 2, the independent check of `a2d9bd32` (not mergeable: B1 to B3, m1 to m11)

- 15:25 The check read. B1: the routed half compared `max_mm` only for nets with a declared rise past their critical
  length, and board C declares no rise for any allowance net. B2: `max_mm` tied to nothing cited. B3: C24 routes the
  eleven at 3.3 to 23.9 times the limits, and the record called them decided.
- Between 15:25 and 15:38, in this order: `routed_main` changed (every net a held entry names is held to its `max_mm`
  first); `allow_refusal` changed (`max_mm` required and at most the cited lengths scaled by the reference layout's
  delay over board C's slowest; pattern, quote, PDF page and documents outside the repository refused, m7);
  `measure_minimal.py` states the reference board (1.0 mm, two layers, every net on F.Cu with no via) and its delay,
  5.572 ps/mm by the tool's own outer-layer formula, against board C's slowest 7.154 ps/mm (limits scaled by 0.779, the
  clock held to its own length, m2); `board_c_layout.py` written (C24's routed lengths reproduce the check's to the
  hundredth, and every net's farthest pad pair is past its limit); board C's table rewritten (eight entries, Q3_G's
  basis with its RC, the SWD reasoning labelled the session's, `_edge_allow_why` "pending the layout"); tests (fourteen
  refusal cases, a routed test on a stub board with board C's table; on the previous tool the new and changed tests
  fail, the routed one INCONCLUSIVE with nothing over its limit); `rules_status.py` (the two documents declared, the
  comment's line numbers); nine test files, 152 passed; commit `69409613` behind the pre-commit check's PASSED line;
  readings re-taken in scratch views (C 23, 11 and 7 layout-bound, the eleven now allowed pending the layout; C24
  through the routed half on a stub: FAIL, 11 over their limits; A, B, D, E and P identical but for `allowed_nets: 0`;
  apply and read-back as before).
- 15:38 `test_requirements`: the same five failures on the base view and on the branch.
- 15:40 README rewritten whole (section 9 answers the check item by item) and this log.

## Round 3, the re-check of `6605f3f6` (not mergeable: R2-B1, R2-B2, m1 to m4)

- 16:13 The re-check read. R2-B1 is the second failure of round 1's B2 (`max_mm` on any length of any file, for any net),
  so the method is replaced, not patched. R2-B2: the four e-paper lines were counted decided on a placement nothing holds.
- Between 16:13 and 16:24, in this order: `allow_limit` rewritten on `reference_nets` (only their length rows and the
  delay row, one document, a row naming another net or none refused); the evidence prints both lengths to the
  hundredth (m1); `ALLOW_PENDS_LAYOUT` keeps the schematic reading INCONCLUSIVE while any net is allowed (m3);
  `measure_minimal.py` also measures the maker's two pin-to-27R stubs (2.56 and 2.81 mm); board C's entries carry
  `reference_nets` and the new listing's sha; tests (the re-check's counterexamples as fixtures and on the committed
  entries, the pending guard, m1); `r2_counterexamples.py` shows the round 2 tool holding all four cases and this one
  refusing them; `board_c_layout.py` reads only held entries (m4), holds the pin-to-resistor stubs to 2.1 mm (the maker's
  runs scaled; the guide's "placed close to the chip") and reports each U3 pin's nearest escape via (m2); commit
  `171fb51a` behind the PASSED line; readings re-taken (C 23, 11, 7 layout-bound, the eleven pending; C24's R2 and R3
  stubs 71.79 and 92.31 mm, thirteen items past; the routed half on C24 FAIL, 11 over; A, B, D, E, P unchanged); on the
  round 2 tool five edge_length tests fail; on this one nine files, 152 passed.
- 16:24 `test_requirements`: the same five failures as on the base.
- 16:26 README rewritten whole: 1 decided, 4 decided in the schematic pending the layout, 11 allowed pending the layout,
  7 open; section 9 answers both checks item by item.
