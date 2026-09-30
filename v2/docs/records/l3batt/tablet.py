#!/usr/bin/env python3
"""tablet.py: a proposed USB-C service budget for the lid tablet, and Options A and B carried with it (stream l3batt,
MESHSAT-1357, 30 September 2026; the owner's words that day: "The USB-C outlet's 45 W rating is peak capability, not
continuous mission consumption. Check what the existing 42.8 W budget includes and prevent double-counting. Calculate
tablet support using: operating/charging energy delivered per day, in Wh; peak output power; converter losses; charging
schedule and starting charge assumptions. [...] Label that budget as a proposal, not verified tablet endurance. Do not
assume maximum charging power throughout the mission, or remove charging to obtain a pass.").

PROTOTYPE DESIGN, desk arithmetic: nothing is built, bought, powered or measured.
- The budget is a PROPOSAL, measurable at the outlet. It is not verified tablet endurance, and no tablet model is picked.
- The class figures come from two makers' rugged-tablet spec sheets, held back by their copyright notices and pinned by
  sha256 (fetch_held_back.py).
- The converter figures come from TI's LM5176 (Figure 6-2, read by pixel with l3plane's curve_readings.py, pinned),
  TPS25740 and CSD18510Q5B sheets and board A's committed netlist.
- The energy results are MODELED through energy_basis.py's set-up (pinned), as runtime.py runs it, with the kit's load
  set hour by hour so the outlet draws only in its window.

Run from the repository root:  python3 v2/docs/records/l3batt/tablet.py > v2/docs/records/l3batt/tablet.out
Deterministic. Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction failed."""
import hashlib
import math
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
L3 = os.path.join(TOP, "v2", "docs", "records", "l3plane")
PINS = {"energy_basis.py": "7e2f19bff6b63ba5bfdb7ce430dc32e143613f2339cd1bc88e15f71dd022fb47",
        "curve_readings.py": "dacb57cebd73d16f16f2247720de683082fb035fea170c425686c170b2afffa2"}
for _f, _want in PINS.items():
    if hashlib.sha256(open(os.path.join(L3, _f), "rb").read()).hexdigest() != _want:
        sys.stderr.write("tablet: %s is not the pinned file; refusing\n" % _f)
        sys.exit(2)
sys.path.insert(0, L3)
import energy_basis as EB  # noqa: E402
import curve_readings as CR  # noqa: E402
import netlist_sexp as N  # noqa: E402  (v2/ecad/tools, put on the path by curve_readings)
TP, ER = EB.TP, EB.ER

LOAD_OUT = "v2/docs/records/l3batt/load_trace.out"
RUN_OUT = "v2/docs/records/l3batt/runtime.out"
R11_OUT = "v2/docs/records/r11dep/r11_dep.out"
PWR_OUT = "v2/docs/records/rv-pwr/pwr_budget.out"
PWR_PY = "v2/docs/records/rv-pwr/pwr_budget.py"
NET_A = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"
LM5176 = "v2/vendor/ti/lm5176-datasheet.pdf"
TPS = "v2/vendor/ti/ti-tps25740.pdf"
CSD = "v2/vendor/battery/ti-csd18510q5b.pdf"
ZEB = ("v2/vendor/tablet/held/zebra-et40-et45-spec-sheet-en-us.pdf", "59f0c2807fb5b24d43d418e45f684c0394123cf0cda921a61f030a78c5056d73")
SAM = ("v2/vendor/tablet/held/samsung-galaxy-tab-active5-spec-sheet.pdf", "f5a40178566ca410f5a91423730697deeb598edc949ed50f9df5ae054b800fa5")
T_COLD = -10.0
LID_A = 9
VBAT = 14.4             # the 4S node's nominal (INFERRED: 4 x 3.6 V), the outlet converter's input and bias supply
NH_WH = 67.2            # runtime.out 1: one NH2054HD34 smart pack, usable aged at +20 C (INFERRED there)
NH_KG = 0.435           # runtime.py: the NH2054HD34's mass (maker, 3.6.1)

# THE PROPOSED BUDGET: every parameter is the session's (a PROPOSAL), each measurable at the outlet
P_CAP = 18.0            # W: the most the outlet offers (TPS25740A Table 5: PSEL direct to GND, PCTRL low), not the 45 W as drawn
WIN_H = 2               # h: the daily window the outlet converter is enabled in; E_OUT = P_CAP x WIN_H, a ceiling without a meter
WINDOWS = {"W13": (13, 15), "W10": (10, 12), "W19": (19, 21), "ANY": None}   # UTC; ANY = the converter on all day, spread evenly
NAMES = {None: "no tablet budget", "W13": "budget, window 13 to 15 UTC", "W10": "budget, window 10 to 12 UTC",
         "W19": "budget, window 19 to 21 UTC (after dark)", "ANY": "budget, any time (converter on 24 h)"}


def refuse(code, msg):
    sys.stderr.write("tablet: %s; refusing\n" % msg)
    sys.exit(code)


def need(text, pat, what):
    m = re.search(pat, text, re.M)
    if not m:
        refuse(3, "%s not parsed" % what)
    return m


def pdf(rel, pages=None):
    args = ["pdftotext", "-layout"] + (["-f", str(pages[0]), "-l", str(pages[1])] if pages else []) + [os.path.join(TOP, rel), "-"]
    return subprocess.run(args, capture_output=True, text=True).stdout


def sha16(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()[:16]


def main():
    for rel, want in (ZEB, SAM):
        p = os.path.join(TOP, rel)
        if not os.path.exists(p) or hashlib.sha256(open(p, "rb").read()).hexdigest() != want:
            refuse(2, "%s is not the pinned file (held back: run fetch_held_back.py)" % rel)
    o = []
    P = o.append
    P("THE LID TABLET'S USB-C SERVICE BUDGET (a PROPOSAL) AND OPTIONS A AND B WITH IT (tablet.py, stream l3batt, MESHSAT-1357).")
    P("PROTOTYPE DESIGN: nothing built, bought, powered or measured. The budget is a proposal measurable at the outlet, not")
    P("verified tablet endurance; no tablet model is picked. Basis per figure: MAKER (sheet, page), NETLIST, MODELED, INFERRED")
    P("(method stated), ASSUMPTION (a figure no document gives), PROPOSAL (the session's setting). The author's analysis, AI")
    P("arithmetic; not a qualified review and not the independent check.")
    P("")

    # 1. double counting
    lt = EB.head_equal(LOAD_OUT)
    pwr = EB.head_equal(PWR_OUT)
    no_tab = "The tablet: no row." in lt
    outlet_off = "The outlets are off in every state" in lt
    pdo = need(EB.head_equal(PWR_PY),
               r'"PDO": \("fixed", "VBAT", ([\d.]+), ([\d.]+), "([^"]+)"\)', "pwr_budget.py PDO node")
    spec = pwr.split("== shares PS-IDLE-SPEC\n", 1)[1].split("\n==", 1)[0]
    nshare = len([ln for ln in spec.splitlines() if " load " in ln])
    pd_rows = [ln.strip() for ln in spec.splitlines() if re.search(r"USB-C|outlet|PDO|tablet", ln, re.I)]
    P("1. DOUBLE COUNTING: what PS-IDLE-SPEC's 42.8 W holds of the tablet and the outlet")
    P("   pwr_budget.out's %d PS-IDLE-SPEC shares name no tablet, USB-C, outlet or PDO row (%s); load_trace.out: the tablet has" % (
        nshare, "none found" if not pd_rows else "; ".join(pd_rows)))
    P("   no row (%s) and the outlets are off in every state (%s); pwr_budget.py carries the outlet stage as node PDO (%s V, its" % (
        "yes" if no_tab else "NO", "yes" if outlet_off else "NO", pdo.group(1)))
    P("   efficiency %s DECLARED: '%s') for the section 7.1 variants only." % (pdo.group(2), pdo.group(3)))
    P("   So the 42.8 W carries no tablet energy, no outlet conversion loss and no idle draw of the outlet converter: every")
    P("   figure below is ADDED to it, and nothing in it is counted twice")
    if not (no_tab and outlet_off) or pd_rows:
        sys.stdout.write("\n".join(o) + "\n")
        refuse(4, "the 42.8 W may hold an outlet or tablet row")
    na = N.load(os.path.join(TOP, NET_A))
    ca, pa = na["components"], na["pins"]
    if not (pa["U19"]["2"]["net"] == "VBAT" and pa["U19"]["24"]["net"] == "VBAT" and "LM5176" in ca["U19"]["value"]
            and "TPS25740" in ca["U18"]["value"] and pa["U18"]["17"]["net"] == "+5V_DEV"):
        refuse(3, "board A's outlet stage is not as read")
    rt = [ref for ref, _pin, _f, _t in na["nets"]["PD_RT"] if ref.startswith("R")]
    fsw = float(need(ca[rt[0]]["value"], r"\((\d+) kHz\)", "the outlet stage's RT").group(1)) * 1e3
    mode = [ref for ref, _pin, _f, _t in na["nets"]["PD_MODE"] if ref.startswith("R")]
    fets = [q for q in ("Q21", "Q22", "Q25", "Q26") if "CSD18510Q5B" in ca[q]["value"]]
    if len(fets) != 4 or not any("(MODE: CCM)" in ca[r]["value"] for r in mode):
        refuse(3, "the outlet stage's FETs or MODE are not as read")
    t6 = pdf(LM5176, (6, 6))
    iq_t, iq_m = (float(x) * 1e-3 for x in need(t6, r"VIN operating current\s+VEN/UVLO = 2 V, VFB = 0\.9 V\s+([\d.]+)\s+([\d.]+)\s+mA",
                                                "LM5176 p.6 VIN operating current").groups())
    vcc = float(need(t6, r"Regulation voltage\s+VBIAS = 0 V, VCC open\s+[\d.]+\s+([\d.]+)", "LM5176 p.6 VCC").group(1))
    c3 = pdf(CSD, (3, 3))
    q45t, q45m = (float(x) * 1e-9 for x in need(c3, r"Gate charge total \(4\.5 V\)\s+([\d.]+)\s+([\d.]+)\s+nC", "CSD18510Q5B Qg 4.5 V").groups())
    q10t, q10m = (float(x) * 1e-9 for x in need(c3, r"Gate charge total \(10 V\)\s+([\d.]+)\s+([\d.]+)\s+nC", "CSD18510Q5B Qg 10 V").groups())
    qg_t = q45t + (q10t - q45t) * (vcc - 4.5) / 5.5
    qg_m = q45m + (q10m - q45m) * (vcc - 4.5) / 5.5
    tps = " ".join(pdf(TPS).split())
    tps8 = " ".join(pdf(TPS, (8, 8)).split())
    it_t, it_m = (float(x) * 1e-3 for x in need(tps8, r"Operating current while sink attached ([\d.]+) [\d.]+ ([\d.]+) mA",
                                                "TPS25740 operating current").groups())
    idle = {}
    for tag, qg, iq, it in (("typ", qg_t, iq_t, it_t), ("max", qg_m, iq_m, it_m)):
        idle[tag] = {"g4": 4 * qg * fsw * VBAT, "g2": 2 * qg * fsw * VBAT, "iq": iq * VBAT, "tps": it * 5.0 / 0.90}
    p_idle = idle["max"]["g4"] + idle["max"]["iq"] + idle["max"]["tps"]
    p_idle_t = idle["typ"]["g4"] + idle["typ"]["iq"] + idle["typ"]["tps"]
    P("   THE OUTLET CONVERTER'S OWN DRAW WHEN ENABLED, NOT IN THE 42.8 W (board A: U19 LM5176 with VIN and BIAS on VBAT, MODE")
    P("   strapped to forced CCM by %s, RT %s = %.0f kHz, four CSD18510Q5B, L11 %s; U18 TPS25740A with VDD on +5V_DEV; NETLIST" % (
        mode[0], rt[0], fsw / 1e3, ca["L11"]["value"]))
    P("   %s sha256/16 %s):" % (NET_A, sha16(NET_A)))
    P("     the LM5176's VIN operating current (not switching, VFB = 0.9 V) %.0f / %.0f mA typ / max (MAKER %s p.6): %.3f / %.3f W" % (
        iq_t * 1e3, iq_m * 1e3, LM5176, idle["typ"]["iq"], idle["max"]["iq"]))
    P("     the gate drive, Qg x fsw x VBAT a FET (VCC is regulated from BIAS = VBAT, so the gate charge is drawn at VBAT): Qg at")
    P("     VCC's %.2f V (MAKER p.6) interpolated between the sheet's %.0f / %.0f nC at 4.5 V and %.0f / %.0f nC at 10 V typ / max (MAKER" % (
        vcc, q45t * 1e9, q45m * 1e9, q10t * 1e9, q10m * 1e9))
    P("     %s p.3): %.0f / %.0f nC; all four switching (buck-boost, the 15 V contract from a 12 to 16.8 V node) %.3f / %.3f W;" % (
        CSD, qg_t * 1e9, qg_m * 1e9, idle["typ"]["g4"], idle["max"]["g4"]))
    P("     two switching (buck, the 5 and 9 V contracts) %.3f / %.3f W (INFERRED)" % (idle["typ"]["g2"], idle["max"]["g2"]))
    P("     the TPS25740A's operating current while a sink is attached %.0f / %.0f mA typ / max (MAKER %s p.8, I(SUPP)) at 5 V over" % (
        it_t * 1e3, it_m * 1e3, TPS))
    P("     +5V_DEV's converter at 0.90 (INFERRED): %.3f / %.3f W" % (idle["typ"]["tps"], idle["max"]["tps"]))
    P("     IDLE DRAW, ENABLED AND NOT LOADED: %.2f W typ, %.2f W max (INFERRED from the sheets' terms). Forced CCM keeps switching" % (
        p_idle_t, p_idle))
    P("     at no load; the inductor's ripple and core losses and the FETs' switching of the ripple are not in the sheets held, so")
    P("     the true idle draw is higher by an amount not quantified here. The budget below takes %.2f W" % p_idle)
    P("")

    # 2. the class and the budget
    zt = " ".join(pdf(ZEB[0]).split())
    z8 = float(need(zt, r"8 in\.: 6100 mAh 3\.87 V rechargeable.*?\(([\d.]+) Wh\)", "Zebra 8 in. Wh").group(1))
    z10 = float(need(zt, r"10 in\.: 7600 mAh 3\.87 .*?\(([\d.]+) Wh\)", "Zebra 10 in. Wh").group(1))
    st = " ".join(pdf(SAM[0]).split())
    s_typ = need(st, r"Li-Po ([\d,]+) ?mAh", "Samsung capacity").group(1)
    s_min = need(st, r"[Rr]ated \(minimum\) capacity is ([\d,]+) ?mAh", "Samsung rated capacity").group(1)
    e_out = P_CAP * WIN_H
    p_win = P_CAP
    # the outlet's straps as drawn (NETLIST) against the TPS25740A's tables (MAKER, SLVSDG8B pp.28 to 29)
    strap = {nm: pa["U18"][pn]["net"] for nm, pn in (("HIPWR", "5"), ("EN9V", "8"), ("PSEL", "12"), ("PCTRL", "14"))}
    if strap != {"HIPWR": "PD_DVDD", "EN9V": "GND", "PSEL": "PD_DVDD", "PCTRL": "PD_VAUX"}:
        refuse(3, "U18's straps are not as read: %s" % strap)
    t5 = need(tps, r"Table 5\. Maximum Current Advertised in the Power Data Object for a Given Voltage \(TPS25740A\) (.*?) Copyright", "TPS25740A Table 5").group(1)
    rows5 = re.findall(r"(Direct to GND|DVDD via R\(SEL\)|GND via ?R\(SEL\)|Direct to DVDD)(?: Max = 3 A| R\(SEL\) or Direct to| DVDD through| Direct to DVDD)?"
                       r" (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)", t5)
    if len(rows5) != 12:
        refuse(3, "TPS25740A Table 5's twelve 3 A rows not parsed")
    gnd = [(float(a), float(b)) for nm, a, b in rows5[:12] if nm == "Direct to GND"]      # 5, 9, 15 V; (PCTRL low, high)
    dvdd = [(float(a), float(b)) for nm, a, b in rows5[:12] if nm == "Direct to DVDD"]
    if len(gnd) != 3 or len(dvdd) != 3:
        refuse(3, "TPS25740A Table 5's PSEL rows not parsed")
    p_as = max(v * i[1] for v, i in zip((5, 9, 15), dvdd))
    p_lo = max(v * i[0] for v, i in zip((5, 9, 15), gnd))
    if abs(p_lo - P_CAP) > 0.01:
        refuse(3, "the cap is not the table's PSEL-to-GND, PCTRL-low power (%.1f W)" % p_lo)
    en = {pin: pa["U26"][pin]["net"] for pin in ("11", "12", "13")}
    exp = [r for r, pn, _f, _t in na["nets"][en["12"]] if r.startswith("U") and r != "U26"]
    mons = [r for r in ca if "INA226" in ca[r]["value"]]
    mon_out = [r for r in mons if {v["net"] for v in pa[r].values()} & {"PD_VBUS", "PD_OUT", "PD_VPWR", "PD_SW"}]
    P("2. THE PROPOSED USB-C SERVICE BUDGET (a PROPOSAL, measurable at the outlet; not a tablet's verified endurance)")
    P("   the class, 8 to 10 inch rugged tablets (REQ-011), from makers' spec sheets held back and cited in v2/vendor/sources.txt:")
    P("     Zebra ET40/ET45 (sha256/16 %s, p.3): 8 in. 6100 mAh 3.87 V, %.2f Wh; 10 in. 7600 mAh 3.87 V, %.2f Wh (MAKER)" % (ZEB[1][:16], z8, z10))
    P("     Samsung Galaxy Tab Active5, 8 in. (sha256/16 %s, p.2): %s mAh typical, rated (minimum) %s mAh; no voltage or Wh" % (
        SAM[1][:16], s_typ, s_min))
    P("     printed (MAKER). At a 3.8 to 3.9 V cell nominal it is about %.0f Wh (INFERRED, not a maker figure)" % (
        float(s_typ.replace(",", "")) * 3.85 / 1000.0))
    P("   THE OUTLET AS DRAWN (NETLIST, U18 TPS25740A): HIPWR and PSEL straight to DVDD, EN9V to GND, PCTRL to VAUX, so by the")
    P("     maker's Tables 2, 3 and 5 (%s pp.28 to 29) it advertises 5, 9 and 15 V at 3 A, %.0f W peak," % (TPS, p_as))
    P("     with no way to lower it in the field. Its enable PD_EN is U26's AND of %s (an output of %s, the %s)" % (
        en["12"], exp[0], ca[exp[0]]["value"].split(":")[0]))
    P("     and %s, so the converter can be switched by software on existing hardware. No INA226 monitors the outlet (%d on" % (
        en["13"], len(mons)))
    P("     board A, on %s): the kit cannot meter the energy it delivers there%s" % (
        ", ".join(sorted({v["net"] for r in mons for v in pa[r].values() if v["net"].startswith(("+5V", "+13", "+54"))})),
        "" if not mon_out else " (FOUND: %s)" % mon_out))
    P("   P_CAP, PEAK OUTPUT POWER: %.0f W at the outlet. It is the maker's own setting for PSEL direct to GND with PCTRL low" % P_CAP)
    P("     (Table 5, TPS25740A, HIPWR high: 5 V %.1f A, 9 V %.1f A, 15 V %.1f A). It needs a STRAP CHANGE on board A, an" % tuple(i[0] for i in gnd))
    P("     electrical correction neither designed nor checked: PSEL from DVDD to GND, and PCTRL from VAUX to GND (or to a spare")
    P("     expander line, which gives %.0f W with PCTRL high, for shore power). With it the board, not the tablet, holds the" % max(
        v * i[1] for v, i in zip((5, 9, 15), gnd)))
    P("     cap. The 45 W of the drawn straps is a peak capability the budget never assumes")
    P("   SCHEDULE: the outlet converter enabled only in one %d h window a day by the expander line; the case is W13 (13 to" % WIN_H)
    P("     15 UTC). W10 (10 to 12 UTC), W19 (19 to 21 UTC, after dark) and ANY (the converter on all day) are compared in")
    P("     section 5")
    P("   E_OUT, ENERGY DELIVERED AT THE OUTLET: at most %.0f Wh a day = the cap x the window, a ceiling the strapped board and" % e_out)
    P("     the schedule enforce without a meter. It covers one full recharge a day of the class's largest battery (%.2f Wh) with" % z10)
    P("     up to %.0f %% lost in the tablet's own charger (no sheet held gives that loss). The model charges the ceiling every day," % (
        100.0 * (e_out / z10 - 1.0)))
    P("     at the cap for the whole window: the kit side at its bound, not a guessed tablet draw. Whether a given tablet takes a")
    P("     full recharge in %d h at %.0f W is for the named model's verification (REQ-011's open acceptance, SC-45)" % (WIN_H, P_CAP))
    P("   STARTING CHARGE: the tablet full at the mission's start; every day's window, the first included, delivers the day's")
    P("     full budget, so the kit's energy does not depend on the tablet's starting charge (it decides only the tablet's use")
    P("     before the first window)")
    P("")

    # 3. converter losses at the operating point
    im = CR.render(LM5176, 9)
    rows, cols = CR.frame(im, (1400, 2260), (480, 1110), 600, 450)
    top = [r for r in rows if 500 < r < 530]
    bot = [r for r in rows if 1050 < r < 1090]
    left = [c for c in cols if 1420 < c < 1450]
    right = [c for c in cols if 2210 < c < 2240]
    if not (top and bot and left and right):
        refuse(3, "SNVSAI1D p.9 Figure 6-2's frame not found")
    box = (left[0], top[0], right[0], bot[0])

    def red(p):
        return p[0] > 180 and p[1] < 90 and p[2] < 90

    def grey(p):
        return 165 <= p[0] <= 200 and abs(p[0] - p[1]) < 8 and abs(p[1] - p[2]) < 8
    i_op = round(p_win / 12.0, 2)
    xs = (0.5, 1.0, i_op)
    r12 = CR.read(im, box, (0.0, 6.0), (80.0, 100.0), xs, red)
    g24 = CR.read(im, box, (0.0, 6.0), (80.0, 100.0), xs, grey)
    if any(v is None for _x, v in r12 + g24) or not all(80.0 < v < 100.0 for _x, v in r12 + g24):
        refuse(3, "Figure 6-2's VIN 12 V or 24 V curve not read")
    eta_curve = min(v for x, v in r12 + g24 if x == i_op) / 100.0
    eta_decl = float(pdo.group(2))
    eta = min(eta_curve, eta_decl)
    P("3. THE CONVERTER'S LOSS AT THE BUDGET'S OPERATING POINT (INFERRED: a pixel reading of TI's TYPICAL curve)")
    P("   LM5176 %s sha256/16 %s, p.9 Figure 6-2 'Efficiency vs Load': VOUT 12 V, fsw 300 kHz, L1 4.7 uH, the maker's circuit;" % (
        LM5176, sha16(LM5176)))
    P("   read with curve_readings.py's frame and reader (pinned). The VIN 12 V curve (a ratio of 1, as the 15 V contract from")
    P("   the 14.4 V node): %s" % "; ".join("%.2f A %.1f %%" % (x, v) for x, v in r12))
    P("   the VIN 24 V curve (a buck at 0.5, near the 9 V contract's 0.63): %s" % "; ".join("%.2f A %.1f %%" % (x, v) for x, v in g24))
    P("   at the operating point, the cap's %.1f W, %.2f A at the plot's 12 V: the lower curve reads %.3f; the record's declared %.2f" % (p_win, i_op, eta_curve, eta_decl))
    P("   (pwr_budget.py PDO) is the bracket; the budget takes the lower, %.3f. Board A differs from the maker's circuit: 206 kHz," % eta)
    P("   6.8 uH, CSD18510Q5B, 5 to 15 V out; the plot's curves are typical at 25 C")
    e_win = e_out / eta
    e_any = e_out / eta + p_idle * 24.0
    days = {"W13": e_win, "W10": e_win, "W19": e_win, "ANY": e_any}
    P("   ENERGY AT VBAT A DAY for %.0f Wh at the outlet:" % e_out)
    P("     in a %d h window: %.0f / %.3f = %.1f Wh (%.1f W for %d h); the idle draw is inside the curve's loss while it delivers" % (
        WIN_H, e_out, eta, e_win, e_win / WIN_H, WIN_H))
    P("     ANY, the same Wh with the converter on all day: %.0f / %.3f + %.2f W x 24 h = %.1f Wh (INFERRED, indicative: at about %.1f W" % (
        e_out, eta, p_idle, e_any, e_out / 24.0))
    P("     out on average the converter runs far below the plot's lightest point, 0.2 A, so its loss is taken as the curve's plus")
    P("     the idle draw; the kit cannot hold a daily energy limit in this schedule without a meter on the outlet)")
    P("   PEAK AT VBAT with the cap: %.0f W / %.3f = %.1f W, on top of the kit's load for the minutes the tablet draws its peak" % (P_CAP, eta, P_CAP / eta))
    P("")

    # 4. the model with the budget, hour by hour
    D0, PACK0, RES0, t2m = TP.load_model()
    EB.D0, EB.PACK0, EB.RES0 = D0, PACK0, RES0
    EB.TMIN = round(min(t2m), 2)
    notes = " ".join(EB.head_equal(EB.PANEL).split())
    m = need(notes, r"0\.01 h step lowers the lowest stores by about ([\d.]+) to ([\d.]+) Wh \(B\) and ([\d.]+) to ([\d.]+) Wh \(C\)", "NOTES step")
    md = need(notes, r"standby drain \(about ([\d.]+) to ([\d.]+) Wh over 72 h\)", "NOTES drain")
    EB.FLOOR = max(float(m.group(2)), float(m.group(4)))
    drain_w = float(md.group(2)) / D0["mission"]["hours"]
    vr = EB.VR.compute()
    AC, _e, _t = ER.pinned_import()
    AC.check_pins()
    pr0 = RES0["pr"]
    v_min, v_nom = vr["bands"][0][4], vr["nominal"]
    rd = EB.bracket(TP.PAR["r_lid_dsg"][1], "r_lid_dsg")
    rc_ = EB.bracket(TP.PAR["r_lid_chg"][1], "r_lid_chg")
    vak = tuple(float(x) / 1000.0 for x in need(TP.PAR["v_ak"][1], r"([\d]+) / ([\d]+) / ([\d]+) mV", "v_ak").groups())
    ch = D0["solar"]["chain"]
    ce = D0["pack"]["charge"]["energy_efficiency"]
    r11 = EB.head_equal(R11_OUT)
    held = float(need(r11, r"held, R11 10\.0 mOhm:\s+([\d.]+) /", "r11_dep.out held band").group(1))
    other = float(need(r11, r"plus ([\d.]+) A of VBUS20's other loads", "r11_dep.out other loads").group(1))
    hf_rx = float(need(pwr.split("== shares PS-TYP", 1)[1], r"^\s+QMX HF\s+load\s+[\d.]+\s+battery\s+([\d.]+)\s+S", "QMX receiving").group(1))
    u3_e1, u3_e2 = TP.v("u3_iin_e1_a"), TP.v("u3_iin_draft_a")

    def we(v, i, extra=None):
        x = {"eta_u3": EB.u3_day(v, i, "lower"), "eta_b": TP.v("eta_u3b_lo"), "v_ak": vak[2], "r_dsg": rd[1], "r_chg": rc_[1],
             "drain_w": drain_w}
        x.update(extra or {})
        return x
    lo3 = {"eta_st": ch[0]["low"], "eta_fe": ch[1]["low"], "chg_eta": ce["low"]}
    cases = {
        "DRAWN": (v_nom, u3_e1, {"eta_u3": EB.u3_day(v_nom, u3_e1, "TI"), "fe_i": held - other}),
        "NOM": (v_nom, u3_e2, {"eta_u3": EB.u3_day(v_nom, u3_e2, "TI")}),
        "NOM90": (v_nom, u3_e2, dict({"eta_u3": EB.u3_day(v_nom, u3_e2, "TI")}, **lo3)),
        "WE": (v_min, 6.1, we(v_min, 6.1)),
        "WE90": (v_min, 6.1, we(v_min, 6.1, lo3)),
    }
    G40, TA40, _ = ER.september(ER.plane_file(40, 0))
    R40 = ER.Ratios(AC, G40, TA40)
    rat40 = {"TYP": R40.typical(), "WAB": R40.adverse()[0]}
    prof0 = RES0["months"][TP.MONTH]["profile"]

    def extra_at(sched, hh):
        if sched is None:
            return 0.0
        win = WINDOWS[sched]
        if win is None:
            return days["ANY"] / 24.0
        return days[sched] / float(win[1] - win[0]) if win[0] <= hh < win[1] else 0.0

    class Hourly(EB.Series):
        """EB.Series that also sets the kit's load for the hour it hands out: sim() asks prof[hh] before it reads LOAD."""

        def __init__(self, vals, base, sched):
            super().__init__(vals)
            self.base, self.sched = base, sched

        def __getitem__(self, hh):
            TP.LOAD = self.base + extra_at(self.sched, hh)
            return super().__getitem__(hh)

    def sim1(key, n, b, start, hours, hf, sched, trace=None):
        vb, iin, ov = cases[key]
        d, pack, r, cfg = EB.setup(n, pr0 * rat40[b], vb, iin, ov)
        d = dict(d)
        d["mission"] = dict(d["mission"], hours=hours)
        load0 = TP.LOAD
        base = load0 + ov.get("drain_w", 0.0) + (hf_rx if hf else 0.0)
        TP.LOAD = base + sum(extra_at(sched, h) for h in range(24)) / 24.0      # the packs' shares and usable energy at the day's mean
        try:
            return TP.sim(d, pack, r, Hourly([prof0[(start + h) % 24] for h in range(hours)], base, sched), 400.0, 200.0, start,
                          TP.v("t_base_c"), EB.TMIN, cfg, trace)
        finally:
            TP.LOAD = load0

    def meanday(key, n, b, hours, hf, sched):
        rs = [sim1(key, n, b, s, hours, hf, sched) for s in (6, 18)]
        return {"ok": all(r_["ok"] for r_ in rs), "both": min(r_["low_t"] for r_ in rs), "short": max(r_["short"] for r_ in rs),
                "el": rs[0]["el_full"], "stops": [r_["first_stop"] for r_ in rs]}

    def least(key, b, hours, hf, sched):
        def ok(x):
            s = meanday(key, x, b, hours, hf, sched)
            return s["ok"] and s["both"] > EB.FLOOR
        lo, hi = 1.0, 40.0
        if not ok(hi):
            return None, None
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            if ok(mid):
                hi = mid
            else:
                lo = mid
        return hi, meanday(key, hi, b, hours, hf, sched)["el"] - meanday(key, LID_A, b, hours, hf, sched)["el"]

    def cell(s):
        if s["ok"]:
            return "met, lowest %.1f Wh" % s["both"]
        return "stops h %s, %.1f Wh unserved" % ("/".join("-" if x is None else str(x) for x in s["stops"]), s["short"])

    # reproduction: no budget, HF available, reproduces runtime.out section 2's 72 h NOM and WE rows
    rt_out = EB.head_equal(RUN_OUT)
    bad = 0
    for key in ("NOM", "WE"):
        allm = re.findall(r"^\s+%s\s+TYP NOT MET, stops at h [\d/]+, ([\d.]+) unserved\s+WAB NOT MET, stops at h [\d/]+, ([\d.]+) unserved"
                          % key, rt_out, re.M)
        if len(allm) != 2:
            refuse(3, "runtime.out section 2's %s rows not parsed" % key)
        got = tuple("%.1f" % meanday(key, LID_A, b, 72, False, None)["short"] for b in ("TYP", "WAB"))
        if got != allm[1]:
            bad += 1
    P("4. THE BUDGET IN THE MODEL (runtime.py's set-up; the kit's load set hour by hour, the outlet drawing only in its window).")
    P("   Reproduction: with no budget, the 72 h NOM and WE rows of runtime.out section 2 read the same: %s" % ("yes" if bad == 0 else "NO (%d)" % bad))
    if bad:
        sys.stdout.write("\n".join(o) + "\n")
        refuse(4, "the reproduction failed")
    P("   SOLAR ASSISTED, the present store (base 4S6P + lid 4S9P of 35E, 502.6 Wh at the start, runtime.out 2), SC-37's mean")
    P("   September day at 40/0, TYP (WAB a sensitivity), the budget in window W13. Each cell: met with the lowest store, or")
    P("   where the kit stops (hours from the 06 / 18 UTC starts) and the energy unserved. DRAWN = the circuit as drawn (an upper")
    P("   bound); NOM, WE = the corrected path, HYPOTHETICAL and CONDITIONAL on three undocumented efficiencies; NOM90, WE90 =")
    P("   the same at their 0.90 bracket")
    res4 = {}
    for hf in (False, True):
        for hours in (48, 72):
            for b in ("TYP", "WAB"):
                cells = []
                for key in ("DRAWN", "NOM", "NOM90", "WE", "WE90"):
                    s = meanday(key, LID_A, b, hours, hf, "W13")
                    res4[(hf, hours, b, key)] = s
                    cells.append("%s %s" % (key, cell(s)))
                P("     HF %-9s %d h %s: %s" % ("listening" if hf else "available", hours, b, "; ".join(cells)))
    P("")

    # 5. the schedule
    P("5. HOW THE SCHEDULE MATTERS: the least store carrying the mean day (the lid's parallel count, continuous, the base held at")
    P("   4S6P) and the usable Wh it adds to the both-kept 4S9P lid at its %.2f C, corrected path NOM, TYP, HF available" % EB.TMIN)
    res5 = {}
    for hours in (48, 72):
        for sched in (None, "W13", "W10", "W19", "ANY"):
            x, wh = least("NOM", "TYP", hours, False, sched)
            res5[(hours, sched)] = (x, wh)
            P("     %d h %-40s %s" % (hours, NAMES[sched], "none up to 4S40P" if x is None else "lid 4S%.2fP, %+.1f Wh usable" % (x, wh)))
    tr = []
    x72 = res5[(72, "W13")][0]
    r_ = sim1("NOM", x72, "TYP", 6, 72, False, "W13", tr)
    day2 = [t for t in tr if 24 <= t[0] < 48]
    lvl = [hh for w in ("W10", "W13") for hh in range(*WINDOWS[w])]
    node = {t[1]: t[2] for t in day2}
    held = [hh for hh in range(24) if abs(node[hh] - max(node.values())) < 0.05]
    top_b = max(t[8] for t in day2)
    top_l = max(t[9] for t in day2)
    ok_lvl = all(h in held for h in lvl)
    full = not (top_b < r_["eb_full"] - 0.05 and top_l < r_["el_full"] - 0.05)
    P("   Why the daylight windows read alike, from the model's own trace (NOM, TYP, 72 h, the lid at 4S%.2fP, the 06 UTC" % x72)
    P("   start's second day, window W13):")
    P("     node power at %s UTC: %s W" % ("/".join("%02d" % h for h in range(8, 18)), " ".join("%.0f" % node[h] for h in range(8, 18))))
    P("     level at %.1f W (the path's limit in the model) from %02d to %02d UTC; both windows' hours inside it: %s" % (
        max(node.values()), held[0], held[-1], "yes" if ok_lvl else "NO"))
    P("     the store's highest that day: base %.1f of %.1f Wh, lid %.1f of %.1f Wh: %s" % (
        top_b, r_["eb_full"], top_l, r_["el_full"], "FULL at some hour" if full else "never full"))
    if ok_lvl and not full:
        P("   So every Wh the tablet takes in a daylight window is a Wh the packs do not take, whichever level hours the window")
        P("   holds. After dark it comes from the store directly; with the converter enabled all day the idle draw of section 1")
        P("   is added for 24 h")
    else:
        P("   The daylight windows' equality is NOT explained by a level node and packs short of full here")
    P("")

    # 6. the extra store for Options A and B
    P("6. THE EXTRA USABLE STORE OPTIONS A (48 h) AND B (72 h) NEED WITH THE BUDGET (window W13), over the both-kept 4S9P lid, Wh")
    P("   at the lid's %.2f C (35E-equivalent); TYP the case, WAB a sensitivity. DRAWN is the circuit as drawn; the other cases" % EB.TMIN)
    P("   are the corrected path, HYPOTHETICAL and CONDITIONAL. DRAWN keeps min(available, cap), an upper bound on its harvest, so")
    P("   its store is a lower bound; a store does not cure the as-drawn path's defects (r11_dep.out)")
    res6, res6x = {}, {}
    for hf in (False, True):
        for hours in (48, 72):
            parts = []
            for key in ("DRAWN", "NOM", "NOM90", "WE", "WE90"):
                for b in (("TYP",) if key == "DRAWN" else ("TYP", "WAB")):
                    x, wh = least(key, b, hours, hf, "W13")
                    res6[(hf, hours, key, b)] = wh
                    res6x[(hf, hours, key, b)] = x
                    parts.append("%s %s %s" % (key, b, "none up to 4S40P" if wh is None else "%+.1f" % wh))
            P("     HF %-9s %d h (Option %s): %s" % ("listening" if hf else "available", hours, "A" if hours == 48 else "B", "; ".join(parts)))
    P("   OPTION A'S STORE AGAINST ITS DESIRED 72 h (the 48 h store run for 72 h, W13, TYP):")
    for hf in (False, True):
        parts = []
        for key in ("NOM", "NOM90", "WE", "WE90"):
            s72 = meanday(key, res6x[(hf, 48, key, "TYP")], "TYP", 72, hf, "W13")
            parts.append("%s %s" % (key, cell(s72)))
        P("     HF %-9s %s" % ("listening" if hf else "available", "; ".join(parts)))
    P("   The corrected path's TYP cases, NOM to WE90, as packs outside the case (a PROPOSAL; NH2054HD34 at %.1f Wh usable aged at" % NH_WH)
    P("   +20 C, runtime.out 1, %.3f kg each; fewer Wh at the lid's 13 C, so the count is a lower bound):" % NH_KG)
    for hf in (False, True):
        for hours in (48, 72):
            v_ = [res6[(hf, hours, k, "TYP")] for k in ("NOM", "NOM90", "WE", "WE90")]
            v_ = [x for x in v_ if x is not None]
            P("     HF %-9s %d h TYP: %.0f to %.0f Wh, %d to %d packs, %.2f to %.2f kg" % (
                "listening" if hf else "available", hours, min(v_), max(v_), math.ceil(min(v_) / NH_WH), math.ceil(max(v_) / NH_WH),
                math.ceil(min(v_) / NH_WH) * NH_KG, math.ceil(max(v_) / NH_WH) * NH_KG))
    P("")

    # 7. battery only
    pk = PACK0
    load = TP.LOAD
    nb, nl = 6, LID_A
    v_l = pk.n_s * 3.60

    def usable(avg, t_):
        pb, pl = avg * nb / (nb + nl), avg * nl / (nb + nl)
        i = pl / v_l
        ll = (i * vak[1] + i * i * TP.v("r_lid_dsg")) / pl
        return pk.usable_wh(pb, t_, pk.age80, "3v00", nb)[0] + pk.usable_wh(pl, t_, pk.age80, "3v00", nl)[0] * (1 - ll)
    P("7. BATTERY-ONLY ENDURANCE with the budget (no solar), to the kit's shutdown, both packs at +20 C then at %.0f C, as" % T_COLD)
    P("   runtime.out 1 (A35 there: 544.4 / 224.5 Wh, 12.71 / 5.24 h). In a window schedule the hours depend on whether the")
    P("   day's window falls inside the run: 'window in the run' charges the day's %.1f Wh at VBAT to the store, 'window after'" % e_win)
    P("   does not (the tablet then runs on its own battery). The options' stores add the section 6 extra (TYP) as an")
    P("   external store, its Wh taken as usable at +20 C and x 0.4124 at %.0f C (runtime.py's cold factor, INFERRED)" % T_COLD)
    stores = [("A35, the present both-kept store", 0.0)]
    for hf_ in (False,):
        for hours in (48, 72):
            for key in ("NOM", "WE"):
                wh = res6[(hf_, hours, key, "TYP")]
                if wh is not None:
                    stores.append(("A35 + the Option %s store (%s TYP, %+.1f Wh)" % ("A" if hours == 48 else "B", key, wh), wh))
    res7 = {}
    for hf in (False, True):
        base_w = load + drain_w + (hf_rx if hf else 0.0)
        for label, add in stores:
            hrs = []
            for t_ in (20.0, T_COLD):
                ext = add * (1.0 if t_ > 0 else 0.4124)
                u_in = usable(base_w + e_win / 24.0, t_) + ext
                h_none = (usable(base_w, t_) + ext) / base_w
                h_in = (u_in - e_win) / base_w
                u_any = usable(base_w + e_any / 24.0, t_) + ext
                h_any = u_any / (base_w + e_any / 24.0)
                hrs.append((h_none, h_in, h_any))
            res7[(hf, label)] = hrs
            P("     HF %-9s %-48s no budget %5.2f / %5.2f h; window in the run %5.2f / %5.2f h; any time %5.2f / %5.2f h" % (
                "listening" if hf else "available", label, hrs[0][0], hrs[1][0], hrs[0][1], hrs[1][1], hrs[0][2], hrs[1][2]))
    P("   (+20 C / %.0f C; the 'window after' figure equals 'no budget')" % T_COLD)
    P("")
    P("END. The budget is a PROPOSAL; nothing is measured. No result here is demonstrated capability: the circuit as drawn")
    P("fails; the corrected path is HYPOTHETICAL and CONDITIONAL on three undocumented efficiencies; external packs are a")
    P("PROPOSAL whose join (D-20's DC entry, EQ-13 (b), or VBAT, reopening D-06, EQ-13 (d)) is not designed.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
