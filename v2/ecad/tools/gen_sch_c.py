#!/usr/bin/env python3
"""PCB-C CONTROL PANEL, phase C3: generate the KiCad 9 schematic (netlist-style: every pin gets a
stub and a net label; power pins get power symbols). Runs on the laptop (needs the KiCad libs).
Usage: gen_sch_c.py <out.kicad_sch> <project-name>
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-c-display"
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
 "R": "Resistor_SMD:R_0603_1608Metric", "C": "Capacitor_SMD:C_0603_1608Metric", "C10u": "Capacitor_SMD:C_0805_2012Metric",
 "LED3": "LED_THT:LED_D3.0mm", "EXP": "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", "SOT23": "Package_TO_SOT_SMD:SOT-23", "SOT236": "Package_TO_SOT_SMD:SOT-23-6",
 "SOD123": "Diode_SMD:D_SOD-123", "FB": "Inductor_SMD:L_0603_1608Metric", "JP2": "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm", "TP": "TestPoint:TestPoint_Pad_D1.5mm",
 "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "IDC20": "Connector_IDC:IDC-Header_2x10_P2.54mm_Vertical", "HDR8": "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical",
 "SW19": "meshsat:PanelSwitch_19mm", "SW16": "meshsat:PanelSwitch_16mm", "TGL6": "meshsat:PanelToggle_DPDT", "TGL3": "meshsat:GuardedToggle_SPDT",
 "BZ": "Buzzer_Beeper:Buzzer_12x9.5RM7.6", "MHPAD": "MountingHole:MountingHole_3.2mm_M3_Pad",
}
P = []   # (ref, lib, symbol, value, footprint, nets{pin: net}, lcsc)
def part(ref, lib, sym, value, fp, nets, lcsc=""):
    P.append(dict(ref=ref, lib=lib, sym=sym, value=value, fp=FP.get(fp, fp), nets=nets, lcsc=lcsc))
def r(ref, val, a, b, fp="R", lcsc=""): part(ref, "Device", "R", val, fp, {"1": a, "2": b}, lcsc)
def c(ref, val, a, b, fp="C", lcsc=""): part(ref, "Device", "C", val, fp, {"1": a, "2": b}, lcsc)
def esd(ref, la, lb, vbus): part(ref, "Power_Protection", "USBLC6-2SC6", "USBLC6-2SC6 (2-line TVS)", "SOT236", {"1": la, "6": la, "3": lb, "4": lb, "5": vbus, "2": "GND"}, "C7519")
def nfet(ref, g, s, d, value="2N7002"): part(ref, "Transistor_FET", "2N7002", value, "SOT23", {"1": g, "2": s, "3": d}, "C8545")
def led(ref, colour, a, k): part(ref, "Device", "LED", "3 mm %s, sunlight viewable" % colour, "LED3", {"2": a, "1": k})
def tp(ref, net): part(ref, "Connector", "TestPoint", net, "TP", {"1": net})

# --- ribbon from PCB-B (J_PANEL on B has the same pin map), power entry
part("J_PANEL", "Connector_Generic", "Conn_02x10_Odd_Even", "panel ribbon from PCB-B (IDC 2x10, underside)", "IDC20", {
 "1": "+5V", "2": "+5V", "3": "GND", "4": "SDA", "5": "SCL", "6": "EXP_INT", "7": "TR_APRS", "8": "EPD_DC", "9": "GND", "10": "SPI_SCLK",
 "11": "GND", "12": "SPI_MOSI", "13": "GND", "14": "SPI_CE0", "15": "EPD_RES_ALT", "16": "PWM1", "17": "PANEL_PWM", "18": "GND", "19": "TX_INHIBIT_n", "20": "+3V3"})
c("C1", "10u", "+5V", "GND", "C10u", "C15850"); c("C2", "10u", "+3V3", "GND", "C10u", "C15850")
esd("U5", "SPI_SCLK", "SPI_MOSI", "+3V3"); esd("U6", "SPI_CE0", "EPD_DC", "+3V3"); esd("U7", "SDA", "SCL", "+3V3"); esd("U8", "PANEL_PWM", "PWM1", "+3V3")
for i in range(1, 6): part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": ["+5V", "+3V3", "GND", "LED_RAIL_SW", "LED_RAIL"][i - 1]})

# --- I2C expanders: U1 0x22 (A1 high), U2 0x23 (A1 + A0 high). Port 0 = LED sinks (open-drain by configuration), port 1 = inputs / misc
part("U1", "Interface_Expansion", "PCA9555PW", "PCA9555PW 0x22: LEDs + switches", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "2": "+3V3", "21": "GND", "3": "GND",
 "4": "SOSACT_K", "5": "MWARN_K", "6": "MCAUT_K", "7": "CHG_K", "8": "SAT_K", "9": "MESH_K", "10": "LTE_K", "11": "GPS_K",
 "13": "SOS_SW", "14": "TX_INHIBIT_n", "15": "ZEROIZE_SW", "16": "TEST_SW", "17": "LIGHT_DAY_n", "18": "LIGHT_NIGHT_n", "19": "RAIL_SENSE", "20": "PANEL_ID"}, "C50993")
part("U2", "Interface_Expansion", "PCA9555PW", "PCA9555PW 0x23: LEDs, bar, e-paper control", "EXP", {
 "24": "+3V3", "12": "GND", "22": "SCL", "23": "SDA", "1": "EXP_INT", "2": "+3V3", "21": "+3V3", "3": "GND",
 "4": "SHORE_K", "5": "MSG_K", "6": "PIRING_K", "7": "BAT1_K", "8": "BAT2_K", "9": "BAT3_K", "10": "BAT4_K", "11": "BAT5_K",
 "13": "TX_LAMPTEST", "14": "EPD_RES", "15": "EPD_BUSY", "16": "SPARE1", "17": "SPARE2", "18": "SPARE3", "19": "SPARE4", "20": "SPARE5"}, "C50993")
c("C3", "100n", "+3V3", "GND", "C", "C14663"); c("C4", "100n", "+3V3", "GND", "C", "C14663")
for i, net in enumerate(("SOS_SW", "ZEROIZE_SW", "TEST_SW", "LIGHT_DAY_n", "LIGHT_NIGHT_n"), 1):
    r("R%d" % i, "10k", net, "+3V3", "R", "C25804"); c("C%d" % (i + 4), "10n", net, "GND", "C", "C57112")
r("R6", "100k", "TX_INHIBIT_n", "+3V3", "R", "C25803"); c("C10", "10n", "TX_INHIBIT_n", "GND", "C", "C57112")
r("R7", "10k", "LED_RAIL_SW", "RAIL_SENSE", "R", "C25804"); r("R8", "10k", "PANEL_ID", "+3V3", "R", "C25804")
part("JP1", "Jumper", "SolderJumper_2_Open", "PANEL_ID strap (closed = variant B)", "JP2", {"1": "PANEL_ID", "2": "GND"})
part("JP2", "Jumper", "SolderJumper_2_Open", "EPD RES from BCM7 instead of U2 (close to use)", "JP2", {"1": "EPD_RES_ALT", "2": "EPD_RES"})

# --- LED rail: +5V -> LIGHTING toggle (open in BLACKOUT) -> LED_RAIL_SW -> Q1 P-FET (PWM from PANEL_PWM through Q2) -> LED_RAIL
part("SW_LIGHT", "Connector_Generic", "Conn_01x06", "LIGHTING DAY/NIGHT/BLACKOUT toggle DPDT ON-ON-ON (pole 1: rail, pole 2: sense)", "TGL6",
     {"1": "LED_RAIL_SW", "2": "+5V", "3": "NC", "4": "GND", "5": "LIGHT_DAY_n", "6": "LIGHT_NIGHT_n"})
part("Q1", "Transistor_FET", "AO3401A", "AO3401A P-FET high side", "SOT23", {"1": "Q1_G", "2": "LED_RAIL_SW", "3": "LED_RAIL"}, "C15127")
r("R9", "2.2k", "LED_RAIL_SW", "Q1_G", "R", "C4190"); r("R10", "47R", "Q1_G", "Q2_D", "R", "C25118")
nfet("Q2", "Q2_G", "GND", "Q2_D"); r("R11", "100R", "PANEL_PWM", "Q2_G", "R", "C22775"); r("R12", "100k", "Q2_G", "GND", "R", "C25803")
tp("TP1", "LED_RAIL"); tp("TP2", "LED_RAIL_SW")

# --- indicators (3 mm THT, anode from LED_RAIL through the series resistor, cathode to the expander sink; red/amber 300R, green/white 180R at 8 mA)
LEDS = [("D1", "MWARN", "red", "300R"), ("D2", "MCAUT", "amber", "300R"), ("D4", "SOSACT", "red", "300R"), ("D5", "SAT", "green", "180R"), ("D6", "MESH", "green", "180R"),
        ("D7", "LTE", "green", "180R"), ("D8", "GPS", "green", "180R"), ("D9", "SHORE", "green", "180R"), ("D10", "CHG", "white", "180R"), ("D11", "MSG", "white", "180R"),
        ("D12", "BAT1", "amber", "300R"), ("D13", "BAT2", "green", "180R"), ("D14", "BAT3", "green", "180R"), ("D15", "BAT4", "green", "180R"), ("D16", "BAT5", "green", "180R")]
rn = 13
for ref, name, colour, val in LEDS:
    r("R%d" % rn, val, "LED_RAIL", name + "_A", "R", "C23025" if val == "300R" else "C25270"); led(ref, "%s %s" % (name, colour), name + "_A", name + "_K"); rn += 1
# TX lamp: hardware from TR_APRS (the real PTT mirror after D5), lamp test through a BAT54 from U2
r("R%d" % rn, "300R", "LED_RAIL", "TX_A", "R", "C23025"); rn += 1; led("D3", "TX red (RF hazard)", "TX_A", "TX_K")
nfet("Q3", "Q3_G", "GND", "TX_K"); r("R%d" % rn, "1k", "TR_APRS", "Q3_G", "R", "C11702"); rn += 1; r("R%d" % rn, "100k", "Q3_G", "GND", "R", "C25803"); rn += 1
part("D17", "Device", "D_Schottky", "BAT54 lamp-test tie", "SOD123", {"2": "TX_K", "1": "TX_LAMPTEST"}, "C2166")

# --- switches (bench parts on flying leads; footprints = panel hole + lead pads)
part("SW_MAIN", "Connector_Generic", "Conn_01x04", "MAIN PWR 19 mm momentary, green ring (to X1202 external switch)", "SW19", {"1": "X1202SW_A", "2": "X1202SW_B", "3": "MAINRING_A", "4": "GND"})
r("R%d" % rn, "470R", "LED_RAIL_SW", "MAINRING_A", "R", "C23179"); rn += 1
part("SW_PI", "Connector_Generic", "Conn_01x04", "PI 16 mm recessed momentary, amber ring (to Pi 5 J2)", "SW16", {"1": "PIJ2_A", "2": "PIJ2_B", "3": "PIRING_A", "4": "PIRING_K"})
r("R%d" % rn, "300R", "LED_RAIL", "PIRING_A", "R", "C23025"); rn += 1
part("SW_TEST", "Connector_Generic", "Conn_01x04", "TEST/ACK 16 mm momentary, white ring", "SW16", {"1": "TEST_SW", "2": "GND", "3": "TESTRING_A", "4": "GND"})
r("R%d" % rn, "470R", "LED_RAIL", "TESTRING_A", "R", "C23179"); rn += 1
part("SW_SOS", "Connector_Generic", "Conn_01x03", "SOS guarded momentary toggle (red cover)", "TGL3", {"1": "SOS_SW", "2": "GND", "3": "NC"})
part("SW_EMCON", "Connector_Generic", "Conn_01x03", "EMCON guarded latching toggle (closed = TX inhibit)", "TGL3", {"1": "TX_INHIBIT_n", "2": "GND", "3": "NC"})
part("SW_ZERO", "Connector_Generic", "Conn_01x03", "ZEROIZE guarded momentary toggle (hold 5 s)", "TGL3", {"1": "ZEROIZE_SW", "2": "GND", "3": "NC"})
# power-button leads: ferrite + 100 nF at the panel end (the leads pass the antenna feeds)
part("FB1", "Device", "L", "ferrite 600R", "FB", {"1": "X1202SW_A", "2": "X1202SW_A2"}, "C1017"); part("FB2", "Device", "L", "ferrite 600R", "FB", {"1": "X1202SW_B", "2": "X1202SW_B2"}, "C1017")
c("C11", "100n", "X1202SW_A2", "X1202SW_B2", "C", "C14663")
part("J_X1202SW", "Connector_Generic", "Conn_01x02", "lead to the X1202 external-switch pins (XH2.5)", "XH2", {"1": "X1202SW_A2", "2": "X1202SW_B2"})
part("FB3", "Device", "L", "ferrite 600R", "FB", {"1": "PIJ2_A", "2": "PIJ2_A2"}, "C1017"); part("FB4", "Device", "L", "ferrite 600R", "FB", {"1": "PIJ2_B", "2": "PIJ2_B2"}, "C1017")
c("C12", "100n", "PIJ2_A2", "PIJ2_B2", "C", "C14663")
part("J_PIJ2", "Connector_Generic", "Conn_01x02", "lead to the Pi 5 J2 power-button pads (XH2.5)", "XH2", {"1": "PIJ2_A2", "2": "PIJ2_B2"})

# --- e-paper 3.7 in (module on standoffs, wired by an 8-way lead to J_EPD; 100R series on the Pi lines)
r("R%d" % rn, "100R", "SPI_SCLK", "EPD_SCL_F", "R", "C22775"); rn += 1; r("R%d" % rn, "100R", "SPI_MOSI", "EPD_SDA_F", "R", "C22775"); rn += 1
r("R%d" % rn, "100R", "SPI_CE0", "EPD_CS_F", "R", "C22775"); rn += 1; r("R%d" % rn, "100R", "EPD_DC", "EPD_DC_F", "R", "C22775"); rn += 1
part("J_EPD", "Connector_Generic", "Conn_01x08", "e-paper module lead: BUSY RES D/C CS SCL SDA GND VCC", "HDR8",
     {"1": "EPD_BUSY", "2": "EPD_RES", "3": "EPD_DC_F", "4": "EPD_CS_F", "5": "EPD_SCL_F", "6": "EPD_SDA_F", "7": "GND", "8": "+3V3"})
c("C13", "100n", "+3V3", "GND", "C", "C14663")

# --- sounder (85 dB active piezo on +5V, keyed by PWM1 through Q4; ACK mutes in software)
part("BZ1", "Device", "Buzzer", "active piezo 5 V 85 dB", "BZ", {"1": "BZ_K", "2": "+5V"})
nfet("Q4", "Q4_G", "GND", "BZ_K"); r("R%d" % rn, "100R", "PWM1", "Q4_G", "R", "C22775"); rn += 1; r("R%d" % rn, "100k", "Q4_G", "GND", "R", "C25803"); rn += 1

# --- chassis bond: the 16 frame screws through GND ring pads (MIL-STD-461 bonding of the aluminium frame)
for i in range(1, 17): part("H%d" % i, "Mechanical", "MountingHole_Pad", "frame screw M3, GND bond", "MHPAD", {"1": "GND"})
for i, net in enumerate(("+5V", "+3V3", "GND", "EXP_INT", "TX_INHIBIT_n", "SPARE1", "SPARE2", "SPARE3", "SPARE4", "SPARE5", "EPD_BUSY"), 3): tp("TP%d" % i, net)

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
SECTIONS = [("RIBBON FROM PCB-B, RAILS, TVS, TEST POINTS", ["J_PANEL", "C1", "C2", "U5", "U6", "U7", "U8", "#FLG01", "#FLG02", "#FLG03", "#FLG04", "#FLG05", "TP1", "TP2", "TP3", "TP4", "TP5", "TP6", "TP7"]),
            ("I2C EXPANDERS 0x22 / 0x23, SWITCH INPUTS, STRAPS", ["U1", "C3", "U2", "C4", "R1", "C5", "R2", "C6", "R3", "C7", "R4", "C8", "R5", "C9", "R6", "C10", "R7", "R8", "JP1", "JP2", "TP8", "TP9", "TP10", "TP11", "TP12", "TP13"]),
            ("LED RAIL: LIGHTING TOGGLE, PWM HIGH-SIDE SWITCH", ["SW_LIGHT", "Q1", "R9", "R10", "Q2", "R11", "R12"]),
            ("INDICATORS (MIL-STD-1472 COLOUR CODE) + BATTERY BAR", [x for pair in zip(["R%d" % (13 + i) for i in range(15)], [d for d, _, _, _ in LEDS]) for x in pair]),
            ("TX LAMP (HARDWARE FROM THE PTT MIRROR) + LAMP TEST", ["R28", "D3", "Q3", "R29", "R30", "D17"]),
            ("SWITCHES: MAIN PWR, PI, TEST/ACK, SOS, EMCON, ZEROIZE + POWER-BUTTON LEADS", ["SW_MAIN", "R31", "SW_PI", "R32", "SW_TEST", "R33", "SW_SOS", "SW_EMCON", "SW_ZERO", "FB1", "FB2", "C11", "J_X1202SW", "FB3", "FB4", "C12", "J_PIJ2"]),
            ("E-PAPER 3.7in LEAD + SOUNDER", ["R34", "R35", "R36", "R37", "J_EPD", "C13", "BZ1", "Q4", "R38", "R39"]),
            ("FRAME SCREWS, GND BOND", ["H%d" % i for i in range(1, 17)])]
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
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-C CONTROL PANEL") (date "2026-09-02") (rev "A") (company "MeshSat") (comment 1 "Phase C3 schematic, generated by tools/gen_sch_c.py. Netlist style: every pin carries a stub and a net label.") (comment 2 "MESHSAT-709. FE1.1s hub on internal regulators; TPS2065C x2 + TPS22810 x4 switches (B4: LoRa and RockBLOCK channels at 2 A for the T-Beam 1W and 9704 bursts); INA219 per channel; PCA9555 EN/FAULT; both Pi UARTs to the RockBLOCK site via JP3/JP4."))\n'
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
