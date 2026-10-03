/* test_list.h: every host test with the statements it checks. One T() a line: test_fw_panel.py parses this list to
 * check that every FW-C row is cited here or listed in README.md section 3 as not the firmware's or owed. */
#define TEST_LIST(T) \
    T(t_debounce_30ms,               "PANEL.md s.3: debounce 30 ms on every switch input") \
    T(t_lighting_modes,              "PANEL.md s.8: DAY 100 %, NIGHT 15 %, NVG 2 % red and amber only, BLACKOUT 0, backlight 100/20/5/0") \
    T(t_tx_floor,                    "PANEL.md s.8: the TX lamp never dimmed below 10 % duty (finding F-05)") \
    T(t_rail_sense,                  "PANEL.md s.3 GPIO26: the rail present above 1.25 V; s.8 BLACKOUT with RAIL_SENSE low") \
    T(t_led_drive_rule,              "PANEL.md s.4: LED on = output driving 0, off = input, never a 1") \
    T(t_led_boot_one_by_one,         "PANEL.md s.4: after boot the outputs are enabled one by one") \
    T(t_warn_caut_semantics,         "PANEL.md s.9: MASTER WARN and CAUT flash unacknowledged, steady after ACK") \
    T(t_bridge_hold_on_link_drop,    "PANEL.md s.9: the controller holds the last written state when the USB link drops") \
    T(t_msg_cleared_by_ack,          "PANEL.md s.9: MSG for an unread message, cleared by ACK") \
    T(t_battery_bar,                 "PANEL.md s.9: BAT1..5 for 5 s after a short TEST press, the lowest flashing below 10 %") \
    T(t_pi_ring_heartbeat,           "PANEL.md s.9: the PI ring a 0.5 Hz heartbeat while any slot's bridge runs") \
    T(t_sounder_patterns,            "PANEL.md s.9: sounder chirp 50 ms, SOS 1 s on 1 s off, all muted in BLACKOUT") \
    T(t_epd_refresh_rules,           "PANEL.md s.9: e-paper refresh at most once a minute, full once an hour; power down between refreshes (finding F-08)") \
    T(t_epd_busy_polled,             "PANEL.md s.9: BUSY polled before every command") \
    T(t_test_short_press_ack,        "PANEL.md s.9: TEST short press = acknowledge, sounder muted, battery bar 5 s") \
    T(t_test_hold_lamp_test,         "PANEL.md s.9: TEST hold 2 s = lamp test of all seventeen for 3 s, the battery bar after (finding F-06)") \
    T(t_test_qr_while_held,          "PANEL.md s.9: hold 5 s within 60 s of a show QR request = the QR while held") \
    T(t_sos_hold_2s,                 "PANEL.md s.9, FW-C10: SOS closed 2 s = SOS mode, flipping back cancels") \
    T(t_sos_indications,             "PANEL.md s.9 SOS indications: armed, queued, sent, no host; FW-C10") \
    T(t_sos_emcon_queue,             "FW-C10, V-C10: SOS under EMCON queues and tells; released, it sends") \
    T(t_pi_button_logic,             "PANEL.md s.5, FW-C03: PI short press = PI_SHDN_REQ, held 8 s = PI_KILL (finding F-01)") \
    T(t_emcon_edges,                 "FW-C07: every EMCON edge reported, MASTER CAUT steady, EMCON on the e-paper; PANEL.md corrections (17) RB_SW_IEN") \
    T(t_never_drives_hardware_lines, "PANEL.md s.6, FW-C07, FW-A10: the hardware lines are never driven; GPIO21 never an output") \
    T(t_zeroize_abort_inside_5s,     "PANEL.md s.9, FW-C04: ZEROIZE flipped back inside 5 s aborts") \
    T(t_zeroize_commit_sequence,     "FW-C04, ZEROIZE.md 3.4 steps 0 to 8, PANEL.md s.9 ZEROIZE indications") \
    T(t_zeroize_confirm_cuts_early,  "ZEROIZE.md 3.4 step 6: SLOT_EN dropped once every module confirmed; FW-C04") \
    T(t_zeroize_retry_policy,        "ZEROIZE.md 3.4 step 3 retry policy and deadline D, step 7; FW-C04") \
    T(t_zeroize_incomplete,          "PANEL.md s.9 ZEROIZE incomplete; ZEROIZE.md 3.4 step 7; FW-C04") \
    T(t_zeroize_rearm_on_return,     "FW-C04: re-arm only when the toggle returns") \
    T(t_journal_torn_reads_pending,  "ZEROIZE.md 3.4 invariant I3; FW-C04 wipe-pending record") \
    T(t_zeroize_boot_table,          "ZEROIZE.md 3.5 boot table; FW-C01 step 3; FW-C04 level-sensitive") \
    T(t_boot_order,                  "FW-C01: PI_KILL low, PI_SHDN_REQ released, ZEROIZE read, expanders, SLOT_EN one at a time") \
    T(t_boot_slot_adopt,             "FW-C02: SLOT_EN held levels read and adopted at boot; a wipe due drives them low first") \
    T(t_exp_outputs_before_config,   "FW-A08, FW-C01 step 4, PANEL.md s.5: outputs before configuration, DEV_EN kept 1") \
    T(t_hb_lost_3s,                  "FW-C05: a slot alive while its line toggles, lost after 3 s without an edge") \
    T(t_slot_fault_cycle,            "PANEL.md s.5: flat 60 s = slot fault, power-cycled once (5 s off), then off until the operator acts") \
    T(t_hdmi_select,                 "FW-C06, PANEL.md s.5: follow the bridge, else the lowest live slot, never a dark slot") \
    T(t_shutdown_main_tap,           "FW-C03, FW-A10, FW-A12: MAIN tap, PI_SHDN_REQ low 200 ms, wait for the heartbeats, PI_KILL") \
    T(t_shore_inhibit,               "PANEL.md s.10, FW-C08: SHORE_INHIBIT boot low, only inputs off or water isolation, warning first") \
    T(t_hotr1_decode,                "FW-C14: HOT-R1's four states; EXP_INT serviced with a non-zero command byte; polled 1 s") \
    T(t_hot_stop_h1,                 "FW-C13: H1 actions and its release after 1 Hz and 30 minutes, the heat stage's one module") \
    T(t_hot_stop_h2,                 "FW-C13: H2 on the line held low: the page, then PI_KILL") \
    T(t_hot_tmp117_fallback,         "FW-C13, FW-C14: the line held high: TMP117 at +55.0 and +56.0 C in two readings; reduced mode, outlets off") \
    T(t_hot_boot_read,               "FW-C14: HOT-R1 read at start-up before any slot is raised") \
    T(t_margin_hold,                 "FW-C15: the margin hold's trigger, actions, SOS queued and restore") \
    T(t_power_fallback,              "FW-C09 (in part): the 10 s pack-reading fallback and C1's first stage") \
    T(t_bus_recover,                 "FW-K04, V-K02: nine SCL pulses and a STOP on a held bus")
