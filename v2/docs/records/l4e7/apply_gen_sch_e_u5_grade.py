#!/usr/bin/env python3
"""apply_gen_sch_e_u5_grade.py: DRAFT for board E's generator owner (task L4-E7, MESHSAT-1357, 1 October 2026). NOT
APPLIED to the tree by L4-E7; its author ran it only on scratch copies with --check (the tests also write scratch copies).

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else: U5's value text and order code, from the LCSC field the
netlist carries, C674164 (LT8705AEUHF#TRPBF, the E grade), to LT8705AIUHF#PBF, LCSC C674169 (C674170 is the same part on
tape and reel). The I grade is the one 8705af guarantees over -40 to 125 C junction (p.6 Note 3); the E grade is guaranteed
from 0 C and only characterized below. The H and MP grades exist only in the TSSOP (p.3), not the drawn QFN land. U5 is
bench-fitted, and LCSC held no I-grade stock on 1 October 2026 (inputs/lcsc-C674169-2026-10-01.json): another distributor.
The pin map is not touched (apply_gen_sch_e_input_limit.py edits pins 32 and 34; the two drafts apply in either order).

Usage:  apply_gen_sch_e_u5_grade.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_u5_grade"
EDITS = [
    ('part("U5", "Connector_Generic", "Conn_02x20_Odd_Even", "LT8705A buck-boost controller, 38-lead QFN 5x7 (pin 39 = exposed pad GND, pin 40 unused); bench-fitted", "QFN38", {',
     'part("U5", "Connector_Generic", "Conn_02x20_Odd_Even", "LT8705AIUHF#PBF buck-boost controller, I grade (-40 to 125 C junction, 8705af p.6 Note 3), 38-lead QFN 5x7 (pin 39 = exposed pad GND, pin 40 unused); bench-fitted", "QFN38", {'),
    ('"39": "GND", "40": "NC"}, "C674164")',
     '"39": "GND", "40": "NC"}, "C674169")   # L4-E7 (MESHSAT-1357): the I grade, LCSC C674169 (was C674164, the E grade); v2/docs/records/l4e7/L4E7-STAGE-SETTINGS.md'),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
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


# NOT RELEASED: task L4-E7 drafts these values for board E's generator owner and never applies them. Writing the
# repository's own gen_sch_e.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and
# names an accepted check of L4-E7 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be
# written (the tests do, on scratch copies).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_e.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; L4-E7's values wait on an accepted check")
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
