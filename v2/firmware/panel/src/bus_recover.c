/*
 * bus_recover.c: the kit bus's recovery (HW-FW-CONTRACT.md FW-K04, V-K02). A target holding SDA low is released by up to
 * nine SCL pulses, then a STOP; the caller logs it. The master never holds SCL low longer than one pulse's half
 * period here (5 us at 100 kHz), far inside FW-K04's 10 ms. Pure logic over a bit-bang interface.
 */
#include "panel.h"

#define RECOVER_PULSES 9
#define HALF_PERIOD_US 5u

/* Returns the number of pulses it took (0 when SDA was already high), or -1 when SDA stays low after nine. */
int panel_bus_recover(const panel_bitbang_t *bb)
{
    int pulses = 0;
    while (!bb->sda(bb->ctx) && pulses < RECOVER_PULSES) {
        bb->scl(bb->ctx, false);
        bb->delay_us(bb->ctx, HALF_PERIOD_US);
        bb->scl(bb->ctx, true);
        bb->delay_us(bb->ctx, HALF_PERIOD_US);
        pulses++;
    }
    bool free_bus = bb->sda(bb->ctx);
    bb->stop(bb->ctx);
    return free_bus ? pulses : -1;
}
