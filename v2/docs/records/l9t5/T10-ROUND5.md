**ROUND 5 (T10, 5 October 2026), Slot C: DONE: V6-B3 corrected (CON-004 traced), T10-A1's row and the fabrics' share and fault handling drafted (FW-B20, FW-B21), SHDN drafted, composed, read and mutated, the credible bus faults re-solved, C-DEV's figure derived. NOT DONE: no independent check; the rows unapplied; Layer 5 has not accepted them; nothing physical. NEXT: the README lines of section 8 (Slot A applies them), then Parts 2 and 3 (records efuse, l8p, l4e11).**

# T10 round 5: the supervisors' regulators after the independent check V6 (L9T5-F06, F13, F16, F17)

Record l9t5, task T10, MESHSAT-1357, Slot C of the P0 power closure (owner's instruction of 5 October 2026, 14:20 CEST, and its
amendment 1 of 15:45). Branch `fnd/p0t10` from `fnd/p0base` `e132db0e`. Prototype design: nothing in this kit has been built,
bought, powered or measured, and no figure here is a measurement. Every figure is printed by `l9t5_t10.py` into `l9t5_t10.out`
("t10 N" is its section; round 5 is section 10). Labels: PRINTED (a maker's limit), TYPICAL, DECLARED, MODEL, ASSUMPTION, SESSION.
Case rows: C-DEV rev 1 (the supervisors) and C-PROT rev 1, cited, not changed.

## 1. What V6 found and what this round does

V6 (an AI review of candidate `7a82e82a`) read T10 CONFIRMED AS CONDITIONAL, not on T10-A1 alone, with V6-B3 blocking: round 4's
sentence placing the two fabric-fault states outside every requirement was wrong.

| V6 item | This round | Where |
|---|---|---|
| V6-B3 | CON-004 (constraint, core, BLOCKER; accepted when test A7 passes) covers both fault states through `ARCH-PCB-B-IOHA.md` section 12 rows 7 and 8; the sentence is replaced in `l9t5_t10.py`, its output and `L9T5-CASES.md` (rows f1, f2 and the findings line); A7 as written cuts a fabric and does not exercise the shorted-bus row | t10 8 (f1), (f2); t10 10a |
| item C, F13 | FW-B21's share: each supervisor's own TXD dominant at most 2 % of every 100 ms window per fabric, with FDCAN_CCCR.DAR = 1 so every transmission is a scheduled one | t10 10d |
| item C, T10-A1 | FW-B20 drafted; the reference manual is held (RM0433 Rev 8): the reset state (HSI 64 MHz, VOS3) is inside the bound, replacing round 4's assumption | t10 10b |
| V6-m10 | the enabled peripherals bounded from Table 39 (rev Y) and Table 137 (rev V); each figure states its air: 76.25 C (the case's mixed air, judged) and 81.89 C (exhaust, read) | t10 10c |
| item C, F16, F17 | every credible bus fault inside board B with its current and junction held, with the parts alone (the DTO) and with the response; the response drafted as firmware rows and a circuit change | t10 10e, 10f |
| V6-m9 | CON-017 (5) fits revision V or X; (4) refuses both fabrics on Y or W; rev Y's larger rows are kept as the cover for a rev X part (no rev X section in DS12110) | t10 10a |
| item C, case row | C-DEV's supervisor figure derived for the coordinator | t10 10g; section 6 here |

## 2. The four acceptance states (constitution section 2)

| Deliverable | Document acceptance | Supported design | Implementation | Physical qualification |
|---|---|---|---|---|
| T10 (L9T5-F06): K3, the pre-regulator, with FW-B20 | round 4's record and this round's; no independent check of round 4's correction or of this round | T10-A2 to A4 hold on the desk at 76.25 C on both revisions (122.9 C rev Y, 107.8 C rev V, MODEL); T10-A1 drafted | `apply_gen_sch_a_iocpre.py`, `apply_gen_sch_b_iocpre.py` composed and mutated (round 4); FW-B20 unapplied; no firmware exists | T10-A5, the supplier's validation task (section 5) |
| F13: FW-B21's share | this round | 122.9 C rev Y, 107.8 C rev V at 76.25 C against 125 C (MODEL); the transceivers' 20 mA declaration holds for any dominant current up to 828.5 mA at the share | FW-B21 unapplied; no firmware exists | V-B21 confirms the schedule |
| F16, F17: FW-B21's fault handling and the SHDN draft | this round | every credible single fault 123.5 C at worst (rev Y), both fabrics 124.1 C (rev Y), against 125 C and 150 C (MODEL) | `apply_gen_sch_b_canshdn.py` composed straight after T10's iocpre: SHDN DRAWN, the board before it FAIL, three mutations FAIL; FW-B21 unapplied | V-B21's fault injections confirm the firmware |

## 3. The credible bus faults, their figures and responses (t10 10e; each regulator at 76.25 C, MODEL)

Both fabrics lie wholly on board B (the parts on CANH_*/CANL_* are the six transceivers, the two split terminations, the four break
links and four test points; no connector). Board B carries no rail below 0 V, so the TCAN334's 180 mA bus-fault row (CANH at -12 V)
has no source in this kit; it is used only as the ASSUMED figure for the faults whose current TI does not print.

| Fault | What the bus does | I_f while its TXD is dominant | Held, rev Y | Parts alone (the DTO) | With the response, rev Y / rev V |
|---|---|---|---|---|---|
| B1 CANH to GND (SOIC-8 pins 7 and 8 adjacent, STB on GND) | every dominant bit reads recessive: errors, bus-off | 0.1800 A ASSUMED | 154.9 C FAILS | NOT BOUNDED (no row bounds the restart) | 123.3 C / 108.3 C |
| B2 CANH to CANL (pins 6 and 7) | as B1 | 0.1800 A ASSUMED | 154.9 C FAILS | NOT BOUNDED | 123.3 C / 108.3 C |
| B3 CANL to GND | the bus still works | 0.0809 A MODEL | 136.8 C FAILS | NOT BOUNDED | 123.0 C / 107.9 C |
| B4 CANH to a 3.3 V or 5 V net (own rail the worst) | the bus still works | 0.1160 A MODEL | 143.2 C FAILS | NOT BOUNDED | 123.5 C / 108.4 C |
| B5 CANL to a 3.3 V or 5 V net | errors, as B1 | 0.2000 A ASSUMED (IOS(DOM)) | 158.5 C FAILS | NOT BOUNDED | 123.4 C / 108.3 C |
| B6 an open (A7's cut) | an isolated node's frames go unacknowledged | 0.0550 A MODEL | 132.1 C FAILS | 130.5 C (automatic retransmission without end) | 122.9 C / 107.8 C |
| B7a TXD held low | the DTO frees the bus after 1.2 to 3.8 ms (PRINTED) | 0.0600 A PRINTED | 133.0 C FAILS | 123.6 C | 122.9 C / 107.8 C |
| B7b driver stuck on, DTO dead | the bus held dominant | 0.0600 A MODEL | 133.0 C FAILS | 133.0 C | 122.0 C / 107.0 C if SHDN acts; 133.0 C if not (L9T5-D5) |
| both fabrics faulted (row 8) | nothing moves (accepted) | the worst of the above on both | 194.1 C, over 150 C | NOT BOUNDED | 124.1 C / 109.0 C, inside 150 C and 125 C |

The response (t10 10f): FW-B21 (DAR = 1; the 2 % share per 100 ms; a fabric at error passive, bus-off or with no valid frame for
100 ms while a frame is pending is stopped and its transceiver put in shutdown; probed at most once a second for 100 ms; the other
fabric carries the quorum) and `apply_gen_sch_b_canshdn.py` (each TCAN334D's SHDN, on no net as drawn, to its controller's PD2 or
PB14 with 100 k to GND). The result does not rest on the unprinted fault currents: at the 2 % share a transceiver's average stays
under its 20 mA declaration for any dominant current up to 828.5 mA.

## 4. CORRECTED and OPEN

- **V6-B3: CORRECTED** (a record statement): the trace is read from `REQUIREMENTS-TRACE.md` and `ARCH-PCB-B-IOHA.md` by the script; the
  regression test fails on the old sentence.
- **L9T5-F13, F16, F17: DRAFTED CORRECTIONS, desk acceptance met by their author on the printed figures and the labelled models above;
  they stay OPEN in the register** until an independent check reads them and Layer 5 applies FW-B20 and FW-B21 (the integrator runs
  `apply_hw_fw_contract_t10.py`). The circuit half composes, reads DRAWN and fails under mutation; the firmware half is a contract
  row (no supervisor firmware exists, so nothing more can be composed at the desk).
- **L9T5-F06: STAYS OPEN** for the same check and application; T10-A5 is the supplier's (section 5).
- **Residual B7b (SESSION decision L9T5-D5, tolerated):** a transceiver whose driver, time-out and SHDN fail together holds its own
  regulator at 133.0 C on rev Y (117.9 C rev V): under the 150 C absolute maximum, over the 125 C criterion. Why: one part failing
  three of its own functions at once; its supervisor stays inside its absolute maximum and the quorum holds on the other fabric (row
  7). To reverse: a load switch on each transceiver's supply (six parts).
- **The exhaust air:** on rev V's rows the bounded state holds at 81.89 C (118.2 C); on rev Y's rows (the cover for a rev X part) the
  controller itself has no operating point there, and the bounded state holds only to 76.44 C local air. Which air the supervisors'
  pockets see is U-02's question (the inside air, the T-H1 mock-up), an existing Layer 4 external item; PROVISIONAL for a rev X part.

## 5. The supplier's validation tasks and the bounded provisional choices (amendment 1)

| Fact not established at the desk | Claim it supports | Bounded provisional choice | Supplier task: specimen, quantity, pass limit |
|---|---|---|---|
| a rev X controller's supply current (DS12110 prints rev Y and rev V only) | T10-A2 and F13 on a rev X part | rev Y's larger rows (122.9 C at 76.25 C) | first-article board B with the three fitted supervisors, revision read at goods-in (CON-017 (5)); each supervisor's supply current at the FW-B20 bound and FW-B21 share with its junction at 105 C or more: at most 0.2558 A at its regulator (V-B20) |
| the enabled peripherals' maxima (Tables 39 and 137 print typical only) | T10-A2 | typical times 144 MHz times the whole set's max/typ ratio (MODEL) | the same measurement (V-B20) |
| each LDO's thermal resistance on board B's copper (184 C/W printed without a heat sink) and its transient impedance (not printed) | T10-A2, F13's window | the printed 184 C/W; the junction never above the held figure | first-article board B in a 76 C chamber: each AP2112K's case temperature in the bounded state, so that the junction it implies is at most 125 C (T10-A5) |
| the TCAN334's supply current with a bus line at 0 V or on a rail (not printed) | B1, B2, B5 | the printed 180 mA and 200 mA rows; the share makes the result hold to 828.5 mA | V-B21: each fault injected with traffic running; each AP2112K's output current averaged over 1 s at or under the response figure |
| the firmware's implementation of FW-B20 and FW-B21 | every row above | the drafted rows | V-B20, V-B21 on the first firmware build |

## 6. For the coordinator: C-DEV's supervisor figure (t10 10g)

C-DEV rev 1 carries rv-pwr's HIGH, 0.400 A a controller plus 0.060 A of its other parts (0.46 A a regulator; +5V_IOC 1.3800 A). The
derived figure: the bounded controller with its enabled peripherals at its operating point at 76.25 C on rev Y's rows (the cover),
**0.2396 A** (TJ 111.8 C). Two ways to carry it:
- **for the thermal and the regulator rows (recommended):** 0.2558 A a regulator (rev Y; 0.1732 A rev V), with FW-B21's share and the
  circuit's own auxiliaries (0.0069 A at most, every resistor from the rail at the full rail, from the composed netlist);
- **in the budget's own form (power only, conservative):** 3 x (0.2396 + 0.060) x 3.3 = 2.966 W at +3V3_IOCx in place of 4.554 W;
  +5V_IOC 0.8989 A in place of 1.3800 A. Read as a regulator figure it gives 130.9 C, because the declared 0.060 A over-covers the
  auxiliaries; it is not the thermal figure.
Computed here as a LABELLED SCENARIO only; the row is the coordinator's to issue.

## 7. The README lines for Slot A to apply (the README is Slot A's)

- Lines 58 and 59, replace "a served fault state no requirement covers (**L9T5-F16 OPEN**, Layer 5's owner); both faulted, 176.3 C,
  over the 150 C absolute maximum, no requirement covers it (**L9T5-F17 OPEN**, Layer 5's owner)" with "a served fault state covered by
  CON-004 through IOHA row 7 (**L9T5-F16 OPEN**; round 5 drafts its response, `T10-ROUND5.md`); both faulted, 176.3 C held, over the
  150 C absolute maximum, covered by CON-004 through row 8 (**L9T5-F17 OPEN**; round 5)".
- Line 172, replace "the CAN fabric-fault rows, which no requirement covers, with the response each needs (t10 8)" with "the CAN
  fabric-fault rows, covered by CON-004, drafted as FW-B20 and FW-B21 with the SHDN draft (t10 10)".
- Rows C58 and C59, replace "no requirement covers this fault state (REQ-073 covers the other direction ...)" and "no requirement
  covers this fault state" with "covered by CON-004 (constraint, core, BLOCKER) through IOHA row 7 (C58) or row 8 (C59) and test A7".
  The test `test_l9t5` no longer requires the old phrase of C58 (V6-B3 is the basis).
- Line 1 (status): add "Round 5 (T10, Slot C): `T10-ROUND5.md`; F13, F16, F17 drafted corrections, OPEN pending the independent check".
- The composition order (`l9t5_drafts.py`, Slot A's): `apply_gen_sch_b_canshdn.py` after `apply_gen_sch_b_iocpre.py`, and a row for it in
  L4-E9's change list (L9T5-F20).

## 8. SESSION decisions of this round (under the owner's standing rule of 26 September 2026)

| Id | Decision | Why | To reverse |
|---|---|---|---|
| L9T5-D1 | the share bound 2 % of every 100 ms window per fabric | about 20 classic frames per 100 ms at 1 Mbit/s, many times a 2-of-3 heartbeat's need; keeps every fault response inside 125 C on rev Y's rows | a larger share with the junctions re-solved (`SHARE` in `l9t5_t10.py`) |
| L9T5-D2 | FDCAN_CCCR.DAR = 1 | makes every transmission a scheduled one, so the share holds whatever the fault (B6's endless retransmission removed) | automatic retransmission with a bounded retry count written into FW-B21 |
| L9T5-D3 | SHDN on PD2 (fabric A) and PB14 (fabric B), 100 k to GND | free GPIO next to each FDCAN's pins; the pull-down keeps today's normal mode in reset; TI does not want the internal bias relied on | drop `apply_gen_sch_b_canshdn.py`; FW-B21's stop then rests on INIT alone |
| L9T5-D4 | judged at 76.25 C; rev Y's rows as the cover for rev X; FDCAN's peripheral current counted twice; the circuit's own auxiliaries instead of the 0.020 A declaration | the case's air; no rev X rows printed; one clock enable serves both instances; the declaration is not a bound | read at the exhaust air (t10 10c prints it); rev V only (a procurement change, the owner's) |
| L9T5-D5 | the B7b residual tolerated | section 4 | a load switch per transceiver |

## 9. Findings for other authors

L9T5-F18 (board B's generator owner): SHDN on no net, answered by the draft. L9T5-F19 (board B's layout owner, Layer 10): +54V_POE,
POE_P and the PoE pairs MDI_A_P/N exceed the transceivers' 14 V bus pins; a clearance between them and the fabrics is a layout
means, not credited. L9T5-F20 (Layer 6 and L4-E9): PD2 and PB14 become outputs in `STM32H743-COMPATIBILITY.md`'s matrix; R67, R68,
R79, R80, R91, R92 need order codes; the draft needs a row in L4-E9's change list. L9T5-F12 (the coordinator): section 6.

## 10. Reproduce

From the repository root: `python3 v2/docs/records/l9t5/l9t5_t10.py` (about 15 s; it composes both boards and board B again with the
SHDN draft, in temporary directories). Tests: `env -C v2/ecad/tools python3 tests/run.py test_l9t5.`
