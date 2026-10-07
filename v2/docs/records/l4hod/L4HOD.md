**L4A-58 (W146, branch `fnd/l4hod` from `664d4019` with fnd/l4reg `86dbcdff` merged, 7 October 2026): DONE: the peers' in-service test of each supervisor's TPS2553-1 drafted on board B as `apply_gen_sch_b_hodtest.py` (a 3.0 Ohm test load, two series AO3400A switches one per peer, each peer's own FAULT and output reads, a diode that holds the tested regulator off while the load conducts; 54 parts, pins 15, 16 and 42 to 45), composed with canmb, regstage and canen in all five orders they admit (identical netlists), read by pin with seven netlist mutations that FAIL; the test's acceptance (J0 to J9) on printed figures with five mutations that FAIL; the procedure, its interval out of the quorum (5.945 s), the service lost and the detection interval of a lost limit (3602.341 s; 102.341 s for one present at start-up); the test path's 35 fault rows and five procedure mutations that FAIL; the tests. NOT DONE: no independent check; nothing applied; the transient dip of +5V_IOC at the test's load step is not bounded on printed figures (PROVISIONAL, W146-F10); nothing physical. NEXT: the coordinator's reading, then row (b)'s check (L4A-62) with L4A-61's propagation.**

# Record l4hod: HO-D under the limiter, the peers' in-service test of each supervisor's TPS2553-1 (a draft, not applied)

Layer 4 task L4A-58 (row (b) of the AI-scope register; the ledger's HO-D under W138's limiter), MESHSAT-1357, W146. Prototype
design: nothing in this kit has been built, bought, powered or measured, and no figure here is a measurement. Figures are printed by
`l4hod.py` into `l4hod.out` ("hod N" below is its section). Labels: PRINTED (a maker's limit or tested row), TYPICAL, DESCRIBED (a
maker's prose), DRAFTED (a contract row or a drafted figure), MODEL, INFERRED, ASSUMPTION, SESSION. A DRAFT: like every draft of
L4-E9's change list, None is APPLIED; `apply_gen_sch_b_hodtest.py` refuses the tree's generator until `RELEASE-T10.md` names an
accepted check AND record l4canen's EN route is in the generator.

## 1. Why (hod 2)

W138's limiter (TPS2553-1 at 49.9 kOhm, record l4reg) bounds each supervisor's regulator current, but its FAULT pin "is asserted
(active low) during an overcurrent, overtemperature, or reverse-voltage condition" (SLVS841F 9.3.3): a limiter that has lost its limit
looks healthy in service. W138 named it as a new failure mode ("the limiter's latent loss of its limit (HO-D, L4A-58: FAULT asserts
only while limiting)"), W127's check 1a and finding 4 sized it, and the owner's part 24 asks that "Any automatic diagnostic needs a
bounded detection/response interval, including faults that arise after startup and faults affecting the diagnostic itself." The
guard's objection in L8P-BREAKER.md ("one that tests a shunt opens the breaker in service") does not hold here: the quorum tolerates
one supervisor out (IOHA row 3), so the other two can switch it off to test it.

## 2. The design (`apply_gen_sch_b_hodtest.py`; hod 4 and 5)

Per supervisor t, with p its next controller and q the one after (designators for A; B and C by +20 or +10, +2 for the switches):

| Part | What is drawn | Designators |
|---|---|---|
| the test load | 3.0 Ohm 1 % 2512 1 W (UNI-ROYAL thick film) from the limiter's output IOC{t}_LDO_IN | R800 |
| the test switch | two AO3400A in series below it; the upper gated by p, the lower by q, each through 1 kOhm with 100 kOhm to ground | Q590, Q591, R801 to R804 |
| the FAULT read | the limiter's FAULT (pin 4, left open by regstage) read by each peer through its own BAT46W (cathode on FAULT) from its own pin node pulled to its own rail by 10 kOhm | D404, D405, R805, R806 |
| the output read | each peer's own 10 kOhm over 20 kOhm (0.1 %, 25 ppm/C) with 10 nF at its ADC pin | R807 to R810, C970, C971 |
| the regulator off | a third BAT46W from t's regulator EN (anode) to the load's bottom: the conducting load pulls that EN under 0.5 V | D406 |
| the pins | PE12, PE13 (42, 43) close its halves on the next and the one after; PE14, PE15 (44, 45) read their FAULT; PC0 (15, ADC123_INP10) and PC1 (16, ADC123_INP11), both FT, read their outputs | per controller |

Traced on the netlist (hod 5): every path from each load to ground needs both of its target's peers ("2 of 2"), never one and never
the target; both peers read the output and the FAULT of that limiter. 54 parts added, none removed; the three limiters (pin 4) and the
three controllers change. The count (CON-017's convention): 43 of 100 before, 49 of 100; 14 supplies, 37 unconnected with this draft.

## 3. The procedure (DRAFTED for Layer 5's contract, hod 9)

Preconditions, each peer on its own observation: all three in the quorum on both fabrics for the last 10 windows, no other HO-D test
and no contained node, the target's FAULT high and its output in band. Schedule: the first round 60 s after the quorum first holds (A,
B, C 20 s apart), then each supervisor every 3600 s, the three 1200 s apart.

| Step | Duration (bound) | What the two peers do | A failure means |
|---|---|---|---|
| 0 | 0.100 s | mark the target under test in their state frames; canen's automatic restart and FW-B21's stop do not act on it; W143's self-test skips by its own precondition | (none) |
| 1 | 2.190 s | assert their restart votes (record l4canen's route): the output falls under 2.0 V within 1.384 s; release: it is back over 3.3 V within 0.804 s | RESTORE ROUTE: abort, nothing latched |
| settle | 0.020 s | the output at 3.3 V for 20 ms | (none) |
| 2 | 0.012 s | the upper half alone for 4 ms, then the lower alone for 4 ms: no drop under 2.5 V | SWITCH STUCK ON (the other half); under the 5 ms least deglitch, nothing latches |
| 3 | 0.019 s | the upper closes, then the lower (the load's moment); the closer checks the output under 2.5 V 0.2 ms after closing, the other peer 3.2 ms after its own; each reads I = V / 3.0 Ohm 1 to 4 ms after the drop it sees, FAULT's fall 4.75 to 10.25 ms after it, the output under 0.3 V 1 ms after FAULT; both open by 12 ms; the output stays under 0.3 V for 5 ms | LIMIT NOT SHOWN (the limit lost, or the test path open); LIMIT HIGH; LIMIT LOW; FAULT NOT SEEN; NO LATCH; the peers disagree |
| 4 | 3.604 s | restart votes for 2.0 s, release: the output back over 3.3 V, FAULT high; the target boots and rejoins within 0.800 s (W139) | RESTORE FAILED: canen's automatic restart retries every 10 s |

Any failure: both peers open their halves, report the verdict (state frames, the kit's status path), restore the target if latched,
and stop that supervisor's tests until the next start (W146-D6). Each peer records the target and the step in its backup registers
before step 3 and clears it after step 4, so a peer that boots with a step 3 recorded (the survivors reset by the step's transient,
W146-F10) takes that test as failed and stops its tests (DRAFTED; the registers' retention through a brown-out reset is an ASSUMPTION,
RM0433's backup domain not read here). Continuous checks every window (a fault on the second consecutive
failure, within 0.3 s): each peer reads both targets' FAULT and output; FAULT low with the output normal, or an output out of its band,
is a test-path fault. The FAULT window 4.75 to 10.25 ms is the printed deglitch widened by 0.25 ms for the 50 us sampling and the
divider's 66.7 us time constant (MODEL).

## 4. The interval, the service lost, the detection interval (hod 9)

- **Out of the quorum: 5.945 s** a test (MODEL on PRINTED, DRAFTED and the boot and domain ASSUMPTIONs); record l4canen's recovery
  5.603 s is step 4 plus its 2.0 s decision.
- **The service lost:** two of three serve (IOHA row 3: ownership unaffected); no spare for that interval (a second supervisor out is
  row 4's home assignment); 0.50 % of the time at 3600 s a supervisor. The survivors' frames hold: the target's transceivers go to the
  protected mode as its rail falls under UV(VCC) (SLLSEQ7F 6.3.4, PRINTED 1.65 to 2.50 V), its TXDs rest recessive on canmb's
  pull-ups, and W139's row R3 reads "a node out and contained" with the survivors' gap 0 against the loss count 3: W139's loss count
  respected. The survivors' supply holds on the DC path (J2: 3.5854 V against 3.4555 V with the limit lost); the transient dip of
  +5V_IOC at the load step (0.5704 A with a healthy limit, 1.4396 A with the limit lost, for the closer's 0.2 ms) is NOT bounded on
  printed figures: PROVISIONAL (W146-F10). The hold-up it would need (MODEL on the drawn capacitors and printed thresholds): board B's
  10.3 uF on +5V_IOC carries the lost limit's step 1.37 us before the survivors' limiter inputs reach their need (3.5127 V), and each
  survivor's own 12.0 uF holds its rail from 3.2505 V over VBOR2's highest falling 2.37 V for 24.9 us at 0.4240 A: the survivors stay
  out of reset if U601 and the lead carry the step within 26.3 us, 12 of U601's switching periods at its printed least 450 kHz.
- **The detection interval of a lost limit:** 3600 s + 2.341 s = 3602.341 s from its onset after start-up; 102.341 s from the quorum
  first holding for one present at start-up; a test whose preconditions fail waits (a node out or a fabric down adds its own repair
  time, IOHA rows 3 and 7).
- **W143's self-test** skips while the target is out: its 2.60 s becomes 8.545 s for a vote-path fault arising in a test (W146-F2).

## 5. The test's acceptance (hod 8)

The reading (each peer, its own): I = V / 3.0 Ohm. Its error terms, every corner taken: R_T 2.8602 to 3.1417 Ohm (1 %, 200 ppm/C over
51 K PRINTED, the load life's 1 % + 0.05 Ohm as ageing); the divider 0.1 %, 25 ppm/C; the peer's own rail 3.2422 to 3.3577 V (record
l4canen's envelope); the ADC +-10 mV at the pin (ASSUMPTION: DS12110 Table 186 prints a TYPICAL only, characterised on BGA); what the
output feeds besides the load, 0 to 0.5 mA (the dividers and the EN pull-up, MODEL, and the regulator held off by D406, ASSUMPTION on a
TYPICAL 20 nA). A healthy limiter (0.4702 to 0.5704 A) reads 0.4345 to 0.6140 A: PASS inside. **A PASS admits IOS 0.4023 to 0.6620
A, under the regulator's 125 C current 0.7399 A (76.0 C/W PRINTED, 0.8669 V corner): a lost limit never passes, and every limit that
passes keeps the regulator at 119.9 C or less.** The margin: B up to 78.4 mA (the second barrier, BOR level 2 with D406 open: 20 mA
assumed) and an ADC error up to +-83 mV. The low side: a pass admits a limit 0.0217 A under the largest served peak (S3' 0.4240 A), a
service residual (W146-F8), not a protection one.

| Row | What holds (hod 8) |
|---|---|
| J0 | every figure used as a limit is PRINTED |
| J1 | the demand at the least input 1.0767 A, 1.89 times IOSmax: a healthy limiter always limits |
| J2 | a lost limit draws at most 1.4396 A; with all three at 0.4240 A U601 carries 2.7116 A against 3 A; the survivors' input 3.5854 V against 3.4555 V |
| J3 | the load inside UNI-ROYAL's printed short-time overload (2.5 x RCWV = 4.330 V for 5 s) |
| J4 | the pass band under the regulator's 125 C current |
| J5 | the output with a healthy limit reads at most 1.8419 V, with the limit lost at least 3.3130 V; the abort at 2.5 V between them |
| J6 | each half alone 4.0 ms, under the 5.0 ms least deglitch |
| J7 | the reading 1 to 4 ms, before the least deglitch; its start 500 times the TYPICAL 2 us response (ASSUMPTION that the limit has settled) |
| J8 | the limiter's 15.8 mJ in a test, inside W138's 23.5 mJ latch case |
| J9 | the gates at least 2.8141 V, the upper's VGS at least 2.7150 V: over the 2.5 V RDS(on) row |

Mutations, each FAILS: a TYPICAL deglitch used as the bound (J0); a test that cannot detect a lost limit, a 10 Ohm load that never
makes a healthy limiter limit (J1, J5); a 1.0 Ohm load (J2, J3); 6 ms single steps (J6); the reading past 5 ms (J7).

## 6. The test path's own faults (hod 10)

35 rows, each with its detection and bound; none NOT FOUND. Found within the test period: the limit lost or high or low, no latch, FAULT
stuck high, the load open or shorted, either half stuck on (step 2) or open, a gate's 1 kOhm or 100 kOhm, a peer's switch pin stuck
either way, a peer's FAULT pull-up, diode or pin, a peer's reading stuck inside its band (the peers disagree), canen's restore route
unable to pull EN low (step 1, before anything latches). Found within 0.3 s by the continuous checks: FAULT stuck low, a peer's FAULT
pin stuck low, a peer's divider or its 10 nF open or shorted. Five residuals with no effect alone in service: a gate's 1 kOhm short, a
gate's 100 kOhm open (its peer dark, when no test runs), a reading capacitor open, D406 open (the second barrier holds), D406 short (in
service none; with the bench jumper fitted the load sits across the output and the limiter latches, bench only).

**The test cannot leave a supervisor limited or unpowered by a single fault of its own path:** no single fault loads the rail outside a
test (two halves in series, one per peer); none holds a load past 4 ms in step 2 or past the abort in step 3 (either peer opens its
half); the restore route is exercised 2.222 s before the load. The one row that can leave its supervisor off is the part's own: a
TPS2553-1 whose latch does not clear on EN (against 9.3.1's description), which any real overload would show the same way; found at
once (step 4), canen retries every 10 s, RAIL_EN returns it. Double faults, named: the load shorted and the limit lost (the test then
asks up to U601's own limit for the closer's 0.2 ms; the first found ends that supervisor's tests); both halves stuck on (the target
held off, a node out); a common firmware fault in both peers, outside the single-fault scope as for every 2-of-2 vote of this plane.

Procedure mutations, each FAILS: a stuck test switch left undetected (step 2 omitted: three rows NOT FOUND); the lower half's partner
not checked; the restore route not exercised first (a restore-route fault then leaves its supervisor latched); one peer alone judging
FAULT; no continuous checks.

## 7. Composition, mutations, tests

Board B in L4-E9's change-list order, iocpre, canshdn, iocset and iocguard, then canmb, regstage, canen and this draft in the five
orders they admit (canmb, regstage, canen, hodtest; canmb, regstage, hodtest, canen; regstage, canmb, canen, hodtest; regstage, canmb,
hodtest, canen; regstage, hodtest, canmb, canen), then R-236, R-237 and Layer 6's three: 22 steps each, every one OK, the netlists
IDENTICAL (1608 parts; 1554 without this draft); CON-004 HOLDS, canmb and canen's EN route read DRAWN. Netlist mutations, each FAILS: a
test a single peer can start (both halves' gates from B: "1 of 1"; the upper half bridged: "1 of 1"); the target in its own test
("SELF"); a test that cannot detect a lost limit (the load ahead of the limiter: "NO LOAD"); the load on another supervisor's output; a
peer reading the limiter's input; a peer reading another limiter's FAULT. The draft refuses a generator without regstage, a second
application and the tree's generator (NOT RELEASED).

The tests, as run.py printed them (7 October 2026, this branch, the held sheets staged from sibling worktrees):

| Module | run.py's line |
|---|---|
| test_l4hod | (filled below) |

## 8. The four acceptance states (constitution section 2)

| Deliverable | Document acceptance | Supported design | Implementation | Physical qualification |
|---|---|---|---|---|
| the test path (`apply_gen_sch_b_hodtest.py`) | this record, read by its author only | composed in every order, read by pin, mutations FAIL, levels and acceptance on printed rows with labelled assumptions; the transient dip PROVISIONAL | NOT APPLIED | the supplier's tasks of section 11 |
| the procedure and its interval | this record (DRAFTED rows) | timing on printed figures, the boot and domain assumptions labelled | no firmware exists | V rows owed (L4A-61) |

## 9. SESSION decisions (under the owner's standing rule of 26 September 2026; authority SESSION, ruled_by W146, ruled_on 7 October 2026, reversed_by none)

| Id | Decision | authority_why | To reverse |
|---|---|---|---|
| W146-D1 | the test load 3.0 Ohm 1 % 2512 (UNI-ROYAL series) | an engineering choice inside the drafted circuit: it forces limiting at 1.89 times IOSmax, keeps a lost limit's current at 1.4396 A inside U601's 3 A and the load inside its printed short-time overload, and keeps the limited output under VBOR2 (the second barrier) | 4.3 to 4.7 Ohm (a smaller lost-limit step, about 1.0 to 0.93 A, with the BOR barrier lost), hod 8 re-solved |
| W146-D2 | two series AO3400A, one per peer | no single peer can start, either can end; a single stuck half loads nothing; found by step 2 without latching | an AND gate driving one switch (a single shorted switch would load the rail in service) |
| W146-D3 | each peer reads the output on its own divider and pin, and FAULT through its own Schottky from its own rail | independent judgements; a dark peer loads nothing; no pin sees more than its own rail | one shared divider and a pull-up from +5V_IOC (a 4.1174 V node on an unpowered pin) |
| W146-D4 | the five-step procedure with the restore route exercised first and 4 ms single steps | a latent restore-route fault is found before anything latches; a stuck half is found under the least deglitch | a test without step 1 (fails the procedure mutation) |
| W146-D5 | the schedule: first round 60 s after the quorum first holds, then 3600 s a supervisor, staggered 1200 s | 0.50 % of the time without a spare against an hourly detection; the mission's 48 to 72 h carries 48 or more tests a supervisor | another period with hod 9 re-solved |
| W146-D6 | a failed test is reported; that supervisor keeps serving; its tests stop until the next start | a lost limit is a latent loss of RE-7's bound, not an active state; repeating a failed test adds no evidence and could repeat a double-fault step | hold it off by a 2-of-2 EN hold (a new rule in canen's contract) |
| W146-D7 | the pins 15, 16, 42 to 45 | free FT pins with the ADC functions read in Table 9; no debug pin | other free pins with hod 6 re-read |
| W146-D8 | the thresholds: PASS 0.4345 to 0.6140 A; the abort at 2.5 V, 0.2 ms after the closer's closure | taken from every corner of the reading so a healthy limiter always passes and a lost one never does | other thresholds with hod 8 re-solved |
| W146-D9 | BOR at level 2 (DRAFTED) | the second barrier on the target's draw if D406 is open | another level with the barrier re-read |
| W146-D10 | the test suspends canen's automatic restart for its target; the self-test skips by its own precondition | the test's restore is its own step 4; no double votes | the automatic rule kept active (its 2 s decision then adds to the interval) |
| W146-D11 | the load switches without a slow gate ramp; the transient dip left PROVISIONAL with the supplier's measurement | a gate ramp's benefit rests on TYPICAL transfer curves too; the base design's own IOSmax step has the same open term | a gate capacitor on the lower half (a load ramp of about a millisecond) |

## 10. Findings for other authors

- **W146-F1 (L4A-61; W143's record l4canen):** step 1 exercises canen's route end to end every test, so six of canen's seven
  recovery-only residuals (the RC's 100 kOhm open, its 4.7 uF short, the 1 MOhm short, the AO3400A open or gate-source short, the 470
  Ohm open, the EN pull-up short) are found within the test period; "a peer's restart decision dead" stays a residual.
- **W146-F2 (L4A-61; W143's self-test interval):** 2.60 s outside HO-D tests; 8.545 s for a vote-path fault arising in a test.
- **W146-F3 (CON-017's owner):** 49 of 100; 14 supplies, 37 unconnected per controller.
- **W146-F4 (Layer 6):** order codes owed: the 3.0 Ohm 1 % 2512 (UNI-ROYAL), 10 kOhm and 20 kOhm 0.1 % 25 ppm, 10 nF; BAT46W-7-F
  C83152 (board A's part, nine more); AO3400A C20917 (six more).
- **W146-F5 (Layer 10):** 54 parts (six SOT-23, three 2512, nine SOD-123, the rest 0603) beside the supervisors; the 2512's copper.
- **W146-F6 (the coordinator, C-DEV):** each controller's rail adds at most 0.353 mA (its two FAULT pull-ups while FAULT is low); no
  case row changes.
- **W146-F7 (L4A-61, Layer 5):** the procedure (section 3), its preconditions, thresholds and responses, BOR level 2 and the
  suspension of canen's automatic restart are DRAFTED here for the contract (FW and V rows); IOHA section 12 needs the test's rows.
- **W146-F8 (the coordinator):** the low side: a limit 0.4023 to 0.4240 A may pass and later latch its supervisor at the S3' peak, a
  node out canen restarts; a service residual of the reading's error.
- **W146-F9 (Layer 12):** a shorted divider top puts the output (at most 4.1174 V) on that peer's FT pin, 0.1174 V over 4.0 V only
  while that peer is dark: a double-condition residual; and regstage's comment "FAULT is left open (L4A-58 reads it)" is stale once
  this draft is taken.
- **W146-F10 (L4A-57; W138; the coordinator):** the transient dip of +5V_IOC at a load step is not bounded on printed figures: the
  test's 1.4396 A step with a lost limit, and the base design's own step of up to IOSmax 0.5704 A at any supervisor's overload (W138's
  J7 is a DC row). PROVISIONAL; the hold-up a step needs is 26.3 us (section 4, MODEL), which U601's printed figures do not bound
  (its load-transient response is printed only as TYPICAL curves); a desk transient model of U601 and the lead, or the supplier's
  measurement of section 11, task 2. Were the survivors reset by it, the quorum would be lost for their boot and rejoin (IOHA row 4: every
  voted bit on its pull-down, the banks on their home modules, for about 0.8 s), once: the backup-register rule of section 3 stops that
  supervisor's tests.

## 11. The supplier's tasks (amendment 1; none a gate of this desk round)

On the first article of board B (one board, its three supervisors):
1. the test run on each supervisor: PASS, the reading inside 0.4345 to 0.6140 A, FAULT 4.75 to 10.25 ms after the drop, LATCHED,
   restored within 5.945 s;
2. a lost limit injected on one supervisor (RILIM shorted): LIMIT NOT SHOWN or LIMIT HIGH at its next test; the two survivors' +3V3
   rails, reset flags and board B's +5V_IOC recorded through the step: pass, no survivor resets, each survivor's +3V3 stays over 2.37 V,
   and +5V_IOC at board B is back over 3.5127 V within 26.3 us of the step (W146-F10); the same with a healthy limiter's step;
3. each half's drain and source bridged in turn: SWITCH STUCK ON at step 2 with no latch; the load opened, then shorted: LIMIT NOT SHOWN,
   LIMIT LOW; a FAULT read diode opened: the peers disagree; canen's RC capacitor shorted: step 1 aborts with nothing latched;
4. the output's draw during the reading window with D406 fitted (pass: 0.5 mA or less) and with it removed (pass: 20 mA or less);
5. each peer's reading against a reference at 1.3 to 1.8 V on its pin's divider (pass: within +-10 mV at the pin);
6. the limiter's settling after the load's closure (pass: settled within 1 ms).

## 12. What closes once independently checked, and what stays open

Once row (b)'s check (L4A-62) reads this record with L4A-61's propagation, it would answer HO-D under the limiter for the circuit's
part: a lost limit found within a bounded interval by a test whose own single faults are found. Until then HO-D stays REMAINING
ENGINEERING, cx46's items NOT CLOSED, Layer 4's DESK gate NOT PASSED, and the transient dip PROVISIONAL (W146-F10). Open beyond that
check: the firmware (none exists), the contract rows (L4A-61), the supplier's tasks.

## 13. Reproduce

From the repository root: `python3 v2/docs/records/l4hod/l4hod.py` (about 15 s; it composes board B in temporary directories, never
the tree); its output through `_bin/regen_out.py`. Texts: `python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l4hod`;
held sheets through the fetch scripts `pdftext.FETCH` names. Tests: `env -C v2/ecad/tools python3 tests/run.py test_l4hod.`.
