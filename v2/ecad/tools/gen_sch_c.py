#!/usr/bin/env python3
"""PCB-C CONTROL PANEL BACKER, phase C7 (MESHSAT-830; appendix 32.51, 32.52, 32.60): generate the KiCad 9 schematic (netlist style: every pin gets a
stub and a net label; GND gets power symbols). Runs where the KiCad symbol libraries are (the vast.ai box). Usage: gen_sch_c.py <out.kicad_sch> <project>

The backer hangs 10 mm under the aluminium face plate (tools/panel1450.py is the single source of the face positions). C7 replaces the two expanders'
role by an RP2040 panel controller (32.52: a USB device of B16's slot-2 hub, the kit I2C master, the e-paper, the sounder, the LED rail PWM, the
heartbeats, slot enables, HDMI input select and the power-control lines to B16 over the 2x13 ribbon J_PANEL; the two PCA9555 stay as the LED sinks
and mode inputs on the same bus). The hardware lines stay hardware: the EMCON toggle drives TX_INHIBIT_n directly and EMCON_HW through an inverter,
the ZEROIZE toggle drives ZEROIZE_HW, the TX lamp follows TR_APRS. The e-paper is the bare Pervasive Displays E2370KS0C1 on a 24-way ZIF with the
maker's boost circuit (rev 02 note: MOSFET, 10 uH, three SS2040FL, 0.47 ohm, 1 uF/25 V caps) behind a P-FET power switch. New on the face: the Xenarc
monitor (no electronics here; its cables go to B16 and A22), two U-174/U headset jacks wired to D8, a VEML7700 ambient light sensor under a light guide,
and a USB camera module behind a sealed window (its lead to B16's J_CAM). Eight standoff screws bond the board to the plate."""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-c-display"
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import intent as _intent
# the loads as the schematic wires them (8 Sep 2026): the LED rail leaves through the LIGHTING toggle in the left strip and comes back as LED_RAIL_SW,
# the LDO feeds the controller, the expanders, the e-paper and the sensor, the sounder is the rest; without them dc_drop split the whole 0.6 A over
# every U and J pad and asked for a 1.0 mm class, which the router could not lay on this board (two runs with no session, 90 min and 3 h)
_intent.rail("+5V", 5.0, 0.6, 1.0, "J_PANEL", budget=0.05, loads={"SW_LIGHT": 0.35, "U5": 0.20, "BZ1": 0.03},
             note="the panel rail over the ribbon (PANEL_5V on B16, fused F6). Budget 5 percent, not the 2 percent default and not the 3 percent this line "
                  "carried until 8 Sep 2026 22:55: every load tolerates it. The LED rail is PWM'd, the sounder is a buzzer, and the only regulated load is the "
                  "TLV75533 LDO, which has 1.5 V of headroom at 5 V in and 3.3 V out. C8 measures 171 mV (3.41 percent) with 0.6 A over 561 mm of 0.5 mm track, "
                  "half of it on 0.5 oz inner copper; the rail class stays 0.5 mm because 1.0 mm strangled the router in the driver cluster (32.76).")
SYMDIR = "/usr/share/kicad/symbols/"

# ----------------------------------------------------------------- s-expression helpers (as B13/B15)
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
    head = []
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
    sym = find_sym(lib, name)
    ext = [e for e in sym if isinstance(e, list) and e and e[0] == "extends"]
    if ext:
        parent = flatten_raw(lib, uq(ext[0][1]))
        child_props = {uq(e[1]): e for e in sym if isinstance(e, list) and e and e[0] == "property"}
        out = ["symbol", q(lib + ":" + name)]
        for e in parent[2:]:
            if isinstance(e, list) and e and e[0] == "property": e = child_props.get(uq(e[1]), e)
            out.append(e)
        for k, e in child_props.items():
            if not any(isinstance(x, list) and x and x[0] == "property" and uq(x[1]) == k for x in out): out.append(e)
        return rename_units(out, uq(ext[0][1]), name)
    return rename_units(flatten_raw(lib, name), name, name)
def flatten_raw(lib, name):
    import copy
    sym = copy.deepcopy(find_sym(lib, name))
    ext = [e for e in sym if isinstance(e, list) and e and e[0] == "extends"]
    if ext: return flatten(lib, name)
    sym[1] = q(lib + ":" + name); return sym
def rename_units(sym, oldname, newname):
    for e in sym:
        if isinstance(e, list) and e and e[0] == "symbol" and uq(e[1]).startswith(oldname + "_"): e[1] = q(newname + uq(e[1])[len(oldname):])
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

# ----------------------------------------------------------------- synthetic box symbols (odd pins left, even pins right)
# Raspberry Pi RP2040 (QFN-56, pin 57 the pad), the PDi 24-way FPC (pin names from the driving circuit note rev 02)
RP2040 = {1: "IOVDD", 2: "GPIO0", 3: "GPIO1", 4: "GPIO2", 5: "GPIO3", 6: "GPIO4", 7: "GPIO5", 8: "GPIO6", 9: "GPIO7", 10: "IOVDD", 11: "GPIO8", 12: "GPIO9", 13: "GPIO10", 14: "GPIO11", 15: "GPIO12", 16: "GPIO13",
          17: "GPIO14", 18: "GPIO15", 19: "TESTEN", 20: "XIN", 21: "XOUT", 22: "IOVDD", 23: "DVDD", 24: "SWCLK", 25: "SWD", 26: "RUN", 27: "GPIO16", 28: "GPIO17", 29: "GPIO18", 30: "GPIO19", 31: "GPIO20", 32: "GPIO21",
          33: "IOVDD", 34: "GPIO22", 35: "GPIO23", 36: "GPIO24", 37: "GPIO25", 38: "GPIO26_A0", 39: "GPIO27_A1", 40: "GPIO28_A2", 41: "GPIO29_A3", 42: "IOVDD", 43: "ADC_AVDD", 44: "VREG_VIN", 45: "VREG_VOUT",
          46: "USB_DM", 47: "USB_DP", 48: "USB_VDD", 49: "IOVDD", 50: "DVDD", 51: "QSPI_SD3", 52: "QSPI_SCLK", 53: "QSPI_SD0", 54: "QSPI_SD2", 55: "QSPI_SD1", 56: "QSPI_SS_N", 57: "GND"}
EPD24 = {1: "NC", 2: "GDR", 3: "RESE", 4: "NC", 5: "VDHR", 6: "NC", 7: "NC", 8: "BS", 9: "BUSY_N", 10: "RST_N", 11: "DC", 12: "CSB", 13: "SCL", 14: "SDA", 15: "VDDIO", 16: "VDD", 17: "VSS", 18: "VDDD",
         19: "NC", 20: "VDH", 21: "VGH", 22: "VDL", 23: "VGL", 24: "VCOM", 25: "SHIELD", 26: "SHIELD"}
SYNTH = {"RP2040": RP2040, "EPD24": EPD24}
def synth_symbol(lib, name):
    pins = SYNTH[name]; n = len(pins); rows = (n + 1) // 2; first = min(pins)
    W = 30.48; H = rows * 2.54 + 2.54
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
        if (num - first) % 2 == 0: at = ["at", "%.2f" % (-W / 2 - 2.54), "%.2f" % y, "0"]
        else: at = ["at", "%.2f" % (W / 2 + 2.54), "%.2f" % y, "180"]
        unit.append(["pin", "passive", "line", at, ["length", "2.54"], ["name", q(pins[num]), fx()], ["number", q(str(num)), fx()]])
    sym.append(body); sym.append(unit); return sym

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
P = []
def part(ref, lib, sym, value, fp, nets, lcsc=""):
    if any(p["ref"] == ref for p in P): raise SystemExit("duplicate reference " + ref)
    P.append(dict(ref=ref, lib=lib, sym=sym, value=value, fp=FP.get(fp, fp), nets={str(k): v for k, v in nets.items()}, lcsc=lcsc))
def synth(ref, name, value, fp, nets, lcsc=""):
    full = {str(k): nets.get(k, nets.get(str(k), "NC")) for k in SYNTH[name]}
    part(ref, "Connector_Generic", name, value, fp, full, lcsc)
def r(ref, val, a, b, fp="R", lcsc=""): part(ref, "Device", "R", val, fp, {"1": a, "2": b}, lcsc)
def c(ref, val, a, b, fp="C", lcsc="", bypass=None):
    part(ref, "Device", "C", val, fp, {"1": a, "2": b}, lcsc)
    if bypass: _intent.bypass(ref, bypass[0], bypass[1])   # 8 Sep 2026 (MESHSAT-862): the pin this capacitor serves, for the decoupling gate
def led(ref, colour, anode, cathode): part(ref, "Device", "LED", colour, "LED", {"2": anode, "1": cathode})
def nfet(ref, gate, source, drain, value="2N7002"): part(ref, "Transistor_FET", "2N7002", value, "SOT23", {"1": gate, "2": source, "3": drain}, "C8545")   # 1 G 2 S 3 D (SOT-23 order, appendix 32.36)
def level(ref, rn, far, near, near_rail, far_rail=None, rf=None):
    """Bidirectional 2N7002 stage between a module-domain line (near, pulled up to the module's rail) and the always-on side (far); the module off = gate low, nothing flows."""
    nfet(ref, near_rail, near, far); r(rn, "10k", near, near_rail)
    if far_rail: r(rf, "10k", far, far_rail)
def usb_c_recept(ref, dp, dm, vbus, cc1, cc2):
    part(ref, "Connector", "USB_C_Receptacle_USB2.0_16P", "USB-C 2.0 receptacle", "USBC",
         {"A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "A4": vbus, "A9": vbus, "B4": vbus, "B9": vbus, "A5": cc1, "B5": cc2, "A6": dp, "B6": dp, "A7": dm, "B7": dm, "A8": "NC", "B8": "NC", "S1": "GND"}, "C165948")
def esd(ref, dp, dm, vbus): part(ref, "Power_Protection", "USBLC6-2SC6", "USBLC6-2SC6", "SOT236", {"1": dp, "6": dp, "3": dm, "4": dm, "5": vbus, "2": "GND"}, "C7519")
def tps2065(ref, rail, en, out, flt): part(ref, "Power_Management", "TPS2065CDBV", "TPS2065CDBV", "SOT235", {"5": rail, "4": en, "1": out, "3": flt, "2": "GND"})
def tps22810(ref, vin, en, out, ct): part(ref, "Power_Management", "TPS22810DRV", "TPS22810DRV", "WSON6", {"6": vin, "5": en, "1": out, "2": "NC", "3": ct, "4": "GND", "7": "GND"})
def ic(ref, npins, value, fp, nets, lcsc=""): part(ref, "Connector_Generic", "Conn_01x%02d" % npins, value, fp, {str(k): nets.get(str(k), "NC") for k in range(1, npins + 1)}, lcsc)

def led3(ref, colour, a, k): part(ref, "Device", "LED", "3 mm %s, sunlight viewable" % colour, "LED3", {"2": a, "1": k})
def tp(ref, net): part(ref, "Connector", "TestPoint", net, "TP", {"1": net})
# ================================================================= the design
# --- ribbon from B16 (J_PANEL there has the same 2x13 map), 5 V entry, the local 3.3 V LDO, ESD on the USB pair
part("J_PANEL", "Connector_Generic", "Conn_02x13_Odd_Even", "panel ribbon from B16 J_PANEL (IDC 2x13 SMD, underside): 5 V, kit I2C, EMCON/ZEROIZE/inhibit, HDMI selects, USB, heartbeats, slot enables, power control", "IDC26", {
 "1": "+5V", "2": "+5V", "3": "GND", "4": "SDA", "5": "SCL", "6": "EXP_INT", "7": "TR_APRS", "8": "EMCON_HW", "9": "GND", "10": "ZEROIZE_HW", "11": "TX_INHIBIT_n", "12": "HDMI_SEL1", "13": "HDMI_SEL2",
 "14": "GND", "15": "USB_PNL_P", "16": "USB_PNL_N", "17": "GND", "18": "HB1", "19": "HB2", "20": "HB3", "21": "SLOT_EN1", "22": "SLOT_EN2", "23": "SLOT_EN3", "24": "PI_SHDN_REQ", "25": "PI_KILL", "26": "SHORE_INHIBIT"})
c("C1", "10u", "+5V", "GND", "C10u", "C15850"); c("C2", "10u", "+3V3", "GND", "C10u", "C15850")
ic("U5", 5, "TLV75533PDBV 3.3 V 500 mA LDO for the controller, expanders, e-paper and sensor (1 IN 2 GND 3 EN 4 NC 5 OUT)", "SOT235", {"1": "+5V", "2": "GND", "3": "+5V", "5": "+3V3"})
c("C3", "1u", "+5V", "GND"); c("C4", "1u", "+3V3", "GND")
esd("U6", "USB_PNL_P", "USB_PNL_N", "+3V3"); esd("U7", "SDA", "SCL", "+3V3"); esd("U8", "TR_APRS", "EXP_INT", "+3V3")
for i in range(1, 6): part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": ["+5V", "+3V3", "GND", "LED_RAIL_SW", "LED_RAIL"][i - 1]})
# --- the RP2040 panel controller (rp2040/rpi-rp2040-datasheet.pdf; the minimal design of the hardware design guide: 12 MHz crystal with 15 pF loads and a 1k on XOUT, W25Q16 QSPI flash,
#     27 ohm USB series, RUN pull-up, BOOTSEL by a solder jumper on QSPI_SS). GPIO: 0 SDA 1 SCL (the kit I2C bus, this board its master), 2 EPD SCL, 3 EPD SDA, 4 EPD DC, 5 EPD CS, 6 EPD RST,
#     7 EPD BUSY, 8 LED rail PWM, 9 sounder PWM, 10 to 12 heartbeats HB1..3 (in), 13 to 15 SLOT_EN1..3, 16 and 17 HDMI_SEL1/2, 18 PI_SHDN_REQ, 19 PI_KILL, 20 SHORE_INHIBIT, 21 EMCON_HW (read),
#     22 ZEROIZE_HW (read), 23 TR_APRS (read), 24 EXP_INT (read), 25 status LED, 26 LED rail sense (ADC0), 27 TEST_SW, 28 SOS_SW, 29 EPD_PWR_n (the boost's power switch)
synth("U3", "RP2040", "RP2040 panel controller (USB device on B16's slot-2 hub, the kit I2C master)", "QFN56", {
 1: "+3V3", 10: "+3V3", 22: "+3V3", 33: "+3V3", 42: "+3V3", 49: "+3V3", 43: "+3V3", 44: "+3V3", 48: "+3V3", 23: "C_DVDD", 50: "C_DVDD", 45: "C_DVDD", 57: "GND", 19: "GND",
 2: "SDA", 3: "SCL", 4: "EPD_SCL", 5: "EPD_SDA", 6: "EPD_DC", 7: "EPD_CS", 8: "EPD_RST", 9: "EPD_BUSY", 11: "PANEL_PWM", 12: "PWM1", 13: "HB1", 14: "HB2", 15: "HB3", 16: "SLOT_EN1", 17: "SLOT_EN2", 18: "SLOT_EN3",
 20: "XIN", 21: "XOUT_R", 24: "SWCLK", 25: "SWDIO", 26: "C_RUN", 27: "HDMI_SEL1", 28: "HDMI_SEL2", 29: "PI_SHDN_REQ", 30: "PI_KILL", 31: "SHORE_INHIBIT", 32: "EMCON_HW", 34: "ZEROIZE_HW", 35: "TR_APRS", 36: "EXP_INT",
 37: "LED_STAT", 38: "RAIL_SENSE", 39: "TEST_SW", 40: "SOS_SW", 41: "EPD_PWR_n", 46: "USB_DM_R", 47: "USB_DP_R", 51: "QSPI_D3", 52: "QSPI_SCLK", 53: "QSPI_D0", 54: "QSPI_D2", 55: "QSPI_D1", 56: "QSPI_SS"}, "C2040")
ic("U4", 9, "W25Q16JVUXIQ 16 Mbit QSPI flash (USON-8: 1 CS 2 DO/IO1 3 WP/IO2 4 GND 5 DI/IO0 6 CLK 7 HOLD/IO3 8 VCC, pad)", "USON8", {"1": "QSPI_SS", "2": "QSPI_D1", "3": "QSPI_D2", "4": "GND", "5": "QSPI_D0", "6": "QSPI_SCLK", "7": "QSPI_D3", "8": "+3V3", "9": "GND"}, "C2843335")
part("Y1", "Device", "Crystal_GND24", "12 MHz ABM8-272-T3 (3225): 1 XIN, 3 XOUT, 2 and 4 GND", "XTAL", {"1": "XIN", "2": "GND", "3": "XOUT", "4": "GND"}, "C20625731")
c("C5", "15p NP0", "XIN", "GND", "C0402"); c("C6", "15p NP0", "XOUT", "GND", "C0402"); r("R1", "1k", "XOUT_R", "XOUT")
r("R2", "27R", "USB_DP_R", "USB_PNL_P"); r("R3", "27R", "USB_DM_R", "USB_PNL_N"); r("R4", "10k", "C_RUN", "+3V3"); r("R5", "1k (BOOTSEL)", "QSPI_SS", "BOOT_J")
part("JP1", "Jumper", "SolderJumper_2_Open", "BOOTSEL: short while powering to enter the USB bootloader", "JP2", {"1": "BOOT_J", "2": "GND"})
for k in range(7, 14): c("C%d" % k, "100n", "+3V3", "GND")
c("C14", "1u", "C_DVDD", "GND"); c("C15", "1u", "C_DVDD", "GND"); c("C16", "1u", "+3V3", "GND")
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
for i, net in enumerate(("SOS_SW", "ZEROIZE_HW", "TEST_SW", "LIGHT_DAY_n", "LIGHT_NIGHT_n"), 9):
    r("R%d" % i, "10k", net, "+3V3", "R", "C25804"); c("C%d" % (i + 10), "10n", net, "GND", "C", "C57112")
r("R14", "100k", "TX_INHIBIT_n", "+3V3", "R", "C25803"); c("C24", "10n", "TX_INHIBIT_n", "GND", "C", "C57112")
ic("U9", 5, "74LVC1G04 inverter (2 A 4 Y): EMCON_HW = NOT TX_INHIBIT_n, the hardware emission-control line to every transmitter rail (32.50 item 3)", "SOT235", {"2": "TX_INHIBIT_n", "3": "GND", "4": "EMCON_HW", "5": "+3V3"})
c("C25", "100n", "+3V3", "GND")
r("R15", "10k", "LED_RAIL_SW", "RAIL_SENSE", "R", "C25804"); r("R16", "10k", "PANEL_ID", "+3V3", "R", "C25804")
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
# --- switches (bench parts on flying leads; footprints = panel hole + lead pads)
part("SW_MAIN", "Connector_Generic", "Conn_01x04", "MAIN PWR 19 mm momentary, green ring (to A22 J_MAINSW); C&K ATP19-SL1-603-B0SA-03G; silicone gasket washer under the bezel", "SW19", {"1": "MAINSW_A", "2": "MAINSW_B", "3": "MAINRING_A", "4": "GND"})
r("R%d" % rn, "470R", "LED_RAIL_SW", "MAINRING_A", "R", "C23179"); rn += 1
part("SW_PI", "Connector_Generic", "Conn_01x04", "PI 16 mm recessed momentary, amber ring (PI_SHDN_REQ to the modules through the controller); C&K ATP16-SL1-403-M0SA-04G; silicone gasket washer under the bezel", "SW16", {"1": "PIJ2_A", "2": "PIJ2_B", "3": "PIRING_A", "4": "PIRING_K"})
r("R%d" % rn, "300R", "LED_RAIL", "PIRING_A", "R", "C23025"); rn += 1
part("SW_TEST", "Connector_Generic", "Conn_01x04", "TEST/ACK 16 mm momentary, white ring; C&K ATP16-SL1-203-M0SA-04G; silicone gasket washer under the bezel", "SW16", {"1": "TEST_SW", "2": "GND", "3": "TESTRING_A", "4": "GND"})
r("R%d" % rn, "470R", "LED_RAIL", "TESTRING_A", "R", "C23179"); rn += 1
part("SW_SOS", "Connector_Generic", "Conn_01x03", "SOS locking toggle, maintained (APEM 5636ADKB-2V, both positions locked, red boot, hinged safety cover per 32.50; ruling 32.13); K front seal in the keyed 6.5 hole; the controller acts after 2 s closed", "TGL3", {"1": "SOS_SW", "2": "GND", "3": "NC"})
part("SW_EMCON", "Connector_Generic", "Conn_01x03", "EMCON locking toggle (closed = TX inhibit, a hardware line: TX_INHIBIT_n low and EMCON_HW high; APEM 5636ADKB-2V, hinged safety cover); K front seal in the keyed 6.5 hole", "TGL3", {"1": "TX_INHIBIT_n", "2": "GND", "3": "NC"})
part("SW_ZERO", "Connector_Generic", "Conn_01x03", "ZEROIZE locking toggle, maintained (APEM 5636ADKB-2V, hinged safety cover; ruling 32.13); K front seal in the keyed 6.5 hole; ZEROIZE_HW low = wipe the secure element and assert the disk-key wipe (32.52)", "TGL3", {"1": "ZEROIZE_HW", "2": "GND", "3": "NC"})
# power-button leads: ferrite + 100 nF at the panel end (the leads pass the antenna feeds)
part("FB1", "Device", "L", "ferrite 600R", "FB", {"1": "MAINSW_A", "2": "MAINSW_A2"}, "C1002"); part("FB2", "Device", "L", "ferrite 600R", "FB", {"1": "MAINSW_B", "2": "MAINSW_B2"}, "C1002")
c("C26", "100n", "MAINSW_A2", "MAINSW_B2", "C", "C14663")
part("J_MAINSW", "Connector_Generic", "Conn_01x02", "MAIN button lead to A22 J_MAINSW (XH2.5 at the A22 end): two solder lands on the underside, soldered and beaded", "XH2", {"1": "MAINSW_A2", "2": "MAINSW_B2"})
part("FB3", "Device", "L", "ferrite 600R", "FB", {"1": "PIJ2_A", "2": "PIJ2_A2"}, "C1002"); part("FB4", "Device", "L", "ferrite 600R", "FB", {"1": "PIJ2_B", "2": "PIJ2_B2"}, "C1002")
c("C27", "100n", "PIJ2_A2", "PIJ2_B2", "C", "C14663")
part("J_PIJ2", "Connector_Generic", "Conn_01x02", "PI button lead: two solder lands on the underside (the controller reads it as the module shutdown request)", "XH2", {"1": "PIJ2_A2", "2": "PIJ2_B2"})
# --- e-paper: the bare E2370KS0C1 on a 24-way ZIF (top strip, top side) with the PDi rev 02 driving circuit behind a P-FET power switch (leakage: "connect to a transistor switch")
synth("J_EPD", "EPD24", "Hirose FH34SRJ-24S-0.5SH ZIF for the E2370KS0C1 flex (0.5 mm, 24 way; pin names per the PDi driving circuit note rev 02)", "ZIF24",
     {2: "EPD_GDR", 3: "EPD_RESE", 5: "EPD_VDHR", 8: "GND", 9: "EPD_BUSY", 10: "EPD_RST", 11: "EPD_DC", 12: "EPD_CS", 13: "EPD_SCL", 14: "EPD_SDA", 15: "EPD_VCC", 16: "EPD_VCC", 17: "GND", 18: "EPD_VDDD",
      20: "EPD_VDH", 21: "EPD_VGH", 22: "EPD_VDL", 23: "EPD_VGL", 24: "EPD_VCOM", 25: "GND", 26: "GND"})
part("Q5", "Transistor_FET", "AO3401A", "AO3401A P-FET: the e-paper's supply switch (EPD_PWR_n low = on)", "SOT23", {"1": "EPD_PWR_n", "2": "+3V3", "3": "EPD_VCC"}, "C15127"); r("R%d" % rn, "10k", "EPD_PWR_n", "+3V3"); rn += 1
c("C28", "4.7u", "EPD_VCC", "GND", "C10u"); c("C29", "100n", "EPD_VCC", "GND")
part("L1", "Device", "L", "10uH ATNR4010100MT 0.8 A (the boost inductor)", "L4020", {"1": "EPD_VCC", "2": "EPD_SW"})
part("Q6", "Transistor_FET", "2N7002", "Si1308EDL class N-FET (RDS under 200 mOhm, VGS 2.5 V): the boost switch on GDR", "SOT23", {"1": "EPD_GDR", "2": "EPD_RESE", "3": "EPD_SW"}, "C8545")
r("R%d" % rn, "0.47R 1%", "EPD_RESE", "GND"); rn += 1
part("D19", "Device", "D_Schottky", "SS2040FL: EPD_SW -> VGH", "SOD123F", {"1": "EPD_SW", "2": "EPD_VGH"}); c("C30", "1u 25V", "EPD_VGH", "GND")
c("C31", "1u 25V", "EPD_SW", "EPD_PUMP"); part("D20", "Device", "D_Schottky", "SS2040FL: pump clamp", "SOD123F", {"1": "EPD_PUMP", "2": "GND"}); part("D21", "Device", "D_Schottky", "SS2040FL: pump -> VGL", "SOD123F", {"1": "EPD_VGL", "2": "EPD_PUMP"}); c("C32", "1u 25V", "EPD_VGL", "GND")
for i, net in enumerate(("EPD_VDHR", "EPD_VDDD", "EPD_VDH", "EPD_VDL", "EPD_VCOM"), 33): c("C%d" % i, "1u 25V", net, "GND")
# --- sounder: IP67 panel-mount part in its own sealed hole on the face, driven on +5V through Q4 from the controller's PWM1; ACK mutes in firmware
part("BZ1", "Device", "Buzzer", "IP67 panel-mount sounder, 5 V DC continuous, bezel gasket on the face, two flying leads (Floyd Bell MC-09-530-Q class)", "BZ", {"1": "BZ_K", "2": "+5V"})
nfet("Q4", "Q4_G", "GND", "BZ_K"); r("R%d" % rn, "100R", "PWM1", "Q4_G", "R", "C22775"); rn += 1; r("R%d" % rn, "100k", "Q4_G", "GND", "R", "C25803"); rn += 1
# --- ambient light sensor (right strip, top side, under its own Mentor light guide) and the camera module's mount (its USB lead goes to B16's J_CAM)
ic("U_LIGHT", 4, "Vishay VEML7700 ambient light sensor (1 SCL 2 VDD 3 GND 4 SDA), I2C 0x10", "VEML", {"1": "SCL", "2": "+3V3", "3": "GND", "4": "SDA"}, "C504893"); c("C38", "100n", "+3V3", "GND")
for i in (1, 2): part("CAM_H%d" % i, "Mechanical", "MountingHole", "M2 screw of the USB camera module (25 x 25 board, sheet owed) behind the plate's sealed window", "CAMH", {})
for i in (1, 2): part("J_HSJ%d" % i, "Mechanical", "MountingHole", "U-174/U headset jack %d (Amphenol Nexus class, drawing owed): 17 mm hole through the backer, bushing nut below; its five leads run to D8 J_HS%d" % (i, i), "HSJ", {})
# --- chassis bond: the eight standoff screws through GND ring pads (MIL-STD-461 bonding of the aluminium plate)
for i in range(1, 9): part("H%d" % i, "Mechanical", "MountingHole_Pad", "M3 x 6 into the face plate's self-clinching standoff: GND bond to the plate", "MHPAD", {"1": "GND"})
for i, net in enumerate(("+5V", "+3V3", "GND", "EXP_INT", "TX_INHIBIT_n", "EMCON_HW", "ZEROIZE_HW", "SPARE1", "SPARE2", "SPARE3", "SPARE4", "SPARE5", "SPARE6", "SPARE7", "SPARE8", "SPARE9", "SPARE10", "SPARE11", "SPARE12", "EPD_BUSY", "EPD_VGH", "EPD_VGL", "HB1", "HB2", "HB3", "SLOT_EN1", "SLOT_EN2", "SLOT_EN3", "HDMI_SEL1", "HDMI_SEL2", "PI_SHDN_REQ", "PI_KILL", "SHORE_INHIBIT", "PIJ2_A", "PIJ2_B"), 6): tp("TP%d" % i, net)
# ----------------------------------------------------------------- emit (as B15)
POWER = {"GND": ("power", "GND")}
libsyms = {}; out = []; ROOT = str(uuid.uuid4())
def U(): return str(uuid.uuid4())
def ensure(lib, name):
    key = lib + ":" + name
    if key not in libsyms: libsyms[key] = synth_symbol(lib, name) if name in SYNTH else flatten(lib, name)
    return libsyms[key]
def extents(sym):
    pins = pins_of(sym); xs = [p[2] for p in pins] or [0]; ys = [p[3] for p in pins] or [0]
    return min(xs), max(xs), min(ys), max(ys)
def place_symbol(lib, name, ref, value, fp, x, y, lcsc="", hide_props=False):
    sym = ensure(lib, name); pins = pins_of(sym); x0, x1, y0, y1 = extents(sym)
    s = '(symbol (lib_id %s) (at %.2f %.2f 0) (unit 1) (exclude_from_sim no) (in_bom %s) (on_board %s) (dnp no) (fields_autoplaced yes) (uuid "%s")\n' % (
        q(lib + ":" + name), x, y, "no" if lib == "power" or name in ("TestPoint",) else "yes", "no" if lib == "power" else "yes", U())
    def prop(k, v, px, py, hide): return '\t(property %s %s (at %.2f %.2f 0) (effects (font (size 1.27 1.27)) (justify left)%s))\n' % (q(k), q(v), px, py, " (hide yes)" if hide else "")
    s += prop("Reference", ref, x + x1 + 1.27, y - y1 - 1.27, hide_props); s += prop("Value", value, x + x1 + 1.27, y - y1 + 1.27, hide_props)
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
    pins = place_symbol(p["lib"], p["sym"], p["ref"], p["value"], p["fp"], x, y, p["lcsc"]); seen = set()
    for num, nm, px, py, rot in pins:
        sx, sy = x + px, y - py; key = (round(sx, 2), round(sy, 2)); net = p["nets"].get(num)
        if net is None: raise SystemExit("%s pin %s (%s) has no net assignment" % (p["ref"], num, nm))
        if key in seen: continue
        seen.add(key)
        if net == "NC": noconn(sx, sy); continue
        dx, dy = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[rot]; ex, ey = sx + dx * STUB, sy + dy * STUB; wire(sx, sy, ex, ey)
        if net in POWER:
            lib, nm2 = POWER[net]; place_symbol(lib, nm2, "#PWR%03d" % pf_n[0], net, "", ex, ey); pf_n[0] += 1
        else: label(net, ex, ey, {(-1, 0): 180, (1, 0): 0, (0, 1): 270, (0, -1): 90}[(dx, dy)])
def emit_pwr_flag(p, x, y):
    place_symbol("power", "PWR_FLAG", p["ref"], "PWR_FLAG", "", x, y); net = p["nets"]["1"]; wire(x, y, x, y + STUB)
    if net in POWER:
        lib, nm2 = POWER[net]; place_symbol(lib, nm2, "#PWR%03d" % pf_n[0], net, "", x, y + STUB); pf_n[0] += 1
    else: label(net, x, y + STUB, 270)
byref = {p["ref"]: p for p in P}

def refs_matching(pred): return [p["ref"] for p in P if pred(p["ref"])]
SECTIONS = [("RIBBON FROM B16, 5 V, 3.3 V LDO, USB AND BUS ESD, FLAGS", ["J_PANEL", "C1", "C2", "U5", "C3", "C4", "U6", "U7", "U8", "#FLG01", "#FLG02", "#FLG03", "#FLG04", "#FLG05"]),
            ("RP2040 PANEL CONTROLLER, FLASH, CRYSTAL, BOOTSEL, BUS PULL-UPS", ["U3", "U4", "Y1", "C5", "C6", "R1", "R2", "R3", "R4", "R5", "JP1"] + ["C%d" % k for k in range(7, 17)] + ["TP1", "TP2", "TP3", "R6", "D18", "R7", "R8"]),
            ("EXPANDERS 0x22 / 0x23, MODE INPUTS, EMCON INVERTER, STRAPS", ["U1", "U2", "C17", "C18"] + ["R%d" % k for k in range(9, 17)] + ["C%d" % k for k in range(19, 26)] + ["U9", "JP2"]),
            ("LED RAIL, INDICATORS, TX LAMP, SWITCHES AND LEADS", ["SW_LIGHT", "Q1", "R17", "R18", "Q2", "R19", "R20", "TP4", "TP5"] + [p["ref"] for p in P if p["ref"].startswith("D") and p["ref"][1:].isdigit() and int(p["ref"][1:]) <= 17] + ["R%d" % k for k in range(21, 43)] + ["Q3", "SW_MAIN", "SW_PI", "SW_TEST", "SW_SOS", "SW_EMCON", "SW_ZERO", "FB1", "FB2", "C26", "J_MAINSW", "FB3", "FB4", "C27", "J_PIJ2"]),
            ("E-PAPER ZIF AND THE PDi BOOST, SOUNDER, LIGHT SENSOR, CAMERA MOUNT", ["J_EPD", "Q5", "C28", "C29", "L1", "Q6", "D19", "C30", "C31", "D20", "D21", "C32", "C33", "C34", "C35", "C36", "C37", "BZ1", "Q4", "U_LIGHT", "C38", "CAM_H1", "CAM_H2", "J_HSJ1", "J_HSJ2"])]
placed_refs = {r_ for _, rs in SECTIONS for r_ in rs}
SECTIONS.append(("STANDOFF SCREWS (GND BOND), TEST POINTS, THE REST", [p["ref"] for p in P if p["ref"] not in placed_refs]))
def layout(page_h):
    global out, pf_n
    out = []; pf_n = [0]; placed = set(); COLW = 92.0; x = 20.0; y = 30.0
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
max_x = layout(800.0); PAPER = "A0"
print("layout width %.0f mm -> paper %s (A0 landscape is 1189 wide; the schematic PDF is a netlist record, not a drawing)" % (max_x, PAPER))
hdr = '(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "%s")\n\t(paper "%s")\n' % (ROOT, PAPER)
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-C CONTROL PANEL BACKER") (date "2026-09-07") (rev "A") (company "MeshSat") (comment 1 "Phase C7 schematic (RP2040 panel controller, PDi e-paper driver, Xenarc face, headset jacks, camera window, light sensor; appendix 32.51, 32.52, 32.60), generated by tools/gen_sch_c.py"))\n'
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
for _i, _pin in enumerate((1, 10, 22, 33, 42, 49)): _intent.bypass("C%d" % (7 + _i), "U3", _pin, "+3V3")   # the RP2040's six IOVDD pins
_intent.bypass("C13", "U4", "8", "+3V3")        # the QSPI flash's VCC
_intent.bypass("C14", "U3", "23", "C_DVDD"); _intent.bypass("C15", "U3", "50", "C_DVDD")   # the two DVDD pins off the internal regulator
_intent.bypass("C16", "U3", "44", "+3V3")       # VREG_VIN
_intent.bypass("C3", "U5", "1", "+5V"); _intent.bypass("C4", "U5", "5", "+3V3")            # the LDO's input and output capacitors
_intent.bypass("C17", "U1", "24", "+3V3"); _intent.bypass("C18", "U2", "24", "+3V3")       # the two expanders
_intent.bypass("C25", "U9", "5", "+3V3")        # the EMCON inverter
_intent.bypass("C38", "U_LIGHT", "2", "+3V3")   # the light sensor
_intent.bypass("C29", "J_EPD", "15", "EPD_VCC"); _intent.bypass("C28", "J_EPD", "16", "EPD_VCC")
# OPEN, needs a part and therefore a regeneration, not fixed here: the RP2040's ADC_AVDD (pin 43) and USB_VDD (pin 48) share the seven
# 100 nF above with the six IOVDD pins and the flash, so two supply pins have no capacitor of their own; RAIL_SENSE is an ADC input, so
# pin 43 wants its own 100 nF behind a ferrite or a 10 ohm. Carried with the decoupling placement decision for the next C phase.
_intent.write(OUT, PROJECT, P)   # 8 Sep 2026 (MESHSAT-862): design intent as data, out/<project>-intent.json
