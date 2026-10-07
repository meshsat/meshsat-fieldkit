#!/usr/bin/env python3
"""check_l8p_och.py: Layer 8 record l8p ROUND 11 (MESHSAT-1357, 7 October 2026; register row L4A-67, finding L8P-R10-F1): board P's
netlist read by pin for the held-overcurrent trip apply_gen_sch_p_ocheld.py, drawn after the breaker and the ideal diode. ROUND 12
(the focused check L4A-69, W147's F3 and F2): the window and the delays are computed from the DRAWN values of R10, R132, R133, R135,
C117, C119 and C120 (round 11 read R132 and R133 only), and the on-time bound (D106, R143, OCH_S2) is read. ROUND 13 (the targeted
recheck L4A-69, W153's F1): OCH_S2's level while PGD is LOW is computed with every leakage that can reach it at the record's 86.25 C
site (round 12's R143 2.2 MOhm from BRK_PGD let D106's and Q112's leakage lift it over SENSE2's threshold), so round 12's drawing
FAILS and round 13's (R143 330 kOhm from BRK_VIN, Q114 holding OCH_S2 low while PGD is low, its gate PGD inverted by Q113 with R144
and the zener D107) reads DRAWN; BRK_PGD may carry no resistor or diode of the trip; RESET1's node may not be the pull-down's node.

check_l8p_netlist.py (whose digest other records print) is left as it is; this module reads a board P that carries the trip, using
that reader's netlist parser and helpers:
  SENSE  U106 (OPA187) inverting on the gauge's R10: R132 from GND (R10's cell side) to -IN, R133 from -IN to OUT, +IN on PACK_N
         through R134, V- on PACK_N, V+ on BRK_VIN; R10 itself between GND and PACK_N; R135 and C117 into U107's SENSE1;
  WINDOW the held current the gain and U107's printed 0.792 to 0.808 V admit, from the drawn values (R10, R132, R133, R135; R10's
         tolerance 1 % and 75 ppm/K over 130 K ASSUMED, E-6): inside 18.80 A (the 18 A service's true current at the gauge's
         uncalibrated error, record l9stk's condition C4) and 22.75 A (the blades' printed rerated current at the band's 85.41 C);
  DELAY  from the drawn C117, C119, C120 and R135 (TI's Equations 5 and 6, C0G at 5 %): SENSE1's filter R135 x C117 at most 5 % of
         the least sense delay; the least sense delay over E-10's 0.282 ms; the least arming delay over the trip's gate and the
         -1's 1.292 ms clearing by 0.5 ms or more; the most arming delay at most 3.93 ms (the on-time R140's E-6b is stated for);
  TRIP   U107 (a TPS37A010122) on BRK_VIN and PACK_N, SENSE1 on OCH_S, SENSE2 on OCH_S2, RESET1 on OCH_R, RESET2 on OCH_EG, CTS1 and
         CTS2 each on its own capacitor to PACK_N (4.7 nF and 22 nF), CTR1 and CTR2 open;
  BOUND  (round 12) D106 (BAT46W, cathode on OCH_R): while RESET1 is asserted OCH_S2 is under 0.64 V (0.55 V at 25 C, 90 mV for
         -20 C), so RESET2 disarms the crowbar after the arming delay whatever the breaker does; (round 13) R143 from BRK_VIN to
         OCH_S2 keeps OCH_S2 over the release level with Q114's off leakage at the site, RESET1's 300 nA and SENSE2's largest printed
         2 uA through it; BRK_PGD carries only gates (Q106's and Q113's), over Q106's 2.5 V threshold maximum at BRK_VIN 7.6 V;
  PGDLOW (round 13) OCH_S2 while PGD is low, at BRK_VIN 7.6 V and every leakage at the 86.25 C site: a 2N7002 from OCH_S2 to PACK_N
         whose gate is PGD inverted (a 2N7002 from BRK_PGD) and pulled up from BRK_VIN, at least 5 V with the inverter's and the
         zener's leakage (where its 7 Ohm is printed), holds OCH_S2 at its drop; without it, the leakage into OCH_S2 through D106
         (BAT46W's printed 60 C row doubled to the site) through R143 sets the level;
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
              "R137", "Q110", "R142", "R138", "D105", "Q111", "R140", "R143", "D106", "TP110", "TP111", "TP112", "Q113", "Q114", "R144",
              "D107")
TRIP_NETS = ("OCH_N", "OCH_P", "OCH_A", "OCH_S", "OCH_R", "OCH_EG", "OCH_X", "OCH_PG", "OCH_GD", "OCH_CG", "OCH_CD", "OCH_CTS", "OCH_CTS2",
             "OCH_S2", "OCH_PN")
KEEP_OFF = ("DOCK_EN_OUT", "DOCK_EN_RET", "BRK_UVLO", "BRK_H", "BRK_HD", "BRK_G2", "INH_G", "INH_OUT", "INH_NTC", "INH_REF")
VALUES = (("U106", "OPA187"), ("U107", "TPS37A010122"), ("Q112", "2N7002"), ("Q110", "AO3401A"), ("Q111", "CSD18510Q5B"),
          ("D105", "BZT52C12"), ("R132", "1.00k 0.1% 25ppm"), ("R133", "19.3k 0.1% 25ppm"), ("R136", "47k"), ("R137", "100k"),
          ("R138", "4.7k"), ("R139", "1M"), ("R141", "1M"), ("R142", "1k"), ("C119", "4.7n 50V C0G"), ("C120", "22n 50V C0G"),
          ("R143", "330k"), ("D106", "BAT46W"), ("Q113", "2N7002"), ("Q114", "2N7002"), ("R144", "200k"), ("D107", "BZT52C12"))
# the delays (TI SNVSBJ1E Equations 5 and 6, the capacitors C0G at 5 %; the no-capacitor least not printed, taken 0)
C_TOL = 0.05
E10 = 0.282e-3                       # record l9stk 15.7: E-10's bound on the key-down excursions over the breaker's least limit
T_GATE, CLEAR, ARM_MARGIN = 12.3e-6, 1.292e-3, 0.5e-3     # the crowbar's gate (l8p_cprot 4c), the -1's clearing at most (l9stk), margin
T_ON_BOUND = 3.93e-3                 # round 12: the most arming delay R140's E-6b figure is stated for (l8p_cprot.out [CP 4c'])
FILTER_SHARE = 0.05                  # SENSE1's R135 x C117 at most this share of the least sense delay
# the on-time bound's levels (round 12): Q106's VGS(th) maximum (JSCJ 2N7002, PRINTED), TPS37's VOL at 5 mA and leakage, BAT46W's VF
VTH_Q106, VOL, ILKG_OD, VF_D106, BRK_LEAST = 2.5, 0.300, 300e-9, 0.25, 7.6
REL_MAX = 0.808 * 1.13 * 1.015       # SENSE2's release at most: VITN's 0.808 V plus the TPS37 family's largest 13 % hysteresis, +1.5 %
# round 13 (W153's F1): the leakages at the record's site (86.25 C, the air plus 10 K), each off leakage doubled every 10 K (the record's
# ASSUMED rule) from its printed row; the gate oxide's IGSS taken at its printed 25 C row (not an off leakage; Q106's gate already
# rests on it); RDS(on) printed at VGS 5 V; SENSE's largest printed input current (2 uA, the 26 V and over row) taken for SENSE2 far
# over its 0.8 V threshold (ASSUMED to bound it); BAT46W's VF rises about 90 mV at -20 C (INFERRED from its typical curve, W153)
SITE, DOUBLING_K, CLAMP = 86.25, 10.0, 29.2
IDSS_HOT = 80e-9 * 2 ** ((SITE - 25.0) / DOUBLING_K)        # JSCJ 2N7002 80 nA at 60 V and 25 C (PRINTED), doubled (ASSUMED)
IR_ZENER_HOT = 0.1e-6 * 2 ** ((SITE - 25.0) / DOUBLING_K)   # BZT52C12 0.1 uA at VR 8 V and 25 C (PRINTED, DS18004), doubled (ASSUMED)
IR_D106_HOT = 15e-6 * 2 ** ((SITE - 60.0) / DOUBLING_K)     # BAT46W 15 uA at VR 50 V and TJ 60 C (PRINTED, DS30044), doubled (ASSUMED)
IGSS, RDS_5V, VGS_RDS, ISENSE_MAX, VF_COLD, VOL_PGD = 80e-9, 7.0, 5.0, 2e-6, 0.09, 0.150
VF_ROWS = ((0.1e-3, 0.25), (10e-3, 0.45))                  # BAT46W VF at most at IF (PRINTED, 25 C)
R_TOL = 0.01


def _num(v, units):
    import re
    m = re.match(r"([0-9.]+)\s*([%s]?)" % "".join(units), str(v))
    if not m:
        raise ValueError(v)
    return float(m.group(1)) * units.get(m.group(2), 1.0)


def ohms(v):
    """A resistor's leading figure in ohms, milliohms included: '2m 2512' is 0.002, '0.39R' 0.39, '2.2M' 2.2e6."""
    return _num(v, {"m": 1e-3, "R": 1.0, "k": 1e3, "K": 1e3, "M": 1e6})


def farads(v):
    """A capacitor's leading figure in farads: '4.7n 50V' is 4.7e-9, '10u' 1e-5."""
    return _num(v, {"p": 1e-12, "n": 1e-9, "u": 1e-6, "\u00b5": 1e-6})


def och_drawn(nl):
    return str(nl["comps"].get("U107", {}).get("value", "")).startswith("TPS37A010122") and "OCH_S" in nl["on"]


def _val(nl, ref):
    return str(nl["comps"].get(ref, {}).get("value", ""))


def window(nl):
    """(least, most) held current the drawn gain, the drawn R10 and R135 and the printed threshold admit, or None if a value does not
    read. R10's tolerance and temperature coefficient are the record's assumption (E-6); its value is read from the netlist."""
    try:
        rin, rf, r135 = ohms(_val(nl, "R132")), ohms(_val(nl, "R133")), ohms(_val(nl, "R135"))
        r10 = ohms(_val(nl, "R10"))
    except (ValueError, KeyError):
        return None
    g = rf / rin
    gd = GAIN_TOL + GAIN_TCR * GAIN_DT
    g_hi, g_lo = g * (1 + gd) / (1 - gd), g * (1 - gd) / (1 + gd)
    rd = R10_TOL + R10_TCR * R10_DT
    r_hi, r_lo = r10 * (1 + rd), r10 * (1 - rd)
    lo = (VITP[0] - (1 + g_hi) * VOS - IB * rf * (1 + gd) - ISENSE * r135) / (g_hi * r_hi)
    hi = (VITP[2] + (1 + g_hi) * VOS + IB * rf * (1 + gd) + ISENSE * r135) / (g_lo * r_lo)
    return lo, hi


def tcts(c):
    """(least, most) sense delay of a TPS37 channel with the capacitor c (TI's Equations 5 and 6; RCTS 88 to 122 kOhm)."""
    import math
    return (-math.log(0.31) * 88e3 * c * (1 - C_TOL), -math.log(0.25) * 122e3 * c * (1 + C_TOL) + 17e-6)


def delays(nl):
    """The drawn delays: SENSE1's filter, the sense delay and the arming delay, or None if a value does not read."""
    try:
        r135, c117 = ohms(_val(nl, "R135")), farads(_val(nl, "C117"))
        c119, c120 = farads(_val(nl, "C119")), farads(_val(nl, "C120"))
    except (ValueError, KeyError):
        return None
    return {"filter": r135 * c117, "cts1": tcts(c119), "cts2": tcts(c120)}


def _vf(i):
    """BAT46W's printed VF at most for a forward current up to i (the first printed row at or over i)."""
    for imax, v in VF_ROWS:
        if i <= imax:
            return v
    return None


def topo(nl):
    """The arming's arrangement as the netlist draws it: R143's far net, the pull-down on OCH_S2 and its gate's network, the gates on
    BRK_PGD. A value-only netlist (no pins, the unit tests) is read as round 13 draws it."""
    if not nl.get("pins"):
        return {"r143_far": "BRK_VIN", "pull": "Q114", "gate": "OCH_PN", "gate_r": "R144", "gate_fets": 1, "gate_zeners": 1,
                "inverter": True, "pgd_gates": 2, "pgd_other": []}
    two = lambda ref: C._two(nl, ref)
    far = [n for n in two("R143") if n != "OCH_S2"]
    fets = [r for r, c in nl["comps"].items() if str(c.get("value", "")).startswith("2N7002")]
    pull = [q for q in fets if C._pin(nl, q, "3") == "OCH_S2" and C._pin(nl, q, "2") == "PACK_N"]
    g = C._pin(nl, pull[0], "1") if pull else None
    gate_r = [r for r in nl["comps"] if r.startswith("R") and g and two(r) == sorted({"BRK_VIN", g})]
    on_g = [q for q in fets if g and C._pin(nl, q, "3") == g and C._pin(nl, q, "2") == "PACK_N"]
    zen = [d for d, c in nl["comps"].items() if str(c.get("value", "")).startswith("BZT52C12") and g and C._pin(nl, d, "1") == g
           and C._pin(nl, d, "2") == "PACK_N"]
    pgd_gates = [q for q in fets if C._pin(nl, q, "1") == "BRK_PGD"]
    pgd_other = sorted(r for r in nl["on"].get("BRK_PGD", set()) if r in TRIP_PARTS and r not in pgd_gates)
    return {"r143_far": far[0] if far else None, "pull": pull[0] if pull else None, "gate": g, "gate_r": gate_r[0] if gate_r else None,
            "gate_fets": len(on_g), "gate_zeners": len(zen), "inverter": any(C._pin(nl, q, "1") == "BRK_PGD" for q in on_g),
            "pgd_gates": len(pgd_gates), "pgd_other": pgd_other}


def bound_levels(nl):
    """The arming's levels from the drawn R143 (and R144) at BRK_VIN 7.6 V: OCH_S2 with RESET1 asserted (low), BRK_PGD's level with the
    trip's load on it (pgd), OCH_S2 armed (PGD high, RESET1 released, every sink at the site), and (round 13) OCH_S2 while PGD is LOW
    with every leakage that can reach it at the site (pgd_low). Round 12's arrangement (R143 from BRK_PGD) is computed as drawn, so
    its leakage-lifted PGD-low level reads; None if a value does not read."""
    try:
        r143 = ohms(_val(nl, "R143"))
    except (ValueError, KeyError):
        return None
    tp = topo(nl)
    on_pgd = tp["r143_far"] == "BRK_PGD"
    # RESET1 asserted: D106 carries R143's current into RESET1 (VOL at its 5 mA row), at the clamp when R143 is on BRK_VIN
    i_d = (BRK_LEAST / 2 if on_pgd else CLAMP - VOL) / (r143 * (1 - R_TOL))
    vf = _vf(i_d)
    low = VOL + (vf if vf is not None else 1.0) + VF_COLD
    if on_pgd:
        pgd = (BRK_LEAST / 2 * r143 + (VOL + VF_D106) * 0.5e6) / (r143 + 0.5e6)
        armed = BRK_LEAST / 2 - (ILKG_OD + ISENSE) * r143
        # PGD low: the PGD pin sinks; whatever leaks into OCH_S2 through D106 (Q112's off leakage when it is off, D106's reverse
        # current when Q112 holds OCH_R up) returns through R143 into it
        # (the lift stops where D106's reverse bias collapses, at OCH_R's level: at most half of BRK_VIN through Q112)
        pgd_low = min(VOL_PGD + IR_D106_HOT * r143 * (1 + R_TOL), BRK_LEAST / 2)
        gate = None
    else:
        pgd = BRK_LEAST / 2 - 0.5e6 * IGSS * max(tp["pgd_gates"], 1)
        armed = BRK_LEAST - r143 * (1 + R_TOL) * ((IDSS_HOT if tp["pull"] else 0.0) + ILKG_OD + ISENSE_MAX)
        gate = None
        if tp["pull"] and tp["inverter"] and tp["gate_r"]:
            try:
                rg = ohms(_val(nl, tp["gate_r"])) if nl.get("pins") else ohms(_val(nl, "R144"))
            except (ValueError, KeyError):
                rg = None
            if rg:
                gate = min(BRK_LEAST - rg * (1 + R_TOL) * (tp["gate_fets"] * IDSS_HOT + tp["gate_zeners"] * IR_ZENER_HOT),
                           12.7 if tp["gate_zeners"] else CLAMP)
        if gate is not None and gate >= VGS_RDS:
            # the pull-down conducts on its printed 7 Ohm: R143's current at the clamp and D106's leakage at the site through it
            pgd_low = RDS_5V * (CLAMP / (r143 * (1 - R_TOL)) + IR_D106_HOT)
        else:
            pgd_low = BRK_LEAST      # no pull-down shown on printed figures: R143 holds OCH_S2 up toward BRK_VIN
    return {"low": low, "pgd": pgd, "armed": armed, "pgd_low": pgd_low, "gate": gate, "i_d106": i_d, "on_pgd": on_pgd,
            "pgd_other": tp["pgd_other"]}


def checks_och(nl):
    bad = []
    # round 13: the electrical predicates first, so a mutation reads its electrical failure before a pin or value mismatch
    if C._pin(nl, "U107", "4") and C._pin(nl, "U107", "4") == C._pin(nl, "Q114", "3"):
        bad.append("RESET1's node is the PGD-low pull-down's node (a shorted D106: Q114 completes the crowbar's gate path at a fall of PGD)")
    b = bound_levels(nl)
    if b is None:
        bad.append("R143 does not read")
    else:
        if not b["pgd_low"] < VITP[0]:
            bad.append("OCH_S2 at %.2f V while PGD is low (every leakage at the %.2f C site, BRK_VIN %.1f V) is not under SENSE2's least threshold: "
                       "the crowbar armed on a breaker that is not running" % (b["pgd_low"], SITE, BRK_LEAST))
        if not b["low"] < VITP[0]:
            bad.append("OCH_S2 at %.3f V with RESET1 asserted (D106 at %.0f uA, -20 C) is not under SENSE2's least threshold" % (b["low"], b["i_d106"] * 1e6))
        if not b["pgd"] > VTH_Q106:
            bad.append("BRK_PGD at %.2f V with the trip's load (BRK_VIN %.1f V) is not over Q106's %.1f V threshold maximum" % (b["pgd"], BRK_LEAST, VTH_Q106))
        if not b["armed"] > REL_MAX:
            bad.append("OCH_S2 armed at %.2f V (BRK_VIN %.1f V, the sinks at the site) is not over SENSE2's release %.3f V" % (b["armed"], BRK_LEAST, REL_MAX))
        if b["pgd_other"]:
            bad.append("BRK_PGD reaches the trip's %s beyond Q113's gate (round 13: no resistor or diode of the trip on BRK_PGD)" % b["pgd_other"])
    bad += C.props(nl, [("U106", "1", "OCH_A"), ("U106", "2", "PACK_N"), ("U106", "3", "OCH_P"), ("U106", "4", "OCH_N"), ("U106", "5", "BRK_VIN"),
                        ("R10", "1", "GND"), ("R10", "2", "PACK_N")])
    pairs = (("R132", "GND", "OCH_N"), ("R133", "OCH_N", "OCH_A"), ("R134", "PACK_N", "OCH_P"), ("R135", "OCH_A", "OCH_S"),
             ("C117", "OCH_S", "PACK_N"), ("C116", "BRK_VIN", "PACK_N"), ("C118", "BRK_VIN", "PACK_N"), ("C119", "OCH_CTS", "PACK_N"),
             ("C120", "OCH_CTS2", "PACK_N"), ("R139", "BRK_VIN", "OCH_EG"), ("R141", "OCH_EG", "PACK_N"), ("R136", "BRK_VIN", "OCH_PG"),
             ("R137", "OCH_PG", "OCH_X"), ("R142", "OCH_GD", "OCH_CG"), ("R138", "OCH_CG", "PACK_N"), ("R140", "PACK_P", "OCH_CD"),
             ("R143", "BRK_VIN", "OCH_S2"), ("R144", "BRK_VIN", "OCH_PN"))
    bad += ["%s on %s, wanted %s and %s" % (r, C._two(nl, r), a, b) for r, a, b in pairs if C._two(nl, r) != sorted({a, b})]
    bad += C.props(nl, [("U107", "1", "BRK_VIN"), ("U107", "2", "OCH_S"), ("U107", "3", "OCH_S2"), ("U107", "4", "OCH_R"),
                        ("U107", "5", "OCH_EG"), ("U107", "7", "OCH_CTS"), ("U107", "8", "OCH_CTS2"), ("U107", "10", "PACK_N"),
                        ("U107", "11", "PACK_N"), ("U107", "6", None), ("U107", "9", None)])
    bad += C.props(nl, [("Q112", "1", "OCH_EG"), ("Q112", "2", "OCH_R"), ("Q112", "3", "OCH_X"),
                        ("Q110", "1", "OCH_PG"), ("Q110", "2", "BRK_VIN"), ("Q110", "3", "OCH_GD"),
                        ("D105", "1", "OCH_CG"), ("D105", "2", "PACK_N"), ("D106", "1", "OCH_R"), ("D106", "2", "OCH_S2"),
                        ("Q113", "1", "BRK_PGD"), ("Q113", "2", "PACK_N"), ("Q113", "3", "OCH_PN"), ("Q114", "1", "OCH_PN"),
                        ("Q114", "2", "PACK_N"), ("Q114", "3", "OCH_S2"), ("D107", "1", "OCH_PN"), ("D107", "2", "PACK_N"),
                        ("Q111", "1", "PACK_N"), ("Q111", "2", "PACK_N"), ("Q111", "3", "PACK_N"), ("Q111", "4", "OCH_CG"), ("Q111", "5", "OCH_CD")])
    if C._pin(nl, "U101", "8") != "BRK_PGD":
        bad.append("U101's PGD (pin 8) on %r, not BRK_PGD" % C._pin(nl, "U101", "8"))
    for ref, pre in VALUES:
        if not _val(nl, ref).startswith(pre):
            bad.append("%s value %r does not start %r" % (ref, _val(nl, ref), pre))
    try:
        r140 = ohms(_val(nl, "R140"))
    except (ValueError, KeyError):
        r140 = None
    if r140 is None or PACK_LEAST / (r140 * 1.01) <= VCL_MAX_LIMIT:
        bad.append("R140 %r: the crowbar's own current at %.1f V does not exceed the breaker's most limit %.2f A" % (_val(nl, "R140"), PACK_LEAST, VCL_MAX_LIMIT))
    w = window(nl)
    if w is None or not (w[0] > SERVICE_TRUE and w[1] < BLADE_BAND):
        bad.append("the held window %s is not inside %.2f to %.2f A" % (("%.2f to %.2f A" % w) if w else "unreadable", SERVICE_TRUE, BLADE_BAND))
    d = delays(nl)
    if d is None:
        bad.append("the delays do not read (R135, C117, C119, C120)")
    else:
        if d["filter"] > FILTER_SHARE * d["cts1"][0]:
            bad.append("SENSE1's filter R135 x C117 %.1f us is over %.0f %% of the least sense delay %.3f ms" % (d["filter"] * 1e6, 100 * FILTER_SHARE, d["cts1"][0] * 1e3))
        if d["cts1"][0] <= E10:
            bad.append("the least sense delay %.3f ms is not over E-10's %.3f ms" % (d["cts1"][0] * 1e3, E10 * 1e3))
        if d["cts2"][0] < T_GATE + CLEAR + ARM_MARGIN:
            bad.append("the least arming delay %.3f ms does not cover the gate, the -1's clearing and %.1f ms" % (d["cts2"][0] * 1e3, ARM_MARGIN * 1e3))
        if d["cts2"][1] > T_ON_BOUND:
            bad.append("the most arming delay %.3f ms is over the %.2f ms R140's pulse figure is stated for" % (d["cts2"][1] * 1e3, T_ON_BOUND * 1e3))
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
