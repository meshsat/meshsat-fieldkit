**HO-E COMPARISON (Layer 4 task L4A-59, 7 October 2026; W140, branch `fnd/l4hoe` from `06d064ff`; corrected by W145 the same day on the focused check L4A-100, W144's findings F1 to F11; its reset-loop hold made indifferent to S5 by W148 the same day, W145's finding W145-F1): DONE: three approaches compared on the makers' pages (H-1 DROPS OUT: RM0433 Rev 8, DS12110 Rev 11 and AN4938 Rev 7 show the voltage scale chosen by software, no strap and no option byte, PWR_CR3's POR-only lock recorded; H-3 NOT ESTABLISHED ON PRINTED FIGURES: no package and no printed heat path reaches the 15.57 C/W VOS0 needs at 76.25 C air at one supply corner; H-2 STANDS as the one design, PROVISIONAL: a drafted VCORE monitor per supervisor that resets the controller on any VOS1 or VOS0 entry whatever its firmware does); the reset loop's hold compared (section 11: HS-1 a hold stage after the TPS37, read with TI's TPS3808 and TPS3703; HS-2 one window supervisor on VCAP; HS-3 no retry) and SESSION W148-1 taken (a TPS3703F6050 hold stage per monitor, its printed 14 ms minimum for any manual-reset pulse of 1 us, so the loop's duty is bounded on printed figures for any fault length and S5 is retired); the selection SESSION W140-1, W145's decisions and W148's W148-1 to W148-3 with their authority fields; the draft `apply_gen_sch_b_vcoremon.py` (24 parts) composed on board B (also with W137's canmb and W138's regstage, either order), read by pin, nine mutations FAIL (W140's six, the hold removed, the hold stage bypassed, a hold under its printed minimum), refusals; the firmware row FW-B23 restated (`apply_hw_fw_contract_hoe.py`: the 122.6 us window and the hold's timing); the register rows (`HO-E-REGISTER-ROWS.md`); the test module `test_l9t5_hoe.py`. NOT DONE: the targeted recheck of L4A-100 (W144's C1 to C3); nothing applied; nothing physical (S1 to S4). NEXT: the coordinator's reading and the targeted recheck.**

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
| H-2 | a firmware bound with an independent ending | FW-B20 (DRAFTED, T10); RM0433 p.1896 (IWDG), pp.329 to 332 (resets); W137's vote; TI TPS37 SNVSBJ1E pp.5 to 23; TI TPS3703 SBVS249B pp.3 to 20; DS12110 Tables 112, 116, 119 to 121, 147, 152 | the firmware bound alone ends nothing; the IWDG ends hangs, not a running firmware; the peers act on SHDN, not on VOS0; a VCORE monitor (drafted) resets the controller on any VOS1 or VOS0 entry on printed thresholds, and its hold stage (W148-1) holds the reset after for a printed minimum | **NOT SUPPORTED ON PRINTED FIGURES AS A PROOF** (S1 and S2 unprinted; S5 retired by W148-1); **STANDS, PROVISIONAL** under amendment 1 |

## 3. H-2 in detail: the drafted VCORE monitor (OUT 5)

**What it reads.** Each controller's core voltage is on its VCAP pins (48 and 73). ST prints it per scale with the LDO on (DS12110 Rev
11 Table 112, p.209): VOS3 0.95 to 1.05 V, VOS2 1.05 to 1.15 V, VOS1 1.15 to 1.26 V, VOS0 1.26 to 1.40 V. Those rows sit on the pages
headed "Electrical characteristics (rev V)"; rev Y's Table 14 (p.105) prints no core voltage per scale, and no held page prints rev X's:
the trip window rests on revision V, which L9T5-D7 fits (W144's F4, condition C3; S3 extended for a rev X part).

**The circuit (DRAFTED, `apply_gen_sch_b_vcoremon.py`, NOT APPLIED).** Per supervisor: a TI TPS37 in WSON-10, channel 1 overvoltage
with the adjustable 800 mV option "01" (SNVSBJ1E Table 11-1, p.34), open-drain active-low RESET1; VDD on the controller's own 3.3 V with
100 nF (Table 6-1, p.5); SENSE1 from VCAP through 39.2 kOhm over 100 kOhm, both 0.1 % and 25 ppm/K; SENSE2 on the rail; CTR1/MR open
again (W145's capacitor withdrawn). **RESET1 drives only the manual reset of a hold stage (SESSION W148-1, section 11):** a TI
TPS3703F6050DSER (SBVS249B, held back, `l9t5hoe/fetch_held_back.py`; WSON-6, 1.50 x 1.50 mm; UV only, its SENSE on its own VDD, "Connect to VDD
pin if monitoring VDD supply voltage.", p.4), CT pulled to its VDD through 10 kOhm 1 % (7.3 note 1, 9.1.2.1: the factory-programmed
delay), 100 nF at its VDD, its open-drain RESET through 390 Ohm 1 % to the controller's NRST (pin 14). Designators U810, U811, U820,
U821, U830, U831, R810 to R813, R820 to R823, R830 to R833, C810 to C812, C816 to C818: 24 parts, none of a controller's pins added.
RESET1 is not wired to NRST as well: with a hold stage that would latch (its RESET holding NRST, NRST holding MR through the series
resistor), W145's finding W145-F1; section 8's bypass mutation reads exactly that wiring as FAIL.

**The band.** Trip 1.0969 to 1.1303 V, release from 1.0746 V (MODEL on TI's VITP, ISENSE and hysteresis rows): every VCAP in VOS3's
band leaves it released, every VCAP in VOS1's or VOS0's band trips it. VOS2's band straddles the trip (S-f).

**The ending.** A trip holds NRST; the reset puts the controller back in its reset state: RM0433 p.263 "When a system reset occurs, the
voltage regulator is enabled and supplies VCORE."; PWR_D3CR's reset value is Scale 3 (p.309), SYSCFG_PWRCR's ODEN 0 (p.560). Which
resets restore them is PRINTED (W144's F5, replacing W140's "the manual does not name"): "A system reset (nreset) resets all registers
to their reset values unless otherwise specified in the register description.", with "A reset from NRST pin (external reset)" among
its sources (8.4.2, p.329); Table 55's NRST row (p.330): "Resets VDD domain: IWDG1, LDO..."; neither register's description names an
exception, where PWR_CR3's does (p.306). S2's ACTVOS reading confirms a printed fact on the specimen.

**Its timing (OUT 5d).** TPS37 sense delay 17 us at most, printed only at "20% Overdrive from VIT" and 1 V/us (7.6, p.9): VOS0's bottom
is 11.5 % over the trip's top, VOS1's 1.7 %, so the printed maximum does NOT cover these entries (S2, on the real VCAP ramp, W144's
F11). RESET1 into the TPS3703's MR: RESET1 at most 300 mV at 5 mA against VMR_L at most 0.3 V (7.5, p.6); the pulse must last tMR_W, at
least 1 us (7.6, p.7, MIN column); MR to RESET 500 ns, NOM only (TYPICAL, inside S2's measured interval). NRST falls to 0.3 VDD within
104.8 us at the slowest corner (MODEL on the TPS3703's 250 mV at 3 mA, VDD 2 V row; ASSUMPTION: no weaker at the rail's 3.24 to 3.36
V); peak 8.70 mA under the recommended 10 mA. t_resp = 122.6 us, CONDITIONAL on S2 (W140's and W145's chain, RESET1 through 750 Ohm
onto NRST: 157.4 us of fall, 174.7 us).

**The reset hold (W144's F1; W145-F1; SESSION W148-1).** W145's 100 nF on CTR1 gave Equation 2's 82.2 ms only after a full discharge,
which TI ties to a fault longer than 5 % of the programmed delay (9.54 ms, SNVSBJ1E 8.3.4.1, p.23), and a loop's fault was not shown to
last that long: S5. The hold stage replaces it: "A logic low on MR causes RESET to assert. After MR returns to a logic high and the
SENSE pin voltage is within a valid window ... RESET is deasserted after the reset delay time (tD)." (SBVS249B 8.3.5, p.16), option F
with CT pulled to VDD: tD 14 / 20 / 26 ms (7.6, p.7, PRINTED), a factory-programmed timer (9.1.2.1), not a capacitor's discharge; TI
prints no condition on the fault's length beyond tMR_W's 1 us minimum. In a loop the MR pulse lasts at least NRST's fastest fall, 38.8
us (MODEL), because the controller holds VCAP up until it is reset and only the hold stage resets it. TI's Figure 8-2 note B ("To
initiate and continue time reset counter both conditions must be met MR pin above VMR_H or floating") and note C ("MR is ignored during
output RESET low event") are read either way below. The CT option is evaluated when SENSE enters the window (8.3.4, p.15), here at the
part's own start; a misread would show as a short hold, which W148-3's timing finds at the start's own test.

**The reset loop (OUT 5g).** Each cycle the image is in VOS1 or VOS0 for at most t_resp, then out of them for at least tD less t_resp
(note C) or tD (note B): duty at most t_resp / tD(min) = 0.876 %, average rise at most 0.518 K (MODEL), S1's limit 3.25 K/W at t_resp,
for ANY length of the fault: S-k reads CONDITIONAL on S1 and S2 only, and S5 is retired. W145's figures (0.212 %, 0.125 K at 174.7 us)
were CONDITIONAL on S5 and are withdrawn with its capacitor.

**Power-up.** The TPS3703 holds NRST from its VPOR (at most 1.0 V) through its UVLO (1.2 to 1.7 V, 8.4.2, p.17); the TPS37 holds MR low
from its VPOR (1.4 V) to its 2.7 V minimum (8.3.1.1, p.18), and its output is correct after tSD, 2 ms (7.6 note 4, p.9); the hold adds
at least 14 ms after MR rises, so the monitor is valid before the controller's first instruction: NRST released 14.0 to 28.04 ms after
VDD reaches 2.7 V (S4 confirms; the TPS37's release is Figure 7-3's DIAGRAM).

**Its own faults and the self-test (SESSION W140-3 as restated by W145-2, W145-3 and W148-3; the firmware row FW-B23, drafted).** At
every start and once an hour, one supervisor at a time: clear the flags (RMVF, RM0433 8.4.4 p.332), keep a marker and the RTC's time
where NRST does not reach (Table 55, p.330: "Debug features, Flash memory, RTC and backup RAM are not reset"), write Scale 1 at HCLK at
most 144 MHz and wait t_resp (122.6 us) from that write (W144's F11: the window times the regulator's ramp, the monitor, the hold stage
and NRST's fall on every unit in service, and finds a slowed one); still running, write Scale 3 within 10 us and report MONITOR FAILED.
PASSED needs the marker and RCC_RSR equal to Table 56's row 2 (p.332): PINRSTF and CPURSTF set, LPWRRSTF, WWDG1RSTF, IWDG1RSTF, SFTRSTF,
PORRSTF, BORRSTF, D2RSTF and D1RSTF clear (W144's F3), and (W148-3) the RTC's time from the write to the restart at least 7 ms: half
the hold's printed 14 ms minimum, 5.4 times the 1.3 ms TI prints with CT open, so a lost CT pull-up reads HOLD FAILED on an RTC clock
within +-40 % (the restart's NRST rise and boot, unprinted, must stay under 3.6 ms: ASSUMPTION, read by V-B24). Faults (OUT 5e): an
open divider, a stuck RESET1 or hold output, an unpowered TPS37 or hold stage, a swapped sense pin and a slowed chain are found by the
next test or at once; CT at ground (TI's latch mode, 9.1.3) holds the controller at once; **a lost CT pull-up is found by the next test's
hold timing**, so a latent hold fault followed by the loop is a double fault inside the test interval (S-l), no longer a latent single
fault seen only by inspection. A healthy unit whose ramp makes the interval from the write longer than t_resp reads MONITOR FAILED:
found at the first article by S2, then the window and S1 are re-read together.

**The controller's thermal time: NOT PRINTED (OUT 5f).** At the rail's top the bounded state is 100.20 C at 0.1585 A (T10's own model,
which gives T10's 99.6 C and 0.1570 A at 3.3 V); VOS0's 550 mA adds 1.3144 W, so inside 105 C the junction-to-ambient transient
impedance at t_resp (122.6 us) must be at most 3.65 K/W (W140's 4.09 K/W mixed the two corners; W144 read about 3.63 K/W). VOS1's
largest printed 125 C current is Table 120's 544 mA (W144's F7): at most 19.16 K/W at t_resp and at 132.6 us for a dead-monitor
self-test (W140 read 19.96 K/W; W144's F7 19.55 K/W at W140's corners). **U-02's local air (W144's F2):** the bounded state itself reaches 105 C at 79.32 C
local air at the rail's top (MODEL; W144's linear 79.5 C): at or over that air no ending of any speed keeps a VOS0 entry inside 105 C.

## 4. The acceptance, state by state (OUT 6)

"The controller inside 105 C in every served state and every state the protection admits" (105 C VOS0's limit; 125 C VOS1 to VOS3's).

| State | Criterion | Figure (one supply corner) | Verdict |
|---|---|---|---|
| S-a the bounded served state (FW-B20, FW-B21, rev V) | 105 C | 100.20 C | HOLDS (MODEL on PRINTED) |
| S-b VOS3 at its printed 200 MHz with every peripheral | 125 C | 121.32 C | HOLDS (MODEL on PRINTED) |
| S-c a VOS0 entry by any firmware | 105 C | ended within 122.6 us; needs ZthJA at most 3.65 K/W | CONDITIONAL (S1, S2; C2, C3) |
| S-d a VOS1 entry, the self-test included | 125 C | ended within t_resp; needs at most 19.16 K/W | CONDITIONAL (S1, S2) |
| S-e the self-test with a dead monitor | 125 C | at most 132.6 us; needs at most 19.16 K/W | CONDITIONAL (S1) |
| S-f VOS2 with VCAP under the trip's top | 125 C | not surely ended by the monitor | OPEN (row R-1) |
| S-g VOS3 above its printed 200 MHz | 125 C | no printed current | OPEN (row R-2) |
| S-h power-up before the monitor is valid | 105 C | held under both UVLOs; released at least 14 ms after MR rises | CONDITIONAL (S4) |
| S-i a latent monitor fault, then a VOS0 entry | 105 C | a double fault; window at most 3600 s | RESIDUAL (single-fault) |
| S-k the reset loop (an image entering VOS1 or VOS0 at every boot) | 105 C | duty at most 0.876 %, rise at most 0.518 K, any fault length; needs at most 3.25 K/W | CONDITIONAL (S1, S2) |
| S-l a latent hold fault (CT's pull-up lost), then the reset loop | 105 C | a double fault; W148-3's hold timing, window at most 3600 s | RESIDUAL (single-fault) |
| S-j any current up to the limiter's 0.5704 A | as above | every such state is one of S-a to S-l | none outside them |

**HO-E's acceptance: CONDITIONAL.** The served state holds 105 C; every VOS0 state the protection admits is ended by the drafted
monitor; whether the junction stays inside 105 C during the ending rests on S1 and S2 (in a reset loop too) and on C2 and C3.
Not claimed: a hardware bar from any document, a printed interval, a printed bound on the reset loop, or a closure.

**The focused check's conditions, restated:**

- **C1 (F1):** the reset hold drafted, composed, read and mutated, with the reset-loop row: W145's CTR1 hold (CONDITIONAL on S5)
  replaced by the hold stage of SESSION W148-1 (OUT 5d, 5g, 5h, 8): its printed minimum bounds the loop for any fault length; S5 retired.
- **C2 (F2):** U-02's local air at the supervisors at or under 79.32 C (MODEL at the rail's top; W144's linear 79.5 C).
- **C3 (F4):** revision V fitted (L9T5-D7), or a rev X part with its VCAP per scale confirmed first (S3).
- **C4 (F8, F11):** S1 at one supply corner (at most 3.65 K/W at t_resp, 3.25 K/W less the loop's rise); S2 on the real VCAP ramp
  with the self-test's window timed from the Scale 1 write, now through the hold stage; S3 and S4 as written; S5 retired (W148-1).
- **C5 (F3, F6):** the register rows R-1 (S-f), R-2 (S-g) and R-3 (FW-B23) in `HO-E-REGISTER-ROWS.md`.

## 5. The selection

**SESSION W140-1: H-2 with the drafted VCORE monitor (`apply_gen_sch_b_vcoremon.py`) and the self-test row FW-B23, PROVISIONAL on S1
to S4 (S5 retired by W148-1).**

- **authority:** SESSION, under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026.
- **authority_why:** an engineering selection inside the drafted circuit; no requirement, protected class, case row, purchase or
  publication changes; one approach stands after the reading (H-1 drops out on the documents, H-3 is not established on printed
  figures), so the ruling's second half (more than one option standing) fails; the residuals are measurable on a specimen (S1 to S4):
  amendment 1's supplier tasks (S5 retired), not a risk no measurement can remove.
- **ruled_by:** W140 (Claude), MESHSAT-1357. **ruled_on:** 7 October 2026. **reversed_by:** none.
- **To reverse:** drop `apply_gen_sch_b_vcoremon.py`; HO-E returns to REMAINING ENGINEERING with the owner item below.
- **End condition:** S1 reads the controller's ZthJA at t_resp over 3.65 K/W on board B (3.25 K/W less the loop's rise); or S2 reads a
  sense delay long enough that S1 fails at the longer interval; or two negative independent checks of this selection (W145's "S5 fails"
  clause retired with S5).
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
| W145-1 | the reset hold: 100 nF from CTR1/MR to GND per monitor, read at +-20 %; REVERSED by W148-1 | W144's F1 value: Equation 2's 82.2 ms kept the loop's duty at 0.212 % after a full discharge a loop was not shown to reach (S5) | W148-1's reversal |
| W145-2 | the self-test's window: t_resp from the Scale 1 write, then Scale 3 within 10 us | W144's F11: the ending timed on every unit in service, a slowed monitor found; the dead-monitor dwell bounded at 132.6 us (184.7 in W145's chain) | a window read from S2's measured ramp, S1 re-read |
| W145-3 | PASSED: the marker and RCC_RSR equal to Table 56's row 2 | W144's F3: six other rows set PINRSTF too | none needed |
| W145-4 | every thermal limit at one supply corner, 3.3577 V | W144's F8 | a narrower rail band issued as a case row |
| W145-5 | the reset loop's bound left CONDITIONAL on S5; the fixed-delay stage named, not drafted; REVERSED by W148-1 | the brief fixed the CTR1 hold; the stage needs a second part per supervisor, a latch-breaking element and its own check | W148-1 drafted the stage |
| W148-1 | the reset hold: HS-1b, a TPS3703F6050DSER per monitor (U811, U821, U831), CT to its VDD through 10 kOhm (R813, R823, R833), its RESET through 390 Ohm (R812, R822, R832) onto NRST, RESET1 on its MR alone, CTR1 open, C813 to C815 withdrawn | section 11: its registration (tMR_W 1 us) and its hold (14 ms) are both printed minima; its drive keeps t_resp at 122.6 us against HS-1a's 363.5 us and TYPICAL registration; HS-2 is non-stock with millivolt margins; HS-3 breaks the self-test or CON-004 | HS-1a (TPS3808G30, CT to VDD through 49.9 k, RESET through 750 Ohm) with OUT 5g re-read; end condition: V-B24 reads a hold under 14 ms or an MR pulse that does not register, or two negative independent checks |
| W148-2 | the series resistor 390 Ohm 1 % from the hold stage's RESET to NRST | the E24 value whose peak sink, 8.70 mA, stays under the TPS3703's recommended 10 mA with 13 % margin, its held current over the 0.3 mA minimum | 750 Ohm with OUT 5d's fall re-read |
| W148-3 | FW-B23 times the hold: the restart at least 7 ms after the Scale 1 write, on the RTC | a lost CT pull-up (the hold at 0.7 to 1.3 ms) is found by the next test, so S-l is a double fault inside the test interval | drop the check; S-l back to inspection |
| W148-4 | the TPS3703 sheet's fetch line in `v2/docs/records/l9t5hoe/fetch_held_back.py`, a folder of its own | l9t5's own fetch script is pinned by sha256 in l9t5_a1.py and l9t5_f01.py, whose outputs other records and pages pin | move the entry into l9t5's script with a dependency pass |

Each W145 decision: authority SESSION under the same rules; authority_why an engineering value or method inside the drafted circuit and
its rows, no requirement, class, case row, purchase or publication changed, one option standing after the focused check's reading;
ruled_by W145 (Claude), MESHSAT-1357; ruled_on 7 October 2026; reversed_by none, except W145-1 and W145-5 (reversed_by W148-1).
Each W148 decision: authority SESSION under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026;
authority_why an engineering selection inside the drafted circuit and its rows: the ruling's first half fails (no line a protected
class holds, no money spent, nothing bought, the parts drafted; no change to what the kit is claimed to be; no residual risk accepted
that a measurement cannot remove), so although HS-1a also stands the choice is an engineering value taken on section 11's figures;
ruled_by W148 (Claude), MESHSAT-1357; ruled_on 7 October 2026; reversed_by none.

## 6. The draft (OUT 8)

Composed in L4-E9's change-list order after iocguard (R-245), before the efuse record's R-236 and R-237 and Layer 6's three: 19 steps,
every one OK, the generator run to its end through record l8p's `gen_netlist.py`; 1539 parts and 1099 nets against 1515 and 1087;
added 24, removed 0, no existing part changed. Read by pin (now also: MONRST carrying only RESET1 and the hold stage's MR, the hold
stage's RESET through R812 alone to NRST, its CT through 10 k to its rail, and its printed minimum delay, read off its order code and
its CT, at least the loop row's 14 ms): DRAWN (before the draft: FAIL). With W137's canmb and W138's regstage, this draft after and
before them: DRAWN, the two netlists identical; no designator shared. Nine mutations FAIL: the output on a peer's NRST, the divider's
top from the rail, top and bottom exchanged, SENSE1 and SENSE2 exchanged, the monitor on a peer's rail, RESET1 and ground exchanged
(W140's six); the hold removed (U811 not fitted: W145's seventh, on the hold that replaced its capacitor); the hold stage bypassed
(RESET1 and the stage's RESET exchanged: RESET1 through R812 onto NRST, the latching wiring); a hold shorter than its printed minimum
(R813 not fitted: CT open, 0.7 to 1.3 ms). It applies to the tree's generator as it stands (order-free), refuses a second application and refuses the
tree's own generator (NOT RELEASED: RELEASE-T10.md). CON-004's failure domains kept.

The firmware row (`apply_hw_fw_contract_hoe.py`, FW-B23 and V-B24): on a scratch copy of the tree's contract it is refused alone (T10's
rows absent), applies after `apply_hw_fw_contract_t10.py`, refuses a second application, and leaves the tree's contract unchanged.

## 7. The four acceptance states (constitution section 2)

| Deliverable | Document acceptance | Supported design | Implementation | Physical qualification |
|---|---|---|---|---|
| the comparison | this page, its authors and W144's focused check (SUPPORTED AS CONDITIONAL) | H-1 and H-3 on quoted pages; H-2 PROVISIONAL | none | none |
| the monitor with its hold stage (`apply_gen_sch_b_vcoremon.py`) | this page | composed, read by pin, nine mutations FAIL; band on printed rows; interval CONDITIONAL (S1, S2); the loop's hold a printed minimum for any fault length (S5 retired) | NOT APPLIED (release-guarded) | S1 to S4 |
| the self-test row FW-B23 (`apply_hw_fw_contract_hoe.py`) | this page | window, PASSED pattern and hold timing on printed pages | no firmware exists | S2 and the hold's confirmation on the first article |

## 8. The supplier's tasks (OUT 9)

- **S1:** the controller's junction-to-ambient transient impedance on board B, three first-article supervisors at the rail's top, a
  step at 1.3144 W: pass at most 3.65 K/W at 122.6 us (3.25 K/W if the reset loop's 0.518 K is carried), and at most 19.16 K/W at the
  VOS1 step at 122.6 us and 132.6 us (or ST's transient thermal data with board B's copper).
- **S2:** the monitor's interval on the real VCAP ramp (TPS37 tCTS printed at 20 % overdrive only, the hold stage's MR to RESET as NOM
  only): VCAP driven by the controller's own Scale 1 write and VOS0 entry, three supervisors, at 76 C and at -40 C: pass, from the
  Scale 1 write and from VCAP crossing the trip to NRST under VIL, at most 122.6 us; PWR_CSR1's ACTVOS reading Scale 3 at the restart.
- **S3:** VCAP in VOS3 with the divider fitted under load steps: inside 0.95 to 1.05 V and under the trip's least 1.0969 V; a rev X
  part's VCAP in VOS3, VOS1 and VOS0 read on three parts against Table 112's revision V rows before it is accepted.
- **S4:** NRST held low from the hold stage's VPOR through both UVLOs, the TPS37's tSD and the hold at power-up, released 14.0 to
  28.04 ms after VDD reaches 2.7 V; ten power cycles each supervisor.
- **S5: RETIRED (SESSION W148-1).** The reset loop's hold is the hold stage's printed minimum, 14 ms for any manual-reset pulse of at
  least 1 us, so no figure TI does not print decides it. V-B24 still scopes NRST's low time per cycle on the first article as a
  confirmation of the implementation (pass at least 14 ms), which closes nothing by itself and gates nothing here. W145's drafted
  correspondence to TI on the CTR discharge is no longer needed.

## 9. W144's findings and their corrections

| Finding | Class | Correction here |
|---|---|---|
| F1 the reset loop | blocks | W145: CTR1 hold 100 nF drafted, its bound CONDITIONAL on S5 (TI's full-discharge condition not shown for a loop); W148: replaced by the hold stage (W148-1), composed alone and with canmb and regstage in both orders, read by pin, nine mutations FAIL; the loop row OUT 5g: duty 0.876 %, rise 0.518 K for any fault length on printed figures; S5 retired |
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
recheck, C1): closed as a draft by W148-1 (the hold stage); **W145-F2** withdrawn with C813 to C815; **W145-F3** (L4A-61): FW-B23 and
V-B24 after T10's rows, restated by W148; **W145-F4** (the coordinator): the register rows; **W145-F5** (IOHA, Layer 5), restated: the
hold delays the supervisors' start by 14.0 to 28.04 ms after their rail reaches 2.7 V and holds the supervisor under test up to 26 ms
each hour, inside IOHA row 3; **W148-F1** (Layer 6): the TPS3703F6050DSER's LCSC code and stock line (TI lists it Active), its WSON-6
land an ASSUMPTION (Layer 10); **W148-F2** (Layer 10): the hold stage by its TPS37 in the controller's pocket, CT's pull-up at its pin,
R812 at the NRST end; **W148-F3** (the targeted recheck): read OUT 5d's new chain, 5g's duty on TI's notes B and C read either way, and
5h; S1's limit is now read at 122.6 us; **W148-F4** (R-2's owner, a note): a loop driven by the image's own resets, each shorter than the
TPS37's sense delay, is not seen by the monitor and so not held; it is S-g's kind (no printed current for an image outside FW-B20), not
this hold's; **W148-F5** (the coordinator): TI's TPS3808 sheet has been committed in the tree since 26 September 2026 (SOURCES.yaml,
supervisor-tps3808g30); the fetch of 7 October 2026 is byte for byte that copy (`inputs/SOURCES-HOE.txt`); its committed status is left
as it is.

## 10. What this does not do, and reproduce

It runs no independent check and applies nothing. It does not print the controller's transient thermal impedance, the TPS37's delay
under 20 % overdrive or the TPS3703's maximum MR to RESET delay (no document prints them), bound VOS2 under the trip or VOS3 above
200 MHz (rows R-1 and R-2), or restate the register and the ledger (the coordinator's). The TPS3703 sheet is held back: its text is
read through `v2/docs/records/l9t5hoe/fetch_held_back.py` (SESSION W148-4: a folder of its own, because l9t5's own fetch script is pinned by
l9t5_a1.py and l9t5_f01.py) and `v2/docs/records/_lib/retake_pdf_text.py`; without it the record refuses and the test skips.

```
python3 v2/docs/records/l9t5/l9t5_hoe.py                    # prints l9t5_hoe.out (a few seconds)
env -C v2/ecad/tools python3 tests/run.py test_l9t5_hoe
```

The constitution was read and is acknowledged (sections 3 to 6 and 8): at most three materially different approaches, each basis
printed or labelled, the selection within authority, every limit a printed one, the failing mutations exercise the failure cases, and
no verdict is upgraded.

## 11. The reset loop's hold, compared (W148, on W145's finding W145-F1; OUT 5h)

W145's CTR1 hold bounded the loop only after TI's full discharge (a fault over 5 % of the programmed delay), which a loop's fault was
not shown to last, so the bound rested on a new supplier task S5. The standing rule (design robustness over measurement) asks the
design to be indifferent to that unknown first. At most three materially different approaches, each on its printed minimum:

| | What it is | Printed minimum hold, and what registers it | Response and loop (MODEL on PRINTED) | Own faults, detection | Parts, board B | Verdict |
|---|---|---|---|---|---|---|
| HS-1a | a hold stage after the TPS37: TI TPS3808G30 (board B's U221 and U543), RESET1 on its MR alone, its RESET through 750 Ohm onto NRST | td 180 / 300 / 420 ms with CT to VDD (SBVS050N 6.6, p.7); "A logic low (0.3 VDD) on MR causes RESET to assert." (7.3.3, p.11) and the delay after MR is high (7.3.4, p.12), no fault-length condition; the MR pulse that registers prints 0.001 us in the TYP column only | its drive prints 0.4 V at 1 mA only (6.5, p.6; board B's D4E-F2 buffers U221 for the same reason): NRST's fall bounded at 346.1 us, t_resp 363.5 us; duty 0.202 %, rise 0.119 K, S1's limit 3.56 K/W at 363.5 us | stuck released or R812 open: the next test; stuck low: at once; CT open gives 12 to 28 ms | 8 per supervisor; ICs' bodies 10.89 mm2 (TPS37 2.5 x 2.5, TPS3808 2.90 x 1.60) | stands; not selected (registration TYPICAL, a slower ending that makes S1 harder) |
| HS-1b | the same stage with TI TPS3703F6050DSER (UV only, SENSE on its own VDD), CT to VDD through 10 k, RESET through 390 Ohm onto NRST | tD 14 / 20 / 26 ms with CT to VDD (SBVS249B 7.6, p.7), a factory-programmed timer (9.1.2.1); "A logic low on MR causes RESET to assert." (8.3.5, p.16); tMR_W 1 us in the MIN column | VOL 250 mV at 3 mA (VDD 2 V row): NRST's fall 104.8 us, t_resp 122.6 us; duty 0.876 %, rise 0.518 K, S1's limit 3.25 K/W at 122.6 us; the loop's MR pulse at least 38.8 us | as HS-1a, and CT open (0.7 to 1.3 ms) found by W148-3's hold timing; CT at ground (latch mode) at once | 8 per supervisor; ICs' bodies 8.50 mm2 (TPS3703 1.50 x 1.50); Active in TI's addendum | **SELECTED, SESSION W148-1** |
| HS-2 | one supervisor on VCAP with a printed timeout, no TPS37: a TPS3703 window | tD 140 / 200 / 260 ms (option A, CT to VDD); tPD at most 30 us at 5 % overdrive | of the 13 orderable window codes none keeps VOS3's printed 0.95 to 1.05 V inside its window with both releases outside and trips under 1.15 V (7.5's +-0.7 % and 0.8 %); 11 catalogue options fit, none orderable ("minimum order quantities apply.", p.3); 1.00 V at 7 % direct leaves 4.0 mV and 6.0 mV | its UV side resets on any VCAP under the window (a constraint on a reduced-voltage low-power mode) | 4 to 6 per supervisor, one IC of 2.25 mm2 | not selected: a non-stock part with millivolt margins |
| HS-3 | no retry: TI's latch mode (9.1.3, p.20), the first trip holds until CT is driven from outside | unbounded (duty 0 after the first trip) | FW-B23's self-test trips the monitor at every start, so each supervisor would latch at its first start | a release needs a peer or a power cycle, an action from outside its failure domain (CON-004) | as HS-2 plus the release path | rejected |

**SESSION W148-1 (authority fields in section 5):** HS-1b. Both hold stages bound the loop for any fault length on a printed minimum;
HS-1b's registration is a printed minimum where HS-1a's is TYPICAL, and its drive keeps t_resp at 122.6 us where HS-1a's needs 363.5 us
(S1's limit is then read at a longer time, which makes it harder to meet); its shorter hold costs 0.518 K of loop rise, inside the
3.25 K/W limit S1 is read at. **End condition:** V-B24 reads a hold under 14 ms or an MR pulse that does not register, or two negative
independent checks of this selection; then HS-1a is the reversal. **S5's fate: RETIRED**, with W145's capacitor; V-B24's scope of the
hold is a confirmation, not a gate. HO-E's acceptance stays CONDITIONAL on S1 and S2 (and C2, C3), as the brief requires; this narrows
it, it upgrades nothing. AI review only where reviews are named; prototype design, nothing built or measured.
