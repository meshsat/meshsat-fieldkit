acceptable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026). The second end-to-end check. Its blocking items B1 and B2 (two thermocouple placements) and minor items r1 to r14 are answered by patch_od01g.py; see LOG-od01b.md. -->

# AI review: end-to-end check of the OD-01 package, fnd/od01b at 28f7a990 (MESHSAT-1357)

This is an AI review, not a qualified engineering review. The checker wrote none of the work under review. It ran on 29
September 2026 from 04:23 to about 04:40 CEST (read from `date`) in the read-only scratch clone at `28f7a990a9f8`.
It is an end-to-end read, not a diff review. The documents read as the operator follows them: TEST-PROCEDURE sections 1
to 9, TEST-BRIEF, CHECKOUT-LIST (every line, the totals and section 6), MACHINING-RFQ sections 1, 3 and 6, and the od01
README. The shutdown was traced as a circuit, and H1's positions were read from its DXF. No box, agent or other model was used. Nothing was committed.

The shutdown now holds as a circuit, and check 6's B1 to B3 are answered. Two defects remain that an operator would
meet, both in thermocouple placement: one is a wrong position, the other is a step in the wrong order. Neither makes a
heating state unsafe.

## Blocking

**B1. V3 (b) puts CH4 on a face screw, not on the rebated band it names.** TEST-PROCEDURE lines 188 to 189 read "move CH4
... to H1's rebated band at X 0, Y -121 (over the o-ring nearest TS3)". Sheet H1-1's DXF has one of the ten 4.6 screw
holes at X 0.0, Y -121.16, with a 6-32 pan head up to 6.86 across on top of it. The rebated band is the zone outside the
REBATE_2MM_TOP line at |Y| 126.5 (the band runs from |Y| 126.5 to 131.5). The o-ring lies in the channel outside the
frame's 252.88 top flange (`CASE-MARGINS.md`, about 6.9 wide in Y). So Y -121 is on the full-thickness face over the
frame's insert, and the text contradicts the drawing. The operator finds a screw head where the text names the band.
The same wrong figure is in check 6's q6 ("Y -117 to -125"), and the patch copied it. Safety is not affected: CH3 at 20
mm from the spot reads above the band either way.
Fix, lines 188 to 189: "move CH4 for this check to H1's rebated band at X 0, Y -129 (the band's middle, over the o-ring,
beside the face screw at X 0, Y -121.16)".

**B2. The patch runs move three inside thermocouples after H1 is screwed back on.** Section 6 step 2 (lines 320 to 323)
fits the HS100, then says "Tape CH7 on the HS100's body now". It repeats V3 (a), refits H1 with its ten screws, and
repeats V3 (b). Only then does step 3 (line 324) "move five: CH3, CH5, CH6, CH7 and CH8" onto H1's top face. But CH5 is
on the floor under H2, CH6 is on H2 and CH8 is on the pack block (steady map, lines 261 to 264). With H1 screwed down,
their junctions cannot be reached, and their wires are clamped under the band. There is no spare wire either (INFERRED):
ten thermocouples minus eight in use leaves two spares plus CH3's wire, for four positions. The step cannot be done as
written without lifting H1 a second time. This is the same kind of defect as check 6's q10, but the patch fixed only CH7.
Fix, step 2: "Tape CH7 on the HS100's body now, and free CH5, CH6 and CH8 from the floor, H2 and the pack block, laying
their wires out on the thermocouple run so their junctions are outside once H1 is on; route these wires and the HS100's
leads out with the others." Step 3: "(CH5, CH6, CH7 and CH8 were freed in step 2; tape CH3, CH5, CH6 and CH8 on H1's top
face now)".

## Check 6's items

| Item | Answered | Where, and what is left |
|---|---|---|
| B1 lid-gasket crossing | yes | Wiring 2, item 7 and the brief each give the chain one wire in and one wire out, each on its own run, 50 mm from the other and from the heater leads. "Not shown (2)" states that the crossings are untested and that it would take two pinches to bypass the chain. The V4 heading is corrected. |
| B2 heaters on while H1 is lifted | yes | Line 315 turns the heaters "off for good". Line 334 feeds the patch from the test A supply moved to the HS100, or from a second supply. The clause is gone from the brief. |
| B3 hot plate | yes | Brief line 64: "a hot-air gun (V1 to V3; a hot plate may serve V1 only)". README line 38: "a hot-air gun". |
| q1, q2, q3, q5, q7, q12, q14, q16 | yes | Lines 223 to 226, 197, 199 to 200, 174, 215 to 217, 297, brief lines 36 to 38 and line 267. |
| q4 | yes | Lines 176 to 177 and 192 to 193 wait 5 K under the V1 closing temperature. The next START shows that the thermostat has reclosed. |
| q6 | partly | The gun setting, the rim shield and the 65 C stop are in. CH4's position is wrong (B1 here), and the lowest setting may not heat the plate enough (r9). |
| q8 | yes | The buttons are now PB1 and PB2. The diodes D1 and D2 now share names with the differences D1 to D9 (r10). |
| q9 | yes | Items 4, 7, 8 and 9 give the order, and item 4 now holds TS2, TS3 and TS1's M3 hole. V1 is still not placed in section 4 (r11). |
| q10 | partly | Step 2 gives the count of five, CH7 before the refit, the gloves or cooling, and TS3's slack. CH5, CH6 and CH8 are still moved after the refit (B2 here). |
| q11 | yes | Line 377 says how to resume after a trip, and lines 388 to 389 add the stop columns. After a trip, V4 (a) has no heaters on (r4). |
| q13 | yes | CHECKOUT line 15 now lists the receptacles, 150 C tape, a DIN rail and a meter rated for 6 A. |
| q15 | yes | check-1 lines 5 and 85 are generalised. The same path survives as a literal in `patch_od01f.py` (r14). |

## Circuit trace

Heater path: supply + -> F1 -> K1 11-14 -> K2 11-14 -> ammeter -> link block -> heaters -> common -> supply -. Coil path:
supply + -> F2 -> PB2 (normally closed) -> [PB1 (normally open) in parallel with K1 21-24 + K2 21-24] -> TS1 -> TS2 ->
TS3 -> TS4 -> the two coils in parallel, with D1 and D2 reverse-biased -> supply -. The meter used in V2 and V3 is on
the link block's input.

| Step | State | Observation | What it proves | Vacuous |
|---|---|---|---|---|
| V1 | each thermostat alone on a block | opens inside its band, recloses | each disc's opening temperature before mounting | no |
| V2 (a) | bench, 12 V, link block open | START released: 12. STOP/TEST: two clicks, 0, still 0 on release. START: 12 | the latch, reset only by START; PB2 in the coil path | no |
| V2 (b) | bench, gun on each thermostat in turn | 0 when it opens; still 0 after it cools 5 K under its closing temperature; START gives 12 | each thermostat opens the chain; the latch holds after the thermostat recloses | no |
| V2 (c) | bench, one relay's A1 lead off | the other relay pulls in, meter 0, drops on release; then mirrored | each 11-14 is in series in the heater path and each 21-24 in the hold path | no, given (a) |
| V3 (a) | in the case, H1 lifted, link block open | lead off: 0; lead refitted: still 0 until START | each installed thermostat's leads are in the chain | no for the leads; a bridged pair of tabs is not seen (r2) |
| V3 (b) | H1 screwed on, lid open, link block open | START 12, STOP/TEST 0, START 12; gun on TS3's place: 0 before 65 C; cooled: 0 until START | TS3 opens in place; no short at H1's seal between the chain's two wires | no; the heater-lead case is stated wrongly (r1); CH4 is misplaced (B1) |
| V4 (a) | heaters on | two clicks, current 0, still 0 on release | STOP/TEST stops the heating and latches | no |
| V4 (b) | supply off, F2 out | the four contacts and START read open | no contact welded, START not stuck | no: with F2 out, each reading's parallel path ends at an open contact of the other relay |
| V4 (c) | supply off, then link block and lid set, START | leads on their runs, current returns | nothing about the chain after a lid change; the text claims nothing | not claimed |

"What the verification shows" is true as written, apart from r1 and r2 below. The residual-risk paragraph is true of the
circuit.

Lead exit: on sheet H1-1, the straight runs between the R16 corners are 345.2 mm on the long sides (Y +-131.5) and
231.0 mm on the short sides (X +-188.6). The four groups (heater bundle, thermocouple bundle, chain in, chain out) need
three gaps of 50 mm and fit on one short side, and trivially on four sides, so the separation is achievable. Check-2's
under-1 % estimate stays valid (INFERRED). The copper crossing the seal is 4 x 0.75 + 2 x 0.25 = 3.5 mm2, against
check-2's 6 x 0.75 = 4.5 mm2, and every opening lies in one of the two seal planes, so no height difference drives an
exchange between them.

V3 (b) against section 8: the 65 C stop on CH3 or CH4 is below the 70 C limit for the edge over the o-ring, and far below
Peli's 88 C, and the shield keeps the jet off the rim. This holds with CH4 placed as fixed in B1.

## Minor

- **r1.** Lines 207 to 209: with the link block open, a heater + lead sits at supply minus through its 6.8 ohm heater. A
  short from that lead to the return wire would load the chain with about 1.8 A through F2's 1 A fuse, and TS3's trip
  would still drop the relays. The meter would not "stay at 12" (INFERRED from the circuit). Write "... between the
  chain's two wires would keep the meter at 12; a heater lead touching the return wire shows as F2 blowing or the meter
  falling to 0 unprompted: either is a fail".
- **r2.** Lines 120 and 122: aluminium tape laid across the base of TS2's or TS4's tabs would bridge the tabs and bypass
  the thermostat, and V3 (a) would not see it. Write "the aluminium tape over the cap flange or the bracket only, at least
  3 mm clear of both tabs".
- **r3.** Lines 150 to 151: "0.25 mm2 or more for the coil chain" names no insulation, but the chain runs at TS4 (up to
  144 C). Write "0.25 mm2 or more silicone wire".
- **r4.** Line 377: after a trip the heaters are already off, so V4 (a) has nothing to stop. Add to V4 (a): "after a trip:
  after a START with the link block set for the next step".
- **r5.** Line 315 starts with "After S6 is steady", but line 380 expects that S6 may trip. Write "After S6 is steady, or
  stopped at a limit and cooled as in section 8".
- **r6.** Section 6 repeats V3 (a) and V3 (b), but the heaters are off for good and step 4 moves the supply to the HS100,
  so the shutdown switches nothing in the patch runs. Say why the repeat is kept, or drop it. If it is kept, V3 (b) must
  run before step 4, while the chain is still fed at 12 V.
- **r7.** Line 273, "feeler 0.05 at the edge, no gap": every lead lifts H1 where it crosses the flange and the o-ring.
  Write "no gap except over the leads". Also keep the leads at least 10 mm from the ten screws.
- **r8.** V3 (a) at TS2: TS2's tabs sit under the middle of H2, 100 mm in from H2's edge with 45 mm of clearance. Write
  "lift H2 on its stand-offs to reach TS2" (INFERRED).
- **r9.** Line 191: on a variable gun, the lowest setting (often about 50 C) may never bring 766 g of H1 to 60 C.
  Also, CH3 at 20 mm from the spot may sit inside a jet held 20 cm off (INFERRED). Write "the lowest setting that
  raises CH3 by 1 to 2 K per minute".
- **r10.** Diodes D1 and D2 (line 127) now share names with the differences D1 to D9 (lines 53 to 61). Rename the diodes
  VD1 and VD2.
- **r11.** Lines 163 to 164 say that "section 4 says when each part runs", but V1 is not in section 4. Add to item 4:
  "V1 and V2 have been done on the bench before this item".
- **r12.** No list includes M4 screws or nuts to fix H2 to its four stand-offs; line 15 lists M3 only.
- **r13.** Line 57 (D5) still names only "the heater leads". Every lead group now crosses both seals. The bias figure
  stands.
- **r14.** `patch_od01f.py` line 199 keeps check-1's old user path as a search literal. The file is in the folder that the
  README lists, though not in PACKAGE.sha256. `checks/check-5.md` line 96 quotes the box path `/root/od01b`. Build the
  literal from parts, and add a filing note to check-5.

## Verified

- HEAD is `28f7a990`, and the only untracked files are check files. `sha256sum -c v2/docs/records/od01/PACKAGE.sha256`
  from the root gives 74 of 74 OK. H1's `MANIFEST.sha256` gives 6 of 6 OK, and the case release manifest 50 of 50 OK.
  `run.py test_h1_heat_test_plate`: 6 passed, 0 failed. `test_case_geometry`: 11 passed, 0 failed. The brief built with
  pandoc and xelatex (A4, 10 pt, 2 cm margins) is 2 pages.
- Finder XI-2018: the 9.012 coil is 220 ohm and 55 mA, operates from 0.73 UN, holds at 0.4 UN and drops out at 0.1 UN;
  the 40.52 breaks DC1 8 A at 30 V.
- Honeywell: Table 1 bands give 57 to 63, 84 to 96 and 136 to 144. Table 2 gives 0 to 150 C operating and -18 to 177 C
  exposure. Table 4 is AC only.
- Arcol: HS50 is 3.0 K/W, F 39.7, G 21.4, L 3.2; HS100 is F 35.0, G 37.0, L 4.4, 47.5 x 88.0. The derating figures (85.7,
  80.0, 41 and 121 C) check.
- PEM CL: an M3 S nut with code 2 needs 1.4 mm of sheet and a 4.22 +0.08 hole.
- H1's DXF: PEM holes on 37.0 x 35.0 about (-45, 70); TS3's bracket reaches Y -114.6, 2.3 mm inside -116.92.
- Totals: lines 10 to 14 come to 68.40 excl. and 82.76 incl.; lines 1 to 8 to 416.40, 511.80 and 503.85; lines 1 to 14
  to 484.80; shipping to 30.26. The unit prices excl. VAT equal the page prices divided by 1.21.
- The cutting gates agree across procedure section 2 item 1, RFQ section 1, RFQ section 6's last column and brief section 1.
- The T2 ranges 84.38 to 87.62 and 104.77 to 108.27 follow from 86.00 and 106.52 with the stated tolerances.
- No package file has a host name, user path or address, apart from r14. No package file has an em or en dash; dash
  literals appear only in the detectors of the patch scripts, which are outside the package.
