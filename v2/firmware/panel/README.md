# MeshSat field kit V2: panel controller firmware (board C, U3 RP2040)

MESHSAT-1357, Layer 12. **Prototype firmware for an unbuilt kit: no board C exists, nothing here has run on hardware,
and the target build has not been compiled** (this host has no arm toolchain and no pico-sdk). What has run: the
portable core and its 55 host unit tests, compiled with the host gcc 12.2 under `-std=c11 -Wall -Wextra -Werror
-pedantic -Wshadow -Wconversion`, all passing, and the Python checks of `v2/ecad/tools/tests/test_fw_panel.py` that bind
the code to the netlists and the contract pages.

The contract this implements: `v2/docs/PANEL.md` (cited P s.n), `v2/docs/HW-FW-CONTRACT.md` rows FW-C01 to FW-C15
(and the FW-A, FW-K rows they lean on), `v2/docs/feasibility/ZEROIZE.md` sections 3.4 and 3.5 (ZER), the pins of board
C's generator `v2/ecad/tools/gen_sch_c.py` and netlist `v2/ecad/pcb-c-display-c8/out/pcb-c-display.net`, and the
expander bits of boards A, B and D's netlists.

| Path | What |
|---|---|
| `include/panel.h` | the core's types, constants (each citing its statement) and API |
| `include/hal.h` | the hardware layer: every GPIO (`HAL_PIN_LIST`) and expander bit (`HAL_EXP_BIT_LIST`), the I2C map, the HAL calls |
| `src/panel_core.c` | the state machines with a millisecond tick: controls, indicators, lighting, sounder, e-paper model, slots, display select, shutdown, shore inhibit, EMCON, hot stop, margin hold, the power controls in part, the boot order |
| `src/zeroize.c` | the wipe journal and the crypto-erase sequence (ZER 3.4) and the boot table (ZER 3.5) over injected operations |
| `src/expander.c` | the seven PCA9555: the boot writes (outputs before configuration), the LED drive rule, the EXP_INT service, the switched loads' bits |
| `src/bus_recover.c` | the kit bus recovery (FW-K04) |
| `src/sensors.c` | board B's TMP117 (FW-C13's fallback) and board C's VEML7700 (P s.8), read off the kit bus |
| `src/hal_host.c` | the host stub of hal.h |
| `src/hal_rp2040.c`, `src/main_rp2040.c` | the pico-sdk implementation and main loop (NOT BUILT) |
| `CMakeLists.txt` | the target build (pico-sdk 2.3.1), NOT RUN |
| `Makefile`, `tests/` | the host build and tests: `make -C v2/firmware/panel test` |

## 1. What the core implements

Pure logic: `panel_tick(p, now_ms, in, out)` reads a sample of the inputs and writes the wanted outputs. The kit bus,
the secure element, the flash journal and the e-paper's command layer are reached through `panel_ops_t`, so the tests
replace each with a fake (a PCA9555 register model, an ATECC608B that can fail, a NOR flash that can tear, a BUSY line).

- **P s.3**: debounce 30 ms on every switch; PI_SHDN_REQ active low, only ever pulled low by its output enable (FW-A10);
  PI_KILL push-pull low from the first instruction (FW-A11); GPIO21 and GPIO22 inputs only; RAIL_SENSE present above 1.25 V.
- **P s.4**: the LED drive rule (on = output driving 0, off = input, never a 1), the outputs enabled one by one after
  boot, every expander's output registers before its configuration (FW-A08), DEV_EN kept 1.
- **P s.5, FW-C01, FW-C02, FW-C05, FW-C06**: the boot order; the SLOT_EN levels read and adopted at boot (all driven
  low first when the toggle is closed or a wipe is pending); the heartbeat (alive while toggling, lost 3 s after the
  last edge); a flat heartbeat 60 s after the rail came up is a slot fault, power-cycled once with 5 s off, then left
  off until the operator acts; the slots raised one at a time; HDMI_SEL follows the bridge, else the lowest live slot,
  never a dark one (slot 1 = both low, slot 2 = SEL1 high, slot 3 = SEL2 high, read from `gen_sch_b.py:1342-1348`).
- **P s.5, FW-C03**: a MAIN tap (INT low at least 32 ms), the PI button's short press or the bridge's command starts the
  clean shutdown: PI_SHDN_REQ low 200 ms, the heartbeats awaited, then PI_KILL high and held; the PI button held 8 s is
  PI_KILL at once.
- **P s.6, FW-C07**: the hardware lines are never driven (the output structure has no field for TX_INHIBIT_n,
  EMCON_HW or ZEROIZE_HW; the HAL refuses an output on GPIO21); every EMCON edge is reported for the bridge's software
  holds, MASTER CAUT steady; the RockBLOCK's ENABLE request (B:U6 RB_SW_IEN) low on EMCON and raised after a release
  only once a fresh RB_STATUS read is low (P corrections (17)).
- **P s.8**: DAY 100 %, NIGHT 15 %, NVG 2 % with red and amber indicators only, BLACKOUT 0 with every LED and the
  sounder dark; the backlight figures for the bridge; the TX lamp floor of 10 % (finding F-05).
- **P s.9**: MASTER WARN and CAUT (flash unacknowledged, steady after ACK, a cleared condition forgets its ACK),
  SOS ACTIVE, the bearer LEDs, SHORE and CHARGING from the charger's bits, MSG, the PI ring's 0.5 Hz heartbeat, the
  battery bar, the lamp test of all seventeen; TEST short press, hold 2 s, hold 5 s for the QR; SOS closed 2 s and every
  SOS indication; ZEROIZE closed 5 s with the abort, complete and incomplete indications; the sounder patterns; the
  e-paper's page selection, refresh pacing, full refreshes, power and BUSY sequencing; the bridge's indicators held
  when the USB link drops.
- **P s.10, FW-C08**: SHORE_INHIBIT boot low, raised only for 'inputs off' or the water-on-floor isolation, refused
  for any other reason, and refused until the bridge has warned while the pack cannot discharge; held through a link
  loss.
- **FW-C04, ZER 3.4 and 3.5**: the step-0 alarm, the PENDING record, C0 and C1 before any retry, the verifications
  against the created key and the recorded one, at most 6 GenKey commands before the deadline D, DONE, the modules told
  at 1.5 s at the latest, the slots cut on their confirmation or at 3.0 s, step 7's ten creates per slot, the journal's
  torn record reading PENDING (I3), and the five rows of the boot table.
- **FW-C13, FW-C14**: HOT-R1's four states decoded from A:U27 P1.5 at every EXP_INT and a poll every second (with a
  command byte other than 00h after each read); H1's actions and release, H2's page then PI_KILL, the TMP117 fallback
  with the reduced mode and the outlets off, and the start-up read before any slot rises.
- **FW-C15**: the margin hold's two-reading trigger at 68.65 C plus the reference's offset, its actions on A:U27 and
  B:U6, the SOS queued and told, and the restore 5 K under after 30 minutes; H1 overrides it.
- **FW-C09 in part**: the round-8 fallback (the pack readings stopped 10 s: the reduced mode, both outlets off) and
  C1's first stage (+50 C inside air or +55 C on a cell, restore 5 K below).
- **FW-K04**: nine SCL pulses and a STOP on a held bus.

## 2. Statement to test

Every host test (55), from `tests/test_list.h` (the Python wrapper checks that each runs and passes, and that this table
names each).

| Test | Statement |
|---|---|
| t_debounce_30ms | P s.3: debounce 30 ms on every switch input |
| t_lighting_modes | P s.8: DAY, NIGHT, NVG (red and amber only), BLACKOUT, backlight |
| t_tx_floor | P s.8: the TX lamp never dimmed below 10 % (F-05) |
| t_rail_sense | P s.3 GPIO26 and s.8: the rail present above 1.25 V |
| t_led_drive_rule | P s.4: on = output driving 0, off = input, never a 1 |
| t_led_boot_one_by_one | P s.4: the outputs enabled one by one after boot |
| t_warn_caut_semantics | P s.9: flashing unacknowledged, steady after ACK |
| t_bridge_hold_on_link_drop | P s.9: the last state held when the USB link drops |
| t_msg_cleared_by_ack | P s.9: MSG cleared by ACK |
| t_battery_bar | P s.9: the battery bar 5 s, the lowest flashing below 10 % |
| t_pi_ring_heartbeat | P s.9: the PI ring at 0.5 Hz while a slot's bridge runs |
| t_sounder_patterns | P s.9: chirp, SOS pattern, muted in BLACKOUT |
| t_epd_refresh_rules | P s.9: refresh pacing, full refreshes, power between refreshes (F-08) |
| t_epd_busy_polled | P s.9: BUSY polled before every command |
| t_test_short_press_ack | P s.9: TEST short press = acknowledge |
| t_test_hold_lamp_test | P s.9: hold 2 s = lamp test (F-06) |
| t_test_qr_while_held | P s.9: hold 5 s within 60 s of a show QR request |
| t_sos_hold_2s | P s.9, FW-C10: SOS closed 2 s, flipping back cancels |
| t_sos_indications | P s.9: the SOS indications; FW-C10 |
| t_sos_emcon_queue | FW-C10, V-C10: queued under EMCON |
| t_pi_button_logic | P s.5, FW-C03: the PI button (F-01) |
| t_emcon_edges | FW-C07; P corrections (17) |
| t_never_drives_hardware_lines | P s.6, FW-C07, FW-A10 |
| t_zeroize_abort_inside_5s | P s.9, FW-C04: the abort |
| t_zeroize_commit_sequence | FW-C04, ZER 3.4 steps 0 to 8 |
| t_zeroize_confirm_cuts_early | ZER 3.4 step 6; FW-C04 |
| t_zeroize_retry_policy | ZER 3.4 step 3 and step 7; FW-C04 |
| t_zeroize_incomplete | P s.9, ZER 3.4 step 7; FW-C04 |
| t_zeroize_rearm_on_return | FW-C04: re-arm on the toggle's return |
| t_journal_torn_reads_pending | ZER I3; FW-C04 |
| t_zeroize_boot_table | ZER 3.5; FW-C01 step 3; FW-C04 |
| t_boot_order | FW-C01 |
| t_boot_slot_adopt | FW-C02 |
| t_exp_outputs_before_config | FW-A08, FW-C01 step 4, P s.5 |
| t_hb_lost_3s | FW-C05 |
| t_slot_fault_cycle | P s.5: the slot fault |
| t_hdmi_select | FW-C06, P s.5 |
| t_shutdown_main_tap | FW-C03, FW-A10, FW-A12 |
| t_shore_inhibit | P s.10, FW-C08 |
| t_hotr1_decode | FW-C14 |
| t_hot_stop_h1 | FW-C13: H1 |
| t_hot_stop_h2 | FW-C13: H2 |
| t_hot_tmp117_fallback | FW-C13, FW-C14: the line held high |
| t_hot_boot_read | FW-C14: the start-up read |
| t_hotr1_bus_lost | FW-C14: a bus that stops answering is the detector lost, never a stale held low |
| t_boot_main_tap | FW-C03, FW-A12: a MAIN tap during the boot |
| t_hot_boot_held_slot | FW-C14: a slot held up at boot, the line at 5 Hz |
| t_no_raise_while_zeroize_armed | FW-C04, D-03: nothing newly raised while ZEROIZE is armed or wiping |
| t_switch_closed_at_power_up | P s.9, FW-C10: SOS closed at power-up |
| t_tmp117_read | FW-C13, FW-C14: board B's TMP117 read off the bus, once a conversion |
| t_veml7700_read | P s.8: the VEML7700 reading for the bridge |
| t_se_absent_retried | FW-C04, ZER 3.5: the absent SE retried |
| t_margin_hold | FW-C15 |
| t_power_fallback | FW-C09 in part |
| t_bus_recover | FW-K04, V-K02 |

The Python checks (`run.py fw_panel`): the host tests build and pass; every FW-C row is covered (section 3); hal.h's
30 GPIOs match U3's pins on board C's netlist (through `gen_sch_c.py`'s RP2040 table, read with `ast`); every expander
bit hal.h names matches its PCA9555 pin on boards A, B, C and D, and every address matches its A0 to A2 straps; the PI
button reaches no controller pin (F-01's evidence, which fails the day it is wired); no controller pin reaches the
panel LDO's enable (FW-C11); the e-paper messages quoted by P s.9, FW-C13 and FW-C15 are carried verbatim; 29 timing and
threshold constants equal the contract's figures, each with the words that must still stand in its page; the target
build keeps FW-C01's two rules and FW-C02's reset scope.

## 3. The FW-C rows

Machine-checked: every FW-C row of the contract is here; IMPLEMENTED and PARTLY rows are cited by a host test; the
other two statuses are cited by none.

| Row | Status | What the firmware does | What is owed |
|---|---|---|---|
| FW-C01 | PARTLY | steps 1 to 4 and 6 (`panel_init`, `boot_step`, `panel_exp_boot`); the E5 fix off and the BOOTSEL mask in `CMakeLists.txt` and `hal_reboot_to_bootsel` | step 5, the charger's registers (FW-A01 to A03, A16 to A18): no charger driver here |
| FW-C02 | PARTLY | the held levels read and adopted, all low first with a wipe due; the watchdog with SIO, IO_BANK0 and PADS_BANK0 out of its scope and the SDK's early resets overridden (F-03); no ROM bootloader while a slot runs; the reset reason read | the boot reason reported (protocol, F-02); every hardware behaviour (V-C02) |
| FW-C03 | IMPLEMENTED | the MAIN tap, the PI short press and 8 s hold, the bridge's commands | the PI button's input is not wired on board C (F-01) |
| FW-C04 | PARTLY | the level-sensitive trigger, the abort, ZER 3.4's sequence and bounds, the journal, the boot table, the re-arm | the ATECC608B command layer (CryptoAuthLib and the bounded six-function HAL), P_A0 and P_B0 at enrolment, the modules told over the protocol (F-02); Z-EXP-A to C |
| FW-C05 | IMPLEMENTED | inputs without pad pulls, alive while toggling, lost after 3 s, the display re-elected | |
| FW-C06 | IMPLEMENTED | follow the bridge, else the lowest live slot, never a dark slot | |
| FW-C07 | IMPLEMENTED | GPIO21 an input only, every EMCON edge reported, MASTER CAUT steady, EMCON on the e-paper (its own page, and in the SOS pages) | the software holds themselves (queue, AT+CFUN, rfkill) are the bridge's |
| FW-C08 | IMPLEMENTED | boot low, only the two reasons, the warning first, never a charge hold | |
| FW-C09 | PARTLY | the round-8 10 s fallback, C1's first stage | C1's second stage ("reached again there"), C2, C3, C4 and K1 to K5 (`POWER-THERMAL.md` 7.2, PROVISIONAL, not read into this firmware); the readings reach the panel only over the protocol (F-02) |
| FW-C10 | IMPLEMENTED | the 2 s hold, the indications, queued under EMCON, the cancel | the sending is the bridge's |
| FW-C11 | NOT THE FIRMWARE'S | no controller pin reaches U5's EN (on +5V): the firmware has no means to switch its 3.3 V (`t_panel_3v3_cannot_be_switched_by_firmware`) | |
| FW-C12 | OWED | nothing: the wire format (MESHSAT-837) is defined nowhere (F-02); `panel_bridge_t` is only the decoded content the core reads, and the switch edges are queued as events | the wire format, the USB composite device (CDC and HID), the codec, V-C12 |
| FW-C13 | PARTLY | H1 and H2, the clean-shutdown request, the loads off on A:U27 and A:U28, the slots dropped, the release and the heat stage's one module, the TMP117 fallback | the CHRG_INHIBIT bit's write (FW-A19's charger driver; the core raises the flag); the hottest reading on the e-paper (the rendering, section 4) |
| FW-C14 | IMPLEMENTED | the four states, the start-up read, the slot found held up, the EXP_INT service with the command byte, the 1 s poll | |
| FW-C15 | PARTLY | the trigger, the actions on A:U27 and B:U6, the SOS queued and told, MASTER CAUT, the page, the restore, H1's precedence | the Geiger off (the sensor controller, over the protocol), the module idled (the bridge), the CHRG_INHIBIT write, the reference's offset (T-H1) |

## 4. Not implemented, and owed

- **The bridge protocol (FW-C12)**: finding F-02. Until it exists the core runs as if no host were present.
- **The e-paper's command layer and rendering**: the PDi E2370KS0C1's iTC sequence (UltraChip UC8253C class, sheet held
  as `v2/vendor/pdi/ultrachip-uc8253c-a0.6.pdf`), the fonts, the pages' fields and the QR encoder. The core decides
  which page, when, full or partial, and sequences EPD_PWR_n and BUSY; `panel_epd_ops_t.send` is a stub.
- **The charger (FW-A01 to A23)**: no register is written; the core raises the CHRG_INHIBIT flags (hot, margin) and
  reads the SHORE and CHARGING bits as inputs a driver would fill.
- **The secure element**: CryptoAuthLib is not vendored; on the target every SE call fails, so the boot takes "the SE
  does not answer" and a commit ends INCOMPLETE with the slots held off (fail secure).
- **The USB device**, and the kit bus segment buffer of FW-K05 (OWED in the contract). The VEML7700's lux per count at
  the chosen setting is INFERRED by scaling (sensors.c); Vishay's application note is not held.
- **The pico-sdk build**: never compiled; the SDK names were read from pico-sdk 2.3.1 (section 6).

## 5. Findings

Each is raised for the page or board named; nothing in a contract, record, generator or PANEL.md was edited.

| ID | Severity | Finding | Exact place | Owner |
|---|---|---|---|---|
| F-01 | major | The PI button reaches no controller pin. SW_PI's contacts (PIJ2_A, PIJ2_B) pass FB3 and FB4 to J_PIJ2's two lands (PIJ2_A2, PIJ2_B2) and to U11's clamps only: no U3 GPIO, no expander input, neither on GND, and no other board has a mating lead. PANEL.md s.5 and FW-C03 have the controller read it; ASSEMBLY.md says "the panel controller reads it; nothing leaves the backer"; the generator's own note says PIJ2_A2 is the LTC2954's INT on board A. Every one of the 30 GPIOs is used; the expanders' spares are free (U1 P1.3 to P1.7, U2 P1.1 to P1.7). The firmware's logic is done and tested on an input the target HAL cannot fill (`HAL_PI_BUTTON_WIRED 0`) | `gen_sch_c.py:324-326`, `:333`; netlist nets /PIJ2_A2 and /PIJ2_B2; `ASSEMBLY.md:127`; `PANEL.md:149` | board C's author |
| F-02 | major | The bridge protocol's wire format (MESHSAT-837) is defined nowhere: not in the meshsat repository (docs, internal, proto, and no commit message names MESHSAT-837), not in the HAL repository, not in this tree, and the YouTrack issue carries a goal, no format. Nothing of it is implemented. Consequence on the target: no bridge input (the SOS "NO HOST" indication, the bridge's LEDs dark, every switched load off, SHORE_INHIBIT never raised), no pack readings (FW-C09, FW-C15's reference, the battery bar), and ZER 3.4 step 5 has no channel, so step 6 waits for the 3.0 s alarm | `PANEL.md:215`; `HW-FW-CONTRACT.md:461` | MESHSAT-837's owner |
| F-03 | major | FW-C02's reset scope cannot keep SLOT_EN by itself: pico-sdk 2.3.1's `runtime_init_early_resets()` resets IO_BANK0 and PADS_BANK0 on every boot (`runtime_init.c:56-70`), so the firmware overrides that weak function. Whether the PSM's RESETS bit must also be cleared is INFERRED (`hal_watchdog_start`), for V-C02. And ZER 3.4 step 0's backstop ("SLOT_EN1..3 return to inputs" on a watchdog reset) no longer holds under FW-C02: a hang during a wipe is cut by the reset and then the boot path, which drives every SLOT_EN low first with the toggle closed or a PENDING record, at the watchdog period (1 s here) plus the boot's first instructions | `HW-FW-CONTRACT.md` FW-C02; `feasibility/ZEROIZE.md:259-264` | the contract's writer; ZEROIZE.md's owner |
| F-04 | minor | PANEL.md s.4 orders board C's boot as "first writes the configuration registers so every LED bit is an input, then the output registers to 0"; s.5 and FW-A08 order every expander's output registers first. Both are safe on U1 and U2 (every bit written 0, off is an input); the firmware writes outputs first everywhere, then configuration all inputs, then the outputs one by one | `PANEL.md:139` against `PANEL.md:147` | PANEL.md's writer |
| F-05 | minor | NVG's 2 % and "the TX lamp is never dimmed below 10 % duty" share one rail (LED_RAIL behind Q1). The firmware raises the whole panel to 10 % while TR_APRS reads keyed or the lamp test lights the TX lamp, so in NVG the lit red and amber LEDs rise to 10 % for a key-down | `PANEL.md:192`, `:195` | PANEL.md's writer |
| F-06 | minor | The lamp test's sound: "a chirp" in the controls, "double chirp (lamp test)" in the sounder patterns. Taken: the double chirp | `PANEL.md:201`, `:209` | PANEL.md's writer |
| F-07 | minor | A slot fault is in both MASTER WARN's red list and MASTER CAUT's amber list; s.5 names MASTER CAUT. Taken: MASTER CAUT | `PANEL.md:199`, `:147` | PANEL.md's writer |
| F-08 | minor | "Refresh at most once a minute" would delay the QR's removal (the glass keeps it with the power off), the SOS and the ZEROIZE pages. Taken: a change of page refreshes at once; the minute bounds the idle page's content | `PANEL.md:203` | PANEL.md's writer |
| F-09 | minor | "Until the operator acts" names no control. The core offers `panel_slot_operator_retry()` for the bridge (owed, F-02); no panel control does it | `PANEL.md:147` | PANEL.md's writer |
| F-10 | minor | At start-up FW-C14 says a 5 Hz line raises no slot "until it is back at 1 Hz"; FW-C13 leaves H1 only after 1 Hz AND 30 minutes. The firmware enters H1 at boot and waits for both (the stricter) | `HW-FW-CONTRACT.md` FW-C13, FW-C14 | the contract's writer |
| F-11 | minor | Board D's U16 outputs X_SA_PD, X_AMP_EN and X_MMUTE (FW-D01) have no stated boot level; the firmware writes 0 (S-11), which may hold the SA868 powered down until the bridge acts | `HW-FW-CONTRACT.md` FW-D01; `gen_sch_d.py:930` | board D's author |
| F-12 | minor | FW-C15's "an SOS raised meanwhile is queued as under EMCON and the operator told" gives no message; the EMCON message ("OPEN EMCON TO SEND") would be wrong. Taken: "SOS QUEUED: MARGIN HOLD, COOLING" | `HW-FW-CONTRACT.md` FW-C15 | the contract's writer |
| F-13 | observation | HDMI_SEL's encoding is in no contract page; read from board B: slot 1 both low, slot 2 SEL1 high, slot 3 SEL2 high (U3 and U4 cascade, U519 and U520 enables) | `gen_sch_b.py:1342-1348` | PANEL.md's writer |

## 6. Session choices

Taken by the session under the owner's standing rule of 26 September 2026 where the contract leaves the firmware a
choice. Each is reversed by changing the named constant or line.

| ID | Choice | Why | Reverse |
|---|---|---|---|
| S-01 | hold times run from the debounced edge | never shorter than stated | `controls_*` |
| S-02 | MASTER WARN and CAUT flash at 4 Hz; the low battery LED at 2 Hz | inside P s.9's 3 to 5 Hz | `PANEL_FLASH_*` |
| S-03 | the slots raised 1 s apart | "one at a time" with no interval | `PANEL_SLOT_STAGGER_MS` |
| S-04 | the operator's retry is a call for the bridge | F-09 | `panel_slot_operator_retry` |
| S-05 | a clean shutdown waits at most 60 s for the heartbeats | FW-C13's figure; FW-C03 gives none | `PANEL_SHDN_WAIT_MS` |
| S-06 | "no host" = no bridge session | the panel cannot tell a module without its bridge from no module | `page_select`, `indicators` |
| S-07 | HOT-R1: five or more edges in 2 s = 5 Hz, a held line after 3 s, 1 Hz only after 2 s of samples; polled every 50 ms during the start-up read | FW-E10 sends one edge a second at 1 Hz and five at 5 Hz | `panel_hot_classify` |
| S-08 | H2 drives PI_KILL once its page is shown or after 30 s | the page first, as FW-C13 orders | `PANEL_H2_PAGE_WAIT_MS` |
| S-09 | the watchdog's period 1 s | over the 235 ms worst GenKey; ZER leaves it TBD | `PANEL_WATCHDOG_MS` |
| S-10 | every configuration write preceded by an output write of 0 | an expander reset by a brownout returns to FFh | `expander.c` |
| S-11 | board D's U16 outputs written 0 | F-11 | `EXP_BOOT` |
| S-12 | the texts the contract does not quote: IDLE, ENROLMENT QR, SOS SENT, the SE's absence, the margin hold's SOS, EMCON ON | none stated | `panel_page_text` |
| S-13 | both LIGHTING inputs low (not possible on a sound toggle) = the dimmer lit mode, flagged | fail dim | `panel_light_mode` |
| S-14 | battery LED k lit above 20(k-1) % | no empty bar from 10 to 19 % | `indicators` |
| S-15 | the double chirp 50 on, 100 off, 50 on; the incomplete pulses 200 apart | none stated | `sound_level` |
| S-16 | a page change refreshes at once | F-08 | `epd_step` |
| S-17 | HOT-R1 unreadable at start-up = held high (the detector lost) | fail to the TMP117 fallback | `boot_step` |
| S-18 | a 5 Hz line at start-up enters H1 with the stop at boot | F-10 | `boot_step`, `hot_step` |
| S-19 | after H1 only the heat stage's module (slot 2 as board B is generated) runs until the next start | FW-C09's restore is not implemented | `heat_stage_only` |
| S-20 | the margin reference's offset 0 until T-H1 calibrates it | FW-C15 PROVISIONAL | `PANEL_MARGIN_REF_OFFSET_MC` |
| S-21 | after a complete wipe the slots power again when the toggle returns | ZER 3.5's re-armed row | `controls_zeroize` |
| S-22 | the lamp test fires at 2 s on the way to a 5 s QR hold | both statements are unconditional | `controls_test` |
| S-23 | NVG's red-and-amber rule applies to the lamp test | light discipline | `panel_tick` |
| S-24 | the sounder sounds in DAY, NIGHT and NVG; ACK mutes the SOS and incomplete patterns until the condition rises again | P s.8 mutes only BLACKOUT | `sound_level` |
| S-25 | ZEROIZE arming and incomplete force MASTER WARN to flash, complete forces it steady, whatever the ACK | P s.9's ZEROIZE indications are specific | `indicators` |
| S-26 | the pack fallback only after the readings were seen once | a bridge not yet booted is not a lost sensor controller | `power_controls_step` |
| S-27 | with no bridge every switched load stays off | the loads' policy is the bridge's | `panel_exp_write_kit` |
| S-28 | the EXP_INT service reads every input expander and writes the command byte to each | FW-C14 names U27; harmless on the others | `panel_exp_service` |
| S-29 | this controller's own pull on PI_SHDN_REQ, and 5 ms after it, is never read as a MAIN tap | the line is one wired-OR net | `PANEL_OWN_PULL_GUARD_MS` |
| S-30 | an EXP_INT held low is serviced at most every 5 ms; a failed LED write retried after 100 ms | a dead target must not stall the loop at 10 ms a transfer | `PANEL_EXP_INT_MIN_MS`, `PANEL_LED_RETRY_MS` |
| S-31 | with every slot dark the display selection stays where it was | no live slot to choose; board B's enables pass no picture from a dark slot | `display_select` |
| S-33 | a TEST, SOS or PI switch already closed at power-up counts its hold from the controller's start (an SOS toggle left closed arms SOS 2 s after boot) | the toggles are maintained; a hold cannot be shorter than stated | `sample_switches` |
| S-35 | an absent secure element is retried every 60 s (two GenKey-public reads, about 0.26 s of the loop); its answer clears the warning | ZER 3.5 says it is retried and states no period | `PANEL_SE_PROBE_MS` |
| S-36 | the TMP117 polled every 250 ms and counted once per Data_Ready (its reset setting converts each second); the VEML7700 at gain x1/8 and 100 ms (to about 35 klx), polled each second | "two readings in a row" are two conversions; daylight without saturation at NIGHT's cost of 0.54 lx steps | `PANEL_TMP117_POLL_MS`, `sensors.c` |
| S-34 | no slot is newly raised while ZEROIZE is armed (the 5 s) or wiping; a running slot is left to step 6 | fail secure: D-03 cuts the slots | `zeroize_blocks_raise` |
| S-32 | HOT-R1 decided only on reads at most 1.5 s old; 1.5 to 3 s without a read keeps the last verdict; over 3 s is the detector lost | a dead bus must not age a stale low into H2 and kill the kit | `panel_hot_classify` |

## 7. What needs the hardware

Bring-up of board C, in this order: power with the ribbon out and SWD on TP1 to TP3; the first target build (section 8);
the pins (each GPIO's level against hal.h); the expanders at 0x22 and 0x23 and the LED rule (a ghosted LED means a 1
was driven); the kit bus at 100 kHz on the scope (V-K01); then the ribbon in. The verification rows this firmware
feeds, none run: **V-C01** (no glitch on any enable but DEV_EN, the slots only after ZEROIZE_SW), **V-C02** (watchdog,
RUN and SWD resets with three slots running; F-03's INFERRED PSM bit), **V-C03** (MAIN tap, PI short and 8 s, the
force-off), **V-C04**, **V-C05** (a bridge stopped: lost within 3 s, the display moved), **V-C08**, **V-C09**, **V-C10**,
**V-C12** (after F-02), **V-C13** (P15 and E3-H), **V-C15**, **V-K01** to **V-K03**, **Z-EXP-A** to **Z-EXP-C** (the
secure element), **E-01** to **E-12** (EMCON), and the e-paper's first refresh (BUSY, the boost).

## 8. Building

Host tests (any host with gcc and make; nothing is written into the tree with `BUILD=` elsewhere):

    make -C v2/firmware/panel test
    env -C v2/ecad/tools/tests python3 run.py fw_panel

Target (owed; not run here): pico-sdk 2.3.1, arm-none-eabi-gcc, CMake 3.13 or later:

    export PICO_SDK_PATH=/path/to/pico-sdk   # tag 2.3.1
    cmake -S v2/firmware/panel -B build-rp2040 && cmake --build build-rp2040   # meshsat_panel.uf2 / .elf

Flash by SWD (TP1 SWCLK, TP2 SWDIO, TP3 RUN), never through the ROM bootloader while a slot runs (FW-C02).

The pico-sdk names `hal_rp2040.c` and `CMakeLists.txt` use were read from pico-sdk 2.3.1 on 3 October 2026
(`https://raw.githubusercontent.com/raspberrypi/pico-sdk/2.3.1/src/...`, BSD-3-Clause, consulted, not filed), sha256
first 16 hex: `rp2_common/pico_runtime_init/runtime_init.c` 7246c432e8b91c87, `rp2_common/hardware_watchdog/watchdog.c`
e7052da8894a7f12, `rp2040/hardware_regs/include/hardware/regs/psm.h` 99db9c7f82033171, `.../regs/resets.h`
bc261dcd8268c225, `.../regs/vreg_and_chip_reset.h` 002454b252fece95, `.../regs/intctrl.h` 76d1205144a953c7,
`rp2040/hardware_structs/include/hardware/structs/timer.h` 9325fe9694d9d6c8, `rp2_common/hardware_irq/include/hardware/irq.h`
85fabc3046de2b00, `rp2_common/hardware_resets/include/hardware/resets.h` 3688d3a282705b79,
`rp2_common/pico_bootrom/include/pico/bootrom.h` df34abac2ede9284, `rp2_common/hardware_i2c/include/hardware/i2c.h`
ba330ff219f3844a, `rp2_common/hardware_flash/include/hardware/flash.h` 34bcc266f4535e6c, `rp2_common/tinyusb/CMakeLists.txt`
293d51840416b722.
