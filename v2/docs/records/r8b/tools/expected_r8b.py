#!/usr/bin/env python3
"""The round's declared change list for board B (MESHSAT-1357 round 8, stream b), each item tied to its finding id, written
as the --expect input of netdiff_r8b.py. Every pattern is a full-match regular expression over a reference or a net name.
Usage: expected_r8b.py > expected_r8b.json"""
import json
S = "[123]"
ITEMS = [
 # (finding, kind, patterns, [allowed fields for parts_changed | node refs for nets_changed])
 ("FAB-01", "parts_added", [r"R%s90" % S]),
 ("FAB-01", "nets_added", [r"/S%s_TEST2" % S, r"unconnected-\(U%s01-(TCK-Pad89|TDI-Pad93)\)" % S]),
 ("FAB-01", "nets_changed", [r"/S%s_TESTL" % S, r"/S%s_JTAGL" % S, r"/\+3V3_S%sB" % S], [r"U%s01" % S, r"R%s90" % S]),
 ("FAB-02", "parts_added", [r"R%s91" % S, r"R%s92" % S, "U519", "U520", "C564", "C565", r"U51[345]", "C518", "C519", "C560",
                            # pass 2: PG{s} reaches logic only through a Schmitt buffer (the 74LVC1G157's 10 ns/V rule) and its inverse
                            r"U53[0-5]", r"C58[5-9]", "C590"]),
 ("FAB-02", "parts_removed", ["R14"]),
 ("FAB-02", "nets_added", [r"/PG%s" % S, r"/PG%s_S" % S, r"/PG%s_n" % S, r"/PGSEL%s_n" % S, "/HDMI_EN1", "/HDMI_EN2",
                           r"unconnected-\(U53[0-5]-NC-Pad1\)"]),
 ("FAB-02", "nets_removed", ["/HDMI_SW_EN"]),
 ("FAB-02", "nets_changed", ["/HDMI_SEL1", "/HDMI_SEL2"], ["U519", "U520"]),
 ("FAB-03", "parts_added", ["U81", "U84", "U85", "C566", "C567", "C572", r"U50[789]", r"U51[012]", r"C51[2-7]", r"R519", "R520", "R521",
                            r"C56[89]", "C570", r"U51[678]", r"C56[123]",
                            # pass 2: the ARM stage (R522 to R524, C573 to C575, U521 to U523, C576 to C578) and the lock muxes
                            r"R52[234]", r"C57[3-9]", r"C58[0-4]", r"U52[1-9]"]),
 ("FAB-03", "parts_changed", ["U80"], ["value"]),
 ("FAB-03", "nets_added", [r"/BBM%s" % S, r"/BBM%s_(REQ|ARM|ARMR|MOV|RA)" % S, r"/BSEL%s_S" % S, r"/BSEL%s_D2" % S, r"/BSEL%s_D2R" % S,
                           r"/BSEL%s_H1?" % S,
                           r"unconnected-\(U81-NC-Pad(8|11)\)", r"unconnected-\(U8[45]-NC-Pad11\)",
                           r"unconnected-\(U5(0[789]|1[012]|2[123])-NC-Pad1\)"]),
 ("FAB-03", "nets_removed", [r"unconnected-\(U80-NC-Pad11\)"]),
 ("FAB-03", "nets_changed", [r"/BSEL%s" % S, r"/BSEL%s_D" % S, r"/BOE%s_n" % S], [r"U80", r"U%s09" % S, r"U%s10" % S, r"U50[789]", r"U51[678]",
                                                                             r"R47[456]", r"U52[456]"]),
 ("FAB-04", "parts_changed", [r"R4[89]\d|R500", "R15", "R16"], ["value"]),
 ("L1", "parts_added", ["U506", "C511", "R518"]),
 ("L1", "nets_added", ["/EMCON_SUP", r"unconnected-\(U506-NC-Pad1\)"]),
 ("L2", "parts_added", [r"U50[1-5]", "C508", "C509", "C510"]),
 ("L2", "parts_removed", ["U19", "U20"]),
 ("L2", "parts_changed", ["R58"], ["value"]),
 ("L2", "nets_removed", [r"unconnected-\(U20-NC-Pad(6|8|11)\)"]),
 ("L2", "nets_changed", ["/E22_EN", "/E72_EN", "/LIME_EN", "/LIME_EN_A", "/LIME_HW_EN", "/LIME_SW_EN", "/LORA_ON", "/RB_EN",
                         "/RB_SW_EN", "/ZB_ON"], [r"U19", r"U20", r"U50[1-5]"]),
 ("L3", "parts_added", [r"U%s1[2-5]" % S, r"C%s8[345]" % S, "C261", "C262", "C285", r"TP%s04" % S]),
 ("L3", "parts_removed", ["Q11", "R513", r"U%s11" % S, r"Q%s09" % S, r"Q%s10" % S, r"R%s7[34]" % S]),
 ("L3", "nets_added", [r"/EMCON_ON%s" % S, r"unconnected-\(U%s12-NC-Pad1\)" % S]),
 ("L3", "nets_removed", ["/EMCON_ON", r"/(WL|BT)_nDIS%s_KILL" % S, r"unconnected-\(U%s11-NC-Pad(8|11)\)" % S]),
 ("L3", "nets_changed", [r"/(WL|BT)_nDIS%s" % S, r"/(WL|BT)_nDIS%s_OFF" % S, r"/\+3V3_CM%s" % S, "/EMCON_HW"],
  [r"U%s1[1-5]" % S, r"Q%s(09|10)" % S, r"C%s97" % S, r"C%s8[345]" % S, "C261", "C262", "C285", "C299", r"R%s91" % S, "U220",
   "Q11", r"U(19|20)", r"U[456]1", r"U50[1-6]"]),
 ("L7", "parts_removed", [r"Q%s06" % S, "Q111", "Q311"]),
 ("L7", "nets_changed", ["/WIFI_W_DIS_n", "/5G_W_DIS_n", "/WIFI2_W_DIS_n", "/S1A_EN", "/S3A_EN"], [r"Q%s(06|11)" % S, r"U%s15" % S]),
 ("SD-EMC-1", "parts_added", ["R264", "U220", "C299", "U221", "R297", "C200", "Q212", "R295", "R296"]),
 ("SD-EMC-1", "nets_added", ["/S2A_EN", "/5G_DCHG", "/5G_TPR_CT", r"unconnected-\(U22[01]-NC-Pad(3|4)\)"]),
 ("SD-EMC-1", "nets_changed", ["/PCIE_PWR_EN2", "/5G_PWROFF_n", r"/\+3V3_M2C2", r"/\+3V3_S2A"], ["U203", "R264", "U220", "U221", "R295", "R297", "C200"]),
 ("SD-EMC-2", "parts_added", [r"R%s94" % S]),
 ("SD-EMC-2", "nets_added", [r"/CARD%s_PERST_n" % S]),
 ("SD-EMC-2", "nets_removed", [r"unconnected-\(U2[12]-QOD-Pad2\)"]),
 ("SD-EMC-2", "nets_changed", [r"/PCIE%s_RST2_n" % S, r"/\+5V_LORA", r"/\+3V3_ZB"], [r"J_M2C%s" % S, r"R%s94" % S, "U21", "U22"]),
 ("I3-F01", "nets_changed", ["/EMCON_HW"], [r"U[456]1"]),
 ("S-12", "parts_changed", ["J_M2C2"], ["footprint", "field:Footprint"]),
 ("S-13", "parts_added", ["U222", "U223"]),
 ("S-13", "nets_added", [r"unconnected-\(U22[23]-NC-Pad6\)"]),
 ("S-13", "nets_changed", ["/SIM1_VCC", "/SIMC2_VCC", r"/SIMC[12]_(CLK|IO|RST)"], ["U222", "U223"]),
 ("B_PANEL_5V", "parts_changed", ["F1"], ["value", "field:LCSC"]),
 ("G4", "parts_added", [r"C60[56]", r"C63[56]", r"C66[56]", "C571"]),
 ("G4", "nets_changed", [r"/\+5V_S%s" % S, r"/\+5V_DEV"], [r"C6[036][56]", "C571"]),
 ("G6", "parts_added", []),
 ("G7", "parts_added", [r"C60[1-4]", r"C63[1-4]", r"C66[1-4]", r"C53\d", r"C54\d", "C550", r"C55[1-8]", r"C4[135][23]"]),
 ("G7", "parts_changed", ["C27", "C28"], ["value"]),
 ("G7", "nets_changed", [r"/\+1V1_S%s" % S, r"/\+1V2_KSZ", r"/\+2V5_KSZ", r"/\+3V3_IOC[ABC]", r"/\+5V_DEV", r"/\+3V3_DEV"],
  [r"C6[036][1-4]", r"C5[345]\d", r"C4[135][23]"]),
 ("PARTS-RETAKE row 1 (DS3231SN)", "parts_changed", ["U9"], ["footprint", "field:Footprint", "value", "lib", "part", "field:Description"]),
 ("PARTS-RETAKE row 1 (DS3231SN)", "nets_changed", ["/SCL", "/SDA", "/VBAT"], ["U9"]),
 ("PARTS-RETAKE row 6 (U.FL C88373)", "parts_changed", [r"J_W(1A|1B|3A|3B|OA|OB)"], ["field:LCSC"]),
 # the rails and ground every added or removed part above sits on
 ("(the parts above: their supply and ground pins)", "nets_changed", [r"/\+3V3_DEV", "GND"],
  [r"C(19|29|39)7", r"R14", r"R513", r"U%s11" % S, r"U(19|20)", r"C5(0[89]|1\d|6\d|7\d|8\d|90)", r"C5[345]\d", r"C6[036][1-6]",
   r"U5(0\d|1\d|2\d|3[0-5])", "U81", "U84", "U85", r"Q%s(06|09|10|11)" % S, "Q11", r"R%s7[34]" % S, r"U80", r"C%s8[345]" % S, "C200", "C261",
   "C262", "C285", "C299", r"C4[135][23]", "Q212", r"R%s92" % S, "R296", "R518", r"U%s1[2-5]" % S, "U220", "U221", "U222",
   "U223", "U9"]),
]
out = {"parts_added": [], "parts_removed": [], "parts_changed": {}, "nets_added": [], "nets_removed": [], "nets_changed": {},
       "_findings": []}
for it in ITEMS:
    f, kind, pats = it[0], it[1], it[2]
    out["_findings"].append({"finding": f, "kind": kind, "patterns": pats, "allowed": it[3] if len(it) > 3 else None})
    if kind in ("parts_changed",):
        for p in pats: out[kind].setdefault(p, []); out[kind][p] = sorted(set(out[kind][p]) | set(it[3]))
    elif kind == "nets_changed":
        for p in pats: out[kind].setdefault(p, []); out[kind][p] = sorted(set(out[kind][p]) | set(it[3]))
    else:
        out[kind] += pats
print(json.dumps(out, indent=1))
