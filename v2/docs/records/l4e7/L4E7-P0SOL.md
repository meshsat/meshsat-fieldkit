DONE: round 1 (D-16 CORRECTED in draft; since set 31 ADDRESSED IN DRAFTS and PROVISIONAL on S3 and S4, not independently accepted as closing D-16); round 2 (5 October 2026: route B2 drafted and checked; since round 5 UNSELECTED and WITHDRAWN AS DRAFTED, outside the baseline); round 3 (the owner's review of checkpoint 4, part 23): D-10 rewritten as an UNRESOLVED PROTECTION DEFECT in the present model, the receiving company's remaining engineering item E-1 (SUPPLIER-P1-1-P0SOL.md: failing cases F1 to F4, requirements unchanged, the correction needed before any passing claim, PROVISIONAL and independent outputs); round 4 (Astra's check cx45, Q6): B2's cold-connection guarantee WITHDRAWN (the timing a proof needs listed, the .out's 5e) and its fault credit removed (the presence pair's faults solved and tabled, the .out's 5f; P2 and P3 an OPEN defect of the B2 draft); no protection credit for B2; round 5 (Astra's recheck cx46 and the owner's part 25): B2 UNSELECTED and WITHDRAWN AS DRAFTED throughout, no owner item, P2 and P3 REMAINING ENGINEERING outside the baseline; set 30 note (6 October 2026, branch `fnd/w4l4e7`, record text only, adopted in the NEXT set): this page's wording made consistent with the candidate's state (below the title). NOT DONE: E-1's correction, with the lower-source back-feed computed inside it (REMAINING ENGINEERING, the ledger's HO-F); the presence-pair REMAINING ENGINEERING (P2 and P3, detection, INP protection, timing proof), owed only by a route that takes it up again; the record's cache re-key (a box recompute). NEXT: the coordinator's merge in the NEXT set, with the regeneration of the outputs whose printed text still reads as before (l4e7_p0sol.out's 3 (d) and 5g; not this branch's files), and the L4-E9 rows of section 5.

# P0-7: the solar stage's D-10 (a stiff source with the guard on) and D-16 (the input sense out of range) by circuit alternatives

MESHSAT-1357, task P0-7 of the owner's P0 instruction of 5 October 2026 (part 15, sections 3 to 6; part 19, the scope
amendment). Branch `fnd/p0sol` from `fnd/p0base` at `e132db0e`. Prototype design, desk arithmetic: nothing is bought, built,
powered or measured, and no generator, registry or page outside this record is edited. Every figure is printed by
`l4e7_p0sol.py` into `l4e7_p0sol.out`; its bases are PRINTED LIMIT, TYPICAL, MEASURED (none exists), ASSUMPTION, MODELED,
INFERRED, SESSION, NETLIST and CATALOGUE. The lead-inductance method is ended: no loop is searched and none is claimed to pass;
the record's own transient model runs only at its 3.30 uH reference loop and at the envelope's ends, to check a changed circuit
against the same failure case.

**Set 30 note (6 October 2026; record text only, on branch `fnd/w4l4e7` from set 30's integration commit 2c `53a68c7c`; adopted in
the NEXT set, where the coordinator regenerates; the promoted sha `__INTEGRATED__`).** What moved since this page was written: (1) the
candidate merged set 31 (`6fe398e9`; `v2/docs/records/l4e9/SET31-CHANGES.md`), so L4-E9's page and register now read D-16
ADDRESSED IN DRAFTS, "PROVISIONAL in A7's zero-differential output (S3) and in the regulation at 25 V (S4)"
(`v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:841`), "not independently accepted as closing D-16" (`:1031`), with the register's
R-240 (this page's R-NEW) reading "A7's zero-differential output PROVISIONAL (the supplier's S3)"
(`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:336`), and "D-10 as P0-7 states it (E-1, F1 to F4, the lower-source back-feed)" with
route B2 UNSELECTED and WITHDRAWN AS DRAFTED and no owner item (`v2/docs/records/l4e9/SET31-CHANGES.md:54`); (2) the
remaining-engineering ledger's HO-F (`v2/docs/records/l4close/REMAINING-ENGINEERING.md` on `fnd/ledgerfix` `99bbc0c6`, cited as text
only; its section 6, item E) settles the lower-source back-feed as REMAINING ENGINEERING inside E-1, S1's row (b) its later
validation, on the owner's part 23: "Supplier item S1 must carry that engineering problem, rather than presenting it solely as an
unperformed validation test." (`v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:680`). This page now says the same: D-16 is
CORRECTED IN DRAFT and PROVISIONAL (sections 3 and 4 (d)); the back-feed is an open case inside E-1 (section 4 (a)); section 4's
heading carries the one wording for B2 that the owner's part 25 (`v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:838`) and cx46
item 18 (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:111`, `:201`) ask for; E-1 here is record l4e7's E-1, not
record l9stk's (section 4). No figure, verdict, draft or output is changed: `l4e7_p0sol.out` still prints round 5's wording in its
3 (d) and 5g until the next set regenerates it from a changed generator text, which is not this branch's file.

## 1. Both failing cases reproduced on the base (the .out's section 0)

- The record's results cache: its KEY does not hold on this base, and the only differing input is
  `v2/docs/records/l4e11/l4e11_power.out` (L4-E11's rounds 12 to 16). The six figures `l4e7_stage_settings.py` reads from it
  (UVLO rising and falling, the start's slew, INP, the short-circuit and overcurrent thresholds) are equal in the cached version
  (set 29's freeze, `69921ce8`) and in this base's, so the cached results are this base's results. The cache is NOT re-keyed
  here: the record's own recompute takes 30 to 50 core-minutes and belongs on a rented box (the integrator's). Until then the
  record's tests, which read the cache through `results()`, recompute.
- `render(cache)` is byte-identical to the committed `l4e7_stage_settings.out`.
- **D-16**, recomputed by the record's own `sense_ripple` on its cached parameters: equal to every cached figure. At the 25 V
  corner RSENSE1's resistive peak is 0.1174 V at the regulation's highest current, the pins -0.1866 to +0.1863 V, and M1's 10 ns
  edges put -0.4329 V on them (past the -0.3 V absolute maximum).
- **D-10**, recomputed by the record's own `guard_event_b` with every ceramic bank rebuilt from Samsung's held curves at the
  record's bounds (60 events at the 3.30 uH reference loop): U5 0.2493 V resistive with the numerical error, the pins' complete
  budget -0.3021 to +0.2591 V at a connector fault and -0.2884 to +0.2486 V at the far end; equal to the cache. The cold
  connection at 0.30 uH: PV_F 84.62 V, slew 56.10 V/us, INP 18.54 V.

## 2. The comparison (at most three alternatives; the .out's section 1)

Both defects have one cause: RSENSE1 puts U5's own input amplifier (pins rated -0.3 to +0.3 V absolute, -100 to +100 mV
operating) in the path of currents nothing bounds on printed figures: the charge a stiff source pushes into the capacitance
behind it (D-10) and M1's pulsed draw (D-16).

| | Alternative | Fault case (D-10) | Normal case (D-16) | M2 (CS101, the accepted model) | Verdict |
|---|---|---|---|---|---|
| A | RSENSE1 ahead of every bank (route 3's wider form, R-187) | worse: U5 0.956 V resistive at 3.30 uH (3.2 times its absolute maximum) | meets: the flat input current, 0.045 V | fails: the loop holds the port current and pushes the bulk's CS101 current through the bank, 0.33 A filtered against 0.113 A | rejected |
| B | the guard-on event bounded or removed at the port: B1 a series choke (XAL1510-103), B2 a presence contact pair on the solar receptacle carrying U21's INP | B1: the cut current 31.1 A exceeds the choke's 26.3 A Isat; B2: no effect proven (its cold arrival not shown; its pair faults P2 and P3 put INP over its absolute maximum) | untouched | B1: a resonance at 2.7 to 3.2 kHz inside M2's decided band | B1 rejected; B2 UNSELECTED, WITHDRAWN AS DRAFTED (section 4); neither resolves D-10 |
| C | U5's input sense retired (CSPIN and CSNIN tied to VIN, 8705af p.12, p.29, p.31); the regulation fed into IMON_IN by an INA169 | U5 0 V by construction at every loop | U5 0 V by construction | depends on the sense point: C1 at R87 (U21's IMON) fails like A; C2 on the backstop's bank passes; C3 on RSENSE1 keeps the accepted topology | **C2 selected** |

**The selection (SESSION, the owner's rule: the simplest supported correction with useful margin and the fewest new uncertain
dependencies): C2.** U23, a second INA169 (U18's part, TI SBOS181F), sits on the backstop's bank R60 to R64 and drives U5's
IMON_IN into RIMON_IN R16 (34.0k) and CIMON_IN C65; RSENSE1 (R59) and the net TRK_VIN are removed; R97 becomes 24.9k for INP.
Why C2 over C3 (U23 reading the kept RSENSE1): C2's average does not depend on the INA169's typical-only bandwidth (C3 reads
+0.09 % high at the typical bandwidth but +7.1 % at ten times it and +10.1 % if it followed every edge; C2 at most +1.34 %), and
its CS101 margin is larger. C2's price, stated: the regulation and the 100 W trip share the bank, so a short across the bank,
which already defeats the trip (the record's single-fault list), now also defeats the regulation, which was never credited for
the 100 W bound. **Reversal:** to C3 (the same draft with U23 on R59's pads and R59 kept) if Layer 8's fault analysis rules the
shared shunt out; to the drafted A7 arrangement only with a measured or maker-stated bound keeping U5's pins inside +-0.3 V for
the declared envelope.

## 3. The selected circuit on both cases (the .out's section 2)

- **Composition, netlist, mutations (2a).** Board E's generator composed in L4-E9's change-list order with
  `apply_gen_sch_e_p0sol.py` after the solar guard (R-173) and before L4-E11's aux (R-177): all sixteen drafts apply, the draft
  refuses a second application, and the generator runs to its end (record l8p's `gen_netlist.py`, 296 parts). Nine predicates
  on the changed nets hold (U5's pins 32, 33 and 34 on one net; no R59 and no TRK_VIN; U23 on the bank's pads as U18; U23's
  output on IMON_IN with only R16 and C65; R16 34.0k and R97 24.9k; C79; M1's drain and every input ceramic on U5's input; U18
  and the trip unchanged). Four mutations (CSNIN on its own net, U23's VIN- off the bank, R59 restored, U23's output elsewhere)
  each fail the check. d8dec31's input capacitor still takes C149.
- **The fault case, D-10 (2b, 2c).** U5's CSPIN to CSNIN is 0 V in every state (NETLIST; a layout obligation for board E's
  constraints: pins 32 and 33 joined to pin 34 at the package by a trace that carries only their bias current, U23's Kelvin pair
  from the bank's pad centres beside U18's). On the record's model with RSENSE1's
  branch tied, at the reference loop every listed rating holds its line except PV_F against the TPS4811-Q1's recommended 80 V
  row (83.48 V; L6P-F10, unchanged): the bank's differential 0.483 V (corner search 0.548 V) of U18's and U23's 1.8 V line, INP
  16.67 V with R97 24.9k, Q12's VDS 74.85 V, TRK_VS 29.14 V, D4 no current. INP with R97 24.9k stays under 18 V for every PV_F up
  to 90.1 V, so it can no longer fail where PV_F holds; the cold connection's INP becomes 16.90 V. U21 now turns on by 10.05 V
  at the most (over the stage's own 9.5 V enable, under the hold's least 16.97 V: no operating point lost). IMON_IN stays under
  its 5 V absolute maximum at every loop listed (at most 3.40 V, a linear charge bound). At the envelope's least loop the port's
  own ratings still fail (PV_F 321.9 V; the bank 2.57 V over the INA169s' 2 V): D-10's port-level residual.
- **The normal case, D-16 (2d).** The periodic model written out reproduces the record's `sense_ripple` exactly, then takes the
  selected network: at the 25 V corner the bank's current never reverses (at least 0.43 A); U23's sense spans -167 to +165 mV
  with the bank's inductance at 5 nH unshared, its average inside the INA169's printed 10 to 150 mV rows and its peaks inside
  its 500 mV full scale; the negative inductive spikes it cannot follow make it read high by at most +1.34 %, so the regulation
  errs to a lower input current, never toward the trip. U5's operating range is met by construction. **D-16: CORRECTED IN DRAFT**
  on this record's own check (the draft not applied; not independently accepted as closing D-16; PROVISIONAL in A7's
  zero-differential output, S3, section 3's 2h, and in the regulation at 25 V, S4: the register's R-240,
  `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:336`, and L4-E9's D-16 rows, `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:841`,
  `:1031`; set 30 note, 6 October 2026, in place of round 1's bare "CORRECTED").
- **The regulation (2e).** On printed rows (EA2's 1.187 / 1.208 / 1.229 V and the record's design floor; the INA169's gm,
  nonlinearity, offset, CMR and PSR): nominal 2.5378 A, highest 2.9212 A, lowest 2.1839 A (the drafted A7 regulation: nominal
  2.5485 A, highest 2.9337 A). The trip reads the same bank, so the bank's tolerance, TCR, aging and heating cancel: the margin
  to the trip's least is 0.3645 A at its least over the input range (the accepted design's independent margin 0.1130 A). The
  record's trip reproduces exactly.
- **M2 (2f).** On the record's own CS101 model (reproduced over its 121 frequencies to 0): the filtered peak 0.1093 A at 1714 Hz
  against 0.3645 A, the loop branch's room 3.17 times its typical model (the accepted design: 0.0585 A against 0.1130 A, room
  2.51). HOLDS, CONDITIONAL on the typical loop rows as before.
- **The start, ratings, window (2g).** The start puts at most 1.762 A through the bank; U23 then holds IMON_IN at most 0.93 V,
  under its 1.55 V fault threshold. U23 sits on U18's nets pin for pin, so every rating the record gives for U18 holds for U23.
  RSENSE1's 0.133 W is gone. The 100 W bound, re-run: U23's VIN+ pin takes its output current and its input bias (the record's
  SESSION 1 mA) from ahead of the bank, as U18's does, so the static bound rises from 93.5521 W to 93.5783 W, and check (b)'s
  response allowance (C79's charge added) falls from 1.087 ms to 1.052 ms, still over the required 0.401 ms. The hold, the
  cut-off's band, the trip itself, REQ-016's window and D4 are unchanged.
- **The one new unprinted term (2h), PROVISIONAL under the scope amendment.** A7's own output with CSPIN = CSNIN: the sheet
  prints no current out of IMON_IN for a negative differential and no figure at zero; any current A7 sources lowers the
  regulation (about 3 % per uA), away from the trip. That it cannot sink is read from that text (INFERRED); a sink would raise the
  regulation, and the correlated margin falls to the accepted design's 0.1130 A only at 3.67 uA. Bounded provisional choice: the
  band above with A7 at 0 uA. Validation: item S3 of `SUPPLIER-P1-1-P0SOL.md` (five parts, 16 V and 25 V, -20, +25, +62 C, pass
  from -0.5 uA sinking to +1.0 uA sourcing); the question to Analog Devices is drafted,
  `clarification/analog-devices-lt8705a-p0sol.txt` (item 8), UNSENT.

## 4. D-10: an unresolved protection defect, the remaining engineering item E-1, and route B2 (UNSELECTED and WITHDRAWN AS DRAFTED, outside the baseline)

Heading restated 6 October 2026 (set 30 note): round 3 (5 October 2026) described route B2 in the owner's part 23 terms; round 5
withdrew it as drafted (the owner's part 25, `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:838`; cx46 item 18, which asked for
the withdrawal "throughout", `v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:111`, `:201`), and the heading now
says so (K-24 of the DESK-gate draft, `fnd/dgate` `249e9e47`; item 1 of set 30's records pack, `fnd/recpack` `35dca639`).

**D-10 is an UNRESOLVED PROTECTION DEFECT in the present model** (the owner's review of checkpoint 4, part 23), not a case that
merely lacks evidence. It is written as the receiving company's remaining engineering item E-1 in `SUPPLIER-P1-1-P0SOL.md`.
E-1 here is record l4e7's E-1 (the register's R-240: "item l4e7's E-1", `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:336`), not record
l9stk's E-1, the junction limit that R-159 and L4-E9's E11-29 row carry ("l9stk's E-1", `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:255`,
`v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:750`); one identifier, two items (K-08 of the DESK-gate draft), named apart here
without renaming either:

- **(a) The failing cases** (MODELED, the record's own transient model on the C2 circuit): F1, a stiff 36 V source stepping onto
  the port with the guard on at the envelope's least loop 0.30 uH: PV_F 321.9 V, Q12's VDS 307.4 V, INP 64.3 V, TRK_VS 37.83 V
  with D4 conducting 16.1 A, the sense bank 2.57 V, hitting U21 (100 V and 20 V absolute), the port bank (100 V), Q12 (100 V), D4,
  U18 and U23 (+2 V); F2, the same at about 1.04 uH: PV_F 118.5 V, VDS 108.5 V, INP 23.7 V; F3, at the 3.30 uH reference loop: PV_F
  83.48 V over the TPS4811-Q1's recommended operating 80 V row (L6P-F10); F4, a source arriving with the guard off at the least
  loop: slew 56.10 V/us over the 54 V/us SESSION line (inside the 60 V/us absolute maximum). Claims hit: IF-01's protection of the
  solar entry against D-10, R-173's guard as a protection, the backstop's sensing through the event. **E-1 also carries one OPEN
  case that is not a failing case: the lower-source back-feed** (a stiff source below the stage's voltage arriving after a
  withdrawal: while the guard is off, PV_P back-feeds PV_F through Q12's body diode and the source draws the stage's charge back
  through it; `B2-PRESENCE.md` section 7, the .out's 5g). No record computes it, so it neither fails nor passes. It is REMAINING
  ENGINEERING inside E-1, computed by the receiving company on E-1's corrected circuit as part of E-1's correction, against (b)'s
  requirements and S1's own criterion for the case (Q12's body-diode current inside its pulsed rating); S1's added row (b) is the
  later validation of that computation, not a substitute for it (set 30 note: the remaining-engineering ledger's HO-F and its
  section 6, item E, `fnd/ledgerfix` `99bbc0c6`; the owner's part 23, `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:680`;
  cx46: "D-10's E-1 retains F1-F4 and the lower-source back-feed case.",
  `v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:95`).
- **(b) The requirements, unchanged:** L4-E9's single fault D-10 from REQ-015's 9 to 36 V source class; the owner's amendment of
  2 October 2026, item 3 (a bounded analysis against the approved fault exposure and component ratings, REQ-016's window kept);
  every part inside its absolute maximum ratings, the controller inside its recommended conditions while it must act, the SESSION
  10 % lines. The record's envelope stands (0.30 to 10.20 uH, a connector fault with no lead resistance credited, every guard-on
  start); no new exclusion is adopted to avoid a failure.
- **(c) The correction or justified model revision needed before any passing claim:** something must bound the current the source
  drives into the stage's capacitance through the closed guard, or the energy and voltage it delivers to the port when Q12 opens,
  at every loop. B1 (a series choke) is rejected at the desk on Isat and on its CS101 resonance; route B2 is withdrawn as drafted
  (below); open to a supplier's investigation: a choke rated over the cut current and damped against CS101, a lower-impedance
  clamp or a snubber sized for the port's energy, a different cut-off element or method (an active current limit faster than the
  loop's di/dt, a rise detector, a precharge path), and a model revision only on measured loops and resistances; the correction's
  analysis computes the lower-source back-feed of (a) on the corrected circuit. S1 and S2 then qualify the correction.
- **(d) PROVISIONAL until then:** IF-01's D-10 protection claim, R-173 as a protection, R-176 rows 2 and 3, R-180, the port's parts
  and their Layer 6 rows, board E's port layout and Layer 8 fault table, the guard's Layer 9 rows. **Independent of E-1 (they do
  not wait on its correction), on the present port network, and ADDRESSED IN DRAFTS, PROVISIONAL, not completed** (set 30 note,
  6 October 2026, in place of round 3's "Completed independently": the drafts are not applied and not independently accepted;
  K-13 of the DESK-gate draft; set 31's reading, `v2/docs/records/l4e9/SET31-CHANGES.md:113`): D-16's correction (section 3;
  PROVISIONAL in S3 and S4, the register's R-240, `v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:336`, and
  `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:841`), the regulation and its correlated margin, the 100 W bound re-run, M2 with the
  selected sensing (to be re-run only if the correction changes the port), INP's divider ratio.

**Route B2** (drafted on the coordinator's task of 17:12; `B2-PRESENCE.md`; the .out's section 5) is **UNSELECTED and WITHDRAWN
AS DRAFTED** (Astra's cx45 and cx46, Q6; the owner's reviews, parts 24 and 25). No owner item rests on it: the approved interface
stands (the panel on the shore plug's second pair). Its board E draft, `apply_gen_sch_e_p0sol_b2.py`, kept as a record,
composes in its separate check after the C2 draft (seventeen drafts, 298 parts; four predicates on top of the nine; four mutations each fail); the
withdrawn plug turns Q12 off at most 0.544 ms after the pair opens (the pair intact); IF an arriving source meets Q12 off, the
model's cold connection holds every absolute rating over the record's whole grid (PV_F 84.62 V, slew 56.10 V/us, INP 16.90 V, EN
12.48 V; 608 events). **No protection credit is taken for B2:** its cold-connection guarantee is WITHDRAWN (no sequenced
connector chosen; no worst-case contact and control timing proof: 1 mm is 0.50 ms at 2 m/s, under the
0.544 ms turn-off; BST stays charged from the back-fed VS, TI SLUSEE5E p.17; bounce unbounded; the enable path not simulated;
the .out's 5e), and its pair faults are not fail-safe (the .out's 5f: the two cores shorted together defeat it silently, P1; a
presence core shorted to a positive core of the lead puts INP at PV_F, over its 20 V absolute maximum from PV_F 20 V, P2 and P3,
a defect the draft introduces). **P2 and P3 are REMAINING ENGINEERING outside the baseline:** monitored or fault-tolerant
detection, INP's protection and the timing proof are owed by any presence-pair route taken up again, as a new route with its own
check. B2 would not change the port's response when a step happens, and it leaves a source added in parallel with a connected
panel and a lower stiff source arriving after a withdrawal (both inside E-1: the guard-on step of F1 to F3 and the lower-source
back-feed of (a)); it does not resolve D-10.

## 5. Rows for L4-E9 and the register (the coordinator's; nothing of L4-E9's is edited here)

**Set 30 note (6 October 2026; the promoted sha `__INTEGRATED__`).** The rows below are round 5's proposal of 5 October 2026,
kept as dated history. Since then the P0 round entered R-NEW as R-240 (`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:336`), and set 31,
merged into the candidate at `6fe398e9`, restated L4-E9's page, register and generator from them (`v2/docs/records/l4e9/SET31-CHANGES.md:41`,
`:53`, `:54`): D-16 reads ADDRESSED IN DRAFTS, PROVISIONAL in S3 and S4 (`v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md:841`) and
"not independently accepted as closing D-16" (`:1031`), narrower than the D-16 row proposed below (S3 only); D-10 carries
the lower-source back-feed beside F1 to F4 (`v2/docs/records/l4e9/SET31-CHANGES.md:54`), which section 4 (a) now places as REMAINING
ENGINEERING inside E-1 (the ledger's HO-F); R-176 row 3's replacement below is not carried by set 31 ("a finding for the next set",
`v2/docs/records/l4e9/SET31-CHANGES.md:123`). L4-E9's applied text, not the rows below, is the current record of these rows.

- **D-10** (8a and 8c): "AN UNRESOLVED PROTECTION DEFECT in the present model (the owner's review of checkpoint 4, part 23),
  the receiving company's remaining engineering item E-1 (SUPPLIER-P1-1-P0SOL.md: the failing cases F1 to F4 with the parts and
  claims they hit, the requirements unchanged with no new exclusion, the correction or measured model revision needed before any
  passing claim, then S1 and S2). CORRECTED within it by P0-7 (R-NEW): U5's absolute-rating violation (CSPIN and CSNIN tied to VIN,
  0 V at every loop) and INP's margin line (R97 24.9k). Not resolved: the guard's port-level transient (F1, F2 absolute-rating
  violations below about 2.4 uH; F3 PV_F 83.48 V over the recommended 80 V row at 3.30 uH, L6P-F10; F4 the arriving source's slew
  over its 54 V/us line under 0.33 uH). Route B2 (not a baseline row) is UNSELECTED and WITHDRAWN AS DRAFTED, with no protection
  credit and no owner item (cx45 and cx46: its cold-arrival guarantee withdrawn; its pair faults P1 to P3 not fail-safe, P2 and P3
  REMAINING ENGINEERING outside the baseline); it does not resolve D-10; no baseline row depends on it."
- **D-16** (8a and 8c): "CORRECTED in draft by P0-7 (R-NEW): U5's input sense not used (0 V by construction), the regulation's
  sense U23 on the bank, its average at most 1.34 % high (the safe side); PROVISIONAL in A7's zero-differential output (sourcing
  lowers the regulation; a sink, excluded by p.31's text, INFERRED, is covered up to 3.67 uA; S3)." B6-ENG-2 is answered at the desk; B6-ENG-1 becomes E-1, the port's remaining engineering.
- **IF-01:** NOT MET stays, on D-10's port-level defect (the text above); "U5's pins" leaves the NOT MET list. **IF-02:** "the regulation 2.5378 A nominal, 2.9212 A
  highest (U23 on the bank, R16 34.0k); the margin to the trip 0.3645 A, correlated; the static bound 93.5783 W (U23's VIN+
  currents added) and check (b)'s allowance 1.052 ms; A7 at zero differential PROVISIONAL".
- **The change list (section 3), a new row R-NEW** after R-173 and before R-177: "board E, gen_sch_e.py,
  `apply_gen_sch_e_p0sol.py` (13 edits): R59 and TRK_VIN removed, U5's pins 32 to 34 on TRK_VS, U23 INA169 (C44322) on the bank
  into IMON_IN with C79, R16 34.0k (C705770), R97 24.9k (C136967); AFTER the input limit, the backstop and the solar guard;
  DRAFTED (not applied)". **R-20** (the input limit): its R59 and TRK_VIN superseded by R-NEW, R16 and C65 kept. **R-173**: its
  R97 superseded by R-NEW. **R-187** (route 3): "worked to the circuit by P0-7: alternative A rejected (D-10 worse, M2 fails);
  the sense arrangement changed instead (R-NEW)". **R-189** (B6-ENG-2's bench): replaced by S4 (the regulation at 25 V) and S3.
  **R-186** (a sense-pin filter): obsolete under R-NEW. **R-176 row 3**: U5's +-0.240 V line replaced by U5 under 10 mV (layout
  check); the port's rows stay. **R-180**: UNCHANGED in the baseline (its present text stands, PROVISIONAL with D-10 under E-1; E-1's correction may need its own R-180). **The baseline does not depend on route B2 (the owner's review, part 24):** no row for B2 enters L4-E9's change list, Layer 6 or the register; the baseline composition (`ORDER_E`) has no B2 step. Filed in this record ONLY, UNSELECTED and WITHDRAWN AS DRAFTED, with no owner item (part 25): its draft `apply_gen_sch_e_p0sol_b2.py` (4 edits, composed separately after R-NEW for checking), its contact requirement (section 3, a record, never a replacement of R-180) and its Layer 6 rows (section 4, a record). It has no protection credit (cx45: its pair faults P2 and P3 put INP over its absolute maximum, REMAINING ENGINEERING outside the baseline; its cold arrival is not proven) and it does not resolve D-10. **P1-1**:
  narrowed to `SUPPLIER-P1-1-P0SOL.md`.
- **For other authors:** Layer 8's single-fault table (the record's "defeat" list) gains "a short across the sense bank now
  defeats the regulation as well" and "U23's output stuck high stops the stage (IMON_IN fault), stuck low leaves the regulation
  open, the trip unchanged"; record l9t5 and the energy budget: U23's supply at most 4.0 mW, RSENSE1's 0.133 W removed; Layer
  6's components: C705770, C136967 and a second C44322.

## Files

| File | What it is |
|---|---|
| `l4e7_p0sol.py`, `l4e7_p0sol.out` | the reproduction, the comparison, the selected circuit on both cases, the composition with its netlist check and mutations, the verdicts (about 70 s; the output through regen_out.py) |
| `apply_gen_sch_e_p0sol.py` | the DRAFT for board E's generator (13 edits; refuses a generator without the input limit, backstop and solar guard drafts, a second application, and the tree's generator until a RELEASE.md names an accepted check) |
| `B2-PRESENCE.md` | route B2, UNSELECTED and WITHDRAWN AS DRAFTED: why it is withdrawn, the authority as found, what it would have changed, its contact requirement and Layer 6 rows as a record, the draft's checks, the withdrawn guarantee (5a), the pair's faults with P2 and P3 as REMAINING ENGINEERING (5b), the SESSION decisions, what stays open |
| `apply_gen_sch_e_p0sol_b2.py` | route B2's DRAFT for board E (4 edits, after the C2 draft in its separate check; WITHDRAWN AS DRAFTED) |
| `SUPPLIER-P1-1-P0SOL.md` | the narrowed supplier request, UNSENT |
| `clarification/analog-devices-lt8705a-p0sol.txt` | item 8 for Analog Devices, UNSENT |
