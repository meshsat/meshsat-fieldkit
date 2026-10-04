# L8P-BREAKER: W4DP-F2's breaker drawn for boards P, E and A (Layer 8 record l8p)

Record `l8p`, MESHSAT-1357, 4 October 2026, branch `fnd/l8p` from main `64cd25ee`. The author is board P's generator author
for this one correction.

**Status: DRAFTED, not applied.** Three release-guarded apply scripts, a netlist check and their proof on scratch copies.
Nothing in this kit has been built, bought, powered or measured. Every apply script refuses the repository's own generator
until a `RELEASE.md` beside it reads `released: yes` and names an accepted check of this record; none exists.

**The defect.** W4DP-F2, as record `l9stk` section 15 states it (branch `fnd/l9stk` at `2c8b29fb`, independently checked
CONFIRMED AS CONDITIONAL, its text corrections in):
- DD-1: with board P's FETs Q1 and Q2 welded and no firmware, nothing on board P opens the discharge path on current alone
  (15.2).
- DD-6: a docking with a breaker that is already on reaches E11-30's 242.9 A, past the breaker FET's SOA and past VIN to
  SENSE's 0.3 V maximum (15.4, B-P1).

**The design drawn** is l9stk's, unchanged:
- C-1: an LM5069-2 circuit breaker on board P, from Q2's source to the pack terminal.
- C-1b: a make-last dock enable loop into its UVLO, with an RC hold.
- 15.5: the thermal guard, a PRF15BB103 PTC in that loop on the battery FETs' copper on board A.

Every value comes from the record by its section (section 2). Where the record leaves a choice to the drawing, it is taken
here as SESSION under the owner's standing rule of 26 September 2026 (section 3). The record's own copies are in `inputs/`,
pinned by `inputs/SOURCES.txt`.

## 1. The three drafts

| Draft | Board | What it draws |
|---|---|---|
| `apply_gen_sch_p_breaker.py` | P | The breaker U101 with its sense pair, FETs, power limit, timer, dv/dt capacitor, input clamp and input bypass. The enable loop's two inverters, the RC hold and the discharge. J_SMB as a 1x7 with the loop on pins 5 and 7 and the return on pin 6. The gauge's PACK and VCC taps and Q2's R19 moved to Q2's source (IF-6). PACK_P re-declared as the breaker's output. Four test points for E-12. One schematic section. |
| `apply_gen_sch_e_enable.py` | E | J_SMB as the same 1x7, pin for pin. J_BLK pins 3 and 5 carry the loop to the block, with pin 4 ground between them. The loop's two nets declared. Board E is a pass-through: no part. |
| `apply_gen_sch_a_ptc.py` | A | J_DOCK pins 3 and 5 carry the loop, with pin 4 ground between them. RT1, the PRF15BB103, closes the loop on the battery FETs' copper. The loop's two nets declared. |

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

| Ref | Value | l9stk source |
|---|---|---|
| U101 | LM5069MM-2, LCSC C111822 (board E's U6 part); VSSOP-10 | 15.4, C-1: "an LM5069-2 circuit breaker on board P, from Q2's source to PACK_P"; the controller row |
| R101 | 4 mOhm 1 % 2512, at most 50 ppm/K | 15.4 table, Sense RS: "4 mOhm and 7.5 mOhm in parallel, 2.6087 mOhm, 1 % and at most 50 ppm/K" |
| R102 | 7.5 mOhm 1 % 2512, at most 50 ppm/K | as R101 |
| Q101, Q102 | CSD18510Q5B, LCSC C2876544 (board A's PA stage part), PowerPAK SO-8 | 15.4 table, FETs: "2 x CSD18510Q5B" |
| R103 | 8.45 kOhm 1 % (RPWR) | 15.4 table, Power limit: "RPWR 8.45 kOhm" |
| C101 | 10 nF 50 V X7R (TIMER) | 15.4 table, Fault timer: "10 nF" |
| C102 | 22 nF 50 V X7R (GATE to the return, dv/dt) | 15.4 table, dv/dt start: "22 nF into 593 uF" |
| D101 | SMCJ18A, LCSC C374030 (board A's VBAT clamp part), cathode on BRK_VIN | 15.4 table, Clamps: "SMCJ18A on VIN"; IF-6: it returns to PACK_N |
| R104 | 200 kOhm 1 % (R_U, BRK_VIN to UVLO) | 15.4 table, Controller: "UVLO from VIN through R_U 200 kOhm" |
| C103 | 3.3 uF 50 V X7R (C_U, UVLO to the return) | 15.4 table, Controller: "into C_U 3.3 uF (50 V)" |
| R106 | 10 kOhm (BRK_VIN to the loop) | 15.4 C-1b: "The loop leaves board P from VIN through 10 kOhm on one J_SMB contact" |
| R107 | 22 kOhm (the loop's return to the return) | 15.4 C-1b: "a 22 kOhm divider on a first 2N7002's gate" |
| Q103 | 2N7002 (JSCJ, C8545), the first inverter | 15.4 C-1b |
| Q104 | 2N7002, the second inverter | 15.4 C-1b: "the second, when on, discharges UVLO through 150 ohm" |
| R105 | 150 ohm (Q104's drain to UVLO) | 15.4 C-1b |
| R108, R109 | 1 MOhm each (the second inverter's gate divider) | `l9stk_protection.py` constant R_G, "the second inverter's gate divider, each half" (prot 3a's undocking time and the gates' bound): the one value the page does not print |
| RT1 (board A) | PRF15BB103RB6RC, Murata, LCSC C443668 (board P's RT1 part and 0402 land) | 15.5, THE THERMAL GUARD: "the kit's PRF15BB103 chip PTC ... In the enable loop on the battery FETs' copper" |

The connections are the record's too:
- OVLO to the return (15.4, the controller row).
- The clamp, the controller and its small parts return to PACK_N (IF-6).
- D1 stays on PACK_P and carries the lead's freewheel at turn-off (15.4, the clamps row).
- The gauge's PACK and VCC taps stay on Q2's source node (IF-6).
- A ground contact sits between the loop conductors in J_SMB and on the block (C2).

`l8p_drafts.py` section 2 finds each row's text in the copy of the record and refuses when a pattern no longer matches. The
netlist check reads each value prefix back from the regenerated netlist.

## 3. The SESSION choices (what the record leaves to the drawing)

| Choice | Taken | Why |
|---|---|---|
| Designators | Board P: the free 100 block (U101; Q101 to Q104; D101; R101 to R109; C101 to C105; TP101 to TP104). Board A: RT1. Board E: none. | A block no other draft of board P uses, so a later draft that takes the next free number cannot meet it. Board A carries no RT designator. |
| Net names | BRK_VIN (Q2's source, the breaker's input), BRK_SNS, BRK_GATE, BRK_TMR, BRK_PWR, BRK_UVLO, BRK_G2, BRK_DIS, BRK_CMID. DOCK_EN_OUT and DOCK_EN_RET on all three boards. | The dock contract (`check_contracts.py` section 4) compares J_DOCK and J_BLK by net name. |
| J_SMB | A JST-XH 1x7 (B7B-XH-A, the same header row of the held catalogue) at both ends. Pins 1 to 4 unchanged (SMBC, SMBD, the return, PRES). 5 DOCK_EN_RET. 6 the return. 7 DOCK_EN_OUT. | The record asks for two loop conductors on J_SMB with a ground contact between them, and PRES stays. Keeping round 4's order needs three new positions, so the lead gains contacts 5 to 7, not one. DOCK_EN_OUT, the conductor at BRK_VIN through 10 kOhm, sits at the row's end beside ground only. DOCK_EN_RET sits beside PRES: a short there pulls the gate side, and never puts BRK_VIN on an unpowered board E's GPIO17. |
| Dock positions | J_DOCK and J_BLK pins 3 (DOCK_EN_RET) and 5 (DOCK_EN_OUT), with pin 4 ground between them in the 2 x 6 field's first row. | These are the only two free ground positions in one row with a ground between them where the outgoing conductor has no signal neighbour: pin 5's neighbours 4, 6 and 11 are ground. Pin 3's neighbour below is USB_E6_P (pin 9); see section 9. |
| Input bypass | C104 and C105, 2.2 uF 50 V X7R in series through BRK_CMID (1.1 uF), at the sense pair. | IF-2 asks for "VIN's bypass at RS (the sheet's 11.1)". TI SNVS452G section 10: "TI recommends placing a 1-uF ceramic capacitor to ground close to the drain of the hot swap MOSFET". 11.1.1: "place the bypass capacitor close to Rsns instead of the VIN pin". It is drawn in series, as C11 and C12 are (O-12; SLUSC67B 8.2.2.1.5), because one shorted part across the pack must not short it. |
| PGD | Left open. | IF-1's PGD option would need a conductor to board A. That is L4-E11's to decide (section 6). |
| Test points | TP101 BRK_VIN, TP102 BRK_UVLO, TP103 DOCK_EN_OUT, TP104 DOCK_EN_RET. | E-12's commissioning steps: PACK_P dead undocked against a live input, the hold's release after the enable mates, and each loop conductor shorted to ground in turn. |
| Lands | VSSOP-10 (as board E's U6), SMC (as board A's D1), 2512 for the sense pair, PowerPAK SO-8 for the FETs, the 7-circuit XH header, board P's 0402 for RT1. | The kit's own lands for these parts. |

The coordinator's brief named "a fifth J_SMB contact". The record's text (two J_SMB contacts with a ground between, DD-6's
owner row and C2) is what is drawn: three new positions, 5 to 7.

## 4. Designators per draft (`l8p_drafts.out` section 5)

| Board | This record's | Against every other draft of the board, composed in L4-E9's order |
|---|---|---|
| P | U101, Q101 to Q104, D101, R101 to R109, C101 to C105, TP101 to TP104 | DISJOINT (l6r2's two board P drafts add none) |
| E | none (nets only) | DISJOINT |
| A | RT1 | DISJOINT (L4-E4 to L4-E11, l8gnd, l8r2, d8dec31's mainpb, l6r2) |

No literal part call is drawn twice in any composed generator.

The third battery FET of 15.5 (SELECTED) is **not drawn here**: its designator is L4-E11's to give, since Q41 is record
l8r2's VIN_RAW cut-off FET.

## 5. Order constraints for L4-E9's change list

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
4. **Board A: step 3, any position.**
   - It inserts before two lines that l8gnd's GND-002 draft also inserts before (each keeps the line once).
   - It replaces no text L4-E11's charger (R-157) replaces.
   - It adds no R or C, so d8dec31's mainpb (R-193, 3h) still takes R248 and C247.
   - Shown after 3g and before 3h, and also first and last.
5. **Before P and E are regenerated and judged:**
   - `check_contracts.py` section 15c's role table needs a role for the loop's two nets (owed to the tools owner, section 6).
     Without it, P's J_SMB pins 5 and 7 read "unknown" and the contract fails.
   - Layer 5's interface rows go in the same release (section 6).
6. **The layout follows the schematic.** The board P PCB generator draws IF-2 and the bands; board A's places RT1; board E's
   places the 7-way land (section 6).
7. **Record l8r2's later rounds** (branch `fnd/l8r3` at `89924e40`, not on main) were also checked once on scratch copies,
   outside the script: board A's fb01, slotlm and packrtn and board E's packrtn compose with this record's drafts, before
   and after them.
8. **The regeneration steps R-11 and R-22 are blocked today by three other drafts' run-time refusals** (section 8), with or
   without this record. This record adds no refusal: with scratch stand-ins for those three, the composed generators run to
   their end and the loop reads DRAWN.

## 6. Interface rows owed

| Owner | Row |
|---|---|
| **Layer 5** (IF-PE-PACK, `pcb_interfaces.yaml`) | **The fifth to seventh J_SMB contacts:** J_SMB at both ends a JST-XH 1x7 (B7B-XH-A): 1 SMBC, 2 SMBD, 3 GND (the pack side of the shunt), 4 PRES, 5 DOCK_EN_RET, 6 GND, 7 DOCK_EN_OUT. The lead is a straight 7-way XH-to-XH lead. Pin 6's second ground wire runs in parallel with the 12 AWG return as pin 3's does (O-5, a harness matter). |
| **Layer 5** (IF-AE-DOCK) | **The dock enable contacts:** J_DOCK and J_BLK pin 3 DOCK_EN_RET and pin 5 DOCK_EN_OUT, with pin 4 GND between them; the E5 block passes each contact to its own wire. |
| **Layer 5** (IF-5; CONOPS, with the battery stream) | **PACK_P live only while docked:** the pack's terminal is dead whenever the enable loop is open. Any host other than the dock must close the loop through its own path or gets a dead terminal (fail-safe). Board A's J_PRE1 and R1 are no longer exercised at docking. |
| **Layer 7** | **The make-last contact's 1 mm (C1):** J_DOCK positions 3 and 5 mate at least 1 mm after every power pin (J_CP1 to 4, J_CN1 to 4, J_VR1 to 4, J_VN1 to 4) at any angle the dock's guides allow. The RC hold tolerates a reversed order up to 111.6 ms; beyond that, the order is Layer 7's condition. If the Preci-Dip 813 strip cannot be set 1 mm short as a whole, those two positions take separate shorter pins (a board A land change, with board A's generator). |
| **Layer 7** | **The mating order C1, both ways:** at undocking the loop opens 1.51 ms before the gate is low, so the enable parts first at a withdrawal under 0.66 m/s. Also the open dock: E5's flat targets with the ground target between the two enable targets (C2's "on the block"). |
| **L4-E11** | **The third battery FET's designator** and land (15.5, SELECTED; condition C3), and RT1's place on the three FETs' copper (L8P-10 for the layout). |
| **L4-E11** (with board A's generator) | **IF-1:** board A's loads on VSYS stay off until the breaker's start ends, up to 40.7 ms after the gate rises and so up to 0.593 s after the enable mates, or follow the breaker's PGD. PGD is left open here: taking it needs a conductor from board P (a J_SMB and dock contact), which comes back to this record. |
| Layer 6 (L8P-06) | The 7-way J_SMB order code at both ends, pinned in the generators as R8P-02 pinned the 4-way C144395, so no fill decides it. `lcsc_fill.py`'s rule `SMBus lead.*JST-XH 1x4` no longer matches. |
| Layer 6 | E-6 for the sense pair: 2 W each at the band's temperature, at most 50 ppm/K. C103's capacitance at its 0 to 2.55 V charge within the record's 10 % (the hold's 0.110 s least). R105's single pulse at each undocking (C_U from 16.8 V through 150 ohm, about 0.47 mJ). Codes for the new passives. |
| Tools owner | `check_contracts.py` 15c: a role for DOCK_EN_OUT and DOCK_EN_RET, equal at both ends, before the regenerated P and E are judged. `gen_pcb_e5.py`'s silk table `SHORT` gains the two nets (the block's land labels read "?" otherwise; cosmetic). |
| Board P's PCB generator (`gen_pcb_p3.py`) | **IF-2:** each breaker FET's installed RthJA at most 52.5 C/W (1 in2 of 2 oz each gives the sheet's 50). The area budget is two 1 in2 pads, 1290 of the 2084 mm2 left, 793 mm2 for the rest. U101 sits beside the sense pair with Kelvin taps (E-9). C104 and C105 sit at the sense pair. Q2's source band becomes BRK_VIN and the PACK_P band runs from the breaker FETs' sources to W_P. |
| The integrator | IF-3: a stage for the breaker in `pcb_energy_chain.yaml` between PACK_FETS and PACK_LEAD (its limit 23.93 A). |

## 7. Regeneration on the runner and the netlist check (`l8p_drafts.out` section 6)

**KiCad.** The schematic generators place every part through `kisch` without KiCad. Their layout and symbol step
(`schlayout`, KiCad's symbol libraries) and the netlist export (`kicad-cli`) need KiCad, which is only on the box. The box
was not started.

**`gen_netlist.py`** runs a scratch copy of a generator to its end with a stand-in layout:
- it records `kisch`'s part table and writes it in KiCad's netlist form;
- `intent.write` runs, so the generator's own checks of rails, sources, loads, nodes and bypass entries are taken.

**Its fidelity.** On the unpatched generators it reproduces the committed KiCad netlists of boards P, E and A:
- every connected pin is on the same net;
- every footprint is the same;
- the only differences are KiCad's own names for open pins.

**Results of `check_l8p_netlist.py`:**

| Netlist | Reading |
|---|---|
| The committed netlists | NOT DRAWN on all three |
| P, E and A each with this record's draft alone (the generators ran to their end) | DRAWN on BRK and EN; the LOOP across the three boards DRAWN |
| Board P composed in L4-E9's order | DRAWN |
| Boards E and A composed in L4-E9's order | the generators refuse on other drafts' defects (section 8); with scratch stand-ins for those, DRAWN, LOOP DRAWN |
| Two mutated netlists (P's J_SMB pins 6 and 7 exchanged; A's J_DOCK pins 3 and 4 exchanged) | FAIL |

The check parses the netlists and reads the dock lands' pad positions from `meshsat.pretty`. It holds:
- the breaker's nets and values;
- the enable loop on each board;
- the ground contact between the loop conductors, on J_SMB (by position along the row) and on J_DOCK and J_BLK (a ground
  pad at the midpoint of the two loop pads);
- the loop's continuity from BRK_VIN through R106, the lead, the dock and RT1 back to Q103's gate.

**Owed on the box:**
- the regenerated schematics with ERC and the KiCad netlist export;
- the label grid matter of Q2's renamed source (board P's comment at SCP_OUT records one);
- the 7-circuit XH land read from KiCad's library.

## 8. Findings for other authors (run-time refusals no text-level composition test reads)

| Finding | Board | Owner | What stops the composed generator |
|---|---|---|---|
| L8P-F01 | E | L4-E7 (`apply_gen_sch_e_backstop.py`) | Its decoupling entries C66 (U18 pin 5), C67 (U19 pin 5) and C68 (U20 pin 6) carry no G14 class. `gen_sch_e.py` refuses: "decoupling entry C66 -> U18.5 carries no class (G14)". Board E's composition stops at step 4d. |
| L8P-F02 | A | L4-E11 (`apply_gen_sch_a_charger.py`) | VSYS_DOCK names U42 as its source without `source_ic`, which `intent.rail` refuses. With that passed, it is fed from VBAT before VBAT is declared, which is refused too. Board A's composition stops at step 3a. |
| L8P-F03 | E | L4-E11 (`apply_gen_sch_e_aux.py`) | +12V_FAN names L4 as its source, and L4 is not on that net (it sits between F12_SW1 and F12_SW2). `intent.write` refuses. |

Each refusal is the same without this record's draft. The stand-ins in `l8p_drafts.py` (STANDINS) are scratch text only,
never drafts and never applied. They say only that the generator then runs on.

## 9. Residuals of the drawing (for the record's owner; no new defect)

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
- **The inverters' own failures** are the record's remaining latent faults: R105 or Q104 open, or Q103 shorted. E-12 finds
  them: PACK_P dead undocked, and each loop conductor to ground in turn.

## 10. How to run

From the repository root:
- `python3 v2/docs/records/l8p/l8p_drafts.py` prints `l8p_drafts.out`, which is regenerated only with `_bin/regen_out.py`.
- `python3 v2/docs/records/l8p/check_l8p_netlist.py [p=...] [e=...] [a=...]` checks netlists.
- `python3 v2/docs/records/l8p/gen_netlist.py <generator copy> <out.net> [project]` regenerates a part-table netlist.

Tests: `v2/ecad/tools/tests/test_l8p.py`. No KiCad, no network. Scratch copies only; the tree is never written.
