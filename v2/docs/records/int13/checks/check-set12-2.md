mergeable: no

# AI review: focused re-check of set 12's walk fix and circuit minors, fnd/rf2walk2 at 06eb61ef (MESHSAT-1357)

This is an AI review, not a qualified engineering review. Read from the shared scratch clone detached at `06eb61efed3f508c273654e92c96ca8afc6f55a5` (fetched from the rf2walk2 worktree, `w/rf2walk2` at the same sha), 29 Sep 2026 14:10 to 14:17 CEST (times from `date`). Nothing in any worktree or the main checkout was written. Rule tools ran from a scratch cwd with `VERDICT_DIR` in the scratchpad. My scripts are in `_chk/`: `cx_walk.py`, `cx5b.py`, `cx_main.py` from the first check, and new `cx_walk2.py`, `cx_walk3.py`, `rb12_mutants.py`. `git status` shows only `CHECK.md`, `CHECK-2.md` and `_chk/` untracked.

Counts: 1 blocking, 5 minor. The circuit draft `apply_b_chk12.py` checks against the makers' figures. Its read-back discriminates. Every reading reproduces byte for byte.

## Blocking items

1. **B1 is not closed. The fix is keyed on "any SW on an asserted line", so adding a second switch reopens the latch.** Files: `v2/ecad/tools/tx_inhibit.py` `_switch_board` (line 1675), used at 1385 and by `_source_output`, together with `_line_sources` (1730: every SW on the line is "the toggle") and `fail_safe` (2241: the board of every counted source is taken down).
   - **Counterexample CX10** (`_chk/cx_walk2.py`, `_chk/cx_walk3.py`): CX9's latch on board B, plus a switch on board B from TX_INHIBIT_n to GND. That switch can only assert the line.
   - **Why it passes:** the switch makes board B a "switch board", so U30 and U32 count as sources again. `fail_safe` then takes board B, the readers' board, down in every fragment, so the physical state (board C down, board B up, latch holding both lines HIGH) is never solved.
   - **Readings:** on the new walk both lines PASS, in both the direct and the behind-330R form. Main's walk failed EMCON_HW in the behind-330R form (main shape), so this is again a path the old walk caught and the new one hides.
   - **Same root cause, already present on main's, the previous and the new walk (CX14):** a switch on board B from TX_INHIBIT_n to +3V3_DEV, which lifts the line when closed, reads PASS on both lines even with a powered reader on board B.
   - **Scope:** no kit board carries a SW on an asserted line other than C's SW_EMCON (checked on all six netlists), so no set 12 reading changes.
   - **Fix:** declare the toggle, the way ACCESSORIES are declared (board C, SW_EMCON, far pin on GND). Use only that declaration in `_switch_board`, `_line_sources` and `fail_safe`'s `down`. Treat any other SW on an asserted line as an ordinary part: a switch to a rail drives the line up, a switch to ground can only assert it. Add CX10 (both forms) and CX14 as defective fixtures.

## (1) B1: the walk change (149b15f7)

- **Tests:** `env -C <clone>/v2/ecad/tools python3 tests/run.py test_tx_inhibit` gives 138 passed, 0 failed. On the previous walk (a444cb37's `tx_inhibit.py` in a scratch copy) the two new tests FAIL, as recorded.
- **First check's counterexamples on the new walk:** CX3, CX3b, CX3c, CX9 and CX9c (board B) now FAIL on both lines. CX1, CX2, CX4a, CX5, CX6 and CX7 still FAIL, CX4b stays UNDECIDED, and CX0 and CX8 still PASS, all as before. CX5b (a pull-up on EMCON_HW with a TX_INHIBIT_n reader on board B) FAILs both lines through D23. The author's fixture covers the latch on board C run from the received +5V.

| New counterexample (new walk) | Physically | Walk | Judgement |
|---|---|---|---|
| CX10 latch on board B + a board B switch to GND (direct and behind 330R) | latch holds both lines HIGH with board C down | PASS, PASS | hides a real path: blocking 1 |
| CX14 board B switch from TX_INHIBIT_n to +3V3_DEV, reader on board B | closing it releases boards A and D | PASS, PASS (also on main's and the previous walk) | same root cause, not new |
| CX11 second 74LVC1G17 on board C (C's own +3V3) behind its own 330R | legitimate, dead with board C | PASS, PASS | correct |
| CX12 latch on board C from C's own +3V3 | unpowered with board C down | PASS, PASS | correct |
| CX13 toggle alone on board C, EMCON_HW made on board B by a buffer from TX_INHIBIT_n | fail-safe (R59 holds its input low) | EMCON_HW FAIL (PASS on the previous and main's walk) | conservative false FAIL: minor 1 |

## (2) The apply script, its read-back and self-test (cb717e93)

`apply_b_chk12.py` on a scratch copy of HEAD's `gen_sch_b.py`: dry run finds every anchor once, the apply takes 5 edits, and a second run is refused. The LCSC codes (C23184 49.9k, C13167 2.7k, C4184 20.0k) match `lcsc_fill.py`. Regenerating was not possible on the runner (the KiCad symbol libraries are absent), so the netlist figures below are arithmetic on set 12's netlist.

| Item | Value | Maker's figure | My check | Holds |
|---|---|---|---|---|
| M1 R238 | 49.9k 1% | RM520N HD v1.1 Table 9: VIL 0.2 V, VIH 1.19 V, internal 100 k pull-down, tolerance unstated; SCES308L VOL 0.1 V at 100 uA | 3.545/49.4k = 71.8 uA held; 3.135 x 100/150.4 = 2.08 V released; at or over 1.19 V down to a 30.8 k pull-down | yes |
| M2a R532, R527 | 2.7k 1%, 20.0k 1% | SBVS050N: VIT 2.79 V +-1.25 % (-40 to 85 C), VHYS at most 2.5 %, VOL 0.4 V at 1 mA; GC I_EN 270k/430k, Logic In HIGH 2.0 V, LOW 0.4 V | sink (2.90 - 0.40)/2.673k + 5.3/270k = 0.955 mA; released 2.10 V (2.02 V with 15k); asserted 0.15 to 0.16 V; all rails lost 20.3 uA x 18.0k = 0.37 V | yes (0.37 V is 30 mV under 0.4 V) |
| M2b R551, CT | CT to +5V_DEV (U543's VDD) through 49.9k 1% | SBVS050N 7.3.2: "a fixed 300ms typical delay time by tying CT to VDD; use a resistor from 40kOhm to 200kOhm"; 6.6: td 180/300/420 ms | CT is tied to VDD, not SENSE's rail. No held Ground Control document (hardware page, specification page, product page, RB9704 datasheet) states an I_EN-low-to-I_BTD-low time, so E-04's new measurement is the right dependency; it is in the E-04 row, and 4d.6 states it | yes, bench-dependent as stated |
| M5 intent | loads and notes of +3V3_CM1..3, +3V3_ZB | set 12 netlist | loads name exactly the U parts on each rail (4, 6, 14; U3xA aside) and R536 to R538 at 0.71 mA. The note mislabels Q{s}01 (minor 2) | yes |

- **Read-back:** `readback_chk12.py` on set 12's committed board B gives 10 FAIL of 11, identical to the filed reading; only "U543 pin 3 open" passes, as it must.
- **Self-test** (into scratch): the synthetic after-pair passes, and the three mutants fail.
- **My mutants on the same synthetic pair** (`_chk/rb12_mutants.py`) each fail as wanted:
  - R551 to +3V3_DEV
  - MR on RB_TD_CT in place of CT
  - R238 left at 100k
  - U112 missing from +3V3_CM1's loads
  - R538 missing from +3V3_ZB's loads
- **Not checked by the read-back:** "the netlist otherwise differs only by R551 and RB_TD_CT". This is stated as the integrator's comparator; `_chk/netcmp.py` does it.

## (3) Readings and anything new

- **Readings:** `check_contracts.py` into scratch, each output `cmp`-identical to its file in `records/rf2walk/readings/b1/`:
  - set 12 HEAD, new walk: 0 FAIL, 11 UNDECIDED, 15 PASS; inhibit_chain A 7/2, B 12/8, C PASS, D 8/1, E PASS, P PASS.
  - set 12 at eafb324d with the previous walk: identical bytes.
  - main with the new walk equals main with the previous walk, and equals the first round's main-fixed file.
  - main with its own walk: 7 UNDECIDED, 18 PASS.
- **Fail-safe bounds on the new walk** are unchanged: EMCON_HW 0.401 V and 0.584 V; TX_INHIBIT_n 0.354 V, 0.339 V and 0.578 V.
- **New since the first check (integration commits on this branch):** board C's netlist at HEAD equals e41df395's in every part and pin (export path and date only). The EMCON_HW node declaration in `gen_sch_c.py` matches the net (U13 pin 2 and U14 pin 6 read it on board C).

## Minor items

1. CX13: a buffer off the switch's board is now always a second driver, so a fail-safe architecture that builds EMCON_HW on board B from TX_INHIBIT_n would FAIL. This is conservative and not the kit's design; say so in `_switch_board`'s docstring.
2. M5's note says each module rail "level-shifts against it (Q{s}01 to Q{s}05 and their pull-ups)". But Q{s}01 is a BC857 LED buffer: its emitter is on the rail, and it feeds the power LED through R{s}50 1k. R{s}48 (1k) also feeds the ACT LED from the rail. About 3 mA a slot is missing from the loads, which name U parts only.
3. M2b covers the I_EN-low case. The maker's other rule, that once I_EN has been driven high the host must wait for I_BTD high before driving it low, is also broken by a dip during the module's 25 to 40 s supercapacitor charge at start-up. Add that case to E-04.
4. M2a's "every rail lost" margin is 30 mV (0.37 V against 0.4 V) and rests on the stated Ioff sum. It holds, but it is thin.
5. `apply_rebind_page_rf2walk2.py` and the registry and evidence rebinds on this branch were not reviewed (out of scope).
