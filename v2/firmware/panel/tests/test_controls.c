/* test_controls.c: TEST/ACK, SOS, the PI button, EMCON and the hardware lines. */
#include "fixture.h"

void t_test_short_press_ack(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.br.alive = true;
    x->in.br.red = RED_PACK_UV;
    x->in.br.soc_pct = 90;
    fx_run(x, 50);
    x->in.test_sw = false;
    fx_run(x, 1500);                              /* released before 2 s */
    x->in.test_sw = true;
    fx_run(x, 40);
    CHECK(x->p.red_acked & 8u);                   /* the red condition acknowledged */
    CHECK(x->p.sound_muted);
    CHECK(((x->out.leds >> LED_BAT1) & 0x1Fu) == 0x1F);
    CHECK(x->p.lamptest_until == 0);              /* no lamp test */
}

void t_test_hold_lamp_test(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.br.alive = true;
    x->in.br.soc_pct = 30;
    x->in.test_sw = false;
    fx_run(x, 1990);
    CHECK(x->out.leds != PANEL_LED_ALL);
    fx_run(x, 60);                                /* 2 s held (30 ms debounce) */
    CHECK(x->out.leds == PANEL_LED_ALL);          /* all seventeen */
    CHECK(x->p.sound == SND_DOUBLE_CHIRP);
    x->in.test_sw = true;
    fx_run(x, 2900);
    CHECK(x->out.leds == PANEL_LED_ALL);          /* for 3 s */
    fx_run(x, 200);
    CHECK(x->out.leds != PANEL_LED_ALL);
    CHECK(((x->out.leds >> LED_BAT1) & 0x1Fu) == 0x03);   /* the battery bar after */
    CHECK(!(x->p.red_acked));                     /* a hold is not an acknowledgement */
}

void t_test_qr_while_held(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.br.alive = true;
    /* no request: a 5 s hold shows no QR */
    x->in.test_sw = false;
    fx_run(x, 6000);
    CHECK(!x->p.test_qr_active);
    x->in.test_sw = true;
    fx_run(x, 4000);
    /* a request, then a 5 s hold: the QR while held, and gone at release */
    x->in.br.qr_request_seq = 1;
    fx_run(x, 10000);
    x->in.test_sw = false;
    fx_run(x, 5100);
    CHECK(x->p.test_qr_active);
    fx_run(x, 1000);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_QR);
    x->in.test_sw = true;
    fx_run(x, 1000);
    CHECK(!x->p.test_qr_active);
    CHECK(x->epd_pages[x->n_epd - 1] != PAGE_QR);  /* the QR is taken off the glass at once */
    /* a request older than 60 s does not count */
    x->in.br.qr_request_seq = 2;
    fx_run(x, 61000);
    x->in.test_sw = false;
    fx_run(x, 6000);
    CHECK(!x->p.test_qr_active);
    x->in.test_sw = true;
    fx_run(x, 100);
}

void t_sos_hold_2s(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.sos_sw = false;
    fx_run(x, 1900);
    CHECK(!x->p.sos_armed);
    x->in.sos_sw = true;                          /* back before 2 s: nothing */
    fx_run(x, 100);
    CHECK(!x->p.sos_armed && !x->p.sos_cancelled);
    x->in.sos_sw = false;
    fx_run(x, 2040);
    CHECK(x->p.sos_armed);                        /* closed 2 s = SOS mode */
    x->in.sos_sw = true;
    fx_run(x, 40);
    CHECK(!x->p.sos_armed && x->p.sos_cancelled); /* flipping back cancels */
    fx_run(x, 500);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_SOS_CANCELLED);
    CHECK(!(x->out.leds & LED_BIT(LED_SOSACT)));
}

static unsigned count_on(fx_t *x, unsigned led, unsigned ms)
{
    unsigned on = 0, flips = 0;
    bool last = (x->out.leds >> led) & 1u;
    for (unsigned i = 0; i < ms; i++) {
        fx_run(x, 1);
        bool l = (x->out.leds >> led) & 1u;
        on += l;
        flips += l != last;
        last = l;
    }
    return on * 1000u + flips;
}

void t_sos_indications(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.br.alive = true;
    x->in.sos_sw = false;
    fx_run(x, 2100);
    /* armed: D4 at 1 Hz, MASTER WARN flashing, the sounder's pattern, "SOS ARMED" */
    unsigned r = count_on(x, LED_SOSACT, 2000);
    CHECK(r % 1000u >= 3 && r % 1000u <= 5);
    CHECK(x->out.leds & LED_BIT(LED_MWARN) || count_on(x, LED_MWARN, 300) % 1000u > 0);
    fx_run(x, 600);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_SOS_ARMED);
    /* queued for want of a bearer */
    x->in.br.sos = SOS_BR_QUEUED_NO_BEARER;
    fx_run(x, 600);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_SOS_QUEUED_NO_BEARER);
    /* sent: D4 steady, the pattern ends, MASTER WARN until acknowledged */
    x->in.br.sos = SOS_BR_SENT;
    fx_run(x, 600);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_SOS_SENT);
    r = count_on(x, LED_SOSACT, 2000);
    CHECK(r / 1000u == 2000u);
    unsigned snd = 0;
    for (int i = 0; i < 2000; i++) {
        fx_run(x, 1);
        snd += x->out.sounder;
    }
    CHECK(snd == 0);
    /* no host: D4 at 4 Hz and "SOS NOT SENT: NO HOST" */
    fx_t G, *y = &G;
    fx_boot(y);
    y->in.sos_sw = false;
    fx_run(y, 2100);
    r = count_on(y, LED_SOSACT, 2000);
    CHECK(r % 1000u >= 14 && r % 1000u <= 17);
    fx_run(y, 600);
    CHECK(y->epd_pages[y->n_epd - 1] == PAGE_SOS_NO_HOST);
}

void t_sos_emcon_queue(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.br.alive = true;
    x->in.emcon_rd = false;                       /* EMCON asserted */
    fx_run(x, 100);
    x->in.sos_sw = false;
    fx_run(x, 2700);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_SOS_QUEUED_EMCON);
    unsigned r = count_on(x, LED_SOSACT, 2000);
    CHECK(r % 1000u >= 3);                        /* D4 keeps flashing */
    x->in.emcon_rd = true;                        /* released: the bridge sends */
    x->in.br.sos = SOS_BR_SENT;
    fx_run(x, 700);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_SOS_SENT);
}

void t_pi_button_logic(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.pi_button = true;
    fx_run(x, 500);
    x->in.pi_button = false;                      /* a short press: the clean shutdown */
    fx_run(x, 40);
    CHECK(x->p.shdn == SHDN_PULSE && x->out.pi_shdn_assert);
    CHECK(!x->out.pi_kill);
    fx_t G, *y = &G;
    fx_boot(y);
    y->in.pi_button = true;
    fx_run(y, 8100);                              /* held 8 s = PI_KILL */
    CHECK(y->out.pi_kill);
    CHECK(HAL_PI_BUTTON_WIRED == 0);              /* finding F-01: no pin carries it on the drawn board */
}

void t_emcon_edges(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    panel_ev_t e;
    while (panel_ev_pop(&x->p, &e)) {
    }
    x->in.emcon_rd = false;
    fx_run(x, 50);
    bool seen = false;
    while (panel_ev_pop(&x->p, &e))
        seen |= e.type == EV_EMCON && e.value == 1;
    CHECK(seen);                                  /* every EMCON edge is reported for the software holds */
    CHECK(x->out.leds & LED_BIT(LED_MCAUT));      /* MASTER CAUT steady */
    unsigned on = 0;
    for (int i = 0; i < 1000; i++) {
        fx_run(x, 1);
        on += (x->out.leds >> LED_MCAUT) & 1u;
    }
    CHECK(on == 1000);
    /* the RockBLOCK request: low on EMCON, raised after a release only once RB_STATUS reads low */
    CHECK(!x->out.rb_ien_request);
    x->regs[HAL_I2C_B_U7][0] |= (uint8_t)(1u << HAL_EXP_B_RB_STATUS_BIT);
    x->in.emcon_rd = true;
    fx_run(x, 1200);
    CHECK(!x->out.rb_ien_request);
    x->regs[HAL_I2C_B_U7][0] &= (uint8_t)~(1u << HAL_EXP_B_RB_STATUS_BIT);
    fx_run(x, 1200);
    CHECK(x->out.rb_ien_request);
}

void t_never_drives_hardware_lines(void)
{
    /* the outputs carry no field for TX_INHIBIT_n, EMCON_HW or ZEROIZE_HW (P s.6): the core cannot drive them, and
     * PI_SHDN_REQ is only ever pulled low (an output enable with the value 0, FW-A10) */
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.pi_button = true;
    fx_run(x, 300);
    x->in.pi_button = false;
    unsigned asserted = 0;
    for (int i = 0; i < 400; i++) {
        fx_run(x, 1);
        asserted += x->out.pi_shdn_assert;
    }
    CHECK(asserted >= 199 && asserted <= 201);    /* at least 200 ms, then released */
    CHECK(sizeof(panel_out_t) > 0);
    /* the host HAL refuses an output on GPIO21 (EMCON_RD_R) and a high drive on PI_SHDN_REQ */
    extern int hal_host_refused;
    hal_gpio_put(HAL_GPIO_EMCON_RD_R, false);
    hal_gpio_put(HAL_GPIO_PI_SHDN_REQ, true);
    CHECK(hal_host_refused == 2);
}
