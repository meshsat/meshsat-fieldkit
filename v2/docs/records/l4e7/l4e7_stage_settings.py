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
    # the fault-to-limit ratio at its least (check astra-check-l4e7q-1, B2): the fault minimum over the regulated IMON_IN at its
    # highest, the line and EA2 allowances included (stack A, and the conservative assumptions together)
    reg_a = ref_p["max"] * (1 + line_p * 1e-2 * (v_oc - V_LINE_REF)) + dvc / ea2
    reg_c = ref_p["max"] * (1 + LINE_FLOOR_MUL * line_p * 1e-2 * (v_oc - V_LINE_REF)) + dvc / (ea2 / EA2_FLOOR_DIV)
    R["fault_ratio"] = dict(reg_a=reg_a, reg_c=reg_c, a=iovm["min"] / reg_a, c=iovm["min"] / reg_c)
    # RSENSE1's cold TCR from its printed 50 to the assumed 100 ppm/K at -20 C: the sense-path loop gain moves with RSENSE1 and the
    # current at which the fault trips with 1 / RSENSE1 (p.31); the comparator's threshold voltage (p.5) does not move
    dt_c = abs(END[0][1] - 25.0)
    rs50, rs100 = 1 - tcr_h * dt_c, 1 - TCR_COLD_CONS * dt_c
    R["tcr_effects"] = dict(loop=rs100 / rs50 - 1.0, trip=rs50 / rs100 - 1.0, dt=dt_c)
    # LINE: the setpoint moves with the source voltage, a coupling path into the loop: over the envelope's swing at most
    swing = v_oc - v_lo_env
    R["line_coupling"] = dict(swing=swing, printed=line_p * swing, assumed=LINE_FLOOR_MUL * line_p * swing)
    # A7 (check B1): its gm row is guaranteed at VCSPIN - VCSNIN = 50 mV and VCSPIN = 5.025 V; the design runs CSPIN at the panel
    # voltage and about the sense voltage below. The effective gain may fall this far, other terms fixed, before 100 W
    need(raw[5], r"VCSPIN - VCSNIN = 50mV, VCSPIN = 5\.025V|VCSPIN \u2013 VCSNIN = 50mV, VCSPIN = 5\.025V", "8705af p.5 A7's test condition")
    need(raw[8], r"IMON Output Currents", "8705af p.8 the IMON output currents curve (TYPICAL, against the differential only)")
    a7_be = dict(a=[gm_lo * w[0] / p_win for _l, w, _n in R["main_chk"]], c=[gm_lo * w[0] / p_win for _l, w, _n in R["chk_floor"]],
                 joint=gm_lo * R["cons"]["joint"] / p_win)
    R["a7q"] = dict(be=a7_be, vd=R["vd_lim_hi"], cm=(v_lo_env, v_oc), cm_range=(R["csd"]["min"], R["csd"]["max"]),
                   loss=dict(a=[100 * (1 - g / gm_lo) for g in a7_be["a"]], c=[100 * (1 - g / gm_lo) for g in a7_be["c"]],
                             joint=100 * (1 - a7_be["joint"] / gm_lo)))
    # M1: the thermal coupling. The paired ends put both resistors in the same air at each end; the mixed envelope lets each take
    # its own worst end independently, and a dense air sweep (0.1 C, RSENSE1 with and without its rise) checks the pairing
    def rfac_end(tol, tcr_lo, tcr_hi, t, drifts_life, drifts_sold):
        return rfac(tol, tcr_lo if t < 25.0 else tcr_hi, t - 25.0, drifts_life, drifts_sold)

    def p_mixed(gain, lmul, drifts, tcr_cold):
        dl_h, ds_h = (life_h, sold_h) if drifts else (0.0, 0.0)
        dl_y, ds_y = ((R["life_y"][0] + R["life_y"][1] / rm), (R["sold_y"][0] + R["sold_y"][1] / rm)) if drifts else (0.0, 0.0)
        rs_lo = min(rfac_end(tol_h, tcr_cold, tcr_h, t_, dl_h, ds_h) for t_ in (END[0][1], END[1][1]))
        rm_lo = min(rfac_end(tol_y, tcr_y, tcr_y, t_, dl_y, ds_y) for t_ in (END[0][2], END[1][2]))
        return v_oc * i_nom * corner_k(v_oc, gain, lmul, rs_lo, rm_lo)

    def p_sweep(gain, lmul, drifts, tcr_cold):
        dl_h, ds_h = (life_h, sold_h) if drifts else (0.0, 0.0)
        dl_y, ds_y = ((R["life_y"][0] + R["life_y"][1] / rm), (R["sold_y"][0] + R["sold_y"][1] / rm)) if drifts else (0.0, 0.0)
        best = 0.0
        for k in range(int(round((t_air - t_cold) * 10)) + 1):
            ta = t_cold + 0.1 * k
            for rise in (0.0, END[1][1] - t_air):
                rs_lo = rfac_end(tol_h, tcr_cold, tcr_h, ta + rise, dl_h, ds_h)
                rm_lo = rfac_end(tol_y, tcr_y, tcr_y, ta, dl_y, ds_y)
                best = max(best, v_oc * i_nom * corner_k(v_oc, gain, lmul, rs_lo, rm_lo))
        return best
    R["thermal"] = dict(
        paired=dict(a=R["main_chk"][0][1][0], c=R["chk_floor"][0][1][0], joint=R["cons"]["joint"]),
        mixed=dict(a=p_mixed(ea2, 1.0, False, tcr_h), c=p_mixed(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, tcr_h),
                   joint=p_mixed(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, TCR_COLD_CONS)),
        sweep=dict(a=p_sweep(ea2, 1.0, False, tcr_h), c=p_sweep(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, tcr_h),
                   joint=p_sweep(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, TCR_COLD_CONS)))
    if max(R["thermal"]["mixed"].values()) > p_win:
        refuse(4, "the mixed-temperature envelope takes a corner over 100 W")
    need(raw[34], r"reaches approximately 165\u00b0C", "8705af p.34 the thermal shutdown")
    # (e) the hold's lowest against the 25 V corner (why EA3 and the FBIN bias do not reach the bound)
    def p_at(v, gain, lmul, drifts, tcr_cold):
        """The worst power at input v over both ends' resistor values and both line signs, the named stack (check M2: matching stacks)."""
        dl_h, ds_h = (life_h, sold_h) if drifts else (0.0, 0.0)
        dl_y, ds_y = ((R["life_y"][0] + R["life_y"][1] / rm), (R["sold_y"][0] + R["sold_y"][1] / rm)) if drifts else (0.0, 0.0)
        rs_lo = min(rfac(tol_h, tcr_cold if t_ < 25.0 else tcr_h, t_ - 25.0, dl_h, ds_h) for t_ in (END[0][1], END[1][1]))
        rm_lo = min(rfac(tol_y, tcr_y, t_ - 25.0, dl_y, ds_y) for t_ in (END[0][2], END[1][2]))
        return max(v * i_nom * RP.i_factor(v, ref_p["max"], vref_n, line_p * lmul, ls, dvc / gain, 1, gm_lo, rs_lo, rm_lo) for ls in (-1, 1))
    R["p_hold_lo"] = dict(c=p_at(v_lo_env, ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, tcr_h),
                          joint=p_at(v_lo_env, ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, 2.0 * tcr_h), a=p_at(v_lo_env, ea2, 1.0, False, tcr_h))
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
    p_panel_soak = cspr["p"] * (1 + tol_p) * (1 + cspr["gamma_p"] * (t_cold - 25.0))     # a cold-soaked cell at -20 C, 1000 W/m2
    R["outside"] = dict(voc40=voc40, p40=p40, c_vin=caps, e_caps=0.5 * caps * v_oc ** 2, t_cell_cold=t_cell_cold, p_panel_cold=p_panel_cold,
                        tol_p=tol_p, p_panel_soak=p_panel_soak, gamma=cspr["gamma_p"])
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
    WARRANT = ("a limit the manufacturer warrants, with the conditions it applies to; characterization over production lots is "
               "supporting evidence, not a production guarantee, and the row stays CONDITIONAL until a warranted limit exists")
    rows = [
        dict(id="EA2", name="EA2's gain and VC's operating range", bound=True, stability=True, protection=False, other="energy, only in hours the limit binds",
             small={},
             why_bound="the regulated IMON_IN moves by (VC - 1.2 V) / gain (p.5, p.2): %.4f W at 130 V/V against %.4f W with the term left out (stack A, cold)" % (
                 R["main_chk"][0][1][0], R["chk_printed"][0][1][0]),
             why_stability="EA2 drives VC through the compensation network in the input-current loop; with no printed minimum gain or gm the loop's margin is not guaranteed (p.33: the loop stability is affected by a number of factors)",
             why_protection="the IMON_IN fault is a comparator on IMON_IN itself (p.5, 1.55 V minimum, full range), not through EA2; only a gain under %.2f V/V would hold the regulated point at the fault, which stops switching (the safe side)" % R["g_fault"],
             sheet="p.5 EA2 gain 130 V/V and gm 185 umho, typical only; p.4 the IMON_IN regulation, full range, printed at VC = 1.2 V; p.2 VC's absolute maximum -0.3 to 2.2 V; p.7 'Inductor Current Sense Voltage at Minimum Duty Cycle' against VC and p.8 'Maximum VC vs SS' plot VC within 0.5 to 2.0 V (TYPICAL, TA = 25 C; not a limit); p.31 the current-limiting text names 1.208 V typical and no gain bound",
             guaranteed=None,
             conservative="EA2 at least 65 V/V (half its typical) with VC anywhere in its absolute maximum range (the replay's allowance doubled)",
             qualification="Analog Devices: EA2's minimum gain, or the IMON_IN regulation point's shift with VC, over -40 to 125 C junction, as " + WARRANT + "; a bench reading of a few units (7b.10) checks the design only",
             margin_w=p_win - R["cons"]["ea2"], breakeven="%.6f V/V (stack A, cold), %.6f V/V (stack C's other terms, cold)" % (R["be_gain"][(1.0, False)][0], R["be_gain"][(2.0, True)][0]),
             resolved=False, clarification="analog-devices-lt8705a.txt"),
        dict(id="A7", name="A7's gain outside its test point (50 mV differential, CSPIN at 5.025 V)", bound=True, stability=True, protection=True,
             other="energy, only in hours the limit binds",
             small={},
             why_bound="the limit is 1.208 V / (gm x RSENSE1 x RIMON_IN) (p.31): the effective gain enters in proportion. The full-range gm row (0.94 / 1.06 mmho, E and I) is printed at a 50 mV differential with CSPIN at 5.025 V; the design runs CSPIN at the panel voltage, %.3f to %.0f V, and up to %.1f mV across RSENSE1. The CSPIN and CSNIN ranges, 1.5 to 80 V common mode and %.0f to %.0f mV differential (p.5), are operating ranges, not a gain guarantee" % (
                 R["a7q"]["cm"][0], R["a7q"]["cm"][1], 1e3 * R["a7q"]["vd"], R["a7q"]["cm_range"][0], R["a7q"]["cm_range"][1]),
             why_stability="the sense path's gain enters the input-current loop in proportion; an error outside the test point moves the loop gain by the same fraction",
             why_protection="the fault comparator's threshold voltage on IMON_IN (p.5) does not move; the input current at which it trips moves inversely with the effective gain, as the limit does",
             sheet="p.5 A7 gm 0.95 / 1.05 mmho at 25 C and 0.94 / 1.06 mmho over the full range (E, I), each at VCSPIN - VCSNIN = 50 mV and VCSPIN = 5.025 V; p.5 CSPIN and CSNIN 1.5 to 80 V common mode and -100 to 100 mV differential (operating ranges); p.8 'IMON Output Currents' plots the output current against the differential only (TYPICAL, TA = 25 C); no curve against common mode, no transfer-error or offset row",
             guaranteed="the gm limits at the test point, over the full temperature range; nothing printed at the design's common mode and differential, or while switching",
             conservative="the test-point limits apply at the design's common mode and differential while switching (an extrapolation, ASSUMPTION)",
             qualification="Analog Devices: A7's transfer error (gm and offset) over the common mode, the differential, -40 to 125 C junction and switching the design uses, as " + WARRANT,
             margin_w=p_win - R["main_chk"][0][1][0],
             breakeven="the effective gain may fall to %.6f mmho (%.4f %% under 0.94) under stack A, %.6f mmho (%.4f %%) under stack C and %.6f mmho (%.4f %%) under every conservative assumption together, other terms fixed (cold)" % (
                 R["a7q"]["be"]["a"][0], R["a7q"]["loss"]["a"][0], R["a7q"]["be"]["c"][0], R["a7q"]["loss"]["c"][0], R["a7q"]["be"]["joint"], R["a7q"]["loss"]["joint"]),
             resolved=False, clarification="analog-devices-lt8705a.txt"),
        dict(id="LINE", name="the IMON_IN reference's line regulation while switching and at temperature", bound=True, stability=True, protection=False,
             other="energy, a fraction of a percent of the limit, only in hours it binds",
             small={"stability": "the setpoint moves with the source voltage: over the envelope's %.3f V swing at most %.4f %% printed, %.4f %% assumed" % (
                 R["line_coupling"]["swing"], R["line_coupling"]["printed"], R["line_coupling"]["assumed"])},
             why_bound="the reference moves with VIN from the 12 V it is printed at: at 25 V the printed maximum moves the corner by %.4f W" % (R["main_chk"][0][1][0] - p_cold(ea2, 0.0, False, tcr_h)),
             why_stability="small, not zero: the reference's VIN dependence couples a moving source voltage into the regulated current (a feedforward path, at most %.4f %% of the setpoint per volt assumed); the loop's margin is set elsewhere" % (
                 LINE_FLOOR_MUL * line_p),
             why_protection="the regulated point would reach the IMON_IN fault minimum only at %.0f times the printed maximum" % R["k_fault"],
             sheet="p.4 0.002 / 0.005 %/V, VIN 12 to 80 V, not switching, at 25 C (no bullet); p.4 the regulation itself is a full-range row at VIN = 12 V, so its temperature drift at 12 V is guaranteed; p.7 'Feedback Voltages' against temperature at VC = 1.2 V is TYPICAL",
             guaranteed="the full-range IMON_IN regulation row covers temperature at VIN = 12 V; the VIN dependence while switching and away from 25 C is not printed",
             conservative="twice the printed maximum (0.010 %/V), either sign, at every temperature and while switching",
             qualification="Analog Devices: the IMON_IN reference's line regulation while switching, over -40 to 125 C junction, as " + WARRANT,
             margin_w=p_win - R["cons"]["line"], breakeven="%.1f times the printed maximum (stack A, cold); %.1f with EA2 at 65 V/V" % R["be_line"],
             resolved=False, clarification="analog-devices-lt8705a.txt"),
        dict(id="TCR", name="RSENSE1's TCR below +25 C", bound=True, stability=True, protection=True,
             other="energy, a fraction of a percent of the limit, only in hours it binds",
             small={"stability": "the sense-path loop gain moves with RSENSE1: %+.4f %% from 50 to %.0f ppm/K at -20 C" % (100 * R["tcr_effects"]["loop"], TCR_COLD_CONS * 1e6),
                    "protection": "the current at which the fault trips moves with 1 / RSENSE1 (p.31): %+.4f %% from 50 to %.0f ppm/K at -20 C; the comparator's threshold does not move" % (
                        100 * R["tcr_effects"]["trip"], TCR_COLD_CONS * 1e6)},
             why_bound="RSENSE1 sits in the limit's denominator; at -20 C its TCR sets its low end",
             why_stability="small, not zero: the sense-path loop gain is proportional to RSENSE1, %+.4f %% from 50 to %.0f ppm/K at -20 C; the loop's margin is set by the compensation" % (
                 100 * R["tcr_effects"]["loop"], TCR_COLD_CONS * 1e6),
             why_protection="small, not zero: the fault comparator's threshold voltage (IMON_IN 1.55 / 1.61 / 1.67 V, p.5) does not move, but the input current at which it trips is proportional to 1 / RSENSE1 (p.31), %+.4f %% from 50 to %.0f ppm/K at -20 C. The fault-to-limit ratio does not depend on RSENSE1; at its least it is %.6f (stack A, regulation at most %.9f V) and %.6f with every conservative assumption (regulation at most %.9f V)" % (
                 100 * R["tcr_effects"]["trip"], TCR_COLD_CONS * 1e6, R["fault_ratio"]["a"], R["fault_ratio"]["reg_a"], R["fault_ratio"]["c"], R["fault_ratio"]["reg_c"]),
             sheet="HoJLR2512 Ho-A0 p.2 +-50 ppm/K (2 to 500 mOhm); p.4 the TCR test spans +25 to +125 C only; the catalogue prints no TCR for C2903494",
             guaranteed=None,
             conservative="+-%.0f ppm/K below +25 C (twice the printed hot-side value)" % (TCR_COLD_CONS * 1e6),
             qualification="Milliohm: the HoJLR2512 TCR from -40 to +25 C, as " + WARRANT + "; a bench reading of R59 at -20 C (7b.14) checks the design only",
             margin_w=p_win - R["cons"]["tcr"], breakeven="%.3f ppm/K (stack A), %.3f ppm/K (stack C)" % (R["be_tcr_cold"] * 1e6, R["be_tcr_cold_floor"] * 1e6),
             resolved=False, clarification="milliohm-hojlr2512.txt"),
        dict(id="HOLD", name="EA3's gain and the FBIN bias", bound=False, stability=True, protection=False, other="energy (the hold band)",
             small={},
             why_bound="they set the hold, the envelope's low end %.6f V, where the matching stacks (each resistor at its worst end) read %.4f W (A), %.4f W (C, drifts included) and %.4f W (every conservative assumption) against %.4f W, %.4f W and %.4f W at 25 V: the power rises with the input voltage at every vertex" % (
                 v_lo_env, R["p_hold_lo"]["a"], R["p_hold_lo"]["c"], R["p_hold_lo"]["joint"], R["main_chk"][0][1][0], R["chk_floor"][0][1][0], R["cons"]["joint"]),
             why_stability="EA3 closes the input-voltage loop through VC; its margin is part of the hold's bench row",
             why_protection="the hold is a regulation, not a protection; FBOUT's overvoltage and the IMON_IN fault are other pins",
             sheet="p.4 EA3 90 V/V and FBIN bias 10 nA, typical only; p.4 FBIN regulation 1.184 / 1.226 V, full range (I grade), at VC = 1.2 V",
             guaranteed="the FBIN reference is full range; the gain and the bias are typical",
             conservative="EA3 at half its typical with the resistors' drifts: the hold inside %.3f to %.3f V; the bias at ten times its typical moves the lower corner by %.1f mV" % (
                 hb3[0], hb3[2], 1e3 * (R["bias_rows"][2][1] - R["bias_rows"][1][1])),
             qualification="none for the bound; the hold's energy rows carry them as sensitivities and 7b.12 reads the hold",
             margin_w=None, breakeven=None, resolved=False, clarification=None),
        dict(id="TJ", name="U5's junction temperature", bound=True, stability=False, protection=True, other="lifetime (Note 3: derated above 125 C)",
             small={},
             why_bound="every LT8705A row the corner uses is a full-range row, guaranteed for the I grade from -40 to 125 C junction (p.6 Note 3); the bound needs only the junction inside that range, not its value",
             why_stability="the loop's gains move with temperature inside the unprinted EA2 and A7 rows already carried above",
             why_protection="the overtemperature protection acts at approximately 165 C (p.34, approximate): the estimate stays %.1f K under it" % (165.0 - R["tj_hot"]),
             sheet="p.2 theta-JA 34 C/W (UHF, a package figure on the maker's board); p.3 the VIN quiescent current, 4.2 mA maximum, printed at 25 C, not switching, EXTVCC = 0; p.6 Note 3 and Note 8; p.34 the CLKOUT method (+-10 C) and the thermal shutdown at approximately 165 C",
             guaranteed="the I grade's rows hold over -40 to 125 C junction; no junction temperature is printed for this board",
             conservative="an INFERRED estimate, TJ about %.1f C: the maximum gate charge at 10 V for all four FETs at the highest oscillator frequency, the VIN quiescent maximum (printed at 25 C, not switching, EXTVCC = 0, so an extrapolation), EXTVCC at L4-E5's %.2f V ceiling and theta-JA 34 C/W (board-dependent) in %.1f C air; not a demonstrated upper bound" % (
                 R["tj_hot"], R["ceil5"][2], t_air),
             qualification="a design verification of board E's thermal path (7b.13 by p.34's method, +-10 C), with the margin covering the unit spread the maximum gate charge already bounds",
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
    # ================================================================== 11: THE CONTROL DECISION (L4-E7R, the owner's instruction of
    # 1 October 2026; second round after checks/astra-check-l4e7r-1.md): the verdict on the present limit; at most three approaches,
    # each bound with every term classed by the maker's row for its own condition (a term no row bounds is CONDITIONAL and carried by
    # its break-even, never by a common multiplier); the chosen arrangement's static bound, its dynamics and averaging basis, its
    # supply sequencing, its coordination with the regulation, its energy on SC-37's day and a bright day, and the solar entry's
    # protection against the derived disturbance (each SESSION decision named where it is taken)
    INA, TPS = "v2/vendor/ti/held/ti-ina250-sbos511c.pdf", "v2/vendor/ti/held/ti-tps3701-sbvs240c.pdf"
    I169, T38 = "v2/vendor/ti/held/ti-ina169-sbos181f.pdf", "v2/vendor/ti/ti-tps3808.pdf"
    LM69, SMC = "v2/vendor/ti/ti-lm5069.pdf", "v2/vendor/power/littelfuse-smcj-series-tvs.pdf"
    ZA = "v2/vendor/power/held/panasonic-za-eehza1h330xp-2017-11-07.pdf"
    for rel_, want_ in ((INA, "4690d49c0e10739b6dfc1da4d56bc2eeda8276d9b8816fb7b90db539c1eb0868"),
                        (TPS, "27c94a6c3a243bf539e98942d26f0bd9ed979c5775c12cf86b7c1a8c3d7d9560"),
                        (I169, "dbb74b6cdc5431353f17b044b7d762df1f2f9049d03d2d1611a53058e570d62c"),
                        (T38, "74d889c0f68af88032f1633c26381817cc03e10d9fd3b4c177a044ad3ed86eed"),
                        (LM69, "d60d8106a6e8113900ff8b9576dd959942fa7169742baf0beeb30684d4d64681"),
                        (SMC, "6e610db955ed876306999009c62b242f7de9bb05e2cd9717288a96586a5093ea"),
                        (ZA, "43628e509458b8995a5c5e1ade2334286c5acfddf859bf9aa4daf59d5653258a")):
        if sha(rel_) != want_:
            refuse(2, "%s is not the pinned file (fetch it: v2/docs/records/l4e7/fetch_held_back.py)" % rel_)
    # ---- the INA250 (approach B): every row read, then classed by its own condition
    i5, i6, i15 = flat(pg(INA, 5)), flat(pg(INA, 6)), flat(pg(INA, 15, False))
    need(i5, r"At TA = 25.C, VS = 5 V, VIN\+ = 12 V, VREF = 2\.5 V, ISENSE = IN\+ = 0 A, unless otherwise noted", "INA250 p.5 the test conditions")
    cmr = float(need(i5, r"INA250A2, VIN\+ = 0 V to 36 V, (\d+) \d+ TA = .40.C to 125.C", "INA250 p.5 CMR A2").group(1))
    ios = float(need(i5, r"INA250A2, ISENSE = 0 A \u00b1[\d.]+ \u00b1(\d+)", "INA250 p.5 offset A2").group(1)) * 1e-3
    dios = float(need(i5, r"dIOS/dT RTI versus temperature TA = .40.C to 125.C \d+ (\d+) \u03bcA/.C", "INA250 p.5 offset drift").group(1)) * 1e-6
    psr = float(need(i5, r"PSR VS = 2\.7 V to 36 V, TA = .40.C to 125.C \u00b1[\d.]+ \u00b1(\d+) mA/V", "INA250 p.5 PSR").group(1)) * 1e-3
    rsh_n = float(need(i5, r"Shunt resistance [\d.]+ (\d+) [\d.]+", "INA250 p.5 shunt").group(1)) * 1e-3
    st = need(i5, r"Shunt short time overload ISENSE = 30 A for 5 seconds \u00b1([\d.]+)% Shunt thermal shock .65.C to 150.C, 500 cycles \u00b1([\d.]+)% "
              r"Shunt resistance to solder 260.C solder, 10 s \u00b1([\d.]+)% heat Shunt high temperature 1000 hours, TA = 150.C \u00b1([\d.]+)% "
              r"exposure Shunt cold temperature 24 hours, TA = .65.C \u00b1([\d.]+)%", "INA250 p.5 the shunt's stress rows (typical only)").groups()
    stress_sh = sum(float(x) for x in st) / 100.0
    nl = float(need(i6, r"Nonlinearity error ISENSE = 0\.5 A to 10 A \u00b1([\d.]+)%", "INA250 p.6 nonlinearity (typical only)").group(1)) / 100.0
    ro = float(need(i6, r"RO Output impedance ([\d.]+) [\u2126\u03a9]", "INA250 p.6 output impedance (typical only)").group(1))
    g_ina = float(need(i6, r"INA250A2 (\d+) mV/A", "INA250 p.6 gain A2").group(1)) * 1e-3
    eg = float(need(i6, r"System gain error\(6\) \u00b1([\d.]+)% TA = .40.C to 125.C", "INA250 p.6 full-range system gain error").group(1)) / 100.0
    need(flat(pg(INA, 6, False)), r"System gain error does not include the stress related characteristics", "INA250 p.6 note 6")
    iq_ina = float(need(i6, r"IQ Quiescent current TA = .40.C to 125.C \d+ (\d+) \u03bcA", "INA250 p.6 IQ").group(1)) * 1e-6
    ib_ina = float(need(i5, r"IB Input bias current IB\+, IB., ISENSE = 0 A \u00b1[\d.]+ \u00b1(\d+) \u03bcA", "INA250 p.5 IB (25 C)").group(1)) * 1e-6
    abs_ina = float(need(flat(pg(INA, 4)), r"Analog inputs \(IN\+, IN.\) Common-mode GND . 0\.3 (\d+)", "INA250 p.4 IN+ and IN- absolute maximum").group(1))
    need(i15, r"For unidirectional operation, tie the REF pin to ground", "INA250 p.15 REF to ground for unidirectional operation")
    # ---- the TPS3701 (both B and C): its rows hold over TJ -40 to 125 C and VDD 1.8 to 36 V
    t5, t6 = flat(pg(TPS, 5)), flat(pg(TPS, 6))
    need(t5, r"Over the operating temperature range of TJ = .40.C to \+125.C, 1\.8 V \u2264 VDD < 36 V", "TPS3701 p.5 the full-range header")
    vit = need(t5, r"VIT\+\(INB\) INB pin positive input threshold voltage VDD = 1\.8 V to 36 V (\d+) (\d+) (\d+) mV", "TPS3701 p.5 VIT+(INB)").groups()
    vth = (float(vit[0]) * 1e-3, float(vit[2]) * 1e-3)
    via = need(t5, r"VIT.\(INA\) INA pin negative input threshold voltage VDD = 1\.8 V to 36 V (\d+) (\d+) (\d+) mV", "TPS3701 p.5 VIT-(INA)").groups()
    via_p = need(t5, r"VIT\+\(INA\) INA pin positive input threshold voltage VDD = 1\.8 V to 36 V (\d+) ([\d.]+) (\d+) mV", "TPS3701 p.5 VIT+(INA)").groups()
    vtha = (float(via[0]) * 1e-3, float(via_p[2]) * 1e-3)            # INA asserts below the first; releases above at most the second
    iin_t = float(need(t5, r"VDD = 1\.8 V and 36 V, VINA, VINB = 6\.5 V .(\d+) \+1 \+\d+ nA", "TPS3701 p.5 input current").group(1)) * 1e-9
    vol_max = float(need(t5, r"VDD = 5 V, IOUT = 5 mA \d+ (\d+) mV", "TPS3701 p.5 VOL").group(1)) * 1e-3
    vdd_t = float(need(t5, r"VDD Supply voltage range ([\d.]+) 36 V", "TPS3701 p.5 VDD").group(1))
    uvlo_t = need(t5, r"UVLO Undervoltage lockout \(2\) VDD falling ([\d.]+) ([\d.]+) ([\d.]+) V", "TPS3701 p.5 UVLO").groups()
    need(t5, r"When VDD falls below UVLO, OUTA is driven low and OUTB goes to high impedance", "TPS3701 p.5 note 2")
    st_t = float(need(flat(pg(TPS, 6, False)), r"VDD must exceed 1\.8 V for at least (\d+) [\u00b5\u03bc]s \(typical\)", "TPS3701 p.6 note 2 (start)").group(1)) * 1e-6
    tpd_lh = float(need(t6, r"tpd\(LH\) Low-to-high propagation delay \(1\) .*?([\d.]+) [\u00b5\u03bc]s", "TPS3701 p.6 tpd(LH) (typical)").group(1)) * 1e-6
    need(flat(pg(TPS, 6, False)), r"High-to-low and low-to-high refers to the transition at the input pins", "TPS3701 p.6 note 1 (the input edge)")
    # ---- the TPS3808 (both B and C): the supervisor, its reset delay with CT to VDD, its power-up reset
    s6, s7, s4 = flat(pg(T38, 6)), flat(pg(T38, 7)), flat(pg(T38, 4))
    need(s6, r"1\.7V \u2264 VDD \u2264 6\.5V, RLRESET = 100k\u2126, CLRESET = 50pF, over operating temperature range \(TJ = .40.C to 125.C\)", "TPS3808 p.6 the header")
    acc38 = float(need(s6, r"VIT \u2264 3\.3V .([\d.]+)% \u00b10\.5% ([\d.]+)%", "TPS3808 p.6 VIT accuracy (VIT up to 3.3 V, full range)").group(2)) / 100.0
    hys38 = float(need(s6, r"Fixed versions 1% ([\d.]+)%", "TPS3808 p.6 VHYS of the fixed versions").group(1)) / 100.0
    vit38 = float(need(flat(pg(T38, 3)), r"TPS3808G33 3\.3V ([\d.]+)V", "TPS3808 p.3 the G33 threshold").group(1))
    vpor38 = float(need(s6, r"VPOR Power-up reset voltage\(2\) VOL \(max\) = 0\.2V, I RESET = 15\u03bcA ([\d.]+)", "TPS3808 p.6 VPOR").group(1))
    need(flat(pg(T38, 6, False)), r"Trise\(VDD\) \u2265 15 \u03bcs/V", "TPS3808 p.6 the ramp condition of VPOR")
    vol38 = float(need(s6, r"1\.8V \u2264 VDD \u2264 6\.5V, IOL = 1mA ([\d.]+) V", "TPS3808 p.6 VOL at 1 mA").group(1))
    rmr38 = float(need(s6, r"R MR MR Internal pullup resistance (\d+) \d+ k\u2126", "TPS3808 p.6 MR pull-up minimum").group(1)) * 1e3
    td38 = need(s7, r"CT = VDD (\d+) (\d+) (\d+) ms", "TPS3808 p.7 td with CT to VDD").groups()
    td_min = float(td38[0]) * 1e-3
    vdd38 = float(need(s6, r"TJ < 125.C ([\d.]+) 6\.5 V VDD Input supply range", "TPS3808 p.6 VDD").group(1))
    ioh38 = float(need(s6, r"IOH RESET leakage current V RESET = 6\.5V, RESET not asserted (\d+) nA", "TPS3808 p.6 RESET leakage").group(1)) * 1e-9
    need(s4, r"Connecting this pin to VDD through a 40k\u2126 to 200k\u2126 resistor", "TPS3808 p.4 CT to VDD through 40k to 200k")
    need(s4, r"Driving the manual reset pin \( MR\) low asserts RESET", "TPS3808 p.4 MR")
    mr_ns = float(need(s7, r"MR to RESET VIH = 0\.7VDD, VIL = 0\.3VDD (\d+) ns", "TPS3808 p.7 MR to RESET (typical)").group(1)) * 1e-9
    # ---- the INA169 (approach C): every row at TA -40 to 85 C, V+ = 5 V, VIN+ = 12 V, ROUT = 25 kOhm; CMR and PSR printed at VSENSE = 50 mV
    j6, j4 = flat(pg(I169, 6)), flat(pg(I169, 4))
    need(j6, r"INA169: all other characteristics at TA = .40.C to \+85.C V\+ = 5 V, VIN\+ = 12 V, and ROUT = 25 k[\u2126\u03a9]", "INA169 p.6 the header")
    cmr169 = float(need(j6, r"INA169: (\d+) 120 dB VIN\+ = 2\.7 V to 60 V, VSENSE = 50 mV", "INA169 p.6 CMR at VSENSE = 50 mV").group(1))
    vos169 = float(need(j6, r"INA169 \u00b10\.2 \u00b1(\d+) vs\. temperature", "INA169 p.6 offset (RTI)").group(1)) * 1e-3
    psr169 = float(need(j6, r"INA169: 0\.1 (\d+) \u00b5V/V V\+ = 2\.7 V to 60 V, VSENSE = 50 mV", "INA169 p.6 PSR at VSENSE = 50 mV").group(1)) * 1e-6
    gm169 = need(j6, r"VSENSE = 10 mV . 150 mV (\d+) 1000 (\d+) \u00b5A/V", "INA169 p.6 transconductance").groups()
    gm169 = (float(gm169[0]) * 1e-6, float(gm169[1]) * 1e-6)                 # A/V
    nl169 = float(need(j6, r"INA169 \u00b10\.01% \u00b1([\d.]+)%", "INA169 p.6 nonlinearity").group(1)) / 100.0
    iq169 = float(need(j6, r"Quiescent current VSENSE = 0, IO = 0 \d+ (\d+) \u00b5A", "INA169 p.6 quiescent").group(1)) * 1e-6
    sw169 = float(need(j6, r"Swing to power supply, V\+ \(V\+\) . [\d.]+ \(V\+\) . ([\d.]+)", "INA169 p.6 swing to V+").group(1))
    swcm169 = float(need(j6, r"Swing to common-mode, VCM VCM . [\d.]+ VCM . ([\d.]+)", "INA169 p.6 swing to VCM").group(1))
    need(j6, r"Specification, TMIN to TMAX INA169 .40 85 .C", "INA169 p.6 the specified range")
    need(j6, r"Defined as the amount of voltage \(VSENSE\) to drive the output to zero", "INA169 p.6 note 1 (the offset)")
    abs169 = need(j4, r"\(2\) Common-mode .0\.3 (\d+) V Analog inputs, INA169 Differential \(VIN\+\) . \(VIN.\) .40 (\d+) V", "INA169 p.4 inputs' absolute maxima").groups()
    abs169 = (float(abs169[0]), float(abs169[1]))
    ipin169 = float(need(j4, r"Input current into any pin (\d+) mA", "INA169 p.4 input current into any pin").group(1)) * 1e-3
    vsabs169 = float(need(j4, r"Supply voltage, VS INA169 .0\.3 (\d+) V", "INA169 p.4 V+ absolute maximum").group(1))
    bw169 = float(need(j6, r"Bandwidth ROUT = 20 k[\u2126\u03a9] (\d+) kHz", "INA169 p.6 bandwidth at 20 kOhm (typical)").group(1)) * 1e3
    # ---- the LT8705A rows the arrangement uses (all printed; none is an answer the drafts ask for)
    ldo = need(flat(p3), r"LDO33 Pin Voltage 5mA from LDO33 Pin l ([\d.]+) ([\d.]+) ([\d.]+) V", "8705af p.3 LDO33").groups()
    v_ldo = (float(ldo[0]), float(ldo[2]))
    ilim33 = float(need(flat(p3), r"LDO33 Pin Current Limit l (\d+) [\d.]+ (\d+) mA", "8705af p.3 LDO33 current limit").group(2)) * 1e-3
    uvi = float(need(flat(p3), r"INTVCC, GATEVCC Undervoltage Lockout INTVCC Falling, GATEVCC Connected to INTVCC l ([\d.]+)", "8705af p.3 INTVCC lockout").group(1))
    swen_r = RP.ec_row(pages, 4, "SWEN Rising Threshold Voltage (Note 5)", None)
    need(raw[12], r"SWEN \(Pin 36 QFN Only\): Switch Enable Pin\. Tie high to enable switching\. Ground to disable switching\. Don.t float this pin", "8705af p.12 SWEN")
    need(raw[14], r"In the initialize state, the SS \(soft-start\) pin is pulled low", "8705af p.14 the initialize state")
    need(raw[15], r"INITIALIZE . SS PULLED LOW", "8705af p.15 Figure 2 (SS pulled low)")
    csd_abs = float(need(p2, r"VCSP-VCSN, VCSPIN-VCSNIN, VCSPOUT-VCSNOUT\.+ .0\.3V to ([\d.]+)V", "8705af p.2 CSPIN-CSNIN absolute maximum").group(1))
    vin_abs = float(need(p2, r"VIN, EXTVCC Voltage\.+ .0\.3V to (\d+)V", "8705af p.2 VIN absolute maximum").group(1))
    fb_abs = float(need(p2, r"FBIN, SHDN Voltage\.+ .0\.3V to (\d+)V", "8705af p.2 FBIN and SHDN absolute maximum").group(1))
    r14_ = float(re.match(r"([\d.]+)k", e["components"]["R14"]["value"]).group(1)) * 1e3
    r15_ = float(re.match(r"([\d.]+)k", e["components"]["R15"]["value"]).group(1)) * 1e3
    # ---- the clamp D4 and the bulk the entry needs (the derived disturbance, below)
    l1, l2 = flat(pg(SMC, 1, False)), flat(pg(SMC, 2))
    need(l1, r"1500W peak pulse power capability at 10/1000[\u00b5\u03bc]s waveform", "SMCJ p.1 the 10/1000 us rating")
    d4row = need(l2, r"SMCJ28A SMCJ28CA GFG BFG (\d+\.\d) (\d+\.\d+) (\d+\.\d+) 1 (\d+\.\d) (\d+\.\d) (\d+) X", "SMCJ p.2 the SMCJ28A row").groups()
    d4 = dict(vr=float(d4row[0]), vbr=(float(d4row[1]), float(d4row[2])), vc=float(d4row[3]), ipp=float(d4row[4]), ir=float(d4row[5]) * 1e-6)
    z1, z2 = flat(pg(ZA, 1)), flat(pg(ZA, 2))
    zrow = need(z2, r"50 33 6\.3 7\.7 D8 (\d+) (\d+) [\d.]+ EEHZA1H330XP", "ZA p.2 the EEHZA1H330XP row").groups()
    za = dict(v=50.0, c=33e-6, ripple=float(zrow[0]) * 1e-3, esr=float(zrow[1]) * 1e-3)
    za["tol"] = float(need(z1, r"Capacitance tolerance \u00b1(\d+) % \(120 Hz/\+20 .C\)", "ZA p.1 capacitance tolerance").group(1)) / 100.0
    za["end_dc"] = float(need(z1, r"Capacitance change Within \u00b1(\d+)% of the initial value tan d < 200 % of the initial limit E\. S\. R\. < 200 % of the initial limit Endurance", "ZA p.1 endurance capacitance").group(1)) / 100.0
    za["esr_cold"] = float(need(z1, r"\(.40 .C\) 2\.0 1\.4 ([\d.]+) 0\.4 0\.3", "ZA p.1 ESR after endurance at -40 C (D8)").group(1))
    lm6 = flat(pg(LM69, 6))
    need(flat(pg(LM69, 5)), r"VIN = 48 V \(unless otherwise noted\)", "LM5069 p.5 the header")
    vcl69 = need(lm6, r"VCL Threshold voltage VIN-SENSE voltage ([\d.]+) (\d+) ([\d.]+) mV", "LM5069 p.6 VCL").groups()
    # ---- the parts' catalogue readings (filed under inputs/)
    lc_ina, lc_tps, lc169, lc38, lcza, lc104 = (catalogue(c_) for c_ in ("C2859736", "C132788", "C44322", "C43698", "C178637", "C14663"))
    if (lc_ina["model"], lc_tps["model"], lc169["model"], lc38["model"], lcza["model"]) != ("INA250A2PWR", "TPS3701DDCR", "INA169NA/3K", "TPS3808G33DBVR", "EEHZA1H330XP") \
            or lcza["params"].get("Voltage Rating") != "50V" or lc104["params"].get("Voltage Rating") != "50V":
        refuse(3, "the arrangement's catalogue readings are not the parts named")
    amps_pk = float(need(gse, r'_intent\.rail\(_pvn, 17\.6, 5\.68, ([\d.]+), "J_SOLAR" if _pvn == "PV_IN" else "F2"', "gen_sch_e.py the panel entry's amps_peak").group(1))
    dt_end = max(abs(t_cold - 25.0), abs(t_air - 25.0))

    # ---- shared models: the regulation's highest current under the joint assumptions at any RIMON_IN (each resistor at its own
    # worst end, the mixed envelope), the bright day (SESSION: the check's definition), and the energy of a setting on both days
    def inom_of(rmv):
        return vref_n / (a7["(All Grades)"]["typ"] * 1e-3 * rs * rmv)

    def reg_hi(rmv, v):
        rs_lo = min(rfac_end(tol_h, TCR_COLD_CONS, tcr_h, t_, life_h, sold_h) for t_ in (END[0][1], END[1][1]))
        rm_lo = min(rfac_end(tol_y, tcr_y, tcr_y, t_, R["life_y"][0] + R["life_y"][1] / rmv, R["sold_y"][0] + R["sold_y"][1] / rmv)
                    for t_ in (END[0][2], END[1][2]))
        return inom_of(rmv) * corner_k(v, ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, rs_lo, rm_lo)
    BRIGHT = [1000.0 * math.sin(math.pi * (h - 6) / 12.0) if 6 < h < 18 else 0.0 for h in range(24)]
    ta12 = round(LR["TA40"][12], 1)                         # 18.1 C, as the check states it

    def bright(vh, lim):
        """SESSION, the check's bright day (astra-check-l4e7r-1, D3): a twelve-hour sine to 1000 W/m2 at noon, the air constant at
        18.1 C (SC-37's hour-12 value to 0.1 C), NOCT 47 C, the replay's panel, lead and op_point, by the trace's a1solar convention."""
        out, nl_ = [], 0
        for h in range(24):
            g = BRIGHT[h]
            if g <= 0.0:
                out.append(0.0)
                continue
            tc = AC.t_cell(ta12, g, LR["noct"])
            pw, _v, _i, limited = LR["op_point"](dsp, g, tc, vh, lim, LR["rl"])
            out.append(RP.BUD.panel_w(g, 100.0, LR["pr0"]) * (pw / AC.arr_mpp(dsp, 1, 1, g, tc)[0]))
            nl_ += limited
        return out, nl_

    def day(inom_, rmv):
        out = []
        for lab, vh in (("lower", lo_h), ("nominal", nom_h), ("upper", hi_h)):
            tr, nl_ = energy(vh, lim_of(inom_, rmv, "lo"))
            out.append((lab, vh, sum(tr), nl_))
        btr, bnl = bright(nom_h, lim_of(inom_, rmv, "lo"))
        out.append(("bright", nom_h, sum(btr), bnl))
        return out
    gnoon = 1000.0
    tcn = AC.t_cell(ta12, gnoon, LR["noct"])

    def noon_power(inom_, rmv):
        """The stage's input at bright noon at the nominal hold, the regulation at its lowest (as the check reads it)."""
        return LR["op_point"](dsp, gnoon, tcn, nom_h, lim_of(inom_, rmv, "lo"), LR["rl"])[0]
    p_noon_now = noon_power(i_nom, rm)
    e_now = day(i_nom, rm)
    e_free = (sum(bright(nom_h, None)[0]))
    # ---- approach C: a sense bank of identical WSL2512 parts in parallel ahead of everything but R8, R9, TP5 and U18's VIN+ pin;
    # U18 an INA169 (current output into R65 + R66 = its 25 kOhm test load), U19's INB on R66; U19's INA watches TRK_VS; U19's
    # outputs drive U20's MR; U20 a TPS3808G33 on TRK_LDO33 (its own supply is what it watches), CT to VDD through R69 (the fixed
    # delay); U20's RESET drives SWEN through R70 over R71. Every term of the trip is a printed limit at the operating condition
    wsl_rows = json.load(open(os.path.join(TOP, INP, "jlc-search-wsl2512-2026-10-01.json"), encoding="utf-8"))["rows"]
    W_AVG = 0.1                # SESSION: the averaging basis of REQ-016's "at most 100 W into the stage" (the argument is printed)
    R66, R65 = rvalue("RT0603BRD078K06L"), rvalue("RT0603BRD0716K9L")  # SESSION: R65 + R66 = 24.96 kOhm, the INA169's 25 kOhm test load; R66 puts the trip at 49.6 mV nominal
    for code, val in (("C861587", R66), ("C861156", R65)):
        verify_rt(code, val)

    def rdrift(rp, sgn, aged):
        """A WSL part's factor at the end that moves the trip (sgn -1 lowers R): tolerance, TCR over the larger excursion, and, aged,
        the printed solder-heat and load-life test limits (each (x % + 0.5 mOhm)), Document 30100 pp.2, 3."""
        f = (1 + sgn * 0.01) * (1 + sgn * wtcr * dt_end)
        if aged:
            f *= (1 + sgn * (float(wsold[0]) / 100.0 + float(wsold[1]) / rp)) * (1 + sgn * (float(wlife[0]) / 100.0 + float(wlife[1]) / rp))
        return f

    def r66f(sgn, aged):
        f = (1 + sgn * tol_y) * (1 + sgn * tcr_y * dt_end)
        if aged:
            f *= (1 + sgn * (R["life_y"][0] + R["life_y"][1] / R66)) * (1 + sgn * (R["sold_y"][0] + R["sold_y"][1] / R66))
        return f

    def vs_trip(v, sgn, aged):
        """The sense voltage at which U19 trips, at input voltage v: sgn +1 the highest, -1 the lowest. The CMR and PSR rows are
        printed at VSENSE = 50 mV, so they bound the whole output there, offset and gain together; carried at the larger of the
        offset reading and the gain reading (scaled by VSENSE / 50 mV), every other term a printed limit."""
        vit_ = vth[1] if sgn > 0 else vth[0]
        gm_ = (gm169[0] if sgn > 0 else gm169[1]) * (1 - sgn * nl169)
        base = (vit_ + sgn * iin_t * R66 * r66f(-sgn, aged)) / (gm_ * R66 * r66f(-sgn, aged))
        drift = 10 ** (-cmr169 / 20.0) * abs(v - 12.0) + psr169 * abs(v - 5.0)
        return base + sgn * (vos169 + drift * max(1.0, base / 0.050))

    def i_trip_c(v, rp, n, sgn, aged):
        return vs_trip(v, sgn, aged) / (rp / n * rdrift(rp, -sgn, aged))
    r89_min = (R["r8v"] + R["r9v"]) * (1 - tol_y) * (1 - tcr_y * dt_end) * (1 - R["life_y"][0] - R["life_y"][1] / R["r8v"]) * (1 - R["sold_y"][0] - R["sold_y"][1] / R["r8v"])

    def pb_c(v):
        """What enters the stage without crossing the bank: R8 and R9 (the hold draft's RT parts at their lowest) and U18's VIN+ pin,
        whose current (its output current and its input bias, which has no printed maximum) is carried at the pin's absolute maximum."""
        return v * v / r89_min + v * ipin169

    def p_c(rp, n):
        return max(v * i_trip_c(v, rp, n, 1, True) + pb_c(v) for v in grid)
    # the entry's capacitance at its largest (the cap-charge energy of an event): three ZA 33 uF +20 % and C13 to C15, C64 (+10 %)
    c_entry_max = 3 * za["c"] * (1 + za["tol"]) + (10e-6 + 10e-6 + 4.7e-6 + 0.1e-6) * 1.10
    e_cap = 0.5 * c_entry_max * v_oc ** 2
    banks = []
    for r_ in wsl_rows:
        m_ = re.match(r"WSL2512R(\d{4})FEA$", r_["model"])
        if not m_ or r_["stock"] < STOCK_MIN:
            continue
        rp = float("0." + m_.group(1))                    # "R0700" is 0.0700 Ohm
        for n in range(1, 7):
            if p_c(rp, n) + e_cap / W_AVG <= p_win:
                banks.append((min(i_trip_c(v, rp, n, -1, True) for v in grid), -n, rp, r_["code"], r_["model"], r_["stock"]))
    if not banks:
        refuse(4, "BLOCKER: no stocked WSL2512 bank puts approach C's static bound and an event under 100 W")
    bank = max(banks)
    i_lo_aged_c, nb, rpb, bcode, bmodel = bank[0], -bank[1], bank[2], bank[3], bank[4]
    lcb = catalogue(bcode)
    if lcb["model"] != bmodel or lcb["params"].get("Tolerance") != "\u00b11%":
        refuse(3, "the bank part's filed reading is not the chosen part")
    rbank = rpb / nb
    c = dict(rp=rpb, n=nb, rbank=rbank, code=bcode, model=bmodel, stock=lcb["stock"])
    c["p_static"] = p_c(rpb, nb)
    c["v_hi"] = max(grid, key=lambda v: v * i_trip_c(v, rpb, nb, 1, True) + pb_c(v))
    c["i_hi25"] = i_trip_c(v_oc, rpb, nb, 1, True)
    c["i_lo_new"] = min(i_trip_c(v, rpb, nb, -1, False) for v in grid)
    c["i_lo_aged"] = i_lo_aged_c
    c["vs_hi"], c["vs_lo"] = vs_trip(v_oc, 1, True), vs_trip(v_oc, -1, True)
    c["pb25"] = pb_c(v_oc)
    # U18's output compliance where the chain is armed (TRK_VS at U19's INA release at its lowest): V+ - 1.2 V and VCM - 1 V (p.6)
    c["vout_hi"] = c["vs_hi"] * gm169[1] * (1 + nl169) * (R65 + R66) * (1 + tol_y) * (1 + tcr_y * dt_end)
    c["e_cap"], c["c_entry_max"] = e_cap, c_entry_max
    # the response (typical rows only): U18 to 0.1 % in about 5 us at 20 kOhm, U19's INB rising edge 28.1 us, U20's MR to RESET,
    # and one switching period of the LT8705A after SWEN falls (INFERRED); a bench row reads it. What the margin leaves for it:
    t_resp_typ = 1.0 / bw169 + tpd_lh + mr_ns + 1.0 / 180e3
    p_ev = v_oc * amps_pk                                  # the most power the panel delivers while the chain responds (REQ-016's 6.25 A)
    c["t_resp_typ"], c["p_ev"] = t_resp_typ, p_ev
    c["t_resp_max"] = ((p_win - c["p_static"]) * W_AVG - e_cap) / p_ev
    c["p_dyn_typ"] = c["p_static"] + (e_cap + p_ev * t_resp_typ) / W_AVG
    # the terms of C's bound, each with its class and its source (no common multiplier)
    c["terms"] = [
        ("U19 TPS3701 INB rising threshold, TJ -40 to 125 C, VDD 1.8 to 36 V", "397 to 403 mV", "warranted", "TPS3701 SBVS240C p.5"),
        ("U19 input current at INB", "+-%.0f nA, through R66" % (iin_t * 1e9), "warranted", "p.5"),
        ("U18 INA169 transconductance, VSENSE 10 to 150 mV, TA -40 to 85 C", "%.0f to %.0f uA/V" % (gm169[0] * 1e6, gm169[1] * 1e6), "warranted", "INA169 SBOS181F p.6"),
        ("its nonlinearity", "+-%.1f %%" % (100 * nl169), "warranted", "p.6"),
        ("its offset, referred to the input", "+-%.0f mV" % (vos169 * 1e3), "warranted", "p.6"),
        ("its common-mode rejection from VIN+ = 12 V to 25 V, at VSENSE = 50 mV", "%.0f dB minimum: %.0f uV" % (cmr169, 1e6 * 10 ** (-cmr169 / 20.0) * 13.0), "warranted", "p.6, VIN+ 2.7 to 60 V"),
        ("its supply rejection from V+ = 5 V to 25 V, at VSENSE = 50 mV", "%.0f uV/V: %.0f uV" % (psr169 * 1e6, psr169 * 20.0 * 1e6), "warranted", "p.6, V+ 2.7 to 60 V"),
        ("the two rejections above carried at the larger of their offset reading and their gain reading", "x %.4f" % max(1.0, c["vs_hi"] / 0.050), "warranted (the rows, read both ways)", "p.6"),
        ("R66 8.06k, 0.1 %%, 25 ppm/K over %.0f K, the printed solder-heat and life limits" % dt_end, "+-(0.5 % + 0.05 Ohm) each", "warranted (printed test limits)", "YAGEO RT V.16 pp.2, 7, 8"),
        ("the bank, %d x %s in parallel: 1 %%, %.0f ppm/K from -55 to +155 C" % (nb, bmodel, wtcr * 1e6), "%.4f mOhm" % (rbank * 1e3), "warranted", "Vishay WSL 30100 pp.1, 2"),
        ("the bank's solder-heat and load-life test limits", "+-(%s %% + %s Ohm) and +-(%s %% + %s Ohm) per part" % (wsold[0], wsold[1], wlife[0], wlife[1]), "warranted (printed test limits)", "WSL 30100 p.3"),
        ("R8 and R9 (the hold draft's RT parts) across 25 V, bypassing the bank", "%.2f mW" % (1e3 * v_oc ** 2 / r89_min), "warranted", "YAGEO RT V.16"),
        ("U18's VIN+ pin current (its output current and its input bias, which prints no maximum), bypassing the bank", "at most %.0f mA: %.0f mW" % (ipin169 * 1e3, 1e3 * v_oc * ipin169), "rating (the pin's absolute maximum)", "INA169 p.4"),
        ("the input voltage at most 25 V", "REQ-016", "requirement", "REQ-016"),
    ]
    # ---- approach C's coordination (B4 of the check): the smallest stocked RIMON_IN whose regulation, at its highest under the
    # joint assumptions, stays at or under C's lowest trip with its parts aged, at every input voltage: one basis at both corners
    rm_rows = sorted([(r_[0], r_[1], r_[2]) for r_ in rows_rm] + [(rvalue(r_["model"]), r_["code"], r_["stock"]) for r_ in
                     json.load(open(os.path.join(TOP, INP, "jlc-search-rt0603brd07-30k-2026-10-01.json"), encoding="utf-8"))["rows"]
                     if rvalue(r_["model"])], key=lambda t: t[0])

    def coordinate(trip_lo):
        for rv_, c_, s_ in rm_rows:
            if s_ >= STOCK_MIN and all(reg_hi(rv_, v) <= trip_lo(v) for v in grid):
                return rv_, c_, s_
        refuse(4, "no stocked RIMON_IN coordinates under the trip")
    rc_ = coordinate(lambda v: i_trip_c(v, rpb, nb, -1, True))
    verify_rt(rc_[1], rc_[0])
    c["rm"], c["inom"] = rc_, inom_of(rc_[0])
    c["reg_hi25"] = reg_hi(rc_[0], v_oc)
    c["energy"] = day(c["inom"], rc_[0])
    c["noon_red"] = 1.0 - noon_power(c["inom"], rc_[0]) / p_noon_now
    c["cur_red"] = 1.0 - c["inom"] / i_nom
    # where an overlap could cost energy if the regulation's unprinted values were worse than the joint assumptions: the bright
    # day's hours whose panel current at the nominal hold exceeds C's lowest aged trip (a restart model, below, bounds them)
    # the check's bright-day figures, reproduced by this model (astra-check-l4e7r-1, D3: 26.1k 495.3165 Wh, 28.7k 465.6367 Wh)
    c["check_repro"] = [(rv_, sum(bright(nom_h, lim_of(inom_of(rv_), rv_, "lo"))[0]), 1.0 - noon_power(inom_of(rv_), rv_) / p_noon_now) for rv_ in (26100.0, 28700.0)]
    c["exposed"] = [(h, BRIGHT[h], bright(nom_h, None)[0][h]) for h in range(24) if BRIGHT[h] > 0.0
                    and dsp.current(nom_h, BRIGHT[h], AC.t_cell(ta12, BRIGHT[h], LR["noct"]), LR["rl"]) > i_trip_c(nom_h, rpb, nb, -1, True)]
    c["pk_day"] = max(dsp.current(vh, LR["prof0"][h], AC.t_cell(LR["TA40"][h], LR["prof0"][h], LR["noct"]), LR["rl"])
                      for vh in (lo_h, nom_h, hi_h) for h in range(24) if LR["prof0"][h] > 0)
    c["trip_lo_hold"] = min(i_trip_c(vh, rpb, nb, -1, True) for vh in (lo_h, nom_h, hi_h))
    # the bank's conduction on both days at the nominal hold (its nominal resistance; the trace's convention, hourly W over the hold)
    c["loss"] = (sum((p_ / nom_h) ** 2 * rbank for p_ in energy(nom_h)[0]), sum((p_ / nom_h) ** 2 * rbank for p_ in bright(nom_h, None)[0]))
    c["p_bank_max"] = (c["i_hi25"] / nb) ** 2 * rpb * (1 + 0.01)          # one part at the highest trip current, W (its P70 is 1 W)
    # ---- approach B, reclassed (the INA250 with the same trip chain and entry): every row at its printed value; the rows printed at
    # another condition, or typical only, are CONDITIONAL and named, with the gain error they may add before the bound reaches 100 W
    r60b, r61b = rvalue("RT0603BRD0728KL"), rvalue("RT0603BRD077K87L")
    for code, val in (("C705756", r60b), ("C861565", r61b)):
        verify_rt(code, val)

    def i_err_b(v):
        return ios + dios * dt_end + abs(v - 12.0) * 10 ** (-cmr / 20.0) / rsh_n + psr * (5.0 - v_ldo[0])

    def trip_b(v, sgn, aged, extra=0.0):
        def kk(s_t, s_b):
            def f(s_, r_):
                d = ((1 + s_ * (R["life_y"][0] + R["life_y"][1] / r_)) * (1 + s_ * (R["sold_y"][0] + R["sold_y"][1] / r_))) if aged else 1.0
                return (1 + s_ * tol_y) * (1 + s_ * tcr_y * dt_end) * d
            return r61b * f(s_b, r61b) / (r60b * f(s_t, r60b) + r61b * f(s_b, r61b))
        rth = r60b * r61b / (r60b + r61b)
        if sgn > 0:
            k_ = min(kk(a, b) for a in (-1, 1) for b in (-1, 1))
            return (vth[1] + iin_t * rth) / (k_ * g_ina * (1 - eg - extra)) + i_err_b(v)
        k_ = max(kk(a, b) for a in (-1, 1) for b in (-1, 1))
        return (vth[0] - iin_t * rth) / (k_ * g_ina * (1 + eg + extra)) - i_err_b(v)

    def pb_b(v):
        return v * v / r89_min + v * ib_ina
    b = dict(p_static=max(v * trip_b(v, 1, True) + pb_b(v) for v in grid))
    lo_, hi_ = 0.0, 0.2
    for _ in range(60):
        mid = 0.5 * (lo_ + hi_)
        if max(v * trip_b(v, 1, True, mid) + pb_b(v) for v in grid) + e_cap / W_AVG > p_win:
            hi_ = mid
        else:
            lo_ = mid
    b["gain_be"] = lo_                                     # the unprinted gain terms together may reach this before 100 W
    b["typ_gain"] = stress_sh + nl + ro / (r60b + r61b)    # what the typical-only rows print, for scale
    rb_ = coordinate(lambda v: trip_b(v, -1, True))
    verify_rt(rb_[1], rb_[0])
    b["rm"], b["inom"] = rb_, inom_of(rb_[0])
    b["energy"] = day(b["inom"], rb_[0])
    b["noon_red"], b["cur_red"] = 1.0 - noon_power(b["inom"], rb_[0]) / p_noon_now, 1.0 - b["inom"] / i_nom
    r_ina = 4.5e-3                                         # p.5, the package path, IN+ to IN-, the shunt included (typical)
    b["loss"] = (sum((p_ / nom_h) ** 2 * r_ina for p_ in energy(nom_h)[0]), sum((p_ / nom_h) ** 2 * r_ina for p_ in bright(nom_h, None)[0]))
    b["abs"] = abs_ina
    b["conditional"] = [
        "the system gain error and the offset at VS = 3.23 to 3.35 V and VREF = 0 V (both printed at VS = 5 V and VREF = 2.5 V, p.5)",
        "the common-mode rejection away from zero current (printed at ISENSE = 0 A, p.5)",
        "the integrated shunt's change after reflow, thermal cycling and life (typical only, %.3f %% summed; note 6 of p.6 excludes them from the gain error)" % (100 * stress_sh),
        "the nonlinearity (typical only, %.2f %%) and the output impedance (typical only, %.1f Ohm)" % (100 * nl, ro),
        "U18's VIN+ bias across temperature (%.0f uA printed at 25 C only)" % (ib_ina * 1e6),
    ]
    # ---- approach A: the present control with argued margins (unchanged method; its fault comparator's action has no printed timing)
    v_f = iovm["max"] * (1 + LINE_FLOOR_MUL * line_p * 1e-2 * (v_oc - V_LINE_REF))
    rs_lo_c = rfac(tol_h, TCR_COLD_CONS, abs(t_cold - 25.0), life_h, sold_h)
    need_rm = v_oc * v_f / (p_win * gm_lo * 1e-3 * rs * rs_lo_c)
    a30 = json.load(open(os.path.join(TOP, INP, "jlc-search-rt0603brd07-30k-2026-10-01.json"), encoding="utf-8"))["rows"]
    rm_a = None
    for rv_, c_, s_ in sorted((rvalue(r_["model"]), r_["code"], r_["stock"]) for r_ in a30 if rvalue(r_["model"]) and r_["stock"] >= STOCK_MIN):
        rm_lo_c = rfac(tol_y, tcr_y, abs(t_cold - 25.0), R["life_y"][0] + R["life_y"][1] / rv_, R["sold_y"][0] + R["sold_y"][1] / rv_)
        if v_oc * v_f / (gm_lo * 1e-3 * rs * rs_lo_c * rv_ * rm_lo_c) <= p_win:
            rm_a = (rv_, c_, s_, v_oc * v_f / (gm_lo * 1e-3 * rs * rs_lo_c * rv_ * rm_lo_c))
            break
    if rm_a is None:
        refuse(4, "no stocked RIMON_IN holds approach (a)'s argued bound")
    a_ = dict(v_f=v_f, need=need_rm, rm=rm_a, inom=vref_n / (1e-3 * rs * rm_a[0]), bound=rm_a[3])
    a_["energy"] = day(a_["inom"], rm_a[0])
    a_["noon_red"], a_["cur_red"] = 1.0 - noon_power(a_["inom"], rm_a[0]) / p_noon_now, 1.0 - a_["inom"] / i_nom
    # ---- approach C's supply sequencing (B3 of the check): the stage is held off whenever the sensing chain is unsupplied
    seq = dict(vit_lo=vit38 * (1 - acc38), vit_hi=vit38 * (1 + acc38), rel_hi=vit38 * (1 + acc38) * (1 + hys38), ldo_lo=v_ldo[0],
               vdd38=vdd38, vdd_t=vdd_t, vpor=vpor38, td_min=td_min, vol38=vol38, rmr=rmr38, ioh=ioh38)
    R70, R71, R67, R68, R69 = (rvalue("RT0603BRD07%sL" % x_) for x_ in ("22K", "33K", "110K", "9K53", "100K"))
    for code, val in (("C469656", R70), ("C705768", R71), ("C326736", R67), ("C705800", R68), ("C122538", R69)):
        verify_rt(code, val)
    k_sw_hi = R71 * (1 + tol_y) * (1 + tcr_y * dt_end) / (R70 * (1 - tol_y) * (1 - tcr_y * dt_end) + R71 * (1 + tol_y) * (1 + tcr_y * dt_end))
    k_sw_lo = R71 * (1 - tol_y) * (1 - tcr_y * dt_end) / (R70 * (1 + tol_y) * (1 + tcr_y * dt_end) + R71 * (1 - tol_y) * (1 - tcr_y * dt_end))
    # TRK_LDO33's load from the arrangement, at most, against the 5 mA its regulation row is printed at (8705af p.3)
    idd_t = float(need(t5, r"IDD Supply current VDD = 1\.8 V . 36 V \d+ (\d+) [\u00b5\u03bc]A", "TPS3701 p.5 IDD").group(1)) * 1e-6
    idd38 = float(need(s6, r"VDD = 3\.3V, RESET not asserted [\d.]+ (\d+) MR, RESET, CT open", "TPS3808 p.6 IDD at 3.3 V").group(1)) * 1e-6
    seq["i_ldo"] = idd_t + idd38 + v_ldo[1] / (R70 + R71) + v_ldo[1] / rmr38 + v_ldo[1] / R69
    seq["ldo_enable_min"] = swen_r["min"] / k_sw_hi     # SWEN cannot reach its least rising threshold below this LDO33 (pin current zero)
    seq["swen_at_ldo_lo"] = k_sw_lo * v_ldo[0]          # SWEN with RESET released at LDO33's least, against its highest threshold
    seq["sw_th"] = R70 * R71 / (R70 + R71)
    seq["pin_needed_13"] = (swen_r["min"] - k_sw_hi * 1.3) / seq["sw_th"]      # the SWEN source current that alone could enable it below 1.3 V
    seq["uv_ts_lo"] = vtha[0] * (1 + R67 * (1 - tol_y) * (1 - tcr_y * dt_end) / (R68 * (1 + tol_y) * (1 + tcr_y * dt_end)))
    seq["uv_ts_hi"] = vtha[1] * (1 + R67 * (1 + tol_y) * (1 + tcr_y * dt_end) / (R68 * (1 - tol_y) * (1 - tcr_y * dt_end)))
    seq["ramp"] = ilim33 / 1e-6                         # V/s into C20's 1 uF (INFERRED: its capacitance at bias has no row)
    seq["ramp_limit"] = 1.0 / 15e-6                     # TPS3808's VPOR row holds for a rise no faster than this
    seq["intvcc_uv"] = uvi
    seq["i_sw_reset"] = v_ldo[1] / (R70 * (1 - tol_y))  # RESET's sink current, against its VOL row at 1 mA
    if not (seq["rel_hi"] < seq["ldo_lo"] and seq["ldo_enable_min"] > max(vdd38, vdd_t) and seq["swen_at_ldo_lo"] > swen_r["max"]
            and seq["i_ldo"] < 5e-3 and c["vout_hi"] < min(seq["uv_ts_lo"] - sw169, seq["uv_ts_lo"] - swcm169)
            and seq["uv_ts_lo"] > 2.7 and seq["i_sw_reset"] <= 1e-3 and td_min > st_t):
        refuse(4, "approach C's supply sequencing does not hold on the printed rows")
    # ---- the solar entry's protection (B6 of the check): the derived disturbance and every part on the entry against it
    def r59_peak(rb_esr, cb, cc, r59):
        """MODELED: the pulse into TRK_VS, shared by the bulk (rb_esr, cb) and, through R59, the ceramics behind it (cc); the clamp
        left out, which only adds current into the bulk side. The 10/1000 us pulse as a double exponential (3.4 us, 1.44 ms; INFERRED
        shape), scaled to D4's 33.1 A; the peak voltage across R59 in the first 200 us."""
        t1, t2 = 3.4e-6, 1.44e-3
        f = lambda t: math.exp(-t / t2) - math.exp(-t / t1)
        amp = d4["ipp"] / max(f(k * 1e-7) for k in range(2000))
        vb = vc_ = 17.6
        pk = 0.0
        dt_s = 1e-8
        for n_ in range(20000):
            i_ = amp * f(n_ * dt_s)
            vn = (i_ + vb / rb_esr + vc_ / r59) / (1.0 / rb_esr + 1.0 / r59)
            ib_, ic_ = (vn - vb) / rb_esr, (vn - vc_) / r59
            vb += ib_ / cb * dt_s
            vc_ += ic_ / cc * dt_s
            pk = max(pk, abs(ic_) * r59)
        return pk
    cer = (10e-6 + 10e-6 + 4.7e-6 + 0.1e-6) * 1.10
    cb_lo = 3 * za["c"] * (1 - za["tol"]) * (1 - za["end_dc"])
    s59 = [(lab, r59_peak(esr, cb_lo, cer, rs * (1 + 0.01))) for lab, esr in (("new, 20 C", za["esr"] / 3.0), ("after endurance, -40 C", za["esr_cold"] / 3.0))]
    surge = dict(vc=d4["vc"], ipp=d4["ipp"], vbr=d4["vbr"], vr=d4["vr"], s59=s59, csd_abs=csd_abs, vin_abs=vin_abs,
                 d169=d4["ipp"] * rbank * rdrift(rpb, 1, True), d169_abs=abs169[1], cm169_abs=abs169[0], vs169_abs=vsabs169,
                 v_pvp=d4["vc"] + d4["ipp"] * rbank * rdrift(rpb, 1, True), b_abs=abs_ina, za_v=za["v"],
                 esd_dv=2.25e-6 / (3 * za["c"] * (1 - za["tol"]) * (1 - za["end_dc"]) + (10e-6 + 10e-6 + 4.7e-6) * 0.9),
                 esd_d169=45.5 * rbank * rdrift(rpb, 1, True), fb_abs=fb_abs,
                 v_r14=d4["vc"] * r14_ / (r14_ + r15_), v_shdn=d4["vc"] * r15_ / (r14_ + r15_),
                 v_fbin=(d4["vc"] + d4["ipp"] * rbank * rdrift(rpb, 1, True)) * R["r9v"] / (R["r8v"] + R["r9v"]))
    if max(x[1] for x in s59) > csd_abs or surge["d169"] > abs169[1] or surge["v_pvp"] > min(abs169[0], vsabs169) or za["v"] < d4["vc"]:
        refuse(4, "a part on the solar entry exceeds its rating at the derived disturbance")
    # ---- the single faults (for layer 8's fault analysis; this record assigns them, it does not close them)
    faults = dict(
        defeat=["U18's output stuck low or open, or R65 open (no current reaches R66)", "R66 shorted", "U19's OUTB stuck open (high impedance)",
                "U20's RESET stuck open, or its MR input stuck high", "a short across the sense bank", "U5's SWEN input failed active"],
        stop=["U19's OUTA or OUTB stuck low", "U20's RESET stuck low", "R70 open (SWEN pulled to ground by R71)", "U18's output stuck high",
              "the whole sense bank open (one part open only raises the bank's resistance: the trip falls, charging continues)",
              "TRK_LDO33 lost (U20 holds the stage off)"],
        acceptance="Layer 8 lists each fault above with its effect; acceptance: no single fault both defeats the backstop and removes "
                   "the LT8705A's own input-current limit (a defeated backstop leaves the regulation, which holds the stage under the "
                   "trip when its unprinted values are inside the joint assumptions), and every fault that defeats the backstop is "
                   "found by the commissioning and periodic trip test (bench row 7b.15) at an interval layer 8 sets")
    # ---- the series disconnect, evaluated and not taken (the check's suggestion; SESSION)
    disc = dict(vcl=(float(vcl69[0]), float(vcl69[1]), float(vcl69[2])), vin_test=48.0,
                why="the LM5069 class hot-swap controller prints its current limit (VCL %s / %s / %s mV) at VIN = 48 V, not at the "
                    "panel's 17 to 25 V, and its spread (%.0f %% from typical to either end) would push the regulation further down than "
                    "C's; SWEN already removes the path from the panel to the pack (the four switches stop and M1's body diode blocks "
                    "the input), and the input capacitors' charge is bounded as an event (below). A series FET would cover a shorted "
                    "switch of the LT8705A, a single fault layer 8 judges" % (vcl69[0], vcl69[1], vcl69[2], 100 * (float(vcl69[2]) / float(vcl69[1]) - 1)))
    # ---- the verdict on the present control (unchanged reading of section 9)
    verdict = dict(shown=False, depends=[(r_["id"], r_["breakeven"]) for r_ in R["qual_rows"] if r_["bound"] and not r_["resolved"]])
    R["decision"] = dict(
        verdict=verdict, chosen="C", w_avg=W_AVG, e_now=e_now, e_free=e_free, p_noon_now=p_noon_now, ta12=ta12,
        approaches=[
            dict(id="A", name="the present control with argued margins (the IMON_IN fault comparator bounds EA2; RIMON_IN raised)",
                 bound=a_["bound"], status="CONDITIONAL", setting=(rm_a[0], rm_a[1], a_["inom"]), energy=a_["energy"], independent=False,
                 noon_red=a_["noon_red"], cur_red=a_["cur_red"], loss=(0.0, 0.0),
                 classes={"warranted": ["IMON_IN fault maximum 1.67 V (8705af p.5, full range)", "RSENSE1 1 % and RIMON_IN 0.1 %", "the resistors' printed drifts"],
                          "assumption": ["A7 at its test-point limits away from its test point", "the fault threshold's VIN dependence (twice the reference's printed line regulation)",
                                         "RSENSE1's cold TCR at 100 ppm/K", "the fault comparator's response and restart, which print no timing"]},
                 parts="none added; R16 to %gk (%s)" % (rm_a[0] / 1e3, rm_a[1]),
                 failure="a regulation point past the fault minimum turns limiting into the fault's hiccup (switching stops: energy, not the bound)",
                 depends="Analog Devices (A7 away from its test point, the fault threshold away from VIN = 12 V, the fault's timing) and Milliohm (the cold TCR)",
                 surge="no part added; the entry's capacitors need the same correction as C"),
            dict(id="B", name="the INA250A2 (its own 2 mOhm shunt) with the same trip chain as C (TPS3701 into a TPS3808 on SWEN)",
                 bound=b["p_static"], status="CONDITIONAL", setting=(b["rm"][0], b["rm"][1], b["inom"]), energy=b["energy"], independent=False,
                 noon_red=b["noon_red"], cur_red=b["cur_red"], loss=b["loss"],
                 classes={"warranted": ["the TPS3701 and TPS3808 rows", "the divider's RT rows", "the offset's supply and common-mode rows (at ISENSE = 0 A)"],
                          "conditional": b["conditional"]},
                 parts="U18 INA250A2PWR, the trip chain of C, R60 28k and R61 7.87k; R16 to %gk" % (b["rm"][0] / 1e3),
                 failure="as C; and its integrated shunt carries the surge with the amplifier",
                 depends="Texas Instruments (the rows at VS = 3.3 V and VREF = 0 V, the stress rows); the coordination with Analog Devices and Milliohm",
                 surge="FAILS: U18's inputs are rated %.0f V and the derived disturbance clamps at up to %.1f V" % (abs_ina, d4["vc"])),
            dict(id="C", name="a WSL2512 sense bank read by an INA169 into a TPS3701, a TPS3808 supervisor holding SWEN low",
                 bound=c["p_static"], status="UNCONDITIONAL", setting=(rc_[0], rc_[1], c["inom"]), energy=c["energy"], independent=True,
                 noon_red=c["noon_red"], cur_red=c["cur_red"], loss=c["loss"],
                 classes={"warranted": [t_[0] for t_ in c["terms"] if t_[2].startswith("warranted")],
                          "rating": [t_[0] for t_ in c["terms"] if t_[2].startswith("rating")], "requirement": ["the input voltage at most 25 V (REQ-016)"]},
                 parts="U18 INA169NA/3K, U19 TPS3701DDCR, U20 TPS3808G33DBVR, R60 to R64 (%d x %s), R65 16.9k, R66 8.06k, R67 110k, R68 9.53k, "
                       "R69 100k, R70 22k, R71 33k, C66 to C68 100n; C11, C12 and C69 the 50 V bulk; R16 to %gk" % (nb, bmodel, rc_[0] / 1e3),
                 failure="a hiccup if the regulation's unprinted values exceed the joint assumptions (energy, not the bound); the single faults of the fault list",
                 depends="no Analog Devices, Milliohm or Texas Instruments answer for the bound; the coordination and the energy stay with Analog Devices' and Milliohm's answers",
                 surge="passes: every part with a maker row on the entry rated above %.1f V (C13 to C15 and R14 by the generator's value text; their "
                       "maker parts are the regeneration's), U18's differential under %.0f V, U5's sense differential under %.1f V (MODELED)" % (d4["vc"], abs169[1], csd_abs)),
        ],
        c=c, b=b, a=a_, seq=seq, surge=surge, faults=faults, disc=disc,
        rows=dict(st_t=st_t, vth=vth, vtha=vtha, iin_t=iin_t, vol_max=vol_max, tpd_lh=tpd_lh, uvlo_t=uvlo_t, vdd_t=vdd_t, vit38=vit38, acc38=acc38,
                  hys38=hys38, td38=td38, mr_ns=mr_ns, gm169=gm169, vos169=vos169, cmr169=cmr169, psr169=psr169, nl169=nl169,
                  iq169=iq169, sw169=sw169, swcm169=swcm169, ipin169=ipin169, bw169=bw169, v_ldo=v_ldo, ilim33=ilim33,
                  swen=(swen_r["min"], swen_r["max"]), d4=d4, za=za, wtcr=wtcr, wsold=wsold, wlife=wlife, amps_pk=amps_pk,
                  r65=R65, r66=R66, r67=R67, r68=R68, r69=R69, r70=R70, r71=R71, stock169=lc169["stock"], stock38=lc38["stock"],
                  stock_tps=lc_tps["stock"], stockza=lcza["stock"]))
    # the clarification drafts after the decision: no answer moves C's bound; Analog Devices' and Milliohm's answers set the coordination
    # and the energy; the Texas Instruments draft now asks about the INA169's VIN+ pin current only (supporting, not needed)
    ti_p, ad_p = os.path.join(TOP, CLAR, "texas-instruments-ina169.txt"), os.path.join(TOP, CLAR, "analog-devices-lt8705a.txt")
    if not os.path.isfile(ti_p) or os.path.isfile(os.path.join(TOP, CLAR, "texas-instruments-ina250.txt")):
        refuse(3, "the clarification drafts do not follow the decision (the INA169 draft, no INA250 draft)")
    ti_t, ad_t = open(ti_p, encoding="utf-8").read(), " ".join(open(ad_p, encoding="utf-8").read().split())
    if not ti_t.startswith("DRAFT FOR THE OWNER TO SEND.") or "INA169" not in ti_t:
        refuse(3, "the clarification text texas-instruments-ina169.txt does not read as a draft naming its part")
    if "SWEN" not in ad_t or "input current" not in ad_t:
        refuse(3, "the Analog Devices draft does not carry the SWEN question")
    R["decision"]["clar"] = ["analog-devices-lt8705a.txt", "milliohm-hojlr2512.txt", "texas-instruments-ina169.txt"]
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
        if nm == "apply_gen_sch_e_input_limit.py":
            after_il = new
    # the backstop's draft edits the hold and input limit drafts' text: read back on top of both, its codes the decision's
    nm = "apply_gen_sch_e_backstop.py"
    m = load(nm[:-3] + "_for_l4e7", "v2/docs/records/l4e7/" + nm)
    base_ = load("hold_for_backstop", "v2/docs/records/l4e7/apply_gen_sch_e_hold.py").patched(after_il)
    new = m.patched(base_)
    cd_ = R["decision"]["c"]
    want = ["C44322", "C132788", "C43698", cd_["code"], "C178637", cd_["rm"][1], "C861587", "C861156"]
    R["drafts"][nm] = (len(m.EDITS), "R10" in "".join(o_ for o_, _r in m.EDITS), new.count('r("R10", "115k 1% (RFBOUT1: 15.1 V)"') == 1,
                       all(new.count('"%s")' % c_) > base_.count('"%s")' % c_) for c_ in want), want)
    R["backstop_draft"] = dict(swen='"36": "TRK_SWEN"' in new, cspin='"33": "TRK_VS"' in new, r59='"TRK_VS", "TRK_VIN", "RS2512"' in new,
                               bank=('for _bk in range(%d): r("R6%%d" %% _bk, ' % cd_["n"]) in new and new.count('"PV_P", "TRK_VS", "RS2512", "%s")' % cd_["code"]) == 1,
                               r16=('r("R16", "%gk 0.1%%' % (cd_["rm"][0] / 1e3)) in new, d4='"1": "TRK_VS", "2": "GND"}, "C224047")' in new,
                               bulk=new.count('"C178637")') == 2 and 'part("C69", ' in new, r14='r("R14", "100k 1%", "TRK_VS", "TRK_SHDN")' in new)
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
    P("     %.1f mA: %.1f mA, %.2f W, TJ estimated about %.1f C (INFERRED) in %.1f C air with theta-JA %.0f C/W (%.1f C at the drawn output's %.2f V), under" % (
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
    P("   7b.9t (transients, recorded apart): a source step (open circuit to the limit) and irradiance steps to the two panel")
    P("     scenarios of section 9 (%.1f W, a warmed %.1f C cell; %.1f W, a cold-soaked -20 C cell; both at 1000 W/m2); the peak and" % (
        R["outside"]["p_panel_cold"], R["outside"]["t_cell_cold"], R["outside"]["p_panel_soak"]))
    P("     the time above 100 W against the filter's %.2f ms (SESSION: no fault trip, IMON_IN under %.2f V; above 100 W no longer" % (
        R["tau"] * 1e3, R["iovm"]["min"]))
    P("     than five time constants, %.1f ms)" % (5 * R["tau"] * 1e3))
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
    P("   THE CLASSIFICATION (Y: the value can move that outcome; small: it moves it by the stated fraction, nonzero; the reasons below):")
    P("     %-4s %-74s %-6s %-9s %-10s %s" % ("id", "unprinted value", "bound", "stability", "protection", "other"))

    def eff(r_, k):
        return ("small" if k in r_["small"] else "Y") if r_[k] else "N"
    for r_ in R["qual_rows"]:
        P("     %-4s %-74s %-6s %-9s %-10s %s" % (r_["id"], r_["name"][:74], "Y" if r_["bound"] else "N", eff(r_, "stability"),
                                                eff(r_, "protection"), r_["other"]))
    for r_ in R["qual_rows"]:
        P("   %s, %s" % (r_["id"], r_["name"]))
        for lab, key in (("the bound", "why_bound"), ("loop stability", "why_stability"), ("protection", "why_protection"),
                         ("the sheet", "sheet"), ("guaranteed limit", "guaranteed"), ("conservative assumption", "conservative"),
                         ("qualification needed", "qualification")):
            text = r_[key] if r_[key] is not None else "none printed"
            for k, ln in enumerate(textwrap.wrap("%s: %s" % (lab, text), 118)):
                P("     " + ("- " if k == 0 else "  ") + ln)
        for outcome in ("stability", "protection"):
            if outcome in r_["small"]:
                wrapP("     - ", "       ", "small effect on %s: %s" % ("loop stability" if outcome == "stability" else outcome, r_["small"][outcome]))
        if r_["bound"]:
            mtxt = ("%.4f W under its conservative assumption alone (stack A otherwise, cold end)" % r_["margin_w"]) if r_["margin_w"] is not None \
                else "%.1f K of junction" % r_["margin_k"]
            wrapP("     - ", "       ", "margin kept: %s; break-even %s" % (mtxt, r_["breakeven"]))
    cs = R["cons"]
    unres = [r_["id"] for r_ in R["qual_rows"] if r_["bound"] and not r_["resolved"]]
    a7 = R["a7q"]
    wrapP("   ", "   ", "THE RESULT: %s on %s. %.4f W (cold) and %.4f W (hot), %.4f W with each resistor at its own worst end (the mixed "
          "envelope), are calculated results under the assumptions listed below. "
          "Under each unresolved row's conservative assumption alone the cold corner reads %.4f / %.4f / %.4f W (EA2 / LINE / TCR); "
          "A7 at its test-point limits is stack A itself, and TJ moves no figure while the junction stays inside -40 to 125 C. All of "
          "them together with the resistors' drifts read %.4f W (stack C with RSENSE1's cold TCR at %.0f ppm/K): margin %.4f W, which "
          "A7 consumes at an effective gain %.4f %% under its printed minimum (%.6f mmho). The design floor stack C itself reads "
          "%.4f / %.4f W (cold / hot)" % (R["bound_status"], ", ".join(unres), R["main_chk"][0][1][0], R["main_chk"][1][1][0],
                                          R["thermal"]["mixed"]["a"], cs["ea2"],
                                          cs["line"], cs["tcr"], cs["joint"], cs["tcr_cons"] * 1e6, 100.0 - cs["joint"], a7["loss"]["joint"],
                                          a7["be"]["joint"], R["chk_floor"][0][1][0], R["chk_floor"][1][1][0]))
    P("   THE ASSUMPTIONS OF 96.25 W (stack A), in one list:")
    for k, a in enumerate((
            "8705af's full-range rows for the I grade: the IMON_IN regulation 1.187 / 1.229 V and A7's gm 0.94 / 1.06 mmho, with U5's junction inside -40 to 125 C (an INFERRED estimate of about %.1f C, not a demonstrated bound)" % R["tj_hot"],
            "A7's gm limits, printed at VCSPIN - VCSNIN = 50 mV and VCSPIN = 5.025 V, applied at the design's common mode %.3f to %.0f V and up to %.1f mV differential while switching (ASSUMPTION, condition A7)" % (
                R["a7q"]["cm"][0], R["a7q"]["cm"][1], 1e3 * R["a7q"]["vd"]),
            "the IMON_IN line regulation at its printed maximum (0.005 %/V, 25 C, not switching), applied while switching and at both ends (ASSUMPTION)",
            "EA2's gain at its typical 130 V/V as its bound, with VC anywhere in its absolute maximum range -0.3 to 2.2 V (ASSUMPTION)",
            "RSENSE1 15 mOhm +-1 %% and +-50 ppm/K, the TCR printed for +25 to +125 C applied at -20 C (ASSUMPTION); its hot end %.1f C by the derating line (INFERRED)" % END[1][1],
            "RIMON_IN 23.2k +-0.1 %, +-25 ppm/K (tested from -55 to +125 C); the resistors' soldering and life drifts not stacked (they are in C and D)",
            "both resistors in the same inside air at each end (the thermal coupling of the paired ends); the mixed envelope below drops it",
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
    P("       current, p.18); the hold's lowest is the floor (there, with matching stacks and each resistor at its worst end: %.4f W" % R["p_hold_lo"]["a"])
    P("       A, %.4f W C with the drifts, %.4f W with every conservative assumption). The dense check (0.01 V) of each stack finds" % (
        R["p_hold_lo"]["c"], R["p_hold_lo"]["joint"]))
    P("       its worst at the 25 V vertex")
    P("     - every tolerance direction: P is monotonic in each term (up in Vref, in the line term for v above 12 V, in the EA2 term;")
    P("       down in gm, RSENSE1 and RIMON_IN), so the 64 vertices an end hold the extremes; a resistor's low end 1 - a|T - 25| is")
    P("       least at the end of its temperature span farthest from 25 C, so the two ends are enough")
    P("     - temperature: the air from %.0f C (no self-heating; self-heating only moves a part toward 25 C there) to %.1f C plus" % (R["t_cold"], R["t_air"]))
    P("       RSENSE1's own rise (%.1f C); the LT8705A rows are full range, so U5's junction enters only as the condition -40 to" % END[1][1])
    tb = ["%.1f C" % t_ if t_ is not None else "past its 170 C rating" for t_ in R["rs_t_be"]]
    P("       125 C. RSENSE1 would have to reach %s (stack A) or %s (stack C) for the corner to reach 100 W:" % tuple(tb))
    P("       a board hot spot beside L1 and the FETs is covered by that much")
    th = R["thermal"]
    wrapP("     - ", "       ", "the thermal coupling: the paired ends assume both resistors sit in the same inside air at each end "
          "(RSENSE1 adds its own rise). The mixed envelope drops that and lets each take its own worst end: %.9f W (A), %.9f W (C), "
          "%.9f W (every conservative assumption), against %.9f / %.9f / %.9f W paired; a dense air sweep from %.0f to %.1f C in "
          "0.1 C steps, RSENSE1 with and without its rise, finds %.9f / %.9f / %.9f W. The mixed envelope is the bound's figure" % (
              th["mixed"]["a"], th["mixed"]["c"], th["mixed"]["joint"], th["paired"]["a"], th["paired"]["c"], th["paired"]["joint"],
              R["t_cold"], R["t_air"], th["sweep"]["a"], th["sweep"]["c"], th["sweep"]["joint"]), 116)
    P("   STATES OUTSIDE THE CORNERS")
    o_ = R["outside"]
    P("     - below -20 C ambient: outside REQ-024's -20 to +40 C. Computed for information at -40 C (the I grade's least junction):")
    P("       the candidate's open circuit reaches %.2f V there, outside REQ-016's window; the corner at that voltage with both" % o_["voc40"])
    P("       resistors at -40 C reads %.4f W under stack A" % o_["p40"])
    P("     - a source step (a panel plugged in live): TRK_VIN's %.1f uF (NETLIST: C11, C12, C13, C14, C15, C64) charge through R59 at" % (o_["c_vin"] * 1e6))
    P("       most the panel's short circuit, %.1f mJ at 25 V; start-up ramps VC by the soft start (p.15). Bench 7b.9t" % (o_["e_caps"] * 1e3))
    P("     - an irradiance step, two scenarios of the candidate panel (%.0f W +%.0f %%, %.2f %%/K, 1000 W/m2; INFERRED from its sheet):" % (
        100.0, 100 * o_["tol_p"], 100 * o_["gamma"]))
    P("       %.1f W with a cell warmed to %.1f C by the NOCT model in -20 C air, and %.1f W with a cold-soaked -20 C cell; either" % (
        o_["p_panel_cold"], o_["t_cell_cold"], o_["p_panel_soak"]))
    P("       exceeds 100 W until the IMON_IN loop settles through CIMON_IN (tau %.2f ms). Bench 7b.9t, both scenarios" % (R["tau"] * 1e3))
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
    P("")
    P("10. THE CONTROL DECISION (L4-E7R, the owner's instruction of 1 October 2026; second round after checks/astra-check-l4e7r-1.md;")
    P("    SESSION decision)")
    d = R["decision"]
    c, b, a_, sq, sg, rw = d["c"], d["b"], d["a"], d["seq"], d["surge"], d["rows"]
    wrapP("   ", "     ", "THE VERDICT ON THE CURRENT CONTROL: NOT SHOWN on warranted manufacturer limits alone. The LT8705A's input-current limit "
          "as set (RIMON_IN %gk, RSENSE1 %.0f mOhm) holds 100 W only under values no maker warrants: %s. Under all their conservative "
          "assumptions together the corner reads %.4f W (margin %.4f W)" % (
              R["rm"] / 1e3, R["rs"] * 1e3, "; ".join("%s (break-even %s)" % (i_, b_) for i_, b_ in d["verdict"]["depends"]),
              R["cons"]["joint"], 100.0 - R["cons"]["joint"]))
    P("   THE COMPARISON (three approaches; each bound is the static input power at most, at 25 V; the energy is the stage's input on SC-37's")
    P("   day at the kept hold's corners and on the bright day at its nominal, the regulation at its lowest; hours bound in brackets):")
    P("     %-2s %-9s %-13s %-24s %-34s %-17s %-11s %s" % ("id", "bound W", "status", "regulating setting", "Wh SC-37 lower / nominal / upper",
                                                         "Wh bright", "noon I / P", "independent"))
    for x in d["approaches"]:
        e_ = x["energy"]
        P("     %-2s %-9.4f %-13s %-24s %-34s %-17s %-11s %s" % (
            x["id"], x["bound"], x["status"], "%gk %s %.4f A" % (x["setting"][0] / 1e3, x["setting"][1], x["setting"][2]),
            " / ".join("%.1f (%d)" % (y[2], y[3]) for y in e_[:3]), "%.1f (%d)" % (e_[3][2], e_[3][3]),
            "-%.1f / -%.1f %%" % (100 * x["cur_red"], 100 * x["noon_red"]), "yes" if x["independent"] else "no"))
    en = d["e_now"]
    P("     now 23.2k: SC-37 %s; bright %.1f (%d) Wh (the bright day unlimited: %.1f Wh); noon input %.2f W (bright noon, %.1f C air)" % (
        " / ".join("%.1f (%d)" % (y[2], y[3]) for y in en[:3]), en[3][2], en[3][3], d["e_free"], d["p_noon_now"], d["ta12"]))
    P("     (noon I / P: the regulating current's reduction against 23.2k and the input power's reduction it gives at bright noon; the")
    P("     panel's voltage rises when its current falls, so the power falls less than the current)")
    for x in d["approaches"]:
        wrapP("   ", "       ", "(%s) %s" % (x["id"], x["name"]))
        for k_ in ("warranted", "rating", "requirement", "assumption", "conditional"):
            if k_ in x["classes"]:
                wrapP("     - ", "       ", "%s: %s" % (k_, "; ".join(x["classes"][k_])))
        wrapP("     - ", "       ", "parts and board E: %s" % x["parts"])
        wrapP("     - ", "       ", "new failure mode: %s" % x["failure"])
        wrapP("     - ", "       ", "still depends on: %s" % x["depends"])
        wrapP("     - ", "       ", "the derived disturbance: %s" % x["surge"])
        if x["id"] == "B":
            wrapP("     - ", "       ", "its bound with every row at its printed value, %.4f W; the unprinted gain terms together may add %.3f %% before "
                  "100 W with an event (they print %.3f %% typical, not a limit); the conduction of its 4.5 mOhm package path (the shunt "
                  "included, typical) %.4f / %.4f Wh a day" % (b["p_static"], 100 * b["gain_be"], 100 * b["typ_gain"], b["loss"][0], b["loss"][1]))
    wrapP("   ", "     ", "THE CHOICE: (C), UNCONDITIONAL in its static bound. R60 to R64, %d %s (%s) in parallel, %.4f mOhm, carry everything "
          "entering the stage but R8, R9 and U18's VIN+ pin; U18 INA169 (SBOS181F) turns their voltage into a current into R65 %gk and R66 "
          "%gk (its %g kOhm test load); U19 TPS3701 trips at INB on R66 and watches TRK_VS at INA (R67 %gk, R68 %gk); either output pulls "
          "U20 TPS3808G33's MR, whose RESET holds SWEN low through R70 %gk over R71 %gk. The LT8705A's own limit stays as the regulation, "
          "coordinated under the trip: RIMON_IN %gk (%s), %.4f A nominal" % (
              c["n"], c["model"], c["code"], c["rbank"] * 1e3, rw["r65"] / 1e3, rw["r66"] / 1e3, (rw["r65"] + rw["r66"]) / 1e3,
              rw["r67"] / 1e3, rw["r68"] / 1e3, rw["r70"] / 1e3, rw["r71"] / 1e3, c["rm"][0] / 1e3, c["rm"][1], c["inom"]))
    wrapP("   ", "     ", "WHY (C): it is the one arrangement whose bound rests on printed limits at its own operating condition. (A) rests on "
          "assumptions about A7, the fault threshold and the cold TCR; (B) on rows printed at another supply, reference or current "
          "and on typical-only rows, and its sensor's %.0f V inputs fail the derived disturbance. (C)'s INA169 prints its common-mode "
          "and supply rejection at VSENSE = 50 mV over VIN+ and V+ 2.7 to 60 V, which covers the board's 9 to 25 V at the trip's 49.6 mV, "
          "and its transconductance, offset and nonlinearity over the full temperature range; the two rejections are carried at the "
          "larger of their offset and gain readings, so no row is extended past its condition" % sg["b_abs"])
    wrapP("   ", "     ", "THE STATIC BOUND: %.4f W at %.0f V (the highest trip current %.4f A at 25 V, the trip's sense voltage %.3f mV at most), "
          "margin %.4f W. Every term at the end that raises the trip, summed, each a printed limit at the condition it is used at, "
          "or, for U18's VIN+ pin, its printed absolute maximum (no common multiplier; no typical row; nothing assigned zero). "
          "SBOS181F p.6 prints every INA169 row over TA -40 to +85 C ('all other characteristics at'):" % (
              c["p_static"], c["v_hi"], c["i_hi25"], 1e3 * c["vs_hi"], 100.0 - c["p_static"]))
    for t_ in c["terms"]:
        wrapP("     - ", "       ", "%s: %s (%s; %s)" % t_)
    wrapP("   ", "     ", "THE TRIP: its lowest at the hold's voltages %.4f A with the parts aged (%.4f A at 25 V; %.4f A new), against the "
          "panel's highest current on SC-37's day at any hold corner, %.4f A: it never acts that day. One bank part carries at most "
          "%.3f W at the highest trip (its P70 is 1 W)" % (c["trip_lo_hold"], c["i_lo_aged"], c["i_lo_new"], c["pk_day"], c["p_bank_max"]))
    wrapP("   ", "     ", "THE DYNAMIC BOUND AND ITS AVERAGING BASIS (SESSION): REQ-016's 'at most 100 W into the stage' is judged as the mean "
          "input power over any %.1f s. Why: the limit sizes the stage's power parts, F2, J_SOLAR and the pack's charge, whose thermal "
          "and charge time constants are seconds and longer; a sub-millisecond event of tens of mJ is TRN-001's and the inrush's "
          "matter. The events: after a trip U20 holds SWEN low at least %.0f ms (CT to VDD through R69, SBVS050N p.7, full range), so "
          "any %.1f s holds one event at most. Its energy: the entry's capacitance at its largest (%.1f uF) charged to 25 V, %.1f mJ, "
          "plus the panel's %.2f W (25 V at REQ-016's %.2f A) over the chain's response. The response prints only typical rows: U18 "
          "about %.1f us, U19's INB rising edge %.1f us (the input edge, SBVS240C p.6, at 10 mV overdrive and a 100 kOhm load), U20's MR "
          "to RESET %.2f us, one switching period after SWEN falls (INFERRED): %.1f us together, giving %.4f W over %.1f s. The bound "
          "holds for a response up to %.3f ms; bench row 7b.16 reads it, and a slower response would overturn the %.1f s basis, not the "
          "arrangement (a longer basis or a lower trip restores it)" % (
              d["w_avg"], 1e3 * sq["td_min"], d["w_avg"], 1e6 * c["c_entry_max"], 1e3 * c["e_cap"], c["p_ev"], rw["amps_pk"],
              1e6 / rw["bw169"], 1e6 * rw["tpd_lh"], 1e6 * rw["mr_ns"], 1e6 * c["t_resp_typ"], c["p_dyn_typ"], d["w_avg"],
              1e3 * c["t_resp_max"], d["w_avg"]))
    wrapP("   ", "     ", "THE SUPPLY SEQUENCING (warranted rows, no Analog Devices answer): U20 asserts RESET whenever TRK_LDO33 is under its "
          "threshold, %.3f to %.3f V, and releases it only above %.3f V (VIT %.2f V, %.1f %% and its %.1f %% hysteresis, SBVS050N pp.3, 6), "
          "under LDO33's least in regulation, %.2f V (8705af p.3, full range); then it holds RESET a further %.0f ms at least, past "
          "U19's %.0f us start (SBVS240C p.6, typical). Where RESET is released, U19 (VDD from %.1f V) and U20 (from %.1f V) are inside their ranges, and U19's "
          "INA holds MR low whenever TRK_VS is under %.3f V (U18 works from 2.7 V) and lets it go by %.3f V at most, under the hold. R70 over R71 keep SWEN under its least threshold "
          "(%.3f V, 8705af p.4) until TRK_LDO33 reaches %.3f V, above both parts' least supply; at LDO33's least with RESET released SWEN "
          "reads %.3f V, over its highest threshold %.3f V. RESET sinks at most %.3f mA there (its VOL row %.1f V at 1 mA). Below 1.3 V the "
          "VOL rows end: SWEN could rise only if its pin sourced %.1f uA (8705af p.12 describes a logic input; no current row: INFERRED), and "
          "TRK_LDO33 under 1.3 V with INTVCC above its %.2f V lockout is an LDO33 failure, a single fault (below). The power-up reset (VPOR "
          "%.1f V) holds for a rise no faster than %.0f V/s; LDO33's %.0f mA limit into C20's 1 uF gives %.0f V/s (INFERRED: C20's "
          "capacitance at bias has no row). The arrangement draws at most %.0f uA from TRK_LDO33 (the IDD rows, the dividers, U20's MR "
          "pull-up at its least and CT's resistor), under the 5 mA its regulation row is printed at. U18's output at the highest trip, "
          "%.3f V into R65 + R66, stays under its compliance where the chain is armed, %.2f V (V+ less %.1f V at TRK_VS = %.3f V, "
          "SBOS181F p.6)" % (
              sq["vit_lo"], sq["vit_hi"], sq["rel_hi"], rw["vit38"], 100 * rw["acc38"], 100 * rw["hys38"], sq["ldo_lo"], 1e3 * sq["td_min"],
              1e6 * rw["st_t"], sq["vdd_t"], sq["vdd38"], sq["uv_ts_lo"], sq["uv_ts_hi"], rw["swen"][0], sq["ldo_enable_min"], sq["swen_at_ldo_lo"], rw["swen"][1],
              1e3 * sq["i_sw_reset"], sq["vol38"], 1e6 * sq["pin_needed_13"], sq["intvcc_uv"], sq["vpor"], sq["ramp_limit"],
              1e3 * rw["ilim33"], sq["ramp"], 1e6 * sq["i_ldo"], c["vout_hi"], sq["uv_ts_lo"] - rw["sw169"], rw["sw169"], sq["uv_ts_lo"]))
    e_c = c["energy"]
    wrapP("   ", "     ", "THE COORDINATION (SESSION, one basis at both corners): the smallest stocked RIMON_IN whose regulation at its highest "
          "under the joint assumptions (EA2 and EA3 at half gain, the line at twice, RSENSE1's cold TCR at 100 ppm/K, the drifts, each "
          "resistor at its worst end) stays at or under C's lowest trip with its parts aged, at every input voltage: %gk, %.4f A at 25 V "
          "against %.4f A. If the regulation's unprinted values were worse than those assumptions, the overlap would be a hiccup: each "
          "trip stops the stage %.0f to %.0f ms (SBVS050N p.7) and restarts it through the soft start; the bright day's hours whose panel "
          "current at the nominal hold exceeds C's lowest trip are %s, %.1f Wh, the energy such an overlap would put at risk" % (
              c["rm"][0] / 1e3, c["reg_hi25"], c["i_lo_aged"], float(rw["td38"][0]), float(rw["td38"][2]),
              ", ".join("%02d" % h for h, _g, _p in c["exposed"]) or "none", sum(p_ for _h, _g, p_ in c["exposed"])))
    wrapP("   ", "     ", "THE ENERGY: on SC-37's day %.1f / %.1f / %.1f Wh at the lower, nominal and upper hold corners (%d / %d / %d h bound) "
          "against %.1f / %.1f / %.1f Wh with 23.2k (%.1f Wh less at the nominal hold, %.1f Wh at the lower corner); on the bright day "
          "%.1f Wh (%d h bound) against %.1f Wh (%.1f Wh less); at bright noon the input "
          "power falls %.1f %% (the current %.1f %%). The bank's conduction (%.4f mOhm, the hourly current at the nominal hold) costs "
          "%.4f Wh on SC-37's day and %.4f Wh on the bright day; R59 stays. The bright day is the check's own (astra-check-l4e7r-1, "
          "D3) and this model reproduces its figures: %s" % (
              e_c[0][2], e_c[1][2], e_c[2][2], e_c[0][3], e_c[1][3], e_c[2][3], en[0][2], en[1][2], en[2][2], en[1][2] - e_c[1][2],
              en[0][2] - e_c[0][2], e_c[3][2], e_c[3][3], en[3][2], en[3][2] - e_c[3][2],
              100 * c["noon_red"], 100 * c["cur_red"], 1e3 * c["rbank"], c["loss"][0], c["loss"][1],
              "; ".join("%gk %.4f Wh, the noon power %.2f %% under 23.2k" % (rv_ / 1e3, e_, 100 * nr_) for rv_, e_, nr_ in c["check_repro"])))
    s59 = sg["s59"]
    wrapP("   ", "     ", "THE SOLAR ENTRY'S PROTECTION (B6; the derived disturbance, SESSION): no surge level is ruled (DECISION-31 section 3, "
          "D-04, D-16) and the tree holds no surge standard; TRN-001 asks the clamp to clamp below every protected part's absolute "
          "maximum, and D4's maker prints its clamping only at its rated pulse. So the design disturbance is that pulse: 10/1000 us "
          "(SMCJ p.1), %.1f A at D4, clamped at %.1f V at most (p.2); any source of impedance Z gives it with an open-circuit %.1f V "
          "+ %.1f A x Z. The assumption: no surge on the panel lead inside the kit's use exceeds D4's rating; a larger ruled level "
          "would need a larger clamp and parts rated above its clamping voltage, which changes ratings, not the arrangement (U18's "
          "inputs are rated %.0f V, U5's %.0f V)" % (sg["ipp"], sg["vc"], sg["vc"], sg["ipp"], sg["cm169_abs"], sg["vin_abs"]))
    wrapP("     - ", "       ", "the correction: D4 and the bulk move behind the sense bank onto TRK_VS, and the bulk becomes three Panasonic "
          "EEHZA1H330XP, %.0f V, 33 uF (ZA p.2, the same 6.3 x 7.7 mm land; %.0f mA ripple, %.0f mOhm), over D4's %.1f V; the 35 V parts "
          "were under it" % (rw["za"]["v"], 1e3 * rw["za"]["ripple"], 1e3 * rw["za"]["esr"], sg["vc"]))
    wrapP("     - ", "       ", "every part on the entry against it: TRK_VS and TRK_VIN at %.1f V at most: the bulk %.0f V, C13 to C15 50 V (the "
          "generator's value text: their maker parts are the regeneration's), C64 and C66 50 V (C14663), U5's VIN and sense pins %.0f V, "
          "Q3 60 V, U18's V+ and VIN- %.0f V, R67 75 V (RT), R14 %.1f V across it (the generator's 100k 1%%: its maker part is the "
          "regeneration's), SHDN %.2f V and FBIN %.2f V against their %.0f V; PV_P %.2f V at most (the bank's drop added): U18's VIN+, "
          "R8 75 V (RT)" % (sg["vc"], sg["za_v"], sg["vin_abs"], sg["vs169_abs"], sg["v_r14"], sg["v_shdn"], sg["v_fbin"], sg["fb_abs"], sg["v_pvp"]))
    wrapP("     - ", "       ", "U18's differential: the whole pulse crosses the bank, %.3f V at most against its %.0f V; U5's sense "
          "differential: R59 carries only the ceramics' share, %s (MODELED: the bulk's ESR %.0f mOhm new and %.1f Ohm after endurance at "
          "-40 C (ZA p.1), three in parallel, its capacitance at its least, the ceramics at their largest, the clamp left out), against "
          "%.1f V (8705af p.2)" % (sg["d169"], sg["d169_abs"], ", ".join("%.3f V %s" % (v_, l_) for l_, v_ in s59), 1e3 * rw["za"]["esr"],
                                    rw["za"]["esr_cold"], sg["csd_abs"]))
    wrapP("     - ", "       ", "electrostatic discharge (decision 34): its %.2f uC moves the entry by %.3f V at most and puts %.3f V across "
          "the bank; a reversed panel conducts through D4 as DECISION-31's note E-N1 records, now with U18's inputs near -1 V as well "
          "(its sheet allows a pin past its rating while the pin's current stays under %.0f mA, p.4; its gain resistor sits in the "
          "path: INFERRED), board E's owner's note" % (2.25, sg["esd_dv"], sg["esd_d169"], 1e3 * rw["ipin169"]))
    di = d["disc"]
    wrapP("   ", "     ", "THE SERIES DISCONNECT (the check's suggestion, evaluated, not taken; SESSION): %s" % di["why"])
    fl = d["faults"]
    wrapP("   ", "     ", "THE SINGLE FAULTS (assigned to layer 8's fault analysis): those that defeat the backstop: %s. Those that stop "
          "charging: %s. %s" % ("; ".join(fl["defeat"]), "; ".join(fl["stop"]), fl["acceptance"]))
    bd = R["backstop_draft"]
    n_e, _t, r10_once, codes_ok, codes = R["drafts"]["apply_gen_sch_e_backstop.py"]
    wrapP("   ", "     ", "THE DRAFT FOR BOARD E'S GENERATOR OWNER: apply_gen_sch_e_backstop.py, %d edit(s) on the text the hold and input "
          "limit drafts leave (it refuses a generator without them): the bank on PV_P to TRK_VS: %s; R59 and CSPIN behind it: %s; "
          "SWEN on TRK_SWEN: %s; D4 on TRK_VS: %s; the 50 V bulk: %s; R14 on TRK_VS: %s; R16 at %gk: %s; carries %s: %s; R10 untouched: "
          "%s. Read back here; never applied to the tree" % (
              n_e, "yes" if bd["bank"] else "NO", "yes" if (bd["cspin"] and bd["r59"]) else "NO", "yes" if bd["swen"] else "NO",
              "yes" if bd["d4"] else "NO", "yes" if bd["bulk"] else "NO", "yes" if bd["r14"] else "NO", c["rm"][0] / 1e3,
              "yes" if bd["r16"] else "NO", ", ".join(codes), "yes" if codes_ok else "NO", "yes" if r10_once else "NO"))
    wrapP("   ", "     ", "PROTOTYPE MEASUREMENTS (REQ-016's second method; downstream obligations, not blockers): 7b.15, on each built "
          "board, the input current at which SWEN falls, at 17.6 V and 25 V, against %.4f to %.4f A at 25 V, at commissioning and at "
          "layer 8's interval; 7b.16, the response from a current step over the trip to the last switching edge, against %.3f ms, and "
          "with R16 shorted (IMON_IN at 0 V, so neither the regulation nor its fault acts) the mean input over %.1f s at or under 100 W, "
          "each restart through the soft start; 7b.17, the regulation at %gk on a bench panel curve does not trip at 25 C and at the cold "
          "end; 7b.18, R59's differential under a 10/1000 us pulse at D4's rating, against %.1f V; 7b.19, TRK_LDO33's rise at power-up "
          "against %.0f V/s" % (c["i_lo_aged"], c["i_hi25"], 1e3 * c["t_resp_max"], d["w_avg"], c["rm"][0] / 1e3, sg["csd_abs"],
                                 sq["ramp_limit"]))
    wrapP("   ", "     ", "WHAT WOULD OVERTURN IT: a measured response over %.3f ms (the averaging basis, not the arrangement); a stock "
          "change of the bank part (LCSC %d on 1 October 2026; five per board), of U18 (%d) or U20 (%d); a ruled surge level above D4's "
          "rating (the clamp and the ratings, not the arrangement); Analog Devices warranting EA2, A7 and the line row, and Milliohm "
          "the cold TCR (the regulation would then hold the bound itself and C would be redundant protection); layer 8 finding a single "
          "fault that both defeats the backstop and removes the regulation" % (1e3 * c["t_resp_max"], c["stock"], rw["stock169"], rw["stock38"]))
    wrapP("   ", "     ", "WHAT REMAINS CONDITIONAL: nothing in C's static bound. The dynamic bound rests on the response's typical rows "
          "(bench row 7b.16, tolerance %.3f ms against %.1f us typical) and the %.1f s basis (SESSION); the supply sequencing below 1.3 V "
          "on TRK_LDO33 only through a fault (SWEN's pin current INFERRED); the surge protection on the stated design disturbance; the "
          "coordination and the energy on Analog Devices' and Milliohm's answers (EA2, A7, LINE, TCR, TJ), whose failure costs energy, "
          "not the bound" % (1e3 * c["t_resp_max"], 1e6 * c["t_resp_typ"], d["w_avg"]))
    wrapP("   ", "     ", "THE CLARIFICATION DRAFTS (adjusted; text for the owner to send, the session contacts no one): no answer moves "
          "C's bound. Analog Devices' and Milliohm's answers set the coordination and the energy; Analog Devices' item 5 now asks "
          "SWEN's input current and its delay to the last switching edge (the sequencing's one inference and bench row 7b.16). The "
          "Texas Instruments draft now asks the INA169's VIN+ pin current, carried at its absolute maximum meanwhile (supporting); "
          "the INA250 draft is withdrawn with approach B: %s" % ", ".join("clarification/" + c_ for c_ in d["clar"]))
    return o


def main():
    R = compute()
    sys.stdout.write("\n".join(render(R)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
