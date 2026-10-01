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
LT = "v2/vendor/power/lt8705a.pdf"
HOJ = "v2/vendor/passives/milliohm-hojlr2512-series.pdf"
RT = "v2/vendor/passives/held/yageo-rt-series-v16-2025-05-06.pdf"
BSC039 = "v2/vendor/infineon/infineon-bsc039n06ns-rev2.4-c534330.pdf"
BSC028 = "v2/vendor/power/held/infineon-bsc028n06ns-rev2.1-c148250.pdf"
INP = "v2/docs/records/l4e7/inputs"
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
HOLD_RANGE = (15.5, 17.5)  # SESSION: the hold pairs scanned have their nominal inside the candidate's hourly MPP span +- about 1 V
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

    # ================================================================== 4: the hold (R8 and R9), chosen against its energy
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
    best = hold_rows[0]
    r8v, r9v, r8c, r9c = best[2], best[3], best[4], best[5]
    for code, val in ((r8c, r8v), (r9c, r9v)):
        verify_rt(code, val)
    hb = band(r8v, r9v, 1.0)
    hb2 = band(r8v, r9v, EA2_FLOOR_DIV)
    hb3 = band(r8v, r9v, EA2_FLOOR_DIV, drifts=True)
    R.update(r8v=r8v, r9v=r9v, r8c=r8c, r9c=r9c, hb=hb, hb2=hb2, hb3=hb3, hold_rows=hold_rows[:8], n_hold=len(hold_rows),
             hold_drawn=(LR["v_lo"], LR["v_nom_hold"], LR["v_hi_hold"]), stock={r_["code"]: r_["stock"] for r_ in rtj})
    # the hourly maximum-power voltage on SC-37's day (the model's own), for the hold's reason
    AC = LR["AC"]
    vmpp = [dsp.mpp(LR["prof0"][h], AC.t_cell(LR["TA40"][h], LR["prof0"][h], LR["noct"]))[0] for h in range(24) if LR["prof0"][h] >= 100.0]
    R["vmpp"] = (min(vmpp), max(vmpp))

    # ================================================================== 5: THE CORNER CHECK on the achieved values
    v_lo_env = min(hb[0], hb2[0])
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

    def breakeven_tcr_cold():
        """RSENSE1's TCR below 25 C at which the cold 25 V corner (the worst, above) reaches 100 W; searched up to 10000 ppm/K,
        inside which the low end (1 - TCR x 45 K) stays positive and the power rises with the TCR."""
        dt = abs(END[0][1] - 25.0)
        rm_lo = rfac(tol_y, tcr_y, END[0][2] - 25.0)
        f = lambda tc: v_oc * i_nom * corner_k(v_oc, ea2, 1.0, rfac(tol_h, tc, dt), rm_lo)
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
    R["be_tcr_cold"] = breakeven_tcr_cold()
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
                   ("lower, EA3 at its floor", hb2[0]), ("upper, EA3 at its floor", hb2[2])):
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
    for lab, tr in (("NEW nominal (hold %.3f V, limit %.3f A)" % (nom_h, i_nom), tr_nom), ("NEW least-energy corner (%s)" % lab_w, tr_w)):
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
    P("     Rule (SESSION): of the %d stocked pairs with a nominal from %.1f to %.1f V, the one whose band's worse end gives the most energy" % (
        R["n_hold"], HOLD_RANGE[0], HOLD_RANGE[1]))
    P("     on SC-37's day (the model's hourly maximum-power voltage there runs %.2f to %.2f V). The best eight (worse end Wh, pair, band):" % R["vmpp"])
    for row in R["hold_rows"]:
        P("       %.1f Wh  %5.1fk / %4.2fk  %.3f / %.3f / %.3f V" % (row[0], row[2] / 1e3, row[3] / 1e3, row[6], row[7], row[8]))
    P("     the band (FBIN's I-grade limits, its line term, the FBIN bias, R8 and R9 at 0.1 % and 25 ppm/K at both ends):")
    P("       EA3 at its typical %.0f V/V: %.3f / %.3f / %.3f V; EA3 at half: %.3f / %.3f V; with the resistors' drifts too: %.3f / %.3f V" % (
        R["ea3"], R["hb"][0], R["hb"][1], R["hb"][2], R["hb2"][0], R["hb2"][2], R["hb3"][0], R["hb3"][2]))
    P("     as drawn the band was %.3f / %.3f / %.3f V (the replay: 1 %% parts, H and MP's FBIN minimum)" % R["hold_drawn"])
    P("")
    P("4. THE 100 W CORNER CHECK ON THE ACHIEVED VALUES (section 11's physics: the replay's i_factor, 8705af p.31)")
    P("   envelope: %.3f V (the hold's lowest, EA3 at half) to REQ-016's %.0f V in %.2f V steps; I grade; both ends:" % (
        min(R["hb"][0], R["hb2"][0]), 25.0, V_STEP))
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
    P("   THE UNPRINTED ROWS, as break-even values for this setting (the corner reaches 100 W at the value shown):")
    for (lm, dr), (gc, gh) in sorted(R["be_gain"].items()):
        P("     EA2's gain, line x%-4g%-14s cold end %s V/V, hot end %s V/V" % (lm, ", with drifts" if dr else "", "%.1f" % gc if gc else "none passes",
                                                                       "%.1f" % gh if gh else "none passes"))
    P("     the line regulation (cold end) at EA2 130 V/V: up to %.1f times its printed maximum (%.3f %%/V); at 65 V/V: %.1f times" % (
        R["be_line"][0], R["be_line"][0] * R["line_p"], R["be_line"][1]))
    P("     RSENSE1's TCR below 25 C (HoJLR prints its TCR from +25 to +125 C only, so the cold end applies it as an ASSUMPTION): the")
    P("     cold corner passes up to %s" % ("%.0f ppm/K" % (R["be_tcr_cold"] * 1e6) if R["be_tcr_cold"] is not None else "10000 ppm/K and beyond"))
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
    P("   the margin's cost on this day: %.1f Wh at the most over the fifteen cells (chosen less zero-margin from %+.1f to %+.1f Wh:" % (
        max(0.0, -min(d_)), min(d_), max(d_)))
    P("   where the chosen limit binds below the panel's maximum-power point, the voltage rides up toward it)")
    P("   as drawn (the replay, section 12, no input limit): %s" % "; ".join("%.1f Wh at %.3f V" % (g_[3], g_[1]) for g_ in R["old_grid"]
                                                                        if g_[2] == "no input limit (as drawn)"))
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
    P("   - EA2's voltage gain (130 V/V TYP, p.5) and VC's operating range: the corner passes down to %.1f V/V (cold end, line x1)." % R["be_gain"][(1.0, False)][0])
    P("     Bench: in input-current limit at 25 V, step the load to move VC across its range, read VC and IMON_IN; the gain is")
    P("     dVC / dV(IMON_IN); accept at or above 65 V/V (the floor), and at least the break-even at every point")
    P("   - the IMON_IN reference's line regulation while switching and at both ends (printed at 25 C, not switching, p.4): the corner")
    P("     passes up to %.0f times its printed maximum. Bench: the limit's current at VIN 16 and 25 V, switching, at both ends" % R["be_line"][0])
    P("   - RSENSE1's TCR below +25 C (HoJLR p.4 tests +25 to +125 C): passes up to %s. Bench: R59 at -20 C and +25 C" % (
        "%.0f ppm/K" % (R["be_tcr_cold"] * 1e6) if R["be_tcr_cold"] is not None else "10000 ppm/K and beyond"))
    P("   - EA3's gain (90 V/V TYP) and the FBIN bias (10 nA TYP): energy only (the hold band above); the bench reads the hold at both ends")
    P("   - U5's junction (INFERRED from the gate charge at 10 V and theta-JA): the CLKOUT duty cycle method of p.34 (+-10 C)")
    P("   - the candidate panel's own source compliance (O-1) and every efficiency (C-8): unchanged by this record")
    P("")
    P("8. BENCH ROWS")
    P("   7b.9 (steady state): a PV emulator puts the loaded input at the limit from %.3f V to 25 V, at the load's maximum, cold-soaked" % R["hb"][0])
    P("     at %.0f C and in %.1f C air; V_in x I_in at or under 100 W at every point; the limit's current at 25 V at most %.3f A" % (
        R["t_cold"], R["t_air"], 100.0 / 25.0))
    P("   7b.9t (transients, recorded apart): a source step (open circuit to the limit) and an irradiance step; the peak and the")
    P("     time above 100 W against the filter's %.2f ms (SESSION: no fault trip, IMON_IN under %.2f V; above 100 W no longer than" % (
        R["tau"] * 1e3, R["iovm"]["min"]))
    P("     five time constants, %.1f ms)" % (5 * R["tau"] * 1e3))
    P("   7b.10 the EA2 gain row and 7b.11 the line row above; 7b.12 the hold: the panel held at %.3f to %.3f V at both ends" % (R["hb"][0], R["hb"][2]))
    P("   7b.13 U5's junction by CLKOUT at all four switches, EXTVCC at the ceiling, %.1f C air: at most 125 C less p.34's 10 C" % R["t_air"])
    return o


def main():
    R = compute()
    sys.stdout.write("\n".join(render(R)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
