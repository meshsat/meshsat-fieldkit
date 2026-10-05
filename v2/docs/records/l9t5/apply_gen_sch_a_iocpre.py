#!/usr/bin/env python3
"""apply_gen_sch_a_iocpre.py: DRAFT for board A's generator owner (Layer 9 record l9t5, task T10, the owner's instruction of
4 October 2026 part 7, finding L9T5-F06, MESHSAT-1357). NOT APPLIED to the tree by this record; its author ran it only on scratch
copies (the tests write scratch copies). It applies AFTER apply_gen_sch_a_iocbuck.py (I-03's draft) and refuses a target without it.

The defect (record l9t5's l9t5_t10.out): each supervisor's private AP2112K-3.3 on board B drops its whole input to 3.3 V in a
SOT-25 whose sheet prints 184 C/W junction to ambient (Diodes DS39724 Rev. 2-2 p.3). From U601's 5 V (4.8719 to 5.1329 V) at the
inside air of L4-E12's hot stop, 76.25 C, its junction passes the 150 C absolute maximum above 0.2187 A, well under the 600 mA the
part can deliver: the thermal limit binds first, and the supervisors' state is bounded by no contract row.

The correction selected (l9t5_t10.out section 8, SESSION): U601 becomes a PRE-REGULATOR for those LDOs. Its divider's bottom
resistor R602 goes from 10.7 k to 13.3 k (0.1 percent, 25 ppm/K as R601): 4.1805 V nominal, 4.0711 to 4.2907 V, the least set point
on the E96 series that keeps each LDO's input over its requirement at its full 600 mA (3.7693 V: output +1.5 percent, load
regulation 1 percent/A, dropout 400 mV) after the rail's budget, the lead and the return's shift AS DRAWN. An LDO then dissipates
at most 0.9907 V times its current: its junction stays at or under 125 C to 0.2674 A at that air (it was 0.1445 A). It is a
correction ONLY TOGETHER WITH Layer 5's contract row that bounds each supervisor's state (l9t5_t10.out, T10-A1): no regulator
makes the unbounded state hold, because the H743 itself passes its 125 C junction above 0.328 A at that air.
What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else:
  1. R602's value 10.7k to 13.3k (no order code carried: owed to Layer 6) and U601's value text;
  2. +5V_IOC declared at 4.18 V (v_work 4.30 V); its peak from its basis: the three LDOs' own current at rv-pwr's HIGH, 1.3800 A
     (an LDO passes its output current; the constant-power convention of the 5 V case does not apply to a pre-regulated LDO input);
  3. VBAT's entry for U601: 0.14 to 0.12 A (0.36 A x 4.18 V / 12.96 V = 0.1161 A, the S-98 method).
The net keeps its name +5V_IOC (a label; renaming it would touch both boards' I-03 drafts: finding L9T5-F10).
Usage:  apply_gen_sch_a_iocpre.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target lacks I-03's draft, the change is already applied, or the repository's own
generator is named before RELEASE-T10.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_a_iocpre"
BOARD = "a"
ADDS = ()
V_NOM, V_WORK, IOC_PEAK, U601_VBAT = 4.18, 4.30, 1.3800, 0.12
REQUIRES = ('ic("U601", 8, "TPS62933DRLR 3 A buck, 5.0 V for the three supervisors\' LDOs on board B (I-03)"',)

_OLD_R = 'r("R602", "10.7k 0.1% 25ppm", "IOCB_FB", "GND", lcsc="C861078")'
_NEW_R = 'r("R602", "13.3k 0.1% 25ppm", "IOCB_FB", "GND")   # record l9t5 (T10): the pre-regulator\'s set point, 4.1805 V nominal; order code owed (Layer 6)'
_OLD_U = '"TPS62933DRLR 3 A buck, 5.0 V for the three supervisors\' LDOs on board B (I-03)"'
_NEW_U = '"TPS62933DRLR 3 A buck, 4.18 V pre-regulator for the three supervisors\' LDOs on board B (I-03, T10)"'
_OLD_RAIL = '_intent.rail("+5V_IOC", 5.0, 0.36, 1.4749, "L601", loads={"J_5V_IOC": 0.36}, switch="U601", efficiency=0.90, fed_from="VBAT", budget=0.02, share=0.005, v_work=5.14,\n'
_NEW_RAIL = ("# T10, RECORD l9t5 (the owner's instruction of 4 October 2026, part 7; l9t5_t10.out): U601 IS A PRE-REGULATOR FOR THE SUPERVISORS' LDOS.\n"
             "# R602 13.3k sets 4.1805 V nominal (4.0711 to 4.2907 V): each AP2112K-3.3 on board B then dissipates under a volt times its current,\n"
             "# and its junction stays at or under 125 C to 0.2674 A at L4-E12's 76.25 C air (0.1445 A from the 5 V set point). The note below is\n"
             "# I-03's and keeps its 5 V figures as history; the rail's volts, working maximum and peak are T10's. DRAFTED, not applied.\n"
             '_intent.rail("+5V_IOC", %.2f, 0.36, %.4f, "L601", loads={"J_5V_IOC": 0.36}, switch="U601", efficiency=0.90, fed_from="VBAT", budget=0.02, share=0.005, v_work=%.2f,\n'
             % (V_NOM, IOC_PEAK, V_WORK))
_OLD_VBAT = '"U601": 0.14,'
_NEW_VBAT = '"U601": %.2f,' % U601_VBAT
EDITS = [(_OLD_R, _NEW_R), (_OLD_U, _NEW_U), (_OLD_RAIL, _NEW_RAIL), (_OLD_VBAT, _NEW_VBAT)]


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
