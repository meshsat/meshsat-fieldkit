#!/usr/bin/env python3
"""r11_dep.py: board A's front-end current-limit resistor R11, the dependency Option A(i) rests on (stream r11dep,
MESHSAT-1357, 30 September 2026; the owner's instruction of that day: "Keep the current-limit resistor dependency
explicit. Check the proposed setting, tolerances and consequences for the affected power path, component ratings and
thermal margins using manufacturer sources. Distinguish performance of the held circuit from performance conditional on
the proposed change. Track implementation and physical verification separately.").

PROTOTYPE DESIGN, desk arithmetic: nothing is built, powered or measured, no generator is edited and no requirement
changes. Every figure carries its basis: MAKER (document and page, read here from its text layer or, for a plotted curve,
by pixel), NETLIST (board A's or board E's committed netlist), MODELED (the energy model's records) or INFERRED (a method
stated beside it). ASSUMPTION marks a figure no document gives that the analysis must take to proceed.

The held circuit: R11 10 mOhm (NETLIST), bought as C2903468 (lcsc_fill.py; LCSC's answer: Milliohm HoJLR2512-3W-10mR-1%).
The proposed change: R11 6.2 mOhm (a1elec CHARGER.md section 2 and energy_two_pack.py's entry E2), rated here as the same
maker's series at 6.2 mOhm (HoJLR2512, 3 W).

Run from the repository root:  python3 v2/docs/records/r11dep/r11_dep.py > v2/docs/records/r11dep/r11_dep.out
Needs pdftotext, pdftoppm and Pillow. Deterministic for the pinned files. Exit 3: an input is missing or not as expected."""
import ast
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import netlist_sexp as N  # noqa: E402
import track_current as TC  # noqa: E402
import yaml  # noqa: E402
from PIL import Image  # noqa: E402

NET_A = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"
NET_E = "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"
LCSC_FILL = "v2/ecad/tools/lcsc_fill.py"
READING = "v2/docs/records/r11dep/inputs/lcsc-C2903468-2026-09-30.json"
HOJLR = ("v2/vendor/passives/milliohm-hojlr2512-series.pdf", "3224518dbc8bdc858a96cfde88de2611494550f95406f6b65130c232cdfc93fb")
LM5176 = "v2/vendor/ti/lm5176-datasheet.pdf"
BQ25731 = "v2/vendor/ti/bq25731-datasheet.pdf"
XAL1010 = "v2/vendor/power/coilcraft-xal1010.pdf"
CSD = "v2/vendor/power/ti-csd19532q5b-n-fet.pdf"
EEHZK = "v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf"
MILLMAX = "v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf"
LT8705A = "v2/vendor/power/lt8705a.pdf"
ENVELOPE = "v2/ecad/tools/pcb_envelope.yaml"
GEN_A = "v2/ecad/tools/gen_sch_a.py"
GEN_E = "v2/ecad/tools/gen_sch_e.py"
TWO_PACK = "v2/docs/records/a1elec/energy_two_pack.py"
EB_OUT = "v2/docs/records/l3plane/energy_basis.out"
KELVIN = "v2/ecad/pcb-a-power-a23/routed/kelvin_check.verdict.json"
INTENT_A = "v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json"
BOARD_A = "v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb"
VR_OUT = "v2/docs/records/l3plane/vbus20_range.out"

R11_HELD, R11_PROP = 0.010, None      # the proposed value is read from energy_two_pack.py below
R11_TEMP_MAX = 100.0                  # ASSUMPTION: R11's own temperature at most 100 C (the worst inside air plus its own and
                                      # the board's rise; HoJLR2512's sheet gives no thermal resistance)
VIN_TRACKER = 15.1                    # NETLIST/record: board E's tracker output TRK_OUT, FBOUT set at 15.1 V (gen_sch_e.py)
VIN_TREE = 9.0                        # the tree's own convention for VIN_RAW's declaration (board E _FE_A, R8E-N01)
VIN_MAX = 36.0                        # REQ-015: 9 to 36 V in service (vbus20_range and s120 read it the same way)
R12_CS = 0.005                        # NETLIST: R12 5mOhm, U2's CS resistor (section 1's facts check its value and net)
ETA_FE = 0.93                         # DECLARED (gen_sch_a.py VBUS20 intent): the low end, the conservative one for current


def refuse(msg):
    sys.stderr.write("r11_dep: %s; refusing\n" % msg)
    sys.exit(3)


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def page(rel, n):
    return subprocess.run(["pdftotext", "-layout", "-f", str(n), "-l", str(n), os.path.join(TOP, rel), "-"],
                          capture_output=True, text=True, check=True).stdout


def need(text, pat, what):
    m = re.search(pat, text, re.M)
    if not m:
        refuse("%s not found" % what)
    return m


def head_equal(rel):
    text = open(os.path.join(TOP, rel), encoding="utf-8").read()
    head = subprocess.run(["git", "-C", TOP, "show", "HEAD:" + rel], capture_output=True, text=True).stdout
    if text != head:
        refuse("%s differs from HEAD's" % rel)
    return text


def fig8_readings():
    """CSD19532Q5B p.6 Figure 8, the VGS = 6 V curve, normalized RDS(on) at case temperatures, by pixel (INFERRED)."""
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["pdftoppm", "-f", "6", "-l", "6", "-r", "300", "-png", os.path.join(TOP, CSD), os.path.join(td, "p")], check=True)
        im = Image.open(os.path.join(td, [f for f in os.listdir(td) if f.endswith(".png")][0])).convert("RGB")
        im.load()
    px = im.load()

    def dark(p):
        return p[0] < 80 and p[1] < 80 and p[2] < 80
    rows = [y for y in range(430, 1000) if sum(1 for x in range(440, 1180) if dark(px[x, y])) > 600]
    cols = [x for x in range(420, 1210) if sum(1 for y in range(465, 965) if dark(px[x, y])) > 480]
    top = [y for y in rows if 450 < y < 470]
    bot = [y for y in rows if 965 < y < 985]
    left = [x for x in cols if 425 < x < 440]
    right = [x for x in cols if 1185 < x < 1200]
    if not (top and bot and left and right):
        refuse("CSD19532Q5B p.6 Figure 8's frame not found")
    t, b, l, r = sum(top) / len(top), sum(bot) / len(bot), sum(left) / len(left), sum(right) / len(right)
    # gridlines every 0.2 of the 0.4 to 2.2 scale: check 1.0 and 1.6 sit where the scale puts them
    for v in (1.0, 1.6):
        y = int(round(t + (2.2 - v) / 1.8 * (b - t)))
        if max(sum(1 for x in range(int(l) + 10, int(r) - 10) if px[x, yy][0] < 170) for yy in (y - 2, y - 1, y, y + 1, y + 2)) < 300:
            refuse("CSD19532Q5B Figure 8's %.1f gridline not where the scale puts it" % v)
    out = {25.0: 1.0}          # the figure is normalized at 25 C
    for tc in (50.0, 75.0, 100.0, 125.0, 150.0):
        cx = int(round(l + (r - l) * (tc + 75.0) / 250.0))
        vals = []
        for is_c in ((lambda q: q[2] > 170 and q[0] < 90 and q[1] < 90), (lambda q: q[0] > 170 and q[1] < 90 and q[2] < 90)):
            ys = []
            for dx in (-6, -5, -4, 4, 5, 6):
                ys += [y for y in range(int(t) + 3, int(b) - 3) if is_c(px[cx + dx, y])]
            if ys:
                ys.sort()
                vals.append(2.2 - 1.8 * (ys[len(ys) // 2] - t) / (b - t))
        if not vals:
            refuse("Figure 8's curves not read at %.0f C" % tc)
        out[tc] = max(vals)    # the higher of the VGS 6 V and 10 V curves where both show: the larger loss
    return out


def main():
    P = print
    # ---------------------------------------------------------------- inputs
    a = N.load(os.path.join(TOP, NET_A))
    e = N.load(os.path.join(TOP, NET_E))
    ca, pa = a["components"], a["pins"]

    def nets(ref):
        return {p: v["net"] for p, v in pa[ref].items()}
    netmem = {}
    for ref, pins in pa.items():
        for p, v in pins.items():
            netmem.setdefault(v["net"], []).append(ref)
    facts = [
        ("R11", ca["R11"]["value"].startswith("10mOhm 1% 2512") and nets("R11") == {"1": "FE_OUT", "2": "VBUS20"}),
        ("ISNS filter", ca["R160"]["value"].startswith("100R") and ca["R161"]["value"].startswith("100R") and ca["C128"]["value"] == "1n"
         and nets("U2")["14"] == "FE_ISNS_P" and nets("U2")["13"] == "FE_ISNS_N"),
        ("CS sense R12", ca["R12"]["value"].startswith("5mOhm") and nets("R12")["1"] == "FE_CS"),
        ("L1", "XAL1010-103ME" in ca["L1"]["value"]),
        ("Q2 to Q5", all("CSD19532Q5B" in ca[q]["value"] for q in ("Q2", "Q3", "Q4", "Q5"))),
        ("input caps C11 C12", all(ca[c]["value"] == "10u 100V X7R 1210" and nets(c)["1"] == "VIN_RAW" for c in ("C11", "C12"))),
        ("VIN_RAW entry J_VR1 to J_VR4", all(("9 A spring pin" in ca["J_VR%d" % i]["value"]) for i in range(1, 5))),
        ("no fuse on board A's VIN_RAW", not any(r.startswith("F") for r in netmem["VIN_RAW"])),
        ("U2 BIAS on VBUS20", nets("U2")["24"] == "VBUS20"),
        ("MODE", nets("R119") == {"1": "FE_MODE", "2": "FE_VCC"}),
        ("slope C147", ca["C147"]["value"] == "680p" and nets("C147")["1"] == "FE_SLOPE"),
        ("soft start C7", ca["C7"]["value"] == "4.7u" and nets("C7")["1"] == "FE_SS"),
        ("RT R8", ca["R8"]["value"].startswith("40.2k")),
    ]
    if not all(ok for _n, ok in facts):
        refuse("a board A netlist fact does not hold: %s" % [n for n, ok in facts if not ok])
    bulk = [r for r in netmem["VBUS20"] if ca[r]["value"].startswith("330u 35V Panasonic EEHZK1V331P")]
    ce = e["components"]
    e_q2, e_r5, e_f1, e_f2, e_l1 = ce["Q2"]["value"], ce["R5"]["value"], ce["F1"]["value"], ce["F2"]["value"], ce["L1"]["value"]
    # purchase identity
    tree = ast.parse(open(os.path.join(TOP, LCSC_FILL), encoding="utf-8").read())
    mp = [ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == "MAP" for t in n.targets)][0]
    code = [c for (v, f), c in mp.items() if re.match(v, ca["R11"]["value"]) and f in ca["R11"]["footprint"]][0]
    rd = json.load(open(os.path.join(TOP, READING), encoding="utf-8"))
    if code != "C2903468" or rd["code"] != code or rd["model"] != "HoJLR2512-3W-10mR-1%":
        refuse("R11's purchase identity is not C2903468 HoJLR2512-3W-10mR-1%")
    # the proposed value and U3's setting
    tp = open(os.path.join(TOP, TWO_PACK), encoding="utf-8").read()
    r11_prop = float(need(tp, r'"fe_r11_draft_mohm": \(([\d.]+),', "energy_two_pack.py fe_r11_draft_mohm").group(1)) / 1000.0
    iin_set = float(need(tp, r'"u3_iin_draft_a": \(([\d.]+),', "energy_two_pack.py u3_iin_draft_a").group(1))
    # HoJLR2512
    if sha(HOJLR[0]) != HOJLR[1]:
        refuse("the HoJLR2512 sheet is not the pinned file")
    h = "".join(page(HOJLR[0], n) for n in (1, 2, 3, 4))
    need(h, r"3W\s+0\.5~500mR", "HoJLR2512 p.1 the 3 W range")
    need(h, r"±50 \(2mR~500mR\)", "HoJLR2512 p.2 TCR")
    need(h, r"-50℃~\+170℃", "HoJLR2512 p.2 operating range")
    need(h, r"70℃", "HoJLR2512 p.2 derating onset")
    need(h, r"5 X rated power for 5s", "HoJLR2512 p.4 short-time overload")
    need(h, r"1000hours at rated power, 70℃", "HoJLR2512 p.4 load life")
    p_rated, tcr_r, t_derate0, t_derate1, t_max_r = 3.0, 50e-6, 70.0, 170.0, 170.0
    # LM5176
    t5, t6, t7, t17, t20, t24 = (page(LM5176, n) for n in (5, 6, 7, 17, 20, 24))
    vsns = tuple(float(x) / 1000.0 for x in need(t7, r"VSNS\s+Average current loop regulation target\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "p.7 VSNS").groups())
    ib_isns = float(need(t7, r"ISNS\s+ISNS\(\+\), ISNS\(\u2013\) pin bias currents\s+VISNS\(\+\) = VISNS\(\u2013\) = VIN = 24 V\s+([\d.]+)", "p.7 ISNS bias").group(1)) * 1e-6
    vcs_buck = tuple(float(x) / 1000.0 for x in need(t7, r"VCS\(BUCK\)\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "p.7 buck valley").groups())
    vcs_boost = tuple(float(x) / 1000.0 for x in need(t7, r"VCS\(BOOST\)\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "p.7 boost peak").groups())
    gm_ss = float(need(t7, r"Gm\s+gm of soft-start pulldown amplifier\s+([\d.]+)\s+mS", "p.7 CC loop gm").group(1)) * 1e-3
    fsw = tuple(float(x) * 1e3 for x in need(t6, r"fSW\(1\)\s+Switching frequency 1\s+RT = 40 k\S+\s+(\d+)\s+(\d+)\s+(\d+)", "p.6 fSW").groups())
    iq_vin = float(need(t6, r"VIN operating current\s+VEN/UVLO = 2 V, VFB = 0\.9 V\s+([\d.]+)\s+([\d.]+)\s+mA", "p.6 VIN operating current").group(2)) * 1e-3
    need(t5, r"ISNS\(\+\), ISNS\(\u2013\)\s+Average current sense common mode range\s+0\s+55\s+V", "p.5 ISNS common mode")
    need(t17, r"ICL\(AVG\)", "p.17 Equation 4")
    need(t17, r"internal 50-mV\s*\n?\s*reference", "p.17 the 50 mV reference")
    need(t20, r"MODE to VCC", "p.20 MODE to VCC: no hiccup")
    need(t24, r"The filter resistance should not exceed 100 Ω|The filter resistance should not exceed 100 Ω", "p.24 ISNS filter limit")
    need(t24, r"RSENSE u ACS", "p.24 Equation 26 on RSENSE")
    drv = [float(x) for x in re.findall(r"Driver peak (?:source|sink) current\s+(?:VBOOT - VSW = 7 V\s+)?([\d.]+)\s+A", page(LM5176, 8))]
    if len(drv) < 2:
        refuse("p.8 driver currents")
    i_src, i_snk = drv[0], drv[1]
    # BQ25731 U3
    b1, b80 = page(BQ25731, 1), page(BQ25731, 80)
    acc = float(need(b1, r"±([\d.]+)% Input current regulation", "SLUSE66A p.1 accuracy").group(1)) / 100.0
    need(b80, r"Additional 100-mA \(10-m\S+ sense", "SLUSE66A p.80 the 100 mA")
    u3_max = max(iin_set + 0.1, iin_set * (1 + acc))
    # XAL1010-103ME
    x1 = page(XAL1010, 1)
    mx = need(x1, r"XAL1010-103ME_\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "XAL1010 p.1 the 103ME row")
    l_nom, dcr_typ, dcr_max, isat, irms20, irms40 = (float(mx.group(i)) for i in (1, 2, 3, 5, 6, 7))
    l_nom *= 1e-6
    dcr_max *= 1e-3
    need(x1, r"±20%", "XAL1010 inductance tolerance")
    need(x1, r"Ambient temperature \u201340°C to \+125°C with \(40°C rise\) Irms current", "XAL1010 ambient with 40 K rise")
    need(x1, r"Maximum part temperature \+165°C", "XAL1010 maximum part temperature")
    need(x1, r"inductance drop of 30% \(typ\)", "XAL1010 Isat definition")
    # CSD19532Q5B
    c1, c3 = page(CSD, 1), page(CSD, 3)
    rds6_max = float(need(c3, r"VGS = 6 V, ID = 17 A\s+([\d.]+)\s+([\d.]+)\s+m", "CSD p.3 RDS(on) at 6 V").group(2)) * 1e-3
    rtja = float(need(c3, r"RθJA\s+Junction-to-Ambient Thermal Resistance \(1\) \(2\)\s+(\d+)", "CSD p.3 RthetaJA").group(1))
    qgd = float(need(c3, r"Qgd\s+Gate Charge Gate to Drain\s+([\d.]+)", "CSD p.3 Qgd").group(1)) * 1e-9
    qoss = float(need(c3, r"Qoss\s+Output Charge\s+VDS = 50 V, VGS = 0 V\s+(\d+)", "CSD p.3 Qoss").group(1)) * 1e-9
    need(c1, r"\u201355 to 150", "CSD p.1 TJ range")
    need(c3, r"Device mounted on FR4 material with 1-inch2 \(6\.45-cm2\), 2-oz", "CSD p.3 the RthetaJA board")
    k_rds = fig8_readings()
    # EEHZK1V331P
    z2 = page(EEHZK, 2)
    ripple_bulk = float(need(z2, r"330\s+10\.0\s+10\.2\s+10\.5\s+G\s+(\d+)\s+(\d+)\s+[\d.]+\s+EEHZK1V331P", "EEHZK p.2 the 331P row").group(1)) / 1000.0
    need(z2, r"Ripple current \(100 kHz / \+125 ℃\)", "EEHZK ripple condition")
    # Mill-Max
    mm_ = " ".join(page(MILLMAX, 1).split())
    pin_a = float(need(mm_, r"capable of carrying (\d+) amps continuous cur- rent at a low 10° C temperature rise", "Mill-Max 9 A at 10 C").group(1))
    # LT8705A (board E's tracker), E and I grades
    l3 = page(LT8705A, 3)
    vcs_trk = tuple(float(x) / 1000.0 for x in need(l3, r"Buck Mode, Minimum M2 Switch Duty Cycle\s*\n\s*\(LT8705AE, LT8705AI\)\s+l\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "8705af p.3 buck sense").groups())
    r5 = 0.005 if e_r5.startswith("5 mOhm") else refuse("board E R5 not 5 mOhm")
    # envelope, declarations, the energy records
    env = yaml.safe_load(open(os.path.join(TOP, ENVELOPE), encoding="utf-8"))
    t_air = max(env["worst_inside_air_c"]["lid_open"], env["worst_inside_air_c"]["lid_closed"])
    t_cold = env["ambient_c"]["in_use"]["min"]
    ga = open(os.path.join(TOP, GEN_A), encoding="utf-8").read()
    ge = open(os.path.join(TOP, GEN_E), encoding="utf-8").read()
    vb_decl = need(ga, r'_intent\.rail\("VBUS20", 20\.0, ([\d.]+), ([\d.]+), "R11"', "gen_sch_a.py VBUS20 declaration").groups()
    vin_decl = eval(need(ga, r"_VIN_RAW_A = (round\([^)]*\))", "gen_sch_a.py _VIN_RAW_A").group(1))
    trk_decl = eval(need(ge, r"_TRK_A = (round\([^)]*\))", "gen_sch_e.py _TRK_A").group(1))
    eb = head_equal(EB_OUT)
    vr = head_equal(VR_OUT)
    v_bus_max = float(need(vr, r"the envelope, any in-use condition\s+min [\d.]+ V, nominal [\d.]+ V, max ([\d.]+) V", "vbus20_range.out max").group(1))
    gen_rows = re.findall(r"^\s+(4S\d+P)\s+GEN\s+NOT MET, ([\d.]+) unserved\s+N/N\s+NOT MET, ([\d.]+) unserved", eb, re.M)
    we_rows = re.findall(r"^\s+(4S1[45]P)\s+WE\s{2,}(.+?)\s{2,}([YN]/[YN])\s+(.+?)\s{2,}([YN]/[YN])", eb, re.M)
    nom_rows = re.findall(r"^\s+(4S1[45]P)\s+NOM\s{2,}(.+?)\s{2,}([YN]/[YN])\s+(.+?)\s{2,}([YN]/[YN])", eb, re.M)
    gen_u3 = need(eb, r"GEN\s+board A AS GENERATED: R11 10 mOhm, the front end's limit ([\d.]+) A minimum, U3's limit set under it at ([\d.]+) A"
                  r" \(entry E1; its ([\d.]+) A maximum", "energy_basis.out GEN definition").groups()
    if len(gen_rows) != 3 or len(we_rows) != 2 or len(nom_rows) != 2:
        refuse("energy_basis.out's GEN, NOM and WE rows not parsed")

    # ---------------------------------------------------------------- the limit bands
    other_i = iq_vin + 4 * 62e-9 * fsw[2] + 21.0 / 100e3 + 21.0 / 250e3     # INFERRED, the VBUS20 currents through R11 besides U3
    offs = ib_isns * 100.0                                                  # INFERRED: one pin's typical bias over its 100 Ohm
    dt_r = max(abs(t_cold - 25.0), abs(R11_TEMP_MAX - 25.0))

    def band(r):
        lo = (vsns[0] - offs) / (r * (1 + 0.01) * (1 + tcr_r * dt_r))
        hi = (vsns[2] + offs) / (r * (1 - 0.01) * (1 - tcr_r * dt_r))
        return lo, vsns[1] / r, hi
    held, prop = band(R11_HELD), band(r11_prop)
    serv = u3_max + other_i

    P("BOARD A'S FRONT-END CURRENT-LIMIT RESISTOR R11: THE HELD CIRCUIT AND THE PROPOSED CHANGE (r11_dep.py, stream r11dep,")
    P("MESHSAT-1357). PROTOTYPE DESIGN: nothing built, powered or measured; no generator edited; no requirement changed.")
    P("Basis per figure: MAKER (page), NETLIST, MODELED, INFERRED (method stated), ASSUMPTION (a figure no document gives).")
    P("")
    P("1. THE CIRCUIT (NETLIST %s, sha256/16 %s; board E %s, sha256/16 %s)" % (NET_A, sha(NET_A)[:16], NET_E, sha(NET_E)[:16]))
    P("   R11 %s from FE_OUT to VBUS20: the LM5176 U2's AVERAGE (ISNS) current sense, in series with its OUTPUT" % ca["R11"]["value"])
    P("   ISNS filter R160, R161 %s and C128 %s into U2 pins 14 and 13; R12 %s is the cycle-by-cycle CS resistor" % (
        ca["R160"]["value"].split(" (")[0], ca["C128"]["value"], ca["R12"]["value"].split(" (")[0]))
    P("   L1 %s; Q2 to Q5 %s" % (ca["L1"]["value"], ca["Q2"]["value"].split(" (")[0]))
    P("   VIN_RAW: C11, C12 %s; J_VR1 to J_VR4 '%s'; no fuse on board A's VIN_RAW" % (ca["C11"]["value"], ca["J_VR1"]["value"].split(" (")[0]))
    P("   VBUS20: %d x EEHZK1V331P bulk (%s); U2's BIAS (pin 24) on VBUS20, so its supply current passes R11" % (len(bulk), ", ".join(sorted(bulk))))
    P("   MODE: R119 to VCC (no hiccup, SNVSAI1D p.20); SLOPE C147 %s; SS C7 %s; RT R8 %s" % (ca["C147"]["value"], ca["C7"]["value"], ca["R8"]["value"]))
    P("   board E's VIN_RAW sources: the vehicle entry (F1 '%s', LM5069 U6) and the panel tracker (LT8705A, R5 '%s', L1 '%s')," % (
        e_f1.split(":")[0], e_r5.split(" (")[0], e_l1.split(" (")[0]))
    P("   ORed through the ideal diode U4 with Q2 '%s'; the panel input F2 '%s'" % (e_q2.split(" (")[0], e_f2.split(":")[0]))
    P("   facts: %d of %d hold" % (sum(1 for _n, ok in facts if ok), len(facts)))
    P("")
    P("2. THE PARTS AND THE MAKERS' FIGURES")
    P("   R11 held: %s (lcsc_fill.py); LCSC's answer (%s): %s %s, %s, %s (read %s)" % (code, READING, rd["brand"], rd["model"],
                                                                                      rd["params"]["Power(Watts)"], rd["params"]["Tolerance"], rd["read_utc"]))
    P("   HoJLR2512 series (MAKER, %s, sha256/16 %s): 2512, 3 W for 0.5 to 500 mOhm (p.1); TCR +-50 ppm/K for 2 to 500 mOhm;" % (HOJLR[0], HOJLR[1][:16]))
    P("     -50 to +170 C, derated linearly from 70 C (100 %) to 170 C (0 %) (p.2); rated current sqrt(P/R) (p.3); short-time")
    P("     overload 5 x rated power for 5 s, load life 1000 h at rated power and 70 C, each within +-1 % (p.4)")
    P("   R11 proposed: %.1f mOhm (energy_two_pack.py fe_r11_draft_mohm; a1elec CHARGER.md 2), rated here as the same series," % (r11_prop * 1e3))
    P("     HoJLR2512-3W-6.2mR-1% by the maker's own part-number scheme (p.1): the value lies in its 3 W range; ORDER CODE NOT")
    P("     ESTABLISHED (no catalogue answer read for it)")
    P("   LM5176 (MAKER, %s): VSNS %.0f / %.0f / %.0f mV over TJ -40 to 125 C (p.7), ICL(AVG) = 50 mV / RSNS (Equation 4, p.17)," % (
        LM5176, vsns[0] * 1e3, vsns[1] * 1e3, vsns[2] * 1e3))
    P("     ISNS pin bias %.0f uA TYPICAL (p.7, no limit printed), ISNS common mode 0 to 55 V (p.5), CC loop gm %.0f mS into SS (p.7)," % (
        ib_isns * 1e6, gm_ss * 1e3))
    P("     boost peak %.0f / %.0f / %.0f mV and buck valley %.0f / %.0f / %.0f mV on CS (p.7), fSW %.0f / %.0f / %.0f kHz at RT 40 k (p.6)" % (
        vcs_boost[0] * 1e3, vcs_boost[1] * 1e3, vcs_boost[2] * 1e3, vcs_buck[0] * 1e3, vcs_buck[1] * 1e3, vcs_buck[2] * 1e3,
        fsw[0] / 1e3, fsw[1] / 1e3, fsw[2] / 1e3))
    P("   U3 BQ25731 (MAKER, %s): IIN_HOST %.1f A set; its maximum %.3f A, the larger of the 100 mA of p.80 and the +-%.1f %% of p.1" % (
        BQ25731, iin_set, u3_max, acc * 100))
    P("   L1 XAL1010-103ME (MAKER, %s p.1): %.0f uH +-20 %%, DCR %.2f / %.2f mOhm, Isat %.1f A (30 %% drop, typical, 25 C)," % (
        XAL1010, l_nom * 1e6, dcr_typ, dcr_max * 1e3, isat))
    P("     Irms %.1f A (20 K rise) and %.1f A (40 K rise); ambient -40 to +125 C with the 40 K Irms; part at most 165 C" % (irms20, irms40))
    P("   Q2 to Q5 CSD19532Q5B (MAKER, %s): RDS(on) %.1f mOhm maximum at VGS 6 V, 25 C (p.3); RthetaJA %.0f C/W maximum on a" % (CSD, rds6_max * 1e3, rtja))
    P("     1 in2 2 oz pad (p.3); TJ -55 to 150 C (p.1); Qgd %.1f nC, Qoss %.0f nC at 50 V (p.3); Figure 8 (p.6), the higher of its" % (qgd * 1e9, qoss * 1e9))
    P("     VGS 6 V and 10 V curves, read by pixel")
    P("     (INFERRED): " + ", ".join("%.0f C %.2f" % (k, v) for k, v in sorted(k_rds.items())))
    P("   VBUS20 bulk EEHZK1V331P (MAKER, %s p.2): %.1f A rms at 100 kHz, 125 C; the correction factor is 1.00 from 100 to 500 kHz" % (EEHZK, ripple_bulk))
    P("   J_VR spring pins (MAKER, %s): %.0f A continuous at a 10 C rise (the 085X series)" % (MILLMAX, pin_a))
    P("   board E's tracker LT8705A (MAKER, %s p.3, E and I grades): buck current sense %.0f / %.0f / %.0f mV over R5 5 mOhm" % (
        LT8705A, vcs_trk[0] * 1e3, vcs_trk[1] * 1e3, vcs_trk[2] * 1e3))
    P("   the kit: the worst inside air in use %.1f C, the in-use minimum %.0f C (%s)" % (t_air, t_cold, ENVELOPE))
    P("")

    # ---------------------------------------------------------------- 3. the bands
    P("3. THE FRONT END'S AVERAGE CURRENT LIMIT (min / typical / max), every tolerance stacked (R11 at +-1 %, its TCR over")
    P("   %.0f K from +25 C with R11 between %.0f C and an ASSUMED %.0f C, the ISNS bias over the 100 Ohm filter +-%.1f mV INFERRED)" % (
        dt_r, t_cold, R11_TEMP_MAX, offs * 1e3))
    P("   held, R11 %.1f mOhm:     %.3f / %.3f / %.3f A" % ((R11_HELD * 1e3,) + held))
    P("   proposed, R11 %.1f mOhm: %.3f / %.3f / %.3f A" % ((r11_prop * 1e3,) + prop))
    P("   the printed band alone (VSNS over R11): held %.2f / %.2f / %.2f A; proposed %.2f / %.2f / %.2f A" % (
        vsns[0] / R11_HELD, vsns[1] / R11_HELD, vsns[2] / R11_HELD, vsns[0] / r11_prop, vsns[1] / r11_prop, vsns[2] / r11_prop))
    P("   what passes R11 in service: U3 at its %.3f A maximum plus %.3f A of VBUS20's other loads (U2's BIAS: its %.0f mA" % (u3_max, other_i, iq_vin * 1e3))
    P("     operating current and four FETs' 62 nC maximum gate charge at %.0f kHz; R197; the divider; INFERRED) = %.3f A" % (fsw[2] / 1e3, serv))
    P("   MARGIN, the front end's minimum over what passes in service: held %+.3f A (THE FRONT END LIMITS FIRST); proposed %+.3f A" % (
        held[0] - serv, prop[0] - serv))
    P("   (the energy model's entry E2 carries the printed %.2f A minimum; the stacked %.2f A is still above U3, so no energy result" % (
        vsns[0] / r11_prop, prop[0]))
    P("   moves)")
    # the taps: the band is VSNS over R11 ALONE, true only for a Kelvin connection
    kv = json.load(open(os.path.join(TOP, KELVIN), encoding="utf-8"))
    kin = json.load(open(os.path.join(TOP, INTENT_A), encoding="utf-8"))
    tap = {}
    for ev in kv["evidence"]:
        m = re.match(r"(FE_ISNS_[PN]): the copper between (R11\.[12]) and (U2\.1[34]) carries ([\d.]+) mV", ev)
        if m:
            tap[m.group(1)] = (m.group(2), m.group(3), float(m.group(4)))
    if len(tap) != 2:
        refuse("the Kelvin reading of R11's two taps not parsed")
    b_sha = sha(BOARD_A)[:16]
    fe_amps = (kin["rails"]["FE_OUT"]["amps_typ"], 3.80)
    err_mv = tap["FE_ISNS_P"][2] + tap["FE_ISNS_N"][2]
    r_par_max = (vsns[0] - offs) / serv - r11_prop * 1.01 * (1 + tcr_r * dt_r)
    P("   THE TAPS, a condition of every band above: VSNS over R11 alone holds only for a Kelvin connection. The tree's last reading,")
    P("     %s (%s, ADVISORY, board sha256/16 %s, the routed board in the tree today (%s), laid" % (
        KELVIN, kv["ts"][:10], kv["inputs"]["board"]["sha256_16"], "the same file" if b_sha == kv["inputs"]["board"]["sha256_16"] else "NOT the same file"))
    P("     before the ISNS filter R160, R161 entered the netlist): %s between %s and %s carries %.2f mV, %s between %s and %s %.2f mV" % (
        "FE_ISNS_P", tap["FE_ISNS_P"][0], tap["FE_ISNS_P"][1], tap["FE_ISNS_P"][2], "FE_ISNS_N", tap["FE_ISNS_N"][0], tap["FE_ISNS_N"][1], tap["FE_ISNS_N"][2]))
    P("     of copper drop. Both ADD to the sensed voltage (INFERRED: on FE_OUT R11.1 is the only sink, on VBUS20 R11.2 the only source),")
    P("     so the front end limits lower. At dc_drop's solved current (FE_OUT's declared %.1f A typical today; pcb_sensitive.yaml's" % fe_amps[0])
    P("     text names %.2f A) the two are %.1f to %.1f mOhm together, as large as R11 itself: on that board the held front end would" % (
        fe_amps[1], err_mv / fe_amps[0], err_mv / fe_amps[1]))
    P("     limit at about %.1f to %.1f A typical, the proposed at about %.1f to %.1f A, BOTH under U3 (INFERRED)" % (
        vsns[1] / (R11_HELD + err_mv * 1e-3 / fe_amps[1]), vsns[1] / (R11_HELD + err_mv * 1e-3 / fe_amps[0]),
        vsns[1] / (r11_prop + err_mv * 1e-3 / fe_amps[1]), vsns[1] / (r11_prop + err_mv * 1e-3 / fe_amps[0])))
    P("     The proposed margin tolerates at most %.2f mOhm between R11's pads and its two taps together (%.1f mV at %.3f A, %.1f %% of" % (
        r_par_max * 1e3, r_par_max * serv * 1e3, serv, r_par_max * serv * 1e3 / 50.0 * 100))
    P("     the 50 mV scale): Kelvin taps on R11 (the maker's p.3 pad drawing shows separate sensing traces) are a condition of the change")
    P("   M1 with the held circuit (MODELED, %s case GEN, board A as generated, the reference day at 40/0): %s" % (
        EB_OUT, "; ".join("%s NOT MET, %s / %s Wh unserved (TYP / WAB)" % r_ for r_ in gen_rows)))
    P("   GEN's own setting against the stacked band: U3 at %s A, its maximum %s A, plus %.3f A of the other loads = %.3f A through R11," % (
        gen_u3[1], gen_u3[2], other_i, float(gen_u3[2]) + other_i))
    P("     against the stacked minimum %.3f A: %+.3f A (energy_basis names 50 mA between U3's maximum and" % (
        held[0], held[0] - float(gen_u3[2]) - other_i))
    P("     the printed %s A minimum; with the other loads and the stacked band the held circuit's front end can limit first even at GEN)" % gen_u3[0])
    P("   M1 conditional on the change (MODELED, the same file; every case but GEN presumes it; COMB/EACH as in its 1d):")
    for lab_, rows_ in (("NOM (the declared efficiencies, TI's U3 reading)", nom_rows), ("WE (itself conditional on three undocumented efficiencies)", we_rows)):
        P("     %s:" % lab_)
        for r_ in rows_:
            P("       %s TYP %s (%s); WAB %s (%s)" % (r_[0], r_[1].strip(), r_[2], r_[3].strip(), r_[4]))
    P("     4S9P: NOT MET in every case of that file, with or without the change")
    P("")

    # ---------------------------------------------------------------- 4. the power path
    def k_at(tc):
        pts = sorted(k_rds.items())
        if tc <= pts[0][0]:
            return pts[0][1]
        for (t0, k0), (t1, k1) in zip(pts, pts[1:]):
            if tc <= t1:
                return k0 + (k1 - k0) * (tc - t0) / (t1 - t0)
        t0, k0 = pts[-2]
        t1, k1 = pts[-1]
        return k1 + (k1 - k0) * (tc - t1) / (t1 - t0)

    def fet_tj(p_of_k):
        """TJ on the maker's RthetaJA from the worst inside air, RDS(on) at TJ (Figure 8); None if past 150 C."""
        tj = t_air
        for _ in range(200):
            tn = t_air + p_of_k(k_at(tj)) * rtja
            if tn > 150.0:
                return None, p_of_k(k_at(150.0))
            if abs(tn - tj) < 0.01:
                return tn, p_of_k(k_at(tn))
            tj = tn
        return tj, p_of_k(k_at(tj))

    def stage(i_out, vin, v_out=v_bus_max):
        """The LM5176 stage's currents at an output current and input voltage (INFERRED: textbook buck-boost relations,
        L at -20 %, fSW at its minimum for ripple and its maximum for switching loss)."""
        p_out = i_out * v_out
        i_in = p_out / ETA_FE / vin
        l_min = l_nom * 0.8
        if vin < v_out:        # boost region: Q2 on, Q3 off, Q4 and Q5 switch
            d = 1.0 - vin / v_out
            ripple = vin * d / (l_min * fsw[0])
            i_l = i_in
            mode = "boost"
        else:                  # buck region: Q5 on, Q4 off, Q2 and Q3 switch
            d = v_out / vin
            ripple = (vin - v_out) * d / (l_min * fsw[0])
            i_l = i_out
            mode = "buck"
        i_l_rms = math.sqrt(i_l ** 2 + ripple ** 2 / 12.0)
        return dict(i_out=i_out, vin=vin, p_out=p_out, i_in=i_in, i_l=i_l, ripple=ripple, peak=i_l + ripple / 2, rms=i_l_rms, d=d, mode=mode)

    t_sw = qgd / i_src + qgd / i_snk
    cases = [("held, at its limit's maximum", held[2]), ("proposed, in service (U3 at its maximum)", serv), ("proposed, at its limit's maximum", prop[2])]
    P("4. THE POWER PATH AT EACH CASE'S CURRENT (the front end's output at VBUS20's %.3f V maximum, efficiency %.2f DECLARED;" % (v_bus_max, ETA_FE))
    P("   VIN_RAW at the tracker's %.1f V (the lowest bus a source holds at full power), at %.1f V (REQ-015's service floor and the" % (VIN_TRACKER, VIN_TREE))
    P("   tree's declaration basis for VIN_RAW, board E's _FE_A; above the stage's UVLO, 7.86 to 8.31 V falling by gen_sch_a.py; at")
    P("   these currents only with the tracker in its limit and the vehicle together, see the sources below) and at %.0f V (buck)" % VIN_MAX)
    P("   The worst inside air %.1f C throughout. INFERRED relations; every rating MAKER." % t_air)
    res = {}
    for lab, i_out in cases:
        P("   %s: %.3f A out" % (lab, i_out))
        for vin in (VIN_TRACKER, VIN_TREE, VIN_MAX):
            s = stage(i_out, vin)
            res[(lab, vin)] = s
            # L1
            rise = 40.0 * (s["rms"] / irms40) ** 2
            p_dcr = s["rms"] ** 2 * dcr_max * (1 + 0.0039 * (t_air + rise - 25.0))
            l1_ok = s["peak"] <= isat and s["rms"] <= irms40 and t_air + rise <= 165.0
            P("     VIN %4.1f V (%s, D %.2f): in %.2f A; L1 average %.2f A, ripple %.2f A p-p, peak %.2f A against Isat %.1f A; rms %.2f A" % (
                vin, s["mode"], s["d"], s["i_in"], s["i_l"], s["ripple"], s["peak"], isat, s["rms"]))
            P("       L1: rise about %.0f K (the maker's 40 K at %.1f A scaled by the square, INFERRED; core loss excluded), part %.0f C;" % (
                rise, irms40, t_air + rise))
            bads = [x for x, bad in (("peak over Isat", s["peak"] > isat), ("rms over the 40 K Irms", s["rms"] > irms40),
                                     ("part over 165 C", t_air + rise > 165.0)) if bad]
            P("         DCR loss %.2f W; %s" % (p_dcr, "WITHIN the maker's figures" if l1_ok else "NOT WITHIN: " + ", ".join(bads)))
            if s["mode"] == "boost" and s["peak"] > vcs_boost[0] / R12_CS:
                caps = [(v / R12_CS - s["ripple"] / 2.0) for v in vcs_boost]
                P("         the cycle-by-cycle boost limit (%s A peak over R12, p.7) may end the cycle first: L1's average at most" % " / ".join("%.0f" % (v / R12_CS) for v in vcs_boost))
                P("         %s A, the output %s A (INFERRED); even at its minimum L1's peak passes Isat %.1f A" % (
                    " / ".join("%.1f" % c_ for c_ in caps), " / ".join("%.2f" % (c_ * vin * ETA_FE / v_bus_max) for c_ in caps), isat))
            # FETs
            rds = rds6_max
            if s["mode"] == "boost":
                q = {"Q2 (on)": (lambda k, s=s: s["rms"] ** 2 * rds * k),
                     "Q4 (boost switch)": (lambda k, s=s: s["rms"] ** 2 * s["d"] * rds * k + 0.5 * v_bus_max * s["i_l"] * t_sw * fsw[2]
                                           + 0.5 * qoss * v_bus_max * fsw[2]),
                     "Q5 (rectifier)": (lambda k, s=s: s["rms"] ** 2 * (1 - s["d"]) * rds * k)}
            else:
                q = {"Q2 (buck switch)": (lambda k, s=s: s["rms"] ** 2 * s["d"] * rds * k + 0.5 * s["vin"] * s["i_l"] * t_sw * fsw[2]
                                          + 0.5 * qoss * s["vin"] * fsw[2]),
                     "Q3 (rectifier)": (lambda k, s=s: s["rms"] ** 2 * (1 - s["d"]) * rds * k),
                     "Q5 (on)": (lambda k, s=s: s["rms"] ** 2 * rds * k)}
            parts = []
            for name, f in q.items():
                tj, p150 = fet_tj(f)
                if tj is None:
                    need_rth = (150.0 - t_air) / p150
                    parts.append("%s past 150 C (%.2f W at 150 C; needs RthetaJA <= %.0f C/W)" % (name, p150, need_rth))
                else:
                    parts.append("%s %.2f W, TJ %.0f C" % (name, f(k_at(tj)), tj))
            P("       FETs (RDS(on) max x Figure 8 at TJ, RthetaJA %.0f C/W): %s" % (rtja, "; ".join(parts)))
            # capacitors
            if s["mode"] == "buck":
                ic_in = math.sqrt((i_out ** 2) * s["d"] * (1 - s["d"]) + s["ripple"] ** 2 / 12.0)
                ic_out = s["ripple"] / math.sqrt(12.0)
            else:
                ic_in = s["ripple"] / math.sqrt(12.0)
                ic_out = i_out * math.sqrt(s["d"] / (1 - s["d"]))
            P("       input caps C11, C12: %.2f A rms together (INFERRED), no maker ripple rating held for FS32X106K101EGG: NOT ESTABLISHED;" % ic_in)
            P("       output: %.2f A rms against %d x %.1f A = %.1f A of EEHZK1V331P (C13 to C15 on FE_OUT share it): %s" % (
                ic_out, len(bulk), ripple_bulk, len(bulk) * ripple_bulk, "WITHIN" if ic_out <= len(bulk) * ripple_bulk else "NOT WITHIN"))
            P("       J_VR1 to J_VR4: %.2f A a pin if shared evenly (INFERRED) against %.0f A at a 10 K rise: %s" % (
                s["i_in"] / 4.0, pin_a, "WITHIN" if s["i_in"] / 4.0 <= pin_a else "NOT WITHIN"))
        # R11
        p_r11 = i_out ** 2 * (r11_prop if lab.startswith("proposed") else R11_HELD) * 1.01
        allow = [(tc, p_rated * max(0.0, min(1.0, (t_derate1 - tc) / (t_derate1 - t_derate0)))) for tc in (t_air, R11_TEMP_MAX)]
        P("     R11: %.2f W (I2R at +1 %%) against 3 W derated to %s; the 5 s overload 5 x 3 W is %.0f A: WITHIN" % (
            p_r11, " and ".join("%.2f W at %.0f C" % (w, tc) for tc, w in allow),
            math.sqrt(15.0 / (r11_prop if lab.startswith("proposed") else R11_HELD))))
        # copper
        w = []
        for what, amps in (("FE_OUT and VBUS20", i_out), ("VIN_RAW at %.1f V" % VIN_TRACKER, res[(lab, VIN_TRACKER)]["i_in"]),
                           ("VIN_RAW at %.1f V" % VIN_TREE, res[(lab, VIN_TREE)]["i_in"])):
            w.append("%s %.2f A: %.1f mm at 1 oz, %.1f mm at 2 oz" % (what, amps, TC.width_for_current(amps, 1.0, 10.0), TC.width_for_current(amps, 2.0, 10.0)))
        P("     copper (track_current.width_for_current, decision 35's conservative model, external, 10 K rise): %s" % "; ".join(w))
    P("   the declarations the generators lay copper and rate parts to: VBUS20 %s A typical, %s A peak (gen_sch_a.py);" % vb_decl)
    P("     VIN_RAW %.2f A (gen_sch_a.py _VIN_RAW_A, board E's _FE_A: 5.7 A at 20.7 V over 0.93 from 9.0 V); TRK_OUT %.2f A (gen_sch_e.py)" % (vin_decl, trk_decl))
    lab_h, lab_s, lab_p = (c_[0] for c_ in cases)
    fe_a_prop = vsns[2] / r11_prop * 20.7 / ETA_FE / 9.0
    P("   against them (INFERRED): VBUS20: held maximum %.3f A under both; proposed in service %.3f A %s the %s A typical, proposed" % (
        held[2], serv, "PASSES" if serv > float(vb_decl[0]) else "under", vb_decl[0]))
    P("     maximum %.3f A %s the %s A peak. VIN_RAW %.2f A: held at %.1f V %.2f A (the stacked band over _FE_A's printed 5.7 A and 20.7 V);" % (
        prop[2], "PASSES" if prop[2] > float(vb_decl[1]) else "under", vb_decl[1], vin_decl, VIN_TREE, res[(lab_h, VIN_TREE)]["i_in"]))
    P("     proposed in service at %.1f V %.2f A, at the maximum %.2f A; _FE_A's own formula at the proposed printed maximum %.2f A gives" % (
        VIN_TREE, res[(lab_s, VIN_TREE)]["i_in"], res[(lab_p, VIN_TREE)]["i_in"], vsns[2] / r11_prop))
    P("     %.2f A. TRK_OUT %.2f A: at %.1f V the proposed in service carries %.2f A, the maximum %.2f A" % (
        fe_a_prop, trk_decl, VIN_TRACKER, res[(lab_s, VIN_TRACKER)]["i_in"], res[(lab_p, VIN_TRACKER)]["i_in"]))
    w_h, w_s, w_p = (res[(l_, VIN_TRACKER)]["p_out"] / ETA_FE for l_ in (lab_h, lab_s, lab_p))
    P("   board E's 200 W stage (Option A(i)'s, NOT DESIGNED: a1elec CHARGER.md 2, 'its owner's'): the front end asks %.1f W in service" % w_s)
    P("     (%.3f A at %.3f V over %.2f), WITHIN 200 W; held at its maximum %.1f W; proposed at its maximum %.1f W, OVER 200 W, so where" % (
        serv, v_bus_max, ETA_FE, w_h, w_p))
    P("     U3 does not limit (a fault) the stage or the array bounds the draw, not R11 (INFERRED)")
    P("   the vehicle entry alone: its LM5069 passes at most 6.15 A (gen_sch_e.py _VEH_T), so below %.1f V a vehicle alone cannot carry" % (w_s / 6.15))
    P("     the proposed in-service %.1f W (below %.1f V the held maximum %.1f W either): the front end's draw on the vehicle is bounded by" % (
        w_s, w_h / 6.15, w_h))
    P("     that entry whatever R11 is; the host's IIN_HOST per source is a downstream item (INFERRED)")
    s_t = res[("proposed, at its limit's maximum", VIN_TRACKER)]
    trk_lim = tuple(v / r5 for v in vcs_trk)
    P("   VIN_RAW's sources at the proposed maximum: the front end asks %.1f W; the tracker at %.1f V would carry %.2f A against its" % (
        s_t["p_out"] / ETA_FE, VIN_TRACKER, s_t["i_in"]))
    P("     buck current limit %.1f / %.1f / %.1f A (VCS over R5, INFERRED as the average it can pass) and TRK_OUT's declared %.2f A;" % (trk_lim + (trk_decl,)))
    P("     the vehicle entry passes at most its LM5069's 6.15 A (gen_sch_e.py), under its fuse F1's 8 A at 65 C (gen_sch_e.py, the")
    P("     10 A blade derated by pcb_fuse_derating.yaml), whatever R11 is; board E's panel fuse F2 sees the tracker's input,")
    P("     %.1f W over its efficiency at the array's 34.3 V set point, about %.1f A (0.93 DECLARED): under '%s'" % (
        s_t["p_out"] / ETA_FE, s_t["p_out"] / ETA_FE / 0.93 / 34.29, e_f2.split(" (")[0]))
    P("")

    # ---------------------------------------------------------------- 5. the other settings
    c_slope = 2e-6 * l_nom / (0.005 * 5)
    P("5. THE LM5176'S OTHER SETTINGS AND R11 (the maker's equations)")
    P("   average current limit: ICL(AVG) = 50 mV / RSNS (Eq. 4, p.17): the ONE setting R11 sets; bands in section 3")
    P("   the CC loop: its gm amplifier (%.0f mS, p.7) discharges SS (C7 %s) when VSNS passes 50 mV (7.3.6, p.17): the loop's gain" % (
        gm_ss * 1e3, ca["C7"]["value"]))
    P("     per ampere scales with R11, so the proposed loop acts at %.2f of the held loop's gain (INFERRED); its response is a bench item" % (r11_prop / R11_HELD))
    P("   the ISNS filter: 100 Ohm is the maker's ceiling (p.24) and R160, R161 are at it; unchanged. The bias offset is %.1f mV either" % (offs * 1e3))
    P("     way, %.0f mA at the proposed R11 against %.0f mA at the held (in section 3's band)" % (offs / r11_prop * 1e3, offs / R11_HELD * 1e3))
    P("   the current-sense amplifier's range: ISNS common mode 0 to 55 V (p.5) against VBUS20 at most 23.40 V (s120's bound): unchanged;")
    P("     ISNS(+) to ISNS(-) is rated +-0.3 V (p.5): at the proposed R11 that is %.0f A, far past any current the path can carry" % (0.3 / r11_prop))
    P("   slope compensation: Eq. 26 (p.24) uses RSENSE, the CS resistor R12, and L1, not R11: CSLOPE = gmSLOPE x L1 / (RSENSE x ACS)")
    P("     = %.0f pF with 2 uS, %.0f uH, 5 mOhm and 5 (the p.24 example's gm and gain), against C147 %s: unchanged by R11. If L1 runs" % (
        c_slope * 1e12, l_nom * 1e6, ca["C147"]["value"]))
    P("     near its Isat (section 4) its inductance falls and the dead-beat value falls with it (INFERRED)")
    P("   the cycle-by-cycle limits: boost peak %.0f / %.0f / %.0f A and buck valley %.1f / %.1f / %.1f A (VCS over R12 5 mOhm, p.7):" % (
        vcs_boost[0] / 0.005, vcs_boost[1] / 0.005, vcs_boost[2] / 0.005, vcs_buck[0] / 0.005, vcs_buck[1] / 0.005, vcs_buck[2] / 0.005))
    P("     unchanged; with the average limit raised they, not the average loop, bound L1 at a low VIN_RAW in an overload")
    P("   hiccup: MODE to VCC selects no hiccup (p.20), so a sustained overload stays in the average or the cycle-by-cycle limit")
    P("     indefinitely: at the proposed R11 it does so at the higher currents of section 4 (the held circuit sat there in service)")
    P("")
    P("END. Desk figures on the makers' pages and the committed netlists; nothing is measured, nothing implemented.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
