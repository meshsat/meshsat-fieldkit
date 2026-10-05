#!/usr/bin/env python3
"""apply_gen_sch_d_paloop.py: DRAFT for board D's generator owner (Layer 4 P0-1, record l9t5, F01 / D-17 on C-ALLTX rev 3,
MESHSAT-1357, 5 October 2026), board D's half of the PA drain-current cap; board A's half is apply_gen_sch_a_paloop.py and the two go
in ONE release. NOT APPLIED to the tree by this record; its author ran it only on scratch copies. Prototype design: nothing built.

What it changes in v2/ecad/tools/gen_sch_d.py, and nothing else:
  1. J_HARN1 pin 16 from AB_SPARE to PA_ILIM (the loop's output from board A's U553 through R558), and TP10 with it;
  2. R57 110k 1 % from PA_ILIM into VGG_FB, U15's feedback node: PA_ILIM at V lowers VGG by V x R82 / R57 = 0.65 V a volt; R58 470 Ohm
     from VGG_SW to ground, the bleed (U15 cannot sink: round 2, cx44; 10.1 mA and 48 mW at 4.75 V, about 4.1 V/ms with C62); C76 1 nF
     C0G from PA_ILIM to ground with board A's R558 (1k) a 1 us filter on the harness conductor;
  3. R83 10.0k to 11.0k 1 %: R83 in parallel with R57 is 10.0k, so with PA_ILIM at rest (0 V) VGG's band is the drawn one, 4.4825 V
     nominal; R83's LCSC code (C25804, a 10.0k part) is removed, Layer 6 owes the 11.0k code;
  4. VGG_SW's declaration to 4.75 V: the band's top with PA_ILIM at rest and board D's ground up to 0.1 V above board A's is 4.743 V
     (l9t5_paloop.py vgg_band, the shift taken both ways: 4.202 V at the bottom), 0.257 V under the RA30H1317M1's VGG<5V; PA_ILIM declared (0 to 5.14 V, board A's +5V_D8IN);
  5. R57, C76 and R58 in the gate-bias section's list.
What it does not change: U15, R82, C61, C62, the key discipline (U15's EN is PA_KEY; with PA_KEY low U15 is off and its active discharge
holds VGG at 0 V, whatever PA_ILIM does: at most 5.14 V through R57 and R82 into 95 Ohm), EMCON (the loop can only LOWER VGG: PA_ILIM is
at least 0 V, so R57 never raises VGG over the band its rest state gives).
Order: board D's round, anywhere relative to d8dec31's ptt draft (R96, R97, D15 to D18: next free R and D, both above R57) and record
l6r2's intent and LCSC drafts (its table has no R57, R83 or C76 entry; C76 is above every drawn capacitor).
Usage:  apply_gen_sch_d_paloop.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator or net is in
use, or the repository's own generator is named before RELEASE-F01.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_d_paloop"
ADDS = ("R57", "R58", "C76")
NETS = ("PA_ILIM",)
VGG_TOP = 4.75

_OLD_HARN = '"15": "ZEROIZE_HW", "16": "AB_SPARE"})'
_NEW_HARN = '"15": "ZEROIZE_HW", "16": "PA_ILIM"})'
_OLD_TPS = '"ZEROIZE_HW", "AB_SPARE", "SA_TXD"'
_NEW_TPS = '"ZEROIZE_HW", "PA_ILIM", "SA_TXD"'
_OLD_R83 = 'r("R83", "10.0k 1%", "VGG_FB", "GND", lcsc="C25804")'
_NEW_R83 = ('r("R83", "11.0k 1%", "VGG_FB", "GND"); r("R57", "110k 1%", "PA_ILIM", "VGG_FB"); c("C76", "1n 50V C0G", "PA_ILIM", "GND"); r("R58", "470 1%", "VGG_SW", "GND")'
            '   # record l9t5 P0-1 (F01): see the note below')
_OLD_DECL = ('_intent.node("VGG_SW", 4.68, "the PA gate bias from U15, a TLV75801P set by R82 71.5k over R83 10.0k: 0.55 V x "')
_NEW_DECL = ('# F01 / D-17, RECORD l9t5 P0-1 (MESHSAT-1357, 5 October 2026; v2/docs/records/l9t5/l9t5_f01.out): THE PA\'S DRAIN CURRENT IS\n'
             '# CAPPED THROUGH VGG. Board A\'s U553 (apply_gen_sch_a_paloop.py) holds PA_ILIM at 0 V while the PA\'s drain current is under its\n'
             '# set point and raises it when it is over; R57 110k carries it into VGG_FB, U15\'s feedback node, so VGG falls 0.65 V for every\n'
             '# volt of PA_ILIM (R82 / R57) and the loop holds the drain current at 6.3518 to 6.9259 A (MODEL; F01 / D-17 PROVISIONAL on the\n'
             '# supplier\'s B-PA1 and B-PA2, l9t5_f01.out section 6). R83 goes to\n'
             '# 11.0k so R83 // R57 = 10.0k and the band at rest is the drawn one, 4.4825 V nominal; its top with board D\'s ground up to\n'
             '# 0.1 V above board A\'s is 4.743 V (l9t5_paloop.py), under the module\'s VGG<5V. R83\'s code C25804 (10.0k) is removed: Layer 6\n'
             '# owes the 11.0k code. C76 with board A\'s R558 filters the harness conductor (1 us). R58 470 Ohm from VGG_SW to ground (round 2,\n'
             '# Astra\'s cx44): U15 is an LDO and cannot sink, so VGG falls only by its loads; R58 gives it about 4.1 V/ms at 4.2 V with C62\n'
             '# (the module\'s own gate current not counted). DRAFTED, not applied; PROVISIONAL with board A\'s half on the supplier\'s B-PA1, B-PA2.\n'
             '_intent.node("PA_ILIM", 5.14, "the PA current loop\'s output from board A (U553B through R558 on J_MEZZ1 pin 16): 0 V at rest, '
             'up to board A\'s +5V_D8IN (5.14 V v_work) while the loop lowers VGG")\n'
             '_intent.node("VGG_SW", %.2f, "the PA gate bias from U15, a TLV75801P set by R82 71.5k over R83 (11.0k since record l9t5 P0-1, in '
             'parallel with R57 110k from PA_ILIM: 10.0k at rest): 4.4825 V nominal, 4.202 to 4.743 V with every term, PA_ILIM at rest and '
             'the boards\' grounds up to 0.1 V apart (l9t5_paloop.py); R58 470 Ohm bleeds it; the drawn note follows. "\n             '
             '"the PA gate bias from U15, a TLV75801P set by R82 71.5k over R83 10.0k: 0.55 V x "' % VGG_TOP)
_OLD_SEC = '"U15", "C61", "C62", "R82", "R83", "J_VGG"]'
_NEW_SEC = '"U15", "C61", "C62", "R82", "R83", "R57", "C76", "R58", "J_VGG"]'
EDITS = [(_OLD_HARN, _NEW_HARN), (_OLD_TPS, _NEW_TPS), (_OLD_R83, _NEW_R83), (_OLD_DECL, _NEW_DECL), (_OLD_SEC, _NEW_SEC)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    for ref in ADDS:
        if re.search(r'"%s"' % re.escape(ref), text):
            refuse("designator %s is already in use in the target" % ref)
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), text):
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


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_d.py")
RELEASE = os.path.join(HERE, "RELEASE-F01.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE-F01.md; record l9t5's F01 drafts wait on an accepted check")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE-F01.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE-F01.md names no single check")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_d.py", "b/gen_sch_d.py", n=0))
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
