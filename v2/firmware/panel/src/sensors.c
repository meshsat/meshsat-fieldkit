/*
 * sensors.c: the two kit-bus sensors the panel controller reads itself. Pure logic over the injected bus.
 *
 *  - Board B's TMP117 at 0x49 (FW-C13 and FW-C14's fallback with HOT-R1 held high). TI SNOSD82D (September 2022),
 *    held as v2/vendor/ti/ti-tmp117-temperature.pdf: the temperature register 00h is 16-bit two's complement at
 *    7.8125 m°C (section 7.6.2), reads 8000h (-256 °C) until the first conversion; the configuration register 01h
 *    resets to 0220h (continuous, 1 s cycle, 8 averages) and its bit 13 Data_Ready is set at the end of a conversion and
 *    cleared by a read of either register (Table 7-6). Registers are read MSB first. So a reading counts once per
 *    conversion: "two readings in a row" are two conversions, never one conversion read twice.
 *  - Board C's VEML7700 at 0x10 (P s.8: the reading reported to the bridge). Vishay 84286 Rev. 1.8 (28 November 2024),
 *    held as v2/vendor/vishay/veml7700-datasheet.pdf: ALS_CONF_0 (command 00h) powers up shut down (ALS_SD = 1);
 *    the firmware writes gain x1/8 (bits 12:11 = 10b) and 100 ms (bits 9:6 = 0000b), 1000h; ALS (04h) is 16 bit, LSB
 *    first. The lux per count at that setting is INFERRED by scaling the sheet's only printed figure, 0.0042 lx per step
 *    at gain x2 and 800 ms (lux = counts / (gain x responsivity), its Table 1 note): x16 for the gain, x8 for the
 *    time, 0.5376 lx per count; Vishay's application note, which the sheet refers to for the table, is not held.
 */
#include "panel.h"

#define TMP117_REG_TEMP 0x00
#define TMP117_REG_CONF 0x01
#define TMP117_DATA_READY (1u << 13)
#define TMP117_RESET_VALUE 0x8000u
#define VEML_ALS_CONF 0x00
#define VEML_ALS 0x04
#define VEML_CONF_GAIN_1_8_IT_100MS 0x1000u

int panel_tmp117_poll(panel_t *p, ms_t now)
{
    uint8_t b[2];
    p->tmp117_polled_at = now;
    if (p->ops->bus.i2c_read(p->ops->bus.ctx, HAL_I2C_TMP117, TMP117_REG_CONF, b, 2) != 0)
        goto fail;
    if (!(((unsigned)b[0] << 8 | b[1]) & TMP117_DATA_READY))
        return 0;                                            /* no new conversion since the last read */
    if (p->ops->bus.i2c_read(p->ops->bus.ctx, HAL_I2C_TMP117, TMP117_REG_TEMP, b, 2) != 0)
        goto fail;
    uint16_t raw = (uint16_t)((unsigned)b[0] << 8 | b[1]);
    if (raw == TMP117_RESET_VALUE)
        return 0;                                            /* before the first conversion */
    p->tmp117.valid = true;
    p->tmp117.mc = ((int32_t)(int16_t)raw * 125) / 16;        /* 7.8125 m°C a step */
    p->tmp117.seq++;
    p->tmp117_ok_at = now;
    return 0;
fail:
    if ((int32_t)(now - p->tmp117_ok_at) > 3000)
        p->tmp117.valid = false;                             /* no reading for 3 s: none */
    return -1;
}

int panel_veml_init(panel_t *p)
{
    uint8_t w[3] = { VEML_ALS_CONF, (uint8_t)(VEML_CONF_GAIN_1_8_IT_100MS & 0xFFu), (uint8_t)(VEML_CONF_GAIN_1_8_IT_100MS >> 8) };
    p->veml_ready = p->ops->bus.i2c_write(p->ops->bus.ctx, HAL_I2C_VEML7700, w, 3) == 0;
    return p->veml_ready ? 0 : -1;
}

int panel_veml_poll(panel_t *p, ms_t now)
{
    uint8_t b[2];
    p->veml_polled_at = now;
    if (!p->veml_ready && panel_veml_init(p) != 0)
        return -1;
    if (p->ops->bus.i2c_read(p->ops->bus.ctx, HAL_I2C_VEML7700, VEML_ALS, b, 2) != 0) {
        p->light_valid = false;
        p->veml_ready = false;                               /* re-written at the next poll (a power cycle shuts it down) */
        return -1;
    }
    p->light_counts = (uint16_t)(b[0] | (unsigned)b[1] << 8);
    p->light_mlux = (uint32_t)p->light_counts * 5376u / 10u; /* 0.5376 lx a count, INFERRED (header) */
    p->light_valid = true;
    return 0;
}
