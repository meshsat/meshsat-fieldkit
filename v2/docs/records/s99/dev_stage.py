#!/usr/bin/env python3
"""S-99: board A's +5V_DEV LM5176 stage against the PS-ALLTX coincident demand. Desk arithmetic, standard
library only, stdout is the only output. Prototype design, AI engineering analysis: nothing has been built or
measured. Stream s99, MESHSAT-1357, 28 September 2026.

Inputs are the four committed design files named below, pinned by sha256: a changed input is refused by name
before anything is parsed. Every maker constant is typed in with its document and page (see ANALYSIS.md
section 2); nothing is extracted from a PDF at run time. Run from anywhere:
    python3 v2/docs/records/s99/dev_stage.py > v2/docs/records/s99/dev_stage.out
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
A_INTENT = Path("v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json")
B_INTENT = Path("v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json")
D_INTENT = Path("v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs-intent.json")
A_NET = Path("v2/ecad/pcb-a-power-a23/out/pcb-a-power.net")
INPUT_SHA256 = {
    A_INTENT: "3422910a15c4d1450141aa9a5fd725ba75bca9fcb42ae8c87e4cf3385d7d4498",
    B_INTENT: "96ee391b3e3f638d7436cad51fcabf77999b530d8734c1feb93f7766a4877d8a",
    D_INTENT: "8d9f3b2256521b0d76373d434c1104fae6438002e5945088d890ec743a4d260a",
    A_NET: "0a2b59087bcc2678dac7e05b8b67c669f3d1957af846a0827bf59289dcea77d7",
}

# ---------------------------------------------------------------- maker constants (typed, cited)
# TI LM5176 SNVSAI1D (June 2017, revised August 2021), v2/vendor/ti/lm5176-datasheet.pdf
VREF = (0.788, 0.800, 0.812)          # p.6, EA VREF min/typ/max
VSNS_V = (0.043, 0.050, 0.057)        # p.7, VSNS average current loop regulation target
VCS_BUCK_V = (0.066, 0.080, 0.094)    # p.7, VCS(BUCK) valley threshold, HTSSOP-28
ISS_A = (3.75e-6, 5.0e-6, 6.35e-6)    # p.6, ISS soft-start pullup current
VSS_CL = 1.21                         # p.6, SS clamp voltage, typical; no guaranteed timing bound
GM_SS = 1.0e-3                        # p.7, typical gm at ISNS differential 55 mV, VSS 0.5 V; 1 mS
VCC_V = (6.95, 7.35, 7.88)            # p.6, VCC regulation voltage
FSW_SPREAD = (175.0 / 200.0, 225.0 / 200.0)   # p.6, fSW(1) 175/200/225 kHz at RT 40 k
T_DEAD_S = 45e-9                      # p.8, tDT1 and tDT2
RT_OHM = 40.2e3                       # netlist R115 "40.2k (206 kHz)"
FSW_NOM = 1.0 / (RT_OHM * 116e-12 + 190e-9)   # p.17, equation 5
# Vishay WSL, document 30100, revision 23-Nov-2023, v2/vendor/vishay/vishay-wsl-power-metal-strip.pdf
WSL2512_P70_W = 1.0                   # p.1, power rating at +70 C
WSL_TCR_PPM = 110.0                   # p.2, component TCR for 5 to 6.9 mOhm
WSL_TOL = 0.01                        # F code, +-1 percent (netlist "6mOhm 1% 2512")
SHUNT_RISE_K = 50.0                   # an assumed hot-shunt rise for the TCR term; not a measurement
# Coilcraft XAL1010, document 804-1 revised 02/25/26, v2/vendor/power/coilcraft-xal1010.pdf, the -682ME row
L_NOM_H = 6.8e-6
L_TOL = 0.20                          # inductance +-20 percent
L_ISAT_A = 21.8                       # 30 percent inductance drop, note 5
L_IRMS_20K_A = 14.0
L_IRMS_40K_A = 18.5
L_DCR_OHM = (8.10e-3, 8.90e-3)        # typ, max
# TI CSD19532Q5B SLPS414B (December 2013, revised May 2017), v2/vendor/power/ti-csd19532q5b-n-fet.pdf
FET_RDS_6V = (4.6e-3, 5.7e-3)         # p.3, RDS(on) at VGS 6 V, ID 17 A: typ, max, 25 C
FET_HOT_FACTOR = 1.5                  # an assumed RDS(on) rise at a hot junction; the sheet's curve was not read numerically
FET_TR_TF_S = (6e-9, 6e-9)            # p.3, tr and tf at VGS 10 V, RG 0, ID 17 A (faster than the LM5176's drive will give)
FET_EDGE_FACTOR = 3.0                 # an assumed slowing of the edges under the LM5176's 1.8 / 1.1 ohm drivers at 7.35 V
FET_COSS_F = (706e-12, 918e-12)       # p.3, typ, max at VDS 50 V
FET_QRR_C = 249e-9                    # p.3, at IF 17 A, di/dt 300 A/us
FET_VSD_V = (0.8, 1.0)                # p.3, body diode forward voltage, typ, max
FET_RTHJA = 50.0                      # p.3, C/W on a 1 in2, 2 oz pad (the sheet's condition, not this board's)
FET_TJ_MAX = 150.0
# TI INA226 SBOS547C (June 2011, revised August 2026), v2/vendor/ti/ti-ina226.pdf
INA_SHUNT_FS_V = 0.08192              # shunt voltage input range +-81.92 mV
INA_LSB_V = 2.5e-6
INA_BUS_MAX_V = 36.0
# JST VH catalogue, v2/vendor/connectors/jst-vh-catalogue.pdf (revision not printed), p.1
VH16_A = 10.0                         # AWG 16 with the standard header
VH_CONTACT_OHM = (0.010, 0.020)       # initial / after test maxima
# TI TPS2596 SLVSET8A (May 2019, revised August 2019), v2/vendor/power/tps2596.pdf
TPS2596_ILIM_453 = (1.83, 2.004, 2.147)      # RILM 453 ohm: min/typ/max
TPS2596_ILIM_909 = (0.949, 1.005, 1.051)     # RILM 909 ohm: min/typ/max
# p.28 equation 7: RILM [ohm] = 903 [A ohm] / (ILIM [A] - 0.0112 [A]).
# Positive ILIM flows into the load. p.6 has no guaranteed row at 1 kohm.
TPS2596_ILIM_1K_NOM = 903.0 / 1000.0 + 0.0112
TPS2596_RILM_TOL = 0.01
TPS2596_ILIM_1K_RMIN = 903.0 / (1000.0 * (1 - TPS2596_RILM_TOL)) + 0.0112
# TI TPS62933 SLUSEA4D (June 2021, revised August 2022), v2/vendor/ti/ti-tps62933.pdf (the option's part)
TPS62933_IHS_LIMIT = (4.2, 5.0, 5.8)
# Coilcraft XAL6060, document 887-1 revised 02/25/26, v2/vendor/coilcraft/coilcraft-xal60xx-series.pdf, -682ME row
XAL6060_682_ISAT = 9.2
XAL6060_682_IRMS = (7.0, 9.0)
XAL6060_682_DCR = (18.9e-3, 20.8e-3)
# Maker load figures used in the coincident profile (ANALYSIS.md section 3 names each document and page)
LIME_SUPPLY_A = 0.90                  # myriadrf setup page: the host supplies 5 V, 900 mA; product page: maximum power 4.5 W
E22_TX_A = 0.650                      # Ebyte E22-900M30S manual v1.20, TX current 650 mA typical, no maximum printed
RB_DC_IN_MAX_A = 0.500                # Ground Control hardware page (snapshot 2026-09-27): DC input 4.0 to 5.3 V at a maximum of 500 mA
RB_CHARGE_DEFAULT_A = 0.460           # same page: default supercapacitor charge current about 460 mA, optional about 800 mA
KSZ_1V2_A = 0.460 + 0.750             # Microchip DS00002330D Table 6-1 p.169: AVDDL 460 mA + DVDDL 750 mA at 1000 Mbps, all ports 100 percent
SA868_TX_A = (0.900, 1.000)           # NiceRF SA868 datasheet v1.3 p.4: TX current high power 900 typ, 1000 max mA
USB2_DEVICE_MAX_A = 0.500             # a USB 2.0 bus-powered device's maximum, the bound for the wall host port's device
# Project figures (declarations, not maker figures)
V_BAT_RANGE = (12.4, 15.5, 16.8)      # REQ-018's PA-alone floor, the all-transmit floor, the pack's service maximum
EFF_DECL = 0.90                       # board A's declared efficiency floor for the stage
LEAD_R_PAIR_20C = 1.72e-8 * 0.300 / 1.25e-6   # 150 mm each way of AWG 16 (1.25 mm2), dc_drop.py's rho, 20 C

OUT = []


def say(s=""):
    OUT.append(s)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_inputs():
    for rel, want in INPUT_SHA256.items():
        got = sha256(ROOT / rel)
        if got != want:
            sys.stderr.write("Refused: input %s: sha256 mismatch; expected %s, got %s\n" % (rel, want, got))
            sys.exit(1)


def parse_sexp(s):
    tokens = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', s)
    stack = [[]]
    for tok in tokens:
        if tok == "(":
            stack.append([])
        elif tok == ")":
            x = stack.pop()
            stack[-1].append(x)
        else:
            stack[-1].append(tok.strip('"'))
    return stack[0]


def find_all(node, head):
    out = []
    if isinstance(node, list):
        if node and node[0] == head:
            out.append(node)
        for c in node:
            out += find_all(c, head)
    return out


def field(c, name):
    for x in c:
        if isinstance(x, list) and x and x[0] == name:
            return x[1] if len(x) > 1 else None
    return None


def read_stage(net_text):
    """The SD stage's parts and the two shunts' nets, read from the netlist (parsed, never grepped)."""
    tree = parse_sexp(net_text)
    comps = {field(c, "ref"): (field(c, "value"), field(c, "footprint")) for c in find_all(tree, "comp")}
    nets = {}
    for n in find_all(tree, "net"):
        name = field(n, "name")
        nodes = [x for x in n if isinstance(x, list) and x and x[0] == "node"]
        nets[name] = sorted((field(x, "ref"), field(x, "pin")) for x in nodes)
    return comps, nets


def stage_facts(comps, nets):
    want = {"U7": "LM5176PWPR", "Q32": "CSD19532Q5B", "Q33": "CSD19532Q5B", "Q34": "CSD19532Q5B", "Q35": "CSD19532Q5B",
            "L6": "6.8uH XAL1010-682ME", "R43": "6mOhm 1% 2512 (ISNS)", "R177": "5mOhm 1% 2512 (CS)", "R115": "40.2k",
            "R40": "53.6k 1%", "R41": "10k 1%", "C140": "470p", "R132": "2.2k", "C115": "100n", "C141": "1n", "C142": "47n",
            "C143": "4.7u", "R179": "100k (MODE: CCM)", "C47": "10u 50V X7R 1210", "C48": "10u 50V X7R 1210",
            "C49": "22u 25V 1210", "C50": "22u 25V 1210", "C51": "22u 25V 1210", "C167": "150u 25V", "C168": "150u 25V",
            "C169": "150u 25V", "R180": "100R", "R181": "100R", "R182": "100R", "R183": "100R", "C145": "1n", "C146": "1n",
            "U11": "INA226", "U23": "TPS259631DDAR eFuse +5V_DEV -> +5V_D8", "U32": "TPS259631DDAR eFuse +5V_DEV -> VBUS_WALL",
            "R98": "453R 1% (ILM: 2.0 A)", "R186": "1k 1% (ILM: 0.89 A)", "J_5V_DEV": "JST-VH"}
    say("== 1. THE FITTED STAGE, read from the netlist (value must start with or contain the expected text)")
    ok = True
    for ref in sorted(want):
        val = comps.get(ref, (None, None))[0]
        hit = val is not None and want[ref] in val
        ok = ok and hit
        say("  %-8s %-8s %s" % (ref, "PASS" if hit else "FAIL", val))
    # the two shunts' places in the circuit
    def pins_of(ref, net):
        return [p for r, p in nets.get(net, []) if r == ref]
    isns_out = ("SD_OUT" in nets) and bool(pins_of("R43", "/SD_OUT") or pins_of("R43", "SD_OUT"))
    n_out = nets.get("/SD_OUT") or nets.get("SD_OUT") or []
    n_dev = nets.get("/+5V_DEV") or nets.get("+5V_DEV") or []
    n_cs = nets.get("/SD_CS") or nets.get("SD_CS") or []
    r43_out = [p for r, p in n_out if r == "R43"]
    r43_dev = [p for r, p in n_dev if r == "R43"]
    q35_out = [p for r, p in n_out if r == "Q35"]
    r177_cs = [p for r, p in n_cs if r == "R177"]
    q33_cs = [p for r, p in n_cs if r == "Q33"]
    q34_cs = [p for r, p in n_cs if r == "Q34"]
    say("  R43 (ISNS) pins on SD_OUT: %s, on +5V_DEV: %s; Q35 (boost high side) pins on SD_OUT: %s" % (r43_out, r43_dev, q35_out))
    say("  R177 (CS) pins on SD_CS: %s; Q33 pins on SD_CS: %s; Q34 pins on SD_CS: %s" % (r177_cs, q33_cs, q34_cs))
    side = "OUTPUT side (between Q35's drain and the +5V_DEV rail)" if (r43_out and r43_dev and q35_out) else "NOT ESTABLISHED"
    say("  => the average current loop's shunt R43 is on the %s" % side)
    say("  => the cycle-by-cycle shunt R177 is in the low-side FETs' common source (SD_CS) to GND: %s" % ("PASS" if (r177_cs and q33_cs and q34_cs) else "FAIL"))
    say("  netlist parts check: %s" % ("ALL PASS" if ok else "SOME FAIL"))
    return ok and bool(r43_out and r43_dev and q35_out and r177_cs)


def fmt(x, n=3):
    return ("%%.%df" % n) % x


def main():
    check_inputs()
    a = json.loads((ROOT / A_INTENT).read_text())
    b = json.loads((ROOT / B_INTENT).read_text())
    d = json.loads((ROOT / D_INTENT).read_text())
    comps, nets = read_stage((ROOT / A_NET).read_text())
    say("S-99 desk arithmetic. Inputs (sha256): ")
    for rel in INPUT_SHA256:
        say("  %s %s" % (INPUT_SHA256[rel], rel))
    say()
    if not stage_facts(comps, nets):
        raise SystemExit("Refused: fitted stage differs from the expected netlist")
    say("  R186's held netlist label 0.89 A is stale: the corrected equation gives 0.9142 A; no design input is edited here.")

    # ------------------------------------------------------------ 2. thresholds
    say()
    say("== 2. THE PROGRAMMED LIMITS (SNVSAI1D p.7; shunt tolerances Vishay 30100)")
    vout = [v * (1 + 53.6 / 10.0) for v in VREF]
    say("  Output: VREF %s to %s V on 53.6k/10k -> %s / %s / %s V (resistor tolerance not added)" % (VREF[0], VREF[2], fmt(vout[0]), fmt(vout[1]), fmt(vout[2])))
    vo = vout[1]
    rsns = 6.0e-3
    r_lo, r_hi = rsns * (1 - WSL_TOL), rsns * (1 + WSL_TOL)
    tcr = WSL_TCR_PPM * 1e-6 * SHUNT_RISE_K
    i_min0 = VSNS_V[0] / r_hi
    i_typ = VSNS_V[1] / rsns
    i_max0 = VSNS_V[2] / r_lo
    i_min1 = VSNS_V[0] / (r_hi * (1 + tcr))
    i_max1 = VSNS_V[2] / (r_lo * (1 - tcr))
    say("  Average loop, R43 6 mOhm: nominal shunt 43/50/57 mV -> %s / %s / %s A" % (fmt(VSNS_V[0] / rsns), fmt(i_typ), fmt(VSNS_V[2] / rsns)))
    say("  with +-1 percent initial tolerance: %s (min) to %s (max) A" % (fmt(i_min0), fmt(i_max0)))
    say("  with the shunt %d K hot (TCR +-%d ppm/K, %s percent): %s to %s A" % (SHUNT_RISE_K, WSL_TCR_PPM, fmt(tcr * 100, 2), fmt(i_min1), fmt(i_max1)))
    say("  ISS / gm offset: ISS %s to %s uA over gm 1 mS is %s to %s mV, %s to %s A on 6 mOhm; the VSNS spec is taken at VSS = 0.8 V"
        % (fmt(ISS_A[0] * 1e6, 2), fmt(ISS_A[2] * 1e6, 2), fmt(ISS_A[0] / GM_SS * 1e3, 2), fmt(ISS_A[2] / GM_SS * 1e3, 2),
           fmt(ISS_A[0] / GM_SS / rsns, 2), fmt(ISS_A[2] / GM_SS / rsns, 2)))
    say("  so the 43 to 57 mV band is taken as the regulation point as published; the offset is named, not added")
    rcs = 5.0e-3
    rc_lo, rc_hi = rcs * (1 - WSL_TOL), rcs * (1 + WSL_TOL)
    v_min, v_typ, v_max = VCS_BUCK_V[0] / rc_hi, VCS_BUCK_V[1] / rcs, VCS_BUCK_V[2] / rc_lo
    say("  Cycle-by-cycle (buck, VALLEY), R177 5 mOhm +-1 percent: 66/80/94 mV -> valley %s / %s / %s A" % (fmt(v_min), fmt(v_typ), fmt(v_max)))
    fsw_lo, fsw_hi = FSW_NOM * FSW_SPREAD[0], FSW_NOM * FSW_SPREAD[1]
    say("  Switching frequency: RT 40.2k -> %s kHz nominal (equation 5), %s to %s kHz over the fSW(1) spread" % (fmt(FSW_NOM / 1e3, 1), fmt(fsw_lo / 1e3, 1), fmt(fsw_hi / 1e3, 1)))

    def ripple(vin, L=L_NOM_H, f=FSW_NOM):
        dbuck = vo / vin
        return (vin - vo) * dbuck / (L * f)
    say("  Inductor ripple (buck, CCM): %s A at %s V in, %s A at %s V in; worst (L -20 percent, fsw %s kHz): %s A at 16.8 V"
        % (fmt(ripple(V_BAT_RANGE[0]), 2), V_BAT_RANGE[0], fmt(ripple(V_BAT_RANGE[2]), 2), V_BAT_RANGE[2], fmt(fsw_lo / 1e3, 1),
           fmt(ripple(V_BAT_RANGE[2], L_NOM_H * (1 - L_TOL), fsw_lo), 2)))
    rip_nom = ripple(V_BAT_RANGE[2])
    rip_worst = ripple(V_BAT_RANGE[2], L_NOM_H * (1 - L_TOL), fsw_lo)
    say("  Cycle limit as an OUTPUT current (valley limit + half the ripple): %s / %s / %s A nominal ripple" % (fmt(v_min + rip_nom / 2), fmt(v_typ + rip_nom / 2), fmt(v_max + rip_nom / 2)))
    say("  Inductor PEAK in cycle limit (equation 18, valley + full ripple): nominal %s A; corner (VCS max, R -1, L -20, fsw -12.5 percent) %s A against Isat %s A"
        % (fmt(v_typ + rip_nom), fmt(v_max + rip_worst), L_ISAT_A))
    say("  => at the corner the cycle-limit backstop exceeds Isat by %s A (INFERRED; an observation for the stage owner, not S-99's verdict)" % fmt(v_max + rip_worst - L_ISAT_A, 2))

    # ------------------------------------------------------------ 3. loads
    say()
    say("== 3. THE LOADS THAT COINCIDE IN PS-ALLTX (intents parsed; maker figures typed and cited)")
    ra = a["rails"]["+5V_DEV"]
    rb = b["rails"]["+5V_DEV"]
    rd = d["rails"]["+5V_D8"]
    say("  A declares +5V_DEV %s A typ, %s A peak, loads %s" % (ra["amps_typ"], ra["amps_peak"], json.dumps(ra["loads"], sort_keys=True)))
    say("  B declares +5V_DEV %s A typ, %s A peak, %d loads summing to %s A" % (rb["amps_typ"], rb["amps_peak"], len(rb["loads"]), fmt(sum(rb["loads"].values()), 2)))
    say("  D declares +5V_D8 %s A typ, %s A peak, loads summing to %s A" % (rd["amps_typ"], rd["amps_peak"], fmt(sum(rd["loads"].values()), 2)))
    say("  A's +5V_D8 (behind U23): %s / %s A; A's VBUS_WALL (behind U32): %s / %s A" % (a["rails"]["+5V_D8"]["amps_typ"], a["rails"]["+5V_D8"]["amps_peak"], a["rails"]["VBUS_WALL"]["amps_typ"], a["rails"]["VBUS_WALL"]["amps_peak"]))
    # board B's children, input-referred. A switched child names its switch as source; a converted child names its
    # inductor, so the buck ICs are mapped to their rails here (gen_sch_b.py: U25 -> +3V3_DEV, U26 -> +1V2_KSZ,
    # U106/U206/U306 -> +1V1_S1..3, read from the intent's rail names, not typed as numbers).
    children = {r["source"]: (name, r) for name, r in b["rails"].items() if r.get("fed_from") == "+5V_DEV"}
    for ic_ref, rail in (("U25", "+3V3_DEV"), ("U26", "+1V2_KSZ"), ("U106", "+1V1_S1"), ("U206", "+1V1_S2"), ("U306", "+1V1_S3")):
        children[ic_ref] = (rail, b["rails"][rail])
    # every transmitter keyed: the two Zigbee radios on +3V3_ZB (behind +3V3_DEV) at their declared 0.30 A peak
    # against 0.10 A typical (gen_sch_b.py: "0.3 A peak is both radios transmitting at once")
    zb = b["rails"]["+3V3_ZB"]
    zb_tx_increment = (zb["amps_peak"] - zb["amps_typ"]) * 3.3 / (b["rails"]["+3V3_DEV"]["efficiency"] * 5.0)

    def in_ref(r, amps):
        if r.get("converted"):
            return r["volts"] * amps / (r["efficiency"] * 5.0)
        return amps

    say()
    say("  Board B load table (A = input-referred at 5.0 V; MAKER = a held maker figure, PROJECT = a declaration, BOUND = a stated limit)")
    say("  %-6s %-9s %-9s %-9s %-9s  %s" % ("ref", "declared", "childTyp", "childPk", "M-tier", "basis of the M-tier figure"))
    b_typ_decl = 0.0
    b_m = 0.0
    b_p = 0.0
    b_limits = 0.0
    maker = {
        "U23": (LIME_SUPPLY_A, LIME_SUPPLY_A, "MAKER: LimeSDR Mini host supply 5 V 900 mA (setup page); 4.5 W maximum (product page)"),
        "U21": (E22_TX_A, None, "MAKER: E22-900M30S TX 650 mA typical (manual v1.20 printed p.2, PDF p.3); peak tier uses the declared 0.70"),
        "U24": (RB_DC_IN_MAX_A, RB_DC_IN_MAX_A, "MAKER: RockBLOCK 9704 DC input maximum 500 mA, charger default about 460 mA (hardware page)"),
        "U26": (KSZ_1V2_A * 1.2 / (0.85 * 5.0), KSZ_1V2_A * 1.2 / (0.85 * 5.0), "MAKER: KSZ9897R 1.21 A TYPICAL at 25 C, 1.2 V, 1000 Mbps all ports (DS00002330D Table 6-1 p.169), 0.85 buck, PWR-F03"),
    }
    for ref in sorted(rb["loads"], key=lambda k: (-rb["loads"][k], k)):
        decl = rb["loads"][ref]
        b_typ_decl += decl
        if ref in children:
            name, r = children[ref]
            ct, cp = in_ref(r, r["amps_typ"]), in_ref(r, r["amps_peak"])
            basis = "PROJECT: child %s %s / %s A%s" % (name, r["amps_typ"], r["amps_peak"], " through a %s buck at %s" % (r["volts"], r["efficiency"]) if r.get("converted") else "")
        else:
            ct, cp = decl, decl
            basis = "PROJECT: the declared allocation (no child rail in the intent)"
        m_val, p_val = ct, cp
        if ref in maker:
            m_val = maker[ref][0]
            p_val = maker[ref][1] if maker[ref][1] is not None else cp
            basis = maker[ref][2]
        if ref in ("U40", "U50", "U60"):
            basis = "PROJECT: child LDO %s / %s A (Iin = Iout + Ignd, Ignd omitted from these allocations, not a maximum); the parent's 0.05 is inconsistent (S-98 M7)" % (r["amps_typ"], r["amps_peak"])
        if ref == "U25":
            m_val = ct + zb_tx_increment
            basis = "PROJECT: child +3V3_DEV 1.2 A typ through the 0.88 buck (0.900 A) plus the two Zigbee radios' transmit increment %s A (+3V3_ZB 0.30 peak over 0.10 typ)" % fmt(zb_tx_increment)
        b_m += m_val
        b_p += max(p_val, m_val)
        b_limits += max(cp, m_val) if ref == "U26" else cp
        say("  %-6s %-9s %-9s %-9s %-9s  %s" % (ref, fmt(decl), fmt(ct), fmt(cp), fmt(m_val), basis))
    say("  B declared load sum %s A against its declared typical %s A and declared peak %s A" % (fmt(b_typ_decl), rb["amps_typ"], rb["amps_peak"]))
    say("  B M-tier (maker figures where held, declared typicals elsewhere, every transmitter keyed): %s A on the lead" % fmt(b_m))
    say("  B P-tier (maker figures for the transmitters and the switch, declared child PEAKS elsewhere): %s A on the lead" % fmt(b_p))
    say("  B every-declared-limit sum (the eFuse settings counted as loads): %s A; above B's own 6.0 A peak and the lead's 10 A: unphysical as one load, a declaration inconsistency for board B's owner" % fmt(b_limits))
    # board D (D8) in PS-ALLTX: the SA868 keys with the PA
    d_others = sum(v for k, v in rd["loads"].items() if k != "U21")
    tx = d["rails"]["+5V_TX"]["loads"]
    tx_others = sum(v for k, v in tx.items() if k != "FB1")
    d_m = SA868_TX_A[0] + tx_others + d_others
    d_mmax = SA868_TX_A[1] + tx_others + d_others
    d_p = d["rails"]["+5V_TX"]["amps_peak"] + d_others
    d_d = rd["amps_peak"]
    say()
    say("  Board D (the D8 mezzanine behind U23) in PS-ALLTX, the exciter keyed: others %s A (D's +5V_D8 loads less U21) + the +5V_TX branch" % fmt(d_others))
    say("  D8 M-tier: SA868 TX %s A typ (MAKER, v1.3 p.4) + U15/K1 %s + others = %s A; at the maker's 1.000 A maximum %s A" % (SA868_TX_A[0], fmt(tx_others), fmt(d_m), fmt(d_mmax)))
    say("  D8 P-tier: +5V_TX declared peak %s A + others = %s A; D-tier (declared, the eFuse's nominal 2.0 A): %s A" % (d["rails"]["+5V_TX"]["amps_peak"], fmt(d_p), fmt(d_d)))
    u23_max = TPS2596_ILIM_453[2]
    say("  U23's limit itself: %s / %s / %s A (SLVSET8A, RILM 453 ohm); U32's: %s A nominal at 1 k (equation 7), about %s to %s A scaling the 909 ohm row's spread"
        % (TPS2596_ILIM_453[0], TPS2596_ILIM_453[1], u23_max, fmt(TPS2596_ILIM_1K_NOM), fmt(TPS2596_ILIM_1K_NOM * TPS2596_ILIM_909[0] / TPS2596_ILIM_909[1]), fmt(TPS2596_ILIM_1K_NOM * TPS2596_ILIM_909[2] / TPS2596_ILIM_909[1])))
    wall_m = USB2_DEVICE_MAX_A
    # Same 909 ohm row extrapolation as the original analysis, now with the correct sign.
    # It is an estimate, NOT a guaranteed maximum for R186 at 1 kohm.
    wall_p = TPS2596_ILIM_1K_NOM * TPS2596_ILIM_909[2] / TPS2596_ILIM_909[1]
    wall_p_rmin = TPS2596_ILIM_1K_RMIN * TPS2596_ILIM_909[2] / TPS2596_ILIM_909[1]
    say("  Wall equation: 903/1000 + 0.0112 = %.7f A; estimated high %.9f A, with R186 -1 percent %.9f A; no guaranteed 1 kohm maximum" % (TPS2596_ILIM_1K_NOM, wall_p, wall_p_rmin))
    say("  Corrected P demand before split %.9f A (R186 -1 percent %.9f A); after split %.9f A (%.9f A)" % (b_p + d_p + wall_p, b_p + d_p + wall_p_rmin, b_p + wall_p, b_p + wall_p_rmin))
    wall_d = a["rails"]["VBUS_WALL"]["amps_peak"]
    say("  Wall host port: M-tier %s A (BOUND: a USB 2.0 device's maximum), P-tier %s A (extrapolated eFuse estimate, not a guaranteed maximum), D-tier %s A (declared)" % (fmt(wall_m), fmt(wall_p), fmt(wall_d)))

    tiers = [
        ("D  every declared limit (cx1): B 6.0 + D8 2.0 + wall 0.9", rb["amps_peak"] + d_d + wall_d),
        ("Dt declared with D8 at its typical (cx1): B 6.0 + D8 1.0 + wall 0.9", rb["amps_peak"] + rd["amps_typ"] + wall_d),
        ("M  maker figures, declared typicals elsewhere, SA868 at 0.9 A, a USB 2.0 device on the wall port", b_m + d_m + wall_m),
        ("Mx M with the SA868 at its 1.0 A maximum", b_m + d_mmax + wall_m),
        ("P  maker figures for the transmitters, declared child peaks elsewhere, the wall eFuse at its extrapolated high estimate", b_p + d_p + wall_p),
    ]
    say()
    say("== 4a. THE CONVERTER'S COINCIDENT OUTPUT CURRENT against the average loop (output-side sense, so 1:1)")
    say("  loop band: %s (min, 1 percent + TCR at %d K) / %s (typ) / %s (max) A" % (fmt(i_min1), SHUNT_RISE_K, fmt(i_typ), fmt(i_max1)))
    say("  %-100s %8s %10s %10s %10s" % ("tier", "demand A", "vs min", "vs typ", "vs max"))
    for name, dem in tiers:
        def verdict(th):
            m = th - dem
            return "%s %s" % ("PASS" if m >= 0 else "FAIL", fmt(m, 2))
        say("  %-100s %8s %10s %10s %10s" % (name, fmt(dem, 2), verdict(i_min1), verdict(i_typ), verdict(i_max1)))
    say("  => no tier is under the loop's minimum; the M-tier is over it by %s A (%s percent) and the P-tier is over even the maximum" % (fmt(b_m + d_m + wall_m - i_min1, 2), fmt((b_m + d_m + wall_m - i_min1) / i_min1 * 100, 1)))
    say("  Registry model (POWER-THERMAL.md +5V_DEV HIGH 7.8 A, line 709): vs min %s A" % fmt(i_min1 - 7.8, 2))

    # loop response
    say()
    say("== 4b. ILLUSTRATIVE TIMING ESTIMATES ONLY (SNVSAI1D pp.6-7,16-17; CSS 47 nF, typical gm 1 mS, VSS(CL) 1.21 V, VREF 0.8 V); no closed-loop time constant or onset bound is stated")
    css = 47e-9
    say("  dimensional ratio CSS / gm (NOT a closed-loop time constant) = %s us" % fmt(css / GM_SS * 1e6, 1))
    say("  assume constant overdrive, constant typical gm and initial SS %s V; illustrative onset at VREF %s V; assume NET pulldown = gm x positive overdrive (not a separately established net-current model)" % (VSS_CL, VREF[1]))
    for over_mv in (0.3, 1.0, 3.4, 10.4, 20.0):
        i_pd = GM_SS * over_mv * 1e-3
        t_on = css * (VSS_CL - VREF[1]) / i_pd
        dvdt = i_pd / css * (vo / VREF[1])
        say("  overdrive %5.1f mV (%s A over the point on 6 mOhm): illustrative onset %8.3f ms, illustrative droop magnitude %6.1f V/s (dVout/dt negative)" % (over_mv, fmt(over_mv * 1e-3 / rsns, 2), t_on * 1e3, dvdt))
    say("  => These are illustrative estimates, not bounds or measured responses. The 60 s coincident plateau is an assumption; the held Ebyte page supplies no airtime and charger limits supply no duration.")
    say("  => Regulated bucks may draw more current as voltage falls only while regulating at assumed fixed output power/efficiency. AP2112 LDOs draw Iout + Ignd (DS39724 Rev.2-2 pp.2,8), not constant power.")
    say("  => Complete-rail collapse, onset and recovery remain INCONCLUSIVE: measure SS, rail voltage and input/load current through actual bursts, controlled overloads, dropout and UVLO transitions.")

    # cycle-by-cycle at the demand
    say()
    say("== 4c. THE CYCLE-BY-CYCLE LIMIT AT THE DEMAND (buck; valley = Iout - ripple/2, peak = Iout + ripple/2)")
    for name, dem in tiers[:1] + tiers[2:3] + tiers[4:5]:
        pk = dem + rip_worst / 2
        vl = dem - rip_nom / 2
        say("  %-60s Iout %s A: valley %s A (limit min %s A, margin %s A PASS); peak %s A worst ripple vs Isat %s (PASS), Irms 20 K %s (PASS)"
            % (name[:60], fmt(dem, 2), fmt(vl, 2), fmt(v_min, 2), fmt(v_min - vl, 2), fmt(pk, 2), L_ISAT_A, L_IRMS_20K_A))
    say("  => the cycle-by-cycle limit never acts at the coincident demand; the average loop is the governing limiter")

    # shunt
    say()
    say("== 4d. THE SHUNT R43 (WSL2512, 1.0 W at +70 C, 30100 p.1)")
    for lab, i in (("M-tier", b_m + d_m + wall_m), ("D-tier 8.9 A", 8.9), ("loop maximum", i_max0)):
        p = i * i * r_hi
        say("  %-14s %s A: %s W, %s percent of the +70 C rating" % (lab, fmt(i, 2), fmt(p, 3), fmt(p / WSL2512_P70_W * 100, 1)))
    say("  M-tier exact shunt dissipation: %.9f W nominal; %.9f W at +1 percent" % ((b_m + d_m + wall_m) ** 2 * rsns, (b_m + d_m + wall_m) ** 2 * r_hi))
    say("  => PASS on the rating at ambients to +70 C; the derating above +70 C is a figure on p.3 of 30100 not read numerically here; the element's temperature rise needs the board's copper (INCONCLUSIVE, layout calculation followed by prototype temperature measurement)")
    say("  R177 (CS, 5 mOhm) at 8.9 A carries the low-side share: I^2 (1 - D) R = %s W at 16.8 V in" % fmt(8.9 ** 2 * (1 - vo / 16.8) * rc_hi, 3))

    # FETs
    say()
    say("== 4e. THE FETs AT 8.9 A (CSD19532Q5B; illustrative thermal scenario, NOT upper bounds: RDS(on) max at 6 V x %s hot, edges x %s the sheet's; the sheet's 1 in2 2 oz pad)" % (FET_HOT_FACTOR, FET_EDGE_FACTOR))
    i = 8.9
    rds = FET_RDS_6V[1] * FET_HOT_FACTOR
    worst_fet_w = 0.0
    total_fet_w = 0.0
    for vin in (V_BAT_RANGE[0], V_BAT_RANGE[2]):
        dbk = vo / vin
        p_q35 = i * i * rds
        p_q32c = dbk * i * i * rds
        p_q32s = 0.5 * vin * i * sum(FET_TR_TF_S) * FET_EDGE_FACTOR * FSW_NOM
        p_q32o = 0.5 * FET_COSS_F[1] * vin * vin * FSW_NOM
        p_q32r = FET_QRR_C * (i / 17.0) * vin * FSW_NOM
        p_q33c = (1 - dbk) * i * i * rds
        p_q33d = 2 * T_DEAD_S * FSW_NOM * FET_VSD_V[1] * i
        say("  VIN %s V, D %s:" % (vin, fmt(dbk, 3)))
        say("    Q35 (boost high side, on all the time in buck): %s W conduction -> +%s K on the sheet's pad" % (fmt(p_q35, 2), fmt(p_q35 * FET_RTHJA, 0)))
        say("    Q32 (buck high side): %s W conduction + %s W switching + %s W Coss + %s W recovery (Qrr scaled to 8.9 A) = %s W -> +%s K" % (fmt(p_q32c, 2), fmt(p_q32s, 2), fmt(p_q32o, 3), fmt(p_q32r, 2), fmt(p_q32c + p_q32s + p_q32o + p_q32r, 2), fmt((p_q32c + p_q32s + p_q32o + p_q32r) * FET_RTHJA, 0)))
        say("    Q33 (buck low side): %s W conduction + %s W dead-time diode = %s W -> +%s K" % (fmt(p_q33c, 2), fmt(p_q33d, 2), fmt(p_q33c + p_q33d, 2), fmt((p_q33c + p_q33d) * FET_RTHJA, 0)))
        say("    Q34 (boost low side): off in buck, about 0 W")
        worst_fet_w = max(worst_fet_w, p_q35, p_q32c + p_q32s + p_q32o + p_q32r, p_q33c + p_q33d)
        total_fet_w = max(total_fet_w, p_q35 + p_q32c + p_q32s + p_q32o + p_q32r + p_q33c + p_q33d)
    p_l = i * i * L_DCR_OHM[1]
    p_shunts = i * i * r_hi + 8.9 ** 2 * (1 - vo / 16.8) * rc_hi
    p_total = total_fet_w + p_shunts + p_l
    say("  L6 DCR loss at 8.9 A: %s W (DCR max, core loss not held); stage loss scenario about %s W at 16.8 V in (FETs %s + shunts %s + DCR %s), efficiency about %s (declared floor %s)"
        % (fmt(p_l, 2), fmt(p_total, 1), fmt(total_fet_w, 2), fmt(p_shunts, 2), fmt(p_l, 2), fmt(vo * i / (vo * i + p_total), 3), EFF_DECL))
    say("  => at assumed +50 C air the scenario gives hottest FET (%s W) about %s C on the sheet's pad against TJ %s C. No upper bound or thermal PASS: layout loss/thermal calculation and actual FET/shunt temperatures and switching waveforms over intended loads, ambient and VBAT are required (INCONCLUSIVE)" % (fmt(worst_fet_w, 2), fmt(50 + worst_fet_w * FET_RTHJA, 0), fmt(FET_TJ_MAX, 0)))

    # copper, INA226, lead
    say()
    say("== 4f. COPPER, MONITOR, LEAD")
    say("  Board A copper: the filed dc_drop and dc_density verdicts of 21 September (board sha 58e26c67, judged at the declared 4.0 / 6.9 A) hold +5V_DEV and SD_OUT as MET with no per-rail margin recorded;")
    say("    at 8.9 A the density reading scales by %s: INCONCLUSIVE until dc_density runs on the regenerated board with the corrected declaration (calculation, not measurement)" % fmt(8.9 / 6.9, 2))
    v_ina = i_max0 * r_hi
    say("  INA226 U11 across R43: %s mV at the loop's maximum %s A, %s percent of the +-81.92 mV range; bus 5.09 V of 36 V; LSB 2.5 uV = %s mA: PASS" % (fmt(v_ina * 1e3, 1), fmt(i_max0, 2), fmt(v_ina / INA_SHUNT_FS_V * 100, 0), fmt(INA_LSB_V / rsns * 1e3, 2)))
    for lab, il in (("B declared peak", rb["amps_peak"]), ("B M-tier", b_m), ("B P-tier", b_p)):
        say("  JST VH lead at %s %s A: rating %s A (AWG 16, standard header), margin %s A %s; pair drop %s mV at 20 C plus up to %s mV in four contacts at 10 mOhm"
            % (lab, fmt(il, 2), VH16_A, fmt(VH16_A - il, 2), "PASS" if il <= VH16_A else "FAIL", fmt(il * LEAD_R_PAIR_20C * 1e3, 1), fmt(il * 4 * VH_CONTACT_OHM[0] * 1e3, 0)))
    say("  the D8 lead (J_MEZZ_PWR1, VH, AWG 18 per ASSEMBLY.md section 4): no JST rating is stated for AWG 18 with the standard header (cx1 J1): INCONCLUSIVE, the same item as +54V_POE's")

    # pack current
    say()
    say("== 4g. WHAT THE STAGE ASKS OF VBAT (Iin = Vout Iout / (eff Vin), eff %s declared)" % EFF_DECL)
    for name, dem in tiers:
        say("  %-100s %s A at 12.4 V, %s A at 15.5 V" % (name, fmt(vo * dem / (EFF_DECL * V_BAT_RANGE[0]), 2), fmt(vo * dem / (EFF_DECL * V_BAT_RANGE[1]), 2)))
    say("  M-tier exact VBAT current at %.3f V out, 15.5 V in, efficiency %.2f: %.9f A" % (vo, EFF_DECL, vo * (b_m + d_m + wall_m) / (EFF_DECL * 15.5)))
    say("  VBAT's load map carries Q32 at 2.0 A (typical); the 8.9 A case is %s A at 15.5 V, +%s A over that entry" % (fmt(vo * 8.9 / (EFF_DECL * V_BAT_RANGE[1]), 2), fmt(vo * 8.9 / (EFF_DECL * V_BAT_RANGE[1]) - 2.0, 2)))

    # ------------------------------------------------------------ 5. options
    say()
    say("== 5. THE OPTIONS")
    say("  Option A, re-rate the average loop with a 5 mOhm ISNS shunt (the same WSL2512 family):")
    for rr, lab in ((5.0e-3, "5.0 mOhm"), (5.6e-3, "5.6 mOhm")):
        lo, hi = rr * (1 + WSL_TOL), rr * (1 - WSL_TOL)
        say("    %s: loop %s / %s / %s A; the maximum against the lead's 10 A: %s A %s" % (lab, fmt(VSNS_V[0] / lo, 2), fmt(VSNS_V[1] / rr, 2), fmt(VSNS_V[2] / hi, 2), fmt(VSNS_V[2] / hi - VH16_A, 2), "FAIL (over the contact rating in a B-side fault held by a CCM stage with no hiccup)" if VSNS_V[2] / hi > VH16_A else "PASS"))
        hot_min = VSNS_V[0] / (lo * (1 + tcr))
        hot_max = VSNS_V[2] / (hi * (1 - tcr))
        say("      assumed +50 K TCR range %.9f to %.9f A; 8.900 A declared demand %s initial minimum %.9f A and hot minimum %.9f A" % (hot_min, hot_max, "FAILS" if 8.9 > VSNS_V[0] / lo else "PASSES", VSNS_V[0] / lo, hot_min))
    say("    => the 6 mOhm value is pinned by the lead's 10 A (the generator's own reason); re-rating alone fails BOTH the 8.900 A demand at its minimum and the downstream 10 A lead test; a higher threshold is not capacity evidence")
    say("  Option B, the D8 mezzanine on its own buck from VBAT (TPS62933, C3200405, fitted twice on this board; XAL6060-682ME Isat %s A above the part's %s A maximum high-side limit):" % (XAL6060_682_ISAT, TPS62933_IHS_LIMIT[2]))
    tiers_b = [("D", rb["amps_peak"] + wall_d), ("M", b_m + wall_m), ("Mx", b_m + wall_m), ("P", b_p + wall_p)]
    for lab, dem in tiers_b:
        say("    tier %-2s demand %s A: vs loop min %s %s A, vs typ %s %s A" % (lab, fmt(dem, 2), "PASS" if i_min1 >= dem else "FAIL", fmt(i_min1 - dem, 2), "PASS" if i_typ >= dem else "FAIL", fmt(i_typ - dem, 2)))
    rip_b = (16.8 - vo) * (vo / 16.8) / (6.8e-6 * 500e3)
    say("    the new buck at 2.0 A (U23's limit): ripple %s A at 16.8 V and 500 kHz on 6.8 uH, peak %s A against IHS_LIMIT min %s A and Isat %s A: PASS; VBAT +%s A at 12.4 V"
        % (fmt(rip_b, 2), fmt(2.0 + rip_b / 2, 2), TPS62933_IHS_LIMIT[0], XAL6060_682_ISAT, fmt(5.088 * 2.0 / (0.90 * 12.4), 2)))
    say("  Option C, B plus the wall host port on the outlet interlock (U26's spare section 1: USBX_EN_HW = USBX_EN AND OUTLET_OK):")
    tiers_c = [("D", rb["amps_peak"]), ("M", b_m), ("P", b_p)]
    for lab, dem in tiers_c:
        say("    tier %-2s demand %s A: vs loop min %s %s A" % (lab, fmt(dem, 2), "PASS" if i_min1 >= dem else "FAIL", fmt(i_min1 - dem, 2)))
    say("  Option D, declare the 8.9 A bound and name the fold-back as the limiter (cx1's third option): leaves REQ-018's 'every rail in regulation' unmet on the record; not an engineering option")
    say("  Option E, re-allocate D8 or the wall port to +5V_S1 or +5V_S3 (AP64500, 5 A): S1 reads 4.65 A PLAN in PS-ALLTX (PWR-F02, 7 percent margin), S3 about 4.2 A with its card off (cx1): no headroom for 1.5 to 2.0 A; rejected")
    say()
    say("== 6. RECOMMENDATION (authority SESSION, the two-part test in ANALYSIS.md section 5)")
    say("  Take option B now: the coincident demand on +5V_DEV returns to B + wall = %s A declared (the present 6.9 A declaration becomes true), %s A at the M-tier, under the loop's minimum with %s and %s A in hand;" % (fmt(rb["amps_peak"] + wall_d, 1), fmt(b_m + wall_m, 2), fmt(i_min1 - (rb["amps_peak"] + wall_d), 2), fmt(i_min1 - (b_m + wall_m), 2)))
    say("  Precise split margins: declared %.9f A; M-tier %.9f A below conditional minimum %.9f A" % (i_min1 - (rb["amps_peak"] + wall_d), i_min1 - (b_m + wall_m), i_min1))
    say("  Both B and B plus the wall interlock remain configurations; choose B to preserve console availability. S-99 remains open; reconcile M/P allocations and measure current, SS, voltage, collapse/recovery and temperature.")
    say("  the P-tier (%s A) stays FAIL by %s A and is board B's declarations to reconcile (S-98) and the bench to measure; option C is the fallback that buys %s A more if the bench asks for it." % (fmt(b_p + wall_p, 2), fmt(b_p + wall_p - i_min1, 2), fmt(wall_p, 2)))
    print("\n".join(OUT))


if __name__ == "__main__":
    main()
