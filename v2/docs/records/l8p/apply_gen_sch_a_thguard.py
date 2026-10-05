#!/usr/bin/env python3
"""apply_gen_sch_a_thguard.py: DRAFT for board A's generator owner (Layer 8 record l8p round 8, MESHSAT-1357, 5 October 2026). NOT
APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).

Why (findings L8P-F07 and L8P-F08, OPEN; case row C-PROT rev 1): the thermal guard the board A draft apply_gen_sch_a_ptc.py draws,
RT1, a PRF15BB103 chip PTC in the pack breaker's make-last enable loop, has no printed no-trip side (Murata prints 100 kOhm only
over 110 C and 4.7 MOhm at 130 +-3 C; the 18 A service reads 118.0 C: L8P-F07, record l8p 12j). Record l9stk's guard round
(branch fnd/l9stk2; round 4 at 43da41ca selected G2, a factory-preset temperature switch; record l8p's round 7 check found its
AO3400A shunt breaking L4-E11 20c's window, L8P-F08; round 5 at bb6d2c8f re-selected C4, SESSION, unchecked) is drawn here as
round 5 states it (its page 15.9 and l9stk_guard.out section 6, copied into inputs/ at bb6d2c8f):
  R260, R261  two 7.5 kOhm 1 % in series from DOCK_EN_OUT to DOCK_EN_RET in RT1's place (THG_MID between them): the loop's
              fixed element; a short across either leaves 7.5 kOhm, with which the guard still trips and holds on its own supply;
  U60         TI LM26LV preset at 130 C (LM26LVQISDX-130/NOPB; SNIS144G: no trip under 127.8 C and tripped from 132.2 C at VDD 5 V,
              hysteresis 4.5 to 5.5 C, 16 uA, outputs enabled 2.3 ms after VDD passes 1.3 V), its thermal pad and GND on the
              board's ground at an island on the battery FETs' pour (SNIS144G p.4: the pad may float, "for improved noise immunity
              ... must be connected to the circuit GND node"); its push-pull OVERTEMP (pin 5) used, the open drain (pin 3) left
              open; TRIP_TEST (pin 1) on a test point only (it may be left open: an internal pull-down);
  C263        100 nF X8R at U60's VDD (SNIS144G 9 p.25; X8R because the island may pass X7R's 125 C at the trip);
  U61         TI TPS70950DBVR (5.0 V, 2.7 to 30 V in, 32 V absolute; SBVS186H) from DOCK_EN_OUT, so the guard is powered whenever
              the pack is docked, the kit dark or not; EN left open (its 300 nA pull-up enables it; TI: never tie EN to IN, its
              6.5 V clamp); C261 1 uF 50 V at its input (8.1.1 and 8.2.2), C262 4.7 uF 16 V at its output (an effective 1.5 uF or
              more at 5 V and at most 47 uF, ESR under 0.2 ohm: 8.1.1);
  Q60         the kit's 2N7002 (C8545, Q44's and Q107's part) from DOCK_EN_RET to ground, its gate through R262 47 kOhm from
              OVERTEMP with C260 1 uF and R263 1 MOhm to ground (record l9stk's sizing: the gate under 1 V through the 3.8 ms in
              which OVERTEMP is not printed, over 2.5 V within 36 ms of a trip);
  TP60..TP63  TRIP_TEST, VTEMP, the pair's midpoint and U60's VDD, for the commissioning check E-13b (record l8p 12m).
RT1 leaves the generator (the designator is retired, not reused). The intent declares the six new nets as nodes and the three
capacitors' pins with their classes (decision 42). Thermal placement (a LAYOUT and PHYSICAL condition, E-13; record l8p 12m):
U60 on the battery FETs' pour's centroid; U61, Q60 and the gate network off the pour (U61 is specified to TJ 125 C; Q60's off
leakage is counted at 86.25 C, free to 98.7 C); the gradient from each FET's mounting base to U60's die is read by E-13.

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else: the block apply_gen_sch_a_ptc.py inserted (its comment, the
J_DOCK post-edit, RT1's call and the loop's two intent nodes; the old text asserted once, word for word) becomes the guard's
block (the J_DOCK post-edit unchanged but for its description, which names the pair); the schematic section RT1's draft
appended becomes the guard's.

ORDER: AFTER record l8p's apply_gen_sch_a_ptc.py (whose block it replaces) and AFTER task L4-E11's apply_gen_sch_a_dd7.py, which
refuses a target without RT1's call (its REQUIRES); BEFORE d8dec31's mainpb, the next-free taker that runs last (it then takes R264
and C264 on this tree's order). Released with the board P and board E drafts of record l8p, never alone.
SESSION choices (record l8p 12m, each with its reason and reversal there): the designators (above every board A draft's: U60, U61,
Q60, R260 to R263, C260 to C263, TP60 to TP63; record l8r2's 5xx block untouched), the capacitors' values and grades, the test
point on U60's VDD (it finds a shorted regulator at E-13b), the 2 x 2 mm WSON-6 land as a stand-in carrying U60's seven pads (TI's
NGF0006A is 2.20 x 2.50 mm: the land is Layer 6's), the gate network's 1 % resistors.

Usage:  apply_gen_sch_a_thguard.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, RT1's block is absent, the change is already
applied, a designator or net is in use, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_thguard"
# the parts this draft draws: (designator, value) as the generator call writes it; l8p_c4.py reads the values from here
PAIR = (("R260", "7.5k 1%"), ("R261", "7.5k 1%"))
SWITCH = ("U60", "LM26LVQISDX-130/NOPB")
REG = ("U61", "TPS70950DBVR")
SHUNT = ("Q60", "2N7002")
GATE = (("R262", "47k 1%"), ("C260", "1u 16V X7R"), ("R263", "1M 1%"))
CAPS = (("C261", "1u 50V X7R"), ("C262", "4.7u 16V X7R"), ("C263", "100n 50V X8R"))
TPS = (("TP60", "THG_TT"), ("TP61", "THG_VT"), ("TP62", "THG_MID"), ("TP63", "THG_VDD"))
ADDS = tuple(r for r, _v in PAIR) + (SWITCH[0], REG[0], SHUNT[0]) + tuple(r for r, _v in GATE) + tuple(r for r, _v in CAPS) + tuple(r for r, _n in TPS)
NETS = ("THG_MID", "THG_VDD", "THG_OT", "THG_G", "THG_TT", "THG_VT")
RETIRES = ("RT1",)

# ------------------------------------------------------------------ the old text: apply_gen_sch_a_ptc.py's block, word for word
_OLD_LOOP = (
    '# RECORD l8p (MESHSAT-1357, 4 October 2026; record l9stk 15.4, C-1b and condition C2, and 15.5, THE THERMAL GUARD): THE PACK\n'
    '# BREAKER\'S DOCK ENABLE LOOP CROSSES THIS BOARD. Board P\'s LM5069-1 breaker (record l8p\'s apply_gen_sch_p_breaker.py) is held off\n'
    '# unless a loop from its input, out over board E and the dock and back, is closed: J_DOCK pins 5 (DOCK_EN_OUT) and 3 (DOCK_EN_RET)\n'
    '# with pin 4, between them in the 2 x 6 field\'s first row, still ground (C2: a short between the two conductors meets ground\n'
    '# first). On this board the loop passes RT1, the kit\'s PRF15BB103 chip PTC, on the battery FETs\' copper: Murata prints 100 kOhm\n'
    '# over 110 C and 4.7 MOhm at 130 +-3 C, so the breaker is off before RT1\'s copper passes 133 C (its no-trip side is not printed:\n'
    '# record l8p\'s L8P-F07, OPEN; E-13), the guard against the battery FETs\' installed path never being met. The two enable\n'
    '# contacts mate at least 1 mm after every power pin (C1, Layer 7). The third battery FET is\n'
    '# L4-E11\'s to draw and name; RT1 sits beside all three. The map is changed after the call, which is left for the drafts that\n'
    '# edit it (L4-E11\'s pin 1); it refuses if pins 3 to 5 are not all ground any more.\n'
    'for _p8 in P:\n'
    '    if _p8["ref"] == "J_DOCK":\n'
    '        if (_p8["nets"]["3"], _p8["nets"]["4"], _p8["nets"]["5"]) != ("GND", "GND", "GND"):\n'
    '            raise SystemExit("record l8p: J_DOCK pins 3 to 5 are %r, not the ground the enable loop takes" % ((_p8["nets"]["3"], _p8["nets"]["4"], _p8["nets"]["5"]),))\n'
    '        _p8["nets"]["3"], _p8["nets"]["5"] = "DOCK_EN_RET", "DOCK_EN_OUT"\n'
    '        _v8 = re.sub(r"\\b([12])-7 GND, 8 SHORE_INHIBIT", lambda _m: "%s, 4, 6, 7 GND, 3 DOCK_EN_RET and 5 DOCK_EN_OUT (the pack breaker\'s make-last enable loop through RT1, record l8p), 8 SHORE_INHIBIT"\n'
    '                     % ("1, 2" if _m.group(1) == "1" else "2"), _p8["value"], count=1)\n'
    '        if _v8 == _p8["value"]:\n'
    '            raise SystemExit("record l8p: J_DOCK\'s description no longer names its ground pins as 1-7 or 2-7")\n'
    '        _p8["value"] = _v8\n'
    'part("RT1", "Device", "Thermistor_PTC", "PRF15BB103RB6RC chip PTC 10k, 100k over 110 C, 4.7M at 130 C (Murata): the pack breaker\'s thermal guard in the dock enable loop, on the battery FETs\' copper (record l8p; l9stk 15.5)",\n'
    '     "Resistor_SMD:R_0402_1005Metric", {"1": "DOCK_EN_OUT", "2": "DOCK_EN_RET"}, "C443668")\n'
    '_intent.node("DOCK_EN_OUT", 29.2, "the pack breaker\'s enable loop from board P (its BRK_VIN through 10 kOhm, BRK_VIN itself with the "\n'
    '             "loop open), J_DOCK pin 5 to RT1: at most the breaker\'s input clamp, 29.2 V (record l9stk 15.4)", v_work=16.8)\n'
    '_intent.node("DOCK_EN_RET", 17.4, "the loop\'s return from RT1 to J_DOCK pin 3 and board P\'s first inverter gate: at most 17.4 V under "\n'
    '             "the clamp\'s 29.2 V (record l9stk 15.4, the inverters\' bounds)")\n')
_OLD_SEC = ('SECTIONS.append(("THE PACK BREAKER\'S DOCK ENABLE LOOP: THE THERMAL GUARD RT1 ON THE BATTERY FETS\' COPPER (RECORD l8p)", ["RT1"]))   # Layer 8 record l8p\n')

# ------------------------------------------------------------------ the new text
_NEW_LOOP = (
    '# RECORD l8p (MESHSAT-1357, 4 October 2026; ROUND 8, 5 October 2026; record l9stk 15.4, C-1b and condition C2, and 15.9, THE\n'
    '# THERMAL GUARD as its round 5 re-selected it, C4, SESSION): THE PACK BREAKER\'S DOCK ENABLE LOOP CROSSES THIS BOARD. Board P\'s\n'
    '# LM5069-1 breaker (record l8p\'s apply_gen_sch_p_breaker.py) is held off unless a loop from its input, out over board E and the\n'
    '# dock and back, is closed: J_DOCK pins 5 (DOCK_EN_OUT) and 3 (DOCK_EN_RET) with pin 4, between them in the 2 x 6 field\'s first\n'
    '# row, still ground (C2: a short between the two conductors meets ground first). On this board the loop passes R260 and R261,\n'
    '# two 7.5 kOhm 1 % in series (a short across either leaves 7.5 kOhm: the guard still trips and holds on its own supply).\n'
    '# THE THERMAL GUARD (L8P-F07, L8P-F08): U60, a TI LM26LV factory-preset temperature switch at 130 C (no trip under 127.8 C and\n'
    '# tripped from 132.2 C at VDD 5 V, SNIS144G 6.8), on a ground island at the battery FETs\' pour\'s centroid; U61, a TPS70950\n'
    '# (5 V; 2.7 to 30 V in) from DOCK_EN_OUT, so the guard is powered whenever the pack is docked, the kit dark or not; U60\'s\n'
    '# push-pull OVERTEMP (pin 5; pin 3, the open drain, unused) drives Q60, a 2N7002 from DOCK_EN_RET to ground, through R262\n'
    '# 47 kOhm with C260 1 uF and R263 1 MOhm to ground (the gate under 1 V through the 3.8 ms in which OVERTEMP is not printed,\n'
    '# over 2.5 V within 36 ms of a trip). Tripped, Q60 holds the return low: board P\'s first inverter turns the breaker off, and\n'
    '# board A\'s DD-7 reads it as board P\'s own pull (the return held, the loop powered). U61, Q60 and the gate network sit off the\n'
    '# pour (U61 is specified to TJ 125 C; Q60\'s off leakage is counted at 86.25 C); C263 (X8R) at U60\'s pins. Each battery FET\'s\n'
    '# coupling to U60 is the layout\'s and E-13\'s (record l8p 12m). TP60 to TP63 (TRIP_TEST, VTEMP, the pair\'s midpoint, U60\'s\n'
    '# VDD) serve E-13b. Round 7\'s PTC RT1 (PRF15BB103) is withdrawn: its no-trip side is not printed (L8P-F07). The two enable\n'
    '# contacts mate at least 1 mm after every power pin (C1, Layer 7). The third battery FET is L4-E11\'s to draw and name. The\n'
    '# map is changed after the call, which is left for the drafts that edit it (L4-E11\'s pin 1); it refuses if pins 3 to 5 are\n'
    '# not all ground any more.\n'
    'for _p8 in P:\n'
    '    if _p8["ref"] == "J_DOCK":\n'
    '        if (_p8["nets"]["3"], _p8["nets"]["4"], _p8["nets"]["5"]) != ("GND", "GND", "GND"):\n'
    '            raise SystemExit("record l8p: J_DOCK pins 3 to 5 are %r, not the ground the enable loop takes" % ((_p8["nets"]["3"], _p8["nets"]["4"], _p8["nets"]["5"]),))\n'
    '        _p8["nets"]["3"], _p8["nets"]["5"] = "DOCK_EN_RET", "DOCK_EN_OUT"\n'
    '        _v8 = re.sub(r"\\b([12])-7 GND, 8 SHORE_INHIBIT", lambda _m: "%s, 4, 6, 7 GND, 3 DOCK_EN_RET and 5 DOCK_EN_OUT (the pack breaker\'s make-last enable loop through the thermal guard\'s pair R260 and R261, record l8p), 8 SHORE_INHIBIT"\n'
    '                     % ("1, 2" if _m.group(1) == "1" else "2"), _p8["value"], count=1)\n'
    '        if _v8 == _p8["value"]:\n'
    '            raise SystemExit("record l8p: J_DOCK\'s description no longer names its ground pins as 1-7 or 2-7")\n'
    '        _p8["value"] = _v8\n'
    'r("R260", "7.5k 1%", "DOCK_EN_OUT", "THG_MID"); r("R261", "7.5k 1%", "THG_MID", "DOCK_EN_RET")   # the loop\'s fixed element, two in series (C4)\n'
    'ic("U60", 7, "LM26LVQISDX-130/NOPB temperature switch, 130 C preset (TI SNIS144G): the battery FETs\' thermal guard, on their pour", "WSON6", {\n'
    ' "1": "THG_TT", "2": "GND", "3": "NC", "4": "THG_VDD", "5": "THG_OT", "6": "THG_VT", "7": "GND"})   # 3 the open-drain output, unused; 7 the thermal pad, to ground (SNIS144G p.4)\n'
    'c("C263", "100n 50V X8R", "THG_VDD", "GND")   # U60\'s VDD at its pins on the guard\'s island (X8R: the island may pass X7R\'s 125 C at the trip)\n'
    'ic("U61", 5, "TPS70950DBVR 5.0 V LDO, 2.7 to 30 V in (TI SBVS186H): the thermal guard\'s supply from the enable loop", "SOT235", {\n'
    ' "1": "DOCK_EN_OUT", "2": "GND", "3": "NC", "4": "NC", "5": "THG_VDD"})   # 3 EN left open: its 300 nA pull-up enables it (TI: never tie EN to IN, its 6.5 V clamp)\n'
    'c("C261", "1u 50V X7R", "DOCK_EN_OUT", "GND"); c("C262", "4.7u 16V X7R", "THG_VDD", "GND")   # U61\'s input and output (an effective 1.5 to 47 uF at 5 V)\n'
    'r("R262", "47k 1%", "THG_OT", "THG_G"); c("C260", "1u 16V X7R", "THG_G", "GND"); r("R263", "1M 1%", "THG_G", "GND")   # the shunt\'s gate network\n'
    'part("Q60", "Transistor_FET", "2N7002", "2N7002: THG_G high = the thermal guard tripped, DOCK_EN_RET held low (1 G, 2 S, 3 D)", "SOT23", {"1": "THG_G", "2": "GND", "3": "DOCK_EN_RET"}, "C8545")\n'
    'tp("TP60", "THG_TT"); tp("TP61", "THG_VT"); tp("TP62", "THG_MID"); tp("TP63", "THG_VDD")   # E-13b\n'
    '_intent.node("DOCK_EN_OUT", 29.2, "the pack breaker\'s enable loop from board P (its BRK_VIN through 10 kOhm, BRK_VIN itself with the "\n'
    '             "loop open), J_DOCK pin 5 to the guard\'s pair and U61\'s input: at most the breaker\'s input clamp, 29.2 V (record l9stk 15.4)", v_work=16.8)\n'
    '_intent.node("DOCK_EN_RET", 17.4, "the loop\'s return from the guard\'s pair (and Q60\'s drain) to J_DOCK pin 3 and board P\'s first inverter "\n'
    '             "gate: at most 17.4 V under the clamp\'s 29.2 V (record l9stk 15.4, the inverters\' bounds; 13.8 V with the pair at its least)")\n'
    '_thg = "record l8p round 8, the thermal guard (record l9stk 15.9, C4): "\n'
    '_intent.node("THG_MID", 29.2, _thg + "the midpoint of R260 and R261, between DOCK_EN_OUT and DOCK_EN_RET: at most DOCK_EN_OUT\'s 29.2 V")\n'
    '_intent.node("THG_VDD", 5.05, _thg + "U61\'s output, TPS70950 5.0 V +-1 % (TI SBVS186H 6.5): U60\'s VDD")\n'
    '_intent.node("THG_OT", 5.05, _thg + "U60\'s push-pull OVERTEMP, at most its VDD (TI SNIS144G 6.6)")\n'
    '_intent.node("THG_G", 4.83, _thg + "Q60\'s gate, OVERTEMP through R262 over R263 (0.955 of it)")\n'
    '_intent.node("THG_TT", 5.05, _thg + "U60\'s TRIP_TEST, open in service (its pull-down), pulled to VDD at E-13b")\n'
    '_intent.node("THG_VT", 5.05, _thg + "U60\'s VTEMP, an analog output under its VDD")\n'
    '_intent.bypass("C263", "U60", "4", "THG_VDD", cls="D", basis="TI SNIS144G (LM26LV) 9 p.25: \'For noisy environments, TI recommends a 100-nF supply "\n'
    '               "decoupling capacitor placed closed across the VDD and GND pins\'")\n'
    '_intent.bypass("C262", "U61", "5", "THG_VDD", cls="L", basis="TI SBVS186H (TPS709) pin table p.3: OUT \'Connect a small 2.2-uF or greater ceramic "\n'
    '               "capacitor from this pin to ground to assure stability\'; 8.1.1 p.14: \'the minimum effective capacitance for stability is 1.5 uF. "\n'
    '               "The maximum capacitance for stability is 47 uF\', ESR \'between 0 and 0.2\'", value_floor="1.5u", value_ceiling="47u", esr_max=0.2)\n'
    '_intent.bypass("C261", "U61", "1", "DOCK_EN_OUT", cls="D", basis="TI SBVS186H (TPS709) 8.1.1 p.14: \'good analog design practice is to connect a "\n'
    '               "0.1-uF to 2.2-uF capacitor from IN to GND ... An input capacitor is necessary if line transients greater than 10 V in "\n'
    '               "magnitude are anticipated\'")\n')
_NEW_SEC = ('SECTIONS.append(("THE PACK BREAKER\'S DOCK ENABLE LOOP: THE THERMAL GUARD U60 (LM26LV 130 C) ON THE BATTERY FETS\' POUR, ITS SUPPLY U61 '
            'AND ITS SHUNT Q60 (RECORD l8p ROUND 8)", ["R260", "R261", "U60", "C263", "U61", "C261", "C262", "R262", "C260", "R263", "Q60", "TP60", '
            '"TP61", "TP62", "TP63"]))   # Layer 8 record l8p\n')

EDITS = [
    (_OLD_LOOP, _NEW_LOOP),
    (_OLD_SEC, _NEW_SEC),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def code_only(text):
    return "\n".join(l.split("#")[0] for l in text.splitlines())


def patched(text):
    if text.count(_NEW_LOOP) or text.count(_NEW_SEC):
        refuse("already applied (the new text is present)")
    if text.count(_OLD_LOOP) != 1 or text.count(_OLD_SEC) != 1:
        refuse("record l8p's PTC block (apply_gen_sch_a_ptc.py) is not in the target once (%d, %d): apply it first"
               % (text.count(_OLD_LOOP), text.count(_OLD_SEC)))
    code = code_only(text.replace(_OLD_LOOP, "").replace(_OLD_SEC, ""))
    for ref in ADDS + RETIRES:
        if re.search(r'"%s"' % re.escape(ref), code):
            refuse("designator %s is already in use in the target" % ref)
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), code):
            refuse("net %s already exists in the target" % net)
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once: %r" % (new.count(old), old[:70]))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    if re.search(r'"RT1"', code_only(new)):
        refuse("RT1 is still drawn after the edit")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: record l8p drafts this change for board A's generator owner and never applies it. Writing the repository's own
# gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
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
