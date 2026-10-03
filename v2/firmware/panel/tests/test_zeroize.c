/* test_zeroize.c: ZEROIZE (P s.6, s.9; FW-C04; feasibility/ZEROIZE.md 3.4 and 3.5). */
#include "fixture.h"

static void run_slots_up(fx_t *x)
{
    static const bool all[3] = { true, true, true };
    fx_run_hb(x, 5000, all);
}

void t_zeroize_abort_inside_5s(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->log[0] = 0;
    x->n_cmds = 0;
    x->in.zeroize_sw = false;
    fx_run(x, 4900);
    CHECK(x->p.zer.mode == ZM_ARMING);
    CHECK(x->out.leds & LED_BIT(LED_MWARN) || x->p.red_active);   /* MASTER WARN flashes while armed */
    x->in.zeroize_sw = true;
    fx_run(x, 40);
    CHECK(x->p.zer.mode == ZM_ARMED_IDLE);
    CHECK(x->n_cmds == 0 && x->log[0] == 0);       /* nothing reached the secure element */
    fx_run(x, 600);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_ZEROIZE_ABORTED);
}

void t_zeroize_commit_sequence(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    run_slots_up(x);
    CHECK(x->out.slot_en[0] && x->out.slot_en[1] && x->out.slot_en[2]);
    x->log[0] = 0;
    x->in.zeroize_sw = false;
    ms_t closed = x->now;
    static const bool all[3] = { true, true, true };
    while (x->p.zer.mode == ZM_ARMING || x->p.zer.mode == ZM_ARMED_IDLE)
        fx_run_hb(x, 1, all);
    ms_t hold_end = x->p.zer.hold_end;
    CHECK(hold_end - closed >= 5000 && hold_end - closed <= 5040);
    /* step 0 first, then the PENDING record, then C0 C1 V0 V1, DONE, then the modules told */
    CHECK(strcmp(x->log, "A J1 C0 C1 V0 V1 J2 T") == 0);
    CHECK(x->alarm_at == hold_end + 3000);
    CHECK(x->told_at <= hold_end + 1504);          /* step 5 by 1.504 s */
    CHECK(panel_zj_scan(&x->p) == ZJ_DONE);
    /* step 6: the modules have not confirmed; the slots go at the alarm */
    while (x->now < hold_end + 2900)
        fx_run_hb(x, 1, all);
    CHECK(x->out.slot_en[0]);
    while (x->now < hold_end + 3001)
        fx_run_hb(x, 1, all);
    CHECK(!x->out.slot_en[0] && !x->out.slot_en[1] && !x->out.slot_en[2]);
    CHECK(x->p.zer.mode == ZM_COMPLETE);
    /* step 8: the sounder 3 s, MASTER WARN steady, the e-paper fully refreshed to ZEROIZED */
    unsigned snd = 0, warn = 0;
    for (int i = 0; i < 3200; i++) {
        fx_run(x, 1);
        snd += x->out.sounder;
        warn += (x->out.leds >> LED_MWARN) & 1u;
    }
    CHECK(snd >= 2990 && snd <= 3001);
    CHECK(warn == 3200);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_ZEROIZED && x->epd_full[x->n_epd - 1]);
    /* the slots stay off while the toggle stays closed */
    fx_run(x, 20000);
    CHECK(!x->out.slot_en[0] && !x->out.slot_en[1] && !x->out.slot_en[2]);
}

void t_zeroize_confirm_cuts_early(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    run_slots_up(x);
    x->in.br.alive = true;
    x->in.zeroize_sw = false;
    static const bool all[3] = { true, true, true };
    while (x->p.zer.mode != ZM_WIPING_WAIT)
        fx_run_hb(x, 1, all);
    x->in.br.modules_dropped_keys = true;          /* every running module confirmed */
    fx_run_hb(x, 2, all);
    CHECK(!x->out.slot_en[0] && !x->out.slot_en[1] && !x->out.slot_en[2]);
    CHECK(x->now < x->p.zer.hold_end + 3000);
}

void t_zeroize_retry_policy(void)
{
    /* the timed phase: at most 6 GenKey commands, no retry before C0 and C1, nothing after D */
    fx_t F, *x = &F;
    fx_boot(x);
    x->log[0] = 0;
    x->fail_create[0] = 1;                          /* C0 fails once */
    x->n_cmds = 0;
    uint8_t r = panel_zer_wipe_timed(&x->p, x->now);
    CHECK(strncmp(x->log, "A J1 C0 C1", 10) == 0);  /* C1 before any retry */
    CHECK(r == ZER_DONE);
    CHECK(x->n_cmds <= 6);

    fx_t G, *y = &G;
    fx_boot(y);
    y->fail_create[0] = 5;
    y->fail_create[1] = 5;
    y->n_cmds = 0;
    r = panel_zer_wipe_timed(&y->p, y->now);
    CHECK(r == ZER_INCOMPLETE && y->n_cmds <= 6);
    CHECK(panel_zj_scan(&y->p) == ZJ_PENDING);      /* PENDING stays */
    /* step 7: untimed, up to 10 creates per slot in all */
    y->n_cmds = 0;
    r = panel_zer_wipe_untimed(&y->p);
    CHECK(r == ZER_DONE);
    CHECK(y->p.zer.creates_done[0] <= 10 && y->p.zer.creates_done[1] <= 10);
    CHECK(panel_zj_scan(&y->p) == ZJ_DONE);

    /* the deadline D: a part that answers slowly stops at 1.5 s */
    fx_t H, *z = &H;
    fx_boot(z);
    z->cmd_ms = 600;
    z->n_cmds = 0;
    ms_t t0 = z->now;
    r = panel_zer_wipe_timed(&z->p, t0);
    CHECK(z->told && z->told_at <= t0 + 1500 + 600);
    CHECK(z->n_cmds <= 3);
    (void)r;

    /* a verification equal to the recorded key (the key not destroyed) re-runs the create */
    fx_t K, *k = &K;
    fx_boot(k);
    k->log[0] = 0;
    uint8_t same[64];
    memset(same, 0x41, 64);                         /* the fake's first created key on slot 0 */
    memcpy(k->rec[0], same, 64);
    r = panel_zer_wipe_timed(&k->p, k->now);
    CHECK(strstr(k->log, "V0 V1 C0 V0") != NULL);
    CHECK(r == ZER_DONE);
}

void t_zeroize_incomplete(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    run_slots_up(x);
    x->se_dead = true;
    x->in.zeroize_sw = false;
    static const bool all[3] = { true, true, true };
    for (int i = 0; i < 10000 && x->p.zer.mode != ZM_INCOMPLETE; i++)
        fx_run_hb(x, 1, all);
    CHECK(x->p.zer.mode == ZM_INCOMPLETE);
    CHECK(x->p.zer.creates_done[0] == 10 && x->p.zer.creates_done[1] == 10);   /* step 7's 10 tries */
    CHECK(!x->out.slot_en[0] && !x->out.slot_en[1] && !x->out.slot_en[2]);
    /* MASTER WARN keeps flashing; three 200 ms pulses every 5 s */
    unsigned warn = 0, snd = 0, edges = 0;
    bool last = false;
    for (int i = 0; i < 10000; i++) {
        fx_run(x, 1);
        warn += (x->out.leds >> LED_MWARN) & 1u;
        snd += x->out.sounder;
        edges += x->out.sounder && !last;
        last = x->out.sounder;
    }
    CHECK(warn > 3000 && warn < 7000);
    CHECK(snd >= 1150 && snd <= 1250 && edges == 6);
    CHECK(x->epd_pages[x->n_epd - 1] == PAGE_ZEROIZE_INCOMPLETE);
    /* the toggle returned: still held off (fail secure: a wipe that cannot be proven never computes) */
    x->in.zeroize_sw = true;
    fx_run(x, 20000);
    CHECK(!x->out.slot_en[0] && !x->out.slot_en[1] && !x->out.slot_en[2]);
}

void t_zeroize_rearm_on_return(void)
{
    fx_t F, *x = &F;
    fx_boot(x);
    x->in.zeroize_sw = false;
    for (int i = 0; i < 20000 && x->p.zer.mode != ZM_COMPLETE; i++)
        fx_run(x, 1);
    CHECK(x->p.zer.mode == ZM_COMPLETE);
    fx_run(x, 5000);
    CHECK(!x->out.slot_en[0]);
    x->in.zeroize_sw = true;                        /* re-armed only when the toggle returns */
    fx_run(x, 4000);
    CHECK(x->p.zer.mode == ZM_ARMED_IDLE);
    CHECK(x->out.slot_en[0] && x->out.slot_en[1] && x->out.slot_en[2]);
}

void t_journal_torn_reads_pending(void)
{
    fx_t F, *x = &F;
    fx_new(x);
    fx_init(x, false, NULL);
    CHECK(panel_zj_scan(&x->p) == ZJ_NONE);
    panel_zj_append(&x->p, ZJ_PENDING);
    panel_zj_append(&x->p, ZJ_DONE);
    CHECK(panel_zj_scan(&x->p) == ZJ_DONE);
    x->flash_fail_program = 1;                      /* the next program tears */
    panel_zj_append(&x->p, ZJ_DONE);
    CHECK(panel_zj_scan(&x->p) == ZJ_PENDING);      /* I3: a torn entry reads PENDING */
}

void t_zeroize_boot_table(void)
{
    bool may;
    /* closed at boot: the wipe runs before any slot, the slots stay off while closed */
    fx_t A, *a = &A;
    fx_new(a);
    bool held[3] = { true, true, true };
    bool drive[3];
    panel_init(&a->p, &a->ops, a->now, true, held, drive);
    CHECK(!drive[0] && !drive[1] && !drive[2]);     /* FW-C02: the toggle drives every SLOT_EN low first */
    a->in.zeroize_sw = false;
    for (int i = 0; i < 6000 && a->p.boot != BOOT_RUN; i++) {
        fx_tick(a);
        a->now++;
    }
    CHECK(strstr(a->log, "J1 C0 V0 C1 V1 J2") != NULL);
    CHECK(a->p.zer.mode == ZM_COMPLETE);
    fx_run(a, 5000);
    CHECK(!a->out.slot_en[0] && !a->out.slot_en[1] && !a->out.slot_en[2]);
    /* open with a PENDING record: the wipe runs to DONE, then the slots may power */
    fx_t B, *b = &B;
    fx_new(b);
    fx_init(b, false, NULL);
    panel_zj_append(&b->p, ZJ_PENDING);
    CHECK(panel_zer_boot(&b->p, false, &may) == ZER_DONE && may);
    /* the same with a dead SE: INCOMPLETE, slots off */
    fx_t C, *c = &C;
    fx_new(c);
    fx_init(c, false, NULL);
    panel_zj_append(&c->p, ZJ_PENDING);
    c->se_dead = true;
    CHECK(panel_zer_boot(&c->p, false, &may) == ZER_INCOMPLETE && !may);
    /* no PENDING, keys differ from the recorded ones: re-armed, slots may power */
    fx_t D, *d = &D;
    fx_new(d);
    fx_init(d, false, NULL);
    memset(d->key[1], 0x77, 64);
    CHECK(panel_zer_boot(&d->p, false, &may) == ZER_REARMED && may);
    /* no PENDING, the SE does not answer: normal boot without the SE, MASTER WARN and a page */
    fx_t E, *e = &E;
    fx_new(e);
    e->se_dead = true;
    fx_init(e, false, NULL);
    for (int i = 0; i < 6000 && e->p.boot != BOOT_RUN; i++) {
        fx_tick(e);
        e->now++;
    }
    CHECK(e->p.zer.se_absent);
    fx_run(e, 3000);
    CHECK(e->out.slot_en[0]);
    CHECK(e->p.red_active & 16u);
    CHECK(e->epd_pages[e->n_epd - 1] == PAGE_SE_ABSENT);
    /* normal */
    fx_t G, *g = &G;
    fx_new(g);
    fx_init(g, false, NULL);
    CHECK(panel_zer_boot(&g->p, false, &may) == ZER_NORMAL && may);
}
