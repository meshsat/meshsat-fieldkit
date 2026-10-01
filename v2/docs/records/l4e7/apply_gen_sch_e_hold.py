#!/usr/bin/env python3
"""apply_gen_sch_e_hold.py: DRAFT for board E's generator owner (task L4-E7, MESHSAT-1357, 1 October 2026). NOT APPLIED to
the tree by L4-E7; its author ran it only on scratch copies with --check (the tests also write scratch copies).

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else: the input-voltage hold R8 and R9 (FBIN) keep their drawn
values and ratio, 102k over 7.50k (17.593 V nominal, REQ-016's "the panel held at 17.6 V", which the owner's D-34 keeps), and
become YAGEO RT0603BRD07102KL (LCSC C861068) over RT0603BRD077K5L (LCSC C728597), 0.1 % and 25 ppm/K, in place of 1 % parts
with no order code. Only their tolerance, drift and order codes change: the band at both ends narrows (l4e7_stage_settings.out
section 3). The panel entry keeps its declared 17.6 V and its note; no other line is touched. A lower hold would change
REQ-016 and is not drafted (the page's proposal section, for the owner's ruling).

After any application, l4e_replay.py section 11 refuses by design (it parses R8 and R9 at 1 %), and so do l4e5's and this
record's pins of gen_sch_e.py: those are records of the circuit before the change.

Usage:  apply_gen_sch_e_hold.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_hold"
EDITS = [
    ('r("R8", "102k 1% (RFBIN1: panel point 17.6 V)", "PV_P", "TRK_FBIN"); r("R9", "7.50k 1% (RFBIN2)", "TRK_FBIN", "GND")',
     'r("R8", "102k 0.1% 25ppm (RFBIN1: panel point 17.6 V)", "PV_P", "TRK_FBIN", "R", "C861068"); r("R9", "7.50k 0.1% 25ppm (RFBIN2)", "TRK_FBIN", "GND", "R", "C728597")'
     '   # L4-E7 (MESHSAT-1357): YAGEO RT0603BRD07102KL over RT0603BRD077K5L, the drawn ratio (REQ-016\'s 17.6 V point), 0.1 % and 25 ppm/K; v2/docs/records/l4e7/L4E7-STAGE-SETTINGS.md'),
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
