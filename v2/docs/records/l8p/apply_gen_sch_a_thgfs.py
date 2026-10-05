#!/usr/bin/env python3
"""apply_gen_sch_a_thgfs.py: DRAFT for board A's generator owner (Layer 8 record l8p ROUND 9, MESHSAT-1357, 5 October 2026; the
owner's review of checkpoint 3, part 22, item A; the independent check V6's minor m7; the check cx45's Q5). NOT APPLIED to the tree
by this record; its author ran it only on scratch copies. It applies AFTER apply_gen_sch_a_thguard.py (round 8's guard) and refuses a
target without it.

Why: V6-m7 found three single failures the round 8 table missed (Q60's gate shorted to its drain disarms the guard; C261 open leaves
U61 without the input capacitor TI calls necessary for line steps over 10 V; U60's thermal pad open leaves the die coupled through its
leads alone), and cx45 found that the round 8 guard's common path (U61 open, Q60 open, R262 open, C260 or R263 shorted, FM2) removes
the trip as a single failure with no bounded detection interval; no approved requirement permits either (l8p_c4.out 10b). The
correction, judged on C-PROT rev 1 in l8p_c4.out 10c and 10d:
  PATH 1, round 8's guard, kept: U60, U61, R262 47 kOhm, C260 1 uF, R263 1 MOhm, Q60 on DOCK_EN_RET; plus
    Q62, Q63  THE COLD CLAMP: two 2N7002 in series from Q60's gate to ground, gated by THG_ODN, U60's open-drain output (pin 3,
              active low, unused in round 8) pulled to VDD by R268 and R269 (220 kOhm each, in series): Q60's gate to drain short
              TRIPS; no single short of the clamp holds the gate low;
    C261,C268 330 nF each on U61's input (was C261 1 uF): one open leaves 330 nF, inside TI's 0.1 to 2.2 uF;
  PATH 2, new, sharing with path 1 only the pour it senses and the loop it opens:
    U62  a second LM26LV-130 on the same pour, its own pad, C269; supplied by U63, a second TPS70950, from VBAT (C270 in, C271 out);
    R270, C272, R271 round 8's gate network (47 kOhm, 1 uF, 1 MOhm) to Q61, a 2N7002 from DOCK_EN_OUT to ground: tripped, it pulls the
         loop's source low and the return with it (board P's first inverter turns the breaker off; DD-7 reads the loop dark);
  TP64 to TP67 E-13b on path 2 apart from path 1, and the clamp's gate.
A sink on DOCK_EN_OUT does not move the return against DOCK_EN_OUT, so L4-E11 20c's window is unchanged by path 2. Consequence for
other rows: the guard's draw on DOCK_EN_OUT rises from 18.25 uA to at most 40 uA cold and 50 uA tripped (l8p_c4.out 10c: L4-E11
section 28 restates 20c and 20f on them; Layer 5's 30 uA row and record l9stk 15.9 to restate, L8P-R9-F2); U63 draws at most 2.25 uA
plus U62's 16 uA from VBAT.
Usage:  apply_gen_sch_a_thgfs.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (round 8's guard absent, already applied, a designator or net in use, or the repository's
own generator named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_thgfs"
CLAMP = (("Q62", "2N7002"), ("Q63", "2N7002"))
PULLUP = (("R268", "220k 1%"), ("R269", "220k 1%"))
SWITCH2 = ("U62", "LM26LVQISDX-130/NOPB")
REG2 = ("U63", "TPS70950DBVR")
SHUNT2 = ("Q61", "2N7002")
GATE = (("R262", "47k 1%"), ("C260", "1u 16V X7R"), ("R263", "1M 1%"))
GATE2 = (("R270", "47k 1%"), ("C272", "1u 16V X7R"), ("R271", "1M 1%"))
CAPS = (("C261", "330n 50V X7R"), ("C268", "330n 50V X7R"), ("C262", "4.7u 16V X7R"), ("C263", "100n 50V X8R"), ("C269", "100n 50V X8R"),
        ("C270", "330n 50V X7R"), ("C271", "4.7u 16V X7R"))
TPS = (("TP64", "THG_TT2"), ("TP65", "THG_VT2"), ("TP66", "THG_ODN"), ("TP67", "THG_VDD2"))
ADDS = tuple(r for r, _v in CLAMP + PULLUP + GATE2) + (SWITCH2[0], REG2[0], SHUNT2[0], "C268", "C269", "C270", "C271") + tuple(r for r, _n in TPS)
NETS = ("THG_ODN", "THG_PU", "THG_CL", "THG_VDD2", "THG_OT2", "THG_G2", "THG_TT2", "THG_VT2")
_OLD_0 = 'part("Q60", "Transistor_FET", "2N7002", "2N7002: THG_G high = the thermal guard tripped, DOCK_EN_RET held low (1 G, 2 S, 3 D)", "SOT23", {"1": "THG_G", "2": "GND", "3": "DOCK_EN_RET"}, "C8545")\n'
_NEW_0 = 'part("Q60", "Transistor_FET", "2N7002", "2N7002: THG_G high = the thermal guard tripped, DOCK_EN_RET held low (1 G, 2 S, 3 D)", "SOT23", {"1": "THG_G", "2": "GND", "3": "DOCK_EN_RET"}, "C8545")\n# ROUND 9 (record l8p, the owner\'s review of 5 October 2026 part 22 and the check cx45\'s Q5, V6-m7): PATH 1\'s COLD CLAMP. Q62 and\n# Q63, two 2N7002 in series from THG_G to ground, gates on THG_ODN: U60\'s open-drain OVERTEMP (pin 3, active low) pulled to VDD by\n# R268 and R269 in series. Cold, both are on and hold THG_G at ground, so a gate to drain short of Q60 ties the return to ground\n# through them: the return held, the breaker off, the fault TRIPS rather than disarms. Tripped, U60\'s open drain pulls THG_ODN low,\n# the clamp lets go and OVERTEMP lifts the gate as before. Two in series so one shorted FET or one shorted resistor leaves the clamp\npart("Q62", "Transistor_FET", "2N7002", "2N7002: the thermal guard\'s cold clamp, upper (THG_ODN high = cold, THG_G held low; 1 G, 2 S, 3 D)", "SOT23", {"1": "THG_ODN", "2": "THG_CL", "3": "THG_G"}, "C8545")\npart("Q63", "Transistor_FET", "2N7002", "2N7002: the thermal guard\'s cold clamp, lower (1 G, 2 S, 3 D)", "SOT23", {"1": "THG_ODN", "2": "GND", "3": "THG_CL"}, "C8545")\nr("R268", "220k 1%", "THG_VDD", "THG_PU"); r("R269", "220k 1%", "THG_PU", "THG_ODN")   # U60\'s open drain\'s pull-up, two in series\n# ROUND 9 (cx45 Q5): PATH 2, A SECOND GUARD WITH NOTHING IN COMMON WITH PATH 1 BUT THE POUR IT SENSES AND THE LOOP IT OPENS. U62, a\n# second LM26LV-130 on the same pour on its own pad, supplied by U63, a second TPS70950, from VBAT (not from DOCK_EN_OUT: its start\n# then loads no docking); its OVERTEMP drives Q61, a 2N7002 from DOCK_EN_OUT to ground, through R270 47 kOhm with C272 1 uF and R271\n# 1 MOhm (round 8\'s network). Tripped, Q61 pulls the loop\'s source low: the return falls with it, board P\'s first inverter turns the\n# breaker off, and board A\'s DD-7 reads the loop dark (no trigger). A sink on DOCK_EN_OUT does not move the return against\n# DOCK_EN_OUT, so L4-E11 20c\'s window is untouched. U61, Q60, R262, C260 or R263 failing leaves path 2; path 2 failing leaves path 1\nic("U63", 5, "TPS70950DBVR 5.0 V LDO, 2.7 to 30 V in (TI SBVS186H): the second thermal guard\'s supply from VBAT (record l8p round 9)", "SOT235", {\n "1": "VBAT", "2": "GND", "3": "NC", "4": "NC", "5": "THG_VDD2"})   # 3 EN left open: its 300 nA pull-up enables it (TI: never tie EN to IN)\nc("C270", "330n 50V X7R", "VBAT", "GND"); c("C271", "4.7u 16V X7R", "THG_VDD2", "GND")   # U63\'s input and output (an effective 1.5 to 47 uF at 5 V)\nr("R270", "47k 1%", "THG_OT2", "THG_G2"); c("C272", "1u 16V X7R", "THG_G2", "GND"); r("R271", "1M 1%", "THG_G2", "GND")   # path 2\'s gate network\npart("Q61", "Transistor_FET", "2N7002", "2N7002: THG_G2 high = the second thermal guard tripped, DOCK_EN_OUT held low (1 G, 2 S, 3 D)", "SOT23", {"1": "THG_G2", "2": "GND", "3": "DOCK_EN_OUT"}, "C8545")\n'
_OLD_1 = 'c("C261", "1u 50V X7R", "DOCK_EN_OUT", "GND"); c("C262", "4.7u 16V X7R", "THG_VDD", "GND")   # U61\'s input and output (an effective 1.5 to 47 uF at 5 V)\n'
_NEW_1 = 'c("C261", "330n 50V X7R", "DOCK_EN_OUT", "GND"); c("C262", "4.7u 16V X7R", "THG_VDD", "GND")   # U61\'s input and output (an effective 1.5 to 47 uF at 5 V)\nc("C268", "330n 50V X7R", "DOCK_EN_OUT", "GND")   # ROUND 9: U61\'s input as two capacitors, so one open leaves 330 nF (TI: necessary, 0.1 to 2.2 uF)\n'
_OLD_2 = ' "1": "THG_TT", "2": "GND", "3": "NC", "4": "THG_VDD", "5": "THG_OT", "6": "THG_VT", "7": "GND"})   # 3 the open-drain output, unused; 7 the thermal pad, to ground (SNIS144G p.4)\n'
_NEW_2 = ' "1": "THG_TT", "2": "GND", "3": "THG_ODN", "4": "THG_VDD", "5": "THG_OT", "6": "THG_VT", "7": "GND"})   # 3 the open-drain output, the cold clamp\'s gate (round 9); 7 the thermal pad, to ground (SNIS144G p.4)\nic("U62", 7, "LM26LVQISDX-130/NOPB temperature switch, 130 C preset (TI SNIS144G): the battery FETs\' second thermal guard (path 2), on their pour (record l8p round 9)", "WSON6", {\n "1": "THG_TT2", "2": "GND", "3": "NC", "4": "THG_VDD2", "5": "THG_OT2", "6": "THG_VT2", "7": "GND"})   # 3 the open drain, unused; 7 the thermal pad, to ground\nc("C269", "100n 50V X8R", "THG_VDD2", "GND")   # U62\'s VDD at its pins (X8R as C263)\n'
_OLD_3 = 'tp("TP60", "THG_TT"); tp("TP61", "THG_VT"); tp("TP62", "THG_MID"); tp("TP63", "THG_VDD")   # E-13b\n'
_NEW_3 = 'tp("TP60", "THG_TT"); tp("TP61", "THG_VT"); tp("TP62", "THG_MID"); tp("TP63", "THG_VDD")   # E-13b\ntp("TP64", "THG_TT2"); tp("TP65", "THG_VT2"); tp("TP66", "THG_ODN"); tp("TP67", "THG_VDD2")   # E-13b on path 2 apart from path 1, and the clamp\'s gate (round 9)\n'
_OLD_4 = '_intent.node("THG_G", 4.83, _thg + "Q60\'s gate, OVERTEMP through R262 over R263 (0.955 of it)")\n'
_NEW_4 = '_intent.node("THG_G", 4.83, _thg + "Q60\'s gate, OVERTEMP through R262 over R263 (0.955 of it); held at ground cold by Q62 and Q63 (round 9)")\n_intent.node("THG_ODN", 5.05, _thg + "U60\'s open-drain OVERTEMP and the clamp\'s gates, pulled to VDD by R268 and R269 (round 9)")\n_intent.node("THG_PU", 5.05, _thg + "the midpoint of R268 and R269 (round 9)")\n_intent.node("THG_CL", 4.83, _thg + "between the clamp\'s two FETs, at most THG_G (round 9)")\n_intent.node("THG_VDD2", 5.05, _thg + "U63\'s output, TPS70950 5.0 V +-1 %: path 2\'s switch U62 (round 9)")\n_intent.node("THG_OT2", 5.05, _thg + "U62\'s push-pull OVERTEMP, at most its VDD (round 9)")\n_intent.node("THG_G2", 4.83, _thg + "Q61\'s gate, U62\'s OVERTEMP through R270 over R271 (0.955 of it) (round 9)")\n_intent.node("THG_TT2", 5.05, _thg + "U62\'s TRIP_TEST, open in service, pulled to VDD at E-13b (round 9)")\n_intent.node("THG_VT2", 5.05, _thg + "U62\'s VTEMP, an analog output under its VDD (round 9)")\n'
_OLD_5 = '               "magnitude are anticipated\'")\n'
_NEW_5 = '               "magnitude are anticipated\'")\n_intent.bypass("C269", "U62", "4", "THG_VDD2", cls="D", basis="TI SNIS144G (LM26LV) 9 p.25: \'For noisy environments, TI recommends a 100-nF supply "\n               "decoupling capacitor placed closed across the VDD and GND pins\' (record l8p round 9)")\n_intent.bypass("C271", "U63", "5", "THG_VDD2", cls="L", basis="TI SBVS186H (TPS709) pin table p.3: OUT \'Connect a small 2.2-uF or greater ceramic "\n               "capacitor from this pin to ground to assure stability\'; 8.1.1 p.14: \'the minimum effective capacitance for stability is 1.5 uF. "\n               "The maximum capacitance for stability is 47 uF\', ESR \'between 0 and 0.2\' (record l8p round 9)", value_floor="1.5u", value_ceiling="47u", esr_max=0.2)\n_intent.bypass("C270", "U63", "1", "VBAT", cls="D", basis="TI SBVS186H (TPS709) 8.1.1 p.14: \'good analog design practice is to connect a "\n               "0.1-uF to 2.2-uF capacitor from IN to GND ... An input capacitor is necessary if line transients greater than 10 V in "\n               "magnitude are anticipated\' (record l8p round 9)")\n_intent.bypass("C268", "U61", "1", "DOCK_EN_OUT", cls="D", basis="TI SBVS186H (TPS709) 8.1.1 p.14: \'good analog design practice is to connect a "\n               "0.1-uF to 2.2-uF capacitor from IN to GND ... An input capacitor is necessary if line transients greater than 10 V in "\n               "magnitude are anticipated\' (record l8p round 9: C261 and C268 together, one open leaves the other)")\n'
_OLD_6 = 'SECTIONS.append(("THE PACK BREAKER\'S DOCK ENABLE LOOP: THE THERMAL GUARD U60 (LM26LV 130 C) ON THE BATTERY FETS\' POUR, ITS SUPPLY U61 AND ITS SHUNT Q60 (RECORD l8p ROUND 8)", ["R260", "R261", "U60", "C263", "U61", "C261", "C262", "R262", "C260", "R263", "Q60", "TP60", "TP61", "TP62", "TP63"]))   # Layer 8 record l8p\n'
_NEW_6 = 'SECTIONS.append(("THE PACK BREAKER\'S DOCK ENABLE LOOP: THE THERMAL GUARD U60 (LM26LV 130 C) ON THE BATTERY FETS\' POUR, ITS SUPPLY U61 AND ITS SHUNT Q60 (RECORD l8p ROUND 8)", ["R260", "R261", "U60", "C263", "U61", "C261", "C262", "R262", "C260", "R263", "Q60", "TP60", "TP61", "TP62", "TP63", "Q62", "Q63", "R268", "R269", "C268", "U62", "C269", "U63", "C270", "C271", "R270", "C272", "R271", "Q61", "TP64", "TP65", "TP66", "TP67"]))   # Layer 8 record l8p\n'
EDITS = [(_OLD_0, _NEW_0), (_OLD_1, _NEW_1), (_OLD_2, _NEW_2), (_OLD_3, _NEW_3), (_OLD_4, _NEW_4), (_OLD_5, _NEW_5), (_OLD_6, _NEW_6)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def code_only(text):
    return "\n".join(l.split("#")[0] for l in text.splitlines())


def patched(text):
    if "THG_ODN" in code_only(text):
        refuse("already applied (the new text is present)")
    if text.count(_OLD_0) != 1:
        refuse("record l8p's round 8 guard (apply_gen_sch_a_thguard.py) is not in the target: apply it first")
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


# NOT RELEASED: as apply_gen_sch_a_thguard.py, writing the repository's own gen_sch_a.py is refused until RELEASE.md beside this
# script reads "released: yes" and names one accepted check. A copy elsewhere may be written (the tests do).
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
