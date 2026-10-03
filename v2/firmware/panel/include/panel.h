/*
 * panel.h: the panel controller's portable core (board C, U3 RP2040; MESHSAT-1357 Layer 12).
 *
 * Prototype firmware for an UNBUILT kit: nothing here has run on hardware. Pure logic: no register, pin or clock is
 * touched here. The core reads a sample of the inputs (panel_in_t) and the time in milliseconds, and writes the wanted
 * outputs (panel_out_t). The kit I2C bus, the secure element, the flash journal and the e-paper are reached through
 * injected operations (panel_ops_t), so the host tests replace them with fakes.
 *
 * Every constant names the statement it implements: PANEL.md section n (P s.n), HW-FW-CONTRACT.md row (FW-xnn),
 * feasibility/ZEROIZE.md (ZER s.n). A value the contract leaves to the firmware is marked SESSION with its reason in
 * README.md section "Session choices".
 */
#ifndef PANEL_H
#define PANEL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "hal.h"

#define PANEL_FW_VERSION "0.1.0"

/* ---------------------------------------------------------------- timing (milliseconds) */
#define PANEL_DEBOUNCE_MS           30u     /* P s.3: debounce 30 ms on every switch input */
#define PANEL_TEST_LAMP_HOLD_MS     2000u   /* P s.9: TEST hold 2 s = lamp test */
#define PANEL_TEST_QR_HOLD_MS       5000u   /* P s.9: hold 5 s within 60 s of a show QR request */
#define PANEL_QR_WINDOW_MS          60000u  /* P s.9 */
#define PANEL_LAMPTEST_MS           3000u   /* P s.9: all seventeen for 3 s */
#define PANEL_BATBAR_MS             5000u   /* P s.9: battery bar 5 s */
#define PANEL_SOS_HOLD_MS           2000u   /* P s.9, FW-C10: SOS closed 2 s */
#define PANEL_ZEROIZE_HOLD_MS       5000u   /* P s.6, s.9, FW-C04: closed 5 s */
#define PANEL_HB_LOST_MS            3000u   /* FW-C05: lost after 3 s without an edge */
#define PANEL_SLOT_FLAT_MS          60000u  /* P s.5: heartbeat flat 60 s after the rail came up = slot fault */
#define PANEL_SLOT_CYCLE_OFF_MS     5000u   /* P s.5: power-cycle once, rail off 5 s */
#define PANEL_SLOT_STAGGER_MS       1000u   /* SESSION S-03: "one at a time" with no interval stated */
#define PANEL_MAIN_TAP_MS           32u     /* FW-A10: a MAIN tap holds INT low at least 32 ms */
#define PANEL_SHDN_PULSE_MS         200u    /* P s.3, FW-C03: PI_SHDN_REQ low at least 200 ms */
#define PANEL_SHDN_WAIT_MS          60000u  /* SESSION S-05: FW-C03 gives no bound; FW-C13's 60 s taken */
#define PANEL_KILL_HOLD_MS          3000u   /* P s.3: PI_KILL held high 3 s */
#define PANEL_PI_KILL_PRESS_MS      8000u   /* P s.5, FW-C03: PI held 8 s = PI_KILL */
#define PANEL_HOTR1_WINDOW_MS       2000u   /* FW-C14 decode window (SESSION S-07) */
#define PANEL_HOTR1_HELD_MS         3000u   /* FW-C14: held when no edge comes for 3 s */
#define PANEL_OWN_PULL_GUARD_MS     5u      /* SESSION S-29: the line's rise through R3 after this controller lets go */
#define PANEL_EXP_INT_MIN_MS        5u      /* SESSION S-30: an EXP_INT held low is serviced at most every 5 ms */
#define PANEL_LED_RETRY_MS          100u    /* SESSION S-30: a failed LED write is retried after 100 ms */
#define PANEL_HOT_RELEASE_MS        1800000u /* FW-C13: 30 minutes since the stop */
#define PANEL_HOT_SHDN_WAIT_MS      60000u  /* FW-C13: drop SLOT_EN once stopped or 60 s */
#define PANEL_EXP_POLL_MS           1000u   /* FW-C14: poll the port at least once a second */
#define PANEL_MARGIN_RESTORE_MS     1800000u /* FW-C15: restore after 30 minutes (PROVISIONAL) */
#define PANEL_EPD_MIN_INTERVAL_MS   60000u  /* P s.9: refresh at most once a minute (idle content) */
#define PANEL_EPD_FULL_INTERVAL_MS  3600000u /* P s.9: full refresh once an hour */
#define PANEL_ZER_KILL_AFTER_MS     3000u   /* ZER s.3.4 step 0: slots cut 3.0 s after the end of the hold */
#define PANEL_ZER_DEADLINE_MS       1500u   /* ZER s.3.4 step 3 (b): the deadline D */
#define PANEL_H2_PAGE_WAIT_MS       30000u  /* SESSION S-08: H2 drives PI_KILL once its page is shown or after 30 s */
#define PANEL_FLASH_WARN_HALF_MS    125u    /* P s.9: MASTER WARN 3 to 5 Hz: 4 Hz (SESSION S-02) */
#define PANEL_CHIRP_MS              50u     /* P s.9: chirp 50 ms (acknowledge) */
#define PANEL_DCHIRP_ON_MS          50u     /* P s.9 (F-06, S-15): double chirp 50 ms on, 100 ms off, 50 ms on */
#define PANEL_DCHIRP_OFF_MS         100u
#define PANEL_FLASH_1HZ_HALF_MS     500u    /* P s.9: SOS ACTIVE 1 Hz */
#define PANEL_FLASH_4HZ_HALF_MS     125u    /* P s.9: SOS ACTIVE 4 Hz, no host */
#define PANEL_FLASH_PIRING_HALF_MS  1000u   /* P s.9: PI ring 0.5 Hz heartbeat */
#define PANEL_FLASH_BAT_HALF_MS     250u    /* P s.9: lowest bar LED flashing below 10 % (rate SESSION S-02) */
#define PANEL_WATCHDOG_MS           1000u   /* FW-C02 (period SESSION S-09) */

/* ---------------------------------------------------------------- temperatures, milli-degrees C */
#define PANEL_HOT_TMP117_H1_MC      55000   /* FW-C13 */
#define PANEL_HOT_TMP117_H2_MC      56000   /* FW-C13 */
#define PANEL_HOT_TMP117_REL_MC     45000   /* FW-C13 */
#define PANEL_MARGIN_TRIGGER_MC     68650   /* FW-C15 (PROVISIONAL), plus the reference's calibrated offset */
#define PANEL_MARGIN_RESTORE_DK_MC  5000    /* FW-C15: 5 K under the trigger */

/* ---------------------------------------------------------------- lighting duties, per mille (P s.8) */
#define PANEL_DUTY_DAY       1000u
#define PANEL_DUTY_NIGHT     150u
#define PANEL_DUTY_NVG       20u            /* the lowest PWM step the firmware allows */
/* F-05 (round 3, PANEL.md s.8): no TX lamp floor. The TX lamp D3 shares LED_RAIL behind Q1 and follows the panel's duty
 * in every position (NVG 2 %), dark in BLACKOUT. The 10 % floor of the first contract was withdrawn on 3 October 2026. */

/* ---------------------------------------------------------------- the seventeen controller-lit indicators */
enum panel_led {
    LED_SOSACT = 0, LED_MWARN, LED_MCAUT, LED_CHG, LED_SAT, LED_MESH, LED_LTE, LED_GPS, /* U1 port 0 bits 0..7 */
    LED_SHORE, LED_MSG, LED_PIRING, LED_BAT1, LED_BAT2, LED_BAT3, LED_BAT4, LED_BAT5,  /* U2 port 0 bits 0..7 */
    LED_TXTEST,                                                                        /* U2 port 1 bit 0, D3 via D17 */
    LED_COUNT
};
enum panel_colour { COL_RED, COL_AMBER, COL_GREEN, COL_WHITE };
extern const uint8_t panel_led_colour[LED_COUNT];
#define LED_BIT(l) (1u << (l))
#define PANEL_LED_ALL ((1u << LED_COUNT) - 1u)

enum panel_light_mode { LIGHT_DAY, LIGHT_NIGHT, LIGHT_NVG, LIGHT_BLACKOUT };

/* ---------------------------------------------------------------- e-paper pages (P s.9, FW-C13, FW-C15) */
enum panel_page {
    PAGE_NONE = 0, PAGE_IDLE, PAGE_QR,
    PAGE_SOS_ARMED, PAGE_SOS_SENT, PAGE_SOS_QUEUED_EMCON, PAGE_SOS_QUEUED_NO_BEARER, PAGE_SOS_NO_HOST,
    PAGE_SOS_CANCELLED,
    PAGE_ZEROIZE_ABORTED, PAGE_ZEROIZED, PAGE_ZEROIZE_INCOMPLETE, PAGE_SE_ABSENT,
    PAGE_HOT_STOP, PAGE_HOT_SHUTDOWN, PAGE_MARGIN_HOLD, PAGE_SOS_QUEUED_MARGIN, PAGE_EMCON,
    PAGE_COUNT
};
extern const char *const panel_page_text[PAGE_COUNT];

/* ---------------------------------------------------------------- sounder patterns (P s.9) */
enum panel_sound {
    SND_NONE = 0, SND_CHIRP, SND_DOUBLE_CHIRP, SND_SOS, SND_ZER_COMPLETE, SND_ZER_INCOMPLETE
};

/* ---------------------------------------------------------------- loads the core may force off (FW-C13, C15, C09) */
enum panel_load {
    LOAD_MONITOR = 0, LOAD_HEATER, LOAD_BOARD_D, LOAD_POE, LOAD_USBC, LOAD_WALL_VBUS, LOAD_PA, LOAD_HF,
    LOAD_ROCKBLOCK, LOAD_LORA, LOAD_ZIGBEE, LOAD_GEIGER, LOAD_COUNT
};

/* ---------------------------------------------------------------- what the bridge tells the panel.
 * This is the DECODED content of the USB bridge protocol of P s.11. Its wire format is MESHSAT-837 and is not defined
 * anywhere (README finding F-02): no codec exists, so on the target nothing fills this structure and the core runs
 * as if no host were present (alive false). */
enum { BEARER_SAT = 1, BEARER_MESH = 2, BEARER_LTE = 4, BEARER_GPS = 8 };
enum { AMBER_BEARER_LOST = 1, AMBER_SHORE_LOST = 2, AMBER_DISK_FULL = 4 };
enum { RED_PACK_UV = 1 };
enum sos_bridge { SOS_BR_NONE = 0, SOS_BR_QUEUED_NO_BEARER, SOS_BR_SENT };
enum shore_cmd { SHORE_CMD_NONE = 0, SHORE_CMD_INPUTS_OFF, SHORE_CMD_WATER_ISOLATION, SHORE_CMD_OTHER };

typedef struct {
    bool     valid;
    uint32_t seq;          /* increments on every fresh reading: "two readings in a row" counts these */
    int32_t  mc;           /* milli-degrees C */
} panel_reading_t;

typedef struct {
    bool     alive;               /* a bridge session is talking on the CDC port */
    int8_t   display_slot;        /* the slot the bridge names for HDMI, 0..2, or -1 */
    bool     nvg;                 /* the bridge's NVG mode (P s.8) */
    uint8_t  bearers_up;          /* BEARER_* (GPS: a fix) */
    uint8_t  amber;               /* AMBER_* conditions */
    uint8_t  red;                 /* RED_* conditions */
    bool     msg_unread;
    uint16_t msg_seq;             /* the latest inbound message */
    uint8_t  sos;                 /* enum sos_bridge */
    uint32_t qr_request_seq;      /* increments on every "show QR" request from the touch UI */
    uint8_t  shore_cmd;           /* enum shore_cmd */
    bool     shore_warned;        /* the bridge has given FW-C08's warning (pack cannot discharge) */
    bool     pack_cannot_discharge; /* states S2 and S4 (FW-C08, FW-A19) as the sensor controller reports */
    bool     shutdown_cmd;        /* P s.11: the shutdown command */
    bool     kill_cmd;            /* P s.11: the kill command */
    int8_t   soc_pct;             /* the pack's state of charge, -1 unknown */
    bool     modules_dropped_keys; /* ZER s.3.4 step 6: every running module confirmed */
    uint16_t loads_wanted;        /* 1 << panel_load: what the bridge's policy wants on (FW-A06, A07, A13) */
    panel_reading_t cell_max;     /* the hottest cell (FW-C09 C1) */
    panel_reading_t inside_air;   /* inside air (FW-C09 C1) */
    panel_reading_t margin_ref;   /* FW-C15's reference (mixed air near the +70 C parts) */
} panel_bridge_t;

/* ---------------------------------------------------------------- one sample of the inputs */
typedef struct {
    bool test_sw;        /* GPIO27, low = pressed */
    bool sos_sw;         /* GPIO28, low = closed */
    bool zeroize_sw;     /* GPIO22, low = closed */
    bool emcon_rd;       /* GPIO21, low = EMCON asserted (U13's copy of EMCON_HW) */
    bool tr_aprs;        /* GPIO23, high = D8 keyed (the TX lamp lit by hardware) */
    bool exp_int;        /* GPIO24, low = an expander interrupt */
    bool hb[3];          /* GPIO10..12 */
    bool pi_shdn_req;    /* GPIO18 read as an input: low = a request on the line */
    bool pi_button;      /* SW_PI pressed; not wired (HAL_PI_BUTTON_WIRED 0, finding F-01) */
    bool epd_busy;       /* GPIO7, high while the display refreshes */
    uint16_t rail_mv;    /* RAIL_SENSE at the pin */
    panel_reading_t tmp117; /* board B's TMP117 at 0x49 (FW-C13 fallback), read over the kit bus */
    bool charger_ok;     /* the charger's status bits were read (FW-A rows' driver, owed) */
    bool charger_input_present;
    bool charger_charging;
    panel_bridge_t br;
} panel_in_t;

/* ---------------------------------------------------------------- the outputs */
typedef struct {
    bool     pi_kill;            /* GPIO19 push-pull level; low from the first instruction (FW-A11) */
    bool     pi_shdn_assert;     /* GPIO18 output enable with value 0 (FW-A10); never driven high */
    bool     slot_en[3];         /* GPIO13..15 */
    bool     hdmi_sel1, hdmi_sel2;
    bool     shore_inhibit;      /* GPIO20 */
    uint16_t pwm_permille;       /* PANEL_PWM */
    bool     sounder;            /* PWM1 on */
    uint32_t leds;               /* LED_BIT(panel_led) lit */
    bool     led_stat;           /* GPIO25, the board's status LED: 1 Hz while the core runs */
    bool     epd_power;          /* EPD_PWR_n low */
    uint16_t loads_off;          /* 1 << panel_load: loads the core forces off */
    uint16_t loads_on;           /* the bridge's wanted loads less the forced ones, as written to A:U27, A:U28, B:U6 */
    bool     charge_hold_hot;    /* FW-C13: the CHRG_INHIBIT bit's flag (FW-A19) */
    bool     charge_hold_margin; /* FW-C15: the same bit's flag */
    bool     rb_ien_request;     /* B:U6 RB_SW_IEN (FW-B13 via P corrections (17)) */
    bool     reduced_mode;       /* the reduced mode (FW-C09 fallback, FW-C14 held high) */
    bool     backlight_off;      /* P s.8 BLACKOUT, for the bridge */
    uint8_t  backlight_pct;      /* P s.8: 100, 20, 5, 0 for the bridge */
    bool     shore_refused;      /* a SHORE_INHIBIT request refused (FW-C08) */
    bool     light_valid;        /* P s.8: the VEML7700 reading for the bridge */
    uint32_t light_mlux;
} panel_out_t;

/* ---------------------------------------------------------------- injected operations */
typedef struct {
    void *ctx;
    int  (*i2c_write)(void *ctx, uint8_t addr, const uint8_t *buf, unsigned len);
    int  (*i2c_read)(void *ctx, uint8_t addr, uint8_t reg, uint8_t *buf, unsigned len);
} panel_bus_t;

typedef struct {
    void *ctx;
    ms_t (*now_ms)(void *ctx);
    /* GenKey mode 0x04 (create) and mode 0x00 (public) on a KEK slot (0 = KEK_A, 1 = KEK_B); 0 on success, negative
     * on any error; no bus operation runs past deadline_ms (ZER s.3.4 step 3). pub: 64 bytes. */
    int  (*genkey_create)(void *ctx, uint8_t slot, uint8_t pub[64], ms_t deadline_ms);
    int  (*genkey_public)(void *ctx, uint8_t slot, uint8_t pub[64], ms_t deadline_ms);
    bool (*recorded_pub)(void *ctx, uint8_t slot, uint8_t pub[64]);  /* P_A0, P_B0 (ZER I2) */
    void (*arm_slot_cut)(void *ctx, ms_t at_ms);                     /* step 0 */
    void (*tell_modules_drop_keys)(void *ctx);                       /* step 5 */
    void (*feed_watchdog)(void *ctx);
    /* the journal's flash region: read, program (pre-erased), erase */
    int  (*flash_read)(void *ctx, uint32_t off, uint8_t *buf, unsigned len);
    int  (*flash_program)(void *ctx, uint32_t off, const uint8_t *buf, unsigned len);
    int  (*flash_erase)(void *ctx);
    uint32_t flash_size;
} panel_zer_ops_t;

/* the e-paper's command layer (PDi iTC, UltraChip UC8253C class): OWED, README section 4; the core only sequences
 * power, BUSY and the page */
typedef struct {
    void *ctx;
    void (*send)(void *ctx, uint8_t page, bool full);
} panel_epd_ops_t;

/* FW-C05 (F-14, record l5r4): the slot-fault state kept beside the wipe-pending record, in its own flash region: a torn
 * record here must never read as a pending wipe, which invariant I3 would make of it inside the wipe journal */
typedef struct {
    void *ctx;
    int  (*read)(void *ctx, uint32_t off, uint8_t *buf, unsigned len);
    int  (*program)(void *ctx, uint32_t off, const uint8_t *buf, unsigned len);
    int  (*erase)(void *ctx);
    uint32_t size;
} panel_store_ops_t;

typedef struct {
    panel_bus_t      bus;
    panel_zer_ops_t  zer;
    panel_epd_ops_t  epd;
    panel_store_ops_t slots;
} panel_ops_t;

enum { SLOTREC_CYCLED = 1, SLOTREC_OFF = 2 };   /* per slot: the retry spent, left off until the operator acts */

/* ---------------------------------------------------------------- module states */
typedef struct { bool stable, raw; ms_t since; bool rose, fell; } panel_deb_t;

enum zer_journal_state { ZJ_NONE = 0, ZJ_PENDING, ZJ_DONE };
enum zer_result { ZER_DONE = 0, ZER_INCOMPLETE, ZER_SE_ABSENT, ZER_NORMAL, ZER_REARMED };
enum zer_mode { ZM_ARMED_IDLE = 0, ZM_ARMING, ZM_WIPING_WAIT, ZM_COMPLETE, ZM_INCOMPLETE, ZM_WAIT_RETURN };

typedef struct {
    uint8_t  mode;               /* enum zer_mode */
    ms_t     closed_at;
    ms_t     hold_end;           /* the end of the 5 s hold */
    bool     slots_cut;
    uint8_t  creates_done[2];    /* GenKey mode 0x04 tries per slot, the timed phase included (ZER step 7) */
    bool     verified[2];
    uint8_t  last_result;        /* enum zer_result */
    ms_t     complete_at;
    ms_t     next_retry;
    bool     aborted_shown;
    uint32_t journal_off;        /* the next free record */
    uint32_t journal_seq;
    bool     se_absent;          /* boot table: normal boot without the SE */
} panel_zer_t;

enum hot_line { HOT_LINE_UNKNOWN = 0, HOT_LINE_1HZ, HOT_LINE_5HZ, HOT_LINE_HELD_LOW, HOT_LINE_HELD_HIGH };
enum hot_state { HOT_NONE = 0, HOT_H1, HOT_H2 };

typedef struct {
    bool     have_sample, level;
    ms_t     last_edge;
    ms_t     edges[12];          /* the latest edges, newest at [0] */
    uint8_t  n_edges;
    ms_t     first_sample;
    ms_t     last_sample;            /* a read that succeeded */
    uint8_t  line;               /* enum hot_line */
    uint8_t  state;              /* enum hot_state */
    ms_t     stop_at;            /* H1 entered */
    ms_t     h2_at;
    uint32_t tmp_seq;
    uint8_t  tmp_over_h1, tmp_over_h2;
    bool     shdn_done;
} panel_hot_t;

enum slot_state { SLOT_OFF = 0, SLOT_WAIT_HB, SLOT_RUNNING, SLOT_CYCLING, SLOT_FAULT_OFF };

typedef struct {
    uint8_t state;               /* enum slot_state */
    bool    en;
    ms_t    since;               /* rail up, or rail off for a cycle */
    bool    cycled;              /* the one power-cycle has been spent */
    bool    hb_level, hb_seen;
    ms_t    hb_edge;
    bool    alive;               /* FW-C05 */
    bool    fault;               /* P s.5 slot fault */
    bool    wanted;              /* policy: this slot may run */
    bool    lost_reported;       /* the 3 s loss of a running slot reported (F-14) */
} panel_slot_t;

enum boot_phase { BOOT_ZEROIZE = 0, BOOT_EXPANDERS, BOOT_CHARGER, BOOT_HOTR1, BOOT_SLOTS, BOOT_RUN };

enum shdn_state { SHDN_IDLE = 0, SHDN_PULSE, SHDN_WAIT_HB, SHDN_KILL };

#define PANEL_EVENTS 32
enum panel_ev_type {
    EV_BOOT = 0x40,                  /* the reset reason (FW-C02), reported by the target loop */
    EV_TEST = 1, EV_SOS, EV_ZEROIZE, EV_EMCON, EV_LIGHT_DAY, EV_LIGHT_NIGHT, EV_PI, EV_TR_APRS, EV_HB1, EV_HB2,
    EV_HB3, EV_RAIL, EV_SHORE_INHIBIT, EV_SLOT_FAULT, EV_HOT_LINE, EV_I2C_RECOVERED, EV_WIPE_RESULT,
    EV_SLOT_CYCLE, EV_SLOT_OFF                  /* FW-C05: the one retry spent, the slot left off (value: the slot) */
};
typedef struct { uint8_t type; uint8_t value; ms_t at; } panel_ev_t;

typedef struct {
    const panel_ops_t *ops;
    ms_t     t0;
    uint8_t  boot;               /* enum boot_phase */
    ms_t     boot_phase_at;

    panel_deb_t sw_test, sw_sos, sw_zer, sw_emcon, sw_day, sw_night, sw_pi;

    /* controls */
    ms_t     test_down_at;
    bool     test_lamp_fired, test_qr_active;
    uint32_t qr_seq_seen;
    ms_t     qr_request_at;
    bool     qr_pending;
    ms_t     lamptest_until, batbar_until;
    ms_t     sos_closed_at;
    bool     sos_armed, sos_sent_seen, sos_cancelled;
    ms_t     sos_cancel_at;
    ms_t     pi_down_at;
    bool     pi_kill_fired;

    /* indicators */
    uint8_t  red_active, red_acked;   /* RED_COND_* bits */
    uint8_t  amb_active, amb_acked;   /* AMB_COND_* bits */
    uint16_t msg_acked_seq;
    bool     msg_acked;
    uint32_t last_br_leds;            /* the bridge-driven LEDs last shown (held on link loss) */
    bool     br_was_alive;

    /* sounder */
    uint8_t  sound;                   /* enum panel_sound */
    ms_t     sound_at;
    bool     sound_muted;

    /* lighting */
    uint8_t  light;                   /* enum panel_light_mode */
    bool     light_fault;             /* toggle inputs and RAIL_SENSE disagree */

    /* slots and display */
    panel_slot_t slot[3];
    ms_t     next_slot_at;
    uint8_t  hdmi_slot;

    /* shutdown */
    uint8_t  shdn;                    /* enum shdn_state */
    ms_t     shdn_at;
    ms_t     main_low_at;
    bool     main_low;
    ms_t     own_pull_until;          /* this controller's own pull on PI_SHDN_REQ, never read as a MAIN tap */
    bool     kill;
    ms_t     kill_at;

    /* shore */
    bool     shore_inhibit;

    /* EMCON and the RockBLOCK request (P corrections (17)) */
    bool     emcon_on;
    bool     rb_ien;

    /* hot stop, margin hold, power controls */
    panel_hot_t hot;
    bool     margin_hold;
    ms_t     margin_at;
    uint32_t margin_seq;
    uint8_t  margin_over;
    bool     margin_below_since_valid;
    ms_t     margin_below_since;
    ms_t     pack_seen_at;
    uint32_t pack_seq;
    bool     pack_ever_seen;

    /* zeroize */
    panel_zer_t zer;

    /* expanders */
    ms_t     exp_polled_at;
    uint32_t leds_written;
    bool     leds_written_valid;
    bool     exp_init_done;
    bool     leds_ramped;             /* P s.4: the first lit set after boot enabled one by one */
    bool     rb_need_fresh;           /* RB_STATUS not yet read since the EMCON release */
    uint8_t  kit_out[3][2];           /* A:U27, A:U28, B:U6 output registers last written */
    bool     kit_out_valid;
    ms_t     led_fail_at;
    bool     led_failed;

    /* the kit-bus sensors (sensors.c) and the absent secure element's retry */
    panel_reading_t tmp117;
    ms_t     tmp117_polled_at, tmp117_ok_at;
    bool     veml_ready, light_valid;
    uint16_t light_counts;
    uint32_t light_mlux;
    ms_t     veml_polled_at;
    ms_t     se_probe_at;
    uint8_t  hot_r1_level;            /* last read of A:U27 P1.5 */
    bool     rb_status;               /* B:U7 RB_STATUS */
    bool     light_day_n, light_night_n, panel_id;
    bool     exp_c_ok;

    /* e-paper */
    uint8_t  page_shown, page_want;
    ms_t     epd_last_refresh, epd_last_full;
    bool     epd_full_due;
    uint8_t  epd_step;
    ms_t     epd_step_at;
    uint32_t epd_refreshes;

    /* the bridge's view */
    panel_bridge_t br;

    /* flags the tick derives */
    bool     switches_ready;
    bool     reduced_mode_flag;      /* slots 2 and 3 only */
    bool     heat_stage_only;        /* after H1: the heat stage's module first, until C1's restore 5 K below (S-19 declined) */
    bool     hot_block_slots;        /* FW-C14 at boot: 5 Hz, raise no slot */
    bool     hot_pulse;              /* FW-C13 H1: the clean-shutdown request on PI_SHDN_REQ */
    ms_t     hot_pulse_at;
    bool     pack_fallback;          /* FW-C09 round 8: the pack readings stopped 10 s */
    bool     c1_reduced;             /* FW-C09 C1's first stage */
    bool     zer_page_hold;          /* the ZEROIZED page after a boot wipe */
    bool     pi_btn_wired;           /* the PI button on U1 P1.3 (record l8r2's draft, released with board C) */
    uint32_t slot_store_off, slot_store_seq;
    uint8_t  slot_rec_saved[3];       /* the slot-fault state last written (FW-C05) */
    bool     slot_rec_dirty;
    bool     pi_btn_pressed;

    /* events for the bridge (P s.11) */
    panel_ev_t ev[PANEL_EVENTS];
    uint8_t  ev_head, ev_count;
} panel_t;

/* ---------------------------------------------------------------- the core API */

/* FW-C01 steps 1 to 3 and FW-C02, before any other work: given the raw ZEROIZE_SW level and the levels the SLOT_EN pads
 * read as inputs, return in drive[] the level each SLOT_EN is driven at from now on (all low when the toggle is closed
 * or the journal holds PENDING). */
void panel_init(panel_t *p, const panel_ops_t *ops, ms_t now, bool zeroize_raw_closed, const bool held_slot_en[3],
                bool power_on_reset, bool drive_slot_en[3]);
/* power_on_reset: CHIP_RESET HAD_POR set AND the watchdog's REASON zero (finding F-15): HAD_POR alone stays set across a
 * watchdog reset that follows a power-on, since CHIP_RESET records the last CHIP-LEVEL reset (RP2040 datasheet 2.12.7) */
void panel_tick(panel_t *p, ms_t now, const panel_in_t *in, panel_out_t *out);

/* the operator's act (the touch UI, the bridge's retry; P s.5, FW-C05): re-arms the slot's one retry and raises a slot
 * left off. A MAIN restart is the third act: a power-on reset clears every slot's state */
void panel_slot_operator_retry(panel_t *p, unsigned slot, ms_t now);

/* the slot-fault store (slotstore.c): 0 when a record was read, 1 when empty */
int  panel_slot_store_load(panel_t *p, uint8_t st[3]);
int  panel_slot_store_save(panel_t *p, const uint8_t st[3]);
uint32_t panel_crc32(const uint8_t *b, unsigned n);

/* debounce */
void panel_deb_init(panel_deb_t *d, bool level, ms_t now);
bool panel_deb_update(panel_deb_t *d, bool raw, ms_t now);

/* lighting */
uint8_t  panel_light_mode(bool day_n, bool night_n, bool bridge_nvg, bool *fault);
uint16_t panel_light_duty(uint8_t mode);   /* the one dimmer; the TX lamp follows it (F-05) */
void     panel_hdmi_encode(uint8_t slot, bool *sel1, bool *sel2);   /* F-13 */
unsigned panel_modules_lost(const panel_t *p);                       /* F-07 */
uint32_t panel_light_filter(uint8_t mode, uint32_t leds);

/* HOT-R1 decoding (FW-C14) */
void    panel_hot_sample(panel_hot_t *h, bool level, ms_t now);
uint8_t panel_hot_classify(panel_hot_t *h, ms_t now);

/* zeroize: the journal and the wipe (ZER s.3.4, s.3.5) */
uint8_t panel_zj_scan(panel_t *p);           /* enum zer_journal_state; a torn record reads PENDING (I3) */
int     panel_zj_append(panel_t *p, uint8_t state);
uint8_t panel_zer_wipe_timed(panel_t *p, ms_t hold_end);  /* steps 0 to 5; enum zer_result */
uint8_t panel_zer_wipe_untimed(panel_t *p);   /* step 7 and the boot table's runs */
uint8_t panel_zer_boot(panel_t *p, bool toggle_closed, bool *slots_may_power); /* the table of s.3.5 */

/* the expanders (FW-A08, P s.4, FW-C14) */
int  panel_exp_boot(panel_t *p);
int  panel_exp_write_leds(panel_t *p, uint32_t leds);
int  panel_exp_service(panel_t *p, ms_t now);
int  panel_exp_write_kit(panel_t *p, uint16_t loads_on, bool rb_ien);

/* the kit-bus sensors (sensors.c) */
int  panel_tmp117_poll(panel_t *p, ms_t now);
int  panel_veml_init(panel_t *p);
int  panel_veml_poll(panel_t *p, ms_t now);
#define PANEL_TMP117_POLL_MS 250u   /* SESSION S-36: four looks a conversion cycle (1 s at the TMP117's reset setting) */
#define PANEL_VEML_POLL_MS   1000u
#define PANEL_SE_PROBE_MS    60000u /* SESSION S-35: ZER 3.5 "the SE is retried" with no period stated */

/* the kit bus recovery (FW-K04), through a bit-bang interface */
typedef struct {
    void *ctx;
    void (*scl)(void *ctx, bool level);
    bool (*sda)(void *ctx);
    void (*stop)(void *ctx);
    void (*delay_us)(void *ctx, unsigned us);
} panel_bitbang_t;
int panel_bus_recover(const panel_bitbang_t *bb);

/* events */
bool panel_ev_pop(panel_t *p, panel_ev_t *ev);
void panel_ev_report(panel_t *p, uint8_t type, uint8_t value, ms_t at);  /* e.g. EV_I2C_RECOVERED from the target loop */

#endif
