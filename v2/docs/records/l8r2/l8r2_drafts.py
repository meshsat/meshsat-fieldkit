#!/usr/bin/env python3
"""l8r2_drafts.py: the Layer 8 record l8r2's figures and drafts, proved on scratch copies (MESHSAT-1357, 3 October 2026).

It prints, deterministically and without touching the tree:
  1. the inputs, each pinned by sha256 (the generators, every board A and board B draft in the tree, this record's drafts, the makers'
     sheets it reads, its inputs/ copies); the held-back TPS4811-Q1 sheet by the sha256 its fetch script checks;
  2. item 1, board B's coolers: the TPS61089 step-up from TI's equations, the eFuse's window, the slot power of the two choices;
  3. item 2, VBUS20's single faults: the clamp's power at the fault (rejected), the cut-off's window and the bus after the cut;
  4. item 3, Layer 5's round 2 findings: the PANEL_5V and board D 3.3 V limits per conductor, the J_QMX land;
  5. the composition on board A: L4-E9's power order (r12, guard, charger, r11, bank, r138, u17), l8gnd's two, this record's two, then
     d8dec31's mainpb LAST; this record's drafts first and then every other draft (their anchors still apply after these); each power
     draft alone after this record's; the four Layer 8 drafts of board A in forward and reverse order;
  6. the composition on board B: l8gnd's GND-002 draft and this record's three in forward and reverse order, and each alone;
  7. the designators each draft adds on boards A and B, pairwise disjoint, and every literal designator in part-call position of the
     composed generators drawn once;
  8. the netlist check (check_l8r2_netlist.py) on the committed netlists (NOT DRAWN) and on fixtures carrying the drafts (DRAWN).
Run from the repository root:  python3 v2/docs/records/l8r2/l8r2_drafts.py  (l8r2_drafts.out is its output, regenerated with
_bin/regen_out.py). Nothing here is built or measured: every statement is about generator text, netlists and printed figures."""
import ast
import hashlib
import importlib.util
import io
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
RECS = os.path.join(ROOT, "v2", "docs", "records")
GEN_A = os.path.join(TOOLS, "gen_sch_a.py")
GEN_B = os.path.join(TOOLS, "gen_sch_b.py")
NET_A = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"

POWER_A = [("l4e6", "r12"), ("l4e11", "guard"), ("l4e11", "charger"), ("l4e4", "r11"), ("l4e8", "bank"), ("l4e4", "r138"), ("l4e9", "u17")]
L8_A = [("l8gnd", "gnd002"), ("l8gnd", "hotr1"), ("l8r2", "d8v3"), ("l8r2", "vbus20ov")]
MINE_A = [("l8r2", "d8v3"), ("l8r2", "vbus20ov")]
L8_B = [("l8gnd", "gnd002"), ("l8r2", "fans12"), ("l8r2", "panel5v"), ("l8r2", "ph4")]
MINE_B = [("l8r2", "fans12"), ("l8r2", "panel5v"), ("l8r2", "ph4")]
MAINPB = "v2/docs/records/d8dec31/apply_gen_sch_a_mainpb.py"
HELD = [("v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf", "3cfe41fef1407b85abaaee1e27a95ac3cf2cb1bdf218209b8578a835c4c9497f")]

INPUTS = [
    "v2/ecad/tools/gen_sch_a.py", "v2/ecad/tools/gen_sch_b.py", "v2/ecad/tools/gen_sch_c.py", "v2/ecad/tools/gen_sch_d.py",
    "v2/ecad/tools/lcsc_fill.py", "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md", "v2/docs/records/s120/README.md",
    "v2/docs/records/rv-pwr/pwr_budget.py", "v2/docs/ASSEMBLY.md", "v2/ecad/tools/pcb_interfaces.yaml",
    "v2/vendor/power/ti-tps61089-boost.pdf", "v2/vendor/power/tps2596.pdf", "v2/vendor/power/littelfuse-smcj-series-tvs.pdf",
    "v2/vendor/connectors/jst-ph-catalogue.pdf", "v2/vendor/connectors/wurth-wr-cab-ribbon-63912615521cab.pdf",
    "v2/vendor/connectors/wurth-wr-bhd-idc-socket-61202623021.pdf", "v2/vendor/power/ti-csd19532q5b-n-fet.pdf",
    "v2/docs/records/l8r2/inputs/l7pwr-cooler-identity-2087060b.md", "v2/docs/records/l8r2/inputs/l5r2-findings-and-rows-6902db8f.md",
    "v2/docs/records/l8r2/inputs/SOURCES.txt", "v2/docs/records/l8r2/check_l8r2_netlist.py", "v2/docs/records/l8r2/fetch_held_back.py",
    MAINPB, "v2/docs/records/d8dec31/genpatch.py", "v2/docs/records/d8dec31/netread.py", NET_A,
    "v2/docs/PANEL.md", "v2/ecad/tools/gen_sch_c.py", "v2/vendor/ti/ti-pca9555.pdf", "v2/docs/records/l8r2/apply_gen_sch_c_pibtn.py",
    "v2/docs/records/l8r2/inputs/fw-panel-F01-42c27369.md", "v2/docs/records/l8r2/inputs/l6r2-apply_gen_sch_c_lcsc-7633ae0a.py",
    "v2/docs/records/l8r2/inputs/l6r2-l6r2_apply-7633ae0a.py",
] + ["v2/docs/records/%s/apply_gen_sch_a_%s.py" % rn for rn in POWER_A + L8_A] + ["v2/docs/records/%s/apply_gen_sch_b_%s.py" % rn for rn in L8_B]
L6_C = ("v2/docs/records/l8r2/inputs/l6r2-apply_gen_sch_c_lcsc-7633ae0a.py", "v2/docs/records/l8r2/inputs/l6r2-l6r2_apply-7633ae0a.py")
PIBTN = "v2/docs/records/l8r2/apply_gen_sch_c_pibtn.py"

# ---------------------------------------------------------------------------------------------------------------- the figures
# Classes: MAKER (printed in a held sheet), INFERRED (derived from printed figures under a stated assumption), ASSUMPTION (a figure
# no held document gives), BOUND (a limit this record states and holds the design to).
F = {
    # item 1: TI SLVSD38C (TPS61089)
    "vref": ((1.188, 1.212, 1.236), "MAKER", "TPS61089 VREF, PWM mode (SLVSD38C 7.5)"),
    "ifb": (100e-9, "MAKER", "TPS61089 FB leakage at most 100 nA (SLVSD38C 7.5)"),
    "r1": (88.7e3, "BOUND", "FB top 88.7 k 1 %"), "r2": (10.0e3, "BOUND", "FB bottom 10 k 1 %"), "rtol": (0.01, "BOUND", "1 % resistors"),
    "rfreq": (301e3, "BOUND", "FSW resistor 301 k"), "cfreq": (24e-12, "MAKER", "Equation 3: CFREQ 24 pF"), "tdel": (86e-9, "MAKER", "Equation 3: tDELAY 86 ns"),
    "vin_nom": (5.1, "BOUND", "the slot rail +5V_Sn, 5.1 V nominal (gen_sch_b.py)"), "vin_min": (4.9, "BOUND", "the slot rail at its low end at board B, 4.9 V"),
    "eta_lo": (0.80, "ASSUMPTION", "TI's advice (9.2.2.5): a low efficiency for the inductor's worst case"),
    "eta": (0.85, "ASSUMPTION", "the step-up's efficiency at 0.17 A for the budget"),
    "ifan": (0.17, "MAKER", "9WPA0412P6G001 rated current 0.17 A (Sanyo Denki's page, inputs/)"),
    "pfan": (2.0, "MAKER", "9WPA0412P6G001 rated input 2.0 W (Sanyo Denki's page, inputs/)"),
    "vfan": ((10.8, 13.2), "MAKER", "9WPA0412P6G001 operating range (Sanyo Denki's page, inputs/)"),
    "l": (4.7e-6, "MAKER", "XAL6060-472ME 4.7 uH, Isat 11 A (board A's own part)"), "ltol": (0.30, "MAKER", "TI's -30 % for the worst case (9.2.2.5)"),
    "isat": (11.0, "MAKER", "XAL6060-472ME Isat 11 A"), "ilim": ((7.3, 8.1, 8.9), "MAKER", "TPS61089 ILIM at RILIM 127 k (SLVSD38C 7.5)"),
    "fsw_tol": (0.10, "ASSUMPTION", "fsw -10 % for the ripple (the sheet prints only typical rows)"),
    "co_eff": (33e-6, "ASSUMPTION", "3 x 22 uF 25 V X7R 1210 at 12 V, 50 % under DC bias (no curve held)"),
    "rsense": (0.08, "MAKER", "Equation 11: Rsense 0.08 Ohm"), "gea": (190e-6, "MAKER", "GEA 190 uS (SLVSD38C 7.5)"),
    "resr": (0.005, "ASSUMPTION", "the ceramic output bank's ESR 5 mOhm"), "fc": (10e3, "BOUND", "the chosen crossover 10 kHz"),
    "r5": (23.7e3, "BOUND", "COMP resistor 23.7 k (E96)"), "c5": (47e-9, "BOUND", "COMP capacitor 47 nF"),
    "ovp": ((12.7, 13.6), "MAKER", "TPS61089 output OVP 12.7 to 13.6 V (SLVSD38C 7.5)"),
    # TPS2596 (SLVSET8A)
    "ilim_rows": (((909.0, 0.949, 1.005, 1.051), (453.0, 1.83, 2.004, 2.147), (3830.0, 0.224, 0.247, 0.269)), "MAKER", "TPS2596 ILIM rows (SLVSET8A 7.5)"),
    "vovlo_r": ((1.17, 1.22), "MAKER", "VOVLO(R) 1.17 to 1.22 V (SLVSET8A 7.5)"), "vovlo_f": ((1.08, 1.13), "MAKER", "VOVLO(F) 1.08 to 1.13 V"),
    "ron_lo": (0.1434, "MAKER", "RON at VIN under 4 V, -40 to 125 C, at most 143.4 mOhm (SLVSET8A 7.5)"),
    "rilm_fan": (1870.0, "BOUND", "the coolers' eFuse ILM 1.87 k"), "rilm_pnl": (604.0, "BOUND", "PANEL_5V's eFuse ILM 604 Ohm"),
    "rilm_d8": (3830.0, "BOUND", "board D's 3.3 V eFuse ILM 3.83 k (the printed row)"),
    # item 2
    "smcj22a": ((22.0, 24.40, 26.90, 35.5, 42.3, 6.5), "MAKER", "SMCJ22A VRWM 22.0, VBR 24.40 to 26.90 at 1 mA, VC 35.5 at IPP 42.3 A; PD 6.5 W on an infinite heat sink at TL 50 C (Littelfuse SMCJ, 11/20/15)"),
    "brk_oc": ((6.364, 7.136), "INFERRED", "board E's entry breaker trip 6.364 to 7.136 A (L4-E11 3c)"),
    "vin_service": ((9.0, 36.0), "MAKER", "REQ-015's vehicle input 9 to 36 V in service"),
    "ovr": ((1.16, 1.20), "MAKER", "TPS48110 V(OVR) 1.16 to 1.20 V (SLUSEE5E 6.5)"), "ovf": ((1.10, 1.13), "MAKER", "V(OVF) 1.10 to 1.13 V"),
    "iov": (300e-9, "MAKER", "I(OV) at most 300 nA"), "uvlor": ((1.16, 1.20), "MAKER", "V(UVLOR) 1.16 to 1.20 V"),
    "rt_ov": (200e3, "BOUND", "OV top 200 k 0.1 %"), "rb_ov": (10.0e3, "BOUND", "OV bottom 10.0 k 0.1 %"), "tol_ov": (0.001, "BOUND", "0.1 % resistors"),
    "rt_en": (33.2e3, "BOUND", "EN top 33.2 k 1 %"), "rb_en": (10.0e3, "BOUND", "EN bottom 10.0 k 1 %"),
    "bus_bound": (23.40, "INFERRED", "VBUS20's in-service bound (records/s120 section 4)"),
    "u3_abs": (32.0, "MAKER", "U3's VBUS, ACP, ACN absolute 32 V (SLUSE66A p.8)"), "u3_rec": (26.0, "MAKER", "U3's recommended 26 V and ACOV's 26.0 V minimum"),
    "q7_abs": (30.0, "MAKER", "Q7's VDS 30 V (SLPS526); Q8's VSD 1.0 V (SLPS516) while the charger switches"),
    "c_bank": (1.584e-3 * 0.8, "INFERRED", "the six EEHZK1V331P at -20 %, 1.267 mF, ceramics not counted (records/s120 section 4)"),
    "c_vin": (32e-6, "INFERRED", "board A's VIN_RAW 20 to 32 uF (the restart guard's comment, gen_sch_a.py)"),
    "vin_ov": (41.22, "INFERRED", "board E's entry OV maximum 41.22 V (L4-E11 3c)"), "uv_fall": (8.08, "INFERRED", "U34's UV fall 8.08 V nominal"),
    "e_l1_first": (12.57e-3, "INFERRED", "L1's first-on-time energy, s120's MODEL term (records/s120 section 4)"),
    "i_brk_sc": (13.87, "INFERRED", "board E's short-circuit trip at most 13.87 A (L4-E11 3c)"),
    # item 3
    "i_cond": (1.0, "MAKER", "Wurth WR-CAB 63912615521CAB and WR-BHD 61202623021: 1 A per conductor and contact at most (inputs/ R2-03)"),
    "f1": ((1.10, 2.20), "MAKER", "MF-MSMF110-2 hold 1.10 A, trip 2.20 A at 23 C (inputs/ R2-04)"),
    "c_peak": (1.0, "BOUND", "board C's +5V declared peak 1.0 A (gen_sch_c.py)"), "d_peak": (0.10, "BOUND", "board D's +3V3 declared peak 0.10 A (gen_sch_d.py)"),
    "mismatch": (0.20, "ASSUMPTION", "a 20 % resistance mismatch between the two PANEL_5V conductors"),
    "rt_pnl": (42.2e3, "BOUND", "PANEL_5V eFuse OVLO top 42.2 k 1 %"), "rt_d8": (30.1e3, "BOUND", "board D eFuse OVLO top 30.1 k 1 %"),
    "rb_ovlo": (10.0e3, "BOUND", "OVLO bottom 10 k 1 %"), "v5dev": (5.1, "BOUND", "+5V_DEV 5.1 V"), "v3": (3.3, "BOUND", "+3V3 3.3 V"),
    "budget_fan": ((0.36, 0.51, 0.56), "INFERRED", "pwr_budget.py's cooler row per slot, a representative 30 mm 5 V fan (records/rv-pwr)"),
    "eta_a": (0.89, "ASSUMPTION", "board A's 12 V buck-boost for choice (b)"), "eta_slot": (0.90, "ASSUMPTION", "board A's slot converters"),
}
V = {k: v for k, (v, _c, _w) in F.items()}


def eq7(r):
    return 903.0 / r + 0.0112


def ilim_window(r):
    """TPS2596 Equation 7 nominal; the tolerance of the printed row when r is one, else the wider of the two neighbouring rows."""
    rows = sorted(V["ilim_rows"], key=lambda x: x[0])
    for rr, lo, ty, hi in rows:
        if abs(rr - r) < 0.5:
            return lo, ty, hi, "printed row"
    lo_side = [x for x in rows if x[0] < r]; hi_side = [x for x in rows if x[0] > r]
    nb = [lo_side[-1]] if lo_side else []
    nb += [hi_side[0]] if hi_side else []
    dn = max((x[2] - x[1]) / x[2] for x in nb); up = max((x[3] - x[2]) / x[2] for x in nb)
    n = eq7(r)
    return n * (1 - dn), n, n * (1 + up), "INFERRED (the wider neighbouring row's tolerance)"


def divider(rt, rb, tol):
    lo = 1 + rt * (1 - tol) / (rb * (1 + tol)); hi = 1 + rt * (1 + tol) / (rb * (1 - tol))
    return lo, 1 + rt / rb, hi


def item1():
    o = {}
    vref = V["vref"]; lo, nom, hi = divider(V["r1"], V["r2"], V["rtol"])
    o["vout"] = (vref[0] * lo - V["ifb"] * V["r1"], vref[1] * nom, vref[2] * hi + V["ifb"] * V["r1"])
    o["fsw"] = 1.0 / (V["rfreq"] * V["cfreq"] / 4.0 + V["tdel"] * o["vout"][1] / V["vin_nom"])
    o["d"] = 1 - V["vin_nom"] * V["eta"] / o["vout"][1]
    def peak(iout):
        vin, vo = V["vin_min"], o["vout"][2]
        idc = vo * iout / (vin * V["eta_lo"])
        l = V["l"] * (1 - V["ltol"]); f = o["fsw"] * (1 - V["fsw_tol"])
        ipp = 1.0 / (l * (1.0 / (vo - vin) + 1.0 / vin) * f)
        return idc, ipp, idc + ipp / 2
    o["peak_rated"] = peak(V["ifan"])
    o["efuse"] = ilim_window(V["rilm_fan"])
    o["peak_fault"] = peak(o["efuse"][2])
    ro = o["vout"][1] / V["ifan"]
    o["ro"] = ro
    o["frhpz"] = ro * (1 - o["d"]) ** 2 / (2 * math.pi * V["l"])
    o["fc_max"] = min(o["fsw"] / 10, o["frhpz"] / 5)
    o["r5_calc"] = 2 * math.pi * o["vout"][1] * V["rsense"] * V["fc"] * V["co_eff"] / ((1 - o["d"]) * V["vref"][1] * V["gea"])
    o["c5_calc"] = ro * V["co_eff"] / (2 * V["r5"])
    o["c6_calc"] = V["resr"] * V["co_eff"] / V["r5"]
    o["fc_at"] = {co: V["fc"] * (V["r5"] / o["r5_calc"]) * (V["co_eff"] / co) for co in (22e-6, 33e-6, 66e-6)}
    dlo, dnom, dhi = divider(100e3, 10e3, 0.01)
    o["ovlo"] = (V["vovlo_r"][0] * dlo, V["vovlo_r"][1] * dhi)
    o["ovlo_margin"] = o["ovlo"][0] - o["vout"][2]
    o["fan_in"] = o["vout"][0] >= V["vfan"][0] and o["vout"][2] <= V["vfan"][1]
    pin = V["pfan"] / V["eta"]
    o["slot_w"] = pin; o["slot_a"] = pin / V["vin_nom"]; o["slot_a_min"] = pin / V["vin_min"]
    o["a_vbat"] = 3 * pin / V["eta_slot"]; o["b_vbat"] = 3 * V["pfan"] / V["eta_a"]
    o["a_minus_b"] = o["a_vbat"] - o["b_vbat"]
    return o


def item2():
    o = {}
    vrwm, vbr_lo, vbr_hi, vc, ipp, pd = V["smcj22a"]
    o["smcj_v_at_trip"] = vbr_hi + (vc - vbr_hi) * V["brk_oc"][0] / ipp
    o["smcj_p_at_trip"] = o["smcj_v_at_trip"] * V["brk_oc"][0]
    o["smcj_p_1a"] = (vbr_hi + (vc - vbr_hi) * 1.0 / ipp) * 1.0
    o["smcj_ratio"] = o["smcj_p_at_trip"] / pd
    o["band_in_service"] = vbr_lo < V["vin_service"][1] - 0.8
    lo, nom, hi = divider(V["rt_ov"], V["rb_ov"], V["tol_ov"])
    rth = V["rt_ov"] * V["rb_ov"] / (V["rt_ov"] + V["rb_ov"])
    dv = V["iov"] * rth * nom
    o["trip"] = (V["ovr"][0] * lo - dv, V["ovr"][1] * hi + dv)
    o["release"] = (V["ovf"][0] * lo - dv, V["ovf"][1] * hi + dv)
    o["over_bound"] = o["trip"][0] - V["bus_bound"]
    o["under_rec"] = V["u3_rec"] - o["trip"][1]
    elo, enom, ehi = divider(V["rt_en"], V["rb_en"], 0.01)
    o["en_on"] = (V["uvlor"][0] * elo, V["uvlor"][1] * ehi)
    c1, c2, v1, v2 = V["c_vin"], V["c_bank"], V["vin_ov"], o["trip"][1]
    l1e = 0.5 * 12e-6 * V["i_brk_sc"] ** 2
    o["after_q2"] = math.sqrt(((v2 ** 2) + c1 * v1 ** 2 / c2) / (1 + c1 / c2) + 2 * l1e / c2)
    e_fb = 0.5 * c1 * (v1 ** 2 - V["uv_fall"] ** 2) + V["e_l1_first"]
    o["after_fb"] = math.sqrt(v2 ** 2 + 2 * e_fb / c2)
    o["margin_abs"] = V["u3_abs"] - max(o["after_q2"], o["after_fb"])
    o["margin_q7"] = V["q7_abs"] - (max(o["after_q2"], o["after_fb"]) + 1.0)
    o["over_rec"] = max(o["after_q2"], o["after_fb"]) - V["u3_rec"]
    return o


def item3():
    o = {}
    o["pnl"] = ilim_window(V["rilm_pnl"])
    o["pnl_cond_eq"] = o["pnl"][2] / 2
    o["pnl_cond_mm"] = o["pnl"][2] * (1 + V["mismatch"]) / (2 + V["mismatch"])
    o["old_cond"] = V["f1"][1] / 2
    lo, nom, hi = divider(V["rt_pnl"], V["rb_ovlo"], 0.01)
    o["pnl_ovlo"] = (V["vovlo_r"][0] * lo, V["vovlo_r"][1] * hi); o["pnl_pin"] = (V["v5dev"] / hi, V["v5dev"] / lo)
    o["d8"] = ilim_window(V["rilm_d8"])
    lo, nom, hi = divider(V["rt_d8"], V["rb_ovlo"], 0.01)
    o["d8_ovlo"] = (V["vovlo_r"][0] * lo, V["vovlo_r"][1] * hi); o["d8_pin"] = (V["v3"] / hi, V["v3"] * 1.03 / lo)
    o["d8_drop"] = V["ron_lo"] * V["d_peak"]
    return o


# ---------------------------------------------------------------------------------------------------------------- the drafts
def item4():
    """The PI button's input on U1 P1.3 (record l8r2, F-01): R57 10 k to +3V3, C27 100 nF to GND."""
    r, c, vcc = 10e3, 100e-9, 3.3
    tau = r * c
    vih, vil = 0.7 * vcc, 0.3 * vcc            # PCA9555 VIH 0.7 x VCC, VIL 0.3 x VCC (TI SCPS131J 6.3), MAKER
    return {"tau": tau, "t_release": -tau * math.log(1 - 0.7), "vih": vih, "vil": vil, "i_press": vcc / r}


def l6_scratch(d):
    """Layer 6's board C draft and its helper side by side in a scratch git repository (the helper asks git for its top level)."""
    sc = os.path.join(d, "l6c"); os.makedirs(sc, exist_ok=True)
    shutil.copy(os.path.join(ROOT, L6_C[0]), os.path.join(sc, "apply_gen_sch_c_lcsc.py"))
    shutil.copy(os.path.join(ROOT, L6_C[1]), os.path.join(sc, "l6r2_apply.py"))
    subprocess.run(["git", "init", "-q", sc], capture_output=True, check=True)
    return os.path.join(sc, "apply_gen_sch_c_lcsc.py")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def draft(rec, name, board):
    return os.path.join(RECS, rec, "apply_gen_sch_%s_%s.py" % (board, name))


def run(script, target):
    r = subprocess.run([sys.executable, "-B", script, target, "--write"], capture_output=True)
    return r.returncode, (r.stderr.decode("utf-8", "replace").strip().splitlines() or [""])[-1]


def run_mainpb(target):
    r = subprocess.run([sys.executable, "-B", os.path.join(ROOT, MAINPB), target, os.path.join(ROOT, NET_A)], capture_output=True)
    out = r.stdout.decode("utf-8", "replace").strip().splitlines()
    return r.returncode, (out[-1] if out else (r.stderr.decode("utf-8", "replace").strip().splitlines() or [""])[-1])


STMT = re.compile(r'^\s*(ic|part|c|r|tp|nfet|vh2|synth|q|esd|efuse)\(\s*"([A-Z][A-Z0-9_]*)"')
TOKEN = re.compile(r"\b([RCDLQUH]\d{1,3}|J_[A-Z0-9]+|TP\d{1,3})\b(?!-)")


def strip_comments(s):
    return "\n".join("" if l.lstrip().startswith("#") else l.split("#")[0] for l in s.splitlines())


def literal_calls(text):
    """[(helper, ref)] of every call in part-call position whose first argument is a literal, comments stripped."""
    out = []
    for line in strip_comments(text).splitlines():
        for stmt in line.split(";"):
            m = STMT.match(stmt)
            if m:
                out.append(m.groups())
    return out


def tokens(text):
    """Designator strings ("R221") where the generator DRAWS or LISTS a part: the first argument of a call, or an element of a list
    or tuple, read with ast. A note that mentions a reference is prose and counts for nothing, and a dict key (a table that names
    parts that exist, as Layer 6's LCSC table does) is not an addition."""
    out = set()
    for n in ast.walk(ast.parse(text)):
        cands = []
        if isinstance(n, ast.Call) and n.args:
            cands.append(n.args[0])
        elif isinstance(n, (ast.List, ast.Tuple)):
            cands.extend(n.elts)
        for c in cands:
            if isinstance(c, ast.Constant) and isinstance(c.value, str) and TOKEN.fullmatch(c.value):
                out.add(c.value)
    return out


def declared_adds(script):
    """The designators a draft declares it adds (its ADDS tuple, which its own refusal checks absent from the target)."""
    if not script:
        return set()
    sp = importlib.util.spec_from_file_location("adds_" + os.path.basename(script)[:-3], script)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return set(getattr(m, "ADDS", ()))


def added(before, after, script=None):
    cb = {r for _h, r in literal_calls(before)}; ca = {r for _h, r in literal_calls(after)}
    return (ca - cb) | (tokens(after) - tokens(before)) | declared_adds(script)


def compose(gen, seq, d, tag, mainpb_last=False):
    p = os.path.join(d, tag + ".py"); shutil.copy(gen, p); res = []
    for s in seq:
        rc, msg = run(s, p)
        res.append((os.path.relpath(s, RECS), "OK" if rc == 0 else "REFUSED (%s)" % msg))
        if rc:
            return p, res
    if mainpb_last:
        rc, msg = run_mainpb(p)
        res.append(("d8dec31/apply_gen_sch_a_mainpb.py", "OK (%s)" % msg if rc == 0 else "REFUSED (%s)" % msg))
    return p, res


def designators(gen, seq, d, tag, mainpb_last=False):
    p = os.path.join(d, tag + ".py"); shutil.copy(gen, p)
    before = open(p, encoding="utf-8").read(); out = {}
    for s in seq + ([None] if mainpb_last else []):
        rc = run_mainpb(p)[0] if s is None else run(s, p)[0]
        after = open(p, encoding="utf-8").read()
        out["d8dec31/apply_gen_sch_a_mainpb.py" if s is None else os.path.relpath(s, RECS)] = added(before, after, s) if rc == 0 else None
        before = after
    return p, out


def duplicates(text):
    seen = {}
    for _h, ref in literal_calls(text):
        seen[ref] = seen.get(ref, 0) + 1
    return sorted(r for r, n in seen.items() if n > 1)


def main():
    w = sys.stdout.write
    w("l8r2_drafts: the Layer 8 record l8r2 (round 2): the known engineering defects a desk design corrects (MESHSAT-1357)\n")
    w("prototype design; nothing built, powered or measured; nothing applied to the tree\n\n1. INPUTS, pinned by sha256\n")
    miss = [p for p in INPUTS if not os.path.isfile(os.path.join(ROOT, p))]
    if miss:
        sys.stderr.write("l8r2_drafts: inputs missing: %s\n" % miss)
        return 3
    for p in INPUTS:
        w("%s %s\n" % (sha(os.path.join(ROOT, p))[:16], p))
    for p, h in HELD:
        w("%s %s (held back by its terms, fetched by fetch_held_back.py)\n" % (h[:16], p))

    w("\n   the figures and their classes\n")
    for k, (v, c, why) in F.items():
        w("   %-12s %-34s %-10s %s\n" % (k, v if not isinstance(v, float) else "%g" % v, c, why))

    o = item1()
    w("\n2. ITEM 1, BOARD B'S COOLERS (E11-40, R-190): a per-slot TPS61089 step-up to 12 V behind an eFuse\n")
    w("  output %.3f / %.3f / %.3f V (VREF and the 1 %% divider, FB leakage), inside the fan's %.1f to %.1f V: %s\n" % (o["vout"] + V["vfan"] + ("YES" if o["fan_in"] else "NO",)))
    w("  fsw %.1f kHz at 5.1 V in (Equation 3); duty %.4f at efficiency %.2f; RO %.1f Ohm at the rated 0.17 A\n" % (o["fsw"] / 1e3, o["d"], V["eta"], o["ro"]))
    w("  inductor at the rated current: DC %.3f A, ripple %.3f A, peak %.3f A (4.9 V in, the highest output, L -30 %%, fsw -10 %%, efficiency 0.80)\n" % o["peak_rated"])
    w("  inductor at the eFuse's highest limit %.3f A: DC %.3f A, ripple %.3f A, peak %.3f A; ILIM %.1f to %.1f A over both, Isat %.1f A over ILIM's %.1f A maximum\n"
      % ((o["efuse"][2],) + o["peak_fault"] + (V["ilim"][0], V["ilim"][2], V["isat"], V["ilim"][2])))
    w("  RHP zero %.0f kHz; the crossover limit min(fsw/10, fRHPZ/5) %.1f kHz; the chosen 10 kHz under it\n" % (o["frhpz"] / 1e3, o["fc_max"] / 1e3))
    w("  COMP: Equation 17 gives R5 %.1f k at CO %.0f uF effective (ASSUMPTION), drawn 23.7 k; Equation 18 C5 %.1f nF, drawn 47 nF; Equation 19 C6 %.1f pF, under 10 pF: open\n"
      % (o["r5_calc"] / 1e3, V["co_eff"] * 1e6, o["c5_calc"] * 1e9, o["c6_calc"] * 1e12))
    w("  the crossover with R5 23.7 k against the effective output capacitance: %s\n" % ", ".join("%.0f uF %.1f kHz" % (co * 1e6, f / 1e3) for co, f in sorted(o["fc_at"].items())))
    w("  eFuse ILM 1.87 k: %.3f / %.3f / %.3f A, %s; OVLO 100 k over 10 k cuts at %.2f to %.2f V, %.2f V over the rail's highest; the boost's own OVP %.1f to %.1f V\n"
      % (o["efuse"][:3] + (o["efuse"][3], o["ovlo"][0], o["ovlo"][1], o["ovlo_margin"]) + V["ovp"]))
    w("  power, the fan row: pwr_budget.py's cooler row %.2f / %.2f / %.2f W per slot (a representative 30 mm 5 V fan, not the pick); the pick prints %.1f W at full speed\n"
      % (V["budget_fan"] + (V["pfan"],)))
    w("  choice (a), a step-up per slot (SELECTED): %.3f W on +5V_Sn per slot at full speed, %.3f A at 5.1 V (%.3f A at 4.9 V), +%.3f W of conversion per slot; the three %.2f W at VBAT behind the slot converters\n"
      % (o["slot_w"], o["slot_a"], o["slot_a_min"], o["slot_w"] - V["pfan"], o["a_vbat"]))
    w("  choice (b), one 12 V feed from board A over the bay harness: the three %.2f W at VBAT; (b) is %.2f W lower at full speed, %.2f W at the budget's 0.56 W a fan\n"
      % (o["b_vbat"], o["a_minus_b"], o["a_minus_b"] * 0.56 / V["pfan"]))

    t = item2()
    w("\n3. ITEM 2, VBUS20 AGAINST U2's SINGLE FAULTS (S-111, R-48)\n")
    w("  the SMCJ22A: standoff %.1f V over the regulated band's 20.96 V; breakdown %.2f to %.2f V, inside REQ-015's 9 to 36 V in service: %s\n"
      % (V["smcj22a"][0], V["smcj22a"][1], V["smcj22a"][2], "YES" if t["band_in_service"] else "NO"))
    w("  a source holding the bus under the entry breaker's 6.364 A: the clamp at %.2f V carries %.1f W, %.0f times its %.1f W on an infinite heat sink; at 1 A, %.1f W: REJECTED\n"
      % (t["smcj_v_at_trip"], t["smcj_p_at_trip"], t["smcj_ratio"], V["smcj22a"][5], t["smcj_p_1a"]))
    w("  the cut-off: OV trip %.2f to %.2f V of VBUS20 (V(OVR), the 0.1 %% divider, I(OV)), %.2f V over the in-service bound %.2f V, %.2f V under U3's recommended %.1f V\n"
      % (t["trip"] + (t["over_bound"], V["bus_bound"], t["under_rec"], V["u3_rec"])))
    w("  release %.2f to %.2f V; EN on at %.2f to %.2f V of VIN_RAW_IN, under U34's 8.08 V UV\n" % (t["release"] + t["en_on"]))
    w("  after the cut, a shorted Q2: VIN_RAW's %.0f uF from %.2f V into the bank (%.3f mF) with L1 at %.2f A: at most %.2f V\n"
      % (V["c_vin"] * 1e6, V["vin_ov"], V["c_bank"] * 1e3, V["i_brk_sc"], t["after_q2"]))
    w("  after the cut, an open FB: U2 pumping VIN_RAW's %.0f uF down to %.2f V and L1's %.2f mJ into the bank: at most %.2f V\n"
      % (V["c_vin"] * 1e6, V["uv_fall"], V["e_l1_first"] * 1e3, t["after_fb"]))
    w("  margins: %.2f V under U3's absolute %.1f V; %.2f V under Q7's %.1f V with Q8's 1.0 V; at most %.2f V over U3's recommended %.1f V, for the event\n"
      % (t["margin_abs"], V["u3_abs"], t["margin_q7"], V["q7_abs"], t["over_rec"], V["u3_rec"]))

    u = item3()
    w("\n4. ITEM 3, LAYER 5'S ROUND 2 FINDINGS\n")
    w("  L5R2-F03, PANEL_5V: as drawn F1 lets up to %.2f A a conductor (its %.2f A trip over two); with U901 (ILM 604 Ohm) %.3f / %.3f / %.3f A, %s;\n"
      "    a conductor %.3f A (equal split) or %.3f A (20 %% mismatch), under the %.1f A; the lowest limit %.3f A over board C's %.1f A peak\n"
      % (u["old_cond"], V["f1"][1], u["pnl"][0], u["pnl"][1], u["pnl"][2], u["pnl"][3], u["pnl_cond_eq"], u["pnl_cond_mm"], V["i_cond"], u["pnl"][0], V["c_peak"]))
    w("    its OVLO 42.2 k over 10 k: the pin at %.3f to %.3f V on 5.1 V (0.5 to 2 V recommended); cut at %.2f to %.2f V\n" % (u["pnl_pin"] + u["pnl_ovlo"]))
    w("  L5R2-F05, board D's 3.3 V: U44 (ILM 3.83 k) %.3f / %.3f / %.3f A, %s; %.1f times board D's %.2f A peak, %.0f %% of the conductor's 1 A at most; drop %.1f mV at the peak\n"
      % (u["d8"][0], u["d8"][1], u["d8"][2], u["d8"][3], u["d8"][0] / V["d_peak"], V["d_peak"], 100 * u["d8"][2] / V["i_cond"], u["d8_drop"] * 1e3))
    w("    its OVLO 30.1 k over 10 k: the pin at %.3f to %.3f V on 3.3 V (+3 %%); cut at %.2f to %.2f V\n" % (u["d8_pin"] + u["d8_ovlo"]))
    w("  L5R2-F04, J_QMX and J_CAM: PH1x4 is a 2.54 mm pin header in board B's table; ASSEMBLY.md and IF-LID-HF say JST PH 1x4; corrected to PH4,\n"
      "    Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical with C131334 (B4B-PH-K-S), the part boards A (J_USBW) and D (J_USB3) carry\n")

    with tempfile.TemporaryDirectory() as d:
        pa = [draft(r, n, "a") for r, n in POWER_A]; l8a = [draft(r, n, "a") for r, n in L8_A]; mya = [draft(r, n, "a") for r, n in MINE_A]
        w("\n5. COMPOSITION ON BOARD A (scratch copies of gen_sch_a.py; OK = applied and the result parses)\n")
        _p, res = compose(GEN_A, pa + l8a, d, "a_fwd", mainpb_last=True)
        w("  L4-E9's power order, l8gnd's two, this record's two, then d8dec31's mainpb:\n")
        for s, v in res: w("    %-42s %s\n" % (s, v))
        _p, res = compose(GEN_A, mya + pa + l8a[:2], d, "a_rev", mainpb_last=True)
        w("  this record's two first, then the power order, l8gnd's two and mainpb (every anchor of theirs still applies after these):\n")
        for s, v in res: w("    %-42s %s\n" % (s, v))
        w("  each power draft alone after this record's two (the bank after r12, which it requires):\n")
        r12 = [x for x in pa if x.endswith("_r12.py")]
        for s in pa:
            p = os.path.join(d, "alone_" + os.path.basename(s)); shutil.copy(GEN_A, p)
            ok = all(run(m, p)[0] == 0 for m in mya + (r12 if s.endswith("_bank.py") else []))
            rc, msg = run(s, p)
            w("    %-42s %s\n" % (os.path.relpath(s, RECS), "OK" if ok and rc == 0 else "REFUSED (%s)" % msg))
        _p, res = compose(GEN_A, l8a[::-1], d, "a_l8rev")
        w("  the four Layer 8 drafts of board A in reverse order: %s\n" % ("OK" if all(v == "OK" for _s, v in res) else res))
        pb = [draft(r, n, "b") for r, n in L8_B]
        w("\n6. COMPOSITION ON BOARD B (no power draft targets gen_sch_b.py)\n")
        for tag, seq in (("forward", pb), ("reverse", pb[::-1])):
            _p, res = compose(GEN_B, seq, d, "b_" + tag)
            w("  %s: %s\n" % (tag, "; ".join("%s %s" % (os.path.basename(s)[13:-3], v) for s, v in res)))
        for s in pb:
            _p, res = compose(GEN_B, [s], d, "b_alone_" + os.path.basename(s)[:-3])
            w("  alone %-30s %s\n" % (os.path.relpath(s, RECS), res[0][1]))

        w("\n7. DESIGNATORS\n")
        pA, addA = designators(GEN_A, pa + l8a, d, "a_desig", mainpb_last=True)
        for k, v in addA.items(): w("  A %-42s %s\n" % (k, ", ".join(sorted(v)) if v else "none"))
        pB, addB = designators(GEN_B, pb, d, "b_desig")
        for k, v in addB.items(): w("  B %-42s %s\n" % (k, ", ".join(sorted(v)) if v else "none"))
        for tag, add in (("A", addA), ("B", addB)):
            names = sorted(add); clash = []
            for i, x in enumerate(names):
                for y in names[i + 1:]:
                    both = (add[x] or set()) & (add[y] or set())
                    if both: clash.append("%s and %s: %s" % (x, y, sorted(both)))
            w("  board %s pairwise intersections: %s\n" % (tag, "none (DISJOINT)" if not clash else "; ".join(clash)))
        ta, tb = open(pA, encoding="utf-8").read(), open(pB, encoding="utf-8").read()
        w("  literal designators drawn twice in the composed board A generator: %s\n" % (duplicates(ta) or "none"))
        w("  literal designators drawn twice in the composed board B generator: %s\n" % (duplicates(tb) or "none"))
        w("  board B's 700 and 900 blocks against every designator the generator builds from a base: %s\n"
          % ("free" if not re.search(r'"[RCQULD]%d" % \(\s*[79]\d\d\b', open(GEN_B, encoding="utf-8").read()) else "TAKEN"))

    w("\n7b. ITEM 4, BOARD C'S PI BUTTON (the panel firmware's F-01): PIJ2_A2 on U1 P1.3 (PI_BTN_n)\n")
    q = item4()
    w("  R57 10 k to +3V3 with C27 100 nF to GND: tau %.2f ms; a release reaches VIH (%.2f V, 0.7 x VCC) after %.2f ms; a press pulls under VIL (%.2f V)\n"
      "    through FB3 and the contact; the pull-up's %.2f mA through the closed contact\n" % (q["tau"] * 1e3, q["vih"], q["t_release"] * 1e3, q["vil"], q["i_press"] * 1e3))
    with tempfile.TemporaryDirectory() as d:
        l6 = l6_scratch(d); pi = os.path.join(ROOT, PIBTN); res = {}
        for tag, seq in (("l6 then pibtn", [l6, pi]), ("pibtn then l6", [pi, l6])):
            p = os.path.join(d, tag.replace(" ", "_") + ".py"); shutil.copy(os.path.join(TOOLS, "gen_sch_c.py"), p)
            rcs = [subprocess.run([sys.executable, "-B", x, p, "--write"], capture_output=True).returncode for x in seq]
            res[tag] = (rcs, open(p, "rb").read())
            w("  %-16s %s\n" % (tag, "OK" if rcs == [0, 0] else "REFUSED %s" % rcs))
        w("  the two orders give the same generator: %s\n" % ("YES" if res["l6 then pibtn"][1] == res["pibtn then l6"][1] else "NO"))
        _p, addC = designators(os.path.join(TOOLS, "gen_sch_c.py"), [l6, pi], d, "c_desig")
        w("  designators: Layer 6's draft %s; this record's %s; intersection %s\n"
          % (", ".join(sorted(addC[os.path.relpath(l6, RECS)])) or "none", ", ".join(sorted(addC[os.path.relpath(pi, RECS)])),
             sorted(addC[os.path.relpath(l6, RECS)] & addC[os.path.relpath(pi, RECS)]) or "none (DISJOINT)"))
        w("  literal designators drawn twice in the composed board C generator: %s\n" % (duplicates(open(_p, encoding="utf-8").read()) or "none"))

    w("\n8. THE NETLIST CHECK (check_l8r2_netlist.py)\n")
    sp = importlib.util.spec_from_file_location("l8r2_check", os.path.join(HERE, "check_l8r2_netlist.py"))
    chk = importlib.util.module_from_spec(sp); sp.loader.exec_module(chk)
    buf = io.StringIO(); chk.run(chk.committed(ROOT), ROOT, buf)
    for l in buf.getvalue().splitlines(): w("  %s\n" % l)
    w("  on fixtures carrying the drafts (built in check_l8r2_netlist.py, not files of the tree):\n")
    for letter in ("a", "b", "c"):
        v, lines = chk.judge(letter, chk.read_netlist(chk.fixture(letter)))
        for l in lines: w("    %s\n" % l)
        w("    fixture %s: %s\n" % (letter.upper(), v))
    w("\nEND\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
