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

## 11. Open rulings

1. **CLOSED 9 September 2026 by the owner's condition: WiFi stays on PCIe.** The condition was that the radio must do peer-to-peer links with no access point. The gate fails for USB: **MT7921, the embeddable USB WiFi 6 chip, does not support mesh point mode** (openwrt/mt76 issue 653, 2022, cited in morrownr/USB-WiFi issue 526, where the question of hardware, firmware or driver cause was asked and never answered). The mt76 chip that does mesh over USB is the MT7612U, and the 5 September research had already established that **no embeddable MT7612U module exists**, which is why that ruling moved WiFi to M.2 PCIe in the first place. The MT7915 in the AW7915-AED is documented for AP, station and mesh in its kernel submission, so the card stays. The consequence is that the PCIe switches are not deleted and no area is freed there.
2. **CLOSED: one board.** The underside under the three CM5 modules, X -98 to 94 and Y 32 to 88, is **10,752 mm2 and carries nothing** (`gen_pcb_b3.py` places no back-side region there). The control plane needs roughly 2,400 mm2: about 650 mm2 per controller for the MCU, two CAN transceivers, its regulator, supervisor, crystal and SWD pads, plus about 450 mm2 of voters. It fits on the underside with room for routing, so no second board and no ribbon. B16's underside clears D8's SA868 by about 20 mm, which an LQFP part uses 1.7 mm of; a gate for back-side clearance to A22 does not exist yet and is added with the rest.
3. **CLOSED 9 September 2026, the owner asked for a recommendation and took it: the WiFi card is DUPLICATED and the two cards SHARE the antennas.** Slot 3's spare M-key drive socket becomes a second E-key socket carrying a second AW7915-AED, so any single module loss leaves one mesh radio. The two cards feed the **existing** pair of P2P antennas through a passive RF changeover, because every case penetration is a seal under the no-vent ruling of 7 September and two more jacks would be a case change: the end walls, the 1:1 template and A22's jack count all stay as they are. Only one radio is live at a time, which is what failover needs rather than capacity; the price is about 0.5 dB of insertion loss on the primary path. The changeover follows the voted "secondary active" signal and pulls to the primary card, so a dark control plane leaves the primary connected. The RF switch part is picked from the manufacturer's own data, not from a distributor listing. The trade accepted here is a fourth spare drive slot, which k3s does not need with three replicas, against a redundant kit-to-kit link.
4. **OPEN: 5G to USB 3.0.** The RM520N-GL supports both PCIe and USB 3.1 Gen1, and moving it to USB would put cellular into the failover fabric and delete one PCIe switch. Gated on Quectel's hardware design guide, which is not yet on file.
5. **B18 is superseded.** Its information route remains useful as placement data; no B release is cut against the current topology.
