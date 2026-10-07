**ROUND 9 (T10; Layer 4 task L4A-54's correction on W139's L4A-55, 7 October 2026, W143, branch `fnd/l4canmb`, after W139's `fnd/l4canq` merged): DONE: the self-test restated in canmb's draft and record (W139's 12-window cycle with both fabrics at once, every S phase run as worded, the attribution path exercised by V, the surviving fabric tested when one is down; interval 2.60 s, enumerated, with round 7's literal precondition as a failing mutant); FW-B21's stop at the loss count (W139's row) read against the corrected drafts, the single-window stop failing the jammer row; the latched supervisor's EN route drafted as `apply_gen_sch_b_canen.py` (a 2-of-2 of the two peers on the TPS2553-1's EN through an RC-delayed AO3400A, read back by its target; recovery interval 5.603 s; 26 fault rows, 7 mutations FAIL); DAR = 1 with ES0392's workaround quoted with its page in the contract text; composition with W138's regstage in both orders (identical netlists); the tests. NOT DONE: no independent check; nothing applied; W138's regstage is read from a copy (fnd/l4reg not merged); IOHA section 12 and the V rows' propagation (L4A-61); nothing physical. NEXT: the coordinator's reading, then row (b)'s focused independent check (L4A-62) of M-B with W139's analysis and these corrections.**

# T10 round 9: row (b)'s CAN draft corrected on W139's quorum analysis

Record l9t5, task T10, MESHSAT-1357; Layer 4 task L4A-54 (row (b) of the AI-scope register, `_runs/l4ai/REGISTER.draft.md`), round 9
after W137's round 7 (`T10-ROUND6.md`) and W139's round 8 (`T10-CANQ.md`). Prototype design: nothing in this kit has been built,
bought, powered or measured, and no figure here is a measurement. Figures are printed by `l9t5_canmb.py` into `l9t5_canmb.out`
("canmb N" below is its section) and by record l4canen's `l4canen.py` into `v2/docs/records/l4canen/l4canen.out` ("canen N"). Labels:
PRINTED (a maker's limit), TYPICAL, DRAFTED (a contract row or a drafted figure, not applied), MODEL, ASSUMPTION, SESSION. A DRAFT:
like every draft of L4-E9's change list, None is APPLIED; `apply_gen_sch_b_canen.py` refuses the tree's generator until
`RELEASE-T10.md` names an accepted check.

## 1. Why

W139 analysed the quorum on W137's draft (fnd/l4canmb `0d079eaf`) and W138's regulator stage (fnd/l4reg `86dbcdff`): every row held,
contained, or lost as row 8 accepts, with one REQUIRED change and four findings this round corrects before row (b)'s check:

| Item | W139's finding, as received | This round |
|---|---|---|
| FW-B21's stop | "FW-B21's drafted 100 ms stop is a single window of the schedule, and with it the GPIO jammer loses the quorum (row F2)" | the row W139 drafted (the stop at the loss count) carried and read against the corrected drafts (section 3) |
| W139-F5 | W137's precondition read literally "is failed by its own S and V phases" so no S phase runs | the restated precondition reads state frames only, which the test never touches (section 2) |
| W139-F8 | "W137's V phase commands the votes, so the attribution path itself is never exercised in service" | V runs the attribution path end to end (section 2) |
| one fabric down | W137's self-test "stops testing whenever one fabric is down" | each fabric's phases run on that fabric's own precondition (section 2) |
| W139-F2 | "a latched TPS2553-1 has no automatic return (nothing drives IOC_LIM_EN ...)" | the EN route drawn, its recovery interval and its own faults (section 4) |
| W137-F1 | DAR = 1 against the compatibility page's "firmware does not use DAR" | DAR = 1 kept with ES0392's workaround quoted with its page (section 5) |

## 2. The self-test restated (canmb 7; `apply_gen_sch_b_canmb.py` docstring item 4; the contract text)

W139's schedule (W139-D1 to D3), its words made exact. Each fabric's 100 ms window keeps the state slots (A at 10, B at 20, C at 30 ms,
10 ms each) free of the test; the test acts only in its hold, 52 to 88 ms, where each controller sends one test frame (A at 60, B at
70, C at 80 ms). In window n of a 12-window cycle fabric A's target is A, B or C by (n mod 12) div 4 and fabric B's the next
controller, both fabrics at once, the phase S, P1, P2 or V by n mod 4:

| Phase | What the hold carries | Expected |
|---|---|---|
| S | the target's own SHDN request; its test frame attempted, received by no peer; it hears no peer's | silenced |
| P1, P2 | one peer's vote alone (commanded); every test frame received both ways | not silenced |
| V | the target's ONE malformed test frame (12 dominant bit-times, V1) at the hold's start, its only frame in that hold, struck by both readers through their attribution paths; their votes act to the hold's end; it hears no peer's test frame | silenced |

The precondition, per fabric and run as worded: in the previous window every controller received every other's STATE frame on that
fabric, no controller has stopped it (FW-B21), no vote on it is asserted outside the test, and all three are functional; else that
fabric's phase is skipped and each controller's published phase counter shows it. The enumeration (canmb 7, MODEL of the schedule):
the restated schedule runs every phase of every transceiver once a cycle; round 7's with its precondition as worded runs S 0 times
(the mutant, FAILS); with fabric A down at every controller the restated schedule runs every fabric B phase and no fabric A phase,
round 7's runs nothing.

| Figure | Value | Basis |
|---|---|---|
| one cycle | 1.2000 s | 12 windows x 100 ms (DRAFTED), crystals +-20 ppm |
| a latent fault of the vote path declared | within 2.60 s of its onset | exercised within a cycle, judged at its window's end, 2nd consecutive failure, verdict in the next window (MODEL); W139's event model: 2.51 s, degraded 2.51 s, a dead attribution path 1.71 s (round 7's: NOT FOUND) |
| the tightest margin | 5.686 ms | V's strike chain, 1.310 ms from the malformed frame (W139, MODEL on PRINTED parts), before the first peer test frame at 60 ms, less the 1.0 ms window alignment (DRAFTED, W143-D9) and two crystals' drift |
| the error count | +16 a cycle against at least 22 successes | S's test frame and V's malformed frame each +8 (ASSUMPTION: ISO 11898-1's increments, not held); 12 state frames and 10 test frames |
| degraded | the surviving fabric keeps 2.60 s | the down fabric's elements within 2.60 s of its return, which FW-B21's probe brings within 1.200 s of a repair (W139) |

Finding W143-F1: read with the target's test frame also sent in V (round 8's wording leaves it open), the target loses +24 a cycle
against the same 22 successes and its error count rises; the restated wording makes the malformed frame its only frame there. W139's
model already counted one failure in V, so its simulated figures stand.

## 3. FW-B21's stop at the loss count (canen 9; the contract row as W139 drafted it)

FW-B21 restated: "or with a frame pending and no valid frame for more than 3 windows (300 ms, FW-B22's loss count; frames lost to a
deviation the peers attribute and silence do not stop it), is stopped at once (INIT kept set)", V-B21's stop time 400 ms. Read
against the corrected drafts: the self-test never silences a state frame, so no phase can starve a fabric toward the stop; a fabric
the stop holds is probed once a second, so its controller's TXDs move within 1.1 s, under the restart decision's 2.0 s (the stop never
invites a restart); and a stopped fabric's phases wait while the other's run. The drafted single-window stop: W139's row F2 (M1c's GPIO
jammer on both fabrics) reads "quorum lost" against the required "a node out and contained", which the loss-count stop gives; the test
re-runs it on W139's model (FAILS as it must).

## 4. The latched supervisor's EN route (`apply_gen_sch_b_canen.py`; canen 3 to 8)

| Part | What is drawn | Designators (controller A; B and C by +20 or +10, +2 for R660 to R665) |
|---|---|---|
| the votes (6 outputs) | each controller's pins 59 and 60 (PD12, PD13) vote to restart the next controller and the one after | pins only |
| the 2-of-2 element (3) | an SN74LVC1G08 per target supplied from the NEXT controller's rail through 100 Ohm 1 % with its 100 nF, so it lives while the target is latched and dark; each input held low by 10 kOhm | U586, R615, C947, R616, R617 |
| the delay and the switch | its output through 100 kOhm 1 % into 4.7 uF with 1 MOhm 1 % to ground drives an AO3400A (C20917) that pulls the target's IOC{t}_LIM_EN low through 470 Ohm 1 % | R618, C948, R619, Q586, R660 |
| the pull-up | W138's EN pull-up becomes 10 kOhm 1 % (was 100 kOhm) | R602 (changed) |
| the read-back | the target reads its own gate's output on pin 61 (PD14) through 10 kOhm | R661 |

Traced on the netlist from each EN back to the controllers (canen 4): A's EN is an AND of {B} and {C}, B's of {C} and {A}, C's of {A}
and {B}. 33 parts added, none removed; 1554 parts in both orders. Pins: 43 of 100; 14 supplies, 43 unconnected on each controller.

The levels (canen 6, MODEL on PRINTED): the votes at least 2.8422 V against the gate's VIH 2.0 V; the gate's VCC 3.1399 to 3.3577 V
with its worst draw 1.0133 mA (delta ICC 500 uA an input, PRINTED); a restart drives the FET's gate toward at least 2.7131 V against
the 2.5 V of its printed RDS(on) row; a 4 ms test pulse leaves it at most 0.2288 V against VGS(th) 0.65 V (PRINTED at 25 C only, on a
1.0 uF effective floor of the 4.7 uF, ASSUMPTION; margin 0.421 V); EN low at most 0.1884 V against the TPS2553's VIL 0.66 V (SLVS841F
7.3, page 6); EN high for any FET leakage up to 269.6 uA against IDSS printed only to 55 C (5 uA): the margin at 76.25 C is an
ASSUMPTION, finding W143-F6; a shorted capacitor of the gate costs the next controller 33.9 mA, inside its limiter's least 0.4702 A.

The timing (canen 7): a peer votes when it has seen no edge on either of the target's TXDs and no state frame of it on either fabric for
2.0 s (over FW-B21's 1.1 s probe cycle and the 0.800 s rejoin), holds 2.0 s, at most once in 10 s; EN is under VIL for at least
0.791 s of the hold (the limiter's turn-off at most 3 ms, PRINTED; SLVS841F 9.3.1, page 13: "The device remains off until power is
cycled or the device enable is toggled."). **The recovery interval of a latched supervisor, its cause gone: 5.603 s** (2.0 s decision,
1 ms, 2.0 s hold, 0.799 s release, ton 3 ms PRINTED, tSTR 431 us TYPICAL, 0.800 s rejoin with W139's boot ASSUMPTION); before this
round: none, an operator's power cycle. A persistent cause re-latches within 5 to 10 ms (PRINTED) and is retried every 10 s, at most
23.5 mJ an attempt (W138's MODEL).

The route's own faults (canen 8, 26 rows): it can never let one peer act alone; the only faults that leave a 1-of-1 route (a restart
vote stuck high, or a peer's decision that votes without cause) are found within 2.60 s by the other peer's P_EN pulse, read at the
target, without switching anything off; the faults that switch a supervisor off (the gate's output stuck high, the FET shorted, the
pull-up open) are single faults of its own power path, IOHA row 3, found at once; a shorted RC resistor or an open RC capacitor is
found by V_EN at the cost of one restart (back within 0.803 s); 12 residuals, 7 of them of the recovery only (a latched supervisor
then waits for RAIL_EN, the state before this round). The route's test rides in the fabric A target's windows (P1, P2: one peer's 4 ms
pulse at 68 to 72 ms; V: both; the target reading 66 to 74 ms) and needs only one fabric for its verdicts.

The mutations (canen 4), each FAILS: an EN route a single peer can hold (both of A's gate inputs from B, A's EN: AND {B} {B}); the
FET's gate on one peer's vote (DIRECT {B}); the gate on the target's own rail; the FET on another supervisor's EN; no delay; the
read-back on another controller's gate; a peer's vote on the wrong target. The draft refuses a generator without regstage, without
canmb, a second application, and the tree's generator (NOT RELEASED).

## 5. DAR = 1 with ES0392's workaround quoted with its page (canmb 7, canen 9, the contract text)

FW-B22 restated now reads: "DAR = 1 with ES0392 Rev 15 2.24.5's printed workaround (page 48/73: 'Upon failure, clear the corresponding
Tx buffer transmission request bit TRPx of the FDCAN_TXBRP register and set the corresponding cancellation finished bit CFx of the
FDCAN_TXBCF register, then restart the transmission.'), the restart inside its own slot only". The test reads the quote against the
sheet's committed text. W137-F1 is answered; the compatibility page's "firmware does not use DAR" stays Layer 6's to restate (W139-F1).

## 6. Composition and tests

Board B in L4-E9's change-list order, canmb and regstage after iocguard in either order, canen after both: 21 steps, every one OK, the
netlists identical in both orders with canen (1554 parts, 1132 nets) and without (1521, 1111: W138's claim re-read on the corrected
canmb); CON-004 HOLDS (each rail sourced by its own regulator alone, no resistor joining two rails); canmb DRAWN on the limiter's state.
The contract draft composes after t10's on a scratch copy (exit 3 without t10's rows, 0, 0, 3 on a second application) and W139's A9
holds on the new text. The tests, as run.py printed them (7 October 2026, this branch, the held sheets staged from a sibling as
set 32's chain stages them):

| Module | run.py's line |
|---|---|
| test_l4canen | tests: 11 passed, 0 failed, 0 skipped |
| test_l9t5_canmb | tests: 10 passed, 0 failed, 0 skipped |
| test_l9t5_canq | tests: 22 passed, 0 failed, 0 skipped |
| test_pdftext_input | tests: 19 passed, 0 failed, 0 skipped |
| test_applier_state | tests: 20 passed, 0 failed, 0 skipped |
| test_l9t5 | tests: 42 passed, 0 failed, 0 skipped |

## 7. The four acceptance states (constitution section 2)

| Deliverable | Document acceptance | Supported design | Implementation | Physical qualification |
|---|---|---|---|---|
| the restated self-test | this round, read by its author only | enumerated, interval 2.60 s on printed timing and the drafted window, within W139's model | no firmware exists | V-B22 restated (the contract draft) |
| the EN route (`apply_gen_sch_b_canen.py`) | this round | composed in both orders, read by pin, 7 mutations FAIL, levels and timing on printed rows with labelled assumptions | NOT APPLIED | the supplier's tasks of section 9 |
| FW-B21, FW-B22's text | this round (W139's rows, this round's text) | composes after t10's | UNAPPLIED | V-B21, V-B22 |

## 8. SESSION decisions of this round (under the owner's standing rule of 26 September 2026)

| Id | Decision | Why | To reverse |
|---|---|---|---|
| W143-D1 | the EN route is its own draft, `apply_gen_sch_b_canen.py`, after canmb and regstage | canmb keeps composing with regstage in either order; the route exists only with W138's limiter | fold it into canmb once regstage is adopted |
| W143-D2 | the 2-of-2 element is one SN74LVC1G08 on the NEXT controller's rail through 100 Ohm driving one AO3400A through an RC, not two series FETs | its output can be read back, so the 1-of-1 faults are found in service without switching a supervisor off; it lives while the target is dark; a short of its capacitor costs the next controller 33.9 mA only | two series AO3400A with gate RCs (no read-back; the 1-of-1 faults then found only by switching the target off) |
| W143-D3 | the RC 100 kOhm, 4.7 uF, 1 MOhm; test pulses 4 ms | a test pulse stays at most 0.2288 V on a 1 uF floor, a restart passes 2.5 V within 1.208 s | other values with canen 6 and 7 re-solved |
| W143-D4 | W138's EN pull-up to 10 kOhm 1 %, 470 Ohm in the FET's drain | the FET's leakage has no printed row above 55 C; 10 kOhm tolerates 269.6 uA; 470 Ohm bounds a shorted pull-up to 8.85 mA | 100 kOhm with a FET whose leakage is printed at 85 C |
| W143-D5 | the restart rule: 2.0 s of silence on both TXDs and no state frame, a 2.0 s vote, at most once in 10 s, each peer on its own observation | over FW-B21's probe cycle (1.1 s) and the rejoin (0.800 s); W139's rate | other times with canen 7 re-solved |
| W143-D6 | the target reads its own restart gate (one pin), not its peers (two) | a faulty target can only flag its own route falsely or hide its own route's latent fault (a double fault before it matters) | both peers read it (two more pins each) |
| W143-D7 | no start-up restart of each supervisor | it would switch every healthy supervisor off once per start; the residuals it would bound affect recovery only | a start-up restart by the peers before service |
| W143-D8 | V's malformed frame is the target's only frame in that hold | the error count stays bounded (finding W143-F1) | keep the test frame in V and lengthen the cycle |
| W143-D9 | the window clocks aligned within 1.0 ms (DRAFTED, from the state frames' start of frame on TIM3) | the hold's margins (5.686 ms least) and the route's test pulses overlap (2 ms or more) | another bound with canmb 7 and canen 8 re-solved |
| W143-D10 | the route's levels on the envelope of the AP2112K's band and the TPS73733's printed 1.5 % | conservative for either regulator state; the TPS73733's band at low input is INFERRED (W138's L4REG-F2) | the TPS73733's band alone once L4REG-F2 closes |

## 9. Findings for other authors, and the supplier's tasks (amendment 1)

- **W143-F1 (L4A-61, T10-CANQ.md section 3):** V's malformed frame with a test frame too would raise the target's error count each
  cycle; the contract text now makes it the only frame in V's hold.
- **W143-F2 (the coordinator, `_lib/pdftext.py`):** this branch lists the TPS2553 and TPS737 sheets in FETCH as ("l4canen",); W138's
  fnd/l4reg lists them as ("l4reg",): at integration both lines read ("l4canen", "l4reg") (a textual conflict on two lines).
- **W143-F3 (W138, L4A-58):** R602, R622 and R642 become 10 kOhm 1 % in canen; L4A-58's in-service test of the limiter, if it drives
  IOC_LIM_EN, shares the node with this route.
- **W143-F4 (CON-017's owner):** 43 of 100; 14 supplies, 43 unconnected with canen (40, 14, 46 with canmb).
- **W143-F5 (Layer 6):** three more SN74LVC1G08DBVR (C7666), three AO3400A (C20917); the 4.7 uF, 1 MOhm, 100 Ohm and 470 Ohm order
  codes are owed.
- **W143-F6 (Layer 10, Layer 6):** the RC capacitor at least 1.0 uF effective at 3.3 V over -20 to 85 C; the AO3400A's leakage and
  threshold at 85 C have no printed row (the margins of canen 6 are labelled ASSUMPTION).
- **W143-F7 (L4A-61):** V-B22's route rows are in the contract draft; IOHA section 12 needs the route's rows.
- **W143-F8 (the coordinator, C-DEV):** each controller's rail with the route at most 0.1770 A (round 7: 0.1753 A), a labelled scenario
  inside C-DEV rev 2's conservative 0.2558 A.
- **W143-F9 (Layer 12, IOHA A4 and A6):** a supervisor held off by J_IOCOFF is restarted by its peers every 10 s, harmlessly.
- **W143-F10 (the coordinator, L4-E9's change list and the register):** a row for `apply_gen_sch_b_canen.py` on board B, after both
  canmb (W137-F2's row) and W138's regstage, before R-236; L4A-54's text gains six restart votes and three read-backs (43 of 100).
- **W143-F11 (the coordinator, the integration gates):** `inputs/l4canmb-l9t5_canmb-5d14cc85.out` (W139's copy) and
  `inputs/l4reg-l4reg_compare-9fbda7a6.out` are verbatim copies whose own pin lines name canmb's draft at its round 7 sha; they are
  inputs, not outputs, and a gate that re-checks every `.out` file's pins must skip `inputs/`.
- **Supplier's tasks (none a gate of this desk round):** on the first article of board B, each route fault of canen 8 injected with the
  self-test running and found within its bound; one supervisor's limiter latched by an over-limit load and restarted by its peers
  within 5.603 s; one peer's restart vote held asserted: the supervisor never switched off; the AO3400A's leakage at 85 C and 4.2 V;
  the RC capacitor's effective value at 3.3 V and 85 C.

## 10. What closes once independently checked, and what stays open

Once row (b)'s independent check (L4A-62) reads M-B with W139's analysis and this round, it would answer W139-F2 (the recovery proof
for a latched supervisor) for the circuit's part, W139-F5 and W139-F8 (the self-test as worded), FW-B21's single-window stop, and
W137-F1. Until then cx46's item 5 stays NOT CLOSED, CON-004's quorum service OPEN, FW-B22 PROVISIONAL and the ledger's RE-5 REMAINING
ENGINEERING. Open beyond that check: IOHA section 12 and the V rows' propagation (L4A-61); the compatibility page's DAR row (W139-F1);
the limiter's own in-service test (L4A-58); W138's stage itself is unchecked.

## 11. Reproduce

From the repository root: `python3 v2/docs/records/l9t5/l9t5_canmb.py` (about 7 s) and `python3 v2/docs/records/l4canen/l4canen.py`
(about 15 s; both compose board B in temporary directories, never the tree); outputs through `_bin/regen_out.py`. Held sheets:
`python3 v2/docs/records/l4canen/fetch_held_back.py`. Tests: `env -C v2/ecad/tools python3 tests/run.py test_l4canen.`,
`test_l9t5_canmb.`, `test_l9t5_canq.`.
