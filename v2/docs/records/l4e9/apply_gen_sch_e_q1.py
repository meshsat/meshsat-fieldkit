#!/usr/bin/env python3
"""apply_gen_sch_e_q1.py: DRAFT for board E's generator owner (task L4-E9, MESHSAT-1357, 1 October 2026). NOT APPLIED to the
tree by L4-E9; it was run only on scratch copies (the tests write scratch copies).

Why. L4-E5 raises the tracker's output ceiling to 28.28 / 29.21 / 30.15 V (R10 232 k). The tracker then back-feeds DC_P
through the hot swap Q7's body diode (L4-E5's finding: Q7's source on DC_HS, its drain on HS_S). A reversed vehicle input,
which REQ-015's acceptance asks the entry to take without damage, puts DC_F at -36 V while DC_P holds up to 30.15 V, so the
vehicle entry's ideal-diode FET Q1 stands off up to 66.15 V (the body diode's drop taken as zero, an upper bound;
l4e9_power_path.out section 7). Q1 is a BSC039N06NS, 60 V (Infineon Rev.2.4 p.1). As drawn, with the 15.56 V ceiling, the
same reverse is 51.56 V. The LM74700-Q1 that drives Q1 stays inside its ratings at 66.15 V: CATHODE to ANODE 75 V absolute,
ANODE to CATHODE -70 V recommended (TI SNOSD17G 6.1, 6.3).

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else (two edits inside the helper and above it; the call lines
are untouched, so it composes in either order with d8dec31's apply_gen_sch_e_cin.py, which anchors on the call):
  1. a module constant _ENTRY_FET: the CSD19532Q5B, 100 V (TI SLPS414B p.1, held as v2/vendor/power/ti-csd19532q5b-n-fet.pdf),
     LCSC C473333, the code Q7 carries;
  2. ideal_diode() takes an optional fet=(value, lcsc) and uses _ENTRY_FET when its anode is DC_F, the vehicle entry; the
     FET is then drawn by nfet() on the PowerPAK SO-8 / 5x6 SON land ("PPAK") that Q7 already uses. Every other call is drawn
     exactly as before: the tracker's U4/Q2 keeps its BSC039N06NS, which stands off at most the vehicle's OVLO maximum,
     42.49 V, against 60 V.
The land changes (TDSON-8 to the PPAK map: pads 1 to 3 source, 4 gate, 5 the drain tab), so the placement and the layout
constraints of DECISION-31 section 7 (D10 at F1's far pad, Q1 beside it) are the generator owner's to re-seat.

Usage:  apply_gen_sch_e_q1.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_q1"
EDITS = [
    ("def ideal_diode(uref, qref, cref, rref, anode, cathode, gnd):",
     '# L4-E9 (MESHSAT-1357): the vehicle entry\'s ideal-diode FET. With L4-E5\'s raised tracker ceiling a reversed 36 V input\n'
     '# stands off up to 66.15 V across it (DC_P back-fed through Q7\'s body diode), over the BSC039N06NS\'s 60 V; the CSD19532Q5B\n'
     '# (100 V, the part and code Q7 carries) on Q7\'s PPAK land. v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md, section 5.\n'
     '_ENTRY_FET = ("CSD19532Q5B 100 V N-FET (4.6 mOhm at VGS 6 V, PowerPAK SO-8 / SON-8 5x6), the vehicle entry\'s ideal diode: '
     'a reversed 36 V input with DC_P back-fed from the raised tracker ceiling stands off up to 66.15 V across it (L4-E9)", "C473333")\n'
     "def ideal_diode(uref, qref, cref, rref, anode, cathode, gnd, fet=None):"),
    ('    part(qref, "Transistor_FET", "IRF7404", "BSC039N06NS 60 V 3.9 mOhm N-FET (PG-TDSON-8: 1-3 S, 4 G, 5-8 D)", "TDSON8",',
     '    fet = fet or (_ENTRY_FET if anode == "DC_F" else None)   # the vehicle entry only; the tracker\'s U4/Q2 is unchanged\n'
     '    if fet:\n'
     '        nfet(qref, fet[0], qref + "_G", cathode, anode, lcsc=fet[1])\n'
     '    else:\n'
     '        part(qref, "Transistor_FET", "IRF7404", "BSC039N06NS 60 V 3.9 mOhm N-FET (PG-TDSON-8: 1-3 S, 4 G, 5-8 D)", "TDSON8",'),
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
