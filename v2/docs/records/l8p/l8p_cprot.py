#!/usr/bin/env python3
"""l8p_cprot.py: record l8p, round 11 (Layer 4 AI-scope register row (c), tasks L4A-67 and L4A-68; MESHSAT-1357, 7 October 2026).

L8P-R10-F1 (record l8p round 10, L8P-BREAKER.md 15c): at the breaker's held 23.93 A from the 76.25 C inside air the three 25 A MINI
blades carry 103.6 % of their printed rerated current. This round treats it as an unresolved design choice (constitution section 4:
at most three materially different approaches, none lowering a protection, the 18 A service or a printed rating's margin), selects
one as SESSION with its end condition, and draws it (apply_gen_sch_p_ocheld.py, release-guarded, composed with board P's drafts,
read by check_l8p_ocn and mutated). L4A-67: C-PROT rev 1 re-evaluated on the corrected circuit, every series part below and above
the trip on its printed limits or its missing figure named. L4A-68: the guard's allowance (record l8p 10c) printed for its consumers;
the replay of L4-E11's 20f, 22 and 28 is record l4e11's l4e11_rowc.py.

This script prints:
  0. its pins (the records and the makers' documents it reads, sha256);
  1. the finding and the case (RECORD: record l8p round 10, l8p_rowc.py's own computation, records l9stk and l8p);
  2. the three approaches on printed figures: (A) a fuse or a holder arrangement, (B) a held-overcurrent trip into the -1's own latch,
     (C) a controller with a tighter printed current-limit spread;
  3. the selection (SESSION) and its end condition;
  4. the selected trip on printed figures: its window, its delays, the crowbar into the -1's latch, the arming on PGD, the parts'
     ratings and leakages, power-up and the start, its standing current, its own single failures;
  5. the draft composed in L4-E9's order, read by check_l8p_netlist.py and check_l8p_och.py, and its mutations;
  6. L4A-67: C-PROT rev 1 for the guard on the corrected circuit, part by part, with the trip intact and with it latently failed;
  7. L4A-68: the guard's allowance as its consumers are to restate it (the texts of the two apply scripts);
  8. the verdicts;
  9. the predicates.
Labels: PRINTED (a maker's printed limit or maximum), TYPICAL (never a limit), READING (this record's reading of a maker's drawing),
INFERRED (arithmetic on printed figures by a stated rule), MODEL, RECORD (another record's figure, read from its file), ASSUMED.
Nothing has been built, bought or measured; no V2 board exists.

Run from anywhere:  python3 v2/docs/records/l8p/l8p_cprot.py   (l8p_cprot.out is its output, regenerated with _bin/regen_out.py).
Exit 0: printed, whatever the verdicts; 3: refused (an input missing, a sha256 that differs, a printed row not found, a draft that
does not compose)."""
import hashlib
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import l8p_rowc as RC          # noqa: E402  round 10's computation, read, never retyped
import l8p_drafts as D         # noqa: E402  the composition helpers and L4-E9's board P order
import check_l8p_netlist as C  # noqa: E402
import check_l8p_och as O      # noqa: E402
import gen_netlist as GN       # noqa: E402


class Refused(Exception):
    pass


def refuse(msg):
    raise Refused(msg)


RECS = {
    "rowc": "v2/docs/records/l8p/l8p_rowc.out",
    "c4": "v2/docs/records/l8p/l8p_c4.out",
    "prot": "v2/docs/records/l9stk/l9stk_protection.out",
    "stk": "v2/docs/records/l9stk/L9-STACKUPS.md",
    "draft": "v2/docs/records/l8p/apply_gen_sch_p_ocheld.py",
    "brk": "v2/docs/records/l8p/apply_gen_sch_p_breaker.py",
    "dio": "v2/docs/records/l8p/apply_gen_sch_p_idealdiode.py",
    "och": "v2/docs/records/l8p/check_l8p_och.py",
    "gen_p": "v2/ecad/tools/gen_sch_p.py",
    "l9g": "v2/docs/records/l8p/inputs/l9stk-section15.9-bb6d2c8f.md",
}
DOCS = {
    "tps37": ("v2/vendor/ti/ti-tps37-snvsbj1e.pdf", "TI TPS37, SNVSBJ1E (August 2023)"),
    "opa187": ("v2/vendor/ti/held/ti-opa187-sbos807e.pdf", "TI OPA187, SBOS807E (held back)"),
    "lm5069": ("v2/vendor/ti/ti-lm5069.pdf", "TI LM5069, SNVS452G"),
    "lm5066i": ("v2/vendor/ti/held/ti-lm5066i-snvs950c.pdf", "TI LM5066I, SNVS950C (held back, fetch_held_back_rowc.py)"),
    "ao3401a": ("v2/vendor/power/aos-ao3401a-p-mosfet.pdf", "AOS AO3401A"),
    "n7002": ("v2/vendor/power/jscj-2n7002-c8545.pdf", "JSCJ 2N7002 (C8545)"),
    "csd": ("v2/vendor/battery/ti-csd18510q5b.pdf", "TI CSD18510Q5B, SLPS632"),
    "bzt": ("v2/vendor/diodes/diodes-bzt52c-ds18004.pdf", "Diodes BZT52C series, DS18004"),
    "lf297": ("v2/vendor/keystone/littelfuse-297-ficcorp.pdf", "Littelfuse MINI 297"),
}
PIN = {"lm5066i": "a759a5d04fe5b81577af575153fd528f0f03f147c892040eac6c51e400693628"}

# ---------------------------------------------------------------- the trip as drawn (read back from the draft below)
G_RIN, G_RF = 1.00e3, 19.3e3
C_CTS1, C_CTS2, C_TOL = 4.7e-9, 47e-9, 0.05           # C0G, 5 %
R136, R137, R138, R139, R141, R142, R140 = 47e3, 100e3, 4.7e3, 1e6, 1e6, 1e3, 0.39
PACK_LEAST, PACK_MOST, CLAMP = 10.6, 16.8, 29.2
SERVICE_TRUE = O.SERVICE_TRUE                          # 18.80 A: record l9stk condition C4
DOUBLING_K = 10.0                                      # the record's ASSUMED doubling of an off leakage every 10 K (l8p 12j, l9stk 15.9)
SITE = 86.25                                           # the site the record counts small parts' leakage at (the air plus 10 K)


def p(rel):
    return os.path.join(ROOT, rel)


def sha(path, n=64):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()[:n]


def read(rel):
    if not os.path.exists(p(rel)):
        refuse("missing input %s" % rel)
    with open(p(rel), encoding="utf-8", errors="replace") as f:
        return f.read()


def doc(key):
    rel = DOCS[key][0]
    if not os.path.exists(p(rel)):
        refuse("missing maker's document %s (%s)" % (rel, DOCS[key][1]))
    if key in PIN and sha(p(rel)) != PIN[key]:
        refuse("%s: sha256 %s, pinned %s" % (rel, sha(p(rel), 16), PIN[key][:16]))
    return p(rel)


def pdftext(key, first=None, last=None):
    args = ["pdftotext", "-layout"]
    if first:
        args += ["-f", str(first), "-l", str(last or first)]
    r = subprocess.run(args + [doc(key), "-"], capture_output=True)
    if r.returncode != 0:
        refuse("pdftotext failed on %s" % DOCS[key][0])
    return r.stdout.decode("utf-8", "replace")


def need(text, pat, what, flags=re.S):
    m = re.search(pat, text, flags)
    if not m:
        refuse("%s: not found (%s)" % (what, pat[:70]))
    return m


def flat(s):
    return re.sub(r"\s+", " ", s)


# ---------------------------------------------------------------- the computation
def compute():
    R = {"pins": []}
    for k, rel in RECS.items():
        read(rel)
        R["pins"].append((sha(p(rel), 16), rel))
    for k in DOCS:
        doc(k)
        R["pins"].append((sha(p(DOCS[k][0]), 16), DOCS[k][0]))
    W = RC.compute()                                     # round 10's own figures (its pins checked by it)
    R["W"] = W
    I, T_AIR = W["I"], W["T_AIR"]

    # 1. the case (RECORD)
    rowc = flat(read(RECS["rowc"]))
    need(rowc, r"23\.93 A held is 103\.6 % of the rerated current at the air \(OVER by 0\.83 A, 3\.6 %\)", "round 10's finding (l8p_rowc.out 3a)")
    prot = flat(read(RECS["prot"]))
    m = need(prot, r"current limit ([\d.]+) / ([\d.]+) / ([\d.]+) A \(VCL ([\d.]+) to ([\d.]+) mV", "the breaker's limits")
    LIM = tuple(float(m.group(k)) for k in (1, 2, 3))
    VCL = (float(m.group(4)), float(m.group(5)))
    m = need(prot, r"breaker ([\d.]+) to ([\d.]+) A \(VCB ([\d.]+) to ([\d.]+) mV\)", "the circuit breaker")
    CB = (float(m.group(1)), float(m.group(2)))
    m = need(prot, r"clearing ([\d.]+) ms at most from the limit's onset \(tCL ([\d.]+) us typical, no maximum printed\)", "the clearing")
    CLEAR, TCL_TYP = float(m.group(1)) * 1e-3, float(m.group(2)) * 1e-6
    m = need(prot, r"the fault pulse: ([\d.]+) W for ([\d.]+) ms against ([\d.]+) W derated: ([\d.]+)", "the fault pulse")
    PULSE = tuple(float(m.group(k)) for k in (1, 2, 3, 4))
    m = need(prot, r"VIN to SENSE's 0\.3 V maximum is passed above ([\d.]+) A", "VIN to SENSE's 0.3 V")
    VSNS_I = float(m.group(1))
    m = need(prot, r"acts only while PGD is low \(the breaker off, starting or in a fault: VDS over ([\d.]+) to ([\d.]+) V\)", "PGD's VDS")
    PGD_VDS = (float(m.group(1)), float(m.group(2)))
    need(prot, r"a persistent fault on the -1 \(selected\) \| one event, then latched until UVLO or VIN cycles", "the -1's latch row")
    need(prot, r"recovery: redocking, the input's return \(DD-7\), the guard's cycle", "the -1's recovery")
    stk = flat(read(RECS["stk"]))
    m = need(stk, r"\| 50 A for 600 s \(gauge failed\) \| ([\d.]+) C steady, reached before clearance \| \*\*OVER\*\* \| within \|", "the copper's 50 A row")
    CU50 = float(m.group(1))
    need(stk, r"board A's pack bands \| 105 C \| 125 C \|", "board A's band limits")
    need(stk, r"board E's pack bands \| 105 C \| 120 C \|", "board E's band limits")
    m = need(stk, r"\| Sense RS \| 4 mOhm and 7\.5 mOhm in parallel, 2\.6087 mOhm, 1 % and at most 50 ppm/K: plus or minus 1\.5 % for the parts only .*? \| its window ([\d.]+) to ([\d.]+) mOhm \|", "RS's window")
    RS = (float(m.group(1)), float(m.group(2)))
    c4 = flat(read(RECS["c4"]))
    m = need(c4, r"cold at most ([\d.]+) uA \(U60 16, U61 2\.25, the pull-up's leakage 1\.16, Q61 off 5\.58\), ([\d.]+) uA with the clamp's gates doubled; path 1 tripped at most ([\d.]+) uA \(the pull-up across 435\.6 kOhm\), ([\d.]+) uA with one of its resistors shorted\. Allowances taken: (\d+) uA cold, (\d+) uA tripped", "the guard's draw (l8p 10c)")
    DRAW = tuple(float(m.group(k)) for k in (1, 2, 3, 4))
    ALLOW = (float(m.group(5)), float(m.group(6)))
    m = need(c4, r"U62 LM26LVQISDX-130/NOPB on the same pour, supplied by U63 TPS70950DBVR from VBAT", "path 2 on VBAT (l8p 10c)")
    l9g = flat(read(RECS["l9g"]))
    need(l9g, r"The switch and the regulator draw 18\.25 uA at their printed maxima, against the 30 uA this round allows the guard\.",
         "record l9stk 15.9's allowance sentence (inputs copy at bb6d2c8f)")
    R.update(LIM=LIM, VCL=VCL, CB=CB, CLEAR=CLEAR, TCL_TYP=TCL_TYP, PULSE=PULSE, VSNS_I=VSNS_I, PGD_VDS=PGD_VDS, CU50=CU50, RS=RS,
             DRAW=DRAW, ALLOW=ALLOW)

    # 2A. a fuse or a holder arrangement (Littelfuse's printed rerating; record l9stk's copper)
    need_f = I / 25.0
    cu60 = T_AIR + (CU50 - T_AIR) * (60.0 / 50.0) ** 2           # the copper's steady rise at the 30 A blade's 200 % (I^2, the record's own scaling)
    R.update(need_f=need_f, f_air=W["f_air"], f_band=W["f_band"], b30=W["blade30_rr"], b30_135=W["blade30_135"], cu60=cu60,
             band_pinned=(125.0, 120.0))

    # 2C. a controller with a tighter printed limit spread (TI LM5066I)
    t = flat(pdftext("lm5066i"))
    m = need(t, r"Current limit threshold voltage CL = VDD ([\d.]+) ([\d.]+) ([\d.]+) VCL mV \(VVIN_K – VSENSE\) CL = GND ([\d.]+) ([\d.]+) ([\d.]+)",
             "LM5066I VCL rows")
    V66 = (float(m.group(4)), float(m.group(6)))
    m = need(t, r"VIN, SENSE, OUT voltage ([\d.]+) ([\d.]+) V", "LM5066I recommended VIN")
    VIN66 = float(m.group(1))
    rs_spread = RS[1] / RS[0]
    most_at = lambda least: V66[1] / (V66[0] / least / rs_spread) if False else least * (V66[1] / V66[0]) * rs_spread
    R.update(V66=V66, VIN66=VIN66, rs_spread=rs_spread, c_most_1832=most_at(LIM[0]), c_most_1880=most_at(SERVICE_TRUE),
             c_need=W["I_rr_air"] / LIM[0])

    # 4a. the window (check_l8p_och's own arithmetic on the drawn values)
    dr = read(RECS["draft"])
    for pat in (r'r\("R132", "1\.00k 0\.1% 25ppm', r'r\("R133", "19\.3k 0\.1% 25ppm', r'c\("C119", "4\.7n 50V C0G 5%', r'c\("C120", "47n 50V C0G 5%',
                r'r\("R136", "47k"', r'r\("R137", "100k"', r'r\("R142", "1k", "OCH_GD", "OCH_CG"\); r\("R138", "4\.7k"',
                r'r\("R140", "0\.39R 1% 2512', r'r\("R139", "1M", "BRK_VIN", "OCH_EG"\); r\("R141", "1M", "OCH_EG", "PACK_N"\)'):
        need(dr, pat, "the draft's value %s" % pat[3:9])
    t37 = flat(pdftext("tps37"))
    need(t37, r"VITP \(Overvoltage\) VIT = 800 mV \(3\) 0\.792 0\.800 0\.808 V", "TPS37 VITP at 800 mV")
    need(t37, r"RCTS 88 100 122 Kohms", "TPS37 RCTS")
    need(t37, r"tCTSx \(min\) = -ln \(0\.31\) x RCTSx \(min\) x CCTSx_EXT \(min\)", "TPS37 Equation 5")
    need(t37, r"tCTSx \(max\) = -ln \(0\.25\) x RCTSx \(max\) x CCTSx_EXT \(max\)", "TPS37 Equation 6")
    need(t37, r"VIT = 800 mV CCTS1 = CCTS2 = Open 8 17 [µμ]s", "TPS37 tCTS without a capacitor")
    need(t37, r"tSD Startup Delay \(4\) 2 ms", "TPS37 tSD")
    need(t37, r"VRESET = 5\.5 V 300 nA Open-Drain leakage", "TPS37 open-drain leakage")
    need(t37, r"Current IRESET1, IRESET2, IRESET1, IRESET2 0 ±5 mA", "TPS37 recommended RESET current")
    need(t37, r"Voltage VDD 2\.7 65 V", "TPS37 VDD range")
    need(t37, r"ISENSE VIT = 800 mV 100 nA", "TPS37 ISENSE")
    need(t37, r"VIT = 800 mV 1 2\.6 [µμ]A", "TPS37 IDD at 800 mV")
    o = flat(pdftext("opa187"))
    need(o, r"OFFSET VOLTAGE ±1 ±10 [µμ]V VOS Input offset voltage TA = –40°C to \+125°C ±0\.001 ±0\.015 [µμ]V/°C", "OPA187 VOS and drift")
    need(o, r"\(V–\) – 0\.1 \(V\+\) – 2 V", "OPA187 VCM")
    need(o, r"IO = 0 mA, TA = –40°C to \+125°C 150 [µμ]A", "OPA187 IQ")
    lo, hi = O.window({"comps": {"R132": {"value": "1.00k"}, "R133": {"value": "19.3k"}}, "pins": {}, "on": {}})
    gd = O.GAIN_TOL + O.GAIN_TCR * O.GAIN_DT
    vos_tot = O.VOS
    r10_hi = (O.VITP[0] - (1 + G_RF / G_RIN * (1 + gd) / (1 - gd)) * vos_tot - O.IB * G_RF * (1 + gd) - O.ISENSE * 1e3) / \
             ((G_RF / G_RIN * (1 + gd) / (1 - gd)) * SERVICE_TRUE)
    r10_lo = (O.VITP[2] + (1 + G_RF / G_RIN * (1 + gd) / (1 - gd)) * vos_tot + O.IB * G_RF * (1 + gd) + O.ISENSE * 1e3) / \
             ((G_RF / G_RIN * (1 - gd) / (1 + gd)) * O.BLADE_BAND)
    R.update(win=(lo, hi), r10_room=(r10_lo / O.R10_NOM - 1, r10_hi / O.R10_NOM - 1),
             r10_assumed=O.R10_TOL + O.R10_TCR * O.R10_DT, out_service=G_RF / G_RIN * SERVICE_TRUE * O.R10_NOM,
             out_18=G_RF / G_RIN * 18.0 * O.R10_NOM, out_10=G_RF / G_RIN * 10.0 * O.R10_NOM)

    # 4b. the delays (TI's Equations 5 and 6; the no-capacitor delay's least is not printed, taken 0)
    tcts1 = (-math.log(0.31) * 88e3 * C_CTS1 * (1 - C_TOL), -math.log(0.25) * 122e3 * C_CTS1 * (1 + C_TOL) + 17e-6)
    tcts2 = (-math.log(0.31) * 88e3 * C_CTS2 * (1 - C_TOL), -math.log(0.25) * 122e3 * C_CTS2 * (1 + C_TOL) + 17e-6)
    R.update(tcts1=tcts1, tcts2=tcts2, e10=0.282e-3, tsd=2e-3)

    # 4c. the crowbar into the -1's latch
    i_c = lambda v, r=R140 * 1.01: v / r
    R.update(ic_least=i_c(PACK_LEAST), ic_16=i_c(PACK_MOST), ic_clamp=i_c(CLAMP, R140 * 0.99),
             peak_16=i_c(PACK_MOST, R140 * 0.99) + LIM[2], peak_clamp=i_c(CLAMP, R140 * 0.99) + LIM[2],
             vlim=LIM[2] * R140 * 1.01)
    p_lim = R["vlim"] ** 2 / (R140 * 0.99)
    e_lim = p_lim * (CLEAR + 50e-6)
    c_kit = 593e-6
    e_cap = 0.5 * c_kit * R["vlim"] ** 2
    R.update(p_lim=p_lim, e_lim=e_lim, e_cap=e_cap, e_r140=e_lim + e_cap + R["peak_clamp"] ** 2 * R140 * 16.5e-6)
    # the sequence: the trip's sense delay, the gate drive, the -1's clearing; the arming's delay after PGD falls
    t_gate = 75e-9 / ((PACK_LEAST - 4.5) / R142)                  # Qg(4.5 V) 75 nC at most through R142 from BRK_VIN
    R.update(t_gate=t_gate, t_event=tcts1[1] + t_gate + CLEAR, arm_margin=tcts2[0] - (t_gate + CLEAR))
    # 4d. ratings and leakages
    vgs110 = (PACK_LEAST * R136 / (R136 + R137), CLAMP * R136 / (R136 + R137))
    leak_n = 80e-9 * 2 ** ((SITE - 25.0) / DOUBLING_K)             # 2N7002 80 nA at 25 C (PRINTED), doubled (ASSUMED)
    leak_p = 5e-6 * 2 ** ((SITE - 55.0) / DOUBLING_K)              # AO3401A 5 uA at 55 C (PRINTED), doubled (ASSUMED)
    leak_p101 = 5e-6 * 2 ** ((101.0 - 55.0) / DOUBLING_K)
    R.update(vgs110=vgs110, leak_n=leak_n, leak_p=leak_p, v_off110=(leak_n + 0.3e-6) * R136, v_cg_off=leak_p * R138,
             v_cg_off101=leak_p101 * R138, vth_p=0.5, vth_csd=1.2, ireset1=CLAMP / (R136 + R137), ireset2=CLAMP / R139,
             vgs112=CLAMP / 2, vcg=12.7, ig110=(CLAMP - 11.4) / R142 + 12.7 / R138, iz=(CLAMP - 11.4) / R142,
             stand=(150e-6, 2.6e-6, PACK_MOST / (R139 + R141)))
    need(flat(pdftext("ao3401a")), r"Gate-Source Voltage VGS ±12 V", "AO3401A VGS")
    need(flat(pdftext("ao3401a")), r"VGS\(th\) Gate Threshold Voltage VDS=VGS ID=-250mA -0\.5 -0\.9 -1\.3 V", "AO3401A VGS(th)")
    need(flat(pdftext("ao3401a")), r"TJ=55°C -5", "AO3401A IDSS at 55 C")
    need(flat(pdftext("n7002")), r"Zero Gate Voltage Drain Current IDSS VDS=60 V, VGS=0 V 80 nA", "2N7002 IDSS")
    need(flat(pdftext("n7002")), r"Gate-Source Voltage VGS ±20 V", "2N7002 VGS")
    cs = flat(pdftext("csd"))
    need(cs, r"VGS\(th\) Gate-to-source threshold voltage VDS = VGS, ID = 250 μA 1\.2 1\.7 2\.3 V", "CSD18510Q5B VGS(th)")
    need(cs, r"Qg Gate charge total \(4\.5 V\) 58 75 nC", "CSD18510Q5B Qg")
    need(cs, r"IDM Pulsed Drain Current, TA = 25°C\(2\) 400 A", "CSD18510Q5B IDM")
    need(cs, r"IDSS Drain-to-source leakage current VGS = 0 V, VDS = 32 V 1 μA", "CSD18510Q5B IDSS")
    need(flat(pdftext("bzt")), r"BZT52C12 WH 12 11\.4 12\.7", "BZT52C12 VZ")
    l69 = flat(pdftext("lm5069"))
    need(l69, r"When the external MOSFET VDS increases above 2\.5 V the PGD indicator switches low", "LM5069 PGD")
    need(l69, r"If the voltage across RS reaches 55 mV the load current is limited and the fault timer activates", "LM5069 SENSE")
    return R


def compose():
    """The draft composed in L4-E9's board P order (this record's breaker and ideal diode at the list's slot, then this round's draft,
    then Layer 6's two tables), read by check_l8p_netlist and check_l8p_och, mutated, and its refusals."""
    out = {}
    with tempfile.TemporaryDirectory() as d:
        seq = D.order("p", "fwd")
        mine = D.mine_seq("p")
        i = max(seq.index(x) for x in mine)
        seq = seq[:i + 1] + [p(RECS["draft"])] + seq[i + 1:]
        gen, res = D.compose("p", seq, d, "och")
        out["steps"] = [(os.path.relpath(s, os.path.join(ROOT, "v2", "docs", "records")), r) for s, (_n, r) in zip(seq, res)]
        if any(not r.startswith("OK") for _n, r in res) or len(res) != len(seq):
            refuse("the composition stopped: %s" % res)
        rc, net, table = D.netlist_text("p", gen, d, "och")
        if rc:
            refuse("board P's generator stopped on the composition: %s" % net)
        nl = C.read_netlist(open(net, "rb").read())
        out["parts"] = len(nl["comps"])
        kit, verdicts = C.run({"p": net}, out=open(os.devnull, "w"))
        out["l8p"] = verdicts["p"]
        lines = []
        _v, lines = C.judge("p", nl)
        out["l8p_lines"] = lines
        out["och"] = O.judge(nl)["OCH"]
        out["win_drawn"] = O.window(nl)
        muts = []
        for name, ops in MUTATIONS:
            q = D.mutate_ops(net, d, "m%d" % len(muts), ops)
            v, why = O.judge(C.read_netlist(open(q, "rb").read()))["OCH"]
            muts.append((name, v, why[0] if why else ""))
        out["muts"] = muts
        # refusals: without the breaker and the ideal diode; a second time; the repository's own generator
        bare = os.path.join(d, "bare_gen_sch_p.py")
        shutil.copy(D.GEN["p"], bare)
        r1 = subprocess.run([sys.executable, "-B", p(RECS["draft"]), bare], capture_output=True)
        r2 = subprocess.run([sys.executable, "-B", p(RECS["draft"]), gen], capture_output=True)
        r3 = subprocess.run([sys.executable, "-B", p(RECS["draft"]), D.GEN["p"], "--write"], capture_output=True)
        out["refusals"] = [(r1.returncode, (r1.stderr.decode().strip().splitlines() or [""])[-1][:90]),
                           (r2.returncode, (r2.stderr.decode().strip().splitlines() or [""])[-1][:90]),
                           (r3.returncode, (r3.stderr.decode().strip().splitlines() or [""])[-1][:90])]
        out["net_sha"] = sha(net, 16)
    return out


MUTATIONS = (
    ("the crowbar's resistor on BRK_VIN, upstream of the sense pair (the breaker could never end it)", [("move", "R140", "1", "BRK_VIN")]),
    ("the amplifier's input and reference exchanged (R132 from PACK_N, R134 from GND)", [("move", "R132", "1", "PACK_N"), ("move", "R134", "1", "GND")]),
    ("RESET1 on UVLO instead of the arming FET (a sink on UVLO; a retry, not the -1's latch)", [("move", "U107", "4", "BRK_UVLO")]),
    ("the arming on BRK_VIN instead of PGD (the crowbar armed at power-up)", [("move", "U107", "3", "BRK_VIN")]),
    ("the crowbar at 2 Ohm (its own current under the breaker's most limit)", [("value", "R140", "2.0R 1% 2512")]),
    ("the sense delay capacitor removed", [("drop", "C119")]),
    ("the crowbar's gate clamp removed", [("drop", "D105")]),
    ("the gain at 10 kOhm (the window off)", [("value", "R133", "10.0k 0.1% 25ppm")]),
    ("the crowbar's drain on DOCK_EN_OUT (a sink on the enable loop)", [("move", "R140", "2", "DOCK_EN_OUT")]),
)


def fmt(x, n=2):
    return ("%%.%df" % n) % x


def render(R, K):
    W = R["W"]
    o = []
    w = o.append
    I, T_AIR = W["I"], W["T_AIR"]
    lo, hi = R["win"]
    w("l8p_cprot: record l8p round 11, Layer 4 register row (c): L8P-R10-F1 as a design choice, L4A-67 (C-PROT rev 1 for the guard on the")
    w("corrected circuit) and L4A-68 (the guard's allowance for its consumers) (MESHSAT-1357, 7 October 2026). Desk arithmetic on the makers'")
    w("printed figures and the records' own; nothing was built, bought or measured. LABELS: PRINTED; TYPICAL (never a limit); READING;")
    w("INFERRED; MODEL; RECORD; ASSUMED.")
    w("")
    w("0. PINS (sha256/16)")
    for s_, rel in R["pins"]:
        w("   %s  %s" % (s_, rel))
    w("")
    w("1. THE FINDING AND THE CASE (RECORD)")
    w("   L8P-R10-F1 (record l8p round 10, l8p_rowc.out 3a, computed again here by l8p_rowc.py): at the breaker's held %s A from %s C the three" % (fmt(I), fmt(T_AIR)))
    w("     25 A MINI blades (P's F1, E's F3, A's F1; Littelfuse 297) carry %s %% of their printed rerated current (%s A at the air, %s A at the" % (
        fmt(100 * I / W["I_rr_air"], 1), fmt(W["I_rr_air"]), fmt(W["I_rr_band"])))
    w("     band's %s C): OVER by %s A; the 18 A service is %s %% of it: within" % (fmt(W["t_band_a"]), fmt(W["over_air_a"]), fmt(100 * W["f_18"], 1)))
    w("   the case: C-PROT rev 1 (the breaker's band %s to %s A held from %s C, board P's FETs welded, no firmware, 10 A held and 18 A for 60 s" % (
        fmt(R["LIM"][0]), fmt(R["LIM"][2]), fmt(T_AIR)))
    w("     never interrupted; record l9stk's condition C4: an indicated 18 A may be a true %s A)" % fmt(SERVICE_TRUE))
    w("   what may not move (the brief, constitution 4): no protection lowered, not the 18 A service, no printed rating's margin")
    w("")
    w("2. THREE APPROACHES ON PRINTED FIGURES (constitution section 4: at most three, materially different)")
    w("   (A) A FUSE OR A HOLDER ARRANGEMENT THAT CARRIES %s A ON ITS PRINTED RERATING" % fmt(I))
    w("     a 25 A element needs a printed rerating of at least %s at %s C (and at the band's %s C); the held MINI 297 prints %s and %s" % (
        fmt(R["need_f"], 4), fmt(T_AIR), fmt(W["t_band_a"]), fmt(R["f_air"], 4), fmt(R["f_band"], 4)))
    w("       (READING of its line); no other maker's sheet held or read prints a 25 A element at or above it: NOT AVAILABLE ON PRINTED FIGURES")
    w("     a 30 A element (0297030) carries it on its own row (%s A rerated at the air), but the copper was sized and coordinated at the 25 A" % fmt(R["b30"]))
    w("       blade (record l9stk 14.4 to 14.6): the 30 A blade's 135 %% to 200 %% band runs from %s A to 60 A for up to 600 s, and the bands'" % fmt(R["b30_135"]))
    w("       steady reading at 60 A, scaled by the current squared from the record's own 50 A row (%s C), is %s C over board A's %s C and" % (
        fmt(R["CU50"]), fmt(R["cu60"], 1), fmt(R["band_pinned"][0], 0)))
    w("       board E's %s C with the plating pinned: a protection lowered: REFUSED (round 10's (a)); the copper's weight is the open OWNER" % fmt(R["band_pinned"][1], 0))
    w("       DECISION (L9STK CU), not this record's to move")
    w("     a holder or busbar that cools the blade: Littelfuse's rerating curve is drawn against the AMBIENT temperature (READING of its axis);")
    w("       no printed figure of the 297 sheet or the 3568's credits a holder or busbar with a lower blade temperature, and the 76.25 C air")
    w("       is every blade's ambient inside the sealed case: NO PRINTED BASIS")
    w("     verdict (A): NOT SUPPORTED on printed figures")
    w("   (B) A HELD-OVERCURRENT TRIP ON BOARD P THAT ENDS IN THE -1'S OWN LATCH (apply_gen_sch_p_ocheld.py; section 4)")
    w("     the held current is ended over a window of %s to %s A (printed maxima; R10 as the record assumes it, E-6), inside %s A (the" % (fmt(lo), fmt(hi), fmt(SERVICE_TRUE)))
    w("       service's true current, C4) and %s A (the blades at the band); above it a single event per recovery, the -1's own" % fmt(O.BLADE_BAND))
    w("     verdict (B): SUPPORTED on printed figures, CONDITIONAL as section 4 names")
    w("   (C) A CONTROLLER WITH A TIGHTER PRINTED CURRENT-LIMIT SPREAD (TI LM5066I, SNVS950C, the record's E-5 fallback)")
    w("     its VCL at CL = GND %s to %s mV (PRINTED, -40 to 125 C) with RS's window spread %s (record l9stk 15.4): the least kept at %s A" % (
        fmt(R["V66"][0], 0), fmt(R["V66"][1], 0), fmt(R["rs_spread"], 4), fmt(R["LIM"][0])))
    w("       gives a most of %s A: under the air's %s A by %s A, OVER the band's %s A; at the service's true %s A the most is %s A, over both" % (
        fmt(R["c_most_1832"]), fmt(W["I_rr_air"]), fmt(W["I_rr_air"] - R["c_most_1832"]), fmt(W["I_rr_band"]), fmt(SERVICE_TRUE), fmt(R["c_most_1880"])))
    w("     its recommended VIN starts at %s V, %s V under the pack's least %s V; and it replaces the whole breaker of record l9stk 15.4 to 15.6" % (
        fmt(R["VIN66"], 1), fmt(PACK_LEAST - R["VIN66"], 1), fmt(PACK_LEAST, 1)))
    w("       (its power limit, timer, SOA, latch and the drafts of rounds 1 to 4)")
    w("     verdict (C): NOT SELECTED (fails the band reading and C4's service current on printed figures; the largest redesign of the three)")
    w("")
    w("3. THE SELECTION (SESSION, decision L8P-R11-D1): (B)")
    w("   why: the one approach that ends every held current under the blades' printed rerated current at both readings without moving the")
    w("     breaker, the copper, the 18 A service or any printed margin; it adds a protection and lowers none; every part type is in the kit")
    w("   END CONDITION (any one): (1) R10's maker sheet (E-6) reads a tolerance with its temperature coefficient over 130 K outside %s to %s %%;" % (
        fmt(100 * R["r10_room"][0], 1), fmt(100 * R["r10_room"][1], 1)))
    w("     (2) Layer 6 finds no R140 whose maker prints a single pulse of at least %s J in 1.4 ms; (3) a check of this round finds a held" % fmt(R["e_r140"], 2))
    w("     current over %s A, a trip at or under %s A, or a crowbar event that does not end in the -1's latch, and a second negative check of" % (fmt(O.BLADE_BAND), fmt(SERVICE_TRUE)))
    w("     the same trip follows; then (C) with its band reading resolved, or the blades' evidence route (round 10's (c)) as the supplier's")
    w("")
    w("4. THE TRIP ON PRINTED FIGURES (B)")
    w("   4a. THE WINDOW (INFERRED on PRINTED rows; R10 ASSUMED): OCH_A = %s x I x R10 (U106 inverting, R133 over R132); U107's VITP %s to %s V" % (
        fmt(G_RF / G_RIN, 1), fmt(O.VITP[0], 3), fmt(O.VITP[2], 3)))
    w("     (TI SNVSBJ1E 7.5, -40 to 125 C); R132 and R133 at 0.1 %% and 25 ppm/K over 100 K; OPA187's VOS %s uV in all (10 uV, 0.015 uV/C over" % fmt(O.VOS * 1e6, 1))
    w("     100 K, CMRR 126 dB at VCM V-), IB 7.5 nA, U107's ISENSE 100 nA through R135; R10 2 mOhm at 1 % and 75 ppm/K over 130 K (ASSUMED,")
    w("     record l8p 12c; no maker's sheet held, E-6): the held current is ended from %s A at the least to %s A at the most" % (fmt(lo, 3), fmt(hi, 3)))
    w("     margins: %s A over the service's true %s A; %s A under the blades' %s A at the band (%s A under %s A at the air)" % (
        fmt(lo - SERVICE_TRUE), fmt(SERVICE_TRUE), fmt(O.BLADE_BAND - hi), fmt(O.BLADE_BAND), fmt(W["I_rr_air"] - hi), fmt(W["I_rr_air"])))
    w("     robustness: the window stays inside both while R10 reads within %s %% to +%s %% (the record assumes +-%s %%)" % (
        fmt(100 * R["r10_room"][0], 1), fmt(100 * R["r10_room"][1], 1), fmt(100 * R["r10_assumed"], 2)))
    w("     OCH_A in the service: %s V at 10 A, %s V at 18 A, %s V at the true %s A: under the least %s V" % (
        fmt(R["out_10"], 3), fmt(R["out_18"], 3), fmt(R["out_service"], 3), fmt(SERVICE_TRUE), fmt(O.VITP[0], 3)))
    w("   4b. THE DELAYS (TI's Equations 5 and 6, C0G at 5 %%; the no-capacitor least not printed, taken 0): the trip's sense delay %s to %s ms," % (
        fmt(R["tcts1"][0] * 1e3, 3), fmt(R["tcts1"][1] * 1e3, 3)))
    w("     longer than E-10's %s ms excursions (record l9stk 15.7: the key-down current's excursions above %s A each under it), so the trip," % (
        fmt(R["e10"] * 1e3, 3), fmt(R["LIM"][0])))
    w("     whose least is over %s A, is never more sensitive than the breaker's least unit; the arming's delay after PGD falls %s to %s ms" % (
        fmt(R["LIM"][0]), fmt(R["tcts2"][0] * 1e3, 2), fmt(R["tcts2"][1] * 1e3, 2)))
    w("   4c. THE CROWBAR INTO THE -1'S LATCH: R140 %s Ohm and Q111; its own current %s A at %s V, %s A at %s V, %s A at the %s V clamp," % (
        fmt(R140, 2), fmt(R["ic_least"], 1), fmt(PACK_LEAST, 1), fmt(R["ic_16"], 1), fmt(PACK_MOST, 1), fmt(R["ic_clamp"], 1), fmt(CLAMP, 1)))
    w("     each over the breaker's most limit %s A WHATEVER THE LOAD: U101 enters its current limit (its circuit breaker from %s A) and the" % (
        fmt(R["LIM"][2]), fmt(R["CB"][0])))
    w("     fault timer latches the -1 off, clearing %s ms at most from the limit's onset plus tCL (%s us typical, no maximum: RECORD, l9stk" % (
        fmt(R["CLEAR"] * 1e3, 3), fmt(R["TCL_TYP"] * 1e6, 0)))
    w("     prot 3): the row 'an overload over the unit's limit' (%s W for %s ms against %s W derated: %s) and, from %s A, the hot-short" % (
        fmt(R["PULSE"][0]), fmt(R["PULSE"][1], 3), fmt(R["PULSE"][2], 1), fmt(R["PULSE"][3]), fmt(R["CB"][0])))
    w("     row's release in 16.5 us; the crowbar's peak with the most limit's load %s A at %s V, %s A at the clamp, under the %s A where VIN to" % (
        fmt(R["peak_16"], 1), fmt(PACK_MOST, 1), fmt(R["peak_clamp"], 1), fmt(R["VSNS_I"], 1)))
    w("     SENSE passes its 0.3 V: no row of record l9stk 15.6 is newly reached; ONCE per recovery (redocking, an input's return, the guard's")
    w("     cycle: the -1's own); no retry train")
    w("     the gate: Q111's Qg(4.5 V) 75 nC at most through R142 from BRK_VIN at %s V: %s us; the event from the held current's onset at most" % (
        fmt(PACK_LEAST, 1), fmt(R["t_gate"] * 1e6, 1)))
    w("       %s ms (the trip's delay, the gate, the clearing) plus tCL; PGD falls only when VDS passes %s to %s V (RECORD), and the arming's" % (
        fmt(R["t_event"] * 1e3, 3), fmt(R["PGD_VDS"][0], 2), fmt(R["PGD_VDS"][1], 2)))
    w("       least delay after it, %s ms, leaves %s ms for tCL past the gate and the clearing: the crowbar stays until the latch" % (
        fmt(R["tcts2"][0] * 1e3, 2), fmt(R["arm_margin"] * 1e3, 2)))
    w("     R140's single pulse (INFERRED): PACK_P under the limit at most %s V (the most limit through R140 alone), %s W for %s ms plus 50 us" % (
        fmt(R["vlim"], 2), fmt(R["p_lim"], 0), fmt(R["CLEAR"] * 1e3, 3)))
    w("       of tCL: %s J; the kit's %s uF on PACK_P from %s V: %s J; the release spike at the clamp: under 0.003 J; at most %s J in all:" % (
        fmt(R["e_lim"], 3), fmt(593, 0), fmt(R["vlim"], 2), fmt(R["e_cap"], 3), fmt(R["e_r140"], 2)))
    w("       a 2512 part whose maker prints a single pulse of at least that in 1.4 ms (Layer 6; CONDITIONAL, E-6b)")
    w("     Q111 (CSD18510Q5B, PRINTED): IDM 400 A against %s A; VDS 40 V against PACK_P's %s V clamp; VGS 20 V against D105's 12.7 V" % (
        fmt(R["peak_clamp"], 1), fmt(CLAMP, 1)))
    w("   4d. THE ARMING AND THE GATE DRIVE (PRINTED limits; leakages ASSUMED to double every 10 K at the record's %s C site)" % fmt(SITE))
    w("     Q110 (AO3401A) driven at VGS -%s V at %s V to -%s V at the clamp (R136 over R137), against its +-12 V and its -2.5 V RDS(on) row" % (
        fmt(R["vgs110"][0], 2), fmt(PACK_LEAST, 1), fmt(R["vgs110"][1], 2)))
    w("     Q110 held off: RESET1's 300 nA and Q112's off leakage %s uA through R136: %s V, under its least threshold %s V" % (
        fmt(R["leak_n"] * 1e6, 2), fmt(R["v_off110"], 3), fmt(R["vth_p"], 1)))
    w("     the crowbar held off: Q110's off leakage %s uA (5 uA at 55 C PRINTED) through R138: %s V (%s V at a 101 C site), under Q111's least" % (
        fmt(R["leak_p"] * 1e6, 1), fmt(R["v_cg_off"], 3), fmt(R["v_cg_off101"], 3)))
    w("       threshold %s V (25 C row; the threshold falls with temperature, TYPICAL Figure 6: a layout condition keeps both off the pad)" % fmt(R["vth_csd"], 1))
    w("     U107's RESET1 sinks at most %s mA and RESET2 %s mA (TI recommends 5 mA); U107's VDD and SENSE at most %s V against 65 V;" % (
        fmt(R["ireset1"] * 1e3, 3), fmt(R["ireset2"] * 1e3, 3), fmt(CLAMP, 1)))
    w("       Q112's gate at most %s V against 20 V; OCH_CG under D105's %s V; R142 and D105 carry at most %s mA for the event" % (
        fmt(R["vgs112"], 1), fmt(R["vcg"], 1), fmt(R["iz"] * 1e3, 1)))
    w("   4e. POWER-UP, THE START AND A LATCHED BREAKER: U107 holds RESET1 and RESET2 asserted for tSD (2 ms at most) and RESET2 while PGD is")
    w("     low, so Q112 is off and the crowbar disarmed whenever the breaker is not running: at a gauge's wake, at a docking (the RC hold's")
    w("     0.110 s and the start), during a start (PGD low while VDS is high) and once latched; the trip touches neither the enable loop nor")
    w("     UVLO (check_l8p_och's APART): L4-E11 20c's window, its readings and the RC hold's 0.110 to 0.907 s are unchanged")
    w("   4f. THE STANDING CURRENT from BRK_VIN: U106 %s uA, U107 %s uA, R139 with R141 %s uA at %s V (PRINTED maxima): beside the detector's" % (
        fmt(R["stand"][0] * 1e6, 0), fmt(R["stand"][1] * 1e6, 1), fmt(R["stand"][2] * 1e6, 1), fmt(PACK_MOST, 1)))
    w("     0.47 mA (record l8p round 3), a standby load on the pack for the battery stream")
    w("   4g. ITS OWN SINGLE FAILURES (INFERRED from the circuit as drawn):")
    for a, b in FAILS:
        w("     %-52s %s" % (a, b))
    w("     so a latent first failure returns the design to round 10's rows at %s A held (the blades at %s %% of their rerated current, no part" % (
        fmt(I), fmt(100 * I / W["I_rr_air"], 1)))
    w("       the guard protects exposed: M-A holds the FETs at %s A); no automatic diagnostic is drawn: E-12f at commissioning and at each" % fmt(I))
    w("       service, and an automatic test is REMAINING ENGINEERING with HO-A's pattern")
    w("")
    w("5. THE DRAFT COMPOSED IN L4-E9'S ORDER (board P; INFERRED from the regenerated netlist)")
    for name, r in K["steps"]:
        w("   %-58s %s" % (name, r))
    w("   board P regenerated: %d parts; netlist sha256/16 %s" % (K["parts"], K["net_sha"]))
    w("   check_l8p_netlist.py on it: %s" % "; ".join(l.strip() for l in K["l8p_lines"]))
    w("   check_l8p_och.py on it: OCH %s%s; the window from the drawn values %s to %s A" % (
        K["och"][0], (": " + "; ".join(K["och"][1])) if K["och"][1] else "", fmt(K["win_drawn"][0], 3), fmt(K["win_drawn"][1], 3)))
    w("   the mutations, each read by check_l8p_och.py:")
    for name, v, why in K["muts"]:
        w("     %-100s OCH %s: %s" % (name + ",", v, why[:90]))
    w("   the draft refuses a board P without the breaker and the ideal diode (exit %d: %s), a second application (exit %d: %s) and the" % (
        K["refusals"][0][0], K["refusals"][0][1][:70], K["refusals"][1][0], K["refusals"][1][1][:60]))
    w("     repository's own generator while unreleased (exit %d: %s)" % (K["refusals"][2][0], K["refusals"][2][1][:80]))
    w("")
    w("6. L4A-67: C-PROT REV 1 FOR THE GUARD ON THE CORRECTED CIRCUIT (the delta of round 9, M-A of round 10, the trip of this round)")
    w("   the states: (i) the trip intact: no current is HELD over %s A; above it one event per recovery as 4c; (ii) the trip latently failed" % fmt(hi))
    w("     (4g): round 10's rows at the breaker's held %s A. Each row: below the trip (held) | above the trip (the event) | verdict" % fmt(I))
    for row in R["rows"]:
        w("   %s" % row[0])
        for line in row[1:]:
            w("       %s" % line)
    w("   the guard's own claims (rounds 8 and 9, 10c): unchanged by the trip, which touches neither its pour nor the loop; with the trip")
    w("     intact the hottest battery FET reads at most %s C at E-1's bar and %s C at the design target held (the guard: no trip under" % (
        fmt(R["tj_trip_bar"], 1), fmt(R["tj_trip_tgt"], 1)))
    w("     127.8 C at its die, surely tripped from 132.2 C); a held overload over the window is ended by the trip within %s ms plus tCL," % fmt(R["t_event"] * 1e3, 2))
    w("     long before the pour's own time; the guard keeps its own case (the pour's temperature at any current, a pour worse than the bar")
    w("     included), and its latent failures (L8P-R9-F1) expose no part at the held currents M-A holds")
    w("")
    w("7. L4A-68: THE GUARD'S ALLOWANCE FOR ITS CONSUMERS (RECORD, record l8p 10c; the texts the apply scripts write)")
    w("   the draw on DOCK_EN_OUT at printed maxima, the off leakage at the doubling: cold %s uA (%s uA with the clamp's gates doubled), tripped" % (
        fmt(R["DRAW"][0]), fmt(R["DRAW"][1])))
    w("     %s uA (%s uA with one of path 1's pull-up resistors shorted): the allowances %s uA cold and %s uA tripped (10c)" % (
        fmt(R["DRAW"][2]), fmt(R["DRAW"][3]), fmt(R["ALLOW"][0], 0), fmt(R["ALLOW"][1], 0)))
    w("   the capacitance on DOCK_EN_OUT: C261 and C268, 330 nF each, and U61's 4.7 uF C262 behind its input in dropout (L4-E11 28d)")
    w("   path 2's load is on VBAT, not on the loop: U62 16 uA and U63 2.25 uA at their printed table maxima (10c)")
    w("   the round 11 trip adds nothing on DOCK_EN_OUT or DOCK_EN_RET (check_l8p_och's APART); the consumers' texts:")
    w("     Layer 5 (IF-AE-DOCK, apply_pcb_interfaces_guard_allowance.py): '%s'" % LAYER5_TEXT)
    w("     record l9stk 15.9 (apply_l9stk_guard_allowance.py): '%s'" % L9STK_TEXT)
    w("   the replay of L4-E11's 20f, 22 and 28 at these figures: record l4e11's round 19 (l4e11_rowc.py)")
    w("")
    w("8. VERDICTS")
    w("   L8P-R10-F1: CORRECTED IN DRAFT by (B), SESSION L8P-R11-D1: composed in L4-E9's order, read DRAWN, %d of %d mutations FAIL; electrical" % (
        sum(1 for _n, v, _w in K["muts"] if v == "FAIL"), len(K["muts"])))
    w("     acceptance on printed figures: no current held over %s A, %s %% of the blades' rerated current at the band, the service untouched;" % (
        fmt(hi), fmt(100 * hi / O.BLADE_BAND, 1)))
    w("     CONDITIONAL on E-6 (R10's sheet within -7.3 to +8.3 %), E-6b (R140's printed pulse), E-12f, and the latent-failure residual of 4g;")
    w("     UNVERIFIED until the focused check (L4A-69); the approaches (A) NOT SUPPORTED and (C) NOT SELECTED on printed figures")
    w("   L4A-67: C-PROT rev 1 for the guard on the corrected circuit: every series part within its printed limits below and above the trip")
    w("     where a printed figure exists; NOT SHOWN, each missing figure named and CONDITIONAL: board P's switches' hot RDS(on) (E-8, E-11),")
    w("     R10, R101, R102 and R140 (E-6, E-6b), the 12 AWG wires (a maker's ampacity at 76.25 C with its insulation class), the dock pins'")
    w("     split (E-4); the battery FETs at most 150 C on the held state, CONDITIONAL on E-05, E11-29 and E11-36 (round 10); L8P-R9-F1's")
    w("     latent pattern now carries the trip too (REMAINING ENGINEERING)")
    w("   L4A-68: the allowance stated for its consumers (section 7, two apply scripts, NOT APPLIED); the replay is record l4e11's round 19")
    w("")
    w("9. PREDICATES")
    for name, ok in R["preds"]:
        w("   %-118s %s" % (name, "yes" if ok else "NO"))
    return "\n".join(o) + "\n"


FAILS = (
    ("U106 or U107 dead, Rin open, RESET1 stuck high", "the trip lost, LATENT: round 10's rows (the blades over by 0.83 A)"),
    ("Q112, Q110, R142, Q111 or R140 open; D105 short", "the crowbar lost, LATENT: as above"),
    ("U106's output stuck high, Rf open", "a trip at every running start: the -1 latches, the kit dark (found)"),
    ("Q110 or Q111 shorted", "the crowbar at every start: the -1 latches in its start (found)"),
    ("Q112 shorted, RESET2 stuck high", "the arming lost: a crowbar for tSD at a gauge's wake on a live PACK_P"),
    ("RESET2 stuck low, C120 shorted", "the crowbar disarmed, LATENT: as the first row"),
    ("C119 open", "the sense delay 17 us at most: a trip on an excursion E-10 allows (found)"),
)

LAYER5_TEXT = ("DOCK_EN_OUT on board A carries the thermal guard's draw: at most 40 uA with the guard cold and 50 uA tripped (record l8p 10c: "
               "printed maxima, the off leakage at the doubling, the worst single fault), C261 and C268 330 nF each and U61's 4.7 uF "
               "behind them; path 2's regulator and switch load VBAT, not the loop; DOCK_EN_RET may be held at ground by board A's Q60, "
               "Q44 and board P's Q107 with Q108, and DOCK_EN_OUT by board A's Q61 (path 2 tripped); DRAFTED (R-222, R-244), applied with "
               "record l8p's drafts; replaces round 8's 30 uA and 1 uF")
L9STK_TEXT = ("ROUND 11 OF RECORD l8p (7 October 2026): with record l8p's fail-safe delta (two guard paths, apply_gen_sch_a_thgfs.py) the guard's "
              "draw on DOCK_EN_OUT is at most 40 uA cold and 50 uA tripped (record l8p 10c, printed maxima with the off leakage at the "
              "doubling), in place of the 30 uA this round allows round 8's single path; its input capacitance is C261 and C268, 330 nF each")


def rows(R):
    """C-PROT rev 1, part by part, on the corrected circuit."""
    W = R["W"]
    I, T_AIR = W["I"], W["T_AIR"]
    lo, hi = R["win"]
    k = (hi / I) ** 2
    tj_bar = T_AIR + k * (W["TJ_bar"] - T_AIR)
    tj_tgt = T_AIR + k * (W["TJ_tgt"] - T_AIR)
    R["tj_trip_bar"], R["tj_trip_tgt"] = tj_bar, tj_tgt
    # R17 on ROHM's lower printed line at the trip's most (round 10's function, the TCR above 60 C ASSUMED)
    p17 = lambda tk: hi ** 2 * W["R17_MAX"] * (1 + 50e-6 * max(0.0, tk - 60.0))
    allowed = lambda tk: min(7.0 if tk <= 70 else 7.0 * (170 - tk) / 100.0, 5.0 if tk <= 110 else 5.0 * (170 - tk) / 60.0)
    a, b = 25.0, 170.0
    for _ in range(80):
        m_ = (a + b) / 2
        a, b = (m_, b) if p17(m_) <= allowed(m_) else (a, m_)
    share = 9.0 / hi
    pin_ratio = (1 - share) / (3 * share)
    xt_rise = 85.0 * (hi / 35.0) ** 2
    q1k = (150.0 - T_AIR) / (50.0 * 2 * hi ** 2 * W["q1_r"])
    q101k = (150.0 - T_AIR) / (50.0 * 2 * (hi / 2) ** 2 * W["q101_r"])
    R["rows_num"] = dict(tk=a, pin=pin_ratio, xt=T_AIR + xt_rise, q1k=q1k, q101k=q101k, cell=8.0 * 0.997 * hi / I)
    ev = "the event: at most %s A for %s ms plus tCL, the crowbar's peak %s A for 16.5 us at most" % (
        fmt(I), fmt(R["t_event"] * 1e3, 2), fmt(R["peak_clamp"], 1))
    return [
        ["Q39, Q40, Q42 (BUK6Y10-30P; round 10's 15a, PRINTED device maxima)",
         "held: at most %s A: the hottest junction %s C at E-1's bar, %s C at the design target (trip intact); %s C at the bar with the" % (fmt(hi), fmt(tj_bar, 1), fmt(tj_tgt, 1), fmt(W["TJ_bar"], 2)),
         "  trip failed (round 10) | %s: at most the held %s A state by superposition (round 10's 15e) | WITHIN 150 C, CONDITIONAL on" % (ev, fmt(I)),
         "  E-05, E11-29, E11-36"],
        ["R17 (ROHM GMR100HJAAFD5L00, PRINTED derating)",
         "held: %s W at %s A on its printed maximum; its terminals admitted to %s C on the lower line (round 10: 128.5 C at %s A) | the" % (fmt(p17(a), 3), fmt(hi), fmt(a, 1), fmt(I)),
         "  event: within its held state's energy for 2.2 ms; the 16.5 us spike inside the hot-short row the record carries | WITHIN its",
         "  derating, CONDITIONAL on the terminal reading (E11-29's coupon)"],
        ["the pour and the vias (MODEL; record l9stk's conductor model)",
         "held: the band %s K over the air at %s A (round 10: 9.16 K at %s A) | the event: as the held state | WITHIN on the model; the" % (fmt(W["BAND"] * k, 2), fmt(hi), fmt(I)),
         "  laminate's limit NOT HELD (L9-STACKUPS 14.3)"],
        ["the three 25 A MINI blades (Littelfuse 297, PRINTED rerating READ)",
         "held: at most %s A, %s %% of the rerated %s A at the air, %s %% of %s A at the band (trip intact); round 10's %s %% with the trip" % (
             fmt(hi), fmt(100 * hi / W["I_rr_air"], 1), fmt(W["I_rr_air"]), fmt(100 * hi / W["I_rr_band"], 1), fmt(W["I_rr_band"]), fmt(100 * I / W["I_rr_air"], 1)),
         "  failed | the event: one excursion per recovery of at most 2.2 ms at 103.6 %% of the rerated current and 16.5 us at %s A, inside" % fmt(R["peak_clamp"], 1),
         "  the printed rows' least opening times (135 %: 0.75 s; 600 %: 30 ms) | WITHIN with the trip intact (L8P-R10-F1 CORRECTED IN DRAFT);",
         "  OVER by 0.83 A on the trip's latent failure (4g)"],
        ["the Keystone 3568 holders (M65 p.42, PRINTED UL 30 A, -50 to +145 C)",
         "held: %s %% of 30 A | the event: as the blades | WITHIN on current" % fmt(100 * hi / 30.0, 1)],
        ["the dock pins J_CP1 to 4, J_CN1 to 4 (Mill-Max 0858, 9 A continuous PRINTED, no minimum resistance)",
         "held: %s A a pin evenly; no pin over 9 A needs the split ratio at least %s (round 10: 0.553 at %s A) | the event: at most %s A a" % (
             fmt(hi / 4.0), fmt(pin_ratio, 3), fmt(I), fmt(R["peak_clamp"] / 4.0, 1)),
         "  pin for 16.5 us, inside the hot-short row | WITHIN evenly, CONDITIONAL on E-4"],
        ["the XT60 J_BATT (Amass, PRINTED 30 A; 35 A at a rise under 85 K)",
         "held: %s %% of 30 A; the rise scaled from the 35 A row %s K (INFERRED), %s C, %s K under its 120 C | the event: as the blades |" % (
             fmt(100 * hi / 30.0, 1), fmt(xt_rise, 1), fmt(T_AIR + xt_rise, 1), fmt(120.0 - T_AIR - xt_rise, 1)),
         "  WITHIN on current, its temperature INFERRED"],
        ["the 12 AWG wires (W_P, W_N, P_CP)",
         "no maker's sheet held: MISSING the wire maker's ampacity at a 76.25 C ambient for its insulation class (Layer 6, the harness",
         "  supplier) | NOT SHOWN, CONDITIONAL (the held current now at most %s A)" % fmt(hi)],
        ["Q1, Q2, Q109 (CSD17570Q5B, PRINTED 0.69 mOhm at 25 C only; hot TYPICAL)",
         "held: the 150 C junction admits a hot factor up to %s with both losses through the common pad at %s A (round 10: 1.866 at %s A)," % (fmt(q1k, 3), fmt(hi), fmt(I)),
         "  against the typical 1.8 | the event: the held state's bound | NOT SHOWN on printed maxima: MISSING TI's maximum RDS(on) at",
         "  125 or 150 C, or E-8's joint-case reading on board P's first specimen (TJ under 150 C at the held current from 76.25 C); CONDITIONAL"],
        ["Q101, Q102 (CSD18510Q5B, the breaker's FETs)",
         "held: a hot factor up to %s admitted to 150 C (round 10: 5.37) | the event: l9stk 15.6's 'over the unit's limit' row, 0.57 of" % fmt(q101k, 2),
         "  the derated SOA (RECORD) | NOT SHOWN on printed maxima (E-11, the installed path at most 52.5 C/W, and the hot RDS(on)); the",
         "  event's SOA reading CONDITIONAL on E-2 and E-3 (record l9stk)"],
        ["Q111 (CSD18510Q5B, the crowbar; this round)",
         "held: off (IDSS 1 uA at 25 C PRINTED) | the event: %s A at most against IDM 400 A PRINTED, VDS a few hundred mV | WITHIN" % fmt(R["peak_clamp"], 1)],
        ["R10 (2 mOhm 2512 2 W, the gauge's sense and the trip's)",
         "held: %s W at %s A | the event: the hot-short row's 16.5 us | NOT SHOWN: MISSING its maker's sheet (tolerance, temperature" % (fmt(hi ** 2 * 2e-3, 2), fmt(hi)),
         "  coefficient, derating at the band; E-6); the trip's window holds for R10 within -7.3 to +8.3 %"],
        ["R101, R102 (the breaker's sense pair; no part chosen)",
         "held: %s and %s W at %s A | NOT SHOWN: MISSING the parts (Layer 6: 2 W each at the band's temperature, 1 %%, at most 50 ppm/K; E-6)" % (
             fmt(W["SNS_REC"][0] * k, 2), fmt(W["SNS_REC"][1] * k, 2), fmt(hi))],
        ["R140 (the crowbar's resistor; this round)",
         "held: no current | the event: at most %s J in 1.4 ms | NOT SHOWN: MISSING a part whose maker prints that single pulse (E-6b)" % fmt(R["e_r140"], 2)],
        ["F2 (Eaton SCF9550, 30 A, -20 to +60 C PRINTED)",
         "held: %s %% of 30 A; its printed range ends 16.25 K under the 76.25 C air at any current: the pack's thermal environment (record" % fmt(100 * hi / 30.0, 1),
         "  l4e10 section 9), not a held-current row"],
        ["the cells",
         "held: E-5's split at %s A (round 10: 0.997 of 8 A at %s A, here %s of 8 A per cell evenly, INFERRED) | the battery stream's" % (
             fmt(hi), fmt(I), fmt(hi / I * 0.997, 3)),
         "  and U-01's (outside M-A)"],
    ]


def predicates(R, K):
    W = R["W"]
    lo, hi = R["win"]
    return [
        ("round 10's finding reproduces: the blades over their rerated current at the held breaker limit", W["over_air"] > 0 and W["over_band"] > 0),
        ("a 25 A element would need a rerating over the MINI 297's printed one at the air", R["need_f"] > R["f_air"]),
        ("a 30 A blade's 60 A row puts the copper over both pinned band limits (approach A refused)", R["cu60"] > max(R["band_pinned"])),
        ("the LM5066I's printed spread fails the band reading at the record's least limit (approach C)", R["c_most_1832"] > W["I_rr_band"]),
        ("the LM5066I's printed spread fails the air reading at the service's true current (approach C)", R["c_most_1880"] > W["I_rr_air"]),
        ("the trip's least is over the service's true current (C4)", lo > SERVICE_TRUE),
        ("the trip's most is under the blades' rerated current at the band", hi < W["I_rr_band"]),
        ("the trip's most is under the blades' rerated current at the air", hi < W["I_rr_air"]),
        ("the window from the drawn netlist equals the computed one", abs(K["win_drawn"][0] - lo) < 1e-6 and abs(K["win_drawn"][1] - hi) < 1e-6),
        ("the window tolerates R10 over the record's assumed error", R["r10_room"][0] < -R["r10_assumed"] and R["r10_room"][1] > R["r10_assumed"]),
        ("the trip's least sense delay is over E-10's excursion bound", R["tcts1"][0] > R["e10"]),
        ("the crowbar's own current at the pack's least exceeds the breaker's most limit", R["ic_least"] > R["LIM"][2]),
        ("the crowbar's peak stays under the current where VIN to SENSE passes 0.3 V", R["peak_clamp"] < R["VSNS_I"]),
        ("the arming's least delay covers the gate, the clearing and some tCL", R["arm_margin"] > 1e-3),
        ("Q110's VGS at the clamp is within its 12 V", R["vgs110"][1] < 12.0),
        ("Q110 stays off under the leakages at the site", R["v_off110"] < R["vth_p"]),
        ("the crowbar stays off under Q110's leakage at the site", R["v_cg_off"] < R["vth_csd"]),
        ("U107's RESET currents are within TI's recommended 5 mA", max(R["ireset1"], R["ireset2"]) < 5e-3),
        ("the crowbar's peak is within Q111's printed IDM", R["peak_clamp"] < 400.0),
        ("the composition ran in L4-E9's order and board P reads its earlier groups DRAWN", K["l8p"] == "DRAWN"),
        ("check_l8p_och reads the composed board P DRAWN", K["och"][0] == "DRAWN"),
        ("every mutation FAILS", all(v == "FAIL" for _n, v, _w in K["muts"])),
        ("the draft refuses without its predecessors, twice, and on the tree's generator", all(rc == 3 for rc, _m in K["refusals"])),
        ("the battery FETs stay at or under 150 C with the trip intact and failed", R["tj_trip_bar"] <= 150.0 + 1e-9 and W["TJ_bar"] <= 150.0 + 1e-9),
        ("the allowance read from 10c is 40 uA cold and 50 uA tripped", R["ALLOW"] == (40.0, 50.0)),
    ]


def main():
    try:
        R = compute()
        K = compose()
        R["rows"] = rows(R)
        R["preds"] = predicates(R, K)
    except (Refused, RC.Refused) as e:
        sys.stderr.write("l8p_cprot: REFUSED: %s\n" % e)
        return 3
    sys.stdout.write(render(R, K))
    return 0


if __name__ == "__main__":
    sys.exit(main())
