accepted: no

# Record l9stk: the independent checker's check 4, PROTECTION: NOT CONFIRMED (filed as received)

MESHSAT-1357. An AI review by a fresh Claude session that authored none of the record (an independent checker, not a qualified engineering review, not an Astra check), read-only in a disposable scratch clone at `d449375b07bfbb6560f0d5396f6d2898e768cc2c` (branch `fnd/l9stk`). Time: 4 October 2026, 04:12 to 04:18 CEST. Nothing in the kit has been built, bought or measured.

Scope, from the coordinator's brief: the targeted recheck of section 15.4b (the owner's reviewer's retry question on the d834e6a7 package: the LM5069-2's repeated fault and restart waveform and its accumulated heating over the breaker FETs and every protected series part; the latch-off -1 selected), the updated table and defect lists, `l9stk_protection.py` and its output.

Filed by the integrator of set 29 from the checker's final message for the round, without edits to its content. The record's author answered it in the next round (`L9-STACKUPS.md` sections 14 and 15 name each revision); this note is the checker's own record of what it read and found.

## The checker's report, as received

**PROTECTION: NOT CONFIRMED**

The retry arithmetic reproduces, and rejecting the -2 is right. The -1 is the right selection but does not yet meet the owner's criterion in two places: the breaker FET restarting hot, and charging through a latched breaker.

In a scratch clone at d449375b (SLVA673A fetched; the LM5069 sheet is already in the tree), `test_l9stk` gave 40 passed, 0 failed, 0 skipped. The tree is unchanged and the clone is deleted.

**What reproduces at the sheet (sections 5 and 8.4.3)**
- **One retry cycle:**
  - on 1.075 to 1.227 ms (the fault time from 0.3 V plus the 0.394 ms gate pulldown);
  - off 50.7 to 62.0 ms (seven 1.25 V to 4 V cycles, then the fall to 0.3 V);
  - per cycle 5.14 A²s, 55.6 A² average, 7.46 A RMS, which is 0.097 of the heating at the held 23.93 A.
- **The per-part table:** all within except Q1's body diode under BAT-F20 (3.79 W, 266 °C, DD-5).
- **Hard short on the -2:** 43.4 mJ per cycle, 0.84 W, case 118.1 °C, 0.79 of the derated SOA.
- **Resistive fault of 0.915 Ω on VSYS on the -2:** about 130 mJ in a 5.6 ms ramp plus the limited phase, 174 mJ per cycle, 3.03 W, case 228 °C.
- **The -1's latch:** the timer falls to 0.3 V within 34.0 ms (11 nF × 3.86 V / 1.25 µA), well inside the 0.110 s RC hold.
- **The -1's first event:** 0.57 for an overload; 0.54 for a cold start into the worst resistive fault.

The -2 fails the criterion on the 228 °C case alone. Board P cannot provide the 24.3 °C/W that would bring it under 150 °C. CONOPS 4e and POWER-THERMAL 9.3 both say what the record quotes.

**Blockers**

**B-R1. A hot restart of the -1 exceeds the margin the record used to reject the -2.**
- The record rejects the -2's hard short at 0.79 against TI's 0.67, yet accepts the -1's start into the 0.915 Ω fault at 0.85 hot (0.95 with the 10 % reading allowance) and sends it to E-3 as a test.
- My arithmetic: 180 mJ is an equivalent 4.46 ms at 40.32 W; the SOA at 16.8 V is 125.4 W at 25 °C.
  - case 76.25 °C: 0.545
  - case 90.0 °C: 0.670
  - case 101.0 °C (the held state): 0.820
  - case 103.0 °C: 0.855
- The record's own design makes hot restarts credible:
  - **The thermal guard's cycle.** A held fault on VSYS just under the limit leaves the breaker FET's case near 101 °C. The guard trips, cools in seconds, and closes the loop while the case is still hot (time constant on the order of minutes). The restart then meets the power limit and latches at about 0.82 to 0.85.
  - **DD-7's automatic pulse**, within 0.633 s of an input returning.
  - **A quick redock.**
- **Correction:** keep restarts below about 90 °C case (83 °C with the reading allowance). One way is a thermal sense on the breaker pad in the enable loop, like the battery FETs' guard. The other is to state one SOA criterion and apply it to both variants.

**B-R2. DD-7's fix covers only the first restart.**
- Board A's pulse fires when an input appears. If the fault on VSYS persists, the restart meets the power limit and latches again within milliseconds. The input is still there and no second pulse comes.
- From then on, only IF-7 (firmware) stands between a commanded charge and the latched FET's body diode. That breaks the firmware-independence the criterion requires.
- **Counterexample:** a 4 A charge × up to 1 V is 4 W, which settles at 76.25 + 4 × 50 = 276 °C. At 8 A it is 476 °C. Destroying the breaker FET silently removes W4DP-F2's element.
- E-14's acceptance ("until the input-return reset restarts it, 0.633 s at most") does not cover a second latch.
- **Correction:** a hardware bound on charging while the terminal is dead or the breaker is latched, for example a hardware charge inhibit taken from the enable loop and the pack terminal's state. Extend E-14 to a second latch with the input still present.
- **Owners:** board A's generator with L4-E11; the firmware owner for IF-7.

**Minors**
- **IF-1 is now critical to the service.** Under the -1, a start that meets the power limit (board A's loads not held off) latches the breaker, so the kit stays dark until a redock or an input. The record still describes it as a retry.
- **The guard's "trips and restarts at the PTC's rate indefinitely"** holds only for loads that IF-1 holds off. A resistive fault on VSYS latches the -1 at the first restart (the B-R1 event).
- **The <0.3 V restart condition** does not say which UVLO edge it is judged at. If it is the falling edge, a pulse within 34 ms of a latch does not restart the breaker. That fails safe, but should be stated.
- **The retry duty** pairs the fault-detection current's slowest value (on) with its fastest (off cycles). One unit has a single source, so this is conservative, not wrong.
- **Outside this scope, from 2c8b29fb:** the RC hold's 3.3 µF now delays the undock turn-off to 1.51 ms. That lowers the safe withdrawal speed from 2.53 to 0.66 m/s, which a hand can exceed, so the dock contacts may break load current. This belongs to Layer 7 or the hold's circuit (a discharge path that bypasses C_U).

**Questions as asked**
- **Retry timing, envelope and per-part table:** confirmed.
- **The -2's failure:** confirmed.
- **The -1 against the criterion:**
  - service: met;
  - every series part, one event per fault: met;
  - tolerances and delays: met;
  - firmware independence: not met (B-R2);
  - the protector's own SOA under TI's margin: not met on hot restart (B-R1).
- **Recovery by redock or input:** bounded for the first restart; not bounded after a second latch (B-R2).
- **DD-7:** owners right; statement incomplete (B-R2).

**Smallest next action.** One revision of 15.4b and DD-7, then a targeted recheck:
1. Hold restarts below the case temperature that keeps the worst resistive start within 0.67 (about 90 °C), or restate one SOA criterion for both variants.
2. Add a hardware bound on charging through a latched breaker, and extend E-14 to a second latch with the input still present.
3. Fold in the minors.

**Owner decision.** Nothing new. L9STK CU (the copper weight, money) is still his. Q-TI-L9S-1 and Q-TI-17 still need sending to TI (an outside contact), by him or through the supplier.
