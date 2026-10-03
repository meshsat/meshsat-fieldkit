# Host build and unit tests of the panel controller's portable core (MESHSAT-1357 Layer 12).
#   make -C v2/firmware/panel test            build and run the host tests
#   make -C v2/firmware/panel test BUILD=/tmp/x   the same, with the objects elsewhere
# The target build is CMake with the pico-sdk (CMakeLists.txt); it is NOT run here (no arm toolchain on this host).
CC      ?= gcc
BUILD   ?= build
CFLAGS  ?= -std=c11 -O1 -g -Wall -Wextra -Werror -pedantic -Wshadow -Wconversion -Wno-sign-conversion
CPPFLAGS += -Iinclude -Itests
CORE    := src/panel_core.c src/zeroize.c src/expander.c src/bus_recover.c src/sensors.c src/hal_host.c
TESTS   := tests/fixture.c tests/test_main.c tests/test_io.c tests/test_controls.c tests/test_zeroize.c tests/test_power.c

.PHONY: test probe clean
test: $(BUILD)/panel_tests
	$(BUILD)/panel_tests

# the contract probe: the values PANEL.md and HW-FW-CONTRACT.md decide, measured on the core (test_fw_panel.py reads them)
probe: $(BUILD)/contract_probe
	$(BUILD)/contract_probe

$(BUILD)/contract_probe: $(CORE) tests/fixture.c tests/contract_probe.c include/panel.h include/hal.h tests/fixture.h
	mkdir -p $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ $(CORE) tests/fixture.c tests/contract_probe.c

$(BUILD)/panel_tests: $(CORE) $(TESTS) include/panel.h include/hal.h tests/fixture.h tests/test_list.h
	mkdir -p $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ $(CORE) $(TESTS)

clean:
	rm -rf $(BUILD)
