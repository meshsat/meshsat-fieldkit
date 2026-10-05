#!/usr/bin/env python3
"""apply_gen_sch_b_iocpre.py: DRAFT for board B's generator owner (Layer 9 record l9t5, task T10, finding L9T5-F06, MESHSAT-1357,
4 October 2026), board B's half of apply_gen_sch_a_iocpre.py. NOT APPLIED to the tree by this record; its author ran it only on
scratch copies. It applies AFTER apply_gen_sch_b_iocbuck.py (I-03's draft) and refuses a target without it.

The correction (record l9t5's l9t5_t10.out section 8): board A's U601 feeds the three supervisors' LDOs U40, U50 and U60 at a
pre-regulated 4.18 V instead of 5 V. No part and no net changes on this board: each controller keeps its own AP2112K-3.3, its EN
pull-up, its bench jumper and its capacitors. Only the DECLARATIONS follow the rail:
  1. +5V_IOC arrives at 4.18 V (4.0711 to 4.2907 V at board A); its peak is the three LDOs' own current at rv-pwr's HIGH, 1.3800 A;
  2. each +3V3_IOCx is an LDO from 4.18 V: its declared conversion efficiency 0.66 (3.3 / 5.0) becomes 0.79 (3.3 / 4.18).
The clamp D900 (SMBJ5.0A) and C900 stand: a 5 V standoff over a 4.3 V working maximum.
Usage:  apply_gen_sch_b_iocpre.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target lacks I-03's draft, the change is already applied, or the repository's own
generator is named before RELEASE-T10.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_b_iocpre"
BOARD = "b"
ADDS = ()
V_NOM, IOC_PEAK, LDO_EFF = 4.18, 1.3800, 0.79
REQUIRES = ('_intent.rail("+5V_IOC", 5.0, 0.36, 1.4749, "J_5V_IOC", loads=_IOC_LOADS,',)

_OLD_RAIL = '_intent.rail("+5V_IOC", 5.0, 0.36, 1.4749, "J_5V_IOC", loads=_IOC_LOADS, budget=0.02, share=0.015, converted=False,\n'
_NEW_RAIL = ("# T10, RECORD l9t5 (l9t5_t10.out): +5V_IOC ARRIVES PRE-REGULATED AT 4.18 V (board A's U601, R602 13.3k), so that each controller's\n"
             "# AP2112K-3.3 drops under a volt; the net keeps its name. The note below is I-03's and keeps its 5 V figures as history.\n"
             '_intent.rail("+5V_IOC", %.2f, 0.36, %.4f, "J_5V_IOC", loads=_IOC_LOADS, budget=0.02, share=0.015, converted=False,\n' % (V_NOM, IOC_PEAK))
_OLD_EFF = ('converted=True, efficiency=0.66,\n'
            '                 fed_from="+5V_IOC",   # U40/U50/U60 pin 1 and their EN pull-ups are on /+5V_IOC (record l9t5, I-03)')
_NEW_EFF = ('converted=True, efficiency=%.2f,\n'
            '                 fed_from="+5V_IOC",   # U40/U50/U60 pin 1 and their EN pull-ups are on /+5V_IOC (record l9t5, I-03), at 4.18 V since T10: 3.3 / 4.18'
            % LDO_EFF)
EDITS = [(_OLD_RAIL, _NEW_RAIL), (_OLD_EFF, _NEW_EFF)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if EDITS[0][1] in text:
        refuse("the change is already applied")
    for need_ in REQUIRES:
        if need_ not in text:
            refuse("the target does not carry record l9t5's I-03 draft (%s): apply apply_gen_sch_%s_iocbuck.py first" % (need_[:40], BOARD))
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
