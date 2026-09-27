# MeshSat field kit V2: concept of operations

**Status: DRAFT for Review A of the foundation baseline (MESHSAT-1357), written 25 September 2026, revised the
same day after an independent challenge, and revised on 26 September 2026 to carry the owner's rulings D-01 to
D-17 of 25 and 26 September 2026 and the choices the session took under the owner's standing rule of 26
September 2026; section 7 lists every question with its ruling, and D-18, the one still open and
conditional. Corrected later on 26 September 2026 (appendix 32.367): the owner reversed D-08 at about 09:30 CEST
and D-08a stands (section 7), the session settled SC-02 at about 11:35 CEST (section 2a), and the pack's
transport route follows the review of that day (section 4, Transport row). Corrected again later that day (open
item S-07 of the requirements registry): sections 3 (M2 and M4), 4, 4a (PS-EMCON), 4b and 5 describe the circuit
as generated at `45bde541`, after the circuit corrections of `faf8c981`, `458b2873` and `d90f30e4`; no need of section
2 changed.** **Revised on 27 September 2026 to close the layer-2 items of the handover audit (MESHSAT-1357; the owner's
execution prompt of that day, `reviews/2026-09-27-handover-execution-prompt.md` sections 2 and 3):** the reduced mode
is defined with the modules that can host it (section 4c), the hot end is stated as controls on measured internal
temperatures with the ambient figures as bounds (section 4c), the power and runtime figures follow
`feasibility/POWER-THERMAL.md` (sections 4a, 5 and 6), EMCON's latency and fault conditions are carried (section
4b.1), storage, transport, commissioning, shutdown and faults have scenarios (sections 4, 4d, 4e and 4f), the mission
duration, the duty profile, "aged" and the recovery and delivery targets are set, and every choice this revision took
is in section 7a. No need of section 2 changed. Prototype design. **Revised again on 27 September 2026 (pass 2) to
answer the seven blocking findings of Review A's first pass (`reviews/REVIEW-A-LAYER-2-2026-09-27.md`, B1 to B7) and
its minor ones:** the heat stage's losses and its shutdown source are stated (sections 4 and 4c); a start-up with the
lid closed is defined on what the panel controller can know (section 4c); M1's finding is restated with the pack's
energy across the night as the binding limit (section 3); the closed-lid requirement stays at the owner's example set,
the bank allocation that lets one module carry it is taken as a board B design item (BANK-R1), and the generated
board's shortfall is stated as a finding (section 4c); commissioning drops the ten-minute key-down that K1 forbids
(section 4d); and the cold end names the warm-up that brings the inside air to 0 C and the conductance at which it
fails (section 4c). **Revised a third time on 27 September 2026 (pass 3) to answer Review A's second pass (P2-B1,
P2-B2) and the ConOps side of Review B of layer 3 (`reviews/REVIEW-B-LAYER-3-2026-09-27.md`, B1 to B5):** past the
heat stage the kit acts on the pack's measured cell temperature on every input state, the hot stop, whose path from
the sensor controller to the panel controller is a board A and board E design item (HOT-R1) and whose firing inside
the envelope stays a feasibility question (sections 4, 4c, 4e and 4f, and M2); M1 carries the solar window board E's
generator declares and the design month of its energy balance, with no season taken off the mission (section 3); the
NVG mode has a compatibility target and no claim before its test (section 4, NVG row); the lightning mast-down alarm
is carried (section 4e); and the session's choices in D-02b's row are marked as the session's (section 7).

**Review A, the gate this layer closes through (defined 27 September 2026).** One fresh reviewer who wrote none of
this layer's documents checks this document, `OPERATING-ENVELOPE.md`, `v2/ecad/tools/pcb_envelope.yaml`, the operator
sections of `PANEL.md` (1, 3, 5, 8, 9 and 10) and the state and envelope rows of `TEST-PLAN.md`, at one pinned commit,
against the layer-2 items of the owner's execution prompt (section 3: normal, degraded, startup, charging, shutdown,
storage, service and fault scenarios; the operating envelope; simultaneous modes; the explicit behaviour of the core
functions; product decisions settled under existing authority) and against `ARCH-PCB-B-IOHA.md` section 15,
`feasibility/EMCON.md` section 5a and `feasibility/POWER-THERMAL.md` section 9. The review is recorded under
`v2/docs/reviews/` with the commit it read, **labelled AI review**; it is never a qualified review,
it replaces no qualified review a record requires (D-09), and it establishes no circuit's correctness. Its findings are answered
in the documents; the layer is then marked baselined at that commit. The first pass was recorded
(`reviews/REVIEW-A-LAYER-2-2026-09-27.md`: FAIL, seven blocking findings, read on `e3aedb25` with this revision's first
draft) and pass 2 answered it; the second pass (the same record, FAIL, two blocking findings, P2-B1 and P2-B2) is
answered by pass 3, and a pass at the integrating commit decides the baseline. Until a pass
finds no blocking item this document is a DRAFT for Review A. Prototype design.
Nothing described here has been built, powered or field deployed. This document says how the kit is meant to be
used, so that requirements, budgets and tests have something to trace to. The needs of section 2 carry stable
identifiers (NEED-nn); requirements trace to them, and an identifier is never reused for a different need.
Numbers that no source in this tree supports are written **TBD** with the effect of not knowing them; they are
never filled with a convenient value. Every power and runtime figure is **PROVISIONAL**: it is arithmetic over
datasheet figures, generator declarations and placeholders, and nothing has been measured.

Sources: `PRODUCT-BRIEF.md`, `V2-SPEC.md`, `OPERATING-ENVELOPE.md` (adopted 21 September 2026, decision 34),
`PANEL.md`, `ARCH-PCB-B-IOHA.md`, `ASSEMBLY.md`, `TEST-PLAN.md`, `v2/ecad/tools/pcb_board_facts.yaml`
(`_product`), the generators `v2/ecad/tools/gen_sch_*.py` where a statement is about what the design carries, and
the design record `MESHSAT-709-geometry-appendix.md` sections 32.49, 32.50, 32.52, 32.53, 32.54, 32.55, 32.56 and
32.62. `PANEL.md`, `ARCH-PCB-B-IOHA.md`, `OPERATING-ENVELOPE.md` and `ASSEMBLY.md` are revised in the same
baseline, so they are cited by section rather than by line. Since 27 September 2026 the figures of sections 4a, 5, 6
and 4c come from `feasibility/POWER-THERMAL.md` and its model `records/rv-pwr/pwr_budget.py` (with
`records/rv-pwr/pwr_budget.json`), and the states that model did not carry (the reduced mode, the heat stage in both
of its configurations, EMCON as generated, and the cold end of section 4c) from `records/hc2/pwr_red2.py`, which
imports it unchanged (its output `records/hc2/pwr_red2.out`; filed with this revision), and the hot stop's thresholds
and the ambients at which it acts from `records/hc2/hotstop_bounds.py` (its output `records/hc2/hotstop_bounds.out`,
arithmetic on `pwr_red2.out` and the battery packet's error budget; filed with this revision). Where two sources disagree, this document says which one it follows and why, and the disagreement is
carried in the foundation's conflict list (W1's list of 25 September 2026, `records/w1/w1-conflicts.md`, with W1's
owner decision table `records/w1/w1-decisions.md`) until it is resolved; the conflicts that bear on a requirement are
also carried as conflict records in the requirements registry `v2/ecad/tools/pcb_requirements.yaml`.

## 1. Actors and external systems

| Actor or system | Relation to the kit |
|---|---|
| Kit operator | deploys, powers, configures and operates the kit at its face plate. The prototype is non-commercial and is to be operated in the Netherlands and the EU by a licensed radio amateur (owner ruling D-04, section 7): every transmitter is to be configured to the operator's licence and the EU limits, and the VHF path is to get a band lock (a design item, not in the generators yet). The HF transmitter is to operate on the amateur bands under the owner's licence (appendix 32.50 item 16a) |
| Second crew member | voice on the second headset jack with its own push-to-talk (32.50 item 16g) |
| Local end users | Meshtastic LoRa handhelds, Zigbee and Thread devices, WiFi clients, the lid tablet (ATAK class, fed by the USB-C outlet and the kit's WiFi, 32.50 item 16d) |
| Remote correspondents | reached over Iridium Messaging Transport, 5G cellular, HF (Winlink, Reticulum over the Mercury modem), VHF APRS, or a second kit; the recipients of an SOS message are a configured list (owner ruling D-10) |
| Second kit | kit-to-kit WiFi link without an access point, LoRa mesh, HF |
| Power sources | the kit's own pack (one 4S3P block, owner ruling D-06), a 9 to 36 V vehicle or shore supply (NATO 2-pin plug cable, 32.50 item 16b; not qualified against any vehicle surge standard, and not for 24 V military vehicle buses, owner ruling D-16), a solar panel |
| Powered accessories | PoE out on the sealed Ethernet port, the USB-C outlet, which carries power only (owner ruling D-12) |
| Service laptop | console and key fill over the sealed Glenair 233-370 USB receptacle on the connector plate (owner ruling D-12) |
| Time and position | GNSS constellations, DCF77 (77.5 kHz) |

## 2. Needs

| ID | Need | Source |
|---|---|---|
| NEED-01 | Relay messages between local off-grid networks and remote correspondents when internet and cellular infrastructure are absent or down. | MeshSat Bridge purpose; `V2-SPEC.md` bearers table (lines 37 to 51) |
| NEED-02 | Keep at least one long-range path when any single bearer is unavailable. | `V2-SPEC.md` lines 40 to 50; `ARCH-PCB-B-IOHA.md` section 8 |
| NEED-03 | Keep the kit's services and every critical peripheral reachable after the loss of any one compute module or any one I/O supervisor. | `V2-SPEC.md` line 29; appendix 32.52 (line 2829); `ARCH-PCB-B-IOHA.md` section 1 |
| NEED-04 | Let an operator and a second crew member run the kit at the kit: see its state, operate it, talk with push-to-talk, capture images, and read identity and status with the power off. | `V2-SPEC.md` lines 53 to 62; 32.50 items 9, 10, 16d, 16g |
| NEED-05 | Run from the kit's own pack, recharge from vehicle, shore or solar, and power accessories. | `V2-SPEC.md` lines 15 to 24; 32.50 items 1, 2, 16b; owner rulings D-06, D-11, D-12 |
| NEED-06 | Survive carriage and field placement in a sealed case: transit drop, vehicle vibration, driven rain and blowing dust when deployed, immersion when closed, with no vent opening. | 32.53 (line 2864); 32.62 (line 3056); 32.50 item 16e; `TEST-PLAN.md` E1, E2, E6, E7, E8; owner ruling D-02c |
| NEED-07 | Operate and store across the adopted temperature envelope, with its declared carve-outs. | `OPERATING-ENVELOPE.md` section 4; owner rulings D-02a, D-02b, D-02d, D-02e |
| NEED-08 | Silence every transmitter with one operator action that does not depend on software. | 32.50 item 3 (line 2787); `PANEL.md` section 6; owner ruling D-05 |
| NEED-09 | Darken and silence the kit on command (blackout), and give a night-vision-compatible panel (NVG). | 32.50 item 16c (line 2802); `PANEL.md` section 8 |
| NEED-10 | Protect stored keys and data: erase them on command, record case opening, and fill keys only by a signed procedure. | 32.50 items 5 and 6, 16f; `V2-SPEC.md` line 34; owner rulings D-03, D-12, D-13 |
| NEED-11 | Provide position and time, with a second time source and holdover when GNSS is lost. | 32.50 items 11 and 13; `V2-SPEC.md` line 35 |
| NEED-12 | Sense the kit's own condition and its surroundings, and act on the hazards (water on the floor, battery-bay gas) by shutting the pack down. | 32.50 item 14 and the sensor walk-through (line 2802); 32.54 (line 2896); `V2-SPEC.md` line 65 |
| NEED-13 | Keep the energy store safe: cell protection independent of software, fault current bounded at every stage, charge only inside the cells' temperature window. | rules BAT-001, BAT-002, PWR-003; `TEST-PLAN.md` section 5; `OPERATING-ENVELOPE.md` section 3; 32.62 ("MIL-STD if possible"); owner rulings D-11, D-15 |
| NEED-14 | Be serviceable: open the kit, lift the stack out without unscrewing a cable, program and recover every programmable device, reach the test points a bring-up needs. | `V2-SPEC.md` line 13; rule TST-001; owner rulings D-12, D-14 |
| NEED-15 | Be verifiable: every requirement has an analysis, inspection or test, and the prototype runs a whole-kit test plan with pass criteria before any rating or envelope is claimed. | 32.50 item 16e (line 2804); rule ENV-002; `TEST-PLAN.md`; owner ruling D-09 |
| NEED-16 | Transmit only where and how the operator is permitted (bands, power, duty cycle, licence) in the markets the owner scopes. | 32.49 item 4 (EU LoRa cap, line 2761); 32.50 item 16a (amateur bands, HF); markets scoped by owner ruling D-04 |
| NEED-17 | Keep the kit's own transmitters from damaging or blinding its own receivers. | 32.50 item 4 (line 2788); `TEST-PLAN.md` M6 |
| NEED-18 | Work in its electromagnetic surroundings: bounded conducted and radiated emissions outside the intentional transmissions, and no upset from conducted, radiated or electrostatic disturbance. | 32.50 item 16e (line 2804); `TEST-PLAN.md` M1 to M5 and M7; decision 34 (ESD level); owner rulings D-04 (no EMC claim for the prototype) and D-17 |
| NEED-19 | Let the operator raise a distress or assistance alert with one deliberate, covered action. | `PANEL.md` sections 1, 3 and 9; `V2-SPEC.md` line 58; owner ruling D-10 |

NEED-18 and NEED-19 were added in the revision of 25 September 2026: the approved test plan already tests
NEED-18, and the SOS toggle is on the face, but neither had a need to trace to.

### 2a. What prototype 1 is accepted against (owner ruling D-01)

The owner ruled the prototype scope on 25 September 2026: **full design, staged acceptance.** Every ruled function
stays designed and fitted where copper exists; prototype 1 is accepted on a named core, and everything else is
built where possible and reported NOT_YET_TESTED, never as a pass. The functions the ruling names as outside the
core are the Geiger counter, the lightning detector, DCF77, the outside sensor pod, the camera, net audio
recording, the tablet bracket, the NVG claim, HF and a second pack. Deferral removes nothing from the design.

The second pack has no location found yet: no pack is expected to fit the 160 mm west pocket as the board set
stands (INFERRED from the committed board B underside, `v2/ecad/tools/panel1450.py` line 23, against the pocket of
appendix 32.62; no case measurement is owed since the owner reversed D-08 on 26 September 2026), and the pack ruling D-06 of 26 September 2026 sets one pack
in the east pocket, with missions longer than it relying on vehicle or solar input. The second pack stays a
deferred function of D-01; it is not withdrawn.

| Core function | Needs it traces to | What the core covers |
|---|---|---|
| Messaging over Iridium, 5G, LoRa and APRS | NEED-01, NEED-02 | the four named bearers; HF is deferred, VHF voice is not named, and the kit-to-kit WiFi link is exercised through the fabric's changeover test (IOHA A11) |
| The three-slot failover fabric | NEED-03 | `ARCH-PCB-B-IOHA.md` acceptance tests A1 to A14 |
| Pack, vehicle and solar charging | NEED-05 | the three inputs (shore uses the vehicle's 9 to 36 V input, `V2-SPEC.md` line 21); the accessory outlets are not named |
| Hardware EMCON | NEED-08 | EMCON as D-05 rules it (section 4b) |
| ZEROIZE of the secure element | NEED-10 | ZEROIZE as D-03 rules it (section 4, ZEROIZE row); the case-open record and key fill are not named |
| Pack safety | NEED-13 | the pack's protection, including the floor of D-15 |
| Service and programming access | NEED-14 | console, `rpiboot`, SWD and the dock-lift procedure of D-14 |
| SOS | NEED-19 | SOS as D-10 defines it. **Taken by the session under the owner's standing rule of 26 September 2026:** D-01 does not name SOS, D-10 then defined its action (firmware only), and W1's decision table had recommended it for the core |

**The attribute is carried per requirement, not per need.** A requirement under a need that the table does not
name is core when it is a condition of a core function: fitting the boards and the pack into the 1450 (NEED-06), a
core transmitter kept inside the operator's licence and the EU limits (NEED-16), a core transmitter that must not
blind a core receiver (NEED-17), or the test plan's tracing rules that the core is accepted through (NEED-15). A
requirement under a named need is deferred when it serves a function the ruling leaves out, such as the accessory
outlets under NEED-05 or the HF rail. The environmental, EMC and self-interference tests outside those conditions
(NEED-06, NEED-07, NEED-15, NEED-17, NEED-18) are reported NOT_YET_TESTED until they run, and when they run they keep
the pass lines of D-02a and the severities of D-02c. Reading D-01 this literally for qualification (the ruling
names the core and says the rest is reported NOT_YET_TESTED) is **taken by the session under the owner's standing
rule of 26 September 2026**. The classification record by record is in the requirements registry.

**Which peripherals NEED-03 protects.** Every USB peripheral that `ARCH-PCB-B-IOHA.md` section 15 traces, each
designed to move with its bank, and the kit-to-kit WiFi link, whose antennas move to the standby card (IOHA A11).
The LoRa module (slot 3's SPI) and cellular data (slot 2's PCIe lane), which have no second path and go down with
their module, are **NAMED EXCEPTIONS to NEED-03 for prototype 1**, as `ARCH-PCB-B-IOHA.md` sections 15 and 15a and
appendix 32.366 record. **Settled by the session under the owner's standing rule of 26 September 2026 (SC-02,
about 11:35 CEST):** making either bearer critical needs a second LoRa site or the 5G module moved to USB 3, and
both change the floor plan of board B, the board that is not routed; the exceptions need no board B change, and
without them the kit is designed to keep at least three of D-01's four messaging bearers through the loss of any
one module (`ARCH-PCB-B-IOHA.md` section 15a). Reverse by naming either bearer critical, which reopens board B's
floor plan. **Corrected 26 September 2026:** this paragraph first called the two "open design gaps against
NEED-03, not accepted exceptions", on the reading that the owner's requirement ("every device visible to all
modules", `V2-SPEC.md` line 29) names no exception; that contradicted section 15a and appendix 32.366, and SC-02
settles it as above. Prototype 1's NEED-03 acceptance stays IOHA tests A1 to A14, as D-01 names it.

## 3. Representative missions

Each mission is written as intended use of a prototype design, not as a record of use. The needs it
exercises are listed so that a requirement with no mission behind it, or a mission outcome with no
requirement, is visible. Power states (PS-...) are defined in section 4a.

### M1. Remote site relay on pack and solar (72 hours)

**Setting:** a team at a place with no infrastructure. The kit sits on a table or a vehicle tailgate, lid open,
shaded, antennas on the end-wall jacks, a solar panel on the solar input. **Operating shaded is a stated operating
condition (owner ruling D-02e, 26 September 2026)**, with a shade accessory, a lid sun shield or a tarp: a black
plate in full sun absorbs about 60 W, more than the electronics (32.53), and full-sun operation is a later
qualification item. **Sequence:** deploy; start up; the local team's Meshtastic handhelds join the LoRa mesh;
outbound messages leave over the bearer the MeshSat routing layer picks by cost (free bearers first, metered ones
such as Iridium only when nothing free is up; the Bridge README); inbound messages are shown on the monitor, the
MSG lamp and the e-paper; by day the pack charges from solar while the kit runs; at night the panel goes to NIGHT
lighting. **Must hold:** a message typed on a handheld reaches a remote correspondent over at least one bearer
(NEED-01, NEED-02); the kit keeps running on its pack plus solar for the mission's duration (NEED-05). **The
duration is 72 hours, taken by the session under the owner's standing rule of 26 September 2026 (section 7a) in
place of the setting D-06 reserved for the owner, which replaces it whenever he gives one.** The energy basis is
PS-IDLE-SPEC, the idle state of the D-06 runtime requirement (42.8 W at the pack terminals, section 4a), with the
reduced mode as the operator's lever when the balance is negative. **What that asks of the kit's energy, and what the
design gives (a layer-4 finding, not a reason to shorten the mission; restated on 27 September 2026 after Review A,
B3).** Two limits, and the first binds. (1) **The night.** Solar input stops in the dark, and an aged pack holds about
108 Wh usable (INFERRED: each state's aged runtime times its power, section 4a), which carries the kit through 2.5 h
of darkness at PS-IDLE-SPEC, 3.5 h in the reduced mode and 4.7 to 5.0 h in the heat stage (3.2, 4.3 and 5.9 to 6.3 h
on a new pack). At the Netherlands' latitude, about 52 N, the sun is down for about 7 hours at midsummer and about 16
at midwinter (INFERRED from the latitude; no ephemeris is held in this tree); only near the Arctic Circle, at the EU's
northern edge in summer, are nights as short as the pack, and a panel gives little near dawn and dusk. So across the
market D-04 scopes, those northern summers apart, on its pack and solar alone the kit does not run through a night, in
any state and at any solar rating, with the one pack of D-06 and the second pack D-01 defers: the shortest night at 52 N in the lightest state
asks about 150 Wh (21.7 W for 7 hours) of the 108 Wh held. (2) **The day's
energy.** 72 hours at 42.8 W is 3.08 kWh, so solar must supply about 1.0 kWh a day through the charge path; the kit's
input front end regulates 20 V at up to 5 A, about 100 W (32.55), so the panel would have to deliver that full rating
for about 10 to 11 hours of every 24, which a fixed panel does not do: on the design month's mean day (September at
Leiden, 4.0 kWh/m2 a day on a panel inclined at the optimum 40 degrees, PVGIS-SARAH2 2015 to 2020,
`v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json`; the requirements registry's reference day, a session choice,
section 7a) the 72 hours ask for a panel rated about 266 W; in the reduced mode (31.4 W, section 4a) about 7.5 to 8
full hours a day, and in the heat stage (21.7 to 23.3 W) about 5 to 5.5. **The solar input's window is set**
(REQ-016, a session choice of 27 September 2026, section 7a): a panel of at most 25 V open circuit at its coldest,
held at 17.6 V by board E's LT8705A stage, and at most 100 W into it, as board E's generator declares the entry (its
v_max of 25 V on the panel entry, against which every part on it is judged); whether the input path is re-rated to
carry the day's energy is judged in layer 4, where the requirements registry's M1 balance record (REQ-072) reads FAIL
at desk on both limits. September is the design month of that judgement, not a season M1 is limited to: M1 keeps the
setting this section gives it, with no season taken off it, and a month with less sun asks more of the panel
(December's mean on the same plane is about 1.1 kWh/m2 a day), which layer 4 records beside the design month. **The
routes that carry the night, none of them taken here:** an overnight input on the 9 to 36 V vehicle and shore entry
(a vehicle, a shore supply, or any DC source inside that entry's window, an external battery included, with no board
change); the second pack that D-01 defers, which has no location found (section 2a); or a larger pack, which reopens
D-06. The first changes M1's setting and the other two are the owner's rulings to reopen, so M1 stays as set and the
finding stands. **It is reported to the owner at the next checkpoint, not asked,** as a consequence of D-06's one pack
together with the session's 72 hours: on pack and solar alone the kit does not hold M1 through a single night,
whatever the solar rating. The battery-only runtime per power state is PROVISIONAL (section 6). The
pack gauge holds charging off when the cells are outside their temperature window (NEED-13). **Consequence accepted by
the owner (ruling D-02b), and what the analysis now bounds it at:** the owner accepted that, with three loaded modules
and the lid open, charging holds off above about +25 C ambient, a figure argued on an estimated 16 K inside-air rise.
With the power figures of section 4a, three *typical* modules put the hold-off at +19.5 to +21.6 C on the design
record's own enclosure conductance (appendix 32.53) and anywhere from -17.8 to +19.4 C on the independent bound
(`feasibility/POWER-THERMAL.md` section 9.2); the enclosure conductance is unmeasured and decides where in that range
it falls. The behaviour does not depend on the number: the gauge holds the charge on the cells' own measured
temperature whatever the ambient (section 4c). So the kit charges freely only in cool conditions or in the reduced
mode, and the ambient at which it stops is a bound until the empty-case heat-balance test (`TEST-PLAN.md` T-H1)
measures the conductance. The ruling stands; the changed figure is reported to the owner at the next checkpoint, not
asked.

### M2. Vehicle move with position reporting

**Setting:** the kit travels in a vehicle, powered from the 9 to 36 V vehicle input, lid closed. The input
carries no vehicle surge claim and is not for 24 V military vehicle buses (owner ruling D-16, section 7).
**Sequence:** the kit runs in the reduced mode (32.53: closed-lid operation is the reduced mode); GNSS keeps
position and time; APRS position beacons and LoRa mesh traffic continue over the end-wall antennas if they
are fitted. **Must hold:** vehicle power runs the kit and charges the pack inside its window (NEED-05);
vibration does not loosen a fastener, connector or pigtail (NEED-06, `TEST-PLAN.md` E2, the severity D-02c rules).
**Ruled (D-02b):** the kit operates with the lid closed in a defined reduced mode; the owner's example is GNSS,
LoRa mesh, Iridium and APRS beacons, monitor off, one compute module. **Defined 27 September 2026 (section 4c):**
the reduced mode runs two modules, slots 2 and 3, because no single slot can host the owner's example set with the
SOS path as board B is generated (Iridium and the panel controller hang on bank 1, whose hosts are slots 1 and 2;
the LoRa module is on slot 3's SPI; `ARCH-PCB-B-IOHA.md` sections 4 and 15); it carries GNSS, the LoRa mesh, Iridium,
APRS beacons, the SOS path and 5G, with the monitor off. The closed-lid state and its thermal test are in
`TEST-PLAN.md` (section 1, state "deployed closed-lid"; E3-L). **The move is a use state, not the Transport mode:** a
kit operated in a vehicle runs the reduced mode on the vehicle input; a kit carried as cargo is off, its pack in the
gauge's shutdown (section 4, Transport row). Taken by the session under the owner's standing rule (section 7a).
In a hot vehicle the heat stage and, past it, the hot stop act on the vehicle input as on the pack (section 4c): the
kit sheds to its minimum load before its cells pass +60 C, shuts itself down if they keep rising, and restarts once
they have cooled; whether that happens at +40 C with the lid closed is FEA-004's, open until the enclosure is measured.

### M3. Two kits linked

**Setting:** two kits a few hundred metres to a few kilometres apart (range **TBD**, antenna and terrain
dependent). **Sequence:** the kits form a WiFi link without an access point over the P2P antenna pair and
share each other's bearers; LoRa mesh traffic crosses between the two meshes. **Must hold:** the link comes
up with no access point (NEED-01); if the primary WiFi card or its compute module fails, the second card
takes the antennas under voted control and the link returns (NEED-03, `ARCH-PCB-B-IOHA.md` A11: margin
within 1 dB of the primary path).

### M4. Emission-controlled posture

**Setting:** the operator must stop all emissions for a period, then send in a short window.
**Sequence:** EMCON toggle closed: the hardware line puts the radios dark as section 4b sets out, the software
holds and queues every send (an SOS included, which is queued and announced to the operator, D-10), the e-paper
shows EMCON (`PANEL.md` sections 6 and 9); LIGHTING at BLACKOUT darkens the panel and the monitor and mutes the
speaker and the sounder; at the window the operator opens EMCON, the queue drains, EMCON closes again; if the kit
is about to be lost, ZEROIZE. **Must hold:** once EMCON is closed, every transmitter's output falls below the pass
line within its row's maximum latency L_max and stays there while EMCON stays closed, by a path that needs no
software (NEED-08): 1 s for every radio but the 5G module; for a 5G module that has been turned on, 20 s set by
hardware timers at their worst tolerance, with its disable pin pulled at once; 0 at power-up under EMCON (section
4b.1, `feasibility/EMCON.md` section 5a). So "no transmitter emits while EMCON is closed" holds from the end of each
row's L_max, not from the instant the toggle closes. Nothing lights or sounds in blackout (NEED-09); ZEROIZE destroys
the secure element's wrapping keys as ruled in D-03 (section 4, ZEROIZE row; NEED-10).
**Ruled (D-05, 26 September 2026): radios dark.** Every radio with an emission path is powered off or RF-disabled
in hardware; the VHF path keeps listening because its gate is on the transmit side only; GNSS, DCF77 and the
lightning sensor continue. The kit therefore stops RECEIVING on every other radio while EMCON is closed. As
generated since `458b2873` the two gaps this mission first named are closed in the schematic: the compute modules'
own WiFi and Bluetooth are pulled off through open drains, and the WiFi link cards lose their supply. What remains is
session work under the ruling (S-01), read transmitter by transmitter in `feasibility/EMCON.md` section 0a: the 5G
module, whose only path was its disable pin, a firmware-mediated airplane mode, and the items every row of the EMCON
line shares (section 4b). **Since board B's round 8 (27 September 2026) the 5G module's supply is removed by hardware
at once and board B's shared items are drawn (section 4b)**, so the radio's own chain is closed at desk for 15 of the
17 transmitters and open for two: the SA868 (its PTT pin's receive threshold is unpublished) and the RockBLOCK 9704
(once its supply is cut it runs on its own supercapacitors with its ENABLE held by firmware). No row is closed end to
end, from the toggle to silence at the antenna port, so NEED-08 is not met for any transmitter until the design closes
it, and no row has been shown on a bench.

### M5. Degraded operation during a mission

**Setting:** any of M1 to M4, when something fails or the weather turns. **Sequence and outcomes, as designed:**
one compute module stops: its I/O bank moves to its neighbour under 2-of-3 voted control (bank 1 to slot 2, bank
2 to slot 3, bank 3 to slot 1, per `gen_sch_b.py` line 543 and `ARCH-PCB-B-IOHA.md` section 4) and k3s
reschedules the workload; the two bearers with no second path go with their slot (the LoRa module on slot 3's
SPI, cellular data on slot 2's PCIe lane; `ARCH-PCB-B-IOHA.md` section 15), which section 2a records as the named
exceptions to NEED-03 for prototype 1 (SC-02); every device of the moved bank is required back in service within
30 s of its home module's loss, plus the device's own start-up where its maker states a longer one, and the bridge's
own service back on a surviving module within 60 s (section 4c, where "back in service" is defined); a
slot whose heartbeat stays flat for 60 s is power-cycled once and then left off until the
operator acts (`PANEL.md` section 5); when a long-range bearer is declared down, a queued message goes over the next
bearer that is up (section 4c, delivery targets). **In the heat** the kit sheds on measured internal temperatures,
not on an ambient reading (it has no ambient sensor in prototype 1's core: the outside pod is deferred by D-01): at
+50 C inside air or +55 C on any cell it drops to the reduced mode (slots 2 and 3, monitor off), and if those
triggers are reached again there, to the heat stage, one module, which is required to carry the owner's example
(GNSS, the LoRa mesh, Iridium and APRS beacons) with the SOS path: slot 3 once board B carries the bank allocation
BANK-R1, and until then slot 2, which keeps the SOS path, Iridium, GNSS and 5G and loses the LoRa mesh, APRS and the
pack's readings, a shortfall stated as a finding against the generated board (section 4c). So in the heat the kit
has no compute redundancy left, the consequence the owner accepted with D-02b; the ambient at which each stage acts
is a bound, not the +35 C of the ruling's argument (section 4c). Below -15 C the e-paper updates slowly or not at all; below 0 C
inside air the two WiFi link cards and the SDR stay unpowered (their makers' ranges) while the kit's cold warm-up, the
pack heater with the three modules loaded, brings the air to 0 C, which at the envelope's -20 C it does on the record's
conductances but not above about 3.6 W/K (section 4c); below 0 C at the cells the pack gauge holds charging off until the pack is warmed. A kit
that has cold-soaked below about -10 C at the cells does not start from its pack: cold start from the pack is out of
scope for the prototype (owner ruling D-02d), so it needs shore or vehicle power, or warming, first; once it is warm
and running, the in-use envelope down to -20 C ambient applies. The faults of section 4e (the panel controller, the
ribbon, a device rail, a fan, water, gas, a pack protection trip, an input) each have their indication and recovery
there. **Must hold:** a single fault degrades a capability, never removes every path (NEED-02, NEED-03), except the
common modes section 4e names, and the operator is told (MASTER CAUT or MASTER WARN, the e-paper).

## 4. Operating modes

"Guarantee" says what is designed to hold the mode: **HW** means a hardware line that holds with every processor dead,
**FW** means firmware on the panel or sensor controller, **SW** means software on the compute modules.
The table has eighteen rows: the fourteen of the first draft, SOS (added on 25 September 2026), the heat stage
and commissioning (added on 27 September 2026), and the hot stop (added later that day, pass 3). "Power state" points
to section 4a. How the reduced mode, the heat stage, the hot stop, the hot and cold ends, the recovery and delivery targets and the graceful shutdown are set is section 4c;
commissioning is section 4d; the faults are section 4e; section 4f joins the core functions to every mode.

| Mode | Entry | Exit | Running | Off or held | Guarantee | Power state | Source | Open |
|---|---|---|---|---|---|---|---|---|
| Transport | carried as cargo: lid closed and latched, antennas off, cables out, pack fitted, the kit off, and the pack put in the gauge's SHUTDOWN (ManufacturerAccess 0x0010 over the pack's SMBus, sent by the sensor controller: the gauge opens both FETs, TI SLUUAQ3A 5.4.2; `gen_sch_e.py` line 213), which it enters only with no charger present (SLUUAQ3A 5.4.2 and 13.1.8), so every input is unplugged first | an input applied (the gauge returns to NORMAL when its PACK pin rises above VSTARTUP, SLUUAQ3A 5.4.2), then deploy | nothing; no load on the cells | everything | the pack's hardware protection, which needs no firmware: its PTC trip ("also works in SHUTDOWN mode", SLUUAQ3A 3.15) and the floor of owner ruling D-15, in board P's schematic since `faf8c981` (a BQ7720700 second level whose over-voltage, open-wire and over-temperature output blows the chemical fuse F2, as the gauge's FUSE output can, once the arming jumper JP1 is closed at commissioning, and whose under-voltage output holds the discharge FET off; `gen_sch_p.py` lines 243, 288 and 414 to 502 at `45bde541`, with the over-temperature network of `d90f30e4`); the 25 A blade | PS-SHUT | `TEST-PLAN.md` section 1; session choice of 27 September 2026 (section 7a) | a kit operated in a vehicle is not in this mode: it runs the reduced mode on the vehicle input (M2). Altitude 0 to 4500 m in transport and 0 to 3000 m in use (owner ruling D-02c). The cell maker's restriction applies: the kit with its pack fitted is never left "in a car or similar place where inside of temperature may be over 60°C" (Samsung INR18650-35E Ver. 1.1, handling notes). The pack's transport route (owner ruling D-04, REQ-069): **no route is claimed**. The pack is built for the kit rather than bought and its UN 38.3 status is unknown, and an unknown status permits no route by itself: road carriage has its own dangerous-goods rules (the ADR, which the Dutch ILT names for road consignments; review of 26 September 2026, `reviews/2026-09-26-foundation-progress-review.md` section 5, reference R5), as air and parcel carriage have theirs. The pack's classification, the conditions that apply to it or an exception that applies are to be established from the ADR's own text before any route is claimed; that is a bounded desk item (the battery stream's), not a broad compliance project, and no ADR text is held in this tree yet (the UNECE site refused this host on 27 September 2026, HTTP 403). No mode, interface or board of this layer depends on its answer, because nothing claims a route; if the reading requires a UN 38.3 test, that is a purchase for the owner, and if it requires the pack to travel apart from the kit, the pack's bonded mounting (`ASSEMBLY.md` section 1, VHB pads) reopens in layer 7. **What this state does not run** (Review A, m5): board E's always-on domain sits on the pack side of the gauge's FETs, so with the pack in shutdown the lid and tamper log (NEED-10's case-open record, REQ-036) does not run while the kit is carried, and the kit cannot start from its own pack until an input has woken the gauge (Deploy row). **Corrected 26 September 2026:** this cell had stated a road route with the kit as the session's choice, inferring from the unknown status that carriage by road was open where air and parcel carriage were not; that inference is withdrawn (appendix 32.367). **Changed 27 September 2026:** the kit in transport is off with its pack in the gauge's shutdown; before, whether it was powered was TBD |
| Deploy | operator opens the lid, fits antennas, connects cables, shades the plate (D-02e); a kit whose pack is in the gauge's shutdown (Transport, Storage) first gets an input (shore, vehicle or solar) to wake the gauge, and a kit out of storage is charged before a mission, because it was stored at about 30 % charge | startup | none | none | operator | PS-SHUT to PS-OFF | `TEST-PLAN.md` section 1 | none |
| Startup | MAIN PWR held (hardware lead to board A's power controller) | normal, reduced or degraded | board A's 3.3 V and the shared device rail come up; the panel controller boots, reads the ZEROIZE toggle (`ZEROIZE_SW`) and completes any pending wipe (D-03), then raises `SLOT_EN1..3`; LED rail dark until firmware is up; `SHORE_INHIBIT` low | every slot stays off until the panel controller raises its enable (pull-downs on board A); a slot with a flat heartbeat after 60 s is marked faulty, cycled once, then left off | HW power path, FW slot enable and supervision | transient | `PANEL.md` sections 3, 5, 6 and 10 | cold start from a pack below about -10 C at the cells is out of scope (D-02d); the fixes this cell used to name are in board A's schematic since `458b2873`: the device rail's enable is pulled up to board A's 3.3 V (`R42`, `gen_sch_a.py` line 887), the power controller's KILL input is pulled to 3.3 V (`R4`) and the 3.3 V buck's EN sits on a divider from the pack that reaches at most 4.7 V at 16.8 V (`R2` over `R184`, lines 260 and 261), the software enables are held off, and the charge inhibit released, by 4.7 k pull-downs until the firmware writes the expanders (lines 763, 1009, 1112 and 1125), and the monitor and heater eFuses trip at about 17.6 to 19.0 V (143 k over 10 k, lines 1041 to 1064); the power-up calculation of every enable at requirement level is owed (CON-014 of the registry); rail sequencing, inrush and hot-plug bounds (rule PWR-002): **TBD**; a kit whose pack is in the gauge's shutdown starts only once an input has woken the gauge (Transport and Storage rows); the panel controller cannot know the lid's state at start-up (the reed lands on the sensor controller alone, `gen_sch_e.py` lines 524 to 542, and the sensor controller reaches a module only as a USB device on bank 3), so it raises all three slots at every start-up, and a kit started with its lid closed enters the reduced mode by the normal route once the bridge has read the lid (section 4c). **Changed 27 September 2026 after Review A (B2):** this cell had the panel controller raise `SLOT_EN2` and `SLOT_EN3` only when the lid was closed, which it cannot sense |
| Normal (full) | startup with three modules, lid open, C1's triggers clear (inside air under +50 C and every cell under +55 C, section 4c) | lid closed, C1 or C3 acting (to Reduced), a fault (to Degraded), EMCON, shutdown | three modules, monitor, every bearer available, sensors | none | SW | PS-IDLE 39.7 W to PS-TYP 63.0 W; PS-BUSY a bounded mode (its sustained bound 92.0 W, ended by C1 at every conductance in the record); PS-ALLTX bursts inside the bounds of D-11 (section 5) | `OPERATING-ENVELOPE.md` section 4; `feasibility/POWER-THERMAL.md` sections 4 and 7.1 | the planning duty profile is section 5's (session choice); D-11's key-down time and floors are the figures the session set (SC-10: every transmitter at once only above a pack rest voltage of 15.5 V, the PA alone above 12.4 V, each PA key-down at most 60 s, `feasibility/POWER-THERMAL.md` section 7.2), requirement REQ-018's pass lines since 27 September 2026 (the layer-3 closer's session choice on D-11's declared values); whether the design meets them is feasibility blocker FEA-004's (PWR-F12, PWR-F15), and if it closes in failure they reopen |
| Reduced | lid closed (the reed under the frame on board E's `J_TAMP`, read by the sensor controller, `gen_sch_e.py` lines 524 to 542), or C1 (inside air +50 C, or any cell +55 C on the gauge's thermistors), or C3 (with the outlets already off, a 10 s average pack current above 9.0 A for 30 s), or the operator; a kit started with its lid closed starts all three modules and enters it once the bridge has read the lid (section 4c) | lid open and every trigger clear (C1's 5 K below its trigger; C3's predicted current under 8.0 A for 60 s), or the operator | **slots 2 and 3** (section 4c): slot 2 hosts bank 2 (GNSS, both E72, the QMX receiving) and, by the fabric's failover, bank 1 (Iridium, the panel controller and with it the SOS path, the kit I2C devices); slot 3 hosts bank 3 (the APRS board D8, the sensor controller, the wall USB port, the 5G management link) and the LoRa module; the 5G module on slot 2's PCIe, registered and idle; APRS position beacons. That is board B as generated; after BANK-R1 (section 4c) the same two slots carry the same set, with Iridium on bank 2 (slot 2's own) and the panel controller on bank 3 (slot 3's own), and bank 1 (the SDR, the camera, the QMX, the wall port) failed over to slot 2 | slot 1; both WiFi link cards (card 1 hangs on slot 1, card 2 is held off by software); the monitor; the SDR and the camera; HF transmit | SW decides, FW switches: the bridge asks, the panel controller drops `SLOT_EN1`, and the three supervisors move bank 1 to slot 2 through the voted fabric (their 2-of-3 decision in firmware, the voting in hardware, `ARCH-PCB-B-IOHA.md` sections 4, 5 and 7). **Preconditions owed on board B, because this mode makes dropping `SLOT_EN1` routine** (Review A, m3): the break-before-make order, which the generated circuit does not have (FAB-03, CON-003); a bank detached from a host that has lost its power, which nothing does as generated (FAB-02, CON-022); and the supervisors' I2C status path, absent as generated (`ARCH-PCB-B-IOHA.md` section 6) | PS-RED2 31.4 W (17.6 to 55.6), PROVISIONAL (section 4a) | owner ruling D-02b; section 4c; `ARCH-PCB-B-IOHA.md` section 15; `feasibility/POWER-THERMAL.md` section 9.3 | the definition is the session's (section 7a), a departure from the owner's example in one respect, two modules where the example says one, because no single slot hosts the example's bearers and the SOS path as board B is generated; the owner's example on one module is the heat stage's required set (next row); the thermal proof is FEA-004's (`TEST-PLAN.md` E3-L and T-H1); the ambient at which C1 acts with the lid closed is a bound, +20.1 to +37.3 C on the independent bound and +28.9 to +34.2 C on 32.53's conductance (section 4c); `feasibility/POWER-THERMAL.md` still takes the reduced mode as slot 3 alone (its sections 1 and 9.3, C1's shed target) and is to follow this definition (a hand-off to its owner) |
| Heat stage | in the reduced mode, C1's triggers reached again | the inside-air reading this stage keeps (board B's TMP117 under the coolers, on the kit bus through the panel controller) 5 K under its value at entry; the reduced mode is then restored, at most once in any 30 minutes (a planning value), and sheds again at once if C1's triggers still hold. **Past it, the hot stop (next row):** with C1's triggers still set the kit stays here until the pack's measured cell temperature reaches the hot stop's first step (section 4c) | **one module carrying the owner's D-02b example (GNSS, the LoRa mesh, Iridium and APRS beacons) with the SOS path, the required set (REQ-052).** After BANK-R1 (section 4c): **slot 3 alone**, with bank 3 (APRS, the sensor controller and with it the pack's readings and the lid, water and gas sensors, the panel controller and the SOS path), bank 2 by failover (GNSS, both E72, Iridium) and the LoRa module. **As board B is generated: slot 2 alone**, with bank 1 by failover (Iridium, the panel controller, SOS), bank 2 (GNSS, both E72) and the 5G module's data and AT control over slot 2's PCIe (Quectel RM520N series hardware design v1.1 section 3.2: in its PCIe modes the module "Supports MBIM/QMI/QRTR/AT over PCIe interface"; `feasibility/EMCON.md` section 4.5; the AT control counted only once the bridge's PCIe AT channel is shown) | after BANK-R1: slots 1 and 2, so bank 1 (the SDR, the camera, the QMX, the wall port), the 5G module (its data is slot 2's), both WiFi link cards, the monitor. As generated: slots 1 and 3; bank 3 has no host (its home slot 3 and its failover slot 1 are both off): APRS, the sensor controller's USB link (the gauge's readings, the lid switch, the water and gas sensors reach no module; the sensor controller itself keeps running on board E's always-on domain), the wall USB port and **the 5G module's USB link** (bank 3, port 4: in the module's USB-AT-based PCIe mode its only firmware-update path, HD v1.1 section 3.2); the LoRa module; the monitor; and the outlets, held off because C2's cell input is lost | SW decides, FW switches; the pack gauge's own windows and board P's second level act whatever the kit can read (the second level destructively, above the cells' limit). On the cells' measured temperature the gauge's charge window acts first (a charge start refused above 42 C, a running charge ended above 43 C, OTC at 44 C; section 4c), and the hot stop (next row) is designed to act after it and before the gauge's discharge cut (OTD, 57.5 C), board P's second level, the gauge's SOT and the PTC; as generated the hot stop has no path in this stage, whose one module does not host bank 3, until HOT-R1 is in the generators of boards A and E (its requirement reads FAIL until then, next row) | after BANK-R1 PS-SURV-R 23.3 W (12.8 to 46.9); as generated PS-SURV 21.7 W (12.4 to 42.0); PROVISIONAL (section 4a) | owner ruling D-02b ("above +35 C ambient the kit runs one module"); section 4c; `ARCH-PCB-B-IOHA.md` section 15 | the stage and BANK-R1 are the session's (section 7a). **As board B is generated the stage does not carry its required set:** slot 2 has neither the LoRa mesh nor APRS, a finding against the generated board, reported to the owner, until BANK-R1 is in board B's generator (section 4c). **As generated, with the gauge's readings lost:** the bridge reads the pack's voltage and discharge current from the charger over the kit bus instead (the BQ25731's ADC, SLUSE66A 9.6.8 and 9.6.10, with its low power mode off), which gives C3 its input and the graceful shutdown a pack-voltage line (section 4c); C1's cell trigger, the cells' voltages and the state of charge are lost, the battery bar shows the pack voltage, and the e-paper says so; the water and gas responses of section 4e wait for a host of bank 3. The ambient at which C1 acts in this stage: after BANK-R1 +27.9 to +40.6 C lid closed and +30.8 to +41.8 C lid open on the independent bound (+34.4 to +38.3 C and +42.2 to +42.9 C on 32.53's conductance); as generated +29.4 to +41.2 C and +32.1 to +42.3 C (+35.4 to +39.1 C and +42.7 to +43.4 C) |
| Hot stop | on the pack's measured cell temperature, in any mode and on every input state: the hottest of the gauge's four cell thermistors at +56.5 C in two readings a second apart (H1, shed to the minimum load), then at +57.0 C with H1 acting (H2, the kit's controlled shutdown); read by the sensor controller and passed to the panel controller on HOT-R1 (section 4c); with the sensor controller lost, board B's TMP117 at +55.0 and +56.0 C | H1: the hottest cell at +46.5 C or less and at least 30 minutes after the stop, the panel controller then raising the heat stage's one module; H2: the operator's MAIN, after which no slot is raised until the cells read released | H1: the panel controller, board A's 3.3 V logic and expanders, the shared device rail that feeds the panel, board E's always-on domain with the mixer fans at full speed, the pack gauge, the e-paper page; H2: the pack gauge and board E's always-on domain | H1: every compute module (a clean shutdown on `PI_SHDN_REQ`, then `SLOT_EN1..3` dropped within 60 s), the monitor, the heater, board D, PoE, the USB-C outlet, the wall port's VBUS, the PA and HF rails, the charge (the charger's `CHRG_INHIBIT` bit, its converter still carrying the kit on an input), every bearer and SOS; H2: every converter on board A (`PI_KILL`, the LTC2954's `KILL`, `RAIL_EN`) | FW (the sensor controller detects, the panel controller acts) over one hardware line and hardware that keeps a released load off; behind it the gauge's OTD (firmware in the pack, recoverable) and the destructive backstops (board P's second level from 62.7 C, which blows F2; the gauge's SOT from 64.2 C; the PTC) | H1 PS-HOLD, not computed (the heat stage's loads less any module, **TBD**); H2 PS-OFF (0.2 to 1.7 W) | section 4c; `review-packets/battery/THERMAL-COORDINATION.md` sections 3, 4 and 8; `records/hc2/hotstop_bounds.out` | the stop and HOT-R1 are the session's (section 7a); **HOT-R1 is owed on boards A and E before their layout entry, and until it is in both generators the hot stop's requirement reads FAIL on the generated boards** (as generated the cells' temperature reaches the panel controller only through the bridge on a module that hosts bank 3, which the heat stage as generated does not have); the thresholds are PROVISIONAL (`TEST-PLAN.md` P14 and E3-H); whether it fires inside the envelope is FEA-004's, OPEN until T-H1 (at the independent bound's worst corner it acts from +33.2 to +38.6 C, section 4c); a non-destructive hardware stage is an open design question (section 4c) |
| Charging | shore, vehicle or solar present, the panel controller has configured the charger, and the pack gauge reports the cells inside their charge window | input gone, inhibit asserted, pack full | the BQ25731 (its cell-count strap at 4S since `458b2873`, `gen_sch_a.py` lines 764 to 771) regulates the charge into the 4S pack beyond its sense resistor `R17`, and the kit's loads sit on the charger's system node (VSYS, the net `VBAT`, lines 18 to 48), so shore carries the loads up to the charger's input limit and the pack supplies above it; board E's always-on domain (the sensor controller and the fans) sits on the pack side and shares the charge current | charge held off by the pack gauge outside 0 to +45 C at the cells (the over-temperature half acts on the charge FET only with the golden image's OTFET bit set, `review-packets/battery/CHARGER-STATE-SEQUENCE.md` section 3; the bridge clears its own hold above +3 C); once armed, board P's second level opens the chemical fuse at its fixed 70 C over-temperature, a backstop; the front end held off by `SHORE_INHIBIT`; the charger held off by `CHG_INHIBIT`; the heater mat warms the pack in the cold | pack gauge firmware (decision 40), with the second level of D-15 in hardware behind it; FW writes the charger (it has no thermistor input, a 175 s watchdog, and it never ends a charge by itself) | overlay: pack current reverses while the source covers the load | `PANEL.md` section 10; `review-packets/battery/CHARGER-STATE-SEQUENCE.md`; `pcb_pack_protection.yaml` CHARGE_TEMPERATURE_WINDOW; `OPERATING-ENVELOPE.md` sections 3 and 4; appendix 32.55 line 2915, 32.57 line 2984; BQ25731 datasheet SLUSE66A | without its host the charger's input limit is about 31 W at the 20 V bus, near the kit's idle load, and its charge current is 256 mA (SLUSE66A section 9.3.21.1: on a watchdog timeout "ChargeCurrent() resets to 256 mA"; TI's answer on its start-up value, E2E thread 1316778 of 23 January 2024, https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1316778/bq25731-bq25731-chargecurrent-start-up-behavior; whether it charges before any host write, bench confirmation owed), of which board E's always-on draw takes about half, so a hostless kit's pack is held rather than charged (`CHARGER-STATE-SEQUENCE.md` section 6); the 4 A charge setting is to be lowered for cell life on the ruled 4S3P pack (a session item under D-06); charge current and time: **TBD**. **Corrected 26 September 2026 (S-07):** this row said the kit's loads sat on the pack side of the charger's sense resistor and the strap selected 2S, the circuit before `458b2873` |
| Degraded | a module, supervisor, bearer or sensor lost, or a carve-out reached | cause removed | whatever survives | the lost item | HW (voted fabric), FW, SW | between PS-SURV and the state before the fault, not computed | `ARCH-PCB-B-IOHA.md` sections 7 and 12; `PANEL.md` section 5; section 4e | per-device recovery: **required** within 30 s of the home module's loss, plus the device's own start-up where its maker states a longer one, "back in service" being `ARCH-PCB-B-IOHA.md` section 7 step 12 (application access resumed) by a bridge instance already running on the adopting module; the bridge's own service **required** back on a surviving module within 60 s of the loss (section 4c, both session choices); the measured time on hardware must be at or under it (`ARCH-PCB-B-IOHA.md` section 7, "measured on hardware, not invented", which is the measurement, not the bound) |
| EMCON | `SW_EMCON` closed (locking toggle) | toggle opened | receive-only radios (GNSS, DCF77, lightning sensor), the VHF receiver, compute, display in its lighting mode | radios dark (owner ruling D-05), as section 4b: power removed from the SDR, the RockBLOCK, the LoRa module, both E72, the HF unit and the two WiFi link cards; the compute modules' own WiFi and Bluetooth disabled through open drains; the 5G module's supply removed by hardware with its disable pins pulled low at the same moment (since board B's round 8, section 4b); the PA rail and keying off; software holds every send, an SOS included | HW for the gated rails, the module radio disables and the VHF keying, and the RockBLOCK keeps running on its own stored energy with its ENABLE held by firmware until that ENABLE is forced low in hardware (`feasibility/EMCON.md` section 4.4); SW hold on top | PS-EMCON 47.1 W (37.3 to 80.6) as generated since `458b2873`, PROVISIONAL (section 4a) | `PANEL.md` sections 6 and 9; `feasibility/EMCON.md`; `gen_sch_b.py` lines 478, 716 to 741, 974 to 977 and 1029, `gen_sch_a.py` line 1102, `gen_sch_d.py` lines 532 to 534, at `45bde541` | session work owed under D-05 (S-01): the RockBLOCK's ENABLE forced low by the EMCON hardware with its stored energy bounded (EMCON.md section 4.4), the SA868's PTT threshold (bench E-01), the line's shared items left open after board B's round 8 (the gate supplies of `U501` to `U505`, `feasibility/EMCON.md` sections 4b and 7) and the back-feed paths into the RockBLOCK, the E22 and the E72 (SD-EMC-2); the hardware EMCON lamp's plate light guide (SD-EMC-6; the lamp is drawn on board C since its round 8); the 5G module's staged supply removal (SD-EMC-1) is drawn since board B's round 8 (SD-EMC-1r8); twelve bench tests, none of them with the kit's own SDR (EMCON.md section 6). **Corrected 26 September 2026 (S-07):** this row said the module radios were off the line and the WiFi cards had only their disable pin, the circuit before `458b2873` |
| Blackout | LIGHTING toggle at BLACKOUT | toggle moved | everything else as before | LED rail opened in hardware, monitor backlight and touch UI dark, speaker and sounder muted, TX lamp dark | HW for the LED rail; FW and SW for the monitor and sound | overlay: removes most of the monitor share, TBD | `PANEL.md` section 8; `V2-SPEC.md` line 60 | none |
| NVG | LIGHTING at NIGHT plus the bridge's NVG mode | either removed | panel at 2 % duty, backlight 5 %, red and amber indicators only | green and white indicators | FW and SW | overlay: monitor power at 5 % backlight TBD | `PANEL.md` section 8 | the compatibility target is MIL-STD-3009's lighting system NVIS compatible examination (5.7.2) for a Type I, Class B NVIS, applied to the panel, its light guides and the monitor at their NVG levels (the requirements registry's REQ-034, a session choice, section 7a; Class B because the standard makes Class A incompatible with red lights, and the ruled NVG light is red); no night-vision compatibility is claimed until that examination has passed on the built prototype (the claim deferred under D-01) |
| SOS | `SW_SOS` closed 2 s (covered locking toggle) | toggle returned (cancels; the e-paper confirms both) | MASTER WARN flashes; sounder 1 s on, 1 s off (muted in blackout); the e-paper confirms; a distress message with the kit's position goes over the available bearers, Iridium first when nothing else is up, to a configured recipient list (owner ruling D-10) | never transmitted through EMCON: while EMCON is closed the message is queued and the operator is told (D-10) | FW (the panel controller reads the switch) and SW (the message); firmware only, no board change | transient transmit, not computed | `PANEL.md` sections 1, 3 and 9; `V2-SPEC.md` line 58; owner ruling D-10 | the recipient list and the message format are the session's; in prototype 1's core (section 2a) |
| ZEROIZE | `SW_ZERO` held closed 5 s (covered locking toggle), the only trigger (owner ruling D-03: the case-open or lid switch logs only; a remote wipe is deferred) | switch returned; the kit re-arms only when the toggle returns | MASTER WARN flashes while armed; flipping back inside 5 s aborts; then a crypto-erase through the secure element: every drive and eMMC key is wrapped by keys only the secure element holds (two, both needed, `feasibility/ZEROIZE.md` section 3), ZEROIZE destroys them, then the running modules drop their keys from RAM, then the slots are cut; continuous 3 s sounder when complete; e-paper full refresh | the wrapping keys, which leaves every drive unreadable, a powered-off module's included | FW and provisioning: the covered toggle pulls a net local to board C that only the panel controller reads (`ZEROIZE_SW`, GPIO22), and the buffer `U12` copies it onto `ZEROIZE_HW`, which runs over the ribbons to a 10 k pull-up on board A (`R117`) and to test pads on boards B and D where no part listens (`gen_sch_c.py` lines 168 to 178 and 217, `gen_sch_a.py` line 1150, at `45bde541`; the buffer is the one board change, `faf8c981`), and the panel controller is also the kit I2C master that reaches the secure element; level-sensitive after a power loss: the toggle is read at boot before any slot powers and a wipe-pending record resumes the wipe | transient | `PANEL.md` sections 6 and 9; decision 30; owner ruling D-03 | precondition: the fitted ATECC608B must let the wrapping keys be destroyed after its zones are locked; `feasibility/ZEROIZE.md` closes that at desk from Microchip's public documents (the full datasheet stays under NDA) and leaves the physical demonstration to bench experiments Z-EXP-A and Z-EXP-B (S-35), with the SLB 9673 TPM 2.0 on board B's `U8` site the fallback (a TPM 2.0 is what 32.50 item 5 already names): **TBD** until the bench; accepted residual risk (D-03): a drive unlocks at boot only through the secure element, the panel controller and the kit I2C bus |
| Shutdown | PI button short press (clean shutdown of every module) or held 8 s (hard kill); MAIN PWR; on the pack, the graceful threshold of section 4c | startup | e-paper keeps identity and status with the power off | modules, radios | FW request, HW kill | PS-OFF after | `PANEL.md` section 5; `V2-SPEC.md` line 57 | **graceful shutdown on the pack** (section 4c, PROVISIONAL, a session choice): the bridge starts a clean shutdown when the gauge's relative state of charge reaches 5 % (the reserve section 6's runtimes keep) or the lowest cell reads 3.00 V or less under load for 10 s, whichever comes first, and writes the e-paper's power-off page; in the heat stage as board B is generated, where the gauge's readings reach no module, it starts it when the pack voltage the charger reads falls to 12.8 V or less under load for 10 s (section 4c); behind it the gauge opens the discharge FET at 2.5 V per cell (`TEST-PLAN.md` section 5, row 2), in its firmware, and since `faf8c981` board P's second level holds the discharge FET off in hardware below 2.25 V per cell (the first branch of owner ruling D-15, `gen_sch_p.py` lines 414 and 502); if the proposed over-current backstop (OCD1 at 11 A for 90 s, `feasibility/POWER-THERMAL.md` section 9.3) trips on the pack, the kit goes dark until an input returns, taken as the safe state (section 4e) |
| Storage | closed and latched, **pack fitted**, brought to the cells' ex-factory state (3.49 to 3.69 V per cell, about 30 % of charge: Samsung INR18650-35E Ver. 1.1 7.11 and 3.13 note 1, the charge its storage ratings are stated at), then, with every input unplugged, the pack put in the gauge's shutdown as in Transport | an input applied, then charge and deploy | nothing | everything | the pack's hardware protection, as in Transport | PS-SHUT | `OPERATING-ENVELOPE.md` section 4; the cell specification 3.13, 7.11 and handling notes 1.1 and 11.1; session choice of 27 September 2026 (section 7a) | the storage envelope is the cells': -20 to +45 C for three months, -20 to +25 C for a year, and at most a month up to +60 C; dry, and preferably below +20 C (the maker's handling note 1.1); never where the temperature may exceed +60 C. The LimeSDR Mini's own storage range is 0 to +70 C (section 4c, an exception recorded, not a lowered envelope). Storage humidity has no number in any held source: non-condensing and dry (TBD as a figure). D-02a's storage margins (+71 C, -33 C) are beyond the cells' ratings, so they run on the kit less its pack and on the pack at its cells' own limits, and the stored product's result is recorded as finding BAT-F19 (`TEST-PLAN.md` section 6). **Changed 27 September 2026:** this row had the pack out; the pack is bonded under the stack (`ASSEMBLY.md` section 1) and comes out only by the service lift of D-14, so storage keeps it fitted (section 7a). As in Transport, the lid and tamper log does not run in storage and the kit starts only once an input has woken the gauge (Review A, m5) |
| Service | face plate off (ten 6-32 screws, case choice C1 of `CASE-MARGINS.md` section 4), rod stack lifted off the blind-mate joint, pack out of its cradle | reassembly | console and key fill over the sealed Glenair 233-370 USB receptacle (owner ruling D-12), `rpiboot` per module, SWD on the controllers | as the task needs | procedure (owner ruling D-14): before the lift the kit is off, the pack's XT60 unplugged and shore removed, and an insulating cap covers the dock block E5 while the stack is out | bench supply | `V2-SPEC.md` line 13; 32.50 items 2 and 16f; `ARCH-PCB-B-IOHA.md` section 2; `ASSEMBLY.md` sections 4 and 7 | since `458b2873` the wall data path (bank 3's hub, port 3) leaves board A at `J_USBW` for the 233-370 with its own VBUS eFuse, and the USB-C outlet carries VBUS, CC1 and CC2 only (`gen_sch_a.py` lines 1012 to 1015 and 1151 to 1167); lifting the stack live is an accepted, recorded residual risk (D-14), and a hardware stack-present interlock is studied at Review D; test access list per board: **TBD** (foundation baseline, before placement); the first power-up of a built or rebuilt kit is the Commissioning row and section 4d |
| Commissioning | a newly built or rebuilt kit, or a replaced pack, secure element or panel controller | every step of section 4d recorded | the steps of section 4d, in order, on shore with the pack's arming jumper open until its step | slots until the secure element is provisioned and its zones locked | procedure; the record is the commissioning log (`ASSEMBLY.md` section 8) | bench supply, then shore | section 4d; `ASSEMBLY.md` section 8; `feasibility/ZEROIZE.md` section 3; `review-packets/battery/PROTECTION-ARCHITECTURE.md` (O-9) | added 27 September 2026 (the audit found no scenario for it while D-03, D-12 and D-15 depend on it) |

### 4a. Power states

The operating modes above are states of use. The power budget needs a smaller set of power states, and each
operating mode maps to one of them (or to an overlay that changes a share of one). The identifiers are
PS-... so that they never collide with the missions M1 to M5.

All figures are **PROVISIONAL**: arithmetic over datasheet figures, generator declarations and stated duty
assumptions, and nothing has been measured. **Since 27 September 2026 they are `feasibility/POWER-THERMAL.md`'s**
(sections 4 and 6, finding PWR-F07), computed by `records/rv-pwr/pwr_budget.py`; the reduced mode, the heat stage and
EMCON as generated since `458b2873`, which that model does not carry as states, are computed by
`records/hc2/pwr_red2.py`, which imports it unchanged. The figures this table carried until then were the W2 model's
of 25 September 2026 (`records/w2/w2-runtime.md` and `w2-power.md`), which the current model supersedes: PS-IDLE-SPEC
moved from 32.4 to 42.8 W and PS-TYP from 60.1 to 63.0 W. Battery W is at the pack terminals and includes each
converter's loss read off its own datasheet and the distribution loss (22.5 mOhm, the chemical fuse F2 at its
maximum included); PLAN is the headline and LOW to HIGH the documented bounds (HIGH puts every load at its maximum at
once, an upper bound, not a scenario). Runtime is usable energy over battery W, with the Samsung INR18650-35E at its
specification minimum of 3.35 Ah, the rate factor of its section 7.8, the voltage sag, and a 5 % reserve for the
graceful shutdown (section 4c); +20 C takes no temperature derating (the cell's standard condition is 23 +- 3 C).
**"Aged" is 80 % of the specification minimum capacity** (section 6, a session choice); the 60 % column is the cell
sheet's own stated minimum after 500 cycles (7.9), kept as the lower bracket. The loads with no document at all now carry
8.4 of PS-IDLE-SPEC's 42.8 W and 11.7 of PS-TYP's 63.0 W, and a further 11.3 and 21.0 W sit inside a maker's bound at an
assumed duty (`feasibility/POWER-THERMAL.md` section 4); those shares move every hour below.

| Power state | Definition | Battery W, PLAN (LOW to HIGH) | 4S3P, the ruled pack, +20 C: new / aged 80 % / aged 60 %, h |
|---|---|---|---|
| PS-SHUT | the pack in the gauge's shutdown (Storage, Transport): both FETs open, no kit load | none from the kit; the cells carry only the gauge's shutdown current, the second level's own supply current and their self-discharge (**TBD** from the sheets) | not a runtime state |
| PS-OFF | pack connected, MAIN off: board E's always-on domain (0.2 to 1.7 W, its firmware's sleep state **TBD**) and the gauge's 336 uA | 0.2 to 1.7 | 3.4 to 27.9 days / 2.7 to 22.4 days / not computed |
| PS-IDLE | three modules idle, monitor dimmed, radios receiving, SDR off, no transmit | 39.7 (30.9 to 81.7) | 3.4 / 2.7 / 2.0 |
| PS-IDLE-SPEC | PS-IDLE as `V2-SPEC.md` line 23 words it: monitor on, APRS beacons; the idle state of the D-06 runtime requirement, with the kit-to-kit link card up and idle (the conservative reading of "radios idle") | 42.8 (33.1 to 82.8) | 3.2 / **2.5** / 1.9 |
| PS-TYP | three modules at typical operation, monitor on, radios receiving with light traffic, SDR on, HF receiving; the typical state of the D-06 runtime requirement | 63.0 (46.9 to 120.6) | 2.1 / **1.7** / 1.3 |
| PS-BUSY | three modules loaded, 5G and the WiFi link passing traffic, Iridium and LoRa sending, each at full duty: a **sustained bound**, not a duty estimate, and **a bounded mode, not a sustained one**: at +20 C it reaches C1's +55 C cell trigger on every conductance in the record, so C1 ends it (PWR-F13) | 92.0 (54.6 to 134.4) | 1.4 / 1.1 / 0.9 (energy only) |
| PS-RED2 | **the reduced mode** (section 4c): slots 2 and 3, monitor off, both WiFi link cards off, the 5G module registered and idle, APRS beacons | 31.4 (17.6 to 55.6) | 4.3 / 3.5 / 2.6 |
| PS-SURV-R | **the heat stage, after BANK-R1** (section 4c): slot 3 alone, monitor off, APRS beacons; `feasibility/POWER-THERMAL.md`'s PS-RED with the beacons added | 23.3 (12.8 to 46.9) | 5.9 / 4.7 / 3.5 |
| PS-SURV | **the heat stage as board B is generated** (section 4c): slot 2 alone, monitor off | 21.7 (12.4 to 42.0) | 6.3 / 5.0 / 3.8 |
| PS-RED | slot 3 alone, monitor off: the reduced state `feasibility/POWER-THERMAL.md` computes; as board B is generated it has no host for Iridium or the SOS path, and after BANK-R1 it is the heat stage less the APRS beacons (PS-SURV-R) | 22.2 (12.7 to 45.9) | 6.2 / 4.9 / 3.7 |
| PS-RED-b | three modules idle, monitor off: 32.53's cluster-idle reading of the reduced mode, kept for comparison | 35.7 (26.9 to 71.5) | 3.8 / 3.0 / 2.3 |
| PS-EMCON | EMCON as generated since `458b2873` (section 4b): PS-TYP with the gated radios dark and both WiFi link cards unpowered (all three runtimes printed by `records/hc2/pwr_red2.py`, the 60 % one since pass 2) | 47.1 (37.3 to 80.6) | 2.9 / 2.3 / 1.7 |
| PS-ALLTX | every transmitter keyed at once, monitor full, fans, outlets off, the standby WiFi card off, the other loads at typical: D-11 bounds it by a declared key-down time above a declared state of charge, with the outlets at their minimum contract, **0 W** (section 5) | 203.8 (168.9 to 272.0) | 0.61 / 0.49 / 0.36 (energy only) |
| PS-ALLTX-OUT | PS-ALLTX with the outlets on: excluded by D-11, whose hardware interlock drops the outlets while the PA keys (section 5); about 316 W on the W2 figures | excluded | excluded |

**What the table does not carry any more (27 September 2026).** The 4S4P columns: no 4S4P 18650 block has been shown
to fit either pocket with the pack board beside it (the pack paragraph below), so they described no configuration
the design carries, and the current model computes the ruled pack only. PS-EMCON-L (EMCON with the receivers kept
listening, 52.5 W on the W2 figures): the option D-05 did not take. The PS-EMCON of 25 September (47.6 W) was computed
for the circuit before `458b2873`; `feasibility/POWER-THERMAL.md`'s 53.1 W still carries both WiFi link cards (4.0 W
and 1.0 W, the circuit before `458b2873`), which is why this table's figure is lower.

**The pack (owner ruling D-06, 26 September 2026).** One 4S3P block of the held cell, the Samsung INR18650-35E, of
about 145 Wh (144.7 Wh at the cell's specification minimum), shrink-wrapped in the east pocket under board B,
ruled subject to the case measurement, which the owner withdrew on 26 September 2026 (D-08 reversed): the fit is
designed against the worst of Peli's own figures instead, and the margins that rest on unstated allowances stay OPEN
until the targeted mock-up, which runs before boards A and P enter layout because the pack's rows M4a and M5 can move
board A's east edge and board P's place (`CASE-MARGINS.md` section 7, `CASE-FIT-UNCERTAINTIES.md` section 2). Missions longer than the pack rely on vehicle or solar input. The
table's runtime columns describe the ruled pack. The 1.35 mm across the pocket that adjudication A06 of 25 September
2026 reported (its working files are not filed in this tree at `e3aedb25`; the records stream files them under
`v2/docs/records/`, and the finding is carried by `ASSEMBLY.md` section 3 and `CASE-MARGINS.md`) was taken against the X 178
of appendix 32.62, which is not a Peli surface: bounded by board A's edge and Peli's R 15.88 floor fillet, the
block keeps 1.85 mm to the fillet and 7.38 mm to the east wall at the worst of Peli's figures, and, centred in Y,
3.65 mm per side to the frame's setting legs, 1.77 at the worst (`CASE-MARGINS.md` M4a, M4b, M5, on the design
basis only; M4b MET, M4a and M5 OPEN on the pack's placement by hand); no rigid box fits, so `v2/cad/pack_4s.py` is
to be redesigned around the shrink-wrapped block (a session item under D-06). No 4S4P 18650 block (193 Wh) has been shown to fit
either pocket while the pack board stays beside the cells (INFERRED from the committed board B underside and the
pocket of appendix 32.62), which is why this table no longer carries 4S4P columns.
PS-ALLTX and PS-ALLTX-OUT are energy arithmetic only: the gauge's 20 A for 2 s limit and the 25 A blade bound
delivery first, especially at low charge, which is why D-11 bounds the all-transmit case.

**Mapping of the operating modes:** Transport and Storage map to PS-SHUT; Deploy to PS-SHUT or PS-OFF; Normal spans
PS-IDLE to PS-TYP, with PS-BUSY as a bounded mode and PS-ALLTX bursts inside the bounds of D-11; Reduced is PS-RED2
and the heat stage PS-SURV-R once board B carries BANK-R1 (PS-SURV as generated); EMCON is PS-EMCON; Charging, Blackout and NVG are overlays; Startup, Shutdown, SOS,
ZEROIZE and Commissioning are transients; Degraded is not computed; Service runs from a bench supply. The cold
overlay adds the pack heater, regulated to 12 V on board A since `458b2873` (7.5 W plus its buck's loss; the model
keeps the unregulated 10.8 W at 14.4 V, which overstates it): PS-TYP plus the heater is 73.9 W and the reduced mode
plus the heater about 42 W (INFERRED, PS-RED2 plus the model's 10.8 W). The cold warm-up of section 4c (the heater,
taken at the regulated mat's 8.5 W, and the three modules loaded, with the WiFi link cards and the SDR held off) is
71.1 W (`records/hc2/pwr_red2.out`), 1.5 h on an aged pack at +20 C and less in the cold. The cells' own capacity also falls in the cold:
the Samsung INR18650-35E specification (section 7.5, `v2/vendor/battery/samsung-35e-akkuzentrum.pdf`) gives 40 % at
-10 C against 97 % at 23 C when discharged at 3,400 mA, a factor of about 0.41. That factor holds at -10 C and that
current only: it is conservative at lower currents, and it says nothing below -10 C, where the cells' discharge
range ends (section 3.15: discharge -10 to 60 C ambient). A start from a pack below about -10 C at the cells is out
of scope for the prototype (owner ruling D-02d).

### 4b. What EMCON does to each radio, as generated

Read from the generators and the committed netlists of boards A, B, C and D at `45bde541`, which carry the circuit
corrections of `faf8c981` and `458b2873`; the transmitter-by-transmitter record, with each state, fault and proof
owed, is `feasibility/EMCON.md` section 4. "Asserted" means `SW_EMCON` closed: `TX_INHIBIT_n` goes low, `EMCON_HW`
follows it low through the buffer on board C, and board B inverts it once into `EMCON_ON` (high = asserted).
**Board B as generated in its round 8 (27 September 2026, MESHSAT-1357; `feasibility/EMCON.md` section 4b):** each
slot inverts `EMCON_HW` into its own `EMCON_ON1..3` from that module's own 3.3 V (`U112`, `U212`, `U312`), every stage
on it is an open-drain logic output (SN74LVC2G06) but `Q212`, the 5G socket rail's discharge FET, and the single gates `U501` to `U505` replace `U19` and `U20`; the
rows below that name `U19`, `U20`, `Q206`, `Q111`, `Q311`, `Q106`, `Q306` or `U{s}11` read with those parts.

| Radio | What the line drives | What EMCON removes | Receive under EMCON |
|---|---|---|---|
| LimeSDR Mini 2.4 | the enable of the eFuse that feeds its USB VBUS, its only supply: the hub's port power AND `EMCON_HW` AND the software enable (`U501`, `U502`, single gates since round 8) | power | lost |
| RockBLOCK 9704 | the enable of the eFuse that feeds its external supply pin, the only supply wired (`U503`) | power at that pin; the module's own two 10 F supercapacitors (about 16 J) keep it running after the gate opens, with its ENABLE driven only by the firmware expander `U6`, so its local chain is OPEN until ENABLE is forced low in hardware (`feasibility/EMCON.md` section 4.4) | lost once its own stored energy is spent (about 4.5 minutes idle, INFERRED, EMCON.md section 4.4) |
| E22-900M30S LoRa | the enable of the load switch that feeds its VCC pins (`U504`); its TXEN pin is driven by slot 3 and is not on the line | power | lost |
| Two E72 CC2652P (Zigbee, Thread) | the enable of the load switch that feeds both (`U505`) | power | lost |
| RM520N-GL 5G | since round 8: the enable of its 3.3 V buck, pulled low by `U215` from `EMCON_ON2`; its FULL_CARD_POWER_OFF# (`U220`) and W_DISABLE1# (`U215`) pulled low at the same moment; its socket rail discharged through 15 Ohm (`Q212`, `R295`) | power, with no firmware in the path: RF off within about 1.2 ms plus 1.8 ms per mF of the module's own input capacitance, which no held document states (`feasibility/EMCON.md` section 4b, SD-EMC-1r8); Quectel warns that cutting the supply of a working module can corrupt its flash, a residual accepted | lost |
| Two AW7915-AED WiFi link cards | the enable of each card's 3.3 V buck, pulled low by `U115` and `U315` from `EMCON_ON1` and `EMCON_ON3`, and each card's W_DISABLE1#, pulled low by the same parts | power (the disable pin is not counted: the maker's datasheet does not mention it and the mainline Linux driver has no code for it) | lost |
| SA868 VHF with the 30 W PA | the KEY gate on board D (`KEY = PTT_ANY AND TX_INHIBIT_n`) and the PA rail and keying on board A (`PA_EN = EMCON_HW AND PA_SW_EN`, `U26`; in board A's round 8 candidate `PA_EN = TX_INHIBIT_n AND EMCON_HW AND PA_SW_EN`, `U35` and `U36`, `feasibility/EMCON.md` section 4a); the exciter's supply is not gated and the resting relay joins antenna to exciter | transmit only | continues |
| QMX HF | the enable of the converter that feeds its DC input (`HF_EN = EMCON_HW AND HF_SW_EN`, `U26`, `gen_sch_a.py` line 1102 at `45bde541`; in board A's round 8 candidate `HF_EN = TX_INHIBIT_n AND EMCON_HW AND HF_SW_EN`, `U37` and `U38`, `gen_sch_a.py` lines 1240 to 1243); its USB supply is not gated | power (its receiver runs from the DC input per its manual) | lost |
| The three compute modules' own WiFi and Bluetooth | each module's WL_nDisable and BT_nDisable, only ever pulled low, by open-drain outputs run from the module's own 3.3 V: `U{s}13` from `EMCON_ON{s}` and `U{s}14` from the software request (round 8) | RF (the module's radio disabled in hardware, Compute Module 5 datasheet sections 2.1.1 and 2.1.2) | lost |
| LG290P GNSS, DCF77, lightning sensor | nothing | receive-only; nothing to remove | continues |

**Owner ruling D-05 (26 September 2026): EMCON means radios dark, as generated and completed.** Every radio with an
emission path is powered off or RF-disabled in hardware; the VHF path keeps listening because its gate is on the
transmit side only; GNSS, DCF77 and the lightning sensor continue. Read transmitter by transmitter
(`feasibility/EMCON.md` section 0a, sixth revision), the radio's own chain meets that meaning at desk for 15 of the 17
transmitters. The 5G module's is among them since board B's round 8 (27 September 2026): its only EMCON path had been
its disable pin, and its supply is now removed by hardware at once with a bounded time to RF off (EMCON.md section 4b,
SD-EMC-1r8). Two stay open: the SA868, whose PTT pin's receive threshold its maker does not publish (bench E-01), and
the RockBLOCK 9704, whose own supercapacitors keep the module running after its supply gate opens, with its ENABLE held
by firmware (EMCON.md section 4.4). What every row
shares was open as well (EMCON.md section 7: the line's hold with its source gone, a loss of board B's `+3V3_DEV`
that released every gate hung on `EMCON_ON` or on `U{s}11`, gate supplies outside their range, the drive of the
2N7002s, and the back-feed paths of SD-EMC-2); on board B round 8 closes the hold, the `+3V3_DEV` loss and the drive at
desk, and the 5G module's back-feed, and leaves open the gate supplies of `U501` to `U505` and the back-feed into the
RockBLOCK, the E22 and the E72 (EMCON.md section 4b); end to end, from the toggle to silence at the antenna port within
the latency of REQ-071, no row is closed; and no row has been shown on a bench (EMCON.md section 6, twelve tests, none
of which can use the kit's own SDR, whose supply EMCON removes).
The 5G module's own GNSS receiver is not counted in the last row: the kit's position source is the LG290P, the module's GNSS ports (L5 on ANT1, L1 on ANT3, Quectel hardware design v1.1
Table 32) are fitted only in part under D-07, and whether W_DISABLE1# stops it is not established.

The design record listed both switches under EMCON (appendix 32.55, line 2930: a supply switch for the 5G module and
a converter enable for the WiFi card). The WiFi cards' converter enables are drawn since `458b2873`; the 5G supply
switch, SD-EMC-1's, is drawn since board B's round 8 (SD-EMC-1r8, EMCON.md section 4b). **Corrected 26 September 2026 (S-07):** this section described the circuit before
`458b2873`, in which the compute modules' radios were driven only by a software I/O expander and the WiFi link cards
had only their disable pin.

### 4b.1 How fast EMCON must act, and in which faults (added 27 September 2026)

The table above says what each gate removes; `feasibility/EMCON.md` section 5a (SD-EMC-7, the session's, under the
owner's standing rule) sets how fast and in which faults. From the instant the EMCON toggle's contact closes
(`TX_INHIBIT_n` below 0.8 V at board C's TP10) to the instant a transmitter's conducted output at its antenna port
falls below the pass line of `feasibility/EMCON.md` section 6, the time is at most that row's **L_max**, and the output
stays below the line for as long as EMCON is asserted, by a path in which every element that bounds the time is
hardware:

| Rows | L_max |
|---|---|
| SA868, the 30 W PA, the QMX, the RockBLOCK 9704, both WiFi link cards, the compute modules' own WiFi and Bluetooth, the E22 LoRa module, both E72, the LimeSDR | 1 s |
| RM520N-GL 5G | **20 s** for a module that has been turned on, set by hardware timers at their worst tolerance (SD-EMC-1's staged supply removal, owed on board B); **0** at power-up under EMCON (its rail never rises); its W_DISABLE1# pulled within 1 s, which is firmware-mediated and not counted |

**The fault conditions it must hold in** (EMCON.md section 5a, F1 to F9): every processor that can reach the row held
in reset; each of them unpowered; each running a wrong image; the radio's own firmware booting, hung or configured
otherwise; the panel ribbon, `J_AB1` or `J_MEZZ1` unplugged; a logic rail lost or in its unspecified band; back-feed
from every live signal; every store of energy on the radio's side of its gate full; and EMCON asserted at power-up,
during a transmission, during a boot or restart, and through the contact's bounce. **Excluded:** a fault of the one
element every row shares (the toggle's contact, the `TX_INHIBIT_n` conductor), which the hardware EMCON lamp shows
without firmware once it is drawn on board C (CON-021, S-44).

**What the operator does with it.** A posture that needs every radio silent within 1 s closes EMCON at least 20 s
before silence is needed while the 5G module is running, or has the 5G module turned off first (INFERRED from the 5G
row's L_max). After setting EMCON the operator confirms the EMCON lamp before relying on it, and sets EMCON and
confirms the lamp before selecting BLACKOUT, in which the lamp is dark by choice (`feasibility/EMCON.md` section 5,
SD-EMC-6, the procedure lines it owes); until the lamp is drawn no indicator shows the line's state without the panel
controller. **State at `e3aedb25`:** this is a requirement on the design, and no row meets it at desk yet
(`feasibility/EMCON.md` sections 0a and 5a: rows 1, 4 and 5 are open locally and every row inherits the shared items of
its section 3); the registry text for REQ-030 is drafted in its section 8. NEED-08 is not met until the design closes
it and the bench tests of `feasibility/EMCON.md` section 6 pass.

### 4c. The reduced mode, the heat stage, the hot and cold ends, and the targets (27 September 2026)

Every choice in this section was taken by the session under the owner's standing rule of 26 September 2026 and is
listed in section 7a with its reason and how to reverse it. The figures are PROVISIONAL (section 4a).

**Which modules can host what, as board B is generated** (`ARCH-PCB-B-IOHA.md` sections 4 and 15, `gen_sch_b.py` line
543). Bank 1 (the LimeSDR, the panel controller and with it the SOS path and the kit I2C devices, the camera, the
RockBLOCK) is hosted by slot 1 or, failed over, slot 2. Bank 2 (the GNSS, both E72, the QMX) by slot 2 or slot 3. Bank
3 (the APRS board D8, the sensor controller and with it the pack gauge's readings, the lid switch and the water and gas
sensors, the sealed wall USB port, the 5G management link) by slot 3 or slot 1. The LoRa module is on slot 3's SPI
only, the 5G module's data on slot 2's PCIe only, WiFi link card 1 on slot 1 and card 2 on slot 3. So **no single
slot hosts the owner's D-02b example** (GNSS, the LoRa mesh, Iridium and APRS beacons) together with the SOS path:
slot 3 alone has LoRa, APRS and GNSS but neither Iridium nor the panel; slot 1 alone has Iridium, the panel and APRS
but neither LoRa nor GNSS; slot 2 alone has Iridium, the panel, GNSS and 5G but neither LoRa nor APRS.
`feasibility/POWER-THERMAL.md` (sections 1 and 9.3) and `ARCHITECTURE.md` took the reduced mode as slot 3 alone, which
leaves Iridium and SOS, a core function (section 2a), with no host as board B is generated. The ring of the fabric
cannot change that; the hub port each device hangs on can, which is BANK-R1 below.

**The reduced mode: slots 2 and 3.** Slot 2 hosts bank 2 and, by the fabric's failover, bank 1; slot 3 hosts bank 3 and
the LoRa module. It carries every bearer of the owner's example, the SOS path, and 5G (the fourth core bearer),
with the monitor off, the display switch off, both WiFi link cards unpowered, the SDR and the camera off and the 5G
module registered and idle. Two modules where the example says one is the one departure from it, stated here; the
other two-slot pair that hosts the example (slots 1 and 3) leaves 5G data without a host. BANK-R1 (below) lets one
module carry the example, and it is taken for the heat stage, where one module is what the owner accepted; the reduced
mode keeps its two modules after BANK-R1 as well, so that 5G stays (reversal in section 7a). **Entered** by the lid
closing (the reed on board E's `J_TAMP`, read by the sensor controller), by C1 or C3 below, or by the operator; a kit
started with its lid closed enters it once the bridge has read the lid (the start-up paragraph below).
**Left** when the lid is open and every trigger is clear. **How:** the bridge asks the panel controller to drop
`SLOT_EN1`; the supervisors see slot 1's heartbeat stop and move bank 1 to slot 2 through the voted fabric, the
sequence of `ARCH-PCB-B-IOHA.md` section 7 that its acceptance test A1 exercises ("drop `SLOT_EN` for one slot"); k3s
moves slot 1's workload. Dropping `SLOT_EN1` as a routine act rests on three board B items owed as generated (Review
A, m3): the break-before-make order (FAB-03, CON-003), a bank detached from a host that has lost its power (FAB-02,
CON-022), and the supervisors' I2C status path (`ARCH-PCB-B-IOHA.md` section 6); they are preconditions of this mode
on the hardware, not of its definition. The remaining redundancy is the ring's: as generated, a further loss of slot 2
moves bank 2 to slot 3 and leaves bank 1 (Iridium, SOS) with no host; a further loss of slot 3 moves bank 3 nowhere
(its failover slot 1 is off) unless the panel powers slot 1 again, which it does on that loss (the panel controller
reads every slot's heartbeat itself; the reduced mode gives way to the degraded one; a panel firmware contract item).
After BANK-R1 a further loss of slot 2 leaves bank 1 (the SDR, the camera, the QMX, the wall port) with no host and
keeps Iridium (bank 2 moves to slot 3) and SOS; a further loss of slot 3 is met the same way, slot 1 powered again and
bank 3, with the panel and SOS, moved to it. **Power:** PS-RED2, 31.4 W (17.6 to 55.6); aged runtime 3.5 h at +20 C.

**A start-up with the lid closed (answering Review A, B2).** The lid reed lands on the sensor controller alone
(`gen_sch_e.py` lines 524 to 542: "it never reaches ZEROIZE, the panel or any supervisor"), and the sensor controller
reaches a module only as a USB device on bank 3, so before any module runs the panel controller has no lid state to
act on. **Taken:** the panel controller raises all three slots at every start-up, as with the lid open; once the bridge
has read the lid from the sensor controller (on bank 3's host, slot 3, or slot 1 if slot 3 has not come up) and finds
it closed, the kit enters the reduced mode by the route above. Nothing new is asked of the supervisors (no
never-powered slot to treat as lost) or of the panel. The cost is three modules for the start-up's length before the
shed (**TBD**, the bridge's boot): under 1 K of inside air for two minutes even at PS-BUSY's 92.0 W over PS-RED2
(7.3 kJ into appendix 32.53's 8 to 10 kJ/K of thermal mass, INFERRED), and C1 acts on it in any case. If bank 3 has
no host after start-up the lid is not read, and the kit stays in the normal mode under C1 and C3. Reverse by a lid line
from the sensor controller to the panel controller (a layer-5 interface item on boards E and C), so that a start with
the lid closed never powers slot 1.

**The heat stage: one module carrying the owner's example with the SOS path.** Entered when C1's triggers are reached
again in the reduced mode. It is the owner's accepted consequence of D-02b ("above +35 C ambient the kit runs one
module"), reached on measured temperatures instead of an ambient reading, and its one module is required to carry the
owner's example (GNSS, the LoRa mesh, Iridium and APRS beacons) with the SOS path: that is REQ-052 at the envelope's hot
edge with the lid closed, kept at the owner's set and not restated to what the generated board does (Review A, B5).
**After BANK-R1 the stage is slot 3 alone:** bank 3 on its home slot (the APRS board D8; the sensor controller with the
pack's readings and the lid, water and gas sensors; the panel controller with the SOS path), bank 2 by failover (GNSS,
both E72, Iridium) and the LoRa module on slot 3's SPI. It loses 5G (its data is slot 2's PCIe lane), both WiFi link
cards, bank 1 (the SDR, the camera, the QMX, the wall port) and the monitor. **Power:** PS-SURV-R, 23.3 W (12.8 to 46.9).

**As board B is generated no module carries that set, and the stage runs slot 2 alone,** the only single slot that
keeps the SOS path with a live GNSS position (slot 3 alone has neither Iridium nor the panel; slot 1 alone has no GNSS
and would first have to boot a module the reduced mode had off, in the heat). What slot 2 alone loses, stated in full
(Review A, B1): **the LoRa mesh and APRS,** two bearers of the owner's example, so on the generated board the stage does
not meet its required set (the finding under BANK-R1 below); and **bank 3's whole USB side,** whose two hosts are both
off: the sensor controller's link (the gauge's readings, meaning the state of charge, the cells' voltages and their
temperatures, and the lid, water and gas sensors), the sealed wall USB port, and **the 5G module's USB link**, which in
the module's USB-AT-based PCIe mode is its only firmware-update path (Quectel RM520N series hardware design v1.1,
section 3.2). **What slot 2 alone keeps of 5G:** its data and its AT control, both over slot 2's PCIe lane: in its PCIe
modes the module "Supports MBIM/QMI/QRTR/AT over PCIe interface" (the same section, which `feasibility/EMCON.md` section
4.5 reads the same way), so the host sequence SD-EMC-1 relies on (AT+CFUN=0 and its OK over PCIe, then PERST# and the
panel controller's `5G_OFF` and `5G_RESET` over the kit bus) stays reachable; that the bridge's driver exposes the
AT channel over PCIe is a software item, and until it is shown the stage counts 5G as data only. **What the kit reads
in place of the gauge:** the pack's voltage (the BQ25731's ADCVBAT, 64 mV steps for 1S to 4S) and its discharge
current through `R17` (ADCIDCHG, 512 mA steps with the 5 mOhm shunt), read from the charger over the kit bus through
the panel controller (TI SLUSE66A 9.6.8 and 9.6.10; the charger is at 0x6B on the kit bus, `gen_sch_a.py` line 708),
with the charger's low power mode, on at its reset, turned off on the pack so that its ADC runs (SLUSE66A Table
9-8, ChargeOption0 EN_LWPWR: "ADC is not available in Low Power Mode"; a panel firmware contract item). That gives C3 its current input and the graceful shutdown a
pack-voltage line (below). C1's cell trigger, the cells' voltages and the state of charge are lost, and C2's cell
input with them, so the outlets are held off in this stage; the battery bar shows the pack voltage instead of the
charge, and the e-paper says so; the water and gas responses of section 4e wait for a host of bank 3. **Power:**
PS-SURV, 21.7 W (12.4 to 42.0).

In both configurations the pack's own protection does not depend on what the kit reads: the gauge's charge and
discharge windows (0 to 45 C and -10 to 60 C at the cell surface, `v2/ecad/tools/pcb_pack_protection.yaml`; round 8
sets OTC at 44.0 C and OTD at 57.5 C inside them, SC-12, on main since `53a98a71`) and board P's second level act
whatever the modules see, and the sensor controller keeps running on board E's always-on domain. Past this stage is
the hot stop.

**The hot stop, past the heat stage (taken by the session on 27 September 2026 under the owner's standing rule of 26
September 2026, section 7a, answering Review A's second pass, P2-B2, and Review B of layer 3, B1; it replaces this
section's earlier "there is no stage after this one").** The heat stage's worst inside air in use at +40 C is above
C1's +50 C at the independent bound's lowest conductance, +60.6 C lid closed as generated and +62.1 C after BANK-R1
(`OPERATING-ENVELOPE.md` section 3), so C1's triggers can stay set. On an input (shore, vehicle or solar) the pack
carries no current and its cells sit at about the inside air (INFERRED: the model's cell rise over the air is the
pack's own I2R, zero at no current), which there is above the cell maker's +60 C ("Don't leave, charge or use the
battery in a car or similar place where inside of temperature may be over 60°C", Samsung INR18650-35E Ver. 1.1).
Nothing earlier removes that heat: the gauge's charge hold and its discharge cut open the pack's FETs, which carry no
current on an input, and C1 has nothing left to shed, so without a further step the first actions would be the
destructive backstops below. The kit therefore acts on the pack's own measured cell temperature, in every mode and on
every input state, in two steps:

| Step | Acts when (the hottest of the four cell thermistors TS1 to TS4, as the pack gauge reads them) | Does | Released |
|---|---|---|---|
| H1, shed to the minimum load | +56.5 C in two readings in a row (the sensor controller reads the gauge once a second), in any mode | the panel controller asks every running module for a clean shutdown (`PI_SHDN_REQ`) and drops `SLOT_EN1..3` once each has stopped or 60 s have passed; through board A's expanders on the kit bus it turns off the monitor, the pack heater, board D, PoE, the USB-C outlet, the wall port's VBUS and the PA and HF software holds; it holds the charge by the charger's own charge-inhibit bit (below); it keeps the shared device rail, which feeds the panel controller itself; the sensor controller runs the mixer fans at full speed; MASTER WARN and the e-paper "HOT STOP: COOLING" with the hottest cell reading | the hottest cell at +46.5 C or less (10 K under H1) and at least 30 minutes after the stop: the panel controller raises the heat stage's one module, and the normal controls take over from there |
| H2, the kit's controlled shutdown | +57.0 C in two readings in a row, with H1 already acting (the kit's own heat is then at its minimum, so the rise is the ambient's) | the panel controller writes the e-paper "HOT SHUTDOWN: RESTART WITH MAIN WHEN COOL", then pulls `PI_KILL`: board A's `Q1` takes the LTC2954's `KILL` low, `RAIL_EN` falls and every converter on board A stops, the panel controller's own supply with them; what stays on is the pack gauge and board E's always-on domain (PS-OFF, 0.2 to 1.7 W) | only by the operator's MAIN press; the panel controller then raises no slot until the cells read released (the path below) |

**Where the thresholds come from (INFERRED arithmetic, `records/hc2/hotstop_bounds.out`; PROVISIONAL).** The hot stop
reads the same four thermistors through the same gauge as the gauge's own discharge cut (OTD, 57.5 C, SC-12), so the
battery packet's error budget applies to it unchanged: the published terms of the gauge's reading sum to 2.07 K on
the hot side (`review-packets/battery/THERMAL-COORDINATION.md` section 3: thermistor interchangeability 0.71 K,
pull-up drift 0.40 K, sensor lag 0.80 K, detection 0.16 K). A cell is then at most 58.57 C when H1 acts and 59.07 C
when H2 acts, 1.43 K and 0.93 K inside the cells' +60 C, which is what is left for the budget's two TBD terms (the
gauge's own ADC and fit, and the sensed cell to the hottest cell, both read on the bench in `TEST-PLAN.md` P14); the
stop's own detection is at most 1.2 s slower than the gauge's (one reading older, and the line to the panel
controller), 0.06 K at the budget's 3.2 K per minute. In the reading itself the order is fixed whatever the sensor's
error: C1's cell trigger at 55.0 C, H1 at 56.5 C, H2 at 57.0 C, OTD at 57.5 C, 1.5, 0.5 and 0.5 K apart, so on the
pack the kit sheds and shuts down before the pack drops out. When P14 lowers OTD (the packet's rule: by whatever the
measured terms need beyond the 0.4 K OTD keeps in hand), H1, H2 and C1's cell trigger come down with it and keep their
spacing. The charge is held in both steps by the pack gauge's own window, which at these readings already refuses a
charge start above 42 C and ends a running charge above 43 C (T3, T4 and OTC, the packet's section 4); in H1 the panel
controller also sets the charger's `CHRG_INHIBIT` bit (ChargeOption0 bit 0, TI SLUSE66A 9.4.1 and 9.6.1), which ends a
charge while the charger's converter keeps carrying the kit from the input. It does not use board A's `CHG_INHIBIT`
line: that line puts the charger in HIZ, whose converter shuts off (SLUSE66A 9.3.8), and with no BATFET the kit's load
would then move onto the pack (`gen_sch_a.py` line 782).

**Who does it, and over which path (from the netlists at `a8652172`).** *Detector:* board E's sensor controller `U10`,
the pack gauge's only SMBus host (`gen_sch_e.py` line 264, `J_SMB`; line 581, `U10`'s GPIO2 and GPIO3 on `SMBD` and
`SMBC`), which runs on board E's always-on domain (the buck `U12`, line 565, its EN tied to the pack node `CELL_F`):
on the pack, and on an input, where the charger's system node holds the pack node through the sense resistor
(INFERRED from the charger's arrangement without a BATFET, `gen_sch_a.py` line 782). *Actor:* the panel controller
`U3` on board C (`gen_sch_c.py` line 127): `SLOT_EN1..3` on its GPIO13 to 15, through `J_PANEL` pins 21 to 23 and
`J_AB1` pins 17 to 19, to board A's slot converters `U4`, `U5` and `U6` (`gen_sch_a.py` lines 916, 949 and 917), which
their pull-downs hold off once released; `PI_SHDN_REQ` on GPIO18 to every module's GPIO6 (`gen_sch_b.py` line 402);
the kit bus on GPIO0 and GPIO1 to board A's expanders `U27` at 0x21 and `U28` at 0x24 (`gen_sch_a.py` lines 1259 to
1266) and to the charger at 0x6B (line 784); `PI_KILL` on GPIO19, through `J_AB1` pin 10, to `Q1` and the LTC2954's
`KILL` (lines 269 and 273). *Between them, as generated,* the only path is USB through a running compute module: the
sensor controller's USB (`USB_E6`, `gen_sch_e.py` line 590) over the dock (`J_BLK` pins 9 and 10, `J_DOCK` pins 9 and
10, `J_AB1` pins 25 and 26) to board B's bank 3 hub, port 2 (`gen_sch_b.py` line 766), the bridge on the module that
hosts bank 3, and on to the panel controller on bank 1, port 2 (line 764; bank 3 after BANK-R1). That path is software
on a compute module; it does not exist in the heat stage as board B is generated (bank 3 has no host, above), and it
disappears as soon as H1 has stopped the last module, so the panel controller could neither act on the cells'
temperature there nor see it fall again.

**HOT-R1, the line that makes the path independent of the modules (taken by the session on 27 September 2026 as a
board A and board E design item, owed before their layout entry; section 7a).** The dock already carries a spare
contact from board E's `J_BLK` pin 12 (`BLK_SPARE`, whose only other node as generated is the test point `TP7`,
`gen_sch_e.py` lines 562 and 693) through the dock block to board A's `J_DOCK` pin 12 (`DOCK_SPARE`, `gen_sch_a.py`
line 226), which lands on `U27` pin 18, an input of the expander whose change raises `EXP_INT` (`U27` pin 1 with
`R110`, line 1267), the panel controller's interrupt (`J_AB1` pin 13, board B, `J_PANEL` pin 6, `U3` GPIO24). HOT-R1
drives that contact from the sensor controller's free GPIO19 (`U10` pin 30, not connected as generated) through an
open-drain 2N7002 with a gate pull-down on board E, and pulls it up to board A's 3.3 V with 10 k beside `U27`; the
dock contract `IF-AE-DOCK` (`v2/ecad/tools/pcb_interfaces.yaml`, its pin 12) names it. No part number is new to either
board and no contact is added. One wire carries four states: toggled at 1 Hz, each edge after a fresh reading of all
four cells, the cells read and below H1; toggled at 5 Hz, H1; held low, H2 (so is a line shorted to ground, which
stops the kit); held high, the sensor controller lost (unpowered, in reset or hung, or the contact open). On the last
the panel controller applies the same two steps to board B's `TMP117` under the coolers, which it reads itself on the
kit bus (`gen_sch_b.py` line 1050), at +55.0 C and +56.0 C, released at +45.0 C (the `TMP117` reads at or above the
inside air and idle cells sit at about it: INFERRED, re-derived from `TEST-PLAN.md` E3-L's log), together with the
fallback `THERMAL-COORDINATION.md` section 7 drafts for a lost sensor controller (the reduced mode, the outlets off);
with the line, that fallback no longer mistakes the heat stage as generated, where the readings stop reaching a
module by design, for a lost sensor controller. With HOT-R1 the stop needs no compute module, the panel controller
sees the release itself, and at every start-up it reads the line before it raises any slot, as it reads the ZEROIZE
toggle. **Until HOT-R1 is in both generators the hot stop's requirement reads FAIL on the generated boards,** a finding
reported to the owner, not asked: the stop then acts only where the bridge links the two controllers (the normal and
reduced modes, and the heat stage after BANK-R1, up to H1 itself), and falls back to the `TMP117` elsewhere. The
hand-offs are layer 5's: the dock contract's pin 12, and the four states in the sensor controller's and the panel
controller's firmware contracts (`PANEL.md`).

**Firmware or hardware, and what stands behind it.** The hot stop is FIRMWARE: the sensor controller decides and the
panel controller acts, over one hardware line (HOT-R1) and through hardware that keeps a load off once it is released
(the slot converters' and the expanders' pull-downs; a panel controller that dies stops every module, section 4e). It
is a control, like C1, not a protection. Behind it stand the gauge's discharge cut (OTD, 57.5 C: firmware in the pack,
recoverable, which on the pack takes the kit's supply away and on an input removes no heat) and the hardware
backstops, **every one of them destructive**: board P's second level (the BQ7720700's fixed 70 C over-temperature,
which trips from 62.7 C at its own thermistor and, once armed, blows the chemical fuse F2 and so retires the pack), the
gauge's permanent over-temperature (SOT, 65.0 C, which a cell can meet from 64.2 C: a permanent failure with F2 blown)
and its PTC input at the FETs (about 110 to 133 C: a permanent failure) (`THERMAL-COORDINATION.md` section 4, rows L8
to L12, and section 8). On an input nothing non-destructive in hardware stands between the firmware stop and them.

**An open design question: a non-destructive hardware stage (recorded, not taken).** Whether one is needed is the
question of `THERMAL-COORDINATION.md` section 8 and its Q-P15 (a firmware-free, recoverable hold at the cells' limit),
asked here for the kit's own heat. A comparator on its own 103AT-2 on the hottest cell, supplied from the cell stack,
at most 57.5 C including its own tolerance, with 5 K of hysteresis, whose output takes board A's `KILL` low without any
firmware (over a second dock contact, or through a hardware decode of HOT-R1's held-low state on board A), would stop
the kit's own heat when both controllers' firmware fails; the packet's version, which pulls the pack's FETs off,
removes no heat on an input. It is a protection-architecture judgement for the battery-and-protection reviewer
D-09 provides for, decided before the layout entry of boards A, E and P (board P's four-layer regeneration, O-11), and
it is carried as an open item in the requirements registry with its options, recommendation and cost.

**What it costs, and why it stays open (FEA-004).** On the model's figures (`records/hc2/hotstop_bounds.out`,
INFERRED), H1 acts, lid closed, at the independent bound's worst corner from +34.8 C ambient on the pack and +35.9 C on
an input with the heat stage as generated (+33.2 C and +34.4 C after BANK-R1), and lid open from +37.5 C and +38.6 C
(+36.1 C and +37.3 C); on appendix 32.53's own conductance not below +40.3 C lid closed and +48.1 C lid open. So
whether the hot stop fires inside the envelope is a FEA-004 feasibility question, OPEN until the empty-case
heat-balance test (`TEST-PLAN.md` T-H1) measures the enclosure. Where it fires at +40 C the kit runs no module there, so
closed-lid operation at +40 C (and, at the worst corner, lid-open operation) is predicted to fail REQ-052 on any
supply, not only on the pack: a layer-4 item under FEA-004, recorded and not waived. Whether H1's minimum load
(PS-HOLD, not computed: the heat stage's loads less any module, **TBD**) brings the cells back under the release at
+40 C is part of the same measurement. No requirement is lowered and the envelope is not narrowed. The requirements
registry carries the hot stop as a core requirement under NEED-13 (the kit acts before idle cells pass +60 C in every
input state), verified by `TEST-PLAN.md` E3-H.

**BANK-R1: the bank allocation that lets one module carry the owner's example (taken by the session on 27 September
2026 under the owner's standing rule of 26 September 2026, as a board B design item; section 7a).** Which hub port a
USB device hangs on is one table in board B's generator (`gen_sch_b.py` lines 764 to 766, `PORTS`), and the LoRa
module ties the example to slot 3, whose banks are 3 (its home) and 2 (its failover). Two exchanges of hub ports put
the example and the SOS path on those two banks: **the RockBLOCK (bank 1, port 4) with the QMX (bank 2, port 4)**, and
**the panel controller (bank 1, port 2) with the sealed wall USB port (bank 3, port 3)**. The banks then hold: bank 1
the SDR, the wall port, the camera and the QMX; bank 2 the GNSS, both E72 and the RockBLOCK; bank 3 the APRS board D8,
the sensor controller, the panel controller and the 5G management link. **It keeps `ARCH-PCB-B-IOHA.md` section 8's
rule** that no bank holds two long-range bearers (bank 1 HF, bank 2 Iridium, bank 3 APRS: the invariant
`check_pcb_b.py` lines 424 to 431 checks), and the kit still keeps at least three of D-01's four messaging bearers
through any one module loss (slot 1 lost: all four; slot 2 lost: the LoRa mesh, Iridium moved with bank 2 to slot 3,
and APRS; slot 3 lost: 5G, Iridium on its home slot 2, and APRS moved with bank 3 to slot 1). Iridium then fails over with bank 2 (to slot
3) and SOS with bank 3 (to slot 1), so the pair of modules whose loss leaves SOS without a host becomes slots 3 and 1
(it is slots 1 and 2 as generated), and the modules that can unlock their drives at boot through the panel controller
(`feasibility/ZEROIZE.md` section 3.3 and its risk R4) become the hosts of bank 3. The exchange is a netlist change on board B
alone: the hubs' data pairs, with no part added or moved. Its routing, its checks (the bearer invariant, the contracts
on `USB_PNL` and `USB_WALL`, the acceptance tests A1 to A14) and the documents that name bank 1 as the panel
controller's (`ARCH-PCB-B-IOHA.md` sections 4, 15 and 15a, `feasibility/ZEROIZE.md`, `feasibility/EMCON.md` section 4.5,
`PANEL.md`) are board B's owner's, before board B's layout entry, from a hand-off that carries the proposed generator
change. If board B's owner finds a reason the exchange cannot be made, the other one that keeps section 8's rule (the
panel controller with the 5G management link, bank 3, port 4) is tried; if neither can, the finding below stands and
goes to the owner as a trade between his example and section 8's rule. **Until BANK-R1 is in board B's generator,
REQ-052 is not met by board B as generated** (its one-module stage lacks the LoRa mesh and APRS): a finding against the
generated board, reported to the owner at the next checkpoint, not asked.

**The hot end is behaviour on measured internal temperatures; the ambient figures are bounds.** The kit has no ambient
sensor in prototype 1's core (the outside pod is deferred by D-01), so no mode can be entered on "ambient above +35
C". The controls, taken by the session in `feasibility/POWER-THERMAL.md` section 9.3 and carried here with what the
operator sees:

| Control | Acts when | Does | The operator sees |
|---|---|---|---|
| the gauge's charge window | any cell outside the gauge's charge window (0 to 45 C in `pcb_pack_protection.yaml`; round 8 sets UTC 1.0 C and OTC 44.0 C inside it, SC-12, on main since `53a98a71`) | holds the charge; the loads carry on from shore | CHARGING dark with SHORE lit; the e-paper names the cell temperature |
| C1, module shedding | inside air +50 C or any cell +55 C | normal to the reduced mode; reached again in the reduced mode, to the heat stage; restores 5 K below | MASTER CAUT, the e-paper "HEAT: REDUCED MODE" or "HEAT: ONE MODULE" with the trigger |
| C2, the outlet budget | the 10 s average pack current above 9.0 A, or any cell +50 C | sheds USB-C, then PoE; a temperature shed latches until the operator re-enables | the e-paper names the outlet and the trigger |
| C3, current shedding | with both outlets off, the 10 s average pack current above 9.0 A for 30 s (the gauge's current, or the charger's reading in the heat stage as board B is generated) | as C1 | as C1, "CURRENT" |
| K1 to K5 and C4, every PA key-down | a key-down (60 s at most, gates at key-on, the in-key guard) | refuses or ends the key-down (section 5) | the e-paper "TX HELD" or "TX CUT" with the reason; the TX lamp follows the real KEY line |

C2 and C3 ignore a PA key-down while it runs and for 10 s after it (`feasibility/POWER-THERMAL.md` section 9.3). **The ambient at which each stage acts, as bounds**
(INFERRED: `feasibility/POWER-THERMAL.md` section 9.2's columns and `records/hc2/pwr_red2.out`, both on the same model;
first the independent enclosure bound, worst to best, then in brackets appendix 32.53's own conductance):

| From | Enclosure | C1 acts at an ambient of (C) | The cells' charge stops at (C) |
|---|---|---|---|
| three typical modules (PS-TYP) | lid open | -6.3 to +27.5 [+28.6 to +30.5] | -17.8 to +19.4 [+19.5 to +21.6] |
| the reduced mode (PS-RED2) | lid closed | +20.1 to +37.3 [+28.9 to +34.2] | +5.3 to +29.2 [+18.4 to +24.5] |
| the reduced mode (PS-RED2) | lid open | +24.0 to +38.9 [+39.4 to +40.4] | +10.0 to +31.0 [+30.7 to +31.8] |
| the heat stage after BANK-R1 (PS-SURV-R) | lid closed | +27.9 to +40.6 [+34.4 to +38.3] | +13.5 to +32.6 [+24.1 to +28.8] |
| the heat stage after BANK-R1 (PS-SURV-R) | lid open | +30.8 to +41.8 [+42.2 to +42.9] | +17.1 to +34.0 [+33.6 to +34.4] |
| the heat stage as generated (PS-SURV) | lid closed | +29.4 to +41.2 [+35.4 to +39.1] | +15.1 to +33.3 [+25.2 to +29.7] |
| the heat stage as generated (PS-SURV) | lid open | +32.1 to +42.3 [+42.7 to +43.4] | +18.5 to +34.6 [+34.1 to +34.9] |

**What the owner accepted with D-02b, and where it now stands.** He accepted two consequences argued on estimated 10 K
and 16 K rises: one module above +35 C ambient, and no charge above about +25 C with three loaded modules. On the
current figures the kit sheds sooner (the first row: +28.6 to +30.5 C on the design record's own conductance) and
stops charging sooner (+19.5 to +21.6 C there), and on the independent bound both could happen at any ambient of the
envelope. The ruling stands, the behaviour is defined, and the changed figures are reported to the owner at the next
checkpoint, not asked. **Reported with them (Review A, m7):** at the independent bound's worst corner the kit leaves
its three-module redundancy from -6.3 C ambient (PS-TYP, lid open) and runs on one module from +20.1 C lid closed or
+24.0 C lid open (the reduced mode's C1 rows), well below the +35 C the owner accepted; the one-module stage as board B
is generated has neither the LoRa mesh nor APRS (BANK-R1 restores them); and the owner accepted CON-012's residual risk
at +35 C, so that acceptance is not carried over to these ambients: the registry restates CON-012 on them without an
owner acceptance (a hand-off). **Whether the in-use hot end holds on the pack is a layer-4 feasibility item, not
settled here:** in the heat stage as generated (slot 2), lid open and shaded at the envelope's +40 C, the cells stay
inside their 60 C window at every corner of the record (the worst corner has 1.0 K to spare), and round 8's discharge
cut at 57.5 C (OTD, SC-12) would act from +38.5 C at that corner (INFERRED, the stage's discharge ceiling less 2.5 K),
leaving the kit to an input; lid closed the cells' 60 C is reached from +38.3 C and OTD from +35.8 C at
that corner. In the required heat stage after BANK-R1 (slot 3, 1.6 W more), the worst corner passes the cells' 60 C
from +39.6 C lid open and +36.7 C lid closed, and OTD from about +37.1 C and +34.2 C (`records/hc2/pwr_red2.out`).
Since pass 3 the hot stop (above) acts before OTD in the same reading, from about 1 K lower ambients on the pack and
somewhat later on an input, so at that corner the kit keeps no module running at +40 C on any supply, lid open or
closed (`records/hc2/hotstop_bounds.out`).
Three typical modules at the runtime requirement's own +20 C put the
cells at 45.4 to 81.3 C on the independent bound (`feasibility/POWER-THERMAL.md` section 9.2). **Why this layer can
close without the number, and what does depend on it:** no mode, trigger, bearer set or product decision of this
document changes with the enclosure conductance, because every control acts on a measured internal temperature or
current, the hot stop included: REQ-077 requires it to act before any cell passes +60 C in every mode and on every
input, and the design intends it to do so at any conductance once HOT-R1 is in the generators of boards A and E (the
requirement reads FAIL on the generated boards until then) and on the provisional error budget (H2 leaves 0.93 K for
the budget's two TBD terms, `TEST-PLAN.md` P14); whether it acts inside the envelope is FEA-004's, open. What changes is
at which ambient each acts (for the hot stop, whether inside the envelope at all, above), whether PS-TYP is a sustained mode at +20 C, and whether the pack
pocket and the PA's flange site need a different thermal design, and, at the cold end, whether the warm-up brings
the WiFi link cards up at -20 C (below): a feasibility outcome that can fail, not a mode or a decision of this
document. Those are decided by the empty-case heat-balance test (`TEST-PLAN.md` T-H1, FEA-004), which gates the
placement freeze of the pack and the PA flange site, before layout of boards A, D and P, and at the cold end by the
part search that removes the bound; lowering the envelope is not an option taken or offered.

**The cold end (restated 27 September 2026, answering Review A, B7).** The in-use floor is -20 C ambient with the
carve-outs of `OPERATING-ENVELOPE.md` section 4 (the pack warmed before charge below -10 C; the e-paper degraded below
-15 C; no start from a pack cold-soaked below about -10 C at the cells, D-02d). Two bought parts are rated only from
0 C (`feasibility/POWER-THERMAL.md` section 9.4, PWR-F09): the AW7915-AED WiFi link cards (0 to +70 C in AsiaRF's 2023
PDF, -10 to +70 C on its 2026 page) and the LimeSDR Mini 2.4 (0 to +70 C operating and storage). The kit-to-kit link
the cards carry is a critical peripheral of prototype 1 (SC-02; `ARCH-PCB-B-IOHA.md` section 15a) whose changeover is
core test A11, so the cold end has to bring the link up, not only the rest of the kit. **The inside air per state,
lid open with the fans on** (`records/hc2/pwr_red2.out`, its COLD block; INFERRED: the air reaches 0 C from the
ambient that equals minus the heat inside over the conductance, and the coldest case is the highest conductance in the
record, appendix 32.53's 3.3 W/K):

| State (the link cards and the SDR held off unless the row says otherwise) | Battery W, PLAN | The air reaches 0 C from an ambient of (C): 32.53's conductance, worst to best [the independent bound] | The air at -20 C ambient on 32.53's conductance (C) |
|---|---|---|---|
| PS-IDLE-SPEC | 36.9 | -11.3 to -12.4 [-13.1 to -30.6] | -8.7 to -7.6 |
| PS-IDLE-SPEC with the pack heater | 45.5 | -14.0 to -15.4 [-16.2 to -37.8] | -6.0 to -4.6 |
| PS-TYP | 51.2 | -15.8 to -17.4 [-18.3 to -42.7] | -4.2 to -2.6 |
| PS-TYP with the pack heater | 59.8 | -18.5 to -20.3 [-21.4 to -50.0] | -1.5 to +0.3 |
| **the cold warm-up:** PS-TYP with the pack heater and the three modules loaded | 71.1 | -22.0 to -24.2 [-25.5 to -59.6] | +2.0 to +4.2 |
| PS-TYP with every load on and the heater (once the parts are powered) | 71.6 | -22.2 to -24.4 [-25.7 to -60.0] | +2.2 to +4.4 |

The heater is taken at 8.5 W, the regulated mat on main since `458b2873`; the model's own unregulated 10.8 W reproduces
`feasibility/POWER-THERMAL.md` section 7.1's cold row (+2.9 to +5.2 C at -20 C). So in its idle and typical states the
kit's own heat does not bring the inside air to 0 C at the envelope's -20 C on the design record's conductance, and
with the carve-out alone the cards and the SDR could stay off for as long as the kit ran, which would remove the
kit-to-kit link at the cold end: "they come up late", this paragraph's first reading, did not hold. **Taken: the cold
warm-up, as the behaviour the carve-out rests on.** While the WiFi link cards or the SDR are wanted and the inside air
(the BME688 on board E, the TMP117 on board B) reads under 0 C, the bridge runs the pack heater and loads the three
modules; the cards and the SDR are powered once the air reads 0 C or more and stay powered while it does; the
modules' load is released once the air holds +5 C with the parts running and taken up again if it falls to +1 C, and
the heater runs while the air is under +5 C (PROVISIONAL thresholds, re-derived at bring-up). At -20 C on 32.53's
conductance the warm-up holds the air at +2.0 to +4.2 C, and the typical load with every part on and the heater at
+2.2 to +4.4 C, so at the envelope's floor the heater stays on and the link runs; the
kit then draws about 71 W (1.5 h on an aged pack at +20 C, less in the cold, section 4a), which is why a long mission
at the cold end runs on an input. **Where it fails, which stays open (a feasibility bound that includes failure):**
the warm-up reaches 0 C at -20 C only while the enclosure's conductance, lid open with the fans, is at most about
3.6 W/K (72.7 W of heat over 20 K), 10 % above appendix 32.53's upper figure; neither figure in the record is a
measurement, and neither counts wind on the case, which would raise it (INFERRED). Above it the cards stay off at
-20 C and `TEST-PLAN.md` E4-O fails on the link; E4-O's pass line is not relaxed. **The route that removes the
failure** is a WiFi link card and an SDR of an extended grade (layer 6), and where the part found does not fit the same
M.2 socket and 3.3 V supply, or the same USB 3 receptacle, the change is board B's and is decided before board B's
layout entry. T-H1 measures the conductance (FEA-004); if no extended-grade part is found and the conductance is above
3.6 W/K, the link at -20 C is reported to the owner as not met. **Why this layer can close with it open:** the
requirement (use down to -20 C, the link a critical peripheral, E4-O's pass line) and the behaviour are set here;
whether the parts and the thermal path meet them is a component and architecture question (layers 6 and 4), with its
decision point named, and no mode or product decision of this document changes with its answer. The LimeSDR's storage
range (0 to +70 C) is narrower than the kit's storage envelope and the +71 C and -33 C margins: an
exception recorded, not a lowered envelope, judged at E3-S and E4-S (`TEST-PLAN.md`). The NVMe drives, not yet picked,
are to be a -20 C or industrial grade (a requirement on the pick).

**Recovery and delivery targets.** (1) **A moved bank:** every device of a bank whose home module is lost is back in
service within **30 s** of the loss, plus the device's own start-up where its maker states a longer one (the
RockBLOCK's network registration, the GNSS re-acquisition: each **TBD** from its sheet); this is the pass line of
REQ-004's per-device timeout, and the time measured on hardware must be at or under it. "Back in service" is step 12
of `ARCH-PCB-B-IOHA.md` section 7, application access resumed, by a bridge instance already running on the adopting
module (Review A, m9). **The bridge's own service** is a separate bound: when the lost module ran the bridge, its
service is required back on a surviving module within **60 s** of the loss; whether k3s reschedules it with its
timeouts set to meet that, or an instance is kept running on every module, is the Bridge's design, outside this
repository (MESHSAT-835 to 848), and until it is shown the 30 s holds only where a bridge instance already runs.
(2) **A bearer declared down:**
a bearer is declared down when its device is lost or when it has accepted no hand-off for 60 s while one was
pending; every message queued on it goes to the next long-range bearer that is up, in the routing layer's cost order,
within **10 s** of the declaration (NEED-02). (3) **The kit's own share of every delivery:** a message for a bearer
that is up is handed to that bearer's device within **10 s** of being queued. (4) **End to end**, from the kit to a
correspondent, is set by networks outside the kit (the Iridium constellation, a cellular network, a mesh, an APRS
digipeater or gateway): it is measured per bearer in the functional check and recorded as characterisation, not
a pass line. These close S-37 and REQ-003's latency TBD for the kit's part.

**Graceful shutdown on the pack.** The bridge starts a clean shutdown of every module when the gauge's relative state
of charge reaches 5 % (the reserve the runtimes of section 6 keep) or the lowest cell reads 3.00 V or less under load
for 10 s, whichever first (the voltage line stands in for the gauge's state of charge until the pack's learning
cycle has run); it writes the e-paper's power-off page with the time and the reason, and the panel controller drops
`DEV_EN` last (`PANEL.md` section 5). 3.00 V sits above the cell's rated cut-off (2.65 V, Ver. 1.1 3.9) and the gauge's
2.50 V trip. **In the heat stage as board B is generated**, where the gauge's readings reach no module, the bridge
starts the same shutdown when the pack voltage the charger reads (above) is 12.8 V or less under load for 10 s: 3.20 V
a cell on average, 0.20 V above the per-cell line, because a sum cannot see one low cell. One cell more than about
0.9 V below the other three (12.8 V with one cell at the gauge's 2.50 V leaves 3.43 V on each of the others) can still
let the gauge's under-voltage trip act first, and the kit then goes dark as on a pack protection trip (section 4e).
After BANK-R1 the heat stage keeps the gauge's readings and the lines above apply. Every threshold here is PROVISIONAL
and re-derived at bring-up from the pack's measured discharge curve.

**Preparing for storage or transport.** The operator selects it on the touch UI; the bridge brings the pack to the
ex-factory state for storage (3.49 to 3.69 V per cell, by running the kit down or charging it on shore) or leaves its
charge for transport; the operator then unplugs every input, because the gauge enters its shutdown only with no
charger present (SLUUAQ3A 5.4.2 and 13.1.8), and the e-paper says so until it is done; the bridge shuts every module
down, and the sensor controller sends the gauge's shutdown as the last act; the e-paper keeps "STORED" or "TRANSPORT"
with the date and the pack's charge. In that state board E's always-on domain, on the pack side of the gauge's FETs,
is unpowered, so the lid and tamper log does not run, and the kit starts only once an input has woken the gauge
(Review A, m5). A kit left in PS-OFF instead drains its pack in 3 to 28 days (section 4a).

### 4d. Commissioning (added 27 September 2026)

The first power-up of a built or rebuilt kit, of a replaced pack, secure element or panel controller. Every step is
written into the commissioning log (`ASSEMBLY.md` section 8), which the handover keeps. D-03, D-12 and D-15 depend on
it.

1. **Build checks, current-limited, board by board**, as `ASSEMBLY.md` section 8 orders them (each rail at its
   converter before its loads), **except its step 10**, ten minutes of key-down of the PA at 30 W into a load: K1
   limits every key-down to 60 s (section 5), and one 60 s key-down at 45 W of heat from a +50 C plate already puts
   the flange at about 95 C on the record's own figure, against the RA30H1317M1's +100 C case maximum and its 90 C
   advice (`feasibility/POWER-THERMAL.md` PWR-F15). Step 10 is superseded by T-H3's procedure (`TEST-PLAN.md` section
   8): key-downs of at most 60 s into a load, at least 2 s apart, with the flange sensor and a thermocouple beside it
   logged, each started only inside K2 and ended by C4. The correction is handed to `ASSEMBLY.md`'s owner, with its
   step 7's lamp-test count, which is `PANEL.md` section 9's seventeen controller-lit indicators (changed 27 September
   2026, answering Review A, B6).
2. **The pack, before its first charge or discharge:** the gauge's golden image written and its protection thresholds
   and enabled protections read back and compared with `v2/ecad/tools/pcb_pack_protection.yaml` (the data-flash
   verification of D-15; `ASSEMBLY.md` section 8 step 12); the second level's commissioning readings
   (`review-packets/battery/PROTECTION-ARCHITECTURE.md`, O-9); only when both pass is the arming jumper JP1 closed,
   which lets the second level and the gauge's FUSE output blow the chemical fuse F2. Then one full charge and
   discharge for the gauge's learning cycle; the full-charge capacity it records is the pack's reference for "aged"
   (section 6).
3. **The secure element**, as `feasibility/ZEROIZE.md` section 3 sets it: its configuration written and its zones
   locked, the two key-encryption keys generated and their public keys recorded, every drive and eMMC enrolled under
   both with one keyslot and no recovery keyslot.
4. **Key fill** over the console on the sealed Glenair 233-370 port, by the signed procedure (D-12, REQ-037).
5. **Firmware:** the panel controller, the sensor controller and the three supervisors (their software-verified boot
   is D-13's floor), each image's version logged.
6. **The functional check of `TEST-PLAN.md` section 4**, including EMCON with the lamp check of section 4b.1 and a
   ZEROIZE, after which the drives are re-enrolled from the recovery state (`feasibility/ZEROIZE.md` section 3.2).

### 4e. Faults: what the kit does, what the operator sees, how it recovers (added 27 September 2026)

As generated at `45bde541` unless a row says a fix is owed. The four whole-kit common modes (ASM-002: the device
rails, the `J_PANEL` ribbon, the Ethernet switch, the kit I2C bus) are here with their behaviour; whether each is
mitigated or kept as a named exception is decided at Review C (S-36), not here.

| Fault | What the kit does | What the operator sees | Recovery |
|---|---|---|---|
| a compute module lost | its bank moves to the neighbour (section 4c, 30 s); the named exceptions go with it (LoRa with slot 3, 5G data with slot 2) | MASTER CAUT; the e-paper names the slot | the slot is cycled once and then left off until the operator acts (`PANEL.md` section 5) |
| two modules lost | one bank has no host (`ARCH-PCB-B-IOHA.md` section 4); as generated, with slots 1 and 2 both lost, bank 1 and with it Iridium, the panel's USB link and so SOS have no host, and slot 3 cannot unlock a drive at its next boot (`feasibility/ZEROIZE.md` section 3.3); after BANK-R1 (section 4c) the pair that leaves SOS without a host is slots 3 and 1, and Iridium then stays on slot 2 | MASTER WARN; SOS set in that state shows "SOS NOT SENT: NO HOST" (`PANEL.md` section 9) | a module restored on a host of the lost bank |
| a supervisor lost | the other two keep quorum; nothing moves (acceptance test A4) | MASTER CAUT | service |
| the panel controller lost (crash, held in reset, in its bootloader) | as generated, `SLOT_EN1..3` fall to their pull-downs and every module stops (`ARCH-PCB-B-IOHA.md` section 10); EMCON, MAIN PWR and the TX lamp act without it; the charger loses its host and falls to 256 mA after its watchdog (`PANEL.md` section 10); no SOS, no ZEROIZE until it runs again | the indicators hold their last state or go dark; the e-paper keeps its last page; the monitor goes dark | its watchdog restarts it, and it runs the boot order again and powers the slots (every module cold-boots); the hold of `SLOT_EN` across a controller restart is a layer-5 design item still owed (board C or A) |
| the panel ribbon unplugged | every EMCON gate closes, the PA cannot key, no module runs, the charger has no host (`PANEL.md` section 7) | the panel dark (its supply comes over the ribbon) | service: reconnect |
| a device rail lost (`+5V_DEV` or `+3V3_DEV`, one converter each on board A) | every bank's hub and peripheral is lost; a loss of `+3V3_DEV` releases every EMCON gate hung on `EMCON_ON` or on a slot's `U{s}11` (EMCON.md L3, open under S-01) | MASTER WARN; every bearer chip down | service |
| the Ethernet switch lost | the modules lose each other and the wall port; a module that does not host bank 1 cannot unlock its drives at boot (`feasibility/ZEROIZE.md` R4) | MASTER WARN | service |
| the kit I2C bus stuck, or its master lost | the secure element, the charger, the supervisors' status and board A's expanders are unreachable; drives do not unlock at boot; a wipe that is due cannot be proven, so the slots stay off (fail secure, `feasibility/ZEROIZE.md` section 3.5) | MASTER WARN, the e-paper message | service |
| a fan stopped | the mixer fans' tachometers are read by the sensor controller (`gen_sch_e.py` line 503); the cooler fans' are **TBD**; the inside air rises and C1 sheds; on 32.53's still-air figure PS-TYP at +20 C brings the air to about +50 C, where C1 acts (`feasibility/POWER-THERMAL.md` section 9.2) | MASTER CAUT "FAN n" for a mixer fan; the C1 indications | service; the kit runs shed until then |
| water on the case floor (REQ-042, deferred by D-01) | designed: the bridge shuts every module down, the panel asserts `SHORE_INHIBIT`, and the sensor controller puts the pack in the gauge's shutdown, so the kit is dark and isolated; the threshold is **TBD**, and the path from the sensor to the pack is REQ-042's (the gauge's SMBus shutdown the sensor controller already sends is the one the design has); in the heat stage as board B is generated bank 3 has no host, so the bridge does not learn of it, and what the sensor controller does on its own then is a firmware contract item (**TBD**) | MASTER WARN and the e-paper "WATER IN CASE" before it goes dark | service: dry, inspect, then an input wakes the gauge |
| gas in the battery bay (the SGP41; its response to hydrogen **TBD**) | as for water, and no charge | MASTER WARN and the e-paper "BATTERY GAS: MOVE THE KIT INTO THE OPEN AIR, DO NOT OPEN NEAR PEOPLE" | service; the pack is inspected and, if it vented, replaced (section 4d) |
| a pack protection trip that recovers (the gauge's over-current, over- or under-temperature, cell under-voltage) | the gauge opens its FET; on the pack alone the kit goes dark; with shore or vehicle input the loads carry on from it (the loads sit on the charger's system node) and the charge holds | before a trip, the indications of section 4c and the graceful shutdown; the bridge writes a "PACK PROTECTION" page when the gauge reports a pending safety status | the gauge's own recovery: temperature back inside its window, an input for a cell under-voltage; the proposed over-current backstop recovers only on an input (`feasibility/POWER-THERMAL.md` section 9.3) |
| the heat stage cannot hold the cells (the enclosure at the low end of its bound; on the pack or on an input) | the hot stop (section 4c): at +56.5 C, the hottest cell as the gauge reads it, every module shut down cleanly and the switched loads and the charge held off (H1); at +57.0 C the kit shut down by `PI_KILL` (H2); behind it the gauge's OTD and the destructive backstops | MASTER WARN and the e-paper "HOT STOP: COOLING" (H1) or "HOT SHUTDOWN: RESTART WITH MAIN WHEN COOL" (H2), with the hottest cell reading; every bearer down, SOS included | H1: the heat stage's module raised again once the hottest cell reads +46.5 C or less, at most once in 30 minutes; H2: the operator's MAIN; meanwhile the operator shades the kit, opens the lid or moves it |
| the hot stop's detector lost (with HOT-R1: the line held high because the sensor controller is unpowered, in reset or hung, or the dock's spare contact is open) | the panel controller applies the hot stop's two steps to board B's `TMP117` (+55.0 and +56.0 C) and falls back to the reduced mode with the outlets off; a line shorted to ground reads as H2 and stops the kit | MASTER CAUT "PACK TEMPERATURE NOT READ" | the sensor controller's watchdog; otherwise service |
| lightning within 10 km (the AS3935's storm-distance estimate; the sensor deferred by D-01) | the mast-down alarm (the requirements registry's REQ-041, a session choice, section 7a): the sensor controller detects it and the bridge raises it (in the heat stage as generated, where bank 3 has no host, it waits for one, as the water and gas responses do); it moves no switch and removes no power | MASTER WARN with the storm distance and the instruction to lower the masts | cleared once 30 minutes pass with no event at 10 km or less |
| a permanent pack protection (the second level or the gauge blows F2; the PTC trips) | the pack is retired; the kit runs only on an input | the e-paper "PACK FAILED: REPLACE" | service: a new pack, commissioned (section 4d) |
| an input fault (a reversed or over-voltage vehicle input, shore lost while charging, weak solar) | the ideal diode and the 9 to 36 V front end hold the kit off a reversed or over-voltage input; no vehicle surge claim (D-16); the pack carries the loads | MASTER CAUT "SHORE LOST" when a charge was expected (`PANEL.md` section 9) | the input fault removed |
| a push to talk held, or board D's CP2102N RTS line stuck, while the panel controller and the bridge are hung (`feasibility/POWER-THERMAL.md` PWR-F16, round 8, on main since `53a98a71`) | board D's KEY follows the held line in hardware, so the PA stays keyed: K1's 60 s, K2 and C4 are firmware, and nothing in hardware ends the key-down or bounds the flange (PWR-F15) | the TX lamp lit (it follows the real KEY line) | release the push to talk; a hardware bound is PWR-F16's open item |

### 4f. The core functions in every mode (added 27 September 2026)

The core of D-01 (section 2a), mode by mode. "Held" means the function waits, queued, and the operator is told.

The heat stage has two columns: its required set, which board B carries once BANK-R1 is in its generator (slot 3),
and what board B as generated gives (slot 2), with its shortfall marked (section 4c).

| Core function | Normal | Reduced | Heat stage, required (slot 3, after BANK-R1) | Heat stage as generated (slot 2) | EMCON | One module lost | Panel controller lost |
|---|---|---|---|---|---|---|---|
| Iridium | yes | yes (as generated bank 1 on slot 2; after BANK-R1 bank 2 on its own slot 2) | yes | yes | held (dark) | yes (its bank moves) | no module runs |
| 5G | yes | yes | no (its data is slot 2's) | yes: data over PCIe, and AT control over PCIe once the bridge's PCIe AT channel is shown (data only until then); no firmware update (its USB link is on bank 3) | held (airplane mode now; supply removal owed, section 4b.1) | yes, unless slot 2 (named exception) | no module runs |
| LoRa mesh | yes | yes | yes | **no: the finding against the generated board** | held (dark) | yes, unless slot 3 (named exception) | no module runs |
| APRS | yes | yes | yes | **no: the finding against the generated board** | receive only | yes (bank 3 moves) | no module runs |
| The failover fabric | one loss absorbed | a further loss leaves one bank without a host | no redundancy | no redundancy | as the mode it overlays | a second loss leaves one bank without a host | no module runs |
| Charging | yes, inside the gauge's window | yes | yes | yes, inside the gauge's window, which the kit no longer reads | yes | yes | the charger falls to its host-free 256 mA |
| Hardware EMCON | yes | yes | yes | yes | asserted | yes | yes (hardware) |
| ZEROIZE | yes | yes | yes | yes | yes | yes | not until the controller runs again; a toggle still closed completes the wipe at its next boot |
| Pack safety | the gauge and board P's second level in every mode, PS-SHUT included (the second level destructively, above the cells' limit); past the heat stage, the hot stop on the cells' measured temperature in every mode and on every input state (firmware; HOT-R1 owed on boards A and E, section 4c) | | | | | | |
| Service access | in the service mode | | | | | | |
| SOS | yes | yes | yes, with a live position | yes, with a live position | held, the operator told (D-10) | yes; a further loss of the other host of the panel's bank removes it (slots 1 and 2 as generated, slots 3 and 1 after BANK-R1) | not available |

## 5. What runs at the same time, and how often

**The rule the hardware is designed to:** no transmit serialisation is required; every transmitter may key at
once (owner ruling of 4 September 2026, appendix line 2337, restated at line 2465), **bounded since 26 September
2026 by owner ruling D-11**: all at once for a declared key-down time above a declared state of charge, with the
outlets at their minimum contract, which is **0 W, the outlets off** (the session's reading of D-11, section 7a; it
is what the hardware interlock below does and what `feasibility/POWER-THERMAL.md` assumes). The session set the
thresholds (session choice SC-10 of the requirements registry and the key-down rules K1 to K5 with the in-key guard C4
of `feasibility/POWER-THERMAL.md` sections 7.2 and 9.3), and since 27 September 2026 they are requirement REQ-018's
pass lines (the layer-3 closer's session choice on D-11's declared values): every transmitter at
once only above a pack rest voltage of 15.5 V, the PA keyed alone only above 12.4 V and never below it (the operator
is told); every PA key-down, all-transmit or alone, **at most 60 s** with at least 2 s between key-downs (K1), started
only with every cell at most +55 C, the inside air at most +50 C and the PA's flange at most +75 C (K2) and the pack
current at most 9.0 A (K3), with the outlets, the pack heater and the standby WiFi card off (K4), and ended early above
18 A, below 2.70 V on any cell or at +85 C on the flange (C4). Whether the design meets them is feasibility blocker
FEA-004's, not an open requirement: the pack chain has to carry its short-time rating at 18 A for 60 s (PWR-F12) and
the flange reading has to hold (PWR-F15; the sensor drawn on board D in round 8, on main since `53a98a71`, and read by
firmware), and if FEA-004 closes in failure these values reopen; until then one key-down from a +50 C plate is bounded at about 30 s on the record's own
figure, and repeated key-downs are OPEN (`feasibility/POWER-THERMAL.md` PWR-F15). The hardware interlock that drops the outlets while the PA keys, which the design record asks for
(32.55 line 2932), is on board A since `458b2873`: `U30` forms OUTLET_OK = NOT (TR_APRS AND PA_EN), low while the PA
keys, and two gates of `U26` give POE_EN = POE_SW_EN AND OUTLET_OK and PD_EN = PD_SW_EN AND OUTLET_OK (`gen_sch_a.py`
lines 1088 to 1104 at `45bde541`). **Corrected 26 September 2026 (S-07):** this paragraph said the PoE and USB-C
enables were software expander pins with no hardware tie to the PA keying, the circuit before `458b2873`. The load figures below are the design estimate of
appendix 32.52 item 3 (line 2846) unless a datasheet figure is given beside it; **none has been measured**. Duty
cycles are the weakest part of the record: where no source exists the cell says **TBD** and names what the
missing number moves.

| Load | Typical / peak W (32.52) | Datasheet cross-check | Realistic duty | Worst duty | Missing number moves |
|---|---|---|---|---|---|
| Three CM5 modules | 18 / 36 | idle 0.4 A, operation 0.9 A typical at 5 V each (CM5 datasheet, current consumption table) | three idle in normal, one in reduced | three loaded | runtime, inside-air rise |
| Xenarc monitor | 6 / 10 | at most 10 W (Xenarc 709GNK product manual v2) | on in DAY and NIGHT, dimmed, off in blackout | full brightness | runtime |
| WiFi link card (one live) | 3 / 10 | none held | link up continuously in M3: **TBD** | continuous transmit | runtime, EMC |
| 5G module | 3 / 10 | idle 60 mA, RF disabled 4.7 mA, LTE carrier aggregation 1,512 mA (RM520N series hardware design v1.1, Table 43) | **TBD** | continuous data | runtime, thermal |
| LimeSDR Mini 2.4 | 3 / 3 | up to 4.5 W, the USB 3.0 limit (maker's page https://myriadrf.org/projects/limesdr-mini-2-0, "Maximum Power 4.5 W", read 25 September 2026) | receive while monitoring: **TBD** | continuous | runtime |
| LoRa E22-900M30S | 0.5 / 6.5 | TX 650 mA, RX 14 mA (Ebyte manual v1.20) | **TBD** (mesh traffic) | regulatory cap: 10 % duty at 27 dBm on 869.4 to 869.65 MHz (32.49 item 4) | runtime |
| RockBLOCK 9704 | 0.5 / 5 | 60 mW idle, 1.4 W max (`rb9704-datasheet-RB9704-001-JUN26.pdf`) | message driven: **TBD** | continuous session | runtime (the budget is above the datasheet) |
| QMX HF | 1 / 12 | RX 80 mA, TX 0.7 to 1.1 A at 12 V (32.51 line 2816) | **TBD** (a Winlink or Mercury transfer is long) | continuous transmit for a transfer | runtime, thermal |
| APRS with the 30 W PA | 1.5 / 75 | over 30 W out at over 40 % efficiency at 12.5 V, about 45 W of heat (32.51 line 2813) | a beacon every 10 minutes at a fixed site, at most one a minute on the move (the planning profile below); "APRS duty only at full power" (32.49 item 8) | **at most 60 s per key-down** (K1), started only inside K2 to K5 and cut by C4 (`feasibility/POWER-THERMAL.md` sections 7.2 and 9.3, PWR-F14); the design record's two figures bracket it: 32.53's "the 200 W peak (PA key-down) lasts minutes" (line 2860) and 32.56's "a 20 s key-down at 45 W" on the plate's local patch (line 2940). Corrected 27 September 2026: this cell said "key-down for minutes" | thermal (PA flange and plate patch, PWR-F15), runtime |
| Switches, hubs, bridges, controllers | 6 / 8 | plus about 0.9 W for the I/O supervisors (`ARCH-PCB-B-IOHA.md` section 14) | continuous | continuous | runtime |
| Sensors and panel | 2.5 / 2.5 | none | continuous | continuous | runtime |
| PoE and USB-C outlets | 0 / 90 | 45 W USB-C (32.57 line 2980), PoE 54 V at 0.6 A (32.55 line 2927) | accessory dependent: **TBD** | full, cut to minimum while the PA keys (D-11) | runtime, input budget |
| Conversion losses | 12 % | none | | | runtime |
| **Sum** | the listed loads are 45.0 W typical and 178 W peak; with the 12 % allowance that is 50.4 W and 199 W, the record's "about 50 W" and "about 200 W", so those two figures are **at the battery**. The record's "up to 290 W" is 199 W plus 90 W of outlets, **without** the allowance on the outlets | | | | |

The 32.52 estimate predates the loads added after 7 September 2026 (the I/O supervisors, the second WiFi card,
the fans) and uses one flat 12 % for conversion; re-derived per path with each converter's own curve, the typical
state is PS-TYP at 63.0 W (section 4a, `feasibility/POWER-THERMAL.md`). Where the two differ, section 4a is the current
PROVISIONAL figure and 32.52 is history.

**The planning duty profile (taken by the session under the owner's standing rule of 26 September 2026, section
7a).** A product choice for the budgets and for REL-001's duty cycle; measured duty replaces it after
bring-up. The power states of section 4a already carry these duties or bound them from above.

| Bearer or load | Planning duty | Carried in the model as |
|---|---|---|
| LoRa mesh | receive continuously; transmit airtime inside the EU cap of 10 % on 869.4 to 869.65 MHz at 27 dBm, and inside the stricter caps elsewhere in the band (REQ-054) | PS-TYP's 0.3 W against 3.25 W transmitting: about 9 % airtime; PS-BUSY at 100 %, a bound |
| APRS | a position beacon every 10 minutes at a fixed site; on the move at most one a minute; each about 1 s, never over K1's 60 s | PS-IDLE-SPEC's 0.9 W average on the PA rail, about 1.2 % of a 75 W key-down. It bounds the fixed site (0.17 %, about 0.13 W) but not the move at one beacon a minute (1.7 %, about 1.25 W), which the reduced mode's PS-RED2 therefore understates by about 0.35 W on the move, inside its HIGH figure (INFERRED; corrected 27 September 2026, Review A, m1: this cell said the 0.9 W bounded both) |
| Iridium (RockBLOCK 9704) | message driven: at most one session in 10 minutes in the normal modes; the SOS and queued traffic go first | PS-TYP's 0.1 W against 1.4 W: about 7 %; PS-BUSY at 100 % |
| 5G | registered; light traffic in PS-TYP; bulk transfers are PS-BUSY | 1.5 W in PS-TYP (5.59 W at LTE CA in PS-BUSY) |
| WiFi link | one card up and idle whenever a peer kit is linked (M3); traffic is PS-BUSY; the standby card held off by software | 4.0 W idle, 6.0 W in PS-TYP, 8.0 W in PS-BUSY |
| HF (deferred by D-01) | receive; a transfer transmits in bursts, never with the PA keyed on the pack alone (K4) | 0.96 W receiving; 12 W transmitting in PS-ALLTX |
| PS-BUSY as a whole | a bounded mode: it runs until C1 or C3 ends it | the 92.0 W sustained bound |
| The outlets | off unless the operator enables one; on the pack only inside C2's budget (PWR-F13) | off in every state; the outlet rows of `feasibility/POWER-THERMAL.md` section 7.1 |

**Simultaneity cases, for the power, thermal and runtime budgets:**

| Case | What is on | Power state and estimate (PROVISIONAL) | Source or status |
|---|---|---|---|
| S1 idle watch | three modules idle, radios receiving | PS-IDLE 39.7 W (monitor dimmed); PS-IDLE-SPEC 42.8 W (monitor on, APRS beacons) | `feasibility/POWER-THERMAL.md` sections 4 and 5; the 29 W "typical" of `V2-SPEC.md` line 23 was the single-module figure of 32.49 (line 2775) |
| S1b typical relay | three modules at typical operation, monitor on, SDR on, light traffic | PS-TYP 63.0 W, sustained on the pack while C1 allows it: at +20 C the cells sit at 43.8 to 45.7 C on 32.53's conductance and 45.4 to 81.3 C on the independent bound, so C1 sheds it at +20 C over part of that bound (section 4c) | `feasibility/POWER-THERMAL.md` section 7.1 |
| S1c typical relay with an outlet | S1b plus PoE or USB-C | PS-TYP plus PoE 100.4 W, plus USB-C 112.3 W, plus both 150.2 W: **bounded, not sustained** on the pack; C2 sheds USB-C then PoE on 9.0 A or a +50 C cell | `feasibility/POWER-THERMAL.md` section 7.1, PWR-F13 |
| S2 busy relay | three modules loaded, 5G and WiFi link passing traffic, Iridium and LoRa sending | PS-BUSY, a **bounded mode**: its sustained bound 92.0 W reaches C1's +55 C cell trigger at +20 C on every conductance in the record, so C1 ends it (how long it runs first is **TBD** until the heat capacities are measured) | `feasibility/POWER-THERMAL.md` sections 4 and 7.1, PWR-F13 |
| S3 every transmitter keyed | S2 plus the PA at key-down and HF transmitting, the outlets at their minimum contract (0 W, off) | PS-ALLTX 203.8 W, for at most 60 s per key-down above a 15.5 V rest voltage (D-11's declared values, REQ-018's pass lines since 27 September 2026; whether the chain meets them is FEA-004's); the outlets drop in hardware while the PA keys | `feasibility/POWER-THERMAL.md` section 7.2; owner ruling D-11 |
| S3b the PA keyed alone | the PA at key-down over PS-IDLE-SPEC or PS-TYP, the other transmitters' sends deferred | 122.4 to 184.0 W at the pack, 8.5 to 18.8 A between a 14.4 V and a 10.0 V stack: above the pack chain's 10 A continuous rating for most of the discharge, so a bounded key-down, at most 60 s, above a 12.4 V rest voltage | `feasibility/POWER-THERMAL.md` section 7.1, PWR-F14 |
| S4 operating while charging | S1 to S2 with shore or vehicle present | the front end regulates 20 V at up to 5 A (100 W, 32.55 line 2915), so S3 draws from the pack even on shore power; and the loads sit on the charger's system node, so shore carries them up to the charger's input limit (about 31 W before the host writes it) and the pack supplies above it (section 4, Charging) | inferred from the two numbers; input current limit **TBD** |
| S5 reduced | slots 2 and 3, monitor off (section 4c) | PS-RED2 31.4 W; the heat stage PS-SURV-R 23.3 W after BANK-R1, PS-SURV 21.7 W as generated | section 4c; `records/hc2/pwr_red2.out`; 32.53's "about 30 W with one module" (line 2860) is the lid-open, monitor-on figure, not the reduced mode |

## 6. Runtime and endurance

The runtime of `V2-SPEC.md` line 23 (8 to 9.5 hours typical) was computed for the withdrawn BB-2590/U pack
and is **not valid** for this kit. It divided the BB-2590's nominal energy by a battery-side figure with no
derating (29 W x 8 to 9.5 h is 232 to 276 Wh; 50 W x 5 to 6 h is 250 to 300 Wh). On the pack the owner ruled
(D-06: one 4S3P 18650 block of about 145 Wh, its fit designed against Peli's figures since D-08 was reversed), with usable energy, conversion
losses and a reserve applied, the PROVISIONAL figures of section 4a are (PWR-F07, `feasibility/POWER-THERMAL.md`
section 6):

- the state `V2-SPEC.md` describes (monitor on, radios idle, beacons), PS-IDLE-SPEC: about 3.2 h new and
  2.5 h aged (documented bounds 1.3 to 3.3 h aged);
- the typical state of 32.52, PS-TYP: about 2.1 h new and 1.7 h aged (0.9 to 2.3 h aged);
- the reduced mode (PS-RED2, section 4c): about 4.3 h new and 3.5 h aged; the heat stage: 5.9 h and 4.7 h after
  BANK-R1 (PS-SURV-R), 6.3 h and 5.0 h as board B is generated (PS-SURV).

These replace the W2 model's 4.2 and 3.4 h, 2.2 and 1.8 h, and the one-module reduced figures, which were computed
before the loads were sourced (section 4a).

**The runtime requirement (owner ruling D-06, 26 September 2026)** is stated as battery-only hours in an idle and
a typical mode at +20 C for an aged pack. The session takes PS-IDLE-SPEC and PS-TYP as those two modes, the pair
W1's decision table recommended, **under the owner's standing rule of 26 September 2026**. **"Aged" is 80 % of the
cell's specification minimum capacity** (3.35 Ah per cell, so 8.04 Ah for the 3P block), taken by the session under the
owner's standing rule (section 7a): it is the end of the pack's service in the kit, and the pack is replaced when
the gauge's learned full-charge capacity falls below it, so the stated hours hold for every pack the kit is allowed
to carry. The cell sheet's own floor, 60 % after 500 cycles (7.9), stays the lower bracket of section 4a. The
PROVISIONAL figures for an aged pack are 2.5 h (PS-IDLE-SPEC) and 1.7 h (PS-TYP); the required values stay **TBD as
pass lines** because they are measured on the prototype, and no published runtime may exceed the measured one
(REQ-014). They move with the undocumented share of each power state and with cold (the heater overlay and the cells'
reduced capacity). Missions longer than the pack rely on vehicle or solar input: M1 is set at 72 hours (section 3,
taken by the session under the owner's standing rule in place of the later setting D-06 reserved for the owner, whose
own setting replaces it), and section 3 shows that on pack and solar alone the kit does not carry it through a single
night, whatever the solar rating, because the aged pack bridges 2.5 to 5.0 h of darkness; the solar path's rating is
a second limit. Both are a layer-4 finding, reported to the owner as a consequence of D-06's one pack with the
session's 72 hours, not asked.

## 7. Owner questions and their rulings

Each question was asked one at a time with its evidence, options and a recommendation, and the owner took the
recommended option each time. The identifiers D-nn are those of the foundation's owner decision table
(MESHSAT-1357, `records/w1/w1-decisions.md`). D-01, D-02a and D-02b were ruled on 25 September 2026 (about 23:27 to 23:40 CEST); D-02c and every
later ruling of that sitting on 26 September 2026 (about 00:05 to 00:55 CEST). D-08a was ruled later on 26
September, and at about 09:30 CEST the owner reversed D-08, declining the measurement request that ruling had
answered (appendix 32.367). A ruling that sets a threshold or names a session
item leaves that engineering work to the session; until it is done, the requirements that depend on it carry TBD
with its effect, never an assumed answer.

| ID | Question | Status | The ruling |
|---|---|---|---|
| D-01 | Prototype scope | RULED 25 Sep | full design, staged acceptance on a named core; everything else built where possible and reported NOT_YET_TESTED (section 2a) |
| D-02a | Qualification margins | RULED 25 Sep | `TEST-PLAN.md`'s +55 C operation, +71 C storage (E3) and -33 C storage (E4) are qualification margins over the envelope's -20 to +40 C in use and -20 to +45 C in storage, with two pass lines: operate to specification inside the envelope; survive and recover at the margin |
| D-02b | Closed-lid operation | RULED 25 Sep | the kit operates with the lid closed in a defined reduced mode (the owner's example: GNSS, LoRa mesh, Iridium and APRS beacons, monitor off, one module); a closed-lid state and thermal test join `TEST-PLAN.md`; a lid sensor is an engineering item, and the case-open switch can serve both. Accepted consequences: above +35 C ambient the kit runs one module; with three loaded modules charging holds off above about +25 C ambient. **As ruled; carried since 27 September 2026 by section 4c, with choices taken by the session under the owner's standing rule of 26 September 2026 (section 7a), which are not part of the ruling:** the reduced mode runs slots 2 and 3, and the owner's example on one module is its heat stage, which board B carries once two of its hub ports are exchanged (BANK-R1; as generated no single slot hosts the example with the SOS path, a finding reported to him); past the heat stage the hot stop acts on the cells' measured temperature (section 4c); and, restated by the session, the two consequences are carried there as bounds on the current analysis (the kit sheds, and stops charging, at lower ambients than the figures the ruling was argued on); the ruling stands, and the changed figures are reported to the owner, not asked |
| D-02c | Severities and altitude | RULED 26 Sep | `TEST-PLAN.md` E1 (26 drops from 1.22 m) and E2 (composite wheeled vehicle profile, 1 hour per axis); altitude 0 to 3000 m in use and 0 to 4500 m in transport; service life **TBD** for prototype 1 |
| D-02d | Cold start from a cold-soaked pack | RULED 26 Sep | out of scope for the prototype, to be stated in the envelope and stated here: a kit cold-soaked below about -10 C at the cells needs shore or vehicle power, or warming, before it starts from the pack; once warm, use down to -20 C holds. No hardware is added |
| D-02e | Direct sun | RULED 26 Sep | "operate shaded" is a stated operating condition, with a shade accessory (a lid sun shield or a tarp); full-sun design is a later qualification item. No board change |
| D-03 | ZEROIZE: what it erases, what triggers it, what a power loss during the hold does | RULED 26 Sep | a crypto-erase through the secure element, the covered toggle held 5 s the only trigger, level-sensitive after a power loss, and the accepted residual risk that a drive unlocks at boot only through the secure element, the panel controller and the kit I2C bus (section 4, ZEROIZE row). Firmware and provisioning, no board change; the secure element's erasable slot map is a precondition still **TBD**. Decision 30 is ruled by it |
| D-04 | Markets and obligations | RULED 26 Sep | a non-commercial prototype in the Netherlands and the EU, operated by a licensed radio amateur; no CE or RED conformity marking claimed and no EMC claim yet, so every MIL-STD-461 run is characterisation; the design keeps an EU route open. Every transmitter is to be configured to the operator's licence and the EU limits, the VHF path gets a band lock, and the pack's transport route is stated (section 4, Transport row; UN 38.3 status unknown). What the row states since its correction of 26 September 2026 is that no route is claimed acceptable until the pack's classification, conditions or applicable exception are established (section 7a) |
| D-05 | EMCON meaning | RULED 26 Sep | radios dark, as generated and completed: every radio with an emission path powered off or RF-disabled in hardware; VHF keeps listening (transmit-only gate); GNSS, DCF77 and lightning continue. The gap fixes (the compute modules' radios onto the line, the WiFi link cards' disable shown to act or their supplies gated) are session work (section 4b) |
| D-06 | Pack size and runtime target | RULED 26 Sep | one 4S3P 18650 (Samsung INR18650-35E) pack of about 145 Wh, shrink-wrapped in the east pocket, subject to the case measurement (answered from Peli's own figures after the D-08 reversal: `CASE-MARGINS.md` M4a to M6, with M4b and M6 MET and M4a and M5 OPEN until the pack's hold-down and the targeted mock-up before boards A and P enter layout); missions longer than the pack rely on vehicle or solar input; the runtime requirement is battery-only hours in idle and typical modes at +20 C for an aged pack (section 6); the mission duration for the solar energy balance is set later by the owner. Session items: a lower charge setting for cell life, and `pack_4s.py` redesigned. **Since 27 September 2026** the mission duration is taken by the session at 72 hours under the owner's standing rule, in place of his later setting, which replaces it whenever he gives one (section 3, M1); "aged" is 80 % of the minimum capacity (section 6); on the one pack this ruling sets, the kit does not hold M1 through a night on pack and solar alone (section 3), a consequence reported to the owner, not asked |
| D-07 | 5G antenna jacks | RULED 26 Sep, conditional | three jacks (ANT0, ANT2, ANT3), making twelve bulkheads, at the board A site found free (X +46), if the case measurement confirms that site and the board E clamp fit; otherwise two jacks on ANT0 and ANT2. The case half is laid out from Peli's own figures after the D-08 reversal (the third jack is one of five arrestor bulkheads on the east wall's RF entry plate, at Y 0 and Z 59, between 5G DIV (Y -31) and IRIDIUM (Y +31); that wall's margins and its jumpers' planned route are in `CASE-MARGINS.md` section 3.4, where the jumpers' layering under the east plugs stays OPEN until the plug is picked); the board E clamp fit remains a board item. The key-M socket is replaced by a key-B part either way (session) |
| D-08 | Measuring the owner's Peli 1450 and building a mock-up | RULED 26 Sep, REVERSED 26 Sep about 09:30 | no owner measurement and no mock-up. The owner: "you have the CAD files and all the measurements why do you need from me to measure an old case?" The design computes every case-dependent margin against the worst of Peli's own figures (drawing 1451-931 of 15 January 2025, the STEP bodies, frame sheet 1453-314-000, the pelican.com page), plus a stated minimum, and marks OPEN what rests on a tolerance no source states (`CASE-MARGINS.md`); the OPEN margins, the seals and the stack-up are shown on hardware, on a targeted unpowered mock-up the session recommends for the build stage in a new case of the current moulding. The first ruling answered a request the session had written (W4); it had the owner measure his case (about 1 hour) and build a cardboard mock-up (2 to 3 hours), and buy the 1450PF frame later, before the face plate is final |
| D-08a | Which moulding the design targets | RULED 26 Sep | the current 1450 moulding of Peli's 1451-931 customer drawing dated 15 January 2025. The owner: "if it is older i will buy another newer case": the design never adapts to an older moulding, and a new 1450 is bought if the build case is older |
| D-09 | Independent review and test route | RULED 26 Sep | the SIDN voucher goes to a ZEROIZE and key-fill security review; a paid battery-and-protection review by a qualified electronics engineer before the pack is built; an EMC pre-compliance session once the prototype exists. The session prepares the packets and requests; nothing is spent beyond the voucher without a quote and the owner's approval |
| D-10 | SOS | RULED 26 Sep | a distress message with position over the available bearers (Iridium first when nothing else is up) to a configured recipient list; never through EMCON: under EMCON the message is queued and the operator is told. Firmware only |
| D-11 | Peak simultaneity | RULED 26 Sep | every radio may still transmit at once, for a declared key-down time above a declared state of charge, with the outlets at their minimum contract; the session sets the thresholds from the fuse and gauge limits and adds a hardware interlock that drops the outlets while the PA keys (section 5) |
| D-12 | External USB data port | RULED 26 Sep | the wall data path is routed to the sealed Glenair 233-370, which is also the console and key-fill port; the USB-C becomes a power-only outlet |
| D-13 | Firmware integrity and the supervisor part | RULED 26 Sep | software-verified boot on the STM32H743 supervisors (and on the compute modules if Raspberry Pi documents it) is the prototype's floor; a hardware root of trust is required at a production trigger. The H743 is accepted; the component mismatch with the STM32H753 in the schematic closes only when the schematic text and the BOM are aligned to the H743 and regeneration parity has been shown again |
| D-14 | Lifting the stack with the pack connected | RULED 26 Sep | the procedure (kit off, pack XT60 unplugged, shore removed) plus an insulating cap over the dock block E5 while the stack is out; lifting live is an accepted, recorded residual risk; a hardware stack-present interlock is studied at Review D |
| D-15 | Cell under-voltage on the gauge's firmware (decision 40) | RULED 26 Sep | a 4S secondary protector that also covers cell under-voltage if one can be sourced near the cost of the over-voltage-only part; otherwise firmware under-voltage with a data-flash verification at commissioning. The session floor either way: the over-voltage secondary protector, a chemical fuse, the BQ4050's FUSE output and its PTC input |
| D-16 | Vehicle surge claim | RULED 26 Sep | no vehicle surge claim for the prototype; the entry is recorded as not qualified, with a warning against 24 V military vehicle buses; MIL-STD-1275 is revisited only if military vehicles become a market |
| D-17 | Board A's USB-C CC pins (decision 31) | RULED 26 Sep | an external low-capacitance ESD array at the CC pins by the connector, riding on the board A update already owed |
| D-18 | IP68 fans | OPEN, conditional | it arises only if Delta's 40 mm IP68 fan does not fit the coolers; if it does, the session settles it under the owner's standing rule of 26 September 2026 (section 7a) and records the option it takes. The sealed case's thermal path waits on it. **This layer does not wait on it:** no mode, trigger or behaviour here changes with the fan part; a stopped fan is a fault of section 4e, and the fans-on conductance every thermal row assumes is what the empty-case heat-balance test measures (FEA-004). The fit check against the fan's and the CM5 Cooler's drawings is the parts stream's, the fan's drawing still to be filed under `v2/vendor/` |

The board-level decisions 27 (board C on six layers), 28 (board P on four layers at 2 oz), 41 (the order set
rebuilt and quarantined) and 43 (board B measured on eight layers first, its whole-board run EXPERIMENTAL) were
ruled by the owner on 25 September 2026 (appendix 32.365). They change no need, mission or mode here.

On the evening of 25 September 2026 the owner also ruled that the foundation documents (the product brief, this
concept of operations, the requirements and the decision table) are written directly into the public repository's
`v2/docs/`, not into a private draft area first (owner ruling `public-docs` of the requirements registry, recorded
on 27 September 2026). It changes no need, mission or mode here.

### 7a. Choices the session took under the owner's standing rule of 26 September 2026

On 26 September 2026 the owner ruled that he is not to be asked further questions: where a choice is left, the
session takes the option the evidence recommends and records it as its own, so that it can be reversed. Each
choice below was taken that way; a choice later corrected or withdrawn keeps its row, marked and dated. Rows seven
to nine are the case choices of `CASE-MARGINS.md` section 4, taken after the owner reversed D-08 (section 7). The rows
after them were taken on 27 September 2026 to close this layer; each is also a session choice record in the
requirements registry (its SC number is the registry's), and each says how it is reversed. Rows marked **pass 2**
were taken, or changed, later that day to answer the first pass of Review A (`reviews/REVIEW-A-LAYER-2-2026-09-27.md`);
rows marked **pass 3** answer its second pass and the ConOps side of Review B of layer 3
(`reviews/REVIEW-B-LAYER-3-2026-09-27.md`).

| Choice | Taken | Why | Where |
|---|---|---|---|
| Does SOS join prototype 1's core? | yes | D-10 defines its action as firmware only, and W1's decision table recommended it for the core | section 2a |
| Which peripherals NEED-03 protects (SC-02, settled about 11:35 CEST) | every USB peripheral `ARCH-PCB-B-IOHA.md` section 15 traces, and the kit-to-kit WiFi link; the LoRa module and cellular data are NAMED EXCEPTIONS for prototype 1, as `ARCH-PCB-B-IOHA.md` sections 15 and 15a and appendix 32.366 record | making either critical needs a second LoRa site or the 5G module on USB 3, and both change board B's floor plan, the board that is not routed; without them the kit is designed to keep at least three of the four messaging bearers through the loss of any one module. **Corrected 26 September 2026:** this row first recorded the two as open gaps, because the owner's requirement names no exception, which contradicted section 15a and appendix 32.366 | section 2a |
| Are the qualification tests (NEED-06, 07, 15, 17, 18) outside the core? | yes, except where a requirement is a condition of a core function | D-01 names the core and says the rest is reported NOT_YET_TESTED; D-02a and D-02c set how those tests pass when they run | section 2a |
| The two modes of the D-06 runtime requirement | PS-IDLE-SPEC and PS-TYP | the pair W1's decision table recommended with D-06 | section 6 |
| The pack's transport route (D-04) | **WITHDRAWN 26 September 2026:** no route is claimed; the pack's classification, the conditions that apply to it or an exception that applies are to be established before any transport route is claimed acceptable (**TBD**, a bounded item, not a broad compliance project). The choice first recorded here was by road with the kit, as the operator's own equipment, with air or parcel carriage waiting on a UN 38.3 test summary | that choice read the pack's unknown UN 38.3 status as leaving road carriage open, and it does not: road carriage has its own dangerous-goods rules (the ADR; review of 26 September 2026, `reviews/2026-09-26-foundation-progress-review.md` section 5, reference R5). The pack is to be built for the kit, not bought, and has no test summary. The 4500 m transport ceiling of D-02c stands as ruled; W1's question tied it to no carriage in an unpressurised aircraft hold | section 4, Transport row |
| How the face plate mounts in the 1450PF (C1) | on the frame over Peli's o-ring, screwed from above into Peli's 6-32 inserts, as Peli documents | the as-coded plate under the frame's ring puts the monitor about 8 mm into the compute module heatsinks when the frame sits where Peli puts it | `CASE-MARGINS.md` C1 |
| What sets the frame's height (C6) | four setting legs bonded under the frame's ring by a locator in each window corner, standing on the floor, placed by the frame's centring with wedges before Peli's four screws are driven; pad top 94.13, face top 106.52 | Peli's ribs catch the frame by 0.012 mm at nominal, so its rest spans 11.9 mm on the frame's published tolerance alone, twice the 5.96 mm window the monitor and the lid leave; legs bonded to the floor by hand would have nothing to locate them | `CASE-MARGINS.md` C6, section 2.7 |
| Antenna bulkheads, connector plate, RF entry plates, lid tray (C2 to C5) | the ruled gas-discharge arrestors (PolyPhaser GTH-SFF-AL) are the twelve antenna bulkheads, five on the east wall and seven on the west (the two WIFI P2P moved west, so that every jumper has a planned route past the pack and the setting legs) at a 31 mm pitch and Z 59, bodies outside, on one 6 mm aluminium RF entry plate per end wall that is also their common ground; one 114 x 68.3 x 5 connector plate between the hinge fairings carrying all six ruled items, the sealed RJ45 picked to a MIL-DTL-38999 shell 15 envelope rated for the 54 V PoE feed; the QMX tray 1.5 mm west | each is laid out against the case features Peli's files show, at the worst of Peli's figures, with every margin MET or OPEN in `CASE-MARGINS.md` section 3.2 and none NOT MET; how the east jumpers lie under the plugs stays OPEN until the plug is picked; the arrestors were ruled but had no place, and inside the case their bodies meet the frame skirt and the tall parts at the board's edge; the recommended RJ45 coupler is too large for the wall and rated 42 V | `CASE-MARGINS.md` C2 to C5 |
| The reduced mode (S-24, CFL-011); **pass 2** | slots 2 and 3, monitor off, both WiFi link cards off, the 5G module idle, APRS beacons; entered on the lid switch, C1, C3 or the operator; a kit started with its lid closed starts all three modules and enters it once the lid is read (section 4c) | as board B is generated no single slot hosts the owner's example with the SOS path, and slots 2 and 3 are the pair that also keeps 5G; after BANK-R1 one module can carry the example, and that module is the heat stage, while the reduced mode keeps two so that 5G stays. The one departure from the example (two modules, not one) is stated in section 4c. Reverse, once BANK-R1 is in board B, by making the reduced mode slot 3 alone (the example as the owner worded it, without 5G) | section 4c; Reduced row |
| The heat stage; **pass 2** | one module carrying the owner's example with the SOS path when C1's triggers are reached again in the reduced mode: slot 3 once BANK-R1 is in board B, slot 2 until then; the reduced mode restored at most once in 30 minutes (a planning value); **pass 3:** past it the hot stop (the next rows), which replaces "no further stage (the gauge's discharge window ends it on the pack)"; as generated, the pack's voltage and current read from the charger in place of the gauge's readings, and the outlets held off | D-02b accepts one module above +35 C and REQ-052 asks the example set at the hot edge with the lid closed, which is kept rather than restated to fit the generated board; slot 2 is the only single slot of the generated board that keeps the SOS path with a live position, and its losses (the LoRa mesh, APRS, the gauge's readings, 5G's USB link) are stated in full. Reverse, until BANK-R1 lands, by naming slot 1 (it keeps the gauge's readings and APRS but loses the live position and boots a module first) | section 4c; Heat stage row |
| BANK-R1, a board B design item; **pass 2** | two exchanges of hub ports on board B, the RockBLOCK with the QMX (port 4 of banks 1 and 2) and the panel controller with the sealed wall USB port (bank 1 port 2, bank 3 port 3), so that slot 3 alone carries the owner's example with the SOS path; owed by board B's owner before its layout entry, from the hand-off's proposed generator change; until it is in the generator, REQ-052 is not met by board B as generated, a finding reported to the owner | REQ-052 is kept at the owner's set (Review A, B5); the exchange keeps `ARCH-PCB-B-IOHA.md` section 8's rule of one long-range bearer per bank and three of D-01's four bearers through any one module loss, adds no part and moves nothing, and board B is not at layout entry. Reverse by keeping the generated allocation and reporting REQ-052 as not met, a trade the owner then rules (his example against section 8's rule, if no exchange keeps both) | section 4c |
| A start-up with the lid closed; **pass 2** | the panel controller raises all three slots at every start-up; the bridge sheds to the reduced mode once it reads the lid from the sensor controller | the panel controller has no lid state before a module runs (the reed is the sensor controller's alone, Review A, B2); this asks nothing new of the supervisors or the panel and costs under 1 K of inside air. Reverse by a lid line from the sensor controller to the panel controller, a layer-5 interface item on boards E and C | section 4c; Startup and Reduced rows |
| Storage and transport (CFL-017, S-43, REQ-025, REQ-069) | the kit is stored and carried with its pack fitted, every input unplugged and the pack in the gauge's shutdown (which it enters only with no charger present), and for storage at the cells' ex-factory state (3.49 to 3.69 V per cell); in that state the lid and tamper log does not run and the kit starts only on an input (pass 2, Review A, m5); a kit operated in a vehicle runs the reduced mode, a use state, not transport; D-02a's storage margins run on the kit less its pack and on the pack at its cells' limits, and the stored product's result is finding BAT-F19; no transport route is claimed | the product need, not what a test can pass (second checkpoint review, item B): the pack is bonded under the stack and comes out only by D-14's service lift, a field kit is kept ready to deploy, and the envelope's storage limits are the pack's own. It supersedes the storage clause of the battery stream's round-8 choice (pack out, read from the earlier session text of `TEST-PLAN.md` and this document), and keeps the rest of that choice. Reverse by ruling that a stored kit has its pack out, which needs a pack-removal procedure short of the stack lift | section 4, Transport and Storage rows; `TEST-PLAN.md` sections 1 and 6 |
| M1's mission duration (L-02); **pass 2** for the finding | 72 hours, on the PS-IDLE-SPEC energy basis | the planning horizon of a relay site set up where there is no infrastructure, chosen from the use case (not a sourced figure); D-06 left it for the owner to set later and the standing rule forbids asking. On pack and solar alone the kit does not carry it through a single night on D-06's one pack (the binding limit; Review A, B3), and the solar path's rating is a second limit: a layer-4 finding reported to the owner with its routes (an overnight input, D-01's deferred second pack, a larger pack), not a shorter mission. Reversed by the owner's own setting | section 3, M1 |
| The planning duty profile | section 5's table | the budgets and REL-001 need one; each duty sits inside the model's own planning figure or bounds it. Replaced by measured duty after bring-up | section 5 |
| "Aged" (S-26) | 80 % of the cell's specification minimum capacity; the pack is replaced below it | the stated hours then hold for every pack the kit may carry; the cell sheet's 60 % after 500 cycles stays the lower bracket. Reverse by taking 60 %, which moves the aged hours to 1.9 h and 1.3 h | section 6 |
| D-11's outlet minimum contract | 0 W: the outlets off | it is what the hardware interlock does and what the power analysis assumes. Reverse by a non-zero contract, which re-derives the D-11 floors | section 5 |
| Recovery and delivery targets (REQ-004, S-37, NEED-02); **pass 2** for the definitions | 30 s per moved device plus its maker's start-up, "back in service" being `ARCH-PCB-B-IOHA.md` section 7 step 12; the bridge's own service back on a surviving module within 60 s; a bearer declared down after 60 s with a hand-off pending, its queue moved within 10 s; the kit's own hand-off within 10 s; end to end measured as characterisation | a required bound is a product decision and the hardware only measures it; the end-to-end time is set by networks outside the kit. Reverse by other bounds | section 4c |
| Graceful shutdown on the pack; **pass 2** for the heat stage | at 5 % relative state of charge, or the lowest cell at 3.00 V under load for 10 s; in the heat stage as board B is generated, the pack voltage the charger reads at 12.8 V or less under load for 10 s | above the cell's 2.65 V cut-off and the gauge's 2.50 V trip, with the 5 % reserve the runtimes keep. Re-derived at bring-up | section 4c; Shutdown row |
| The two parts rated from 0 C (PWR-F09); **pass 2** | the cold warm-up: while the inside air is under 0 C and the WiFi link cards or the SDR are wanted, the pack heater runs and the three modules are loaded, and the cards and the SDR are powered from 0 C; an extended-grade card and SDR sought in layer 6 as the route that removes the failure, decided before board B's layout entry if a socket or supply changes; the NVMe picked at a -20 C grade | the kit's own heat in its idle and typical states does not bring the air to 0 C at -20 C on the design record's conductance (Review A, B7); the warm-up does, up to about 3.6 W/K, and above that the link is lost at -20 C, which stays open in layers 4 and 6 with E4-O's pass line kept. It keeps the -20 C envelope for the rest of the kit, as the e-paper's carve-out does. Reverse by an extended-grade part, which removes the warm-up's reason | section 4c; `OPERATING-ENVELOPE.md` sections 2 and 4 |
| Pollution degree (ISO-001) | 2, inside the case | the case is sealed but opened in the field and its interior can see brief condensation (E5); degree 2, which admits occasional temporary conductivity from condensation, is the conservative reading of a sealed case that is opened (IEC 60664-1 is paywalled and not in this tree, `pcb_rules.yaml` ISO-001, so the definitions are the session's reading, to be checked against the standard when it is held). Reverse by a measured dry interior | `OPERATING-ENVELOPE.md` section 5 |
| REL-001's duty cycle | the planning duty profile of section 5, M1's 72 hours as the reference use | REL-001 needs one; the service life stays TBD for prototype 1 (D-02c), so REL-001 still has no life to judge against | `OPERATING-ENVELOPE.md` section 5 |
| SOS, ZEROIZE and lamp-test indications (S-32's operator half, S-19, S-39) | as `PANEL.md` section 9 sets them | D-10 and D-03 leave the indications to the session; the lamp test lights seventeen indicators, the sixteen LEDs D1 to D16 and the PI ring | `PANEL.md` section 9 |
| Water and gas on the floor and in the battery bay | the modules shut down, the inputs inhibited and the pack put in the gauge's shutdown, with the operator told first | a leak or a venting cell is a reason to isolate the energy store; the threshold and the path stay REQ-042's | section 4e |
| The hot stop, past the heat stage (Review A's second pass, P2-B2; Review B of layer 3, B1); **pass 3** | on the pack's measured cell temperature, in every mode and on every input state: H1 at +56.5 C sheds the kit to its minimum load (every module shut down cleanly, the switched loads and the charge held off), H2 at +57.0 C shuts the kit down by `PI_KILL`; released at +46.5 C, H1 by the panel controller at most once in 30 minutes, H2 by the operator's MAIN; the sensor controller detects and the panel controller acts (firmware), with board B's TMP117 at +55.0 and +56.0 C as the stand-in when the sensor controller is lost; PROVISIONAL thresholds | at the recorded low conductance the heat stage leaves idle cells on an input at about the inside air, above the maker's +60 C, with only destructive backstops behind it; H1 and H2 sit 1.0 and 0.5 K under the gauge's OTD in the same reading and 1.43 and 0.93 K inside +60 C after the battery packet's published budget of 2.07 K. Reverse by other thresholds (measured ones replace these at bring-up) or by a hardware stage that makes a step redundant; removing the stop reopens the cells' exposure | section 4c; Hot stop row; `TEST-PLAN.md` E3-H |
| HOT-R1, a board A and board E design item; **pass 3** | the sensor controller drives the dock's spare contact (board E's `J_BLK` pin 12 to board A's `J_DOCK` pin 12, which already lands on the expander `U27`'s input and so on `EXP_INT`) through an open-drain 2N7002, and board A pulls it up with 10 k; four states on the line (1 Hz: read and below H1; 5 Hz: H1; low: H2; high: the detector lost); owed before the layout entry of boards A and E, with the dock contract's pin 12 and the two firmware contracts; until then the hot stop's requirement reads FAIL on the generated boards, a finding reported to the owner | as generated the cells' temperature reaches the panel controller only through the bridge on a module that hosts bank 3, which the heat stage as generated does not have and which H1 itself stops; the spare contact and the expander input exist, so the change is one GPIO, one transistor and one resistor, no part number new to either board. Reverse by a USB-only path, which leaves the heat stage as generated without the stop and H1 without its release | section 4c |
| A non-destructive hardware stage behind the hot stop; **pass 3** | not taken: recorded as an open design question for the D-09 reviewer (a firmware-free comparator on the hottest cell taking board A's `KILL` low), decided before the layout entry of boards A, E and P | the packet's own hardware hold (Q-P15) removes no heat on an input, and whether a second, firmware-free stage is needed is a protection-architecture judgement, not a measurement this tree can make; the requirement it would serve is set | section 4c |
| The NVG mode's compatibility target (Review B of layer 3, B3); **pass 3** | MIL-STD-3009, Type I, Class B NVIS, judged by the standard's own examination (5.7.2): the goggle resolves the same line of the 50 % NVG chart at 20 ft with the kit's NVG lighting on as with every light off, and no light leak is seen; no claim until it has passed | D-01 defers the claim, not the design; Class A is by the standard's words incompatible with red lights and the owner ruled the NVG light red (32.50 item 16c). Reverse by naming Class A (a change of the NVG colour) or another criterion | section 4, NVG row |
| The lightning mast-down alarm (Review B of layer 3, B2); **pass 3** | MASTER WARN when the AS3935 reports a lightning event at 10 km or less; cleared after 30 minutes with none at 10 km or less; it informs and switches nothing | the owner approved the detector with a mast-down alarm and set no level; the sensor's factsheet quotes the 30-30 rule (a storm within 10 km, shelter for 30 minutes after the last thunder). Reverse by another distance or hold | section 4e |
| M1's solar window and design month (REQ-016 and REQ-072 of the requirements registry; Review B of layer 3, B4 and B5); **pass 3** | the window board E's generator declares: at most 25 V open circuit at the panel's coldest, 17.6 V held, at most 100 W; the balance judged on the mean day of September at Leiden (4.0 kWh/m2 on the optimally inclined plane, PVGIS) as the design month, with no season taken off M1 | the generator's own declaration, against which the entry's parts are judged, and a public irradiation record; a season clause that the registry's first text carried would have narrowed M1 in a session choice alone, and is withdrawn. Reverse by re-declaring the entry and judging its parts again, or by another site or month | section 3, M1 |
| Review A | one fresh reviewer, recorded under `v2/docs/reviews/`, labelled AI review, never a qualified review | the audit found the gate undefined; the owner's prompt allows an agent to check usability and consistency and keeps qualified reviews separate | the status paragraph at the top |
