# L8P-BREAKER: W4DP-F2's breaker drawn for boards P, E and A (Layer 8 record l8p)

Record `l8p`, MESHSAT-1357, 4 October 2026, branch `fnd/l8p` from main `64cd25ee`. The author is board P's generator author
for this one correction and, since round 2, DD-8's owner.

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
| `apply_gen_sch_p_breaker.py` | P | The breaker U101 (the -1) with its sense pair, FETs, power limit, timer, dv/dt capacitor, input clamp and input bypass. The enable loop's two inverters and the RC hold through R105 and D102. The restart inhibit: RT101 on the pad, its bridge and reference, the comparator U102, the PGD gate Q105 and Q106. J_SMB as a 1x7 with the loop on pins 5 and 7 and the return on pin 6. The gauge's PACK and VCC taps and Q2's R19 moved to Q2's source (IF-6). PACK_P re-declared as the breaker's output. Six test points for E-12 and E-12b. One schematic section. |
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
| Test points | TP101 BRK_VIN, TP102 BRK_UVLO, TP103 DOCK_EN_OUT, TP104 DOCK_EN_RET (E-12); TP105 INH_NTC, TP106 INH_OUT (E-12b). | E-12's commissioning steps, and E-12b (section 4). |
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
| P | U101, U102, Q101 to Q106, D101, D102, RT101, R101 to R117, C101 to C106, TP101 to TP106 | DISJOINT (l6r2's two board P drafts add none) |
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
| **L4-E11** (with board A's generator) | **DD-7, the input-return pulse:** board A opens the enable loop for a pulse when an input appears, so the -1's latch resets. It sits in the loop on board A, in series with RT1 between J_DOCK pins 5 and 3 (DOCK_EN_OUT and DOCK_EN_RET), so it composes with this record's A draft. B-R2's hardware charge inhibit and E-14 stay L4-E11's. |
| The firmware owner | **IF-7:** the bridge reports a tripped breaker (the pack's terminal dead while the gauge's FETs are on) and enables charging only after the breaker's restart; recovery on battery is redocking. |
| Layer 6 (L8P-06) | **Order codes owed:** the LM5069-1 (U101; the -2's C111822 is not it); the OPA187IDBVR (U102); the NXRT15XH103FA1B010 (RT101); the 7-way J_SMB at both ends, pinned in the generators as R8P-02 pinned the 4-way C144395, so no fill decides it (`lcsc_fill.py`'s rule `SMBus lead.*JST-XH 1x4` no longer matches). |
| Layer 6 | E-6 for the sense pair: 2 W each at the band's temperature, at most 50 ppm/K. R110, R111 and R112 at 0.1 % and at most 25 ppm/K (the budget of section 4 rests on it); R113 15 MOhm 1 %. C103's capacitance at its 0 to 2.55 V charge within the record's 10 % (the hold's 0.110 s least). R105 and D102's single pulse at each undocking and each inhibit pull (C_U from 16.8 V through 150 ohm, about 0.47 mJ, 107 mA peak). RT101's bonding adhesive: electrically insulating, thermally conducting, to 125 C. Codes for the new passives. |
| Tools owner | `check_contracts.py` 15c: a role for DOCK_EN_OUT and DOCK_EN_RET, equal at both ends, before the regenerated P and E are judged. `gen_pcb_e5.py`'s silk table `SHORT` gains the two nets (the block's land labels read "?" otherwise; cosmetic). |
| Board P's PCB generator (`gen_pcb_p3.py`) | **IF-2:** each breaker FET's installed RthJA at most 52.5 C/W (1 in2 of 2 oz each gives the sheet's 50). The area budget is two 1 in2 pads, 1290 of the 2084 mm2 left, 793 mm2 for the rest. U101 sits beside the sense pair with Kelvin taps (E-9). C104 and C105 sit at the sense pair. RT101 sits on the FETs' pad with its two lead lands beside it; U102 and its bridge sit away from the pad. Q2's source band becomes BRK_VIN, and the PACK_P band runs from the breaker FETs' sources to W_P. |
| The integrator | IF-3: a stage for the breaker in `pcb_energy_chain.yaml` between PACK_FETS and PACK_LEAD (its limit 23.93 A). |
| The l9stk register's owner | E-10's line gains VDS under 1.62 V during current-limit excursions; E-12b (section 4) joins E-12; E-15 measures the pad-to-NTC gradient against section 4's 1.24 K. |

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
| P, E and A each with this record's draft alone (the generators ran to their end) | DRAWN on BRK, EN and INH; the LOOP across the three boards DRAWN |
| Board P composed in L4-E9's order | DRAWN on BRK, EN and INH |
| Boards E and A composed in L4-E9's order | the generators refuse on other drafts' defects (section 9); with scratch stand-ins for those, DRAWN, LOOP DRAWN |
| Three mutated netlists (P's J_SMB pins 6 and 7 exchanged; A's J_DOCK pins 3 and 4 exchanged; P's Q105 and Q106 gates exchanged, so the inhibit is no longer gated by PGD) | FAIL |

The check parses the netlists and reads the dock lands' pad positions from `meshsat.pretty`. It holds:
- the breaker's nets and values, U101's PGD on BRK_PGD;
- the enable loop on each board, and the hold through R105 and D102 with Q104 on UVLO;
- the restart inhibit: the bridge and the reference both from U101's VIN, U102's inputs, Q105 on U101's UVLO, Q106's gate on
  U101's PGD and its drain on Q105's gate, RT101 on the lead lands, the values;
- the ground contact between the loop conductors, on J_SMB (by position along the row) and on J_DOCK and J_BLK (a ground
  pad at the midpoint of the two loop pads);
- the loop's continuity from BRK_VIN through R106, the lead, the dock and RT1 back to Q103's gate.

**Owed on the box:**
- the regenerated schematics with ERC and the KiCad netlist export;
- the label grid matter of Q2's renamed source (board P's comment at SCP_OUT records one);
- the 7-circuit XH and SOT-23-5 lands read from KiCad's library.

## 9. Findings for other authors (run-time refusals no text-level composition test reads)

| Finding | Board | Owner | What stops the composed generator | State |
|---|---|---|---|---|
| L8P-F01 | E | L4-E7 (`apply_gen_sch_e_backstop.py`) | Its decoupling entries C66 (U18 pin 5), C67 (U19 pin 5) and C68 (U20 pin 6) carried no G14 class, and `gen_sch_e.py` refused. | **CLOSED** by L4-E7's `fnd/l4e7r6` at `914a2f5a` (class D with each maker's clause). The composition uses that draft; its stand-in is dropped. |
| L8P-F02 | A | L4-E11 (`apply_gen_sch_a_charger.py`) | VSYS_DOCK names U42 as its source without `source_ic`, which `intent.rail` refuses. With that passed, it is fed from VBAT before VBAT is declared, which is refused too. Board A's composition stops at step 3a. | open |
| L8P-F03 | E | L4-E11 (`apply_gen_sch_e_aux.py`) | +12V_FAN names L4 as its source, and L4 is not on that net (it sits between F12_SW1 and F12_SW2). `intent.write` refuses. | open |

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

## 11. How to run

From the repository root:
- `python3 v2/docs/records/l8p/fetch_held_back.py` places TI's held OPA187 sheet and checks it by sha256.
- `python3 v2/docs/records/l8p/l8p_drafts.py` prints `l8p_drafts.out`, which is regenerated only with `_bin/regen_out.py`.
- `python3 v2/docs/records/l8p/check_l8p_netlist.py [p=...] [e=...] [a=...]` checks netlists.
- `python3 v2/docs/records/l8p/gen_netlist.py <generator copy> <out.net> [project]` regenerates a part-table netlist.

Tests: `v2/ecad/tools/tests/test_l8p.py`. No KiCad. The held sheet is fetched once; the tests skip what needs it when it is
absent. Scratch copies only; the tree is never written.
