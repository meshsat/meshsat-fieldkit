/* fixture.c: the fakes behind fixture.h. Host only. */
#include "fixture.h"

int test_failed;

void fx_log(fx_t *f, const char *s)
{
    size_t n = strlen(f->log);
    if (n + strlen(s) + 2 < sizeof f->log) {
        if (n)
            strcat(f->log, " ");
        strcat(f->log, s);
    }
}

/* ---- bus: PCA9555 register model (pairs auto-increment within the pair, SCPS131J 8.6.2) ---- */
static int bus_write(void *ctx, uint8_t addr, const uint8_t *buf, unsigned len)
{
    fx_t *f = ctx;
    if (f->bus_fail || !f->present[addr] || len == 0)
        return -1;
    uint8_t reg = buf[0];
    if (len == 1 && addr == HAL_I2C_A_U27 && reg != 0)
        f->cmd_byte_writes_u27++;
    for (unsigned i = 1; i < len; i++) {
        uint8_t r = (uint8_t)((reg & ~1u) | ((reg + (i - 1)) & 1u));
        if (r >= 2 && r < 8)
            f->regs[addr][r] = buf[i];
        if (f->n_wr < FX_LOG) {
            f->wr[f->n_wr].addr = addr;
            f->wr[f->n_wr].reg = r;
            f->wr[f->n_wr].val = buf[i];
            f->wr[f->n_wr].seq = f->seq++;
            f->n_wr++;
        }
    }
    return 0;
}

static int bus_read(void *ctx, uint8_t addr, uint8_t reg, uint8_t *buf, unsigned len)
{
    fx_t *f = ctx;
    if (f->bus_fail || !f->present[addr])
        return -1;
    f->n_reads[addr]++;
    for (unsigned i = 0; i < len; i++)
        buf[i] = f->regs[addr][(reg & ~1u) | ((reg + i) & 1u)];
    return 0;
}

/* ---- secure element ---- */
static ms_t fz_now(void *ctx) { return ((fx_t *)ctx)->now; }

static int se_create(void *ctx, uint8_t s, uint8_t pub[64], ms_t deadline)
{
    fx_t *f = ctx;
    char b[8];
    if (f->now >= deadline)
        return -2;
    f->now += f->cmd_ms;
    f->n_cmds++;
    snprintf(b, sizeof b, "C%u", s);
    fx_log(f, b);
    if (f->se_dead)
        return -1;
    if (f->fail_create[s] > 0) {
        f->fail_create[s]--;
        return -1;
    }
    f->key_ctr++;
    memset(f->key[s], (int)(0x40 + f->key_ctr), 64);
    memcpy(pub, f->key[s], 64);
    return 0;
}

static int se_public(void *ctx, uint8_t s, uint8_t pub[64], ms_t deadline)
{
    fx_t *f = ctx;
    char b[8];
    if (f->now >= deadline)
        return -2;
    f->now += f->cmd_ms;
    f->n_cmds++;
    snprintf(b, sizeof b, "V%u", s);
    fx_log(f, b);
    if (f->se_dead)
        return -1;
    if (f->fail_public[s] > 0) {
        f->fail_public[s]--;
        return -1;
    }
    memcpy(pub, f->key[s], 64);
    return 0;
}

static bool se_rec(void *ctx, uint8_t s, uint8_t pub[64])
{
    fx_t *f = ctx;
    if (!f->have_rec)
        return false;
    memcpy(pub, f->rec[s], 64);
    return true;
}

static void arm_cut(void *ctx, ms_t at)
{
    fx_t *f = ctx;
    f->alarm_at = at;
    fx_log(f, "A");
}

static void tell(void *ctx)
{
    fx_t *f = ctx;
    f->told = true;
    f->told_at = f->now;
    fx_log(f, "T");
}

static int fl_read(void *ctx, uint32_t off, uint8_t *buf, unsigned len)
{
    fx_t *f = ctx;
    memcpy(buf, f->flash + off, len);
    return 0;
}

static int fl_prog(void *ctx, uint32_t off, const uint8_t *buf, unsigned len)
{
    fx_t *f = ctx;
    char b[8];
    snprintf(b, sizeof b, "J%u", buf[2]);
    fx_log(f, b);
    if (f->flash_fail_program) {
        f->flash_fail_program--;
        f->flash[off] = 'Z';                 /* a torn record */
        return -1;
    }
    for (unsigned i = 0; i < len; i++)
        f->flash[off + i] &= buf[i];
    return 0;
}

static int fl_erase(void *ctx)
{
    fx_t *f = ctx;
    memset(f->flash, 0xFF, sizeof f->flash);
    return 0;
}

static void epd_send(void *ctx, uint8_t page, bool full)
{
    fx_t *f = ctx;
    if (f->n_epd < 64) {
        f->epd_pages[f->n_epd] = page;
        f->epd_full[f->n_epd] = full;
        f->epd_at[f->n_epd] = f->now;
        f->n_epd++;
    }
    f->busy_until = f->now + 100;            /* the refresh: BUSY high */
}

void fx_new(fx_t *f)
{
    memset(f, 0, sizeof *f);
    f->now = 1000;
    f->cmd_ms = 128;                         /* ZER s.3.4: one GenKey 127.85 ms nominal */
    static const uint8_t present[] = { 0x10, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x49, 0x60, 0x6B };
    for (size_t i = 0; i < sizeof present; i++)
        f->present[present[i]] = true;
    for (int a = 0; a < 128; a++) {
        f->regs[a][2] = f->regs[a][3] = 0xFF;   /* PCA9555 power-on: outputs FFh */
        f->regs[a][6] = f->regs[a][7] = 0xFF;   /* configuration FFh: inputs */
        f->regs[a][0] = f->regs[a][1] = 0xFF;
    }
    /* board C U1 port 1: LIGHTING at DAY (LIGHT_DAY_n low) */
    f->regs[HAL_I2C_C_U1][1] = (uint8_t)~(1u << HAL_EXP_C_LIGHT_DAY_N_BIT);
    /* board B U7: RB_STATUS low */
    f->regs[HAL_I2C_B_U7][0] = (uint8_t)~(1u << HAL_EXP_B_RB_STATUS_BIT);
    memset(f->flash, 0xFF, sizeof f->flash);
    memset(f->key[0], 0x11, 64);
    memset(f->key[1], 0x22, 64);
    memcpy(f->rec, f->key, sizeof f->key);
    f->have_rec = true;
    f->hot_sim = HOT_SIM_1HZ;

    f->ops.bus.ctx = f;
    f->ops.bus.i2c_write = bus_write;
    f->ops.bus.i2c_read = bus_read;
    f->ops.zer.ctx = f;
    f->ops.zer.now_ms = fz_now;
    f->ops.zer.genkey_create = se_create;
    f->ops.zer.genkey_public = se_public;
    f->ops.zer.recorded_pub = se_rec;
    f->ops.zer.arm_slot_cut = arm_cut;
    f->ops.zer.tell_modules_drop_keys = tell;
    f->ops.zer.flash_read = fl_read;
    f->ops.zer.flash_program = fl_prog;
    f->ops.zer.flash_erase = fl_erase;
    f->ops.zer.flash_size = sizeof f->flash;
    f->ops.epd.ctx = f;
    f->ops.epd.send = epd_send;

    /* idle inputs: every switch released or open, EMCON released, the rail present, no bridge */
    f->in.test_sw = f->in.sos_sw = f->in.zeroize_sw = true;
    f->in.emcon_rd = true;
    f->in.exp_int = true;
    f->in.pi_shdn_req = true;
    f->in.rail_mv = 2500;
    f->in.br.display_slot = -1;
    f->in.br.soc_pct = -1;
}

void fx_init(fx_t *f, bool zer_closed, const bool held[3])
{
    static const bool none[3] = { false, false, false };
    bool drive[3];
    f->in.zeroize_sw = !zer_closed;
    panel_init(&f->p, &f->ops, f->now, zer_closed, held ? held : none, drive);
}

static void hot_line(fx_t *f)
{
    bool lvl = true;
    switch (f->hot_sim) {
    case HOT_SIM_1HZ: lvl = (f->now / 1000u) & 1u; break;     /* one edge a second */
    case HOT_SIM_5HZ: lvl = (f->now / 200u) & 1u; break;      /* five edges a second */
    case HOT_SIM_LOW: lvl = false; break;
    default: lvl = true; break;
    }
    uint8_t *in1 = &f->regs[HAL_I2C_A_U27][1];
    uint8_t before = *in1;
    if (lvl)
        *in1 |= (uint8_t)(1u << HAL_EXP_A_HOT_R1_BIT);
    else
        *in1 &= (uint8_t)~(1u << HAL_EXP_A_HOT_R1_BIT);
    f->in.exp_int = before == *in1;          /* a change raises EXP_INT (low) */
}

void fx_tick(fx_t *f)
{
    hot_line(f);
    f->in.epd_busy = f->now < f->busy_until;
    panel_tick(&f->p, f->now, &f->in, &f->out);
}

void fx_run(fx_t *f, ms_t ms)
{
    ms_t end = f->now + ms;
    while (f->now < end) {
        fx_tick(f);
        f->now++;
    }
}

void fx_run_hb(fx_t *f, ms_t ms, const bool toggling[3])
{
    ms_t end = f->now + ms;
    while (f->now < end) {
        for (unsigned i = 0; i < 3; i++)
            if (toggling[i])
                f->in.hb[i] = (f->now / 500u) & 1u;     /* a 1 Hz square wave */
        fx_tick(f);
        f->now++;
    }
}

void fx_boot(fx_t *f)
{
    fx_new(f);
    fx_init(f, false, NULL);
    for (int i = 0; i < 10000 && f->p.boot != BOOT_RUN; i++) {
        fx_tick(f);
        f->now++;
    }
}

int fx_find_write(const fx_t *f, uint8_t addr, uint8_t reg, unsigned from)
{
    for (unsigned i = from; i < f->n_wr; i++)
        if (f->wr[i].addr == addr && f->wr[i].reg == reg)
            return (int)i;
    return -1;
}
