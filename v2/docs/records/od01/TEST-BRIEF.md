# OD-01: test brief for the operator (heat balance, then the case mock-up)

MESHSAT-1357, stream od01, 28 September 2026, prepared by an AI session so the owner can assign the work (ruling D-19).
Prototype: nothing is built; these tests use an empty case, dummy blocks and made plates, no board. Full procedures:
`v2/docs/feasibility/POWER-THERMAL.md` section 10 (test A) and `v2/docs/CASE-MARGINS.md` sections 5 and 7 (test B).

## 1. The two tests, in this order (one case serves both: the heat test needs the sealed skin, the mock-up drills it)

| Test | Set-up and runs | Decides | Board gate it lifts | Time |
|---|---|---|---|---|
| **A. Heat balance** | Case with the 1450PF frame on the four legs (C6), the blank plate H1 screwed on; three 6.8 ohm heaters on the dummy stack plate at the stack's place, on stand-offs; the pack block in its pocket. Steps of 21, 42 and 64 W (12.0 V on one, two, three heaters), lid open and closed, fans off (fans on only if the fans are fitted). Then the 2.2 ohm patch block bolted with compound on the plate's two PA-flange studs: 45 and 83 W for 20, 30 and 60 s from a plate at about +50 C (warmed by the block at low power), and its cooling. | the enclosure conductance for each lid and fan state; the patch rise under the PA and its cooling | the placement freeze of the pack and the PA flange site (boards A and P, FEA-004); PWR-F15's flange limits; the +35 C and +25 C controls leaving "proposed" | about 2 h per step until steady (INFERRED from the record's 2.1 W/K and a few kJ/K of heat capacity); 6 steps fans off, 12 with fans; the patch runs half a day: **2 to 3 days, mostly unattended logging** |
| **B. Mock-up** (after A) | Drill the case from the 1:1 templates; plate C1 with a printed monitor stand-in; stand-ins for boards A, B, E on their spacers; one arrestor. Checks T1, T2, T4, T5, T6, T11 now; T3, T7, T8, T9 at the build | the OPEN margins resting on Peli's unstated tolerances (the "YES" rows of `CASE-FIT-UNCERTAINTIES.md` section 2) | T2 and T4: board B (M1 as a monitor-depth limit, M18), E (M15b); A and P (M4a, M5) only once the pack hold-down S-27 gives the block's outline. T5 and T11: board B (M13, M17c, M17w, M17x, M18). T1: the moulding (D-08a). T10 (boards B and E, M17d/f/g/w/x) **cannot run until the jumper plug is picked** | T1 15 min at receipt; drilling 2 to 3 h; T2 1 h after the leg tape has cured (its maker's time); T4 2 h; T5 30 min; T6 1 h; T11 30 min: **about 1.5 working days plus the cure** |

## 2. Competence required

Mechanical fitting from a drawing: caliper, height gauge and feeler gauges; drilling a polypropylene wall from a paper
template with a hole saw; a torque driver; bonding with tape. Bench work at low voltage: setting a bench supply's
voltage and current limit, reading volts and amps, crimping ring or push-on terminals, taping thermocouples on with
Kapton and a dab of compound, starting a logger and exporting its file. **No soldering** (if a heater's tags take solder
only, have its leads fitted first by anyone who solders). No electronics knowledge beyond reading the logger.

## 3. Equipment

**The owner may already have:** a caliper (0.01 mm); a feeler gauge set (0.05 to 1.0 mm); a height gauge or a caliper
depth rod on a flat plate; a bench supply of at least 15 V and 7 A with a current limit; a multimeter; a small torque
driver (6-32 and M4); chalk; a drill with a 27 mm hole saw and a step drill; a deburring tool; a phone camera; Kapton
tape.

**Must be bought or borrowed:** an 8-channel type K logger (any with cold-junction compensation, 0.1 K resolution and a
CSV export; section 6), ten type K thermocouples with plugs to suit it, the heaters, the compound, the dummy blocks
(`CHECKOUT-LIST.md`); 3M VHB 5952 and ten 6-32 x 1/2 in pan-head screws; silicone-insulated wire of 0.75 mm2 or more
with crimp terminals; the printed stand-ins and the made plates (`MACHINING-RFQ.md`).

## 4. What the operator records, and how it reaches the session

One folder `od01-results/`, handed to the session **as files** (copied to the runner or the laptop clone; never typed
into a chat):
- `checks.csv`, one line per reading: `test, check, row, point, reading, unit, instrument, photo, note`; every OPEN
  row a check names gets its own line, and a reading not taken is a line with an empty reading and the reason.
- `heat-steps.csv`: `step, lid, fans, heaters, volts, amps, start_utc, steady_utc, logger_file` (power is V x I, not the
  resistor's label).
- the logger's exports (CSV) and the channel map (which thermocouple sat where, with a photo of each).
- photographs named by check and row; T1's date wheel and markings; the case's label.
- a text line: date, room temperature at start, the operator's initials.

## 5. Safety

The supply is 12 to 13.5 V at up to 6.1 A: no shock hazard, but heat and fire. The heater bodies run well above 60 C
(reichelt lists the parts at 200 C maximum) and the patch block heats a spot of the plate by tens of kelvin in a minute:
burns on touch; gloves for the plate. Peli gives the case body a maximum of 88 C (its 1450EU page), so **no heater or
hot plate touches the polypropylene**: the dummy stack stands on stand-offs, clear of the walls and floor. Inside air
at 64 W with fans off should sit about 30 K above the room (arithmetic on the record's 2.1 W/K). **Stop and switch off**
if a wall thermocouple reads 70 C, the patch thermocouple 110 C, or on any smell or smoke. Set the supply's current
limit at 6.5 A; fuse or limit every lead; check a closed, powered case at least hourly or set the logger's alarm on the
stop limits. Drill the case with it clamped and empty; wear eye protection.

## 6. The monitor and the logger: needed or deferred

- **Monitor (Xenarc 709GNK): deferred.** No check of test A uses it (H1 is a blank). In test B only row M1 needs its
  real depth: the chain from the face to the heatsinks carries the body's 28.66 mm with no tolerance on the held
  drawing and a rear frame whose drawing is owed (`CASE-MARGINS.md` 3.1). A printed stand-in of the drawing's outline
  and depth serves every other reading, and with it T4 yields the largest body depth the real monitor may have while
  keeping M1's 2.0 mm. M1, and so board B's layout entry on that row, then closes when the monitor is in hand and its
  body is read with a caliper against that number (no case needed), or when Xenarc states the tolerance. **Buy it when
  board B nears layout entry, not for this package.**
- **Logger: deferred; borrow first.** Test A needs eight type K channels logged together for hours, with cold-junction
  compensation and a file export. Nothing in the procedure needs the PicoLog TC-08 as such: any such logger, or two
  four-channel logging thermometers started together, serves. Before each run, soak all thermocouples together at room
  temperature for 15 minutes and record each channel's offset, so the rises are read differentially. Test B needs no
  logger. Buy the TC-08 (GBP 349) only if no logger can be borrowed.
