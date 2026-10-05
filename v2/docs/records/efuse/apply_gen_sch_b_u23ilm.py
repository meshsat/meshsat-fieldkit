#!/usr/bin/env python3
"""apply_gen_sch_b_u23ilm.py: DRAFT for board B's generator owner (record efuse, task T12, MESHSAT-1357, 5 October 2026). NOT
APPLIED to the tree by record efuse; its author ran it only on scratch copies (efuse_check.py and the tests write scratch copies).

The defect (EF-F01, from SDR3-F04): U23, the TPS259631 eFuse that feeds the LimeSDR Mini 2.4 on J_LIME, sets its current limit
with R36 = 301 Ohm, labelled "3.0 A". TI SLVSET8A prints the adjustable range 0.125 to 2 A (p.1), recommends RILM 453 to
7869 Ohm and rates the switch for 2 A continuous (p.5, 7.3): at 301 Ohm the sheet prints no limit, no tolerance and no
behaviour, and Equation 5's 3.011 A is an extrapolation above the receptacle's 1.8 A (Wurth 692122030100).

The correction, one component's value: R36 750 Ohm 1 %, the value and code board A's U21 already carries (UNI-ROYAL, LCSC
C23241, +-100 ppm/K by Layer 6's catalogue reading). Equation 5 gives 1.2152 A nominal; with the sheet's +-10.4 % across
process, voltage and temperature (Features and Figure 21) and the resistor's 1 % and 100 ppm/K over -20 to +85 C, the band is
1.0781 to 1.3550 A (efuse_check.py out 4): at or above the LimeSDR's printed demand (4.5 W at C-DEV rev 1's 4.9019 V behind
the eFuse's 0.131 Ohm, 0.9417 A; the host's 900 mA) and at or below the receptacle's 1.8 A and the switch's 2 A. The label
in the call follows the value; the +5V_LIME note and the _DEV_LOADS comment, which name the old resistor and its 3.0 A, are
restated. The rail's declared 1.2 A typical and 3.0 A peak are NOT changed here (finding EF-L01: the generator owner's).

Usage:  apply_gen_sch_b_u23ilm.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_b_u23ilm"
EDITS = [
    ('efuse("U23", "+5V_DEV", "+5V_LIME", "LIME_UVLO", "LIME_FLT", ["C56", "R36", "R37", "R38", "R39", "C57"], "301R 1% (ILM: 3.0 A)");',
     '# record efuse (T12, EF-F01, 5 October 2026): R36 750 R, 1.2152 A nominal by SLVSET8A Equation 5, 1.078 to 1.355 A with the\n'
     '# sheet\'s +-10.4 % and the resistor\'s corners; 301 R was below the 453 to 7869 Ohm the sheet recommends (v2/docs/records/efuse)\n'
     'efuse("U23", "+5V_DEV", "+5V_LIME", "LIME_UVLO", "LIME_FLT", ["C56", "R36", "R37", "R38", "R39", "C57"], "750R 1% (ILM: 1.2 A)");'),
    ('note="the software-defined radio bay behind the eFuse U23 (ILM 301R, 3.0 A): a LimeSDR Mini 2.4 "',
     'note="the software-defined radio bay behind the eFuse U23 (ILM 750R, 1.078 to 1.355 A, record efuse): a LimeSDR Mini 2.4 "'),
    ('# eFuse -> +5V_LIME, the LimeSDR Mini 2.4 (the eFuse\'s ILM is 3.0 A)',
     '# eFuse -> +5V_LIME, the LimeSDR Mini 2.4 (the eFuse\'s ILM is 750R, 1.078 to 1.355 A)'),
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
