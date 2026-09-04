# MeshSat control panel (PCB-C C4): software contract for the bridge

Hardware record: `MESHSAT-709-geometry-appendix.md` section 25.4. Bus: the kit I2C (SDA/SCL on the panel ribbon), SPI0 for the e-paper, three Pi GPIOs. Everything below is what the bridge must implement; nothing on the panel works without it except MAIN PWR, PI, EMCON and the TX lamp, which are hardware.

## 1. Expanders (PCA9555, 16-bit, INT wire-ORed on EXP_INT)

U1 at 0x22. Port 0 = LED cathodes (sinks), port 1 = inputs.

| Bit | Port 0 (output, LED sink) | Port 1 (input, active low unless stated) |
|---|---|---|
| 0 | SOS ACTIVE (red) | SOS_SW: locking toggle, maintained, closed = low (APEM 5636ADKB-2V, both positions locked; ruling 32.13) |
| 1 | MASTER WARN (red) | TX_INHIBIT_n: EMCON cover closed = low (hardware inhibit is already active) |
| 2 | MASTER CAUT (amber) | ZEROIZE_SW: locking toggle, maintained, closed = low (APEM 5636ADKB-2V; ruling 32.13) |
| 3 | CHARGING (white) | TEST_SW: TEST / ACK button, pressed = low |
| 4 | SAT (green) | LIGHT_DAY_n: LIGHTING at DAY = low |
| 5 | MESH (green) | LIGHT_NIGHT_n: LIGHTING at NIGHT = low (both high = BLACKOUT) |
| 6 | LTE (green) | RAIL_SENSE: LED rail present = high |
| 7 | GPS (green) | PANEL_ID: strap JP1, open = variant A (high), closed = B (low) |

U2 at 0x23. Port 0 = LED cathodes, port 1 = mixed.

| Bit | Port 0 (output, LED sink) | Port 1 |
|---|---|---|
| 0 | SHORE (green) | TX_LAMPTEST (output): low lights the TX lamp through the BAT54 tie |
| 1 | MSG (white) | EPD_RES (output): e-paper reset, active low |
| 2 | PI ring (amber, in the PI button) | EPD_BUSY (input): high while the e-paper refreshes |
| 3 | BAT1 (bar 20 %) | spare |
| 4 | BAT2 (40 %) | spare |
| 5 | BAT3 (60 %) | spare |
| 6 | BAT4 (80 %) | spare |
| 7 | BAT5 (100 %) | spare |

LED drive rule: an LED is ON when its port bit is configured as an OUTPUT driving 0; OFF when the bit is configured as an INPUT (high impedance). Never drive a 1: the anode rail is 5 V and a 3.3 V push-pull high ghosts the LED. On boot, the bridge first writes the configuration registers so every LED bit is an input, then the output registers to 0, then enables outputs one by one.

Hardware LEDs, no software: MAIN ring (alive whenever the LED rail is present), TX (red, follows the DMR858M's real PTT pin through Q4 on PCB-D; the lamp-test tie lights it too).

## 2. Pi GPIO

| BCM | Pin on the ribbon | Use |
|---|---|---|
| 12 | 17 PANEL_PWM | LED rail dimmer, PWM 2 kHz, 10-bit (`dtoverlay=pwm-2chan`). Boots low: rail dark until the bridge is up. |
| 13 | 16 PWM1 | Sounder (active piezo through Q4): drive high to sound, PWM for patterns. |
| 7 | 15 EPD_RES_ALT | Alternative e-paper reset (JP2 closed); default is U2 port 1 bit 1. |
| 8 | 14 SPI_CE0 | E-paper chip select. |
| 9 | 8 EPD_DC | E-paper data/command (SPI0 with `no_miso`, `spi0-1cs`). |
| 10 | 12 SPI_MOSI | E-paper data. |
| 11 | 10 SPI_SCLK | E-paper clock. |
| 6 | (X1202) | Existing power-loss input, unchanged. |

## 3. Lighting

| LIGHTING position | Inputs | Bridge action |
|---|---|---|
| DAY | LIGHT_DAY_n low | duty 100 %, display backlight full |
| NIGHT | LIGHT_NIGHT_n low | duty 15 %, display backlight 20 %, sounder allowed |
| BLACKOUT | both high, RAIL_SENSE low | duty 0, display backlight off and the touch UI dark theme; the hardware rail is already open, software only follows |

One dimmer for the whole panel (MIL-STD-1472). The TX lamp is never dimmed below 10 % duty; in BLACKOUT it is dark like everything else (EMCON sits next to it for that case).

## 4. Indicator semantics

| LED | Steady | Flashing (3 to 5 Hz, immediate action only) |
|---|---|---|
| MASTER WARN | | any red condition unacknowledged: SOS active, ZEROIZE armed, thermal trip, pack under-voltage |
| MASTER CAUT | any amber condition acknowledged | any amber condition unacknowledged: bearer lost that was up, shore lost while charging was expected, disk nearly full |
| SOS ACTIVE | SOS mode on | SOS mode on and no bearer has confirmed delivery |
| SAT / MESH / LTE / GPS | bearer up (GPS: fix) | never |
| SHORE | shore 12 V present (from the X1202 monitor: input present) | never |
| CHARGING | X1202 reports charging | never |
| MSG | unread inbound message | never (ACK clears) |
| PI ring | heartbeat 0.5 Hz while the bridge runs | never |
| BAT1..5 | battery bar, shown for 5 s after a lamp test or a short TEST press; otherwise dark | lowest LED flashes below 10 % |

A flasher that fails must fail to steady-on: the bridge writes steady-on before it exits or crashes (a watchdog task holds the last written state).

## 5. Controls

| Control | Gesture | Action |
|---|---|---|
| TEST / ACK | short press (< 1 s) | acknowledge: MASTER WARN and MASTER CAUT stop flashing (steady if still active), sounder muted, MSG cleared, battery bar shown 5 s |
| TEST / ACK | hold 2 s | lamp test: all 17 LEDs on for 3 s (U1, U2 and TX_LAMPTEST), sounder chirp, battery bar shows charge after |
| TEST / ACK | hold 5 s after a touchscreen "show QR" request in the last 60 s | e-paper shows the provisioning QR while held; cleared on release |
| SOS | switch closed for 2 s | SOS mode on (existing SOS activation path); flipping the switch back cancels; the e-paper confirms both. The switch is a maintained locking toggle: pull, flip, leave |
| EMCON | latched closed | hardware: the DMR858M cannot key. Software on TX_INHIBIT_n low: stop direwolf TX, hold LoRa, LTE and satellite sends (queue them), show EMCON on the e-paper, MASTER CAUT steady |
| ZEROIZE | switch closed for 5 s | zeroize keys (existing keystore wipe), then a full-refresh blank of the e-paper; MASTER WARN flashes while armed (0 to 5 s); flipping back inside 5 s aborts; after the wipe the switch must be returned before the kit re-arms |
| PI | hardware to the Pi J2 pads | shutdown / wake, no bridge involvement |
| MAIN PWR | hardware to the X1202 switch pins | kit power, no bridge involvement |
| LIGHTING | DAY / NIGHT / BLACKOUT | section 3 |

Debounce 30 ms on every input; INT-driven read of U1 port 1 in one byte.

## 6. E-paper (WeAct 3.7, 416 x 240, UC8253, SPI0)

- Idle page: callsign, battery percent and shore state, GPS fix, UTC time, last inbound message (one line), bearer chips. Refresh at most once a minute, full refresh once an hour and after ZEROIZE.
- QR mode: only while TEST / ACK is held after a touchscreen request (section 5); the QR carries an enrolment URL plus a one-time code, never key material, because the image survives power loss. Cleared on release and at boot.
- Boot: reset, one full refresh with the idle page.
- BUSY must be polled before every command (EPD_BUSY on U2).

## 7. Bus rules

- The panel's 3V3 is never switched while the ribbon is attached (an unpowered PCA9555 clamps the kit I2C bus).
- With the ribbon unplugged nothing on PCB-B depends on the panel: I2C reads of 0x22 and 0x23 NACK, TR_APRS is held low by PCB-A's pull-down, TX_INHIBIT_n is held high by PCB-D's pull-up. The bridge must treat a NACK as "no panel" and keep running.
- I2C map after A16: 0x20 (B), 0x21 (A), 0x22 and 0x23 (C), 0x36 (X1202 gauge), 0x40 to 0x49 (INA219s). 0x55 and 0x6B are gone. A16 did not move any address; it took the spare bit 0.4 of the expander at 0x21 for `SHORE_INHIBIT` (section 9).

## 8. Existing code to reuse

`scripts/x1202-monitor.py` for the battery and input states (feeds SHORE, CHARGING, the bar); the SOS activation path of the operator dashboard for the SOS switch; the keystore wipe for ZEROIZE; the OOB EMCON semantics for the bearer hold. New: a `panel` package with the expander driver, the e-paper driver (UC8253 over spidev) and the gesture state machine, wired in `cmd/meshsat/main.go`.

## 9. Shore charge inhibit (A16 / E1, 3 Sep 2026)

PCB-A's expander U19 at 0x21, port 0 bit 4 (pin 8), net SHORE_INHIBIT, reaches the dock over spring pin 8 and drives an optocoupler on E1 whose transistor shorts the Traco converter's remote pin to its isolated -Vin. High = the dock's 12 V is off, so nothing charges. Low, floating, or the Pi dead = the converter runs (the LED is off), so a kit with a crashed bridge still charges. The bridge asserts it:
- when the in-case temperature is below 0 C (the ZigBee temperature sensor, or any in-case sensor the bridge trusts), since neither the X1202 nor the pack BMS protects the X1202's own four cells from a cold charge;
- when the operator sets "no charge" in the UI;
- and it clears it with hysteresis (charge again above 3 C).
Boot state: low. The SHORE indicator on the panel shows the dock's 12 V presence, which after this change is the only charge input: the case USB-C inlet is no longer wired to the X1202 (ASSEMBLY.md section 4); a USB-C PD source feeds the dock inlet through a 12 V PD trigger lead.

SHORE and CHARGING sources (audit 26.4): `x1202-monitor.py` must gain a `charging` field (voltage rising against the open-circuit curve while an input is present) and the GPIO 6 power-loss line must be verified wired on the bench (MESHSAT-774) before SHORE can be trusted; until then SHORE follows the dock 12 V sense that E1's LED shows and CHARGING stays dark.

## 10. Charge kick, bearer serialisation, module rail (rulings 3 Sep 2026 evening, appendix 32.3)

- Charge kick: while an input is present (SHORE, or GPIO 6 high) and the node is not full (gauge below 95 percent, or the node below 4.15 V), if the node voltage has not risen for 4 h, drive GPIO 16 high for 5 s and low again. GPIO 16 high disables the X1202 charger, low enables it (Geekworm hardware page, pin 36); the pulse restarts any safety timer the charger may have. Boot state low. *(Struck 4 Sep night, appendix 32.19: the X1202 is removed (32.17); the charger on A19 has its own timer behaviour by design, so no charge kick exists. Do not implement.)*
- Bearer serialisation: LTE, Iridium and LoRa transmissions never start in the same second; the bridge queues them. The A17 module rail is sized for one burst at a time over the whole discharge (about 4.2 A at 5 V); all three at once is tolerated only above about 3.8 V cell voltage, and then the module rail sags, never the Pi.
- Module rail: PCB-A's TPS61089 boost (5.05 V, fused by F3 from the cell node) feeds PCB-A's channel switches and the whole of PCB-B. Its enable follows the X1202's 5 V output over the sense lead into PCB-B J_5V_IN1 and J_AB1 pin 12, so the rail is on exactly while the X1202 powers the Pi; the bridge does not control it. Per-module control stays with the eFuse enables of section 1. *(Superseded 4 Sep night, appendix 32.19: with the X1202 gone, A19 enables the module rail from its own main power control; J_5V_IN1 disappears from PCB-B and J_AB1 pin 12 is spare again; the bridge still does not control the rail.)*
