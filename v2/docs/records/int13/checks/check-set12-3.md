mergeable: yes

# AI review: third look at the RF-002 walk's B1 (declared EMCON toggle) and the LED-load follow-up, fnd/rf2walk3 at f7597bd7 (MESHSAT-1357)

This is an AI review, not a qualified engineering review. It was read from the shared scratch clone detached at `f7597bd747794670febf90a3e23ba46ba06f8b4b`, fetched from the rf2walk3 worktree, where `w/rf2walk3` is the same sha, on 29 Sep 2026 from 14:31 to 14:36 CEST (times from `date`).
- **Nothing written outside scratch:** no worktree and not the main checkout.
- **Rule tools:** run from a scratch cwd with `VERDICT_DIR` in the scratchpad.
- **My scripts** are in `_chk/`: the earlier ones plus `cx_walk4.py`. `rb12_mutants.py` is extended with two LED-feed mutants.

**Counts: 0 blocking, 6 minor.** B1 is closed. Every reading reproduces byte for byte, and the LED follow-up and its read-back check out.

## Blocking items

None.

## (1) B1: the declared toggle (8c143c24)

**The declaration is correctly sourced.** `EMCON_TOGGLES` says board C, SW_EMCON, value "EMCON locking toggle", line TX_INHIBIT_n. The sources agree with it:
- `gen_sch_c.py` line 306: SW_EMCON lug 1 on TX_INHIBIT_n, lug 2 on GND, lug 3 NC.
- `gen_sch_c.py` lines 302 and 137 to 140: lug 2 is the common.
- The APEM 5000 sheet, page 6, 5636 row: I is 1-2 and III is 2-3, so lug 2 is the common. I checked this in `v2/vendor/seals/`.
- `PANEL.md`: the Switches row (line 58) and the TX_INHIBIT_n row (line 155).

On set 12's board C, `_is_toggle('C', ...)` matches the real SW_EMCON. No other board carries a SW on an asserted line.

**How the declaration is used.** Every caller of `_is_toggle`, `_switch_board`, `_source_output`, `drive_net` and `_line_sources` in the walk passes the board key (census 1385 and 1392, `_line_sources` 1785 to 1794, `fail_safe` 2290, `_fs_base` 2465). Other switches are ordinary contacts. In the census, a contact to ground can only assert the line, a contact to a rail FAILs, and a contact to a signal net is followed. In the fail-safe states the contact is taken closed.

**My three scripts on the new walk** match the author's filed `readings/b1r3/check-*-new-walk.txt` line for line:

| Case | EMCON_HW / TX_INHIBIT_n | As stated |
|---|---|---|
| CX10 (latch on B plus a switch to GND on B), CX10b (plus a switch to +3V3_DEV) | FAIL / FAIL | yes |
| cx_walk3: the latch plus a switch to GND, both forms, main's and D4E-F1's shape | FAIL / FAIL | yes |
| CX14, main's shape | PASS / FAIL | yes |
| CX14, D4E-F1 shape | UNDECIDED / FAIL | yes |
| CX9, CX9c, CX3, CX3b, CX3c | FAIL / FAIL | yes |
| CX11, CX12 | PASS / PASS | yes |
| latch on board C from the +5V it receives | FAIL (the author's fixture and table; the brief's "PASS" is a slip, and FAIL is right: the latch stays powered with board C down) | yes |
| CX13 | FAIL / PASS (a conservative false FAIL, stated in `_switch_board`) | yes |
| CX0 to CX8 | as in the earlier rounds | yes |

**Break attempts (`_chk/cx_walk4.py`), judged with the kit's own declaration (`toggles=EMCON_TOGGLES`), not the test file's FIXTURE_TOGGLES.** The fixture list declares SW_EMCON on every board, so it cannot be used for these cases.

| Attempt | Result | Judgement |
|---|---|---|
| T1 latch on B plus a second SW_EMCON on B, same value, TX_INHIBIT_n to GND | FAIL / FAIL | holds: the board is checked |
| T1b a second SW_EMCON on B from TX_INHIBIT_n to +3V3_DEV | UNDECIDED / FAIL | holds |
| T2b C's SW_EMCON lug 2 on +3V3; T2c its value changed; T2d lug 3 on a lamp net | FAIL / FAIL | holds (not the toggle, so conservative) |
| T3a contact on B from TX_INHIBIT_n to a net pulled to +3V3_DEV by 10k; T3b to an expander pin; T3c through two contacts in series to +3V3_DEV | UNDECIDED / FAIL | holds: the path is followed |
| T3d contact on B from EMCON_HW to a net pulled up | FAIL / FAIL | holds |
| T4 a JP solder jumper, an S1 pushbutton, a K1 relay contact or a 2-pin link header J_BR1 on B, from TX_INHIBIT_n to +3V3_DEV | UNDECIDED / UNDECIDED | not hidden, but not FAIL either (minor 2) |
| **T2a** C's SW_EMCON with lug 1 on TX_INHIBIT_n, lug 2 (the common) NC and lug 3 on GND: a toggle that can never ground the line | **PASS / PASS** | not caught (minor 1). Also PASS on the previous walk (06eb61ef), so it is not caused by this change |

## (2) Readings and tests

`check_contracts.py` was run into scratch on a `git archive` of each whole `v2/ecad`. Every output is `cmp`-identical to its file in `readings/b1r3/`.

- **Set 12's netlists under their writing generator (eafb324d):** 0 FAIL, 11 UNDECIDED, 15 PASS on the new walk and on the previous walk (06eb61ef). The two files are byte-identical, and identical to my second-round HEAD reading.
- **Main (2c7730a4):** 0 FAIL, 11 UNDECIDED, 15 PASS on both walks, byte-identical. Main's own walk gives 7 UNDECIDED and 18 PASS (the earlier reading, same file).
- **dd7230a7 (the int13 line with CHK12-B applied, board B not regenerated):** 20 UNJUDGED and 5 PASS on both walks, with board B refused as UNKNOWN GENERATOR, as recorded.

Tests: `tests/run.py test_tx_inhibit` gives 142 passed, 0 failed (138 in `test_tx_inhibit.py` plus the split guard). The new fixtures state properties on fixtures, each with a defective and an acceptable case (CX10 in both shapes, CX14, the legitimate shapes, and "only the declared toggle is a source").

## (3) apply_b_chk12_led.py and the extended read-back

- **Base:** dd7230a7's `gen_sch_b.py` is exactly HEAD's plus `apply_b_chk12.py`, which I checked by applying it in scratch and comparing with `cmp`.
- **Applying the follow-up** in scratch: the dry run finds its anchor once, the apply gives +6 lines, a second run is refused, and on HEAD's generator it refuses without CHK12-B.
- **Netlist facts:** Q{s}01 is a BC857 with its emitter on +3V3_CM{s}, feeding red LED17 through R{s}50 (1k), with its base through R{s}49 (10k) from LED_nPWR. R{s}48 (1k) feeds green LED16 into LED_nACT.
- **Figures:** 3.3 mA each, as 3.3 V over 1k. Slot 3's rail sums to 0.100 + 14 x 0.001 + 2 x 0.0033 = 0.121 A against its 0.20 A peak. With either LED's forward drop taken, the real feed is well under 3.3 mA; minor 4 covers the wording.
- **Read-back** `readback_chk12.py` on set 12's committed board B: 13 FAIL, identical to the filed reading (the three new LED-feed rows among them).
- **Self-test:** the synthetic after-pair passes and its three mutants fail.
- **My mutants** all fail as wanted: the five earlier ones, plus Q301 left out of +3V3_CM3's loads and R148 left out of +3V3_CM1's. The LED check derives the feeds from the netlist (a BC857 on the rail, or a resistor from the rail to a net that carries an LED), and it FAILs if it finds none.

## (4) New

- EMCON.md 4d.6 and the start-up dip added to E-04 match the arithmetic. With R527 at 16.5k the all-rails-lost margin would be 92 mV and the released margin 51 mV, so keeping 20.0k is a stated trade.
- The integration line dd7230a7 has board B unjudged until CHK12-B and CHK12-LED are regenerated together, as the README says.

## Minor items

1. **`_is_toggle` (tx_inhibit.py, after `EMCON_TOGGLES`) ignores lug numbers,** so T2a (the APEM common lug left open) reads PASS on both lines although that toggle can never assert EMCON. The kit had a lug-2 error until the 26 September fix-up (`gen_sch_c.py` lines 137 to 140), and no gate checks the lugs today. This is not a back-drive path and it predates this branch. Fix: put the pins in the declaration (line lug "1", ground lug "2", lug "3" open, from `gen_sch_c.py` 306 and the APEM 5636 row) and match them. Add T2a as a defective fixture.
2. **The ordinary-contact rule is keyed on the SW prefix.** A solder jumper (JP), a relay contact (K), an S-prefixed switch or a link header from TX_INHIBIT_n to a rail reads UNDECIDED rather than FAIL. Nothing is hidden, but classing JP and K parts as contacts would decide those cases.
3. **The board key defaults to None** in `_switch_board`, `_source_output`, `drive_net` and `_line_sources`, and with None `_is_toggle` skips the board check. Every walk caller passes the key today; making it mandatory keeps it that way.
4. **The LED figure's stated derivation, "the rail over 1 k with no LED drop", is not by itself an upper bound.** Rail +5 %, the 1k's unstated tolerance (5 %) and Q{s}01's base current through R{s}49 give about 3.9 mA. With the LED's own drop the feed is well under 3.3 mA; say that instead.
5. **README wording:** "each FAILs on the previous walk". The test file does not load on the previous walk (it reads `T.EMCON_TOGGLES` at import), so that claim rests on the checker-script readings (`b1r3/check-*-previous-walk.txt`, which I reproduce), not on the fixtures themselves.
6. **The M2a margin with every rail lost stays 30 mV** (0.37 V against 0.4 V), as stated.
