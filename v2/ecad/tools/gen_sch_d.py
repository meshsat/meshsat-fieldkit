#!/usr/bin/env python3
"""PCB-D APRS BOARD, phase D2: generate the KiCad 9 schematic (netlist-style: every pin gets a
stub and a net label; power pins get power symbols). Runs on the laptop (needs the KiCad libs).
Usage: gen_sch_d.py <out.kicad_sch> <project-name>
"""
import re, sys, os, uuid
OUT = sys.argv[1]; PROJECT = sys.argv[2] if len(sys.argv) > 2 else "pcb-d-aprs"
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
 "SOT236": "Package_TO_SOT_SMD:SOT-23-6", "SOT235": "Package_TO_SOT_SMD:SOT-23-5", "SOT238": "Package_TO_SOT_SMD:SOT-23-8", "SOT23": "Package_TO_SOT_SMD:SOT-23",
 "WSON6": "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm", "XTAL": "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
 "XH2": "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "XH4": "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
 "IDC40": "Connector_IDC:IDC-Header_2x20_P2.54mm_Vertical", "IDC14": "Connector_IDC:IDC-Header_2x07_P2.54mm_Vertical", "IDC16": "Connector_IDC:IDC-Header_2x08_P2.54mm_Vertical",
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
def tps2065(ref, en, out, flt): part(ref, "Power_Management", "TPS2065CDBV", "TPS2065CDBV", "SOT235", {"5": "+5V", "4": en, "1": out, "3": flt, "2": "GND"})
def tps22810(ref, vin, en, out, ct): part(ref, "Power_Management", "TPS22810DRV", "TPS22810DRV", "WSON6", {"6": vin, "5": en, "1": out, "2": "NC", "3": ct, "4": "GND", "7": "GND"})
def ina219(ref, inp, inn, a0, a1): part(ref, "Sensor_Energy", "INA219AxDCN", "INA219AIDCN", "SOT238", {"1": inp, "2": inn, "3": "GND", "4": "+3V3", "5": "SCL", "6": "SDA", "7": a0, "8": a1}, "C138024")


FP.update({
 "QFN11": "Package_DFN_QFN:Texas_VQFN-RNR0011A-11", "LQFP48": "Package_QFP:LQFP-48_7x7mm_P0.5mm", "SOT235": "Package_TO_SOT_SMD:SOT-23-5",
 "SOT363": "Package_TO_SOT_SMD:SOT-363_SC-70-6", "XTAL5032": "Crystal:Crystal_SMD_5032-2Pin_5.0x3.2mm", "C1210": "Capacitor_SMD:C_1210_3225Metric",
 "L6030": "Inductor_SMD:L_Coilcraft_XAL6030-XXX", "VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "HDR7": "Connector_PinHeader_1.27mm:PinHeader_1x07_P1.27mm_Vertical",
 "HDR3": "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", "QFN32": "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm", "OSC3225": "Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm", "SOIC8": "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "TSSOP16": "Package_SO:TSSOP-16_4.4x5mm_P0.65mm", "PH2": "Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", "DMR": "meshsat:DMR858M", "FB": "Inductor_SMD:L_0603_1608Metric"})
# --- harness to PCB-A (mirror of A20's J_MEZZ1, appendix 32.35): 1 GND 2 +3V3_AB 3 I2S_BCLK 4 I2S_LRCLK 5 GND 6 I2S_DOUT 7 I2S_DIN 8 GND 9 SDA 10 TR_APRS 11 MEZZ_EN 12 +3V3 13 GND 14 SCL 15 TX_INHIBIT_n 16 GND
part("J_HARN1", "Connector_Generic", "Conn_02x08_Odd_Even", "harness to PCB-A J_MEZZ1 (IDC 2x8): I2S, I2C, the gated 3.3 V from B13, PTT lines", "IDC16",
     {"1": "GND", "2": "+3V3_AB", "3": "I2S_BCLK", "4": "I2S_LRCLK", "5": "GND", "6": "I2S_DOUT", "7": "I2S_DIN", "8": "GND", "9": "SDA", "10": "TR_APRS", "11": "MEZZ_EN", "12": "+3V3", "13": "GND", "14": "SCL", "15": "TX_INHIBIT_n", "16": "GND"})
part("J_PWR1", "Connector_Generic", "Conn_01x02", "cell node from PCB-A J_MEZZ_PWR (JST-VH)", "VH2", {"1": "VIN_CELL", "2": "GND"})
for ref, net in (("TP1", "V8"), ("TP2", "GND"), ("TP3", "RADIO_PTT"), ("TP4", "RADIO_MIC"), ("TP5", "RADIO_SPK"), ("TP6", "RADIO_COS"), ("TP7", "+3V3"), ("TP8", "VIN_CELL"), ("TP9", "TR_APRS"), ("TP10", "RADIO_PTT2"), ("TP11", "MEZZ_EN"), ("TP12", "TX_INHIBIT_n"), ("TP13", "MCLK"), ("TP14", "+3V3_AB"), ("TP15", "I2S_BCLK")):
    part(ref, "Connector", "TestPoint", net, "TP", {"1": net})
for i, net in enumerate(("VIN_CELL", "+3V3_AB", "+3.3VA", "+3V3", "GND"), 1):   # V8 is driven by the boost; the two 3.3 V rails arrive over the harness
    part("#FLG%02d" % i, "power", "PWR_FLAG", "PWR_FLAG", "", {"1": net})
# --- TPS61089 boost: cell node (3.0-4.2 V) -> 7.6 V, 500 kHz (R FSW 301k), ILIM 100k = 10 A typ / 9 A min PEAK (audit 19.2), VFB 1.212 V with 105k/20k -> 7.58 V typ, < 7.9 V worst case against the module's 8.5 V maximum (audit 19.3), COMP 17.4k + 4.7n (TI example)
part("U1", "Regulator_Switching", "TPS61089", "TPS61089 boost 7.6 V / 2 A", "QFN11",
     {"1": "FSW", "2": "BST_VCC", "3": "FB8", "4": "COMP", "5": "GND", "6": "V8", "7": "MEZZ_EN", "8": "ILIM", "9": "VIN_CELL", "10": "BOOT", "11": "SW"})
part("L1", "Device", "L", "1.5uH XAL6030-152MEB (Isat 12 A, 5.6 mOhm)", "L6030", {"1": "VIN_CELL", "2": "SW"})
c("C20", "100n 25V", "BOOT", "SW"); c("C21", "1u", "BST_VCC", "GND"); r("R30", "301k 1% (500 kHz)", "FSW", "SW"); r("R31", "100k 1% (ILIM 10 A peak, 9 A min)", "ILIM", "GND")
r("R32", "17.4k", "COMP", "COMPC"); c("C22", "4.7n", "COMPC", "GND"); r("R33", "105k 1%", "V8", "FB8"); r("R34", "20k 1%", "FB8", "GND"); r("R35", "100k", "MEZZ_EN", "GND")
c("C23", "22u 10V X7R 1210", "VIN_CELL", "GND", "C1210"); c("C24", "22u 10V X7R 1210", "VIN_CELL", "GND", "C1210"); c("C25", "100n", "VIN_CELL", "GND")
for i in range(4): c("C%d" % (26 + i), "22u 25V X7R 1210", "V8", "GND", "C1210")
c("C30", "100n 25V", "V8", "GND")
# --- DMR858M (pin numbers are the module pins; symbol is a generic 2x12)
part("U2", "Connector_Generic", "Conn_02x12_Odd_Even", "DNP bench: DMR858M 5 W UHF module on 2 x 1x12 2.54 mm female headers 8.5 mm + M2.5 x 11 mm standoffs", "DMR",
     {"1": "V8", "2": "GND", "3": "CS", "4": "GND", "5": "RADIO_PTT", "6": "RADIO_SPK", "7": "CH8", "8": "CH4", "9": "CH2", "10": "CH1", "11": "NC", "12": "NC",
      "13": "GND", "14": "RADIO_MIC", "15": "GND", "16": "RADIO_COS", "17": "GND", "18": "RADIO_TX", "19": "RADIO_RX", "20": "NC", "21": "NC", "22": "NC", "23": "NC", "24": "NC"})   # D7 (V1.2 datasheet p.10): 16 SPKEN is the module's receive indication OUTPUT (low, high on a received signal), read as carrier detect; 7 to 10 are the channel knob's 8421 code OUTPUTS, read back; 11/12 speaker OUTP/OUTN and 21/22 HST (upgrade UART, the module's own USB-C) unused
# D7: no channel jumpers (the pins are outputs); CS pulled up on the kit-domain rail and driven by the expander bit CS_CTL (low = module sleep, 3 s)
r("R36", "10k", "CS", "+3V3_AB"); r("R48", "1k", "CS_CTL", "CS")
for k, (net, rr, rp) in enumerate((("CH8", "R43", "R49"), ("CH4", "R44", "R50"), ("CH2", "R45", "R51"), ("CH1", "R46", "R52"))):
    r(rr, "1k", net, net + "_IN"); r(rp, "100k", net + "_IN", "GND")   # knob code outputs into expander inputs: 1k against a software mistake, 100k so the inputs read low with the module unplugged (gateway audit 5 Sep 06:35)
# --- D6 rails: +3V3_AB (gated on B13, over J_AB1 and J_MEZZ1) feeds the codec, its clock, the PCA9555 and the UART bridge, so the I2S lines die with the module (32.35);
#     +3V3 (PCB-A's always-on logic rail) keeps the PTT, EMCON and TR-mirror stages as on D5; the codec's analogue rail sits behind a bead
part("FB1", "Device", "FerriteBead", "600R@100MHz", "FB", {"1": "+3V3_AB", "2": "+3.3VA"}); c("C9", "100n", "+3.3VA", "GND"); c("C10", "4.7u", "+3.3VA", "GND")
c("C7", "4.7u", "+3V3_AB", "GND"); c("C8", "100n", "+3V3_AB", "GND"); c("C17", "100n", "+3V3", "GND"); c("C18", "100n", "+3V3_AB", "GND")
# --- WM8960 codec (Cirrus WM8960 rev 4.4, vendor/audio/): QFN-32, I2C 0x1A, I2S slave to the module (BCLK, one LRCLK for DAC and ADC), MCLK 24 MHz from X1 as on
#     the Waveshare WM8960 HAT (in-tree wm8960-soundcard overlay, 24 MHz fixed clock); DCVDD and DBVDD 3.3 V (both 1.71 to 3.6 V), AVDD and the speaker rails on +3.3VA;
#     line in on LINPUT1 from the radio speaker pin, line out on HP_L to the radio microphone pin through the D5 attenuator
WM = {1: "NC", 2: "NC", 3: "NC", 4: "SPK_IN", 5: "NC", 6: "NC", 7: "NC", 8: "+3V3_AB", 9: "GND", 10: "+3V3_AB", 11: "MCLK", 12: "I2S_BCLK", 13: "I2S_LRCLK", 14: "I2S_DOUT",
      15: "I2S_LRCLK", 16: "I2S_DIN", 17: "SCL", 18: "SDA", 19: "NC", 20: "GND", 21: "+3.3VA", 22: "NC", 23: "NC", 24: "GND", 25: "NC", 26: "+3.3VA", 27: "VMID", 28: "GND",
      29: "NC", 30: "NC", 31: "AFOUT", 32: "+3.3VA", 33: "GND", 34: "NC"}
part("U5", "Connector_Generic", "Conn_02x17_Odd_Even", "WM8960 audio codec QFN-32 (pins per datasheet table: 4 LINPUT1, 11 MCLK, 12 BCLK, 13 DACLRC, 14 DACDAT, 15 ADCLRC, 16 ADCDAT, 17 SCLK, 18 SDIN, 27 VMID, 31 HP_L, 32 AVDD, 33 paddle)", "QFN32", {str(k): v for k, v in WM.items()})
c("C33", "100n", "+3.3VA", "GND"); c("C34", "10u", "+3.3VA", "GND", "C1210"); c("C35", "100n", "+3V3_AB", "GND"); c("C36", "100n", "+3V3_AB", "GND"); c("C37", "4.7u", "VMID", "GND")
part("X1", "Oscillator", "ASE-xxxMHz", "24 MHz 3.3 V oscillator 3225 (ASE-24.000MHZ-LC-T class)", "OSC3225", {"1": "+3V3_AB", "2": "GND", "3": "MCLK", "4": "+3V3_AB"}); c("C38", "100n", "+3V3_AB", "GND"); 
# D7: PCA9555 0x26 (A2 A1 A0 = 1 1 0) replaces the PCA9536: P0.0 PTT, P0.1 PTT2 (spare), P0.2 status LED, P0.3 CS control, P0.4 carrier detect (SPKEN, input),
#     P0.5 to P1.0 the channel knob code 8/4/2/1 (inputs), the rest spare; a gpiochip for Direwolf's PTT and DCD
part("U7", "Interface_Expansion", "PCA9555PW", "PCA9555PW 0x26: PTT, PTT2, LED, CS, COS in, channel code in", "EXP", {
 "24": "+3V3_AB", "12": "GND", "22": "SCL", "23": "SDA", "1": "NC", "21": "GND", "2": "+3V3_AB", "3": "+3V3_AB",   # A0 = pin 21, A1 = pin 2, A2 = pin 3: 0x26
 "4": "OUT1", "5": "OUT2", "6": "LED_K", "7": "CS_CTL", "8": "RADIO_COS_IN", "9": "CH8_IN", "10": "CH4_IN", "11": "CH2_IN", "13": "CH1_IN",
 "14": "NC", "15": "NC", "16": "NC", "17": "NC", "18": "NC", "19": "NC", "20": "NC"}, "C5626"); c("C39", "100n", "+3V3_AB", "GND")
r("R3", "100k", "RADIO_COS", "GND"); r("R42", "1k", "RADIO_COS", "RADIO_COS_IN")   # the module's receive indication into the expander, 1k against a software mistake
# D7: SC16IS740 I2C-to-UART bridge (NXP data sheet, TSSOP16: 1 VDD, 2 A0, 3 A1, 4 SO, 5 SCL, 6 SDA, 7 IRQ, 8 I2C/SPI, 9 VSS, 10 RTS, 11 CTS, 12 TX, 13 RX, 14 RESET, 15 XTAL1, 16 XTAL2)
#     on the module's control UART (18 TXD, 19 RXD: channel, power, mic gain, the command set 0x01 to 0x28), A1 = A0 = VDD gives 0x90 (7-bit 0x48), I2C mode,
#     CTS tied low, clocked by the codec's 24 MHz oscillator on XTAL1 (external clock input, XTAL2 open), RESET pulled up; Linux sc16is7xx gives it a tty
part("U8", "Connector_Generic", "Conn_01x16", "SC16IS740IPW I2C-to-UART bridge 0x48, 24 MHz external clock on XTAL1", "TSSOP16",
     {"1": "+3V3_AB", "2": "+3V3_AB", "3": "+3V3_AB", "4": "NC", "5": "SCL", "6": "SDA", "7": "NC", "8": "+3V3_AB", "9": "GND", "10": "NC", "11": "GND", "12": "BR_TX", "13": "BR_RX", "14": "BR_nRST", "15": "MCLK", "16": "NC"})
c("C40", "100n", "+3V3_AB", "GND"); r("R47", "10k", "BR_nRST", "+3V3_AB")
# --- audio paths (D5 values where they stay), PTT from U7, TR mirror, the bridge's UART lines, LED
r("R2", "47k", "AFOUT", "MIC_NODE"); r("R4", "1k", "MIC_NODE", "GND"); c("C13", "4.7u", "MIC_NODE", "RADIO_MIC")   # D7: HP_L line level divided by 48 (about 20 mV rms at full scale) into the module's microphone pin, whose modulation sensitivity is 4 to 10 mV (V1.2 datasheet); the module provides the bias
c("C14", "4.7u", "RADIO_SPK", "SPK_IN")   # the module's audio out into LINPUT1 (internally biased at VMID)
r("R10", "1.5k", "OUT2", "Q1_B"); r("R11", "1.5k", "OUT1", "Q2_B")
part("Q1", "Transistor_BJT", "BC847", "BC847 (PTT2, spare)", "SOT23", {"1": "Q1_B", "2": "GND", "3": "Q1_C"}); part("Q2", "Transistor_BJT", "BC847", "BC847 (PTT to the module)", "SOT23", {"1": "Q2_B", "2": "Q2_E", "3": "Q2_C"})
# D5 EMCON hardware inhibit: Q3 in series with Q2's emitter; line open, panel unplugged or D unpowered = PTT path intact, panel toggle grounds TX_INHIBIT_n = module stays in RX
part("Q3", "Transistor_FET", "2N7002", "2N7002 (EMCON inhibit in Q2 emitter)", "SOT23", {"1": "Q3_G", "2": "GND", "3": "Q2_E"})
r("R37", "1k", "TX_INHIBIT_n", "Q3_G"); r("R38", "100k", "TX_INHIBIT_n", "+3V3"); c("C32", "100n", "Q3_G", "GND"); r("R39", "100k", "RADIO_PTT", "+3V3")
# TX mirror follows the real PTT pin (post-inhibit): Q4 PNP from RADIO_PTT (B13 reads it through a level stage with its own pull-down, 32.35)
part("Q4", "Transistor_BJT", "BC857", "BC857 (TR mirror from RADIO_PTT)", "SOT23", {"1": "Q4_B", "2": "+3V3", "3": "Q4_C"})
r("R40", "10k", "RADIO_PTT", "Q4_B"); r("R41", "100R", "Q4_C", "TR_APRS")
r("R12", "22R", "Q1_C", "RADIO_PTT2"); r("R13", "22R", "Q2_C", "RADIO_PTT")
r("R8", "100R", "BR_TX", "RADIO_RX"); r("R9", "100R", "RADIO_TX", "BR_RX")   # bridge TX into the module RXD, module TXD into the bridge RX
part("D1", "Device", "LED", "green status (U7 bit 3 sinks)", "LED", {"2": "LED_A", "1": "LED_K"}, "C72043"); r("R15", "1k", "+3V3_AB", "LED_A")

# ----------------------------------------------------------------- emit
POWER = {"GND": ("power", "GND"), "+3V3": ("power", "+3V3")}
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
SECTIONS = [("HARNESS TO PCB-A, CELL FEED, TEST POINTS", ["J_HARN1", "J_PWR1", "TP1", "TP2", "TP3", "TP4", "TP5", "TP6", "TP7", "TP8", "TP9", "TP10", "TP11", "TP12", "TP13", "TP14", "TP15", "#FLG01", "#FLG02", "#FLG03", "#FLG04", "#FLG05"]),
            ("TPS61089 BOOST: CELL NODE -> 8 V / 2 A  (500 kHz, ILIM 7.9 A, EN = MEZZ_EN)", ["U1", "L1", "C20", "C21", "R30", "R31", "R32", "C22", "R33", "R34", "R35", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30"]),
            ("DMR858M RADIO MODULE (V1.0 BOARD): CS PULL-UP AND CONTROL, KNOB CODE AND COS INTO THE EXPANDER", ["U2", "R36", "R48", "R43", "R44", "R45", "R46", "R49", "R50", "R51", "R52", "R42"]),
            ("D7 CORE: RAILS, WM8960 CODEC ON I2S + I2C, 24 MHz CLOCK, PCA9555 EXPANDER 0x26, SC16IS740 UART BRIDGE 0x48", ["FB1", "C9", "C10", "C7", "C8", "C17", "C18", "U5", "C33", "C34", "C35", "C36", "C37", "X1", "C38", "U7", "C39", "R3", "U8", "C40", "R47"]),
            ("AUDIO PATHS, PTT + TR MIRROR, BRIDGE UART LINES, LED", ["R2", "R4", "C13", "C14", "R10", "R11", "Q1", "Q2", "R12", "R13", "Q3", "R37", "R38", "C32", "R39", "Q4", "R40", "R41", "R8", "R9", "D1", "R15"])]
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
hdr += '\t(title_block (title "MeshSat Field Kit carrier - PCB-D APRS BOARD") (date "2026-09-05") (rev "A") (company "MeshSat") (comment 1 "Phase D7 schematic (MESHSAT-804: the DMR858M V1.0 board as delivered, the CM5 owns the module) on D6 (appendix 32.35: the AIOC-derived STM32 core is replaced by a WM8960 codec on I2S and I2C, a 24 MHz clock and a PCA9555 for the PTT, CS, carrier-detect and channel-code lines and an SC16IS740 bridge for the control UART; USB is gone), generated by tools/gen_sch_d.py") (comment 2 "D7: WM8960 codec on I2S, PCA9555 0x26 (PTT, CS, carrier detect, channel code), SC16IS740 bridge 0x48 on the module control UART, TPS61089 boost; the DMR858M V1.0 board on two 1x12 sockets"))\n'
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
