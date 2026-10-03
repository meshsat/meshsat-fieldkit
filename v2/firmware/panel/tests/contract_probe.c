/*
 * contract_probe.c: measures, on the running core with the host fixture, the values the panel contract decides, and prints
 * them as key=value lines. v2/ecad/tools/tests/test_fw_panel.py reads the expected values from PANEL.md and
 * HW-FW-CONTRACT.md and compares, so a contract row the code contradicts fails there by name (record l5r2 round 3,
 * finding L5R3-F02). Host only; nothing here touches the tree.
 */
#include <stdio.h>

#include "fixture.h"

static void boot_light(fx_t *x, unsigned day_night_bits)
{
    fx_boot(x);
    x->regs[HAL_I2C_C_U1][1] = (uint8_t)((x->regs[HAL_I2C_C_U1][1] & ~3u) | day_night_bits);
}

/* F-05: the dimmer's duty with D8 keyed (the TX lamp lit), per LIGHTING position */
static void f05(void)
{
    static const struct { const char *name; unsigned bits; bool nvg; unsigned rail; } M[] = {
        { "DAY", 2u, false, 2500 }, { "NIGHT", 1u, false, 2500 }, { "NVG", 1u, true, 2500 }, { "BLACKOUT", 3u, false, 0 },
    };
    for (size_t i = 0; i < sizeof M / sizeof M[0]; i++) {
        fx_t F, *x = &F;
        boot_light(x, M[i].bits);
        x->in.br.alive = true;
        x->in.br.nvg = M[i].nvg;
        x->in.rail_mv = (uint16_t)M[i].rail;
        fx_run(x, 1500);
        unsigned idle = x->out.pwm_permille;
        x->in.tr_aprs = true;
        unsigned keyed_max = 0;
        for (int t = 0; t < 1000; t++) {
            fx_run(x, 1);
            if (x->out.pwm_permille > keyed_max)
                keyed_max = x->out.pwm_permille;
        }
        printf("f05_duty_%s_idle=%u\nf05_duty_%s_keyed=%u\n", M[i].name, idle, M[i].name, keyed_max);
    }
}

/* F-11 and F-04: board D's U16 boot writes, and every configuration write after an output write to the same expander */
static void f11_f04(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    fx_run(x, 3000);
    int o = fx_find_write(x, HAL_I2C_D_U16, PCA9555_OUT0, 0), c = fx_find_write(x, HAL_I2C_D_U16, PCA9555_CFG0, 0);
    printf("f11_d_u16_out0=%u\nf11_d_u16_cfg0=%u\nf11_d_u16_out_before_cfg=%d\n", o >= 0 ? x->wr[o].val : 999u,
           c >= 0 ? x->wr[c].val : 999u, o >= 0 && c >= 0 && o < c);
    /* each configuration write starts at CFG0 (the pair is written in one transaction): the write to the same expander
     * just before it must be an output register */
    int every = 1;
    for (unsigned i = 0; i < x->n_wr; i++) {
        if (x->wr[i].reg != PCA9555_CFG0)
            continue;
        int prev = -1;
        for (int j = (int)i - 1; j >= 0 && prev < 0; j--)
            if (x->wr[j].addr == x->wr[i].addr)
                prev = j;
        every &= prev >= 0 && (x->wr[prev].reg == PCA9555_OUT0 || x->wr[prev].reg == PCA9555_OUT1);
    }
    printf("f04_every_cfg_after_out=%d\n", every);
}

/* F-06: the lamp test's sound as on and off segments in milliseconds */
static void f06(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.test_sw = false;
    unsigned seg[6] = { 0 }, n = 0, run = 0;
    bool last = false;
    for (int i = 0; i < 2600; i++) {
        fx_run(x, 1);
        if (x->out.sounder != last && run && n < 6) {
            seg[n++] = run;
            run = 0;
        }
        if (x->out.sounder || n)
            run++;
        last = x->out.sounder;
    }
    printf("f06_double_chirp=%u,%u,%u\n", seg[0], seg[1], seg[2]);
}

/* F-07: which master indicator one and two lost modules raise */
static void f07(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    bool t[3] = { true, false, true }, u[3] = { true, false, false };
    fx_run_hb(x, 66000, t);
    printf("f07_one_lost_caut=%d\nf07_one_lost_warn=%d\n", (x->p.amb_active & 8u) != 0, (x->p.red_active & 32u) != 0);
    fx_run_hb(x, 3500, u);
    printf("f07_two_lost_warn=%d\n", (x->p.red_active & 32u) != 0);
}

/* F-08: the delay from a change of page to its refresh, and the idle page's interval */
static void f08(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    fx_run(x, 2000);
    unsigned n = x->n_epd;
    ms_t first = x->epd_at[n - 1];
    fx_run(x, 130000);
    ms_t idle = x->n_epd > n ? x->epd_at[n] - first : 0;
    x->in.sos_sw = false;
    fx_run(x, 2030);                                 /* debounce and the 2 s hold: the page changes */
    ms_t changed = x->now;
    unsigned m = x->n_epd;
    fx_run(x, 2000);
    printf("f08_idle_interval_ms=%u\nf08_page_change_delay_ms=%u\n", (unsigned)idle,
           x->n_epd > m ? (unsigned)(x->epd_at[m] - changed) : 99999u);
}

/* F-10: a 5 Hz line at start-up, back at 1 Hz after 5 s: the first slot rises how long after the start */
static void f10(void)
{
    fx_t F, *x = &F;
    fx_new(x);
    x->hot_sim = HOT_SIM_5HZ;
    fx_init(x, false, NULL);
    ms_t t0 = x->now;
    ms_t up = 0;
    while (x->now - t0 < 2400000u && !up) {
        if (x->now - t0 == 5000u)
            x->hot_sim = HOT_SIM_1HZ;
        fx_tick(x);
        if (x->out.slot_en[0] || x->out.slot_en[1] || x->out.slot_en[2])
            up = x->now - t0;
        x->now++;
    }
    printf("f10_first_slot_after_boot_ms=%u\n", (unsigned)up);
}

int main(void)
{
    f05();
    f11_f04();
    f06();
    f07();
    f08();
    f10();
    printf("f12_margin_sos_text=%s\n", panel_page_text[PAGE_SOS_QUEUED_MARGIN]);
    for (uint8_t s = 0; s < 3; s++) {
        bool a, b;
        panel_hdmi_encode(s, &a, &b);
        printf("f13_slot%u_sel1=%d\nf13_slot%u_sel2=%d\n", s + 1u, a, s + 1u, b);
    }
    return 0;
}
