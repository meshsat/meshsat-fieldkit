#!/usr/bin/env python3
"""apply_gen_sch_a_r138.py: DRAFT for board A's generator owner (task L4-E4, MESHSAT-1357, 1 October 2026). NOT APPLIED to
the tree by L4-E4; its author ran it only on scratch copies with --check.

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else: the USB-C outlet's OCP sense R138 (DR-03) from 10 mOhm to
TI's recommended 5 mOhm (SLVSDG8B 8.3.8.2 p.31) with its own order code, Milliohm HoJLR2512-3W-5mR-1%, LCSC C2903482 (the
held HoJLR2512 series sheet is its datasheet), a two-line comment naming the record, and the PD_SW intent note's "10 mOhm"
for R138. The netlist then reads R138 "5mOhm 1% 2512 (ISNS)" with the trip at 3.79 to 4.58 A (l4e4_limits.out 3).

Owed beside it in the same round: R138's two taps (U18 pin 19 ISNS on PD_SW, pin 21 VBUS on PD_VBUS) declared for
kelvin_check in pcb_sensitive.yaml within 1.15 mOhm at 25 C; a box regeneration with the gates and the evidence re-taken;
the bench procedure of l4e4_limits.out section 3: (a) U19 held in shutdown and a regulated supply on PD_VPWR, U18's
differential sense voltage, VBUS and PD_GDNG recorded, the threshold demonstrated in 19.2 to 22.6 mV with VBUS inside the
contract's hold window; (b) 3 A held on each advertised voltage with U19 in the path.

Usage:  apply_gen_sch_a_r138.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named while these values are PROVISIONAL: see RELEASE.md below)."""
import ast
import os
import difflib
import sys

EDITS = [
    ('nfet("Q27", "CSD18510Q5B 40 V N-FET (VBUS switch)", "PD_GDNG", "PD_VPWR", "PD_SW"); r("R138", "10mOhm 1% 2512 (ISNS)", "PD_SW", "PD_VBUS", "RS2512");',
     '# L4-E4 (MESHSAT-1357, DR-03): R138 at TI\'s recommended 5 mOhm (SLVSDG8B 8.3.8.2 p.31), Milliohm HoJLR2512-3W-5mR-1% (LCSC\n'
     '# C2903482): the trip at 3.79 to 4.58 A over VI(TRIP) 19.2 to 22.6 mV, above every 3 A PDO; v2/docs/records/l4e4/L4E4-CURRENT-LIMITS.md\n'
     'nfet("Q27", "CSD18510Q5B 40 V N-FET (VBUS switch)", "PD_GDNG", "PD_VPWR", "PD_SW"); r("R138", "5mOhm 1% 2512 (ISNS)", "PD_SW", "PD_VBUS", "RS2512", "C2903482");'),
    ('on its way to the outlet\'s own 10 mOhm ISNS "', 'on its way to the outlet\'s own 5 mOhm ISNS "'),
]


def refuse(msg):
    sys.stderr.write("apply_gen_sch_a_r138: %s; refusing\n" % msg)
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


# PROVISIONAL (1 October 2026, the owner's instruction): the values wait on the source-control decision (L4-E5) and the
# fault-handling decision (L4-E6). Writing the repository's own board A generator is refused until RELEASE.md beside this
# script reads "released: yes" and names an accepted check of each ("source-control: <check record>", "fault-handling:
# <check record>", each a repository path whose first line is "accepted: yes"). A copy elsewhere may be written (tests).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("PROVISIONAL: no RELEASE.md: the source-control (L4-E5) and fault-handling (L4-E6) decisions have not released these values")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes": refuse("PROVISIONAL: RELEASE.md's first line is not 'released: yes'")
    for key in ("source-control", "fault-handling"):
        rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith(key + ":")]
        if len(rec) != 1: refuse("PROVISIONAL: RELEASE.md names no single %s check" % key)
        path = os.path.join(REPO, rec[0])
        if ".." in rec[0].split("/") or not os.path.isfile(path): refuse("PROVISIONAL: %s check %s is not in this tree" % (key, rec[0]))
        if open(path, encoding="utf-8").readline().rstrip("\n") != "accepted: yes":
            refuse("PROVISIONAL: %s check %s is not accepted" % (key, rec[0]))


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
        print("apply_gen_sch_a_r138: CHECK OK, %d edit(s), nothing written" % len(EDITS))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep) != 1 for _o, rep in EDITS):
        refuse("the written file does not read back as the patched text")
    ast.parse(back)
    print("apply_gen_sch_a_r138: WRITTEN, %d edit(s)" % len(EDITS))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
