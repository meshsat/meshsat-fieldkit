#!/usr/bin/env python3
"""PCB-E1 DOCK, phase E1: generate the KiCad 9 schematic (netlist-style: every pin gets a
stub and a net label; power pins get power symbols). Runs on the laptop (needs the KiCad libs).
Usage: gen_sch_e.py <out.kicad_sch> <project-name>
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-e1-dock"
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
 "R": "Resistor_SMD:R_0603_1608Metric", "C": "Capacitor_SMD:C_0603_1608Metric", "C10u50": "Capacitor_SMD:C_1206_3216Metric", "LED": "LED_SMD:LED_0603_1608Metric",
 "TVS": "Diode_SMD:D_SMC", "SO8": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "SOT23": "Package_TO_SOT_SMD:SOT-23", "SOD123": "Diode_SMD:D_SOD-123",
 "FUSE": "Fuse:Fuseholder_Blade_Mini_Keystone_3568", "BUCK": "Converter_DCDC:Converter_DCDC_TRACO_TEN40-110xxWIRH_THT", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "OPTO": "Package_SO:SOP-4_3.8x4.1mm_P2.54mm",
 "POGO_T": "meshsat:PogoTargets_2x4", "POGO_T6": "meshsat:PogoTargets_2x6", "TP": "TestPoint:TestPoint_Pad_D1.5mm", "TDSON8": "Package_TO_SOT_SMD:TDSON-8-1", "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "QFN38": "Package_DFN_QFN:WQFN-38-1EP_5x7mm_P0.5mm_EP3.15x5.15mm", "L1510": "Inductor_SMD:L_Coilcraft_XAL1510-103", "RS2512": "Resistor_SMD:R_2512_6332Metric", "CPOL63": "Capacitor_SMD:CP_Elec_6.3x7.7", "CPOL8": "Capacitor_SMD:CP_Elec_8x6.7", "XT60": "Connector_AMASS:AMASS_XT60-M_1x02_P7.20mm_Vertical", "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "PAD86": "meshsat:SolderPad_8x6",
}
P = []
def part(ref, lib, sym, value, fp, nets, lcsc=""):
    P.append(dict(ref=ref, lib=lib, sym=sym, value=value, fp=FP.get(fp, fp), nets=nets, lcsc=lcsc))
def r(ref, val, a, b, fp="R", lcsc=""): part(ref, "Device", "R", val, fp, {"1": a, "2": b}, lcsc)
def c(ref, val, a, b, fp="C", lcsc=""): part(ref, "Device", "C", val, fp, {"1": a, "2": b}, lcsc)
def tp(ref, net): part(ref, "Connector", "TestPoint", net, "TP", {"1": net})
# ================================================================ E4 (appendix 32.13 to 32.25, MESHSAT-790): the dock strip carries the shore entry,
# the panel tracker stage, the battery module's current to the raised contact block, and the float clamps of the seven blind-mate plugs (no RF copper).
# Two ground domains: DC_N is the isolated shore/panel side (the TEN 40's -Vin); GND is the kit side (the module return is its own net CELL_N, 32.24 AZ).
# --- shore entry: 38999 DC pair (lead) -> J_DCIN -> F1 7.5 A mini blade -> LM74700 ideal diode (U3 + Q1, reverse-polarity and ORing) -> DC_P -> TEN 40
part("J_DCIN", "Connector_Generic", "Conn_01x02", "shore DC in 9-36 V, lead from the D38999/20FC4PN wall receptacle DC pair (JST-VH, 10 A): + -", "VH2", {"1": "DC_IN", "2": "DC_N"})
part("F1", "Device", "Fuse", "7.5 A mini blade (Keystone 3568 holder, in the clear band): 3.7 A at 12 V full load, 5 A at 9 V", "FUSE", {"1": "DC_IN", "2": "DC_F"})
def ideal_diode(uref, qref, cref, rref, anode, cathode, gnd):
    """LM74700-Q1 (lm74700.pdf, SOT-23-6: 1 VCAP, 2 GND, 3 EN, 4 CATHODE, 5 GATE, 6 ANODE) driving an N-FET (source at the anode, drain at the cathode)"""
    part(uref, "Connector_Generic", "Conn_01x06", "LM74700-Q1 ideal-diode controller: 1 VCAP 2 GND 3 EN 4 CATHODE 5 GATE 6 ANODE", "SOT236", {"1": uref + "_VCAP", "2": gnd, "3": anode, "4": cathode, "5": qref + "_G", "6": anode}, "C2760636")
    part(qref, "Transistor_FET", "IRF7404", "BSC039N06NS 60 V 3.9 mOhm N-FET (PG-TDSON-8: 1-3 S, 4 G, 5-8 D)", "TDSON8", {"1": anode, "2": anode, "3": anode, "4": qref + "_G", "5": cathode, "6": cathode, "7": cathode, "8": cathode}, "C534330")
    c(cref, "100n 50V", uref + "_VCAP", anode, "C", "C14663"); r(rref, "100k", qref + "_G", anode, "R", "C25803")
ideal_diode("U3", "Q1", "C4", "R1", "DC_F", "DC_P", "DC_N")
part("D1", "Device", "D_TVS", "SMCJ33A (input surge, datasheet 50 V 100 ms)", "TVS", {"1": "DC_N", "2": "DC_P"})
c("C1", "10u 50V", "DC_P", "DC_N", "C10u50"); c("C2", "100n", "DC_P", "DC_N", "C", "C14663")
part("U1", "Connector_Generic", "Conn_01x06", "TRACO TEN 40-2412WIN: isolated 9-36 V in, 12 V 3.33 A out, -40..+75 C, 10.2 mm tall under the 13.4 mm gap. Pins 1 +Vin, 2 -Vin, 3 remote (open = on), 4 +Vout, 5 -Vout, 6 trim", "BUCK", {"1": "DC_P", "2": "DC_N", "3": "REMOTE", "4": "SHORE_12V", "5": "GND", "6": "NC"})
c("C3", "22u 25V", "SHORE_12V", "GND", "C10u50"); part("D3", "Device", "D_TVS", "SMCJ15A", "TVS", {"1": "GND", "2": "SHORE_12V"})   # the land is D_SMC (DO-214AB) like the two SMCJ33A parts; SMBJ is the smaller SMB body
r("R2", "2.2k", "SHORE_12V", "LED_A", "R", "C4190"); part("LED1", "Device", "LED", "green: shore 12 V present", "LED", {"2": "LED_A", "1": "GND"})
r("R3", "330R", "SHORE_INHIBIT", "OPTO_A"); r("R4", "100k", "SHORE_INHIBIT", "GND")
part("U2", "Isolator", "PC817", "EL817S / PC817 optocoupler: LED from PCB-A SHORE_INHIBIT (kit side), transistor shorts the converter remote pin to -Vin (isolated side); LED on = converter OFF, LED off or Pi dead = ON", "OPTO", {"1": "OPTO_A", "2": "GND", "3": "DC_N", "4": "REMOTE"})
# --- panel tracker stage (lt8705a.pdf, respin-research-power item 5): LT8705A buck-boost, input regulated at the panel's maximum-power voltage (FBIN 17.6 V),
#     output 15.1 V into the converter input through a second ideal diode; 202 kHz; every part under 12 mm (32.19 AO)
part("J_SOLAR", "Connector_Generic", "Conn_01x02", "bare 12 V class panel in, lead from the D38999 spare pair (JST-VH, 10 A): + - (36-cell panel, up to about 22 V open circuit, 100 W)", "VH2", {"1": "PV_IN", "2": "DC_N"})
part("F2", "Device", "Fuse", "10 A mini blade (Keystone 3568 holder, in the clear band): panel input", "FUSE", {"1": "PV_IN", "2": "PV_P"})
part("D4", "Device", "D_TVS", "SMCJ33A (panel surge)", "TVS", {"1": "DC_N", "2": "PV_P"})
for k in range(1, 3): part("C%d" % (10 + k), "Device", "C_Polarized", "100u 35V Panasonic EEHZK1V101XP hybrid polymer (7.7 mm)", "CPOL63", {"1": "PV_P", "2": "DC_N"}, "C454360")
c("C13", "10u 50V", "PV_P", "DC_N", "C10u50"); c("C14", "10u 50V", "PV_P", "DC_N", "C10u50"); c("C15", "4.7u 50V", "PV_P", "DC_N", "C10u50")
part("U5", "Connector_Generic", "Conn_02x20_Odd_Even", "LT8705A buck-boost controller, 38-lead QFN 5x7 (pin 39 = exposed pad GND, pin 40 unused)", "QFN38", {
 "1": "TRK_SHDN", "2": "TRK_CSN", "3": "TRK_CSP", "4": "TRK_LDO33", "5": "TRK_FBIN", "6": "TRK_FBOUT", "7": "TRK_IMONO", "8": "TRK_VC", "9": "TRK_SS", "10": "NC", "11": "DC_N", "12": "TRK_RT", "13": "DC_N",
 "14": "TRK_BG1", "15": "TRK_INTVCC", "16": "TRK_BG2", "17": "TRK_BOOST2", "18": "TRK_TG2", "19": "TRK_SW2", "20": "NC", "21": "TRK_SW1", "22": "TRK_TG1", "23": "TRK_BOOST1", "24": "NC",
 "25": "NC", "26": "NC", "27": "NC", "28": "NC", "29": "TRK_OUT", "30": "TRK_OUT", "31": "TRK_OUT", "32": "PV_P", "33": "PV_P", "34": "PV_P", "35": "TRK_INTVCC", "36": "TRK_INTVCC", "37": "DC_N", "38": "TRK_IMONI", "39": "DC_N", "40": "NC"}, "C674167")
# gate drivers: M1 TG1 (PV_P to SW1), M2 BG1 (SW1 to DC_N), M3 BG2 (SW2 to DC_N), M4 TG2 (SW2 to TRK_OUT); inductor and RSENSE between SW1 and SW2
part("Q3", "Transistor_FET", "IRF7404", "BSC028N06NS 60 V 2.8 mOhm N-FET, M1 buck top (TDSON-8: 1-3 S, 4 G, 5-8 D)", "TDSON8", {"1": "TRK_SW1", "2": "TRK_SW1", "3": "TRK_SW1", "4": "TRK_TG1", "5": "PV_P", "6": "PV_P", "7": "PV_P", "8": "PV_P"}, "C148250")
part("Q4", "Transistor_FET", "IRF7404", "BSC039N06NS 60 V N-FET, M2 buck bottom", "TDSON8", {"1": "DC_N", "2": "DC_N", "3": "DC_N", "4": "TRK_BG1", "5": "TRK_SW1", "6": "TRK_SW1", "7": "TRK_SW1", "8": "TRK_SW1"}, "C534330")
part("Q5", "Transistor_FET", "IRF7404", "BSC028N06NS 60 V N-FET, M3 boost bottom", "TDSON8", {"1": "DC_N", "2": "DC_N", "3": "DC_N", "4": "TRK_BG2", "5": "TRK_SW2", "6": "TRK_SW2", "7": "TRK_SW2", "8": "TRK_SW2"}, "C148250")
part("Q6", "Transistor_FET", "IRF7404", "BSC039N06NS 60 V N-FET, M4 boost top", "TDSON8", {"1": "TRK_SW2", "2": "TRK_SW2", "3": "TRK_SW2", "4": "TRK_TG2", "5": "TRK_OUT", "6": "TRK_OUT", "7": "TRK_OUT", "8": "TRK_OUT"}, "C534330")
part("L1", "Device", "L", "10uH Coilcraft XAL1510-103MED (Isat 26 A, 10.0 mm tall)", "L1510", {"1": "TRK_SW1", "2": "TRK_LSENSE"}, "C3911782")
part("R5", "Device", "R", "5 mOhm 1% 3 W 2512 RSENSE (RALEC LR2512-23R005F4)", "RS2512", {"1": "TRK_LSENSE", "2": "TRK_SW2"}, "C154688")
r("R6", "100R", "TRK_LSENSE", "TRK_CSP"); r("R7", "100R", "TRK_SW2", "TRK_CSN"); c("C16", "1n", "TRK_CSP", "TRK_CSN")
c("C17", "470n 25V", "TRK_BOOST1", "TRK_SW1"); c("C18", "470n 25V", "TRK_BOOST2", "TRK_SW2")
part("D5", "Device", "D_Schottky", "BAT54 boost diode INTVCC -> BOOST1", "SOD123", {"1": "TRK_BOOST1", "2": "TRK_INTVCC"}); part("D6", "Device", "D_Schottky", "BAT54 boost diode INTVCC -> BOOST2", "SOD123", {"1": "TRK_BOOST2", "2": "TRK_INTVCC"})
c("C19", "4.7u 25V", "TRK_INTVCC", "DC_N", "C10u50"); c("C20", "1u", "TRK_LDO33", "DC_N")
r("R8", "102k 1% (RFBIN1: panel point 17.6 V)", "PV_P", "TRK_FBIN"); r("R9", "7.50k 1% (RFBIN2)", "TRK_FBIN", "DC_N")
r("R10", "115k 1% (RFBOUT1: 15.1 V)", "TRK_OUT", "TRK_FBOUT"); r("R11", "10.0k 1% (RFBOUT2)", "TRK_FBOUT", "DC_N")
r("R12", "215k 1% (RT: 202 kHz)", "TRK_RT", "DC_N"); r("R13", "10k", "TRK_VC", "TRK_VCC1"); c("C21", "4.7n", "TRK_VCC1", "DC_N"); c("C22", "100p", "TRK_VC", "DC_N"); c("C23", "100n", "TRK_SS", "DC_N")
r("R14", "100k 1%", "PV_P", "TRK_SHDN"); r("R15", "15.0k 1% (SHDN: enable above about 9.5 V)", "TRK_SHDN", "DC_N")
r("R16", "10k", "TRK_IMONI", "DC_N"); r("R17", "10k", "TRK_IMONO", "DC_N")   # current loops unused: sense pins tied to their rails above, monitor pins loaded
for k in range(1, 3): part("C%d" % (23 + k), "Device", "C_Polarized", "39u 35V Panasonic 35SVPF39M polymer (6.9 mm)", "CPOL8", {"1": "TRK_OUT", "2": "DC_N"}, "C189474")
c("C26", "10u 25V", "TRK_OUT", "DC_N", "C10u50"); c("C27", "10u 25V", "TRK_OUT", "DC_N", "C10u50")
ideal_diode("U4", "Q2", "C28", "R18", "TRK_OUT", "DC_P", "DC_N")   # tracker output ORed into the converter input (32.15 F)
# --- battery module entry and the raised contact block (32.22, 32.25): the module's XT60 lead lands here, its current runs on heavy copper to the block
part("J_BATT", "Connector_Generic", "Conn_01x02", "battery module lead (XT60-M, 60 A): + - ; fused 40 A at the module; the return is its own net", "XT60", {"1": "CELL_P_MOD", "2": "CELL_N_MOD"})
part("J_TS", "Connector_Generic", "Conn_01x02", "module thermistor lead (XH2.5): 103AT to the charger TS pin over the block", "XH2", {"1": "TS_MOD", "2": "GND"})
part("J_KS", "Connector_Generic", "Conn_01x02", "Kelvin sense lead from the module positive terminal (XH2.5): + (return unused)", "XH2", {"1": "CELL_SENSE_P", "2": "NC"})
part("J_BLK", "Connector_Generic", "Conn_01x12", "solder lands for the 12 signal wires to the block board underside (mirror of PCB-A J_DOCK): 1-4 SHORE_12V, 5-7 GND, 8 SHORE_INHIBIT, 9 TS_MOD, 10 GND, 11 CELL_SENSE_P, 12 spare", "POGO_T6",
     {"1": "SHORE_12V", "2": "SHORE_12V", "3": "SHORE_12V", "4": "SHORE_12V", "5": "GND", "6": "GND", "7": "GND", "8": "SHORE_INHIBIT", "9": "TS_MOD", "10": "GND", "11": "CELL_SENSE_P", "12": "BLK_SPARE"})
part("P_CP", "Connector", "Conn_01x01_Pin", "solder pad, 12 AWG wire to the block board CELL+ targets", "PAD86", {"1": "CELL_P_MOD"})
part("P_CN", "Connector", "Conn_01x01_Pin", "solder pad, 12 AWG wire to the block board return targets", "PAD86", {"1": "CELL_N_MOD"})
tp("TP1", "DC_IN"); tp("TP2", "DC_P"); tp("TP3", "SHORE_12V"); tp("TP4", "GND"); tp("TP5", "PV_P"); tp("TP6", "TRK_OUT"); tp("TP7", "BLK_SPARE"); tp("TP8", "CELL_P_MOD"); tp("TP9", "CELL_N_MOD")
for i, net in enumerate(("DC_IN", "DC_N", "GND", "SHORE_12V", "PV_IN", "PV_P", "TRK_OUT", "DC_P", "DC_F", "CELL_P_MOD", "CELL_N_MOD", "TRK_INTVCC", "TRK_LDO33"), 1): part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})
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
SECTIONS = [("SHORE ENTRY: 38999 DC PAIR, F1, LM74700 IDEAL DIODE, SURGE, TEN 40WIN 12 V 40 W, OPTO INHIBIT", ["J_DCIN", "F1", "U3", "Q1", "C4", "R1", "D1", "C1", "C2", "U1", "C3", "D3", "R2", "LED1", "R3", "R4", "U2"]),
            ("PANEL TRACKER: J_SOLAR, F2, LT8705A BUCK-BOOST (FBIN 17.6 V, FBOUT 15.1 V, 202 kHz), ORed INTO THE CONVERTER INPUT", ["J_SOLAR", "F2", "D4", "C11", "C12", "C13", "C14", "C15", "U5", "Q3", "Q4", "Q5", "Q6", "L1", "R5", "R6", "R7", "C16", "C17", "C18", "D5", "D6", "C19", "C20", "R8", "R9", "R10", "R11", "R12", "R13", "C21", "C22", "C23", "R14", "R15", "R16", "R17", "C24", "C25", "C26", "C27", "U4", "Q2", "C28", "R18"]),
            ("BATTERY MODULE ENTRY, THERMISTOR AND KELVIN LEADS, BLOCK LANDS, TEST POINTS, FLAGS", ["J_BATT", "J_TS", "J_KS", "J_BLK", "P_CP", "P_CN"] + ["TP%d" % k for k in range(1, 10)] + ["#FLG%02d" % k for k in range(1, 14)])]
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
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-E1 DOCK") (date "2026-09-02") (rev "A (E4)") (company "MeshSat") (comment 1 "Phase E1 schematic, generated by tools/gen_sch_e.py. Netlist style: every pin carries a stub and a net label.") (comment 2 "MESHSAT-709. FE1.1s hub on internal regulators; TPS2065C x2 + TPS22810 x4 switches (B4: LoRa and RockBLOCK channels at 2 A for the T-Beam 1W and 9704 bursts); INA219 per channel; PCA9555 EN/FAULT; both Pi UARTs to the RockBLOCK site via JP3/JP4."))\n'
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
