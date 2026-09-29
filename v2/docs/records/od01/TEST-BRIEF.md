# OD-01: test brief for the operator (heat balance, then the case mock-up)

> **Revised 29 September 2026 (stream od01b)** after the owner's instruction of that day and an outside AI review: the
> complete procedure now lives in `TEST-PROCEDURE.md` beside this file, self-contained (R4); what the heat test can and
> cannot prove, with its uncertainty and every difference from the finished kit, is stated (R5); unattended heating runs
> only behind an automatic, latching over-temperature shutdown verified before the case is heated, otherwise under
> continuous supervision, and the Arcol ratings' dependence on their heatsink is stated (R5); nothing fit-dependent is cut
> before the receipt checks that gate it (the table of `MACHINING-RFQ.md` section 6) (R6); H1 has its own drawing. `PACKAGE.md` lists every file by path and sha256.

MESHSAT-1357, 28 September 2026, prepared by an AI session so the owner can assign the work (ruling D-19); revised after
the independent AI checks `checks/check-1.md` and `checks/check-2.md` (both in the package). Prototype: nothing is built;
these tests use an empty case, made plates, dummy blocks and printed stand-ins, no board. Nothing has been bought or run.

## 1. The two tests, in this order (one case: the heat test needs the sealed skin, the mock-up drills it)

**Before either:** the receipt checks R1 to R8 on the case and frame (`MACHINING-RFQ.md` section 6). H1, C6, C1, the
entry plates C4 and the gaskets G1 to G3 are released for cutting only after the checks their row names have passed;
the connector plate C3 is quoted only and waits for the build; quotes may be asked earlier.

**A. Heat balance** (`TEST-PROCEDURE.md` sections 3 to 6).
- Set-up: the case on its frame and four legs (C6), the blank plate H1 (sheet H1-1) on the frame's o-ring. Three 6.8 ohm
  Arcol HS50 heaters bolted with compound to H2 (330 x 200 x 3.0, both faces painted matt black) at the stack's place on
  nylon stand-offs; the pack block in its pocket; eight thermocouples on the channel map; four normally closed
  thermostats holding two latching relays, K1 and K2, whose contacts are in series in the heater supply.
- Runs: 21, 42 and 64 W (12.0 V on one, two, three heaters), lid open and closed, fans off, each to the steady-state
  criterion (CH2 and CH3 change under 0.2 K in 30 min, the room under 0.5 K in 60 min, and at least 3 h). Then, attended,
  the Arcol HS100 patch resistor on H1's four PEM S-M3 nuts: 45 and 83 W for 20, 30 and 60 s from a plate at or under
  +50 C, and its cooling.
- **What it can prove:** the enclosure's conductance for heat released into the inside air, fans off, lid open and
  closed, in still indoor air, to about -2 to +4 % at 64 W and -4 to +8 % at 21 W (rounded outward) (the session's budget, INFERRED), and the rise
  of H1 under a 45 to 83 W block. **What it cannot:** any part's temperature, the fans-on case, the face with the monitor
  and its openings, sun and wind, the kit's transients, or anything about sealing; its readings close neither final
  thermal nor sealing acceptance. It may close FEA-004's conductance clause and W4 T9's spread, and feed the desk
  re-derivation of the +35 and +25 C controls, 32.56's patch figure and the placement freeze of the pack and the PA
  flange (the full table and the nine differences D1 to D9: `TEST-PROCEDURE.md` section 1).
- Time: about 2 days of logging for the six steps, half a day attended for the patch runs, plus the shutdown's
  verification (about 2 h).

**B. Mock-up (after A; `TEST-PROCEDURE.md` section 7).**
- Set-up: drill the case from the 1:1 templates; plate C1 with a printed monitor stand-in; stand-ins for boards A, B and E
  on their spacers, a 21.0 mm printed stand-in for the CM5 cooler until it is picked; one arrestor.
- Checks now: T1, T2, T4, T5, T6, T11. At the build: T3, T7, T8, T9. T10 cannot run until the jumper plug is picked.
- Decides the OPEN margins resting on Peli's unstated tolerances (`margins/CASE-FIT-UNCERTAINTIES.md` section 2): T2 and
  T4 for boards B (M1, M18) and E (M15b), and for A and P (M4a, M5) once S-27 gives the pack block's outline; T5 and T11
  for board B (M13, M17c, M17w, M17x, M18); T1 the moulding (D-08a).
- Time: T1 15 min at receipt; drilling 2 to 3 h; T2 1 h after the legs' tape has cured; T4 2 h; T5, T11 30 min each;
  T6 1 h: about 1.5 working days plus the cure.

## 2. Competence

Mechanical fitting from a drawing: caliper, height gauge and feeler gauges; drilling a polypropylene wall from a paper
template; drilling and tapping M3 in aluminium; a torque driver; bonding with tape. Low-voltage bench work: setting a
supply's voltage and current limit, reading volts and amps, crimping terminals and wiring two relay sockets, two diodes and two
pushbuttons from a wiring list, taping thermocouples on, starting a logger and exporting its file. No soldering (have a
heater's leads fitted by someone who solders if its tags need it).

## 3. Equipment

- **Likely owned:** caliper (0.01 mm, 300 mm); feeler gauges (0.05 to 1.0 mm); a height gauge or depth rod on a flat plate;
  a bench supply of 15 V and 7 A with a current limit; two multimeters; torque driver (6-32, M3 and M4); chalk; a drill
  with hole saws of 29, 27, 22 and 18 mm, drills of 8, 5.0, 4.5 and 2.5 mm, an M3 tap and a step drill; deburring tool;
  phone camera; Kapton and aluminium tape; a stopwatch.
- **To buy or borrow:** a 500 mm caliper with inside jaws (receipt checks R2, R5, R6); a hot plate or a hot-air gun and
  an aluminium block of about 50 x 50 x 10 mm (verification V1); optionally an ultrasonic thickness gauge (R7); an
  8-channel type K logger with cold-junction compensation, 0.1 K resolution and a CSV export (`CHECKOUT-LIST.md` section
  6); ten type K thermocouples with plugs to suit it; a second 15 V, 7 A supply if the patch runs are to keep the heaters
  on; the heaters, compound, the four thermostats, the two relays with their sockets and diodes (`CHECKOUT-LIST.md` lines 5 to 7 and 10 to
  15); four M4 x 45 mm nylon (PA66) stand-offs; 3M VHB 5952; ten 6-32 x 1/2 in pan-head screws; M3 A2 screws and washers;
  silicone wire of 0.75 mm2 or more with crimp terminals; the printed stand-ins and the made plates (`MACHINING-RFQ.md`).

## 4. What is recorded, and how it reaches the session

One folder `od01-results/`, handed over as files (copied to the runner or the laptop clone, never typed into a chat):
`checks.csv`, `heat-steps.csv`, the logger's exports, the channel maps with a photograph per thermocouple, the
photographs by check and row, the instruments' stated accuracies, the date, the room temperature and the operator's
initials (`TEST-PROCEDURE.md` section 9).

## 5. Safety

12 to 13.5 V at up to 6.1 A: no shock hazard, but heat and fire. Peli gives the case body a maximum of 88 C (its 1450EU
page): no heater or hot plate touches the polypropylene; H2 stands on stand-offs clear of the walls and floor.
- **Unattended heating only behind the automatic shutdown** (`TEST-PROCEDURE.md` section 3): four normally closed
  Elmwood 2455R thermostats in series with the coils of two Finder 40.52 relays, K1 and K2 (a diode across each coil),
  whose contacts in series switch the heaters and hold both relays in:
  TS1 on H2 (opens by 96 C), TS2 on the floor under H2 (by 63 C), TS3 on H1 (by 63 C), TS4 on the middle heater's body
  (by 144 C). A trip, a pressed STOP, a broken wire or a supply loss turns the heaters off and **keeps them off** until
  START is pressed. Each thermostat's opening temperature is verified on a hot block (V1), the latch on the bench (V2)
  and in place (V3) before the case is first heated, and before every step STOP/TEST is pressed with the heaters on, then each relay contact and START are read open with
  the supply off (V4). **Without
  V1 to V4, every hour of heating is attended continuously** by a person at the case who reads the logger at least every
  10 minutes. **The supply's current limit (6.5 A) and the fuses do not enforce any temperature limit.**
- **The patch runs are always attended**, each pulse timed by hand, and stopped at once at 110 C on the resistor's body.
- **The Arcol ratings depend on their heatsink and derate with temperature** (Arcol 12/14.08): HS50 50 W on 535 cm2 of
  1 mm aluminium, 14 W with none; HS100 100 W on 995 cm2 of 3 mm, 30 W with none; both at 25 C, falling linearly to zero
  at 200 C. H1 is practically the HS100's standard heatsink: 85.7 W at a 50 C plate, 80 W at 60 C, so 83 W only from a
  plate at or under 50 C and for at most 60 s. Each HS50 has less than its standard heatsink on H2, so its limit is the
  200 C hot spot, held by TS4 and the 150 C body stop.
- **Stop limits** (`TEST-PROCEDURE.md` section 8): a wall or the floor 70 C, H1's edge over the o-ring 70 C, H2 100 C, a
  heater body 150 C, the patch resistor 110 C, any smell or smoke. No limit is raised to let a step finish.
- **The lead exit** (check-2, in the package): the leads pass as flat silicone wires between H1 and the frame's o-ring,
  and under the lid gasket with the lid closed, each on a straight run of the seal; they read the conductance high by
  well under 1 percent (check-2's estimate). Peli's purge valve stays (appendix 32.53 item 1; without it 35 K of heating
  raises the pressure by about 12 kPa).
- Drill the case clamped and empty; eye protection; gloves for the patch plate.

## 6. The monitor and the logger

Both deferred, with the procedure's reasons, in `CHECKOUT-LIST.md` section 6.
