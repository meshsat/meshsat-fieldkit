# L4-E11: source-only and dead-pack operation (U-04), the vehicle-entry interconnect (D-06) and the hot swap's fault timer (D-09) (MESHSAT-1357, 2 October 2026)

**Prototype design, desk arithmetic.** Nothing is bought, built, powered or measured, and no board of this set has a layout.
This page edits no generator, registry record, interface, Layer 3 file or other record. Its circuit changes are three
release-guarded drafts (`apply_gen_sch_e_entry.py`, `apply_gen_sch_a_guard.py`, and `apply_gen_sch_e_timer.py` as the
alternative while the LM5069 stays) and one specification (the corrected knee, section 3f); its interface and firmware texts are
drafts for Layer 5 and the Layer 4 coordinator (section 7a). Every figure is printed by `l4e11_power.py` into `l4e11_power.out`
("out N" is its section), which reads each figure from a generator, a committed netlist, a record's committed output or script, a
filed catalogue reading or a maker's document, each pinned by sha256; L4-E9's output and its hot-swap draft are read from its
commit `3c09b3da` and never retyped. Classes: MAKER, CATALOGUE, NETLIST, REQUIREMENT, RECORD, INFERRED, CONDITIONAL, ASSUMPTION,
and SESSION for a choice this record takes under the owner's standing rule of 26 September 2026 and his ruling of 21 September
2026 that engineering decisions are the session's.

**The task.** U-04 and D-06 were left open by L4-E9 (`L4-POWER-ARCHITECTURE.md` section 7, fix round at `71486686`); D-09 was
found by L4-E9's final round (`3c09b3da`) and added to this task by the coordinator on 2 October 2026. **The fix round** answered
the collaborator's focused check (`checks/astra-check-l4e11-1.md`: the UVLO's equations and POREN, the charge holds, the source
bounds, the weak-source envelope, the charge bounds). **The final round** answers its targeted recheck
(`checks/astra-check-l4e11-2.md`, NOT YET): (1) the efficiency floor was scaled at a fixed voltage; (2) the breaker's timing left
out TI's loaded delay and the short-circuit filter; (3) "met with drafts" compared the plan load only; (4) the resistance floor
allowed 1000 A while the obligations stopped at 883.5 A; (5) R-b's bound ignored the accuracy row's temperature condition; and
four minors. **The consolidation round** (2 October 2026, sections 12 to 14) answers the coordinator's U-04 question for the
consolidation: TI's BQ25730 against this circuit, at most three approaches compared, one selected and U-04 classified. **The fix
round** (section 15) answers the consolidation review cx36 (set 27, NOT YET): its B1, B2 and the charger minors. **The fix round for
the review of the provisional fixes** (section 16) answers the external review's L4-F02 (B2 kept open) and L4-F03 (the dock's VSYS
contact without branch protection).

## In short

- **REQ-015 at 9.00 V at the plug: CONDITIONAL CANDIDATE, not closed.** The drawn entry cannot start from a 9.00 V plug; the
  selected entry (3c, drafted), the corrected knee (3f, specified) and the guard (drafted) carry a bounded shedding sequence
  (3g) at the plan load at every source corner: the warm-up 28.12 W against 29.09 W delivered at the least, 0.98 W in hand,
  then the charge from a 9.52 W surplus. At the load's hi corner the shed state alone (35.24 W) exceeds the source's least, so
  neither control nor the warm-up is bounded there, and the cells' warming time has no held thermal model. It closes on named
  evidence: E11-06 (the shed load at most 20.51 W, the front end's efficiency at least 0.880, the pin's band, the transients),
  E11-09 (the knee drawn), E11-23 (the warm-up time), E11-05 (N1, N2 for S2) and E11-22 (R-b's bounds).
- **Item 1, the efficiency floor.** With the current and the voltage coupled, the floor is Pout / [Itrip x (9 - Itrip x
  Rloop)]: 0.908691 at the fix round's own point (it reproduces 6.36376 A; the fix round's 0.906 is withdrawn). That 2.6 %
  margin is not defensible on held evidence, and R19 cannot buy more within F1's 7.3 A column (its least value 4.399 mOhm moves
  the lowest trip only to 6.51 A, no stocked part). **SESSION: the knee's flat target drops from 1.89 to 1.82 A**, sized to the
  shed warm-up instead of PS-SURV with the heater: the in-service maximum falls to 5.983 A, 6.4 % under the lowest trip, and the
  floor to 0.880 (5.4 % under L4-E5's undocumented 0.93). What closes it is E11-06's measurement of the efficiency, the pin's
  band and the transients.
- **Item 2, the timing.** The breaker's delay is taken from TI's loaded row (370 us typical at CTMR 22 nF): 0.247 / 0.37 / 0.49
  ms. The short-circuit sense passes a first-order filter (RISCP x CSCP, 2.74 to 3.31 us) and then 5 us; the scan now carries
  both, and the current through them: CSD19532Q5B 3.08 of its derated chart, CSD19536KTT 0.704; a start into a hard short 0.743
  (73.4 A for 9.04 us). The threshold (10.36 to 13.87 A) is where the trip begins; the peak in a hard short in service is set by
  the loop inductance, and stays under Q7's derated 178 A for 2.08 uH or more (E11-20). L4-E5's V-A08 is redrafted for the
  breaker's 0.247 ms and the guard's 7.24 V (section 7a, E11-21).
- **Item 4, the prospective fault current.** The loop's actual floor is raised to 56.93 mOhm at 20 C so a stiff source at 43.18
  V gives at most 900 A, 10 % under F1's 1000 A; the reading, four-wire with 2 % and 2 K of uncertainty, must sit at 58.51 to
  64.21 mOhm; the selected construction (3.05 m of AWG 14 with the 0.5 m lead and the contacts) reads 58.82 to 63.57 mOhm. 900 A
  is carried through the last interval, E11-15, E11-16 and every element's withstand obligation.
- **Item 5, the charge current.** R-b permits two settings, 0x0000 and 0x0200; at 0x0200 the actual current is 0.8314 to
  1.2567 A only inside TI's row condition (SRN above VSYS_MIN, 0 to 85 C). Outside it, and under VSYS_MIN, the bound is
  INCONCLUSIVE (E11-22); Q2's 124.9 C is CONDITIONAL on it and on board P's copper.
- **The minors:** the obsolete UVLO model is gone from the script; section 5 compares each state with each ceiling; R-b's
  general maximum is 21.22 W (at 16.884 V); R-a's S4 exception and the hold's persistence are explicit (section 4).
- **The dependency round (section 11):** every specification left to a maker is a row (D1 to D10) with the claim it decides, what
  a maker's answer and what one bench sample can establish, and the consequence of a negative answer; the bounded fallback (a
  direct hybrid can and an isolated hold-up bank on VBAT, 1.117 ms for the worst admitted 48.39 W step) removes D2 and D5 from
  TI's hands; **U-04 stays an architecture-level choice**, resting on D1 and D3, whose negative answers return (B).
- **The consolidation (sections 12 to 14):** TI's BQ25730 (SLUSE65A, held) in U3's land, with a P-channel battery FET Q39, prints a
  bound on VSYS in all three modes (at least 12.054 V with no battery at TJ -40 to 125 C; VSRN + 150 mV within 2 % with the charge
  inhibited), removing D1, D3 and D4; every L4-E4 to L4-E8 setting rests on rows the two sheets print alike. **SELECTED
  (SESSION), drafted in `apply_gen_sch_a_charger.py`**; E11-24's bank is withdrawn; Q39's thermal bar (RthJA at most 20.54 C/W
  for OCD1's 20 A held) and its docking pulse are the new items. **U-04 becomes a downstream qualification test with bounded
  evidence and a workable fallback** once the draft is applied (on the drawn board it stays section 11's architecture-level choice).
- **The fix round (section 15, review cx36):**
  - *B1:* board E's auxiliary domain (U12 and both mixer fans) moves from CELL_F to board A's VSYS over the dock's pin 1, so the
    source carries it while the charge is held and with the pack absent (`apply_gen_sch_e_aux.py`, `apply_pcb_interfaces_dock.py`).
  - *The start:* bounded by the input clamp, the retries (a latch within 3.062 s at worst) and a bench acceptance; the 502.3 ms
    claim is withdrawn.
  - *B2:* the battery FET is re-selected on its makers' printed maxima at BATDRV's least 8.5 V drive: **two Nexperia BUK6Y10-30P
    in parallel**, a bar of 34.42 C/W per FET at +70 C air, with the 18 A for 60 s service kept and no protection lowered (its bound,
    transient shape, Ciss reading and docking I2t superseded by section 16; the selection stands).
  - *The charger minors:* the inhibited acceptance is now piecewise.
- **The review of the provisional fixes (section 16; qualification gaps, not demonstrated failures):**
  - *L4-F02, the battery FETs:* RDS(on) at 8.5 V is an allowance (21.136 mOhm) no printed point bounds, CONDITIONAL on E11-36; the
    thermal basis is the BUK6Y10-30P's own Fig. 4 with the coupling inside the measured Zself + Zmut, the 18 A for 60 s from the hot
    state at 126.7 C, CONDITIONAL on E11-29; Ciss is not shown under TI's 5 nF (about 5.74 nF typical near 0 V), OPEN on E11-37; the
    docking pulse is taken whole in one FET (TJ 123.3 C from +70 C on the stated VF bound), CONDITIONAL on E11-30.
  - *L4-F03, the dock's VSYS contact:* an eFuse U42 (TI TPS16630, 1.4713 to 1.8018 A) on board A, the contact at 51.5 % of 3.5 A,
    VSYS_E at least 9.539 V; drafted in `apply_gen_sch_a_charger.py` and `apply_pcb_interfaces_dock.py`; the hot short's peak E11-38.
- **D-06** stays resolved in design with the corrected envelope and floor; **D-09** keeps its reproduced margin (4.927 to 14.653
  ms against 4.593 ms) and its conditional chart (0.71 A against 0.675 A), as the resolution while the LM5069 stays.

## 1. What the requirements demand of source-only operation (U-04; out 1)

Quoted from `pcb_requirements.yaml` and `TEST-PLAN.md`, not reinterpreted:

- **REQ-015**, statement: "A 9 to 36 V vehicle and shore input runs the kit and charges the pack, with reverse-polarity
  protection, under- and over-voltage limits, a line filter designed to MIL-STD-461 limits, a NATO 2-pin plug cable and the
  MIL-DTL-38999 receptacle. The input is not qualified against any vehicle surge standard and is not intended for 24 V military vehicle buses (D-16)."
  Acceptance: "Operates and charges across 9 to 36 V, and takes a reversed input and an over-voltage to the front end's limit
  (40 V, 32.55) without damage, on the prototype; CE102 under its limit line (TEST-PLAN M1)."
- **REQ-014**: "missions longer than the pack rely on vehicle or solar input (D-06)".
- **REQ-024**: "a pack cold-soaked below about -10 C at the cells is not started from (shore or vehicle power, or warming,
  first; D-02d)"; its acceptance, TEST-PLAN E4-O: "started warm or from shore or vehicle input (D-02d: a cold start from the
  pack below about -10 C cell temperature is out of scope; inside the envelope, so an acceptance test)".
- **REQ-046**: "The cells are charged only between 0 and +45 C and discharged only between -10 and +60 C at the cell surface;
  below 0 C the pack is warmed by its heater mat before charge."; its acceptance: "the bridge's own hold clears above 3 C
  (PANEL.md section 10)".
- **REQ-077**, acceptance: "the charge held by the charger's CHRG_INHIBIT with the charger still carrying the kit on shore".
- **REQ-072** (obligation OBJECTIVE): "after a permitted pack cutoff the remaining supply carries the loads, D-26".

| Requirement | Obligation | Source voltage | Names a load state | What it asks of a source alone |
|---|---|---|---|---|
| REQ-015 | mandatory | 9 to 36 V, the measuring point not stated | no | operates and charges; the pack's state not named |
| REQ-014 | mandatory | none | no | longer missions rely on the input |
| REQ-024 (D-02d), E4-O | mandatory | shore or vehicle (9 to 36 V by REQ-015) | no | a start with a cold-soaked pack, both of whose FETs are open below -9 C (the image's UTD; UTC 1 C) |
| REQ-046 | mandatory | none | no | the pack warmed by its heater before charge; the bridge's hold clears above 3 C |
| REQ-077 | mandatory | on shore | no | the charge held by CHRG_INHIBIT while the charger carries the kit |
| REQ-072 | objective | solar | yes (PS-IDLE-SPEC) | after a permitted pack cutoff the remaining supply carries the loads |

**So**, at 9 V REQ-015 does not mean the full PS-IDLE-SPEC profile: its text names no profile, and the record does not add one.
The mandatory text does ask a function of a source alone: a start and a pack warm-up with the pack's FETs open, and a charge hold
during which the charger carries the kit. This record turns that into a functional acceptance at 9 V at the plug (section 3g): a
bounded shedding sequence (one module running the bridge, its fans, HF, Geiger and 5G modules held, the heater on measured
headroom, the charge held, then the charge) carried by the source.

## 2. The charger and the pack with no usable pack (U-04; out 2)

**What SLUSE66A states (MAKER):** no battery MOSFET (p.1); from VBUS the registers, the cell count, then "Converter powers up."
with no battery condition (9.3.1, p.24); power-up curves drawn "2-cell without battery" (Figures 10-4, 10-5, p.89); "When
CHRG_OK goes HIGH, the system is powered from adapter through the charger. When adapter is removed, the system is connected to
battery." (11, p.92); CHRG_OK's conditions are VBUS's window and the faults, not the battery (9.3.4, p.25); DPM cuts the charge
first and then "the system voltage starts to drop" while the battery supplements (9.3.17, p.29); 4S defaults ChargeVoltage
16.8 V, SYSOVP 19.5 V, VSYS_MIN 12.3 V (Table 9-2) and the charge clamped at 384 mA while SRN is under VSYS_MIN (8.5, p.10), **a
typical figure with no minimum or maximum printed**; ChargeCurrent with the 5 mOhm RSR in 128 mA steps, and at
REG0x03/02 = 0x0200 (1024 mA) regulated within -18 % to +21.5 %, a row printed for VBAT above VSYS_MIN **and 0 to 85 C** (8.5,
p.10), with no accuracy printed for any setting under it; in the BATOVP
paragraph, with charge enabled the converter shuts down and "if charge is disabled the converter should keep operating without
disturbance" (9.3.21.5, p.34): **a sentence about a battery over-voltage event, not a specification of VSYS's regulation or
transient response with no battery** (N1, N2); AUTO_WAKEUP_EN, 0 at POR, would give a battery under VSYS_MIN 128 mA for 30 min,
but only after a host sets it (p.61); HIZ: "converter shuts off" under 0.4 V on ILIM_HIZ (9.3.8); VSYS under 1.6 V for 2 ms:
"shut down and latched off" until a host write (9.3.21.8); "Overall 50-uF effective capacitance on VSYS net is necessary
(POSCAP is preferred)" (10.1, p.83).

**ChargeCurrent() at POR.** The register description says 0 A, its reset value encodes 256 mA, and TI's expert on E2E thread
1316778 (held) states 256 mA, the description being in error (corrected in the dependency round, section 11, row D4).

**What the boards and the pack's image add (NETLIST, RECORD):** board A's strap reads 4S (75.1 % of VDDA), so U3 never sees
"battery removal"; every load is on VSYS with the pack beyond R17; CHG_INHIBIT pulls ILIM_HIZ low (HIZ); SHORE_INHIBIT pulls the
hot swap's UVLO low (input off); board P's gauge has no PCHG FET and its image writes PCHG_COMM 1 (pre-charge through the
charge FET, SLUUAQ3A 4.9 and 14.2.1.1); a CUV trip sets XDSG only (2.2); UTD -9 C sets XDSG and UTC 1 C sets XCHG (4.12); Q2's
body diode is CSD17570Q5B's, VSD at most 1 V (at 50 A) and RthetaJA at most 50 C/W (p.3).

**What follows, by pack state (INFERRED from the rows above):**

| Pack state | VSYS | Charge | What holds it |
|---|---|---|---|
| absent, or both FETs open (below -9 C, SHUTDOWN, a permanent fail) | ChargeVoltage, at most 16.884 V written | none | the voltage loop on SRN with no current in R17 (11, 9.3.1); N1 |
| at CUV, charge FET on | the stack plus VSD, 10 to 11 V | the clamp, 384 mA typical, while SRN is under 12.3 V (0.038 C a cell, under Samsung's 0.1 to 0.5 C pre-charge range, a lower current with no consequence stated) | the clamp; its maximum is not printed: R-b's case (iii), INCONCLUSIVE (E11-22) |
| self-discharged to the Shutdown Voltage (2.0 V a cell) | 8 to 9 V while it precharges | as above | under A-14's assumed 10.0 V floor: the loads wait (N5) |
| the clamp lifted (SRN at 12.3 V, a stack of 11.3 V or more) before CUV recovers (3.00 V a cell) | rising | ChargeCurrent through Q2's diode: 3.0 A would be 3 W, 150 K over the air | rule R-b: 0x0000 or 0x0200 only; in case (i) at most 1.2567 A actual, 1.257 W, 62.8 K, TJ 124.9 C at 62.1 C air (CONDITIONAL, section 4) |
| CHG_INHIBIT (HIZ) or SHORE_INHIBIT asserted, the pack unable to discharge | none: the kit stops, its controller dies, the pull-downs release the line, it restarts: a loop | none | rule R-a forbids it |

**Finding U4-F1.** FW-C08 asserts SHORE_INHIBIT "on the bridge's request when the pack reads below 0 C" (and PANEL.md section
10 says the same). With a pack cold-soaked below -9 C both FETs are open, so the hold cuts the very source start REQ-024
requires; with HIZ the same follows (9.3.8). CONOPS already holds the H1 charge by the CHRG_INHIBIT bit for this reason.

**Not stated in any held document (named, not inferred):** N1 VSYS's regulation and transient response with no battery under
the kit's load steps; N2 what the converter regulates with CHRG_INHIBIT = 1 or ChargeCurrent 0 and no battery current
(Q-TI-3); N3 whether the charger charges before any host write (Q-TI-2); N4 VSYS's effective capacitance at 16.884 V against
TI's 50 uF; N5 every load converter's minimum input (A-14, R-49); N6 0-V charging before the gauge's SUV check (Q-TI-7).

## 3. The entry at a 9.00 V plug, the kit's own losses and the source envelope (U-04; out 3)

### 3a. The drawn LM5069 cannot start from a 9.00 V plug (finding U4-F2, corrected)

SNVS452G gives UVLOTH 2.45 / 2.5 / 2.55 V and UVLOHYS 12 / 21 / 30 uA (p.5), and Equations 38 to 40 (p.24): the **falling**
threshold is UVLOTH x (1 + R20/R21) and the **rising** one adds UVLOHYS x R20 (MAKER). The first round placed the hysteresis on
the falling edge; its numbers and its R21 draft were wrong, the draft is withdrawn and the script no longer carries that model.
Corrected (INFERRED): as drawn (R20 100k, R21 38.3k, 1 %) the entry turns on at 9.91 / 11.13 / 12.37 V and off at 8.72 / 9.03 /
9.34 V; the withdrawn R21 42.2k would turn it on at 9.33 / 10.52 / 11.74 V: neither starts from 9.00 V.

No divider fixes it. POREN, the threshold at which the LM5069 enables all its functions, is 8.4 V typical and **9.0 V at most**
at its own VIN; PORIT 7.6 / 8 V; the operating range starts at 9 V (p.1, p.5; MAKER). U6's VIN is DC_P, behind the LM74700 ideal
diode (NETLIST), whose regulated forward drop is 13 / 20 / 29 mV (SNOSD17G): before the hot swap conducts, VIN is at most
**8.987 V** from a 9.00 V plug, under POREN's 9.0 V maximum (NOT MET, INFERRED); with the in-service current flowing it falls
further, to 8.43 V at the plug's maximum (3e). The IC cannot be supplied from elsewhere: VIN is the current-sense reference (VCL
is the VIN-SENSE voltage), so it sits at R19's top (MAKER, NETLIST).

### 3b. What a replacement must do, and the candidates

(1) Operate and enable below its own supply at the in-service maximum from a 9.00 V plug (DC_P 8.43 V hot); (2) act on overcurrent
between the in-service maximum at 9 V (5.983 A with the final round's knee) and F1's 80 C column (7.3 A); (3) keep the pass FET
inside its derated chart in every start, a start into a resistive fault or a hard short included; (4) lock out over-voltage above
CS101's 38.83 V peak and under D10's 42.4 V breakdown at -20 C (L4-E9), with a 100 V class rating like the LM5069's.

| Candidate (TI sheet, held back) | Rows read (MAKER) | Verdict |
|---|---|---|
| TPS1663 eFuse (SLVSET9G) | 4.5 to 60 V, 67 V absolute; its highest current limit (RILIM 3 k) 5.58 / 6 / 6.42 A | fails (2): its lowest limit is under the in-service maximum |
| TPS4811-Q1 (SLUSEE5E) | VS 3.5 to 80 V, 100 V absolute, VS POR 2.75 / 3 / 3.2 V; EN/UVLO and OV 1.16 / 1.18 / 1.2 V rising, 1.1 / 1.11 / 1.13 V falling; OCP 29.2 / 30.6 / 31.5 mV at RSET 100 Ohm, RIWRN 39.7 k; ISCP bias 13.7 / 15.6 / 17.6 uA (Equation 11); TMR 73 / 82 / 91 uA to 1.112 / 1.2 / 1.3 V; the overcurrent delay 370 us typical at CTMR 22 nF, CL 47 nF; short-circuit propagation 4 / 5 us at CL 47 nF; Equation 3's gate-slew inrush | meets (1), (2) and (4); it limits no power, so (3) rests on the pass FET: **selected** with a FET that carries it |
| a power-limiting controller under 9 V | none among the held sheets (TI's power-limiting hot-swap family starts at 9 V or above) | not drafted (named) |

### 3c. The selected entry (SESSION; draft `apply_gen_sch_e_entry.py`)

U6 **TPS48110AQDGXRQ1** (LCSC C17556513, the OV-pin variant with auto-retry), Q7 **CSD19536KTT** (C2687963, D2PAK), R19 **4.5
mOhm** 1 % 50 ppm/K (C2985708), L2 **SRF1260-1R0Y** (C7084461); RSET 100 Ohm and RIWRN 39.7 k at 0.1 % (TI's characterised point;
C861872), RISCP 3.01 k, CTMR 22 nF C0G (C97929; TI's characterised capacitor for the delay row), gate slew R1 36.5 k with C1 10 nF
C0G 100 V (C184799) and R2 10 Ohm, CBST 1 uF; UVLO 59.0k over 10.0k, OV 332k over 10.0k at 0.1 %, INP 100k over 39k, TI's 100 Ohm
and 100 nF VS filter and 1 nF CSCP. Its figures (INFERRED from the rows of 3b and the parts' tolerances):

| Function | Value |
|---|---|
| UVLO (DC_P) | on at 7.87 / 8.14 / 8.44 V, off at 7.46 / 7.66 / 7.95 V |
| OV | off above 39.6 / 40.36 / 41.22 V, on again under 37.55 / 37.96 / 38.82 V |
| overcurrent threshold | 6.364 / 6.8 / 7.136 A |
| overcurrent delay | Equation 7 gives 0.247 / 0.322 / 0.426 ms; TI's loaded row prints 370 us typical at 22 nF, sense to PD at CL 47 nF (SLUSEE5E p.10). Taken: 0.247 ms at least (Equation 7's, the row's excess not counted), 0.37 ms typical, 0.49 ms at most (Equation 7's maximum scaled by the row's 1.149); retry 0.5 s |
| short-circuit threshold | 10.36 / 12.04 / 13.87 A, on the sense filtered by RISCP x CSCP (2.74 / 3.01 / 3.31 us), then PD within 4 / 5 us (at CL 47 nF; Q7's 153 nC at 12 V is 12.75 nF, under the test load) |
| the start | slew 17.28 / 20.71 / 24.65 V/ms; inrush 0.382 to 1.219 A into 22.1 to 49.5 uF; at most 2.5 ms to 43.18 V |
| pins at the clamps' 64.5 V | INP 18.36 V, EN/UVLO 9.35 V, OV 1.89 V, under the 20 V absolute; INP high from 7.23 V |

**The threshold is where the trip begins; the peak is where the current has got to by the end of the delay.** The filter's
delay depends on the overdrive: a 14 A step against the highest 13.87 A threshold takes 14.19 us before the 5 us propagation (the
check's example); a ramp lags by at most the filter's time constant. So no fixed "5 us + 3RC" bound is used: the scan follows the
filtered current and the trajectory through every delay.

**Faults at the start (out 3c; every point of the pulse held against the chart for the whole pulse, conservative, derated by
L4-E9's 0.4454; the CSD19536KTT's Figure 4-10 read from TI's vector drawing: at 43.18 V 100 us 221.7 A, 1 ms 20.02 A, 10 ms 6.228
A, MAKER; INFERRED):**

| Fault | CSD19532Q5B (as drawn) | CSD19536KTT (selected) |
|---|---|---|
| a start into a resistive fault, 0.1 to 1000 Ohm, the breaker at its slowest (7.14 A for 0.49 ms; 13.87 A filtered at 3.31 us, then 5 us) | 3.08 of the chart at 0.74 Ohm, 0.583 ms, ended by the short-circuit trip: NOT MET | 0.704 at 1.21 Ohm, 0.954 ms, ended by the short-circuit trip: MEETS |
| the ordinary start | 0.689 | 0.182 |
| a start into a hard short: VDS stays at 43.18 V, the current follows the gate at most 8.11 A/us (gfs 329 S, TI's typical at 100 A taken as the bound, times the highest slew) | not computed | a peak of 73.4 A after 9.04 us, 0.743 of the derated 100 us line: MEETS, CONDITIONAL on the transconductance bound |

**A hard short in service** (Q7 fully on): the current rises at VIN / L; the filter and PD add at most 8.31 us, so the peak is at
most 13.87 A plus VIN x 8.31 us / L, and never more than VIN over the loop's resistance. Q7's IDM 400 A derated by 0.4454 gives
178.2 A, which at the entry's highest on-voltage (41.22 V) holds for a loop inductance of **2.08 uH or more** from the source to
the fault. No document gives the inductance (L4-E9's open item): E11-20 carries this bound (CONDITIONAL).

### 3d. The kit's series resistance from the plug, hot

The measured loop (the cable, the D38999 pair, the inside lead and J_DCIN) at its actual ceiling, 66 mOhm at 20 C, with 6.1 m
outside at REQ-024's +40 C and 1 m inside at the 62.1 C air: 71.995 mOhm (SESSION, INFERRED); the NATO plug's pair 3.652 mOhm
(ASSUMPTION, as a size 12 contact); F1 at its rated current 10.8 mOhm (MAKER, 108 mV typical); its holder 1 mOhm (ASSUMPTION); Q1
hot 7.02 mOhm (NETLIST 3.9 mOhm x 1.8, ASSUMPTION); R19 4.556 mOhm (CATALOGUE); Q7 hot 4.32 mOhm (MAKER 2.4 mOhm x 1.8); L2 at the
air plus its rise 33.992 mOhm (MAKER, INFERRED); board copper and the dock's pins 5 mOhm (ASSUMPTION). **94.47 mOhm from the plug
to DC_P, 47.87 mOhm on to VIN_RAW, 142.34 mOhm in all.**

### 3e. The in-service maximum at a 9.00 V plug, and the efficiency floor (item 1)

With the corrected knee's high band, VBUS20 at 20.96 V and the front end at 0.93: **VIN_RAW 8.148 V, 5.983 A from the plug, DC_P
8.435 V** (INFERRED). The UVLO's highest rise (8.44 V) sits under DC_P before any current (8.971 V) and its highest fall (7.95 V)
under DC_P in service (8.43 V) (MEETS). F1: the breaker's highest 7.136 A under its 7.3 A column (MEETS); L2 at 7.14 A 36.1 K over
the air, 98.2 C against 105 C (MEETS); Q7 0.22 W.

**The efficiency floor, with the current and the voltage coupled:** the front end draws Pout / eta at VIN_RAW = 9 - I x Rloop, so
the breaker's lowest is reached when eta = Pout / [Itrip x (9 - Itrip x Rloop)]. At the final round's point that is 45.339 W /
[6.36376 A x (9 - 6.36376 A x 142.336 mOhm)] = **0.88021**. At the fix round's own point (knee 1.89 A, loop 141.525 mOhm, the
check's reproduction) the same equation gives 46.836 W and **0.908691**, and at that efficiency it returns 6.36376 A, the trip's
lowest: the fix round's 0.906 scaled the current inversely with the efficiency at a fixed voltage, and is withdrawn (INFERRED).

**Judged:** the component temperatures and losses are bounded (the hot case is the worst), but the static margin rests on three
things no held document bounds: the front end's efficiency at about 8.1 V and 45 W (L4-E5's 0.93, undocumented, C-8), the pin's
real band (L4-E5's +-0.2 A, INFERRED), and the input current's excursions in load steps and source changes, which the breaker
passes only for less than 0.247 ms. At the fix round's knee (1.89 A) the margin was 2.6 % and an efficiency of 0.909 tripped
the breaker: not defensible. R19 cannot buy more: its least value that keeps the breaker's highest under F1's 7.3 A is 4.399
mOhm (no stocked part), and that moves the lowest trip only to 6.51 A. **SESSION: the margin is moved on the other side, the
knee's flat target to 1.82 A** (3f), sized to the shed warm-up (3g) rather than PS-SURV with the heater: the in-service maximum
is 5.983 A, **6.4 % under the lowest trip**, the efficiency floor 0.880 (5.4 % under 0.93), and the same margin read as U3's board
current is 0.122 A over the knee's high band. CONDITIONAL: E11-06 measures the three at a 9.00 V plug. *Reversed by:* a measured
efficiency under 0.880 or a pin band wider than inferred: then the knee drops further (the warm-up's margin pays) or F1 changes.

### 3f. The corrected knee (SESSION, a specification) and the restart guard (draft `apply_gen_sch_a_guard.py`)

L4-E5's H3 network is not drawn (its own missing draft), so this record specifies the shape it is to be drawn to: **a flat 1.82 A
of board current** (the pin at 1.728 V) from VIN_RAW **7.95 V** up to 10.549 V, where L4-E5's line takes over; below 7.95 V
L4-E5's knee slope (2.484 V/V at the pin): zero at 7.657 V, HIZ entry 7.415 V, exit 7.576 V. With L4-E5's +-0.5 % the knee's top is
at most 7.99 V, 0.158 V under the plug's operating point, and HIZ is certain below **7.378 V**. The shed warm-up's plan figure sets
the target at 1.7666 A or more; 1.82 A leaves the rest of the window to the breaker (3e).

The front end's restart guard (U34, board A) as drawn falls at 7.856 / 8.08 / 8.309 V, over the plug's 8.148 V operating point.
**R14 76.8k 1 % (C23107)** puts its fall at **6.754 / 6.944 / 7.139 V** and its rise at 6.889 / 7.083 / 7.282 V, 0.239 V under the
knee's certain HIZ (L4-E5's rule: 0.1 V or more); at its lowest fall the guard's running levels scale to FE_VZ 4.64 V, FE_RUN
2.75 V (Q36 and Q37 need 2.5 V at most) and EN 1.89 V (VEN(OP) 1.29 V at most) (INFERRED).

### 3g. The functional warm-up at a 9.00 V plug, as a bounded shedding sequence (item 3)

REQ-024's start with the pack cold-soaked (both FETs open, S4), REQ-046's heater before any charge, and the charge held while the
charger carries the kit (REQ-077) are done by the bridge on slot 2. The loads are computed with hc2's `pwr_red2.py` and rv-pwr's
`pwr_budget.py`, run as hc2 runs them (both pinned; the model reproduces `pwr_red2.out`'s PS-SURV), battery-side (RECORD,
INFERRED). **SESSION: the shed state P1 holds the two mixer fans (0.78 / 1.44 / 3 W at the load; the inside air is cold, the
modules' own cooler fan stays), the HF module (0.1 / 0.1 / 2.5 W), the Geiger module (0.1 / 0.3 / 0.5 W) and the 5G module
(0.222 W);** the bridge, GNSS, Iridium and the panel (the SOS path) stay.

| Phase | lo / plan / hi W at VBAT | against 9.00 V at the plug, 29.09 to 42.52 W (3h) |
|---|---|---|
| P0 start: the bridge boots on slot 2 (PS-SURV) | 12.45 / 21.73 / 42 | carried / carried / only above the minimum |
| P1 shed | 11.17 / 19.57 / 35.24 | carried / carried / only above the minimum |
| P2 warm-up: P1 with the regulated mat on | 19.7 / 28.12 / 43.82 | carried / carried / not carried |
| P3 charge: the cells over 3 C, the cold hold cleared | the source's surplus over P1 goes to the charge by DPM: 9.52 W at the plan figure, none at the hi corner | within R-b's bounds |

The mat runs on measured headroom (SESSION): on only while the source's measured headroom over the load is at least its 8.58 W,
else it is cycled, so control is kept whenever P1 alone is carried, and the warm-up completes on that rule while P1's load is at
most **20.51 W** (the source's least 29.09 W less the mat).

**The result.** At the plan figure every phase is carried at every source corner, the warm-up with 0.98 W in hand (the fix
round's comparison had 61 mW). At the hi corner P1 (35.24 W) exceeds the source's least, so neither control nor the warm-up is
bounded there by held evidence; the hi corner is an estimate's upper bound (the supervisors, the panel, the hubs and the HF
module at their highest estimates), and E11-06 measures P1. **The thermal side:** P2 puts 28.4 W of heat inside; with hc2's
lid-open conductance (3 to 3.3 W/K, the fans on, which understates the air's rise with the mixer fans held) the inside air at
-20 C ambient is -11.4 to -10.5 C, so the cells are warmed by the mat alone; the time from the cold soak to 3 C needs the
mat-to-cell coupling and the pack's loss to the air, which no held record gives (E11-23).

**REQ-015 at 9.00 V at the plug: CONDITIONAL CANDIDATE.** It closes when E11-06 shows P1 at most 20.51 W, the front end at 0.880
or more, the pin inside its band and the breaker never tripped; E11-09 draws the knee; E11-23 measures the warm-up time; E11-05
answers N1 and N2 for S2; and E11-22 closes R-b's open cases. It is not claimed closed.

### 3h. The source envelope at the plug

The low side with the losses hot and VBUS20 at 19.146 V, the high side with no loss and 20.96 V, U3 0.9733 (INFERRED):

| Plug | VIN_RAW at the low side | U3 board current, A | at VBAT, W | L4-E9 at VIN_RAW (no loss) |
|---|---|---|---|---|
| 9 V | 8.43 V | 1.561 to 2.084 | 29.09 to 42.52 | 19.9 to 36.6 W |
| 12 V | 11.541 V | 1.729 to 2.339 | 32.22 to 47.72 | up to 47.4 W |
| 24 V | 23.522 V | 3.755 to 4.451 | 69.97 to 90.81 | up to 90.6 W |
| 36 V | 35.62 V | 4.537 to 4.884 | 84.55 to 99.64 | the window |

| State (plan, at VBAT) | 9 V | 12 V | 24 V | 36 V |
|---|---|---|---|---|
| PS-RED 22.2 W | carried | carried | carried | carried |
| the warm-up P2 28.12 W | carried | carried | carried | carried |
| PS-RED with the heater 33.1 W | above the minimum only | above the minimum only | carried | carried |
| PS-IDLE-SPEC 42.8 W | not carried | above the minimum only | carried | carried |
| PS-IDLE-SPEC cold, heater on 45.46 W | not carried | above the minimum only | carried | carried |
| PS-TYP 63.0 W | not carried | not carried | carried | carried |
| the cold warm-up 71.06 W (CONOPS 4c) | not carried | not carried | above the minimum only | carried |

A dead pack's charge on top: at most 1.257 A x 16.884 V = 21.22 W under R-b in case (i) (17.59 W at its 14 V threshold), drawn
only from what DPM leaves after the system (9.3.17), so it never pushes the kit out of the envelope (INFERRED). A pack able to
discharge supplements any shortfall (L4-E9 section 3); these bounds are for the pack that cannot.

**Finding U4-F3, kept.** REQ-015 names no measuring point; **SESSION (first round): the design basis for its 9 V is the kit's
plug**, the most demanding reading. Through the drawn knee (zero at 8.75 V of VIN_RAW) a 9.00 V plug settles VIN_RAW at 8.832 V
and gives 10 W (8.819 V and 8.3 W with the drawn lead), against 30.2 W at VIN_RAW 9 V: 3f replaces that knee (out 3i).

## 4. The comparison, the selection and the rules (U-04; out 4)

| | (A) the drawn non-power-path charger, with rules | (B) a charger with a battery FET (NVDC power path) | (C) a pre-charge path on board P (PCHG FET and resistor) |
|---|---|---|---|
| Power at 9, 12, 24 V with no usable pack | section 3h's envelope; the same in (B) and (C), whose limit is the source path, not the charger | the same | the same |
| Start from a dead pack | the source carries the kit at once when the pack is absent or both FETs open; a pack at CUV holds VSYS at 10 to 11 V; one self-discharged to 2.0 V a cell holds it at 8 to 9 V, under the converters' assumed floor, until it precharges | VSYS regulated at VSYS_MIN whatever the pack; the pack precharged through the battery FET | VSYS stays at ChargeVoltage while the resistor precharges the pack |
| Protection interaction | the gauge's window acts on its FETs as now; rules R-a and R-b keep the holds off the source and the diode's junction under its maximum (CONDITIONAL on R-b's case (i) and board P's copper) | a series FET in the pack path, a new single point on the battery-only path, its own fault list | the PCHG FET short leaves a resistor path round both protection FETs; the resistor in the sealed case |
| Parts and board changes | none of power for the charger (the entry's replacement, 3c, is needed by every option) | U3 replaced, a battery FET, every L4-E4 to L4-E8 setting on the charger re-derived (IIN_HOST, H3 on ILIM_HIZ, R11, R12, the bank) | a P-FET, a power resistor and its land on board P; PCHG_COMM 0 in the image |
| Energy cost | none | 0.324 W per mOhm at 18 A; 8.8 mW per mOhm at PS-IDLE-SPEC | 8.98 W in the resistor at 2.0 V a cell for 0.1 C (8.63 ohm), 3.38 W for the charger's 384 mA (22.9 ohm) |
| What still depends on a maker | N1 (TI); N2 for state S2 (open); N3 for a pack below the controllers' floor; Q-TI-7; R-b's cases (ii) and (iii) | the new charger's sheet: the one NVDC charger held, TI's BQ25798, states the regulation (p.1) but its integrated battery FET carries 6 A RMS and 10 A for 1 s (p.7), under the pack's 18 A peak, so an external-FET part is needed, of which no sheet is held | Q-TI-7; the resistor's pulse rating |

Considered and not compared: a source-fed keep-alive rail for the controllers. It keeps the controllers up but does not run the
kit, which still hangs on VSYS; whether the controllers' own converters reach down to a dead pack's VSYS is E11-08's reading.

**Selected (SESSION): (A).** *Why:* it is the only arrangement with no power part added to the charger; TI's own text covers its
two central behaviours (the system powered through the charger with no battery, 11 and Figures 10-4 and 10-5; the dead pack
charged at a clamped current, Table 9-2 and 8.5); its hazards are rules, not topology (U4-F1's holds, R-a; Q2's diode, R-b); (B)
reopens five accepted records on a part whose sheet is not held, and (C) puts 3.4 to 9.0 W into the sealed case to buy a faster
start from a pack nobody requires the kit to start from at once. **Its cost, stated:** a pack self-discharged under about 2.4 V a
cell holds VSYS under 10 V until it precharges at the clamp; the time is not computable from held data and is measured by
E11-06. **Reversed by:** TI's answer to N1 (E11-05) or E11-06 showing VSYS does not hold under the kit's load steps with no
battery; the first remedy is VSYS's capacitance (TI's 50 uF effective, POSCAP preferred, E11-07), and only if that fails does
(B) return. **Superseded by section 14** (the consolidation round of 2 October 2026), which selects (B) as TI's BQ25730, whose
sheet is now held and prints the bounds; (A) and its rules stand on the drawn board until E11-27 is applied.

**Rule R-a, the charge holds as a state table (SESSION).** The gauge's own FETs give two separate permissions (SLUUAQ3A 2.2
and 4.12; INFERRED):

| State | Charge FET | Discharge FET | Examples | What carries the kit | How a charge hold is made |
|---|---|---|---|---|---|
| S1 | on | on | in both windows | the pack and the source together | the CHRG_INHIBIT bit or ChargeCurrent 0 (9.4.1): the converter keeps carrying the kit from the source (11), REQ-077 as written |
| S2 | on | off | a warm CUV trip; an OCD, AOLD or SCD latch | the source alone; the pack can still take charge through Q2's diode, so the gauge does NOT hold the charge | only the bit or ChargeCurrent 0; whether VSYS stays regulated with charge inhibited while the pack cannot discharge is N2 (Q-TI-3): OPEN, the bench shows it (E11-06) before the hold is relied on |
| S3 | off | on | between UTD -9 C and UTC 1 C; OTC; COV | the pack or the source | the gauge already holds; a requested hold (REQ-077's hot hold, the operator's "no charge") by the bit as in S1 |
| S4 | off | off | below -9 C; SHUTDOWN; a permanent fail; no pack | the source alone | the gauge holds. **The one exception to the bit:** in S4 the bit is NOT set and ChargeCurrent() is not written 0, so N2 never arises where the source alone carries the kit with no charge possible |

**The hold persists across states.** A charge hold (the cold hold, REQ-046's, REQ-077's hot hold, the operator's "no charge") is
a flag in the firmware, set and cleared only by its own condition (the cold hold clears above 3 C with hysteresis), never by a
state change. In S1, S2 and S3 the CHRG_INHIBIT bit follows the flag; in S4 it is left clear (the exception). On leaving S4 (a
FET closing, a pack fitted) the bit is written from the flag at once; in the firmware's reaction time only the gauge's window
acts, which keeps the cells inside their charge window. After a charger POR, ChargeCurrent() is 256 mA (TI's E2E answer, row
D4), so a 256 mA charge can begin before the firmware writes the flag's bit: in that window too only the gauge's window acts, and
256 mA is under R-b's bound. In every state the CHG_INHIBIT line (HIZ) and SHORE_INHIBIT are never a
charge hold; in S2 and S4 neither is asserted, because each removes the kit's only supply. SHORE_INHIBIT stays for the operator's
"inputs off" and the water-on-floor isolation, with a warning first in S2 and S4. REQ-077 asks the charger to carry the kit while
the charge is held; no pack fallback is relied on.

**R-b (SESSION; item 5).** While U3's own SRN reading is under 14.0 V or the gauge reports XDSG or PRECHARGE, ChargeCurrent()
takes **exactly two settings: 0x0000 (no charge) and 0x0200 (1024 mA set)**; no value under 0x0200, because TI prints no accuracy
for one. TI's accuracy row for 0x0200 (-18 % / +21.5 %) holds for a 5 mOhm RSR with VBAT above VSYS_MIN at 0 to 85 C (SLUSE66A
p.10, MAKER). The bounds by case:

| Case | When | Actual current | Status |
|---|---|---|---|
| (i) | SRN at or above VSYS_MIN, the charger inside 0 to 85 C | 0.8314 to 1.2567 A (R17 at +-1 %) | BOUNDED (MAKER row, INFERRED) |
| (ii) | SRN at or above VSYS_MIN, the charger outside 0 to 85 C (it sits in the inside air, -20 C at a cold start to 62.1 C hot, plus its own rise, which no held record gives) | not printed | INCONCLUSIVE: E11-22 |
| (iii) | SRN under VSYS_MIN | the clamp, 384 mA typical, no maximum printed | INCONCLUSIVE: E11-22 |

In case (i) Q2's diode dissipates at most 1.257 W, 62.8 K over the air, so its junction is at most 124.9 C at the 62.1 C inside
air against 150 C: **CONDITIONAL** on case (i) holding and on board P's installed copper giving TI's 50 C/W, which TI states for
its own 1 in2 2 oz board (E11-22). Without the gauge's report the 14.0 V threshold covers a cell up to 0.25 V under the stack's
average (the panel controller reaches the gauge only through a running module). R-b also holds above 14 V while the gauge
reports XDSG or PRECHARGE, so its charge power is at most 1.2567 A x 16.884 V = **21.22 W** (17.59 W at the 14 V threshold).
Beyond it RT1's PTC beside the FETs turns them off (a permanent fail, safe, named).

**R-c.** While the pack cannot discharge (S2, S4), the bridge keeps the kit's load under the envelope's minimum at the measured
input (section 3h) by the shedding sequence of 3g (P1, then the mat on measured headroom); on a source-only brown-out the charger
may latch off (9.3.21.8): the host clears the fault bit when it can, or the operator re-plugs the source.

**R-d.** The image keeps PCHG_COMM 1 and the SUV check (PRIMARY-CONFIGURATION.md), with Q-TI-7 open.

## 5. Is an owner question forced? (out 5)

No. The brief's test is whether REQ-015 as written cannot be met at 9 V by any arrangement because the source path's own
capability caps the power below the required load. The functional sequence the mandatory text asks of a source alone is carried
at 9 V at the plug at its plan figure (3g, CONDITIONAL), and no requirement names a larger load. What the source path admits at a
9.00 V plug, with the kit's losses and VBUS20's other loads (INFERRED; the check's reference without either: 53.9 / 69.79 / 76.96
W):

| Ceiling | Loop | VIN_RAW | at VBAT |
|---|---|---|---|
| F1's 80 C column, 7.3 A, the losses hot | 142.34 mOhm | 7.961 V | 50.99 W |
| F1's 0 C column, 9.8 A, the losses cold | 97.71 mOhm | 8.042 V | 69.73 W |
| a 15 A MINI's 80 C column, 11 A, the losses hot | 142.34 mOhm | 7.434 V | 72.41 W |

These are ceilings with the electronics set to use all of them; the breaker's band and the knee's spread keep the least delivered
figure at 29.09 W. **Against them:** PS-TYP (63.0 W) is over F1's hot ceiling (50.99 W) and under its cold one (69.73 W); the
CONOPS cold warm-up (71.06 W, a cold state, so F1's cold column applies) is over F1's cold ceiling (69.73 W); a 15 A part's hot
ceiling (72.41 W) is over both. So the kit at 9 V with F1 as fitted carries neither PS-TYP hot nor the CONOPS warm-up cold: a
design envelope stated, not a conflict with an approved requirement. REQ-015 states no source current capability, so every
figure takes the source as holding its voltage (named).

## 6. D-06: the vehicle-entry interconnect (out 6)

**The envelope (MAKER, the held 0997 sheet p.3; read monotone, INFERRED).** 110 %: at least 360000 s; 135 %: 0.75 to 600 s;
200 %: 0.15 to 5 s; 350 %: 0.08 to 0.5 s; 600 %: 0.03 to 0.1 s. A larger current clears no later than a smaller one, so a source
can leave:

| Current | For at most | Energy at the interval's top |
|---|---|---|
| up to 13.5 A | no maximum printed: with no time limit | continuous |
| 13.5 to 20 A | 600 s | 240000 A2s (a continuous rating of 20 A covers it) |
| 20 to 35 A | 5 s | 6125 A2s |
| 35 to 60 A | 0.5 s | 1800 A2s |
| 60 A to the specified worst stiff-source current, 900 A (the loop's floor, below) | 0.1 s | the 600 % row bounds it only by 81000 A2s; F1's total clearing I2t at 900 A and 58 V DC is not printed (the sheet's 93 A2s is a typical melting figure), so the elements are judged against it once filed (R-115) |

PWR-003 asks the clearing characteristic to sit below the damage characteristic of the weakest element downstream.

**The elements as drawn (NOT MET):** J_DCIN's VH contact with the drawn AWG 18 lead on the standard header (VH prints 10 A at AWG
16 standard and 7 A at AWG 18 shrouded only: none stated); the D38999 size 16 contact, insert 13-4 (13 A, Amphenol's test
current); F1's holder Keystone 3568 (the catalogue page prints UL ratings of 15, 20 and 30 A for other MINI clips and holders and
none for the 3568); the DC lead, Lapp OLFLEX ROBUST 210 4 x 1.0 or Alpha Wire 25064 (no current rating in either sheet); the
inside lead, 500 mm of AWG 18 (no part, no rating); board E's input bands (10 A declared).

**The options:**

| Option | What it does | Verdict |
|---|---|---|
| (i) rate the interconnect to the whole envelope | every element at least 20 A continuous where installed, the short-time obligations of the table above, and a resistance floor | **selected (SESSION)** |
| (ii) a fuse and protection change | the 7.5 A MINI's 80 C column is 5.1 A. An entry limit whose maximum is 5.1 A has its minimum at 3.942 A for the LM5069 (VCL 48.5 over 61.5 mV, R19 at +-1 %) and at 4.548 A for the selected breaker: both under the in-service 5.983 A at 9 V (and L4-E5's 4.629 A); its own envelope still passes the unrated cable | rejected: it fails 9 V, and leaves the cable unrated |
| (iii) the source's capability stated in REQ-015 (ECSS 6.17.3c) | a requirement change, the owner's | not needed: (i) resolves it in design |

**Selected part classes and their obligations (SESSION; the exact parts Layer 7's and Layer 8's):**

| Element | Selected class | Rating and evidence |
|---|---|---|
| receptacle and plug contacts | MIL-DTL-38999 size 12; insert 17-6 (six size 12: DC and solar pairs on four, the two unassigned between power and return, the ECSS 6.11.3a screen), or 13-26 (two size 12 and six 22D) with the solar pair moved to rated contacts elsewhere | Amphenol prints 23 A as a crimp-contact test current (p.28), not an installed rating: the insert's installed continuous rating of 20 A at the case's air (the maker's derating, or a measured rise) is E11-10; short-time data E11-16 |
| J_DCIN | a board connector of the XT60 class, of the gender opposite J_BATT's so the pack lead cannot mate it, or soldered lead lands | 30 A rated, 60 A instantaneous, 12 AWG recommended (Amass V1.2); the 60 A's duration is unstated: E11-16 |
| F1's holder | a MINI 297/997 holder whose maker prints at least 20 A | the 3568 prints none |
| the interconnect's conductors | cores whose maker states at least 20 A continuous each; the loop specified by its resistance (below) | no sheet held: E11-11, E11-12 |
| board E's copper, J_DCIN to F1 to D10, C4 and Q1 | at least 20 A continuous | a layout constraint, E11-14 |
| F1 | unchanged, Littelfuse 0997010.WXN | 58 V DC, 1000 A at 58 V DC; 7.3 A at 80 C against the selected breaker's 7.136 A (the drawn LM5069's 6.15 A) |

**The withstand obligations (item 4).** Every element the fault current passes (the receptacle and plug contacts, the NATO plug,
the cable's and the inside lead's cores, J_DCIN, F1's holder, board E's copper to F1) carries 20 A continuous (which covers the
envelope to 20 A), 35 A for 5 s and 60 A for 0.5 s, and from 60 A to 900 A has a short-time capability of at least F1's total clearing I2t at 900 A and 58 V
DC. That I2t is not printed; until it is filed the only bound is the 600 % row's 81000 A2s, which no element's held data is shown
to withstand (E11-16 files both sides). The interval tops against an AWG 14 core, adiabatic: 35 A for 5 s 7.07 K, 60 A for 0.5 s
2.08 K, and at 900 A the monotone bound alone 93.47 K, so F1's clearing I2t decides that interval (INFERRED). Against the size 12
contact's 23 A the same I2t equals 11.578 s (35 A for 5 s) and 3.403 s (60 A for 0.5 s) at its test current, which is not a
short-time rating (E11-16).

**The interconnect by its resistance (SESSION; item 4 and the minor on A11-1).** A larger or purer conductor raises a stiff
fault, so the check rests on a measured floor, not on copper constants or on a gauge and a length. The floor is set so the worst
case stays **900 A, 10 % under F1's 1000 A**, on L4-E9's 43.18 V basis (kept: it is over REQ-015's 40 V over-voltage test and the
new entry's OV maximum 41.22 V, which would give 859.1 A on the same floor):

| Item | Value |
|---|---|
| the loop | from the NATO plug's pins to J_DCIN's board pins: the cable, the D38999 pair, the inside lead, J_DCIN |
| its actual resistance at 20 C | at least **56.93 mOhm** (47.98 mOhm at -20 C: 900 A at 43.18 V) and at most **66 mOhm** (the 9 V envelope's basis, 3d) |
| the acceptance | four-wire on every assembly and every replacement, the instrument and fixture within 2 % of reading, the conductor's temperature known within 2 K (2.79 % in all with copper's coefficient), the reading corrected to 20 C: **58.51 to 64.21 mOhm** |
| the selected construction | 3.05 m of AWG 14 with the 0.5 m lead: copper 58.82 mOhm at 20 C, with the D38999 pair and J_DCIN at most 4.75 mOhm more: 58.82 to 63.57 mOhm, inside the window; copper alone reaches the floor from 2.94 m; a reading outside the window is corrected by length |

**The stiff source again** (copper alone at -20 C, the source's resistance zero, A-12, at 43.18 V; INFERRED): as drawn 0.07577
ohm, 569.9 A (L4-E9 569.8 A); AWG 14 at 2.0 m 0.03491 ohm, **1236.9 A against F1's 1000 A, NOT MET**; AWG 12 at 3.05 m 1385 A,
NOT MET; **AWG 14 at 3.05 m 0.04957 ohm, 871 A**; F1's 1000 A alone would need 0.04318 ohm at -20 C (AWG 14 from 2.59 m). The
specified floor keeps 900 A with the margin and the measurement's uncertainty. A shorter or heavier lead needs a fuse with a
larger interrupting rating at 58 V DC, of which no sheet is held. The lowest stiff fault at 9 V with the copper at 62.1 C is
131.3 A, 13.13 times the rating, inside the 600 % row's 0.1 s. **D-06 is resolved in design**, CONDITIONAL on the makers' data
the acceptances name (cable, inside lead, holder, NATO plug, the contacts' installed rating and short-time data, F1's clearing
I2t at 900 A).

## 7. D-09: the hot swap's fault time against its start (out 7)

**This section stands for the LM5069 as drawn.** The selected entry of 3c removes the LM5069 and its timer; `apply_gen_sch_e_timer.py`
is the alternative to `apply_gen_sch_e_entry.py` while the LM5069 stays, and the two drafts refuse each other (SESSION).

**The rows (MAKER, SNVS452G):** VTMRH 3.76 / 4 / 4.16 V, ITIMER 51 / 85 / 120 uA, VCL 48.5 / 55 / 61.5 mV, Equation 9, and TI's
9.2.1.2.4: "TI recommends setting the minimum fault time (tflt) to be greater than the start time (tstart) by adding an
additional margin of 50% of the fault time". The power limit with L4-E9's R24 22k is 22.018 W at 43.18 V and falls with VDS
(Equation 9), which TI notes makes the start "slightly longer".

**The start, recomputed (INFERRED):** the hot swap charges 34 uF, not 31 (NETLIST: board E C6 on DC_HS, C7, C8; board A C11,
C12, and C207 and C210 behind D19 and R196); the resistive load on VIN_RAW is bounded by its resistors alone (R27 with LED1,
R40, R14, R200: 21.8 mA at 43.18 V) plus U2's 10 uA shutdown current. **The front end's own load:** U34 holds U2 off until 79 /
127 / 201 ms after VIN_RAW passes its UV rise (gen_sch_a.py's derivation from SNVSBJ1E), 25.8 times the start's maximum, so the
soft start never overlaps the hot swap's start and the front end's load during it is its bias network. Integrating Equation 12
with the limit following VDS: nominal 1.588 ms (L4-E9 1.324 ms); at the corners (the X7R rows stacked as L4-E9, R24 -1 %, R19
+1 %, the limit over TI's 1.3, VCL's minimum) **3.062 ms**, so the fault time's minimum must be at least **4.593 ms**.

**C5 as drawn** (100 nF K X7R, stacked) gives 2.037 to 11.866 ms: NOT MET. **No single 150 nF C0G part is stocked** (49 rows
read, none in stock at JLCPCB or LCSC; CATALOGUE). The stocked Murata GRM3195 C0G 50 V 1206 parts, read on their makers'
reference sheets (as of Jun.11,2026; held back): 0+-30 ppm/K, Table A +0.58 / -0.24 % at -55 C, endurance +-3 %, damp heat
+-7.5 % (MAKER).

| Candidate (at most two parts, SESSION) | C, nF | fault time, ms (tolerance, temperature, endurance stacked) | start | Figure 10 at its maximum |
|---|---|---|---|---|
| one 100 nF G | 100 | 2.970 to 8.619 | NOT MET | MEETS |
| one 68 nF J | 68 | 1.958 to 6.034 | NOT MET | MEETS |
| two 100 nF G | 200 | 5.939 to 17.239 | MEETS | NOT MET (0.662 A) |
| two 68 nF J | 136 | 3.915 to 12.067 | NOT MET | MEETS |
| **100 nF G with 68 nF J** | **168** | **4.927 to 14.653** | **MEETS** | **MEETS (0.710 A)** |

**Selected (SESSION): C5 GRM3195C1H104GA05D (C907944) with C121 GRM3195C1H683JA05D (C3847777)**, both on HS_TIMER, 1206 (draft
`apply_gen_sch_e_timer.py`; C121 a free designator). Fault time 7.906 ms nominal, 4.927 to 14.653 ms stacked: 0.334 ms over the
4.593 ms margin (MEETS, INFERRED). At the maximum, Q7's Figure 10 at 43.18 V from TI's vector drawing (10 ms 1.879 A, 1 ms 5.055
A, m 0.4299) carried past the 10 ms line by 46.5 % and derated to Q7's 94.3 C case by 0.4454 (L4-E9) allows 0.71 A against
the pulse's 0.675 A (MEETS, CONDITIONAL on the power law past 10 ms and on board E's copper under Q7). Sensitivities: a steeper
law past 10 ms (m 0.5) 0.691 A, MEETS; the damp-heat row stacked instead of endurance 4.699 to 15.293 ms and 0.697 A, MEETS; TI's
own basis (typical values) 7.906 ms against 2.382 ms. The DC line derated (0.271 A) is under the pulse; the pulse ends at the
fault time, so no steady rating is asked of it. *Reversed by:* a measured start (E11-17) longer than 3.285 ms at 43 V, or a
measured fault time outside the band; the alternatives then are a higher power limit (a shorter start against a larger pulse)
or a Q7 with a larger SOA. **D-09 is resolved in design for the LM5069**, CONDITIONAL as stated.

## 7a. The interface, firmware and L4-E5 drafts (text, for Layer 5, the firmware owner and the Layer 4 coordinator)

These replace rows of `HW-FW-CONTRACT.md`, a paragraph of `PANEL.md` and two texts of L4-E5's record; this record edits none of
them.

- **FW-C08 (SHORE_INHIBIT), proposed behaviour:** "Boot low. Asserted only on the operator's 'inputs off' and on the
  water-on-floor isolation, never for a temperature or 'no charge' hold. When the pack cannot discharge (states S2 and S4: the
  gauge's XDSG, no pack, or both FETs open) the bridge first warns that asserting it removes the kit's supply." (as written: "Boot
  low; assert on the bridge's request when the pack reads below 0 C and clear above 3 C, or when the operator sets 'no charge'")
- **FW-A14 (CHG_INHIBIT, HIZ), proposed behaviour:** "Held low (charger enabled) at power-up; asserted only by firmware, never as a
  charge hold, and never while the pack cannot discharge (S2, S4)." (as written: "Held low (charger enabled) at power-up; asserted
  only by firmware")
- **PANEL.md section 10, proposed sentence** in place of "The bridge asks the controller to assert it when the pack temperature
  (...) is below 0 C, when the operator sets 'no charge', and clears it with hysteresis (charge again above 3 C).": "Every charge
  hold (cold, hot, or the operator's 'no charge') is a flag the firmware keeps until its own condition clears it (the cold hold
  above 3 C with hysteresis), whatever the pack's state. While the pack can take charge or discharge, the flag sets the charger's
  CHRG_INHIBIT bit; with both pack FETs open the gauge holds and the bit is left clear, and it is written from the flag the moment a
  FET closes. No hold uses the CHG_INHIBIT line or SHORE_INHIBIT. The bridge asks the controller to assert SHORE_INHIBIT only for
  'inputs off' and the water-on-floor isolation."
- **DCIN_PGD (board E's RP2040 input), proposed meaning** with the selected entry: the entry's fault flag (U6's FLT_I and FLT_T,
  open drain, low on an overcurrent, a short circuit or an overtemperature), no longer a power-good line.
- **New firmware rows:** R-a (the state table of section 4, with S4's exception and the hold's persistence); R-b (ChargeCurrent()
  0x0000 or 0x0200 and no other value while U3's SRN reading is under 14.0 V or the gauge reports XDSG or PRECHARGE); R-c (the
  shedding sequence of 3g, the mat on measured headroom, and the VSYS_UVP recovery); R-d (the image's PCHG_COMM 1 and SUV check).
- **L4-E5's V-A08, proposed text (item 2; E11-21):** "transients, recorded apart from steady state: the vehicle supply stepped 24
  to 12 V, 36 to 9 V and 12 to 24 V, plugged and unplugged, and a panel simulator stepped from 100 W into the stage to 50, 30 and
  10 W and back, each under U3's full demand: the entry's U6 never asserts FLT_I (its current over the breaker's lowest 6.36 A
  for less than 0.247 ms, its filtered short-circuit sense under 10.36 A), VIN_RAW never falls below 7.24 V (the guard's highest
  fall 7.14 V plus 0.1 V), FE_PGOOD never drops; the peak and settling time of U3's input current and of the entry's current
  recorded" (as written: "... the LM5069's TIMER never reaches 3.76 V, VIN_RAW never falls below 8.41 V (the guard's highest 8.31 V
  plus 0.1 V), FE_PGOOD never drops; the peak and settling time of U3's input current recorded").
- **L4-E5's source-change row, proposed transient cell:** "The pin is read continuously (p.6) and acts through U3's input loop and
  the front end's loop (crossover 0.71 to 3.6 kHz, gen_sch_a.py, MODELED). U3's loop response is not printed: INCONCLUSIVE. It
  must keep the entry's current under the breaker's lowest 6.36 A except for excursions shorter than its 0.247 ms minimum delay,
  and its filtered short-circuit sense under 10.36 A at all times, and keep VIN_RAW above 7.24 V (V-A08)." (as written: "... It
  must beat the entry's 3.13 ms fault timeout and keep VIN_RAW above 8.41 V, the guard's highest 8.31 V plus 0.1 V (V-A08)").
  The old millisecond allowance cannot stand against the new breaker's 0.247 ms minimum delay.

## 7b. The CONOPS statement (draft, for the CONOPS owner)

"With no usable pack (absent, at its cutoff, or cold-soaked with its FETs open) the kit runs from its vehicle or shore input
within the source envelope at its input plug: about 29 W at 9 V, 32 W at 12 V and 70 W at 24 V on its bus at the least. At 9 V
it sheds to one module with its fans, HF, Geiger and 5G modules held and runs the pack heater on the headroom left, which warms a
cold-soaked pack at the plan load; the time is measured on the prototype. A pack self-discharged under about 2.4 V a cell holds
the system node under the converters' floor while it pre-charges, so the kit's loads wait for it. A brown-out on the input alone
may latch the charger off until the input is re-plugged."

## 8. The downstream items (out 8)

An owner and an acceptance close the assignment, not the item.

| ID | Kind | Owner | Acceptance |
|---|---|---|---|
| E11-01 | implementation | Layer 8 board E generator owner | `apply_gen_sch_e_entry.py` after L4-E9's `apply_gen_sch_e_hotswap.py`, instead of `apply_gen_sch_e_timer.py`: U6 TPS48110AQDGXRQ1, Q7 CSD19536KTT, R19 4.5 mOhm, L2 SRF1260-1R0Y and the network of 3c; the DGX-19 land added to meshsat.pretty from TI's DGX0019A drawing and the D2PAK land checked against TI's KTT drawing; _VEH_T restated to 7.14 A; the regenerated netlist reads every value of 3c |
| E11-02 | implementation | Layer 8 board A generator owner | `apply_gen_sch_a_guard.py` with the corrected knee (E11-09): R14 76.8k (C23107); U34's fall from the fitted parts 6.75 to 7.14 V |
| E11-03 | interface | Layer 5 interfaces | FW-C08, FW-A14 and PANEL.md section 10 restated as section 7a (R-a's state table, S4's exception, the hold's persistence); DCIN_PGD restated as the entry's fault flag; REQ-046's hold still clears above 3 C |
| E11-04 | firmware | firmware owner | rules R-a to R-d implemented (section 7a) and checked on the bench (E11-06) |
| E11-05 | evidence | Layer 6 components | TI's answers filed: Q-TI-3 restated as N2 for S2 (VSYS's regulation with CHRG_INHIBIT = 1 while the pack can take charge but cannot discharge, under a 5 A load step) and N1, and Q-TI-2; not needed once E11-27 is applied (SLUSE65A prints the bounds, section 12) |
| E11-06 | test | prototype bench | R-85 extended: at 9.00 V at the plug with the interconnect at its resistance ceiling, and at 12 and 24 V: the shedding sequence of 3g (P0 to P3) with the pack cold-soaked (S4), at a warm CUV (S2, the charge held by the bit: VSYS stays up) and absent; P1's load at most 20.51 W at VBAT; the front end's efficiency at the operating point at least 0.8802; U3's board current at the knee's flat target inside its band; the entry's current over the kit's load steps and source changes above the breaker's lowest 6.36 A for less than 0.247 ms and its filtered short-circuit sense under 10.36 A; VSYS's step response; Q2's case at R-b's current; the latch recovery by a re-plug |
| E11-07 | analysis | Layer 9 pre-layout analysis | VSYS's effective capacitance at 16.884 V from the makers' DC-bias curves at least 50 uF, or the direct EEHZK1V181P of E11-24, which gives it by design |
| E11-08 | evidence | Layer 9 pre-layout analysis | every load converter's and the controllers' minimum input against 10.0 V (A-14, R-49) and 8.0 V |
| E11-09 | analysis | Layer 4 coordinator | L4-E5's undrawn H3 network drawn to 3f's specification (flat 1.82 A from 7.95 V to 10.549 V, zero 7.657 V, HIZ certain below 7.378 V) with E11-02's guard; L4-E5's low-light settle, the solar line and its V-A09 sweep re-run on it |
| E11-10 | implementation | Layer 7 mechanical | the DC receptacle and plug on size 12 contacts (17-6, or 13-26 with the solar pair elsewhere) with the insert's installed continuous rating of 20 A at the case's air filed; the plate cut-out checked against CASE-MARGINS 3.3 |
| E11-11 | implementation | Layer 7 mechanical | the DC interconnect's loop, NATO plug pins to J_DCIN's board pins, read four-wire (2 % of reading, the temperature within 2 K, corrected to 20 C) at 58.51 to 64.21 mOhm on every assembly and replacement (the actual floor 56.93 mOhm keeps a stiff source under 900 A); cores and the NATO plug with a maker's rating of at least 20 A; sheets filed |
| E11-12 | implementation | Layer 7 mechanical | the inside lead (at least 20 A) and J_DCIN at least 20 A (XT60 class, gender opposite J_BATT's, or soldered lands); board E's generator names the part |
| E11-13 | implementation | Layer 8 board E generator owner | F1's holder with a maker's rating of at least 20 A; its sheet filed |
| E11-14 | layout | Layer 9 pre-layout analysis | board E's copper from J_DCIN through F1 to D10, C4 and Q1 at 20 A continuous, and Q7's D2PAK land with its copper |
| E11-15 | implementation | Layer 8 board E generator owner | `pcb_energy_chain.yaml` SHORE_INPUT restated with L4-E9's R-95: conductor 20 A, the breaker's 7.14 A, prospective high 900 A (the specified floor's worst case) |
| E11-16 | evidence | Layer 6 components | F1's total clearing I2t at 900 A and 58 V DC (R-115), and against it and against the monotone envelope (35 A for 5 s, 60 A for 0.5 s) the short-time withstand of every element the fault passes: the size 12 contacts, the NATO plug, the cable's and the inside lead's cores, J_DCIN, F1's holder and board E's copper to F1; filed |
| E11-17 | test | prototype bench | R-118 for the selected entry at 43 V, the trip thresholds apart from the peak currents: the start inside 2.5 ms with at most 1.22 A; the thresholds on a slow ramp (overcurrent 6.36 to 7.14 A after 0.247 to 0.49 ms, short circuit 10.36 to 13.87 A on the filtered sense); the peaks recorded and held under the chart: a start into a resistive fault near 1.2 Ohm, a start into a hard short (at most 73 A), Q7 unharmed; with the LM5069 kept, D-09's rows (4.927 to 14.653 ms, the start inside 3.062 ms) |
| E11-18 | document | CONOPS owner | section 7b's statement in CONOPS |
| E11-19 | analysis | Layer 4 coordinator | L4-E9's entry findings that rest on the LM5069 (IF-05's hot short, D-07's power limit, R-118, the start's I2t) re-judged for the selected entry |
| E11-20 | evidence | Layer 9 pre-layout analysis | a hard short in service: the loop inductance from the source to a fault on DC_HS or VIN_RAW at least 2.08 uH, or the peak through Q7 measured at most 178 A (its IDM derated), the threshold (10.36 to 13.87 A) being only where the turn-off begins; with L4-E9's open item |
| E11-21 | interface | Layer 4 coordinator | L4-E5's V-A08 and its source-change transient cell restated as section 7a's drafts: the breaker never trips (over 6.36 A for less than 0.247 ms, the filtered sense under 10.36 A) and VIN_RAW never under 7.24 V |
| E11-22 | evidence | Layer 6 components | R-b's cases (ii) and (iii) closed: the charger's temperature while R-b holds bounded inside 0 to 85 C (Layer 9 thermal), or TI's 0x0200 accuracy outside it and the clamp's maximum under VSYS_MIN (Q-TI), or the bench's current at 0x0200 and under VSYS_MIN at the inside air's ends; board P's copper under Q2 for TI's 50 C/W |
| E11-23 | test | prototype bench | TEST-PLAN E4-O at the plug: the kit cold-soaked at -20 C with the pack inside, started from 9.00 V at the plug through the interconnect at its ceiling; the shedding sequence of 3g runs, the mat on measured headroom: the cells reach 3 C, the hold clears and the charge begins; the time recorded and accepted against CONOPS's warm-up |
| E11-24 | implementation | Layer 8 board A generator owner | the dependency round's fallback on VBAT (a register row, never applied by this record): one EEHZK1V181P direct (C242139) and a hold-up bank of four EEHZK1E471P (C242138) charged through R_CH 330 Ohm RC2512FK-07330RL (C137025) and discharging through D_H B540C-13-F (C72264); the regenerated netlist carries them; the bank's hold recomputed from the fitted parts reads at least 1.117 ms for the worst admitted step (48.39 W); withdrawn once E11-27 is applied (section 14) |
| E11-25 | evidence | Layer 6 components | the questions of `clarification/TI-QUESTIONS.md` (Q-TI-11 to Q-TI-14, the addendum to Q-TI-3) sent by the owner and answered, each answer filed against its row D1 to D10 and judged: a limit closes a row production-wide, a typical figure does not |
| E11-26 | test | prototype bench | the bench methods of rows D1 to D10 run on one unit each, every reading filed as a sample with its uncertainty and conditions, never as a limit; D2's recovery at most 0.2 ms against the bank's 1 ms assumption gives the engineering margin section 11 names |
| E11-27 | implementation | Layer 8 board A generator owner | `apply_gen_sch_a_charger.py` applied (sections 14 and 15): U3 BQ25730RSNR (C5219071) with pin 21 on CH_BATDRV; Q39 and Q40, two Nexperia BUK6Y10-30PX (C3278350) in parallel, sources on VBAT, drains on CH_BATQ, gates on CH_BATDRV; R17 and R149 on CH_BATQ; C236 EEHZK1V181P (C242139) on VBAT; U42 TPS16630PWPR from VBAT to VSYS_DOCK with R221 11k 0.1 %, C237 22 nF and MODE to GND, J_DOCK pin 1 on VSYS_DOCK for board E's VSYS_E (section 16e), the HTSSOP-20 land checked against TI's PWP0020 drawing; CH_BATQ declared a segment of the pack path; the LFPAK56 lands checked against Nexperia's SOT669 drawing, seated by R17 with matched paths; the regenerated netlist reads each |
| E11-28 | firmware | firmware owner | the BQ25730's register rules: EN_OOA 0 at boot; ChargeCurrent written for any charge (0 A at POR and after the watchdog's 175 s), the watchdog serviced or WDTMR_ADJ 00; VSYS_MIN, EN_LDO, EN_PORT_CTRL, BATFET_ENZ and BATFETOFF_HIZ never written from their power-on values; the device ID D5h checked; R-a's bit following the hold flag in every state (S4's exception withdrawn); R-b' under VSYS_MIN: 0x0080 only, and no charge under 5.7 V on SRN (section 15c) |
| E11-29 | layout | Layer 9 pre-layout analysis | the installed pair Q39 and Q40 (section 16b): each FET's self impedance and the mutual one, junction to air by the body diode's VSD method on the built board, at the +70 C mixed air or referred to it: (Zself + Zmut) at most 33.12 K/W steady and at 60 s, 10.753 at 1 s, 3.785 at 20 ms and 0.703 K/W at 244 us (at the allowance of E11-36); the 18 A for 60 s and 10 A continuous kept, no protection lowered; the case-rise reading at 10 A alone does not close it |
| E11-30 | evidence | Layer 6 components | the docking pulse through one FET's body diode with no sharing credited (section 16d, 242.9 A peak, time constant 33.8 us, from +70 C): VF at the pulse's currents at a +70 C mounting base at most 1.501 times max(1.2 V, 1.2 V x i / 80 A) (pulsed VSD on parts from the lot, or Nexperia's curve), and ISM's 320 A amplitude at a mounting base of +70 C, with the waveform past ISM's 10 us judged on TJ alone, from Nexperia or a pulse test on parts; or board P's owner constrains the pulse with a slower discharge-FET turn-on whose turn-off under ASCD is shown unchanged |
| E11-31 | test | prototype bench | the three modes on the BQ25730 build (EN_OOA 0), piecewise (section 15d): pack absent, VSYS at least 12.054 V; CHRG_INHIBIT 1 with SRN over 12.546 V, VSRN plus 150 mV within 2 percent, under 12.054 V at least 12.054 V, between at least 11.96 V; the held pack current at most 1 mA with board E on VSYS_E; the start from cold at VBUS20 19.15 and 20.96 V, VSYS's maximum capacitance and the always-on loads, at -20, 25 and 62.1 C, with Fault VSYS_UVP clear, the hiccup and latch on a shorted VSYS and the re-plug; VSYS before EN_OOA's write recorded; VSYS's step response in S2 and S4 for each declared step against the converters' floor (D2, 2.054 V of margin), the outlets held by R-c where a step uses more |
| E11-32 | evidence | Layer 6 components | the BQ25730RSNR's supply for the build quantity from an authorised source, filed (LCSC stock 0 on 2 October 2026), and the two battery FETs' (BUK6Y10-30PX, LCSC stock 67) |
| E11-33 | implementation | Layer 8 board E generator owner | `apply_gen_sch_e_aux.py` applied with E11-27 (section 15a): J_BLK pin 1 on VSYS_E; U12's VIN and EN, C31, J_FAN1 and J_FAN2 pin 1 and D7 and D8 on VSYS_E; VSYS_E declared (source J_BLK, 1 A: U12 0.8, the fans 0.1 each, always on); CELL_F's loads the pack path alone; E6_SW, E6_BST and the fans' switched returns re-declared to VSYS's 17.375 V; the regenerated netlist and check_contracts read the dock's pin 1 as VSYS_DOCK and VSYS_E |
| E11-34 | interface | Layer 4 coordinator | `apply_pcb_interfaces_dock.py` applied (IF-AE-DOCK: pin 1 VSYS_DOCK and VSYS_E behind U42's eFuse, the alias, BAT-F06's charge_share replaced by the VSYS feed, the ground return with seven 813 contacts) and section 15e's texts for L4-E9's record: the IF rows of VBAT and the dock, the source-change rows, the two sentences that say no battery FET and the diagram's system-node label (9.688 to 17.375 V) |
| E11-35 | evidence | Layer 6 components | the mixer fans' supply range from their maker: at least 17.375 V at the top (VSYS_E's top; CELL_F reached 16.884 V) and running at 9.539 V or less at the bottom (VSYS_E's least with 1.0 A, section 16e), and their starting current, with U12's 0.8 A, under U42's least limit 1.471 A; or a fan of that range named |
| E11-36 | evidence | Layer 6 components | the battery FETs' RDS(on) at VGS -8.5 V and a 150 C junction at most 21.136 mOhm (the allowance of section 16a): Nexperia's maximum at that point filed, or a pulsed Kelvin reading on parts from the build lot in an oven at 150 C (a sample, not a production limit: only the maker's maximum closes it for every part); a reading over it reverses the allowance and E11-29 is re-sized before layout |
| E11-37 | evidence | Layer 6 components | TI's statement of what the BATFET's 5 nF bounds (Ciss at which VDS, or a gate charge; Q-TI-17, drafted in `clarification/TI-QUESTIONS.md`, not sent), or the bench's BATDRV behaviour with the pair at -20, 25 and 70 C: supplement entry, the ideal diode's 30 mV regulation without oscillation and LDO mode at VSYS_MIN within its printed band; on a negative answer the engineer chooses between the pair and one FET with a heat path through the case (section 16c) |
| E11-38 | test | prototype bench | the dock's VSYS branch (section 16e): U42's limit read on a slow ramp between 1.471 and 1.802 A at -20, 25 and 70 C; the 2.88 Ohm overload and a hard short at board E's VSYS_E, the peak through J_DOCK pin 1 recorded and the auto-retry seen; the contact's resistance unchanged after the shorts; VSYS_E at least 9.539 V at 1.0 A with VSYS at 9.688 V |

## 9. What stays conditional, and the decisions this record takes

**Conditional or open (named):** U-04: REQ-015 at 9.00 V at the plug is a CONDITIONAL CANDIDATE (3g: E11-06, E11-09, E11-23,
E11-05, E11-22); N1 (VSYS under load steps with no battery: TI and E11-06; the only item that could still change the charger),
**N2 for state S2** (OPEN), N3, N4 (E11-07), N5 (E11-08), N6 (Q-TI-7); the front end's efficiency at 8.1 V (0.880 or more, C-8);
the pin's real band (L4-E5's 0.2 A, INFERRED); the input current's transients against the breaker's 0.247 ms (E11-06, E11-21);
the load's hi corner (P1 measured at most 20.51 W); the cells' warming time (E11-23); R-b's cases (ii) and (iii) and Q2's
installed thermal path (E11-22); a deeply discharged pack's wait (E11-06); the start into a hard short (the transconductance
bound) and the hot-short peak in service (E11-20); REQ-015's unstated source capability. D-06: the cable's, inside lead's,
holder's and NATO plug's makers' ratings (E11-11 to E11-13), the contacts' installed rating and short-time data (E11-10, E11-16),
F1's total clearing I2t at 900 A (R-115), the plate's fit for shell 17 (E11-10). D-09 (for the LM5069): Figure 10 past 10 ms,
board E's copper under Q7, the X7R stack for every start capacitor (an ASSUMPTION, as L4-E9), Murata's sheet as fetched.

**SESSION decisions:** (1) U-04: arrangement (A) with rules R-a to R-d, R-a a state table with S4's exception and a persistent
hold; (2) the entry replaced: TPS48110-Q1 with a CSD19536KTT, R19 4.5 mOhm, L2 SRF1260-1R0Y and the network of 3c (the first
round's R21 42.2k withdrawn); (3) REQ-015's 9 V taken at the kit's plug as the design basis (U4-F3); (4) the corrected knee's
flat 1.82 A from 7.95 V (final round, from 1.89 A: the margin to the breaker); (5) the guard's R14 76.8k; (6) the shedding
sequence of 3g (P1's held loads, the mat on measured headroom); (7) R-b's two settings and its 14.0 V threshold; (8) D-06:
every element of the interconnect at 20 A or more continuous where installed, with the classes of section 6; (9) the
interconnect by its loop resistance: the actual floor 56.93 mOhm for 900 A, 10 % under F1's 1000 A, the ceiling 66 mOhm, the
acceptance 58.51 to 64.21 mOhm with 2 % and 2 K, the construction 3.05 m; (10) insert 17-6 preferred to 13-26; (11) J_DCIN of the
gender opposite J_BATT's; (12) D-09: C5 and C121, at most two parts, for the LM5069; (13) the dependency round's fallback: the
direct EEHZK1V181P and the isolated hold-up bank of four EEHZK1E471P, R_CH 330 Ohm and D_H B540C (section 11a), isolated so the
pack's inrush stays under ASCD; (14) the consolidation (section 14), superseding (1)'s arrangement and (13)'s bank once E11-27 is applied: arrangement (B1), TI's BQ25730 with the battery FET Q39
AONS21357 and the direct can C236, the bank withdrawn; rule R-b' (ChargeCurrent 0x0080 under VSYS_MIN, no charge under 7.8 V on
SRN); EN_OOA 0 at boot; the battery FET's registers left at POR; R-a without S4's exception; CELL_BATPRESZ never tied to battery
presence; (15) the fix round (section 15): board E's auxiliary domain on VSYS over one 813 contact (pin 1), the battery FETs two
Nexperia BUK6Y10-30P in parallel (Q39, Q40), RDS(on) bounded at BATDRV's 8.5 V by `fet_bound`, the junction limit 150 C, the +70 C
air line, R-b' revised to no charge under 5.7 V on SRN, the held pack current's bench acceptance 1 mA. Each carries its reason and reversal above. **Conditional with (B1) (named):** Q39's installed thermal path (E11-29),
its docking pulse (E11-30), D2 (E11-31), the BQ25730's supply (E11-32), VSYS_MIN's upper accuracy (A11-18).

**The gate's view (for the coordinator, not decided here):** U-04 moves from "unresolved by the held documents" to a selected
arrangement whose 9 V at the plug is a CONDITIONAL CANDIDATE on the evidence named; D-06 stays resolved in design with the
envelope carried to 900 A; D-09 stays resolved for the LM5069, the alternative to the selected entry. After the consolidation
round, U-04 with (B1) applied is a downstream qualification test with bounded evidence and a workable fallback (section 14).

## 10. Assumptions

| ID | Assumption | Impact if wrong | Verification |
|---|---|---|---|
| A11-1 | The stiff-source check rests on the interconnect's measured loop (its actual floor 56.93 mOhm at 20 C, read with 2 % and 2 K), with copper's 0.00393 /K for the temperature only; AWG 14's 2.081 mm2 describes one construction inside the window, not the check | a loop under the floor passes more than 900 A | E11-11 (each assembly measured) |
| A11-2 | The budget's battery-terminal watts taken at VBAT | a small overstatement of each state | E11-06 |
| A11-3 | Q2's VSD at most 1 V at R-b's current, from its 50 A row; board P's copper giving 50 C/W | Q2's rise under R-b | E11-22, E11-06 |
| A11-4 | The start's capacitors at the Yageo X7R rows stacked, for parts of other makers too | the start's corner | E11-17 |
| A11-5 | Each VIN_RAW load path bounded by its resistor alone | the start a little shorter in fact | E11-17 |
| A11-6 | The loss model's unprinted elements: MOSFETs at 1.8 times their 25 C maximum hot, the NATO plug's contacts as size 12 contacts, the holder 1 mOhm, board copper and the dock's pins 5 mOhm, F1 at its typical rated-current drop | the 9 V operating point and the breaker's 6.4 % | E11-06 |
| A11-7 | The power law between Figure 10's 1 and 10 ms lines carried past 10 ms (as L4-E9); a fault start judged with every point held against the chart for the whole pulse, derated by L4-E9's 0.4454 | the timer's maximum (D-09) and the fault starts (3c) against the charts | E11-17, R-118 |
| A11-8 | The 22 nF, 10 nF and 1 nF C0G parts on the GRM3195 family's rows held for the 100 nF and 68 nF parts | the breaker's delay, the slew and the filter within a few percent | E11-17 |
| A11-9 | The front end at 0.93 at 8.1 V (L4-E5's figure, C-8) | the in-service maximum against the breaker's lowest (floor 0.880) | E11-06 |
| A11-10 | TI's typical transconductance (329 S at 100 A) taken as the bound on a hard short's current rise at the start | the start into a hard short (73.4 A, 0.743) | E11-17 |
| A11-11 | The overcurrent delay's maximum: Equation 7's maximum scaled by TI's loaded row over Equation 7 (1.149) | the longest fault pulse | E11-17 |
| A11-12 | P1's held loads (the mixer fans, HF, Geiger, 5G) each have a switch the bridge or the controllers drive | the shed state's figures | E11-03, E11-06 |
| A11-13 | The charger restores VSYS within 1 ms of a step with no battery (T_RESP) | the bank's 1.117 ms against the worst admitted step | E11-26 (D2) |
| A11-14 | A hybrid polymer can keeps 0.9 of its 20 C capacitance at -20 C (the ZK sheet prints none) | the bank's energy | E11-26 |
| A11-15 | A Schottky's forward drop rises 0.1 V from 25 C to -20 C | the bank's lowest useful voltage | E11-26 |
| A11-16 | The slot rail's efficiency 0.90 (+5V_DEV's declared figure) | the slot step at VSYS | E11-26 |
| A11-17 | The kit's declared load steps are r4a's session targets (INFERRED there), the largest a rail takes at once | the worst admitted step | E11-06, E11-26 |
| A11-18 | VSYS_MIN_REG_ACC's maximum, printed -2 % (SLUSE65A p.10), read as +2 % (12.546 V) | Q39's LDO-mode heat and the 7.8 V floor of R-b', by a few tenths of a volt | E11-31 |
| A11-19 | Q39's RDS(on) at its 125 C maximum (10.7 mOhm) held up to 150 C (the first selection's; withdrawn by 15c, which judges no option above its last printed row) | Q39's junction at the pack's protection currents | E11-29 |
| A11-21 | The board's transient shape for every candidate taken from AOS Figure 14 over its steady 55 C/W (a 5 x 6 mm class on a 1 in2 2 oz board) | the bars of 15c for events under 60 s | E11-29 |
| A11-22 | ISM derated linearly from 25 C to the 175 C rating at the inside air | the docking pulse's hot share, 0.848 | E11-30 |
| A11-20 | The docking inrush taken as the dependency round's model (the discharge FET at once, no diode drop credited) | Q39's peak, an overstatement if the gauge's DSG rise limits it | E11-30 |


## 11. The dependency round: each missing specification, the claim it decides, who can settle it (2 October 2026; out 9 to 11)

**The owner's instruction (2 October 2026):** separate each missing specification from the engineering claim it affects; state
what a manufacturer's answer would establish and what a bench test could; a measurement on one sample must not become a
production-wide bound; evaluate a bounded engineering fallback where worthwhile. The rows below are every
specification this record leaves to a maker (TI for all but D5). Their figures are printed in out 9. **A correction found on
the way:** ChargeCurrent()'s value at POR is 256 mA, not 0 A: TI's expert on E2E thread 1316778 (held) states the register
description's 0 A is in error. Section 2 and section 4's hold persistence are corrected; the persistence argument already covered
the window (only the gauge's window acts until the firmware writes the flag's bit), and 256 mA is under R-b's bound.

| Row | The missing statement (the held sheet, its page) | The claim it affects (this record) | What a maker's answer would establish | What one bench sample could establish, and what it cannot | The bench method | If the answer is negative |
|---|---|---|---|---|---|---|
| D1, N1a | VSYS's DC regulation with no battery current: VBAT_REG_ACC +-0.5 % is a charge-voltage row at 0 to 85 C (SLUSE66A p.9); section 11 (p.92) says only that the system is powered through the charger; Figures 10-4 and 10-5 (p.89) are typical power-up curves without battery | line 152: section 2's "absent, or both FETs open: VSYS at ChargeVoltage", and every S4 figure of 3g and 3h | that the loop holds VSYS at ChargeVoltage with no battery current, the +-0.5 % row applying: production-wide if stated as a limit | **can:** that one unit enters and holds the mode at the conditions tried; the mode is a design behaviour, and VSYS needs only 12.3 V against ChargeVoltage's floor 16.716 V, a 4.416 V margin, large against any plausible spread once the mode is shown. **Cannot:** that every unit and silicon revision enters the mode, or the accuracy below 0 C | pack absent, P1's load and the envelope's maximum on VSYS, VBUS20 19.1 to 21 V, VSYS on a calibrated meter at -20, 25 and 62 C ambient | (A) cannot run S4: (B), a charger whose battery FET regulates VSYS by design (an architecture change; five records reopen) |
| D2, N1b | VSYS's load-step response with no battery: no load-transient figure or limit for the system output (Figure 10-17, p.91, is the OTG output's) | line 406: R-c and 3g's S4 operation through the kit's load steps, up to 48.39 W | a characterised deviation and recovery, or a minimum loop bandwidth; production-wide only if TI states a limit | **can:** one unit's deviation and recovery; with the bank sized for 1 ms, a measured recovery of 0.2 ms or less is a five-fold engineering margin against a loop's plausible spread. **Cannot:** a recovery time bounded for every unit | pack absent, an electronic load stepping VSYS by each declared step with a 1 us edge, VSYS and the inductor current on a scope, at three ambients | the bank of out 10 carries the worst admitted step for 1.117 ms with no help from the charger; longer needs more cans (8 for 2 ms) or (B) |
| D3, N2 (Q-TI-3) | VSYS with CHRG_INHIBIT = 1 or ChargeCurrent 0 and no battery current: 9.4.1 (p.35) lets the host end a charge either way; 9.3.21.5 (p.34) keeps the converter operating with charge disabled only in the BATOVP paragraph | line 373: R-a's S2 row, and REQ-077's hold in every state: the charger still carrying the kit while the charge is held | the control mode with charge inhibited, production-wide (a design behaviour) | **can:** one unit's mode with the bit set and with ChargeCurrent 0, pack absent and in S2: a deterministic logic behaviour, so strong evidence for that silicon revision. **Cannot:** that no later revision changes the mode, nor a temperature-dependent comparator's effect | the pack emulated in S2 (a supply behind a diode), the bit set and cleared under P1's load, VSYS and the switch node recorded | REQ-077's hold cannot use the bit with this charger; ChargeCurrent 0 is tried; if both fail, (B) or a change to REQ-077's acceptance (the owner's) |
| D4, N3 (Q-TI-2) | whether it charges before any host write: 9.6.3 says on a host write; the reset value encodes 256 mA; TI's expert on E2E (held): the POR value is 256 mA, 9.6.3 not addressed | line 139: section 2's ChargeCurrent at POR, R-a's persistence after a charger POR, CONOPS's hostless 256 mA | a datasheet erratum: production-wide (a forum answer is TI's word, not a revised document) | **can:** one unit's SRP-SRN current after POR with no host: a logic behaviour, strong for that revision. **Cannot:** other revisions | no host, the pack at 3.6 V a cell, SRP-SRN read for 200 s after POR | a hostless 256 mA charge is safe (inside the gauge's window; Q2's diode 0.256 W); no hostless charge leaves a hostless kit's dead pack uncharged: a stated limitation |
| D5, N4 | VSYS's effective capacitance at 16.884 V against TI's 50 uF (10.1, p.83): the fitted MLCCs' DC-bias capacitance is not printed in the held Yageo CC sheet (a capacitor maker's item) | line 605: N1's premise and E11-07 | the capacitor makers' DC-bias curves: typical per part number, not limits | **can:** one board's VSYS capacitance at 16.8 V of bias. **Cannot:** lot-to-lot spread | an LCR meter with DC bias on the populated node | none needed: the direct EEHZK1V181P gives 90.72 uF at its stacked worst, no DC-bias dependence, over 50 uF by design |
| D6, Q-TI-7 | 0-V charging before the gauge's SUV check: SLUUAQ3A 4.9 enables the 0-V circuit with PCHG_COMM = 1; its timing against 3.2.1's SUV check is not stated | line 410: R-d: no cell below 1.0 V charged (Samsung) | the gauge's sequence, production-wide | **can:** one gauge with a cell simulator: a logic sequence, strong for that firmware. **Cannot:** other firmware revisions | a cell simulator at 0.8 V a cell, the charger enabled, the stack current logged from wake | ZVCHG Exit Threshold set to stop 0-V charging, or a precharge FET with PCHG_COMM 0 (arrangement (C)'s part) |
| D7 | the clamp's maximum under VSYS_MIN: 384 mA typical only (SLUSE66A 8.5, p.10) | line 397: R-b's case (iii), Q2's diode below VSYS_MIN | a maximum, production-wide | **can:** one unit's clamp current; Q2 reaches 150 C only at 1.758 A on its 50 C/W, 4.58 times the typical clamp, so a sample near typical is a large engineering margin. **Cannot:** a maximum | SRN held at 11 V by a sink, 0x0200 set, the current read at three temperatures | a maximum over 1.758 A: Q2's copper improved, or arrangement (C) |
| D8 | ChargeCurrent's accuracy at 0x0200 outside 0 to 85 C, and under 0x0200 (p.10) | line 396: R-b's case (ii), Q2's 124.9 C (CONDITIONAL) | limits outside the range, production-wide | **can:** one unit at -20 and 62 C; Q2's limit 1.758 A is 1.4 times R-b's 1.2567 A, so a sample within about 1.3 A is an engineering margin. **Cannot:** production limits | as D7 with SRN at 13 V | the charger's temperature bounded inside the row by layout (E11-22), or Q2's copper improved |
| D9 | the TPS48110-Q1's overcurrent delay at CTMR 22 nF: 370 us typical only (SLUSEE5E p.10) | line 210: V-A08's 0.247 ms and the fault scan's 0.49 ms (A11-11) | a minimum and a maximum over temperature, production-wide | **can:** one unit's delay; the scan's worst fault ends on the short-circuit trip, so the maximum does not decide it; the minimum sets V-A08. **Cannot:** the spread | a current step over the threshold at three temperatures, sense to PD timed | V-A08's allowance re-derived on TI's minimum, or CTMR raised |
| D10 | the CSD19536KTT's transconductance: 329 S typical only (SLPS540C p.3) | line 228: the start into a hard short, 0.743 of the derated chart | a maximum, or the transfer curve's spread | **can:** one unit's transfer curve; the 1.346-fold headroom is not large against a plausible spread, so **no** margin. **Cannot:** a bound across units | a pulsed transfer curve at VDS 10 V, 10 to 100 A | a slower gate slew for the start, or a power-limiting controller |

### 11a. The bounded fallback: VSYS's hold-up with no battery that does not lean on the charger's transient response (out 10)

**The criterion.** With no battery (S4) VSYS sits at ChargeVoltage, at least 16.716 V (16.8 V less TI's 0.5 %), and must stay above
VSYS_MIN 12.3 V through a step while the charger delivers only its pre-step power for **1 ms (ASSUMPTION: the time the charger could
take to respond; D2's bench reading makes it a margin)**. No VSYS divider sets a higher line: the VBAT stages' EN/UVLO pins are
driven by logic, the heater buck starts at about 7.3 V, and A-14's assumed 10.0 V converter floor is under VSYS_MIN.

**The kit's own steps** (r4a's loop design, recovered by L4-E8, session targets INFERRED there; efficiencies from gen_sch_a.py; the
mat from hc2), at VSYS, and whether R-c's envelope admits each on top of P1's plan (19.57 W) at the widest source (36 V, 84.55 W):

| Step | At VSYS | In S4 | Held by the fallback |
|---|---|---|---|
| slot rail +5V_S2, 3 A at 5.09 V (a 5G burst; 0.90 ASSUMPTION) | 16.97 W | admitted | 3.187 ms |
| device rail +5V_DEV, 3 A at 5.09 V | 16.97 W | admitted | 3.187 ms |
| PA rail, 5.4 A at 13.76 V (a 30 W carrier keyed) | 79.9 W | not admitted (R-c holds it) | 0.677 ms |
| HF rail, 2 A at 12 V | 25.81 W | admitted | 2.095 ms |
| PoE rail, 0.6 A at 54 V | 36.82 W | admitted | 1.469 ms |
| USB-C PD outlet, 3 A at 15 V | **48.39 W** | admitted (the worst) | **1.117 ms** |
| the pack heater mat, regulated | 8.5 W | admitted | 6.361 ms |

**The fallback (SESSION; a register row, E11-24, never applied):** one Panasonic **EEHZK1V181P** directly on VSYS (180 uF 35 V,
C242139), and a **hold-up bank of four EEHZK1E471P** (470 uF 25 V, C242138) charged from VSYS through **R_CH 330 Ohm** (Yageo
RC2512FK-07330RL, 1 W at 70 C, C137025) and discharging into VSYS through **D_H, a Diodes B540C-13-F** (40 V, 5 A, VF at most
0.55 V at 5 A and 25 C, C72264). **The derating:** the Panasonic ZK sheet's +-20 % tolerance and endurance within +-30 %, no DC-bias
dependence (an aluminium hybrid polymer part), the low-temperature change not printed (0.9 at -20 C, ASSUMPTION): 0.504 of nominal at
the stacked worst. The bank (947.5 uF effective) sits at 16.561 V (the leakage across R_CH) and gives into VSYS down to 12.95 V
(VSYS_MIN plus D_H's 0.65 V, its 25 C maximum plus 0.1 V cold, ASSUMPTION): 48.26 mJ net of the diode; the direct can (90.72 uF
effective) 5.81 mJ; **54.07 mJ in all, the MLCCs not counted. Against the worst admitted step: 1.117 ms of hold over the 1 ms
assumed** (CONDITIONAL on that assumption); the least cans for 0.25, 0.5, 1, 2 and 5 ms: 1, 2, 4, 8 and 20.

**Feasibility:**
- *Size:* four G cans (10.3 mm square lands, 10.5 mm tall), one F can, an SMC diode and a 2512: about 5.5 cm2.
- *Placement:* board A, on VBAT, the charger's VSYS. Board P sits behind the pack's FETs, which are open in S4, so it cannot hold
  VSYS. The zone and the height are Layer 9's; L4-E8 placed six G cans on board A's VBUS20, so the class fits the board.
- *Inrush, the entry and F1:* the bank charges through R_CH at 51.2 mA at most (0.864 W at most against the resistor's 1 W at 70 C,
  the inside air 62.1 C; a 0.744 s time constant, 0.322 J per full charge). The direct can charges with VSYS under the charger's
  own start (0.5 A until 1.6 V, 3 min allowed, 9.3.21.8; 1.93 ms). The entry's start ends before U34 releases the front end (79 ms
  at least), so neither the entry's inrush nor F1's I2t changes (MEETS).
- *Inrush from the pack* (S1 from cold, VSYS discharged, the discharge FET switching at once): the direct can and the MLCCs (603.4
  uF at most) through the pack's least loop (69.17 mOhm): 242.9 A peak, over the image's ASCD 55.6 A for 61.5 us against its 183 us
  delay (MEETS). The bank, behind R_CH, adds 51.2 mA and cannot trip ASCD. **This is why the bank is isolated**: four cans directly
  on VSYS would hold the pack's inrush over ASCD for longer than its delay.

**What it does not do:**
- A step beyond the source's headroom is a deficit, not a transient. At a 9.00 V plug the slot rail's step on P1's plan leaves
  7.45 W short, which the fallback only delays by 7.26 ms. R-c's measured headroom must therefore count the largest uncontrolled step
  of the loads P1 keeps (E11-06 measures P1's peaks).
- In S2 (a warm CUV) VSYS is the stack plus Q2's diode, 10 to 11 V, at A-14's assumed 10.0 V floor: no droop is left to hold. S2
  still rests on the charger's response and on the converters' real minimum inputs (E11-08).
- It settles neither D1 (the steady mode) nor D3 (the inhibited mode): no capacitance answers what the converter regulates.

**What remains for (B) or (C):** (B), an NVDC charger with a battery FET, is the only arrangement that removes D1 and D3, since it
regulates VSYS by design whatever the pack and holds a charge with its battery FET; it reopens five records on a part whose sheet is
not held (section 4). (C), a precharge path, answers D6 and a deeply discharged pack's wait, not D1 to D3.

### 11b. What changes for U-04's classification (out 11)

- **Made independent of TI by the fallback:** D2, for every step R-c admits in S4, within the bank's 1.117 ms (with D2's bench
  margin); and D5, by the direct can.
- **Still depending on TI:** D1 (S4 at all), D3 (REQ-077's hold and R-a's S2), D4 (low consequence), D6 (the image's 0-V charging),
  D7 and D8 (R-b's cases (iii) and (ii)); and on the entry's makers, D9 and D10.
- **Negative answers with a remedy inside arrangement (A):** D4 to D10. **With none:** D1 and D3, whose negative answers return
  (B).

**U-04 stays an ARCHITECTURE-LEVEL CHOICE.** The fallback narrows the architecture's dependence on TI from four statements (D1, D2,
D3, D5) to two (D1, D3). Those two decide whether arrangement (A) can run on a source with no usable pack and hold a charge while
carried, and no part, rule or capacitance inside (A) answers them. One bench sample can show the mode on that silicon revision; it
cannot make it a production-wide behaviour. U-04 can be re-classified only when TI states D1 and D3 as behaviours of the part (or a
datasheet revision does), or the architecture moves to (B). Section 12 takes up (B) as TI's BQ25730, whose sheet prints both.

**What stays CONDITIONAL:** REQ-015 at 9.00 V at the plug (section 3g's evidence list, unchanged); D2's 1 ms (E11-26); the hybrid
parts' cold capacitance and the diode's cold drop (A11-14, A11-15); the declared steps (r4a's session targets, A11-17); the bank's
zone on board A (E11-24).

**The TI draft:** `clarification/TI-QUESTIONS.md` adds what REVIEW-REQUEST.md section 4 does not ask: Q-TI-11 (D1, D2, and the
largest stable VSYS capacitance), an addendum to Q-TI-3 (D3: ChargeCurrent 0, and a pack that takes charge but cannot discharge),
Q-TI-12 (D7, D8), Q-TI-13 (D9) and Q-TI-14 (D10). Q-TI-2 is left as worded, partly answered on E2E (D4). REVIEW-REQUEST.md is not
edited. Drafted, not sent.

## 12. The U-04 question for the consolidation: TI's BQ25730 against board A's circuit (2 October 2026; out 12)

**The owner's instructions (2 October 2026).** At 11:25: for a function still failing after repeated corrections, compare at
most three credible approaches (a simpler topology, a better-documented part or a module among them), prefer adequate margin
and fewer interacting controls, quantify power, heat, space, cost and endurance, select the best-supported route, stop
preserving a part through more assumptions and compensating circuitry, and keep the work already done unless the change affects
it. At 12:00: select the charger implementation that supports the battery-present, battery-absent and charging-inhibited modes,
and evaluate TI's BQ25730 against its datasheet and this circuit (interfaces, settings, startup, protection, budgets), since a
shared family does not make two parts compatible. The coordinator framed it: U-04 rests on a non-power-path charger, D1 and D3
are unbounded, and the hold-up bank is compensating circuitry.

**The documents (MAKER).** TI BQ25730, **SLUSE65A** (February 2021, revised January 2024), 111 pages, sha256
`e41ef289ce1de377d7b92bce609177d924e149099d9c4424d88f6b21ad57153f`, fetched from TI's own link on 2 October 2026 and held back
under TI's terms like the other TI sheets of this record (`fetch_held_back.py`, `v2/vendor/ti/held/`). The battery FET's sheet:
AOS AONS21357 Rev 2.1 (November 2023), sha256 `1a6460e7c63596ca7d48fe1660ee3a3ee48c33d6e345ef41d7c94c21cd7642d9`, held back the
same way (it carries AOS's copyright and no grant to redistribute). The gauge's DSG rise time comes from the tracked
`ti-bq4050.pdf`; the catalogue readings, with prices, are filed in `inputs/` (out 0).

### 12a. The pins against U3's netlist

The two pin tables (SLUSE66A and SLUSE65A, pp.5 to 7, read by the script) name 31 of the 32 pins alike. **The one difference is
pin 21:** NC on the BQ25731 ("must be floating"; U3 draws it NC) and **BATDRV** on the BQ25730, the gate drive of a P-channel
battery FET, "shorted to VSYS to turn off the BATFET. It goes 10 V below VSYS to fully turn on BATFET. BATFET is in linear mode to
regulate VSYS at minimum system voltage when battery is depleted. BATFET is fully on during fast charge and works as an
ideal-diode in supplement mode" (p.5).

| Pin | BQ25731 (drawn) | BQ25730 | Change on board A (SESSION) |
|---|---|---|---|
| 21 | NC | BATDRV | to CH_BATDRV, the gate of the new Q39 |
| 22 VSYS | sense of the system node | the regulated system: "maximum limit ... ChargeVoltage register plus 150 mV and regulation minimum limit ... VSYS_MIN register" (p.7) | none: VBAT stays the system node |
| 20 SRP | the system side of RSR | the battery FET's side of RSR (Figure 9-1) | R149 moves from VBAT to CH_BATQ |
| 19 SRN | the pack side (R148, CELL_FUSED) | the same | none |
| 18 CELL_BATPRESZ | 4S strap, 75.14 % of VDDA | the same; pulled low it loads VSYS_MIN 3.6 V, SYSOVP 25 V and ChargeVoltage 4.2 V (p.29) | none, and battery presence is never wired to it |
| 6, 4, 10, 11 and the rest | | the same names, the same rows (12b) | none |

Added: **Q39**, source on VBAT (VSYS), drain on a new node **CH_BATQ**, gate on CH_BATDRV; **R17** (the 5 mOhm RSR) moves to
CH_BATQ to CELL_FUSED, as TI's Figure 9-1 draws the battery FET between VSYS and RSR.

### 12b. The settings L4-E4 to L4-E8 drafted, sheet against sheet (MAKER, INFERRED)

The script reads both electrical tables row by row: **98 of the BQ25731's 107 row blocks are identical** in the BQ25730's
table, among them every row the drafted settings rest on (ChargeVoltage's accuracy, ChargeCurrent's, the input limit by register
and by ILIM_HIZ, VINDPM, REGN, ACOV, SYSOVP, BATOVP, ACOC, the converter's OCP rows, thermal shutdown, HIZ, the 4S strap,
IDCHG, PSYS, the monitors), and the 400 kHz row, REGN's limit and ChargeCurrent's accuracy (-12 / 13.5 %, -18 / 21.5 %) are the
same. **Rows whose numbers differ:** VSYS_UVLOZ 1.5/1.7/1.85 V becomes 2.3/2.5/2.65 V and VSYS_UVLO 1.4/1.6/1.75 V becomes
2.2/2.4/2.55 V; IDCHG_TH2's typical 24.567 A is reprinted 24.576 A; five more differ only in text. **Rows added:** the system
voltage rows (VSYSMAX, VSYS_MIN), the precharge accuracy, the LDO-to-fast-charge thresholds and the BATDRV rows. The script
refuses a sheet in which any other row differs.

**Carried over unchanged** (RECORD): ChargeVoltage 16.8 V, written at most 16.884 V; IIN_HOST 4.70 A with RSNS_RAC 0 and
EN_EXTILIM 1 (L4-E4, L4-E5); the ILIM_HIZ line and section 3f's knee; VINDPM; SYSOVP 19.5 V, BATOVP, ACOV, ACOC and the
converter's OCP; HIZ under 0.4 V; PROCHOT and PSYS (R23, R24); the 400 kHz row with R219 191k, the compensation and L2 (S-117);
Q7 to Q10 on REGN; and R11, R12 and L4-E8's bank with its ballasts, which sit on VBUS20 ahead of the charger and see the same
input current.

**Registers that change** (MAKER): ChargeCurrent resets to **0000h, 0 A** (p.49), where the BQ25731's resets to 0080h, and the
watchdog (175 s at POR) returns it to 0 A, a non-zero write resuming the charge (p.36); VSYS_MIN becomes a register, 12.3 V at
POR for 4S (p.83); EN_LDO 1, EN_PORT_CTRL 1, BATFET_ENZ 0 and BATFETOFF_HIZ 0 at POR (pp.48, 67, 68): the battery FET is driven
and stays on in HIZ; **EN_OOA is 1 at POR** (p.47); the device ID reads D5h, not D6h; the I2C address 6Bh is the same.

### 12c. The three modes: the statement that bounds VSYS in each (the acceptance)

The table's conditions are TJ -40 to 125 C unless a row says otherwise (p.9). The two VSYS rows hold "OOA disabled", and EN_OOA
is 1 at POR, so **the firmware writes EN_OOA 0 at boot** for the printed accuracy to apply (SESSION; before that write the modes
are stated and their accuracy is not).

| Mode | The maker's statement (page) | VSYS | Startup (page) | The exact gap |
|---|---|---|---|---|
| (1) battery present, source on | "system voltage is regulated 150 mV above battery voltage when BATFET is turned off"; the BATFET fully on while charging or supplementing; VSYS_MIN the floor (p.38) | 12.054 V (the floor), or with the source overloaded the pack less Q39's drop (9.786 V at the CUV stack and OCD1's 20 A, as (A)'s pack sits on VSYS less R17's drop), up to 17.375 V (the pack at 16.884 V plus 150 mV, +2 %, VSYSMAX_ACC p.9): **BOUNDED** | from VBUS: the registers, the cell count, then "Converter powers up" (p.27); with only the battery above VVBAT_UVLOZ (2.35 to 2.8 V), "charger wakes up and the BATFET is turned on" (p.27); no charge until ChargeCurrent is written (p.49) | none for VSYS |
| (2) battery absent, or both of the pack's FETs open, source on | "independent system voltage instant-on with no battery or depleted battery" (p.1); below VSYS_MIN "the BATFET operates in linear mode (LDO mode), and the system is regulated at VSYS_MIN" (p.38); VSYS_MIN_REG_ACC 12.3 V, minimum -2 % (p.10) | at least **12.054 V at TJ -40 to 125 C**; at most 17.375 V by the VSYS pin's maximum limit (p.7) and VSYSMAX_ACC (p.9): **BOUNDED** | the same power-up (p.27); VSYS_UVP clamps the input to 0.5 A under 2.4 V and after 2 ms shuts the converter for 500 ms, retrying for 10 ms, latching after 7 failures in 90 s (p.38); the start time is bounded in 15b (the earlier "502.3 ms" withdrawn: the 0.5 A is an input clamp, not a delivered current) | VSYS_MIN_REG_ACC prints -2 % in its maximum column as well (p.10), so its upper side is not printed; no claim rests on it (the floor decides each), and where a figure needs it 12.546 V is taken (A11-18) |
| (3) battery present, charging inhibited | CHRG_INHIBIT 1 inhibits the charge (p.48); VSYSMAX_ACC with charge disabled: VSRN + 150 mV within +-2 % (p.9); the BATFET off, so no battery current unless the load exceeds the source (supplement, p.5) | VSRN + 150 mV within 2 %, and at least 12.054 V with the pack at its CUV stack: **BOUNDED** | as (1); the bit is 0 at POR and is written from the hold flag | none for VSYS |

**So each mode has the maker's printed bound on VSYS: D1 and D3 are removed.** The margin from the floor to A-14's assumed 10.0 V
converter floor is 2.054 V, which a load step in S2 or S4 must not use up: that is D2, and SLUSE65A prints no transient limit
either (Figure 9-22, p.96, draws the peak power mode on VSYS undershoot, 1 to 6 A at VSYS_MIN 12.3 V with ICHG 0 A, at 4 ms a
division, a scale that resolves no transient).

### 12d. Protection (MAKER)

The over-voltage, input over-current, converter OCP and thermal rows are the same (12b); VSYS_UVP moves to 2.4 V with hiccup
(12c). BATOC stops the converter, and "BATFET status is not impacted if need to supplement power to system" (p.37). In HIZ the
battery FET stays on (BATFETOFF_HIZ 0), so CHG_INHIBIT's HIZ leaves the kit on the pack exactly as with the BQ25731 and R-a's
rule on that line holds. BATFET_ENZ would force the battery FET off on battery, and the kit would run through its body diode: it
is never written (SESSION). For a pack under VSYS_MIN with the source overloaded, TI's peak power mode on VSYS undershoot is the
one meant "when ... battery is removed" (p.33).

### 12e. The affected budgets

**Superseded by section 15c for the battery FET** (BATDRV drives 8.5 V at least, where AONS21357 prints no hot maximum; the
selected FETs are two BUK6Y10-30P, and the fallback "OCD1 set to the installed path" is withdrawn). The figures below are the first
selection's, kept as history.

- **The inductor L2.** With the pack at its CUV supplementing at the gauge's OCD1 20 A, VSYS is 9.786 V (Q39's drop), so S-117's
  11.8 A at 10 V becomes **12.057 A** and its worst peak **14.41 A** against Isat 25.4 A (S-117: 14.1 A): re-derived, 2.19 % up.
- **L4-E8's bank, its ballasts, R11 and R12:** on VBUS20 ahead of R16; the charger's input current and switching are the same
  rows: unchanged.
- **The battery FET Q39 (SESSION):** AOS **AONS21357**, 30 V, VGS +-25 V, RDS(on) at -10 V at most 7.8 mOhm at 25 C and **10.7
  mOhm at 125 C**, Ciss 2.83 nF typical, IDM 144 A, IS 36 A, RthJA 25 C/W at 10 s and 55 C/W steady on a 1 in2 2 oz board (Rev
  2.1, pp.1 and 2); LCSC C404364, stock 3875. TI's selection (p.92): P-channel, 20 V or more for 1 to 4 cells, Ciss under 5 nF:
  2.83 nF typical, 56.6 % of it (no maximum printed); SYSOVP's 19.5 V is 65 % of its VDS, BATDRV's 11.5 V at most 46 % of its VGS.
- **Its SOA.** Figure 9 (p.4) is junction-to-case on a large heatsink at TC 25 C (Note F), so on board A's copper the
  junction-to-ambient single-pulse rating of **Figure 14** decides; the script reads Figure 14 from the sheet's drawing (ZthJA at
  10 s: 25.01 C/W against the table's 25). Every protection current below sits at VDS under 0.6 V, in Figure 9's RDS(on) region
  and under IDM; RDS(on) is taken at its 125 C maximum above 125 C (A11-19); the inside air is 62.1 C (L4-E9).

| Q39 on the pack's path | Current, time | TJ from the inside air | TJ after 10 A held | Verdict |
|---|---|---|---|---|
| PS-IDLE-SPEC on battery | 2.972 A | 0.0945 W, **0.221 % of the pack's output** | | the endurance it costs |
| PS-TYP on battery | 4.375 A | 0.2048 W, 0.325 % | | |
| the coordinator's 10 A for 60 s | 10 A, 60 s | 107.8 C | 120.9 C (10 A held, the steady 55 C/W) | MEETS |
| the pack's 18 A peak | 18 A (3.467 W) | at most 10.44 s | at most 0.916 s | bounded by time |
| the gauge's OCD1 | 20 A, 2 s | 127.9 C | 170.3 C | NOT MET after 10 A held |
| the image's OCD2 | 24 A, 1 s | 138.9 C | 184.4 C | NOT MET after 10 A held |
| the AFE's AOLD | 30 A, 20 ms | 89.9 C | 145.7 C | MEETS |
| the image's ASCD | 55.6 A, 244 us | 73.2 C | 131.6 C | MEETS |

**So the sheet's own board does not carry the pack's protection envelope:** below OCD1's 20 A the gauge never trips, and 20 A held
needs an installed **RthJA of at most 20.54 C/W** (25.35 C/W for 18 A held), against the sheet's 55: a Layer 9 bar (**E11-29**,
CONDITIONAL). The fallback: the gauge's OCD1 set to what the installed path carries, or the bridge shedding on PROCHOT's IDCHG.

- **The docking inrush** (S1 from cold, the dependency round's pack loop, the discharge FET at once, no diode drop credited):
  242.9 A peak through Q39's body diode into VSYS's 489 uF at most, over IDM's 144 A for **17.7 us** (time constant 33.8 us). The
  sheet prints no body-diode pulse rating, only IS 36 A continuous: **the exact gap (E11-30)**. The gauge's DSG drive rises in 200
  to 500 us typical to maximum (bq4050 p.12) with no minimum, so it bounds nothing. The same peak passes R17, F1 and the pack's FETs
  in arrangement (A).
- **The precharge in LDO mode** (a pack under VSYS_MIN with the source on): ChargeCurrent 0x0080, 256 mA within +-30 % at 0 to 85 C
  (p.11), at most 332.8 mA; Q39 drops VSYS_MIN's 12.546 V to the pack: TJ 108.7 C at the CUV stack (10 V) and 145.3 C at the
  Shutdown Voltage's 8 V, reaching 150 C at 7.744 V; at 0x00C0 (480 mA at most) it would reach 150 C already at 9.216 V. **Rule
  R-b' (SESSION):** under VSYS_MIN, ChargeCurrent 0x0080 only, and no charge under 7.8 V on SRN (CONDITIONAL on E11-29's path,
  the steady 55 C/W used here); Q2's diode then carries 0.333 W, TJ 78.7 C. TI's own note: "Typically the battery depletion
  threshold should be greater than the VSYS_MIN" (p.97); the pack's CUV (10 V) is under it, so LDO-mode precharge is a normal
  state after a deep discharge, budgeted here.

## 13. Three approaches compared (out 13)

*The battery FET's figures in this section are the first selection's (one AONS21357); section 15c supersedes them with the pair of
BUK6Y10-30P, and section 15a adds board E's VSYS feed. The comparison of (A), (B1) and (B2) stands.*

**(B2), one other implementation whose maker's sheet states the property that removes D1 and D3: none found.** Looked at, all
held: the BQ25798 and BQ25792 (NVDC, both statements, but an integrated battery FET of 6 A RMS and 10 A for 1 s, BQ25798 p.7 and
BQ25792 p.8, under the pack's 18 A); the LM74700-Q1 (an ideal-diode controller, p.1: it blocks reverse current and regulates no
node); the LT8705A (a buck-boost regulator with no battery FET); the TPS2595, TPS2596 and TPS1663 (eFuses). TI's other
external-FET NVDC parts are the BQ25730's family and architecture, not a different implementation.

| | (A) the drawn BQ25731 with E11-24's hold-up | (B1) TI's BQ25730 with Q39 |
|---|---|---|
| D1 | OPEN (TI): no row bounds VSYS with no battery current | **removed**: VSYS_MIN_REG_ACC, at least 12.054 V at TJ -40 to 125 C (p.10), p.38's LDO mode, p.1's instant-on |
| D2 | the bank: 1.117 ms against T_RESP 1 ms (an assumption) | OPEN: no transient limit (Figure 9-22 a typical waveform); bench E11-31 against the 2.054 V margin, R-c's step rule the fallback |
| D3 | OPEN (TI): no statement with charge inhibited and no battery current | **removed**: VSRN + 150 mV within +-2 % with charge disabled (p.9), the battery FET off (p.38) |
| D4 | TI's forum answer: 256 mA at POR | **removed**: ChargeCurrent's reset printed 0000h (p.49); the watchdog returns it to 0 A (p.36) |
| D5 | the direct EEHZK1V181P | the same can (TI's 50 uF, p.87) |
| D6 | OPEN (the gauge's 0-V sequence) | OPEN, unchanged |
| D7 | OPEN: the clamp typical only | **removed inside 0 to 85 C**: 256 mA within +-30 % (p.11) |
| D8 | OPEN (0x0200 outside 0 to 85 C) | OPEN, the same row |
| D9, D10 | OPEN (board E's entry) | OPEN, unchanged |
| Carried over | all | every L4-E4 to L4-E8 figure (12b), section 3, R-b's case (i) |
| Re-derived | none | VSYS per mode; L2's 12.057 A; the start; ChargeCurrent's POR and watchdog; R-b'; Q39's loss, bar and inrush; CELL_FUSED's 104 uF now behind Q39; the bank withdrawn (at the 12.054 V floor four cans would hold only 0.302 ms) |
| Power and heat into the case, on battery | none added | Q39: 0.0945 W at PS-IDLE-SPEC, 0.2048 W at PS-TYP, 1.07 W at 10 A |
| Endurance on battery | none lost | 0.221 % at PS-IDLE-SPEC, 0.325 % at PS-TYP |
| Area on board A | the bank and the direct can, about 5.5 cm2 | Q39's 5 x 6 mm land and the direct can, about 1 cm2 of parts, with Q39's copper sized by E11-29 (at least the sheet's 1 in2 of 2 oz copper, on any layer) |
| Part cost, LCSC 10-piece (2 October 2026) | 6.2468 USD | **4.1792 USD**, 2.0676 USD less; but the BQ25730 has LCSC stock 0 (the BQ25731 1125): E11-32 |
| Interacting controls | four run-time rules, two tied to the gauge's FET state (R-a's S4 exception, R-b), R-c, the hold's flag, the bank leaning on T_RESP | three run-time rules (R-a with no exception, R-b' tied to the gauge, R-c), the flag, two boot writes (EN_OOA 0, ChargeCurrent with the watchdog); the battery FET's registers left at POR |
| Still depending on a maker | D1, D3 (TI), D6, D7, D8, D9, D10 | D2 (bench), D6, D8, D9, D10, Q39's docking pulse (AOS or the bench), its thermal path (layout) |

## 14. The selection, the draft and U-04's class (out 14)

**SELECTED (SESSION): (B1), TI's BQ25730 in U3's land with the battery FET Q39** (the fix round: Q39 and Q40, two BUK6Y10-30P,
section 15c; board E on VSYS, 15a). *Why:* it is the only option whose maker prints
a bound on VSYS in all three modes (12c), removing D1, D3 and D4 and bounding D7 inside 0 to 85 C, where (A) leaves D1 and D3 to
TI and holds D2 with compensating parts on an assumed 1 ms; every setting L4-E4 to L4-E8 drafted rests on rows the two sheets
print alike (12b), so that work carries over; it costs less and removes the bank. *Its costs, named and bounded:* Q39's thermal bar
(E11-29), the docking pulse (E11-30), 0.221 % of the pack's output at PS-IDLE-SPEC, and the BQ25730's stock (E11-32). No line a
class in `reserved.json` protects changes, and no money beyond parts is spent, so the choice is the session's. *Reversed by:* a
layout that cannot reach E11-29's bar (15c: 34.42 C/W per FET at +70 C air) even with the pair's drain copper tied into the plate,
or E11-30 showing the pair cannot take the docking pulse with no matched layout or workable slower turn-on; then (A) with its dependency round stands and TI's answers on D1 and D3 decide.

**The draft:** `apply_gen_sch_a_charger.py` (release-guarded, never applied here): U3 BQ25730RSNR (C5219071) with pin 21 on
CH_BATDRV; Q39 and Q40, two BUK6Y10-30PX (C3278350; the first draft's AONS21357 superseded, 15c), between VBAT and CH_BATQ;
J_DOCK pin 1 on VBAT for board E's VSYS_E (15a); R17 and R149 moved to CH_BATQ; C236 EEHZK1V181P (C242139) on VBAT
with its land key; CH_BATQ declared a segment of the pack path; the charger's sheet group renamed. It composes with
`apply_gen_sch_a_guard.py` in either order.

**What it changes downstream (for the consolidation):** E11-27 to E11-32 are added (E11-33 to E11-35 by the fix round, 15); E11-24 is withdrawn and E11-05 is no longer
needed once E11-27 is applied; E11-22's case (iii) is bounded inside 0 to 85 C by R-b'; in `clarification/TI-QUESTIONS.md`,
Q-TI-11's D1 part and Q-TI-3's addendum fall away while D2's question stays, and Q-TI-15, Q-TI-16 and Q-AOS-1 are drafted for (B1); R-a's S4 exception is withdrawn (the CHRG_INHIBIT bit
follows the hold flag in every state); E11-04's firmware rules gain E11-28's; section 3 (REQ-015 at the plug) is unchanged.

**U-04's claims still open with (B1):** D2 (load steps in S2 and S4 against the 2.054 V margin: bench E11-31, R-c's step rule the
fallback); the pair's thermal bar (E11-29) and the docking pulse's split (E11-30); the start's first window and the held pack
current (E11-31); the fans' supply rating (E11-35); D6; D8 (R-b's case (ii)); REQ-015 at 9.00 V at the plug as
section 3g (E11-06, E11-09, E11-23); and on board E, D9 and D10.

**U-04 by the owner's exit definition: A DOWNSTREAM QUALIFICATION TEST WITH BOUNDED EVIDENCE AND A WORKABLE FALLBACK**, once E11-27
is applied. The three modes rest on the maker's printed rows; each open claim has a test or an analysis that bounds it and a
fallback that needs no new architecture (R-c's step rule; the pair's drain copper tied into the plate; a matched layout of the two
diode paths or a slower DSG turn-on on board P; no protection lowered, section 15c). On the
drawn board, arrangement (A), it stays the architecture-level choice of section 11.

## 15. The fix round for the consolidation review (cx36, NOT YET on set 27's `8fbb68b6`; out 15)

The owner's one authorised review of the consolidation (`records/l4close/checks/astra-check-l4close-1.md` in set 27) found two
blocking discrepancies in this record's selection, B1 and B2, and four charger minors (its E1). This round answers them; a targeted
recheck follows. Sections 12 to 14 stand where this section does not supersede them, and every superseded passage says so.

### 15a. B1: board E's auxiliary domain on a source-capable feed

**The finding holds (NETLIST, MAKER).** Board E's U12 (the AP63205 that feeds the sensor controller, the Geiger supply and the
fans' logic: its VIN and EN), C31 and both mixer fans with D7 and D8 sit on CELL_F, the pack node before board A's R17 and the
battery FET; CELL_F declares them at 1 A (U12 0.8 A, the fans 0.1 A each). With the charge inhibited the battery FET is off
(SLUSE65A p.38) and they still drained the pack; with the pack absent nothing fed them.

**The feed (SESSION): VSYS alone, over the dock.** Board A's J_DOCK pin 1 goes from GND to VBAT (VSYS), board E's J_BLK pin 1 to a
new net VSYS_E, and U12's VIN and EN, C31, the fans' supply pins and D7 and D8 move to VSYS_E. CELL_F keeps the pack path to board A,
D3, C1 and the pack monitor R42 and R43. *Why VSYS and no OR:* VSYS exists whenever the pack or a source does (the battery FETs are
on with the battery alone, p.27, and their body diodes conduct under any fault of the drive), while a diode or ideal-diode OR with
CELL_F would take the pack whenever VSYS sits under it, which the +-2 % row allows in the held state.

**The contact (SESSION): one 813 on pin 1**, 1 A declared, 28.6 % of its 3.5 A, 4.9 K by w3de's assumed rise. The ground return keeps
seven 813 contacts. At the 32.1 A coincidence with every Mill-Max pin at 20 mOhm (w3de's model, pinned):

| 813 ground contacts | Each carries | Of 3.5 A | At the 51 C inside air | At the margin's 65 C |
|---|---|---|---|---|
| 8 (as drawn) | 2.092 A | 59.8 % | 72.4 C | 86.4 C |
| 8, one open | 2.238 A | 63.9 % | 75.5 C | 89.5 C |
| 7 (this round) | 2.238 A | 63.9 % | 75.5 C | 89.5 C |
| 7, one open | 2.406 A | 68.7 % | 79.3 C | 93.3 C |

One contact moves W3DE-DOCK-R1's residual by one contact's step and keeps the 51 C envelope under the 813's 85 C with one open; a
second supply contact would leave six, 84.1 C with one open at 51 C. A lost pin 1 unpowers board E's controller, which board A
reads on HOT-R1 as the detector lost (IF-AE-DOCK `hot_r1`): a detected state.

**VSYS_E's range:** the supplement floor 9.688 V to 17.375 V (15d). The AP63205 takes 3.8 to 32 V (Diodes DS41326 p.1). The fans,
rated as a 12 V class on CELL_F's 16.884 V, now see up to 17.375 V: their maximum supply voltage is owed (**E11-35**).

**No unintended pack discharge with the charge inhibited.** With an adequate source the battery FETs are off with no charging or
supplement current (p.38) and board E runs on VSYS_E from the source. What the pack still feeds:

| Element | The drain | Basis |
|---|---|---|
| the pack monitor R42 + R43 (122 kOhm, at -1 %) | 0.1398 mA at 16.884 V, intended (the controller's own pack reading) | NETLIST |
| D3, SMCJ18A | IR at most 1 uA at 18 V and 25 C; hot leakage not printed | Littelfuse SMC series (held) |
| the battery FETs' body diodes | VSYSMAX_ACC's -2 % lets VSYS sit up to 0.191 V under the pack at 16.884 V; no current printed at that bias (VSD only at 80 A) | not bounded on held evidence |
| the charger's SRN pin | its leakage row prints a mismatch only | not bounded on held evidence |

So no kit load is fed from the pack while the source carries it. **0.1408 mA is the quantified subset of the held-pack drain** (the monitor
and D3 at 25 C); D3's hot leakage and the body diodes' current are not bounded on held evidence (section 16e). The bench reads the held
pack current at **at most 1 mA** (E11-31's acceptance; board E's domain drew about 0.5 to 1.5 W from the pack before). The pack still
supplements when the source cannot carry the load, which is NVDC's intended behaviour and R-c's case.

**The sequences.** *Source only* (the pack absent or both its FETs open): the source and the entry (3c); the front end to VBUS20;
U3's POR (p.27) with ChargeCurrent 0 A; the converter up; VSYS through VSYS_UVP's start (15b) to VSYS_MIN; board A's always-on and
board E's U12 on VSYS_E; E's controller up and driving HOT-R1; firmware writes EN_OOA 0, IIN_HOST 4.70 A and CHRG_INHIBIT from the
hold flag. *Held:* the flag set writes CHRG_INHIBIT 1; the battery FETs turn off as the charge stops (p.38); VSYS moves to VSRN + 150
mV; nothing on either board moves; the flag cleared writes 0 and ChargeCurrent by R-b'.

**The drafts:** board A's half joins `apply_gen_sch_a_charger.py` (J_DOCK pin 1 on VBAT, VBAT's loads gain J_DOCK's 1.0 A); board
E's half is **`apply_gen_sch_e_aux.py`** (17 edits: J_BLK pin 1, U12, C31, the fans and their diodes on VSYS_E; VSYS_E declared;
CELL_F's loads the pack path alone; E6_SW, E6_BST and the fans' switched returns to 17.4 V; a power flag); the interface is
**`apply_pcb_interfaces_dock.py`** (IF-AE-DOCK: the alias, pin 1, pins_history, BAT-F06's charge share reversed, an `aux_feed`
entry with the figures above, the findings list; and check_contracts.py's alias table). All three are release-guarded and applied
together (E11-27, E11-33, E11-34).

### 15b. The start, bounded where the held sheets bound it

**Withdrawn:** section 12c's "the start bounded at 502.3 ms, never a latch". The 0.5 A is VSYS_UVP's input clamp, a ceiling, not a
delivered current, so no start time follows from it.

- **The input limits (MAKER, p.38):** under 2.4 V of VSYS (VSYS_UVLO; rising 2.3 / 2.5 / 2.65 V, p.13) the input is clamped to 0.5
  A, at most 10.48 W from VBUS20's 20.96 V top. The sheet prints no minimum delivered current below that voltage.
- **The loads below 2.65 V:** the converters on VSYS are held off by their enables or their UVLOs (the LM5176 stages by logic, U12
  under its 3.8 V start, the heater buck by its divider). The resistors on VBAT (R2 100 k, R92 143 k, R96 143 k) draw at most 0.0636
  mA at 2.65 V. The ICs' currents under UVLO are not all held. Bringing VSYS's 489 uF to 2.65 V takes 1.717 mJ.
- **The retries (MAKER):** each failed start shuts the converter for 500 ms and retries for 10 ms; the 7th failure inside 90 s
  latches it, at most 3.062 s after the first window. With no pack only a POR clears it (VBUS re-plugged: "5 ms after either VBUS or
  VBAT becomes valid, the charger resets all the registers", p.27); with a pack the host does, running on the pack through the
  battery FETs.

So on held evidence the start ends in VSYS_MIN or in a latch within 3.062 s, never undefined. Whether the first window succeeds is
not bounded (no minimum delivered current is printed): **bench E11-31**, acceptance: from cold, at VBUS20 19.15 and 20.96 V, with
VSYS's maximum capacitance and the declared always-on loads (board E on VSYS_E), at -20, 25 and 62.1 C, VSYS reaches 12.054 V with
Fault VSYS_UVP clear; the hiccup's 500 / 10 ms and the latch shown on a shorted VSYS and cleared by a re-plug.

### 15c. B2: the battery FET, three options on one basis

**The finding holds.** BATDRV may drive only 8.5 V (SLUSE65A p.17), and AONS21357's hot maximum is printed at -10 V only. The 18 A
service for 60 s (pcb_interfaces.yaml, PWR-F12) stays, and no protection is lowered to meet it: section 12e's fallback "the gauge's
OCD1 set to what the installed path carries" is withdrawn.

*Superseded in part by section 16: `fet_bound`'s figure is kept as an allowance, not a bound (16a); AOS's transient shape, the Ciss
reading and the docking pulse's I2t reading are replaced (16b to 16d); the selection of the pair stands.*

**The basis (INFERRED from MAKER rows only, `fet_bound`).** RDS(on) at BATDRV's least drive (8.5 V) is bounded by the chord between
the printed maxima at -4.5 V and -10 V at 25 C: each unit's RDS(on) is convex and falling in |VGS|, and so is their pointwise
maximum. The temperature factor is bounded by the chord between the printed -10 V maxima bracketing the junction limit. The gate
ratio is taken from 25 C, where the threshold sits highest; it falls with temperature, so the hot ratio is no larger. No option is
judged above its last printed temperature.

**The air and the events.** The air is the consolidation's +70 C mixed-air line for the parts that must work in the heat stage
(L4-POWER-ARCHITECTURE K9, E3-O at +55 C ambient; K3 at +40 C); it covers L4-E9's 62.1 C. The board's transient shape comes from
AOS Figure 14 over its steady 55 C/W, applied to every option (A11-21): z(244 us) 0.00608, z(20 ms) 0.0525, z(1 s) 0.2266, z(60 s)
0.7766. The events each start from a hot state; per FET, the even split bounds each FET's power for any split of the RDS(on) spread:
- 10 A held;
- 18 A for 60 s after 10 A held (the service);
- 20 A held, under the gauge's OCD1, which never trips below it;
- from 20 A held: OCD2's 24 A for 1 s, the AFE's AOLD 30 A for 20 ms, and the image's ASCD 55.6 A for 244 us.

The bar is the installed junction-to-air resistance per FET at which every event keeps TJ at the limit or under.

| | (Q-a) AOS AONS21357, one | (Q-b) Vishay SQJ403EP, one | (Q-c) Nexperia BUK6Y10-30P, two in parallel |
|---|---|---|---|
| Printed RDS(on) maxima | 7.8 mOhm at -10 V and 25 C; 10.7 at 125 C; 12.3 at -4.5 V | 8.5 at -10 V and 25 C; 13.0 at 125 C; 15.0 at 175 C; 20.0 at -4.5 V | 10 at -10 V and 25 C; 16 at 175 C; 25 at -4.5 V |
| Junction limit | 125 C (its last printed row; rated 150 C) | 150 C (25 K under its 175 C) | 150 C (25 K under its 175 C) |
| Bound at 8.5 V and the limit | gate factor 1.1573: **12.384 mOhm** | 1.369: **19.166 mOhm** | 1.4091: **21.136 mOhm each** |
| Ciss against TI's 5 nF | 2.83 nF typical: MEETS | 4.5 nF maximum: MEETS | 4.72 nF typical for the two: MEETS |
| The bar per FET at +70 C (at 62.1 C) | **10.1 C/W** (11.55), set by OCD2 after 20 A held | **9.49 C/W** (10.43), the same | **34.42 C/W** (37.82), the same |
| Against the maker's board | 55 C/W: the bar is 0.184 of it | 68 C/W: 0.14 of it | none printed (LFPAK56, Rth(j-mb) 1.4 K/W); 0.626 of AOS's 1 in2 figure for the class |
| The docking pulse, 242.9 A | IDM 144 A; no body-diode pulse rating | ISM 84 A | ISM 320 A each |
| Part cost, LCSC 10-piece | 0.4238 USD | 3.5497 USD | 2 x 1.7386 USD |

**SELECTED (SESSION): (Q-c), two Nexperia BUK6Y10-30P in parallel, Q39 and Q40** (LCSC C3278350, 67 in stock; the sheet of 17
April 2020, held back). *Why:* it is the only option inside TI's Ciss whose bar is of the order a board pour gives (34.42 C/W per
FET at +70 C air, 0.626 of AOS's 1 in2 figure for the same 5 x 6 mm class). (Q-a) would need 10.1 C/W and (Q-b) 9.49 C/W, a fifth
and a seventh of their makers' own board figures, which a pour does not give one part. It also has a printed RDS(on) maximum to
175 C, a 175 C rating, and a printed body-diode pulse rating over the docking pulse. A third FET would put Ciss at 7.08 nF, over
TI's rule.

**Its envelope at the bar, +70 C air:** TJ at most 150 C for every event above; 18 A for 60 s after 10 A held reaches 119.8 C
(CONDITIONAL on E11-29, the installed path).

**The docking pulse:**
- *All of it in one FET at 25 C:* 242.9 A against ISM 320 A, and 0.9977 A2s against the ISM rectangle's 1.024 A2s (MEETS).
- *From the +70 C air,* with ISM derated linearly to the 175 C rating (x0.7, A11-22): 224 A and 0.7168 A2s. This is met if one FET
  takes at most 0.848 of the pulse.
- *Open:* the split between two body diodes is not printed (E11-30: the bench pulse on the pair, or a layout matching the two
  paths).

**The drive:** BATDRV's 6 kOhm at most into 4.72 nF gives a 28.32 us time constant.

**The precharge in LDO mode, with R17's tolerance (the review's minor):**
- The current: 0.256 x 1.30 / 0.99 = **0.33616 A** at most, all of it in one FET (linear-mode sharing is not assumed).
- The junction reaches 150 C at the bar and +70 C air with SRN at 5.632 V.
- **R-b' (SESSION, revised):** no charge under **5.7 V** on SRN (the cells' 1.0 V a cell floor is 4 V). Q2's diode then carries
  0.3362 W, TJ 86.8 C. R17's drift with temperature is not held.

**On battery:** 0.0934 W in the pair at PS-IDLE-SPEC (0.218 % of the pack's output) and 0.2023 W at PS-TYP (0.321 %).

**L2:** VSYS in supplement is 9.688 V (CELL_FUSED's 10.0 V less R17 and the pair at OCD1's 20 A), giving 12.179 A and a peak of 14.55
A against Isat 25.4 A.

### 15d. The charger minors (E1)

- **The inhibited acceptance, piecewise** (VBAT_VSYS_MIN_RISE, 98 to 102 % of VSYS_MIN, p.14):
  - SRN under 12.054 V: LDO mode, VSYS at least 12.054 V.
  - SRN over 12.546 V: VSRN + 150 mV within +-2 %.
  - Between the two: either mode, so at least **11.96 V**.
  - The review's case, SRN at 10 V, is the LDO region; (10 + 0.15) x 1.02 = 10.353 V belongs to no region.
- **The LDO region's upper side, 12.546 V,** is an assumed reading of TI's malformed maximum column (A11-18), not a printed limit.
- **Every floor above holds with adequate input power.** With the source overloaded, VSYS follows the pack through the battery FETs
  and R17: 9.688 V at CELL_FUSED's 10.0 V and OCD1's 20 A. With no pack and an overloaded source there is no floor; R-c sheds.
- **EN_OOA resets to 1 (p.47):** the printed accuracy covers VSYS only after the firmware writes 0. The pre-firmware start has no
  printed accuracy, and E11-31 records it.
- **"No battery FET":** this record's section 2 describes the drawn BQ25731 and stays. L4-E9's texts are drafted below for their
  owner (E11-34).

### 15e. The texts drafted for L4-E9's record (E11-34; this record edits no other record)

| Where | Now | Drafted |
|---|---|---|
| L4-POWER-ARCHITECTURE.md 4a, "plug out" | the pack carries VBAT with no break (no battery FET) | the pack carries VBAT with no break, through the battery FETs Q39 and Q40 (ideal-diode supplement, SLUSE65A p.38; their body diodes conduct first) |
| L4-POWER-ARCHITECTURE.md 4a, "pack connected" | the always-on comes up on CELL_F | board E's always-on comes up on VSYS_E (board A's VSYS over the dock's pin 1, L4-E11 15a); the inrush passes the pair's body diodes (E11-30) |
| L4-POWER-ARCHITECTURE.md 4a, "pack disconnected, or both FETs open, with a source" | (B1): the BQ25730 regulates VSYS at VSYS_MIN through Q39 in LDO mode | (B1): the BQ25730 regulates VSYS at VSYS_MIN (at least 12.054 V with adequate input); board E's auxiliary domain runs on VSYS_E from the source (L4-E11 15a) |
| L4-POWER-ARCHITECTURE.md 4a, "the charge inhibited, the pack present" | (B1): Q39 off, VSYS at the pack plus 150 mV, no battery current | (B1): Q39 and Q40 off, VSYS piecewise (VSRN + 150 mV within 2 % over 12.546 V, VSYS_MIN under 12.054 V, at least 11.96 V between); board E on VSYS_E; the pack feeds no kit load, its monitor 0.14 mA (L4-E11 15a, 15d) |
| L4-POWER-ARCHITECTURE.md Appendix B2, "A source leaving" (kept history: a note, or the text) | VBAT is the system node with no battery FET | VBAT is the system node behind the battery FETs Q39 and Q40, which the charger turns on as an ideal diode when the source leaves (p.38) |
| L4-POWER-ARCHITECTURE.md IF rows of VBAT (IF-09 to IF-14) | VBAT 10.0 to 16.884 V | VBAT 9.688 to 17.375 V (the supplement floor at OCD1's 20 A; the held top), 12.054 V with no pack and adequate input (L4-E11 15d) |
| L4-POWER-ARCHITECTURE.md IF-06 (the dock) | VIN_RAW over the dock | VIN_RAW over the dock, and VSYS to board E's VSYS_E on the 813 pin 1, 1.0 A (L4-E11 15a) |
| L4-POWER-DIAGRAM.svg, the system node | 10.0 to 16.884 V | 9.688 to 17.375 V |

## 16. The fix round for the review of the provisional fixes, L4-F02 and L4-F03 (out 16)

The external engineering review of the provisional fixes (2 October 2026, on `8fbb68b6`, `516d43fe` and `11339ec7`) keeps B2 open
(L4-F02) and adds L4-F03, the branch protection of the dock's new VSYS contact. Both are qualification gaps, **not demonstrated
failures**: nothing here says the BUK6Y10-30P pair or the 813 contact has failed or would fail. Every figure below is printed by
`l4e11_power.py` in out 16; every circuit change stays drafted. B1's topology, the withdrawn start-time guarantee and the B4
arithmetic (50.043663 W; 52.133663 W with the ballasts) are untouched.

**Status, item by item (2 October 2026):**

| Item | Status | The figure and the sheet |
|---|---|---|
| L4-F02 objection 1, RDS(on) at BATDRV's 8.5 V | **CONDITIONAL** (E11-36) | no sheet read prints a maximum under 10 V of drive above 25 C (BUK6Y10-30P Table 7 p.6: 10, 16 at 175 C, 25 at -4.5 V and 25 C); 21.136 mOhm is now an allowance |
| L4-F02 objection 2, the transient shape and the coupling | **CLOSED as an analysis basis; qualification CONDITIONAL** (E11-29) | the device's own Fig. 4 (p.5), scaled to Rth(j-mb) 1.4 K/W: 0.2589 K/W at 244 us, 1.3571 at 20 ms, 1.4 at 1 s; coupling in the measured sum Zself + Zmut |
| L4-F02 objection 3, Ciss against TI's 5 nF | **OPEN** (E11-37) | 4.72 nF typical for the pair at -15 V (Table 7), about 5.74 nF near 0 V (Fig. 12, typical, p.8); no maximum printed; TI p.92 |
| L4-F02 objection 4, the docking pulse | **CONDITIONAL** (E11-30) | ISM 320 A for 10 us at Tmb 25 C (Table 5 p.3) against the 242.9 A peak, one FET; TJ 123.3 C from +70 C on the printed VSD (1.2 V at 80 A, p.6) carried up by concavity; VF hot and ISM hot not printed |
| The 18 A for 60 s service from the hot state | **CONDITIONAL** on E11-29 and E11-36 | TJ 126.7 C from 87.5 C at 10 A held, +70 C air, no board capacity credited |
| L4-F03, the dock's VSYS branch | **CLOSED in design** (overload, soft short, inrush, recovery); the hot short's peak **CONDITIONAL** (E11-38) | TI TPS16630 (SLVSET9G pp.8 to 10, 20, 26) at R(ILIM) 11.0 kOhm: 1.4713 to 1.8018 A; the 813 at 51.5 % of 3.5 A |
| The held-pack drain wording | **CORRECTED** (15a and the text drafted for L4-E9 below) | 0.1408 mA is the quantified subset; the 1 mA bench acceptance kept |
| check_contracts.py, the interface draft's second target | **CONFIRMED** in the tree | `v2/ecad/tools/check_contracts.py`; the alias edit applies to it (the tests apply it to a copy) |

### 16a. Objection 1: RDS(on) at BATDRV's least drive

BATDRV's gate drive is 8.5 / 10 / 11.5 V (SLUSE65A p.17) with the FETs' sources on VSYS, so VGS is -8.5 V at the least. The
BUK6Y10-30P's sheet (17 April 2020, Table 7, p.6) prints RDS(on) at most 10 mOhm at -10 V and 25 C, 16 mOhm at -10 V and 175 C and
25 mOhm at -4.5 V and 25 C. **No printed point bounds the operating point** (-8.5 V, hot): the -10 V rows need more drive than BATDRV
promises and the -4.5 V row is at 25 C only. The search for a part whose sheet prints one found none: the held SQJ403EP and AONS21357,
and two sheets fetched for this round and filed held (Vishay SQJ407EP, 62806 Rev. B; Nexperia PXP9R1-30QL, 5 January 2021), all print
their hot maxima at -10 V only.

**SESSION:** section 15c's 21.136 mOhm is withdrawn as a bound and kept as the **allowance** each FET is sized to (why this value:
every downstream figure of 15c and 15d, the 9.688 V supplement floor among them, was computed at it, and at 25 mOhm the sensitivity is
printed); **E11-36** confirms it
(Nexperia's maximum at -8.5 V and 150 C filed, or a pulsed Kelvin reading on parts from the lot in an oven at 150 C) or reverses it. At
the sheet's largest printed maximum, 25 mOhm, every power scales by 1.1828; parts at 25 mOhm on a board built to the allowance would take
the held 20 A to 152.8 C and the service to 137.1 C, which is why E11-36 gates E11-29. *Reverse:* a reading over the allowance re-sizes
E11-29 before layout.

### 16b. Objection 2: the device's own transient impedance, and the two FETs' coupling

**The device.** Fig. 4 (p.5) prints Zth(j-mb) against pulse width with duty-cycle curves and no single-pulse curve; the lowest, duty
0.01, lies above any single pulse, so it is read (`inputs/nexperia-buk6y10-30p-figure-readings-2026-10-02.json`: the page rendered at
400 dpi, the axes located by the printed grid, one pixel 1.8 % of Z) and scaled from its plateau 1.3225 K/W to Table 6's maximum
Rth(j-mb) 1.4 K/W: **0.2589 K/W at 244 us, 1.3571 at 20 ms, 1.4 at 1 s and at 60 s**. AOS's Figure 14 shape is no longer used for
these FETs; steady resistance and transient impedance are kept apart, from the sheet's own Fig. 4 and Table 6 only (Nexperia's
AN90016, which the review names for the method, is not held here).

**The board and the coupling, stated as what a bench reads.** Each FET's self impedance Zself(t) (heat one, read its own junction by its
body diode's VSD) and the mutual Zmut(t) (heat one, read the other). With Pb the even split's per-FET power at the allowance (it bounds
each FET's power for any split, 15c), **TJ <= air + Pb x (Zself + Zmut)(t)** for either FET: the coupling is in the sum, not assumed away,
and Zself includes the device's own Zth(j-mb).

**The plan (SESSION), at the +70 C mixed air:** the held 20 A under OCD1 reaches at most **140 C**, keeping 10 K of the 150 C limit for
the pulses from it, so the installed **(Zself + Zmut) at most 33.12 K/W** at steady state (28 at 25 mOhm). Per-FET power 0.5284 W at
10 A, 1.712 W at 18 A, 2.1136 W at 20 A.

- **The service, 18 A for 60 s from the hot state** (10 A held at +70 C, no board capacity credited, so 60 s counts as steady):
  **TJ 126.7 C**, from 87.5 C, 23.3 K under the limit. The 18 A for 60 s stays; no protection is lowered.
- **The fault histories from the held 20 A** (each a step from 140 C to 150 C), the allowance on the installed sum at the event's
  width against the device alone:

| Event | Per FET | (Zself + Zmut) at most | The device alone | Left for the board and the coupling |
|---|---|---|---|---|
| OCD2 24 A for 1 s | 3.044 W | 10.753 K/W | 1.4 K/W | 9.353 K/W |
| AOLD 30 A for 20 ms | 4.756 W | 3.785 K/W | 1.3571 K/W | 2.428 K/W |
| ASCD 55.6 A for 244 us | 16.335 W | 0.703 K/W | 0.2589 K/W | 0.444 K/W |

- **The LDO-mode precharge**, one FET linear at 0.33616 A: under the plan's steady sum it stays at 150 C down to SRN 5.36 V, so R-b'
  (no charge under 5.7 V) keeps its margin.

**E11-29 is rewritten** to measure exactly these assumptions: Zself and Zmut at 244 us, 20 ms, 1 s, 60 s and steady, against the
table. E11-29's old case rise at 10 A and E11-30's old sharing check are no longer the closing evidence.

### 16c. Objection 3: Ciss against TI's 5 nF

TI's rule (SLUSE65A p.92) is "the Ciss of P-channel MOSFET should be chosen less than 5 nF"; TI prints the drive, RBATDRV_ON at most
6 kOhm and RBATDRV_OFF at most 2.1 kOhm, not the requirement behind 5 nF. The BUK6Y10-30P prints Ciss as a typical only: **2.36 nF at
-15 V** (Table 7), no maximum and no spread; its Fig. 12 (typical) reads about **2.87 nF at -0.1 V**, near the battery FET's working
point (on, or an ideal diode at 30 mV). The pair is **4.72 nF at the maker's test point and about 5.74 nF near 0 V**: it meets TI's
figure only at that test point and as a typical. Into the pair's typical Ciss BATDRV's time constants are 28.32 us on (-15 V), 34.44 us
on near 0 V and 12.05 us off; no printed limit exists to compare them with, so the actual requirement cannot be derived from TI's
sheet. **Not shown on printed data.**

**Three approaches (at most three):**

| | Margin to 5 nF | Heat | Interacting controls | Area and cost |
|---|---|---|---|---|
| (S1) the pair, kept | none shown (typical 4.72 at -15 V, about 5.74 near 0 V) | a board pour: (Zself + Zmut) at most 33.12 K/W | TI's BATDRV loops unchanged | two LFPAK56, 2 x 1.7386 USD |
| (S2) one BUK6Y10-30P | about 2.87 nF near 0 V, 57 % (typical) | junction to air at most 8.28 K/W for 20 A held: a path through the case, not a pour | unchanged | one LFPAK56 and a heat path to the case |
| (S3) a part whose sheet prints both | none found among the parts read (16a) | | | |

**SESSION:** the pair stays selected (it is the only arrangement whose heat a board pour can carry). **OPEN**, with E11-37: TI's statement
of what 5 nF bounds (Q-TI-17, drafted in `clarification/TI-QUESTIONS.md`, not sent) or the bench's BATDRV behaviour with the pair, and on
a negative answer the engineer's choice between (S1) and (S2).

### 16d. Objection 4: the docking pulse

Section 15c's reading of ISM's 320 A for 10 us as an I2t of 1.024 A2s **is withdrawn**: the sheet prints no I2t. The waveform (the
dependency round's pack loop, the discharge FET at once): **242.9 A peak, time constant 33.8 us**. It is over the continuous IS 80 A
(Tmb 25 C, Table 5 p.3) for 37.6 us and still 180.7 A when ISM's 10 us ends. **No sharing is credited:** the whole pulse is taken in one
FET (the sheet prints VSD's maximum and no minimum, so the split cannot be bounded).

**Its junction from +70 C:** P = VF x i with VF at most max(1.2 V, 1.2 V x i / 80 A): the printed maximum at 80 A and 25 C (p.6) carried
up by VF's concavity in i (3.643 V at the peak, INFERRED); superposed on Fig. 4 as scaled: **a rise of 53.3 K, TJ 123.3 C**, 16.68 mJ,
885 W at the peak. The bound is reached at once because Fig. 4 is held at its first read point (12 us, 0.0602 K/W, 4.3 % of its steady
value) below that width, a bound and not a waveform; within 12 us the heat is still inside the package, so the board below cannot add to
it. Between ISM's 10 us and the continuous IS the sheet prints no rating but the junction limit, so the waveform past 10 us is judged on
TJ alone, at 25 C as hot. **What the sheet does not print:** VF above 80 A or at a hot junction (TJ stays under 150 C while
VF is at most 1.501 times that bound), and ISM at a mounting base over 25 C (the 242.9 A peak is 75.9 % of 320 A at 25 C). **CONDITIONAL**
on E11-30: both from Nexperia or a pulse test on parts. The constraint that would remove both, a slower turn-on of board P's discharge
FET, interacts with the pack's ASCD turn-off and belongs to board P's owner; it is named in E11-30, not drafted here.

### 16e. L4-F03: the dock's VSYS contact and its branch protection

**The branch:** VBAT (VSYS) on board A to J_DOCK pin 1, one Preci-Dip 813 (3.5 A operating maximum, 85 C with its music-wire spring), its
24 AWG and board E's copper to VSYS_E; 1.0 A declared. The review's counterexample, 5 A from 14.4 V (2.88 Ohm), is over the contact and
under every upstream threshold, in source-only and battery operation alike; the 1 A declaration limits nothing.

**Three protections compared, on maker-printed rows over temperature and time:**

| | Over the contact's rating | Over temperature | Interrupt and recovery | Drop, area |
|---|---|---|---|---|
| (F) Littelfuse 0997 MINI 2 A 58 V (held) | from 3.5 A (175 %) to 4 A it may carry up to 600 s (the 135 % row's maximum); under 2.7 A it need never open | load allowed 1.6 A at 60 C, 1.4 A at 80 C | 1000 A at 58 V; replaced by hand | 55.6 mOhm cold; a blade and holder |
| (P) Bourns MF-MSMF150/24X (held) | trip 3 A at 23 C | hold 0.88 A at 70 C, under the 1.0 A load; hold 2.1 A at -40 C, so a trip near 4.2 A there | Imax 20 A, under the pack's prospective current | up to 0.12 Ohm |
| (E) TI TPS16630, eFuse (held) | limit 1.4713 to 1.8018 A at R(ILIM) 11.0 kOhm 0.1 % | the printed rows hold over TJ -40 to 125 C (+-10 % at the wider of the 9 and 30 kOhm rows) | current limiting at most 202 ms, auto-retry after 500 to 800 ms (MODE to GND); a soft short off within 4.5 us | RON at most 53 mOhm; HTSSOP-20 |

**SELECTED (SESSION): (E)**, U42 TPS16630PWPR on board A between VBAT and a new net VSYS_DOCK on J_DOCK pin 1; R221 11.0 kOhm 0.1 % on
ILIM (I(OL) = 18 / R(ILIM), Equation 6, p.20), C237 22 nF on dVdT, MODE and OVP to GND, UVLO and P_IN on IN, SHDN, IMON, FLT and PGOOD
open (drafted in `apply_gen_sch_a_charger.py`). It is UL 2367 recognized (p.1). *Why:* the only one of the three that keeps the contact,
the 24 AWG and the copper downstream inside their ratings over temperature and every pulse width it limits. The contact sees at most
**1.802 A, 51.5 % of 3.5 A**: 66.9 C at the 51 C air and 80.9 C at the 65 C margin by w3de's assumed I2 rise, under the spring's 85 C; the
1.0 A load is 68 % of the least limit. *Reverse:* a fan or U12 current over 1.47 A, or a limit read outside the band by E11-38.

**The cases**, source-only and battery alike (the eFuse limits whatever feeds VSYS):
- *Overload* (the 2.88 Ohm counterexample): held at 1.802 A at most, 16.6 W in the eFuse until its timer (or its thermal regulation at
  136 to 154 C), then off for at least 500 ms: a duty of at most 0.288.
- *Soft short:* at most 45 A for 4.5 us, 0.0091 A2s, what 3.5 A gives in 0.744 ms.
- *Hot short* (over I(SCP), 45 A typical): off in about 1 us (typical); the peak is set by the loop's inductance: **CONDITIONAL** on
  E11-38's bench short.
- *Inrush:* C(dVdT) 22 nF +-10 %: ramps of 3.99 to 8.75 ms (Equation 2), 24.3 mA into C31's 10 uF.
- *Recovery:* auto-retry; board A reads HOT-R1 lost meanwhile. The eFuse draws at most 1.7 mA from VSYS: on the source while one
  carries the kit, on the pack otherwise, an addition to the always-on load and never to the held pack's drain.

**The drop**, at the supplement floor 9.688 V with 1.0 A: the eFuse 53 mOhm, the 813 path 43.4 mOhm (w3de's 21.7 at its 2:1 spread) and
the return's shift (2.406 A on an 813 ground contact with one open): **0.1486 V, so VSYS_E at least 9.539 V** (11.905 V at VSYS_MIN's
start). The AP63205 takes 3.8 V and up; the fans' least operating voltage is owed with their maximum (E11-35, extended).

**The held-pack drain, corrected:** 0.1408 mA is the **quantified subset** (the monitor R42 and R43, and D3 at 25 C); D3's hot clamp
leakage and the body diodes' current are not bounded on held evidence; the bench acceptance stays **at most 1 mA** (E11-31).

**check_contracts.py** is in the tree (`v2/ecad/tools/check_contracts.py`, the alias table beside DOCK_SPARE and BLK_SPARE); the
review's packet only omitted it. The interface draft now writes the alias VSYS_DOCK and VSYS_E (board A names its branch after the
eFuse), and the tests apply both of its edit sets to copies.

### 16f. Text drafted for L4-E9's record (this record edits no other record; line numbers as of set 27's `694a8417`)

| Where | Now | Drafted |
|---|---|---|
| L4-POWER-ARCHITECTURE.md line 700 (and D-13's rows, lines 687 and 840) | its drains 0.1408 mA, the bench at most 1 mA / the held pack's drains bounded at 0.1408 mA | its quantified drains 0.1408 mA (the monitor and D3 at 25 C; D3's hot leakage and the battery FETs' body-diode current not bounded on held evidence), the bench at most 1 mA (L4-E11 15a, 16e) |
| line 700 to 701 | the battery FET as a pair of BUK6Y10-30P, every protection event at TJ 150 C or under at 34.42 C/W per FET | the battery FET as a pair of BUK6Y10-30P sized to an RDS(on) allowance of 21.136 mOhm (E11-36), every protection event from the held 20 A at TJ 150 C or under for the installed (Zself + Zmut) of E11-29 (L4-E11 16a, 16b) |
| line 677 (U-04's row) | each FET's installed path (at most 34.42 C/W at the +70 C mixed air, E11-29), the docking pulse's split on the pair (a share of at most 0.848 hot, E11-30) | the pair's installed Zself + Zmut (33.12 K/W steady, 10.753 at 1 s, 3.785 at 20 ms, 0.703 at 244 us, E11-29) at the RDS(on) allowance (E11-36); Ciss against TI's 5 nF (E11-37, open); the docking pulse whole in one FET, VF and ISM hot (E11-30) |
| line 95 (P16) | (B1) VSYS over the dock's pin 1 to board E's VSYS_E | (B1) VSYS through the eFuse U42 (TPS16630, 1.47 to 1.80 A, auto-retry) over the dock's pin 1 to board E's VSYS_E (L4-E11 16e) |

### 16g. What stays for the engineer (handoff rows)

| Affected circuit or function | Evidence and failed condition | Decision or measurement needed | Pass criterion | Consequence of failure | Work blocked |
|---|---|---|---|---|---|
| Q39, Q40: RDS(on) at BATDRV's least drive | no printed maximum at -8.5 V above 25 C (16a) | Nexperia's maximum, or a pulsed Kelvin reading at -8.5 V and 150 C on parts from the lot (E11-36) | at most 21.136 mOhm | the allowance is reversed and the installed path re-sized (at 25 mOhm the held 20 A reaches 152.8 C on the planned board) | E11-29's layout target |
| Q39, Q40: the installed thermal path | the board's transient and the coupling are not printed (16b) | Zself and Zmut on the built board by the VSD method (E11-29) | (Zself + Zmut) at most 33.12 / 10.753 / 3.785 / 0.703 K/W at steady and 60 s / 1 s / 20 ms / 244 us | more copper or a heat path; the service is never lowered | board A's layout release |
| BATDRV with the pair: Ciss | 4.72 nF typical at -15 V, about 5.74 nF near 0 V, no maximum; TI's 5 nF unexplained (16c) | TI's statement (Q-TI-17) or the bench's BATDRV behaviour at -20, 25 and 70 C (E11-37) | supplement entry, the 30 mV ideal-diode regulation without oscillation, LDO mode inside its printed band | the engineer chooses (S2): one FET with a heat path through the case | the charger draft's release (E11-27) |
| The docking pulse in one body diode | VF above 80 A and hot, and ISM at a hot mounting base, not printed (16d) | Nexperia's data or a pulse test on parts; or board P's slower discharge-FET turn-on with its ASCD turn-off shown unchanged (E11-30) | VF at most 1.501 times the stated bound at +70 C; 242.9 A inside the hot ISM | a precharge or slew constraint on board P | none on board A's drawing; E11-27's release |
| The dock's VSYS branch, hot short | the peak is set by the loop's inductance (16e) | the bench short at board E's VSYS_E (E11-38) | the contact's resistance unchanged; the auto-retry seen; the limit inside 1.471 to 1.802 A | a series inductance or a second contact | none |

Not claimed: nothing here is verified, built or measured; software tests establish this record's own behaviour only.
