<!-- COPIED INPUT (MESHSAT-1357, Layer 5 round 3, record l5r2, 3 October 2026). Source: branch fnd/fw-panel at commit 42c27369, file v2/firmware/panel/README.md, whose sha256 at that commit is 8582354e9c20206e4c698e794621b684aaaf6addf8b56e83d61bf1d2cc2ec3c9. Copied: sections 5 (findings F-01 to F-13) and 6 (session choices S-01 to S-36), from section 5's heading to the line before section 7's, verbatim between the two markers below; the body's own sha256 is 74935330d4e37d22b7a813574ee729bdf89b4e799a10124e93cb640703459b64 (l5r3_panel.py recomputes it and refuses a copy that differs). Copied because the commit is not in this branch's history; no git command reads it. -->
<!-- BODY BEGIN -->
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

<!-- BODY END -->
