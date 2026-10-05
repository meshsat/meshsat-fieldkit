#!/usr/bin/env python3
"""efuse_check.py: every eFuse and current-limit setting in the schematic generators checked against its exact part's sheet
(record efuse, task T12, MESHSAT-1357, 5 October 2026; driven by finding SDR3-F04 on board B's U23).

What it reads, and from where (nothing is typed twice):
  - the generators' OWN part tables: each generator in v2/ecad/tools (and each one composed with the board's pending drafts in
    L4-E9's change-list order) is run through record l8p's gen_netlist.py (the stand-in layout step records kisch's part
    table: every part's reference, value, LCSC field and pin-to-net map, and intent.write's rails). The current-limiting
    parts are found by their value; their setting components by the pins they hang on (the ILM pin's resistor to ground, the
    resistor between a hot-swap controller's VIN and SENSE pins, and so on); the setting's value, tolerance and label are read
    from that component's own value text;
  - the makers' printed figures: each figure is written once, as the sentence or table row the maker prints (QUOTES), and the
    numbers are parsed from that quote; each quote is then searched for in the sheet's own text (pdftotext of the held PDF,
    NFKC-normalised, white space collapsed). A sheet that is absent on this host (the held-back folders are not in git) is
    reported SHEET ABSENT with its fetch script, and the figures stay the quotes' own;
  - the loads: record l9pwr's committed output (section 5, every state, LOW / PLAN / HIGH watts at the pins) and the
    generators' own rail declarations; the cases by id (C-DEV rev 1 and the others, _runs/cases/CASES-2026-10-04.md);
  - the downstream ratings: the connector makers' sheets in v2/vendor/connectors/, quoted the same way.

What it judges, per instance: (a) the setting inside the printed range; (b) the band's minimum at or above the load's
requirement in every state the rail serves, and its start-up; (c) the band's maximum at or below what the downstream
connector, cable and the load allow (and the switch's own continuous rating, reported beside); (d) the label in the generator
against the computed band. A failure of (a), (b) or (c) is a design defect (EF-Fnn); of (d) alone a labelling finding (EF-Lnn).

Nothing is built, bought or measured; every figure is desk arithmetic on printed data, labelled PRINTED (a guaranteed limit
the maker prints), TYPICAL, INFERRED or ASSUMPTION. Run from anywhere; the output goes through _bin/regen_out.py.
Exit 0 when the script ran to its end (the verdicts are in the output); 2 when an input is missing or a quote is not in its
sheet (a figure that is not the maker's must not be printed as one)."""
import ast
import hashlib
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
RECS = os.path.join(ROOT, "v2", "docs", "records")
GEN = {b: "v2/ecad/tools/gen_sch_%s.py" % b for b in "abcdep"}
GEN_NETLIST = "v2/docs/records/l8p/gen_netlist.py"
L9PWR_OUT = "v2/docs/records/l9pwr/l9pwr_budget.out"
L6R2_CAT = "v2/docs/records/l6r2/inputs/jlc-parts-2026-10-03.json"
MY_DRAFTS = {"b": ["v2/docs/records/efuse/apply_gen_sch_b_u23ilm.py", "v2/docs/records/efuse/apply_gen_sch_b_u24ilm.py"]}

# ------------------------------------------------------------------------------------------------------------ the sheets
# key: (path in the tree, document and revision, held back (not in git), how to get it). TI's current download of every TI
# sheet below was compared byte for byte with the held copy on 5 October 2026 (plain GET of www.ti.com/lit/ds/symlink/<part>.pdf):
# all eight identical, so each held copy IS the maker's current revision on that date (the README records the readings).
SHEETS = {
    "tps2596": ("v2/vendor/power/tps2596.pdf", "TI SLVSET8A (TPS2596xx, May 2019, revised August 2019)", False, ""),
    "tps2065c": ("v2/vendor/ti/ti-tps2065c-slvsau6i.pdf", "TI SLVSAU6I (TPS20xxC, June 2011, revised May 2026)", False, ""),
    "tps22810": ("v2/vendor/ti/ti-tps22810-load-switch.pdf", "TI SLVSDH0C (TPS22810, December 2016, revised January 2018)", False, ""),
    "lm5069": ("v2/vendor/ti/ti-lm5069.pdf", "TI SNVS452G (LM5069, September 2006, revised January 2020)", False, ""),
    "tps23861": ("v2/vendor/ti/tps23861-datasheet.pdf", "TI SLUSBX9I (TPS23861, March 2014, revised July 2019)", False, ""),
    "tps25740": ("v2/vendor/ti/ti-tps25740.pdf", "TI SLVSDG8B (TPS25740, TPS25740A, April 2016, revised June 2017)", False, ""),
    "tps1663": ("v2/vendor/ti/held/ti-tps1663-slvset9g.pdf", "TI SLVSET9G (TPS1663x, September 2018, revised April 2026)", True,
                "v2/docs/records/l4e11/fetch_held_back.py"),
    "tps4811": ("v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf", "TI SLUSEE5E (TPS4811-Q1, January 2022, revised April 2026)", True,
                "v2/docs/records/l4e11/fetch_held_back.py"),
    "usb3a": ("v2/vendor/connectors/wurth-wr-com-usb3-a-692122030100.pdf", "Wurth WR-COM 692122030100 (USB 3.0 type A receptacle)", False, ""),
    "idc16": ("v2/vendor/connectors/wurth-wr-bhd-idc-socket-61201623021.pdf", "Wurth WR-BHD 61201623021 (IDC socket, 16 pins)", False, ""),
    "ribbon16": ("v2/vendor/connectors/wurth-wr-cab-ribbon-63911615521cab.pdf", "Wurth WR-CAB 63911615521CAB (flat cable, 16 ways)", False, ""),
    "jst_ph": ("v2/vendor/connectors/jst-ph-catalogue.pdf", "JST PH connector catalogue", False, ""),
    "jst_vh": ("v2/vendor/connectors/jst-vh-catalogue.pdf", "JST VH connector catalogue", False, ""),
    "jst_sh": ("v2/vendor/connectors/jst-sh-catalogue.pdf", "JST SH connector catalogue", False, ""),
    "rb9704": ("v2/vendor/rockblock/groundcontrol-docs-rockblock-9704-hardware-20260927.txt",
               "Ground Control, RockBLOCK 9704 hardware page (text as saved 27 September 2026)", False, ""),
    "lime_page": ("v2/vendor/limesdr/myriadrf-limesdr-mini-2-0-page-20260925.html",
                  "LimeSDR Mini v2 documentation v2.4, Introduction (page as saved 25 September 2026)", False, ""),
    "lime_setup": ("v2/vendor/limesdr/myriadrf-limesdr-mini-2-0-user-setup-20260926.html",
                   "LimeSDR Mini v2 documentation v2.4, Hardware Setup (page as saved 26 September 2026)", False, ""),
}

# id: (sheet, where, the maker's printed text as it reads in the sheet's own text layer). Numbers are parsed from these.
QUOTES = {
    # TPS2596xx (the TPS259631 is its adjustable-OVLO, auto-retry variant; the device comparison table, p.3)
    "T96_VARIANT": ("tps2596", "p.3, 5 Device Comparison Table", "TPS259631 Adjustable OVLO Auto-retry"),
    "T96_RANGE": ("tps2596", "p.1, 1 Features", "Current range: 0.125-A to 2-A"),
    "T96_ACC": ("tps2596", "p.1, 1 Features", "±10.4 % (maximum) across current range"),
    "T96_RILM": ("tps2596", "p.5, 7.3 Recommended Operating Conditions", "RILM ILM Pin Resistance ILM 453 7869 Ω"),
    "T96_IMAX": ("tps2596", "p.5, 7.3 Recommended Operating Conditions", "IMAX Continuous Switch Current IN to OUT 2 A"),
    "T96_VIN": ("tps2596", "p.5, 7.3 Recommended Operating Conditions", "VIN Input Voltage Range IN 2.7 19"),
    "T96_ROW_7870": ("tps2596", "p.6, 7.5 ILIM (TA at most 80 C)", "RILM = 7.87 KΩ, VDS = 0.5 0.113 0.125 0.139 A V, –40°C ≤ TA ≤ 80°C"),
    "T96_ROW_3830": ("tps2596", "p.6, 7.5 ILIM", "RILM = 3.83 KΩ, VDS = 0.5 V 0.224 0.247 0.269 A"),
    "T96_ROW_909": ("tps2596", "p.6, 7.5 ILIM", "RILM = 909 Ω, VDS = 0.5 V 0.949 1.005 1.051 A"),
    "T96_ROW_453": ("tps2596", "p.6, 7.5 ILIM", "RILM = 453 Ω, VDS = 0.5 V 1.83 2.004 2.147 A"),
    "T96_EQ": ("tps2596", "p.21, 8.3.3.2 Equation 5 (the minus sign is lost in the text layer; Equation 7's worked example, p.28, "
               "903 / (1 - 0.0112) = 913.2, fixes it)", "903 RILM : ILIM A 0.0112"),
    "T96_EQ_EX": ("tps2596", "p.28, 9.2.3.1 Equation 7", "903 903 RILM : 913.2"),
    "T96_PVT": ("tps2596", "p.11, Figure 21 (Current Limit Accuracy)", "Across Process, Voltage and Temperature Corners, VDS = 0.5 V"),
    "T96_RON": ("tps2596", "p.7, 7.5 RON", "VIN > 4 V, IOUT = 0.2 A, TJ = 131 mΩ -40 to 125"),
    "T96_IDVDT": ("tps2596", "p.7, 7.5 DVDT", "IDVDT dVdt Pin Charging Current 1.89 2.11 2.33 µA"),
    "T96_GDVDT": ("tps2596", "p.7, 7.5 DVDT", "GDVDT DVDT gain 20.31 20.93 21.5 V"),
    # TPS2065C (the 1 A rated member, fixed limit)
    "T65_IOS": ("tps2065c", "p.7, 6.7 (TJ -40 to 125 C, VIN 4.5 to 5.5 V), 1-A rated output, TPS20xxC", "TPS20xxC 1.2 1.55 1.9"),
    "T65_IOUT": ("tps2065c", "p.5, 6.3 Recommended Operating Conditions, IOUT", "TPS2061C, TPS2065C and TPS2065C-2 1"),
    "T65_VIN": ("tps2065c", "p.7, 6.7 conditions", "4.5 V ≤ VIN ≤ 5.5 V"),
    # TPS22810 (no current limit: thermal protection only)
    "T22_TITLE": ("tps22810", "p.1, title", "Load Switch With Thermal Protection"),
    "T22_IMAX": ("tps22810", "p.5, 7.3 Recommended Operating Conditions", "Maximum continuous switch current, TA = 65°C (DRV) 3"),
    # LM5069
    "L69_VCL": ("lm5069", "p.6, 7.5 Current limit", "VCL Threshold voltage VIN-SENSE voltage 48.5 55 61.5 mV"),
    "L69_VCB": ("lm5069", "p.6, 7.5 Circuit breaker", "VCB Threshold voltage VIN to SENSE 80 105 130 mV"),
    "L69_VIN": ("lm5069", "p.5, 7.3 Recommended Operating Conditions", "VIN Supply voltage 9 80 V"),
    # TPS23861
    "T61_RS": ("tps23861", "p.24, 8.1 Overview", "either a 255-mΩ (two 510 mΩ in parallel) or a 250-mΩ (four 1 Ω in parallel)"),
    "T61_ICUT110": ("tps23861", "p.9, 7.5 VCUT, ICUT port n[2:0] = 110", "156.27 164.5 172.72 mV"),
    "T61_AUTO": ("tps23861", "8.3 Auto mode, Class 4", "set to 0b110 corresponding to 645 mA"),
    "T61_VLIM2X": ("tps23861", "p.9, 7.5 VLIM2X, PoEPn = 1, VDRAINn = 1 V", "VDRAINn = 1 V 260 270.3 285 mV"),
    # TPS25740A
    "T40_TRIP3A": ("tps25740", "p.11, 7.5 VI(TRIP)", "HIPWR: 5 A not enabled 19.2 22.6 mV"),
    "T40_TRIP5A": ("tps25740", "p.11, 7.5 VI(TRIP)", "HIPWR = DVDD (5 A enabled) 29 34 mV"),
    "T40_REC": ("tps25740", "p.31, 8.3.8.2", "Following the recommended implementation of a 5-mΩ sense resistor"),
    # TPS1663x
    "T63_RANGE": ("tps1663", "p.1, 1 Features", "Adjustable current limit: 0.6A to 6A (±7%)"),
    "T63_EQ": ("tps1663", "p.20, Equation 6 (I(OL) = 18 / R(ILIM), R in kOhm)", "IOL = R 18"),
    "T63_ROW_30k": ("tps1663", "p.8, 7.5 I(OL)", "R(ILIM) = 30kΩ, V(IN) – V(OUT) = 1V 0.54 0.6 0.66 A"),
    "T63_ROW_9k": ("tps1663", "p.8, 7.5 I(OL)", "R(ILIM) = 9kΩ, V(IN) – V(OUT) = 1V 1.84 2 2.16 A"),
    "T63_ROW_4k02": ("tps1663", "p.8, 7.5 I(OL)", "R(ILIM) = 4.02kΩ, V(IN) – V(OUT) = 1V 4.185 4.5 4.815 A"),
    "T63_ROW_3k": ("tps1663", "p.8, 7.5 I(OL)", "R(ILIM) = 3kΩ, V(IN) – V(OUT) = 1V 5.58 6 6.42 A"),
    # TPS4811-Q1
    "T48_OCP": ("tps4811", "p.10, 7.5 V(SNS_WRN)", "RSET = 100 Ω, RIWRN = 39.7kΩ 29.2 30.6 31.5 mV"),
    "T48_EQ6": ("tps4811", "p.22, Equation 6", "11.9 × RSET"),
    # the connectors and the loads
    "C_USB3A": ("usb3a", "p.1, electrical properties", "Rated Current IR 1.8 A max."),
    "C_IDC16": ("idc16", "p.1, electrical properties", "Rated Current IR 1 A max."),
    "C_RIB16": ("ribbon16", "p.1, electrical properties", "Rated Current IR 1 A max."),
    "C_PH": ("jst_ph", "specifications", "Current rating: 2 A AC/DC (AWG #24)"),
    "C_VH": ("jst_vh", "specifications", "Current rating: 10 A AC/DC"),
    "C_SH": ("jst_sh", "specifications", "Current rating: 1.0 A AC/DC(AWG #28)"),
    "L_RB_DC": ("rb9704", "DC power input pin", "It requires a voltage between 4.0V and 5.3VDC, at a maximum of 500mA."),
    "L_LIME_W": ("lime_page", "Power Supply table", "Maximum Power 4.5 W USB 3.0 power limit"),
    "L_LIME_HOST": ("lime_setup", "Hardware Setup", "supply power (5V, 900 mA) via the USB type-A connector"),
}

NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)")


def nums(qid):
    """the numbers printed in a quote, in order"""
    return [float(x) for x in NUM.findall(unicodedata.normalize("NFKC", QUOTES[qid][2]))]


def norm(t):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", t))


_TEXT = {}


def sheet_text(key):
    """the sheet's own text layer, normalised; None when the file is absent; raises when pdftotext is missing"""
    if key in _TEXT:
        return _TEXT[key]
    p = os.path.join(ROOT, SHEETS[key][0])
    if not os.path.isfile(p):
        _TEXT[key] = None
        return None
    if p.endswith(".pdf"):
        r = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True)
        t = r.stdout.decode("utf-8", "replace")
    else:
        t = open(p, encoding="utf-8", errors="replace").read()
        if p.endswith(".html"):
            t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
            t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    _TEXT[key] = norm(t)
    return _TEXT[key]


def verify_quotes():
    """{qid: 'VERIFIED' | 'SHEET ABSENT' | 'NOT FOUND'}"""
    out = {}
    for qid, (key, _w, q) in sorted(QUOTES.items()):
        t = sheet_text(key)
        out[qid] = "SHEET ABSENT" if t is None else ("VERIFIED" if norm(q) in t else "NOT FOUND")
    return out


def sha(rel, n=16):
    p = os.path.join(ROOT, rel)
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:n] if os.path.isfile(p) else None


# ------------------------------------------------------------------------------------------------- printed figures, parsed
def figures():
    F = {}
    F["t96_rilm"] = tuple(nums("T96_RILM"))                      # (453, 7869) ohm
    F["t96_range"] = (nums("T96_RANGE")[0], nums("T96_RANGE")[1])  # (0.125, 2) A
    F["t96_acc"] = nums("T96_ACC")[0] / 100.0                    # 0.104 across the range
    F["t96_imax"] = nums("T96_IMAX")[0]                          # 2 A continuous
    F["t96_vin"] = tuple(nums("T96_VIN")[:2])                    # 2.7 to 19 V
    k, off = nums("T96_EQ")                                      # 903, 0.0112
    F["t96_eq"] = (k, off)
    rows = []
    for qid, r in (("T96_ROW_7870", 7870.0), ("T96_ROW_3830", 3830.0), ("T96_ROW_909", 909.0), ("T96_ROW_453", 453.0)):
        n = nums(qid)
        lo, ty, hi = n[-6:-3] if qid == "T96_ROW_7870" else n[-3:]
        rows.append((r, lo, ty, hi, qid))
    F["t96_rows"] = rows
    F["t96_ron"] = nums("T96_RON")[3] / 1000.0                   # 0.131 ohm, VIN > 4 V, TJ to 125 C
    F["t96_idvdt"] = tuple(x * 1e-6 for x in nums("T96_IDVDT")[:3])
    F["t96_gdvdt"] = tuple(nums("T96_GDVDT")[:3])
    F["t65_ios"] = tuple(nums("T65_IOS")[-3:])                   # 1.2 / 1.55 / 1.9 A
    F["t65_iout"] = nums("T65_IOUT")[-1]                         # 1 A
    F["t65_vin"] = (nums("T65_VIN")[0], nums("T65_VIN")[1])
    F["t22_imax"] = nums("T22_IMAX")[-1]                         # 3 A (DRV)
    F["l69_vcl"] = tuple(x / 1000.0 for x in nums("L69_VCL")[:3])
    F["l69_vcb"] = tuple(x / 1000.0 for x in nums("L69_VCB")[:3])
    F["l69_vin"] = tuple(nums("L69_VIN")[:2])
    F["t61_rs"] = (nums("T61_RS")[0] / 1000.0, nums("T61_RS")[3] / 1000.0)     # 0.255, 0.250 ohm
    F["t61_icut110"] = tuple(x / 1000.0 for x in nums("T61_ICUT110"))
    F["t61_vlim2x"] = tuple(x / 1000.0 for x in nums("T61_VLIM2X")[-3:])
    F["t40_trip3a"] = tuple(x / 1000.0 for x in nums("T40_TRIP3A")[-2:])
    F["t40_trip5a"] = tuple(x / 1000.0 for x in nums("T40_TRIP5A")[-2:])
    F["t63_range"] = (nums("T63_RANGE")[0], nums("T63_RANGE")[1])
    F["t63_acc"] = nums("T63_RANGE")[2] / 100.0
    F["t63_k"] = nums("T63_EQ")[0]                               # 18 (A x kOhm)
    rows = []
    for qid in ("T63_ROW_30k", "T63_ROW_9k", "T63_ROW_4k02", "T63_ROW_3k"):
        n = nums(qid)
        rows.append((n[0] * 1000.0, n[-3], n[-2], n[-1], qid))
    F["t63_rows"] = rows
    F["t48_ocp"] = tuple(x / 1000.0 for x in nums("T48_OCP")[-3:])
    F["t48_point"] = (nums("T48_OCP")[0], nums("T48_OCP")[1] * 1000.0)        # RSET 100, RIWRN 39.7k
    F["c_usb3a"] = nums("C_USB3A")[0]
    F["c_idc16"] = nums("C_IDC16")[0]
    F["c_rib16"] = nums("C_RIB16")[0]
    F["c_ph"] = nums("C_PH")[0]
    F["c_vh"] = nums("C_VH")[0]
    F["c_sh"] = nums("C_SH")[0]
    F["l_rb_dc"] = nums("L_RB_DC")[-1] / 1000.0                  # 0.5 A
    F["l_lime_w"] = nums("L_LIME_W")[0]                          # 4.5 W
    F["l_lime_host"] = nums("L_LIME_HOST")[-1] / 1000.0          # 0.9 A
    return F


# ---------------------------------------------------------------------------------------------- the pending drafts, in order
# L4-E9's change list (L4-POWER-ARCHITECTURE.md section 3 at main aa32332c), per board, the rows that name a generator draft,
# with the drafts record l8r2 composes beside it (l8r2_drafts.py's L8_A and L8_B). Drafts that take a netlist (d8dec31's) and
# Layer 6's tables (l6r2) change no current-limiting part and are not composed; the parser below confirms it on their text.
ORDER = {
    "a": ["l4e6/apply_gen_sch_a_r12.py", "l4e11/apply_gen_sch_a_guard.py", "l4e11/apply_gen_sch_a_charger.py",
          "l4e4/apply_gen_sch_a_r11.py", "l4e8/apply_gen_sch_a_bank.py", "l4e4/apply_gen_sch_a_r138.py",
          "l4e9/apply_gen_sch_a_u17.py", "l8gnd/apply_gen_sch_a_gnd002.py", "l8gnd/apply_gen_sch_a_hotr1.py",
          "l8r2/apply_gen_sch_a_d8v3.py", "l8r2/apply_gen_sch_a_vbus20ov.py", "l8r2/apply_gen_sch_a_packrtn.py",
          "l8r2/apply_gen_sch_a_slotlm.py", "l8r2/apply_gen_sch_a_fb01.py", "l8p/apply_gen_sch_a_ptc.py", "l4e11/apply_gen_sch_a_dd7.py"],
    "b": ["l8gnd/apply_gen_sch_b_gnd002.py", "l8r2/apply_gen_sch_b_fans12.py", "l8r2/apply_gen_sch_b_panel5v.py",
          "l8r2/apply_gen_sch_b_ph4.py", "l8r2/apply_gen_sch_b_rt500.py"],
    "e": ["l4e9/apply_gen_sch_e_q1.py", "l4e7/apply_gen_sch_e_u5_grade.py", "l4e7/apply_gen_sch_e_hold.py",
          "l4e7/apply_gen_sch_e_input_limit.py", "l4e7/apply_gen_sch_e_backstop.py", "l4e9/apply_gen_sch_e_f1.py",
          "l4e9/apply_gen_sch_e_hotswap.py", "l4e11/apply_gen_sch_e_entry.py", "l4e7/apply_gen_sch_e_solar_guard.py",
          "l4e11/apply_gen_sch_e_aux.py", "l8r2/apply_gen_sch_e_packrtn.py", "l8p/apply_gen_sch_e_enable.py"],
    "p": ["l8p/apply_gen_sch_p_breaker.py"],
    "c": [], "d": [],
}

# the part families this record judges, by the value text the generator writes
FAMILY = [("TPS259631", "tps2596"), ("TPS2065C", "tps2065c"), ("TPS22810", "tps22810"), ("LM5069", "lm5069"),
          ("TPS23861", "tps23861"), ("TPS25740A", "tps25740"), ("TPS1663", "tps1663"), ("TPS4811", "tps4811")]
FAMILY_RE = re.compile(r"\b(TPS259631\w*|TPS2065C\w*|TPS22810\w*|LM5069\w*(?:-[12])?|TPS23861\w*|TPS25740A\w*|TPS1663\d\w*|TPS4811\d\w*)")


def run_apply(script, target):
    r = subprocess.run([sys.executable, "-B", script, target, "--write"], capture_output=True)
    return r.returncode, (r.stderr.decode("utf-8", "replace").strip().splitlines() or [""])[-1]


def compose(board, d, extra=()):
    """the board's generator with its pending drafts applied in order on a scratch copy: (path, [(draft, OK|REFUSED ...)])"""
    p = os.path.join(d, "gen_sch_%s_%s.py" % (board, "x".join(os.path.basename(e)[:-3] for e in extra) or "drafted"))
    shutil.copy(os.path.join(ROOT, GEN[board]), p)
    res = []
    for rel in ORDER[board] + list(extra):
        s = os.path.join(RECS, rel) if not rel.startswith("v2/") else os.path.join(ROOT, rel)
        rc, msg = run_apply(s, p)
        res.append((rel, "OK" if rc == 0 else "REFUSED (%s)" % msg[:120]))
        if rc:
            break
    return p, res


_GN = None


def gen_netlist_mod():
    global _GN
    if _GN is None:
        sp = importlib.util.spec_from_file_location("efuse_gen_netlist", os.path.join(ROOT, GEN_NETLIST))
        _GN = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(_GN)
    return _GN


def table_of(gen_path, net_path):
    rc, log, table = gen_netlist_mod().run(gen_path, net_path)
    if rc or table is None:
        raise RuntimeError("gen_netlist refused %s: %s" % (os.path.basename(gen_path), log.strip().splitlines()[-1:]))
    return table


# ------------------------------------------------------------------------------------------------------- value text parsing
RVAL = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(mOhm|m|R|k|K|M)?(?![a-zA-Z])")


def ohms(value):
    """(ohms, tolerance fraction or None, tcr ppm/K or None) from a resistor's value text, or None"""
    v = unicodedata.normalize("NFKC", value)
    m = RVAL.match(v)
    if not m:
        return None
    x = float(m.group(1)); u = m.group(2) or "R"
    x *= {"mOhm": 1e-3, "m": 1e-3, "R": 1.0, "k": 1e3, "K": 1e3, "M": 1e6}[u]
    t = re.search(r"(\d+(?:\.\d+)?)\s*%", v)
    p = re.search(r"(\d+)\s*ppm", v)
    return x, (float(t.group(1)) / 100.0 if t else None), (float(p.group(1)) if p else None)


LABEL = re.compile(r"\((?:ILM|I\(OL\))[^)]*?(\d+(?:\.\d+)?)\s*A\)")


def label_amps(value):
    m = LABEL.search(value or "")
    return (float(m.group(1)), m.group(1)) if m else (None, None)


def catalogue():
    p = os.path.join(ROOT, L6R2_CAT)
    if not os.path.isfile(p):
        return {}
    d = json.load(open(p, encoding="utf-8"))
    out = {}
    for _k, s in sorted(d.get("searches", {}).items()):
        for row in s.get("rows", []):
            a = row.get("attributes", {})
            tc = re.search(r"(\d+)\s*ppm", a.get("Temperature Coefficient", ""))
            if row.get("code") and tc:
                out[row["code"]] = (float(tc.group(1)), "l6r2's catalogue reading of %s (%s)" % (row["code"], a.get("Temperature Coefficient", "")))
    return out


# ------------------------------------------------------------------------------------------------------------ the instances
def nets_of(table):
    by_net = {}
    for p in table["parts"]:
        for pin, net in p["nets"].items():
            by_net.setdefault(net, []).append((p["ref"], pin))
    return by_net


def parts_by_ref(table):
    return {p["ref"]: p for p in table["parts"]}


def resistors_between(table, a, b):
    out = []
    for p in table["parts"]:
        if p["sym"] == "R" or p["lib"] == "Device" and p["sym"] == "R":
            ns = set(p["nets"].values())
            if ns == {a, b}:
                out.append(p)
    return out


def resistors_on(table, net):
    return [p for p in table["parts"] if p["sym"] == "R" and net in p["nets"].values()]


def instances(table, board):
    """every current-limiting part of a part table with its setting components (read by pins)"""
    by = parts_by_ref(table); out = []
    for p in table["parts"]:
        m = FAMILY_RE.search(p["value"])
        if not m or p["sym"] == "R":
            continue
        fam = next(f for pre, f in FAMILY if m.group(1).startswith(pre))
        n = p["nets"]; inst = dict(board=board, ref=p["ref"], family=fam, mpn=m.group(1), value=p["value"], lcsc=p.get("lcsc", ""),
                                   setting=[], vin=None, vout=None)
        if fam == "tps2596":
            inst["vin"], inst["vout"] = n.get("4"), n.get("5")
            inst["setting"] = [r for r in resistors_between(table, n.get("7"), "GND")]
            inst["dvdt"] = [c for c in table["parts"] if c["sym"] == "C" and set(c["nets"].values()) == {n.get("2"), "GND"}]
        elif fam == "tps2065c":
            inst["vin"], inst["vout"] = n.get("5"), n.get("1")
        elif fam == "tps22810":
            inst["vin"], inst["vout"] = n.get("6"), n.get("1")
        elif fam == "lm5069":
            inst["vin"], inst["vout"] = n.get("2"), n.get("9")
            inst["setting"] = resistors_between(table, n.get("2"), n.get("1"))
        elif fam == "tps23861":
            sen = n.get("15")                                       # SEN1 (port 1, the one used)
            nodes = {sen} | {x for r in resistors_on(table, sen) for x in r["nets"].values()}
            inst["setting"] = [r for r in table["parts"] if r["sym"] == "R" and "GND" in r["nets"].values()
                               and (set(r["nets"].values()) - {"GND"}) & nodes and (ohms(r["value"]) or (9e9,))[0] < 1.0]
            inst["vin"], inst["vout"] = "+54V_POE", "POE_DRAIN"
        elif fam == "tps25740":
            inst["vin"], inst["vout"] = n.get("19"), n.get("21")
            inst["setting"] = resistors_between(table, n.get("19"), n.get("21"))
        elif fam == "tps1663":
            inst["vin"], inst["vout"] = n.get("1"), n.get("18")
            inst["setting"] = resistors_between(table, n.get("11"), "GND")
        elif fam == "tps4811":
            cs_m, cs_p, vs, iwrn = n.get("17"), n.get("18"), n.get("20"), n.get("8")
            rs = [r for r in resistors_on(table, cs_m) if (ohms(r["value"]) or (9e9,))[0] < 1.0]
            src = (set(rs[0]["nets"].values()) - {cs_m}).pop() if rs else None
            inst["vin"], inst["vout"] = src, cs_m
            inst["setting"] = rs
            inst["rset"] = resistors_between(table, src, cs_p)
            inst["riwrn"] = resistors_between(table, iwrn, n.get("6"))
        out.append(inst)
    return out


def rail_from(intent, ref):
    """the rail(s) the intent declares with this part as its source or switch"""
    out = []
    for name, r in sorted((intent or {}).get("rails", {}).items()):
        if r.get("source") == ref or r.get("switch") == ref:
            out.append((name, r))
    return out


# --------------------------------------------------------------------------------------------------------------- the bands
TJ_LO, TJ_HI, T_REF = -20.0, 85.0, 25.0     # ASSUMPTION A-T: the setting resistor between -20 C (D-02a's in-use floor) and +85 C
TCR_DEFAULT = 100.0                         # ASSUMPTION A-TCR: a 1 % chip resistor with no code read at +-100 ppm/K (the series the tree uses)
SENSE_TCR = {"C2903468": 50.0, "C2903482": 50.0}   # HoJLR2512 10 and 5 mOhm, +-50 ppm/K (record l4e4's reading of the series sheet)


def r_corners(r, tol, tcr):
    dt = max(TJ_HI - T_REF, T_REF - TJ_LO)
    k = tcr * 1e-6 * dt
    return r * (1 - tol) * (1 - k), r * (1 + tol) * (1 + k)


def t96_band(F, r, tol, tcr):
    """(basis, lo, nom, hi, note) for a TPS2596 ILM resistor; lo/hi None when the sheet prints nothing for it"""
    k, off = F["t96_eq"]; f = lambda x: k / x + off
    nom = f(r)
    rmin, rmax = F["t96_rilm"]
    if not (rmin <= r <= rmax) or not (F["t96_range"][0] <= nom <= F["t96_range"][1]):
        return ("NONE: outside the printed range", None, nom, None,
                "Equation 5 extrapolated to %.4f A; the sheet prints no limit, tolerance or behaviour there" % nom)
    r_lo, r_hi = r_corners(r, tol, tcr)
    for rr, lo, ty, hi, qid in F["t96_rows"]:
        if abs(rr - r) / rr < 0.005:
            return ("PRINTED ROW %s" % qid, lo * f(r_hi) / f(rr), nom, hi * f(r_lo) / f(rr),
                    "the row's min and max scaled by the resistor's corners (proportional scaling INFERRED)")
    acc = F["t96_acc"]
    rows = sorted(F["t96_rows"])
    below = [x for x in rows if x[0] < r]; above = [x for x in rows if x[0] > r]
    brk = max([max(1 - x[1] / f(x[0]), x[3] / f(x[0]) - 1) for x in (below[-1:] + above[:1])] or [0])
    return ("PRINTED RANGE-WIDE +-%.1f %% (Figure 21: across process, voltage and temperature)" % (acc * 100),
            f(r_hi) * (1 - acc), nom, f(r_lo) * (1 + acc),
            "the bracketing rows' worst deviation is %.1f %% (INFERRED band %.4f to %.4f A)" % (brk * 100, f(r_hi) * (1 - brk), f(r_lo) * (1 + brk)))


def t63_band(F, r, tol, tcr):
    kk = F["t63_k"]; f = lambda x: kk / (x / 1000.0)
    nom = f(r)
    rows = sorted(F["t63_rows"])
    if not (rows[0][0] <= r <= rows[-1][0]):
        return ("NONE: outside the printed range", None, nom, None, "")
    r_lo, r_hi = r_corners(r, tol, tcr)
    for rr, lo, ty, hi, qid in rows:
        if abs(rr - r) / rr < 0.005:
            return ("PRINTED ROW %s" % qid, lo * f(r_hi) / f(rr), nom, hi * f(r_lo) / f(rr), "")
    below = [x for x in rows if x[0] < r]; above = [x for x in rows if x[0] > r]
    brk = max(max(1 - x[1] / f(x[0]), x[3] / f(x[0]) - 1) for x in below[-1:] + above[:1])
    acc = max(brk, F["t63_acc"])
    return ("INFERRED +-%.1f %%: the bracketing rows' worst (the Features' +-%.0f %% is exceeded by the 30 kOhm row)" % (acc * 100, F["t63_acc"] * 100),
            f(r_hi) * (1 - acc), nom, f(r_lo) * (1 + acc), "")


def sense_band(v_lo, v_hi, rs, tol, tcr):
    r_lo, r_hi = r_corners(rs, tol, tcr)
    return v_lo / r_hi, v_hi / r_lo


def parallel(rs):
    return 1.0 / sum(1.0 / x for x in rs)


# ------------------------------------------------------------------------------------------------------- loads and ratings
def l9_loads():
    """{load name: {state: (LOW, PLAN, HIGH) W}} from record l9pwr's section 5 (DRAFTED)"""
    p = os.path.join(ROOT, L9PWR_OUT)
    out = {}; state = None; inside = False
    for line in open(p, encoding="utf-8"):
        if line.startswith("5. PER STATE"):
            inside = True; continue
        if inside and re.match(r"^\d+[a-z]?\. ", line):
            break
        if not inside:
            continue
        m = re.match(r"^   == (.+?) \(pack side", line)
        if m:
            state = m.group(1); continue
        m = re.match(r"^     load (.+?)\s{2,}(\S+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+pack", line)
        if m and state:
            out.setdefault(m.group(1), {})[state] = (float(m.group(3)), float(m.group(4)), float(m.group(5)))
    return out


C_DEV_V = 4.9019     # C-DEV rev 1: the device rail's least load voltage (record l9pwr round 2, every load at constant power)
VBAT_MIN = 9.688     # L4-E9 IF-10/IF-11: VBAT's least under (B1)


def cp_current(watts, v, r_on):
    """the current a constant-power load draws at v behind a series r_on (the smaller root)"""
    if r_on <= 0:
        return watts / v
    disc = v * v - 4 * r_on * watts
    return (v - disc ** 0.5) / (2 * r_on) if disc > 0 else float("inf")


# the judgement's inputs per instance, typed once with their sources. demand: list of (label, amps or callable, tier);
# down: list of (conductor, rating in A, quote id); start: (draw at start A, load capacitance F or None, basis)
def meta(F, L9):
    lime = lambda: max(F["l_lime_host"], cp_current(F["l_lime_w"], C_DEV_V, F["t96_ron"]))
    W = lambda name: max(h for (_l, _p, h) in L9.get(name, {}).values()) if L9.get(name) else None
    M = {
        ("b", "U23"): dict(case="C-DEV rev 1", load="LimeSDR Mini 2.4 (J_LIME, USB 3.0 type A)",
                           demand=[("the maker: 'Maximum Power 4.5 W' at C-DEV's 4.9019 V behind U23's 0.131 Ohm, and the host's "
                                    "'5V, 900 mA' (PRINTED; constant power is the upper reading)", lime(), "PRINTED")],
                           down=[("J_LIME, Wurth 692122030100 VBUS contact", F["c_usb3a"], "C_USB3A")],
                           start=(0.15, 10e-6, "ASSUMPTION: a USB-compliant device draws at most 150 mA unconfigured and "
                                               "carries at most 10 uF on VBUS (USB 3.x; the standard is not held here)")),
        ("b", "U24"): dict(case="C-DEV rev 1", load="RockBLOCK 9704 (J_RB9704, IDC 2x8, pin 15 the one 5 V conductor)",
                           demand=[("the maker: DC input 'at a maximum of 500mA' (PRINTED)", F["l_rb_dc"], "PRINTED")],
                           down=[("J_RB9704's IDC socket contact, Wurth 61201623021", F["c_idc16"], "C_IDC16"),
                                 ("the 16-way flat cable conductor, Wurth 63911615521CAB", F["c_rib16"], "C_RIB16")],
                           start=(F["l_rb_dc"], None, "the module's own input capacitance is not printed: the allowance is "
                                                      "computed with the module drawing its full 500 mA during the ramp")),
        ("b", "U28"): dict(case="C-DEV rev 1", load="the camera (part TBD) on J_CAM, USB 2.0",
                           demand=[("l9pwr's camera row at HIGH, %.2f W at 4.9019 V (T: a placeholder)" % (W("camera (part TBD)") or 0),
                                    (W("camera (part TBD)") or 0) / C_DEV_V, "T")],
                           down=[("J_CAM, JST PH", F["c_ph"], "C_PH")], start=None),
        ("a", "U21"): dict(case="VBAT 9.688 to 17.375 V (L4-E9 IF-10)", load="Xenarc 709GNK monitor (J_MON, JST VH)",
                           demand=[("l9pwr's Xenarc row at HIGH, %.2f W at VBAT's 9.688 V behind U21" % (W("Xenarc 709GNK") or 0),
                                    cp_current(W("Xenarc 709GNK") or 0, VBAT_MIN, F["t96_ron"]), "S")],
                           down=[("J_MON, JST VH", F["c_vh"], "C_VH")], start=None),
        ("a", "U22"): dict(case="VBAT; the cold overlay", load="the heater mat's 12.0 V buck U33",
                           demand=[("the generator's VHEAT_IN note: 0.65 A at the 12.9 V edge of regulation (D)", 0.65, "D")],
                           down=[], start=None),
        ("a", "U23"): dict(case="C-DEV rev 1", load="board D's 5 V (J_MEZZ_PWR1, JST VH)",
                           demand=[("l9pwr's 'board D (SA868 and logic)' row at HIGH, %.2f W at 4.9019 V behind U23" % (W("board D (SA868 and logic)") or 0),
                                    cp_current(W("board D (SA868 and logic)") or 0, C_DEV_V, F["t96_ron"]), "S")],
                           down=[("J_MEZZ_PWR1, JST VH", F["c_vh"], "C_VH")], start=None),
        ("a", "U32"): dict(case="C-DEV rev 1", load="the Glenair 233-370 USB 2.0 host port (J_USBW, JST PH)",
                           demand=[("USB 2.0's 500 mA per port (the generator's note; the standard is not held here)", 0.5, "D")],
                           down=[("J_USBW, JST PH", F["c_ph"], "C_PH")], start=None),
        ("a", "U39"): dict(case="+3V3", load="the EMCON gates (four 74AUP1G08 and U40)",
                           demand=[("the generator's declaration (EQ-17)", None, "D")], down=[], start=None),
        ("a", "U44"): dict(case="+3V3", load="board D's 3.3 V on J_MEZZ1 pin 13 (record l8r2's draft)",
                           demand=[("the draft's declaration", None, "D")], down=[], start=None),
        ("b", "U901"): dict(case="C-DEV rev 1", load="board C's 5 V over the panel ribbon (record l8r2's draft)",
                            demand=[("l9pwr's 'panel board C' row at HIGH, %.2f W at 4.9019 V behind U901" % (W("panel board C") or 0),
                                     cp_current(W("panel board C") or 0, C_DEV_V, F["t96_ron"]), "D")],
                            down=[], start=None),
        ("a", "U42"): dict(case="VBAT", load="board E's auxiliary domain VSYS_E (L4-E11's draft)",
                           demand=[("the draft's VSYS_DOCK declaration", None, "D")], down=[], start=None),
    }
    for s in (1, 2, 3):
        M[("b", "U%d" % (702 + 30 * (s - 1)))] = dict(
            case="the cooler's 12 V lead", load="cooler fan of slot %d on J_FAN%d (JST SH; record l8r2's draft)" % (s, s),
            demand=[("l9pwr's cooler row at HIGH (2.75 W at the step-up's input, l8r2's envelope) x 0.80 / 11.51 V",
                     W("cooler fan slot %d" % s) * 0.80 / 11.51 if W("cooler fan slot %d" % s) else None, "R")],
            down=[("J_FAN%d, JST SH" % s, F["c_sh"], "C_SH")], start=None)
    return M


# --------------------------------------------------------------------------------------------------------------- the judge
def judge(inst, F, M, cat, intent):
    """fill inst with band, demand, ratings and the four verdicts"""
    fam = inst["family"]; key = (inst["board"], inst["ref"]); mt = M.get(key, {})
    rails = rail_from(intent, inst["ref"])
    inst["rails"] = rails
    inst["band"] = None; inst["basis"] = ""; inst["note"] = ""; inst["a"] = inst["b"] = inst["c"] = inst["d"] = "n/a"
    inst["imax"] = None
    setting = inst["setting"]
    inst["set_text"] = ", ".join("%s %s" % (r["ref"], r["value"]) for r in setting) or "none"
    if fam == "tps2596":
        if len(setting) != 1:
            inst["a"] = "FAIL: %d resistors on ILM" % len(setting); return
        rv = ohms(setting[0]["value"]); r, tol, tcr = rv[0], rv[1] if rv[1] is not None else 0.01, rv[2]
        if tcr is None:
            tcr, tsrc = (cat[setting[0]["lcsc"]] if setting[0].get("lcsc") in cat else (TCR_DEFAULT, "ASSUMPTION A-TCR"))
        else:
            tsrc = "the value text"
        inst["r"], inst["tol"], inst["tcr"], inst["tcr_src"] = r, tol, tcr, tsrc
        basis, lo, nom, hi, note = t96_band(F, r, tol, tcr)
        inst["basis"], inst["note"], inst["nom"] = basis, note, nom
        inst["band"] = (lo, hi) if lo is not None else None
        rmin, rmax = F["t96_rilm"]
        if inst["band"] is None:
            inst["a"] = "FAIL: %.0f Ohm outside %g to %g Ohm (ROC) and %.3f A outside %g to %g A" % (r, rmin, rmax, nom, F["t96_range"][0], F["t96_range"][1])
        else:
            r_lo, r_hi = r_corners(r, tol, tcr)
            inst["a"] = "PASS" + ("" if r_lo >= rmin and r_hi <= rmax else
                                  " (EDGE: the resistor's corners %.1f to %.1f Ohm reach outside %g to %g Ohm)" % (r_lo, r_hi, rmin, rmax))
        inst["imax"] = F["t96_imax"]
        lab, lab_txt = label_amps(setting[0]["value"])
        if lab is None:
            inst["d"] = "no label"
        else:
            dec = len(lab_txt.split(".")[1]) if "." in lab_txt else 0
            ok = abs(round(nom, dec) - lab) < 1e-9
            inst["d"] = ("PASS: '%s A' is the nominal %.4f A" % (lab_txt, nom) if ok and inst["band"] else
                         "FAIL: '%s A' against the nominal %.4f A" % (lab_txt, nom) if not ok else
                         "FAIL: '%s A' states a limit the sheet does not print (extrapolation)" % lab_txt)
        # start-up: the dVdt slew rate's highest (IDVDT max x GDVDT max over the 10 nF at -10 %, ASSUMPTION on the capacitor)
        cd = inst.get("dvdt") or []
        cdv = (ohms(cd[0]["value"].replace("n", "R")) or (None,))[0] if cd else None
        cdv = cdv * 1e-9 if cdv else None
        inst["sr_max"] = (F["t96_idvdt"][2] * F["t96_gdvdt"][2] / (cdv * 0.9)) if cdv else None
    elif fam == "tps2065c":
        inst["band"] = (F["t65_ios"][0], F["t65_ios"][2]); inst["nom"] = F["t65_ios"][1]
        inst["basis"] = "PRINTED (fixed limit, 6.7, TJ -40 to 125 C)"; inst["a"] = "PASS (fixed; VIN %g to %g V)" % F["t65_vin"]
        inst["imax"] = F["t65_iout"]; inst["d"] = "no label"
    elif fam == "tps22810":
        inst["basis"] = "NO CURRENT LIMIT on the part (the sheet: thermal protection only)"; inst["imax"] = F["t22_imax"]
        inst["a"] = "n/a (no setting)"
    elif fam in ("lm5069", "tps25740", "tps23861", "tps4811"):
        vals = [ohms(r["value"]) for r in setting]
        if not vals or None in vals:
            inst["a"] = "FAIL: no sense resistor read"; return
        rs = parallel([v[0] for v in vals]); tol = max(v[1] or 0.01 for v in vals)
        tcr = max((v[2] if v[2] is not None else SENSE_TCR.get(r.get("lcsc", ""), TCR_DEFAULT)) for v, r in zip(vals, setting))
        inst["r"], inst["tol"], inst["tcr"] = rs, tol, tcr
        if fam == "lm5069":
            lo, hi = sense_band(F["l69_vcl"][0], F["l69_vcl"][2], rs, tol, tcr); inst["nom"] = F["l69_vcl"][1] / rs
            inst["basis"] = "PRINTED VCL / RS (7.5); circuit breaker at VCB %.0f to %.0f mV: %.2f to %.2f A" % (
                F["l69_vcb"][0] * 1e3, F["l69_vcb"][2] * 1e3, *sense_band(F["l69_vcb"][0], F["l69_vcb"][2], rs, tol, tcr))
            inst["a"] = "PASS (no printed RS range; VIN %g to %g V)" % F["l69_vin"]
        elif fam == "tps25740":
            lo, hi = sense_band(F["t40_trip3a"][0], F["t40_trip3a"][1], rs, tol, tcr); inst["nom"] = None
            lo5, hi5 = sense_band(F["t40_trip5a"][0], F["t40_trip5a"][1], rs, tol, tcr)
            inst["basis"] = ("PRINTED VI(TRIP) 19.2 to 22.6 mV (the 3 A row, record l4e4's reading of Tables 4 and 5; the p.11 label's "
                             "29 to 34 mV row would give %.2f to %.2f A)" % (lo5, hi5))
            inst["a"] = "PASS (R138 is the sheet's 'may be tuned' sense; TI recommends 5 mOhm)"
        elif fam == "tps23861":
            lo, hi = sense_band(F["t61_icut110"][0], F["t61_icut110"][2], rs, tol, tcr); inst["nom"] = F["t61_icut110"][1] / rs
            lim = sense_band(F["t61_vlim2x"][0], F["t61_vlim2x"][2], rs, tol, tcr)
            inst["basis"] = "PRINTED ICUT 0b110 (Class 4, auto mode); ILIM 2x at VDRAIN 1 V %.3f to %.3f A" % lim
            inst["a"] = "PASS (%.3f Ohm: the sheet permits 0.255 or 0.250 Ohm)" % rs if any(abs(rs - x) < 1e-4 for x in F["t61_rs"]) else "FAIL: RS %.4f Ohm" % rs
        else:
            rset = [ohms(r["value"])[0] for r in inst.get("rset", [])]; riw = [ohms(r["value"])[0] for r in inst.get("riwrn", [])]
            at = rset and riw and abs(rset[0] - F["t48_point"][0]) < 0.5 and abs(riw[0] - F["t48_point"][1]) < 50
            lo, hi = sense_band(F["t48_ocp"][0], F["t48_ocp"][2], rs, tol, tcr); inst["nom"] = F["t48_ocp"][1] / rs
            inst["basis"] = "PRINTED V(SNS_WRN) at RSET %s, RIWRN %s (%s)" % (rset, riw, "the characterised point" if at else "NOT the printed point")
            inst["a"] = "PASS (the printed point)" if at else "FAIL: off the printed point"
        inst["band"] = (lo, hi); inst["d"] = "no label"
    elif fam == "tps1663":
        rv = ohms(setting[0]["value"]) if setting else None
        if not rv:
            inst["a"] = "FAIL: no ILIM resistor"; return
        r, tol, tcr = rv[0], rv[1] or 0.01, rv[2] if rv[2] is not None else TCR_DEFAULT
        inst["r"], inst["tol"], inst["tcr"] = r, tol, tcr
        basis, lo, nom, hi, _n = t63_band(F, r, tol, tcr)
        inst["basis"], inst["nom"] = basis, nom
        inst["band"] = (lo, hi) if lo is not None else None
        inst["a"] = "PASS (R(ILIM) %.1f kOhm in 3 to 30 kOhm)" % (r / 1e3) if inst["band"] else "FAIL"
        inst["d"] = "no label"
    # (b) the demand
    dem = [x for x in mt.get("demand", []) if x[1] is not None]
    if not dem:
        decl = [(n, r.get("amps_peak")) for n, r in rails]
        dem = [("the generator's declared peak of %s (D)" % n, a, "D") for n, a in decl if a is not None][:1]
    inst["demand"] = dem
    lo = inst["band"][0] if inst["band"] else None
    if fam == "tps22810":
        inst["b"] = "n/a (no limit); continuous %g A against %s" % (F["t22_imax"], ", ".join("%.3f" % d[1] for d in dem) or "-")
    elif inst["band"] is None:
        inst["b"] = "UNDEFINED: the sheet prints no limit for this setting"
    elif dem:
        need = max(d[1] for d in dem)
        inst["b"] = ("PASS: %.3f A >= %.3f A (margin %+.3f A)" % (lo, need, lo - need)) if lo >= need else \
                    ("FAIL: %.3f A < %.3f A" % (lo, need))
    else:
        inst["b"] = "NOT JUDGED: no demand read"
    st = mt.get("start")
    inst["start"] = None
    if st and inst.get("sr_max") and inst["band"]:
        c_board = sum((ohms(c["value"].split()[0].replace("u", "R")) or (0,))[0] * 1e-6 for c in [] )
        inst["start"] = st
    # (c) the downstream
    down = mt.get("down", [])
    inst["down"] = down
    hi = inst["band"][1] if inst["band"] else (inst.get("nom") if fam == "tps2596" else None)
    if fam == "tps22810":
        inst["c"] = "n/a (no limit on the part; the feeding rail's protection governs a fault)"
    elif not down:
        inst["c"] = "NOT RATED HERE: no conductor rating read for this branch"
    elif hi is None:
        inst["c"] = "NOT JUDGED"
    else:
        cap = min(x[1] for x in down)
        tag = "" if inst["band"] else " (on the EXTRAPOLATED nominal: the printed band does not exist)"
        inst["c"] = ("PASS: %.3f A <= %.3f A (%s)" % (hi, cap, min(down, key=lambda x: x[1])[0]) if hi <= cap else
                     "FAIL: %.3f A > %.3f A (%s)%s" % (hi, cap, min(down, key=lambda x: x[1])[0], tag))
