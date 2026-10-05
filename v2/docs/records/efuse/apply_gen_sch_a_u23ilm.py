#!/usr/bin/env python3
"""apply_gen_sch_a_u23ilm.py: DRAFT for board A's generator owner (record efuse, round 2, finding EF-F03, MESHSAT-1357, 5 October
2026; the independent check V6's minor m6). NOT APPLIED to the tree by record efuse; its author ran it only on scratch copies.

The defect (EF-F03, judged by EF-F01's rule): U23, the TPS259631 eFuse that feeds board D's 5 V (+5V_D8IN to +5V_D8, J_MEZZ_PWR1),
sets its current limit with R98 = 453 Ohm 1 %, labelled "2.0 A". 453 Ohm is TI SLVSET8A's recommended minimum itself (7.3, p.5:
RILM 453 to 7869 Ohm), so the resistor's corners (1 % and 100 ppm/K over -20 to +85 C) reach 445.8 Ohm, outside the recommended
range, and the band's top 2.1816 A is above the switch's 2 A continuous rating (p.5). Round 1 read it PASS (EDGE); the same rule
that made EF-F01 a defect (a setting outside the printed recommended range) makes this one a defect at its corners.

The correction, one component's value: R98 511 Ohm 1 % (the record's own suggestion, EF-O03 of round 1): Equation 5 gives
1.7783 A nominal; the band by the sheet's +-10.4 % across process, voltage and temperature and the resistor's corners is 1.5684 to
1.9949 A (efuse_check.py out 4): its foot over board D's demand (l9pwr's HIGH, 3.30 W at 4.9019 V behind 0.131 Ohm, 0.6858 A) and
its top under the switch's 2 A and the JST VH's 10 A. The label follows the value; the +5V_D8 note that names the old resistor is
restated. The rail's declared 2.0 A peak is NOT changed here (the generator owner's; it is conservative for the copper).
Order: after board A's pending drafts (efuse_check.py ORDER["a"]); no other draft touches U23's call.

Usage:  apply_gen_sch_a_u23ilm.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_a_u23ilm"
EDITS = [
    ('efuse("U23", "+5V_D8IN", "+5V_D8", "D8_EN", "D8_FLT", ["C102", "R98", "R99", "R100", "R101", "C103"], "453R 1% (ILM: 2.0 A)", ovlo_top="40.2k 1%", ovlo_lcsc="C12447");',
     '# record efuse (round 2, EF-F03, 5 October 2026): R98 511 R, 1.7783 A nominal by SLVSET8A Equation 5, 1.568 to 1.995 A with the\n'
     '# sheet\'s +-10.4 % and the resistor\'s corners; 453 R was the recommended minimum itself, its corners outside it (v2/docs/records/efuse)\n'
     'efuse("U23", "+5V_D8IN", "+5V_D8", "D8_EN", "D8_FLT", ["C102", "R98", "R99", "R100", "R101", "C103"], "511R 1% (ILM: 1.8 A)", ovlo_top="40.2k 1%", ovlo_lcsc="C12447");'),
    ('"The APRS board\'s 5 V behind the eFuse U23 (ILM 453R, 2.0 A), leaving on the mezzanine "',
     '"The APRS board\'s 5 V behind the eFuse U23 (ILM 511R, 1.568 to 1.995 A, record efuse EF-F03), leaving on the mezzanine "'),
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


# Writing the repository's own board A generator is refused until RELEASE.md beside this script reads "released: yes" and
# names one accepted check ("check: <repository path>", whose first line is "accepted: yes"). A copy elsewhere may be written.
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; record efuse's drafts wait on an accepted check")
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
