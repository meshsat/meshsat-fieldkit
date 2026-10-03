/*
 * zeroize.c: the wipe journal and the crypto-erase sequence of feasibility/ZEROIZE.md sections 3.4 and 3.5
 * (owner ruling D-03, decision 30; HW-FW-CONTRACT.md FW-C04). Pure logic over injected operations: the secure element
 * (ATECC608B at 0x60, GenKey), the flash journal region, the clock, the slot-cut alarm and the watchdog.
 *
 * Prototype for an unbuilt board: the ATECC608B behaviour this rests on is a desk result; Z-EXP-A to Z-EXP-C are owed.
 */
#include <string.h>

#include "panel.h"

#define ZJ_REC 16u
#define ZJ_MAX_CREATES 10u          /* ZER s.3.4 step 7: up to 10 GenKey mode 0x04 tries per slot in all */
#define ZJ_TIMED_COMMANDS 6u        /* ZER s.3.4 step 3: at most 6 GenKey commands in the timed phase */
#define ZJ_UNTIMED_DEADLINE 0xFFFFFFFFu

static uint32_t crc32_bytes(const uint8_t *b, unsigned n)
{
    uint32_t c = 0xFFFFFFFFu;
    for (unsigned i = 0; i < n; i++) {
        c ^= b[i];
        for (int k = 0; k < 8; k++)
            c = (c >> 1) ^ (0xEDB88320u & (0u - (c & 1u)));
    }
    return ~c;
}

static bool all_ff(const uint8_t *b, unsigned n)
{
    for (unsigned i = 0; i < n; i++)
        if (b[i] != 0xFF)
            return false;
    return true;
}

/* Scan the journal. The last record decides; a torn or unreadable record reads PENDING (invariant I3). */
uint8_t panel_zj_scan(panel_t *p)
{
    const panel_zer_ops_t *z = &p->ops->zer;
    uint8_t state = ZJ_NONE;
    uint8_t rec[ZJ_REC];
    uint32_t off = 0;
    p->zer.journal_seq = 0;
    for (; off + ZJ_REC <= z->flash_size; off += ZJ_REC) {
        if (z->flash_read(z->ctx, off, rec, ZJ_REC) != 0) {
            state = ZJ_PENDING;                  /* unreadable: fail toward the wipe */
            continue;
        }
        if (all_ff(rec, ZJ_REC))
            break;
        uint32_t crc = (uint32_t)rec[12] | (uint32_t)rec[13] << 8 | (uint32_t)rec[14] << 16 | (uint32_t)rec[15] << 24;
        bool ok = rec[0] == 'Z' && rec[1] == 'J' && (uint8_t)(rec[2] ^ rec[3]) == 0xFF &&
                  (rec[2] == ZJ_PENDING || rec[2] == ZJ_DONE) && crc == crc32_bytes(rec, 12);
        if (!ok) {
            state = ZJ_PENDING;                  /* torn */
            continue;
        }
        state = rec[2];
        p->zer.journal_seq = (uint32_t)rec[4] | (uint32_t)rec[5] << 8 | (uint32_t)rec[6] << 16 | (uint32_t)rec[7] << 24;
    }
    p->zer.journal_off = off;
    return state;
}

/* Append one record: one page program, the region pre-erased (ZER s.3.4 step 1: no sector erase in this path). */
int panel_zj_append(panel_t *p, uint8_t state)
{
    const panel_zer_ops_t *z = &p->ops->zer;
    if (p->zer.journal_off + ZJ_REC > z->flash_size)
        return -1;                               /* full: housekeeping at boot keeps this from happening */
    uint8_t rec[ZJ_REC];
    uint32_t seq = ++p->zer.journal_seq;
    memset(rec, 0, sizeof rec);
    rec[0] = 'Z';
    rec[1] = 'J';
    rec[2] = state;
    rec[3] = (uint8_t)~state;
    rec[4] = (uint8_t)seq;
    rec[5] = (uint8_t)(seq >> 8);
    rec[6] = (uint8_t)(seq >> 16);
    rec[7] = (uint8_t)(seq >> 24);
    uint32_t crc = crc32_bytes(rec, 12);
    rec[12] = (uint8_t)crc;
    rec[13] = (uint8_t)(crc >> 8);
    rec[14] = (uint8_t)(crc >> 16);
    rec[15] = (uint8_t)(crc >> 24);
    int r = z->flash_program(z->ctx, p->zer.journal_off, rec, ZJ_REC);
    p->zer.journal_off += ZJ_REC;                /* a failed program leaves a torn record: it reads PENDING (I3) */
    return r;
}

static ms_t zn(panel_t *p) { return p->ops->zer.now_ms(p->ops->zer.ctx); }
static void zfeed(panel_t *p)
{
    if (p->ops->zer.feed_watchdog)
        p->ops->zer.feed_watchdog(p->ops->zer.ctx);
}

/* One slot's verification: GenKey mode 0x00 equals the key the create returned and differs from P_x0 (step 3). */
static bool verify_slot(panel_t *p, uint8_t s, const uint8_t created[64], ms_t deadline, bool *cmd_error)
{
    const panel_zer_ops_t *z = &p->ops->zer;
    uint8_t pub[64], rec[64];
    *cmd_error = false;
    if (z->genkey_public(z->ctx, s, pub, deadline) != 0) {
        *cmd_error = true;
        return false;
    }
    bool have_rec = z->recorded_pub(z->ctx, s, rec);
    if (memcmp(pub, created, 64) != 0)
        return false;
    if (have_rec && memcmp(pub, rec, 64) == 0)
        return false;
    return true;
}

static void reset_request(panel_t *p)
{
    p->zer.creates_done[0] = p->zer.creates_done[1] = 0;
    p->zer.verified[0] = p->zer.verified[1] = false;
}

/*
 * Steps 0 to 5 of ZER s.3.4, run at the 5 s commit point. hold_end is the end of the hold. Returns ZER_DONE or
 * ZER_INCOMPLETE. Step 6 (the slot cut) and step 7 (the untimed retries) are the caller's (panel_core.c).
 */
uint8_t panel_zer_wipe_timed(panel_t *p, ms_t hold_end)
{
    const panel_zer_ops_t *z = &p->ops->zer;
    const ms_t deadline = hold_end + PANEL_ZER_DEADLINE_MS;          /* the deadline D */
    uint8_t created[2][64];
    bool create_ok[2] = { false, false };
    bool need_create[2] = { false, false };
    unsigned commands = 0;

    reset_request(p);
    z->arm_slot_cut(z->ctx, hold_end + PANEL_ZER_KILL_AFTER_MS);     /* step 0: I4 */
    panel_zj_append(p, ZJ_PENDING);                                  /* step 1 */

    /* step 2: C0 then C1, both before any retry */
    for (uint8_t s = 0; s < 2; s++) {
        if (zn(p) >= deadline)
            break;
        create_ok[s] = z->genkey_create(z->ctx, s, created[s], deadline) == 0;
        p->zer.creates_done[s]++;
        commands++;
        zfeed(p);
    }
    /* step 3: the nominal verifications */
    for (uint8_t s = 0; s < 2; s++) {
        if (!create_ok[s]) {
            need_create[s] = true;
            continue;
        }
        if (zn(p) >= deadline || commands >= ZJ_TIMED_COMMANDS)
            break;
        bool err;
        p->zer.verified[s] = verify_slot(p, s, created[s], deadline, &err);
        commands++;
        need_create[s] = !p->zer.verified[s] && !err;  /* a mismatch re-runs the create; an error re-verifies */
        zfeed(p);
    }
    /* the two shared retries, round robin, never past D and never more than 6 commands in all */
    for (unsigned guard = 0; guard < 8; guard++) {
        bool progressed = false;
        for (uint8_t s = 0; s < 2; s++) {
            if (p->zer.verified[s])
                continue;
            if (zn(p) >= deadline || commands >= ZJ_TIMED_COMMANDS)
                break;
            if (need_create[s]) {
                create_ok[s] = z->genkey_create(z->ctx, s, created[s], deadline) == 0;
                p->zer.creates_done[s]++;
                need_create[s] = !create_ok[s];
            } else {
                bool err;
                p->zer.verified[s] = verify_slot(p, s, created[s], deadline, &err);
                need_create[s] = !p->zer.verified[s] && !err;
            }
            commands++;
            progressed = true;
            zfeed(p);
        }
        if (!progressed)
            break;
    }
    /* step 4: every verification above finished before D, because the HAL fails any bus operation past D */
    bool done = p->zer.verified[0] && p->zer.verified[1];
    if (done)
        panel_zj_append(p, ZJ_DONE);                                 /* otherwise PENDING stays */
    z->tell_modules_drop_keys(z->ctx);                               /* step 5: I5, whatever the bus did */
    p->zer.last_result = done ? ZER_DONE : ZER_INCOMPLETE;
    return p->zer.last_result;
}

/* Step 7 (and the boot table's runs): untimed, up to 10 creates per slot in all, each followed by its verification. */
uint8_t panel_zer_wipe_untimed(panel_t *p)
{
    const panel_zer_ops_t *z = &p->ops->zer;
    uint8_t created[64];
    for (uint8_t s = 0; s < 2; s++) {
        while (!p->zer.verified[s] && p->zer.creates_done[s] < ZJ_MAX_CREATES) {
            int r = z->genkey_create(z->ctx, s, created, ZJ_UNTIMED_DEADLINE);
            p->zer.creates_done[s]++;
            zfeed(p);
            if (r != 0)
                continue;
            bool err;
            p->zer.verified[s] = verify_slot(p, s, created, ZJ_UNTIMED_DEADLINE, &err);
            if (!p->zer.verified[s] && err)       /* one more read of the public key before another create */
                p->zer.verified[s] = verify_slot(p, s, created, ZJ_UNTIMED_DEADLINE, &err);
            zfeed(p);
        }
    }
    bool done = p->zer.verified[0] && p->zer.verified[1];
    if (done)
        panel_zj_append(p, ZJ_DONE);
    p->zer.last_result = done ? ZER_DONE : ZER_INCOMPLETE;
    return p->zer.last_result;
}

/*
 * The boot table of ZER s.3.5, run before any SLOT_EN is raised. Returns:
 *   ZER_DONE        the wipe ran to DONE (toggle closed: slots stay off while it stays closed; toggle open: re-armed)
 *   ZER_INCOMPLETE  a wipe was due and could not be proven: slots stay off, retried at every boot
 *   ZER_REARMED     no wipe due, the KEKs differ from the recorded keys: slots may power (recovery state)
 *   ZER_SE_ABSENT   no wipe due, the SE does not answer: normal boot without the SE (MASTER WARN, e-paper)
 *   ZER_NORMAL      no wipe due, the keys equal the recorded ones
 */
uint8_t panel_zer_boot(panel_t *p, bool toggle_closed, bool *slots_may_power)
{
    const panel_zer_ops_t *z = &p->ops->zer;
    uint8_t js = panel_zj_scan(p);
    reset_request(p);
    if (toggle_closed || js == ZJ_PENDING) {
        if (js != ZJ_PENDING)
            panel_zj_append(p, ZJ_PENDING);                          /* step 1 (I1: a record never skips the wipe) */
        uint8_t r = panel_zer_wipe_untimed(p);                       /* steps 2 to 4 and 7 */
        *slots_may_power = !toggle_closed && r == ZER_DONE;
        return r;
    }
    /* housekeeping: erase a journal over half full while no wipe is due (never in the wipe's path) */
    if (p->zer.journal_off > z->flash_size / 2u && z->flash_erase(z->ctx) == 0)
        p->zer.journal_off = 0;
    *slots_may_power = true;
    bool differ = false;
    for (uint8_t s = 0; s < 2; s++) {
        uint8_t pub[64], rec[64];
        if (z->genkey_public(z->ctx, s, pub, ZJ_UNTIMED_DEADLINE) != 0) {
            p->zer.se_absent = true;
            p->se_probe_at = z->now_ms(z->ctx);
            return p->zer.last_result = ZER_SE_ABSENT;
        }
        if (!z->recorded_pub(z->ctx, s, rec) || memcmp(pub, rec, 64) != 0)
            differ = true;
    }
    return p->zer.last_result = differ ? ZER_REARMED : ZER_NORMAL;
}
