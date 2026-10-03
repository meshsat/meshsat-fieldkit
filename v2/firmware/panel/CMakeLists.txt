# The panel controller's target build (board C, U3 RP2040; MESHSAT-1357 Layer 12).
# NOT RUN HERE: written for pico-sdk 2.3.1 (PICO_SDK_PATH set, arm-none-eabi-gcc on the PATH); the first build is owed.
#   cmake -S v2/firmware/panel -B build-rp2040 -DPICO_BOARD=none && cmake --build build-rp2040
cmake_minimum_required(VERSION 3.13)
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)
project(meshsat_panel C CXX ASM)
set(CMAKE_C_STANDARD 11)
pico_sdk_init()

add_executable(meshsat_panel
    src/main_rp2040.c
    src/hal_rp2040.c
    src/panel_core.c
    src/zeroize.c
    src/expander.c
    src/bus_recover.c
    src/sensors.c
)
target_include_directories(meshsat_panel PRIVATE include)

# Board C: 12 MHz crystal, W25Q16JV 2 MiB QSPI flash (gen_sch_c.py: Y1, U4).
target_compile_definitions(meshsat_panel PRIVATE
    PICO_FLASH_SIZE_BYTES=2097152
    PICO_XOSC_STARTUP_DELAY_MULTIPLIER=64
    # FW-C01: never the RP2040-E5 USB enumeration fix (it drives GPIO15, SLOT_EN3)
    PICO_RP2040_USB_DEVICE_ENUMERATION_FIX=0
    # FW-C01: a BOOTSEL activity mask of GPIO25 only: hal_reboot_to_bootsel() is the one caller of reset_usb_boot()
    # ZEROIZE.md 3.4 step 0: the slot-cut handler runs from RAM through the RAM vector table
    PICO_NO_RAM_VECTOR_TABLE=0
)
target_link_libraries(meshsat_panel
    pico_stdlib
    hardware_i2c
    hardware_pwm
    hardware_adc
    hardware_flash
    hardware_watchdog
    hardware_irq
    hardware_resets
    pico_bootrom
)
# No stdio on the UARTs or USB until the bridge protocol (MESHSAT-837) defines the USB device: finding F-02.
pico_enable_stdio_usb(meshsat_panel 0)
pico_enable_stdio_uart(meshsat_panel 0)
pico_add_extra_outputs(meshsat_panel)
