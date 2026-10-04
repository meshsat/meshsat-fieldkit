# L8P-BREAKER: W4DP-F2's breaker drawn for boards P, E and A (Layer 8 record l8p)

Record `l8p`, MESHSAT-1357, 4 October 2026, branch `fnd/l8p` from main `64cd25ee`; round 3 on branch `fnd/l8p2` from
`fnd/l8p` at `e1bc3cba`. The author is board P's generator author for this one correction and, since round 2, DD-8's owner.

**Status: DRAFTED, not applied.** Four release-guarded apply scripts, a netlist check and their proof on scratch copies.
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

**Round 4 (4 October 2026, the correction of design defect DD-5; section 13).** With the gauge's CHGIN = 1 above T3 the
discharge current crossed the charge switch Q1's body diode: 10 W at 10 A and 23.9 W at the breaker's held 23.93 A, against the
1.48 W its pad holds (record `l9stk` 15.5 to 15.7; BAT-F20, EQ-15). **Corrected in a new board P draft,
`apply_gen_sch_p_idealdiode.py`:** an ideal diode beside Q1 (Q109, a second CSD17570Q5B, under U105, an LM74700-Q1). On case
row C-PROT with CHGIN = 1, Q109 carries 10 A at 0.30 W, 18 A at 0.54 W and 23.93 A at 0.72 W at most. The gauge's charge blocking
and its drive of Q1 are unchanged, and no discharge is refused. E-8 (restated), E-16 and E-12d stay open.

**Round 5 (4 October 2026 evening, the independent check V1 of B-R2, CONFIRMED AS CONDITIONAL; its condition C4 and its minors).**
Task L4-E11's round 10 (`fnd/l4e11r10` at `a09e9a60`) drew board A's side of route R1 and corrected L8P-F02 to L8P-F05. This round:
1. **C4, clerical:** `check_l8p_netlist.py`'s board A EN group admits DD-7's readers by pin (L4E11-R10-F2), and three mutations of the
   composed board A fail it; the compositions used round 10's drafts, copied byte for byte, with no stand-in (round 12's in
   round 6, round 13's since round 6b); `l8p_drafts.out` is regenerated. Boards E and A composed in L4-E9's order run to their end.
2. **The interface restated** (section 12f, finding L4E11-R10-F1), quoted from L4-E11's sections 20c and 20d.
3. **Two findings, both OPEN** (section 12j): L8P-F06, the breaker FETs' hot off leakage inside L4-E11's latch budget, and L8P-F07,
   the guard RT1's printed points (condition C3). On Murata's typical curve the guard reaches the first inverter's turn-off at record
   l9stk's held reading of the 18 A service. The Murata question is drafted and UNSENT; two alternative parts are named and not
   selected.

**Round 6 (4 October 2026 evening, the independent check V2, an AI review).** V2 read the candidate `fnd/v2cand` at `dfa1eef2`,
which held round 5. Its verdict on this record: the ideal diode (round 4) CONFIRMED AS CONDITIONAL; L8P-F06 and L8P-F07 CONFIRMED
real and correctly OPEN; **NOT CONFIRMED for two statements**, both corrected here:
1. **V2-B2: the record was a round behind.** Round 5's copies of L4-E11 were its round 10; the candidate held round 11, and
   L4-E11's round 12 (`fnd/l4e11r11` at `ac72e730`) has since answered V2-B1: R256 back at 4.7 kOhm and the latch budget as TWO
   limits, the static 0.846 mA and the timing 520.7 uA. Every copy is taken again at `ac72e730`, the boards recomposed, the output
   regenerated, and 12f, 12j and E-14c restated on both limits. A test now compares each copy with `records/l4e11/` wherever a tree
   holds L4-E11's round 10 or later, so a copy a round behind fails.
2. **V2-B3: TDK's alternative, the bound taken the wrong way round.** The sure-off is a LOWER bound on the loop's scale k. On the
   sheet's printed limits a window exists: 10.51 to 10.62 at 7.6 V, 8.53 to 10.62 at 10.6 V. NOT SELECTED stands on three other
   grounds, each with its printed figure (12j).
3. **The minors that are this record's:** V2-m5 (the guard's trip side on L4-E11's worst split, and what is not bounded), V2-m7
   (E-16 reads U105's package), V2-m8 (E-8 measures the joint case), V2-m9 (board A composed in L4-E9's list order), V2-m4's row
   (C3 as V1 worded it), and the PTC draft's Murata quote.
The thermal guard's redesign (L8P-F07's correction) is not in this round: record l9stk's author is comparing approaches.

**Round 6b (4 October 2026 late evening): the copies of L4-E11 taken again at its round 13.** L4-E11 moved one more round
(`fnd/l4e11r11` at `4def5975`: its section 23, E11-29's measurement method, and its section 20c restated on Murata's printed
points), and on the coordinator's merged candidate this record's own guard fired, as round 6 built it to. Every copy is now
`4def5975`'s; round 12's are removed. **Of the eleven copies one changed, section 20c;** the four drafts and sections 20d, 20e,
22b, 22c, 22g and 22h are byte for byte round 12's.
- **No figure this record quotes or computes moved:** board A's held, powered, dead and alive readings, the load on the return,
  the window, the first inverter's band, the delays, the two limits of the latch, L8P-F06's table and E-14c's acceptance all read
  as in round 6. `l8p_drafts.out` changed only in the copies' names and pins and in four new lines of section 3b.
- **What no longer stands, in 20c and here:** record l9stk's "bound point" (the loop at 10.6 V with RT1 at 47 kOhm, the first
  inverter's gate at 2.894 V) bounds nothing, since 47 kOhm is not a point of this part. This record leant on it in one sentence
  of 12e, restated below; 12f gains the quote. That agrees with L8P-F07 (12j), which stays OPEN.
The guard's draft is this record's next round, with its own brief; nothing of it is here.

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
| `apply_gen_sch_p_idealdiode.py` | P | Round 4, DD-5 (section 13), applied after the breaker draft, which it requires: Q109 beside Q1 on SCP_OUT and SW, its controller U105, the charge pump's C111, R130 from gate to source, EN from BRK_VIN through D104 with R131, the anode pair C112 and C113, the cathode pair C114 and C115, TP109. SCP_OUT's loads and SW's sources re-declared with Q109. One schematic section. |
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
| P | The breaker draft: U101 to U104, Q101 to Q108, D101 to D103, RT101, R101 to R129, C101 to C110, TP101 to TP108. The ideal diode draft (round 4): Q109, U105, D104, R130, R131, C111 to C115, TP109 | DISJOINT, from each other too (l6r2's two board P drafts add none) |
| E | none (nets only) | DISJOINT |
| A | RT1 | DISJOINT (L4-E4 to L4-E11, l8gnd, l8r2, d8dec31's mainpb, l6r2) |

No literal part call is drawn twice in any composed generator.

The third battery FET of 15.5 (SELECTED) is **not drawn here**: its designator is L4-E11's to give, since Q41 is record
l8r2's VIN_RAW cut-off FET.

## 6. Order constraints for L4-E9's change list

1. **One release for the four drafts.** P (the breaker, then the ideal diode), E and A are released and applied together, never
   one alone. The netlist check reads FAIL on a board P that carries the breaker without the ideal diode (DD-5 uncorrected).
   - `check_contracts.py` section 15c compares J_SMB at both ends: family, pitch, pin count and roles.
   - Section 4 compares the dock's 2 x 6 map on J_DOCK and J_BLK.
   - Either check fails when only one end has changed.
2. **Board P: a new round.** The ideal diode draft follows the breaker draft directly (it reads BRK_VIN and refuses a target
   without it); l6r2's two tables before or after the pair. No other board P circuit change is in the list today, apart from U-01's R-105, which is undrafted and
   only under approach (II).
   - The breaker draft goes into board P's round with l6r2's two board P tables, in either order (both shown).
   - R-105, when drafted, must leave U101, Q2's source and J_SMB as this draft leaves them.
   - Board P's regeneration on the box follows.
3. **Board E: step 4e, any position.**
   - No other board E draft touches J_SMB, the J_BLK pins this one moves, the line it inserts before, or the section title.
   - Shown after L4-E11's aux (R-177) and before d8dec31's cin (R-16, step 4f), and also first and last.
   - The composition uses L4-E7's backstop draft of `fnd/l4e7r6` at `914a2f5a` (copied byte for byte into `inputs/`), which
     closes L8P-F01; when it reaches main, main's draft is that one.
4. **Board A: step 3g, before L4-E11's DD-7 draft, which goes before d8dec31's mainpb.**
   - It inserts before two lines that l8gnd's GND-002 draft also inserts before (each keeps the line once).
   - It replaces no text L4-E11's charger (R-157) replaces.
   - It adds no R or C, so by itself it composes anywhere: shown in its place, first and last.
   - **Round 6 (V2-m9): the order composed is L4-E9's list as the candidate carries it** (`fnd/v2cand` at `dfa1eef2`, rows 24 to
     33): r12, guard, charger, r11, bank, r138, u17, gnd002, hotr1, packrtn (R-201), slotlm (R-199), fb01 (R-200), this record's
     ptc (R-208), L4-E11's dd7 (R-217), then mainpb (R-193), with l6r2's table.
   - **Not in this record's tree** (main at `64cd25ee`): record l8r2's packrtn, slotlm and fb01 (its rounds 4 to 6 on `fnd/l8r3`
     at `89924e40`). They are left out of `l8p_drafts.out` and named there; `test_l8p` composes the whole list, runs the
     generator and reads the netlist wherever a tree holds them.
   - **In the tree and not in the list:** l8r2's d8v3 and vbus20ov. Composed in a second pass, before this record's draft.
   - **L4-E11's DD-7 draft must precede d8dec31's mainpb** (the list: R-217 before R-193). Applied after mainpb it is refused:
     mainpb takes the next free R and C at apply time, and on the list's order those are R233 and C241, which the DD-7 draft
     draws. With DD-7 before it, mainpb takes R257 and C249. A finding for the list's owner, beside L8G-F12 (R-194).
5. **Before P and E are regenerated and judged:**
   - `check_contracts.py` section 15c's role table needs a role for the loop's two nets (owed to the tools owner, section 7).
     Without it, P's J_SMB pins 5 and 7 read "unknown" and the contract fails.
   - Layer 5's interface rows go in the same release (section 7).
6. **The layout follows the schematic.** The board P PCB generator draws IF-2, the bands and RT101 on the pad; board A's
   places RT1; board E's places the 7-way land (section 7).
7. **Record l8r2's later rounds** (branch `fnd/l8r3` at `89924e40`, not on main) were checked once in round 1 on scratch
   copies, outside the script: board A's fb01, slotlm and packrtn and board E's packrtn compose with this record's E and A
   drafts, before and after them. Round 2 did not change those two drafts' anchors. Round 6: `test_l8p` composes them in the
   list's order wherever a tree holds them (item 4); on a scratch overlay of this tree with those four drafts of `dfa1eef2` laid
   in, the whole list composed and read DRAWN (README).
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
| **L4-E11** (with board A's generator) | **B-R2's interface, route R1 (section 12f, finding L8P-F04), restated in round 5:** board A's inhibit sets while DOCK_EN_RET reads held (under 0.7755 V at least) and DOCK_EN_OUT reads powered (over 1.981 V at most), whatever CELL+ reads, within 0.85 ms; it holds at least 1.341 s after the return rises, then releases on CELL+ alive; board A loads DOCK_EN_RET with at most 2 uA. Round 3's box (under 1.0 V, 2.0 V or over) is replaced by that narrower reading (L4E11-R10-F1). Drawn by L4-E11 since its round 10 (round 13 at `4def5975`, the same levels and delays); no new contact: J_DOCK pin 3. E-14 as it now reads (section 12g) and E11-45 (c2)'s acceptance. |
| The firmware owner | **IF-7:** the bridge reports a tripped breaker (the pack's terminal dead while the gauge's FETs are on) and enables charging only after the breaker's restart; recovery on battery is redocking. |
| Layer 6 | **Round 4:** C111, a 220 nF 50 V X7R 0805 whose maker's curve keeps at least 0.136 uF at 14 V and to 125 C (section 13d takes 20 % for the bias, ASSUMED); C112 to C115 at 50 V, each able to hold the applied voltage alone. Q109 and U105 are parts the kit already orders (C529279, C2941042). |
| Layer 6 (L8P-06) | **Order codes owed:** the LM5069-1 (U101; the -2's C111822 is not it); the OPA187IDBVR (U102, and U103 and U104 in round 3); the NXRT15XH103FA1B010 (RT101); the 7-way J_SMB at both ends, pinned in the generators as R8P-02 pinned the 4-way C144395, so no fill decides it (`lcsc_fill.py`'s rule `SMBus lead.*JST-XH 1x4` no longer matches). |
| Layer 6 | E-6 for the sense pair: 2 W each at the band's temperature, at most 50 ppm/K. R110, R111 and R112 at 0.1 % and at most 25 ppm/K (the budget of section 4 rests on it); R113 15 MOhm 1 %. C103's capacitance at its 0 to 2.55 V charge within the record's 10 % (the hold's 0.110 s least). R105 and D102's single pulse at each undocking and each inhibit pull (C_U from 16.8 V through 150 ohm, about 0.47 mJ, 107 mA peak). RT101's bonding adhesive: electrically insulating, thermally conducting, to 125 C. Codes for the new passives. Round 3: R121 to R124 at 0.05 % and at most 10 ppm/K, R118 and R119 at 0.1 % and at most 25 ppm/K (section 12c rests on them); **R10's tolerance and temperature coefficient** (the gauge's 2 mOhm sense: the generator prints neither; section 12c takes 1 % and 75 ppm/K, ASSUMED); R129's temperature coefficient (100 ppm/K ASSUMED). |
| Tools owner | `check_contracts.py` 15c: a role for DOCK_EN_OUT and DOCK_EN_RET, equal at both ends, before the regenerated P and E are judged. `gen_pcb_e5.py`'s silk table `SHORT` gains the two nets (the block's land labels read "?" otherwise; cosmetic). |
| Board P's PCB generator (`gen_pcb_p3.py`) | **Round 4 (IF-8, DD-5):** Q109 beside Q1 on the same SCP_OUT and SW bands, each on the bands' full width; the SW pour (Q1's, Q109's and Q2's drains) at 51.4 K/W or better to the inside air for the hottest junction with Q109's and Q2's losses counted, with 35.5 K/W as the target (section 13d; the bottom face is free); U105 off the pour where the board stays under 125 C at 23.93 A held, its ANODE, GATE and CATHODE traces taken at Q109's own pins (TI 12.1); C111 away from the FETs; C112 at U105's ANODE pin. **Round 3:** U103's sense by Kelvin taps from R10's two pads (R120's trace from the GND pad; U103's V-, R119 and C109 at the PACK_N pad), as the gauge's SRP and SRN are taken; U104's dividers from the FETs' own drain and source pads (BRK_SNS and PACK_P at Q101 and Q102), so no band drop adds to the reverse VDS; U103 and U104 away from the pad. **IF-2:** each breaker FET's installed RthJA at most 52.5 C/W (1 in2 of 2 oz each gives the sheet's 50). The area budget is two 1 in2 pads, 1290 of the 2084 mm2 left, 793 mm2 for the rest. U101 sits beside the sense pair with Kelvin taps (E-9). C104 and C105 sit at the sense pair. RT101 sits on the FETs' pad with its two lead lands beside it; U102 and its bridge sit away from the pad. Q2's source band becomes BRK_VIN, and the PACK_P band runs from the breaker FETs' sources to W_P. |
| The integrator | IF-3: a stage for the breaker in `pcb_energy_chain.yaml` between PACK_FETS and PACK_LEAD (its limit 23.93 A). |
| The l9stk register's owner | **Round 4:** DD-5's row (15.5, 15.6 and 15.7) with the correction of section 13: Q1's row reads Q109 at 0.724 W and 148.0 C with Q2 through one pad at 23.93 A held; **E-8 restated** with Q109 (three FETs on the SW pour; CHG off and CHG on); **E-16** and **E-12d** added (section 13g). |
| The l9stk register's owner | **Rounds 5 and 6 (section 12j):** **E-14c** (new): IDSS of the breaker FETs Q101 and Q102 at VGS 0 V and VDS 29.2 V at 25, 101 and 125 C; acceptance: the pair at most 388 uA at the 101.0 C held case, which keeps BOTH of L4-E11's limits (the timing 520.7 uA with 85.9 uA in hand, the static 0.846 mA with 398.8 uA); a reading over 473.9 uA reverses L4-E11's R256 selection (its 22e) (L8P-F06). **15.5, the thermal guard (L8P-F07):** the PTC's 47 kOhm point is the 470 ohm group's column; PRF15BB103RB6RC prints 100 kOhm over 110 C and 4.7 MOhm at 130 +-3 C. The trip side's resistance is printed (off before the PTC's copper passes 133 C); the hottest junction over that copper is not bounded (V2-m5: 2.12 K over its own mounting base at the worst split's 1.513 W, the base against the sensor's copper unread; E11-29's added reading). The no-trip side in the 18 A service is not printed, and on the typical curve the guard's onset at 10.6 V is 107.3 to 116.3 C, under the held 118.0 C. E-13 stays the guard's coupon test; the guard's design is the register owner's next round. |
| The l9stk register's owner | E-10's line gains VDS under 1.62 V during current-limit excursions; E-12b (section 4) joins E-12; E-15 measures the pad-to-NTC gradient against section 4's 1.24 K. Round 3: **E-14 as it now reads** and E-12c (section 12g); **a fourth recovery of the -1** (15.4b lists redocking, an input's return and the guard's cycle): a charge over the detector's threshold through the off breaker resets it, and it restarts after the hold with board A's battery FETs held off (section 12b). |
| **The battery stream** (BAT-F20, EQ-15, S-46; `review-packets/battery/`) | **Round 4, DD-5's correction (section 13):** the ladder rows L2 and L4a, the mode table and BAT-F20's text, which read the discharge crossing Q1's body diode under CHGIN = 1, are answered by Q109 under U105; FET Options stays 0x3D (CHGIN = 1), and no gauge setting changes (IF-4). For its review: U105's ANODE and GND sit directly on the cell node behind F1 and F2 (TI's circuit; every other IC on that node is behind a series resistor); a welded Q109 is found as a welded Q1 is (CFETF, SLUUAQ3A 3.10, if the golden image enables it; the second level behind it); U105 draws 152 uA at most while the gauge holds the discharge FET on, and 2.5 uA with the gauge shut down. The correction does not wait on Q-P18 or Q-TI-10 (drafted, unsent); whether they are still sent is the battery stream's. |
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
| P, E and A each with this record's drafts alone (the generators ran to their end) | DRAWN on BRK, EN, INH, REV and DIO; the LOOP across the three boards DRAWN |
| Board P composed in L4-E9's order | DRAWN on BRK, EN, INH, REV and DIO |
| Board P with the breaker draft and without the ideal diode | FAIL: DIO NOT DRAWN beside a drawn breaker (DD-5 uncorrected) |
| Boards E and A composed in L4-E9's list order (L4-E11's drafts, copied byte for byte: round 13's at `4def5975`, the same bytes as round 12's; no stand-in; l8r2's packrtn, slotlm and fb01 not in this tree) | the generators run to their end (295 and 728 parts); DRAWN, LOOP DRAWN, board A's EN group admitting DD-7's readers by pin |
| Board A, the same with l8r2's d8v3 and vbus20ov (in the tree, not in the list) | the generator runs to its end (750 parts); DRAWN |
| Ten mutated netlists (round 5, the composed board A: U48's SENSE1 and VDD exchanged, VBAT's pin on the return; Q44's drain and source exchanged, its source on the return; R109 moved from DOCK_EN_OUT to ground, so U48's SENSE2 reads nothing. Round 4: Q109's source and drain exchanged, the ideal diode the wrong way round; U105's GATE on Q1's gate, a second driver on the gauge's charge switch. Earlier: P's J_SMB pins 6 and 7 exchanged; A's J_DOCK pins 3 and 4 exchanged; P's Q105 and Q106 gates exchanged, so the inhibit is no longer gated by PGD; round 3: U104's inputs exchanged, so the detector reads a forward drop; R120 moved to PACK_N and R119 to GND, so U103 no longer reads R10) | FAIL |

The check parses the netlists and reads the dock lands' pad positions from `meshsat.pretty`. It holds:
- the breaker's nets and values, U101's PGD on BRK_PGD;
- the enable loop on each board, and the hold through R105 and D102 with Q104 on UVLO; on board A, round 5 (finding
  L4E11-R10-F2), the loop nets reach J_DOCK, RT1 and DD-7's readers admitted by pin, not by reference (U48 pin 2 and Q44 pin 3 on
  DOCK_EN_RET; R109 on DOCK_EN_OUT as a sense divider of 470 kOhm or more to neither loop net nor ground), so U48's VDD or Q44's
  source on the return fails;
- the restart inhibit: the bridge and the reference both from U101's VIN, U102's inputs, Q105 on U101's UVLO, Q106's gate on
  U101's PGD and its drain on Q105's gate, RT101 on the lead lands, the values;
- the ground contact between the loop conductors, on J_SMB (by position along the row) and on J_DOCK and J_BLK (a ground
  pad at the midpoint of the two loop pads);
- the loop's continuity from BRK_VIN through R106, the lead, the dock and RT1 back to Q103's gate;
- round 4, DIO, the ideal diode: Q109's three source pins on Q1's source net and its drain on Q1's drain net, which is Q2's
  drain; U105's ANODE and CATHODE on those two nets, its GATE on Q109's gate with R130 and TP109 and nothing of the gauge's,
  its GND on the cells' side of R10; C111 from VCAP to the anode; D104's cathode on EN and its anode on U101's VIN, which is
  Q2's source; R131; the two series pairs to the cells' negative; Q1's gate still on the gauge's drive; the values;
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
| L8P-F02 | A | L4-E11 (`apply_gen_sch_a_charger.py`) | VSYS_DOCK named U42 as its source without `source_ic`, which `intent.rail` refused; with that passed, it was fed from VBAT before VBAT was declared. Board A's composition stopped at step 3a. | **CLOSED** by L4-E11's round 9 (`fnd/l4e11r9`) and carried to its round 13 (`fnd/l4e11r11` at `4def5975`). The composition uses that draft, copied byte for byte into `inputs/`, with no stand-in: board A runs to its end (728 parts in the list's order) |
| L8P-F03 | E | L4-E11 (`apply_gen_sch_e_aux.py`) | +12V_FAN named L4 as its source, and L4 is not on that net (it sits between F12_SW1 and F12_SW2). `intent.write` refused. | **CLOSED** the same way (the aux draft at `4def5975`, copied byte for byte): board E runs to its end (295 parts) |
| L8P-F04 | A | L4-E11 (`apply_gen_sch_a_dd7.py`) | Not a refusal: B-R2's interface (section 12f). Round 9's DD-7 draft read the loop powered at half of DOCK_EN_OUT (Q47 through R109 and R144). With the return held low, DOCK_EN_OUT falls to 2.52 V at BRK_VIN 7.6 V and 3.51 V at 10.6 V, so Q47's gate read 1.26 and 1.75 V, under the 2N7002's 2.5 V; and nothing on board A read DOCK_EN_RET. | **ANSWERED** in L4-E11's draft since its round 10 (round 13 at `4def5975`, not on main): U48 reads the return held under 0.7755 V and the loop powered over 1.981 V (12f); composed here; the check V1 CONFIRMED AS CONDITIONAL |
| L8P-F05 | A | L4-E11 (`apply_gen_sch_a_dd7.py`), with record l9stk | Not a refusal. With the breaker off, the LM5069 feeds PACK_P, and so CELL+, through its internal 1 MOhm from SENSE to OUT (SNVS452G 7.5, note 1). With board A's 200 kOhm (R107, R108) alone, CELL+ read 2.80 V at BRK_VIN 16.8 V, over round 9's 1.98 V 'dead' point, so Q48 might release the inhibit while the breaker is off; 1.92 V with this record's U104 divider, 3.34 V at the 29.2 V clamp, and the 1 MOhm's tolerance not printed. | **ANSWERED** in L4-E11's draft since its round 10: a bleeder (R256, 4.7 kOhm again since its round 12) on CELL+ while the inhibit holds. The latch then has two limits on the sources into CELL+, the static 0.846 mA and the timing 520.7 uA (20e, 22c). The breaker FETs' leakage is one of those sources: L8P-F06 |
| L8P-F06 | P, with A | L4-E11 (the latch's two limits, 20e and 22c) with this record (Q101, Q102) | Not a refusal. With the breaker off, Q101's and Q102's off leakage flows into PACK_P and CELL+. TI prints IDSS 1 uA at 25 C only; on an ASSUMED doubling every 10 K the pair is 388.0 uA at the held 101.0 C case. Against the timing limit (520.7 uA, which leaves the pair 473.9 uA) that is 85.9 uA in hand: the pair alone fills it from a 103.9 C case, 2.9 K over the held case, or by a doubling every 9.63 K. Against the static limit (0.846 mA, 786.8 uA for the pair): 398.8 uA in hand, 111.2 C, 8.82 K (12j) | **OPEN** (E-14c, restated on both limits; the TI question drafted, unsent) |
| L8P-F07 | A, with P | record l9stk (15.5, the guard) with L4-E11 (RT1) and this record (the loop) | Not a refusal; V1's condition C3. Murata prints RT1 only at 25 C, over 110 C for 100 kOhm and at 130 +-3 C for 4.7 MOhm: the trip side's resistance is printed (the junction over the sensor's copper is not bounded), the no-trip side at 10 A only from a 15.51 V pack and in the 18 A service not at all; on the typical curve RT1 is 74.0 kOhm or more at the held 118.0 C, over the first inverter's 58.4 kOhm at 10.6 V. Record l9stk 15.5 read the 470 ohm group's 47 kOhm column (12j) | **OPEN** (the Murata question drafted, unsent; TDK's B59721A and Murata's PRF15BA102 named, not selected). The guard's redesign is record l9stk's next round, not this record's round 6 |

No stand-in is used since round 5: `STANDINS` in `l8p_drafts.py` is empty, and every board composes in L4-E9's order to its end.

**For the integrator and L4-E11's author (round 6).** `test_l4e11.py` pins this record's board A PTC draft by sha256 (`L8P3_PTC`,
the draft of rounds 3 to 5). Round 6 corrected that draft's quote of Murata's sheet, so its sha256 moved. On a line that holds both,
one L4-E11 test stops at that pin; on a scratch merge with `ac72e730`, `test_l4e11` read 68 passed and 1 failed with the pin as it
is, and 69 passed with that one pin moved. Round 6b, on a scratch merge with `4def5975`, whose test still carries the old pin:
71 passed and 2 failed, and 73 passed, 0 failed once the draft had moved the pin on the scratch copy. `apply_test_l4e11_ptc_pin.py` drafts the one-line change; it is not applied here.

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
- **The ideal diode's own failures** (round 4) are listed with how each is found in section 13h.

## 11. How to run

From the repository root:
- `python3 v2/docs/records/l8p/fetch_held_back.py` places TI's held OPA187 sheet and checks it by sha256.
- `python3 v2/docs/records/l8p/l8p_drafts.py` prints `l8p_drafts.out`, which is regenerated only with `_bin/regen_out.py`.
- `python3 v2/docs/records/l8p/check_l8p_netlist.py [p=...] [e=...] [a=...]` checks netlists.
- `python3 v2/docs/records/l8p/gen_netlist.py <generator copy> <out.net> [project]` regenerates a part-table netlist.
- `python3 v2/docs/records/l8p/read_prf_typical.py` prints the reading of Murata's typical BB curve that `l8p_drafts.py` carries as
  `PRF_BB_TYP` (round 5, L8P-F07; needs pdftoppm and Pillow; a reading aid, not a gate).
- `fetch_held_back.py` also places TDK's held sheet (round 5); `l8p_drafts.py` does not read it, and `test_l8p` reads the typed
  B59721A figures against it when it is present.

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
and nothing on DOCK_EN_OUT, so the detector moves no level of the loop. (Rounds 3 to 6 wrote here "so l9stk's bound point of the
inverters and the thermal guard is unchanged". That bound point, the loop at RT1 47 kOhm, is withdrawn as a bound: 12f, round 6b.
What RT1 may read in service is L8P-F07, 12j, and the detector's 80 nA is counted there in the return's 2.08 uA.)

### 12f. The interface with L4-E11's DD-7 draft (finding L8P-F04; restated from L4-E11 20c, 20d and 20e, taken again in rounds 6 and 6b)

- **The contact:** J_DOCK pin 3, DOCK_EN_RET, already on board A. No new contact, and no Layer 5 or Layer 7 row changes.
- **What board P drives:** DOCK_EN_RET held at 0.055 V or under while a charge over 0.368 to 1.213 A passes the off breaker
  (12c); otherwise the loop as today.

**Round 3's box, and why it is restated.** Round 3 wrote the interface as a box: board A's inhibit sets "while DOCK_EN_RET is
under 1.0 V and DOCK_EN_OUT is at 2.0 V or over". Task L4-E11's round 10 drew board A's side with a narrower reading, and the
check V1 confirmed it (finding L4E11-R10-F1, for this record). Quoted from the copy `inputs/l4e11-section20c-4def5975.md`
(L4-E11's round 13; these two passages read word for word as at its rounds 10 and 12):

> The box "RET under 1.0 V with OUT at 2.0 V or over" holds every state board P produces (the return
> at 0.055 V). It also holds a CLOSED loop: RET/OUT is 22 / (22 + RT1), under 0.5 for RT1 over 22 kOhm

> Board A's reading is therefore narrower than the box and holds the state board P produces with 0.72 V
> of margin. The 1.0 V figure is a 2N7002's least threshold (l8p 12f).

A trigger inside the box at a closed loop would stop a dead pack's precharge on its ramp; the narrower reading leaves those ramps
out and still reads the state board P produces. **The interface now reads as board A draws it** (each cell quoted from the copies
of L4-E11's 20c, 20d and 20e at `4def5975`; the U48 thresholds are TI SNVSBJ1E's, as 20c states; every cell reads word for word
as it did at `ac72e730`):

| Item | Board A's reading, quoted | Copy |
|---|---|---|
| The return read held | "under **0.7755 V** at least; read closed over 0.84 V at most" | 20c |
| The loop read powered | "over **1.981 V** at most (1.825 V at least)" | 20c |
| The load on DOCK_EN_RET | "is SENSE1 alone, at most 2 uA" | 20c |
| The inhibit set | "**0.85 ms**, under the interface's 1 ms" | 20d |
| The charge ended | "**The charge through the off breaker ends within 1.41 ms** of passing board P's threshold" | 20d |
| The hold | "It lasts **at least 1.341 s** after the return rises" | 20d |
| The release | "dead under **4.076 V** at least, alive over **4.774 V** at most" (CELL+, read only while an inhibit is asked) | 20c |
| The static limit on the sources into CELL+ while the inhibit holds | "stays under **0.846 mA** together (the static limit)" | 20e |
| The timing limit on them | "inside the hold's least 1.341 s while the sources total under 520.7 uA" | 20e |
| No window on a ramp | "A ramping closed loop never reads held while RT1 is under **25.8 kOhm**" | 20c |

**Board P's side against it** (`l8p_drafts.out` section 3b, computed for the drawn values):
- The return held at 0.055 V at most: 0.721 V under the held reading.
- With the return held, DOCK_EN_OUT is 2.52 V at BRK_VIN 7.6 V and 3.51 V at 10.6 V (RT1 at its 5 kOhm printed least, R106 +1 %,
  the return taken at 0 V): 0.536 V over the powered reading.
- Board P's pull within 0.56 ms plus board A's set within 0.85 ms: 1.41 ms, the sum 20d quotes.
- The breaker restarts within 0.9477 s (the hold 0.907 s and the start 40.7 ms), the same figure 20d uses: 0.393 s before board
  A's hold ends.
- Round 9's Q47 read half of DOCK_EN_OUT, 1.26 and 1.75 V, under the 2N7002's 2.5 V (L8P-F04). Since its round 10 L4-E11 reads
  the return itself with U48 and DOCK_EN_OUT through R109 and R144 (984 kOhm on the loop): **L8P-F04 is answered in L4-E11's
  draft** (section 9).
- The release row's dead reading moved with R256 in L4-E11's rounds: 4.076 V at 4.7 kOhm (rounds 10, 12 and 13), 4.147 V at
  6.8 kOhm (round 11, withdrawn). Round 5 quoted round 10's copy while the candidate held round 11 (the check V2's V2-B2); the
  quote above is round 13's, unchanged from round 12's.
- Board P's own leakage into CELL+ against the two limits is L8P-F06 (12j).

**What L4-E11's round 13 changed in 20c, and what it did not (round 6b).** Its 20c is restated on Murata's printed points (its
23g, with record l9stk's round 4). Quoted from the copy:

> **The loop at 10.6 V and RT1 47 kOhm** (record l9stk's former "bound point"; **withdrawn as a bound by round 13, 23g:** 47 kOhm is
> not a point of this part)

- **No longer stands:** the "bound point" as a bound. 20c still prints the loop's reading there (the first inverter's gate at
  2.894 V with board A's loads), and now says it "bounds nothing". Round 3's interface had asked board A to load the return
  lightly "so l9stk's bound point of the first inverter stays over its 2.5 V"; that reason is gone, while the load itself, at
  most 2 uA, stands. 12e's sentence on it is restated.
- **Stands, word for word:** every row of the table above; the two passages on the box; the first inverter's band (off from 61.3
  to 201.2 kOhm at 10.6 V, nominal); board A reading a closed return as held only past 269 kOhm at 10.6 V.
- **Not quoted here:** L4-E11's 23g also reads what a tripped guard does to DD-7, and what the guard record l9stk has since
  selected would owe. That belongs to the guard's draft, this record's next round.

**What stays with it:**
- The 25.8 kOhm window and board A's powered reading of a held DOCK_EN_OUT (RT1 at least 3.57 kOhm at 7.6 V, the return taken
  at 0 V; the check V1 read 3.46 kOhm with the return at its 0.055 V most) both rest on RT1's resistance away from 25 C, which
  Murata does not print (L8P-F07, 12j).
- **At docking** DOCK_EN_OUT and DOCK_EN_RET rise together at a ratio over 0.4603 while RT1 is under 25.8 kOhm, so the return is
  never read held while the loop is powered (L4-E11 20f).
- **What board A gains:** the inhibit in every off state of the breaker that passes a charge over the threshold, the thermal
  guard's trip and C-1c's hold included.

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
draft), the netlist check's REV group DRAWN on the regenerated netlists and FAIL on two mutations. **Board A's side is drafted by
task L4-E11** (since its round 10; round 13 on `fnd/l4e11r11` at `4def5975`, not on main): U48 reads the held return and the
powered loop, and L8P-F04 and L8P-F05 are answered there (section 9). The independent check V1 read candidate `a09e9a60` and
returned **B-R2: CONFIRMED AS CONDITIONAL**, no blocking item, with conditions C1 to C4. The independent check V2 (an AI review)
read `fnd/v2cand` at `dfa1eef2` and returned, for this record: the ideal diode CONFIRMED AS CONDITIONAL, L8P-F06 and L8P-F07
CONFIRMED real and correctly OPEN, and two statements NOT CONFIRMED (V2-B2, V2-B3), corrected in round 6 (below).

| V1's condition | Owner | State after round 6 |
|---|---|---|
| C1: E-14, E-14b (VSD hot at 0.3 A, at least 0.30 V) and E-12c on the specimen; R10's sheet | this record (the supplier's bench); Layer 6 for R10 | OPEN: physical and vendor evidence (12c, 12g) |
| C2: E11-45, the hold timed at -20, 25 and 85 C, the latch with the breaker held off, the failure rows | L4-E11 | L4-E11's |
| C3, as V1 worded it (round 5 wrote "between 25 C and 110 C"; V2-m4): a Murata question asking for the resistance limits at about 90 C and 120 C, or a guard part whose sheet prints both points; E-13 alone is a sample | record l9stk with this record | OPEN: L8P-F07 (12j); the Murata question, drafted and UNSENT, asks 90, 100, 110 and 120 C; two alternative parts named and not selected; the guard's redesign is record l9stk's next round |
| C4: `l8p_drafts.out` regenerated on the merged line; `check_l8p_netlist.py`'s board A EN group widened to admit DD-7's loads | this record (clerical) | DONE on this branch: the EN group admits DD-7's readers by pin (U48 pin 2, Q44 pin 3, R109) and three mutations of the composed board A fail it; the compositions use L4-E11's drafts with no stand-in (round 12's since round 6); the output regenerated. Round 5's scratch merge was with `a09e9a60`, round 6's with `ac72e730`, round 6b's with `4def5975` (README); the committed candidate is the integrator's |

V1's minors held here: the breaker FETs' hot off leakage (L8P-F06, 12j, OPEN); the held DOCK_EN_OUT reading's least RT1 (3.57 kOhm
with the return at 0 V, 12f). The others (R84's pulse basis, U47's 6.39 mA transient, the hysteresis sensitivity, the CONOPS wording
of the named residual) are L4-E11's and the battery stream's.

| V2's finding (for this record) | State after round 6 |
|---|---|
| V2-B2: the F06 figures and one interface quote a round behind the candidate | CORRECTED: every copy taken again at L4-E11's round 12 (`ac72e730`) in round 6, and again at its round 13 (`4def5975`) in round 6b when the guard fired on the merged candidate; 12f, 12j and E-14c restated on the two limits; a test fails a copy that is not the tree's |
| V2-B3: TDK's "no k exists at 7.6 V", the sure-off taken as an upper bound | CORRECTED: `tdk_window` takes it as a lower bound; a window exists at both voltages; NOT SELECTED on three other grounds (12j) |
| V2-m5 (this record's half): the trip side's junction | RESTATED on the worst split; the mounting base against the sensor's copper named as not bounded (12j) |
| V2-m7: E-16 does not read U105's temperature | ADDED to E-16's acceptance (13g) |
| V2-m8: the pads' 50 C/W cannot all hold at once | ONE SENTENCE in E-8 with the board's 4.57 W (13g; output 3c) |
| V2-m9 (this record's half): board A composed in the main-era order | RECOMPOSED in L4-E9's list order; what the tree lacks is named (section 6) |

These are the author's corrections; V2's targeted recheck of them is owed, and until it reads them they are unverified.

CONDITIONAL on:
- E-14b, the body diodes' VSD read from a typical figure;
- R10's tolerance and temperature coefficient (Layer 6; 1 % and 75 ppm/K assumed);
- E-14 and E-12c on the specimen;
- the breaker FETs' hot off leakage against both of L4-E11's limits (L8P-F06; E-14c).

Not claimed: nothing here is built, bought, powered or measured; the statements are about generator text, netlists and
arithmetic on the makers' printed figures.

### 12j. The findings L8P-F06 and L8P-F07 (round 5; restated in round 6; `l8p_drafts.out` section 3d)

**The labels.** PRINTED: a maker's printed limit. TYPICAL: a maker's typical figure or curve. READ: a value this record reads from
a plotted curve (INFERRED). ASSUMED: an assumption named where it is used. DERIVED: this record's arithmetic on those.

#### L8P-F06: the breaker FETs' off leakage into CELL+ (board P, with L4-E11's latch; on the two limits of L4-E11's round 12 since round 6)

- **What it is.** With the breaker off (latched or held), Q101 and Q102 (CSD18510Q5B) stand off BRK_SNS, which sits at BRK_VIN,
  from PACK_P, which board A ties to CELL+. Each FET's drain-to-source off leakage flows into CELL+, where L4-E11 holds its
  inhibit while CELL+ reads dead.
- **Which budget.** Round 5 took L4-E11's round 10 budget, one limit of 0.846 mA. The check V2 found that a round behind the
  candidate (V2-B2), and found L4-E11's bleed claim not standing (V2-B1). L4-E11's round 12 (R256 at
  4.7 kOhm again) states **two limits** on the sources into CELL+ while the inhibit holds and the breaker is off. Quoted from the
  copies of its 20e and 22g, taken at its round 13 (`4def5975`), where both sections are unchanged:

> The latch reads dead while every source into CELL+ stays under **0.846 mA** together (the static limit).

> **within 1.218 s with the sources at their hot bound
> (434.8 uA, 22b), inside the hold's least 1.341 s while the sources total under 520.7 uA**

> **Between 520.7 uA and 0.846 mA** (not reached at the hot bound): the hold may end with CELL+ still read alive and the breaker off;

- **The timing limit, reproduced here** (DERIVED from L4-E11's printed inputs: R256 4.7 kOhm +1 %; CELL_FUSED 104 uF +20 %, L4-E11's
  ASSUMPTION; from VSYS's 17.375 V to the 4.076 V dead reading; the foot 0.060 V; the sources lifting the level CELL+ falls
  towards): the static limit 846.0 uA, the timing limit 520.9 uA against its printed 520.7 uA, the bleed 1.218 s at its hot bound.
  `l8p_drafts.py` refuses if these part by more than 0.5 %.
- **L4-E11's source list** (its 22b): the LM5069's internal 1 MOhm, 16.8 uA at 16.8 V and 29.2 uA at the 29.2 V clamp (a maker's
  value; its tolerance is not printed); the three battery FETs, 30 uA at Tj 125 C (Nexperia BUK6Y10-30P, 17 April 2020, Table 7
  p.6, printed maxima as L4-E11 and the check V2 read them; that sheet is held back and not read by this record); the breaker
  pair, which is this finding.
- **PRINTED:** TI SLPS632 (March 2017), 5.1 Electrical Characteristics, "TA = 25°C (unless otherwise stated)", p.3: IDSS 1 uA at
  most at VGS 0 V and VDS 32 V (over the 29.2 V clamp). It is the sheet's only IDSS row: nothing above 25 C.
- **ASSUMED:** the off leakage doubles every 10 K from the 25 C row, the convention L4-E11 20d applies to Q51. On it the pair is
  69.8 uA at the 76.25 C air, **388.0 uA at the held 101.0 C case** (record l9stk 15.4) and 2.048 mA at TI's 125 C.
- **DERIVED, against each limit** (the 1 MOhm and the battery FETs' printed 30 uA counted first):

| | The timing limit, 520.7 uA (the pack at 16.8 V, L4-E11's basis) | The static limit, 0.846 mA (the 29.2 V clamp) |
|---|---|---|
| Left for the breaker pair | 473.9 uA (461.5 uA with BRK_VIN at the clamp) | 786.8 uA |
| A breaker FET | 236.95 uA | 393.4 uA |
| In hand with the pair at its ASSUMED 388.0 uA | **85.9 uA** (73.5 uA at the clamp) | 398.8 uA |
| Then left for a battery FET (Nexperia prints 10 uA each at 125 C) | 38.6 uA | 142.9 uA |
| The case at which the pair alone fills it | **103.9 C, 2.9 K over the held case** (103.5 C at the clamp) | 111.2 C |
| The doubling rate at which it fills it at the held case | every 9.63 K or faster (9.68 K at the clamp) | every 8.82 K or faster |

- At TI's 125 C the pair's 2.048 mA is over both. L4-E11's own figures for the timing limit (473.9 uA for the pair, 103.9 C,
  9.63 K, 85.9 uA in hand; its 22c and 22g) are read from the copies and agree with this table; `l8p_drafts.py` refuses otherwise.
- **Superseded:** round 5's single room (816.8 uA, 111.7 C, 8.76 K) counted no battery FET leakage and no timing. The check V2's
  figures on round 11 (568.1 uA, 60.0 uA a battery FET, 106.5 C, 9.33 K) were on R256 at 6.8 kOhm, which round 12 withdrew.
- **Verdict: OPEN.** Both limits hold at the held case only on the ASSUMED doubling, and the timing limit is the nearer one:
  85.9 uA and 2.9 K away. Nothing printed for this part bounds the rate. No printed figure says the latch fails, and none says it
  holds above 25 C.
- **What closes it: E-14c** (board P's specimen, the supplier's bench): IDSS of Q101 and Q102 at VGS 0 V and VDS 29.2 V, at 25,
  101 and 125 C. **Acceptance: the pair at most 388 uA at the 101.0 C held case. That keeps both limits:** the timing limit with
  85.9 uA in hand (73.5 uA with BRK_VIN at the clamp) and the static limit with 398.8 uA. A reading over 388 uA does not meet
  E-14c, even where it is still inside the static room. Over 473.9 uA the bleed no longer ends inside the hold's least 1.341 s,
  which reverses L4-E11's R256 selection (its 22e). Between the two, the margin is L4-E11's to judge on its E11-45 (f2), which
  times the bleed against the same unit's own hold. A reading describes that specimen; TI's answer to the question below bounds
  the part.
- On board P a charge over 0.368 to 1.213 A through the off breaker is still caught by route R1 (12b), whatever the latch reads.
- **The question to TI (DRAFTED, UNSENT; outside contact is the owner's):** "CSD18510Q5B, SLPS632: please state the maximum IDSS at
  VGS = 0 V and VDS = 30 V at TJ = 100 C and at TJ = 125 C, or a curve of IDSS against junction temperature."

#### L8P-F07: the guard RT1's printed points (board A, with record l9stk; V1's condition C3)

- **PRINTED** (Murata DM-SA16-E056 Rev.1 201608, 3.1 Line up, p.4, row PRF15BB103RB6RC, under the header "*at 100kohm" and "*at
  4.7Mohm"): 10 kOhm +-50 % at 25 C; 100 kOhm at a sensing temperature over 110 C, with no upper bound; 4.7 MOhm at 130 +-3 C;
  32 V; operation -20 to +140 C. The only resistance curve drawn (3.2) is labelled typical; 4.1's range figure is marked
  "Reference" and drawn for a PRF18 BB part of the 470 ohm group.
- **Record l9stk 15.5 reads "47 kOhm at 130 C plus or minus 3 C" for this part.** The sheet's 47 kOhm column is the 470 ohm
  groups' (header "*at 4.7kohm *at 47kohm"). So 15.5's band of 127 to 133 C at 47 kOhm, and its "service at the allowances reads
  118.0 C, 9.0 to 15.0 K under the band", do not stand. L4-E11 found the same (L4E11-R10-F3).
- **Read as single crossings** (INFERRED: a sensing temperature is where R reaches the value; that R stays under it below is the
  curve's form, drawn only as typical): under 100 kOhm to 110 C; under 4.7 MOhm to 127 C; over 4.7 MOhm from 133 C.
- **What the loop asks of RT1** (DERIVED: the first inverter Q103's gate is DOCK_EN_RET; board A's 984 kOhm on DOCK_EN_OUT and
  2.08 uA on the return, U48's SENSE1 (20c) and Q107's 80 nA (the 2N7002's printed IDSS); R106 and R107 at 1 %, ASSUMED, each at
  its worse sign; the 2N7002's printed threshold, 1.0 to 2.5 V):

| Need | At BRK_VIN 10.6 V | At 16.8 V |
|---|---|---|
| no trip: RT1 under | 58.4 kOhm (L4-E11 20c's 61.3 kOhm is the nominal) | 110.9 kOhm |
| surely off: RT1 from | 203.4 kOhm (20c's nominal 201.2 kOhm) | 341.2 kOhm |
| a ramping closed loop never read held (20c), the copper at the air | RT1 under 25.8 kOhm | |
| a held DOCK_EN_OUT read powered (12f) | RT1 at least 2.33 kOhm (3.57 kOhm at 7.6 V) | |

- **Where the PTC sits:** record l9stk 15.5 reads the battery FETs' junction at the allowances, held: 89.4 C at 10 A, 118.0 C in
  the 18 A service (its 60 s taken as held), 150.0 C at 23.93 A. The copper is cooler by up to 1.88 K at 23.93 A (about 89.1 and
  116.9 C at 10 and 18 A), so the junction's reading is taken for the PTC: the hot side for the no-trip judgement.

**On the printed points:**

| Side | Reading | Verdict |
|---|---|---|
| The trip, the resistance side | over 4.7 MOhm from 133 C, against the 341.2 kOhm sure-off at 16.8 V: the breaker is off before the PTC's copper passes 133 C | PRINTED |
| The trip, the junction over that copper (V2-m5) | Round 5 wrote "the junction at most 134.9 C", adding the even split's 1.88 K. With L4-E11's worst split the hottest FET dissipates 1.513 W (9/8 of the even split's 1.345 W): 2.12 K over its own mounting base (Rth(j-mb) 1.4 K/W), 135.1 C if that base sat at the sensor's copper. How far the hottest FET's mounting base leads the copper under the PTC no record bounds; 14.9 K are left for it to 150 C | NOT BOUNDED: E11-29's coupon now reads the PTC's site against each junction with one FET heated alone (L4-E11 22h) |
| No trip at 10 A (89.4 C) | under 100 kOhm, against 58.4 kOhm at 10.6 V | NOT PRINTED under a 15.51 V pack; PRINTED from 15.51 V |
| No trip in the 18 A service (118.0 C) | nothing under 4.7 MOhm between 110 and 127 C | NOT PRINTED at any pack voltage |
| The window and the held reading | nothing but the 25 C row | NOT PRINTED |

**On Murata's typical curve** (3.2, p.5; READ by `read_prf_typical.py` at 400 dpi; TYPICAL):
- The curve is drawn per temperature code, normalised to R25. For BB it reads x10 at 115.2 C and x100 at 129.5 C, the 1 kOhm
  group's printed 115 +-5 and 130 +-3 C. At 133 C, where PRF15BB103 prints at least 4.7 MOhm (x313 with R25 at its 15 kOhm most),
  it reads x156. **It is not the 10 kOhm part's own curve above x10**, and it is the only curve the maker draws for it.
- At 10 A (89.4 C): x1.227, RT1 at most 18.4 kOhm. No trip at any pack voltage, inside the window: holds on the typical basis.
- The window: at most x1.515 from -20 C up (the curves' top at -19.5 C), 22.7 kOhm against 25.8 kOhm. The held reading: at least
  x0.749 (the figure's lowest stroke), 3.745 kOhm against 3.574 kOhm. Both hold on the typical basis, the second by 5 %.
- **In the 18 A service held (118.0 C): x14.79, RT1 74.0, 147.9 and 221.9 kOhm** with R25 at its least, nominal and most, every
  one over the 58.4 kOhm at 10.6 V. At 16.8 V the 110.9 kOhm holds only for R25 under 7.50 kOhm. At the copper's 116.9 C: x12.66,
  63.3 kOhm at R25's least, still over. **On the typical curve the guard may turn the breaker off in the 18 A service at record
  l9stk's held reading: there C-PROT's "18 A for 60 s never interrupted" does not hold against the guard.**
- The guard's onset at 10.6 V on the typical curve: 107.3 C (R25 at its most), 111.1 C (nominal), 116.3 C (least). From 10 A held
  (89.4 C) the 60 s service stays under it only if the copper's rise is a first-order step (an ASSUMED form) whose time constant
  is at least 61.1 s, 42.2 s or 21.2 s. No record holds the pad's thermal capacity; record l9stk's 118.0 C is the held reading.

**Verdict: OPEN.** The trip side is printed. The no-trip side is printed only at 10 A from a 15.51 V pack. In the 18 A service it
is not printed, and the only curve the maker draws puts the guard's onset under the held reading. That is neither a printed
failure (the curve is typical and not this part's own) nor a closure. It is a design question for record l9stk's guard (15.5) with
L4-E11 (RT1 on board A) and this record (the loop on board P). E-13, the guard's coupon, stays its test ("no trip through the
service (18 A for 60 s after 10 A held at 76.25 C)"); a reading on that coupon describes that specimen, not every unit.

**The question to Murata (DRAFTED, UNSENT; outside contact is the owner's):**

> Subject: PRF15BB103RB6RC, resistance limits below the sensing temperature
>
> Your data sheet DM-SA16-E056 Rev.1 (August 2016), 3.1 Line up, gives PRF15BB103RB6RC as 10 kOhm +-50 % at 25 C, 100 kOhm at a
> sensing temperature above 110 C, and 4.7 MOhm at 130 +-3 C. We use the part as an overheat sensor in series with a 32 kOhm
> divider at 10.6 to 16.8 V (0.2 to 0.45 mA). Please state, for the part as delivered:
> 1. the maximum resistance at 90 C, 100 C, 110 C and 120 C, or the temperature range over which it stays under 58 kOhm, at a
>    measuring current of 0.5 mA or less;
> 2. the minimum resistance from -20 C to 125 C;
> 3. the upper limit of the 100 kOhm sensing temperature, which the sheet gives only as above 110 C;
> 4. whether the typical curve of 3.2 applies to the 10 kOhm group, whose 4.7 MOhm point at 130 +-3 C lies about 10 K under the BB
>    curve's reading at that ratio;
> 5. whether a resistance-temperature range document like 4.1's (shown for a PRF18 BB part) exists for PRF15BB103RB6RC.

**The alternative parts (named, NOT SELECTED; SESSION):**

| Part | What it prints | Against the loop | Verdict |
|---|---|---|---|
| Murata PRF15BA102RB6RC (the same sheet, p.4) | 1 kOhm +-50 % at 25 C; 10 kOhm at 125 +-5 C; 100 kOhm at 140 +-3 C; -40 to +150 C | under 10 kOhm to 120 C prints the no-trip side at 10 A and in the 18 A service; its 100 kOhm point is under the 341.2 kOhm sure-off (the trip not printed), and its least R25, 500 ohm, is under the 3.57 kOhm held reading | not a part swap |
| TDK B59721A0130A062 (superior series, EIA 0805; TDK's sheet of August 2019, held back by its notice, `fetch_held_back.py`) | p.4: 680 ohm +-50 % at 25 C; R(Tsense - 5 C) at most 5.5 kOhm; R(Tsense + 5 C) at least 13.3 kOhm; R(Tsense + 15 C) at least 40 kOhm; Tsense 130 C; 32 V. p.29, the part's own table, headed "Rmin and Rmax values are typical values for reference only": Rmin 212 ohm at 100 C | limits on both sides, as C3 asks: no trip to 125 C, off by 145 C. Its 40 kOhm is under the 341.2 kOhm sure-off, so the loop would scale by k (R106, R107 and the guard together, which keeps every level of 20c). **The bounds on k (corrected in round 6, V2-B3):** no trip, k x 5.5 kOhm at most 58.4 kOhm: k at most 10.62. Surely off, k x 40 kOhm at least 341.2 kOhm: k at least 8.53, a LOWER bound (round 5 took it as an upper one and wrote "no k exists at 7.6 V"). The held reading on its least R25, 340 ohm: k at least 10.51 at 7.6 V, 6.84 at 10.6 V. **A window exists on the printed limits: 10.51 to 10.62 at 7.6 V (1.0 % wide), 8.53 to 10.62 at 10.6 V.** | NOT SELECTED, on three grounds. (1) Dissipation: 18.1 to 21.4 mW in the part at its printed 5.5 kOhm (k 8.53 to 10.62, the pack at 16.8 V), against the sheet's note on p.4, "the electrical power during measurement should be below 6 mW for EIA case size 0805": its printed limits are read under that power and are not its limits at three times it. (2) Static draw: 4.11 to 5.01 mA in the loop, against record l9stk's 0.45 mA. (3) The sheet's own reference table (TYPICAL): Rmin 212 ohm at 100 C asks k at least 16.86 at 7.6 V and 10.98 at 10.6 V, over the 10.62 that no trip allows, so on that table no k exists at either voltage (round 5 applied such a dip to Murata's part and not to TDK's) |

A third approach, for record l9stk's owner and not drafted here: an NTC read by a comparator, as C-1c reads the breaker pad on
board P (section 4), whose trip and no-trip points rest on printed NTC and resistor tolerances. It makes board A's guard active
rather than a passive series element.

**SESSION decision (round 5, its reason corrected in round 6):** RT1 stays PRF15BB103RB6RC in the board A draft. Why: no part
read prints both sides inside the present loop. The one that prints both (TDK's) needs the loop rescaled about tenfold; a window
for that scale exists on its printed limits, but there the part dissipates three times the power its limits are read under, the
loop draws about ten times its present current, and the part's own typical table closes the window. A loop rescale or an active
guard changes record l9stk's design (15.5) and L4-E11's levels, which are their owners'. Reversed by a guard round of record
l9stk that selects another part or approach; the A draft's RT1 line then changes with it. That round is running now (record
l9stk's author is comparing approaches); its draft is assigned afterwards and is not part of this round.

## 13. DD-5: the charge switch's body diode in discharge (round 4; `l8p_drafts.out` section 3c)

**The case row: C-PROT**, record l9stk 15.1's criterion at set 29's line `e58e906a` (l9stk at `0d72880b`, copied in `inputs/`):
10 A held and 18 A for 60 s never interrupted; every series part within its limits below and above the trip; the start at
L4-E12's 76.25 C plus own heating; the breaker's band 18.32 to 23.93 A. For DD-5, the state that makes it bite: CHGIN = 1 above
T3, in discharge. Nothing is labelled unsettled.

**The defect** (record l9stk 15.5 to 15.7, DD-5; finding L9C-F21; the battery packet's BAT-F20, EQ-15, S-46). With FET Options
CHGIN = 1 the BQ4050 trips its charge inhibit while "Not charging" in the High Temp range and sets XCHG = 1 (SLUUAQ3A, revised
October 2022, 4.13, p.40; 14.2.1.1, p.116: "Charging and Precharging disabled, FETs off"). "Not charging" is relax and discharge
alike, so above T3 the discharge current crosses Q1's body diode:

| Discharge | In Q1's diode (VSD 1 V at most, SLPS471D 5.1, printed) | Against the 1.48 W its pad holds from 76.25 C |
|---|---|---|
| 10 A held | 10.0 W | 6.8 times |
| 18 A for 60 s | 18.0 W | 12.2 times |
| the breaker's 23.93 A held | 23.9 W | 16.2 times |

Record l9stk reads the same defect as 7 to 10 W at 10 A (OVER by 4.7 times), 23.9 W held, and 266 C in its retry table.

### 13a. Three approaches compared

| | (i) The gauge keeps Q1 on in discharge | (ii) A diode path that may carry the service | (iii) An ideal diode beside Q1 (SELECTED) |
|---|---|---|---|
| What it is | A function of the BQ4050 that turns the charge FET on while discharge current flows and charging is inhibited; or the setting CHGIN = 0 | A Schottky rectifier across Q1 | A second FET beside Q1, driven by an ideal-diode controller on its own drain-to-source voltage |
| Printed data | **No such function is printed:** "body diode" occurs nowhere in SLUUAQ3A or in the data sheet SLUSC67B, and no table turns the charge FET on in discharge (4.12, 4.13, 4.14). CHGIN = 0 is printed (14.2.1.1: "0 = FET active (default)") | On Q1's pad (50 C/W at most, 1.48 W) the forward drop may be 0.148 V at 10 A, 0.082 V at 18 A and 0.062 V at 23.93 A; with Q2's loss on the same pour, 0.032 V at 23.93 A | LM74700-Q1 (SNOSD17G, revised December 2020): regulated forward drop 13 to 29 mV; CSD17570Q5B (SLPS471D): 0.69 mOhm at most |
| What it changes | The golden image (FET Options 0x3D to 0x2D) | One large rectifier and its heat path on board P | Q109, U105 and nine small parts on board P; no setting |
| What it needs | With CHGIN = 0 the inhibit above T3 only writes ChargingCurrent() 0 and no longer opens Q1: the charge start above 42 C then rests on the charger's obedience and on OTC. That reduces the ladder's level L4a, and it is outside the case row, which fixes CHGIN = 1 | No junction diode prints such a drop (a Schottky's 0.3 to 0.5 V at its rated current is a statement of the class; the kit holds no sheet of a 25 A class Schottky, only 1 A and 5 A parts: ASSUMPTION). At 0.3 V the pad would have to be 25 K/W at 10 A and 10 K/W at 23.93 A, on a 70 x 44 mm board | The kit's own parts (board E's U3 and this board's Q1); 51.4 K/W for the SW pour (E-8, as today's enhanced row asks) |
| The breaker draft, B-R2's detector, IF-1, DD-7, the copper | No effect on the circuit; the battery stream's ladder, mode table and tests change | The rectifier's leakage hot, its heat beside F2 and RT1, a new band | None on the breaker, the detector, IF-1 or DD-7 (13e); Q109 on Q1's two bands |
| Verdict | **DROPPED**: the function is not printed, and the setting reduces a protection | **NOT SELECTED**: not supported on printed data | **SELECTED** |

A separate charge path (EQ-15's option b) is not a fourth approach: with one terminal for charge and discharge it needs the same
ideal diode in the discharge path.

### 13b. The correction drawn (`apply_gen_sch_p_idealdiode.py`)

| Ref | Value | What it does | Decoupling class |
|---|---|---|---|
| Q109 | CSD17570Q5B (Q1's part, C529279), PowerPAK SO-8 | Source on SCP_OUT, drain on SW, as Q1: its body diode points as Q1's, and off it blocks a charge as Q1 does | |
| U105 | LM74700QDBVRQ1 (board E's U3 part, C2941042), SOT-23-6 | ANODE on SCP_OUT, CATHODE on SW, GATE on Q109's gate alone, GND on the cells' negative. Forward: it holds 20 mV (13 to 29 mV) across Q109 by its gate, and connects the gate to its charge pump above 50 mV. Reverse: the gate is at the anode | |
| C111 | 220 nF 50 V X7R 0805 | VCAP to the anode: the charge pump's reservoir | L: TI 10.1.1.2.3, at least 0.1 uF and ten times Ciss (0.136 uF); ESR not stated |
| R130 | 10 MOhm | Q109's gate to its source, as R17 on Q1: an open GATE pin leaves Q109 off | |
| D104, R131 | 1N4148W (C81598); 1 MOhm | EN from BRK_VIN, with 1 MOhm to ground: U105 runs only while the gauge holds the discharge FET on or a charger is present. The diode keeps a negative transient of BRK_VIN off EN (-0.3 V) | |
| C112, C113 | 100 nF 50 V X7R, in series | The anode's capacitance, 50 nF (TI: at least 22 nF) | C112 D: ANODE is the supply pin |
| C114, C115 | 470 nF 50 V X7R 0805, in series | The cathode's capacitance, 235 nF (TI: at least 100 nF) | C114 B2: no distance stated |
| TP109 | test point | Q109's gate, for E-12d | |

Nets: IDL_GATE, IDL_VCAP, IDL_EN, IDL_AMID, IDL_CMID. The intent re-declares SCP_OUT's loads (Q1 and Q109) and SW's sources
(Q1 and Q109).

### 13c. The SESSION choices

| Choice | Taken | Why |
|---|---|---|
| A second FET beside Q1, not a second driver on Q1's gate | Q109 | The gauge's CHG drive, R16 and R17 stay as TI draws them, so its charge blocking and its CFETF check are untouched. The netlist check fails a GATE wired to Q1's gate |
| The FET | Q1's own part | At 23.93 A hot it must stay near 0.7 W: 1.24 mOhm or less. A FET inside TI's guideline window at 10 A (2 mOhm) would dissipate 2.06 W there |
| EN's source | BRK_VIN through D104 | An always-on U105 would draw up to 130 uA from a pack whose gauge has shut down. BRK_VIN is live only while the gauge holds Q2 on, or a charger is present |
| Series pairs | C112 with C113, C114 with C115 | As C11 and C12 (O-12): one shorted part across the cells must not short them |
| U105's ground | GND, the cells' negative | As the gauge's VSS; its 0.13 mA is under the coulomb counter's resolution either side of R10 |
| Designators and nets | Q109, U105, D104, R130, R131, C111 to C115, TP109; IDL_* | The 100 block, after round 3's |

### 13d. The electrical acceptance on C-PROT with CHGIN = 1

**The labels.**
- **Printed guarantees:**
  - V(AK REG) 13 / 20 / 29 mV, full conduction above 34 / 50 / 57 mV, reverse blocking at -17 / -11 / -2 mV within 0.75 us,
    and the gate drive 10.8 to 13.9 V over the anode (SNOSD17G 6.5 and 6.6, TJ -40 to 125 C);
  - RDS(on) 0.69 mOhm at most at VGS 10 V and 25 C, RthJA 50 C/W at most on 1 in2 of 2 oz, TJ 150 C (SLPS471D 5.1, 5.2).
- **Assumption:** RDS(on) 1.8 times hot, as record l9stk takes it (E-8); and both losses through one pad of 50 C/W, l9stk's
  bound for Q1 and Q2 on the SW pour.
- **Typical, read by eye:** the CSD17570Q5B's own Figure 8 gives 1.68 times at 150 C.
- **Model:** Q109's loss is the current times the larger of the regulated drop and the current times RDS(on) hot. The regulated
  drop is taken at 29 mV plus 1.24 mV for R130 and the gate's leakage through the error amplifier (1200 uA/V at least): 30.24 mV.

| Case (from 76.25 C) | Q109 | Was, in Q1's diode | Q2 | TJ on its own pad | TJ, both through one pad | Limit |
|---|---|---|---|---|---|---|
| 10 A held | 30.24 mV, 0.302 W | 10.0 W | 0.124 W | 91.4 C | 97.6 C | 150 C |
| 18 A for 60 s (taken as held) | 30.24 mV, 0.544 W | 18.0 W | 0.402 W | 103.5 C | 123.6 C | 150 C |
| the breaker's 23.93 A held | 30.24 mV, 0.724 W | 23.9 W | 0.711 W | 112.4 C | 148.0 C | 150 C |
| the breaker's largest threshold, 50.59 A, until it clears (1.292 ms) | 62.8 mV, 3.18 W | | | 2.5 K over its case | | |

- **The installed path this asks:** 51.4 K/W or better for the hottest junction with both losses counted. That is E-8, restated
  with Q109; record l9stk's enhanced row asked the same of Q1 and Q2 (147.4 C).
- **On the typical basis** (0.56 mOhm times 1.68, the regulation's 20 mV, 40 C/W): 119.3 C at 23.93 A held.
- **With Q1 on** (below T3) the two FETs share, and the pair's loss is at most Q1's alone (0.711 W at 23.93 A): no row of
  l9stk 15.5 is worsened.
- **The service is not reduced:** an ideal diode cannot refuse a discharge. With U105 dead or disabled the body diodes still
  conduct (SNOSD17G 9.4.1), which is the defect's state and not an interruption.

**The condition that stays (E-16).** TI's guideline (10.1.1.2.2) asks RDS(on) between 20 mV and 50 mV over the nominal current:
2.0 to 5.0 mOhm at 10 A, 1.11 to 2.78 at 18 A, 0.84 to 2.09 at 23.93 A. Q109's 0.56 to 1.24 mOhm is under it at 10 A, where
U105 holds it in regulated conduction (the sheet's light-load mode), and at its edge above 18 A. That the regulation settles
with this FET is a model (a first-order loop: the error amplifier into the gate's capacitance), not a printed guarantee. If it
did not settle, the drop is still bounded by the full conduction threshold, 57 mV:

| Case | Q109 at most | TJ, both through one pad of 50 C/W |
|---|---|---|
| 10 A held | 0.570 W | 111.0 C |
| 18 A held | 1.026 W | 147.7 C |
| 23.93 A held | 1.364 W | 180.0 C: OVER |

So the 10 A and 18 A rows hold either way, and the 23.93 A row rests on E-16 unless the SW pour is 35.5 K/W or better with both
losses counted. **That is the layout's target** (section 7; the bottom face is free).

**Delays and the transitions** (printed limits unless marked):
- **U105's start.** It drives 11.61 ms at most after EN (ENTDLY 110 us; C111 at +10 % to 7.7 V at 162 uA). The breaker's hold
  keeps every load off for 0.110 s at least after BRK_VIN rises, so only the start's 0.659 A crosses the body diodes meanwhile.
- **Q1 turned off under load** (the inhibit trips in discharge). Q109's gate is up within 85.5 us (2.6 us, then 249 nC at 3 mA;
  the charge is a model). The body diodes carry the current meanwhile, at most 19.1 K over the case (VSD times RthJC).
- **C111.** At least 0.158 uF derated (10 % tolerance, 20 % for its bias, ASSUMED) against ten times Ciss, 0.136 uF. VCAP falls
  1.57 V as the gate connects, from 10.8 V at least to 9.23 V, over its 6.0 V lockout.
- **EN.** On from BRK_VIN 3.31 V (2.6 V at most, plus D104's 0.715 V at 1 mA); off under 0.5 V.

**The charge blocking, unchanged:**
- The gauge's drive of Q1 is not touched, and Q109 is off in reverse: "ensures zero DC reverse current flow" (SNOSD17G 9.4.2.1).
- What crosses when Q1 is off: Q1's and Q109's IDSS (1 uA each at 24 V and 25 C). U105's cathode current, 2.2 uA at most, goes to
  ground, not into the cells.
- A reversal faster than the regulation follows is ended by the comparator within 0.75 us from 30.4 A (17 mV over the typical
  0.56 mOhm; no minimum is printed). Under that, the regulation's sink (6 uA at least) ends it in 41.5 ms: 0.46 C at board A's
  largest 11.1 A. Both are a model.

### 13e. The rest of the pack path

- **The breaker draft:** unchanged. BRK_VIN gains D104 and R131 (17 uA at 16.8 V) and U105's EN (5 uA).
- **B-R2's detector (section 12):** unchanged. With Q1 off a charge is blocked by Q1 and Q109, so R10 carries none and U103
  stays low.
- **IF-1 and the breaker's start:** unchanged. U105 is driving before any load (13d).
- **DD-7 and board A's charge inhibit:** unchanged; nothing new crosses the dock.
- **The gauge:** no setting changes (IF-4). Its discharge protections act through Q2, which Q109 does not bypass. Q109 conducts
  in every state that holds Q1 off in discharge (the inhibit, COV, sleep with SLEEPCHG = 0), not only above T3.
- **The copper:** Q109 sits on Q1's two bands; no new band. The SW pour carries the same two losses record l9stk already counts.
- **Standby:** U105 draws 80 uA typical and 130 uA at most while the gauge holds the discharge FET on (152 uA with R131 and EN at
  16.8 V), and 2.5 uA at most with the gauge shut down.

### 13f. The closure credit

| Condition | Reading |
|---|---|
| (a) It composes with board P's other pending drafts in change-list order, and the generator runs | The breaker draft, then the ideal diode, then l6r2's two tables: every step OK; the pair first and the pair last: every step OK; the composed generator ran to its end (169 parts, intent written). The ideal diode draft refuses a target without the breaker draft, and a second application (`l8p_drafts.out` sections 4, 5 and 7) |
| (b) Its changed nets are read in the regenerated netlist, with a mutation that fails | DIO reads DRAWN on the regenerated board P. FAIL with Q109's source and drain exchanged, with U105's GATE on Q1's gate, and (in the tests) with U105's ANODE and CATHODE exchanged, D104 reversed and U105's GND on PACK_N. FAIL also on the breaker draft without the ideal diode |
| (c) The electrical acceptance holds | Section 13d: Q109 inside its printed limits at 10 A held, 18 A held and 23.93 A held from 76.25 C, on the labelled basis |

A netlist check is not electrical acceptance, and nothing here is a measurement. **The claim made: DD-5 is corrected in the
draft, and its electrical acceptance holds on printed limits.** Not claimed: implemented, independently checked, built or
measured.

### 13g. What stays open

| Item | Specimen | Acceptance | Owner |
|---|---|---|---|
| **E-8, restated** | Board P's first specimen, the three FETs on the SW pour | The hottest junction under 150 C at 23.93 A held from 76.25 C, with CHG off (Q109 and Q2) and with CHG on (Q1, Q109 and Q2); the pour at 51.4 K/W or better with both losses counted, 35.5 K/W as the target. **The joint case (round 6, V2-m8):** the sheet's 50 C/W is one device on 1 in2 of 2 oz on a 1.5 in x 1.5 in board; the SW pour and IF-2's two pads for the breaker FETs would be three such boards, 6.75 in2, on a 70 x 44 mm board of 4.77 in2 a face that also carries R10 and the sense pair, 4.57 W in all at 23.93 A held: the pads' figures cannot all be the sheet's at once without another heat path (the leads, the bottom face). E-8's specimen carries the current through every part, so it measures that joint case, not each pad alone | Board P's PCB generator; the supplier's thermal bench (the body diode's VSD method) |
| **E-16**, the ideal diode's regulated drop and its reverse blocking | The same specimen, CHG held off by the gauge (the FET test command, SLUUAQ3A 13.1.12, or a reading above T3) | SCP_OUT to SW (TP13 to TP5) at 2.5, 10, 18 and 23.93 A, at 25 C and at the 76.25 C air: within 13 to 30.3 mV, or the current times RDS(on) where that is larger; steady, with under 10 mV peak to peak of ripple. **U105's package at most 125 C at 23.93 A held (round 6, V2-m7):** TI prints V(AK REG) for TJ -40 to 125 C only (SNOSD17G 6.5), and the FETs' pour beside it is near 147 C on that row. A source at PACK_P 2 V over the cells with CHG off: under 1 mA into the cells (the two FETs' leakage) | The supplier's bench |
| **E-12d**, a commissioning check like E-12 | The built pack at commissioning and at each service | With CHG held off and a discharge of 2 A or more: TP13 to TP5 under 60 mV (a body diode reads 0.4 V or more), and TP109 over TP13 by more than 1 V | The supplier's commissioning procedure |
| C111's capacitance at 14 V and hot | The part's sheet | At least 0.136 uF | Layer 6 |
| U105 directly on the cell node; a welded Q109's detection (CFETF enabled in the golden image); the standby | | | The battery stream's review |

### 13h. The ideal diode's own failures

| Failure | Effect | Found by |
|---|---|---|
| U105 dead or its EN low (D104 open); C111 shorted; U105's GATE open | Q109 stays off behind R130 and the body diodes carry the discharge: the defect's state returns, latent. No interruption | E-12d |
| Q109 shorted, or its gate stuck high | The charge blocking is lost while Q1 is off: the gauge reads a charge with CHG off and sets CFETF (SLUUAQ3A 3.10), as for a welded Q1; the second level stands behind it | The gauge |
| Q109 open | As U105 dead | E-12d |
| D104 shorted | EN follows BRK_VIN, a negative transient included (EN's -0.3 V); latent | not found by a check here |
| R131 open | EN is pulled low by U105's own sink alone (3 uA typical; no minimum printed) | not found |
| One capacitor of a series pair shorted | Its partner holds the voltage (50 V parts) | not found |
| A short inside U105 from ANODE to GND | Behind F1 and F2 only, as section 13g names for the battery stream | |
