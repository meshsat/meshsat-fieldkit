# Building a V1 kit (tesseract or parallax)

This page describes the two V1 kits as they stand on 13 November 2026: a Raspberry Pi 5 with a UPS, three radios, a cellular modem, a satellite modem and a touchscreen on three HDPE plates in an IP67 case. Both kits are now built the same way. They were first built in April 2026; what changed since is in section 9. Before a kit goes to a demo day it passes the [acceptance checklist](ACCEPTANCE.md).

MeshSat is a prototype. A kit built from this page runs the Bridge software on the bench and in demos; it has not been through a real deployment.

The two Word files in `docs/` are the April checklists and pinout sheets (Rev C, Rev D). Where they disagree with this page, this page wins.

## 1. Parts

One kit. Numbers are the BOM numbers from `docs/MeshSat-Field-Kit-BOM.docx`; a dash marks a part added after April.

| # | Part | Role | Connects to |
|---|---|---|---|
| 1 | Raspberry Pi 5, 8 GB | the Bridge computer | |
| 2 | Pi 5 active cooler | | Pi fan header |
| 3 | Geekworm X1202 UPS | four-cell UPS, fuel gauge, the only charger | Pi GPIO header (pogo pins) |
| 4 | Samsung INR18650-35E, 4 x | about 50 Wh | X1202 holders |
| - | Raspberry Pi RTC battery (ML2020) | keeps the clock while the kit is off | Pi RTC connector |
| 19 | microSD 64 GB, A2 class | system disk | Pi slot |
| - | RockBLOCK Mk2 (Iridium 9602, SBD) | satellite modem | Pi UART2 and 5 V, section 6 |
| 17 | TAOGLAS IAA.01 Iridium antenna (puck) | | bulkhead, section 3 |
| - | LILYGO T-Echo (nRF52840, SX1262, 868 MHz) | Meshtastic mesh radio; own cell and power switch | Pi USB, direct |
| - | PicoAPRS V4 VHF | APRS transceiver with its own KISS TNC; own 850 mAh cell | Pi USB, direct |
| 26 | LilyGO T-Call A7670E, V1.0 | 4G/2G modem (SMS, data) | Pi USB, direct |
| 18 | KPN prepaid SIM | | T-Call slot |
| 24 | Raspberry Pi Touch Display 2, 7 inch | operator display | Pi DSI port, 5 V and GND from the header |
| - | Mean Well GST60A12-P1J, 12 V | supply, stays indoors | the case's 12 V inlet, section 5 |
| 13 | IP67 case | | |
| 28 | Dupont wires, female to female | modem harness | |
| 21, 31 | Short USB cables | | |
| 20, 29, 30 | Velcro, foam, M3 nylon screws, standoffs | | |
| 23 | ANENG SZ308+B15 multimeter combo | loose in the kit | |

Not on the BOM but part of the kits: four M3 stainless threaded rods (110 mm) with 24 M3 nuts, three 3 mm black HDPE plates (section 4), and the antenna bulkhead set below.

All three USB devices sit directly on the Pi's own ports. There is no USB hub in the kit.

Antenna and bulkhead materials, per kit:

| Item | Qty |
|---|---|
| SMA female bulkhead, panel mount, waterproof (D-hole 6.5 mm) | 5 |
| SMA pigtails, 15 cm (RG178 SMA to SMA, RG1.13 u.FL to SMA) | as in section 3 |
| 868 MHz SMA whip, 2 to 3 dBi | 1 |
| 4G/LTE SMA stubby, wideband | 1 |
| VHF antenna for the PicoAPRS | 1 |
| SMA male to female 90 degree adapter | 1 |
| TY16 panel socket and plug (12 V inlet) | 1 set |
| M12 IP68 vent plug (membrane) | 1 |
| 3 mm waterproof LED holder plus LED | 1 |

Cost reference, both kits together as bought in April 2026: EUR 1637 (about EUR 819 per kit). The radios changed since; the project's expense records hold the rest.

## 2. Tools

Drill with a step bit (6.5 mm and 16.5 mm holes), deburring tool, a crimp tool for Dupont housings, a multimeter, an SMA torque wrench that breaks over at 1 Nm, a spot of thread locker for the rod nuts, IPA. FreeCAD if you want to change the plates. No soldering: the pack is four cells in the X1202's own holders.

## 3. Case preparation

Holes to drill per kit:

| Hole | Size | Where |
|---|---|---|
| SMA bulkhead x 5 | 6.5 mm D-hole | one wall, in a row, clear of the plate stack |
| 12 V inlet | 16.5 mm for the TY16 back-nut socket | front wall, reachable with the lid closed; the socket is rated for walls up to 3 mm |
| M12 vent plug | 12 mm | bottom of the case |
| LED holder | 3 mm | front wall |

Bulkhead assignment, with the internal cable from each radio:

As built in April 2026. The radios behind sockets 2, 4 and 5 have changed since (section 9); the sockets are re-checked with the case open and this table is updated then.

| Bulkhead | Radio inside (April) | Internal cable | Antenna outside |
|---|---|---|---|
| 1 | Iridium modem | SMA to SMA RG178, 15 cm | TAOGLAS IAA.01 puck |
| 2 | LoRa radio | u.FL to SMA RG1.13, 15 cm | 868 MHz whip |
| 3 | T-Call A7670E | u.FL to SMA RG1.13, 15 cm | LTE stubby |
| 4 | RTL-SDR V4 (taken out) | SMA to SMA RG178, 15 cm | SRH805S |
| 5 | APRS radio | SMA to SMA RG178, 15 cm | Nagoya NA-771 through the 90 degree adapter |

Tighten every SMA joint, inside and outside, with the 1 Nm wrench, and again after any antenna work. A loose SMA joint looks exactly like "no satellite": on 25 September 2026 the torque wrench was what got both kits a working Iridium link.

### The PicoAPRS units

| | tesseract | parallax |
|---|---|---|
| Device ID | 255202693282056 | 180444492527880 |
| SW / Modem version | 26 / 22B | 26 / 22B |
| CP2102N serial | 36414a145c57ed11aeab52ca5720eef3 | 1cb04e3ba957ed11928b4aca5720eef3 |
| Callsign the Bridge sends as | MSTSRT-10 | MSPRLX-10 |

The CP2102N serial tells the two units apart without opening a case: it is the `/dev/serial/by-id/` name the Bridge opens. Never swap the units between kits without changing the Bridge's APRS device and callsign with them: a unit discards frames sent from its own callsign. Radio settings live on the units' buttons only and survive no firmware update or factory reset, so re-read them after either: VHF 1 W, APRS 1 W, VHF BW Wide on, FM Noise Cancel off, AFSK BW Wide on, AFSK RX volume about three quarters.

A PicoAPRS runs on its own cell when USB power is gone, shuts down when the cell is empty, and only a 3 s press of its PTT button, inside the case, turns it on again. After anything touches an APRS connector, count frames before trusting the link: `rx` and `tx` on the Bridge's APRS status on both kits seven minutes apart. 30 dB attenuator pads were tried on both kits on 16 September 2026 and made both deaf; do not fit them.

## 4. Plates and rods

The stack is modelled in `cad/` (FreeCAD, generated by `field_kit_build.py` from `field_kit_config.py`; `cad/README.md` explains how to run it and how to export DXF cut files).

| Plate | Size (mm) | Holes |
|---|---|---|
| bottom | 240 x 160 x 3 | 4 x M3 at the rod positions, cable pass-through |
| middle | 245 x 170 x 3 | 4 x M3, pass-through |
| top | 250 x 180 x 3 | 4 x M3, 5 x LED holes, the display cutout with the DSI pass-through |

The plates grow with the case taper. The four M3 rods stand on the case floor at the middle plate's corners, 12 mm in from its edges; all three plates are drilled at the same absolute positions. Every rod carries six nuts, one on each side of each plate. Rods 110 mm.

What went where in April: the bottom plate carried the APRS radio and the USB hub, the middle plate the T-Call, the RTL-SDR, the ZigBee coordinator and the RockBLOCK, and the top plate the Pi 5 on the X1202, hung under it on standoffs, with the Touch Display 2 recessed into its cutout. Parts have been taken out and swapped since (section 9); today's layout is re-checked with the case open and added here then.

## 5. Power

12 V from a Mean Well GST60A12-P1J brick into the X1202's DC input (6 to 18 V), through a TY16 panel socket in the case wall. The brick and its cord are indoor-grade and stay indoors; for a kit outside, extend the 12 V lead, never the mains side. At 27 W and a 9 V floor at the kit, 2 x 1.0 mm² rubber cable (H05RN-F or H07RN-F) reaches about 27 m; check its outer diameter against the TY16 plug's 4.5 to 7.5 mm seal. Never feed the X1202's USB-C input at the same time: a 5 V input cannot carry the kit and the charger together.

The X1202 is the only charger. The Pi runs from it through the pogo pins, and the USB devices from the Pi's ports (the EEPROM setting of section 7 raises the Pi's USB budget to 1.6 A). `sudo poweroff` cuts all of the X1202's output; never stop the Bridge container first, or it stays stopped after the next start.

Two radios carry their own cells. The T-Echo keeps running, and transmitting, when the kit is off: switch it off by hand for storage. The PicoAPRS shuts itself down when its cell runs empty (section 3).

The RTC battery keeps the clock through a power cut. Check it charges: `cat /sys/class/rtc/rtc0/charging_voltage` must not be 0.

## 6. Harness (both kits)

All signals are 3.3 V. GPIO numbers are BCM; "pin" is the header pin. The chip is `/dev/gpiochip4` (RP1).

### RockBLOCK Mk2

The Mk2 runs on the eight-wire Dupont harness first made for the 9704, from the X1202's stacking header on top of the Pi. One page wiring sheet: `docs/MeshSat-Field-Kit-RockBLOCK-Mk2-wiring-sheet.pdf`.

| Pi pin | Signal | Mk2 | Colour |
|---|---|---|---|
| 2 | 5 V | 8, 5vIn | yellow |
| 6 | GND | 7, GND | teal |
| 9 | GND | 14, GND | black |
| 7 | UART2 TX | 3, TXD | purple |
| 29 | UART2 RX | 2, RXD | blue |
| 16 | RI (off in software) | 10, RI | grey |
| 18 | | taped off | olive |
| 37 | | taped off | orange |

Serial `/dev/ttyAMA2` at 19200 8N1. The RI pin stays off in the Bridge (`MESHSAT_IRIDIUM_RI_PIN=0`): with it on, the lead picked up noise and raised false ring alerts on both kits. The Bridge takes ring alerts over the UART instead. Before RI goes back on, meter the Mk2's RI drive and add a 4.7 kΩ pull-up to 3.3 V at the Pi end if it is open-collector. Never use UART0 (BCM 14/15) for a modem on these kits: its TXD is undefined at power-on and the kernel console reads garbage and panics.

### Touch Display 2

DSI ribbon (22 to 15 way) into the Pi 5 DSI connector. Power from header pin 4 (5 V, red) and pin 14 (GND, black) on loose jumper wires. A panel that stays dim with everything set to full in software has lost its 5 V lead from pin 4.

### X1202

Pogo pins to the Pi carry the supply; the I2C fuel gauge is at 0x36 (BCM 2/3), AC-loss on BCM 6 (read with pull-up), charging control on BCM 16 held low.

## 7. Software

The kit runs Ubuntu Server 24.04 and the MeshSat Bridge in standalone mode (Docker Compose, privileged, direct serial). In this order:

1. **Flash** Ubuntu Server 24.04 (arm64) to the microSD, first boot with keyboard and screen, set the hostname (`tesseract01`, `parallax01`), create the admin user, join WiFi.
2. **`/boot/firmware/config.txt`**, as on both kits (read 13 November 2026), on top of Ubuntu's defaults:

   ```
   [all]
   enable_uart=0
   dtparam=i2c_arm=on
   dtoverlay=vc4-kms-v3d
   dtoverlay=vc4-kms-dsi-generic
   disable_fw_kms_setup=1
   display_auto_detect=0
   [pi5]
   dtoverlay=uart2-pi5
   dtoverlay=vc4-kms-dsi-7inch
   dtoverlay=vc4-kms-dsi-ili9881-7inch
   display_lcd_rotate=2
   [all]
   dtparam=rtc_bbat_vchg=3000000
   ```

   The Touch Display 2's own overlay (`ili9881`) must come after `vc4-kms-dsi-7inch`, with auto-detect off, or the panel stays dark after a warm reboot. `rtc_bbat_vchg` charges the RTC battery. In `cmdline.txt` remove `console=serial0,115200` (the kits keep `console=tty1` only). Keep every line under 98 characters, comments included: the firmware drops longer lines without a word.
3. **Bootloader EEPROM**: the Pi caps its USB ports at 600 mA unless the EEPROM says otherwise, and the cellular modem browns out on every burst without this. Apply and reboot:

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
4. **Kernel**: stay on `6.8.0-1051-raspi`. The 1052 build blanks the Touch Display 2; never run a bare `apt upgrade`.
5. **Bridge**: `curl -fsSL https://get.meshsat.net | sudo bash` installs Docker and the compose stack under `/srv/meshsat`. Per-kit values live only in `/srv/meshsat/.env`; both kits run the same compose file. Satellite: `MESHSAT_IRIDIUM_PORT=/dev/ttyAMA2`, `MESHSAT_IRIDIUM_RI_PIN=0`, `MESHSAT_IRIDIUM_NETAV_PIN=0`, `MESHSAT_IRIDIUM_ONOFF_PIN=0`, `MESHSAT_IMT_PORT=auto`. APRS: the callsign of section 3 in three places that must agree (the APRS gateway's settings, `MESHSAT_AX25_CALLSIGN`, and the other kit's management peer), and the APRS gateway's device set to the unit's `/dev/serial/by-id/` path. Other USB devices are found by VID:PID; never pin a `ttyUSB` or `ttyACM` path.
6. **Host services** from the meshsat repository:
   - `scripts/install-kiosk.sh`: labwc and a Chromium kiosk on the Touch Display 2. Its first step installs packages; on a built kit place changed kiosk files by hand instead of running it again. The two panels sit turned differently in their lids, so each kit has its own touch calibration matrix in udev: tesseract `0 -1 1 1 0 0`, parallax `0 1 0 -1 0 1`.
   - `scripts/install-kit-network.sh`, then reboot: WiFi roaming fix (`brcmfmac roamoff=1`), power save off, the management keepalive. WiFi is the only way into a closed kit: never change `/etc/netplan/` over it.
   - `scripts/x1202-monitor.py` as `x1202-monitor.service`; it writes `/run/x1202.json`, which the compose file mounts read-only into the Bridge.
   - `scripts/install-oob-agent.sh`: the host agent for remote management commands over any bearer.
   - The clock guard, ordered before Docker; after any boot, `journalctl -b | grep -i "ordering cycle"` must print nothing.
   - If touch is dead after a boot, the `goodix-touch-rebind` service (sleep 10 s, then rebind `11-005d` to the Goodix driver).
   - `meshsat-gpio.service` (`/usr/local/bin/meshsat-gpio-init.sh`) holds BCM 16 low at boot, which keeps the X1202 charging. It also still holds BCM 24 and 20 low, left from the 9704 and the DCF77; their wires are taped off or not fitted.
7. **Radios**: the T-Echo on Meshtastic 2.8 with role CLIENT_MUTE and `security.debug_log_api_enabled` on, each kit on its own channel; export its config before any flash. The T-Call on the stock `ATdebug.ino` passthrough firmware with the SIM PIN off. The PicoAPRS as in section 3.

Traps that cost days on these kits: never send USSD (`AT+CUSD`) through the modem, it blocks the AT channel until a power toggle; the T-Call takes about 30 s after `AT+CPIN` before it answers, that is not a fault; any open of the T-Call's serial port reboots its ESP32, which is why the Bridge opens it with DTR and RTS low; MT7921U WiFi dongles drop off the bus on this kernel.

## 8. Checks that prove the kit

The [acceptance checklist](ACCEPTANCE.md): case and antennas, power and start-up, the Bridge, one real message each way on every channel, and RUN FULL DEMO. Every run is published in [`acceptance/`](acceptance/).

## 9. What changed since April 2026

| Date | Change |
|---|---|
| 4 to 16 Sep 2026 | The USB-C power inlet replaced by 12 V into the X1202's DC input (a 5 V input could not carry the kit and the charger together) |
| 10 Sep 2026 | APRS: the PicoAPRS V4 replaced the UV-K5 and the AIOC; no sound card, no Direwolf |
| 13 Sep 2026 | The Touch Display 2 overlay pinned, so the panel survives a warm reboot |
| 18 Sep 2026 | Mesh: a LILYGO T-Echo replaced the XIAO ESP32-S3 |
| 20 Sep 2026 | The ZigBee coordinator and sensor and the GPS taken out |
| 17 Oct 2026 | The RTL-SDR taken out; the 9704 of tesseract moved to the compact kit |
| 23 Oct 2026 | Both kits on a RockBLOCK Mk2 (9602, SBD) on UART2; parallax's 9704 out |
| autumn 2026 | RTC batteries fitted; the USB hubs gone; the DCF77 receiver never wired |

The parts taken out are kept as spares. Each kit's Bridge marks them as removed, so its device log does not count their absence as a fault.
