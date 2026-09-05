#!/usr/bin/env python3
"""PCB-B COMPUTE, phase B13: generate the KiCad 9 schematic (netlist-style: every pin gets a
stub and a net label; power pins get power symbols). Runs on the laptop (needs the KiCad libs).
Usage: gen_sch_b.py <out.kicad_sch> <project-name>

B13 (appendix 32.35, MESHSAT-795): a Raspberry Pi Compute Module 5 on two Amphenol 10164227
board-to-board connectors replaces the Pi 5 on standoffs. No USB socket, plug or cable sits between
the compute and the kit: the module's 5 V comes from the J_5V_PI rail, its USB 2.0 pairs feed a
USB2517I hub (SDR bay, wall port over the ribbon) and the LTE mini PCIe socket, the display is a
22-pin FPC on MIPI0, GNSS is a u-blox NEO-M9N on I2C with its timepulse on a GPIO, LoRa a Seeed
Wio-SX1262 on SPI0, ZigBee an Ebyte E72-2G4M20S1E (CC2652P, ZNP) on UART1, the RockBLOCK site and
the panel ribbon stay, I2S goes to the mezzanine codec over J_AB1 (2x9). The T-Call, XIAO, T-Beam,
ZigBee dongle, GPS puck and WiFi dongle leave the kit. Every 3.3 V load on this board runs from a
buck that is enabled by the module's own 3.3 V, so nothing back-feeds a module pin while it is off
(CM5 datasheet section 4.2.1); the two power-control lines to PCB-A and the TX mirror from PCB-D
cross that boundary through 2N7002 level stages, the kit I2C through a TCA9517A buffer.
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

# ----------------------------------------------------------------- synthetic symbols (parts with more pins than any library connector symbol)
# The CM5 has 200 pins. A box symbol is generated here with the datasheet pin names (Table 4 of the CM5 datasheet,
# release 3, vendor/cm5/); odd pins on the left, even pins on the right, 2.54 mm pitch, like a connector symbol.
CM5_PINS = {1:"GND",2:"GND",3:"Ethernet_Pair3_P",4:"Ethernet_Pair1_P",5:"Ethernet_Pair3_N",6:"Ethernet_Pair1_N",7:"GND",8:"GND",9:"Ethernet_Pair2_N",10:"Ethernet_Pair0_N",11:"Ethernet_Pair2_P",12:"Ethernet_Pair0_P",13:"GND",14:"GND",15:"Ethernet_nLED3",16:"Fan_Tacho",17:"Ethernet_nLED2",18:"Ethernet_SYNC_OUT",19:"Fan_PWM",20:"EEPROM_nWP",21:"LED_nACT",22:"GND",23:"GND",24:"GPIO26",25:"GPIO21",26:"GPIO19",27:"GPIO20",28:"GPIO13",29:"GPIO16",30:"GPIO6",31:"GPIO12",32:"GND",33:"GND",34:"GPIO5",35:"ID_SC",36:"ID_SD",37:"GPIO7",38:"GPIO11",39:"GPIO8",40:"GPIO9",41:"GPIO25",42:"GND",43:"GND",44:"GPIO10",45:"GPIO24",46:"GPIO22",47:"GPIO23",48:"GPIO27",49:"GPIO18",50:"GPIO17",51:"GPIO15",52:"GND",53:"GND",54:"GPIO4",55:"GPIO14",56:"GPIO3",57:"SD_CLK",58:"GPIO2",59:"GND",60:"GND",61:"SD_DAT3",62:"SD_CMD",63:"SD_DAT0",64:"SD_DAT5",65:"GND",66:"GND",67:"SD_DAT1",68:"SD_DAT4",69:"SD_DAT2",70:"SD_DAT7",71:"GND",72:"SD_DAT6",73:"SD_VDD_OVERRIDE",74:"GND",75:"SD_PWR_ON",76:"VBAT",77:"5V",78:"GPIO_VREF",79:"5V",80:"SCL0",81:"5V",82:"SDA0",83:"5V",84:"CM5_3.3V",85:"5V",86:"CM5_3.3V",87:"5V",88:"CM5_1.8V",89:"WL_nDisable",90:"CM5_1.8V",91:"BT_nDisable",92:"PWR_Button",93:"nRPIBOOT",94:"CC1",95:"LED_nPWR",96:"CC2",97:"CAM_GPIO0",98:"GND",99:"PMIC_Enable",100:"CAM_GPIO1",101:"USB_OTG_ID",102:"PCIe_CLK_nREQ",103:"USB_N",104:"PCIE_nWAKE",105:"USB_P",106:"PCIE_PWR_EN",107:"GND",108:"GND",109:"PCIe_nRST",110:"PCIe_CLK_P",111:"VBUS_EN",112:"PCIe_CLK_N",113:"GND",114:"GND",115:"MIPI0_D0_N",116:"PCIe_RX_P",117:"MIPI0_D0_P",118:"PCIe_RX_N",119:"GND",120:"GND",121:"MIPI0_D1_N",122:"PCIe_TX_P",123:"MIPI0_D1_P",124:"PCIe_TX_N",125:"GND",126:"GND",127:"MIPI0_C_N",128:"USB3-0-RX_N",129:"MIPI0_C_P",130:"USB3-0-RX_P",131:"GND",132:"GND",133:"MIPI0_D2_N",134:"USB3-0-DP",135:"MIPI0_D2_P",136:"USB3-0-DM",137:"GND",138:"GND",139:"MIPI0_D3_N",140:"USB3-0-TX_N",141:"MIPI0_D3_P",142:"USB3-0-TX_P",143:"HDMI1_HOTPLUG",144:"GND",145:"HDMI1_SDA",146:"HDMI1_TX2_P",147:"HDMI1_SCL",148:"HDMI1_TX2_N",149:"HDMI1_CEC",150:"GND",151:"HDMI0_CEC",152:"HDMI1_TX1_P",153:"HDMI0_HOTPLUG",154:"HDMI1_TX1_N",155:"GND",156:"GND",157:"USB3-1-RX_N",158:"HDMI1_TX0_P",159:"USB3-1-RX_P",160:"HDMI1_TX0_N",161:"GND",162:"GND",163:"USB3-1-DP",164:"HDMI1_CLK_P",165:"USB3-1-DM",166:"HDMI1_CLK_N",167:"GND",168:"GND",169:"USB3-1-TX_N",170:"HDMI0_TX2_P",171:"USB3-1-TX_P",172:"HDMI0_TX2_N",173:"GND",174:"GND",175:"MIPI1_D0_N",176:"HDMI0_TX1_P",177:"MIPI1_D0_P",178:"HDMI0_TX1_N",179:"GND",180:"GND",181:"MIPI1_D1_N",182:"HDMI0_TX0_P",183:"MIPI1_D1_P",184:"HDMI0_TX0_N",185:"GND",186:"GND",187:"MIPI1_C_N",188:"HDMI0_CLK_P",189:"MIPI1_C_P",190:"HDMI0_CLK_N",191:"GND",192:"GND",193:"MIPI1_D2_N",194:"MIPI1_D3_N",195:"MIPI1_D2_P",196:"MIPI1_D3_P",197:"GND",198:"GND",199:"HDMI0_SDA",200:"HDMI0_SCL"}
SYNTH = {"CM5A": {k: v for k, v in CM5_PINS.items() if k <= 100}, "CM5B": {k: v for k, v in CM5_PINS.items() if k > 100}}   # one part per receptacle: JLC places two connectors
def synth_symbol(lib, name):
    pins = SYNTH[name]; n = len(pins); rows = (n + 1) // 2; first = min(pins)
    W = 25.4; H = rows * 2.54 + 2.54
    fx = lambda: ["effects", ["font", ["size", "1.27", "1.27"]]]
    sym = ["symbol", q(lib + ":" + name), ["pin_names", ["offset", "1.016"]], ["exclude_from_sim", "no"], ["in_bom", "yes"], ["on_board", "yes"],
           ["property", q("Reference"), q("U"), ["at", "0", "%.2f" % (H / 2 + 1.27), "0"], fx()],
           ["property", q("Value"), q(name), ["at", "0", "%.2f" % (-H / 2 - 1.27), "0"], fx()],
           ["property", q("Footprint"), q(""), ["at", "0", "0", "0"], ["effects", ["font", ["size", "1.27", "1.27"]], ["hide", "yes"]]],
           ["property", q("Datasheet"), q(""), ["at", "0", "0", "0"], ["effects", ["font", ["size", "1.27", "1.27"]], ["hide", "yes"]]]]
    body = ["symbol", q(name + "_0_1"), ["rectangle", ["start", "%.2f" % (-W / 2), "%.2f" % (H / 2)], ["end", "%.2f" % (W / 2), "%.2f" % (-H / 2)],
            ["stroke", ["width", "0.254"], ["type", "default"]], ["fill", ["type", "background"]]]]
    unit = ["symbol", q(name + "_1_1")]
    for num in sorted(pins):
        row = (num - first) // 2; y = H / 2 - 2.54 * (row + 1)
        if num % 2 == 1: at = ["at", "%.2f" % (-W / 2 - 2.54), "%.2f" % y, "0"]
        else: at = ["at", "%.2f" % (W / 2 + 2.54), "%.2f" % y, "180"]
        unit.append(["pin", "passive", "line", at, ["length", "2.54"], ["name", q(pins[num]), fx()], ["number", q(str(num)), fx()]])
    sym.append(body); sym.append(unit); return sym

# ----------------------------------------------------------------- the design
FP = {
 "R": "Resistor_SMD:R_0603_1608Metric", "RS": "Resistor_SMD:R_1206_3216Metric", "C": "Capacitor_SMD:C_0603_1608Metric", "C0402": "Capacitor_SMD:C_0402_1005Metric",
 "C10u": "Capacitor_SMD:C_0805_2012Metric", "C100u": "Capacitor_SMD:C_1206_3216Metric", "C1210": "Capacitor_SMD:C_1210_3225Metric", "LED": "LED_SMD:LED_0603_1608Metric",
 "TVS": "Diode_SMD:D_SMB", "F1812": "Fuse:Fuse_1812_4532Metric", "F2920": "Fuse:Fuse_2920_7451Metric",
 "QFN64": "Package_DFN_QFN:QFN-64-1EP_9x9mm_P0.5mm_EP4.7x4.7mm", "EXP": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", "MSOP8": "Package_SO:MSOP-8_3x3mm_P0.65mm",
 "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "SOT235": "Package_TO_SOT_SMD:SOT-23-5", "SOT238": "Package_TO_SOT_SMD:SOT-23-8", "SOT23": "Package_TO_SOT_SMD:SOT-23",
 "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", "L4020": "Inductor_SMD:L_Coilcraft_XAL4020-XXX", "L0402": "Inductor_SMD:L_0402_1005Metric",
 "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "XH4": "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical",
 "SH4": "Connector_JST:JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical",
 "IDC16": "Connector_IDC:IDC-Header_2x08_P2.54mm_Vertical", "IDC18": "Connector_IDC:IDC-Header_2x09_P2.54mm_Vertical", "IDC20": "Connector_IDC:IDC-Header_2x10_P2.54mm_Vertical",
 "PICO10": "Connector_Molex:Molex_PicoBlade_53047-1010_1x10_P1.25mm_Vertical",
 "PH1x2": "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", "PH1x3": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", "PH1x5": "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
 "USBA": "Connector_USB:USB_A_Stewart_SS-52100-001_Horizontal", "USBC": "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
 "JP2": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "JP3": "Jumper:SolderJumper-3_P1.3mm_Open_RoundedPad1.0x1.5mm",
 "TP": "TestPoint:TestPoint_Pad_D1.5mm",
 # B13 sites
 "CM5A": "meshsat:CM5_Conn_A_10164227", "CM5B": "meshsat:CM5_Conn_B_10164227",   # the two 100-pin Amphenol 10164227 receptacles of the module site (CM5IO design files); holes and outline by gen_pcb_b.py
 "FPC22": "meshsat:Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal",      # Touch Display 2 FPC, 22-pin 0.5 mm (CM5IO design files)
 "MPCIE": "meshsat:MiniPCIe_Socket_52P_H4.0_Standoff",
 "M2E": "meshsat:M2_E-Key_Socket_2230",                                      # M.2 E-key socket, 2230 card, plated M2.5 standoff hole 28.25 mm from the datum (B14)
 "NANOSIM": "Connector_Card:nanoSIM_GCT_SIM8060-6-0-14-00",
 "NEO": "RF_GPS:ublox_NEO", "WIO": "meshsat:Seeed_Wio-SX1262", "E72": "meshsat:Ebyte_E72-2G4M20S1E",
 "UFL": "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical", "CR2032": "Battery:BatteryHolder_Keystone_3034_1x20mm",
}
P = []   # (ref, lib, symbol, value, footprint, nets{pin: net}, lcsc)
def part(ref, lib, sym, value, fp, nets, lcsc=""):
    P.append(dict(ref=ref, lib=lib, sym=sym, value=value, fp=FP.get(fp, fp), nets=nets, lcsc=lcsc))
def usb_c_recept(ref, dp, dm, vbus, cc1, cc2):
    part(ref, "Connector", "USB_C_Receptacle_USB2.0_16P", "USB-C 2.0 receptacle", "USBC",
         {"A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "A4": vbus, "A9": vbus, "B4": vbus, "B9": vbus,
          "A5": cc1, "B5": cc2, "A6": dp, "B6": dp, "A7": dm, "B7": dm, "A8": "NC", "B8": "NC", "S1": "GND"}, "C165948")
def esd(ref, dp, dm, vbus):
    part(ref, "Power_Protection", "USBLC6-2SC6", "USBLC6-2SC6", "SOT236", {"1": dp, "6": dp, "3": dm, "4": dm, "5": vbus, "2": "GND"}, "C7519")
def r(ref, val, a, b, fp="R", lcsc=""): part(ref, "Device", "R", val, fp, {"1": a, "2": b}, lcsc)
def c(ref, val, a, b, fp="C", lcsc=""): part(ref, "Device", "C", val, fp, {"1": a, "2": b}, lcsc)
def tps2065(ref, en, out, flt, rail="+5V_M1"): part(ref, "Power_Management", "TPS2065CDBV", "TPS2065CDBV", "SOT235", {"5": rail, "4": en, "1": out, "3": flt, "2": "GND"})
def ina219(ref, inp, inn, a0, a1): part(ref, "Sensor_Energy", "INA219AxDCN", "INA219AIDCN", "SOT238", {"1": inp, "2": inn, "3": "GND", "4": "+3V3", "5": "SCL", "6": "SDA", "7": a0, "8": a1}, "C138024")
def nfet(ref, gate, source, drain, value="2N7002"):
    # KiCad's 2N7002 symbol is numbered for the SOT-23 part: 1 = G, 2 = S, 3 = D (the 2N7000 symbol is the TO-92 order S G D
    # and must never be put on a SOT-23 land: appendix 32.36)
    part(ref, "Transistor_FET", "2N7002", value, "SOT23", {"1": gate, "2": source, "3": drain}, "C8545")
def level_in(ref, rn, far, cm):
    """One line from the always-on domain of PCB-A/D into a module GPIO: 2N7002 with gate on the module's 3.3 V, source on the
    module side (10k pull-up to +3V3_CM), drain on the far side. Module off: gate 0, body diode reverse, nothing flows."""
    nfet(ref, "+3V3_CM", cm, far); r(rn, "10k", cm, "+3V3_CM")
def buck(ref, ln, cb, cin, co1, co2, r1, r2, vin, en, out, sw, fb, bst, note):
    # TPS563201 3 A synchronous buck, the A19 recipe (tps563201.pdf; C116592): 3.3 uH XAL4020, 2 x 22 uF out, 33.2k/10k for 3.32 V
    part(ref, "Regulator_Switching", "TPS563201", "TPS563201 " + note, "SOT236", {"1": "GND", "2": sw, "3": vin, "4": fb, "5": en, "6": bst})
    part(ln, "Device", "L", "3.3uH XAL4020-332MEB", "L4020", {"1": sw, "2": out}); c(cb, "100n", bst, sw); c(cin, "10u", vin, "GND", "C10u")
    c(co1, "22u 10V X7R 1210", out, "GND", "C1210"); c(co2, "22u 10V X7R 1210", out, "GND", "C1210")
    r(r1, "33.2k 1%", out, fb); r(r2, "10k 1%", fb, "GND")   # 0.768 V x (1 + 33.2/10) = 3.32 V

# --- power input: three rails from PCB-A over JST-VH leads (B12 topology kept): M1 hub, display, panel, LTE; M2 SDR; PI the module alone
part("J_5V_M1", "Connector_Generic", "Conn_01x02", "5 V rail M1 from PCB-A J_5V_M1 (JST-VH, 18 AWG): + - ; hub, display, panel, LTE socket, 3.3 V buck", "VH2", {"1": "+5V_M1", "2": "GND"})
part("J_5V_M2", "Connector_Generic", "Conn_01x02", "5 V rail M2 from PCB-A J_5V_M2 (JST-VH, 18 AWG): + - ; SDR channel, RockBLOCK channel", "VH2", {"1": "+5V_M2", "2": "GND"})
part("J_5V_PI", "Connector_Generic", "Conn_01x02", "Pi rail 5.1 V 5 A from PCB-A J_5V_PI (JST-VH, 18 AWG): + - ; the CM5 5 V pins and the fan, no plug", "VH2", {"1": "+5V_PI", "2": "GND"})
part("D1", "Device", "D_TVS", "SMBJ5.0A", "TVS", {"1": "+5V_M1", "2": "GND"}); c("C1", "100u 10V", "+5V_M1", "GND", "C100u"); c("C2", "100u 10V", "+5V_M1", "GND", "C100u")
part("D3", "Device", "D_TVS", "SMBJ5.0A", "TVS", {"1": "+5V_M2", "2": "GND"}); c("C40", "100u 10V", "+5V_M2", "GND", "C100u"); c("C41", "100u 10V", "+5V_M2", "GND", "C100u")
part("D4", "Device", "D_TVS", "SMBJ5.0A", "TVS", {"1": "+5V_PI", "2": "GND"}); c("C42", "100u 10V", "+5V_PI", "GND", "C100u")
c("C43", "100u 10V", "+5V_PI", "GND", "C100u"); c("C44", "100u 10V", "+5V_PI", "GND", "C100u")   # at the module's six 5 V pins (design point 2.5 A, datasheet B.3)
for k in (45, 46, 47, 48): c("C%d" % k, "10u", "+5V_PI", "GND", "C10u")
r("R1", "1k", "+5V_M1", "LED_5V_A"); part("LED1", "Device", "LED", "green 5V", "LED", {"2": "LED_5V_A", "1": "GND"})
part("J_TD2", "Connector_Generic", "Conn_01x02", "Touch Display 2 5V (XH2.54)", "XH2", {"1": "+5V_M1", "2": "GND"})
for i, net in enumerate(("+5V_M1", "GND", "+3V3", "SDA", "SCL", "TX_INHIBIT_n", "PI_KILL", "+5V_M2", "+5V_PI", "+3V3_CM", "+1V8_CM", "VBUS_EN", "PMIC_EN", "PWR_BUT", "GNSS_PPS", "GNSS_TXD", "I2S_BCLK", "I2S_LRCLK", "VBUS_FLASH", "SDA_CM", "SCL_CM", "+3V3_LTE", "EXP_INT"), 1):
    part("TP%d" % i, "Connector", "TestPoint", net, "TP", {"1": net})
for i, net in enumerate(("+5V_M1", "+5V_M2", "+5V_PI", "+3V3", "GND", "5V_RTL", "+3V3_CM", "+1V8_CM", "+3V3_LTE", "VBAT", "RB_FUSED", "5V_LTE_IN", "+3V3_AB", "SIM_VCC", "5V_RB", "+3V3_WIFI", "5V_WIFI_IN"), 1):
    part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})

# --- 3.3 V rails: U31 board logic and radios, enabled by the module's own 3.3 V so the rail follows the module (no back-feed when it is off);
#     U32 the LTE socket alone (EG25-G bursts 2 A at 3.3 V), enabled by the expander bit EN_LTE
buck("U31", "L31", "C31", "C32", "C33", "C34", "R35", "R36", "+5V_M1", "EN33", "+3V3", "SW33", "FB33", "BST33", "3.3 V buck from M1 for the board (follows the CM5 3.3 V)")
r("R37", "100k", "+3V3_CM", "EN33"); r("R38", "100k", "EN33", "GND")   # EN = 1.65 V when CM5_3.3V is up, 0 V when the module is off
r("R41", "0.05R 1% 1206", "+5V_M1", "5V_LTE_IN", "RS"); ina219("U33", "+5V_M1", "5V_LTE_IN", "GND", "+3V3")   # 0x44, the B12 LTE address
buck("U32", "L32", "C35", "C36", "C37", "C38", "R39", "R40", "5V_LTE_IN", "EN_LTE", "+3V3_LTE", "SW_LTE", "FB_LTE", "BST_LTE", "3.3 V buck for the LTE socket (EN_LTE)")
r("R42", "100k", "EN_LTE", "GND")
c("C50", "100u 6.3V", "+3V3_LTE", "GND", "C100u"); c("C51", "100n", "+3V3_LTE", "GND"); c("C52", "33p", "+3V3_LTE", "GND", "C0402"); c("C53", "10p", "+3V3_LTE", "GND", "C0402")   # Quectel EG25-G mini PCIe HD 3.3: bulk + RF decoupling at the socket
#     U36 the M.2 WiFi socket (B14, appendix 32.37: AsiaRF AW7915-AED, 3.3 V at up to 3 A, 9 W maximum), on the Pi rail (owner ruling 5 Sep 06:00: the
#     5.1 V 5 A converter carries the module's 2.5 A design point plus the card's 2.0 A worst case; M2 would have been left with 10 percent margin) through
#     its own shunt and INA219 (0x45), enabled by the module's PCIE_PWR_EN output (3.3 V, active high) so the card rail follows the module and its PCIe link state
r("R72", "0.05R 1% 1206", "+5V_PI", "5V_WIFI_IN", "RS"); ina219("U35", "+5V_PI", "5V_WIFI_IN", "+3V3", "+3V3")   # A0 = A1 = VS: 0x45
buck("U36", "L36", "C67", "C68", "C69", "C70", "R73", "R74", "5V_WIFI_IN", "PCIE_PWR_EN", "+3V3_WIFI", "SW_WIFI", "FB_WIFI", "BST_WIFI", "3.3 V buck for the M.2 WiFi socket (PCIE_PWR_EN)")
r("R75", "100k", "PCIE_PWR_EN", "GND")
c("C71", "100u 6.3V", "+3V3_WIFI", "GND", "C100u"); c("C72", "100n", "+3V3_WIFI", "GND")   # bulk at the socket's four 3.3 V pins
c("C49", "10u", "+3V3_CM", "GND", "C10u"); c("C39", "100n", "+3V3_CM", "GND")

# --- the Compute Module 5 (U30): pin functions per Table 4 of the datasheet; GPIO map per appendix 32.35 (I2S on 18 to 21, SPI0 for the e-paper and LoRa,
#     UART0 console, UART1 ZigBee, UART2 RockBLOCK, PWM0 on 12/13, the kit I2C on 2/3 behind U34, the display I2C on the dedicated SDA0/SCL0)
GPIO = {0: "UART1_TX", 1: "UART1_RX", 2: "SDA_CM", 3: "SCL_CM", 4: "UART2_TX", 5: "UART2_RX", 6: "PI_SHDN_REQ_CM", 7: "LORA_NSS", 8: "SPI_CE0", 9: "SPI_MISO",
        10: "SPI_MOSI", 11: "SPI_SCLK", 12: "PANEL_PWM", 13: "PWM1", 14: "UART0_TX", 15: "UART0_RX", 16: "EPD_DC", 17: "PI_KILL_CM", 18: "I2S_BCLK", 19: "I2S_LRCLK",
        20: "I2S_DIN", 21: "I2S_DOUT", 22: "GNSS_PPS", 23: "LORA_BUSY", 24: "LORA_DIO1", 25: "EXP_INT", 26: "LORA_NRST", 27: "TR_APRS_CM"}
CM5 = {}
for n, nm in CM5_PINS.items():
    if nm == "GND": CM5[n] = "GND"
    elif nm == "5V": CM5[n] = "+5V_PI"
    elif nm == "CM5_3.3V": CM5[n] = "+3V3_CM"
    elif nm == "CM5_1.8V": CM5[n] = "+1V8_CM"
    elif nm.startswith("GPIO") and nm[4:].isdigit(): CM5[n] = GPIO[int(nm[4:])]
    elif nm.startswith("MIPI0_"): CM5[n] = "DSI0_" + nm[6:]
    else: CM5[n] = "NC"          # Ethernet, HDMI, PCIe, USB 3.0 super-speed, MIPI1, SD (eMMC variant), CC
CM5.update({36: GPIO[0], 35: GPIO[1], 16: "FAN_TACHO", 19: "FAN_PWM", 20: "EEPROM_nWP", 21: "LED_nACT", 76: "VBAT", 78: "+3V3_CM", 80: "DISP_SCL", 82: "DISP_SDA",
            89: "WL_nDIS", 91: "BT_nDIS", 92: "PWR_BUT", 93: "nRPIBOOT", 95: "LED_nPWR", 97: "CAM_GPIO0", 99: "PMIC_EN", 103: "USB_OTG_N", 105: "USB_OTG_P",
            111: "VBUS_EN", 134: "USB_UP_P", 136: "USB_UP_N", 163: "USB_LTE_P", 165: "USB_LTE_N",
            # B14: the PCIe Gen 2 x1 lane and its control lines to the M.2 socket J_WIFI1 (everything not listed here falls back to NC above)
            102: "PCIe_CLK_nREQ", 104: "PCIE_nWAKE", 106: "PCIE_PWR_EN", 109: "PCIe_nRST", 110: "PCIe_CLK_P", 112: "PCIe_CLK_N", 116: "PCIe_RX_P", 118: "PCIe_RX_N", 122: "PCIe_TX_P", 124: "PCIe_TX_N"})
part("U30A", "Connector_Generic", "CM5A", "Amphenol 10164227-1004A1RLF receptacle A (CM5 pins 1-100, GPIO side); module CM5108064 8 GB 64 GB eMMC wireless, bench-fitted", "CM5A", {str(k): v for k, v in CM5.items() if k <= 100}, "C7435219")
part("U30B", "Connector_Generic", "CM5B", "Amphenol 10164227-1004A1RLF receptacle B (CM5 pins 101-200, high-speed side)", "CM5B", {str(k): v for k, v in CM5.items() if k > 100}, "C7435219")
# module support: RTC cell (shared with the GNSS backup pin), LEDs, fan, flashing port, bench headers
part("BT1", "Device", "Battery_Cell", "CR2032 holder Keystone 3034 (VBAT, also the NEO-M9N V_BCKP)", "CR2032", {"1": "VBAT", "2": "GND"})
r("R46", "1k", "+3V3_CM", "LED_ACT_A"); part("LED5", "Device", "LED", "green ACT (LED_nACT sinks)", "LED", {"2": "LED_ACT_A", "1": "LED_nACT"})
part("Q2", "Transistor_BJT", "BC857", "BC857: LED_nPWR must be buffered (datasheet Table 4)", "SOT23", {"1": "Q2_B", "2": "+3V3_CM", "3": "Q2_C"})
r("R47", "10k", "LED_nPWR", "Q2_B"); r("R48", "1k", "Q2_C", "LED_PWR_A"); part("LED6", "Device", "LED", "red PWR", "LED", {"2": "LED_PWR_A", "1": "GND"})
part("J_FAN", "Connector_Generic", "Conn_01x04", "CM5 cooler fan (JST-SH 1.0): 5V GND TACHO PWM; 5 V from the Pi rail so the fan stops with the module", "SH4", {"1": "+5V_PI", "2": "GND", "3": "FAN_TACHO", "4": "FAN_PWM"})
r("R49", "10k", "FAN_PWM", "+3V3_CM")   # Fan_PWM is an open-drain output
usb_c_recept("J_FLASH", "USB_OTG_P", "USB_OTG_N", "VBUS_FLASH", "CC1_F", "CC2_F"); r("R50", "5.1k", "CC1_F", "GND"); r("R51", "5.1k", "CC2_F", "GND"); esd("U9", "USB_OTG_P", "USB_OTG_N", "VBUS_FLASH")
part("J_RPIBOOT", "Connector_Generic", "Conn_01x02", "nRPIBOOT jumper: fit to flash the eMMC over J_FLASH with rpiboot", "PH1x2", {"1": "nRPIBOOT", "2": "GND"})
part("J_WP", "Connector_Generic", "Conn_01x02", "EEPROM_nWP jumper: fit to write-protect the bootloader EEPROM", "PH1x2", {"1": "EEPROM_nWP", "2": "GND"})
part("J_PMIC", "Connector_Generic", "Conn_01x02", "PMIC_Enable: short to force the module off (bench)", "PH1x2", {"1": "PMIC_EN", "2": "GND"})
part("J_PWRBTN", "Connector_Generic", "Conn_01x02", "PWR_Button: momentary to GND wakes the module from soft-off (bench)", "PH1x2", {"1": "PWR_BUT", "2": "GND"})
part("J_DBG", "Connector_Generic", "Conn_01x03", "console UART0 (GPIO14/15, 3.3 V): GND TX RX", "PH1x3", {"1": "GND", "2": "UART0_TX", "3": "UART0_RX"})
# --- the always-on domain boundary: PCB-A's LTC2954 lines and PCB-D's TX mirror through 2N7002 stages, the kit I2C through a TCA9517A
level_in("Q3", "R52", "PI_SHDN_REQ", "PI_SHDN_REQ_CM")   # LTC2954 INT (open drain, 100k to A's 3.3 V) -> GPIO6
level_in("Q4", "R53", "PI_KILL", "PI_KILL_CM")           # GPIO17 -> A's Q5 gate (100k to GND on A): module high pulls nothing, low pulls the far side low; A19 semantics inverted on A20 (32.36)
level_in("Q5", "R54", "TR_APRS", "TR_APRS_CM"); r("R55", "4.7k", "TR_APRS", "GND")   # D5 Q4 sources 3.3 V through 100R when PTT is active; the pull-down defines idle
part("U34", "Logic_LevelTranslator", "TCA9517ADGK", "TCA9517A I2C buffer: A = module (GPIO2/3, +3V3_CM), B = kit bus to PCB-A and PCB-C, EN from the module rail", "MSOP8",
     {"1": "GND", "2": "SDA_CM", "3": "SCL_CM", "4": "+3V3_CM", "5": "EN_I2C", "6": "SCL", "7": "SDA", "8": "+3V3"})   # LCSC code matched at order time
r("R56", "10k", "EN_I2C", "+3V3_CM"); c("C54", "100n", "+3V3_CM", "GND"); c("C55", "100n", "+3V3", "GND")
r("R57", "2.2k", "SDA", "+3V3"); r("R58", "2.2k", "SCL", "+3V3")   # kit-bus pull-ups on the B side (A19 and C5 carry none of their own on the shared bus)
r("R25", "10k", "EXP_INT", "+3V3")   # open-drain interrupt line shared by U20, U21 and the expanders on A and C

# --- USB 2.0 hub USB2517I on the module's USB3-0 pair (the A19 block, ports: 1 SDR bay, 2 wall port over J_AB1; 3 to 5 unused, 6 and 7 disabled by straps)
part("U1", "Connector_Generic", "Conn_02x33_Odd_Even", "USB2517I-JZX seven-port USB 2.0 hub (strap defaults, ports 6-7 disabled)", "QFN64", {
 "1": "USB_RTL_N", "2": "USB_RTL_P", "3": "USB_WALL_N", "4": "USB_WALL_P", "5": "+3V3", "6": "NC", "7": "NC", "8": "NC", "9": "NC", "10": "+3V3",
 "11": "NC", "12": "NC", "13": "GND", "14": "NC", "15": "NC", "16": "NC", "17": "NC", "18": "NC", "19": "GND", "20": "NC", "21": "+3V3", "22": "+3V3", "23": "NC", "24": "+3V3", "25": "HUB_VD18",
 "26": "NC", "27": "+3V3", "28": "FLT_RTL", "29": "NC", "30": "NC", "31": "NC", "32": "NC", "33": "NC", "34": "NC", "35": "+3V3", "36": "NC", "37": "NC", "38": "NC", "39": "NC", "40": "NC", "41": "HUB_CFG0", "42": "HUB_CFG1", "43": "+3V3", "44": "+3V3", "45": "NC",
 "46": "+3V3", "47": "NC", "48": "NC", "49": "NC", "50": "NC", "51": "NC", "52": "+3V3", "53": "HUB_DIS6M", "54": "HUB_DIS6P", "55": "HUB_DIS7M", "56": "HUB_DIS7P", "57": "+3V3", "58": "USB_UP_N", "59": "USB_UP_P", "60": "XOUT", "61": "XIN", "62": "HUB_VD18PLL", "63": "HUB_RBIAS", "64": "+3V3", "65": "GND", "66": "NC"}, "C1521556")
part("Y1", "Device", "Crystal_GND24", "24 MHz 3225", "XTAL", {"1": "XIN", "3": "XOUT", "2": "GND", "4": "GND"})
c("C3", "27p", "XIN", "GND"); c("C4", "27p", "XOUT", "GND"); r("R2", "12.0k 1% (RBIAS)", "HUB_RBIAS", "GND")   # 18 pF load crystal: 2 x (18 - 4 stray)
for k in range(5, 12): c("C%d" % k, "100n", "+3V3", "GND")   # C5..C11 at VDD33, VDDA33 x4, VDD33CR, VDD33PLL
c("C12", "1u", "HUB_VD18", "GND"); c("C13", "1u", "HUB_VD18PLL", "GND"); c("C14", "1u", "+3V3", "GND")
r("R3", "10k", "HUB_CFG0", "GND"); r("R4", "10k", "HUB_CFG1", "GND")
for ref, net in (("R5", "HUB_DIS6M"), ("R6", "HUB_DIS6P"), ("R7", "HUB_DIS7M"), ("R8", "HUB_DIS7P")): r(ref, "10k", net, "+3V3")
esd("U2", "USB_UP_P", "USB_UP_N", "+3V3"); esd("U7", "USB_WALL_P", "USB_WALL_N", "+3V3")
# CH1 SDR bay on M2 (0x40): TPS2065C 1 A switch, INA219, USB-A receptacle (the one plug that stays)
tps2065("U4", "EN_RTL", "SW_RTL", "FLT_RTL", "+5V_M2"); r("R13", "10k", "FLT_RTL", "+3V3"); r("R30", "100k", "EN_RTL", "+3V3"); c("C15", "100n", "+5V_M2", "GND"); r("R14", "0.1R 1% 1206", "SW_RTL", "5V_RTL", "RS"); ina219("U5", "SW_RTL", "5V_RTL", "GND", "GND")
c("C16", "100n", "+3V3", "GND"); c("C17", "10u", "5V_RTL", "GND", "C10u")
part("J_RTL1", "Connector", "USB_A", "USB-A receptacle RTL-SDR", "USBA", {"1": "5V_RTL", "2": "USB_RTL_N", "3": "USB_RTL_P", "4": "GND", "5": "GND"}); esd("U6", "USB_RTL_P", "USB_RTL_N", "5V_RTL")

# --- LTE: mini PCIe socket for the Quectel EG25-G (mini PCIe HD V1.0, vendor/lte/): USB on 36/38 straight from the module's USB3-1 pair, 3.3 V from U32,
#     SIM on 8/10/12/14 to a nano-SIM holder, W_DISABLE# 20 and PERST# 22 from the expander, RI 17 and WAKE# 1 to it, UART 11/13 on a bench header, pin 24 reserved (not 3.3 V on this module)
MP = {n: "GND" for n in (4, 9, 15, 18, 21, 26, 27, 29, 34, 35, 37, 40, 43, 50)}
MP.update({n: "+3V3_LTE" for n in (2, 39, 41, 52)})
MP.update({1: "LTE_WAKE_n", 8: "SIM_VCC", 10: "SIM_IO", 11: "LTE_UART_RX", 12: "SIM_CLK", 13: "LTE_UART_TX", 14: "SIM_RST", 17: "LTE_RI", 20: "LTE_W_DIS_n", 22: "LTE_PERST_n",
           31: "LTE_DTR", 36: "USB_LTE_N", 38: "USB_LTE_P", 42: "LTE_nLED"})
part("J_LTE1", "Connector_Generic", "Conn_02x26_Odd_Even", "mini PCIe socket 52P H4.0 + 2x M2.5 standoffs: Quectel EG25-G (Cat 4, QMI, GNSS inside)", "MPCIE", {str(n): MP.get(n, "NC") for n in range(1, 53)})
part("J_SIM1", "Connector", "SIM_Card_Shielded", "nano-SIM push-push GCT SIM8060", "NANOSIM", {"1": "SIM_VCC", "2": "SIM_RST", "3": "SIM_CLK", "5": "GND", "6": "NC", "7": "SIM_IO", "SH": "GND"})
for k, net in ((56, "SIM_IO"), (57, "SIM_CLK"), (58, "SIM_RST")): c("C%d" % k, "33p", net, "GND", "C0402")
c("C59", "100n", "SIM_VCC", "GND")
r("R59", "4.7k", "LTE_W_DIS_n", "+3V3_LTE"); r("R60", "4.7k", "LTE_PERST_n", "+3V3_LTE"); r("R61", "10k", "LTE_DTR", "GND"); r("R62", "10k", "LTE_RI", "+3V3"); r("R63", "10k", "LTE_WAKE_n", "+3V3")
r("R64", "1k", "+3V3_LTE", "LED_LTE_A"); part("LED2", "Device", "LED", "amber LTE network (LED_WWAN# sinks)", "LED", {"2": "LED_LTE_A", "1": "LTE_nLED"})
part("J_LTEDBG", "Connector_Generic", "Conn_01x03", "EG25-G main UART (3.3 V, bench): GND TX RX", "PH1x3", {"1": "GND", "2": "LTE_UART_TX", "3": "LTE_UART_RX"})
esd("U8", "USB_LTE_P", "USB_LTE_N", "+3V3_LTE")

# --- WiFi P2P (B14): M.2 E-key socket on the module's PCIe Gen 2 x1 lane for the AsiaRF AW7915-AED (MediaTek MT7915DAN, 2T2R DBDC, vendor/wifi/),
#     the kit-to-kit link without an access point (IBSS as on V1, mesh or P2P as the bridge decides). Socket-side names of the KiCad Bus_M.2_Socket_E symbol
#     (M.2 specification): PETp/n0 35/37 = the card's transmit pair = the module's PCIe_RX, PERp/n0 41/43 = the module's PCIe_TX, REFCLK 47/49,
#     PERST0# 52 from PCIe_nRST, CLKREQ0# 53 to PCIe_CLK_nREQ, PEWAKE0# 55 to PCIE_nWAKE (unsupported in software, wired anyway), W_DISABLE1# 56 pulled up and
#     driven low by Q6 from the expander bit WIFI_DIS (radio off), W_DISABLE2# 54 pulled up, LED_1# 6 sinks LED7, 3.3 V on 2/4/72/74 from U36, USB and the rest NC.
#     AC coupling: the module's TX pair has its capacitors on the module, the card's TX pair has them on the card (CM5 datasheet 2.3).
M2 = {n: "NC" for n in list(range(1, 24)) + list(range(32, 76))}
M2.update({1: "GND", 7: "GND", 18: "GND", 33: "GND", 39: "GND", 45: "GND", 51: "GND", 57: "GND", 63: "GND", 69: "GND", 75: "GND",
           2: "+3V3_WIFI", 4: "+3V3_WIFI", 72: "+3V3_WIFI", 74: "+3V3_WIFI", 6: "WIFI_nLED",
           35: "PCIe_RX_P", 37: "PCIe_RX_N", 41: "PCIe_TX_P", 43: "PCIe_TX_N", 47: "PCIe_CLK_P", 49: "PCIe_CLK_N",
           52: "PCIe_nRST", 53: "PCIe_CLK_nREQ", 54: "WIFI_W_DIS2_n", 55: "PCIE_nWAKE", 56: "WIFI_W_DIS_n"})
part("J_WIFI1", "Connector", "Bus_M.2_Socket_E", "M.2 E-key socket 2230, M2.5 standoff: AsiaRF AW7915-AED (MT7915, WiFi 6 2x2 DBDC) on the CM5 PCIe lane, kit-to-kit link", "M2E", {str(k): v for k, v in M2.items()})
r("R76", "10k", "WIFI_W_DIS_n", "+3V3_WIFI"); r("R77", "10k", "WIFI_W_DIS2_n", "+3V3_WIFI"); nfet("Q6", "WIFI_DIS", "GND", "WIFI_W_DIS_n")   # expander bit high = radio disabled, no back-feed when the card rail is off
r("R78", "1k", "+3V3_WIFI", "LED7_A"); part("LED7", "Device", "LED", "blue WiFi link", "LED", {"2": "LED7_A", "1": "WIFI_nLED"})

# --- GNSS: u-blox NEO-M9N-00B (UBX-19014285, vendor/gnss/) on the module-side I2C (0x42), TIMEPULSE to GPIO22, active antenna bias from VCC_RF through a tee to the U.FL
part("U40", "RF_GPS", "NEO-M9N", "u-blox NEO-M9N-00B: I2C + PPS, external active antenna", "NEO",
     {"1": "NC", "2": "NC", "3": "GNSS_PPS", "4": "NC", "5": "NC", "6": "NC", "7": "GND", "8": "GNSS_nRST", "9": "GNSS_VCC_RF", "10": "GND", "11": "GNSS_RF_IN", "12": "GND",
      "13": "GND", "14": "NC", "15": "NC", "16": "NC", "17": "NC", "18": "SDA_CM", "19": "SCL_CM", "20": "GNSS_TXD", "21": "NC", "22": "VBAT", "23": "+3V3", "24": "GND"})
r("R65", "10k", "GNSS_nRST", "+3V3"); c("C60", "100n", "+3V3", "GND"); c("C61", "10u", "+3V3", "GND", "C10u")
r("R66", "10R", "GNSS_VCC_RF", "GNSS_BIAS"); part("L40", "Device", "L", "27nH 0402 (antenna bias tee)", "L0402", {"1": "GNSS_BIAS", "2": "GNSS_ANT"}); c("C62", "47p", "GNSS_ANT", "GNSS_RF_IN", "C0402")
part("J_GNSS1", "Connector", "Conn_Coaxial", "U.FL to the GNSS bulkhead pigtail", "UFL", {"1": "GNSS_ANT", "2": "GND"})
# --- LoRa: Seeed Wio-SX1262 (datasheet V1.1, vendor/lora/) on SPI0 CE1; T/R switching is the module's own DIO2, TCXO on DIO3; antenna on the module's IPEX
part("U41", "Connector_Generic", "Conn_01x12", "Seeed Wio-SX1262: 1 RF_SW 2 MISO 3 MOSI 4 SCK 5 NRST 6 NSS 7 GND 8 VCC 9 ANT 10 GND 11 BUSY 12 DIO1", "WIO",
     {"1": "NC", "2": "SPI_MISO", "3": "SPI_MOSI", "4": "SPI_SCLK", "5": "LORA_NRST", "6": "LORA_NSS", "7": "GND", "8": "+3V3", "9": "NC", "10": "GND", "11": "LORA_BUSY", "12": "LORA_DIO1"})
c("C63", "100n", "+3V3", "GND"); c("C64", "10u", "+3V3", "GND", "C10u"); r("R67", "10k", "LORA_NSS", "+3V3")
# --- ZigBee: Ebyte E72-2G4M20S1E (CC2652P, user manual, vendor/zigbee/), Koenkk CC1352P2_CC2652P_other coordinator firmware (UART DIO_12/13, BSL DIO_15, LEDs DIO_7/8), on-board PCB antenna
E72 = {n: "GND" for n in (1, 11, 12, 19, 23, 34)}
E72.update({2: "ZB_LED_R", 3: "ZB_LED_G", 7: "UART1_TX", 8: "UART1_RX", 10: "ZB_BSL", 13: "ZB_TMSC", 14: "ZB_TCKC", 20: "+3V3", 24: "ZB_nRST"})
part("U42", "Connector_Generic", "Conn_01x34", "Ebyte E72-2G4M20S1E CC2652P ZigBee coordinator (ZNP over UART1): 7 DIO_12 RX, 8 DIO_13 TX, 10 DIO_15 BSL, 24 RESET_N", "E72", {str(n): E72.get(n, "NC") for n in range(1, 35)})
c("C65", "100n", "+3V3", "GND"); c("C66", "10u", "+3V3", "GND", "C10u"); r("R68", "10k", "ZB_nRST", "+3V3"); r("R69", "10k", "ZB_BSL", "+3V3")
r("R70", "1k", "ZB_LED_R", "LED_ZBR_A"); part("LED3", "Device", "LED", "red ZigBee (DIO_7)", "LED", {"2": "LED_ZBR_A", "1": "GND"})
r("R71", "1k", "ZB_LED_G", "LED_ZBG_A"); part("LED4", "Device", "LED", "green ZigBee (DIO_8)", "LED", {"2": "LED_ZBG_A", "1": "GND"})
part("J_ZBDBG", "Connector_Generic", "Conn_01x05", "CC2652P cJTAG (bench): 3V3 GND TMSC TCKC RESET", "PH1x5", {"1": "+3V3", "2": "GND", "3": "ZB_TMSC", "4": "ZB_TCKC", "5": "ZB_nRST"})

# --- display: Touch Display 2 on MIPI0 through the 22-pin FPC (CM5IO J5 wiring: lanes, clock, CAM_GPIO0 on 17, SDA0/SCL0 on 20/21, 3.3 V on 22); 5 V by the J_TD2 lead
part("J_DISP", "Connector_Generic", "Conn_01x22", "Touch Display 2 FPC 22-pin 0.5 mm (Hirose FH12-22S-0.5SH), Standard-Mini 22-to-15 cable", "FPC22", {
 "1": "GND", "2": "DSI0_D0_N", "3": "DSI0_D0_P", "4": "GND", "5": "DSI0_D1_N", "6": "DSI0_D1_P", "7": "GND", "8": "DSI0_C_N", "9": "DSI0_C_P", "10": "GND", "11": "DSI0_D2_N", "12": "DSI0_D2_P",
 "13": "GND", "14": "DSI0_D3_N", "15": "DSI0_D3_P", "16": "GND", "17": "CAM_GPIO0", "18": "NC", "19": "NC", "20": "DISP_SCL", "21": "DISP_SDA", "22": "+3V3_CM"})
esd("U10", "DISP_SDA", "DISP_SCL", "+3V3_CM")

# --- expanders: U20 0x20 (channel and radio control), U21 0x25 (module and panel lines), both on the kit-bus side of U34 as on B12
part("U20", "Interface_Expansion", "PCA9555PW", "PCA9555PW 0x20", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "2": "GND", "21": "GND", "3": "GND",
 "4": "EN_RTL", "5": "EN_LTE", "6": "LTE_W_DIS_n", "7": "LTE_PERST_n", "8": "LTE_DTR", "9": "ZB_nRST", "10": "ZB_BSL", "11": "GNSS_nRST",
 "13": "FLT_RTL", "14": "LTE_RI", "15": "LTE_WAKE_n", "16": "RB_STATUS", "17": "RB_NETAV", "18": "RB_XMTG", "19": "RB_CTRL", "20": "RB_IEN"}, "C5626")
part("U21", "Interface_Expansion", "PCA9555PW", "PCA9555PW 0x25", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "2": "GND", "21": "+3V3", "3": "+3V3",   # A0 = pin 21, A1 = pin 2, A2 = pin 3: 0x25
 "4": "WL_nDIS", "5": "BT_nDIS", "6": "DCF_PON", "7": "EPD_RES_ALT", "8": "WIFI_DIS", "9": "EXP_SPARE1", "10": "EXP_SPARE2", "11": "EXP_SPARE3",
 "13": "DCF_T", "14": "EXP_SPARE4", "15": "EXP_SPARE5", "16": "EXP_SPARE6", "17": "EXP_SPARE7", "18": "EXP_SPARE8", "19": "EXP_SPARE9", "20": "EXP_SPARE10"}, "C5626")
c("C26", "100n", "+3V3", "GND"); c("C27", "100n", "+3V3", "GND")
for i in range(11):
    net = "WIFI_DIS" if i == 0 else "EXP_SPARE%d" % i   # B14: spare 0 became the WiFi radio disable
    part("TP%d" % (30 + i), "Connector", "TestPoint", net, "TP", {"1": net})
# --- RockBLOCK site (as B12, on UART2 fixed; the five status and control lines on U20)
part("J_RB9704", "Connector_Generic", "Conn_02x08_Odd_Even", "RockBLOCK 9704 16-pin (IDC 2x8)", "IDC16", {
 "1": "GND", "2": "NC", "3": "RB_IEN", "4": "GND", "5": "NC", "6": "RB_CTRL", "7": "RB_STATUS", "8": "RB_XMTG", "9": "NC", "10": "GND", "11": "NC", "12": "NC",
 "13": "UART2_RX", "14": "UART2_TX", "15": "5V_RB", "16": "GND"})
part("J_RB9603", "Connector_Generic", "Conn_01x10", "RockBLOCK 9603 PicoBlade 10", "PICO10", {
 "1": "UART2_RX", "2": "NC", "3": "NC", "4": "RB_NETAV", "5": "RB_STATUS", "6": "UART2_TX", "7": "RB_ONOFF", "8": "5V_RB", "9": "NC", "10": "GND"})
nfet("Q1", "Q1_G", "GND", "RB_ONOFF", "2N7002 OnOff open-drain buffer"); r("R26", "100R", "RB_CTRL", "Q1_G"); r("R27", "100k", "Q1_G", "GND"); r("R28", "10k", "RB_STATUS", "+3V3")
# CH4 RockBLOCK 5 V (0x43, 2 A): 9704 transmit bursts exceed the TPS2065C 1 A limit
part("F5", "Device", "Polyfuse", "2A hold 1812", "F1812", {"1": "+5V_M2", "2": "RB_FUSED"})
part("U13", "Power_Management", "TPS22810DRV", "TPS22810DRV", "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm", {"6": "RB_FUSED", "5": "EN_RB", "1": "SW_RB", "2": "NC", "3": "RB_CT", "4": "GND", "7": "GND"})
c("C28", "1n", "RB_CT", "GND"); c("C30", "1u", "RB_FUSED", "GND"); r("R33", "100k", "EN_RB", "+3V3")
r("R21", "0.05R 1% 1206", "SW_RB", "5V_RB", "RS"); ina219("U14", "SW_RB", "5V_RB", "SCL", "GND"); c("C18", "100n", "+3V3", "GND"); c("C19", "10u", "5V_RB", "GND", "C10u")   # U14 at 0x43 on B13 (0x42 on B12): the NEO-M9N answers at 0x42 on the same bus
# --- panel ribbon (PCB-C C5): fused 5 V, the kit I2C, SPI0 for the e-paper, the PWM dimmer, the TX mirror and the EMCON line; EPD_RES_ALT now from U21
part("F6", "Device", "Polyfuse", "0.5A hold 1812", "F1812", {"1": "+5V_M1", "2": "PANEL_5V"})
part("J_PANEL", "Connector_Generic", "Conn_02x10_Odd_Even", "panel ribbon to PCB-C (IDC 2x10)", "IDC20", {
 "1": "PANEL_5V", "2": "PANEL_5V", "3": "GND", "4": "SDA", "5": "SCL", "6": "EXP_INT", "7": "TR_APRS", "8": "EPD_DC", "9": "GND", "10": "SPI_SCLK",
 "11": "GND", "12": "SPI_MOSI", "13": "GND", "14": "SPI_CE0", "15": "EPD_RES_ALT", "16": "PWM1", "17": "PANEL_PWM", "18": "GND", "19": "TX_INHIBIT_n", "20": "+3V3"})
# --- DCF77 (both lines on U21 now), A-B interconnect 2x9: the two power-control lines, the wall-port USB pair from the hub, the kit I2C, EXP_INT, the TX mirror,
#     the EMCON line, I2S to the mezzanine codec, and the gated 3.3 V for that codec's digital side (so its I2S drivers die with the module)
part("J_DCF77", "Connector_Generic", "Conn_01x04", "DCF77 remote (XH2.5): 3V3 GND T P1", "XH4", {"1": "+3V3", "2": "GND", "3": "DCF_T", "4": "DCF_PON"}); r("R29", "10k", "DCF_T", "+3V3")
part("F7", "Device", "Polyfuse", "0.5A hold 1812", "F1812", {"1": "+3V3", "2": "+3V3_AB"})
part("J_AB1", "Connector_Generic", "Conn_02x09_Odd_Even", "A-B interconnect (IDC 2x9, underside)", "IDC18", {
 "1": "PI_SHDN_REQ", "2": "PI_KILL", "3": "GND", "4": "USB_WALL_P", "5": "USB_WALL_N", "6": "GND", "7": "SDA", "8": "SCL", "9": "EXP_INT", "10": "TR_APRS",
 "11": "I2S_BCLK", "12": "I2S_LRCLK", "13": "GND", "14": "TX_INHIBIT_n", "15": "I2S_DOUT", "16": "I2S_DIN", "17": "+3V3_AB", "18": "GND"})
# B13 note: 5V_RB, SW_RB and the RockBLOCK channel keep the B12 references; the ZigBee, XIAO, T-Call and T-Beam channels are gone with their plugs

# ----------------------------------------------------------------- emit
POWER = {"GND": ("power", "GND"), "+3V3": ("power", "+3V3")}   # the rails are plain labels, as on A: there is no power:+5V_M1 symbol
libsyms = {}; out = []; ROOT = str(uuid.uuid4())
def U(): return str(uuid.uuid4())
def ensure(lib, name):
    key = lib + ":" + name
    if key not in libsyms: libsyms[key] = synth_symbol(lib, name) if name in SYNTH else flatten(lib, name)
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
SECTIONS = [("POWER INPUT, RAILS, TEST POINTS", ["J_5V_M1", "J_5V_M2", "J_5V_PI", "D1", "C1", "C2", "D3", "C40", "C41", "D4", "C42", "C43", "C44", "C45", "C46", "C47", "C48", "R1", "LED1", "J_TD2"] + ["TP%d" % k for k in range(1, 24)] + ["#FLG%02d" % k for k in range(1, 18)]),
            ("3.3 V BUCKS: U31 BOARD (FOLLOWS THE CM5 3.3 V), U32 LTE SOCKET (EN_LTE, 0x44)", ["U31", "L31", "C31", "C32", "C33", "C34", "R35", "R36", "R37", "R38", "R41", "U33", "U32", "L32", "C35", "C36", "C37", "C38", "R39", "R40", "R42", "C50", "C51", "C52", "C53", "C49", "C39"]),
            ("COMPUTE MODULE 5 (2x AMPHENOL 10164227-1004A1RLF)", ["U30A", "U30B"]),
            ("CM5 SUPPORT: RTC CELL, LEDS, FAN, FLASH PORT, BENCH HEADERS", ["BT1", "R46", "LED5", "Q2", "R47", "R48", "LED6", "J_FAN", "R49", "J_FLASH", "R50", "R51", "U9", "J_RPIBOOT", "J_WP", "J_PMIC", "J_PWRBTN", "J_DBG"]),
            ("DOMAIN BOUNDARY: 2N7002 STAGES (SHDN_REQ, KILL, TR_APRS), TCA9517A I2C BUFFER", ["Q3", "R52", "Q4", "R53", "Q5", "R54", "R55", "U34", "R56", "C54", "C55", "R57", "R58", "R25"]),
            ("USB 2.0 HUB USB2517I ON THE CM5 USB3-0 PAIR", ["U1", "Y1", "C3", "C4", "R2", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14", "R3", "R4", "R5", "R6", "R7", "R8", "U2", "U7"]),
            ("CH1 SDR BAY: RTL-SDR V4 or LimeSDR Mini 2.0  (0x40)", ["U4", "R13", "R30", "C15", "R14", "U5", "C16", "C17", "J_RTL1", "U6"]),
            ("LTE: MINI PCIe SOCKET (QUECTEL EG25-G) ON THE CM5 USB3-1 PAIR, NANO-SIM", ["J_LTE1", "J_SIM1", "C56", "C57", "C58", "C59", "R59", "R60", "R61", "R62", "R63", "R64", "LED2", "J_LTEDBG", "U8"]),
            ("WIFI P2P: M.2 E-KEY SOCKET ON THE CM5 PCIe LANE (ASIARF AW7915-AED), 3.3 V BUCK ON PCIE_PWR_EN, 0x45", ["J_WIFI1", "R72", "U35", "U36", "L36", "C67", "C68", "C69", "C70", "R73", "R74", "R75", "C71", "C72", "R76", "R77", "Q6", "R78", "LED7"]),
            ("GNSS u-blox NEO-M9N ON I2C (0x42) + PPS, ANTENNA BIAS TEE", ["U40", "R65", "C60", "C61", "R66", "L40", "C62", "J_GNSS1"]),
            ("LoRa SEEED Wio-SX1262 ON SPI0 CE1", ["U41", "C63", "C64", "R67"]),
            ("ZIGBEE EBYTE E72-2G4M20S1E (CC2652P, ZNP) ON UART1", ["U42", "C65", "C66", "R68", "R69", "R70", "LED3", "R71", "LED4", "J_ZBDBG"]),
            ("TOUCH DISPLAY 2 ON MIPI0 (22-PIN FPC)", ["J_DISP", "U10"]),
            ("I2C EXPANDERS PCA9555 0x20 + 0x25", ["U20", "U21", "C26", "C27"] + ["TP%d" % (30 + k) for k in range(11)]),
            ("ROCKBLOCK SITE ON UART2: 9704 + 9603 CONNECTORS, OnOff BUFFER, CH4 5 V (0x43, 2A)", ["J_RB9704", "J_RB9603", "Q1", "R26", "R27", "R28", "F5", "U13", "C28", "C30", "R33", "R21", "U14", "C18", "C19"]),
            ("PANEL RIBBON (PCB-C CONTROL PANEL)", ["F6", "J_PANEL"]),
            ("DCF77 + A-B INTERCONNECT 2x9 (I2S, GATED 3.3 V FOR THE CODEC)", ["J_DCF77", "R29", "F7", "J_AB1"])]
byref = {p["ref"]: p for p in P}
def layout(page_h):
    """Columns of sections, top-down cursor; returns the layout width. A1 landscape takes 560 mm columns, A0 800 mm."""
    global out, pf_n
    out = []; pf_n = [0]; placed = set()
    COLW = 88.0; x = 20.0; y = 30.0
    for title, refs in SECTIONS:
        hs = []
        for ref in refs:
            p = byref[ref]; x0, x1, y0, y1 = extents(ensure(p["lib"], p["sym"])); hs.append((y1 - y0) + 2 * STUB + 12.0)
        if y + sum(hs) + 10 > page_h and y > 30.0:
            x += COLW; y = 30.0
        text(title, round((x - 15.0) / 1.27) * 1.27, round((y - 4.0) / 1.27) * 1.27)
        y += 4.0
        for ref, h in zip(refs, hs):
            p = byref[ref]; x0, x1, y0, y1 = extents(ensure(p["lib"], p["sym"]))
            if y + h > page_h:
                x += COLW; y = 34.0
            cy = y + (y1 + STUB) + 4.0               # symbol origin so its top pin+stub sits at y
            gx = round((x + 20.0) / 1.27) * 1.27; gy = round(cy / 1.27) * 1.27   # 1.27 mm grid, so every pin end and label is on grid
            if p["sym"] == "PWR_FLAG": emit_pwr_flag(p, gx, gy)
            else: emit_part(p, gx, gy)
            placed.add(ref); y += h
        y += 8.0
    missing = [p["ref"] for p in P if p["ref"] not in placed]
    if missing: raise SystemExit("unplaced parts: %s" % missing)
    return x + COLW
max_x = layout(560.0); PAPER = "A1"
if max_x > 820:
    max_x = layout(800.0); PAPER = "A0"      # A0 landscape is 1189 x 841
print("layout width %.0f mm -> paper %s" % (max_x, PAPER))
hdr = '(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "%s")\n\t(paper "%s")\n' % (ROOT, PAPER)
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-B COMPUTE") (date "2026-09-04") (rev "A") (company "MeshSat") (comment 1 "Phase B13 schematic (Compute Module 5 carrier, appendix 32.35), generated by tools/gen_sch_b.py. Netlist style: every pin carries a stub and a label; power pins carry power symbols."))\n'
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
