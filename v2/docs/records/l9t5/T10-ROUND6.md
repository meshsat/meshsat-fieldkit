**ROUND 7 (T10; Layer 4 task L4A-54, 7 October 2026, W137, branch `fnd/l4canmb` from `06d064ff`): DONE: method M-B drafted as `apply_gen_sch_b_canmb.py` (iocguard's successor, release-guarded, NOT APPLIED), composed on board B with the 18 pending drafts of its change list (19 steps, every one OK), read by pin on the regenerated netlist (DRAWN; CON-004 HOLDS with and without it), seven mutations FAIL (the brief's three among them), three refusals; the pin plan recounted on the composed candidate and read against DS12110 Rev 10 (40 of 100; 14 supplies, 46 unconnected); the levels on the makers' printed rows, a faulty reader included; the vote path's in-service self-test with its interval (5.00 s) and its own faults; the test module (`test_l9t5_canmb.py`). NOT DONE: no independent check; nothing applied; the quorum service under every fault row, the attribution rule and the recovery proof (L4A-55); the propagation into FW-B20 to FW-B22, V-B20 to V-B23 and IOHA section 12 (L4A-61); nothing physical. NEXT: the coordinator's review and the independent check of M-B; then L4A-55.**

# T10 round 7: the CAN containment by the peers' 2-of-2 vote (the ledger's RE-5 and HO-C, method M-B)

Record l9t5, task T10, MESHSAT-1357; Layer 4 task L4A-54 of the AI-scope register (`_runs/l4ai/REGISTER.draft.md`, W129's draft 2,
row L4A-54), method M-B as re-selected by W129 on W127's finding 1. This page is the second T10 page: `T10-ROUND5.md` holds rounds 5
and 6 (round 6 is its section 12, the transmit-share limiter of `apply_gen_sch_b_iocguard.py`), and this page holds round 7. Prototype
design: nothing in this kit has been built, bought, powered or measured, and no figure here is a measurement. Every figure is printed
by `l9t5_canmb.py` into `l9t5_canmb.out` ("canmb N" below is its section). Labels: PRINTED (a maker's limit), TYPICAL, DECLARED,
DRAFTED (a contract row, not applied), MODEL, ASSUMPTION, SESSION. A DRAFT: like every draft of L4-E9's change list, None is APPLIED;
the draft refuses the tree's generator until `RELEASE-T10.md` names an accepted check.

## 1. Why, and what M-B keeps

cx46 ended round 6's method (FW-B22's schedule with the per-transceiver share limiter, R-245): "The GPIO jammer and latent comparator
cases remain admitted counterexamples." (cx46 finding 5, quoted in the ledger's RE-5). The record's own route was named and not drafted:
"each controller's TXD read by the other two and a 2-of-2 vote of the other two on its SHDN or its LDO's EN (twelve observation inputs
and six vote outputs, a pin plan for the three H743s): NOT DRAFTED here" (`l9t5_t10.out` 10j (c)). M-B drafts it and keeps the fixed
interface W127 found: CON-004, "Each I/O supervisor has its own regulator branch, reset supervisor, watchdog, crystal and SWD pads, and
the three talk over two independent CAN-FD fabrics with separate transceivers and termination.", accepted when "Netlist shows three
independent supply branches and two fabrics; A7 (either fabric cut, the quorum holds) passes." (canmb 2), with IOHA row 7 and test A7
as accepted. CON-004 reads HOLDS on the regenerated netlist with the draft and without it (canmb 3). No requirement is amended; the
point-to-point alternative stays only as owner item E-18, not raised.

## 2. The circuit drafted (`apply_gen_sch_b_canmb.py`, after iocguard)

| Part of M-B | What is drawn | Designators (controller A; B and C at +10, +20 and +2 for the buffers) |
|---|---|---|
| Observation (12 inputs) | each controller's TXD on each fabric drives a 74LVC1G34 buffer on its own 3.3 V; the buffer's output reaches each of the other two controllers through its own 2.2 kOhm 1 %; the reader's input is a TIM3 capture channel (canmb 5) | buffers U580, U581 (new) with C943, C945; R611 to R614 (new); readers on pins 63 to 66 (PC6 to PC9) |
| The TXD at rest | each TXD held recessive by 10 kOhm 1 % to its controller's own rail while the controller is in reset (TI prints no minimum for the TCAN334's integrated pull-up: TXD IIL -4 to 0 uA) | R606, R610 (the limiter pull-ups' places) |
| Vote (12 outputs) | each controller drives four votes, one per transceiver of the other two, on pins 55 to 58 (PD8 to PD11, GPIO) | pins only |
| 2-of-2 element (6) | an SN74LVC1G08 per transceiver on the TARGET's own 3.3 V, its two inputs the other two controllers' votes, each held low by 10 kOhm; its output lifts that transceiver's SHDN through a 1N4148W | U47, U48 (the limiter's places), R604/R605 and R608/R609, D401 and D403, C944 and C946 |
| Kept | each transceiver's own SHDN request and its diode (canshdn, iocguard), SD's 100 kOhm, the rail trips (INA169, TPS3701 on the LDO's EN) | D400, D402, R603, R607, U45, U46 |
| Removed (SESSION W137-D2) | the six transmit-share limiters: TPS3701 comparators, 1 MOhm and 150 kOhm dividers, 1 uF filters, LIMO pull-ups | every place re-used above; nothing removed outright |

Net change on board B: 18 parts added (12 resistors, 6 buffers), none removed, 42 of the limiter's places re-used with a new value
or new nets and the three controllers' new pins; 1533 parts against 1515; 1111 nets against 1087 (canmb 3). The parts are board B's
already: SN74LVC1G08DBVR (JLCPCB C7666), 74LVC1G34W5-7 (C526347), 1N4148W (C81598).

## 3. Composition, reading and mutations (canmb 3 and 4)

Board B in L4-E9's change-list order: record l8r2's and l8gnd's drafts, then iocbuck (R-233), iocpre (R-234), canshdn (R-235), iocset
(R-243), iocguard (R-245), this draft, the efuse record's R-236 and R-237, Layer 6's three tables: 19 steps, every one OK, the generator
run to its end through record l8p's `gen_netlist.py`. Read by pin: each TXD's net is exactly its controller, its transceiver, its
pull-up and its buffer's input; each buffer's output reaches exactly two isolation resistors; each reading pin is the planned one and,
traced back through its resistor and buffer, never reads its own controller's TXD; each SD is lifted only by its own request's diode
and its gate's diode; each gate sits on its target's rail with the two OTHER controllers' planned votes; no TPS3701 is left but the
rail trips, which stay: DRAWN.

| Mutation | Read by | Result |
|---|---|---|
| a draft that removes fabric B (every transceiver on fabric A) | CON-004 | FAIL |
| a vote that does not reach its SHDN (fabric A's vote diode on fabric B's SD) | the draft's reading | FAIL |
| an observation reading the node's own TXD | the draft's reading | FAIL |
| a 1-of-1 vote (both inputs from one peer) | the draft's reading | FAIL |
| the gate on a peer's rail | the draft's reading | FAIL |
| an observation without its isolation resistor | the draft's reading | FAIL |
| an observation without its buffer (the resistor on the TXD itself) | the draft's reading | FAIL |

The draft refuses a generator without iocguard, a second application, and the tree's own generator (NOT RELEASED).

## 4. The pin plan and CON-017's count (canmb 5)

Per controller, pins 63 to 66 (PC6 to PC9, FT_h and FT_fh in DS12110 Rev 10 Table 9; TIM3_CH1 to TIM3_CH4 at AF2 in Table 12) read
the next controller's TXD on fabrics A and B and the one after it on A and B; pins 55 to 58 (PD8 to PD11, FT_h, plain outputs) are its
votes. Every pin is free on the candidate before the draft, none is a debug pin (RM0433 Rev 8 p.533 names PA15, PA14, PA13, PB4, PB3),
the votes are analog (high impedance) during and just after reset (p.533), and each of TIM3_CH1 to TIM3_CH4 carries its own DMA request
(RM0433 Tables 122 and 123, inputs 23 to 26), so a reader can time-stamp every edge of the four TXDs it reads on one counter without a
processor step per edge. The count in CON-017's convention: the tree's board B 30 of 100; 14 supplies, 56 unconnected (reproduces the
evidence); the candidate before canmb 32 of 100; 14 supplies, 54 unconnected (canshdn's PD2 and PB14); with canmb 40 of 100; 14
supplies, 46 unconnected, the same on all three controllers. CON-017's restated count is for its owner (the registry is the
integrator's file).

## 5. The levels on the makers' printed rows (canmb 6, MODEL from PRINTED)

Each rail 3.2422 to 3.3577 V (AP2112K-3.3 band and load regulation at the rail's declared 0.25 A). A vote reaches the gate at least at
2.8422 V against VIH 2.0 V; a voter in reset or dark leaves it at most 0.0551 V against VIL 0.8 V. The gate lifts SHDN to at least
2.3773 V against the TCAN334's VIH 2.0 V (the diode's 0.715 V at 1 mA is printed at 25 C; taken as the bound at 45.3 uA and at the kit's
-20 C floor: ASSUMPTION, margin 0.377 V); SHDN rests at most 0.420 V. An observation reads the buffer at least 3.1422 V high against
2.3504 V and at most 0.6040 V low against 0.9727 V, with the reader's own pull-up enabled (RPU 30 to 50 kOhm PRINTED, a firmware row).

A faulty reader driving its input reaches only its buffer's output, through 2.2 kOhm: at most 1.646 mA, inside the 16 mA at which the
74LVC1G34 holds 2.4 V high and 0.4 V low (VCC 3 V, -40 to 85 C, PRINTED), so the other reader still reads 2.4 V against its 2.3504 V
(margin 0.050 V on a row printed for ten times the current and a lower supply) and 0.6040 V against 0.9727 V; the TXD and the
transceiver's input are never reached. So one reader cannot frame a healthy controller, in service OR while that controller is in reset
with its TX pin undriven: without the buffer (this round's first composition, 2.2 kOhm straight on the TXD) a faulty reader could pull
an undriven TXD dominant and get a resetting controller voted off with the honest peer's agreement, a single fault defeating CON-004's
quorum; the buffer is the correction (SESSION W137-D8). While its controller is in reset each TXD is held at least 3.2018 V by its
10 kOhm (W137-D9). A dark controller's readers read its unpowered buffer at least 2.7200 V, RECESSIVE (IOFF 10 uA PRINTED): a dark
controller is defined at its readers. The controller's own rail in the worst serving state: at most 0.1753 A against round 6's 0.1739 A,
inside C-DEV rev 2's conservative 0.2558 A (a labelled scenario for the coordinator; no case row is changed here).

## 6. The vote path's in-service self-test (canmb 7; specified for the firmware stage, its contract rows L4A-61's; nothing applied)

One transceiver at a time, never while a fabric is down, so the quorum keeps its three controllers on the other fabric and two on the
tested one. Per transceiver four phases, one per 100 ms window of FW-B22 (DRAFTED): S, the target's own SHDN request alone (silenced);
P1 and P2, one peer's vote alone (not silenced); V, both peers' votes (silenced). The asserting party holds its line from 10 ms after
the window opens to 10 ms before it closes; the state frames on the tested fabric go at mid-window; a silence is evidenced by three
readings (the target's attempt on its TXD at both readers with no frame of it on the bus, and its own receiver hearing neither peer:
SHDN high turns driver and receiver off and holds RXD high, TCAN334 Table 6-5 PRINTED).

| Item | Figure | Basis |
|---|---|---|
| silence takes effect | within 10.020 us of the second vote | GPIO edge 16.6 ns (DS12110 Table 160), gate tpd 3.6 ns, TCAN334 tMODE 10 us: PRINTED maxima |
| silence ends | within 13.01 us of the release | SD's 105 kOhm against 20 pF (ASSUMPTION: no SHDN capacitance printed) to VIL, plus tMODE |
| the guard's margin | 5.383 ms | 10 ms over FW-B22's 4.6 ms queue (MODEL), two crystals' 4.0 us drift (+-20 ppm) and the hardware |
| the vote edge | 6.18 ns/V against 10 ns/V | at 50 pF (a Layer 10 bound named here) |
| one cycle | 2.4000 s | 6 transceivers x 4 phases x 100 ms |
| a latent fault of the vote path | DETECTED WITHIN 5.00 s of its onset | exercised within a cycle, judged in the next window, declared on the 2nd consecutive failure |
| the cost | 80 ms of one transceiver silenced in two windows of four; the error count bounded | DAR = 1 (L9T5-D2): one attempt, +8, against at least 22 successes a cycle |

Its own faults (canmb 7, element by element): a vote stuck low, a vote stuck high, a gate stuck low, either diode open or short, a
transceiver ignoring SHDN: each found by a phase within 5.00 s; a gate stuck high, a capacitor shorted or a TXD pull-up shorted: at
once (the target's frames absent, IOHA rows 7 or 3); an isolation resistor open, a reading input stuck or a buffer stuck or open:
within 300 ms by the continuous reading; a stalled schedule: within one window by the published phase counter; a wrong verdict:
outvoted 2 of 3 and confirmed. Every one of the 72 parts of the six vote and six observation paths is the subject of a row. Four
RESIDUALS, each needing further faults and none defeating the containment alone: an open vote pull-down (acts only while its voter is in
reset or dark and the other votes wrongly), a shorted isolation resistor (matters only when its reader also drives its input, and then
reaches the buffer's output, never the TXD), an open SD resistor (TI's internal pull-down remains), an open TXD pull-up (TI's own
pull-up only while its controller resets; a resetting controller that then drives dominant is contained by the vote). A voter resetting
while asserting gives the gate a slow edge outside its 10 ns/V limit, which can only end a silence early.

## 7. The four acceptance states (constitution section 2)

| Deliverable | Document acceptance | Supported design | Implementation | Physical qualification |
|---|---|---|---|---|
| M-B's circuit (`apply_gen_sch_b_canmb.py`) | this round, read by its author only | composed, read by pin, seven mutations FAIL; levels on printed rows; no independent check | NOT APPLIED (release-guarded) | none; section 10's tasks |
| the pin plan | this round | read against DS12110 Table 9 and Table 12 and RM0433 p.533 and Tables 122 and 123 | NOT APPLIED | first-article SWD read of the pins' functions |
| the self-test | this round | interval 5.00 s on printed hardware timing and the DRAFTED window | no firmware exists | V-B (to be drafted under L4A-61): every row of section 6 injected on the first article |

## 8. What this closes once independently checked, and what stays open

Once an independent check reads it, this round would answer, for the circuit's part, HO-C's undrafted "2-of-2 peer observation and
vote" and the share half of HO-D (the limiter, and so its latent stuck comparator, is removed; the vote path's latent faults carry the
5.00 s interval). Until then cx46's item 5 stays NOT CLOSED, CON-004's quorum service OPEN, FW-B22 PROVISIONAL and L9T5-F21 OPEN, and
the ledger's RE-5 stays REMAINING ENGINEERING. The rail trip's half of HO-D, RE-6, RE-7 and HO-E stay with L4A-56 to L4A-59.

OPEN, L4A-55's (it analyses the quorum under every fault row with this circuit): the quorum SERVICE under IOHA rows 3, 5, 7 and 8 and the
added rows (the GPIO-toggled TX, a babbler, a stuck vote output, a two-faced controller on the common frame); the attribution rule
(which TXD activity is out of contract, read against the frames received); the recovery proof; FW-B22 restated on the two fabrics with
the test windows (a state frame taken from either fabric); DAR (finding W137-F1). L4A-61: FW-B20 to FW-B22, V-B20 to V-B23 and IOHA
section 12 restated.

## 9. SESSION decisions of this round (under the owner's standing rule of 26 September 2026)

| Id | Decision | Why | To reverse |
|---|---|---|---|
| W137-D1 | the vote acts per transceiver: twelve vote outputs (two per transceiver), not the record's six (one per controller) | the self-test the register names ("one transceiver silenced on one fabric while the quorum runs on the other") needs a vote per fabric; a one-fabric jammer then costs its controller that fabric only, so all three stay in the quorum; the pins fit (40 of 100) | one vote per controller on both SDs (six outputs), the self-test then silencing the whole controller for a window (IOHA A4's state) |
| W137-D2 | the transmit-share limiter of round 6 is removed, not kept as a first line | the vote covers the GPIO jammer and the babbler by attribution; the limiter's window (4.7 to 12.3 %) contains neither, its latent stuck comparator would need its own in-service test (HO-D's share half), and its response times are PROVISIONAL; the TCAN334's own DTO (1.2 to 3.8 ms PRINTED) still frees a held-dominant TXD in hardware | keep iocguard's limiter beside the vote (drop the draft's second edit); its comparator then joins L4A-58's in-service test |
| W137-D3 | the vote acts on SHDN, not on the LDO's EN | per-fabric containment keeps a jammer's controller in the quorum on its other fabric; EN stays the rail trip's (L4A-56 to L4A-58); a transceiver that ignores SHDN is IOHA row 7 (the other fabric) | the gate's output on the target's EN through a diode-OR with the rail trip |
| W137-D4 | each reader's input through 2.2 kOhm 1 % from the buffer, with the reader's own pull-up enabled | a faulty reader then moves at most 1.646 mA, inside the buffer's 16 mA row, and the low level keeps 0.369 V of margin; 4.7 kOhm left 0.169 V and a slower copy | another value with section 6 of the output re-solved |
| W137-D5 | readers on PC6 to PC9 (TIM3_CH1 to CH4, AF2), votes on PD8 to PD11 | one timer for the four TXDs a controller reads, each channel with a DMA request; no debug pin and no pin with a pull at reset under a vote | any free pins with the same functions, the plan re-read |
| W137-D6 | the 2-of-2 element is an SN74LVC1G08 on the target's own rail | board B's part (C7666) with Ioff printed; dark with its target, so a dark controller's gate draws nothing and leaves nothing driven | two series NFETs (needs an inversion to drive SHDN high) |
| W137-D7 | the self-test runs a phase in every window, four phases per transceiver, a 10 ms guard, a fault declared on the 2nd consecutive failure | the shortest interval the window allows (5.00 s) at no service cost (two of three controllers always on the tested fabric, three on the other), while one corrupted frame never declares a fault | a phase every N windows: the interval grows N times |
| W137-D8 | a 74LVC1G34 buffer between each TXD and its readers, on the TXD's own rail | without it a faulty reader can pull an undriven TXD dominant while its controller is in reset and get it voted off with the honest peer's agreement (a single fault defeating the quorum, found by this round's own analysis of its first composition); the buffer also makes a dark controller read recessive; board B's part (C526347) | the resistors straight on the TXD, with that single fault named as a residual for the owner |
| W137-D9 | each TXD held recessive by 10 kOhm 1 % while its controller is in reset | TI prints no minimum for the TCAN334's integrated pull-up (TXD IIL -4 to 0 uA), so the resting state of a resetting controller's TXD rested on an unprinted figure; the limiter pull-up's place re-used | drop the pull-up and keep TI's integrated pull-up |

## 10. Findings for other authors, and the supplier's tasks (amendment 1)

- **W137-F1 (L4A-55, Layer 5):** the contract draft reads "FDCAN_CCCR.DAR = 1" (L9T5-D2) and the compatibility page's ES0392 2.24.5 row
  reads "firmware does not use DAR". The self-test's probe and its bounded error count rest on DAR = 1; with DAR = 0 the target sends
  nothing on the tested fabric in its silenced phases and a silence rests on two readings, not three, with the same interval.
- **W137-F2 (the coordinator, L4-E9's change list):** a row for `apply_gen_sch_b_canmb.py`: board B, AFTER R-245 (it edits iocguard's
  lines), before R-236; l9t5's RELEASE-T10.md; DRAFTED (not applied). The composition here placed it there.
- **W137-F3 (CON-017's owner, the registry):** the count on the composed candidate is 40 of 100; 14 supplies, 46 unconnected; the
  compatibility page's section 3 gains eight rows per controller (pins 55 to 58 and 63 to 66, section 4 above).
- **W137-F4 (the coordinator, C-DEV):** each supervisor's worst serving state at most 0.1753 A (round 6: 0.1739 A), a labelled
  scenario inside C-DEV rev 2's conservative 0.2558 A.
- **W137-F5 (Layer 10):** two capacitance bounds the timing rests on, a vote line at most 50 pF and an observation line at most 46 pF
  (the pins' printed CIO 5 pF included); each buffer and its isolation resistors at the TXD's end of the lines.
- **W137-F6 (L4A-61):** with the limiter removed, round 6's limiter rows (V-B22's bench test of the limiter, `l9t5_t10.out` 10j (b) 1)
  describe a circuit this draft takes out; they stay as history until L4A-61 restates them.
- **W137-F7 (the register):** L4A-54's row reads "twelve observation inputs, six vote outputs"; this round draws twelve of each
  (W137-D1).
- **W137-F8 (board B's owner, the tree as it stands):** the tree's TXD lines have no pull-up and TI prints no minimum for the TCAN334's
  integrated one (TXD IIL -4 to 0 uA), so a supervisor in reset (its TX pin in analog mode, RM0433 p.533) leaves its transceiver's input
  on an unprinted figure; this draft's W137-D9 answers it on the candidate.
- **Supplier's tasks (none is a gate of this desk round):** on the first article of board B, every row of section 6 injected (a vote
  line held low and held high, each diode opened, a transceiver's SHDN lifted from its pad, a reader's input driven) with the self-test
  running, each found within 5.00 s; each vote line's and observation line's capacitance measured against the Layer 10 bounds; the
  1N4148W's forward voltage at 45 uA at -20 C (printed at 25 C only).

## 11. Reproduce

From the repository root: `python3 v2/docs/records/l9t5/l9t5_canmb.py` (about 6 s; it composes board B three times in temporary
directories, never the tree). Output: `_bin/regen_out.py <worktree> v2/docs/records/l9t5/l9t5_canmb.py v2/docs/records/l9t5/l9t5_canmb.out`.
Tests: `env -C v2/ecad/tools python3 tests/run.py test_l9t5_canmb.`
