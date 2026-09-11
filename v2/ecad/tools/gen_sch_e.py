#!/usr/bin/env python3
"""PCB-E1 DOCK, phase E6 (MESHSAT-830, 7 Sep 2026): generate the KiCad 9 schematic (netlist-style: every pin gets a
stub and a net label; power pins get power symbols). Runs on the laptop (needs the KiCad libs).
Usage: gen_sch_e.py <out.kicad_sch> <project-name>
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-e1-dock"
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
# 10 September 2026 (MESHSAT-862, red team C2): the schematic engine lives in kisch.py, one copy for the six boards.
# What stays here is this board: its part tables, its nets, its sheet layout. `ic()` is strict for every board again.
import kisch
from kisch import (U, c, emit_part, emit_pwr_flag, ensure, extents, find_sym, flatten, flatten_raw, ic, label, lib_tree, noconn, parse, part, pins_of, place_symbol, q, r, rename_units, ser, text, uq, wire)
import intent as _intent
_intent.rail("CELL_F", 14.4, 10.0, 18.0, "F3", note="the pack node after the 25 A blade F3, to the block pads")
_intent.rail("VIN_RAW", 12.0, 8.0, 10.0, "L2", note="shore and vehicle entry after the filter choke, 10 A fuse")
SYMDIR = "/usr/share/kicad/symbols/"

# ----------------------------------------------------------------- s-expression helpers
LIBCACHE = {}

# ----------------------------------------------------------------- the design
FP = {
 "R": "Resistor_SMD:R_0603_1608Metric", "C": "Capacitor_SMD:C_0603_1608Metric", "C10u50": "Capacitor_SMD:C_1206_3216Metric", "LED": "LED_SMD:LED_0603_1608Metric",
 "TVS": "Diode_SMD:D_SMC", "SO8": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "SOT23": "Package_TO_SOT_SMD:SOT-23", "SOD123": "Diode_SMD:D_SOD-123",
 "FUSE": "Fuse:Fuseholder_Blade_Mini_Keystone_3568", "BUCK": "Converter_DCDC:Converter_DCDC_TRACO_TEN40-110xxWIRH_THT", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "OPTO": "Package_SO:SOP-4_3.8x4.1mm_P2.54mm",
 "POGO_T": "meshsat:PogoTargets_2x4", "POGO_T6": "meshsat:PogoTargets_2x6", "TP": "TestPoint:TestPoint_Pad_D1.5mm", "TDSON8": "Package_TO_SOT_SMD:TDSON-8-1", "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "QFN38": "Package_DFN_QFN:WQFN-38-1EP_5x7mm_P0.5mm_EP3.15x5.15mm", "L1510": "Inductor_SMD:L_Coilcraft_XAL1510-103", "RS2512": "Resistor_SMD:R_2512_6332Metric", "CPOL63": "Capacitor_SMD:CP_Elec_6.3x7.7", "CPOL8": "Capacitor_SMD:CP_Elec_8x6.7", "XT60": "Connector_AMASS:AMASS_XT60-M_1x02_P7.20mm_Vertical", "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "PAD86": "meshsat:SolderPad_8x6",
}
kisch.configure(fp=FP)   # the engine needs the tables before the first part
P = kisch.P                           # one list, shared with the engine (not a copy)
def tp(ref, net): part(ref, "Connector", "TestPoint", net, "TP", {"1": net})
# ================================================================ E6 (7 Sep 2026, appendix 32.55 to 32.57, MESHSAT-830): the dock strip of the A22 generation. It carries the BB-2590/U cable entry
# and its 25 A blade to the raised block, the vehicle and shore entry (10 A blade, LM74700 ideal diode, LM5069 hot-swap with under and over-voltage limits, the input filter) to the
# raw 9 to 36 V bus that climbs the dock contacts into A22's LM5176 front end, the LT8705A panel tracker of E4 (bench-fitted part, 32.54) ORed into the same bus, eleven float clamps,
# and the kit's sensor controller (the S1 board of the plan folded in, 32.57): an RP2040 on USB through two dock contacts with the inside climate sensor, the IMU, the floor water
# electrodes, the two mixer fan drivers, the pack's SMBus, and headers for the Geiger module, the DCF77 receiver, the lightning sensor module and the outside sensor pod. One ground
# domain (the vehicle return joins the kit ground through the filter's second winding); the isolated TRACO converter of E4 is gone.
FP.update({"QFN56": "Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm", "USON8": "Package_SON:Winbond_USON-8-1EP_3x2mm_P0.5mm_EP0.2x1.6mm", "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
           "LGA8B": "Package_LGA:Bosch_LGA-8_3x3mm_P0.8mm_ClockwisePinNumbering", "LGA14B": "Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm", "TSOT6": "Package_TO_SOT_SMD:TSOT-23-6", "SOT235": "Package_TO_SOT_SMD:SOT-23-5",
           "L4020": "Inductor_SMD:L_Coilcraft_XAL4020-XXX", "L1010": "Inductor_SMD:L_Coilcraft_XAL1010-XXX", "CMC": "Inductor_SMD:L_CommonModeChoke_Bourns_SRF1260", "VSSOP10": "Package_SO:VSSOP-10_3x3mm_P0.5mm",
           "PPAK": "Package_SO:PowerPAK_SO-8_Single", "PH3": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", "PH4": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
           "PH5": "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical", "PH6": "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical", "C1210": "Capacitor_SMD:C_1210_3225Metric",
           "C0805": "Capacitor_SMD:C_0805_2012Metric", "JP2": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "SMB": "Diode_SMD:D_SMB"})
def nfet(ref, value, g, d, s, fp="PPAK", lcsc=""): part(ref, "Transistor_FET", "Q_NMOS_GDS", value, fp, {"1": g, "2": d, "3": s}, lcsc)
def ph(ref, n, value, nets): part(ref, "Connector_Generic", "Conn_01x%02d" % n, value, "PH%d" % n, nets)
# --- pack entry: the BTA-70762-2 cable of the BB-2590/U (both 14.4 V sections in parallel) on an XT60, the 25 A blade, the 12 AWG pads to the block; the pack's two SMBus sections on J_SMB
part("J_BATT", "Connector_Generic", "Conn_01x02", "BB-2590/U cable (BTA-70762-2) on XT60-M: pin 2 (the pad nearer the fuse F3) is +, pin 1 is the return; the pack's own protection is inside it (E6 run 11: a 3 mm CELL+ track could not pass the return pad to reach pin 1)", "XT60", {"1": "GND", "2": "CELL+"})
part("F3", "Device", "Fuse", "25 A mini blade (Keystone 3568 holder): pack to the block", "FUSE", {"1": "CELL+", "2": "CELL_F"})
part("P_CP", "Connector", "Conn_01x01_Pin", "solder pad, 12 AWG wire to the block board CELL+ targets", "PAD86", {"1": "CELL_F"})
part("P_CN", "Connector", "Conn_01x01_Pin", "solder pad, 12 AWG wire to the block board return targets", "PAD86", {"1": "GND"})
ph("J_SMB", 6, "pack SMBus (XH or pin header): section A SDA SCL on I2C0, section B SDA SCL on the sensor bus I2C1, GND GND", {"1": "SDA0", "2": "SCL0", "3": "SDA1", "4": "SCL1", "5": "GND", "6": "GND"})
c("C1", "10u 25V 1210", "CELL_F", "GND", "C1210"); part("D3", "Device", "D_TVS", "SMCJ18A (pack node clamp)", "TVS", {"1": "GND", "2": "CELL_F"})
# --- vehicle and shore entry 9 to 36 V: J_DCIN -> F1 10 A -> LM74700 ideal diode (reverse polarity) -> LM5069 hot-swap (UVLO 9 V, OVLO 40 V, current limit, power limit) -> the filter
#     (SRF1260 dual-winding choke on both lines, X capacitors, transient clamp) -> VIN_RAW to the block lands. Vehicle-side ground GND_V joins the kit ground GND through the choke's second winding.
part("J_DCIN", "Connector_Generic", "Conn_01x02", "vehicle and shore DC in 9-36 V, lead from the D38999 wall receptacle DC pair (JST-VH, 10 A): + -", "VH2", {"1": "DC_IN", "2": "GND_V"})
part("F1", "Device", "Fuse", "10 A mini blade (Keystone 3568 holder): vehicle input", "FUSE", {"1": "DC_IN", "2": "DC_F"})
def ideal_diode(uref, qref, cref, rref, anode, cathode, gnd):
    """LM74700-Q1 (ti/ti-lm74700-q1.pdf, SOT-23-6: 1 VCAP, 2 GND, 3 EN, 4 CATHODE, 5 GATE, 6 ANODE) driving an N-FET (source at the anode, drain at the cathode)"""
    part(uref, "Connector_Generic", "Conn_01x06", "LM74700-Q1 ideal-diode controller: 1 VCAP 2 GND 3 EN 4 CATHODE 5 GATE 6 ANODE", "SOT236", {"1": uref + "_VCAP", "2": gnd, "3": anode, "4": cathode, "5": qref + "_G", "6": anode}, "C2941042")
    part(qref, "Transistor_FET", "IRF7404", "BSC039N06NS 60 V 3.9 mOhm N-FET (PG-TDSON-8: 1-3 S, 4 G, 5-8 D)", "TDSON8", {"1": anode, "2": anode, "3": anode, "4": qref + "_G", "5": cathode, "6": cathode, "7": cathode, "8": cathode}, "C534330")
    c(cref, "100n 50V", uref + "_VCAP", anode, "C", "C14663"); r(rref, "100k", qref + "_G", anode, "R", "C25803")
ideal_diode("U3", "Q1", "C4", "R1", "DC_F", "DC_P", "GND_V")
part("D1", "Device", "D_TVS", "SMCJ33A (input surge, datasheet 50 V 100 ms)", "TVS", {"1": "GND_V", "2": "DC_P"}); c("C2", "100n 100V", "DC_P", "GND_V", "C0805")
# LM5069 (ti/ti-lm5069.pdf, VSSOP-10: 1 SENSE 2 VIN 3 UVLO 4 OVLO 5 GND 6 TIMER 7 PWR 8 PGD 9 OUT 10 GATE); the -2 variant restarts after a fault; sense resistor 10 mOhm, pass FET 60 V
ic("U6", 10, "LM5069MM-2 hot-swap controller: 9 V on, 40 V off, current and power limit", "VSSOP10", {"1": "HS_S", "2": "DC_P", "3": "HS_UVLO", "4": "HS_OVLO", "5": "GND_V", "6": "HS_TIMER", "7": "HS_PWR", "8": "DCIN_PGD", "9": "DC_HS", "10": "HS_GATE"}, "C111822")
r("R19", "10mOhm 1% 2512 (hot-swap sense)", "DC_P", "HS_S", "RS2512"); nfet("Q7", "CSD19532Q5B 100 V N-FET (4.6 mOhm at VGS 6 V, PowerPAK SO-8 / SON-8 5x6), hot-swap pass", "HS_GATE", "HS_S", "DC_HS", lcsc="C473333")
r("R20", "100k 1%", "DC_P", "HS_UVLO"); r("R21", "38.3k 1% (UVLO: 9 V)", "HS_UVLO", "GND_V"); r("R22", "100k 1%", "DC_P", "HS_OVLO"); r("R23", "6.65k 1% (OVLO: 40 V)", "HS_OVLO", "GND_V")
c("C5", "100n (TIMER)", "HS_TIMER", "GND_V"); r("R24", "20k (PWR: power limit)", "HS_PWR", "GND_V"); r("R25", "10k", "DCIN_PGD", "+3V3_E6")
part("Q8", "Transistor_FET", "2N7002", "2N7002: SHORE_INHIBIT high pulls UVLO low = input off (1 G, 2 S, 3 D)", "SOT23", {"1": "SHORE_INHIBIT", "2": "GND_V", "3": "HS_UVLO"}); r("R26", "100k", "SHORE_INHIBIT", "GND")
part("L2", "Connector_Generic", "Conn_01x04", "Bourns SRF1260-4R7Y dual-winding choke (7.2 A per winding at 4.7 uH): winding 1 pins 1-2 on the positive line, winding 2 pins 3-4 on the return (pin map per the Bourns drawing, verified 7 Sep 2026)", "CMC", {"1": "DC_HS", "2": "VIN_RAW", "3": "GND_V", "4": "GND"})
c("C6", "1u 100V 1210 (X, input side)", "DC_HS", "GND_V", "C1210"); c("C7", "1u 100V 1210 (X, bus side)", "VIN_RAW", "GND", "C1210"); c("C8", "10u 50V 1210", "VIN_RAW", "GND", "C1210")
part("D2", "Device", "D_TVS", "SMCJ33A (bus clamp)", "TVS", {"1": "GND", "2": "VIN_RAW"})
r("R27", "2.2k", "VIN_RAW", "LED_A", "R", "C4190"); part("LED1", "Device", "LED", "green: vehicle input present", "LED", {"2": "LED_A", "1": "GND"})
# --- panel tracker stage (power/lt8705a.pdf, E4's design kept: LT8705A buck-boost, input regulated at the panel's maximum-power voltage (FBIN 17.6 V), output 15.1 V ORed into the bus; bench-fitted, 32.54)
part("J_SOLAR", "Connector_Generic", "Conn_01x02", "bare 12 V class panel in, lead from the D38999 spare pair (JST-VH, 10 A): + - (36-cell panel, up to about 22 V open circuit, 100 W)", "VH2", {"1": "PV_IN", "2": "GND"})
part("F2", "Device", "Fuse", "10 A mini blade (Keystone 3568 holder): panel input", "FUSE", {"1": "PV_IN", "2": "PV_P"})
part("D4", "Device", "D_TVS", "SMCJ33A (panel surge)", "TVS", {"1": "GND", "2": "PV_P"})
for k in range(1, 3): part("C%d" % (10 + k), "Device", "C_Polarized", "100u 35V Panasonic EEHZK1V101XP hybrid polymer (7.7 mm)", "CPOL63", {"1": "PV_P", "2": "GND"}, "C454360")
c("C13", "10u 50V", "PV_P", "GND", "C10u50"); c("C14", "10u 50V", "PV_P", "GND", "C10u50"); c("C15", "4.7u 50V", "PV_P", "GND", "C10u50")
part("U5", "Connector_Generic", "Conn_02x20_Odd_Even", "LT8705A buck-boost controller, 38-lead QFN 5x7 (pin 39 = exposed pad GND, pin 40 unused); bench-fitted", "QFN38", {
 "1": "TRK_SHDN", "2": "TRK_CSN", "3": "TRK_CSP", "4": "TRK_LDO33", "5": "TRK_FBIN", "6": "TRK_FBOUT", "7": "TRK_IMONO", "8": "TRK_VC", "9": "TRK_SS", "10": "NC", "11": "GND", "12": "TRK_RT", "13": "GND",
 "14": "TRK_BG1", "15": "TRK_INTVCC", "16": "TRK_BG2", "17": "TRK_BOOST2", "18": "TRK_TG2", "19": "TRK_SW2", "20": "NC", "21": "TRK_SW1", "22": "TRK_TG1", "23": "TRK_BOOST1", "24": "NC",
 "25": "NC", "26": "NC", "27": "NC", "28": "NC", "29": "TRK_OUT", "30": "TRK_OUT", "31": "TRK_OUT", "32": "PV_P", "33": "PV_P", "34": "PV_P", "35": "TRK_INTVCC", "36": "TRK_INTVCC", "37": "GND", "38": "TRK_IMONI", "39": "GND", "40": "NC"}, "C674167")
part("Q3", "Transistor_FET", "IRF7404", "BSC028N06NS 60 V 2.8 mOhm N-FET, M1 buck top (TDSON-8: 1-3 S, 4 G, 5-8 D)", "TDSON8", {"1": "TRK_SW1", "2": "TRK_SW1", "3": "TRK_SW1", "4": "TRK_TG1", "5": "PV_P", "6": "PV_P", "7": "PV_P", "8": "PV_P"}, "C148250")
part("Q4", "Transistor_FET", "IRF7404", "BSC039N06NS 60 V N-FET, M2 buck bottom", "TDSON8", {"1": "GND", "2": "GND", "3": "GND", "4": "TRK_BG1", "5": "TRK_SW1", "6": "TRK_SW1", "7": "TRK_SW1", "8": "TRK_SW1"}, "C534330")
part("Q5", "Transistor_FET", "IRF7404", "BSC028N06NS 60 V N-FET, M3 boost bottom", "TDSON8", {"1": "GND", "2": "GND", "3": "GND", "4": "TRK_BG2", "5": "TRK_SW2", "6": "TRK_SW2", "7": "TRK_SW2", "8": "TRK_SW2"}, "C148250")
part("Q6", "Transistor_FET", "IRF7404", "BSC039N06NS 60 V N-FET, M4 boost top", "TDSON8", {"1": "TRK_SW2", "2": "TRK_SW2", "3": "TRK_SW2", "4": "TRK_TG2", "5": "TRK_OUT", "6": "TRK_OUT", "7": "TRK_OUT", "8": "TRK_OUT"}, "C534330")
part("L1", "Device", "L", "10uH Coilcraft XAL1510-103MED (Isat 26 A, 10.0 mm tall)", "L1510", {"1": "TRK_SW1", "2": "TRK_LSENSE"}, "C3911782")
part("R5", "Device", "R", "5 mOhm 1% 3 W 2512 RSENSE (RALEC LR2512-23R005F4)", "RS2512", {"1": "TRK_LSENSE", "2": "TRK_SW2"}, "C154688")
r("R6", "100R", "TRK_LSENSE", "TRK_CSP"); r("R7", "100R", "TRK_SW2", "TRK_CSN"); c("C16", "1n", "TRK_CSP", "TRK_CSN")
c("C17", "470n 25V", "TRK_BOOST1", "TRK_SW1"); c("C18", "470n 25V", "TRK_BOOST2", "TRK_SW2")
part("D5", "Device", "D_Schottky", "BAT54 boost diode INTVCC -> BOOST1", "SOD123", {"1": "TRK_BOOST1", "2": "TRK_INTVCC"}); part("D6", "Device", "D_Schottky", "BAT54 boost diode INTVCC -> BOOST2", "SOD123", {"1": "TRK_BOOST2", "2": "TRK_INTVCC"})
c("C19", "4.7u 25V", "TRK_INTVCC", "GND", "C10u50"); c("C20", "1u", "TRK_LDO33", "GND")
r("R8", "102k 1% (RFBIN1: panel point 17.6 V)", "PV_P", "TRK_FBIN"); r("R9", "7.50k 1% (RFBIN2)", "TRK_FBIN", "GND")
r("R10", "115k 1% (RFBOUT1: 15.1 V)", "TRK_OUT", "TRK_FBOUT"); r("R11", "10.0k 1% (RFBOUT2)", "TRK_FBOUT", "GND")
r("R12", "215k 1% (RT: 202 kHz)", "TRK_RT", "GND"); r("R13", "10k", "TRK_VC", "TRK_VCC1"); c("C21", "4.7n", "TRK_VCC1", "GND"); c("C22", "100p", "TRK_VC", "GND"); c("C23", "100n", "TRK_SS", "GND")
r("R14", "100k 1%", "PV_P", "TRK_SHDN"); r("R15", "15.0k 1% (SHDN: enable above about 9.5 V)", "TRK_SHDN", "GND")
r("R16", "10k", "TRK_IMONI", "GND"); r("R17", "10k", "TRK_IMONO", "GND")
for k in range(1, 3): part("C%d" % (23 + k), "Device", "C_Polarized", "39u 35V Panasonic 35SVPF39M polymer (6.9 mm)", "CPOL8", {"1": "TRK_OUT", "2": "GND"}, "C189474")
c("C26", "10u 25V", "TRK_OUT", "GND", "C10u50"); c("C27", "10u 25V", "TRK_OUT", "GND", "C10u50")
ideal_diode("U4", "Q2", "C28", "R18", "TRK_OUT", "VIN_RAW", "GND")   # tracker output ORed into the raw bus that A22's front end regulates
# --- the block lands (mirror of A22's J_DOCK, 32.57): 1-4 VIN_RAW, 5-7 GND, 8 SHORE_INHIBIT (from A22, into the hot-swap UVLO), 9-10 the controller's USB, 11 GND, 12 spare
part("J_BLK", "Connector_Generic", "Conn_01x12", "solder lands for the 12 signal wires to the block board underside (mirror of A22 J_DOCK): 1-4 VIN_RAW, 5-7 GND, 8 SHORE_INHIBIT, 9 USB D+, 10 USB D-, 11 GND, 12 spare", "POGO_T6",
     {"1": "VIN_RAW", "2": "VIN_RAW", "3": "VIN_RAW", "4": "VIN_RAW", "5": "GND", "6": "GND", "7": "GND", "8": "SHORE_INHIBIT", "9": "USB_E6_P", "10": "USB_E6_N", "11": "GND", "12": "BLK_SPARE"})
# --- controller power: AP63205 5 V 2 A buck from the pack node (diodes/diodes-ap63205.pdf, TSOT-26: 1 FB 2 EN 3 VIN 4 GND 5 SW 6 BST; fixed 5 V, FB is the output sense), TLV75533 3.3 V LDO (SOT-23-5: 1 IN 2 GND 3 EN 4 NC 5 OUT)
ic("U12", 6, "AP63205WU-7 5 V 2 A buck for the controller, the Geiger module and the fans' logic", "TSOT6", {"1": "+5V_E6", "2": "CELL_F", "3": "CELL_F", "4": "GND", "5": "E6_SW", "6": "E6_BST"}, "C2071056")
part("L3", "Device", "L", "4.7uH XAL4030-472ME", "L4020", {"1": "E6_SW", "2": "+5V_E6"}); c("C30", "100n", "E6_BST", "E6_SW"); c("C31", "10u 25V 1210", "CELL_F", "GND", "C1210"); c("C32", "22u 10V X7R 1210", "+5V_E6", "GND", "C1210"); c("C33", "22u 10V X7R 1210", "+5V_E6", "GND", "C1210")
ic("U13", 5, "TLV75533PDBVR 3.3 V LDO", "SOT235", {"1": "+5V_E6", "2": "GND", "3": "+5V_E6", "4": "NC", "5": "+3V3_E6"}, "C404027"); c("C34", "1u", "+5V_E6", "GND"); c("C35", "1u", "+3V3_E6", "GND")
# --- RP2040 (rp2040/rpi-rp2040-datasheet.pdf, QFN-56; the minimal design of the hardware design guide: 12 MHz crystal with 15 pF loads and a 1k series on XOUT, W25Q16 QSPI flash, 27 Ohm USB series,
#     RUN pull-up, BOOTSEL by a solder jumper on QSPI_SS). GPIO: 2 SDA0 3 SCL0 (pack section A), 4 SDA1 5 SCL1 (sensors, pack section B, pod, lightning module), 6 DCF77 pulse, 7 Geiger pulse,
#     8 and 9 fan PWM, 10 and 11 fan tachometers, 12 input power good, 13 IMU interrupt, 14 lightning interrupt, 15 SHORE_INHIBIT read-back, 21 status LED, 26 water electrodes (ADC0),
#     27 bus voltage (ADC1), 28 pack voltage (ADC2)
ic("U10", 57, "RP2040 sensor controller (USB to B16 through the dock)", "QFN56", {
 "1": "+3V3_E6", "2": "NC", "3": "NC", "4": "SDA0", "5": "SCL0", "6": "SDA1", "7": "SCL1", "8": "DCF_PULSE", "9": "GEIGER_IN", "10": "+3V3_E6", "11": "FAN1_PWM", "12": "FAN2_PWM", "13": "FAN1_TACH", "14": "FAN2_TACH",
 "15": "DCIN_PGD", "16": "IMU_INT1", "17": "LTG_IRQ", "18": "SHORE_INHIBIT", "19": "GND", "20": "XIN", "21": "XOUT_R", "22": "+3V3_E6", "23": "E6_DVDD", "24": "SWCLK", "25": "SWDIO", "26": "E6_RUN",
 "27": "NC", "28": "NC", "29": "NC", "30": "NC", "31": "NC", "32": "NC", "33": "+3V3_E6", "34": "NC", "35": "NC", "36": "NC", "37": "LED_STAT", "38": "WATER_SENSE", "39": "VIN_MON", "40": "CELL_MON", "41": "NC",
 "42": "+3V3_E6", "43": "+3V3_E6", "44": "+3V3_E6", "45": "E6_DVDD", "46": "USB_DM_R", "47": "USB_DP_R", "48": "+3V3_E6", "49": "+3V3_E6", "50": "E6_DVDD", "51": "QSPI_D3", "52": "QSPI_SCLK", "53": "QSPI_D0",
 "54": "QSPI_D2", "55": "QSPI_D1", "56": "QSPI_SS", "57": "GND"}, "C2040")
ic("U11", 9, "W25Q16JVUXIQ 16 Mbit QSPI flash (USON-8: 1 CS 2 DO/IO1 3 WP/IO2 4 GND 5 DI/IO0 6 CLK 7 HOLD/IO3 8 VCC, pad)", "USON8", {"1": "QSPI_SS", "2": "QSPI_D1", "3": "QSPI_D2", "4": "GND", "5": "QSPI_D0", "6": "QSPI_SCLK", "7": "QSPI_D3", "8": "+3V3_E6", "9": "GND"}, "C2843335")
part("Y1", "Device", "Crystal_GND24", "12 MHz ABM8-272-T3 (3225): 1 XIN, 3 XOUT, 2 and 4 GND", "XTAL", {"1": "XIN", "2": "GND", "3": "XOUT", "4": "GND"}, "C20625731")
c("C36", "15p", "XIN", "GND"); c("C37", "15p", "XOUT", "GND"); r("R28", "1k", "XOUT_R", "XOUT")
r("R29", "27R", "USB_DP_R", "USB_E6_P"); r("R30", "27R", "USB_DM_R", "USB_E6_N"); r("R31", "10k", "E6_RUN", "+3V3_E6"); r("R32", "1k (BOOTSEL)", "QSPI_SS", "BOOT_J"); part("JP1", "Jumper", "SolderJumper_2_Open", "BOOTSEL: short while powering to enter the USB bootloader", "JP2", {"1": "BOOT_J", "2": "GND"})
for k in range(38, 45): c("C%d" % k, "100n", "+3V3_E6", "GND")
c("C45", "1u", "E6_DVDD", "GND"); c("C46", "1u", "E6_DVDD", "GND"); c("C47", "1u", "+3V3_E6", "GND")
tp("TP10", "SWCLK"); tp("TP11", "SWDIO"); tp("TP12", "E6_RUN")
r("R33", "1k", "LED_STAT", "LED_STAT_A"); part("LED2", "Device", "LED", "status (GPIO25)", "LED", {"2": "LED_STAT_A", "1": "GND"})
r("R34", "4.7k", "SDA0", "+3V3_E6"); r("R35", "4.7k", "SCL0", "+3V3_E6"); r("R36", "4.7k", "SDA1", "+3V3_E6"); r("R37", "4.7k", "SCL1", "+3V3_E6")
# --- sensors on the strip: BME688 inside climate and gas (bosch/bosch-bme688.pdf, LGA-8: 1 GND 2 CSB 3 SDI 4 SCK 5 SDO 6 VDDIO 7 GND 8 VDD; I2C 0x76 with SDO low), BMI270 IMU for shock, tilt and
#     motion (bosch/bosch-bmi270.pdf, LGA-14; I2C 0x68 with SDO low; CSB and the unused OIS and aux pins tied per the sheet's I2C column); the magnetometer sits in the outside pod (32.57)
ic("U14", 8, "BME688 inside climate: temperature, humidity, pressure, gas index (I2C 0x76)", "LGA8B", {"1": "GND", "2": "+3V3_E6", "3": "SDA1", "4": "SCL1", "5": "GND", "6": "+3V3_E6", "7": "GND", "8": "+3V3_E6"}, "C3664478"); c("C48", "100n", "+3V3_E6", "GND")
ic("U15", 14, "BMI270 six-axis IMU (I2C 0x68): shock and tilt log, motion wake", "LGA14B", {"1": "GND", "2": "GND", "3": "GND", "4": "IMU_INT1", "5": "+3V3_E6", "6": "GND", "7": "GND", "8": "+3V3_E6", "9": "NC", "10": "NC", "11": "NC", "12": "IMU_CSB", "13": "SCL1", "14": "SDA1"}, "C2836813"); r("R51", "0R (CSB high: I2C mode; its own net keeps the pin joiner off the diagonal)", "+3V3_E6", "IMU_CSB"); c("C49", "100n", "+3V3_E6", "GND"); c("C50", "100n", "+3V3_E6", "GND")
# --- water electrodes (two exposed pads on the strip's underside edge, 1 mm above the floor on the VHB pads), fans, headers
part("PAD_W1", "Connector", "Conn_01x01_Pin", "water electrode A (bare copper, +3.3 V through 1 M)", "PAD86", {"1": "WATER_A"}); r("R38", "1M", "+3V3_E6", "WATER_A")
part("PAD_W2", "Connector", "Conn_01x01_Pin", "water electrode B (bare copper, to ADC0)", "PAD86", {"1": "WATER_SENSE"}); r("R39", "1M", "WATER_SENSE", "GND"); c("C51", "100n", "WATER_SENSE", "GND")
r("R40", "100k 1%", "VIN_RAW", "VIN_MON"); r("R41", "10k 1% (ADC1: 0.091 x bus)", "VIN_MON", "GND"); r("R42", "100k 1%", "CELL_F", "CELL_MON"); r("R43", "22k 1% (ADC2: 0.18 x pack)", "CELL_MON", "GND")
for n in ("1", "2"):
    ph("J_FAN%s" % n, 3, "mixer fan %s under the plate (12 V class fan on the pack node, low-side PWM, tachometer)" % n, {"1": "CELL_F", "2": "FAN%s_SW" % n, "3": "FAN%s_TACH" % n})
    part("Q%s" % ("9" if n == "1" else "10"), "Transistor_FET", "2N7002", "2N7002 fan %s low-side switch (1 G, 2 S, 3 D)" % n, "SOT23", {"1": "FAN%s_G" % n, "2": "GND", "3": "FAN%s_SW" % n})
    r("R%s" % ("44" if n == "1" else "45"), "100R", "FAN%s_PWM" % n, "FAN%s_G" % n); r("R%s" % ("46" if n == "1" else "47"), "10k", "FAN%s_TACH" % n, "+3V3_E6")
    part("D%s" % ("7" if n == "1" else "8"), "Device", "D_Schottky", "SS14 flyback across fan %s" % n, "SMB", {"1": "CELL_F", "2": "FAN%s_SW" % n})
ph("J_GEIGER", 3, "Geiger counter module (RadiationD-v1.1 class): 5 V, GND, pulse", {"1": "+5V_E6", "2": "GND", "3": "GEIGER_PULSE"})
ph("J_DCF", 3, "DCF77 receiver module: 3.3 V, GND, pulse", {"1": "+3V3_E6", "2": "GND", "3": "DCF_PULSE"})
ph("J_LTG", 5, "AS3935 lightning sensor module (CJMCU-3935 class): 3.3 V, GND, SDA, SCL, IRQ", {"1": "+3V3_E6", "2": "GND", "3": "SDA1", "4": "SCL1", "5": "LTG_IRQ"})
ph("J_POD", 4, "outside sensor pod on the connector plate (M8 sealed lead): 3.3 V, GND, SDA, SCL", {"1": "+3V3_E6", "2": "GND", "3": "SDA1", "4": "SCL1"})
# 9 Sep 2026 (E7, appendix 32.83): U10 pin 9 was on GEIGER_PULSE, so R48 sat in series with NOTHING: the module's pulse reached the
# RP2040 pin directly and GEIGER_IN went only to TP13. Pin 9 is GEIGER_IN now and the resistor is in the path it was drawn for.
# (This comment is on its OWN line: appended to the code line it swallowed tp("TP13") and R49 and R50, the trap CLAUDE.md section 8 names.)
r("R48", "22R (pulse input series)", "GEIGER_PULSE", "GEIGER_IN"); tp("TP13", "GEIGER_IN"); r("R49", "10k", "DCF_PULSE", "+3V3_E6"); r("R50", "10k", "LTG_IRQ", "+3V3_E6")
tp("TP1", "DC_IN"); tp("TP2", "DC_P"); tp("TP3", "VIN_RAW"); tp("TP4", "GND"); tp("TP5", "PV_P"); tp("TP6", "TRK_OUT"); tp("TP7", "BLK_SPARE"); tp("TP8", "CELL_F"); tp("TP9", "+5V_E6")
for i, net in enumerate(("DC_IN", "DC_F", "DC_P", "DC_HS", "GND_V", "GND", "VIN_RAW", "PV_IN", "PV_P", "TRK_OUT", "TRK_INTVCC", "TRK_LDO33", "CELL+", "CELL_F", "+5V_E6", "+3V3_E6", "E6_DVDD"), 1): part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})

# ----------------------------------------------------------------- emit
POWER = {"GND": ("power", "GND"), "+5V": ("power", "+5V"), "+3V3": ("power", "+3V3")}
libsyms = kisch.libsyms; out = kisch.out; pf_n = kisch.pf_n   # the engine's objects, by reference
ROOT = str(uuid.uuid5(kisch.UUID_NS, "root:" + PROJECT))   # deterministic: a board regenerates byte for byte (10 Sep 2026)
STUB = 5.08
kisch.configure(power=POWER, stub=STUB, root=ROOT, project=PROJECT, seed=PROJECT)
# power flag symbols connect at their pin; place them wired to a label of the net

# layout: columns, top-down cursor; group order = list order with section titles
SECTIONS = [("PACK ENTRY: BB-2590/U CABLE ON XT60, 25 A BLADE, PADS TO THE BLOCK, SMBUS HEADER", ["J_BATT", "F3", "P_CP", "P_CN", "J_SMB", "C1", "D3"]),
            ("VEHICLE AND SHORE ENTRY 9-36 V: F1, LM74700 IDEAL DIODE, LM5069 HOT-SWAP, SRF1260 FILTER, CLAMPS", ["J_DCIN", "F1", "U3", "Q1", "C4", "R1", "D1", "C2", "U6", "R19", "Q7", "R20", "R21", "R22", "R23", "C5", "R24", "R25", "Q8", "R26", "L2", "C6", "C7", "C8", "D2", "R27", "LED1"]),
            ("PANEL TRACKER: J_SOLAR, F2, LT8705A BUCK-BOOST (FBIN 17.6 V, FBOUT 15.1 V, 202 kHz), ORed INTO THE RAW BUS", ["J_SOLAR", "F2", "D4", "C11", "C12", "C13", "C14", "C15", "U5", "Q3", "Q4", "Q5", "Q6", "L1", "R5", "R6", "R7", "C16", "C17", "C18", "D5", "D6", "C19", "C20", "R8", "R9", "R10", "R11", "R12", "R13", "C21", "C22", "C23", "R14", "R15", "R16", "R17", "C24", "C25", "C26", "C27", "U4", "Q2", "C28", "R18"]),
            ("BLOCK LANDS (MIRROR OF A22 J_DOCK)", ["J_BLK"]),
            ("SENSOR CONTROLLER: 5 V BUCK, 3.3 V LDO, RP2040, QSPI FLASH, CRYSTAL, USB, BOOTSEL, PULL-UPS", ["U12", "L3", "C30", "C31", "C32", "C33", "U13", "C34", "C35", "U10", "U11", "Y1", "C36", "C37", "R28", "R29", "R30", "R31", "R32", "JP1"] + ["C%d" % k for k in range(38, 48)] + ["TP10", "TP11", "TP12", "R33", "LED2", "R34", "R35", "R36", "R37"]),
            ("SENSORS, WATER ELECTRODES, MONITORS, FANS, HEADERS", ["U14", "C48", "U15", "R51", "C49", "C50", "PAD_W1", "R38", "PAD_W2", "R39", "C51", "R40", "R41", "R42", "R43", "J_FAN1", "Q9", "R44", "R46", "D7", "J_FAN2", "Q10", "R45", "R47", "D8", "J_GEIGER", "J_DCF", "J_LTG", "J_POD", "R48", "TP13", "R49", "R50"]),
            ("TEST POINTS, FLAGS", ["TP%d" % k for k in range(1, 10)] + ["#FLG%02d" % k for k in range(1, 18)])]
_listed = {r for _, refs in SECTIONS for r in refs}
_rest = [p["ref"] for p in P if p["ref"] not in _listed]
if _rest: SECTIONS.append(("OTHER PARTS (not in a section list)", _rest))
byref = {p["ref"]: p for p in P}
placed = set()
COLW = 88.0; x = 20.0; y = 30.0; PAGE_H = 560.0   # A1 landscape is 841 x 594; A0 is chosen below if the columns overflow
for title, refs in SECTIONS:
    # estimate section height
    hs = []
    for ref in refs:
        p = byref[ref]; x0, x1, y0, y1 = extents(ensure(p["lib"], p["sym"])); hs.append((y1 - y0) + 2 * STUB + 12.0)
    if y + sum(hs) + 10 > PAGE_H and y > 30.0:
        x += COLW; y = 30.0
    text(title, round((x - 15.0) / 1.27) * 1.27, round((y - 4.0) / 1.27) * 1.27)
    y += 4.0
    for ref, h in zip(refs, hs):
        p = byref[ref]; x0, x1, y0, y1 = extents(ensure(p["lib"], p["sym"]))
        if y + h > PAGE_H:
            x += COLW; y = 34.0
        cy = y + (y1 + STUB) + 4.0               # symbol origin so its top pin+stub sits at y
        gx = round((x + 20.0) / 1.27) * 1.27; gy = round(cy / 1.27) * 1.27   # 1.27 mm grid, so every pin end and label is on grid
        if p["sym"] == "PWR_FLAG": emit_pwr_flag(p, gx, gy)
        else: emit_part(p, gx, gy)
        placed.add(ref); y += h
    y += 8.0
missing = [p["ref"] for p in P if p["ref"] not in placed]
if missing: raise SystemExit("unplaced parts: %s" % missing)

max_x = x + COLW
PAPER = "A1" if max_x <= 820 else "A0"
print("layout width %.0f mm -> paper %s" % (max_x, PAPER))
hdr = '(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "%s")\n\t(paper "%s")\n' % (ROOT, PAPER)
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-E1 DOCK") (date "2026-09-07") (rev "A (E6)") (company "MeshSat") (comment 1 "Phase E6 schematic (MESHSAT-830, appendix 32.55 to 32.57), generated by tools/gen_sch_e.py. Netlist style: every pin carries a stub and a net label.") (comment 2 "E6: BB-2590/U cable entry and 25 A blade to the raised block; vehicle input 9-36 V through LM74700, LM5069 hot-swap and the SRF1260 filter to the raw bus up the dock contacts; LT8705A panel tracker ORed into the bus; RP2040 sensor controller on USB (BME688, BMI270, water electrodes, fans, pack SMBus, Geiger, DCF77, lightning and pod headers); eleven float clamps."))\n'
hdr += '\t(lib_symbols\n' + "".join("\t\t" + ser(v, 2).replace("\n", "\n\t\t") + "\n" for v in libsyms.values()) + '\t)\n'
body = "".join("\t" + s.replace("\n", "\n\t").rstrip("\t") for s in out)
tail = '\t(sheet_instances (path "/" (page "1")))\n)\n'
open(OUT, "w").write(hdr + body + tail)
print("wrote", OUT, "parts:", len(P), "lib symbols:", len(libsyms))
nets = {}
for p in P:
    for num, net in p["nets"].items():
        if net != "NC": nets.setdefault(net, []).append("%s.%s" % (p["ref"], num))
single = [n for n, v in nets.items() if len(v) == 1]
print("nets:", len(nets), "single-pin nets (should be empty or intentional):", single)
# --- decoupling as data (8 Sep 2026, MESHSAT-862 Stage C): the pin each capacitor serves, so the loop gate measures a distance instead of
# counting parts. The tracker's compensation and soft-start networks (C16 to C23), the boost and bootstrap capacitors (C17, C18, C30), the
# hot-swap timer (C5), the crystal loads and the sense filters are not decoupling and are not listed. `intent.write` refuses an entry whose
# capacitor is not on that pin's net, so a wrong line here stops the generator.
for _i, _pin in enumerate((1, 10, 22, 33, 42, 49)): _intent.bypass("C%d" % (38 + _i), "U10", _pin, "+3V3_E6")   # the RP2040's six IOVDD pins
_intent.bypass("C44", "U11", "8", "+3V3_E6")     # the QSPI flash's VCC
_intent.bypass("C45", "U10", "23", "E6_DVDD"); _intent.bypass("C46", "U10", "50", "E6_DVDD")
_intent.bypass("C47", "U10", "44", "+3V3_E6")    # VREG_VIN
_intent.bypass("C31", "U12", "2", "CELL_F")      # the 5 V buck's input capacitor, the loop that matters on a switcher
_intent.bypass("C34", "U13", "1", "+5V_E6"); _intent.bypass("C35", "U13", "5", "+3V3_E6")   # the LDO's input and output
_intent.bypass("C48", "U14", "8", "+3V3_E6")     # BME688 VDD
_intent.bypass("C49", "U15", "8", "+3V3_E6"); _intent.bypass("C50", "U15", "5", "+3V3_E6")  # BMI270 VDD and VDDIO
# The dock strip's only differential pair is the sensor controller's own USB port, and the RP2040 is USB 1.1 FULL SPEED. The shared USB
# class targets 90 ohm, which belongs to USB 2.0 high speed; requiring it here is a wrong requirement, not a strict one, so this board
# declares the class with no impedance target and `impedance_check.py` skips it (9 September 2026, the same as C9).
_intent.pair_class("USB")

_intent.write(OUT, PROJECT, P)   # 8 Sep 2026 (MESHSAT-862): design intent as data, out/<project>-intent.json
