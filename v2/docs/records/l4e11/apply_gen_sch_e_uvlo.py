#!/usr/bin/env python3
"""apply_gen_sch_e_uvlo.py: DRAFT for board E's generator owner (task L4-E11, MESHSAT-1357, 2 October 2026). NOT APPLIED to
the tree by L4-E11; its author ran it only on scratch copies (the tests write scratch copies).

Why (finding U4-F2 of L4E11-SOURCE-ONLY-AND-ENTRY.md, l4e11_power.out section 3): REQ-015 asks the vehicle and shore input
to operate from 9 V. The LM5069's UVLO turns the entry on at UVLOTH x (1 + R20 / R21), with UVLOTH 2.45 / 2.5 / 2.55 V
(SNVS452G p.5) and R20 100k over R21 38.3k at 1 %: 8.72 / 9.03 / 9.34 V. At its nominal and upper corners a 9.00 V source
never turns the entry on, before any current flows. R21 42.2k 1 % puts the rising threshold at 8.14 / 8.42 / 8.71 V, under
9.00 V by 0.29 V at its maximum, and the falling one at 5.11 / 6.32 / 7.53 V, under H3's knee (8.71 V) and the restart guard
(7.86 V at its lowest falling). Nothing on DC_P draws power before the hot swap turns on, so the source's voltage is the
UVLO's. U6's value text follows it.

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else: R21's value text and U6's value text.

ORDER: apply it AFTER L4-E9's apply_gen_sch_e_hotswap.py (R22, R23, R24 and U6's OVLO; L4-E9's release order step 4e). That
draft replaces the whole R20 to R23 line by its old text, which carries R21's drawn value, so it refuses once this one has
run; this one edits R21's own text and the "9 V on," part of U6's, which both of L4-E9's states keep.

Usage:  apply_gen_sch_e_uvlo.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_uvlo"
EDITS = [
    ('r("R21", "38.3k 1% (UVLO: 9 V)", "HS_UVLO", "GND_V")',
     'r("R21", "42.2k 1% (UVLO: on by 8.71 V, L4-E11)", "HS_UVLO", "GND_V")'),
    ('"LM5069MM-2 hot-swap controller: 9 V on, ',
     '"LM5069MM-2 hot-swap controller: on by 8.71 V, '),
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
# own gen_sch_e.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an
# accepted check of L4-E11 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written
# (the tests do, on scratch copies).
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
