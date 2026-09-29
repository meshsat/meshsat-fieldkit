acceptable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026). The first end-to-end check (the method change of check 5). Its blocking items B1 to B3 and minor items q1 to q16 are answered by patch_od01f.py; see LOG-od01b.md. -->

# AI review: end-to-end check of the OD-01 package, fnd/od01b at d8992d4e (MESHSAT-1357)

This is an AI review, not a qualified engineering review. The checker wrote none of the work under review. It ran on 29
September 2026 from 04:02 to about 04:20 CEST (read from `date`) in the read-only scratch clone at `d8992d4ea990`.
Not a diff review: TEST-PROCEDURE sections 1 to 9, TEST-BRIEF, CHECKOUT-LIST lines 10 to 15 with totals and sources, RFQ
sections 1 and 6 and the od01 README were read as an operator would follow them, and the shutdown traced as a circuit.
No box, no agent, no other model, no commit.

The rewritten verification block holds together as a circuit: V2 (c) proves both relays in series in both paths, V3 (b)
is not vacuous, and V4 (a) presses STOP/TEST with the heaters on. Three defects remain that an operator would meet. B1
is in the shutdown's coverage. B2 and B3 are older text that no longer fits V3 as rewritten.

## Blocking

**B1. The chain's crossing under the lid gasket is never verified, and S2, S3 and S6 run unattended with the lid closed.**
TEST-PROCEDURE lines 156 to 157 say the chain "enters and leaves the case as one flat pair beside the heater leads".
Lines 249 to 251 add that the pair passes under H1's band and, "lid closed, under the lid gasket". A short between the
pair's two conductors bypasses all four thermostats (the text's own words, line 200). V3 (b) rules that out only at H1's
seal, with the lid open. Once the lid closes, nothing is run: V4 (a) and (b) come before the lid change (V4 (c), line
194, sets the lid and presses START at once). Neither could see a chain bypass anyway, because STOP/TEST sits upstream
of the chain and the contact readings never touch it. So S2, S3 and S6 run unattended behind a crossing that no test
covers. S6 is the step where section 8 expects TS1 to be needed (lines 359 to 360). V4's heading (line 189, "after each
lid change") claims a check that its own order does not make. Neither "what it does not show" (line 202) nor the
residual risk names the gap.
Fix, one of two:
- (1) Wiring 2 and section 4 item 7: "The chain enters the case on one single wire and leaves on another, each on its
  own straight run of the seal, at least 50 mm from the other and from the heater leads, so no single pinch at H1's band
  or the lid gasket can join them." Lines 199 to 200: "... the chain intact with H1 closed. The crossings under the lid
  gasket are not tested; a single pinch there cannot bypass the chain, because its two wires cross apart."
- (2) Line 99: "S2, S3 and S6 (lid closed) are attended steps."

Either way, line 189 becomes "V4, before every step (the lid is set in (c))".

**B2. The patch runs offer to keep the heaters on, then need them off.** TEST-PROCEDURE line 298 says "switch the
heaters off (STOP/TEST) unless a second supply is available for the patch; open the lid and lift H1". TEST-BRIEF lines
66 to 67 add "a second 15 V, 7 A supply if the patch runs are to keep the heaters on". Both conflict with lines 302 to
304: V3 (a) needs "the link block open (nothing heats)" and opens the chain at every thermostat, and V3 (b) comes "before
any heating".
With a second supply, the operator lifts H1 and mounts the HS100 while 64 W is still on in an open base. TS3 is lifted
away from the heat and the heater bodies are near 120 C, a state no verification covers. He then has to stop the
heaters for V3 anyway, and no step turns them back on (no link-block setting, no V4 before a restart).
Fix: line 298, "After S6 is steady, press STOP/TEST, switch the supply off and open the link block; open the lid and
lift H1 ...", with "unless a second supply is available for the patch" deleted. Line 315, "The patch on its own supply
(the test A supply moved to the HS100's leads, or a second one)". Brief lines 66 to 67: delete the second-supply clause.

**B3. The buy list lets the operator take a hot plate instead of the air gun that V2 and V3 need.** TEST-BRIEF line 63
reads "a hot plate or a hot-air gun ... (verification V1)", and od01 README lines 37 to 38 read "a hot plate or hot-air
gun". But V2 (b) warms each thermostat "with the air gun" (line 173), and V3 (b) heats H1's top in place with it (line
185), which a hot plate cannot do. An operator who borrows only a hot plate cannot complete V3, so no step may run
unattended (line 98). Fix: brief line 63, "a hot-air gun (V1 to V3; a hot plate may serve V1 only) and an aluminium
block ..."; README line 38, "a hot-air gun".

## Circuit trace per verification step

Heater path: F1, K1 11-14, K2 11-14, link block, heaters. Coil path: F2, S2 (NC), [S1 (NO) parallel to K1 21-24 plus K2
21-24 in series], TS1 to TS4, the two coils in parallel, D1 and D2 reverse-biased. The meter is at the link block's
input, after both contacts.

| Step | State | Observation | What it proves | Vacuous? |
|---|---|---|---|---|
| V1 | each thermostat alone on a block | opens in band, recloses | each disc's opening temperature before mounting | no |
| V2 (a) | bench, 12 V, link block open | START 12; STOP/TEST 0, stays 0; START 12 | the latch, reset only by START | no, if 12 is read after START is released (q5) |
| V2 (b) | bench, air gun on each thermostat | 0 on opening; 0 after cooling | each thermostat opens the chain | partly: "stays 0" looks the same as a still-open thermostat (q4) |
| V2 (c) | bench, one coil's A1 off | the other relay in, meter 0, drops on release; mirrored | each 11-14 and each 21-24 is in series | no (given V2 (a)) |
| V3 (a) | H1 lifted, link block open | lead off: 0; refitted: stays 0 until START | each installed thermostat's lead is in the chain | no (INFERRED: unless two chain wires share one tab) |
| V3 (b) | H1 screwed, lid open, link block open | TS3 heated: 0 before 70 C | TS3 opens in place; no short across the pair at H1's seal | no; the lid-closed crossing is not covered (B1) |
| V4 (a) | heaters on | STOP/TEST: current 0, stays 0 | STOP/TEST stops the heating and latches | "drops both relays" yes: it passes with one (q2) |
| V4 (b) | supply off | 4 contacts and START read open | no weld, START not stuck | no; the START reading runs through the supply (q3) |
| V4 (c) | supply off, then on, lid changed | current returns | nothing after the lid change | no check at all (B1) |

"What the verification shows" is true of V1 to V3 as written, apart from B1's omission. It overstates V4 (q2), and its
"second line" holds only while someone attends (q7). The residual risk is wrong for the heater pair (q1).

## Minor

- **q1.** Lines 211 to 212, "Both contacts of one pair welding ... would defeat the latch": for the 11-14 pair the
  heaters stay on through every trip, so no temperature limit holds. Say so: "both 11-14 welding leaves the heaters on
  through any trip; both 21-24 lets them cycle on the thermostats".
- **q2.** Line 201: V4 (a) watches only the heater current, which falls when either relay drops. Write "stops the
  heater current (both relays heard to drop)" and add "both relays click" to V4 (a).
- **q3.** V4 (b), START read in circuit: S2 and F2 tie it to supply plus, the coils or D1 and D2 to supply minus. With
  the supply off, a good button may chirp or read a finite value (INFERRED). Write "pull F2, read across START, refit F2".
- **q4.** V2 (b) line 174 and V3 (b) line 187: nothing tells the operator the thermostat has reclosed (TS2 and TS3
  reclose near 45 C). Write "cool until its thermocouple reads 5 K under its V1 closing temperature: the meter stays 0
  until START".
- **q5.** V2 (a) line 171: "START (released): K1 and K2 pull in and stay in, the meter reads 12".
- **q6.** V3 (b) meets section 8's limits only at the limit (INFERRED). At the 70 C stop beside the spot, H1's edge over
  the o-ring 18 to 26 mm away (Y -117 to -125) is near CH4's 70 C stop, and nothing reads it: CH4 is at X +186, Y 0.
  The air jet reaches the polypropylene rim about 35 mm from the spot, with no gun setting given and nothing reading the
  rim (Peli's limit is 88 C). A taped junction in the jet reads high, which gives false fails. Fix: the gun at its lowest
  setting, a card shield over the front rim, a 65 C stop. The claim about the flat pair is correct for H1's seal with
  the lid open.
- **q7.** Line 204's "second line" (the stop limits) holds only while attended; unattended, a TS1, TS2 or TS4 that
  fails in place has only the others' indirect cover.
- **q8.** "S1" and "S2" name both the buttons and the steps, and lines 190 and 193 use both meanings. Rename the buttons
  (PB1 START, PB2 STOP/TEST).
- **q9.** Section 4 never schedules V2 before the in-case wiring, V3 (a) before item 8, or V3 (b) after it. Item 9 soaks
  the thermocouples "before they are fitted" but comes after item 6 fits them. TS2, TS3 and TS1's tapped M3 hole in H2
  are not in section 4.
- **q10.** Section 6: line 305 says "move four thermocouples" but moves five (CH3 and CH8 swap); CH7 on the HS100
  must go on before H1 is refitted in step 2; V3 (b)'s thermocouple has no free logger channel; TS3's leads need slack
  to turn H1 over; V3 (a) puts hands on TS1 (H2 near 90 C) and TS4 (about 120 C) right after S6: gloves, or cool first.
- **q11.** After a trip, section 8 says to cool with the lid open, while 5.1 has no cooling between steps. Say how the
  sequence resumes (as before S1), and give `heat-steps.csv` a stop column: steady or at the limit, the time, and which
  thermostat.
- **q12.** 5.2's "every 30 minutes" cannot be kept in unattended hours. Write "while attended, and at least once in the
  step's last 30 minutes".
- **q13.** Missing from every list: 6.3 x 0.8 mm receptacles for the 2455R tabs (reichelt: "AMP connectors 6.3 x 0.8
  mm"), heat-rated at TS4; aluminium tape rated for 150 C or more; a DIN rail or panel for the 95.05 sockets. A
  handheld's 10 A range may not carry 5.3 A for two days (INFERRED).
- **q14.** The brief's "about 2 h" for the verification looks low (INFERRED 4 to 5 h: V1, V2 (b) and V3 (b) wait for
  recloses near 45 C).
- **q15.** `checks/check-1.md` (group A, public) carries this host's user path on line 5 and a scratch path on line 85.
  Write "the checker's scratch clone". No other package file has a host name, user path or address.
- **q16.** Section 4 item 7 says "the heater pair", but the heater leads are four conductors (three plus, one common).

## Verified

- **Checksums.** HEAD is `d8992d4e`, and the clone is unchanged apart from the untracked check files.
  `sha256sum -c v2/docs/records/od01/PACKAGE.sha256` from the root: 73 of 73 OK. H1's `MANIFEST.sha256`: 6 of 6 OK.
  The case release manifest: 50 of 50 OK. `run.py test_h1_heat_test_plate`: 6 passed, 0 failed;
  `test_case_geometry`: 11 passed, 0 failed.
- **Finder, 40 series XI-2018.** The 12 V DC coil (9.012) is 220 ohm, 55 mA, 0.65 W, so two coils draw 110 mA. It
  operates from 0.73 UN, holds at 0.4 UN and drops out at 0.1 UN. The 40.52 breaks DC1 8 A at 30 V.
- **Honeywell.** Table 1 gives +-3 C (27 to 82 C, 8 to 16 K differential), +-4 to +-6 C (83 to 110 C) and +-4 to
  +-7 C (111 to 150 C), so V1's bands 57 to 63, 84 to 96 and 136 to 144 hold. Table 2: operating 0 to 150 C, exposure
  -18 to 177 C. Table 4 is AC only. Figure 3: 16.0 across, 11.91 tall. Figure 18, B203S: 31.19 overall, holes 23.80
  apart, 17.55 across. A later copy of reichelt's 90 NC page shows "rotatable mounting", "Screw mounting", opening at
  90 C and closing at 75 C, +-6 C, so TS1 can be bolted.
- **TS3 and Arcol.** -99 - 15.6 = -114.6, which is 2.3 inside -116.92 (`panel1450.WINDOW` 233.83 / 2). Arcol HS50:
  F 39.7, G 21.4, L 3.2; HS100: F 35.0, G 37.0, L 4.4; 535 and 995 cm2. The derating arithmetic, the 45 W and 83 W
  settings and the 43 s check.
- **Totals.** Lines 10 to 14: 10.50 + 22.26 + 19.58 + 8.24 + 7.82 = 68.40 excl. VAT, 82.76 incl. Lines 1 to 8: 416.40.
  Lines 1 to 14: 484.80. The budget in section 1 checks.
- **Gates and dashes.** RFQ section 1, RFQ section 6's last column, procedure section 2 item 1 and brief section 1
  name the same checks. No em or en dash in any document; only detector literals in the patch scripts.
