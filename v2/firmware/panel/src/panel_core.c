/*
 * panel_core.c: the panel controller's duties as state machines with a millisecond tick (MESHSAT-1357 Layer 12).
 *
 * Statements implemented, by source (README.md section 2 has the statement-to-test table):
 *   PANEL.md s.3 (debounce, PI_SHDN_REQ active low, PI_KILL), s.4 (LED drive rule: expander.c), s.5 (boot order, slot
 *   fault and power-cycle, HDMI select, PI button), s.6 (the hardware lines: the core never drives them), s.8 (lighting,
 *   NVG, BLACKOUT), s.9 (indicators, TEST, SOS, ZEROIZE, sounder, e-paper), s.10 (SHORE_INHIBIT);
 *   HW-FW-CONTRACT.md FW-C01 to C08, C10, C11, C13 to C15, and C09 in part (the 10 s fallback and C1's first stage).
 *
 * Pure logic: no register is touched. Prototype firmware for an unbuilt kit; nothing has run on hardware.
 */
#include <string.h>

#include "panel.h"

/* ------------------------------------------------------------------------------------------------ tables */

const uint8_t panel_led_colour[LED_COUNT] = {
    [LED_SOSACT] = COL_RED,   [LED_MWARN] = COL_RED,    [LED_MCAUT] = COL_AMBER, [LED_CHG] = COL_WHITE,
    [LED_SAT] = COL_GREEN,    [LED_MESH] = COL_GREEN,   [LED_LTE] = COL_GREEN,   [LED_GPS] = COL_GREEN,
    [LED_SHORE] = COL_GREEN,  [LED_MSG] = COL_WHITE,    [LED_PIRING] = COL_AMBER, [LED_BAT1] = COL_AMBER,
    [LED_BAT2] = COL_GREEN,   [LED_BAT3] = COL_GREEN,   [LED_BAT4] = COL_GREEN,  [LED_BAT5] = COL_GREEN,
    [LED_TXTEST] = COL_RED,
};

/* The e-paper's messages. The quoted ones are PANEL.md s.9's and FW-C13's and FW-C15's words; the test module checks
 * them against those pages. The rest are SESSION S-12. */
const char *const panel_page_text[PAGE_COUNT] = {
    [PAGE_NONE] = "",
    [PAGE_IDLE] = "IDLE",
    [PAGE_QR] = "ENROLMENT QR",
    [PAGE_SOS_ARMED] = "SOS ARMED",
    [PAGE_SOS_SENT] = "SOS SENT",
    [PAGE_SOS_QUEUED_EMCON] = "SOS QUEUED: EMCON ON, OPEN EMCON TO SEND",
    [PAGE_SOS_QUEUED_NO_BEARER] = "SOS QUEUED: NO BEARER",
    [PAGE_SOS_NO_HOST] = "SOS NOT SENT: NO HOST",
    [PAGE_SOS_CANCELLED] = "SOS CANCELLED",
    [PAGE_ZEROIZE_ABORTED] = "ZEROIZE ABORTED",
    [PAGE_ZEROIZED] = "ZEROIZED\nKEYS DESTROYED AND VERIFIED",
    [PAGE_ZEROIZE_INCOMPLETE] = "ZEROIZE INCOMPLETE: SLOTS HELD OFF, RETRYING",
    [PAGE_SE_ABSENT] = "SECURE ELEMENT NOT ANSWERING: DRIVES STAY LOCKED",
    [PAGE_HOT_STOP] = "HOT STOP: COOLING",
    [PAGE_HOT_SHUTDOWN] = "HOT SHUTDOWN: RESTART WITH MAIN WHEN COOL",
    [PAGE_MARGIN_HOLD] = "MARGIN HOLD: COOLING",
    [PAGE_SOS_QUEUED_MARGIN] = "SOS QUEUED: MARGIN HOLD, COOLING",
    [PAGE_EMCON] = "EMCON ON: EVERY SEND QUEUED",
};

/* red and amber conditions of P s.9 */
enum { RC_SOS = 1, RC_ZEROIZE = 2, RC_THERMAL = 4, RC_PACK_UV = 8, RC_SE_ABSENT = 16 };
enum { AC_BEARER_LOST = 1, AC_SHORE_LOST = 2, AC_DISK_FULL = 4, AC_SLOT_FAULT = 8, AC_MARGIN = 16 };

#define HEAT_STAGE_SLOT 1u      /* FW-C09/C13: the heat stage's one module, slot 2 as board B is generated (index 1) */

/* ------------------------------------------------------------------------------------------------ helpers */

static bool after(ms_t now, ms_t t) { return (int32_t)(now - t) >= 0; }
static bool within(ms_t now, ms_t until) { return (int32_t)(until - now) > 0; }
static bool phase_on(ms_t now, ms_t half) { return ((now / half) & 1u) == 0; }

static void ev_push(panel_t *p, uint8_t type, uint8_t value, ms_t at)
{
    uint8_t i = (uint8_t)((p->ev_head + p->ev_count) % PANEL_EVENTS);
    p->ev[i].type = type;
    p->ev[i].value = value;
    p->ev[i].at = at;
    if (p->ev_count < PANEL_EVENTS)
        p->ev_count++;
    else
        p->ev_head = (uint8_t)((p->ev_head + 1) % PANEL_EVENTS);  /* the oldest is dropped */
}

void panel_ev_report(panel_t *p, uint8_t type, uint8_t value, ms_t at) { ev_push(p, type, value, at); }

bool panel_ev_pop(panel_t *p, panel_ev_t *ev)
{
    if (!p->ev_count)
        return false;
    *ev = p->ev[p->ev_head];
    p->ev_head = (uint8_t)((p->ev_head + 1) % PANEL_EVENTS);
    p->ev_count--;
    return true;
}

/* ------------------------------------------------------------------------------------------------ debounce (P s.3) */

void panel_deb_init(panel_deb_t *d, bool level, ms_t now)
{
    d->stable = d->raw = level;
    d->since = now;
    d->rose = d->fell = false;
}

/* 30 ms: the stable level follows the raw level only after it has held 30 ms. Returns true on a stable change. */
bool panel_deb_update(panel_deb_t *d, bool raw, ms_t now)
{
    d->rose = d->fell = false;
    if (raw != d->raw) {
        d->raw = raw;
        d->since = now;
        return false;
    }
    if (raw != d->stable && after(now, d->since + PANEL_DEBOUNCE_MS)) {
        d->stable = raw;
        d->rose = raw;
        d->fell = !raw;
        return true;
    }
    return false;
}

/* ------------------------------------------------------------------------------------------------ lighting (P s.8) */

uint8_t panel_light_mode(bool day_n, bool night_n, bool bridge_nvg, bool *fault)
{
    *fault = false;
    if (!day_n && !night_n) {
        *fault = true;           /* both low cannot happen on a sound toggle: the dimmer of the two (SESSION S-13) */
        return bridge_nvg ? LIGHT_NVG : LIGHT_NIGHT;
    }
    if (!day_n)
        return LIGHT_DAY;
    if (!night_n)
        return bridge_nvg ? LIGHT_NVG : LIGHT_NIGHT;
    return LIGHT_BLACKOUT;
}

/* One dimmer for the whole panel. The TX lamp is never dimmed below 10 %: while it is lit the duty is raised to
 * 10 % (finding F-05: in NVG this lifts the red and amber LEDs to 10 % too). BLACKOUT is 0, TX lamp included. */
uint16_t panel_light_duty(uint8_t mode, bool tx_lamp_lit)
{
    uint16_t d;
    switch (mode) {
    case LIGHT_DAY: d = PANEL_DUTY_DAY; break;
    case LIGHT_NIGHT: d = PANEL_DUTY_NIGHT; break;
    case LIGHT_NVG: d = PANEL_DUTY_NVG; break;
    default: return 0;
    }
    if (tx_lamp_lit && d < PANEL_DUTY_TX_FLOOR)
        d = PANEL_DUTY_TX_FLOOR;
    return d;
}

/* NVG: red and amber indicators only. BLACKOUT: nothing. */
uint32_t panel_light_filter(uint8_t mode, uint32_t leds)
{
    if (mode == LIGHT_BLACKOUT)
        return 0;
    if (mode != LIGHT_NVG)
        return leds;
    uint32_t out = 0;
    for (unsigned l = 0; l < LED_COUNT; l++)
        if ((leds & LED_BIT(l)) && (panel_led_colour[l] == COL_RED || panel_led_colour[l] == COL_AMBER))
            out |= LED_BIT(l);
    return out;
}

/* ------------------------------------------------------------------------------------------------ HOT-R1 (FW-C14) */

void panel_hot_sample(panel_hot_t *h, bool level, ms_t now)
{
    h->last_sample = now;
    if (!h->have_sample) {
        h->have_sample = true;
        h->level = level;
        h->first_sample = now;
        return;
    }
    if (level != h->level) {
        h->level = level;
        h->last_edge = now;
        memmove(&h->edges[1], &h->edges[0], sizeof h->edges - sizeof h->edges[0]);
        h->edges[0] = now;
        if (h->n_edges < 12)
            h->n_edges++;
    }
}

/* toggling at 1 Hz (one edge a second), at 5 Hz (five a second), held low or held high (no edge for 3 s) */
uint8_t panel_hot_classify(panel_hot_t *h, ms_t now)
{
    if (!h->have_sample)
        return h->line = HOT_LINE_UNKNOWN;
    if (after(now, h->last_sample + PANEL_HOTR1_HELD_MS))
        return h->line = HOT_LINE_HELD_HIGH;        /* no read for 3 s: the detector lost, never a stale level (S-17) */
    if (after(now, h->last_sample + PANEL_EXP_POLL_MS + 500u))
        return h->line;                             /* reads late: no new verdict on old evidence */
    bool recent = h->n_edges && !after(now, h->last_edge + PANEL_HOTR1_HELD_MS);
    if (!recent) {
        if (!after(now, h->first_sample + PANEL_HOTR1_HELD_MS) && !h->n_edges)
            return h->line = HOT_LINE_UNKNOWN;
        return h->line = h->level ? HOT_LINE_HELD_HIGH : HOT_LINE_HELD_LOW;
    }
    unsigned in_window = 0;
    for (unsigned i = 0; i < h->n_edges; i++)
        if (!after(now, h->edges[i] + PANEL_HOTR1_WINDOW_MS))
            in_window++;
    if (in_window >= 5)
        return h->line = HOT_LINE_5HZ;
    if (!after(now, h->first_sample + PANEL_HOTR1_WINDOW_MS))
        return h->line = HOT_LINE_UNKNOWN;          /* too early to tell 1 Hz from 5 Hz */
    return h->line = HOT_LINE_1HZ;
}

/* ------------------------------------------------------------------------------------------------ init (FW-C01, C02) */

static void slot_set(panel_slot_t *s, bool en, uint8_t state, ms_t now)
{
    s->en = en;
    s->state = state;
    s->since = now;
}

void panel_init(panel_t *p, const panel_ops_t *ops, ms_t now, bool zeroize_raw_closed, const bool held[3],
                bool drive[3])
{
    memset(p, 0, sizeof *p);
    p->ops = ops;
    p->t0 = now;
    p->boot = BOOT_ZEROIZE;
    p->boot_phase_at = now;
    p->br.display_slot = -1;
    p->br.soc_pct = -1;
    p->rb_status = true;           /* not yet read low: RB_SW_IEN stays down (P corrections (17)) */
    p->light_day_n = p->light_night_n = true;
    panel_deb_init(&p->sw_zer, !zeroize_raw_closed, now);
    /* FW-C01 step 3 and FW-C02: the toggle or a wipe-pending record drives every SLOT_EN low first (D-03) */
    bool pending = panel_zj_scan(p) == ZJ_PENDING;
    for (unsigned i = 0; i < 3; i++) {
        drive[i] = (zeroize_raw_closed || pending) ? false : held[i];
        if (drive[i])
            slot_set(&p->slot[i], true, SLOT_WAIT_HB, now);      /* a module kept up by the keeper (FW-C02) */
        else
            slot_set(&p->slot[i], false, SLOT_OFF, now);
    }
}

void panel_slot_operator_retry(panel_t *p, unsigned i, ms_t now)
{
    if (i < 3 && p->slot[i].state == SLOT_FAULT_OFF) {
        p->slot[i].fault = false;
        p->slot[i].cycled = false;
        slot_set(&p->slot[i], false, SLOT_OFF, now);
    }
}

/* ------------------------------------------------------------------------------------------------ the tick, parts */

static void sound_start(panel_t *p, uint8_t s, ms_t now)
{
    p->sound = s;
    p->sound_at = now;
}

static void controls_test(panel_t *p, ms_t now)
{
    bool pressed = !p->sw_test.stable;
    if (p->br.qr_request_seq != p->qr_seq_seen) {
        p->qr_seq_seen = p->br.qr_request_seq;
        p->qr_pending = true;
        p->qr_request_at = now;
    }
    if (p->sw_test.fell) {
        p->test_down_at = now;
        p->test_lamp_fired = false;
        p->test_qr_active = false;
        ev_push(p, EV_TEST, 1, now);
    }
    if (pressed) {
        if (!p->test_lamp_fired && after(now, p->test_down_at + PANEL_TEST_LAMP_HOLD_MS)) {
            p->test_lamp_fired = true;                       /* hold 2 s = lamp test */
            p->lamptest_until = now + PANEL_LAMPTEST_MS;
            p->batbar_until = p->lamptest_until + PANEL_BATBAR_MS;
            sound_start(p, SND_DOUBLE_CHIRP, now);           /* finding F-06: "a chirp" vs "double chirp" */
        }
        if (!p->test_qr_active && p->qr_pending && after(now, p->test_down_at + PANEL_TEST_QR_HOLD_MS) &&
            !after(now, p->qr_request_at + PANEL_QR_WINDOW_MS))
            p->test_qr_active = true;                        /* hold 5 s within 60 s of a show QR request */
    }
    if (p->sw_test.rose) {
        ev_push(p, EV_TEST, 0, now);
        if (!p->test_lamp_fired) {                           /* short press = acknowledge */
            p->red_acked = p->red_active;
            p->amb_acked = p->amb_active;
            p->sound_muted = true;
            p->msg_acked = true;
            p->msg_acked_seq = p->br.msg_seq;
            p->batbar_until = now + PANEL_BATBAR_MS;
            sound_start(p, SND_CHIRP, now);
        }
        if (p->test_qr_active) {
            p->test_qr_active = false;                       /* the QR only while held */
            p->qr_pending = false;
        }
    }
    if (p->qr_pending && !p->test_qr_active && after(now, p->qr_request_at + PANEL_QR_WINDOW_MS))
        p->qr_pending = false;
}

static void controls_sos(panel_t *p, ms_t now)
{
    bool closed = !p->sw_sos.stable;
    if (p->sw_sos.fell) {
        p->sos_closed_at = now;
        ev_push(p, EV_SOS, 1, now);
    }
    if (closed && !p->sos_armed && after(now, p->sos_closed_at + PANEL_SOS_HOLD_MS)) {
        p->sos_armed = true;                                 /* SOS closed 2 s = SOS mode (FW-C10) */
        p->sos_sent_seen = false;
        p->sos_cancelled = false;
        p->sound_muted = false;
        p->red_acked &= (uint8_t)~RC_SOS;
    }
    if (p->sw_sos.rose) {
        ev_push(p, EV_SOS, 0, now);
        if (p->sos_armed) {                                  /* flipping back cancels */
            p->sos_armed = false;
            p->sos_cancelled = true;
            p->sos_cancel_at = now;
        }
    }
    if (p->sos_armed && p->br.alive && p->br.sos == SOS_BR_SENT)
        p->sos_sent_seen = true;
}

static bool any_slot_alive(const panel_t *p)
{
    return p->slot[0].alive || p->slot[1].alive || p->slot[2].alive;
}

static void cut_all_slots(panel_t *p, ms_t now)
{
    for (unsigned i = 0; i < 3; i++)
        slot_set(&p->slot[i], false, p->slot[i].state == SLOT_FAULT_OFF ? SLOT_FAULT_OFF : SLOT_OFF, now);
}

static void controls_zeroize(panel_t *p, ms_t now)
{
    bool closed = !p->sw_zer.stable;
    if (p->sw_zer.fell)
        ev_push(p, EV_ZEROIZE, 1, now);
    if (p->sw_zer.rose)
        ev_push(p, EV_ZEROIZE, 0, now);
    switch (p->zer.mode) {
    case ZM_ARMED_IDLE:
        if (closed) {
            p->zer.mode = ZM_ARMING;
            p->zer.closed_at = now;
            p->red_acked &= (uint8_t)~RC_ZEROIZE;
        }
        break;
    case ZM_ARMING:
        if (!closed) {                                       /* flipping back inside 5 s aborts */
            p->zer.mode = ZM_ARMED_IDLE;
            p->zer.aborted_shown = true;
            p->zer.complete_at = now;
        } else if (after(now, p->zer.closed_at + PANEL_ZEROIZE_HOLD_MS)) {
            p->zer.hold_end = now;                           /* the 5 s commit */
            p->zer.aborted_shown = false;
            panel_zer_wipe_timed(p, now);
            p->zer.mode = ZM_WIPING_WAIT;
        }
        break;
    case ZM_WIPING_WAIT:                                     /* step 6 */
        if (!any_slot_alive(p) || (p->br.alive && p->br.modules_dropped_keys) ||
            after(now, p->zer.hold_end + PANEL_ZER_KILL_AFTER_MS)) {
            cut_all_slots(p, now);
            p->zer.slots_cut = true;
            if (p->zer.last_result != ZER_DONE)
                panel_zer_wipe_untimed(p);                   /* step 7, slots already off */
            p->zer.mode = p->zer.last_result == ZER_DONE ? ZM_COMPLETE : ZM_INCOMPLETE;
            p->zer.complete_at = now;
            p->sound_muted = false;
            if (p->zer.mode == ZM_COMPLETE) {
                sound_start(p, SND_ZER_COMPLETE, now);       /* step 8 */
                p->epd_full_due = true;
            }
            ev_push(p, EV_WIPE_RESULT, p->zer.last_result, now);
        }
        break;
    case ZM_COMPLETE:
        if (!closed)
            p->zer.mode = ZM_ARMED_IDLE;                     /* re-armed only when the toggle returns */
        break;
    case ZM_INCOMPLETE:
    default:
        break;                                               /* slots held off; retried at every boot */
    }
}

static bool zeroize_holds_slots(const panel_t *p)
{
    return p->zer.mode == ZM_WIPING_WAIT ? p->zer.slots_cut
         : p->zer.mode == ZM_COMPLETE || p->zer.mode == ZM_INCOMPLETE;
}

/* the PI button (P s.5, FW-C03): short press = clean shutdown, held 8 s = PI_KILL. Not wired: finding F-01. */
static void start_shutdown(panel_t *p, ms_t now)
{
    if (p->shdn == SHDN_IDLE && !p->kill) {
        p->shdn = SHDN_PULSE;
        p->shdn_at = now;
    }
}

static void do_kill(panel_t *p, ms_t now)
{
    if (!p->kill) {
        p->kill = true;
        p->kill_at = now;
    }
}

static void controls_pi(panel_t *p, ms_t now)
{
    if (p->sw_pi.rose) {
        p->pi_down_at = now;
        p->pi_kill_fired = false;
        ev_push(p, EV_PI, 1, now);
    }
    if (p->sw_pi.stable && !p->pi_kill_fired && after(now, p->pi_down_at + PANEL_PI_KILL_PRESS_MS)) {
        p->pi_kill_fired = true;
        do_kill(p, now);
    }
    if (p->sw_pi.fell) {
        ev_push(p, EV_PI, 0, now);
        if (!p->pi_kill_fired)
            start_shutdown(p, now);
    }
}

/* MAIN taps arrive on PI_SHDN_REQ as the LTC2954's INT, low for at least 32 ms (FW-A10, FW-A12) */
static void shutdown_step(panel_t *p, ms_t now, const panel_in_t *in)
{
    if (p->shdn == SHDN_IDLE && !p->kill) {
        if (!in->pi_shdn_req && after(now, p->own_pull_until)) {
            if (!p->main_low) {
                p->main_low = true;
                p->main_low_at = now;
            } else if (after(now, p->main_low_at + PANEL_MAIN_TAP_MS)) {
                p->main_low = false;
                start_shutdown(p, now);
            }
        } else {
            p->main_low = false;
        }
        if (p->br.alive && p->br.shutdown_cmd)
            start_shutdown(p, now);
    }
    if (p->br.alive && p->br.kill_cmd)
        do_kill(p, now);
    switch (p->shdn) {
    case SHDN_PULSE:
        if (after(now, p->shdn_at + PANEL_SHDN_PULSE_MS)) {
            p->shdn = SHDN_WAIT_HB;
            p->shdn_at = now;
        }
        break;
    case SHDN_WAIT_HB:
        if (!any_slot_alive(p) || after(now, p->shdn_at + PANEL_SHDN_WAIT_MS)) {
            p->shdn = SHDN_KILL;
            do_kill(p, now);
        }
        break;
    default:
        break;
    }
}

/* FW-C05: a slot is alive while its line toggles; lost after 3 s without an edge. P s.5: 60 s flat after the rail came
 * up is a slot fault, power-cycled once (5 s off), then left off until the operator acts. */
static void slots_heartbeats(panel_t *p, ms_t now, const panel_in_t *in)
{
    for (unsigned i = 0; i < 3; i++) {
        panel_slot_t *s = &p->slot[i];
        bool lvl = in->hb[i];
        if (!s->hb_seen) {
            s->hb_seen = true;
            s->hb_level = lvl;
        } else if (lvl != s->hb_level) {
            s->hb_level = lvl;
            s->hb_edge = now;
            if (!s->alive)
                ev_push(p, (uint8_t)(EV_HB1 + i), 1, now);
            s->alive = true;
        }
        if (s->alive && after(now, s->hb_edge + PANEL_HB_LOST_MS)) {
            s->alive = false;
            ev_push(p, (uint8_t)(EV_HB1 + i), 0, now);
        }
        if (!s->en)
            s->alive = s->alive && !after(now, s->hb_edge + PANEL_HB_LOST_MS);
    }
}

static void slots_policy(panel_t *p, ms_t now)
{
    bool want[3] = { true, true, true };
    bool shutting = p->kill || p->shdn != SHDN_IDLE;
    bool reduced = p->reduced_mode_flag;
    for (unsigned i = 0; i < 3; i++) {
        if (zeroize_holds_slots(p))
            want[i] = false;
        if (shutting && !p->slot[i].en)
            want[i] = false;                                 /* a shutdown raises nothing; PI_KILL removes power */
        if (reduced && i == 0)
            want[i] = false;                                 /* the reduced mode: slots 2 and 3 */
        if (p->hot.state == HOT_H1 && after(now, p->hot.stop_at + PANEL_SHDN_PULSE_MS) &&
            (!p->slot[i].alive || p->hot.shdn_done))
            want[i] = false;                         /* FW-C13: each slot once it has stopped, all at 60 s */
        if (p->heat_stage_only && i != HEAT_STAGE_SLOT)
            want[i] = false;
        if (p->hot.state == HOT_H2)
            want[i] = false;
        if (p->boot != BOOT_RUN && !p->slot[i].en)
            want[i] = false;                                 /* nothing new rises before FW-C01 step 6 */
        p->slot[i].wanted = want[i];
    }
    for (unsigned i = 0; i < 3; i++) {
        panel_slot_t *s = &p->slot[i];
        if (!s->wanted) {
            if (s->en || s->state == SLOT_CYCLING)
                slot_set(s, false, s->state == SLOT_FAULT_OFF ? SLOT_FAULT_OFF : SLOT_OFF, now);
            continue;
        }
        switch (s->state) {
        case SLOT_OFF:
            if (after(now, p->next_slot_at)) {               /* one at a time */
                slot_set(s, true, SLOT_WAIT_HB, now);
                p->next_slot_at = now + PANEL_SLOT_STAGGER_MS;
            }
            break;
        case SLOT_WAIT_HB:
            if (s->alive && after(s->hb_edge, s->since)) {
                s->state = SLOT_RUNNING;
                s->fault = false;
            } else if (after(now, s->since + PANEL_SLOT_FLAT_MS)) {
                s->fault = true;
                ev_push(p, EV_SLOT_FAULT, (uint8_t)i, now);
                if (!s->cycled) {
                    s->cycled = true;
                    slot_set(s, false, SLOT_CYCLING, now);
                } else {
                    slot_set(s, false, SLOT_FAULT_OFF, now);
                }
            }
            break;
        case SLOT_CYCLING:
            if (after(now, s->since + PANEL_SLOT_CYCLE_OFF_MS))
                slot_set(s, true, SLOT_WAIT_HB, now);
            break;
        default:
            break;
        }
    }
}

/* FW-C06: follow the bridge's display owner; with no instruction the lowest live slot; never a dark slot */
static void display_select(panel_t *p)
{
    int pick = -1;
    if (p->br.alive && p->br.display_slot >= 0 && p->br.display_slot < 3 && p->slot[p->br.display_slot].alive)
        pick = p->br.display_slot;
    for (int i = 0; pick < 0 && i < 3; i++)
        if (p->slot[i].alive)
            pick = i;
    if (pick >= 0)
        p->hdmi_slot = (uint8_t)pick;                        /* all dark: the last selection stays */
}

/* FW-C08, P s.10 */
static void shore_step(panel_t *p, ms_t now, panel_out_t *out)
{
    bool want = p->shore_inhibit;
    out->shore_refused = false;
    if (p->br.alive) {
        switch (p->br.shore_cmd) {
        case SHORE_CMD_INPUTS_OFF:
        case SHORE_CMD_WATER_ISOLATION:
            if (p->br.pack_cannot_discharge && !p->br.shore_warned) {
                out->shore_refused = true;                   /* the warning comes first (S2, S4) */
                want = false;
            } else {
                want = true;
            }
            break;
        case SHORE_CMD_OTHER:
            out->shore_refused = true;                       /* never a charge hold */
            want = false;
            break;
        default:
            want = false;
            break;
        }
    }
    if (want != p->shore_inhibit)
        ev_push(p, EV_SHORE_INHIBIT, want, now);
    p->shore_inhibit = want;
}

/* FW-C07 and P corrections (17): the RockBLOCK's ENABLE request goes low on EMCON and rises after a release only once
 * RB_STATUS reads low */
static void emcon_step(panel_t *p, ms_t now)
{
    bool on = !p->sw_emcon.stable;
    if (p->sw_emcon.fell || p->sw_emcon.rose)
        ev_push(p, EV_EMCON, on, now);
    if (on) {
        p->rb_ien = false;
        p->rb_need_fresh = true;
    } else if (!p->rb_ien && !p->rb_need_fresh && !p->rb_status) {
        p->rb_ien = true;
    }
    p->emcon_on = on;
}

/* FW-C13, FW-C14: the hot stop */
static bool fresh_two(uint32_t seq, uint32_t *seen, bool cond, uint8_t *count)
{
    if (seq == *seen)
        return *count >= 2;
    *seen = seq;
    *count = cond ? (uint8_t)(*count + 1) : 0;
    return *count >= 2;
}

static void hot_step(panel_t *p, ms_t now, const panel_in_t *in)
{
    panel_hot_t *h = &p->hot;
    uint8_t prev = h->line;
    uint8_t line = panel_hot_classify(h, now);
    if (line == HOT_LINE_UNKNOWN && p->boot == BOOT_RUN)
        line = h->line = HOT_LINE_HELD_HIGH;         /* never read since the start-up decision (S-17) */
    if (line != prev)
        ev_push(p, EV_HOT_LINE, line, now);
    bool tmp_h1 = false, tmp_h2 = false, tmp_rel = false;
    if (in->tmp117.valid && in->tmp117.seq != h->tmp_seq) {
        h->tmp_seq = in->tmp117.seq;
        h->tmp_over_h1 = in->tmp117.mc >= PANEL_HOT_TMP117_H1_MC ? (uint8_t)(h->tmp_over_h1 + 1) : 0;
        h->tmp_over_h2 = in->tmp117.mc >= PANEL_HOT_TMP117_H2_MC ? (uint8_t)(h->tmp_over_h2 + 1) : 0;
    }
    if (line == HOT_LINE_HELD_HIGH) {
        tmp_h1 = h->tmp_over_h1 >= 2;
        tmp_h2 = h->tmp_over_h2 >= 2;
        tmp_rel = in->tmp117.valid && in->tmp117.mc <= PANEL_HOT_TMP117_REL_MC;
    }
    bool want_h2 = line == HOT_LINE_HELD_LOW || (h->state == HOT_H1 && tmp_h2);
    bool want_h1 = line == HOT_LINE_5HZ || tmp_h1;
    if (want_h2 && h->state != HOT_H2) {
        h->state = HOT_H2;
        h->h2_at = now;
    } else if (want_h1 && h->state == HOT_NONE) {
        h->state = HOT_H1;
        h->stop_at = now;
        h->shdn_done = false;
        p->hot_pulse_at = now;
        p->hot_pulse = true;                                 /* ask every running module for a clean shutdown */
        p->red_acked &= (uint8_t)~RC_THERMAL;
    }
    if (h->state == HOT_H1) {
        if (!h->shdn_done && (!any_slot_alive(p) || after(now, h->stop_at + PANEL_HOT_SHDN_WAIT_MS)) &&
            after(now, h->stop_at + PANEL_SHDN_PULSE_MS))
            h->shdn_done = true;                             /* then drop SLOT_EN1..3 */
        bool cool = line == HOT_LINE_1HZ || (line == HOT_LINE_HELD_HIGH && tmp_rel);
        if (cool && after(now, h->stop_at + PANEL_HOT_RELEASE_MS)) {
            h->state = HOT_NONE;                             /* raise the heat stage's one module */
            p->heat_stage_only = true;
        }
    }
    if (h->state == HOT_H2) {
        bool shown = p->page_shown == PAGE_HOT_SHUTDOWN && p->epd_step == 0;
        if (shown || after(now, h->h2_at + PANEL_H2_PAGE_WAIT_MS))
            do_kill(p, now);                                 /* then PI_KILL high, as FW-C03 does */
    }
    if (p->hot_pulse && after(now, p->hot_pulse_at + PANEL_SHDN_PULSE_MS))
        p->hot_pulse = false;
}

/* FW-C15: the margin hold (PROVISIONAL) */
#ifndef PANEL_MARGIN_REF_OFFSET_MC
#define PANEL_MARGIN_REF_OFFSET_MC 0   /* the reference's offset calibrated at T-H1 (R-104); 0 until calibrated */
#endif
static void margin_step(panel_t *p, ms_t now)
{
    const panel_reading_t *r = &p->br.margin_ref;
    const int32_t trig = PANEL_MARGIN_TRIGGER_MC + PANEL_MARGIN_REF_OFFSET_MC;
    if (!r->valid)
        return;
    bool two = fresh_two(r->seq, &p->margin_seq, r->mc >= trig, &p->margin_over);
    if (!p->margin_hold && two) {
        p->margin_hold = true;
        p->margin_at = now;
        p->amb_acked &= (uint8_t)~AC_MARGIN;
    } else if (p->margin_hold && after(now, p->margin_at + PANEL_MARGIN_RESTORE_MS) &&
               r->mc <= trig - PANEL_MARGIN_RESTORE_DK_MC) {
        p->margin_hold = false;
        p->margin_over = 0;
    }
}

/* FW-C09, in part: C1's first stage (shed to the reduced mode at +50 C inside air or +55 C on a cell, restore 5 K
 * below) and the round-8 fallback (the pack readings stopped 10 s: the reduced mode with both outlets off). */
static void power_controls_step(panel_t *p, ms_t now)
{
    const panel_reading_t *cell = &p->br.cell_max, *air = &p->br.inside_air;
    if (cell->valid && cell->seq != p->pack_seq) {
        p->pack_seq = cell->seq;
        p->pack_seen_at = now;
        p->pack_ever_seen = true;
    }
    p->pack_fallback = p->pack_ever_seen && after(now, p->pack_seen_at + 10000u);
    if (!p->pack_fallback && cell->valid) {
        bool hot = cell->mc >= 55000 || (air->valid && air->mc >= 50000);
        bool cool = cell->mc <= 50000 && (!air->valid || air->mc <= 45000);
        if (hot)
            p->c1_reduced = true;
        else if (cool)
            p->c1_reduced = false;
    }
}

/* ------------------------------------------------------------------------------------------------ indicators */

static uint32_t indicators(panel_t *p, ms_t now, const panel_in_t *in)
{
    uint32_t L = 0;
    /* conditions */
    uint8_t red = 0, amb = 0;
    if (p->sos_armed)
        red |= RC_SOS;
    if (p->zer.mode == ZM_ARMING || p->zer.mode == ZM_INCOMPLETE || p->zer.mode == ZM_WIPING_WAIT)
        red |= RC_ZEROIZE;
    if (p->hot.state != HOT_NONE)
        red |= RC_THERMAL;
    if (p->br.red & RED_PACK_UV)
        red |= RC_PACK_UV;
    if (p->zer.se_absent)
        red |= RC_SE_ABSENT;
    if (p->br.amber & AMBER_BEARER_LOST)
        amb |= AC_BEARER_LOST;
    if (p->br.amber & AMBER_SHORE_LOST)
        amb |= AC_SHORE_LOST;
    if (p->br.amber & AMBER_DISK_FULL)
        amb |= AC_DISK_FULL;
    for (unsigned i = 0; i < 3; i++)
        if (p->slot[i].fault)
            amb |= AC_SLOT_FAULT;                            /* P s.5 names MASTER CAUT (finding F-07) */
    if (p->margin_hold)
        amb |= AC_MARGIN;
    p->red_active = red;
    p->amb_active = amb;
    p->red_acked &= red;                                     /* a cleared condition forgets its acknowledgement */
    p->amb_acked &= amb;

    /* MASTER WARN: flashes for an unacknowledged red condition; ZEROIZE's own indications (s.9) override */
    bool warn_flash = (red & (uint8_t)~p->red_acked) != 0;
    bool warn_on = red != 0;
    if (p->zer.mode == ZM_ARMING || p->zer.mode == ZM_INCOMPLETE) {
        warn_flash = true;
        warn_on = true;
    } else if (p->zer.mode == ZM_COMPLETE) {
        warn_on = true;
        warn_flash = false;
    }
    if (warn_on && (!warn_flash || phase_on(now, PANEL_FLASH_WARN_HALF_MS)))
        L |= LED_BIT(LED_MWARN);

    /* MASTER CAUT: flashes for an unacknowledged amber condition; EMCON steady */
    bool caut_flash = (amb & (uint8_t)~p->amb_acked) != 0;
    bool caut_on = amb != 0 || p->emcon_on;
    if (caut_on && (!caut_flash || phase_on(now, PANEL_FLASH_WARN_HALF_MS)))
        L |= LED_BIT(LED_MCAUT);

    /* SOS ACTIVE */
    if (p->sos_armed) {
        if (p->sos_sent_seen)
            L |= LED_BIT(LED_SOSACT);
        else if (!p->br.alive ? phase_on(now, PANEL_FLASH_4HZ_HALF_MS) : phase_on(now, PANEL_FLASH_1HZ_HALF_MS))
            L |= LED_BIT(LED_SOSACT);
    }

    /* the bridge's indicators, held at their last state when the link drops (s.9) */
    if (p->br.bearers_up & BEARER_SAT)
        L |= LED_BIT(LED_SAT);
    if (p->br.bearers_up & BEARER_MESH)
        L |= LED_BIT(LED_MESH);
    if (p->br.bearers_up & BEARER_LTE)
        L |= LED_BIT(LED_LTE);
    if (p->br.bearers_up & BEARER_GPS)
        L |= LED_BIT(LED_GPS);
    if (p->br.msg_unread && !(p->msg_acked && p->msg_acked_seq == p->br.msg_seq))
        L |= LED_BIT(LED_MSG);

    /* SHORE and CHARGING from the charger's bits over the bus */
    if (in->charger_ok && in->charger_input_present)
        L |= LED_BIT(LED_SHORE);
    if (in->charger_ok && in->charger_charging)
        L |= LED_BIT(LED_CHG);

    /* the PI ring: a 0.5 Hz heartbeat while any slot's bridge runs */
    if (any_slot_alive(p) && phase_on(now, PANEL_FLASH_PIRING_HALF_MS))
        L |= LED_BIT(LED_PIRING);

    /* the battery bar for 5 s after a lamp test or a short TEST press; the lowest LED flashing below 10 % */
    if (within(now, p->batbar_until) && !within(now, p->lamptest_until) && p->br.soc_pct >= 0) {
        int soc = p->br.soc_pct;
        int n = (soc + 19) / 20;                             /* SESSION S-14: LED k lit above 20(k-1) % */
        if (n > 5)
            n = 5;
        for (int k = 0; k < n; k++)
            L |= LED_BIT(LED_BAT1 + k);
        if (soc < 10) {
            L &= ~LED_BIT(LED_BAT1);
            if (phase_on(now, PANEL_FLASH_BAT_HALF_MS))
                L |= LED_BIT(LED_BAT1);
        }
    }

    /* the lamp test: all seventeen controller-lit indicators for 3 s */
    if (within(now, p->lamptest_until))
        L = PANEL_LED_ALL;
    return L;
}

static bool sound_level(panel_t *p, ms_t now)
{
    ms_t t = now - p->sound_at;
    switch (p->sound) {
    case SND_CHIRP:
        if (t < 50)
            return true;
        break;
    case SND_DOUBLE_CHIRP:
        if (t < 200)
            return t < 50 || t >= 150;                       /* SESSION S-15: 50 on, 100 off, 50 on */
        break;
    case SND_ZER_COMPLETE:
        if (t < 3000)
            return true;
        break;
    default:
        break;
    }
    p->sound = SND_NONE;
    if (p->sound_muted)
        return false;
    if (p->zer.mode == ZM_INCOMPLETE) {                      /* three 200 ms pulses every 5 s */
        ms_t c = (now - p->zer.complete_at) % 5000u;
        return c < 1000u && (c / 200u) % 2u == 0u;
    }
    if (p->sos_armed && !p->sos_sent_seen)                   /* 1 s on, 1 s off until the first send */
        return phase_on(now - p->sos_closed_at, 1000u);
    return false;
}

/* ------------------------------------------------------------------------------------------------ e-paper (P s.9) */

static uint8_t page_select(panel_t *p, ms_t now)
{
    if (p->zer.mode == ZM_COMPLETE ||
        (p->zer_page_hold && !after(now, p->zer.complete_at + PANEL_EPD_MIN_INTERVAL_MS)))
        return PAGE_ZEROIZED;
    if (p->zer.mode == ZM_INCOMPLETE)
        return PAGE_ZEROIZE_INCOMPLETE;
    if (p->hot.state == HOT_H2)
        return PAGE_HOT_SHUTDOWN;
    if (p->hot.state == HOT_H1)
        return PAGE_HOT_STOP;
    if (p->test_qr_active)
        return PAGE_QR;
    if (p->sos_armed) {
        if (!p->br.alive)
            return PAGE_SOS_NO_HOST;
        if (p->sos_sent_seen)
            return PAGE_SOS_SENT;
        if (p->emcon_on)
            return PAGE_SOS_QUEUED_EMCON;
        if (p->margin_hold)
            return PAGE_SOS_QUEUED_MARGIN;
        if (p->br.sos == SOS_BR_QUEUED_NO_BEARER)
            return PAGE_SOS_QUEUED_NO_BEARER;
        return PAGE_SOS_ARMED;
    }
    if (p->zer.aborted_shown && !after(now, p->zer.complete_at + PANEL_EPD_MIN_INTERVAL_MS))
        return PAGE_ZEROIZE_ABORTED;
    if (p->sos_cancelled && !after(now, p->sos_cancel_at + PANEL_EPD_MIN_INTERVAL_MS))
        return PAGE_SOS_CANCELLED;
    if (p->emcon_on)
        return PAGE_EMCON;                                   /* FW-C07, P s.9: show EMCON on the e-paper */
    if (p->margin_hold)
        return PAGE_MARGIN_HOLD;
    if (p->zer.se_absent)
        return PAGE_SE_ABSENT;
    return PAGE_IDLE;
}

/* A change of page refreshes at once (SESSION S-16, finding F-08); the idle page's content at most once a minute;
 * a full refresh once an hour and after ZEROIZE. Power on, BUSY polled before every command, power off after. */
enum { EPD_IDLE = 0, EPD_POWER_ON, EPD_SEND, EPD_WAIT_DONE };
#define EPD_BUSY_TIMEOUT_MS 30000u

static void epd_step(panel_t *p, ms_t now, const panel_in_t *in, panel_out_t *out)
{
    p->page_want = page_select(p, now);
    switch (p->epd_step) {
    case EPD_IDLE: {
        bool change = p->page_want != p->page_shown;
        bool idle_due = p->page_want == PAGE_IDLE && after(now, p->epd_last_refresh + PANEL_EPD_MIN_INTERVAL_MS);
        if (change || idle_due || !p->epd_refreshes) {
            if (after(now, p->epd_last_full + PANEL_EPD_FULL_INTERVAL_MS) || !p->epd_refreshes)
                p->epd_full_due = true;
            p->epd_step = EPD_POWER_ON;
            p->epd_step_at = now;
        }
        break;
    }
    case EPD_POWER_ON:
        if (!in->epd_busy) {
            p->epd_step = EPD_SEND;
            p->epd_step_at = now;
        } else if (after(now, p->epd_step_at + EPD_BUSY_TIMEOUT_MS)) {
            p->epd_step = EPD_IDLE;
        }
        break;
    case EPD_SEND:
        if (!in->epd_busy) {                                  /* BUSY polled before the command */
            uint8_t page = p->page_want;
            bool full = p->epd_full_due;
            if (p->ops->epd.send)
                p->ops->epd.send(p->ops->epd.ctx, page, full);
            p->page_shown = page;
            p->epd_refreshes++;
            p->epd_last_refresh = now;
            if (full) {
                p->epd_last_full = now;
                p->epd_full_due = false;
            }
            p->epd_step = EPD_WAIT_DONE;
            p->epd_step_at = now;
        }
        break;
    case EPD_WAIT_DONE:
        if (!in->epd_busy && after(now, p->epd_step_at + 1u))
            p->epd_step = EPD_IDLE;                           /* power down between refreshes */
        else if (after(now, p->epd_step_at + EPD_BUSY_TIMEOUT_MS))
            p->epd_step = EPD_IDLE;
        break;
    default:
        p->epd_step = EPD_IDLE;
    }
    out->epd_power = p->epd_step != EPD_IDLE;
}

/* ------------------------------------------------------------------------------------------------ the tick */

static void sample_switches(panel_t *p, ms_t now, const panel_in_t *in)
{
    if (!p->switches_ready) {
        p->switches_ready = true;
        panel_deb_init(&p->sw_test, in->test_sw, now);
        panel_deb_init(&p->sw_sos, in->sos_sw, now);
        panel_deb_init(&p->sw_emcon, in->emcon_rd, now);
        panel_deb_init(&p->sw_pi, in->pi_button, now);
        panel_deb_init(&p->sw_day, p->light_day_n, now);
        panel_deb_init(&p->sw_night, p->light_night_n, now);
        p->rb_ien = false;
        return;
    }
    panel_deb_update(&p->sw_test, in->test_sw, now);
    panel_deb_update(&p->sw_sos, in->sos_sw, now);
    panel_deb_update(&p->sw_zer, in->zeroize_sw, now);
    panel_deb_update(&p->sw_emcon, in->emcon_rd, now);
    panel_deb_update(&p->sw_pi, in->pi_button, now);
    if (panel_deb_update(&p->sw_day, p->light_day_n, now))
        ev_push(p, EV_LIGHT_DAY, p->sw_day.stable, now);
    if (panel_deb_update(&p->sw_night, p->light_night_n, now))
        ev_push(p, EV_LIGHT_NIGHT, p->sw_night.stable, now);
}

static void boot_step(panel_t *p, ms_t now)
{
    switch (p->boot) {
    case BOOT_ZEROIZE:
        /* FW-C01 step 3: the level read, stable 30 ms; the boot table of ZER s.3.5 */
        if (after(now, p->sw_zer.since + PANEL_DEBOUNCE_MS) && p->sw_zer.raw == p->sw_zer.stable) {
            bool closed = !p->sw_zer.stable;
            bool may = true;
            uint8_t r = panel_zer_boot(p, closed, &may);
            if (r == ZER_DONE) {
                p->zer.mode = closed ? ZM_COMPLETE : ZM_ARMED_IDLE;
                p->zer.complete_at = now;
                p->zer_page_hold = true;
                p->epd_full_due = true;
                if (closed)
                    sound_start(p, SND_ZER_COMPLETE, now);
            } else if (r == ZER_INCOMPLETE) {
                p->zer.mode = ZM_INCOMPLETE;
                p->zer.complete_at = now;
            } else {
                p->zer.mode = closed ? ZM_ARMING : ZM_ARMED_IDLE;
            }
            if (!may)
                cut_all_slots(p, now);
            p->boot = BOOT_EXPANDERS;
            p->boot_phase_at = now;
        }
        break;
    case BOOT_EXPANDERS:
        panel_exp_boot(p);                                   /* FW-C01 step 4, FW-A08 */
        p->boot = BOOT_CHARGER;
        p->boot_phase_at = now;
        break;
    case BOOT_CHARGER:
        /* FW-C01 step 5: the charger (FW-A01 to A03, A16 to A18): OWED, not in this firmware (README section 4) */
        p->boot = BOOT_HOTR1;
        p->boot_phase_at = now;
        break;
    case BOOT_HOTR1: {
        /* FW-C14: HOT-R1 read before any slot is raised */
        uint8_t line = panel_hot_classify(&p->hot, now);
        if (line == HOT_LINE_UNKNOWN && !after(now, p->boot_phase_at + PANEL_HOTR1_HELD_MS + 500u))
            break;
        if (line == HOT_LINE_UNKNOWN)
            p->hot.line = HOT_LINE_HELD_HIGH;                /* nothing read: the detector lost (SESSION S-17) */
        p->hot_block_slots = p->hot.line == HOT_LINE_5HZ;
        if (p->hot_block_slots)
            break;                                           /* raise no slot until it is back at 1 Hz */
        p->boot = BOOT_RUN;
        p->boot_phase_at = now;
        break;
    }
    default:
        break;
    }
}

void panel_tick(panel_t *p, ms_t now, const panel_in_t *in, panel_out_t *out)
{
    memset(out, 0, sizeof *out);

    /* the bridge's view: kept at its last content while the link is down (s.9) */
    if (in->br.alive)
        p->br = in->br;
    else
        p->br.alive = false;

    if (p->exp_init_done && ((!in->exp_int && after(now, p->exp_polled_at + PANEL_EXP_INT_MIN_MS)) ||
                             after(now, p->exp_polled_at + PANEL_EXP_POLL_MS) ||
                             (p->boot == BOOT_HOTR1 && after(now, p->exp_polled_at + 50u))))
        panel_exp_service(p, now);

    sample_switches(p, now, in);
    if (p->boot != BOOT_RUN)
        boot_step(p, now);

    /* lighting */
    bool fault;
    p->light = panel_light_mode(p->sw_day.stable, p->sw_night.stable, p->br.nvg, &fault);
    bool rail = in->rail_mv > HAL_RAIL_PRESENT_MV;
    p->light_fault = fault || (rail == (p->light == LIGHT_BLACKOUT));
    if (p->exp_c_ok == false && p->exp_init_done)
        p->light_fault = true;

    slots_heartbeats(p, now, in);
    emcon_step(p, now);
    if (p->boot == BOOT_RUN) {
        controls_test(p, now);
        controls_sos(p, now);
        controls_zeroize(p, now);
        controls_pi(p, now);
    }
    if (p->boot >= BOOT_HOTR1)
        hot_step(p, now, in);
    if (p->boot >= BOOT_EXPANDERS || p->kill)
        shutdown_step(p, now, in);                   /* a MAIN tap counts from the end of the ZEROIZE read */
    margin_step(p, now);
    power_controls_step(p, now);
    p->reduced_mode_flag = p->pack_fallback || p->c1_reduced || p->hot.line == HOT_LINE_HELD_HIGH;
    slots_policy(p, now);
    display_select(p);
    shore_step(p, now, out);

    /* outputs: the lines this controller drives (FW-C01: PI_KILL low until a kill; PI_SHDN_REQ only pulled low) */
    out->pi_kill = p->kill;
    out->pi_shdn_assert = p->shdn == SHDN_PULSE || p->hot_pulse;
    if (out->pi_shdn_assert)
        p->own_pull_until = now + PANEL_OWN_PULL_GUARD_MS;
    for (unsigned i = 0; i < 3; i++)
        out->slot_en[i] = p->slot[i].en;
    out->hdmi_sel1 = p->hdmi_slot == 1;
    out->hdmi_sel2 = p->hdmi_slot == 2;
    out->shore_inhibit = p->shore_inhibit;

    uint32_t leds = indicators(p, now, in);
    out->leds = panel_light_filter(p->light, leds);
    bool tx_lamp = in->tr_aprs || (out->leds & LED_BIT(LED_TXTEST));
    out->pwm_permille = panel_light_duty(p->light, tx_lamp);
    out->sounder = p->light != LIGHT_BLACKOUT && sound_level(p, now);
    if (p->light == LIGHT_BLACKOUT)
        out->sounder = false;
    out->backlight_off = p->light == LIGHT_BLACKOUT;
    out->backlight_pct = p->light == LIGHT_DAY ? 100 : p->light == LIGHT_NIGHT ? 20 : p->light == LIGHT_NVG ? 5 : 0;
    out->led_stat = p->boot != BOOT_RUN || phase_on(now - p->t0, 500u);
    if (p->exp_init_done && (!p->led_failed || after(now, p->led_fail_at + PANEL_LED_RETRY_MS))) {
        p->led_failed = panel_exp_write_leds(p, out->leds) != 0;
        if (p->led_failed)
            p->led_fail_at = now;
    }
    epd_step(p, now, in, out);

    /* forced-off loads and charge holds */
    uint16_t off = 0;
    if (p->hot.state != HOT_NONE)
        off |= (1u << LOAD_MONITOR) | (1u << LOAD_HEATER) | (1u << LOAD_BOARD_D) | (1u << LOAD_POE) |
               (1u << LOAD_USBC) | (1u << LOAD_WALL_VBUS) | (1u << LOAD_PA) | (1u << LOAD_HF);
    if (p->margin_hold)
        off |= (1u << LOAD_BOARD_D) | (1u << LOAD_PA) | (1u << LOAD_ROCKBLOCK) | (1u << LOAD_LORA) |
               (1u << LOAD_ZIGBEE) | (1u << LOAD_GEIGER);
    if (p->pack_fallback || p->hot.line == HOT_LINE_HELD_HIGH)
        off |= (1u << LOAD_POE) | (1u << LOAD_USBC);
    out->loads_off = off;
    out->charge_hold_hot = p->hot.state != HOT_NONE;
    out->charge_hold_margin = p->margin_hold;
    out->rb_ien_request = p->rb_ien && !(off & (1u << LOAD_ROCKBLOCK));
    out->reduced_mode = p->reduced_mode_flag;
    out->loads_on = (uint16_t)(p->br.loads_wanted & ~off);
    if (p->exp_init_done && p->boot >= BOOT_HOTR1)
        panel_exp_write_kit(p, out->loads_on, out->rb_ien_request);
}
