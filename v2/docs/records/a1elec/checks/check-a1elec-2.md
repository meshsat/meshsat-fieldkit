acceptable: yes
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026); the scratch paths are redacted. -->

# Focused re-check of fnd/a1elec at 06568798 (answers to CHECK.md), MESHSAT-1357

**AI review** (the same independent Claude checker; wrote none of the work), 29 September 2026, 03:17 to 03:22 CEST.
Not a qualified review. Scope as asked: only whether B1, B2 and M1 to M10 are answered correctly, plus the new k = 3
claim. Scratch clone `_scratch/chk-a1elec`, detached at 06568798 (commits 546e25f6, a55ab834, 70c059ec, 2ea329f4,
06568798 after a21eca38; they touch only records/a1elec/). Nothing committed or pushed; no box, Agent or Codex call.

## Reproduced

- `energy_two_pack.py`, `gauge_scale.py`, `checks/recheck_two_pack.py` rerun at 06568798: exit 0, all three outputs
  byte-identical to the committed ones; the clone stays clean apart from my check files.
- My own model (`CHECK-own_two_pack.py`, no shared code; ceilings at 3.968 and 7.936 A): E1, U3 at 4.15 A: stops at 44
  and 32 (`.out`: [44, 32]). E2, U3 at 6.2 A: lowest 30.3 base, 0.7 lid, 31.05 together (`.out` 31.1); lid 20 C 88.98,
  7.5 C stops at 24 and 36, base 15 C 9.66; threshold between 9.5 and 9.6 C. Entry requirement by my own bisection:
  **5.559 A** to meet at all, **5.811 A** to stay within 0.05 Wh of the unconstrained 31.05 Wh (`.out`: 5.56 and 5.81).
  All agree.

## B1 and B2: answered correctly

- **B1.** The LM5176 limit is now 43 / 50 / 57 mV, 4.3 / 5.0 / 5.7 A, taken at the 4.3 A minimum (`fe_out_w` 89.0 W),
  with SNVSAI1D 6.5 page 7 cited. **E1**: U3 IIN_HOST 4.15 A (code 83 at 50 mA on 10 mOhm; 4.25 A maximum with the
  register text's 100 mA, SLUSE66A 9.6.22) sits under the 4.3 A minimum: NOT MET at any lid temperature and at 800 Wp.
  The three tolerance rows (329.4 / 119.1 Wh unserved, 18.6 Wh) match what I computed in CHECK.md. **E2**: R11 6.2 mOhm
  gives 43 / 50 / 57 mV / 6.2 = 6.94 / 8.06 / 9.19 A; U3 IIN_HOST 6.2 A (code 124), 6.3 A maximum, under both the 6.35 A
  clamp (9.3.5) and the 6.94 A minimum, so U3's loop holds the bus in every part. It meets with 31.1 Wh. L2's peak at E2
  (10.32 A at 400 kHz) is under the 12.2 A value text, and the L2, 800 kHz and R16 changes are now labelled margin
  choices. Board A's heat figures in the E1 (8.4 W) and E2 (14.2 W) columns check.
- **B2.** TOPOLOGY 6 now has rows for Q10B shorted, Q7B shorted, Q_LS shorted (or U_LS's gate stuck on) and Q_E1 open,
  each marked a single fault. The paths and bounds are as I stated them. The old double-fault row is replaced by "U3B
  off". Q_LD is kept. The hardware bounds in 1.3, 3c and the threshold table are qualified as fault-free and point to
  section 6. The Q_LS row honestly says that the base's OCC1 opening in time is not shown.

## Minors: all answered

M1: EN_FAST_5MOHM is written 0b on U3B, and on U3 if its R16 becomes 5 mOhm. That is correct: the clamp note applies
under RSNS_RAC = 1b only. M2: the discharge-path loss is now 6.0 Wh. M3: current limit is now modelled linear (1.0 /
12.0 / 42.7 W at 1 / 2 / 4.8 V gaps; my arithmetic agrees). M4: the requirement is stated and the margin choices are
separated. M5: R_AND 100 k and the Q_E1-open row. M6: the shoulder-hour rule. M7: the heading is reworded. M8: the
XAL6030 / L6060 mismatch is named in CHARGER and `.out` 7. M9: standby drain 1.38 to 1.73 mA, 1.0 to 1.25 Ah a month,
with IIN-EN and IIN-DIS read from SNVS452G page 5 (checked). M10: the ceilings are at their register values.

## The k = 3 claim for a 4S14P lid: correct

14 x 3,350 mAh = 46,900 mAh, and x 14.40 V = 67,536 cWh (69,552 at 3.45 Ah). At k = 2 the cWh word would be 33,768,
above the I2 maximum of 32,767 (SLUUAQ3A Table 14-1 row 0x444f), so k = 3 is the smallest integer that fits: 22,512 and
23,184 cWh, 15,634 mAh. A 4S8P lid (38,592 cWh) needs k = 2, as stated. The mechanism is SLUA760's integer scaling
(its own examples use 2x and 4x). Note: `gauge_scale.py` has K = 2 as a constant and a 4S12P true-value table, so a 4S14P
lid needs an edit, not just a re-run. At k = 3 its away-from-zero rounding moves each threshold by at most 2 mA true.

## New minor items introduced by the answer (none blocking)

- **N1.** TOPOLOGY 3b (lines 127 and 128) still says "charging the base first or the lid first gives the same lowest
  points (`.out` 4)". Under the drafted cap, `.out` 4 now gives 31.1 Wh charging the base first and **23.5 Wh** charging
  the lid first (base 22.8 Wh). The capacity-proportional law the host draft uses gives 31.1 Wh, so no verdict moves,
  but the sentence must be restated: under a capped entry the allocation matters.
- **N2.** CHARGER.md 1, E3 bullet: "both packs are full by 13 UTC each day" is true of E3. Under E2 both are full at
  15 UTC (my trace, hour 33). The argument still holds (full before the 17 UTC deficit); fix the figure.
- **N3.** `.out` section 8 prints its table header twice; the old header line was left in `energy_two_pack.py`.
- **N4.** CHARGER.md 3, E3 column: with R16 at 10 mOhm (0.67 W) the column sums to about 19.3 W, not 19.0 W.
- **N5 (observation).** E2 runs U3 at its 6.2 A nominal. SLUSE66A gives no 10 mOhm accuracy row; its 5 mOhm rows are
  plus or minus 200 mA of the code. The model keeps 31.1 Wh down to 5.85 A, so the page's own rule (a limit holding a
  load taken at its minimum) is met with margin. One sentence would say so.
