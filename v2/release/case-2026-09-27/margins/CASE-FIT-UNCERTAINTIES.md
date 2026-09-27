# Case fit uncertainties: what is still open, which check closes it, and which board decision waits on it

MESHSAT-1357, layer 7 (mechanical and enclosure), written 27 September 2026 by the layer 7 closer and revised the same morning after the
second review of the case release; the fixer c7 added the QMX lid tray's drawing and its open fit item (section 3) that day. Prototype design: nothing in the kit has been made, bought, fitted or powered. This page is the
allocation the owner's execution prompt of 27 September 2026 asks for (sections 2 and 3, layer 7: "critical fit uncertainties resolved by
suitable evidence; later tests clearly allocated"). It adds no margin of its own: every figure is `v2/vendor/peli/1450/frame_seat.out`'s
(sha256 first 16 `214e915b985518cb`), every verdict is that file's, and `v2/docs/CASE-MARGINS.md` (`275a3083db30a7bf`) stays the
design-basis tolerance analysis. The geometry is `v2/ecad/tools/panel1450.py`, the single source the case set `v2/release/case-2026-09-27/`
is generated from; the board heights are `v2/cad/zstack.json`, read from the committed KiCad boards by `v2/cad/zstack.py`. Every choice
named below is the session's under the owner's standing rule of 26 September 2026, recorded with its reason and its reversal; none is the
owner's.

**The review behind this page is AI review.** The checks that shaped CASE-MARGINS.md's revisions (its findings 24 and 25) and this page,
the second review of the case release among them, were made by agent sessions, not by a qualified mechanical engineer; no qualified
mechanical or thermal review route exists in `v2/docs/reviews/REVIEW-ROUTES.md` (section 5 below).

## 1. The rule this page applies

- A margin is **closed at desk** when a held maker's drawing or a pick settles what it rests on; it is then MET or NOT MET on the design basis
  (a MET is a sensitivity reading, never a bound on an unstated tolerance, CASE-MARGINS.md section 1).
- A margin that rests on a tolerance no source states (Peli publishes none for the case; the build's allowances are the session's) is closed
  only on hardware: the checks T1 to T11 of CASE-MARGINS.md section 5, in a new case of the current moulding (D-08a), the targeted ones
  (T1, T2, T4, T5, T6, T10, T11) on an unpowered mock-up with stand-ins for the boards (section 7 of that file). The mock-up needs no board
  of this set, so requiring it before a board's layout entry is not a circular gate (the second review of 26 September 2026, finding 2A: a
  test that needs the final PCB cannot gate designing it; this one does not).
- **A row is marked YES when a failing reading of its physical check would be remedied by moving a board outline, a connector or a board
  part**, and its reading with the unstated allowances doubled falls below its minimum (so its plausible bound includes failure) or it rests
  on a TBD contributor. **For a YES row the physical check is required before that board's layout entry.** The owner's execution prompt of
  27 September 2026 says, in section 2, that "a later physical test may remain planned only where it is not required to establish
  feasibility or make the current stage's design decision", and in section 5, "Do not move a decisive uncertainty to a later phase merely
  to unblock a status". A YES row decides the board's outline or placement, which is the layout-entry decision, so its check is not deferred.
- A row is marked NO when its remedy is a made part (the face plate, the legs, the connector plate, the RF entry plates, their drilling)
  or a cable's route and ties. **Deferring its check to the build is justified** because the made parts are cut after the checks and a
  cable route is set at assembly: no result can change a board. Where a NO row's check is part of the mock-up anyway, it runs there.
- A desk redesign that adds margin to a YES row lowers the chance that its check moves an outline, but does not make the row independent of
  the check: the tolerance it rests on has no stated bound, and doubling it is a sensitivity test, not a bound (the second review, section
  3). So the hold on a YES row is lifted only by the check itself, or by the owner accepting the residual risk (section 7, option b).
- Buying the case, the frame and the mock-up's parts is money: the owner's decision (D-09). **Until he authorizes it, the layout entry of
  boards A, B, E and P is BLOCKED on that decision.** The compact engineering question is section 7. The desk items of every board are
  closed first either way: they make the mock-up's readings decisive and they are layout-entry prerequisites on their own. Nothing here asks
  the owner to measure or build anything.
- **This replaces the page's first allocation of the same morning**, which recommended the mock-up before the outlines freeze but carried
  the YES rows to fabrication release "if the case has not been bought by then" (CASE-MARGINS.md section 7, option c, and
  `v2/docs/reviews/READY-TO-ACT.md` 6.1: "Layout entry does not wait on it"). The only reason given for that deferral was that a layout-entry
  hold would depend on a purchase, which is not a reason the owner's prompt admits (section 2). The drafts that bring those two files in
  line are `drafts/hc7/CASE-MARGINS.md.patch` (section 7) and `drafts/hc7/READY-TO-ACT.mockup-timing.patch`.

## 2. Every OPEN margin, allocated

"x2" is the row's reading with every unstated allowance doubled (CASE-MARGINS.md section 1). A row whose x2 reading is at or above its
minimum still rests on an unstated tolerance and stays OPEN until its check runs.

| Row | Verdict (frame_seat.out) | Nominal / worst / x2 (minimum) | What it rests on | Desk evidence that closes or narrows it | Physical check | Can a failing check move a board outline, connector or part? | Stage |
|---|---|---|---|---|---|---|---|
| M1 | OPEN | +6.26 / +3.62 / +1.80 (2.0) | the Xenarc body's 28.66 and rear frame, the CM5 cooler's 21.0, the gap and bay spacers (TBD); floor, ring and bow allowances | lookups: Xenarc drawing, Raspberry Pi CM5 Cooler drawing, spacer parts | T2, T4 | **YES, board B**: the remedy is B's stack (the bay spacer's length, which moves every B part in Z) or the CM5 slots' place under the monitor (the board reading: JST VH headers +10.76, the heatsinks govern) | **B layout entry**: the lookups, then T2 and T4 on the mock-up (BLOCKED on the purchase) |
| M2 | OPEN | +4.45 / +1.84 / -0.44 (1.0) | the floor, ring and rim heights | none | T3, T9 | NO: the face plate's rebate (a made part) | build; the plate is cut after T2 and T3 |
| M2b | OPEN | +2.94 / +1.25 / +0.29 (1.0) | the lid's cavity and its place on the base | none | T3, T9 | NO: the face plate's outline | build |
| M3 | OPEN | +19.92 / +16.39 / +14.11 (1.0 plus the parts) | the C&K button and APEM lever heights under the tray (TBD) | the makers' sheets | T9 | NO: the lid tray (a made part) | build |
| M4a | OPEN | +3.71 / +1.85 / +0.85 (1.0) | the pack placed by hand | the pack's hold-down design (S-27) | T4 | **YES, boards A and P**: board A's east edge (X 120) bounds the pocket; board P's place | **A and P layout entry**: the hold-down design, then T4 on the mock-up (BLOCKED on the purchase) |
| M5 | OPEN | +3.65 / +1.77 / +0.27 (1.0) | the pack placed by hand; the legs' locator | the hold-down design | T4, T2 | **YES, board P**: its place in Y | **P layout entry**: the hold-down, then T4 and T2 on the mock-up (BLOCKED on the purchase) |
| M8x | OPEN | +2.41 / +1.10 / +0.52 (1.0) | the case's width in the rim zone, the frame's centring | none | T2, T3 | NO: the plate's outline | mock-up if bought, else build (the plate is cut after T2 and T3) |
| M8y | OPEN | +2.36 / +1.05 / +0.47 (1.0) | as M8x | none | T2, T3 | NO: as M8x | as M8x |
| M8z | OPEN | +2.48 / +0.10 / -2.18 (0) | the shoulder's and the ring's heights | none | T2 | NO: the legs' pad height (a made part) | as M8x |
| M10 | OPEN | +3.65 / +1.73 / -0.09 (1.0) | the floor, skirt and marking allowances | none | T2, T6 | NO: the entry plates' screw rows | as M8x |
| M11c | OPEN | +3.60 / +3.00 / +2.40 (3.0) | holes and plate marked by hand | a drilling jig makes it a stated tolerance | T6 | NO: the plate's drilling | as M8x |
| M11d | OPEN | +2.34 / +0.43 / -0.83 (0) | the wall's thickness, the gasket | a gasket with compression limiters makes it stated | T5 | NO: the screw length | as M8x |
| M11e | OPEN | +0.51 / +0.11 / -0.19 (0) | the hole marked by hand | a drilling jig | T6 | NO: the drilling | as M8x |
| M11g | OPEN | +3.66 / +1.95 / +0.69 (1.4) | the wall's thickness, the gasket | as M11d | T5 | NO: the screw length | as M8x |
| M13 | OPEN | +2.12 / +1.20 / +0.38 (0) | the installed height of the arrestor's O-ring (drawn 0.63, not dimensioned) | PolyPhaser's dimension (lookup) | T11 | the row itself: NO (the spot-face depth). But the O-ring sets where the inner jack ends, which M18, M17w and M17x carry: **YES, board B**, through those rows | **B layout entry**: the lookup, then T11 on the mock-up (BLOCKED on the purchase) |
| M13c | OPEN | +1.50 / +0.48 / -0.12 (0) | holes and plate marked by hand | a drilling jig | T6 | NO: the drilling | as M8x |
| M14a | OPEN | +4.50 / +2.58 / +0.76 (1.0) | the case's heights at the back wall; marking | none | T1, T6 | NO: the connector plate's height (the inside mates, M14c to M14h, are MET) | as M8x |
| M14b | OPEN | +2.40 / +1.34 / +0.28 (1.0) | the case's height; marking | none | T6 | NO: the connector plate | as M8x |
| M14i | OPEN | +1.93 / +1.15 / +0.47 (1.0) | the fairings' extent down the back wall (in no view); marking | none | T1, T6 | NO: the connector plate's width | as M8x |
| M14m | OPEN | +3.65 / +3.05 / +2.45 (3.0) | holes and plate marked by hand | a drilling jig | T6 | NO: the drilling | as M8x |
| M15b | OPEN | +1.49 / +0.11 / -1.27 (0) | the dock strip placed by hand | SESSION RECOMMENDATION: set the strip's VHB pads 2.0 inboard of its south edge (Y -111): 3.49 nominal, 2.11 worst, 0.73 with the unstated allowances doubled, MET on the design basis | T4, T8 | YES for board E until the pads move (their places are E's underside keep-outs); NO once they sit 2.0 inboard, where x2 reads +0.73 against 0 and the remaining remedy is a pad, not a part | **E layout entry**: the pad places (desk); T4 and T8 then confirm at the mock-up or the build |
| M17a | OPEN | +4.44 / +2.96 / +1.90 (2.0) | the floor under the pack, the plate's marking | none | T6, T8, T10 | NO: the remedy is the hold-down's profile over the block or the bundle's route through the slot, not a board | mock-up (it runs there with T10), else build |
| M17b | OPEN | +2.22 / +1.00 / +0.20 (1.0) | the ties, the marking | none | T10 | NO: the ties | as M17a |
| M17c | OPEN | +8.68 / +1.56 / -2.34 (0) | the wall, gasket, O-ring, marking, locator | M13's lookup | T5, T10, T11 | NO: the S-bend's route and the legs' inner face | as M17a |
| M17d | OPEN | +5.42 / +3.44 / +1.94 (2.0) | the stack's placement, the locator | none | T10 | **YES, board B**: its east edge at X 165 against the legs' columns (the lane) | **B layout entry**: T10 on the mock-up (BLOCKED on the purchase) |
| M17e | OPEN | +2.85 / +1.47 / +0.47 (1.0) | the locator, the ties | none | T10 | NO: the ties, the leg's outer face | as M17a |
| M17f | OPEN | +2.25 / +0.75 / -0.75 (0) | the strip's placement, the ties | E's clamp lanes (desk) | T10 | **YES, board E**: its south edge and front clamp lanes | **E layout entry**: the lanes (desk), then T10 on the mock-up (BLOCKED on the purchase) |
| M17g | OPEN, FAILS AS ASSUMED | -1.21 / -2.43 / -3.23 (0) | FAILS AS ASSUMED: the jumper plug's reach, ferrule diameter and cable-axis offset (no held sheet) | the plug's drawing (a pick): reach 13.58 or less, or 5G MAIN turned 26.5 degrees | T10 | **YES, board B**: the east plug layout and B's east-end parts | **B layout entry**: the plug pick (desk, REQUIRED), then T10 with the picked plug on the mock-up (BLOCKED on the purchase) |
| M17x | OPEN, FAILS AS ASSUMED | +3.89 / -0.38 / -4.35 (1.0) | FAILS AS ASSUMED: the plug's cable-axis offset and ferrule | the plug's drawing: axis 1.38 or more from the inner end with a ferrule 2.58 or less | T10 | **YES, board B**: its east edge at X 165 and its east-end tall parts | as M17g |
| M17w | OPEN | +6.38 / +2.11 / -1.86 (1.0) | the wall, gasket, O-ring, the stack's placement | M13's lookup | T5, T10, T11 | **YES, board B**: its west edge (X -165) through the stack's placement | **B layout entry**: T5, T10 and T11 on the mock-up (BLOCKED on the purchase) |
| M18 | OPEN | +7.63 / +3.36 / -0.61 (1.0) | the wall, gasket and O-ring in the plug's reach; the stack's placement | M13's lookup; the plug pick | T4, T5, T11 | **YES, board B**: its east-end tall parts (RockBLOCK 7.63, the E72 module U14 7.76 in the board reading) | **B layout entry**: the lookup and the pick, then T4, T5 and T11 on the mock-up (BLOCKED on the purchase) |
| M20 | OPEN | 86.00 / 84.38..87.62 (stated) | the floor and ring allowances (the seat) | none | T2 | NO: board C's Z hangs from the plate, and the face gate's tightest pair (the monitor body over the CM5 heatsinks) keeps 6.3 mm against its 2.0 rule, more than the seat's range of 1.62 either way; the remedy is the legs' pad | mock-up if bought, else build |
| M21b | OPEN | +2.09 / +0.83 / -0.05 (0) | the locator, the centring | none | T2 | NO: the leg's foot | as M20 |
| M21c | OPEN | +2.50 / +1.24 / +0.36 (1.0) | the locator, the centring | none | T2 | NO: the leg's relief | as M20 |
| M21d | OPEN | +2.48 / +1.14 / +0.26 (1.0) | the locator, the skirt's face | none | T2 | NO: the leg's column | as M20 |
| M21e | OPEN | +0.57 / +0.27 / -0.03 (0) | the locator | none | T2 | NO: the leg's pad | as M20 |

**Summary per board: what its layout entry needs, and whether the purchase holds it:**

| Board | Desk items that must close before its layout entry | Physical checks required before its layout entry (its YES rows) | Held by the purchase (D-09)? | Outline or placement at risk if a check fails |
|---|---|---|---|---|
| A | the pack hold-down (S-27, M4a); J_AB2 under board D (W4-F17, section 4 item 3); the dock and blind-mate stack (row DOCK, section 3) | T4 (M4a), with T1 at purchase | **YES, BLOCKED** | the east edge X 120 |
| B | the jumper plug pick (M17g, M17x: FAILS AS ASSUMED as laid out); PolyPhaser's O-ring height (M13); the Xenarc, CM5 cooler and spacer lookups (M1) | T2 and T4 (M1, M18), T5 and T11 (M18, M17w, M17x through M13), T10 (M17d, M17g, M17w, M17x), with T1 at purchase | **YES, BLOCKED** | the east edge X 165 and the east-end tall parts (RockBLOCK, E72 U14, J_ETH, T1, LimeSDR); the west edge through the stack's place; the stack height and the CM5 slots under the monitor |
| C | none (its outline passes the window, M21h MET; its Z hangs from the plate); the D22 lamp's plate hole follows its next layout (section 3) | none: M20 and the M21 rows are NO | no | none (its Z only) |
| D | J_AB2 under board D (W4-F17, section 4 item 3): board A's header moved out of D's rectangle, or D's standoff re-derived against the mated socket | none (T4 at first assembly confirms the standoff) | no | D's standoff height; A's J_AB2 place |
| E | the clamp bar R4E-07 with an ANT3 clamp at X +46 and the front clamp lanes (M17f); the VHB pads 2.0 inboard (M15b); the dock stack (row DOCK) | T10 (M17f), with T1 at purchase | **YES, BLOCKED** | the south edge and the clamp lanes |
| P | the pack hold-down (S-27: M4a, M5, its Z) | T4 (M4a, M5) and T2 (the legs' locator in M5), with T1 at purchase | **YES, BLOCKED** | its place in the pocket and its Z |
| E5 | the dock and blind-mate stack (row DOCK, section 3), with the standoff under the block named | none: the stack rests on the makers' stated tolerances (Radiall, Preci-Dip, Mill-Max, 3M), so its desk analysis is a bound; T4 at first assembly confirms | no | the block's height and the contacts' compression |

The acceptance item "later physical checks clearly allocated, with deferral justified where the current decision does not depend on them"
(the layer 7 audit) reads on this table as follows: every NO row is deferred with its reason stated; every YES row is allocated to its
board's layout entry, not deferred. The item "critical fit uncertainties resolved by suitable evidence" is **not met**: the YES rows stay
OPEN until the mock-up runs, and that waits on the owner's purchase decision.

## 3. Carried TBDs and design items that are not margin rows yet

| Item | Evidence route | Check | Board decision that waits on it |
|---|---|---|---|
| DOCK: the dock and blind-mate tolerance stack (SMP-MAX axial +-1.0 and radial float against the rods' 0.3, the Preci-Dip 813 window +0.4/-1.0, the Mill-Max 0858 power pins, VHB 1.1 +-10 percent, the gap spacer, the laminates) | desk, from the held Radiall, Preci-Dip and Mill-Max sheets (`v2/docs/respin-research-mech-2026-09-04.md` 2.4 and 2.5); CASE-MARGINS.md section 6 end says no row judges it. The board reading adds one input: board E5's face is stated as 7.4 over the strip on 6 mm standoffs (`gen_pcb_e5.py` docstring), which a 6.0 standoff and a 1.6 board make 7.6: the stack must name the standoff | T4 at first assembly; TEST-PLAN at the build | A, E, E5: connector X and Y, block height, shims, the gap spacer (REQ-047) |
| The pack hold-down (S-27, CON-006) | desk design. What it must meet: the block 56.65 x 133.5 x 38.1 with its west face at X 122.0 and the group (block, board P, 2.0) centred in Y between the east legs (M4a +1.85, M5 +1.77 at the worst today, on hand placement); no hole in the case floor (REQ-020); the heater mat under the block (50 wide, X 122.3 to 172.3; its thickness 0.6 to 1.4 is TBD); the block's top under board B's underside parts (M6; B's J_AB2 ribbon header stands 9.1 below B at X 121.6 to 131.5, Y -80.7 to -59.3, over board P's planned place, lowest Z 39.90 in the board reading); retention through TEST-PLAN E1 (26 drops from 1.22 m) and E2 with a load estimate; a VHB bond to the case's polypropylene needs primer (T8) | T4, T8, E1, E2 | A's east edge, P's place and Z |
| The rod stack's retention (W4-F7: the rods stand on the dock strip's VHB pads only; the north rods have no foot; proposal RF-1 not ruled) | desk design with an E1/E2 load estimate | T8, E1, E2 | the mounting holes of A, B and E |
| The fans (W4-F9 against `open-picks.txt` ip68-fans) and the floor plan (fans, water electrodes, sensor modules, harness and jumper lanes, shore lead lane), clear of the legs' zones (|X| 156.0 to 180.17, |Y| 106.4 to 112.4) | desk | T10 (lanes) | E's placement; the jumper routes |
| The arrestors' ground leads to stud F, and the end-wall drop guard or TEST-PLAN E1 exclusion (the arrestors stand 43.9 off the end walls) | desk | E1 | none |
| The sealed RJ45 re-pick (a 38999 shell 15 envelope rated 54 V; the Bulgin PX0833 fails both), the PXP4043/C panel drawing, the M8 receptacle sheet, the pod and the stud | lookups and picks; each connector plate cut-out stays PROVISIONAL until then (the drawing marks them red) | T6, T7 | none (the connector plate only) |
| The thermal interfaces: the enclosure conductance (the desk bounds differ 2.3 times and include failure), the PA flange on the plate (now 13.0 above the CM5 fans with the face at 106.52), its flange sensor (PWR-F15) | the empty-case heat-balance test of `v2/docs/feasibility/POWER-THERMAL.md` section 10; recommended before the hot-part placement of A, B, D and P freezes, which FEA-004's stage table (fabrication release) contradicts: the registry writer reconciles it | heat-balance test (owner's money) | hot-part placement of A, B, D, P; possibly layer 4 |
| The QMX lid tray's fit to the unit (C5; the part of 9 September 2026, `v2/cad/lid_bracket_qmx.py`, drawn with its place on sheet 14 of `v2/release/case-2026-09-27/`). The held QMX operating manual (`v2/vendor/qrp-labs/qmx-operating-manual-1_04_004.pdf`, pages 7 to 9) puts the Paddle, Audio and DC jacks on the unit's left panel and RF (BNC), PTT and USB-C on its right panel; the tray has its two cable notches (12 wide, 9.0 deep from the open face) in one end wall only, so the lid harness's DC lead cannot leave it together with the USB-C and BNC leads, and the notches' heights against the jacks are not checked (the manual's panel drawings carry no dimensions). The unit's 95 x 63 x 25 is the generator's figure, which the held manual does not state | desk: the unit's enclosure drawing (the QMX assembly manual, online, not held), then the tray revised with an opening at each end at the jacks' heights, and M3 re-read if the tray's depth changes | T9 (the lid closed over the face with the tray and the unit) | none: the tray is a made part and the harness ends (B16 `J_QMX`, A22 `J_HF` and `J_RF2`) do not move; it is revised before it is printed |
| The light guide over D22 (the seventeenth LED guide), the hardware EMCON lamp board C's round 8 draws beside `SW_EMCON` (`v2/docs/ASSEMBLY.md` at main `84e52461`, the light-guide row) | desk: the lamp's place is set at board C's next layout; then `panel1450.py` gains the 2.6 H7 hole and a new case release is cut. This release's plate carries the sixteen LED light-guide holes over D1 to D16 and the light sensor's, and no D22 hole | T9 (the lid over the face) | none: the plate follows board C |

## 4. What the board reading changed (v2/cad/zstack.py, 27 September 2026)

1. **The face gates' list of board B's tall parts had drifted from the committed board (B21).** The hand list of 9 September (panel1450.B16_TALL,
   kept as `LEGACY_B16_TALL` in zstack.py) held J_ETH at 14.0 where the RJ45's library model stands 15.5; nine 2.54 mm pin headers of 8.54 and
   six XAL6060 inductors of 6.10 sat under 6.0 envelopes; the E22 and E72 modules, the LG290P, slot 1's two M.2 cards, three fan headers,
   J_RB9704 and BT1 lay under no envelope; and the JST VH power headers, 16.5 mated by JST's catalogue, sat under 10.0 envelopes or none.
   `panel1450.B16_TALL` is now the reading (59 envelopes: 8 modules, 6 M.2 cards over the committed sockets, 45 parts). What moved inside
   board C's gate: 55 deep-part-over-tall-part pairs are judged where 19 were, the tightest (the monitor body over the CM5 heatsinks) keeps
   6.3 mm where it kept 2.2 against the rule's 2.0, and B16's tall parts keep 16.32 mm under the backer strips (J_ETH) where they kept 12.8
   (the rule is 3.0). M1 does not move: the CM5 coolers govern it (+6.26 nominal). The nearest board part under the monitor is a JST VH
   header at +10.76.
2. **The reading is required, never replaced (the second review of the case release).** The first loader of the reading fell back to the
   8 module envelopes, with one line on stderr, when `v2/cad/zstack.json` was absent, and board C's gate would still have printed PASS under
   the same code bundle; a chain tree staged by `routeflow/cloud/stage_chain.sh` carries no `v2/cad/`. Now `panel1450.B16_TALL`,
   `B16_FROM_BOARD` and `clearance_report()` raise `panel1450.ZstackMissing` without a board reading (importing panel1450 still works, so the
   generators and the CAD are unaffected); `test_case_geometry.py` proves it on an absent, a truncated and a modules-only file. The drafts
   make the gate record the reading by sha (`drafts/hc7/check_pcb_c.py.patch`), declare it in `rules_status.CONFIG_INPUTS`
   (`drafts/hc7/rules_status.CONFIG_INPUTS.patch`, which also declares the gate's other run-time reads: board C's table and, taken whole,
   intent_checks.py's inputs) and stage it into chain trees (`drafts/hc7/stage_chain.sh.patch`). Board C's gate with the first patch, run on
   the committed C24 file (sha256 first 16 `2a273803757c68fb`) in a scratch copy on the CAD box on 27 September 2026 about 06:55 CEST: PASS
   of 48 with `zstack.json` recorded in its inputs (`b4fb79d90d2f3ee1`, which `rules_status._recorded_sha` binds); the same run with the
   file removed: INCONCLUSIVE, `ZstackMissing`, exit 3 (`v2/docs/records/hc7/`, filed from the closer's `drafts/hc7/records/`; a scratch reading, not recorded evidence: the consolidated
   re-take records it). The intent screens that gate reports moved with board C's round 8 intent file at `84e52461` (24 bypass entries where
   19 were); they are decided by intent_checks' own verdicts and not counted in MEC-001's 48.
3. **W4-F17 is confirmed from the board file:** board A's J_AB2 (IDC 2x5, 9.1 by the library model) stands 3.10 into board D's underside at
   the 6.0 standoffs, before the mated socket, whose height above the shroud is TBD. A board A or D decision (move the header or re-derive
   D's standoff), desk, before A's and D's layout entry.
4. **frame_seat.py's own board inputs:** it types U51's height as 1.6, an INFERRED class figure, and a six-part hand list of the east-end
   parts. The 1.6 is right as a worst-case input: U51 is an STM32H753VITx in LQFP-100, and ST's DS12117 Rev 9, Table 217 (page 322 of
   `v2/vendor/st/st-stm32h753xi-datasheet.pdf`) gives its body height A as 1.50 typical and **1.60 maximum**; the library model's 1.50 is the
   typical. `v2/cad/zstack.py` now carries the maker's maximum onto the board part (`MAKER_MAX`: `height_max` 1.60 with its source, matched by
   footprint and part value), and the draft `frame_seat.py` reads that maximum for M14e and M14g, both worst-case chains, so neither row
   moves. The first draft of this page read the model's 1.50 there and called the 1.6 a drift; the second review found that it weakened a
   worst-case input, and the detector `case_geometry_check.worst_case_reads` now refuses a worst-case chain on a nominal body. The hand list
   misses the E72 module U14, whose edge at X 164.9 keeps 7.76 to the east plugs (M18 is still governed by the RockBLOCK at 7.63); the draft
   reads the list from the board. With the draft, `frame_seat.out` changes only in M18's printed part list; no figure and no verdict moves.
5. **Nineteen of the 94 model files the boards name are not in KiCad's library at 9.0.9:** ten take the same body's model (SUBSTITUTE), nine a
   declared class or the maker's figure (the JST VH headers, the HRO USB-C at 3.26, the small SMD packages at 2.0 or less, the E22, E72 and
   LG290P at a 5.0 class whose maker drawings are still to read). `v2/cad/zstack-models.json` lists each. Every other height in the reading
   is a library model's nominal body. Of the board parts, only U51 enters a worst-case chain by its height (M14e, M14g), and it carries the
   maker's maximum; M18 takes the tall parts' X edges, and the face gates judge nominal geometry against their 2.0 and 3.0 rules.

## 5. Review status

- AI review only: the agent checks behind CASE-MARGINS.md's revisions 1 to 7 and this page, and the second review of the case release that
  revised it, are AI review. No qualified mechanical or thermal reviewer has checked the case analysis, the legs, the plates or the stack;
  `v2/docs/reviews/REVIEW-ROUTES.md` has no mechanical route. The session's recommendation is a mechanical route (an engineer with enclosure
  and tolerance-stack experience) before the case parts are ordered, as an item for the review-routes owner; its cost is not known.
- The drawings are checked against their sources by `v2/cad/case_geometry_check.py` (board identity, the face gates' coverage, the face basis
  against frame_seat.out, frame_seat.py against its record, the makers' maxima on board parts, the worst-case reads, the release manifest),
  a software check of consistency, not of fit. Every sheet of the release was rendered to an image and read back by the session before the
  release was written (AI review of legibility and of the numbers against panel1450.py and frame_seat.out); no engineer has checked them.

## 6. Where the allocation is carried

- **The registry** (`drafts/hc7/apply_registry.py`, for the registry writer): FEA-007, the case fit, a feasibility blocker whose bounds
  include failure, staged:
  - LAYOUT_ENTRY holds boards A, B, D, E, E5 and P and needs DESK and BENCH_MOCKUP: the desk items of section 2 for all six, and the
    mock-up's checks for the YES rows of A, B, E and P. It waits on S-27 (the pack's hold-down) and on a new LATER open item, the purchase
    of the mock-up, which D-09 does not approve (the pattern of L-04 and L-05: "not approved by D-09; it needs the owner's spending
    approval before board A enters layout").
  - FABRICATION_RELEASE holds boards A, B, C, E, P and the case: every board's committed layout re-read against the mock-up's readings
    (frame_seat.py re-run with them, no row below its minimum), and the made parts drawn to them before they are cut for the prototype.
  - PROTOTYPE_VERIFICATION holds the case and the kit: T3, T7, T8 and T9 at the build, and REQ-047's lift-out on the assembled prototype.
  CON-006's acceptance loses its clause "or, if it has not run by then, at the affected boards' fabrication release" for the same reason
  (M4a and M5 are YES rows). FEA-007 is the geometry item the computed layout-entry test lacked (the layer 7 audit, stage_gate_cycles);
  until the registry writer applies it, this page is the allocation and `v2/docs/CURRENT-EVIDENCE.md`'s layout-entry table does not show it.
- **The session's application** of the owner's execution prompt of 27 September 2026 (sections 2 and 5), recorded under his standing rule
  of 26 September 2026 (the session never asks him; it takes the recommended option and records it as its own):
  - Taken: every YES row's physical check before its board's layout entry; the NO rows at the build, each with its reason; the layout
    entry of A, B, E and P shown as BLOCKED on the purchase, with the compact question of section 7.
  - Why: a YES row decides the board's outline or placement, which is the layout-entry decision itself, and its plausible bound includes
    failure; the only reason the first allocation gave for deferring it (that a layout-entry hold would depend on a purchase) is not one the
    owner's prompt admits.
  - Reversal: (1) the mock-up runs and its readings meet the YES rows' minimums, and the hold lifts on evidence; (2) the owner accepts, as
    his residual risk, entering layout on the design basis (section 7, option b), recorded as `residual_risk_accepted` by OWNER on FEA-007,
    and the BENCH_MOCKUP need moves to FABRICATION_RELEASE with the layout-change risk named per board. The session cannot take (2): it
    accepts a residual risk no measurement in this tree can remove, which the owner's ruling of 21 September 2026 keeps his.

## 7. BLOCKED: the case mock-up before boards A, B, E and P enter layout (the compact engineering question)

- **Exact issue.** Eleven OPEN case margins can move a board outline, a connector or a board part if their physical check fails (the YES
  rows of section 2: M1, M4a, M5, M13, M15b until its pads move 2.0 inboard, M17d, M17f, M17g, M17w, M17x and M18). Each rests on a
  tolerance no source states (Peli publishes no case tolerance; the build's placements are by hand) or on a TBD part. With those allowances
  doubled, M1, M4a, M5, M15b (as laid out), M17d, M17f, M17w and M18 read below their minimums; M17g and M17x fail with the jumper plug as
  laid out; M13 rests on an O-ring height its maker draws but does not dimension. Only a new case of the current moulding, measured with the
  made parts and stand-ins, settles them.
- **Affected decisions and boards.** Board A's east edge (X 120); board B's east edge (X 165), its east-end tall parts, its west edge through
  the stack's place, its stack height and the CM5 slots under the monitor; board E's south edge and front clamp lanes; board P's place and
  Z in the pocket. REQ-019, CON-006, REQ-047, FEA-007; D-07's third 5G jack through the east plug layout. Boards C, D and E5 are not held
  by it.
- **Evidence.** `v2/vendor/peli/1450/frame_seat.out` (`214e915b985518cb`) and CASE-MARGINS.md section 3.2 (35 of 70 rows OPEN, two
  FAILS AS ASSUMED); the rows and remedies of section 2 above; the drawings and 1:1 templates of `v2/release/case-2026-09-27/`, which the
  made parts can be machined from.
- **Attempts and results.** Seven revisions of CASE-MARGINS.md on 26 September 2026 held every row against the worst of Peli's own figures
  (the 1451-931 drawing, the STEP bodies, the frame sheet) with each unstated allowance doubled as a sensitivity test; the owner withdrew
  the request that he measure his own case (D-08 reversed); this release draws every made part of C1 to C6: the face plate, the legs with
  their locator and wedges, the connector plate, the RF entry plates and (since the fixer c7's rebuild of 27 September 2026) the QMX lid
  tray with its place on the lid (sheet 14; its fit to the unit is an open item of section 3). The pack's hold-down (section 3) and board E's
  clamp bar (R4E-07, section 2's summary) are not designed yet. None of this bounds an unstated tolerance.
- **Viable options.** (a) Authorize the purchase now and run T1, T2, T4, T5, T6, T10 and T11 before boards A, B, E and P enter layout.
  (b) Accept, as the owner's residual risk, entering layout on the design basis and carrying the YES rows to fabrication release, where a
  failing check becomes a layout change on the board it moves. (c) Hold boards A, B, E and P out of layout until (a) or (b) is decided,
  while their desk items close and boards C, D and E5 proceed on their own paths.
- **Recommended next action.** (a), on the same case as the empty-case heat-balance test (`v2/docs/reviews/READY-TO-ACT.md` S-1: the
  heat test first while the case is undrilled, then the mock-up), after the desk items that make the readings decisive: the jumper plug
  pick, PolyPhaser's O-ring height, the Xenarc and CM5 Cooler lookups, the pack's hold-down and board E's clamp lanes. Until the owner
  decides, (c) holds without any action from him.
- **Required expertise and equipment.** A mechanical assembler with a height gauge, calipers and feeler gauges; hole saws of 27, 29, 22 and
  18 mm and a drill; an SMA crimp tool for RG-316; a CNC shop for the legs and plates (a printer for the locator and wedges).
- **Cost and lead time where known.** The case and frame EUR 168.90 and EUR 29.66 excl. VAT, in stock (READY-TO-ACT.md 5.2, VERIFIED;
  shared with the heat test and kept as the prototype's case). One PolyPhaser GTH-SFF-AL for T11, USD 78.99 excl. duties (READY-TO-ACT.md
  6.3, VERIFIED; the twelve at USD 947.88 are the prototype's own, bought early). For M1's T4 the Xenarc 709GNK, USD 569.00 (VERIFIED,
  the prototype's own monitor), and a CM5 heatsink, GBP 4.80 incl. VAT (VERIFIED). The machining of the four legs, the face plate, the
  connector plate and the two entry plates is TBD by quote (JLCCNC lists aluminium 6061 from 3 business days); the picked jumper plugs and
  RG-316, and the stand-in blocks, are TBD.
