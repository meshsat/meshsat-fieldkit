#!/usr/bin/env python3
"""apply_gen_sch_p_idealdiode.py: DRAFT for board P's generator owner (Layer 8 record l8p, MESHSAT-1357, round 4, 4 October
2026: the correction of design defect DD-5). NOT APPLIED to the tree by this record; its author ran it only on scratch copies
(the tests write scratch copies).

The defect (record l9stk section 15.5 to 15.7 at 0d72880b, DD-5; the battery packet's finding BAT-F20, EQ-15): with the gauge's
FET Options CHGIN = 1 the BQ4050 holds the charge FET Q1 off whenever the pack is not charging and the reading is above T3
(SLUUAQ3A 4.13 and 14.2.1.1), discharge included, so the kit's discharge current crosses Q1's body diode: 10 W at 10 A and 23.9
W at the breaker's held 23.93 A (VSD 1 V at most, SLPS471D) against the 1.48 W its pad holds. The BQ4050's documents print no
function that turns the charge FET on while discharge current flows (L8P-BREAKER.md section 13a).

The correction drawn here (case row C-PROT with CHGIN = 1; L8P-BREAKER.md section 13): AN IDEAL DIODE IN PARALLEL WITH Q1.
  Q109    CSD17570Q5B (Q1's part, C529279), source on SCP_OUT and drain on SW as Q1 is, so its body diode points as Q1's does and
          it blocks a charge exactly as Q1 does when off.
  U105    LM74700QDBVRQ1 (TI SNOSD17G; board E's U3 part, C2941042): ANODE on SCP_OUT, CATHODE on SW, GATE on Q109's gate alone.
          Forward (discharge): it holds ANODE to CATHODE at 20 mV (13 to 29 mV) by Q109's gate, and connects the gate to its
          charge pump (10.8 to 13.9 V over the anode) above 50 mV. Reverse (charge): the gate is at the anode, Q109 is off, and
          the charge passes Q1's channel only when the gauge holds CHG on. The gauge's own drive of Q1 (CHG_G, R16, R17) is
          not touched.
  C111    220 nF 50 V X7R 0805 from VCAP to the anode (TI: at least 0.1 uF and at least ten times Q109's Ciss of 13.6 nF).
  R130    10 MOhm from Q109's gate to its source, as R17 is on Q1: an open GATE pin leaves Q109 off.
  D104, R131  EN from BRK_VIN (Q2's source, live only while the gauge holds the discharge FET on, or a charger is present)
          through a 1N4148W, with 1 MOhm to ground: with the gauge shut down U105 draws at most 1.5 uA; the diode keeps a
          negative transient of BRK_VIN off EN (its -0.3 V rating).
  C112, C113  100 nF 50 V in series from the anode to ground (TI: at least 22 nF); C114, C115 470 nF 50 V in series from the
          cathode to ground (TI: at least 100 nF); each pair in series as C11 and C12 are (O-12): one shorted part across the
          cells must not short them.
  TP109   Q109's gate, for the commissioning check E-12d.
  intent  SCP_OUT's loads Q1 and Q109; SW's sources Q1 and Q109; the nodes IDL_GATE, IDL_VCAP, IDL_EN, IDL_AMID, IDL_CMID; the
          decoupling entries C111 (class L), C112 (class D) and C114 (class B2); one schematic section.
SESSION choices (under the owner's standing rule of 26 September 2026; L8P-BREAKER.md section 13c): the arrangement (a second
FET beside Q1, not a second driver on Q1's gate), the parts (both already in the kit), EN's source, the series pairs, the
designators (the 100 block, after round 3's) and the net names.

ORDER: AFTER this record's apply_gen_sch_p_breaker.py (EN reads its BRK_VIN; it refuses a target without it), released with it.

Usage:  apply_gen_sch_p_idealdiode.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; no added designator or net may
exist in the target; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator or
net is in use, the breaker draft is not applied, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_p_idealdiode"
ADDS = ("Q109", "U105", "D104", "R130", "R131", "C111", "C112", "C113", "C114", "C115", "TP109")
NETS = ("IDL_GATE", "IDL_VCAP", "IDL_EN", "IDL_AMID", "IDL_CMID")
REQUIRES = ('ic("U101", 10, "LM5069MM-1 circuit breaker', '_intent.rail("BRK_VIN", ',
            'pfet5("Q2", "CSD17570Q5B 30 V N-FET, discharge switch", "DSG_G", "SW", "BRK_VIN", "C529279")')

_OLD_SCP = '_intent.rail("SCP_OUT", 14.4, 10.0, 18.0, "F2", loads={"Q1": 10.0}, always_on=True, converted=False, fed_from="FUSED",\n'
_NEW_SCP = (
    '# record l8p round 4 (DD-5): SCP_OUT feeds Q1 and, beside it, Q109, the ideal diode U105 drives (drawn before the pack leads).\n'
    '# Either carries the whole discharge current: Q1 while the gauge holds CHG on, Q109 whenever it holds CHG off. The loads are\n'
    '# written as halves of the 18 A peak because the declaration takes one current per part; the layout seats each on the\n'
    '# bands\' full width.\n'
    '_intent.rail("SCP_OUT", 14.4, 10.0, 18.0, "F2", loads={"Q1": 9.0, "Q109": 9.0}, always_on=True, converted=False, fed_from="FUSED",\n')

_OLD_SW = (
    '_intent.rail("SW", 14.4, 10.0, 18.0, "Q1", loads={"Q2": 10.0}, series_of="SCP_OUT", converted=False, v_work=16.8,\n'
    '             note="the common drain of Q1 and Q2 (CSD17570Q5B, TI SLPS471D), the pack\'s whole current: 10 A typical and 18 A "\n'
    '                  "peak as SCP_OUT and PACK_P carry it; discharge current enters through Q1 (its channel, or its body diode "\n'
    '                  "while the gauge holds CHG off: BAT-F20, S-46, open) and leaves through Q2, and charge current the other way")\n')
_NEW_SW = (
    '# record l8p round 4 (DD-5, BAT-F20): Q109 beside Q1 on the same two nets. Where the comment above reads the discharge current\n'
    '# crossing Q1\'s body diode, read Q109\'s channel under U105.\n'
    '_intent.rail("SW", 14.4, 10.0, 18.0, ["Q1", "Q109"], loads={"Q2": 10.0}, series_of="SCP_OUT", converted=False, v_work=16.8,\n'
    '             note="the common drain of Q1, Q109 and Q2 (CSD17570Q5B, TI SLPS471D), the pack\'s whole current: 10 A typical and "\n'
    '                  "18 A peak as SCP_OUT and PACK_P carry it; discharge current enters through Q1\'s channel while the gauge holds "\n'
    '                  "CHG on, and through Q109\'s channel under the ideal-diode controller U105 whenever the gauge holds CHG off "\n'
    '                  "(record l8p, DD-5: BAT-F20\'s body-diode loss corrected in the draft), and leaves through Q2; charge current "\n'
    '                  "the other way, through Q1\'s channel only")\n')

_ANCHOR_WP = 'part("W_P", "Connector", "Conn_01x01_Pin", "pack lead + (12 AWG to the XT60 on E6 J_BATT pin 2)", "WIRE", {"1": "PACK_P"})\n'
_DIODE = (
    '# =========================================================================================================================\n'
    '# RECORD l8p (MESHSAT-1357, 4 October 2026, round 4): DESIGN DEFECT DD-5 (record l9stk 15.5 to 15.7 at 0d72880b; BAT-F20,\n'
    '# EQ-15) CORRECTED IN THE DRAFT. With FET Options CHGIN = 1 the BQ4050 holds Q1 off whenever the pack is not charging and the\n'
    '# reading is above T3 (SLUUAQ3A 4.13: "Not charging AND ..." sets OperationStatus()[XCHG] = 1; 14.2.1.1: "Charging and\n'
    '# Precharging disabled, FETs off"), so the discharge current crossed Q1\'s body diode: 10 W at 10 A, 23.9 W at the breaker\'s\n'
    '# held 23.93 A (VSD 1 V at most), against the 1.48 W its pad holds. The BQ4050\'s documents print no function that turns\n'
    '# the charge FET on while discharge current flows.\n'
    '# THE CORRECTION: AN IDEAL DIODE BESIDE Q1. Q109, a second CSD17570Q5B, has its source on SCP_OUT and its drain on SW as Q1\n'
    '# has, and U105, an LM74700-Q1 (TI SNOSD17G), drives its gate alone: ANODE on SCP_OUT, CATHODE on SW. FORWARD (discharge): U105\n'
    '# holds ANODE to CATHODE at 20 mV (13 to 29 mV) by Q109\'s gate and connects the gate to its charge pump (10.8 to 13.9 V over\n'
    '# the anode) above 50 mV (34 to 57 mV), so Q109 carries 10 A at 0.30 W at most, 18 A at 0.54 W and the breaker\'s 23.93 A at\n'
    '# 0.72 W (0.69 mOhm at most, taken 1.8 times hot as record l9stk takes it), where Q1\'s diode took 10, 18 and 23.9 W. REVERSE\n'
    '# (charge): the gate is at the anode and Q109 is off, so a charge passes Q1\'s channel only, when the gauge holds CHG on: the\n'
    '# gauge\'s charge blocking is unchanged, and its drive of Q1 (CHG_G, R16, R17) is not touched. With Q1 on, the two share and the\n'
    '# pair never dissipates more than Q1 alone did. Q109 welded or its gate stuck high is found as a welded Q1 is (the gauge\'s\n'
    '# CFETF, SLUUAQ3A 3.10; the second level). U105 dead leaves Q109 off behind R130 and the body diodes carry on: E-12d finds it.\n'
    '# EN reads BRK_VIN (Q2\'s source) through D104, with R131 to ground: U105 runs while the gauge holds the discharge FET on or a\n'
    '# charger is present (80 uA typical, 130 uA at most), and draws 1.5 uA at most with the gauge shut down; D104 keeps a negative\n'
    '# transient of BRK_VIN off EN. C111 is the charge pump\'s reservoir (TI: at least 0.1 uF and ten times Ciss, 13.6 nF at most).\n'
    '# C112 with C113 and C114 with C115 are TI\'s anode (22 nF) and cathode (100 nF) capacitances, each pair in series as C11 and\n'
    '# C12 are (O-12). U105 returns to GND, the cells\' negative, as the gauge does. FOR THE LAYOUT (gen_pcb_p3.py): Q109 beside Q1\n'
    '# on the same SCP_OUT and SW bands; the SW pour carrying Q109\'s and Q2\'s losses at 51 K/W or better to the inside air (E-8);\n'
    '# U105 off the pour, where the board stays under 125 C, its ANODE, GATE and CATHODE taken at Q109\'s own pins; C111 away from\n'
    '# the FETs (TI 12.1). Nothing here is built or measured. The acceptance and what stays open: L8P-BREAKER.md section 13.\n'
    'pfet5("Q109", "CSD17570Q5B 30 V N-FET, the ideal diode beside the charge switch Q1 (source on the cells\' side, drain on SW; driven by U105)", "IDL_GATE", "SW", "SCP_OUT", "C529279")\n'
    'ic("U105", 6, "LM74700QDBVRQ1 ideal-diode controller on Q109 (record l8p, DD-5): 1 VCAP, 2 GND, 3 EN, 4 CATHODE, 5 GATE, 6 ANODE",\n'
    '   "SOT236", {"1": "IDL_VCAP", "2": "GND", "3": "IDL_EN", "4": "SW", "5": "IDL_GATE", "6": "SCP_OUT"}, "C2941042")\n'
    'c("C111", "220n 50V X7R 0805 (VCAP: U105\'s charge pump reservoir, to the anode)", "IDL_VCAP", "SCP_OUT", "C10u")   # the board\'s 0805 land\n'
    'r("R130", "10M", "IDL_GATE", "SCP_OUT")   # as R17 on Q1: an open GATE pin leaves Q109 off\n'
    'part("D104", "Device", "D", "1N4148W (U105\'s EN from BRK_VIN; blocks a negative transient)", "SOD123", {"1": "IDL_EN", "2": "BRK_VIN"}, "C81598")   # Device:D, pin 1 K, pin 2 A\n'
    'r("R131", "1M", "IDL_EN", "GND")\n'
    'c("C112", "100n 50V X7R (U105\'s anode capacitance, in series with C113)", "SCP_OUT", "IDL_AMID"); c("C113", "100n 50V X7R (U105\'s anode capacitance, in series with C112)", "IDL_AMID", "GND")\n'
    'c("C114", "470n 50V X7R 0805 (U105\'s cathode capacitance, in series with C115)", "SW", "IDL_CMID", "C10u"); c("C115", "470n 50V X7R 0805 (U105\'s cathode capacitance, in series with C114)", "IDL_CMID", "GND", "C10u")\n'
    'part("TP109", "Connector", "TestPoint", "IDL_GATE", "TP", {"1": "IDL_GATE"})   # E-12d: Q109\'s gate over its source\n'
    '_intent.bypass("C111", "U105", "1", "IDL_VCAP", cls="L", basis="TI LM74700-Q1 SNOSD17G, revised December 2020 (v2/vendor/ti/ti-lm74700-q1.pdf): "\n'
    '               "10.1.1.2.3 \\"VCAP: Minimum 0.1 uF is required; recommended value of VCAP (uF) >= 10 x CISS(MOSFET)(uF)\\" (p.18); 6.3 "\n'
    '               "External capacitance, VCAP to ANODE, 0.1 uF minimum (p.5); 12.1 \\"The charge pump capacitor across VCAP and ANODE pins "\n'
    '               "must be kept away from the MOSFET\\" (p.23)", value_floor="0.136u (ten times the CSD17570Q5B\'s Ciss of 13.6 nF at most, SLPS471D 5.1)",\n'
    '               esr_max="not stated by the maker")\n'
    '_intent.bypass("C112", "U105", "6", "SCP_OUT", cls="D", basis="TI LM74700-Q1 SNOSD17G: 10.1.1.2.3 \\"CIN: minimum 22 nF of input "\n'
    '               "capacitance\\" (p.18) and 6.3 External capacitance, ANODE, 22 nF minimum (p.5); ANODE is the part\'s supply pin "\n'
    '               "(Table 5-1: \\"Anode of the diode and input power\\"); drawn as C112 and C113 in series, 50 nF")\n'
    '_intent.bypass("C114", "U105", "4", "SW", cls="B2", basis="TI LM74700-Q1 SNOSD17G: 10.1.1.2.3 \\"COUT: minimum 100 nF of output "\n'
    '               "capacitance\\" (p.18), with no distance stated; drawn as C114 and C115 in series, 235 nF")\n'
    '_intent.node("IDL_GATE", 30.7, "Q109\'s gate: the anode SCP_OUT (the cells\' 16.8 V at most) plus U105\'s charge pump, at most 13.9 V over "\n'
    '             "the anode (SNOSD17G 6.5, charge pump turn off voltage); the CSD17570Q5B\'s VGS is 20 V (SLPS471D)", rides_on="SCP_OUT", bias_v=13.9)\n'
    '_intent.node("IDL_VCAP", 30.7, "U105\'s charge pump output, at most 13.9 V over the anode SCP_OUT (SNOSD17G 6.5)", rides_on="SCP_OUT", bias_v=13.9)\n'
    '_intent.node("IDL_EN", 29.2, "U105\'s EN, a diode drop under BRK_VIN: the pack\'s 16.8 V in service and the breaker input clamp\'s "\n'
    '             "29.2 V (record l9stk 15.4, the clamps row); EN is 65 V (SNOSD17G 6.1)", v_work=16.8)\n'
    '_intent.node("IDL_AMID", 16.8, "the midpoint of the series pair C112 and C113 on SCP_OUT: about half the cells\' voltage, and the "\n'
    '             "whole 16.8 V across one part when the other has shorted (the case the pair exists for)", v_work=16.8)\n'
    '_intent.node("IDL_CMID", 29.2, "the midpoint of the series pair C114 and C115 on SW: about half of it, and the whole of it across "\n'
    '             "one part when the other has shorted; SW follows BRK_VIN, at most the input clamp\'s 29.2 V", v_work=16.8)\n'
    '# =========================================================================================================================\n')

_ANCHOR_SEC = 'placed_refs = {r_ for _, rs in SECTIONS for r_ in rs}\n'
_SEC = ('SECTIONS.append(("THE IDEAL DIODE BESIDE THE CHARGE SWITCH Q1 (DD-5, BAT-F20): Q109, ITS CONTROLLER U105 (RECORD l8p)",\n'
        '                 ["Q109", "U105", "C111", "R130", "D104", "R131", "C112", "C113", "C114", "C115", "TP109"]))\n')

EDITS = [
    (_OLD_SCP, _NEW_SCP),
    (_OLD_SW, _NEW_SW),
    (_ANCHOR_WP, _DIODE + _ANCHOR_WP),
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
    for req in REQUIRES:
        if req not in text:
            refuse("this record's breaker draft is not applied in the target (%r missing): apply apply_gen_sch_p_breaker.py first" % req[:44])
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
