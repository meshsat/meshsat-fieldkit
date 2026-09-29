#!/usr/bin/env python3
"""PCB-C CONTROL PANEL BACKER, phase C7 (MESHSAT-830; appendix 32.51, 32.52, 32.60): generate the KiCad 9 schematic (netlist style: every pin gets a
stub and a net label; GND gets power symbols). Runs where the KiCad symbol libraries are (the vast.ai box). Usage: gen_sch_c.py <out.kicad_sch> <project>

The backer hangs 10 mm under the aluminium face plate (tools/panel1450.py is the single source of the face positions). C7 replaces the two expanders'
role by an RP2040 panel controller (32.52: a USB device of B16's slot-1 hub, PORTS[1][2] in gen_sch_b.py, corrected 9 Sep 2026, the kit I2C master, the e-paper, the sounder, the LED rail PWM, the
heartbeats, slot enables, HDMI input select and the power-control lines to B16 over the 2x13 ribbon J_PANEL; the two PCA9555 stay as the LED sinks
and mode inputs on the same bus). The hardware lines stay hardware: the EMCON toggle drives TX_INHIBIT_n directly and EMCON_HW through a
Schmitt-trigger buffer (U9), the ZEROIZE toggle drives the local sense ZEROIZE_SW that the controller reads and U12 buffers onto ZEROIZE_HW (26 September
2026, D-03), the TX lamp follows TR_APRS. Since round 8 of MESHSAT-1357 (26 September 2026) the controller reads EMCON_HW only through a
one-way buffer (U13, EMCON.md L1), and a hardware EMCON lamp (D22, lit through U14 and Q7 while both EMCON lines read low, no processor in
its path, SD-EMC-6) sits beside the EMCON toggle. The e-paper is the bare Pervasive Displays E2370KS0C1 on a 24-way ZIF with the
maker's boost circuit (rev 02 note: MOSFET, 10 uH, three SS2040FL, 0.47 ohm, 1 uF/25 V caps and one 4.7 uF/25 V pump cap) behind a P-FET power switch. New on the face: the Xenarc
monitor (no electronics here; its cables go to B16 and A22), two U-174/U headset jacks wired to D8, a VEML7700 ambient light sensor under a light guide,
and a USB camera module behind a sealed window (its lead to B16's J_CAM). Eight standoff screws bond the board to the plate."""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-c-display"
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
# 10 September 2026 (MESHSAT-862, red team C2): the schematic engine lives in kisch.py, one copy for the six boards.
# What stays here is this board: its part tables, its nets, its sheet layout. `ic()` is strict for every board again.
import kisch
from kisch import (U, c, emit_part, emit_pwr_flag, ensure, esd, extents, find_sym, flatten, flatten_raw, ic, label, lib_tree, noconn, parse, part, pins_of, place_symbol, q, r, rename_units, ser, synth_symbol, text, tps22810, uq, usb_c_recept, wire)
import intent as _intent
# the loads as the schematic wires them (8 Sep 2026): the LED rail leaves through the LIGHTING toggle in the left strip and comes back as LED_RAIL_SW,
# the LDO feeds the controller, the expanders, the e-paper and the sensor, the sounder is the rest; without them dc_drop split the whole 0.6 A over
# every U and J pad and asked for a 1.0 mm class, which the router could not lay on this board (two runs with no session, 90 min and 3 h)
_intent.rail("+5V", 5.0, 0.6, 1.0, "J_PANEL", budget=0.05, loads={"SW_LIGHT": 0.35, "U5": 0.20, "BZ1": 0.03},
             always_on=True, always_on_why="it arrives over the panel ribbon from board B, behind B's own fuse F6; nothing on this board switches it",
             note="the panel rail over the ribbon (PANEL_5V on B16, fused F6). Budget 5 percent, not the 2 percent default and not the 3 percent this line "
                  "carried until 8 Sep 2026 22:55: every load tolerates it. The LED rail is PWM'd, the sounder is a buzzer, and the only regulated load is the "
                  "TLV75533 LDO, which has 1.5 V of headroom at 5 V in and 3.3 V out. C8 measures 171 mV (3.41 percent) with 0.6 A over 561 mm of 0.5 mm track, "
                  "half of it on 0.5 oz inner copper; the rail class stays 0.5 mm because 1.0 mm strangled the router in the driver cluster (32.76).")

# DECLARED 16 September 2026. The panel's own 3.3 V was not in the intent file, so `signalnets` could not know
# it was a rail and the return-path gate judged it as a SIGNAL NET, while `dc_drop` and `derate` could not see
# it at all. Every load is named because a rail without loads is not declarable.
# WHAT FEEDS THIS RAIL (20 September 2026, appendix 32.246): `power_path` adds up what a rail's
# converters draw and refuses to let a feeder declare less than its children take. Board A's VBAT
# declared 10 A and its nine converters drew 15.18, and nothing checked it on any board until now.
# THIS RAIL COVERS ITS CHILD EPD_VCC (27 September 2026, stream w4c, finding W4C-F5 of the independent check; taken by the
# session under the owner's standing rule of 26 September 2026). EPD_VCC, declared at the end of the design, takes 0.521 A at
# its peak from this rail through Q5 (the boost's 0.5 A switch-current class into L1), and this rail declared 0.20 A: the
# +3V3 copper from U5 and C2 to Q5 would have been judged for less than it carries. Q5 is a switch, not a filter: C28 (4.7 uF)
# behind Q5's at most 85 mOhm (AOS AO3401A, RDS(ON) at VGS -2.5 V, v2/vendor/power/aos-ao3401a-p-mosfet.pdf) is a 0.40 us time
# constant against an on-phase of about 1.6 us (10 uH to 0.5 A from 3.135 V), so by the end of each on-phase about three
# quarters of the inductor's current or more comes through Q5 and the bound that needs no layout is all of it. So this rail
# declares its own loads (0.119 A typical and 0.199 A peak: the 0.12 and 0.20 A it declared before, less Q5's former 1 mA)
# plus EPD_VCC's figures. U5's own share is W4C-F5's open item: the TLV75533 is rated 500 mA (IOUT, TI SBVS320D 5.3; ICL
# 560 mA minimum), and the 0.22 A by which the peak exceeds it, held for no longer than one on-phase, is at most 0.35 uC, 24 mV
# on C2, C28 and C29 (14.8 uF nominal) against this rail's 99 mV budget; what U5 carries on average through a refresh no held document states (the
# boost's output power; EPD_VCC's 10 mA is INFERRED), so it is read at bring-up. The check after EPD_VCC's declaration
# refuses a file where this rail no longer covers its child.
_P3V3_OWN = (0.119, 0.199)   # the panel's logic loads without the e-paper supply (typical, peak)
_EPD = (0.030, 0.521)        # EPD_VCC (typical, peak), declared at the end of the design with its basis
_intent.rail("+3V3", 3.3, round(_P3V3_OWN[0] + _EPD[0], 3), round(_P3V3_OWN[1] + _EPD[1], 3), "U5", budget=0.03, share=0.0075, always_on=True, fed_from="+5V",
             always_on_why="U5 is a TLV75533 whose EN pin is tied to its own input, so this rail follows the 5 V that arrives on the ribbon and has no switch of its own",
             source_ic="U5 is a TLV75533 LDO in SOT-23-5: pin 5 IS its output power pin",
             loads={"U1": 0.040, "U2": 0.010, "U3": 0.010, "U4": 0.015, "U6": 0.005, "U7": 0.005,
                    "U8": 0.005, "U10": 0.005, "U11": 0.005, "U9": 0.002, "U12": 0.002, "U_LIGHT": 0.020, "Q5": 0.030,   # U12: the ZEROIZE buffer (D-03, 26 September 2026); Q5: the switched e-paper supply EPD_VCC at its declared 30 mA (PWR-001, 27 September 2026; was 1 mA)
                    "U13": 0.002, "U14": 0.002},   # round 8: the controller's one-way EMCON copy and the EMCON lamp's gate, at the 2 mA allowance U9 and U12 carry (ICC 10 uA max each, DS35124 p.4, SCES414P p.5)
             note="the panel's logic 3.3 V from the LDO U5: the RP2040 controller, its QSPI flash, the two "
                  "expanders, the buffers, the EMCON lamp's gate, the light sensor and the e-paper's supply switch. Budget 3 percent, "
                  "because every load is a logic part with a wide supply range. Since 27 September 2026 (W4C-F5) the figures cover "
                  "the child EPD_VCC: its own loads' 0.119 A typical and 0.199 A peak plus EPD_VCC's 0.030 and 0.521 A, because "
                  "within each boost on-phase (about 1.6 us) Q5 carries most of the inductor's current (C28 behind Q5 is a 0.40 us "
                  "time constant). U5 is rated 500 mA (TI SBVS320D): the excess at the peak is 0.35 uC per on-phase, 24 mV on C2, "
                  "C28 and C29 at most; U5's average through a refresh is an open item read at bring-up")
SYMDIR = "/usr/share/kicad/symbols/"

# ----------------------------------------------------------------- s-expression helpers (as B13/B15)
LIBCACHE = {}

# ----------------------------------------------------------------- synthetic box symbols (odd pins left, even pins right)
# Raspberry Pi RP2040 (QFN-56, pin 57 the pad), the PDi 24-way FPC (pin names from the driving circuit note rev 02)
RP2040 = {1: "IOVDD", 2: "GPIO0", 3: "GPIO1", 4: "GPIO2", 5: "GPIO3", 6: "GPIO4", 7: "GPIO5", 8: "GPIO6", 9: "GPIO7", 10: "IOVDD", 11: "GPIO8", 12: "GPIO9", 13: "GPIO10", 14: "GPIO11", 15: "GPIO12", 16: "GPIO13",
          17: "GPIO14", 18: "GPIO15", 19: "TESTEN", 20: "XIN", 21: "XOUT", 22: "IOVDD", 23: "DVDD", 24: "SWCLK", 25: "SWD", 26: "RUN", 27: "GPIO16", 28: "GPIO17", 29: "GPIO18", 30: "GPIO19", 31: "GPIO20", 32: "GPIO21",
          33: "IOVDD", 34: "GPIO22", 35: "GPIO23", 36: "GPIO24", 37: "GPIO25", 38: "GPIO26_A0", 39: "GPIO27_A1", 40: "GPIO28_A2", 41: "GPIO29_A3", 42: "IOVDD", 43: "ADC_AVDD", 44: "VREG_VIN", 45: "VREG_VOUT",
          46: "USB_DM", 47: "USB_DP", 48: "USB_VDD", 49: "IOVDD", 50: "DVDD", 51: "QSPI_SD3", 52: "QSPI_SCLK", 53: "QSPI_SD0", 54: "QSPI_SD2", 55: "QSPI_SD1", 56: "QSPI_SS_N", 57: "GND"}
EPD24 = {1: "NC", 2: "GDR", 3: "RESE", 4: "NC", 5: "VDHR", 6: "NC", 7: "NC", 8: "BS", 9: "BUSY_N", 10: "RST_N", 11: "DC", 12: "CSB", 13: "SCL", 14: "SDA", 15: "VDDIO", 16: "VDD", 17: "VSS", 18: "VDDD",
         19: "NC", 20: "VDH", 21: "VGH", 22: "VDL", 23: "VGL", 24: "VCOM", 25: "SHIELD", 26: "SHIELD"}
SYNTH = {"RP2040": RP2040, "EPD24": EPD24}

# ----------------------------------------------------------------- footprints
FP = {
 "R": "Resistor_SMD:R_0603_1608Metric", "C": "Capacitor_SMD:C_0603_1608Metric", "C10u": "Capacitor_SMD:C_0805_2012Metric", "C0402": "Capacitor_SMD:C_0402_1005Metric",
 "LED3": "LED_THT:LED_D3.0mm", "LED": "LED_SMD:LED_0603_1608Metric", "EXP": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", "SOT23": "Package_TO_SOT_SMD:SOT-23", "SOT235": "Package_TO_SOT_SMD:SOT-23-5", "SOT236": "Package_TO_SOT_SMD:SOT-23-6",
 "SOD123": "Diode_SMD:D_SOD-123", "SOD123F": "Diode_SMD:D_SOD-123F", "FB": "Inductor_SMD:L_0603_1608Metric", "L4020": "Inductor_SMD:L_APV_ANR4020", "JP2": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "TP": "TestPoint:TestPoint_Pad_D1.5mm",
 "XH2": "meshsat:LeadLands_1x02", "IDC26": "Connector_IDC:IDC-Header_2x13_P2.54mm_Vertical_SMD", "ZIF24": "meshsat:Hirose_FH34SRJ-24S", "VEML": "meshsat:Vishay_VEML7700",
 "QFN56": "Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm", "USON8": "Package_SON:Winbond_USON-8-1EP_3x2mm_P0.5mm_EP0.2x1.6mm", "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
 "SW19": "meshsat:PanelSwitch_19mm", "SW16": "meshsat:PanelSwitch_16mm", "TGL6": "meshsat:ToggleBody_DPDT", "TGL3": "meshsat:ToggleBody_SPDT", "HSJ": "meshsat:PanelJack_17mm", "CAMH": "MountingHole:MountingHole_2.2mm_M2",
 "BZ": "meshsat:PanelSounder", "MHPAD": "meshsat:BackerScrew_M3_GND",
}
kisch.configure(fp=FP, synth=SYNTH)   # the engine needs the tables before the first part
P = kisch.P                           # one list, shared with the engine (not a copy)
def synth(ref, name, value, fp, nets, lcsc=""):
    full = {str(k): nets.get(k, nets.get(str(k), "NC")) for k in SYNTH[name]}
    part(ref, "Connector_Generic", name, value, fp, full, lcsc)
# 13 September 2026: an LED row carried its COLOUR as its value and no part number, so the certification
# could not identify it: "no part number and no value this search understands: 'amber NVMe activity'". The
# colour is the design intent and stays in the value, where the schematic reader wants it; the code is what
# makes the row orderable. Hubei KENTO's 0603 family, every entry read back from JLCPCB with its stock on
# 13 September 2026: red C2286 (BASIC, 3,879,968), yellow/amber C2287 (98,669), green C12624 (113,369),
# blue C2288 (99,839), white C2290 (BASIC, 1,168,521). A colour with no entry gets no code rather than a
# guess, and the certification will say so.
LED_CODE = {"red": "C2286", "amber": "C2287", "yellow": "C2287", "green": "C12624", "blue": "C2288", "white": "C2290"}
def led_code(colour):
    w = (colour or "").strip().split()
    return (LED_CODE.get(w[0].lower()) or "") if w else ""   # "" and not None: part() defaults lcsc to ""
def led(ref, colour, anode, cathode): part(ref, "Device", "LED", colour, "LED", {"2": anode, "1": cathode}, led_code(colour))
def nfet(ref, gate, source, drain, value="2N7002"): part(ref, "Transistor_FET", "2N7002", value, "SOT23", {"1": gate, "2": source, "3": drain}, "C8545")   # 1 G 2 S 3 D (SOT-23 order, appendix 32.36)
def level(ref, rn, far, near, near_rail, far_rail=None, rf=None):
    """Bidirectional 2N7002 stage between a module-domain line (near, pulled up to the module's rail) and the always-on side (far); the module off = gate low, nothing flows."""
    nfet(ref, near_rail, near, far); r(rn, "10k", near, near_rail)
    if far_rail: r(rf, "10k", far, far_rail)
def tps2065(ref, rail, en, out, flt): part(ref, "Power_Management", "TPS2065CDBV", "TPS2065CDBV", "SOT235", {"5": rail, "4": en, "1": out, "3": flt, "2": "GND"})

def led3(ref, colour, a, k): part(ref, "Device", "LED", "3 mm %s, sunlight viewable" % colour, "LED3", {"2": a, "1": k})   # no code: a 3 mm through-hole lamp in a light guide is a hand-fitted panel part, declared in lcsc-allow.txt
def tp(ref, net): part(ref, "Connector", "TestPoint", net, "TP", {"1": net})
# ================================================================= the design
# --- ribbon from B16 (J_PANEL there has the same 2x13 map), 5 V entry, the local 3.3 V LDO, ESD on the USB pair
part("J_PANEL", "Connector_Generic", "Conn_02x13_Odd_Even", "panel ribbon from B16 J_PANEL (IDC 2x13 SMD, underside): 5 V, kit I2C, EMCON/ZEROIZE/inhibit, HDMI selects, USB, heartbeats, slot enables, power control", "IDC26", {
 "1": "+5V", "2": "+5V", "3": "GND", "4": "SDA", "5": "SCL", "6": "EXP_INT", "7": "TR_APRS", "8": "EMCON_HW", "9": "GND", "10": "ZEROIZE_HW", "11": "TX_INHIBIT_n", "12": "HDMI_SEL1", "13": "HDMI_SEL2",
 "14": "GND", "15": "USB_PNL_P", "16": "USB_PNL_N", "17": "GND", "18": "HB1", "19": "HB2", "20": "HB3", "21": "SLOT_EN1", "22": "SLOT_EN2", "23": "SLOT_EN3", "24": "PI_SHDN_REQ", "25": "PI_KILL", "26": "SHORE_INHIBIT"})
c("C1", "10u", "+5V", "GND", "C10u", "C15850"); c("C2", "10u", "+3V3", "GND", "C10u", "C15850")
ic("U5", 5, "TLV75533PDBV 3.3 V 500 mA LDO for the controller, expanders, e-paper and sensor (1 IN 2 GND 3 EN 4 NC 5 OUT)", "SOT235", {"1": "+5V", "2": "GND", "3": "+5V", "4": "NC", "5": "+3V3"})
c("C3", "1u", "+5V", "GND"); c("C4", "1u", "+3V3", "GND")
esd("U6", "USB_PNL_P", "USB_PNL_N", "+3V3"); esd("U7", "SDA", "SCL", "+3V3"); esd("U8", "TR_APRS", "EXP_INT", "+3V3")
for i in range(1, 6): part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": ["+5V", "+3V3", "GND", "LED_RAIL_SW", "LED_RAIL"][i - 1]})
# --- the RP2040 panel controller (rp2040/rpi-rp2040-datasheet.pdf; the minimal design of the hardware design guide: 12 MHz crystal with 15 pF loads and a 1k on XOUT, W25Q16 QSPI flash,
#     27 ohm USB series, RUN pull-up, BOOTSEL by a solder jumper on QSPI_SS). GPIO: 0 SDA 1 SCL (the kit I2C bus, this board its master), 2 EPD SCL, 3 EPD SDA, 4 EPD DC, 5 EPD CS, 6 EPD RST,
#     7 EPD BUSY, 8 LED rail PWM, 9 sounder PWM, 10 to 12 heartbeats HB1..3 (in), 13 to 15 SLOT_EN1..3, 16 and 17 HDMI_SEL1/2, 18 PI_SHDN_REQ, 19 PI_KILL, 20 SHORE_INHIBIT, 21 EMCON_RD_R (EMCON_HW read one way through U13 and R46, round 8),
#     22 ZEROIZE_SW (read, the toggle's local sense), 23 TR_APRS (read), 24 EXP_INT (read), 25 status LED, 26 LED rail sense (ADC0), 27 TEST_SW, 28 SOS_SW, 29 EPD_PWR_n (the boost's power switch)
# ZEROIZE AT BOOT, WHAT THE HARDWARE GIVES THE FIRMWARE (26 September 2026, owner ruling D-03.3: level-sensitive, read before any slot powers).
#   The pin: GPIO22 (pin 34) on ZEROIZE_SW. RP2040 datasheet (build 3184e62) PADS_BANK0 resets IE=1, OD=0, PDE=1, PUE=0, SCHMITT=1, and section
#   2.19.2 says the input "is always connected, so software can check the state of GPIOs at any time": the level is readable at the first
#   instruction, before any function select. The pull: R10 10k to +3V3 against the pad's 50 to 80k pull-down (Table 625 RPD) gives at least
#   2.75 V open, over VIH min 2.0 V at IOVDD 3.3 V (Table 625); closed is 0 V. The toggle: APEM 5636ADKB-2V, single pole ON-NONE-ON, both
#   positions locked (appendix 32.13 ruling 1), so the level holds through a power loss; APEM's 5000 series sheet
#   (v2/vendor/seals/apem-5000-series-datasheet-rs-copy.pdf, page 6, 5636 row) connects 1-2 in lever position I and 2-3 in position III, so
#   lug 2 is the common and is the one on GND here (26 September 2026 fix-up). SLOT_EN1..3 (GPIO13..15) reset as inputs with the pad
#   pull-down, and board A holds them with 100k to GND (gen_sch_a.py buck5, R30/R34/R38), so no slot powers until firmware drives a pin high.
#   The bootrom drives no bank-0 GPIO on a cold boot (Table 168: an activity pin only when _reset_to_usb_boot is given a mask); the only SDK
#   code that touches GPIO15 (SLOT_EN3) is the RP2040-E5 USB enumeration fix, off by default and fixed in hardware on RP2040B2 (datasheet
#   errata). The firmware obligations that follow (read GPIO22 before any SLOT_EN write, the 5 s hold, the wipe-pending record, never the E5
#   fix, a BOOTSEL activity mask of 0 or GPIO25 only) belong in PANEL.md section 6 beside ZEROIZE and in decision 30 of pcb_decisions.yaml.
synth("U3", "RP2040", "RP2040 panel controller (USB device on B16's slot-1 hub, the kit I2C master)", "QFN56", {
 1: "+3V3", 10: "+3V3", 22: "+3V3", 33: "+3V3", 42: "+3V3", 49: "+3V3", 43: "+3V3", 44: "+3V3", 48: "+3V3", 23: "C_DVDD", 50: "C_DVDD", 45: "C_DVDD", 57: "GND", 19: "GND",
 2: "SDA", 3: "SCL", 4: "EPD_SCL", 5: "EPD_SDA", 6: "EPD_DC", 7: "EPD_CS", 8: "EPD_RST", 9: "EPD_BUSY", 11: "PANEL_PWM", 12: "PWM1", 13: "HB1", 14: "HB2", 15: "HB3", 16: "SLOT_EN1", 17: "SLOT_EN2", 18: "SLOT_EN3",
 20: "XIN", 21: "XOUT_R", 24: "SWCLK", 25: "SWDIO", 26: "C_RUN", 27: "HDMI_SEL1", 28: "HDMI_SEL2", 29: "PI_SHDN_REQ", 30: "PI_KILL", 31: "SHORE_INHIBIT", 32: "EMCON_RD_R", 34: "ZEROIZE_SW", 35: "TR_APRS", 36: "EXP_INT",
 37: "LED_STAT", 38: "RAIL_SENSE", 39: "TEST_SW", 40: "SOS_SW", 41: "EPD_PWR_n", 46: "USB_DM_R", 47: "USB_DP_R", 51: "QSPI_D3", 52: "QSPI_SCLK", 53: "QSPI_D0", 54: "QSPI_D2", 55: "QSPI_D1", 56: "QSPI_SS"}, "C2040")
ic("U4", 9, "W25Q16JVUXIQ 16 Mbit QSPI flash (USON-8: 1 CS 2 DO/IO1 3 WP/IO2 4 GND 5 DI/IO0 6 CLK 7 HOLD/IO3 8 VCC, pad)", "USON8", {"1": "QSPI_SS", "2": "QSPI_D1", "3": "QSPI_D2", "4": "GND", "5": "QSPI_D0", "6": "QSPI_SCLK", "7": "QSPI_D3", "8": "+3V3", "9": "GND"}, "C2843335")
part("Y1", "Device", "Crystal_GND24", "12 MHz ABM8-272-T3 (3225): 1 XIN, 3 XOUT, 2 and 4 GND", "XTAL", {"1": "XIN", "2": "GND", "3": "XOUT", "4": "GND"}, "C20625731")
c("C5", "15p NP0", "XIN", "GND", "C0402"); c("C6", "15p NP0", "XOUT", "GND", "C0402"); r("R1", "1k", "XOUT_R", "XOUT")
r("R2", "27R", "USB_DP_R", "USB_PNL_P"); r("R3", "27R", "USB_DM_R", "USB_PNL_N"); r("R4", "10k", "C_RUN", "+3V3"); r("R5", "1k (BOOTSEL)", "QSPI_SS", "BOOT_J")
part("JP1", "Jumper", "SolderJumper_2_Open", "BOOTSEL: short while powering to enter the USB bootloader", "JP2", {"1": "BOOT_J", "2": "GND"})
for k in range(7, 14): c("C%d" % k, "100n", "+3V3", "GND")
# EVERY RP2040 SUPPLY PIN HAS ITS OWN CAPACITOR (MESHSAT-1357 round 8, DECOUPLING.md 8.3 items G9 and G13; decision 42). The maker, RP2040
# Datasheet (v2/vendor/rp2040/rpi-rp2040-datasheet.pdf, build-version 3184e62-clean) section 2.9: "IOVDD should be decoupled with a 100nF
# capacitor close to each of the chip's IOVDD pins" (2.9.1), "DVDD should be decoupled with a 100nF capacitor close to each of the chip's
# DVDD pins" (2.9.2), "A 1uF capacitor should be connected between VREG_VIN and ground" (2.9.3), "USB_VDD should be decoupled with a 100nF
# capacitor close to the chip's USB_VDD pin" (2.9.4), all printed page 151, and "ADC_AVDD should be decoupled with a 100nF capacitor close
# to the chip's ADC_AVDD pin" (2.9.5, printed page 152); section 2.10.1 (printed page 156): "The regulator must have 1uF capacitors placed
# close to its input (VREG_VIN) and output (VREG_VOUT) pins". Until round 8 ADC_AVDD (pin 43) and USB_VDD (pin 48) shared the IOVDD
# capacitors (round 4 open item O-C1, G9), and the regulator's output net carried two 1 uF declared at the DVDD pins 23 and 50 (G13).
# Now: C42 and C43, 100 nF at pins 43 and 48; C14 stays the 1 uF, declared at VREG_VOUT (pin 45); C15 becomes 100 nF at DVDD pin 50 and
# C44 is added, 100 nF at DVDD pin 23, so C_DVDD holds 1 uF + 2 x 100 nF. ADC_AVDD stays on +3V3 with no series filter: the maker's
# single-supply scheme powers it "directly from the 3.3V supply" (2.9.7.1, printed page 152) and asks only the 100 nF, and the one ADC
# input on this board (RAIL_SENSE, GPIO26) reads whether the LED rail is present, not a precision level. The filter the note at the foot
# of this file used to offer is not fitted (taken by the session under the owner's standing rule of 26 September 2026).
c("C14", "1u", "C_DVDD", "GND"); c("C15", "100n", "C_DVDD", "GND"); c("C16", "1u", "+3V3", "GND")
c("C42", "100n", "+3V3", "GND", "C", "C14663"); c("C43", "100n", "+3V3", "GND", "C", "C14663"); c("C44", "100n", "C_DVDD", "GND", "C", "C14663")
tp("TP1", "SWCLK"); tp("TP2", "SWDIO"); tp("TP3", "C_RUN"); r("R6", "1k", "LED_STAT", "LED_STAT_A"); part("D18", "Device", "LED", "status (GPIO25)", "LED", {"2": "LED_STAT_A", "1": "GND"})
r("R7", "2.2k", "SDA", "+3V3"); r("R8", "2.2k", "SCL", "+3V3")   # the kit bus pull-ups live with the master
# --- I2C expanders on the kit bus: U1 0x22 (A1 high), U2 0x23 (A1 + A0 high). Port 0 = LED sinks (open-drain by configuration), port 1 = mode inputs and spares
part("U1", "Interface_Expansion", "PCA9555PW", "PCA9555PW 0x22: LED sinks, light mode inputs", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "2": "+3V3", "21": "GND", "3": "GND",
 "4": "SOSACT_K", "5": "MWARN_K", "6": "MCAUT_K", "7": "CHG_K", "8": "SAT_K", "9": "MESH_K", "10": "LTE_K", "11": "GPS_K",
 "13": "LIGHT_DAY_n", "14": "LIGHT_NIGHT_n", "15": "PANEL_ID", "16": "SPARE1", "17": "SPARE2", "18": "SPARE3", "19": "SPARE4", "20": "SPARE5"}, "C2864778")
part("U2", "Interface_Expansion", "PCA9555PW", "PCA9555PW 0x23: LED sinks, the battery bar, lamp test", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "2": "+3V3", "21": "+3V3", "3": "GND",
 "4": "SHORE_K", "5": "MSG_K", "6": "PIRING_K", "7": "BAT1_K", "8": "BAT2_K", "9": "BAT3_K", "10": "BAT4_K", "11": "BAT5_K",
 "13": "TX_LAMPTEST", "14": "SPARE6", "15": "SPARE7", "16": "SPARE8", "17": "SPARE9", "18": "SPARE10", "19": "SPARE11", "20": "SPARE12"}, "C2864778")
c("C17", "100n", "+3V3", "GND", "C", "C14663"); c("C18", "100n", "+3V3", "GND", "C", "C14663")
for i, net in enumerate(("SOS_SW", "ZEROIZE_SW", "TEST_SW", "LIGHT_DAY_n", "LIGHT_NIGHT_n"), 9):   # R10/C20 now on the local ZEROIZE_SW (D-03, 26 September 2026)
    r("R%d" % i, "10k", net, "+3V3", "R", "C25804"); c("C%d" % (i + 10), "10n", net, "GND", "C", "C57112")
r("R14", "2.2k 1%", "TX_INHIBIT_n", "+3V3", "R", "C4190"); c("C24", "10n", "TX_INHIBIT_n", "GND", "C", "C57112"); r("R50", "10k 1%", "TX_INHIBIT_n", "GND", "R", "C25804")   # A22, B16 and D9 each hold TX_INHIBIT_n
# down with 100k so a cut ribbon inhibits at every consumer; since EQ-25 (27 September 2026, W3T-F1) R14 is 2.2k 1% and R50 holds it down on this board too: the arithmetic is in the note at the end of the design
# EMCON_HW is a BUFFERED COPY of TX_INHIBIT_n, not its inverse (9 September 2026, red team C1). Both consumer boards were already built on
# "low silences": A22 computes PA_EN = EMCON_HW AND PA_SW_EN and B16 computes every transmitter enable the same way, while this board
# inverted the toggle into them. Asserting EMCON therefore ENABLED the PA and released both M.2 radios' W_DISABLE1#. A 74LVC1G34
# non-inverting buffer in the same SOT-23-5 land (2 A, 4 Y) fixes the sense at its source. The toggle stays the only driver of
# TX_INHIBIT_n: A22's gate that drove it back from EMCON_HW is deleted, which also removes a one-inversion feedback loop.
# A SCHMITT INPUT, NOT A PLAIN ONE (26 September 2026, MESHSAT-1357 round 4). TX_INHIBIT_n is a switch node with R14 up, C24 10n down
# and three 100k pull-downs off board (A R145, B R59, D R2), so releasing the EMCON toggle gives a slow rising edge: with R14 10k, a 77 us time constant
# (7.7k Thevenin into 10n) toward 2.54 V, about 74 us/V at a 1.5 V threshold; since EQ-25 (R14 2.2k, R50 10k) 17 us toward 2.57 V, still microseconds per volt. The 74LVC1G34's recommended operating conditions allow an
# input transition of 10 ns/V at 3.3 V (Diodes DS36108 Rev. 10-2, Delta t/Delta V), so the plain buffer ran several thousand times
# outside its input-slew limit on the kit's EMCON line. The
# 74LVC1G17 is the same function with a Schmitt-trigger input and no slew limit, in the same SOT-25 land with the same pins (Diodes
# DS35124 Rev. 8-2: 1 NC, 2 A, 3 GND, 4 Y, 5 VCC; IOFF partial power down; -40 to +125 C; VT+ 1.50 to 2.00 V at 3.0 V and 2.16 to 2.74 V
# at 4.5 V; the sheet has no 3.3 V row, and interpolating linearly between those two gives about 2.15 V worst case at 3.3 V, against
# the 2.57 V this line rests at since EQ-25, 2.37 V at the adverse ends; 2.54 V and 2.11 V with R14 10k). Diodes 74LVC1G17W5-7, LCSC C151394.
ic("U9", 5, "74LVC1G17 Schmitt-trigger non-inverting buffer (Diodes 74LVC1G17W5-7, SOT-25: 2 A 4 Y): EMCON_HW follows TX_INHIBIT_n; low = every transmitter inhibited (32.50 item 3)", "SOT235", {"1": "NC", "2": "TX_INHIBIT_n", "3": "GND", "4": "EMCON_HW_DRV", "5": "+3V3"}, "C151394")
c("C25", "100n", "+3V3", "GND")
# EMCON_HW CANNOT SIT ABOVE TX_INHIBIT_n BY MORE THAN ONE SCHOTTKY DROP (stream d4emcon, finding D4E-F1, 29 September 2026;
# taken by the session under the owner's standing rule of 26 September 2026). With this board's +3V3 in 0 to 1.65 V and the toggle
# at EMCON, U9 is outside its specified supply and its output is unspecified up to 1.65 V, which board B's readers (VIL 0.8 V)
# cannot be shown to read LOW; every board B row reads EMCON_HW alone. R52 (330R 1%) limits what U9 can push, and D23 (BAT46W,
# anode EMCON_HW, cathode TX_INHIBIT_n) clamps EMCON_HW to the contact: at most 5.1 mA in the band and VF 0.45 V at 10 mA (Diodes
# DS30044 Rev. 20-2, 25 C). Released, EMCON_HW is at least 2.13 V (U9's VOH 2.4 V at -16 mA into 3.165 k through 333 Ohm), over
# VIH 2.0 V. A U9 stuck high now asserts EMCON_HW instead of releasing board B. Reverse: delete R52 and D23, U9 pin 4 on EMCON_HW.
r("R52", "330R 1%", "EMCON_HW_DRV", "EMCON_HW", "R", "C23138")
part("D23", "Device", "D_Schottky", "BAT46W-7-F Schottky 100V (EMCON_HW clamp to TX_INHIBIT_n, D4E-F1)", "SOD123", {"1": "TX_INHIBIT_n", "2": "EMCON_HW"}, "C83152")
# NO FIRMWARE PIN SITS ON EMCON_HW (MESHSAT-1357 round 8, EMCON.md section 3 item L1; the second checkpoint review of 26 September 2026,
# finding C). Until round 8 the controller's GPIO21 (U3 pin 32) was a node of EMCON_HW itself. The RP2040 resets that pad as an input with
# its pull-down and no function selected (datasheet 2.19.6.1 Table 285, FUNCSEL reset 0x1f "NULL"; 2.19.6.3 Table 341, IE 1, PDE 1), so it
# is benign in reset; a running image that sets it as an output would fight U9 while EMCON is asserted, and with this board unpowered its
# pad passes a current no held sheet bounds, which left the line's fail-safe hold UNDECIDED on every board that reads it (R4T-D40). Now
# the pin reads a one-way copy: U13 takes EMCON_HW on its input only and drives the local net EMCON_RD, and R46 (1 k) joins that net to the
# pin. A CMOS buffer's output cannot drive its own input, so nothing the firmware does reaches the line. U13 is the part U9 and U12 already
# are (Diodes 74LVC1G17W5-7, DS35124 Rev. 8-2, v2/vendor/diodes/diodes-74lvc1g17.pdf: SOT25 pins 1 NC, 2 A, 3 GND, 4 Y, 5 VCC, page 1;
# II +-5 uA at VCC 0 to 5.5 V and IOFF +-10 uA at VCC 0, page 4). EMCON.md's hand-off named a 74LVC1G34; the 74LVC1G17 is taken instead
# because it is the same function on the same land with a Schmitt input, so no input-slew bound applies to it (DS36108 states 10 ns/V for
# the 1G34), it states IOFF as the 1G34 does, and it is a reel this board already carries (taken by the session under the owner's
# standing rule of 26 September 2026). R46 bounds a contention with a pad the firmware has set as an output to about 3.4 mA, inside the
# pad's 4 mA reset drive setting (2.19.6.3 Table 341, DRIVE reset 0x1 = 4MA) and far inside U13's 24 mA; read through it, U13's high
# (VCC - 0.1 V at 100 uA, DS35124 page 4) against the pad's 50 to 80 k pull-down (Table 625 RPD) is at least VCC - 0.17 V, 3.13 V at
# a 3.3 V rail, over VIH 2.0 V (the 64 uA the 50 k draws at 3.2 V drops 0.064 V across R46).
# What the line sees from this board is now three parts that state IOFF: U9's output, U13's input and U14's input below.
ic("U13", 5, "74LVC1G17 Schmitt-trigger non-inverting buffer (Diodes 74LVC1G17W5-7, SOT-25: 2 A 4 Y): the panel controller's one-way copy of EMCON_HW (EMCON_RD, to GPIO21 through R46)", "SOT235", {"1": "NC", "2": "EMCON_HW", "3": "GND", "4": "EMCON_RD", "5": "+3V3"}, "C151394")
c("C40", "100n", "+3V3", "GND", "C", "C14663"); r("R46", "1k", "EMCON_RD", "EMCON_RD_R", "R", "C21190")
# ZEROIZE IS SENSED ON THIS BOARD ONLY, AND EXPORTED THROUGH A BUFFER (26 September 2026, owner rulings D-03.2 and D-03.3, MESHSAT-1357
# round 4). As generated at 82dd1e4d the toggle, R10, C20 and GPIO22 sat on ZEROIZE_HW itself, which leaves this board on J_PANEL pin 10,
# crosses board B to J_AB1 pin 20, board A (a second 10k pull-up R117 to A's +3V3) and the mezzanine to board D, and is read by nothing
# but GPIO22. D-03.2 makes the covered toggle the ONLY trigger and D-03.3 makes the wipe level-sensitive at boot, so any conductor of that
# chain held low (a pinched ribbon shorting conductor 10 to its neighbour, conductor 9, which is GND; a board fault) would read as a closed toggle and
# start an irreversible crypto-erase. Round 2 also left open (W3-F12) that A's R117 back-feeds this board through ZEROIZE_HW when A's 3.3 V
# is up and this board is not; RP2040 Table 622 allows an IO no higher than IOVDD + 0.5 V. Now the toggle, R10, C20 and GPIO22 are on
# the local net ZEROIZE_SW, and U12 copies it onto ZEROIZE_HW for the boards that carry the name (their test points, and any later
# listener). U12's IOFF disables its output while this board is unpowered, so R117 no longer reaches this board's rail through this line.
# Same part as U9 for the same reason (a 10k/10n switch node): Diodes 74LVC1G17W5-7, LCSC C151394, pins as above.
ic("U12", 5, "74LVC1G17 Schmitt-trigger non-inverting buffer (Diodes 74LVC1G17W5-7, SOT-25: 2 A 4 Y): ZEROIZE_HW follows the local ZEROIZE_SW (owner D-03)", "SOT235", {"1": "NC", "2": "ZEROIZE_SW", "3": "GND", "4": "ZEROIZE_HW", "5": "+3V3"}, "C151394")
c("C39", "100n", "+3V3", "GND", "C", "C14663")
r("R15", "10k", "LED_RAIL_SW", "RAIL_SENSE", "R", "C25804"); r("R16", "10k", "PANEL_ID", "+3V3", "R", "C25804"); r("R51", "10k", "RAIL_SENSE", "GND", "R", "C25804")   # R51: the divider's bottom leg (W4C-F1, note at the end of the design)
part("JP2", "Jumper", "SolderJumper_2_Open", "PANEL_ID strap (closed = variant B)", "JP2", {"1": "PANEL_ID", "2": "GND"})
# --- LED rail: +5V -> LIGHTING toggle (open in BLACKOUT) -> LED_RAIL_SW -> Q1 P-FET (PWM from PANEL_PWM through Q2) -> LED_RAIL; NVG mode is the lowest PWM level in firmware (16c)
part("SW_LIGHT", "Connector_Generic", "Conn_01x06", "LIGHTING DAY/NIGHT/BLACKOUT toggle DPDT ON-ON-ON (pole 1: rail, pole 2: sense); NKK M2044SD3A01 on the D3 splashproof bushing, its O-ring (spare AT516) under the nut on the face, AT428H boot; D hole, flat toward +X", "TGL6",
     {"1": "LED_RAIL_SW", "2": "+5V", "3": "NC", "4": "GND", "5": "LIGHT_DAY_n", "6": "LIGHT_NIGHT_n"})
part("Q1", "Transistor_FET", "AO3401A", "AO3401A P-FET high side", "SOT23", {"1": "Q1_G", "2": "LED_RAIL_SW", "3": "LED_RAIL"}, "C15127")
r("R17", "2.2k", "LED_RAIL_SW", "Q1_G", "R", "C4190"); r("R18", "47R", "Q1_G", "Q2_D", "R", "C23182")
nfet("Q2", "Q2_G", "GND", "Q2_D"); r("R19", "100R", "PANEL_PWM", "Q2_G", "R", "C22775"); r("R20", "100k", "Q2_G", "GND", "R", "C25803")
tp("TP4", "LED_RAIL"); tp("TP5", "LED_RAIL_SW")
# --- indicators (3 mm THT, anode from LED_RAIL through the series resistor, cathode to the expander sink; red/amber 300R, green/white 180R at 8 mA)
LEDS = [("D1", "MWARN", "red", "300R"), ("D2", "MCAUT", "amber", "300R"), ("D4", "SOSACT", "red", "300R"), ("D5", "SAT", "green", "180R"), ("D6", "MESH", "green", "180R"),
        ("D7", "LTE", "green", "180R"), ("D8", "GPS", "green", "180R"), ("D9", "SHORE", "green", "180R"), ("D10", "CHG", "white", "180R"), ("D11", "MSG", "white", "180R"),
        ("D12", "BAT1", "amber", "300R"), ("D13", "BAT2", "green", "180R"), ("D14", "BAT3", "green", "180R"), ("D15", "BAT4", "green", "180R"), ("D16", "BAT5", "green", "180R")]
rn = 21
for ref, name, colour, val in LEDS:
    r("R%d" % rn, val, "LED_RAIL", name + "_A", "R", "C23025" if val == "300R" else "C22828"); led3(ref, "%s %s" % (name, colour), name + "_A", name + "_K"); rn += 1
# TX lamp: hardware from TR_APRS (the real PTT mirror of D8's KEY line), lamp test through a BAT54 from U2
r("R%d" % rn, "300R", "LED_RAIL", "TX_A", "R", "C23025"); rn += 1; led3("D3", "TX red (RF hazard)", "TX_A", "TX_K")
nfet("Q3", "Q3_G", "GND", "TX_K"); r("R%d" % rn, "1k", "TR_APRS", "Q3_G", "R", "C21190"); rn += 1; r("R%d" % rn, "100k", "Q3_G", "GND", "R", "C25803"); rn += 1
part("D17", "Device", "D_Schottky", "BAT54 lamp-test tie", "SOD123", {"2": "TX_K", "1": "TX_LAMPTEST"}, "C7502705")
# THE HARDWARE EMCON LAMP (MESHSAT-1357 round 8; EMCON.md section 5, SD-EMC-6, the condition on which the one element every transmitter's
# inhibit shares, the SW_EMCON toggle and the TX_INHIBIT_n conductor, is accepted; requirement CON-021, open item S-44). Until round 8 no
# indication of the EMCON lines was independent of firmware: the TX lamp's anode is LED_RAIL, which exists only while the controller
# drives PANEL_PWM, and the e-paper's EMCON page needs the controller and the display-owning bridge. D22 lights only while BOTH lines read
# LOW here, so it also exposes U9's output stuck high (every row on EMCON_HW released while board D's KEY gate stays inhibited) and a
# toggle at EMCON whose contact leaves TX_INHIBIT_n high. The gate is one TI SN74LVC1G57 (SCES414P, November 2016; filed for v2/vendor
# from drafts/c/datasheets): pins 1 In1, 2 GND, 3 In0, 4 Y, 5 VCC, 6 In2 (DBV, page 3); Table 1 (page 8) gives Y = H for In2 L, In1 L,
# In0 L and Y = L in the other three rows with In1 L, so In1 on GND makes Y = NOR(In0, In2), the configuration of its Figure 7. Its inputs
# are Schmitt triggers ("allows for noisy or slow inputs", 8.3.1, page 8), which TX_INHIBIT_n needs: it rises through R14 and C24 with a
# 77 us time constant (17 us since EQ-25), the reason U9 is a 74LVC1G17. VT+ is 1.5 to 1.87 V at VCC 3 V and 2.16 to 2.74 V at 4.5 V, VT- 0.84 to 1.19 V at
# 3 V (6.5, page 5); the sheet has no 3.3 V row, and interpolating linearly, as R14's note does for U9, puts VT+ at about 2.04 V at
# most, against the 2.57 V TX_INHIBIT_n rests at since EQ-25 and U9's rail-to-rail EMCON_HW. II +-1 uA, Ioff +-10 uA at VCC 0 ("Ioff supports partial-
# power-down mode", page 1; 6.5, page 5), so what it adds to each line with this board unpowered is a bounded current for R4T-D37's sums.
# Its output drives Q7 through R48 (100R, as Q2 and Q4 are driven), and R49 (10k) holds the gate low while U14 is unpowered: 10 uA of Ioff
# into 10k is 0.10 V against the FET's VGS(th) minimum of 0.6 V. Q7 is the Vishay Si2300DS-T1-GE3 already fitted as Q6 (document 65701,
# S10-0111-Rev. A, v2/vendor/vishay/vishay-si2300ds.pdf, page 2, TJ 25 C): RDS(on) 85 mOhm max at VGS 2.5 V and 2.6 A, VGS(th) 0.6 to 1.5 V,
# IGSS +-100 nA. Lit, U14 sources the 0.32 mA R49 draws; the row that bounds VOH at that load is the 16 mA one, at least 2.4 V at VCC 3 V
# (6.5, page 5; the VCC - 0.1 V row is for 100 uA). That is 0.9 V over Q7's maximum threshold and 0.1 V under the 2.5 V its on-resistance
# is stated at, for a 6.4 mA lamp against the 2.6 A that figure is stated at: the channel is not the lamp's limit, an inference from
# stated figures and recorded as one (bench E-02 lights the lamp). The 2N7002 on this board states RDS(on) only at 5 V and 10 V, which is
# why it is not used here (L7). The lamp is fed from LED_RAIL_SW through R47 (470R, the MAIN ring's
# value), ahead of Q1, so it lights with the controller dead, in reset or unflashed, and is dark in BLACKOUT (the LIGHTING toggle's pole
# 1 is open), as every emissive indicator is. About (5.0 - 2.0) / 470 = 6.4 mA with an amber lamp's 2 V; its level against the NVG mode
# is the PANEL.md writer's to set (EMCON.md section 8), and only R47 moves. Amber, because NVG mode shows "red and amber indicators only"
# (PANEL.md section 8) and red is the TX lamp's RF-hazard colour beside it (taken by the session under the owner's standing rule of 26
# September 2026). It needs one light-guide hole beside SW_EMCON in the face plate, which is the plate owner's (panel1450.py).
ic("U14", 6, "SN74LVC1G57DBVR configurable gate wired as a 2-input NOR, Schmitt inputs (TI, SOT-23-6: 1 In1 on GND, 2 GND, 3 In0 TX_INHIBIT_n, 4 Y, 5 VCC, 6 In2 EMCON_HW): the EMCON lamp's gate, high only while both EMCON lines read low", "SOT236",
   {"1": "GND", "2": "GND", "3": "TX_INHIBIT_n", "4": "EMCLAMP_Y", "5": "+3V3", "6": "EMCON_HW"}, "C485080")
c("C41", "100n", "+3V3", "GND", "C", "C14663")
r("R48", "100R", "EMCLAMP_Y", "EMCLAMP_G", "R", "C22775"); r("R49", "10k", "EMCLAMP_G", "GND", "R", "C25804")
part("Q7", "Transistor_FET", "2N7002", "Si2300DS-T1-GE3 N-FET (Vishay, SOT-23, G S D like the 2N7002 symbol; RDS(on) 85 mOhm max at VGS 2.5 V, VGS(th) 0.6 to 1.5 V): the EMCON lamp's sink", "SOT23", {"1": "EMCLAMP_G", "2": "GND", "3": "EMCLAMP_K"}, "C72271")
r("R47", "470R", "LED_RAIL_SW", "EMCLAMP_A", "R", "C23179"); led3("D22", "EMCON amber (hardware, no processor)", "EMCLAMP_A", "EMCLAMP_K")
# --- switches (bench parts on flying leads; footprints = panel hole + lead pads)
part("SW_MAIN", "Connector_Generic", "Conn_01x04", "MAIN PWR 19 mm momentary, green ring (to A22 J_MAINSW); C&K ATP19-SL1-603-B0SA-03G; silicone gasket washer under the bezel", "SW19", {"1": "MAINSW_A", "2": "MAINSW_B", "3": "MAINRING_A", "4": "GND"})
r("R%d" % rn, "470R", "LED_RAIL_SW", "MAINRING_A", "R", "C23179"); rn += 1
part("SW_PI", "Connector_Generic", "Conn_01x04", "PI 16 mm recessed momentary, amber ring (PI_SHDN_REQ to the modules through the controller); C&K ATP16-SL1-403-M0SA-04G; silicone gasket washer under the bezel", "SW16", {"1": "PIJ2_A", "2": "PIJ2_B", "3": "PIRING_A", "4": "PIRING_K"})
r("R%d" % rn, "300R", "LED_RAIL", "PIRING_A", "R", "C23025"); rn += 1
part("SW_TEST", "Connector_Generic", "Conn_01x04", "TEST/ACK 16 mm momentary, white ring; C&K ATP16-SL1-203-M0SA-04G; silicone gasket washer under the bezel", "SW16", {"1": "TEST_SW", "2": "GND", "3": "TESTRING_A", "4": "GND"})
r("R%d" % rn, "470R", "LED_RAIL", "TESTRING_A", "R", "C23179"); rn += 1
# SW_SOS, SW_EMCON and SW_ZERO are the same APEM 5636ADKB-2V: lug 2 is the common (APEM 5000 series sheet, page 6, 5636 row: 1-2 in
# lever position I, 2-3 in position III; v2/vendor/seals/apem-5000-series-datasheet-rs-copy.pdf), so lug 2 on GND and lug 1 on the
# sense line is the maker's own wiring; which lever position the hinged cover forces is an assembly item (26 September 2026 fix-up).
part("SW_SOS", "Connector_Generic", "Conn_01x03", "SOS locking toggle, maintained (APEM 5636ADKB-2V, both positions locked, red boot, hinged safety cover per 32.50; ruling 32.13); K front seal in the keyed 6.5 hole; the controller acts after 2 s closed", "TGL3", {"1": "SOS_SW", "2": "GND", "3": "NC"})
part("SW_EMCON", "Connector_Generic", "Conn_01x03", "EMCON locking toggle (closed = TX inhibit, a hardware line: TX_INHIBIT_n low and EMCON_HW low, the same sense; APEM 5636ADKB-2V, hinged safety cover); K front seal in the keyed 6.5 hole", "TGL3", {"1": "TX_INHIBIT_n", "2": "GND", "3": "NC"})
# 26 September 2026 (W5-ZEROIZE-4, owner rulings D-03.1 to D-03.3): the value string promised "assert the disk-key wipe (32.52)", a line
# that exists in no netlist. It now says what the hardware does (the closed toggle pulls ZEROIZE_SW low and the panel controller alone reads
# it) and names the rest as the firmware behaviour the owner ruled (D-03): read at boot before any slot powers, the crypto-erase after 5 s
# closed. The erase itself is not stated as a fact of this board, because its precondition, an erasable slot map in the secure element
# (NDA datasheet), is still open (fix-up of 26 September 2026). Lug 2 is the common per APEM's 5636 row (see the U3 note above).
part("SW_ZERO", "Connector_Generic", "Conn_01x03", "ZEROIZE locking toggle, maintained (APEM 5636ADKB-2V, single pole ON-NONE-ON, lug 2 common, hinged safety cover; ruling 32.13); K front seal in the keyed 6.5 hole; closed = ZEROIZE_SW low, read by the panel controller alone (GPIO22); ruled firmware behaviour (owner D-03): read at boot before any slot powers, crypto-erase after 5 s closed", "TGL3", {"1": "ZEROIZE_SW", "2": "GND", "3": "NC"})
# power-button leads: ferrite + 100 nF at the panel end (the leads pass the antenna feeds)
part("FB1", "Device", "L", "ferrite 600R", "FB", {"1": "MAINSW_A", "2": "MAINSW_A2"}, "C1002"); part("FB2", "Device", "L", "ferrite 600R", "FB", {"1": "MAINSW_B", "2": "MAINSW_B2"}, "C1002")
c("C26", "100n", "MAINSW_A2", "MAINSW_B2", "C", "C14663")
part("J_MAINSW", "Connector_Generic", "Conn_01x02", "MAIN button lead to A22 J_MAINSW (XH2.5 at the A22 end): two solder lands on the underside, soldered and beaded", "XH2", {"1": "MAINSW_A2", "2": "MAINSW_B2"})
part("FB3", "Device", "L", "ferrite 600R", "FB", {"1": "PIJ2_A", "2": "PIJ2_A2"}, "C1002"); part("FB4", "Device", "L", "ferrite 600R", "FB", {"1": "PIJ2_B", "2": "PIJ2_B2"}, "C1002")
c("C27", "100n", "PIJ2_A2", "PIJ2_B2", "C", "C14663")
part("J_PIJ2", "Connector_Generic", "Conn_01x02", "PI button lead: two solder lands on the underside (the controller reads it as the module shutdown request)", "XH2", {"1": "PIJ2_A2", "2": "PIJ2_B2"})
# THE TWO BUTTON LEADS LEAVE THE CASE AND HAD NO CLAMP ON THEM (rule TRN-001, 16 September 2026). A person's
# hand on the MAIN or the PI button is the transient source, and what stood between that hand and the chip at
# the other end of the lead was a 600 R bead and a 100 nF across the pair, which is an EMI filter: it slows the
# edge and passes the energy on. Both pairs sit at or below 3.3 V, so the array this board already uses three
# times is the right standoff and not a new part on the BOM: the LTC2954's PB pin is a current-source pull-up
# whose OPEN-CIRCUIT voltage is 1.0 to 2.0 V (ltc2954.pdf, VPB(VOC), 1.6 V typical at -1 uA), so MAINSW_A2
# rides at about 1.6 V and is shorted to its return when the button is pressed; PIJ2_A2 is the same part's
# open-drain INT output, held at +3V3 by R3 on board A. The B line of each pair is the lead's own return and
# is GND at the far end, so its diode to this board's ground is what gives the discharge somewhere to go that
# is not the lead. The LTC2954 declares +-10 kV HBM on PB, which is the part being built for a button and is
# not a substitute for a clamp: HBM is a 1.5 k / 100 pF hand model and IEC 61000-4-2 contact discharge is a
# 330 R / 150 pF waveform with several times the energy at the same voltage.
esd("U10", "MAINSW_A2", "MAINSW_B2", "+3V3"); esd("U11", "PIJ2_A2", "PIJ2_B2", "+3V3")
# --- e-paper: the bare E2370KS0C1 on a 24-way ZIF (top strip, top side) with the PDi rev 02 driving circuit behind a P-FET power switch (leakage: "connect to a transistor switch")
synth("J_EPD", "EPD24", "Hirose FH34SRJ-24S-0.5SH ZIF for the E2370KS0C1 flex (0.5 mm, 24 way; pin names per the PDi driving circuit note rev 02)", "ZIF24",
     {2: "EPD_GDR", 3: "EPD_RESE", 5: "EPD_VDHR", 8: "GND", 9: "EPD_BUSY", 10: "EPD_RST", 11: "EPD_DC", 12: "EPD_CS", 13: "EPD_SCL", 14: "EPD_SDA", 15: "EPD_VCC", 16: "EPD_VCC", 17: "GND", 18: "EPD_VDDD",
      20: "EPD_VDH", 21: "EPD_VGH", 22: "EPD_VDL", 23: "EPD_VGL", 24: "EPD_VCOM", 25: "GND", 26: "GND"})
part("Q5", "Transistor_FET", "AO3401A", "AO3401A P-FET: the e-paper's supply switch (EPD_PWR_n low = on)", "SOT23", {"1": "EPD_PWR_n", "2": "+3V3", "3": "EPD_VCC"}, "C15127"); r("R%d" % rn, "10k", "EPD_PWR_n", "+3V3"); rn += 1
c("C28", "4.7u", "EPD_VCC", "GND", "C10u"); c("C29", "100n", "EPD_VCC", "GND")
part("L1", "Device", "L", "10uH ATNR4010100MT 0.8 A (the boost inductor)", "L4020", {"1": "EPD_VCC", "2": "EPD_SW"})
# THE BOOST SWITCH MEETS THE PANEL MAKER'S VOLTAGE CRITERION (26 September 2026, MESHSAT-1357 round 4). PDi Rev.02 page 4 note (1) asks
# for "RDS<200m ohm ..., VDDS=30V, VGS<2.5V@Id=0.5A"; the Si2302CDS fitted until now is a 20 V part (Vishay 68645, S12-2336-Rev. D:
# VDS 20 V), below the drain rating every part PDi lists carries, on a node that swings to the positive gate rail plus a diode. The
# replacement is one PDi names, the Vishay Si2300DS-T1-GE3 (document 65701, S10-0111-Rev. A: VDS 30 V, VGS +-12 V, RDS(on) 85 mOhm max
# at VGS 2.5 V, VGS(th) 0.6 to 1.5 V, TJ -55 to +150 C, SOT-23 with 1 G 2 S 3 D, the same land and pin map). LCSC C72271.
part("Q6", "Transistor_FET", "2N7002", "Si2300DS-T1-GE3 N-FET (Vishay, SOT-23, G S D like the 2N7002 symbol; VDS 30 V, RDS 85 mOhm max at VGS 2.5 V, VGS(th) 0.6 to 1.5 V; named by PDi Rev.02): the boost switch on GDR", "SOT23", {"1": "EPD_GDR", "2": "EPD_RESE", "3": "EPD_SW"}, "C72271")
r("R%d" % rn, "0.47R 1%", "EPD_RESE", "GND"); rn += 1
# THE THREE RECTIFIERS POINT THE WAY THE PANEL MAKER DRAWS THEM (26 September 2026, S-09, adjudication A03, finding F-IN-01 extended).
# Device:D_Schottky pin 1 is K and pin 2 is A, and pad 1 of D_SOD-123F is the cathode; PANJIT's SS2020FL~SS20100FL sheet (SS2020FL_SERIES
# REV.10S, 17 Aug 2017, SOD-123FL) draws "1 Cathode, 2 Anode", colour band on the cathode. PDi's driving-circuit note Rev.02 page 3 puts the
# VGH diode's anode on the L1/MOSFET switch node and its cathode on VGH (pin 21, 1 uF to GND); the pump clamp's anode on the pump node and
# its cathode on GND; the VGL diode's cathode on the pump node and its anode on VGL (pin 23, "Negative Gate driving voltage", page 7).
# As generated at 82dd1e4d all three were the other way round: VGH could not charge and VGL would have charged positive. The code is
# pinned here to PANJIT's own part, the one PDi names (LCSC C268712, PANJIT SS2040FL: 40 V, 2 A, TJ -50 to +150 C), so no filler can
# substitute a same-named part of another maker (the generated PARTS.md row still carries C55259975, a FUXINSEMI part, from the C17 BOM).
part("D19", "Device", "D_Schottky", "SS2040FL: EPD_SW -> VGH", "SOD123F", {"1": "EPD_VGH", "2": "EPD_SW"}, "C268712"); c("C30", "1u 25V", "EPD_VGH", "GND")
# THE PUMP CAPACITOR IS THE 4.7 uF THE MAKER DRAWS (26 September 2026). PDi Rev.02 page 3 labels the capacitor from the switch node to the
# pump node "4.7uF/25V" and its BOM (page 10, item 2) lists "CAP 4.7uF 25V 0603"; this board carried 1 uF there. Murata
# GRM188R61E475KE11D (0603, X5R, 4.7 uF, DC 25 V, -55 to +85 C; Murata reference sheet GRM188R61E475KE11-01), LCSC C90057.
c("C31", "4.7u 25V", "EPD_SW", "EPD_PUMP", "C", "C90057"); part("D20", "Device", "D_Schottky", "SS2040FL: pump clamp", "SOD123F", {"1": "GND", "2": "EPD_PUMP"}, "C268712"); part("D21", "Device", "D_Schottky", "SS2040FL: pump -> VGL", "SOD123F", {"1": "EPD_PUMP", "2": "EPD_VGL"}, "C268712"); c("C32", "1u 25V", "EPD_VGL", "GND")
for i, net in enumerate(("EPD_VDHR", "EPD_VDDD", "EPD_VDH", "EPD_VDL", "EPD_VCOM"), 33): c("C%d" % i, "1u 25V", net, "GND")
# THE PANEL'S OWN CHARGE PUMPS, JUDGED BY THE PANEL MAKER (16 September 2026, rule CMP-001). These ten nets
# are the source and gate supplies the driver builds inside the glass, and this board only carries the boost
# inductor, the pump capacitors and the two Schottkys the reference circuit asks for. Their peaks live in a
# driver datasheet that is not published, so declaring a voltage here would be inventing one, which is the
# invention this rule exists to stop; and reporting them as unknown loses a real comparison, because the panel
# maker STATES THE PART. PDI's driving-circuit note rev 02 (v2/vendor/pdi/pdi-epd-driving-circuit-rev02.pdf)
# specifies "Capacitors 25V 0603" for this circuit and lists 1 uF 25 V 0603 in its own bill of materials, and
# every capacitor on these nets here is exactly that. `derate.py` records the citation instead of a number.
# 26 September 2026: the pump capacitor C31 is the 4.7 uF 25 V 0603 of BOM item 2, the others the 1 uF 25 V 0603 of item 1.
_PDI = ("PDI driving-circuit note rev 02, the components table and its bill of materials: 'Capacitors 25V "
        "0603', 'CAP 1uF 25V 0603' and 'CAP 4.7uF 25V 0603' for this exact pump and stabilising network "
        "(v2/vendor/pdi/pdi-epd-driving-circuit-rev02.pdf). Every capacitor this board puts on that net is "
        "the 25 V 0603 part the panel maker specifies there: 1 uF on the stabilising pins and 4.7 uF for the "
        "pump capacitor from the switch node to the pump node, as the page 3 figure labels it")
for _en in ("EPD_VGH", "EPD_VGL", "EPD_VDH", "EPD_VDL", "EPD_VDHR", "EPD_VCOM", "EPD_VDDD",
            "EPD_SW", "EPD_PUMP"):
    _intent.node(_en, None, "a charge-pump node of the e-paper driver, inside the panel's own glass: this "
                 "project states no voltage for it and does not need to, because the panel maker states the "
                 "part", vendor_reference=_PDI)
_intent.node("GND", 0.0, "the board's reference, so a part between a live net and ground is judged against "
             "the live net rather than reported as sitting on an undeclared one")
# --- sounder: IP67 panel-mount part in its own sealed hole on the face, driven on +5V through Q4 from the controller's PWM1; ACK mutes in firmware
part("BZ1", "Device", "Buzzer", "IP67 panel-mount sounder, 5 V DC continuous, bezel gasket on the face, two flying leads (Floyd Bell MC-09-530-Q class)", "BZ", {"1": "BZ_K", "2": "+5V"})
# BZ_K IS A SWITCHED NODE AND IT WAS DECLARED AS NOTHING AT ALL (20 September 2026; appendix 32.237). It is
# the sounder's low side between BZ1 and Q4's drain, so it sits at the 5 V rail while the FET is off and at
# the FET's own on-state drop while it conducts. It is not a rail (a drop budget in percent means nothing on
# a switched leg) and it is not nothing: CMP-001 asks what voltage a part on a net can see, and this one sees
# the panel's 5 V.
_intent.node("BZ_K", 5.0, "the sounder's low side between BZ1 and Q4's drain: it sits at the +5V rail while "
             "the FET is off and at its on-state drop while it conducts")
nfet("Q4", "Q4_G", "GND", "BZ_K"); r("R%d" % rn, "100R", "PWM1", "Q4_G", "R", "C22775"); rn += 1; r("R%d" % rn, "100k", "Q4_G", "GND", "R", "C25803"); rn += 1
# --- ambient light sensor (right strip, top side, under its own Mentor light guide) and the camera module's mount (its USB lead goes to B16's J_CAM)
ic("U_LIGHT", 4, "Vishay VEML7700 ambient light sensor (1 SCL 2 VDD 3 GND 4 SDA), I2C 0x10", "VEML", {"1": "SCL", "2": "+3V3", "3": "GND", "4": "SDA"}, "C504893"); c("C38", "100n", "+3V3", "GND")
# 15 Sep 2026: a hole is not a BOM line. The library MountingHole footprint is excluded from the position file, so the two
# camera holes reached the BOM and not the CPL and C17's deliverable was refused for "every BOM designator is in the CPL".
for i in (1, 2): part("CAM_H%d" % i, "Mechanical", "MountingHole", "M2 screw of the USB camera module (25 x 25 board, sheet owed) behind the plate's sealed window", "CAMH", {}, in_bom=False)
for i in (1, 2): part("J_HSJ%d" % i, "Mechanical", "MountingHole", "U-174/U headset jack %d (Amphenol Nexus class, drawing owed): 17 mm hole through the backer, bushing nut below; its five leads run to D8 J_HS%d" % (i, i), "HSJ", {})
# --- chassis bond: the eight standoff screws through GND ring pads (MIL-STD-461 bonding of the aluminium plate)
for i in range(1, 9): part("H%d" % i, "Mechanical", "MountingHole_Pad", "M3 x 6 into the face plate's self-clinching standoff: GND bond to the plate", "MHPAD", {"1": "GND"})
for i, net in enumerate(("+5V", "+3V3", "GND", "EXP_INT", "TX_INHIBIT_n", "EMCON_HW", "ZEROIZE_HW", "SPARE1", "SPARE2", "SPARE3", "SPARE4", "SPARE5", "SPARE6", "SPARE7", "SPARE8", "SPARE9", "SPARE10", "SPARE11", "SPARE12", "EPD_BUSY", "EPD_VGH", "EPD_VGL", "HB1", "HB2", "HB3", "SLOT_EN1", "SLOT_EN2", "SLOT_EN3", "HDMI_SEL1", "HDMI_SEL2", "PI_SHDN_REQ", "PI_KILL", "SHORE_INHIBIT", "PIJ2_A", "PIJ2_B"), 6): tp("TP%d" % i, net)
# THE TEST ACCESS OWED BEFORE PLACEMENT (26 September 2026, rule TST-001, W5 test-access list section 3, MESHSAT-1357 round 4). Appended
# after TP40 so no existing test point is renumbered. ZEROIZE_SW is the local sense HW6 times from the switch edge; SDA and SCL, SOS_SW,
# TEST_SW and TR_APRS are the lines W5 names; C_DVDD is the RP2040 core; BOOT_J is the BOOTSEL node beside JP1, which a probe grounds through
# R5's 1k exactly as the solder jumper does (a pad on QSPI_SS itself would let a probe short the flash select without that 1k).
for i, net in enumerate(("ZEROIZE_SW", "SDA", "SCL", "SOS_SW", "TEST_SW", "TR_APRS", "C_DVDD", "BOOT_J"), 41): tp("TP%d" % i, net)
# ================================================================= EQ-25 AND PWR-001 (MESHSAT-1357, stream w4c, 27 September 2026)
# TX_INHIBIT_n FAILS SAFE WITH THIS BOARD UNPOWERED (EQ-25, open item S-64, finding W3T-F1 of the RF-002 walk). With this board unpowered
# the line was held only by the three consumer pull-downs, A R145, B R59 and D R2, 100k each and taken at 5 percent because their values
# state none (3 x 105k in parallel, 35.0k), against 31 uA of stated pin current: this board's U9 (74LVC1G17, IOFF 10 uA at VCC 0, Diodes
# DS35124 Rev. 8-2 page 4) and U14 (SN74LVC1G57, Ioff 10 uA, TI SCES414P 6.5), board D's U12 (10 uA) and board A's U35 and U37
# (SN74AUP1G08, 0.5 uA each). 31 uA x 35.0k = 1.09 V, over the 0.8 V VIL the walk (tx_inhibit.py, VIL_LOW) applies to every gate that
# reads it; the walk takes an unpowered part at its Ioff (round 6), so this is a FAIL under the tree's worst-case convention, and the
# remedy is margin. Taken by the session under the owner's standing rule of 26 September 2026: option (a) of S-64, R50 (10k 1 percent,
# UNI-ROYAL 0603WAF1002T5E, C25804) from the line to GND on this board and R14 10k to 2.2k 1 percent (0603WAF2201T5E, C4190), both 0603
# 100 mW. The figures, resistors at the adverse end of their stated tolerance and +3V3 5 percent low as the walk takes them:
#   failed safe, this board unpowered: R50 at 10.1k in parallel with 35.0k is 7.84k, x 31 uA = 0.24 V, 0.56 V under VIL. The panel ribbon
#     out: boards B, A and D keep their own 35.0k against 11 uA, 0.39 V, as before. The A-B ribbon out: this board and B, 10.1k with 105k,
#     9.21k x 20 uA = 0.18 V; A and D, 52.5k x 11 uA = 0.58 V, as before. The A-D mezzanine out: A, B and this board 0.18 V (1.10 V
#     before). The walk itself reads 0.243 V and 0.178 V for the two states that failed at 1.085 V and 1.103 V (stream w4c's records);
#   released (toggle open, this board powered): nominal 3.3 V x 7.69k / (2.2k + 7.69k) = 2.57 V; at the adverse ends (3.135 V, R14
#     2.222k, R50 9.9k, the three at 95k, the 31 uA sunk through the 1.72k Thevenin) 2.37 V: over VIH 2.0 V and over the VT+ this file
#     reads at 3.3 V for U9 (about 2.15 V) and U14 (about 2.04 V). With R14 10k the same ends read 2.11 V, under U9's 2.15 V, so the
#     change widens the released margin too;
#   asserted (toggle closed, this board powered): the contact holds the line at ground, 1.6 mA x its 10 mOhm (APEM 5000 series, page
#     2, 'Initial contact resistance : 10 mOhm max'), about 16 uV. R14 then draws 3.465 V / 2.178k = 1.59 mA, inside the 5636ADKB's
#     gold-plated contacts' range (AD, page 2: 10 uA at 5 V to 100 mA at 30 VDC) and under the walk's 4 mA pull limit (PULL_MA_MAX);
#     R14 dissipates 5.5 mW, R50 0.7 mW released;
#   latency: asserting is the contact itself; C24 discharges through it, so the line is at ground from the first touch and settled
#     within the contact bounce (2 ms max, APEM page 2), and U9's EMCON_HW follows in nanoseconds; release rises with 1.71k x 10 nF =
#     17 us toward 2.57 V and crosses U9's 2.15 V after about 31 us (144 us with R14 10k); with this board's supply gone the line
#     falls with +3V3 and R50 with the three pull-downs then hold it, 7.84k x 10 nF = 78 us. Each is far inside REQ-071's 1 s.
# Options not taken: (b) board B's R59 to 10k 1 percent with R14 2.2k (0.26 V; two boards) and (c) the three pull-downs to 47k with R14
# 4.7k (0.51 V; four boards): (a) is one board, the board whose round 8 lamp gate added the current, and reads the lowest level. Reverse by
# (b) or (c) if a measured Ioff on the bench (E-01, E-11) or a later reader changes the sums; the arithmetic is in the w3t records.
_intent.node("TX_INHIBIT_n", 3.333, "the hardware EMCON line at its source: R14 (2.2k 1 percent) to +3V3 and SW_EMCON to GND, R50 (10k) and the "
             "three consumer pull-downs to GND; at most +3V3 at the TLV75533's 1 percent (TI SBVS320D, 'Output accuracy: 1%'), and no "
             "part takes its supply from it (U9, U14 and the far gates read it)", v_work=3.333)
# THE LED RAIL SENSE IS A DIVIDER (finding W4C-F1, read while declaring LED_RAIL_SW for PWR-001; taken by the session under the owner's
# standing rule of 26 September 2026). R15 alone joined the 5 V LED_RAIL_SW to GPIO26 (ADC0, U3 pin 38). The RP2040 datasheet
# (v2/vendor/rp2040/rpi-rp2040-datasheet.pdf, build-version 3184e62-clean): 'the voltage on the ADC analogue inputs must not exceed IOVDD
# ... Voltages greater than IOVDD will result in leakage currents through the ESD protection diodes' (2.9.5 note and 4.9 note), and the
# absolute maximum VPIN is IOVDD + 0.5 V (Table 622). Through 10k the pin sat on its diode above IOVDD with about 0.15 mA into +3V3
# whenever the lights were on. PANEL.md's LED-rail row already calls it a divider. R51 (10k, C25804) to GND makes it one: at most
# 5.25 V x 10.1k / (9.9k + 10.1k) = 2.65 V, under the rail's 3.135 V floor, and the pad's own 50 to 80k pull-down (Table 625) only
# lowers it; 0 V at BLACKOUT, where pole 1 is open and R15 and R51 hold it down. The firmware threshold for 'present' is the PANEL.md
# writer's (about 2.5 V present, 0 V absent). Reverse by a measured reason the pin must see the rail undivided (none is known).
# PWR-001 ON THIS BOARD: EVERY POWER NET DECLARED, AND THE ELEVEN UNDECIDED NETS SETTLED (EQ-19 for board C; the kinds follow board D's
# and E's SC-57 and board B's stream w3b: a rail where a net carries a current to more than one place or through a switch to a load, a
# node where it is one part's own supply, a lamp's feed or a signal). Session decisions under the owner's standing rule of 26 September
# 2026; reverse any node by a load on it that is another part's supply, and any current by a measurement at bring-up.
#   C_DVDD: a NODE, the RP2040's own core regulator output. It carries U3's VREG_VOUT (pin 45) and DVDD (pins 23 and 50) with C14, C15,
#     C44 and TP47 and nothing else. The regulator is set to 1.10 V at power-on and firmware may select 0.80 to 1.30 V in 50 mV steps
#     (datasheet 2.10.3; Table 189, VSEL 1111 = 1.30 V); DVDD's operating range is 1.05 / 1.1 / 1.16 V (Table 634).
_intent.node("C_DVDD", 1.30, "the RP2040's own core regulator output VREG_VOUT (U3 pin 45) to its DVDD pins 23 and 50: 1.10 V at power-on, "
             "at most 1.30 V by VSEL (RP2040 datasheet 2.10.3, Table 189), 1.16 V the operating maximum (Table 634); one part's own "
             "supply, as board D's PCM2912A outputs are declared", v_work=1.16)
#   EPD_VCC: a RAIL, the e-paper's switched supply from +3V3 through Q5 to the panel's VDDIO and VDD (J_EPD 15 and 16) and to the boost
#     inductor L1. No held document states the panel's own current; the driver it carries (UC8253c, PDi flyer E2370KS0C1) states 0.1 mA
#     IVDD, 0.1 mA IVDDIO and 20.0 mA IVDDA operating maximum at VDD 3.0 V and 25 C (UltraChip UC8253c A0.6, DC characteristics, page 59; filed as a
#     draft for v2/vendor/pdi/ by stream w4c), so the typical 30 mA is those 20.2 mA plus an INFERRED 10 mA for the boost's own inductor
#     current, whose output power no held document states (to be read at bring-up). The peak is the boost's switch-current class the
#     panel maker states for Q6 ('VGS<2.5V@Id=0.5A or less', PDi driving-circuit note Rev.02 page 4 note (1)): during the on-phase the
#     inductor's current is this rail's. Q5 turns it on (EPD_PWR_n low, GPIO29).
_intent.rail("EPD_VCC", 3.3, _EPD[0], _EPD[1], "Q5", loads={"J_EPD": 0.0202, "L1": 0.500}, converted=False, fed_from="+3V3", switch="Q5",
             enable_net="EPD_PWR_n", budget=0.03,
             note="the e-paper's switched supply: Q5 (AO3401A) from +3V3 to the panel's VDDIO and VDD and to the boost inductor L1. 30 mA "
                  "typical = the UC8253c's 20.2 mA operating maximum (IVDD 0.1, IVDDIO 0.1, IVDDA 20.0 mA at 3.0 V and 25 C, UltraChip UC8253c A0.6 page 59) "
                  "plus 10 mA INFERRED for the boost, read at bring-up; 0.5 A peak into L1 = the boost switch's current class (PDi "
                  "Rev.02 page 4 note 1). Budget 3 percent as +3V3's: the driver's supply range is 2.3 to 3.6 V (UC8253c page 59)")
# THE FEEDER COVERS THE CHILD (W4C-F5): power_path's feed sum judges typical currents only, so the peak is held here, where both
# figures are written. A change to either rail that leaves +3V3 under its own loads plus EPD_VCC stops the generator.
_f3, _fe = _intent.rail_amps("+3V3"), _intent.rail_amps("EPD_VCC")
if _f3[0] + 1e-9 < _P3V3_OWN[0] + _fe[0] or _f3[1] + 1e-9 < _P3V3_OWN[1] + _fe[1]:
    raise SystemExit("gen_sch_c: +3V3 declares %.3f / %.3f A and its own loads plus EPD_VCC take %.3f / %.3f A (W4C-F5): raise "
                     "+3V3 with its child" % (_f3[0], _f3[1], _P3V3_OWN[0] + _fe[0], _P3V3_OWN[1] + _fe[1]))
#   LED_RAIL_SW and LED_RAIL: RAILS, the lighting supply. +5V through the LIGHTING toggle's pole 1 (SW_LIGHT, open at BLACKOUT) is
#     LED_RAIL_SW; Q1 (AO3401A), gated by Q2 from PANEL_PWM through Q1_G, makes LED_RAIL. Their current leaves through the lamps' series
#     resistors, so those are the loads. The 3 mm lamps are hand-fitted panel parts with no part number (lcsc-allow.txt), so no maker
#     states their forward voltage: the typical is the 8 mA per lamp the series resistors were chosen for (the LED table above) and
#     6.4 mA for the two 470R lamps on LED_RAIL_SW (the EMCON lamp's note), and the peak takes every lamp lit with its forward drop
#     at zero on +5V 5 percent high (5.25 V / R), the bound that needs no lamp sheet. The +5V rail's own SW_LIGHT load (0.35 A) lies
#     between the two and is not moved here. The cathode side of each lamp is a node below (the expander's sink or a FET's drain).
_V5HI = 5.25   # +5V at 5 percent high
def _ohm_of(v):
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([kR]?)", v)
    return float(m.group(1)) * (1e3 if m.group(2) == "k" else 1.0)
_on = lambda net: [p for p in P if p["lib"] == "Device" and p["sym"] == "R" and net in p["nets"].values()]
_lamp_r = {p["ref"]: round(_V5HI / _ohm_of(p["value"]), 5) for p in _on("LED_RAIL")}
_led_peak = round(sum(_lamp_r.values()), 4)
_led_typ = round(0.008 * len(_lamp_r), 4)
_sw_loads = {"Q1": _led_peak, "R47": round(_V5HI / 470.0, 5), "R39": round(_V5HI / 470.0, 5),
             "R17": round(_V5HI / (2200.0 + 47.0), 5), "R15": round(_V5HI / 20000.0, 5)}   # R17 and R18 to Q2 while it conducts; R15 and R51
if sorted(r_["ref"] for r_ in _on("LED_RAIL_SW")) != sorted(k for k in _sw_loads if k.startswith("R")):
    raise SystemExit("gen_sch_c: LED_RAIL_SW's resistors changed; redeclare its loads: %s" % sorted(r_["ref"] for r_ in _on("LED_RAIL_SW")))
_intent.rail("LED_RAIL_SW", 5.0, round(_led_typ + 2 * 0.0064 + 5.0 / 2247.0 + 5.0 / 20000.0, 4), round(sum(_sw_loads.values()), 4), "SW_LIGHT",
             loads=_sw_loads, converted=False, fed_from="+5V", budget=0.05, always_on=True,
             always_on_why="no enable line: the LIGHTING toggle SW_LIGHT (pole 1) switches it by hand, open at BLACKOUT, and nothing on any "
                           "board drives it, so it can neither deadlock nor be sequenced; it follows +5V whenever the toggle is at DAY or NIGHT",
             note="the lighting supply behind the LIGHTING toggle: Q1 to LED_RAIL, the EMCON lamp D22 through R47, the MAIN ring through R39, "
                  "Q1's gate pull-up R17 and the sense divider R15 and R51. Typical: the lamps at their design currents; peak: every lamp "
                  "with no forward drop at 5.25 V. Budget 5 percent as +5V's: every load is a lamp behind its own resistor")
_intent.rail("LED_RAIL", 5.0, _led_typ, _led_peak, "Q1", loads=_lamp_r, converted=False, fed_from="LED_RAIL_SW", switch="Q1",
             enable_net="Q1_G", budget=0.05,
             note="the PWM'd lamp rail: Q1 (AO3401A) from LED_RAIL_SW, its gate Q1_G pulled down through R18 by Q2 from PANEL_PWM; %d "
                  "lamps behind their series resistors, 8 mA each by design, %.3f A with every lamp's forward drop at zero at 5.25 V"
                  % (len(_lamp_r), _led_peak))
#   The lamps' feed and return nets and the pull-up lines: NODES at the voltage the circuit states. A lamp's anode sits behind its
#     series resistor and can reach no more than its rail's 5.0 V; its cathode sits on an expander's open-drain sink (PCA9555, 5 V
#     tolerant I/O, TI SCPS131J) or a FET's drain (Q3 2N7002, Q7 Si2300DS) and can reach no more than the anode; the lamp-test tie
#     TX_LAMPTEST sits below TX_K through D17. Q1_G swings between LED_RAIL_SW and Q2's drain; RAIL_SENSE is the divider's middle.
#     The switch lines idle at +3V3 through their 10k pull-ups (R10 to R13) and their toggles short them to ground.
for _ref, _name, _col, _val in LEDS:
    _intent.node(_name + "_A", 5.0, "lamp %s's anode (%s), behind its %s series resistor from LED_RAIL: it can only reach that rail" % (_ref, _name, _val))
    _intent.node(_name + "_K", 5.0, "lamp %s's cathode on its expander's open-drain sink (PCA9555, 5 V tolerant I/O, SCPS131J): no higher than "
                 "its anode, which can only reach LED_RAIL" % _ref)
for _n, _why in (("TX_A", "the TX lamp D3's anode behind its 300R from LED_RAIL"),
                 ("TX_K", "the TX lamp D3's cathode on Q3's drain (2N7002), with the lamp-test tie D17: no higher than D3's anode"),
                 ("TX_LAMPTEST", "U2's P1.0 (PCA9555, 5 V tolerant I/O) below TX_K through the BAT54 D17: no higher than TX_K"),
                 ("PIRING_A", "the PI button ring's anode behind its 300R from LED_RAIL"),
                 ("TESTRING_A", "the TEST button ring's anode behind its 470R from LED_RAIL"),
                 ("MAINRING_A", "the MAIN button ring's anode behind its 470R from LED_RAIL_SW"),
                 ("EMCLAMP_A", "the hardware EMCON lamp D22's anode behind R47 470R from LED_RAIL_SW"),
                 ("EMCLAMP_K", "the EMCON lamp D22's cathode on Q7's drain (Si2300DS, 30 V): no higher than D22's anode"),
                 ("Q1_G", "Q1's gate between R17 from LED_RAIL_SW and R18 to Q2's drain: at most LED_RAIL_SW")):
    _intent.node(_n, 5.0, _why + "; no part takes its supply from it")
_intent.node("RAIL_SENSE", 2.65, "the LED rail sense divider's middle (R15 from LED_RAIL_SW, R51 to GND, 10k each): 5.25 V x 10.1 / 20 at "
             "most, read by GPIO26 (ADC0); W4C-F1", v_work=2.65)
for _n, _pu in (("ZEROIZE_SW", "R10"), ("TEST_SW", "R11"), ("LIGHT_DAY_n", "R12"), ("LIGHT_NIGHT_n", "R13")):
    _intent.node(_n, 3.333, "a switch line idling at +3V3 through %s (10k), shorted to GND by its toggle or button: at most +3V3 at the "
                 "TLV75533's 1 percent (TI SBVS320D); its readers take no supply from it" % _pu, v_work=3.333)
#   EPD_RESE: a NODE, the boost's current-sense node between Q6's source and R43 (0.47 ohm) to GND, read by the panel's RESE input
#     ('Current Sense Input for the Control Loop', PDi Rev.02 pin table). Its current is chopped, the switch's each on-phase. The panel
#     maker states the parts on it: the 0.47 ohm 0603 1 percent 1/10 W resistor (BOM item 9) and the Si2300DS (component table), so it is
#     declared the way the pump nodes above are, by the maker's reference, and no DC figure is invented for a chopped current.
_intent.node("EPD_RESE", None, "the e-paper boost's current-sense node: Q6's source, R43 (0.47 ohm) to GND and the panel's RESE input; "
             "a chopped switch current each on-phase, whose parts the panel maker states", vendor_reference=_PDI + "; and BOM item 9, "
             "'RES 0.47 ohm 0603 1% 1/10W', for the sense resistor on this node (page 10)")
# ----------------------------------------------------------------- emit (as B15)
POWER = {"GND": ("power", "GND")}
libsyms = kisch.libsyms; out = kisch.out; pf_n = kisch.pf_n   # the engine's objects, by reference
ROOT = str(uuid.uuid5(kisch.UUID_NS, "root:" + PROJECT))   # deterministic: a board regenerates byte for byte (10 Sep 2026)
STUB = 5.08
kisch.configure(power=POWER, stub=STUB, root=ROOT, project=PROJECT, seed=PROJECT)
byref = {p["ref"]: p for p in P}

def refs_matching(pred): return [p["ref"] for p in P if pred(p["ref"])]
SECTIONS = [("RIBBON FROM B16, 5 V, 3.3 V LDO, USB AND BUS ESD, FLAGS", ["J_PANEL", "C1", "C2", "U5", "C3", "C4", "U6", "U7", "U8", "#FLG01", "#FLG02", "#FLG03", "#FLG04", "#FLG05"]),
            ("RP2040 PANEL CONTROLLER, FLASH, CRYSTAL, BOOTSEL, BUS PULL-UPS", ["U3", "U4", "Y1", "C5", "C6", "R1", "R2", "R3", "R4", "R5", "JP1"] + ["C%d" % k for k in range(7, 17)] + ["C42", "C43", "C44"] + ["TP1", "TP2", "TP3", "R6", "D18", "R7", "R8"]),
            ("EXPANDERS 0x22 / 0x23, MODE INPUTS, EMCON AND ZEROIZE BUFFERS, STRAPS", ["U1", "U2", "C17", "C18"] + ["R%d" % k for k in range(9, 17)] + ["C%d" % k for k in range(19, 26)] + ["U9", "U12", "C39", "U13", "C40", "R46", "R50", "R51", "R52", "D23", "JP2"]),   # U9 is a buffer since 9 Sep 2026, "INVERTER" was stale; U12 and C39 added 26 Sep 2026; U13, C40 and R46 in round 8; R50 (EQ-25) and R51 (W4C-F1) 27 Sep 2026
            ("LED RAIL, INDICATORS, TX LAMP, SWITCHES AND LEADS", ["SW_LIGHT", "Q1", "R17", "R18", "Q2", "R19", "R20", "TP4", "TP5"] + [p["ref"] for p in P if p["ref"].startswith("D") and p["ref"][1:].isdigit() and int(p["ref"][1:]) <= 17] + ["R%d" % k for k in range(21, 43)] + ["Q3", "U14", "C41", "R48", "R49", "Q7", "R47", "D22", "SW_MAIN", "SW_PI", "SW_TEST", "SW_SOS", "SW_EMCON", "SW_ZERO", "FB1", "FB2", "C26", "U10", "J_MAINSW", "FB3", "FB4", "C27", "U11", "J_PIJ2"]),
            ("E-PAPER ZIF AND THE PDi BOOST, SOUNDER, LIGHT SENSOR, CAMERA MOUNT", ["J_EPD", "Q5", "C28", "C29", "L1", "Q6", "D19", "C30", "C31", "D20", "D21", "C32", "C33", "C34", "C35", "C36", "C37", "BZ1", "Q4", "U_LIGHT", "C38", "CAM_H1", "CAM_H2", "J_HSJ1", "J_HSJ2"])]
placed_refs = {r_ for _, rs in SECTIONS for r_ in rs}
SECTIONS.append(("STANDOFF SCREWS (GND BOND), TEST POINTS, THE REST", [p["ref"] for p in P if p["ref"] not in placed_refs]))
def layout(page_h):
    global out, pf_n
    out = kisch.reset_body(); placed = set(); COLW = 92.0; x = 20.0; y = 30.0
    for title, refs in SECTIONS:
        hs = []
        for ref in refs:
            p = byref[ref]; x0, x1, y0, y1 = extents(ensure(p["lib"], p["sym"])); hs.append((y1 - y0) + 2 * STUB + 12.0)
        if y + 20 > page_h and y > 30.0: x += COLW; y = 30.0
        text(title, round((x - 15.0) / 1.27) * 1.27, round((y - 4.0) / 1.27) * 1.27); y += 4.0
        for ref, h in zip(refs, hs):
            p = byref[ref]; x0, x1, y0, y1 = extents(ensure(p["lib"], p["sym"]))
            if y + h > page_h: x += COLW; y = 34.0
            cy = y + (y1 + STUB) + 4.0; gx = round((x + 20.0) / 1.27) * 1.27; gy = round(cy / 1.27) * 1.27
            if p["sym"] == "PWR_FLAG": emit_pwr_flag(p, gx, gy)
            else: emit_part(p, gx, gy)
            placed.add(ref); y += h
        y += 8.0
    missing = [p["ref"] for p in P if p["ref"] not in placed]
    if missing: raise SystemExit("unplaced parts: %s" % missing)
    return x + COLW
# EVERY DECLARATION CARRIES ITS CLASS AND ITS MAKER'S CLAUSE (MESHSAT-1357 round 8, DECOUPLING.md 8.3 item G14; decision 42, ruled by the
# session under the owner's standing rule of 26 September 2026). A capacitor's class is its ROLE as its maker describes it, never its value
# string: D, a capacitor a maker ties to a supply pin; L, a regulator's output capacitor, with the maker's value floor and ESR bound; B2, bulk
# no maker places (DECOUPLING.md section 6). Where the maker states no capacitor, the generator's own count stands and the basis says so
# (rule D1). `intent.bypass` takes no class yet (T5 of DECOUPLING.md 8.1 is the integrator's tools item), so the class and the basis are
# written onto the entry here and the intent file carries them; this board refuses its own entry without one, as T5 will.
_RP_DS = "RP2040 Datasheet, v2/vendor/rp2040/rpi-rp2040-datasheet.pdf, build-version 3184e62-clean"
_RP_HD = "Hardware design with RP2040, v2/vendor/rp2040/rpi-rp2040-hardware-design.pdf, build date 20/08/2026"
_D1 = "states no supply capacitor in its text; the generator's own 100 nF stands (DECOUPLING.md rule D1)"
def byp(cap, part_ref, pin, net, cls, basis, floor=None, esr=None):
    _intent.bypass(cap, part_ref, pin, net)
    _e = _intent._I["bypass"][-1]; _e["class"] = cls; _e["basis"] = basis
    if cls == "L": _e["floor"] = floor; _e["esr"] = esr
for _i, _pin in enumerate((1, 10, 22, 33, 42, 49)):   # the RP2040's six IOVDD pins
    byp("C%d" % (7 + _i), "U3", _pin, "+3V3", "D", _RP_DS + ", 2.9.1 (printed page 151): 'IOVDD should be decoupled with a 100nF capacitor close to each of the chip's IOVDD pins'")
byp("C13", "U4", "8", "+3V3", "D", "Winbond W25Q16JV, v2/vendor/winbond/winbond-w25q16jv-serial-flash.pdf, Revision H, " + _D1)   # the QSPI flash's VCC
byp("C14", "U3", "45", "C_DVDD", "L", _RP_DS + ", 2.10.1 (printed page 156): 'The regulator must have 1uF capacitors placed close to its input (VREG_VIN) and output (VREG_VOUT) pins'; " + _RP_HD + ", 2.1.3 (printed page 8)",
    floor="1u", esr="no number: the design guide 2.1.3 says physically small ceramic chip capacitors 'will almost certainly' meet the regulator's ESR restriction")   # VREG_VOUT (G13)
byp("C15", "U3", "50", "C_DVDD", "D", _RP_DS + ", 2.9.2 (printed page 151): 'DVDD should be decoupled with a 100nF capacitor close to each of the chip's DVDD pins'")
byp("C16", "U3", "44", "+3V3", "D", _RP_DS + ", 2.9.3 (printed page 151): 'A 1uF capacitor should be connected between VREG_VIN and ground close to the chip's VREG_VIN pin'; 2.10.1 (printed page 156)")
byp("C3", "U5", "1", "+5V", "D", "TI TLV755P, SBVS320D, v2/vendor/power/ti-tlv755p-ldo.pdf, Table 4-1 (page 3): IN, 'A capacitor with a value of 1uF or larger is required from this pin to ground'; 7.1.1 (page 15)")
byp("C4", "U5", "5", "+3V3", "L", "TI TLV755P, SBVS320D, Table 4-1 (page 3): OUT, 'A capacitor with a value of 1uF or larger is required'; 7.1.1 (page 15): 'requires an output capacitance of 0.47uF or larger for stability'",
    floor="1u nominal, 0.47u effective (Table 4-1 note 1)", esr="no number: 7.1.1 names X5R and X7R ceramics")
# The two expanders (round 8 pass 2): the maker does speak of VCC capacitors, in 11.1, and draws one in Figure 11-1; it gives no value.
_PCA = ("TI PCA9555, SCPS131J, v2/vendor/ti/ti-pca9555.pdf, 11.1 (printed page 29): 'By-pass and de-coupling capacitors are commonly used to "
        "control the voltage on the VCC pin, using a larger capacitor to provide additional power in the event of a short power supply glitch "
        "and a smaller capacitor to filter out high-frequency ripple. These capacitors must be placed as close to the PCA9555 as possible. "
        "These best practices are shown in the Section 11.2'; Figure 11-1 (printed page 29), that section's example layout, draws one "
        "'0603 Cap' on VCC and no second capacitor, and the sheet gives no value for either (Figure 9-1, printed page 24, draws none). "
        "One 100 nF per expander stands, its value by DECOUPLING.md rule D1 and its count by Figure 11-1: the session's choice under the "
        "owner's standing rule of 26 September 2026, over adding a larger part the maker neither sizes nor draws. Section 10 bounds the "
        "supply glitch the device rides through without naming a capacitor (Table 10-1, printed page 27: VCC_GH 1.2 V at VCC_GW 1 us), "
        "so the choice is reopened if the prototype's +3V3 is measured outside that bound")
byp("C17", "U1", "24", "+3V3", "D", _PCA)   # the two expanders
byp("C18", "U2", "24", "+3V3", "D", _PCA)
byp("C25", "U9", "5", "+3V3", "D", "Diodes 74LVC1G17, DS35124 Rev. 8-2, v2/vendor/diodes/diodes-74lvc1g17.pdf, " + _D1)    # the EMCON buffer
byp("C39", "U12", "5", "+3V3", "D", "Diodes 74LVC1G17, DS35124 Rev. 8-2, v2/vendor/diodes/diodes-74lvc1g17.pdf, " + _D1)   # the ZEROIZE buffer (26 September 2026)
byp("C38", "U_LIGHT", "2", "+3V3", "D", "Vishay VEML7700, document 84286 Rev. 1.8, v2/vendor/vishay/veml7700-datasheet.pdf, Application Circuit (page 6): C2 100 nF at VDD (C1 and R3 optional)")   # the light sensor
byp("C29", "J_EPD", "15", "EPD_VCC", "D", "Pervasive Displays EPD driving circuit note Rev. 02, v2/vendor/pdi/pdi-epd-driving-circuit-rev02.pdf, page 4: the 0.1 uF beside C1 on the switched supply that feeds VDDIO and VDD (DECOUPLING.md section 6, B2)")
byp("C28", "J_EPD", "16", "EPD_VCC", "B2", "Pervasive Displays EPD driving circuit note Rev. 02, pages 3 and 4: C1, 4.7 uF / 6.3 V for group G2, with no placement or distance given (DECOUPLING.md sections 6 and 6a)")
# round 8: the two RP2040 pins that had none (G9), the second DVDD pin (G13), and the two new logic parts' supplies
byp("C42", "U3", "43", "+3V3", "D", _RP_DS + ", 2.9.5 (printed page 152): 'ADC_AVDD should be decoupled with a 100nF capacitor close to the chip's ADC_AVDD pin'")
byp("C43", "U3", "48", "+3V3", "D", _RP_DS + ", 2.9.4 (printed page 151): 'USB_VDD should be decoupled with a 100nF capacitor close to the chip's USB_VDD pin'")
byp("C44", "U3", "23", "C_DVDD", "D", _RP_DS + ", 2.9.2 (printed page 151): 'DVDD should be decoupled with a 100nF capacitor close to each of the chip's DVDD pins'")
byp("C40", "U13", "5", "+3V3", "D", "Diodes 74LVC1G17, DS35124 Rev. 8-2, v2/vendor/diodes/diodes-74lvc1g17.pdf, " + _D1)   # the controller's one-way EMCON copy
byp("C41", "U14", "5", "+3V3", "D", "TI SN74LVC1G57, SCES414P, section 10 (page 12): 'For devices with a single supply, a 0.1-uF bypass capacitor is recommended', 'installed as close to the power terminal as possible'")   # the EMCON lamp's gate
_unclassed = [e["cap"] for e in _intent._I["bypass"] if not e.get("class") or not e.get("basis")]
if _unclassed: raise SystemExit("gen_sch_c: decoupling entries without a class and a maker's basis: %s" % _unclassed)
import schlayout, time as _time
PAPER, NPAGES, NCOLS, NROWS = schlayout.run(P, SECTIONS, POWER, _intent._I["bypass"], {"date": _time.strftime("%Y-%m-%d")}, os.environ.get("PHASE", ""), 'PCB-C CONTROL PANEL BACKER')   # 15 Sep 2026: one A3 page per block, real wiring (32.196)
out = kisch.out
print("layout: %d A3 pages on a %d x %d sheet -> paper %s" % (NPAGES, NCOLS, NROWS, PAPER))
hdr = '(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "%s")\n\t(paper %s)\n' % (ROOT, PAPER)
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-C CONTROL PANEL BACKER") (date "%s")' % _time.strftime("%Y-%m-%d") + ' (rev "A") (company "MeshSat") (comment 1 "Phase ' + (os.environ.get("PHASE") or "?") + ' schematic (RP2040 panel controller, PDi e-paper driver, Xenarc face, headset jacks, camera window, light sensor; appendix 32.51, 32.52, 32.60), generated by tools/gen_sch_c.py"))\n'
hdr += '\t(lib_symbols\n' + "".join("\t\t" + ser(v, 2).replace("\n", "\n\t\t") + "\n" for v in libsyms.values()) + '\t)\n'
body = "".join("\t" + s.replace("\n", "\n\t").rstrip("\t") for s in out)
open(OUT, "w").write(hdr + body + '\t(sheet_instances (path "/" (page "1")))\n)\n')
print("wrote", OUT, "parts:", len(P), "lib symbols:", len(libsyms))
nets = {}
for p in P:
    for num, net in p["nets"].items():
        if net != "NC": nets.setdefault(net, []).append("%s.%s" % (p["ref"], num))
single = [n for n, v in nets.items() if len(v) == 1]
print("nets:", len(nets), "single-pin nets (should be empty or intentional):", single)
# --- decoupling as data (8 Sep 2026, MESHSAT-862 Stage C): which capacitor serves which supply pin, so the decoupling gate measures the
# pad-to-pin distance instead of counting parts. Only supply pins: the crystal loads, the RC debounce networks, the e-paper charge pump's
# reservoirs (C30 to C37) and the LED rail bulk are not decoupling and are not listed. `intent.write` refuses an entry whose capacitor is
# not on that pin's net, so a wrong line here stops the generator.
# CLOSED in round 8 of MESHSAT-1357 (26 September 2026): ADC_AVDD (pin 43) and USB_VDD (pin 48) have their own 100 nF, C42 and C43 (G9),
# and the regulator's output carries 1 uF at VREG_VOUT plus 100 nF at each DVDD pin (G13); see the note at the RP2040's capacitors. The
# ferrite or 10 ohm this note once proposed for pin 43 is not fitted, for the reason given there.
# The panel board's only differential pair is the RP2040's own USB device port, and the RP2040's controller is USB 1.1 FULL SPEED (12 Mbps).
# The 90 ohm differential target of the shared USB class belongs to USB 2.0 high speed; requiring it here is a wrong requirement, not a strict
# one, so this board declares the class with no impedance target and `impedance_check.py` skips it (8 Sep 2026 23:05, appendix 32.76). The
# geometry stays what the router used: 0.3 mm at the class clearance. Every other board's USB pairs keep the 90 ohm target.
_intent.pair_class("USB")

_intent.write(OUT, PROJECT, P)   # 8 Sep 2026 (MESHSAT-862): design intent as data, out/<project>-intent.json
