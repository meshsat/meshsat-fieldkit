#!/usr/bin/env python3
"""apply_gen_sch_b_u24ilm.py: DRAFT for board B's generator owner (record efuse, task T12, MESHSAT-1357, 5 October 2026). NOT
APPLIED to the tree by record efuse; its author ran it only on scratch copies (efuse_check.py and the tests write scratch copies).

The defect (EF-F02, found by this record's inventory beside SDR3-F04): U24, the TPS259631 eFuse that feeds the RockBLOCK 9704
on J_RB9704, sets its current limit with R43 = 301 Ohm, labelled "3.0 A", the same setting as U23: outside TI SLVSET8A's
0.125 to 2 A range and 453 to 7869 Ohm recommendation (pp.1 and 5), so the sheet prints no limit for it; Equation 5's 3.011 A
is an extrapolation three times the one 5 V conductor's 1 A (the IDC socket Wurth 61201623021 and the flat cable Wurth
63911615521CAB each "Rated Current 1 A max.") and six times the module's own input maximum ("at a maximum of 500mA",
Ground Control's hardware page).

The correction, one component's value: R43 1.21 kOhm 1 % (E96; its order code is Layer 6's to select, finding EF-L03). Equation 5
gives 0.7575 A nominal; with the sheet's +-10.4 % across process, voltage and temperature and the resistor's 1 % and an assumed
100 ppm/K over -20 to +85 C, the band is 0.6682 to 0.8496 A (efuse_check.py out 4): above the module's printed 500 mA and
under the conductor's 1 A. The label follows the value and the +5V_RB note, which names the old resistor and its 3.0 A, is
restated. The rail's declared 2.00 A peak is NOT changed here (finding EF-L02: the generator owner's).

Usage:  apply_gen_sch_b_u24ilm.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_b_u24ilm"
EDITS = [
    ('efuse("U24", "+5V_DEV", "+5V_RB", "RB_UVLO", "RB_FLT", ["C61", "R43", "R44", "R45", "R46", "C62"], "301R 1% (ILM: 3.0 A)");',
     '# record efuse (T12, EF-F02, 5 October 2026): R43 1.21 k, 0.7575 A nominal by SLVSET8A Equation 5, 0.668 to 0.850 A with the\n'
     '# sheet\'s +-10.4 % and the resistor\'s corners, over the module\'s 500 mA and under the ribbon conductor\'s 1 A (v2/docs/records/efuse)\n'
     'efuse("U24", "+5V_DEV", "+5V_RB", "RB_UVLO", "RB_FLT", ["C61", "R43", "R44", "R45", "R46", "C62"], "1.21k 1% (ILM: 0.76 A)");'),
    ('note="the satellite modem behind the eFuse U24 (ILM 301R, 3.0 A): the RockBLOCK 9704\'s burst "',
     'note="the satellite modem behind the eFuse U24 (ILM 1.21k, 0.668 to 0.850 A, record efuse): the RockBLOCK 9704\'s burst "'),
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


# Writing the repository's own board B generator is refused until RELEASE.md beside this script reads "released: yes" and
# names one accepted check ("check: <repository path>", whose first line is "accepted: yes"). A copy elsewhere may be written.
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_b.py")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_b.py", "b/gen_sch_b.py", n=0))
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
