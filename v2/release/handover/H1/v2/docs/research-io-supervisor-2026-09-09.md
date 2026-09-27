# The I/O supervisor part, STM32H753 against i.MX RT1180 (9 September 2026, 18:30 CEST)

Stage 2 of the PCB-B I/O high-availability work (`ARCH-PCB-B-IOHA.md`, MESHSAT-862). The owner set the baseline at
three STM32H753 and asked for the i.MX RT1180 to be compared against it with **raw speed weighted last**. This note is
that comparison, every line cited, plus the two documentation gates the same stage owed (the WiFi radio and the 5G
module) and the alternate-function confirmation the architecture note left open. Prototype work: no board is built.

## 1. What the part has to do

The supervisor is never in the data path. It carries two independent CAN-FD heartbeat fabrics, reads three module
heartbeats, drives seven voted control bits into commodity logic, holds an I2C link for status, and runs a watchdog.
That is the whole job: 4 CAN pins, 7 outputs, 3 inputs, 2 I2C, SWD, reset, boot, crystal. About 25 signal pins.

## 2. The candidates as documented

| | STM32H753VITx (baseline) | i.MX RT1180 (MIMXRT1189/1181) |
|---|---|---|
| Cores | one Cortex-M7 at 480 MHz | Cortex-M7 at 800 MHz plus Cortex-M33 at 300 MHz, single-core M33 variant offered |
| Internal flash | 2 MB, boots on its own | none; a crossover MCU boots from external XSPI flash |
| RAM | 1 MB | 1.5 MB with ECC |
| CAN-FD | 2 instances, exactly the two independent fabrics the architecture needs | 3 instances |
| Packages | LQFP-100 14 x 14 at 0.5 mm, leaded, no via in pad | MAPBGA only: 144 (10 x 10), 196 (12 x 12), 289 (14 x 14), all 0.8 mm pitch |
| Temperature | -40 to +85 C (VIT6), a 105 C grade offered | -40 to +125 C |
| Extras that matter here | none needed | EdgeLock secure enclave, Gb TSN switch |
| JLCPCB stock, read 9 Sep 2026 | STM32H753VIT6 C730206: **0**. STM32H743VIT6 C114409: **1465**, same pinout | MIMXRT1189CVM8C C42760676: **0**, and no other RT118x part is listed at all |

Sources: ST's STM32H753xI datasheet (DS12117) for the H7 line; NXP's i.MX RT1180 product page and family fact sheet for
the cores, the TSN switch, the packages and the temperature range, and NXP's data sheet IMXRT1180EC for the three
CAN-FD instances; JLCPCB's parts API for the stock figures, which is the availability instrument this repo already uses.

## 3. The comparison, in the owner's order of weight

**1. Fitness for the job.** The H753 needs two CAN-FD and has exactly two. The RT1180 has three, which buys nothing
here. The decisive difference is the other way round: the RT1180 has no internal flash, so every supervisor grows an
external XSPI flash, its decoupling and a boot dependency. Three supervisors become three more parts that can fail and
three more boot paths that can corrupt. A supervisor that cannot boot without a second chip is a worse supervisor.

**2. No new hidden single points of failure.** Same argument, stated as the owner's rule: the external flash is a new
single point per controller, and the RT1180's TSN switch would invite folding the Ethernet plane into the control
plane, which would put the data path back inside the supervisor. The H753 adds nothing to the failure list.

**3. Buyability.** The RT118x family cannot be bought through the assembler at all today. The H753VIT6 cannot either,
but its pin-compatible sibling the H743VIT6 can, 1465 in stock. This is the difference between a board that can be
ordered and one that cannot.

**4. Assembly and rework.** LQFP-100 at 0.5 mm is inspected optically and reworked with a hot-air pencil. A 0.8 mm
MAPBGA needs X-ray to inspect and cannot be reworked by hand at all, on a prototype where the supervisors are the
part most likely to be rewired.

**5. Board area and routing.** LQFP-100 escapes on the surface layer with no via in pad. A 196-ball BGA at 0.8 mm needs
dogbone escapes on the inner layers and pushes the stack-up and drill class, on a six-layer board that already carries
the CM5 receptacles at 0.4 mm. It would also not fit the three separate underside pockets the failure-domain rule asks
for (each is 29 x 56 mm).

**6. Power.** Three supervisors run continuously, including in the kit's reduced modes. An M7 at 480 MHz with the
clock dialled back to what a heartbeat needs is tens of milliamps; an 800 MHz M7 plus an M33 plus an external flash is
several times that, on a battery kit.

**7. Temperature.** The RT1180 wins, 125 C against 85 C. Nothing on this board runs near either figure with the fans
in the ruling of 7 September; the pack is the temperature-limited part.

**8. Raw speed, weighted last as instructed.** The RT1180 is far faster and the supervisor does not need it. Its work
is a few kilobytes of state machine and two CAN mailboxes.

## 4. Verdict

**The STM32H753 stands, bought as the STM32H743VIT6.** The RT1180 is the better processor and the worse supervisor
here: no internal flash, BGA only, and nothing in stock. What would reverse it: a requirement for TSN Ethernet in the
control plane, or an RT118x part in a leaded package with internal flash.

The substitution is recorded where it is made: `gen_sch_b.py` carries the H753VI pin table, because the two parts share
it, and the LCSC code of the H743VIT6 with the reason in the same line. The crypto accelerator is the only difference
and this design does not use it (the kit's secure element is the ATECC608B on another board).

## 5. The alternate functions, confirmed

The architecture note left the FDCAN mapping to be confirmed. **FDCAN1_RX on PD0 and FDCAN1_TX on PD1, FDCAN2_RX on
PB12 and FDCAN2_TX on PB13, all alternate function 9**, which is what `gen_sch_b.py` wires on pins 81, 82, 51 and 52
of the LQFP-100.

Source with a caveat worth recording: **st.com refuses both this runner and the rented box** (connection refused, not
a 403), so ST's own PDF could not be read here; it joins wiki.geekworm.com, amphenolrf.com and keyelco.com on that
list. The mapping was taken instead from the pin control file for this exact part number,
`dts/st/h7/stm32h753vitx-pinctrl.dtsi` in `zephyrproject-rtos/hal_stm32`, which is generated from ST's own CubeMX
database and gives `fdcan1_rx_pd0 = STM32_PINMUX('D', 0, AF9)` and its three companions. The same file shows the other
options (PA11/PA12 and PB8/PB9 for FDCAN1, PB5/PB6 for FDCAN2), none of which is used here.

## 6. The two documentation gates of the same stage

**WiFi, closed on evidence.** The condition was that the radio must do peer to peer links with no access point. The
MT7921, the embeddable USB WiFi 6 chip, does not support mesh point mode (openwrt/mt76 issue 653), and the mt76 part
that does mesh over USB, the MT7612U, has no embeddable module, which is why the 5 September ruling moved WiFi to M.2
PCIe in the first place. The MT7915 in the AW7915-AED is documented for AP, station and mesh in its kernel submission.
So WiFi stays on PCIe, and the redundancy comes from a second card on slot 3 rather than from a second bus.

**5G on USB 3.0, still open.** The RM520N-GL is documented for both PCIe and USB 3.1 Gen1, but Quectel's hardware
design guide is not on file and the module's USB 3 mode is not something to design against a search result. It stays
open ruling 4 of the architecture note. The consequence is recorded there: the cellular data path is slot 2's PCIe lane
and dies with slot 2.

## 7. The changeover part, for the record

The antenna changeover of ruling 3 is the **Skyworks SKY13351-378LF**, from data sheet 201132I: 20 MHz to 6.0 GHz,
insertion loss 0.35 dB typical below 3 GHz and 0.50 dB from 3 to 6 GHz, isolation 24 dB, 0.5 dB compression at
+30 dBm against the card's +20 dBm, control on 0 V and 1.8 to 5.0 V applied to VCTL1 or VCTL2, and every RF port must
be DC blocked. JLCPCB C129189, 17337 in stock. Its land pattern is drawn from Figure 12 of that data sheet rather than
borrowed from a library part, and the ground land that merges with the exposed soldering area is drawn as it is drawn
there.
