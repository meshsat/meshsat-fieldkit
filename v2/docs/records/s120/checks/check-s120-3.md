mergeable: yes

# Independent check of stream s120, round 3 (S-120, third issue)

AI review (desk arithmetic on the makers' documents and the committed netlists, done by running and reproducing), not a
qualified engineering review. 29 September 2026, 19:14 CEST. Checker did not write the work. Rounds 1 and 2: `CHECK.md`,
`CHECK-2.md` beside this file.

Checked: `fnd/s120` at `8c504a24429a24a535f7e085a4b14df5193431ba` (confirmed), four commits on `afcdb557` (`723c7412`,
`0a164e97`, `a774acac`, `8c504a24`; the last changes only LOG.md and dryrun.out), all as the owner, no trailer. Clone
`<scratch>/chk-s120` detached at the tip; `<scratch>/chk-s120/_int14` at `b874b744` for main's tools. Netlists of A and E
unchanged (`6c40250c47195ebb`, `2ed95a0e8069ebf8`). No en or em dash in the six records. No commit, no push, no agent, no
box.

Round 2's blocking item is closed and n1 to n7 are answered. Nothing blocking remains.

## Blocking

None.

## Minors

r1. S-124's closing test refers every overshoot to the bus ("each overshoot over the measured bus added to 20.96 V ... and
to 23.40 V"). CH_SW2, and with it Q9's VDS (SW2) and Q10's (VBAT less SW2), ride VBAT, not the bus (Table 9-3 p.27;
the record's own section 5). If the charger ever runs buck boost and SW2 switches, "SW2's peak less the measured bus" plus
20.96 V understates SW2 by the gap between the bench's VBAT and its worst (20.0 V at SYSOVP, p.14). In buck mode SW2 sits
at VBAT with Q10 on, so this matters only if SW2 switches. Suggested wording: "CH_SW2's overshoot over the measured VBAT
added to 20.0 V". (`apply_registry_s120.py`, the S-124 closing test; README section 7 quotation.)

r2. The closing test does not name ACP less ACN (0.5 V absolute, SLUSE66A p.8). With no CACP or CACN drawn, the
differential filter is R146 and R147 (10 Ohm each) with C121 10 nF, a 200 ns time constant. By my arithmetic (INFERRED) a
4.7 V ring near 48 MHz (1 nH against 11 nF, the record's model) reaches the pins at about 0.08 V. So this is low weight;
reading it on the bench costs nothing.

r3. The `.out` header still says "second issue" (`vbus20_bound.out` line 2, printed by `vbus20_bound.py` line 264; the
docstring on line 3 names both issues).

r4. A correction to my round 2 fixtures. My mutant builder attached each added part's second pin to the first
`(name "GND")` in the file, which is a library pin, so those pins landed on +3V3. The round 2 conclusions are unaffected,
because they concerned pin 1's net: membership FAIL for the bypass, and the old sense filter gate FAIL for C998. The round 3
fixtures below were rebuilt on the net declaration and read back through `netlist_sexp.py` (C998 and C997 on
CH_ACN_F/CH_ACP_F and GND).

## The five items, as reproduced

1. **B1 is closed.** S-124's closing test, as applied, equals the coordinator's quotation and the README's word for word
   (compared as parsed strings). It now carries "CH_SW1 and CH_SW2 no lower than -2 V, or -4 V for at most 25 ns
   (SLUSE66A page 8)", read against U3's PGND.
   * All parts of the test are joined by "and", so none can be skipped.
   * The OVP trip reading is part of the test.
   * Remedies "are measured the same way".
   * The layout reading "does not close this item".
   * It cannot close with SW1 or SW2 below its limits, nor without a prototype measurement.
   * The SW1 undershoot model reproduces: 3.0 V (4 V less VSD 1.0 V) over 9.77, 8.77 and 6.66 A/ns gives 0.31, 0.34 and
     0.45 nH, labelled MODEL.
2. **The new bound.**
   * SNVSAI1D 7.3.1 p.14: the buck high side is "turned off by the oscillator clock signal". 7.3.5 p.16: it "skips a
     cycle if the sensed voltage does not fall below this threshold". Both read.
   * Valley limit (94 + 1.9) mV over 4.95 mOhm is 19.374 A. A full period at 60 V with L1 at 8 uH and 175 kHz adds
     26.39 A, giving 45.76 A. At 12 uH that is 12.57 mJ, and the bus reaches 23.397 V.
   * To reach 29.0 V from the trip would take 245.1 mJ, 19.5 times that.
   * Rise rate 28.9 V per ms; 0.24 ms (42 cycles) to reach 30 V.
   * Sensitivities: 12.9, 22.4, 36.7, 41.5 and 51.1 percent.
   * Margins at 23.40 V: Q8 6.60, Q7 5.60, U3 VBUS 8.60, recommended 26 V 2.60, BTST1 8.30 (38 V) and 2.30 (32 V).
   * DC and dump columns are unchanged: 9.04 / 8.04 / 11.04 / 5.04 / 10.74 / 4.74 and 7.76 / 6.76 / 9.76 / 3.76 / 9.46 /
     3.46.
   * `vbus20_bound.py` reprints the committed `.out` byte for byte (exit 0).
   * 23.20 V survives only as the labelled steady current limit cycle figure: `.out` 51 and 106, README 74, and the
     S-124 and S-120 texts. It also appears in history lines (README 13, LOG, `dryrun.out` 101 and 138). Nothing uses it as
     the bound.
3. **n1 to n7.**
   * n1: no order is claimed while the charger switches through ACOV's deglitch, in the `.out`, README 8, the closing
     evidence and S-111's addition.
   * n2: as item 2.
   * n3: 1.52, 1.76 and 2.38 nH on Q7's turn-on edge, reproduced.
   * n4: the strap's percentages come from the parsed values (my R27 20.0k printed 59.58 to 60.54 % and "NOT inside"). U3's
     pin line prints "NOT on GND" when pin 5 moves (my round 1 fixture). A value without a tolerance prints nan and FAILs.
   * n5: the sense filter is a record line; my added CACN and CACP pass (exit 0) and the record lines name them.
   * n6: MODEL and INFERRED column labels; "not reached at the INFERRED bound"; the 22 V standoff sentence is qualified.
   * n7: Q7's VDS is taken from CH_ACN to CH_SW1.
4. **The 20 fact gate with my own fixtures.** My S expression reader confirms VBUS20's 39 pins exactly, the strap
   (74.76 to 75.51 percent), and R150 and R151 into U2 pins 16 and 15.
   * These FAIL (exit 1), each FAIL line printing what the fixture holds:
     * a 100 nF bypass on VBUS20 (membership)
     * a D1 copy from VBUS20 to GND (membership and clamp)
     * R27 at 20.0k (strap)
     * R26 with no tolerance (strap)
     * R150 at 1k (CS filter)
     * the round 1 fixtures: R6 249k, Q7 as CSD18510Q5B, U3 pin 5 moved
   * These PASS (exit 0):
     * TI's 33 nF CACN and CACP to GND (record lines show C998 and C997)
     * R150 and R151 at 4.99 Ohm (the gate asks at most 100 Ohm, which bounds the 1.9 mV offset)
     * R27 at 39.2k (inside the window)
5. **The registry.** The tip's registry equals `b874b744`'s (sha256/16 1dde1fd16f4e260e). `--check` with the short
   `8c504a24` wrote nothing. On scratch copies of both:
   * S-120 is closed by `commit 8c504a24429a24a535f7e085a4b14df5193431ba`.
   * S-124 is opened (SESSION, OPEN).
   * REQ-015 waits on S-106, S-107, S-111, S-124.
   * S-120 is appended after S-121.
   * The two applied copies are byte identical, and a second run refuses.
   * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings on all four copies (main's tools at `b874b744` and
     the tip's).
   * `afcdb557` (README differs) and `a774acac` (LOG differs) are refused, so the integrator passes the tip or a merge that
     carries it, as README section 10 now says.
   * Nothing claims ringing is bounded: README 1, 7 and 11, `.out` 10 and 12, the closing evidence ("not bounded at desk
     ... carried by S-124") and S-124 itself.
   * The bound is labelled INFERRED with its MODEL energy term everywhere it is stated; the dump and line figures are
     labelled MODEL.

## Counts

Blocking 0. Minor 4 (r1 to r3 on the work, r4 a correction of my own round 2 fixtures). Round 2 items: B1 closed, n1 to
n7 answered. Facts 20 of 20 reproduced by an independent reader. Fixtures: 8 FAIL as intended, 3 PASS as intended,
including the added CACN. Registry copies 4 of 4 at 0 errors and 0 warnings; S-124 opened on both registries; `closed_by`
40 characters. Every figure of `.out` sections 2 to 11 re-derived; all agree at the printed decimals.
