**L4A-55 (T10 round 8; Layer 4 task L4A-55, 7 October 2026, W139, branch `fnd/l4canq` from `06d064ff`): DONE: the quorum service of the three I/O supervisors under method M-B analysed on W137's draft (fnd/l4canmb `0d079eaf`: buffered TXDs, TXD pull-ups, twelve 2-of-2 SHDN votes) in an event model of both fabrics, run for IOHA rows 3, 4, 5, 7 and 8 (A7 as written), every fault of M-B's vote path the brief names, W137's four residuals, W137-F1 and W138's latch (fnd/l4reg `86dbcdff`), each row's onset scanned over the window and the self-test cycle, on W137's self-test schedule and on this round's restatement; the attribution rule; the self-test's interval and every latent fault of the vote path with its bound; the recovery proof; FW-B22 restated on the two fabrics as `apply_hw_fw_contract_canq.py` (with FW-B21's stop at the loss count, which the model shows is needed); CON-004 restated, not amended; acceptance A1 to A10 hold; the tests with eleven mutants that FAIL. NOT DONE: no independent check; nothing applied; nothing physical; the latched supervisor's automatic return has no drafted circuit (W139-F2); IOHA section 12's new rows and the V rows' propagation are L4A-61's. NEXT: the coordinator's reading, then one focused independent check of M-B with this analysis (constitution section 6).**

# T10 round 8: the quorum service under method M-B (the ledger's RE-5 and HO-C; Layer 4 task L4A-55)

Record l9t5, task T10, MESHSAT-1357; Layer 4 task L4A-55 of the AI-scope register (`_runs/l4ai/REGISTER.draft.md`, W129's draft 2,
row L4A-55). This page is the third T10 page: `T10-ROUND5.md` holds rounds 5 and 6, W137's `T10-ROUND6.md` (fnd/l4canmb) round 7,
and this page round 8. Prototype design: nothing in this kit has been built, bought, powered or measured, and no figure here is a
measurement. Every figure is printed by `l9t5_canq.py` into `l9t5_canq.out` ("canq N" below is its section). Labels: PRINTED (a
maker's limit), TYPICAL, DRAFTED (a contract row, not applied), MODEL, ASSUMPTION, SESSION. The two drafts it reads are copied
verbatim into `inputs/` and named with their sha256 in `inputs/SOURCES-canq.txt` (a record reads its own tree); both are unchecked.

## 1. Why, and what stays fixed

cx46 ended round 6's method: "The GPIO jammer and latent comparator cases remain admitted counterexamples." The ledger's RE-5 hands over
"the peer-silence or diagnostic circuit and the recovery proof", accepted when CON-004's quorum service holds under every row of the
fault table, with any automatic diagnostic carrying "a bounded detection/response interval, including faults that arise after startup
and faults affecting the diagnostic itself" (the owner's part 24). W137 drafted the circuit (L4A-54); this round proves, or fails to
prove, its service. CON-004 is restated and NOT amended (canq 2): "Each I/O supervisor has its own regulator branch, reset supervisor,
watchdog, crystal and SWD pads, and the three talk over two independent CAN-FD fabrics with separate transceivers and termination.",
accepted when "Netlist shows three independent supply branches and two fabrics; A7 (either fabric cut, the quorum holds) passes." The
model keeps exactly those two fabrics; the acceptance FAILS on any row that needs a third fabric or a removed fabric (A1, A3 and the
mutants of section 7). Point-to-point CAN stays owner item E-18, not raised: M-B has not met its end condition.

## 2. The attribution rule and the containment chain (canq 4)

Each controller reads both other controllers' TXDs on both fabrics through W137's buffers (its own it knows), so it sees every
transmitter's intent. A target's TXD activity is a VIOLATION when on one fabric it shows: V1 a dominant run over 11 bit-times plus
0.25 us (TI SLLSEQ7F 5.6 note 1 PRINTS that "The CAN protocol allows a maximum of eleven successive dominant bits (on TXD)"); V2 edges
closer than half a bit-time; V3 a malformed stream in a frame it owns; V4 the FIRST dominant bit where a frame's owner sends recessive,
outside the ACK slot (the flags of those who answer it come after it and are legal); V5 a start of frame outside its slot or over its
count. A STRIKE needs the violation AND the reader's own evidence on that fabric, a protocol error at its FDCAN (FDCAN_IR.PEA, PSR.LEC,
RM0433 p.2535) or its own scheduled frame lost, explained by that deviation: never a TXD reading alone. So a dark controller (its
buffer reads recessive), a stuck buffer or a stuck reading input yields no strike, and an error nobody's TXD explains (a physical
fabric fault) is left to FW-B21's stop. A reader votes on its OWN strike (k = 1), never on a message received over a fabric, which a
jammer may deny; the 2-of-2 gate then needs both peers' own strikes. The reader rebuilds the bus from the three TXDs only to find WHO
deviated first; whether anything happened on the bus it takes from its own FDCAN, so a target it cannot know to be shut (the other
peer's vote is not visible to it) can at worst appear in the rebuild with no error behind it, and yields no strike. The comparison has
ONE time base: the reader's TIM3 time-stamps the peers' TXD edges (W137's capture channels), and with FDCAN_TSCC.TSS = 10 its FDCANs
take the "External timestamp counter from TIM3" (RM0433 Rev 8 p.2529), captured "on start of frame (both Rx and Tx)" (p.2530).

| Step | 500 kbit/s | 1 Mbit/s | Label |
|---|---|---|---|
| the evidence: the corrupted frame's error reported by its end (150 bit-times) | 300 us | 150 us | MODEL (frame format) |
| the reader's evaluation | 1 ms | 1 ms | DRAFTED (FW-B22 restated) |
| the vote's GPIO edge, speed 00 at 50 pF | 16.6 ns | 16.6 ns | PRINTED (DS12110 Table 160) |
| the SN74LVC1G08 at 3.3 V, 50 pF, to 125 C | 6 ns | 6 ns | PRINTED (SCES217AA 5.8) |
| the TCAN334's tMODE | 10 us | 10 us | PRINTED (SLLSEQ7F 5.6) |
| a deviation to the target's driver off | 1.310 ms | 1.160 ms | MODEL on the rows above |
| a held TXD (V1 at 12 bit-times) to the driver off | 1.034 ms | 1.022 ms | MODEL; the DTO frees the bus anyway after 1.2 to 3.8 ms PRINTED |

A vote is held 1 s, doubled for each strike within 10 s of a release, at most 64 s; nothing can strike a silenced transceiver, so the
hold runs from the silence.

## 3. FW-B22 restated on the two fabrics (canq 5; `apply_hw_fw_contract_canq.py`, DRAFTED)

- **The window, 100 ms on each fabric:** a guard to 10 ms; a 10 ms slot per controller (A from 10 ms, B from 20 ms, C from 30 ms) for
  ALL its frames (one state frame, at most five event frames, as drafted), so healthy controllers never arbitrate against each other;
  a self-test segment with its hold from 52 to 88 ms and one test frame per controller at 60, 70 and 80 ms: no state frame is ever
  silenced by the test.
- **The decision:** a peer's state frame for a window taken from EITHER fabric, and counted only in its sender's slot with its sender's
  identifier (a frame carrying another controller's identifier is discarded, so no controller can speak for another); two copies that
  differ discard that peer's state for the window; a peer lost after 3 consecutive windows with no valid state frame on either fabric
  (the loss count); 2 of 3 as drafted.
- **DAR = 1 kept** (L9T5-D2) with ES0392 Rev 15 2.24.5's PRINTED workaround ("Upon failure, clear the corresponding Tx buffer
  transmission request bit TRPx ... then restart the transmission"), the restart inside the controller's own slot. With slots healthy
  controllers never lose arbitration to each other, so 2.24.5 is met only against a faulty one. This answers W137-F1 toward the
  contract draft; the compatibility page's "firmware does not use DAR" is to be restated (W139-F1). Row F1 shows what DAR = 0 does: a
  silenced attempt is retried to Bus_Off in 1.152 ms (MODEL), FW-B21 then keeps that fabric stopped at least a second, and on the
  restated schedule a healthy controller drops out (canq 6, F1); the self-test's cycle then never completes (canq 7: NOT FOUND).
- **FW-B21's stop restated at the loss count:** the drafted "no valid frame for 100 ms" is ONE window of this schedule, so a single lost
  state frame stopped a fabric for a second; with M1c's GPIO jammer that took the quorum on both schedules (row F2: quorum lost, gap 21
  windows). The draft therefore also edits FW-B21 to "more than 3 windows (300 ms, FW-B22's loss count; frames lost to a deviation the
  peers attribute and silence do not stop it)" and V-B21's stop time to 400 ms. The stop's delay moves no thermal figure: "each window
  carries at most 2 ms of own dominant drive by the schedule, so a fault's current is averaged over the window whatever the detection
  time" (t10 10h (3)).
- **A returning controller** (a reset, a latch released, power back) listens in bus monitoring mode, which "sends only recessive bits
  on the CAN bus" (RM0433 Rev 8 p.2469), for 2 windows, takes the epoch and the window's timing from the state frames, sets its votes
  and voted outputs to the read-back, and only then sends: it moves nothing (IOHA A4).

## 4. The fault table (canq 6): each row's outcome

Each row is run with its onset at 9 positions in the window and at 12 positions in the self-test cycle, on both schedules; the table
gives the worst. "Gap" is the longest run of windows in which a controller of the surviving quorum missed another (the loss count is
3). "Contain" is from the jammer's first deviation to its driver off on its last fabric. Required: 2 quorum held, 1 a node out and
contained (or better), 0 quorum lost accepted (rows 4 and 8).

| Row | Fault | Restated | W137's schedule | Req | Gap | Contain (restated / W137) |
|---|---|---|---|---|---|---|
| R3 | IOHA 3: controller C dark | node out, contained | node out, contained | 1 | 0 | - |
| R4 | IOHA 4: B and C dark (reference) | quorum lost | quorum lost | 0 | - | - |
| R5a to R5c | IOHA 5: C wedged (TXDs recessive; TX pins held dominant; its four votes stuck asserted) | node out, contained | node out, contained | 1 | 0 to 1 | 1.034 ms (held) |
| R7a, R7b | IOHA 7, A7 as written: fabric A, then fabric B, cut at its break links | quorum held | quorum held | 2 | 0 | - |
| R7c to R7g | IOHA 7: shorts with no dominant (B1, B2, B5); shorts that still work (B3, B4); a transceiver failed dominant with DTO and SHDN dead (B7b); a TXD held low (B7a); an open everywhere (B6) | quorum held | quorum held | 2 | 0 | 1.034 ms (B7a) |
| R8a | IOHA 8: both fabrics broken | quorum lost (nothing moves) | quorum lost | 0 | - | - |
| R8b | IOHA 8 with W138's TPS2553-1 latched on all three | quorum lost (nothing moves); return section 6 | quorum lost | 0 | - | - |
| R8c | A7 with both link pairs out | node out (A), B and C keep the quorum | node out | 0 | 0 | - |
| M1a | GPIO-toggled TX on fabric A, into B's state frame | quorum held | quorum held | 1 | 0 | 1.310 / 101.310 ms |
| M1b, M1c | GPIO-toggled TX on both fabrics, into B's (and C's) state frames | node out, contained | node out, contained | 1 | 1 | 1.310 / 101.310 ms |
| M1d, M1e | toggled at the bit rate, and faster than a bit, both fabrics | node out, contained | node out, contained | 1 | 0 | 34.310 / 76.310 ms |
| M1f | TX pins held low as GPIOs, both fabrics | node out, contained | node out, contained | 1 | 0 to 1 | 1.034 ms |
| M2a | a babbler winning arbitration, both fabrics | node out, contained | node out, contained | 1 | 1 | 51.280 / 101.280 ms |
| M2b | a babbler losing arbitration | quorum held (harmless, unattributed) | quorum held | 1 | 0 | - |
| M3a, M3b | a stuck vote output, high and low (B's vote on A, fabric A) | quorum held | quorum held | 2 | 0 | - |
| M3c | a controller asserting all four of its votes | quorum held (no one silenced) | quorum held | 1 | 0 | - |
| M3d, M3e | a 2-of-2 gate's output stuck high, stuck low | quorum held | quorum held | 2 | 0 | - |
| M4a | a two-faced controller across the fabrics | node out (its state discarded) | node out | 1 | 0 | - |
| M5a to M5e | the self-test silencing a fabric A transceiver while fabric B shorts, is cut (A7), is toggled into, is jammed, or C goes dark | as the real fault's own row | the same | 1 or 2 | 0 to 1 | as M1 |
| Q1 to Q4 | W137's residuals, each with the fault that makes it act | node out (Q1, Q4) or quorum held (Q2, Q3) | the same | 1 or 2 | 0 to 1 | 1.034 ms (Q4) |
| O1, O2 | a TXD buffer stuck dominant; a reading input open | quorum held (no strike: the bus is fine) | quorum held | 2 | 0 | - |
| F1, F2 | DAR = 0; FW-B21's stop as drafted (configurations this round rejects) | node out; quorum lost | quorum held; quorum lost | - | - | - |
| D1, D4 | DOUBLE: a latent vote or reading fault on fabric A, then a jammer there | quorum held (fabric B) | quorum held | - | 0 to 1 | - |
| D2, D3, D5 | DOUBLE: a reader's attribution dead, or C dark, then A jams both; a cut fabric A, then A jams fabric B | quorum lost; quorum lost; node out | the same | - | - | - |

What the containment rests on, row by row, is the chain of section 2 (a hardware path whatever the jammer's firmware does) and the
evidence rule. Where W137's schedule contains more slowly (up to 101 ms), it is because its hold (10 to 90 ms) shuts a reader's
receiver for up to 80 ms; the restated hold shuts one for at most 36 ms. Every healthy controller's error counter stays under the
Error_Warning limit of 96 (PRINTED) in every single-fault row (at most 69, ASSUMPTION increments); D rows reach Bus_Off by design of the
double fault. On one fabric a frame is common to every receiver (one bus), so a two-faced controller can tell its peers different
things only BETWEEN the fabrics, or by speaking for another controller, which the slot-and-identifier rule discards. The two-faced
controller (M4a) is contained because every receiver gets both copies on the restated schedule (0 windows
in which one receiver took a single copy); on W137's schedule its S and V phases silence a receiver's state frames on the tested fabric,
giving up to 11 windows of such asymmetry in a run (W139-F6): still contained, because the hardware 2-of-3 voters keep the physical
outcome single-valued.

**Row 8 and W138's latch (R8b).** W138 reads "(f2) 0.5491 A and rev V's held 0.5639 A inside the band (0.4702 to 0.5704 A): a
supervisor there MAY be limited and latched off after 5 to 10 ms" (W138's band at its tested row; on W159's envelope, 0.4702 to 0.5878
A, record l4reg's `l4reg_compare.out` in this tree reads the same two held states inside the band, and `l9t5_canq.out` now reads its
band there: W167 on W163-N4). The held states arise only while both transceivers drive dominant
into their faults: a healthy controller does that for at most one attempt's bits, and a held TXD is ended by the DTO after at most 3.8
ms (PRINTED), under the latch's 5 ms minimum. Whether the TPS2553-1's timer restarts when the current falls is the held sheet's
(SLVS841F, not read here), so R8b takes "MAY latch" as written (SESSION W139-D10): all three latched, quorum lost, which is row 8's
accepted outcome ("nothing moves", the voters at the home assignment). Its return is section 6's. Row 7's held state (f1), 0.3726 A,
is under the limiter's least 0.4702 A, so no row 7 case reaches the band.

## 5. The self-test's interval and the latent faults of the vote path (canq 7)

Simulated with the onset anywhere in the cycle, a phase judged at its window's end, declared on the second consecutive failure, the
verdict exchanged in the next window.

| Element | Fault | Found by | Restated | W137's (as meant) |
|---|---|---|---|---|
| a vote output, its line or its gate input | stuck low or open | V fails | 2.51 s | 4.90 s |
| the same | stuck high | the other peer's P fails | 2.51 s | 4.95 s |
| a vote pull-down | short / open | V fails / RESIDUAL | 2.51 s / residual | 4.90 s / residual |
| the 2-of-2 gate | output stuck low / high | V fails / its frames absent | 2.51 s / 0.20 s | 4.90 s / 0.20 s |
| the vote diode; the own-request diode | open | V fails; S fails | 2.51 s | 4.90 s; 4.95 s |
| SD's 100 kOhm | open | RESIDUAL | residual | residual |
| the transceiver's SHDN input | ignored | S and V fail | 2.21 s | 4.60 s |
| a reader's attribution path (capture, classifier, evidence, decision) | dead | the restated V phase | 1.71 s | NOT FOUND (W139-F8) |
| an isolation resistor, a reading input, a TXD buffer | open or stuck | the continuous reading | 0.30 s | 0.30 s |
| an isolation resistor; a TXD pull-up | short; open | RESIDUAL | residual | residual |
| a node's schedule; a node's verdict | stalled; wrong | the phase counter; 2 of 3 | 0.20 s; its phase's | the same |

The restated interval is 2.51 s (a 12-window cycle, both fabrics in parallel; W139-D2); W137's own figure, 5.00 s, holds in the model
(4.95 s at worst) when its precondition is read as meant. Three facts the model adds: (1) DEGRADED, with one fabric down at every
controller, the restated test keeps running on the other fabric (a fabric B vote stuck low found in 2.51 s), while W137's precondition
needs both fabrics, so a latent fault has no bound for as long as a fabric is down; (2) W137's precondition read LITERALLY ("in the
previous window every controller heard every other on both fabrics") is failed by its own S and V phases, so the phase after each is
skipped and no S phase ever runs (an open own-request diode NOT FOUND; W139-F5); (3) W137's V phase commands the votes, so the
attribution path itself is never exercised in service (W139-F8); the restated V phase runs it end to end (the target's deliberate
malformed test frame in the hold, struck by both readers). W137's four residuals each need further faults; rows Q1 to Q4 run each with
the fault that makes it act, and none reaches a worse outcome than its row requires.

## 6. The recovery proof (canq 8)

| Contained state | Its exit | Bound (printed and drafted) | Simulated return |
|---|---|---|---|
| silenced by votes on a fabric (RC1: a jammer for 0.3 s, then conforming) | the vote released 1 s after the silence; SHDN low within 13.01 us (W137); its own FW-B21 has stopped that fabric and probes it once a second; a Bus_Off it reached is left after 129 x 11 recessive bit-times (2.838 ms, RM0433 p.2534 PRINTED) | 2.203 s | 1.095 s |
| a dark or reset controller (RC2: dark 2 s) | boot (0.5 s, ASSUMPTION), MON 2 windows, its slot; no vote stands against it (no strike while dark) | 0.800 s | 0.715 s |
| a fabric repaired (RC3: open everywhere 2 s) | each controller's next FW-B21 probe | 1.200 s | 0.395 s |
| a two-faced controller (RC5: 1 s) | its copies agree again | one window | 95 ms |
| W137's TXD pull-up residual (RC6: a 50 ms reset with its TXDs floating dominant) | as a silenced controller | 2.203 s | 1.765 s |
| a persistent jammer (RC4: 70 s) | never returns; re-silenced at its first deviation after each release; holds 1, 2, 4, 8, 16, 32, 64 s | the surviving pair's gap 1 window | 6 releases, 2 state frames lost |
| a supervisor latched by W138's TPS2553-1 (R8b) | EN or power cycled: W138's draft drives no EN ("nothing in this draft drives EN"), and +5V_IOC follows U601's EN on RAIL_EN, the kit's own power | NONE automatic: an operator's power cycle | not simulated |

**Who cycles EN, and in what interval (the coordinator's question on W138's latch).** As drafted: nobody, so a latched supervisor
returns only by a kit power cycle (RAIL_EN), at the operator's time: the recovery proof is NOT met for that state (W139-F2). The route,
for L4A-54 and L4A-58 (L4REG-F3 names IOC_LIM_EN as the node) and not drafted here: the two peers restart a latched supervisor by a
2-of-2 pulse on its IOC_LIM_EN, each deciding on its own observation and needing no fabric (the target's buffered TXD silent, which the
buffer makes RECESSIVE for a dark controller, and no state frame of it for the loss count, 0.3 s), at most once per 10 s per target so
that a persistent fault spends at most W138's 23.5 mJ (MODEL) per 10 s; a single faulty peer then cannot restart, and so cannot brown
out, a healthy one. Bound: 0.3 s to decide, the pulse, at most 10 s of rate limit, then 0.8 s to rejoin. With two or three latched the
remaining one cannot restart alone (row 4's outcome until a supervisor returns), and only RAIL_EN returns all three.

## 7. Acceptance (canq 9) and the tests

| Predicate | Result |
|---|---|
| A1 the design has exactly CON-004's two fabrics: none removed, no third | yes |
| A2 every single-fault row, on both schedules, reaches at least its required outcome | yes |
| A3 no row relies on a fabric outside CON-004's two | yes |
| A4 no single fault silences a healthy controller on both fabrics at once | yes |
| A5 no single fault gets a controller whose bus behaviour conforms voted off | yes |
| A6 no single fault of a row that requires a quorum takes the surviving pair to the loss count | yes |
| A7 every latent fault of the vote path is found within a bound on the restated schedule, or is a named residual | yes |
| A8 every contained state returns within a bound once its cause ends (RC1 to RC3, RC5, RC6) | yes |
| A9 the contract draft carries this record's figures, composes after t10's, refuses twice and refuses the tree | yes |
| A10 CON-004 read as written: restated, not amended | yes |

The contract draft on a scratch copy: alone on the page without t10's rows, refused (exit 3); after t10's draft, checked and written
(exit 0); a second application refused (exit 3); alone on the tree's page refused (exit 3); the tree's page untouched. The tests
(`test_l9t5_canq.py`) hold the record and MUTANTS that must FAIL: a removed fabric (A1, A2), a third fabric (A1, A3), CON-004 read with
another count (A1), no attribution (A2), a 1-of-1 vote (A2, A4), a strike on a TXD reading alone (A5, on the stuck buffer), a vote
never released (A8), a loss count of one window (A2 or A6), FW-B21's stop as drafted (A2), W137's precondition read literally (the
own-request diode never found), a contract draft lacking a figure (A9).

## 8. SESSION decisions of this round (under the owner's standing rule of 26 September 2026)

| Id | Decision | Why | To reverse |
|---|---|---|---|
| W139-D1 | the restated window: a 10 ms slot per controller for all its frames, the self-test in its own segment (hold 52 to 88 ms) | no state frame is silenced by the test, so it runs with a fabric down and a two-faced controller never meets a single-copy window; slots give V5 and keep ES0392 2.24.5 away from healthy controllers | W137's schedule (every row is printed on it too) |
| W139-D2 | both fabrics tested in parallel, fabric B's target the next controller | a 12-window cycle: 2.51 s against 4.95 s, at no service cost | one transceiver at a time |
| W139-D3 | the V phase runs the attribution path end to end | the part 24 condition "faults affecting the diagnostic itself": the attribution path is the diagnostic | commanded votes (the path then NOT FOUND) |
| W139-D4 | the attribution rule V1 to V5; a strike only with the reader's own bus evidence; a vote on the reader's own strike, k = 1 | a dark or mis-read controller is never voted off (O1, the mutant), a jammer is out in 1.31 ms, and a denied fabric cannot block a verdict | k over 1 (slower, the gap grows; the mutant at 99 loses the quorum) |
| W139-D5 | a vote held 1 s, doubled within 10 s of a release, at most 64 s | a transient fault returns in about 2 s; a persistent one costs at most one window per release, ever rarer | a fixed hold |
| W139-D6 | the loss count 3 windows; a peer's state from either fabric; two copies that differ discarded | every single fault leaves the surviving pair a gap of at most 1 window | another count, rows re-run |
| W139-D7 | FW-B21's stop at the loss count, V-B21's stop time 400 ms | row F2: the drafted 100 ms (one window) loses the quorum to M1c's jammer | the drafted 100 ms with frames lost to an attributed deviation excluded |
| W139-D8 | DAR = 1 with ES0392 2.24.5's printed workaround inside the own slot | the self-test's probe and the bounded error count need it (row F1, W137-F1); slots keep 2.24.5 away from healthy controllers | DAR = 0 with the self-test redesigned |
| W139-D9 | a returning controller listens in bus monitoring mode for 2 windows and sets its outputs to the read-back first | IOHA A4 ("rejoins without moving anything") | another rejoin rule with its own proof |
| W139-D10 | R8b takes W138's "MAY latch" as written | the TPS2553 sheet is held back and not read here | the latch timer's behaviour read from SLVS841F |
| W139-D11 | the evaluation 1 ms (a firmware row) and a 0.5 s boot (ASSUMPTION) | figures the firmware must meet; neither is printed | the firmware's measured figures |
| W139-D12 | one time base: TIM3 counts the captures and, with FDCAN_TSCC.TSS = 10, the FDCANs' start-of-frame timestamps | RM0433 prints the choice (p.2529); the first-deviation rule compares the peers' TXDs with the reader's own frames | an FDCAN timestamp from its own prescaler, with the two counters correlated by the firmware |

## 9. Findings for other authors, and the supplier's tasks (amendment 1)

- **W139-F1 (Layer 6, `STM32H743-COMPATIBILITY.md`'s ES0392 2.24.5 row):** "firmware does not use DAR" contradicts FW-B21 and FW-B22
  (DAR = 1, L9T5-D2); ES0392 prints a workaround (restart on failure) and the restated slots keep 2.24.5 to faulty controllers: restate
  the row as "DAR = 1 with 2.24.5's workaround inside the controller's own slot".
- **W139-F2 (L4A-54 and L4A-58 by L4REG-F3; W138; board A's owner):** a latched TPS2553-1 has no automatic return (nothing drives
  IOC_LIM_EN; +5V_IOC follows RAIL_EN); the 2-of-2 peer restart of section 6 is the route; until it is drafted the recovery proof for a
  latched supervisor is NOT met.
- **W139-F3 (L4A-61, FW-B21's owner):** FW-B21's drafted 100 ms stop is one window of FW-B22; this round's draft restates it (D7).
- **W139-F4 (IOHA A7's owner, Layer 12):** A7's break links cut only controller A off a fabric (controller A sits alone on its segment);
  with both pairs out B and C keep a quorum (R8c), so "with both broken nothing moves" does not exercise row 8 (no majority); row 8
  needs a break between B and C too, which no link provides.
- **W139-F5 (W137, L4A-61):** W137's self-test precondition, read literally, is failed by its own S and V phases; restate it to exclude
  the test's own silence, or take the restated schedule.
- **W139-F6 (L4A-61):** on W137's schedule a two-faced controller meets windows in which one receiver takes a single copy.
- **W139-F7 (L4A-61, IOHA section 12's owner):** no FMEA row for the babbler, the GPIO-toggled TX, the two-faced controller or the vote
  path's faults: the rows of section 4 are the text for it (L9T5-F21's FMEA row among them).
- **W139-F8 (W137, L4A-61):** W137's V phase commands the votes, so the attribution path itself is never exercised in service.
- **For set 33's regeneration:** `l9t5_canq.out` pins `v2/docs/HW-FW-CONTRACT.md`, `apply_hw_fw_contract_t10.py`, `l9t5_t10.out`,
  `T10-ROUND5.md`, the ledger and the IOHA page; it changes no file that another output pins (`l9t5_t10.py` is untouched, and the
  round's sources are in `inputs/SOURCES-canq.txt`, not in `inputs/SOURCES.txt`, which `l9t5_case.out` and `l9t5_drafts.out` pin).
- **Supplier's tasks (none a gate of this desk round):** V-B22 restated (each TX pin driven as a GPIO, held, at the bit rate and once
  a window, on one fabric then both: SHDN high within section 2's figure and no peer missing 3 windows; each latent fault of section 5
  injected, found within its bound); the TPS2553-1's latch timer under an intermittent over-limit current (specimen: three
  first-article board B supervisors; pass: no latch from one attempt's dominant bits into a faulted fabric at 0.5491 A).

## 10. The four acceptance states (constitution section 2)

| Deliverable | Document acceptance | Supported design | Implementation | Physical qualification |
|---|---|---|---|---|
| the quorum service under M-B (`l9t5_canq.py`) | read by its author only | A1 to A10 hold on the DRAFTED rows and W137's circuit (MODEL on PRINTED timing) | no firmware exists; W137's circuit NOT APPLIED | V-B22 restated, first article |
| FW-B22 restated, FW-B21's stop (`apply_hw_fw_contract_canq.py`) | this round | composes after t10's, refuses twice and the tree | UNAPPLIED | V-B21, V-B22 |
| the recovery of a latched supervisor | this round | NOT MET (W139-F2) | none | none |

## 11. What closes once independently checked, and what stays open

Once an independent check reads it (with W137's circuit), this round would answer CON-004's quorum service under every row of the
fault table, HO-C (the GPIO-toggled TX attributed and silenced by hardware), FW-B22 (restated here), L9T5-F21's babbler row (its FMEA
text, for L4A-61) and the vote path's part 24 interval (2.51 s). Until then cx46's item 5 stays NOT CLOSED, CON-004's quorum service
OPEN, FW-B22 PROVISIONAL and the ledger's RE-5 REMAINING ENGINEERING. Open beyond that check: the latched supervisor's return
(W139-F2); the propagation of FW-B20 to FW-B22, V-B20 to V-B23 and IOHA section 12 (L4A-61); the thermal half (RE-6, RE-7, HO-D's
limiter half, HO-E: L4A-56 to L4A-59).

## 12. Reproduce

From the repository root: `python3 v2/docs/records/l9t5/l9t5_canq.py` (about 70 s on the runner; it touches no tree file and runs
the two contract drafts on a scratch copy). Output: `_bin/regen_out.py <worktree> v2/docs/records/l9t5/l9t5_canq.py
v2/docs/records/l9t5/l9t5_canq.out`. Tests: `env -C v2/ecad/tools python3 tests/run.py test_l9t5_canq.`

## Authority fields of this page's SESSION decisions (W159, 7 October 2026, on W157's finding F5)

Added by W159 (fnd/l4hod, row (b)'s composite for set 33) after row (b)'s focused check found these decisions without the explicit fields. Nothing in the decisions changes; each row below gives the fields the house format asks for. `reversed_by` none means not reversed; the way back is each decision's own To reverse (or Reverse by) text above.

| Id | authority | authority_why | ruled_by | ruled_on | reversed_by |
|---|---|---|---|---|---|
| W139-D1 | SESSION (the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026) | an engineering choice inside the drafted circuit or its contract text, taken on printed figures (the row's Why above): it changes no line a class of `v2/ecad/tools/reserved.json` protects, spends nothing, changes no claim about the kit and accepts no residual risk a measurement could remove; after the reading one option stands | W139 (Claude), MESHSAT-1357 | 2026-10-07 | none |
| W139-D2 | SESSION (the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026) | an engineering choice inside the drafted circuit or its contract text, taken on printed figures (the row's Why above): it changes no line a class of `v2/ecad/tools/reserved.json` protects, spends nothing, changes no claim about the kit and accepts no residual risk a measurement could remove; after the reading one option stands | W139 (Claude), MESHSAT-1357 | 2026-10-07 | none |
| W139-D3 | SESSION (the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026) | an engineering choice inside the drafted circuit or its contract text, taken on printed figures (the row's Why above): it changes no line a class of `v2/ecad/tools/reserved.json` protects, spends nothing, changes no claim about the kit and accepts no residual risk a measurement could remove; after the reading one option stands | W139 (Claude), MESHSAT-1357 | 2026-10-07 | none |
| W139-D4 | SESSION (the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026) | an engineering choice inside the drafted circuit or its contract text, taken on printed figures (the row's Why above): it changes no line a class of `v2/ecad/tools/reserved.json` protects, spends nothing, changes no claim about the kit and accepts no residual risk a measurement could remove; after the reading one option stands | W139 (Claude), MESHSAT-1357 | 2026-10-07 | none |
| W139-D5 | SESSION (the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026) | an engineering choice inside the drafted circuit or its contract text, taken on printed figures (the row's Why above): it changes no line a class of `v2/ecad/tools/reserved.json` protects, spends nothing, changes no claim about the kit and accepts no residual risk a measurement could remove; after the reading one option stands | W139 (Claude), MESHSAT-1357 | 2026-10-07 | none |
| W139-D6 | SESSION (the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026) | an engineering choice inside the drafted circuit or its contract text, taken on printed figures (the row's Why above): it changes no line a class of `v2/ecad/tools/reserved.json` protects, spends nothing, changes no claim about the kit and accepts no residual risk a measurement could remove; after the reading one option stands | W139 (Claude), MESHSAT-1357 | 2026-10-07 | none |
| W139-D7 | SESSION (the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026) | an engineering choice inside the drafted circuit or its contract text, taken on printed figures (the row's Why above): it changes no line a class of `v2/ecad/tools/reserved.json` protects, spends nothing, changes no claim about the kit and accepts no residual risk a measurement could remove; after the reading one option stands | W139 (Claude), MESHSAT-1357 | 2026-10-07 | none |
| W139-D8 | SESSION (the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026) | an engineering choice inside the drafted circuit or its contract text, taken on printed figures (the row's Why above): it changes no line a class of `v2/ecad/tools/reserved.json` protects, spends nothing, changes no claim about the kit and accepts no residual risk a measurement could remove; after the reading one option stands | W139 (Claude), MESHSAT-1357 | 2026-10-07 | none |
| W139-D9 | SESSION (the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026) | an engineering choice inside the drafted circuit or its contract text, taken on printed figures (the row's Why above): it changes no line a class of `v2/ecad/tools/reserved.json` protects, spends nothing, changes no claim about the kit and accepts no residual risk a measurement could remove; after the reading one option stands | W139 (Claude), MESHSAT-1357 | 2026-10-07 | none |
| W139-D10 | SESSION (the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026) | R8b reads the sheet's 'MAY latch' as written; the timer behaviour behind it is not described by TI's sheet, and no single-fault row depends on it (W157-F11); otherwise an engineering choice inside the drafted circuit or its contract text, taken on printed figures (the row's Why above): it changes no line a class of `v2/ecad/tools/reserved.json` protects, spends nothing, changes no claim about the kit and accepts no residual risk a measurement could remove; after the reading one option stands | W139 (Claude), MESHSAT-1357 | 2026-10-07 | none |
| W139-D11 | SESSION (the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026) | the 1 ms evaluation and the 0.5 s boot are labelled ASSUMPTION in the record and checked on the first article by V-B21 and V-B22; no verdict rests on them unlabelled; otherwise an engineering choice inside the drafted circuit or its contract text, taken on printed figures (the row's Why above): it changes no line a class of `v2/ecad/tools/reserved.json` protects, spends nothing, changes no claim about the kit and accepts no residual risk a measurement could remove; after the reading one option stands | W139 (Claude), MESHSAT-1357 | 2026-10-07 | none |
| W139-D12 | SESSION (the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026) | an engineering choice inside the drafted circuit or its contract text, taken on printed figures (the row's Why above): it changes no line a class of `v2/ecad/tools/reserved.json` protects, spends nothing, changes no claim about the kit and accepts no residual risk a measurement could remove; after the reading one option stands | W139 (Claude), MESHSAT-1357 | 2026-10-07 | none |
