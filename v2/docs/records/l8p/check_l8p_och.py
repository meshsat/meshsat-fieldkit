#!/usr/bin/env python3
"""check_l8p_och.py: Layer 8 record l8p ROUND 11 (MESHSAT-1357, 7 October 2026; register row L4A-67, finding L8P-R10-F1): board P's
netlist read by pin for the held-overcurrent trip apply_gen_sch_p_ocheld.py, drawn after the breaker and the ideal diode.

check_l8p_netlist.py (whose digest other records print) is left as it is; this module reads a board P that carries the trip, using
that reader's netlist parser and helpers:
  SENSE  U106 (OPA187) inverting on the gauge's R10: R132 from GND (R10's cell side) to -IN, R133 from -IN to OUT, +IN on PACK_N
         through R134, V- on PACK_N, V+ on BRK_VIN; R10 itself between GND and PACK_N; R135 and C117 into U107's SENSE1;
  WINDOW the held current the gain and U107's printed 0.792 to 0.808 V admit, from the drawn values (R132, R133) and the record's R10
         (2 mOhm, 1 % and 75 ppm/K over 130 K, ASSUMED): inside 18.80 A (the 18 A service's true current at the gauge's
         uncalibrated error, record l9stk's condition C4) and 22.75 A (the blades' printed rerated current at the band's 85.41 C);
  TRIP   U107 (a TPS37A010122) on BRK_VIN and PACK_N, SENSE1 on OCH_S, SENSE2 on BRK_PGD, RESET1 on OCH_R, RESET2 on OCH_EG, CTS1 and
         CTS2 each on its own capacitor to PACK_N (4.7 nF and 47 nF), CTR1 and CTR2 open;
  ARM    Q112 (2N7002) with its gate on OCH_EG (R139 from BRK_VIN, R141 to PACK_N), its source on RESET1, its drain on R137;
         Q110 (AO3401A) with its source on BRK_VIN and its gate on R136 from BRK_VIN over R137;
  BAR    the crowbar Q111 (CSD18510Q5B) with its gate on OCH_CG (R142 from Q110's drain, R138 and the zener D105 to PACK_N), its
         source on PACK_N and its drain through R140 to PACK_P, R140 at most 0.44 Ohm (its own current at the pack's least 10.6 V
         over the LM5069's most limit 23.93 A);
  APART  no net of the trip is a net of the enable loop (DOCK_EN_OUT, DOCK_EN_RET), of UVLO and its hold (BRK_UVLO, BRK_H,
         BRK_HD, BRK_G2) or of the restart inhibit; each trip net reaches only the trip's pins and a test point.
Usage:  check_l8p_och.py NETLIST      Exit 0 DRAWN, 4 FAIL, 3 NOT DRAWN (U107 absent). Nothing is written."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import check_l8p_netlist as C  # noqa: E402

VITP = (0.792, 0.800, 0.808)         # TI SNVSBJ1E 7.5, VITP at VIT = 800 mV (the 0.8 V variant), over -40 to 125 C: PRINTED
R10_NOM, R10_TOL, R10_TCR, R10_DT = 2.0e-3, 0.01, 75e-6, 130.0     # record l8p 12c's R10 (1 %, 75 ppm/K: ASSUMED, E-6), 25 to 155 C
GAIN_TOL, GAIN_TCR, GAIN_DT = 0.001, 25e-6, 100.0                  # R132 and R133 as drawn (0.1 %, 25 ppm/K), -40 to 125 C
VOS = 18.8e-6                        # OPA187 SBOS807E: VOS 10 uV + drift 0.015 uV/C x 100 K + CMRR 126 dB at VCM V- (7.3 uV): PRINTED rows
IB, ISENSE = 7.5e-9, 100e-9          # OPA187's IB over temperature; TPS37's ISENSE at VIT 800 mV: PRINTED
SERVICE_TRUE, BLADE_BAND = 18.80, 22.75   # record l9stk condition C4 (an indicated 18 A, a true 18.80 A); record l8p round 10 (22.75 A)
VCL_MAX_LIMIT, PACK_LEAST = 23.93, 10.6   # the breaker's most limit (record l9stk 15.4); the pack's least in service

TRIP_PARTS = ("U106", "R132", "R133", "R134", "C116", "R135", "C117", "U107", "C118", "C119", "C120", "R139", "R141", "Q112", "R136",
              "R137", "Q110", "R142", "R138", "D105", "Q111", "R140", "TP110", "TP111")
TRIP_NETS = ("OCH_N", "OCH_P", "OCH_A", "OCH_S", "OCH_R", "OCH_EG", "OCH_X", "OCH_PG", "OCH_GD", "OCH_CG", "OCH_CD", "OCH_CTS", "OCH_CTS2")
KEEP_OFF = ("DOCK_EN_OUT", "DOCK_EN_RET", "BRK_UVLO", "BRK_H", "BRK_HD", "BRK_G2", "INH_G", "INH_OUT", "INH_NTC", "INH_REF")
VALUES = (("U106", "OPA187"), ("U107", "TPS37A010122"), ("Q112", "2N7002"), ("Q110", "AO3401A"), ("Q111", "CSD18510Q5B"),
          ("D105", "BZT52C12"), ("R132", "1.00k 0.1% 25ppm"), ("R133", "19.3k 0.1% 25ppm"), ("R136", "47k"), ("R137", "100k"),
          ("R138", "4.7k"), ("R139", "1M"), ("R141", "1M"), ("R142", "1k"), ("C119", "4.7n 50V C0G"), ("C120", "47n 50V C0G"))


def och_drawn(nl):
    return str(nl["comps"].get("U107", {}).get("value", "")).startswith("TPS37A010122") and "OCH_S" in nl["on"]


def _val(nl, ref):
    return str(nl["comps"].get(ref, {}).get("value", ""))


def window(nl):
    """(least, most) held current the drawn gain and the printed threshold admit, or None if a value does not read."""
    try:
        rin, rf = C._ohms(_val(nl, "R132")), C._ohms(_val(nl, "R133"))
    except (ValueError, KeyError):
        return None
    g = rf / rin
    gd = GAIN_TOL + GAIN_TCR * GAIN_DT
    g_hi, g_lo = g * (1 + gd) / (1 - gd), g * (1 - gd) / (1 + gd)
    rd = R10_TOL + R10_TCR * R10_DT
    r_hi, r_lo = R10_NOM * (1 + rd), R10_NOM * (1 - rd)
    lo = (VITP[0] - (1 + g_hi) * VOS - IB * rf * (1 + gd) - ISENSE * 1e3) / (g_hi * r_hi)
    hi = (VITP[2] + (1 + g_hi) * VOS + IB * rf * (1 + gd) + ISENSE * 1e3) / (g_lo * r_lo)
    return lo, hi


def checks_och(nl):
    bad = []
    bad += C.props(nl, [("U106", "1", "OCH_A"), ("U106", "2", "PACK_N"), ("U106", "3", "OCH_P"), ("U106", "4", "OCH_N"), ("U106", "5", "BRK_VIN"),
                        ("R10", "1", "GND"), ("R10", "2", "PACK_N")])
    pairs = (("R132", "GND", "OCH_N"), ("R133", "OCH_N", "OCH_A"), ("R134", "PACK_N", "OCH_P"), ("R135", "OCH_A", "OCH_S"),
             ("C117", "OCH_S", "PACK_N"), ("C116", "BRK_VIN", "PACK_N"), ("C118", "BRK_VIN", "PACK_N"), ("C119", "OCH_CTS", "PACK_N"),
             ("C120", "OCH_CTS2", "PACK_N"), ("R139", "BRK_VIN", "OCH_EG"), ("R141", "OCH_EG", "PACK_N"), ("R136", "BRK_VIN", "OCH_PG"),
             ("R137", "OCH_PG", "OCH_X"), ("R142", "OCH_GD", "OCH_CG"), ("R138", "OCH_CG", "PACK_N"), ("R140", "PACK_P", "OCH_CD"))
    bad += ["%s on %s, wanted %s and %s" % (r, C._two(nl, r), a, b) for r, a, b in pairs if C._two(nl, r) != sorted({a, b})]
    bad += C.props(nl, [("U107", "1", "BRK_VIN"), ("U107", "2", "OCH_S"), ("U107", "3", "BRK_PGD"), ("U107", "4", "OCH_R"),
                        ("U107", "5", "OCH_EG"), ("U107", "7", "OCH_CTS"), ("U107", "8", "OCH_CTS2"), ("U107", "10", "PACK_N"),
                        ("U107", "11", "PACK_N"), ("U107", "6", None), ("U107", "9", None)])
    bad += C.props(nl, [("Q112", "1", "OCH_EG"), ("Q112", "2", "OCH_R"), ("Q112", "3", "OCH_X"),
                        ("Q110", "1", "OCH_PG"), ("Q110", "2", "BRK_VIN"), ("Q110", "3", "OCH_GD"),
                        ("D105", "1", "OCH_CG"), ("D105", "2", "PACK_N"),
                        ("Q111", "1", "PACK_N"), ("Q111", "2", "PACK_N"), ("Q111", "3", "PACK_N"), ("Q111", "4", "OCH_CG"), ("Q111", "5", "OCH_CD")])
    if C._pin(nl, "U101", "8") != "BRK_PGD":
        bad.append("U101's PGD (pin 8) on %r, not BRK_PGD" % C._pin(nl, "U101", "8"))
    for ref, pre in VALUES:
        if not _val(nl, ref).startswith(pre):
            bad.append("%s value %r does not start %r" % (ref, _val(nl, ref), pre))
    try:
        r140 = C._ohms(_val(nl, "R140"))
    except (ValueError, KeyError):
        r140 = None
    if r140 is None or PACK_LEAST / (r140 * 1.01) <= VCL_MAX_LIMIT:
        bad.append("R140 %r: the crowbar's own current at %.1f V does not exceed the breaker's most limit %.2f A" % (_val(nl, "R140"), PACK_LEAST, VCL_MAX_LIMIT))
    w = window(nl)
    if w is None or not (w[0] > SERVICE_TRUE and w[1] < BLADE_BAND):
        bad.append("the held window %s is not inside %.2f to %.2f A" % (("%.2f to %.2f A" % w) if w else "unreadable", SERVICE_TRUE, BLADE_BAND))
    for n in TRIP_NETS:
        extra = sorted(r for r in nl["on"].get(n, set()) if r not in TRIP_PARTS and not C._is_tp(nl, r))
        if extra:
            bad.append("%s reaches %s beyond the trip's parts" % (n, extra))
    for n in KEEP_OFF:
        touch = sorted(r for r in nl["on"].get(n, set()) if r in TRIP_PARTS)
        if touch:
            bad.append("%s reaches the trip's %s (the trip must touch neither the loop nor UVLO)" % (n, touch))
    return ("FAIL", bad) if bad else ("DRAWN", [])


def judge(nl):
    if not och_drawn(nl):
        return {"OCH": ("NOT DRAWN", ["U107 is absent"])}
    return {"OCH": checks_och(nl)}


def main(argv):
    if len(argv) != 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0].strip() + "\n")
        return 2
    nl = C.read_netlist(open(argv[0], "rb").read())
    res = judge(nl)
    for k, (v, why) in res.items():
        print("P %-4s %s%s" % (k, v, (": " + "; ".join(why)) if why else ""))
    vs = [v for v, _w in res.values()]
    return 3 if "NOT DRAWN" in vs else 4 if "FAIL" in vs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
