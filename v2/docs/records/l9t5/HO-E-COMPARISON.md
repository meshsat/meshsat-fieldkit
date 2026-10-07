**HO-E COMPARISON (Layer 4 task L4A-59, 7 October 2026; W140, branch `fnd/l4hoe` from `06d064ff`; corrected by W145 the same day on the focused check L4A-100, W144's findings F1 to F11): DONE: three approaches compared on the makers' pages (H-1 DROPS OUT: RM0433 Rev 8, DS12110 Rev 11 and AN4938 Rev 7 show the voltage scale chosen by software, no strap and no option byte, PWR_CR3's POR-only lock recorded; H-3 NOT ESTABLISHED ON PRINTED FIGURES: no package and no printed heat path reaches the 15.57 C/W VOS0 needs at 76.25 C air at one supply corner; H-2 STANDS as the one design, PROVISIONAL: a drafted VCORE monitor per supervisor that resets the controller on any VOS1 or VOS0 entry whatever its firmware does, now with a CTR1 reset hold for an image that loops through VOS0 at every boot); the selection SESSION W140-1 and W145's decisions W145-1 to W145-5 with their authority fields; the draft `apply_gen_sch_b_vcoremon.py` (18 parts) composed on board B (also with W137's canmb and W138's regstage, either order), read by pin, seven mutations FAIL (the last the hold capacitor removed), refusals; the firmware row FW-B23 drafted (`apply_hw_fw_contract_hoe.py`); the register rows (`HO-E-REGISTER-ROWS.md`); the test module `test_l9t5_hoe.py`. NOT DONE: the targeted recheck of L4A-100; nothing applied; nothing physical (S1 to S5); the fixed-delay stage that would remove S5 is named, not drafted. NEXT: the coordinator's reading and the targeted recheck of C1 to C3.**

# HO-E: the supervisor's STM32H743 past its own 105 C VOS0 limit, compared and selected

Record l9t5, Layer 4 task L4A-59 of the AI-scope register (`_runs/l4ai/REGISTER.draft.md`, draft 2, rows L4A-59 and L4A-100, written on
W127's check 1a and finding 2). Prototype design: nothing in this kit has been built, bought, powered or measured, and no figure here is
a measurement. Every figure is printed by `l9t5_hoe.py` into `l9t5_hoe.out` ("OUT n" below is its section). Labels: PRINTED (a maker's
limit or tested row), TYPICAL, DIAGRAM (read from a maker's drawn figure), DECLARED, DRAFTED (not applied), MODEL, ASSUMPTION, SESSION.
This task closes no cx46 item: cx46 CORRECTIONS NOT CLOSED and Layer 4's DESK gate NOT PASSED stand. The focused check (W144,
`_runs/claude/w144chkhoe/REPORT-FULL-AS-RECEIVED.md`) read W140's page as SUPPORTED AS CONDITIONAL with conditions C1 to C5; section 9
lists each finding and its correction here. Every thermal limit below is at ONE supply corner, the rail's top 3.3577 V (SESSION W145-4,
W144's F8): W140 mixed T10's 3.3 V state with a rail-top step.

## 1. The failed case, and what the protection now admits (OUT 2)

- T10 10j (c) and (e): "VOS0 under the trip takes the controller past its own 105 C VOS0 limit from 0.1936 A" and "(112.7 C at
  0.2452 A)"; cx46 finding 17: "the MCU reaches its 105 C VOS0 PRINTED LIMIT at approximately 0.1936 A, MODEL". Reproduced from T10's
  own 76.25 C air and LQFP100's 45.0 C/W (DS12110 Rev 11 Table 222, p.344).
- The 105 C is ST's: Table 112 note 5, p.210, "5. TJMax = 105 °C." on the VOS0 rows; Table 113, p.210, VOS0 Max TJ 105 C, VOS1 to VOS3
  125 C.
- W138 (record l4reg, `fnd/l4reg` 86dbcdff, filed in `inputs/`) selected a TPS2553-1 with IOS 0.4702 to 0.5704 A ahead of a
  TPS73733DCQRM3 (76.0 C/W) and removed round 6's rail trip; its L4REG-F7 hands the controller's protection to this task.
- On the printed maxima (Table 119, p.215, revision V) no VOS0 row has an operating point inside 105 C at this air. The largest printed
  VOS0 current at 105 C is Table 119's 550 mA (Table 120 prints 546, Table 121 504; p.216), inside the limiter's band. So HO-E is not a
  current limit's problem: VOS0 must be kept out, or ended before the junction moves.

## 2. The three approaches

| | What it is | Basis | Result | Verdict |
|---|---|---|---|---|
| H-1 | a hardware-forced voltage scale | RM0433 Rev 8 p.264, p.279, p.280, p.306, p.307, p.309, p.560, p.260, p.262, p.215 to 216, p.256 (Table 32); DS12110 Rev 11 p.29, p.210; AN4938 Rev 7 p.10, p.19 (PRINTED, quoted in OUT 3) | the scale is written by software after every reset (PWR_D3CR's VOS bits, then SYSCFG_PWRCR's ODEN for VOS0); no option-byte field and no PWR pin selects a scale; the one hardware means printed, the Bypass supply ("Scale 0 ... available only with LDO regulator"), is configured by software once after every POR. PWR_CR3 "is reset only by POR. It is not reset by wakeup from Standby mode and by the RESET pad." (p.306) and is written once (p.307): after its first write no later fault can change the supply configuration before the next POR, but the first write is made by whatever image runs first (W144's F9) | **DROPS OUT**. No hardware bar is claimed |
| H-3 | a thermal-headroom part or heat path | Table 119 p.215 and Table 222 p.344 to 345 (PRINTED) | VOS0 needs at most 15.84 C/W at 3.3 V, 15.57 C/W at the rail's top; the least ThetaJA is the TFBGA240+25's 36.6 C/W, the LQFP100's 45.0 C/W; every ThetaJB is over the need; a case-top path leaves 4.07 C/W after the LQFP100's ThetaJC, 8.17 C/W after the TFBGA240+25's (W144's 4.34 and 8.44 C/W on the 3.3 V figure), and a path to the case wall is a third form; no held document prints a heat sink, an interface, a strap or a wall path for these parts | **NOT ESTABLISHED ON PRINTED FIGURES** (W144's F10: not impossible, not established, not selected) |
| H-2 | a firmware bound with an independent ending | FW-B20 (DRAFTED, T10); RM0433 p.1896 (IWDG), pp.329 to 332 (resets); W137's vote; TI TPS37 SNVSBJ1E pp.5 to 23; DS12110 Tables 112, 116, 119 to 121, 147, 152 | the firmware bound alone ends nothing; the IWDG ends hangs, not a running firmware; the peers act on SHDN, not on VOS0; a VCORE monitor (drafted) resets the controller on any VOS1 or VOS0 entry on printed thresholds, and its CTR1 capacitor holds the reset after | **NOT SUPPORTED ON PRINTED FIGURES AS A PROOF** (S1, S2 and S5 unprinted); **STANDS, PROVISIONAL** under amendment 1 |

## 3. H-2 in detail: the drafted VCORE monitor (OUT 5)

**What it reads.** Each controller's core voltage is on its VCAP pins (48 and 73). ST prints it per scale with the LDO on (DS12110 Rev
11 Table 112, p.209): VOS3 0.95 to 1.05 V, VOS2 1.05 to 1.15 V, VOS1 1.15 to 1.26 V, VOS0 1.26 to 1.40 V. Those rows sit on the pages
headed "Electrical characteristics (rev V)"; rev Y's Table 14 (p.105) prints no core voltage per scale, and no held page prints rev X's:
the trip window rests on revision V, which L9T5-D7 fits (W144's F4, condition C3; S3 extended for a rev X part).

**The circuit (DRAFTED, `apply_gen_sch_b_vcoremon.py`, NOT APPLIED).** Per supervisor: a TI TPS37 in WSON-10, channel 1 overvoltage
with the adjustable 800 mV option "01" (SNVSBJ1E Table 11-1, p.34), open-drain active-low RESET1; VDD on the controller's own 3.3 V with
100 nF (Table 6-1, p.5); SENSE1 from VCAP through 39.2 kOhm over 100 kOhm, both 0.1 % and 25 ppm/K; SENSE2 on the rail; RESET1 through
750 Ohm 1 % to the controller's NRST (pin 14); **CTR1/MR to GND through 100 nF (C813, C814, C815; SESSION W145-1, W144's F1)**.
Designators U810, U820, U830, R810 to R832, C810 to C815: 18 parts, none of a controller's pins added.

**The band.** Trip 1.0969 to 1.1303 V, release from 1.0746 V (MODEL on TI's VITP, ISENSE and hysteresis rows): every VCAP in VOS3's
band leaves it released, every VCAP in VOS1's or VOS0's band trips it. VOS2's band straddles the trip (S-f).

**The ending.** A trip holds NRST; the reset puts the controller back in its reset state: RM0433 p.263 "When a system reset occurs, the
voltage regulator is enabled and supplies VCORE."; PWR_D3CR's reset value is Scale 3 (p.309), SYSCFG_PWRCR's ODEN 0 (p.560). Which
resets restore them is PRINTED (W144's F5, replacing W140's "the manual does not name"): "A system reset (nreset) resets all registers
to their reset values unless otherwise specified in the register description.", with "A reset from NRST pin (external reset)" among
its sources (8.4.2, p.329); Table 55's NRST row (p.330): "Resets VDD domain: IWDG1, LDO..."; neither register's description names an
exception, where PWR_CR3's does (p.306). S2's ACTVOS reading confirms a printed fact on the specimen.

**Its timing.** TPS37 sense delay 17 us at most, printed only at "20% Overdrive from VIT" and 1 V/us (7.6, p.9): VOS0's bottom is 11.5 %
over the trip's top, VOS1's 1.7 %, so the printed maximum does NOT cover these entries (S2, now on the real VCAP ramp, W144's F11). NRST
falls to 0.3 VDD within 157.4 us at the slowest corner (MODEL). t_resp = 174.7 us, CONDITIONAL on S2.

**The reset hold (W144's F1).** With CTR1 open the hold after a trip is tCTR(no cap), at most 40 us and no minimum printed, so an image
that enters VOS1 or VOS0 at every boot loops through resets with no printed bound on its duty. With 100 nF (read at +-20 %, ASSUMPTION,
as the record reads the reset capacitor) TI's Equation 2 (8.3.4.1, p.23) on RCTR's 877 kOhm minimum (7.5, p.8) gives tCTR(min) 82.2 ms,
Equation 3 gives at most 190.8 ms. **TI's own condition**, the same page: "When a voltage fault occurs, the previously charged up
capacitor discharges and if the monitored voltage returns from the fault condition before the delay capacitor discharges completely,
the delay will be shorter than expected." and "To ensure the capacitor is fully discharged, the time period or duration of the voltage
fault needs to be greater than 5% of the programmed reset time delay.": at most 9.54 ms. A loop's fault lasts at least NRST's fastest
fall, 78.1 us (MODEL), plus VCAP's fall after the reset, which no held document prints. So the 82.2 ms is a hold only if that fall
outlasts 9.54 ms: S5 (W145-F1). The hold costs up to 190.8 ms of reset at each self-test and at power-up (TI p.9 note 4: "Capaicitor in
CCTR1 or CCTR2 will add time to tSD.", TI's spelling).

**The reset loop (OUT 5g).** After a full discharge: duty at most 0.212 %, the average rise at most 0.125 K (MODEL), and S1's limit
becomes 3.55 K/W. Those figures are CONDITIONAL on S5; the state S-k never reads HOLDS. The route that removes S5 is a delay that does
not depend on the fault's length, for example board B's own TPS3808G30 with CT to VDD (TI SBVS050N 6.6, p.7: td 180 / 300 / 420 ms;
7.3.3, p.11: "After MR returns to a logic high and SENSE is above its reset threshold, RESET is de-asserted after the user-defined reset
delay expires."), RESET1 on its MR and its RESET on NRST; drawn naively it latches through NRST and the 750 Ohm back to MR, so RESET1
must drive MR alone or through a diode. It is named, not drafted (SESSION W145-5).

**Power-up.** The TPS37's outputs are "in reset, regardless of the voltage at SENSE pins" between VPOR and UVLO (8.3.1.1, p.18); the
first release is at tSD + tCTR (Figure 7-3, p.12, DIAGRAM): 82.2 to 192.8 ms after VDD reaches 2.7 V (S4).

**Its own faults and the self-test (SESSION W140-3 as restated by W145-2 and W145-3; the firmware row FW-B23, drafted).** At every start
and once an hour, one supervisor at a time: clear the flags (RMVF, RM0433 8.4.4 p.332), keep a marker where NRST does not reach (Table
55, p.330: "Debug features, Flash memory, RTC and backup RAM are not reset"), write Scale 1 at HCLK at most 144 MHz and wait t_resp
(174.7 us) from that write (W144's F11: the window times the regulator's ramp, the monitor and NRST's fall on every unit in service,
and finds a slowed monitor); still running, write Scale 3 within 10 us and report MONITOR FAILED. PASSED needs the marker and RCC_RSR
equal to Table 56's row 2 (p.332): PINRSTF and CPURSTF set, LPWRRSTF, WWDG1RSTF, IWDG1RSTF, SFTRSTF, PORRSTF, BORRSTF, D2RSTF and D1RSTF
clear (W144's F3: Table 56 sets PINRSTF on a power-on, brownout, software, window watchdog, independent watchdog and low-power reset
too). Faults (OUT 5e): an open divider, a stuck output, an unpowered TPS37, a swapped sense pin and a slowed monitor are found by the
next test or at once; a shorted hold capacitor holds the reset (at once); an **open hold capacitor is not found by the test** (it times
no hold): S5 and inspection, the residual S-l. A healthy unit whose ramp makes the interval from the write longer than t_resp reads
MONITOR FAILED: found at the first article by S2, then the window and S1 are re-read together.

**The controller's thermal time: NOT PRINTED (OUT 5f).** At the rail's top the bounded state is 100.20 C at 0.1585 A (T10's own model,
which gives T10's 99.6 C and 0.1570 A at 3.3 V); VOS0's 550 mA adds 1.3144 W, so inside 105 C the junction-to-ambient transient
impedance at t_resp must be at most 3.65 K/W (W140's 4.09 K/W mixed the two corners; W144 read about 3.63 K/W). VOS1's largest printed
125 C current is Table 120's 544 mA (W144's F7): at most 19.16 K/W at t_resp and at 184.7 us for a dead-monitor self-test (W140 read
19.96 K/W; W144's F7 19.55 K/W at W140's corners). **U-02's local air (W144's F2):** the bounded state itself reaches 105 C at 79.32 C
local air at the rail's top (MODEL; W144's linear 79.5 C): at or over that air no ending of any speed keeps a VOS0 entry inside 105 C.

## 4. The acceptance, state by state (OUT 6)

"The controller inside 105 C in every served state and every state the protection admits" (105 C VOS0's limit; 125 C VOS1 to VOS3's).

| State | Criterion | Figure (one supply corner) | Verdict |
|---|---|---|---|
| S-a the bounded served state (FW-B20, FW-B21, rev V) | 105 C | 100.20 C | HOLDS (MODEL on PRINTED) |
| S-b VOS3 at its printed 200 MHz with every peripheral | 125 C | 121.32 C | HOLDS (MODEL on PRINTED) |
| S-c a VOS0 entry by any firmware | 105 C | ended within 174.7 us; needs ZthJA at most 3.65 K/W | CONDITIONAL (S1, S2; C2, C3) |
| S-d a VOS1 entry, the self-test included | 125 C | ended within t_resp; needs at most 19.16 K/W | CONDITIONAL (S1, S2) |
| S-e the self-test with a dead monitor | 125 C | at most 184.7 us; needs at most 19.16 K/W | CONDITIONAL (S1) |
| S-f VOS2 with VCAP under the trip's top | 125 C | not surely ended by the monitor | OPEN (row R-1) |
| S-g VOS3 above its printed 200 MHz | 125 C | no printed current | OPEN (row R-2) |
| S-h power-up before the monitor is valid | 105 C | held under UVLO; released at tSD + tCTR (DIAGRAM) | CONDITIONAL (S4) |
| S-i a latent monitor fault, then a VOS0 entry | 105 C | a double fault; window at most 3600 s | RESIDUAL (single-fault) |
| S-k the reset loop (an image entering VOS1 or VOS0 at every boot) | 105 C | duty at most 0.212 %, rise at most 0.125 K; needs at most 3.55 K/W | CONDITIONAL (S5, S1, S2) |
| S-l an open hold capacitor, then the reset loop | 105 C | a double fault the self-test does not see | RESIDUAL (single-fault) |
| S-j any current up to the limiter's 0.5704 A | as above | every such state is one of S-a to S-l | none outside them |

**HO-E's acceptance: CONDITIONAL.** The served state holds 105 C; every VOS0 state the protection admits is ended by the drafted
monitor; whether the junction stays inside 105 C during the ending rests on S1 and S2, in a reset loop also on S5, and on C2 and C3.
Not claimed: a hardware bar from any document, a printed interval, a printed bound on the reset loop, or a closure.

**The focused check's conditions, restated:**

- **C1 (F1):** the CTR1 hold drafted, composed, read and mutated, with the reset-loop row: DONE in this round (OUT 5d, 5g, 8). The
  row's bound is CONDITIONAL on S5 (W145-F1); a fixed-delay stage would remove S5 and is named, not drafted.
- **C2 (F2):** U-02's local air at the supervisors at or under 79.32 C (MODEL at the rail's top; W144's linear 79.5 C).
- **C3 (F4):** revision V fitted (L9T5-D7), or a rev X part with its VCAP per scale confirmed first (S3).
- **C4 (F8, F11):** S1 at one supply corner (at most 3.65 K/W at t_resp, 3.55 K/W less the loop's rise with S5); S2 on the real VCAP
  ramp with the self-test's window timed from the Scale 1 write; S3 and S4 as written; S5 new.
- **C5 (F3, F6):** the register rows R-1 (S-f), R-2 (S-g) and R-3 (FW-B23) in `HO-E-REGISTER-ROWS.md`.

## 5. The selection

**SESSION W140-1: H-2 with the drafted VCORE monitor (`apply_gen_sch_b_vcoremon.py`) and the self-test row FW-B23, PROVISIONAL on S1
to S5.**

- **authority:** SESSION, under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026.
- **authority_why:** an engineering selection inside the drafted circuit; no requirement, protected class, case row, purchase or
  publication changes; one approach stands after the reading (H-1 drops out on the documents, H-3 is not established on printed
  figures), so the ruling's second half (more than one option standing) fails; the residuals are measurable on a specimen (S1 to S5):
  amendment 1's supplier tasks, not a risk no measurement can remove.
- **ruled_by:** W140 (Claude), MESHSAT-1357. **ruled_on:** 7 October 2026. **reversed_by:** none.
- **To reverse:** drop `apply_gen_sch_b_vcoremon.py`; HO-E returns to REMAINING ENGINEERING with the owner item below.
- **End condition:** S1 reads the controller's ZthJA at t_resp over 3.65 K/W on board B (3.55 K/W less the loop's rise); or S2 reads a
  sense delay long enough that S1 fails at the longer interval; or S5 fails and the fixed-delay stage is not taken; or two negative
  independent checks of this selection.
- **The owner item, PREPARED AND NOT RAISED** (raised only if the end condition is met): "The I/O supervisors' STM32H743 cannot hold its
  105 C VOS0 limit in the case's air, and no hardware means bars VOS0. Either accept that the 105 C limit during a firmware fault rests
  on the controller's measured transient thermal response, or change the supervisor part to one whose printed rows hold at this air,
  or give it a heat sink and a path to the case (a part or mechanical change and its cost)." (W144's F10 adds the heat path.)

| Id | Decision | Why | To reverse |
|---|---|---|---|
| W140-2 | the divider 39.2 kOhm over 100 kOhm, 0.1 % and 25 ppm/K | the E96 top with the largest least margin (19.7 mV) | another top with the table re-read |
| W140-3 | the self-test at start and every 3600 s, one supervisor at a time, the peers flag a stalled counter (as restated by W145-2, W145-3) | the whole real path exercised; the latent window bounded | a longer interval |
| W140-4 | 750 Ohm in series from RESET1 to NRST | the open drain under the recommended 5 mA (4.52 mA) | a smaller reset capacitor |
| W140-5 | the monitor acts on NRST, not on the regulator's EN | a reset returns the scale within the interval | the output on W138's limiter EN through a diode |
| W140-6 | a decoupling class entry "TPS37 " (class D) | the generator's class table needs one | none needed if the part changes |
| W140-7 | the WSON-10 land id | the DSK package; KiCad's land check runs only where KiCad is | the 14-pin DYY package |
| W145-1 | the reset hold: 100 nF from CTR1/MR to GND per monitor, read at +-20 % | W144's F1 value: Equation 2's 82.2 ms keeps the loop's duty at 0.212 %; it costs at most 190.8 ms of reset at power-up and per test | another value with OUT 5g re-read |
| W145-2 | the self-test's window: t_resp from the Scale 1 write, then Scale 3 within 10 us | W144's F11: the ending timed on every unit in service, a slowed monitor found; the dead-monitor dwell bounded at 184.7 us | a window read from S2's measured ramp, S1 re-read |
| W145-3 | PASSED: the marker and RCC_RSR equal to Table 56's row 2 | W144's F3: six other rows set PINRSTF too | none needed |
| W145-4 | every thermal limit at one supply corner, 3.3577 V | W144's F8 | a narrower rail band issued as a case row |
| W145-5 | the reset loop's bound left CONDITIONAL on S5; the fixed-delay stage named, not drafted | the brief fixes the CTR1 hold; the stage needs a second part per supervisor, a latch-breaking element and its own check | draft the stage (W145-F1) |

Each W145 decision: authority SESSION under the same rules; authority_why an engineering value or method inside the drafted circuit and
its rows, no requirement, class, case row, purchase or publication changed, one option standing after the focused check's reading;
ruled_by W145 (Claude), MESHSAT-1357; ruled_on 7 October 2026; reversed_by none.

## 6. The draft (OUT 8)

Composed in L4-E9's change-list order after iocguard (R-245), before the efuse record's R-236 and R-237 and Layer 6's three: 19 steps,
every one OK, the generator run to its end through record l8p's `gen_netlist.py`; 1533 parts and 1096 nets against 1515 and 1087;
added 18, removed 0, no existing part changed. Read by pin (now also CTR1 on a node carrying only its hold capacitor, whose value is
at least the draft's): DRAWN (before the draft: FAIL). With W137's canmb and W138's regstage, this draft after and before them: DRAWN,
the two netlists identical; no designator shared. Seven mutations FAIL: the output on a peer's NRST, the divider's top from the rail, top
and bottom exchanged, SENSE1 and SENSE2 exchanged, the monitor on a peer's rail, RESET1 and ground exchanged, and the hold capacitor
removed (C813 not fitted). It applies to the tree's generator as it stands (order-free), refuses a second application and refuses the
tree's own generator (NOT RELEASED: RELEASE-T10.md). CON-004's failure domains kept.

The firmware row (`apply_hw_fw_contract_hoe.py`, FW-B23 and V-B24): on a scratch copy of the tree's contract it is refused alone (T10's
rows absent), applies after `apply_hw_fw_contract_t10.py`, refuses a second application, and leaves the tree's contract unchanged.

## 7. The four acceptance states (constitution section 2)

| Deliverable | Document acceptance | Supported design | Implementation | Physical qualification |
|---|---|---|---|---|
| the comparison | this page, its authors and W144's focused check (SUPPORTED AS CONDITIONAL) | H-1 and H-3 on quoted pages; H-2 PROVISIONAL | none | none |
| the monitor with its hold (`apply_gen_sch_b_vcoremon.py`) | this page | composed, read by pin, seven mutations FAIL; band on printed rows; interval CONDITIONAL (S1, S2); loop CONDITIONAL (S5) | NOT APPLIED (release-guarded) | S1 to S5 |
| the self-test row FW-B23 (`apply_hw_fw_contract_hoe.py`) | this page | window and PASSED pattern on printed pages | no firmware exists | S2 and S5 on the first article |

## 8. The supplier's tasks (OUT 9)

- **S1:** the controller's junction-to-ambient transient impedance on board B, three first-article supervisors at the rail's top, a
  step at 1.3144 W: pass at most 3.65 K/W at 174.7 us (3.55 K/W if the reset loop's 0.125 K is carried, S5), and at most 19.16 K/W at
  the VOS1 step at 174.7 us and 184.7 us (or ST's transient thermal data with board B's copper).
- **S2:** the monitor's interval on the real VCAP ramp: VCAP driven by the controller's own Scale 1 write and VOS0 entry, three
  supervisors, at 76 C and at -40 C: pass, from the Scale 1 write and from VCAP crossing the trip to NRST under VIL, at most 174.7 us;
  PWR_CSR1's ACTVOS reading Scale 3 at the restart.
- **S3:** VCAP in VOS3 with the divider fitted under load steps: inside 0.95 to 1.05 V and under the trip's least 1.0969 V; a rev X
  part's VCAP in VOS3, VOS1 and VOS0 read on three parts against Table 112's revision V rows before it is accepted.
- **S4:** NRST held low from VPOR through tSD + tCTR at power-up, released 82.2 to 192.8 ms after VDD reaches 2.7 V; ten power cycles
  each supervisor.
- **S5 (new):** the reset loop's hold: three first-article supervisors in a 76 C chamber at the rail's top, an image that enters VOS0
  at every boot: NRST's low time per cycle over 100 cycles and VCAP's fall from VOS0 to the release level after an NRST reset; pass,
  every hold at least 82.2 ms (or VCAP's fall at least 9.54 ms); or TI's discharge figure for a fault shorter than 5 % of the delay
  (correspondence drafted, UNSENT).

## 9. W144's findings and their corrections

| Finding | Class | Correction here |
|---|---|---|
| F1 the reset loop | blocks | CTR1 hold 100 nF drafted (C813 to C815), composed alone and with canmb and regstage in both orders, read by pin, the removal mutation FAILS; the loop row OUT 5g: duty 0.212 %, rise 0.125 K on Equation 2 after a full discharge; TI's full-discharge condition is NOT shown for a loop (78.1 us against 9.54 ms): CONDITIONAL on S5 (W145-F1) |
| F2 U-02's local air | should fix | condition C2: at or under 79.32 C at the rail's top (OUT 5f) |
| F3 the PASSED pattern | should fix | Table 56's row 2 read from p.332 into OUT 5e; FW-B23 drafted; row R-3 |
| F4 rev V's rows | should fix | condition C3 and S3 extended; rev Y's Table 14 (p.105) read |
| F5 the reset state | should fix | p.329 and Table 55 p.330 quoted; "the manual does not name" withdrawn |
| F6 S-f and S-g | should fix | rows R-1 and R-2 |
| F7 Table 120's 544 mA | note | VOS1's step from the largest of Tables 119 to 121 (19.55 K/W at W140's corners; 19.16 K/W at one corner) |
| F8 one supply corner | should fix | SESSION W145-4: 3.65 K/W (W144 about 3.63 K/W), H-3's need 15.57 C/W |
| F9 PWR_CR3's lock | note | p.306 quoted in H-1 |
| F10 H-3 not impossible | note | verdict NOT ESTABLISHED; the TFBGA240+25 top path and the case-wall path named |
| F11 S2 on the real ramp, the window from the write | note | S2 restated; SESSION W145-2 |

Findings for other authors (OUT 9): W140-F1 to F6 as before (F1 now names FW-B23, F4 the rows R-1 and R-2); **W145-F1** (the targeted
recheck, C1): the CTR1 hold's full-discharge condition and the fixed-delay route; **W145-F2** (Layer 6): the hold capacitor's part must
stay inside +-20 % over its tolerance, temperature and bias; **W145-F3** (L4A-61): FW-B23 and V-B24 after T10's rows; **W145-F4** (the
coordinator): the register rows; **W145-F5** (IOHA, Layer 5): the hold delays the supervisors' start by 82.2 to 192.8 ms and holds the
supervisor under test up to 190.8 ms each hour, inside IOHA row 3.

## 10. What this does not do, and reproduce

It runs no independent check and applies nothing. It does not print the controller's transient thermal impedance, the TPS37's delay
under 20 % overdrive or its CTR discharge after a short fault (no document prints them), bound VOS2 under the trip or VOS3 above
200 MHz (rows R-1 and R-2), or restate the register and the ledger (the coordinator's).

```
python3 v2/docs/records/l9t5/l9t5_hoe.py                    # prints l9t5_hoe.out (a few seconds)
env -C v2/ecad/tools python3 tests/run.py test_l9t5_hoe
```

The constitution was read and is acknowledged (sections 3 to 6 and 8): at most three materially different approaches, each basis
printed or labelled, the selection within authority, every limit a printed one, the failing mutations exercise the failure cases, and
no verdict is upgraded.
