#!/usr/bin/env python3
"""PCB-A POWER + I/O, phase A22 (MESHSAT-830, 7 Sep 2026): generate the KiCad 9 schematic (netlist-style: every pin gets a
stub and a net label; power pins get power symbols). Runs on the laptop (needs the KiCad libs).
Usage: gen_sch_b.py <out.kicad_sch> <project-name>
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-a-power"
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from idc_pads import idc   # the IDC land is a per-board measurement (IDC_PADS), not a default: see idc_pads.py
# 10 September 2026 (MESHSAT-862, red team C2): the schematic engine lives in kisch.py, one copy for the six boards.
# What stays here is this board: its part tables, its nets, its sheet layout. `ic()` is strict for every board again.
import kisch
from kisch import (U, c, emit_part, emit_pwr_flag, ensure, esd, extents, find_sym, flatten, flatten_raw, ic, label, lib_tree, noconn, parse, part, pins_of, place_symbol, q, r, rename_units, ser, text, tps22810, uq, usb_c_recept, wire)
import intent as _intent
# Rails of A22 (appendix 32.55; the record's currents, not measurements): the node from the pack, the 20 V charge bus, the slot rails, the device rail, the PA and HF rails, PoE
_intent.rail("VBAT", 14.4, 10.0, 18.0, "F1", loads={"U4": 2.0, "U5": 2.0, "U6": 2.0, "U7": 2.0, "Q11": 1.5, "U15": 0.3, "U12": 0.2}, note="the 4S node after the 25 A blade F1; 10 A continuous, 18 A peak by the pack's rating (32.55)")
_intent.rail("CELL+", 14.4, 10.0, 18.0, "J_CP1", loads={"F1": 10.0}, note="the pack side of the RSR shunt. The pack current leaves this node through F1, the 25 A blade to VBAT; R17 is the 5 mOhm charge-sense shunt, R1 the 10 R pre-charge trickle, TP14 a test point and U3 pin 19 the BQ25731's CELL+ SENSE input, which draws microamps. Undeclared, dc_drop split the 10 A over every non-passive part on the net and pushed amps through U3 pin 19's 0.20 mm escape on a 0.4 mm pitch, reading 2.21 percent at a 0.5 mm cell and 2.75 at 0.25 against a 2 percent budget: the same correction VIN_RAW carries above, and for the same reason (12 September 2026, A24)")
_intent.rail("VIN_RAW", 12.0, 8.0, 10.0, "J_DOCK", loads={"Q2": 7.0, "C11": 0.5, "C12": 0.5}, note="shore and vehicle input from E6 over the dock, 10 A fuse; the current enters the front end at Q2's drain and the input caps (the LM5176 U2 draws only its bias: a load named U2 put 8 A into two QFN pins and read 3.3 percent, 32.69)")
_intent.rail("VBUS20", 20.0, 6.0, 8.0, "U2", note="the charge bus, BQ25731 up to 8 A")
for _n, _sh in (("1", "R31"), ("2", "R35"), ("3", "R39")): _intent.rail("+5V_S%s" % _n, 5.1, 2.5, 5.0, _sh, loads={"J_5V_S%s" % _n: 5.0}, note="one CM5 slot with its cooler fan; 5 A peak at the module; the rail net starts at the INA226 shunt")
_intent.rail("+5V_DEV", 5.0, 3.8, 6.0, "R43", loads={"J_5V_DEV": 3.2}, note="the USB devices, the LimeSDR bay and the RockBLOCK behind their switches; the net starts at the shunt. 9 September 2026 (ARCH-PCB-B-IOHA): +0.8 A because B16's three hub banks had to leave the slot rails, or a bank would die with the module it fails away from. The AP64500 is a 5 A part, so the headroom is there; what this declaration buys is that dc_drop judges the copper at the current it now carries.")
_intent.rail("+3V3", 3.3, 0.3, 0.6, "L7", budget=0.03, note="this board's logic (two PCA9555, five INA226, the LTC2954, the controllers' VCC pins: tens of mA each; the 1 A of the first intent was a placeholder, 32.69); the net starts at the TPS62933 inductor L7")
_intent.rail("+13V8_PA", 13.8, 5.0, 6.0, "R55", loads={"J_PA": 6.0}, note="the RA30H1317M1 on the face plate")
_intent.rail("+12V_HF", 12.0, 1.0, 2.0, "U15", budget=0.03, note="the QMX")
_intent.rail("+54V_POE", 54.0, 0.3, 0.6, "U16", note="the TPS23861 PSE on B16")
SYMDIR = "/usr/share/kicad/symbols/"

# ----------------------------------------------------------------- s-expression helpers
LIBCACHE = {}

# ----------------------------------------------------------------- the design
FP = {
 "R": "Resistor_SMD:R_0603_1608Metric", "RS": "Resistor_SMD:R_1206_3216Metric", "C": "Capacitor_SMD:C_0603_1608Metric",
 "C10u": "Capacitor_SMD:C_0805_2012Metric", "C100u": "Capacitor_SMD:C_1206_3216Metric", "LED": "LED_SMD:LED_0603_1608Metric",
 "TVS": "Diode_SMD:D_SMB", "TVSC": "Diode_SMD:D_SMC",   # SMBJ is DO-214AA (SMB), SMCJ is DO-214AB (SMC): never one key for both
 "F1812": "Fuse:Fuse_1812_4532Metric", "F2920": "Fuse:Fuse_2920_7451Metric",
 "HUB": "Package_SO:SSOP-28_5.3x10.2mm_P0.65mm", "EXP": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm",
 "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "SOT235": "Package_TO_SOT_SMD:SOT-23-5", "SOT238": "Package_TO_SOT_SMD:SOT-23-8", "SOT23": "Package_TO_SOT_SMD:SOT-23",
 "WSON6": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm", "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
 "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "XH4": "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
 "IDC18": idc("2x09"), "IDC40": idc("2x20"), "IDC14": idc("2x07"), "IDC16": idc("2x08"),
 "PICO10": "Connector_Molex:Molex_PicoBlade_53047-1010_1x10_P1.25mm_Vertical",
 "USBA": "Connector_USB:USB_A_Stewart_SS-52100-001_Horizontal", "USBC": "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", "USBCP": "Connector_USB:USB_C_Plug_Molex_105444", "PH4": "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical",
 "JP2": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "JP3": "Jumper:SolderJumper-3_P1.3mm_Open_RoundedPad1.0x1.5mm",
 "TP": "TestPoint:TestPoint_Pad_D1.5mm", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "XH10": "Connector_JST:JST_XH_B10B-XH-A_1x10_P2.50mm_Vertical",
 "CELL": "Battery:BatteryHolder_Keystone_1042_1x18650", "XT60": "Connector_AMASS:AMASS_XT60-M_1x02_P7.20mm_Vertical", "POGO": "meshsat:PogoPins_2x4", "FUSE": "Fuse:Fuseholder_Blade_Mini_Keystone_3568", "CHG": "Package_DFN_QFN:Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm", "PROT": "Package_SON:WSON-6_1.5x1.5mm_P0.5mm",
 "BOOST": "Package_DFN_QFN:Texas_RWU0007A_VQFN-7_2x2mm_P0.5mm", "GAUGE": "Package_SON:Texas_S-PDSO-N12", "SOT223": "Package_TO_SOT_SMD:SOT-223-3_TabPin2", "L4020": "Inductor_SMD:L_Coilcraft_XAL4020-XXX", "RS10m": "Resistor_SMD:R_2512_6332Metric",
 "QFN11": "Package_DFN_QFN:Texas_VQFN-RNR0011A-11", "L6030": "Inductor_SMD:L_Coilcraft_XAL6030-XXX", "C1210": "Capacitor_SMD:C_1210_3225Metric",
 "RQQ11": "meshsat:Texas_RQQ0011A_VQFN-HR-11_2.5x3mm", "RQM29": "meshsat:Texas_RQM0029A_QFN-29_4x4mm", "TSSOP14": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "DSG8": "Package_SON:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm",
 "TSOT8": "Package_TO_SOT_SMD:TSOT-23-8", "QFN64": "Package_DFN_QFN:QFN-64-1EP_9x9mm_P0.5mm_EP4.7x4.7mm", "L1010": "Inductor_SMD:L_Coilcraft_XAL1010-XXX", "L4030": "Inductor_SMD:L_Coilcraft_XAL4030-XXX",
 "POGO12": "meshsat:PogoPins_2x6", "MMPIN": "meshsat:Mill-Max_0858_power_pin", "SMAV": "Connector_Coaxial:SMA_Amphenol_132134-11_Vertical", "SMPMAX": "meshsat:Radiall_SMPMAX_R222M00720",
}
kisch.configure(fp=FP)   # the engine needs the tables before the first part
P = kisch.P                           # one list, shared with the engine (not a copy)    (ref, lib, symbol, value, footprint, nets{pin: net}, lcsc)
def usb_c_plug(ref, dp, dm, vbus, cc):
    # captive USB-C pigtail (4-wire cable with the Rp resistor in the plug) on a JST-PH 4-pin header: VBUS, D-, D+, GND
    part(ref, "Connector_Generic", "Conn_01x04", "USB-C pigtail header (JST-PH 2.0): VBUS D- D+ GND", "PH4", {"1": vbus, "2": dm, "3": dp, "4": "GND"})
def tps2065(ref, en, out, flt): part(ref, "Power_Management", "TPS2065CDBV", "TPS2065CDBV", "SOT235", {"5": "+5V_M1", "4": en, "1": out, "3": flt, "2": "GND"})   # A19: the channels hang on rail M1
def ina219(ref, inp, inn, a0, a1): part(ref, "Sensor_Energy", "INA219AxDCN", "INA219AIDCN", "SOT238", {"1": inp, "2": inn, "3": "GND", "4": "+3V3", "5": "SCL", "6": "SDA", "7": a0, "8": a1}, "C138024")

# ================================================================ A22 (7 Sep 2026, appendix 32.52, 32.55, 32.56): the 14.4 V node of the BB-2590/U, the wide-range front end,
# the BQ25731 charger, per-slot 5 V rails for three CM5, the PA and HF rails, the 54 V PoE rail, the USB-C PD outlet, the monitor and heater switches, hardware EMCON gates,
# eleven blind-mate RF sites, the D8 mezzanine as a USB device set. Every pin number below is read from the sheet filed under v2/vendor/ (ti/, power/) and the LCSC codes from 32.54.
# Nets: CELL+ is the pack node (four 9 A dock pins), VBAT the fused node every converter runs from, VIN_RAW the 9 to 36 V vehicle and shore input up the dock signal contacts,
# VBUS20 the 20 V charge bus, +5V_S1..3 the slot rails, +5V_DEV the USB device rail, +3V3 this board's logic, +13V8_PA, +12V_HF, +54V_POE, VMON, VHEAT, +5V_D8.
FP.update({
 "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "IDC26": idc("2x13"), "IDC16": idc("2x08"), "IDC10": idc("2x05"),
 "HTSSOP28": "Package_SO:HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.85x5.4mm", "QFN32_04": "Package_DFN_QFN:QFN-32-1EP_4x4mm_P0.4mm_EP2.65x2.65mm",
 "SO8EP": "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm", "QFN24": "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.5x2.5mm", "SOT583": "Package_TO_SOT_SMD:SOT-583-8", "VSSOP10": "Package_SO:VSSOP-10_3x3mm_P0.5mm", "DDA8": "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm",
 "TSSOP24": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", "TSSOP14": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", "PPAK": "Package_SO:PowerPAK_SO-8_Single",
 "L1010": "Inductor_SMD:L_Coilcraft_XAL1010-XXX", "L6060": "Inductor_SMD:L_Coilcraft_XAL6060-XXX", "L6030": "Inductor_SMD:L_Coilcraft_XAL6030-XXX", "L4030": "Inductor_SMD:L_Coilcraft_XAL4030-XXX",
 "C1210": "Capacitor_SMD:C_1210_3225Metric", "RS2512": "Resistor_SMD:R_2512_6332Metric", "PIN5": "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
})
def nfet(ref, value, g, d, s, fp="PPAK", lcsc=""):
    """PowerPAK SO-8 single (Vishay 71655; the KiCad land): pads 1, 2, 3 = source, 4 = gate, 5 = the drain tab (five pads named 5). A22 round 1 (7 Sep 2026 05:30)
    found the three-pin Q_NMOS_GDS map putting the gate and drain nets on source pins: the symbol is a five-pin connector so every pad carries its net."""
    part(ref, "Connector_Generic", "Conn_01x05", value, fp, {"1": s, "2": s, "3": s, "4": g, "5": d}, lcsc)
def vh2(ref, value, a, b="GND"): part(ref, "Connector_Generic", "Conn_01x02", value, "VH2", {"1": a, "2": b}, "C274411")
def tp(ref, net): part(ref, "Connector", "TestPoint", net, "TP", {"1": net})
# --- pack node over the dock block (32.56): four CELL+ pins, four return pins, the pre-charge pin, then the 25 A blade to VBAT (the 2590 gives 10 A continuous, 18 A peak)
for k in range(1, 5):
    part("J_CP%d" % k, "Connector", "Conn_01x01_Pin", "9 A spring pin, CELL+ (Mill-Max 0858 class, dock block)", "MMPIN", {"1": "CELL+"})
    part("J_CN%d" % k, "Connector", "Conn_01x01_Pin", "9 A spring pin, pack return (Mill-Max 0858 class, dock block)", "MMPIN", {"1": "GND"})
part("J_PRE1", "Connector", "Conn_01x01_Pin", "pre-charge pin, longer, mates first (32.24 AX)", "MMPIN", {"1": "PRECHG"}); r("R1", "10R 2W 2512", "PRECHG", "CELL+", "RS2512")
part("F1", "Device", "Fuse", "25 A mini blade (Keystone 3568 holder): pack node to VBAT", "FUSE", {"1": "CELL+", "2": "VBAT"})
# C1 and C2 are 47 uF, not the 100 uF the node was drawn with. 100 uF 25 V does not exist in a
# 1206 land with stock from any maker (47 uF is the ceiling), so the 200 uF nominal on VBAT was
# never buildable, and after DC-bias derating at 14.4 V neither number was ever close to its
# label. The pair is 94 uF nominal now. If the node needs more real bulk than that it wants an
# SMD aluminium can rather than ceramics, which is a placement change and an owner decision.
c("C1", "47u 25V", "VBAT", "GND", "C100u"); c("C2", "47u 25V", "VBAT", "GND", "C100u"); c("C3", "10u 25V 1210", "VBAT", "GND", "C1210"); part("D1", "Device", "D_TVS", "SMCJ18A (VBAT clamp)", "TVSC", {"1": "VBAT", "2": "GND"}, "C374030")
part("J_DOCK", "Connector_Generic", "Conn_01x12", "spring pins to the dock block (2x6, Preci-Dip 813-S1-012-10-016101, underside): 1-4 VIN_RAW (9 to 36 V from E6), 5-7 GND, 8 SHORE_INHIBIT, 9-10 USB of E6's sensor controller, 11 GND, 12 spare", "POGO12",
     {"1": "VIN_RAW", "2": "VIN_RAW", "3": "VIN_RAW", "4": "VIN_RAW", "5": "GND", "6": "GND", "7": "GND", "8": "SHORE_INHIBIT", "9": "USB_E6_P", "10": "USB_E6_N", "11": "GND", "12": "DOCK_SPARE"})
# --- main power control LTC2954-1 (ltc2954.pdf): the panel MAIN button, EN to every converter's enable (RAIL_EN), INT = shutdown request, KILL from the panel controller through Q1
ic("U1", 8, "LTC2954CTS8-1 push-button on/off controller", "TSOT8", {"1": "VBAT", "2": "MAIN_PB", "3": "NC", "4": "GND", "5": "PI_SHDN_REQ", "6": "RAIL_EN", "7": "NC", "8": "KILL"}, "C683782")
c("C4", "1u", "VBAT", "GND"); r("R2", "100k", "RAIL_EN", "VBAT"); r("R3", "100k", "PI_SHDN_REQ", "+3V3"); r("R4", "100k", "KILL", "VBAT")
part("Q1", "Transistor_FET", "2N7002", "2N7002: panel controller high = pull KILL low = power off (1 G, 2 S, 3 D)", "SOT23", {"1": "PI_KILL", "2": "GND", "3": "KILL"}); r("R5", "100k", "PI_KILL", "GND")
part("J_MAINSW", "Connector_Generic", "Conn_01x02", "MAIN button lead from the panel (XH2.5): PB, GND", "XH2", {"1": "MAIN_PB", "2": "GND"})
# --- LM5176 four-switch buck-boost stages (lm5176-datasheet.pdf, HTSSOP-28 PWP; Vref 0.8 V; pins: 1 EN/UVLO 2 VIN 3 VISNS 4 MODE 5 DITH 6 RT/SYNC 7 SLOPE 8 SS 9 COMP 10 AGND 11 FB 12 VOSNS
#     13 ISNS- 14 ISNS+ 15 CSG 16 CS 17 PGOOD 18 SW2 19 HDRV2 20 BOOT2 21 LDRV2 22 PGND 23 VCC 24 BIAS 25 LDRV1 26 BOOT1 27 HDRV1 28 SW1, pad 29)
def lm5176(p, uref, vin, vout, en, rfb_top, lref, lval, fet, fet_lcsc, refs, isns="10m", rcs="5m", bias=None,
           rfb_val="10k 1%", cout="10u 50V X7R 1210"):
    """one stage with prefix p: refs = (Q_bh, Q_bl, Q_bsl, Q_bsh, R_fb_top, R_fb_bot, R_rt, R_slope, R_comp, C_comp, C_comp2, C_ss, C_vcc, C_boot1, C_boot2, R_isns, R_cs, R_pgood, R_en_top, R_en_bot, Cin1, Cin2, Cout1, Cout2, Cout3, R_mode)"""
    qbh, qbl, qsl, qsh, rft, rfb, rrt, rsl, rco, cco, cco2, css, cvcc, cb1, cb2, risns, rcs_, rpg, ret, reb, ci1, ci2, co1, co2, co3, rmd = refs
    N = lambda s: p + "_" + s
    ic(uref, 29, "LM5176PWPR buck-boost controller, %s from %s" % (vout, vin), "HTSSOP28", {
        "1": N("EN"), "2": vin, "3": vin, "4": N("MODE"), "5": "GND", "6": N("RT"), "7": N("SLOPE"), "8": N("SS"), "9": N("COMP"), "10": "GND", "11": N("FB"), "12": vout,
        "13": vout, "14": N("OUT"), "15": "GND", "16": N("CS"), "17": N("PGOOD"), "18": N("SW2"), "19": N("HDRV2"), "20": N("BOOT2"), "21": N("LDRV2"), "22": "GND", "23": N("VCC"),
        "24": bias or vout, "25": N("LDRV1"), "26": N("BOOT1"), "27": N("HDRV1"), "28": N("SW1"), "29": "GND"}, "C442493")
    nfet(qbh, fet, N("HDRV1"), vin, N("SW1"), lcsc=fet_lcsc); nfet(qbl, fet, N("LDRV1"), N("SW1"), N("CS"), lcsc=fet_lcsc)
    nfet(qsl, fet, N("LDRV2"), N("SW2"), N("CS"), lcsc=fet_lcsc); nfet(qsh, fet, N("HDRV2"), N("OUT"), N("SW2"), lcsc=fet_lcsc)
    part(lref, "Device", "L", lval, "L1010", {"1": N("SW1"), "2": N("SW2")})
    r(rft, rfb_top + " 1%", vout, N("FB")); r(rfb, rfb_val, N("FB"), "GND"); r(rrt, "40.2k (300 kHz)", N("RT"), "GND"); r(rsl, "30k (slope)", N("SLOPE"), "GND")
    r(rco, "10k", N("COMP"), N("COMPC")); c(cco, "10n", N("COMPC"), "GND"); c(cco2, "100p", N("COMP"), "GND"); c(css, "47n", N("SS"), "GND"); c(cvcc, "4.7u", N("VCC"), "GND", "C10u", bypass=(uref, "23"))   # the controller's own VCC
    c(cb1, "100n 25V", N("BOOT1"), N("SW1")); c(cb2, "100n 25V", N("BOOT2"), N("SW2"))
    r(risns, isns + "Ohm 1% 2512 (ISNS)", N("OUT"), vout, "RS2512"); r(rcs_, rcs + "Ohm 1% 2512 (CS)", N("CS"), "GND", "RS2512"); r(rpg, "100k", N("PGOOD"), "+3V3")
    r(ret, "62k 1%", en, N("EN")); r(reb, "10k 1%", N("EN"), "GND"); r(rmd, "100k (MODE: CCM)", N("MODE"), N("VCC"))
    # OWNER RULING 12 September 2026, decision 10. These five stages asked for `22u 50V X7R 1210` in all 25
    # positions and NO SUCH PART EXISTS: at a 1210 size and 50 V the ceramic tops out near 10 uF, which three
    # queries of JLCPCB's catalogue confirm and the physics explains. The ruling is the largest real part that
    # drops into the existing land, so nothing moves and A24 is re-finished rather than re-routed, with the
    # ripple re-measured before anything is ordered rather than before the folder is cut.
    #
    # The OUTPUT value is per stage because the PoE stage's output is +54V_POE: a 50 V part there is over its
    # rating before any derating or transient, which is wrong at any capacitance, so that stage takes a 100 V
    # part in the same land (C5156756, X7R, 426,107 in stock). The cost of the ruling is capacitance: 20 uF in
    # and 30 uF out per stage against 44 and 66, and X7R derates further under bias, so the ripple and loop
    # margin on a 5 A converter are owed a measurement before the order.
    c(ci1, "10u 50V X7R 1210", vin, "GND", "C1210", bypass=(uref, "2")); c(ci2, "10u 50V X7R 1210", vin, "GND", "C1210", bypass=(uref, "3"))   # the two VIN pins
    for cr in (co1, co2, co3): c(cr, cout, vout, "GND", "C1210")
# stage FE: the vehicle and shore input (9 to 36 V after E6's protection and filter) to the 20 V charge bus, 5 A; 60 V FETs
lm5176("FE", "U2", "VIN_RAW", "VBUS20", "VIN_RAW", "240k", "L1", "10uH XAL1010-103ME (Isat 14 A)", "CSD19532Q5B 100 V N-FET (4.6 mOhm at VGS 6 V, PowerPAK SO-8 / SON-8 5x6)", "C473333",
       ["Q2", "Q3", "Q4", "Q5", "R6", "R7", "R8", "R9", "R10", "C5", "C6", "C7", "C8", "C9", "C10", "R11", "R12", "R13", "R14", "R15", "C11", "C12", "C13", "C14", "C15", "R119"])
part("D2", "Device", "D_TVS", "SMCJ33A (VIN_RAW clamp behind E6's filter)", "TVSC", {"1": "VIN_RAW", "2": "GND"})
# --- charger BQ25731 (bq25731-datasheet.pdf, QFN-32 RSN; no BATFET: the battery side IS the system, the pack node CELL+ through RSR): 4S from VBUS20 at up to 8 A, I2C 0x6B on the kit bus,
#     charge inhibited by pulling ILIM_HIZ low through Q6 (the SHORE_INHIBIT function of PANEL.md section 9 becomes CHG_INHIBIT on the expander); cell count set on CELL_BATPRESZ
ic("U3", 33, "BQ25731RSNR 1 to 5 cell buck-boost charger, 4S from the 20 V bus, I2C 0x6B", "QFN32_04", {
 "1": "VBUS20", "2": "CH_ACN", "3": "VBUS20", "4": "CHRG_OK", "5": "GND", "6": "CHG_ILIM", "7": "CH_VDDA", "8": "IADPT", "9": "IBAT", "10": "PSYS", "11": "PROCHOT", "12": "SDA", "13": "SCL",
 "14": "GND", "15": "NC", "16": "CH_COMP1", "17": "CH_COMP2", "18": "CH_CELL", "19": "CELL+", "20": "CH_SRP", "21": "NC", "22": "CH_SRP", "23": "CH_SW2", "24": "CH_HIDRV2", "25": "CH_BTST2", "26": "CH_LODRV2",
 "27": "GND", "28": "REGN", "29": "CH_LODRV1", "30": "CH_BTST1", "31": "CH_HIDRV1", "32": "CH_SW1", "33": "GND"}, "C2871872")
for _qr, _g, _d, _s in (("Q7", "CH_HIDRV1", "CH_ACN", "CH_SW1"), ("Q8", "CH_LODRV1", "CH_SW1", "GND"), ("Q9", "CH_LODRV2", "CH_SW2", "GND"), ("Q10", "CH_HIDRV2", "CH_SRP", "CH_SW2")): nfet(_qr, "CSD18510Q5B 40 V N-FET", _g, _d, _s)
part("L2", "Device", "L", "3.3uH XAL6030-332ME (Isat 12.2 A)", "L6060", {"1": "CH_SW1", "2": "CH_SW2"})
r("R16", "10mOhm 1% 2512 (RAC, input current sense)", "VBUS20", "CH_ACN", "RS2512"); r("R17", "5mOhm 1% 2512 (RSR, charge current sense)", "CH_SRP", "CELL+", "RS2512")
c("C16", "100n 25V", "CH_BTST1", "CH_SW1"); c("C17", "100n 25V", "CH_BTST2", "CH_SW2"); c("C18", "3.3u", "REGN", "GND", "C10u"); r("R18", "10R", "REGN", "CH_VDDA"); c("C19", "1u", "CH_VDDA", "GND")
for k in range(3): c("C%d" % (20 + k), "10u 35V 1210", "CH_ACN", "GND", "C1210")
for k in range(3): c("C%d" % (23 + k), "22u 25V 1210", "CH_SRP", "GND", "C1210")
r("R19", "16.5k 1%", "REGN", "CHG_ILIM"); r("R20", "34.8k 1%", "CHG_ILIM", "GND"); part("Q6", "Transistor_FET", "2N7002", "2N7002: CHG_INHIBIT high = ILIM_HIZ low = charger in HiZ", "SOT23", {"1": "CHG_INHIBIT", "2": "GND", "3": "CHG_ILIM"}); r("R21", "100k", "CHG_INHIBIT", "GND")
r("R22", "10k", "CHRG_OK", "+3V3"); r("R23", "10k", "PROCHOT", "+3V3"); r("R24", "10k (PSYS load)", "PSYS", "GND"); r("R25", "10k", "CH_COMP1", "CH_COMP1C"); c("C26", "10n", "CH_COMP1C", "GND"); c("C27", "1n", "CH_COMP2", "GND")
r("R26", "60.4k 1% (CELL_BATPRESZ: 4S per Table, from VDDA)", "CH_VDDA", "CH_CELL"); r("R27", "40.2k 1%", "CH_CELL", "GND")
# --- per-slot 5 V rails: Diodes AP64500SP-13 (diodes/diodes-ap64500.pdf, SO-8 with exposed pad; pins 1 BST 2 VIN 3 EN 4 RT/CLK 5 FB 6 COMP 7 GND 8 SW 9 pad; 3.8 to 40 V in, 5 A,
#     Vref 0.8 V, 5.1 V from 53.6k/10k), enable from the panel controller over J_AB1, INA226 on each output (ti-ina226.pdf, VSSOP-10; pins 1 A1 2 A0 3 ALERT 4 SDA 5 SCL 6 VS 7 GND 8 VBUS 9 IN- 10 IN+)
def buck5(n, uref, en, out, refs, ina, a1, a0):
    L, cb, ci1, ci2, co1, co2, co3, rt, rb, rpg, rsh, rrt, rco, cco = refs
    ic(uref, 9, "AP64500SP-13 5 A buck, 5.1 V rail %s" % out, "SO8EP", {"1": "S%s_BOOT" % n, "2": "VBAT", "3": en, "4": "S%s_RT" % n, "5": "S%s_FB" % n, "6": "S%s_COMP" % n, "7": "GND", "8": "S%s_SW" % n, "9": "GND"}, "C2070920")
    part(L, "Device", "L", "4.7uH XAL6060-472ME (Isat 11 A)", "L6060", {"1": "S%s_SW" % n, "2": "S%s_OUT" % n}); c(cb, "100n", "S%s_BOOT" % n, "S%s_SW" % n)
    c(ci1, "10u 25V 1210", "VBAT", "GND", "C1210", bypass=(uref, "2")); c(ci2, "10u 25V 1210", "VBAT", "GND", "C1210", bypass=(uref, "2"))   # the buck's VIN pin
    for cr in (co1, co2, co3): c(cr, "22u 10V X7R 1210", out, "GND", "C1210")
    r(rt, "53.6k 1%", out, "S%s_FB" % n); r(rb, "10k 1%", "S%s_FB" % n, "GND"); r(rrt, "68k (RT: 500 kHz)", "S%s_RT" % n, "GND"); r(rco, "22k", "S%s_COMP" % n, "S%s_COMPC" % n); c(cco, "3.3n", "S%s_COMPC" % n, "GND")
    r(rsh, "5mOhm 1% 2512 (shunt)", "S%s_OUT" % n, out, "RS2512"); r(rpg, "100k", en, "GND")   # a slot with no controller line stays off
    ic(ina, 10, "INA226 rail monitor %s" % out, "VSSOP10", {"1": a1, "2": a0, "3": "INA_ALERT", "4": "SDA", "5": "SCL", "6": "+3V3", "7": "GND", "8": out, "9": out, "10": "S%s_OUT" % n}, "C49851")
buck5("1", "U4", "SLOT_EN1", "+5V_S1", ["L3", "C28", "C29", "C30", "C31", "C32", "C33", "R28", "R29", "R30", "R31", "R45", "R129", "C112"], "U8", "GND", "GND")        # 0x40
buck5("2", "U5", "SLOT_EN2", "+5V_S2", ["L4", "C34", "C35", "C36", "C37", "C38", "C39", "R32", "R33", "R34", "R35", "R46", "R130", "C113"], "U9", "GND", "+3V3")       # 0x41
buck5("3", "U6", "SLOT_EN3", "+5V_S3", ["L5", "C40", "C41", "C42", "C43", "C44", "C45", "R36", "R37", "R38", "R39", "R47", "R131", "C114"], "U10", "+3V3", "GND")      # 0x44
buck5("D", "U7", "DEV_EN", "+5V_DEV", ["L6", "C46", "C47", "C48", "C49", "C50", "C51", "R40", "R41", "R42", "R43", "R115", "R132", "C115"], "U11", "+3V3", "+3V3")     # 0x45
for n, out in (("1", "+5V_S1"), ("2", "+5V_S2"), ("3", "+5V_S3")): vh2("J_5V_S%s" % n, "slot %s 5.1 V rail to B16 (JST-VH, 16 AWG): + -" % n, out)
vh2("J_5V_DEV", "USB device rail to B16 (JST-VH): + -", "+5V_DEV")
r("R44", "10k", "INA_ALERT", "+3V3")
# --- 3.3 V logic: TPS62933DRLR (ti-tps62933.pdf, SOT-583; pins 1 RT 2 EN 3 VIN 4 GND 5 SW 6 BST 7 SS 8 FB; Vref 0.8 V, 3.3 V from 31.6k/10k)
ic("U12", 8, "TPS62933DRLR 3 A buck, 3.3 V logic", "SOT583", {"1": "NC", "2": "RAIL_EN", "3": "VBAT", "4": "GND", "5": "B33_SW", "6": "B33_BST", "7": "B33_SS", "8": "B33_FB"}, "C3200405")
part("L7", "Device", "L", "4.7uH XAL4030-472ME", "L4030", {"1": "B33_SW", "2": "+3V3"}); c("C52", "100n", "B33_BST", "B33_SW"); c("C53", "10n", "B33_SS", "GND"); c("C54", "10u 25V 1210", "VBAT", "GND", "C1210")
c("C55", "22u 10V X7R 1210", "+3V3", "GND", "C1210"); c("C56", "22u 10V X7R 1210", "+3V3", "GND", "C1210"); r("R48", "31.6k 1%", "+3V3", "B33_FB"); r("R49", "10k 1%", "B33_FB", "GND")
part("D3", "Device", "D_TVS", "SMBJ5.0A", "TVS", {"1": "+3V3", "2": "GND"})
# --- PA rail: LM5176 from VBAT to 13.8 V at 6 A for the RA30H1317M1 on the face plate (32.56), enabled by the hardware EMCON gate AND the software hold (PA_EN from U26); 40 V FETs
lm5176("PA", "U13", "VBAT", "+13V8_PA", "PA_EN", "162k", "L8", "6.8uH XAL1010-682ME (Isat 17 A)", "CSD18510Q5B 40 V N-FET", "",
       ["Q11", "Q12", "Q13", "Q14", "R50", "R51", "R52", "R53", "R54", "C57", "C58", "C59", "C60", "C61", "C62", "R55", "R56", "R57", "R58", "R59", "C63", "C64", "C65", "C66", "C67", "R120"], isns="2m")
ic("U14", 10, "INA226 PA rail monitor (0x46)", "VSSOP10", {"1": "+3V3", "2": "SDA", "3": "INA_ALERT", "4": "SDA", "5": "SCL", "6": "+3V3", "7": "GND", "8": "+13V8_PA", "9": "+13V8_PA", "10": "PA_OUT"}, "C49851")
vh2("J_PA", "13.8 V to the PA module on the face plate (JST-VH, 16 AWG): + -", "+13V8_PA")
# --- HF rail: a fourth LM5176 stage from VBAT to 12.0 V at 2 A for the QMX (never 13.8 V), enabled by the EMCON gate AND the software hold; FB 140k/10k
lm5176("HF", "U15", "VBAT", "+12V_HF", "HF_EN", "140k", "L9", "6.8uH XAL1010-682ME", "CSD18510Q5B 40 V N-FET", "",
       ["Q15", "Q16", "Q23", "Q24", "R60", "R61", "R62", "R63", "R64", "C68", "C69", "C70", "C71", "C72", "C73", "R65", "R122", "R123", "R124", "R125", "C74", "C108", "C109", "C110", "C111", "R126"], isns="10m")
vh2("J_HF", "12.0 V to the QMX HF unit in its lid tray (JST-VH, in the lid harness): + -", "+12V_HF")
# --- PoE rail: LM5176 in boost from VBAT to 54 V at 0.6 A for the TPS23861 PSE on B16 (the port magnetics sit beside the switch chip); 100 V FETs; software enable
lm5176("POE", "U16", "VBAT", "+54V_POE", "POE_EN", "665k", "L10", "22uH XAL1010-223ME (Isat 9 A)", "CSD19532Q5B 100 V N-FET (4.6 mOhm at VGS 6 V, PowerPAK SO-8 / SON-8 5x6)", "C473333",
       ["Q17", "Q18", "Q19", "Q20", "R66", "R67", "R68", "R69", "R70", "C75", "C76", "C77", "C78", "C79", "C80", "R71", "R72", "R73", "R74", "R75", "C81", "C82", "C83", "C84", "C85", "R121"], isns="20m", rcs="10m", bias="VBAT",
       cout="10u 100V X7R 1210")   # +54V_POE: a 50 V part on a 54 V rail is over its rating (decision 10)
ic("U17", 10, "INA226 PoE rail monitor (0x47)", "VSSOP10", {"1": "+3V3", "2": "SCL", "3": "INA_ALERT", "4": "SDA", "5": "SCL", "6": "+3V3", "7": "GND", "8": "NC", "9": "+54V_POE", "10": "POE_OUT"}, "C49851")   # VBUS pin open: 54 V exceeds its 36 V range
vh2("J_54V", "54 V to the PoE injector on B16 (JST-VH): + -", "+54V_POE")
# --- USB-C PD outlet: TPS25740A source controller (ti-tps25740.pdf, VQFN-24 RGE; pins 1 VTX 2 CC1 3 CC2 4 GND 5 HIPWR 6 CTL1 7 CTL2 8 EN9V 9 N/C 10 N/C 11 UFP 12 PSEL 13 DVDD 14 PCTRL 15 GD 16 VAUX
#     17 VDD 18 AGND 19 ISNS 20 VPWR 21 VBUS 22 GDNG 23 GDNS 24 DSCG, pad 25) with a fifth LM5176 stage as the power supply: CTL2 and CTL1 (open drain) switch R(FBL2) and R(FBL1) in
#     parallel with the stage's 20k bottom resistor (section 9.1.4 of the sheet): 5 V idle, 9 V and 15 V on request (45 W, 3 A); GDNG drives the VBUS N-FET, DSCG discharges through 43 Ohm
lm5176("PD", "U19", "VBAT", "PD_VPWR", "PD_EN", "105k", "L11", "6.8uH XAL1010-682ME", "CSD18510Q5B 40 V N-FET", "",
       ["Q21", "Q22", "Q25", "Q26", "R76", "R77", "R78", "R79", "R80", "C86", "C87", "C88", "C89", "C90", "C91", "R81", "R127", "R128", "R133", "R134", "C92", "C116", "C117", "C118", "C119", "R135"], isns="10m", rfb_val="20k 1% (R_FBL)")
r("R136", "21.0k 1% (R_FBL2: 9 V when CTL2 is low)", "PD_FB", "PD_CTL2"); r("R137", "14.0k 1% (R_FBL1: 15 V when CTL1 is low too)", "PD_FB", "PD_CTL1")
ic("U18", 25, "TPS25740ARGER USB-C PD source controller, 45 W outlet (5, 9, 15 V at 3 A)", "QFN24", {
 "1": "PD_VTX", "2": "PD_CC1", "3": "PD_CC2", "4": "GND", "5": "PD_DVDD", "6": "PD_CTL1", "7": "PD_CTL2", "8": "PD_DVDD", "9": "GND", "10": "GND", "11": "PD_UFP", "12": "PD_DVDD", "13": "PD_DVDD",
 "14": "PD_VAUX", "15": "PD_GD", "16": "PD_VAUX", "17": "+5V_DEV", "18": "GND", "19": "PD_SW", "20": "PD_VPWR", "21": "PD_VBUS", "22": "PD_GDNG", "23": "PD_SW", "24": "PD_DSCG", "25": "GND"}, "C544309")
nfet("Q27", "CSD18510Q5B 40 V N-FET (VBUS switch)", "PD_GDNG", "PD_VPWR", "PD_SW"); r("R138", "10mOhm 1% 2512 (ISNS)", "PD_SW", "PD_VBUS", "RS2512"); r("R139", "43R 1W 2512 (DSCG)", "PD_DSCG", "PD_VBUS", "RS2512")
# R141 is 698k, not the 700k the stage was drawn with: 700k is not an E96 value, JLCPCB carries
# none in 0603, and 0.3 percent on a gate-bias divider is nothing.
r("R140", "1M (GD to VPWR, 9.1.3)", "PD_VPWR", "PD_GD"); r("R141", "698k", "PD_GD", "GND"); r("R142", "10k", "PD_UFP", "+3V3"); r("R143", "100k", "PD_EN", "GND")
c("C93", "100n", "PD_VTX", "GND"); c("C94", "220n", "PD_DVDD", "GND"); c("C95", "100n", "PD_VAUX", "GND"); c("C96", "330p", "PD_CC1", "GND"); c("C97", "330p", "PD_CC2", "GND"); c("C120", "10u 25V 1210", "PD_VBUS", "GND", "C1210")
part("D4", "Device", "D_TVS", "SMBJ18A (VBUS clamp at the outlet)", "TVS", {"1": "PD_VBUS", "2": "GND"})
part("J_USBC_OUT", "Connector_Generic", "Conn_01x05", "wall USB-C outlet, power side (pigtail header): VBUS CC1 CC2 GND GND", "PIN5", {"1": "PD_VBUS", "2": "PD_CC1", "3": "PD_CC2", "4": "GND", "5": "GND"})
# --- eFuse switches TPS259631DDAR (power/tps2596.pdf, SO PowerPAD-8; pins 1 GND 2 dVdt 3 EN/UVLO 4 IN 5 OUT 6 FLT 7 ILM 8 OVLO, pad 9): the monitor (VMON, 10 to 35 V input, under 1 A),
#     the pack heater mat (VHEAT), D8's 5 V (+5V_D8 from the device rail)
def efuse(uref, vin, vout, en, flt, refs, ilim):
    cd, rilm, rflt, rov1, rov2, cin = refs
    ic(uref, 9, "TPS259631DDAR eFuse %s -> %s (%s)" % (vin, vout, ilim), "DDA8", {"1": "GND", "2": uref + "_DVDT", "3": en, "4": vin, "5": vout, "6": flt, "7": uref + "_ILM", "8": uref + "_OVLO", "9": "GND"}, "C2155778")
    # 12 September 2026: the ILM resistor carried the CURRENT as its value ("1.2 A (ILM)"), so its BOM line named
    # an ampere and no resistance and nothing could buy it. TPS2596 equation 7: RILM = 903 / (ILIM + 0.0112) ohms,
    # which the datasheet's own test conditions confirm (1 A at 909 ohm, 2 A at 453 ohm). 750R for 1.2 A, 909R for
    # 1.0 A, 453R for 2.0 A, each keeping its current in the note.
    c(cd, "10n", uref + "_DVDT", "GND"); r(rilm, ilim, uref + "_ILM", "GND"); r(rflt, "10k", flt, "+3V3"); r(rov1, "100k 1%", vin, uref + "_OVLO"); r(rov2, "10k 1% (OVLO)", uref + "_OVLO", "GND"); c(cin, "100n", vin, "GND")
efuse("U21", "VBAT", "VMON", "MON_EN", "MON_FLT", ["C98", "R90", "R91", "R92", "R93", "C99"], "750R 1% (ILM: 1.2 A)"); vh2("J_MON", "monitor supply lead to the Xenarc (JST-VH): + -", "VMON")
efuse("U22", "VBAT", "VHEAT", "HEAT_EN", "HEAT_FLT", ["C100", "R94", "R95", "R96", "R97", "C101"], "909R 1% (ILM: 1.0 A)"); part("J_HEAT", "Connector_Generic", "Conn_01x02", "heater mat under the 2590 cradle (XH2.5): + -", "XH2", {"1": "VHEAT", "2": "GND"})
efuse("U23", "+5V_DEV", "+5V_D8", "D8_EN", "D8_FLT", ["C102", "R98", "R99", "R100", "R101", "C103"], "453R 1% (ILM: 2.0 A)"); vh2("J_MEZZ_PWR1", "D8 mezzanine 5 V (JST-VH): + -", "+5V_D8")
# --- hardware EMCON gates: SN74LVC08APWR quad AND (TSSOP-14: 1 1A 2 1B 3 1Y 4 2A 5 2B 6 2Y 7 GND 8 3Y 9 3A 10 3B 11 4Y 12 4A 13 4B 14 VCC).
#     EMCON_HW is active LOW (low silences) and this board only READS it: gate 3 used to drive TX_INHIBIT_n from EMCON_HW, which closed a
#     one-inversion loop through C7's inverter and put a push-pull output on the same net as the panel's mechanical toggle. Deleted 9 September
#     2026 (red team C1); C7 now buffers rather than inverts, so the sense these two gates were always built on is the sense the panel sends.
#     The 10k pull-UP is gone with it: an unplugged ribbon must inhibit, so both lines are pulled DOWN here, as D9 already pulled TX_INHIBIT_n.
ic("U26", 14, "SN74LVC08APWR quad AND: EMCON gates for the PA rail, the HF rail and the D8 inhibit", "TSSOP14", {
 "1": "EMCON_HW", "2": "PA_SW_EN", "3": "PA_EN", "4": "EMCON_HW", "5": "HF_SW_EN", "6": "HF_EN", "7": "GND", "8": "NC", "9": "GND", "10": "GND", "11": "NC", "12": "GND", "13": "GND", "14": "+3V3"}, "C465737")
r("R102", "100k", "EMCON_HW", "GND"); c("C104", "100n", "+3V3", "GND"); r("R103", "100k", "PA_SW_EN", "GND"); r("R104", "100k", "HF_SW_EN", "GND"); r("R145", "100k", "TX_INHIBIT_n", "GND")   # fail safe: no panel, no transmit
# --- I2C: the kit bus (SDA, SCL) carries the charger, the expanders and the INA226s; no mux since the TPS55288 and TPS25750 left the design (7 Sep 01:50)
# --- expanders: U27 0x21 (outputs: the enables and the charge inhibit; inputs: faults and status), U28 0x24 (power-good lines, spares on test points); PCA9555PW pins as the A21 map
part("U27", "Interface_Expansion", "PCA9555PW", "PCA9555PW (0x21): enables and status", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "21": "+3V3", "2": "GND", "3": "GND",
 "4": "CHG_INHIBIT", "5": "MON_EN", "6": "HEAT_EN", "7": "D8_EN", "8": "POE_EN", "9": "PA_SW_EN", "10": "HF_SW_EN", "11": "DEV_EN",
 "13": "CHRG_OK", "14": "PROCHOT", "15": "MON_FLT", "16": "HEAT_FLT", "17": "D8_FLT", "18": "DOCK_SPARE", "19": "INA_ALERT", "20": "FE_PGOOD"}, "C2864778")
part("U28", "Interface_Expansion", "PCA9555PW", "PCA9555PW (0x24): power-good lines, spares", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "21": "GND", "2": "GND", "3": "+3V3",
 "4": "EXP2_SPA", "5": "EXP2_SPB", "6": "EXP2_SPC", "7": "EXP2_SPD", "8": "PA_PGOOD", "9": "POE_PGOOD", "10": "HF_PGOOD", "11": "PD_PGOOD",
 "13": "PD_EN", "14": "PD_UFP", "15": "EXP2_SP3", "16": "EXP2_SP4", "17": "EXP2_SP5", "18": "EXP2_SP6", "19": "EXP2_SP7", "20": "EXP2_SP8"}, "C2864778")
c("C106", "100n", "+3V3", "GND"); c("C107", "100n", "+3V3", "GND"); r("R110", "10k", "EXP_INT", "+3V3"); r("R111", "100k", "MON_EN", "GND"); r("R112", "100k", "HEAT_EN", "GND"); r("R113", "100k", "D8_EN", "GND"); r("R114", "100k", "POE_EN", "GND")
for k in range(3, 9): tp("TP%d" % k, "EXP2_SP%d" % k)
for k, nm in enumerate("ABCD", 1): tp("TP%d" % (22 + k), "EXP2_SP" + nm)
# --- the A to B ribbon J_AB1 (2x13, top side, at (-90, 76)) and the D8 mezzanine harness J_MEZZ1 (2x8)
# 10 September 2026 (MESHSAT-862): the ribbon pairs sit in one row of the header, ground pins on both sides (the same change in
# gen_sch_b.py and gen_sch_d.py; the two maps are compared by check_contracts.py). Pins 4/5, 7/8 and 10/11 were diagonal
# neighbours 3.59 mm apart and no pair can be laid into them. AB_SPARE keeps its seat on the D harness only.
# 11 September 2026: the mezzanine harness pair moved once more, to the END row (pins 1/2), because an inner row of a 2.54 mm
# IDC field with 1.70 mm pads leaves a 0.84 mm channel between the columns and a coupled pair needs 1.20 mm. J_AB1 below is NOT
# fixed by that move: it carries THREE pairs and a 2x13 has only two end rows, so one pair cannot escape coupled whatever the
# pin map. That is a connector decision (two headers, a mezzanine stack connector, smaller pads, or an accepted uncoupled fan)
# and it is written up with its arithmetic in v2/docs/OWNER-DECISIONS-2026-09-11.md.
# 12 September 2026 (MESHSAT-862, appendix 32.135): THE WALL PAIR LEAVES J_AB1. Measured with the pre-router honest
# about its own copper: J_AB1 carries three pairs, a 2x13 has two end rows, and the third pair's only escape is the
# 1.14 mm channel between the columns, which EXITS AT THE SAME END the end-row pair leaves from. With USB_WALL laid
# first the tool laid USB_D8 on top of it (0.00 mm, twelve DRC items); with either other order USB_WALL fails for
# want of a corridor. Three pairs do not fit one 2x13 whatever the pin map, so the wall pair takes a ribbon of its
# own: a 2x5 with the pair on pins 1/2 (an end row) and eight grounds behind it. J_AB1's pins 5 and 6 become GND.
part("J_AB1", "Connector_Generic", "Conn_02x13_Odd_Even", "A-B interconnect (IDC 2x13, top side) to B16's underside header", "IDC26", {
 "1": "USB_D8_P", "2": "USB_D8_N", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "GND", "8": "GND", "9": "PI_SHDN_REQ", "10": "PI_KILL", "11": "SDA", "12": "SCL",
 "13": "EXP_INT", "14": "TR_APRS", "15": "EMCON_HW", "16": "TX_INHIBIT_n", "17": "SLOT_EN1", "18": "SLOT_EN2", "19": "SLOT_EN3", "20": "ZEROIZE_HW", "21": "SHORE_INHIBIT", "22": "GND", "23": "GND", "24": "GND", "25": "USB_E6_P", "26": "USB_E6_N"})
part("J_AB2", "Connector_Generic", "Conn_02x05_Odd_Even", "A-B wall-port ribbon (IDC 2x5): the wall USB pair on the END row with eight grounds behind it", "IDC10", {
 "1": "USB_WALL_P", "2": "USB_WALL_N", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "GND", "8": "GND", "9": "GND", "10": "GND"})
part("J_MEZZ1", "Connector_Generic", "Conn_02x08_Odd_Even", "D8 mezzanine harness (IDC 2x8): its USB pair, the PTT mirror, the inhibit, the PA rail state, I2C", "IDC16", {
 "1": "USB_D8_P", "2": "USB_D8_N", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "TR_APRS", "8": "TX_INHIBIT_n", "9": "PA_EN", "10": "SDA", "11": "SCL", "12": "EXP_INT", "13": "+3V3", "14": "GND", "15": "ZEROIZE_HW", "16": "AB_SPARE"})
r("R116", "100k", "TR_APRS", "GND"); r("R117", "10k", "ZEROIZE_HW", "+3V3"); r("R118", "100k", "SHORE_INHIBIT", "GND")
part("J_USBW", "Connector_Generic", "Conn_01x04", "wall USB-C data pair to B16 passes here on the ribbon: this header is the pigtail's data side (D+ D- GND GND)", "PH4", {"1": "USB_WALL_P", "2": "USB_WALL_N", "3": "GND", "4": "GND"}); esd("U29", "USB_WALL_P", "USB_WALL_N", "+5V_DEV")
# --- eleven blind-mate RF sites (32.56): top-side SMA jack for the device pigtail, bottom-side Radiall R222M00720 receptacle to the dock plug
RF = (("VHF", "RF_VHF"), ("HF", "RF_HF"), ("WIFI24", "RF_WIFI24"), ("GNSS", "RF_GNSS"), ("SDR", "RF_SDR"), ("P2P-A", "RF_P2PA"), ("P2P-B", "RF_P2PB"), ("5G-MAIN", "RF_5G1"), ("5G-DIV", "RF_5G2"), ("IRID", "RF_IRIDIUM"), ("LORA", "RF_LORA"))
for k, (nm, net) in enumerate(RF, 1):
    part("J_RF%d" % k, "Connector", "Conn_Coaxial", "SMA jack (Amphenol 132134, vertical), pigtail from the %s device" % nm, "SMAV", {"1": net, "2": "GND"}, "C3174425")
    part("J_BM%d" % k, "Connector", "Conn_Coaxial", "SMP-MAX slide-on receptacle R222M00720 (underside), %s to the dock plug" % nm, "SMPMAX", {"1": net, "2": "GND"})
# --- test points and flags
for ref, net in (("TP9", "VBAT"), ("TP10", "GND"), ("TP11", "+3V3"), ("TP12", "VBUS20"), ("TP13", "VIN_RAW"), ("TP14", "CELL+"), ("TP15", "EMCON_HW"), ("TP16", "RAIL_EN"), ("TP17", "SDA"), ("TP18", "SCL"), ("TP19", "IADPT"), ("TP20", "IBAT"), ("TP21", "DOCK_SPARE"), ("TP22", "REGN"), ("TP27", "AB_SPARE")): tp(ref, net)   # TP27: AB_SPARE lost its seat on J_AB1 when the ribbon pairs took their columns (10 Sep 2026), and it reaches D alone
for i, net in enumerate(("CELL+", "VBAT", "GND", "+3V3", "VIN_RAW", "VBUS20", "+5V_S1", "+5V_S2", "+5V_S3", "+5V_DEV", "+13V8_PA", "+12V_HF", "+54V_POE", "VMON", "VHEAT", "+5V_D8", "PD_VBUS", "PD_VPWR", "PD_SW", "REGN", "CH_SRP", "CH_ACN", "PRECHG", "FE_OUT", "PA_OUT", "HF_OUT", "POE_OUT", "PD_OUT"), 1):
    part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})

# ----------------------------------------------------------------- emit
POWER = {"GND": ("power", "GND"), "+5V": ("power", "+5V"), "+3V3": ("power", "+3V3")}
libsyms = kisch.libsyms; out = kisch.out; pf_n = kisch.pf_n   # the engine's objects, by reference
ROOT = str(uuid.uuid5(kisch.UUID_NS, "root:" + PROJECT))   # deterministic: a board regenerates byte for byte (10 Sep 2026)
STUB = 5.08
kisch.configure(power=POWER, stub=STUB, root=ROOT, project=PROJECT, seed=PROJECT)
# power flag symbols connect at their pin; place them wired to a label of the net

# layout: columns, top-down cursor; group order = list order with section titles
def refs_with(prefixes, exclude=()):
    return [p["ref"] for p in P if any(p["ref"] == x or p["ref"].startswith(x) for x in prefixes) and p["ref"] not in exclude]
SECTIONS = [("PACK NODE OVER THE DOCK BLOCK (32.56): 9 A PINS, PRE-CHARGE, 25 A BLADE, DOCK SIGNAL PINS", ["J_CP1", "J_CP2", "J_CP3", "J_CP4", "J_CN1", "J_CN2", "J_CN3", "J_CN4", "J_PRE1", "R1", "F1", "C1", "C2", "C3", "D1", "J_DOCK"]),
            ("MAIN POWER CONTROL LTC2954", ["U1", "C4", "R2", "R3", "R4", "Q1", "R5", "J_MAINSW"]),
            ("FRONT END: LM5176 FROM THE 9 TO 36 V INPUT TO THE 20 V CHARGE BUS", ["U2", "Q2", "Q3", "Q4", "Q5", "L1", "R6", "R7", "R8", "R9", "R10", "C5", "C6", "C7", "C8", "C9", "C10", "R11", "R12", "R13", "R14", "R15", "C11", "C12", "C13", "C14", "C15", "R119", "D2"]),
            ("CHARGER BQ25731: 4S FROM THE 20 V BUS INTO THE PACK NODE, I2C 0x6B", ["U3", "Q7", "Q8", "Q9", "Q10", "L2", "R16", "R17", "C16", "C17", "C18", "R18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "R19", "R20", "Q6", "R21", "R22", "R23", "R24", "R25", "C26", "C27", "R26", "R27"]),
            ("SLOT RAIL S1: AP64500 5.1 V + INA226 0x40", ["U4", "L3", "C28", "C29", "C30", "C31", "C32", "C33", "R28", "R29", "R30", "R31", "R45", "R129", "C112", "U8", "J_5V_S1"]),
            ("SLOT RAIL S2: AP64500 5.1 V + INA226 0x41", ["U5", "L4", "C34", "C35", "C36", "C37", "C38", "C39", "R32", "R33", "R34", "R35", "R46", "R130", "C113", "U9", "J_5V_S2"]),
            ("SLOT RAIL S3: AP64500 5.1 V + INA226 0x44", ["U6", "L5", "C40", "C41", "C42", "C43", "C44", "C45", "R36", "R37", "R38", "R39", "R47", "R131", "C114", "U10", "J_5V_S3"]),
            ("DEVICE RAIL: AP64500 5.1 V + INA226 0x45", ["U7", "L6", "C46", "C47", "C48", "C49", "C50", "C51", "R40", "R41", "R42", "R43", "R115", "R132", "C115", "U11", "J_5V_DEV", "R44"]),
            ("3.3 V LOGIC: TPS62933", ["U12", "L7", "C52", "C53", "C54", "C55", "C56", "R48", "R49", "D3"]),
            ("PA RAIL: LM5176 13.8 V 6 A, EMCON GATED, INA226 0x46", ["U13", "Q11", "Q12", "Q13", "Q14", "L8", "R50", "R51", "R52", "R53", "R54", "C57", "C58", "C59", "C60", "C61", "C62", "R55", "R56", "R57", "R58", "R59", "C63", "C64", "C65", "C66", "C67", "R120", "U14", "J_PA"]),
            ("HF RAIL: LM5176 12.0 V 2 A, EMCON GATED", ["U15", "Q15", "Q16", "Q23", "Q24", "L9", "R60", "R61", "R62", "R63", "R64", "C68", "C69", "C70", "C71", "C72", "C73", "R65", "R122", "R123", "R124", "R125", "C74", "C108", "C109", "C110", "C111", "R126", "J_HF"]),
            ("POE RAIL: LM5176 BOOST 54 V 0.6 A, INA226 0x47", ["U16", "Q17", "Q18", "Q19", "Q20", "L10", "R66", "R67", "R68", "R69", "R70", "C75", "C76", "C77", "C78", "C79", "C80", "R71", "R72", "R73", "R74", "R75", "C81", "C82", "C83", "C84", "C85", "R121", "U17", "J_54V"]),
            ("USB-C PD OUTLET: TPS25740A + LM5176 5/9/15 V STAGE", ["U19", "Q21", "Q22", "Q25", "Q26", "L11", "R76", "R77", "R78", "R79", "R80", "C86", "C87", "C88", "C89", "C90", "C91", "R81", "R127", "R128", "R133", "R134", "C92", "C116", "C117", "C118", "C119", "R135", "R136", "R137", "U18", "Q27", "R138", "R139", "R140", "R141", "R142", "R143", "C93", "C94", "C95", "C96", "C97", "C120", "D4", "J_USBC_OUT"]),
            ("EFUSES: MONITOR, HEATER, D8 5 V", ["U21", "C98", "R90", "R91", "R92", "R93", "C99", "J_MON", "U22", "C100", "R94", "R95", "R96", "R97", "C101", "J_HEAT", "U23", "C102", "R98", "R99", "R100", "R101", "C103", "J_MEZZ_PWR1"]),
            ("EMCON GATES 74LVC08, EXPANDERS 0x21 0x24", ["U26", "R102", "C104", "R103", "R104", "U27", "U28", "C106", "C107", "R110", "R111", "R112", "R113", "R114"] + ["TP%d" % k for k in range(3, 9)] + ["TP23", "TP24", "TP25", "TP26"]),
            ("RIBBON J_AB1 2x13, MEZZANINE HARNESS J_MEZZ1 2x8, WALL USB DATA", ["J_AB1", "J_MEZZ1", "R116", "R117", "R118", "J_USBW", "U29"]),
            ("ELEVEN BLIND-MATE RF SITES: SMA JACK (TOP) + SMP-MAX RECEPTACLE (UNDERSIDE)", ["J_RF%d" % k for k in range(1, 12)] + ["J_BM%d" % k for k in range(1, 12)]),
            ("TEST POINTS, FLAGS", ["TP%d" % k for k in range(9, 23)] + ["TP27"] + ["#FLG%02d" % k for k in range(1, 28)])]
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
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-A POWER + I/O") (date "2026-09-07") (rev "A") (company "MeshSat") (comment 1 "Phase A22 schematic (appendix 32.55 and 32.56: the BB-2590/U node, LM5176 front end and PA and PoE rails, BQ25731 charger, per-slot TPS56637 rails, TPS55288 HF and PD stages, hardware EMCON gates, eleven blind-mate sites), generated by tools/gen_sch_a.py. Netlist style: every pin carries a stub and a net label.") (comment 2 "MESHSAT-830. Earlier: Phase A20 schematic (appendix 32.35: hub and dongle channels gone to B13, J_AB1 2x9 with I2S, Q5 pin order corrected per 32.36), generated by tools/gen_sch_a.py. Netlist style: every pin carries a stub and a net label.") (comment 2 "MESHSAT-709 / MESHSAT-789. A19 (4 Sep 2026 rulings, appendix 32.13 to 32.25): the kit UPS. BQ25792 charger from the dock 12 V, BQ34Z100-G1 gauge, three TPS61288L rails (M1, M2, Pi), LTC2954 main power control, TPS259571 heating-pad switch, USB2517I seven-port hub with the wall host port, PCA9555 0x21 and 0x24, seven SMP-MAX blind-mate sites, 9 A power pins to the floor battery module. No X1202."))\n'
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

# the decoupling this file writes outside the converter blocks (which declare their own, 8 Sep 2026, MESHSAT-862 Stage C):
# each capacitor sits directly after the part it serves in this file and is filtered to supply pins, so crystal loads, reset
# networks and reference filters are not listed. intent.py refuses an entry whose capacitor is not on that pin's net.
_intent.bypass("C4", "U1", "1", "VBAT")
_intent.bypass("C19", "U3", "7", "CH_VDDA")
_intent.bypass("C54", "U12", "3", "VBAT")
_intent.bypass("C94", "U18", "5", "PD_DVDD")
_intent.bypass("C104", "U26", "14", "+3V3")
_intent.bypass("C106", "U26", "14", "+3V3")
_intent.bypass("C107", "U26", "14", "+3V3")
_intent.write(OUT, PROJECT, P)   # 8 Sep 2026 (MESHSAT-862): design intent as data, out/<project>-intent.json
