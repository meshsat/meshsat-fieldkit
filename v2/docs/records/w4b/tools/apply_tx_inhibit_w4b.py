#!/usr/bin/env python3
"""Stream w4b (MESHSAT-1357, 27 September 2026): a DRAFT for the owner of v2/ecad/tools/tx_inhibit.py (the tools author, r4t
line), not applied in the stream's worktree. Usage: apply_tx_inhibit_w4b.py <path to tx_inhibit.py> [--check]

Three table changes, each the hand-off EMCON.md section 8 already names for the tools author (board B's round 8, section 4b),
none of them a change to how the walk reasons:
  1. a LOGIC row for the TI SN74LVC2G06 dual open-drain inverter (SCES307J), with its maker's open-drain words in
     _LOGIC_ROWS, as the 74LVC2G07 and 74LVC1G06 rows are drawn. Without it the walk stops at U{s}13, U{s}15 and U220
     ("no pin map") and reads the six Compute Module radios, both AW7915-AED cards and the RM520N-GL "EMCON does not
     reach it"; board B has carried these open drains since round 8 (EMCON.md L7).
  2. U221 (TPS3808G30 supervisor, whose value names the RM520N because it holds the module's FULL_CARD_POWER_OFF# low
     on release) claimed in ACCESSORIES: it is neither a radio nor the radio's supply or keying point, and the census read
     board B FAIL on it.
  3. J_QMX moved from OWED to ACCESSORIES, citing QRP Labs' own schematics (PCB Rev 1, 2, 3/4 and 5, filed under
     v2/vendor/qrp-labs/): the USB-C connector J201's VBUS pin is not connected on any of them (EMCON.md 4.3, VERIFIED
     from the maker's drawings), which is the statement R4T-D17's OWED item asked for.
  4. the AO3400A (board B's Q212, the 5G rail's discharge FET on EMCON_ON2 since round 8) read as the N-channel MOSFET its
     maker calls it (AOS AO3400A Rev 3.1, v2/vendor/power/aos-ao3400a-n-mosfet.pdf, page 1: "30V N-Channel MOSFET"), so
     its gate on EMCON_ON2 is a FET gate that only reads, where the walk read "an active pin no held document shows to
     be an input" and left slot 2's two module radios and the 5G module UNDECIDED.
  5. a LOGIC row for the TI SN74LV1T08 (SCLS739F), board B's U116, U216 and U316 since stream w4b (W4B-D3): each slot's card
     buck enable S{s}A_EN = EMCON_HW AND PCIE_PWR_EN{s}, run from the buck's own input +5V_S{s}. Without it the walk stops at
     those gates and reads both AW7915-AED cards and the RM520N-GL's supply "EMCON does not reach it".
  6. _vcc_ok() reads a family's `vil_ok_bands` where the row carries one, in place of VCC_RANGE: the VCC bands in which
     its maker states a VIL of at least VIL_LOW. The SN74LV1T08 states VIL 0.8 V at VCC 4.5 V to 5.5 V and 0.65 V at 3 V to
     3.6 V (SCLS739F 6.5, -40 to +125 C), so VCC_RANGE is the wrong band for it both ways: at 5 V (board B's U{s}16) a hold
     under 0.8 V is a stated low, and at 3.3 V it would not be. No other row carries the field, so no other reading moves.
Every edit asserts the text it replaces and the file is re-parsed after. --check applies nothing and reports whether each
edit's anchor is present exactly once."""
import sys, ast

ROW_ANCHOR = '''    dict(name="74LVC07 hex open-drain buffer", value=r"74LVC07", fp=r"(TSSOP|SOIC|SSOP|SO)-14",'''
ROW_NEW = '''    # BOARD B's U{s}13, U{s}14, U{s}15 AND U220 SINCE ITS ROUND 8 (EMCON.md L7, section 4b): the per-slot EMCON open drains on
    # WL_nDisable, BT_nDisable, the cards' W_DISABLE1#, the card bucks' EN and the 5G module's FULL_CARD_POWER_OFF# are TI
    # SN74LVC2G06DBVR. Row added by stream w4b (27 September 2026), from the filed sheet v2/vendor/ti/ti-sn74lvc2g06.pdf. The
    # sheet's Pin Functions table marks 1Y "I" in its I/O column and "Open-drain output 1" in its description; the description,
    # the DBV drawing and 2Y's "O" row agree that pin 6 is an output. vil_ceiling: VIL 0.3 x VCC at VCC 4.5 V to 5.5 V (6.3).
    dict(name="74LVC2G06 dual open-drain inverter", value=r"74LVC2G06", fp=r"SOT-23-6|SC-70-6|SOT-363",
         gates=[(("1",), "6", "INV_OD"), (("3",), "4", "INV_OD")],
         cite="TI SN74LVC2G06, SCES307J (July 2015), Pin Functions (DBV, DCK): 1A 1, GND 2, 2A 3, 2Y 4, VCC 5, 1Y 6 "
              "(v2/vendor/ti/ti-sn74lvc2g06.pdf)",
         vcc=("5",), ii=5e-6, ioff=10e-6, vil_ceiling=1.65,
         leak_cite="SCES307J 6.5, -40 to +85 C and -40 to +125 C: II +-5 uA (A inputs, VCC 0 to 5.5 V), Ioff +-10 uA (VCC 0, "
                   "VI or VO 5.5 V); 6.3: VIL 0.8 V at VCC 3 V to 3.6 V, 0.3 x VCC at 4.5 V to 5.5 V"),
    # BOARD B's U116, U216 AND U316 SINCE STREAM w4b (W4B-D3, 27 September 2026): each slot's card buck EN = EMCON_HW AND
    # PCIE_PWR_EN{s}, an SN74LV1T08DBVR run from the buck's own input +5V_S{s}. Sheet fetched by stream w4b (TI SCLS739F,
    # drafts/w4b/datasheets/ti-sn74lv1t08.pdf, for v2/vendor/ti/). The sheet states II +-1 uA at VCC 0 V as well as powered
    # (VI 0 V or VCC), which bounds an unpowered input; it has no Ioff row for the output, whose power-off rating is 4.6 V
    # (6.1), so `ioff` carries the input figure and the output is never read unpowered on a held net. vil_ceiling: the
    # highest VIL any band states, 0.8 V at VCC 4.5 V to 5.5 V (-40 to +125 C). vih_gap: its VIH is 2.03 V at 4.5 V to 5.0 V
    # and 2.11 V at 5.5 V, above VIH_HIGH, so a HIGH at it never passes.
    dict(name="74LV1T08 AND", value=r"74LV1T08", fp=r"SOT-23-5|SC-70-5|SOT-353",
         gates=[(("1", "2"), "4", "AND")],
         cite="TI SN74LV1T08, SCLS739F (October 2025), Table 5-1 Pin Functions (DCK, DBV): A 1, B 2, GND 3, Y 4, VCC 5 "
              "(v2/vendor/ti/ti-sn74lv1t08.pdf)",
         vcc=("5",), ii=1e-6, ioff=1e-6, vil_ceiling=0.8,
         leak_cite="SCLS739F 6.5, -40 to +125 C: II +-1 uA (A input, VI 0 V or VCC, VCC 0 V, 1.8 V, 2.5 V, 3.3 V and 5.5 V); "
                   "VIL 0.8 V at VCC 4.5 V to 5.5 V, 0.65 V at 3 V to 3.6 V; no Ioff row for the output (6.1: 4.6 V in the "
                   "power-off state)",
         vih_gap="SCLS739F 6.5 states VIH 2.03 V maximum at VCC 4.5 V to 5.0 V and 2.11 V at 5.5 V, above VIH_HIGH's 2.0 V",
         # the VCC bands in which the sheet's VIL is at least VIL_LOW (0.8 V): 4.5 V to 5.5 V only. At 3 V to 3.6 V it states
         # 0.65 V (-40 to +125 C), so VCC_RANGE is NOT where this family reads 0.8 V as low (see _vcc_ok)
         vil_ok_bands=[(4.5, 5.5)]),
'''
OD_ANCHOR = '''    "74LVC07 hex open-drain buffer": dict(od_words="SCAS595W, page 1: 'SN74LVC07A Hex Buffer and Driver With Open-Drain "
                                                   "Outputs'"),
'''
OD_NEW = '''    "74LVC2G06 dual open-drain inverter": dict(od_words="SCES307J, page 1: 'SN74LVC2G06 Dual Inverter Buffer and Driver With "
                                                        "Open-Drain Outputs' and 'The output of the SN74LVC2G06 device is an "
                                                        "open-drain which can be connected to other open-drain outputs'"),
'''
ACC_ANCHOR = '''    dict(board="D", ref="J_VGG", value=r"PA gate bias", why="the PA's gate-bias lead, switched on this board by "
         "PA_KEY; the PA's supply is board A's J_PA, which is the gate this table relies on"),
]'''
ACC_NEW = '''    dict(board="D", ref="J_VGG", value=r"PA gate bias", why="the PA's gate-bias lead, switched on this board by "
         "PA_KEY; the PA's supply is board A's J_PA, which is the gate this table relies on"),
    # stream w4b, 27 September 2026 (EMCON.md section 8's hand-off for board B's round 8):
    dict(board="B", ref="U221", value=r"TPS3808", why="the TPS3808G30 supervisor on +3V3_S2A that holds the 5G module's "
         "FULL_CARD_POWER_OFF# low for 180 to 420 ms after the rail (SD-EMC-1r8, Quectel's Tpr); its value names the RM520N, "
         "and it is neither the radio nor its supply or keying point"),
    dict(board="B", ref="J_QMX", value=r"QMX USB lead", why="the QMX's USB data lead: QRP Labs' schematics for PCB Rev 1, "
         "Rev 2, Rev 3/4 and Rev 5 (v2/vendor/qrp-labs/qrplabs-qmx-schematics-rev1-a.pdf, -rev2.pdf, -rev3.pdf, -rev5.pdf, "
         "page 2) draw the USB-C connector J201's VBUS pin with no connection, and Rev 5's page 1 makes the unit's supplies "
         "from the DC jack J101 alone (EMCON.md 4.3); the QMX's hardware gate is board A's J_HF"),
]'''
OWED_ANCHOR = '''OWED = [
    dict(board="B", ref="J_QMX", value=r"QMX USB lead", why="the QMX's USB data lead",
         owed="a QRP Labs statement that USB VBUS does not power the QMX's transmitter, or VBUS_QMX switched off by "
              "EMCON on board B; until then the QMX's hardware gate (board A's J_HF) covers only its DC input"),
]'''
OWED_NEW = '''OWED = [
    # J_QMX left this list for ACCESSORIES (stream w4b, 27 September 2026): QRP Labs' own schematics answer it (EMCON.md 4.3).
]'''

FET_ANCHOR = '''           "N" if re.search(r"NMOS|2N7002|BSS138|N-FET|N-channel|Q_NMOS", txt, re.I) else None'''
FET_NEW = '''           "N" if re.search(r"NMOS|2N7002|BSS138|AO3400|N-FET|N-channel|Q_NMOS", txt, re.I) else None'''
VCC_ANCHOR = '''    vs = [v for v in vs if v is not None]
    if not vs: return False, None
    v = max(vs)
    return VCC_RANGE[0] <= v <= VCC_RANGE[1], v'''
VCC_NEW = '''    vs = [v for v in vs if v is not None]
    if not vs: return False, None
    v = max(vs)
    # a family whose sheet states VIL_LOW in other VCC bands than VCC_RANGE says so (`vil_ok_bands`, stream w4b)
    bands = (logic_of(nl, ref) or {}).get("vil_ok_bands")
    if bands: return any(lo <= v <= hi for lo, hi in bands), v
    return VCC_RANGE[0] <= v <= VCC_RANGE[1], v'''
EDITS = [("LOGIC rows 74LVC2G06, 74LV1T08", ROW_ANCHOR, ROW_NEW + ROW_ANCHOR),
         ("_vcc_ok reads vil_ok_bands", VCC_ANCHOR, VCC_NEW),
         ("fet_of: AO3400 is an N-channel MOSFET", FET_ANCHOR, FET_NEW),
         ("_LOGIC_ROWS od_words 74LVC2G06", OD_ANCHOR, OD_ANCHOR + OD_NEW),
         ("ACCESSORIES U221 and J_QMX", ACC_ANCHOR, ACC_NEW),
         ("OWED without J_QMX", OWED_ANCHOR, OWED_NEW)]


def main(a):
    if not a:
        print(__doc__); return 2
    p = a[0]; check = "--check" in a
    s = open(p, encoding="utf-8").read(); o = s
    bad = []
    for name, old, new in EDITS:
        n = s.count(old)
        print("%-34s anchor found %d time(s)" % (name, n))
        if n != 1: bad.append(name); continue
        if not check: s = s.replace(old, new, 1)
    if bad:
        print("REFUSED: anchors not found exactly once: %s" % bad); return 1
    if check:
        return 0
    assert s != o, "no change"
    ast.parse(s)
    open(p, "w", encoding="utf-8").write(s)
    print("applied to %s" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
