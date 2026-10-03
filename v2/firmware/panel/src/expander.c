/*
 * expander.c: the seven PCA9555 on the kit bus, as the panel controller (the bus's only master) drives them.
 *
 *  - FW-A08 and P s.5 (boot): every expander's OUTPUT registers are written before its CONFIGURATION registers (the
 *    power-on output register is all ones, so configuring first would drive every output high for a moment), and
 *    A:U27's DEV_EN stays 1 (it feeds this controller); DEV_EN is written 0 only as the last act of a shutdown.
 *  - P s.4 (board C's LED sinks): an LED is ON when its bit is an OUTPUT driving 0, OFF when the bit is an INPUT; a 1
 *    is never driven. Every configuration write that enables an output is preceded by an output-register write of 0
 *    (SESSION S-10: an expander reset by a brownout returns its output register to FFh).
 *  - FW-C14: every EXP_INT is serviced by reading the input ports (A:U27 port 1 carries HOT-R1 on P1.5), followed by a
 *    command byte other than 00h (TI SCPS131J 8.4.1.1); the ports are polled at least once a second too.
 *
 * Pure logic over the injected bus. Prototype for an unbuilt kit.
 */
#include <string.h>

#include "panel.h"

typedef struct {
    uint8_t addr;
    uint8_t out0, out1;   /* boot output registers */
    uint8_t cfg0, cfg1;   /* boot configuration registers (1 = input) */
    bool    configure;    /* false: left at its power-on state (all inputs) */
} exp_boot_t;

/* The boot values. Board C: every LED bit an input (dark). Board A U27: port 0 all outputs at 0 except DEV_EN (P0.7)
 * at 1, port 1 inputs; U28: USBX_EN (P0.0) and PD_SW_EN (P1.0) outputs at 0, the rest inputs. Board B U6: sixteen
 * active-high requests, each held low by a pull-down at power-up (gen_sch_b.py R60 to R62 and the 100 k on the
 * others): outputs at 0. Board B U7: inputs only, not configured. Board D U16: X_SA_PD, X_AMP_EN, X_MMUTE (P0.5 to
 * P0.7) outputs at 0 (SESSION S-11: off), the rest inputs (FW-D01). */
static const exp_boot_t EXP_BOOT[] = {
    { HAL_I2C_C_U1,  0x00, 0x00, 0xFF, 0xFF, true },
    { HAL_I2C_C_U2,  0x00, 0x00, 0xFF, 0xFF, true },
    { HAL_I2C_A_U27, 1u << HAL_EXP_A_DEV_EN_BIT, 0x00, 0x00, 0xFF, true },
    { HAL_I2C_A_U28, 0x00, 0x00, (uint8_t)~(1u << HAL_EXP_A_USBX_EN_BIT), (uint8_t)~(1u << HAL_EXP_A_PD_SW_EN_BIT), true },
    { HAL_I2C_B_U6,  0x00, 0x00, 0x00, 0x00, true },
    { HAL_I2C_B_U7,  0x00, 0x00, 0xFF, 0xFF, false },
    { HAL_I2C_D_U16, 0x00, 0x00, 0x1F, 0xFF, true },
};

/* the expanders that carry inputs and raise EXP_INT */
static const uint8_t EXP_INPUTS[] = { HAL_I2C_C_U1, HAL_I2C_A_U27, HAL_I2C_A_U28, HAL_I2C_B_U7, HAL_I2C_D_U16 };

static int wr3(panel_t *p, uint8_t addr, uint8_t reg, uint8_t a, uint8_t b)
{
    uint8_t buf[3] = { reg, a, b };
    return p->ops->bus.i2c_write(p->ops->bus.ctx, addr, buf, 3);
}

int panel_exp_boot(panel_t *p)
{
    int errors = 0;
    for (size_t i = 0; i < sizeof EXP_BOOT / sizeof EXP_BOOT[0]; i++) {
        const exp_boot_t *e = &EXP_BOOT[i];
        if (!e->configure)
            continue;
        if (wr3(p, e->addr, PCA9555_OUT0, e->out0, e->out1) != 0) {
            errors++;
            continue;                            /* never configure an expander whose outputs were not written */
        }
        if (wr3(p, e->addr, PCA9555_CFG0, e->cfg0, e->cfg1) != 0)
            errors++;
    }
    p->leds_written = 0;
    p->leds_written_valid = false;
    p->exp_init_done = true;
    return errors;
}

static void led_cfg(uint32_t leds, uint8_t *u1c0, uint8_t *u2c0, uint8_t *u2c1)
{
    *u1c0 = (uint8_t)~(leds & 0xFFu);
    *u2c0 = (uint8_t)~((leds >> 8) & 0xFFu);
    *u2c1 = (leds & LED_BIT(LED_TXTEST)) ? (uint8_t)~(1u << HAL_EXP_C_TX_LAMPTEST_BIT) : 0xFF;
}

static int write_led_cfg(panel_t *p, uint32_t leds)
{
    uint8_t u1c0, u2c0, u2c1;
    led_cfg(leds, &u1c0, &u2c0, &u2c1);
    int r = 0;
    r |= wr3(p, HAL_I2C_C_U1, PCA9555_OUT0, 0x00, 0x00);
    r |= wr3(p, HAL_I2C_C_U1, PCA9555_CFG0, u1c0, 0xFF);
    r |= wr3(p, HAL_I2C_C_U2, PCA9555_OUT0, 0x00, 0x00);
    r |= wr3(p, HAL_I2C_C_U2, PCA9555_CFG0, u2c0, u2c1);
    return r;
}

/* Show a new LED set. After boot the outputs are enabled one by one (P s.4); later only a change is written. */
int panel_exp_write_leds(panel_t *p, uint32_t leds)
{
    leds &= PANEL_LED_ALL;
    if (p->leds_written_valid && p->leds_written == leds)
        return 0;
    int r = 0;
    if (!p->leds_ramped && leds != 0) {
        p->leds_ramped = true;
        uint32_t acc = 0;
        for (unsigned l = 0; l < LED_COUNT; l++) {
            if (!(leds & LED_BIT(l)))
                continue;
            acc |= LED_BIT(l);
            r |= write_led_cfg(p, acc);
        }
        if (acc == 0)
            r |= write_led_cfg(p, 0);
    } else {
        r = write_led_cfg(p, leds);
    }
    if (r == 0) {
        p->leds_written = leds;
        p->leds_written_valid = true;
    }
    return r;
}

/* Read every input expander; return 0 if board C's and board A's U27 reads succeeded. */
int panel_exp_service(panel_t *p, ms_t now)
{
    int r = 0;
    uint8_t in[2];
    for (size_t i = 0; i < sizeof EXP_INPUTS; i++) {
        uint8_t a = EXP_INPUTS[i];
        int e = p->ops->bus.i2c_read(p->ops->bus.ctx, a, PCA9555_IN0, in, 2);
        if (e == 0) {
            uint8_t cmd = PCA9555_OUT0;          /* any command byte but 00h (SCPS131J 8.4.1.1) */
            (void)p->ops->bus.i2c_write(p->ops->bus.ctx, a, &cmd, 1);
        }
        if (a == HAL_I2C_C_U1) {
            p->exp_c_ok = e == 0;
            if (e == 0) {
                p->light_day_n = (in[1] >> HAL_EXP_C_LIGHT_DAY_N_BIT) & 1u;
                p->light_night_n = (in[1] >> HAL_EXP_C_LIGHT_NIGHT_N_BIT) & 1u;
                p->panel_id = (in[1] >> HAL_EXP_C_PANEL_ID_BIT) & 1u;
            } else {
                r = -1;
            }
        } else if (a == HAL_I2C_A_U27) {
            if (e == 0) {
                p->hot_r1_level = (in[1] >> HAL_EXP_A_HOT_R1_BIT) & 1u;
                panel_hot_sample(&p->hot, p->hot_r1_level, now);
            } else {
                r = -1;
            }
        } else if (a == HAL_I2C_B_U7 && e == 0) {
            p->rb_status = (in[HAL_EXP_B_RB_STATUS_PORT] >> HAL_EXP_B_RB_STATUS_BIT) & 1u;
            p->rb_need_fresh = false;         /* a read after the EMCON release */
        }
    }
    p->exp_polled_at = now;
    return r;
}

/* The switched loads' software enables (FW-A06, A07, A13; FW-C13 and FW-C15's actors): A:U27 port 0, A:U28 ports 0 and
 * 1, B:U6 ports 0 and 1. DEV_EN stays 1. Written only on a change; the output registers only (the configuration was
 * set at boot). */
int panel_exp_write_kit(panel_t *p, uint16_t on, bool rb_ien)
{
#define ON(l) ((on >> (l)) & 1u)
    uint8_t a27 = (uint8_t)((1u << HAL_EXP_A_DEV_EN_BIT) | ON(LOAD_MONITOR) << HAL_EXP_A_MON_EN_BIT |
                            ON(LOAD_HEATER) << HAL_EXP_A_HEAT_EN_BIT | ON(LOAD_BOARD_D) << HAL_EXP_A_D8_EN_BIT |
                            ON(LOAD_POE) << HAL_EXP_A_POE_SW_EN_BIT | ON(LOAD_PA) << HAL_EXP_A_PA_SW_EN_BIT |
                            ON(LOAD_HF) << HAL_EXP_A_HF_SW_EN_BIT);
    uint8_t a28_0 = (uint8_t)(ON(LOAD_WALL_VBUS) << HAL_EXP_A_USBX_EN_BIT);
    uint8_t a28_1 = (uint8_t)(ON(LOAD_USBC) << HAL_EXP_A_PD_SW_EN_BIT);
    uint8_t b6_0 = (uint8_t)(ON(LOAD_ROCKBLOCK) << HAL_EXP_B_RB_SW_EN_BIT | ON(LOAD_LORA) << HAL_EXP_B_LORA_ON_BIT |
                             ON(LOAD_ZIGBEE) << HAL_EXP_B_ZB_ON_BIT);
    uint8_t b6_1 = (uint8_t)((rb_ien ? 1u : 0u) << HAL_EXP_B_RB_SW_IEN_BIT);
#undef ON
    const uint8_t want[3][2] = { { a27, 0x00 }, { a28_0, a28_1 }, { b6_0, b6_1 } };
    const uint8_t addr[3] = { HAL_I2C_A_U27, HAL_I2C_A_U28, HAL_I2C_B_U6 };
    int r = 0;
    for (int i = 0; i < 3; i++) {
        if (p->kit_out_valid && p->kit_out[i][0] == want[i][0] && p->kit_out[i][1] == want[i][1])
            continue;
        if (wr3(p, addr[i], PCA9555_OUT0, want[i][0], want[i][1]) == 0) {
            p->kit_out[i][0] = want[i][0];
            p->kit_out[i][1] = want[i][1];
        } else {
            r = -1;
        }
    }
    p->kit_out_valid = r == 0;
    return r;
}
