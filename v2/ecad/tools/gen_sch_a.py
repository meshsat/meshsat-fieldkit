#!/usr/bin/env python3
"""PCB-A POWER + I/O, phase A2: generate the KiCad 9 schematic (netlist-style: every pin gets a
stub and a net label; power pins get power symbols). Runs on the laptop (needs the KiCad libs).
Usage: gen_sch_b.py <out.kicad_sch> <project-name>
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-a-power"
SYMDIR = "/usr/share/kicad/symbols/"

# ----------------------------------------------------------------- s-expression helpers
def parse(s):
    tok = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', s)
    def rd(i):
        out = []
        while i < len(tok):
            t = tok[i]
            if t == "(":
                sub, i = rd(i + 1); out.append(sub)
            elif t == ")":
                return out, i + 1
            else:
                out.append(t); i += 1
        return out, i
    return rd(0)[0]
def ser(n, ind=0):
    if not isinstance(n, list): return n
    if all(not isinstance(x, list) for x in n): return "(" + " ".join(n) + ")"
    parts = []; head = []
    i = 0
    while i < len(n) and not isinstance(n[i], list): head.append(n[i]); i += 1
    s = "(" + " ".join(head)
    for x in n[i:]:
        s += "\n" + "\t" * (ind + 1) + ser(x, ind + 1) if isinstance(x, list) else " " + x
    return s + "\n" + "\t" * ind + ")"
def q(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
def uq(s): return s[1:-1] if s.startswith('"') else s
LIBCACHE = {}
def lib_tree(lib):
    if lib not in LIBCACHE: LIBCACHE[lib] = parse(open(SYMDIR + lib + ".kicad_sym").read())[0]
    return LIBCACHE[lib]
def find_sym(lib, name):
    for e in lib_tree(lib)[1:]:
        if isinstance(e, list) and e and e[0] == "symbol" and uq(e[1]) == name: return e
    raise SystemExit("symbol not found: %s:%s" % (lib, name))
def flatten(lib, name):
    """Return a flattened copy of symbol `name` (resolving `extends`), renamed to lib:name for lib_symbols."""
    sym = find_sym(lib, name)
    ext = [e for e in sym if isinstance(e, list) and e and e[0] == "extends"]
    if ext:
        parent = flatten_raw(lib, uq(ext[0][1]))
        # take the parent's graphics/pins, the child's properties
        child_props = {uq(e[1]): e for e in sym if isinstance(e, list) and e and e[0] == "property"}
        out = ["symbol", q(lib + ":" + name)]
        for e in parent[2:]:
            if isinstance(e, list) and e and e[0] == "property":
                e = child_props.get(uq(e[1]), e)
            out.append(e)
        for k, e in child_props.items():
            if not any(isinstance(x, list) and x and x[0] == "property" and uq(x[1]) == k for x in out): out.append(e)
        return rename_units(out, uq(ext[0][1]), name)   # parent's bare name -> child's bare name for the unit sub-symbols
    return rename_units(flatten_raw(lib, name), name, name)
def flatten_raw(lib, name):
    import copy
    sym = copy.deepcopy(find_sym(lib, name))
    ext = [e for e in sym if isinstance(e, list) and e and e[0] == "extends"]
    if ext:
        return flatten(lib, name)
    sym[1] = q(lib + ":" + name)
    return sym
def rename_units(sym, oldname, newname):
    for e in sym:
        if isinstance(e, list) and e and e[0] == "symbol" and uq(e[1]).startswith(oldname + "_"):
            e[1] = q(newname + uq(e[1])[len(oldname):])
    # drop `extends`
    return [e for e in sym if not (isinstance(e, list) and e and e[0] == "extends")]
def pins_of(sym):
    pins = []
    def walk(n):
        for e in n:
            if isinstance(e, list) and e:
                if e[0] == "symbol": walk(e)
                elif e[0] == "pin":
                    at = [x for x in e if isinstance(x, list) and x and x[0] == "at"][0]
                    num = uq([x for x in e if isinstance(x, list) and x and x[0] == "number"][0][1])
                    nm = uq([x for x in e if isinstance(x, list) and x and x[0] == "name"][0][1])
                    pins.append((num, nm, float(at[1]), float(at[2]), int(float(at[3]))))
    walk(sym); return pins

# ----------------------------------------------------------------- the design
FP = {
 "R": "Resistor_SMD:R_0603_1608Metric", "RS": "Resistor_SMD:R_1206_3216Metric", "C": "Capacitor_SMD:C_0603_1608Metric",
 "C10u": "Capacitor_SMD:C_0805_2012Metric", "C100u": "Capacitor_SMD:C_1206_3216Metric", "LED": "LED_SMD:LED_0603_1608Metric",
 "TVS": "Diode_SMD:D_SMB", "F1812": "Fuse:Fuse_1812_4532Metric", "F2920": "Fuse:Fuse_2920_7451Metric",
 "HUB": "Package_SO:SSOP-28_5.3x10.2mm_P0.65mm", "EXP": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm",
 "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "SOT238": "Package_TO_SOT_SMD:SOT-23-8", "SOT23": "Package_TO_SOT_SMD:SOT-23",
 "WSON6": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm", "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
 "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "XH4": "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
 "IDC40": "Connector_IDC:IDC-Header_2x20_P2.54mm_Vertical", "IDC14": "Connector_IDC:IDC-Header_2x07_P2.54mm_Vertical", "IDC16": "Connector_IDC:IDC-Header_2x08_P2.54mm_Vertical",
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
P = []   # (ref, lib, symbol, value, footprint, nets{pin: net}, lcsc)
def part(ref, lib, sym, value, fp, nets, lcsc=""):
    P.append(dict(ref=ref, lib=lib, sym=sym, value=value, fp=FP.get(fp, fp), nets=nets, lcsc=lcsc))
def usb_c_recept(ref, dp, dm, vbus, cc1, cc2):
    part(ref, "Connector", "USB_C_Receptacle_USB2.0_16P", "USB-C 2.0 receptacle", "USBC",
         {"A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "A4": vbus, "A9": vbus, "B4": vbus, "B9": vbus,
          "A5": cc1, "B5": cc2, "A6": dp, "B6": dp, "A7": dm, "B7": dm, "A8": "NC", "B8": "NC", "S1": "GND"}, "C165948")
def usb_c_plug(ref, dp, dm, vbus, cc):
    # captive USB-C pigtail (4-wire cable with the Rp resistor in the plug) on a JST-PH 4-pin header: VBUS, D-, D+, GND
    part(ref, "Connector_Generic", "Conn_01x04", "USB-C pigtail header (JST-PH 2.0): VBUS D- D+ GND", "PH4", {"1": vbus, "2": dm, "3": dp, "4": "GND"})
def esd(ref, dp, dm, vbus):
    part(ref, "Power_Protection", "USBLC6-2SC6", "USBLC6-2SC6", "SOT236", {"1": dp, "6": dp, "3": dm, "4": dm, "5": vbus, "2": "GND"}, "C7519")
def r(ref, val, a, b, fp="R", lcsc=""): part(ref, "Device", "R", val, fp, {"1": a, "2": b}, lcsc)
def c(ref, val, a, b, fp="C", lcsc=""): part(ref, "Device", "C", val, fp, {"1": a, "2": b}, lcsc)
def tps2065(ref, en, out, flt): part(ref, "Power_Management", "TPS2065CDBV", "TPS2065CDBV", "SOT236", {"5": "+5V_M1", "4": en, "1": out, "3": flt, "2": "GND"})   # A19: the channels hang on rail M1
def tps22810(ref, vin, en, out, ct): part(ref, "Power_Management", "TPS22810DRV", "TPS22810DRV", "WSON6", {"6": vin, "5": en, "1": out, "2": "NC", "3": ct, "4": "GND", "7": "GND"})
def ina219(ref, inp, inn, a0, a1): part(ref, "Sensor_Energy", "INA219AxDCN", "INA219AIDCN", "SOT238", {"1": inp, "2": inn, "3": "GND", "4": "+3V3", "5": "SCL", "6": "SDA", "7": a0, "8": a1}, "C138024")

# ================================================================ A19 (appendix 32.13 to 32.25): the kit UPS on PCB-A
# The Geekworm X1202 is gone (32.17). The battery is a floor module (twelve Samsung 35E, 1S12P, 42 Ah, BMS 30 A) reaching this board over the
# dock's 9 A blind-mate power pins (32.22, 32.24). This board carries the charger, the gauge, three 5 V converters (M1, M2, Pi), the heating-pad
# switch, the main power control, a seven-port hub with the wall host port, and the seven blind-mate RF receptacles. Every value below is from
# the sheets filed in v2/vendor/ (power/, usb2517/, rf/) and the research notes v2/docs/respin-research-*-2026-09-04.md.
# --- pack node: the module's current arrives on four CELL+ pins, returns on four CELL_N pins through the gauge shunt to GND; a pre-charge pin mates first
for k in range(1, 5):
    part("J_CP%d" % k, "Connector", "Conn_01x01_Pin", "9 A spring pin, CELL+ (Mill-Max 0858 class, dock block)", "MMPIN", {"1": "CELL+"})
    part("J_CN%d" % k, "Connector", "Conn_01x01_Pin", "9 A spring pin, module return CELL_N (Mill-Max 0858 class, dock block)", "MMPIN", {"1": "CELL_N"})
part("J_PRE1", "Connector", "Conn_01x01_Pin", "pre-charge pin, longer, mates first (32.24 AX)", "MMPIN", {"1": "PRECHG"}); r("R51", "10R 2W 2512", "PRECHG", "CELL+", "RS10m")
part("R52", "Device", "R", "3 mOhm 1% 3 W 2512 shunt (RALEC LR2512-23R003F4): gauge SRP/SRN Kelvin (32.24 AV)", "RS10m", {"1": "CELL_N", "2": "GND"}, "C154688")
part("F2", "Device", "Fuse", "10 A mini blade (Keystone 3568 holder): pack node to the 8 V boost feed", "FUSE", {"1": "CELL+", "2": "MEZZ_CELL"})
part("J_MEZZ_PWR1", "Connector_Generic", "Conn_01x02", "mezzanine 8 V boost feed (JST-VH): cell node through F2 (R15)", "VH2", {"1": "MEZZ_CELL", "2": "GND"})
c("C7", "10u", "CELL+", "GND", "C10u"); c("C50", "100u 10V", "CELL+", "GND", "C100u")
# --- charger BQ25792 (bq25792.pdf, sheet in vendor/power): 12 V shore in, 1S charge up to 5 A (3 A set), JEITA on the module's 103AT, I2C 0x6B, no input FETs, no ship FET
part("U20", "Connector_Generic", "Conn_01x29", "BQ25792 1S charger from SHORE_12V (3 A set over ILIM_HIZ, 750 kHz, I2C 0x6B)", "RQM29", {
 "1": "CHG_STAT", "2": "SHORE_12V", "3": "SHORE_12V", "4": "BTST1", "5": "REGN", "6": "NC", "7": "NC", "8": "SHORE_12V", "9": "SHORE_12V", "10": "GND", "11": "GND",
 "12": "QON", "13": "GND", "14": "SCL", "15": "SDA", "16": "TS_CHG", "17": "ILIM_HIZ", "18": "CELL_SENSE_P", "19": "BTST2", "20": "PROG", "21": "CHG_INT", "22": "CELL+", "23": "CELL+",
 "24": "SDRV", "25": "SYS_CHG", "26": "SW2_CHG", "27": "GND", "28": "SW1_CHG", "29": "PMID"}, "C2862876")
part("L5", "Device", "L", "2.2uH XAL4030-222MEB (Isat 7.4 A) between SW1 and SW2 (750 kHz, PROG 4.7k)", "L4030", {"1": "SW1_CHG", "2": "SW2_CHG"})
c("C51", "10u 25V 1210", "SHORE_12V", "GND", "C1210"); c("C52", "10u 25V 1210", "SHORE_12V", "GND", "C1210")
for k in range(3): c("C%d" % (53 + k), "10u 25V 1210", "PMID", "GND", "C1210")
for k in range(5): c("C%d" % (56 + k), "10u 25V 1210", "SYS_CHG", "GND", "C1210")
c("C61", "10u", "CELL+", "GND", "C10u"); c("C62", "10u", "CELL+", "GND", "C10u")
c("C63", "47n", "BTST1", "SW1_CHG"); c("C64", "47n", "BTST2", "SW2_CHG"); c("C65", "4.7u", "REGN", "GND", "C10u"); c("C66", "1n", "SDRV", "GND"); c("C67", "100n", "CELL_SENSE_P", "GND")
r("R53", "4.7k 1% (PROG: 1S, 750 kHz)", "PROG", "GND"); r("R54", "16.5k 1%", "REGN", "ILIM_HIZ"); r("R55", "34.8k 1%", "ILIM_HIZ", "GND")   # 1 V + 0.8 R x 3 A = 3.4 V from REGN 5 V
r("R56", "5.24k 1% (RT1 JEITA)", "REGN", "TS_CHG"); r("R57", "30.31k 1% (RT2 JEITA)", "TS_CHG", "GND"); r("R58", "100k", "REGN", "QON")
r("R59", "10k", "CHG_STAT", "REGN"); r("R60", "10k", "CHG_INT", "+3V3")
part("J_DOCK", "Connector_Generic", "Conn_01x12", "spring pins to the dock block (2x6, Preci-Dip 813-S1-012-10-016101, underside): 1-4 SHORE_12V, 5-7 GND, 8 SHORE_INHIBIT, 9 module thermistor (103AT to GND), 10 GND, 11 Kelvin cell sense +, 12 spare", "POGO12",
     {"1": "SHORE_12V", "2": "SHORE_12V", "3": "SHORE_12V", "4": "SHORE_12V", "5": "GND", "6": "GND", "7": "GND", "8": "SHORE_INHIBIT", "9": "TS_CHG", "10": "GND", "11": "CELL_SENSE_P", "12": "DOCK_SPARE"})
# --- gauge BQ34Z100-G1 (bq34z100-g1.pdf): low-side shunt, Kelvin cell sense, on-board 103AT, I2C 0x55, ALERT to the second expander
part("U21", "Connector_Generic", "Conn_01x14", "BQ34Z100-G1 gauge (I2C 0x55, SCALED for 42 Ah, 3 mOhm shunt)", "TSSOP14", {
 "1": "GAUGE_ALERT", "2": "NC", "3": "NC", "4": "CELL_SENSE_P", "5": "CELL+", "6": "CELL+", "7": "REG25", "8": "CELL_N", "9": "CELL_N", "10": "GND", "11": "TS_GAUGE", "12": "NC", "13": "SCL", "14": "SDA"}, "C91302")
c("C68", "100n", "CELL+", "CELL_N"); c("C69", "1u", "REG25", "CELL_N"); part("RT1", "Device", "Thermistor_NTC", "103AT-2 10k NTC on the board near the pins (gauge temperature)", "R", {"1": "REG25", "2": "TS_GAUGE"})
# --- three converters TPS61288L (tps61288.pdf): M1 (this board's logic and hub, PCB-B's hub, display, panel, the LTE channel), M2 (PCB-B's SDR, ZigBee, LoRa, RockBLOCK), Pi 5.1 V 5 A
part("F3", "Device", "Fuse", "10 A mini blade (Keystone 3568 holder): pack node to the M1 converter", "FUSE", {"1": "CELL+", "2": "BOOST1_IN"})
part("F4", "Device", "Fuse", "10 A mini blade (Keystone 3568 holder): pack node to the M2 converter", "FUSE", {"1": "CELL+", "2": "BOOST2_IN"})
part("F5", "Device", "Fuse", "15 A mini blade (Keystone 3568 holder): pack node to the Pi converter", "FUSE", {"1": "CELL+", "2": "BOOST3_IN"})
def boost(n, uref, vin, vout, r1, r2, ncout, lref, refs):
    """One TPS61288L rail: uref the IC, refs = (L, Cbst, Cvcc, Rc, Cc, Cp, R1, R2, Cin1, Cin2, Cin3, [Cout...])."""
    L, cb, cv, rc, cc, cp, ra, rb, ci1, ci2, ci3 = refs[:11]; couts = refs[11:]
    part(uref, "Connector_Generic", "Conn_01x11", "TPS61288L boost %s (15 A switch, 500 kHz, no MODE pin)" % vout, "RQQ11",
         {"1": "FB%d" % n, "2": "COMP%d" % n, "3": "GND", "4": "SW%d" % n, "5": vout, "6": "BOOST_EN", "7": vin, "8": "BST%d" % n, "9": "SW%d" % n, "10": "GND", "11": "VCC%d" % n}, "C7498841")
    part(L, "Device", "L", "2.2uH XAL1010-222MED (Isat 34 A, 10 mm)", "L1010", {"1": vin, "2": "SW%d" % n})
    c(cb, "100n 25V", "BST%d" % n, "SW%d" % n); c(cv, "2.2u", "VCC%d" % n, "GND")
    r(rc, "8.87k", "COMP%d" % n, "COMP%dC" % n); c(cc, "3.3n", "COMP%dC" % n, "GND"); c(cp, "27p", "COMP%d" % n, "GND")
    r(ra, r1 + " 1%", vout, "FB%d" % n); r(rb, r2 + " 1%", "FB%d" % n, "GND")
    c(ci1, "22u 10V X7R 1210", vin, "GND", "C1210"); c(ci2, "22u 10V X7R 1210", vin, "GND", "C1210"); c(ci3, "100n", vin, "GND")
    for cr in couts: c(cr, "22u 10V X7R 1210", vout, "GND", "C1210")
boost(1, "U22", "BOOST1_IN", "+5V_M1", "102k", "13.7k", 6, "L2", ["L2", "C38", "C39", "R44", "C40", "C41", "R47", "R48", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C70"])
boost(2, "U23", "BOOST2_IN", "+5V_M2", "102k", "13.7k", 6, "L3", ["L3", "C71", "C72", "R61", "C73", "C74", "R62", "R63", "C75", "C76", "C77", "C78", "C79", "C80", "C81", "C82", "C83"])
boost(3, "U24", "BOOST3_IN", "+5V_PI", "75k", "10k", 4, "L4", ["L4", "C84", "C85", "R64", "C86", "C87", "R65", "R66", "C88", "C89", "C90", "C91", "C92", "C93", "C94"])
c("C95", "100u 10V", "+5V_M1", "GND", "C100u"); c("C96", "100u 10V", "+5V_M2", "GND", "C100u"); c("C97", "100u 10V", "+5V_PI", "GND", "C100u")
part("J_5V_M1", "Connector_Generic", "Conn_01x02", "rail M1 to PCB-B J_5V_M1 (JST-VH, 18 AWG): + -", "VH2", {"1": "+5V_M1", "2": "GND"})
part("J_5V_M2", "Connector_Generic", "Conn_01x02", "rail M2 to PCB-B J_5V_M2 (JST-VH, 18 AWG): + -", "VH2", {"1": "+5V_M2", "2": "GND"})
part("J_5V_PI", "Connector_Generic", "Conn_01x02", "Pi rail 5.1 V 5 A to PCB-B J_5V_PI (JST-VH, 18 AWG): + -", "VH2", {"1": "+5V_PI", "2": "GND"})
# --- main power control LTC2954-1 (ltc2954.pdf): panel MAIN button, EN to the three converters, INT = shutdown request to the Pi, KILL pulled low by the Pi through Q5
part("U25", "Connector_Generic", "Conn_01x08", "LTC2954CTS8-1 push-button on/off controller", "TSOT8", {"1": "CELL+", "2": "MAIN_PB", "3": "NC", "4": "GND", "5": "PI_SHDN_REQ", "6": "BOOST_EN", "7": "NC", "8": "KILL"}, "C683782")
c("C98", "1u", "CELL+", "GND"); r("R67", "100k", "BOOST_EN", "CELL+"); r("R68", "100k", "PI_SHDN_REQ", "+3V3"); r("R69", "100k", "KILL", "CELL+")
part("Q5", "Transistor_FET", "2N7002", "2N7002: Pi GPIO high = pull KILL low = power off", "SOT23", {"1": "PI_KILL", "2": "KILL", "3": "GND"}); r("R70", "100k", "PI_KILL", "GND")
part("J_MAINSW", "Connector_Generic", "Conn_01x02", "MAIN button lead from the panel (XH2.5): PB, GND", "XH2", {"1": "MAIN_PB", "2": "GND"})
# --- heating pad on the shore rail (tps2595.pdf, TPS259571: 12 V eFuse, 2 A limit, auto-retry), enable from the second expander
part("F6", "Device", "Polyfuse", "2.5A hold 1812", "F1812", {"1": "SHORE_12V", "2": "HEAT_IN"})
part("U26", "Connector_Generic", "Conn_01x09", "TPS259571DSGR eFuse 12 V 2.0 A for the heating pad", "DSG8", {"1": "HEAT_DVDT", "2": "HEAT_EN", "3": "HEAT_IN", "4": "HEAT_IN", "5": "HEAT_OUT", "6": "HEAT_FLT", "7": "HEAT_ILM", "8": "GND", "9": "GND"}, "C471038")
c("C99", "10n", "HEAT_DVDT", "GND"); r("R71", "1.02k 1% (2.0 A)", "HEAT_ILM", "GND"); r("R72", "10k", "HEAT_FLT", "+3V3"); r("R73", "100k", "HEAT_EN", "GND"); c("C100", "100n", "HEAT_IN", "GND")
part("J_HEAT", "Connector_Generic", "Conn_01x02", "12 V heating pad on the battery module (XH2.5): + -", "XH2", {"1": "HEAT_OUT", "2": "GND"})
# --- 3.3 V logic from M1: TPS563201 buck (tps563201.pdf), 3 A, replaces the AMS1117 (the hub alone draws up to 460 mA)
part("U5", "Regulator_Switching", "TPS563201", "TPS563201 3.3 V buck from M1", "SOT236", {"1": "GND", "2": "SW33", "3": "+5V_M1", "4": "FB33", "5": "+5V_M1", "6": "BST33"})
part("L6", "Device", "L", "3.3uH XAL4020-332MEB", "L4020", {"1": "SW33", "2": "+3V3"}); c("C13", "100n", "BST33", "SW33"); c("C14", "10u", "+5V_M1", "GND", "C10u"); c("C15", "22u 10V X7R 1210", "+3V3", "GND", "C1210"); c("C101", "22u 10V X7R 1210", "+3V3", "GND", "C1210")
r("R74", "33.2k 1%", "+3V3", "FB33"); r("R75", "10k 1%", "FB33", "GND")   # 0.768 V x (1 + 33.2/10) = 3.32 V
part("D2", "Device", "D_TVS", "SMBJ5.0A", "TVS", {"1": "+5V_M1", "2": "GND"})
r("R18", "1k", "+5V_M1", "LED_PWR_A")   # PWR LED on the M1 rail
for ref, net in (("TP1", "+5V_M1"), ("TP2", "GND"), ("TP3", "+3V3"), ("TP4", "CELL_N"), ("TP5", "CELL+"), ("TP6", "SHORE_INHIBIT"), ("TP7", "GAUGE_ALERT"), ("TP8", "MEZZ_SPARE1"), ("TP9", "TX_INHIBIT_n"), ("TP10", "SHORE_12V"), ("TP11", "CHG_INT"), ("TP12", "+5V_M2"), ("TP13", "+5V_PI"), ("TP14", "DOCK_SPARE"), ("TP15", "BOOST_EN"), ("TP16", "CELL_SENSE_P")):
    part(ref, "Connector", "TestPoint", net, "TP", {"1": net})
for i, net in enumerate(("CELL+", "CELL_N", "GND", "+3V3", "+5V_M1", "+5V_M2", "+5V_PI", "5V_WIFI", "5V_GPS", "5V_CODEC", "5V_UART", "5V_WALL", "BOOST1_IN", "BOOST2_IN", "BOOST3_IN", "SHORE_12V", "HEAT_IN", "HEAT_OUT", "REGN", "SYS_CHG", "PMID", "REG25"), 1):
    part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})
# --- seven-port hub USB2517I (usb2517 sheet): CFG_SEL 000 = internal defaults with straps; ports 6 and 7 disabled by the PRT_DIS straps; upstream from the Pi over J_AB1
part("U6", "Connector_Generic", "Conn_02x33_Odd_Even", "USB2517I-JZX seven-port USB 2.0 hub (strap defaults, ports 6-7 disabled)", "QFN64", {
 "1": "USB_WIFI_N", "2": "USB_WIFI_P", "3": "USB_GPS_N", "4": "USB_GPS_P", "5": "+3V3", "6": "USB_CODEC_N", "7": "USB_CODEC_P", "8": "USB_UART_N", "9": "USB_UART_P", "10": "+3V3",
 "11": "USB_WALL_N", "12": "USB_WALL_P", "13": "GND", "14": "NC", "15": "NC", "16": "NC", "17": "NC", "18": "NC", "19": "GND", "20": "NC", "21": "FLT_UART", "22": "FLT_CODEC", "23": "NC", "24": "+3V3", "25": "HUB_VD18",
 "26": "NC", "27": "FLT_GPS", "28": "FLT_WIFI", "29": "NC", "30": "NC", "31": "NC", "32": "NC", "33": "NC", "34": "NC", "35": "FLT_WALL", "36": "NC", "37": "NC", "38": "NC", "39": "NC", "40": "NC", "41": "HUB_CFG0", "42": "HUB_CFG1", "43": "+3V3", "44": "+3V3", "45": "NC",
 "46": "+3V3", "47": "NC", "48": "NC", "49": "NC", "50": "NC", "51": "NC", "52": "+3V3", "53": "HUB_DIS6M", "54": "HUB_DIS6P", "55": "HUB_DIS7M", "56": "HUB_DIS7P", "57": "+3V3", "58": "USB_A_N", "59": "USB_A_P", "60": "XOUT", "61": "XIN", "62": "HUB_VD18PLL", "63": "HUB_RBIAS", "64": "+3V3", "65": "GND", "66": "NC"}, "C1521556")
part("Y1", "Device", "Crystal_GND24", "24 MHz 3225", "XTAL", {"1": "XIN", "3": "XOUT", "2": "GND", "4": "GND"})
c("C16", "22p", "XIN", "GND"); c("C17", "22p", "XOUT", "GND"); r("R19", "12.0k 1% (RBIAS)", "HUB_RBIAS", "GND")
for k, net in enumerate(("+3V3", "+3V3", "+3V3", "+3V3", "+3V3", "+3V3", "+3V3"), 18): c("C%d" % k, "100n", net, "GND")   # C18..C24 at VDD33, VDDA33 x4, VDD33CR, VDD33PLL
c("C25", "1u", "HUB_VD18", "GND"); c("C26", "1u", "HUB_VD18PLL", "GND"); c("C27", "1u", "+3V3", "GND")
r("R20", "10k", "HUB_CFG0", "GND"); r("R21", "10k", "HUB_CFG1", "GND")
for ref, net in (("R22", "HUB_DIS6M"), ("R23", "HUB_DIS6P"), ("R25", "HUB_DIS7M"), ("R79", "HUB_DIS7P")): r(ref, "10k", net, "+3V3")   # PRT_DIS straps: ports 6 and 7 disabled
esd("U27", "USB_A_P", "USB_A_N", "+3V3")
# --- channels on the M1 rail: WiFi (0x46), GPS (0x47), codec (0x48), UART (0x49), wall host port (0x4A)
tps2065("U7", "EN_WIFI", "SW_WIFI", "FLT_WIFI"); r("R26", "10k", "FLT_WIFI", "+3V3"); r("R40", "100k", "EN_WIFI", "+3V3"); c("C34", "100n", "+5V_M1", "GND"); r("R27", "0.1R 1% 1206", "SW_WIFI", "5V_WIFI", "RS"); ina219("U8", "SW_WIFI", "5V_WIFI", "SDA", "+3V3"); c("C28", "100n", "+3V3", "GND"); c("C29", "10u", "5V_WIFI", "GND", "C10u")
part("J_WIFI1", "Connector", "USB_A", "USB-A receptacle, WiFi", "USBA", {"1": "5V_WIFI", "2": "USB_WIFI_N", "3": "USB_WIFI_P", "4": "GND", "5": "GND"}); esd("U9", "USB_WIFI_P", "USB_WIFI_N", "5V_WIFI")
tps2065("U10", "EN_GPS", "SW_GPS", "FLT_GPS"); r("R28", "10k", "FLT_GPS", "+3V3"); r("R41", "100k", "EN_GPS", "+3V3"); c("C35", "100n", "+5V_M1", "GND"); r("R29", "0.1R 1% 1206", "SW_GPS", "5V_GPS", "RS"); ina219("U11", "SW_GPS", "5V_GPS", "SCL", "+3V3"); c("C30", "100n", "+3V3", "GND"); c("C31", "10u", "5V_GPS", "GND", "C10u")
part("J_GPS1", "Connector", "USB_A", "USB-A receptacle, GPS", "USBA", {"1": "5V_GPS", "2": "USB_GPS_N", "3": "USB_GPS_P", "4": "GND", "5": "GND"}); esd("U12", "USB_GPS_P", "USB_GPS_N", "5V_GPS")
tps2065("U13", "EN_CODEC", "SW_CODEC", "FLT_CODEC"); r("R30", "10k", "FLT_CODEC", "+3V3"); r("R42", "100k", "EN_CODEC", "+3V3"); c("C36", "100n", "+5V_M1", "GND"); r("R31", "0.1R 1% 1206", "SW_CODEC", "5V_CODEC", "RS"); ina219("U14", "SW_CODEC", "5V_CODEC", "GND", "SDA"); c("C32", "100n", "+3V3", "GND"); c("C33", "10u", "5V_CODEC", "GND", "C10u"); esd("U15", "USB_CODEC_P", "USB_CODEC_N", "5V_CODEC")
tps2065("U16", "EN_UART", "SW_UART", "FLT_UART"); r("R32", "10k", "FLT_UART", "+3V3"); r("R43", "100k", "EN_UART", "+3V3"); c("C37", "100n", "+5V_M1", "GND"); r("R33", "0.1R 1% 1206", "SW_UART", "5V_UART", "RS"); ina219("U17", "SW_UART", "5V_UART", "+3V3", "SDA"); c("C102", "100n", "+3V3", "GND"); c("C103", "10u", "5V_UART", "GND", "C10u"); esd("U18", "USB_UART_P", "USB_UART_N", "5V_UART")
tps2065("U28", "EN_WALL", "SW_WALL", "FLT_WALL"); r("R76", "10k", "FLT_WALL", "+3V3"); r("R77", "100k", "EN_WALL", "+3V3"); c("C104", "100n", "+5V_M1", "GND"); r("R78", "0.1R 1% 1206", "SW_WALL", "5V_WALL", "RS"); ina219("U29", "SW_WALL", "5V_WALL", "SDA", "SDA"); c("C105", "100n", "+3V3", "GND"); c("C106", "10u", "5V_WALL", "GND", "C10u")
part("J_WALL1", "Connector", "USB_A", "USB-A receptacle, internal cable to the Glenair 233-370 wall host port", "USBA", {"1": "5V_WALL", "2": "USB_WALL_N", "3": "USB_WALL_P", "4": "GND", "5": "GND"}); esd("U30", "USB_WALL_P", "USB_WALL_N", "5V_WALL")
# --- expanders: U19 0x21 (as A18) and U31 0x24 (A19: wall port, heating pad, charger, gauge)
part("U19", "Interface_Expansion", "PCA9555PW", "PCA9555PW (0x21)", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "21": "+3V3", "2": "GND", "3": "GND",
 "4": "EN_WIFI", "5": "EN_GPS", "6": "EN_CODEC", "7": "EN_UART", "8": "SHORE_INHIBIT", "9": "EXP_SP2", "10": "MEZZ_EN", "11": "LED_MESH_K",
 "13": "LED_SAT_K", "14": "LED_LTE_K", "15": "LED_SYS_K", "16": "FLT_WIFI", "17": "FLT_GPS", "18": "FLT_CODEC", "19": "FLT_UART", "20": "EXP_SP3"}, "C5626")
c("C107", "100n", "+3V3", "GND"); r("R34", "10k", "EXP_INT", "+3V3"); part("TP17", "Connector", "TestPoint", "EXP_SP2", "TP", {"1": "EXP_SP2"}); part("TP18", "Connector", "TestPoint", "EXP_SP3", "TP", {"1": "EXP_SP3"})
part("U31", "Interface_Expansion", "PCA9555PW", "PCA9555PW (0x24): wall port, heating pad, charger, gauge", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "21": "GND", "2": "GND", "3": "+3V3",
 "4": "EN_WALL", "5": "HEAT_EN", "6": "FLT_WALL", "7": "HEAT_FLT", "8": "CHG_INT", "9": "GAUGE_ALERT", "10": "CHG_STAT", "11": "EXP2_SP0",
 "13": "EXP2_SP1", "14": "EXP2_SP2", "15": "EXP2_SP3", "16": "EXP2_SP4", "17": "EXP2_SP5", "18": "EXP2_SP6", "19": "EXP2_SP7", "20": "EXP2_SP8"}, "C5626")
c("C108", "100n", "+3V3", "GND")
for k in range(9): part("TP%d" % (19 + k), "Connector", "TestPoint", "EXP2_SP%d" % k, "TP", {"1": "EXP2_SP%d" % k})
r("R35", "330R", "+3V3", "LED_MESH_A"); r("R36", "330R", "+3V3", "LED_SAT_A"); r("R37", "330R", "+3V3", "LED_LTE_A"); r("R38", "330R", "+3V3", "LED_SYS_A")
part("J_LEDS1", "Connector_Generic", "Conn_01x10", "front-wall LED row (XH2.5): PWR MESH SAT LTE SYS", "XH10",
     {"1": "LED_PWR_A", "2": "GND", "3": "LED_MESH_A", "4": "LED_MESH_K", "5": "LED_SAT_A", "6": "LED_SAT_K", "7": "LED_LTE_A", "8": "LED_LTE_K", "9": "LED_SYS_A", "10": "LED_SYS_K"})
# --- mezzanine harness and interconnect (ribbon: no 5 V any more; 1 = shutdown request, 2 = Pi KILL)
part("J_MEZZ1", "Connector_Generic", "Conn_02x08_Odd_Even", "APRS mezzanine harness (IDC 2x8)", "IDC16", {
 "1": "GND", "2": "5V_CODEC", "3": "USB_CODEC_P", "4": "USB_CODEC_N", "5": "GND", "6": "5V_UART", "7": "USB_UART_P", "8": "USB_UART_N",
 "9": "GND", "10": "TR_APRS", "11": "MEZZ_EN", "12": "+3V3", "13": "GND", "14": "MEZZ_SPARE1", "15": "TX_INHIBIT_n", "16": "GND"})
r("R39", "100k", "TR_APRS", "GND")
part("J_AB1", "Connector_Generic", "Conn_02x07_Odd_Even", "A-B interconnect (IDC 2x7, top side)", "IDC14", {
 "1": "PI_SHDN_REQ", "2": "PI_KILL", "3": "GND", "4": "USB_A_P", "5": "USB_A_N", "6": "GND", "7": "SDA", "8": "SCL", "9": "EXP_INT", "10": "TR_APRS", "11": "VBUS_A_SENSE", "12": "AB_SPARE", "13": "GND", "14": "TX_INHIBIT_n"})
part("TP28", "Connector", "TestPoint", "AB_SPARE", "TP", {"1": "AB_SPARE"}); r("R24", "4.7k", "VBUS_A_SENSE", "GND")
# --- seven blind-mate RF sites (32.23): top-side SMA jack for the module pigtail, bottom-side Radiall R222M00720 receptacle to the dock plug
RF = (("UHF", "RF_UHF"), ("WIFI24", "RF_WIFI24"), ("WIFI58", "RF_WIFI58"), ("SDR", "RF_SDR"), ("LTE", "RF_LTE"), ("IRID", "RF_IRIDIUM"), ("LORA", "RF_LORA"))
for k, (nm, net) in enumerate(RF, 1):
    part("J_RF%d" % k, "Connector", "Conn_Coaxial", "SMA jack (Amphenol 132134, vertical), pigtail from the %s module" % nm, "SMAV", {"1": net, "2": "GND"})
    part("J_BM%d" % k, "Connector", "Conn_Coaxial", "SMP-MAX slide-on receptacle R222M00720 (underside), %s to the dock plug" % nm, "SMPMAX", {"1": net, "2": "GND"})

# ----------------------------------------------------------------- emit
POWER = {"GND": ("power", "GND"), "+5V": ("power", "+5V"), "+3V3": ("power", "+3V3")}
libsyms = {}; out = []; ROOT = str(uuid.uuid4())
def U(): return str(uuid.uuid4())
def ensure(lib, name):
    key = lib + ":" + name
    if key not in libsyms: libsyms[key] = flatten(lib, name)
    return libsyms[key]
def extents(sym):
    pins = pins_of(sym)
    xs = [p[2] for p in pins] or [0]; ys = [p[3] for p in pins] or [0]
    return min(xs), max(xs), min(ys), max(ys)
def place_symbol(lib, name, ref, value, fp, x, y, lcsc="", hide_props=False):
    sym = ensure(lib, name); pins = pins_of(sym)
    x0, x1, y0, y1 = extents(sym)
    s = '(symbol (lib_id %s) (at %.2f %.2f 0) (unit 1) (exclude_from_sim no) (in_bom %s) (on_board %s) (dnp no) (fields_autoplaced yes) (uuid "%s")\n' % (
        q(lib + ":" + name), x, y, "no" if lib == "power" or name in ("TestPoint",) else "yes", "no" if lib == "power" else "yes", U())
    def prop(k, v, px, py, hide):
        return '\t(property %s %s (at %.2f %.2f 0) (effects (font (size 1.27 1.27)) (justify left)%s))\n' % (q(k), q(v), px, py, " (hide yes)" if hide else "")
    s += prop("Reference", ref, x + x1 + 1.27, y - y1 - 1.27, hide_props)
    s += prop("Value", value, x + x1 + 1.27, y - y1 + 1.27, hide_props)
    s += prop("Footprint", fp, x, y, True); s += prop("Datasheet", "", x, y, True); s += prop("Description", "", x, y, True)
    if lcsc: s += prop("LCSC", lcsc, x, y, True)
    for num, nm, px, py, rot in pins: s += '\t(pin %s (uuid "%s"))\n' % (q(num), U())
    s += '\t(instances (project %s (path "/%s" (reference %s) (unit 1))))\n)\n' % (q(PROJECT), ROOT, q(ref))
    out.append(s); return pins
def wire(x1, y1, x2, y2): out.append('(wire (pts (xy %.2f %.2f) (xy %.2f %.2f)) (stroke (width 0) (type default)) (uuid "%s"))\n' % (x1, y1, x2, y2, U()))
def label(net, x, y, rot):
    just = {0: "left bottom", 180: "right bottom", 90: "left bottom", 270: "right bottom"}[rot]
    out.append('(label %s (at %.2f %.2f %d) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify %s)) (uuid "%s"))\n' % (q(net), x, y, rot, just, U()))
def noconn(x, y): out.append('(no_connect (at %.2f %.2f) (uuid "%s"))\n' % (x, y, U()))
def text(t, x, y, size=2.0): out.append('(text %s (exclude_from_sim no) (at %.2f %.2f 0) (effects (font (size %.2f %.2f) bold) (justify left bottom)) (uuid "%s"))\n' % (q(t), x, y, size, size, U()))
STUB = 5.08
pf_n = [0]
def emit_part(p, x, y):
    pins = place_symbol(p["lib"], p["sym"], p["ref"], p["value"], p["fp"], x, y, p["lcsc"])
    seen = set()
    for num, nm, px, py, rot in pins:
        sx, sy = x + px, y - py                      # KiCad sheet: Y down
        key = (round(sx, 2), round(sy, 2))
        net = p["nets"].get(num)
        if net is None:
            raise SystemExit("%s pin %s (%s) has no net assignment" % (p["ref"], num, nm))
        if key in seen: continue                     # stacked pins (USB-C GND/VBUS) share one point
        seen.add(key)
        if net == "NC":
            noconn(sx, sy); continue
        dx, dy = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[rot]
        if net in POWER:
            lib, nm2 = POWER[net]
            ex, ey = sx + dx * STUB, sy + dy * STUB
            wire(sx, sy, ex, ey)
            place_symbol(lib, nm2, "#PWR%03d" % pf_n[0], net, "", ex, ey); pf_n[0] += 1
        else:
            ex, ey = sx + dx * STUB, sy + dy * STUB
            wire(sx, sy, ex, ey)
            lrot = {(-1, 0): 180, (1, 0): 0, (0, 1): 270, (0, -1): 90}[(dx, dy)]
            label(net, ex, ey, lrot)
# power flag symbols connect at their pin; place them wired to a label of the net
def emit_pwr_flag(p, x, y):
    place_symbol("power", "PWR_FLAG", p["ref"], "PWR_FLAG", "", x, y)
    net = p["nets"]["1"]
    wire(x, y, x, y + STUB)
    if net in POWER:
        lib, nm2 = POWER[net]; place_symbol(lib, nm2, "#PWR%03d" % pf_n[0], net, "", x, y + STUB); pf_n[0] += 1
    else: label(net, x, y + STUB, 270)

# layout: columns, top-down cursor; group order = list order with section titles
SECTIONS = [("PACK NODE (A19): MODULE CURRENT OVER THE DOCK PINS, PRE-CHARGE, GAUGE SHUNT, MEZZANINE FEED", ["J_CP1", "J_CP2", "J_CP3", "J_CP4", "J_CN1", "J_CN2", "J_CN3", "J_CN4", "J_PRE1", "R51", "R52", "F2", "J_MEZZ_PWR1", "C7", "C50"]),
            ("CHARGER BQ25792 (SHORE_12V -> CELL+, 3 A, JEITA ON THE MODULE THERMISTOR) + DOCK SIGNAL PINS", ["U20", "L5", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58", "C59", "C60", "C61", "C62", "C63", "C64", "C65", "C66", "C67", "R53", "R54", "R55", "R56", "R57", "R58", "R59", "R60", "J_DOCK"]),
            ("GAUGE BQ34Z100-G1 (0x55)", ["U21", "C68", "C69", "RT1"]),
            ("RAIL M1: F3 + TPS61288L 5.05 V (LOGIC, HUB, PCB-B M1)", ["F3", "U22", "L2", "C38", "C39", "R44", "C40", "C41", "R47", "R48", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C70", "C95", "J_5V_M1"]),
            ("RAIL M2: F4 + TPS61288L 5.05 V (PCB-B M2)", ["F4", "U23", "L3", "C71", "C72", "R61", "C73", "C74", "R62", "R63", "C75", "C76", "C77", "C78", "C79", "C80", "C81", "C82", "C83", "C96", "J_5V_M2"]),
            ("RAIL PI: F5 + TPS61288L 5.1 V 5 A", ["F5", "U24", "L4", "C84", "C85", "R64", "C86", "C87", "R65", "R66", "C88", "C89", "C90", "C91", "C92", "C93", "C94", "C97", "J_5V_PI"]),
            ("MAIN POWER CONTROL LTC2954 + HEATING PAD SWITCH TPS259571", ["U25", "C98", "R67", "R68", "R69", "Q5", "R70", "J_MAINSW", "F6", "U26", "C99", "R71", "R72", "R73", "C100", "J_HEAT"]),
            ("3.3 V BUCK TPS563201 FROM M1, TEST POINTS, FLAGS", ["U5", "L6", "C13", "C14", "C15", "C101", "R74", "R75", "D2", "R18"] + ["TP%d" % k for k in range(1, 17)] + ["#FLG%02d" % k for k in range(1, 23)]),
            ("USB 2.0 HUB USB2517I (upstream over J_AB1, ports 6-7 disabled)", ["U6", "Y1", "C16", "C17", "R19", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "R20", "R21", "R22", "R23", "R25", "R79", "U27"]),
            ("CH1 WIFI (0x46)", ["U7", "R26", "R40", "C34", "R27", "U8", "C28", "C29", "J_WIFI1", "U9"]),
            ("CH2 GPS (0x47)", ["U10", "R28", "R41", "C35", "R29", "U11", "C30", "C31", "J_GPS1", "U12"]),
            ("CH3 MEZZANINE CODEC (0x48)", ["U13", "R30", "R42", "C36", "R31", "U14", "C32", "C33", "U15"]),
            ("CH4 MEZZANINE UART (0x49)", ["U16", "R32", "R43", "C37", "R33", "U17", "C102", "C103", "U18"]),
            ("CH5 WALL HOST PORT (0x4A)", ["U28", "R76", "R77", "C104", "R78", "U29", "C105", "C106", "J_WALL1", "U30"]),
            ("I2C EXPANDERS PCA9555 0x21 AND 0x24, LEDs", ["U19", "C107", "R34", "TP17", "TP18", "U31", "C108"] + ["TP%d" % k for k in range(19, 28)] + ["R35", "R36", "R37", "R38", "J_LEDS1"]),
            ("MEZZANINE HARNESS + A-B INTERCONNECT", ["J_MEZZ1", "R39", "J_AB1", "TP28", "R24"]),
            ("SEVEN BLIND-MATE RF SITES: SMA JACK (TOP) + SMP-MAX RECEPTACLE (UNDERSIDE)", ["J_RF%d" % k for k in range(1, 8)] + ["J_BM%d" % k for k in range(1, 8)])]
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
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-A POWER + I/O") (date "2026-09-05") (rev "A") (company "MeshSat") (comment 1 "Phase A2 schematic (A4: 16.3 fixes), generated by tools/gen_sch_a.py. Netlist style: every pin carries a stub and a net label.") (comment 2 "MESHSAT-709 / MESHSAT-789. A19 (4 Sep 2026 rulings, appendix 32.13 to 32.25): the kit UPS. BQ25792 charger from the dock 12 V, BQ34Z100-G1 gauge, three TPS61288L rails (M1, M2, Pi), LTC2954 main power control, TPS259571 heating-pad switch, USB2517I seven-port hub with the wall host port, PCA9555 0x21 and 0x24, seven SMP-MAX blind-mate sites, 9 A power pins to the floor battery module. No X1202."))\n'
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
