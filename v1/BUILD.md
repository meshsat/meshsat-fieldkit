# Building a V1 kit (tesseract or parallax)

This is the kit as it was actually built in April 2026 and has run since: a Raspberry Pi 5 with a UPS, five radios, a satellite modem and a touchscreen on three HDPE plates in an IP67 case. Two exist, tesseract (RockBLOCK 9603, Iridium SBD) and parallax (RockBLOCK 9704, Iridium IMT). Everything else is identical. Budget about two days of bench time once the parts are in hand, plus the wait for the antenna bulkhead materials.

MeshSat is a prototype. A kit built from this page runs the Bridge software on the bench and in demos; it has not been through a real deployment.

The two Word files in `docs/` are the original checklists and pinout sheets (Rev C, Rev D). Where this page and those files disagree, this page wins: it reflects the wiring as audited live on both kits on 19 April 2026 and the later corrections (UART2 on parallax, the X1202 lines, the display power tap, the DCF77 pins on parallax).

## 1. Parts

One kit, 33 lines. Numbers are the BOM numbers from `docs/MeshSat-Field-Kit-BOM.docx`. The satellite line differs per kit.

| # | Part | Role | Connects to |
|---|---|---|---|
| 1 | Raspberry Pi 5, 8 GB | the Bridge computer | |
| 2 | Pi 5 active cooler | | Pi fan header |
| 3 | Geekworm X1202 UPS | 4 x 18650 UPS, fuel gauge, charging | Pi GPIO header (pogo pins) |
| 4 | Samsung INR18650-35E, 4 x | 50 Wh pack | X1202 holders |
| 19 | microSD 64 GB, A2 class | system disk | Pi slot |
| A1 / B1 | RockBLOCK 9603 (tesseract) or RockBLOCK 9704 (parallax) | satellite modem | Pi UART + GPIO, see section 6 |
| 17 | TAOGLAS IAA.01 Iridium antenna (puck) | | bulkhead 1 |
| 16 | Vecys LMR400 1 m SMA cable | no longer used inside the case; the internal run is a 15 cm pigtail | |
| 8 | ESP32-S3 LoRa, SX1262 868 MHz (XIAO) | Meshtastic radio | Pi USB-A, direct |
| 5 | Quansheng UV-K5(8) with custom firmware | APRS transceiver | 3.5 mm to the AIOC |
| 6 | SRH805S antenna, SMA female | reassigned to the RTL-SDR (RX only) | bulkhead 4 |
| 7 | AIOC v1.2 | audio and PTT for APRS | hub port 1 |
| 26 | LilyGO T-Call A7670E, V1.0 | 4G/2G modem (SMS, data) | Pi USB-A, direct |
| 18 | KPN prepaid SIM | | T-Call slot |
| 9 | RTL-SDR Blog V4 | spectrum monitor | hub port 3 (read from the USB tree on 25 April 2026) |
| 10 | RTL-SDR antenna set | | |
| 11 | ZigBee CC2652P coordinator (USB) | ZigBee | hub port 2 |
| 25 | Tuya ZigBee temperature and humidity sensor, IP65 | | paired to the coordinator |
| 27 | USB GPS, Gmouse u-blox 7 | position and time | hub port 3, cable through a gland, puck on the lid |
| 12 | Sabrent HB-UM43 4-port USB 3.0 hub | | Pi USB-A, direct; bus powered (the aux cable is optional) |
| 22 | DCF77 receiver module (DCF-1060N-800 class) | longwave time | Pi GPIO, see section 6 |
| 24 | Raspberry Pi Touch Display 2, 7 inch | operator display | Pi DSI port plus 5 V and GND from the header |
| 28 | Dupont wires, female to female | GPIO harness | |
| 13 | IP67 case | | |
| 14 | Cable glands PG7 / PG9 | GPS cable | case wall |
| 15 | Long USB-C cable | external power into the X1202 | |
| 20 | Mounting hardware (velcro, foam) | | |
| 29 | M3 nylon screws | | |
| 30 | PCB standoffs | | |
| 21 | Short internal USB cables | | |
| 31 | USB-C to USB-A, 0.15 m | | |
| 32 | USB 3.0 extension, 90 degree | | |
| 23 | ANENG SZ308+B15 multimeter combo | loose in the kit | |

Not on the BOM but part of the built kits: four M3 stainless threaded rods (110 mm) with 24 M3 nuts, three 3 mm black HDPE plates (section 4), the antenna bulkhead set below, an MT7612U USB WiFi dongle (Alfa AWUS036ACM or Panda PAU0D) for the kit-to-kit link (installed, disabled until antennas are fitted), and the WeAct 3.7 inch e-paper of the first build, which was decommissioned when the Touch Display 2 arrived (the Rev C pinout sheet records that change).

Antenna and bulkhead materials, per kit:

| Item | Qty |
|---|---|
| SMA female bulkhead, panel mount, waterproof (D-hole 6.5 mm) | 5 |
| SMA male to SMA male RG178 pigtail, 15 cm | 3 |
| u.FL/IPEX to SMA male RG1.13 pigtail, 15 cm | 2 |
| 868 MHz SMA whip, 2 to 3 dBi | 1 |
| 4G/LTE SMA stubby, wideband | 1 |
| Nagoya NA-771 VHF/UHF whip | 1 |
| SMA male to female 90 degree adapter | 1 |
| USB-C IP67 panel mount with cap | 1 |
| M12 IP68 vent plug (membrane) | 1 |
| 3 mm waterproof LED holder plus LED | 1 |

Cost reference, both kits together as bought in April 2026: EUR 1637 (about EUR 819 per kit), the 9704 being a Ground Control sample.

## 2. Tools

Drill with a step bit (6.5 mm and 12 to 16 mm holes), deburring tool, soldering iron and a crimp tool for the modem harness (Molex PicoBlade 1.25 mm on the 9603, the 16-pin connector on the 9704, dupont on the Pi side), a multimeter, a spot of thread locker for the rod nuts, IPA. FreeCAD if you want to change the plates. No spot welder: the V1 pack is four cells in the X1202's own holders.

## 3. Case preparation

Holes to drill per kit (8 or 9):

| Hole | Size | Where |
|---|---|---|
| SMA bulkhead x 5 | 6.5 mm D-hole | one wall, in a row, clear of the plate stack |
| USB-C panel mount | 12 to 16 mm (check the part) | front wall, reachable with the lid closed |
| M12 vent plug | 12 mm | bottom of the case |
| LED holder | 3 mm | front wall |
| Cable gland for the GPS cable | PG7 / PG9 | lid side, the puck mounts outside on the lid |

Bulkhead assignment, with the internal cable from each radio:

| Bulkhead | Radio inside | Internal cable | Antenna outside |
|---|---|---|---|
| 1 | Iridium modem | SMA to SMA RG178, 15 cm | TAOGLAS IAA.01 puck |
| 2 | ESP32-S3 LoRa | u.FL to SMA RG1.13, 15 cm | 868 MHz whip |
| 3 | T-Call A7670E | u.FL to SMA RG1.13, 15 cm | LTE stubby |
| 4 | RTL-SDR V4 | SMA to SMA RG178, 15 cm | SRH805S (receive only) |
| 5 | Quansheng UV-K5 | SMA to SMA RG178, 15 cm | Nagoya NA-771 through the 90 degree adapter |

The UV-K5 stays inside the case (it was external in the first plan). Label the row on the outside; the order above is the one on the built kits.

## 4. Plates and rods

The stack is modelled in `cad/` (FreeCAD, generated by `field_kit_build.py` from `field_kit_config.py`; `cad/README.md` explains how to run it and how to export DXF cut files). The numbers that matter:

| Plate | Size (mm) | Holes |
|---|---|---|
| bottom | 240 x 160 x 3 | 4 x M3 at the rod positions, cable pass-through |
| middle | 245 x 170 x 3 | 4 x M3, pass-through |
| top | 250 x 180 x 3 | 4 x M3, 5 x LED holes, the display cutout with the DSI pass-through |

The plates grow with the case taper. The four M3 rods stand on the case floor at the middle plate's corners, 12 mm in from its edges; all three plates are drilled at the same absolute positions. Every rod carries six nuts, one on each side of each plate. Gaps (top face of one plate to the bottom face of the next): bottom to middle 42.3 mm (set by the UV-K5, 37.5 mm, plus two nuts), middle to top 53.9 mm (set by the Pi 5 and X1202 stack hanging under the top plate). Rods 110 mm.

What goes where:

| Floor | Parts |
|---|---|
| bottom | UV-K5 with the AIOC strapped to it, the Sabrent hub, the GPS cable entry |
| middle | T-Call, RTL-SDR, XIAO ZigBee, DCF77 module, RockBLOCK |
| top | the Pi 5 pogo-mounted on the X1202, hung 1 mm under the top plate on standoffs; the Touch Display 2 recessed into the top plate's cutout so only the glass stands 1 mm proud, its board and connectors below the plate |

The FreeCAD model's component boxes are placeholders; verify fit with the real parts before cutting the display cutout. Cables are not modelled; leave a pass-through at the plate edge for the vertical runs and tie them to a rod.

## 5. Power

The X1202 takes four cells and charges from its USB-C or its barrel input; the case USB-C inlet feeds it. The Pi is powered from the X1202 through the pogo pins. The Sabrent hub runs bus-powered from one Pi USB-A port: with the EEPROM setting of section 7 the Pi's USB budget is 1.6 A and the hub's four devices advertise about 900 mA together (AIOC 100, GPS 100, RTL-SDR 500, ZigBee 100). Keep the hub's barrel-jack aux cable in the spares pouch; it goes back in only if the assembled kit shows USB drops or modem resets in the field. The T-Call and the WiFi dongle sit on the Pi's other USB controller, not behind the hub.

## 6. Harness (as wired, 19 April 2026 audit, with the later corrections)

All signals are 3.3 V. GPIO numbers are BCM; "pin" is the header pin. The chip is `/dev/gpiochip4` (RP1).

### parallax (RockBLOCK 9704, IMT)

| Pin | BCM | Direction | Signal | Goes to |
|---|---|---|---|---|
| 1 | | out | 3.3 V | DCF77 V |
| 2 | | out | 5 V | 9704 pin 15, V_IN+ |
| 3 | 2 | both | I2C1 SDA | X1202 fuel gauge (0x36) |
| 4 | | out | 5 V | Touch Display 2 V+ (loose jumper wire, see below) |
| 5 | 3 | both | I2C1 SCL | X1202 fuel gauge |
| 6 | | | GND | 9704 pin 16, V_IN- |
| 7 | 4 | out | UART2 TX | 9704 pin 14, RXD |
| 9 | | | GND | 9704 pin 1, signal ground |
| 14 | | | GND | Touch Display 2 GND (jumper wire) |
| 16 | 23 | in, pull-up | I_BTD (open drain) | 9704 pin 7 |
| 18 | 24 | out, low | P_EN (charger enable, active low) | 9704 pin 6 |
| 29 | 5 | in | UART2 RX | 9704 pin 13, TXD |
| 31 | 6 | in | AC-loss | X1202 |
| 35 | 19 | out, low | DCF77 P1 (enable, active low) | DCF77 P1 |
| 36 | 16 | out, low | charging control (low = enabled) | X1202 |
| 37 | 26 | out, on demand | I_EN (boot control) | 9704 pin 3 |
| 39 | | | GND | DCF77 G |
| 40 | 21 | in | DCF77 data | DCF77 T |

Serial `/dev/ttyAMA2` at 230400 8N1 (UART2 on BCM 4/5). Never use UART0 (BCM 14/15) for the 9704: its TXD is undefined at power-on and the kernel console reads garbage and panics. I_BTD is open drain; always read it with `gpioget --bias=pull-up gpiochip4 23`. The DCF77 wiring above (data BCM 21, enable BCM 19) is the field wiring of 23 April 2026; the Rev D sheet's BCM 12/20 was the plan before it.

### tesseract (RockBLOCK 9603, SBD)

| Pin | BCM | Direction | Signal | Goes to |
|---|---|---|---|---|
| 1 | | out | 3.3 V | DCF77 V |
| 2 | | out | 5 V | 9603 pin 8, V+ |
| 3 | 2 | both | I2C1 SDA | X1202 fuel gauge (0x36) |
| 4 | | out | 5 V | Touch Display 2 V+ (jumper wire) |
| 5 | 3 | both | I2C1 SCL | X1202 fuel gauge |
| 6 | | | GND | 9603 pin 10, GND |
| 8 | 14 | out | UART0 TX | 9603 pin 6, RXD |
| 10 | 15 | in | UART0 RX | 9603 pin 1, TXD |
| 14 | | | GND | Touch Display 2 GND (jumper wire) |
| 15 | 22 | in | NetAv | 9603 pin 4 |
| 16 | 23 | in | RI (active low) | 9603 pin 5 |
| 18 | 24 | | not wired | 9603 pin 7 OnOff stays unconnected, see below |
| 20 | | | GND | DCF77 G |
| 31 | 6 | in | AC-loss | X1202 |
| 32 | 12 | in | DCF77 data | DCF77 T |
| 36 | 16 | out, low | charging control | X1202 |
| 38 | 20 | out, low | DCF77 P1 | DCF77 P1 |

Serial `/dev/ttyAMA0` at 19200 8N1 (UART0). The 9603 Rev F OnOff pin needs 4.5 V to switch on and the Pi's pad clamps at about 3.8 V, so it is left unconnected (the modem defaults to on); driving it needs an N-MOSFET open-drain buffer (MESHSAT-669), not a direct wire.

### Touch Display 2 (both kits)

DSI ribbon (22 to 15 way) into the Pi 5 DSI connector; no GPIO signal pins. Power from header pin 4 (5 V) and pin 14 (GND) with loose jumper wires, not the bundled 3-wide lead: pins 2 and 6 are taken by the modem and the bundled shroud would cover pin 4.

### X1202 (both kits)

Pogo pins to the Pi header carry the supply; the I2C fuel gauge is at 0x36 (BCM 2/3), AC-loss on BCM 6 (read with pull-up), charging control on BCM 16 held low.

### Every device on the Pi (both kits)

What each device uses on the Pi, and what else it could use. "Used" is the wiring above and the USB tree read from `lsusb -t` on parallax on 25 April 2026; "offers" comes from the makers' documents where this repository holds them (the 9704 schematic and the X1202 page in `../v2/vendor/`, the AIOC sources, the Touch Display 2 brief) and from the makers' product pages otherwise.

| Device | Used on the Pi | Protocol used | Interfaces the device offers |
|---|---|---|---|
| Geekworm X1202 UPS | pogo pins (5 V to the Pi); header pins 3 and 5, 31, 36 | power; I2C1 fuel gauge 0x36; GPIO in (AC loss); GPIO out (charge control) | pogo-pin 5 V out to the Pi; USB-C in 5 V 5 A; DC 6 to 18 V in (XH2.54, also a 5.5 x 2.1 jack); two 5 V outputs (XH2.54); I2C to the fuel gauge; GPIO for AC loss and charge control; auto power-on |
| Raspberry Pi Touch Display 2 | DSI connector; header pins 4 and 14 | DSI video and touch; 5 V | DSI only (touch rides on the same ribbon); no HDMI, no USB |
| RockBLOCK 9704 (parallax) | header UART2 pins 7 and 29; GPIO pins 16, 18, 37; 5 V pin 2 | UART 230400 8N1; three GPIO lines; 5 V | 16-pin main connector: 3.3 V UART, control lines, power in; USB-C (USB to UART bridge on the board); RS232 as an alternative transceiver fit; battery connector; SMA |
| RockBLOCK 9603 (tesseract) | header UART0 pins 8 and 10; GPIO pins 15, 16; 5 V pin 2 | UART 19200 8N1; two GPIO inputs; 5 V | 10-way PicoBlade only: 3.3 V UART, NetAv, RI, OnOff, 5 V; no USB on the board (USB needs the maker's adapter); SMA |
| DCF77 receiver | header 3.3 V and GND; data pin 40 (parallax) or 32 (tesseract); enable pin 35 or 38 | GPIO bit stream; 3.3 V | four wires only: V, G, data out, enable; no bus |
| Pi 5 active cooler | fan header | 5 V, PWM, tacho | fan header only |
| LilyGO T-Call A7670E | Pi USB-A, direct | USB CDC serial (CH343 bridge) | USB-C to the ESP32; ESP32 header pins (UART, I2C, SPI, GPIO); the modem is reached only through the ESP32 firmware; u.FL antenna; SIM slot; battery connector |
| Alfa AWUS036ACM WiFi (MT7612U) | Pi USB-A, direct | USB | USB only (USB 3.0 plug, runs at USB 2.0 here); two RP-SMA antennas |
| XIAO ESP32-S3 LoRa (Meshtastic) | Pi USB-A, direct | USB CDC serial | USB-C native; header pins (UART, I2C, SPI, GPIO); own WiFi and BLE radios; u.FL |
| Sabrent HB-UM43 hub | Pi USB-A, direct | USB, bus-powered | USB 3.0 upstream; four USB-A downstream; optional 5 V aux input |
| AIOC v1.2 | hub port 1 | USB audio class plus CDC serial | USB only on the Pi side; radio side 3.5 and 2.5 mm Kenwood plugs (audio in, audio out, PTT, radio programming pass-through) |
| Gmouse u-blox 7 GPS | hub port 2 | USB CDC serial (NMEA) | USB only on the puck (the u-blox 7 chip also has UART, I2C and SPI, not brought out) |
| RTL-SDR Blog V4 | hub port 3 | USB bulk | USB only; SMA; bias-T out |
| ZigBee CC2652P coordinator | hub port 4 | USB CDC serial | USB only on the dongle (the CC2652P has UART and SPI, not brought out); SMA |
| Quansheng UV-K5(8) | none (through the AIOC) | none | Kenwood 2-pin: audio in, audio out, PTT, UART programming; no USB |
| microSD 64 GB | SD slot | SDIO | SDIO only |

All four Pi USB-A ports are taken (T-Call, WiFi dongle, XIAO, hub). Unused on both kits: the Pi's own USB-C power input (the X1202 feeds the pogo pins instead), Ethernet, both HDMI, the CSI and second DSI connector, PCIe, the 3-pin debug UART, and the SPI0 pins freed when the e-paper was retired.

## 7. Software

The kit runs Ubuntu Server 24.04 and the MeshSat Bridge in standalone mode (Docker Compose, privileged, direct serial). In this order:

1. **Flash** Ubuntu Server 24.04 (arm64) to the microSD, first boot with keyboard and screen or a serial console, set the hostname (`tesseract01`, `parallax01`), create the admin user, join WiFi.
2. **`/boot/firmware/config.txt`**, both kits, under `[all]`: `dtparam=i2c_arm=on`, `dtoverlay=vc4-kms-v3d`, `dtoverlay=vc4-kms-dsi-generic`, `dtoverlay=vc4-kms-dsi-7inch` (both display overlays are required, with only one the panel enumerates at 840 x 480 and stays dark), `disable_fw_kms_setup=1`, `enable_uart=0`, `display_auto_detect=1`. Under `[pi5]`: `dtoverlay=uart2-pi5` on parallax, `dtoverlay=uart0-pi5` on tesseract. In `cmdline.txt` remove `console=serial0,115200`.
3. **Bootloader EEPROM**: the Pi caps its USB ports at 600 mA unless the EEPROM says otherwise, and the kit draws about 1.5 A, so the LTE modem browns out on every burst without this. Apply and reboot:

   ```
   sudo tee /tmp/eeprom.txt >/dev/null <<'EOF'
   [all]
   BOOT_UART=1
   POWER_OFF_ON_HALT=1
   BOOT_ORDER=0xf41
   PSU_MAX_CURRENT=5000
   PCIE_PROBE=1
   EOF
   sudo rpi-eeprom-config --apply /tmp/eeprom.txt
   ```

   Verify with `vcgencmd get_config usb_max_current_enable` (must be 1).
4. **Kernel**: stay on `6.8.0-1051-raspi`. The 1052 build breaks the Touch Display 2 (DSI overlay collision) and fixes nothing the kit needs; do not run a bare `apt upgrade`. If a newer `linux-raspi` (6.14 or later) ships, test it on one kit with the display first.
5. **Bridge**: `curl -fsSL https://get.meshsat.net | sudo bash` installs Docker and the compose stack under `/srv/meshsat`. Set in the compose environment: `MESHSAT_MODE=direct`, `MESHSAT_AX25_KISS_ADDR=localhost:8001`, `MESHSAT_AX25_CALLSIGN`, and per kit `MESHSAT_IMT_PORT=/dev/ttyAMA2` (parallax) or `MESHSAT_IRIDIUM_PORT=/dev/ttyAMA0` with `MESHSAT_IRIDIUM_NETAV_PIN=22`, `MESHSAT_IRIDIUM_RI_PIN=23`, `MESHSAT_IRIDIUM_ONOFF_PIN=0` (tesseract). DCF77 on parallax: `MESHSAT_DCF77_ENABLED=true`, `MESHSAT_DCF77_DATA_PIN=21`, `MESHSAT_DCF77_PON_PIN=19`. USB devices are found by VID:PID; never pin a `ttyUSB` or `ttyACM` path.
6. **Host services** from the meshsat repository (clone it on the kit or copy the files):
   - `scripts/install-kiosk.sh` (run as root): labwc plus Chromium kiosk on the Touch Display 2, autologin, touch rotation, nightly restart. Tesseract's panel is mounted flipped 180 degrees relative to parallax: after the installer, change its labwc autostart to `--transform 270` and the udev calibration matrix to `0 1 0 -1 0 1`.
   - `scripts/install-kit-network.sh` then reboot: WiFi roaming fix (`brcmfmac roamoff=1`), power save off, the management keepalive, the MT7612U dongle option, the kit-to-kit link unit (disabled until antennas are on).
   - `scripts/x1202-monitor.py` to `/usr/local/bin/`, run as a systemd service (`x1202-monitor.service`); it writes `/run/x1202.json` every 10 s, and the compose file needs the bind mount `/run/x1202.json:/run/x1202.json:ro` (recreate the container after adding it).
   - A GPIO hold service (`meshsat-gpio.service`) that keeps the control lines in their safe state at boot: `gpioset --mode=signal gpiochip4 24=0 26=0 20=0 16=0` on parallax (P_EN, I_EN, DCF77 P1, X1202 charging). On tesseract hold 20 and 16.
   - parallax only: the 9704 power script (`meshsat-9704-power.sh on|off|status`) that sequences I_EN and reads I_BTD.
   - `scripts/install-oob-agent.sh`: the host agent for remote management commands (reboot, reset, log, network status) over any bearer.
   - On kernel 1051 the Touch Display 2 touch controller can lose the probe race at boot; if touch is dead after a boot, install the small `goodix-touch-rebind` service (sleep 10 s, then `echo 11-005d > /sys/bus/i2c/drivers/Goodix-TS/bind`).
7. **APRS**: flash the AIOC and configure the gateway as in `docs/direwolf-aioc-setup.md` (the Bridge bundles Direwolf; the AIOC is the sound card and PTT).
8. **Radios**: Meshtastic on the XIAO (both kits on one primary encrypted channel), T-Call with the stock `ATdebug.ino` passthrough firmware and the SIM PIN disabled, RTL-SDR and ZigBee need no configuration.

Traps that cost days on the built kits: never send USSD (`AT+CUSD`) through the modem, it blocks the AT channel until a power toggle; never change `/etc/netplan/` over the kit's own WiFi, it is the only management path into a sealed box; the T-Call takes about 30 s after `AT+CPIN` before it answers, that is not a fault; MT7921U WiFi dongles drop off the bus on this kernel, only the MT7612U works.

## 8. Checks that prove the kit

1. `lsusb -t` shows the hub with its four devices, the T-Call (`1a86:55d4`), the XIAO and the RTL-SDR; no `over-current` in `dmesg`.
2. `vcgencmd get_config usb_max_current_enable` = 1; `uname -r` = `6.8.0-1051-raspi`.
3. The display shows the operator dashboard; touch works in the display's orientation.
4. `curl localhost:6050/api/system/battery` returns voltage and state of charge from the X1202; the Battery tile follows.
5. Satellite: parallax `meshsat-9704-power.sh status` reports the modem booted and the Bridge's JSPR handshake succeeds; tesseract the SBD modem answers `AT` at 19200 and `NetAv` follows the sky.
6. APRS: a test frame from the UV-K5 decodes in the Bridge (Direwolf on `localhost:8001`).
7. RUN FULL DEMO from the operator dashboard exercises mesh, APRS, cellular, Hub and Reticulum; the Iridium leg needs sky.
8. Battery runtime: about 6 to 9 h from the four cells at 5.5 W idle to 14 W active; the case USB-C inlet extends it.
