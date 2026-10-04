#!/usr/bin/env python3
"""apply_gen_sch_a_dd7.py: DRAFT for board A's generator owner (task L4-E11, MESHSAT-1357; round 9, 4 October 2026, record l9stk's DD-7;
round 10, 4 October 2026, record l8p's round 3: board P's reverse-charge detector of route R1 and its findings L8P-F04 and L8P-F05).
NOT APPLIED to the tree by L4-E11; its author ran it only on scratch copies (the tests write scratch copies).

Why (L4E11-SOURCE-ONLY-AND-ENTRY.md sections 19h and 20, l4e11_power.out sections 19h and 20): board P's breaker is the latch-off
LM5069-1 (record l9stk 15.4b). Round 9 drew the input-return reset (Q44 to Q46) and a hardware charge inhibit that set only while
CELL+ read dead. Record l8p's round 3 (branch fnd/l8p2 at a46597e2, its section 12) draws route R1 on board P: a detector that holds
the enable loop's return DOCK_EN_RET under 0.06 V while a charge over 0.368 to 1.213 A passes the off breaker's body diodes, and asks
board A (12f, L8P-F04) to set its inhibit while DOCK_EN_RET is low and DOCK_EN_OUT is powered, whatever CELL+ reads, within 1 ms,
to hold it at least 1.0 s after the return rises, then to release it on CELL+ alive, and to load DOCK_EN_RET with 1 MOhm or more.
Round 9's sense of the loop (Q47 on half of DOCK_EN_OUT) read 1.26 and 1.75 V with the return held, under a 2N7002's 2.5 V; and its
dead point (1.98 V on CELL+) sat under the 2.80 V the LM5069's internal 1 MOhm holds CELL+ at with the breaker off (L8P-F05). Round
10 redraws board A's side:
  U48     TPS37A010122DSKR (C3685740, U34's and U46's part) on VBAT. Channel 1 (OV) reads DOCK_EN_RET on SENSE1 directly: RESET1
          releases (the return read as held) under 0.7756 V at least and asserts over 0.808 V at most. Channel 2 (UV) reads
          DOCK_EN_OUT over R109 562k / R144 422k (0.1 %): RESET2 (DD7_LP) releases (the loop powered) over 1.982 V at most and
          asserts under 1.79 V at least. RESET1 is DD7_T, pulled up from DD7_LP through R63: DD7_T is high exactly while the
          return reads held AND the loop reads powered (the trigger).
  Q50,Q51 the arm: Q50 (2N7002) on DD7_T pulls Q51's (AO3401A) gate through R249 (Q51's VGS -VBAT/3, R69 from VBAT); Q51
          charges the hold node DD7_H from VBAT through R84 56R and D26 (1N4148W); R79 10k bleeds Q51's off leakage.
  C241,R85 the hold: 1 uF 100 V X7R and 1 MOhm on DD7_H.
  U47     TPS37A010122DSKR on VBAT. Channel 1 (OV) reads DD7_H: RESET1 (DD7_N) asserts after CTS1's delay (C248 3.9 nF C0G:
          0.382 to 0.709 ms, Equations 5 and 6) and holds while DD7_H is over 0.79 V: at least 1.0 s after the trigger ends. The
          set delay makes the trigger last until the arm is complete, because board P's pull holds while the charge flows.
          Channel 2 (UV) reads CELL+ over R107 464k / R108 100k, the divider's foot DD7_REF switched to DD7_N by Q52 only
          while the loop is powered and an inhibit is asked; otherwise R185 lifts it and the channel reads alive. So a dead
          CELL+ never SETS the inhibit; it keeps an inhibit that is set (the release on CELL+ alive).
  Q47,Q49 the inhibit: Q47 (2N7002, gate DD7_LP) passes DD7_N to SYS_INH_D; Q49 (AO3401A) then holds CH_BATDRV, the battery
          FETs' gates, at VBAT (R82 / R83 as round 9).
  Q48,R250 the bleeder: Q48 (2N7002, gate DD7_LP) loads CELL+ with R250 4.7k into DD7_N while the inhibit holds, so the
          LM5069's internal 1 MOhm (its tolerance not printed) and the battery FETs' off leakage cannot lift CELL+ to the
          alive threshold: CELL+ reads alive only when the breaker itself drives it.
  Q46     its gate moves from CELL+/2 (round 9's DD7_ALIVE) to DD7_N: the input-return pulse is blocked while VBAT is up and
          no inhibit is asked (the kit running on its pack), allowed while VBAT is down (the dark kit) or an inhibit holds.
  R233,D27 DD7_VC, the gates' supply: VBAT through 100k, clamped by a BZT52C12 under 12.7 V; R53 DD7_LP's pull-up, R9 DD7_N's.
  TP1,TP2 DD7_H and DD7_N, for E11-45.
Kept from round 9: Q44, R106, D25 and Q45 (the input-return reset), Q49, R82 and R83. Removed: the nets DD7_ALIVE and SYS_INH_G
(Q47 and Q48 are redrawn; R107, R108, R109 and R144 keep their designators with new values and nets).
VDD of U47 and U48: C238 (the charger draft's 1 uF at U42's IN, U46's bypass) with both placed beside it, class D entries.
Designators: U47, U48, Q50 to Q52, D26, D27, TP1 and TP2 are above every board A draft's; R9, R53, R63, R69, R79, R84, R85, R185,
R233 and C241 are gaps no draft composed in L4-E9's order uses; R249, R250 and C248 lie above the main-based order's highest, so
d8dec31's mainpb, which takes the next free R and C at apply time and runs LAST, takes the next ones after them (R251 and C249 on
that order; in set 29's order l8r2's slotlm already sets them higher).

ORDER: AFTER record l8p's apply_gen_sch_a_ptc.py (it refuses a target without DOCK_EN_RET) and this record's charger draft (CH_BATDRV,
the three battery FETs, C238); before d8dec31's mainpb; released with l8p's three drafts and this record's charger draft.

Usage:  apply_gen_sch_a_dd7.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator or net is in
use, record l8p's loop is not drawn, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_dd7"
ADDS = ("Q44", "Q45", "Q46", "R106", "D25", "Q47", "Q48", "Q49", "R82", "R83", "R107", "R108", "R109", "R144",
        "U47", "U48", "Q50", "Q51", "Q52", "D26", "D27", "R9", "R53", "R63", "R69", "R79", "R84", "R85", "R185", "R233", "R249", "R250",
        "C241", "C248", "TP1", "TP2")
NETS = ("DD7_G", "DD7_VC", "DD7_OS", "DD7_LP", "DD7_T", "DD7_AD", "DD7_AG", "DD7_K", "DD7_KA", "DD7_H", "DD7_CTS", "DD7_CS", "DD7_REF",
        "DD7_N", "DD7_BL", "SYS_INH_D", "SYS_INH_P")
REQUIRES = ('part("RT1", "Device", "Thermistor_PTC"', '_intent.node("DOCK_EN_RET", ', '"4": "FE_RUN", "5": "FE_RUN"',
            'nfet(_qb, "BUK6Y10-30PX 30 V P-FET', '"21": "CH_BATDRV", "22": "VBAT"', 'c("C238", "1u 50V X7R", "VBAT", "GND")')

_ANCHOR_MAIN = ("# --- main power control LTC2954-1 (ltc2954.pdf): the panel MAIN button, EN to every converter's enable (RAIL_EN), "
                "INT = shutdown request, KILL from the panel controller through Q1\n")
_N = 'part(%r, "Transistor_FET", "2N7002", %r, "SOT23", {"1": %r, "2": %r, "3": %r}, "C8545")\n'
_P = 'part(%r, "Transistor_FET", "AO3401A", %r, "SOT23", {"1": %r, "2": %r, "3": %r}, "C15127")\n'
_DD7 = (
    '# L4-E11 ROUNDS 9 AND 10 (MESHSAT-1357, 4 October 2026; record l9stk 15.4b DD-7, record l8p 12 route R1 and its L8P-F04 and\n'
    '# L8P-F05): BOARD A\'S SIDE OF THE PACK BREAKER\'S LATCH. Board P\'s breaker is the latch-off LM5069-1; route R1 on board P holds\n'
    '# the enable loop\'s return DOCK_EN_RET under 0.06 V while a charge over 0.368 to 1.213 A passes the off breaker. Board A:\n'
    '# (1) THE INPUT-RETURN RESET (round 9): an input arriving while the kit is dark, or while an inhibit holds, pulls the return\n'
    '#     low through Q44 until U34 releases FE_RUN (Q45): at least 78.6 ms, so the latch resets and the breaker restarts.\n'
    '# (2) THE TRIGGER (round 10): U48 reads the return on SENSE1 (held under 0.7756 V, closed over 0.808 V) and DOCK_EN_OUT on\n'
    '#     SENSE2 over R109 / R144 (powered over 1.982 V at most); DD7_T is high only while both hold.\n'
    '# (3) THE HOLD: DD7_T arms DD7_H through Q50, Q51, R84 and D26; U47\'s channel 1 asserts DD7_N 0.382 to 0.709 ms after DD7_H\n'
    '#     passes 0.808 V (CTS1, C248) and keeps it until DD7_H has fallen through R85 under 0.79 V: at least 1.0 s after the\n'
    '#     trigger ends, so the inhibit covers the breaker\'s restart (0.948 s at most).\n'
    '# (4) THE RELEASE ON CELL+ ALIVE: while the loop is powered and DD7_N is low, Q52 grounds the foot of U47\'s CELL+ divider and\n'
    '#     Q48 loads CELL+ through R250, so a dead CELL+ keeps DD7_N low until the breaker drives CELL+ over 4.7 V; with no inhibit\n'
    '#     asked R185 lifts the foot and the channel reads alive (a dead CELL+ never sets the inhibit: a back-fed precharge passes).\n'
    '# (5) THE INHIBIT: Q47 (on while the loop is powered) passes DD7_N to SYS_INH_D, and Q49 holds the battery FETs\' gates at VBAT.\n'
    '# No firmware anywhere. Reach and margins: L4E11-SOURCE-ONLY-AND-ENTRY.md section 20 (round 10).\n'
    + _N % ("Q44", "2N7002: DD7_G high = the breaker's enable loop opened at board A (1 G, 2 S, 3 D)", "DD7_G", "GND", "DOCK_EN_RET")
    + 'r("R106", "1M", "VIN_RAW", "DD7_G", lcsc="C22935"); part("D25", "Device", "D_Zener", "BZT52C12-7-F zener, the input-return reset\'s gate clamp", "SOD123", {"1": "DD7_G", "2": "GND"}, "C124196")\n'
    + _N % ("Q45", "2N7002: FE_RUN high = the input-return pulse ended (1 G, 2 S, 3 D)", "FE_RUN", "GND", "DD7_G")
    + _N % ("Q46", "2N7002: DD7_N high (VBAT up, no inhibit asked) = no input-return pulse (1 G, 2 S, 3 D)", "DD7_N", "GND", "DD7_G")
    + 'r("R233", "100k", "VBAT", "DD7_VC", lcsc="C25803"); part("D27", "Device", "D_Zener", "BZT52C12-7-F zener, DD-7\'s gate supply under 12.7 V", "SOD123", {"1": "DD7_VC", "2": "GND"}, "C124196")\n'
    'ic("U48", 11, "TPS37A010122DSKR 65 V OV/UV supervisor: DD-7\'s loop reader, the return held and the loop powered", "WSON10", {\n'
    ' "1": "VBAT", "2": "DOCK_EN_RET", "3": "DD7_OS", "4": "DD7_T", "5": "DD7_LP", "6": "NC", "7": "NC", "8": "NC", "9": "NC", "10": "GND", "11": "GND"}, "C3685740")\n'
    'r("R109", "562k 0.1%", "DOCK_EN_OUT", "DD7_OS"); r("R144", "422k 0.1%", "DD7_OS", "GND")   # U48 SENSE2: the loop powered over 1.982 V at most\n'
    'r("R53", "100k", "DD7_VC", "DD7_LP", lcsc="C25803"); r("R63", "1M", "DD7_LP", "DD7_T", lcsc="C22935")   # DD7_T high = return held AND loop powered\n'
    + _N % ("Q50", "2N7002: DD7_T high = the hold armed (1 G, 2 S, 3 D)", "DD7_T", "GND", "DD7_AD")
    + 'r("R69", "100k 1%", "VBAT", "DD7_AG", lcsc="C25803"); r("R249", "200k 1%", "DD7_AG", "DD7_AD")   # Q51 VGS -VBAT/3\n'
    + _P % ("Q51", "AO3401A P-FET: the hold's arm from VBAT (1 G, 2 S, 3 D)", "DD7_AG", "VBAT", "DD7_K")
    + 'r("R79", "10k 1%", "DD7_K", "GND", lcsc="C25804"); r("R84", "56R 1%", "DD7_K", "DD7_KA", fp="RS")   # R79 bleeds Q51\'s off leakage; R84 sets the arm\'s current\n'
    'part("D26", "Device", "D", "1N4148W: the hold\'s arm diode (cathode on DD7_H)", "SOD123", {"1": "DD7_H", "2": "DD7_KA"}, "C81598")\n'
    'c("C241", "1u 100V 1210", "DD7_H", "GND", fp="C1210", lcsc="C382212"); r("R85", "1M", "DD7_H", "GND", lcsc="C22935")   # the hold: at least 1.0 s\n'
    'ic("U47", 11, "TPS37A010122DSKR 65 V OV/UV supervisor: DD-7\'s hold (channel 1) and the release on CELL+ alive (channel 2)", "WSON10", {\n'
    ' "1": "VBAT", "2": "DD7_H", "3": "DD7_CS", "4": "DD7_N", "5": "DD7_N", "6": "NC", "7": "DD7_CTS", "8": "NC", "9": "NC", "10": "GND", "11": "GND"}, "C3685740")\n'
    'c("C248", "3.9n 50V C0G", "DD7_CTS", "GND")   # U47 CTS1: the set delay, 0.382 to 0.709 ms (SNVSBJ1E Equations 5 and 6)\n'
    'r("R107", "464k 1%", "CELL+", "DD7_CS"); r("R108", "100k 1%", "DD7_CS", "DD7_REF", lcsc="C25803")   # U47 SENSE2: CELL+ alive over 4.70 V at most\n'
    + _N % ("Q52", "2N7002: the CELL+ reading's foot to DD7_N while the loop is powered (1 G, 2 S, 3 D)", "DD7_LP", "DD7_N", "DD7_REF")
    + 'r("R185", "1M", "DD7_VC", "DD7_REF", lcsc="C22935"); r("R9", "1M", "DD7_VC", "DD7_N", lcsc="C22935")\n'
    + _N % ("Q47", "2N7002: the loop powered = DD7_N reaches the charge inhibit (1 G, 2 S, 3 D)", "DD7_LP", "DD7_N", "SYS_INH_D")
    + 'r("R82", "100k 1%", "VBAT", "SYS_INH_P", lcsc="C25803"); r("R83", "200k 1%", "SYS_INH_P", "SYS_INH_D")   # Q49 VGS -VBAT/3\n'
    + _P % ("Q49", "AO3401A P-FET: the charge inhibit, the battery FETs' gates held at VBAT (1 G, 2 S, 3 D)", "SYS_INH_P", "VBAT", "CH_BATDRV")
    + _N % ("Q48", "2N7002: the CELL+ bleeder while the inhibit holds (1 G, 2 S, 3 D)", "DD7_LP", "DD7_N", "DD7_BL")
    + 'r("R250", "4.7k 1%", "CELL+", "DD7_BL", fp="RS")   # 3.6 mA at 16.8 V into DD7_N while the inhibit holds\n'
    'tp("TP1", "DD7_H"); tp("TP2", "DD7_N")\n'
    '_r10 = "L4-E11 rounds 9 and 10 (DD-7, record l8p\'s L8P-F04 and L8P-F05): "\n'
    '_intent.node("DD7_G", 12.7, _r10 + "Q44\'s gate, VIN_RAW through R106 1M clamped by D25 (BZT52C12, 11.4 to 12.7 V, DS18004)")\n'
    '_intent.node("DD7_VC", 12.7, _r10 + "the gates\' supply, VBAT through R233 100k clamped by D27 (BZT52C12, 12.7 V at most)")\n'
    '_intent.node("DD7_OS", 12.6, _r10 + "U48 SENSE2, DOCK_EN_OUT over R109 / R144: 0.4289 of it, 12.6 V at the loop\'s 29.2 V clamp")\n'
    '_intent.node("DD7_LP", 12.7, _r10 + "U48 RESET2 (the loop powered), pulled up from DD7_VC by R53")\n'
    '_intent.node("DD7_T", 12.7, _r10 + "U48 RESET1 (the trigger), pulled up from DD7_LP by R63")\n'
    '_intent.node("DD7_AD", 29.2, _r10 + "Q50\'s drain, VBAT through R69 and R249 while Q50 is off: at most VBAT\'s 29.2 V clamp")\n'
    '_intent.node("DD7_AG", 29.2, _r10 + "Q51\'s gate, VBAT through R69; two thirds of VBAT while Q50 holds R249 low")\n'
    '_intent.node("DD7_K", 29.2, _r10 + "Q51\'s drain, at most VBAT\'s 29.2 V clamp while the arm runs")\n'
    '_intent.node("DD7_KA", 29.2, _r10 + "D26\'s anode behind R84, at most VBAT\'s 29.2 V clamp")\n'
    '_intent.node("DD7_H", 29.2, _r10 + "the hold node: C241, R85, U47 SENSE1 (65 V graded); at most VBAT\'s 29.2 V clamp less D26")\n'
    '_intent.node("DD7_CTS", 5.5, _r10 + "U47 CTS1\'s delay capacitor C248: SNVSBJ1E recommends 0 to 5.5 V on the pin (6 V absolute)")\n'
    '_intent.node("DD7_CS", 29.2, _r10 + "U47 SENSE2 (65 V graded), CELL+ over R107 / R108: at most CELL+ at the 29.2 V clamp")\n'
    '_intent.node("DD7_REF", 29.2, _r10 + "the CELL+ divider\'s foot: Q52\'s drain and R185 from DD7_VC; at most CELL+ at the 29.2 V clamp")\n'
    '_intent.node("DD7_N", 12.7, _r10 + "U47 RESET1 and RESET2 (65 V graded), the inhibit asked when low; R9 from DD7_VC")\n'
    '_intent.node("DD7_BL", 29.2, _r10 + "Q48\'s drain, CELL+ through R250: at most CELL+ at the 29.2 V clamp")\n'
    '_intent.node("SYS_INH_D", 29.2, _r10 + "Q47\'s drain, VBAT through R82 and R83 while Q47 is off: at most VBAT\'s 29.2 V clamp")\n'
    '_intent.node("SYS_INH_P", 29.2, _r10 + "Q49\'s gate, VBAT through R82; two thirds of VBAT while Q47 holds R83 low")\n'
    '_intent.bypass("C238", "U47", "1", cls="D", basis="TI SNVSBJ1E (TPS37A) pin table: VDD \'Input Supply Voltage: Bypass with a 0.1 uF capacitor to GND\'; "\n'
    '               "C238, 1 uF X7R on VBAT at U42\'s IN, serves it with U47 placed beside it (L4-E11 round 10)")\n'
    '_intent.bypass("C238", "U48", "1", cls="D", basis="TI SNVSBJ1E (TPS37A) pin table: VDD \'Input Supply Voltage: Bypass with a 0.1 uF capacitor to GND\'; "\n'
    '               "C238, 1 uF X7R on VBAT at U42\'s IN, serves it with U48 placed beside it (L4-E11 round 10)")\n')

_ANCHOR_LISTED = "_listed = {r for _, refs in SECTIONS for r in refs}\n"
_SEC = ('SECTIONS.append(("THE PACK BREAKER\'S LATCH ON BOARD A (DD-7, L4-E11 ROUNDS 9 AND 10): THE INPUT-RETURN RESET, THE LOOP READER U48, '
        'THE HOLD AND THE RELEASE U47, THE CHARGE INHIBIT Q49", '
        '["Q44", "R106", "D25", "Q45", "Q46", "R233", "D27", "U48", "R109", "R144", "R53", "R63", "Q50", "R69", "R249", "Q51", "R79", "R84", "D26", '
        '"C241", "R85", "U47", "C248", "R107", "R108", "Q52", "R185", "R9", "Q47", "R82", "R83", "Q49", "Q48", "R250", "TP1", "TP2"]))   # L4-E11 rounds 9 and 10\n')

EDITS = [
    (_ANCHOR_MAIN, _DD7 + _ANCHOR_MAIN),
    (_ANCHOR_LISTED, _SEC + _ANCHOR_LISTED),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def code_only(text):
    return "\n".join(l.split("#")[0] for l in text.splitlines())


def patched(text):
    code = code_only(text)
    for req in REQUIRES:
        if req not in text:
            refuse("record l8p's enable loop, U34's FE_RUN or this record's charger is not drawn in the target (%r missing): apply l8p's PTC draft "
                   "and the charger draft first" % req[:40])
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


# NOT RELEASED: task L4-E11 drafts this change for board A's generator owner and never applies it. Writing the repository's own
# gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of L4-E11 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; L4-E11's values wait on an accepted check")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_a.py", "b/gen_sch_a.py", n=0))
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
