**DISPOSITION (T10, 5 October 2026, after the recheck cx46 of 4d0ff8a2: CORRECTIONS NOT CLOSED, the second negative; the method ends), Slot C: cx45's Q3 stays NOT CLOSED [as written at this disposition, 5 October 2026; W53, 6 October 2026 (W38's F10, W48's residual): each word is its check's, Q3: cx45 'P0-3: NOT CONFIRMED' (`records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md` line 10), cx46's items 5 to 8 'NOT CLOSED' (`records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md` lines 136 to 151)] and is carried as REMAINING ENGINEERING with its claims OPEN or PROVISIONAL (section 12): CON-004's quorum service OPEN; FW-B22 PROVISIONAL (a traffic MODEL); L9T5-F21 OPEN; the limiter's and the rail trip's response times PROVISIONAL (no printed maximum for the comparator's delay); V-B23's 0.2 s WITHDRAWN; the universal sustained thermal bound WITHDRAWN (cx46's periodic countermodel, reproduced: 127.54 C under the trip); T10-A3 at a peak PROVISIONAL; revision X held with no admission route. What stays: the drafted circuits (apply_gen_sch_b_iocguard.py, composed, read, mutated) and the rows on revision V and R602 14.0k. NOT DONE: no new design; nothing applied; nothing physical. NEXT: the receiving company's scope (section 12's list).**

**ROUND 5 (T10, 5 October 2026), Slot C: DONE: V6-B3 corrected (CON-004 traced); FW-B20 and FW-B21 drafted; SHDN drafted, composed, read and mutated; the credible bus faults re-solved; C-DEV rev 2 issued from it; the owner's four questions of part 21 answered (every junction at the LDO's worst drop corner; rev V fitted, L9T5-D7); and the owner's part 22: the criterion per state (125 C for every sustained state, 150 C only for a transient hardware ends), the babbling supervisor a SUSTAINED state that FAILED 125 C on rev V (130.6 C) and holds with the set point delta drafted (R602 14.0k, apply_gen_sch_?_iocset.py: 121.5 C), revision V made enforceable by three drafted rows (Layer 6 identity, Layer 12 inspection, the model's selection). NOT DONE: no independent check; the rows unapplied; the babbler's quorum effect (L9T5-F21) not drafted; nothing physical. NEXT: Slot A takes the canshdn and iocset drafts and restates its pre-regulator check (L9T5-F24).**

# T10 round 5: the supervisors' regulators after the independent check V6 (L9T5-F06, F13, F16, F17)

Record l9t5, task T10, MESHSAT-1357, Slot C of the P0 power closure (owner's instruction of 5 October 2026, 14:20 CEST, its
amendment 1 of 15:45 and his review of checkpoint 2, part 21). Branch `fnd/p0t10` from `fnd/p0base` `e132db0e`. Prototype design:
nothing in this kit has been built, bought, powered or measured, and no figure here is a measurement. Every figure is printed by
`l9t5_t10.py` into `l9t5_t10.out` ("t10 N" is its section; round 5 is section 10). Labels: PRINTED (a maker's limit), TYPICAL,
DECLARED, MODEL, ASSUMPTION, SESSION. Case rows: C-DEV rev 1 and rev 2 (issued 16:00 from this round), C-PROT rev 1.

## 1. What V6 found and what this round does

| V6 item | This round | Where |
|---|---|---|
| V6-B3 | CON-004 (constraint, core, BLOCKER; accepted when test A7 passes) covers both fault states through `ARCH-PCB-B-IOHA.md` section 12 rows 7 and 8; the sentence is replaced in `l9t5_t10.py`, its output and `L9T5-CASES.md`; A7 as written cuts a fabric and does not exercise the shorted-bus row | t10 8 (f1), (f2); t10 10a |
| item C, F13 | FW-B21's share: each supervisor's own TXD dominant at most 2 % of every 100 ms window per fabric, with FDCAN_CCCR.DAR = 1 so every transmission is a scheduled one | t10 10d |
| item C, T10-A1 | FW-B20 drafted; the reference manual is held (RM0433 Rev 8): the reset state (HSI 64 MHz, VOS3) is inside the bound | t10 10b |
| V6-m10 | the enabled peripherals bounded from Table 39 (rev Y) and Table 137 (rev V); each figure states its air; every junction at the LDO's worst drop corner (part 21) | t10 10c, 10h (1) |
| item C, F16, F17 | every credible bus fault inside board B with its current and junction held, with the parts alone and with the response; the response drafted as firmware rows and a circuit change | t10 10e, 10f |
| V6-m9 | CON-017 (5) fits revision V or X; (4) refuses both fabrics on Y or W; rev Y's larger rows are the cover for a rev X part | t10 10a |
| item C, case row | C-DEV's supervisor figure derived; issued by the coordinator as C-DEV rev 2 | t10 10g, 10h (4) |

## 2. The four acceptance states (constitution section 2)

| Deliverable | Document acceptance | Supported design | Implementation | Physical qualification |
|---|---|---|---|---|
| T10 (L9T5-F06): K3 with FW-B20 | rounds 4 and 5 read by their author only | T10-A2 holds at 76.25 C on rev V's rows, 109.4 C at the drop's worst corner; NOT on rev Y's (125.2 C), so rev V is fitted (L9T5-D7); T10-A3, T10-A4 as round 4 | the iocpre drafts composed and mutated (round 4); FW-B20 unapplied; no firmware exists | T10-A5, the supplier's (section 6) |
| F13: FW-B21's share | this round | 109.4 C on rev V against 125 C (MODEL); the transceivers' 20 mA declaration holds for any dominant current up to 828.5 mA at the share | FW-B21 unapplied | V-B21 confirms the schedule |
| F16, F17: FW-B21's fault handling and the SHDN draft | this round | every credible single fault 110.0 C at worst on rev V, both fabrics 110.7 C on rev V and 126.5 C on rev Y's cover (inside 150 C) | `apply_gen_sch_b_canshdn.py` composed straight after T10's iocpre: SHDN DRAWN, the board before it FAIL, three mutations FAIL; FW-B21 unapplied | V-B21's fault injections |

## 3. The owner's four questions (part 21; t10 10h)

**(1) What the result rests on and where its margin is lost.** The inputs: the air (L4-E12 E5's mixed 76.25 C, the case's; 81.89 C in
the exhaust); the LDO's 184 C/W "no heat sink" (no board printed: the layout must give each LDO at least that copper, a Layer 10
means read by T10-A5); the pre-regulator's top 4.2907 V with every tolerance at its worst; the LDO's least output 3.2505 V (98.5 %,
PRINTED), the corner of its largest drop, 1.0402 V and 191.4 K/A (round 4 and this round's first pass used the nominal 3.3 V: 0.9907
V, 182.3 K/A, which is not the worst corner); the controller's printed maxima at its own junction; the enabled set's bound; the
circuit's auxiliaries at the full rail; the share fully used. At that corner and the case's air:

| State | rev V (fitted) | rev Y's rows (the cover for rev X) |
|---|---|---|
| the bounded state | 0.1732 A, 109.4 C, margin +15.60 K; lost at a local air of 84.20 C | 0.2558 A, 125.2 C, margin -0.22 K |
| the worst single fault, responded | 0.1766 A, 110.0 C, margin +14.96 K; lost at 83.90 C | 0.2592 A, 125.9 C, margin -0.86 K |
| both fabrics faulted, responded | 0.1799 A, 110.7 C, margin +14.31 K; lost at 83.60 C | 0.2626 A, 126.5 C, margin -1.50 K |

What consumes the margin: the controller's leakage at its own junction (rev Y's 144 MHz row climbs from 120 mA at 85 C to 180 mA at 105 C),
the enabled set's bound and the drop's corner; each kelvin of local air costs 1.71 K at the LDO on rev V's rows and 11.36 K on rev
Y's. So rev V holds over the 81.89 C exhaust; rev Y's rows do not hold even at the case's air. **SESSION L9T5-D7: the supervisors are
fitted in revision V** (inside CON-017 (5)). **SUPERSEDED (round 6, and the recheck cx46's item 8), kept as written only as history,
not an instruction:** round 5's admission route for a rev X part ("accepted only after the supplier's V-B20 reads its supply current
at the bound at most 0.2318 A"; rev V's rows 0.1570 A, rev Y's 0.2396 A) and L9T5-F22's shortcut (R602 14.0 k with T10-A3 at
0.4512 A, 3.7004 V over 3.6652 V, rev Y's cover at 118.1 C, "that would admit any revision without V-B20"). **Current instruction:**
revision V only; revision X HELD with no admission route; R602 14.0 k is the final set point; a rev X part's qualification is
REMAINING ENGINEERING (section 12).

**(2) The CAN service under the bound.** The fabrics carry the supervisors' quorum only; the modules' heartbeats (GPIO, FW-B01), the
voted outputs (GPIO, FW-B12) and FW-E07's stopped-fan report (board E, the kit bus, V-E07's 5 s) are not on them. The tree defines no
CAN message rate; the record ASSUMED (round 5; SUPERSEDED in round 6 by the drafted schedule FW-B22, section 12) one state frame per supervisor per fabric per 100 ms and a burst of 8 event frames when ownership
moves. With every bit of a 135-bit frame counted dominant and two acknowledgements a frame, the 2 % share leaves 7 frames a window at
500 kbit/s and 14 at 1 Mbit/s (1 at 125 kbit/s, which FW-B21 therefore excludes: its rates are now 500 kbit/s to 1 Mbit/s). REQ-004's
30 s is 300 windows; A7's surviving fabric carries the same traffic under its own share. The firmware confirms its real message set
against it (V-B21).

**(3) What enforces the bound and the response.** Hardware, whatever the firmware does: the TCAN334's driver time-out (1.2 to 3.8 ms,
PRINTED); the FDCAN's own bus-off (INIT set by the device, no automatic restart); any reset (the IWDG, hardware-started under FW-B10)
returns the reset state, inside the bound, with every TXD recessive; SHDN's 100 k keeps normal mode by default. Firmware, once the
rows are applied and built: the clock read-back, DAR = 1, the share, the stop and shutdown of a faulted fabric within 100 ms. Each
window carries at most 2 ms of own dominant drive by the schedule, so a fault's current is averaged whatever the detection time (the
per-fault table is t10 10h (3)). The firmware as the faulting party: a hang ends at the IWDG; with DAR mis-set and the CPU hung,
B6's endless retransmission reads 133.2 C on rev Y's cover; a babbling supervisor at the clock bound reads 146.4 C on rev Y's cover:
under 150 C, over 125 C (it costs margin, not the regulator; its quorum effect is finding L9T5-F21). A firmware that breaks the CLOCK
bound takes the H743 itself outside its rating and can take the LDO over 150 C: nothing in hardware prevents it (round 5; SUPERSEDED in round 6: the rail trip, section 12, holds each supply's average at 0.2452 A or less). That is a systematic
firmware defect, closed by the firmware's verification (FW-B20's read-back, V-B20, CON-017 (4)'s firmware stage): an OPEN
implementation obligation, not a desk-fixable circuit defect. **SESSION L9T5-D6:** round 4's K1 (a buck per supervisor) is not taken
for it, because it would keep the regulator alive in a state the controller itself cannot hold; to reverse, K1.

**(5) The owner's review of checkpoint 3 (part 22): the criterion per state, the babbling and hung rows (t10 10i).** A SUSTAINED state,
served or a fault the design must survive, is judged at 125 C: 150 C is the absolute maximum and never an operating target. A TRANSIENT
that hardware ends within a bound is judged at 150 C on its steady-state figure (an upper bound of any transient). Every row of 10e is
sustained (a bus fault stays until repaired). The hung row (the CPU hung with DAR mis-set) is a transient the IWDG ends (hardware-started
under FW-B10). The babbling row (a running firmware that breaks FW-B21 and still serves its watchdog) is ended by nothing: SUSTAINED, so
125 C applies, and on revision V with iocpre's 13.3k it reads 130.6 C: it FAILED. The response drafted: the set point delta
`apply_gen_sch_a_iocset.py` and `apply_gen_sch_b_iocset.py` (after iocpre; L9T5-F22 drafted): R602 14.0k, 4.0114 V nominal, 3.9063 to
4.1174 V, the drop at its worst corner 0.8669 V (159.5 K/A). On revision V every row then holds 125 C (bounded 103.9 C, the worst fault
104.4 C, both fabrics 104.9 C, B7b with SHDN ignored 112.7 C, hung 110.5 C, babbling 121.5 C). It composes (board A 22 drafts, board B
14), reads 14.0k, refuses a generator without iocpre and the tree's, and its two mutations (the divider inverted, R602 back to 13.3k)
FAIL. T10-A3 is restated at the largest current the record computes for a regulator (0.4512 A): the LDOs' input at least 3.7004 V
against 3.6652 V (SESSION L9T5-D8; round 4's 600 mA criterion fails at 14.0k, and a supervisor drawing more browns out alone under its
BOR). On rev Y's rows (the cover for rev X) every served row holds at 14.0k except the babbler (134.7 C) and B7b with SHDN ignored
(125.9 C): a rev X part still waits on V-B20. The service in the babbling state: the babbler can deny both fabrics by arbitration, so
the quorum may stop and the voters hold the home assignment (row 8's safe state); that one supervisor's firmware can stop CON-004's
quorum stays OPEN (L9T5-F21: a voted silence of the babbler by the other two is the circuit direction, not drafted).

**(6) Revision V made enforceable (part 22, C; drafted rows, not applied; named prerequisites of the Layer 4 power gate, reason L9T5-D7
and t10 10h, 10i):**

| Layer | Row (drafted) | Acceptance |
|---|---|---|
| 6, part identity (`STM32H743-COMPATIBILITY.md` F1 and the BOM line of U41, U51, U61) | STM32H743VIT6, LCSC C114409, SILICON REVISION V ONLY: package marking revision code "V", DBGMCU_IDC REV_ID 0x2003 (ES0392 Rev 15 Table 2); revisions X and Y not accepted | the BOM line and the compatibility page name revision V |
| 12, incoming inspection and first article | every supervisor's package read for revision code "V" before assembly, a lot with any other code held; at first power each supervisor's REV_ID read over SWD equal to 0x2003 | the inspection record names each part's code; no other code fitted |
| the model (`l9t5_t10.py`) | the verdicts of F13, F16, F17 and the part 22 rows read revision V's printed rows only (`FITTED_REV`); revision Y's rows are printed as the cover for rev X and decide nothing | the test keys the verdicts to `FITTED_REV` |

**(4) The composed changes against the calculation and the case row.** The contract draft's rows carry the record's figures (VOS3, at
most 144 MHz, 2 % of every 100 ms, the 100 ms stop and the once-a-second probe, DAR = 1, PD2 and PB14 with 100 k, 500 kbit/s to
1 Mbit/s): every one. The SHDN draft's nets read DRAWN in the regenerated board B netlist. C-DEV rev 2 as issued (copied verbatim
into `inputs/cases-cdev-rev2-20261005.md` from `_runs/cases/CASES-2026-10-04.md` at sha256 b2dfb4a6..., with its 16:25 clarification) carries this output's 0.2558 A,
0.1732 A, 0.2396 A at TJ 111.8 C, 2.966 W, +5V_IOC 0.8989 A and 0.0069 A: every one equal. Its regulator figures are currents and stand;
at the worst drop corner rev Y's 0.2558 A reads 125.2 C, which L9T5-D7 answers.

## 4. The credible bus faults, their figures and responses (t10 10e; each regulator at 76.25 C at the worst drop corner, MODEL)

Both fabrics lie wholly on board B (no connector on CANH_*/CANL_*). Board B carries no rail below 0 V, so the TCAN334's 180 mA
bus-fault row (CANH at -12 V) has no source in this kit; it is used only as the ASSUMED figure for the faults whose current TI does
not print.

| Fault | What the bus does | I_f | Held, rev V | With the response, rev V / rev Y's cover |
|---|---|---|---|---|
| B1 CANH to GND (SOIC-8 pins 7 and 8 adjacent, STB on GND) | bits read wrong: errors, bus-off | 0.1800 A ASSUMED | 143.0 C FAILS | 109.9 C / 125.7 C |
| B2 CANH to CANL (pins 6 and 7) | as B1 | 0.1800 A ASSUMED | 143.0 C FAILS | 109.9 C / 125.7 C |
| B3 CANL to GND | the bus still works | 0.0809 A MODEL | 124.0 C | 109.5 C / 125.3 C |
| B4 CANH to a 3.3 V or 5 V net | the bus still works | 0.1160 A MODEL | 130.7 C FAILS | 110.0 C / 125.9 C |
| B5 CANL to a 3.3 V or 5 V net | errors, as B1 | 0.2000 A ASSUMED | 146.8 C FAILS | 109.9 C / 125.8 C |
| B6 an open (A7's cut) | no acknowledgement | 0.0550 A MODEL | 119.0 C | 109.4 C / 125.2 C |
| B7a TXD held low | the DTO frees the bus in 1.2 to 3.8 ms (PRINTED) | 0.0600 A PRINTED | 120.0 C | 109.4 C / 125.2 C |
| B7b driver stuck on, DTO dead | the bus held dominant | 0.0600 A MODEL | 120.0 C | 108.5 C if SHDN acts; 120.0 C if not (rev V) |
| both fabrics faulted (row 8) | nothing moves (accepted) | the worst on both | 184.2 C, over 150 C | 110.7 C / 126.5 C, inside 150 C |

The response does not rest on the unprinted fault currents: at the 2 % share a transceiver's average stays under its 20 mA
declaration for any dominant current up to 828.5 mA.

## 5. CORRECTED and OPEN

- **V6-B3: CORRECTED** (a record statement), read from the trace by the script; the regression test fails on the old sentence.
- **L9T5-F13, F16, F17: DRAFTED CORRECTIONS, desk acceptance met by their author on rev V's printed rows (fitted under L9T5-D7) at the
  worst drop corner; they stay OPEN in the register** until an independent check reads them and Layer 5 applies FW-B20 and FW-B21.
  The circuit half composes, reads DRAWN and fails under mutation; the firmware half is a contract row (no supervisor firmware exists).
- **L9T5-F06: STAYS OPEN** for the same check and application; T10-A5 is the supplier's (section 6); the clock bound's enforcement is
  an OPEN firmware-verification obligation (section 3 (3)).
- **Residual B7b:** a transceiver whose driver, time-out and SHDN fail together: 120.0 C on revision V, the fitted part, inside 125 C
  (round 6: L9T5-D5 WITHDRAWN, nothing is tolerated over 125 C; over the rail trip's least 0.2183 A the supervisor is unpowered and the
  other two hold the quorum).
- **Revision X: HELD** (not fitted, round 6) until its own qualification: V-B20 in its bounded state at most 0.2183 A (the rail trip's
  least) and its rows re-solved; no revision V figure is applied to it.

## 6. The supplier's validation tasks and the bounded provisional choices (amendment 1)

| Fact not established at the desk | Claim it supports | Bounded provisional choice | Supplier task: specimen, quantity, pass limit |
|---|---|---|---|
| a rev X controller's supply current (DS12110 prints rev Y and rev V only) | T10-A2, F13, F16 on a rev X part | fit rev V (L9T5-D7); revision X HELD | three rev X STM32H743VIT6 on the first-article board B: each supervisor's supply current at the FW-B20 bound and FW-B21 share at its operating junction: at most 0.2183 A (V-B20, the rail trip's least) |
| the enabled peripherals' maxima (typical only printed) | T10-A2 | typical times 144 MHz times the whole set's max/typ ratio (MODEL) | the same measurement (V-B20) |
| each LDO's thermal resistance on board B's copper (184 C/W printed, its board not printed), and its transient impedance (not printed) | every junction; the trip's transient | the printed 184 C/W; the steady figure as the transient's bound | first-article board B in a 76 C chamber with one supervisor forced to its rail trip (round 6): each AP2112K's implied junction, its junction-to-air resistance and its step response MEASURED and reported, and the INA169's site under 85 C (T10-A5 restated): measurements, NOT an acceptance of a sustained bound (cx46: the periodic countermodel meets the round 6 limits and passes 125 C; the bound is REMAINING ENGINEERING) |
| the TCAN334's current with a bus line at 0 V or on a rail (not printed) | B1, B2, B5 | the printed 180 mA and 200 mA rows; the share holds to 828.5 mA | V-B21: each fault injected with traffic running; each AP2112K's output current averaged over 1 s at or under the response figure |
| the firmware's implementation of FW-B20 and FW-B21 | every row | the drafted rows | V-B20, V-B21 on the first firmware build; the clock bound's code review (CON-017 (4)) |

## 7. For the coordinator: C-DEV rev 2

Issued at 16:00 from this round (0.2558 A a regulator on rev Y's rows, 0.1732 A on rev V's; the budget form 2.966 W and +5V_IOC
0.8989 A). Section 3 (4) reads the issued copy against this output: equal. Under L9T5-D7 the fitted revision is V, so 0.1732 A is the
fitted figure; 0.2558 A stays the conservative one for power.

## 8. SESSION decisions of this round (under the owner's standing rule of 26 September 2026)

| Id | Decision | Why | To reverse |
|---|---|---|---|
| L9T5-D1 | the share 2 % of every 100 ms window per fabric | 7 to 14 frames a window at 500 kbit/s to 1 Mbit/s, above the assumed need; keeps the fault responses inside 125 C on rev V | a larger share with the junctions re-solved (`SHARE`) |
| L9T5-D2 | FDCAN_CCCR.DAR = 1 | every transmission a scheduled one, so the share holds whatever the fault (B6's endless retransmission removed) | automatic retransmission with a bounded retry count in FW-B21 |
| L9T5-D3 | SHDN on PD2 (fabric A) and PB14 (fabric B), 100 k to GND | free GPIO next to each FDCAN's pins; today's normal mode kept in reset; TI does not want the internal bias relied on | drop `apply_gen_sch_b_canshdn.py` |
| L9T5-D4 | judged at 76.25 C at the drop's worst corner; FDCAN's peripheral current counted twice; the circuit's own auxiliaries instead of the 0.020 A declaration | the case's air; one clock enable serves both instances; the declaration is not a bound | read at the exhaust air (t10 10c prints it) |
| L9T5-D5 | WITHDRAWN (round 6): was the B7b residual tolerated where it is over 125 C | on revision V, the fitted part, B7b reads 120.0 C, inside 125 C; nothing is tolerated over it | none |
| L9T5-D6 | REVERSED (round 6): was K1 not taken for a firmware that breaks the clock bound | the rail trip (L9T5-D10) bounds that supply's AVERAGE in hardware instead (PROVISIONAL at a peak, section 12) | none |
| L9T5-D8 | SUPERSEDED (round 6): T10-A3 is judged at the rail trip's AVERAGE maximum, 0.2452 A, the sense resistor's drop counted (3.6524 V against 3.5213 V); PROVISIONAL at a peak (cx46) | no supervisor carries a larger AVERAGE; a periodic peak is not covered | none |
| L9T5-D7 | the supervisors fitted in revision V | rev V's printed rows hold with 14 K or more; rev Y's (the cover for rev X) miss 125 C; inside CON-017 (5) | a rev X part only after its own qualification (V-B20 at most 0.2183 A) |
| L9T5-D10 (round 6; renamed from D9, L9T5-F27: Slot A's D9 is the set point) | the containment as hardware on each controller: a transmit-share limiter per transceiver and a rail trip per supervisor (`apply_gen_sch_b_iocguard.py`), not a vote of the peers | no firmware sets either bound, a fault common to all three firmwares included; no H743 pin plan needed; the parts are the kit's (INA169, TPS3701) | the peers' 2-of-2 vote on SHDN or EN with TXD observation (twelve inputs, six outputs) |

## 9. The README lines for Slot A to apply (the README is Slot A's)

- Lines 58 and 59, replace "a served fault state no requirement covers (**L9T5-F16 OPEN**, Layer 5's owner); both faulted, 176.3 C,
  over the 150 C absolute maximum, no requirement covers it (**L9T5-F17 OPEN**, Layer 5's owner)" with "a served fault state covered by
  CON-004 through IOHA row 7 (**L9T5-F16 OPEN**; round 5 drafts its response, `T10-ROUND5.md`); both faulted, 176.3 C held, over the
  150 C absolute maximum, covered by CON-004 through row 8 (**L9T5-F17 OPEN**; round 5)".
- Line 172, replace "the CAN fabric-fault rows, which no requirement covers, with the response each needs (t10 8)" with "the CAN
  fabric-fault rows, covered by CON-004, drafted as FW-B20 and FW-B21 with the SHDN draft (t10 10)".
- Rows C58 and C59, replace "no requirement covers this fault state (REQ-073 covers the other direction ...)" and "no requirement
  covers this fault state" with "covered by CON-004 (constraint, core, BLOCKER) through IOHA row 7 (C58) or row 8 (C59) and test A7".
- Line 1 (status): add "Round 5 (T10, Slot C): `T10-ROUND5.md`; F13, F16, F17 drafted corrections on rev V (L9T5-D7), OPEN pending the
  independent check; L9T5-F22 (R602 14.0 k) offered".
- The composition order (`l9t5_drafts.py`): `apply_gen_sch_b_canshdn.py` after `apply_gen_sch_b_iocpre.py`, and a row for it in L4-E9's
  change list (L9T5-F20). `inputs/SOURCES.txt`: one line for `inputs/cases-cdev-rev2-20261005.md` (the C-DEV rev 2 section of
  `_runs/cases/CASES-2026-10-04.md` at sha256 b2dfb4a643f9f997..., copied verbatim with its 16:25 clarification, 5 October 2026).
- Round 6 (the check cx45's Q3): line 1 (status), add "Round 6 (T10, Slot C): `T10-ROUND5.md` section 12; the containment drafted
  (`apply_gen_sch_b_iocguard.py`: transmit-share limiters and rail trips), FW-B22 and V-B22, V-B23 drafted, revision V only at R602
  14.0 k"; the composition order: `apply_gen_sch_b_iocguard.py` after `apply_gen_sch_b_iocset.py`, with its row in L4-E9's change list;
  `check_l9t5_netlist.py`'s I-03 entry restated for the LDOs behind their sense resistors (L9T5-F25).

## 10. Findings for other authors

L9T5-F18 (board B's generator owner): SHDN on no net, answered by the draft. L9T5-F19 (Layer 10): +54V_POE, POE_P and the PoE pairs
exceed the transceivers' 14 V bus pins; a clearance is a layout means, not credited. L9T5-F20 (Layer 6 and L4-E9): PD2 and PB14 become
outputs; R67, R68, R79, R80, R91, R92 need order codes; the draft needs its change-list row. L9T5-F21 (Layer 5, IOHA section 12): a
babbling supervisor is in no FMEA row and can stop the quorum (part 22: OPEN, its voted silence not drafted). L9T5-F22: DRAFTED in
part 22 as `apply_gen_sch_?_iocset.py` (Slot A folds it into iocpre). L9T5-F24 (Slot A): `check_l9t5_netlist.py`'s 't10' divider
restated to 14.0k when the delta is taken.
L9T5-F23 (Layer 6, part identities and procurement): L9T5-D7 fits silicon revision V. The order code STM32H743VIT6 fixes no
revision (L9T5-F14); CON-017 (5) already reads the marking (V or X) and REV_ID at goods-in, so D7 narrows the accepted lots to V.
Consequence (SUPERSEDED in its admission clauses by round 6 and cx46's item 8): a lot of rev X is HELD; no V-B20 reading and no set
point admits it; its qualification is REMAINING ENGINEERING. No purchase is made and no supplier is asked here; lot availability of
rev V against rev X is not read (no distributor query sent).

## 12. Round 6 and its disposition: the check cx45's Q3 and the recheck cx46 (t10 10j)

cx45 (Astra's focused check of 06077cee) read Q3 NOT CONFIRMED; round 6 drafted a correction; cx46 (the targeted recheck of 4d0ff8a2)
read it CORRECTIONS NOT CLOSED, the second negative, so the method ends: this section is the DISPOSITION (text and predicates, no new
design). Every claim is OPEN or PROVISIONAL; what stays is drafted and reproducible, not closed.

| Item | What stays (drafted, reproducible) | Disposition | REMAINING ENGINEERING (for the receiving company) |
|---|---|---|---|
| (a) schedule, FW-B22 | 822 dominant bit-times at most against FW-B21's 1000 at 500 kbit/s; a state frame waits at most 4.6 ms (a traffic MODEL) | PROVISIONAL: it is not fault-contained quorum service; L9T5-F21 (a TX pin toggled as a GPIO under the limiter's share) and a latent stuck share comparator are admitted counterexamples | the peer-silence or diagnostic circuit and the recovery proof |
| (b) containment | `apply_gen_sch_b_iocguard.py`: a transmit-share limiter per transceiver and a rail trip per supervisor, composed, read by pin, six mutations FAIL | PROVISIONAL: the response times (16 ms, 0.23 s) are MODEL figures without a printed maximum for the comparator's delay (TYPICAL only in SBVS240C); V-B23's "within 0.2 s" WITHDRAWN (the drafted network, its charging path RL + RF, takes about 0.98 s from the bounded state, MODEL) | a corrected rail-trip response mechanism and the complete network calculation, protection not relaxed |
| (c) quorum per fault | the fault table of t10 10j (c) | CON-004's quorum service OPEN; L9T5-F21 OPEN; VOS0 under the trip (the H743 at its 105 C VOS0 limit from 0.1936 A, MODEL, under the trip's band) weakens the controller's survival and FW-B20's and FW-B22's service | the same circuit and proof as (a); a hardware bar on VOS0 or its acceptance |
| (d) headroom | the other LDOs at 3.6571 V against 3.4798 V during a response; T10-A3 at the trip's average maximum 3.6524 V against 3.5213 V | PROVISIONAL at a peak current (the trip holds an average) | T10-A3 on the peak current the containment allows |
| (e) thermal | the constant-current figure at the trip's average maximum, 115.4 C (MODEL) | the universal sustained bound and its positive margin WITHDRAWN: cx46's periodic countermodel, reproduced on its ASSUMPTIONS (0.50 A for 0.40 s every 1.50 s, one pole of 184 K/W and 0.25 s): its filtered current 0.2122 A stays under the trip's least, its Zth(171 ms) 91.2 K/W meets the proposed limit, and its junction peaks at 127.54 C; a latent rail trip removes even the average bound; the qualification limits are measurements, not an acceptance | peak-current containment, or a complete periodic electrothermal solution with uncertainty |
| (f) rows | revision V only, R602 14.0 k, 125 C for every sustained state in the contract draft, the 10i rows, this page and the output | revision X HELD with no admission route; round 5's V-B20 route at 0.2318 A and L9T5-F22's "admits any revision" SUPERSEDED (sections 3 (1) and 10) | a rev X part's qualification, resting on (e) |

SESSION decision **L9T5-D10** (renamed from D9 under L9T5-F27; Slot A's D9 is the set point) stays as a drafted direction, not a closure.
Findings: L9T5-F25 (Slot A): `check_l9t5_netlist.py`'s I-03 entry for the LDOs behind their sense resistors. L9T5-F28 (Slot A; renamed from L9T5-F26 under the remaining-engineering ledger's item A, `records/l4close/REMAINING-ENGINEERING.md` section 6, the way L9T5-F27 settled D9 and D10: this page first wrote "L9T5-F26 (Slot A, its
`l9t5_connected.out` 193-199, 282-301, 350-352)", lines of that output at 4d0ff8a2, and L9T5-F26 is Slot A's finding on J_PA's VH derating, `README.md` lines 194 to 196 and `l9t5_connected.out` lines 356 to 358 at 53a68c7c; the same three places in that output at 53a68c7c are lines 194 to 203, the guard row, 293 to 317, the final figures, and 387, 388 and 390, the T10 predicates): its connected verdicts inherit this section's OPEN and PROVISIONAL claims (the latent
rail trip, the sustained peak, the guard's L8P-R9-F1). For the coordinator (C-DEV): the limiters' two pull-up currents raise each
supervisor's bounded state to 0.1739 A on revision V (against C-DEV rev 2's 0.1732 A, inside its conservative 0.2558 A); no row is
changed by this record.

## 11. Reproduce

From the repository root: `python3 v2/docs/records/l9t5/l9t5_t10.py` (about 20 s; it composes both boards and board B again with the
SHDN draft, in temporary directories). Tests: `env -C v2/ecad/tools python3 tests/run.py test_l9t5.`

## W9 (6 October 2026): one identifier restated

Line 227: the second finding of section 12 is L9T5-F28, renamed from L9T5-F26 (the remaining-engineering ledger's item A); L9T5-F26
stays Slot A's finding on J_PA's VH derating. No figure, verdict or state changes. The table of W9's items is the README's section W9;
adopted in the NEXT set with the cascade (`l9t5_connected.py` reads this page).
