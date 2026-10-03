/*
 * main_rp2040.c: the panel controller's main loop on the RP2040 (pico-sdk). NOT BUILT HERE (no arm toolchain on this
 * host); prototype firmware for an unbuilt board.
 *
 * Order (FW-C01, FW-C02): PI_KILL low and PI_SHDN_REQ released first; ZEROIZE_SW and the SLOT_EN pads read as inputs;
 * the core decides each SLOT_EN's first level (all low with the toggle closed or a wipe pending); the watchdog; then
 * the 1 ms loop, in which the core runs the rest of the boot order (the wipe table, the expanders, the charger (owed),
 * HOT-R1, the slots one at a time).
 *
 * Not here, and owed (README.md section 4): the USB device and the bridge protocol (MESHSAT-837, wire format not
 * defined), the e-paper's command layer, the charger's registers (FW-A rows), the secure element's command layer
 * (CryptoAuthLib, not vendored), the VEML7700 and TMP117 reads.
 */
#include <stdbool.h>

#include "hal.h"
#include "panel.h"

void hal_init_rest(void);

static panel_t P;

/* FW-K04: after a failed transfer, a held SDA is released by nine SCL pulses and a STOP, and the event is logged */
static void bb_scl(void *c, bool l) { (void)c; hal_i2c_bitbang_scl(l); }
static bool bb_sda(void *c) { (void)c; return hal_i2c_bitbang_sda_read(); }
static void bb_stop(void *c) { (void)c; hal_i2c_bitbang_stop(); }
static void bb_delay(void *c, unsigned us) { (void)c; hal_delay_us(us); }
static const panel_bitbang_t BB = { 0, bb_scl, bb_sda, bb_stop, bb_delay };

static int recover_if_held(int r)
{
    if (r == 0)
        return 0;
    hal_i2c_bitbang_begin();
    if (!hal_i2c_bitbang_sda_read()) {
        int pulses = panel_bus_recover(&BB);
        panel_ev_report(&P, EV_I2C_RECOVERED, (uint8_t)(pulses < 0 ? 0xFF : pulses), hal_now_ms());
    }
    hal_i2c_bitbang_end();
    return r;
}

static int bus_write(void *ctx, uint8_t addr, const uint8_t *buf, unsigned len)
{
    (void)ctx;
    return recover_if_held(hal_i2c_write(addr, buf, len, hal_now_ms() + HAL_I2C_OP_TIMEOUT_MS));
}

static int bus_read(void *ctx, uint8_t addr, uint8_t reg, uint8_t *buf, unsigned len)
{
    (void)ctx;
    ms_t d = hal_now_ms() + HAL_I2C_OP_TIMEOUT_MS;
    if (hal_i2c_write(addr, &reg, 1, d) != 0)
        return recover_if_held(-1);
    return recover_if_held(hal_i2c_read(addr, buf, len, d));
}

static ms_t z_now(void *ctx) { (void)ctx; return hal_now_ms(); }

/* The secure element's two GenKey modes go through CryptoAuthLib (atcab_genkey, atcab_get_pubkey) with the panel's
 * six-function HAL bounded as ZEROIZE.md 3.4 (a) and (b) set out. The library is not vendored in this tree: OWED. Until
 * it is, every SE call fails, so the boot table takes "the SE does not answer" (normal boot without the SE, MASTER WARN)
 * and a ZEROIZE commit ends INCOMPLETE with the slots held off: fail secure. */
static int se_create(void *ctx, uint8_t slot, uint8_t pub[64], ms_t deadline)
{
    (void)ctx; (void)slot; (void)pub; (void)deadline;
    return -1;
}
static int se_public(void *ctx, uint8_t slot, uint8_t pub[64], ms_t deadline)
{
    (void)ctx; (void)slot; (void)pub; (void)deadline;
    return -1;
}
static bool se_recorded(void *ctx, uint8_t slot, uint8_t pub[64])
{
    (void)ctx; (void)slot; (void)pub;
    return false;                            /* P_A0 and P_B0 are written at enrolment (ZEROIZE.md 3.3): owed */
}
static void arm_cut(void *ctx, ms_t at) { (void)ctx; hal_arm_slot_cut_alarm(at); }
static void tell_modules(void *ctx) { (void)ctx; /* over the bridge protocol: owed (F-02) */ }
static void feed(void *ctx) { (void)ctx; hal_watchdog_feed(); }
static int fl_read(void *ctx, uint32_t off, uint8_t *buf, unsigned len) { (void)ctx; return hal_journal_read(off, buf, len); }
static int fl_prog(void *ctx, uint32_t off, const uint8_t *buf, unsigned len) { (void)ctx; return hal_journal_program(off, buf, len); }
static int fl_erase(void *ctx) { (void)ctx; return hal_journal_erase(); }
static void epd_send(void *ctx, uint8_t page, bool full) { (void)ctx; (void)page; (void)full; /* owed */ }
static int ss_read(void *ctx, uint32_t off, uint8_t *buf, unsigned len) { (void)ctx; return hal_slotstore_read(off, buf, len); }
static int ss_prog(void *ctx, uint32_t off, const uint8_t *buf, unsigned len) { (void)ctx; return hal_slotstore_program(off, buf, len); }
static int ss_erase(void *ctx) { (void)ctx; return hal_slotstore_erase(); }

static const panel_ops_t OPS = {
    .bus = { 0, bus_write, bus_read },
    .zer = { 0, z_now, se_create, se_public, se_recorded, arm_cut, tell_modules, feed, fl_read, fl_prog, fl_erase,
             8192u },
    .epd = { 0, epd_send },
    .slots = { 0, ss_read, ss_prog, ss_erase, 4096u },
};

int main(void)
{
    hal_init_pins_first();                                   /* FW-C01 steps 1 and 2 */
    bool zer_closed = !hal_gpio_get(HAL_GPIO_ZEROIZE_SW);    /* step 3: the level, at the first instruction */
    bool held[3], drive[3];
    hal_slot_en_read(held);                                  /* FW-C02 */
    panel_init(&P, &OPS, hal_now_ms(), zer_closed, held, hal_reset_was_power_on(), drive);   /* FW-C05 (F-15) */
    hal_slot_en_drive_initial(drive);
    panel_ev_report(&P, EV_BOOT, (uint8_t)hal_reset_reason(), hal_now_ms());   /* FW-C02: the boot reason logged */
    hal_init_rest();
    hal_watchdog_start(PANEL_WATCHDOG_MS);

    panel_in_t in = { 0 };
    panel_out_t out;
    in.br.display_slot = -1;
    in.br.soc_pct = -1;
    ms_t last = hal_now_ms();
    for (;;) {
        ms_t now = hal_now_ms();
        if (now == last) {
            continue;
        }
        last = now;
        in.test_sw = hal_gpio_get(HAL_GPIO_TEST_SW);
        in.sos_sw = hal_gpio_get(HAL_GPIO_SOS_SW);
        in.zeroize_sw = hal_gpio_get(HAL_GPIO_ZEROIZE_SW);
        in.emcon_rd = hal_gpio_get(HAL_GPIO_EMCON_RD_R);
        in.tr_aprs = hal_gpio_get(HAL_GPIO_TR_APRS);
        in.exp_int = hal_gpio_get(HAL_GPIO_EXP_INT);
        in.hb[0] = hal_gpio_get(HAL_GPIO_HB1);
        in.hb[1] = hal_gpio_get(HAL_GPIO_HB2);
        in.hb[2] = hal_gpio_get(HAL_GPIO_HB3);
        in.pi_shdn_req = hal_gpio_get(HAL_GPIO_PI_SHDN_REQ);
        in.pi_button = false;                                /* HAL_PI_BUTTON_WIRED 0: finding F-01 */
        in.epd_busy = hal_gpio_get(HAL_GPIO_EPD_BUSY);
        in.rail_mv = hal_rail_sense_mv();

        panel_tick(&P, now, &in, &out);

        hal_gpio_put(HAL_GPIO_PI_KILL, out.pi_kill);
        hal_pi_shdn_req_assert(out.pi_shdn_assert);
        hal_gpio_put(HAL_GPIO_SLOT_EN1, out.slot_en[0]);
        hal_gpio_put(HAL_GPIO_SLOT_EN2, out.slot_en[1]);
        hal_gpio_put(HAL_GPIO_SLOT_EN3, out.slot_en[2]);
        hal_gpio_put(HAL_GPIO_HDMI_SEL1, out.hdmi_sel1);
        hal_gpio_put(HAL_GPIO_HDMI_SEL2, out.hdmi_sel2);
        hal_gpio_put(HAL_GPIO_SHORE_INHIBIT, out.shore_inhibit);
        hal_gpio_put(HAL_GPIO_EPD_PWR_n, !out.epd_power);
        hal_gpio_put(HAL_GPIO_LED_STAT, out.led_stat);
        hal_pwm_set_permille(HAL_GPIO_PANEL_PWM, out.pwm_permille);
        hal_pwm_set_permille(HAL_GPIO_PWM1, out.sounder ? 1000u : 0u);
        hal_watchdog_feed();
    }
}
