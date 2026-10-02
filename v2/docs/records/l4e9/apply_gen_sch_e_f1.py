#!/usr/bin/env python3
"""apply_gen_sch_e_f1.py: DRAFT for board E's generator owner (task L4-E9 round 2, MESHSAT-1357, 2 October 2026). NOT
APPLIED to the tree by L4-E9; it was run only on scratch copies (the tests write scratch copies).

Why (finding E-F2, open item S-107). F1, the vehicle entry's fuse, is a MINI blade of the Littelfuse 297 series the record
held: 32 V DC, 1000 A at 32 V DC (v2/vendor/keystone/littelfuse-297-ficcorp.pdf). The entry admits a steady input up to the
hot swap's OVLO maximum, 42.49 V (s120), so a short behind F1 would ask it to interrupt above its voltage rating.

The part: Littelfuse 0997010.WXN, the MINI series rated 58 V DC, 10 A, interrupting rating 1000 A at 58 V DC (Littelfuse's
datasheet "MINI Series Blade Fuses - Rated 58V", revised 11/18/2025, read at the Internet Archive's snapshot 20251210045250
of the maker's own address and held back by its terms: fetch_held_back.py). Keystone's catalogue page M65 p.42 names the
3568 holder board E carries "For Littelfuse Mini 297 or 997 series", and the sheet gives the same blade size and pitch, so
the land does not change. The conditions verified (l4e9_power_path.out section 11): the DC voltage rating against 42.49 V;
the interrupting rating against the kit cable's prospective current, 561 A at 42.49 V with the copper at -20 C and the
source taken stiff (REQ-015 states no source impedance); the maker's derating table at the next higher column above the
62.1 C inside air (80 C: 7.3 A) against the entry's 6.15 A; the hot swap's start-up I2t against the part's; the
time-current rows against the conductors behind it. The 58 V part's rejection feature works only in a 58 V keyed holder:
the 3568 also takes a 32 V MINI, so the BOM, the label and ASSEMBLY.md name the 0997 (register R-18).

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else: F1's value text names the part and its ratings (the fuse
is a loose part in the holder: no order code is added; procurement is Layer 6's).

Usage:  apply_gen_sch_e_f1.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_f1"
EDITS = [
    ('part("F1", "Device", "Fuse", "10 A mini blade (Keystone 3568 holder): vehicle input", "FUSE", {"1": "DC_IN", "2": "DC_F"})',
     '# L4-E9 (MESHSAT-1357, E-F2): the 58 V DC MINI blade; the 32 V 297 series could not interrupt at the OVLO maximum 42.49 V.\n'
     'part("F1", "Device", "Fuse", "Littelfuse 0997010.WXN MINI blade 10 A, 58 V DC, 1000 A at 58 V DC (Keystone 3568 holder, which takes the 997 series): vehicle input", "FUSE", {"1": "DC_IN", "2": "DC_F"})'),
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


# NOT RELEASED: task L4-E9 drafts this change for board E's generator owner and never applies it. Writing the repository's
# own gen_sch_e.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an
# accepted check of L4-E9 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written.
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_e.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; L4-E9's change waits on an accepted check")
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
