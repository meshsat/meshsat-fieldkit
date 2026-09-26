# MeshSat field kit V2: concept of operations

**Status: DRAFT for Review A of the foundation baseline (MESHSAT-1357), written 25 September 2026, revised the
same day after an independent challenge, and revised on 26 September 2026 to carry the owner's rulings D-01 to
D-17 of 25 and 26 September 2026 and the choices the session took under the owner's standing rule of 26
September 2026; section 7 lists every question with its ruling, and D-18, the one still open and
conditional. Corrected later on 26 September 2026 (appendix 32.367): the owner reversed D-08 at about 09:30 CEST
and D-08a stands (section 7), the session settled SC-02 at about 11:35 CEST (section 2a), and the pack's
transport route follows the review of that day (section 4, Transport row).** Prototype design.
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
baseline, so they are cited by section rather than by line. Where two sources disagree, this document says which
one it follows and why, and the disagreement is carried in the foundation's conflict list (MESHSAT-1357, a working
draft of the baseline that is not published in this repository) until it is resolved; the conflicts that bear on
a requirement are also carried as conflict records in the requirements registry `v2/ecad/tools/pcb_requirements.yaml`.

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

### M1. Remote site relay on pack and solar (duration TBD)

**Setting:** a team at a place with no infrastructure. The kit sits on a table or a vehicle tailgate, lid open,
shaded, antennas on the end-wall jacks, a solar panel on the solar input. **Operating shaded is a stated operating
condition (owner ruling D-02e, 26 September 2026)**, with a shade accessory, a lid sun shield or a tarp: a black
plate in full sun absorbs about 60 W, more than the electronics (32.53), and full-sun operation is a later
qualification item. **Sequence:** deploy; start up; the local team's Meshtastic handhelds join the LoRa mesh;
outbound messages leave over the bearer the MeshSat routing layer picks by cost (free bearers first, metered ones
such as Iridium only when nothing free is up; the Bridge README); inbound messages are shown on the monitor, the
MSG lamp and the e-paper; by day the pack charges from solar while the kit runs; at night the panel goes to NIGHT
lighting. **Must hold:** a message typed on a handheld reaches a remote correspondent over at least one bearer
(NEED-01, NEED-02); the kit keeps running on its pack plus solar for the mission's duration (NEED-05). The
duration is **TBD**: no source in this tree states one, and D-06 leaves the mission duration for the pack-plus-solar
energy balance to the owner. The battery-only runtime per power state is PROVISIONAL (section 6), and the solar
yield is not in the record. The pack gauge holds charging off when the cells are outside their temperature window
(NEED-13). **Consequence accepted by the owner (ruling D-02b):** with three loaded modules and the lid open the
inside air is estimated at ambient plus 16 K, so charging holds off above about +25 C ambient
(`OPERATING-ENVELOPE.md` section 3), and the kit charges freely only in temperate conditions or in the reduced mode.

### M2. Vehicle move with position reporting

**Setting:** the kit travels in a vehicle, powered from the 9 to 36 V vehicle input, lid closed. The input
carries no vehicle surge claim and is not for 24 V military vehicle buses (owner ruling D-16, section 7).
**Sequence:** the kit runs in the reduced mode (32.53: closed-lid operation is the reduced mode); GNSS keeps
position and time; APRS position beacons and LoRa mesh traffic continue over the end-wall antennas if they
are fitted. **Must hold:** vehicle power runs the kit and charges the pack inside its window (NEED-05);
vibration does not loosen a fastener, connector or pigtail (NEED-06, `TEST-PLAN.md` E2, the severity D-02c rules).
**Ruled (D-02b):** the kit operates with the lid closed in a defined reduced mode; the owner's example is GNSS,
LoRa mesh, Iridium and APRS beacons, monitor off, one compute module. A closed-lid state and a closed-lid thermal
test join `TEST-PLAN.md`, which today defines only three states (transit with antennas off and cables out,
deployed, stored). **Still open:** the exact bearer set of the closed-lid mode and its thermal proof are
engineering items, as is a lid sensor (section 4, Reduced row). Whether the kit is powered at all in transit is
**TBD** (effect: PS-OFF against a reduced state for the whole move).

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
is about to be lost, ZEROIZE. **Must hold:** no transmitter emits while EMCON is closed, with no software involved
(NEED-08); nothing lights or sounds in blackout (NEED-09); ZEROIZE destroys the secure element's wrapping key as
ruled in D-03 (section 4, ZEROIZE row; NEED-10).
**Ruled (D-05, 26 September 2026): radios dark.** Every radio with an emission path is powered off or RF-disabled
in hardware; the VHF path keeps listening because its gate is on the transmit side only; GNSS, DCF77 and the
lightning sensor continue. The kit therefore stops RECEIVING on every other radio while EMCON is closed. As
generated, two gaps remain, and closing them is session work under the ruling: the three compute modules' own WiFi
and Bluetooth are not on the EMCON line at all, and whether the two WiFi link cards obey their disable pin is not
established. NEED-08 is not met for those radios until the design closes both.

### M5. Degraded operation during a mission

**Setting:** any of M1 to M4, when something fails or the weather turns. **Sequence and outcomes, as designed:**
one compute module stops: its I/O bank moves to its neighbour under 2-of-3 voted control (bank 1 to slot 2, bank
2 to slot 3, bank 3 to slot 1, per `gen_sch_b.py` line 543 and `ARCH-PCB-B-IOHA.md` section 4) and k3s
reschedules the workload; the two bearers with no second path go with their slot (the LoRa module on slot 3's
SPI, cellular data on slot 2's PCIe lane; `ARCH-PCB-B-IOHA.md` section 15), which section 2a records as the named
exceptions to NEED-03 for prototype 1 (SC-02); a slot whose heartbeat stays flat for 60 s is power-cycled once and then left off until the
operator acts (`PANEL.md` section 5); above +35 C ambient the kit drops to the reduced mode, which runs one module
(the consequence the owner accepted with ruling D-02b), so it has no compute redundancy left in the heat (the
session's inference from that consequence); below -15 C the e-paper updates slowly or not at all; below 0 C at
the cells the pack gauge holds charging off until the pack is warmed. A kit that has cold-soaked below about -10 C
at the cells does not start from its pack: cold start from the pack is out of scope for the prototype (owner
ruling D-02d), so it needs shore or vehicle power, or warming, first; once it is warm and running, the in-use
envelope down to -20 C ambient applies. **Must hold:** a single fault degrades a capability, never removes every
path (NEED-02, NEED-03), and the operator is told (MASTER CAUT or MASTER WARN, the e-paper).

## 4. Operating modes

"Guarantee" says what is designed to hold the mode: **HW** means a hardware line that holds with every processor dead,
**FW** means firmware on the panel or sensor controller, **SW** means software on the compute modules.
The table has fifteen rows: the fourteen of the first draft and SOS, added in the revision. "Power state"
points to section 4a.

| Mode | Entry | Exit | Running | Off or held | Guarantee | Power state | Source | Open |
|---|---|---|---|---|---|---|---|---|
| Transport | lid closed and latched, antennas off, cables out, pack fitted | deploy | nothing required; pack protection always | everything else | pack gauge (its own firmware); the floor of owner ruling D-15 (a 4S secondary over-voltage protector with a chemical fuse, the gauge's FUSE output and its PTC input; as generated board P fits no chemical fuse and holds PTC disabled, `gen_sch_p.py` line 11); the 25 A blade | PS-OFF if unpowered | `TEST-PLAN.md` line 8 | whether the kit is powered in transport (PS-OFF against a reduced state); altitude ruled 0 to 4500 m in transport and 0 to 3000 m in use (owner ruling D-02c). The pack's transport route (owner ruling D-04): **TBD**. The pack is built for the kit rather than bought and its UN 38.3 status is unknown, and an unknown status permits no route by itself: road carriage has its own dangerous-goods rules (the ADR, which the Dutch ILT names for road consignments; review of 26 September 2026, `reviews/2026-09-26-foundation-progress-review.md` section 5, reference R5), as air and parcel carriage have theirs. The pack's classification, the conditions that apply to it or an exception that applies are to be established before any transport route is claimed acceptable; that is a bounded item, not a broad compliance project. **Corrected 26 September 2026:** this cell had stated a road route with the kit as the session's choice, inferring from the unknown status that carriage by road was open where air and parcel carriage were not (no transport regulation is held in this tree); that inference is withdrawn (appendix 32.367) |
| Deploy | operator opens the lid, fits antennas, connects cables, shades the plate (D-02e) | startup | none | none | operator | PS-OFF | `TEST-PLAN.md` line 8 | none |
| Startup | MAIN PWR held (hardware lead to board A's power controller) | normal, reduced or degraded | board A's 3.3 V and the shared device rail come up; the panel controller boots, reads `ZEROIZE_HW` and completes any pending wipe (D-03), then raises `SLOT_EN1..3`; LED rail dark until firmware is up; `SHORE_INHIBIT` low | every slot stays off until the panel controller raises its enable (pull-downs on board A); a slot with a flat heartbeat after 60 s is marked faulty, cycled once, then left off | HW power path, FW slot enable and supervision | transient | `PANEL.md` sections 3, 5, 6 and 10 | cold start from a pack below about -10 C at the cells is out of scope (D-02d); as generated the device rail's enable rests on an I/O expander's internal pull-up that no datasheet limit guarantees, and two pins are pulled to the pack voltage (up to 16.8 V) above their rated maximum: the power controller's KILL input (7 V, LTC2954) and the 3.3 V buck's EN (6 V, TPS62933), `gen_sch_a.py` lines 172 and 434; until the panel firmware writes board A's expander, the PA and HF software enables and the charge inhibit sit between logic levels, and the monitor, heater and mezzanine enables are asserted; the monitor and heater eFuses lock out above about 12.9 to 13.4 V of the pack (100 k over 10 k against the TPS2596's 1.17 to 1.22 V threshold, `gen_sch_a.py` lines 526 to 528, SLVSET8A), so both are dark over most of the pack range: engineering fixes owed; rail sequencing, inrush and hot-plug bounds (rule PWR-002): **TBD** |
| Normal (full) | startup with three modules, lid open, ambient at or below +35 C | any other mode | three modules, monitor, every bearer available, sensors | none | SW | PS-IDLE to PS-TYP, bursts to PS-ALLTX inside the bounds of D-11 | `OPERATING-ENVELOPE.md` section 4 | busy-relay duty cycles (PS-BUSY): **TBD**; the declared key-down time and state-of-charge floor of D-11: **TBD**, set by the session from the fuse and gauge limits |
| Reduced | lid closed, or ambient above +35 C | conditions clear | one module (envelope) | monitor off and the cluster idle (32.53) | SW | PS-RED 19.7 W or PS-RED-b 25.4 W, PROVISIONAL | `OPERATING-ENVELOPE.md` section 4; appendix 32.53 line 2860 | closed-lid operation in a defined reduced mode is ruled (D-02b); the owner's example (GNSS, LoRa mesh, Iridium and APRS beacons, monitor off, one module) is PS-RED; the exact bearer set and its thermal proof are engineering items, with a closed-lid state and thermal test to join `TEST-PLAN.md`; a lid sensor is an engineering item (the case-open switch of 32.50 item 6 can serve both) and neither is in any generator yet |
| Charging | shore, vehicle or solar present, the panel controller has configured the charger, and the pack gauge reports the cells inside their charge window | input gone, inhibit asserted, pack full | the BQ25731 charger regulates into the 4S node; the kit's loads sit on the pack side of the charger's sense resistor, so shore carries the loads only up to the programmed charge current, which loads and pack share | charge held off by the pack gauge outside 0 to +45 C at the cells (the bridge clears its own hold above +3 C); the front end held off by `SHORE_INHIBIT`; the charger held off by `CHG_INHIBIT`; the heater mat warms the pack in the cold | pack gauge firmware (decision 40, whose residual D-15 rules); FW writes the charger (it has no thermistor input and a 175 s watchdog) | overlay: pack current reverses while the source covers the load | `PANEL.md` section 10; `pcb_pack_protection.yaml` CHARGE_TEMPERATURE_WINDOW; `OPERATING-ENVELOPE.md` sections 3 and 4; appendix 32.55 line 2915, 32.57 line 2984; BQ25731 datasheet SLUSE66A | without its host the charger falls back to a 256 mA charge current (SLUSE66A section 9.3.21.1: on a watchdog timeout "ChargeCurrent() resets to 256 mA"; TI's answer on its start-up value, E2E thread 1316778 of 23 January 2024, https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1316778/bq25731-bq25731-chargecurrent-start-up-behavior; bench confirmation owed), below the load of every running power state of section 4a, so without its host the pack gains charge only while the load on it stays under that 256 mA; as generated the charger's cell-count strap selects 2S, not 4S (engineering fix owed); the 4 A charge setting is to be lowered for cell life on the ruled 4S3P pack (a session item under D-06); charge current and time: **TBD** |
| Degraded | a module, supervisor, bearer or sensor lost, or a carve-out reached | cause removed | whatever survives | the lost item | HW (voted fabric), FW, SW | between PS-RED and the state before the fault, not computed | `ARCH-PCB-B-IOHA.md` sections 7 and 12; `PANEL.md` section 5 | per-device failover timeouts: **TBD**, to be measured on hardware (`ARCH-PCB-B-IOHA.md` section 7) |
| EMCON | `SW_EMCON` closed (locking toggle) | toggle opened | receive-only radios (GNSS, DCF77, lightning sensor), the VHF receiver, compute, display in its lighting mode | radios dark (owner ruling D-05), as section 4b: power removed from the SDR, RockBLOCK, LoRa, both E72 and the HF unit; 5G in airplane mode; the PA rail and keying off; disable pin asserted on the two WiFi link cards; software holds every send, an SOS included | HW for the gated rails and the VHF keying; SW hold on top | PS-EMCON 47.6 W as generated, PROVISIONAL | `PANEL.md` sections 6 and 9; `gen_sch_b.py` lines 724 to 743; `gen_sch_a.py` lines 535 to 537; `gen_sch_d.py` lines 270 to 287 | session fixes owed under D-05: the compute modules' own WiFi and Bluetooth onto the line, and the WiFi link cards' supplies gated from EMCON or their disable pin shown on the bench to act (section 4b) |
| Blackout | LIGHTING toggle at BLACKOUT | toggle moved | everything else as before | LED rail opened in hardware, monitor backlight and touch UI dark, speaker and sounder muted, TX lamp dark | HW for the LED rail; FW and SW for the monitor and sound | overlay: removes most of the monitor share, TBD | `PANEL.md` section 8; `V2-SPEC.md` line 60 | none |
| NVG | LIGHTING at NIGHT plus the bridge's NVG mode | either removed | panel at 2 % duty, backlight 5 %, red and amber indicators only | green and white indicators | FW and SW | overlay: monitor power at 5 % backlight TBD | `PANEL.md` section 8 | NVG compatibility of the light guides and LEDs is not specified: **TBD** (deferred under D-01) |
| SOS | `SW_SOS` closed 2 s (covered locking toggle) | toggle returned (cancels; the e-paper confirms both) | MASTER WARN flashes; sounder 1 s on, 1 s off (muted in blackout); the e-paper confirms; a distress message with the kit's position goes over the available bearers, Iridium first when nothing else is up, to a configured recipient list (owner ruling D-10) | never transmitted through EMCON: while EMCON is closed the message is queued and the operator is told (D-10) | FW (the panel controller reads the switch) and SW (the message); firmware only, no board change | transient transmit, not computed | `PANEL.md` sections 1, 3 and 9; `V2-SPEC.md` line 58; owner ruling D-10 | the recipient list and the message format are the session's; in prototype 1's core (section 2a) |
| ZEROIZE | `SW_ZERO` held closed 5 s (covered locking toggle), the only trigger (owner ruling D-03: the case-open or lid switch logs only; a remote wipe is deferred) | switch returned; the kit re-arms only when the toggle returns | MASTER WARN flashes while armed; flipping back inside 5 s aborts; then a crypto-erase through the secure element: every drive and eMMC key is wrapped by a key only the secure element holds, ZEROIZE destroys that key, then the running modules drop their keys from RAM, then the slots are cut; continuous 3 s sounder when complete; e-paper full refresh | the wrapping key, which leaves every drive unreadable, a powered-off module's included | FW and provisioning, no board change: no part but the panel controller reads the line (`gen_sch_c.py` line 113, GPIO22; it also runs over the ribbons to a 10 k pull-up on board A, R117 at `gen_sch_a.py` line 573, and to test pads on boards B and D), and the panel controller is also the kit I2C master that reaches the secure element; level-sensitive after a power loss: the toggle is read at boot before any slot powers and a wipe-pending record resumes the wipe | transient | `PANEL.md` sections 6 and 9; decision 30; owner ruling D-03 | precondition: the ATECC608B's slot map must let the wrapping key be erased, which needs its NDA datasheet (only the summary DS40002239A is held; a TPM 2.0 is the fallback 32.50 item 5 already names): **TBD**; accepted residual risk (D-03): a drive unlocks at boot only through the secure element, the panel controller and the kit I2C bus |
| Shutdown | PI button short press (clean shutdown of every module) or held 8 s (hard kill); MAIN PWR | startup | e-paper keeps identity and status with the power off | modules, radios | FW request, HW kill | PS-OFF after | `PANEL.md` section 5; `V2-SPEC.md` line 57 | shutdown on pack under-voltage: the gauge opens the discharge FET at 2.5 V per cell (`TEST-PLAN.md` section 5, row 2), in its firmware; owner ruling D-15 adds a 4S secondary protector that also covers cell under-voltage if one is sourced near the cost of the over-voltage-only part, or else keeps firmware under-voltage with a data-flash check at commissioning; a graceful shutdown before the trip is **TBD** |
| Storage | closed, pack out | deploy | none | all | none | none (pack out) | `TEST-PLAN.md` line 8; `OPERATING-ENVELOPE.md` section 4 | the envelope names an "ex-factory 30 percent" storage charge, but the pack is to be built for the kit, not bought: storage charge **TBD** |
| Service | face plate off (ten M3), rod stack lifted off the blind-mate joint, pack out of its cradle | reassembly | console and key fill over the sealed Glenair 233-370 USB receptacle (owner ruling D-12), `rpiboot` per module, SWD on the controllers | as the task needs | procedure (owner ruling D-14): before the lift the kit is off, the pack's XT60 unplugged and shore removed, and an insulating cap covers the dock block E5 while the stack is out | bench supply | `V2-SPEC.md` line 13; 32.50 items 2 and 16f; `ARCH-PCB-B-IOHA.md` section 2; `ASSEMBLY.md` sections 4 and 7 | as generated the wall USB data path goes to the USB-C outlet and the 233-370 has no data path (`gen_sch_a.py` line 574, `gen_sch_b.py` line 521): the move to the 233-370 is a design change owed; lifting the stack live is an accepted, recorded residual risk (D-14), and a hardware stack-present interlock is studied at Review D; test access list per board: **TBD** (foundation baseline, before placement) |

### 4a. Power states

The operating modes above are states of use. The power budget needs a smaller set of power states, and each
operating mode maps to one of them (or to an overlay that changes a share of one). The identifiers are
PS-... so that they never collide with the missions M1 to M5.

All figures are **PROVISIONAL**. They come from the foundation's power budget (MESHSAT-1357, 25 September 2026, a
working draft that is not published in this repository); every figure it contributes is reproduced here, and the
hours follow from the cell model stated here. Battery W is at the pack terminals and includes each path's
conversion loss and the distribution loss at 14.4 V. Runtime is usable energy over battery W, with the Samsung
INR18650-35E at its specification minimum of 3.35 Ah (specification sections 3.1 and 7.2; its standard condition
is 23 +- 3 C, so +20 C takes no temperature derating), the rate factor of its section 7.8, an average cell voltage
of 3.60 V less 0.05 Ohm times the current, and a 5 % reserve. "New" is the specification minimum capacity; "aged"
is 80 % of it, an assumption that still needs a requirement, because the cell specification (section 7.9)
states a minimum of only 60 % after 500 cycles. A large share of each figure rests on parts with no power
document or on duty assumptions (12.2 of the 29.4 W of PS-IDLE, 29.7 of the 60.1 W of PS-TYP): that share is
**TBD** and moves every hour below.

| Power state | Definition | Battery W | 4S3P, the ruled pack: new / aged, h | 4S4P, comparison only: new / aged, h |
|---|---|---|---|---|
| PS-OFF | pack connected, MAIN off: the dock strip's always-on controller, the gauge, clamp leakage | 0.37 to 1.87 (always-on draw TBD) | 3.1 to 15.5 days / 2.4 to 12.4 days | 4.1 to 20.6 days / 3.3 to 16.5 days |
| PS-IDLE | three modules idle, monitor dimmed, radios receiving, SDR off, no transmit | 29.4 | 4.6 / 3.7 | 6.2 / 5.0 |
| PS-IDLE-SPEC | PS-IDLE as `V2-SPEC.md` line 23 words it: monitor on, APRS beacons (interval TBD); the idle state of the D-06 runtime requirement | 32.4 | 4.2 / 3.4 | 5.6 / 4.5 |
| PS-TYP | three modules at typical operation, monitor on, radios receiving with light traffic, SDR on, HF receiving (32.52's "typical", re-derived); the typical state of the D-06 runtime requirement | 60.1 | 2.2 / 1.8 | 3.0 / 2.4 |
| PS-BUSY | three modules loaded, 5G and WiFi link passing traffic, Iridium and LoRa sending | **TBD** (needs duty cycles) | TBD | TBD |
| PS-RED | reduced, the envelope's definition: one module, monitor off, the other two slots and their cards off | 19.7 | 6.9 / 5.5 | 9.2 / 7.4 |
| PS-RED-b | reduced, 32.53's definition: three modules idle, monitor off | 25.4 | 5.4 / 4.3 | 7.2 / 5.7 |
| PS-EMCON | EMCON as generated: PS-TYP with the gated radios of section 4b off (the dark meaning D-05 rules) | 47.6 | 2.8 / 2.3 | 3.8 / 3.0 |
| PS-EMCON-L | EMCON if it kept receivers listening: the option D-05 did not take, kept for comparison | 52.5 | 2.6 / 2.0 | 3.4 / 2.7 |
| PS-ALLTX | every transmitter keyed at once, monitor full, fans; outlets off. D-11 bounds it by a declared key-down time above a declared state of charge and keeps the outlets at their minimum contract, which is **TBD** and comes on top of this figure | 227.0 | 0.5 / 0.4 (energy only) | 0.7 / 0.6 (energy only) |
| PS-ALLTX-OUT | PS-ALLTX plus PoE (0.6 A at 54 V) and USB-C at 45 W: excluded by D-11, whose interlock drops the outlets while the PA keys; kept to show the peak that ruling removes | 316.4 | 0.4 / 0.3 (pack protection trips first) | 0.5 / 0.4 |

**The pack (owner ruling D-06, 26 September 2026).** One 4S3P block of the held cell, the Samsung INR18650-35E, of
about 145 Wh (144.7 Wh at the cell's specification minimum), shrink-wrapped in the east pocket under board B,
ruled subject to the case measurement, which the owner withdrew on 26 September 2026 (D-08 reversed): the fit is
designed against the worst of Peli's own figures instead, and the margins that rest on unstated allowances stay OPEN
until a mock-up at the build (`CASE-MARGINS.md`). Missions longer than the pack rely on vehicle or solar input. The
4S3P columns describe the ruled pack. The 1.35 mm across the pocket that A06 reported was taken against the X 178
of appendix 32.62, which is not a Peli surface: bounded by board A's edge and Peli's R 15.88 floor fillet, the
block keeps 1.85 mm to the fillet and 7.38 mm to the east wall at the worst of Peli's figures, and, centred in Y,
3.65 mm per side to the frame's setting legs, 1.77 at the worst (`CASE-MARGINS.md` M4a, M4b, M5, on the design
basis only; M4b MET, M4a and M5 OPEN on the pack's placement by hand); no rigid box fits, so `v2/cad/pack_4s.py` is
to be redesigned around the shrink-wrapped block (a session item under D-06). No 4S4P 18650 block (193 Wh) has been shown to fit
either pocket while the pack board stays beside the cells (INFERRED from the committed board B underside and the
pocket of appendix 32.62): the 4S4P columns are arithmetic for comparison, not a configuration the design carries.
PS-ALLTX and PS-ALLTX-OUT are energy arithmetic only: the gauge's 20 A for 2 s limit and the 25 A blade bound
delivery first, especially at low charge, which is why D-11 bounds the all-transmit case.

**Mapping of the operating modes:** Transport and Deploy map to PS-OFF (or a reduced state if the kit is powered
in transit); Normal spans PS-IDLE to PS-TYP with PS-ALLTX bursts inside the bounds of D-11; Reduced is PS-RED, the
one-module state of the owner's closed-lid example (D-02b) and of the envelope above +35 C, with PS-RED-b (32.53's
cluster-idle definition) kept until the session defines the mode; EMCON is PS-EMCON as generated (the session's
D-05 gap fixes change it by an amount not computed); Charging, Blackout and NVG are overlays; Startup, Shutdown,
SOS and ZEROIZE are transients; Degraded is not computed; Storage has no pack fitted; Service runs from a bench
supply. The cold overlay adds the pack heater, about 10.8 W at the battery (7.5 W at 12 V, scaled to 14.4 V):
PS-TYP becomes about 71.0 W and PS-RED about 30.6 W. The cells' own capacity also falls in the cold: the Samsung
INR18650-35E specification (section 7.5, `v2/vendor/battery/samsung-35e-akkuzentrum.pdf`) gives 40 % at -10 C
against 97 % at 23 C when discharged at 3,400 mA, a factor of about 0.41. That factor holds at -10 C and that
current only: it is conservative at lower currents, and it says nothing below -10 C, where the cells' discharge
range ends (section 3.15: discharge -10 to 60 C ambient). A start from a pack below about -10 C at the cells is out
of scope for the prototype (owner ruling D-02d).

### 4b. What EMCON does to each radio, as generated

Read from the generators and confirmed on the regenerated netlists of boards A, B and D (connectivity
identical to the committed netlists). "Asserted" means `SW_EMCON` closed: `TX_INHIBIT_n` goes low and
`EMCON_HW` follows it low through the buffer on board C.

| Radio | What the line drives | What EMCON removes | Receive under EMCON |
|---|---|---|---|
| LimeSDR Mini 2.4 | the enable of the eFuse that feeds its USB VBUS, its only supply (`gen_sch_b.py` lines 724 to 728) | power | lost |
| RockBLOCK 9704 | the enable of the eFuse that feeds its external supply pin, the only supply wired | power | lost |
| E22-900M30S LoRa | the enable of the load switch that feeds its VCC pins; its TXEN pin is driven by slot 3 and is not on the line | power | lost |
| Two E72 CC2652P (Zigbee, Thread) | the enable of the load switch that feeds both | power | lost |
| RM520N-GL 5G | its W_DISABLE1# pin, low; the card's supply follows the module's own PCIe power enable only | RF (airplane mode, "the RF function will be disabled", Quectel hardware design section 4.4.1); the module stays powered | lost |
| Two AW7915-AED WiFi link cards | their W_DISABLE1# pin, low; the card supplies follow the modules' PCIe power enables only | a request to disable RF; whether the card acts on it is **TBD**: the maker's datasheet does not mention the pin and the mainline Linux driver has no code for it | unknown |
| SA868 VHF with the 30 W PA | the KEY gate on board D (`KEY = PTT_ANY AND TX_INHIBIT_n`) and the PA rail and keying on board A; the exciter's supply is not gated and the resting relay joins antenna to exciter | transmit only | continues |
| QMX HF | the enable of the converter that feeds its DC input (`gen_sch_a.py` line 536); its USB supply is not gated | power (its receiver runs from the DC input per its manual) | lost |
| The three compute modules' own WiFi and Bluetooth | nothing: their disable pins are driven only by a software I/O expander on the kit bus (`gen_sch_b.py` lines 378 and 743) | nothing in hardware | continues, and so does transmit |
| LG290P GNSS, DCF77, lightning sensor | nothing | receive-only; nothing to remove | continues |

**Owner ruling D-05 (26 September 2026): EMCON means radios dark, as generated and completed.** Every radio with an
emission path is powered off or RF-disabled in hardware; the VHF path keeps listening because its gate is on the
transmit side only; GNSS, DCF77 and the lightning sensor continue. The table meets that meaning in every row but
two, and closing those two is session work under the ruling, owed and not yet in the generators: the compute
modules' own WiFi and Bluetooth go onto the EMCON line through open-drain elements that may only drive their
disable pins low (Compute Module 5 datasheet sections 2.1.1 and 2.1.2: each pin "may only be driven low"), and
the WiFi link cards' supplies are gated from EMCON or their W_DISABLE1# is shown on the bench to act before any
rule counts them as silenced. The 5G module's own GNSS receiver is not counted in the last row: the kit's
position source is the LG290P, the module's GNSS ports (L5 on ANT1, L1 on ANT3, Quectel hardware design v1.1
Table 32) are fitted only in part under D-07, and whether W_DISABLE1# stops it is not established.

The design record promised more than the generators carry: appendix 32.55 (line 2930) lists a supply switch
for the 5G module and a converter enable for the WiFi card under EMCON, and neither is in the generated
boards. That difference is carried in the conflict list, not resolved here.

## 5. What runs at the same time, and how often

**The rule the hardware is designed to:** no transmit serialisation is required; every transmitter may key at
once (owner ruling of 4 September 2026, appendix line 2337, restated at line 2465), **bounded since 26 September
2026 by owner ruling D-11**: all at once for a declared key-down time above a declared state of charge, with the
outlets at their minimum contract. The session sets both thresholds from the fuse and gauge limits (**TBD**), and
adds a hardware interlock that drops the outlets while the PA keys. The design record already asks for that drop
(32.55 line 2932), but as generated the PoE and USB-C enables are software expander pins on board A (`gen_sch_a.py`
lines 542 and 547) with no hardware tie to the PA keying. The load figures below are the design estimate of
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
| APRS with the 30 W PA | 1.5 / 75 | over 30 W out at over 40 % efficiency at 12.5 V, about 45 W of heat (32.51 line 2813) | beacon interval **TBD**; "APRS duty only at full power" (32.49 item 8) | key-down for minutes (32.53 line 2860), inside the key-down bound of D-11 | thermal (PA column, plate), runtime |
| Switches, hubs, bridges, controllers | 6 / 8 | plus about 0.9 W for the I/O supervisors (`ARCH-PCB-B-IOHA.md` section 14) | continuous | continuous | runtime |
| Sensors and panel | 2.5 / 2.5 | none | continuous | continuous | runtime |
| PoE and USB-C outlets | 0 / 90 | 45 W USB-C (32.57 line 2980), PoE 54 V at 0.6 A (32.55 line 2927) | accessory dependent: **TBD** | full, cut to minimum while the PA keys (D-11) | runtime, input budget |
| Conversion losses | 12 % | none | | | runtime |
| **Sum** | the listed loads are 45.0 W typical and 178 W peak; with the 12 % allowance that is 50.4 W and 199 W, the record's "about 50 W" and "about 200 W", so those two figures are **at the battery**. The record's "up to 290 W" is 199 W plus 90 W of outlets, **without** the allowance on the outlets | | | | |

The 32.52 estimate predates the loads added after 7 September 2026 (the I/O supervisors, the second WiFi card,
the fans) and uses one flat 12 % for conversion; re-derived per path, the typical state is PS-TYP at about
60.1 W (section 4a). Where the two differ, section 4a is the current PROVISIONAL figure and 32.52 is history.

**Simultaneity cases, for the power, thermal and runtime budgets:**

| Case | What is on | Power state and estimate (PROVISIONAL) | Source or status |
|---|---|---|---|
| S1 idle watch | three modules idle, radios receiving | PS-IDLE 29.4 W (monitor dimmed); PS-IDLE-SPEC 32.4 W (monitor on, APRS beacons) | the 29 W "typical" of `V2-SPEC.md` line 23 is the single-module figure of 32.49 (line 2775) |
| S1b typical relay | three modules at typical operation, monitor on, SDR on, light traffic | PS-TYP 60.1 W | 32.52 item 3's "about 50 W typical", re-derived |
| S2 busy relay | three modules loaded, 5G and WiFi link passing traffic, Iridium and LoRa sending | PS-BUSY, **TBD** (between PS-TYP and PS-ALLTX) | needs the duty cycles above |
| S3 every transmitter keyed | S2 plus the PA at key-down and HF transmitting, outlets at their minimum contract | PS-ALLTX 227.0 W with the outlets off, plus their minimum contract (**TBD**), for the declared key-down time above the declared state of charge (D-11, both **TBD**) | 32.52 item 3, 32.53 line 2860; owner ruling D-11 |
| S4 operating while charging | S1 to S2 with shore or vehicle present | the front end regulates 20 V at up to 5 A (100 W, 32.55 line 2915), so S3 draws from the pack even on shore power; and the charger carries the loads only up to its programmed charge current (section 4, Charging) | inferred from the two numbers; input current limit **TBD** |
| S5 reduced | one module or an idle cluster, monitor off | PS-RED 19.7 W (one module) or PS-RED-b 25.4 W (cluster idle); the definition is the session's to fix | 32.53's "about 30 W with one module" (line 2860) is the lid-open, monitor-on figure, not the reduced mode |

## 6. Runtime and endurance

The runtime of `V2-SPEC.md` line 23 (8 to 9.5 hours typical) was computed for the withdrawn BB-2590/U pack
and is **not valid** for this kit. It divided the BB-2590's nominal energy by a battery-side figure with no
derating (29 W x 8 to 9.5 h is 232 to 276 Wh; 50 W x 5 to 6 h is 250 to 300 Wh). On the pack the owner ruled
(D-06: one 4S3P 18650 block of about 145 Wh, its fit designed against Peli's figures since D-08 was reversed), with usable energy, conversion
losses and a reserve applied, the PROVISIONAL figures of section 4a are:

- the state `V2-SPEC.md` describes (monitor on, radios idle, beacons), PS-IDLE-SPEC: about 4.2 h new and
  3.4 h aged;
- the typical state of 32.52, PS-TYP: about 2.2 h new and 1.8 h aged;
- the reduced mode: about 6.9 h new with one module (PS-RED, the owner's closed-lid example) or 5.4 h with
  the cluster idle (PS-RED-b), until the session defines the mode.

**The runtime requirement (owner ruling D-06, 26 September 2026)** is stated as battery-only hours in an idle and
a typical mode at +20 C for an aged pack. The session takes PS-IDLE-SPEC and PS-TYP as those two modes, the pair
W1's decision table recommended, **under the owner's standing rule of 26 September 2026**. The required values are
**TBD**: the PROVISIONAL figures for an aged 4S3P pack are 3.4 h and 1.8 h, and they move with the TBD share of each
power state, with the definition of "aged" (80 % of the minimum capacity is the assumption of section 4a; the cell
specification states a minimum of 60 % after 500 cycles), and with cold (the heater overlay and the cells' reduced
capacity). Missions longer than the pack rely on vehicle or solar input; the mission duration for M1's
pack-plus-solar energy balance is left to the owner by D-06 and stays **TBD** until he sets it, because no source in
this tree states one.

## 7. Owner questions and their rulings

Each question was asked one at a time with its evidence, options and a recommendation, and the owner took the
recommended option each time. The identifiers D-nn are those of the foundation's owner decision table
(MESHSAT-1357). D-01, D-02a and D-02b were ruled on 25 September 2026 (about 23:27 to 23:40 CEST); D-02c and every
later ruling of that sitting on 26 September 2026 (about 00:05 to 00:55 CEST). D-08a was ruled later on 26
September, and at about 09:30 CEST the owner reversed D-08, declining the measurement request that ruling had
answered (appendix 32.367). A ruling that sets a threshold or names a session
item leaves that engineering work to the session; until it is done, the requirements that depend on it carry TBD
with its effect, never an assumed answer.

| ID | Question | Status | The ruling |
|---|---|---|---|
| D-01 | Prototype scope | RULED 25 Sep | full design, staged acceptance on a named core; everything else built where possible and reported NOT_YET_TESTED (section 2a) |
| D-02a | Qualification margins | RULED 25 Sep | `TEST-PLAN.md`'s +55 C operation, +71 C storage (E3) and -33 C storage (E4) are qualification margins over the envelope's -20 to +40 C in use and -20 to +45 C in storage, with two pass lines: operate to specification inside the envelope; survive and recover at the margin |
| D-02b | Closed-lid operation | RULED 25 Sep | the kit operates with the lid closed in a defined reduced mode (the owner's example: GNSS, LoRa mesh, Iridium and APRS beacons, monitor off, one module); a closed-lid state and thermal test join `TEST-PLAN.md`; a lid sensor is an engineering item, and the case-open switch can serve both. Accepted consequences: above +35 C ambient the kit runs one module; with three loaded modules charging holds off above about +25 C ambient |
| D-02c | Severities and altitude | RULED 26 Sep | `TEST-PLAN.md` E1 (26 drops from 1.22 m) and E2 (composite wheeled vehicle profile, 1 hour per axis); altitude 0 to 3000 m in use and 0 to 4500 m in transport; service life **TBD** for prototype 1 |
| D-02d | Cold start from a cold-soaked pack | RULED 26 Sep | out of scope for the prototype, to be stated in the envelope and stated here: a kit cold-soaked below about -10 C at the cells needs shore or vehicle power, or warming, before it starts from the pack; once warm, use down to -20 C holds. No hardware is added |
| D-02e | Direct sun | RULED 26 Sep | "operate shaded" is a stated operating condition, with a shade accessory (a lid sun shield or a tarp); full-sun design is a later qualification item. No board change |
| D-03 | ZEROIZE: what it erases, what triggers it, what a power loss during the hold does | RULED 26 Sep | a crypto-erase through the secure element, the covered toggle held 5 s the only trigger, level-sensitive after a power loss, and the accepted residual risk that a drive unlocks at boot only through the secure element, the panel controller and the kit I2C bus (section 4, ZEROIZE row). Firmware and provisioning, no board change; the secure element's erasable slot map is a precondition still **TBD**. Decision 30 is ruled by it |
| D-04 | Markets and obligations | RULED 26 Sep | a non-commercial prototype in the Netherlands and the EU, operated by a licensed radio amateur; no CE or RED conformity marking claimed and no EMC claim yet, so every MIL-STD-461 run is characterisation; the design keeps an EU route open. Every transmitter is to be configured to the operator's licence and the EU limits, the VHF path gets a band lock, and the pack's transport route is stated (section 4, Transport row; UN 38.3 status unknown). What the row states since its correction of 26 September 2026 is that no route is claimed acceptable until the pack's classification, conditions or applicable exception are established (section 7a) |
| D-05 | EMCON meaning | RULED 26 Sep | radios dark, as generated and completed: every radio with an emission path powered off or RF-disabled in hardware; VHF keeps listening (transmit-only gate); GNSS, DCF77 and lightning continue. The gap fixes (the compute modules' radios onto the line, the WiFi link cards' disable shown to act or their supplies gated) are session work (section 4b) |
| D-06 | Pack size and runtime target | RULED 26 Sep | one 4S3P 18650 (Samsung INR18650-35E) pack of about 145 Wh, shrink-wrapped in the east pocket, subject to the case measurement (answered from Peli's own figures after the D-08 reversal: `CASE-MARGINS.md` M4a to M6, with M4b and M6 MET and M4a and M5 OPEN until the pack's hold-down and a mock-up at the build); missions longer than the pack rely on vehicle or solar input; the runtime requirement is battery-only hours in idle and typical modes at +20 C for an aged pack (section 6); the mission duration for the solar energy balance is set later by the owner. Session items: a lower charge setting for cell life, and `pack_4s.py` redesigned |
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
| D-18 | IP68 fans | OPEN, conditional | it arises only if Delta's 40 mm IP68 fan does not fit the coolers; if it does, the session settles it under the owner's standing rule of 26 September 2026 (section 7a) and records the option it takes. The sealed case's thermal path waits on it |

The board-level decisions 27 (board C on six layers), 28 (board P on four layers at 2 oz), 41 (the order set
rebuilt and quarantined) and 43 (board B measured on eight layers first, its whole-board run EXPERIMENTAL) were
ruled by the owner on 25 September 2026 (appendix 32.365). They change no need, mission or mode here.

### 7a. Choices the session took under the owner's standing rule of 26 September 2026

On 26 September 2026 the owner ruled that he is not to be asked further questions: where a choice is left, the
session takes the option the evidence recommends and records it as its own, so that it can be reversed. Each
choice below was taken that way; a choice later corrected or withdrawn keeps its row, marked and dated. The last
three rows are the case choices of `CASE-MARGINS.md` section 4, taken after the owner reversed D-08 (section 7).

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
