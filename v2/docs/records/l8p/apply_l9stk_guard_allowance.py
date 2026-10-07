#!/usr/bin/env python3
"""apply_l9stk_guard_allowance.py: DRAFT for record l9stk's owner (Layer 8 record l8p, MESHSAT-1357, round 11, 7 October 2026; finding
L8P-R9-F2, register row L4A-68). NOT APPLIED by this record: record l9stk's page is its owner's, and its section 15.9 (rounds 4 and 5,
branch fnd/l9stk2 at bb6d2c8f) is not yet in this tree's L9-STACKUPS.md; the integrator runs this script once that section is merged.

What it restates: record l9stk 15.9 allows round 8's single-path guard 30 uA on DOCK_EN_OUT. Record l8p's fail-safe delta (round 9,
apply_gen_sch_a_thgfs.py, change-list row R-244) draws at most 40 uA with the guard cold and 50 uA tripped (record l8p 10c: printed
maxima, the off leakage at the doubling, the worst single fault) and splits U61's input capacitor into C261 and C268, 330 nF each.
Three edits, each keeping the round's own figure as its history:
  E1  the supply bullet's "against the 30 uA this round allows the guard." gains the restatement after it;
  E2  the acceptance item "The guard's draw at most 30 uA; ..." names the delta's 40 and 50 uA and its 0.66 uF;
  E3  the correction-scope table's Layer 5 row names the delta's figures and Layer 5's own text (record l8p's
      apply_pcb_interfaces_guard_allowance.py).
The replay of the rows resting on the allowance is record l4e11's round 19 (l4e11_rowc.out) and record l8p's round 11 (l8p_cprot.out).

Usage:  apply_l9stk_guard_allowance.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the page's 15.9 heading and every
table row's cell count must read back unchanged.
Exit 0: checked (or written); 3: refused (the target is not the expected text or the change is already applied)."""
import difflib
import re
import sys

NAME = "apply_l9stk_guard_allowance"
HEADING = "### 15.9 The guard round: three approaches on printed figures, the selection and its correction scope"

_OLD_1 = "  maxima, against the 30 uA this round allows the guard.\n"
_NEW_1 = ("  maxima, against the 30 uA this round allows the guard.\n"
          "  **Restated (record l8p round 11, 7 October 2026; L8P-R9-F2):** with record l8p's fail-safe delta (two guard paths,\n"
          "  `apply_gen_sch_a_thgfs.py`, change-list row R-244) the guard's draw on DOCK_EN_OUT is at most 40 uA cold and 50 uA tripped\n"
          "  (record l8p 10c: printed maxima, the off leakage at the doubling, the worst single fault), in place of the 30 uA this round\n"
          "  allows round 8's single path; its input capacitance is C261 and C268, 330 nF each; path 2's regulator and switch load VBAT,\n"
          "  not the loop. The rows that rest on it are replayed in record l4e11's round 19 and record l8p's round 11.\n")
_OLD_2 = "  - The guard's draw at most 30 uA; the regulator's input capacitor under 14.1 uF (FM1's cycle).\n"
_NEW_2 = ("  - The guard's draw at most 30 uA (round 8's single path; with record l8p's delta at most 40 uA cold and 50 uA tripped,\n"
          "    record l8p 10c, restated in its round 11); the regulator's input capacitor under 14.1 uF (FM1's cycle; the delta's C261 and\n"
          "    C268, 0.66 uF in all).\n")
_OLD_3 = ("| Layer 5 | DOCK_EN_OUT's load on board A gains 30 uA; DOCK_EN_RET may be held at ground by board A's guard as by board P's "
          "detector |\n")
_NEW_3 = ("| Layer 5 | DOCK_EN_OUT's load on board A gains 30 uA (round 8's single path; with record l8p's delta 40 uA cold and 50 uA "
          "tripped, record l8p 10c, restated in its round 11, Layer 5's own text in record l8p's `apply_pcb_interfaces_guard_allowance.py`); "
          "DOCK_EN_RET may be held at ground by board A's guard as by board P's detector |\n")
EDITS = [(_OLD_1, _NEW_1), (_OLD_2, _NEW_2), (_OLD_3, _NEW_3)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def table_shape(text):
    return [l.count("|") for l in text.splitlines() if l.startswith("|")]


def patched(text):
    if HEADING not in text:
        refuse("record l9stk's section 15.9 is not in the target (rounds 4 and 5, fnd/l9stk2 at bb6d2c8f, are not merged here)")
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if text.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once: %r" % (new.count(old), old[:70]))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    if new.count(HEADING) != 1 or table_shape(new) != table_shape(text):
        refuse("the result does not read back: the heading or a table row's cells moved")
    if any(re.search("[\\u2013\\u2014]", rep) for _o, rep in EDITS):
        refuse("a dash crept into the new text")
    return new


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    text = open(target, encoding="utf-8").read()
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/L9-STACKUPS.md", "b/L9-STACKUPS.md", n=0))
    if not write:
        print("%s: CHECK OK, %d edit(s), nothing written" % (NAME, len(EDITS)))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep) != 1 for _o, rep in EDITS):
        refuse("the written file does not read back as the patched text")
    print("%s: WRITTEN, %d edit(s)" % (NAME, len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
