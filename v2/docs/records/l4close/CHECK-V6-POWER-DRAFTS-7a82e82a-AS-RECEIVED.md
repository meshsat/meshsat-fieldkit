# CHECK-V6: the focused independent check of the board A and B power drafts on candidate 7a82e82a

An AI review (Claude, independent checker V6), labelled so. It qualifies no hardware: nothing has been built, bought, powered or
measured, and every current and junction temperature below is a MODEL figure on labelled inputs. I wrote none of the drafts checked.

- **Candidate:** worktree `<worktree>/cxl4`, branch `fnd/v6cand`, commit
  `7a82e82a6c990873483e7ebbeac85b5065edbac6` (HEAD read before and after the check; `git status --ignored` identical before and
  after, and no file in the worktree newer than the check's start marker).
- **When:** read and run from 13:35 to 14:10 CEST, 5 October 2026 (Europe/Amsterdam).
- **Changed:** nothing in any worktree. My scripts and scratch compositions are under
  `<worktree>/_runs/claude/v6/scratch/` (2.2 MB).
- **Inputs read:** the constitution sections 3, 4, 6 and 8; case rows C-DEV rev 1, C-PROT rev 1, C-ALLTX rev 3; V3 (cx41) as received;
  the authors' reports T5b, L8R2-R8, T5-3, L9T5-R4, EFUSE-T12, L9STK-R5, L8P-R7, L8P-R8 (claims, not evidence); the records on the
  candidate; the makers' sheets named per item.

## 1. Verdicts

| Item | Verdict | Conditions (class) |
|---|---|---|
| **A** the dedicated return (L8R2-F31) | **CONFIRMED AS CONDITIONAL**, with blocking findings V6-B1 and V6-B2: every figure of the record reproduces on an independent solver and the every-vertex method is right, but the acceptance rests on two things the record does not state as conditions, one of which consumes its whole margin on a plausible layout | **physical (layout):** the plane resistance between the return sockets' lands and the other conductors' lands, on either board, in series with the return bundle, at most 0.354 mOhm for the printed ratings at the declared peak and 0.774 mOhm at C-DEV rev 1 (V6-B1); each XT60 contact under 2.06 mOhm over its life (one shared margin with the plane term); the 150 mm and 80 mm lengths. **vendor:** the XT60's after-test resistance and a rating for a PCB-soldered end (V6-m8); derating curves (JST, Wurth, Amass); minimum contact resistances. **desk:** the indirect A to B ground paths counted and bounded (V6-B2); `J_54V`'s lead at AWG 16 and the three return leads as Layer 7 harness rows (L8R2-F34); a ruling on F-4b (V6-m12); L8R2-F39's bond reading or detect line; L4-E9's rows (V6-m11) |
| **B** I-03 on C-DEV rev 1 | **CONFIRMED AS CONDITIONAL**: U7's relief, U601, the lead's pin 1 and the LDO input chain reproduce; `J_5V_IOC`'s pin 2 now holds with the composed return and is robust there; the connected path inherits A's conditions through the ribbons | **physical:** U601's efficiency, start-up and the rails' sequencing (drafts.out item 7); A's layout condition for the ribbons (V6-B1). **vendor:** JST's derating for `J_5V_DEV`'s pin 1 (6.0359 A against the inferred 5.9948 A, L8R2-F43). **desk:** ASSEMBLY.md's `J_5V_IOC` row (L9T5-F07) and IF-AB-POWER's rows (L9T5-F08); the record's LDO-input statement restated for the composed T10 design (V6-m1). T10 itself is item C |
| **C** T10 (L9T5-F06) | **CONFIRMED AS CONDITIONAL, but NOT on T10-A1 alone; the deficit is NOT corrected on the candidate.** The operating-condition findings, ST's, Diodes' and TI's rows, K3's arithmetic and composition reproduce. In T10's own scope the held two-transmitter row (L9T5-F13, 132.6 C) fails 125 C until a transmit-share row exists; on C-DEV rev 1 as the row stands the composed LDOs read 160.1 C, over the 150 C absolute maximum; F16 and F17 fail their limits; and the record's "no requirement covers either fault state" is wrong (V6-B3) | **desk (Layer 5, four rows, none exists):** T10-A1 (the state bound); a transmit-share bound (F13); a fault response for one and for both fabrics (F16, F17) traced to CON-004; the case row's supervisor figure revised once T10-A1 stands (L9T5-F12, the coordinator's). **physical:** T10-A5; the LDOs' local air at most 79.4 C for the declared peak (V6-m10); the SOT25's real thermal resistance on board B. **vendor:** the H743's enabled-peripheral currents (typical only, V6-m10); the AP2112K's accuracy between dropout and its 4.3 V test condition |
| **D** the eFuse settings (EF-F01, EF-F02) | **CONFIRMED AS CONDITIONAL**: both resistors are inside TI's printed 453 to 7869 Ohm; both bands reproduce from Equation 5, the resistor's corners and Figure 21's envelope; each foot clears its maker-printed demand; each top is under its downstream printed rating; the inventory missed no current-limiting switch in the record's scope | **vendor/physical:** the J_LIME receptacle's and the RockBLOCK conductor's rise at the inside air (V6-m4); the RockBLOCK's input capacitance and the LimeSDR's transients at start. **desk:** the RockBLOCK's charge-current pads left unbridged as a build condition (V6-m5); the record's composition brought up to the candidate (V6-m3); Layer 6's codes (EF-L03) |
| **E** the thermal guard C4 (L8P-F07, L8P-F08) | **CONFIRMED AS CONDITIONAL.** This is not a negative check: the guard-selection loop does not end. The window as a ramp (0.908 V against 0.84 V on the full count), the four loop readings, the gate network at tolerances, FM1, FM2, the no-trip arithmetic and the seven mutations reproduce | **physical:** E-13's gradient (15.68 K, 13.56 K with two FETs carrying all) and heat-step lag; E-13b (b2) (the state before tEN on a slow ramp; the switch under VDD 5 V during a precharge); the A to P ground offset under 0.980 V; the off-leakage doubling (the shunt's site under 98.7 C); the 2N7002's on-resistance at a 4.5 V drive (17.2 Ohm assumed against 657 Ohm needed); the no-trip margins rest on record l9stk's junctions, which rest on E11-29's 33.12 K/W target. **vendor:** C262's and C260's X7R bias; the NGF0006A land. **desk:** L4-E11's DD-7 netlist check and its 20c and 20f rows restated (V6-m2); the single-failure table completed (V6-m7) |
| **F** the connected supply path | **CONFIRMED AS CONDITIONAL**: with every draft of A to E composed on both boards the generators run (board A 828 parts, board B 1479, none unplaced, intent written), no designator collides, and every record check that applies reads DRAWN with its mutations failing; two record checks break on the full composition (L4-E11's DD-7 check and record l9t5's I-03 divider mode), both check-text defects, not circuit ones; **no claim of "supply path complete" is made anywhere** (EXECUTION-PLAN.md line 1603 says the opposite) | **desk:** restate L4-E11's `check_dd7_netlist.py` for the guard (V6-m2); run record l9t5's I-03 acceptance in its T10 mode on the composed design (V6-m1); L4-E9's change-list rows for the new drafts (V6-m11); the efuse record's board B order (V6-m3) |

**The affected supply path is not complete:** A's return is conditional (V6-B1, V6-B2 open) and T10 is conditional on four Layer 5 or
case-row items that do not exist. Neither may be reported as closed on this check.

## 2. Findings

### Blocking

**V6-B1 (items A and B): the acceptance assumes each board is one node; the boards' own plane resistance can consume the whole
margin, and it is not among the conditions.**
- *Where:* `v2/docs/records/l8r2/l8r2_gndret.out` lines 196 and 197 (3a, "NOT IN THE MODEL ... each board's own plane resistance, taken
  as one node a board") and lines 476 to 488 (6d, the conditions, which do not list it); `l8r2_gndret.py` lines 766 to 767 and 1285;
  `L8R2-KNOWN-DEFECTS.md` lines 937 to 950 (6d) and 973 (the credit "(c) ... on the conditions of 6d"); L8R2-F33 (6f) bounds only the
  land joins' widths, not the path between lands.
- *Why it matters:* the six return conductors at their printed contact limit total about 0.44 mOhm (cold). A resistance in series
  with that bundle (plane copper between the return sockets and the place the 5 V return enters or leaves) shifts the division back to
  the VH pins and the ribbons. On board A the 5 V returns "close at each stage's output" (`l8r2_gndret.out` 3h); no board is laid
  out, so nothing yet places the XT60 sockets at those points rather than at a distance the VH pins' path does not have.
- *My arithmetic (MODEL, my own solver, a shared series resistance Rs on the bundle, every other input the record's):* the largest
  Rs that keeps every row inside its rating is: printed ratings at -20 C, a ribbon conductor 0.354 mOhm (declared peak 27.9108 A) and
  0.774 mOhm (C-DEV rev 1), a VH pin 2 1.206 and 4.348 mOhm; least ratings at 76.25 C, a ribbon 0.143 and 0.438 mOhm, a VH pin 2
  0.447 and 1.157 mOhm. For scale (ASSUMPTION: rho 1.72e-8 Ohm m, 0.5 oz = 17.5 um inner planes as l8r2 6f states the stackups, spreading
  between two 3 mm lands 50 mm apart, Rs/pi times ln(d/a)): board B's three ground planes 0.25 mOhm at -20 C and 0.36 mOhm at 76.25 C,
  board A's two 0.37 and 0.54 mOhm. With 0.62 mOhm (both boards, cold) the declared peak puts a ribbon conductor at 1.218 A against
  its printed 1 A (a VH pin 2 8.27 A); with 0.90 mOhm hot, 1.041 A. On C-DEV rev 1 a ribbon conductor reads 0.916 A cold (inside 1 A)
  and 0.783 A hot against the least 0.5995 A, the criterion decision D8-3 used to choose three leads over two.
- *Correction (smallest):* add the series plane resistance to 6d as a named condition with the bounds above, carry it into 6b's
  verdict text and into L8R2-F33 as a layout constraint (the return sockets adjacent to the 5 V stages' outputs on A and to the 5 V
  leads' entries on B, or a stated maximum resistance between them), and close it by an extraction on the routed boards or a measured
  division on the first harness. If the bound cannot be met by placement, the fourth lead or a bar on the bundle is the design change.

**V6-B2 (item A): the census counts only the direct A to B conductors; several indirect ground paths between the two boards are
neither counted nor bounded.**
- *Where:* `l8r2_gndret.out` lines 196 to 197 name only "the shields of the GNSS and LoRa pigtails"; 6a (line 425) and 6b count the
  leads, ribbons and sockets only. The paths, read on my composed netlists and `v2/ecad/tools/pcb_interfaces.yaml`: IF-BA-RF (line
  1432: board B's U.FL `J_GNSS1`, `J_LORA1`, `J_WOA`, `J_WOB` and the RM520N's, RockBLOCK's and LimeSDR's coax to board A's SMA jacks
  `J_RF3` to `J_RF11`, every one with its shell on GND on board A), IF-MON (line 1380: the monitor's supply return at A `J_MON` pin 2
  and its HDMI grounds at B `J_HDMI` pins 2, 5, 8, 11, 17, SH), IF-LID-HF (line 1052: the QMX's supply return at A `J_HF` pin 2 and its
  USB ground at B `J_QMX` pin 4), the panel board C (A `J_MAINSW` pin 2 and B `J_PANEL` pins 3, 9, 14, 17), and board D (A `J_MEZZ1`,
  `J_MEZZ_PWR1` to D, and D's touch USB to the monitor). The QMX and the monitor are also fed from board A with a second ground through
  board B, so part of their supply current returns through the A to B network and is in none of the three totals.
- *My arithmetic:* at its own worst vertex an indirect branch of resistance R carries the total divided by (1 + R x G), G the counted
  network at every contact high: with the return, R = 20 mOhm gives 0.560 A at the declared peak and 0.421 A on C-DEV rev 1 (76.25 C);
  R = 10 mOhm, 1.098 A and 0.826 A. As drawn without the return, 2.283 A and 4.119 A. These branches end in U.FL, MHF4, HDMI and USB
  contacts whose current ratings no held record states.
- *Correction:* list every indirect ground path between A and B with its resistance from held data (or a bounding assumption labelled
  so) and its weakest printed rating, apply the same every-vertex bound, and add the QMX's and the monitor's possible share to the
  return totals; or break the DC path where it carries no function (for example a shell isolated from GND on one end). Until then the
  claim "every branch with a printed rating is inside it" covers the counted branches only.

**V6-B3 (item C): "no requirement covers either fault state" is wrong; CON-004 does.**
- *Where:* `v2/docs/records/l9t5/l9t5_t10.out` lines 154 and 161 and lines 258 to 261; `l9t5_t10.py` lines 452, 463, 622 and 627;
  `L9T5-CASES.md` line 171 (and rows 114 and 115); `README.md` lines 58, 59 and 172.
- *The sources:* `v2/docs/REQUIREMENTS-TRACE.md` lines 974 to 978: **CON-004** (constraint, core, BLOCKER), "the three talk over two
  independent CAN-FD fabrics", accepted when "A7 (either fabric cut, the quorum holds) passes"; REQ-004's notes (line 760) "A7 is traced
  by CON-004". `v2/docs/ARCH-PCB-B-IOHA.md` section 12 (lines 232 to 233: "Every row is a failure this design is supposed to survive"),
  row 7 "One CAN fabric breaks or a transceiver fails dominant" and row 8 "Both CAN fabrics break"; section 13 A7 "cut fabric A, then
  fabric B, one at a time ... with both broken nothing moves". The record read REQ-073 (the other direction, rightly) and REQ-004's
  acceptance, and missed CON-004.
- *What is true:* both fault states are inside a mandatory core constraint's scope (rows 7 and 8, A7); what no requirement or test
  names is the shorted-bus variant that the TCAN334's 180 mA row describes (A7 cuts the bus). The verdicts of F16 (144.2 C against
  125 C) and F17 (176.3 C against the 150 C absolute maximum) stand; their basis is CON-004, not an uncovered state, so their closure is
  required for CON-004, not optional.
- *Correction:* replace the sentence with the CON-004 trace in the four files, name CON-004's owner beside Layer 5's for F16 and F17,
  and state that A7 as written (a cut) does not exercise the 180 mA row, so the shorted-bus variant needs its own test or analysis.

### Minor

**V6-m1 (B, F): record l9t5's I-03 acceptance of the LDO input describes a design the candidate no longer composes.** `l9t5_drafts.out`
line 271 (B3) and line 312 judge the LDOs at U601's 5 V set point ("for any ground shift under 0.9417 V"); with T10's selected
`iocpre` drafts composed the set point is 4.18 V and the chain is T10-A3's: 4.0711 - 0.0836 - 1.8 x 0.042520 - 0.0681 = 3.8428 V against
3.7693 V, so the shift the LDOs allow falls from 0.9417 V to 0.1417 V (still 12 times the 0.0114 V shift with the return). On the full
composition `check_l9t5_netlist.py` in its default mode reads `A DIV FAIL` (it wants 10.7 k; `DIVS` at line 49); only `div="t10"`
reads DRAWN. Correction: state B3 as superseded by T10-A3 when the T10 drafts are composed, and make the I-03 check read the T10 mode
whenever `apply_gen_sch_a_iocpre.py` is in the composition.

**V6-m2 (E, F): L4-E11's DD-7 netlist check reads FAIL on any board A that carries the guard.** `v2/docs/records/l4e11/check_dd7_netlist.py`
lines 11, 12, 70 and 71 require RT1 on DOCK_EN_RET and DOCK_EN_OUT; on my full composition it prints "DOCK_EN_RET reaches ['J_DOCK',
'Q44', 'Q60', 'R261', 'U48'], wanted ['J_DOCK', 'Q44', 'RT1', 'U48']" and the same for DOCK_EN_OUT, and nothing else fails.
`test_l4e11` passes only because it does not compose the guard. Also the guard adds C261 (1 uF) and 30 uA on DOCK_EN_OUT, which
L4-E11 20f's docking row does not yet count. Correction: L4-E11 restates its LOOP group for the guard's pair (L8P-R8-F1) and its 20c
and 20f rows.

**V6-m3 (D, F): the efuse record's board B order predates record l8r2's round 7 and 8 drafts.** `efuse_check.py` line 276 (`ORDER["b"]`)
has no fandec, gndret, gndrtn, iocbuck or iocpre, so on the candidate its board B still refuses at fans12 (`efuse_check.out` line 180)
and its netlist reading ran without fans12 (line 181). On my full composition (15 board B drafts, u23ilm and u24ilm among them) R36
reads 750R on U23 pin 7 to GND and R43 1.21k on U24 pin 7 to GND, and putting R36 back to 301R or R43 at 909R fails my check.
Correction: add the five drafts to `ORDER["b"]` in their places and regenerate.

**V6-m4 (D): the downstream checks use the printed ratings without the inside air, while record l8r2 on the same candidate does not.**
`efuse_check.out` line 533 (J_LIME, Wurth 692122030100, 1.8 A) and line 540 (the RockBLOCK's conductor, 1 A). Wurth's USB 3.0
receptacle prints 1.8 A max and an operating range of -20 to +85 C including the rise (sheet p.1); at the 76.25 C inside air that
leaves 8.75 K for the contact's own rise, and on record l8r2's least-rating reading it carries at least 1.8 x sqrt(8.75/60) = 0.687 A,
under the LimeSDR's own 0.9534 A demand, independent of U23's setting. The RockBLOCK's 5 V conductor (1 A at 25 C, 105 C top) reads at
least 0.5995 A at the inside air, under U24's top 0.8496 A (the demand, 0.500 A, is under it). Correction: carry both rows as vendor
conditions (the rise at current, or a derating curve) and state the ambient each rating is judged at.

**V6-m5 (D): the RockBLOCK's charge-current option is not a stated build condition.** Ground Control's hardware page
(`v2/vendor/rockblock/groundcontrol-docs-rockblock-9704-hardware-20260927.txt` lines 310 and 362 to 369): the 16-pin input is "4.0V and
5.3VDC, at a maximum of 500mA", the supercapacitors' charge limit is about 460 mA and "can be increased to ~800mA" by bridging two
pads. U24's foot 0.6681 A holds only with the pads open. Correction: one line in ASSEMBLY.md and EFUSE-SETTINGS.md.

**V6-m6 (D): board A's U23 is judged more leniently than EF-F01 on the same criterion.** `EFUSE-SETTINGS.md` line 38 and line 134
(EF-O03), `efuse_check.out` lines 400 and 405: R98 453 Ohm at 1 % and its TCR reaches 445.8 Ohm, under the recommended 453 Ohm minimum
(TPS2596 sheet 7.3, p.5), and its band's top 2.1816 A is over the 2 A continuous rating; it is read PASS (EDGE). Correction: classify it
by the same rule as EF-F01 (511 Ohm, the record's own suggestion, gives 1.5684 to 1.9949 A) or record why an edge is tolerated.

**V6-m7 (E): the single-failure table misses Q60's gate-to-drain short (and C261 open, U60's ground pad open).** `l8p_c4.out` section 10
(lines 172 to 187). With Q60's gate on its drain, the cold gate network (R262 47 k to OVERTEMP low, R263 1 M) loads the return with
about 44.9 kOhm beside the other 13.25 uA of sinks: the return then solves to 0.5898 x (1.825 - 13.25e-6 x 15150) / (1 + 0.5898 x
15150 / 44900) = 0.799 V at DOCK_EN_OUT 1.825 V (about 18 uA through the network, 31 uA of sinks against the 26.45 uA allowance), under
0.84 V before any conduction of the diode-connected Q60 is counted (the window fails: a dead pack's precharge can be stopped); tripped, Q60 cannot
pull the return below its own threshold, so the guard cannot trip, and the closed loop's first-inverter gate is no longer sure to pass
2.5 V. Found by E-13b (a) or at start; latent between checks. Correction: add the rows.

**V6-m8 (A): neither XT60 sheet states a rating for a PCB-soldered end.** `v2/vendor/battery/amass-xt60-spec-2021v1-lcsc-c98733.pdf`
prints 35 A MAX "(12AWG/delta T < 85 C)" and describes the series for wire-to-wire use; the V1.2 sheet prints 30 A with no condition.
The board end of each `J_GR` contact is soldered into the board (KiCad's `AMASS_XT60-F_1x02_P7.20mm_Vertical`), a termination no
printed condition names. The rows' 11.03 A is about a third of 30 A, so the margin is large; the label should say so.

**V6-m9 (C): CON-017 already restricts the fitted supervisors to revision V or X.** `REQUIREMENTS-TRACE.md` CON-017 acceptance (5) and
(4): revision V or X at assembly, and the firmware refuses both FDCAN fabrics on revision Y or W. T10's bounded demand takes revision Y's
larger row (0.1691 A at 101.4 C; revision V's is 0.1333 A at 96.0 C), which is conservative; L9T5-F14 should cite CON-017.

**V6-m10 (C): T10-A2's margins rest on two unstated inputs.** (1) The air: at L4-E12's 76.25 C mixed air the declared peak reads
121.8 C; at its 81.89 C exhaust the same 0.25 A reads 81.89 + 184 x 0.9907 x 0.25 = 127.5 C (over 125 C) and the bounded state 123.6 C;
the LDOs' local air must be at most 79.4 C for the declared peak. (2) The bounded demand 0.2291 A uses ST's "all peripherals disabled"
row; the enabled set (FDCAN, I2C1, the ports, the watchdog) is printed only as typical microamps per megahertz (DS12110 Table 39,
p.117 to 122), a few milliamps at 144 MHz. The record names (2) as owed in T10-A1; (1) is not stated.

**V6-m11 (F): L4-E9's change list has no row for most of the drafts composed here.** `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`
section 3 (rows 24 to 33 for board A, 63 to 66 for board B): no row for gndret, fandec, gndrtn (A and B), iocbuck and iocpre (A and B),
thguard, u23ilm, u24ilm, panel5v, ph4, d8v3 or vbus20ov, so "L4-E9's change-list order" for them is each author's placement (owed:
L8R2-F36, L8P-R8-F2). mainpb, a next-free taker, draws R603 and C607 on the full composition, R264 and C264 in record l8p's, while
row 33 names R233 and C241 (L9T5-F02). No order I composed collided.

**V6-m12 (A): F-4b fails a printed rating and no ruling places it outside the fault set.** `l8r2_gndret.out` line 522: every source at
its bound (44.1338 A) puts a ribbon conductor at 1.00436 A at -20 C against 1 A (my figure 1.004364 A). It is a five-overload state;
the record says it is not drafted for, but no decision (SESSION, with authority fields) records that the design need not serve it. With
V6-B1's plane term it is worse. Correction: record the decision, or carry the fourth lead (0.7885 A there) into V6-B1's correction.

## 3. Item by item

### A. The dedicated return

- **The census, read on my own full composition** (both boards with every draft of A to E): six VH lead contacts with pin 2 on GND on
  both boards (`J_5V_S1` to `S3`, `J_5V_DEV`, `J_5V_IOC`, `J_54V`), all on the B2P-VH standard header land; 17 ribbon ground
  conductors (`J_AB1` pins 3 to 8 and 22 to 24, `J_AB2` pins 3 to 10); `J_GR1` to `J_GR3` whole on GND on both boards: six return
  conductors. It matches 6a. Not counted: V6-B2.
- **The vertex argument is right.** A conductor's current is I times g_i / (g_i + the rest); it rises with its own conductance and
  falls with every other, and each conductance falls with each of its contact resistances, so the maximum over the box is the vertex
  with its own contacts at zero and every other at its maximum. My brute force over every class-count state (independent code) equals
  that vertex for every class at both copper ends. A non-uniform copper temperature (the branch's own conductor at -20 C, all others at
  76.25 C, not a physical split) still holds: a VH pin 2 5.36 A, a ribbon 0.70 A, an XT60 contact 11.72 A at the declared peak.
- **Every figure reproduces** on my solver: as drawn 10.6376 / 12.0918 A (VH pin 2, 76.25 / -20 C, C-DEV rev 1; V3's corner) and
  2.0747 / 2.6716 A (ribbon); with the return, C-DEV rev 1: VH 2.9578 / 3.7056, ribbon 0.3671 / 0.4776, XT60 6.9915 / 8.2964, `J_54V`
  2.0611 / 2.6152 A; declared peak 27.9108 A: 3.9333 / 4.9277, 0.4882 / 0.6352, 9.2972 / 11.0326, 2.7408 / 3.4777 A; ground shift
  11.43 mV. On the full composition the GND peak is 27.8159 A (T10 lowers `+5V_IOC` to 1.38 A), slightly under the figure judged.
- **The ratings and their conditions, read on the sheets:** JST VH catalogue p.1, 10 A "When using AWG #16 with the standard type
  header", 7 A for AWG #18 with the shrouded header, -40 to +105 C including the rise, 10 mOhm initial and 20 mOhm after test with no
  minimum, the note against parallel branching; Wurth WR-CAB 63912615521CAB p.1, 1 A max, rated at 25 C with the derating sentence,
  -25 to +105 C, 237 Ohm/km max; WR-BHD socket 61202623021, 1 A, 20 mOhm max, -40 to +105 C; Amass V1.2 (XT60-F and XT60-M pages),
  0.55 mOhm, 30 A, 60 A momentary, 12 AWG, 1000 uses, -20 to 120 C; Amass 2021V1, 35 A MAX (12 AWG, rise under 85 C), at most 1.0 mOhm,
  100 uses, -20 to 120 C. The least ratings recompute: 5.9948 A (VH, taken at 25 C), 0.5995 A (ribbon), 25.11 A (XT60 from 35 A and
  85 K; 20.36 A if V1.2's 30 A is taken from 25 C). The 12 AWG and 16 AWG wires themselves have no maker's sheet (L8R2-F34): JST's 10 A
  rates the contact with that gauge.
- **`J_54V`'s pin 2 at AWG 18:** no printed rating for the standard header, confirmed; at AWG 16 it reads 4.9269 A, confirmed. The
  lead is still 18 AWG in ASSEMBLY.md: a Layer 7 harness row.
- **The fault cases reproduce:** F-1 6.4094 / 0.8746 / 13.7130 A (VH, ribbon, XT60, declared peak, -20 C), F-2 5.5717 / 0.7359 /
  12.2276, F-3 4.9642 / 0.6408 / 11.1016, F-4b 1.0044 A on a ribbon (V6-m12); F-1 to F-3 inside the printed ratings and latent (no
  detect line, L8R2-F39); F-5 is the board as drawn.
- **The stated assumptions reproduce:** the rows hold on the printed ratings up to 2.06 mOhm an XT60 contact (a ribbon then 0.9994 A at
  -20 C) and on the least ratings up to 1.43 mOhm (0.5995 A at 76.25 C); zero minimum resistance is the right reading; no sheet prints a
  derating curve; 150 mm and 80 mm are assumptions (IF-AB-WALL leaves the length TBD).
- **Credit:** (a) yes, on my own composition in L4-E9's order with the authors' placements (V6-m11); (b) yes, the record's 13 mutations
  plus mine (`J_GR2` removed from board A, `J_GR1` pin 2 moved to `+5V_DEV` on board B: both FAIL); (c) on the record's one-node model
  yes, on the printed ratings and the least ones; not established for a layout (V6-B1) or for the uncounted branches (V6-B2).
- **Answer:** L8R2-F31 is corrected in direction and on the model's printed figures, CONDITIONAL; it is not corrected on printed
  figures without conditions, and the conditions the record lists are incomplete.

### B. I-03 on C-DEV rev 1

- **U7:** (36.6251 - 7.0380) W at 4.9019 V = 6.0359 A (the budget's figures, RECORD) against 0.043 / (0.006 x 1.01) = 7.0957 A (LM5176
  SNVSAI1D p.7, VSNS 43 / 50 / 57 mV; R43 declared 6 mOhm 1 %): +1.0598 A. On my composition no LDO is on `+5V_DEV` (check DEV DRAWN;
  U40's input moved back to `+5V_DEV` FAILS).
- **U601 and the lead's pin 1:** TPS62933 SLUSEA4D p.6 and 7: VFB 0.784 to 0.816 V over TJ -40 to 150 C, IFB 0.15 uA, high-side limit
  4.2 / 5.0 / 5.8 A, low-side 2.9 / 3.8 / 4.5 A, so about 5.15 A at most, under the VH's 10 A; the load 1.4749 A (I-03 alone, constant
  power) or 1.3800 A (with T10, the LDOs' own current), under the 3 A rating.
- **The LDO input:** I-03 alone, 4.8719 - 0.100 - 0.0627 - 0.0512 = 4.6580 V against 3.7674 V (AP2112 DS39724 p.8 at VIN 4.3 V:
  +1.5 % at 1 to 30 mA, 1 %/A, 0.1 %/V, 400 mV at 600 mA), confirmed; with T10 composed, T10-A3's 3.8428 V against 3.7693 V (V6-m1).
- **The connected path (V3's point):** `J_5V_IOC`'s pin 2 now reads 2.9578 / 3.7056 A on C-DEV rev 1 with the composed return
  (3.9199 / 4.9109 A at the composed GND peak), inside the printed 10 A and the least 5.9948 A. It is robust to V6-B1: the printed row on
  C-DEV rev 1 holds up to 4.35 mOhm of series plane resistance. So the pin's acceptance holds, and it holds **on** the composed return
  drafts and l8r2's 6d conditions; it is not independent of L8R2-F31, as round 4 now says. The ribbons and the ground shift, the rest of
  the connected path, carry V6-B1 and V6-B2.
- **Credit:** (a) yes on both boards; (b) yes (my mutations above); (c) its own parts hold on printed figures; the connected path is
  conditional on A.

### C. T10 (L9T5-F06)

- **The operating state:** confirmed unbounded; HW-FW-CONTRACT.md and PANEL.md carry no clock, run-mode or voltage-scale row for the
  supervisors, ARCH-PCB-B-IOHA.md's "roughly 60 mA each" is an intent, and no supervisor firmware exists.
- **ST's rows read:** DS12110 Rev 10 Table 30 (rev Y, p.111): VOS1 400 MHz all enabled 220 / 400 / 500 / 840 mA at TJ 25 / 85 / 105 /
  125 C; VOS3 144 MHz disabled 41 / 120 / 180 / 290 mA. Table 129 (rev V, p.218): VOS3 144 MHz 55 / 109 / 153 / 212 mA. Table 230
  (p.346): LQFP100 45.0 C/W. The operating point 101.4 C at 0.1691 A reproduces.
- **The regulator:** DS39724 p.3: TJ +150 C (absolute maximum), SOT25 184 C/W without a heat sink, VIN 2.5 to 6.0 V, TA -40 to +85 C;
  p.8: IOUT(MAX) 600 mA at VIN 4.3 V, dropout 400 mV at 600 mA, shutdown 160 C typical. Junctions reproduce, 76.25 + 184 x 0.9907 x I:
  118.0 C (0.2291 A), 121.8 C (0.25 A), 132.6 C (0.3091 A), 144.2 C (0.3726 A), 176.3 C (0.5491 A), 160.1 C (0.46 A); as drawn (1.8329 V)
  153.5, 180.5, 201.9, 261.4 and 231.4 C.
- **The pre-regulator:** 56.2 k over 13.3 k gives 4.0711 to 4.2907 V (my arithmetic on VFB, IFB, 0.1 % and 25 ppm/K over 65 K); 13.3 k
  is the least E96 value that holds T10-A3 (13.7 k gives 3.7487 V against 3.7693 V). Composed on both boards after I-03's drafts; the
  divider reads in my netlist; R602 put back to 10.7 k FAILS.
- **The CAN rows on their own limits:** TCAN334 SLLSEQ7F p.6: 55 mA dominant at 60 Ohm, 60 mA at 50 Ohm, 180 mA dominant with a bus
  fault (TXD 0 V, CANH -12 V, RL open), 3.5 mA recessive; tTXD_DTO 1.2 / 2.6 / 3.8 ms. F13 132.6 C against 125 C (in T10's scope),
  F16 144.2 C against 125 C (a served state), F17 176.3 C against 150 C: each FAILS and is rightly OPEN. The basis sentence is wrong
  (V6-B3).
- **Answer:** the deficit is not corrected on the candidate. K3 holds T10-A2 and T10-A3 on MODEL figures only with T10-A1 **and** a
  transmit-share bound, and the case row still carries the supervisors' HIGH that puts the composed LDOs at 160.1 C; F16 and F17 need
  fault responses traced to CON-004. CONDITIONAL on those four desk items and on T10-A5, not on T10-A1 alone.

### D. The eFuse settings

- **TI TPS2596 (SLVSET8A, the TPS2596xx family sheet naming TPS259631):** 7.3 (p.5) RILM 453 to 7869 Ohm, IMAX 2 A continuous; 7.5
  (p.6) ILIM rows 7.87 k 0.113 / 0.125 / 0.139 A (TA to 80 C), 3.83 k 0.224 / 0.247 / 0.269, 909 0.949 / 1.005 / 1.051, 453 1.83 / 2.004 /
  2.147 A, VDS 0.5 V; Equation 5, RILM = 903 / (ILIM - 0.0112); Figure 21 (p.13, in the typical characteristics, "Across Process,
  Voltage and Temperature Corners") MIN and MAX error curves, about +-10.4 % at 0.125 A and about -5.7 / +4.8 % near 1.2 A, so the
  range-wide +-10.4 % is wider than the curve at both settings (conservative); it is a characterization figure, not a tested row.
- **My bands:** R36 750 Ohm at 1 % and 100 ppm/K over 60 K: corners 738.0 to 762.0 Ohm, 1.0718 / 1.2152 / 1.3632 A; R43 1.21 k: 1190.6 to
  1229.4 Ohm, 0.6682 / 0.7575 / 0.8497 A. Both reproduce.
- **Demand and ratings:** LimeSDR "Maximum Power 4.5 W" (maker's page) at C-DEV's 4.9019 V through 0.131 Ohm and two 30 mOhm contacts:
  0.9534 A, under the foot by 0.118 A; RockBLOCK 9704 "at a maximum of 500mA" (Ground Control), under the foot by 0.168 A; tops 1.3632 A
  under J_LIME's 1.8 A and the switch's 2 A, and 0.8497 A under the 1 A conductor, on printed figures (V6-m4 for the inside air).
- **Start-up:** the 143.6 uF and 8.2 uF allowances are labelled conditions; I did not re-derive them.
- **The inventory:** I listed every U, Q, F and RT value on the composed boards A and B and on the committed C, D, E and P netlists. The
  current-limiting switches are the record's families (TPS259631, TPS25740A, TPS23861, TPS2065C, TPS16630, TPS48110, LM5069); the
  TPS22810s limit nothing (EF-O01 is right); the limiters outside the record's stated scope are BQ4050's protection, BQ25731's input
  limit, the converters' and LDOs' own limits, and the fuses. None was missed within the scope.
- **Credit:** (a) yes on the full board B order (V6-m3: the record's own order is stale); (b) yes (R36 at 301R and R43 at 909R fail my
  check); (c) yes on printed figures, with V6-m4 and V6-m5.

### E. The thermal guard C4

- **The sheets:** JSCJ 2N7002: IDSS 80 nA at 60 V and 25 C, IGSS +-80 nA, threshold 1.0 to 2.5 V at 250 uA, TJ 150 C, every row at
  25 C; LM26LV SNIS144G: trip accuracy +-2.2 C at VDD 5 V only (TA 0 to 150 C), hysteresis 4.5 to 5.5 C, IS 16 uA max, VOH VDD - 0.2 V up
  to 780 uA, tEN 2.3 ms max, VDD 1.6 to 5.5 V (6 V absolute), TJ(MAX) 155 C; TPS709 SBVS186H: VIN 2.7 to 30 V (32 V absolute), EN "can be
  left floating" (300 nA pull-up; "Do not connect EN to VIN", 7.4), +-1 % at VIN 6 V and 1 mA, IGND 2.25 uA max, output capacitor
  2.2 uF or more. The draft's open EN is correct.
- **The window as a ramp:** the sinks on DOCK_EN_RET read on the composed netlists (board A `J_DOCK`, Q44, Q60, R261, U48; board P
  Q103's gate, Q107 over Q108, R107, TP104): 2.00 + 3 x 5.58 + 0.08 = 18.82 uA (24.33 uA all doubled; 80 nA doubled every 10 K to
  86.25 C is 5.58 uA); the return at DOCK_EN_OUT 1.825 V, the pair at +1 % and R107 at -1 %: (1.825 - 18.83e-6 x 15150) x 21780 / 36930
  = 0.908 V (0.859 V), over 0.84 V; allowance 26.45 uA. Reproduced. L4-E11 20c on the candidate is byte-identical to the copy used.
- **The loop:** the first inverter's gate at 7.6 V, my nodal solution 3.13 V, reproduced; the gate network 44.9 ms and 0.955, 0.391 V
  nominal and 0.438 V at tolerances before tEN, 2.5 V in 36.0 ms nominal and 40.0 ms at tolerances, reproduced.
- **No trip:** 127.8 C (130 - 2.2) less record l9stk's junctions 89.4, 118.0 and 121.8 C: 38.4, 9.8 and 6.0 K, the arithmetic
  reproduced; the junctions are RECORD figures resting on E11-29's 33.12 K/W target, not re-derived here.
- **Trip:** 150 - 132.2 - 2.12 = 15.68 K (13.56 K with two FETs), reproduced; a layout and physical condition (E-13).
- **FM1, FM2, the docking times:** reproduced by re-running `l8p_c4.py` (byte-identical output); not re-derived independently.
- **The seven mutations of L9S5-F1,** run by me on my own full composition: the shunt on DOCK_EN_OUT, the open drain used, the regulator
  fed from VBAT, two 15 k, one resistor for the pair, an AO3400A, C260 removed: each reads `THG FAIL`.
- **The 14 single failures:** each row's reading is right as far as it goes; the table is incomplete (V6-m7).
- **Answer:** C-PROT rev 1 holds on the desk for the draft with the conditions listed; this is a positive check of C4, not the second
  negative.

### F. The connected supply path

- **Composition:** my own harness composes board A with 22 drafts (L4-E9's rows, l8gnd's two, l8r2's d8v3, vbus20ov, packrtn, slotlm,
  fb01, l8p's ptc, L4-E11's dd7, then thguard, iocbuck, iocpre, gndrtn, mainpb last, Layer 6's table) and board B with 15 (gnd002,
  fans12, fandec, panel5v, ph4, rt500, gndret, gndrtn, iocbuck, iocpre, u23ilm, u24ilm, Layer 6's three). Every step OK; the generators
  run to their end with intent written; 828 and 1479 parts, no duplicate designator, none unplaced.
- **Checks on that composition:** `check_gndret_netlist.py` declaration and dedicated return DRAWN; `check_l9t5_netlist.py` DRAWN in
  T10 mode, FAIL in its default mode (V6-m1); `check_l8r2_netlist.py` DRAWN (A VCO, D8V3, SLOTS, FB01; B FANS, PNL, PH4);
  `check_gnd002_netlist.py` DRAWN; record l8p's A EN and THG DRAWN; `check_dd7_netlist.py` FAIL on RT1 only (V6-m2); U23 and U24 read
  as drafted.
- **Rail declarations:** board B's GND 13.30 A typical and 27.8159 A peak with nine sources (the three return sockets among them), the
  leads' sum; `+5V_IOC` 4.18 V, 1.38 A on both boards; board A's GND stays the pack return (18.0 A, sources `J_CN1` to `J_CN4`) and
  declares no 5 V return (L8R2-F33). New and changed parts carry no LCSC code (R36, R43, R602, `J_GR1` to `J_GR3`, U60, U61: Layer 6's).
- **Order dependencies:** dd7 before thguard (dd7 refuses afterwards); iocbuck before iocpre; gndret before gndrtn on board B; mainpb's
  designators move with the composition (V6-m11).
- **Claims:** no text on the candidate claims the supply path complete; EXECUTION-PLAN.md line 1603 states it is not, and the four
  records keep L8R2-F31, I-03 and L9T5-F06 OPEN.

## 4. What I reproduced and how

- Re-ran on the candidate, with `TMPDIR` in my scratch and `python3 -B` at nice 19: `l8r2_gndret.py` (30 s), `l9t5_case.py`,
  `l9t5_drafts.py` (26 s), `l9t5_t10.py` (8 s), `l8p_c4.py`: every output byte-identical to the committed one (trailing spaces aside).
- `run.py test_l8p test_l4e11 test_l9t5 test_l8r2 test_l8gnd test_l9pwr test_efuse test_public_hygiene`: `tests: 205 passed, 0 failed,
  0 skipped` (4.5 min wall, nice 19).
- My own composition harness (`scratch/compose_all.py`, record l8p's `gen_netlist.py` as the regenerator) and my own netlist reader;
  the records' checkers run on my netlists; my own mutations (eleven, listed per item).
- My own return solver (`scratch/ret.py`, `ret2.py`, `ret3.py`): independent code from the sheets' figures and the record's lengths and
  sections; the monotone vertex and a brute force over every class-count state; the plane and indirect-path sensitivities.
- My own eFuse band check (`scratch/ilm.py`) from TI's Equation 5, the resistor corners and Figure 21 (read as an image of p.13).
- Read on the makers' sheets: JST VH, Wurth WR-CAB, WR-BHD socket and header, Wurth USB 3.0 A, Amass XT60 V1.2 and 2021V1, TI TPS2596,
  TPS62933, LM5176, TCAN334, LM26LV, TPS709, Diodes AP2112, ST DS12110 Rev 10, JSCJ 2N7002, the LimeSDR page and the RockBLOCK pages.
- Read in the tree: REQUIREMENTS-TRACE.md (REQ-004, REQ-073, CON-004, CON-017), ARCH-PCB-B-IOHA.md sections 12 and 13,
  HW-FW-CONTRACT.md, pcb_interfaces.yaml (IF-BA-RF, IF-MON, IF-LID-HF, IF-AC-MAINSW, IF-AD-HARNESS), L4-E9's change list.

## 5. What I did not check

- No KiCad export, no land (the XT60-F and NGF0006A lands), no routed copper: the plane figures in V6-B1 are a spreading estimate.
- Layer 9's budget (the 36.6251 W and 7.038 W inputs) and C-ALLTX rev 3 / F01: taken as RECORD.
- Record l9stk's junction temperatures and E11-29's thermal impedance; the docking simulation, FM1's cycle and E-13b's bands beyond
  re-running the author's script.
- The resistance and current rating of each indirect A to B path (V6-B2): no held data.
- The start-up allowances of D; the TPS2596's behaviour at VDS other than 0.5 V.
- Anything physical. Compute used: about 6 core-minutes in all, single scripts at nice 19.
