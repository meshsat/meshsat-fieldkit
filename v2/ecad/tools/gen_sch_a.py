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
def tps2065(ref, en, out, flt): part(ref, "Power_Management", "TPS2065CDBV", "TPS2065CDBV", "SOT236", {"5": "+5V_MOD", "4": en, "1": out, "3": flt, "2": "GND"})   # A17: the channels hang on the module rail
def tps22810(ref, vin, en, out, ct): part(ref, "Power_Management", "TPS22810DRV", "TPS22810DRV", "WSON6", {"6": vin, "5": en, "1": out, "2": "NC", "3": ct, "4": "GND", "7": "GND"})
def ina219(ref, inp, inn, a0, a1): part(ref, "Sensor_Energy", "INA219AxDCN", "INA219AIDCN", "SOT238", {"1": inp, "2": inn, "3": "GND", "4": "+3V3", "5": "SCL", "6": "SDA", "7": a0, "8": a1}, "C138024")

# --- pack node (A15, owner ruling 3 Sep): the welded 1S8P pack sits in parallel with the X1202's four cells (1S12P on one node, behind the
#     X1202's own protection); the X1202 charges all twelve from its USB-C or its 6-18 V barrel. No charger, protection, gauge or boost on PCB-A.
part("J_PACK", "Connector_Generic", "Conn_01x02", "welded 1S8P pack, 8 x Samsung 35E, 1S BMS 15 A with NTC cutoff inside (XT60-M): + -", "XT60", {"1": "CELL+", "2": "CELL_N"})
part("J_X1202BAT", "Connector_Generic", "Conn_01x02", "lead to the X1202 battery terminals B+ / B- (holder solder tabs), 16 AWG (XT60-M): + - (through F1)", "XT60", {"1": "CELL_X", "2": "CELL_N"})
part("F1", "Device", "Fuse", "15 A mini blade (Keystone 3568 holder): pack node to the X1202 lead", "FUSE", {"1": "CELL+", "2": "CELL_X"})
part("F2", "Device", "Fuse", "10 A mini blade (Keystone 3568 holder): pack node to the 8 V boost feed", "FUSE", {"1": "CELL+", "2": "MEZZ_CELL"})
part("J_MEZZ_PWR1", "Connector_Generic", "Conn_01x02", "mezzanine 8 V boost feed (JST-VH): cell node through F2 (R15)", "VH2", {"1": "MEZZ_CELL", "2": "GND"})
c("C7", "10u", "CELL+", "GND", "C10u")
# --- A17 (owner ruling 3 Sep 2026 evening, option B of the 5 V budget): the 5 V MODULE RAIL comes from the cell node, not from the X1202.
#     F3 + TPS61089 boost -> +5V_MOD feeds this board's four channel switches and, over J_5V_MOD1 (JST-VH) to PCB-B's J_5V_MOD, the whole of
#     PCB-B (modules, hub, display, panel). The X1202's 5.1 V output then carries only the Pi. EN follows the X1202's 5 V (sense line X1202_5V
#     from PCB-B over J_AB1.12) so the rail dies with the kit. RILIM 100k = 10 A typ / 9 A min peak (the part's maximum): 5 V at about 4.2 A
#     continuous from 3.3 V cells (7 A switch current), bursts to the limit; the unserialised burst case sags the modules, never the Pi.
part("F3", "Device", "Fuse", "15 A mini blade (Keystone 3568 holder): pack node to the 5 V module-rail boost", "FUSE", {"1": "CELL+", "2": "BOOST_CELL"})
part("U20", "Regulator_Switching", "TPS61089", "TPS61089 boost 5.05 V module rail", "QFN11",
     {"1": "FSW5", "2": "BST5_VCC", "3": "FB5", "4": "COMP5", "5": "GND", "6": "+5V_MOD", "7": "MOD_EN", "8": "ILIM5", "9": "BOOST_CELL", "10": "BOOT5", "11": "SW5"})
part("L2", "Device", "L", "1.5uH XAL6030-152MEB (Isat 12 A, 5.6 mOhm)", "L6030", {"1": "BOOST_CELL", "2": "SW5"})
c("C38", "100n 25V", "BOOT5", "SW5"); c("C39", "1u", "BST5_VCC", "GND"); r("R44", "301k 1% (500 kHz)", "FSW5", "SW5"); r("R45", "100k 1% (ILIM 10 A peak, 9 A min)", "ILIM5", "GND")
r("R46", "17.4k", "COMP5", "COMP5C"); c("C40", "4.7n", "COMP5C", "GND"); r("R47", "63.4k 1%", "+5V_MOD", "FB5"); r("R48", "20k 1%", "FB5", "GND")   # 1.212 V x (1 + 63.4/20) = 5.05 V
r("R49", "100k", "MOD_EN", "GND"); r("R50", "10k", "X1202_5V", "MOD_EN")   # EN follows the X1202 5 V sense (EN abs max 7 V), off when the kit is off
c("C41", "22u 10V X7R 1210", "BOOST_CELL", "GND", "C1210"); c("C42", "22u 10V X7R 1210", "BOOST_CELL", "GND", "C1210"); c("C43", "100n", "BOOST_CELL", "GND")
for i in range(4): c("C%d" % (44 + i), "22u 10V X7R 1210", "+5V_MOD", "GND", "C1210")
c("C48", "100n", "+5V_MOD", "GND"); c("C49", "100u 10V", "+5V_MOD", "GND", "C100u")
part("J_5V_MOD1", "Connector_Generic", "Conn_01x02", "5 V module rail to PCB-B J_5V_MOD (JST-VH, 18 AWG): + -", "VH2", {"1": "+5V_MOD", "2": "GND"})
# --- 5V_A rail from PCB-B, local 3.3 V
c("C13", "100u 10V", "+5V", "GND", "C100u"); part("D2", "Device", "D_TVS", "SMBJ5.0A", "TVS", {"1": "+5V", "2": "GND"})
part("U5", "Regulator_Linear", "AMS1117-3.3", "AMS1117-3.3", "SOT223", {"3": "+5V", "2": "+3V3", "1": "GND"})
c("C14", "10u", "+5V", "GND", "C10u"); c("C15", "10u", "+3V3", "GND", "C10u")
r("R18", "1k", "+5V_MOD", "LED_PWR_A")   # A17: hub, its decoupling and the PWR LED on the module-rail plane; the ribbon +5V feeds only the LDO in the PWR zone (keeps the hub escape lanes free)
for ref, net in (("TP1", "+5V"), ("TP2", "GND"), ("TP3", "+3V3"), ("TP4", "CELL_N"), ("TP5", "CELL+"), ("TP6", "SHORE_INHIBIT"), ("TP7", "EXP_SP2"), ("TP8", "MEZZ_SPARE1"), ("TP9", "TX_INHIBIT_n"), ("TP10", "SHORE_12V"), ("TP11", "EXP_SP3"), ("TP12", "+5V_MOD"), ("TP13", "BOOST_CELL")):
    part(ref, "Connector", "TestPoint", net, "TP", {"1": net})
for i, net in enumerate(("+5V", "CELL_N", "GND", "CELL+", "5V_WIFI", "5V_GPS", "5V_CODEC", "5V_UART", "BOOST_CELL", "X1202_5V"), 1):
    part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})
# --- hub (upstream from PCB-B over J_AB1)
part("U6", "Interface_USB", "FE1.1s", "FE1.1s", "HUB", {
 "1": "GND", "2": "XOUT", "3": "XIN", "4": "USB_UART_N", "5": "USB_UART_P", "6": "USB_CODEC_N", "7": "USB_CODEC_P", "8": "USB_GPS_N", "9": "USB_GPS_P",
 "10": "USB_WIFI_N", "11": "USB_WIFI_P", "12": "HUB_VD18", "13": "HUB_VD33", "14": "HUB_REXT", "15": "USB_A_N", "16": "USB_A_P", "17": "HUB_RST",
 "18": "HUB_VBUSM", "19": "HUB_BUSJ", "20": "+5V_MOD", "21": "HUB_VD33", "22": "NC", "23": "HUB_LED1", "24": "NC", "25": "NC", "26": "HUB_OVCJ", "27": "HUB_TESTJ", "28": "HUB_VD18"}, "C2848")
part("Y1", "Device", "Crystal_GND24", "12 MHz 3225", "XTAL", {"1": "XIN", "3": "XOUT", "2": "GND", "4": "GND"})
c("C16", "22p", "XIN", "GND"); c("C17", "22p", "XOUT", "GND"); r("R19", "2.7k 1% (REXT, verify datasheet)", "HUB_REXT", "GND")
c("C18", "100n", "HUB_VD33", "GND"); c("C19", "1u", "HUB_VD33", "GND"); c("C20", "100n", "HUB_VD18", "GND"); c("C21", "1u", "HUB_VD18", "GND"); c("C22", "100n", "+5V_MOD", "GND")
r("R20", "10k", "HUB_RST", "HUB_VD33"); c("C23", "1u", "HUB_RST", "GND"); r("R21", "10k", "HUB_BUSJ", "HUB_VD33"); part("JP1", "Jumper", "SolderJumper_2_Open", "BUSJ to GND = bus-powered", "JP2", {"1": "HUB_BUSJ", "2": "GND"})
r("R22", "10k", "HUB_TESTJ", "HUB_VD33"); r("R23", "10k", "HUB_OVCJ", "HUB_VD33"); r("R24", "4.7k", "VBUS_A_SENSE", "HUB_VBUSM")
r("R25", "1k", "HUB_VD33", "LED_HUB_A"); part("LED2", "Device", "LED", "amber hub", "LED", {"2": "LED_HUB_A", "1": "HUB_LED1"})
# --- channels: WiFi (0x46), GPS (0x47), codec (0x48), UART (0x49)
tps2065("U7", "EN_WIFI", "SW_WIFI", "FLT_WIFI"); r("R26", "10k", "FLT_WIFI", "+3V3"); r("R40", "100k", "EN_WIFI", "+3V3"); c("C34", "100n", "+5V_MOD", "GND"); r("R27", "0.1R 1% 1206", "SW_WIFI", "5V_WIFI", "RS"); ina219("U8", "SW_WIFI", "5V_WIFI", "SDA", "+3V3"); c("C24", "100n", "+3V3", "GND"); c("C25", "10u", "5V_WIFI", "GND", "C10u")
part("J_WIFI1", "Connector", "USB_A", "USB-A receptacle, WiFi", "USBA", {"1": "5V_WIFI", "2": "USB_WIFI_N", "3": "USB_WIFI_P", "4": "GND", "5": "GND"}); esd("U9", "USB_WIFI_P", "USB_WIFI_N", "5V_WIFI")
tps2065("U10", "EN_GPS", "SW_GPS", "FLT_GPS"); r("R28", "10k", "FLT_GPS", "+3V3"); r("R41", "100k", "EN_GPS", "+3V3"); c("C35", "100n", "+5V_MOD", "GND"); r("R29", "0.1R 1% 1206", "SW_GPS", "5V_GPS", "RS"); ina219("U11", "SW_GPS", "5V_GPS", "SCL", "+3V3"); c("C26", "100n", "+3V3", "GND"); c("C27", "10u", "5V_GPS", "GND", "C10u")
part("J_GPS1", "Connector", "USB_A", "USB-A receptacle, GPS", "USBA", {"1": "5V_GPS", "2": "USB_GPS_N", "3": "USB_GPS_P", "4": "GND", "5": "GND"}); esd("U12", "USB_GPS_P", "USB_GPS_N", "5V_GPS")
tps2065("U13", "EN_CODEC", "SW_CODEC", "FLT_CODEC"); r("R30", "10k", "FLT_CODEC", "+3V3"); r("R42", "100k", "EN_CODEC", "+3V3"); c("C36", "100n", "+5V_MOD", "GND"); r("R31", "0.1R 1% 1206", "SW_CODEC", "5V_CODEC", "RS"); ina219("U14", "SW_CODEC", "5V_CODEC", "GND", "SDA"); c("C28", "100n", "+3V3", "GND"); c("C29", "10u", "5V_CODEC", "GND", "C10u"); esd("U15", "USB_CODEC_P", "USB_CODEC_N", "5V_CODEC")
tps2065("U16", "EN_UART", "SW_UART", "FLT_UART"); r("R32", "10k", "FLT_UART", "+3V3"); r("R43", "100k", "EN_UART", "+3V3"); c("C37", "100n", "+5V_MOD", "GND"); r("R33", "0.1R 1% 1206", "SW_UART", "5V_UART", "RS"); ina219("U17", "SW_UART", "5V_UART", "+3V3", "SDA"); c("C30", "100n", "+3V3", "GND"); c("C31", "10u", "5V_UART", "GND", "C10u"); esd("U18", "USB_UART_P", "USB_UART_N", "5V_UART")
# --- expander 0x21, LEDs
part("U19", "Interface_Expansion", "PCA9555PW", "PCA9555PW (0x21)", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "21": "+3V3", "2": "GND", "3": "GND",
 "4": "EN_WIFI", "5": "EN_GPS", "6": "EN_CODEC", "7": "EN_UART", "8": "SHORE_INHIBIT", "9": "EXP_SP2", "10": "MEZZ_EN", "11": "LED_MESH_K",
 "13": "LED_SAT_K", "14": "LED_LTE_K", "15": "LED_SYS_K", "16": "FLT_WIFI", "17": "FLT_GPS", "18": "FLT_CODEC", "19": "FLT_UART", "20": "EXP_SP3"}, "C5626")
c("C32", "100n", "+3V3", "GND"); r("R34", "10k", "EXP_INT", "+3V3")
r("R35", "330R", "+3V3", "LED_MESH_A"); r("R36", "330R", "+3V3", "LED_SAT_A"); r("R37", "330R", "+3V3", "LED_LTE_A"); r("R38", "330R", "+3V3", "LED_SYS_A")
part("J_LEDS1", "Connector_Generic", "Conn_01x10", "front-wall LED row (XH2.5): PWR MESH SAT LTE SYS", "XH10",
     {"1": "LED_PWR_A", "2": "GND", "3": "LED_MESH_A", "4": "LED_MESH_K", "5": "LED_SAT_A", "6": "LED_SAT_K", "7": "LED_LTE_A", "8": "LED_LTE_K", "9": "LED_SYS_A", "10": "LED_SYS_K"})
# --- mezzanine harness and interconnect
part("J_MEZZ1", "Connector_Generic", "Conn_02x08_Odd_Even", "APRS mezzanine harness (IDC 2x8)", "IDC16", {
 "1": "GND", "2": "5V_CODEC", "3": "USB_CODEC_P", "4": "USB_CODEC_N", "5": "GND", "6": "5V_UART", "7": "USB_UART_P", "8": "USB_UART_N",
 "9": "GND", "10": "TR_APRS", "11": "MEZZ_EN", "12": "+3V3", "13": "GND", "14": "MEZZ_SPARE1", "15": "TX_INHIBIT_n", "16": "GND"})
r("R39", "100k", "TR_APRS", "GND")
# dock (PCB-E1): spring pins on the underside land on the dock targets; 12 V shore rail up to the X1202 DC jack by a lead
part("J_DOCK", "Connector_Generic", "Conn_01x08", "spring pins to the PCB-E1 dock: 1-4 SHORE_12V, 5-7 GND, 8 SHORE_INHIBIT (expander 0x21 bit 0.4, high = dock converter off) (underside)", "POGO", {"1": "SHORE_12V", "2": "SHORE_12V", "3": "SHORE_12V", "4": "SHORE_12V", "5": "GND", "6": "GND", "7": "GND", "8": "SHORE_INHIBIT"})
part("J_X1202DC", "Connector_Generic", "Conn_01x02", "12 V shore lead to the X1202 DC jack (XH2.5 -> 5521 plug)", "XH2", {"1": "SHORE_12V", "2": "GND"})
part("J_AB1", "Connector_Generic", "Conn_02x07_Odd_Even", "A-B interconnect (IDC 2x7, top side)", "IDC14", {
 "1": "+5V", "2": "+5V", "3": "GND", "4": "USB_A_P", "5": "USB_A_N", "6": "GND", "7": "SDA", "8": "SCL", "9": "EXP_INT", "10": "TR_APRS", "11": "VBUS_A_SENSE", "12": "X1202_5V", "13": "GND", "14": "TX_INHIBIT_n"})

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
SECTIONS = [("PACK NODE (A17): WELDED 1S8P PACK IN PARALLEL WITH THE X1202 CELLS, MEZZANINE FEED", ["J_PACK", "F1", "J_X1202BAT", "F2", "J_MEZZ_PWR1", "C7"]),
            ("5 V MODULE RAIL (A17): F3 + TPS61089 BOOST FROM THE CELL NODE, EN FROM THE X1202 5 V SENSE (J_AB1.12)", ["F3", "U20", "L2", "C38", "C39", "R44", "R45", "R46", "C40", "R47", "R48", "R49", "R50", "C41", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "J_5V_MOD1"]),
            ("5V_A RAIL FROM PCB-B, 3.3 V LDO, TEST POINTS, FLAGS", ["C13", "D2", "U5", "C14", "C15", "R18", "TP1", "TP2", "TP3", "TP4", "TP5", "TP6", "TP7", "TP8", "TP9", "TP10", "TP11", "TP12", "TP13", "#FLG01", "#FLG02", "#FLG03", "#FLG04", "#FLG05", "#FLG06", "#FLG07", "#FLG08", "#FLG09", "#FLG10"]),
            ("USB 2.0 HUB FE1.1s (upstream over J_AB1)", ["U6", "Y1", "C16", "C17", "R19", "C18", "C19", "C20", "C21", "C22", "R20", "C23", "R21", "JP1", "R22", "R23", "R24", "R25", "LED2"]),
            ("CH1 WIFI (0x46)", ["U7", "R26", "R40", "C34", "R27", "U8", "C24", "C25", "J_WIFI1", "U9"]),
            ("CH2 GPS (0x47)", ["U10", "R28", "R41", "C35", "R29", "U11", "C26", "C27", "J_GPS1", "U12"]),
            ("CH3 MEZZANINE CODEC (0x48)", ["U13", "R30", "R42", "C36", "R31", "U14", "C28", "C29", "U15"]),
            ("CH4 MEZZANINE UART (0x49)", ["U16", "R32", "R43", "C37", "R33", "U17", "C30", "C31", "U18"]),
            ("I2C EXPANDER PCA9555 (0x21): EN, LEDs, FAULTS, SPARES", ["U19", "C32", "R34", "R35", "R36", "R37", "R38", "J_LEDS1"]),
            ("MEZZANINE HARNESS + A-B INTERCONNECT + DOCK", ["J_MEZZ1", "R39", "J_AB1", "J_DOCK", "J_X1202DC"])]
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
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-A POWER + I/O") (date "2026-09-02") (rev "A") (company "MeshSat") (comment 1 "Phase A2 schematic (A4: 16.3 fixes), generated by tools/gen_sch_a.py. Netlist style: every pin carries a stub and a net label.") (comment 2 "MESHSAT-709. A17: 5 V module rail (F3, TPS61089 boost from the cell node, EN from the X1202 5 V sense over J_AB1.12), option B of the 3 Sep 5 V budget ruling. A15: welded 1S8P pack in parallel with the X1202 cells (the X1202 is the only charger and UPS), USB hub with eFuses + INA219, PCA9555 0x21, mezzanine harness, dock spring pins for the 12 V shore lead."))\n'
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
