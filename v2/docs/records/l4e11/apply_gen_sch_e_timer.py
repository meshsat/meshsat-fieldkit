#!/usr/bin/env python3
"""apply_gen_sch_e_timer.py: DRAFT for board E's generator owner (task L4-E11, MESHSAT-1357, 2 October 2026). NOT APPLIED to
the tree by L4-E11; its author ran it only on scratch copies (the tests write scratch copies).

Why (defect D-09, found by L4-E9's final round; L4E11-SOURCE-ONLY-AND-ENTRY.md section 7, l4e11_power.out section 7): the
LM5069's fault time is C x VTMRH / ITIMER (3.76 to 4.16 V over 120 to 51 uA, SNVS452G p.5). C5 as drawn, 100 nF K X7R, stacked
over its printed rows gives 2.04 to 11.87 ms, under TI's half-again margin over the start into VIN_RAW (9.2.1.2.4): the start
at 43.18 V into the 34 uF the hot swap charges, with the power limit following VDS, the X7R rows stacked and the bias load,
takes 3.062 ms, so the fault time must be at least 4.593 ms. No 150 nF C0G part is stocked (the filed search); two Murata
GRM3195 C0G 50 V 1206 parts in parallel, 100 nF 2 % (LCSC C907944) and 68 nF 5 % (LCSC C3847777), stacked over Murata's
tolerance, Table A and endurance rows, give 4.927 to 14.653 ms: over the 4.593 ms, and at the maximum the hot-short pulse
(0.675 A at 43.18 V) sits under Figure 10's power law at Q7's derated case (0.71 A, carried 46.5 % past the 10 ms line,
CONDITIONAL). The second capacitor takes the free designator C121 (the generator owner may renumber it).

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else: C5's call, which becomes C5 and C121 on HS_TIMER, each with
its land (the 1206 key C10u50) and its LCSC code, and the vehicle entry's schematic section, which lists C121 after C5.

ORDER: none with L4-E9's apply_gen_sch_e_hotswap.py: the two touch disjoint text on the same line (C5's call against R24's),
so either may run first. It is the ALTERNATIVE to apply_gen_sch_e_entry.py, for a board that keeps the LM5069 (the fix round
selects the TPS48110 entry, which removes this timer): each refuses once the other has run.

Usage:  apply_gen_sch_e_timer.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_timer"
EDITS = [
    ('c("C5", "100n (TIMER)", "HS_TIMER", "GND_V")',
     'c("C5", "100n C0G 2% 50V 1206 (TIMER with C121: 168 nF, L4-E11)", "HS_TIMER", "GND_V", "C10u50", lcsc="C907944"); '
     'c("C121", "68n C0G 5% 50V 1206 (TIMER with C5, L4-E11)", "HS_TIMER", "GND_V", "C10u50", lcsc="C3847777")'),
    ('"C5", "R24", "R25", "Q8"', '"C5", "C121", "R24", "R25", "Q8"'),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if text.count('"C121"') != 0:
        refuse("the designator C121 is already used")
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once" % new.count(old))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: task L4-E11 drafts these parts for board E's generator owner and never applies them. Writing the
# repository's own gen_sch_e.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and
# names an accepted check of L4-E11 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may
# be written (the tests do, on scratch copies).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_e.py")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_e.py", "b/gen_sch_e.py", n=0))
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
