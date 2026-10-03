#!/usr/bin/env python3
"""l8r2_drafts.py: the Layer 8 record l8r2's figures and drafts, proved on scratch copies (MESHSAT-1357, 3 October 2026).

It prints, deterministically and without touching the tree:
  1. the inputs, each pinned by sha256 (the generators, every board A and board B draft in the tree, this record's drafts, the makers'
     sheets it reads, its inputs/ copies); the held-back TPS4811-Q1 sheet by the sha256 its fetch script checks;
  2. item 1, board B's coolers: the TPS61089 step-up from TI's equations, the eFuse's window, the slot power of the two choices;
  3. item 2, VBUS20's single faults: the clamp's power at the fault (rejected), the cut-off's window and the bus after the cut;
  4. item 3, Layer 5's round 2 findings: the PANEL_5V and board D 3.3 V limits per conductor, the J_QMX land;
  5. the composition on board A: L4-E9's power order (r12, guard, charger, r11, bank, r138, u17), l8gnd's two, this record's four, then
     d8dec31's mainpb LAST; this record's drafts first and then every other draft (their anchors still apply after these; round 4's
     slotlm after L4-E11's charger, whose anchor it rewrites); each power draft alone after this record's; the six Layer 8 drafts of
     board A in forward and reverse order;
  6. the composition on board B: l8gnd's GND-002 draft and this record's three in forward and reverse order, and each alone;
  7. the designators each draft adds on boards A and B, pairwise disjoint, and every literal designator in part-call position of the
     composed generators drawn once;
  8. the netlist check (check_l8r2_netlist.py) on the committed netlists (NOT DRAWN) and on fixtures carrying the drafts (DRAWN);
round 3 (branch fnd/l8r3 from set 28's 37bc2f1d, 3 October 2026):
  2b. item 1 re-decided on record l9pwr's figures, PARSED from its output (inputs/l9pwr_budget-38ef774c.txt): the slot rails and the
      device rail at HIGH in every state for each option, the slot rail's declared loads through intent.rail's own check, the
      efficiency round 2 typed, the bound's limit and what stands if it fails open;
  6b. the composition on board E: the change list's board E round (L4-POWER-ARCHITECTURE.md's table) with the pack return's draft;
  9. item 5, the pack path's return on boards A and E declared as rails (record l9stk's finding): the drafts' declarations evaluated by
     intent.py itself, their sources and loads on the committed netlists, the rules that then judge them;
  10. item 6, the energy chain's board E texts at 1 oz: the widths the declared ratings need (track_current.py), record l9stk's own
     widths parsed beside them, the apply script's runs, energy_chain.check before and after (identical).
round 4 (3 October 2026, the owner's focused check of L9P-F02):
  2c. the two margins of round 3 reconciled (state, boundary, voltage); the fan's input at 70 % PWM from the maker's catalogue rows
      (C1152B001 '25.10, held back) and what they do not print; the states of boot, reset, firmware failure and an open PWM lead; the
      coolers' airflow at 70 % against the approved thermal basis; the AP64500's junction by record l4e12's method and the maker's
      Figure 24; the correction (slots 1 and 3 on slot 2's LM5176 stage, apply_gen_sch_a_slotlm.py) with its margins in every state,
      its hottest FET's junction, the energy it costs and the composition's order constraint.
round 5 (4 October 2026, the collaborator's check astra-check-l9pf02-1, B1 to B3): section 2c corrected in place: the AP64500's
      drawn frequency (68 k on DS41979 Eq. 7, 1.47 MHz) and what stands without a curve there; the slot's ENVELOPE (the fan's 2.75 W
      bound at the step-up's 12.43 V top over its 0.80, every slot load at HIGH, board B's slot bucks at 500 kHz by
      apply_gen_sch_b_rt500.py) with the margins in every state, the start and a degraded fan; the declarations of both boards at
      5.63 A; the FET's sensitivity to the recovery charge; section 6 composes Layer 6's board B drafts with this record's.
round 6 (4 October 2026, the collaborator's recheck astra-check-l9pf02-2): the AP64500's Figure 24 reading a CONDITIONAL screen, no
      longer a bound; F5-03 corrected by apply_gen_sch_a_fb01.py (the 5.1 V stages' dividers at 0.1 %: 5.0019 to 5.1744 V); the
      slot leads declared at 6.6 A on both boards over the bounded start-up and fault envelope (the cooler branch's 1.80 A start
      bound, a 100 us average); the loop's least from VSNS unrounded; the junction screen over C4-1's whole steady matrix.
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
GEN_E = os.path.join(TOOLS, "gen_sch_e.py")
NET_A = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"
NET_E = "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"
L9PWR = "v2/docs/records/l8r2/inputs/l9pwr_budget-38ef774c.txt"
L9STK = "v2/docs/records/l8r2/inputs/l9stk_stackups-7388a84b.txt"
L9STK_PAGE = "v2/docs/records/l8r2/inputs/l9stk-L9-STACKUPS-7388a84b.md"
L4E9_PAGE = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
CHAIN = "v2/ecad/tools/pcb_energy_chain.yaml"
CHAIN_FIX = "v2/docs/records/l8r2/apply_energy_chain_e1oz.py"

POWER_A = [("l4e6", "r12"), ("l4e11", "guard"), ("l4e11", "charger"), ("l4e4", "r11"), ("l4e8", "bank"), ("l4e4", "r138"), ("l4e9", "u17")]
L8_A = [("l8gnd", "gnd002"), ("l8gnd", "hotr1"), ("l8r2", "d8v3"), ("l8r2", "vbus20ov"), ("l8r2", "packrtn"), ("l8r2", "slotlm"), ("l8r2", "fb01")]
MINE_A = [("l8r2", "d8v3"), ("l8r2", "vbus20ov"), ("l8r2", "packrtn"), ("l8r2", "slotlm"), ("l8r2", "fb01")]
# round 4: slotlm rewrites VBAT's "U4": 2.0, which L4-E11's charger names in its anchor, so it follows the charger (L4-E9's order)
AFTER_CHARGER = [("l8r2", "slotlm")]
# board E's round in the change list's order (L4-POWER-ARCHITECTURE.md's table; section 6b prints whether the page still says so)
E_ROUND = [("l4e9", "q1"), ("l4e7", "u5_grade"), ("l4e7", "hold"), ("l4e7", "input_limit"), ("l4e7", "backstop"), ("l4e9", "f1"),
           ("l4e9", "hotswap"), ("l4e11", "entry"), ("l4e7", "solar_guard"), ("l4e11", "aux"), ("d8dec31", "cin")]
MINE_E = [("l8r2", "packrtn")]
L8_B = [("l8gnd", "gnd002"), ("l8r2", "fans12"), ("l8r2", "panel5v"), ("l8r2", "ph4"), ("l8r2", "rt500")]
MINE_B = [("l8r2", "fans12"), ("l8r2", "panel5v"), ("l8r2", "ph4"), ("l8r2", "rt500")]
# round 5: Layer 6's board B drafts on this branch (record l6r2, merged in set 28), composed with this record's in either order
L6_B = ["v2/docs/records/l6r2/apply_gen_sch_b_%s.py" % n for n in ("xal_land", "lcsc", "intent")]
MAINPB = "v2/docs/records/d8dec31/apply_gen_sch_a_mainpb.py"
HELD = [("v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf", "3cfe41fef1407b85abaaee1e27a95ac3cf2cb1bdf218209b8578a835c4c9497f"),
        ("v2/vendor/fans/held/sanyo-denki-san-ace-c1152b001-2510-p0362.pdf", "7e5e2e7b1fe7e92fd0d1a63eb5e365fdca85be56559c7f6ee2353a10c4d072b9"),
        ("v2/vendor/fans/held/sanyo-denki-san-ace-c1152b001-2510-p0616.pdf", "5a7dbdd94339d81b574e4218bf2f73ae7deb1daf1883a46d9c4e24ffc34578ee"),
        ("v2/vendor/fans/held/sanyo-denki-san-ace-c1152b001-2510-p0623.pdf", "cd8112da11bc536f1054609d6afee0e43850d00cbfa657624ad49c29d0697c3f"),
        ("v2/vendor/fans/held/sanyo-denki-san-ace-c1152b001-2510-p0633.pdf", "17e067067bfe798f1ed6371c32df81c050bd5edaf82242b433a23e4d5ff989af")]

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
    L9PWR, L9STK, L9STK_PAGE, "v2/ecad/tools/gen_sch_e.py", NET_E, CHAIN, CHAIN_FIX, "v2/ecad/tools/pcb_decisions.yaml",
    "v2/ecad/tools/energy_chain.py", "v2/ecad/tools/track_current.py", "v2/ecad/tools/intent.py", "v2/vendor/diodes/diodes-ap64500.pdf",
    "v2/ecad/tools/gen_pcb_e3.py",
    # round 4
    "v2/docs/records/l4e12/L4E12-ELECTRONICS-THERMAL.md", "v2/docs/records/l4e12/l4e12_thermal.out", "v2/vendor/cm5/cm5-datasheet.pdf",
    "v2/vendor/cm5/linux-bcm2712-rpi-cm5.dtsi", "v2/vendor/fans/sunon-dc-fan-catalogue-240A-pp18-40-extract.pdf",
    "v2/vendor/ti/lm5176-datasheet.pdf", "v2/vendor/fans/sanyo-denki-splash-proof-fan-pages-2026-10-03.md",
    # round 5: Layer 6's board B drafts and their helpers (composition), the collaborator's check as filed
    "v2/docs/records/l6r2/apply_gen_sch_b_xal_land.py", "v2/docs/records/l6r2/apply_gen_sch_b_lcsc.py",
    "v2/docs/records/l6r2/apply_gen_sch_b_intent.py", "v2/docs/records/l6r2/l6r2_apply.py", "v2/docs/records/l6r2/l6r2_land.py",
    "v2/docs/records/l6r2/l6r2_intent.py", "v2/docs/records/l8r2/checks/astra-check-l9pf02-1.md",
    "v2/docs/records/l8r2/checks/astra-check-l9pf02-2.md",
] + ["v2/docs/records/%s/apply_gen_sch_a_%s.py" % rn for rn in POWER_A + L8_A] + ["v2/docs/records/%s/apply_gen_sch_b_%s.py" % rn for rn in L8_B] \
  + ["v2/docs/records/%s/apply_gen_sch_e_%s.py" % rn for rn in E_ROUND + MINE_E]
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
    "eta_a": (0.89, "ASSUMPTION", "board A's 12 V buck-boost for choice (b)"),
    # round 3 (item 1 re-decided; round 2's "eta_slot", a flat 0.90 for board A's slot converters, is retired: record l9pwr's R9 reads
    # the three coolers' watts at VBAT on each slot rail's own converter)
    "duty_max": (0.70, "BOUND", "the modules' Fan_PWM maximum duty for the coolers (round 3, L9P-F02), a firmware rule (section 1's text for HW-FW-CONTRACT)"),
    "ap_ipk": ((6.8, 8.0, 9.2), "MAKER", "AP64500 HS peak current limit, minimum / typical / maximum (Diodes DS41979, electrical characteristics, Note 8)"),
    "ap_l": (4.7e-6, "BOUND", "board A's slot inductors L3 and L5, 4.7 uH XAL6060-472ME (gen_sch_a.py, buck5)"),
    "ap_ltol": (0.20, "ASSUMPTION", "the slot inductor taken 20 % low for the ripple"),
    "ap_fsw": (500e3, "BOUND", "RT 68 k, 500 kHz (gen_sch_a.py, buck5)"),
    "vsys_max": (17.375, "INFERRED", "the system node's highest, on shore (L4-E11 15a: VSYS_E 9.494 to 17.375 V)"),
    # round 4 (L9P-F02's focused check): the cooler's maker's catalogue (held back by its terms), the slot converters, the cooling basis
    "fan_rows": (((100, 0.17, 2.0, 13700, 0.38, 210.0), (25, 0.03, 0.36, 3000, 0.07, 9.8)), "MAKER",
                 "9WPA0412P6G001 at 12 V, free air: PWM duty %, A, W, min-1, m3/min, Pa (San Ace catalogue C1152B001 '25.10 p.362)"),
    "n70": ((10400.0, 400.0), "INFERRED", "the speed at 70 % duty read off p.362's PWM duty to speed example (12 V, 25 kHz), +-400 min-1 for the reading"),
    "pq100": ((80.0, 0.22), "INFERRED", "p.362's 100 % duty curve stays at or over 80 Pa up to 0.22 m3/min (read off the graph at its plateau's least)"),
    "pq50": (30.0, "INFERRED", "p.362's 50 % duty curve at 0.105 m3/min (3.7 CFM): about 30 Pa (read off the graph, +-5 Pa)"),
    "pwm_in": (((4.75, 5.25), (0.0, 0.4), 25e3, 1e-3, 5.25), "MAKER",
               "the PWM input example: VIH, VIL, 25 kHz, Isource and Isink at most 1 mA, the open terminal at most 5.25 V (p.623; 'differ with models')"),
    "tps_eta_typ": (0.88, "INFERRED", "TPS61089 Figure 7-2 (typical, VIN 3.6 V, VOUT 12 V) read at 0.1 A, about 88 % (SLVSD38C p.7)"),
    "vfb_ap": ((0.792, 0.800, 0.808), "MAKER", "AP64500 VFB in CCM (DS41979 Rev 5-2 p.6)"),
    "vref_lm": ((0.788, 0.800, 0.812), "MAKER", "LM5176 VREF (SNVSAI1D electrical characteristics)"),
    "fb_div": ((53.6e3, 10.0e3, 0.01), "BOUND", "the slot stages' FB divider 53.6 k over 10 k, 1 % (gen_sch_a.py: buck5's and slot 2's lm5176 call)"),
    "drop": (0.02, "BOUND", "the slot rails' end-to-end drop budget, 2 % (gen_sch_a.py and gen_sch_b.py, budget=0.02)"),
    "ap_theta": ((45.0, 5.0), "MAKER", "AP64500 theta-JA, theta-JC: SO-8EP on a four-layer 2 oz board, the minimum recommended pad (DS41979 p.5 Note 6)"),
    "ap_tj": ((125.0, 160.0), "MAKER", "AP64500 operating junction at most +125 C; thermal shutdown +160 C (DS41979 pp.5, 6)"),
    "ap_fig24": (((45.0, 5.0), (123.0, 0.0)), "INFERRED",
                 "AP64500 Figure 24 (typical, VIN 12 V, 500 kHz), its VOUT 5 V line read off the graph: 5.0 A to 45 C, straight to 0 A at 123 C (+-2 C)"),
    "rep_fan": ((3.7, 0.11), "MAKER", "Sunon MF30060V2, record l4e12's representative cooler fan: 3.7 CFM, 0.11 inch H2O (catalogue 240-A, held)"),
    "csd": ((5.7e-3, 50.0, 125.0, 150.0), "MAKER",
            "CSD19532Q5B: RDS(on) at most 5.7 mOhm at VGS 6 V, 25 C; RthJA at most 50 C/W on 1 inch2 of 2 oz copper, 125 C/W on the minimum pad; junction to +150 C (SLPS414B)"),
    "csd_q": ((8.7e-9, 13e-9, 9.5e-9, 128e-9, 249e-9, 17.0, 2.4, 1.0), "MAKER",
              "CSD19532Q5B: Qgd 8.7 nC, Qgs 13 nC, Qg(th) 9.5 nC, Qoss 128 nC at 50 V, Qrr 249 nC at 17 A, RG at most 2.4 Ohm, VSD at most 1.0 V (SLPS414B)"),
    "lm_drv": ((1.8, 1.1, 45e-9, 7.35), "MAKER", "LM5176 driver pull-up 1.8 Ohm, pull-down 1.1 Ohm, dead time 45 ns (SNVSAI1D); VCC 7.35 V (gen_sch_a.py's figure)"),
    "lm_fsw": (232e3, "INFERRED", "the LM5176 stages' highest switching frequency, 232 kHz (RT 40.2 k, gen_sch_a.py on Equation 5)"),
    "rds_hot": (2.0, "ASSUMPTION", "RDS(on) at the junction taken 2.0 times the 25 C maximum (SLPS414B Figure 8 not read)"),
    "v_plat": (4.5, "ASSUMPTION", "the CSD19532Q5B's Miller plateau taken at 4.5 V (VGS(th) 2.6 V typical; the gate charge curve not read)"),
    "qrr_prop": (True, "ASSUMPTION", "the body diode's Qrr taken in proportion to its forward current from the sheet's 17 A row"),
    "eta_lm": (0.90, "ASSUMPTION", "the LM5176 5.1 V stages' declared efficiency, NOT PLOTTED by the maker (rv-pwr's rule; record l9pwr's M1)"),
    "slot_peak": (6.6, "BOUND", "the three slot leads' declared peak, both ends: the bounded start-up and fault envelope (round 6; apply_gen_sch_a_slotlm.py, apply_gen_sch_b_fans12.py)"),
    # round 6 (the collaborator's recheck: B2 the start-up envelope, B3 the matrix's thermal acceptance, F5-03 corrected)
    "start_bound": (1.80, "BOUND", "the cooler branch's bounded start on +5V_Sn: a 100 us moving average at most 1.80 A, over the steady 0.712 A for at most 1.0 s a start (C4-3 holds the chain to it)"),
    "fb_tol01": (0.001, "BOUND", "the LM5176 5.1 V stages' divider at 0.1 % (apply_gen_sch_a_fb01.py)"),
    "ibias_fb": (25e-9, "MAKER", "LM5176 IBIAS(FB) at most 25 nA in regulation (SNVSAI1D electrical characteristics)"),
    "vsns": ((0.043, 0.050, 0.057), "MAKER", "LM5176 VSNS, the average current loop's target (SNVSAI1D)"),
    "isns_r": ((0.006, 0.01), "BOUND", "the ISNS shunt 6 mOhm 1 % (WSL2512, gen_sch_a.py)"),
    "tlim": (87e-6, "MAKER", "TPS2596 current limit response time 87 us typical (SLVSET8A 7.6)"),
    "matrix": ((3.0, 4.1), "BOUND", "C4-1's lower steady points (A), with the steady envelope and the declared peak"),
    # round 5 (the collaborator's check: B1 the AP64500's drawn frequency, B2 the envelope)
    "fan_env": (2.75, "BOUND", "the cooler's steady input at the step-up's 12.43 V top, any duty: the maker's 2.0 W at 12 V x 1.111 by the fan laws, with room for -20 C air and the cooler's pressure; C4-3 holds the chain to it"),
    "ap_rt": (68e3, "BOUND", "board A's and B's drawn AP64500 RT, 68 k (gen_sch_a.py buck5, gen_sch_b.py buck33; O-20)"),
    "ap_eq7": (100000.0, "MAKER", "DS41979 Eq. 7: RT[kOhm] = 100000 / fsw[kHz] (p.14); 450 to 550 kHz at 200 k (p.6)"),
    "rt_tol": (0.10, "INFERRED", "the oscillator's spread taken as the printed 200 k row's 10 % at 68 k, where no row is printed"),
    "fss": (0.06, "MAKER", "AP64500 frequency spread spectrum +-6 % in resistor timing (p.1, p.14)"),
    "ap_rds": ((0.045, 0.020), "MAKER", "AP64500 high and low side RDS(on) 45 and 20 mOhm, typical only (p.6, Note 8)"),
    "rds_hot_ap": (1.5, "ASSUMPTION", "the AP64500's RDS(on) taken 1.5 times its typical when hot (Figure 9 not read)"),
    "cm5_vin": ((4.75, 5.25), "MAKER", "CM5 5 V input 4.75 to 5.25 V (CM5 datasheet, pin table: 'main power input')"),
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
    o["a_vbat"] = l9pwr()["r9"]["this"]; o["a_vbat_r2"] = l9pwr()["r9"]["theirs"][2]   # round 3: record l9pwr's R9, not a flat 0.90
    o["b_vbat"] = 3 * V["pfan"] / V["eta_a"]
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


# ---------------------------------------------------------------------------------------------------------------- round 3
_P = {}
RAIL_L = re.compile(r"^\s+rail (\S+)\s+(\S+)\s+([\d.]+) V\s+out\s+([\d.]+)\s+([\d.]+)\s+([\d.]+) W\s+([\d.]+)\s+([\d.]+) A\s+eta ([\d.]+)"
                    r"\s+loss\s+([\d.]+) W\s+(\S+)\s*$")
LIMIT_L = re.compile(r"^\s+limit (.+?)\s+([\d.]+) A \((\w+)\): judged\s+([\d.]+) /\s+([\d.]+) A, margin at HIGH\s+([+-][\d.]+) A "
                     r"\(\s*([+-][\d.]+) %\): (.+)$")
STATE_L = re.compile(r"^   == (PS-[A-Za-z0-9-]+)( \(.*\))? \(pack side ([\d.]+) / ([\d.]+) / ([\d.]+) W\)$")


def l9pwr():
    """Record l9pwr's output (inputs/, at 38ef774c), parsed: section 5's rails and limits per state, R9, U901's RON, L9P-F02's line.
    Nothing of it is typed in this record; a line that no longer parses stops the script."""
    if _P:
        return _P
    lines = open(os.path.join(ROOT, L9PWR), encoding="utf-8").read().splitlines()
    s5 = [i for i, l in enumerate(lines) if l.startswith("5. PER STATE, DRAFTED")]
    s6 = [i for i, l in enumerate(lines) if l.startswith("6. THE PACK CURRENT")]
    if len(s5) != 1 or len(s6) != 1:
        raise SystemExit("l8r2_drafts: record l9pwr's output has no single section 5 and 6")
    states, cur, last = {}, None, None
    for l in lines[s5[0]:s6[0]]:
        m = STATE_L.match(l)
        if m:
            cur = states.setdefault(m.group(1), {"label": m.group(1) + (m.group(2) or ""), "rails": {}, "drawn": {}})
            continue
        m = RAIL_L.match(l)
        if m and cur is not None:
            g = m.groups()
            last = cur["rails"][g[0]] = {"kind": g[1], "v": float(g[2]), "out": (float(g[3]), float(g[4]), float(g[5])),
                                         "a": (float(g[6]), float(g[7])), "eta": float(g[8]), "status": g[10], "limit": None}
            continue
        m = LIMIT_L.match(l)
        if m and last is not None:
            g = m.groups()
            last["limit"] = {"part": g[0], "a": float(g[1]), "kind": g[2], "judged": (float(g[3]), float(g[4])),
                             "margin": float(g[5]), "pct": float(g[6]), "verdict": g[7]}
            continue
        if cur is not None and "DRAWN's margins at HIGH that differ:" in l:
            for nm, v in re.findall(r"(\w+) ([+-][\d.]+) A", l.split("differ:", 1)[1]):
                cur["drawn"][nm] = float(v)
    heads = [l for l in lines[s5[0]:s6[0]] if l.startswith("   == PS-")]
    if len(heads) != len(states):
        raise SystemExit("l8r2_drafts: record l9pwr's section 5 has %d state headers, %d parsed" % (len(heads), len(states)))
    t = "\n".join(lines)
    m = re.search(r"R9 l8r2 item 1, choice \(a\)[^\n]*\n\s+theirs \(([\d., ]+)\); reproduced \(([\d., ]+)\): (\w+)\n"
                  r"\s+this record: [^\n]*?: \(([\d.]+),\)", t)
    r = re.search(r"D5 U901: RON at most ([\d.]+) Ohm", t)
    f = re.search(r"\n   (L9P-F02)  ([A-Z ]+?)  \((\w+)\)  ([^\n]+)\n\s+figure: ([^\n]+)", t)
    f3 = re.search(r"\n   (L9P-F03)  ([A-Z ]+?)  \(([^)]+)\)\)?  ([^\n]+)\n\s+figure: ([^\n]+)", t)
    if not (states and m and r and f and f3):
        raise SystemExit("l8r2_drafts: record l9pwr's output no longer parses (states %d, R9 %s, D5 %s, F02 %s, F03 %s)"
                         % (len(states), bool(m), bool(r), bool(f), bool(f3)))
    _P.update(states=states, r9={"theirs": tuple(float(x) for x in m.group(1).split(",")), "equal": m.group(3),
                                 "this": float(m.group(4))},
              ron=float(r.group(1)), f02=(f.group(1), f.group(2), f.group(5)), f03=(f3.group(1), f3.group(2), f3.group(5)))
    return _P


def slot_loads(text):
    """board B's _SLOT_LOADS and the slots' declared peak, read from a generator's text with ast (never typed)."""
    tree = ast.parse(text)
    fn = [n.value for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "_SLOT_LOADS"]
    if len(fn) != 1:
        raise SystemExit("l8r2_drafts: gen_sch_b.py has no single _SLOT_LOADS")
    loads = eval(compile(ast.Expression(fn[0]), "_SLOT_LOADS", "eval"), {})
    peak = {}
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "rail" and n.args
                and isinstance(n.args[0], ast.BinOp) and getattr(n.args[0].left, "value", "") == "+5V_S%d"):
            for s in (1, 2, 3):
                peak[s] = eval(compile(ast.Expression(n.args[3]), "peak", "eval"), {"_n": s})
    if sorted(peak) != [1, 2, 3]:
        raise SystemExit("l8r2_drafts: gen_sch_b.py declares no +5V_S%d rail call")
    return {s: loads(s) for s in (1, 2, 3)}, peak


def fresh_intent():
    sp = importlib.util.spec_from_file_location("intent_fresh", os.path.join(TOOLS, "intent.py"))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def intent_says(peak, loads, net="+5V_S1"):
    """intent.rail's own verdict on a slot rail's declared peak and loads: 'accepted' or its refusal's first sentence."""
    it = fresh_intent()
    try:
        it.rail(net, 5.1, 2.5, peak, "J_5V_S1", loads=loads, converted=False)
    except SystemExit as e:
        return "REFUSED (%s)" % str(e).split(". ")[0]
    return "accepted"


def item1_r3():
    """Round 3: each option's current on the slot converters and the device rail at HIGH, from record l9pwr's rails per state."""
    P = l9pwr(); D = V["duty_max"]; rows = []
    for st, d in P["states"].items():
        R = d["rails"]
        for n in ("1", "2", "3"):
            s, f, a = R.get("S" + n), R.get("S%sF" % n), R.get("S%sA" % n)
            if not s or not f or not s["limit"]:
                continue
            v, hi, lim = s["v"], s["out"][2], s["limit"]["a"]
            full_in = f["out"][2] / f["eta"]                      # the cooler's input on the slot rail at full speed (2.0 W / 0.85)
            cap_w = D * f["out"][2]                               # the linear bound at the cap
            I = {"a": hi / v,
                 "cap": (hi - full_in + cap_w / f["eta"]) / v,
                 "cap_lo": (hi - full_in + cap_w / V["eta_lo"]) / v,
                 "cap_law": (hi - full_in + D ** 3 * f["out"][2] / f["eta"]) / v,
                 "b": (hi - full_in) / v,
                 "rel": (hi - (a["out"][2] if a else 0.0)) / v}
            rows.append({"state": st, "slot": n, "part": s["limit"]["part"].split(",")[0], "limit": lim, "I": I,
                         "printed": s["limit"]["judged"][1], "margin": {k: lim - x for k, x in I.items()}})
    dev = []
    for st, d in P["states"].items():
        R = d["rails"]; s = R.get("DEV")
        if not s or not s["limit"]:
            continue
        drawn = s["limit"]["a"] - d["drawn"]["DEV"] if "DEV" in d["drawn"] else s["limit"]["judged"][1]
        pnl = R.get("PNL")
        u901 = (pnl["a"][1] ** 2 * P["ron"] / s["v"]) if pnl else 0.0
        dev.append({"state": st, "limit": s["limit"]["a"], "drafted": s["limit"]["judged"][1], "margin": s["limit"]["margin"],
                    "pct": s["limit"]["pct"], "drawn": drawn, "u901": u901})
    fixed = (D - D ** 3) / (1 - D ** 3)                           # the fan law with a speed-independent share f: f + (1 - f) D^3 = D
    l = V["ap_l"] * (1 - V["ap_ltol"]); fs = V["ap_fsw"] * (1 - V["fsw_tol"]); vo = V["vin_nom"]
    ripple = vo * (1 - vo / V["vsys_max"]) / (l * fs)
    worst = max(r["I"]["a"] for r in rows if r["part"].startswith("AP64500"))
    return {"rows": rows, "dev": dev, "fixed": fixed, "ripple": ripple, "worst": worst, "ipk": worst + ripple / 2,
            "vbat_full": P["r9"]["this"], "vbat_cap": P["r9"]["this"] * D}


def e_round_page():
    """board E's scripts in the change list's order, as L4-POWER-ARCHITECTURE.md's change table gives them (the ALT rows left out)."""
    page = open(os.path.join(ROOT, L4E9_PAGE), encoding="utf-8").read().splitlines()
    i = [k for k, l in enumerate(page) if l.startswith("| # | Step | Row |")]
    if len(i) != 1:
        raise SystemExit("l8r2_drafts: L4-POWER-ARCHITECTURE.md has no single change table")
    seq = []
    for l in page[i[0] + 2:]:
        if not l.startswith("|"):
            break
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if c[1] == "ALT" or not c[3].startswith("board E, gen_sch_e.py") or not c[4].startswith("apply_gen_sch_e_"):
            continue
        for s in [x.strip() for x in c[4].split(",")]:
            if s not in seq:
                seq.append(s)
    return seq


def run_e(script, target):
    """board E's drafts: d8dec31's input capacitor takes board E's netlist and writes by itself; every other one takes --write."""
    args = [target, os.path.join(ROOT, NET_E)] if script.endswith("_cin.py") else [target, "--write"]
    r = subprocess.run([sys.executable, "-B", script] + args, capture_output=True)
    return r.returncode, (r.stderr.decode("utf-8", "replace").strip().splitlines() or [""])[-1]


def compose_e(seq, d, tag):
    p = os.path.join(d, tag + ".py"); shutil.copy(GEN_E, p); res = []
    for s in seq:
        rc, msg = run_e(s, p)
        res.append((os.path.relpath(s, RECS), "OK" if rc == 0 else "REFUSED (%s)" % msg))
        if rc:
            break
    return p, res


def rail_calls(text, names):
    """The _intent.rail calls of a generator's text whose net is one of names, evaluated by a fresh intent.py in the file's order:
    {net: 'accepted' or the refusal, and the declaration as intent recorded it}."""
    it = fresh_intent(); out = {}
    calls = [n for n in ast.parse(text).body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
             and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == "rail" and n.value.args
             and isinstance(n.value.args[0], ast.Constant) and n.value.args[0].value in names]
    for c in sorted(calls, key=lambda x: x.lineno):
        net = c.value.args[0].value
        try:
            eval(compile(ast.Expression(c.value), "rail", "eval"), {"_intent": it})
            out[net] = ("accepted", it._I["rails"][net])
        except SystemExit as e:
            out[net] = ("REFUSED (%s)" % str(e).split(". ")[0], None)
    return out


def l9stk_rows():
    """record l9stk's section 2 (inputs/, at 7388a84b): the width rows per board and its line on the returns, parsed."""
    t = open(os.path.join(ROOT, L9STK), encoding="utf-8").read()
    rows, board = {}, None
    for l in t.splitlines():
        m = re.match(r"^   board (\w+) \(", l)
        if m:
            board = m.group(1); continue
        m = re.match(r"^     (\S+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(yes|no)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)$", l)
        if m and board:
            rows[(board, m.group(1))] = tuple(float(x) for x in m.group(2, 3, 4, 6, 7, 8, 9))
    ret = re.search(r"returns declared in the intents: ([^\n]+)", t)
    if not rows or not ret:
        raise SystemExit("l8r2_drafts: record l9stk's output no longer parses")
    return rows, ret.group(1)


def amps_for_width(w, oz):
    """the current a band of width w (mm, outer layer) carries at 10 K by decision 35's model: track_current's inverse, bisected."""
    sys.path.insert(0, TOOLS)
    import track_current as tc
    lo, hi = 0.0, 200.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tc.width_for_current(mid, oz=oz) <= w else (lo, mid)
    return lo


def dchs_band():
    """board E's DC_HS band as gen_pcb_e3.py lays it (one B.Cu band: its run along Q7's source pads and its leg up L2 pin 1), the
    widths read from the generator's own rectangles."""
    t = open(os.path.join(TOOLS, "gen_pcb_e3.py"), encoding="utf-8").read()
    run = re.search(r"^\s*_run = \(min\(_qx, _lx\) - ([\d.]+), _qy - ([\d.]+), max\(_qx, _lx\) \+ [\d.]+, _qy \+ ([\d.]+)\)", t, re.M)
    leg = re.search(r"^\s*_leg = \(_lx - ([\d.]+), min\(_qy, _ly\) - [\d.]+, _lx \+ ([\d.]+),", t, re.M)
    one = re.search(r'_pc\.union\("DC_HS", "DC_HS band B\.Cu', t)
    if not (run and leg and one):
        raise SystemExit("l8r2_drafts: gen_pcb_e3.py's DC_HS band no longer parses")
    return float(run.group(2)) + float(run.group(3)), float(leg.group(1)) + float(leg.group(2))


def item6():
    """The widths the energy chain's declared ratings need at 1 oz (decision 35's model), and what board E's input band carries."""
    sys.path.insert(0, TOOLS)
    import track_current as tc
    w = lambda a, oz=1.0: tc.width_for_current(a, oz=oz)
    run, leg = dchs_band()
    return {"w25": (w(25.0 / 2), w(25.0)), "w18": (w(18.0 / 2), w(18.0)), "w10": (w(10.0 / 2), w(10.0)),
            "a_672_two": 2 * amps_for_width(6.72, 1.0), "dchs": (run, leg), "dchs_1oz": (amps_for_width(run, 1.0), amps_for_width(leg, 1.0)),
            "dchs_2oz": (amps_for_width(run, 2.0), amps_for_width(leg, 2.0))}


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
    """What a draft adds: a new literal part call, a new designator token, or its declared ADDS; a designator the generator already
    named (round 4: slotlm draws U8, U10, R30 and R38 as literal calls where buck5 took them in a list) is kept, not added."""
    cb = {r for _h, r in literal_calls(before)}; ca = {r for _h, r in literal_calls(after)}; tb = tokens(before)
    return (ca - cb - tb) | (tokens(after) - tb) | declared_adds(script)


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


def r3_slot_loads():
    """the slot rail's declared loads on board B: as drawn, as round 2 drafted them (the step-up at full speed), as round 3 did (the
    70 % maximum, computed here: round 4 withdrew it from the draft), as round 4's draft does (full speed, slots 1 and 3 at 5.3 A on
    board A's LM5176 stages), and with no fan row (choice (b))."""
    base, peak = slot_loads(open(GEN_B, encoding="utf-8").read())
    r2 = round(V["pfan"] / V["eta"] / 5.0, 2); r3 = round(V["duty_max"] * V["pfan"] / V["eta"] / 5.0, 2); s = 1
    fan = "U%d" % (701 + 30 * (s - 1))
    l2 = {(fan if k == "J_FAN%d" % s else k): (r2 if k == "J_FAN%d" % s else v) for k, v in base[s].items()}
    l3 = {(fan if k == "J_FAN%d" % s else k): (r3 if k == "J_FAN%d" % s else v) for k, v in base[s].items()}
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "b.py"); shutil.copy(GEN_B, p)
        rc, msg = run(draft("l8r2", "fans12", "b"), p)
        if rc:
            raise SystemExit("l8r2_drafts: the coolers' draft refused a copy of gen_sch_b.py: %s" % msg)
        r4, peak4 = slot_loads(open(p, encoding="utf-8").read())
    lb = {k: v for k, v in base[s].items() if k != "J_FAN%d" % s}
    return [("as drawn (J_FAN%d 0.1 A)" % s, base[s], peak[s]),
            ("round 2 (the step-up at full speed, %.2f A)" % r2, l2, peak[s]),
            ("round 3 (the step-up at the %.0f %% maximum, %.2f A)" % (100 * V["duty_max"], r3), l3, peak[s]),
            ("round 4's draft (full speed %.2f A, LM5176 slot)" % r4[s][fan], r4[s], peak4[s]),
            ("(b), the cooler off the slot rail (no fan row)", lb, peak[s])]


def item1_r3_print(w):
    P = l9pwr(); o = item1_r3(); D = V["duty_max"]
    w("\n2b. ROUND 3: ITEM 1 RE-DECIDED ON RECORD l9pwr'S FIGURES (inputs/l9pwr_budget-38ef774c.txt, its section 5 parsed: %d states; nothing typed)\n"
      % len(P["states"]))
    w("  %s (%s): %s\n" % P["f02"])
    w("  %s (%s): %s\n" % P["f03"])
    w("  the efficiency: round 2's %.2f W for the three coolers at VBAT took board A's slot converters at a flat 0.90; record l9pwr's R9 (theirs %s, reproduced: %s) reads %.4f W on each slot rail's own converter, the figure item 1 now carries\n"
      % (P["r9"]["theirs"][2], "(%s)" % ", ".join("%g" % x for x in P["r9"]["theirs"]), P["r9"]["equal"], P["r9"]["this"]))
    w("  the slot rail's declared loads on board B (gen_sch_b.py's _SLOT_LOADS and its +5V_Sn rail's peak, read with ast), judged by intent.rail itself (loads at most 1.02 times the peak):\n")
    for tag, loads, peak in r3_slot_loads():
        w("    %-52s slot 1: %.3f A against %.3f A: %s\n" % (tag, sum(loads.values()), peak, intent_says(peak, loads)))
    w("  the options at HIGH on each slot's converter, every state (A on its output, the margin to its limit in brackets); record l9pwr's rails:\n")
    w("    (a) as drafted at full speed; (a) with the %.0f %% Fan_PWM maximum, the linear bound (%.1f W of fan) at the step-up's 0.85, at its low 0.80, and by the fan law (%.3f of full power);\n"
      "    (b) the cooler off the slot rail (one feed from board A or one per slot alike); released: Fan_PWM released and the card socket's supply off (PCIE_PWR_EN low), the fan at full speed\n"
      % (100 * D, D * V["pfan"], D ** 3))
    w("    %-12s %-4s %-24s %-17s %-17s %-17s %-17s %-17s %-17s\n" % ("state", "slot", "converter (limit)", "(a) drafted", "(a) cap", "(a) cap eta 0.80", "(a) cap fan law", "(b)", "released"))
    same = True
    for r in o["rows"]:
        same = same and abs(r["I"]["a"] - r["printed"]) < 0.0006
        w("    %-12s %-4s %-24s %s\n" % (r["state"], r["slot"], "%s (%.3f A)" % (r["part"], r["limit"]),
                                       " ".join("%-17s" % ("%.3f (%+.3f)" % (r["I"][k], r["margin"][k])) for k in ("a", "cap", "cap_lo", "cap_law", "b", "rel"))))
    w("    (a) drafted, from the rail's watts, equals record l9pwr's printed current in every row: %s\n" % ("YES" if same else "NO"))
    for fam in ("AP64500", "LM5176"):
        rs = [r for r in o["rows"] if r["part"].startswith(fam)]
        least = {k: min(rs, key=lambda r: r["margin"][k]) for k in ("a", "cap", "cap_lo", "cap_law", "b", "rel")}
        w("  the least margin at HIGH over every state, %s (%s): %s\n" % (fam, ", ".join(sorted({r["part"] for r in rs})), "; ".join(
            "%s %+.3f A (%+.1f %%, %s)" % ({"a": "(a) drafted", "cap": "(a) cap", "cap_lo": "(a) cap eta 0.80", "cap_law": "(a) cap fan law", "b": "(b)", "rel": "released"}[k],
                                         least[k]["margin"][k], 100 * least[k]["margin"][k] / least[k]["limit"], least[k]["state"]) for k in least)))
    w("  the device rail (%s): no option feeds a cooler from +5V_DEV, so every option leaves it as record l9pwr prints it:\n" % P["f03"][0])
    for d in o["dev"]:
        w("    %-12s LM5176 U7 %.3f A DRAFTED against %.3f A, margin %+.3f A (%+.1f %%); DRAWN %.3f A; U901's RON loss (record l8r2 item 3) %.3f A of the difference\n"
          % (d["state"], d["drafted"], d["limit"], d["margin"], d["pct"], d["drawn"], d["u901"]))
    pnl = max(st["rails"]["PNL"]["a"][1] for st in P["states"].values() if "PNL" in st["rails"])
    w("    U901's RON (at most %.4f Ohm, record l9pwr's D5) at the panel's %.3f A at HIGH: %.3f W on +5V_DEV, %.3f A at 5.1 V\n"
      % (P["ron"], pnl, pnl ** 2 * P["ron"], pnl ** 2 * P["ron"] / 5.1))
    w("  the linear bound fails only if more than %.1f %% of the fan's full-speed input does not fall with its speed (the fan law with a fixed share f: f + (1 - f) x %.3f > %.2f)\n"
      % (100 * o["fixed"], D ** 3, D))
    w("  if the bound fails open (Fan_PWM uncapped with the card on): %.3f A on slots 1 and 3, the AP64500's inductor peak %.3f A (ripple %.3f A at VSYS's %.3f V, L %.0f %% low, fsw %.0f %% low) under its least HS peak current limit %.1f A by %.3f A: no limit acts\n"
      % (o["worst"], o["ipk"], o["ripple"], V["vsys_max"], 100 * V["ap_ltol"], 100 * V["fsw_tol"], V["ap_ipk"][0], V["ap_ipk"][0] - o["ipk"]))
    w("  the coolers at VBAT: %.4f W at full speed (R9); at the %.0f %% maximum at most %.2f W (the linear bound, the slot converters' efficiency taken flat over the change): %.2f W less at HIGH, a figure for L9P-F01's owner\n"
      % (o["vbat_full"], 100 * D, o["vbat_cap"], o["vbat_full"] - o["vbat_cap"]))
    w("  round 3 SELECTED (SESSION): (a) with the modules' %.0f %% Fan_PWM maximum; (b) as one 12 V feed would make one converter common to the three modules' coolers, a shared element ASM-002 does not name; WITHDRAWN by round 4 (2c)\n" % (100 * D))



# ---------------------------------------------------------------------------------------------------------------- round 4
_PB = {}


def rvpwr():
    """record rv-pwr's model (an input pinned above): its AP64500 efficiency curves, the maker's Figures 4 and 5 and their 3.3 V twins"""
    if not _PB:
        sp = importlib.util.spec_from_file_location("l8r2_rvpwr", os.path.join(ROOT, "v2", "docs", "records", "rv-pwr", "pwr_budget.py"))
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); _PB["m"] = m
    return _PB["m"]


def pdf_text(rel):
    r = subprocess.run(["pdftotext", "-layout", os.path.join(ROOT, rel), "-"], capture_output=True)
    if r.returncode:
        raise SystemExit("l8r2_drafts: pdftotext refused %s" % rel)
    return r.stdout.decode("utf-8", "replace")


def r4_sources():
    """the figures round 4 reads from the tree's own files (never typed): C1's inside air, the cooling basis, the CM5's fan line"""
    page = open(os.path.join(ROOT, "v2/docs/records/l4e12/L4E12-ELECTRONICS-THERMAL.md"), encoding="utf-8").read()
    c1 = re.search(r'C1: "inside air \+(\d+) C or any cell \+(\d+) C \.\.\. normal to the reduced mode', page)
    out = open(os.path.join(ROOT, "v2/docs/records/l4e12/l4e12_thermal.out"), encoding="utf-8").read()
    h2 = re.search(r"2h The running module's cooler exhaust \(MODELED\): the representative 30 mm fan's ([\d.]+) CFM free-air \(MAKER, Sunon p\.1\) at (\d+) %\s*\n"
                   r"\s+through the heatsink \(ASSUMPTION\), ([\d.]+) l/s: the CM5's ([\d.]+) W and the fan's ([\d.]+) W lift the exhaust ([\d.]+) K", out)
    sun = re.search(r"MF30060V2-10000-A99\s+5\s+72\s+0\.36\s+7100\s+(\d+\.\d)\s+(\d\.\d+)", pdf_text("v2/vendor/fans/sunon-dc-fan-catalogue-240A-pp18-40-extract.pdf"))
    cm5 = " ".join(pdf_text("v2/vendor/cm5/cm5-datasheet.pdf").split())
    shut = re.search(r"(During CM5 shutdown, power to the Fan_PWM signal is also stopped\.)", cm5)
    oc = re.search(r"(Fan_PWM : An open-collector output pin designed to drive a variety of PWM-controlled fans\.)", cm5)
    pe = re.search(r"(PCIE_PWR_EN 3\.3 V signal: active high, used to signal that a PCIe device can be powered down when low)", cm5)
    dts = open(os.path.join(ROOT, "v2/vendor/cm5/linux-bcm2712-rpi-cm5.dtsi"), encoding="utf-8").read()
    fan = re.search(r'fan: cooling_fan \{\s*status = "(\w+)";.*?cooling-levels = <([\d ]+)>;\s*pwms = <&rp1_pwm1 \d+ (\d+) PWM_POLARITY_INVERTED>;', dts, re.S)
    gb = open(GEN_B, encoding="utf-8").read()
    pce = re.search(r'r\(R\(6\), "100k", "PCIE_PWR_EN%d" % s, "GND"\)', gb)
    gate = re.search(r'lv1t08\(U\(16\), "EMCON_HW", "PCIE_PWR_EN%d" % s, "S%dA_EN" % s, n5,', gb)
    if not (c1 and h2 and sun and shut and oc and pe and fan and pce and gate):
        raise SystemExit("l8r2_drafts: a round 4 source no longer reads (C1 %s, 2h %s, Sunon %s, CM5 %s %s %s, dtsi %s, board B %s %s)"
                         % (bool(c1), bool(h2), bool(sun), bool(shut), bool(oc), bool(pe), bool(fan), bool(pce), bool(gate)))
    return {"c1_air": float(c1.group(1)), "c1_cell": float(c1.group(2)), "h2": tuple(float(x) for x in h2.groups()),
            "sunon": (float(sun.group(1)), float(sun.group(2))), "cm5_shut": shut.group(1), "cm5_oc": oc.group(1), "cm5_pe": pe.group(1),
            "dts": (fan.group(1), [int(x) for x in fan.group(2).split()], int(fan.group(3))), "pce_pd": bool(pce), "gate": bool(gate)}


def vout_least(vref, div):
    """the stage's least output and nominal: VREF's least on the 1 % divider's lowest ratio"""
    rt, rb, tol = div
    return vref[0] * (1 + rt * (1 - tol) / (rb * (1 + tol))), vref[1] * (1 + rt / rb)


def ap_loss(pout, i, vin):
    eta = rvpwr().eff_curve("AP64500_5V", vin, i)
    return pout * (1 / eta - 1), eta


def fig24(t):
    (t0, i0), (t1, i1) = V["ap_fig24"]
    return i0 if t <= t0 else max(0.0, i0 + (i1 - i0) * (t - t0) / (t1 - t0))


def qh1(i, vin, vo, rth, prop=True):
    """the LM5176 stage's buck-side high FET in buck mode: conduction, the two edges, Coss, the body diode's recovery (MAKER figures,
    the ASSUMPTIONS of F); every term taken on its high side. prop=False takes the sheet's Qrr unscaled (the sensitivity of round 5)"""
    rds, _r1, _r2, _tj = V["csd"]; qgd, qgs, qth, qoss, qrr, irr, rg, _vsd = V["csd_q"]; rpu, rpd, _dt, vcc = V["lm_drv"]
    f = V["lm_fsw"]; rh = rds * V["rds_hot"]; d = vo / vin; qsw = qgd + (qgs - qth)
    tr = qsw / ((vcc - V["v_plat"]) / (rpu + rg)); tf = qsw / (V["v_plat"] / (rpd + rg))
    terms = {"conduction": d * i * i * rh, "edges": 0.5 * vin * i * (tr + tf) * f, "coss": qoss * vin * f, "recovery": qrr * (i / irr if prop else 1.0) * vin * f}
    p = sum(terms.values())
    return p, terms, (tr, tf)


def ql1(i, vin, vo):
    rds = V["csd"][0] * V["rds_hot"]; d = vo / vin
    return (1 - d) * i * i * rds + 2 * V["lm_drv"][2] * V["lm_fsw"] * V["csd_q"][7] * i


def item1_r4():
    """Round 4, L9P-F02's focused check (the owner's questions 1 to 5), every figure from record l9pwr's parsed rails, the makers'
    rows in F and the tree's own files."""
    P = l9pwr(); o3 = item1_r3(); src = r4_sources(); o = {"src": src}
    st = P["states"]["PS-BUSY"]["rails"]; s1, s1f, s1a, s1b, s1c = st["S1"], st["S1F"], st["S1A"], st["S1B"], st["S1C"]
    fan_full = s1f["out"][2] / s1f["eta"]
    other = s1["out"][2] - fan_full
    pb = rvpwr()
    parts = {"CM5 slot 1 (8.0 W)": P["states"]["PS-BUSY"]["rails"]["S1"]["out"][2] - s1a["out"][2] / pb.eff_curve("AP64500_3V3", 12.0, s1a["out"][2] / 3.3)
             - s1b["out"][2] / pb.eff_curve("AP64500_3V3", 12.0, s1b["out"][2] / 3.3) - s1c["out"][2] / s1c["eta"] - fan_full,
             "card buck U103 (9.1 W)": s1a["out"][2] / pb.eff_curve("AP64500_3V3", 12.0, s1a["out"][2] / 3.3),
             "NVMe and switch 3.3 V buck U104 (3.99 W)": s1b["out"][2] / pb.eff_curve("AP64500_3V3", 12.0, s1b["out"][2] / 3.3),
             "switch core buck U105 (0.676 W)": s1c["out"][2] / s1c["eta"]}
    o["parts"] = parts; o["other"] = other; o["fan_full_w"] = fan_full
    duty = V["duty_max"]; cap_w = duty * s1f["out"][2] / s1f["eta"]
    lo_ap, nom_ap = vout_least(V["vfb_ap"], V["fb_div"]); lo_lm1, nom_lm = vout_least(V["vref_lm"], V["fb_div"])
    # round 6 (F5-03 corrected by apply_gen_sch_a_fb01.py): the LM5176 stages' divider at 0.1 %, IBIAS(FB) through the top resistor
    rt6, rb6, _t6 = V["fb_div"]; t01 = V["fb_tol01"]; bias_v = V["ibias_fb"] * rt6
    lo_lm = V["vref_lm"][0] * (1 + rt6 * (1 - t01) / (rb6 * (1 + t01))) - bias_v
    hi_lm = V["vref_lm"][2] * (1 + rt6 * (1 + t01) / (rb6 * (1 - t01))) + bias_v
    vl_ap, vl_lm = lo_ap * (1 - V["drop"]), lo_lm * (1 - V["drop"])
    vl_lm1 = lo_lm1 * (1 - V["drop"])
    rt, rb, tol = V["fb_div"]; hi_ratio = 1 + rt * (1 + tol) / (rb * (1 - tol))
    o["v"] = {"nominal_ap": nom_ap, "least_ap": lo_ap, "load_ap": vl_ap, "least_lm": lo_lm, "load_lm": vl_lm, "hi_lm": hi_lm,
              "least_lm1": lo_lm1, "load_lm1": vl_lm1, "bias_v": bias_v,
              "most_ap": V["vfb_ap"][2] * hi_ratio, "most_lm": V["vref_lm"][2] * hi_ratio}
    base, peak = slot_loads(open(GEN_B, encoding="utf-8").read())
    r3 = round(duty * V["pfan"] / V["eta"] / 5.0, 2)
    decl3 = sum(v for k, v in base[1].items() if k != "J_FAN1") + r3
    o["c1"] = [  # question 1: the figures, their state, their boundary
        ("+0.129 A (round 3's margin)", 5.0 - (other + cap_w) / 5.1, "PS-BUSY and PS-ALLTX at HIGH (every load at its maximum at once)",
         "the AP64500 U4's output (slot side): the CM5 8.0 W, the card 9.1 W, the NVMe and switch 3.99 W and the switch core 0.676 W through "
         "board B's bucks at their curve, the fan at 1.4 W (70 %% of 2.0 W, the linear bound) over the step-up's 0.85; %.3f W / 5.1 V = %.3f A against 5 A"
         % (other + cap_w, (other + cap_w) / 5.1)),
        ("+0.019 A (the declared 4.981 A)", 5.0 - decl3, "no state: a declaration board B's intent.rail judges",
         "board B's _SLOT_LOADS rows on +5V_S1 (CM5 1.6, U103 2.2, U104 0.7, U105 0.15, U116 0.001 A) and the fan's row %.2f A (1.4 W / 0.85 / 5.0 V) "
         "summed, %.3f A against the rail's declared 5.0 A peak (intent.rail refuses over 1.02 x, %.3f A: %+.3f A to the refusal)"
         % (r3, decl3, 1.02 * 5.0, 1.02 * 5.0 - decl3)),
        ("the same state at the least voltage", 5.0 - (other + cap_w) / vl_ap, "PS-BUSY at HIGH, the AP64500's least output less the rail's whole drop",
         "%.3f W / %.3f V = %.3f A: VFB %.3f V on the 1 %% divider gives %.3f V, less 2 %% %.3f V; every load behind a converter draws its "
         "power, so its current rises as its voltage falls" % (other + cap_w, vl_ap, (other + cap_w) / vl_ap, V["vfb_ap"][0], lo_ap, vl_ap)),
    ]
    o["rows_vs_decl"] = [(k, w / 5.1) for k, w in parts.items()]
    o["decl"] = dict(base[1]); o["decl3"] = decl3; o["r3_row"] = r3
    # question 2: the fan's input at 70 %
    (d1, a1, p1, n1, q1, s1p), (d2, a2, p2, n2, q2, s2p) = V["fan_rows"]
    r25 = n2 / n1; rr = [(V["n70"][0] + k * V["n70"][1]) / n1 for k in (-1, 0, 1)]
    b = (p1 - p2) / (1 - r25 ** 3); a = p1 - b
    law = [a + b * r ** 3 for r in rr]; chord = [p2 + (p1 - p2) * (r - r25) / (1 - r25) for r in rr]
    vh = 12.43; kv = (vh / 12.0) ** 3
    ef = item1()["efuse"]
    start_w = ef[2] * item1()["vout"][2]
    o["c2"] = {"r25": r25, "rr": rr, "law": law, "chord": chord, "linear": duty * p1, "kv": kv, "hi_70": max(chord) * kv, "hi_100": p1 * kv,
               "start_w": start_w, "start_slot_w": start_w / V["eta_lo"], "eff_typ": V["tps_eta_typ"],
               "loss": {e: max(chord) * (1 / e - 1) for e in (V["tps_eta_typ"], V["eta"], V["eta_lo"])},
               "room_nom": (5.0 * 5.1 - other) * V["eta"], "room_least": (5.0 * vl_ap - other) * V["eta"]}
    # question 3: the states, the slot's current at HIGH on the AP64500 as drawn and on the stage of the correction. Round 5 (the
    # collaborator's B2): every state with the fan at full speed takes the ENVELOPE, the fan's bound at the step-up's 12.43 V top
    # over the step-up's worst efficiency (fan_env over eta_lo), and the last duty after a firmware fault is up to 100 % (no maximum)
    env_branch = V["fan_env"] / V["eta_lo"]; env_w = other + env_branch
    rel = [r for r in o3["rows"] if r["state"] == "PS-BUSY" and r["slot"] == "1"][0]
    rel_w = rel["I"]["rel"] * 5.1 - fan_full + env_branch
    start_slot = o["c2"]["start_slot_w"]
    ef = item1()["efuse"]; vtop = item1()["vout"][2]
    degr_slot = ef[0] * vtop / V["eta_lo"]
    o["env"] = {"branch": env_branch, "w": env_w, "degr_slot": degr_slot, "efuse_lo": ef[0], "vtop": vtop}
    def both(wt):
        return wt / 5.1, wt / vl_ap, wt / vl_lm
    o["c3"] = [
        ("module off, slot rail on", "released: unpowered at the module's shutdown (CM5 2.11); R7x12 10 k to +5V_Sn", "low: R{s}06 100 k holds it, the module's 3.3 V off", "100 %", rel_w),
        ("boot (bootloader, kernel before its fan driver)", "not stated by the maker; the stock CM5 tree leaves the fan node disabled: taken released", "R{s}06 holds it low until software raises it; the bootloader's PCIe probe NOT STATED: taken high", "100 %", env_w),
        ("reset or a watchdog restart", "the module's reset state, not stated: taken released", "a warm restart keeps the module's 3.3 V; low only if the module lets go (NOT STATED): taken high", "100 %", env_w),
        ("firmware failure, PWM block running", "held at its last duty, up to 100 % (no maximum since round 4)", "high (the card on)", "the last duty, up to 100 %", env_w),
        ("firmware failure, fan driver absent or unbound", "released (the stock levels reach 250/255)", "high (the card on)", "98 to 100 %", env_w),
        ("PWM lead open (J_FANs pin 4, a broken brown lead)", "the fan's terminal open", "high (the card on)", "100 % (maker: open = 100 %)", env_w),
        ("a start with the card on (0 % stops this fan; a locked-rotor retry)", "any", "high (the card on)", "start: up to the eFuse's 0.538 A at 12.43 V (an assumed bound)", other + start_slot),
        ("a degraded fan held steady under the eFuse's least limit (a fault, no trip)", "any", "high (the card on)", "0.448 A at 12.43 V", other + degr_slot),
    ]
    o["c3_i"] = [both(row[4]) for row in o["c3"]]
    # B1: the AP64500's drawn frequency (68 k on DS41979 Eq. 7), its ripple and the start's peak there; the conduction term the
    # smaller ripple takes off (the only loss that falls with frequency)
    fsw_d = V["ap_eq7"] / (V["ap_rt"] / 1e3) * 1e3
    vo = 5.1
    def ripple_at(lf, ff, vin):
        return vo * (1 - vo / vin) / (V["ap_l"] * lf * fsw_d * ff)
    rip_nom = ripple_at(1.0, 1.0, V["vsys_max"]); rip_lo = ripple_at(1 - V["ap_ltol"], (1 - V["rt_tol"]) * (1 - V["fss"]), V["vsys_max"])
    st_i = (other + start_slot) / vl_ap
    rs = V["ap_rds"]; d12 = vo / 12.0; reff = (d12 * rs[0] + (1 - d12) * rs[1]) * V["rds_hot_ap"]
    r500 = vo * (1 - vo / 12.0) / (V["ap_l"] * 500e3); r1470 = vo * (1 - vo / 12.0) / (V["ap_l"] * fsw_d)
    o["b1"] = {"fsw": fsw_d, "rip_nom": rip_nom, "rip_lo": rip_lo, "start_i": st_i, "pk_nom": st_i + rip_nom / 2, "pk_lo": st_i + rip_lo / 2,
               "delta": (r500 ** 2 - r1470 ** 2) / 12 * reff, "cycles_ms": 512 / fsw_d * 1e3}
    o["ap_pk_start"] = o["b1"]["pk_nom"]
    # question 4: cooling (the basis against the pick at 70 %), the AP64500's junction, the stage's FET
    sun_cfm, sun_in = src["sunon"]; sun_pa = sun_in * 249.089; q_rep = sun_cfm * 0.3048 ** 3
    pmin, qmax = V["pq100"]
    r_lo = rr[0]
    o["c4"] = {"rep_q": q_rep, "rep_pa": sun_pa, "q100_needed": q_rep / r_lo, "p70_floor": r_lo ** 2 * pmin, "q70_free": [V["fan_rows"][0][4] * r for r in (rr[0], rr[2])],
               "p70_shut": [V["fan_rows"][0][5] * r ** 2 for r in (rr[0], rr[2])], "p50": V["pq50"], "flow_basis": src["h2"]}
    air = src["c1_air"]; th = V["ap_theta"][0]; tjr = V["ap_tj"][0]
    junction = []   # round 5: a SCREEN at the maker's 500 kHz curves, not a temperature of the drawn 1.47 MHz stage
    for tag, pout in (("(a) full speed", s1["out"][2]), ("(a) 70 % maximum", other + cap_w), ("(b) no cooler on the slot rail", other),
                      ("PLAN, PS-BUSY as drafted", s1["out"][1])):
        i = pout / 5.1
        for vin in (14.4, V["vsys_max"]):
            loss, eta = ap_loss(pout, i, vin)
            junction.append((tag, vin, i, eta, loss, air + loss * th))
    o["junction"] = junction; o["air"] = air
    lo, hi = 0.5, 5.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if air + ap_loss(mid * 5.1, mid, 14.4)[0] * th <= tjr: lo = mid
        else: hi = mid
    o["ap_i125"] = lo
    o["fig24"] = {"air": fig24(air)}
    def t24(i):
        (t0, i0), (t1, _i1) = V["ap_fig24"]
        return None if i > i0 else t0 + (t1 - t0) * (i0 - i) / i0
    o["fig24_t"] = {i: t24(i) for i in (s1["out"][2] / 5.1, (other + cap_w) / 5.1, other / 5.1)}
    # B1: the maker's typical Figure 24 against each option's current at the AP64500's least output (the envelope for (a))
    o["fig24_least"] = [(tag, wt / vl_ap, t24(wt / vl_ap)) for tag, wt in (("(a) the envelope, full speed", env_w),
                                                                         ("(a) 70 % maximum", other + cap_w),
                                                                         ("(b) no cooler on the slot rail", other))]
    # the correction: slots 1 and 3 on the LM5176 stage; the loop's least from record l9pwr's slot 2 line
    lm = [r for r in o3["rows"] if r["part"].startswith("LM5176")][0]["limit"]
    o["lm_limit_printed"] = lm
    o["lm_limit"] = V["vsns"][0] / (V["isns_r"][0] * (1 + V["isns_r"][1]))   # round 6: from the maker's VSNS and the shunt, unrounded
    corr = []
    for r in o3["rows"]:
        if r["slot"] not in ("1", "3"):
            continue
        base_w = r["I"]["a"] * 5.1 - fan_full
        corr.append((r["state"], r["slot"], (base_w + env_branch) / 5.1, (base_w + env_branch) / vl_lm, base_w / vl_lm + V["start_bound"],
                     (base_w + degr_slot) / vl_lm))
    o["corr"] = corr
    worst = max(c[3] for c in corr); worst_start = max(c[4] for c in corr); worst_degr = max(c[5] for c in corr)
    o["corr_worst"] = (worst, worst_start, worst_degr)
    fets = {}
    for vin in (V["vsys_max"], 9.688):
        p, terms, edges = qh1(worst, vin, vo, V["csd"][1])
        fets[vin] = (p, terms, edges, ql1(worst, vin, vo), worst ** 2 * V["csd"][0] * V["rds_hot"])
    o["fets"] = fets
    pq, _t, _e = qh1(worst, V["vsys_max"], vo, V["csd"][1])
    pq_dec, _t, _e = qh1(V["slot_peak"], V["vsys_max"], vo, V["csd"][1])
    pq_rr, _t, _e = qh1(worst, V["vsys_max"], vo, V["csd"][1], prop=False)
    o["fet_tj"] = {k: air + pq * V["csd"][k] for k in (1, 2)}
    o["fet_dec"] = (pq_dec, air + pq_dec * V["csd"][1])
    o["fet_rr"] = (pq_rr, air + pq_rr * V["csd"][1])
    o["fet_rth_for_125"] = (125.0 - air) / pq
    o["fet_rth_for_125_rr"] = (125.0 - air) / pq_rr
    dev = [d for d in o3["dev"] if d["state"] == "PS-ALLTX"][0]
    pdv, _t2, _e2 = qh1(dev["drafted"], V["vsys_max"], vo, V["csd"][1])
    o["dev_fet"] = (dev["drafted"], pdv, air + pdv * V["csd"][1])
    # the declared slot peak and VBAT entry of the correction (round 5: the envelope)
    o["peak_need"] = max(c[4] for c in corr)
    o["start_calc"] = start_slot / vl_lm   # the eFuse-limited calculation's branch current, inside the bounded bound
    st2 = P["states"]["PS-BUSY"]["rails"]["S2"]
    o["slot2_start"] = (st2["out"][2] - P["states"]["PS-BUSY"]["rails"]["S2F"]["out"][2] / P["states"]["PS-BUSY"]["rails"]["S2F"]["eta"]) / vl_lm + V["start_bound"]
    # B3: the junction screen over C4-1's whole steady matrix at the highest VIN, scaled and unscaled recovery; the RthJA each needs
    pts = list(V["matrix"]) + [env_w / vl_lm, V["slot_peak"]]
    o["matrix_fet"] = [(i,) + tuple(qh1(i, V["vsys_max"], hi_lm, V["csd"][1], prop=pr)[0] for pr in (True, False)) for i in pts]
    o["matrix_rth"] = [(i, (125.0 - src["c1_air"]) / pu) for i, _ps, pu in o["matrix_fet"]]
    o["entry"] = V["slot_peak"] * 5.1 / (V["eta_lm"] * 14.4)
    # the LM5176 stage's output window against the CM5's 5 V input, at the drawn 1 % divider and with 0.1 % parts
    lo1, _n1 = vout_least(V["vref_lm"], (V["fb_div"][0], V["fb_div"][1], 0.001))
    rt_, rb_, _t3 = V["fb_div"]
    o["lm_window"] = {"lo": lo_lm1, "hi": o["v"]["most_lm"], "lo01": lo1,
                      "hi01": V["vref_lm"][2] * (1 + rt_ * 1.001 / (rb_ * 0.999)), "cm5": V["cm5_vin"]}
    # the energy the two stages cost at PLAN (VBAT side), every state, at the declared 0.90 against the AP64500's curve point
    energy = []
    for stn, d in P["states"].items():
        dw = 0.0
        for n in ("S1", "S3"):
            rl = d["rails"].get(n)
            if rl and rl["kind"] == "curve":
                dw += rl["out"][1] * (1 / V["eta_lm"] - 1 / rl["eta"])
        energy.append((stn, dw))
    o["energy"] = energy
    # board B's declared loads with round 5's draft applied (the fan row at the envelope, the three slots at 5.63 A)
    with tempfile.TemporaryDirectory() as d:
        pth = os.path.join(d, "b.py"); shutil.copy(GEN_B, pth)
        rc, msg = run(draft("l8r2", "fans12", "b"), pth)
        if rc:
            raise SystemExit("l8r2_drafts: the coolers' draft refused a copy of gen_sch_b.py: %s" % msg)
        b4, peak4 = slot_loads(open(pth, encoding="utf-8").read())
    o["decl4"] = (sum(b4[1].values()), peak4[1], intent_says(peak4[1], b4[1]), peak4[2], peak4[3])
    o["fan_row"] = b4[1]["U701"]
    return o



def item1_r4_print(w):
    o = item1_r4(); s = o["src"]; v = o["v"]; c2 = o["c2"]; c4 = o["c4"]; D = V["duty_max"]
    w("\n2c. ROUND 4, CORRECTED IN ROUND 5: L9P-F02'S FOCUSED CHECK (the owner's questions 1 to 5 and the collaborator's B1 to B3; record l9pwr's rails parsed; the cooler's rows from Sanyo Denki's San Ace catalogue C1152B001 '25.10, held back)\n")
    w("  1. THE TWO MARGINS: what each figure is\n")
    for lab, fig, state, bound in o["c1"]:
        w("    %-38s %+.3f A; state: %s;\n      boundary: %s\n" % (lab, fig, state, bound))
    names = {"CM5 slot 1 (8.0 W)": "U30A", "card buck U103 (9.1 W)": "U103", "NVMe and switch 3.3 V buck U104 (3.99 W)": "U104", "switch core buck U105 (0.676 W)": "U105"}
    w("    each slot-side current at HIGH (5.1 V) beside board B's declared row: %s; the fan %.3f A at the 70 %% bound against its row %.2f A\n"
      % ("; ".join("%s %.3f A (row %.2f)" % (k, a, o["decl"][names[k]]) for k, a in o["rows_vs_decl"]), D * o["fan_full_w"] / 5.1, o["r3_row"]))
    w("    the two sums are of different things (a load's maximum at its state; a load's declared row), and neither bounds the other\n")
    w("    VERDICT: NOT A MARGIN. +0.129 A holds only at the nominal 5.1 V (the divider's nominal %.3f V); at the AP64500's least output %.3f V less the rail's 2 %% drop, %.3f V at the loads, the same state reads %+.3f A. 0.019 A is the declaration's distance from the source's 5 A rating, in no state\n"
      % (v["nominal_ap"], v["least_ap"], v["load_ap"], o["c1"][2][1]))
    rows = V["fan_rows"]
    w("  2. THE FAN'S INPUT AT 70 % PWM, supported data only\n")
    w("    the maker's rows (12 V, free air, p.362): %s; 'When control terminal is open, speed is the same as at 100%% duty cycle'; 'Models without ratings for 0%% PWM duty cycle have zero speed at 0%%'; PWM at 25 kHz\n"
      % "; ".join("%d %%: %.2f A, %.2f W, %d min-1, %.2f m3/min, %.1f Pa" % r for r in rows))
    w("    the speed at 70 %% (p.362's duty to speed example, read): %.0f +- %.0f min-1, %.3f to %.3f of the rated speed\n" % (V["n70"] + (c2["rr"][0], c2["rr"][2])))
    w("    the input at 70 %% (12 V, free air): NOT PRINTED, UNRESOLVED. Bracketed (INFERRED): the fan law through both printed rows (a fixed share plus the cube of the speed) %.2f to %.2f W; the chord in speed between them, the upper bound while the input is convex in speed, %.2f to %.2f W; round 3's linear bound %.2f W lies INSIDE the bracket, so it bounds nothing\n"
      % (c2["law"][0], c2["law"][2], c2["chord"][0], c2["chord"][2], c2["linear"]))
    w("    the supply: the step-up's 11.51 to 12.43 V inside the fan's 10.8 to 13.2 V; the maker prints the input at 12 V only; at 12.43 V the fan laws (speed with voltage) give x%.3f: up to %.2f W at 70 %%, %.2f W at 100 %% (INFERRED)\n"
      % (c2["kv"], c2["hi_70"], c2["hi_100"]))
    w("    against the cooler's own pressure (not free air): the maker prints no input at a static pressure: UNRESOLVED\n")
    w("    the start: 'When voltage is applied or fluctuates ... current several times the rated current may flow' (p.633), no figure: UNRESOLVED; a locked rotor 'the coil current is cut off at regular cycles ... the fan restarts automatically' (p.616); a current-limited power at the eFuse's inferred highest limit, %.3f W on the 12 V side, %.2f W on the slot rail at the step-up's assumed %.2f: a CONDITIONAL calculation, not an instantaneous bound (the limit's response time and the step-up's own start are finite, SLVSET8A pp.6 to 7, SLVSD38C 8.3.3)\n"
      % (c2["start_w"], c2["start_slot_w"], V["eta_lo"]))
    w("    the step-up's loss at the bracket's top: %s (TI's Figure 7-2 is typical at 3.6 V in, not the slot's 4.829 to 5.252 V; no held source makes 0.80 a minimum: an ASSUMPTION the envelope takes and C4-3 measures)\n" % ", ".join("%.2f W at %.2f" % (l, e) for e, l in sorted(c2["loss"].items(), reverse=True)))
    w("    the slot's other loads at HIGH (PS-BUSY): %.3f W; the fan input the AP64500's 5 A leaves at %.2f: %.2f W at 5.1 V, %.2f W at its least %.3f V, under even the fan law's least at 70 %% (%.2f W)\n"
      % (o["other"], V["eta"], c2["room_nom"], c2["room_least"], v["load_ap"], c2["law"][0]))
    e = o["env"]; b1 = o["b1"]
    w("  3. THE STATES (round 5: every full-speed state at the ENVELOPE, the fan's %.2f W bound at %.2f V over %.2f, %.4f W on the slot rail; the slot at HIGH; A at 5.1 V / at the AP64500's least %.3f V / at the LM5176 stage's least %.3f V)\n"
      % (V["fan_env"], e["vtop"], V["eta_lo"], e["branch"], v["load_ap"], v["load_lm"]))
    for (state, pwm, pce, fan, _w), (i1, i2, i3) in zip(o["c3"], o["c3_i"]):
        w("    %-62s Fan_PWM %s; PCIE_PWR_EN %s; the fan %s: %.3f / %.3f / %.3f A; AP64500 (5 A) %s; LM5176 (%.3f A) %+.3f A\n"
          % (state + ":", pwm, pce, fan, i1, i2, i3, "%+.3f A" % (5.0 - i2) + (" OVER" if i2 > 5.0 else ""), o["lm_limit"], o["lm_limit"] - i3))
    w("    the AP64500 at its DRAWN frequency (B1): RT %.0f k on DS41979 Eq. 7 sets %.1f kHz, not the 500 kHz of the maker's curves; its ripple at %.3f V in %.3f A (nominal L and frequency), %.3f A (L 20 %% low, the oscillator %.0f %% and the spread spectrum %.0f %% low)\n"
      % (V["ap_rt"] / 1e3, b1["fsw"] / 1e3, V["vsys_max"], b1["rip_nom"], b1["rip_lo"], 100 * V["rt_tol"], 100 * V["fss"]))
    w("    a start with the card on (the eFuse-limited bound, an ASSUMPTION): %.3f A; the inductor's peak %.3f A nominal, %.3f A at the low corner, against the HS peak limit's %.1f to %.1f A: the limit MAY act at the low corner and need not; hiccup needs it for 512 consecutive cycles (%.3f ms at the drawn frequency), and the start's size and duration are not printed: POSSIBLE, NOT ESTABLISHED, UNRESOLVED\n"
      % (b1["start_i"], b1["pk_nom"], b1["pk_lo"], V["ap_ipk"][0], V["ap_ipk"][2], b1["cycles_ms"]))
    w("    the module's own words (CM5 datasheet 2.11 and the pin table): '%s' '%s' '%s'\n" % (s["cm5_oc"], s["cm5_shut"], s["cm5_pe"]))
    w("    the stock CM5 tree (linux bcm2712-rpi-cm5.dtsi, held): the fan node %s; cooling levels %s of 255; period %d ns, %.2f kHz against the maker's 25 kHz\n"
      % (s["dts"][0], " ".join(str(x) for x in s["dts"][1]), s["dts"][2], 1e6 / s["dts"][2]))
    w("    the fan's PWM lead pulled by R7x12 to +5V_Sn: at most %.3f V on the AP64500 stage, %.3f V on the LM5176 stage (the reference's highest on the divider's highest ratio), against the catalogue example's VIH %.2f to %.2f V and its open terminal's %.2f V at most; the model's own level is the maker's question (C4-4)\n"
      % ((v["most_ap"], v["most_lm"]) + V["pwm_in"][0] + (V["pwm_in"][4],)))
    w("    board B (gen_sch_b.py, read): R{s}06 100 k holds PCIE_PWR_EN{s} low (%s); the card's supply enable U{s}16 = EMCON_HW AND PCIE_PWR_EN{s} (%s)\n"
      % ("READ" if s["pce_pd"] else "NOT READ", "READ" if s["gate"] else "NOT READ"))
    w("    VERDICT: full speed is the default in every state the firmware does not drive; with the card on the AP64500 is over 5 A at the envelope in each (and its HS limit may act in a start); the 70 % maximum, withdrawn, held in none of them\n")
    w("  4. COOLING AND THE CONVERTER'S OWN THERMAL CAPABILITY\n")
    w("    the approved basis (record l4e12 2h, parsed): the representative fan's %.1f CFM free air at %.0f %% through the heatsink, %.3f l/s, the CM5's %.1f W and the fan's %.2f W lift the exhaust %.2f K; that fan (Sunon MF30060V2) %.1f CFM and %.2f inch H2O (%.1f Pa) at most\n"
      % (s["h2"] + (s["sunon"][0], s["sunon"][1], c4["rep_pa"])))
    w("    the pick at 70 %% (the fan laws on p.362's 100 %% curve at the speed's least reading): at least %.1f Pa at every flow up to the representative's %.3f m3/min (the 100 %% curve read at %.3f m3/min, inside its %.0f Pa plateau to %.2f); free air %.3f to %.3f m3/min; shut-off %.0f to %.0f Pa\n"
      % (c4["p70_floor"], c4["rep_q"], c4["q100_needed"], V["pq100"][0], V["pq100"][1], c4["q70_free"][0], c4["q70_free"][1], c4["p70_shut"][0], c4["p70_shut"][1]))
    w("    VERDICT: under the fan laws and an unchanged air path the pick's curve at 70 %% lies over the representative's at every flow, so it moves more air through the same heatsink: the approved airflow HOLDS at 70 %% (at 50 %% the maker's curve reads about %.0f +- 5 Pa at 3.7 CFM against %.1f Pa: inside the reading's resolution, not claimed)\n" % (c4["p50"], c4["rep_pa"]))
    w("    the SoC at 8 W against the cooler (the module throttles to keep it under 85 C, CM5 4.4): no held document gives the cooler's thermal resistance against airflow: UNRESOLVED (C4-5)\n")
    w("    the AP64500's junction (B1): no Diodes curve is printed at the drawn %.0f kHz (Figures 2, 4, 5 and 24 are 500 kHz with 200 k), so no junction of the drawn stage is computed. Two statements stand:\n" % (b1["fsw"] / 1e3))
    w("      (i) a 500 kHz SCREEN by record l4e12's method (the converter's loss at its point x theta-JA %.0f C/W at C1's %.0f C), not a temperature of the drawn stage:\n" % (V["ap_theta"][0], o["air"]))
    for tag, vin, i, eta, loss, tj in o["junction"]:
        w("        %-30s VIN %6.3f V: %.3f A, eta %.4f, loss %.3f W, screen %.1f C (%s)\n" % (tag, vin, i, eta, loss, tj, "over +125 C" if tj > V["ap_tj"][0] else "within +125 C"))
    w("      (ii) a CONDITIONAL thermal screen (round 6, the recheck's B1): the maker's typical Figure 24 (500 kHz, VIN 12 V, read +- 2 C) at each option's current at the least load voltage %.3f V: %s\n"
      % (v["load_ap"], "; ".join("%s %.3f A: %s" % (tg, i, "over the 5 A rating at any air (the rating, not the curve)" if tl is None else "the typical curve ends at %.1f +- 2 C" % tl) for tg, i, tl in o["fig24_least"])))
    w("      no loss comparison at the drawn %.0f kHz covering VIN, inductance and the source is held, so the 500 kHz curve is NOT claimed as a bound on the drawn stage: the retired part needs no characterisation\n" % (b1["fsw"] / 1e3))
    w("    VERDICT: the fan-fed options exceed the AP64500's 5 A rating at the least load voltage (MAKER); the no-fan option (b) reads past the typical curve at C1's %.0f C in this screen only (CONDITIONAL): NOT ADEQUATELY RATED with the cooler on the rail; (b) rejected on its interfaces, its thermal screen CONDITIONAL\n" % o["air"])
    w("  5. THE CORRECTION: slots 1 and 3 on slot 2's LM5176 stage (apply_gen_sch_a_slotlm.py), the 5.1 V stages' dividers at 0.1 % (apply_gen_sch_a_fb01.py, round 6), the coolers at full speed on their step-up (apply_gen_sch_b_fans12.py), no Fan_PWM maximum; board B's slot bucks at 500 kHz (apply_gen_sch_b_rt500.py, round 5)\n")
    w("    the output window (F5-03): %.3f to %.3f V with the 1 %% divider (round 5); with both resistors at 0.1 %% and IBIAS(FB) %.0f nA through %.1f k (%.2f mV) %.4f to %.4f V, inside the CM5's %.2f to %.2f V with %.1f mV to its top before the load's transient (C4-1 measures it); the least load voltage with the 2 %% drop %.4f V (round 5: %.4f V)\n"
      % (o["lm_window"]["lo"], o["lm_window"]["hi"], V["ibias_fb"] * 1e9, V["fb_div"][0] / 1e3, v["bias_v"] * 1e3, v["least_lm"], v["hi_lm"],
         V["cm5_vin"][0], V["cm5_vin"][1], 1e3 * (V["cm5_vin"][1] - v["hi_lm"]), v["load_lm"], v["load_lm1"]))
    w("    the loop's least: VSNS %.0f mV over %.0f mOhm at +%.0f %%: %.6f A (record l9pwr prints %.3f A)\n"
      % (V["vsns"][0] * 1e3, V["isns_r"][0] * 1e3, 100 * V["isns_r"][1], o["lm_limit"], o["lm_limit_printed"]))
    w("    per state (B2): the steady ENVELOPE at 5.1 V / at the least %.4f V; the BOUNDED START (the cooler branch at its %.2f A bound, a 100 us average); a degraded cooler held under its eFuse's least limit; margin to %.4f A:\n"
      % (v["load_lm"], V["start_bound"], o["lm_limit"]))
    for st, sl, a1, a2, a3, a4 in o["corr"]:
        w("      %-12s slot %s  %.4f / %.4f A  start %.4f A  degraded %.4f A  %+.4f / %+.4f / %+.4f A\n" % (st, sl, a1, a2, a3, a4, o["lm_limit"] - a2, o["lm_limit"] - a3, o["lm_limit"] - a4))
    cw = o["corr_worst"]
    w("    least margin: %+.4f A at the steady envelope (%.1f %%); %+.4f A at the bounded start; %+.4f A with a degraded cooler; %+.4f A at the declared %.1f A\n"
      % (o["lm_limit"] - cw[0], 100 * (o["lm_limit"] - cw[0]) / o["lm_limit"], o["lm_limit"] - cw[1], o["lm_limit"] - cw[2], o["lm_limit"] - V["slot_peak"], V["slot_peak"]))
    w("    the eFuse-limited start calculation (an ASSUMPTION, 0.538 A at 12.43 V over 0.80) gives %.4f A of branch current at %.4f V, inside the %.2f A bound; the eFuse's own response is %.0f us typical (tLIM), the bound's 100 us average spans it\n"
      % (o["start_calc"], v["load_lm"], V["start_bound"], V["tlim"] * 1e6))
    w("    slot 2 (its own HIGH, the cooler's bounded start): %.4f A, inside the same %.1f A; its S-98 coincidence (5.63 A) inside it; I-03's all-peak bound stays I-03's\n" % (o["slot2_start"], V["slot_peak"]))
    for vin, (p, terms, (tr, tf), pl1, ph2) in sorted(o["fets"].items(), reverse=True):
        w("    the stage's buck-side high FET at %.4f A, VIN %.3f V: %s; %.3f W (edges %.1f / %.1f ns); the low FET %.3f W; the boost-side high FET %.3f W\n"
          % (cw[0], vin, ", ".join("%s %.3f" % kv for kv in terms.items()), p, tr * 1e9, tf * 1e9, pl1, ph2))
    w("    B3, the junction SCREEN over C4-1's steady matrix (VIN %.3f V, the output at its highest %.4f V; estimates on typical charges and an assumed hot RDS(on), not bounds): %s\n"
      % (V["vsys_max"], v["hi_lm"], "; ".join("%.4f A: %.3f W scaled, %.3f W unscaled Qrr, RthJA for +125 C at %.0f C %.2f C/W" % (i, ps, pu, o["air"], rth) for (i, ps, pu), (_i, rth) in zip(o["matrix_fet"], o["matrix_rth"]))))
    w("      the binding acceptance is C4-1's measured bound: each FET's case plus the stage's MEASURED loss (input less output power, at least any one FET's) times RthJC 0.8 C/W at most +125 C at every steady point; the sheet's +%.0f C is an absolute maximum\n" % V["csd"][3])
    w("    the same arithmetic on the device rail's stage at %.3f A (PS-ALLTX, DRAFTED): %.3f W, %.1f C on 1 inch2 (a finding for board A's owner)\n" % o["dev_fet"])
    w("    the declared peak (B2): the bounded start-up and fault envelope needs %.4f A; %.1f A declared at both ends on all three slots; VBAT's entries %.3f A, declared %.2f A\n" % (o["peak_need"], V["slot_peak"], o["entry"], round(o["entry"], 2)))
    d4 = o["decl4"]
    w("    board B with round 6's draft: slot 1's declared loads %.3f A (the fan row %.2f A) against %.2f A: %s; slot 2 %.2f A, slot 3 %.2f A\n" % (d4[0], o["fan_row"], d4[1], d4[2], d4[3], d4[4]))
    w("    the energy at PLAN, VBAT side (the stages' declared %.2f against the AP64500's curve point, slots 1 and 3): %s\n"
      % (V["eta_lm"], "; ".join("%s %+.3f W" % e2 for e2 in o["energy"])))
    w("    SELECTED (SESSION): slots 1 and 3 on the LM5176 stage, the coolers at full speed on their step-up; round 3's 70 % Fan_PWM maximum WITHDRAWN\n")


def compose_e_print(w, d):
    er = [draft(r, n, "e") for r, n in E_ROUND]; mine = [draft(r, n, "e") for r, n in MINE_E]
    w("\n6b. COMPOSITION ON BOARD E (scratch copies of gen_sch_e.py; the change list's board E round, d8dec31's cin last, and this record's pack return)\n")
    page = e_round_page()
    w("  the change list's board E round as L4-POWER-ARCHITECTURE.md's table gives it: %s: %s\n"
      % (", ".join(page), "the same as this script's E_ROUND" if page == [os.path.basename(x) for x in er] else "DIFFERENT from this script's E_ROUND"))
    for tag, seq in (("the round, then this record's packrtn", er + mine), ("this record's packrtn first, then the round", mine + er),
                     ("the round with this record's packrtn before cin", er[:-1] + mine + er[-1:])):
        _p, res = compose_e(seq, d, "e_" + tag.split()[-1])
        bad = [(s, v) for s, v in res if v != "OK"]
        w("  %-50s %s\n" % (tag + ":", "OK at every step (%d drafts)" % len(res) if not bad and len(res) == len(seq) else bad))
    bad = []
    for k in range(len(er) + 1):
        _p, res = compose_e(er[:k] + mine, d, "e_prefix_%d" % k)
        if any(v != "OK" for _s, v in res) or len(res) != k + 1:
            bad.append((k, res[-1]))
    w("  this record's packrtn after every prefix of the round (0 to %d drafts; the round's drafts depend on one another, so none is applied alone): %s\n"
      % (len(er), "OK at every prefix" if not bad else bad))


def designators_e(d):
    er = [draft(r, n, "e") for r, n in E_ROUND]; mine = [draft(r, n, "e") for r, n in MINE_E]
    p = os.path.join(d, "e_desig.py"); shutil.copy(GEN_E, p)
    before = open(p, encoding="utf-8").read(); out = {}
    for s in er + mine:
        rc = run_e(s, p)[0]
        after = open(p, encoding="utf-8").read()
        out[os.path.relpath(s, RECS)] = added(before, after, s) if rc == 0 else None
        before = after
    return p, out


def netlist_pins(path):
    sp = importlib.util.spec_from_file_location("l8r2_check_r3", os.path.join(HERE, "check_l8r2_netlist.py"))
    chk = importlib.util.module_from_spec(sp); sp.loader.exec_module(chk)
    return chk.read_netlist(open(path, "rb").read())["pins"]


def item5_print(w):
    rows, ret = l9stk_rows()
    w("\n9. ITEM 5, THE PACK PATH'S RETURN ON BOARDS A AND E (record l9stk's finding, its output: \"returns declared in the intents: %s\")\n" % ret)
    for key in (("A", "CELL+"), ("E", "CELL_F")):
        r = rows[key]
        w("  record l9stk's widths, board %s %s at %.2f A (governing): one 1 oz face %.2f mm, each of two %.2f mm; one 2 oz face %.2f mm, each of two %.2f mm\n"
          % (key[0], key[1], r[2], r[3], r[4], r[5], r[6]))
    with tempfile.TemporaryDirectory() as d:
        for letter, gen, fwd, net, names in (("A", GEN_A, [draft(r, n, "a") for r, n in POWER_A + L8_A], NET_A, ("CELL+", "GND")),
                                             ("E", GEN_E, [draft(r, n, "e") for r, n in E_ROUND + MINE_E], NET_E, ("CELL_F", "GND"))):
            p = os.path.join(d, letter + ".py"); shutil.copy(gen, p)
            rc, msg = (run if letter == "A" else run_e)(draft("l8r2", "packrtn", letter.lower()), p)
            if rc:
                raise SystemExit("l8r2_drafts: the pack return's draft refused board %s's generator: %s" % (letter, msg))
            got = rail_calls(open(p, encoding="utf-8").read(), names)
            g = got["GND"][1] or {}
            src = g.get("source"); src = list(src) if isinstance(src, (list, tuple)) else [src]
            w("  board %s, the draft alone: GND a rail, sources %s, loads %s (%.2f A), %.1f / %.1f A, returns %s, share %.1f %%; intent.py on the file's %s and GND declarations: %s\n"
              % (letter, ", ".join(src), ", ".join("%s %g" % kv for kv in g.get("loads", {}).items()), sum(g.get("loads", {}).values()),
                 g.get("amps_typ", 0), g.get("amps_peak", 0), g.get("returns"), 100 * g.get("share", 0), names[0],
                 "; ".join("%s %s" % (k, v[0]) for k, v in got.items())))
            pins = netlist_pins(os.path.join(ROOT, net))
            on = []
            for ref in src + list(g.get("loads", {})):
                gp = sorted((pn for pn, n in pins.get(ref, {}).items() if str(n).lstrip("/") == "GND"), key=lambda x: (len(x), x))
                on.append("%s %s" % (ref, ",".join(gp) if gp else "NONE"))
            w("    on the committed netlist (%s), each source and load's pins on GND: %s: %s\n"
              % (os.path.basename(net), "; ".join(on), "YES" if all(not x.endswith("NONE") for x in on) else "NO"))
            if letter == "A":
                _q, res = compose(GEN_A, fwd, d, "A_fwd")
            else:
                _q, res = compose_e(fwd, d, "E_fwd")
            got2 = rail_calls(open(_q, encoding="utf-8").read(), names)
            w("    after the whole round (%d drafts, this one last): %s\n" % (len(res), "; ".join("%s %s" % (k, v[0]) for k, v in got2.items())))
    w("  the bar each return is judged against (dc_drop, PI-002): its share, 0.5 %%, of the rail it returns, %.1f mV of 14.4 V; the rules that then judge it: PI-001 (conductor capacity at the declared 18 A), PI-002 (the drop), PI-003 (the barrels), PWR-001 (the rail on the netlist), THM-001 (its watts not counted twice)\n"
      % (0.005 * 14.4 * 1e3))


def item6_print(w):
    o = item6(); rows, _ret = l9stk_rows()
    text = open(os.path.join(ROOT, CHAIN), encoding="utf-8").read()
    w("\n10. ITEM 6, THE ENERGY CHAIN'S BOARD E TEXTS AT 1 OZ (record l9stk's second finding; %s)\n" % CHAIN)
    def oz_lines(tx):
        sid, board, out = None, None, []
        for i, l in enumerate(tx.splitlines(), 1):
            m = re.match(r"^ - id: (\S+)", l)
            if m:
                sid = m.group(1)
            m = re.match(r"^   board: (.+)$", l)
            if m:
                board = m.group(1).strip('"')
            if "2 oz" in l:
                out.append("%d (%s, board %s)" % (i, sid, board))
        return out
    w("  lines naming 2 oz: %s\n" % "; ".join(oz_lines(text)))
    sp = importlib.util.spec_from_file_location("chain_fix", os.path.join(ROOT, CHAIN_FIX))
    fx = importlib.util.module_from_spec(sp); sp.loader.exec_module(fx)
    w("  the correction rewrites %s; board P's and E5's 2 oz (owner ruling 7) stay\n" % ", ".join(s for s, *_r in fx.EDITS))
    w("  widths at 10 K, decision 35's model (track_current.width_for_current), each of two 1 oz faces (one face): 25 A %.2f mm (%.2f); 18 A %.2f mm (%.2f), record l9stk's %.2f (%.2f): %s; 10 A %.2f mm (%.2f)\n"
      % (o["w25"][0], o["w25"][1], o["w18"][0], o["w18"][1], rows[("E", "CELL_F")][4], rows[("E", "CELL_F")][3],
         "EQUAL" if abs(o["w18"][0] - rows[("E", "CELL_F")][4]) < 0.006 and abs(o["w18"][1] - rows[("E", "CELL_F")][3]) < 0.006 else "DIFFERENT",
         o["w10"][0], o["w10"][1]))
    named = ("%.2f mm on each of two 1 oz faces" % o["w25"][0] in fx._DOCK_BASIS
             and "%.2f mm on each of two 1 oz faces or %.2f mm on one" % (o["w10"][0], o["w10"][1]) in fx._SHORE_BASIS)
    w("  the corrected texts name those widths: %s\n" % ("YES" if named else "NO"))
    with tempfile.TemporaryDirectory() as d:
        ch = os.path.join(d, "chain.yaml"); shutil.copy(os.path.join(ROOT, CHAIN), ch)
        reg = os.path.join(d, "decisions.yaml")
        shutil.copy(os.path.join(TOOLS, "pcb_decisions.yaml"), reg)
        go = lambda *a: subprocess.run([sys.executable, "-B", os.path.join(ROOT, CHAIN_FIX)] + list(a), capture_output=True)
        r0 = go("--chain", ch)
        open(reg, "a", encoding="utf-8").write('  - n: 999\n    title: "Board E\'s stackup: four layers at 1 oz outer and 0.5 oz inner (L9STK E)"\n    status: ruled\n')
        r1 = go("--chain", ch, "--registry", reg); r2 = go("--chain", ch, "--registry", reg, "--write"); r3 = go("--chain", ch, "--registry", reg, "--write")
        last = lambda r: (r.stdout.decode().strip().splitlines() or r.stderr.decode().strip().splitlines() or [""])[-1].split(": ", 1)[-1]
        w("  the apply script: on the tree's register (exit %d) %s\n" % (r0.returncode, last(r0)))
        w("    on a copy of the register carrying a ruled \"(L9STK E)\" decision: --check exit %d (%s); --write exit %d (%s); again exit %d (%s)\n"
          % (r1.returncode, last(r1), r2.returncode, last(r2), r3.returncode, last(r3)))
        sys.path.insert(0, TOOLS)
        import energy_chain as ec
        a, b = ec.check(os.path.join(ROOT, CHAIN), None), ec.check(ch, None)
        keys = ("fails", "stage_fails", "derate_fails")
        w("  energy_chain.check on the tree's chain and on the corrected copy (%d and %d checks): %s; %s\n"
          % (a["checked"], b["checked"], ", ".join("%s %d / %d" % (k, len(a.get(k) or []), len(b.get(k) or [])) for k in keys),
             "IDENTICAL" if all(a.get(k) == b.get(k) for k in keys) and a["checked"] == b["checked"] else "DIFFERENT"))
        w("  lines naming 2 oz after the correction: %s\n" % "; ".join(oz_lines(open(ch, encoding="utf-8").read())))
    w("  what the copper must carry for the chain's coordination (the blade at or below its conductor's rating): DOCK_ENTRY's 25 A needs %.2f mm on each of two 1 oz faces; record l9stk's band of %.2f mm on each of two carries %.2f A: FINDING\n"
      % (o["w25"][0], rows[("E", "CELL_F")][4], o["a_672_two"]))
    w("  board E's input band as gen_pcb_e3.py lays it (DC_HS, one B.Cu band: run %.1f mm, leg %.1f mm): %.2f and %.2f A at 1 oz (%.2f and %.2f at 2 oz), under SHORE_INPUT's F1 10 A at 1 oz: FINDING\n"
      % (o["dchs"] + o["dchs_1oz"] + o["dchs_2oz"]))


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
    w("  choice (a), a step-up per slot (SELECTED): %.3f W on +5V_Sn per slot at full speed, %.3f A at 5.1 V (%.3f A at 4.9 V), +%.3f W of conversion per slot; the three %.2f W at VBAT behind the slot converters (record l9pwr's R9 on each slot rail's own converter; round 2 printed %.2f W on a flat 0.90)\n"
      % (o["slot_w"], o["slot_a"], o["slot_a_min"], o["slot_w"] - V["pfan"], o["a_vbat"], o["a_vbat_r2"]))
    w("  choice (b), one 12 V feed from board A over the bay harness: the three %.2f W at VBAT (board A's converter at %.2f, an ASSUMPTION); (b) is %.2f W lower at full speed, %.2f W at the budget's 0.56 W a fan\n"
      % (o["b_vbat"], V["eta_a"], o["a_minus_b"], o["a_minus_b"] * 0.56 / V["pfan"]))
    item1_r3_print(w)
    item1_r4_print(w)

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
        late = [draft(r, n, "a") for r, n in AFTER_CHARGER]; first = [x for x in mya if x not in late]
        charger = [x for x in pa if x.endswith("_charger.py")]
        _p, res = compose(GEN_A, pa + l8a, d, "a_fwd", mainpb_last=True)
        w("  L4-E9's power order, l8gnd's two, this record's four, then d8dec31's mainpb:\n")
        for s, v in res: w("    %-42s %s\n" % (s, v))
        _p, res = compose(GEN_A, first + pa + l8a[:2] + late, d, "a_rev", mainpb_last=True)
        w("  this record's first three first, then the power order, l8gnd's two, slotlm (after the charger) and mainpb (every anchor of theirs still applies after these):\n")
        for s, v in res: w("    %-42s %s\n" % (s, v))
        w("  each power draft alone after this record's drafts (slotlm too, but before the charger; the bank after r12, which it requires):\n")
        r12 = [x for x in pa if x.endswith("_r12.py")]
        for s in pa:
            p = os.path.join(d, "alone_" + os.path.basename(s)); shutil.copy(GEN_A, p)
            ok = all(run(m, p)[0] == 0 for m in first + ([] if s in charger else late) + (r12 if s.endswith("_bank.py") else []))
            rc, msg = run(s, p)
            w("    %-42s %s\n" % (os.path.relpath(s, RECS), "OK" if ok and rc == 0 else "REFUSED (%s)" % msg))
        _p, res = compose(GEN_A, late + charger, d, "a_order1")
        _p2, res2 = compose(GEN_A, charger + late, d, "a_order2")
        w("  the order constraint (round 4): slotlm then L4-E11's charger: %s; the charger then slotlm: %s\n"
          % ("REFUSED, as expected: the charger's anchor names VBAT's \"U4\": 2.0, which slotlm rewrites" if res[-1][1] != "OK" else "OK (no constraint)",
             "OK" if all(v == "OK" for _s, v in res2) else res2))
        pk = [x for x in mya if x.endswith("_packrtn.py")]
        _p, _r = compose(GEN_A, pk + late, d, "a_pk1"); _p2, _r2 = compose(GEN_A, late + pk, d, "a_pk2")
        w("  this record's pack return and slotlm in either order give one generator: %s\n"
          % ("YES" if open(_p, "rb").read() == open(_p2, "rb").read() and all(v == "OK" for _s, v in _r + _r2) else "NO"))
        _p, res = compose(GEN_A, l8a[::-1], d, "a_l8rev")
        w("  the six Layer 8 drafts of board A in reverse order: %s\n" % ("OK" if all(v == "OK" for _s, v in res) else res))
        pb = [draft(r, n, "b") for r, n in L8_B]
        w("\n6. COMPOSITION ON BOARD B (no power draft targets gen_sch_b.py)\n")
        for tag, seq in (("forward", pb), ("reverse", pb[::-1])):
            _p, res = compose(GEN_B, seq, d, "b_" + tag)
            w("  %s: %s\n" % (tag, "; ".join("%s %s" % (os.path.basename(s)[13:-3], v) for s, v in res)))
        for s in pb:
            _p, res = compose(GEN_B, [s], d, "b_alone_" + os.path.basename(s)[:-3])
            w("  alone %-30s %s\n" % (os.path.relpath(s, RECS), res[0][1]))
        l6b = [os.path.join(ROOT, x) for x in L6_B]
        _p1, r1 = compose(GEN_B, pb + l6b, d, "b_l6_after"); _p2, r2 = compose(GEN_B, l6b + pb, d, "b_l6_before")
        w("  with Layer 6's board B drafts (l6r2: xal_land, lcsc, intent) after this record's and before them: %s; %s; the same generator either way: %s\n"
          % ("OK" if all(x == "OK" for _s, x in r1) else r1, "OK" if all(x == "OK" for _s, x in r2) else r2,
             "YES" if open(_p1, "rb").read() == open(_p2, "rb").read() else "NO"))

        compose_e_print(w, d)

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
        pE, addE = designators_e(d)
        w("  board E, what this record's pack return adds after the change list's round: %s (the round's own designators are held by test_l4e9)\n"
          % (", ".join(sorted(addE["l8r2/apply_gen_sch_e_packrtn.py"])) or "none"))
        w("  literal designators drawn twice in the composed board E generator: %s\n" % (duplicates(open(pE, encoding="utf-8").read()) or "none"))

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
    item5_print(w)
    item6_print(w)
    w("\nEND\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
