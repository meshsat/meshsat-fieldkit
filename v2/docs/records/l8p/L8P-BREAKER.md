# L8P-BREAKER: W4DP-F2's breaker drawn for boards P, E and A (Layer 8 record l8p)

Record `l8p`, MESHSAT-1357, 4 October 2026, branch `fnd/l8p` from main `64cd25ee`; round 3 on branch `fnd/l8p2` from
`fnd/l8p` at `e1bc3cba`. The author is board P's generator author for this one correction and, since round 2, DD-8's owner.

**Status: DRAFTED, not applied.** Three release-guarded apply scripts, a netlist check and their proof on scratch copies.
Nothing in this kit has been built, bought, powered or measured. Every apply script refuses the repository's own generator
until a `RELEASE.md` beside it reads `released: yes` and names an accepted check of this record; none exists.

**Round 2 (4 October 2026, the coordinator's second round).** The protection record moved after round 1: record `l9stk` at
`0d72880b` (sections 15.4, 15.4b, 15.6, 15.7 and 15.8). Its latest changes were checked CONFIRMED AS CONDITIONAL. Board P's
draft now draws three changes:
1. **The breaker is the latch-off LM5069-1**, not the -2: the -2's retry overheats its own FET under a persistent fault (15.4b).
2. **C-1c, the restart inhibit on the breaker pad (DD-8):** an NTC bridge, a comparator gated by PGD, acting on UVLO (15.4b).
3. **The undock path:** the hold reaches UVLO through 150 ohm and a 1N4148W, and the second inverter pulls UVLO directly
   (15.4). The turn-off is 0.41 ms; the hold is 0.110 to 0.907 s.

The checker's conditions on DD-8 are written into the draft and into section 4 below: the budget allocated by part choice, the
NTC's tolerance marked as assumed, the commissioning check E-12b, the NTC bonded to the pad, the E-10 line, and the lockout at
the allow edge. L8P-F01 is closed (section 9).

**Round 3 (4 October 2026, B-R2's remainder; section 12).** Task L4-E11's round 9 (`fnd/l4e11r9` at `e60a94a8`, section 19h)
left B-R2 open: a latch while a source holds VSYS keeps CELL+ alive, so board A's hardware inhibit never sets, PGD reads good
with the reverse current, and a charge over the latched FET's 1.405 A rested on the firmware. **Route R1 is SELECTED and drawn
on board P:** a reverse-charge detector (U103 and U104, two more OPA187s) holds the enable loop's return DOCK_EN_RET low while
the breaker's body diodes pass a charge into the cells over 0.368 to 1.213 A. That return already reaches board A on J_DOCK pin
3: **no new contact.** Board A's inhibit must read it (the interface of section 12f, owed to L4-E11's DD-7 draft, finding
L8P-F04).

**The defects** (record `l9stk` section 15):
- DD-1: with board P's FETs Q1 and Q2 welded and no firmware, nothing on board P opens the discharge path on current alone
  (15.2).
- DD-6: a docking with a breaker that is already on reaches E11-30's 242.9 A, past the breaker FET's SOA and past VIN to
  SENSE's 0.3 V maximum (15.4, B-P1).
- DD-8: a hot restart of the -1 into the worst resistive fault on VSYS reaches 0.82 of the derated SOA at the held 101.0 C
  case, past TI's margin (15.4b, B-R1).

**The design drawn** is l9stk's, unchanged:
- C-1: an LM5069-1 circuit breaker on board P, from Q2's source to the pack terminal.
- C-1b: a make-last dock enable loop into its UVLO, with an RC hold through a diode.
- C-1c: a restart inhibit on the breaker pad, gated by PGD.
- 15.5: the thermal guard, a PRF15BB103 PTC in the enable loop on the battery FETs' copper on board A.

Every value comes from the record by its section (section 2). Where the record leaves a choice to the drawing, it is taken
here as SESSION under the owner's standing rule of 26 September 2026 (section 3). The record's own copies are in `inputs/`,
pinned by `inputs/SOURCES.txt`.

## 1. The three drafts

| Draft | Board | What it draws |
|---|---|---|
| `apply_gen_sch_p_breaker.py` | P | The breaker U101 (the -1) with its sense pair, FETs, power limit, timer, dv/dt capacitor, input clamp and input bypass. The enable loop's two inverters and the RC hold through R105 and D102. The restart inhibit: RT101 on the pad, its bridge and reference, the comparator U102, the PGD gate Q105 and Q106. Round 3: the reverse-charge detector (B-R2, section 12): U103 on R10's charge with its zener-held reference (R129, D103, R118, R119), U104 on the FETs' reverse VDS (R121 to R124), Q107 and Q108 in series on DOCK_EN_RET, C107 to C110, R120, R125 to R128. J_SMB as a 1x7 with the loop on pins 5 and 7 and the return on pin 6. The gauge's PACK and VCC taps and Q2's R19 moved to Q2's source (IF-6). PACK_P re-declared as the breaker's output. Eight test points for E-12, E-12b and E-12c. One schematic section. |
| `apply_gen_sch_e_enable.py` | E | J_SMB as the same 1x7, pin for pin. J_BLK pins 3 and 5 carry the loop to the block, with pin 4 ground between them. The loop's two nets declared. Board E is a pass-through: no part. Unchanged in round 2. |
| `apply_gen_sch_a_ptc.py` | A | J_DOCK pins 3 and 5 carry the loop, with pin 4 ground between them. RT1, the PRF15BB103, closes the loop on the battery FETs' copper. The loop's two nets declared. Round 2 changed only its comment (the -1). |

Each draft:
- checks by default and writes only with `--write`;
- asserts that every text it replaces occurs exactly once and that its new text is not yet present;
- refuses a designator or net that is already in use, and refuses a second application;
- re-parses the result;
- refuses the tree's own generator while unreleased.

The E and A drafts change J_BLK's and J_DOCK's maps after each part's call, as board P's generator renames its gauge pins.
That leaves the call itself to L4-E11's drafts, which edit pin 1 of the same call, and the post-edit refuses if pins 3 to 5
are no longer all ground.

## 2. The values, each with its l9stk source

| Ref | Value | l9stk source (`0d72880b`) |
|---|---|---|
| U101 | LM5069MM-1, the latch-off variant; VSSOP-10, the land of board E's U6 (its -2 is C111822). **The -1's order code is OWED to Layer 6.** | 15.4, C-1: "an LM5069 circuit breaker on board P, the -1 (latch-off, 15.4b)"; 15.4b "SELECTED: the -1 (latch-off)" |
| R101 | 4 mOhm 1 % 2512, at most 50 ppm/K | 15.4 table, Sense RS: "4 mOhm and 7.5 mOhm in parallel, 2.6087 mOhm, 1 % and at most 50 ppm/K" |
| R102 | 7.5 mOhm 1 % 2512, at most 50 ppm/K | as R101 |
| Q101, Q102 | CSD18510Q5B, LCSC C2876544 (board A's PA stage part), PowerPAK SO-8 | 15.4 table, FETs: "2 x CSD18510Q5B" |
| R103 | 8.45 kOhm 1 % (RPWR) | 15.4 table, Power limit: "RPWR 8.45 kOhm" |
| C101 | 10 nF 50 V X7R (TIMER) | 15.4 table, Fault timer: "10 nF" |
| C102 | 22 nF 50 V X7R (GATE to the return, dv/dt) | 15.4 table, dv/dt start: "22 nF into 593 uF" |
| D101 | SMCJ18A, LCSC C374030 (board A's VBAT clamp part), cathode on BRK_VIN | 15.4 table, Clamps: "SMCJ18A on VIN"; IF-6: it returns to PACK_N |
| R104 | 200 kOhm 1 % (R_U, BRK_VIN to the hold's node BRK_H) | 15.4 C-1b, the hold: "R_U, the series resistor (200 kOhm from VIN), charges C_U on a node H" |
| C103 | 3.3 uF 50 V X7R (C_U, BRK_H to the return) | 15.4 table, Controller: "into C_U 3.3 uF (50 V)" |
| R105 | 150 ohm (BRK_H to D102's anode) | 15.4 C-1b, the hold: "H reaches UVLO through 150 ohm and a 1N4148W" |
| D102 | 1N4148W, LCSC C81598 (the held ST/Semtech sheet), SOD-123, cathode on UVLO | as R105; its 107 mA peak is 0.11 of its 1 A 1 ms surge and 0.71 of its 150 mA average |
| R106 | 10 kOhm (BRK_VIN to the loop) | 15.4 C-1b: "The loop leaves board P from VIN through 10 kOhm on one J_SMB contact" |
| R107 | 22 kOhm (the loop's return to the return) | 15.4 C-1b: "a 22 kOhm divider on a first 2N7002's gate" |
| Q103 | 2N7002 (JSCJ, C8545), the first inverter | 15.4 C-1b |
| Q104 | 2N7002, the second inverter, drain on UVLO | 15.4 C-1b: "the second, when on, pulls UVLO itself" |
| R108, R109 | 1 MOhm each (the second inverter's gate divider) | `l9stk_protection.py` constant R_G, "the second inverter's gate divider, each half": the one value the page does not print |
| RT101 | Murata NXRT15XH103FA1B010: 10 kOhm 1 %, B25/50 3380 K 1 %, B25/85 3434 K (a reference value), 10 mm leads. **Its order code is OWED to Layer 6.** | 15.4b C-1c: "The kit's NTC sheet part, Murata NXRT15XH103FA1B" |
| R110 | 150 kOhm 0.1 %, at most 25 ppm/K (over the NTC, from BRK_VIN) | 15.4b C-1c: "The bridge has 150 kOhm over the NTC: 0.111 mA at most, against its 0.12 mA" |
| RT1 (board A) | PRF15BB103RB6RC, Murata, LCSC C443668 (board P's RT1 part and 0402 land) | 15.5, THE THERMAL GUARD: "the kit's PRF15BB103 chip PTC ... In the enable loop on the battery FETs' copper" |

**The window** (15.4b): allow from 77.25 C, block from 83.20 C, trip 80.22 C plus or minus 2.97 K, the NTC at 1653 ohm. The
NTC takes plus or minus 1.02 K, which leaves plus or minus 1.95 K.

The connections are the record's too:
- OVLO to the return (15.4, the controller row).
- The clamp, the controller and its small parts return to PACK_N (IF-6).
- D1 stays on PACK_P and carries the lead's freewheel at turn-off (15.4, the clamps row).
- The gauge's PACK and VCC taps stay on Q2's source node (IF-6).
- A ground contact sits between the loop conductors in J_SMB and on the block (C2).
- The inhibit's bridge is ratiometric from VIN, and it acts only while PGD is low (15.4b).

`l8p_drafts.py` section 2 finds each row's text in the copy of the record and refuses when a phrase no longer matches. The
netlist check reads each value prefix back from the regenerated netlist.

## 3. The SESSION choices (what the record leaves to the drawing)

| Choice | Taken | Why |
|---|---|---|
| Designators | Board P: the free 100 block (U101, U102; Q101 to Q106; D101, D102; RT101; R101 to R117; C101 to C106; TP101 to TP106). Board A: RT1. Board E: none. | A block no other draft of board P uses, so a later draft that takes the next free number cannot meet it. Board A carries no RT designator. |
| Net names | BRK_VIN (Q2's source, the breaker's input), BRK_SNS, BRK_GATE, BRK_TMR, BRK_PWR, BRK_UVLO, BRK_G2, BRK_H, BRK_HD, BRK_PGD, BRK_CMID; INH_NTC, INH_REF, INH_OUT, INH_G. DOCK_EN_OUT and DOCK_EN_RET on all three boards. | The dock contract (`check_contracts.py` section 4) compares J_DOCK and J_BLK by net name. |
| J_SMB | A JST-XH 1x7 (B7B-XH-A, the same header row of the held catalogue) at both ends. Pins 1 to 4 unchanged (SMBC, SMBD, the return, PRES). 5 DOCK_EN_RET. 6 the return. 7 DOCK_EN_OUT. | The record asks for two loop conductors on J_SMB with a ground contact between them, and PRES stays. Keeping round 4's order needs three new positions, so the lead gains contacts 5 to 7, not one. DOCK_EN_OUT, the conductor at BRK_VIN through 10 kOhm, sits at the row's end beside ground only. DOCK_EN_RET sits beside PRES: a short there pulls the gate side, and never puts BRK_VIN on an unpowered board E's GPIO17. |
| Dock positions | J_DOCK and J_BLK pins 3 (DOCK_EN_RET) and 5 (DOCK_EN_OUT), with pin 4 ground between them in the 2 x 6 field's first row. | These are the only two free ground positions in one row with a ground between them where the outgoing conductor has no signal neighbour: pin 5's neighbours 4, 6 and 11 are ground. Pin 3's neighbour below is USB_E6_P (pin 9); see section 10. |
| Input bypass | C104 and C105, 2.2 uF 50 V X7R in series through BRK_CMID (1.1 uF), at the sense pair. | IF-2 asks for "VIN's bypass at RS (the sheet's 11.1)". TI SNVS452G section 10: "TI recommends placing a 1-uF ceramic capacitor to ground close to the drain of the hot swap MOSFET". 11.1.1: "place the bypass capacitor close to Rsns instead of the VIN pin". It is drawn in series, as C11 and C12 are (O-12; SLUSC67B 8.2.2.1.5), because one shorted part across the pack must not short it. |
| The comparator | U102, TI OPA187IDBVR (SOT-23-5), a zero-drift amplifier on BRK_VIN used as the comparator: +IN on the reference, -IN on the NTC, so its output is high while the pad is hot. C106 100 nF at its V+ (class D, the sheet's 10.1). **Its order code is OWED to Layer 6.** | The checker asked for a zero-drift amplifier or a comparator with about 1.5 mV of offset or less over board P's temperature, from a held or fetched maker sheet with its offset over temperature read. TI's SBOS807E is fetched by `fetch_held_back.py` into `v2/vendor/ti/held/` (held back by TI's notice, as l4e11 and l8r2 hold theirs) and read by `l8p_drafts.py`. It gives 4.5 to 36 V of supply (40 V absolute) against BRK_VIN's 29.2 V clamp, an input range from 0.1 V under its negative rail (the bridge sits at 0.12 to 0.18 V at the trip), no phase reversal, and back-to-back input diodes that the bridge's 150 kOhm keeps far under their 10 mA. |
| The reference | R111 147 kOhm over R112 1.62 kOhm, both 0.1 % and at most 25 ppm/K, from BRK_VIN as R110 is: 1653.06 ohm equivalent against the trip's 1653. R113 15 MOhm 1 % from U102's output to the reference: 0.36 K of hysteresis, 0.363 K at most. | The ratio is the record's trip, from two E96 values. The hysteresis stays under the checker's 0.5 K. |
| The PGD gate | U101's PGD (open drain, high when VDS is under 1.25 V) sits on BRK_PGD at half BRK_VIN through R116 and R117 (1 MOhm each). Q106 holds Q105's gate low while PGD is high. R114 and R115 (100 kOhm each) halve U102's output onto Q105's gate (14.6 V at most against 20 V). Q105 pulls UVLO, as Q104 does. | The record: "gated so that it acts only while PGD is low ... It never acts on a running breaker". Pulling UVLO resets the -1's latch, and the breaker restarts through the hold once the pad cools under the trip. |
| Test points | TP101 BRK_VIN, TP102 BRK_UVLO, TP103 DOCK_EN_OUT, TP104 DOCK_EN_RET (E-12); TP105 INH_NTC, TP106 INH_OUT (E-12b); TP107 REV_IOUT, TP108 REV_VOUT (E-12c). | E-12's commissioning steps, E-12b (section 4) and E-12c (section 12g). |
| The reverse-charge detector (round 3) | U103 and U104, U102's part (OPA187IDBVR). U103: +IN on R10's cell side (GND) through R120 200 ohm with C109 470 nF; -IN on R118 1.15 MOhm over R119 200 ohm (0.1 %, at most 25 ppm/K) from REV_VZ, which is BRK_VIN through R129 47 kOhm under D103 (BZT52C12-7-F, board A's D25 part, C124196). U104: +IN on PACK_P over R121 332 kOhm and R122 33.2 kOhm; -IN on BRK_SNS over R123 328 kOhm and R124 33.2 kOhm (0.05 %, at most 10 ppm/K); C110 1 nF across. Q107 and Q108 (2N7002) in series from DOCK_EN_RET to the return, gates at half of each output (R125 to R128, 100 kOhm). C107 and C108 their bypass (class D). | Section 12b: the charge is read where it enters the cells, so a sleeping gauge's wake (mA) never trips it; the reverse VDS tells a latched FET from a running one; the zener caps the threshold under the FET's 1.405 A at the pack's top while the floor stays over the LDO-mode precharge. |
| Lands | VSSOP-10 (as board E's U6), SMC (as board A's D1), SOD-123 for D102, SOT-23-5 for U102, 2512 for the sense pair, PowerPAK SO-8 for the FETs, the 7-circuit XH header, board P's 0402 for RT1; RT101's 10 mm leads on the project's `LeadLands_1x02`. | The kit's own lands. RT101's body is bonded on the pad, and its leads are soldered to two lands beside it. |

The coordinator's first brief named "a fifth J_SMB contact". The record's text (two J_SMB contacts with a ground between,
DD-6's owner row and C2) is what is drawn: three new positions, 5 to 7.

## 4. C-1c's conditions: the budget, the NTC, E-12b, E-10 and the lockout (DD-8; `l8p_drafts.out` section 3)

**The plus or minus 1.95 K, allocated by part choice.** Each figure is computed by `l8p_drafts.py` from the drawn values and
the makers' sheets; none is typed.

| Term | How it is bounded | Allow side | Block side |
|---|---|---|---|
| The comparator, U102 OPA187 | Read from SBOS807E's high-voltage table: VOS 10 uV, drift 0.015 uV/K to 125 C, IOS 14.5 nA and IB 7.5 nA over temperature through the bridge's 1.6 kOhm, PSRR 1 uV/V over 10.6 to 29.2 V. That is 54.1 uV in all, against the NTC node's 3.143 mV/K at the trip and the least 10.6 V. | 0.017 K | 0.017 K |
| The bridge and reference resistors | R110, R111 and R112 at 0.1 % and at most 25 ppm/K, anywhere between 25 C and the held 101.0 C case (0.29 % each), at the worst of all signs | 0.317 K | 0.317 K |
| The NTC's own heating | 0.111 mA in 1653 ohm against Murata's 1.5 mW/K dissipation constant; it reads hot | 0.014 K | |
| The hysteresis | R113 15 MOhm, the output rail to rail, the parts at their tolerances | 0.363 K | |
| The drawn trip against the record's | 1652.88 ohm against 1653 (sits hotter) | | 0.003 K |
| **Left for the pad-to-NTC gradient (E-15)** | | **1.240 K** | **1.614 K** |

The split closes: the gradient keeps more than the checker's 0.9 K on both sides; the comparator uses 0.017 K of the 0.47 K
allowed and the hysteresis 0.363 K of the 0.5 K allowed. The resistors take more than the checker's example of 0.07 K, because
their temperature coefficient over 76 K is counted; the comparator's margin covers that. An LM393 alone would use 2.2 to 2.8 K
(the checker's figure), more than the whole budget, and is not used.

**The NTC's tolerance at 80 C is ASSUMED.** The held Murata sheet is a product search sheet: B25/85 is printed as a reference
value, and the B tolerance is printed only at 25/50. The record's plus or minus 1.02 K is to be confirmed by Murata's approval
sheet or by E-15.

**An open or detached NTC reads cold and silently removes the inhibit.** U102's output then stays low and the inhibit never
acts. Two measures are drawn and owed:
- **The NTC is bonded to the pad.** RT101's body is bonded on the breaker FETs' pad with an electrically insulating,
  thermally conducting adhesive over the pad's solder mask (the pad is BRK_SNS, about BRK_VIN). Its 10 mm leads go to two
  lands beside it. The adhesive and the process are Layer 6's and Layer 7's.
- **E-12b, a commissioning check like E-12** (at commissioning and at each service, the supplier's procedure):
  - read TP105 (INH_NTC) against TP101 (BRK_VIN) at the ambient;
  - the ratio is R_NTC/(150 kOhm + R_NTC) from the sheet's R25 and B25/50: 0.0625 at 25 C;
  - a ratio near 1 is an open or unsoldered NTC (the inhibit silently gone), near 0 a short (the breaker held off);
  - TP106 (INH_OUT) reads low at the ambient;
  - a detached but connected NTC is found only by E-15's heated specimen.

**E-10's line gains:** VDS under 1.62 V during current-limit excursions. PGD then stays high, so the inhibit stays gated and
never turns off a running breaker.

**The lockout at the allow edge.** A unit tripping at 77.25 C needs its pad within 1 K of a 76.25 C inside air before it
restarts. At that air the cells' hot stop has already shut the kit down.

**The cost**, as the record states: a quick redock, or DD-7's pulse, after heavy use waits for the pad to cool. That time is
NOT HELD (E-15).

## 5. Designators per draft (`l8p_drafts.out` section 6)

| Board | This record's | Against every other draft of the board, composed in L4-E9's order |
|---|---|---|
| P | U101 to U104, Q101 to Q108, D101 to D103, RT101, R101 to R129, C101 to C110, TP101 to TP108 | DISJOINT (l6r2's two board P drafts add none) |
| E | none (nets only) | DISJOINT |
| A | RT1 | DISJOINT (L4-E4 to L4-E11, l8gnd, l8r2, d8dec31's mainpb, l6r2) |

No literal part call is drawn twice in any composed generator.

The third battery FET of 15.5 (SELECTED) is **not drawn here**: its designator is L4-E11's to give, since Q41 is record
l8r2's VIN_RAW cut-off FET.

## 6. Order constraints for L4-E9's change list

1. **One release for the three drafts.** P, E and A are released and applied together, never one alone.
   - `check_contracts.py` section 15c compares J_SMB at both ends: family, pitch, pin count and roles.
   - Section 4 compares the dock's 2 x 6 map on J_DOCK and J_BLK.
   - Either check fails when only one end has changed.
2. **Board P: a new round.** No board P circuit change is in the list today, apart from U-01's R-105, which is undrafted and
   only under approach (II).
   - The breaker draft goes into board P's round with l6r2's two board P tables, in either order (both shown).
   - R-105, when drafted, must leave U101, Q2's source and J_SMB as this draft leaves them.
   - Board P's regeneration on the box follows.
3. **Board E: step 4e, any position.**
   - No other board E draft touches J_SMB, the J_BLK pins this one moves, the line it inserts before, or the section title.
   - Shown after L4-E11's aux (R-177) and before d8dec31's cin (R-16, step 4f), and also first and last.
   - The composition uses L4-E7's backstop draft of `fnd/l4e7r6` at `914a2f5a` (copied byte for byte into `inputs/`), which
     closes L8P-F01; when it reaches main, main's draft is that one.
4. **Board A: step 3, any position.**
   - It inserts before two lines that l8gnd's GND-002 draft also inserts before (each keeps the line once).
   - It replaces no text L4-E11's charger (R-157) replaces.
   - It adds no R or C, so d8dec31's mainpb (R-193, 3h) still takes R248 and C247.
   - Shown after 3g and before 3h, and also first and last.
5. **Before P and E are regenerated and judged:**
   - `check_contracts.py` section 15c's role table needs a role for the loop's two nets (owed to the tools owner, section 7).
     Without it, P's J_SMB pins 5 and 7 read "unknown" and the contract fails.
   - Layer 5's interface rows go in the same release (section 7).
6. **The layout follows the schematic.** The board P PCB generator draws IF-2, the bands and RT101 on the pad; board A's
   places RT1; board E's places the 7-way land (section 7).
7. **Record l8r2's later rounds** (branch `fnd/l8r3` at `89924e40`, not on main) were checked once in round 1 on scratch
   copies, outside the script: board A's fb01, slotlm and packrtn and board E's packrtn compose with this record's E and A
   drafts, before and after them. Round 2 did not change those two drafts' anchors.
8. **The regeneration steps R-11 and R-22 are blocked today by two other drafts' run-time refusals** (section 9), with or
   without this record. This record adds no refusal: with scratch stand-ins for those two, the composed generators run to
   their end and the loop reads DRAWN.

## 7. Interface rows owed

| Owner | Row |
|---|---|
| **Layer 5** (IF-PE-PACK, `pcb_interfaces.yaml`) | **The fifth to seventh J_SMB contacts:** J_SMB at both ends a JST-XH 1x7 (B7B-XH-A): 1 SMBC, 2 SMBD, 3 GND (the pack side of the shunt), 4 PRES, 5 DOCK_EN_RET, 6 GND, 7 DOCK_EN_OUT. The lead is a straight 7-way XH-to-XH lead. Pin 6's second ground wire runs in parallel with the 12 AWG return as pin 3's does (O-5, a harness matter). |
| **Layer 5** (IF-AE-DOCK) | **The dock enable contacts:** J_DOCK and J_BLK pin 3 DOCK_EN_RET and pin 5 DOCK_EN_OUT, with pin 4 GND between them; the E5 block passes each contact to its own wire. |
| **Layer 5** (IF-5; CONOPS, with the battery stream) | **PACK_P live only while docked:** the pack's terminal is dead whenever the enable loop is open. Any host other than the dock must close the loop through its own path or gets a dead terminal (fail-safe). Board A's J_PRE1 and R1 are no longer exercised at docking. |
| **Layer 7** | **The make-last contact's 1 mm (C1):** J_DOCK positions 3 and 5 mate at least 1 mm after every power pin (J_CP1 to 4, J_CN1 to 4, J_VR1 to 4, J_VN1 to 4) at any angle the dock's guides allow. The RC hold tolerates a reversed order up to 111.6 ms; beyond that, the order is Layer 7's condition. If the Preci-Dip 813 strip cannot be set 1 mm short as a whole, those two positions take separate shorter pins (a board A land change, with board A's generator). |
| **Layer 7** | **The mating order C1, both ways:** at undocking the gate is low 0.41 ms after the loop opens, so the enable parts first at a withdrawal under 2.42 m/s (the round 1 hold took 1.51 ms, 0.66 m/s). Also the open dock: E5's flat targets with the ground target between the two enable targets (C2's "on the block"). |
| **L4-E11** | **The third battery FET's designator** and land (15.5, SELECTED; condition C3), and RT1's place on the three FETs' copper. |
| **L4-E11** (with board A's generator) | **IF-1, critical to the service under the -1:** a start that meets the power limit latches the breaker. Board A's loads on VSYS stay off, under 0.81 A at full VDS, until the breaker's start ends: up to 40.7 ms after the gate rises, and so up to 0.907 s after the enable mates. Or they follow the breaker's PGD; PGD is now drawn on BRK_PGD for the inhibit, and taking it to board A needs a conductor from board P (a J_SMB and dock contact), which comes back to this record. |
| **L4-E11** (with board A's generator) | **DD-7, the input-return pulse:** board A opens the enable loop for a pulse when an input appears, so the -1's latch resets. It sits in the loop on board A, in series with RT1 between J_DOCK pins 5 and 3 (DOCK_EN_OUT and DOCK_EN_RET), so it composes with this record's A draft. |
| **L4-E11** (with board A's generator) | **B-R2's interface, route R1 (section 12f, finding L8P-F04):** board A's charge inhibit sets while DOCK_EN_RET is under 1.0 V and DOCK_EN_OUT is at 2.0 V or over, whatever CELL+ reads, within 1 ms; it holds at least 1.0 s after DOCK_EN_RET rises over 2.5 V, then releases on CELL+ alive as now. Board A loads DOCK_EN_RET with 1 MOhm or more. No new contact: J_DOCK pin 3. E-14 as it now reads (section 12g) and E11-45 (c2)'s acceptance. |
| The firmware owner | **IF-7:** the bridge reports a tripped breaker (the pack's terminal dead while the gauge's FETs are on) and enables charging only after the breaker's restart; recovery on battery is redocking. |
| Layer 6 (L8P-06) | **Order codes owed:** the LM5069-1 (U101; the -2's C111822 is not it); the OPA187IDBVR (U102, and U103 and U104 in round 3); the NXRT15XH103FA1B010 (RT101); the 7-way J_SMB at both ends, pinned in the generators as R8P-02 pinned the 4-way C144395, so no fill decides it (`lcsc_fill.py`'s rule `SMBus lead.*JST-XH 1x4` no longer matches). |
| Layer 6 | E-6 for the sense pair: 2 W each at the band's temperature, at most 50 ppm/K. R110, R111 and R112 at 0.1 % and at most 25 ppm/K (the budget of section 4 rests on it); R113 15 MOhm 1 %. C103's capacitance at its 0 to 2.55 V charge within the record's 10 % (the hold's 0.110 s least). R105 and D102's single pulse at each undocking and each inhibit pull (C_U from 16.8 V through 150 ohm, about 0.47 mJ, 107 mA peak). RT101's bonding adhesive: electrically insulating, thermally conducting, to 125 C. Codes for the new passives. Round 3: R121 to R124 at 0.05 % and at most 10 ppm/K, R118 and R119 at 0.1 % and at most 25 ppm/K (section 12c rests on them); **R10's tolerance and temperature coefficient** (the gauge's 2 mOhm sense: the generator prints neither; section 12c takes 1 % and 75 ppm/K, ASSUMED); R129's temperature coefficient (100 ppm/K ASSUMED). |
| Tools owner | `check_contracts.py` 15c: a role for DOCK_EN_OUT and DOCK_EN_RET, equal at both ends, before the regenerated P and E are judged. `gen_pcb_e5.py`'s silk table `SHORT` gains the two nets (the block's land labels read "?" otherwise; cosmetic). |
| Board P's PCB generator (`gen_pcb_p3.py`) | **Round 3:** U103's sense by Kelvin taps from R10's two pads (R120's trace from the GND pad; U103's V-, R119 and C109 at the PACK_N pad), as the gauge's SRP and SRN are taken; U104's dividers from the FETs' own drain and source pads (BRK_SNS and PACK_P at Q101 and Q102), so no band drop adds to the reverse VDS; U103 and U104 away from the pad. **IF-2:** each breaker FET's installed RthJA at most 52.5 C/W (1 in2 of 2 oz each gives the sheet's 50). The area budget is two 1 in2 pads, 1290 of the 2084 mm2 left, 793 mm2 for the rest. U101 sits beside the sense pair with Kelvin taps (E-9). C104 and C105 sit at the sense pair. RT101 sits on the FETs' pad with its two lead lands beside it; U102 and its bridge sit away from the pad. Q2's source band becomes BRK_VIN, and the PACK_P band runs from the breaker FETs' sources to W_P. |
| The integrator | IF-3: a stage for the breaker in `pcb_energy_chain.yaml` between PACK_FETS and PACK_LEAD (its limit 23.93 A). |
| The l9stk register's owner | E-10's line gains VDS under 1.62 V during current-limit excursions; E-12b (section 4) joins E-12; E-15 measures the pad-to-NTC gradient against section 4's 1.24 K. Round 3: **E-14 as it now reads** and E-12c (section 12g); **a fourth recovery of the -1** (15.4b lists redocking, an input's return and the guard's cycle): a charge over the detector's threshold through the off breaker resets it, and it restarts after the hold with board A's battery FETs held off (section 12b). |
| The battery stream | Round 3: the detector draws 0.47 mA from BRK_VIN at 16.8 V (two OPA187s, the reference's feed, the dividers), a standby load on the pack beside U101's and U102's. |

## 8. Regeneration on the runner and the netlist check (`l8p_drafts.out` section 7)

**KiCad.** The schematic generators place every part through `kisch` without KiCad. Their layout and symbol step
(`schlayout`, KiCad's symbol libraries) and the netlist export (`kicad-cli`) need KiCad, which is only on the box. The box
was not started.

**`gen_netlist.py`** runs a scratch copy of a generator to its end with a stand-in layout:
- it records `kisch`'s part table and writes it in KiCad's netlist form;
- `intent.write` runs, so the generator's own checks of rails, sources, loads, nodes and bypass entries are taken (C106's
  class D entry among them).

**Its fidelity.** On the unpatched generators it reproduces the committed KiCad netlists of boards P, E and A:
- every connected pin is on the same net;
- every footprint is the same;
- the only differences are KiCad's own names for open pins.

**Results of `check_l8p_netlist.py`:**

| Netlist | Reading |
|---|---|
| The committed netlists | NOT DRAWN on all three |
| P, E and A each with this record's draft alone (the generators ran to their end) | DRAWN on BRK, EN, INH and REV; the LOOP across the three boards DRAWN |
| Board P composed in L4-E9's order | DRAWN on BRK, EN, INH and REV |
| Boards E and A composed in L4-E9's order | the generators refuse on other drafts' defects (section 9); with scratch stand-ins for those, DRAWN, LOOP DRAWN |
| Five mutated netlists (P's J_SMB pins 6 and 7 exchanged; A's J_DOCK pins 3 and 4 exchanged; P's Q105 and Q106 gates exchanged, so the inhibit is no longer gated by PGD; round 3: U104's inputs exchanged, so the detector reads a forward drop; R120 moved to PACK_N and R119 to GND, so U103 no longer reads R10) | FAIL |

The check parses the netlists and reads the dock lands' pad positions from `meshsat.pretty`. It holds:
- the breaker's nets and values, U101's PGD on BRK_PGD;
- the enable loop on each board, and the hold through R105 and D102 with Q104 on UVLO;
- the restart inhibit: the bridge and the reference both from U101's VIN, U102's inputs, Q105 on U101's UVLO, Q106's gate on
  U101's PGD and its drain on Q105's gate, RT101 on the lead lands, the values;
- the ground contact between the loop conductors, on J_SMB (by position along the row) and on J_DOCK and J_BLK (a ground
  pad at the midpoint of the two loop pads);
- the loop's continuity from BRK_VIN through R106, the lead, the dock and RT1 back to Q103's gate;
- round 3, REV, the reverse-charge detector: U103's +IN on R10's cell side through R120 and its -IN on the zener-held reference
  (R129 from U101's VIN, D103's cathode, R118 over R119), U104's +IN on PACK_P's divider and its -IN on BRK_SNS's, with the
  -IN divider's ratio over the +IN's (so PACK_P must exceed BRK_SNS), Q107's drain on Q103's gate net (the loop's return) and
  Q108's source on the return with REV_MID on the two alone (in series), both supplies on U101's VIN with C107 and C108, the
  values.

**Owed on the box:**
- the regenerated schematics with ERC and the KiCad netlist export;
- the label grid matter of Q2's renamed source (board P's comment at SCP_OUT records one);
- the 7-circuit XH and SOT-23-5 lands read from KiCad's library.

## 9. Findings for other authors (run-time refusals no text-level composition test reads)

| Finding | Board | Owner | What stops the composed generator | State |
|---|---|---|---|---|
| L8P-F01 | E | L4-E7 (`apply_gen_sch_e_backstop.py`) | Its decoupling entries C66 (U18 pin 5), C67 (U19 pin 5) and C68 (U20 pin 6) carried no G14 class, and `gen_sch_e.py` refused. | **CLOSED** by L4-E7's `fnd/l4e7r6` at `914a2f5a` (class D with each maker's clause). The composition uses that draft; its stand-in is dropped. |
| L8P-F02 | A | L4-E11 (`apply_gen_sch_a_charger.py`) | VSYS_DOCK names U42 as its source without `source_ic`, which `intent.rail` refuses. With that passed, it is fed from VBAT before VBAT is declared, which is refused too. Board A's composition stops at step 3a. | open |
| L8P-F03 | E | L4-E11 (`apply_gen_sch_e_aux.py`) | +12V_FAN names L4 as its source, and L4 is not on that net (it sits between F12_SW1 and F12_SW2). `intent.write` refuses. | open on main; L4-E11 reports L8P-F02 and L8P-F03 corrected on `fnd/l4e11r9` (`b985797a`, round 9), not checked here |
| L8P-F04 | A | L4-E11 (`apply_gen_sch_a_dd7.py`) | Not a refusal: B-R2's interface (section 12f). The DD-7 draft reads the loop powered at half of DOCK_EN_OUT (Q47 through R109 and R144). With the return held low (board P's detector, or board A's own Q44), DOCK_EN_OUT falls to 2.52 V at BRK_VIN 7.6 V and 3.51 V at 10.6 V, so Q47's gate reads 1.26 and 1.75 V, under the 2N7002's 2.5 V; and nothing on board A reads DOCK_EN_RET. | open, owed |
| L8P-F05 | A | L4-E11 (`apply_gen_sch_a_dd7.py`), with record l9stk | Not a refusal. With the breaker off, the LM5069 feeds PACK_P, and so CELL+, through its internal 1 MOhm from SENSE to OUT (SNVS452G 7.5, note 1). With board A's 200 kOhm (R107, R108) alone, CELL+ reads 2.80 V at BRK_VIN 16.8 V, over the DD-7 draft's 1.98 V 'dead' point, so Q48 may release the inhibit while the breaker is off. With this record's U104 divider (365.2 kOhm) also on PACK_P it reads 1.92 V, but 3.34 V at the 29.2 V clamp, and the 1 MOhm's tolerance is not printed. The 'dead' reading should not lean on it: a load of board A's own on CELL+, or a threshold that reads such a level as dead. Route R1's return covers a charge either way. | open |

Each open refusal is the same without this record's draft. The stand-ins in `l8p_drafts.py` (STANDINS) are scratch text
only, never drafts and never applied. They say only that the generator then runs on.

## 10. Residuals of the drawing (for the record's owner; no new defect)

- **A short of DOCK_EN_RET to a neighbour.**
  - The neighbours are PRES on J_SMB (pin 4) and USB_E6_P on the dock (pin 9, below pin 3).
  - The current is bounded by R106 10 kOhm, RT1 and R107.
  - The gauge's PRES pin's absolute maximum is 30 V (SLUSC67B 6.1). Board E's GPIO17 sits behind R54 1 kOhm, and its USB
    pair behind its own series resistors.
  - The breaker may stay on or go off. Either way the pack path keeps its current limit.
- **A shorted C101 (TIMER held at the return) while the breaker is on, with an overload afterwards** (two faults). The
  fault timer cannot end the current or power limit, and the power limit holds the FET past its DC line. Whether the
  insertion delay then keeps the breaker off at the next start by the gauge's FET is not read here. E-12's acceptance does
  not include it; the battery stream reviews it.
- **An open dock.** A conductor that bridges the two enable targets on E5 without touching the ground target between
  them makes the terminal live undocked. That is the same as a docking: a dv/dt start with the breaker in place. This is
  Layer 7's cover and geometry.
- **The gauge's wake from a charger.** VCC's tap R7 now sits on BRK_VIN (IF-6), so a charger at PACK_P reaches it
  through the breaker FETs' body diodes while the breaker is off: one diode drop (VSD at most 1 V, 15.4's charge direction).
  This is the path the record states; R7's own comment in the generator still says "from the pack terminal".
- **The inverters' own failures** are the record's remaining latent faults: Q104 open, or Q103 shorted. E-12 finds them:
  PACK_P dead undocked, and each loop conductor to ground in turn. R105 or D102 open holds the breaker off (fail-safe,
  revealed at the next docking).
- **The inhibit's own failures.**
  - Q105 shorted holds the breaker off (fail-safe, revealed).
  - Q105 open, or U102's output stuck low, removes the inhibit like an open NTC. E-12b does not find it; E-15's heated
    specimen does.
  - Q106 open leaves the inhibit ungated: a hot pad would then turn off a running breaker at the trip. That is not unsafe,
    but it interrupts the service, and E-12b does not find it.

- **The reverse-charge detector's own failures** (round 3) are listed with how each is found in section 12d.

## 11. How to run

From the repository root:
- `python3 v2/docs/records/l8p/fetch_held_back.py` places TI's held OPA187 sheet and checks it by sha256.
- `python3 v2/docs/records/l8p/l8p_drafts.py` prints `l8p_drafts.out`, which is regenerated only with `_bin/regen_out.py`.
- `python3 v2/docs/records/l8p/check_l8p_netlist.py [p=...] [e=...] [a=...]` checks netlists.
- `python3 v2/docs/records/l8p/gen_netlist.py <generator copy> <out.net> [project]` regenerates a part-table netlist.

Tests: `v2/ecad/tools/tests/test_l8p.py`. No KiCad. The held sheet is fetched once; the tests skip what needs it when it is
absent. Scratch copies only; the tree is never written.

## 12. B-R2: the charge through a latched breaker (round 3, route R1; `l8p_drafts.out` section 3b)

**The gap** (task L4-E11 section 19h at `e60a94a8`, its checker's B-R2; copied into `inputs/`). The -1 latches while a source
is present and the fault is resistive: the battery FETs keep CELL+ tied to VSYS (10.4 V into the 0.915 ohm fault), so board
A's hardware inhibit, which needs CELL+ under 1.98 V, sets only for faults under 33 mOhm. When the fault clears, a charge passes
the latched FET's body diodes with CELL+ alive and PGD high. The latched FET is held at 89.7 C at the power-on 0.256 A and
142.2 C at R-b's 1.2567 A; over 1.405 A it passes 150 C (from 76.25 C at VSD 1 V and 52.5 C/W). Over that, firmware alone held it.

**The criterion, item by item:**

| Item | How route R1 meets it | Where |
|---|---|---|
| The latched state detected without firmware | U103 reads a charge into the cells over its threshold, U104 reads the breaker's body diodes conducting; both are analog comparators on board P | 12b, 12c |
| Board A's charge inhibit set in every latched case, a resistive fault with a source present included | Every off state of the breaker that passes a charge over the threshold holds DOCK_EN_RET low: the latch, the hold, C-1c's hold and the thermal guard's trip. Board A's inhibit sets on it (the interface, 12f). Under the threshold no inhibit is needed: the FET is held at 139.9 C at most | 12b, 12c, 12f |
| Thresholds with tolerances and bounded delays | The charge threshold 0.368 to 1.213 A, the reverse threshold 0.044 to 0.268 V, every tolerance at its worst sign; the pull within 0.56 ms; the restart within 0.948 s, board A's hold at least 1.0 s | 12c |
| The protector's own limits | Supply, inputs, gate voltages, the pull's level, its standby draw, its failures and how each is found | 12d |
| The service untouched | Discharging, U103 reads a negative drop; charging through a running breaker, U104 reads under its threshold: the detector never acts on a running breaker, at 10 A, at 18 A for 60 s, or in a current-limit excursion | 12e |

### 12a. What exists, and why none of it tells board A

- **PGD** switches on VDS alone (SNVS452G pin 8: active when VDS decreases below 1.25 V). A reverse charge makes VDS negative,
  so PGD reads good in the very state to be told (L4-E11 19h).
- **The -1's latch** has no output. After the fault time the GATE is held low by the 1.75 to 2.6 mA sink until UVLO or VIN
  cycles (8.4.3). A divider on GATE would draw from the 10 to 22 uA charge pump that sets l9stk's 40.7 ms start, on which IF-1
  rests.
- **The enable loop.** Board A reads its two conductors, DOCK_EN_OUT and DOCK_EN_RET, and both are ratiometric to BRK_VIN through
  RT1. Their ratio is 22 kOhm over (22 kOhm plus RT1) whether R106 is in the loop or bypassed: 0.8148 at RT1's 5 kOhm, 0.3188 at
  47 kOhm, 0.0611 at 338 kOhm. So a change of the loop's source scales both conductors alike. A changed return resistor is
  confounded with RT1's own span. A raised return turns Q103 on with no dock, so the breaker would be enabled undocked. **Only the
  return held low is distinct**, and board P's Q103 and Q104 already read it as the loop open: UVLO is pulled and the -1 resets.
- **C-1c's NTC** reads the pad, which follows a body-diode charge only slowly, and its comparator is gated by PGD, which reads
  good in reverse.
- **The gauge's charge FET Q1** could block a charge into the cells, but the owner's criterion takes Q1 and Q2 welded.

So the loop's return carries the state on a contact board A already has (J_DOCK pin 3), with no new contact. The state itself
must be detected by new parts, because no part on board P reads it.

### 12b. Route R1 SELECTED: the reverse-charge detector (SESSION, drafted in `apply_gen_sch_p_breaker.py`)

| Ref | Value | What it does |
|---|---|---|
| U103 | OPA187IDBVR (U102's part) | The charge **into the cells**: +IN on R10's cell side (GND) through R120, -IN on the reference. High while the cells take a charge over the threshold |
| R120, C109 | 200 ohm; 470 nF 25 V X7R | +IN's filter, 94 us. R120's source resistance equals R119's, so the bias currents cancel |
| R129, D103 | 47 kOhm 1 %; BZT52C12-7-F (board A's D25 part, C124196) | REV_VZ, the reference's feed: BRK_VIN times 0.96074 under the zener, at most 13.46 V at the held 101.0 C case |
| R118, R119 | 1.15 MOhm and 200 ohm, 0.1 %, at most 25 ppm/K | The threshold: 1.739e-4 of REV_VZ, 0.0869 A per volt across R10's 2 mOhm |
| U104 | OPA187IDBVR | The breaker's **body diodes conducting**: +IN on PACK_P over R121 and R122, -IN on BRK_SNS over R123 and R124. High while PACK_P exceeds BRK_SNS by 1.107 % of it |
| R121, R122, R123, R124 | 332 k, 33.2 k, 328 k, 33.2 k; 0.05 %, at most 10 ppm/K | The two dividers (1/11 and 1/11.04) |
| C110 | 1 nF C0G | Across U104's inputs, 60 us |
| R125 to R128 | 100 kOhm | Each output halved onto a 2N7002 gate: 14.6 V at most at the 29.2 V clamp |
| Q107, Q108 | 2N7002 | In series from DOCK_EN_RET to the return: the return is held low only while both comparators are high |
| C107, C108 | 100 nF 50 V X7R | The comparators' supply bypass (class D, SBOS807E 10.1, as C106) |
| TP107, TP108 | test points | REV_IOUT and REV_VOUT, for E-12c |

**Why each condition, and why both:**
- U103 alone would pull during a normal charge through a running breaker: R-b's 1.024 A set point reaches 1.2567 A.
- U104 alone would pull during a sleeping gauge's wake. The charger's push then reaches only BRK_VIN's own loads, a few mA
  through the body diode, and the gauge is off, so R10 carries nothing. Pulling then would starve the wake: CELL_FUSED's 104 uF
  cannot carry BRK_VIN through the hold.
- Both together hold exactly when a charge over the threshold passes an off breaker's body diodes. The cause does not matter:
  the -1 latched, in its hold, held by C-1c, or held off by the thermal guard. Q1 and Q2 may be welded or not, because R10 lies
  in the cells' own path.

**Why the reset is harmless here.** The pull resets the -1, as an undocking does. A charge flows backwards only while the source
holds CELL+ above the cells, and board A's inhibit (12f) holds the battery FETs off through the hold and the start. So the dv/dt
start meets CELL_FUSED alone and no forward current: no B-R1 start into a fault. If the fault returns after the restart, the -1
meets it as one fault event, not as a start. A retry needs the fault itself to clear and return, at most once in 1.0 s.

**The sequence:**
1. A charge over the threshold passes the off breaker.
2. U103 and U104 go high, Q107 and Q108 hold DOCK_EN_RET under 0.06 V, within 0.56 ms.
3. On board P, Q103 turns off and Q104 pulls UVLO: the -1 resets if its timer is under 0.3 V, which it is 34.0 ms at most after
   a latch; an earlier pull fails safe and the next one resets it.
4. On board A, the inhibit sets within 1 ms and holds the battery FETs off; the charge stops.
5. U103 falls, so the return rises.
6. The hold (0.110 to 0.907 s) and the start (40.7 ms) restart the breaker within 0.948 s.
7. Board A's inhibit holds at least 1.0 s after the return rises, then releases on CELL+ alive. The charge then passes the
   channel, and U104 reads under its threshold.

### 12c. The thresholds, their tolerances and the delays (`l8p_drafts.out` section 3b; every figure computed there)

**U103, the charge threshold**, read with every tolerance at its worst sign:
- R118 and R119: 0.58 % together.
- R129's share: 0.08 %.
- R10: 1.57 %. Its 1 % and 75 ppm/K are ASSUMED, owed to Layer 6.
- U103's 33.0 uV: VOS, drift to 125 C, IOS through 200 ohm each side, and PSRR, read from SBOS807E.

| BRK_VIN | The threshold |
|---|---|
| 4.70 V, the LDO-mode precharge's floor (SRN 5.7 V, R-b', less VSD 1.0 V) | 0.368 to 0.418 A |
| 7.60 V (PORIT) | 0.605 to 0.666 A |
| 10.6 V | 0.661 to 0.922 A |
| 16.8 V and the 29.2 V clamp | 0.661 to 1.213 A |

The least is 0.368 A, against the LDO-mode precharge's 0.33616 A at most (L4-E11 15c): x1.094. The power-on 0.256 A passes
too, so a dead pack's precharge within R-b' is never stopped by the detector. The most is 1.213 A, against the latched FET's
1.405 A: x1.159. A charge the detector lets pass holds the FET at 139.9 C at most.

The 0.661 A least above 8 V assumes the zener may conduct from 7.95 V. Its knee under 1 mA is not printed; the sheet gives its
leakage at 8.0 V, taken ten times hot.

**U104, the reverse threshold**, read with every tolerance at its worst sign:
- R121 to R124: 0.458 % of BRK_SNS in all.
- U104's 468 uV, mostly IOS through 30.2 kOhm: 5.1 mV referred.

| BRK_VIN | The reverse threshold |
|---|---|
| 7.60 V | 0.0442 to 0.1241 V |
| 10.6 V | 0.0637 to 0.1711 V |
| 16.8 V | 0.1040 to 0.2681 V |

Against both sides of it:
- **A running breaker** at the pack path's 23.93 A shows 20.7 mV (RDS(on) 0.96 mOhm at most, x1.8 at 150 C read from Figure
  8, two in parallel). That is under the least 0.0442 V, and the charger's own bound (118 W over 10.6 V, 11.1 A) is under it
  again.
- **The body diodes** at the threshold's least current, 0.302 A a FET, read 0.399 V at 125 C and 0.348 V at 150 C. At the held
  101.0 C case they read 0.448 V. All are over the most threshold, 0.268 V. These come from TI's typical Figure 9, read by eye:
  INFERRED, and E-14b measures them.

**The pull and the delays:**
- Q107 and Q108's gates are at 3.8 V at BRK_VIN 7.6 V (PORIT, under which the -1 runs nothing), against the 2N7002's 2.5 V
  threshold at most. They are at 14.6 V at the clamp, against its 20 V.
- DOCK_EN_RET is held at 0.055 V at most: 2 x 7 ohm, doubled hot, at 1.96 mA.
- The filters are 94 us and 60 us. Each is taken to a 10 % overdrive, and the OPA187's typical slew and recovery are taken ten
  times slower: the pull comes within 0.56 ms.
- A charge over the threshold for 10 ms at the pack path's 23.93 A and VSD 1.0 V in one FET raises its junction 10.3 K over the
  case (Figure 1's single pulse, 0.54 x 0.8 C/W at 10 ms, read).

### 12d. The protector's own limits and failures

**Ratings:**
- U103 and U104 run on BRK_VIN: 4.5 to 36 V (40 V absolute), against 4.70 to 29.2 V. Their inputs stay within (V-) - 0.1 V to
  (V+) - 2 V.
- U103's +IN reaches 0.101 V under the return at the breaker's 50.59 A, through R120. The sheet states no phase reversal, and
  the output stays low.
- The 2N7002s stay within 20 V on the gate and 60 V on the drain.
- The detector draws 0.47 mA from BRK_VIN at 16.8 V, a standby load for the battery stream.

**Under BRK_VIN 7.6 V** the -1 cannot run or stay latched, and the detector is not claimed: its gates fall under 2.5 V below 5 V.
Down there the charge is the LDO-mode precharge (R-b', at most 0.336 A).

**Its own failures:**

| Failure | Effect | Found by |
|---|---|---|
| U103's or U104's output stuck low; Q107 or Q108 open; R119, R121 or R124 open; C109 shorted | The detector is lost: B-R2 falls back to the firmware, latent | E-12c (a), (b) |
| R120 open | U103's +IN floats on C109 and drifts with its bias current (7.5 nA at most): one of the two rows below or the one above | E-12c (a) to (d) |
| Q108 shorted; R122 or R123 open; U104's output stuck high | The pull follows U103 alone: a charge over the threshold through a running breaker resets it, so the service is interrupted. Fail-safe and revealed | E-12c (c) |
| Q107 shorted; R118 open or D103 shorted; U103's output stuck high | The pull follows U104 alone: a sleeping gauge's wake and an off breaker's precharge stall. Revealed on a dead pack | E-12c (d) |
| Q107 and Q108 both shorted (two faults) | The breaker is held off: fail-safe, revealed | E-12 |
| D103 open | The threshold follows BRK_VIN to about 1.46 A at 16.8 V, over the FET's 1.405 A. Latent | E-12c (a) at a pack near 16.8 V |

### 12e. The service untouched

**At 10 A continuous, 18 A for 60 s, and in every current-limit or power-limit excursion** the current through R10 is a discharge:
U103 reads a negative drop and stays low, whatever U104 reads. **While the breaker runs and the pack charges**, at R-b's 1.2567 A
or any charge up to 23.93 A, U104 reads at most 20.7 mV against its least 0.0442 V and stays low. The detector never pulls the
return of a running breaker, and so never turns it off. Its loads on the loop are a 2N7002's leakage on DOCK_EN_RET (80 nA at most)
and nothing on DOCK_EN_OUT, so l9stk's bound point of the inverters and the thermal guard is unchanged.

### 12f. The interface owed to L4-E11's DD-7 draft (finding L8P-F04)

- **The contact:** J_DOCK pin 3, DOCK_EN_RET, already on board A. No new contact, and no Layer 5 or Layer 7 row changes.
- **What board P drives:** DOCK_EN_RET held at 0.06 V or under while a charge over 0.368 to 1.213 A passes the off breaker;
  otherwise the loop as today.
- **What board A must do:**
  - Set its charge inhibit (the battery FETs held off, BATDRV at VBAT) while DOCK_EN_RET is under 1.0 V and DOCK_EN_OUT is at
    2.0 V or over, whatever CELL+ reads.
  - Set it within 1 ms of the return falling.
  - Hold it at least 1.0 s after DOCK_EN_RET rises over 2.5 V; the breaker restarts within 0.948 s. Then release it on CELL+
    alive, as Q48 does now.
  - Load DOCK_EN_RET with 1 MOhm or more, so l9stk's bound point of the first inverter stays over its 2.5 V.
- **The levels:**
  - With the return held, DOCK_EN_OUT falls to 2.52 V at BRK_VIN 7.6 V and 3.51 V at 10.6 V (RT1 at its 5 kOhm least).
  - The DD-7 draft's Q47 reads half of it (R109, R144), 1.26 and 1.75 V, under the 2N7002's 2.5 V. That sense is redrawn, for
    example a gate whose threshold is 1.5 V at most on DOCK_EN_OUT itself, clamped under 20 V as D25 clamps DD7_G.
  - A 2N7002's gate on DOCK_EN_RET reads it as low under 1.0 V and as high over 2.5 V.
  - Between 1.0 and 2.5 V lies only the thermal guard's band (RT1 past 47 kOhm, outside the service, where the return stays at
    2.94 V or over). There the reading may go either way: the inhibit may set while Q103 still holds the breaker on, which
    hastens the guard's trip by the battery FETs' body diodes. That is the guard's own region.
- **At docking** DOCK_EN_OUT and DOCK_EN_RET rise together, so the return is never low while the loop is powered. The 1.0 s
  hold may be armed only by a low return with the loop powered, or start at every rise of the return. In the second case the
  battery FETs are released the hold's length after the loop closes, where today they follow the breaker's start (0.150 to
  0.948 s). That is L4-E11's choice.
- **What board A gains:** the inhibit in every off state of the breaker that passes a charge over the threshold, the thermal
  guard's trip and C-1c's hold included. For the guard's trip, board A's own reading of a low return sets it whether or not board
  P pulls.

### 12g. E-14 as it now reads, and E-12c

**E-14 (record l9stk's, with route R1)** is a bench test on board P's specimen, the -1 latched and a bench source driving PACK_P
over BRK_VIN through a current limit (board A, or a stand-in for its inhibit):
- (a) **The threshold.** A charge stepped 0.3, 0.6, 0.9, 1.2 and 1.5 A at BRK_VIN 10.6, 13.7 and 16.8 V. DOCK_EN_RET (TP104)
  falls within the band of 12c. Under it, the FET's junction (VSD method) settles at most 150 C (139.9 C predicted at 1.213 A).
- (b) **The stop.** At the source's largest charge (11.1 A at least), DOCK_EN_RET falls under 0.06 V within 1 ms. With board A's
  inhibit the charge ends within 10 ms, and the junction rises 10.3 K at most.
- (c) **The restart.** The breaker restarts within 1.0 s of the return's rise, with the battery FETs off until it is on. The
  charge then passes the channel, with TP108 low.
- (d) **The wake.** The gauge in shutdown and a charger at PACK_P: TP107 stays low throughout, the gauge wakes, and the breaker
  is on within 0.963 s of BRK_VIN's rise (the hold, the insertion time's 15.25 ms and the start).
- (e) **The service.** The breaker on, charging at 1.2567 A and at the largest charge: TP108 low, DOCK_EN_RET unchanged.
- **E-14b:** VSD of Q101 and Q102 at 0.3 and 0.6 A at 25 and 125 C, at least 0.30 V hot, against section 12c's 0.268 V.

**E11-45 (c2)'s acceptance with route R1:** the charge into PACK_P ends within 10 ms of passing the threshold, and the breaker
restarts within 1.0 s.

**E-12c, a commissioning check like E-12**, at commissioning and at each service:
- (a) Undocked, a bench source on PACK_P 1 V over BRK_VIN through a current limit of 0.3 A, then 1.5 A. TP108 high in both;
  TP107 low at 0.3 A and high at 1.5 A.
- (b) Docked on a stand-in for board A: at 1.5 A the return falls (TP104).
- (c) The breaker on, a 1.5 A charge through it: TP108 low, the return unchanged.
- (d) The gauge in shutdown, a charger at PACK_P: TP107 low.

### 12h. Not taken

| Route | Why not |
|---|---|
| R1's reverse-blocking element: a second pair of CSD18510Q5B back to back with Q101 and Q102 | At 23.93 A it doubles the pad's loss, from 2 x 0.247 W to 4 x 0.247 W, and lifts the held 101.0 C case by about 25 K. Every SOA figure of l9stk rests on that case (TI asks under 125 C). It also blocks the charge path a sleeping gauge's wake and the LDO-mode precharge use (l9stk 15.4, the charge direction) |
| R1's gate state on a new contact | A J_SMB 1x8, a dock position and board E's pass-through. Every free dock position (2, 6, 7, 11) sits beside a signal (VSYS_DOCK, SHORE_INHIBIT, DOCK_EN_OUT, HOT-R1, the USB pair), so Layer 5 and Layer 7 rows change. Reading the gate draws from the 10 to 22 uA pump that sets the 40.7 ms start. "Off" alone would stop a sleeping gauge's wake, so the same current condition is needed anyway. The loop's return carries the result on a contact board A has |
| R2, a charge cap on board A | An 11.8 % window (1.2567 to 1.405 A) at R17, a high-side sense part not held, a cap on every charge, running breaker or not, and no recovery. R1's window is 0.336 to 1.405 A, 4.2-fold, with the kit's parts |
| A restart on board P alone, by a short UVLO pulse | The -1 resets on "momentarily pulling the UVLO pin below 2.5 V" (8.4.3), with no minimum printed. A pull that drains C_U restarts only after the hold, up to 0.907 s with the charge still in the body diodes. So board A's inhibit is needed either way |

### 12i. Status

**B-R2's route R1 DRAFTED on board P** (U103, U104, Q107, Q108, D103, R118 to R129, C107 to C110, TP107, TP108, in the breaker
draft), the netlist check's REV group DRAWN on the regenerated netlists and FAIL on two mutations. **Board A's side is owed**
(12f, L8P-F04, L4-E11's to draw). Found on the way, for L4-E11 with record l9stk: L8P-F05, CELL+ held partly up through the
LM5069's internal 1 MOhm while the breaker is off (section 9).

CONDITIONAL on:
- E-14b, the body diodes' VSD read from a typical figure;
- R10's tolerance and temperature coefficient (Layer 6; 1 % and 75 ppm/K assumed);
- E-14 and E-12c on the specimen.

Not claimed: nothing here is built, bought, powered or measured; the statements are about generator text, netlists and
arithmetic on the makers' printed figures.
