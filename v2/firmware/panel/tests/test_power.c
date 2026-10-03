/* test_power.c: boot order, slots, display select, shutdown, shore inhibit, hot stop, margin hold, power controls and
 * the bus recovery. */
#include "fixture.h"

static const bool ALL[3] = { true, true, true };
static const bool NONE[3] = { false, false, false };

void t_boot_order(void)
{
    fx_t F, *x = &F;
    fx_new(x);
    fx_init(x, false, NULL);
    fx_tick(x);
    /* steps 1 and 2 from the first tick: PI_KILL low, PI_SHDN_REQ released */
    CHECK(!x->out.pi_kill && !x->out.pi_shdn_assert);
    CHECK(x->n_wr == 0);                            /* step 3 (the ZEROIZE read, 30 ms stable) before any expander */
    unsigned first_slot_tick = 0, zer_done_tick = 0, exp_tick = 0;
    for (unsigned t = 1; t < 8000; t++) {
        x->now++;
        fx_tick(x);
        if (!zer_done_tick && x->p.boot > BOOT_ZEROIZE)
            zer_done_tick = t;
        if (!exp_tick && x->n_wr)
            exp_tick = t;
        if (!first_slot_tick && (x->out.slot_en[0] || x->out.slot_en[1] || x->out.slot_en[2]))
            first_slot_tick = t;
    }
    CHECK(zer_done_tick >= 30 && exp_tick >= zer_done_tick);
    CHECK(first_slot_tick > exp_tick);
    CHECK(first_slot_tick >= 2000);                 /* after HOT-R1 was read at 1 Hz (FW-C14) */
    /* step 6: one at a time */
    int up_at[3] = { -1, -1, -1 };
    fx_t G, *y = &G;
    fx_new(y);
    fx_init(y, false, NULL);
    for (int t = 0; t < 10000; t++) {
        fx_tick(y);
        for (int i = 0; i < 3; i++)
            if (up_at[i] < 0 && y->out.slot_en[i])
                up_at[i] = t;
        y->now++;
    }
    CHECK(up_at[0] >= 0 && up_at[1] >= up_at[0] + 1000 && up_at[2] >= up_at[1] + 1000);
    CHECK(!y->out.pi_kill);                         /* never released while a slot is powered */
}

void t_boot_slot_adopt(void)
{
    bool held[3] = { true, false, true }, drive[3];
    fx_t F, *x = &F;
    fx_new(x);
    panel_init(&x->p, &x->ops, x->now, false, held, drive);
    CHECK(drive[0] && !drive[1] && drive[2]);       /* FW-C02: driven at the level read */
    fx_tick(x);
    CHECK(x->out.slot_en[0] && !x->out.slot_en[1] && x->out.slot_en[2]);   /* no glitch on a running slot */
    /* a wipe-pending record drives all three low first */
    fx_t G, *y = &G;
    fx_new(y);
    fx_init(y, false, NULL);
    panel_zj_append(&y->p, ZJ_PENDING);
    panel_init(&y->p, &y->ops, y->now, false, held, drive);
    CHECK(!drive[0] && !drive[1] && !drive[2]);
}

void t_exp_outputs_before_config(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    static const uint8_t cfgd[] = { HAL_I2C_C_U1, HAL_I2C_C_U2, HAL_I2C_A_U27, HAL_I2C_A_U28, HAL_I2C_B_U6, HAL_I2C_D_U16 };
    for (size_t i = 0; i < sizeof cfgd; i++) {
        int o = fx_find_write(x, cfgd[i], PCA9555_OUT0, 0);
        int c = fx_find_write(x, cfgd[i], PCA9555_CFG0, 0);
        CHECK(o >= 0 && c >= 0 && o < c);
        int o1 = fx_find_write(x, cfgd[i], PCA9555_OUT1, 0);
        int c1 = fx_find_write(x, cfgd[i], PCA9555_CFG1, 0);
        CHECK(o1 >= 0 && c1 >= 0 && o1 < c1);
    }
    CHECK(fx_find_write(x, HAL_I2C_B_U7, PCA9555_CFG0, 0) < 0);   /* inputs only: left alone */
    /* DEV_EN stays 1; every other board A enable 0 */
    CHECK(x->regs[HAL_I2C_A_U27][2] == (1u << HAL_EXP_A_DEV_EN_BIT));
    for (unsigned i = 0; i < x->n_wr; i++)
        if (x->wr[i].addr == HAL_I2C_A_U27 && x->wr[i].reg == PCA9555_OUT0)
            CHECK(x->wr[i].val & (1u << HAL_EXP_A_DEV_EN_BIT));
    /* the boot values: every board B request and board A U28 enable 0 */
    CHECK(x->wr[fx_find_write(x, HAL_I2C_A_U28, PCA9555_OUT0, 0)].val == 0);
    CHECK(x->wr[fx_find_write(x, HAL_I2C_B_U6, PCA9555_OUT0, 0)].val == 0);
    CHECK(x->wr[fx_find_write(x, HAL_I2C_B_U6, PCA9555_OUT1, 0)].val == 0);
    /* board D's U16 at the generator's power-up levels (FW-D01, F-11): X_SA_PD 1, X_AMP_EN 1, X_MMUTE 0, those three outputs */
    CHECK(x->wr[fx_find_write(x, HAL_I2C_D_U16, PCA9555_OUT0, 0)].val == 0x60);
    CHECK(x->wr[fx_find_write(x, HAL_I2C_D_U16, PCA9555_CFG0, 0)].val == 0x1F);
    /* with no bridge every switched load stays off; RB_SW_IEN follows the request rule (RB_STATUS low, no EMCON) */
    CHECK(x->regs[HAL_I2C_A_U27][2] == (1u << HAL_EXP_A_DEV_EN_BIT) && x->regs[HAL_I2C_A_U28][2] == 0);
    CHECK(x->regs[HAL_I2C_B_U6][2] == 0 && x->regs[HAL_I2C_B_U6][3] == (1u << HAL_EXP_B_RB_SW_IEN_BIT));
}

void t_hb_lost_3s(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    fx_run_hb(x, 3000, ALL);
    CHECK(x->p.slot[0].alive && x->p.slot[1].alive && x->p.slot[2].alive);
    x->in.hb[1] = true;                             /* slot 2's line held high (a dark module, R258) */
    bool t[3] = { true, false, true };
    fx_run_hb(x, 2400, t);
    CHECK(x->p.slot[1].alive);                      /* under 3 s since the last edge */
    fx_run_hb(x, 700, t);
    CHECK(!x->p.slot[1].alive);                     /* lost after 3 s */
    CHECK(x->p.slot[0].alive);
}

void t_slot_fault_cycle(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    bool t[3] = { true, false, true };
    fx_run_hb(x, 4000, t);
    CHECK(x->out.slot_en[1]);
    ms_t up = x->p.slot[1].since;
    while (x->now < up + 59990)
        fx_run_hb(x, 1, t);
    CHECK(x->out.slot_en[1] && !x->p.slot[1].fault);
    fx_run_hb(x, 20, t);
    CHECK(!x->out.slot_en[1] && x->p.slot[1].fault);   /* flat 60 s: a slot fault, rail off */
    CHECK(x->out.leds & LED_BIT(LED_MCAUT) || x->p.amb_active);
    fx_run_hb(x, 4900, t);
    CHECK(!x->out.slot_en[1]);
    fx_run_hb(x, 200, t);
    CHECK(x->out.slot_en[1]);                       /* power-cycled once, 5 s off */
    fx_run_hb(x, 61000, t);
    CHECK(!x->out.slot_en[1] && x->p.slot[1].state == SLOT_FAULT_OFF);
    fx_run_hb(x, 120000, t);
    CHECK(!x->out.slot_en[1]);                      /* left off until the operator acts */
    panel_slot_operator_retry(&x->p, 1, x->now);
    fx_run_hb(x, 1500, ALL);
    CHECK(x->out.slot_en[1]);
}

void t_hdmi_select(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    bool t[3] = { false, true, true };
    fx_run_hb(x, 5000, t);
    /* no bridge instruction: the lowest live slot, slot 2 */
    CHECK(x->out.hdmi_sel1 && !x->out.hdmi_sel2);
    /* the bridge names slot 3 */
    x->in.br.alive = true;
    x->in.br.display_slot = 2;
    fx_run_hb(x, 10, t);
    CHECK(x->out.hdmi_sel2);
    bool s1, s2;                                    /* the encoding (F-13) */
    panel_hdmi_encode(0, &s1, &s2);
    CHECK(!s1 && !s2);
    panel_hdmi_encode(1, &s1, &s2);
    CHECK(s1 && !s2);
    panel_hdmi_encode(2, &s1, &s2);
    CHECK(!s1 && s2);
    /* the bridge names slot 1, which is dark: never a dark slot */
    x->in.br.display_slot = 0;
    fx_run_hb(x, 10, t);
    CHECK(x->out.hdmi_sel1 && !x->out.hdmi_sel2);
    /* every slot dark: the selection stays */
    fx_run_hb(x, 4000, NONE);
    CHECK(x->out.hdmi_sel1 && !x->out.hdmi_sel2);
}

void t_shutdown_main_tap(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    fx_run_hb(x, 4000, ALL);
    x->main_low = true;                      /* INT low under 32 ms: no tap */
    fx_run_hb(x, 20, ALL);
    x->main_low = false;
    fx_run_hb(x, 20, ALL);
    CHECK(x->p.shdn == SHDN_IDLE);
    x->main_low = true;                      /* a MAIN tap */
    unsigned low = 0;
    for (int i = 0; i < 400; i++) {
        if (i == 40) {
            CHECK(x->p.shdn == SHDN_PULSE);
            x->main_low = false;
        }
        fx_run_hb(x, 1, ALL);
        low += x->out.pi_shdn_assert;
    }
    CHECK(low >= 198 && low <= 201);                /* pulled low at least 200 ms, never driven high */
    fx_run_hb(x, 10000, ALL);
    CHECK(!x->out.pi_kill);                         /* heartbeats still toggling: wait */
    CHECK(x->out.slot_en[0]);
    fx_run_hb(x, 3100, NONE);                       /* they stop */
    fx_run_hb(x, 10, NONE);
    CHECK(x->out.pi_kill);                          /* then PI_KILL high */
    fx_run_hb(x, 3000, NONE);
    CHECK(x->out.pi_kill);                          /* held */
}

void t_shore_inhibit(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    CHECK(!x->out.shore_inhibit);                   /* boot low */
    x->in.br.alive = true;
    x->in.br.shore_cmd = SHORE_CMD_INPUTS_OFF;
    fx_run(x, 5);
    CHECK(x->out.shore_inhibit);
    x->in.br.shore_cmd = SHORE_CMD_NONE;
    fx_run(x, 5);
    CHECK(!x->out.shore_inhibit);
    x->in.br.shore_cmd = SHORE_CMD_OTHER;           /* never a charge hold */
    fx_run(x, 5);
    CHECK(!x->out.shore_inhibit && x->out.shore_refused);
    x->in.br.shore_cmd = SHORE_CMD_WATER_ISOLATION;
    x->in.br.pack_cannot_discharge = true;          /* S2, S4: the warning first */
    fx_run(x, 5);
    CHECK(!x->out.shore_inhibit && x->out.shore_refused);
    x->in.br.shore_warned = true;
    fx_run(x, 5);
    CHECK(x->out.shore_inhibit);
    x->in.br.alive = false;                         /* the link drops: the last state is held */
    fx_run(x, 5);
    CHECK(x->out.shore_inhibit);
    /* a hot stop or a margin hold never raises it */
    fx_t G, *y = &G;
    fx_boot(y);
    y->hot_sim = HOT_SIM_5HZ;
    fx_run(y, 4000);
    CHECK(y->p.hot.state == HOT_H1 && !y->out.shore_inhibit && y->out.charge_hold_hot);
}

void t_hotr1_decode(void)
{
    panel_hot_t h;
    memset(&h, 0, sizeof h);
    for (ms_t t = 0; t < 5000; t += 10)
        panel_hot_sample(&h, (t / 1000u) & 1u, t);
    CHECK(panel_hot_classify(&h, 5000) == HOT_LINE_1HZ);
    memset(&h, 0, sizeof h);
    for (ms_t t = 0; t < 3000; t += 10)
        panel_hot_sample(&h, (t / 200u) & 1u, t);
    CHECK(panel_hot_classify(&h, 3000) == HOT_LINE_5HZ);
    memset(&h, 0, sizeof h);
    for (ms_t t = 0; t < 4000; t += 10)
        panel_hot_sample(&h, false, t);
    CHECK(panel_hot_classify(&h, 4000) == HOT_LINE_HELD_LOW);
    memset(&h, 0, sizeof h);
    for (ms_t t = 0; t < 4000; t += 10)
        panel_hot_sample(&h, true, t);
    CHECK(panel_hot_classify(&h, 4000) == HOT_LINE_HELD_HIGH);
    /* a toggling line that stops: held after 3 s without an edge */
    memset(&h, 0, sizeof h);
    for (ms_t t = 0; t < 3000; t += 10)
        panel_hot_sample(&h, (t / 1000u) & 1u, t);
    for (ms_t t = 3000; t <= 5100; t += 10)
        panel_hot_sample(&h, false, t);             /* the reads go on, the line stays low */
    CHECK(panel_hot_classify(&h, 4900) == HOT_LINE_1HZ);
    CHECK(panel_hot_classify(&h, 5100) == HOT_LINE_HELD_LOW);
    /* the same with the reads stopping: no verdict on old evidence, then the detector lost */
    memset(&h, 0, sizeof h);
    for (ms_t t = 0; t < 3000; t += 10)
        panel_hot_sample(&h, (t / 1000u) & 1u, t);
    CHECK(panel_hot_classify(&h, 2995) == HOT_LINE_1HZ);
    CHECK(panel_hot_classify(&h, 5100) == HOT_LINE_1HZ);
    CHECK(panel_hot_classify(&h, 6000) == HOT_LINE_HELD_HIGH);
    /* in the core: every EXP_INT serviced by reading U27, then a command byte other than 00h; polled once a second */
    fx_t F, *x = &F;
    fx_boot(x);
    unsigned r0 = x->n_reads[HAL_I2C_A_U27], c0 = x->cmd_byte_writes_u27;
    x->hot_sim = HOT_SIM_HIGH;
    fx_run(x, 3000);
    CHECK(x->n_reads[HAL_I2C_A_U27] - r0 >= 3);
    CHECK(x->cmd_byte_writes_u27 - c0 == x->n_reads[HAL_I2C_A_U27] - r0);
}

void t_hot_stop_h1(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.br.alive = true;
    x->in.br.loads_wanted = (uint16_t)((1u << LOAD_COUNT) - 1u);    /* the bridge wants every load on */
    fx_run_hb(x, 4000, ALL);
    CHECK(x->regs[HAL_I2C_A_U27][2] == 0xFE && x->regs[HAL_I2C_A_U28][2] == 1 && x->regs[HAL_I2C_A_U28][3] == 1);
    x->hot_sim = HOT_SIM_5HZ;
    fx_run_hb(x, 1500, ALL);
    CHECK(x->p.hot.state == HOT_H1);
    /* the actions: the clean-shutdown request, the loads off, the charge bit's flag, MASTER WARN, the page */
    CHECK(x->out.loads_off & (1u << LOAD_MONITOR));
    CHECK(x->out.loads_off & (1u << LOAD_PA) && x->out.loads_off & (1u << LOAD_HF));
    CHECK(x->out.loads_off & (1u << LOAD_POE) && x->out.loads_off & (1u << LOAD_USBC));
    CHECK(x->out.loads_off & (1u << LOAD_HEATER) && x->out.loads_off & (1u << LOAD_BOARD_D));
    CHECK(x->out.loads_off & (1u << LOAD_WALL_VBUS));
    CHECK(x->out.charge_hold_hot && !x->out.shore_inhibit);
    CHECK(x->regs[HAL_I2C_A_U27][2] == (1u << HAL_EXP_A_DEV_EN_BIT));   /* every enable off on A:U27, +3V3_DEV kept */
    CHECK(x->p.red_active & 4u);
    CHECK(x->out.slot_en[0]);                       /* modules still running: not yet dropped */
    CHECK(x->p.shdn == SHDN_IDLE && !x->out.pi_kill);   /* its own pull on PI_SHDN_REQ is not a MAIN tap */
    bool two[3] = { true, false, true };
    fx_run_hb(x, 3200, two);                        /* slot 2's module stops first */
    CHECK(x->out.slot_en[0] && !x->out.slot_en[1] && x->out.slot_en[2]);   /* each once it has stopped */
    fx_run_hb(x, 3500, NONE);                       /* they stop */
    CHECK(!x->out.slot_en[0] && !x->out.slot_en[1] && !x->out.slot_en[2]);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_HOT_STOP);
    /* back at 1 Hz, but under 30 minutes: still H1 */
    x->hot_sim = HOT_SIM_1HZ;
    fx_run(x, 600000);
    CHECK(x->p.hot.state == HOT_H1);
    for (int i = 0; i < 1300; i++)
        fx_run(x, 1000);
    CHECK(x->p.hot.state == HOT_NONE);
    fx_run(x, 3000);
    CHECK(!x->out.slot_en[0] && x->out.slot_en[1] && !x->out.slot_en[2]);   /* the heat stage's one module */
}

void t_hot_stop_h2(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    fx_run_hb(x, 4000, ALL);
    x->hot_sim = HOT_SIM_LOW;
    fx_run_hb(x, 3500, ALL);
    CHECK(x->p.hot.state == HOT_H2);
    fx_run(x, 1000);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_HOT_SHUTDOWN);
    CHECK(x->out.pi_kill);                          /* the page, then PI_KILL */
}

void t_hot_tmp117_fallback(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->hot_sim = HOT_SIM_HIGH;                      /* the sensor controller lost */
    fx_run(x, 4000);
    CHECK(x->out.reduced_mode);                     /* THERMAL-COORDINATION s.7's fallback */
    CHECK(x->out.loads_off & (1u << LOAD_POE) && x->out.loads_off & (1u << LOAD_USBC));
    CHECK(!x->out.slot_en[0]);                      /* the reduced mode: slots 2 and 3 */
    x->in.tmp117.valid = true;
    x->in.tmp117.mc = 55000;
    x->in.tmp117.seq = 1;
    fx_run(x, 1000);
    CHECK(x->p.hot.state == HOT_NONE);              /* one reading is not two */
    x->in.tmp117.seq = 2;
    fx_run(x, 1000);
    CHECK(x->p.hot.state == HOT_H1);
    x->in.tmp117.mc = 56000;
    x->in.tmp117.seq = 3;
    fx_run(x, 1000);
    CHECK(x->p.hot.state == HOT_H1);
    x->in.tmp117.seq = 4;
    fx_run(x, 1000);
    CHECK(x->p.hot.state == HOT_H2);
}

void t_hot_boot_read(void)
{
    /* held low at start-up: the H2 page and PI_KILL, no slot raised */
    fx_t F, *x = &F;
    fx_new(x);
    x->hot_sim = HOT_SIM_LOW;
    fx_init(x, false, NULL);
    bool raised = false;
    for (int i = 0; i < 40000; i++) {
        fx_tick(x);
        raised |= x->out.slot_en[0] || x->out.slot_en[1] || x->out.slot_en[2];
        x->now++;
    }
    CHECK(!raised && x->out.pi_kill);
    /* at 5 Hz: no slot raised until it is back at 1 Hz */
    fx_t G, *y = &G;
    fx_new(y);
    y->hot_sim = HOT_SIM_5HZ;
    fx_init(y, false, NULL);
    raised = false;
    for (int i = 0; i < 20000; i++) {
        fx_tick(y);
        raised |= y->out.slot_en[0] || y->out.slot_en[1] || y->out.slot_en[2];
        y->now++;
    }
    CHECK(!raised && y->p.boot != BOOT_RUN);
    y->hot_sim = HOT_SIM_1HZ;
    for (int i = 0; i < 5000; i++) {
        fx_tick(y);
        y->now++;
    }
    CHECK(y->p.boot == BOOT_RUN);
}

void t_margin_hold(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.br.alive = true;
    x->in.br.loads_wanted = (uint16_t)((1u << LOAD_COUNT) - 1u);
    x->in.br.margin_ref.valid = true;
    x->in.br.margin_ref.mc = 68650;
    x->in.br.margin_ref.seq = 1;
    fx_run(x, 100);
    CHECK(!x->p.margin_hold);
    x->in.br.margin_ref.seq = 2;                    /* two readings in a row at or over 68.65 C */
    fx_run(x, 100);
    CHECK(x->p.margin_hold);
    CHECK(x->out.charge_hold_margin && !x->out.shore_inhibit);
    CHECK(x->out.loads_off & (1u << LOAD_BOARD_D) && x->out.loads_off & (1u << LOAD_PA));
    CHECK(x->out.loads_off & (1u << LOAD_ROCKBLOCK) && x->out.loads_off & (1u << LOAD_LORA));
    CHECK(x->out.loads_off & (1u << LOAD_ZIGBEE) && x->out.loads_off & (1u << LOAD_GEIGER));
    CHECK(!x->out.rb_ien_request);
    CHECK((x->regs[HAL_I2C_B_U6][2] & 0x1Cu) == 0);  /* RB_SW_EN, LORA_ON, ZB_ON off on B:U6 */
    CHECK(!(x->regs[HAL_I2C_A_U27][2] & (1u << HAL_EXP_A_PA_SW_EN_BIT)) && !(x->regs[HAL_I2C_A_U27][2] & (1u << HAL_EXP_A_D8_EN_BIT)));
    CHECK(x->p.amb_active & 16u);                   /* MASTER CAUT */
    fx_run(x, 1000);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_MARGIN_HOLD);
    /* an SOS raised meanwhile is queued and told */
    x->in.sos_sw = false;
    fx_run(x, 2600);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_SOS_QUEUED_MARGIN);
    x->in.sos_sw = true;
    /* restore: 5 K under the trigger after 30 minutes */
    x->in.br.margin_ref.mc = 63700;
    x->in.br.margin_ref.seq = 3;
    fx_run(x, 1000);
    CHECK(x->p.margin_hold);                        /* 63.70 C is not 5 K under */
    x->in.br.margin_ref.mc = 63650;
    for (int i = 0; i < 1800; i++)
        fx_run(x, 1000);
    CHECK(!x->p.margin_hold);
}

void t_power_fallback(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    fx_run_hb(x, 4000, ALL);
    x->in.br.alive = true;
    x->in.br.cell_max.valid = true;
    x->in.br.cell_max.mc = 30000;
    x->in.br.cell_max.seq = 1;
    fx_run_hb(x, 5000, ALL);
    CHECK(!x->out.reduced_mode);
    fx_run_hb(x, 5100, ALL);                        /* the pack readings stopped for 10 s */
    CHECK(x->out.reduced_mode);
    CHECK(x->out.loads_off & (1u << LOAD_POE) && x->out.loads_off & (1u << LOAD_USBC));
    CHECK(!x->out.slot_en[0] && x->out.slot_en[1] && x->out.slot_en[2]);
    /* C1's first stage: +55 C on a cell sheds to the reduced mode; 5 K below restores */
    x->in.br.cell_max.seq = 2;
    x->in.br.cell_max.mc = 55000;
    fx_run_hb(x, 10, ALL);
    CHECK(x->out.reduced_mode);
    x->in.br.cell_max.seq = 3;
    x->in.br.cell_max.mc = 50000;
    fx_run_hb(x, 10, ALL);
    CHECK(!x->out.reduced_mode);
}

/* ---- the bus recovery, on a fake line that releases after n pulses ---- */
typedef struct { int release_after; int pulses; bool stopped; int scl_low_long; } bb_t;
static void bb_scl(void *c, bool l) { bb_t *b = c; if (l) b->pulses++; }
static bool bb_sda(void *c) { bb_t *b = c; return b->pulses >= b->release_after; }
static void bb_stop(void *c) { ((bb_t *)c)->stopped = true; }
static void bb_delay(void *c, unsigned us) { if (us > 10000u) ((bb_t *)c)->scl_low_long++; }

void t_bus_recover(void)
{
    bb_t b = { 3, 0, false, 0 };
    panel_bitbang_t bb = { &b, bb_scl, bb_sda, bb_stop, bb_delay };
    CHECK(panel_bus_recover(&bb) == 3 && b.stopped && b.scl_low_long == 0);
    bb_t s = { 99, 0, false, 0 };                   /* a target that never lets go: nine pulses, then a failure */
    bb.ctx = &s;
    CHECK(panel_bus_recover(&bb) == -1 && s.pulses == 9 && s.stopped);
}

void t_hotr1_bus_lost(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->hot_sim = HOT_SIM_LOW;                       /* the last level read is low ... */
    fx_run(x, 1200);
    x->bus_fail = true;                             /* ... then the kit bus stops answering */
    fx_run(x, 6000);
    CHECK(x->p.hot.line == HOT_LINE_HELD_HIGH);     /* the detector lost, never a stale "held low" */
    CHECK(x->p.hot.state != HOT_H2 && !x->out.pi_kill);
    CHECK(x->out.reduced_mode && (x->out.loads_off & (1u << LOAD_USBC)));
}

void t_boot_main_tap(void)
{
    fx_t F, *x = &F;
    fx_new(x);
    fx_init(x, false, NULL);
    for (int i = 0; i < 100; i++) {                 /* into the boot, before any slot */
        fx_tick(x);
        x->now++;
    }
    CHECK(x->p.boot != BOOT_RUN);
    x->main_low = true;
    fx_run(x, 40);
    x->main_low = false;
    fx_run(x, 400);
    CHECK(x->out.pi_kill);                          /* no module ran: the kit goes off */
}

void t_hot_boot_held_slot(void)
{
    /* FW-C14 with the SLOT_EN hold: a slot found held up at boot, the line at 5 Hz: H1's shutdown of that slot */
    bool held[3] = { false, true, false }, drive[3];
    fx_t F, *x = &F;
    fx_new(x);
    x->hot_sim = HOT_SIM_5HZ;
    panel_init(&x->p, &x->ops, x->now, false, held, drive);
    CHECK(drive[1]);
    bool t[3] = { false, true, false };
    unsigned asserted = 0;
    for (int i = 0; i < 4000; i++) {
        fx_run_hb(x, 1, t);
        asserted += x->out.pi_shdn_assert;
        CHECK(!x->out.slot_en[0] && !x->out.slot_en[2]);   /* nothing raised */
    }
    CHECK(x->p.hot.state == HOT_H1 && asserted >= 199);    /* the clean-shutdown request */
    CHECK(x->out.slot_en[1]);                               /* still running: kept until it stops */
    fx_run_hb(x, 3200, NONE);
    CHECK(!x->out.slot_en[1]);
}

void t_no_raise_while_zeroize_armed(void)
{
    fx_t F, *x = &F;
    fx_new(x);
    fx_init(x, false, NULL);
    for (int i = 0; i < 10000 && !x->out.slot_en[0]; i++) {
        fx_tick(x);
        x->now++;
    }
    CHECK(x->out.slot_en[0] && !x->out.slot_en[1]);         /* slot 1 up, slot 2 waiting its turn */
    x->in.zeroize_sw = false;                                /* the ZEROIZE toggle closed */
    for (int i = 0; i < 4900; i++) {
        fx_run(x, 1);
        CHECK(!x->out.slot_en[1] && !x->out.slot_en[2]);
    }
    x->in.zeroize_sw = true;                                 /* aborted: the slots rise again */
    fx_run(x, 3000);
    CHECK(x->out.slot_en[1] && x->out.slot_en[2]);
}

void t_switch_closed_at_power_up(void)
{
    /* SOS closed at power-up: SOS mode 2 s after the controller starts, never sooner */
    fx_t F, *x = &F;
    fx_new(x);
    x->in.sos_sw = false;
    fx_init(x, false, NULL);
    ms_t t0 = x->now;
    while (!x->p.sos_armed && x->now < t0 + 20000)
        fx_run(x, 1);
    CHECK(x->p.sos_armed && x->now - t0 >= 2000);
}

static void tmp117_convert(fx_t *x, int32_t mc)
{
    x->r16[HAL_I2C_TMP117][0] = (uint16_t)(int16_t)(mc * 16 / 125);
    x->r16[HAL_I2C_TMP117][1] |= (uint16_t)(1u << 13);   /* Data_Ready */
}

void t_tmp117_read(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    fx_run(x, 1000);
    CHECK(!x->p.tmp117.valid);                      /* 8000h until the first conversion */
    tmp117_convert(x, 55000);
    fx_run(x, 300);
    CHECK(x->p.tmp117.valid && x->p.tmp117.mc == 55000 && x->p.tmp117.seq == 1);
    fx_run(x, 2000);
    CHECK(x->p.tmp117.seq == 1);                    /* one conversion read many times counts once */
    tmp117_convert(x, -12500);
    fx_run(x, 300);
    CHECK(x->p.tmp117.mc == -12500 && x->p.tmp117.seq == 2);
    /* in use: HOT-R1 held high and two conversions at +55.0 C, read off the bus: H1 */
    fx_t G, *y = &G;
    fx_boot(y);
    y->hot_sim = HOT_SIM_HIGH;
    fx_run(y, 4000);
    tmp117_convert(y, 55000);
    fx_run(y, 1000);
    CHECK(y->p.hot.state == HOT_NONE);
    tmp117_convert(y, 55100);
    fx_run(y, 1000);
    CHECK(y->p.hot.state == HOT_H1);
}

void t_veml7700_read(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    CHECK(x->r16[HAL_I2C_VEML7700][0] == 0x1000);   /* gain x1/8, 100 ms, powered on */
    x->r16[HAL_I2C_VEML7700][4] = 1000;
    fx_run(x, 1100);
    CHECK(x->out.light_valid && x->out.light_mlux == 537600);
}

void t_se_absent_retried(void)
{
    fx_t F, *x = &F;
    fx_new(x);
    x->se_dead = true;
    fx_init(x, false, NULL);
    for (int i = 0; i < 6000 && x->p.boot != BOOT_RUN; i++) {
        fx_tick(x);
        x->now++;
    }
    CHECK(x->p.zer.se_absent && (x->p.red_active & 16u));
    x->se_dead = false;                             /* it answers again */
    fx_run(x, 61000);
    CHECK(!x->p.zer.se_absent);
    fx_run(x, 10);
    CHECK(!(x->p.red_active & 16u));
}

void t_modules_lost_caut_then_warn(void)
{
    /* F-07 (CONOPS 4e): one compute module lost is MASTER CAUT, two lost is MASTER WARN */
    fx_t F, *x = &F;
    fx_boot(x);
    bool t[3] = { true, false, true };              /* slot 2 never answers */
    fx_run_hb(x, 66000, t);
    CHECK(panel_modules_lost(&x->p) == 1);
    CHECK((x->p.amb_active & 8u) && !(x->p.red_active & 32u));
    bool u[3] = { true, false, false };             /* slot 3's bridge stops while its rail stays up */
    fx_run_hb(x, 3500, u);
    CHECK(panel_modules_lost(&x->p) == 2);
    CHECK(x->p.red_active & 32u);
    unsigned warn = 0;
    for (int i = 0; i < 1000; i++) {
        fx_run_hb(x, 1, u);
        warn += (x->out.leds >> LED_MWARN) & 1u;
    }
    CHECK(warn > 300 && warn < 700);                /* unacknowledged: flashing */
    /* a deliberate stop loses nothing: a clean shutdown in progress */
    x->main_low = true;
    fx_run_hb(x, 40, u);
    x->main_low = false;
    fx_run_hb(x, 10, u);
    CHECK(panel_modules_lost(&x->p) == 0);
}

void t_after_h1_restore_5k_below(void)
{
    /* S-19 not adopted: after H1 the heat stage's module rises first (FW-C13); C1's restore 5 K below (FW-C09) then
     * releases the others */
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.br.alive = true;
    x->hot_sim = HOT_SIM_5HZ;
    fx_run(x, 2000);
    CHECK(x->p.hot.state == HOT_H1);
    x->hot_sim = HOT_SIM_1HZ;
    for (int i = 0; i < 1810; i++)
        fx_run(x, 1000);
    CHECK(x->p.hot.state == HOT_NONE && x->p.heat_stage_only);
    bool hs[3] = { false, true, false };
    fx_run_hb(x, 3000, hs);
    CHECK(!x->out.slot_en[0] && x->out.slot_en[1] && !x->out.slot_en[2]);   /* the heat stage's module first */
    x->in.br.cell_max.valid = true;                 /* the cells 6 K under C1's +55 C, the air 6 K under +50 C */
    x->in.br.cell_max.mc = 49000;
    x->in.br.cell_max.seq = 1;
    x->in.br.inside_air.valid = true;
    x->in.br.inside_air.mc = 44000;
    x->in.br.inside_air.seq = 1;
    fx_run_hb(x, 3000, hs);
    CHECK(!x->p.heat_stage_only);
    CHECK(x->out.slot_en[0] && x->out.slot_en[1] && x->out.slot_en[2]);
}

void t_pi_button_on_u1_p13_when_wired(void)
{
    /* the drafted input (PANEL.md s.4 row 3, record l8r2, PROVISIONAL): PI_BTN_n on U1 P1.3, low = pressed. As generated
     * the pin is a floating spare, so with the wiring flag off a low there is never a press */
    fx_t F, *x = &F;
    fx_boot(x);
    x->regs[HAL_I2C_C_U1][1] &= (uint8_t)~(1u << HAL_EXP_C_PI_BTN_N_BIT);
    fx_run(x, 2500);
    CHECK(x->p.shdn == SHDN_IDLE);
    x->regs[HAL_I2C_C_U1][1] |= (uint8_t)(1u << HAL_EXP_C_PI_BTN_N_BIT);
    fx_run(x, 1500);
    x->p.pi_btn_wired = true;                       /* board C regenerated with l8r2's draft */
    x->regs[HAL_I2C_C_U1][1] &= (uint8_t)~(1u << HAL_EXP_C_PI_BTN_N_BIT);
    fx_run(x, 1500);                                /* read at the once-a-second poll */
    x->regs[HAL_I2C_C_U1][1] |= (uint8_t)(1u << HAL_EXP_C_PI_BTN_N_BIT);
    fx_run(x, 1500);
    CHECK(x->p.shdn != SHDN_IDLE);                  /* a short press: the clean shutdown */
}
