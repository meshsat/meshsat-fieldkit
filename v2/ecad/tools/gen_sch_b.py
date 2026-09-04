#!/usr/bin/env python3
"""PCB-B COMPUTE, phase B2: generate the KiCad 9 schematic (netlist-style: every pin gets a
stub and a net label; power pins get power symbols). Runs on the laptop (needs the KiCad libs).
Usage: gen_sch_b.py <out.kicad_sch> <project-name>
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-b-compute"
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
 "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "XH4": "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical",
 "IDC40": "Connector_IDC:IDC-Header_2x20_P2.54mm_Vertical", "IDC14": "Connector_IDC:IDC-Header_2x07_P2.54mm_Vertical", "IDC16": "Connector_IDC:IDC-Header_2x08_P2.54mm_Vertical", "IDC20": "Connector_IDC:IDC-Header_2x10_P2.54mm_Vertical",
 "PICO10": "Connector_Molex:Molex_PicoBlade_53047-1010_1x10_P1.25mm_Vertical",
 "USBA": "Connector_USB:USB_A_Stewart_SS-52100-001_Horizontal", "USBC": "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", "USBCP": "Connector_USB:USB_C_Plug_Molex_105444", "PH4": "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical",
 "JP2": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "JP3": "Jumper:SolderJumper-3_P1.3mm_Open_RoundedPad1.0x1.5mm",
 "TP": "TestPoint:TestPoint_Pad_D1.5mm",
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
def tps2065(ref, en, out, flt, rail="+5V"): part(ref, "Power_Management", "TPS2065CDBV", "TPS2065CDBV", "SOT236", {"5": rail, "4": en, "1": out, "3": flt, "2": "GND"})
def tps22810(ref, vin, en, out, ct): part(ref, "Power_Management", "TPS22810DRV", "TPS22810DRV", "WSON6", {"6": vin, "5": en, "1": out, "2": "NC", "3": ct, "4": "GND", "7": "GND"})
def ina219(ref, inp, inn, a0, a1): part(ref, "Sensor_Energy", "INA219AxDCN", "INA219AIDCN", "SOT238", {"1": inp, "2": inn, "3": "GND", "4": "+3V3", "5": "SCL", "6": "SDA", "7": a0, "8": a1}, "C138024")

# --- power input
# no trunk polyfuse (audits 17.5 and round 5): a PPTC sized to the X1202 derates below the load in a sealed case; every branch has its own polyfuse or limited switch plus an INA219
# B12 (appendix 32.17, 32.21, 32.23): the X1202 is gone; PCB-A feeds three rails over JST-VH leads: M1 (+5V here: hub, display, panel, the LTE channel),
#     M2 (+5V_M2: SDR, ZigBee, LoRa, RockBLOCK channels) and the Pi rail (+5V_PI: only the Pi, by a lead with a USB-C plug into the Pi 5).
part("J_5V_M1", "Connector_Generic", "Conn_01x02", "5 V rail M1 from PCB-A J_5V_M1 (JST-VH, 18 AWG): + - ; hub, display, panel, LTE channel", "VH2", {"1": "+5V", "2": "GND"})
part("J_5V_M2", "Connector_Generic", "Conn_01x02", "5 V rail M2 from PCB-A J_5V_M2 (JST-VH, 18 AWG): + - ; SDR, ZigBee, LoRa, RockBLOCK channels", "VH2", {"1": "+5V_M2", "2": "GND"})
part("J_5V_PI", "Connector_Generic", "Conn_01x02", "Pi rail 5.1 V 5 A from PCB-A J_5V_PI (JST-VH, 18 AWG): + - ; lead to a USB-C plug in the Pi 5 power input (Rp 10k in the plug)", "VH2", {"1": "+5V_PI", "2": "GND"})
part("D3", "Device", "D_TVS", "SMBJ5.0A", "TVS", {"1": "+5V_M2", "2": "GND"}); c("C40", "100u 10V", "+5V_M2", "GND", "C100u"); c("C41", "100u 10V", "+5V_M2", "GND", "C100u")
part("D4", "Device", "D_TVS", "SMBJ5.0A", "TVS", {"1": "+5V_PI", "2": "GND"}); c("C42", "100u 10V", "+5V_PI", "GND", "C100u")
part("D1", "Device", "D_TVS", "SMBJ5.0A", "TVS", {"1": "+5V", "2": "GND"})
c("C1", "100u 10V", "+5V", "GND", "C100u"); c("C2", "100u 10V", "+5V", "GND", "C100u")
r("R1", "1k", "+5V", "LED_5V_A"); part("LED1", "Device", "LED", "green 5V", "LED", {"2": "LED_5V_A", "1": "GND"})
part("J_TD2", "Connector_Generic", "Conn_01x02", "Touch Display 2 5V (XH2.54)", "XH2", {"1": "+5V", "2": "GND"})
for ref, net in (("TP1", "+5V"), ("TP2", "GND"), ("TP3", "+3V3"), ("TP4", "SDA"), ("TP5", "SCL"), ("TP11", "TX_INHIBIT_n"), ("TP12", "EXP_SPARE5"), ("TP13", "PI_KILL"), ("TP14", "AB_SPARE"), ("TP15", "+5V_M2"), ("TP16", "+5V_PI")):
    part(ref, "Connector", "TestPoint", net, "TP", {"1": net})
for i, net in enumerate(("+5V", "+5V_M2", "+5V_PI", "+3V3", "GND", "5V_RTL", "5V_ZB", "5V_XIAO", "5V_RB", "5V_TC", "TC_FUSED", "XIAO_FUSED", "RB_FUSED"), 1):
    part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})
# --- Pi GPIO ribbon
part("J_GPIO1", "Connector_Generic", "Conn_02x20_Odd_Even", "Pi 5 GPIO ribbon 2x20", "IDC40", {
 "1": "+3V3", "2": "NC", "3": "SDA", "4": "NC", "5": "SCL", "6": "GND", "7": "UART2_TX", "8": "UART0_TX", "9": "GND", "10": "UART0_RX",
 "11": "PI_KILL", "12": "RB_XMTG", "13": "TR_APRS", "14": "GND", "15": "RB_NETAV", "16": "RB_STATUS", "17": "+3V3", "18": "RB_CTRL", "19": "SPI_MOSI", "20": "GND",
 "21": "EPD_DC", "22": "EXP_INT", "23": "SPI_SCLK", "24": "SPI_CE0", "25": "GND", "26": "EPD_RES_ALT", "27": "NC", "28": "NC", "29": "UART2_RX", "30": "GND",
 "31": "PI_SHDN_REQ", "32": "PANEL_PWM", "33": "PWM1", "34": "GND", "35": "DCF_PON", "36": "NC", "37": "RB_IEN", "38": "NC", "39": "GND", "40": "DCF_T"})
# --- hub
part("U1", "Interface_USB", "FE1.1s", "FE1.1s", "HUB", {
 "1": "GND", "2": "XOUT", "3": "XIN", "4": "USB_XIAO_N", "5": "USB_XIAO_P", "6": "USB_TC_N", "7": "USB_TC_P", "8": "USB_ZB_N", "9": "USB_ZB_P",
 "10": "USB_RTL_N", "11": "USB_RTL_P", "12": "HUB_VD18", "13": "HUB_VD33", "14": "HUB_REXT", "15": "USB_UP_N", "16": "USB_UP_P", "17": "HUB_RST",
 "18": "HUB_VBUSM", "19": "HUB_BUSJ", "20": "+5V", "21": "HUB_VD33", "22": "NC", "23": "HUB_LED1", "24": "NC", "25": "NC", "26": "HUB_OVCJ", "27": "HUB_TESTJ", "28": "HUB_VD18"}, "C2848")
part("Y1", "Device", "Crystal_GND24", "12 MHz 3225", "XTAL", {"1": "XIN", "3": "XOUT", "2": "GND", "4": "GND"})
c("C3", "22p", "XIN", "GND"); c("C4", "22p", "XOUT", "GND")
r("R2", "2.7k 1% (REXT, verify datasheet)", "HUB_REXT", "GND")
c("C5", "100n", "HUB_VD33", "GND"); c("C6", "1u", "HUB_VD33", "GND"); c("C7", "100n", "HUB_VD18", "GND"); c("C8", "1u", "HUB_VD18", "GND")
c("C9", "100n", "+5V", "GND"); c("C10", "10u", "+5V", "GND", "C10u")
r("R3", "10k", "HUB_RST", "HUB_VD33"); c("C11", "1u", "HUB_RST", "GND")
r("R4", "10k", "HUB_BUSJ", "HUB_VD33"); part("JP1", "Jumper", "SolderJumper_2_Open", "BUSJ to GND = bus-powered", "JP2", {"1": "HUB_BUSJ", "2": "GND"})
r("R5", "10k", "HUB_TESTJ", "HUB_VD33"); r("R6", "10k", "HUB_OVCJ", "HUB_VD33")
r("R7", "4.7k", "USB_UP_VBUS", "HUB_VBUSM")
r("R8", "1k", "HUB_VD33", "LED_HUB_A"); part("LED2", "Device", "LED", "amber hub", "LED", {"2": "LED_HUB_A", "1": "HUB_LED1"})
usb_c_recept("J_USB_UP1", "USB_UP_P", "USB_UP_N", "USB_UP_VBUS", "CC1_UP", "CC2_UP"); r("R9", "5.1k", "CC1_UP", "GND"); r("R10", "5.1k", "CC2_UP", "GND"); esd("U2", "USB_UP_P", "USB_UP_N", "USB_UP_VBUS")
usb_c_recept("J_USB_UP2", "USB_A_P", "USB_A_N", "VBUS_A_SENSE", "CC1_UP2", "CC2_UP2"); r("R11", "5.1k", "CC1_UP2", "GND"); r("R12", "5.1k", "CC2_UP2", "GND"); esd("U3", "USB_A_P", "USB_A_N", "VBUS_A_SENSE")
# --- channels
tps2065("U4", "EN_RTL", "SW_RTL", "FLT_RTL", "+5V_M2"); r("R13", "10k", "FLT_RTL", "+3V3"); r("R30", "100k", "EN_RTL", "+3V3"); c("C33", "100n", "+5V_M2", "GND"); r("R14", "0.1R 1% 1206", "SW_RTL", "5V_RTL", "RS"); ina219("U5", "SW_RTL", "5V_RTL", "GND", "GND")
c("C12", "100n", "+3V3", "GND"); c("C13", "10u", "5V_RTL", "GND", "C10u")
part("J_RTL1", "Connector", "USB_A", "USB-A receptacle RTL-SDR", "USBA", {"1": "5V_RTL", "2": "USB_RTL_N", "3": "USB_RTL_P", "4": "GND", "5": "GND"}); esd("U6", "USB_RTL_P", "USB_RTL_N", "5V_RTL")
tps2065("U7", "EN_ZB", "SW_ZB", "FLT_ZB", "+5V_M2"); r("R15", "10k", "FLT_ZB", "+3V3"); r("R31", "100k", "EN_ZB", "+3V3"); c("C34", "100n", "+5V_M2", "GND"); r("R16", "0.1R 1% 1206", "SW_ZB", "5V_ZB", "RS"); ina219("U8", "SW_ZB", "5V_ZB", "+3V3", "GND")
c("C14", "100n", "+3V3", "GND"); c("C15", "10u", "5V_ZB", "GND", "C10u")
part("J_ZB1", "Connector", "USB_A", "USB-A receptacle ZigBee", "USBA", {"1": "5V_ZB", "2": "USB_ZB_N", "3": "USB_ZB_P", "4": "GND", "5": "GND"}); esd("U9", "USB_ZB_P", "USB_ZB_N", "5V_ZB")
# CH3 LoRa: XIAO (0.3 A) or T-Beam 1W (1.3 A at 5 V on transmit): 2 A polyfuse + TPS22810 2 A switch (the TPS2065C limits at 1 A)
part("F4", "Device", "Polyfuse", "2A hold 1812", "F1812", {"1": "+5V_M2", "2": "XIAO_FUSED"}); tps22810("U10", "XIAO_FUSED", "EN_XIAO", "SW_XIAO", "XIAO_CT"); c("C27", "1n", "XIAO_CT", "GND"); c("C29", "1u", "XIAO_FUSED", "GND"); r("R32", "100k", "EN_XIAO", "+3V3")
r("R17", "10k", "FLT_XIAO", "+3V3"); r("R18", "0.05R 1% 1206", "SW_XIAO", "5V_XIAO", "RS"); ina219("U11", "SW_XIAO", "5V_XIAO", "+3V3", "+3V3")
c("C16", "100n", "+3V3", "GND"); c("C17", "10u", "5V_XIAO", "GND", "C10u")
usb_c_plug("J_XIAO1", "USB_XIAO_P", "USB_XIAO_N", "5V_XIAO", None); usb_c_plug("J_TBEAM1", "USB_XIAO_P", "USB_XIAO_N", "5V_XIAO", None); esd("U12", "USB_XIAO_P", "USB_XIAO_N", "5V_XIAO")   # one of J_XIAO1 / J_TBEAM1 used
# CH4 RockBLOCK: 9704 transmit bursts exceed the TPS2065C 1 A limit: 2 A polyfuse + TPS22810 2 A switch
part("F5", "Device", "Polyfuse", "2A hold 1812", "F1812", {"1": "+5V_M2", "2": "RB_FUSED"}); tps22810("U13", "RB_FUSED", "EN_RB", "SW_RB", "RB_CT"); c("C28", "1n", "RB_CT", "GND"); c("C30", "1u", "RB_FUSED", "GND"); r("R33", "100k", "EN_RB", "+3V3")
r("R20", "10k", "FLT_RB", "+3V3"); r("R21", "0.05R 1% 1206", "SW_RB", "5V_RB", "RS"); ina219("U14", "SW_RB", "5V_RB", "SDA", "GND")
c("C18", "100n", "+3V3", "GND"); c("C19", "10u", "5V_RB", "GND", "C10u")
part("F2", "Device", "Polyfuse", "2A hold 1812", "F1812", {"1": "+5V", "2": "TC_FUSED"}); tps22810("U15", "TC_FUSED", "EN_TC", "SW_TC", "TC_CT"); c("C20", "1n", "TC_CT", "GND"); c("C31", "1u", "TC_FUSED", "GND"); r("R34", "100k", "EN_TC", "+3V3")
r("R22", "0.05R 1% 1206", "SW_TC", "5V_TC", "RS"); ina219("U16", "SW_TC", "5V_TC", "GND", "+3V3"); c("C21", "100n", "+3V3", "GND"); c("C22", "10u", "5V_TC", "GND", "C10u")
usb_c_plug("J_TCALL1", "USB_TC_P", "USB_TC_N", "5V_TC", None); esd("U17", "USB_TC_P", "USB_TC_N", "5V_TC")
# panel ribbon (B10): PCB-C control panel gets fused 5 V, I2C, SPI0 for the e-paper, the PWM dimmer, the TX mirror and the EMCON line
part("F6", "Device", "Polyfuse", "0.5A hold 1812", "F1812", {"1": "+5V", "2": "PANEL_5V"})
part("J_PANEL", "Connector_Generic", "Conn_02x10_Odd_Even", "panel ribbon to PCB-C (IDC 2x10)", "IDC20", {
 "1": "PANEL_5V", "2": "PANEL_5V", "3": "GND", "4": "SDA", "5": "SCL", "6": "EXP_INT", "7": "TR_APRS", "8": "EPD_DC", "9": "GND", "10": "SPI_SCLK",
 "11": "GND", "12": "SPI_MOSI", "13": "GND", "14": "SPI_CE0", "15": "EPD_RES_ALT", "16": "PWM1", "17": "PANEL_PWM", "18": "GND", "19": "TX_INHIBIT_n", "20": "+3V3"})
# B12: the channel to PCB-A (5V_A over the ribbon) is gone: PCB-A makes its own logic supply from M1
# --- expander
part("U20", "Interface_Expansion", "PCA9555PW", "PCA9555PW", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "2": "GND", "21": "GND", "3": "GND",
 "4": "EN_RTL", "5": "EN_ZB", "6": "EN_XIAO", "7": "EN_RB", "8": "EN_TC", "9": "EXP_SPARE6", "10": "EXP_SPARE0", "11": "EXP_SPARE1",
 "13": "FLT_RTL", "14": "FLT_ZB", "15": "FLT_XIAO", "16": "FLT_RB", "17": "EXP_SPARE5", "18": "EXP_SPARE2", "19": "EXP_SPARE3", "20": "EXP_SPARE4"}, "C5626")
c("C26", "100n", "+3V3", "GND"); r("R25", "10k", "EXP_INT", "+3V3")
for i in range(5): part("TP%d" % (6 + i), "Connector", "TestPoint", "EXP_SPARE%d" % i, "TP", {"1": "EXP_SPARE%d" % i})
part("TP17", "Connector", "TestPoint", "EXP_SPARE6", "TP", {"1": "EXP_SPARE6"})
# --- RockBLOCK site
part("JP3", "Jumper", "SolderJumper_3_Open", "UART TX select: A=UART2 (BCM4) B=UART0 (BCM14)", "JP3", {"1": "UART2_TX", "3": "UART0_TX", "2": "UART_TX_M"})
part("JP4", "Jumper", "SolderJumper_3_Open", "UART RX select: A=UART2 (BCM5) B=UART0 (BCM15)", "JP3", {"1": "UART2_RX", "3": "UART0_RX", "2": "UART_RX_M"})
part("J_RB9704", "Connector_Generic", "Conn_02x08_Odd_Even", "RockBLOCK 9704 16-pin (IDC 2x8)", "IDC16", {
 "1": "GND", "2": "NC", "3": "RB_IEN", "4": "GND", "5": "NC", "6": "RB_CTRL", "7": "RB_STATUS", "8": "RB_XMTG", "9": "NC", "10": "GND", "11": "NC", "12": "NC",
 "13": "UART_RX_M", "14": "UART_TX_M", "15": "5V_RB", "16": "GND"})
part("J_RB9603", "Connector_Generic", "Conn_01x10", "RockBLOCK 9603 PicoBlade 10", "PICO10", {
 "1": "UART_RX_M", "2": "NC", "3": "NC", "4": "RB_NETAV", "5": "RB_STATUS", "6": "UART_TX_M", "7": "RB_ONOFF", "8": "5V_RB", "9": "NC", "10": "GND"})
part("Q1", "Transistor_FET", "2N7000", "2N7002 (SOT-23) OnOff open-drain buffer", "SOT23", {"2": "Q1_G", "3": "RB_ONOFF", "1": "GND"})
r("R26", "100R", "RB_CTRL", "Q1_G"); r("R27", "100k", "Q1_G", "GND"); r("R28", "10k", "RB_STATUS", "+3V3")
# --- DCF77, interconnect
part("J_DCF77", "Connector_Generic", "Conn_01x04", "DCF77 remote (XH2.5): 3V3 GND T P1", "XH4", {"1": "+3V3", "2": "GND", "3": "DCF_T", "4": "DCF_PON"}); r("R29", "10k", "DCF_T", "+3V3")
part("J_AB1", "Connector_Generic", "Conn_02x07_Odd_Even", "A-B interconnect (IDC 2x7, underside)", "IDC14", {
 "1": "PI_SHDN_REQ", "2": "PI_KILL", "3": "GND", "4": "USB_A_P", "5": "USB_A_N", "6": "GND", "7": "SDA", "8": "SCL", "9": "EXP_INT", "10": "TR_APRS", "11": "VBUS_A_SENSE", "12": "AB_SPARE", "13": "GND", "14": "TX_INHIBIT_n"})   # B12: 1 = shutdown request from PCB-A (LTC2954 INT), 2 = Pi KILL to PCB-A, no 5 V on the ribbon

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
SECTIONS = [("POWER INPUT, RAILS, TEST POINTS", ["J_5V_M1", "J_5V_M2", "J_5V_PI", "D1", "C1", "C2", "D3", "C40", "C41", "D4", "C42", "R1", "LED1", "J_TD2", "TP1", "TP2", "TP3", "TP4", "TP5", "TP11", "TP12", "TP13", "TP14", "TP15", "TP16", "TP17", "#FLG01", "#FLG02", "#FLG03", "#FLG04", "#FLG05", "#FLG06", "#FLG07", "#FLG08", "#FLG09", "#FLG10", "#FLG11", "#FLG12", "#FLG13"]),
            ("Pi 5 GPIO RIBBON", ["J_GPIO1"]),
            ("USB 2.0 HUB FE1.1s + UPSTREAM PORTS", ["U1", "Y1", "C3", "C4", "R2", "C5", "C6", "C7", "C8", "C9", "C10", "R3", "C11", "R4", "JP1", "R5", "R6", "R7", "R8", "LED2", "J_USB_UP1", "R9", "R10", "U2", "J_USB_UP2", "R11", "R12", "U3"]),
            ("CH1 SDR BAY: RTL-SDR V4 or LimeSDR Mini 2.0  (0x40)", ["U4", "R13", "R30", "C33", "R14", "U5", "C12", "C13", "J_RTL1", "U6"]),
            ("CH2 ZIGBEE  (0x41)", ["U7", "R15", "R31", "C34", "R16", "U8", "C14", "C15", "J_ZB1", "U9"]),
            ("CH3 LoRa: XIAO Wio-SX1262 or T-BEAM 1W  (0x45, 2A)", ["F4", "U10", "C27", "C29", "R32", "R17", "R18", "U11", "C16", "C17", "J_XIAO1", "J_TBEAM1", "U12"]),
            ("CH4 ROCKBLOCK 5V  (0x42, 2A)", ["F5", "U13", "C28", "C30", "R33", "R20", "R21", "U14", "C18", "C19"]),
            ("CH5 T-CALL LTE  (0x44, 2A)", ["F2", "U15", "C20", "C31", "R34", "R22", "U16", "C21", "C22", "J_TCALL1", "U17"]),
            ("I2C EXPANDER PCA9555 (0x20): EN + FAULT", ["U20", "C26", "R25", "TP6", "TP7", "TP8", "TP9", "TP10"]),
            ("ROCKBLOCK SITE: UART SELECT, 9704 + 9603 CONNECTORS, OnOff BUFFER", ["JP3", "JP4", "J_RB9704", "J_RB9603", "Q1", "R26", "R27", "R28"]),
            ("PANEL RIBBON (PCB-C CONTROL PANEL)", ["F6", "J_PANEL"]),
            ("DCF77 + A-B INTERCONNECT", ["J_DCF77", "R29", "J_AB1"])]
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
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-B COMPUTE") (date "2026-09-02") (rev "A") (company "MeshSat") (comment 1 "Phase B2 schematic (B12: no X1202, three rails from PCB-A), generated by tools/gen_sch_b.py. Netlist style: every pin carries a stub and a net label.") (comment 2 "MESHSAT-709. B11: +5V from the PCB-A module-rail boost over J_5V_MOD (VH); the X1202 XH output is only a sense line (X1202_5V to J_AB1.12) that enables that boost. FE1.1s hub on internal regulators; TPS2065C x2 + TPS22810 x4 switches (B4: LoRa and RockBLOCK channels at 2 A for the T-Beam 1W and 9704 bursts); INA219 per channel; PCA9555 EN/FAULT; both Pi UARTs to the RockBLOCK site via JP3/JP4."))\n'
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
