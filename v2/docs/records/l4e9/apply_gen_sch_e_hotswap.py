#!/usr/bin/env python3
"""apply_gen_sch_e_hotswap.py: DRAFT for board E's generator owner (task L4-E9 fix round, MESHSAT-1357, 2 October 2026). NOT
APPLIED to the tree by L4-E9; it was run only on scratch copies (the tests write scratch copies).

Why (defects D-02 and D-07, the focused check's B1; l4e9_power_path.out sections 4 and 11).
  D-02: with REQ-015's 36 V source, TEST-PLAN M2's CS101 peak (2.83 V) takes DC_P to 38.83 V, past the drawn OVLO minimum,
  37.78 V (R22 100k and R23 6.65k at 1 %, OVLOTH 2.4 to 2.6 V, SNVS452G), so the hot swap may open under the test. R22 100k and
  R23 6.42k, both 0.1 %, put the OVLO at 39.71 / 41.44 / 43.18 V: 0.88 V over the peak and 1.22 V under D10's 44.4 V breakdown
  minimum at 25 C. F1 (58 V DC), U2 and Q2 (60 V), U4 (75 V) and C26 and C27 (re-rated to 50 V) are checked at 43.18 V.
  D-07: at that OVLO maximum the drawn R24 20k gives the power limit a sense voltage of 4.7429 mV, under the 5 mV SNVS452G
  9.2.1.2.3 does not recommend. R24 22k 1 % gives 5.06 mV at its low corner (Equation 9's least RPWR there is 21443 Ohm), and
  the complete hot-short pulse (the limit at its corners times TI's 1.3, for the timer's maximum 8.16 ms) sits inside Q7's
  Figure 10 line at 43.18 V derated to its 94.3 C case: 0.675 A against 0.913 A.

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else: R22's and R23's value texts (0.1 %, the new R23), R24's value
text (22k 1 %), and U6's value text (its OVLO); a comment line. The 0.1 % parts need LCSC codes (register R-116, Layer 6).

Usage:  apply_gen_sch_e_hotswap.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_hotswap"
EDITS = [
    ('r("R20", "100k 1%", "DC_P", "HS_UVLO"); r("R21", "38.3k 1% (UVLO: 9 V)", "HS_UVLO", "GND_V"); r("R22", "100k 1%", "DC_P", "HS_OVLO"); r("R23", "6.65k 1% (OVLO: 40 V)", "HS_OVLO", "GND_V")',
     '# L4-E9 (MESHSAT-1357, D-02 and D-07): the OVLO clear of CS101 at 36 V (R22 and R23 at 0.1 %) and the power limit at 5 mV or more at 43.18 V.\n'
     'r("R20", "100k 1%", "DC_P", "HS_UVLO"); r("R21", "38.3k 1% (UVLO: 9 V)", "HS_UVLO", "GND_V"); r("R22", "100k 0.1%", "DC_P", "HS_OVLO"); r("R23", "6.42k 0.1% (OVLO: 41.4 V)", "HS_OVLO", "GND_V")'),
    ('r("R24", "20k (PWR: power limit)", "HS_PWR", "GND_V")',
     'r("R24", "22k 1% (PWR: power limit, 5.06 mV at 43.18 V at its low corner)", "HS_PWR", "GND_V")'),
    ('"LM5069MM-2 hot-swap controller: 9 V on, 40 V off, current and power limit"',
     '"LM5069MM-2 hot-swap controller: 9 V on, 41.4 V off, current and power limit"'),
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
