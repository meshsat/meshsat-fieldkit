#!/usr/bin/env python3
"""S-120: board A's charge bus VBUS20 and the charger's switch nodes against the 30 V FETs of decision 57 (stream s120,
MESHSAT-1357, 29 September 2026). Desk arithmetic on the makers' figures and the committed netlists: nothing is built,
powered or measured, and nothing here is a qualified review (AI engineering work).

WHAT IT DOES. It PARSES board A's and board E's committed netlists (v2/ecad/tools/netlist_sexp.py; nothing is grepped) and
asserts every circuit fact the bound rests on (section 1): the front end U2's feedback divider, its output node and bank,
its sense resistors, its inductor and the direction of its FETs; the charger U3's pins, its four FETs and their nets; the
clamps on VIN_RAW and VBAT and the ABSENCE of any clamp on VBUS20; board E's over-voltage lockout divider and its clamps.
A fact that does not hold is printed FAIL and the exit status is 1. Then it computes the bus's worst case mechanism by
mechanism (sections 2 to 8) from the makers' figures, each quoted with its document, revision and printed page, and the
margins to the FETs' 30 V and the BQ25731's own limits (section 9); section 10 is the switch node's budget, section 11 the
single faults outside every requirement, section 12 the answer.

LABELS. A figure the maker states is quoted. INFERRED marks a figure the maker does not state (a curve reading, a model,
a tolerance the maker leaves out); MODEL marks an estimate from a simplified circuit model that is not a bound. A bound is
named a bound.

Usage: python3 vbus20_bound.py [--net-a PATH] [--net-e PATH] > vbus20_bound.out   (deterministic; the committed .out is this
       script's output on the committed netlists). Exit 0 every fact holds, 1 a fact fails, 3 a netlist cannot be read."""
import argparse
import hashlib
import math
import os
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
OVP_HYST = 0.025                      # 6.5 p.8, hysteresis 2.5 %
VCS_BOOST_MAX = 0.140                 # 6.5 p.7, boost current limit (peak) 100 / 120 / 140 mV, HTSSOP-28
VCS_BUCK_MAX = 0.094                  # 6.5 p.7, buck current limit (valley) 66 / 80 / 94 mV, HTSSOP-28
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
VREGN_MAX = 6.3                       # 8.5 p.11, VREGN_REG 5.7 / 6.0 / 6.3 V
RDS_HI_ON_TYP, RDS_HI_OFF_TYP = 6.0, 1.3   # 8.5 p.16, the high-side gate driver loop (typical; the ON figure has no max)

# TI SLPS526 (CSD17578Q5A, March 2015) and SLPS516 (CSD17577Q5A, August 2014): held back by TI's terms, pinned by sha256 in
# v2/vendor/sources.txt, fetched by v2/docs/records/s117/fetch_held_back.py into v2/vendor/ti/held/ (ignored).
FET_VDS = 30.0                        # p.1 Absolute Maximum Ratings VDS 30 V; 5.1 p.3 BVDSS 30 V minimum at 250 uA
Q7 = dict(part="CSD17578Q5A", qgs=3.1e-9, qgth=1.7e-9, rg=1.8, coss=(136e-12, 177e-12), eas="23 mJ (ID 22 A, L 0.1 mH)")
Q8 = dict(part="CSD17577Q5A", qgs=5.1e-9, qgth=2.5e-9, rg=1.4, coss=(208e-12, 270e-12), eas="39 mJ (ID 28 A, L 0.1 mH)")
Q7_VPLT = 2.7                         # INFERRED: the plateau read from SLPS526 Figure 4 p.5 at 10 A (s117 efficiency.py)

# Littelfuse SMCJ series (revised 11/20/15), v2/vendor/power/littelfuse-smcj-series-tvs.pdf, the table on page 2 of 6:
# (standoff VR, VBR min, VBR max at IT 1 mA, VC max at IPP, IPP)
SMCJ = {"SMCJ18A": (18.0, 20.00, 22.10, 29.2, 51.4), "SMCJ22A": (22.0, 24.40, 26.90, 35.5, 42.3),
        "SMCJ40A": (40.0, 44.40, 49.10, 64.5, 23.3)}

# TI SNVS452G (LM5069), v2/vendor/ti/ti-lm5069.pdf, 6.5 p.5: OVLOTH 2.4 / 2.5 / 2.6 V.
OVLOTH = (2.4, 2.5, 2.6)

# Parts and the project's own records.
TOL_R = 0.01                          # the divider's printed 1 %
TCR_DRIFT = 100e-6 * 65               # INFERRED: 100 ppm/K over 65 K, the convention S-116 uses for the same class of part
L1_NOM, L_TOL = 10e-6, 0.20           # Coilcraft XAL1010 (v2/vendor/power/coilcraft-xal1010.pdf): +-20 %
L2_NOM = 4.7e-6
BULK_C, BULK_N, BULK_TOL = 330e-6, 6, 0.20   # Panasonic ZK (v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf): +-20 %
FC_MIN, ZOUT_MAX = 710.0, 0.089       # MODEL: gen_sch_a.py lines 722 to 724 (loop_verify.py FE 6 V331 15 21: crossover
                                      # 0.71 to 3.6 kHz, |Zout| 89 mOhm), the front end's own loop model, not a maker figure
I_IN_A2, I_IN_DECL = 6.45, 8.0        # s117 charger_l_f.out A2 (U3's 6.35 A clamp plus 0.1 A); VBUS20's declared peak
                                      # (gen_sch_a.py line 109)
IL1_AT_MAX_DRAW = 16.2                # gen_sch_a.py line 751: L1 16.2 A peak at 9 V in and 6.45 A
IL2_PK = {"A2": 15.71, "G1": 14.10, "A1": 10.70}   # s117 charger_l_f.out section 2, XAL1010-472ME, worst peak
VIN_SERVICE = (9.0, 36.0)             # REQ-015; v2/docs/OPERATING-ENVELOPE.md section 4

FIG = {}                              # main() leaves its figures here for apply_registry_s120.py (read, never re-typed)


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def val(doc, ref):
    return doc["components"][ref]["value"]


def pins(doc, ref):
    return {p: v["net"] for p, v in doc["pins"].get(ref, {}).items()}


def members(doc, net):
    return sorted({r for r, *_ in doc["nets"].get(net, [])})


def facts(a, e):
    """Every circuit fact the bound rests on, read from the parsed netlists: (name, holds, detail)."""
    out = []

    def add(name, ok, detail):
        out.append((name, bool(ok), detail))

    add("U2 FB divider", pins(a, "R6") in ({"1": "VBUS20", "2": "FE_FB"}, {"1": "FE_FB", "2": "VBUS20"})
        and val(a, "R6") == "240k 1%" and sorted(pins(a, "R7").values()) == ["FE_FB", "GND"] and val(a, "R7") == "10k 1%",
        "R6 %s VBUS20 to FE_FB, R7 %s FE_FB to GND" % (val(a, "R6"), val(a, "R7")))
    add("U2 pins", pins(a, "U2").get("11") == "FE_FB" and pins(a, "U2").get("12") == "VBUS20"
        and pins(a, "U2").get("24") == "VBUS20" and pins(a, "U2").get("2") == "FE_VINP" and pins(a, "U2").get("3") == "FE_VISNS",
        "FB pin 11 on FE_FB, VOSNS pin 12 and BIAS pin 24 on VBUS20, VIN pin 2 on FE_VINP, VISNS pin 3 on FE_VISNS")
    add("U2 MODE", sorted(pins(a, "R119").values()) == ["FE_MODE", "FE_VCC"],
        "R119 %s from MODE to VCC: CCM, hiccup disabled (SNVSAI1D 7.4.2 p.20)" % val(a, "R119"))
    add("front end sense", sorted(pins(a, "R11").values()) == ["FE_OUT", "VBUS20"] and val(a, "R11").startswith("10mOhm 1%")
        and sorted(pins(a, "R12").values()) == ["FE_CS", "GND"] and val(a, "R12").startswith("5mOhm 1%"),
        "R11 %s FE_OUT to VBUS20 (ISNS), R12 %s FE_CS to GND (CS)" % (val(a, "R11"), val(a, "R12")))
    add("L1", sorted(pins(a, "L1").values()) == ["FE_SW1", "FE_SW2"] and val(a, "L1").startswith("10uH XAL1010-103ME"),
        "L1 %s between FE_SW1 and FE_SW2" % val(a, "L1"))
    q2, q5 = pins(a, "Q2"), pins(a, "Q5")
    add("Q2 and Q5 direction", q2.get("5") == "VIN_RAW" and {q2.get(k) for k in "123"} == {"FE_SW1"}
        and q5.get("5") == "FE_OUT" and {q5.get(k) for k in "123"} == {"FE_SW2"},
        "Q2 drain VIN_RAW, source FE_SW1 (its body diode points from FE_SW1 to VIN_RAW, so an idle stage blocks VIN_RAW); "
        "Q5 drain FE_OUT, source FE_SW2; both %s" % val(a, "Q2").split(" (")[0])
    vb = members(a, "VBUS20")
    bulk = [r for r in vb if "EEHZK1V331P" in val(a, r)]
    cer = [r for r in vb if val(a, r).startswith("10u 50V X7R")]
    diodes = [r for r in vb if r.startswith("D") or a["components"][r]["libpart"].startswith("D")]
    add("VBUS20 bank", len(bulk) == BULK_N and len(cer) == 18, "%d x %s and %d x 10 uF 50 V X7R 1210 on VBUS20"
        % (len(bulk), val(a, bulk[0]).split(" (")[0] if bulk else "?", len(cer)))
    add("no clamp on VBUS20", not diodes, "diodes on VBUS20: %s" % (", ".join(diodes) or "none"))
    u3 = pins(a, "U3")
    add("U3 pins", u3.get("1") == "VBUS20" and u3.get("5") == "GND" and u3.get("22") == "VBAT" and u3.get("32") == "CH_SW1"
        and u3.get("23") == "CH_SW2" and u3.get("30") == "CH_BTST1" and u3.get("25") == "CH_BTST2",
        "VBUS pin 1 on VBUS20; OTG/VAP/FRS pin 5 on GND (OTG, VAP and FRS need it pulled high, SLUSE66A pin table p.6, so "
        "the charger cannot drive VBUS20); VSYS pin 22 on VBAT; SW1 32, SW2 23, BTST1 30, BTST2 25 on the CH_ nets")
    want = {"Q7": ("CSD17578Q5A", "CH_ACN", "CH_SW1"), "Q8": ("CSD17577Q5A", "CH_SW1", "GND"),
            "Q9": ("CSD17577Q5A", "CH_SW2", "GND"), "Q10": ("CSD17577Q5A", "VBAT", "CH_SW2")}
    for q, (part, d, s) in sorted(want.items()):
        p = pins(a, q)
        add(q, val(a, q).startswith(part) and p.get("5") == d and {p.get(k) for k in "123"} == {s},
            "%s drain %s, source %s" % (val(a, q), p.get("5"), p.get("1")))
    add("R16 and CH_ACN", sorted(pins(a, "R16").values()) == ["CH_ACN", "VBUS20"]
        and sorted((r, val(a, r)) for r in members(a, "CH_ACN") if r.startswith("C")) == [("C190", "10n"), ("C191", "1n")],
        "R16 %s VBUS20 to CH_ACN; on CH_ACN only C190 10n and C191 1n (SLUSE66A p.86: at most 10 nF + 1 nF after RAC)"
        % val(a, "R16"))
    add("D1 on VBAT", pins(a, "D1") == {"1": "VBAT", "2": "GND"} and val(a, "D1").startswith("SMCJ18A"),
        "D1 %s, cathode on VBAT" % val(a, "D1"))
    add("D2 on VIN_RAW", pins(a, "D2") == {"1": "VIN_RAW", "2": "GND"} and val(a, "D2").startswith("SMCJ40A"),
        "D2 %s, cathode on VIN_RAW" % val(a, "D2").split(" (")[0])
    add("board E OVLO", sorted(pins(e, "R22").values()) == ["DC_P", "HS_OVLO"] and val(e, "R22") == "100k 1%"
        and sorted(pins(e, "R23").values()) == ["GND_V", "HS_OVLO"] and val(e, "R23").startswith("6.65k 1%")
        and pins(e, "U6").get("4") == "HS_OVLO",
        "U6 %s OVLO pin 4 from DC_P over R22 %s and R23 %s" % (val(e, "U6").split(":")[0], val(e, "R22"), val(e, "R23").split(" (")[0]))
    add("board E clamps", val(e, "D1").startswith("SMCJ40A") and pins(e, "D1").get("1") == "DC_P"
        and val(e, "D2").startswith("SMCJ40A") and pins(e, "D2").get("1") == "VIN_RAW"
        and val(e, "D10").startswith("SMCJ40CA") and pins(e, "D10").get("1") == "DC_F",
        "D10 SMCJ40CA on DC_F, D1 SMCJ40A on DC_P, D2 SMCJ40A on VIN_RAW")
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
    P = print
    P("S-120: board A's charge bus VBUS20 and the charger's switch nodes against the 30 V FETs of decision 57. MESHSAT-1357,")
    P("stream s120. Desk arithmetic on the makers' figures and the committed netlists; nothing is built, powered or measured.")
    P("INFERRED = a figure the maker does not state; MODEL = an estimate from a simplified circuit, not a bound.")
    P("netlist A %s sha256/16 %s" % (NET_A, sha16(ar.net_a)))
    P("netlist E %s sha256/16 %s" % (NET_E, sha16(ar.net_e)))
    P("")
    P("1. THE CIRCUIT AS GENERATED (parsed from the netlists)")
    fs = facts(a, e)
    for name, ok, detail in fs:
        P("   %-4s %-20s %s" % ("PASS" if ok else "FAIL", name, detail))
    nbad = sum(1 for _, ok, _ in fs if not ok)
    FIG.update(sha_a=sha16(ar.net_a), sha_e=sha16(ar.net_e), facts=len(fs), facts_bad=nbad)
    P("   facts: %d of %d hold" % (len(fs) - nbad, len(fs)))
    P("")

    # 2. regulation
    rtop, rbot = 240e3, 10e3
    ratio = lambda up, dn: 1 + rtop * (1 + up) / (rbot * (1 - dn))
    r_nom = ratio(0, 0)
    r_hi_i, r_lo_i = ratio(TOL_R, TOL_R), 1 + rtop * (1 - TOL_R) / (rbot * (1 + TOL_R))
    r_hi_t = ratio(TOL_R + TCR_DRIFT, TOL_R + TCR_DRIFT)
    r_lo_t = 1 + rtop * (1 - TOL_R - TCR_DRIFT) / (rbot * (1 + TOL_R + TCR_DRIFT))
    dv_bias = IBIAS_FB * rtop * (1 + TOL_R + TCR_DRIFT)
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

    # 3. OVP
    ovp_nom = VREF[1] * (1 + OVP_TYP) * r_nom
    ovp_hi = VREF[2] * (1 + OVP_TYP) * r_hi_t + dv_bias
    i_l1_max = VCS_BOOST_MAX / (0.005 * (1 - TOL_R))
    e_l1 = 0.5 * L1_NOM * (1 + L_TOL) * i_l1_max ** 2
    c_min = BULK_N * BULK_C * (1 - BULK_TOL)
    ovp_res = math.sqrt(ovp_hi ** 2 + 2 * e_l1 / c_min)
    P("3. THE FRONT END'S OUTPUT OVER-VOLTAGE PROTECTION (SNVSAI1D 6.5 p.8; 7.3.11 p.18; 7.1 p.13)")
    P("   threshold at FB: VREF + 10 % TYPICAL (no minimum or maximum given), hysteresis 2.5 %; response: 'turns off the gate")
    P("   drives' (7.3.11) or 'the high-side drivers' (7.1); either stops the input's energy (Q2 off blocks VIN_RAW). OVP reads FB,")
    P("   so it scales with the same divider: the bus trips at 1.10 x its own regulation.")
    P("   trip, nominal                                   %6.3f V" % ovp_nom)
    P("   trip, VREF maximum and the divider's worst ratio %6.3f V   (INFERRED: TI's 10 %% is typical only)" % ovp_hi)
    P("   L1's energy after the trip: the boost peak limit %.0f mV / (5 mOhm - 1 %%) = %.2f A (p.7), L1 +20 %% = %.0f uH:"
      % (VCS_BOOST_MAX * 1e3, i_l1_max, L1_NOM * 1.2e6))
    P("   %.2f mJ into the six bulk parts at -20 %% (%.3f mF, ceramics not counted) lifts the bus to %6.3f V   <- the bound"
      % (e_l1 * 1e3, c_min * 1e3, ovp_res))
    P("   (L1 saturates at 17.5 A, so 0.5 L I^2 at 28 A overstates the energy: the bound is high by it)")
    P("   the typical 10 % would have to be wrong by this much before the bus reaches each limit (VREF max, worst ratio, residue):")
    res_dv = ovp_res - ovp_hi
    for lim, what in ((24.0, "80 % of the FETs' 30 V"), (26.0, "the BQ25731's recommended 26 V and ACOV's minimum"),
                      (30.0, "the FETs' 30 V"), (32.0, "the BQ25731's absolute 32 V")):
        k = (lim - res_dv - dv_bias) / (VREF[2] * r_hi_t) - 1
        P("     %5.1f V (%s): an OVP %4.1f %% over VREF" % (lim, what, k * 100))
    P("")

    # 4. load dump
    P("4. A LOAD DUMP: THE CHARGER STOPS AT ITS FULL INPUT CURRENT")
    P("   The charger's own inductor L2 does not feed VBUS20 when it stops: with Q7 off its current returns through Q8 to VBAT")
    P("   (Q10's body diode points to VBAT). The front end sees a load step and answers with its loop (MODEL: crossover")
    P("   %.2f kHz at its slowest corner, |Zout| %.0f mOhm, gen_sch_a.py lines 722 to 724); its CCM stage can sink current"
      % (FC_MIN / 1e3, ZOUT_MAX * 1e3))
    P("   (SNVSAI1D 7.3.8). Step dI into the bulk at -20 %: dV = dI / (2 pi fc C), plus L1's stored energy:")
    e_l1d = 0.5 * L1_NOM * (1 + L_TOL) * IL1_AT_MAX_DRAW ** 2
    dump = {}
    for di, what in ((I_IN_A2, "Option A(i)'s bound, U3's 6.35 A clamp plus 0.1 A"), (I_IN_DECL, "VBUS20's declared peak")):
        dv_loop = di / (2 * math.pi * FC_MIN * c_min)
        v1 = v_hi + dv_loop
        v2 = math.sqrt(v1 ** 2 + 2 * e_l1d / c_min)
        dump[di] = v2
        P("   %4.2f A (%s): loop %.3f V, |Zout| %.3f V; with L1's %.2f mJ (%.1f A, gen_sch_a.py line 751) the peak is %6.3f V"
          % (di, what, dv_loop, di * ZOUT_MAX, e_l1d * 1e3, IL1_AT_MAX_DRAW, v2))
    P("   (MODEL; below the OVP trip's %.3f V, so OVP need not act; whatever the model's error, section 3 caps it at %.3f V)"
      % (ovp_hi, ovp_res))
    P("   During the dump the charger is not switching: Q7 and Q8 then block the bus alone, VDS at most the bus plus Q8's")
    P("   body diode (SLPS516 VSD 1.0 V maximum): %.2f V." % (dump[I_IN_DECL] + 1.0))
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
    P("   the bus only through the loop. MODEL, valley current mode at L1 -20 %, fSW 175 kHz: the ripple rises from")
    rip = lambda vin: (vin - v_hi) * (v_hi / vin) / (L1_NOM * (1 - L_TOL) * FSW_MIN)
    r36, r60 = rip(36.0), rip(LM_ABS["VIN"])
    dv_line = (r60 - r36) / 2 / (2 * math.pi * FC_MIN * c_min)
    P("   %.2f A at 36 V to %.2f A at U2's 60 V, the average by %.2f A until the loop answers: %.3f V on the bus (%.3f V)."
      % (r36, r60, (r60 - r36) / 2, dv_line, v_hi + dv_line))
    P("   With U2 idle Q2 blocks VIN_RAW (section 1). Above 55 V U2 leaves its recommended range and above 60 V its absolute")
    P("   ratings (VIN, VISNS, VOSNS 60 V, p.5): the clamps' 64.5 V is S-111's item; this bound assumes U2 inside its ratings.")
    P("")

    # 6. clamps
    P("6. CLAMPS")
    P("   on VBUS20: none (section 1). Upstream: the four SMCJ40A class parts of section 5. On VBAT: D1 SMCJ18A (VR 18 V,")
    P("   VBR 20.00 to 22.10 V, VC 29.2 V at 51.4 A).")
    P("")

    # 7. pack side
    vbat_reg = VBAT_REG * (1 + VBAT_REG_ACC)
    vbat_ovp = VBAT_REG * BATOVP_MAX
    vr, vbr_lo, vbr_hi, vc, ipp = SMCJ["SMCJ18A"]
    d1_at = lambda i: vbr_hi + (vc - vbr_hi) * i / ipp
    e_l2 = 0.5 * L2_NOM * (1 + L_TOL) * IL2_PK["A2"] ** 2
    P("7. THE PACK SIDE (Q10's drain and, in buck mode, Q9's drain through Q10)")
    P("   ChargeVoltage 16.8 V + 0.5 %% = %.3f V (SLUSE66A 8.5 p.9); BATOVP at most 105 %% = %.2f V (p.14); SYSOVP (4S) %.1f / %.1f /"
      % (vbat_reg, vbat_ovp, SYSOVP_4S[0], SYSOVP_4S[1]))
    P("   %.1f V turns the converter off (p.14). A pack that opens while charging at A2's %.2f A: SYSOVP stops the converter at"
      % (SYSOVP_4S[2], IL2_PK["A2"]))
    P("   %.1f V and L2's %.2f mJ goes into VBAT's own capacitance (its effective value under bias is not held: INCONCLUSIVE);"
      % (SYSOVP_4S[2], e_l2 * 1e3))
    P("   D1 bounds it: %.2f V at %.2f A (INFERRED, the straight line from VBR max at 1 mA to VC at IPP), %.1f V at its IPP."
      % (d1_at(IL2_PK["A2"]), IL2_PK["A2"], vc))
    P("")

    # 8. the answer for the bus
    FIG.update(v_lo=v_lo, v_hi=v_hi, ovp_hi=ovp_hi, bound=ovp_res, dump=dump[I_IN_DECL], dump_a2=dump[I_IN_A2],
               line=v_hi + dv_line, d1_a2=d1_at(IL2_PK["A2"]), vbat_ovp=vbat_ovp, sysovp=SYSOVP_4S[2], ov_lo=ov_lo, ov_hi=ov_hi)
    P("8. THE BUS'S WORST CASE")
    P("   DC                        %6.3f V   (section 2)" % v_hi)
    P("   load dump, MODEL          %6.3f V   (section 4, the declared 8.0 A)" % dump[I_IN_DECL])
    P("   line step to 60 V, MODEL  %6.3f V   (section 5)" % (v_hi + dv_line))
    P("   BOUND, every mechanism    %6.3f V   (section 3: the OVP trip at VREF max and the worst ratio, plus L1's energy)" % ovp_res)
    P("")

    # 9. margins
    P("9. THE MARGINS (limit minus the figure)")
    rows = [
        ("Q7, Q8 VDS (30 V, SLPS526 / SLPS516 p.1)", FET_VDS, [v_hi, dump[I_IN_DECL], ovp_res]),
        ("U3 VBUS, ACP, ACN absolute (32 V, p.8)", BQ_ABS["VBUS, ACP, ACN"], [v_hi, dump[I_IN_DECL], ovp_res]),
        ("U3 VBUS, ACP, ACN recommended (26 V, p.8)", BQ_REC["VBUS, ACP, ACN"], [v_hi, dump[I_IN_DECL], ovp_res]),
        ("U3 ACOV rising minimum (26.0 V, p.14)", ACOV[0], [v_hi, dump[I_IN_DECL], ovp_res]),
        ("U3 SW1 absolute (32 V, p.8), before ringing", BQ_ABS["SW1, SW2"], [v_hi, dump[I_IN_DECL], ovp_res]),
        ("U3 SW1 recommended (26 V, p.8), before ringing", BQ_REC["SW1, SW2"], [v_hi, dump[I_IN_DECL], ovp_res]),
        ("U3 BTST1 absolute (38 V; bus + REGN 6.3 V)", BQ_ABS["BTST1, BTST2, HIDRV1, HIDRV2"],
         [v_hi + VREGN_MAX, dump[I_IN_DECL] + VREGN_MAX, ovp_res + VREGN_MAX]),
        ("U3 BTST1 recommended (32 V; bus + REGN 6.3 V)", BQ_REC["BTST1, BTST2, HIDRV1, HIDRV2"],
         [v_hi + VREGN_MAX, dump[I_IN_DECL] + VREGN_MAX, ovp_res + VREGN_MAX]),
    ]
    P("   %-50s %9s %9s %9s" % ("limit", "DC", "dump", "bound"))
    for name, lim, figs in rows:
        P("   %-50s %8.2f  %8.2f  %8.2f" % (name, lim - figs[0], lim - figs[1], lim - figs[2]))
    P("   pack side, against 30 V: Q9, Q10 VDS  %.2f V at BATOVP, %.2f V at SYSOVP, %.2f V at D1 with A2's current, %.2f V at"
      % (FET_VDS - vbat_ovp, FET_VDS - SYSOVP_4S[2], FET_VDS - d1_at(IL2_PK["A2"]), FET_VDS - vc))
    P("   D1's IPP; U3 VSYS, SRP, SRN (32 V abs, 23.15 V rec): %.2f / %.2f V at SYSOVP, %.2f / %.2f V at D1 with A2's current"
      % (BQ_ABS["SRN, SRP, VSYS"] - SYSOVP_4S[2], BQ_REC["SRN, SRP, VSYS"] - SYSOVP_4S[2],
         BQ_ABS["SRN, SRP, VSYS"] - d1_at(IL2_PK["A2"]), BQ_REC["SRN, SRP, VSYS"] - d1_at(IL2_PK["A2"])))
    P("   (BTST2 rides SW2, which sits at VBAT in buck mode: %.2f V at SYSOVP plus REGN, %.2f V under 32 V; BTST to SW is REGN's"
      % (SYSOVP_4S[2] + VREGN_MAX, BQ_REC["BTST1, BTST2, HIDRV1, HIDRV2"] - SYSOVP_4S[2] - VREGN_MAX))
    P("   own %.1f V at most against %.1f V absolute and %.1f V recommended, whatever the bus does)"
      % (VREGN_MAX, BQ_ABS_BTST_SW, BQ_REC_BTST_SW))
    P("")

    # 10. switch node
    P("10. THE SWITCH NODES: A BUDGET, NOT A BOUND (INCONCLUSIVE at desk)")
    P("   No layout exists (S-115) and no TI application note giving a layout-independent ringing bound is held. What TI does")
    P("   state: '30 V or higher voltage rating MOSFETs are preferred for 19-V to 20-V input voltage' (SLUSE66A 10.2.2.6 p.86),")
    P("   in a topology whose hot loop runs through RAC with at most 10 nF + 1 nF after it (p.86; Figure 10-1 p.83), as board A")
    P("   draws it. Board A's DC band tops out %.2f V above TI's 20 V." % (v_hi - 20.0))
    P("   Budget left for ringing over the steady bus (%.2f V) and over the bound (%.2f V):" % (v_hi, ovp_res))
    for name, lim in (("Q7 VDS (the bus plus SW1's undershoot) and Q8 VDS (SW1's overshoot), 30 V", FET_VDS),
                      ("U3 SW1 absolute 32 V", BQ_ABS["SW1, SW2"]), ("U3 SW1 recommended 26 V", BQ_REC["SW1, SW2"])):
        P("     %-78s %5.2f / %5.2f V" % (name, lim - v_hi, lim - ovp_res))
    P("     U3 SW1 below ground: %.0f V, and %.0f V for 25 ns (p.8)" % BQ_ABS_SW_NEG)
    ioff = Q7_VPLT / (RDS_HI_OFF_TYP + Q7["rg"])
    t_fi = (Q7["qgs"] - Q7["qgth"]) / ioff
    P("   MODEL for the layout writer (not a bound): Q7's current falls in (Qgs - Qg(th)) / (VPLT / (RDS_HI_OFF + RG)) =")
    P("   %.1f nC / (%.1f V / (%.1f + %.1f Ohm)) = %.2f ns (SLPS526 p.3; SLUSE66A p.16, typical; plateau INFERRED); each nH of"
      % ((Q7["qgs"] - Q7["qgth"]) * 1e9, Q7_VPLT, RDS_HI_OFF_TYP, Q7["rg"], t_fi * 1e9))
    P("   hot loop then adds L x di/dt, and the inductance between the VBUS20 bank and C190 / C191 lifts CH_ACN by I x sqrt(L /")
    P("   11 nF), which grows as the square root of L (the figure below is at 1 nH):")
    FIG.update(t_fi=t_fi)
    for pt in ("A2", "G1", "A1"):
        i = IL2_PK[pt]
        didt = i / t_fi
        FIG["ring_" + pt] = dict(i=i, vpn=didt * 1e-9, vacn=i * math.sqrt(1e-9 / 11e-9),
                                 l30=(FET_VDS - v_hi) / (didt * 1e-9), l26=(BQ_REC["SW1, SW2"] - v_hi) / (didt * 1e-9))
        P("     %s, L2 peak %5.2f A: %5.2f A/ns, %4.2f V per nH of loop and %4.2f V at 1 nH before C190; for the 30 V budget "
          "%.2f nH, for 26 V %.2f nH" % (pt, i, didt * 1e-9, didt * 1e-9, i * math.sqrt(1e-9 / 11e-9),
                                          (FET_VDS - v_hi) / (didt * 1e-9), (BQ_REC["SW1, SW2"] - v_hi) / (didt * 1e-9)))
    P("   Avalanche, if a ring does pass 30 V: EAS 23 mJ (CSD17578Q5A) and 39 mJ (CSD17577Q5A), single pulse, p.1; a repetitive")
    P("   rating is not stated, so no margin is taken from it.")
    P("")

    # 11. single faults
    vd5 = 0.8   # INFERRED: a body diode's typical drop at these currents
    P("11. SINGLE FAULTS OUTSIDE EVERY REQUIREMENT (ASM-001 refuses 'no single point of failure'; SC-39)")
    P("   Q2 shorted: VBUS20 = VIN_RAW less Q5's body diode (about %.1f V, INFERRED), %.1f V at 36 V in and %.1f V at board E's"
      % (vd5, 36.0 - vd5, ov_hi - vd5))
    P("   OVLO maximum; U3's ACOV (26.0 to 27.7 V, 100 us) stops the charger, and above %.1f V in U3's VBUS, ACP and ACN pass"
      % (BQ_ABS["VBUS, ACP, ACN"] + vd5))
    P("   their 32 V absolute rating. With the charger stopped Q7 and Q8 are both off and share the bus through their leakage")
    P("   and L2 to VBAT (INFERRED), so U3 is the first part past its rating, not the FETs.")
    P("   R6 open or FB shorted: OVP reads the same pin, so nothing on board A bounds the bus; the 35 V bulk parts and U3's")
    P("   32 V are passed. Neither fault is bounded by the FETs' rating: 40 V parts would not keep U3 inside 32 V.")
    P("   Not taken, for the qualified power review (S-111): an independent over-voltage trip on VBUS20 (a second divider into")
    ipk_hs = 6.15
    P("   U34's channel 1, re-armed while the stage runs) would bound the FB faults; an SMCJ22A on VBUS20 (VR 22 V over the")
    vr22, vbl22, vbh22, vc22, ipp22 = SMCJ["SMCJ22A"]
    P("   %.2f V DC band) would hold a Q2 short at about %.1f V at board E's %.2f A hot-swap limit (INFERRED straight line)"
      % (v_hi, vbh22 + (vc22 - vbh22) * ipk_hs / ipp22, ipk_hs))
    P("   until the LM5069's fault timer opens, and clamps %.1f V at its own IPP, over 30 V." % vc22)
    P("")

    # 12. answer
    P("12. THE ANSWER: (a), the bound holds in service")
    P("   VBUS20 stays at or under %.2f V by the front end's own protection whatever the load, the line or the loop model does,"
      % ovp_res)
    P("   %.2f V under the FETs' 30 V and %.2f V under U3's 32 V; U3's ACOV (26.0 V minimum) is never reached. The pack side stays"
      % (FET_VDS - ovp_res, BQ_ABS["VBUS, ACP, ACN"] - ovp_res))
    P("   at or under %.1f V by SYSOVP and %.2f V by D1 in a pack that opens while charging. The switch nodes are INCONCLUSIVE:"
      % (SYSOVP_4S[2], d1_at(IL2_PK["A2"])))
    P("   ringing is a layout and bench item with %.2f V of budget over the steady bus, carried as its own open item." % (FET_VDS - v_hi))
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
