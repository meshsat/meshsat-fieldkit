#!/usr/bin/env python3
"""S-120: board A's charge bus VBUS20 and the charger's switch nodes against the 30 V FETs of decision 57 (stream s120,
MESHSAT-1357, 29 September 2026; second issue after the independent check `_scratch/chk-s120/CHECK.md`, B1 to B3 and m1 to
m11; third issue after the re-check `CHECK-2.md`, B1 and n1 to n7). Desk arithmetic on the makers' figures and the
committed netlists: nothing is built, powered or measured, and nothing here is a qualified review (AI engineering work).

WHAT IT DOES. It PARSES board A's and board E's committed netlists (v2/ecad/tools/netlist_sexp.py; nothing is grepped) and
asserts every circuit fact the bound rests on (section 1): the front end U2's feedback divider, its pins, its sense
resistors and their filter, its inductor and the direction of its FETs; VBUS20's whole membership (so no new source or
clamp can join the bus unseen); the charger U3's pins, its cell strap, its four FETs and their nets;
the clamps on VIN_RAW and VBAT; board E's over-voltage lockout divider and its clamps. Each detail line prints what the
netlist holds, not what is expected, and a fact that does not hold is printed FAIL with exit status 1. The gate holds only
what the bound rests on; U3's input sense filter, which the bound does not use, is printed as a RECORD line and gates
nothing (the re-check's n5: a gate on the absence of TI's CACP and CACN would refuse the closure when they are added). Then it computes the
bus's worst case mechanism by mechanism (sections 2 to 8) from the makers' figures, each quoted with its document, revision
and printed page, the margins per part (section 9), the switch nodes' budget (section 10), the single faults outside every
requirement (section 11) and the answer (section 12).

LABELS. A figure the maker states is quoted. INFERRED marks a figure the maker does not state (a curve reading, a
tolerance the maker leaves out, a typical figure carried to a worst case); MODEL marks an estimate from a simplified circuit
model that is not a bound. THE BUS'S BOUND IS INFERRED: it rests on the LM5176's output over-voltage threshold, which TI
gives as a typical 10 percent only.

Usage: python3 vbus20_bound.py [--net-a PATH] [--net-e PATH] > vbus20_bound.out   (deterministic; the committed .out is this
       script's output on the committed netlists). Exit 0 every fact holds, 1 a fact fails, 3 a netlist cannot be read."""
import argparse
import hashlib
import math
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import netlist_sexp as N  # noqa: E402

NET_A = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"
NET_E = "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"

# ------------------------------------------------------------------------------------------------ the makers' figures
# TI SNVSAI1D (LM5176, June 2017, revised August 2021), v2/vendor/ti/lm5176-datasheet.pdf; printed page = PDF page.
VREF = (0.788, 0.800, 0.812)          # 6.5 p.6, FB = COMP, -40 to 125 C
IBIAS_FB = 25e-9                      # 6.5 p.6, IBIAS(FB) maximum; its direction is not stated, so it is taken both ways
OVP_TYP = 0.10                        # 6.5 p.8, VOVP "Measured with respect to VREF": 10 % TYPICAL, no minimum or maximum
OVP_HYST = 0.025                      # 6.5 p.8, hysteresis 2.5 %; no response time is given (7.3.11 p.18)
VCS_BOOST_MAX = 0.140                 # 6.5 p.7, boost current limit (peak) 100 / 120 / 140 mV, HTSSOP-28
VCS_BUCK_MAX = 0.094                  # 6.5 p.7, buck current limit (valley) 66 / 80 / 94 mV, HTSSOP-28
IOFFSET_CS = 19e-6                    # 6.5 p.7, IOFFSET(CS/CSG) 19 uA maximum: across the 100 Ohm filter resistors it moves
                                      # the sensed voltage, taken here in the direction that raises the current limit
FSW_MIN = 175e3                       # 6.5 p.6, fSW(1) 175 / 200 / 225 kHz at RT 40 kOhm (board A draws 40.2 k)
LM_ABS = {"VIN": 60.0, "VISNS": 60.0, "VOSNS": 60.0, "BIAS": 40.0}   # 6.1 p.5
LM_REC_VIN = 55.0                     # 6.3 p.5

# TI SLUSE66A (BQ25731, June 2020, revised January 2021), v2/vendor/ti/bq25731-datasheet.pdf; printed page = PDF page.
BQ_ABS = {"VBUS, ACP, ACN": 32.0, "SRN, SRP, VSYS": 32.0, "SW1, SW2": 32.0, "BTST1, BTST2, HIDRV1, HIDRV2": 38.0}  # 8.1 p.8
BQ_ABS_SW_NEG = (-2.0, -4.0)          # 8.1 p.8: SW1, SW2 -2 V, and -4 V for 25 ns
BQ_ABS_BTST_SW = 7.0                  # 8.1 p.8, BTST1-SW1, BTST2-SW2 differential
BQ_REC = {"VBUS, ACP, ACN": 26.0, "SRN, SRP, VSYS": 23.15, "SW1, SW2": 26.0, "BTST1, BTST2, HIDRV1, HIDRV2": 32.0}  # 8.3 p.8
BQ_REC_BTST_SW = 6.5                  # 8.3 p.8
ACOV = (26.0, 26.8, 27.7)             # 8.5 p.14, VVBUSOV_RISE; tVBUSOV_RISE_DEG 100 us "VBUS converter rising to stop converter"
SYSOVP_4S = (19.0, 19.5, 20.0)        # 8.5 p.14, VSYSOVP_RISE for 3s and 4s, "to turnoff converter"
VBAT_REG, VBAT_REG_ACC = 16.8, 0.005  # 8.5 p.9, REG0x05/04 = 0x41A0: 16.8 V, -0.5 % to +0.5 % (0 to 85 C)
BATOVP_MAX = 1.05                     # 8.5 p.14, VBATOVP_RISE for 2 s and more: 102.3 / 104 / 105 % of VBAT_REG
VCELL_4S = (0.684, 0.75, 0.815)       # 8.5 p.18, CELL_BATPRESZ as a fraction of VDDA for the 4s setting
VREGN = (5.7, 6.0, 6.3)               # 8.5 p.11, VREGN_REG
RDS_HI_ON_TYP, RDS_HI_OFF_TYP = 6.0, 1.3   # 8.5 p.16, the high-side gate driver loop (typical; the ON figure has no max)

# TI SLPS526 (CSD17578Q5A, March 2015) and SLPS516 (CSD17577Q5A, August 2014): held back by TI's terms, pinned by sha256 in
# v2/vendor/sources.txt, fetched by v2/docs/records/s117/fetch_held_back.py into v2/vendor/ti/held/ (ignored).
FET_VDS = 30.0                        # p.1 Absolute Maximum Ratings VDS 30 V; 5.1 p.3 BVDSS 30 V minimum at 250 uA
Q8_VSD_MAX = 1.0                      # SLPS516 5.1 p.3: VSD 0.8 typical, 1.0 V maximum at ISD 18 A. Q7 holds the bus PLUS
                                      # this drop in every dead time, when L2's current runs through Q8's body diode
Q7 = dict(part="CSD17578Q5A", qgs=3.1e-9, qgth=1.7e-9, rg=1.8, eas="23 mJ (ID 22 A, L 0.1 mH)")          # SLPS526 pp.1, 3
Q8 = dict(part="CSD17577Q5A", qrr=8.2e-9, qrr_test="15 V, 18 A, 300 A/us", eas="39 mJ (ID 28 A, L 0.1 mH)")  # SLPS516 pp.1, 3
Q7_VPLT = 2.7                         # INFERRED: the plateau read from SLPS526 Figure 4 p.5 at 10 A (s117 efficiency.py)

# Littelfuse SMCJ series (revised 11/20/15), v2/vendor/power/littelfuse-smcj-series-tvs.pdf, the table on page 2 of 6:
# (standoff VR, VBR min, VBR max at IT 1 mA, VC max at IPP, IPP)
SMCJ = {"SMCJ18A": (18.0, 20.00, 22.10, 29.2, 51.4), "SMCJ22A": (22.0, 24.40, 26.90, 35.5, 42.3),
        "SMCJ40A": (40.0, 44.40, 49.10, 64.5, 23.3)}

# TI SNVS452G (LM5069), v2/vendor/ti/ti-lm5069.pdf, 6.5 p.5: OVLOTH 2.4 / 2.5 / 2.6 V.
OVLOTH = (2.4, 2.5, 2.6)

# Parts and the project's own records.
TOL_R = 0.01                          # the printed 1 % of the divider, the sense resistors and the straps
TCR_DRIFT = 100e-6 * 65               # INFERRED: 100 ppm/K over 65 K, the convention S-116 uses for the same class of part
L1_NOM, L_TOL = 10e-6, 0.20           # Coilcraft XAL1010 (v2/vendor/power/coilcraft-xal1010.pdf): +-20 %; Isat 17.5 A
L2_NOM = 4.7e-6
BULK_C, BULK_N, BULK_TOL = 330e-6, 6, 0.20   # Panasonic ZK (v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf): +-20 %
FC_MIN, ZOUT_MAX = 710.0, 0.089       # MODEL: gen_sch_a.py lines 722 to 724 (loop_verify.py FE 6 V331 15 21: crossover
                                      # 0.71 to 3.6 kHz, |Zout| 89 mOhm), the front end's own loop model, not a maker figure
I_IN_A2, I_IN_DECL = 6.45, 8.0        # s117 charger_l_f.out A2 (U3's 6.35 A clamp plus 0.1 A); VBUS20's declared peak
                                      # (gen_sch_a.py line 109)
IL2_PK = {"A2": 15.71, "G1": 14.10, "A1": 10.70}   # s117 charger_l_f.out section 2, XAL1010-472ME, worst peak
IL2_DI = {"A2": 4.72, "G1": 4.60, "A1": 3.70}      # the same rows, worst ripple (so the valley is the peak less it)
VBAT_CUV = 10.0                       # the pack at the primary protector's CUV (review-packets/battery/FUSE-INTERPRETATION.md)
VSD_TYP = 0.8                         # INFERRED for a body diode carrying a few amperes (SLPS516 and CSD19532Q5B typical)

# VBUS20's whole membership on board A as generated, (reference, pin): what each is for. Nothing on it drives the bus but
# U2 through R11; the charger's pin 1 cannot (OTG needs its pin 5 high).
VBUS20_MEMBERS = sorted(
    [("C%d" % n, "1") for n in (163, 178, 179, 180, 199, 200)]                          # the six EEHZK1V331P bulk parts
    + [("C%d" % n, "1") for n in list(range(181, 190)) + list(range(201, 207)) + [20, 21, 22]]   # eighteen 10 uF ceramics
    + [("C192", "1"), ("R11", "2"), ("R147", "1"), ("R16", "1"), ("R161", "1"), ("R197", "1"), ("R202", "1"),
       ("R203", "1"), ("R204", "1"), ("R205", "1"), ("R6", "1"), ("TP12", "1"), ("U2", "12"), ("U2", "24"), ("U3", "1")])

FIG = {}                              # main() leaves its figures here for apply_registry_s120.py (read, never re-typed)


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def val(doc, ref):
    c = doc["components"].get(ref)
    return c["value"] if c else "(absent)"


def pins(doc, ref):
    return {p: v["net"] for p, v in doc["pins"].get(ref, {}).items()}


def members(doc, net):
    return sorted({r for r, *_ in doc["nets"].get(net, [])})


def ohms(value):
    """The resistance a value string states, in Ohm, or None: '13.3k 1% (...)' is 13300, '100R 1%' is 100, '4R7' is 4.7."""
    m = re.match(r"\s*(\d+(?:\.\d+)?)\s*([kKMR]?)(\d*)", value or "")
    if not m:
        return None
    whole, mult, frac = m.groups()
    x = float(whole + ("." + frac if frac and "." not in whole else ""))
    return x * {"k": 1e3, "K": 1e3, "M": 1e6, "R": 1.0, "": 1.0}[mult]


def tol(value):
    """The tolerance a value string states, as a fraction, or None."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", value or "")
    return float(m.group(1)) / 100 if m else None


def pinmap(doc, ref, which):
    p = pins(doc, ref)
    return ", ".join("%s %s" % (k, p.get(k, "(none)")) for k in which)


def facts(a, e):
    """Every circuit fact the bound rests on, read from the parsed netlists: (name, holds, detail). The detail is what the
    netlist holds; the condition is what the bound needs."""
    out = []

    def add(name, ok, detail):
        out.append((name, bool(ok), detail))

    add("U2 FB divider", sorted(pins(a, "R6").values()) == ["FE_FB", "VBUS20"] and val(a, "R6") == "240k 1%"
        and sorted(pins(a, "R7").values()) == ["FE_FB", "GND"] and val(a, "R7") == "10k 1%",
        "R6 %s on %s; R7 %s on %s" % (val(a, "R6"), sorted(pins(a, "R6").values()), val(a, "R7"), sorted(pins(a, "R7").values())))
    u2 = pins(a, "U2")
    add("U2 pins", (u2.get("11"), u2.get("12"), u2.get("24"), u2.get("2"), u2.get("3"))
        == ("FE_FB", "VBUS20", "VBUS20", "FE_VINP", "FE_VISNS"),
        "U2 pins %s (FB, VOSNS, BIAS, VIN, VISNS)" % pinmap(a, "U2", ("11", "12", "24", "2", "3")))
    add("U2 MODE", sorted(pins(a, "R119").values()) == ["FE_MODE", "FE_VCC"],
        "R119 %s on %s: to VCC is CCM with hiccup disabled (SNVSAI1D 7.4.2 p.20)" % (val(a, "R119"), sorted(pins(a, "R119").values())))
    add("front end sense", sorted(pins(a, "R11").values()) == ["FE_OUT", "VBUS20"] and val(a, "R11").startswith("10mOhm 1%")
        and sorted(pins(a, "R12").values()) == ["FE_CS", "GND"] and val(a, "R12").startswith("5mOhm 1%"),
        "R11 %s on %s; R12 %s on %s" % (val(a, "R11"), sorted(pins(a, "R11").values()), val(a, "R12"), sorted(pins(a, "R12").values())))
    rcf = [ohms(val(a, r)) for r in ("R150", "R151")]
    add("CS filter", sorted(pins(a, "R150").values()) == ["FE_CS", "FE_CSF"] and sorted(pins(a, "R151").values()) == ["FE_CSGF", "GND"]
        and None not in rcf and max(rcf) <= 100.0 and u2.get("16") == "FE_CSF" and u2.get("15") == "FE_CSGF",
        "R150 %s on %s; R151 %s on %s; U2 pins %s" % (val(a, "R150").split(" (")[0], sorted(pins(a, "R150").values()),
                                                      val(a, "R151").split(" (")[0], sorted(pins(a, "R151").values()),
                                                      pinmap(a, "U2", ("16", "15"))))
    add("L1", sorted(pins(a, "L1").values()) == ["FE_SW1", "FE_SW2"] and val(a, "L1").startswith("10uH XAL1010-103ME"),
        "L1 %s on %s" % (val(a, "L1"), sorted(pins(a, "L1").values())))
    q2, q5 = pins(a, "Q2"), pins(a, "Q5")
    add("Q2 and Q5 direction", q2.get("5") == "VIN_RAW" and {q2.get(k) for k in "123"} == {"FE_SW1"}
        and q5.get("5") == "FE_OUT" and {q5.get(k) for k in "123"} == {"FE_SW2"},
        "Q2 drain %s, source %s; Q5 drain %s, source %s (%s): Q2's body diode points from its source to VIN_RAW, so an "
        "idle stage blocks VIN_RAW" % (q2.get("5"), q2.get("1"), q5.get("5"), q5.get("1"), val(a, "Q2").split(" (")[0]))
    vb = sorted((r, p) for r, p, *_ in a["nets"].get("VBUS20", []))
    extra, missing = sorted(set(vb) - set(VBUS20_MEMBERS)), sorted(set(VBUS20_MEMBERS) - set(vb))
    bulk = [r for r, _ in vb if "EEHZK1V331P" in val(a, r)]
    cer = [r for r, _ in vb if val(a, r).startswith("10u 50V X7R")]
    add("VBUS20 membership", not extra and not missing and len(bulk) == BULK_N and len(cer) == 18,
        "%d members; not in the expected list: %s; expected and absent: %s; %d x EEHZK1V331P, %d x 10 uF 50 V X7R"
        % (len(vb), ", ".join("%s.%s" % x for x in extra) or "none", ", ".join("%s.%s" % x for x in missing) or "none",
           len(bulk), len(cer)))
    diodes = [r for r, _ in vb if r.startswith("D") or a["components"][r]["libpart"].startswith("D")]
    add("no clamp on VBUS20", not diodes, "diodes on VBUS20: %s" % (", ".join(diodes) or "none"))
    add("U3 pins", (pins(a, "U3").get("1"), pins(a, "U3").get("5"), pins(a, "U3").get("22"), pins(a, "U3").get("32"),
                    pins(a, "U3").get("23"), pins(a, "U3").get("30"), pins(a, "U3").get("25"), pins(a, "U3").get("18"))
        == ("VBUS20", "GND", "VBAT", "CH_SW1", "CH_SW2", "CH_BTST1", "CH_BTST2", "CH_CELL"),
        "U3 pins %s (VBUS, OTG/VAP/FRS, VSYS, SW1, SW2, BTST1, BTST2, CELL_BATPRESZ); OTG, VAP and FRS each need pin 5 "
        "high (9.3.9 p.27, EN_OTG p.64, IN_VAP p.49, pin table p.6): pin 5 is %s"
        % (pinmap(a, "U3", ("1", "5", "22", "32", "23", "30", "25", "18")),
           "on GND, so the charger cannot drive VBUS20" if pins(a, "U3").get("5") == "GND" else "NOT on GND"))
    r26, r27 = pins(a, "R26"), pins(a, "R27")
    rt, rb_, tt, tb = ohms(val(a, "R26")), ohms(val(a, "R27")), tol(val(a, "R26")), tol(val(a, "R27"))
    ok_vals = None not in (rt, rb_, tt, tb)
    lo = rb_ * (1 - tb) / (rb_ * (1 - tb) + rt * (1 + tt)) if ok_vals else float("nan")
    hi = rb_ * (1 + tb) / (rb_ * (1 + tb) + rt * (1 - tt)) if ok_vals else float("nan")
    inside = ok_vals and VCELL_4S[0] <= lo and hi <= VCELL_4S[2]
    add("U3 cell strap", sorted(r26.values()) == ["CH_CELL", "CH_VDDA"] and sorted(r27.values()) == ["CH_CELL", "GND"] and inside,
        "R26 %s on %s, R27 %s on %s: CELL_BATPRESZ at %.2f to %.2f %% of VDDA from those values, against the 4s window 68.4 "
        "to 81.5 %% (SLUSE66A p.18): %s" % (val(a, "R26").split(" (")[0], sorted(r26.values()), val(a, "R27"),
                                           sorted(r27.values()), lo * 100, hi * 100,
                                           "inside, so SYSOVP is the 4S 19.0 to 20.0 V" if inside else "NOT inside"))
    want = {"Q7": ("CSD17578Q5A", "CH_ACN", "CH_SW1"), "Q8": ("CSD17577Q5A", "CH_SW1", "GND"),
            "Q9": ("CSD17577Q5A", "CH_SW2", "GND"), "Q10": ("CSD17577Q5A", "VBAT", "CH_SW2")}
    for q, (part, d, s) in sorted(want.items()):
        p = pins(a, q)
        add(q, val(a, q).startswith(part) and p.get("5") == d and {p.get(k) for k in "123"} == {s},
            "%s drain %s, source %s" % (val(a, q), p.get("5"), sorted({p.get(k) for k in "123"})))
    acn_caps = sorted((r, val(a, r)) for r in members(a, "CH_ACN") if r.startswith("C"))
    add("R16 and CH_ACN", sorted(pins(a, "R16").values()) == ["CH_ACN", "VBUS20"] and acn_caps == [("C190", "10n"), ("C191", "1n")],
        "R16 %s on %s; capacitors on CH_ACN: %s (SLUSE66A p.86: at most 10 nF + 1 nF after RAC, Figure 10-3 p.85)"
        % (val(a, "R16"), sorted(pins(a, "R16").values()), ", ".join("%s %s" % x for x in acn_caps) or "none"))
    add("D1 on VBAT", pins(a, "D1") == {"1": "VBAT", "2": "GND"} and val(a, "D1").startswith("SMCJ18A"),
        "D1 %s, pins %s" % (val(a, "D1"), pinmap(a, "D1", ("1", "2"))))
    add("D2 on VIN_RAW", pins(a, "D2") == {"1": "VIN_RAW", "2": "GND"} and val(a, "D2").startswith("SMCJ40A"),
        "D2 %s, pins %s" % (val(a, "D2").split(" (")[0], pinmap(a, "D2", ("1", "2"))))
    add("board E OVLO", sorted(pins(e, "R22").values()) == ["DC_P", "HS_OVLO"] and val(e, "R22") == "100k 1%"
        and sorted(pins(e, "R23").values()) == ["GND_V", "HS_OVLO"] and val(e, "R23").startswith("6.65k 1%")
        and pins(e, "U6").get("4") == "HS_OVLO",
        "U6 %s pin 4 on %s; R22 %s on %s; R23 %s on %s" % (val(e, "U6").split(":")[0], pins(e, "U6").get("4"), val(e, "R22"),
                                                            sorted(pins(e, "R22").values()), val(e, "R23").split(" (")[0],
                                                            sorted(pins(e, "R23").values())))
    add("board E clamps", val(e, "D1").startswith("SMCJ40A") and pins(e, "D1").get("1") == "DC_P"
        and val(e, "D2").startswith("SMCJ40A") and pins(e, "D2").get("1") == "VIN_RAW"
        and val(e, "D10").startswith("SMCJ40CA") and pins(e, "D10").get("1") == "DC_F",
        "; ".join("%s %s pin 1 on %s" % (r, val(e, r).split(" (")[0], pins(e, r).get("1")) for r in ("D10", "D1", "D2")))
    return out


def records(a):
    """What the netlist holds that the text describes but the bound does not rest on: printed, never gated (n5)."""
    out = []
    for net in ("CH_ACN_F", "CH_ACP_F"):
        mem = sorted(a["nets"].get(net, []))
        to_gnd = sorted(r for r, *_ in mem if r.startswith("C") and "GND" in pins(a, r).values())
        out.append("%s holds %s; capacitors from it to GND: %s" % (
            net, ", ".join("%s.%s %s" % (r, pn, val(a, r).split(" (")[0]) for r, pn, *_ in mem), ", ".join(to_gnd) or "none"))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--net-a", default=os.path.join(TOP, NET_A))
    ap.add_argument("--net-e", default=os.path.join(TOP, NET_E))
    ar = ap.parse_args(argv)
    try:
        a, e = N.load(ar.net_a), N.load(ar.net_e)
    except (OSError, ValueError) as x:
        print("vbus20_bound: cannot read a netlist: %s" % x)
        return 3
    FIG.clear()
    P = print
    P("S-120: board A's charge bus VBUS20 and the charger's switch nodes against the 30 V FETs of decision 57. MESHSAT-1357,")
    P("stream s120, second issue. Desk arithmetic on the makers' figures and the committed netlists; nothing is built, powered")
    P("or measured. INFERRED = a figure the maker does not state; MODEL = an estimate from a simplified circuit, not a bound.")
    P("netlist A %s sha256/16 %s" % (NET_A, sha16(ar.net_a)))
    P("netlist E %s sha256/16 %s" % (NET_E, sha16(ar.net_e)))
    P("")
    P("1. THE CIRCUIT AS GENERATED (parsed from the netlists; each detail is what the netlist holds)")
    fs = facts(a, e)
    for name, ok, detail in fs:
        P("   %-4s %-22s %s" % ("PASS" if ok else "FAIL", name, detail))
    nbad = sum(1 for _, ok, _ in fs if not ok)
    FIG.update(sha_a=sha16(ar.net_a), sha_e=sha16(ar.net_e), facts=len(fs), facts_bad=nbad)
    P("   facts: %d of %d hold" % (len(fs) - nbad, len(fs)))
    P("   RECORD, not gated (U3's input sense filter; TI's Figure 10-3, p.85, draws 4.99 Ohm, CDIFF 10 nF and CACP, CACN 33 nF):")
    rec = records(a)
    for line in rec:
        P("     %s" % line)
    FIG.update(acn_f_caps=rec)
    P("")

    # 2. regulation
    rtop, rbot = 240e3, 10e3
    r_nom = 1 + rtop / rbot
    r_hi_i, r_lo_i = 1 + rtop * (1 + TOL_R) / (rbot * (1 - TOL_R)), 1 + rtop * (1 - TOL_R) / (rbot * (1 + TOL_R))
    dt = TOL_R + TCR_DRIFT
    r_hi_t, r_lo_t = 1 + rtop * (1 + dt) / (rbot * (1 - dt)), 1 + rtop * (1 - dt) / (rbot * (1 + dt))
    dv_bias = IBIAS_FB * rtop * (1 + dt)
    v_nom = VREF[1] * r_nom
    v_hi_i, v_lo_i = VREF[2] * r_hi_i, VREF[0] * r_lo_i
    v_hi = VREF[2] * r_hi_t + dv_bias
    v_lo = VREF[0] * r_lo_t - dv_bias
    P("2. THE FRONT END'S REGULATION (VOUT = VREF x (1 + R6 / R7); VREF 0.788 / 0.800 / 0.812 V, SNVSAI1D 6.5 p.6)")
    P("   nominal                                         %6.3f V" % v_nom)
    P("   VREF and the printed 1 %% only                   %6.3f to %6.3f V" % (v_lo_i, v_hi_i))
    P("   with 100 ppm/K over 65 K (INFERRED) and IBIAS(FB) 25 nA both ways (p.6, %.1f mV)   %6.3f to %6.3f V   <- the DC band"
      % (dv_bias * 1e3, v_lo, v_hi))
    P("")

    # 3. OVP and the largest L1 current inside U2's ratings
    ovp_nom = VREF[1] * (1 + OVP_TYP) * r_nom
    ovp_hi = VREF[2] * (1 + OVP_TYP) * r_hi_t + dv_bias
    rcs = 0.005 * (1 - TOL_R)
    voff = IOFFSET_CS * 100.0
    l1_lo = L1_NOM * (1 - L_TOL)
    ripple = lambda vin, vout: (vin - vout) * (vout / vin) / (l1_lo * FSW_MIN)
    i_boost = (VCS_BOOST_MAX + voff) / rcs
    i_valley = (VCS_BUCK_MAX + voff) / rcs
    i_buck = {v: i_valley + ripple(v, ovp_hi) for v in (36.0, LM_REC_VIN, LM_ABS["VIN"])}
    i_l1_max = max([i_boost] + list(i_buck.values()))
    e_l1 = 0.5 * L1_NOM * (1 + L_TOL) * i_l1_max ** 2
    c_min = BULK_N * BULK_C * (1 - BULK_TOL)
    v_steady = math.sqrt(ovp_hi ** 2 + 2 * e_l1 / c_min)
    i_first = i_valley + (LM_ABS["VIN"] - ovp_hi) / (l1_lo * FSW_MIN)
    e_first = 0.5 * L1_NOM * (1 + L_TOL) * i_first ** 2
    v_first = math.sqrt(ovp_hi ** 2 + 2 * e_first / c_min)
    ovp_res = max(v_steady, v_first)
    e_to_29 = (29.0 ** 2 - ovp_hi ** 2) * c_min / 2
    slew = i_first / c_min
    P("3. THE FRONT END'S OUTPUT OVER-VOLTAGE PROTECTION (SNVSAI1D 6.5 p.8; 7.3.11 p.18; 7.1 p.13)")
    P("   threshold at FB: VREF + 10 % TYPICAL (no minimum or maximum given), hysteresis 2.5 %; response: 'turns off the gate")
    P("   drives' (7.3.11) or 'the high-side drivers' (7.1); either stops the input's energy (Q2 off blocks VIN_RAW). OVP reads FB,")
    P("   so it scales with the same divider: the bus trips at 1.10 x its own regulation.")
    P("   trip, nominal                                   %6.3f V" % ovp_nom)
    P("   trip, VREF maximum and the divider's worst ratio %6.3f V   (INFERRED: TI's 10 %% is typical only)" % ovp_hi)
    P("   L1's current in the steady current-limit cycle inside U2's ratings (R12 5 mOhm - 1 %; the CS and CSG pins sit behind")
    P("   R150 and R151, 100 Ohm each, where IOFFSET(CS/CSG) up to 19 uA, p.7, moves the threshold by up to %.1f mV):"
      % (voff * 1e3))
    P("     boost mode, peak limit (140 + %.1f) mV:                                    %6.2f A" % (voff * 1e3, i_boost))
    for v in sorted(i_buck):
        P("     buck mode at %4.1f V in: valley limit (94 + %.1f) mV = %.2f A, plus the ripple at the trip (L1 -20 %%, 175 kHz) %6.2f A"
          % (v, voff * 1e3, i_valley, i_buck[v]))
    P("   so buck mode at U2's 60 V sets the steady cycle's peak: %.2f A; with L1 at +20 %% (12 uH) that is %.2f mJ, which into"
      % (i_l1_max, e_l1 * 1e3))
    P("   the six bulk parts at -20 %% (%.3f mF, ceramics not counted) lifts the bus to %6.3f V." % (c_min * 1e3, v_steady))
    P("   THE FIRST ON-TIME (the re-check's n2). In buck mode the LM5176 limits the VALLEY only: the high side 'skips a cycle if")
    P("   the sensed voltage does not fall below this threshold' (7.3.5 p.16) and, once on, is 'turned off by the oscillator")
    P("   clock signal' (7.3.1 p.14), so the first on-time after a valley crossing can last up to a period. MODEL, a full period")
    P("   at U2's 60 V from the valley limit, L1 at -20 %%, 175 kHz: %.2f A; with 12 uH (unsaturated, where L1's Isat is 17.5 A)"
      % i_first)
    P("   %.2f mJ, and the bus reaches %6.3f V. The bound takes the larger." % (e_first * 1e3, v_first))
    P("   THE BUS'S BOUND: %.2f V, INFERRED (the typical-only 10 %%) with a MODEL energy term. That term weighs little: to put"
      % ovp_res)
    P("   the bus at 29.0 V (Q7's 30 V less Q8's VSD) from the trip, L1 would have to deliver %.0f mJ, %.0f times this figure."
      % (e_to_29 * 1e3, e_to_29 / e_first))
    P("   Response time: TI gives none. None is needed at this scale: at %.2f A into %.3f mF the bus rises at most %.1f V per ms,"
      % (i_first, c_min * 1e3, slew * 1e-3))
    P("   so %.2f ms of full current past the trip would be needed to reach 30 V (%.0f cycles at 175 kHz)."
      % ((FET_VDS - ovp_hi) / slew * 1e3, (FET_VDS - ovp_hi) / slew * FSW_MIN))
    P("   The typical 10 % would have to be wrong by this much before the bus reaches each limit (VREF max, worst ratio, residue):")
    res_dv = ovp_res - ovp_hi
    sens = {}
    for lim, what in ((24.0, "80 % of the FETs' 30 V"), (26.0, "the BQ25731's recommended 26 V and ACOV's minimum"),
                      (FET_VDS - Q8_VSD_MAX, "Q7's 30 V, with Q8's VSD"), (FET_VDS, "Q8's 30 V"),
                      (32.0, "the BQ25731's absolute 32 V")):
        k = (lim - res_dv - dv_bias) / (VREF[2] * r_hi_t) - 1
        sens[lim] = k
        P("     %5.1f V (%s): an OVP %4.1f %% over VREF" % (lim, what, k * 100))
    P("")

    # 4. load dump
    P("4. A LOAD DUMP: THE CHARGER STOPS AT ITS FULL INPUT CURRENT")
    P("   The charger's own inductor L2 does not feed VBUS20 when it stops: with Q7 off its current returns through Q8's body")
    P("   diode, L2 and Q10 (on, or its body diode) to VBAT. The front end sees a load step and answers with its loop (MODEL:")
    P("   crossover %.2f kHz at its slowest corner, |Zout| %.0f mOhm, gen_sch_a.py lines 722 to 724); its CCM stage can sink"
      % (FC_MIN / 1e3, ZOUT_MAX * 1e3))
    P("   current (SNVSAI1D 7.3.8 p.17). Step dI into the bulk at -20 %: dV = dI / (2 pi fc C), plus L1's energy in the steady")
    P("   current-limit cycle (section 3), which overstates what L1 carries at either step (16.2 A at 9 V in, gen_sch_a.py 751):")
    dump = {}
    for di, what in ((I_IN_A2, "Option A(i)'s bound, U3's 6.35 A clamp plus 0.1 A"), (I_IN_DECL, "VBUS20's declared peak")):
        dv_loop = di / (2 * math.pi * FC_MIN * c_min)
        v2 = math.sqrt((v_hi + dv_loop) ** 2 + 2 * e_l1 / c_min)
        dump[di] = v2
        P("   %4.2f A (%s): loop %.3f V, |Zout| %.3f V; with %.2f mJ the peak is %6.3f V"
          % (di, what, dv_loop, di * ZOUT_MAX, e_l1 * 1e3, v2))
    P("   (MODEL; below the OVP trip's %.3f V, so OVP need not act; whatever the model's error, section 3 caps it at %.3f V)"
      % (ovp_hi, ovp_res))
    P("   During the dump the charger has stopped: Q8 holds the bus less SW1, Q7 at most the bus plus Q8's body diode")
    P("   (SLPS516 VSD 1.0 V maximum): %.2f V." % (dump[I_IN_DECL] + Q8_VSD_MAX))
    P("")

    # 5. line
    ov_lo = OVLOTH[0] * (1 + 100 * (1 - TOL_R) / (6.65 * (1 + TOL_R)))
    ov_ty = OVLOTH[1] * (1 + 100 / 6.65)
    ov_hi = OVLOTH[2] * (1 + 100 * (1 + TOL_R) / (6.65 * (1 - TOL_R)))
    P("5. THE FRONT END'S INPUT (what board E delivers into VIN_RAW)")
    P("   service 9 to 36 V (REQ-015); board E's LM5069 opens its pass FET at OVLO %.2f / %.2f / %.2f V (OVLOTH 2.4 / 2.5 / 2.6 V,"
      % (ov_lo, ov_ty, ov_hi))
    P("   SNVS452G 6.5 p.5, over R22 100k and R23 6.65k at 1 %); the panel tracker's TRK_OUT (15.1 V) joins through an ideal")
    P("   diode; four SMCJ40A class clamps (board E D10 SMCJ40CA, D1 and D2, board A D2): VBR 44.4 to 49.1 V, VC 64.5 V at 23.3 A")
    P("   (Littelfuse, page 2 of 6). U2 regulates VBUS20 for any VIN from 4.2 to 55 V (SNVSAI1D 6.3 p.5); a line step reaches")
    P("   the bus only through the loop. MODEL, valley current mode (7.3.1) at L1 -20 %, fSW 175 kHz: the ripple rises from")
    r36, r60 = ripple(36.0, v_hi), ripple(LM_ABS["VIN"], v_hi)
    dv_line = (r60 - r36) / 2 / (2 * math.pi * FC_MIN * c_min)
    P("   %.2f A at 36 V to %.2f A at U2's 60 V, the average by %.2f A until the loop answers: %.3f V on the bus (%.3f V)."
      % (r36, r60, (r60 - r36) / 2, dv_line, v_hi + dv_line))
    P("   With U2 idle Q2 blocks VIN_RAW (section 1). Above 55 V U2 leaves its recommended range and above 60 V its absolute")
    P("   ratings (VIN, VISNS, VOSNS 60 V, p.5): the clamps' 64.5 V is S-111's item; this bound assumes U2 inside its ratings.")
    P("")

    # 6. clamps
    P("6. CLAMPS")
    P("   on VBUS20: none (section 1, the whole membership read). Upstream: the four SMCJ40A class parts of section 5. On VBAT:")
    P("   D1 SMCJ18A (VR 18 V, VBR 20.00 to 22.10 V, VC 29.2 V at 51.4 A).")
    P("")

    # 7. pack side
    vbat_reg = VBAT_REG * (1 + VBAT_REG_ACC)
    vbat_ovp = VBAT_REG * BATOVP_MAX
    vr, vbr_lo, vbr_hi, vc, ipp = SMCJ["SMCJ18A"]
    d1_at = lambda i: vbr_hi + (vc - vbr_hi) * i / ipp
    e_l2 = 0.5 * L2_NOM * (1 + L_TOL) * IL2_PK["A2"] ** 2
    P("7. THE PACK SIDE (Q10's drain and SW2: SW2 sits at VBAT in buck mode, Table 9-3 p.27; Q9's drain is SW2)")
    P("   ChargeVoltage 16.8 V + 0.5 %% = %.3f V (SLUSE66A 8.5 p.9); BATOVP at most 105 %% = %.2f V (p.14); SYSOVP (4S, the strap of"
      % (vbat_reg, vbat_ovp))
    P("   section 1) %.1f / %.1f / %.1f V turns the converter off (p.14). A pack that opens while charging at A2's %.2f A: SYSOVP"
      % (SYSOVP_4S[0], SYSOVP_4S[1], SYSOVP_4S[2], IL2_PK["A2"]))
    P("   stops the converter at %.1f V and L2's %.2f mJ goes into VBAT's own capacitance (its effective value under bias is not"
      % (SYSOVP_4S[2], e_l2 * 1e3))
    P("   held: INCONCLUSIVE); D1 bounds it: %.2f V at %.2f A (INFERRED, the straight line from VBR max at 1 mA to VC at IPP),"
      % (d1_at(IL2_PK["A2"]), IL2_PK["A2"]))
    P("   %.1f V at its IPP." % vc)
    P("")

    # 8. the answer for the bus
    FIG.update(v_lo=v_lo, v_hi=v_hi, ovp_hi=ovp_hi, bound=ovp_res, dump=dump[I_IN_DECL], dump_a2=dump[I_IN_A2],
               line=v_hi + dv_line, d1_a2=d1_at(IL2_PK["A2"]), vbat_ovp=vbat_ovp, sysovp=SYSOVP_4S[2], ov_lo=ov_lo, ov_hi=ov_hi,
               i_l1_max=i_l1_max, sens30=sens[FET_VDS], sens29=sens[FET_VDS - Q8_VSD_MAX], vsd=Q8_VSD_MAX,
               v_steady=v_steady, i_first=i_first, v_first=v_first, e_to_29=e_to_29, e_first=e_first)
    P("8. THE BUS'S WORST CASE")
    P("   DC                        %6.3f V   (section 2)" % v_hi)
    P("   load dump, MODEL          %6.3f V   (section 4, the declared 8.0 A)" % dump[I_IN_DECL])
    P("   line step to 60 V, MODEL  %6.3f V   (section 5)" % (v_hi + dv_line))
    P("   BOUND, INFERRED           %6.3f V   (section 3: the typical-only OVP at VREF max and the worst ratio, plus L1's energy"
      % ovp_res)
    P("                                         at a first on-time of a period, MODEL; %.3f V in the steady current-limit cycle;"
      % v_steady)
    P("                                         30 V is reached only at an OVP %.1f %% over VREF for Q8, %.1f %% for Q7)"
      % (sens[FET_VDS] * 100, sens[FET_VDS - Q8_VSD_MAX] * 100))
    P("")

    # 9. margins
    P("9. THE MARGINS PER PART (limit minus the figure; the switch nodes' ringing comes on top, section 10)")
    bus3 = [v_hi, dump[I_IN_DECL], ovp_res]
    rows = [
        ("Q8 VDS = SW1 (30 V, SLPS516 p.1)", FET_VDS, bus3),
        ("Q7 VDS = bus + Q8's VSD 1.0 V (30 V, SLPS526 p.1)", FET_VDS, [x + Q8_VSD_MAX for x in bus3]),
        ("U3 VBUS pin 1 (32 V absolute, p.8)", BQ_ABS["VBUS, ACP, ACN"], bus3),
        ("U3 VBUS, ACP, ACN (26 V recommended, p.8)", BQ_REC["VBUS, ACP, ACN"], bus3),
        ("U3 ACOV rising minimum (26.0 V, p.14)", ACOV[0], bus3),
        ("U3 ACP, ACN absolute (32 V), before ringing", BQ_ABS["VBUS, ACP, ACN"], bus3),
        ("U3 SW1 absolute (32 V, p.8), before ringing", BQ_ABS["SW1, SW2"], bus3),
        ("U3 SW1 recommended (26 V, p.8), before ringing", BQ_REC["SW1, SW2"], bus3),
        ("U3 BTST1 absolute (38 V; SW1 + REGN 6.3 V)", BQ_ABS["BTST1, BTST2, HIDRV1, HIDRV2"], [x + VREGN[2] for x in bus3]),
        ("U3 BTST1 recommended (32 V; SW1 + REGN 6.3 V)", BQ_REC["BTST1, BTST2, HIDRV1, HIDRV2"], [x + VREGN[2] for x in bus3]),
    ]
    P("   %-50s %9s %9s %9s" % ("limit", "DC", "dump", "bound"))
    P("   %-50s %9s %9s %9s" % ("", "", "MODEL", "INFERRED"))
    marg = {}
    for name, lim, figs in rows:
        marg[name] = [lim - f for f in figs]
        P("   %-50s %8.2f  %8.2f  %8.2f" % (name, lim - figs[0], lim - figs[1], lim - figs[2]))
    d1v = d1_at(IL2_PK["A2"])
    P("   pack side (VBAT; SW2 at VBAT in buck mode), against the charger's cutoff SYSOVP %.1f V and D1 at A2's current %.2f V:"
      % (SYSOVP_4S[2], d1v))
    P("     Q9 VDS = SW2, Q10 VDS (30 V)                      %.2f V at BATOVP, %.2f at SYSOVP, %.2f at D1, %.2f at D1's IPP"
      % (FET_VDS - vbat_ovp, FET_VDS - SYSOVP_4S[2], FET_VDS - d1v, FET_VDS - vc))
    P("     U3 SW2 (32 V absolute / 26 V recommended), before ringing   %.2f / %.2f at SYSOVP, %.2f / %.2f at D1"
      % (BQ_ABS["SW1, SW2"] - SYSOVP_4S[2], BQ_REC["SW1, SW2"] - SYSOVP_4S[2], BQ_ABS["SW1, SW2"] - d1v, BQ_REC["SW1, SW2"] - d1v))
    P("     U3 VSYS, SRP, SRN (32 V absolute / 23.15 V recommended)     %.2f / %.2f at SYSOVP, %.2f / %.2f at D1"
      % (BQ_ABS["SRN, SRP, VSYS"] - SYSOVP_4S[2], BQ_REC["SRN, SRP, VSYS"] - SYSOVP_4S[2],
         BQ_ABS["SRN, SRP, VSYS"] - d1v, BQ_REC["SRN, SRP, VSYS"] - d1v))
    P("     U3 BTST2 (SW2 + REGN 6.3 V; 38 V absolute / 32 V recommended) %.2f / %.2f at SYSOVP, %.2f / %.2f at D1"
      % (38.0 - SYSOVP_4S[2] - VREGN[2], 32.0 - SYSOVP_4S[2] - VREGN[2], 38.0 - d1v - VREGN[2], 32.0 - d1v - VREGN[2]))
    P("   BTST to SW is REGN's own %.1f V at most against %.1f V absolute and %.1f V recommended, whatever the bus does."
      % (VREGN[2], BQ_ABS_BTST_SW, BQ_REC_BTST_SW))
    FIG.update(q8_m=marg[rows[0][0]], q7_m=marg[rows[1][0]], vbus_abs_m=marg[rows[2][0]], rec26_m=marg[rows[3][0]],
               btst_abs_m=marg[rows[8][0]], btst_rec_m=marg[rows[9][0]], sw2_abs_d1=BQ_ABS["SW1, SW2"] - d1v,
               q9_d1=FET_VDS - d1v)
    P("")

    # 10. switch node
    P("10. THE SWITCH NODES: A BUDGET, NOT A BOUND (INCONCLUSIVE at desk)")
    P("   No layout exists (S-115) and no TI application note giving a layout-independent ringing bound is held. What TI does")
    P("   state: '30 V or higher voltage rating MOSFETs are preferred for 19-V to 20-V input voltage' (SLUSE66A 10.2.2.6 p.86),")
    P("   in a topology whose input loop runs through RAC with at most 10 nF + 1 nF after it (p.86, Figure 10-3 p.85), as board A")
    P("   draws it. Board A's DC band tops out %.2f V above TI's 20 V. Board A draws R146 and R147 at 10 Ohm with C121 10 nF"
      % (v_hi - 20.0))
    P("   (Figure 10-3: 4.99 Ohm, CDIFF 10 nF, and CACP and CACN 33 nF to ground, p.85); without CACN, U3's ACN pin sees CH_ACN's")
    P("   ring through R146 and C121 alone. U3's VBUS pin 1 sits on VBUS20 itself.")
    b = {"Q7": (FET_VDS - v_hi - Q8_VSD_MAX, FET_VDS - ovp_res - Q8_VSD_MAX), "Q8": (FET_VDS - v_hi, FET_VDS - ovp_res),
         "SWneg": (-BQ_ABS_SW_NEG[1] - Q8_VSD_MAX, -BQ_ABS_SW_NEG[0] - Q8_VSD_MAX),
         "SW1a": (BQ_ABS["SW1, SW2"] - v_hi, BQ_ABS["SW1, SW2"] - ovp_res), "SW1r": (BQ_REC["SW1, SW2"] - v_hi, BQ_REC["SW1, SW2"] - ovp_res)}
    P("   Budget left for ringing over the steady bus (%.2f V) and over the bound (%.2f V, INFERRED):" % (v_hi, ovp_res))
    for name, key in (("Q7 VDS: the bus, Q8's VSD 1.0 V in every dead time, and SW1's ring below it; 30 V", "Q7"),
                      ("Q8 VDS: SW1's overshoot over the bus; 30 V", "Q8"),
                      ("U3 SW1 absolute 32 V", "SW1a"), ("U3 SW1 recommended 26 V", "SW1r")):
        P("     %-78s %5.2f / %5.2f V" % (name, b[key][0], b[key][1]))
    P("     U3 SW1 and SW2 below PGND: %.0f V, and %.0f V for at most 25 ns (p.8). In every dead time SW1 sits at minus Q8's VSD"
      % BQ_ABS_SW_NEG)
    P("     (1.0 V maximum), inside -2 V; the ring below that has %.1f V to -4 V, for at most 25 ns" % b["SWneg"][0])
    ioff = Q7_VPLT / (RDS_HI_OFF_TYP + Q7["rg"])
    ion = (VREGN[1] - Q7_VPLT) / (RDS_HI_ON_TYP + Q7["rg"])
    t_fi = (Q7["qgs"] - Q7["qgth"]) / ioff
    t_ri = (Q7["qgs"] - Q7["qgth"]) / ion
    P("   MODEL for the layout writer (not a bound; typical driver figures, the plateau INFERRED):")
    P("   Q7's TURN-OFF (sets Q7's VDS and SW1's undershoot): its current falls in (Qgs - Qg(th)) / (VPLT / (RDS_HI_OFF + RG)) =")
    P("   %.1f nC / (%.1f V / (%.1f + %.1f Ohm)) = %.2f ns (SLPS526 p.3; SLUSE66A p.16); each nH of the loop C190 and C191, Q7,"
      % ((Q7["qgs"] - Q7["qgth"]) * 1e9, Q7_VPLT, RDS_HI_OFF_TYP, Q7["rg"], t_fi * 1e9))
    P("   Q8 adds L x di/dt, each nH between Q8's source and U3's PGND takes SW1 that much further below minus VSD, and the")
    P("   inductance between the VBUS20 bank and C190 / C191 lifts CH_ACN by I x sqrt(L / 11 nF), which grows as the square root")
    P("   of L (the figure below is at 1 nH):")
    FIG.update(t_fi=t_fi, t_ri=t_ri, b_q7=b["Q7"], b_q8=b["Q8"], b_sw1r=b["SW1r"], b_swneg=b["SWneg"])
    for pt in ("A2", "G1", "A1"):
        i = IL2_PK[pt]
        didt = i / t_fi * 1e-9
        FIG["ring_" + pt] = dict(i=i, vpn=didt, vacn=i * math.sqrt(1e-9 / 11e-9), l30=b["Q7"][0] / didt,
                                 lneg=b["SWneg"][0] / didt)
        P("     %s, L2 peak %5.2f A: %5.2f A/ns, %4.2f V per nH and %4.2f V at 1 nH before C190; Q7's 30 V budget allows %.2f nH;"
          % (pt, i, didt, didt, i * math.sqrt(1e-9 / 11e-9), b["Q7"][0] / didt))
        P("         SW1's undershoot to -4 V (25 ns) allows %.2f nH between Q8's source and U3's PGND" % (b["SWneg"][0] / didt))
    P("   Q7's TURN-ON (sets Q8's VDS): the current rises in %.1f nC / ((%.1f - %.1f) V / (%.1f + %.1f Ohm)) = %.2f ns (the 6 Ohm"
      % ((Q7["qgs"] - Q7["qgth"]) * 1e9, VREGN[1], Q7_VPLT, RDS_HI_ON_TYP, Q7["rg"], t_ri * 1e9))
    P("   turn-on driver, RDS_HI_ON_Q1, p.16), from the valley current; each nH adds L x di/dt:")
    for pt in ("A2", "G1", "A1"):
        iv = IL2_PK[pt] - IL2_DI[pt]
        didt = iv / t_ri * 1e-9
        FIG["ring_" + pt].update(l26=b["SW1r"][0] / didt, l8=b["Q8"][0] / didt, valley=iv, didt_on=didt)
        P("     %s, valley %5.2f A: %4.2f A/ns, %4.2f V per nH; Q8's 30 V budget allows %.2f nH and U3 SW1's recommended 26 V"
          % (pt, iv, didt, didt, b["Q8"][0] / didt))
        P("         %.2f nH, both before the recovery below" % (b["SW1r"][0] / didt))
    P("   and Q8's body diode recovers into that edge: Qrr 8.2 nC is stated at %s (SLPS516 p.3), about ten times"
      % Q8["qrr_test"])
    P("   slower than this edge, and no figure at this di/dt is given: the recovery ring is INCONCLUSIVE, a bench reading.")
    P("   Avalanche, if a ring does pass 30 V: EAS 23 mJ (CSD17578Q5A) and 39 mJ (CSD17577Q5A), single pulse, p.1; a repetitive")
    P("   rating is not stated, so no margin is taken from it.")
    P("")

    # 11. single faults
    vd = VSD_TYP
    P("11. SINGLE FAULTS OUTSIDE EVERY REQUIREMENT (ASM-001 refuses 'no single point of failure'; SC-39)")
    P("   With the charger stopped Q7 and Q8 are off, L2 carries DC, and Q10's body diode (source CH_SW2, drain VBAT) holds SW2,")
    P("   and SW1 through L2, near VBAT plus a diode: Q7 then holds VBUS20 less VBAT less VSD, Q8 about VBAT plus VSD (INFERRED).")
    P("   Q2 shorted: VBUS20 = VIN_RAW less Q5's body diode (about %.1f V, INFERRED), %.1f V at 36 V in and %.1f V at board E's"
      % (vd, 36.0 - vd, ov_hi - vd))
    P("   OVLO maximum. On the way the bus passes ACOV's 26.0 to 27.7 V while the charger still switches (the 100 us deglitch,")
    P("   SLUSE66A p.14), and Q7 then holds the bus plus Q8's VSD, %.1f V or more before any ringing: no order is claimed for"
      % (ACOV[2] + Q8_VSD_MAX))
    P("   that phase. Once ACOV has stopped the charger, U3's VBUS, ACP and ACN pass their 32 V absolute rating above %.1f V in,"
      % (BQ_ABS["VBUS, ACP, ACN"] + vd))
    P("   while Q7 reaches 30 V only at VBUS20 = 30 V + VBAT + VSD (%.1f V with the pack at its %.1f V CUV): from then on U3 is"
      % (FET_VDS + VBAT_CUV + vd, VBAT_CUV))
    P("   the first part past its rating while the pack is above about %.1f V." % (32.0 - FET_VDS - vd))
    P("   R6 open or FB shorted: the OVP reads the same pin, so nothing on board A bounds the bus. The charger switches until")
    P("   ACOV trips (up to %.1f V, after its 100 us deglitch), so Q7 holds at least %.1f V (the trip plus Q8's VSD) while it still"
      % (ACOV[2], ACOV[2] + Q8_VSD_MAX))
    P("   switches, before any rise inside the deglitch and before any ringing: the FETs may be first, and no order is claimed.")
    P("   Beyond, the 35 V bulk parts and U3's 32 V are passed.")
    P("   Not taken, for the power review S-111 names: an independent over-voltage trip on VBUS20 (a second divider into U34's")
    ipk_hs = 6.15
    vr22, vbl22, vbh22, vc22, ipp22 = SMCJ["SMCJ22A"]
    P("   channel 1, re-armed while the stage runs) would bound the FB faults; an SMCJ22A on VBUS20 (VR 22 V over the %.2f V"
      % v_hi)
    P("   DC band) would hold a Q2 short at about %.1f V at board E's %.2f A hot-swap limit (INFERRED straight line) until the"
      % (vbh22 + (vc22 - vbh22) * ipk_hs / ipp22, ipk_hs))
    P("   LM5069's fault timer opens, and clamps %.1f V at its own IPP, over 30 V." % vc22)
    P("")

    # 12. answer
    P("12. THE ANSWER: (a), the bound holds in service (INFERRED: it rests on a typical-only threshold)")
    P("   VBUS20 stays at or under %.2f V by the front end's own protection whatever the load, the line or the loop model does"
      % ovp_res)
    P("   while U2 is inside its ratings: Q8 %.2f V and Q7 %.2f V under their 30 V (Q7 carries Q8's VSD), U3's VBUS %.2f V under"
      % (FET_VDS - ovp_res, FET_VDS - ovp_res - Q8_VSD_MAX, BQ_ABS["VBUS, ACP, ACN"] - ovp_res))
    P("   its 32 V; at the INFERRED bound U3's ACOV (26.0 V minimum) is not reached. 30 V is reached only if the trip sat %.1f %%"
      % (sens[FET_VDS - Q8_VSD_MAX] * 100))
    P("   over VREF (Q7) or %.1f %% (Q8), against TI's typical 10 %%; a bench reading of the trip replaces the INFERRED figure."
      % (sens[FET_VDS] * 100))
    P("   The pack side stays at or under %.1f V by SYSOVP and %.2f V by D1 in a pack that opens while charging." % (SYSOVP_4S[2], d1v))
    P("   The switch nodes are INCONCLUSIVE: ringing is a bench item with %.2f V (Q7) and %.2f V (Q8) of budget over the steady"
      % (b["Q7"][0], b["Q8"][0]))
    P("   bus, and SW1's undershoot has %.1f V to U3's -4 V (25 ns), carried as its own open item." % b["SWneg"][0])
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
