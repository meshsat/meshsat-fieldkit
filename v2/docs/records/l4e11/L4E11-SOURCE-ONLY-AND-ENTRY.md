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
contact without branch protection). **Round 9** (section 19, 4 October 2026) answers record l9stk's section 15 (the third battery
FET, E11-29 as a junction limit, DD-3, IF-1, C3), record l8p's findings L8P-F02 and L8P-F03, and the owner's reviewer's rebinding of
E11-37 to the three-device network. **Round 10** (section 20, 4 October 2026) answers record l8p's round 3: route R1 and its findings L8P-F04
and L8P-F05 on board A's side of DD-7, and records T2 (E-1's even split) open. **Round 11** (section 21, 4 October 2026, task T2 on
the shared case row C-PROT rev 1) takes E-1 over the worst split of the battery FETs' RDS(on) spread, compares three approaches for E-1
and E11-37, selects one, and applies the two minors of the independent check V1 of round 10. **Round 12** (section 22, 4 October 2026)
answers the independent check V2 of round 11: its blocking finding V2-B1 (the cost of R256 at 6.8 kOhm) as a design choice over V2's
three corrections, and its minors V2-m1 to m5 and m9.

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
- **The second review (section 17):** U42 kept; its fault envelope set out case by case with printed, inferred and typical figures
  apart (566 A for 4.5 us a resistive extrapolation and E11-38 (c)'s test target, not a bound; the start into a short not bounded by
  printed data, its 1.1 to 1.5 s a thermal-regulation timeout that starts when regulation begins); status *sustained-overload remedy drafted;
  fault qualification open* (E11-38); the docking waveform accepted as a whole by a defined pulse qualification (selected, E11-30); the
  charger draft's text corrected; each measurement row names its specimen, and only the final release waits on it.
- **The fans' feed (section 18):** Layer 7's fans print 10.8 to 13.2 V, which VSYS_E does not cover, so the mixers take a regulated 12.0 V
  rail on board E (U22, an ADI LTC3115-1 as its TA04, selected over a TPS55340 SEPIC and the TPS63070, which fails the range; drafted in
  `apply_gen_sch_e_aux.py`); the branch is declared at 1.3208 A, 89.8 % of U42's least limit, so R228 stays; board B's cooler feed is a
  finding for its owner (E11-40).
- **Round 9 (section 19):** L8P-F02 and L8P-F03 corrected in the drafts (board A composed in L4-E9's order runs to its end); **Q42**, the
  third BUK6Y10-30PX, drafted, with record l8p's PTC at the three's centroid; **E11-29** restated as record l9stk's junction limit (each
  FET's Zself + 2 Zmut at most 45.88 K/W with R17 apart, 40.78 K/W for any split since round 11, the pair's fallback 20.39 K/W); **E11-37** rebound to the three (Ciss 7.08 nF
  typical, about 8.61 near 0 V; sharing and coupling read) and OPEN on Q-TI-17 extended or the bench with three; **DD-3 OPEN** after one
  design-out attempt (J_DCIN drafted as the XT60-F, R19 held on its maker's sheet in the continuous rows, a second pass FET selected; it
  fails on L2, 112.37 C at the breaker's 7.136 A from 76.25 C; E11-41); **IF-1** drafted as a VBAT supervisor U46 that holds U42 and
  RAIL_EN until 78.6 ms at least after VBAT passes 8.476 V, against the breaker's 40.7 ms start; PGD not used (E11-42); the guarantee under
  the latch-off -1 stated case by case; **DD-7** (record l9stk 15.4b) drafted in `apply_gen_sch_a_dd7.py`: an input-return pulse on the
  enable loop for the first restart, and a hardware charge inhibit (the battery FETs held off while the loop is powered and the pack's
  terminal is dead) for every latch that takes CELL+ dead, firmware-independent (E11-43 to E11-45); **B-R2 stays OPEN** for a latch while a
  source holds VSYS into a resistive fault (CELL+ held up through the battery FETs, the breaker's PGD high with reverse current): route R1
  on board P (its gate state or a reverse-blocking element), R2 a hardware charge cap on board A.
- **Round 10 (section 20):** record l8p's route R1 (board P holds the loop's return under 0.055 V while a charge passes the off breaker)
  met on board A: **L8P-F04 corrected** (U48 reads the held return under 0.7755 V and the powered loop over 1.981 V at most; the
  inhibit set within 0.85 ms, held at least 1.341 s after the return rises, released on CELL+ alive); **L8P-F05 corrected** (a dead
  CELL+ never sets the inhibit; while it holds, a 4.7 kOhm bleeder keeps CELL+ at 0.154 V at 16.8 V against the 4.076 V dead reading,
  for any source under 0.846 mA); **B-R2 drafted on both boards**; board A composed in L4-E9's order runs to its end and
  `check_dd7_netlist.py` reads DRAWN (five mutations FAIL); **T2 recorded OPEN** (E-1's even split: one FET of three may take 9/8);
  findings L4E11-R10-F1 to F3 for records l8p and l9stk (F3: the PTC's printed points are 100 kOhm over 110 C and 4.7 MOhm at 130 C).
- **Round 11 (section 21, task T2, C-PROT rev 1):** E-1 sized the three battery FETs at the even split; with their RDS(on) spread
  unprinted, one FET at half the others' value takes half the current, 9/8 of the even loss, and at record l9stk's 45.88 K/W its
  junction reads **157.7 C** held at 23.93 A (round 10's "Zself / 7" corrected to **Zself / 4**). Three approaches compared: (i)(a)
  the three kept with the bar taken over the worst split, (ii) two FETs under TI's 5 nF (half the bar, under 5 nF on a typical figure
  only), (iii) a buffer on BATDRV (no printed basis). **SELECTED (SESSION): (i)(a), E11-29's installed (Zself + 2 Zmut) at most 40.78
  K/W** (or the measured Zself and Zmut by 21b's formula), at the charger's printed least drive; E-1's defect **corrected in the
  acceptance**, CONDITIONAL on E11-29 and E11-36; **E11-37 stays OPEN** with Q-TI-17 (e) and (f) drafted (not sent) and (ii) as the
  correction scope on a negative answer. V1's minors: R84 specified pulse-rated; R256's move to 6.8 kOhm is **superseded by round 12**.
- **Round 12 (section 22, the check V2's V2-B1, C-PROT rev 1):** round 11 gave the bleed of CELL+ with no source (1.228 s inside the
  1.341 s hold) beside a static limit of 0.597 mA; with the sources counted, 6.8 kOhm keeps the bleed inside the hold only under
  87.4 uA (V2's arithmetic, reproduced). The sources at their hot bound are 434.8 uA: the LM5069's 1 MOhm, the battery FETs on
  Nexperia's printed 125 C row, the breaker pair on record l8p's ASSUMED doubling. V2's three corrections compared against both
  needs: (a) text only fails the bleed; (c) 6.8 kOhm with a longer hold (C241 2.2 uF) holds it but moves the hold to 12.8 s at most
  and the arm; **SELECTED (SESSION): (b) R256 back to 4.7 kOhm**, the bleed 1.218 s at the hot bound, inside the hold while the
  sources total under 520.7 uA, and U47's RESET at most 4.32 mA in every state without a second fault (6.45 mA, under the absolute
  10 mA, only with CELL+ at VBAT's 29.2 V clamp). **Need 1 stays CONDITIONAL and OPEN** on record l8p's E-14c and on E11-45 (f2):
  no correction holds it on printed figures, the breaker FETs' hot leakage being unprinted. V2-m1 to m5 and m9 carried (22h).
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
| J_DCIN | a board connector of the XT60 class, of the gender opposite J_BATT's so the pack lead cannot mate it, or soldered lead lands; drafted in round 9 as the Amass XT60-F, C98734 (19e) | 30 A rated, 60 A instantaneous, 12 AWG recommended (Amass V1.2); the 60 A's duration is unstated: E11-16 |
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
| E11-12 | implementation | Layer 7 mechanical | the inside lead (at least 20 A) ending in an Amass XT60-M on J_DCIN, which `apply_gen_sch_e_entry.py` now draws as the Amass XT60-F (C98734; round 9, 19e; the gender opposite J_BATT's XT60-M); the lead's polarity matched to J_DCIN's pad 1 (+) as read on KiCad's AMASS land at board E's regeneration |
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
| E11-27 | implementation | Layer 8 board A generator owner | `apply_gen_sch_a_charger.py` applied (sections 14 and 15): U3 BQ25730RSNR (C5219071) with pin 21 on CH_BATDRV; Q39 and Q40, two Nexperia BUK6Y10-30PX (C3278350) in parallel, sources on VBAT, drains on CH_BATQ, gates on CH_BATDRV; R17 and R149 on CH_BATQ; C236 EEHZK1V181P (C242139) on VBAT; U42 TPS16630PWPR from VBAT to VSYS_DOCK with R228 11k 0.1 %, C237 22 nF, MODE to GND, C238 1 uF at IN, C239 0.1 uF at OUT and D23 B540C from GND to OUT, within 20 nH of C236, J_DOCK pin 1 on VSYS_DOCK for board E's VSYS_E (section 16e), the HTSSOP-20 land checked against TI's PWP0020 drawing; CH_BATQ declared a segment of the pack path; the LFPAK56 lands checked against Nexperia's SOT669 drawing, seated by R17 with matched paths; the regenerated netlist reads each |
| E11-28 | firmware | firmware owner | the BQ25730's register rules: EN_OOA 0 at boot; ChargeCurrent written for any charge (0 A at POR and after the watchdog's 175 s), the watchdog serviced or WDTMR_ADJ 00; VSYS_MIN, EN_LDO, EN_PORT_CTRL, BATFET_ENZ and BATFETOFF_HIZ never written from their power-on values; the device ID D5h checked; R-a's bit following the hold flag in every state (S4's exception withdrawn); R-b' under VSYS_MIN: 0x0080 only, and no charge under 5.7 V on SRN (section 15c) |
| E11-29 | layout | Layer 9 pre-layout analysis | the junction limit of record l9stk 15.5 (E-1; round 9, 19c), sized before layout and measured on the specimen of 17d (a coupon or the controlled first prototype; it blocks only the final release): the installed three Q39, Q40 and Q42 on one pour with R17 placed apart, each FET's (Zself + 2 Zmut) at most 40.78 K/W steady by the body diode's VSD method with the band carrying 23.93 A and R17 dissipating in place, R17's coupling into each junction at most 1 K/W (heat R17 alone), so the hottest junction stays at most 150 C held at 23.93 A from 76.25 C for ANY split of the RDS(on) spread under the allowance (round 11, section 21: one FET at R / 2 takes 9/8 of the even split's loss, so record l9stk's even-split 45.88 K/W is taken times 8/9; with Zself and Zmut read apart, the largest of each into any junction, (Zself + 2 Zmut) at most 45.88 x 8 (1 - m)(1 + 2 m) / 9 for m = Zmut / Zself under 1/4, 45.88 at or over it) (the pair's fallback, its Zself + Zmut at most 20.39 K/W, the even split its worst); the pair's former 33.12 K/W target and its 1 s, 20 ms and 244 us targets withdrawn with record l8p's breaker; the 18 A for 60 s and 10 A continuous kept, no protection lowered; the case-rise reading at 10 A alone does not close it; recorded OPEN in round 10 (20i) on the even split, corrected in this acceptance by round 11 (21d), CONDITIONAL on this measurement; the coupon also reads the PTC's site (RT1 at the drain tabs' centroid) against each junction with one FET heated alone at the worst split's 1.513 W, so the thermal guard's trip side is judged on the hottest FET and not on the even split (round 12, the check V2's V2-m5; record l8p's guard) |
| E11-30 | evidence | Layer 6 components | the WHOLE hot docking waveform accepted (sections 16d and 17b): 242.9 A peak, time constant 33.8 us, from a +70 C mounting base, once per docking event, taken whole in one FET's body diode; by the pulse qualification selected in 17b: 6 parts, each 2000 pulses 10 s apart at 267.2 A peak and 37.2 us (x1.1), mounting base 75 C, every part passing VSD at 80 A pulsed within +5 % of its first reading, IDSS at -30 V and 25 C at most the printed 1 uA, RDS(on) at -10 V and 25 C within +5 % and at most the printed 10 mOhm, IGSS at most the printed 100 nA; or Nexperia's written acceptance of the same waveform (Q-NXP-1); a sample result is not a production limit; on a failure board P's owner bounds the inrush (a slower discharge-FET turn-on or a precharge path, its normal charging and its ASCD turn-off re-shown) |
| E11-31 | test | prototype bench | the three modes on the BQ25730 build (EN_OOA 0), piecewise (section 15d): pack absent, VSYS at least 12.054 V; CHRG_INHIBIT 1 with SRN over 12.546 V, VSRN plus 150 mV within 2 percent, under 12.054 V at least 12.054 V, between at least 11.96 V; the held pack current at most 1 mA with board E on VSYS_E; the start from cold at VBUS20 19.15 and 20.96 V, VSYS's maximum capacitance and the always-on loads, at -20, 25 and 62.1 C, with Fault VSYS_UVP clear, the hiccup and latch on a shorted VSYS and the re-plug; VSYS before EN_OOA's write recorded; VSYS's step response in S2 and S4 for each declared step against the converters' floor (D2, 2.054 V of margin), the outlets held by R-c where a step uses more |
| E11-32 | evidence | Layer 6 components | the BQ25730RSNR's supply for the build quantity (five boards) from an authorised source, filed: LCSC read stock 0 on 2 October 2026 (the Layer 6 author's L6P-F05: a procurement fact for the owner's list, not a reselection; TI and its distributors are the next sources to read), and the two battery FETs' (BUK6Y10-30PX, LCSC stock 67) |
| E11-33 | implementation | Layer 8 board E generator owner | `apply_gen_sch_e_aux.py` applied with E11-27 (sections 15a and 18): J_BLK pin 1 on VSYS_E; U12's VIN and EN and C31 on VSYS_E; the mixers' 12.0 V rail +12V_FAN from VSYS_E: U22 LTC3115EFE-1 as ADI's TA04 (L4 XAL6060-103ME 10 uH, C142 10 uF in, C143 22 uF out, C144 4.7 uF PVCC, C145 and C146 100 nF bootstraps, R105 1M and R106 90.9k FB, R107 40.2k and C147 820 pF on VC, R108 10k and C148 33 pF feed-forward, R109 35.7k RT, R103 1.5M and R104 255k RUN, PWM/SYNC to VCC); J_FAN1 and J_FAN2 four pins (12 V, GND, PWM, TACH) with Q9 and Q10 as open-drain PWM drivers and D7 and D8 removed; VSYS_E declared (source J_BLK, 1.32 A: U12 0.8, U22 0.52 at the floor, always on); +12V_FAN declared (source L4, 0.34 A: two fans at 0.17); CELL_F's loads the pack path alone; E6_SW and E6_BST re-declared to VSYS's 17.375 V; the FE and XAL6060 lands checked against ADI's FE20 and Coilcraft's drawings; the regenerated netlist and check_contracts read the dock's pin 1 as VSYS_DOCK and VSYS_E |
| E11-34 | interface | Layer 4 coordinator | `apply_pcb_interfaces_dock.py` applied (IF-AE-DOCK: pin 1 VSYS_DOCK and VSYS_E behind U42's eFuse, the alias, BAT-F06's charge_share replaced by the VSYS feed, the ground return with seven 813 contacts) and section 15e's texts for L4-E9's record: the IF rows of VBAT and the dock, the source-change rows, the two sentences that say no battery FET and the diagram's system-node label (9.688 to 17.375 V) |
| E11-35 | evidence | Layer 6 components | the mixers 9WL0612P4H001 (Layer 7's v2/docs/records/l7pwr/L7-FANS-AND-TH1.md at 2087060b, 2e): their starting current, PWM input level and hole pattern from the maker's manual M0011876C or the bench (Layer 7's F-L7-11); against the rail: the start on a 12.0 V bench channel recorded, and against U42's room 0.1504 A at the floor (section 18b: 1.21 W at the rail, 1.6 times one fan's running power); the supply range 10.8 to 13.2 V is met by the rail's 11.512 to 12.431 V (section 18a), no longer by VSYS_E |
| E11-36 | evidence | Layer 6 components | the battery FETs' RDS(on) at VGS -8.5 V and a 150 C junction at most 21.136 mOhm (the allowance of section 16a): Nexperia's maximum at that point filed, or a pulsed Kelvin reading on parts from the build lot in an oven at 150 C (a sample, not a production limit: only the maker's maximum closes it for every part); a reading over it reverses the allowance and E11-29 is re-sized before layout |
| E11-37 | evidence | Layer 6 components | BATDRV with the three-device network Q39, Q40 and Q42 (round 9, 19d; record l9stk's C3): TI's statement of what the BATFET's 5 nF bounds for three P-channel FETs on one BATDRV (Ciss at which VDS, or a gate charge; Q-TI-17 extended to three, drafted in `clarification/TI-QUESTIONS.md`, not sent), or the bench's BATDRV behaviour with the three (Ciss 7.08 nF typical at -15 V, about 8.61 nF near 0 V) at -20, 25 and 70 C: supplement entry, the ideal diode's 30 mV regulation without oscillation, LDO mode at VSYS_MIN within its printed band, each FET's share of the current in LDO mode and as an ideal diode, and each junction on the shared pour; a result with the pair does not transfer; Q-TI-17 (e) and (f) (round 11, 21d) ask the 5 nF's drain-source voltage, the pair's typical figure and the gate load TI accepts; on a negative answer the supplier's correction scope is round 11's (ii): the pair at its fallback, its bar measured on the coupon, Q42 removed (a draft then owed; 16c, 19d and 21d) |
| E11-38 | test | prototype bench | the dock's VSYS branch, the whole fault envelope (sections 16e, 17a and 18), at -20, 25 and 70 C and at VSYS 9.688 and 17.375 V, ten times each: (a) U42's limit on a slow ramp at VIN - VOUT 1 V between 1.471 and 1.802 A, and recorded at 17 V; (b) an operating overload (2.88 Ohm, and a load just under 2 x I(OL)): settled at or under 1.802 A within 1 ms, off within 202 ms, retry after 500 to 800 ms; (c) a 10 mOhm short applied at board E's VSYS_E while on: the peak through J_DOCK pin 1 recorded against the 566 A extrapolation (a target: a reading over it revises 17a) and over 3.6 A for at most 4.5 us, U42's IN at most 60 V, OUT's least recorded against -0.3 V (Q-TI-18); (d) a start into that short: at most 1.802 A after the first 100 us, the time to thermal regulation and the regulated current recorded, off within 1.5 s of regulation's start, the total on-time recorded; (e) one hour of retry into it at 70 C: the 813's body at most 85 C; (h) an intermittent short applied and removed at 10 Hz, 1 Hz and 0.1 Hz for ten minutes each at 70 C, and removed once during limiting and once during the retry's off-time: the recovery of VSYS_E and U22's rail recorded, the 813's body at most 85 C; for every case the 813's resistance at 1 A four-wire within +10 % of its first reading and at most 20 mOhm, the plunger free, the 24 AWG's body at or under the rating its maker states (F-L7-08; 85 C until one is named) and its insulation unmarked, board A's and board E's copper at the contact lands and under U42 unmarked and at or under 85 C, D23 (VF at 5 A within +5 %) unchanged; (f) with the fans 9WL0612P4H001 on the 12.0 V rail (section 18): U12, U22 and both fans started one at a time by the PWM-duty ramp, and both fans' duty stepped 0 to 100 percent together, at VSYS 9.688 V: U42 never limits (FLT high), VSYS_E at least 9.494 V, U22 never disables (the rail never under 10.8 V), the branch's current at full speed recorded against the declared 1.3208 A; (g) one fan stalled and the 12 V rail shorted at the header, each at 70 C: U22 limits or disables and recovers, VSYS_E never under U12's 3.8 V, the controller keeps running, U42's retry seen or not and recorded |
| E11-39 | firmware | firmware owner | board E's mixer fans (four-wire, on the 12.0 V rail) started one at a time, each by a PWM-duty ramp into the fan's PWM input, never both within 1 s and never while U12 or U22 starts (sections 17a and 18c; Layer 7's F-L7-05): U22's 9 ms soft start covers the rail's rise only, and the fans' start current is NOT READ, so the ramp is what keeps the start near the running current under U42's least limit 1.471 A |
| E11-40 | implementation | Layer 8 board B generator owner | a FINDING, not a draft (section 18d; Layer 7's F-L7-02): board B's J_FAN1 to J_FAN3 carry +5V_Sn (5.1 V) on pin 1 and declare the fan at 0.1 A, and no 12 V net exists on the board; the coolers 9WPA0412P6G001 print 10.8 to 13.2 V: a regulated 12.0 V feed per slot (a step-up from +5V_Sn, Layer 7's 0.436 A each at full speed, keeping an empty slot off) or a 12 V feed from board A over the bay harness; the header's pin 1 becomes 12 V, the slot budget's fan row 2.0 W at 12 V, the module's Fan_PWM and Fan_Tacho kept |
| E11-41 | test | prototype bench | DD-3's condition (round 9, 19e; record l9stk's DD-3): L2 (SRF1260-1R0Y) on board E's land at the TPS48110 breaker's highest held current, 7.136 A, its winding's hot spot read by resistance or a thermocouple in still air at 76.25 C (or referred to it), three samples: at most 105 C including the rise; or Bourns's statement of the rise in this connection; or a choke rated at least 8.42 A at a 40 K rise with board E's input filter shown again to its attenuation; a reading over it returns to L4-E11 for the choke, and the second pass FET of 19e is drafted with the choke in one board E change |
| E11-42 | test | prototype bench | IF-1's hold (round 9, 19f) on board A's first prototype docked onto a board P carrying record l8p's breaker, with no source: (a) twenty dockings, U42's output and RAIL_EN low until at least 78.6 ms after VBAT passes 8.476 V, and the breaker's start ending with its TIMER under the fault threshold, each recorded; (b) an undocking and redocking after 0.5, 1 and 2 s with VBAT held up by board A's capacitance: U46 asserting as VBAT falls under 8.309 V and the following start held the same way; (c) MAIN held through a docking: the release to KILL recorded, at least 207.7 ms of U1's blanking left; (d) with a source present at the plan load, the breaker's start completing, or the -1 latching while the source keeps the kit up, as 19f bounds; (e) the static draw from VBAT while U46 holds at most 40 mA at 16.8 V |
| E11-43 | implementation | Layer 8 board A generator owner | `apply_gen_sch_a_dd7.py` applied after record l8p's `apply_gen_sch_a_ptc.py` and this record's charger draft, released with l8p's three drafts (rounds 9 and 10, 19h and 20; record l9stk's DD-7, record l8p's route R1 and its L8P-F04 and L8P-F05): the input-return reset Q44 to Q46, R106 and D25 on DOCK_EN_RET (Q46's gate on DD7_N); the loop reader U48 with R109, R144, R249 and R250; the hold and the release on CELL+ alive U47 with C241, R85, C248, R107, R108, Q52, R254 and R255, the arm Q50, Q51, R251, R252, R253, R84 and D26; the charge inhibit Q47, Q49, R82 and R83 on CH_BATDRV and the bleeder Q48 and R256 on CELL+; DD7_VC from R233 and D27; TP1 and TP2; the layout keeps Q49 within 10 mm of the battery FETs' gate node and U47 and U48 beside C238, their VDD bypass; R249 to R256 and C248 sit above the main-based order's highest, so d8dec31's mainpb takes the next ones; `check_dd7_netlist.py` reads DRAWN on the regenerated netlist; L4-E9's change list keeps the draft after l8p's PTC and before mainpb (the integrator's) |
| E11-44 | firmware | firmware owner | record l9stk's IF-7 with 19h's hardware: the bridge reports a tripped breaker (the BQ25730's ADC reads SRN dead while the gauge reports its FETs on, or the charge inhibit holding) and writes ChargeCurrent only after the terminal reads alive; R-b's bound kept; the hardware inhibit holds the charge whether or not this rule runs |
| E11-45 | test | prototype bench | DD-7 and E-14 (rounds 9 and 10, 19h and 20) on board A's first prototype with board P's -1 breaker and record l8p's reverse-charge detector: (a) the -1 latched by a fault, no source, then an input applied as a step and as a 1 V/ms ramp at 9, 12, 24 and 36 V: DOCK_EN_RET low for at least 78.6 ms and the breaker restarting within 1.149 s of VIN_RAW passing U34's threshold (the pad under C-1c's trip); (b) with the pack alive, an input's arrival leaves DOCK_EN_RET unchanged and the kit up; (c) E-14 extended: a hard short kept on VSYS, so the -1 latches again with the input present, and ChargeCurrent forced to its register maximum by the host: the current into PACK_P at most 1 mA and the breaker FET's junction (VSD method) within 2 K of its case for 10 minutes; (c2) the same with a 0.915 ohm fault removed after the latch (B-R2, route R1): the charge into PACK_P ends within 1.41 ms of passing board P's threshold, TP2 (DD7_N) low within 0.85 ms of DOCK_EN_RET falling, the battery FETs held off at least 1.341 s after DOCK_EN_RET rises (TP1 over 0.79 V), then released once CELL+ reads alive, the breaker restarted within 0.948 s; (d) failures, each found by its row: U47's RESET1 held high (the hold lost, (c2)), Q48 opened (the latch reads the leak, (f)), Q49's gate opened (the inhibit lost, (c)); (e) L8P-F04's interface alone: DOCK_EN_RET pulled under 0.06 V by a stand-in at BRK_VIN 7.6, 10.6 and 16.8 V with RT1 replaced by 5 kOhm: CH_BATDRV at VBAT within 1 ms whatever CELL+ reads, released no earlier than 1.0 s after the release; the loop closed at RET 0.9 V and DOCK_EN_OUT 2.0 V: nothing inhibited (20c); (f) L8P-F05: the breaker held off with BRK_VIN at 16.8 V and, from a bench supply through 10 mA, at 29.2 V: CELL+ under 3.58 V while the inhibit holds and the inhibit kept until the breaker is enabled; (f2, round 12, the check V2's V2-B1) the bleed timed: CELL_FUSED charged to 17.4 V, the inhibit set and the breaker held off, the battery FETs' pour at 125 C and the breaker FETs' case at 101 C (or 435 uA injected into CELL+ on a cold board): CELL+ under 4.076 V at least 0.1 s before the same unit's hold ends as (h) times it; the current into CELL+ with both FET groups hot read, at most 521 uA; U47's RESET current read at the set and with the breaker restarted, at most 5 mA; (g) a back-fed precharge (the gauge's FETs off, the charger in LDO mode) at 25 and 70 C: CH_BATDRV follows BATDRV and nothing is inhibited; (h) the hold timed from five triggers at -20, 25 and 85 C: at least 1.0 s each, and each at least 0.1 s longer than (f2)'s bleed on the same unit |

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
| D1, N1a | VSYS's DC regulation with no battery current: VBAT_REG_ACC +-0.5 % is a charge-voltage row at 0 to 85 C (SLUSE66A p.9); section 11 (p.92) says only that the system is powered through the charger; Figures 10-4 and 10-5 (p.89) are typical power-up curves without battery | line 204: section 2's "absent, or both FETs open: VSYS at ChargeVoltage", and every S4 figure of 3g and 3h | that the loop holds VSYS at ChargeVoltage with no battery current, the +-0.5 % row applying: production-wide if stated as a limit | **can:** that one unit enters and holds the mode at the conditions tried; the mode is a design behaviour, and VSYS needs only 12.3 V against ChargeVoltage's floor 16.716 V, a 4.416 V margin, large against any plausible spread once the mode is shown. **Cannot:** that every unit and silicon revision enters the mode, or the accuracy below 0 C | pack absent, P1's load and the envelope's maximum on VSYS, VBUS20 19.1 to 21 V, VSYS on a calibrated meter at -20, 25 and 62 C ambient | (A) cannot run S4: (B), a charger whose battery FET regulates VSYS by design (an architecture change; five records reopen) |
| D2, N1b | VSYS's load-step response with no battery: no load-transient figure or limit for the system output (Figure 10-17, p.91, is the OTG output's) | line 458: R-c and 3g's S4 operation through the kit's load steps, up to 48.39 W | a characterised deviation and recovery, or a minimum loop bandwidth; production-wide only if TI states a limit | **can:** one unit's deviation and recovery; with the bank sized for 1 ms, a measured recovery of 0.2 ms or less is a five-fold engineering margin against a loop's plausible spread. **Cannot:** a recovery time bounded for every unit | pack absent, an electronic load stepping VSYS by each declared step with a 1 us edge, VSYS and the inductor current on a scope, at three ambients | the bank of out 10 carries the worst admitted step for 1.117 ms with no help from the charger; longer needs more cans (8 for 2 ms) or (B) |
| D3, N2 (Q-TI-3) | VSYS with CHRG_INHIBIT = 1 or ChargeCurrent 0 and no battery current: 9.4.1 (p.35) lets the host end a charge either way; 9.3.21.5 (p.34) keeps the converter operating with charge disabled only in the BATOVP paragraph | line 425: R-a's S2 row, and REQ-077's hold in every state: the charger still carrying the kit while the charge is held | the control mode with charge inhibited, production-wide (a design behaviour) | **can:** one unit's mode with the bit set and with ChargeCurrent 0, pack absent and in S2: a deterministic logic behaviour, so strong evidence for that silicon revision. **Cannot:** that no later revision changes the mode, nor a temperature-dependent comparator's effect | the pack emulated in S2 (a supply behind a diode), the bit set and cleared under P1's load, VSYS and the switch node recorded | REQ-077's hold cannot use the bit with this charger; ChargeCurrent 0 is tried; if both fail, (B) or a change to REQ-077's acceptance (the owner's) |
| D4, N3 (Q-TI-2) | whether it charges before any host write: 9.6.3 says on a host write; the reset value encodes 256 mA; TI's expert on E2E (held): the POR value is 256 mA, 9.6.3 not addressed | line 191: section 2's ChargeCurrent at POR, R-a's persistence after a charger POR, CONOPS's hostless 256 mA | a datasheet erratum: production-wide (a forum answer is TI's word, not a revised document) | **can:** one unit's SRP-SRN current after POR with no host: a logic behaviour, strong for that revision. **Cannot:** other revisions | no host, the pack at 3.6 V a cell, SRP-SRN read for 200 s after POR | a hostless 256 mA charge is safe (inside the gauge's window; Q2's diode 0.256 W); no hostless charge leaves a hostless kit's dead pack uncharged: a stated limitation |
| D5, N4 | VSYS's effective capacitance at 16.884 V against TI's 50 uF (10.1, p.83): the fitted MLCCs' DC-bias capacitance is not printed in the held Yageo CC sheet (a capacitor maker's item) | line 657: N1's premise and E11-07 | the capacitor makers' DC-bias curves: typical per part number, not limits | **can:** one board's VSYS capacitance at 16.8 V of bias. **Cannot:** lot-to-lot spread | an LCR meter with DC bias on the populated node | none needed: the direct EEHZK1V181P gives 90.72 uF at its stacked worst, no DC-bias dependence, over 50 uF by design |
| D6, Q-TI-7 | 0-V charging before the gauge's SUV check: SLUUAQ3A 4.9 enables the 0-V circuit with PCHG_COMM = 1; its timing against 3.2.1's SUV check is not stated | line 462: R-d: no cell below 1.0 V charged (Samsung) | the gauge's sequence, production-wide | **can:** one gauge with a cell simulator: a logic sequence, strong for that firmware. **Cannot:** other firmware revisions | a cell simulator at 0.8 V a cell, the charger enabled, the stack current logged from wake | ZVCHG Exit Threshold set to stop 0-V charging, or a precharge FET with PCHG_COMM 0 (arrangement (C)'s part) |
| D7 | the clamp's maximum under VSYS_MIN: 384 mA typical only (SLUSE66A 8.5, p.10) | line 449: R-b's case (iii), Q2's diode below VSYS_MIN | a maximum, production-wide | **can:** one unit's clamp current; Q2 reaches 150 C only at 1.758 A on its 50 C/W, 4.58 times the typical clamp, so a sample near typical is a large engineering margin. **Cannot:** a maximum | SRN held at 11 V by a sink, 0x0200 set, the current read at three temperatures | a maximum over 1.758 A: Q2's copper improved, or arrangement (C) |
| D8 | ChargeCurrent's accuracy at 0x0200 outside 0 to 85 C, and under 0x0200 (p.10) | line 448: R-b's case (ii), Q2's 124.9 C (CONDITIONAL) | limits outside the range, production-wide | **can:** one unit at -20 and 62 C; Q2's limit 1.758 A is 1.4 times R-b's 1.2567 A, so a sample within about 1.3 A is an engineering margin. **Cannot:** production limits | as D7 with SRN at 13 V | the charger's temperature bounded inside the row by layout (E11-22), or Q2's copper improved |
| D9 | the TPS48110-Q1's overcurrent delay at CTMR 22 nF: 370 us typical only (SLUSEE5E p.10) | line 262: V-A08's 0.247 ms and the fault scan's 0.49 ms (A11-11) | a minimum and a maximum over temperature, production-wide | **can:** one unit's delay; the scan's worst fault ends on the short-circuit trip, so the maximum does not decide it; the minimum sets V-A08. **Cannot:** the spread | a current step over the threshold at three temperatures, sense to PD timed | V-A08's allowance re-derived on TI's minimum, or CTMR raised |
| D10 | the CSD19536KTT's transconductance: 329 S typical only (SLPS540C p.3) | line 280: the start into a hard short, 0.743 of the derated chart | a maximum, or the transfer curve's spread | **can:** one unit's transfer curve; the 1.346-fold headroom is not large against a plausible spread, so **no** margin. **Cannot:** a bound across units | a pulsed transfer curve at VDS 10 V, 10 to 100 A | a slower gate slew for the start, or a power-limiting controller |

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
fallback); the three FETs' junction limit (E11-29 since round 9, the pair's thermal bar superseded; its even split OPEN, 20i) and the docking pulse's split (E11-30); the start's first window and the held pack
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

**VSYS_E's range:** the supplement floor 9.688 V to 17.375 V (15d). The AP63205 takes 3.8 to 32 V (Diodes DS41326 p.1). *The fans
directly on VSYS_E are withdrawn by section 18:* Layer 7's fans print 10.8 to 13.2 V, so the mixers run on a regulated 12.0 V rail (U22)
from VSYS_E, and the branch is declared at 1.3208 A (18b).

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
| L4-F02 objection 4, the docking pulse | **CONDITIONAL** (E11-30; its acceptance rewritten by 17b: the whole hot waveform, by a pulse qualification) | ISM 320 A for 10 us at Tmb 25 C (Table 5 p.3) against the 242.9 A peak, one FET; TJ 123.3 C from +70 C on the printed VSD (1.2 V at 80 A, p.6) carried up by concavity; VF hot and ISM hot not printed |
| The 18 A for 60 s service from the hot state | **CONDITIONAL** on E11-29 and E11-36 | TJ 126.7 C from 87.5 C at 10 A held, +70 C air, no board capacity credited |
| L4-F03, the dock's VSYS branch | **sustained-overload remedy drafted; fault qualification open** (17a, E11-38; the 566 A is an extrapolation and a test target, the start into a short is not bounded by printed data) | TI TPS16630 (SLVSET9G pp.8 to 10, 20, 26) at R(ILIM) 11.0 kOhm: 1.4713 to 1.8018 A; the 813 at 51.5 % of 3.5 A |
| The held-pack drain wording | **CORRECTED** (15a and the text drafted for L4-E9 below) | 0.1408 mA is the quantified subset; the 1 mA bench acceptance kept |
| the fans' feed (section 18, after Layer 7's D-18) | **SELECTED and DRAFTED** (U22); the declared current 1.3208 A, R228 kept; board B **OPEN** (E11-40) | the fans print 10.8 to 13.2 V; VSYS_E runs 9.494 to 17.375 V |
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
a negative answer the engineer's choice between (S1) and (S2). *Superseded in part by round 9 (19b, 19d): a third FET, Q42, on record
l9stk's junction limit; E11-37 bound to the three, the pair its fallback.*

### 16d. Objection 4: the docking pulse

Section 15c's reading of ISM's 320 A for 10 us as an I2t of 1.024 A2s **is withdrawn**: the sheet prints no I2t. The waveform (the
dependency round's pack loop, the discharge FET at once): **242.9 A peak, time constant 33.8 us**. It is over the continuous IS 80 A
(Tmb 25 C, Table 5 p.3) for 37.6 us and still 180.7 A when ISM's 10 us ends. **No sharing is credited:** the whole pulse is taken in one
FET (the sheet prints VSD's maximum and no minimum, so the split cannot be bounded).

**Its junction from +70 C:** P = VF x i with VF at most max(1.2 V, 1.2 V x i / 80 A): the printed maximum at 80 A and 25 C (p.6) carried
up by VF's concavity in i (3.643 V at the peak, INFERRED); superposed on Fig. 4 as scaled: **a rise of 53.3 K, TJ 123.3 C**, 16.68 mJ,
885 W at the peak. The bound is reached at once because Fig. 4 is held at its first read point (12 us, 0.0602 K/W, 4.3 % of its steady
value) below that width, a bound and not a waveform; within 12 us the heat is still inside the package, so the board below cannot add to
it. *[Historical, overridden by 17b: this round judged the waveform past ISM's 10 us on the junction temperature alone; a temperature does
not extend a printed pulse rating, so 17b accepts the whole hot waveform by a qualification instead.]* **What the sheet does not print:** VF above 80 A or at a hot junction (TJ stays under 150 C while
VF is at most 1.501 times that bound), and ISM at a mounting base over 25 C (the 242.9 A peak is 75.9 % of 320 A at 25 C). **CONDITIONAL**
on E11-30: both from Nexperia or a pulse test on parts. The constraint that would remove both, a slower turn-on of board P's discharge
FET, interacts with the pack's ASCD turn-off and belongs to board P's owner; it is named in E11-30, not drafted here.

*Section 17b rewrites this item's acceptance: the whole hot waveform, by a defined pulse qualification on parts (selected), with
Nexperia asked in parallel and board P's inrush limit the fallback.*

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

**SELECTED (SESSION): (E)**, U42 TPS16630PWPR on board A between VBAT and a new net VSYS_DOCK on J_DOCK pin 1; R228 11.0 kOhm 0.1 % on
ILIM (I(OL) = 18 / R(ILIM), Equation 6, p.20), C237 22 nF on dVdT, MODE and OVP to GND, UVLO and P_IN on IN, SHDN, IMON, FLT and PGOOD
open (drafted in `apply_gen_sch_a_charger.py`; 17a adds C238, C239 and D23). It is UL 2367 recognized (p.1). *Why:* the only one of the
three whose printed rows keep the contact, the 24 AWG and the copper downstream inside their ratings in a sustained overload over
temperature. In a sustained overload the contact sees at most **1.802 A, 51.5 % of 3.5 A**: 66.9 C at the 51 C air and 80.9 C at the 65 C margin by w3de's assumed I2 rise, under the spring's 85 C; the
1.0 A load is 68 % of the least limit. *Reverse:* a fan or U12 current over 1.47 A, or a limit read outside the band by E11-38.

**The cases**, source-only and battery alike (the eFuse limits whatever feeds VSYS):
- *Overload* (the 2.88 Ohm counterexample): held at 1.802 A at most, 16.6 W in the eFuse until its timer (or its thermal regulation at
  136 to 154 C), then off for at least 500 ms: a duty of at most 0.288.
- *A short applied while on, a start into a short, and the retry:* section 17a. The first version's soft-short figure (45 A for 4.5 us,
  0.0091 A2s) is **withdrawn**: TI prints 45 A as a typical only, and a limiter's steady setting is not an instantaneous ceiling.
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
| BATDRV with the three (since round 9, 19d; the pair's 4.72 and 5.74 nF superseded): Ciss | 7.08 nF typical at -15 V, about 8.61 nF near 0 V, no maximum; TI's 5 nF unexplained (16c) | TI's statement (Q-TI-17) or the bench's BATDRV behaviour at -20, 25 and 70 C (E11-37) | supplement entry, the 30 mV ideal-diode regulation without oscillation, LDO mode inside its printed band | the engineer chooses (S2): one FET with a heat path through the case | the charger draft's release (E11-27) |
| The docking pulse in one body diode | VF above 80 A and hot, and ISM at a hot mounting base, not printed (16d) | Nexperia's data or a pulse test on parts; or board P's slower discharge-FET turn-on with its ASCD turn-off shown unchanged (E11-30) | VF at most 1.501 times the stated bound at +70 C; 242.9 A inside the hot ISM | a precharge or slew constraint on board P | none on board A's drawing; E11-27's release |
| The dock's VSYS branch, hot short | the peak is set by the loop's inductance (16e) | the bench short at board E's VSYS_E (E11-38) | the contact's resistance unchanged; the auto-retry seen; the limit inside 1.471 to 1.802 A | a series inductance or a second contact | none |

## 17. The second review (L4-CP01 to L4-CP03) and the evidence specimens (out 17)

A second external review, of the 22:30 checkpoint that carried `d2a59468`, keeps U42 and section 16's labelling and finds three targeted
items. It reproduced 1.471256 / 1.801802 A, 33.11828 K/W, 87.5 / 126.7 C, 152.7957 C and 123.3078 C; those stand. Nothing here is
evidence of a failure. Classes in 17a: **G** a printed limit (minimum or maximum), **I** inferred, **T** typical only (TI SLVSET9G Rev. G).

### 17a. L4-CP01: U42's fault envelope, case by case

**The setting.** I(OL) is 1.4713 to 1.8018 A at R(ILIM) 11.0 kOhm: **I**, between the printed 9 and 30 kOhm rows, each **G** over TJ
-40 to 125 C at VIN - VOUT = 1 V (p.8), by Equation 6 (p.20). It is a regulated, steady setting and **not an instantaneous ceiling**. The
fast-trip threshold (2 x I(OL)) and I(SCP) (45 A) are **T** only (p.8). Section 16e's soft-short figure built on the typical 45 A
(0.0091125 A2s) is withdrawn.

| Case | What TI prints (p.) | The bound here | What the bench must still settle (E11-38) |
|---|---|---|---|
| (1) operating overload, I(OL) < I < I(FASTTRIP) | held at the setting once its loop settles (8.3.4.1); limiting at most 202 ms (**G**, 129 to 202, p.10), then off 500 to 800 ms (**G**, p.10) and a retry (Table 8-1, p.26) | the contact at most 1.802 A once settled (**I**), 15.9 K by w3de's assumed rise; a duty of at most 0.288 | the settling's peak (no loop bandwidth printed) |
| (2) a short applied while on | turn-off 2.2 to 4.5 us for I(FASTTRIP) < I < I(SCP) (**G** times, from a **T** threshold, p.10); about 1 us over I(SCP) (**T**); then a slow turn-back-on into case (1) (8.3.4.2, p.21) | a resistive **extrapolation, not a bound** (**I**): **566 A** would flow if VSYS's 17.375 V stood over RON's printed least 19 mOhm and the path's 11.7 mOhm with the contact at 0 and no inductance; TI prints RON at 0.6 to 6 A only (p.9), so the FET's resistance at hundreds of amperes, its saturation and the loop's inductance are not printed. 566 A for 4.5 us (1.441 A2s) is **E11-38's test target** for the recorded peak; a reading over it revises this row | the actual peak and its width; the 813's pulse capability (Preci-Dip prints 3.5 A operating only); the 24 AWG and board copper; D23 |
| the pins in case (2) | Equation 14 (p.30): Vspike = VIN + I x sqrt(LIN / CIN); a Schottky at OUT for the negative spike (9.4.1, 9.5.1, p.31); IN, OUT -0.3 to 67 V (6.1, p.7) | IN at most **41.1 V** at the 566 A extrapolation with U42 within 20 nH of C236 (90.7 uF effective at its stacked worst, ESR 27 mOhm printed); the 20 nH is a layout requirement (SESSION) | OUT's undershoot: a clamp at hundreds of amperes cannot be shown to hold -0.3 V (Q-TI-18) |
| (3) a start into a pre-existing short | "the current begins to limit at I(OL)" until the junction reaches T(J_REG) 136 to 154 C (**G**); then a lower, regulated current for the **timeout** t(Treg_timeout) 1.1 to 1.5 s (**G**, p.10), which starts when regulation begins; then off (8.3.4.2.1, p.22) | at most the setting until regulation; the time to reach regulation (VIN x I(OL) into the package from the air) and the regulated current are **not printed**, so the total on-time and the energy into the contact are **not bounded by printed data** (the first version's "at most 1.5 s" is withdrawn) | the current at 17.4 V across U42 (the setting's row is printed at 1 V), the pre-regulation interval, the regulated current and the total on-time: E11-38 (d) |
| (4) repeated retry into a persistent short | each cycle is case (3), off at least 500 ms (**G**) between | the cycle's on-time is not bounded (3), so **no duty is claimed** (the first version's 0.75 from the timeout alone is withdrawn); what holds: after the first microseconds the current never exceeds the setting, so at any duty the contact's heating is at most case (1)'s 15.9 K by w3de's rise (**I**) | an intermittent short applied and removed faster than the retry, and the recovery between: not bounded by the device's timers, E11-38 (h) |

**The hotter interval.** The current U42 regulates while its junction sits at T(J_REG) is not printed (under the setting; how far is unknown):
E11-38 (d) records it.

**Source impedance and local capacitance.** In both source-only and battery operation the first microseconds of a short come from VSYS's
local capacitance (C236 and C23 to C25), not from the source; the extrapolation above credits neither the source's impedance nor the capacitors'
ESR, so it holds for both. **Temperature:** every **G** row above is over TJ -40 to 125 C; in normal service U42 carries 1.0 A through at
most 53 mOhm. **Added to the draft** (TI's recommendations): C238 1 uF at IN (9.4.1), C239 0.1 uF at OUT (6.3's 0.1 uF minimum at OUT)
and D23 B540C-13-F (C72264, Diodes DS13012, held) from GND to OUT (9.4.1, 9.5.1).

**The fans' start** (as first written, with the fans directly on VSYS_E; superseded by section 18, which puts them on a regulated 12.0 V
rail behind U22 and re-derives the branch at 1.3208 A). Against U42's least limit 1.471 A with U12's 0.8 A: both fans together at most
**0.3356 A each**; one at a time at most **0.5713 A** (the other running at 0.1 A). VSYS_E at the least limit is at least **9.494 V** at
the supplement floor. **E11-39** (firmware): the fans start one at a time, each with a PWM ramp (restated in 18c).

**STATUS: sustained-overload remedy drafted; fault qualification open (E11-38).** E11-38 now covers the complete relevant histories with
pass limits: the limit at 1 V and 17 V; the overload settling and its timers; the hard short's peak recorded against the 566 A target, over
3.6 A for at most 4.5 us, IN at most 60 V, OUT against -0.3 V; the start into a short with its pre-regulation interval, regulated current
and total on-time recorded; one hour of retry at 70 C; intermittent shorts at 10, 1 and 0.1 Hz and removals during limiting and during the
off-time (h); and after every case the 813's resistance within +10 % of its first reading and at most 20 mOhm with its body at or under
85 C, the plunger free, the 24 AWG's body at or under its maker's rating (85 C until one is named, F-L7-08) with its insulation unmarked,
the copper at the contact lands and under U42 unmarked and at or under 85 C, D23 unchanged; the fans' start with no limiting.

### 17b. L4-CP02: the whole hot docking waveform

A junction-temperature calculation does not extend ISM's printed rating (320 A, single pulse, tp at most 10 us, Tmb 25 C; Table 5,
p.3). The waveform to accept: **242.9 A peak, time constant 33.8 us**, over IS's 80 A for 37.6 us, from a +70 C mounting base, once per
docking event (the pack's discharge FET switching onto an empty VSYS), taken whole in one FET's body diode.

| | Basis | Circuit change | Interacting controls | Cost, time |
|---|---|---|---|---|
| (D1) Nexperia's written acceptance of the waveform (Q-NXP-1, drafted, not sent) | the maker | none | none | an answer outside this project's control |
| (D2) a defined pulse qualification on parts | samples, within a stated scope | none | none | 6 parts (BUK6Y10-30PX, LCSC C3278350, 1.7386 USD each at 10, read 2 October 2026) and a capacitor-discharge rig |
| (D3) board P bounds the inrush (a slower discharge-FET turn-on, or a precharge path) | a designed limit | board P's protection path | the pack's ASCD turn-off and normal charging must be re-shown | a draft for board P's generator and its owner's register row |

**SELECTED (SESSION): (D2)**, with (D1) asked in parallel. *Why:* it needs no circuit change and touches no protection, and the review
accepts "a defined prototype qualification within its stated scope". The qualification (E11-30): 6 parts, each 2000 pulses 10 s apart
(a lifetime allowance of 1000 docking events, twice; SESSION) at **267.2 A peak and 37.2 us** (1.1 x the waveform), the mounting base at
75 C; every part passes VSD at 80 A pulsed within +5 % of its first reading, IDSS at -30 V and 25 C at most the printed 1 uA, RDS(on) at
-10 V and 25 C within +5 % and at most the printed 10 mOhm, IGSS at most the printed 100 nA. A sample result is not a production limit.
*Reverse:* a failure moves to (D3), board P's owner. **STATUS: CONDITIONAL on E11-30.**

### 17c. L4-CP03: the charger draft's text

`apply_gen_sch_a_charger.py`'s `_PAIR` text no longer writes the three withdrawn statements (each FET "bounded" at 21.1 mOhm, "34.4
C/W per FET", E11-30 establishing the split between the two diodes). It now writes the allowance (E11-36), the 33.12 K/W self-plus-mutual
target with its 1 s, 20 ms and 244 us limits (E11-29) and the whole pulse in one body diode with no sharing credited (E11-30); its U42
text says the setting is steady and not an instantaneous ceiling. The test applies the draft to a copy and checks that the three
statements are absent from what it writes.

### 17d. The evidence specimens: prototype evidence apart from the release it gates

E11-29 asked a built board for junction temperatures under "pre-layout analysis", and a release gate on it would be circular. Each
measurement row below names its specimen. The evidence builds proceed under their own scope; **only the final design or production
release stays held** until the measurements pass. Purchases stay the owner's; nothing is bought.

**What a specimen's result is, and what it is not (the owner's review of 3 October, L4-QR01).** A junction-to-ambient figure belongs to the
board and its environment, not to the device: TI's "Semiconductor and IC Package Thermal Metrics" (SPRA953D, revised March 2024, the
revision TI serves for SPRA953C; held) states in 1.2 (p.3) that "RθJA is not a constant" and in 1.8 (p.5) that it "is a system-level
parameter that depends strongly on system parameters". A maker's limiting value holds under its stated conditions only: Nexperia's AN11158
(Rev. 7.0, 18 February 2025; held), 2.4 (p.4): operation outside the stated conditions carries no assurance from the maker. So **a coupon's thermal result
transfers only where the final board's thermal boundaries are shown no worse by a named rule, and a sample's pulse result is prototype
evidence for that lot and those conditions, never a production limit or an extension of the maker's guarantee.** Each row's block below
records its specimen, lot, operating point, mounting, thermal boundaries, measurement uncertainty, permitted extrapolation, the rule for
any final-board comparison and what requires a re-test. The first version's wording that the docking pulse capability is
"layout-independent", and that E11-29's result transfers on copper area, layers, weight and vias alone, is **withdrawn**.

| Row | Specimen | Represents | Transfers | Blocks only |
|---|---|---|---|---|
| Row E11-29 | a power-stage coupon of board A's battery-switch region, or the controlled first prototype of board A | the three FETs' self and mutual junction-to-air impedance in their thermal environment, with the band and R17 in place (round 9, 19c) | the steady figures only by the comparison rule of its block; the transients only from a region copied unchanged or from the first prototype | board A's final release |
| Row E11-30 | six BUK6Y10-30PX samples on single-device coupons on a heated mounting base, and a capacitor-discharge rig | the device under the whole hot docking waveform, one FET carrying all of it | to the build only for the tested lot and inside the tested envelope; prototype evidence, not a production limit | board A's final release |
| Row E11-36 | BUK6Y10-30PX samples on a Kelvin coupon in an oven | RDS(on) at VGS -8.5 V and a 150 C junction | to the lot read, at a drive at least 8.5 V and a junction at most 150 C; only Nexperia's maximum holds for every lot | the sizing's confirmation and board A's final release |
| Row E11-37 | TI's BQ25730 evaluation hardware (whether TI offers one, and its price, not read) modified as drafted, or the controlled first prototype of board A | BATDRV with the three FETs' gate load, their sharing and coupling (round 9, 19d) | only when the gate loop, the three FETs and VSYS's capacitance are the draft's | the choice between (S1) and (S2) for the final design |
| Row E11-38 | a coupon of the dock's VSYS branch (U42 and its network, VSYS's local capacitance, one 813 in a dock block, 60 mm of 24 AWG, a board E stub with C31, U22's rail and the fan headers), or the first prototypes of boards A and E | the branch through the fault envelope of 17a | U42's limits and timings as device properties of the lot; peaks, pin spikes and contact temperatures only where the block's comparison rule holds | board A's and board E's final release |
| Row E11-35 | the fans Layer 7 selected (Sanyo Denki 9WL0612P4H001) on a 12.0 V bench channel and on E11-38's coupon behind U22 | the fans' starting current and PWM input level | the start current as a property of the fan's lot within the tested voltage and temperature; the installed running current only from the first prototype | the fans' acceptance for board E's final release |

#### Block E11-29: the three FETs' installed thermal path and the junction limit (restated in round 9, 19c, and round 11, 21)

- **The limit (record l9stk 15.5, E-1):** the hottest battery FET's junction at most 150 C held at 23.93 A from 76.25 C, with the pack
  band carrying the current (9.16 K) and R17 dissipating its 2.86 W in place, **for any split of the RDS(on) spread under the
  allowance** (round 11): each FET's installed (Zself + 2 Zmut) at most **40.78 K/W** steady with R17 placed apart and R17's coupling
  into each junction at most 1 K/W. With Zself and Zmut read apart the bar is record l9stk's even-split 45.88 K/W times 8 (1 - m)(1 +
  2 m) / 9 for m = Zmut / Zself under 1/4 (21b's table), 45.88 K/W at or over it. The pair's fallback 20.39 K/W (the even split is
  its worst). The pair's former
  33.12 K/W target at +70 C air and its 1 s, 20 ms and 244 us targets are withdrawn with record l8p's breaker (no current over 23.93 A
  outlasts its clearing); without the breaker, record l9stk's DD-1 stays open.
- **Specimen:** a coupon of board A's battery-switch region (Q39, Q40 and Q42 on the drafted LFPAK56 lands, R17 placed apart as drafted, the
  VBAT and CH_BATQ copper, the pack band carrying its current, the intended stack-up, copper weight and via field, and record l8p's PTC at
  the drain tabs' centroid), or the controlled first prototype of board A.
- **Lot:** the three FETs' reel and date code and the coupon's fabricator, stack-up and copper weight, recorded. Each unit's own
  junction-to-mounting-base impedance is a unit property: read on a cold plate before mounting (the transient dual-interface method), so
  the board's part can be separated from the unit's; for other units the printed maximum Rth(j-mb) 1.4 K/W less the coupon units' reading is
  added.
- **Operating point:** each FET heated through its body diode at the held limit's 1.345 W per FET (23.93 A over three at the 21.136 mOhm
  allowance), all three together and each alone (each alone gives Zself and the two Zmut, from which m and 21b's bar follow); the band
  carrying 23.93 A from a separate supply; R17 heated alone at 2.86 W for its coupling; junction read by VSD at a small sense current
  against a K-factor calibrated in an oven; readings at 60 s and steady. Unequal impedances (the middle FET couples to two
  neighbours) are judged by the largest Zself and the largest Zmut into any junction: the hottest rise over every split grows with
  each, so the bound holds (INFERRED). **With each FET heated alone at the worst split's 1.513 W, the PTC's site (RT1, at the drain
  tabs' centroid) is read against that FET's junction** (round 12, the check V2's V2-m5): record l8p's guard adds the even split's
  rise to its trip side, and the hottest FET's mounting base leads the centroid by an amount no record bounds.
- **Mounting:** the coupon fixed to a plate section as board A is fixed to the case, in its installed orientation.
- **Thermal boundaries:** **device spacing** (Q39, Q40 and Q42 centre to centre as drafted, R17's distance from the pour);
  **copper connectivity** (the pour's connection to the VBAT and CH_BATQ planes, the via count to each inner plane, the planes' extent);
  **neighbouring sources** (U3, L2, R17 and every part within 30 mm that dissipates in service, carried on the coupon as resistive dummies at
  their declared heat and positions); **airflow** (still air, or the mixers' flow where they reach the region, as installed);
  **enclosure coupling** (the plate section and its attachment; the air at 76.25 C in a chamber, or the rise referred to it).
- **Measurement uncertainty:** the K-factor within 2 %, the heating power within 1 %, the air within 1 K, stated as an expanded uncertainty
  on Zself + 2 Zmut; a reading passes when it plus its uncertainty is under the limits of E11-29.
- **Permitted extrapolation and the comparison rule:** the steady figures transfer to the final board only when each boundary is no worse
  by this rule: the three FETs' spacing is at least the coupon's; the pour inside the region is the coupon's or a superset joined only to the
  same nets and planes with at least the via count, and joined to no additional heat source; R17 sits no closer; every neighbouring source
  within 30 mm dissipates no more and sits no closer; airflow is at least the coupon's; the attachment to the plate is the coupon's or more
  conductive. *Why this rule (INFERRED, a property of linear conduction):* the steady conduction network's conductance matrix is an
  M-matrix; adding conductance to the ambient node raises its diagonal, and an M-matrix's inverse does not increase entrywise when the matrix
  increases entrywise, so no node's steady rise grows for the same or smaller sources; conductance added between the three and another source
  is excluded because it can raise them. Convection and radiation enter linearised at the operating point.
- **Re-test when:** any boundary fails the rule; a different FET part or lot without a unit reading; the FET count or R17's place changes;
  the plate attachment, the fan or its position changes.

#### Block E11-30: the whole hot docking waveform

- **Specimen:** six BUK6Y10-30PX, one per coupon, each on a heated block.
- **Lot:** the six from one reel and date code, recorded; the result is **prototype evidence for that lot and those conditions, not a
  production limit**, and it does not extend Nexperia's limiting values (AN11158 2.4): the build's parts are taken from the tested lot, or
  the test is repeated on the build's lot.
- **Operating point (the waveform):** 267.2 A peak, time constant 37.2 us (1.1 x the docking waveform's 242.9 A and 33.8 us), 2000 pulses
  10 s apart (a lifetime allowance of 1000 docking events, twice), the whole pulse in one body diode.
- **Mounting:** each part soldered to a coupon whose mounting-base pad sits on a block held at 75 C.
- **Thermal boundaries:** the mounting base at **75 C** (over the +70 C mixed air at docking, when no current flows before the pulse);
  **device spacing** none (a single device, as the record takes the whole pulse in one FET); **copper connectivity** the pad and the block;
  **neighbouring sources**, **airflow** and **enclosure coupling** enter only through the mounting base's starting temperature, which the
  block sets: within the pulse's few hundred microseconds the heat stays inside the package (16d, Fig. 4's reading), a reading the test itself
  does not establish for longer pulses.
- **Measurement uncertainty:** the peak current within 2 % (a calibrated shunt or probe), the time constant within 5 %, the block within 2 K;
  the envelope is set so that the waveform less its uncertainty still covers 242.9 A and 33.8 us.
- **Permitted extrapolation:** none outside the tested envelope and lot: a docking event in the kit is covered only when its peak, time
  constant and starting mounting-base temperature are each at most the tested values and the count stays under 2000.
- **Comparison with the final board:** the first prototype's docking waveform is measured (peak, time constant, the FET's mounting-base
  temperature at the event) and compared value by value with the tested envelope; no equivalence is assumed from the layout.
- **Re-test when:** another lot or part; the prototype's measured peak, time constant or mounting-base temperature exceeds the tested ones;
  the pack loop or VSYS's capacitance changes; the expected count of docking events passes 2000.

#### Block E11-36: RDS(on) at BATDRV's least drive

- **Specimen and lot:** ten BUK6Y10-30PX from the build's lot (reel and date code recorded) on a Kelvin coupon.
- **Operating point:** VGS -8.5 V measured at the gate, ID -9 A in pulses short enough that the self-heating stays under 1 K (Fig. 4's
  Zth at the pulse width times the pulse's power), junction 150 C set by an oven after a soak to within 1 K.
- **Mounting and thermal boundaries:** the junction is set by the oven, so device spacing, copper connectivity, neighbouring sources,
  airflow and enclosure coupling are **not** what this row measures; they are named so that no one reads the result as an installed figure.
- **Measurement uncertainty:** the Kelvin voltage within 0.5 %, the current within 1 %, the oven within 1 K: RDS(on) within about 2 %.
- **Permitted extrapolation:** to a drive of at least 8.5 V and a junction of at most 150 C for the lot read (more drive and a cooler junction
  do not raise RDS(on) in Nexperia's typical Figures 8 and 10: INFERRED); to other lots as a limit, never.
- **Re-test when:** another lot or part; BATDRV's printed least drive falls; the junction limit rises over 150 C.

#### Block E11-37: BATDRV with the three (rebound in round 9, 19d)

- **Why rebound:** the owner's reviewer (4 October) read this block as covering the pair only, with transfer restricted to that gate
  network; the third FET changes the network, so the block is the three's. Thermal improvement does not close the gate-drive question.
- **Specimen and lot:** TI's BQ25730 evaluation hardware modified as drafted, or the controlled first prototype of board A; the BQ25730's and
  the three FETs' lots recorded.
- **Operating point:** supplement entry on a source removed under 0 to 10 A; the ideal diode's 30 mV regulation; LDO mode at VSYS_MIN with
  the precharge's 0.33616 A; at -20, 25 and 70 C ambient. The gate load is the three's Ciss, 7.08 nF typical at -15 V and about 8.61 nF
  near 0 V (1.42 and 1.72 times TI's 5 nF); BATDRV's time constants 42.48 us on (-15 V), 51.66 us on near 0 V and 18.08 us off.
- **Mounting and thermal boundaries:** the gate loop from BATDRV to the three gates (its length, the equal branches and any series element)
  and VSYS's capacitance as drafted; **current sharing**: each FET's drain current read (a shunt or a Hall probe per drain) in LDO mode and as
  an ideal diode, one gate node driving three thresholds; **thermal coupling**: each junction recorded on the shared pour; **device
  spacing**, **copper connectivity**, **neighbouring sources** (the charger's converter running as in service), **airflow** and
  **enclosure coupling** (a chamber's still air) recorded, because the gate's capacitance and the threshold move with temperature.
- **Measurement uncertainty:** probes with at least 100 MHz bandwidth and short ground loops; VSYS within 1 %; each drain current within 2 %.
- **Permitted extrapolation:** to the final board only when the gate loop, the three FETs and VSYS's capacitance are the draft's; a result
  with the pair does not transfer to the three, nor the three's to the pair.
- **Re-test when:** the gate network, the FET part, lot or count, VSYS's capacitance or the charger's settings (EN_LDO, VSYS_MIN) change.

#### Block E11-38: the dock's VSYS branch through the fault envelope

- **Specimen and lot:** the branch coupon (U42 with R228, C237, C238, C239 and D23 on their drafted copper, VSYS's local capacitance within
  20 nH, one Preci-Dip 813 in a dock block with its neighbours, 60 mm of 24 AWG, a board E stub with C31, U22's rail and the fan headers), or
  the first prototypes of boards A and E; U42's, the contacts' and the wire's lots recorded (the wire's maker is Layer 7's F-L7-08).
- **Operating points:** the cases (a) to (h) of E11-38.
- **Mounting:** the 813 in a dock block as installed, its neighbours populated; the wire routed as in the case.
- **Thermal boundaries:** **device spacing** (the 813's neighbours in the block); **copper connectivity** (U42's pad and planes, the contact
  lands); **neighbouring sources** (the dock's other contacts at their declared currents, the ground return's 2.406 A in one 813 with one
  open, during (e) and (h)); **airflow** (the dock region's still air); **enclosure coupling** (a 70 C chamber).
- **Measurement uncertainty:** current within 2 % at 50 MHz or more for (c), the 813 body's thermocouple within 1.5 K, the four-wire
  resistance within 1 %.
- **Permitted extrapolation:** U42's limits and timings as device properties of the lot; the peaks, the pin spikes and the contact's
  temperatures only where the IN-side inductance (at most 20 nH, measured), the output loop, the block and the neighbours' currents are the
  final's, compared value by value; otherwise re-read on the first prototypes.
- **Re-test when:** U42's network or lot, the dock block or contact part, the wire, VSYS's capacitance or its placement, or the
  neighbouring contacts' currents change.

#### Block E11-35: the fans' start

- **Specimen and lot:** two 9WL0612P4H001 (Layer 7's selection), date code recorded.
- **Operating point:** the PWM duty from 0 to 100 % in one step and by the firmware's ramp, at 12.0 V and at the rail's 11.512 and 12.431 V,
  at -20, 25 and 70 C ambient.
- **Mounting and thermal boundaries:** the fan on its mounting as under the plate; **device spacing** and **neighbouring sources** do not
  set a fan's start current, **airflow** and back pressure set its running current, **enclosure coupling** sets its temperature: recorded.
- **Measurement uncertainty:** current within 2 % at 10 kHz bandwidth or more for the start surge.
- **Permitted extrapolation:** the start current within the tested voltage and temperature for the lot; the installed running current only
  from the first prototype.
- **Re-test when:** another fan part or lot; a temperature outside -20 to 70 C; the rail's window or the PWM ramp changes.

### 17e. The Layer 6 author's findings on this record's board A draft (L6P-F01, L6P-F05; 3 October 2026)

**L6P-F01, a designator collision.** L4-E8's `apply_gen_sch_a_bank.py` adds R221 to R226 (the front end's six can ballasts) and this
record's `apply_gen_sch_a_charger.py` added R221 as U42's ILIM resistor, so whichever applied second would refuse. Every board A draft
under `records/l4e4` to `l4e11` was applied to a copy of `gen_sch_a.py` (the bank draft after L4-E6's `apply_gen_sch_a_r12.py`, its
stated order) and the designators each adds were read from the text it writes: L4-E8's bank R221 to R226; L4-E9's `apply_gen_sch_a_u17.py`
R227; this record's charger draft Q39, Q40, C236 to C239, D23, U42 and the ILIM resistor; the other drafts add none. **U42's ILIM
resistor is renamed R228**, the next free resistor designator on board A (SESSION); C236 to C239, D23 and U42 collide with nothing. The
pairwise check over all board A drafts is a test (`t_the_board_a_drafts_add_disjoint_designators`), so a later draft that takes one of
these fails it rather than refusing at application.

**Board E, the same class of defect (Astra's recheck of set 27, blocking discrepancy 1; the coordinator's set 27 run).** Every board E
draft the integration carries is composed on a copy of `gen_sch_e.py` in L4-E9's change-list order (d8dec31's `apply_gen_sch_e_cin.py`,
q1, u5_grade, hold, input_limit, backstop, f1, hotswap, entry, solar_guard, aux; the timer only as the LM5069 alternative) and the
designators each adds are read from the text it writes, both as new names and as duplicate part calls. With L4-E7's round 2 port bank
(its solar guard adds C126 to C136 since `68bc3bad`), the fan rail's capacitors C135 and C136 collided with it: **U22's capacitors are now
C142 to C148** (in 10 uF, out 22 uF, PVCC 4.7 uF, the two bootstraps, VC 820 pF, feed-forward 33 pF; SESSION), U22, L4 and R103 to R109
unchanged; this record's drafts now collide with no other board E draft. **A finding for the coordinator, not this record's files:** in that
order d8dec31's cin draft takes the next free capacitor, C65, before L4-E7's input-limit draft writes its own `c("C65", ...)`, so the
composed generator carries C65 twice; one of the two owners renumbers, or the change list moves R-16 after R-20.

**L6P-F05, a procurement fact.** The BQ25730RSNR read LCSC stock 0 on 2 October 2026, and five are needed for the five boards. It goes to
the owner's procurement list as a fact (E11-32 names the next sources to read); it is not a reselection, and nothing is bought here.

## 18. The fans' feed after Layer 7's selection (F-L7-01, F-L7-02, F-L7-04; the B1 topology kept; out 18)

**The facts, cited from Layer 7's record** (`v2/docs/records/l7pwr/L7-FANS-AND-TH1.md` at `2087060b`, sections 2d, 2e, 2f and 5; not in
this tree): D-18 settled on **Sanyo Denki 9WL0612P4H001** (the two mixers, board E's J_FAN1 and J_FAN2) and **9WPA0412P6G001** (the three
cooler fans, board B), both 12 V with a printed operating range of **10.8 to 13.2 V**, 0.17 A each at 12 V, four wires (12 V, GND, pulse
sensor, PWM), IP68, -20 to +70 C; no fan of any maker read prints a range covering VSYS_E's 9.494 to 17.375 V, and no 5 V IP68 40 mm fan
exists in the lines read. **Section 15a's two mixers directly on VSYS_E are withdrawn**, and the five fans at full speed would have drawn
1.277 A (Layer 7, at an efficiency of 0.90) on the branch this record declared at 1.0 A.

### 18a. The mixers' regulated 12.0 V rail on board E

A buck cannot hold 12.0 V from the 9.688 V supplement floor and a boost cannot from 17.375 V: the rail is a buck-boost from VSYS_E. Three
candidates on their makers' printed data (all three sheets fetched from the makers and filed held; prices NOT READ, LCSC's search refused
this host):

| | Input | Current limit | Package, thermal | What else it needs | Reads |
|---|---|---|---|---|---|
| (V1) ADI LTC3115-1 (Rev. E) | 2.7 to 40 V | inductor 2.4 / 3.0 / 3.7 A | FE TSSOP-20 EP, thetaJA 38 C/W; E grade -40 to 125 C | TA04's 12 V 1 MHz network: one 10 uH inductor, 10 uF in, 22 uF out, FB 1M / 90.9k, VC 40.2k and 820 pF, feed-forward 10k and 33 pF, RT 35.7k; internal 9 ms soft start | TA04b about 93 % at 0.34 A for 10.6 and 12 V in (typical); about 1.2 A of load at 12 V out near 9.5 V in (G12, 22 uH 500 kHz, typical) |
| (V2) TI TPS55340 (SLVSBD4E) as a SEPIC | 2.9 to 32 V | switch 5.25 to 7.75 A | RthJA 43.3 C/W | a coupled inductor and a coupling capacitor | efficiency printed for a boost only; the SEPIC's NOT PRINTED |
| (V3) TI TPS63070 (SLVSC58B) | 2 to 16 V | input 3.05 to 4.15 A | thetaJA 63 C/W | | **fails** VSYS_E's 17.375 V |

**SELECTED (SESSION): (V1)**, U22 LTC3115EFE-1 as ADI's TA04, with L4 Coilcraft XAL6060-103ME (10 uH, DCR 29.82 mOhm, Isat 5.0 A over the
3.7 A limit, Irms 7.0 A; Coilcraft 887-1, held), PWM/SYNC to VCC (fixed 1 MHz). *Why:* the only one of the three whose printed input range
covers VSYS_E and whose current limit is of the fans' order; one inductor and the maker's own 12 V network. The output is **12.001 V
(11.512 to 12.431 V at FB's limits with the drafted 1 % divider)**, inside the fans' 10.8 to 13.2 V by 0.71 V below and 0.77 V above. *Reverse:* a fan whose maker prints a range covering VSYS_E.

**Its RUN divider** (R103 1.5M / R104 255k): enabled at **8.33 V** (7.98 to 8.67 V at the comparator's limits), disabled at **6.89 V** (6.55 to
7.23 V), so under the floor and over U12's 3.8 V start. This is what breaks the interaction 17a could not: a fan fault that drives U22 to its
2.4 A limit against U42's limit lets VSYS_E fall only to U22's disable, where U22 stops and VSYS_E recovers; the controller stays up and
the fault appears as a rail hiccup, not a controller reset (INFERRED; the same model reproduces TA04's own 10.6 / 8.7 V within 0.15 V).

**Heat into the case** (MODELED; the efficiency 0.85 is an ASSUMPTION, read 5 points under TA04b's typical curves): **0.72 W** at full
speed (4.08 W of fans), 0.254 W at the plan's 1.44 W; TJ 97.4 C at +70 C air on thetaJA 38. **Its protection:** U22's own current limit and
soft start, behind U42, the branch's limiter; no fuse of its own.

**The draft** (`apply_gen_sch_e_aux.py`, rewritten; the generator's own text is unchanged where the edits do not reach): U22 and its network
(C142 to C148, R103 to R109, L4) on the FE and XAL6060 lands; J_FAN1 and J_FAN2 four pins (12 V, GND, PWM, TACH); Q9 and Q10 kept as open-drain
drivers of the fans' PWM inputs (the fan's PWM level NOT READ, Layer 7); D7 and D8 and the FANn_SW nodes removed (the old node loop is
emptied, its text left for board E's owner to delete); +12V_FAN declared (source L4, 0.34 A, converted at 0.85). The land key HTSSOP20EP
is the 4.4 x 6.5 mm 0.65 mm pitch exposed-pad land board A's draft uses for TI's PWP; the parts stream checks it against ADI's FE20 drawing.

### 18b. The branch's declared current and U42's setting, re-derived

At the floor with both fans at full speed U22's input is **0.5208 A** (4.08 W over 0.85 at 9.508 V, plus 16 mA of PWM-mode quiescent
current), and with U12's 0.8 A the branch is **1.3208 A, declared on IF-AE-DOCK pin 1** (was 1.0 A; Layer 7's 1.277 A at 0.90); at the
plan's duty 0.9942 A. Against **U42's least limit 1.4713 A: 89.8 %, 0.1504 A in hand: not exceeded, so R228 stays 11.0 kOhm** (I(OL)
1.4713 to 1.8018 A). The contact at 37.7 % of 3.5 A, 8.54 K by w3de's rise; the sustained-overload figures of 16e and the retry duty of
17a are unchanged. **The drop** at the floor with 1.3208 A is 0.1795 V, VSYS_E 9.508 V; at U42's least limit 9.494 V; U22 holds 12.0 V from
2.7 V up, so VSYS_E's floor no longer reaches the fans.

**The fans' start** (NOT READ, Layer 7): with one fan running and U12 on, U42's 0.1504 A of room leaves 1.21 W at the rail for the other
fan's start, 1.6 times its running power, before U42 limits; U22 itself delivers about 1.2 A at the floor. The fan, not the rail, is the
unknown (E11-35, E11-38 f).

### 18c. The stagger (E11-39) restated

U22's 9 ms soft start covers the rail's own rise only; a fan's start surge comes when its PWM duty rises. **The stagger stays**: one fan
at a time, each by a PWM-duty ramp into the fan's PWM input (Layer 7's F-L7-05), never while U12 or U22 starts.

### 18d. Board B's cooler fans: a finding, not a draft

Board B's generator (`gen_sch_b.py`, read): J_FAN1 to J_FAN3 carry the slot rail +5V_Sn at **5.1 V** on pin 1 and declare the fan at 0.1 A on
it; no +12V net is declared on the board. **The feed does not cover the coolers' 10.8 to 13.2 V and needs the same regulated 12.0 V**:
**E11-40**, a finding for board B's owner with the rows (Layer 7's F-L7-02): a per-slot step-up from +5V_Sn (Layer 7's 0.436 A each at
full speed, keeping an empty slot off) or a 12 V feed from board A over the bay harness; the header's pin 1 becomes 12 V, the slot
budget's fan row 2.0 W at 12 V, the module's Fan_PWM and Fan_Tacho kept.

**Status, section 18:** the mixers' feed SELECTED and DRAFTED (U22, applied with E11-33); the declared current 1.3208 A and U42's setting
kept; board B OPEN as E11-40; the fans' start current and PWM level stay Layer 7's and E11-35's.


## 19. Round 9: record l9stk's protection and record l8p's breaker (4 October 2026; out 19)

**The task.** Record l9stk's section 15 (branch `fnd/l9stk` at `2c8b29fb`, independently checked CONFIRMED AS CONDITIONAL) selected a
third battery FET and handed this record E11-29 as a junction limit, the three-FET Ciss condition C3, the shore input's DD-3 and the
interface demand IF-1; record l8p (branch `fnd/l8p` at `b1295c1e`) drew the breaker and found two run-time refusals in this record's
drafts (L8P-F02, L8P-F03); the owner's reviewer (4 October, "Two precise checks") asked E11-37 to be rebound to the three-device network.
Both records are read from their commits by sha256 (`l4e11_power.py`, out 19); nothing of theirs is edited. Every circuit change is a
release-guarded draft; nothing is built, bought or measured.

### 19a. L8P-F02 and L8P-F03, corrected

| Finding | The defect | The correction (drafted) |
|---|---|---|
| L8P-F02 | `apply_gen_sch_a_charger.py` declared VSYS_DOCK with U42 as its source and no `source_ic`, ahead of VBAT, the rail it is fed from; `intent.rail` refuses both | VSYS_DOCK declared after VBAT's declaration, with `source_ic` (U42's OUT pins 18 to 20 are the internal FET's source, the branch's whole current) |
| L8P-F03 | `apply_gen_sch_e_aux.py` named L4 as +12V_FAN's source; L4 sits between U22's SW1 and SW2 | +12V_FAN names U22 with `source_ic` (the LTC3115-1's VOUT pins carry the rail; its switches are inside the IC) |

**The composition proof (scratch copies, record l8p's `gen_netlist.py` stand-in layout):** board A composed in L4-E9's order (L4-E6's
R12, this record's guard and charger, L4-E4's R11, L4-E8's bank, L4-E4's R138, L4-E9's U17, l8gnd's two, l8r2's two, d8dec31's mainpb,
l6r2's codes) **runs to its end with `intent.write`, 713 parts** (714 with record l8p's PTC draft before mainpb); mainpb still takes
R248 and C247. Board E in L4-E9's order runs to its end (295 parts) with record l8p's scratch stand-in for L8P-F01, which is L4-E7's.
L4-E9's own composition tests pass with its pins of this record's three changed drafts re-pinned in memory only (the integrator re-pins).

### 19b. B-P2: the third battery FET, Q42

**The limit** (record l9stk 15.5): the hottest battery FET's junction at most 150 C held at the breaker's largest limit, 23.93 A, from
L4-E12's 76.25 C, with the band carrying the current (9.16 K) and R17 dissipating its 2.86 W in place. The budget for the FETs and R17's
coupling is 64.59 K; R17's coupling into a junction is at most 1 K/W when it is designed apart.

| FETs | Loss each at 23.93 A | FETs only | R17 apart | R17 anywhere |
|---|---|---|---|---|
| the pair, (Zself + Zmut) | 3.027 W | 21.34 K/W | **20.39 K/W** | 10.96 K/W |
| three, (Zself + 2 Zmut) | 1.345 W | 48.01 K/W | **45.88 K/W** | 15.34 K/W |

The script reproduces record l9stk's figures on this record's 21.136 mOhm allowance within 0.1 % (its printed inputs are rounded) and takes
the printed ones. The three's allowance is 1.386 times the pair's former 33.12 K/W target, the pair's 0.616 times it. At the allowances the
junction reads 89.4 C at 10 A, 118.0 C in the 18 A service and 150.0 C held at 23.93 A (RECORD).

**DRAFTED (SESSION), in `apply_gen_sch_a_charger.py`:** **Q42**, a third BUK6Y10-30PX (C3278350) on the LFPAK56 land, gate CH_BATDRV,
drain CH_BATQ, source VBAT; CH_BATQ's loads now Q39, Q40 and Q42. **Q41 is record l8r2's VIN_RAW cut-off FET; Q42 is free** in
`gen_sch_a.py`, its committed netlist and every board A draft (main's, record l8p's and record l8r2's later rounds).

**The layout requirement** (Layer 9 and board A's PCB generator): the three side by side on one CH_BATQ drain pour and one VBAT source pour,
the gates from one CH_BATDRV node by equal branches; R17 off that pour; **record l8p's RT1 (the PTC of the enable loop) at the three drain
tabs' centroid, within 3 mm of each tab's edge**, so it reads the hottest tab's copper (l9stk's thermal guard; L8P-10 places it).
**The fallback:** the pair at 20.39 K/W with R17 apart, if E11-37 refuses three.

### 19c. E11-29 restated as the junction limit

E11-29 is now record l9stk's E-1: **the installed three, each FET's (Zself + 2 Zmut) at most 45.88 K/W steady with R17 placed apart, R17's
coupling into each junction at most 1 K/W (heat R17 alone), so the hottest junction stays at most 150 C held at 23.93 A from 76.25 C** with
the band and R17 in place. The pair's former 33.12 K/W target at +70 C air and its 1 s, 20 ms and 244 us targets are **withdrawn**: with
record l8p's breaker no current over 23.93 A outlasts its clearing, and the held limit governs; without the breaker, record l9stk's DD-1
stays open. The block in 17d is restated to the three, the band and R17 (CONDITIONAL on E11-29). Round 11 (21d) restates the bar at 40.78 K/W for any split.

### 19d. E11-37 rebound to the three-device network

The owner's reviewer read E11-37 as covering the pair only, with transfer restricted to that gate network. It is rebound to the three:

| Item | The pair | The three |
|---|---|---|
| Ciss at -15 V (typical, no maximum printed) | 4.72 nF | **7.08 nF**, 1.42 times TI's 5 nF (SLUSE65A p.92) |
| Ciss near 0 V (Fig. 12, typical) | about 5.74 nF | **about 8.61 nF**, 1.72 times |
| BATDRV on (6 kOhm at most), -15 V / near 0 V | 28.32 / 34.44 us | 42.48 / 51.66 us |
| BATDRV off (2.1 kOhm at most), near 0 V | 12.05 us | 18.08 us |

The bench now reads, besides the gate: **current sharing** (one gate node driving three thresholds, each drain's current in LDO mode and as
an ideal diode) and **thermal coupling** (each junction on the shared pour). A result with the pair does not transfer to the three.
**Q-TI-17** is extended to three devices (`clarification/TI-QUESTIONS.md`, drafted, not sent). **Thermal improvement alone cannot close
the gate-drive question: E11-37 stays OPEN**, condition: Q-TI-17's answer or E11-37's bench with the three; production conformance needs
one of them (record l9stk's C3).

### 19e. DD-3: the shore input, by the owner's current-and-time criterion

**The defect as stated** (record l9stk 14.6 and 15.7): R19 at 4.0 W at 20 A, over its 3 W from 17.32 A, and J_DCIN's JST VH at 10 A,
inside F1's 600 s interval (Q7 shorted, the hot swap's limit lost). l9stk read the drawn 10 mOhm R19; R-123 (`apply_gen_sch_e_entry.py`)
already makes R19 a 4.5 mOhm part. **The criterion** (the owner's): every series part within its limits across the credible overload
range, with the trip's tolerance, the delays at their printed limits, the initial temperature (L4-E12's 76.25 C plus each part's own heating), the
retry's heating, the protector's own SOA and the currents held just under the trip.

**The one design-out attempt (SESSION):**
1. **J_DCIN DRAFTED** as the Amass XT60-F (C98734, `apply_gen_sch_e_entry.py`), D-06's selection: 30 A rated, 60 A instantaneous, -20 to
   120 C (Amass V1.2), the gender opposite J_BATT's XT60-M; nets unchanged, pad 1 the + contact read on KiCad's land at regeneration.
2. **R19** as R-123 draws it, the HoLLR2512 4.5 mOhm 3 W (C2985708), judged on its maker's sheet (Shenzhen Milliohm, Ho-A0, held back:
   `fetch_held_back.py --only hollr2512`): 3 W to 70 C ambient, derated linearly to 170 C; a 5 s short-time overload at twice the rated
   power. Hot 4.578 mOhm (+1 %, 50 ppm/K to 170 C); at its local 86.25 C (the air plus the band's 10 K, ASSUMPTION) 2.513 W.
3. **The coordination:** a second pass FET in series with Q7 on its gate (the same CSD19536KTT, the same orientation), so one welded FET
   leaves the other to open and every series part sees the breaker's envelope, not F1's, after a single fault.

| Part | Case | Reading | Against |
|---|---|---|---|
| R19 | the breaker's highest, held (Q7 working), 7.136 A | 0.233 W | 0.093 of the derated 2.513 W |
| R19 | F1's 135 % held, 13.5 A | 0.834 W | 0.332 |
| R19 | F1's 600 s interval top, 20 A | 1.831 W | 0.729 |
| R19 | 35 A for 5 s | 5.608 W | 0.935 of the 5 s overload's energy, a room-temperature test: from 86.25 C CONDITIONAL on E11-16 |
| R19 | 60 A for 0.5 s | 16.481 W | 0.275 of that energy (INFERRED); over 60 A, F1's clearing I2t (E11-16) |
| J_DCIN (XT60-F) | 7.136 / 13.5 / 20 A | 0.238 / 0.45 / 0.667 of 30 A | 35 and 60 A within the 60 A instantaneous figure, its duration unstated (E11-16) |
| Q7 | 7.136 A held | 0.22 W | within |
| Q1 (BSC039N06NS) | 7.136 A held; F1's 20 A | 0.358 W; 2.81 W | 20 A unbounded (no installed path held): the coordination keeps it at the breaker's figure |
| **L2 (SRF1260-1R0Y)** | **7.136 A held from 76.25 C** | **112.37 C** | **OVER its 105 C** (40 K at 7.51 A Irms, the rise included) |
| F1's holder (Keystone 3568) | | no current rating printed | record l9stk's DD-4 (Layer 6 and 7) |

L2 carries at most **6.367 A** held from the 76.25 C air: between the breaker's least threshold (6.364 A) and its highest (7.136 A), so a
unit at its highest threshold holding a current just under its trip overheats L2 **with Q7 working**. In service at a 9.00 V plug (5.983
A) it reads 101.64 C, within; section 3e's 98.2 C was at the 62.1 C air. A part rated at least 8.42 A at a 40 K rise is needed.

**The coordination's cost** (INFERRED, for the drafting with L2): 4.32 mOhm hot in the loop; at a 9.00 V plug 6.004 A (was 5.983 A), VIN_RAW
8.119 V, 6.0 % under the lowest trip; the efficiency floor 0.8832 (was 0.8802); the gate load 25.5 nF for the two, under the 47 nF TI's
short-circuit row is printed at.

**RESULT: the attempt FAILS on L2** (and F1's holder stays DD-4). **DD-3 stays OPEN**, owner L4-E11 with board E's generator owner;
condition **E11-41**: L2's winding at most 105 C held at 7.136 A from 76.25 C on board E's land, or Bourns's statement, or a choke whose rating covers
it with the input filter's attenuation shown again. The second pass FET is drafted with that choke in one board E change (one
recomputation of section 3's loop, not two); **J_DCIN's XT60-F is drafted now**, independent of it; R19's continuous rows hold on its
maker's sheet and its short-time rows rest on E11-16.

### 19f. IF-1: board A's loads on VSYS held through the pack breaker's start

**The start** (record l9stk): a dv/dt start, 22 nF +-10 % into 593 uF, gate 10 to 22 uA: 0.413 to 1.111 V/ms, 0.659 A at most, **40.7 ms
at most** to 16.8 V, beginning 0.110 to 0.907 s after the enable mates (record l9stk at `0d72880b`, its hold now bypassing C_U on
undocking); the power limit's least 24.71 W. **IF-1 is critical to the service under the -1:** a start that meets the power limit latches
the breaker and the kit stays dark until a redock or an input; the start leaves room for at most 0.81 A of load at full VDS (RECORD).

**What IF-1 names, read on the drafts as they stood** (INFERRED): every board A converter on VBAT is enabled by RAIL_EN or behind it, and
U1 (LTC2954-1) holds RAIL_EN low from power-up until MAIN has been held 26 ms at least (2954fb: "When power is first applied to the
LTC2954, the part initializes the output pins"). But **U42's branch to board E is always on**: from its IN's 4.5 V floor it feeds board E's
U12 and U22 through the start, when the breaker FET drops 12.3 V; with the inrush and U42's 1.802 A that is 30.3 W, over the power limit's
least 24.71 W, so the timer runs and the -1 latches. And MAIN held through a docking asserts RAIL_EN 31.4 ms after the ramp begins at
the slowest slope, with 3.81 V still across the breaker FET.

**THE HOLD (SESSION), drafted in `apply_gen_sch_a_charger.py`:** **U46**, the TPS37A010122DSKR U34 already is (C3685740, SNVSBJ1E), on
VBAT (VDD 2.7 to 65 V):

| Element | Value | Effect |
|---|---|---|
| Channel 2 (UV), SENSE2 on SYS_UVS | R86 91k over R87 10k, 1 % (U34's pair) | VBAT falling 7.856 / 8.08 / 8.309 V, rising 8.014 / 8.242 / 8.476 V |
| CTR2 | C105 100 nF (C14663; +-10 %, X7R +-15 %, ASSUMPTION) | release **78.6** / 127.3 / 201.2 ms after VBAT passes the rising threshold; a fall re-asserts within 17 us |
| RESET2 on EF_UVLO | U42's UVLO pin (moved off VBAT), R88 100k over R89 22k | U42 held off (under 0.3 V against its 1.09 V falling threshold, off within 16 us); released, U42's own UVLO at 6.90 V on at most and 5.95 V off at least, under U46's |
| Channel 1 (OV), SENSE1 on EF_UVLO | RESET1 on SYS_HOLD_G, R105 100k from VBAT, D24 BZT52C12 | held (0.3 V) is under SENSE1's 0.776 V falling threshold, so RESET1 is released and SYS_HOLD_G rises (clamped under 12.7 V) |
| Q43 (2N7002) | drain on RAIL_EN | RAIL_EN held low whatever U1 asserts; RAIL_EN can reach the TPS62933's 1.1 V only from VBAT 3.921 V, where Q43's gate is 1.42 V over its 2.5 V threshold maximum; under U46's 2.7 V, RAIL_EN is at most 0.758 V |
| C238 | U42's IN capacitor, 1 uF | U46's VDD bypass (a class D entry; U46 beside U42) |

**The result** (INFERRED): the start ends at most 40.7 ms after VBAT begins to rise; the hold releases at least 78.6 ms after VBAT passes
its rising threshold, **37.9 ms later at the least**: no board A load on VSYS draws through the start. A quick undocking and redocking with
VBAT held up by board A's capacitance: J_DOCK's pin 1, a full-length position, mates before the enable's positions 3 and 5, which record l8p
sets 1 mm short (record l9stk's C1), so board E's load drains VSYS's 489 uF first. More than 37.7 mA takes VBAT under 8.309 V before the
breaker can start (0.110 s after the enable mates at the least), U46 asserts and the start is held; a smaller load leaves the hold
released, and the guarantee below bounds that start.

**PGD is not used (SESSION):** it needs an eighth J_SMB position and a dock contact through two connectors from board P (record l8p's
J_SMB carries seven); a supervisor on board A acts on what board A's loads see, for every start (a docking, the gauge's FET, a retry, a
source-only rise), with no new interface.

**The residuals** (INFERRED, each with its row):
- **MAIN held through a docking:** U1 asserts first and RAIL_EN follows the hold; the panel controller keeps at least **207.7 ms** of U1's
  400 ms KILL blanking to raise KILL; if it needs more, U1 releases EN and a second press starts the kit (E11-42 c).
- **A source present:** VSYS at 12.054 V at least keeps U46 released and the loads on; the breaker carries only what the charger does not,
  at 4.746 V across its FET at most: under 4.55 A of excess its power limit never acts; over it the -1 latches (record l9stk 15.4b) while
  the source carries the kit, and 19h's inhibit keeps the charge off the latched FET (E11-42 d).
- **A VBAT under 8.309 V in service** holds every RAIL_EN converter and the dock branch (was each converter's own UVLO, about 4.3 V for
  U12); VBAT is at least the pack's 10.6 V less the path's drop or VSYS_MIN's 12.054 V in every mode, so only a collapse reaches it.
- **Record l9stk's IF-5:** once record l8p's drafts are applied the docking pulse E11-30 qualifies no longer arises; E11-30 is kept until
  then.

**The guarantee under the -1** (the coordinator's note and record l9stk's IF-1, CRITICAL TO THE SERVICE: a start that meets the power
limit latches the breaker and the kit stays dark until a redock or an input; the start leaves room for at most **0.81 A** of load at full
VDS; INFERRED). **What board A still draws from VBAT while U46 holds** (RAIL_EN low, +3V3 down, so the expanders and U43 are unpowered and
every enable sits on its pull-down: R30, R34, R38, R111 to R114, DEV_EN's pull-up to the dead +3V3; NETLIST), at the pack's 16.8 V, each
part at its sheet's largest printed figure:

| Draw | mA | Class |
|---|---|---|
| U3 BQ25730, battery only, performance mode (SLUSE65A's largest row) | 1.2700 | MAKER |
| U42 TPS16630 held by UVLO (IQ(ON) as the bound; no row with UVLO low) | 1.7000 | MAKER |
| U1 LTC2954; U46 TPS37A | 0.0120; 0.0026 | MAKER |
| five LM5176 (U5, U7, U13, U15, U19), two AP64500 (U4, U6), two TPS62933 (U12, U41, typical only), two TPS259631 (U21, U22), in shutdown | 0.0500; 0.0060; 0.0040; 0.0023 | MAKER |
| R2 (RAIL_EN held by Q43); R86 and R87; R88 (EF_UVLO held); R105 into D24; R82 and R83 (the inhibit) | 0.1682; 0.1665; 0.1682; 0.0542; 0.0561 | NETLIST, SESSION |
| R92 and R96 (U21's and U22's OVLO dividers, their 143k tops as the bound); R107 and R108 on CELL+ | 0.2352; 0.0841 | NETLIST, SESSION |
| **in all** | **3.98 mA, 0.49 % of the 0.81 A room** | |

Board E's VSYS_E is off behind U42. So:

| Start | Board A's load on the breaker during it | Bound |
|---|---|---|
| from a VBAT under 7.856 V: a docking, a redocking after the kit went dark, 19h's input-return restart, the thermal guard's cycle | the static 3.98 mA only: U46 releases at least 37.9 ms after the start ends | the inrush alone, 11.1 W against the 24.71 W least power limit |
| with VBAT held over 7.856 V by board A's capacitance (a quick redocking; the whole load under 37.7 mA to hold VBAT up for 0.110 s) | the running load, released | VDS at most 8.944 V: up to 2.10 A of load before the power limit acts (U42's 1.802 A alone: 22 W); a step past that within the 40.7 ms latches the -1 and the kit goes dark until a redock or an input: a residual |
| with a source carrying VSYS (at least 12.054 V) | what the charger does not carry | under 4.55 A of excess the power limit never acts; beyond, the pack latches while the source keeps the kit up (not dark) |

E11-42 (e) reads the static draw on the bench (at most 40 mA, ten times the desk's sum).

**New designators (board A):** Q42, U46, R86 to R89, R105, C105, D24, Q43; U44 and U45 are record l8r2's, so the supervisor is U46. R86
to R89, R105 and C105 sit below every draft's reference, so d8dec31's next-free reference stays R248 and C247 in the full composition.

### 19g. Status of round 9

| Item | Status |
|---|---|
| L8P-F02 | **corrected in the draft**; board A composes and runs to its end |
| L8P-F03 | **corrected in the draft**; board E runs to its end (with L8P-F01's stand-in, L4-E7's) |
| B-P2, the third FET | **Q42 drafted**, its land LFPAK56, RT1 at the three's centroid (a layout requirement) |
| E11-29's restatement | **restated** as the junction limit, 45.88 K/W with R17 apart (pair's fallback 20.39 K/W); CONDITIONAL on its specimen |
| E11-37's rebinding | **rebound** to the three-device network; **OPEN** on Q-TI-17 (extended) or the bench with three |
| DD-3 | **OPEN** after one design-out attempt (fails on L2, 112.37 C at 7.136 A from 76.25 C), owner L4-E11 with board E's generator owner, condition E11-41; J_DCIN's XT60-F drafted |
| IF-1 (critical to the service under the -1) | **drafted**: the VSYS hold U46 on U42's UVLO and RAIL_EN; PGD not used; the guarantee under the -1 stated case by case, board A's static draw 3.98 mA against the 0.81 A room; bench E11-42 |
| DD-7 (l9stk 15.4b, the -1) | **drafted** in `apply_gen_sch_a_dd7.py`: the input-return reset (Q44 to Q46) for the first restart and the hardware charge inhibit (Q47 to Q49) for every latch that takes CELL+ dead; E-14 extended; CONDITIONAL on E11-45 and TI's answer on BATDRV held at VSYS; IF-7 the firmware owner's (E11-44); **B-R2 OPEN** for a latch with a source present into a resistive fault (route R1, board P's generator with record l9stk; R2 this record's fallback) |

**For the integrator** (nothing of theirs edited here): L4-E9's pins of `apply_gen_sch_a_charger.py`, `apply_gen_sch_e_aux.py`,
`apply_gen_sch_e_entry.py`, this record's output, page and TI questions, and its register rows R-157 to R-181 and E11-29's (R-159)
texts; L4-E9's change list gains `apply_gen_sch_a_dd7.py` (19h) after record l8p's PTC draft and before d8dec31's mainpb, with rows for
E11-41 to E11-45 (its script refuses an apply script it does not list; L4-E9's composition tests pass with that row and the re-pins
emulated in memory); record l8gnd's output (it prints the charger draft's sha and its designators, so `test_l8gnd`'s output check reads
it stale until regenerated); record l9stk's readings of this record's output (the phrases it reads are kept); record l8p's
`check_contracts.py` role table (unchanged by this round); board E's `check_pcb_e.py` height for J_DCIN (the XT60-F stands taller than
the VH) and its placement (the PCB generator's); Layer 5's IF-AE-DOCK row is unchanged, the IF for the DC inlet (`pcb_interfaces.yaml`,
J_DCIN's part text) owes the XT60-F (R-131).

### 19h. DD-7: the latch-off breaker, the input-return reset and the hardware charge inhibit

**Superseded in its board A sensing by round 10 (section 20):** the loop's sense (Q47 on half of DOCK_EN_OUT) and the dead point
(Q48 on half of CELL+) below are round 9's; record l8p's L8P-F04 and L8P-F05 found them failing, and section 20 redraws them. The
input-return reset and Q49 stand.

**The change** (record l9stk 15.4b, read at `0d72880b`, the coordinator's addition): the automatic-retry LM5069-2 fails its own breaker FET under
a persistent fault (0.79 of the derated SOA in a hard short; over 150 C in a resistive fault on VSYS), so board P's breaker is now the
**latch-off LM5069-1**. After a trip it stays off until its UVLO or its VIN cycles; on battery the kit goes dark. **DD-7** (owners board
A's generator with this record): when an input returns, the charger could push charge current through the latched breaker's body
diodes. **The checker's B-R2** on that recheck: the pulse covers only the first restart; if the fault persists the -1 latches again with
the input still present, no second pulse comes, and only the firmware stands between a commanded charge and the FET's body diode (4 A at
1 V is 4 W, 276 C settled). The owner's criterion asks firmware independence. Record l9stk's `0d72880b` adds **C-1c**, a restart inhibit
on the breaker pad (an NTC bridge gated by PGD, blocking restarts from 83.2 C), which widens the RC hold to 0.110 to 0.907 s and DD-7's
restart to 0.948 s from the loop's closing, later while a hot pad cools (its time NOT HELD, its E-15).

**The input-return reset (SESSION, drafted in `apply_gen_sch_a_dd7.py`, after record l8p's PTC draft):**

| Part | Value | What it does |
|---|---|---|
| Q44 (2N7002) | drain on DOCK_EN_RET | pulls the enable loop's return low: the loop opens as an undocking does, board P's second inverter pulls UVLO at once (on in 16 us; C_U drains in 1.10 ms behind it), the -1's latch resets |
| R106, D25 | 1M from VIN_RAW; BZT52C12 (11.4 to 12.7 V) | Q44's gate DD7_G follows an input on the dock, clamped |
| Q45 (2N7002) | gate FE_RUN | ends the pulse when U34 releases the front end: **78.6 / 127.3 / 201.2 ms** after VIN_RAW passes U34's UV threshold (6.889 to 7.282 V rising with this record's R14); C212 is C105's part and value on the same TPS37A010122 |
| Q46 (2N7002) | gate DD7_ALIVE, CELL+ over R107 / R108 (100k each) | holds the gate low while CELL+ is over 5.05 V (cannot conduct under 1.98 V): an input arriving on a live pack opens nothing |

The pulse is at least 78.6 ms, 71 times C_U's 1.10 ms drain; the -1's timer falls under its 0.3 V re-enable within 34.0 ms, inside the
pulse and the hold with 154.6 ms to spare. From VIN_RAW passing U34's threshold to the restart's end: **at most 1.149 s** (the pulse
201.2 ms, the hold 0.907 s, the start 40.7 ms); from the loop's closing, record l9stk's 0.948 s; longer while C-1c holds a hot pad, the
hardware inhibit below holding the charge meanwhile. **The UVLO edge** (record l9stk): read at the falling edge, an input arriving within
34.0 ms of a latch does not restart the breaker; that fails safe (the breaker stays off, the inhibit holds the charge), and the input's
next return or a redocking restarts it.

**The hardware charge inhibit (SESSION, the same draft), for the later latches:**

| Part | Value | What it does |
|---|---|---|
| R109, R144 | 1M each, DOCK_EN_OUT to SYS_INH_G to ground | **the signal**: the loop powered, i.e. the pack's cells reach board P's breaker (BRK_VIN alive); docked, DOCK_EN_OUT is at least 7.735 V (the pack's 10.6 V, RT1 at its cold least 5 kOhm, l8p's 10k and 22k), so SYS_INH_G at least 3.829 V |
| Q47 (2N7002) | gate SYS_INH_G | on while the loop is powered |
| Q48 (2N7002) | gate DD7_ALIVE | **the threshold**: releases the inhibit once CELL+ (the pack's terminal) is over 5.05 V; under 1.98 V it cannot conduct |
| R82, R83 | 100k from VBAT, 200k to Q47's drain | Q49's VGS -VBAT/3: -4.07 V at VSYS_MIN's 12.054 V (its threshold -1.3 V at most), -9.86 V at the 29.2 V clamp (12 V absolute) |
| Q49 (AO3401A, C15127) | source VBAT, drain CH_BATDRV | **where it acts**: holds the battery FETs' gates at VBAT, so Q39, Q40 and Q42 are off and their body diodes point from the pack to VSYS; no charge leaves VSYS for the pack while the source keeps carrying the kit |

The inhibit acts exactly while the loop is powered and the terminal is dead: the breaker off (latched, in its hold or starting) with the
cells present. **No firmware.** BATDRV meanwhile sinks at most 3.83 mA (its 11.5 V over its 3 kOhm least RBATDRV_ON, SLUSE65A): an
addendum to Q-TI-17 asks TI whether holding BATDRV at VSYS is acceptable. **Not inhibited, by design:** with the loop unpowered (the gauge's
FETs off, the pack absent, undocked) a pack's wake and precharge pass the breaker's body diodes at the gauge's own current (record l9stk's
charge direction), and source-only operation (U-04) is untouched.

**The loop's load** (an interface effect for records l9stk and l8p): the 2 MOhm sense at DOCK_EN_OUT moves the first inverter's gate at
l9stk's bound point (10.6 V, RT1 at 47 kOhm) from 2.952 V to 2.939 V against its 2.5 V threshold.

**E-14, extended to a second latch with the input present.** With the inhibit, the charge into a latched breaker is the battery FETs' off
leakage (IDSS 1 uA at 25 C each; the hot value not printed). Without it, at the breaker FET's VSD 1 V and IF-2's 52.5 C/W, held:

| Charge current | Body diode | TJ from 76.25 C |
|---|---|---|
| the charger's ChargeCurrent at POR (TI's E2E answer, D4), 0.256 A | 0.256 W | 89.7 C |
| R-b's largest actual current, 1.2567 A | 1.257 W | 142.2 C |
| the checker's commanded 4 A (outside R-b) | 4 W | 286 C at 52.5 C/W (276 C at the sheet's 50) |

So the inhibit is what holds a commanded charge beyond R-b off the FET, wherever it sets. **E11-45** measures it: a hard short kept, the -1
latched again with the input present and ChargeCurrent forced to its register maximum, the current into PACK_P at most 1 mA and the FET's
junction within 2 K of its case for 10 minutes; and (c2) the open case below, recorded.

**Its reach, read after drafting (the one design-out attempt):** the inhibit sets only when CELL+ falls under 1.98 V. A latch while a source
is present (the pack supplementing into the fault, the battery FETs on) leaves CELL+ tied to VSYS, which the charger holds into a resistive
fault at sqrt(P x R): **10.4 V** at the breaker's least-limit fault of 0.915 ohm with the front end's 118 W, so the inhibit sets only for
faults under **33 mOhm**. When such a resistive fault clears with the -1 latched, a charge passes the breaker's body diode with CELL+ reading
alive. **The breaker's PGD reads high in that state too:** the LM5069 switches PGD on VDS alone (8.3.6), and a reverse current makes VDS
negative. So no board A signal, and no PGD, tells a latched -1 passing charge from an -1 that is on. **B-R2 stays OPEN for that case**:

| Route | What it is | Owner |
|---|---|---|
| **R1 (SESSION: preferred)** | board P tells the latch by the breaker's gate state (a gate-below-OUT comparator brought to board A), or blocks reverse current in the breaker (a reverse-blocking element), so a latched -1 passes no charge | board P's generator (record l8p) with record l9stk |
| R2 (the fallback) | a hardware cap on the charge current on board A, above R-b's largest 1.2567 A and under 1.405 A (the latched FET's body diode at 150 C held from 76.25 C at VSD 1 V and 52.5 C/W): a high-side current-sense part at R17 with a timed off-state on Q49, none of whose parts is held; an 11.8 % window | this record with board A's generator |

Until one is drawn, a charge past R-b in that state rests on the firmware (R-b, IF-7); at R-b's largest the FET reads 142.2 C held.

**The charger-side hold** is the inhibit itself where it sets, until the terminal is alive; the firmware's IF-7 reports the trip and writes ChargeCurrent
only after the restart (**E11-44**); the hold does not wait on it.

**Residuals:** Q49 shorted holds the battery FETs off (their body diodes carry the discharge, and record l8p's PTC trips the breaker before
their junctions pass 150 C); Q47, Q48 or Q49 open loses the inhibit or never releases it (E11-45 d); a Q46 open lets an input's arrival
drop a live pack for the pulse and the restart (E11-45 b); Q44 shorted holds the breaker off (fail-safe, revealed at commissioning).

**Status:** DD-7 **DRAFTED** for the first restart and for every latch whose fault takes CELL+ dead (the dark kit on battery, a hard short,
the input's return), CONDITIONAL on E11-45 and on TI's answer on BATDRV held at VSYS; **B-R2 OPEN** for a latch with a source present into a
resistive fault (route R1, owner board P's generator with record l9stk; R2 this record's fallback); IF-7 the firmware owner's. New board A designators: Q44 to Q49, R82, R83, R106 to R109, R144, D25. The
draft is a new apply script in this record: L4-E9's change list gains it after record l8p's PTC draft (the integrator's).

Not claimed: nothing here is verified, built or measured; software tests establish this record's own behaviour only.

## 20. Round 10: board A's side of the breaker's latch against record l8p's route R1 (L8P-F04, L8P-F05; 4 October 2026; out 20)

**The task.** Record l8p's round 3 (branch `fnd/l8p2` at `a46597e2`, merged into this branch for the composition tests) drew route R1
on board P: a reverse-charge detector (U103 and U104) holds the enable loop's return DOCK_EN_RET under 0.055 V while a charge over
0.368 to 1.213 A passes the off breaker's body diodes, and asks board A (its 12f, finding L8P-F04) to set the hardware charge inhibit
while the return is low and DOCK_EN_OUT is powered, whatever CELL+ reads, within 1 ms; to hold it at least 1.0 s after the return
rises (the breaker restarts within 0.948 s); then to release it on CELL+ alive; and to load DOCK_EN_RET with 1 MOhm or more. Its
L8P-F05 found round 9's dead point under the level the LM5069's internal 1 MOhm holds CELL+ at with the breaker off. The failure
cases are those of case row **C-PROT** (record l9stk `L9-STACKUPS.md` 15.1, 15.6 and 15.7 with this record's section 19, as on set
29's line `e58e906a`; the current sharing between the battery FETs and the 1 MOhm's tolerance UNSETTLED and not leant on). Record
l8p's page and output are read from `a46597e2` by sha256 (`l4e11_power.py`, out 20). Every circuit change is a release-guarded
draft; nothing is built, bought or measured.

### 20a. The failure, reproduced on round 9's draft (RECORD, l8p; INFERRED)

| Case | Round 9's reading | Against |
|---|---|---|
| L8P-F04: the return held at 0.055 V, BRK_VIN 7.6 V and 10.6 V | DOCK_EN_OUT 2.52 and 3.51 V; Q47 read half of it, 1.26 and 1.75 V | the 2N7002's 2.5 V: **the inhibit did not set** |
| L8P-F05: the breaker off, BRK_VIN 16.8 V and the 29.2 V clamp | CELL+ 2.80 V with board A's 200 kOhm (1.92 V with U104's 365.2 kOhm), 3.34 V at the clamp | round 9's 1.98 V dead point: **the inhibit could release with the breaker off** |

### 20b. The redrawn circuit (SESSION, `apply_gen_sch_a_dd7.py`)

| Part | Value | What it does |
|---|---|---|
| U48 | TPS37A010122DSKR (C3685740, U34's and U46's part) on VBAT | channel 1 (OV) reads DOCK_EN_RET on SENSE1 directly; channel 2 (UV) reads DOCK_EN_OUT on SENSE2 |
| R109, R144 | 562k and 422k, 0.1 % | DOCK_EN_OUT's divider, 0.4289 of it; 984 kOhm on the loop (round 9's 2 MOhm) |
| R249, R250 | 100k from DD7_VC to DD7_LP; 1M from DD7_LP to DD7_T | U48's RESET2 is DD7_LP (high: the loop powered); RESET1 is DD7_T, pulled up only from DD7_LP: **DD7_T high = the return held AND the loop powered**, the trigger |
| Q50, Q51, R251, R252 | 2N7002; AO3401A; 100k / 200k | the arm: DD7_T turns Q51 on (VGS -VBAT/3), which charges the hold node DD7_H from VBAT |
| R84, D26, R253 | 56R 1206; 1N4148W; 10k | the arm's current; its diode into DD7_H; R253 bleeds Q51's off leakage so the hold always ends |
| C241, R85 | 1 uF 100 V X7R 1210 (C382212); 1.2M 1 % | the hold |
| U47 | TPS37A010122DSKR on VBAT | channel 1 (OV) on DD7_H with C248 on CTS1: RESET1 asserts after the set delay and holds while DD7_H is over 0.79 V; channel 2 (UV) on CELL+ |
| C248 | 3.9 nF C0G | U47's CTS1: the set delay, 0.382 to 0.710 ms (SNVSBJ1E Equations 5 and 6) |
| R107, R108, Q52, R254 | 464k / 100k 1 %; 2N7002; 1M | U47's CELL+ reading; its foot DD7_REF goes to DD7_N through Q52 only while the loop is powered and an inhibit is asked, else R254 lifts it and the channel reads alive |
| R255 | 1M | DD7_N's pull-up; DD7_N low = the inhibit asked (U47's RESET1 and RESET2) |
| Q47, Q49, R82, R83 | 2N7002; AO3401A; 100k / 200k | **the inhibit:** Q47 (gate DD7_LP) passes DD7_N to SYS_INH_D; Q49 holds CH_BATDRV, the battery FETs' gates, at VBAT |
| Q48, R256 | 2N7002; 4.7k 1206 (6.8k in round 11 only: section 22) | **the bleeder:** while the inhibit holds, CELL+ is loaded into DD7_N, so it reads alive only when the breaker drives it |
| Q46 | 2N7002, gate moved to DD7_N | the input-return pulse is blocked while VBAT is up and nothing is asked (the kit on its pack), allowed while VBAT is down or an inhibit holds |
| R233, D27 | 100k; BZT52C12 | DD7_VC, the gates' supply under 12.7 V |
| TP1, TP2 | test points | DD7_H and DD7_N, for E11-45 |

Kept from round 9: Q44, R106, D25 and Q45 (the input-return reset), Q49, R82 and R83. The nets DD7_ALIVE and SYS_INH_G are gone.
U47 and U48 sit beside C238 (the charger draft's 1 uF at U42's IN), their VDD bypass, as U46 does. **No firmware anywhere.**

**Designators.** U47, U48, Q50 to Q52, D26, D27, TP1 and TP2 lie above every board A draft's. R84, R85, R233 and C241 are gaps that
no draft composed in L4-E9's order uses and no comment of `gen_sch_a.py` names; R9, R53, R63, R69, R79 and R185 are gaps too, but its
comments name them retired, so they are not reused. R249 to R256 and C248 lie above the main-based order's highest: d8dec31's mainpb
takes the next free R and C at apply time and runs last, so it takes R257 and C249 on the main-based order (R248 and C247 before); on
set 29's order l8r2's slotlm already sets them higher, and R249 to R256 and C248 are free there. Its fixed references are L4-E9's
R-194 (L8G-F12).

### 20c. The thresholds and their tolerances (MAKER: TI SNVSBJ1E, VITP and VITN 0.792 / 0.800 / 0.808 V, the variant's 2 % hysteresis within +-1.5 %, ISENSE 100 nA at 800 mV and 2 uA its largest row; resistors at their tolerances, each at its worst sign; INFERRED)

| Reading | Where it switches | Against |
|---|---|---|
| the return held (U48 channel 1, its OV release) | under **0.7755 V** at least; read closed over 0.84 V at most | board P's pull, 0.055 V: **0.72 V of margin**; the closed return in service, 2.894 V at the bound point: 2.054 V of margin |
| the loop powered (U48 channel 2, its UV release) | over **1.981 V** at most (1.825 V at least); unpowered under 1.789 V at least | the interface's 2.0 V; the held DOCK_EN_OUT (RT1 at 5 kOhm, R106 +1 %, board A's 984 kOhm on it): **2.545 V at 7.6 V, 3.535 V at 10.6 V, 5.581 V at 16.8 V**, 0.564 V or more over the powered reading |
| CELL+ alive (U47 channel 2, read only while an inhibit is asked and the loop is powered) | dead under **4.076 V** at least, alive over **4.774 V** at most (the foot at RESET's 0.060 V, VOL read as 60 ohm) | the breaker's restart drives CELL+ to the pack's 10.6 to 16.8 V; the latch holds CELL+ at 0.154 V (below) |

**The load on DOCK_EN_RET** is SENSE1 alone, at most 2 uA: over 8.7 MOhm at the return's 17.4 V clamp, against the interface's 1 MOhm.
**The bound point** (record l9stk, 10.6 V, RT1 47 kOhm): the first inverter's gate reads 2.952 V unloaded, 2.939 V with round 9's 2 MOhm,
**2.894 V** with round 10's loads (R109 and R144 on DOCK_EN_OUT, 2 uA on the return), against its 2.5 V.

**The interface's literal box, and why board A reads the return held under 0.7755 V and not up to 1.0 V (SESSION; finding
L4E11-R10-F1 for record l8p).** The box "RET under 1.0 V with OUT at 2.0 V or over" holds every state board P produces (the return
at 0.055 V). It also holds a CLOSED loop: RET/OUT is 22 / (22 + RT1), under 0.5 for RT1 over 22 kOhm, at BRK_VIN under 2.82 V (RT1
30 kOhm) or 3.59 V (RT1 47 kOhm). Every ramp of a closed loop (a docking, the gauge's wake, a precharge back-fed through the breaker's
body diodes) passes through it, and a trigger there stops a dead pack's precharge (the hold and the inhibit while BRK_VIN rises,
then again on every rise). Board A's reading is therefore narrower than the box and holds the state board P produces with 0.72 V
of margin. The 1.0 V figure is a 2N7002's least threshold (l8p 12f).

**No window.** A ramping closed loop never reads held while RT1 is under **25.8 kOhm** (RET/OUT over 0.4603 when OUT reads powered).
Murata prints RT1 at most 15 kOhm at 25 C and 100 kOhm only above 110 C (DM-SA16-E056 Rev.1 p.4, MAKER); a back-fed precharge
carries at most 0.33616 A, so the FETs' copper sits at the air. At the precharge's floor (BRK_VIN 4.70 V, RT1 at 15 kOhm) the return
reads 2.20 V, 1.36 V over the closed reading; it would read held there only past RT1 91.1 kOhm.

**Against board P's guard.** Board A reads a closed return as held only past RT1 269 kOhm at 10.6 V (445 kOhm at 16.8 V); board P's
first inverter turns off (its gate 2.5 to 1.0 V) from 61.3 to 201.2 kOhm at 10.6 V: board A never reads held before the guard's own
trip.

### 20d. The delays (INFERRED; each element's bound named)

| Step, from the return falling under 0.7755 V | At most |
|---|---|
| U48's release (tCTR with no capacitor, MAKER) | 40 us |
| DD7_T to Q50's 2.5 V (R250 1 MOhm into 110 pF, ASSUMPTION: Q50's 50 pF typical Ciss doubled and U48's pin) | 41.2 us |
| Q51 on (R251 and R252 into 1.5 times its typical 645 pF) | 25.2 us |
| DD7_H over 0.808 V (the arm's time constant at most 71.5 us) | 5.6 us |
| U47's CTS1 (Equations 5 and 6, C248 +-5 %, RCTS 88 to 122 kOhm) | 0.382 to 0.710 ms |
| Q49 on (R82 and R83 into 1.5 times its typical Ciss) | 26 us |
| **the inhibit set** | **0.85 ms**, under the interface's 1 ms |

**The arm completes before the set:** the set comes at least 0.382 ms after DD7_H passes 0.808 V, and board P's pull holds the trigger
while the charge flows, i.e. until the inhibit stops it (Q44's own pull lasts at least 78.6 ms). With the arm's time constant at most
71.5 us (R84 into C241's 1.265 uF most) DD7_H is 0.99519 of the way, so the hold starts from at least **11.145 V** (VSYS_MIN's 12.054 V
less D26's 0.855 V at 10 mA). **The charge through the off breaker ends within 1.41 ms** of passing board P's threshold (its pull
0.56 ms and board A's set), against E-14's 10 ms.

**The hold.** DD7_H falls from 11.145 V through R85 (1 %) and C241 (0.6502 uF at its least: K, X7R's 15 % and 15 % under DC bias,
ASSUMPTION) to U47's OV release, 0.7924 V at most, against every sink on the node: D26's reverse leakage 0.807 uA at 86.25 C
(INFERRED, log-linear between the sheet's 25 nA at 25 C and 30 uA at 150 C), SENSE1's 100 nA (MAKER) and C241's insulation 0.292 uA
(ASSUMPTION). It lasts **at least 1.341 s** after the return rises: 0.341 s over the interface's 1.0 s and 0.393 s over the breaker's
restart (0.9477 s). At most 5.82 s (the clamp's VBAT, the sinks reversed). It still reaches 1.0 s with D26's leakage 2.76 times the
inferred figure. **It always ends:** Q51's off leakage, 43.6 uA at 86.25 C (the sheet's 55 C row doubled every 10 K, INFERRED), holds
DD7_K at 0.436 V through R253, 0.339 V under the OV release's least 0.7756 V.

### 20e. L8P-F05 corrected: the release on CELL+ alive (INFERRED)

**A dead CELL+ never sets the inhibit.** U47's channel 2 reads alive while R254 lifts its foot, that is while nothing is asked. It
**keeps** an inhibit that is set: Q52 then grounds the foot through DD7_N, and Q48 loads CELL+ through R256, so CELL+ reads alive
only when the breaker itself drives it. Round 9's dead point leant on board A's 200 kOhm against the LM5069's internal 1 MOhm, whose
tolerance is not printed; the latch leans on R256's 4.7 kOhm:

| BRK_VIN | The LM5069's resistor may fall to | CELL+ at 1 MOhm with the three FETs' 3 uA (25 C) | Round 9 |
|---|---|---|---|
| 16.8 V | 19.9 kOhm (0.020 of 1 MOhm) | **0.154 V**, 3.922 V under the dead reading | 2.80 V against 1.98 V |
| 29.2 V (the clamp) | 34.5 kOhm (0.035) | **0.213 V**, 3.864 V under it | 3.34 V against 1.98 V |

The latch reads dead while every source into CELL+ stays under **0.846 mA** together (the static limit). The battery FETs' off
leakage (Nexperia prints at most 1 uA each at 25 C and 10 uA at Tj 125 C, nothing over 125 C: MAKER; rounds 10 and 11 called the hot
figure "not printed") may reach 272 uA each before that limit; the breaker pair's leakage enters CELL+ too (record l8p's L8P-F06),
and section 22b counts all five devices. By the hold's end CELL+ has fallen under the dead reading unless the breaker drives it:
from VSYS's 17.375 V through R256 into CELL_FUSED's 104 uF (+20 %, ASSUMPTION) **within 1.218 s with the sources at their hot bound
(434.8 uA, 22b), inside the hold's least 1.341 s while the sources total under 520.7 uA** (the coupled limit, round 12; 0.859 s is
the figure with no source, which rounds 10 and 11 printed alone: the check V2's V2-B1). The release: the breaker's restart drives
CELL+ over 4.774 V against R256's 3.57 mA at 16.8 V, inside IF-1's 0.81 A room.

### 20f. The service untouched (INFERRED)

- **10 A held, 18 A for 60 s and every current-limit excursion:** the breaker on, the return at least 2.894 V at the pack's 10.6 V with
  RT1 to 47 kOhm, read closed with 2.054 V to spare; board P's detector never pulls a running breaker (l8p 12e). No trigger, no hold,
  no request: Q47, Q48 and Q52 idle, Q46 blocks the input-return pulse. **No board A part acts on a running breaker or its loop.**
- **The precharge and the gauge's wake** (a closed loop back-fed through the body diodes): never read held while RT1 is under 25.8 kOhm,
  and CELL+ never sets the inhibit, so a dead pack's precharge passes. Round 9's inhibit set on CELL+ under its dead point whenever the
  loop read powered, which a back-fed precharge reaches on the way up: at its threshold corners it could stop the precharge (withdrawn).
- **A docking:** OUT and RET rise together at RET/OUT of 0.4603 or more (RT1 under 25.8 kOhm): no trigger. With no source board A is
  unpowered until the breaker's start feeds VBAT, and at power-up U47 and U48 hold their outputs for tSD, 2 ms at most: the inhibit at
  most that long, then on CELL+ as read.
- **Each source present or absent** (shore, solar, vehicle): any source holds VSYS at VSYS_MIN's 12.054 V or more, the basis of the
  hold's start; with no source no charge exists to inhibit, and board A's DD-7 parts are unpowered with VBAT.

### 20g. The parts within their limits (MAKER limits; INFERRED readings)

| Part | Reading | Limit |
|---|---|---|
| U47, U48 | VDD 12.054 to 29.2 V; SENSE and RESET at most 29.2 V; RESET sinks at most 3.73 mA (the bleeder at 16.8 V) and 4.32 mA with CELL+ following VBAT at SYSOVP (R256 at -1 %); 6.39 mA only with CELL+ at the 29.2 V clamp | VDD 2.7 to 65 V; 65 V graded pins; VOL 300 mV at 5 mA and TI's recommended 5 mA at most, the absolute maximum 10 mA; the clamp's state needs a second fault (V1's minor; the states in 22d) |
| 2N7002 (Q44 to Q48, Q50, Q52) | VGS at most 12.7 V (DD7_VC); VDS at most 29.2 V; at most 6.39 mA | 20 V; 60 V; 0.115 A |
| AO3401A (Q49, Q51) | VGS 4.02 to 9.86 V; VDS 29.2 V; Q51's arm peak 0.514 A (0.29 A at 16.8 V) | +-12 V; 30 V; IDM 27 A |
| D26 (1N4148W) | the arm's peak 0.514 A decaying in 71.5 us, I2t 9.44e-06 A2s, at most once a hold (1.0 s apart) | 4 A for 1 us; 1 A for 1 ms (I2t 1e-03 A2s) |
| R84 (56R 1206, pulse-rated) | the arm's 0.539 mJ at the clamp: 14.6 W peak decaying in 71.5 us (4.7 W at 16.8 V), once a hold | no held sheet prints a pulse rating; Yageo's short-time overload is a 5 s test and no basis for a 71 us pulse (V1's minor: the comparison withdrawn). **Specified:** a part whose maker prints a single-pulse curve covering 14.6 W for 72 us once a second; its code owed to Layer 6 (CONDITIONAL) |
| R256 (4.7k 1206; 6.8k in round 11 only) | 0.0596 W at 16.8 V while the inhibit holds after a restart; 0.1807 W at the 29.2 V clamp | RC1206's 0.25 W derated to 0.202 W at 86.25 C |
| D27 (BZT52C12) | at most 0.18 mA, 2.28 mW from the 29.2 V clamp through R233 | its 370 mW at 25 C ambient (DS18004 note 8) |

**IF-1's static draw restated** (19f's table, R107 and R108's 0.084 mA row replaced): U47 and U48, 0.0052 mA; R233 into D27, at most
0.168 mA; Q51's off leakage, 0.005 mA; the CELL+ divider into DD7_VC, 0.0107 mA: **4.08 mA in all, 0.5 % of the 0.81 A room**
(round 9's 3.98 mA).

### 20h. The checked correction (closure credit (a) to (c))

| Item | How it is shown |
|---|---|
| (a) composes in L4-E9's order | board A composed with every pending board A draft and record l8p's PTC (the tree's, round 3), this draft before d8dec31's mainpb: the generator runs to its end with `intent.write` (750 parts); refused without l8p's loop, once applied, refused a second time and on the tree (`test_l4e11`) |
| (b) the changed nets in the regenerated netlist | `check_dd7_netlist.py` reads every DD-7 pin, value and net membership from the netlist record l8p's `gen_netlist.py` regenerates: **DRAWN**; five circuit mutations each read **FAIL** (U48's SENSE1 on DOCK_EN_OUT, Q47's gate on DD7_T, R108's foot on ground, R256 removed, a 100 kOhm load on DOCK_EN_RET), and since rounds 11 and 12 three more (R256 at 6.8k, R84 without its pulse rating, a battery FET drawn reversed); the committed netlist reads NOT DRAWN |
| (c) the electrical acceptance on C-PROT | out 20: the held return at 7.6 and 10.6 V sets the inhibit within 0.85 ms (was never); the hold at least 1.341 s; CELL+ with the breaker off at 16.8 V and 29.2 V held at 0.154 and 0.213 V against the 4.076 V dead reading (was 2.80 and 3.34 V against 1.98 V); the latch with a source present into a resistive fault: B-R2 with route R1, the charge ending within 1.41 ms; the service rows above; each part within its printed limit |

### 20i. T2, recorded now: E-1's even split (OPEN against E-1's acceptance; its comparison is the next task)

Record l9stk's E-1 limit (45.88 K/W, 1.345 W a FET at 23.93 A) assumes the current splits evenly between Q39, Q40 and Q42. With one
FET at r and two at R, the one carries I R / (R + 2 r) and dissipates I^2 R^2 r / (R + 2 r)^2. Over r this is largest at r = R / 2:
I^2 R / 8, which is **9/8 of the even split's I^2 R / 9**. With two FETs the even split is the worst case; with three it is not. The
other two then carry I / 4 each (9/16 of the even loss), so that FET's rise is (9/8) (Zself + Zmut) against E-1's (Zself + 2 Zmut):
over E-1's figure at that split wherever Zmut is under Zself / 7, and at the worst split, one FET at R / (2 - 4 m) for m = Zmut /
Zself, wherever Zmut is under **Zself / 4** (round 11's correction of this line, 21a: 1.0045 at m = 0.2, where R / 2 gives 0.9643).
With the coupling negligible the allowance's 45.88 K/W puts that junction at
**157.7 C** held at 23.93 A where E-1 states 150 C (INFERRED; the spread of RDS(on) between parts is not printed). **45.88 K/W is NOT
SETTLED**; E11-29's row says so. T2 compares at most three approaches for E11-37 and E-1 together.

### 20j. E-14 and E11-45 as they now read

- **E-14** (record l9stk's, with record l8p's 12g), board A's part: (b) with the return held the inhibit sets within 0.85 ms, so the
  charge through the off breaker ends within 1.41 ms of passing board P's threshold (0.368 to 1.213 A), under E-14's 10 ms and
  inside record l8p's 10.3 K for 10 ms; (c) the battery FETs stay off at least 1.341 s after the return rises (the breaker restarts
  within 0.948 s), then are released once CELL+ reads alive.
- **E11-45** (section 8): (c2) is B-R2's case with route R1, no longer open on board A's side; (e) L8P-F04's interface alone; (f)
  L8P-F05's latch with the breaker held off at 16.8 V and 29.2 V; (g) a back-fed precharge not inhibited; (h) the hold timed at -20,
  25 and 85 C, at least 1.0 s; (d) each failure found by its row.

### 20k. Findings for other records (each is its owner's; nothing of theirs is edited here)

| Finding | Owner | What |
|---|---|---|
| L4E11-R10-F1 | record l8p (12f) | the interface's box (RET under 1.0 V with OUT at 2.0 V or over) also contains a closed loop at low BRK_VIN with RT1 over 22 kOhm, which every back-fed ramp passes; the state board P produces is "held" (0.055 V); board A reads it under 0.7755 V (20c) |
| L4E11-R10-F2 | record l8p (`check_l8p_netlist.py`, its EN group on board A) | it wants DOCK_EN_OUT and DOCK_EN_RET to reach J_DOCK and RT1 alone, so it reads FAIL on any board A that carries DD-7 (round 9's Q44 and R109 already; round 10's U48 and R109): the group should allow DD-7's loads, which `check_dd7_netlist.py` reads |
| L4E11-R10-F3 | record l9stk (15.5, the thermal guard) with record l8p (RT1) | Murata's PRF15BB103RB6RC prints 10 kOhm +-50 % at 25 C, **100 kOhm at a sensing temperature over 110 C** (no upper bound) and **4.7 MOhm at 130 +-3 C** (DM-SA16-E056 Rev.1 p.4); "47 kOhm at 130 C" is the 470 ohm group's column. The guard's trip lies under 133 C, but its no-trip side in the 18 A service (the FETs at 118.0 C) rests on no printed point: RT1 may pass the first inverter's 61.3 kOhm anywhere over 110 C |

### 20l. What stays open

- **Physical:** the hold's capacitor under DC bias and D26's hot leakage (E11-45 h); U47's and U48's thresholds as the lot reads them;
  the latch with the breaker held off (E11-45 f); board P's own conditions (record l8p: E-14b, R10's tolerance, E-12c).
- **T2 (20i):** E-1's even split, OPEN against its acceptance (round 11 corrects it in the acceptance at 40.78 K/W, section 21);
  **E11-37** OPEN (Q-TI-17 or the bench with three).
- **The latch with a source present and no charge over board P's threshold** stays latched (nothing asks an inhibit and Q46 blocks
  the pulse): it restarts on board P's detector at a charge over 0.368 to 1.213 A, on a redocking, or on the input's return to a dark
  kit (record l9stk's DD-7 reach, unchanged).
- **The window's bound** (RT1 under 25.8 kOhm) rests on RT1 staying under it while the FETs' copper sits at the air: Murata prints no
  point between 25 C and 110 C (its curve is typical).
- **DD-3** (19e) and the rest of section 19g as they stand.

### 20m. Status of round 10

| Item | Status |
|---|---|
| L8P-F04 | **corrected in the draft:** U48 reads the held return (under 0.7755 V) and the powered loop (over 1.981 V at most); the inhibit set within 0.85 ms, held at least 1.341 s, released on CELL+ alive |
| L8P-F05 | **corrected in the draft:** a dead CELL+ never sets the inhibit; the bleeder holds the latch for any source under 0.846 mA (the LM5069's resistor down to 0.020 of its value at 16.8 V) |
| B-R2 | **drafted on both boards** with route R1 (board P's detector, record l8p; board A's interface, this round); CONDITIONAL on E11-45 and record l8p's E-14 and E-12c |
| T2 | **recorded, OPEN** against E-1's acceptance (20i); round 11 corrects it in the acceptance (21e) |
| the composition and the netlist | board A composed in L4-E9's order runs to its end; `check_dd7_netlist.py` DRAWN, five mutations FAIL |

Not claimed: nothing here is verified, built or measured; software tests establish this record's own behaviour only.

## 21. Round 11: E-1 with the sharing not assumed even, and E11-37, over three approaches (task T2, 4 October 2026; out 21)

**The case** is the coordinator's shared row **C-PROT rev 1** (`_runs/cases/CASES-2026-10-04.md`; record l9stk 15.1, 15.6 and 15.7 at
`0d72880b`, this record's section 19 at `e60a94a8`): 10 A held and 18 A for 60 s never interrupted, the breaker's band 18.32 to
23.93 A, the start at L4-E12's 76.25 C plus own heating, docking included, each source present or absent. The row names "current
sharing between the battery FETs" as **unsettled**; this round bounds it on printed figures. Inputs: round 10's 20i (T2 recorded),
the independent check V1 of round 10 (CONFIRMED AS CONDITIONAL, conditions C1 to C4; its two minors are applied in 21f), and the
shutdown checkpoint's row T2. Nothing is bought, built or measured.

### 21a. The defect on C-PROT rev 1 (record l9stk's E-1, INFERRED)

E-1 sized each FET at the even split, **1.3448 W** at the RDS(on) allowance 21.136 mOhm, and set each FET's installed (Zself + 2
Zmut) at most **45.88 K/W** with R17 apart (the band 9.16 K and R17's 2.86 K in the 150 C budget). Every FET's RDS(on) is at most the
allowance; Nexperia prints no minimum. With two at R and one at R / x (x at least 1), the hottest one's rise is I^2 R (Zself x + 2
Zmut) / (x + 2)^2; against the even split's I^2 R (Zself + 2 Zmut) / 9 the factor is 9 (x + 2 m) / ((x + 2)^2 (1 + 2 m)) with m =
Zmut / Zself. It is largest at **x = 2 - 4 m while m is under 1/4**, and the even split is the worst at or over 1/4. At m = 0 the
factor is **1.125** (one FET at R / 2 takes I / 2 and 1.5129 W), and at record l9stk's 45.88 K/W the hottest junction reads **157.7 C**
held at 23.93 A where E-1 states 150 C: **E-1 fails at its own case.** Round 10's 20i said the even split's figure is exceeded
"wherever Zmut is under Zself / 7"; that holds for the split R / 2 only, and 20i is corrected in place: over every split the region is
**Zmut under Zself / 4** (at m = 0.2 the worst split gives 1.0045 where R / 2 gives 0.9643).

**The drive.** The allowance is section 15c's two-chord figure at the charger's **printed least gate drive, VBATDRV_ON 8.5 V**
(SLUSE65A p.17), and 150 C; at a 10 V drive it would read 15 mOhm and every bar would loosen by that ratio, so the printed least
drive is the one taken (MAKER, INFERRED). *For information only:* with the spread bounded at the sheet's typical over its maximum
(0.8 at -10 V and 25 C; no printed minimum, so not a bound) the factor would be 1.0651.

### 21b. Three approaches (MAKER rows; the bars are installed per-FET figures at E-1's limit; INFERRED)

| Approach | What changes | E-1's installed bar | Gate load against TI's 5 nF (SLUSE65A p.92) | Verdict |
|---|---|---|---|---|
| **(i)(a) three BUK6Y10-30P kept** | no land, net or part; the acceptance | (Zself + 2 Zmut) at most **40.78 K/W** for any split | 7.08 nF typical at -15 V, about 8.61 near 0 V: 1.42 times (OPEN, E11-37) | **SELECTED** |
| (i)(b) three PXP9R1-30QL (Nexperia, MLPAK33) | a new land; rated 150 C, so the record's convention puts its limit at 125 C | 32.85 K/W (15.619 mOhm at 8.5 V and 125 C from the printed 15.3 mOhm at -10 V and 150 C, gate chord x1.1109) | 8.58 nF typical for three, 1.72 times | rejected: worse on its bar (printed maxima) and on Ciss (typical) |
| (ii) two FETs under 5 nF | Q42 and its land leave; RT1 to the pair's centroid | (Zself + Zmut) at most **20.39 K/W** (record l9stk; the even split is the worst for two) | the BUK6Y10-30P pair 4.72 nF **typical** at -15 V, about 5.74 near 0 V (over it); no maximum printed | rejected now (its bar is 0.5 of (i)'s); the correction scope if E11-37 refuses three |
| (iii) a buffer between BATDRV and the FETs | a supply below VSYS less 10 V, which board A has not | not bounded | not bounded | rejected: no printed basis (below) |

The bar of (i)(a) for a coupling read on the specimen (record l9stk's even-split 45.88 K/W times 8 (1 - m)(1 + 2 m) / 9 for m under
1/4; the worst FET at R / (2 - 4 m)):

| m = Zmut / Zself | 0 | 0.05 | 0.1 | 0.15 | 0.2 | 0.25 | 0.4 |
|---|---|---|---|---|---|---|---|
| (Zself + 2 Zmut) at most, K/W | **40.78** | 42.62 | 44.04 | 45.06 | 45.68 | 45.88 | 45.88 |

(ii)'s parts, each Ciss against 2.5 nF at its sheet's own VDS: the printed maximum where the sheet prints one (Vishay's two), the
typical figure where it prints none (round 12, the check V2's V2-m1: round 11 took Vishay's typical column and called it the maximum).
BUK6Y10-30P 2.36 nF typical (two 4.72, under 5 nF); PXP9R1-30QL 2.86 typical (two 5.72, over); AONS21357 2.83 typical (two 5.66,
over); SQJ403EP 4.5 nF maximum, 3.4 typical (two 9, over); SQJ407EP 10.7 nF maximum, 8.2 typical (two 21.4, over). Only the
BUK6Y10-30P pair stays under 5 nF, **on a typical figure: CONDITIONAL, Q-TI-17 (e)**.

(iii): SLUSE65A prints BATDRV as the gate driver of the linear-mode regulation of VSYS_MIN and of the ideal diode in supplement
("BATFET is in linear mode to regulate VSYS at minimum system voltage when battery is depleted ... works as an ideal-diode in
supplement mode"), the driver "internally integrated into the IC", and names no external driver or buffer on BATDRV in any sentence
(the script refuses if one appears). A buffer would sit inside loops whose gain and compensation TI does not print, and a follower
loses its own drop from BATDRV's least 8.5 V drive, raising every RDS(on) bound. No printed figure supports it; Q-TI-17 (f) asks.

### 21c. The connected path (INFERRED)

- **The charger's gate drive:** (i) BATDRV into the three, 42.48 / 51.66 us on and 18.08 us off (round 9); (ii) 28.32 / 34.44 us
  and 12.05 us; (iii) not bounded.
- **IF-1 and DD-7** do not depend on the count: Q49 moves at most 192 nC (three QG(tot) maxima) and BATDRV sinks at most 3.83 mA
  while it holds. The breaker's band (23.93 A) and R17 are untouched. (i)(a) keeps the land, the pour and RT1 at the three's
  centroid; (ii) would remove Q42 and move RT1 to the pair's centroid.
- **The service rows are unchanged** at the corrected bar, by construction (the factor does not depend on the current): 89.4 C at 10 A,
  118 C in the 18 A service, 150 C held at 23.93 A. E-1's limit, the 23.93 A, the 18 A for 60 s and 76.25 C are not lowered.

### 21d. The selection and the decisions (SESSION)

| Decision | Authority | Why no owner judgement stands | Reversed by |
|---|---|---|---|
| (i)(a): the three BUK6Y10-30P stay and **E-1's installed acceptance becomes the worst split's, (Zself + 2 Zmut) at most 40.78 K/W** (or the measured Zself and Zmut by 21b's formula) | SESSION (ruled by the L4-E11 author, 4 October 2026, under the owner's standing rules of 21 and 26 September 2026) | an engineering choice inside the task: no money, no requirement change, no reserved line; the printed figures leave (i)(a) ahead ((ii)'s bar is half, (iii) has none) | E11-29's coupon reading over the bar after a layout iteration, or a negative answer to Q-TI-17 (E11-37): then (ii), a draft owed |
| the RDS(on) allowance read at VBATDRV_ON's printed minimum, 8.5 V | SESSION | the conservative reading of a printed row | Nexperia printing a maximum at 8.5 V and 150 C (E11-36) |
| R256 6.8 kOhm and R84 specified pulse-rated (21f) | SESSION, on V1's minors | the part limits of 20g | a Layer 6 part whose sheet changes 21f's figures |

**E11-37 STAYS OPEN:** no printed figure decides a three-device gate load against TI's 5 nF. Q-TI-17 (`clarification/TI-QUESTIONS.md`,
drafted, **NOT SENT**) gains **(e)**, the 5 nF's drain-source voltage and the pair's 4.72 / 5.74 nF typical (the fallback rests on that
typical figure), and **(f)**, the gate load TI accepts on BATDRV (Ciss or QG(tot), over -20 to 70 C) and whether any buffer is
supported. The bench row E11-37 stands. On a negative answer the supplier's correction scope is (ii): the pair, its bar 20.39 K/W
measured on the coupon, Q42 removed (a draft then owed).

### 21e. Status and closure credit

| Item | Status |
|---|---|
| E-1's even split (T2, recorded in 20i) | **CORRECTED IN THE ACCEPTANCE**: the bar 40.78 K/W for any split; CONDITIONAL on E11-29 at that bar and E11-36's allowance. No printed figure shows 40.78 K/W achievable: E11-29's coupon decides (the bar 11.1 % under the even split's) |
| (a) composition | the charger draft changes only its layout comment (the bar); board A composes in L4-E9's order and runs to its end (`test_l4e11`) |
| (b) netlist | no net changed by this correction, so a netlist reading does not apply to it; DD-7 still reads DRAWN (at R256 4.7 kOhm since round 12) |
| (c) electrical acceptance on C-PROT rev 1 | the hottest junction at most 150 C held at 23.93 A from 76.25 C over a scan of every split of the three RDS(on) values under the allowance at m from 0 to 0.4, at the printed least drive; the even split's 45.88 K/W, a bar 1 % over 40.78, or the split read as even each FAIL (`test_l4e11`) |
| E11-37's state | **OPEN** (TI or the bench) |
| E11-29's row and block | restated at 40.78 K/W (section 8, 17d) |

### 21f. V1's minors of round 10 (R84 stands; R256's part is superseded by round 12, section 22)

- **R256:** round 11 moved it from 4.7k to 6.8k so that U47's RESET stayed under TI's recommended 5 mA at the 29.2 V clamp (4.47 mA
  against 6.39 mA), and printed its cost as a static limit of 0.597 mA beside a bleed of 1.228 s, 0.112 s inside the hold. The
  independent check V2 (V2-B1) showed that bleed counted no source: at 6.8k it ends inside the hold only for sources under 87.4 uA.
  **Those figures are WITHDRAWN**; round 12 compares V2's three corrections and selects 4.7k again (section 22), so section 20
  carries round 10's values.
- **R84 56R: SPECIFIED pulse-rated.** Its value text carries it; a part whose maker prints a single-pulse curve covering 14.6 W for
  72 us, its code owed to Layer 6 (CONDITIONAL). The 5 s overload comparison is withdrawn.
- **Credit:** (a) board A composes in main's order and runs to its end; (b) `check_dd7_netlist.py` reads R84's value as "56R 1%
  pulse-rated" and R256's as 4.7k: DRAWN, and three more mutations read FAIL (R256 at 6.8k, R84 without its rating, a battery FET
  reversed), eight in all; (c) out 20g, 20e and 22 on C-PROT rev 1.

### 21g. What stays open, and findings for other records

- **Physical:** E11-29 at 40.78 K/W (the coupon or the first prototype); E11-36 (the allowance); E11-37 (Q-TI-17 (a) to (f), or the
  bench with three); the bleed of CELL+ against the hold (section 22: E11-45 (f2) and (h), record l8p's E-14c).
- **V1's two minors that no record carried** (the check V2's V2-m4) are named in 22h, each with its owner and next action: the
  TPS37's hysteresis accuracy read as percentage points, and the CONOPS wording of the named residual.
- **For record l9stk (15.5, E-1):** its even-split 45.88 K/W is not the bar for three paralleled FETs whose RDS(on) spread is
  unprinted; this record carries 40.78 K/W (or 21b's formula) and edits nothing of l9stk's. The same holds wherever a record
  credits "the even split bounds each FET's power" (true for two FETs, 15c and 16b, not for three).
- **For Layer 9 and board A's PCB generator:** the layout requirement now carries 40.78 K/W (the charger draft's comment).

Not claimed: nothing here is verified, built or measured; software tests establish this record's own behaviour only.

## 22. Round 12: the check V2's finding V2-B1 (the cost of R256) as a design choice, and its minors for this record (4 October 2026; out 22)

**The case** is C-PROT rev 1. The independent check V2 (an AI review, as the coordinator received it; it read the combined candidate
`fnd/v2cand` at `dfa1eef2`, which holds round 11) confirmed round 11's item A (the worst split, the 40.78 K/W bar, E11-37 open) as
conditional and found one claim that does not stand, **V2-B1**: the cost of moving R256 to 6.8 kOhm. This round reproduces V2's
arithmetic in `l4e11_power.py`, compares V2's three corrections as an unresolved design choice, selects one, and carries V2's minors
m1 to m5 and m9. Nothing is bought, built or measured.

### 22a. The claim that did not stand, and V2's arithmetic reproduced (INFERRED)

Round 11 (21f) gave CELL+'s bleed with the breaker off as 1.228 s, inside the hold's least 1.341 s, beside a static limit of 0.597 mA
for the sources into CELL+. The bleed was taken towards 0 V, as if no source fed the node. A source I lifts the level CELL+ falls
towards to the foot plus I x R256, so **t = R C ln((V0 - Vinf) / (Vdead - Vinf))**, from VSYS's 17.375 V into CELL_FUSED's 104 uF at
+20 % (ASSUMPTION). The script reproduces each of V2's figures within 1.2 % and refuses otherwise:

| Case | This script | V2 |
|---|---|---|
| 6.8 kOhm, no source, towards 0 V (round 11's figure) | 1.228 s | 1.228 s |
| 6.8 kOhm, the record's 25 C sources, 19.8 uA | 1.257 s | 1.257 s |
| 6.8 kOhm, the sources at which the bleed takes the hold's least 1.341 s | **87.4 uA** | 88 uA |
| the same with board P's U104 divider and R107 with R108 credited as loads | 121.3 uA | 122 uA |
| 6.8 kOhm, the breaker pair at the 76.25 C air (L8P-F06) and the 1 MOhm, 86.6 uA | 1.339 s | 1.339 s |
| 6.8 kOhm, the breaker pair at the held 101.0 C case and the 1 MOhm, 404.8 uA | **2.056 s** | 2.06 s |
| 4.7 kOhm, no source, towards the foot (round 10 printed 0.859 s towards 0 V) | 0.866 s | 0.866 s |
| 4.7 kOhm, the sources at which the bleed takes 1.341 s | **520.7 uA** | 521 uA |
| 4.7 kOhm, the breaker pair at the held case and the 1 MOhm | 1.182 s | 1.18 s |

So the two limits of 21f could not both be used: with R256 at 6.8 kOhm the bleed ends inside the hold only while the sources total
under 87.4 uA, and V1's minor was applied by spending that margin.

### 22b. The sources into CELL+ with the breaker off and the inhibit held (each labelled)

| Source | Figure | Label and document |
|---|---|---|
| the LM5069's internal 1 MOhm, SENSE to OUT | 16.8 uA at BRK_VIN 16.8 V (29.2 uA at the 29.2 V clamp) | MAKER value (TI SNVS452G 7.5 note 1, as record l8p reads it); its tolerance is not printed |
| the three battery FETs Q39, Q40, Q42 | 3 uA at 25 C, **30 uA at Tj 125 C** (1 and 10 uA each, VDS -30 V) | MAKER, printed maxima: Nexperia BUK6Y10-30P (17 April 2020) Table 7 p.6. Over 125 C nothing is printed; on the sheet's own two rows' slope E-1's 150 C would read 53.3 uA for the three (INFERRED, information only) |
| the breaker pair Q101, Q102 (CSD18510Q5B) | 2 uA at 25 C; **69.8 uA at the 76.25 C air, 388.0 uA at the held 101.0 C case** | 25 C: MAKER (TI SLPS632, March 2017, p.3: IDSS 1 uA at VGS 0 V, VDS 32 V, TA 25 C, its only row). Hot: **ASSUMPTION**, record l8p's L8P-F06 (OPEN; `fnd/l8p2` at `69156072`, 12j, copied to `inputs/l8p-section12j-f06-69156072.md`): a doubling every 10 K |

**The hot bound on C-PROT rev 1** (the pack at 16.8 V, the battery FETs on their printed 125 C row, the breaker pair at its held
case): 16.8 + 30 + 388.0 = **434.8 uA** (116.6 uA at the air; 447.2 uA with BRK_VIN at the clamp; 458.2 uA with the battery FETs at
150 C, INFERRED).

### 22c. V2's three corrections on one basis

**Need 1:** the bleed with the sources at their hot bound ends inside the hold's least value. **Need 2:** U47's RESET sink stays
within TI's recommended 5 mA (SNVSBJ1E 7.3, p.6; the absolute maximum is 10 mA, 7.1, p.6) in every state where it sinks, R256 at -1 %.

| | (a) text only: 6.8 kOhm, the hold as drawn | **(b) R256 back to 4.7 kOhm, the hold as drawn** | (c) 6.8 kOhm, the hold lengthened (C241 2.2 uF) |
|---|---|---|---|
| the hold, least to most | 1.341 to 5.82 s | 1.341 to 5.82 s | 2.585 to 12.8 s |
| the static limit (the latch reads dead) | 0.597 mA | **0.846 mA** | 0.597 mA |
| the bleed with no source (towards 0 V) | 1.228 s | 0.859 s | 1.228 s |
| the bleed at the air's 116.6 uA | 1.381 s | 0.934 s | 1.381 s |
| the bleed at the hot bound's 434.8 uA (with the loads credited) | 2.189 s (2.063 s) | **1.218 s** (1.181 s) | 2.189 s (2.063 s) |
| the same with the battery FETs at 150 C (INFERRED) | 2.312 s | 1.248 s | 2.312 s |
| the coupled limit: the sources under which the bleed ends inside the hold's least | 87.4 uA | **520.7 uA** | 498 uA |
| what that leaves the breaker pair | 40.6 uA | **473.9 uA** | 451.2 uA |
| on the ASSUMED doubling, the pair's case (held: 101.0 C) or the slowest doubling at the held case | 68.4 C; every 17.49 K | 103.9 C; every 9.63 K | 103.2 C; every 9.72 K |
| **need 1** | **FAILS** at the hot bound and at the air | holds, 0.123 s inside the hold, on the ASSUMED leakage | holds, 0.396 s inside the hold, on the ASSUMED leakage |
| RESET at the instant of setting (CELL+ at VSYS's 17.375 V) | 2.7 mA | 3.85 mA | 2.7 mA |
| RESET with the breaker restarted while the hold runs (the pack's 16.8 V) | 2.61 mA | 3.72 mA | 2.61 mA |
| RESET with CELL+ following VBAT at the charger's SYSOVP, 19.5 V | 3.02 mA | 4.32 mA | 3.02 mA |
| RESET with CELL+ at VBAT's 29.2 V clamp | 4.51 mA | 6.45 mA | 4.51 mA |
| CELL+ at which RESET reaches 5 mA | 32.45 V | 22.51 V | 32.45 V |
| **need 2** | holds in every state | holds in every state without a second fault (22d) | holds in every state |

**What (c) moves for the hold's readers** (20d, 20g, E-14 (c), E11-45 (h)): the hold's most 12.8 s, from 5.82 s (the battery FETs held
off that long after every set, a false set at a docking included); the arm completes 0.9116 of the way before the set, from 0.99519,
so the hold starts from 10.209 V; R84's pulse 1.186 mJ and D26's I2t 2.08e-05 A2s, from 0.539 mJ and 9.44e-06 A2s; a 2.2 uF 100 V
part whose DC bias is not read. With R85 at 2.4 MOhm instead, the hold's least is only 2.08 s (D26's leakage and C241's insulation
take more of it) and need 1 fails. **(c)'s reach:** with C241 at 3.3 uF the hold is 3.35 to 19.2 s and the coupled limit 557.6 uA (the
pair 510.8 uA, a case of 105 C on the ASSUMED doubling): wider than (b)'s by 36.9 uA, and never past its static 0.597 mA, where (b)'s
static room is 0.846 mA.

### 22d. The states in which U47's RESET sinks, from the draft's netlist (INFERRED from the netlist; TI's limits MAKER)

DD7_N is pulled low by U47's RESET1 and RESET2 alone. While the loop reads powered (Q47, Q48 and Q52 on) the pulls into it are R256
from CELL+ (Q48), R107 with R108 from CELL+ (Q52), R82 with R83 from VBAT (Q47), R254 and R255 from DD7_VC; with the loop unpowered,
only R255 (12.7 uA). **The battery FETs Q39, Q40 and Q42 have their source on VBAT and their drain on CH_BATQ** (the new BODY group
of `check_dd7_netlist.py` reads it; a reversed FET reads FAIL). A P-channel FET's body diode conducts from drain to source, here from
CELL+ towards VBAT, so once the inhibit holds their gates at VBAT nothing on VBAT can lift CELL+: it only bleeds, or is driven by
the pack through the breaker.

| State | CELL+ | RESET at 4.7 kOhm | Against TI |
|---|---|---|---|
| 1. the instant of setting (the FETs were on, a charge passing the off breaker's body diodes into the cells) | at most VBAT, regulated to VSYS's 17.375 V, and within the breaker FETs' VSD of the cells, 17.8 V at most | 3.85 mA, falling with the bleed | under 5 mA |
| 2. the breaker restarted while the hold runs (5.82 s at most) | the pack's 16.8 V at most | 3.72 mA | under 5 mA |
| 3. a charger regulating high | following VBAT up to SYSOVP's 19.5 V (SLUSE65A, the 4S row) | 4.32 mA | under 5 mA |
| (i) **a second condition, a surge:** VBAT at the SMCJ18A's 29.2 V clamp at the very instant of a set, CELL+ lifted 4.71 V over the cells and their body-diode drop while the charge that set it flows; or board P's BRK_VIN at its own 29.2 V clamp with the breaker restarted while a hold runs (the pack pulling CELL+ back at once) | over 22.51 V, 3.01 V over SYSOVP | at most 6.45 mA, over 5 mA for at most 0.155 s of the bleed | under the absolute 10 mA (V1's "transient only") |
| (ii) **two faults:** a battery FET failed short AND VBAT held over 22.51 V, which SYSOVP stops | sustained over 22.51 V | at most 6.45 mA | under the absolute 10 mA |

At 6.45 mA RESET's VOL on the 60 ohm reading is about 0.39 V: the inhibit still holds (Q49's VGS under -9 V).

### 22e. The selection (SESSION) and what it costs

No correction holds need 1 on printed figures alone: the breaker pair's hot leakage has no printed row, so each depends on record
l8p's L8P-F06 (its bench row E-14c; TI's question drafted there, unsent). (a) fails need 1 at the hot bound and at the air. (c) holds
it by 0.396 s with a pair allowance of 451.2 uA, at the cost of a new part, an arm that reaches 0.91 of the way and a hold of up to
12.8 s. (b) holds it by 0.123 s with a pair allowance of 473.9 uA and the larger static room (0.846 mA against 0.597 mA), with no
part beyond round 10's circuit, which the check V1 read in full.

| Decision | Authority | Why no owner judgement stands | Reversed by |
|---|---|---|---|
| **(b): R256 back to 4.7 kOhm.** At the hold as drawn it has the widest allowance for the unprinted leakage, and the higher ceiling if the hold is ever lengthened; (c) buys 36.9 uA more only with a hold of up to 19 s, about 1.1 K of case temperature on an assumed rate, which does not remove the dependence on E-14c; need 2 holds on TI's printed rows in every state without a second fault | SESSION (ruled by the L4-E11 author, 4 October 2026, under the owner's standing rules of 21 and 26 September 2026) | an engineering choice inside the task: no money, no requirement change, no reserved line; (a) fails on its numbers and (c) costs more for no wider allowance | E-14c reading the breaker pair over 473.9 uA at its held case, or E11-45 (f2) reading the bleed outside the unit's own hold. The next lever is then the hold on top of 4.7 kOhm (the static 0.846 mA is its ceiling): a new round, with both checks' arithmetic beside it |

**What it costs:** U47's RESET goes over TI's recommended 5 mA in the named states of 22d (never over the absolute 10 mA), where
6.8 kOhm kept it under 5 mA in every state; and the margin of need 1 is 0.123 s on an ASSUMED leakage.

### 22f. V1's and V2's arithmetic side by side

R256 has moved twice: 4.7 kOhm in round 10, 6.8 kOhm on V1's minor in round 11, 4.7 kOhm now. It does not move again without this
table restated.

| Check | What it read | 4.7 kOhm | 6.8 kOhm |
|---|---|---|---|
| V1 (round 10) | U47's RESET sink with CELL+ at the 29.2 V clamp | 6.39 mA, over TI's recommended 5 mA, "transient only" | 4.47 mA |
| V2 (round 11) | the bleed of CELL+ with the sources into it | ends inside the hold for sources under 520.7 uA; 1.218 s at the hot bound | only under 87.4 uA; 2.189 s at the hot bound, 1.381 s at the air |
| this round | RESET's sink at the most without a second fault | 4.32 mA | 3.02 mA |

### 22g. What stays open, and E11-45 (f) and (h)

- **V2-B1's claim is corrected:** the bleed counts the sources, and the record states one coupled limit (520.7 uA) beside the static
  one (0.846 mA).
- **OPEN:** the latch's timing with the breaker off at the hot bound, on record l8p's **E-14c** (the breaker pair's IDSS hot) and on
  this record's **E11-45 (f2)** (the bleed timed against the unit's own hold, the current into CELL+ read with both FET groups hot, at
  most 521 uA; U47's RESET current read at the set and with the breaker restarted, at most 5 mA) and **(h)** (each hold at least 0.1 s
  longer than (f2)'s bleed on the same unit). CELL_FUSED's 104 uF at +20 % is an ASSUMPTION.
- **Between 520.7 uA and 0.846 mA** (not reached at the hot bound): the hold may end with CELL+ still read alive and the breaker off;
  the inhibit releases, and a charge over board P's threshold (0.368 to 1.213 A) sets it again within 1.41 ms, once a hold; under
  the threshold it is the named residual of 20l (the latched FET at most 139.9 C, record l8p). That repeated cycle is not analysed
  further.
- **For record l8p (L8P-F06 and E-14c; nothing of its is edited here):** the latch's budget is two limits, the static 0.846 mA
  (round 10's again, so its 12j figures stand for the static room) and the timing 520.7 uA, which the pair alone fills from a
  103.9 C case, 2.9 K over its held case. E-14c's acceptance (the pair at most 388 uA at 101 C) keeps the timing with 85.9 uA in
  hand. Its copies of 20c to 20e and of this record's drafts are round 10's and are taken again at this round (the check V2's V2-B2,
  its owner's).

### 22h. The minors (V2-m1 to m5 and m9, this record's part)

- **V2-m1:** 21b (ii) takes Vishay's printed maxima for the SQJ403EP (4.5 nF) and the SQJ407EP (10.7 nF) and prints the typical
  figures beside them; the verdict is unchanged.
- **V2-m2:** Nexperia's hot IDSS row (10 uA at Tj 125 C) is quoted in 20e and 22b where the record said "not printed".
- **V2-m3:** the dd7 draft's comment carries 22c's figures (3.85 mA at the set, 4.32 mA with CELL+ at SYSOVP, 6.45 mA only at the clamp).
- **V2-m4, V1's two minors that no record carried:**
  1. *The TPS37's hysteresis accuracy (+-1.5 %) read as percentage points, not relative.* The return reads held under 0.7642 V (board
     P holds 0.055 V), the loop reads powered over 2.008 V at most (8 mV over the interface's 2.0 V; the held loop reads 0.536 V over
     it at 7.6 V), the window's bound is 25.1 kOhm: every margin still holds (V1's figures, reproduced by the script).
     **Owner:** this record. **Next action:** Q-TI-19 (`clarification/TI-QUESTIONS.md`, drafted, NOT SENT) and E11-45 (e), which reads
     U48's thresholds on the unit; the interface's 2.0 V is record l8p's to restate if TI answers "percentage points".
  2. *The CONOPS wording of the named residual.* Drafted sentence, for the CONOPS owner: "If the pack's breaker latches while a
     source carries the kit and no charge over 0.368 to 1.213 A flows, the pack stays isolated: the kit runs on the source alone, and
     the pack returns only on a redocking or when an input returns to a dark kit." **Owner:** the CONOPS owner with record l9stk (the
     battery stream), as V1 named them. **Next action:** L4-E9's next round takes the sentence as a register row; a controlled
     amendment of an accepted Layer 2 page is the coordinator's.
- **V2-m5:** E11-29's coupon also reads the PTC's site (RT1) against each junction with one FET heated alone at the worst split's
  1.513 W (the row in section 8 and block E11-29 in 17d), so the guard's trip side is judged on the hottest FET.
- **V2-m9:** the tests compose board A in main's order, with record l8r2's d8v3 and vbus20ov. The candidate's change list (L4-E9
  rows 24 to 33) names l8r2's packrtn, slotlm and fb01 instead; those three drafts are **not in this branch's tree** (`fnd/l8r3` at
  `89924e40`), so the tests keep the order this tree can show. **The list's order, shown where its drafts are:** on a scratch copy of
  the candidate's files (`fnd/v2cand` at `dfa1eef2`) with this round's drafts laid over them, `compose_in_list_order.py` composed the
  list's order (16 drafts, each exit 0), the generator ran to its end (778 parts, intent written), `check_dd7_netlist.py` read DRAWN
  and three mutations read FAIL (a scratch run of 4 October 2026). `test_l4e11` runs that script: in this tree it reports the missing
  drafts; once they are in the tree (the candidate's line) it requires the list's order to compose and read DRAWN.

### 22i. Status of round 12

| Item | Status |
|---|---|
| V2-B1 | **answered by correction (b)**, R256 4.7 kOhm; the claim corrected (22a, 20e) |
| need 1 (the bleed at the hot bound inside the hold) | **CONDITIONAL**, 0.123 s on record l8p's ASSUMED leakage; **OPEN** until E-14c or E11-45 (f2) reads |
| need 2 (U47's RESET within TI's recommended 5 mA) | holds on TI's printed rows in every state without a second fault; the two other states named (22d) |
| R84 | stays specified pulse-rated (CONDITIONAL, Layer 6) |
| closure credit | (a) board A composes in main's order in this tree and, on a scratch copy of the candidate's files, in L4-E9's change-list order (22h), the generator running to its end both ways; (b) the netlist reads DRAWN at 4.7 kOhm, eight mutations FAIL (R256 at 6.8k and a reversed battery FET among them); (c) 22c on C-PROT rev 1, the round refusing a bleed that counts no source |
| V2-m1 to m5, m9 | carried (22h) |

Not claimed: nothing here is verified, built or measured; software tests establish this record's own behaviour only. This round is the
author's answer to V2's first negative check of the 6.8 kOhm value; its targeted recheck is owed.
