/* test_io.c: debounce, lighting, the LED drive rule, indicators, the sounder and the e-paper model. */
#include "fixture.h"

void t_debounce_30ms(void)
{
    panel_deb_t d;
    panel_deb_init(&d, true, 0);
    CHECK(!panel_deb_update(&d, false, 1));
    CHECK(!panel_deb_update(&d, true, 10));      /* a bounce restarts the 30 ms */
    CHECK(!panel_deb_update(&d, false, 15));
    CHECK(!panel_deb_update(&d, false, 44));     /* 29 ms */
    CHECK(d.stable);
    CHECK(panel_deb_update(&d, false, 45));      /* 30 ms */
    CHECK(!d.stable && d.fell);
}

void t_lighting_modes(void)
{
    bool fault;
    CHECK(panel_light_mode(false, true, false, &fault) == LIGHT_DAY && !fault);
    CHECK(panel_light_mode(true, false, false, &fault) == LIGHT_NIGHT);
    CHECK(panel_light_mode(true, false, true, &fault) == LIGHT_NVG);
    CHECK(panel_light_mode(true, true, false, &fault) == LIGHT_BLACKOUT);
    CHECK(panel_light_duty(LIGHT_DAY) == 1000);
    CHECK(panel_light_duty(LIGHT_NIGHT) == 150);
    CHECK(panel_light_duty(LIGHT_NVG) == 20);
    CHECK(panel_light_duty(LIGHT_BLACKOUT) == 0);
    /* NVG: red and amber indicators only */
    uint32_t f = panel_light_filter(LIGHT_NVG, PANEL_LED_ALL);
    CHECK(f & LED_BIT(LED_MWARN));
    CHECK(f & LED_BIT(LED_MCAUT));
    CHECK(f & LED_BIT(LED_SOSACT));
    CHECK(f & LED_BIT(LED_BAT1));
    CHECK(f & LED_BIT(LED_PIRING));
    CHECK(!(f & LED_BIT(LED_SAT)) && !(f & LED_BIT(LED_GPS)) && !(f & LED_BIT(LED_MSG)) && !(f & LED_BIT(LED_CHG)));
    CHECK(panel_light_filter(LIGHT_BLACKOUT, PANEL_LED_ALL) == 0);
    /* in the running core: BLACKOUT darkens every LED and the sounder, backlight off */
    fx_t F, *x = &F;
    fx_boot(x);
    x->regs[HAL_I2C_C_U1][1] |= 3u;               /* both LIGHTING inputs high */
    x->in.rail_mv = 0;
    x->in.br.alive = true;
    x->in.br.bearers_up = BEARER_SAT;
    fx_run(x, 1500);
    CHECK(x->p.light == LIGHT_BLACKOUT);
    CHECK(x->out.leds == 0 && x->out.pwm_permille == 0 && !x->out.sounder && x->out.backlight_off);
    CHECK(x->out.backlight_pct == 0);
    x->regs[HAL_I2C_C_U1][1] &= (uint8_t)~2u;     /* NIGHT */
    x->in.rail_mv = 2500;
    fx_run(x, 1500);
    CHECK(x->p.light == LIGHT_NIGHT && x->out.pwm_permille == 150 && x->out.backlight_pct == 20);
    x->in.br.nvg = true;
    fx_run(x, 100);
    CHECK(x->p.light == LIGHT_NVG && x->out.pwm_permille == 20 && x->out.backlight_pct == 5);
    CHECK(!(x->out.leds & LED_BIT(LED_SAT)));
}

void t_tx_lamp_follows_duty(void)
{
    /* F-05 (decided 3 October 2026): no floor; the TX lamp follows the one dimmer, keyed or not, dark in BLACKOUT */
    fx_t F, *x = &F;
    fx_boot(x);
    x->regs[HAL_I2C_C_U1][1] = (uint8_t)~(1u << HAL_EXP_C_LIGHT_NIGHT_N_BIT);
    x->in.br.alive = true;
    x->in.br.nvg = true;
    x->in.br.red = RED_PACK_UV;                   /* a red LED lit beside the keyed TX lamp */
    fx_run(x, 1500);
    CHECK(x->out.pwm_permille == 20);
    x->in.tr_aprs = true;                         /* D8 keyed: the TX lamp lit in hardware */
    for (int i = 0; i < 2000; i++) {
        fx_run(x, 1);
        CHECK(x->out.pwm_permille == 20);         /* NVG's 2 % holds through the key-down */
    }
    x->in.br.nvg = false;
    fx_run(x, 10);
    CHECK(x->out.pwm_permille == 150);
    x->regs[HAL_I2C_C_U1][1] = (uint8_t)~(1u << HAL_EXP_C_LIGHT_DAY_N_BIT);
    fx_run(x, 1200);
    CHECK(x->out.pwm_permille == 1000);
    x->regs[HAL_I2C_C_U1][1] |= 3u;               /* BLACKOUT, still keyed */
    x->in.rail_mv = 0;
    fx_run(x, 1200);
    CHECK(x->out.pwm_permille == 0);
}

void t_rail_sense(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.rail_mv = 1300;                         /* above 1.25 V: present */
    fx_run(x, 10);
    CHECK(!x->p.light_fault);
    x->in.rail_mv = 1200;                         /* DAY with the rail absent: a disagreement */
    fx_run(x, 10);
    CHECK(x->p.light_fault);
}

void t_led_drive_rule(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.br.alive = true;
    x->in.br.bearers_up = BEARER_SAT | BEARER_GPS;
    fx_run(x, 50);
    /* an LED is ON when its bit is an OUTPUT driving 0 and OFF when an INPUT; a 1 is never driven */
    CHECK(x->regs[HAL_I2C_C_U1][2] == 0 && x->regs[HAL_I2C_C_U2][2] == 0);
    CHECK(!(x->regs[HAL_I2C_C_U1][6] & (1u << HAL_EXP_C_SAT_BIT)));
    CHECK(!(x->regs[HAL_I2C_C_U1][6] & (1u << HAL_EXP_C_GPS_BIT)));
    CHECK(x->regs[HAL_I2C_C_U1][6] & (1u << HAL_EXP_C_MESH_BIT));
    CHECK(x->regs[HAL_I2C_C_U1][7] == 0xFF);      /* port 1 stays inputs */
    for (unsigned i = 0; i < x->n_wr; i++)
        if ((x->wr[i].addr == HAL_I2C_C_U1 || x->wr[i].addr == HAL_I2C_C_U2) && (x->wr[i].reg == 2 || x->wr[i].reg == 3))
            CHECK(x->wr[i].val == 0);
    /* every configuration write of board C follows an output write of 0 */
    for (unsigned i = 0; i < x->n_wr; i++) {
        if ((x->wr[i].addr == HAL_I2C_C_U1 || x->wr[i].addr == HAL_I2C_C_U2) && x->wr[i].reg == PCA9555_CFG0) {
            int o = -1;
            for (int j = (int)i - 1; j >= 0; j--)
                if (x->wr[j].addr == x->wr[i].addr && x->wr[j].reg == PCA9555_OUT0) { o = j; break; }
            CHECK(o >= 0);
        }
    }
}

void t_led_boot_one_by_one(void)
{
    fx_t F, *x = &F;
    fx_new(x);
    x->in.br.alive = true;
    x->in.br.bearers_up = BEARER_SAT | BEARER_MESH | BEARER_LTE;
    fx_init(x, false, NULL);
    for (int i = 0; i < 6000 && !x->p.leds_ramped; i++) {
        fx_tick(x);
        x->now++;
    }
    /* the first LED write after boot enables the lit outputs one by one: the number of zero bits in successive U1
     * configuration writes grows by one */
    int prev = -1;
    unsigned grows = 0;
    for (unsigned i = 0; i < x->n_wr; i++) {
        if (x->wr[i].addr == HAL_I2C_C_U1 && x->wr[i].reg == PCA9555_CFG0) {
            int zeros = __builtin_popcount((uint8_t)~x->wr[i].val);
            if (prev >= 0 && zeros == prev + 1)
                grows++;
            prev = zeros;
        }
    }
    CHECK(grows >= 2);
}

void t_warn_caut_semantics(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.br.alive = true;
    x->in.br.amber = AMBER_BEARER_LOST;
    x->in.br.red = RED_PACK_UV;
    unsigned on = 0, n = 0;
    for (int i = 0; i < 1000; i++) {
        fx_run(x, 1);
        on += (x->out.leds >> LED_MWARN) & 1u;
        n++;
    }
    CHECK(on > 300 && on < 700);                   /* flashing */
    /* a short TEST press acknowledges: flashers to steady */
    x->in.test_sw = false;
    fx_run(x, 100);
    x->in.test_sw = true;
    fx_run(x, 100);
    on = 0;
    for (int i = 0; i < 1000; i++) {
        fx_run(x, 1);
        on += (x->out.leds >> LED_MWARN) & 1u;
        on += (x->out.leds >> LED_MCAUT) & 1u;
    }
    CHECK(on == 2000);
    /* a new amber condition flashes again */
    x->in.br.amber |= AMBER_DISK_FULL;
    on = 0;
    for (int i = 0; i < 1000; i++) {
        fx_run(x, 1);
        on += (x->out.leds >> LED_MCAUT) & 1u;
    }
    CHECK(on < 800);
    /* the condition gone: dark */
    x->in.br.amber = 0;
    x->in.br.red = 0;
    fx_run(x, 10);
    CHECK(!(x->out.leds & LED_BIT(LED_MCAUT)) && !(x->out.leds & LED_BIT(LED_MWARN)));
}

void t_bridge_hold_on_link_drop(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.br.alive = true;
    x->in.br.bearers_up = BEARER_MESH;
    x->in.br.msg_unread = true;
    x->in.br.msg_seq = 7;
    fx_run(x, 20);
    CHECK(x->out.leds & LED_BIT(LED_MESH));
    CHECK(x->out.leds & LED_BIT(LED_MSG));
    memset(&x->in.br, 0, sizeof x->in.br);        /* the USB link drops */
    fx_run(x, 2000);
    CHECK(x->out.leds & LED_BIT(LED_MESH));        /* the last state is held */
    CHECK(x->out.leds & LED_BIT(LED_MSG));
}

void t_msg_cleared_by_ack(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.br.alive = true;
    x->in.br.msg_unread = true;
    x->in.br.msg_seq = 3;
    fx_run(x, 20);
    CHECK(x->out.leds & LED_BIT(LED_MSG));
    x->in.test_sw = false;
    fx_run(x, 100);
    x->in.test_sw = true;
    fx_run(x, 100);
    CHECK(!(x->out.leds & LED_BIT(LED_MSG)));
    x->in.br.msg_seq = 4;                          /* a new message lights it again */
    fx_run(x, 10);
    CHECK(x->out.leds & LED_BIT(LED_MSG));
}

void t_battery_bar(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.br.alive = true;
    x->in.br.soc_pct = 55;
    fx_run(x, 20);
    CHECK(!(x->out.leds & LED_BIT(LED_BAT1)));     /* the bar shows only after a press */
    x->in.test_sw = false;
    fx_run(x, 100);
    x->in.test_sw = true;
    fx_run(x, 100);
    uint32_t bar = (x->out.leds >> LED_BAT1) & 0x1Fu;
    CHECK(bar == 0x07);                            /* 55 %: three LEDs */
    fx_run(x, 5000);
    CHECK(((x->out.leds >> LED_BAT1) & 0x1Fu) == 0);  /* 5 s */
    x->in.br.soc_pct = 5;                          /* below 10 %: the lowest LED flashes */
    x->in.test_sw = false;
    fx_run(x, 100);
    x->in.test_sw = true;
    unsigned on = 0;
    for (int i = 0; i < 2000; i++) {
        fx_run(x, 1);
        on += (x->out.leds >> LED_BAT1) & 1u;
    }
    CHECK(on > 600 && on < 1400);
}

void t_pi_ring_heartbeat(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    static const bool one[3] = { true, false, false };
    fx_run_hb(x, 3000, one);
    unsigned on = 0, flips = 0;
    bool last = false;
    for (int i = 0; i < 4000; i++) {
        fx_run_hb(x, 1, one);
        bool l = (x->out.leds >> LED_PIRING) & 1u;
        on += l;
        flips += l != last;
        last = l;
    }
    CHECK(on > 1500 && on < 2500 && flips >= 3 && flips <= 5);   /* 0.5 Hz */
    static const bool none[3] = { false, false, false };
    fx_run_hb(x, 4000, none);
    CHECK(!(x->out.leds & LED_BIT(LED_PIRING)));
}

void t_sounder_patterns(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    /* ACK chirp 50 ms */
    x->in.test_sw = false;
    fx_run(x, 100);
    x->in.test_sw = true;
    unsigned on = 0;
    for (int i = 0; i < 400; i++) {
        fx_run(x, 1);
        on += x->out.sounder;
    }
    CHECK(on >= 48 && on <= 52);
    /* the lamp test's double chirp: 50 ms on, 100 ms off, 50 ms on (F-06, S-15) */
    x->in.test_sw = false;
    unsigned seg[8] = { 0 }, nseg = 0;
    bool last = false;
    unsigned run = 0;
    for (int i = 0; i < 2600; i++) {
        fx_run(x, 1);
        if (x->out.sounder != last && run && nseg < 8) {
            seg[nseg++] = run;
            run = 0;
        }
        if (x->out.sounder || nseg)
            run++;
        last = x->out.sounder;
    }
    x->in.test_sw = true;
    fx_run(x, 3500);
    CHECK(nseg >= 3 && seg[0] == 50 && seg[1] == 100 && seg[2] == 50);
    /* SOS pattern 1 s on 1 s off while armed and unsent */
    x->in.sos_sw = false;
    fx_run(x, 2100);
    on = 0;
    for (int i = 0; i < 4000; i++) {
        fx_run(x, 1);
        on += x->out.sounder;
    }
    CHECK(on > 1900 && on < 2100);
    /* muted in BLACKOUT */
    x->regs[HAL_I2C_C_U1][1] |= 3u;
    x->in.rail_mv = 0;
    fx_run(x, 1200);
    on = 0;
    for (int i = 0; i < 3000; i++) {
        fx_run(x, 1);
        on += x->out.sounder;
    }
    CHECK(on == 0);
}

static unsigned epd_count(const fx_t *x, uint8_t page)
{
    unsigned n = 0;
    for (unsigned i = 0; i < x->n_epd; i++)
        n += x->epd_pages[i] == page;
    return n;
}

void t_epd_refresh_rules(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    fx_run(x, 1000);
    CHECK(x->n_epd >= 1 && x->epd_full[0]);        /* the first refresh is full */
    unsigned before = x->n_epd;
    fx_run(x, 30000);
    CHECK(x->n_epd == before);                     /* the idle content at most once a minute */
    fx_run(x, 31000);
    CHECK(x->n_epd == before + 1);
    /* a change of page refreshes at once */
    x->in.sos_sw = false;
    fx_run(x, 2300);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_SOS_NO_HOST);
    /* the display is powered only around a refresh */
    fx_run(x, 500);
    CHECK(!x->out.epd_power);
    /* a full refresh once an hour */
    x->in.sos_sw = true;
    unsigned fulls = 0;
    for (int i = 0; i < 3700; i++)
        fx_run(x, 1000);
    for (unsigned i = 0; i < x->n_epd; i++)
        fulls += x->epd_full[i];
    CHECK(fulls >= 2);
    CHECK(epd_count(x, PAGE_SOS_CANCELLED) == 1);
}

void t_epd_busy_polled(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    fx_run(x, 1000);
    unsigned n = x->n_epd;
    x->busy_until = x->now + 5000;                  /* the display still busy */
    x->in.sos_sw = false;
    fx_run(x, 4000);
    CHECK(x->n_epd == n);                           /* no command while BUSY is high */
    fx_run(x, 1500);
    CHECK(x->n_epd == n + 1);
}
