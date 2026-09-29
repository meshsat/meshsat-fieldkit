acceptable: yes
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026): acceptable, no blocking item; N1 to N4 answered in reconcile_lid_panel.py's notes and RECONCILE.md. -->

# AI review: focused re-check of the two-pack lid reconciliation, fnd/a1int at 637c9876 (MESHSAT-1357)

This is an AI review, not a qualified engineering review; every figure is a model result on the September reference day,
nothing is measured. Re-checked 29 September 2026, 12:25 to about 12:35 CEST, in the same shared clone, detached at
637c9876832935c3a5e2ef3329bbb1cdaddead6e (verified), against the first check (`CHECK.md`, filed as
`checks/check-a1int-1.md`). Read-only; my scripts and outputs for this pass are in `_chk2/` (untracked). Materiality as
in the first check.

**Blocking items: none. Minor items: 4 (N1 to N4), all wording or stale sensitivity figures; no verdict or quoted margin
changes.**

## (1) B1 answered

- `reconcile_lid_panel.py` (second issue) runs exit 0 and its output is byte-identical to the committed `.out`
  (sha256 b7620512...).
- The runtime entry (line 55) copies E2's front-end cap (`fe_out_w`, 43 mV over 6.2 mOhm, 143.6 W) and changes only
  U3's input (`u3_in_w` = 6.2, 6.1 or 6.0 A x 20.7 V). The nominal rows equal the first issue's figures exactly.
- All 21 printed rows (every lid, ratio and U3 value: verdict, lowest base, lid and both, unserved energy, lid
  threshold) agree with my independent balance at a 1 h step, with U3B at 7.936 A, to 0.05 Wh and 0.05 K
  (`_chk2/cmp2.out`: 21 rows, 0 differing). At ratio C:
  - 4S14P: 87.4 Wh and +5.9 C at 6.1 A; 77.6 Wh and +6.1 C at 6.0 A. My first record's "+5.95 C" and "+6.0 C" are
    5.947 C unrounded, so the script's +5.9 is the correct one-decimal figure.
  - 4S15P: 118.5 Wh and +2.2 C at 6.1 A; 108.7 Wh and +4.0 C at 6.0 A.
- The B rows (93.7 and 125.2 Wh, +3.8 and +1.5 C) and the A rows (94.0 and 125.5 Wh) do not move with U3 at 6.2, 6.1 or
  6.0 A. The 4S9P rows are NOT MET at every setting and at +40 C. The requirement at C with U3B at 7.936 A is still
  5.565 A (4S14P) and 5.429 A (4S15P).

## (2) M3 and M7

- **M3:** U3B stays at code 62, 7.936 A, for every lid (line 56, `base_cfg()`). No printed figure moved against the
  first issue's per-string setting: every nominal row is identical, including 4S9P's unserved energy.
- **M7:** the model pin (lines 24 to 27) equals energy_runs.py's sha256 81694b2b..., and it works. A copy of the script
  beside a changed energy_two_pack.py refuses with exit 2 before importing.

## (3) RECONCILE.md

- Lines 38 to 62 state the table's figures correctly: the 6.1 A reading and its reason, the 6.0 A bracket, U3B at
  7.936 A, the 5.57 and 5.43 A requirements, and k = 3 for both lids (33,768 and 36,180 cWh).
- The thresholds' instability is stated truthfully. At 0.1 h steps with U3B at 7.936 A the 4S14P C threshold at 6.1 A
  reads +4.62 C, against +5.95 C at 1 h (1.3 K).
- The planes are stated truthfully. Re-run at the new basis on the grid points (`_chk2/more.out`), every point from 20
  to 50 degrees within 15 of south meets both B and C for both lids at 6.2, 6.1 and 6.0 A. At 6.1 A the lowest C point
  among the window's corners is 48.0 Wh (4S14P, 20/-15) and 78.8 Wh (4S15P, 20/-15). Laid flat, 4S14P B is NOT MET, and 4S15P B MEETS
  with 26.4 / 18.9 / 8.4 Wh at 6.2 / 6.1 / 6.0 A. So "sufficient" and "4S15P flat in the typical case only" hold.
- Line 64 now names the k = 3 calibration.
- No line of RECONCILE.md quotes 90.9 or 122.4 Wh, +4.1 C or +2.1 C. In `reconcile_lid_panel.out` they appear only on
  rows labelled "U3 nominal". The first section's 94 Wh and +3.8 C (lines 18 and 23 to 24) are ratio A figures, which
  are unchanged at 6.1 and 6.0 A. No other page in v2/docs quotes the superseded C figures, apart from the filed first
  check.

## (4) New: minor items

The four items below restate sensitivity figures from my first check. I measured them at the first issue's per-string
lid current and at U3's nominal limit. Under the second issue's settings, some of them are no longer the right size.

- **N1** (RECONCILE.md line 56; `reconcile_lid_panel.py` notes, lines 98 to 99): the text says a 0.01 h step lowers the
  lowest stores "by about 0.8 Wh (B) and 2.4 Wh (C)". With U3B at 7.936 A:

  | case | 4S14P | 4S15P |
  |---|---|---|
  | ratio B | 1.2 to 1.6 Wh | 1.5 to 1.9 Wh |
  | ratio C, U3 nominal | 3.3 Wh | 3.9 Wh |
  | ratio C, U3 at 6.1 A (the table's basis) | 3.7 Wh (87.4 to 83.8) | 4.2 Wh (118.5 to 114.3) |

  The largest drop is 4.2 percent, under the materiality line. Fix: quote "about 1.2 to 1.9 Wh (B) and 3.3 to 4.2 Wh
  (C)".
- **N2** (RECONCILE.md lines 56 to 57): "U3B at its 0.96 efficiency bracket costs 3.2 and 3.5 Wh at C" is the nominal-U3
  figure (3.1 and 3.5 with U3B at 7.936 A). At the table's 6.1 A basis it costs 6.0 Wh (4S14P) and 6.2 Wh (4S15P).
  Fix: name the basis, or quote 6.0 and 6.2 Wh.
- **N3** (script notes, line 101): the discard at the full clamp, "23 to 58 Wh over 72 h", was measured at the first
  issue's settings. At the second issue's settings it is 8.2 to 48.2 Wh (B and C, U3 at 6.2 and 6.1 A). It is still
  energy thrown away, never created.
- **N4** (script notes, lines 102 to 103): "The lid path's standby drain and board PL's own supply (about 1.5 to 1.8 Wh
  over 72 h)". The 1.5 to 1.8 Wh is the lid path's drain alone (TOPOLOGY 9: 1.38 to 1.73 mA). Board PL's own supply was
  not read. Fix: "the lid path's standby drain (about 1.5 to 1.8 Wh over 72 h) and board PL's own supply (not read)".

## Reproduced

- `git -C <clone> fetch ... fnd/a1int:refs/remotes/w/a1int`, then detached at 637c9876 (rev-parse verified).
- `env -C <clone> python3 v2/docs/records/a1int/reconcile_lid_panel.py`: exit 0, `cmp` identical to the committed
  `.out`.
- `_chk2/cmp2.py`: every row parsed from the committed `.out` against `_chk2/indep.py` (my model, U3B at 7.936 A); 21 of
  21 agree.
- `_chk2/more.py`: the step and U3B-bracket deltas, the discard, the requirement and the plane window at 6.2, 6.1 and
  6.0 A. `_chk2/tmin_fine.out`: thresholds at 1 h and 0.1 h.
- The pin refusal was tested on a copy under `_chk2/pintest/`, since removed.
- `git -C <clone> status`: only CHECK.md, CHECK-2.md, `_chk/` and `_chk2/` are untracked; nothing is committed.
