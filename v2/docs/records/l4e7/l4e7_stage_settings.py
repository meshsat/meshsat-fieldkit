#!/usr/bin/env python3
"""l4e7_stage_settings.py: layer 4 task L4-E7 (MESHSAT-1357, 1 October 2026). Implementable choice 3, REAL COMPONENT
SETTINGS for board E's solar stage, of v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md (finding O-2, "the stage's input power
is not controlled", status "B2: arithmetic corrected under stated assumptions (closed). O-2 physical compliance: OPEN";
the power review's L4-R01): the LT8705A's grade, RSENSE1 and RIMON_IN of its input-current limit, and R8 and R9 of its
input-voltage hold, chosen as catalogue parts with their makers' tolerance and TCR, and section 11's 100 W corner check of
l4e_replay.py re-run on the values those parts achieve, at both temperature ends.

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured; no generator, registry or rendered page in
the tree is edited (the apply_gen_sch_e_*.py drafts beside this file are for board E's generator owner). Every figure carries
its basis: MAKER (document, revision, page), NETLIST (the committed board E netlist), CATALOGUE (an LCSC or JLCPCB reading
filed under inputs/), MODELED (the energy model, through l4e_replay.py's own functions), INFERRED (method stated),
ASSUMPTION (a figure no document gives) or SESSION (a design rule this record sets, with its reason).

Section 0 proves, before any result (exit 4 otherwise):
  0a l4e_replay.py, re-run in a child process, reproduces l4e_replay.out byte for byte;
  0b l4e5_source_control.py, re-run in a child process, reproduces l4e5_source_control.out byte for byte;
  0c l4e_replay.main(), run here with its locals captured by l4e4_limits.run_main_captured(), prints l4e_replay.out byte
     for byte, so the functions this record uses (i_factor, ec_row, the hold, the candidate panel's trace, meanday and
     least) are the ones that printed the record. Nothing here compares a git hash with a recorded string.

Run from the repository root:  python3 v2/docs/records/l4e7/l4e7_stage_settings.py > v2/docs/records/l4e7/l4e7_stage_settings.out
Needs pdftotext, PyYAML and the held documents (fetch_held_back.py beside this file, and the ones the imported records
name). About five minutes, most of it section 0.
Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction or a predicate failed."""
import hashlib
import importlib.util
import itertools
import json
import math
import os
import re
import subprocess
import sys
import textwrap

sys.dont_write_bytecode = True
try:
    os.nice(10)                 # a shared host: stay behind interactive work
except OSError:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REPLAY_PY = "v2/docs/records/l4e/l4e_replay.py"
REPLAY_OUT = "v2/docs/records/l4e/l4e_replay.out"
L4E5_PY = "v2/docs/records/l4e5/l4e5_source_control.py"
L4E5_OUT = "v2/docs/records/l4e5/l4e5_source_control.out"
L4E4_PY = "v2/docs/records/l4e4/l4e4_limits.py"
GEN_E = "v2/ecad/tools/gen_sch_e.py"
NET_E = "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"
ENV = "v2/ecad/tools/pcb_envelope.yaml"
REQS = "v2/ecad/tools/pcb_requirements.yaml"
LT = "v2/vendor/power/lt8705a.pdf"
HOJ = "v2/vendor/passives/milliohm-hojlr2512-series.pdf"
RT = "v2/vendor/passives/held/yageo-rt-series-v16-2025-05-06.pdf"
BSC039 = "v2/vendor/infineon/infineon-bsc039n06ns-rev2.4-c534330.pdf"
BSC028 = "v2/vendor/power/held/infineon-bsc028n06ns-rev2.1-c148250.pdf"
INP = "v2/docs/records/l4e7/inputs"
CLAR = "v2/docs/records/l4e7/clarification"
INP_L4E4 = "v2/docs/records/l4e4/inputs/jlc-search-hojlr2512-3w-2026-10-01.json"
PINS = {
    REPLAY_PY: "3de985e2e3e06453d2c9d576311c1f39935149ac1e9b7cff0431a40933bb8734",
    REPLAY_OUT: "59c6eeab16da98f8ddf16880ddcdc1d2a2c910f4256be9b69aade49dd4d2726d",
    L4E5_PY: "4315c900db1426f78b544baf7c40597e2ac06479258794bf554281a26e391fd1",
    L4E5_OUT: "f9c98ec5c43ada0e1a5a033a794c98b45f110ffcb0a67ff8c81a31fede134e71",
    L4E4_PY: "d4a484439a7b53030423b596769bf748469134a45a46b3c91724e2b80d9e2a42",
    GEN_E: "f846e138cb53a8c63247efb3ad7b5cc44a68cb73e71699c65fd53b63c01af186",
    NET_E: "2ed95a0e8069ebf8ad31f4567a14015e863182a83b6de7b3b13218488d8316d4",
    LT: "8f552a0b57677bfa7e4a5d5d0fac56d56fbbd1a6f65a9ee7aaaf8743cd534ec3",
    HOJ: "3224518dbc8bdc858a96cfde88de2611494550f95406f6b65130c232cdfc93fb",
    RT: "0a729d144519a7021c82a0ef242b064e467c70d44afcf9eabd6c7ffdc4b673a3",
    BSC039: "8d95c1da9c78b3afb037e1f80c3bea1ed0f874f689e3a0c96d926dafe6a437b9",
    BSC028: "2959653166e981f9de24cd9c141c44490ecc62acba5971ec8c0b263eca9708e0",
    INP_L4E4: None,             # read only; its codes are checked against the filed LCSC answer below
}
# The figures this record sets itself (each SESSION or ASSUMPTION, named where it is used):
EA2_FLOOR_DIV = 2.0      # SESSION: the setting's design floor takes EA2's and EA3's unprinted gains at half their typical
LINE_FLOOR_MUL = 2.0     # SESSION: and the references' line regulation (printed at 25 C, not switching) at twice its maximum
STOCK_MIN = 1000         # SESSION: a catalogue value is a candidate only with at least this many in stock at the reading
V_STEP = 0.01            # the corner check's voltage grid, V (the replay's own step)
I_RES = 0.001            # the old setting's grid, A (the replay's I_RES), for its row only
HOLD_RANGE = (15.5, 17.5)  # the NOT ADOPTED proposal's scan only: nominals inside the candidate's hourly MPP span +- about 1 V
OFFICIAL_URL = "https://www.analog.com/media/en/technical-documentation/data-sheets/8705af.pdf"   # the owner's named sheet
IA_SNAPSHOT = "20250322064938"   # the Internet Archive's copy of that URL (the live site resets this runner's connection)
CIMON = ("C65", "100n", "C14663")   # SESSION: CIMON_IN at the maker's 0.1 uF lower end (8705af p.31), the 0603 X7R board E uses


def refuse(code, msg):
    sys.stderr.write("l4e7_stage_settings: %s; refusing\n" % msg)
    sys.exit(code)


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def pg(rel, n, layout=True):
    a = ["pdftotext"] + (["-layout"] if layout else []) + ["-f", str(n), "-l", str(n), os.path.join(TOP, rel), "-"]
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode != 0:
        refuse(3, "pdftotext could not read %s p.%d" % (rel, n))
    return r.stdout


def flat(t):
    return " ".join(t.split())


def need(text, pat, what):
    m = re.search(pat, text, re.M)
    if not m:
        refuse(3, "%s not found" % what)
    return m


def load(name, rel):
    sp = importlib.util.spec_from_file_location(name, os.path.join(TOP, rel))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def catalogue(code):
    """A filed LCSC answer (inputs/lcsc-<code>-2026-10-01.json): model, stock, tolerance and TCR as the catalogue prints them."""
    p = os.path.join(TOP, INP, "lcsc-%s-2026-10-01.json" % code)
    if not os.path.isfile(p):
        refuse(3, "no filed catalogue reading for %s" % code)
    return json.load(open(p, encoding="utf-8"))


def rvalue(model):
    """The resistance of a YAGEO RT0603BRD07 model in ohms ('RT0603BRD0723K2L' is 23.2k)."""
    m = re.match(r"RT0603BRD07(\d+)K(\d*)L$", model)
    return float(m.group(1) + ("." + m.group(2) if m.group(2) else "")) * 1e3 if m else None


def bound_status(rows):
    """CONDITIONAL exactly when a row that affects the 100 W bound is not resolved by a guaranteed limit or a maker's statement."""
    return "CONDITIONAL" if any(r_["bound"] and not r_["resolved"] for r_ in rows) else "UNCONDITIONAL"


def compute():
    for rel, want in PINS.items():
        if want is not None and sha(rel) != want:
            refuse(2, "%s is not the pinned file%s" % (rel, " (fetch it: v2/docs/records/l4e7/fetch_held_back.py)" if "/held/" in rel else ""))
    R = {}
    # ================================================================== 0: the reproductions
    outr = open(os.path.join(TOP, REPLAY_OUT), "rb").read()
    out5 = open(os.path.join(TOP, L4E5_OUT), "rb").read()
    cr = subprocess.run([sys.executable, "-B", os.path.join(TOP, REPLAY_PY)], cwd=TOP, capture_output=True)
    R["r0a"] = cr.returncode == 0 and cr.stdout == outr
    c5 = subprocess.run([sys.executable, "-B", os.path.join(TOP, L4E5_PY)], cwd=TOP, capture_output=True)
    R["r0b"] = c5.returncode == 0 and c5.stdout == out5
    if not (R["r0a"] and R["r0b"]):
        refuse(4, "a child re-run does not reproduce its record (replay %s, l4e5 %s)" % (R["r0a"], R["r0b"]))
    L4 = load("l4e4_limits_for_l4e7", L4E4_PY)
    RP = load("l4e_replay_for_l4e7", REPLAY_PY)
    rc, text, LR = L4.run_main_captured(RP)
    R["r0c"] = rc == 0 and text.encode("utf-8") == outr
    if not R["r0c"]:
        refuse(4, "l4e_replay.main() does not print its record in-process")

    # ================================================================== 1: board E as drawn (NETLIST) and the generator
    sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
    import netlist_sexp as N
    e = N.load(os.path.join(TOP, NET_E))

    def nets(ref):
        return {p: v["net"] for p, v in e["pins"][ref].items()}

    def members(net):
        return sorted({r for r, pins in e["pins"].items() for v in pins.values() if v["net"] == net})
    u5 = e["components"]["U5"]
    facts = [
        ("U5 pins 32 (CSNIN), 33 (CSPIN) and 34 (VIN) all on PV_P: the input-current sense is tied off, so as drawn no input "
         "limit acts (8705af p.12, p.31)", [nets("U5")[k] for k in ("32", "33", "34")] == ["PV_P"] * 3),
        ("U5 pin 38 (IMON_IN) on TRK_IMONI with R16 alone, 10k, and no CIMON_IN", members("TRK_IMONI") == ["R16", "U5"]
         and e["components"]["R16"]["value"] == "10k"),
        ("U5 pins 29 to 31 (EXTVCC, CSNOUT, CSPOUT) on TRK_OUT: INTVCC is regulated from the output (8705af p.32)",
         [nets("U5")[k] for k in ("29", "30", "31")] == ["TRK_OUT"] * 3),
        ("U5's LCSC field %s and its land %s" % (u5["fields"].get("LCSC"), u5["footprint"].split(":")[1]),
         u5["fields"].get("LCSC") == "C674164" and "QFN-38" in u5["footprint"]),
        ("R8 102k 1% from PV_P to TRK_FBIN, R9 7.50k 1% to GND", e["components"]["R8"]["value"].startswith("102k 1%")
         and nets("R8") == {"1": "PV_P", "2": "TRK_FBIN"} and e["components"]["R9"]["value"].startswith("7.50k 1%")
         and nets("R9") == {"1": "TRK_FBIN", "2": "GND"}),
        ("R12 215k (RT), the oscillator's 202 kHz row", e["components"]["R12"]["value"].startswith("215k")),
        ("Q3 and Q5 BSC028N06NS (M1, M3), Q4 and Q6 BSC039N06NS (M2, M4)", all("BSC028N06NS" in e["components"][q]["value"] for q in ("Q3", "Q5"))
         and all("BSC039N06NS" in e["components"][q]["value"] for q in ("Q4", "Q6"))),
        ("PV_P carries F2, D4, the bulk C11 to C15, C64, Q3's drain, R8, R14, TP5 and U5", members("PV_P") ==
         ["C11", "C12", "C13", "C14", "C15", "C64", "D4", "F2", "Q3", "R14", "R8", "TP5", "U5"]),
    ]
    bad = [f for f, ok in facts if not ok]
    if bad:
        refuse(3, "a netlist fact does not hold: %s" % bad)
    R["facts"] = [f for f, _ in facts]
    gse = open(os.path.join(TOP, GEN_E), encoding="utf-8").read()
    r10 = need(gse, r'r\("R10", "(\d+)k 1% \(RFBOUT1', "gen_sch_e.py R10").group(1)
    R["r10_gen"] = r10

    # ================================================================== 2: the makers' rows
    p2, p3, p6, p6r = flat(pg(LT, 2, False)), pg(LT, 3), flat(pg(LT, 6)), flat(pg(LT, 6, False))
    order = {}
    for ln in p3.split("\n"):
        m = re.match(r"(LT8705A(E|I|H|MP)(UHF|FE)#PBF)\s+\S+\s+\S+\s+(.*?)\s{2,}([\u2013-]\d+)\u00b0C to (\d+)\u00b0C", ln)
        if m:
            order.setdefault(m.group(2), []).append((m.group(3), m.group(1), int(m.group(5).replace("\u2013", "-")), int(m.group(6))))
    if sorted(order) != ["E", "H", "I", "MP"]:
        refuse(3, "8705af p.3's order table does not read as four grades: %s" % sorted(order))
    qfn = {g for g, rows in order.items() if any(pk == "UHF" for pk, *_ in rows)}
    note3 = need(p6r, r"Note 3: The LT8705AE is guaranteed to meet performance specifications from 0\u00b0C to 125\u00b0C junction "
                 r"temperature\. Specifications over the [\u2013-]40\u00b0C to 125\u00b0C operating junction temperature range are "
                 r"assured by design, characterization and correlation with statistical process controls\. The LT8705AI is "
                 r"guaranteed over the full [\u2013-]40\u00b0C to 125\u00b0C junction temperature range\.", "8705af p.6 Note 3").group(0)
    tja = float(need(p2, r"UHF PACKAGE 38-LEAD \(5mm \u00d7 7mm\) PLASTIC QFN TJMAX = 125\u00b0C, \u03b8JA = (\d+)\u00b0C/W", "8705af p.2 QFN theta-JA").group(1))
    iq = float(need(flat(p3), r"VIN Quiescent Current Not Switching, VEXTVCC = 0 [\d.]+ ([\d.]+) mA", "8705af p.3 VIN quiescent maximum").group(1))
    fosc = need(p6, r"RT = 215k l (\d+) (\d+) (\d+) kHz", "8705af p.6 fOSC at RT 215k").groups()
    f_max = float(fosc[2]) * 1e3
    pages = {n: RP.pdf_lines(LT, n) for n in (2, 3, 4, 5, 6)}
    ref_p = RP.ec_row(pages, 4, "Regulation Voltages for IMON_IN and IMON_OUT", None)
    line_p = RP.ec_row(pages, 4, "Line Regulation for IMON_IN and IMON_OUT Error Amp", None)["max"]
    a7 = {g: RP.ec_row(pages, 5, "VCSPIN-CSNIN to IMON_IN Amplifier A7 gm", g) for g in ("(All Grades)", "(LT8705AE, LT8705AI)", "(LT8705AH, LT8705AMP)")}
    ea2 = RP.ec_row(pages, 5, "IMON_IN Error Amp EA2 Voltage Gain", None)["typ"]
    fbin = RP.ec_row(pages, 4, "Regulation Voltage for FBIN", "(LT8705AE, LT8705AI)")
    ea3 = RP.ec_row(pages, 4, "FBIN Error Amp EA3 Voltage Gain", None)["typ"]
    iovm = RP.ec_row(pages, 5, "IMON_IN Overvoltage Threshold", None)
    ioutmin = RP.ec_row(pages, 5, "IMON_IN Maximum Output Current", None)["min"]
    csd = RP.ec_row(pages, 5, "CSPIN, CSNIN Differential Operating Voltage Range", None)
    # the replay's own reading must be the same (its locals)
    if (ref_p, line_p) != (LR["ref_p"], LR["line_p"]) or LR["fb_p"][0] != fbin or abs(LR["dvc"] - 1.5) > 1e-12:
        refuse(4, "this record's read of 8705af differs from the replay's")
    p31 = flat(pg(LT, 31, False))
    need(p31, r"IMON_IN voltages exceeding 1\.208V \(typical\) cause the VC voltage to reduce, thus limiting the inductor and input currents", "p.31 the limit")
    cim = need(p31, r"CIMON_IN should be chosen by the equation:\W*(\d+)\W*F CIMON_IN >", "p.31 CIMON_IN's minimum").group(1)
    need(p31, r"bringing the CIMON_IN total to 0\.1\u03bcF to 1\u03bcF, may be necessary to maintain loop stability if the IMON_IN pin is used in a constant-current regulation loop", "p.31 CIMON_IN 0.1 to 1 uF")
    need(flat(pg(LT, 30, False)), r"do not place resistors in series with any of the CSxIN or CSxOUT pins", "p.30 no series resistance")
    need(flat(pg(LT, 32, False)), r"INTVCC is regulated by the EXTVCC LDO instead", "p.32 INTVCC from EXTVCC")
    need(flat(pg(LT, 34, False)), r"The actual die temperature can deviate from the above equation by \u00b110\u00b0C", "p.34 the CLKOUT junction method")
    R.update(order=order, qfn=sorted(qfn), note3=note3.replace("\u2013", "-"), tja=tja, iq=iq * 1e-3, f_max=f_max, ref_p=ref_p, line_p=line_p, a7=a7,
             ea2=ea2, fbin=fbin, ea3=ea3, iovm=iovm, ioutmin=ioutmin, csd=csd, cim=float(cim))
    # Milliohm HoJLR2512 series sheet (Ho-A0)
    h1, h2, h4 = flat(pg(HOJ, 1)), flat(pg(HOJ, 2)), flat(pg(HOJ, 4))
    need(h1, r"F=\u00b11%", "HoJLR p.1 the F tolerance code")
    tcr_h = float(need(h2, r"T\.C\.R \( ppm / \u2103 \) \u00b1(\d+) \(2mR~500mR\)", "HoJLR p.2 TCR").group(1)) * 1e-6
    need(h2, r"Operating Temperature Range -50\u2103~\+170\u2103", "HoJLR p.2 operating range")
    tcr_h_span = need(h4, r"Temperature Coefficient IEC60115-1-4\.8 JIS-C5201-4\.8 \+25\u2103 ~ \+125\u2103", "HoJLR p.4 the TCR test span").group(0)
    life_h = float(need(h4, r"Load Life JIS-C5201-4\.25\.1 < \u00b1(\d+)%", "HoJLR p.4 load life").group(1)) / 100.0
    sold_h = float(need(h4, r"Resistance to Soldering IEC60115-1-4\.18 260\u00b15\u2103 for 10\u00b11 sec < \u00b1([\d.]+)%", "HoJLR p.4 soldering heat").group(1)) / 100.0
    k_r = (170.0 - 70.0) / 3.0         # INFERRED, as r11_dep.py: the derating line, 3 W at 70 C to 0 at 170 C (p.2), in K/W
    need(h2, r"70\u2103", "HoJLR p.2 the derating onset")
    # YAGEO RT series V.16 (held)
    y2, y5, y7, y8 = flat(pg(RT, 2)), flat(pg(RT, 5)), flat(pg(RT, 7)), flat(pg(RT, 8))
    tol_y = float(need(y2, r"B = \u00b1 ([\d.]+)%", "RT p.2 tolerance B").group(1)) / 100.0
    tcr_y = float(need(y2, r"D = (\d+) ppm/\u00b0C", "RT p.2 TCR D").group(1)) * 1e-6
    need(y2, r"R = Paper/PE taping reel", "RT p.2 packaging R")
    need(flat(pg(RT, 7)), r"At \+25/\u201355 \u00b0C and \+25/\+125 \u00b0C", "RT p.7 the TCR test span")
    life_y = need(y7, r"Life/Endurance IEC 60115-1 4\.25\.1 At 70\u00b1 5 \u00b0C for 1,000 hours, rated voltage applied \u00b1 \(([\d.]+)%\+([\d.]+) \u03a9\)", "RT p.7 life").groups()
    sold_y = need(y8, r"Resistance to IEC 60115-1 4\.18 Condition B, no pre-heat of samples\. \u00b1 \(([\d.]+)%\+([\d.]+) \u03a9\)",
                  "RT p.8 soldering heat").groups()
    need(y5, r"RT0603 1/10W 75V 150V", "RT p.5 the RT0603 row")
    # Infineon gate charges (maximum, VGS 0 to 10 V)
    qg039 = float(need(flat(pg(BSC039, 4)), r"Gate charge total 1\) Qg - \d+ (\d+) nC VDD=30\W?V,\W?ID=50\W?A,\W?VGS=0\W?to\W?10\W?V", "BSC039N06NS p.4 Qg").group(1)) * 1e-9
    qg028 = float(need(flat(pg(BSC028, 3)), r"Gate charge total Qg (\d+) (\d+) (\d+)", "BSC028N06NS p.3 Qg").group(3)) * 1e-9
    need(flat(pg(BSC028, 3)), r"V GS=0 to 10 V", "BSC028N06NS p.3 the gate charge's VGS")
    R.update(tcr_h=tcr_h, tcr_h_span=tcr_h_span, life_h=life_h, sold_h=sold_h, k_r=k_r, tol_y=tol_y, tcr_y=tcr_y,
             life_y=(float(life_y[0]) / 100.0, float(life_y[1])), sold_y=(float(sold_y[0]) / 100.0, float(sold_y[1])), qg039=qg039, qg028=qg028)
    # the envelope (as r11_dep.py reads it)
    import yaml
    env = yaml.safe_load(open(os.path.join(TOP, ENV), encoding="utf-8"))
    t_air = max(env["worst_inside_air_c"]["lid_open"], env["worst_inside_air_c"]["lid_closed"])
    t_cold = env["ambient_c"]["in_use"]["min"]
    t_amb_hi = env["ambient_c"]["in_use"]["max"]
    R.update(t_air=t_air, t_cold=t_cold, t_amb_hi=t_amb_hi)
    # L4-E5's raised ceiling, from its reproduced record (0b)
    o5 = out5.decode("utf-8")
    m5 = need(o5, r"so E96 (\d+) k: ceiling ([\d.]+) / ([\d.]+) / ([\d.]+) V", "l4e5_source_control.out the tracker's raised ceiling")
    R["r10_5"], R["ceil5"] = m5.group(1), tuple(float(m5.group(i)) for i in (2, 3, 4))
    R["out_drawn"] = tuple(float(x) for x in need(o5, r"([\d.]+) / ([\d.]+) / ([\d.]+) V: FBOUT [\d.]+ / [\d.]+ / [\d.]+ V, MAKER 8705af p\.4",
                                                  "l4e5_source_control.out the drawn output band").groups())

    # ================================================================== 3: the catalogue (filed readings) and the choices
    lc = {c: catalogue(c) for c in ("C674164", "C674169", "C674170", "C148250")}

    def verify_rt(code, val):
        """A chosen RT0603BRD07 value must have its own filed LCSC reading, naming the same value, 0.1 % and 25 ppm/K, and
        linking the held RT sheet."""
        c = catalogue(code)
        lc[code] = c
        if rvalue(c["model"]) != val or c["params"].get("Tolerance") != "\u00b10.1%" or c["params"].get("Temperature Coefficient") != "\u00b125ppm/\u2103" \
                or c["pdf_sha256"] != PINS[RT]:
            refuse(3, "the filed reading of %s is not the chosen %.0f Ohm RT0603BRD07 part" % (code, val))
    if lc["C674164"]["model"] != "LT8705AEUHF#TRPBF" or lc["C674169"]["model"] != "LT8705AIUHF#PBF" or lc["C674170"]["model"] != "LT8705AIUHF#TRPBF":
        refuse(3, "the LT8705A catalogue readings are not the grades named")
    if any(lc[c]["pdf_sha256"] != PINS[LT] for c in ("C674164", "C674169", "C674170")):
        refuse(3, "LCSC's sheet for the LT8705A codes is not the filed 8705af")
    hoj = json.load(open(os.path.join(TOP, INP_L4E4), encoding="utf-8"))["rows"]
    rtj = json.load(open(os.path.join(TOP, INP, "jlc-search-rt0603brd07-2026-10-01.json"), encoding="utf-8"))["rows"]

    # the IC grade (SESSION, below): the drawn land is the QFN; H and MP exist only in the TSSOP (p.3)
    grade = "I"
    if grade not in qfn or "H" in qfn or "MP" in qfn:
        refuse(4, "the grade reasoning's premise (only E and I in the QFN) does not hold")
    gm_lo, gm_hi = a7["(LT8705AE, LT8705AI)"]["min"], a7["(LT8705AE, LT8705AI)"]["max"]
    if not (gm_lo <= a7["(All Grades)"]["min"] and a7["(All Grades)"]["max"] <= gm_hi):
        refuse(4, "A7's 25 C limits are not inside the I grade's full-range limits")
    R.update(grade=grade, gm_lo=gm_lo, gm_hi=gm_hi)

    # RSENSE1: the HoJLR2512-3W value that puts the zero-margin limit nearest A7's printed 50 mV test point (p.5)
    vref_n = ref_p["typ"]
    dvc = LR["dvc"]

    def corner_k(v, gain, lmul, rs_lo, rm_lo):
        """I_lim / I_nom at v, every term at the end that raises the current (the replay's i_factor)."""
        return RP.i_factor(v, ref_p["max"], vref_n, line_p * lmul, 1, dvc / gain, 1, gm_lo, rs_lo, rm_lo)

    def low_k(v, gain, lmul, rs_hi, rm_hi):
        return RP.i_factor(v, ref_p["min"], vref_n, line_p * lmul, -1, dvc / gain, -1, gm_hi, rs_hi, rm_hi)
    v_oc, p_win = LR["v_oc"], LR["p_win"]

    def rfac(tol, tcr, dt, life=0.0, sold=0.0, sgn=-1):
        return (1 + sgn * tol) * (1 + sgn * tcr * abs(dt)) * (1 + sgn * life) * (1 + sgn * sold)
    i_zero = p_win / v_oc / corner_k(v_oc, ea2, 1.0, rfac(0.01, tcr_h, t_cold - 25.0), rfac(tol_y, tcr_y, t_cold - 25.0))
    hoj_ok = [(float(re.search(r"-([\d.]+)mR-1%", r_["model"]).group(1)) * 1e-3, r_["code"], r_["stock"]) for r_ in hoj
              if re.search(r"HoJLR2512-3W-[\d.]+mR-1%$", r_["model"]) and r_["stock"] >= STOCK_MIN]
    rs, rs_code, rs_stock = min(hoj_ok, key=lambda t: (abs(t[0] * i_zero - 0.050), t[0]))
    lc[rs_code] = catalogue(rs_code)
    if lc[rs_code]["model"] != "HoJLR2512-3W-%gmR-1%%" % (rs * 1e3) or lc[rs_code]["pdf_sha256"] != PINS[HOJ]:
        refuse(3, "the filed reading of %s is not the chosen RSENSE1" % rs_code)
    tol_h = float(lc[rs_code]["params"]["Tolerance"].strip("\u00b1%")) / 100.0

    # the two temperature ends: every part at the in-use minimum (a cold start, no self-heating); the hot end at the worst
    # inside air, RSENSE1 plus its own rise at the highest current the limit passes, by the derating line (INFERRED)
    def ends(i_nom_, rm_val):
        """(label, RSENSE1's temperature, RIMON_IN's (and R8's, R9's) temperature, the air, RSENSE1's watts). The hot end's
        RSENSE1 carries the most current the limit can pass (the stack under the design floor with drifts) and sits above the
        air by the derating line's K/W, iterated to its fixed point (INFERRED)."""
        t = t_air
        for _ in range(30):
            i_hi = i_nom_ * corner_k(v_oc, ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, rfac(tol_h, tcr_h, t - 25.0, life_h, sold_h),
                                     rfac(tol_y, tcr_y, t_air - 25.0, R["life_y"][0] + R["life_y"][1] / rm_val, R["sold_y"][0] + R["sold_y"][1] / rm_val))
            p_rs = i_hi ** 2 * rs * (1 + tol_h) * (1 + tcr_h * (t - 25.0))
            t = t_air + p_rs * k_r
        return (("the cold end", t_cold, t_cold, t_cold, 0.0), ("the hot end", t, t_air, t_air, p_rs))

    # RIMON_IN: the largest stocked RT0603BRD07 setting whose corner passes at both ends under the SESSION floor
    def stack(rm_val, end, floor, drifts, i_nom):
        _lab, t_rs, t_rm, _t3, _p = end
        rs_lo = rfac(tol_h, tcr_h, t_rs - 25.0, life_h if drifts else 0.0, sold_h if drifts else 0.0)
        rm_lo = rfac(tol_y, tcr_y, t_rm - 25.0, (R["life_y"][0] + R["life_y"][1] / rm_val) if drifts else 0.0,
                     (R["sold_y"][0] + R["sold_y"][1] / rm_val) if drifts else 0.0)
        gain = ea2 / EA2_FLOOR_DIV if floor else ea2
        lmul = LINE_FLOOR_MUL if floor else 1.0
        return v_oc * i_nom * corner_k(v_oc, gain, lmul, rs_lo, rm_lo)
    cands = sorted({(rvalue(r_["model"]), r_["code"], r_["stock"]) for r_ in rtj if rvalue(r_["model"]) and 20e3 <= rvalue(r_["model"]) < 30e3})
    rows_rm = []
    for rm_val, code, stock in cands:
        i_nom = vref_n / (a7["(All Grades)"]["typ"] * 1e-3 * rs * rm_val)
        e2 = ends(i_nom, rm_val)
        worst_floor = max(stack(rm_val, en, True, True, i_nom) for en in e2)
        worst_typ = max(stack(rm_val, en, False, False, i_nom) for en in e2)
        rows_rm.append((rm_val, code, stock, i_nom, worst_typ, worst_floor))
    ok_rm = [r_ for r_ in rows_rm if r_[2] >= STOCK_MIN and r_[5] <= p_win + 1e-9]
    if not ok_rm:
        refuse(4, "BLOCKER: no stocked RIMON_IN passes the corner under the design floor")
    rm, rm_code, rm_stock, i_nom = min(ok_rm, key=lambda t: t[0])[:4]
    verify_rt(rm_code, rm)
    R.update(rs=rs, rs_code=rs_code, rs_stock=rs_stock, tol_h=tol_h, rm=rm, rm_code=rm_code, rm_stock=rm_stock, i_nom=i_nom, i_zero=i_zero,
             rows_rm=rows_rm)
    END = ends(i_nom, rm)
    R["ends"] = END

    # ================================================================== 4: the hold (R8 and R9), REQ-016's 17.6 V point kept
    hold, trace, dsp = LR["hold"], LR["trace"], LR["dsp"]
    r8n, r9n = LR["r8"], LR["r9"]

    def band(r8v, r9v, ea3div, drifts=False):
        """The hold's lowest, nominal and highest over both ends: FBIN's I-grade limits (p.4), its line regulation, the EA3
        allowance at its gain / ea3div, the FBIN bias, and R8 and R9 at 0.1 % and 25 ppm/K (and their drifts when asked), through
        the replay's own hold()."""
        los, his = [], []
        for _lab, _t_rs, t_rm, _t3, _p in END:
            dt = t_rm - 25.0
            for s8, s9 in itertools.product((-1, 1), (-1, 1)):
                k8 = r8v / (r8n * 1e3) * rfac(tol_y, tcr_y, dt, (R["life_y"][0] + R["life_y"][1] / r8v) if drifts else 0.0,
                                               (R["sold_y"][0] + R["sold_y"][1] / r8v) if drifts else 0.0, s8)
                k9 = r9v / (r9n * 1e3) * rfac(tol_y, tcr_y, dt, (R["life_y"][0] + R["life_y"][1] / r9v) if drifts else 0.0,
                                               (R["sold_y"][0] + R["sold_y"][1] / r9v) if drifts else 0.0, s9)
                los.append(hold(fbin["min"], -1, -ea3div, k8, k9, LR["fbbias_p"]))
                his.append(hold(fbin["max"], 1, ea3div, k8, k9, 0.0))
        return min(los), hold(fbin["typ"], 0, 0, r8v / (r8n * 1e3), r9v / (r9n * 1e3), 0.0), max(his)
    e_at = {}

    def energy(v, lim=None):
        if lim is None:
            k = round(v, 6)
            if k not in e_at:
                e_at[k] = trace(dsp, v, None)
            return e_at[k]
        return trace(dsp, v, lim)
    # REQ-016 (approved) holds the panel at 17.6 V, and D-34 keeps REQ-016's window unchanged unless the owner rules otherwise
    # (check astra-check-l4e7-1, B1): the hold keeps the drawn nominal ratio. SESSION: R8 and R9 at their drawn values as the
    # RT0603BRD07 parts (0.1 %, 25 ppm/K) with the most stock; only tolerance and drift change.
    reqs = open(os.path.join(TOP, REQS), encoding="utf-8").read()
    r016 = " ".join(reqs.split("  - id: REQ-016\n", 1)[1].split("\n  - id: ", 1)[0].split())
    need(r016, r"the panel held at 17\.6 V by the stage's input regulation", "REQ-016's 17.6 V hold")
    need(r016, r"the FBIN divider R8 and R9 sets the 17\.6 V operating point", "REQ-016's acceptance on R8 and R9")
    d34 = " ".join(reqs.split("  - id: D-34\n", 1)[1].split("\n  - id: ", 1)[0].split())
    need(d34, r"authority: OWNER", "D-34's authority")
    need(d34, r"REQ-016's approved solar window stays unchanged", "D-34's ruling")
    r8v, r9v = r8n * 1e3, r9n * 1e3

    def stocked(val):
        rows = [(r_["stock"], r_["code"]) for r_ in rtj if rvalue(r_["model"]) == val and r_["stock"] >= STOCK_MIN]
        if not rows:
            refuse(4, "BLOCKER: no stocked RT0603BRD07 part at %.0f Ohm" % val)
        return max(rows)[1]
    r8c, r9c = stocked(r8v), stocked(r9v)
    for code, val in ((r8c, r8v), (r9c, r9v)):
        verify_rt(code, val)
    hb = band(r8v, r9v, 1.0)                                  # EA3 at its typical, tolerance and TCR
    hb4 = band(r8v, r9v, 1.0, drifts=True)                    # EA3 at its typical, with the soldering and life drifts
    hb2 = band(r8v, r9v, EA2_FLOOR_DIV)                       # EA3 at half its typical
    hb3 = band(r8v, r9v, EA2_FLOOR_DIV, drifts=True)          # EA3 at half, with the drifts: the widest conditioned band
    # the drawn circuit (check astra-check-l4e7-1, M1): the replay's band takes H and MP's FBIN minimum; with the E grade's
    # (the netlist's C674164) and the replay's other terms, 1 % resistors
    rt_ = RP.R_TOL
    drawn_e_lo = min(hold(fbin["min"], -1, -1, s8, s9, LR["fbbias_p"]) for s8 in (1 - rt_, 1 + rt_) for s9 in (1 - rt_, 1 + rt_))
    # the FBIN bias as an energy sensitivity (check M2): the lower corner (EA3 typical) with no bias, the typical and ten times it
    k8lo = rfac(tol_y, tcr_y, t_cold - 25.0, sgn=-1)
    k9hi = rfac(tol_y, tcr_y, t_cold - 25.0, sgn=1)
    bias_rows = []
    for mult in (0.0, 1.0, 10.0):
        lo_b = min(hold(fbin["min"], -1, -1, s8 * r8v / (r8n * 1e3), s9 * r9v / (r9n * 1e3), LR["fbbias_p"] * mult)
                   for s8 in (k8lo, rfac(tol_y, tcr_y, t_air - 25.0, sgn=-1)) for s9 in (k9hi, rfac(tol_y, tcr_y, t_air - 25.0, sgn=1)))
        bias_rows.append((mult * LR["fbbias_p"], lo_b, sum(energy(lo_b)[0])))
    R.update(r8v=r8v, r9v=r9v, r8c=r8c, r9c=r9c, hb=hb, hb2=hb2, hb3=hb3, hb4=hb4, drawn_e_lo=drawn_e_lo, bias_rows=bias_rows,
             fbin_hmp_min=LR["fb_p"][1]["min"],
             hold_drawn=(LR["v_lo"], LR["v_nom_hold"], LR["v_hi_hold"]), stock={r_["code"]: r_["stock"] for r_ in rtj})

    # THE PROPOSAL, NOT ADOPTED: a lower hold would change REQ-016's 17.6 V point and needs the owner's ruling (D-34). Nothing
    # below depends on it and no draft carries it: the stocked pair whose band's worse end gives the most energy on SC-37's day.
    r8s = sorted({(rvalue(r_["model"]), r_["code"], r_["stock"]) for r_ in rtj if rvalue(r_["model"]) and 90e3 <= rvalue(r_["model"]) < 120e3 and r_["stock"] >= STOCK_MIN})
    r9s = sorted({(rvalue(r_["model"]), r_["code"], r_["stock"]) for r_ in rtj if rvalue(r_["model"]) and 6e3 <= rvalue(r_["model"]) < 10e3 and r_["stock"] >= STOCK_MIN})
    hold_rows = []
    for (a8, c8, s8_), (a9, c9, s9_) in itertools.product(r8s, r9s):
        nom = fbin["typ"] * (1 + a8 / a9)
        if not (HOLD_RANGE[0] <= nom <= HOLD_RANGE[1]):
            continue
        lo, nm, hi = band(a8, a9, 1.0)
        elo, ehi = sum(energy(lo)[0]), sum(energy(hi)[0])
        hold_rows.append((round(min(elo, ehi), 1), -min(s8_, s9_), a8, a9, c8, c9, lo, nm, hi, elo, ehi))
    hold_rows.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    pb = hold_rows[0]
    R["proposal"] = dict(r8=pb[2], r9=pb[3], c8=pb[4], c9=pb[5], band=(pb[6], pb[7], pb[8]), e_band=(pb[9], sum(energy(pb[7])[0]), pb[10]),
                         e_nom_kept=sum(energy(hb[1])[0]), n=len(hold_rows))
    # the hourly maximum-power voltage on SC-37's day (the model's own), for the hold's reason
    AC = LR["AC"]
    vmpp = [dsp.mpp(LR["prof0"][h], AC.t_cell(LR["TA40"][h], LR["prof0"][h], LR["noct"]))[0] for h in range(24) if LR["prof0"][h] >= 100.0]
    R["vmpp"] = (min(vmpp), max(vmpp))

    # ================================================================== 5: THE CORNER CHECK on the achieved values
    v_lo_env = min(hb[0], hb2[0], hb3[0], hb4[0])         # the widest conditioned band's lowest (check M3)
    grid = sorted(set([v_lo_env, v_oc] + [round(v_lo_env + V_STEP * k, 6) for k in range(int((v_oc - v_lo_env) / V_STEP) + 1)]))
    grid = [v for v in grid if v_lo_env - 1e-12 <= v <= v_oc + 1e-12]

    def check(gain, lmul, drifts, tcr_cold_h=None):
        """Every vertex at every grid voltage at one end: the reference, its line term's sign, A7, the two resistors' ends and
        the EA2 term's sign. Returns, per end, the worst (power, voltage, vertex) and the corner count."""
        out = []
        for lab, t_rs, t_rm, _t3, _p in END:
            th = tcr_cold_h if (tcr_cold_h is not None and t_rs < 25.0) else tcr_h
            rs_e = [rfac(tol_h, th, t_rs - 25.0, life_h if drifts else 0.0, sold_h if drifts else 0.0, s) for s in (-1, 1)]
            rm_e = [rfac(tol_y, tcr_y, t_rm - 25.0, (R["life_y"][0] + R["life_y"][1] / rm) if drifts else 0.0,
                         (R["sold_y"][0] + R["sold_y"][1] / rm) if drifts else 0.0, s) for s in (-1, 1)]
            worst, n = None, 0
            for vref, ls, gm, r1, r2, es in itertools.product((ref_p["min"], ref_p["max"]), (-1, 1), (gm_lo, gm_hi), rs_e, rm_e, (-1, 1)):
                for v in grid:
                    pw = v * i_nom * RP.i_factor(v, vref, vref_n, line_p * lmul, ls, (dvc / gain) if gain else 0.0, es, gm, r1, r2)
                    n += 1
                    if worst is None or pw > worst[0]:
                        worst = (pw, v, vref, ls, gm, r1, r2, es)
            out.append((lab, worst, n))
        return out
    main_chk = check(ea2, 1.0, False)
    for lab, w, _n in main_chk:
        if w[0] > p_win + 1e-9:
            refuse(4, "the achieved setting %.4f A takes %.4f W at %.3f V (%s): over REQ-016's %.0f W" % (i_nom, w[0], w[1], lab, p_win))
    R["main_chk"] = main_chk
    R["chk_printed"] = check(None, 0.0, False)          # the two unprinted rows left out: what the printed rows alone give
    R["chk_floor"] = check(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True)
    R["chk_drift"] = check(ea2, 1.0, True)
    for lab, w, _n in R["chk_floor"]:
        if w[0] > p_win + 1e-9:
            refuse(4, "the setting fails its own design floor at %s" % lab)

    def breakeven_gain(lmul, drifts, end_i):
        lab, t_rs, t_rm, _t3, _p = END[end_i]
        rs_lo = rfac(tol_h, tcr_h, t_rs - 25.0, life_h if drifts else 0.0, sold_h if drifts else 0.0)
        rm_lo = rfac(tol_y, tcr_y, t_rm - 25.0, (R["life_y"][0] + R["life_y"][1] / rm) if drifts else 0.0,
                     (R["sold_y"][0] + R["sold_y"][1] / rm) if drifts else 0.0)
        f = lambda g: v_oc * i_nom * corner_k(v_oc, g, lmul, rs_lo, rm_lo)
        if v_oc * i_nom * RP.i_factor(v_oc, ref_p["max"], vref_n, line_p * lmul, 1, 0.0, 1, gm_lo, rs_lo, rm_lo) > p_win:
            return None
        lo, hi = 0.01, 1e6
        for _ in range(200):
            mid = math.sqrt(lo * hi)
            if f(mid) > p_win:
                lo = mid
            else:
                hi = mid
        return hi
    R["be_gain"] = {(lm, dr): [breakeven_gain(lm, dr, k) for k in range(2)] for lm in (1.0, 2.0, 5.0, 10.0) for dr in (False, True)}

    def breakeven_line(gain):
        lab, t_rs, t_rm, _t3, _p = END[0]
        rs_lo, rm_lo = rfac(tol_h, tcr_h, t_rs - 25.0), rfac(tol_y, tcr_y, t_rm - 25.0)
        lo, hi = 0.0, 1e4
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if v_oc * i_nom * corner_k(v_oc, gain, mid, rs_lo, rm_lo) > p_win:
                hi = mid
            else:
                lo = mid
        return lo
    R["be_line"] = (breakeven_line(ea2), breakeven_line(ea2 / EA2_FLOOR_DIV))

    def breakeven_tcr_cold(gain, lmul, drifts):
        """RSENSE1's TCR below 25 C at which the cold 25 V corner (the worst, above) reaches 100 W under the named stack (check
        M2: each break-even states its stack); searched up to 10000 ppm/K, inside which the low end (1 - TCR x 45 K) stays positive
        and the power rises with the TCR."""
        dt = abs(END[0][1] - 25.0)
        rm_lo = rfac(tol_y, tcr_y, END[0][2] - 25.0, (R["life_y"][0] + R["life_y"][1] / rm) if drifts else 0.0,
                     (R["sold_y"][0] + R["sold_y"][1] / rm) if drifts else 0.0)
        f = lambda tc: v_oc * i_nom * corner_k(v_oc, gain, lmul, rfac(tol_h, tc, dt, life_h if drifts else 0.0, sold_h if drifts else 0.0), rm_lo)
        if f(0.01) <= p_win:
            return None
        lo, hi = 0.0, 0.01
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if f(mid) > p_win:
                hi = mid
            else:
                lo = mid
        return lo
    R["be_tcr_cold"] = breakeven_tcr_cold(ea2, 1.0, False)                                   # stack A
    R["be_tcr_cold_floor"] = breakeven_tcr_cold(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True)   # stack C, the design floor
    # the old setting on the achieved parts (information): 3.548 A on the replay's 1 mA grid, with these parts
    R["old_on_parts"] = max(v_oc * LR["i_set"] * corner_k(v_oc, ea2, 1.0, rfac(tol_h, tcr_h, en[1] - 25.0), rfac(tol_y, tcr_y, en[2] - 25.0)) for en in END)

    # ================================================================== 6: the conditions the mechanism needs (CONDITION rows)
    vd_lim_hi = i_nom * max(corner_k(v_oc, ea2, 1.0, 1.0, 1.0), 1.0) * rs * (1 + tol_h)
    dt_max = max(abs(en[1] - 25.0) for en in END)
    v_fault_max = iovm["max"] / (gm_lo * 1e-3 * rm * (1 - tol_y) * (1 - tcr_y * dt_max))       # the sense voltage at which IMON_IN reaches its fault maximum
    i_imon_lim = vd_lim_hi * gm_hi * 1e-3
    cim_min = R["cim"] / (float(fosc[0]) * 1e3 * rm)
    R.update(vd_lim_hi=vd_lim_hi, v_fault_max=v_fault_max, i_imon_lim=i_imon_lim, cim_min=cim_min, tau=rm * 100e-9)
    isc_hot = AC.isc_at(AC.CAND["SPR100"], 70.0)
    R["vd_isc"] = isc_hot * rs * (1 + tol_h) * (1 + tcr_h * dt_max)

    # ================================================================== 7: U5's junction (INFERRED) and RSENSE1's rise
    i_g = iq * 1e-3 + f_max * (2 * qg028 + 2 * qg039)
    p_ic = R["ceil5"][2] * i_g
    R.update(i_g=i_g, p_ic=p_ic, tj_hot=t_air + tja * p_ic, tj_hot_old=t_air + tja * R["out_drawn"][2] * i_g, tj_cold=t_cold)

    # ================================================================== 8: the energy (MODELED, the replay's trace and runs)
    lo_h, nom_h, hi_h = hb
    vert = list(itertools.product((ref_p["min"], ref_p["max"]), (-1, 1), (gm_lo, gm_hi), (-1, 1), (-1, 1), (-1, 1)))

    def lim_of(inom, rmv, which, gain=ea2, lmul=1.0):
        def f(v):
            vals = []
            for lab, t_rs, t_rm, _t3, _p in END:
                for a, b, gm, s1, s2, c_ in vert:
                    vals.append(RP.i_factor(v, a, vref_n, line_p * lmul, b, dvc / gain, c_, gm, rfac(tol_h, tcr_h, t_rs - 25.0, sgn=s1),
                                            rfac(tol_y, tcr_y, t_rm - 25.0, sgn=s2)))
            return inom * (min(vals) if which == "lo" else max(vals))
        return f
    # the zero-margin catalogue setting: the largest stocked value passing at the typical rows (no floor, no drifts)
    zero = min([r_ for r_ in rows_rm if r_[2] >= STOCK_MIN and r_[4] <= p_win + 1e-9], key=lambda t: t[0])
    R["zero"] = zero
    grid_e = []
    for hl, vh in (("lower hold corner", lo_h), ("nominal hold", nom_h), ("upper hold corner", hi_h),
                   ("lower, EA3 at its floor", hb2[0]), ("upper, EA3 at its floor", hb2[2]),
                   ("lower, EA3 floor, drifts", hb3[0]), ("upper, EA3 floor, drifts", hb3[2])):
        row = [hl, vh, sum(energy(vh)[0])]
        for inom, rmv in ((i_nom, rm), (zero[3], zero[0])):
            for which in ("lo", "nom", "hi"):
                lim = (lambda v, i=inom: i) if which == "nom" else lim_of(inom, rmv, which)
                tr, nl = energy(vh, lim)
                row.append((sum(tr), nl, tr))
        grid_e.append(row)
    R["grid_e"] = [(r_[0], r_[1], r_[2]) + tuple((x[0], x[1]) for x in r_[3:]) for r_ in grid_e]
    R["e_mpp"] = LR["e_mpp"]
    # the irradiance at which the limit's lowest begins to bind at the hold's nominal and lower corner (hour 12's air)
    ta12 = LR["TA40"][12]
    gb = []
    for inom, rmv in ((i_nom, rm), (zero[3], zero[0])):
        for vh in (lo_h, nom_h):
            lim = lim_of(inom, rmv, "lo")(vh)
            g_lo, g_hi = 50.0, 1500.0
            for _ in range(60):
                g = 0.5 * (g_lo + g_hi)
                if dsp.current(vh, g, AC.t_cell(ta12, g, LR["noct"]), LR["rl"]) > lim:
                    g_hi = g
                else:
                    g_lo = g
            gb.append((inom, vh, lim, g_hi))
    R["g_bind"], R["ta12"] = gb, ta12
    # A1 and A2 on the new traces, exactly as the replay's section 12 runs them (CORRECTED, WE, TYP, the service ledger)
    meanday, least, gs, archs, win = LR["meanday"], LR["least"], LR["gs"], LR["archs"], LR["win_req016"]
    tr_nom = grid_e[1][4][2]                            # the nominal hold, the limit nominal
    cands_w = [(r_[0] + ", limit at its lowest", r_[3][2]) for r_ in grid_e[:3]] + [(r_[0] + ", no limit", energy(r_[1])[0]) for r_ in grid_e[:3]]
    lab_w, tr_w = min(cands_w, key=lambda t: sum(t[1]))
    runs = {}
    tr_cond = energy(hb3[2])[0]                          # the conditioned envelope's upper end (EA3 at half, drifts): information
    for lab, tr in (("NEW nominal (hold %.3f V, limit %.3f A)" % (nom_h, i_nom), tr_nom), ("NEW least-energy corner (%s)" % lab_w, tr_w),
                    ("NEW conditioned upper end (%.3f V: EA3 at half, the resistors' drifts; information)" % hb3[2], tr_cond)):
        for ak, _alab, n in archs:
            r_ = [meanday(ak, "WE", n, "TYP", h, win, collapse=False, gser=gs(tr), wp=100.0, ratio=1.0) for h in (48, 72)]
            x = [least(ak, "WE", "TYP", h, win, 1.0, 160.0, 34, collapse=False, gser=gs(tr), wp=100.0, ratio=1.0) for h in (48, 72)]
            kk = "el" if ak == "A2" else "eb"
            add = [(meanday(ak, "WE", x[i], "TYP", h, win, collapse=False, gser=gs(tr), wp=100.0, ratio=1.0)[kk] - r_[i][kk])
                   if x[i] is not None else None for i, h in enumerate((48, 72))]
            runs[(lab, ak)] = (sum(tr), r_[1]["stops"], r_[0]["uns"], r_[1]["uns"], add)
    R["runs"] = runs
    old = {}
    for k, (r_, add) in LR["ctr"].items():
        if k[0].startswith("CORRECTED, WE; O-2 nominal") or k[0].startswith("CORRECTED, WE; the least-energy corner"):
            old[(k[0].split(" (")[0] if "O-2 nominal" in k[0] else "CORRECTED, WE; the least-energy corner", k[1])] = (r_[1]["stops"], r_[0]["uns"], r_[1]["uns"], add)
    R["old_runs"] = old
    R["old_grid"] = [(g_[0], g_[1], g_[2], g_[3], g_[4]) for g_ in LR["grid_rows"]]

    # ================================================================== 10: QUALIFICATION OF THE 100 W BOUND (the owner's instruction,
    # 1 October 2026): each unprinted value classified by the outcome it affects, the sheet searched for a guaranteed limit
    # beyond the electrical table, a conservative assumption and the qualification it needs where none exists, the corners
    # shown to bound the permitted range, and the states outside them made a computed case or a bench obligation.
    ia = json.load(open(os.path.join(TOP, INP, "ia-8705af-20250322064938.json"), encoding="utf-8"))
    if ia["sha256"] != PINS[LT] or ia["url"] != OFFICIAL_URL or ia["snapshot"] != IA_SNAPSHOT:
        refuse(3, "the Internet Archive reading of 8705af is not the held sheet at the official URL")
    raw = {n: flat(pg(LT, n, False)) for n in range(1, 45)}
    if sum(1 for n in raw if "8705af" in raw[n]) != 44:
        refuse(3, "8705af does not print its code on each of its 44 pages")
    R["prov"] = dict(url=ia["url"], snapshot=ia["snapshot"], sha=ia["sha256"], read=ia["read_utc"])
    # what the sheet gives beyond the electrical table (each phrase read back; curves are TYPICAL, p.7 and p.8 headers)
    for n, phrase in ((7, "Feedback Voltages"), (7, "Inductor Current Sense Voltage at Minimum Duty Cycle"),
                      (7, "TA = 25\u00b0C unless otherwise specified"), (8, "Maximum VC vs SS"), (8, "IMON Output Currents"),
                      (8, "TA = 25\u00b0C unless otherwise specified"), (14, "which is the diode-AND of error amplifiers EA1-EA4"),
                      (15, "gradual ramp-up of the inductor current by gradually allowing the VC voltage to rise"),
                      (18, "synchronous switch M4 is held off whenever reverse current in the inductor is detected"),
                      (33, "The loop stability is affected by a number of factors"), (34, "reaches approximately 165\u00b0C")):
        need(raw[n], re.escape(phrase), "8705af p.%d '%s'" % (n, phrase))
    ec = {r_["id"]: r_ for r_ in RP.EC_ROWS}
    unprinted_rows = {k: (ec[k]["page"], ec[k]["full"], ec[k]["min"], ec[k]["typ"], ec[k]["max"]) for k in ("EA2_AV", "EA2_GM", "IMON_LINE", "EA3_AV", "FBIN_BIAS")}
    if any(v[1] for v in unprinted_rows.values()) or any(unprinted_rows[k][2] is not None for k in ("EA2_AV", "EA3_AV", "FBIN_BIAS")):
        refuse(4, "a row taken as unprinted carries a full-range limit or a minimum")
    R["unprinted_rows"] = unprinted_rows
    # (a) monotonicity: P(v) = v I_set F(v); dP/dv = I_set [Vref (1 + ls lam (2v - 12)) + es dVC / G] / (Vref_typ gm r1 r2) at every vertex
    def dpdv_min(gain, lmul):
        lam = line_p * lmul * 1e-2
        return min(a * (1 + ls * lam * (2 * v - V_LINE_REF)) + es * dvc / gain
                   for a in (ref_p["min"], ref_p["max"]) for ls in (-1, 1) for es in (-1, 1) for v in (v_lo_env, v_oc))
    V_LINE_REF = RP.V_LINE_REF
    R["dpdv"] = (dpdv_min(ea2, 1.0), dpdv_min(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL))
    if min(R["dpdv"]) <= 0:
        refuse(4, "the power is not increasing in the input voltage at every vertex")
    for nm, chk in (("A", R["main_chk"]), ("B", R["chk_printed"]), ("C", R["chk_floor"]), ("D", R["chk_drift"])):
        if any(abs(w[1] - v_oc) > 1e-9 for _l, w, _n in chk):
            refuse(4, "stack %s's dense check finds its worst below the 25 V vertex" % nm)
    # (b) RSENSE1's temperature: the break-even over the air, stacks A and C (a hot spot on the board beside L1 and the FETs)
    def rs_t_breakeven(gain, lmul, drifts):
        rm_lo = rfac(tol_y, tcr_y, t_air - 25.0, (R["life_y"][0] + R["life_y"][1] / rm) if drifts else 0.0,
                     (R["sold_y"][0] + R["sold_y"][1] / rm) if drifts else 0.0)
        f = lambda t: v_oc * i_nom * corner_k(v_oc, gain, lmul, rfac(tol_h, tcr_h, t - 25.0, life_h if drifts else 0.0, sold_h if drifts else 0.0), rm_lo)
        if f(170.0) <= p_win:
            return None
        lo, hi = 25.0, 170.0
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if f(mid) > p_win:
                hi = mid
            else:
                lo = mid
        return lo
    R["rs_t_be"] = (rs_t_breakeven(ea2, 1.0, False), rs_t_breakeven(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True))
    # (c) the conservative assumptions one at a time on stack A (the cold end, the worse), and together (stack C with RSENSE1's
    # cold TCR at twice its printed hot-side value)
    TCR_COLD_CONS = 2.0 * tcr_h
    def p_cold(gain, lmul, drifts, tcr_cold):
        dt = abs(END[0][1] - 25.0)
        rs_lo = rfac(tol_h, tcr_cold, dt, life_h if drifts else 0.0, sold_h if drifts else 0.0)
        rm_lo = rfac(tol_y, tcr_y, END[0][2] - 25.0, (R["life_y"][0] + R["life_y"][1] / rm) if drifts else 0.0,
                     (R["sold_y"][0] + R["sold_y"][1] / rm) if drifts else 0.0)
        return v_oc * i_nom * corner_k(v_oc, gain, lmul, rs_lo, rm_lo)
    R["cons"] = dict(base=p_cold(ea2, 1.0, False, tcr_h), ea2=p_cold(ea2 / EA2_FLOOR_DIV, 1.0, False, tcr_h),
                     line=p_cold(ea2, LINE_FLOOR_MUL, False, tcr_h), tcr=p_cold(ea2, 1.0, False, TCR_COLD_CONS),
                     joint=p_cold(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, TCR_COLD_CONS), tcr_cons=TCR_COLD_CONS)
    if R["cons"]["joint"] > p_win:
        refuse(4, "the conservative assumptions together take the corner over 100 W")
    # (d) protection: the IMON_IN fault (p.5, full range) against the regulated point; the fault/limit ratio does not depend on RSENSE1
    reg_hi = ref_p["max"] * (1 + line_p * 1e-2 * (v_oc - V_LINE_REF))
    R["g_fault"] = dvc / (iovm["min"] - reg_hi)                         # EA2 gain below which regulation would reach the fault (safe side)
    R["k_fault"] = (iovm["min"] / ref_p["max"] - 1.0) / (line_p * 1e-2 * (v_oc - V_LINE_REF))
    R["tsd"], R["tj_margin"] = 165.0, 125.0 - R["tj_hot"]
    need(raw[34], r"reaches approximately 165\u00b0C", "8705af p.34 the thermal shutdown")
    # (e) the hold's lowest against the 25 V corner (why EA3 and the FBIN bias do not reach the bound)
    w_lo = max(v_lo_env * i_nom * RP.i_factor(v_lo_env, ref_p["max"], vref_n, line_p * LINE_FLOOR_MUL, ls, dvc / (ea2 / EA2_FLOOR_DIV), 1, gm_lo,
                                               rfac(tol_h, tcr_h, END[1][1] - 25.0), rfac(tol_y, tcr_y, END[0][2] - 25.0)) for ls in (-1, 1))
    R["p_hold_lo"] = w_lo
    # (f) states outside the corners
    voc40 = LR["voc40"]
    p40 = voc40 * i_nom * corner_k(voc40, ea2, 1.0, rfac(tol_h, tcr_h, -40.0 - 25.0), rfac(tol_y, tcr_y, -40.0 - 25.0))
    caps = 0.0
    for ref in ("C11", "C12", "C13", "C14", "C15", "C64"):
        m = re.match(r"([\d.]+)(u|n)", e["components"][ref]["value"])
        caps += float(m.group(1)) * (1e-6 if m.group(2) == "u" else 1e-9)
    cspr = AC.CAND["SPR100"]
    tol_p = float(need(" ".join(RP.pdf_lines(RP.SPR_PDF[0], 1)), r"Power Tolerance\s+\+(\d+)/", "the SunPower sheet's power tolerance").group(1)) / 100.0
    t_cell_cold = AC.t_cell(t_cold, 1000.0, LR["noct"])
    p_panel_cold = cspr["p"] * (1 + tol_p) * (1 + cspr["gamma_p"] * (t_cell_cold - 25.0))
    R["outside"] = dict(voc40=voc40, p40=p40, c_vin=caps, e_caps=0.5 * caps * v_oc ** 2, t_cell_cold=t_cell_cold, p_panel_cold=p_panel_cold,
                        tol_p=tol_p)
    # (g) the design option that removes RSENSE1's cold TCR unknown: a stocked 15 mOhm 1 % 2512 whose maker states TCR from
    # -55 C, evaluated by the same rules (Vishay Dale WSL, Document Number 30100, Revision 23-Nov-2023, held)
    WSL = "v2/vendor/passives/held/vishay-wsl-30100-2023-11-23.pdf"
    if sha(WSL) != "1b5c68910aa562a0dcce11ec572b4dd1febe63cfb90d20f3eaf5f9c7e01b59ac":
        refuse(2, "%s is not the pinned file (fetch it: v2/docs/records/l4e7/fetch_held_back.py)" % WSL)
    w1, w2, w3 = flat(pg(WSL, 1)), flat(pg(WSL, 2)), flat(pg(WSL, 3))
    wp = float(need(w1, r"WSL2512 2512 ([\d.]+) \(1\) 0\.003 to 0\.5", "WSL p.1 WSL2512's P70").group(1))
    wtcr = float(need(w2, r"\u00b1 (\d+) for 7 m\u03a9 to 500 m\u03a9", "WSL p.2 TCR 7 to 500 mOhm").group(1)) * 1e-6
    need(w2, r"TCR measured from -55 \u00b0C to \+155 \u00b0C", "WSL p.2 the TCR's span")
    wtop = float(need(w2, r"Operating temperature range \u00b0C -65 to \+(\d+)", "WSL p.2 operating range").group(1))
    wlife = need(w3, r"Load life 1000 h at rated power, \+ 70 \u00b0C.*?\u00b1 \(([\d.]+) % \+ ([\d.]+) \u03a9\)", "WSL p.3 load life").groups()
    wsold = need(w3, r"Resistance to solder heat .*?\u00b1 \(([\d.]+) % \+ ([\d.]+) \u03a9\)", "WSL p.3 solder heat").groups()
    wc = catalogue("C844695")
    if wc["model"] != "WSL2512R0150FEA" or wc["params"].get("Tolerance") != "\u00b11%" or wc["pdf_sha256"] != sha(WSL):
        refuse(3, "the filed WSL reading is not the evaluated part")
    w_kr = (wtop - 70.0) / wp                                         # INFERRED, as for HoJLR: rated at 70 C to zero at the top of its range
    w_life = float(wlife[0]) / 100.0 + float(wlife[1]) / rs
    w_sold = float(wsold[0]) / 100.0 + float(wsold[1]) / rs

    def p_wsl(rmv, inom, floor):
        out = []
        t = t_air
        for _ in range(30):
            i_hi = inom * corner_k(v_oc, ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, rfac(0.01, wtcr, t - 25.0, w_life, w_sold), 1.0)
            t = t_air + i_hi ** 2 * rs * 1.01 * w_kr
        for t_rs, t_rm in ((t_cold, t_cold), (t, t_air)):
            rs_lo = rfac(0.01, wtcr, t_rs - 25.0, w_life if floor else 0.0, w_sold if floor else 0.0)
            rm_lo = rfac(tol_y, tcr_y, t_rm - 25.0, (R["life_y"][0] + R["life_y"][1] / rmv) if floor else 0.0,
                         (R["sold_y"][0] + R["sold_y"][1] / rmv) if floor else 0.0)
            out.append(v_oc * inom * corner_k(v_oc, ea2 / EA2_FLOOR_DIV if floor else ea2, LINE_FLOOR_MUL if floor else 1.0, rs_lo, rm_lo))
        return max(out), t
    wa, w_t = p_wsl(rm, i_nom, False)
    wf, _ = p_wsl(rm, i_nom, True)
    w_ok = [(rv, c_, st, iv) for rv, c_, st, iv, _a, _b in rows_rm if st >= STOCK_MIN and p_wsl(rv, iv, True)[0] <= p_win]
    w_pick = min(w_ok, key=lambda t: t[0]) if w_ok else None
    R["wsl"] = dict(model=wc["model"], code="C844695", stock=wc["stock"], p70=wp, tcr=wtcr, life=w_life, sold=w_sold, kr=w_kr, t_hot=w_t,
                    p_a=wa, p_floor=wf, pick=w_pick, cost=(1.0 - w_pick[3] / i_nom) if w_pick else None)
    # the classification (each figure above; `resolved` is True only where the sheet or a maker's statement bounds the row)
    rows = [
        dict(id="EA2", name="EA2's gain and VC's operating range", bound=True, stability=True, protection=False, other="energy, only in hours the limit binds",
             why_bound="the regulated IMON_IN moves by (VC - 1.2 V) / gain (p.5, p.2): %.4f W at 130 V/V against %.4f W with the term left out (stack A, cold)" % (
                 R["main_chk"][0][1][0], R["chk_printed"][0][1][0]),
             why_stability="EA2 drives VC through the compensation network in the input-current loop; with no printed minimum gain or gm the loop's margin is not guaranteed (p.33: the loop stability is affected by a number of factors)",
             why_protection="the IMON_IN fault is a comparator on IMON_IN itself (p.5, 1.55 V minimum, full range), not through EA2; only a gain under %.2f V/V would hold the regulated point at the fault, which stops switching (the safe side)" % R["g_fault"],
             sheet="p.5 EA2 gain 130 V/V and gm 185 umho, typical only; p.4 the IMON_IN regulation, full range, printed at VC = 1.2 V; p.2 VC's absolute maximum -0.3 to 2.2 V; p.7 'Inductor Current Sense Voltage at Minimum Duty Cycle' against VC and p.8 'Maximum VC vs SS' plot VC within 0.5 to 2.0 V (TYPICAL, TA = 25 C; not a limit); p.31 the current-limiting text names 1.208 V typical and no gain bound",
             guaranteed=None,
             conservative="EA2 at least 65 V/V (half its typical) with VC anywhere in its absolute maximum range (the replay's allowance doubled)",
             qualification="Analog Devices' statement of EA2's minimum gain, or of the IMON_IN regulation point's guaranteed shift with VC, over -40 to 125 C junction (a production limit); a bench reading of a few units (7b.10) checks the design, it is not that limit",
             margin_w=p_win - R["cons"]["ea2"], breakeven="%.6f V/V (stack A, cold), %.6f V/V (stack C's other terms, cold)" % (R["be_gain"][(1.0, False)][0], R["be_gain"][(2.0, True)][0]),
             resolved=False, clarification="analog-devices-lt8705a.txt"),
        dict(id="LINE", name="the IMON_IN reference's line regulation while switching and at temperature", bound=True, stability=False, protection=False, other="energy, a fraction of a percent of the limit, only in hours it binds",
             why_bound="the reference moves with VIN from the 12 V it is printed at: at 25 V the printed maximum moves the corner by %.4f W" % (R["main_chk"][0][1][0] - p_cold(ea2, 0.0, False, tcr_h)),
             why_stability="a static shift of the reference with VIN; it adds no gain or pole to the loop",
             why_protection="the regulated point would reach the IMON_IN fault minimum only at %.0f times the printed maximum" % R["k_fault"],
             sheet="p.4 0.002 / 0.005 %/V, VIN 12 to 80 V, not switching, at 25 C (no bullet); p.4 the regulation itself is a full-range row at VIN = 12 V, so its temperature drift at 12 V is guaranteed; p.7 'Feedback Voltages' against temperature at VC = 1.2 V is TYPICAL",
             guaranteed="the full-range IMON_IN regulation row covers temperature at VIN = 12 V; the VIN dependence while switching and away from 25 C is not printed",
             conservative="twice the printed maximum (0.010 %/V), either sign, at every temperature and while switching",
             qualification="Analog Devices' statement of the IMON_IN reference's line regulation while switching, over -40 to 125 C junction",
             margin_w=p_win - R["cons"]["line"], breakeven="%.1f times the printed maximum (stack A, cold); %.1f with EA2 at 65 V/V" % R["be_line"],
             resolved=False, clarification="analog-devices-lt8705a.txt"),
        dict(id="TCR", name="RSENSE1's TCR below +25 C", bound=True, stability=False, protection=False, other="energy, a fraction of a percent of the limit, only in hours it binds",
             why_bound="RSENSE1 sits in the limit's denominator; at -20 C its TCR sets its low end",
             why_stability="a fraction of a percent of loop gain at most; the loop's margin is set by the compensation, not by this",
             why_protection="the fault and the limit both act on IMON_IN, so their ratio (1.55 / 1.229 V at its least) does not depend on RSENSE1",
             sheet="HoJLR2512 Ho-A0 p.2 +-50 ppm/K (2 to 500 mOhm); p.4 the TCR test spans +25 to +125 C only; the catalogue prints no TCR for C2903494",
             guaranteed=None,
             conservative="+-%.0f ppm/K below +25 C (twice the printed hot-side value)" % (TCR_COLD_CONS * 1e6),
             qualification="Milliohm's statement of the HoJLR2512 TCR from -55 (or -40) to +25 C, or its production characterization; a bench reading of R59 at -20 C (7b.14) checks the design only",
             margin_w=p_win - R["cons"]["tcr"], breakeven="%.3f ppm/K (stack A), %.3f ppm/K (stack C)" % (R["be_tcr_cold"] * 1e6, R["be_tcr_cold_floor"] * 1e6),
             resolved=False, clarification="milliohm-hojlr2512.txt"),
        dict(id="HOLD", name="EA3's gain and the FBIN bias", bound=False, stability=True, protection=False, other="energy (the hold band)",
             why_bound="they set the hold, the envelope's low end: the corner there is %.4f W against %.4f W at 25 V (the power rises with the input voltage at every vertex)" % (
                 R["p_hold_lo"], R["chk_floor"][0][1][0]),
             why_stability="EA3 closes the input-voltage loop through VC; its margin is part of the hold's bench row",
             why_protection="the hold is a regulation, not a protection; FBOUT's overvoltage and the IMON_IN fault are other pins",
             sheet="p.4 EA3 90 V/V and FBIN bias 10 nA, typical only; p.4 FBIN regulation 1.184 / 1.226 V, full range (I grade), at VC = 1.2 V",
             guaranteed="the FBIN reference is full range; the gain and the bias are typical",
             conservative="EA3 at half its typical with the resistors' drifts: the hold inside %.3f to %.3f V; the bias at ten times its typical moves the lower corner by %.1f mV" % (
                 hb3[0], hb3[2], 1e3 * (R["bias_rows"][2][1] - R["bias_rows"][1][1])),
             qualification="none for the bound; the hold's energy rows carry them as sensitivities and 7b.12 reads the hold",
             margin_w=None, breakeven=None, resolved=False, clarification=None),
        dict(id="TJ", name="U5's junction temperature", bound=True, stability=False, protection=True, other="lifetime (Note 3: derated above 125 C)",
             why_bound="every LT8705A row the corner uses is a full-range row, guaranteed for the I grade from -40 to 125 C junction (p.6 Note 3); the bound needs only the junction inside that range, not its value",
             why_stability="the loop's gains move with temperature inside the unprinted EA2 row already carried above",
             why_protection="the overtemperature protection acts at approximately 165 C (p.34, approximate): the estimate stays %.1f K under it" % (165.0 - R["tj_hot"]),
             sheet="p.2 theta-JA 34 C/W (UHF, a package figure on the maker's board); p.6 Note 3 and Note 8; p.34 the CLKOUT method (+-10 C) and the thermal shutdown at approximately 165 C",
             guaranteed="the I grade's rows hold over -40 to 125 C junction",
             conservative="TJ at most %.1f C: the maximum gate charge at 10 V for all four FETs at the highest oscillator frequency, the VIN quiescent maximum, EXTVCC at L4-E5's %.2f V ceiling and theta-JA 34 C/W in %.1f C air" % (
                 R["tj_hot"], R["ceil5"][2], t_air),
             qualification="a design verification of board E's thermal path (7b.13 by p.34's method), with the margin covering the unit spread the maximum gate charge already bounds",
             margin_w=None, margin_k=R["tj_margin"], breakeven="125 C junction (%.1f K above the estimate)" % R["tj_margin"], resolved=False, clarification=None),
    ]
    for r_ in rows:
        if r_["clarification"]:
            cp = os.path.join(TOP, CLAR, r_["clarification"])
            if not os.path.isfile(cp):
                refuse(3, "the clarification text %s is missing" % r_["clarification"])
            ct = open(cp, encoding="utf-8").read()
            if not ct.startswith("DRAFT FOR THE OWNER TO SEND.") or not any(k in ct for k in ("LT8705AIUHF", "HoJLR2512-3W-15mR-1%")):
                refuse(3, "the clarification text %s does not read as a draft naming its part" % r_["clarification"])
    R["qual_rows"] = rows
    R["bound_status"] = bound_status(rows)
    # ================================================================== 9: what the drafts change (read back from each)
    R["models"] = {c_: v_["model"] for c_, v_ in lc.items()}
    R["drafts"] = {}
    for nm in ("apply_gen_sch_e_u5_grade.py", "apply_gen_sch_e_hold.py", "apply_gen_sch_e_input_limit.py"):
        m = load(nm[:-3] + "_for_l4e7", "v2/docs/records/l4e7/" + nm)
        new = m.patched(gse)
        want = {"apply_gen_sch_e_u5_grade.py": ["C674169"], "apply_gen_sch_e_hold.py": [r8c, r9c],
                "apply_gen_sch_e_input_limit.py": [rs_code, rm_code, CIMON[2]]}[nm]
        R["drafts"][nm] = (len(m.EDITS), "R10" in "".join(o_ for o_, _r in m.EDITS), new.count('r("R10", "115k 1% (RFBOUT1: 15.1 V)"') == 1,
                           all(new.count('"%s")' % c_) > gse.count('"%s")' % c_) for c_ in want), want)
    return R


def render(R):
    o = []
    P = o.append
    END = R["ends"]
    P("L4-E7: REAL COMPONENT SETTINGS FOR BOARD E'S SOLAR STAGE (layer 4, MESHSAT-1357, 1 October 2026)")
    P("prototype design, desk arithmetic; nothing bought, built, powered or measured. Bases: MAKER, NETLIST, CATALOGUE, MODELED,")
    P("INFERRED, ASSUMPTION, SESSION, as named on each line")
    P("")
    P("0. REPRODUCTIONS (before any figure)")
    P("   0a l4e_replay.py in a child process reproduces l4e_replay.out byte for byte: %s" % ("yes" if R["r0a"] else "NO"))
    P("   0b l4e5_source_control.py in a child process reproduces l4e5_source_control.out byte for byte: %s" % ("yes" if R["r0b"] else "NO"))
    P("   0c l4e_replay.main() in-process, locals captured, prints l4e_replay.out byte for byte: %s" % ("yes" if R["r0c"] else "NO"))
    P("   (the functions used below are the replay's: i_factor, ec_row, pdf_lines, hold, trace, meanday, least; no git hash compared)")
    P("")
    P("1. BOARD E AS DRAWN (NETLIST v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net, pinned)")
    for f in R["facts"]:
        P("   - " + f)
    P("   gen_sch_e.py's R10 reads %sk; L4-E5 (its record, reproduced in 0b) raises it to %sk, ceiling %.2f / %.2f / %.2f V" % (
        R["r10_gen"], R["r10_5"], *R["ceil5"]))
    P("")
    P("2. THE MAKERS' ROWS USED")
    P("   LT8705A 8705af (v2/vendor/power/lt8705a.pdf): p.3 order table: grades in the drawn QFN (UHF): %s; H and MP only in the" % ", ".join(R["qfn"]))
    P("     TSSOP (FE); p.6 Note 3, its U+2013 minus written -:")
    for ln in textwrap.wrap("\"" + R["note3"] + "\"", 118):
        P("       " + ln)
    P("   p.4 IMON_IN regulation %.3f / %.3f / %.3f V (full range); line regulation max %.3f %%/V (25 C, VIN 12 to 80 V, not switching);" % (
        R["ref_p"]["min"], R["ref_p"]["typ"], R["ref_p"]["max"], R["line_p"]))
    P("     p.5 A7 gm E, I %.2f / %.2f mmho (full range), all grades %.2f / %.2f (25 C); EA2 gain %.0f V/V TYP only; p.4 FBIN E, I" % (
        R["gm_lo"], R["gm_hi"], R["a7"]["(All Grades)"]["min"], R["a7"]["(All Grades)"]["max"], R["ea2"]))
    P("     %.3f / %.3f / %.3f V (full range); EA3 gain %.0f V/V TYP only; p.5 IMON_IN fault %.2f / %.2f / %.2f V; IMON_IN output" % (
        R["fbin"]["min"], R["fbin"]["typ"], R["fbin"]["max"], R["ea3"], R["iovm"]["min"], R["iovm"]["typ"], R["iovm"]["max"]))
    P("     current at least %.0f uA; CSPIN-CSNIN differential %.0f to %.0f mV; p.31 CIMON_IN > %.0f / (f x RIMON_IN), 0.1 to 1 uF in a" % (
        R["ioutmin"], R["csd"]["min"], R["csd"]["max"], R["cim"]))
    P("     current loop; p.2 QFN theta-JA %.0f C/W; p.3 VIN quiescent %.1f mA max; p.6 fOSC at RT 215k up to %.0f kHz" % (
        R["tja"], R["iq"] * 1e3, R["f_max"] / 1e3))
    P("   Milliohm HoJLR2512 series (v2/vendor/passives/milliohm-hojlr2512-series.pdf, Ho-A0): p.1 F = +-1 %%; p.2 TCR +-%.0f ppm/K" % (R["tcr_h"] * 1e6))
    P("     (2 to 500 mOhm), 3 W derating from 70 C to 0 at 170 C (%.1f K/W, INFERRED as r11_dep.py); p.4 the TCR test spans +25 to" % R["k_r"])
    P("     +125 C only; soldering heat < +-%.1f %%; load life < +-%.0f %%" % (100 * R["sold_h"], 100 * R["life_h"]))
    P("   YAGEO RT series V.16, May 06 2025 (held: v2/vendor/passives/held/yageo-rt-series-v16-2025-05-06.pdf): p.2 B = +-%.1f %%," % (100 * R["tol_y"]))
    P("     D = %.0f ppm/K; p.7 TCR tested at +25/-55 C and +25/+125 C; life +-(%.1f %% + %.2f Ohm); p.8 soldering heat +-(%.1f %% + %.2f Ohm)" % (
        R["tcr_y"] * 1e6, 100 * R["life_y"][0], R["life_y"][1], 100 * R["sold_y"][0], R["sold_y"][1]))
    P("   Infineon BSC028N06NS Rev.2.1 p.3 (held) Qg max %.0f nC; BSC039N06NS Rev.2.4 p.4 Qg max %.0f nC (both VGS 0 to 10 V)" % (
        R["qg028"] * 1e9, R["qg039"] * 1e9))
    P("   the envelope (v2/ecad/tools/pcb_envelope.yaml): ambient in use %.0f to %.0f C (REQ-024, D-02a); worst inside air %.1f C" % (
        R["t_cold"], R["t_amb_hi"], R["t_air"]))
    P("")
    P("3. THE DECISIONS")
    P("   GRADE: LT8705AI in the drawn QFN (LT8705AIUHF#PBF, LCSC C674169; #TRPBF C674170), replacing the netlist's C674164")
    P("     (LT8705AEUHF#TRPBF, the E grade). The H and MP grades exist only in the TSSOP, which is not the drawn land. Of E and I,")
    P("     only I is GUARANTEED (tested) below 0 C junction; the kit starts cold at %.0f C ambient, so its junction range starts at" % R["t_cold"])
    P("     %.0f C. With I fixed, A7's limits are %.2f / %.2f mmho (the replay stacked H and MP's %.2f because no grade was named)." % (
        R["tj_cold"], R["gm_lo"], R["gm_hi"], R["a7"]["(LT8705AH, LT8705AMP)"]["min"]))
    P("     Hot end (INFERRED): INTVCC from EXTVCC on TRK_OUT up to L4-E5's %.2f V; gate charge 2 x %.0f + 2 x %.0f nC at %.0f kHz plus" % (
        R["ceil5"][2], R["qg028"] * 1e9, R["qg039"] * 1e9, R["f_max"] / 1e3))
    P("     %.1f mA: %.1f mA, %.2f W, TJ at most %.1f C in %.1f C air with theta-JA %.0f C/W (%.1f C at the drawn output's %.2f V), under" % (
        R["iq"] * 1e3, R["i_g"] * 1e3, R["p_ic"], R["tj_hot"], R["t_air"], R["tja"], R["tj_hot_old"], R["out_drawn"][2]))
    P("     125 C.")
    P("     So the I grade's tested range, -40 to 125 C junction, covers %.0f to %.1f C. Catalogue: stock 0 at LCSC on 1 October 2026" % (
        R["tj_cold"], R["tj_hot"]))
    P("     (U5 is bench-fitted; another distributor)")
    P("   RSENSE1 (new, R59): %.0f mOhm, Milliohm HoJLR2512-3W-15mR-1%%, LCSC %s (stock %d): +-%.0f %% (CATALOGUE and MAKER p.1)," % (
        R["rs"] * 1e3, R["rs_code"], R["rs_stock"], 100 * R["tol_h"]))
    P("     +-%.0f ppm/K (MAKER p.2). Rule (SESSION): the family value that puts the zero-margin limit (%.3f A) nearest A7's printed" % (
        R["tcr_h"] * 1e6, R["i_zero"]))
    P("     50 mV test point (p.5), since no A7 offset row is printed; at the chosen setting %.1f mV" % (R["i_nom"] * R["rs"] * 1e3))
    P("   RIMON_IN (R16): %gk, YAGEO %s, LCSC %s (stock %d): +-%.1f %%, +-%.0f ppm/K (MAKER p.2, CATALOGUE)." % (
        R["rm"] / 1e3, R["models"][R["rm_code"]], R["rm_code"], R["rm_stock"], 100 * R["tol_y"], R["tcr_y"] * 1e6))
    P("     Rule (SESSION): the largest stocked RT0603BRD07 setting whose 25 V corner stays at or under 100 W at both ends with every")
    P("     printed limit, the resistors' printed soldering-heat and life drifts stacked, EA2's gain at 1/%.0f of its typical and the" % EA2_FLOOR_DIV)
    P("     line regulation at %.0f times its printed maximum. ACHIEVED SETTING: 1.208 V / (1 mmho x %.0f mOhm x %.1fk) = %.4f A" % (
        LINE_FLOOR_MUL, R["rs"] * 1e3, R["rm"] / 1e3, R["i_nom"]))
    P("     candidates (setting A; worst corner at the typical rows / under the floor with drifts, W):")
    for rm_val, code, stock, inom, wt, wf in R["rows_rm"]:
        if 22e3 <= rm_val <= 24.9e3:
            P("       %5.1fk %-9s stock %6d  %.4f A  %7.3f / %7.3f%s" % (rm_val / 1e3, code, stock, inom, wt, wf,
                                                                    "  <- chosen" if code == R["rm_code"] else ("  (zero margin)" if code == R["zero"][1] else
                                                                    ("  (stock under %d)" % STOCK_MIN if stock < STOCK_MIN else ""))))
    P("     CIMON_IN (new, %s): %s, LCSC %s: above p.31's minimum %.1f nF at the slowest oscillator, at the 0.1 uF lower end; tau %.2f ms" % (
        CIMON[0], CIMON[1], CIMON[2], R["cim_min"] * 1e9, R["tau"] * 1e3))
    P("   THE HOLD: R8 %gk (%s, LCSC %s, stock %d) over R9 %gk (%s, LCSC %s, stock %d), 0.1 %%, 25 ppm/K: nominal %.3f V" % (
        R["r8v"] / 1e3, R["models"][R["r8c"]], R["r8c"], R["stock"][R["r8c"]], R["r9v"] / 1e3, R["models"][R["r9c"]], R["r9c"],
        R["stock"][R["r9c"]], R["hb"][1]))
    P("     Rule (SESSION, under REQ-016 \"the panel held at 17.6 V by the stage's input regulation\" and the owner's D-34, which keeps")
    P("     REQ-016's window unchanged; check astra-check-l4e7-1, B1): the drawn ratio 102k over 7.5k kept, each at its drawn value as")
    P("     the stocked RT0603BRD07 part (0.1 %, 25 ppm/K); only the tolerance and the drift change")
    P("     the band at both ends (FBIN's I-grade limits, its line term, the FBIN bias at its typical, R8 and R9 at 0.1 % and 25 ppm/K):")
    P("       EA3 at its typical %.0f V/V:                      %.6f / %.6f / %.6f V" % (R["ea3"], R["hb"][0], R["hb"][1], R["hb"][2]))
    P("       EA3 at its typical, soldering and life drifts:  %.6f / %.6f V" % (R["hb4"][0], R["hb4"][2]))
    P("       EA3 at half its typical:                       %.6f / %.6f V" % (R["hb2"][0], R["hb2"][2]))
    P("       EA3 at half, soldering and life drifts:        %.6f / %.6f V (the widest conditioned band)" % (R["hb3"][0], R["hb3"][2]))
    P("     as drawn (1 %% parts), the replay's legacy calculation with H and MP's FBIN minimum %.3f V: %.3f / %.3f / %.3f V; with the" % (
        R["fbin_hmp_min"], *R["hold_drawn"]))
    P("     E grade the netlist names (C674164, FBIN minimum %.3f V) and the replay's other terms, its lower corner is %.6f V" % (
        R["fbin"]["min"], R["drawn_e_lo"]))
    P("   PROPOSAL, NOT ADOPTED: it would change REQ-016's 17.6 V point and needs the owner's ruling (D-34). Not drafted; nothing here")
    P("     depends on it. Of %d stocked RT0603BRD07 pairs with a nominal from %.1f to %.1f V (the model's hourly maximum-power voltage on" % (
        R["proposal"]["n"], HOLD_RANGE[0], HOLD_RANGE[1]))
    P("     SC-37's day runs %.2f to %.2f V), the one whose band's worse end gives the most energy: %gk over %gk (%s, %s), band" % (
        R["vmpp"][0], R["vmpp"][1], R["proposal"]["r8"] / 1e3, R["proposal"]["r9"] / 1e3, R["proposal"]["c8"], R["proposal"]["c9"]))
    P("     %.3f / %.3f / %.3f V (EA3 typical), %.1f / %.1f / %.1f Wh a day; at nominal %+.1f Wh a day against the kept hold's %.1f Wh" % (
        *R["proposal"]["band"], *R["proposal"]["e_band"], R["proposal"]["e_band"][1] - R["proposal"]["e_nom_kept"], R["proposal"]["e_nom_kept"]))
    P("")
    P("4. THE 100 W CORNER CHECK ON THE ACHIEVED VALUES (section 11's physics: the replay's i_factor, 8705af p.31)")
    P("   envelope: %.6f V (the kept hold's lowest: EA3 at half, the resistors' drifts) to REQ-016's %.0f V in %.2f V steps; I grade;" % (
        min(R["hb"][0], R["hb2"][0], R["hb3"][0], R["hb4"][0]), 25.0, V_STEP))
    P("   both ends:")
    for lab, t_rs, t_rm, _t3, p_ in END:
        P("     %s: RSENSE1 at %.1f C, RIMON_IN at %.1f C%s" % (lab, t_rs, t_rm, "" if lab == "the cold end" else
                                                               " (RSENSE1 %.2f W x %.1f K/W over the air, INFERRED)" % (p_, R["k_r"])))

    def show(name, chk, basis):
        P("   %s (%s):" % (name, basis))
        for lab, w, n in chk:
            P("     %-12s worst %.4f W at %.3f V (ref %.3f V, line %s, gm %.2f, RSENSE1 x%.5f, RIMON_IN x%.5f, EA2 %s); margin %.4f W; %d corners" % (
                lab, w[0], w[1], w[2], "+" if w[3] > 0 else "-", w[4], w[5], w[6], "+" if w[7] > 0 else "-", 100.0 - w[0], n))
    show("A. THE CHECK", R["main_chk"], "printed limits; the two TYP-only rows as the replay carries them: EA2 at 130 V/V over VC's absolute range, line at its 25 C maximum")
    show("B. printed rows alone", R["chk_printed"], "information: EA2's and the line term left out")
    show("C. the design floor", R["chk_floor"], "EA2 at 65 V/V, line x2, the resistors' soldering and life drifts stacked: SESSION")
    show("D. drifts at the typical rows", R["chk_drift"], "information")
    P("   VERDICT: A PASSES at both ends with a margin of %.2f W, and C (the floor) passes; refused above 100 W" % (100.0 - max(w[0] for _l, w, _n in R["main_chk"])))
    P("   THE UNPRINTED ROWS, as break-even values for this setting (the corner reaches 100 W at the value shown), each with its stack:")
    for (lm, dr), (gc, gh) in sorted(R["be_gain"].items()):
        P("     EA2's gain; printed limits, line x%-4g%-28s cold end %s V/V, hot end %s V/V" % (
            lm, ", resistors' drifts stacked" if dr else (", no drifts (stack A)" if lm == 1.0 else ", no drifts"), "%.6f" % gc if gc else "none passes",
            "%.6f" % gh if gh else "none passes"))
    P("     the line regulation (cold end; printed limits, no drifts): with EA2 at 130 V/V (stack A) up to %.1f times its printed" % R["be_line"][0])
    P("     maximum (%.3f %%/V); with EA2 at 65 V/V, %.1f times" % (R["be_line"][0] * R["line_p"], R["be_line"][1]))
    P("     RSENSE1's TCR below 25 C (HoJLR prints its TCR from +25 to +125 C only, so the cold end applies it as an ASSUMPTION): the")
    P("     cold corner passes up to %s under stack A, and up to %s under stack C (EA2 65 V/V, line x2, drifts)" % (
        "%.3f ppm/K" % (R["be_tcr_cold"] * 1e6) if R["be_tcr_cold"] is not None else "10000 ppm/K and beyond",
        "%.3f ppm/K" % (R["be_tcr_cold_floor"] * 1e6) if R["be_tcr_cold_floor"] is not None else "10000 ppm/K and beyond"))
    P("   for comparison, the replay's 3.548 A on these parts would take %.3f W at the worse end" % R["old_on_parts"])
    P("   CONDITIONS: sense voltage at the limit's highest %.1f mV (operating range %.0f mV); IMON_IN %.1f uA at it (at least %.0f uA);" % (
        R["vd_lim_hi"] * 1e3, R["csd"]["max"], R["i_imon_lim"] * 1e6, R["ioutmin"]))
    P("     the fault (IMON_IN %.2f V maximum) at up to %.1f mV across RSENSE1; the candidate's hot short circuit through RSENSE1 %.1f mV," % (
        R["iovm"]["max"], R["v_fault_max"] * 1e3, R["vd_isc"] * 1e3))
    P("     inside the operating range; no resistor in series with CSPIN or CSNIN (p.30): R59's pads are their Kelvin taps")
    P("")
    P("5. THE ENERGY (MODELED: the replay's trace on SC-37's mean September day, the SunPower SPR-E-Flex-100, 1S1P, nominal sheet)")
    P("   Wh a day into the stage (hours the limit binds); PVGIS's maximum-power figure %.1f Wh. Columns: no limit; the chosen setting" % R["e_mpp"])
    P("   at its lowest / nominal / highest; the zero-margin catalogue setting (%.1fk, %.4f A) at its lowest / nominal / highest" % (R["zero"][0] / 1e3, R["zero"][3]))
    for row in R["grid_e"]:
        P("     %-24s %.3f V  %6.1f | %s | %s" % (row[0], row[1], row[2], " ".join("%6.1f (%d h)" % x for x in row[3:6]),
                                                 " ".join("%6.1f (%d h)" % x for x in row[6:9])))
    d_ = [row[3 + k][0] - row[6 + k][0] for row in R["grid_e"] for k in range(3)]
    P("   the margin's cost on this day: %.1f Wh at the most over the %d cells (chosen less zero-margin from %+.1f to %+.1f Wh:" % (
        max(0.0, -min(d_)), len(d_), min(d_), max(d_)))
    P("   %s)" % ("where the chosen limit binds below the panel's maximum-power point, the voltage rides up toward it" if max(d_) > 0.05
                     else "the limit binds in no hour of this day at any cell"))
    P("   as drawn (the replay, section 12, no input limit; its legacy band): %s" % "; ".join("%.1f Wh at %.3f V" % (g_[3], g_[1]) for g_ in R["old_grid"]
                                                                                       if g_[2] == "no input limit (as drawn)"))
    ge = {r_[0]: r_ for r_ in R["grid_e"]}
    P("   ENERGY SENSITIVITY of the two TYP-only hold rows (check M2: energy rows, not parameter break-evens; no input limit):")
    P("     EA3's gain from its typical to half: lower corner %.1f to %.1f Wh, upper corner %.1f to %.1f Wh (with the drifts %.1f / %.1f Wh)" % (
        ge["lower hold corner"][2], ge["lower, EA3 at its floor"][2], ge["upper hold corner"][2], ge["upper, EA3 at its floor"][2],
        ge["lower, EA3 floor, drifts"][2], ge["upper, EA3 floor, drifts"][2]))
    P("     the FBIN bias (out of the pin, lowering the hold; EA3 typical, the lower corner): %s" % "; ".join(
        "%.0f nA %.6f V %.1f Wh" % (b[0] * 1e9, b[1], b[2]) for b in R["bias_rows"]))
    P("   where the margin costs: the limit's lowest begins to bind above (hour 12's %.1f C air, the model's cells):" % R["ta12"])
    for inom, vh, lim, g in R["g_bind"]:
        P("     setting %.4f A, hold %.3f V: lowest %.4f A, above %.0f W/m2" % (inom, vh, lim, g))
    P("     (SC-37's day peaks at 520.7 W/m2); in an hour it binds, the stage's input falls in the ratio of the two settings, %.1f %%" % (
        100.0 * (1 - R["i_nom"] / R["zero"][3])))
    P("   A1 AND A2 ON THE NEW TRACES (CORRECTED, WE, TYP; the replay's meanday and least, unchanged; pairs 06 / 18 UTC):")
    for (lab, ak), (e_, stops, u48, u72, add) in sorted(R["runs"].items()):
        P("     %s, %s: %.1f Wh a day; first interruption h %s; unserved %s at 48 h, %s at 72 h; least addition %s Wh" % (
            lab, ak, e_, "/".join("-" if s is None else str(s) for s in stops), " / ".join("%.1f" % v for v in u48),
            " / ".join("%.1f" % v for v in u72), " / ".join("none" if a is None else "%+.1f" % a for a in add)))
    for (lab, ak), (stops, u48, u72, add) in sorted(R["old_runs"].items()):
        P("     was %s, %s: unserved %s at 48 h, %s at 72 h; least addition %s / %s Wh" % (
            lab, ak, " / ".join("%.1f" % v for v in u48), " / ".join("%.1f" % v for v in u72), add[0], add[1]))
    P("")
    P("6. THE INTERACTION WITH L4-E5 (R10 115k to 232k, the ceiling raised, C26 and C27 re-rated)")
    for nm, (n_e, touches, r10_once, codes_ok, codes) in sorted(R["drafts"].items()):
        P("   %s: %d edit(s); names R10: %s; R10's drawn line still present once after it: %s; carries %s: %s" % (
            nm, n_e, "yes" if touches else "no", "yes" if r10_once else "NO", ", ".join(codes), "yes" if codes_ok else "NO"))
    P("   U5's junction is taken at L4-E5's raised EXTVCC (%.2f V): %.1f C; the stage's input stays at or under REQ-016's window, so" % (
        R["ceil5"][2], R["tj_hot"]))
    P("   L4-E5's line (sized for the window's 100 W) covers it; the hold and the limit are on the input, R10 and C26/C27 on the output")
    P("")
    P("7. INCONCLUSIVE (no printed bound), each with the measurement that bounds it")
    P("   - EA2's voltage gain (130 V/V TYP, p.5) and VC's operating range: the corner passes for an EA2 gain at or above %.6f V/V" % R["be_gain"][(1.0, False)][0])
    P("     cold and %.6f V/V hot under stack A, and %.6f V/V cold and %.6f V/V hot with stack C's other terms (line x2, drifts)." % (
        R["be_gain"][(1.0, False)][1], R["be_gain"][(2.0, True)][0], R["be_gain"][(2.0, True)][1]))
    P("     Bench: in input-current limit at 25 V, step the load to move VC across its range, read VC and IMON_IN; the gain is")
    P("     dVC / dV(IMON_IN); accept at or above 65 V/V (the floor), and at least the break-even at every point")
    P("   - the IMON_IN reference's line regulation while switching and at both ends (printed at 25 C, not switching, p.4): the corner")
    P("     passes up to %.0f times its printed maximum (stack A, cold end). Bench: the limit's current at VIN 16 and 25 V, switching," % R["be_line"][0])
    P("     at both ends")
    P("   - RSENSE1's TCR below +25 C (HoJLR p.4 tests +25 to +125 C): passes up to %s (stack A) and %s (stack C). Bench: R59 at -20 C" % (
        "%.0f ppm/K" % (R["be_tcr_cold"] * 1e6) if R["be_tcr_cold"] is not None else "10000 ppm/K and beyond",
        "%.0f ppm/K" % (R["be_tcr_cold_floor"] * 1e6) if R["be_tcr_cold_floor"] is not None else "10000 ppm/K and beyond"))
    P("     and +25 C")
    P("   - EA3's gain (90 V/V TYP) and the FBIN bias (10 nA TYP): no compliance effect (the corner is at 25 V); an energy sensitivity")
    P("     only (section 5); the bench reads the hold at both ends (7b.12)")
    P("   - U5's junction (INFERRED from the gate charge at 10 V and theta-JA): the CLKOUT duty cycle method of p.34 (+-10 C)")
    P("   - the candidate panel's own source compliance (O-1) and every efficiency (C-8): unchanged by this record")
    P("")
    P("8. BENCH ROWS")
    P("   7b.9 (steady state): a PV emulator puts the loaded input at the limit from %.3f V (the kept hold's lowest: EA3 at half, the" % R["hb3"][0])
    P("     resistors' drifts) to 25 V, at the load's maximum, cold-soaked")
    P("     at %.0f C and in %.1f C air; V_in x I_in at or under 100 W at every point; the limit's current at 25 V at most %.3f A" % (
        R["t_cold"], R["t_air"], 100.0 / 25.0))
    P("   7b.9t (transients, recorded apart): a source step (open circuit to the limit) and an irradiance step; the peak and the")
    P("     time above 100 W against the filter's %.2f ms (SESSION: no fault trip, IMON_IN under %.2f V; above 100 W no longer than" % (
        R["tau"] * 1e3, R["iovm"]["min"]))
    P("     five time constants, %.1f ms)" % (5 * R["tau"] * 1e3))
    P("   7b.10 the EA2 gain row and 7b.11 the line row above; 7b.12 the hold, read at both ends: accepted inside %.3f to %.3f V (EA3 at" % (
        R["hb3"][0], R["hb3"][2]))
    P("     half, the resistors' drifts: the conditioned envelope); a reading outside %.3f to %.3f V (EA3 typical, new parts) is recorded" % (
        R["hb"][0], R["hb"][2]))
    P("     with EA3's gain it implies")
    P("   7b.13 U5's junction by CLKOUT at all four switches, EXTVCC at the ceiling, %.1f C air: at most 125 C less p.34's 10 C" % R["t_air"])
    P("   7b.14 R59 at -20 C and +25 C (a design check of the cold TCR; Milliohm's statement is the qualification)")
    P("")
    P("9. QUALIFICATION OF THE 100 W BOUND (the owner's instruction of 1 October 2026)")
    pv = R["prov"]

    def wrapP(first, rest, text, width=118):
        for k, ln in enumerate(textwrap.wrap(text, width)):
            P((first if k == 0 else rest) + ln)
    wrapP("   ", "     ", "THE SHEET: %s, read as the Internet Archive's snapshot %s (the id_ form; the live site resets this runner's "
          "connection), sha256 %s, byte-identical to the held v2/vendor/power/lt8705a.pdf; it prints its document code 8705af on "
          "each of its 44 pages and carries no revision table. Only its rows are used" % (pv["url"], pv["snapshot"], pv["sha"]))
    P("   THE CLASSIFICATION (Y: the value can move that outcome; the reasons below):")
    P("     %-4s %-74s %-6s %-9s %-10s %s" % ("id", "unprinted value", "bound", "stability", "protection", "other"))
    for r_ in R["qual_rows"]:
        P("     %-4s %-74s %-6s %-9s %-10s %s" % (r_["id"], r_["name"], "Y" if r_["bound"] else "N", "Y" if r_["stability"] else "N",
                                                "Y" if r_["protection"] else "N", r_["other"]))
    for r_ in R["qual_rows"]:
        P("   %s, %s" % (r_["id"], r_["name"]))
        for lab, key in (("the bound", "why_bound"), ("loop stability", "why_stability"), ("protection", "why_protection"),
                         ("the sheet", "sheet"), ("guaranteed limit", "guaranteed"), ("conservative assumption", "conservative"),
                         ("qualification needed", "qualification")):
            text = r_[key] if r_[key] is not None else "none printed"
            for k, ln in enumerate(textwrap.wrap("%s: %s" % (lab, text), 118)):
                P("     " + ("- " if k == 0 else "  ") + ln)
        if r_["bound"]:
            mtxt = ("%.4f W under its conservative assumption alone (stack A otherwise, cold end)" % r_["margin_w"]) if r_["margin_w"] is not None \
                else "%.1f K of junction" % r_["margin_k"]
            wrapP("     - ", "       ", "margin kept: %s; break-even %s" % (mtxt, r_["breakeven"]))
    cs = R["cons"]
    unres = [r_["id"] for r_ in R["qual_rows"] if r_["bound"] and not r_["resolved"]]
    wrapP("   ", "   ", "THE RESULT: %s on %s. %.4f W (cold) and %.4f W (hot) are calculated results under the assumptions listed below. "
          "Under each unresolved row's conservative assumption alone the cold corner reads %.4f / %.4f / %.4f W (EA2 / LINE / TCR; "
          "TJ moves no figure while the junction stays inside -40 to 125 C), and all of them together with the resistors' drifts "
          "%.4f W (stack C with RSENSE1's cold TCR at %.0f ppm/K): margin %.4f W. The design floor stack C itself reads %.4f / %.4f W "
          "(cold / hot)" % (R["bound_status"], ", ".join(unres), R["main_chk"][0][1][0], R["main_chk"][1][1][0], cs["ea2"], cs["line"],
                            cs["tcr"], cs["joint"], cs["tcr_cons"] * 1e6, 100.0 - cs["joint"], R["chk_floor"][0][1][0], R["chk_floor"][1][1][0]))
    P("   THE ASSUMPTIONS OF 96.25 W (stack A), in one list:")
    for k, a in enumerate((
            "8705af's full-range rows for the I grade: the IMON_IN regulation 1.187 / 1.229 V and A7's gm 0.94 / 1.06 mmho, with U5's junction inside -40 to 125 C (estimated at most %.1f C)" % R["tj_hot"],
            "the IMON_IN line regulation at its printed maximum (0.005 %/V, 25 C, not switching), applied while switching and at both ends (ASSUMPTION)",
            "EA2's gain at its typical 130 V/V as its bound, with VC anywhere in its absolute maximum range -0.3 to 2.2 V (ASSUMPTION)",
            "RSENSE1 15 mOhm +-1 %% and +-50 ppm/K, the TCR printed for +25 to +125 C applied at -20 C (ASSUMPTION); its hot end %.1f C by the derating line (INFERRED)" % END[1][1],
            "RIMON_IN 23.2k +-0.1 %, +-25 ppm/K (tested from -55 to +125 C); the resistors' soldering and life drifts not stacked (they are in C and D)",
            "the envelope: the input from the hold's lowest %.3f V to REQ-016's 25 V, ambient -20 to +40 C (REQ-024), inside air at most %.1f C (pcb_envelope.yaml)" % (min(R["hb"][0], R["hb2"][0], R["hb3"][0], R["hb4"][0]), R["t_air"]),
            "nothing in series with CSPIN or CSNIN (p.30): R59's pads are their Kelvin taps (a layout obligation)",
            "steady state; transients are 7b.9t's",
            "the setting realised as drafted: R59 15 mOhm and R16 23.2k with C65 (the drafts applied in a circuit round)"), 1):
        for j, ln in enumerate(textwrap.wrap(a, 114)):
            P("     %s %s" % (("%d." % k) if j == 0 else "  ", ln))
    P("   WHY THE CORNERS BOUND THE PERMITTED RANGE")
    P("     - the input voltage: P = v x I_set x [Vref (1 + ls lam (v - 12)) + es dVC / G] / (Vref_typ gm r1 r2); its slope in v is")
    P("       I_set [Vref (1 + ls lam (2v - 12)) + es dVC / G] / (Vref_typ gm r1 r2), whose bracket is at least %.6f V (stack A) and" % R["dpdv"][0])
    P("       %.6f V (stack C) at every vertex over %.3f to 25 V: the power rises with v, so 25 V is the worst; no loaded voltage" % (
        R["dpdv"][1], min(R["hb"][0], R["hb2"][0], R["hb3"][0], R["hb4"][0])))
    P("       exceeds REQ-016's 25 V open circuit (the panel is PV_P's only source and in discontinuous mode M4 is held off on reverse")
    P("       current, p.18); the hold's lowest is the floor (the corner there %.4f W). The dense check (0.01 V) of each stack finds" % R["p_hold_lo"])
    P("       its worst at the 25 V vertex")
    P("     - every tolerance direction: P is monotonic in each term (up in Vref, in the line term for v above 12 V, in the EA2 term;")
    P("       down in gm, RSENSE1 and RIMON_IN), so the 64 vertices an end hold the extremes; a resistor's low end 1 - a|T - 25| is")
    P("       least at the end of its temperature span farthest from 25 C, so the two ends are enough")
    P("     - temperature: the air from %.0f C (no self-heating; self-heating only moves a part toward 25 C there) to %.1f C plus" % (R["t_cold"], R["t_air"]))
    P("       RSENSE1's own rise (%.1f C); the LT8705A rows are full range, so U5's junction enters only as the condition -40 to" % END[1][1])
    tb = ["%.1f C" % t_ if t_ is not None else "past its 170 C rating" for t_ in R["rs_t_be"]]
    P("       125 C. RSENSE1 would have to reach %s (stack A) or %s (stack C) for the corner to reach 100 W:" % tuple(tb))
    P("       a board hot spot beside L1 and the FETs is covered by that much")
    P("   STATES OUTSIDE THE CORNERS")
    o_ = R["outside"]
    P("     - below -20 C ambient: outside REQ-024's -20 to +40 C. Computed for information at -40 C (the I grade's least junction):")
    P("       the candidate's open circuit reaches %.2f V there, outside REQ-016's window; the corner at that voltage with both" % o_["voc40"])
    P("       resistors at -40 C reads %.4f W under stack A" % o_["p40"])
    P("     - a source step (a panel plugged in live): TRK_VIN's %.1f uF (NETLIST: C11, C12, C13, C14, C15, C64) charge through R59 at" % (o_["c_vin"] * 1e6))
    P("       most the panel's short circuit, %.1f mJ at 25 V; start-up ramps VC by the soft start (p.15). Bench 7b.9t" % (o_["e_caps"] * 1e3))
    P("     - an irradiance step: the candidate panel can give up to %.1f W (%.0f W +%.0f %% at 1000 W/m2, cells %.1f C at -20 C air," % (
        o_["p_panel_cold"], 100.0, 100 * o_["tol_p"], o_["t_cell_cold"]))
    P("       its -0.35 %%/K, INFERRED), more than 100 W, until the IMON_IN loop settles through CIMON_IN (tau %.2f ms). Bench 7b.9t" % (R["tau"] * 1e3))
    P("     - the hold transition: VC passes between EA3 and EA2 (the diode-AND, p.14); each side's steady state is bounded above.")
    P("       The handover is a transient: bench 7b.9t")
    P("     - an unstable current loop would break the steady-state premise: bench 7b.9t with p.33's load and line steps")
    w = R["wsl"]
    wrapP("   ", "     ", "THE DESIGN OPTION THAT REMOVES AN UNKNOWN (SESSION decision): RSENSE1's cold TCR. Of the stocked 15 mOhm 1 %% 2512 "
          "parts read, only Vishay Dale's WSL2512 (%s, LCSC %s, stock %d; Document 30100, Revision 23-Nov-2023, p.2) states its TCR "
          "from -55 C: +-%.0f ppm/K, %.1f W at 70 C (HoJLR: +25 to +125 C, Ho-A0 p.4; YAGEO PA V.10 p.9 and RALEC LR IE-SP-060 p.10: "
          "the hot side only). Its printed solder-heat and life limits each carry 0.5 mOhm (p.3): %.2f %% and %.2f %% of 15 mOhm. "
          "With it, stack A reads %.4f W (RSENSE1 at %.1f C by %.0f K/W, INFERRED) and the design floor %.4f W at 23.2k; the same "
          "rule would move RIMON_IN to %s" % (
              w["model"], w["code"], w["stock"], w["tcr"] * 1e6, w["p70"], 100 * w["sold"], 100 * w["life"], w["p_a"], w["t_hot"], w["kr"],
              w["p_floor"], ("%gk (%.4f A), %.1f %% less input in every hour the limit binds" % (w["pick"][0] / 1e3, w["pick"][3], 100 * w["cost"]))
              if w["pick"] else "no stocked value"))
    wrapP("     ", "     ", "NOT TAKEN: the swap trades an unknown with a large margin (break-even %.3f ppm/K under stack C, %.1f times the "
          "printed value) for a certain loss of setting; the unknown is qualified by Milliohm's statement instead (clarification/)" % (
              R["be_tcr_cold_floor"] * 1e6, R["be_tcr_cold_floor"] / R["tcr_h"]))
    P("   CLARIFICATION REQUESTS (text for the owner to send; the session contacts no one): clarification/analog-devices-lt8705a.txt,")
    P("     clarification/milliohm-hojlr2512.txt")
    P("   PROTOTYPE MEASUREMENTS ARE DOWNSTREAM OBLIGATIONS, NOT BLOCKERS: no architecture decision depends on 7b.9, 7b.9t, 7b.10,")
    P("     7b.11, 7b.12, 7b.13 or 7b.14 (R59 at -20 C and +25 C). The current-limit mechanism holds its bound under the conservative")
    P("     assumptions above; an adverse reading changes a value (RIMON_IN, the compensation), not the mechanism or the architecture")
    return o


def main():
    R = compute()
    sys.stdout.write("\n".join(render(R)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
