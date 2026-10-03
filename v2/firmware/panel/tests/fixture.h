/* fixture.h: the host test fixture: a fake kit bus with the seven PCA9555, a fake ATECC608B, a fake flash journal,
 * a fake e-paper BUSY line and a clock. Host only. */
#ifndef PANEL_FIXTURE_H
#define PANEL_FIXTURE_H

#include <stdio.h>
#include <string.h>

#include "panel.h"

/* ---- the tiny test runner ---- */
extern int test_failed;
#define CHECK(c) do { if (!(c)) { printf("    FAIL %s:%d: %s\n", __FILE__, __LINE__, #c); test_failed = 1; return; } } while (0)

/* ---- the fake world ---- */
#define FX_LOG 4096
enum hot_sim { HOT_SIM_1HZ = 0, HOT_SIM_5HZ, HOT_SIM_LOW, HOT_SIM_HIGH, HOT_SIM_NONE };

typedef struct {
    uint8_t addr, reg, val;
    unsigned seq;
} fx_wr_t;

typedef struct fx {
    panel_t     p;
    panel_ops_t ops;
    panel_in_t  in;
    panel_out_t out;
    ms_t        now;

    /* bus */
    uint8_t  regs[128][8];
    bool     present[128];
    fx_wr_t  wr[FX_LOG];
    unsigned n_wr, seq;
    unsigned n_reads[128];
    bool     bus_fail;
    int      hot_sim;
    unsigned cmd_byte_writes_u27;    /* pointer-only writes after a read of U27 */

    /* secure element */
    uint8_t  key[2][64];
    uint8_t  rec[2][64];
    bool     have_rec;
    unsigned key_ctr;
    int      fail_create[2];         /* the next n creates on a slot fail */
    int      fail_public[2];
    bool     se_dead;
    ms_t     cmd_ms;                 /* the time one GenKey takes */
    char     log[512];               /* "A C0 C1 V0 V1 J1 J2 T" */
    unsigned n_cmds;
    ms_t     alarm_at;
    bool     told;
    ms_t     told_at;

    /* flash */
    uint8_t  flash[4096];
    int      flash_fail_program;

    /* e-paper */
    ms_t     busy_until;
    uint8_t  epd_pages[64];
    bool     epd_full[64];
    ms_t     epd_at[64];
    unsigned n_epd;
} fx_t;

void fx_new(fx_t *f);
void fx_init(fx_t *f, bool zer_closed, const bool held[3]);
void fx_tick(fx_t *f);                       /* one tick at f->now */
void fx_run(fx_t *f, ms_t ms);               /* ticks every millisecond */
void fx_boot(fx_t *f);                       /* fx_new + fx_init + run until BOOT_RUN with a 1 Hz HOT-R1 */
void fx_hb(fx_t *f, unsigned slot, bool toggling);
void fx_run_hb(fx_t *f, ms_t ms, const bool toggling[3]);  /* run with each slot's line toggling at 1 Hz or flat */
int  fx_find_write(const fx_t *f, uint8_t addr, uint8_t reg, unsigned from);
void fx_log(fx_t *f, const char *s);

#endif
