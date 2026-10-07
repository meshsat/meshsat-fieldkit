**HO-E COMPARISON (Layer 4 task L4A-59, 7 October 2026, W140, branch `fnd/l4hoe` from `06d064ff`): DONE: three approaches compared on the makers' pages (H-1 DROPS OUT: RM0433 Rev 8, DS12110 Rev 11 and AN4938 Rev 7 show the voltage scale chosen by software, no strap and no option byte; H-3 FAILS: no package or printed heat path reaches the 15.84 C/W VOS0 needs at 76.25 C air; H-2 STANDS as the one design, PROVISIONAL: a drafted VCORE monitor per supervisor that resets the controller on any VOS1 or VOS0 entry whatever its firmware does, its interval proof resting on two unprinted figures); the selection SESSION W140-1 with its authority fields; the draft `apply_gen_sch_b_vcoremon.py` composed on board B (also with W137's canmb and W138's regstage, either order), read by pin, six mutations FAIL, refusals; the test module `test_l9t5_hoe.py`. NOT DONE: no independent check (L4A-100); nothing applied; the firmware rows (L4A-61); nothing physical (S1 to S4). NEXT: the coordinator's reading, then L4A-100's focused check of this selection.**

# HO-E: the supervisor's STM32H743 past its own 105 C VOS0 limit, compared and selected

Record l9t5, Layer 4 task L4A-59 of the AI-scope register (`_runs/l4ai/REGISTER.draft.md`, draft 2, rows L4A-59 and L4A-100, written on
W127's check 1a and finding 2). Prototype design: nothing in this kit has been built, bought, powered or measured, and no figure here is
a measurement. Every figure is printed by `l9t5_hoe.py` into `l9t5_hoe.out` ("OUT n" below is its section). Labels: PRINTED (a maker's
limit or tested row), TYPICAL, DIAGRAM (read from a maker's drawn figure), DECLARED, DRAFTED (not applied), MODEL, ASSUMPTION, SESSION.
This task closes no cx46 item: cx46 CORRECTIONS NOT CLOSED and Layer 4's DESK gate NOT PASSED stand until L4A-100 reads it.

## 1. The failed case, and what the protection now admits (OUT 2)

- T10 10j (c) and (e): "VOS0 under the trip takes the controller past its own 105 C VOS0 limit from 0.1936 A" and "(112.7 C at
  0.2452 A)"; cx46 finding 17: "the MCU reaches its 105 C VOS0 PRINTED LIMIT at approximately 0.1936 A, MODEL". Reproduced from T10's
  own 76.25 C air and LQFP100's 45.0 C/W (DS12110 Rev 11 Table 222, p.344).
- The 105 C is ST's: Table 112 note 5, p.210, "5. TJMax = 105 °C." on the VOS0 rows; Table 113, p.210, VOS0 Max TJ 105 C, VOS1 to VOS3
  125 C.
- The coordinator's message of this morning: W138 (record l4reg, `fnd/l4reg` 86dbcdff, filed in `inputs/`) selected a TPS2553-1 with
  IOS 0.4702 to 0.5704 A ahead of a TPS73733DCQRM3 (76.0 C/W) and removed round 6's rail trip; its L4REG-F7 hands the controller's
  protection to this task. The protection now admits up to 0.5704 A.
- On the printed maxima (Table 119, p.215, revision V) no VOS0 row has an operating point inside 105 C at this air: 480 MHz with every
  peripheral reads 157.9 C at its 105 C column, with none 134.2 C. The controller's own VOS0 maximum at 105 C, 0.550 A, sits inside the
  limiter's band. So HO-E is not a current limit's problem at all (W127's finding 2 is right and is not the whole of it): VOS0 must be
  kept out, or ended before the junction moves.

## 2. The three approaches

| | What it is | Basis | Result | Verdict |
|---|---|---|---|---|
| H-1 | a hardware-forced voltage scale | RM0433 Rev 8 p.264, p.279, p.280, p.309, p.560, p.260, p.262, p.307, p.215 to 216, p.256 (Table 32, the PWR pins); DS12110 Rev 11 p.29, p.210; AN4938 Rev 7 p.10, p.19 (PRINTED, quoted in OUT 3) | the scale is written by software after every reset (PWR_D3CR's VOS bits, then SYSCFG_PWRCR's ODEN for VOS0); no option-byte field and no PWR pin (VDD, VDDA, VREF, VBAT, VDDLDO, VCAP, the USB supplies, VSS, PDR_ON) selects a scale; the one hardware means printed, the Bypass supply ("Scale 0 ... available only with LDO regulator"), is itself "configured by software" once after every POR with the LDO enabled by default | **DROPS OUT** (the register's end condition). No hardware bar is claimed |
| H-3 | a thermal-headroom part or heat path | Table 119 p.215 and Table 222 p.344 to 345 (PRINTED); W138's regulator theta (record l4reg) | VOS0 needs at most 15.84 C/W junction to ambient (22.34 C/W with every peripheral off; 15.27 C/W at the limiter's 0.5704 A); the least ThetaJA of any package is 36.6 C/W, the LQFP100's 45.0 C/W; a case-top path leaves 4.34 C/W after ThetaJC 11.5 C/W for an interface and heat sink no held document prints for an LQFP100 (the one cooler held is the CM5's); VOS0 holds 105 C on 45.0 C/W only below 23.3 C air; the regulator's theta does not enter the controller's limit | **FAILS** on printed figures |
| H-2 | a firmware bound with an independent ending | FW-B20 (DRAFTED, T10); RM0433 p.1896 (IWDG); W137's vote (T10-ROUND6.md, `inputs/`); the TPS37 sheet SNVSBJ1E pp.5 to 18; DS12110 Tables 112, 116, 147, 152 | the firmware bound alone ends nothing; the IWDG ends hangs, not a running firmware that keeps writing IWDG_KR; the peers see TXD and act on SHDN, not on VOS0; a VCORE monitor (drafted) resets the controller on any VOS1 or VOS0 entry, on printed thresholds | **NOT SUPPORTED ON PRINTED FIGURES AS A PROOF** (the register's end condition is met: neither the sense delay at VOS0's overdrive nor the controller's transient impedance is printed); **STANDS, PROVISIONAL** under amendment 1 with S1 and S2 as supplier tasks |

## 3. H-2 in detail: the drafted VCORE monitor (OUT 5)

**What it reads.** Each controller's core voltage is on its VCAP pins (48 and 73). ST prints it per scale with the LDO on (DS12110 Rev
11 Table 112, p.209): VOS3 0.95 to 1.05 V, VOS2 1.05 to 1.15 V, VOS1 1.15 to 1.26 V, VOS0 1.26 to 1.40 V. RM0433 p.280: "VOS0 can be
enabled only when VOS1 is programmed in PWR D3 domain control register (PWR_D3CR) VOS bits." Whatever the path, a VOS0 core voltage is
over any VOS1 bottom.

**The circuit (DRAFTED, `apply_gen_sch_b_vcoremon.py`, NOT APPLIED).** Per supervisor: a TI TPS37 in WSON-10, channel 1 overvoltage
with the adjustable 800 mV option "01" (SNVSBJ1E Table 11-1, p.34), open-drain active-low RESET1; VDD on the controller's own 3.3 V with
100 nF (Table 6-1, p.5); SENSE1 from VCAP through 39.2 kOhm over 100 kOhm, both 0.1 % and 25 ppm/K; SENSE2 on the rail (the
undervoltage channel inert); RESET1 through 750 Ohm 1 % to the controller's NRST (pin 14). Designators U810, U820, U830, R810 to R832,
C810 to C812 (free on board B, and on W137's and W138's drafts). No controller pin added.

**The band (MODEL on PRINTED: VITP 0.792 to 0.808 V and ISENSE at most 100 nA, p.7; VHYS from Hyst% x 0.985 to x 1.015 of VIT+(OV)MIN,
Figure 7-1, p.10).** Trip 1.0969 to 1.1303 V, release from 1.0746 V: every VCAP in VOS3's band leaves it released, every VCAP in VOS1's
or VOS0's band trips it. VOS2's band straddles the trip (S-f below).

**The ending.** A trip holds NRST; the reset puts the controller back in its reset state: RM0433 p.263 "When a system reset occurs, the
voltage regulator is enabled and supplies VCORE."; PWR_D3CR's reset value 0x0000 4000 (p.309: Scale 3) and SYSCFG_PWRCR's 0x0000 0000
(p.560: ODEN off). The manual does not name which resets clear those two registers: read as the system reset an NRST pulse makes, and
S2 confirms it.

**Its timing.** TPS37 sense delay 17 us at most at VIT 800 mV, but printed at "20% Overdrive from VIT" (7.6, p.9); VOS0's bottom is only
11.5 % over the trip's top, VOS1's 1.7 %, so the printed maximum does NOT cover these entries (S2). NRST pulled to 0.3 x VDD (Table
147, p.241) through 750 Ohm toward the drain's at most 300 mV (p.7; ASSUMPTION: its current rises with its voltage), against
NRST's 10 kOhm, RPU 30 to 50 kOhm (Table 152, p.248) and the 100 nF reset capacitor, every corner of the rail and the pull-ups: at
most 157.4 us (MODEL), the sink's peak 4.52 mA under the recommended 5 mA (7.3, p.6). NRST's not-filtered pulse at least 300 ns (Table 152).
t_resp = 174.7 us, CONDITIONAL on S2.

**Power-up.** The TPS37's outputs are "in reset, regardless of the voltage at SENSE pins" between VPOR (1.4 V) and UVLO (8.3.1.1, p.18),
and the H743 leaves its own BOR0 reset from 1.62 to 1.71 V (Table 116, p.212), so NRST is held until the TPS37 is at its 2.7 V minimum;
then tSD, 2 ms (p.9), and Figure 7-3 (p.12) marks the first release at "tSD + tCTRx" (DIAGRAM, S4).

**Its own faults (SESSION W140-3; the firmware rows are L4A-61's).** At every start and once an hour the controller writes Scale 1 at
HCLK at most 144 MHz, waits at most 1 ms for VOSRDY (RM0433 p.309) and 2 ms for its own reset; a return is MONITOR FAILED, reported in
its state frame; RCC_RSR's PINRSTF ("Set by hardware when a reset from pin occurs.", p.450) with a kept marker reads PASSED. Scale 1 drives the whole real path (VCAP, divider, SENSE1, RESET1, NRST). An open or
shorted divider, a stuck output, an open series resistor, an unpowered TPS37 and a swapped sense pin are each found by the next test
or at once (OUT 5e); a firmware that skips the test is found by the peers within two hours (FW-B22's state frame). The residual is a
double fault: a monitor fault latent since the last test, then a firmware VOS0 entry, its window at most 3600 s.

**The controller's thermal time: NOT PRINTED.** DS12110 Rev 11 prints steady resistances only (Table 222). From the bounded state
(revision V, 0.1570 A, 99.6 C at 76.25 C air, T10 10c) VOS0 adds at most 1.320 W; inside 105 C the junction-to-ambient transient
impedance at t_resp must be at most 4.09 K/W (S1). The self-test with a dead monitor holds Scale 1 at most 3.0 ms; inside VOS1's 125 C
that needs at most 19.96 K/W (S1). A handbook figure for silicon's heat capacity is printed beside these for scale only (ASSUMPTION,
credited nothing): ST prints no die size.

## 4. The acceptance, state by state (OUT 6)

"The controller inside 105 C in every served state and every state the protection admits" (105 C VOS0's limit; 125 C VOS1 to VOS3's).

| State | Criterion | Figure | Verdict |
|---|---|---|---|
| S-a the bounded served state (FW-B20, FW-B21, rev V) | 105 C | 99.6 C (T10 10c) | HOLDS (MODEL on PRINTED) |
| S-b VOS3 at its printed 200 MHz with every peripheral | 125 C | 119.4 C (T10 section 4) | HOLDS (MODEL on PRINTED) |
| S-c a VOS0 entry by any firmware | 105 C | ended within 174.7 us; needs ZthJA at most 4.09 K/W | CONDITIONAL (S1, S2) |
| S-d a VOS1 entry, the self-test included | 125 C | ended within t_resp; needs at most 19.96 K/W | CONDITIONAL (S1, S2) |
| S-e the self-test with a dead monitor | 125 C | at most 3.0 ms; needs at most 19.96 K/W | CONDITIONAL (S1) |
| S-f VOS2 with VCAP under the trip's top | 125 C | not surely ended by the monitor | OPEN (FW-B20's verification; L4REG-F7) |
| S-g VOS3 above its printed 200 MHz | 125 C | no printed current | OPEN (FW-B20's verification; L4REG-F7) |
| S-h power-up before the monitor is valid | 105 C | held under UVLO; first release at tSD + tCTRx (DIAGRAM) | CONDITIONAL (S4) |
| S-i a latent monitor fault, then a VOS0 entry | 105 C | a double fault; window at most 3600 s | RESIDUAL (single-fault) |
| S-j any current up to the limiter's 0.5704 A | as above | every such state is one of S-a to S-i | none outside them |

**HO-E's acceptance: CONDITIONAL.** The served state holds 105 C; every VOS0 state the protection admits is ended by the drafted
monitor; whether the junction stays inside 105 C during the ending rests on S1 and S2. Not claimed: a hardware bar from any document,
a printed interval, or a closure.

## 5. The selection

**SESSION W140-1: H-2 with the drafted VCORE monitor (`apply_gen_sch_b_vcoremon.py`) and the self-test rows, PROVISIONAL on S1 to S4.**

- **authority:** SESSION, under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026.
- **authority_why:** an engineering selection inside the drafted circuit; no requirement, protected class, case row, purchase or
  publication changes; one approach stands after the reading (H-1 drops out on the documents, H-3 fails on printed figures), so the
  ruling's second half (more than one option standing) fails; the residuals are measurable on a specimen (S1 to S4): amendment 1's
  supplier tasks, not a risk no measurement can remove.
- **ruled_by:** W140 (Claude), MESHSAT-1357. **ruled_on:** 7 October 2026. **reversed_by:** none.
- **To reverse:** drop `apply_gen_sch_b_vcoremon.py`; HO-E returns to REMAINING ENGINEERING with the owner item below.
- **End condition:** S1 reads the controller's ZthJA at t_resp over 4.09 K/W on board B; or S2 reads a sense delay at VOS0's overdrive
  long enough that S1 fails at the longer interval; or two negative independent checks of this selection.
- **The owner item, PREPARED AND NOT RAISED** (raised only if the end condition is met): "The I/O supervisors' STM32H743 cannot hold its
  105 C VOS0 limit in the case's air, and no hardware means bars VOS0. Either accept that the 105 C limit during a firmware fault rests
  on the controller's measured transient thermal response, or change the supervisor part to one whose printed rows hold at this air (a
  part change and its cost)."

| Id | Decision | Why | To reverse |
|---|---|---|---|
| W140-2 | the divider 39.2 kOhm over 100 kOhm, 0.1 % and 25 ppm/K | the E96 top with the largest least margin (19.7 mV) between VOS3's top, VOS1's bottom and the release (OUT 5d's table) | another top with the table re-read |
| W140-3 | the self-test: at start and every 3600 s, Scale 1, VOSRDY within 1 ms, the reset within 2 ms; one supervisor at a time; the peers flag a counter stalled two intervals | the whole real path exercised; the latent window bounded; at most one supervisor out (IOHA row 3); 3.0 ms bounds the dead-monitor hold | a longer interval (the double-fault window grows with it) |
| W140-4 | 750 Ohm in series from RESET1 to NRST | the open drain discharging the 100 nF reset capacitor stays under the recommended 5 mA (4.52 mA) | a smaller reset capacitor with the drain on NRST directly |
| W140-5 | the monitor acts on NRST, not on the regulator's EN | a reset returns the scale within the interval above; a supply cut waits on the rail's capacitors to discharge and repeats the start, the supply configuration's single write after POR included (p.307) | the output on W138's limiter EN (IOC_LIM_EN) through a diode |
| W140-6 | a decoupling class entry "TPS37 " (class D, Table 6-1's sentence) | the generator's class table needs one for the new bypass | none needed if the part changes |
| W140-7 | the WSON-10 land id | the DSK package; KiCad's land check runs only where KiCad is | the 14-pin DYY package with its own pin map |

## 6. The draft (OUT 8)

Composed in L4-E9's change-list order after iocguard (R-245), before the efuse record's R-236 and R-237 and Layer 6's three: 19 steps,
every one OK, the generator run to its end through record l8p's `gen_netlist.py`; 1530 parts and 1093 nets against 1515 and 1087;
added 15, removed 0, no existing part changed. Read by pin: DRAWN (before the draft: FAIL). With W137's canmb and W138's regstage
(`inputs/`), this draft after and before them: DRAWN, the two netlists identical; no designator shared; no old text of this draft inside
any of theirs. Six mutations FAIL: the output on a peer's NRST, the divider's top from the rail, top and bottom exchanged, SENSE1 and
SENSE2 exchanged, the monitor on a peer's rail, RESET1 and ground exchanged. It applies to the tree's generator as it stands
(order-free), refuses a second application and refuses the tree's own generator (NOT RELEASED: RELEASE-T10.md). CON-004's failure
domains kept: each monitor touches only its own controller's nets and ground.

The five files copied from W137's and W138's branches are listed with their sha256 in `inputs/SOURCES-HOE.txt`, not in
`inputs/SOURCES.txt`: l9t5_case.py and l9t5_drafts.py pin that file's sha256, so an entry there would move their outputs and every
record that pins them (checked: with SOURCES.txt untouched, test_l9t5 reproduces every output of the record byte for byte).

## 7. The four acceptance states (constitution section 2)

| Deliverable | Document acceptance | Supported design | Implementation | Physical qualification |
|---|---|---|---|---|
| the comparison | this page, its author only | H-1 and H-3 on quoted pages; H-2 PROVISIONAL | none | none |
| the monitor (`apply_gen_sch_b_vcoremon.py`) | this page | composed, read by pin, six mutations FAIL; band on printed rows; interval CONDITIONAL (S1, S2) | NOT APPLIED (release-guarded) | S1 to S4 |
| the self-test rows | this page (text for L4A-61) | interval and dead-monitor hold on the drafted rows | no firmware exists | S2 on the first article |

## 8. Findings for other authors and the supplier's tasks (OUT 9)

- **W140-F1 (L4A-61, Layer 5):** FW-B20 restated: VOS3 only; SYSCFG_PWRCR.ODEN never written; the one other VOS write is the self-test;
  a static check of the image; FW-B22's state frame carries the test counter.
- **W140-F2 (Layer 6):** the TPS37 option needs an orderable code and a stock line; TI: "minimum order quantities may apply" (section 5).
- **W140-F3 (Layer 10):** the land id is an ASSUMPTION; the divider at the VCAP pins, its sense node short; the series resistor at NRST.
- **W140-F4 (L4REG-F7, W138):** VOS1 and VOS0 entries are ended by the monitor; VOS2 under the trip and VOS3 above 200 MHz are not (S-f,
  S-g) and rest on FW-B20's verification.
- **W140-F6 (board B's generator owner):** the comment over the supervisors' loop reads "Watchdog and brownout are the H743's own IWDG
  and BOR. That is deliberate: ..." (against a supervisor chip for output correctness, which the voters carry); the monitor serves the
  controller's own VOS0 thermal limit; the draft does not edit the comment, which is restated when the draft is taken.
- **W140-F5 (L4A-100):** the check reads this page, `l9t5_hoe.out` and the draft; H-1 and H-3 rest on the pages OUT 3 and OUT 4 quote.
- **S1:** the controller's junction-to-ambient transient impedance on board B, three first-article supervisors, a step of 1.320 W: pass
  at most 4.09 K/W at 174.7 us and 19.96 K/W at 3.0 ms (or ST's transient thermal data with board B's copper).
- **S2:** the monitor's entry-to-NRST interval at a VOS0 entry and at the self-test's Scale 1 entry, three supervisors, 76 C chamber:
  pass at most 174.7 us, and PWR_CSR1's ACTVOS reading Scale 3 at the restart.
- **S3:** VCAP in VOS3 with the divider fitted, under load steps: inside 0.95 to 1.05 V and under the trip's least 1.0969 V; ST prints no
  figure for a load on VCAP (at most 10.1 uA here).
- **S4:** NRST held low from the TPS37's VPOR through tSD + tCTR at power-up, ten power cycles each supervisor.

## 9. What this does not do, and reproduce

It runs no independent check and applies nothing. It does not print the controller's transient thermal impedance or the TPS37's delay
under 20 % overdrive (neither document prints them), bound VOS2 under the trip or VOS3 above 200 MHz (firmware verification), write
Layer 5's rows (L4A-61) or restate the register and the ledger (the coordinator's).

```
python3 v2/docs/records/l9t5/l9t5_hoe.py                    # prints l9t5_hoe.out (a few seconds)
env -C v2/ecad/tools python3 tests/run.py test_l9t5_hoe
```

The constitution was read and is acknowledged (sections 3 to 6 and 8): at most three materially different approaches, each basis
printed or labelled, the selection within authority, every limit a printed one, and the failing mutations exercise the failure cases.
