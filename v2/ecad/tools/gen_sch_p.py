#!/usr/bin/env python3
"""PCB-P PACK BMS, phase P1 (MESHSAT-830; appendix 32.62: the built 4S smart pack of the kit): generate the KiCad 9 schematic (netlist style:
every pin gets a stub and a net label; GND pins get power symbols). Runs where the KiCad symbol libraries are (the vast.ai box).
Usage: gen_sch_p.py <out.kicad_sch> <project>

The board sits inside the pack's printed enclosure in the east pocket of the Peli 1450 (58 x 240 x 48 mm beside A22, under B16's overhang) on
a 4S block of 18650 or 21700 cells (4S4P or 4S3P, about 200 Wh). TI BQ4050 (SMBus 1.1 gas gauge with Impedance Track, primary protection and
internal cell balancing for 1S to 4S; datasheet SLUSC67B in vendor/battery/ti-bq4050.pdf): the cell taps VC1..VC4 through 100 ohm and 0.1 uF,
BAT and PACK sense inputs through 100 ohm and 1 kohm, VCC from the pack terminal, the coulomb counter across a 2 mohm 2512 sense resistor in the
negative path (SRP on the cell side, SRN on the pack side, 100 ohm each), one 10k NTC (103AT in the cell block) on TS1, the unused TS inputs
tied to VSS through 10k, PTC and PTCEN to VSS (disabled), PRES pulled to VSS (an embedded pack, present), no chemical fuse (the 25 A mini blade
is the fuse), no LED display (the panel shows the bar). The high-side protection is two CSD17570Q5B PowerPAK N-FETs in series with common drain
(the charge FET's source at the fused cell terminal, the discharge FET's source at PACK+), 5.1 kohm gate drive and 10 Mohm gate-source each,
driven by CHG and DSG. SMBus clock and data leave through 100 ohm with an ESD clamp. Connectors: J_CELL (JST-XH 1x5, the five tap wires),
J_TS (JST-PH 1x2, the thermistor), J_SMB (JST-XH 1x4: SMBC, SMBD, GND, PRES), the pack leads W_P and W_N as 2.5 mm2 solder lands (12 AWG to
the XT60 that lands on E6's J_BATT), the blade holder F1. Two layers, 2 oz copper, the power path in locked bands (gen_pcb_p3.py).
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-p-pack"
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import intent as _intent
_intent.rail("PACK_P", 14.4, 10.0, 18.0, "W_P", note="the pack lead")
_intent.rail("CELL4", 14.4, 10.0, 18.0, "W_BP", note="the top cell node from the block strip")
_intent.rail("FUSED", 14.4, 10.0, 18.0, "F1", note="after the blade fuse")
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

# ----------------------------------------------------------------- synthetic box symbols (parts with no library symbol): odd pins left, even pins right
# NiceRF SA868 (V1.x manual, 18 castellations); TI PCM2912A (SLES230A, TQFP-32); TI TPA6132A2 (SLOS553, QFN-16, pin 17 the pad); TI TUSB2046B (SLLS413L, LQFP-32);
# Silicon Labs CP2102N QFN28 (as B16)
SA868 = {1: "AUDIO_ON_n", 2: "NC", 3: "AF_OUT", 4: "NC", 5: "PTT_n", 6: "PD", 7: "H/L", 8: "VBAT", 9: "GND", 10: "GND", 11: "NC", 12: "ANT", 13: "NC", 14: "NC", 15: "NC", 16: "RXD", 17: "TXD", 18: "MIC_IN"}
PCM2912A = {1: "BGND", 2: "VBUS", 3: "D-", 4: "D+", 5: "VDD", 6: "DGND", 7: "XTO", 8: "XTI", 9: "FL", 10: "FR", 11: "VCOM1", 12: "VCOM2", 13: "AGND", 14: "NC", 15: "VCCA", 16: "VIN", 17: "MBIAS", 18: "VOUTL",
            19: "VCCL", 20: "HGND", 21: "VCCR", 22: "VOUTR", 23: "MAMP", 24: "POWER", 25: "PGND", 26: "VCCP", 27: "TEST1", 28: "TEST0", 29: "SSPND", 30: "MMUTE", 31: "REC", 32: "PLAY"}
TPA6132A2 = {1: "INL-", 2: "INL+", 3: "INR+", 4: "INR-", 5: "OUTR", 6: "G0", 7: "G1", 8: "HPVSS", 9: "CPN", 10: "PGND", 11: "CPP", 12: "HPVDD", 13: "EN", 14: "VDD", 15: "SGND", 16: "OUTL", 17: "PAD"}
TUSB2046B = {1: "DP0", 2: "DM0", 3: "VCC", 4: "RESET_n", 5: "EECLK", 6: "EEDATA/GANGED", 7: "GND", 8: "BUSPWR", 9: "PWRON1_n", 10: "OVRCUR1_n", 11: "DM1", 12: "DP1", 13: "PWRON2_n", 14: "OVRCUR2_n", 15: "DM2", 16: "DP2",
             17: "PWRON3_n", 18: "OVRCUR3_n", 19: "DM3", 20: "DP3", 21: "PWRON4_n", 22: "OVRCUR4_n", 23: "DM4", 24: "DP4", 25: "VCC", 26: "EXTMEM", 27: "TSTPLL/48MCLK", 28: "GND", 29: "XTAL2", 30: "XTAL1", 31: "TSTMODE", 32: "SUSPND"}
CP2102 = {1:"DCD",2:"RI_CLK",3:"GND",4:"D+",5:"D-",6:"VDD",7:"VREGIN",8:"VBUS",9:"RSTb",10:"NC",11:"SUSPENDb",12:"SUSPEND",13:"CHREN",14:"CHR1",15:"CHR0",16:"GPIO3",17:"GPIO2",18:"GPIO1",19:"GPIO0",20:"GPIO6",21:"GPIO5",22:"GPIO4",23:"CTS",24:"RTS",25:"RXD",26:"TXD",27:"DSR",28:"DTR",29:"GND"}
BQ4050 = {1: "PBI", 2: "VC4", 3: "VC3", 4: "VC2", 5: "VC1", 6: "SRN", 7: "NC", 8: "SRP", 9: "VSS", 10: "TS1", 11: "TS2", 12: "TS3", 13: "TS4", 14: "NC", 15: "BTP_INT", 16: "PRES",
          17: "DISP", 18: "SMBD", 19: "SMBC", 20: "LEDCNTLA", 21: "LEDCNTLB", 22: "LEDCNTLC", 23: "PTC", 24: "PTCEN", 25: "FUSE", 26: "VCC", 27: "PACK", 28: "DSG", 29: "NC", 30: "PCHG", 31: "CHG", 32: "BAT", 33: "PAD"}   # SLUSC67B pin table, RSM package, 33 = the thermal pad
SYNTH = {"SA868": SA868, "PCM2912A": PCM2912A, "TPA6132A2": TPA6132A2, "TUSB2046B": TUSB2046B, "CP2102N": CP2102, "BQ4050": BQ4050}
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
 "R": "Resistor_SMD:R_0603_1608Metric", "R2010": "Resistor_SMD:R_2010_5025Metric", "C": "Capacitor_SMD:C_0603_1608Metric", "C0402": "Capacitor_SMD:C_0402_1005Metric",
 "C10u": "Capacitor_SMD:C_0805_2012Metric", "C1206": "Capacitor_SMD:C_1206_3216Metric", "C1210": "Capacitor_SMD:C_1210_3225Metric", "LED": "LED_SMD:LED_0603_1608Metric",
 "SOT23": "Package_TO_SOT_SMD:SOT-23", "SOT235": "Package_TO_SOT_SMD:SOT-23-5", "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "WSON6": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
 "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "IDC16": "Connector_IDC:IDC-Header_2x08_P2.54mm_Vertical",
 "TP": "TestPoint:TestPoint_Pad_D1.5mm", "QFN28": "Package_DFN_QFN:QFN-28-1EP_5x5mm_P0.5mm_EP3.35x3.35mm", "TQFP32": "Package_QFP:TQFP-32_7x7mm_P0.8mm", "LQFP32": "Package_QFP:LQFP-32_7x7mm_P0.8mm",
 "QFN16": "Package_DFN_QFN:QFN-16-1EP_3x3mm_P0.5mm_EP1.75x1.75mm", "VSSOP8": "Package_SO:VSSOP-8_3x3mm_P0.65mm", "TSSOP24": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm",
 "SA868": "meshsat:NiceRF_SA868", "RELAY": "Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y", "SMA": "Connector_Coaxial:SMA_Amphenol_132134_Vertical", "UFL": "Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical",
 "L1812": "Inductor_SMD:L_1812_4532Metric", "FB": "Inductor_SMD:L_0805_2012Metric", "SOD123": "Diode_SMD:D_SOD-123", "SMB": "Diode_SMD:D_SMB",
 "PH2": "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", "PH4": "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical", "PH5": "Connector_JST:JST_PH_B5B-PH-K_1x05_P2.00mm_Vertical",
 "JP": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",
 "QFN32": "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm", "PPAK": "Package_SO:PowerPAK_SO-8_Single", "RS2512": "Resistor_SMD:R_2512_6332Metric",
 "FUSE": "Fuse:Fuseholder_Blade_Mini_Keystone_3568", "XH5": "Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical", "XH4": "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
 "WIRE": "Connector_Wire:SolderWire-2.5sqmm_1x01_D2.4mm_OD3.6mm", "R1206": "Resistor_SMD:R_1206_3216Metric",
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
def cp2102(uref, tag, vusb, dp, dm, txd, rxd, rts="NC", dtr="NC", refs=()):
    """CP2102N-A02-GQFN28 bridge: bus sense and regulator input from the slot rail whose hub carries it, its own 3.3 V out (VDD) bypassed, RSTb pulled to VDD."""
    synth(uref, "CP2102N", "CP2102N-A02-GQFN28 USB-UART bridge (%s)" % tag, "QFN28", {3: "GND", 29: "GND", 4: dp, 5: dm, 6: tag + "_3V3", 7: vusb, 8: vusb, 9: tag + "_RST", 25: rxd, 26: txd, 24: rts, 28: dtr}, "C964632")
    rr, c1, c2 = refs
    r(rr, "1k", tag + "_RST", tag + "_3V3"); c(c1, "4.7u", tag + "_3V3", "GND", "C10u"); c(c2, "100n", tag + "_3V3", "GND")


# ================================================================= the design (nets are root-sheet labels; GND = the cell block's negative, the only power symbol)
def pfet5(ref, value, g, d, sv, lcsc=""): part(ref, "Connector_Generic", "Conn_01x05", value, "PPAK", {"1": sv, "2": sv, "3": sv, "4": g, "5": d}, lcsc)   # PowerPAK SO-8: 1-3 source, 4 gate, 5 the drain tab (A22 lesson, 32.57)
# --- cell taps, the gauge and its filters
part("J_CELL", "Connector_Generic", "Conn_01x05", "cell tap sense wires from the 4S block (JST-XH 1x5): B- C1 C2 C3 B+; the current leaves through W_BP and W_BN", "XH5", {"1": "GND", "2": "CELL1", "3": "CELL2", "4": "CELL3", "5": "CELL4"})
synth("U1", "BQ4050", "BQ4050RSMR: SMBus 1.1 gas gauge, primary protection, 4S balancing (SLUSC67B)", "QFN32", {
 1: "PBI", 2: "VC4_F", 3: "VC3_F", 4: "VC2_F", 5: "VC1_F", 6: "SRN_F", 7: "GND", 8: "SRP_F", 9: "GND", 10: "TS1", 11: "TS2", 12: "TS3", 13: "TS4", 14: "GND", 15: "BTP_INT", 16: "PRES",
 17: "DISP", 18: "SMBD_I", 19: "SMBC_I", 20: "NC", 21: "NC", 22: "NC", 23: "GND", 24: "GND", 25: "FUSE", 26: "VCC_F", 27: "PACK_F", 28: "DSG_G", 29: "GND", 30: "NC", 31: "CHG_G", 32: "BAT_F", 33: "GND"}, "C157570")
c("C1", "2.2u", "PBI", "GND", "C10u")                                                                       # the backup supply capacitor on PBI
for k in (1, 2, 3, 4): r("R%d" % k, "100R", "CELL%d" % k, "VC%d_F" % k); c("C%d" % (k + 1), "100n", "VC%d_F" % k, "GND")   # cell sense filters (R1..R4, C2..C5)
r("R5", "100R", "CELL4", "BAT_F"); c("C6", "100n", "BAT_F", "GND")                                             # BAT, the primary supply
r("R6", "1k", "PACK_P", "PACK_F"); c("C7", "100n", "PACK_F", "GND")                                             # PACK sense
r("R7", "1k", "PACK_P", "VCC_F"); c("C8", "100n", "VCC_F", "GND")                                               # VCC, the secondary supply from the pack terminal (wakes a shut-down pack from the charger)
r("R8", "100R", "GND", "SRP_F"); r("R9", "100R", "PACK_N", "SRN_F"); c("C9", "100n", "SRP_F", "SRN_F")          # the coulomb counter across the sense resistor
r("R10", "2m 2512 2W (sense)", "GND", "PACK_N", "RS2512")                                                       # 25 A gives 50 mV, inside the counter's range
part("J_TS", "Connector_Generic", "Conn_01x02", "cell thermistor (JST-PH 1x2): the 103AT in the block", "PH2", {"1": "TS1", "2": "GND"}); c("C10", "100n", "TS1", "GND")
for k, n in ((11, "TS2"), (12, "TS3"), (13, "TS4")): r("R%d" % k, "10k", n, "GND")                             # unused thermistor inputs held valid
r("R14", "10k", "PRES", "GND"); r("R15", "10k", "DISP", "GND")                                                  # embedded pack: present; no LED display
# --- the high-side protection: fuse, charge FET, discharge FET (common drain), gate networks
part("F1", "Device", "Fuse", "25 A mini blade (Keystone 3568 holder): the pack's fuse", "FUSE", {"1": "CELL4", "2": "FUSED"})
pfet5("Q1", "CSD17570Q5B 30 V N-FET, charge switch", "CHG_G", "SW", "FUSED", "C2825431"); pfet5("Q2", "CSD17570Q5B 30 V N-FET, discharge switch", "DSG_G", "SW", "PACK_P", "C2825431")
r("R16", "5.1k", "CHG_G", "CHG_R"); r("R17", "10M", "CHG_G", "FUSED"); r("R18", "5.1k", "DSG_G", "DSG_R"); r("R19", "10M", "DSG_G", "PACK_P")
# the gauge drives the gates through the 5.1k: rename the gauge pins onto the resistor side
for p_ in P:
    if p_["ref"] == "U1": p_["nets"]["31"] = "CHG_R"; p_["nets"]["28"] = "DSG_R"
c("C11", "100n 50V", "PACK_P", "PACK_N"); c("C12", "100n 50V", "PACK_P", "PACK_N", "C1206")                     # ESD across the terminals
part("D1", "Device", "D_TVS", "SMBJ20A", "SMB", {"1": "PACK_N", "2": "PACK_P"})
part("W_P", "Connector", "Conn_01x01_Pin", "pack lead + (12 AWG to the XT60 on E6 J_BATT pin 2)", "WIRE", {"1": "PACK_P"})
part("W_N", "Connector", "Conn_01x01_Pin", "pack lead - (12 AWG to the XT60 on E6 J_BATT pin 1)", "WIRE", {"1": "PACK_N"})
part("W_BP", "Connector", "Conn_01x01_Pin", "cell block B+ (12 AWG from the block's positive strip)", "WIRE", {"1": "CELL4"})
part("W_BN", "Connector", "Conn_01x01_Pin", "cell block B- (12 AWG from the block's negative strip)", "WIRE", {"1": "GND"})
# --- SMBus out, test points, flags
r("R20", "100R", "SMBC_I", "SMBC"); r("R21", "100R", "SMBD_I", "SMBD")
part("D2", "Power_Protection", "USBLC6-2SC6", "USBLC6-2SC6 ESD clamp on the SMBus pair", "SOT236", {"1": "SMBC", "6": "SMBC", "3": "SMBD", "4": "SMBD", "5": "VCC_F", "2": "GND"}, "C7519")
part("J_SMB", "Connector_Generic", "Conn_01x04", "SMBus lead to E6 J_SMB (JST-XH 1x4): SMBC SMBD GND PRES", "XH4", {"1": "SMBC", "2": "SMBD", "3": "GND", "4": "PRES"})
for i, net in enumerate(("BTP_INT", "FUSE", "CHG_R", "DSG_R", "SW", "FUSED", "PACK_P", "PACK_N", "SMBC", "SMBD"), 1): part("TP%d" % i, "Connector", "TestPoint", net, "TP", {"1": net})
for i, net in enumerate(("CELL4", "CELL1", "CELL2", "CELL3", "PACK_P", "PACK_N", "FUSED", "SW", "GND"), 1): part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})
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
SECTIONS = [("CELL TAPS, GAUGE BQ4050, SENSE AND SUPPLY FILTERS, THERMISTOR", ["J_CELL", "U1", "C1"] + ["R%d" % k for k in range(1, 10)] + ["C%d" % k for k in range(2, 11)] + ["R10", "J_TS", "R11", "R12", "R13", "R14", "R15"]),
            ("FUSE, PROTECTION FETS, GATE NETWORKS, TERMINAL ESD, PACK LEADS", ["W_BP", "W_BN", "F1", "Q1", "Q2", "R16", "R17", "R18", "R19", "C11", "C12", "D1", "W_P", "W_N"]),
           ]
placed_refs = {r_ for _, rs in SECTIONS for r_ in rs}
SECTIONS.append(("SMBUS OUT, TEST POINTS, FLAGS", [p["ref"] for p in P if p["ref"] not in placed_refs]))
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
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-P PACK BMS") (date "2026-09-07") (rev "A") (company "MeshSat") (comment 1 "Phase P1 schematic (BQ4050 SMBus gauge and protection for the built 4S pack; appendix 32.62), generated by tools/gen_sch_p.py"))\n'
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
_intent.write(OUT, PROJECT, P)   # 8 Sep 2026 (MESHSAT-862): design intent as data, out/<project>-intent.json
