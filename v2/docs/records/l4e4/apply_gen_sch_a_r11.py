#!/usr/bin/env python3
"""apply_gen_sch_a_r11.py: DRAFT for board A's generator owner (task L4-E4, MESHSAT-1357, 1 October 2026). NOT APPLIED to
the tree by L4-E4; its author ran it only on scratch copies with --check.

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else: the front end's ISNS shunt R11 from the lm5176() default
10 mOhm (lcsc_fill.py's C2903468) to 8 mOhm with its own order code, Milliohm HoJLR2512-3W-8mR-1%, LCSC C2904240, the value
l4e4_limits.py chose together with U3's IIN_HOST of 4.70 A (code 94; its second round, R16's tolerance included;
L4E4-CURRENT-LIMITS.md). The netlist then reads R11 "8mOhm 1% 2512 (ISNS)".

It is not the whole change. The same circuit round owes, beside it: the firmware's IIN_HOST 4.70 A (REG0x0F/0E 0x5E00)
with RSNS_RAC = 0b and A-2's VIN_RAW rule; the re-declarations of VBUS20, FE_OUT and VIN_RAW at the window-sized currents
and the generator's own VBUS20 node analysis at the new highest permitted current, 7.262 A (B-3, B-4); L1 and the FETs
rated for that current, or hiccup as a candidate whose peak current and ripple pass item 4's criteria (B-1, B-2);
pcb_sensitive.yaml's FE_ISNS text; Kelvin taps within 0.38 mOhm at 25 C (C-1); a box regeneration with the gates and the
evidence re-taken. After regeneration r11_dep.py refuses by design (its netlist facts describe the held 10 mOhm circuit),
and l4e4_limits.py's section 0 with it: both are records of the circuit before this change.

Usage:  apply_gen_sch_a_r11.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named while these values are PROVISIONAL: see RELEASE.md below)."""
import ast
import os
import difflib
import sys

EDITS = [
    ('       cs_filter=("R150", "R151", "C123"), isns_filter=("R160", "R161", "C128"), cin="10u 100V X7R 1210", l_lcsc="C6358489",\n',
     '       cs_filter=("R150", "R151", "C123"), isns_filter=("R160", "R161", "C128"), isns="8m", isns_lcsc="C2904240", cin="10u 100V X7R 1210",'
     ' l_lcsc="C6358489",   # L4-E4 (MESHSAT-1357): R11 8 mOhm, Milliohm HoJLR2512-3W-8mR-1% (LCSC C2904240), coordinated with U3\'s'
     ' IIN_HOST 4.70 A; v2/docs/records/l4e4/L4E4-CURRENT-LIMITS.md\n'),
]


def refuse(msg):
    sys.stderr.write("apply_gen_sch_a_r11: %s; refusing\n" % msg)
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
        print("apply_gen_sch_a_r11: CHECK OK, %d edit(s), nothing written" % len(EDITS))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep) != 1 for _o, rep in EDITS):
        refuse("the written file does not read back as the patched text")
    ast.parse(back)
    print("apply_gen_sch_a_r11: WRITTEN, %d edit(s)" % len(EDITS))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
