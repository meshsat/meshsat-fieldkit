# OD-01: the operator's complete procedure (heat balance, then the case mock-up)

MESHSAT-1357, stream od01b, 29 September 2026, prepared by an AI session after the owner's instruction of 29 September
(R4, R5) and an outside AI review of the package. `TEST-BRIEF.md` is the two-page summary; this page is what the operator
follows, step by step, and it is self-contained: every figure it uses is here or in a file listed in `PACKAGE.md`.
**Prototype:** nothing is built; these tests use an empty case, made plates, dummy blocks and printed stand-ins, no board.
Nothing here has been bought, made or run. Where a figure is the session's estimate it says INFERRED.

Sources this page takes its procedure from (in the package): `v2/docs/feasibility/POWER-THERMAL.md` section 10 (the
heat-balance experiment), `v2/docs/CASE-MARGINS.md` sections 5 and 7 (checks T1 to T11 and when each runs), the H1
definition `v2/release/case-2026-09-27/h1-heat-test-plate/`, the independent checks `checks/check-1.md` and
`checks/check-2.md` (the lead exit and the H2 size rest on check-2), and the makers' sheets named in each step.

## Contents

1. What the heat test can prove, and what it cannot (R5)
2. Receipt: the case and frame first, then the parts
3. The automatic over-temperature shutdown and its verification (R5)
4. Test A set-up: plates, heaters, thermostats, thermocouples, leads
5. Test A steady-state steps
6. Test A patch runs (attended)
7. Test B, the mock-up: T1, T2, T4, T5, T6, T11
8. Stop limits and what to do when one is reached
9. What is recorded

## 1. What the heat test can prove, and what it cannot

**What it measures.** The empty case, sealed by H1 on the 1450PF frame and its o-ring, lid open and lid closed, with 21,
42 and 64 W released into the base volume from a black dummy plate (H2) at the stack's place, fans off. At steady state each step gives one number (a step
stopped at a limit before steady state gives none, section 8): the enclosure's conductance for heat released into the inside air,
`G = P / (T_air,in - T_room)` in W/K, with `T_air,in` read at the named point CH2 (section 4, item 6). The patch runs give the
rise of H1 under a 45 to 83 W block (an Arcol HS100 on its 35.0 x 37.0 fixing) for 20, 30 and 60 s, and its cooling.

**Applicability to Option A(i)'s proposed lid pack (29 September 2026).** Option A(i) (a 400 Wp array into a 200 W stage,
`v2/docs/records/a1solar/`, `a1elec/`, `a1mech/` and `a1int/` on branch `fnd/a1int`, not yet on main) proposes a second
pack of 56 or 60 cells in the lid over the face, a harness across the hinge and a stay; it waits on the owner's decisions
(which lid function leaves, REQ-016, D-06, the deployment rule: `v2/docs/EXECUTION-PLAN.md`, the standing rule of 29
September). Nothing below adopts it. What each OD-01 test still gives if it is adopted:

| Test | Applies unchanged? | Why, and what the lid pack would add |
|---|---|---|
| Receipt checks R1 to R8 | yes | the case, the frame and the walls are the same |
| H1, C6 and the gates of RFQ section 6 | yes | the heat-test plate and the legs do not meet the lid |
| C1 (face plate) for the mock-up | yes for T2 and T4 | as drawn it has no sealed crossing for the lid's lead (not designed, S-95): it is a mock-up plate, not the kit's final face under Option A(i) |
| Shutdown V1 to V4, stop limits, records | yes | the test rig, not the kit |
| Test A, lid-open steps S1, S4, S5 | yes | the open lid stands away from the base volume the test measures (INFERRED; the lid pack's own heat when charging is not in the test) |
| Test A, lid-closed steps S2, S3, S6 | no, as a measure of Option A(i) | with the lid pack the closed lid's space over the face is mostly cells; the conductance with the lid closed would need a lid-pack thermal dummy in the lid (a new step) |
| Patch runs | yes | the plate's spreading under the PA flange site does not depend on the lid |
| Test B: T1, T2, T5, T11 | yes | case, frame, legs, walls, arrestor |
| Test B: T4 and T6 | partly | T4 has no lid-pack stand-in; T6's open-lid clearance to the mated plugs would change with a lid pack |
| New for the lid pack (not in OD-01) | none yet | `records/a1mech/README.md` names T-A1-1 (the lid's depth to the ceiling), T-A1-2 (the U-174/U jack), T-A1-3 (the stop, the hinge axis, the open case on a slope) and T-A1-4 (200 lid cycles with a dummy module and the harness), plus the sealed lid-lead crossing (S-95) |

**Its uncertainty (the session's budget, INFERRED until the operator's own instruments' stated accuracies replace the
typical figures used here):**

| Term | At 64 W (rise about 30 K) | At 21 W (rise about 10 K) | Basis |
|---|---|---|---|
| Power, volts x amps on two meters | about 1.1 % | about 1.1 % | typical handheld DC accuracy, 0.5 % on volts and 1 % on amps |
| The rise, after the 15-minute common soak removes each channel's offset | about 0.3 K = 1.0 % | about 0.3 K = 3 % | same logger, same cold junction; type K slope differences between channels of one batch |
| Not yet steady at the criterion of section 5.3 | at most 0.33 K = 1.1 % low | at most 0.33 K = 3.3 % low | 0.2 K per 30 min on a 50 min time constant leaves at most 0.33 K to come |
| Heat conducted out along the leads and past the seal at the lead exit | under 1 %, reads G high | under 1 %, reads G high | check-2 (about 0.006 W/K against 2.1 W/K) |
| **Combined** | **-1.5 % to +3.6 %** | **-3.2 % to +7.5 %** | the two random terms by root sum of squares; the two biases, both reading `G` high, added in their sign |

Two things this budget does NOT cover, and the record reports them separately instead of folding them in: the spread of
the inside air between points (fans off, the air stratifies; CH2, CH3 and CH8 are all reported and `G` is quoted against
CH2 only), and the room's air movement (a draught raises `G`; the room is still and its condition recorded).

**Every difference between the surrogate and the finished enclosure:**

| # | Surrogate | Finished kit | What it does to the reading |
|---|---|---|---|
| D1 | H1 is a closed 3 mm aluminium skin | C1 has the monitor window 205.75 x 140.09 (about 29 % of the plate) filled by the Xenarc 709GNK, the e-paper window with its 1 mm lens, 17 light-guide holes and the controls | Aluminium spreads heat over the whole face; the monitor's glass and body do not, and the monitor adds its own heat in that window. INFERRED: `G` through the face reads optimistic for the finished kit's internal heat. Magnitude not known; only a later test with C1 and the monitor gives it. |
| D2 | All heat comes from three HS50 on H2 at the stack's place, about 50 mm above the floor | Heat comes from boards A, B, D, E and P, the pack in its pocket, the PA on the plate's underside and the monitor in the plate | Heat put directly into the plate (the PA, the monitor) bypasses the inside air, so `G` measured for air-coupled heat is not the kit's for plate-coupled heat. The measured `G` applies to the fraction of the kit's heat that enters the air. |
| D3 | Local temperatures: H2, the heater bodies, the pack block | Each part's own temperature: CM5, converters, cells, radios | Not measured and not inferable from this test: each part adds its own resistance to the air, which the empty case does not have. |
| D4 | Fans off | Five fans (three coolers, two mixers; picks open) | Fans-on `G` stays open (no fans are picked or bought). Fans off is the record's conservative case (2.1 W/K still, `POWER-THERMAL.md` section 10). |
| D5 | Every lead (the heater leads, the thermostat chain's two wires, the thermocouples) passes flat under H1's edge over the frame's o-ring and, lid closed, under the lid gasket | The kit's leads pass sealed connectors in the back wall | Under 1 % high on `G` (check-2). The seal is locally opened by the leads: the test says nothing about sealing. |
| D6 | Empty case: 2.5 kg (the seller's figure), time constant about 50 min (INFERRED) | Loaded kit: several kilograms more | Steady-state `G` does not depend on mass; every transient of this test (warm-up, the patch's cooling of the plate) is the empty case's, not the kit's. |
| D7 | Indoors, still air, no sun, the case on a bench | Outdoors: sun on the black face, wind, ground or snow under the case | The hot end in the field adds solar load and changes the outside film; not tested here. |
| D8 | The HS100's aluminium foot, about 47.5 x 88 mm, on compound | The RA30H1317M1's copper flange, 67.0 x 19.4 mm (`panel1450.PA_MOUNT`), on its own interface | A larger footprint spreads the same heat over more plate: INFERRED, the patch rise here is LOWER than the PA's would be at the same power. It becomes a PA figure only through a spreading model the session runs at desk. |
| D9 | Peli's purge valve in place, as the design keeps it | The same | none |

**Which gates it may and may not close.**

| May close, or feed, as a measured input (the session re-derives at desk; the test itself decides nothing else) | May NOT close |
|---|---|
| FEA-004's clause "the enclosure conductance measured", for heat released into the inside air, fans off, lid open and closed, in still indoor air | FEA-004 as a whole (its loads, PWR-F12 and PWR-F15 clauses stay) |
| W4 T9 and the 2.3 x spread of the conductance bound on the fans-off still-air case: replaced by the measured `G` with its uncertainty | Final thermal acceptance of the kit (TEST-PLAN E3 on the built kit), any part's temperature, the fans-on conductance, the lid-closed reduced mode with real loads |
| The +35 C and +25 C restrictions: re-derived at desk from the measured `G`; they remain proposed controls, verified at E3 | Any sealing or ingress claim (IP67, the o-ring, the leads' exit): only T3, T7 and TEST-PLAN E6 and E7 with water decide those |
| Appendix 32.56's patch figure (+15 K per 20 s at 45 W) as a plate-spreading input to PWR-F15's thresholds, PROVISIONAL and scaled for D8 at desk | PWR-F15 (the flange sensor and its limits are read on the real PA at bring-up) and PWR-F16 |
| The desk re-run that decides the placement freeze of the pack and the PA flange (boards A and P) | The placement freeze itself, which also needs the pack hold-down (S-27) and the loads |

**Its readings never close final thermal or sealing acceptance.** They are one empty case, one plate blank and one
arrangement of heat.

## 2. Receipt: the case and frame first, then the parts

1. **The case and the frame:** run the receipt checks R1 to R8 of `MACHINING-RFQ.md` section 6 (identity, the rim
   zone, the depths, the floor, the frame, the insert pattern). **Each fit-dependent part is released for cutting only when every receipt check that its row in
   `MACHINING-RFQ.md` section 1 names (the checks are the table of its section 6, whose last column names the same parts)
   has passed: H1 and C1 after R1, R2, R3, R5 and R6; C6 after R1, R3, R4 and R5; the entry plates C4 and the connector
   plate C3 after R1, R3, R7 and R8 (C3 is not released before the build); the gaskets G1 to G3 after R1 and R8, and
   never before the plate each seals.** A case that fails R1 goes back to the seller (60-day return) rather than being adapted.
2. **The HS100 patch resistor (step A0):** read its four mounting holes' centre distances with a caliper (hole edge to hole
   edge plus one hole diameter): F 35.0 +-0.3 along its length, G 37.0 +-0.3 across (Arcol 12/14.08 page 2), holes
   4.4 +-0.25 (L). Offer it to H1 with four M3 x 10 A2 pan heads and flat washers: all four start by hand into the PEM
   nuts. Record the readings.
3. **The three HS50 heaters:** fixing holes 3.2 +-0.25 (L) on F 39.7 by G 21.4 (Arcol page 2), two holes at diagonal
   corners. Read their resistance cold: 6.8 ohm +-1 %.
4. **The thermostats (section 3):** read the part number on each body against the list (two 60 C NC, one 90 C NC, one
   140 C NC); continuity closed at room temperature.
5. **H1:** the shop's dimensional report against sheet H1-1, the finish black anodised, the four PEM nuts flush on the
   underside, flatness 0.5 or better on a flat table with feeler gauges (the plate face down, the gauge under each corner
   and mid-side). Record.

## 3. The automatic over-temperature shutdown, and its verification

**Rule.** The steady-state steps run for hours and may run unattended **only** with the shutdown below in place and
verified (V1 to V3 before the case is first heated, V4 at the start of every step). Without it, every hour of heating
needs continuous competent supervision: a person present at the case who reads the logger at least every 10 minutes and
switches off at any stop limit of section 8. The patch runs of section 6 are always attended. **The bench supply's current
limit does not enforce any temperature limit and is not part of the shutdown.**

**The arrangement: a latching relay held in by a chain of normally closed thermostats.**
- The heater current (up to 5.3 A at 12.0 V) passes a normally open contact of each of two relays, K1 and K2, in series. The two coils, in parallel, are fed
  through a chain of four normally closed bimetal thermostats TS1 to TS4, a normally closed STOP/TEST button, and, in
  parallel with a normally open START button, the second contacts of K1 and K2 in series (the self-hold).
- Pressing START energises K1 and K2; they hold themselves in. If any thermostat opens (or STOP/TEST is pressed, or a wire breaks, or the
  supply is lost: the relays drop out below 0.1 of their rated voltage), the coils drop, the heaters go off and **stay off after the thermostat has cooled and closed again**,
  until someone presses START. The heaters therefore never cycle unattended.
- The thermostats carry only the two coils' current (0.65 W each at 12 V, about 110 mA together: 55 mA each on Finder's 12 V DC coil row), never the heater current: their maker states AC
  ratings only (Honeywell, 2455R contact ratings, Table 4: 10 A resistive at 240 V AC; "additional contact ratings are
  available"), so none is used to switch the heaters' DC directly.

**Parts (`CHECKOUT-LIST.md` lines 10 to 14 priced from the seller's pages; line 15, the small items, unpriced):**

| Ref | Part | Maker's figures (held sheet) | Placed |
|---|---|---|---|
| TS1 | Elmwood (Honeywell) 2455R, 90 C, normally closed, automatic reset, with bracket; reichelt "2455R 90 NC" | opens at 90 C, +-6 C on reichelt's page (the sheet's Table 1 gives +-4 to +-6 C in the 83 to 110 C band, by differential): **opens by 96 C at the latest**; 0 to 150 C operating, -18 to 177 C exposure (Table 2) | bolted to H2 with an M3 screw through its bracket, within 10 mm of the middle heater (the hottest), with a thin layer of compound under its cap |
| TS2 | 2455R, 60 C, normally closed; reichelt "2455R 60 NC" | opens at 60 C +-3 C, closes at 45 C (reichelt's page; Table 1, 27 to 82 C band, differential 8 to 16 K: +-3 C open): **opens by 63 C at the latest** | taped cap-down with Kapton and aluminium tape (the aluminium tape over the cap flange or the bracket only, at least 3 mm clear of both tabs) to the case floor directly under the middle heater, beside CH5 (the polypropylene that sees H2 most) |
| TS3 | 2455R, 60 C, normally closed, as TS2 | as TS2 | taped cap-up to H1's underside with the body's centre at X 0, Y -99 (the front, away from the patch) and its bracket B203-S's tabs and its two terminals along X: the body, 16.0 mm across and 11.91 mm tall (Honeywell 2455R, Figure 3, page 5), spans Y -107 to -91, and the bracket, whose largest dimension is 31.19 mm (Honeywell, Figure 18, B203S), reaches at most 15.6 mm from the centre, to Y -114.6, 2.3 mm inside the frame window's edge at Y -116.92, so H1 still sits flat on the ring |
| TS4 | 2455R, 140 C, normally closed; reichelt "2455R 140 NC" | opens at 140 C +-4 C (reichelt's name; Table 1, 111 to 150 C band: +-4 to +-7 C by differential, so read at V1): **opens by 144 C at the latest** at the +-4 C of the name | held cap-down on the middle heater's aluminium body with Kapton and aluminium tape (the aluminium tape over the cap flange only, at least 3 mm clear of both tabs) over a thin layer of compound, beside CH7 |
| K1 | Finder 40.52.9.012.0000, 2 changeover contacts, 12 V DC coil | 8 A rated current; breaking capacity DC1 8 A at 30 V; coil 0.65 W, operates from 0.73 UN, drops out at 0.1 UN (Finder 40 series, XI-2018, pages 1 to 3) | outside the case, on its socket, beside the supply |
| X1 | Finder 95.05 socket for K1 (screw terminals, DIN rail) | 10 A, 250 V (reichelt's page) | outside the case |
| PB1, PB2 | START (PB1): any panel pushbutton, normally open; STOP/TEST (PB2): any panel pushbutton, normally closed; each rated at least 1 A at 24 V DC | not priced, not held | outside the case, within reach |
| K2, X2 | a second Finder 40.52.9.012.0000 on its own 95.05 socket, as K1 and X1; its contact 11-14 in series with K1's in the heater lead and its 21-24 in series with K1's in the hold path, its coil in parallel with K1's | as K1 and X1 | outside the case |
| VD1, VD2 | a 1N4007 (or equivalent) across each relay coil, cathode to A1 (the + side), so no thermostat breaks an inductive current | a standard rectifier | at each socket |
| F1, F2 | in-line blade fuse holders: F1 with a 7.5 A fuse in the heater lead at the supply's +, before K1; F2 with a 1 A fuse at the start of the coil chain | not priced | outside the case |

**What each trip enforces:** TS1 holds H2 at or under 96 C (its stop limit is 100 C); TS2 holds the polypropylene nearest
H2 at or under 63 C (the wall stop is 70 C, Peli's case maximum 88 C); in the steady-state steps (not the patch runs, whose
limits are the operator's, section 6) TS3 holds H1 at or under 63 C, and so its edge
over the o-ring (stop 70 C), which on a 3 mm aluminium plate heated from below differs from the underside near the
window's edge by a few kelvin at most (INFERRED); TS4 holds the middle heater's body at or under 144 C (stop 150 C, Arcol's
hot spot 200 C). Arcol's 3.0 K/W is a body's rise over the air on a standard heatsink: at 21.2 W about 64 K, so about 120 C
with the inside air at 55 C (check-1, INFERRED). The middle heater is on in every step, so TS1 and TS4 always sit at an
energised heater; the outer heaters run at the same 21.2 W on the same plate with heat on one side only, so they sit no
hotter than the middle one (INFERRED).

**The Arcol ratings depend on the heatsink, and derate with temperature (Arcol 12/14.08, pages 1 and 2):**
- HS50: 50 W on its standard heatsink (535 cm2 of 1 mm aluminium), 14 W with no heatsink, both at 25 C; "dissipation
  derates linearly to zero at 200 C". On H2 each heater has about 220 cm2 of the 3 mm plate, less area than its standard
  heatsink, so its 50 W does not apply: its limit is the 200 C hot spot, held by TS4 (opens by 144 C) and the 150 C body
  stop. At 55 C
  air the linear derating gives 41 W on the standard heatsink; 21.2 W is about half of that (INFERRED).
- HS100: 100 W on its standard heatsink (995 cm2 of 3 mm aluminium), 30 W with none, at 25 C, derating to zero at 200 C.
  H1 (992 cm2 of 3 mm) is practically that heatsink: 85.7 W at a 50 C plate, 80.0 W at 60 C (linear). **So the 83 W
  pulses start only from a plate at or under 50 C, last at most 60 s, and stop at the patch stops (110 C at CH7, 70 C at CH4), whichever comes
  first.** 45 W is inside the rating at any plate temperature under 121 C.

**Wiring (all outside the case except the four thermostats; crimped terminals, 0.75 mm2 silicone wire for the heater
leads, 0.25 mm2 or more silicone wire for the coil chain):**
1. Supply + -> F1 (7.5 A) -> K1 contact 11-14 (normally open) -> K2 contact 11-14 (normally open) -> a three-way link block outside the case -> one + lead
   per heater into the case (three leads) -> each HS50 on H2 -> one common - lead out of the case -> supply -. The link
   block chooses one, two or three heaters without opening the lid.
2. Supply + -> F2 (1 A) -> PB2 STOP/TEST (normally closed) -> [PB1 START (normally open) in parallel with K1 contact
   21-24 and K2 contact 21-24 in series (both normally open)] -> TS1 -> TS2 -> TS3 -> TS4 -> K1 coil A1 -> A2 -> supply -, with K2's coil A1 -> A2 in parallel with K1's (both drop together) and VD1, VD2 across the coils. The thermostat chain enters the case
   on one single wire (to TS1) and leaves it on another (from TS4 to the coils), each on its own straight run of the
   seals (H1's band and, lid closed, the lid gasket), at least 50 mm from the other and from every heater lead, so that no
   single pinch at a seal can join the chain's two ends or feed the coils from a heater lead (section 4 item 7).
3. The ammeter in the heater lead after K2, the voltmeter across the heater leads where they enter the case: the coils'
   110 mA is not in the heater reading. Power = volts x amps (never the label).

**Verification (before the case is heated, each result recorded in `checks.csv`; section 4 says when each part runs;
what it shows and what it does not is stated after V4):**
- **V1, each thermostat alone.** Clamp it cap-down on an aluminium block of about 50 x 50 x 10 mm with one thermocouple
  taped beside it, on a hot plate or under the hot-air gun held 20 cm off. Multimeter on its terminals (continuity). Warm
  at no more than 2 K per minute over the last 15 K. Record the block temperature when it opens and, cooling, when it
  closes. **Pass:** TS1 opens between 84 and 96 C; TS2 and TS3 between 57 and 63 C; TS4 between 136 and 144 C; each
  closes again on cooling. A part outside its band is rejected, not adjusted.
- **V2, the latch on the bench** (before any thermostat is fitted in the case). Wire the arrangement on the bench at
  12.0 V, the heaters' link block open so nothing heats, a multimeter on volts at the link block's input (the load side
  of K2, after both contacts): it reads the supply's volts only while both relays are in. A thermocouple is taped beside
  each thermostat.
  (a) START, pressed and released: K1 and K2 pull in and stay in, the meter reads 12. STOP/TEST: both relays are heard
  to drop, the meter reads 0 and stays 0 when the button is released. START again: 12.
  (b) Warm each thermostat in turn with the air gun until it opens: 0. Let it cool until its thermocouple reads 5 K under
  its V1 closing temperature (so it has reclosed): **the meter stays at 0** until START.
  (c) The series wiring. Supply off, K2's A1 lead off its socket terminal; supply on, hold START: K1 pulls in and the
  meter reads 0 (K2's contact 11-14 is in the heater path); release START: K1 drops (K2's contact 21-24 is in the hold
  path). Supply off, refit the lead, take K1's A1 lead off and repeat: K2 pulls in, the meter reads 0, K2 drops on
  release. Supply off, refit the lead.
  **Pass:** every action behaves so.
- **V3, in place.** Heat-resistant gloves near H2 and the heaters whenever they are warm.
  (a) With the thermostats fitted and wired (section 4 item 4) and the leads laid (item 7), H1 lifted and the link block
  open (nothing heats): START, the meter at the link block reads 12. Disconnect one lead at each thermostat in turn (lift H2 on its stand-offs as far as its leads allow to reach TS2): the
  meter falls to 0 and stays 0 when the lead is refitted, until START, which is pressed before the next thermostat.
  (b) With H1 screwed on and the leads out under its seal (section 4 item 8), the lid open and the link block still open:
  START, 12; STOP/TEST, 0, and it stays 0 on release; START, 12. Then move CH4 for this check to H1's rebated band at X 0, Y -129 (the band's middle, over the o-ring,
  beside the face screw at X 0, Y -121.16) and CH3 to H1's top face at X 20, Y -99 (beside TS3's place, outside the
  jet), and stand a card shield on the case's front rim between the jet and the rim. Warm H1's top face over TS3 (X 0,
  Y -99) with the air gun held 20 cm off at the lowest setting that raises CH3 by 1 to 2 K per minute, aimed so that
  CH3 is outside the jet's spot: the meter falls to 0 before CH3 or CH4 reads 65 C
  (if it does not, stop the gun: V3 has failed). Let H1 cool until CH3 reads 5 K under TS3's V1 closing temperature: the
  meter stays 0 until START. Put CH3 and CH4 back on the channel map in use.
  **Pass:** every action behaves so.
- **V4, before every step (the lid and the link block are set in (c)).**
  (a) With the heaters on (the step just ended; before step S1, or after a trip, after a START with the link block set for the
  step to come), press
  STOP/TEST: both relays are heard to drop, the heater current falls to zero and stays zero when the button is
  released.
  (b) Switch the supply off and pull F2. A continuity check reads open across each relay's contacts 11-14 and 21-24
  (four readings) and across the START button: no contact has welded and START has not stuck. Refit F2.
  (c) With the supply still off, set the link block and the lid for the next step; after a lid change, see that every
  lead still lies flat on its own straight run of the gasket (section 4 item 7). Supply on, START: the heater current
  returns. Record the time.

**What the verification shows, and what it does not.** V1 shows each thermostat's opening temperature before it is
mounted. V2 shows the latch, its reset only by START, and both relays' contacts in series in the heater path and in the
hold path. V3 shows each installed thermostat in the chain, the chain intact with H1 closed (a short at H1's seal between the chain's two wires would
bypass the thermostats and keep the meter at 12; a heater lead touching the return wire shows, with the link block
open, as F2 blowing or the meter falling to 0 unprompted: either is a fail), and TS3 opening on heat in its place. V4 shows, before each step, that STOP/TEST stops the
heating with both relays heard to drop, that no relay contact has welded and that START has not stuck. **Not shown in
place:** (1) that TS1, TS2 and TS4 still open on heat after mounting: V1 proved each before it; the M3 through TS1's
bracket and the tape on TS2 and TS4 do not load the disc (INFERRED); heating them in place would heat the case, which is
the test itself. (2) The chain's crossings under the lid gasket with the lid closed (steps S2, S3 and S6): they are not
tested. Because the chain's two wires cross each on a run of its own, at least 50 mm from each other and from every
heater lead (wiring item 2), a single pinch there cannot bypass the chain; two pinches at once could. The stop limits of
section 8 are a second line only while someone attends; unattended, a TS1, TS2 or TS4 that failed to open in place has
only the other thermostats' indirect cover.

**Residual risk with this arrangement:** one relay's contact welding closed no longer leaves the heaters on through a
trip: the other relay's contact, in series, still opens (a second relay, about EUR 9 with its socket). Likewise one
relay's self-hold contact 21-24 welding no longer makes the latch reset by itself: the other's, in series in the hold
path, opens, so the heaters stay off after a trip. START sticking closed during a step would let the heaters cycle on the
thermostats, which still hold every temperature they sit at; V4 reads START open before every step. Both 11-14 contacts
welding in the same step would leave the heaters on through any trip, with no temperature held; both 21-24 contacts
welding would let them cycle on the thermostats; V4 reads each contact on its own before every step. A step started
without V4, or with any of V1 to V3 failed, is an attended step.

## 4. Test A set-up

1. **The case on a bench** indoors, in still air away from windows, heaters, fans and air conditioning outlets, on four
   wooden blocks about 20 mm thick (so the floor is not on a cold or warm surface). Record the room.
2. **The frame:** the four C6 legs bonded under the frame's ring with 3M VHB 5952 in their pad pockets, placed by the
   printed locators in the window corners (sheet 2); cure 24 h. Lower the frame on the legs into the case, centre it with
   the two wedge pairs, fix it with Peli's four self-tapping screws (Peli's instructions, step 3: press firmly while
   starting them). The o-ring into the channel between the frame and the case wall (step 4).
3. **H2 at the stack's place:** H2 (330 x 200 x 3.0 aluminium, both faces matt black, `MACHINING-RFQ.md` line H2)
   centred on the case centre, long side along X, top face at about Z 48 (board B's top at Z 50.6), on four M4 PA66
   (nylon) stand-offs of 45 mm (fixed to H2 with four M4 x 10 A2 screws and washers) standing on the floor at X +-110, Y +-90 (its holes, 10 mm from the long edges), not bonded:
   they stand 12 mm west of the pack pocket's edge at X 122.0, and H2 overhangs them by 55 mm at each end. H2 then clears
   the legs' columns (X +-175.4 to +-180.2) by about 10 mm and the pack block's top (Z 39.9) by about 5 mm, as board B
   stands over the pack in the kit.
4. **The heaters on H2's top face:** the three HS50 at X -110, 0 and +110, Y 0, long axis along X. Mark each one's two
   holes from the part itself, drill 2.5 and tap M3 through H2, bolt with M3 x 8 A2 and flat washers, a thin even layer of
   the Amasan compound under each (wipe the excess: squeeze-out should be a thin line). Solder or crimp the leads to the
   tags (someone who solders, if the tags need it): one + lead per heater, the three - tags joined on H2 to one common
   lead; fix the four leads to H2 with a P-clip so no tug reaches a tag. V1 and V2 have been done on the bench before this item. TS1 and
   TS4 at the middle heater (section 3; TS1's bracket on an M3 hole drilled 2.5 and tapped in H2 like the heaters'), TS2 on
   the floor under it and TS3 on H1's underside, joined into the chain inside the case with the 6.3 mm receptacles of
   `CHECKOUT-LIST.md` line 15 (heat-rated at TS4).
5. **The pack block H3** in its pocket (X 122.0 to 178.65, Y +-102.75, under Z 39.9; `zstack/zstack.json`) on the floor,
   its mass that of the pack group (until S-27 gives the outline, `MACHINING-RFQ.md` note 4).
6. **The thermocouples, steady-state channel map** (soaked first, item 9; eight channels; each junction taped under Kapton with its first 50 mm
   of wire laid along the surface; photograph each):

| Ch | Where | Stop limit |
|---|---|---|
| CH1 | Room air, 1 m from the case at its mid-height, shaded from it (a folded card), not in a draught | none |
| CH2 | Inside air, base volume, 25 mm under H1's underside at X +100, Y 0, the junction free in the air inside a foil tube 30 mm long open at both ends (a radiation shield) | none |
| CH3 | H1's top face at X 0, Y 0 | none |
| CH4 | H1's edge over the o-ring: the top face of the rebated band at X +186, Y 0 | **70 C** |
| CH5 | The case floor directly under the middle heater, beside TS2 (the polypropylene that sees H2 most) | **70 C** |
| CH6 | H2's top face within 10 mm of the middle heater, beside TS1 | **100 C** |
| CH7 | The middle heater's aluminium body, on its top | **150 C** |
| CH8 | The dummy pack block, on its top face | none |

7. **The leads' exit** (the method accepted by check-2): every lead passes as a flat silicone wire between H1's rebated
   band and the frame's o-ring, and, lid closed, under the lid gasket, on a straight run of the seal, never where it
   turns a corner. The four heater leads (three + and the common) lie side by side on one run, the thermocouple wires on
   another; the thermostat chain's two single wires each on a run of its own, at least 50 mm from the other and from
   every heater lead (section 3, wiring item 2). Lay every lead at least 10 mm from the ten screw holes (sheet H1-1). Photograph it. Do not replace Peli's purge valve with a gland. Then V3
   (a), H1 still lifted.
8. **H1 on:** the ten 6-32 x 1/2 in A2 pan heads into Peli's inserts **by hand, no pressure** (Peli step 4: excess pressure
   pushes the inserts out). Check H1 seats evenly on the frame all round (feeler 0.05 at the edge, no gap except over the leads; every lead at least 10 mm from the ten screws) and that the
   lid latches without force over the leads. Then V3 (b); V4 before step S1.
9. **The logger:** eight type K channels with cold-junction compensation, 0.1 K resolution or better, CSV export. Soak:
   all thermocouples together in one place in the room (bundled, junctions touching a small aluminium block) for 15 min before they are fitted (before item 6); record each channel's reading; the offsets are subtracted from every later reading. Sampling:
   every 10 s for the steady-state steps.

## 5. Test A steady-state steps

### 5.1 The sequence

| Step | Heaters on | Volts (set) | Lid | Fans |
|---|---|---|---|---|
| S1 | one (the middle) | 12.0 | open | off |
| S2 | one | 12.0 | closed | off |
| S3 | two (the middle and the west) | 12.0 | closed | off |
| S4 | two | 12.0 | open | off |
| S5 | three | 12.0 | open | off |
| S6 | three | 12.0 | closed | off |

Each step follows the last without cooling (the next step starts from the last one's steady state). Between steps V4 (section 3)
runs in full: its STOP/TEST with the heaters on, the contacts and START read with the supply off, the link block (the
power) and the lid set for the next step while the supply is off, then START. V4 (c) checks the leads after a lid change. The supply's current limit at 6.5 A.

### 5.2 During a step
- V4 (section 3) at the start. Record `start_utc`, the volts at the entry and the amps after K2, every 30 minutes while attended and at least once in the step's last 30 minutes (a photograph of
  both meters is enough).
- If any stop limit of section 8 is reached, the step ends there (section 8).

### 5.3 The steady-state criterion
A step is steady when, over the last 30 minutes:
- CH2 (inside air) and CH3 (H1's top) each change by less than 0.2 K; and
- CH1 (room) changes by less than 0.5 K over the last 60 minutes;
- and at least 3 h have passed since the step began (the empty case's time constant is about 50 min, INFERRED).
If the room drifts more, extend the step until the criterion holds or the room settles; record either way. Write
`steady_utc` in `heat-steps.csv`.

### 5.4 The result per step (the session computes it; the operator only records)
`G = P / (T_CH2 - T_CH1)`, both the means of the last 30 minutes after the soak offsets; also reported against CH3 and
CH8. `P` = the mean of the readings in that window. Uncertainty per section 1. Only a step with `steady_utc` yields `G`;
a step stopped at a limit yields none (section 8).

## 6. Test A patch runs (attended; the operator present at the switch throughout)

1. After S6 is steady, or stopped at a limit and cooled as in section 8, **switch the heaters off for good**: STOP/TEST, supply off, link block open. Wait until CH6 and
   CH7 read under 60 C, or wear heat-resistant gloves, before hands go near TS1 and TS4. Open the lid and lift H1 off the
   frame (its ten screws) to reach its underside, turning it over on TS3's leads (leave them slack enough for that).
2. The HS100 on H1's underside with the four M3 x 10 A2 and flat washers into the PEM nuts, a thin even layer of compound
   under its foot, tightened evenly by hand with a torque driver at about 0.5 N m (INFERRED; Arcol states no torque). Its
   leads leave its +Y tag downward and toward -Y (the tag is 2.9 mm from the frame window's edge). Tape CH7 on the HS100's body now (the patch map
   below), and free CH5, CH6 and CH8 from the floor, H2 and the pack block, laying their wires out on the thermocouple
   run so that their junctions are outside once H1 is on; route these wires and the HS100's leads out with the others.
   Refit H1 on the frame with its ten screws, the leads out under the seal as before. The shutdown switches nothing in
   the patch runs (the heaters stay off and the supply feeds the HS100 alone), so V3 is not repeated: the patch runs are
   attended, and section 8's limits for the patch runs (110 C at CH7, 70 C at CH4) are the operator's.
3. **Patch channel map** (CH5, CH6, CH7 and CH8 were freed in step 2; tape CH3, CH5, CH6 and CH8 on H1's top face now; move CH4 to the band nearest the resistor; keep CH1 and CH2):

| Ch | Where | Stop limit |
|---|---|---|
| CH3 | H1's top face directly over the resistor's centre, X -45.0, Y 70.0 | none |
| CH4 | H1's edge over the o-ring nearest the resistor: the top face of the rebated band at X -45.0, Y +129.0 | **70 C** |
| CH5 | H1's top face at X +5.0, Y 70.0 (50 mm along +X) | none |
| CH6 | H1's top face at X +55.0, Y 70.0 (100 mm along +X) | none |
| CH7 | the HS100's body, on its top | **110 C** |
| CH8 | H1's top face at X 0, Y 0 | none |

4. Sampling every 1 s. The patch on the test A supply, moved to the HS100's leads (or a second supply of the same
   class), current limit 6.5 A, output off; the heaters' link block stays open.
5. The pulses, each from a plate (CH3) at or under +50 C, recording the plate's start temperature:
   45 W (9.95 V, 4.5 A) for 20, 30 and 60 s; then 83 W (13.5 V, 6.1 A) for 20, 30 and 60 s. Time each pulse with a
   stopwatch, switching the supply's output on and off by hand. **Switch off at once if CH7 reaches 110 C or CH4 reaches 70 C**, and record the
   time; with 83 W from a warm plate this may come before 60 s (on the record's figure, taken linear, 110 C is reached in
   about 43 s from +50 C, INFERRED).
6. After each pulse, wait until CH3 is within 1 K of its value before the pulse, or 15 min, whichever is longer, logging
   the cooling.
7. If the plate is under 40 C at the start of the series, the series still runs; the plate's start temperature is
   recorded and the rise is the measurand.

## 7. Test B, the mock-up (after test A; in the same case)

The checks run now are T1, T2, T4, T5, T6 and T11 (`CASE-MARGINS.md` section 5; T3, T7, T8, T9 at the build; T10 needs
the jumper plug, not picked). Each check either confirms the OPEN rows it names or sends them back with a measured number;
a failed check stops the build. Tools: the ones of `TEST-BRIEF.md` section 3.

| Check | Do | Read with | Pass |
|---|---|---|---|
| T1 (at receipt, R1 of the RFQ) | Record the date wheel and the moulded markings; photograph the inside of both long walls (which one carries the X 0 rib: five ribs on one long wall, four on the other) and the outside of the back wall | camera, eyes | matches the current moulding (drawing 1451-931 of 15 January 2025, D-08a); otherwise a new case |
| T2 | With the legs bonded to the frame and the frame on them, centred and screwed, and later H1 or C1 on it: the frame's bottom at each leg, and the face top at four corners, from the floor | height gauge or depth rod on the floor, 0.02 mm; a steel rule against the fillet's tangent line | frame bottom Z 84.38 to 87.62 at every leg (or at most 85.34 on the rib tops with the feet clear of the floor by at most 0.96); face top 104.77 to 108.27 at every point; every foot on the flat floor |
| T4 | Stack-up with stand-ins: the monitor stand-in's body to the 21.0 mm heatsink stand-in with a feeler; B's top copper from the floor; the pack block and the dock strip stand-in against the floor fillet, the legs and the east wall | feeler gauges, height gauge, caliper | at least 2.0 mm at the monitor (M1, read as the largest body depth the monitor may have); M4a, M5, M15b and M18 at or above their minimums (`margins/CASE-FIT-UNCERTAINTIES.md`) |
| T5 | Drill the end walls and the back wall from the 1:1 templates (`templates/case-templates-1to1.pdf`, clamped, the case empty); read the wall thickness at each hole | caliper across the hole's bore | 4.58 to 6.10 mm at every hole |
| T6 | Offer the connector plate's footprint (X -57.0 to +57.0, Z 18.3 to 86.6) to the back wall's outside and each entry plate's (Y -110.1 to +110.1, Z 34.55 to 83.45) to its end wall's, from the check prints; Peli's four frame screws against the outside features; the open lid against the mated plugs | the check prints of `templates/case-templates-1to1.pdf`, eyes | every plate and gasket on plain skin all round; each screw into an external rib; the lid opens without touching a plug |
| T11 | One arrestor tightened on the bench with its O-ring, lock washer and nut on the east entry plate, or on a 6.0 coupon spot-faced as drawn: the thread's end against the nut's outer face, the O-ring's installed height, the nut and washer across and thick | caliper, depth rod | the thread's end at or beyond the nut's outer face (M13); nut and washer within 24.0 across and 5.0 thick, inside the 26.0 spot-face (M13b to M13d); the O-ring compressed evenly all round |

Drilling: hole saws 29, 27, 22 and 18 mm, drills 8, 5.0 and 4.5 mm and a step drill (the 27 mm saw is the end walls'
arrestor holes, sheet 4; the 5.0 drill is the entry plates' M4 wall holes, M11e). Eye protection; the case clamped and
empty. Time: T1 15 min; drilling 2 to 3 h; T2 1 h after the legs' tape has cured; T4 2 h; T5 and T11 30 min each; T6 1 h.

## 8. Stop limits, and what to do at one

| Reading | Limit | Enforced automatically by |
|---|---|---|
| Case floor or wall (CH5, steady-state steps) | 70 C | TS2 (opens by 63 C) |
| H1's edge over the o-ring (CH4) | 70 C | TS3 on H1 (opens by 63 C) in the steady-state steps; in the patch runs the attending operator (CH4 on the band nearest the resistor) |
| H2 (CH6, steady-state steps) | 100 C | TS1 (opens by 96 C) |
| A heater body (CH7, test A) | 150 C | TS4 on the middle heater (opens by 144 C) |
| The patch resistor's body (CH7, patch runs) | 110 C | the attending operator |
| Any smell or smoke | - | the operator: supply off, lid open, nothing touched bare-handed |

TS1 to TS4 act only in the steady-state steps: in the patch runs the heaters are off and the shutdown switches nothing
(section 6), so every limit there is the operator's.

At a limit or a trip: supply off; do not press START; note the time and every channel; let the case cool with the lid
open; photograph what tripped. To resume: when every channel reads within 5 K of the room, V4 in full, then the next step
of the sequence, recorded as starting cold. A trip in S3 to S6 is recorded, not treated as a fault: the step is recorded as "stopped at the
limit" with every reading up to the trip, the time and what tripped. Those readings are kept as transient data and are **not** a
steady-state result. While the case still warms, part of the input goes into storage (`P = G (T - T_room) + C dT/dt`),
so `P / (T - T_room)` before steady state can exceed the true conductance (64 W, a 20 K rise and 24 W still stored is
2 W/K, not 3.2), and with several temperature nodes and a local trip no general bound holds in either direction. A
stopped step therefore yields no `G`; any conductance the session infers from it needs a stated transient model with
its uncertainty, is labelled so, and closes no row of section 1 until that model is itself checked. **No limit is raised to let a step
finish.** On the check-2 estimate H2 may reach about 93 C at 64 W lid closed with a 30 K inside rise, so TS1 may open in S6: that is the arrangement doing its job, and
then S6 gives no `G`: the 64 W lid-closed point stays open until the session plans a replacement step at desk.

## 9. What is recorded

One folder `od01-results/`, handed over as files (copied to the runner or the laptop clone, never typed into a chat):
- `checks.csv`: `test, check, row, point, reading, unit, instrument, photo, note` (every receipt check R1 to R8, A0,
  V1 to V4, T1 to T11 run; a reading not taken gets a line with its reason);
- `heat-steps.csv`: `step, lid, fans, heaters, volts, amps, start_utc, steady_utc, logger_file, stopped_at_limit_utc,
  tripped_by` (the last two empty for a step that reached steady state), and for the patch
  `pulse, watts, seconds, plate_start_C, peak_C, time_to_stop_s, stopped_by` (CH7 or CH4; empty
  when the pulse ran its full time);
- the logger's CSV exports and the channel maps above with a photograph per thermocouple;
- photographs named by check and row: T1's date wheel and markings, the lead exit, each thermostat's place, H2 on its
  stand-offs;
- the instruments' makes, models and stated accuracies (the uncertainty of section 1 is recomputed with them);
- the date, the room temperature at the start and the operator's initials.
