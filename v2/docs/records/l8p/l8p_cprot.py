#!/usr/bin/env python3
"""l8p_cprot.py: record l8p, round 11 (Layer 4 AI-scope register row (c), tasks L4A-67 and L4A-68; MESHSAT-1357, 7 October 2026).

L8P-R10-F1 (record l8p round 10, L8P-BREAKER.md 15c): at the breaker's held 23.93 A from the 76.25 C inside air the three 25 A MINI
blades carry 103.6 % of their printed rerated current. This round treats it as an unresolved design choice (constitution section 4:
at most three materially different approaches, none lowering a protection, the 18 A service or a printed rating's margin), selects
one as SESSION with its end condition, and draws it (apply_gen_sch_p_ocheld.py, release-guarded, composed with board P's drafts,
read by check_l8p_ocn and mutated). L4A-67: C-PROT rev 1 re-evaluated on the corrected circuit, every series part below and above
the trip on its printed limits or its missing figure named. L4A-68: the guard's allowance (record l8p 10c) printed for its consumers;
the replay of L4-E11's 20f, 22 and 28 is record l4e11's l4e11_rowc.py.

ROUND 12 (W149, 7 October 2026, after the focused check L4A-69, W147's F1 to F12): 4c' bounds a source's share of the crowbar's
current (the path that holds VSYS is the charger, not board E's entry) and restates R140's single pulse (E-6b) and Q111's row; 4i
states the BRK_VIN range the event can happen at, the band under 9.43 V where the crowbar's own current can hold the trip with the
-1 out of its limit, and the on-time bound drawn against it (channel 2 also disarms once the trip has been asserted: D106, R143,
C120 at 22 nF); check_l8p_och.py reads R10, R135, C117, C119 and C120 into the window and the delays, with the new mutations; 4g
carries a shorted crowbar with a source (L8P-R12-F1) and 4h the RC hold's stretch; the verdicts state L4A-67's latent-failure
clause NOT MET and name E-10 among L8P-R11-D1's conditions. The constitution was read and applied (sections 3 to 5 and 8).

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
    "e11": "v2/docs/records/l4e11/l4e11_power.out",
    "c4": "v2/docs/records/l8p/l8p_c4.out",
    "prot": "v2/docs/records/l9stk/l9stk_protection.out",
    "stk": "v2/docs/records/l9stk/L9-STACKUPS.md",
    "draft": "v2/docs/records/l8p/apply_gen_sch_p_ocheld.py",
    "brk": "v2/docs/records/l8p/apply_gen_sch_p_breaker.py",
    "dio": "v2/docs/records/l8p/apply_gen_sch_p_idealdiode.py",
    "och": "v2/docs/records/l8p/check_l8p_och.py",
    "gen_p": "v2/ecad/tools/gen_sch_p.py",
    "l9g": "v2/docs/records/l8p/inputs/l9stk-section15.9-bb6d2c8f.md",
    "a5": "v2/docs/records/l8p/apply_pcb_interfaces_guard_allowance.py",
    "a9": "v2/docs/records/l8p/apply_l9stk_guard_allowance.py",
    "arch": "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md",
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
    "bq25730": ("v2/vendor/ti/held/ti-bq25730-sluse65a.pdf", "TI BQ25730, SLUSE65A (held back, record l4e11's fetch_held_back.py)"),
    "bat46w": ("v2/vendor/diodes/diodes-bat46w.pdf", "Diodes BAT46W, DS30044 Rev. 20-2"),
}
PIN = {"lm5066i": "a759a5d04fe5b81577af575153fd528f0f03f147c892040eac6c51e400693628",
       "bq25730": "e41ef289ce1de377d7b92bce609177d924e149099d9c4424d88f6b21ad57153f"}

# ---------------------------------------------------------------- the trip as drawn (read back from the draft below)
G_RIN, G_RF = 1.00e3, 19.3e3
C_CTS1, C_CTS2, C_TOL = 4.7e-9, 22e-9, 0.05           # C0G, 5 % (C120 47 nF in round 11, 22 nF since round 12: the on-time bound)
R136, R137, R138, R139, R141, R142, R140 = 47e3, 100e3, 4.7e3, 1e6, 1e6, 1e3, 0.39
R143 = 2.2e6                                           # round 12: BRK_PGD to OCH_S2
CISS_Q110_TYP, CISS_Q111_MAX = 645e-12, 11.4e-9        # AO3401A Ciss TYPICAL only (no maximum printed); CSD18510Q5B Ciss 11400 pF MAX
Q110_CISS_FACTOR = 2.0                                 # ASSUMED: twice the AO3401A's typical Ciss bounds its gate charge (no maximum printed)
TCL_RECORD = 50e-6                                     # tCL taken 50 us: 45 us TYPICAL, no maximum printed (RECORD, l9stk prot 3; F12)
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
    e11 = flat(read(RECS["e11"]))
    m = need(e11, r"overcurrent ([\d.]+) / ([\d.]+) / ([\d.]+) A \(the printed row, the 0\.1 % parts.*?short circuit ([\d.]+) / ([\d.]+) / ([\d.]+) A",
             "the entry's overcurrent and short-circuit rows (record l4e11 3c)")
    ENTRY = (float(m.group(1)), float(m.group(3)), float(m.group(4)), float(m.group(6)))
    R.update(LIM=LIM, VCL=VCL, CB=CB, CLEAR=CLEAR, TCL_TYP=TCL_TYP, PULSE=PULSE, VSNS_I=VSNS_I, PGD_VDS=PGD_VDS, CU50=CU50, RS=RS,
             DRAW=DRAW, ALLOW=ALLOW, ENTRY=ENTRY)

    # 2A. a fuse or a holder arrangement (Littelfuse's printed rerating; record l9stk's copper)
    need_f = I / 25.0
    cu60 = T_AIR + (CU50 - T_AIR) * (60.0 / 50.0) ** 2           # the copper's steady rise at the 30 A blade's 200 % (I^2, the record's own scaling)
    R.update(need_f=need_f, f_air=W["f_air"], f_band=W["f_band"], b30=W["blade30_rr"], b30_135=W["blade30_135"], cu60=cu60,
             band_pinned=(125.0, 120.0))

    # 2C. a controller with a tighter printed limit spread (TI LM5066I)
    t = flat(pdftext("lm5066i"))
    m = need(t, r"Current limit threshold voltage CL = VDD ([\d.]+) ([\d.]+) ([\d.]+) VCL mV \(VVIN_K \u2013 VSENSE\) CL = GND ([\d.]+) ([\d.]+) ([\d.]+)",
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
    for pat in (r'r\("R132", "1\.00k 0\.1% 25ppm', r'r\("R133", "19\.3k 0\.1% 25ppm', r'c\("C119", "4\.7n 50V C0G 5%', r'c\("C120", "22n 50V C0G 5%', r'r\("R143", "2\.2M 1%", "BRK_PGD", "OCH_S2"\)',
                r'part\("D106", "Device", "D_Schottky", "BAT46W-7-F',
                r'r\("R136", "47k"', r'r\("R137", "100k"', r'r\("R142", "1k", "OCH_GD", "OCH_CG"\); r\("R138", "4\.7k"',
                r'r\("R140", "0\.39R 1% ', r'r\("R139", "1M", "BRK_VIN", "OCH_EG"\); r\("R141", "1M", "OCH_EG", "PACK_N"\)'):
        need(dr, pat, "the draft's value %s" % pat[3:9])
    t37 = flat(pdftext("tps37"))
    need(t37, r"VITP \(Overvoltage\) VIT = 800 mV \(3\) 0\.792 0\.800 0\.808 V", "TPS37 VITP at 800 mV")
    need(t37, r"RCTS 88 100 122 Kohms", "TPS37 RCTS")
    need(t37, r"tCTSx \(min\) = -ln \(0\.31\) x RCTSx \(min\) x CCTSx_EXT \(min\)", "TPS37 Equation 5")
    need(t37, r"tCTSx \(max\) = -ln \(0\.25\) x RCTSx \(max\) x CCTSx_EXT \(max\)", "TPS37 Equation 6")
    need(t37, r"VIT = 800 mV CCTS1 = CCTS2 = Open 8 17 [µμ]s", "TPS37 tCTS without a capacitor")
    need(t37, r"tSD Startup Delay \(4\) 2 ms", "TPS37 tSD")
    need(t37, r"tCTR \(CTR1/MR, CTR2/MR\) \(2\) VIT = 800 mV CCTR1 = CCTR2 = Open 40 [\u00b5\u03bc]s", "TPS37 tCTR without a capacitor")
    need(cs_pre := flat(pdftext("csd")), r"Ciss Input capacitance 8770 11400 pF", "CSD18510Q5B Ciss")
    need(t37, r"VRESET = 5\.5 V 300 nA Open-Drain leakage", "TPS37 open-drain leakage")
    need(t37, r"Current IRESET1, IRESET2, IRESET1, IRESET2 0 ±5 mA", "TPS37 recommended RESET current")
    need(t37, r"Voltage VDD 2\.7 65 V", "TPS37 VDD range")
    need(t37, r"ISENSE VIT = 800 mV 100 nA", "TPS37 ISENSE")
    need(t37, r"VIT = 800 mV 1 2\.6 [µμ]A", "TPS37 IDD at 800 mV")
    o = flat(pdftext("opa187"))
    need(o, r"OFFSET VOLTAGE ±1 ±10 [µμ]V VOS Input offset voltage TA = \u201340°C to \+125°C ±0\.001 ±0\.015 [µμ]V/°C", "OPA187 VOS and drift")
    need(o, r"\(V\u2013\) \u2013 0\.1 \(V\+\) \u2013 2 V", "OPA187 VCM")
    need(o, r"IO = 0 mA, TA = \u201340°C to \+125°C 150 [µμ]A", "OPA187 IQ")
    lo, hi = O.window({"comps": {"R132": {"value": "1.00k"}, "R133": {"value": "19.3k"}, "R135": {"value": "1k"},
                                 "R10": {"value": "2m 2512 2W (sense)"}}, "pins": {}, "on": {}})   # the drafted values; section 5 reads the netlist
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
    e_lim = p_lim * (CLEAR + TCL_RECORD)
    c_kit = 593e-6
    e_cap = 0.5 * c_kit * R["vlim"] ** 2
    e_spike = R["peak_clamp"] ** 2 * R140 * 16.5e-6                # round 11's arithmetic: the crowbar's peak with the load's (an overcount)
    R.update(p_lim=p_lim, e_lim=e_lim, e_cap=e_cap, e_spike=e_spike, e_n=e_lim + e_cap + e_spike)
    # the sequence: the trip's sense delay, the gate drive, the -1's clearing; the arming's delay after PGD falls
    t_gate = 75e-9 / ((PACK_LEAST - 4.5) / R142)                  # Qg(4.5 V) 75 nC at most through R142 from BRK_VIN
    R.update(t_gate=t_gate, t_event=tcts1[1] + t_gate + CLEAR, arm_margin=tcts2[0] - (t_gate + CLEAR))
    # the crowbar's turn-off once RESET1 releases or RESET2 disarms (round 12 adds Q110's own turn-off, which round 11 left out): tCTR1
    # without a capacitor at most 40 us (PRINTED); Q110's gate pulled up through R136 (+1 %) from its drive to 0.5 V with twice its
    # TYPICAL Ciss (ASSUMED: no maximum printed); Q111's gate through R138 (+1 %) for five time constants of its PRINTED 11.4 nF maximum
    t_q110 = max(math.log(v * R136 / (R136 + R137) / 0.5) for v in (PACK_LEAST, PACK_MOST, CLAMP)) * R136 * 1.01 * Q110_CISS_FACTOR * CISS_Q110_TYP
    t_off = 40e-6 + t_q110 + 5 * R138 * 1.01 * CISS_Q111_MAX
    R.update(t_q110=t_q110, t_off=t_off, t_src=R["t_event"] + t_off)
    need(t37, r"VOL \(5\) Low level output voltage 300 mV", "TPS37 VOL")
    need(t37, r"tCTR \(CTR1/MR, CTR2/MR\) \(2\) VIT = 800 mV CCTR1 = CCTR2 = Open 40", "TPS37 tCTR at 800 mV")
    need(flat(pdftext("ao3401a")), r"Ciss Input Capacitance 645 pF", "AO3401A Ciss (TYPICAL only)")

    # 4c'. A SOURCE'S SHARE OF THE CROWBAR'S CURRENT (round 12; the check's F1). The path that holds VSYS (L4-E9's power edges): board
    # E's entry feeds VIN_RAW, board A's front end makes VBUS20 and the charger U3 holds VSYS; board E's thresholds bound VIN_RAW's
    # current two conversions upstream, not the current a source pushes from VSYS through board A's battery FETs into PACK_P
    arch = flat(read(RECS["arch"]))
    need(arch, r"\| P06 \| ENTRY \| VINRAW \| R19, L2 to VIN_RAW \|", "L4-E9's edge P06: the entry feeds VIN_RAW")
    need(arch, r"\| P07 \| VINRAW \| FE \| the dock's pins, U2's input \|", "L4-E9's edge P07: VIN_RAW into the front end")
    need(arch, r"\| P10 \| CHG \| VBAT \| U3's output, VSYS \|", "L4-E9's edge P10: the charger holds VSYS")
    need(arch, r"\| P11 \| VBAT \| PACK \| \(B1\) Q39 and Q40 to CH_BATQ, then R17, A F1, the pack pins, board P \|", "L4-E9's edge P11: VSYS to the pack")
    m = need(e11, r"to ([\d.]+) V \(the pack at ChargeVoltage's ([\d.]+) V plus 150 mV, \+2 %, p\.9\): BOUNDED", "VSYS's most (L4-E11 12c)")
    vsys_max = float(m.group(1))
    m = need(e11, r"into a resistive fault at sqrt\(P x R\): ([\d.]+) V at the breaker's least-limit fault of ([\d.]+) ohm with the front end's "
             r"([\d.]+) W \(its ([\d.]+) A ISNS maximum\)", "the source's settled power into a resistive fault (L4-E11, B-R2's reach)")
    p_src = float(m.group(3))
    inh_v = float(need(e11, r"the inhibit sets only when CELL\+ falls under ([\d.]+) V", "the DD-7 inhibit's CELL+ threshold (L4-E11)").group(1))
    bq = flat(pdftext("bq25730"))
    need(bq, r"Pre-charge current REG0x03/02\(\) = 0x00C0H 384 mA regulation accuracy \u22652S \u201325\.0% 25\.0%", "BQ25730 IPRECHRG_REG_ACC at 384 mA")
    need(bq, r"CONVERTER OVER-CURRENT COMPARATOR \(Q2\) Converter Over- Reg0x32\[5\]=1b 150 mV", "BQ25730 VOCP_lim_Q2 (a TYPICAL only)")
    pre_max = 0.384 * 1.25
    r_lo, r_hi = R140 * 0.99, R140 * 1.01
    # the crowbar conducts until RESET1 releases (after the -1 latches, the cells' current through R10 stops) or RESET2 disarms
    # (round 12): while the -1 conducts, PACK_P is under BRK_VIN; once latched it is at most VSYS. No printed figure bounds the
    # source's current inside the event (the charger's and the front end's regulation loops print no settling time; the charger's
    # cycle-by-cycle comparators print a typical only), so R140's power is bounded on VOLTAGE over the bounded on-time
    p_on, p_after = PACK_MOST ** 2 / r_lo, vsys_max ** 2 / r_lo
    R.update(vsys_max=vsys_max, p_src=p_src, inh_v=inh_v, pre_max=pre_max, p_on=p_on, p_after=p_after,
             v_settled=math.sqrt(p_src * r_hi), i_settled=math.sqrt(p_src / r_hi),
             e_n_src=p_on * (t_gate + CLEAR + TCL_RECORD) + p_after * t_off + e_spike)

    # 4i. THE BRK_VIN RANGE AND THE ON-TIME BOUND (round 12; the check's F2). The -1 runs from 7.6 V (record l8p 12d, C-PROT rev 1;
    # LM5069's PORIT, typical) to the pack's 16.8 V; the crowbar's own current exceeds the most limit only from LIM x R140 (+1 %)
    l69 = flat(pdftext("lm5069"))
    need(l69, r"PORIT VIN increasing 7\.6 8 V", "LM5069 PORIT")
    v_force = R["LIM"][2] * r_hi
    lim, w_lo = R["LIM"][2], R["win"][0]
    # the band where the crowbar's own current lies between the trip's least and a unit's most limit (no source); with a source's
    # settled share on the record's B-R2 basis (p_src into the pack side) the -1 can stay under its limit up to v_band_src; a held
    # overload that persists through the bound needs the source to carry (V / R140 + the window's least - the most limit) x V
    v_band_src = (lim * r_hi + math.sqrt((lim * r_hi) ** 2 + 4 * p_src * r_hi)) / 2
    a_ = 1 / r_hi
    v_resid = (-(w_lo - lim) + math.sqrt((w_lo - lim) ** 2 + 4 * a_ * p_src)) / (2 * a_)
    R.update(v_floor=7.6, v_force=v_force, band=(w_lo * r_lo, v_force), v_band_src=v_band_src, v_resid=v_resid)
    t2 = tcts2
    R.update(t_on_max=t2[1] + t_off, arm_cover=t2[0] - (t_gate + CLEAR))
    p_stall = R["LIM"][2] ** 2 * r_hi                                  # the crowbar's own current under the most limit, no source
    R.update(p_stall=p_stall, e_s=p_stall * (t2[1] + t_off), e_w=p_on * t2[1] + p_after * t_off + e_spike,
             p_peak=CLAMP ** 2 / r_lo, i_q111_src=vsys_max / r_lo,
             p_q111_off=vsys_max ** 2 / (4 * r_lo), p_q111_off_settled=p_src * r_hi / (4 * r_lo),
             p_q111_off_nosrc=v_force ** 2 / (4 * r_lo), t_q111_off=5 * R138 * 1.01 * CISS_Q111_MAX)
    R["e_r140"] = max(R["e_n"], R["e_s"], R["e_w"])
    need(dr, r"single pulse of at least %s J in %s ms with %s kW for 16\.5 us" % (re.escape(fmt(R["e_r140"], 2)), re.escape(fmt(R["t_on_max"] * 1e3, 2)),
         re.escape(fmt(R["p_peak"] / 1e3, 2))), "the draft's R140 stating this round's pulse")
    # D106's low level and R143's levels (check_l8p_och's own arithmetic on the drawn values)
    bt = flat(pdftext("bat46w"))
    need(bt, r"0\.25 IF = 0\.1mA Forward Voltage VF", "BAT46W VF at 0.1 mA")
    need(flat(pdftext("n7002")), r"Gate-Threshold Voltage Vth\(GS\) VDS=VGS, ID=250 \u00b5A 1 1\.6 2\.5", "2N7002 Vth(GS)")
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
    # 4h. the drawn UVLO node at a start (record l8p's own C-1b; not this round's circuit): UVLOHYS 12 to 30 uA PRINTED (enabled below
    # the threshold, SNVS452G 8.3.4), R104 200 kOhm +1 %, D102's 0.715 V and UVLOTH's 2.55 V as record l9stk reads them, and the off
    # leakage of Q104 and Q105 (2N7002, drains on BRK_UVLO) at 80 nA at 25 C PRINTED, doubled every 10 K (ASSUMED, the record's rule)
    need(l69, r"UVLOHYS UVLO hysteresis current UVLO = 1 V 12 21 30", "LM5069 UVLOHYS")
    need(l69, r"When VSYS is below the UVLO level, the internal 21-.A current source at UVLO is enabled", "LM5069 UVLO sink below the level")
    need(prot, r"settles at 4\.6 V, over 2\.55 V and the diode's 0\.715 V", "record l9stk's H at 10.6 V (the sink alone)")

    def uvlo_at(site, vin=PACK_LEAST, n=2, rf=1.01):
        leak = 80e-9 * 2 ** ((site - 25.0) / DOUBLING_K)
        h = vin - 200e3 * rf * (30e-6 + n * leak)
        return h, h - 0.715
    lo_t, hi_t = 25.0, 150.0
    for _ in range(80):
        mid = (lo_t + hi_t) / 2
        lo_t, hi_t = (mid, hi_t) if uvlo_at(mid)[1] >= 2.55 else (lo_t, mid)
    R.update(uvlo_air=uvlo_at(76.25), uvlo_site=uvlo_at(SITE), uvlo_t=lo_t, uvlo_sink_only=uvlo_at(-273.0, n=0, rf=1.0))

    # the RC hold's release on the same rule (round 12; the check's F8): BRK_H charges through R104 (+1 %) into C103 (3.3 uF +10 %,
    # record l9stk's CAP_TOL) toward its settled value and releases at UVLOTH's 2.55 V plus D102's 0.715 V
    def hold_t(site, n=2, rf=1.01):
        h = uvlo_at(site, n=n, rf=rf)[0]
        need_h = 2.55 + 0.715
        return float("inf") if h <= need_h else 200e3 * 1.01 * 3.3e-6 * 1.10 * math.log(h / (h - need_h))
    R.update(hold_sink_only=hold_t(-273.0, n=0, rf=1.0), hold_air=hold_t(76.25), hold_site=hold_t(SITE))
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
        out["delays"] = O.delays(nl)
        out["levels"] = O.bound_levels(nl)
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
    # round 12 (the check's F3 and F2): the values the window and the delays are now read from, and the on-time bound
    ("R10 at 1 mOhm (round 12: the window read from R10's drawn value, about 40 to 43 A)", [("value", "R10", "1m 2512 2W (sense)")]),
    ("R135 at 1 MOhm (round 12: SENSE1's input current through it moves the window)", [("value", "R135", "1M")]),
    ("C117 at 100 nF (round 12: SENSE1's filter over its share of the sense delay)", [("value", "C117", "100n 50V C0G (SENSE1's filter)")]),
    ("C120 at 47 nF (round 12: round 11's value, the on-time past R140's figure)", [("value", "C120", "47n 50V C0G 5% (CTS2)")]),
    ("D106 removed (round 12: the on-time bound lost)", [("drop", "D106")]),
    ("R143 at 100 kOhm (round 12: BRK_PGD under Q106's threshold while the trip asserts)", [("value", "R143", "100k 1%")]),
    ("SENSE2 back on BRK_PGD (round 12: round 11's arming, no on-time bound)", [("move", "U107", "3", "BRK_PGD")]),
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
    w("     (2) Layer 6 finds no R140 whose maker prints a single pulse of at least %s J in %s ms (round 12, 4c'; 0.40 J in 1.4 ms in round 11);" % (
        fmt(R["e_r140"], 2), fmt(R["t_on_max"] * 1e3, 2)))
    w("     (3) a check of this round finds a held current over %s A, a trip at or under %s A, or a crowbar event that ends neither in" % (
        fmt(O.BLADE_BAND), fmt(SERVICE_TRUE)))
    w("     the -1's latch nor within the on-time bound (round 12), and a second negative check of the same trip follows; then (C) with its")
    w("     band reading resolved, or the blades' evidence route (round 10's (c)) as the supplier's")
    w("")
    w("4. THE TRIP ON PRINTED FIGURES (B)")
    w("   4a. THE WINDOW (INFERRED on PRINTED rows; R10 ASSUMED): OCH_A = %s x I x R10 (U106 inverting, R133 over R132); U107's VITP %s to %s V" % (
        fmt(G_RF / G_RIN, 1), fmt(O.VITP[0], 3), fmt(O.VITP[2], 3)))
    w("     (TI SNVSBJ1E 7.5, -40 to 125 C); R132 and R133 at 0.1 %% and 25 ppm/K over 100 K; OPA187's VOS %s uV in all (10 uV, 0.015 uV/C over" % fmt(O.VOS * 1e6, 1))
    w("     100 K, CMRR 126 dB at VCM V-), IB 7.5 nA, U107's ISENSE 100 nA through R135; R10 2 mOhm at 1 % and 75 ppm/K over 130 K (ASSUMED,")
    w("     record l8p 12c; no maker's sheet held, E-6): the held current is ended from %s A at the least to %s A at the most" % (fmt(lo, 3), fmt(hi, 3)))
    w("     (round 12, the check's F3: check_l8p_och.py reads R10's, R132's, R133's and R135's DRAWN values into this window and C117's,")
    w("     C119's and C120's into the delays; round 11 read R132 and R133 only, so R10 at 1 mOhm or R135 at 1 MOhm still read DRAWN)")
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
    w("     whose least is over %s A, is never more sensitive than the breaker's least unit INSIDE E-10's bound (E-10 is a bench item: an" % fmt(R["LIM"][0]))
    w("     excursion over the window lasting from %s ms up to the -1's own timer would be ended by the trip where the breaker alone" % fmt(R["tcts1"][0] * 1e3, 3))
    w("     would ride it out; the check's F7: E-10 is a condition of L8P-R11-D1); the arming's delay after PGD falls OR THE TRIP ASSERTS")
    w("     %s to %s ms (C120 22 nF C0G since round 12; round 11's 47 nF gave 4.60 to 8.36 ms after PGD's fall only)" % (
        fmt(R["tcts2"][0] * 1e3, 2), fmt(R["tcts2"][1] * 1e3, 2)))
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
    w("       %s ms (the trip's delay, the gate, the clearing) plus tCL; PGD falls only when VDS passes %s to %s V (RECORD); the arming's" % (
        fmt(R["t_event"] * 1e3, 3), fmt(R["PGD_VDS"][0], 2), fmt(R["PGD_VDS"][1], 2)))
    w("       least delay, now counted from the trip's assertion (round 12), %s ms, leaves %s ms for tCL past the gate and the clearing" % (
        fmt(R["tcts2"][0] * 1e3, 2), fmt(R["arm_margin"] * 1e3, 2)))
    w("       (tCL 45 us TYPICAL, no maximum printed: the 50 us taken is RECORD, the check's F12): the crowbar stays until the latch")
    w("     R140's single pulse WITHOUT A SOURCE (INFERRED): PACK_P under the limit at most %s V (the most limit through R140 alone), %s W" % (
        fmt(R["vlim"], 2), fmt(R["p_lim"], 0)))
    w("       for %s ms plus tCL (50 us, RECORD: 45 us TYPICAL, no maximum printed; the check's F12): %s J; the kit's %s uF on PACK_P from" % (
        fmt(R["CLEAR"] * 1e3, 3), fmt(R["e_lim"], 3), fmt(593, 0)))
    w("       %s V: %s J; the onset at the clamp, the crowbar's peak with the most limit's load for 16.5 us (an overcount: the load's current" % (
        fmt(R["vlim"], 2), fmt(R["e_cap"], 3)))
    w("       does not pass R140): %s J (round 11 printed 'under 0.003 J' beside this same arithmetic: corrected); %s J in all: ROUND 11'S" % (
        fmt(R["e_spike"], 3), fmt(R["e_n"], 2)))
    w("       FIGURE, which left out a source's share (the check's F1) and the band of 4i (F2): restated in 4c' and 4i")
    w("   4c'. A SOURCE'S SHARE (round 12, the check's F1; C-PROT rev 1: each source present or absent)")
    w("     the path that holds VSYS (RECORD, L4-E9's power edges): P06 the entry to VIN_RAW, P07 VIN_RAW into the front end U2, P10 the")
    w("       charger U3 onto VSYS, P11 VSYS through the battery FETs, R17 and A's F1 to the pack: THE CHARGER holds VSYS; board E's entry")
    w("       (its overcurrent 6.364 to 7.136 A, its short-circuit 10.36 to 13.87 A) acts on VIN_RAW two conversions upstream, so its")
    w("       thresholds bound VIN_RAW's current, not the current a source pushes from VSYS into PACK_P (round 11's 4e and the check's")
    w("       estimate read them as VSYS's: WITHDRAWN as the path's reading)")
    w("     the charger's printed figures are regulations: the pre-charge clamp at 384 mA +-25 % (PRINTED, IPRECHRG_REG_ACC, 0 to 85 C:" )
    w("       at most %s A) acts only while a charge is commanded and VBAT is under VSYS_MIN; its cycle-by-cycle comparators (VOCP_lim) print" % fmt(R["pre_max"], 2))
    w("       a typical only; neither its loops nor the front end's ISNS loop print a settling time. SETTLED, on the record's B-R2 basis")
    w("       (L4-E11: the charger holds a resistive load on the pack side at sqrt(P x R) with the front end's %s W, RECORD), a source alone" % fmt(R["p_src"], 0))
    w("       holds R140 at %s V, %s A; INSIDE THE EVENT no printed figure bounds its current, so R140 is bounded on VOLTAGE:" % (
        fmt(R["v_settled"], 2), fmt(R["i_settled"], 1)))
    w("       while the -1 conducts PACK_P is under BRK_VIN (at most %s V: %s W in R140 at its least), once latched at most VSYS's %s V" % (
        fmt(PACK_MOST, 1), fmt(R["p_on"], 0), fmt(R["vsys_max"], 3)))
    w("       (RECORD, L4-E11 12c: %s W), for the crowbar's on-time, which 4i bounds" % fmt(R["p_after"], 0))
    w("     the turn-off (round 12 adds Q110's own, left out in round 11): tCTR1 40 us PRINTED, Q110's gate through R136 %s ms (twice its" % fmt(R["t_q110"] * 1e3, 3))
    w("       TYPICAL Ciss, ASSUMED: no maximum printed), Q111's gate through R138, five time constants of its PRINTED 11.4 nF: %s ms in all" % fmt(R["t_off"] * 1e3, 3))
    w("     R140's single pulse, each case (INFERRED; the time from the trip's assertion):")
    w("       no source, the -1 latched (round 11, above)                                   %s J in %s ms" % (fmt(R["e_n"], 3), fmt((R["t_gate"] + R["CLEAR"] + TCL_RECORD) * 1e3, 3)))
    w("       a source present, the -1 latched                                              %s J in %s ms" % (fmt(R["e_n_src"], 3), fmt((R["t_gate"] + R["CLEAR"] + TCL_RECORD + R["t_off"]) * 1e3, 3)))
    w("       no source, the band of 4i, ended by the on-time bound                         %s J in %s ms" % (fmt(R["e_s"], 3), fmt(R["t_on_max"] * 1e3, 3)))
    w("       a source present, the -1 held out of its limit, ended by the on-time bound    %s J in %s ms" % (fmt(R["e_w"], 3), fmt(R["t_on_max"] * 1e3, 3)))
    w("       E-6b RESTATED: a part whose maker prints a single pulse of at least %s J in %s ms (%s W held, %s W for 16.5 us at the clamp);" % (
        fmt(R["e_r140"], 2), fmt(R["t_on_max"] * 1e3, 2), fmt(R["p_after"], 0), fmt(R["p_peak"], 0)))
    w("       round 11's 0.40 J in 1.4 ms is withdrawn. No 2512 sheet this record holds prints it: a larger part (Layer 6's selection,")
    w("       with its maker's pulse curve read at %s ms; a power package or parallel pulse-rated chips on the PACK_P band) (CONDITIONAL)" % fmt(R["t_on_max"] * 1e3, 2))
    w("     Q111 (CSD18510Q5B, PRINTED): IDM 400 A against %s A at the onset and %s A held with a source; VDS 40 V against PACK_P's %s V" % (
        fmt(R["peak_clamp"], 1), fmt(R["i_q111_src"], 1), fmt(CLAMP, 1)))
    w("       clamp; VGS 20 V against D105's 12.7 V; its own turn-off crosses at most V^2/4R: %s W without a source (at %s V), WITHIN the" % (
        fmt(R["p_q111_off_nosrc"], 1), fmt(R["v_force"], 2)))
    w("       record's derated %s W of the same part at %s ms (l9stk 15.6) for at most %s ms; %s W on the settled source basis, WITHIN;" % (
        fmt(R["PULSE"][2], 1), fmt(R["PULSE"][1], 3), fmt(R["t_q111_off"] * 1e3, 3), fmt(R["p_q111_off_settled"], 1)))
    w("       %s W on the voltage bound with a source: NOT SHOWN (its SOA at %s ms or less is not read: CONDITIONAL, with E-2 and E-3)" % (
        fmt(R["p_q111_off"], 0), fmt(R["t_q111_off"] * 1e3, 2)))
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
    w("     low (round 12: or while RESET1 is asserted, through D106), so Q112 is off and the crowbar disarmed whenever the breaker is not")
    w("     running: at a gauge's wake, at a docking (the RC hold's 0.110 s and the start), during a start (PGD low while VDS is high), once")
    w("     latched, and %s ms at most after the trip asserts (4i); the trip touches neither the enable loop nor" % fmt(R["tcts2"][1] * 1e3, 2))
    w("     UVLO (check_l8p_och's APART): L4-E11 20c's window, its readings and the RC hold's 0.110 to 0.907 s are unchanged")
    w("     EACH SOURCE PRESENT OR ABSENT (C-PROT rev 1): with a source holding VSYS and board A's battery FETs on, the crowbar also loads the")
    w("       source through those FETs, CELL+, the dock and the lead, for the event and the crowbar's turn-off after the latch (%s ms," % fmt(R["t_off"] * 1e3, 2))
    w("       4c'), %s ms at most when the -1 latches, %s ms at most when it does not (4i); that current returns through board A's ground," % (
        fmt(R["t_src"] * 1e3, 2), fmt(R["t_on_max"] * 1e3, 2)))
    w("       not R10, so it never holds the trip; THE CHARGER holds VSYS (L4-E9's P10, 4c'): board E's entry (overcurrent %s to %s A," % (
        fmt(R["ENTRY"][0], 3), fmt(R["ENTRY"][1], 3)))
    w("       short-circuit %s to %s A, record l4e11 3c, RECORD) meets it only through the front end and the charger, two conversions" % (
        fmt(R["ENTRY"][2], 2), fmt(R["ENTRY"][3], 2)))
    w("       upstream (round 11 read it as a short on VSYS: corrected); the source's share and R140's pulse are 4c''s; the battery FETs")
    w("       carry at most that source current, reversed, inside their held rows; afterwards a charge through the latched")
    w("       breaker's body diodes is route R1's (round 3: the detector holds the return, board A's inhibit sets), as after any latch")
    w("     THE GAUGE: R10 carries the event, so the gauge's AFE reads it as it reads any short on PACK_P (IF-6); its levels are unchanged")
    w("       (IF-4), and if its ASCD acts Q2 opens behind the latched breaker; the gauge's recovery is the battery stream's")
    w("   4f. THE STANDING CURRENT from BRK_VIN: U106 %s uA, U107 %s uA, R139 with R141 %s uA at %s V (PRINTED maxima): beside the detector's" % (
        fmt(R["stand"][0] * 1e6, 0), fmt(R["stand"][1] * 1e6, 1), fmt(R["stand"][2] * 1e6, 1), fmt(PACK_MOST, 1)))
    w("     0.47 mA (record l8p round 3), a standby load on the pack for the battery stream")
    w("   4g. ITS OWN SINGLE FAILURES (INFERRED from the circuit as drawn):")
    for a, b in FAILS:
        w("     %-52s %s" % (a, b))
    w("     so a latent first failure returns the design to round 10's rows at %s A held (the blades at %s %% of their rerated current, no part" % (
        fmt(I), fmt(100 * I / W["I_rr_air"], 1)))
    w("       the guard protects exposed: M-A holds the FETs at %s A on a board whose path meets E-1's bar); no automatic diagnostic is" % fmt(I))
    w("       drawn and THE TRIP'S SILENT FAILURES HAVE NO DETECTION INTERVAL beyond E-12f at commissioning and at each service: L4A-67's")
    w("       acceptance ('fails on any latent first failure left without its interval') reads NOT MET on that clause (the check's F6);")
    w("       an automatic test is REMAINING ENGINEERING with HO-A's pattern")
    w("     Q110 OR Q111 SHORTED WITH A SOURCE (the check's F11): the -1 latches (found at the next start); while a source holds VSYS with")
    w("       the battery FETs on when the failure comes, CELL+ stays tied to VSYS and the charger holds R140 as a resistive load: on the")
    w("       record's settled B-R2 basis %s V, %s A, %s W held (L4-E11: the DD-7 inhibit sets only under %s V on CELL+, and does not here)," % (
        fmt(R["v_settled"], 2), fmt(R["i_settled"], 1), fmt(R["p_src"], 0), fmt(R["inh_v"], 2)))
    w("       until R140 opens (then the crowbar's open failure, latent, as the second row) or the source goes; the charger's pre-charge")
    w("       clamp (at most %s A, PRINTED) holds it under %s W only while a charge is commanded with VBAT under VSYS_MIN, which nothing" % (
        fmt(R["pre_max"], 2), fmt(R["pre_max"] ** 2 * R140 * 1.01, 3)))
    w("       drawn forces; when the failure precedes the source, CELL+ is dead, the DD-7 inhibit holds the battery FETs off and only their")
    w("       off leakage flows. FINDING L8P-R12-F1 (new, OPEN; the record's B-R2 state with R140 as its resistive fault): smallest")
    w("       corrections for the next round, none drafted here: a series element whose maker's curve passes the event's pulse and opens")
    w("       the held %s A inside R140's printed short-time rating (chosen with R140's part, E-6b), or route R1's blocking element" % fmt(R["i_settled"], 1))
    w("   4h. A FINDING ON THE DRAWN UVLO NODE (L8P-R11-F1, this record's own C-1b of round 2; OPEN; not this round's circuit, which adds")
    w("     nothing on UVLO): below its threshold U101 sinks UVLOHYS, 12 to 30 uA PRINTED, so at a start H settles under R104 with that sink and")
    w("     every off leakage on BRK_UVLO; record l9stk counts the sink alone (H %s V at %s V, R104 nominal). Q104's and Q105's drains sit on BRK_UVLO: at" % (
        fmt(R["uvlo_sink_only"][0], 2), fmt(PACK_LEAST, 1)))
    w("     the 2N7002's 80 nA at 25 C (PRINTED) doubled every 10 K (ASSUMED, the record's own rule), R104 +1 %, D102's 0.715 V and UVLOTH's")
    w("     2.55 V (RECORD): at %s V UVLO reaches %s V with both at the 76.25 C air (%s V of margin) and %s V at the %s C site: NOT RELEASED;" % (
        fmt(PACK_LEAST, 1), fmt(R["uvlo_air"][1], 2), fmt(R["uvlo_air"][1] - 2.55, 2), fmt(R["uvlo_site"][1], 2), fmt(SITE)))
    w("     the release at the pack's least fails above a site of %s C on that rule: a docking with board P warm and the pack low would not" % fmt(R["uvlo_t"], 1))
    w("     start the breaker (the service, not a protection). Smallest corrections, for this record's next round (none drafted here): R104")
    w("     lowered with C103 raised to keep the hold's 0.110 to 0.907 s, or inverters whose maker prints the hot off leakage, or both;")
    w("     evidence: Q104's and Q105's IDSS at 86.25 and 101 C on board P's specimen (E-12's bench)")
    w("     IT ALSO STRETCHES THE RC HOLD (the check's F8; the same rule, INFERRED): BRK_H settles at %s V at the 76.25 C air against the" % fmt(R["uvlo_air"][0], 2))
    w("       3.265 V the release needs, so the hold takes %s s (R104 +1 %%, C103 +10 %%), against the %s s the record's sink-only figure" % (
        fmt(R["hold_air"], 2), fmt(R["hold_sink_only"], 3)))
    w("       gives and L4-E11's DD-7 restart timeline (at most 1.149 s) uses: an affected output of L8P-R11-F1 (L4-E11 20d's timeline")
    w("       and record l9stk's 0.110 to 0.907 s); never released at the %s C site" % fmt(SITE))
    w("   4i. THE BRK_VIN RANGE AND THE ON-TIME BOUND (round 12, the check's F2)")
    w("     the event can happen from BRK_VIN %s V (C-PROT rev 1: the -1 runs from its power-on threshold, record l8p 12d; PORIT %s V is" % (
        fmt(R["v_floor"], 1), fmt(7.6, 1)))
    w("       a TYPICAL with an 8 V maximum and no minimum printed) to the pack's %s V, the clamp's %s V in a surge" % (fmt(PACK_MOST, 1), fmt(CLAMP, 1)))
    w("     from %s V up (the most limit through R140 at +1 %%) the crowbar's own current exceeds every unit's limit: the -1 limits and" % fmt(R["v_force"], 2))
    w("       latches whatever the load (no source). UNDER IT the latch rests on the faulted load persisting as PACK_P falls; if the load")
    w("       drops out (a constant-power load under its own UVLO, another protection acting) a unit whose limit is over the crowbar's own")
    w("       current leaves its limit, and the crowbar's own current through R10, over the window's least, HOLDS THE TRIP: the band")
    w("       %s to %s V (the window's least through R140 at -1 %%, the most limit through it at +1 %%), %s W in R140 held in round 11's" % (
        fmt(R["band"][0], 2), fmt(R["band"][1], 2), fmt(R["p_stall"], 0)))
    w("       drawing: a DEMONSTRATED DEFECT of the draft (no source); with a source's settled share on the record's B-R2 basis the -1 can")
    w("       stay out of its limit up to %s V, and inside the event's unprinted transient up to the pack's %s V (4c')" % (fmt(R["v_band_src"], 2), fmt(PACK_MOST, 1)))
    w("     three approaches (constitution section 4): (a) R140 under 7.6 V / (23.93 A x 1.01) = %s Ohm, so the crowbar alone exceeds the" % fmt(7.6 / (R["LIM"][2] * 1.01), 4))
    w("       limit from 7.6 V: its peak at the clamp, %s A with the most limit's load, passes the %s A where VIN to SENSE exceeds its 0.3 V" % (
        fmt(CLAMP / (7.6 / (R["LIM"][2] * 1.01) * 0.99) + R["LIM"][2], 1), fmt(R["VSNS_I"], 1)))
    w("       absolute maximum (a row newly reached), and a source can still hold the -1 out of its limit: NOT SELECTED; (b) the trip armed")
    w("       only above %s V: the blades' held 23.93 A stays uncorrected under it, L8P-R10-F1 open in that band: NOT SELECTED; (c) THE" % fmt(R["v_force"], 2))
    w("       ON-TIME BOUND, SELECTED (SESSION L8P-R12-D1): channel 2 also reads the trip, through D106 (BAT46W: VF at most 0.25 V at 0.1 mA,")
    w("       PRINTED, with RESET1's VOL at most 0.3 V: OCH_S2 under 0.55 V against SENSE2's least 0.792 V) and R143 2.2 MOhm from BRK_PGD,")
    w("       so RESET2 disarms the crowbar %s to %s ms after the trip asserts whatever the breaker does; it re-arms only once RESET1 has" % (
        fmt(R["tcts2"][0] * 1e3, 2), fmt(R["tcts2"][1] * 1e3, 2)))
    w("       released (R10 under the window: the dropped load) and PGD is high, so no retry train; the least delay covers the gate and the")
    w("       -1's clearing with %s ms for tCL; the crowbar conducts at most %s ms" % (fmt(R["arm_cover"] * 1e3, 2), fmt(R["t_on_max"] * 1e3, 2)))
    w("     its levels (check_l8p_och.py's arithmetic on the drawn R143): BRK_PGD stays over Q106's 2.5 V threshold maximum (JSCJ, PRINTED)")
    w("       at BRK_VIN 7.6 V while D106 pulls (so the restart inhibit stays gated during the event), and OCH_S2 armed stays over SENSE2's")
    w("       release with RESET1's 300 nA and SENSE2's 100 nA through R143 (PRINTED)")
    w("     WHAT STAYS: a held overload that persists through the bound with the -1 out of its limit leaves the trip disarmed until it falls")
    w("       under the window (round 10's rows meanwhile): it needs a source to carry (V / R140 + the window's least - the most limit) x V")
    w("       for %s ms, on the record's settled basis only at BRK_VIN under %s V (the -1's floor %s V), otherwise only inside the source's" % (
        fmt(R["tcts2"][0] * 1e3, 2), fmt(R["v_resid"], 2), fmt(R["v_floor"], 1)))
    w("       unprinted settling: CONDITIONAL, evidence E-12s (new): board P with boards A and E, a source at its IIN_HOST, a held overload")
    w("       over the window at BRK_VIN 7.6, 10.6 and 16.8 V, ten events each: the -1 latched inside %s ms, the source's current into the" % fmt(R["tcts2"][0] * 1e3, 2))
    w("       pack lead and R140's voltage recorded")
    w("")
    w("5. THE DRAFT COMPOSED IN L4-E9'S ORDER (board P; INFERRED from the regenerated netlist)")
    for name, r in K["steps"]:
        w("   %-58s %s" % (name, r))
    w("   board P regenerated: %d parts; netlist sha256/16 %s" % (K["parts"], K["net_sha"]))
    w("   check_l8p_netlist.py on it: %s" % "; ".join(l.strip() for l in K["l8p_lines"]))
    w("   check_l8p_och.py on it: OCH %s%s; the window from the drawn values %s to %s A" % (
        K["och"][0], (": " + "; ".join(K["och"][1])) if K["och"][1] else "", fmt(K["win_drawn"][0], 3), fmt(K["win_drawn"][1], 3)))
    w("     (round 12) the drawn delays: SENSE1's filter %s us, the sense delay %s to %s ms, the arming and on-time delay %s to %s ms;" % (
        fmt(K["delays"]["filter"] * 1e6, 1), fmt(K["delays"]["cts1"][0] * 1e3, 3), fmt(K["delays"]["cts1"][1] * 1e3, 3),
        fmt(K["delays"]["cts2"][0] * 1e3, 2), fmt(K["delays"]["cts2"][1] * 1e3, 2)))
    w("     the bound's levels at BRK_VIN 7.6 V: OCH_S2 %s V with RESET1 asserted, BRK_PGD %s V, OCH_S2 armed %s V" % (
        fmt(K["levels"]["low"], 2), fmt(K["levels"]["pgd"], 2), fmt(K["levels"]["armed"], 2)))
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
    w("     included); its latent failures (L8P-R9-F1) expose no part at the held currents M-A holds ON A BOARD WHOSE INSTALLED PATH MEETS")
    w("     E-1's BAR (round 12, the check's F5: a per-built-board check of the battery FETs' path, E11-29u, names it); on a board that")
    w("     misses the bar (a void or a tab joint E11-29's coupon does not see) the guard's own silent failures, with no detection")
    w("     interval, stay a residual (REMAINING ENGINEERING, HO-A's pattern)")
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
    w("     record l9stk 15.9 (apply_l9stk_guard_allowance.py, three edits: this restatement after the supply bullet, the acceptance item")
    w("       and the Layer 5 row of its correction scope, each keeping the round's 30 uA as history): '%s'" % L9STK_TEXT)
    w("   the replay of L4-E11's 20f, 22 and 28 at these figures: record l4e11's round 19 (l4e11_rowc.py)")
    w("")
    w("8. VERDICTS")
    w("   L8P-R10-F1: CORRECTED IN DRAFT by (B), SESSION L8P-R11-D1: composed in L4-E9's order, read DRAWN, %d of %d mutations FAIL; electrical" % (
        sum(1 for _n, v, _w in K["muts"] if v == "FAIL"), len(K["muts"])))
    w("     acceptance on printed figures: no current held over %s A, %s %% of the blades' rerated current at the band, the service untouched;" % (
        fmt(hi), fmt(100 * hi / O.BLADE_BAND, 1)))
    w("     CONDITIONAL on E-6 (R10's sheet within -7.3 to +8.3 %%), E-6b (R140's printed pulse, RESTATED in round 12: %s J in %s ms), E-10" % (
        fmt(R["e_r140"], 2), fmt(R["t_on_max"] * 1e3, 2)))
    w("     (the key-down excursions under 0.282 ms: a bench item, the check's F7), E-12f, E-12s (round 12, 4i) and the latent-failure")
    w("     residual of 4g; round 12 corrects the band of 4i (a demonstrated defect of round 11's drawing) by the on-time bound, composed,")
    w("     read DRAWN and mutated (section 5); UNVERIFIED until the targeted recheck (L4A-69); the approaches (A) NOT SUPPORTED and (C) NOT")
    w("     SELECTED on printed figures")
    w("   L4A-67: C-PROT rev 1 for the guard on the corrected circuit: every series part within its printed limits below and above the trip")
    w("     where a printed figure exists; NOT SHOWN, each missing figure named and CONDITIONAL: board P's switches' hot RDS(on) (E-8, E-11),")
    w("     R10, R101, R102 and R140 (E-6, E-6b), the 12 AWG wires (a maker's ampacity at 76.25 C with its insulation class), the dock pins'")
    w("     split (E-4), Q111's turn-off with a source (its SOA); the battery FETs at most 150 C on the held state, CONDITIONAL on E-05,")
    w("     E11-29, E11-36 and E-9 (round 12, the check's F4); THE REGISTER'S ACCEPTANCE READS NOT MET on its latent-failure clause: the")
    w("     trip's silent failures (4g) and the guard's on a board that misses E-1's bar have no detection interval (REMAINING ENGINEERING;")
    w("     the check's F6; round 11's 'DONE on the desk' withdrawn); L8P-R12-F1 (a shorted crowbar with a source, 4g) OPEN")
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
    ("Q110 or Q111 shorted", "the crowbar at every start: the -1 latches in its start (found); with a source, 4g's last lines"),
    ("Q112 shorted, RESET2 stuck high", "the arming and the on-time bound lost: a crowbar for tSD at a gauge's wake on a live PACK_P"),
    ("RESET2 stuck low, C120 shorted", "the crowbar disarmed, LATENT: as the first row"),
    ("C119 open", "the sense delay 17 us at most: a trip on an excursion E-10 allows (found)"),
    ("D106 or R143 open (round 12)", "the on-time bound lost, LATENT: round 11's state, 4i's band unbounded (E-12f reads TP112)"),
    ("C120 open (round 12)", "the bound at 17 us: the crowbar too short to latch the -1: the trip lost, LATENT (E-12f: TP111's pulse)"),
    ("R143 shorted (round 12)", "D106 pulls BRK_PGD while the trip asserts: Q106 off, a hot pad's inhibit pulls UVLO (found, E-12b)"),
    ("D106 shorted (round 12)", "OCH_S2 on OCH_R: armed at OCH_R's level, disarmed while RESET1 asserts: as drawn"),
)

import apply_pcb_interfaces_guard_allowance as A5   # noqa: E402  Layer 5's text, one source
import apply_l9stk_guard_allowance as A9           # noqa: E402  record l9stk 15.9's restatement, one source
LAYER5_TEXT = A5.TEXT
L9STK_TEXT = " ".join(A9._NEW_1.split("\n", 1)[1].replace("**", "").split())


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
         "  E-05, E11-29, E11-36, E-9 (the -1's as-built most limit: the trip failed, the FETs hold the breaker's limit; round 12, the check's",
         "  F4) and, for the claim that the guard's silent failures expose nothing, each built board's path meeting E-1's bar (E11-29u; F5)"],
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
        ["Q111 (CSD18510Q5B, the crowbar; round 11, restated in round 12)",
         "held: off (IDSS 1 uA at 25 C PRINTED) | the event: %s A at the onset and %s A held with a source (4c') against IDM 400 A PRINTED; its" % (
             fmt(R["peak_clamp"], 1), fmt(R["i_q111_src"], 1)),
         "  turn-off crossing %s W without a source, WITHIN the same part's derated %s W at %s ms; %s W with a source on the voltage" % (
             fmt(R["p_q111_off_nosrc"], 1), fmt(R["PULSE"][2], 1), fmt(R["PULSE"][1], 3), fmt(R["p_q111_off"], 0)),
         "  bound (%s W on the settled basis) | WITHIN on current; the turn-off with a source NOT SHOWN (its SOA at %s ms not read)" % (
             fmt(R["p_q111_off_settled"], 1), fmt(R["t_q111_off"] * 1e3, 2))],
        ["D106 (BAT46W) and R143 (2.2 MOhm; round 12, the on-time bound)",
         "held: D106 reverse at most half the clamp's 29.2 V against its 100 V; R143 at most 14.6 V across 2.2 MOhm | WITHIN"],
        ["R10 (2 mOhm 2512 2 W, the gauge's sense and the trip's)",
         "held: %s W at %s A | the event: the hot-short row's 16.5 us | NOT SHOWN: MISSING its maker's sheet (tolerance, temperature" % (fmt(hi ** 2 * 2e-3, 2), fmt(hi)),
         "  coefficient, derating at the band; E-6); the trip's window holds for R10 within -7.3 to +8.3 %"],
        ["R101, R102 (the breaker's sense pair; no part chosen)",
         "held: %s and %s W at %s A | NOT SHOWN: MISSING the parts (Layer 6: 2 W each at the band's temperature, 1 %%, at most 50 ppm/K; E-6)" % (
             fmt(W["SNS_REC"][0] * k, 2), fmt(W["SNS_REC"][1] * k, 2), fmt(hi))],
        ["R140 (the crowbar's resistor; round 11, restated in round 12)",
         "held: no current | the event: at most %s J in %s ms (4c': a source present, the -1 held out of its limit; %s J without a source" % (
             fmt(R["e_r140"], 2), fmt(R["t_on_max"] * 1e3, 2), fmt(R["e_n"], 2)),
         "  and the -1 latched) | NOT SHOWN: MISSING a part whose maker prints that single pulse (E-6b restated; round 11's 0.40 J withdrawn)"],
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
        ("the arming's least delay, from the trip's assertion, covers the gate, the clearing and 0.5 ms for tCL (round 12)", R["arm_margin"] > O.ARM_MARGIN),
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
        ("record l9stk's H at 10.6 V with the sink alone reproduces 4.6 V (R104 nominal)", abs(R["uvlo_sink_only"][0] - 4.6) < 0.05),
        ("L8P-R11-F1: the drawn UVLO node is not released at 10.6 V with its inverters at the 86.25 C site (the rule ASSUMED)", R["uvlo_site"][1] < 2.55),
        # round 12
        ("F8: the RC hold's sink-only release reproduces the record's 0.907 s", abs(R["hold_sink_only"] - 0.907) < 1e-3),
        ("F8: on the same leakage rule the hold at the 76.25 C air is longer than DD-7's 0.907 s", R["hold_air"] > 0.907),
        ("F2: round 11's band exists: the window's least through R140 is under the most limit through it", R["band"][0] < R["band"][1]),
        ("F2: the band lies inside the BRK_VIN range the -1 runs at (from 7.6 V)", R["band"][1] > R["v_floor"]),
        ("F2: approach (a)'s peak at the clamp passes VIN to SENSE's 0.3 V current", CLAMP / (7.6 / (R["LIM"][2] * 1.01) * 0.99) + R["LIM"][2] > R["VSNS_I"]),
        ("F2: the on-time bound's most is the one R140's restated pulse is stated for", R["tcts2"][1] <= O.T_ON_BOUND),
        ("F1: R140's restated pulse is the largest of the four cases and over round 11's", R["e_r140"] >= max(R["e_n"], R["e_s"], R["e_w"], R["e_n_src"]) and R["e_r140"] > R["e_n"]),
        ("F1: the source's settled voltage on R140 is under VSYS's most and over the DD-7 inhibit's threshold (L8P-R12-F1)", R["inh_v"] < R["v_settled"] < R["vsys_max"]),
        ("F1: Q111's turn-off without a source is within the same part's derated point", R["p_q111_off_nosrc"] < R["PULSE"][2] and R["t_q111_off"] < R["PULSE"][1] * 1e-3),
        ("F3: the reader computes the window, the delays and the bound from the drawn values", K["delays"] is not None and K["levels"] is not None),
        ("F2: D106's low level is under SENSE2's least threshold", K["levels"]["low"] < O.VITP[0]),
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
