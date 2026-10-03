/*
 * hal_rp2040.c: hal.h on the RP2040 with the pico-sdk (written against pico-sdk 2.3.1's API by name).
 *
 * NOT BUILT HERE: the host this was written on has no arm toolchain and no pico-sdk. Every SDK name below was read
 * from pico-sdk 2.3.1's sources (README.md section 6 lists the files and their sha256); the first build on a machine
 * with the SDK is owed, and so is everything this file does on hardware (README.md section 5, the V-C rows).
 * Prototype firmware for an unbuilt board.
 */
#include <string.h>

#include "hal.h"

#include "hardware/adc.h"
#include "hardware/clocks.h"
#include "hardware/flash.h"
#include "hardware/gpio.h"
#include "hardware/i2c.h"
#include "hardware/irq.h"
#include "hardware/pwm.h"
#include "hardware/resets.h"
#include "hardware/structs/psm.h"
#include "hardware/structs/resets.h"
#include "hardware/structs/sio.h"
#include "hardware/structs/timer.h"
#include "hardware/structs/vreg_and_chip_reset.h"
#include "hardware/sync.h"
#include "hardware/watchdog.h"
#include "pico/bootrom.h"
#include "pico/time.h"

#define KIT_I2C i2c0
#define SLOT_MASK ((1u << HAL_GPIO_SLOT_EN1) | (1u << HAL_GPIO_SLOT_EN2) | (1u << HAL_GPIO_SLOT_EN3))
#define CUT_ALARM 3u                         /* timer alarm 3, TIMER_IRQ_3 */

/* The journal: the top two 4 KiB sectors of U4 (W25Q16JV, 2 MiB). */
#define JOURNAL_SIZE (2u * FLASH_SECTOR_SIZE)
#define JOURNAL_OFF  (PICO_FLASH_SIZE_BYTES - JOURNAL_SIZE)

/*
 * FW-C02 (finding F-03): pico-sdk 2.3.1's runtime_init_early_resets() resets every peripheral but the QSPI bank, the
 * PLLs, USB and SYSCFG on EVERY boot, IO_BANK0 and PADS_BANK0 included (src/rp2_common/pico_runtime_init/
 * runtime_init.c lines 56 to 70), so a panel reset would drop SLOT_EN1..3 whatever the watchdog's scope. The SDK makes
 * the function weak; this one keeps IO_BANK0 and PADS_BANK0 out of the reset, so a driven SLOT_EN keeps its level
 * through a watchdog reset (the keeper of record l8gnd, when applied, holds it through a RUN or SWD reset, which reset
 * the whole chip).
 */
void runtime_init_early_resets(void)
{
    reset_block_mask(~((1u << RESET_IO_QSPI) | (1u << RESET_PADS_QSPI) | (1u << RESET_PLL_USB) |
                       (1u << RESET_USBCTRL) | (1u << RESET_SYSCFG) | (1u << RESET_PLL_SYS) |
                       (1u << RESET_IO_BANK0) | (1u << RESET_PADS_BANK0)));
    unreset_block_mask_wait_blocking(RESETS_RESET_BITS & ~((1u << RESET_ADC) | (1u << RESET_RTC) | (1u << RESET_SPI0) |
                                                           (1u << RESET_SPI1) | (1u << RESET_UART0) |
                                                           (1u << RESET_UART1) | (1u << RESET_USBCTRL)));
}

/* ---------------------------------------------------------------- pins */

static void out_low(unsigned g)
{
    gpio_put(g, 0);                          /* the value first, then the direction, then the function: no glitch */
    gpio_set_dir(g, GPIO_OUT);
    gpio_set_function(g, GPIO_FUNC_SIO);
}

static void in_nopull(unsigned g)
{
    gpio_set_dir(g, GPIO_IN);
    gpio_set_function(g, GPIO_FUNC_SIO);     /* sets IE again (runtime_init clears IE on GPIO26..29 on RP2040) */
    gpio_disable_pulls(g);
}

/* FW-C01 steps 1 and 2, the first thing main() does. */
void hal_init_pins_first(void)
{
    out_low(HAL_GPIO_PI_KILL);               /* push-pull low, never tri-stated while a slot is powered (FW-A11) */
    gpio_put(HAL_GPIO_PI_SHDN_REQ, 0);       /* value 0 for ever; asserting is the output enable (FW-A10) */
    in_nopull(HAL_GPIO_PI_SHDN_REQ);
    in_nopull(HAL_GPIO_ZEROIZE_SW);          /* R10 10 k up; readable at the first instruction (gen_sch_c.py U3 note) */
}

bool hal_gpio_get(enum hal_gpio g) { return gpio_get((unsigned)g); }

/* Set by the slot-cut handler; while set no SLOT_EN is raised, and it clears once the main loop has written all three
 * low itself (the core cuts at the same instant: this closes the race between the alarm and a loop pass computed a
 * millisecond earlier). */
static volatile uint32_t slot_cut_latched;

void hal_gpio_put(enum hal_gpio g, bool level)
{
    if (g == HAL_GPIO_EMCON_RD_R || g == HAL_GPIO_ZEROIZE_SW || g == HAL_GPIO_PI_SHDN_REQ)
        return;                              /* never outputs (FW-C07, FW-C04); PI_SHDN_REQ only by its OE */
    if (g >= HAL_GPIO_SLOT_EN1 && g <= HAL_GPIO_SLOT_EN3 && slot_cut_latched) {
        if (level)
            return;
        slot_cut_latched &= ~(1u << g);
    }
    gpio_put((unsigned)g, level);
}

/* FW-C02: read as inputs before the pads are made outputs (the pad's pull-down may stay on). */
void hal_slot_en_read(bool held[3])
{
    for (unsigned i = 0; i < 3; i++)
        held[i] = gpio_get(HAL_GPIO_SLOT_EN1 + i);
}

void hal_slot_en_drive_initial(const bool level[3])
{
    for (unsigned i = 0; i < 3; i++) {
        unsigned g = HAL_GPIO_SLOT_EN1 + i;
        gpio_put(g, level[i]);
        gpio_set_dir(g, GPIO_OUT);
        gpio_set_function(g, GPIO_FUNC_SIO);
    }
}

void hal_pi_shdn_req_assert(bool assert)
{
    gpio_put(HAL_GPIO_PI_SHDN_REQ, 0);
    gpio_set_dir(HAL_GPIO_PI_SHDN_REQ, assert ? GPIO_OUT : GPIO_IN);
}

/* the rest of the pins, after panel_init() */
void hal_init_rest(void);
void hal_init_rest(void)
{
    static const unsigned outs[] = { HAL_GPIO_EPD_DC_R, HAL_GPIO_EPD_CS_R, HAL_GPIO_EPD_RST, HAL_GPIO_HDMI_SEL1,
                                     HAL_GPIO_HDMI_SEL2, HAL_GPIO_SHORE_INHIBIT, HAL_GPIO_LED_STAT };
    static const unsigned ins[] = { HAL_GPIO_EPD_BUSY, HAL_GPIO_HB1, HAL_GPIO_HB2, HAL_GPIO_HB3, HAL_GPIO_EMCON_RD_R,
                                    HAL_GPIO_TR_APRS, HAL_GPIO_EXP_INT, HAL_GPIO_TEST_SW, HAL_GPIO_SOS_SW };
    for (size_t i = 0; i < sizeof outs / sizeof outs[0]; i++)
        out_low(outs[i]);                    /* SHORE_INHIBIT boot low (FW-C08) */
    for (size_t i = 0; i < sizeof ins / sizeof ins[0]; i++)
        in_nopull(ins[i]);                   /* HB1..3: no pad pulls (FW-C05) */
    gpio_put(HAL_GPIO_EPD_PWR_n, 1);         /* the e-paper off (Q5, low = on) */
    gpio_set_dir(HAL_GPIO_EPD_PWR_n, GPIO_OUT);
    gpio_set_function(HAL_GPIO_EPD_PWR_n, GPIO_FUNC_SIO);

    /* the kit bus: I2C0 on GPIO0/1, Standard-mode 100 kHz, no internal pull, 4 mA, slow slew (FW-K01, FW-K02) */
    i2c_init(KIT_I2C, HAL_I2C_HZ);
    for (unsigned g = HAL_GPIO_SDA; g <= HAL_GPIO_SCL; g++) {
        gpio_set_function(g, GPIO_FUNC_I2C);
        gpio_disable_pulls(g);
        gpio_set_drive_strength(g, GPIO_DRIVE_STRENGTH_4MA);
        gpio_set_slew_rate(g, GPIO_SLEW_RATE_SLOW);
    }

    /* PANEL_PWM (slice 4 A) and PWM1 (slice 4 B): 2 kHz, 10 bit; the rail dark until the firmware is up */
    unsigned slice = pwm_gpio_to_slice_num(HAL_GPIO_PANEL_PWM);
    pwm_set_wrap(slice, HAL_PWM_TOP);
    pwm_set_clkdiv(slice, (float)clock_get_hz(clk_sys) / (float)(HAL_PWM_HZ * (HAL_PWM_TOP + 1u)));
    pwm_set_chan_level(slice, PWM_CHAN_A, 0);
    pwm_set_chan_level(slice, PWM_CHAN_B, 0);
    gpio_set_function(HAL_GPIO_PANEL_PWM, GPIO_FUNC_PWM);
    gpio_set_function(HAL_GPIO_PWM1, GPIO_FUNC_PWM);
    pwm_set_enabled(slice, true);

    /* RAIL_SENSE on ADC0 (IE off, OD on: adc_gpio_init) */
    adc_init();
    adc_gpio_init(HAL_GPIO_RAIL_SENSE);
    adc_select_input(0);

    /* the e-paper's SPI (spi0 on GPIO2 SCK and GPIO3 TX): its command layer is OWED (README section 4) */
}

void hal_pwm_set_permille(enum hal_gpio g, uint16_t permille)
{
    uint32_t level = ((uint32_t)permille * (HAL_PWM_TOP + 1u) + 999u) / 1000u;   /* 2 % is the lowest step: 21 of 1024 */
    pwm_set_gpio_level((unsigned)g, (uint16_t)level);
}

uint16_t hal_rail_sense_mv(void)
{
    return (uint16_t)(((uint32_t)adc_read() * 3300u) / 4095u);
}

ms_t hal_now_ms(void) { return to_ms_since_boot(get_absolute_time()); }

/* ---------------------------------------------------------------- the kit bus */

static absolute_time_t op_until(ms_t deadline_ms)
{
    absolute_time_t t = make_timeout_time_ms(HAL_I2C_OP_TIMEOUT_MS);   /* T_HAL = 10 ms (ZEROIZE.md 3.4 (a)) */
    absolute_time_t d = from_us_since_boot((uint64_t)deadline_ms * 1000u);
    return absolute_time_diff_us(d, t) > 0 ? d : t;
}

int hal_i2c_write(uint8_t addr, const uint8_t *buf, unsigned len, ms_t deadline_ms)
{
    if (hal_now_ms() >= deadline_ms)
        return -2;
    int r = i2c_write_blocking_until(KIT_I2C, addr, buf, len, false, op_until(deadline_ms));
    if (r == PICO_ERROR_TIMEOUT)
        i2c_init(KIT_I2C, HAL_I2C_HZ);       /* through reset: an SCL held low cannot be recovered otherwise */
    return r == (int)len ? 0 : -1;
}

int hal_i2c_read(uint8_t addr, uint8_t *buf, unsigned len, ms_t deadline_ms)
{
    if (hal_now_ms() >= deadline_ms)
        return -2;
    int r = i2c_read_blocking_until(KIT_I2C, addr, buf, len, false, op_until(deadline_ms));
    if (r == PICO_ERROR_TIMEOUT)
        i2c_init(KIT_I2C, HAL_I2C_HZ);
    return r == (int)len ? 0 : -1;
}

/* FW-K04's recovery: SCL and SDA as open drains by their output enables */
void hal_i2c_bitbang_begin(void)
{
    for (unsigned g = HAL_GPIO_SDA; g <= HAL_GPIO_SCL; g++) {
        gpio_put(g, 0);
        gpio_set_dir(g, GPIO_IN);
        gpio_set_function(g, GPIO_FUNC_SIO);
    }
}
void hal_i2c_bitbang_scl(bool level) { gpio_set_dir(HAL_GPIO_SCL, level ? GPIO_IN : GPIO_OUT); }
bool hal_i2c_bitbang_sda_read(void) { return gpio_get(HAL_GPIO_SDA); }
void hal_i2c_bitbang_stop(void)
{
    gpio_set_dir(HAL_GPIO_SDA, GPIO_OUT);    /* SDA low while SCL high-ish, then SCL up, then SDA up */
    busy_wait_us(5);
    gpio_set_dir(HAL_GPIO_SCL, GPIO_IN);
    busy_wait_us(5);
    gpio_set_dir(HAL_GPIO_SDA, GPIO_IN);
    busy_wait_us(5);
}
void hal_i2c_bitbang_end(void)
{
    for (unsigned g = HAL_GPIO_SDA; g <= HAL_GPIO_SCL; g++)
        gpio_set_function(g, GPIO_FUNC_I2C);
    i2c_init(KIT_I2C, HAL_I2C_HZ);
}
void hal_delay_us(unsigned us) { busy_wait_us(us); }

/* ---------------------------------------------------------------- watchdog and reset reason (FW-C02) */

void hal_watchdog_start(ms_t period_ms)
{
    watchdog_enable(period_ms, true);
    /* keep the pads, the GPIO bank and SIO out of the watchdog's reset (PSM and RESETS WDSEL); the PSM's RESETS bit is
     * cleared too, so the reset controller is not itself reset and its WDSEL decides (INFERRED; V-C02 checks it) */
    hw_clear_bits(&psm_hw->wdsel, PSM_WDSEL_SIO_BITS | PSM_WDSEL_RESETS_BITS);
    hw_clear_bits(&resets_hw->wdsel, RESETS_WDSEL_IO_BANK0_BITS | RESETS_WDSEL_PADS_BANK0_BITS);
}

void hal_watchdog_feed(void) { watchdog_update(); }

/* 1 watchdog, 2 RUN pin, 3 debugger, 0 power-on (logged at boot and reported, FW-C02, FW-C12) */
int hal_reset_reason(void)
{
    if (watchdog_enable_caused_reboot())
        return 1;
    uint32_t r = vreg_and_chip_reset_hw->chip_reset;
    if (r & VREG_AND_CHIP_RESET_CHIP_RESET_HAD_RUN_BITS)
        return 2;
    if (r & VREG_AND_CHIP_RESET_CHIP_RESET_HAD_PSM_RESTART_BITS)
        return 3;
    return 0;
}

/* FW-C01 and FW-C02: the ROM bootloader only with every slot off, and an activity mask of GPIO25 only */
int hal_reboot_to_bootsel(void)
{
    if (sio_hw->gpio_out & SLOT_MASK)
        return -1;
    reset_usb_boot(1u << HAL_GPIO_LED_STAT, 0);
}

/* ---------------------------------------------------------------- ZEROIZE step 0: the slot cut, from RAM */

static void __not_in_flash_func(slot_cut_isr)(void)
{
    timer_hw->intr = 1u << CUT_ALARM;
    sio_hw->gpio_clr = SLOT_MASK;            /* SLOT_EN1..3 low, whatever the rest of the firmware is doing */
    slot_cut_latched = SLOT_MASK;
}

void hal_arm_slot_cut_alarm(ms_t at_ms)
{
    irq_set_exclusive_handler(TIMER_IRQ_3, slot_cut_isr);
    irq_set_priority(TIMER_IRQ_3, PICO_HIGHEST_IRQ_PRIORITY);
    hw_set_bits(&timer_hw->inte, 1u << CUT_ALARM);
    irq_set_enabled(TIMER_IRQ_3, true);
    timer_hw->alarm[CUT_ALARM] = (uint32_t)((uint64_t)at_ms * 1000u);
}

void hal_cancel_slot_cut_alarm(void)
{
    timer_hw->armed = 1u << CUT_ALARM;
    hw_clear_bits(&timer_hw->inte, 1u << CUT_ALARM);
}

/* ---------------------------------------------------------------- the journal (ZEROIZE.md 3.4 steps 1 and 4) */

int hal_journal_read(uint32_t off, uint8_t *buf, unsigned len)
{
    if (off + len > JOURNAL_SIZE)
        return -1;
    memcpy(buf, (const void *)(XIP_BASE + JOURNAL_OFF + off), len);
    return 0;
}

/* one page program (at most 3 ms, interrupts masked only for it); NOR programming only clears bits, so the page is
 * re-programmed with its own content around the new record */
int hal_journal_program(uint32_t off, const uint8_t *buf, unsigned len)
{
    static uint8_t page[FLASH_PAGE_SIZE];
    uint32_t base = off & ~(FLASH_PAGE_SIZE - 1u);
    if (off + len > JOURNAL_SIZE || (off - base) + len > FLASH_PAGE_SIZE)
        return -1;
    memcpy(page, (const void *)(XIP_BASE + JOURNAL_OFF + base), FLASH_PAGE_SIZE);
    memcpy(page + (off - base), buf, len);
    uint32_t s = save_and_disable_interrupts();
    flash_range_program(JOURNAL_OFF + base, page, FLASH_PAGE_SIZE);
    restore_interrupts(s);
    return memcmp((const void *)(XIP_BASE + JOURNAL_OFF + off), buf, len) == 0 ? 0 : -1;
}

/* only at boot with no wipe due (never in the wipe's path) */
int hal_journal_erase(void)
{
    uint32_t s = save_and_disable_interrupts();
    flash_range_erase(JOURNAL_OFF, JOURNAL_SIZE);
    restore_interrupts(s);
    return 0;
}
