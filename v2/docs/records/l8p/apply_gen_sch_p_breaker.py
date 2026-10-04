#!/usr/bin/env python3
"""apply_gen_sch_p_breaker.py: DRAFT for board P's generator owner (Layer 8 record l8p, MESHSAT-1357, 4 October 2026). NOT
APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).

The defect: W4DP-F2 (record l9stk section 15, DD-1 and DD-6, on branch fnd/l9stk at 2c8b29fb, independently checked
CONFIRMED AS CONDITIONAL). With board P's FETs Q1 and Q2 welded and no firmware, nothing on this board opens the discharge path
on current alone (l9stk 15.2), and a docking with a breaker that is already on reaches E11-30's 242.9 A (15.4, B-P1).

The correction drawn here, every value from record l9stk by its section (the record page's section 2 lists each with its source):
  C-1 (15.4)    U101 LM5069MM-2 (C111822, board E's U6 part) from Q2's source, the new net BRK_VIN, to the pack terminal PACK_P;
                the sense pair R101 4 mOhm and R102 7.5 mOhm in parallel (1 %, at most 50 ppm/K); Q101 and Q102 CSD18510Q5B
                (C2876544, board A's PA stage part) from BRK_SNS to PACK_P; R103 RPWR 8.45 kOhm; C101 timer 10 nF; C102 dv/dt
                22 nF on the gate; D101 SMCJ18A (C374030, board A's VBAT clamp part) on BRK_VIN; OVLO, the controller's ground,
                the clamp and the small parts on PACK_N (IF-6).
  C-1b (15.4)   the make-last enable LOOP into UVLO with its RC hold: R106 10 kOhm from BRK_VIN onto J_SMB pin 7 (DOCK_EN_OUT),
                out over board E and the dock to board A's thermal guard RT1 and back on J_SMB pin 5 (DOCK_EN_RET) into R107
                22 kOhm on the first inverter Q103 (2N7002); Q103 holds the second inverter Q104's gate, R108 and R109 1 MOhm
                each from BRK_VIN (l9stk_protection.py's R_G, prot 3a), low; Q104 discharges UVLO through R105 150 ohm; R104
                200 kOhm from BRK_VIN and C103 3.3 uF 50 V make the RC hold. J_SMB pin 6 is the ground contact between the two
                loop conductors (C2), J_SMB a JST-XH 1x7 (pins 1 to 4 unchanged).
  IF-6          the gauge's PACK and VCC taps R6 and R7, and Q2's gate-source resistor R19, follow Q2's source to BRK_VIN; D1
                stays on PACK_P; VCC_F is fed from BRK_VIN.
SESSION choices (under the owner's standing rule of 26 September 2026; L8P-BREAKER.md section 3): the designators (the free
100 block: U101, Q101 to Q104, D101, R101 to R109, C101 to C104, TP101 to TP104), the net names, J_SMB's pin assignment, C104
1 uF 50 V at the sense pair (TI SNVS452G section 10 and 11.1.1), PGD left open, the four test points for E-12.

What it changes in v2/ecad/tools/gen_sch_p.py, and nothing else:
  1. PACK_P's declaration: the breaker's output (loads Q101 and Q102, switch U101 on BRK_UVLO); BRK_VIN and BRK_SNS declared as
     segments of PACK_P (BRK_VIN switched by the gauge as PACK_P was);
  2. R6 and R7 on BRK_VIN;
  3. Q2's source and R19 on BRK_VIN;
  4. the breaker and the enable loop drawn before the pack leads W_P and W_N, with their node declarations;
  5. J_SMB a 1x7 with the loop on pins 5 and 7 and the return on pin 6 (no order code: the 7-way code is Layer 6's, L8P-06);
  6. VCC_F fed from BRK_VIN;
  7. one schematic section for the new parts.
Order (L8P-BREAKER.md section 4): released together with apply_gen_sch_e_enable.py and apply_gen_sch_a_ptc.py (never alone:
J_SMB's two ends and the dock's two ends must change together), with l6r2's two board P drafts in either order.

Usage:  apply_gen_sch_p_breaker.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; no added designator or net may
exist in the target; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator or
net is in use, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_p_breaker"
ADDS = ("U101", "Q101", "Q102", "Q103", "Q104", "D101", "R101", "R102", "R103", "R104", "R105", "R106", "R107", "R108", "R109",
        "C101", "C102", "C103", "C104", "TP101", "TP102", "TP103", "TP104")
NETS = ("BRK_VIN", "BRK_SNS", "BRK_GATE", "BRK_TMR", "BRK_PWR", "BRK_UVLO", "BRK_G2", "BRK_DIS", "DOCK_EN_OUT", "DOCK_EN_RET")

_OLD_RAIL = (
    '_intent.rail("PACK_P", 14.4, 10.0, 18.0, "W_P", loads={"Q2": 10.0}, switch="U1", enable_net="DSG_R", v_work=16.8, converted=False,   # the GAUGE\'s own pin; R18, 5.1k, sits between it and the FET gate DSG_G\n'
    '             note="the pack lead. THE SWITCH IS THE GAUGE: Q2 is the discharge FET and the BQ4050 drives its gate on DSG_G, so the pack terminal is live only while the gauge allows it, which is the first stage of the energy chain")\n')
_NEW_RAIL = (
    '# RECORD l8p (MESHSAT-1357, 4 October 2026; record l9stk 15.4, C-1 and C-1b, IF-5, IF-6): THE PACK TERMINAL IS THE BREAKER\'S\n'
    '# OUTPUT. Q2\'s source is the net BRK_VIN, the LM5069-2 breaker U101 (drawn below, before the pack leads) passes BRK_VIN through\n'
    '# its sense pair to BRK_SNS and through Q101 and Q102 to PACK_P, so the terminal is live only while the gauge holds Q2 on AND\n'
    '# the dock\'s enable loop is closed. BRK_VIN and BRK_SNS are segments of the one pack path whose power PACK_P counts.\n'
    '_intent.rail("PACK_P", 14.4, 10.0, 18.0, "W_P", loads={"Q101": 5.0, "Q102": 5.0}, switch="U101", enable_net="BRK_UVLO", v_work=16.8, converted=False,\n'
    '             note="the pack lead, the breaker\'s output (record l8p; l9stk 15.4 C-1, IF-6): U101 (LM5069-2) drives Q101 and Q102 '
    '(CSD18510Q5B, an even split when enhanced, SLVA673A 2.4) from BRK_SNS; its UVLO is held low unless the dock\'s enable loop '
    'is closed (C-1b), so the terminal is live only while the gauge holds Q2 on and the kit is docked (IF-5)")\n'
    '_intent.rail("BRK_VIN", 14.4, 10.0, 18.0, "Q2", loads={"R101": 6.52, "R102": 3.48}, switch="U1", enable_net="DSG_R", series_of="PACK_P",\n'
    '             v_work=16.8, v_max=29.2, converted=False,\n'
    '             note="Q2\'s source, the breaker\'s input (record l8p; l9stk 15.4 C-1): the gauge drives Q2 on DSG_G through R18 as it '
    'drove the terminal before; the sense pair shares 65.2 and 34.8 percent (l9stk prot 3); D101 (SMCJ18A, VC 29.2 V at 51.4 A) '
    'clamps it to PACK_N; the gauge\'s PACK and VCC taps sit here (IF-6)")\n'
    '_intent.rail("BRK_SNS", 14.4, 10.0, 18.0, ["R101", "R102"], loads={"Q101": 5.0, "Q102": 5.0}, series_of="PACK_P", v_work=16.8,\n'
    '             converted=False, note="the breaker FETs\' drains, after the sense pair R101 and R102 (record l8p; l9stk 15.4 C-1)")\n')

_OLD_R6 = 'r("R6", "1k", "PACK_P", "PACK_F")'
_NEW_R6 = 'r("R6", "1k", "BRK_VIN", "PACK_F")'
_OLD_R7 = 'r("R7", "1k", "PACK_P", "VCC_F")'
_NEW_R7 = 'r("R7", "1k", "BRK_VIN", "VCC_F")'
_OLD_Q2 = 'pfet5("Q2", "CSD17570Q5B 30 V N-FET, discharge switch", "DSG_G", "SW", "PACK_P", "C529279")'
_NEW_Q2 = 'pfet5("Q2", "CSD17570Q5B 30 V N-FET, discharge switch", "DSG_G", "SW", "BRK_VIN", "C529279")'
_OLD_R19 = 'r("R19", "10M", "DSG_G", "PACK_P")'
_NEW_R19 = 'r("R19", "10M", "DSG_G", "BRK_VIN")'

_ANCHOR_WP = 'part("W_P", "Connector", "Conn_01x01_Pin", "pack lead + (12 AWG to the XT60 on E6 J_BATT pin 2)", "WIRE", {"1": "PACK_P"})\n'
_BREAKER = (
    '# =========================================================================================================================\n'
    '# RECORD l8p (MESHSAT-1357, 4 October 2026): W4DP-F2\'S FIRMWARE-INDEPENDENT ELEMENT, drawn from record l9stk section 15\n'
    '# (branch fnd/l9stk at 2c8b29fb, CONFIRMED AS CONDITIONAL). With Q1 and Q2 welded and no firmware, nothing on this board\n'
    '# opened the discharge path on current alone (l9stk 15.2). C-1 (15.4): the LM5069-2 circuit breaker U101 from BRK_VIN (Q2\'s\n'
    '# source) to PACK_P. The sense pair R101 4 mOhm and R102 7.5 mOhm in parallel, 2.6087 mOhm, 1 percent and at most 50 ppm/K\n'
    '# (current limit 18.32 to 23.93 A, breaker 30.21 to 50.59 A); Q101 and Q102 CSD18510Q5B, 40 V; RPWR R103 8.45 kOhm (32.52 W\n'
    '# nominal); the timer C101 10 nF (clearing at most 1.292 ms); the dv/dt capacitor C102 22 nF on the gate (a start is 0.659 A at\n'
    '# most); the input clamp D101 SMCJ18A. The clamp, the controller and its small parts return to PACK_N (IF-6), and OVLO is\n'
    '# tied there (15.4, the controller row). D1 stays on PACK_P and carries the lead\'s freewheel at turn-off (15.4, the clamps\n'
    '# row). Where an older comment above names PACK_P as Q2\'s source, read BRK_VIN.\n'
    '# C-1b (15.4, B-P1, conditions C1 and C2): THE MAKE-LAST ENABLE IS A LOOP. R106 10 kOhm from BRK_VIN onto J_SMB pin 7\n'
    '# (DOCK_EN_OUT); board E passes it to the dock, board A passes it through its thermal guard RT1 (a PRF15BB103 on the battery\n'
    '# FETs\' copper, 15.5) and back; it returns on J_SMB pin 5 (DOCK_EN_RET) into R107 22 kOhm on the first inverter Q103\'s gate.\n'
    '# Q103 holds the second inverter Q104\'s gate (R108 and R109, 1 MOhm each: half of BRK_VIN, l9stk_protection.py\'s R_G) low;\n'
    '# Q104, when on, discharges UVLO through R105 150 ohm. UVLO charges from BRK_VIN through R104 200 kOhm into C103 3.3 uF 50 V:\n'
    '# the gate rises 0.110 to 0.593 s after the enable mates and a dv/dt start follows; the loop opening turns the gate off in\n'
    '# 1.51 ms; an open or a short to ground on either conductor holds the breaker off. J_SMB pin 6 is the ground contact between\n'
    '# the two conductors (C2). The order of mating (every power pin before the enable, 1 mm short) is Layer 7\'s (C1).\n'
    '# SESSION choices of record l8p (L8P-BREAKER.md section 3): the designators (the free 100 block), the net names, J_SMB\'s pin\n'
    '# assignment, C104 1 uF 50 V at the sense pair (TI SNVS452G section 10, "a 1-uF ceramic capacitor to ground close to the drain\n'
    '# of the hot swap MOSFET", and 11.1.1, the bypass "close to Rsns instead of the VIN pin"), PGD left open (IF-1\'s PGD option\n'
    '# would need a conductor to board A: L4-E11\'s), TP101 to TP104 for E-12 (BRK_VIN, the hold on BRK_UVLO, both loop conductors).\n'
    '# IF-2 for the layout (gen_pcb_p3.py): each breaker FET\'s installed RthJA at most 52.5 C/W (1 in2 of 2 oz each gives the\n'
    '# sheet\'s 50), U101 beside the sense pair with Kelvin taps (E-9), C104 at the sense pair. Nothing here is built or measured.\n'
    'ic("U101", 10, "LM5069MM-2 circuit breaker on the pack path (record l8p; l9stk 15.4 C-1): 1 SENSE, 2 VIN, 3 UVLO, 4 OVLO, 5 GND, 6 TIMER, 7 PWR, 8 PGD, 9 OUT, 10 GATE",\n'
    '   "Package_SO:VSSOP-10_3x3mm_P0.5mm", {"1": "BRK_SNS", "2": "BRK_VIN", "3": "BRK_UVLO", "4": "PACK_N", "5": "PACK_N", "6": "BRK_TMR",\n'
    '   "7": "BRK_PWR", "8": "NC", "9": "PACK_P", "10": "BRK_GATE"}, "C111822")\n'
    'r("R101", "4m 1% 2512 (breaker sense, at most 50 ppm/K; 2 W at the band\'s temperature, E-6)", "BRK_VIN", "BRK_SNS", "RS2512")\n'
    'r("R102", "7.5m 1% 2512 (breaker sense, at most 50 ppm/K; 2 W at the band\'s temperature, E-6)", "BRK_VIN", "BRK_SNS", "RS2512")\n'
    'pfet5("Q101", "CSD18510Q5B 40 V N-FET, breaker pass (one of two in parallel; IF-2: RthJA at most 52.5 C/W installed)", "BRK_GATE", "BRK_SNS", "PACK_P", "C2876544")\n'
    'pfet5("Q102", "CSD18510Q5B 40 V N-FET, breaker pass (one of two in parallel; IF-2: RthJA at most 52.5 C/W installed)", "BRK_GATE", "BRK_SNS", "PACK_P", "C2876544")\n'
    'r("R103", "8.45k 1% (PWR: the power limit)", "BRK_PWR", "PACK_N"); c("C101", "10n 50V X7R (TIMER)", "BRK_TMR", "PACK_N")\n'
    'c("C102", "22n 50V X7R (GATE: the dv/dt start)", "BRK_GATE", "PACK_N")\n'
    'c("C104", "1u 50V X7R 1206 (VIN bypass at the sense pair)", "BRK_VIN", "PACK_N", "C1206")\n'
    'if _tvs:\n'
    '    _tvs("D101", "SMCJ18A (breaker input clamp, unidirectional: cathode on BRK_VIN)", "BRK_VIN", "PACK_N", "Diode_SMD:D_SMC", "C374030")\n'
    'else:\n'
    '    part("D101", "Device", "D_Zener", "SMCJ18A (breaker input clamp, unidirectional: cathode on BRK_VIN)", "Diode_SMD:D_SMC", {"1": "BRK_VIN", "2": "PACK_N"}, "C374030")\n'
    'r("R106", "10k", "BRK_VIN", "DOCK_EN_OUT"); r("R107", "22k", "DOCK_EN_RET", "PACK_N")\n'
    'nfet("Q103", "DOCK_EN_RET", "PACK_N", "BRK_G2", "2N7002 60 V N-FET: the enable loop\'s first inverter, on while the loop is closed")\n'
    'r("R108", "1M", "BRK_VIN", "BRK_G2"); r("R109", "1M", "BRK_G2", "PACK_N")\n'
    'nfet("Q104", "BRK_G2", "PACK_N", "BRK_DIS", "2N7002 60 V N-FET: the enable loop\'s second inverter, discharges UVLO while the loop is open")\n'
    'r("R105", "150R", "BRK_DIS", "BRK_UVLO"); r("R104", "200k 1%", "BRK_VIN", "BRK_UVLO")\n'
    'c("C103", "3.3u 50V X7R 1206 (UVLO: the RC hold)", "BRK_UVLO", "PACK_N", "C1206")\n'
    'for _i8, _n8 in enumerate(("BRK_VIN", "BRK_UVLO", "DOCK_EN_OUT", "DOCK_EN_RET"), 101):\n'
    '    part("TP%d" % _i8, "Connector", "TestPoint", _n8, "TP", {"1": _n8})   # E-12: the input, the hold\'s release, each loop conductor to ground in turn\n'
    '_intent.node("BRK_GATE", 29.4, "the breaker FETs\' gate: OUT (PACK_P, at most the pack\'s 16.8 V) plus the gate drive, at most 12.6 V above OUT "\n'
    '             "(VGATE, SNVS452G 7.5; record l9stk 15.4, the FETs row)", rides_on="PACK_P", bias_v=12.6)\n'
    '_intent.node("BRK_UVLO", 29.2, "the breaker\'s UVLO, charged from BRK_VIN through R104 200 kOhm: at most BRK_VIN, the pack\'s 16.8 V in "\n'
    '             "service and the input clamp D101\'s 29.2 V (SMCJ18A, VC at 51.4 A; record l9stk 15.4, the clamps row)", v_work=16.8)\n'
    '_intent.node("BRK_G2", 14.6, "the second inverter\'s gate, half of BRK_VIN through R108 and R109 (1 MOhm each): at most half the "\n'
    '             "clamp\'s 29.2 V (record l9stk 15.4, the inverters\' bounds)")\n'
    '_intent.node("DOCK_EN_OUT", 29.2, "the enable loop leaving board P, BRK_VIN through R106 10 kOhm and BRK_VIN itself with the loop open: "\n'
    '             "at most the input clamp\'s 29.2 V (record l9stk 15.4)", v_work=16.8)\n'
    '_intent.node("DOCK_EN_RET", 17.4, "the enable loop\'s return, the first inverter\'s gate over R107 22 kOhm: at most 17.4 V under the "\n'
    '             "clamp\'s 29.2 V with RT1 at its least 5 kOhm (record l9stk 15.4, the inverters\' bounds)")\n'
    '# =========================================================================================================================\n')

_OLD_JSMB = (
    'part("J_SMB", "Connector_Generic", "Conn_01x04", "SMBus lead to E6 J_SMB (JST-XH 1x4): SMBC SMBD GND(pack side of the shunt) PRES", "XH4", '
    '{"1": "SMBC", "2": "SMBD", "3": "PACK_N", "4": "PRES_J"}, "C144395")   # R8P-02, round 8 (26 September 2026), owner condition 1: the line '
    'carried no code and lcsc_fill.py:158\'s MAP filled C594232, JST B4B-XH-A-G (gold contacts per LCSC), which JST\'s XH catalogue '
    '(v2/vendor/connectors/jst-xh-catalogue.pdf, sha256 9426b136, page 5, Header "Top entry type" table) does not list '
    '(v2/vendor/SOURCES.yaml jlc_retake_45bde541). C144395 is B4B-XH-A(LF)(SN), the table\'s own 4-circuit header without boss '
    '("Post: Brass, copper-undercoated, tin-plated"; note 1 "This product displays (LF)(SN) on a label"), JLC API 2026-09-26T21:09Z: JST, '
    'stock 108,967. Pinned here so no fill decides it; same land, pins and nets\n')
_NEW_JSMB = (
    '# RECORD l8p (MESHSAT-1357, 4 October 2026; l9stk 15.4 C-1b and condition C2): J_SMB CARRIES THE DOCK ENABLE LOOP. Pins 1 to 4\n'
    '# keep the round 4 order (S-05, A07); pin 5 is the loop\'s return DOCK_EN_RET, pin 6 the ground contact between the two loop\n'
    '# conductors (the pack side of the shunt, as pin 3), pin 7 the loop\'s outgoing DOCK_EN_OUT at the end of the row. The part is\n'
    '# the 7-circuit member of the same JST XH header row (B7B-XH-A, the held catalogue\'s page 5 table, v2/vendor/connectors/\n'
    '# jst-xh-catalogue.pdf); R8P-02\'s 4-way code C144395 is withdrawn with the 4-way header, and the 7-way code is Layer 6\'s to pin\n'
    '# here as R8P-02 pinned the 4-way one (L8P-06), so no fill decides it.\n'
    'part("J_SMB", "Connector_Generic", "Conn_01x07", "SMBus and dock enable lead to E6 J_SMB (JST-XH 1x7, B7B-XH-A): 1 SMBC, 2 SMBD, 3 GND (pack side of the shunt), 4 PRES, 5 DOCK_EN_RET, 6 GND, 7 DOCK_EN_OUT",\n'
    '     "Connector_JST:JST_XH_B7B-XH-A_1x07_P2.50mm_Vertical",\n'
    '     {"1": "SMBC", "2": "SMBD", "3": "PACK_N", "4": "PRES_J", "5": "DOCK_EN_RET", "6": "PACK_N", "7": "DOCK_EN_OUT"})\n')

_OLD_VCCF = '_intent.rail("VCC_F", 14.4, 0.0, 0.00034, "R7", loads={"U1": 0.00034}, fed_from="PACK_P", converted=False, v_work=16.8,\n'
_NEW_VCCF = ('# record l8p: R7 follows Q2\'s source to BRK_VIN (l9stk IF-6), so VCC_F is fed from BRK_VIN, the breaker\'s input\n'
             '_intent.rail("VCC_F", 14.4, 0.0, 0.00034, "R7", loads={"U1": 0.00034}, fed_from="BRK_VIN", converted=False, v_work=16.8,\n')

_ANCHOR_SEC = 'placed_refs = {r_ for _, rs in SECTIONS for r_ in rs}\n'
_SEC = ('SECTIONS.append(("PACK BREAKER LM5069-2 (W4DP-F2), ITS FETS, SENSE PAIR AND CLAMP; THE DOCK ENABLE LOOP, ITS INVERTERS AND THE RC HOLD (RECORD l8p)",\n'
        '                 ["U101", "R101", "R102", "Q101", "Q102", "R103", "C101", "C102", "C104", "D101", "R106", "R107", "Q103", "R108", "R109",\n'
        '                  "Q104", "R105", "R104", "C103", "TP101", "TP102", "TP103", "TP104"]))\n')

EDITS = [
    (_OLD_RAIL, _NEW_RAIL),
    (_OLD_R6, _NEW_R6),
    (_OLD_R7, _NEW_R7),
    (_OLD_Q2, _NEW_Q2),
    (_OLD_R19, _NEW_R19),
    (_ANCHOR_WP, _BREAKER + _ANCHOR_WP),
    (_OLD_JSMB, _NEW_JSMB),
    (_OLD_VCCF, _NEW_VCCF),
    (_ANCHOR_SEC, _SEC + _ANCHOR_SEC),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def code_only(text):
    """The generator without its comments (a designator or net named in prose is not in use)."""
    return "\n".join(l.split("#")[0] for l in text.splitlines())


def patched(text):
    code = code_only(text)
    for ref in ADDS:
        if re.search(r'"%s"' % re.escape(ref), code):
            refuse("designator %s is already in use in the target" % ref)
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), code):
            refuse("net %s already exists in the target" % net)
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once: %r" % (new.count(old), old[:70]))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: record l8p drafts this change for board P's generator owner and never applies it. Writing the repository's own
# gen_sch_p.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_p.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; l8p's drafts wait on an accepted check")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE.md names no single check")
    path = os.path.join(REPO, rec[0])
    if ".." in rec[0].split("/") or not os.path.isfile(path):
        refuse("NOT RELEASED: check %s is not in this tree" % rec[0])
    if open(path, encoding="utf-8").readline().rstrip("\n") != "accepted: yes":
        refuse("NOT RELEASED: check %s is not accepted" % rec[0])


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    if write and os.path.realpath(target) == os.path.realpath(TREE_GEN):
        released()
    text = open(target, encoding="utf-8").read()
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_p.py", "b/gen_sch_p.py", n=0))
    if not write:
        print("%s: CHECK OK, %d edit(s), nothing written" % (NAME, len(EDITS)))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep) != 1 for _o, rep in EDITS):
        refuse("the written file does not read back as the patched text")
    ast.parse(back)
    print("%s: WRITTEN, %d edit(s)" % (NAME, len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
