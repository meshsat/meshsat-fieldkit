#!/usr/bin/env python3
"""apply_gen_sch_a_guard.py: DRAFT for board A's generator owner (task L4-E11, MESHSAT-1357, fix round of 2 October 2026). NOT
APPLIED to the tree by L4-E11; its author ran it only on scratch copies (the tests write scratch copies).

Why (blocker B3 of the focused check cx30, l4e11_power.out section 3f): with REQ-015's 9 V at the kit's plug, the in-service
maximum from a 9.00 V plug settles VIN_RAW at 8.15 V (the kit's own losses hot), so L4-E5's knee moves down (a specification:
a flat 1.82 A from 7.95 V, zero at 7.657 V, HIZ certain below 7.378 V) and the front end's restart guard U34 must fall under the
knee's certain HIZ by L4-E5's 0.1 V. As drawn (R14 91k over R15 10k) it falls at 7.86 / 8.08 / 8.31 V, above the plug's 8.15 V
operating point; R14 76.8k 1 % (LCSC C23107) puts the fall at 6.75 / 6.94 / 7.14 V (0.24 V under 7.378 V) and the rise at
6.89 / 7.08 / 7.28 V (TPS37A VIT 0.792 to 0.808 V, 2 % hysteresis, SNVSBJ1E). At the lowest fall the guard's own running levels
scale to FE_VZ 4.64 V, FE_RUN 2.75 V (Q36 and Q37 need 2.5 V at most) and EN 1.89 V (VEN(OP) 1.29 V at most).

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else: R14's call and its line comment, FE_UVS's declared fraction of
VIN_RAW (10 / 86.8), and the two comment lines that state the guard's thresholds; C212's release text is untouched.

ORDER: apply it with the corrected knee (E11-09), never before it: with the drawn knee the plug's 9 V settles VIN_RAW on the
knee and the guard's position does not matter, but the knee drawn to the specification needs this guard under it.

Usage:  apply_gen_sch_a_guard.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_a_guard"
EDITS = [
    ('r("R14", "91k 1%", "VIN_RAW", "FE_UVS", lcsc="C23265")',
     'r("R14", "76.8k 1% (guard under the L4-E11 knee)", "VIN_RAW", "FE_UVS", lcsc="C23107")'),
    ('# channel 2 (UV): 8.08 V falling, 8.24 V rising',
     '# channel 2 (UV): 6.94 V falling, 7.08 V rising (L4-E11)'),
    ('_intent.node("FE_UVS", round(_GVIN * 10 / 101, 2), _gw + "SENSE2, VIN_RAW over R14 / R15 (10 / 101 of it)")',
     '_intent.node("FE_UVS", round(_GVIN * 10 / 86.8, 2), _gw + "SENSE2, VIN_RAW over R14 / R15 (10 / 86.8 of it)")'),
    ("#  Channel 2 (UV) is the stage's UVLO now: R14 91 k over R15 10 k (the old UVLO pair, re-valued) put VIN_RAW's\n"
     "#   threshold at 7.86 / 8.08 / 8.31 V falling and 8.01 / 8.24 / 8.48 V rising, under the 9 V service floor; C212",
     "#  Channel 2 (UV) is the stage's UVLO now: R14 76.8 k over R15 10 k (L4-E11, under the corrected knee) put VIN_RAW's\n"
     "#   threshold at 6.75 / 6.94 / 7.14 V falling and 6.89 / 7.08 / 7.28 V rising, under the knee's certain HIZ (7.378 V); C212"),
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


# NOT RELEASED: task L4-E11 drafts this value for board E's generator owner and never applies it. Writing the repository's
# own gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an
# accepted check of L4-E11 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written
# (the tests do, on scratch copies).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
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
