# l8p: W4DP-F2's breaker drawn for boards P, E and A (Layer 8, MESHSAT-1357)

**Round 7 (5 October 2026, branch `fnd/l8p2` from `2c258cf9`): record l9stk's guard selection G2 CHECKED before any draft; NOT
CONFIRMED on one figure, so NO G2 draft; L8P-F07 stays OPEN and L8P-F08 is new and OPEN.** Done: the check (`l8p_guard.py`,
`l8p_guard.out`, page 12k), the recheck V2R's V2R-m8 (19h and 15c under the stale-copies guard) and V2R-m9 (E-8 and E-14 (a)
restated per device, page 12l, 12g, 13g). Not done: the G2 apply script, its composition, netlist and mutations, and its
judgement on C-PROT (the brief stops the draft at a figure that does not reproduce). Next action: the selection's owner (record
l9stk) or the coordinator picks one of 12k's three corrections (this record recommends the 2N7002 shunt), then this record drafts G2.
- **The finding, L8P-F08.** G2's AO3400A on DOCK_EN_RET leaks, by record l9stk's own count, 43.6 uA at its assumed 86.25 C site.
  With it, L4-E11 20c's window fails: a ramping closed loop reads held between DOCK_EN_OUT 1.825 and 2.12 V (45.7 uA on the return
  against the 26.45 uA allowed). 20c says such a reading "stops a dead pack's precharge". Record l9stk's own window check compared
  the closed loop's ratio, 0.590, not a ramp's reading.
- **Everything else reproduces** on the makers' sheets (12k's table), with three relabellings:
  - the switch's trip accuracy is printed at VDD 5 V only;
  - the regulator's 2.25 uA ground current is printed at VIN 6.0 V only;
  - its accuracy is printed from 100 uA of load.

### For the next independent check (round 7)

| Item | Where | What to read |
|---|---|---|
| G2 checked on the sheets | `l8p_guard.py` sections 1 to 6; `l8p_guard.out`; page 12k | each PRINTED figure against TI SNIS144G, SBVS186H (held back, `fetch_held_back.py`), AOS AO3400A Rev 3.1, JSCJ 2N7002; the loop's readings at tolerance |
| L8P-F08, the window with the shunt's leakage | `l8p_guard.out` 5 (e); page 12k and section 9 | 26.45 uA allowed, 45.7 uA at l9stk's site; 0.770 V at the most favourable corners; 77.9 C as the site limit |
| The stop | page 12k "The stop"; `apply_gen_sch_a_ptc.py` unchanged | no G2 draft exists; this is the first negative check of G2 as selected |
| The correction scope | `l8p_guard.out` 7; page 12k | the 2N7002 (7.7 uA), 11 kOhm (tripped VIN condition from 11.93 V), the site under 77.9 C; DERIVED, not drafted |
| V2R-m8 | `l8p_drafts.py` `L4E11_SECTIONS`, `inputs/l4e11-section19h-4def5975.md`, `inputs/l4e11-section15c-precharge-4def5975.md`, `inputs/SOURCES.txt` | both under the guard; a scratch mutation of each fails (`test_l8p.t_round7_v2r_m8_19h_and_15c_are_under_the_guard`) |
| V2R-m9 | page 12l, 12g (E-14 (a)), 13g (E-8); `l8p_guard.out` 8; `inputs/l4e11-sections23d-24b-08f7e38a.md` | the pair's reading lies between its junctions; RthJC 0.8 K/W times the pair's power plus the mounting bases' difference; L4-E11's method (B) quoted, unchecked |
| E11-45 (c), for L4-E11 | page 12l | the 1 mA clause bounds each junction within 0.8 mK of its base; the VSD clause reads nothing per device |

**Round 6b (4 October 2026 late evening, branch `fnd/l8p2` from `053901ea`): the copies of L4-E11 taken again at its round 13.**
L4-E11 moved one more round after round 6 (`fnd/l4e11r11` at `4def5975`), and on the coordinator's merged candidate this
record's own guard fired, as round 6 built it to (`test_l8p.t_round6_no_copy_of_l4e11_is_a_round_behind_the_tree`).
- **Retaken at `4def5975`:** the four drafts and sections 20c, 20d, 20e, 22b, 22c, 22g, 22h; round 12's copies removed
  (`inputs/SOURCES.txt`, round 6b). The copies' names are now built from two values in `l8p_drafts.py` (`L4E11_AT`,
  `L4E11_ROUND`).
- **What changed: one copy of eleven, section 20c.** L4-E11 restated it on Murata's printed points: record l9stk's "bound point"
  (the loop at 10.6 V with RT1 at 47 kOhm, the first inverter's gate at 2.894 V) is withdrawn as a bound.
- **Which quoted figures moved: none.** The held and closed readings (0.7755 V, 0.84 V), the powered reading (1.981 V), the dead
  and alive readings (4.076 V, 4.774 V), the load on the return (2 uA), the window (25.8 kOhm), the first inverter's band (61.3
  to 201.2 kOhm), the delays (0.85 ms, 1.41 ms, 1.341 s), the two limits (0.846 mA, 520.7 uA), the hot bound (434.8 uA) and
  everything L8P-F06 and E-14c derive from them read as in round 6. `l8p_drafts.out` changed only in the copies' names and pins
  and in four new lines of section 3b.
- **What no longer stands, and where this record leant on it:** one sentence of 12e ("so l9stk's bound point of the inverters
  and the thermal guard is unchanged"), restated; 12f gains L4-E11's own words on the withdrawal, quoted from the copy. It
  agrees with L8P-F07, which stays OPEN.
- **Scratch checks of round 6b** (read-only `git merge-tree`, then a scratch overlay, deleted): the merge with `4def5975` is
  CLEAN; it brings `records/l4e11/`, `test_l4e11.py` and `test-procedures/TP-E11-29.md`. On it `l8p_drafts.py` prints this
  `l8p_drafts.out` byte for byte; `test_l8p` 22 passed; `test_l4e11` 71 passed, 2 failed with L4-E11's pin of this record's PTC
  draft as it is at `4def5975` (still the old sha256), and 73 passed, 0 failed after `apply_test_l4e11_ptc_pin.py --write` on
  the overlay's copy.
- **Not in this round:** the guard's draft (this record's next round, with its own brief); V2's targeted recheck of round 6.

**Round 6 (4 October 2026 evening, branch `fnd/l8p2` from `69156072`): the independent check V2's findings for this record
answered; UNVERIFIED until its targeted recheck. L8P-F06 and L8P-F07 stay OPEN.** V2 (an AI review; it read `fnd/v2cand` at
`dfa1eef2`, which held round 5) confirmed the ideal diode as conditional and F06 and F07 as real and correctly open, and did not
confirm two statements, V2-B2 and V2-B3. The thermal guard's redesign (L8P-F07's correction) is NOT in this round: record l9stk's
author is comparing approaches.

### V2's findings answered (for the targeted recheck)

| Finding | What changed | File |
|---|---|---|
| **V2-B2** (blocking): the F06 figures and one interface quote a round behind the candidate | Every copy of L4-E11 taken again at its round 12, `fnd/l4e11r11` at `ac72e730` (four drafts; sections 20c, 20d, 20e, 22b, 22c, 22g, 22h); round 10's copies removed; boards A and E recomposed with those drafts; the output regenerated through `_bin/regen_out.py` | `inputs/SOURCES.txt` (round 6), `inputs/*-ac72e730.*`, `l8p_drafts.py` (`INPUT_FILES`, `SOURCES_SHA`, `REPLACED`, `FOLLOW`), `l8p_drafts.out` sections 1, 3b, 5, 7 |
| V2-B2, F06 on round 12's budget | F06 against BOTH limits. Timing 520.7 uA (the pack at 16.8 V): 473.9 uA for the pair, 236.95 uA a FET, 85.9 uA in hand at the ASSUMED 388.0 uA, filled from a 103.9 C case or by a doubling every 9.63 K. Static 0.846 mA (the 29.2 V clamp): 786.8 uA, 393.4 uA, 398.8 uA, 111.2 C, 8.82 K. The timing limit and the 1.218 s bleed are reproduced from L4-E11's printed inputs (520.9 uA against 520.7); L4-E11's own derived figures are read from the copies and the script refuses if they part | `l8p_drafts.py` (`round5`), `l8p_drafts.out` 3d and 9, `L8P-BREAKER.md` 12j (the F06 table) and section 9 |
| V2-B2, E-14c | Acceptance: the pair at most 388 uA at the 101.0 C held case, stated as keeping both limits; over 473.9 uA reverses L4-E11's R256 selection; between, L4-E11's E11-45 (f2) | `L8P-BREAKER.md` 12j and section 7 (the register row) |
| V2-B2, 12f's release row | The quote "dead under 4.076 V" is round 12's (4.147 V was round 11's, withdrawn); two rows added for the limits, quoted from 20e | `L8P-BREAKER.md` 12f |
| V2-B2, why no test saw it | `stale_copies()` compares every copy with `records/l4e11/` wherever a tree holds L4-E11's round 10 or later; run on L4-E11's real trees it reports rounds 10 and 11 and passes round 12 | `l8p_drafts.py`, `test_l8p.t_round6_no_copy_of_l4e11_is_a_round_behind_the_tree` |
| **V2-B3** (blocking): TDK B59721A0130A062, "no k exists at 7.6 V" | `tdk_window()` takes the sure-off as a LOWER bound: `max(k_low, k_trip) <= k_notrip`. A window exists: 10.51 to 10.62 at 7.6 V (1.0 % wide), 8.53 to 10.62 at 10.6 V. A mutation of the direction fails a scan of the three conditions | `l8p_drafts.py` (`tdk_window`, `round5`), `test_l8p.t_round6_tdks_window_takes_the_sure_off_as_a_lower_bound` |
| V2-B3, NOT SELECTED | Stands on three grounds, each with its printed figure: 18.1 to 21.4 mW in the part against the sheet's p.4 note (under 6 mW while measuring); 4.11 to 5.01 mA of static draw against 0.45 mA; the sheet's own p.29 table (typical, reference only), Rmin 212 ohm at 100 C, on which no k exists at either voltage. The SESSION decision's reason restated | `l8p_drafts.out` 3d, `L8P-BREAKER.md` 12j (the alternatives table, the SESSION decision) |
| **V2-m5** (this record's half): the trip side added the even split's 1.88 K | Restated on L4-E11's worst split: 1.513 W, 2.12 K over the hottest FET's own mounting base, 135.1 C if that base sat at the sensor's copper; the base against the sensor's copper named NOT BOUNDED (14.9 K left to 150 C), pointing at E11-29's added reading | `l8p_drafts.py`, `l8p_drafts.out` 3d, `L8P-BREAKER.md` 12j (the trip rows) and section 7 |
| **V2-m7**: E-16 does not read U105 | E-16's acceptance gains "U105's package at most 125 C at 23.93 A held" (TI prints V(AK REG) for TJ -40 to 125 C only) | `L8P-BREAKER.md` 13g |
| **V2-m8**: the pads cannot all be the sheet's | One sentence in E-8: three test boards are 6.75 in2, board P is 4.77 in2 a face and dissipates 4.57 W in all at 23.93 A held; E-8's specimen measures the joint case | `L8P-BREAKER.md` 13g, `l8p_drafts.py` (`dd5_budget`), `l8p_drafts.out` 3c |
| **V2-m9** (this record's half): board A composed in the main-era order | Composed in L4-E9's list order as the candidate carries it (rows 24 to 33). Not in this tree and named: l8r2's packrtn, slotlm, fb01 (board A) and packrtn (board E). In the tree and not in the list, composed in a second pass: l8r2's d8v3 and vbus20ov. `test_l8p` composes the whole list wherever a tree holds its drafts | `l8p_drafts.py` (`ORDER`, `LIST_ABSENT`, `TREE_ONLY`, `list_order_full`), `l8p_drafts.out` 5 to 7, `L8P-BREAKER.md` section 6 |
| V2-m4 (the row that is this record's): C3 given as "between 25 C and 110 C" | Restated as V1 worded it (about 90 C and 120 C) | `L8P-BREAKER.md` 12i |
| The PTC draft's "47 kOhm at 130 C" (the coordinator's brief, item 7) | Corrected to what Murata prints (100 kOhm over 110 C, 4.7 MOhm at 130 +-3 C) in the docstring, in the comment the draft writes and in RT1's value text | `apply_gen_sch_a_ptc.py` |

**Found on the way (for other owners):**
- **L4-E11 and the integrator:** `test_l4e11.py` pins this record's PTC draft by sha256 (`L8P3_PTC`). Round 6's correction of
  that draft moves its sha256, so on a line holding both, one L4-E11 test stops at the pin. `apply_test_l4e11_ptc_pin.py` is a
  one-line draft for the integrator (it refuses unless the tree's PTC draft is the round 6 one).
- **L4-E9's list owner:** L4-E11's DD-7 draft applied after d8dec31's mainpb is refused (mainpb then holds R233 and C241): the
  list's order, R-217 before R-193, is a hard constraint and not a preference (page section 6).

**Scratch checks of round 6** (read-only: `git merge-tree`, then a scratch overlay of this tree; no merge in progress, nothing
written in any worktree; the overlay is deleted):
- The merge with `ac72e730`: CLEAN; it brings only `records/l4e11/` and `test_l4e11.py`. On it `l8p_drafts.py` prints this
  `l8p_drafts.out` byte for byte; `test_l8p` 21 passed; `test_l4e11` 68 passed, 1 failed (the pin above), and 69 passed, 0
  failed after `apply_test_l4e11_ptc_pin.py --write` on the overlay's copy.
- The same overlay with l8r2's four list drafts of `dfa1eef2` laid in: `test_l8p` 21 passed; the whole list composed (board A 16
  drafts, 778 parts, intent written, DRAWN; board E 15 drafts, 295 parts, DRAWN).

**Not done, and whose it is:** V2's targeted recheck of these corrections; the committed candidate and its suite (the
integrator); the box's KiCad export; E-14c, E-13 and the other bench items; the TI and Murata questions (drafted, UNSENT); the
thermal guard's redesign (record l9stk).

**Round 5** (the check V1's condition C4, DONE on this branch then; superseded in part by round 6): `check_l8p_netlist.py`'s board
A EN group admits DD-7's readers by pin (L4E11-R10-F2) and three mutations of the composed board A fail it; the compositions use
L4-E11's drafts with no stand-in; 12f restated by quotes; 12j's findings L8P-F06 and L8P-F07 with the Murata and TI questions
DRAFTED and UNSENT. Its scratch merge was with `a09e9a60`.

Layer 8 record `l8p`, 4 October 2026, branch `fnd/l8p` from main `64cd25ee`. It draws record `l9stk` section 15's design
(branch `fnd/l9stk` at `0d72880b`, its latest changes CONFIRMED AS CONDITIONAL):
- an LM5069-1 latch-off breaker on board P;
- its make-last dock enable loop through boards E and A, with an RC hold through a diode;
- the PTC thermal guard on board A;
- the restart inhibit C-1c on the breaker pad (DD-8, owned here);
- round 3 (branch `fnd/l8p2` from `fnd/l8p` at `e1bc3cba`): B-R2's route R1, a reverse-charge detector on board P that holds the
  loop's return low while a latched or held-off breaker passes a charge, read by board A on the contact it already has (task
  L4-E11's round 9, `fnd/l4e11r9` at `e60a94a8`, section 19h);
- round 4 (the same branch): the correction of design defect DD-5 (BAT-F20), an ideal diode beside the charge switch Q1, so the
  discharge no longer crosses Q1's body diode while the gauge holds the charge FET off (case row C-PROT with CHGIN = 1).

Round 1 drew the record at `2c8b29fb`; round 2 (the same day) follows its move.

This is prototype design: generator text and netlists only. Nothing is built, powered or measured, and **nothing here is
applied to the tree**. Every apply script refuses the repository's own generator until a `RELEASE.md` beside it names an
accepted check of this record; none exists.

| File | What it is |
|---|---|
| `L8P-BREAKER.md` | The record page: the drafts, the values with their l9stk sections, the SESSION choices, C-1c's budget and conditions (E-12b, E-10, the lockout, the NTC's assumed tolerance), the designators, the order constraints for L4-E9's change list, the interface rows owed, the regeneration and the netlist check, findings for other authors, residuals, and (section 12) B-R2: why no existing element serves, the detector, its thresholds and limits, the service, the interface owed to L4-E11, E-14 as it now reads and E-12c; and (section 13) DD-5: the three approaches, the ideal diode, its acceptance on C-PROT with every figure labelled, the closure credit and what stays open (E-8, E-16, E-12d). |
| `apply_gen_sch_p_breaker.py` | DRAFT, board P: U101 LM5069-1, R101 and R102 (4 and 7.5 mOhm), Q101 and Q102 CSD18510Q5B, R103 8.45 k, C101 10 nF, C102 22 nF, D101 SMCJ18A, C104 and C105. The enable inverters Q103 and Q104 with R106 to R109, and the hold: R104, C103, R105 and D102 1N4148W. The restart inhibit: RT101 NXRT15 on the pad, R110 to R113, U102 OPA187, Q105 and Q106 gated by PGD (R114 to R117), C106. TP101 to TP106. Round 3, the reverse-charge detector: U103 and U104 OPA187, D103 BZT52C12, R118 to R129, C107 to C110, Q107 and Q108 on DOCK_EN_RET, TP107 and TP108. J_SMB as a 1x7 (5 DOCK_EN_RET, 6 ground, 7 DOCK_EN_OUT). R6, R7, R19 and Q2's source on BRK_VIN. |
| `apply_gen_sch_p_idealdiode.py` | DRAFT, board P, round 4 (DD-5), after the breaker draft: Q109 CSD17570Q5B beside Q1 under U105 LM74700-Q1, C111, R130, D104, R131, C112 to C115, TP109. |
| `apply_gen_sch_e_enable.py` | DRAFT, board E: J_SMB as a 1x7 pin for pin; J_BLK pins 3 and 5 on the loop with 4 ground between. |
| `apply_gen_sch_a_ptc.py` | DRAFT, board A: J_DOCK pins 3 and 5 on the loop with 4 ground between; RT1 PRF15BB103 on the battery FETs' copper. |
| `check_l8p_netlist.py` | What the regenerated netlists must show, parsed: the breaker, the loop on each board, the hold, the restart inhibit and its PGD gate, the reverse-charge detector (REV), the ideal diode beside Q1 (DIO), the ground contact between the loop conductors, and the loop's continuity across the boards. It reads NOT DRAWN on the committed netlists. |
| `gen_netlist.py` | A generator's own part table written as a KiCad-form netlist on a host without KiCad: a stand-in layout step, with `intent.write` run. |
| `fetch_held_back.py` | TI's OPA187 sheet (SBOS807E) into `v2/vendor/ti/held/` and, round 5, TDK's superior-series PTC sheet into `v2/vendor/battery/held/`, each checked by sha256 (held back by their notices). |
| `read_prf_typical.py` | Round 5: the reading of Murata's typical BB curve (DM-SA16-E056 Rev.1, 3.2) that `l8p_drafts.py` carries as `PRF_BB_TYP`, INFERRED; a reading aid, not a gate. |
| `apply_test_l4e11_ptc_pin.py` | Round 6: a one-line draft for the integrator and L4-E11's author, the sha256 by which `test_l4e11.py` pins this record's PTC draft. Not applied here. |
| `l8p_drafts.py`, `l8p_drafts.out` | The inputs pinned by sha256, the values found in l9stk's text, C-1c's budget read from the makers' sheets, B-R2's detector (section 3b), DD-5's acceptance (section 3c), each draft on a scratch copy, the composition in L4-E9's order, the designators, the regeneration and the netlist check, the intent, and the findings. Regenerated with `_bin/regen_out.py`. |
| `inputs/` | Record l9stk's section 15, its protection output and its design constants at `0d72880b`, L4-E7's backstop draft of `fnd/l4e7r6` at `914a2f5a`, and task L4-E11's sections 19h and 15c (the LDO-mode precharge) at `e60a94a8`, byte for byte, with `inputs/SOURCES.txt`; since round 6b: L4-E11's round 13 drafts and its sections 20c, 20d, 20e, 22b, 22c, 22g and 22h at `4def5975` (round 5's copies of `a09e9a60` and round 6's of `ac72e730` removed). |

Tests: `v2/ecad/tools/tests/test_l8p.py`. Run `python3 run.py test_l8p`, `test_l8r2` and `test_public_hygiene` from the tests folder, one module a run.
