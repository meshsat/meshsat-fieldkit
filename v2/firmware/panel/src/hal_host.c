/*
 * hal_host.c: the host stub of hal.h for the unit tests. It keeps pin levels in memory and refuses what the target
 * implementation must never do: an output on GPIO21 (EMCON_RD_R, FW-C07) and a high drive on PI_SHDN_REQ (FW-A10).
 */
#include <string.h>

#include "hal.h"

int hal_host_refused;
static bool levels[30];
static ms_t host_now;

void hal_init_pins_first(void)
{
    levels[HAL_GPIO_PI_KILL] = false;
    levels[HAL_GPIO_PI_SHDN_REQ] = true;
}

bool hal_gpio_get(enum hal_gpio g) { return levels[g]; }

void hal_gpio_put(enum hal_gpio g, bool level)
{
    if (g == HAL_GPIO_EMCON_RD_R || g == HAL_GPIO_ZEROIZE_SW || (g == HAL_GPIO_PI_SHDN_REQ && level)) {
        hal_host_refused++;
        return;
    }
    levels[g] = level;
}

void hal_slot_en_read(bool held[3])
{
    for (int i = 0; i < 3; i++)
        held[i] = levels[HAL_GPIO_SLOT_EN1 + i];
}

void hal_slot_en_drive_initial(const bool level[3])
{
    for (int i = 0; i < 3; i++)
        levels[HAL_GPIO_SLOT_EN1 + i] = level[i];
}

int hal_reboot_to_bootsel(void)
{
    for (int i = 0; i < 3; i++)
        if (levels[HAL_GPIO_SLOT_EN1 + i])
            return -1;
    return 0;
}

void hal_pi_shdn_req_assert(bool assert) { levels[HAL_GPIO_PI_SHDN_REQ] = !assert; }
void hal_pwm_set_permille(enum hal_gpio g, uint16_t permille) { levels[g] = permille > 0; }
uint16_t hal_rail_sense_mv(void) { return 2500; }
ms_t hal_now_ms(void) { return host_now++; }
int hal_i2c_write(uint8_t addr, const uint8_t *buf, unsigned len, ms_t deadline_ms) { (void)addr; (void)buf; (void)len; (void)deadline_ms; return 0; }
int hal_i2c_read(uint8_t addr, uint8_t *buf, unsigned len, ms_t deadline_ms) { (void)addr; (void)deadline_ms; memset(buf, 0xFF, len); return 0; }
void hal_i2c_bitbang_begin(void) {}
void hal_i2c_bitbang_scl(bool level) { (void)level; }
bool hal_i2c_bitbang_sda_read(void) { return true; }
void hal_i2c_bitbang_stop(void) {}
void hal_i2c_bitbang_end(void) {}
void hal_delay_us(unsigned us) { (void)us; }
void hal_watchdog_start(ms_t period_ms) { (void)period_ms; }
void hal_watchdog_feed(void) {}
int hal_reset_reason(void) { return 0; }
void hal_arm_slot_cut_alarm(ms_t at_ms) { (void)at_ms; }
void hal_cancel_slot_cut_alarm(void) {}
int hal_journal_read(uint32_t off, uint8_t *buf, unsigned len) { (void)off; memset(buf, 0xFF, len); return 0; }
int hal_journal_program(uint32_t off, const uint8_t *buf, unsigned len) { (void)off; (void)buf; (void)len; return 0; }
int hal_journal_erase(void) { return 0; }
