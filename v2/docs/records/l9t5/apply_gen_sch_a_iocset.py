#!/usr/bin/env python3
"""apply_gen_sch_a_iocset.py: DRAFT for board A's generator owner (Layer 9 record l9t5, task T10 round 5, the owner's review of 5 October 2026 part 22,
finding L9T5-F22, MESHSAT-1357). NOT APPLIED to the tree by this record; its author ran it only on scratch copies. It applies
AFTER apply_gen_sch_a_iocpre.py (T10's pre-regulator) and refuses a target without it; it is a delta on that draft, which is
record l9t5's T10 draft (Slot A folds it in when it takes it: one writer per file).

The correction (l9t5_t10.out section 10i): a supervisor whose firmware babbles (both transceivers held dominant, a sustained
state nothing in hardware ends) puts its AP2112K-3.3 at 130.6 C on revision V's printed rows at 76.25 C at the drop's worst corner,
over the 125 C criterion that applies to a sustained state. Lowering U601's set point from 4.1805 V (R602 13.3k) to 4.0114 V
(R602 14.0k, 3.9063 to 4.1174 V) lowers every LDO's drop and puts that state at 121.5 C; each LDO's input stays over its
requirement at the largest current the record computes for a regulator (0.4512 A, the held B5 row on rev Y's rows), 3.7004 V
against 3.6652 V. T10-A3 is restated at that current (round 4 held it at the LDO's full 600 mA, which no set point under 4.18 V meets).
What it changes: R602's value to 14.0k (order code owed, Layer 6), U601's value text, +5V_IOC declared at 4.01 V
(v_work 4.12 V). Nothing else.
Usage:  apply_gen_sch_a_iocset.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target lacks T10's pre-regulator draft, the change is already applied, or the
repository's own generator is named before RELEASE-T10.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_a_iocset"
BOARD = "a"
ADDS = ()
REQUIRES = ('r("R602", "13.3k 0.1% 25ppm", "IOCB_FB", "GND")   # record l9t5 (T10): the pre-regulator\'s set point, 4.1805 V nominal; order code owed (Layer 6)',)

_OLD_0 = 'r("R602", "13.3k 0.1% 25ppm", "IOCB_FB", "GND")   # record l9t5 (T10): the pre-regulator\'s set point, 4.1805 V nominal; order code owed (Layer 6)'
_NEW_0 = 'r("R602", "14.0k 0.1% 25ppm", "IOCB_FB", "GND")   # record l9t5 (T10 round 5, L9T5-F22): the set point 4.0114 V nominal, 3.9063 to 4.1174 V; order code owed (Layer 6)'
_OLD_1 = '"TPS62933DRLR 3 A buck, 4.18 V pre-regulator for the three supervisors\' LDOs on board B (I-03, T10)"'
_NEW_1 = '"TPS62933DRLR 3 A buck, 4.01 V pre-regulator for the three supervisors\' LDOs on board B (I-03, T10 round 5)"'
_OLD_2 = '_intent.rail("+5V_IOC", 4.18, 0.36, 1.3800, "L601", loads={"J_5V_IOC": 0.36}, switch="U601", efficiency=0.90, fed_from="VBAT", budget=0.02, share=0.005, v_work=4.30,\n'
_NEW_2 = '# T10 ROUND 5, RECORD l9t5 (L9T5-F22, the owner\'s review of 5 October 2026, part 22): R602 14.0k, 4.0114 V nominal (3.9063 to 4.1174 V);\n# each LDO\'s input stays over its requirement at the largest current the record computes for a regulator (0.4512 A), and a babbling\n# supervisor\'s regulator holds 125 C on revision V at 76.25 C. DRAFTED, not applied.\n_intent.rail("+5V_IOC", 4.01, 0.36, 1.3800, "L601", loads={"J_5V_IOC": 0.36}, switch="U601", efficiency=0.90, fed_from="VBAT", budget=0.02, share=0.005, v_work=4.12,\n'
EDITS = [(_OLD_0, _NEW_0), (_OLD_1, _NEW_1), (_OLD_2, _NEW_2)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if EDITS[0][1] in text:
        refuse("the change is already applied")
    for need_ in REQUIRES:
        if need_ not in text:
            refuse("the target does not carry record l9t5's T10 draft (%s): apply apply_gen_sch_%s_iocpre.py first" % (need_[:40], BOARD))
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once: %r" % (new.count(old), old[:60]))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: record l9t5 drafts this change for the generator's owner and never applies it. Writing the repository's own generator
# is refused until RELEASE-T10.md beside this script reads "released: yes" on its first line and names an accepted check of task T10
# ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_%s.py" % BOARD)
RELEASE = os.path.join(HERE, "RELEASE-T10.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE-T10.md; record l9t5's T10 drafts wait on an accepted check")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE-T10.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE-T10.md names no single check")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_%s.py" % BOARD, "b/gen_sch_%s.py" % BOARD, n=0))
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
