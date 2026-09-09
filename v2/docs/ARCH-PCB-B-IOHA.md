# PCB-B I/O high availability: three I/O supervisors and a host-selection fabric

Owner ruling, 9 September 2026. Architecture note, Stage 1 of the programme in `~/.claude/plans/`. **Prototype design. Nothing here has been built, and no board carries this topology yet.** MESHSAT-862.

## 1. Why

The kit has compute redundancy and no I/O redundancy. Three CM5 modules run k3s, so the loss of one module does not end the service. But every peripheral is wired to exactly one module, so the loss of one module ends that module's peripherals:

| slot lost | what goes with it |
|---|---|
| 1 | LimeSDR Mini, the panel RP2040, the camera, the RockBLOCK (Iridium) |
| 2 | LG290P GNSS, Zigbee E72 A, Thread E72 B, the QMX HF unit |
| 3 | the APRS board on PCB-D, the sensor RP2040 on the dock, the wall USB port, the spare |

The design record says "every radio is a USB device shared by the HAL over the network". That is true only while the module that physically owns the radio is alive, and it is corrected wherever it appears. **Compute redundancy is not peripheral redundancy and must never be presented as it.**

The requirement, ruled by the owner: the loss of any one CM5, or of any one I/O supervisor, must not make a critical peripheral permanently unreachable; ownership must move to a surviving module without a fourth central arbiter; and the hardware, not the firmware, must prevent two hosts owning one peripheral.

## 2. What the board is today

Audited from `gen_sch_b.py`, `gen_pcb_b.py`, `gen_pcb_b3.py` at commit `c233302`. The numbers below are the constraints the redesign has to live inside.

**USB.** Three TUSB8041I four-port hubs, one per slot, each on its own module's USB3-0 port. Eleven of the twelve downstream ports are USB2 only; slot 1 port 1 is the single SuperSpeed downstream port, for the LimeSDR.

**The host-port budget, which decides the whole architecture.** Each CM5 exposes exactly **two** USB3 host ports:

| port | state |
|---|---|
| USB3-0 (CM5 pins 128, 130, 134, 136, 140, 142) | fully consumed by that slot's hub upstream |
| USB3-1 (pins 157, 159, 169, 171 SuperSpeed; 163, 165 USB2) | **the four SuperSpeed pins are `NC` on all three slots** and already brought to the receptacle land. The USB2 half is free on slot 3 only; on slots 1 and 2 it carries the M.2 card's USB2 link |
| USB2 OTG (pins 103, 105) | wired as a **device** port to `J_FLASH{s}` for `rpiboot`, not a host |

So the spare USB3-1 port is the entire failover budget: one per module, three in the kit.

**PCIe.** One PI7C9X2G404SL per slot fans the module's single Gen2 lane to an NVMe M.2 socket and one card socket (WiFi E-key on slot 1, 5G B-key on slot 2, a spare M-key on slot 3). Port 3 of every switch is free. There is no AC coupling on any PCIe lane or on the reference clock tree.

**Ethernet.** One KSZ9897R: ports 1 to 3 face the three modules PHY to PHY through 100 nF, port 4 is the wall RJ45 through magnetics with the PoE injector. **Port 5, a whole copper PHY, and MAC ports 6 and 7 are unused.** Management is I2C and the master is the RP2040 on PCB-C; no CM5 is on that bus at all.

**Defects the audit found that belong to this work.**

1. `HUB{s}_RST_n` is an RC only. **No hub on the board can be reset by anything.** A wedged hub can only be recovered by cutting its slot rail.
2. Four CP2102N bridges take their power from **slot** rails: GNSS and both E72s from `+5V_S2`, the RockBLOCK from `+5V_S1`. The radios themselves sit on shared rails, so a slot loss kills the host interface of radios that are otherwise alive. This looks unintended.
3. `KSZ_RST`, `5G_OFF` and `5G_RESET` drive FET gates with no pull-down, so they float through PCA9555 power-on reset.
4. The panel RP2040 is on **slot 1's** hub, not slot 2's as `gen_sch_c.py` claims.
5. The `J_PANEL` 2x13 ribbon carries `PI_KILL`, `PI_SHDN_REQ`, the kit I2C, EMCON and all three `SLOT_EN`. One connector failure is a whole-kit failure. The EMCON half of that is deliberate and stays.

**Board area.** 330 x 200 mm, six layers, assembled both sides. 84.1 percent of the front is inside a placement rectangle and the largest free pocket is 18 x 34 mm. Three controller blocks do not fit without a floor-plan pass and the underside.

## 3. Three planes

```text
  compute        CM5-A            CM5-B            CM5-C          k3s, unchanged
                   |                |                |
  data       ===== host-selection fabric (passive, high speed) =====
                   |                |                |
               bank 1           bank 2           bank 3           hubs and peripherals
                   |                |                |
  control      IOCTRL-A  <-CAN->  IOCTRL-B  <-CAN->  IOCTRL-C     2 of 3 quorum
```

The control plane decides ownership and never carries payload. **No peripheral traffic passes through a controller**, and in particular the LimeSDR's 5 Gbps never touches one.

## 4. The USB ring

Three hub banks are kept, so three I/O failure domains survive. Each bank's upstream is selected between its **home** module (that module's USB3-0) and one **neighbour** module (that module's spare USB3-1):

```text
bank 1  <- 2:1 <-  CM5-A USB3-0 (home)  |  CM5-B USB3-1 (failover)
bank 2  <- 2:1 <-  CM5-B USB3-0 (home)  |  CM5-C USB3-1 (failover)
bank 3  <- 2:1 <-  CM5-C USB3-0 (home)  |  CM5-A USB3-1 (failover)
```

Every module uses both host ports and none is wasted. Any single module loss moves exactly one bank to a neighbour that has a free port.

Two simultaneous module losses leave one bank unreachable. That is inherent and no topology fixes it: one module has two host ports and cannot host three banks. The requirement is single-failure tolerance and the ring meets it exactly.

**Per bank:** one **TI TMUXHS4212** for the SuperSpeed pair set and one USB2 high-speed mux for D+/D-. The TMUXHS4212 is a 2-channel 2:1 differential mux, 16 Gbps, **-1.3 dB insertion loss at 5 GHz**, 13 GHz -3 dB bandwidth, in a 2.5 x 4.5 mm QFN (`https://www.ti.com/product/TMUXHS4212`). The ring needs **one hop**, so no cascade and no eye-budget gamble.

**The hubs move from the slot rails to `+5V_DEV`,** or a bank cannot outlive its home module. The four CP2102N bridges move with them.

## 5. How the hardware prevents split brain

Four independent mechanisms, strongest first.

1. **Majority voting on every mux control.** Each `SEL` and each `OE` is generated by a 2-of-3 voter in commodity logic, `out = AB + BC + CA`, one voter per control bit, with the three controllers as the three inputs. A controller wedged in any state is outvoted by the other two. **No firmware is trusted for this.**
2. **Fail-safe defaults.** With all three controllers dark the voter outputs pull to *home host* and `OE` pulls to *disconnected*. A dead control plane degrades to the static assignment the board has today, not to contention.
3. **Break before make.** The voted `OE` is de-asserted, a delay elapses, the voted `SEL` changes, `OE` is re-asserted. A hardware delay element prevents `OE` rising coincident with a `SEL` change, so the ordering is not a firmware promise.
4. **The hub's own rule, where a USB4715 front end is used.** Microchip's AN2341 states that with FlexConnect *"only one of these hosts may have access to the USB tree at a time"*, and the hub **auto-reverts to its default host when VBUS_DET on the owning port goes low**. Two hosts cannot be attached, and the commonest failure case, a module losing power, needs no controller at all.

## 6. The control plane

**Three equivalent supervisors, `IOCTRL-A/B/C`, baseline 3x STM32H753.** They hold controller identity, epoch, ownership leases and expiry, the owner module per bank, peripheral and module health, the failover state machine, and the interlock state. The MCU choice is settled in Stage 2 against the i.MX RT1180 on the owner's weighting, with raw clock speed weighted last; the package is chosen from the pin and resource matrix, not before it.

**Heartbeat: two independent CAN-FD fabrics**, one per FDCAN peripheral, with separate transceivers, separate termination and separately routed pairs. Loss of either fabric, or of one transceiver, leaves quorum. Ethernet health reporting to the cluster is secondary and is never the arbitration path. The KSZ's free PHY port 5 is one candidate; three controller links do not fit on one port, so this is an open design item and not an assumption.

**Power independence.** Each controller gets its own regulator branch, supervisor, watchdog, reset and SWD pads. `+3V3_DEV` must not feed all three, or the control plane has a common-mode failure by construction.

**Hub reset becomes real.** The voted plane drives `HUB{s}_RST_n`, which today has no driver at all, so a wedged hub can be recycled as part of the failover sequence.

## 7. Failover sequence, per bank

1. the owner module stops answering its heartbeat
2. quorum confirms the loss, 2 of 3
3. the ownership lease is revoked and its epoch incremented
4. the old path is quiesced where the hardware still permits it
5. the voted `OE` drops, the fabric goes to its disconnected state
6. the hub or peripheral is reset or power-cycled where the device needs it
7. the voted `SEL` moves to the failover module
8. `OE` re-asserts after the break-before-make delay
9. USB re-enumeration on the new host
10. device identity and health verified
11. the HAL's logical name is re-pointed
12. application access resumes

Timeouts are per device and are measured on hardware, not invented.

## 8. Bearer distribution

An I/O bank failure must degrade capability, never remove every path. Today bank 1 holds the SDR **and** Iridium, and bank 2 holds the HF unit **and** both 2.4 GHz radios. The redesign distributes the long-range bearers so that **no bank holds two of them**, and `check_pcb_b.py` gains that as an invariant rather than a note.

## 9. PCIe

NVMe stays one per slot. That is high availability by **duplication**, which k3s already exploits, and not by failover. Multi-host PCIe with an NTB-capable switch is **rejected for this revision**: the parts are large and power-hungry, each CM5 offers a single Gen2 lane upstream, and an unverified multi-host PCIe design must not be committed. This is an explicit decision, recorded here, not a silent exemption.

The card sockets depend on the open ruling in section 11.

## 10. What still fails after this

Named honestly, because an FMEA that lists nothing is worthless:

- `+5V_DEV` and `+3V3_DEV` feed everything shared. A short on either is a whole-board failure.
- The `J_PANEL` ribbon remains a whole-kit control failure.
- The KSZ9897R is one switch: it fails, all three modules lose the wall port and each other's Ethernet.
- The kit I2C bus is one bus with one master on another board.
- The voters themselves are silicon and can fail; they fail to a defined state, which is why the safe state is the home assignment.
- Two simultaneous module losses leave one bank unreachable, as section 4 explains.

## 10a. What is built, 9 September 2026 17:40 to 18:40 CEST

The fabric and the control plane are in `gen_sch_b.py` and the generator builds: **939 parts, 815 nets, no single-pin net.**
Every claim below was read back from the exported netlist rather than assumed.

**Per bank:** a TMUXHS4212 with port A on the hub, port B the home module's USB3-0 and port C the neighbour's USB3-1;
a TS3USB221A on D+/D-, because the TMUXHS4212's common mode range is 0 to 1.8 V against USB2's 3.3 V swing and its I/O
absolute maximum is 2.4 V; the hub's AC coupling moved to the hub side of the mux so one pair of caps serves either host.

**Per controller:** an STM32H753VITx in LQFP-100, its own AP2112K-3.3 branch off `+5V_DEV`, its own 25 MHz crystal
because CAN-FD bit timing cannot ride on the HSI, its own reset, SWD pads, status LED, and **two** TCAN334D transceivers
on two independent fabrics with separate termination. The pin table is KiCad's own `STM32H753VITx` symbol, which cites
`https://www.st.com/resource/en/datasheet/stm32h753vi.pdf`; the alternate-function choices, FDCAN1 on PD0/PD1 and FDCAN2
on PB12/PB13, are the classic H7 mappings and are to be confirmed against the datasheet's AF table before release.

**Six voters**, one per voted bit, `out = AB + BC + CA` in 74LVC08 and 74LVC32 quads, the same families the EMCON chain
already uses. Verified on bank 1: the three controllers' selects enter U70 at pins 1/9, 2/4 and 10/5, the three products
leave at 3, 6 and 8, and the OR tree in U76 produces `BSEL1`, which reaches both muxes, its pull-down, the RC and the
break-before-make detector. Every one of the eighteen controller outputs carries a pull-down, so a controller that is
absent, unpowered or in reset is read as a definite no rather than as an undefined CMOS input.

**Break before make is hardware.** A 74LVC86 compares each voted select against an RC-delayed copy of itself and raises
that bank's mux enable for the RC time on any transition. The firmware does not sequence it and cannot skip it.

**One fail-safe inversion was caught by reading the netlist back, not by inspection.** The hub reset was first wired
straight from its voter. A voter output is push-pull and its inputs sit low when the control plane is dark, so that
arrangement would have held every hub in reset whenever the controllers were absent: the exact opposite of a safe state,
on a board where no hub reset had any driver at all before today. The voted signal now gates a 2N7002 that pulls the
reset down, the way `KSZ_RST` has always been done here, so the existing RC holds each hub out of reset by default and a
majority can still recycle a wedged one.

**Placement (corrected the same evening).** One back-side band under the modules was wrong twice: it put parts under
the six CM5 receptacles, whose 0.4 mm rows escape into vias at the pad tips, and over the twelve M2.5 standoff holes at
Y 36 and Y 84, and it put all three supervisors in one failure domain. The three controller blocks sit in three
separate back-side pockets instead: the gap between the slot 1 and slot 2 module columns (X -52 to -23), the gap
between slot 2 and slot 3 (X 18 to 47), and the free underside of the QMX bay (X -158 to -129, clear of its four strap
slots). The voters and the small logic take the band between the receptacles and the standoff row, Y 69 to 80.5, and
the antenna changeover sits on the underside of the LimeSDR bay near the east wall.

**State, 9 September 2026 18:45 CEST.** The full board builds and `check_pcb_b.py` prints `RESULT: ALL PASS` with
every invariant of section 5 and the new ownership, rail-independence, read-back and WiFi-duplication checks: 951
footprints, 840 nets, no region overflow, nothing unplaced. It is not routed: no B deliverable is cut against this
topology. Five further defects were found by building it and are recorded in appendix 32.86, the most important being
that a bank's hub and both its host selects hung on the rail of the module they are meant to fail away from.

## 11. Open rulings

1. **CLOSED 9 September 2026 by the owner's condition: WiFi stays on PCIe.** The condition was that the radio must do peer-to-peer links with no access point. The gate fails for USB: **MT7921, the embeddable USB WiFi 6 chip, does not support mesh point mode** (openwrt/mt76 issue 653, 2022, cited in morrownr/USB-WiFi issue 526, where the question of hardware, firmware or driver cause was asked and never answered). The mt76 chip that does mesh over USB is the MT7612U, and the 5 September research had already established that **no embeddable MT7612U module exists**, which is why that ruling moved WiFi to M.2 PCIe in the first place. The MT7915 in the AW7915-AED is documented for AP, station and mesh in its kernel submission, so the card stays. The consequence is that the PCIe switches are not deleted and no area is freed there.
2. **CLOSED: one board.** The underside under the three CM5 modules, X -98 to 94 and Y 32 to 88, is **10,752 mm2 and carries nothing** (`gen_pcb_b3.py` places no back-side region there). The control plane needs roughly 2,400 mm2: about 650 mm2 per controller for the MCU, two CAN transceivers, its regulator, supervisor, crystal and SWD pads, plus about 450 mm2 of voters. It fits on the underside with room for routing, so no second board and no ribbon. B16's underside clears D8's SA868 by about 20 mm, which an LQFP part uses 1.7 mm of; a gate for back-side clearance to A22 does not exist yet and is added with the rest.
3. **CLOSED 9 September 2026, the owner asked for a recommendation and took it: the WiFi card is DUPLICATED and the two cards SHARE the antennas.** Slot 3's spare M-key drive socket becomes a second E-key socket carrying a second AW7915-AED, so any single module loss leaves one mesh radio. The two cards feed the **existing** pair of P2P antennas through a passive RF changeover, because every case penetration is a seal under the no-vent ruling of 7 September and two more jacks would be a case change: the end walls, the 1:1 template and A22's jack count all stay as they are. Only one radio is live at a time, which is what failover needs rather than capacity; the price on the primary path is the switch's 0.35 dB below 3 GHz and 0.50 dB from 3 to 6 GHz (Skyworks 201132I) plus two U.FL transitions of about 0.1 dB each, so roughly 0.6 dB at 2.4 GHz and 0.7 dB at 5 GHz. The changeover follows the voted "secondary active" signal and pulls to the primary card, so a dark control plane leaves the primary connected. The RF switch part is picked from the manufacturer's own data, not from a distributor listing. The trade accepted here is a fourth spare drive slot, which k3s does not need with three replicas, against a redundant kit-to-kit link.
4. **OPEN: 5G to USB 3.0.** The RM520N-GL supports both PCIe and USB 3.1 Gen1, and moving it to USB would put cellular into the failover fabric and delete one PCIe switch. Gated on Quectel's hardware design guide, which is not yet on file.
5. **B18 is superseded.** Its information route remains useful as placement data; no B release is cut against the current topology.

## 12. FMEA

Every row is a failure this design is supposed to survive or is knowingly exposed to. "Detected by" names the
mechanism that notices, because a failure nothing notices is not handled, it is unnoticed. Nothing here has been
tested: the prototype is not built, and section 13 is how each row will be shown.

| # | Failure | Effect before this work | Effect with it | Detected by | What still hurts |
|---|---|---|---|---|---|
| 1 | One CM5 dies (any slot) | its whole bank of peripherals is unreachable until a person opens the case | its bank moves to the neighbour module on a voted select; k3s reschedules the workload | heartbeat loss on both CAN fabrics, and the module's Ethernet link dropping | the neighbour carries two banks on its two host ports, so its USB bandwidth is shared |
| 2 | Two CM5s die | two banks unreachable | one bank unreachable, the other two hosted by the survivor | as above | inherent: two host ports per module, three banks |
| 3 | One I/O supervisor dies or is unpowered | n/a, none existed | the other two are a majority and ownership is unaffected | its heartbeat stops on both fabrics; its status LED is dark | none |
| 4 | Two supervisors die | n/a | no majority; every voted bit reads its pull-down and the fabric rests on the home assignment, which is the board's behaviour before this work | heartbeat | no failover until a supervisor returns |
| 5 | A supervisor wedges with its outputs stuck | n/a | outvoted 2 of 3; it cannot move a single bit | the other two see its heartbeat stop or its votes disagree with quorum | none |
| 6 | A voter output stuck at one value | n/a | that bank cannot move, or is stuck on the failover host | **each controller reads the four voted bits back**, so a vote that does not match quorum is visible | a stuck voter needs a person; the bank still works on whichever host it is stuck to |
| 7 | One CAN fabric breaks or a transceiver fails dominant | n/a | quorum continues on the other fabric | bus-off and error counters on the broken fabric | a second fabric failure isolates the controllers |
| 8 | Both CAN fabrics break | n/a | no controller can form a majority; firmware rule is that a controller without quorum does not act, so the voters hold the home assignment | each controller sees both fabrics silent | no failover |
| 9 | A bank's hub fails or wedges | the bank is dead until a power cycle of the whole kit | a voted majority pulls `HUB{s}_RST_n` through its FET and recycles it | the owning module loses every device of that bank at once | a hub that fails hard takes its bank; the peripherals are not dual-homed, only the host is |
| 10 | A slot's 5 V or 3.3 V rail fails | the bank died with it | the bank's hub, both host-selection switches and the hub core are on `+5V_DEV` and `+3V3_DEV`, so the bank survives and moves to a neighbour | the module stops, the rail's own LED is dark | the module and its NVMe and card socket are gone, by design |
| 11 | `+5V_DEV` or `+3V3_DEV` fails | whole board | whole board: every hub, every mux, every supervisor and the Ethernet switch | everything stops | **unmitigated common mode.** A22 feeds it from one converter and this design does not change that |
| 12 | The `J_PANEL` ribbon is cut or unseated | whole kit loses the panel, EMCON and the slot enables | unchanged | the panel controller stops answering | **unmitigated common mode**, named in section 10 |
| 13 | The KSZ9897R fails | all three modules lose the wall port and each other's Ethernet | unchanged; heartbeat is on CAN and does not depend on it | link loss on every port | **unmitigated common mode**; the CAN fabrics are what keep the control plane alive through it |
| 14 | The WiFi mesh card fails, or slot 1 dies | the kit-to-kit link is gone until the case is opened | the second card on slot 3 takes the antennas on a voted select | the card stops answering on its PCIe bus; the mesh link drops | one antenna pair is shared, so only one radio is live: this is redundancy, not capacity |
| 15 | An antenna changeover switch fails | n/a | that chain is stuck on whichever card it rests on; with the FET open it rests on the primary | the standby card cannot bring the chain up when selected | a stuck changeover needs a person |
| 16 | The changeover's complement FET or its pull-up fails | n/a | VCTL1 stuck high leaves the primary card connected, which is the safe state; stuck low with VCTL2 low isolates both | the selected card's link does not come up | the isolated case needs a person |
| 17 | A peripheral itself fails (the SDR, the GNSS, a radio) | that capability is gone | unchanged: the fabric moves hosts, not devices | the device stops enumerating | **peripherals are not duplicated**, except the WiFi card and the NVMe drives |
| 18 | The 5G module or its PCIe lane fails, or slot 2 dies | cellular is gone | unchanged: cellular hangs on slot 2's PCIe lane, and only its management USB is on the ring | the module stops answering | open ruling 4: moving 5G to USB 3.0 would put it on the ring, and needs Quectel's design guide |
| 19 | A voted control line shorts to ground or to a rail | n/a | the pull-down decides the safe state on an open; a hard short to a rail defeats the voter for that bit | read-back disagrees with quorum | a short is a board fault, not a covered failure |
| 20 | The whole control plane is unpopulated (a build without it) | n/a | every voted bit reads its pull-down, every bank rests on its home module, every hub is out of reset through its RC | n/a | the board is exactly the board before this work, which is the intended degradation |

## 13. Acceptance tests

The owner's kill tests, written as a matrix so the bench has no room for interpretation. All are run on the built
prototype; none has been run.

| # | Test | Method | Pass criterion |
|---|---|---|---|
| A1 | CM5 kill, cold | drop `SLOT_EN` for one slot | its bank is on the neighbour and every device of that bank enumerates within the per-device timeout; the other two banks are untouched |
| A2 | CM5 kill, hot | pull the module's power while traffic runs on its bank | as A1, plus no wedged device: the hub is reset in the sequence and every device re-enumerates |
| A3 | CM5 kill, twice | kill two modules in turn | exactly one bank is unreachable, the surviving module hosts two, and the state matches the ring of section 4 |
| A4 | IOCTRL kill | remove power from one supervisor | ownership does not move; the other two hold quorum; the removed one rejoins without moving anything on return |
| A5 | IOCTRL wedge | hold one supervisor in reset with its GPIOs pulled the wrong way, then run A1 | failover still happens and the wedged controller's votes are outvoted; read-back on the other two shows the voted value, not its vote |
| A6 | Two IOCTRL kill | remove power from two | no bank moves; every bank rests on its home module; the kit behaves as the pre-fabric board |
| A7 | Heartbeat fabric break | cut fabric A, then fabric B, one at a time | quorum survives each; the broken fabric reports bus-off; with both broken nothing moves |
| A8 | Voter stuck | force one voted line at its voter output | the three controllers report the read-back disagreeing with quorum, and the log names the bit |
| A9 | Bank rail independence | disable one slot's 3.3 V buck (`EN33_Sx`) with its module running | the bank's hub and both muxes stay up; the bank is movable |
| A10 | Break before make | scope `BOE{s}_n` and `BSEL{s}` through a failover | the enable is low for the whole select transition, with no overlap at the resolution of the scope |
| A11 | WiFi failover | disable the primary card | the voted `WIFI_SEC` moves both chains, the second card links to the peer kit, and the measured link margin is within 1 dB of the primary path |
| A12 | Dark plane | unpopulate or hold all three supervisors in reset from power-on | every bank comes up on its home module, every hub leaves reset, the kit works |
| A13 | USB bandwidth under failover | run the SDR at full rate on a bank that has failed over | throughput is measured and recorded; the neighbour hosting two banks is expected to share, and the number is what matters |
| A14 | EMCON through the fabric | assert EMCON while a bank is failed over | every transmitter of that bank is silenced, measured with the SDR, exactly as when it is home |

## 14. What it costs

**Parts, measured against the netlist this work started from** (`096b67c`, the board before the fabric): **756 parts
before, 925 after, +169**. By prefix: capacitors +69, resistors +52, integrated circuits +33, transistors +5, LEDs +3,
crystals +3, six U.FL receptacles, and two removals (the spare USB header, which became the 5G module's port, and one
fuse). Grouped by what they are for, on the placed board: the three supervisor blocks 66 parts (MCU, its LDO, two CAN
transceivers, crystal, SWD pads, status LED, decoupling and pulls, three times over), the voters and the
break-before-make 59, the three per-bank host selects 21, the WiFi antenna changeover 16, the CAN termination 12.
That is 22 percent more parts, and every one of them is a passive, a logic quad, a small mux or one of three MCUs.

**Area.** 2,709 mm2 of part bounding box, all of it on the **underside**, in pockets that carried nothing before:
the two gaps between the module columns (29 x 56 mm each), the free underside of the QMX bay, and the band between
the CM5 receptacles and the standoff row. The board outline does not change and no top-side block moves.

**Power.** About 0.9 W continuous added, dominated by the three supervisors (roughly 60 mA each at 3.3 V with the
core clocked to what CAN-FD timing needs, not to 480 MHz) and the six CAN transceivers (about 10 mA each). The rest
is negligible by measurement from the data sheets: the TMUXHS4212 draws 250 uA maximum, the TS3USB221A 30 uA, the
74LVC quads microamps, and the SKY13351 is a passive GaAs switch whose control pins draw microamps. The second WiFi
card adds about 0.3 W while it is powered and idle; it never transmits at the same time as the primary, because the
two share one pair of antennas.

**Rails, redistributed rather than increased.** Moving each bank's hub, its 1.1 V core and its two host selects off
the slot rails puts about **0.8 A more on `+5V_DEV`** and takes about 0.2 A off each slot rail. The kit draws the
same; A22's device-rail converter carries more of it and its three slot converters less, which is an item for A22's
next rail check and is recorded here so it is not discovered on the bench. `+3V3_DEV` is now a declared rail in the
intent layer at 1.2 A against U25's 2 A part, so `dc_drop.py` judges it like any other.

**What it does not cost.** No second board, no ribbon between boards, no change to the case, the face plate, the
antenna count or any other board's outline. The three PCIe switches stay, because the WiFi ruling kept the cards on
PCIe.
