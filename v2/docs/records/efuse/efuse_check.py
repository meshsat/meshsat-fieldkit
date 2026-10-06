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
import math
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
MY_DRAFTS = {"b": ["v2/docs/records/efuse/apply_gen_sch_b_u23ilm.py", "v2/docs/records/efuse/apply_gen_sch_b_u24ilm.py"],
             "a": ["v2/docs/records/efuse/apply_gen_sch_a_u23ilm.py"]}
L4E12_OUT = "v2/docs/records/l4e12/l4e12_thermal.out"     # round 2 (V6-m4): the inside air the downstream ratings are read at
ASSEMBLY_DRAFT = "v2/docs/records/efuse/apply_assembly_rb_pads.py"
# W34 (Q-41 item 1, adopted in set 32): the makers' PDFs this script reads as text, each with its pdftotext options. Each text is a
# verbatim input taken once on the runner by v2/docs/records/_lib/retake_pdf_text.py beside its PDF (a held-back sheet's text is held
# back with it); _lib/pdftext.py returns it byte for byte and refuses when it is absent, so this script never runs pdftotext.
# Re-take after a sheet changes: python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/efuse
PDFTEXT = {
    "v2/vendor/connectors/jst-ph-catalogue.pdf": [["-layout"]],
    "v2/vendor/connectors/jst-sh-catalogue.pdf": [["-layout"]],
    "v2/vendor/connectors/jst-vh-catalogue.pdf": [["-layout"]],
    "v2/vendor/connectors/wurth-wr-bhd-idc-socket-61201623021.pdf": [["-layout"]],
    "v2/vendor/connectors/wurth-wr-bhd-idc-socket-61202623021.pdf": [["-layout"]],
    "v2/vendor/connectors/wurth-wr-cab-ribbon-63911615521cab.pdf": [["-layout"]],
    "v2/vendor/connectors/wurth-wr-cab-ribbon-63912615521cab.pdf": [["-layout"]],
    "v2/vendor/connectors/wurth-wr-com-usb3-a-692122030100.pdf": [["-layout"]],
    "v2/vendor/power/ti-tps2595-efuse.pdf": [["-layout"]],
    "v2/vendor/power/tps2596.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tps1663-slvset9g.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf": [["-layout"]],
    "v2/vendor/ti/ti-lm5069.pdf": [["-layout"]],
    "v2/vendor/ti/ti-tps2065c-slvsau6i.pdf": [["-layout"]],
    "v2/vendor/ti/ti-tps22810-load-switch.pdf": [["-layout"]],
    "v2/vendor/ti/ti-tps25740.pdf": [["-layout"]],
    "v2/vendor/ti/tps23861-datasheet.pdf": [["-layout"]],
}

_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(RECS, "_lib", "pdftext.py"))
PT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PT)

# ------------------------------------------------------------------------------------------------------------ the sheets
# key: (path in the tree, document and revision, held back (not in git), how to get it). TI's current download of every TI
# sheet below was compared byte for byte with the held copy on 5 October 2026 (plain GET of www.ti.com/lit/ds/symlink/<part>.pdf):
# all eight identical, so each held copy IS the maker's current revision on that date (the README records the readings).
SHEETS = {
    "tps2596": ("v2/vendor/power/tps2596.pdf", "TI SLVSET8A (TPS2596xx, May 2019, revised August 2019)", False, ""),
    "tps2595": ("v2/vendor/power/ti-tps2595-efuse.pdf", "TI TPS2595xx datasheet (Rev. C), the 4 A sibling family (not fitted)", False, ""),
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
    "idc26": ("v2/vendor/connectors/wurth-wr-bhd-idc-socket-61202623021.pdf", "Wurth WR-BHD 61202623021 (IDC socket, 26 pins)", False, ""),
    "ribbon26": ("v2/vendor/connectors/wurth-wr-cab-ribbon-63912615521cab.pdf", "Wurth WR-CAB 63912615521CAB (flat cable, 26 ways)", False, ""),
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
    "T96_ROW_7870": ("tps2596", "p.6, 7.5 ILIM (TA at most 80 C)", "RILM = 7.87 KΩ, VDS = 0.5 0.113 0.125 0.139 A V, -40°C ≤ TA ≤ 80°C"),
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
    # TPS2595xx, the sibling family a 3 A limit would have needed (not fitted; out 8's variant note)
    "T95_RANGE": ("tps2595", "p.1, 1 Features", "Current Range: 0.5 A to 4 A"),
    "T95_RILM": ("tps2595", "7.3 Recommended Operating Conditions", "RILM ILM pin resistance (Active Current Limiting Operation) ILM 487 5000 Ω"),
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
    "T63_ROW_30k": ("tps1663", "p.8, 7.5 I(OL)", "R(ILIM) = 30kΩ, V(IN) - V(OUT) = 1V 0.54 0.6 0.66 A"),
    "T63_ROW_9k": ("tps1663", "p.8, 7.5 I(OL)", "R(ILIM) = 9kΩ, V(IN) - V(OUT) = 1V 1.84 2 2.16 A"),
    "T63_ROW_4k02": ("tps1663", "p.8, 7.5 I(OL)", "R(ILIM) = 4.02kΩ, V(IN) - V(OUT) = 1V 4.185 4.5 4.815 A"),
    "T63_ROW_3k": ("tps1663", "p.8, 7.5 I(OL)", "R(ILIM) = 3kΩ, V(IN) - V(OUT) = 1V 5.58 6 6.42 A"),
    # TPS4811-Q1
    "T48_OCP": ("tps4811", "p.10, 7.5 V(SNS_WRN)", "RSET = 100 Ω, RIWRN = 39.7kΩ 29.2 30.6 31.5 mV"),
    "T48_EQ6": ("tps4811", "p.22, Equation 6", "11.9 × RSET"),
    "T48_IISCP": ("tps4811", "p.10, 7.5 I(ISCP)", "I(ISCP) SCP Input Bias current 13.7 15.6 17.6 µA"),
    "T48_EQ11": ("tps4811", "p.23, Equation 11 (RISCP = ISC x RSNS / 15.6 uA - 464; the text layer garbles it)", "15.6µSNS - 464"),
    "T48_IWRN": ("tps4811", "p.5, Table 5-1, pin IWRN", "Connect IWRN to GND if overcurrent protection feature is not"),
    # the connectors and the loads
    "C_USB3A": ("usb3a", "p.1, electrical properties", "Rated Current IR 1.8 A max."),
    "C_IDC16": ("idc16", "p.1, electrical properties", "Rated Current IR 1 A max."),
    "C_USB3A_R": ("usb3a", "p.1, electrical properties", "Contact Resistance R 30 mΩ max."),
    "C_RIB16": ("ribbon16", "p.1, electrical properties", "Rated Current IR 1 A max."),
    "C_IDC26": ("idc26", "p.1, electrical properties", "Rated Current IR 1 A max."),
    "C_RIB26": ("ribbon26", "p.1, electrical properties", "Rated Current IR 1 A max."),
    "C_PH": ("jst_ph", "specifications", "Current rating: 2 A AC/DC (AWG #24)"),
    "C_VH": ("jst_vh", "specifications", "Current rating: 10 A AC/DC"),
    "C_SH": ("jst_sh", "specifications", "Current rating: 1.0 A AC/DC(AWG #28)"),
    "L_RB_DC": ("rb9704", "DC power input pin", "It requires a voltage between 4.0V and 5.3VDC, at a maximum of 500mA."),
    "L_LIME_W": ("lime_page", "Power Supply table", "Maximum Power 4.5 W USB 3.0 power limit"),
    "L_LIME_HOST": ("lime_setup", "Hardware Setup", "supply power (5V, 900 mA) via the USB type-A connector"),
    # round 2 (V6-m4, V6-m5): each downstream part's range, which includes its own rise, and the RockBLOCK's charge-current pads
    "C_USB3A_T": ("usb3a", "p.1, general information", "Operating Temperature -20 °C up to +85 °C"),
    "C_IDC16_T": ("idc16", "p.1, general information", "Operating Temperature -40 up to +105 °C"),
    "C_RIB16_T": ("ribbon16", "p.1, general information", "Operating Temperature -25 °C up to +105 °C"),
    "C_RIB16_D": ("ribbon16", "cautions", "current rating may decrease due to the derating effect at higher temperatures"),
    "L_RB_CHG": ("rb9704", "Charge Current", "The default DC input charge current of the supercapacitors is limited to ~460mA"),
    "L_RB_CHG_UP": ("rb9704", "Charge Current", "the charge current limit can be increased to ~800mA"),
}

NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)")


def nums(qid):
    """the numbers printed in a quote, in order"""
    return [float(x) for x in NUM.findall(unicodedata.normalize("NFKC", QUOTES[qid][2]))]


DASHES = {0x2010: "-", 0x2011: "-", 0x2012: "-", 0x2013: "-", 0x2014: "-", 0x2212: "-"}


def norm(t):
    """NFKC, the makers' dashes and minus signs as a hyphen, white space collapsed"""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", t).translate(DASHES))


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
        t = PT.pdf_text(ROOT, SHEETS[key][0], ["-layout"], PDFTEXT, "v2/docs/records/efuse")
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
        lo, ty, hi = n[2:5]          # [R, 0.5 (VDS), min, typ, max, ...]
        rows.append((r, lo, ty, hi, qid))
    F["t96_rows"] = rows
    F["t96_ron"] = nums("T96_RON")[2] / 1000.0                   # 0.131 ohm, VIN > 4 V, TJ to 125 C ([4, 0.2, 131, 40, 125])
    F["t96_idvdt"] = tuple(x * 1e-6 for x in nums("T96_IDVDT")[:3])
    F["t96_gdvdt"] = tuple(nums("T96_GDVDT")[:3])
    F["t65_ios"] = tuple(nums("T65_IOS")[-3:])                   # 1.2 / 1.55 / 1.9 A
    F["t65_iout"] = nums("T65_IOUT")[-1]                         # 1 A
    F["t65_vin"] = (nums("T65_VIN")[0], nums("T65_VIN")[1])
    F["t22_imax"] = nums("T22_IMAX")[-1]                         # 3 A (DRV)
    F["l69_vcl"] = tuple(x / 1000.0 for x in nums("L69_VCL")[:3])
    F["l69_vcb"] = tuple(x / 1000.0 for x in nums("L69_VCB")[:3])
    F["l69_vin"] = tuple(nums("L69_VIN")[:2])
    F["t61_rs"] = (nums("T61_RS")[0] / 1000.0, nums("T61_RS")[2] / 1000.0)     # 0.255, 0.250 ohm
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
    F["t48_iiscp"] = tuple(x * 1e-6 for x in nums("T48_IISCP")[-3:])
    F["t48_off"] = nums("T48_EQ11")[-1]                                         # 464 ohm
    F["c_usb3a"] = nums("C_USB3A")[0]
    F["c_usb3a_r"] = nums("C_USB3A_R")[0] / 1000.0             # 0.030 ohm a contact
    F["c_idc16"] = nums("C_IDC16")[0]
    F["c_rib16"] = nums("C_RIB16")[0]
    F["c_idc26"] = nums("C_IDC26")[0]
    F["c_rib26"] = nums("C_RIB26")[0]
    F["c_ph"] = nums("C_PH")[0]
    F["c_vh"] = nums("C_VH")[0]
    F["c_sh"] = nums("C_SH")[0]
    F["l_rb_dc"] = nums("L_RB_DC")[-1] / 1000.0                  # 0.5 A
    F["l_lime_w"] = nums("L_LIME_W")[0]                          # 4.5 W
    F["l_lime_host"] = nums("L_LIME_HOST")[-1] / 1000.0          # 0.9 A
    F["t_usb3a"] = nums("C_USB3A_T")[-1]                          # 85 C, the range's top, its own rise included
    F["t_idc16"] = nums("C_IDC16_T")[-1]                          # 105 C
    F["t_rib16"] = nums("C_RIB16_T")[-1]                          # 105 C
    F["l_rb_chg"] = nums("L_RB_CHG")[-1] / 1000.0                 # about 0.46 A
    F["l_rb_chg_up"] = nums("L_RB_CHG_UP")[-1] / 1000.0           # about 0.80 A with the pads bridged
    m = re.search(r"E5\s+ambient 60\.0 C; mixed air ([\d.]+) C; in the exhaust ([\d.]+) C", open(os.path.join(ROOT, L4E12_OUT), encoding="utf-8").read())
    if not m:
        raise SystemExit("efuse_check: L4-E12's inside air at E5 no longer reads in %s" % L4E12_OUT)
    F["air"], F["air_exhaust"] = float(m.group(1)), float(m.group(2))
    return F


# ---------------------------------------------------------------------------------------------- the pending drafts, in order
# L4-E9's change list (L4-POWER-ARCHITECTURE.md section 3 at main aa32332c), per board, the rows that name a generator draft,
# with the drafts record l8r2 composes beside it (l8r2_drafts.py's L8_A and L8_B). Drafts that take a netlist (d8dec31's) and
# Layer 6's tables (l6r2) change no current-limiting part and are not composed; the parser below confirms it on their text.
# Round 2 (5 October 2026, V6-m3): the composition is the P0 candidate's full one, in the order record l9t5's l9t5_drafts.py and
# the independent check V6 composed it: board B gains record l8r2's rounds 7 and 8 (fandec, gndret, gndrtn), record l9t5's I-03 and
# T10 drafts (iocbuck, iocpre) and T10 round 5's canshdn; board A gains record l8p's thguard after L4-E11's dd7 (dd7 refuses after
# it), record l9t5's iocbuck and iocpre, and record l8r2's gndrtn. Board B's chain then regenerates whole (round 1 ran it without
# fans12, EF-O02).
ORDER = {
    "a": ["l4e6/apply_gen_sch_a_r12.py", "l4e11/apply_gen_sch_a_guard.py", "l4e11/apply_gen_sch_a_charger.py",
          "l4e4/apply_gen_sch_a_r11.py", "l4e8/apply_gen_sch_a_bank.py", "l4e4/apply_gen_sch_a_r138.py",
          "l4e9/apply_gen_sch_a_u17.py", "l8gnd/apply_gen_sch_a_gnd002.py", "l8gnd/apply_gen_sch_a_hotr1.py",
          "l8r2/apply_gen_sch_a_d8v3.py", "l8r2/apply_gen_sch_a_vbus20ov.py", "l8r2/apply_gen_sch_a_packrtn.py",
          "l8r2/apply_gen_sch_a_slotlm.py", "l8r2/apply_gen_sch_a_fb01.py", "l8p/apply_gen_sch_a_ptc.py", "l4e11/apply_gen_sch_a_dd7.py",
          "l8p/apply_gen_sch_a_thguard.py", "l9t5/apply_gen_sch_a_iocbuck.py", "l9t5/apply_gen_sch_a_iocpre.py", "l8r2/apply_gen_sch_a_gndrtn.py"],
    "b": ["l8gnd/apply_gen_sch_b_gnd002.py", "l8r2/apply_gen_sch_b_fans12.py", "l8r2/apply_gen_sch_b_fandec.py", "l8r2/apply_gen_sch_b_panel5v.py",
          "l8r2/apply_gen_sch_b_ph4.py", "l8r2/apply_gen_sch_b_rt500.py", "l8r2/apply_gen_sch_b_gndret.py", "l8r2/apply_gen_sch_b_gndrtn.py",
          "l9t5/apply_gen_sch_b_iocbuck.py", "l9t5/apply_gen_sch_b_iocpre.py", "l9t5/apply_gen_sch_b_canshdn.py"],
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


def try_table(gen_path, net_path):
    """(table or None, the generator's last line when it refused)"""
    rc, log, table = gen_netlist_mod().run(gen_path, net_path)
    if rc or table is None:
        return None, (log.strip().splitlines() or [""])[-1]
    return table, ""


def runnable(board, d, extra=()):
    """the board's composed generator run through gen_netlist; when the full chain's generator refuses, the chain without the
    one draft whose removal lets it run (the first such draft in the order): (table, composed path, results, dropped, why)"""
    p, res = compose(board, d, extra)
    tag = os.path.splitext(os.path.basename(p))[0]
    table, why = try_table(p, os.path.join(d, tag + ".net"))
    if table is not None or any(v != "OK" for _r, v in res):
        return table, p, res, None, why
    chain = ORDER[board]
    for drop in chain:
        keep = [x for x in chain if x != drop]
        saved = ORDER[board]
        ORDER[board] = keep
        try:
            p2, res2 = compose(board, d, extra)
        finally:
            ORDER[board] = saved
        if any(v != "OK" for _r, v in res2):
            continue
        t2, _w = try_table(p2, os.path.join(d, tag + "_without.net"))
        if t2 is not None:
            return t2, p2, res, drop, why
    return None, p, res, None, why


def text_instances(draft_rel, board):
    """the eFuse calls a draft writes, read from its string constants (ast) for a draft that cannot run in its generator on this
    tree. A call inside a loop the target generator already has (the draft's text is the loop's body) is evaluated once per pass:
    its free loop variable takes the literal values the draft's own comprehension or loop over that name gives (fans12's ADDS
    over s in (1, 2, 3)), and only the body's assignments are executed. [instance dicts as instances() makes them]"""
    import builtins
    import textwrap
    out = []
    src = open(os.path.join(RECS, draft_rel), encoding="utf-8").read()
    whole = ast.parse(src)
    domains = {}
    for n in ast.walk(whole):
        gens = n.generators if isinstance(n, (ast.GeneratorExp, ast.ListComp, ast.SetComp)) else []
        for g in gens:
            if isinstance(g.target, ast.Name):
                try:
                    domains.setdefault(g.target.id, ast.literal_eval(g.iter))
                except ValueError:
                    pass
        if isinstance(n, ast.For) and isinstance(n.target, ast.Name):
            try:
                domains.setdefault(n.target.id, ast.literal_eval(n.iter))
            except ValueError:
                pass
    for c in ast.walk(whole):
        if not (isinstance(c, ast.Constant) and isinstance(c.value, str) and "efuse(" in c.value):
            continue
        try:
            mod = ast.parse(textwrap.dedent(c.value))
        except SyntaxError:
            continue
        calls = [n for n in ast.walk(mod) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "efuse"]
        if not calls:
            continue
        assigns = [st for st in mod.body if isinstance(st, ast.Assign)]
        bound = {t.id for st in assigns for t in ast.walk(st) if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store)}
        used = {n.id for st in assigns + calls for n in ast.walk(st) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        free = sorted(x for x in used - bound if not hasattr(builtins, x) and x in domains)
        passes = [dict()] if not free else [{free[0]: v} for v in domains[free[0]]]
        for ns0 in passes:
            ns = dict(ns0)
            for st in assigns:
                try:
                    exec(compile(ast.Module(body=[st], type_ignores=[]), "<draft>", "exec"), ns)   # one namespace: the lambdas read it
                except Exception:
                    pass
            for call in calls:
                try:
                    a = [eval(compile(ast.Expression(body=x), "<draft>", "eval"), ns) for x in call.args[:7]]
                except Exception:
                    continue
                out.append(dict(board=board, ref=a[0], family="tps2596", mpn="TPS259631DDAR", lcsc="C2155778", vin=a[1], vout=a[2],
                                value="TPS259631DDAR eFuse %s -> %s (%s)" % (a[1], a[2], a[6]), dvdt=[], from_text=draft_rel,
                                setting=[dict(ref=a[5][1], value=a[6], nets={"1": a[0] + "_ILM", "2": "GND"}, lcsc="", fp="", sym="R")]))
    return out


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
            inst["ocp_off"] = iwrn == n.get("6") or (iwrn or "").startswith("GND")
            inst["riscp"] = [r for r in resistors_on(table, n.get("19")) if (ohms(r["value"]) or (0,))[0] >= 1.0]
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
    if not (rmin <= r <= rmax):
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
    lime = lambda: max(F["l_lime_host"], cp_current(F["l_lime_w"], C_DEV_V, F["t96_ron"] + 2 * F["c_usb3a_r"]))
    W = lambda name: max(h for (_l, _p, h) in L9.get(name, {}).values()) if L9.get(name) else None
    M = {
        ("b", "U23"): dict(case="C-DEV rev 1", load="LimeSDR Mini 2.4 (J_LIME, USB 3.0 type A)",
                           demand=[("the maker: 'Maximum Power 4.5 W' at C-DEV's 4.9019 V behind U23's 0.131 Ohm and J_LIME's two "
                                    "30 mOhm contacts (VBUS and GND), and the host's '5V, 900 mA' (PRINTED; constant power is the "
                                    "upper reading)", lime(), "PRINTED")],
                           down=[("J_LIME, Wurth 692122030100 VBUS contact", F["c_usb3a"], "C_USB3A")],
                           start=(0.15, 10e-6, "ASSUMPTION: a device inside the USB standard's limits draws at most 150 mA unconfigured and "
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
                           demand=[("the draft's declaration", None, "D")],
                           down=[("J_MEZZ1 pin 13, one IDC contact of the 2x8 harness (Wurth 61201623021)", F["c_idc16"], "C_IDC16"),
                                 ("one conductor of the 16-way flat cable (Wurth 63911615521CAB)", F["c_rib16"], "C_RIB16")], start=None),
        ("b", "U901"): dict(case="C-DEV rev 1", load="board C's 5 V over the panel ribbon (record l8r2's draft)",
                            demand=[("l9pwr's 'panel board C' row at HIGH, %.2f W at 4.9019 V behind U901" % (W("panel board C") or 0),
                                     cp_current(W("panel board C") or 0, C_DEV_V, F["t96_ron"]), "D")],
                            down=[("J_PANEL pins 1 and 2, two IDC contacts (Wurth 61202623021) at 1 A each, sharing ASSUMED even",
                                   2 * F["c_idc26"], "C_IDC26"),
                                  ("two conductors of the 26-way flat cable (Wurth 63912615521CAB) at 1 A each, sharing ASSUMED even",
                                   2 * F["c_rib26"], "C_RIB26")], start=None),
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




def meta_family(F):
    """the instances whose judgement inputs depend on the part drawn (board E's entry changes part between the trees)"""
    return {
        ("e", "U6", "lm5069"): dict(
            case="C-SHORE rev 1 (the drawn LM5069; L4-E9 IF-07)", load="VIN_RAW: the vehicle and shore entry into board A",
            demand=[("L4-E9 IF-07: L4-E5's drawn line at VIN_RAW 9 V, 4.629 A (CITED, record l4e9)", 4.629, "CITED")],
            down=[], start=None),
        ("e", "U6", "tps4811"): dict(
            case="C-SHORE rev 1 (L4-E11 19e, DD-3)", load="VIN_RAW: the vehicle and shore entry into board A",
            demand=[("L4-E9 IF-07 with the corrected knee: the in-service maximum 5.983 A from a 9.00 V plug (CITED, record l4e9)", 5.983, "CITED")],
            down=[("F1's 80 C column (L4-E11's entry draft's reading of the Littelfuse 997 sheet; CITED, not re-read)", 7.3, None),
                  ("L2 SRF1260-1R0Y (L4-E11's entry draft; CITED, not re-read)", 7.51, None)], start=None),
        ("p", "U101", "lm5069"): dict(
            case="C-PROT rev 1", load="the pack path through the breaker (record l8p's draft)",
            demand=[("C-PROT rev 1: 18 A for 60 s never interrupted (the owner's criterion, l9stk 15.1)", 18.0, "CASE")],
            down=[("C-PROT rev 1: every series part within its limits below and above the trip, judged by record l9stk 15.1 "
                   "(CONFIRMED AS CONDITIONAL); the band's top against C-PROT's 23.93 A", 23.93, None)], start=None),
        ("a", "U18", "tps25740"): dict(
            case="the outlet's PDO contracts (L4-E9 IF-12)", load="the USB-C PD outlet J_USBC_OUT",
            demand=[("every PDO 3.0 A (5, 9 and 15 V; the generator's _PD_A from Table 2 and Equation 2, record l4e4)", 3.0, "D")],
            down=[("the receptacle's 5 A (L4-E9 IF-12; CITED)", 5.0, None)], start=None),
        ("b", "U5", "tps23861"): dict(
            case="the PoE port (802.3at Class 4 at the PSE)", load="the wall RJ45's PoE port 1",
            demand=[("the generator's POE_SEN declared peak 0.60 A (802.3at Class 4 at the PSE; the standard is not held here)", 0.60, "D")],
            down=[], start=None),
    }


CAP = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(p|n|u|µ|m)")


def farads(value):
    m = CAP.match(unicodedata.normalize("NFKC", value or ""))
    return float(m.group(1)) * {"p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3}[m.group(2)] if m else None


def lcsc_map():
    t = ast.parse(open(os.path.join(TOOLS, "lcsc_fill.py"), encoding="utf-8").read())
    for n in t.body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", None) == "MAP" for x in n.targets):
            return ast.literal_eval(n.value)
    return {}


def code_of(part, MAP):
    if part.get("lcsc"):
        return part["lcsc"], "the generator"
    for (rx, fp), code in MAP.items():
        if re.match(rx, part["value"]) and fp in part["fp"]:
            return code, "lcsc_fill.py's MAP"
    return "", "none"


def judge(inst, F, M, MF, cat, intent, table, MAP):
    """fill inst with its band, demand, start-up, ratings and the four verdicts"""
    fam = inst["family"]; key = (inst["board"], inst["ref"])
    mt = MF.get(key + (fam,)) or M.get(key, {})
    rails = rail_from(intent, inst["ref"])
    inst.update(rails=rails, band=None, basis="", note="", a="n/a", b="n/a", c="n/a", d="n/a", imax=None, nom=None, demand=[],
                down=[], own="", verdict="DEFECT (a: no setting read)",
                start_v="n/a", case=mt.get("case", "the generator's declaration"), load=mt.get("load", ", ".join(n for n, _r in rails) or "-"))
    me = next((p for p in table["parts"] if p["ref"] == inst["ref"]), None)
    inst["code"], inst["code_src"] = (inst["lcsc"], "the generator" if me else "the draft's helper") if inst["lcsc"] or not me else code_of(me, MAP)
    setting = inst["setting"]
    inst["set_text"] = ", ".join("%s %s" % (r["ref"], r["value"]) for r in setting) or "none (no setting component)"
    if fam == "tps2596":
        if len(setting) != 1:
            inst["a"] = "FAIL: %d resistors from ILM to GND" % len(setting); return
        rv = ohms(setting[0]["value"]); r, tol, tcr = rv[0], (rv[1] if rv[1] is not None else 0.01), rv[2]
        code, _src = code_of(setting[0], MAP)
        if tcr is None:
            tcr, tsrc = cat[code] if code in cat else (TCR_DEFAULT, "ASSUMPTION A-TCR")
        else:
            tsrc = "the value text"
        inst.update(r=r, tol=tol, tcr=tcr, tcr_src=tsrc, set_code=code or "none")
        basis, lo, nom, hi, note = t96_band(F, r, tol, tcr)
        inst.update(basis=basis, note=note, nom=nom, band=(lo, hi) if lo is not None else None, imax=F["t96_imax"])
        rmin, rmax = F["t96_rilm"]
        if inst["band"] is None:
            inst["a"] = "FAIL: %.0f Ohm is outside %g to %g Ohm (7.3) and %.3f A outside %g to %g A (Features)" % (
                r, rmin, rmax, nom, F["t96_range"][0], F["t96_range"][1])
        else:
            r_lo, r_hi = r_corners(r, tol, tcr)
            # round 2 (V6-m6): EF-F01's rule applied at the resistor's corners: a setting whose tolerance and drift take it outside the
            # recommended 453 to 7869 Ohm is outside the range the sheet prints a band for, as 301 Ohm was (round 1 read it EDGE)
            inst["a"] = ("PASS" if r_lo >= rmin and r_hi <= rmax else
                         "FAIL: the resistor's corners %.1f to %.1f Ohm reach outside the recommended %g to %g Ohm (7.3), EF-F01's rule" % (r_lo, r_hi, rmin, rmax))
        lab, lab_txt = label_amps(setting[0]["value"])
        if lab is None:
            inst["d"] = "no label"
        else:
            dec = len(lab_txt.split(".")[1]) if "." in lab_txt else 0
            same = abs(round(nom, dec) - lab) < 1e-9
            inst["d"] = ("PASS: '%s A' is the nominal %.4f A rounded" % (lab_txt, nom) if same and inst["band"] else
                         "FAIL: '%s A' states a limit the sheet does not print (Equation 5 extrapolated)" % lab_txt if same else
                         "FAIL: '%s A' against the nominal %.4f A" % (lab_txt, nom))
        cd = [farads(c["value"]) for c in inst.get("dvdt") or []]
        if cd and cd[0]:
            # the output's fastest rise: IDVDT max x GDVDT max over CdVdt at -10 % (ASSUMPTION A-C: an X7R 10 nF at +-10 %)
            inst["sr_max"] = F["t96_idvdt"][2] * F["t96_gdvdt"][2] / (cd[0] * 0.9)
        inst["c_board"] = sum(farads(p["value"]) or 0 for p in table["parts"] if p["sym"] == "C" and inst["vout"] in p["nets"].values()
                              and "GND" in p["nets"].values())
    elif fam == "tps2065c":
        inst.update(band=(F["t65_ios"][0], F["t65_ios"][2]), nom=F["t65_ios"][1], imax=F["t65_iout"],
                    basis="PRINTED fixed limit IOS (6.7, TJ -40 to 125 C, VIN 4.5 to 5.5 V), the 1 A rated member",
                    a="PASS (fixed limit; +5V_DEV 4.9019 to 5.1744 V inside %g to %g V)" % F["t65_vin"], d="no label")
    elif fam == "tps22810":
        inst.update(basis="NO CURRENT LIMIT: the sheet's device is a load switch 'With Thermal Protection'; no current-limit row",
                    imax=F["t22_imax"], a="n/a (no setting)", d="no label")
    elif fam == "tps4811" and inst.get("ocp_off"):
        inst.update(basis="OVERCURRENT NOT USED: IWRN on the controller's GND (Table 5-1: 'Connect IWRN to GND if overcurrent protection "
                          "feature is not required'); the part is an over-voltage cut-off here", a="n/a (no current setting)", d="no label",
                    b="n/a (no limit)", c="n/a (no limit)", verdict="PASS (no current limit drawn)")
        return
    elif fam in ("lm5069", "tps25740", "tps23861", "tps4811"):
        vals = [ohms(r["value"]) for r in setting]
        if not vals or None in vals:
            inst["a"] = "FAIL: no sense resistor read"; return
        rs = parallel([v[0] for v in vals]); tol = max((v[1] if v[1] is not None else 0.01) for v in vals)
        tcrs = []
        for v, rp in zip(vals, setting):
            code, _s = code_of(rp, MAP)
            tcrs.append(v[2] if v[2] is not None else SENSE_TCR.get(code, TCR_DEFAULT))
        tcr = max(tcrs)
        inst.update(r=rs, tol=tol, tcr=tcr, d="no label")
        if fam == "lm5069":
            lo, hi = sense_band(F["l69_vcl"][0], F["l69_vcl"][2], rs, tol, tcr)
            cb = sense_band(F["l69_vcb"][0], F["l69_vcb"][2], rs, tol, tcr)
            inst.update(nom=F["l69_vcl"][1] / rs, basis="PRINTED VCL / RS (7.5); the circuit breaker at VCB: %.2f to %.2f A%s" % (cb + (
                            "; C-PROT rev 1's band 18.32 to 23.93 A takes the resistors at the band's own temperature (l9stk)" if inst["board"] == "p" else "",)),
                        a="PASS (the sheet prints no RS range; VIN %g to %g V)" % F["l69_vin"])
        elif fam == "tps25740":
            lo, hi = sense_band(F["t40_trip3a"][0], F["t40_trip3a"][1], rs, tol, tcr)
            lo5, hi5 = sense_band(F["t40_trip5a"][0], F["t40_trip5a"][1], rs, tol, tcr)
            inst.update(basis="PRINTED VI(TRIP) 19.2 to 22.6 mV, the 3 A row by record l4e4's reading of Tables 4 and 5 (the p.11 "
                              "label's 29 to 34 mV row would give %.3f to %.3f A: l4e4's bench (a) settles which)" % (lo5, hi5),
                        a="PASS (the sense 'may be tuned', 8.3.8.2; TI recommends 5 mOhm)")
        elif fam == "tps23861":
            lo, hi = sense_band(F["t61_icut110"][0], F["t61_icut110"][2], rs, tol, tcr)
            lim = sense_band(F["t61_vlim2x"][0], F["t61_vlim2x"][2], rs, tol, tcr)
            ok = any(abs(rs - x) < 1e-4 for x in F["t61_rs"])
            inst.update(nom=F["t61_icut110"][1] / rs,
                        basis="PRINTED ICUT at 0b110 (Class 4 in auto mode, 645 mA by the sheet's 255 mOhm); ILIM 2x at VDRAIN 1 V %.3f to %.3f A" % lim,
                        a=("PASS (%.3f Ohm: the sheet names 0.255 or 0.250 Ohm)" % rs) if ok else "FAIL: RS %.4f Ohm is neither" % rs)
        else:
            rset = [ohms(r["value"])[0] for r in inst.get("rset", [])]; riw = [ohms(r["value"])[0] for r in inst.get("riwrn", [])]
            at = bool(rset and riw and abs(rset[0] - F["t48_point"][0]) < 0.5 and abs(riw[0] - F["t48_point"][1]) < 50)
            lo, hi = sense_band(F["t48_ocp"][0], F["t48_ocp"][2], rs, tol, tcr)
            sc = ""
            if inst.get("riscp"):
                rsc = ohms(inst["riscp"][0]["value"])[0]
                sc = ("; the short-circuit trip by Equation 11 with I(ISCP) %.1f to %.1f uA over RISCP %s %g Ohm: %.2f to %.2f A (INFERRED: "
                      "RISCP is not a printed point and the comparator's own offset is not printed apart; not judged here)" % (
                          F["t48_iiscp"][0] * 1e6, F["t48_iiscp"][2] * 1e6, inst["riscp"][0]["ref"], rsc,
                          (rsc * (1 - tol) + F["t48_off"]) * F["t48_iiscp"][0] / (rs * (1 + tol)),
                          (rsc * (1 + tol) + F["t48_off"]) * F["t48_iiscp"][2] / (rs * (1 - tol))))
            inst.update(nom=F["t48_ocp"][1] / rs, basis="PRINTED V(SNS_WRN) 29.2 / 30.6 / 31.5 mV at RSET 100 Ohm, RIWRN 39.7 kOhm (7.5)" + sc,
                        a="PASS (RSET %s Ohm, RIWRN %s Ohm: the printed point)" % (rset[0], riw[0]) if at else
                        "FAIL: RSET %s, RIWRN %s are not the printed point" % (rset, riw))
        inst["band"] = (lo, hi)
    elif fam == "tps1663":
        rv = ohms(setting[0]["value"]) if setting else None
        if not rv:
            inst["a"] = "FAIL: no ILIM resistor"; return
        r, tol, tcr = rv[0], (rv[1] if rv[1] is not None else 0.01), (rv[2] if rv[2] is not None else TCR_DEFAULT)
        basis, lo, nom, hi, _n = t63_band(F, r, tol, tcr)
        inst.update(r=r, tol=tol, tcr=tcr, basis=basis, nom=nom, band=(lo, hi) if lo is not None else None, d="no label",
                    a="PASS (R(ILIM) %.2f kOhm inside the 3 to 30 kOhm rows)" % (r / 1e3) if lo is not None else "FAIL: outside the rows")
    # (b) the demand, in the states the rail serves
    dem = [x for x in mt.get("demand", []) if x[1] is not None]
    if not dem:
        dem = sorted([("the generator's declared peak of %s (D)" % n, r.get("amps_peak"), "D") for n, r in rails if r.get("amps_peak") is not None],
                     key=lambda x: -x[1])[:1]
    inst["demand"] = dem
    lo = inst["band"][0] if inst["band"] else None
    need = max(d[1] for d in dem) if dem else None
    if fam == "tps22810":
        inst["b"] = ("PASS (continuous): %.3f A within the switch's %g A; no limit to judge" % (need, F["t22_imax"]) if need is not None and need <= F["t22_imax"]
                     else "NOT JUDGED")
    elif inst["band"] is None:
        inst["b"] = "UNDEFINED: the sheet prints no limit for this setting"
    elif need is not None:
        inst["b"] = ("PASS: %.3f A >= %.3f A (margin %+.3f A)" % (lo, need, lo - need)) if lo >= need else ("FAIL: %.3f A < %.3f A" % (lo, need))
    else:
        inst["b"] = "NOT JUDGED: no demand read"
    # (b) start-up (eFuses with a dVdt capacitor): the allowance for the load's own capacitance at the band's minimum
    st = mt.get("start")
    if fam == "tps2596" and inst.get("sr_max") and inst["band"]:
        draw = st[0] if st else (need or 0.0)
        allow = (lo - draw) / inst["sr_max"] - inst["c_board"]
        known = st[1] if st else None
        inst["start_v"] = ("%s: at %.2f V/ms the band's minimum leaves %.1f uF for the load's own input capacitance beside the board's "
                           "%.1f uF, the load drawing %.3f A during the rise" % (
                               ("PASS" if known is not None and allow >= known else "CONDITION" if known is None else "FAIL"),
                               inst["sr_max"] / 1e3, allow * 1e6, inst["c_board"] * 1e6, draw)
                           + (" (assumed %.0f uF: %s)" % (known * 1e6, st[2]) if known is not None else
                              (" (%s)" % st[2] if st else " (no load capacitance printed; above it the start passes through the "
                                                          "current limit, the sheet's dVdt-limited start, Figures 48 and 49)")))
    # (c) the downstream, with the switch's own continuous rating beside
    down = mt.get("down", [])
    inst["down"] = down
    hi = inst["band"][1] if inst["band"] else (inst["nom"] if fam == "tps2596" else None)
    if fam == "tps22810":
        inst["c"] = "n/a: the part limits nothing; a fault is limited by the feeding rail's own protection"
    elif hi is None:
        inst["c"] = "NOT JUDGED"
    elif not down:
        inst["c"] = "NOT RATED HERE: no record rates this branch's conductor (top of band %.3f A)" % hi
    else:
        cap, what = min((x[1], x[0]) for x in down)
        tag = "" if inst["band"] else " (on Equation 5's EXTRAPOLATED nominal: no printed band exists)"
        inst["c"] = ("PASS: %.3f A <= %.3f A (%s)" % (hi, cap, what)) if hi <= cap else ("FAIL: %.3f A > %.3f A (%s)%s" % (hi, cap, what, tag))
    if fam == "tps2065c":
        inst["own"] = ("the 1 A rated member (continuous %g A); its printed limit sits above the rating by the part's design" % inst["imax"])
    elif inst["imax"] is not None and hi is not None:
        inst["own"] = ("the switch's continuous %g A: %s" % (inst["imax"], "within" if hi <= inst["imax"] else
                       "the band's top %.3f A is above it (EDGE: a load between them is carried until the part's thermal shutdown)" % hi))
    else:
        inst["own"] = ""
    # the verdict
    fails = [k for k in "abc" if str(inst[k]).startswith(("FAIL", "UNDEFINED"))]
    inst["verdict"] = "DEFECT (%s)" % ",".join(fails) if fails else ("LABEL" if str(inst["d"]).startswith("FAIL") else "PASS")


# the findings this record registers, by instance and tree: a computed DEFECT without an entry here is printed UNREGISTERED and the
# test fails; an entry whose instance no longer fails is printed RESOLVED IN THIS TREE (the record's text is then restated)
FINDINGS = {
    ("DRAWN", "b", "U23"): ("EF-F01", "DESIGN DEFECT", "OPEN", "SDR3-F04 confirmed: R36 301 R, '3.0 A', outside TPS2596's range; corrected by "
                            "apply_gen_sch_b_u23ilm.py (750 R), DRAFTED"),
    ("DRAWN", "b", "U24"): ("EF-F02", "DESIGN DEFECT", "OPEN", "R43 301 R, '3.0 A', the same setting on the RockBLOCK's eFuse; corrected by "
                            "apply_gen_sch_b_u24ilm.py (1.21 k), DRAFTED"),
    ("DRAFTED", "b", "U23"): ("EF-F01", "DESIGN DEFECT", "OPEN", "the pending drafts of board B leave U23 as drawn"),
    ("DRAFTED", "b", "U24"): ("EF-F02", "DESIGN DEFECT", "OPEN", "the pending drafts of board B leave U24 as drawn"),
    ("DRAWN", "a", "U18"): ("DR-03", "DESIGN DEFECT (known)", "OPEN", "record l4e4: R138 10 mOhm trips under the 3 A contracts; its "
                            "draft apply_gen_sch_a_r138.py (5 mOhm, L4-E9 R-05) corrects it, DRAFTED"),
    ("DRAWN", "a", "U23"): ("EF-F03", "DESIGN DEFECT", "OPEN", "V6-m6: R98 453 R, the recommended minimum itself, its corners at 445.8 Ohm "
                            "outside the range and the band's top over the 2 A rating (round 1's EF-O03, read EDGE); corrected by "
                            "apply_gen_sch_a_u23ilm.py (511 R), DRAFTED"),
    ("DRAFTED", "a", "U23"): ("EF-F03", "DESIGN DEFECT", "OPEN", "the pending drafts of board A leave U23 as drawn"),
}


# --------------------------------------------------------------------------------------------------------- the netlist check
def sexp(text):
    """a minimal s-expression reader for the export form E that gen_netlist writes"""
    tok = re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', text)
    stack = [[]]
    for t in tok:
        if t == "(":
            stack.append([])
        elif t == ")":
            x = stack.pop(); stack[-1].append(x)
        else:
            stack[-1].append(t[1:-1].replace('\\"', '"').replace("\\\\", "\\") if t.startswith('"') else t)
    return stack[0][0]


def read_net(text):
    e = sexp(text); comps, nets = {}, {}
    for sec in e[1:]:
        if sec[0] == "components":
            for c in sec[1:]:
                d = {x[0]: x[1] for x in c[1:] if isinstance(x, list) and len(x) == 2 and not isinstance(x[1], list)}
                comps[d["ref"]] = d.get("value", "")
        elif sec[0] == "nets":
            for n in sec[1:]:
                name = next(x[1] for x in n[1:] if x[0] == "name").lstrip("/")
                nets[name] = sorted((next(y[1] for y in x[1:] if y[0] == "ref"), next(y[1] for y in x[1:] if y[0] == "pin"))
                                    for x in n[1:] if x[0] == "node")
    return comps, nets


def check_ilm(text, F, eref, rref, need, cap):
    """the eFuse's ILM pin carries exactly one resistor, the expected one, to GND, and its band (read from the value in the
    netlist) is inside the sheet's range, at or above need and at or below cap: (ok, reason)"""
    comps, nets = read_net(text)
    pin7 = [n for n, nodes in nets.items() if (eref, "7") in nodes]
    if len(pin7) != 1:
        return False, "%s pin 7 is on %d nets" % (eref, len(pin7))
    others = [x for x in nets[pin7[0]] if x != (eref, "7")]
    if others != [(rref, "1")] and others != [(rref, "2")]:
        return False, "%s's ILM net carries %s, not %s alone" % (eref, others, rref)
    far = "2" if others[0][1] == "1" else "1"
    if (rref, far) not in nets.get("GND", []):
        return False, "%s's far pin is not on GND" % rref
    rv = ohms(comps.get(rref, ""))
    if not rv:
        return False, "%s's value %r is not a resistance" % (rref, comps.get(rref))
    basis, lo, nom, hi, _n = t96_band(F, rv[0], rv[1] if rv[1] is not None else 0.01, TCR_DEFAULT)
    if lo is None:
        return False, "%s %s: %s" % (rref, comps[rref], basis)
    if lo < need or hi > cap:
        return False, "%s %s: band %.4f to %.4f A against %.4f to %.4f A" % (rref, comps[rref], lo, hi, need, cap)
    return True, "%s %s on %s pin 7 to GND: band %.4f to %.4f A within %.4f to %.4f A" % (rref, comps[rref], eref, lo, hi, need, cap)


def mutate_value(text, ref, new_value):
    old = re.search(r'\(comp \(ref "%s"\) \(value "([^"]*)"\)' % re.escape(ref), text)
    return text.replace(old.group(0), '(comp (ref "%s") (value "%s")' % (ref, new_value), 1)


def mutate_far_pin(text, ref, net_to):
    """move the resistor's GND pin onto another net"""
    m = re.search(r'\(net \(code "\d+"\) \(name "GND"\)[^\n]*', text)
    line = m.group(0)
    for pin in ("2", "1"):
        node = ' (node (ref "%s") (pin "%s"))' % (ref, pin)
        if node in line:
            text = text.replace(line, line.replace(node, ""), 1)
            m2 = re.search(r'\(net \(code "\d+"\) \(name "/?%s"\)' % re.escape(net_to), text)
            return text.replace(m2.group(0), m2.group(0) + node, 1)
    return text


# ------------------------------------------------------------------------------------------------------------------- output
def fmt_band(inst):
    if inst["band"] is None:
        return "none printed" + (" (Equation 5: %.4f A, EXTRAPOLATED)" % inst["nom"] if inst.get("nom") else "")
    return "%.4f / %s / %.4f A" % (inst["band"][0], ("%.4f" % inst["nom"]) if inst.get("nom") else "-", inst["band"][1])


def main():
    P = print
    missing = [p for p in list(GEN.values()) + [GEN_NETLIST, L9PWR_OUT] if not os.path.isfile(os.path.join(ROOT, p))]
    if missing:
        sys.stderr.write("efuse_check: missing inputs %s\n" % missing); return 2
    F = figures(); L9 = l9_loads(); M = meta(F, L9); MF = meta_family(F); cat = catalogue(); MAP = lcsc_map()
    VQ = verify_quotes()
    P("EFUSE (MESHSAT-1357, TASK T12): EVERY EFUSE AND CURRENT-LIMIT SETTING IN THE GENERATORS AGAINST ITS EXACT PART'S SHEET.")
    P("Prototype design, desk arithmetic: nothing built, bought, powered or measured. DRAWN = main's generators; DRAFTED = each generator")
    P("with its board's pending drafts composed in L4-E9's change-list order (out 2); EFUSE = DRAFTED plus this record's two drafts.")
    P("")
    P("0. INPUTS (sha256/16)")
    ins = sorted(set(list(GEN.values()) + [GEN_NETLIST, L9PWR_OUT, L6R2_CAT, "v2/ecad/tools/lcsc_fill.py", "v2/docs/records/l6r2/apply_gen_sch_b_lcsc.py",
                      L4E12_OUT, ASSEMBLY_DRAFT, "v2/docs/ASSEMBLY.md"] + MY_DRAFTS["b"] + MY_DRAFTS["a"]
                     + ["v2/docs/records/" + x for b in "abep" for x in ORDER[b]] + [v[0] for v in SHEETS.values()]
                     + [t for t, _h, _held in PT.inputs(ROOT, PDFTEXT)]))
    for p in ins:
        h = sha(p)
        P("   %s %s" % (h, p) if h else "   ABSENT          %s (held back: %s)" % (p, next((v[3] for v in SHEETS.values() if v[0] == p),
                                                                                "its sheet's fetch, then " + PT.retake_command("v2/docs/records/efuse"))))
    P("")
    P("1. THE SHEETS AND THE PRINTED FIGURES: every quote searched for in its sheet's own text layer (NFKC, white space collapsed)")
    for k, (path, doc, held, fetch) in sorted(SHEETS.items()):
        P("   %-10s %s%s" % (k, doc, " [held back by its notice; fetch: %s]" % fetch if held else ""))
    for qid, (key, where, q) in sorted(QUOTES.items()):
        P("   %-13s %-12s %s: \"%s\" (%s)" % (qid, VQ[qid], key, q, where))
    bad = [q for q, v in VQ.items() if v == "NOT FOUND"]
    absent = [q for q, v in VQ.items() if v == "SHEET ABSENT"]
    P("   quotes: %d VERIFIED, %d SHEET ABSENT, %d NOT FOUND" % (len(VQ) - len(bad) - len(absent), len(absent), len(bad)))
    if bad:
        sys.stderr.write("efuse_check: quotes not in their sheets: %s\n" % bad); return 2
    P("   parsed: TPS2596 RILM %g to %g Ohm, %g to %g A, +-%.1f %% across the range, %g A continuous, VIN %g to %g V, Equation 5 "
      "ILIM = %g / RILM + %g; rows %s; RON %.3f Ohm (VIN > 4 V, TJ to 125 C); IDVDT %s A, GDVDT %s" % (
          F["t96_rilm"][0], F["t96_rilm"][1], F["t96_range"][0], F["t96_range"][1], F["t96_acc"] * 100, F["t96_imax"],
          F["t96_vin"][0], F["t96_vin"][1], F["t96_eq"][0], F["t96_eq"][1],
          "; ".join("%g Ohm %g / %g / %g A" % r[:4] for r in F["t96_rows"]), F["t96_ron"],
          "/".join("%.2e" % x for x in F["t96_idvdt"]), "/".join("%g" % x for x in F["t96_gdvdt"])))
    P("   parsed: TPS2065C IOS %g / %g / %g A, %g A continuous; TPS22810 %g A continuous, no limit; LM5069 VCL %s V, VCB %s V, VIN %g to %g V;" % (
        F["t65_ios"] + (F["t65_iout"], F["t22_imax"], F["l69_vcl"], F["l69_vcb"]) + F["l69_vin"]))
    P("           TPS23861 RS %s Ohm, ICUT(110) %s V, VLIM2X(1 V) %s V; TPS25740A VI(TRIP) %s / %s V; TPS1663 I(OL) = %g / R(kOhm), %g to %g A "
      "(+-%.0f %%), rows %s; TPS4811 V(SNS_WRN) %s V at %s" % (
          F["t61_rs"], F["t61_icut110"], F["t61_vlim2x"], F["t40_trip3a"], F["t40_trip5a"], F["t63_k"], F["t63_range"][0], F["t63_range"][1],
          F["t63_acc"] * 100, "; ".join("%g Ohm %g / %g / %g A" % r[:4] for r in F["t63_rows"]), F["t48_ocp"], F["t48_point"]))
    P("           ratings: USB 3.0 A receptacle %g A, IDC socket %g A, flat cable %g A, JST PH %g A, VH %g A, SH %g A; RockBLOCK DC input "
      "%g A; LimeSDR %g W, host %g A" % (F["c_usb3a"], F["c_idc16"], F["c_rib16"], F["c_ph"], F["c_vh"], F["c_sh"], F["l_rb_dc"],
                                           F["l_lime_w"], F["l_lime_host"]))
    P("")
    with tempfile.TemporaryDirectory(prefix="efuse_") as d:
        P("2. THE PENDING DRAFTS, composed per board in L4-E9's change-list order (section 3 at aa32332c) on scratch copies, then the")
        P("   generator run through gen_netlist (its own intent checks included)")
        trees = {}; nets = {}; extra_inst = {}; dropped = {}
        for b in "abcdep":
            base = os.path.join(ROOT, GEN[b])
            nets[("DRAWN", b)] = os.path.join(d, "%s_drawn.net" % b)
            trees[("DRAWN", b)] = table_of(base, nets[("DRAWN", b)])
            if not ORDER[b]:
                P("   board %s  no pending generator draft names a current-limiting part (section 2b's parse)" % b.upper())
                trees[("DRAFTED", b)] = trees[("DRAWN", b)]; nets[("DRAFTED", b)] = nets[("DRAWN", b)]
                continue
            table, p, res, drop, why = runnable(b, d)
            for rel, v in res:
                P("   board %s  %-44s %s" % (b.upper(), rel, v))
            if drop:
                P("   board %s  THE COMPOSED GENERATOR REFUSES: %s" % (b.upper(), why[:200]))
                P("   board %s  it runs without %s; that draft's eFuse calls are read from its text (2c) and judged on their values" % (b.upper(), drop))
                dropped[b] = (drop, why)
                extra_inst[b] = text_instances(drop, b)
            elif table is None:
                P("   board %s  THE COMPOSED GENERATOR REFUSES and no single omission lets it run: %s" % (b.upper(), why[:200]))
                table = trees[("DRAWN", b)]
            trees[("DRAFTED", b)] = table
            nets[("DRAFTED", b)] = os.path.join(d, os.path.splitext(os.path.basename(p))[0] + ("_without.net" if drop else ".net"))
        table, p_eb, res_eb, drop_eb, why_eb = runnable("b", d, extra=MY_DRAFTS["b"])
        P("   board B  then this record's drafts: %s%s" % ("; ".join("%s %s" % (os.path.basename(r), v) for r, v in res_eb[-2:]),
                                                         "; the generator run without %s, as above" % drop_eb if drop_eb else ""))
        trees[("EFUSE", "b")] = table
        net_eb = os.path.join(d, os.path.splitext(os.path.basename(p_eb))[0] + ("_without.net" if drop_eb else ".net"))
        table_a, p_ea, res_ea, drop_ea, _why_ea = runnable("a", d, extra=MY_DRAFTS["a"])
        P("   board A  then this record's draft: %s%s" % ("; ".join("%s %s" % (os.path.basename(r), v) for r, v in res_ea[-1:]),
                                                       "; the generator run without %s" % drop_ea if drop_ea else ""))
        trees[("EFUSE", "a")] = table_a
        net_ea = os.path.join(d, os.path.splitext(os.path.basename(p_ea))[0] + ("_without.net" if drop_ea else ".net"))
        P("")
        P("2c. EFUSE CALLS READ FROM THE TEXT OF A DRAFT THE GENERATOR CANNOT RUN WITH ON THIS TREE")
        for b, insts in sorted(extra_inst.items()):
            for i in insts:
                P("   board %s  %s: %s %s -> %s, ILM %s %s" % (b.upper(), i["from_text"], i["ref"], i["vin"], i["vout"], i["setting"][0]["ref"], i["setting"][0]["value"]))
        if not extra_inst:
            P("   none")
        P("")
        P("2b. EVERY apply_gen_sch_*.py UNDER v2/docs/records ON THIS TREE, parsed (ast over its string constants) for a current-limiting part")
        for rel in sorted(os.path.relpath(os.path.join(dp, f), RECS) for dp, _dn, fs in os.walk(RECS) for f in fs
                          if f.startswith("apply_gen_sch_") and f.endswith(".py") and os.path.relpath(dp, RECS) != "efuse"):
            hits = sorted(set(m.group(1) for c in ast.walk(ast.parse(open(os.path.join(RECS, rel), encoding="utf-8").read()))
                              if isinstance(c, ast.Constant) and isinstance(c.value, str) for m in FAMILY_RE.finditer(c.value)))
            if hits:
                P("   %-48s names %s%s" % (rel, ", ".join(hits), "" if any(rel == x for b in "abep" for x in ORDER[b]) else "  (not composed: see the README)"))
        P("")
        # the inventory and the judgement
        rows = []
        for (tree, b), table in sorted(trees.items(), key=lambda kv: ("DRAWN DRAFTED EFUSE".split().index(kv[0][0]), kv[0][1])):
            for inst in instances(table, b) + (extra_inst.get(b, []) if tree == "DRAFTED" else []):
                judge(inst, F, M, MF, cat, table.get("intent"), table, MAP)
                inst["tree"] = tree
                rows.append(inst)
        drawn = {(i["board"], i["ref"]): i for i in rows if i["tree"] == "DRAWN"}
        P("3. THE INVENTORY: every current-limiting part, DRAWN on main, and what the pending drafts add or change (DRAFTED), and EFUSE")
        for i in rows:
            if i["tree"] != "DRAWN":
                base = drawn.get((i["board"], i["ref"]))
                if base and base["value"] == i["value"] and base["set_text"] == i["set_text"] and i["tree"] == "DRAFTED":
                    continue
                if i["tree"] == "EFUSE" and i["ref"] not in ("U23", "U24"):
                    continue
            P("   %-7s %s %-5s %-14s %-9s code %-10s (%s) %s -> %s; setting %s; rail %s" % (
                i["tree"], i["board"].upper(), i["ref"], i["mpn"], i["family"], i["code"] or "none", i["code_src"], i["vin"], i["vout"],
                i["set_text"], ", ".join("%s (typ %s, peak %s A)" % (n, r.get("amps_typ"), r.get("amps_peak")) for n, r in i["rails"]) or "-"))
        P("")
        P("4. THE BANDS (min / nominal / max), the basis of each, and the resistor's corners (tolerance, TCR over %g to %g C, ASSUMPTION A-T)" % (TJ_LO, TJ_HI))
        shown = set()
        for i in rows:
            k = (i["board"], i["ref"], i["value"], i["set_text"])
            if k in shown:
                continue
            shown.add(k)
            P("   %-7s %s %-5s %-9s %-34s %s" % (i["tree"], i["board"].upper(), i["ref"], i["family"], fmt_band(i), i["basis"]))
            if i.get("r") is not None:
                P("%s setting %.6g Ohm, %.1f %%, %g ppm/K (%s)%s" % (" " * 21, i["r"], i["tol"] * 100, i["tcr"], i.get("tcr_src", "the value text or SENSE_TCR"),
                                                                 ("; " + i["note"]) if i.get("note") else ""))
        P("")
        P("5. THE LOADS (record l9pwr section 5 at HIGH, every state the rail serves; the cases by id) AND THE DOWNSTREAM RATINGS")
        shown = set()
        for i in rows:
            k = (i["board"], i["ref"], i["family"])
            if k in shown:
                continue
            shown.add(k)
            P("   %s %-5s %-9s case %s; load %s" % (i["board"].upper(), i["ref"], i["family"], i["case"], i["load"]))
            for lab, amps, tier in i["demand"]:
                P("        demand %.4f A  [%s] %s" % (amps, tier, lab))
            for what, amps, qid in i["down"]:
                P("        rating %.3f A  %s%s" % (amps, what, " (%s, %s)" % (qid, VQ.get(qid, "")) if qid else ""))
        names = ("LimeSDR Mini 2.4", "RockBLOCK 9704", "camera (part TBD)", "Xenarc 709GNK", "board D (SA868 and logic)", "panel board C",
                 "cooler fan slot 1")
        for n in names:
            P("   l9pwr %-26s %s" % (n, "; ".join("%s %g/%g/%g W" % ((s,) + v) for s, v in sorted(L9.get(n, {}).items()))))
        P("")
        R0 = {(i["tree"], i["board"], i["ref"]): i for i in rows}
        P("5b. ROUND 2 (V6-m4): THE DOWNSTREAM RATINGS READ AT THE INSIDE AIR, record l8r2's least-rating method (each sheet's range INCLUDES its")
        P("   own rise and prints no rise at current and no derating curve: the part may add (top - air) K, and the rise at the printed rating is")
        P("   taken as the whole span from 25 C to the range's top, the most severe reading the sheet allows; heating as the current squared:")
        P("   I_air = I_printed x sqrt((top - air) / (top - 25)), MODEL on PRINTED figures; the rating's own ambient is not printed, 25 C is")
        P("   record l8r2's reading, ASSUMPTION). Air: L4-E12 E5's mixed %.2f C (the case's air; %.2f C in the exhaust)" % (F["air"], F["air_exhaust"]))
        AIR = {}
        for ref, conds in (("U23", (("J_LIME, Wurth 692122030100 VBUS contact", F["c_usb3a"], F["t_usb3a"], "C_USB3A, C_USB3A_T"),)),
                           ("U24", (("J_RB9704's IDC socket contact, Wurth 61201623021", F["c_idc16"], F["t_idc16"], "C_IDC16, C_IDC16_T"),
                                    ("the 16-way flat cable conductor, Wurth 63911615521CAB", F["c_rib16"], F["t_rib16"], "C_RIB16, C_RIB16_T, C_RIB16_D")))):
            e = R0[("EFUSE", "b", ref)]
            need_ = max(x[1] for x in e["demand"])
            for what, ipr, top, q in conds:
                ia = ipr * math.sqrt(max(0.0, top - F["air"]) / (top - 25.0))
                ix = ipr * math.sqrt(max(0.0, top - F["air_exhaust"]) / (top - 25.0))
                t_need = top - (top - 25.0) * (need_ / ipr) ** 2
                t_top = top - (top - 25.0) * (e["band"][1] / ipr) ** 2
                AIR[(ref, what)] = (ia, need_, e["band"][1], t_need, t_top)
                P("   B %s %s: %.3f A PRINTED, range to %.0f C (%s): %.4f A at %.2f C (%.4f A at %.2f C)" % (
                    ref, what, ipr, top, q, ia, F["air"], ix, F["air_exhaust"]))
                P("        against the load's own demand %.4f A: %s; against U%s's band top %.4f A (the most the eFuse passes): %s" % (
                    need_, "covered" if ia >= need_ else "NOT COVERED", ref[1:], e["band"][1], "covered" if ia >= e["band"][1] else "NOT COVERED"))
                P("        the largest air at which the rating covers the demand: %.1f C; the band's top: %.1f C (MODEL)" % (t_need, t_top))
        P("   VENDOR CONDITION (both rows): the makers print no rise at current and no derating curve (the cable sheet only 'current rating")
        P("   may decrease due to the derating effect at higher temperatures'); the full-span reading above is the most severe the sheets allow.")
        P("   PROVISIONAL (amendment 1): EF-F01's and EF-F02's (c) hold on the printed ratings at 25 C (section 6) and are PROVISIONAL at the inside")
        P("   air until the supplier's measurement or a design alternative settles them: the receptacle or harness at the band's top current in a")
        P("   76 C chamber, the contact temperature at or under the range's top (85 C, 105 C); alternatives: a USB receptacle whose printed")
        P("   rating holds at the inside air (a range to 105 C or a printed derating curve), or J_LIME placed where the local air is bounded")
        P("   under the largest air above. No eFuse setting answers U23's row: the LimeSDR's own demand is above the rating's full-span reading.")
        P("   For U24 the module's printed 0.500 A is covered; only the eFuse's band top is not, and no TPS2596 setting can put its top under the")
        P("   conductor's reading while its foot stays at 0.500 A (the band's ratio of top to foot is %.3f at R43)" % (R0[("EFUSE", "b", "U24")]["band"][1] / R0[("EFUSE", "b", "U24")]["band"][0]))
        foot24 = R0[("EFUSE", "b", "U24")]["band"][0]
        P("   V6-m5, THE ROCKBLOCK'S CHARGE PADS: the supercapacitors' default charge current about %.3f A (L_RB_CHG), about %.3f A with two pads" % (F["l_rb_chg"], F["l_rb_chg_up"]))
        P("   bridged (L_RB_CHG_UP); U24's foot %.4f A holds the default and NOT the bridged figure: a build condition, the pads OPEN (drafted for" % foot24)
        P("   ASSEMBLY.md in apply_assembly_rb_pads.py, section 8)")
        P("")
        P("6. THE JUDGEMENT: (a) range, (b) the band's minimum against the demand, and its start-up, (c) the band's maximum against the")
        P("   downstream, with the switch's own continuous rating beside, (d) the label")
        shown = set()
        for i in rows:
            k = (i["board"], i["ref"], i["value"], i["set_text"])
            if k in shown:
                continue
            shown.add(k)
            P("   %-7s %s %-5s %-9s %s" % (i["tree"], i["board"].upper(), i["ref"], i["family"], i["verdict"]))
            for x in "abcd":
                P("        (%s) %s" % (x, i[x]))
            if i["start_v"] != "n/a":
                P("        (b, start) %s" % i["start_v"])
            if i["own"]:
                P("        (own) %s" % i["own"])
        P("")
        P("7. FINDINGS")
        seen = set(); unreg = []
        for i in rows:
            if i["tree"] == "EFUSE":
                continue
            k = (i["tree"], i["board"], i["ref"])
            f = FINDINGS.get(k)
            if i["verdict"].startswith("DEFECT"):
                if not f:
                    unreg.append(k)
                    P("   UNREGISTERED DEFECT %s %s %s: %s" % (k + (i["verdict"],)))
                elif f[0] not in seen:
                    seen.add(f[0])
                    P("   %-7s %s, %s: %s %s %s; %s" % (f[0], f[1], f[2], i["tree"], i["board"].upper(), i["ref"], f[3]))
            elif f:
                P("   %-7s RESOLVED IN THIS TREE (%s %s %s reads %s): the record's text is to be restated" % (f[0], k[0], k[1].upper(), k[2], i["verdict"]))
        P("   unregistered defects: %d" % len(unreg))
        # labelling findings and observations, each computed from the rows above
        R = {(i["tree"], i["board"], i["ref"]): i for i in rows}
        b23, b24 = R[("DRAWN", "b", "U23")], R[("DRAWN", "b", "U24")]
        lime = dict(b23["rails"]).get("+5V_LIME", {}); rb = dict(b24["rails"]).get("+5V_RB", {})
        need23 = max(x[1] for x in M[("b", "U23")]["demand"]); need24 = max(x[1] for x in M[("b", "U24")]["demand"])
        if lime.get("amps_typ", 0) > need23:
            P("   EF-L01  LABEL, OPEN (board B's generator owner): +5V_LIME declares %.2f A typical and %.2f A peak (J_LIME %.2f A) and "
              "_DEV_LOADS gives U23 %.2f A, with no source; the maker prints 4.5 W at most (%.4f A at C-DEV rev 1's least voltage) and a "
              "5 V, 900 mA host supply. The note's 'peaks higher while its FPGA configures' has no printed figure. EF-F01's draft "
              "restates the note's resistor and leaves the declared figures to the owner (they are conservative for the copper)" % (
                  lime["amps_typ"], lime["amps_peak"], lime["loads"].get("J_LIME", 0), lime["amps_typ"], need23))
        if rb.get("amps_peak", 0) > min(x[1] for x in M[("b", "U24")]["down"]):
            P("   EF-L02  LABEL, OPEN (board B's generator owner): +5V_RB declares a %.2f A peak (J_RB9704 %.2f A, 'the burst current on a "
              "transmit attempt') against the maker's DC input maximum %.3f A and the one 5 V conductor's %.1f A; after EF-F02 the "
              "eFuse passes at most %.4f A" % (rb["amps_peak"], rb["loads"].get("J_RB9704", 0), need24,
                                                min(x[1] for x in M[("b", "U24")]["down"]), R[("EFUSE", "b", "U24")]["band"][1]))
        e23, e24 = R[("EFUSE", "b", "U23")], R[("EFUSE", "b", "U24")]
        P("   EF-L03  LABEL, OPEN (Layer 6, part identities): Layer 6's board B table keys R36 and R43 on '301R 1%% (ILM: 3.0 A)' "
          "(C25192); after EF-F01 and EF-F02 R36 reads %r (code %s by lcsc_fill.py's map, the code Layer 6 read for board A's R90) and R43 %r "
          "(no code read: a 1.21 kOhm 1 %% 0603 is owed). Layer 6's draft applies after this record's drafts (out 8) and its value "
          "key then no longer matches R36 or R43" % (e23["setting"][0]["value"], e23.get("set_code"), e24["setting"][0]["value"]))
        nocode = sorted("%s %s %s (%s)" % (i["tree"], i["board"].upper(), i["ref"], i["mpn"]) for i in rows
                        if i["tree"] == "DRAFTED" and not i["code"] and not i.get("from_text"))
        if nocode:
            P("   EF-L04  LABEL, OPEN (Layer 6, part identities): the pending drafts place %s with no LCSC code; the "
              "orderable part is the draft's text alone" % "; ".join(nocode))
        lab5 = []
        for k, said in ((("DRAFTED", "b", "U702"), "0.448 to 0.538 A"), (("DRAFTED", "b", "U901"), "1.375 to 1.614 A")):
            if k in R and R[k]["band"]:
                lab5.append("%s %s's text says %s by interpolating between the printed rows (INFERRED); the printed bound across "
                            "the range gives %.4f to %.4f A, and (b) and (c) hold on it" % (k[1].upper(), k[2], said, R[k]["band"][0], R[k]["band"][1]))
        if lab5:
            P("   EF-L05  LABEL, OPEN (record l8r2's owner): " + "; ".join(lab5))
        sw = sorted("%s %s (%s -> %s)" % (i["board"].upper(), i["ref"], i["vin"], i["vout"]) for i in rows if i["tree"] == "DRAWN" and i["family"] == "tps22810")
        P("   EF-O01  OBSERVATION (generator owners, Layers 8 and 9): the TPS22810 load switches %s limit no current (the sheet: a "
          "load switch 'With Thermal Protection', no current-limit row); a fault behind one is limited only by the stage that feeds "
          "its input, and no record may count it as a current limit" % "; ".join(sw))
        if "b" in dropped:
            P("   EF-O02  OBSERVATION (record l8r2's owner; known to its round 8 on fnd/l8r4, not on this tree): board B's pending chain does "
              "not regenerate on this tree: %s after %s" % (dropped["b"][1][:110], dropped["b"][0]))
        a21 = R[("DRAWN", "a", "U21")]
        P("   EF-O04  OBSERVATION (board A's generator owner, Layer 9): U21's band minimum %.4f A clears the monitor's 10 W at VBAT's "
          "9.688 V floor (%.4f A) by %.3f A; the monitor's own start current and input capacitance are not printed (start-up CONDITION)" % (
              a21["band"][0], max(x[1] for x in a21["demand"]), a21["band"][0] - max(x[1] for x in a21["demand"])))
        b5 = R[("DRAWN", "b", "U5")]
        P("   EF-O05  OBSERVATION (board B's generator owner): the PoE port's ICUT band %.4f to %.4f A clears the declared 0.60 A by "
          "%.3f A with R12 at 250 mOhm 1 %%; at TI's 255 mOhm the foot would be %.4f A" % (
              b5["band"][0], b5["band"][1], b5["band"][0] - 0.60, F["t61_icut110"][0] / (0.255 * 1.01 * (1 + 100e-6 * 60))))
        e21 = R.get(("DRAFTED", "e", "U21"))
        if e21 and e21["band"]:
            P("   EF-O06  OBSERVATION (record l4e7's owner): R87's text says 'its breaker at 6.36 to 7.14 A, over the panel's 6.8 A'; the "
              "printed band %.4f to %.4f A straddles 6.8 A, so the text is right only if the cut-off may trip on the panel's 6.8 A "
              "(the record's to state); against PV_P's declared 6.25 A (b) holds" % e21["band"])
        P("")
        P("8. THIS RECORD'S DRAFTS (EF-F01, EF-F02; round 2: EF-F03 and the ASSEMBLY.md row): composition, the netlist, the mutations, the band")
        for order_name, seq in (("forward", MY_DRAFTS["b"]), ("reverse", MY_DRAFTS["b"][::-1])):
            p, res = compose("b", d, extra=seq)
            P("   %-8s %s" % (order_name, "; ".join("%s %s" % (os.path.basename(r), v) for r, v in res[-2:])))
        pf = compose("b", d, extra=MY_DRAFTS["b"])[0]; pr = compose("b", d, extra=MY_DRAFTS["b"][::-1])[0]
        P("   the two orders give the same text: %s" % (open(pf, "rb").read() == open(pr, "rb").read()))
        # the drafts alone on main's generator, and each on the composed generator a second time (refused)
        p0 = os.path.join(d, "b_alone.py"); shutil.copy(os.path.join(ROOT, GEN["b"]), p0)
        alone = [(os.path.basename(s), run_apply(os.path.join(ROOT, s), p0)[0]) for s in MY_DRAFTS["b"]]
        again = [(os.path.basename(s), run_apply(os.path.join(ROOT, s), p0)[0]) for s in MY_DRAFTS["b"]]
        P("   on main's generator alone: %s; a second run: %s" % (alone, again))
        tree_rc = subprocess.run([sys.executable, "-B", os.path.join(ROOT, MY_DRAFTS["b"][0]), os.path.join(ROOT, GEN["b"]), "--check"],
                                 capture_output=True).returncode
        P("   --check on the repository's own generator: exit %d (a check writes nothing; --write is refused until RELEASE.md)" % tree_rc)
        txt = open(net_eb, encoding="utf-8").read()
        need23 = max(x[1] for x in M[("b", "U23")]["demand"]); cap23 = min(x[1] for x in M[("b", "U23")]["down"] + [("own", F["t96_imax"], None)])
        need24 = max(x[1] for x in M[("b", "U24")]["demand"]); cap24 = min(x[1] for x in M[("b", "U24")]["down"] + [("own", F["t96_imax"], None)])
        base_txt = open(nets[("DRAFTED", "b")], encoding="utf-8").read()
        checks = [
            ("EFUSE netlist, U23", check_ilm(txt, F, "U23", "R36", need23, cap23), True),
            ("EFUSE netlist, U24", check_ilm(txt, F, "U24", "R43", need24, cap24), True),
            ("DRAFTED netlist (no correction), U23", check_ilm(base_txt, F, "U23", "R36", need23, cap23), False),
            ("DRAFTED netlist (no correction), U24", check_ilm(base_txt, F, "U24", "R43", need24, cap24), False),
            ("mutation: R36 back to 301R", check_ilm(mutate_value(txt, "R36", "301R 1% (ILM: 3.0 A)"), F, "U23", "R36", need23, cap23), False),
            ("mutation: R43 to 909R (band top over 1 A)", check_ilm(mutate_value(txt, "R43", "909R 1% (ILM: 1.0 A)"), F, "U24", "R43", need24, cap24), False),
            ("mutation: R43 to 1.87k (band under 500 mA)", check_ilm(mutate_value(txt, "R43", "1.87k 1% (ILM: 0.49 A)"), F, "U24", "R43", need24, cap24), False),
            ("mutation: R36's GND pin onto +5V_LIME", check_ilm(mutate_far_pin(txt, "R36", "+5V_LIME"), F, "U23", "R36", need23, cap23), False),
        ]
        okall = True
        for name, (ok, why), want in checks:
            good = ok == want; okall &= good
            P("   %-46s %-5s %s %s" % (name, "PASS" if ok else "FAIL", "(as required)" if good else "(NOT AS REQUIRED)", why))
        P("   the netlist reading and its mutations: %s" % ("every check reads as required" if okall else "A CHECK DID NOT READ AS REQUIRED"))
        # the alternatives: every E96 value (1 %, 100 ppm/K) whose printed band holds (b) and (c) for each corrected eFuse
        e96 = [100, 102, 105, 107, 110, 113, 115, 118, 121, 124, 127, 130, 133, 137, 140, 143, 147, 150, 154, 158, 162, 165, 169, 174,
               178, 182, 187, 191, 196, 200, 205, 210, 215, 221, 226, 232, 237, 243, 249, 255, 261, 267, 274, 280, 287, 294, 301, 309,
               316, 324, 332, 340, 348, 357, 365, 374, 383, 392, 402, 412, 422, 432, 442, 453, 464, 475, 487, 499, 511, 523, 536, 549,
               562, 576, 590, 604, 619, 634, 649, 665, 681, 698, 715, 732, 750, 768, 787, 806, 825, 845, 866, 887, 909, 931, 953, 976]
        for name, need, cap in (("U23 (R36)", need23, cap23), ("U24 (R43)", need24, cap24)):
            ok = []
            for dec in (1, 10, 100):
                for v in e96:
                    bb = t96_band(F, v * dec, 0.01, TCR_DEFAULT)
                    if bb[1] is not None and bb[1] >= need and bb[3] <= cap:
                        ok.append((v * dec, bb[1], bb[3]))
            P("   E96 values whose printed band holds %s's (b) %.4f A and (c) %.4f A: %s" % (
                name, need, cap, ", ".join("%g (%.4f to %.4f A)" % x for x in ok) if ok else "none"))
        # round 2: board A's draft (EF-F03)
        p0a = os.path.join(d, "a_alone.py"); shutil.copy(os.path.join(ROOT, GEN["a"]), p0a)
        alone_a = run_apply(os.path.join(ROOT, MY_DRAFTS["a"][0]), p0a)[0]
        again_a = run_apply(os.path.join(ROOT, MY_DRAFTS["a"][0]), p0a)[0]
        tree_a = subprocess.run([sys.executable, "-B", os.path.join(ROOT, MY_DRAFTS["a"][0]), os.path.join(ROOT, GEN["a"]), "--write"],
                                capture_output=True).returncode
        P("   EF-F03 (board A): after board A's %d pending drafts: %s; on main's generator alone: exit %d, a second run exit %d; --write on the" % (
            len(ORDER["a"]), "; ".join("%s %s" % (os.path.basename(r), v) for r, v in res_ea[-1:]), alone_a, again_a))
        P("   repository's own generator: exit %d (refused until RELEASE.md)" % tree_a)
        txa = open(net_ea, encoding="utf-8").read()
        base_a = open(nets[("DRAFTED", "a")], encoding="utf-8").read()
        needa = max(x[1] for x in M[("a", "U23")]["demand"]); capa = min(x[1] for x in M[("a", "U23")]["down"] + [("own", F["t96_imax"], None)])
        checks_a = [
            ("EFUSE netlist, board A U23", check_ilm(txa, F, "U23", "R98", needa, capa), True),
            ("DRAFTED netlist (no correction), A U23", check_ilm(base_a, F, "U23", "R98", needa, capa), False),
            ("mutation: R98 back to 453R", check_ilm(mutate_value(txa, "R98", "453R 1% (ILM: 2.0 A)"), F, "U23", "R98", needa, capa), False),
            ("mutation: R98 to 2k (band under the demand)", check_ilm(mutate_value(txa, "R98", "2k 1% (ILM: 0.46 A)"), F, "U23", "R98", needa, capa), False),
            ("mutation: R98's GND pin onto +5V_D8", check_ilm(mutate_far_pin(txa, "R98", "+5V_D8"), F, "U23", "R98", needa, capa), False),
        ]
        oka = True
        for name, (ok, why), want in checks_a:
            good = ok == want; oka &= good
            P("   %-46s %-5s %s %s" % (name, "PASS" if ok else "FAIL", "(as required)" if good else "(NOT AS REQUIRED)", why))
        ea = R[("EFUSE", "a", "U23")]
        P("   board A's U23 on R98 511 R: (a) %s; band %.4f to %.4f A; (b) %s; (c) %s; own: %s" % (ea["a"], ea["band"][0], ea["band"][1], ea["b"], ea["c"], ea["own"]))
        P("   the netlist reading and its mutations (board A): %s" % ("every check reads as required" if oka else "A CHECK DID NOT READ AS REQUIRED"))
        okall &= oka
        ok511 = [(v * dec, t96_band(F, v * dec, 0.01, TCR_DEFAULT)) for dec in (1, 10) for v in e96]
        ok511 = [(r_, b_[1], b_[3]) for r_, b_ in ok511 if b_[1] is not None and r_corners(r_, 0.01, TCR_DEFAULT)[0] >= F["t96_rilm"][0]
                 and b_[1] >= needa and b_[3] <= capa]
        P("   E96 values whose corners stay inside the range and whose printed band holds board A U23's (b) %.4f A and (c) %.4f A: %s" % (
            needa, capa, ", ".join("%g (%.4f to %.4f A)" % x for x in ok511[:6]) + (" ..." if len(ok511) > 6 else "")))
        # round 2: the ASSEMBLY.md draft (V6-m5) on a scratch copy
        pas = os.path.join(d, "ASSEMBLY.md"); shutil.copy(os.path.join(ROOT, "v2", "docs", "ASSEMBLY.md"), pas)
        before_as = sha("v2/docs/ASSEMBLY.md", 64)
        r1 = subprocess.run([sys.executable, "-B", os.path.join(ROOT, ASSEMBLY_DRAFT), pas], capture_output=True)
        r2 = subprocess.run([sys.executable, "-B", os.path.join(ROOT, ASSEMBLY_DRAFT), pas, "--write"], capture_output=True)
        r3 = subprocess.run([sys.executable, "-B", os.path.join(ROOT, ASSEMBLY_DRAFT), pas, "--write"], capture_output=True)
        as_ok = r1.returncode == 0 and r2.returncode == 0 and r3.returncode == 3 and "charge-current pads stay OPEN" in open(pas, encoding="utf-8").read() \
            and sha("v2/docs/ASSEMBLY.md", 64) == before_as
        P("   apply_assembly_rb_pads.py on a scratch copy of ASSEMBLY.md: check exit %d, written exit %d, a second run exit %d, the tree's page "
          "untouched: %s" % (r1.returncode, r2.returncode, r3.returncode, "yes" if as_ok else "NO"))
        P("   the variant: no TPS2596-family part has a fixed limit or a range above %g A; the sibling TPS2595xx prints %g to %g A with RILM "
          "%g to %g Ohm (T95_RANGE, T95_RILM) and would be the part for a limit near 3 A; the loads here need at most %.4f A, so the "
          "TPS259631 stays and only its resistor changes" % (F["t96_range"][1], nums("T95_RANGE")[0], nums("T95_RANGE")[1],
                                                             nums("T95_RILM")[0], nums("T95_RILM")[1], max(need23, need24)))
        # Layer 6's LCSC table after this record's drafts
        l6 = os.path.join(RECS, "l6r2", "apply_gen_sch_b_lcsc.py")
        p6 = os.path.join(d, "b_l6.py"); shutil.copy(pf, p6)
        rc6, msg6 = run_apply(l6, p6)
        P("   Layer 6's apply_gen_sch_b_lcsc.py after this record's drafts: %s" % ("OK" if rc6 == 0 else "REFUSED (%s)" % msg6[:160]))
        P("")
        P("9. PREDICATES")
        P("   every quote in its sheet: %s" % ("YES" if not bad else "NO"))
        P("   every DRAWN TPS2596 setting inside 453 to 7869 Ohm: %s" % ("YES" if all(i["band"] for i in rows if i["tree"] == "DRAWN" and i["family"] == "tps2596")
                                                                        else "NO: " + ", ".join("%s %s" % (i["board"].upper(), i["ref"]) for i in rows
                                                                                                if i["tree"] == "DRAWN" and i["family"] == "tps2596" and not i["band"])))
        P("   every EFUSE TPS2596 setting inside the range: %s" % ("YES" if all(i["band"] for i in rows if i["tree"] == "EFUSE" and i["family"] == "tps2596") else "NO"))
        P("   unregistered defects: %d; this record's netlist checks as required: %s" % (len(unreg), "YES" if okall else "NO"))
        P("   round 2: board B's full composition regenerates without a dropped draft: %s; the ASSEMBLY.md draft applies once: %s" % (
            "YES" if "b" not in dropped and drop_eb is None else "NO", "YES" if as_ok else "NO"))
        P("   round 2: every EFUSE TPS2596 setting's corners inside the range: %s" % (
            "YES" if all(i["a"] == "PASS" for i in rows if i["tree"] == "EFUSE" and i["family"] == "tps2596") else "NO"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
