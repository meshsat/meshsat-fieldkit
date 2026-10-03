# TP-SOLAR: the solar input guard and the LT8705A's input sense (R-176 rows 1 to 6, R-189, R-174)

<!-- tp
id: TP-SOLAR
title: The solar input guard and the LT8705A's input sense (R-176 rows 1 to 6, R-189, R-174)
register: R-176, R-189, R-174
e11: none
route5d: The solar guard's bench (R-176 rows 1 to 6; R-174 at layer 8) ;; B6-ENG-2's bench (R-189; D-16)
-->

**Status: PROPOSED, for the supplier to review and agree before execution.** MESHSAT-1357, 3 October 2026. Prototype design:
nothing here has been built, bought, powered or measured. Common rules: `v2/docs/test-procedures/README.md`.

> **Read this first. The drafted network is known to FAIL this procedure's step row at a fault at the connector.** On the desk model,
> with a stiff 36 V source arriving while the guard is on, the LT8705A U5's current-sense pins reach -0.3021 V, past their -0.3 V
> absolute maximum, and no source loop was found that passes (L4-E7 rounds 2 to 5, quoted in section 1). That is a known design
> defect (supplier handover row P1, task P1-1), not missing bench evidence. **This procedure measures the supplier's corrected
> network**, the output of phase 1's task P1-1, against the same envelope and the same lines. Section 6 says how to treat the
> drafted network if it is ever stepped to check the model.

## 1. Purpose and the decision it settles

Board E's solar input carries a cut-off and reverse guard (U21 TPS48110-Q1 with Q12, Q13, D11, the port bank, D4) ahead of the
LT8705A tracker U5, whose input current is sensed across RSENSE1. Three register rows specify the bench:

- **R-176** (rows 1 to 6): the guard's cut-off thresholds, the cold connection of a stiff 36 V source, the guard-on step with the
  waveforms at U5's pins, a reversed panel, Q13's leakage hot, and no false short-circuit trip; it settles **D-10** (the cut-off and
  the cold connection at both fault positions, and the guard-on case) and **D-11** (Q13's leakage).
- **R-189** (B6-ENG-2): the sense in normal operation at the 25 V corner; it settles **D-16**.
- **R-174**: MIL-STD-461G CS116 and CS115 on the solar input, at a laboratory; R-176 row 6 runs under it.

The record's statement of the defect and of what the engineer must decide:

<!-- q src="v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md" row="Evidence and failed condition" col="Entry" -->
> no passing loop is claimed. At round 2's 3.30 uH the pins' complete budget (the resistive peak, RSENSE1's inductance at the
> WSL's printed bound 5 nH, the Kelvin pair's 1 nH, the numerical error) reads -0.3021 to +0.2591 V at a fault at the connector
> (no lead resistance credited) and -0.2884 to +0.2486 V at the lead's far end, against +-0.240 V: outside the line in both
> polarities, inside the +-0.3 V absolute maximum only on the positive side. At 1.00 uH U5's resistive peak alone reads 0.5858 V,
> over the absolute maximum, because any guard that is closed when a stiff source arrives charges the stage's capacitance at a
> rate only the loop sets; the source's own resistance is bounded by no document. INP reads 18.29 V there at a fault at the
> connector, over its 18 V margin line (inside the 20 V absolute maximum; the margin holds from 3.58 uH). PV_F 83.47 V at that
> loop exceeds the TPS4811-Q1's recommended operating VS row of 80 V (OPEN, round 4: under the row from 4.03 uH; the 90 V line
> above it is the exclusion line only)
<!-- /q -->

<!-- q src="v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md" row="Decision or measurement needed" col="Entry" -->
> the stage's current-sense arrangement itself (where the input current is sensed and with what; B6-ENG-2's stage-level note),
> with RSENSE1's inductance (unprinted for the chosen part; 5 nH taken) and the source's loop and resistance bounded by the kit's
> rules and measured before any step is applied; a sense-pin filter only if Analog Devices permits it with a bounded error
> (clarification item 6)
<!-- /q -->

<!-- q src="v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md" row="Pass criterion" col="Entry" -->
> U5's differential within +-0.240 V at the IC pins for the declared envelope, both fault positions, captured at layer 9 with the
> guard on and a 36 V supply stepped on from about 7.5 V and from 25 V
<!-- /q -->

and of the sense in operation:

<!-- q src="v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md" row="Evidence and failed condition" col="Entry (B6-ENG-2)" -->
> the periodic model above against 8705af p.5 (the +-100 mV operating range) and p.31: at 25 V in and a 12.0 V bus the resistive
> peak across RSENSE1 is 0.1174 V at the regulation's highest current, the pins -0.1866 to +0.1863 V with RSENSE1's 5 nH; the
> monitor's average +7.9 % (MODELED; positive: high)
<!-- /q -->

<!-- q src="v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md" row="Pass criterion" col="Entry (B6-ENG-2)" -->
> the pins within +-100 mV at every operating point, or the regulated input current measured within check (a)'s error budget at
> the 25 V corner
<!-- /q -->

The corrected design's acceptance, as the supplier task list states it (the same lines this procedure measures):

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="P1-1" col="Acceptance" -->
> a stiff 36 V source arriving with the guard on over the declared 0.30 to 10.20 uH, at both fault positions (the connector with
> no lead resistance credited, the lead's far end): U5's CSPIN to CSNIN inside its +-0.3 V absolute maximum and the +-0.240 V
> design target, INP inside its 18 V margin line, PV_F under the TPS4811-Q1's recommended 80 V row, the cold connection's slew and
> INP inside their margin lines (R-176 rows 2 and 3); in operation at the 25 V corner the sense pins within +-100 mV or the
> regulated input current within check (a)'s error budget (R-189); the 100 W backstop bound kept (R-21, R-98)
<!-- /q -->

## 2. The specimen and what transfers

The guard's bench:

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="The solar guard's bench (R-176 rows 1 to 6; R-174 at layer 8)" col="Specimen" -->
> the controlled first prototype of board E with the drafted guard applied (U21, Q12, Q13, D11, the port bank, C133, C134, C71 to
> C74, D4, the bulk, the sense bank and U5's input), or a coupon of that solar entry on the intended stack-up; a stiff 36 V supply
> stepped on through a loop measured first, and a ramped supply
<!-- /q -->

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="The solar guard's bench (R-176 rows 1 to 6; R-174 at layer 8)" col="What transfers to the final board" -->
> the cut-off's thresholds and Q13's leakage (device properties) fully; the guard-on and cold-connection waveforms only for the
> measured source loop and fault position, and only where the specimen's input-loop inductance and RSENSE1's fitted part are the
> final layout's
<!-- /q -->

The sense in operation:

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="B6-ENG-2's bench (R-189; D-16)" col="Specimen" -->
> the controlled first prototype of board E's solar stage, or the guard bench's coupon with U5's input sense (RSENSE1, CSPIN,
> CSNIN, C13 to C15 behind it, C71 to C74 ahead), delivering from 25 V in into a 12.0 V bus at the regulation's highest current
> and at the trip's
<!-- /q -->

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="B6-ENG-2's bench (R-189; D-16)" col="What transfers to the final board" -->
> only where the specimen's input ceramics, RSENSE1 (its inductance) and the Kelvin taps are the final layout's; the amplifier's
> reading above 100 mV is Analog Devices' to state (item 7)
<!-- /q -->

**Consequences for this procedure.** The thresholds and Q13's leakage are device properties and transfer fully. The step and cold
connection waveforms transfer only for the source loop measured and the fault position tested, and only where the specimen's
input-loop inductance and RSENSE1's fitted part are the final layout's; a coupon is therefore built on the intended stack-up with
the final placement of the solar entry, or the controlled first prototype of board E is used. The LT8705A demonstration board does
not transfer (it has another sense arrangement; L4-E7, quoted in section 6). L4-E11's 17d has no block for these rows; the
transfer rule is 5d's.

The envelope the model was run over, which the bench reproduces (the source, its loop, both fault positions):

<!-- q src="v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md" -->
> **The envelope and the model** (MODELED, `guard_event_b`: round 1's nodes, parts and U21's latest commands, every ceramic bank
> its curves at its own voltage, the chord capacitance iterated in each step):
>
> - a stiff 36 V source, no source impedance credited;
>
> - its loop from 0.30 to 10.20 uH (38 values 10 % apart; round 2's bisected floor is WITHDRAWN in round 5), whether the fault
> sits at the connector (the loop is the source's own and NO lead resistance is credited: a connector fault has no lead in series,
> and no document bounds the source's own resistance) or at the lead's far end (the lead and its resistance added);
>
> - the lead's resistance at the cold end, 0.0363 Ohm (0.0465 Ohm at a1solar's 40 C), for the far-end fault only;
>
> - every start the guard is on in, the three bulk corners, D11 at both ends.
<!-- /q -->

## 3. Safety

- **Stored energy and voltage.** The stiff 36 V source is a charged low-impedance capacitor bank switched onto the port. The cold
  connection rings PV_F up to about 85 V (the row's line): above the 60 V DC usually treated as touch-safe, so the specimen runs in an
  insulated enclosure, probes are rated for it, and nothing is touched while the bank is charged. The bank has a bleed resistor, a
  charge indicator and an interlock.
- **Current.** The guard turns off some tens of amperes within 12 us (row 3; the model reads 62.7 A at 3.30 uH); the switch, the leads
  and the inductors are rated for it.
- **Reversed source** (row 4): a bench panel or a curve-emulating supply connected reversed; its own current limited.
- **The LT8705A U5** may be damaged if its sense pins pass +-0.3 V: a U5 that has seen a reading past +-0.3 V is replaced and not
  trusted afterwards (proposal).
- **CS116 and CS115** run at a MIL-STD-461 laboratory under its own safety rules.

## 4. Equipment, and the accuracy each measurement needs

| Item | Class | Accuracy and capability needed |
|---|---|---|
| Stiff 36 V step source | a low-ESR capacitor bank charged to 36 V and a fast semiconductor switch | stiff (its own resistance and inductance measured and included in the loop); the switch's closing edge recorded |
| Loop inductors | air-core inductors on a low-inductance fixture | to set the loop over 0.30 to 10.20 uH (the envelope); each loop measured, switch to port and back, before any step (an LCR meter at 100 kHz, or a ring-down against a known capacitor; proposal), within 5 % (proposal) |
| The solar lead (far-end fault position) | the kit's lead as Layer 7 specifies it, or a lead of the same resistance and geometry | 0.0363 Ohm at the cold end (the envelope), its resistance read four-wire |
| Ramped supply | a programmable DC supply with a slow ramp | 25 to 32 V (row 1); the thresholds read within 0.05 V (proposal: about a fiftieth of the 2.51 V rising band) |
| Differential probe at U5's CSPIN and CSNIN | a high-voltage-rated differential probe at the IC pins, at least 200 MHz (L4-E7) | the pins' differential within 0.010 V at the step (proposal: a sixth of the 0.060 V between the 0.240 V target and the 0.3 V maximum); common-mode rejection at least 70 dB to 10 MHz (proposal: the common mode steps by about 28.5 V, from 7.46 V to 36 V, so 70 dB leaves under 0.01 V); two single-ended probes subtracted are not acceptable |
| Probes at PV_F, PV_P, INP, TRK_VS | passive or differential probes, 200 MHz | PV_F against 80 V and 85 V within 1 V (proposal); INP against 18 V and 20 V within 0.2 V (proposal); PV_P against 31.80 V within 0.2 V (proposal) |
| Current probes | wide-band current probes on Q12's path and on D4's lead | Q12's turn-off current within 2 % (proposal; its line is being resolved, section 8); D4's current resolved to show "carries nothing" (proposal: a 1 A per division range with a 10 mA noise floor, its zero checked before each run) |
| Oscilloscope | 8 synchronised channels, 12-bit, 1 GS/s or faster (proposal) | PV_F's slew against 54 and 60 V/us; Q12's 12 us turn-off window |
| Leakage measurement (row 5) | a source-measure unit | Q13's leakage at 25 V against 32.1 uA within 1 uA (proposal) |
| Bench panel curve | a solar array simulator (an I-V curve-emulating supply) | 25 V open circuit and the panel's curve (R-189: 25 V in at the regulation's highest current and at the trip's) |
| Bus load | a battery simulator or an electronic load holding 12.0 V | the bus at its lowest (R-189) |
| DC current through the stage's input | a calibrated shunt and a meter | the regulated input current within 0.5 % (proposal) |
| Impedance analyser | a vector impedance analyser with an SMD fixture | RSENSE1's inductance on the fitted part within 0.5 nH (proposal: a tenth of the 5 nH the budget takes) |
| Climatic chamber | a temperature chamber | -20 to +62.1 C (the range the record bounds the stage's parts over) |

## 5. Setup and measurement points

1. **The specimen** of section 2 with the supplier's corrected network (P1-1) fitted; a record of every part's code and lot, and the
   ceramic banks' measured capacitance at 0 V and at their working bias (the model bounds each bank separately; the bench records
   where the fitted parts sit).
2. **Measurement points:** U5's CSPIN and CSNIN at the IC pins (the differential probe's tips soldered short); PV_F (the port); PV_P;
   TRK_VS; U21's INP and EN/UVLO; Q12's current; D4's current; Q12's gate (information); SWEN (row 6 and R-189).
3. **Fault positions:** (i) at the connector: the step source and its loop connected directly to J_SOLAR, no lead; (ii) at the lead's
   far end: the step source at the far end of the solar lead.

## 6. Steps

**The drafted network.** It is not the specimen. If the supplier steps it to check the desk model before the correction, it starts at
the largest loop (10.20 uH) and steps down, stops before the loop at which the model reads the pins past +-0.3 V (L4-E7: 1.00 uH reads
0.5858 V resistive, and 3.30 uH reads -0.3021 V at the connector), and replaces U5 after any reading past +-0.3 V (proposal). Its
readings are model checks, never a verdict on R-176.

**Part A, R-176 rows 1 to 6, on the corrected network,** at 25 C, and rows 1, 3 and 5 also at -20 C and +62.1 C (proposal):

1. **Row 1, the cut-off.** Ramp the supply from 25 V to 32 V and back (proposal: 0.1 V/s); record the port voltage at which U21 turns
   Q12 off rising and back on falling. Five ramps (proposal).
2. **Row 2, the cold connection.** The guard off (no prior input). At each loop of the set below and at both fault positions, step the
   36 V source onto the port: capture PV_F (peak and slew), INP, EN/UVLO, Q12's and D4's currents.
3. **Row 3, the step with the guard on.** Bring the port to about 7.5 V, then to 25 V (the two start states); at each, step the 36 V
   source on through the loop: capture U5's differential, Q12's current and turn-off time, D4's current, PV_P, PV_F and INP. Both fault
   positions. Before the first step at each loop, the probe check: both differential tips on CSNIN, one step, the reading recorded as the
   common-mode error (proposal).
4. **The loop set** for rows 2 and 3 (proposal): 0.30, 0.53, 1.00, 1.52, 2.44, 3.30, 3.58, 4.03 and 10.20 uH (the loops the record names),
   plus the corrected network's own worst-case loop from the supplier's analysis. Three steps at each point (proposal).
5. **Row 4, reversed panel.** The bench panel curve connected reversed: record the port current and the high side's pins against GND.
6. **Row 5, Q13's leakage** with 25 V across it at the hot end of the stage's range; that temperature is TBD (owed by R-176): the
   temperature "the hot end" denotes for Q13's leakage row, with +62.1 C proposed until it is stated.
7. **Row 6, no false trip.** The stage running from the bench panel curve at the regulation's highest current with C126 at 330 pF:
   SWEN and the short-circuit trip's state over 10 minutes (proposal); the same under CS116 at the laboratory (R-174).

**Part B, R-189, the sense in operation** (board E's first prototype; L4-E7 says why the demonstration board does not serve):

<!-- q src="v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md" -->
> - **B6 round 3, the sense in operation and RSENSE1's inductance** (B6-ENG-2 and B6-ENG-1's added item; board E's first
> prototype, since the LT8705A demonstration board has another sense arrangement and does not transfer):
>
> - the waveform at U5's CSPIN and CSNIN (a differential probe at the pins, at least 200 MHz) with the stage regulating at 25 V in
> and the bus at its lowest, and at the hold: the peaks against +-100 mV, the average against the setting (the model: 0.1174 V
> resistive peak and -0.1866 to +0.1863 V at the pins at 25 V in and a 12.0 V bus, the monitor's average +7.9 %, MODELED);
>
> - RSENSE1's inductance on the fitted part (an impedance analyser or the step response at the pads), against the 5 nH the budget
> takes (no bound is claimed).
<!-- /q -->

8. **The pins in operation.** 25 V in from the bench panel curve, the bus held at 12.0 V; the stage regulating at its setting
   (RIMON_IN 31.6k, 2.5485 A nominal); capture CSPIN to CSNIN at the pins over at least 100 switching periods (proposal): the peaks and
   the average. To read at the regulation's highest current (2.9337 A) and at the trip's (3.7408 A) the specimen's settings are changed
   for the reading only (RIMON_IN, and the backstop's trip raised so it does not act), each change recorded (proposal).
9. **The regulated current.** At the same point, the stage's DC input current against its setting.
10. **RSENSE1's inductance** on the fitted part, by the impedance analyser (or the step response at its pads).

**Part C, R-174, at a MIL-STD-461 laboratory:** CS116 on PV_IN alone and on the J_SOLAR cable at the frequencies the row names, and
CS115 on the cable, with the guard both on and off, recording the cable's peak current, D4's clamp at each disturbance's current, and
U5's sense differential; row 6's no-trip check runs during CS116.

## 7. Data to record

| Row | Ambient (C) | Fault position | Loop (uH, measured) | Start (V) | U5 differential, least and greatest (V), and U | PV_F peak (V) | PV_F slew (V/us) | INP peak (V) | Q12 peak (A), off time (us) | D4 current | PV_P peak (V) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 25 | connector | 0.30 | 7.5 | | | | | | | | |

| Row 1 | Ambient (C) | Rising threshold (V) and U | Falling threshold (V) and U | Verdict |
|---|---|---|---|---|
| ramp 1 | 25 | | | |

| R-189 point | Input current (A) | Pins' peaks (V) and U | Pins' average (V) | Regulated current vs setting (%) | RSENSE1 inductance (nH) | Verdict |
|---|---|---|---|---|---|---|
| regulation's highest | | | | | | |

## 8. Pass, fail and inconclusive

The register's acceptances, quoted:

<!-- q src="v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md" row="R-176" col="Acceptance" -->
> Each of the six rows filed against its bound, both fault positions (the connector with no lead resistance credited, the lead's
> far end); row 2 inside the absolute ratings, its 10 % margin lines not held at a connector fault near the envelope's least loop,
> 0.30 uH (round 5: PV_F's slew 56.1 V/us against 54 and INP 18.54 V against 18, inside 60 V/us and 20 V; the lines hold from 0.53
> uH); row 3 (U5 within +-0.240 V at the IC pins, captured at layer 9): no loop is claimed to pass (round 5: round 2's 3.30 uH
> WITHDRAWN as a passing floor; at that reference loop the pins' complete budget reads -0.3021 to +0.2591 V at a connector fault,
> past the -0.3 V absolute maximum, and -0.2884 to +0.2486 V at the far end; no inductance tried brings both polarities inside,
> round 4's 3.0 nH bound withdrawn; PV_F 83.47 V over the TPS4811-Q1's recommended operating 80 V row, OPEN, under it from 4.03
> uH): the engineer's B6-ENG-1 decides; until the rows pass D-10's guard-on case stays OPEN and D-11 (Q13's leakage, row 5)
> CONDITIONAL
<!-- /q -->

<!-- q src="v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md" row="R-189" col="Acceptance" -->
> The pins within +-100 mV at every operating point, or the regulated input current measured within check (a)'s error budget at
> the 25 V corner; else Analog Devices' statement of what the amplifier reads above 100 mV (item 7), enough low-derating
> capacitance behind RSENSE1 (which worsens the guard-on transient, B6, and is re-run against R-176 row 3), or the engineer's
> rearrangement (then R-187's draft); a failure costs the input limit regulating off its setting at high input and a low bus (this
> model, rectified in round 5: below it, the error +7.9 % at the regulation's highest current and -10.2 % at the trip's, MODELED
> on an amplifier model the sheet does not print) and a possible stress on the sense pins at the switching edges (-0.4329 V at 10
> ns edges, beyond the -0.3 V absolute maximum); round 3's 'no damage' and '5.7 % low' withdrawn (L4-E7's round 5)
<!-- /q -->

<!-- q src="v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md" row="R-174" col="Acceptance" -->
> D4's clamp at each disturbance's recorded current at or under the lowest limit on PV_P (REQ-016's criterion: 50 V on the drafted
> entry); CS115's recorded loop current under 15.7 A, or U5's sense differential measured under its 0.3 V; with the guard (R-173)
> both on and off
<!-- /q -->

The six rows of R-176 as L4-E7 restates them:

<!-- q src="v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md" -->
> - **R-176's acceptance, revised again** (round 2):
>
> 1. the cut-off's rise and fall on a ramped supply: 28.55 to 31.06 V rising, 27.07 V or more falling;
>
> 2. a 36 V supply connected cold: Q12 never conducts, D4 carries nothing, PV_F at most 85 V, its slew and INP inside their
> absolute ratings (their 10 % margin lines are not held at a connector fault near the envelope's least loop, round 5);
>
> 3. at layer 9, the waveforms at the IC pins: a 36 V supply stepped onto the port with the guard on, from about 7.5 V and from 25
> V, through a loop measured first. U5's CSPIN to CSNIN within +-0.240 V, U21 turning Q12 off (at most 61 A, within 12 us), D4
> carrying nothing, PV_P under 31.80 V, PV_F under the TPS4811-Q1's recommended operating 80 V row (OPEN at round 2's loop: 83.47
> V, under the row from 4.03 uH; round 4, L6P-F10). No loop is claimed to pass (round 5): at 3.30 uH the pins' complete budget is
> outside +-0.240 V and B6-ENG-1 decides;
>
> 4. a reversed bench panel's curve: no current, the high side's pins against GND;
>
> 5. Q13's leakage at the hot end, under 32.1 uA;
>
> 6. no short-circuit trip with C126 at 330 pF in operation and under CS116 (R-174).
<!-- /q -->

The lines, with U taken as README section 3 states, for the corrected network at every loop of the set and both fault positions:

- **Row 1:** PASS when the rising threshold less U is at least 28.55 V and plus U at most 31.06 V, and the falling threshold less U is
  at least 27.07 V.
- **Row 2:** PASS (R-176) when Q12 never conducts, D4 carries nothing, PV_F's peak plus U is at most 85 V, its slew plus U at most
  60 V/us and INP plus U at most 20 V (the absolute ratings). For the corrected network, P1-1's acceptance (section 1) also asks for the
  10 % margin lines: PASS (P1-1) when the slew plus U is at most 54 V/us and INP plus U at most 18 V. The drafted network does not hold
  them at a connector fault near 0.30 uH (round 5, quoted in R-176's acceptance).
- **Row 3:** PASS when U5's differential with U stays inside +-0.240 V (and so inside the +-0.3 V absolute maximum), Q12 turns off
  within 12 us, D4 carries nothing, PV_P plus U is under 31.80 V, PV_F plus U is under 80 V, and INP plus U is under 18 V (P1-1).
  **Q12's turn-off current is RECORDED and not yet judged:** R-176's register text and L4-E7's prototype section state "at most
  63 A", while L4-E7's own revised list (quoted above) states 61 A in its item 3. L4-E7's author is resolving the figure; this folder
  chooses neither, and the current line's verdict waits for that resolution (no figure is changed here).
- **Row 4:** PASS when no current flows and the high side's pins stay within 1 V of GND (L4-E7's prototype measurements).
- **Row 5:** PASS when Q13's leakage plus U is under 32.1 uA at the hot end.
- **Row 6:** PASS when no short-circuit trip occurs in operation and under CS116.
- **R-189:** PASS when the pins' peaks with U stay within +-100 mV at every operating point; or, if not, when the regulated input
  current is within check (a)'s error budget at the 25 V corner. Its upper side is the regulation's highest, 2.9337 A (L4-E7); its
  lower side is TBD (owed by R-189): the least regulated input current that check (a)'s error budget accepts at the 25 V corner.
  RSENSE1's inductance is RECORDED against the 5 nH the budget takes (no bound is claimed).
- **R-174:** PASS as its acceptance states (D4's clamp at each recorded current at or under 50 V on PV_P; CS115's loop current under
  15.7 A, or U5's differential under 0.3 V), with the guard on and off.
- **INCONCLUSIVE:** a loop not measured before its step; the probe's common-mode check over 0.010 V (proposal); a clipped channel; the
  specimen's input-loop inductance or RSENSE1's part not the final layout's (the waveform rows then do not transfer, and are repeated
  on the first prototype).

## 9. The uncertainty budget

| Term | Source | Value |
|---|---|---|
| U5's differential | the differential probe's gain and offset, its common-mode error (the tip-shorted check), the scope's channel | 0.010 V at the step (proposal) |
| Loop inductance | the LCR meter or ring-down | 5 % (proposal) |
| Thresholds (row 1) | the supply's readback checked by a meter | 0.05 V (proposal) |
| PV_F, INP, PV_P peaks | probes and channels | 1 V, 0.2 V, 0.2 V (proposal) |
| Q12 current | the current probe | 2 % (proposal) |
| Q13 leakage | the source-measure unit and the fixture's own leakage | 1 uA (proposal) |
| Regulated current | the shunt and meter | 0.5 % (proposal) |
| RSENSE1 inductance | the impedance analyser and its fixture compensation | 0.5 nH (proposal) |
| Ambient | the chamber | its stated uniformity |

## 10. Consequence of a fail, and the re-test triggers

- **Row 3 or row 2 failed on the corrected network:** U5's sense pins over their absolute maximum is a possible loss of the solar stage
  (B6-ENG-1's consequence, quoted below); the correction returns to phase 1, and D-10's guard-on case stays OPEN.

<!-- q src="v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md" row="Consequence of failure" col="Entry" -->
> U5's sense pins over their absolute maximum; the LT8705A possibly damaged and the solar stage lost (the 100 W bound and the
> backstop rest on it)
<!-- /q -->

- **R-189 failed:** B6-ENG-2's consequence, quoted below; the engineer's rearrangement of the sense (R-187's draft) or Analog Devices'
  statement (item 7) follows.

<!-- q src="v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md" row="Consequence of failure" col="Entry (B6-ENG-2)" -->
> the input limit regulating off its setting at high input and a low bus (this model: below it, by the figure above), and a
> possible stress on the sense pins at the switching edges: the sensitivity at 10 ns edges reaches -0.4329 V at the pins, beyond
> the -0.3 V absolute maximum (round 3's unconditional "no damage" is withdrawn); the 100 W bound rests on the backstop
<!-- /q -->

- **Row 5 failed:** D-11 stays CONDITIONAL on Q13's leakage (L4-E7's D5 row: Q13 "leaks under 32.1 uA (the dividers' conductance)").
- **Re-test triggers** (proposal, from 5d's transfer cell): a change of the input-loop inductance or RSENSE1's fitted part from the
  specimen's; any change of the guard network, the port bank, the sense bank or U5's input; a solar lead of another resistance or
  geometry; the corrected network's own analysis moving its worst loop.

## 11. Authorisation and purchases (nothing has been bought)

The guard's bench:

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="The solar guard's bench (R-176 rows 1 to 6; R-174 at layer 8)" col="Authorisation" -->
> the owner's: the parts and the prototype; Analog Devices' question 6
<!-- /q -->

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="The solar guard's bench (R-176 rows 1 to 6; R-174 at layer 8)" col="What to buy" -->
> price not read: TPS48110AQDGXRQ1 (U21; LCSC C17556513, stock 326 on 2 October 2026, price not filed), CSD19532Q5B (Q12, Q13;
> LCSC C473333), the Samsung CL32B225KCJSNNE and CL32B106KBJNNNE and the SMCJ30A (codes owed); the controlled first prototype of
> board E
<!-- /q -->

The sense in operation:

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="B6-ENG-2's bench (R-189; D-16)" col="Authorisation" -->
> the owner's: the prototype; Analog Devices' item 7
<!-- /q -->

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="B6-ENG-2's bench (R-189; D-16)" col="What to buy" -->
> price not read: TPS48110AQDGXRQ1 (U21; LCSC C17556513, stock 326 on 2 October 2026, price not filed), CSD19532Q5B (Q12, Q13;
> LCSC C473333), the Samsung CL32B225KCJSNNE and CL32B106KBJNNNE and the SMCJ30A (codes owed); the controlled first prototype of
> board E
<!-- /q -->

What to send (5d): Analog Devices' question 6 and item 7 in `v2/docs/records/l4e7/clarification/analog-devices-lt8705a.txt` (the owner
sends them).
