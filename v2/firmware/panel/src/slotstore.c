/*
 * slotstore.c: each slot's spent retry and left-off state (HW-FW-CONTRACT.md FW-C05 and FW-C02, record l5r4, finding
 * F-14), kept across a watchdog, RUN or SWD reset and cleared by a power-on reset. Its own flash region beside the wipe
 * journal (SESSION S-37): inside the journal a torn record would read as a pending wipe (ZEROIZE.md invariant I3).
 *
 * Append-only 16-byte records ('S', 'L', three state bytes, their complement, a sequence, a CRC-32). The last valid record
 * wins; a torn or unreadable one is skipped, so a power loss during a write leaves the previous state, at worst one change
 * stale. Pure logic over the injected region. Prototype for an unbuilt board.
 */
#include <string.h>

#include "panel.h"

#define SL_REC 16u

static bool all_ff(const uint8_t *b, unsigned n)
{
    for (unsigned i = 0; i < n; i++)
        if (b[i] != 0xFF)
            return false;
    return true;
}

int panel_slot_store_load(panel_t *p, uint8_t st[3])
{
    const panel_store_ops_t *s = &p->ops->slots;
    uint8_t rec[SL_REC];
    int found = 1;
    uint32_t off = 0;
    memset(st, 0, 3);
    p->slot_store_seq = 0;
    if (!s->read) {
        p->slot_store_off = 0;
        return 1;
    }
    for (; off + SL_REC <= s->size; off += SL_REC) {
        if (s->read(s->ctx, off, rec, SL_REC) != 0)
            continue;                                /* unreadable: the previous record stands */
        if (all_ff(rec, SL_REC))
            break;
        uint32_t crc = (uint32_t)rec[12] | (uint32_t)rec[13] << 8 | (uint32_t)rec[14] << 16 | (uint32_t)rec[15] << 24;
        if (rec[0] != 'S' || rec[1] != 'L' || (uint8_t)(rec[2] ^ rec[3] ^ rec[4] ^ rec[5]) != 0xFF ||
            crc != panel_crc32(rec, 12))
            continue;                                /* torn: the previous record stands */
        memcpy(st, rec + 2, 3);
        p->slot_store_seq = (uint32_t)rec[6] | (uint32_t)rec[7] << 8 | (uint32_t)rec[8] << 16 | (uint32_t)rec[9] << 24;
        found = 0;
    }
    p->slot_store_off = off;
    return found;
}

int panel_slot_store_save(panel_t *p, const uint8_t st[3])
{
    const panel_store_ops_t *s = &p->ops->slots;
    if (!s->program)
        return -1;
    if (p->slot_store_off + SL_REC > s->size) {
        if (s->erase(s->ctx) != 0)                   /* full: erase, then the current state is the first record */
            return -1;
        p->slot_store_off = 0;
    }
    uint8_t rec[SL_REC];
    uint32_t seq = ++p->slot_store_seq;
    memset(rec, 0, sizeof rec);
    rec[0] = 'S';
    rec[1] = 'L';
    memcpy(rec + 2, st, 3);
    rec[5] = (uint8_t)~(st[0] ^ st[1] ^ st[2]);
    rec[6] = (uint8_t)seq;
    rec[7] = (uint8_t)(seq >> 8);
    rec[8] = (uint8_t)(seq >> 16);
    rec[9] = (uint8_t)(seq >> 24);
    uint32_t crc = panel_crc32(rec, 12);
    rec[12] = (uint8_t)crc;
    rec[13] = (uint8_t)(crc >> 8);
    rec[14] = (uint8_t)(crc >> 16);
    rec[15] = (uint8_t)(crc >> 24);
    int r = s->program(s->ctx, p->slot_store_off, rec, SL_REC);
    p->slot_store_off += SL_REC;
    return r;
}
