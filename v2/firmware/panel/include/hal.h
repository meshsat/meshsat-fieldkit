/*
 * hal.h: the panel controller's thin hardware layer (board C, U3 RP2040, MESHSAT-1357 Layer 12).
 *
 * Prototype firmware for an UNBUILT board: nothing here has run on hardware. Every pin and expander bit below is
 * read from v2/docs/PANEL.md sections 3 and 4 and checked by v2/ecad/tools/tests/test_fw_panel.py against board C's
 * committed netlist (v2/ecad/pcb-c-display-c8/out/pcb-c-display.net) and, for the kit expanders, the netlists of
 * boards A, B and D. The two lists HAL_PIN_LIST and HAL_EXP_BIT_LIST are the machine-readable statement the test
 * parses; keep one entry per line.
 *
 * Two implementations: src/hal_rp2040.c (pico-sdk, written against the SDK API by name and NOT built here: this host
 * has no arm toolchain) and src/hal_host.c (a stub for the host unit tests).
 */
#ifndef PANEL_HAL_H
#define PANEL_HAL_H

#include <stdbool.h>
#include <stdint.h>

typedef uint32_t ms_t;

/* ---- RP2040 GPIO map (PANEL.md section 3; netlist U3). X(net, gpio, direction) ----
 * direction: IN input, OUT push-pull output, OD open-drain emulated by output-enable (value 0), ADC analogue,
 * I2C, SPI, PWM. */
#define HAL_PIN_LIST(X) \
    X(SDA,           0,  I2C) \
    X(SCL,           1,  I2C) \
    X(EPD_SCL_R,     2,  SPI) \
    X(EPD_SDA_R,     3,  SPI) \
    X(EPD_DC_R,      4,  OUT) \
    X(EPD_CS_R,      5,  OUT) \
    X(EPD_RST,       6,  OUT) \
    X(EPD_BUSY,      7,  IN) \
    X(PANEL_PWM,     8,  PWM) \
    X(PWM1,          9,  PWM) \
    X(HB1,           10, IN) \
    X(HB2,           11, IN) \
    X(HB3,           12, IN) \
    X(SLOT_EN1,      13, OUT) \
    X(SLOT_EN2,      14, OUT) \
    X(SLOT_EN3,      15, OUT) \
    X(HDMI_SEL1,     16, OUT) \
    X(HDMI_SEL2,     17, OUT) \
    X(PI_SHDN_REQ,   18, OD) \
    X(PI_KILL,       19, OUT) \
    X(SHORE_INHIBIT, 20, OUT) \
    X(EMCON_RD_R,    21, IN) \
    X(ZEROIZE_SW,    22, IN) \
    X(TR_APRS,       23, IN) \
    X(EXP_INT,       24, IN) \
    X(LED_STAT,      25, OUT) \
    X(RAIL_SENSE,    26, ADC) \
    X(TEST_SW,       27, IN) \
    X(SOS_SW,        28, IN) \
    X(EPD_PWR_n,     29, OUT)

#define HAL_ENUM_GPIO(net, gpio, dir) HAL_GPIO_##net = gpio,
enum hal_gpio { HAL_PIN_LIST(HAL_ENUM_GPIO) HAL_GPIO_COUNT_ = 30 };
#undef HAL_ENUM_GPIO

/* The PI button (SW_PI) has NO controller pin: its contacts reach only the two lands of J_PIJ2 (nets PIJ2_A2 and
 * PIJ2_B2, neither on U3 nor on an expander nor on GND). README finding F-01. The core implements the button's
 * logic (PANEL.md section 5) on an input the HAL cannot yet supply; HAL_PI_BUTTON_WIRED stays 0 until board C routes
 * the lead to a pin (an expander spare such as U1 P1.3 SPARE1 with PIJ2_B2 on GND is one way). */
#define HAL_PI_BUTTON_WIRED 0

/* ---- I2C addresses (PANEL.md section 7) ---- */
#define HAL_I2C_VEML7700   0x10
#define HAL_I2C_B_U6       0x20
#define HAL_I2C_A_U27      0x21
#define HAL_I2C_C_U1       0x22
#define HAL_I2C_C_U2       0x23
#define HAL_I2C_A_U28      0x24
#define HAL_I2C_B_U7       0x25
#define HAL_I2C_D_U16      0x26
#define HAL_I2C_TPS23861   0x28
#define HAL_I2C_TPS_BCAST  0x30 /* every TPS23861 answers it; never written except to address all of them (FW-K03) */
#define HAL_I2C_SUP1       0x34
#define HAL_I2C_SUP2       0x35
#define HAL_I2C_SUP3       0x36
#define HAL_I2C_ADS1115    0x48
#define HAL_I2C_TMP117     0x49
#define HAL_I2C_KSZ9897R   0x5F
#define HAL_I2C_ATECC608B  0x60
#define HAL_I2C_DS3231     0x68
#define HAL_I2C_BQ25731    0x6B

/* Kit bus clock: Standard-mode, 100 kHz programmed (FW-K01, SC-HF-03); never Fast-mode on the current copper. */
#define HAL_I2C_HZ 100000u
/* No bus operation longer than this (ZEROIZE.md 3.4 (a) T_HAL; FW-K04's 10 ms SCL-low bound). */
#define HAL_I2C_OP_TIMEOUT_MS 10u

/* ---- PCA9555 bits (PANEL.md section 4 for board C; HW-FW-CONTRACT.md FW-A06 to A14, A16, C14, B13 for A, B, D).
 * X(name, address, port, bit, net). Pin of the PW package: port 0 bit n = pin 4 + n, port 1 bit n = pin 13 + n. ---- */
#define HAL_EXP_BIT_LIST(X) \
    X(C_SOSACT,    0x22, 0, 0, SOSACT_K) \
    X(C_MWARN,     0x22, 0, 1, MWARN_K) \
    X(C_MCAUT,     0x22, 0, 2, MCAUT_K) \
    X(C_CHG,       0x22, 0, 3, CHG_K) \
    X(C_SAT,       0x22, 0, 4, SAT_K) \
    X(C_MESH,      0x22, 0, 5, MESH_K) \
    X(C_LTE,       0x22, 0, 6, LTE_K) \
    X(C_GPS,       0x22, 0, 7, GPS_K) \
    X(C_LIGHT_DAY_N,   0x22, 1, 0, LIGHT_DAY_n) \
    X(C_LIGHT_NIGHT_N, 0x22, 1, 1, LIGHT_NIGHT_n) \
    X(C_PANEL_ID,  0x22, 1, 2, PANEL_ID) \
    X(C_SHORE,     0x23, 0, 0, SHORE_K) \
    X(C_MSG,       0x23, 0, 1, MSG_K) \
    X(C_PIRING,    0x23, 0, 2, PIRING_K) \
    X(C_BAT1,      0x23, 0, 3, BAT1_K) \
    X(C_BAT2,      0x23, 0, 4, BAT2_K) \
    X(C_BAT3,      0x23, 0, 5, BAT3_K) \
    X(C_BAT4,      0x23, 0, 6, BAT4_K) \
    X(C_BAT5,      0x23, 0, 7, BAT5_K) \
    X(C_TX_LAMPTEST, 0x23, 1, 0, TX_LAMPTEST) \
    X(A_CHG_INHIBIT, 0x21, 0, 0, CHG_INHIBIT) \
    X(A_MON_EN,    0x21, 0, 1, MON_EN) \
    X(A_HEAT_EN,   0x21, 0, 2, HEAT_EN) \
    X(A_D8_EN,     0x21, 0, 3, D8_EN) \
    X(A_POE_SW_EN, 0x21, 0, 4, POE_SW_EN) \
    X(A_PA_SW_EN,  0x21, 0, 5, PA_SW_EN) \
    X(A_HF_SW_EN,  0x21, 0, 6, HF_SW_EN) \
    X(A_DEV_EN,    0x21, 0, 7, DEV_EN) \
    X(A_CHRG_OK,   0x21, 1, 0, CHRG_OK) \
    X(A_HOT_R1,    0x21, 1, 5, DOCK_SPARE) \
    X(A_FE_PGOOD,  0x21, 1, 7, FE_PGOOD) \
    X(A_USBX_EN,   0x24, 0, 0, USBX_EN) \
    X(A_USBX_FLT,  0x24, 0, 1, USBX_FLT) \
    X(A_PD_SW_EN,  0x24, 1, 0, PD_SW_EN) \
    X(A_EMCON_EF_FLT, 0x24, 1, 2, EMCON_EF_FLT) \
    X(B_RB_SW_EN,  0x20, 0, 2, RB_SW_EN) \
    X(B_LORA_ON,   0x20, 0, 3, LORA_ON) \
    X(B_ZB_ON,     0x20, 0, 4, ZB_ON) \
    X(B_RB_SW_IEN, 0x20, 1, 6, RB_SW_IEN) \
    X(B_RB_STATUS, 0x25, 0, 3, RB_STATUS) \
    X(D_SA_PD,     0x26, 0, 5, X_SA_PD) \
    X(D_AMP_EN,    0x26, 0, 6, X_AMP_EN) \
    X(D_MMUTE,     0x26, 0, 7, X_MMUTE)

#define HAL_ENUM_EXP(name, addr, port, bit, net) HAL_EXP_##name##_ADDR = addr, HAL_EXP_##name##_PORT = port, HAL_EXP_##name##_BIT = bit,
enum hal_exp_bits { HAL_EXP_BIT_LIST(HAL_ENUM_EXP) HAL_EXP_DUMMY_ = 0 };
#undef HAL_ENUM_EXP

/* PCA9555 registers (TI SCPS131J, Table 8-3). */
#define PCA9555_IN0  0x00
#define PCA9555_IN1  0x01
#define PCA9555_OUT0 0x02
#define PCA9555_OUT1 0x03
#define PCA9555_POL0 0x04
#define PCA9555_POL1 0x05
#define PCA9555_CFG0 0x06
#define PCA9555_CFG1 0x07

/* LED rail dimmer: 2 kHz, 10 bit (PANEL.md section 3). */
#define HAL_PWM_HZ   2000u
#define HAL_PWM_TOP  1023u

/* RAIL_SENSE: the rail is present above 1.25 V at the pin (PANEL.md section 3). */
#define HAL_RAIL_PRESENT_MV 1250u

/* ---- the HAL API ---- */
void     hal_init_pins_first(void);           /* FW-C01 steps 1 and 2 only: PI_KILL low push-pull, PI_SHDN_REQ released */
bool     hal_gpio_get(enum hal_gpio g);       /* the pin's level, any function */
void     hal_gpio_put(enum hal_gpio g, bool level);   /* OUT pins only; refuses EMCON_RD_R and PI_SHDN_REQ */
void     hal_slot_en_read(bool held[3]);      /* FW-C02: GPIO13..15 read as inputs, before they are made outputs */
void     hal_slot_en_drive_initial(const bool level[3]); /* then each driven at the level panel_init() returns */
int      hal_reboot_to_bootsel(void);         /* FW-C01/C02: refused while a slot runs; activity mask GPIO25 only */
void     hal_pi_shdn_req_assert(bool assert); /* FW-A10: value 0 always, output enable on to assert */
void     hal_pwm_set_permille(enum hal_gpio g, uint16_t permille);
uint16_t hal_rail_sense_mv(void);
ms_t     hal_now_ms(void);

int      hal_i2c_write(uint8_t addr, const uint8_t *buf, unsigned len, ms_t deadline_ms);
int      hal_i2c_read(uint8_t addr, uint8_t *buf, unsigned len, ms_t deadline_ms);
/* FW-K04: nine SCL pulses and a STOP on a held bus, done by the core's bus_recover() through these three. */
void     hal_i2c_bitbang_begin(void);
void     hal_i2c_bitbang_scl(bool level);
bool     hal_i2c_bitbang_sda_read(void);
void     hal_i2c_bitbang_stop(void);
void     hal_i2c_bitbang_end(void);
void     hal_delay_us(unsigned us);

void     hal_watchdog_start(ms_t period_ms);  /* FW-C02 scope rule; see hal_rp2040.c */
void     hal_watchdog_feed(void);
int      hal_reset_reason(void);

/* ZEROIZE.md 3.4 step 0: a timer alarm whose RAM-resident, highest-priority handler drives SLOT_EN1..3 low. */
void     hal_arm_slot_cut_alarm(ms_t at_ms);
void     hal_cancel_slot_cut_alarm(void);

/* the flash journal region (two pre-erased sectors at the top of U4, W25Q16JV) */
int      hal_journal_read(uint32_t off, uint8_t *buf, unsigned len);
int      hal_journal_program(uint32_t off, const uint8_t *buf, unsigned len);
int      hal_journal_erase(void);

#endif
