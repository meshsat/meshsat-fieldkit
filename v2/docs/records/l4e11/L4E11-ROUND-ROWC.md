**ROUND 19 (W142, branch `fnd/l4rowc`, 7 October 2026; amended by W149 the same day after the focused check L4A-69, with record l8p's round 12): DONE on the desk: L4A-67's replay of section 28 on the corrected circuit (record l8p's fail-safe delta, M-A and round 11's held-overcurrent trip, with round 12's on-time bound, which reads BRK_PGD only) and L4A-68's replay of 20f against U47's and U48's tSD and of 22's bleed with path 2's VBAT load, at the guard's restated allowance (40 uA cold, 50 uA tripped): every row holds against this record's own windows; after the check (section 5): DD-7's restart timeline stretched by L8P-R11-F1's rule to 2.55 s (an affected output), the fallback's composition read from L4-E9's change list (F9), the pair's conditions kept (F10). NOT DONE: the allowance's consumers are restated as drafts, not applied; the trip's silent failures have no detection interval (L4A-67's latent-failure clause NOT MET, record l8p 16i); no targeted recheck yet. NEXT: the targeted recheck of this round with record l8p's rounds 11 and 12 (L4A-69).**

# L4-E11 round 19: section 28, 20f and 22 replayed at the guard's restated allowance on the corrected circuit (L4A-67, L4A-68) (MESHSAT-1357)

Desk arithmetic on the records' own figures. Nothing here is bought, built, measured or sent, and no V2 board exists. Every figure is
printed by `l4e11_rowc.py` in `l4e11_rowc.out` (cited below as [ROWC n], its section n); the tests are `t_*` in
`v2/ecad/tools/tests/test_l4e11_rowc.py`. Labels: RECORD (another record's figure, read from its file), INFERRED (arithmetic on them by a
stated rule), MODEL (the time-constant model of 27b and 28d), ASSUMED. The round closes no cx46 item; it is UNVERIFIED until checked.

**Why.** Section 28 (round 18) left as REMAINING ENGINEERING (28e) "the replay of the dependent start-up and protection rows (20f's
timing against U47's and U48's tSD at the owners' restated allowance, 22's bleed with path 2's VBAT load) once the owners restate the
allowance" (RE-9, cx46 item 9; register row L4A-68), and the register's L4A-67 asks section 28 replayed on the corrected circuit. Record
l8p's round 11 (`L8P-BREAKER.md` section 16, `l8p_cprot.out`) printed the allowance for its consumers, drafted their restatements
(Layer 5's row in `pcb_interfaces.yaml`, record l9stk 15.9; not applied) and corrected L8P-R10-F1 in draft with a held-overcurrent trip
on board P that touches neither the enable loop nor UVLO.

**Closure contract (constitution section 4).** Type: tool/integration replay of a correction's dependants. Inputs: this record's
`l4e11_power.out` (20c, 20f, 22, 27, 28), record l8p's `l8p_c4.out` (10c), `l8p_cprot.out` and the drafts it names. Requirement: this
record's windows (the held reading under 0.7755 V, the powered reading at most 1.981 V, RET/OUT 0.4707 or more, the breaker's start no
sooner than 0.110 s) and 22's need 1 (the bleed inside the hold's least). Smallest deliverable: this page, the script, its output and
its test. Acceptance: every replayed row against those windows, and the replay of 28a equal to section 28's printed rows. Checkpoint:
one focused independent check (L4A-69).

## 1. Section 28 on the corrected circuit ([ROWC 2])

- **28a, path 1 tripped:** the return held at 0.0665 V at most, against 0.7755 V: read held; DOCK_EN_OUT with the tripped 50 uA drawn
  (R106 +1 %, the pair -1 %, board A's 984 kOhm) 4.224, 5.999 and 9.666 V at BRK_VIN 7.6, 10.6 and 16.8 V, equal to section 28's
  printed rows: read powered, so a trip is DD-7's trigger.
- **28b, path 2 tripped:** DOCK_EN_OUT 50.8 mV and the return 30.4 mV: read dark, the state of an undocked pack: no trigger.
- **28c, the window:** unchanged; the sinks on the return are 27a's, and round 11's trip adds none on DOCK_EN_OUT, DOCK_EN_RET, BRK_UVLO,
  BRK_H, BRK_HD or BRK_G2 (record l8p's `check_l8p_och.py`, APART; its mutation onto DOCK_EN_OUT reads FAIL).
- **28d, a docking:** the rise's time constant 59.5 ms (C261, C268 and C262 at +10 %, R106 +1 %, MODEL); the cold 40 uA lowers
  DOCK_EN_OUT by at most 0.404 V; the trip on board P is disarmed until the breaker runs.
- A -1 latched by round 11's trip is the state 20e and 22 already judge (CELL+ dead, the loop powered, the release on CELL+ alive or on
  DD-7's pulse): no new state for board A.

## 2. 20f against U47's and U48's tSD at the restated allowance ([ROWC 3])

| BRK_VIN | The closed loop settled (the cold 40 uA, R106 +1 %, the pair and R107 -1 %) | At the earliest start, 0.110 s | Powered from |
|---|---|---|---|
| 7.6 V | 5.596 V | 4.713 V | 26.0 ms |
| 10.6 V | 7.928 V | 6.678 V | 17.1 ms |
| 16.8 V | 12.750 V | 10.739 V | 10.1 ms |

With no source board A is unpowered until the breaker's start feeds VBAT, no sooner than 0.110 s after the loop closes; U47 and U48 then
hold their outputs for tSD (2 ms at most) and read the loop powered and the return closed: the inhibit for tSD at most, no hold armed,
as 20f found. With a source present they run through the rise: the window (27a, 28c) keeps a ramping closed loop from reading held, and
the loop reads powered before the earliest start at every corner. A hot docking with path 1 already tripped is DD-7's trigger, as
designed (28a).

## 3. 22's bleed with path 2's VBAT load ([ROWC 4])

Path 2's switch and regulator draw from VBAT (U62 16 uA, U63 2.25 uA at their printed table maxima, record l8p 10c), not from CELL+, so
22b's sources into CELL+ are unchanged (434.8 uA at the hot bound): the bleed 1.218 s against the hold's least 1.341 s (0.123 s of
margin) and the coupled limit 520.7 uA (85.9 uA in hand) stand. Round 11's crowbar sits on PACK_P, which reaches CELL+ through the lead
and the dock: its off leakage is a sink on CELL+, never a source, so it can only shorten the bleed; no part of the trip pulls DD7_N, so
U47's RESET states (22d) are unchanged. Both figures still rest on record l8p's E-14c (the breaker pair's hot leakage, ASSUMED).

## 4. Disposition (SESSION), what stays open, and the outputs for set 33 ([ROWC 5])

- 28e's remaining engineering is executed here: 20f's timing against tSD and 22's bleed with path 2's VBAT load hold at the restated
  allowance, and section 28 holds on the corrected circuit. Until record l8p's two apply scripts are applied by their owners, every row
  resting on the allowance stays PROVISIONAL.
- Still open: record l8p's L8P-R9-F1 pattern (a latent first failure, of the guard and now of the trip, with no automatic diagnostic);
  E-14c and E11-45 (f2) and (h) for 22; the independent check (L4A-69).
- Outputs: `l4e11_power.out` is not regenerated by this round (section 28 stays the record's history and this round's output carries the
  replay); record l8p's `l8p_cprot.out` and `l8p_rowc.out` need the held makers' sheets on the box that regenerates them.

Nothing here is verified, built or measured; the tests establish this record's own behaviour only. Acknowledgement: the execution
constitution (sections 3 to 5 and 8) was read and applied: the replay is on the corrected circuit's connected path, at the restated
figures, against the record's own windows, with tests that fail when a row no longer holds.

## 5. After the focused check L4A-69 (W149, 7 October 2026, with record l8p's round 12; [ROWC 1] and [ROWC 5])

The check (W147, an AI review, `_runs/claude/w147chkrowc/REPORT-FULL-AS-RECEIVED.md`) read this round as SUPPORTED AS CONDITIONAL and
its replay as reproduced. What it found that reaches this record:

- **F8 (DD-7's timeline).** Record l8p's L8P-R11-F1 rule (the inverters' off leakage doubling every 10 K, ASSUMED) also stretches the
  RC hold: at the 76.25 C air BRK_H settles at 3.41 V against the 3.265 V the release needs, so the hold takes 2.31 s (R104 +1 %,
  C103 +10 %; `l8p_cprot.out` 4h), against the 0.907 s 20d uses. The input-return restart then ends at most **2.55 s** after VIN_RAW
  passes U34's threshold, not 1.149 s, and never at the 86.25 C site. An affected output of L8P-R11-F1, closed with it (its evidence:
  Q104's and Q105's hot IDSS on board P's specimen). The pulse and the inhibit are unchanged: the hold only delays the restart.
- **The trip's on-time bound (record l8p 16i, F2).** It adds R143 from BRK_PGD and D106 to RESET1, and moves U107's SENSE2: nothing on
  DOCK_EN_OUT, DOCK_EN_RET, BRK_UVLO, BRK_H, BRK_HD or BRK_G2 (`check_l8p_och.py`'s APART), so section 28 and 20f are unchanged; the
  trip's nets are fourteen ([ROWC 1]).
- **F6.** The trip's silent failures have no detection interval: L4A-67's acceptance reads NOT MET on its latent-failure clause
  (REMAINING ENGINEERING, record l8p 16i); section 4's "still open" carries it.
- **F9 (round FET's fallback test).** `test_l4e11_fet.py` now composes board A in L4-E9's change-list order read from section 3 of
  `L4-POWER-ARCHITECTURE.md` (every board A row whose draft the list names, 25 drafts, then Layer 6's table), not a hand-typed partial
  order; the pair still composes one part fewer than the three and reads DRAWN, and its mutations FAIL.
- **F10 (the pair).** Nothing beyond the stated conditions: the pair is under 5 nF only on a TYPICAL figure at -15 V (5.74 nF near
  0 V) and needs a 20.39 K/W installed bar per FET whose buildability is not shown; it serves one shape of TI's answer to Q-TI-17, and
  option (S2) stays visible (round FET).

Nothing here is verified, built or measured; UNVERIFIED until the targeted recheck (L4A-69).

## 6. After the targeted recheck and Q-179 (W161, 7 October 2026, with record l8p's rounds 13 and 14; [ROWC 1])

The targeted recheck (W153, `_runs/claude/w153rechkrowc/REPORT-FULL-AS-RECEIVED.md`) read row (c) as SUPPORTED AS CONDITIONAL and this
record's replay as reproduced; record l8p's round 13 redrew the trip's PGD-low disarm, and Q-179 (W158,
`_runs/claude/w158chkr13/REPORT-FULL-AS-RECEIVED.md`), the one bounded check of that redraw, read it SUPPORTED AS CONDITIONAL. Both are
AI reviews. What reaches this record:

- **The trip's nets.** Since record l8p's round 13 R143 runs from BRK_VIN, and Q113's gate is the trip's only part on BRK_PGD (Q113,
  Q114, R144, D107 and the net OCH_PN added). Still nothing on DOCK_EN_OUT, DOCK_EN_RET, BRK_UVLO, BRK_H, BRK_HD or BRK_G2
  (`check_l8p_och.py`'s APART), so section 28 and 20f are unchanged. The trip has fifteen nets ([ROWC 1] reads "and 11 more"); section
  5's "fourteen" and "R143 from BRK_PGD" are round 12's and stand as its history; [ROWC 1] and [ROWC 5] now name both rounds.
- **Row (c)'s status, restated (record l8p 16k and `l8p_cprot.out` section 8; no verdict upgraded).** Row (c) as a whole is SUPPORTED
  AS CONDITIONAL and no cx46 item closes unconditionally. W147's conditions: E-05, E11-29, E11-36 and E-9 (RE-10, HO-A by M-A, the
  battery FETs), RE-9's two apply scripts applied by their owners, E-6, E-6b, E-12f and E-10 (the trip). W153's: E11-29u, E-6b as
  restated, E-12s, Q111's SOA with a source, the PGD-low disarm's correction and L8P-R12-F1 (OPEN). W158's: the gate's hot leakage on
  the ASSUMED doubling rule (1.018x to the printed 5 V row), the trip between BRK_VIN 7.6 and 10.16 V PROVISIONAL on the PGD pin's
  leakage (E-12p), the start service on record l9stk's IF-1 for a power-on start (a docking not bounded), and 4g completed (record l8p
  round 14). L8P-R11-F1 stays OPEN; its stretch of DD-7's timeline (section 5, 2.55 s) is unchanged by rounds 13 and 14. L4A-67's
  acceptance reads NOT MET on its latent-failure clause (REMAINING ENGINEERING). HO-L stays OPEN on E-05 (round FET).

Nothing here is verified, built or measured. No further check is due under constitution section 6 without a changed design.
