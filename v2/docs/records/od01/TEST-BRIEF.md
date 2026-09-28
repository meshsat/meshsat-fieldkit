# OD-01: test brief for the operator (heat balance, then the case mock-up)

MESHSAT-1357, 28 September 2026, prepared by an AI session so the owner can assign the work (ruling D-19); revised by the
coordinator after the independent AI check (`checks/check-1.md`). Prototype: nothing is built; these tests use an empty
case, dummy blocks and made plates, no board. Full procedures: `v2/docs/feasibility/POWER-THERMAL.md` section 10 (test A),
`v2/docs/CASE-MARGINS.md` sections 5 and 7 (test B).

## 1. The two tests, in this order (one case: the heat test needs the sealed skin, the mock-up drills it)

**A. Heat balance.**
- Set-up: the case, the 1450PF frame on the four legs (C6), the blank plate H1 screwed on. The three 6.8 ohm heaters are
  bolted with compound to the dummy stack plate H2 at the stack's place, on stand-offs; the pack block is in its pocket.
- Runs: 21, 42 and 64 W (12.0 V on one, two, three heaters), each held to steady state (3 h or more; the empty case's time
  constant is about 50 min, INFERRED), lid open and closed, fans off (on only if fans are fitted). Then the 2.2 ohm patch
  resistor bolted with compound to H1's four S-M3 nuts at the PA flange site: 45 and 83 W for 20, 30 and 60 s from a plate
  at about +50 C, and its cooling.
- Decides: the enclosure's conductance per lid and fan state; the patch rise under the PA. Lifts: the placement freeze of
  the pack and the PA flange (boards A and P, FEA-004), PWR-F15's flange limits, the +35 and +25 C controls.
- Time: about 2 days of mostly unattended logging for the six fans-off steps, half a day for the patch runs.

**B. Mock-up (after A).**
- Set-up: drill the case from the 1:1 templates; plate C1 with a printed monitor stand-in; stand-ins for boards A, B and E
  on their spacers, and a 21.0 mm printed stand-in for the CM5 cooler until it is picked; one arrestor.
- Checks now: T1, T2, T4, T5, T6, T11. At the build: T3, T7, T8, T9. T10 cannot run until the jumper plug is picked.
- Decides: the OPEN margins resting on Peli's unstated tolerances (the YES rows of `CASE-FIT-UNCERTAINTIES.md` section 2).
  Lifts: T2 and T4 for board B (M1 as a monitor-depth limit, M18) and E (M15b), and for A and P (M4a, M5) once the pack
  hold-down S-27 gives the block's outline; T5 and T11 for board B (M13, M17c, M17w, M17x, M18); T1 the moulding (D-08a).
- Time: T1 15 min at receipt; drilling 2 to 3 h; T2 1 h after the leg tape has cured; T4 2 h; T5, T11 30 min each; T6 1 h:
  about 1.5 working days plus the cure.

## 2. Competence

Mechanical fitting from a drawing: caliper, height gauge and feeler gauges; drilling a polypropylene wall from a paper
template; a torque driver; bonding with tape. Low-voltage bench work: setting a supply's voltage and current limit,
reading volts and amps, crimping terminals, taping thermocouples on, starting a logger and exporting its file. No
soldering (have a heater's leads fitted by someone who solders if its tags need it). No electronics knowledge beyond this.

## 3. Equipment

- **Likely owned:** caliper (0.01 mm); feeler gauges (0.05 to 1.0 mm); a height gauge or depth rod on a flat plate; a bench
  supply of 15 V and 7 A with a current limit; multimeter; torque driver (6-32 and M4); chalk; a drill with hole saws of 29,
  22 and 18 mm, drills of 8 and 4.5 mm and a step drill; deburring tool; phone camera; Kapton tape.
- **To buy or borrow:** an 8-channel type K logger with cold-junction compensation, 0.1 K resolution and a CSV export (any
  make; `CHECKOUT-LIST.md` section 6); ten type K thermocouples with plugs to suit that logger; the heaters, compound and
  dummy blocks (`CHECKOUT-LIST.md`); 3M VHB 5952; ten 6-32 x 1/2 in pan-head screws; silicone wire of 0.75 mm2 or more
  with crimp terminals; the printed stand-ins and the made plates (`MACHINING-RFQ.md`).

## 4. What is recorded, and how it reaches the session

One folder `od01-results/`, handed over as files (copied to the runner or the laptop clone, never typed into a chat):
`checks.csv` (`test, check, row, point, reading, unit, instrument, photo, note`; every OPEN row a check names gets a
line, a reading not taken gets a line with the reason); `heat-steps.csv` (`step, lid, fans, heaters, volts, amps,
start_utc, steady_utc, logger_file`; power is volts times amps, not the label); the logger's CSV exports and the channel
map with a photo per thermocouple; photographs named by check and row, T1's date wheel and markings; the date, the room
temperature at the start and the operator's initials.

## 5. Safety

12 to 13.5 V at up to 6.1 A: no shock hazard, but heat and fire. The heater bodies run near 120 C in a closed case
(INFERRED from Arcol's 3.0 K/W); the patch resistor heats a spot of the plate by tens of kelvin in a minute: gloves. Peli
gives the case body a maximum of 88 C (its 1450EU page): no heater or hot plate touches the polypropylene; H2 stands on
stand-offs clear of the walls and floor. Set the supply's current limit at 6.5 A and fuse every lead. **Stop and switch
off** if a wall thermocouple reads 70 C, H1's edge over the frame's o-ring 70 C, H2 100 C, a heater body 150 C (one
thermocouple sits on one heater), the patch thermocouple 110 C, or on any smell or smoke. Check a powered, closed case at
least hourly or set the logger's alarms at these limits. Drill the case clamped and empty; eye protection.

**The lead exit, a proposal for the independent re-check to accept or change:** the procedure does not say how the leads
leave the sealed case. Proposed: flat silicone wires under the lid gasket at one corner, photographed and noted. It bleeds
some air, so it reads the conductance slightly HIGH (optimistic); the alternative is a sealed gland in the purge valve's
port, which reads it right but alters the case.

## 6. The monitor and the logger

Both deferred, with the procedure's reasons, in `CHECKOUT-LIST.md` section 6.
