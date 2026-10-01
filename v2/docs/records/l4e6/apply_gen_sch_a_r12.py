#!/usr/bin/env python3
"""apply_gen_sch_a_r12.py: DRAFT for board A's generator owner (task L4-E6, MESHSAT-1357, 1 October 2026). NOT APPLIED to
the tree by L4-E6; its author ran it only on scratch copies with --check (and --write on copies in the tests).

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else: the front end's (U2, LM5176) call gets
  - rcs="12m": the cycle-by-cycle sense resistor R12 from the lm5176() default 5 mOhm to 12 mOhm, so the boost peak limit is
    8.06 / 10.00 / 11.99 A and the buck valley limit 5.27 / 6.67 / 8.10 A (SNVSAI1D p.7 VCS(BOOST), VCS(BUCK), stacked with the
    HoJLR2512 sheet's +-1 % and 50 ppm/K and the CSG offset; l4e6_fault_handling.out section 5). The netlist then reads R12
    "12mOhm 1% 2512 (CS)", which lcsc_fill.py maps to Milliohm HoJLR2512-3W-12mR-1%, LCSC C2904242, once
    apply_lcsc_fill_r12.py has added that line;
  - cslope=("330p", "C1664"): C147 from 680 pF to 330 pF C0G, SNVSAI1D Equation 26 (p.24) at 12 mOhm, 333 pF, by the same
    at-or-below choice that took 680 pF for the 800 pF of 5 mOhm.
MODE (R119 to VCC, no hiccup) is deliberately left as drawn (L4E6-FAULT-HANDLING.md, the decision).

It is not the whole change. The same circuit round owes: L4-E5's ILIM_HIZ line (H3) on U3 pin 6, which must be in place
before or with this edit (a fixed IIN_HOST of 4.70 A without the line would meet the new peak limit in service below
16.3 V); L4-E4's R11 8 mOhm (apply_gen_sch_a_r11.py, a different line of the same call; the two drafts compose in either
order); the front end's compensation re-verified by the generator's loop check at 12 mOhm (the current loop's gain falls to
0.417 of the drawn); the VBUS20 bank re-sized by the generator's dense node analysis at the chosen highest permitted current
(B-4); the gates and the evidence re-taken on a box. After regeneration r11_dep.py and the L4-E4 to L4-E6 records refuse by
design: they describe the circuit before the change.

Usage:  apply_gen_sch_a_r12.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, or the change is already applied)."""
import ast
import difflib
import sys

EDITS = [
    ('       cslope=("680p", "C30816"), boot_diodes=("D9", "D10"),\n',
     '       cslope=("330p", "C1664"), boot_diodes=("D9", "D10"), rcs="12m",   # L4-E6 (MESHSAT-1357): R12 12 mOhm (Milliohm'
     ' HoJLR2512-3W-12mR-1%, LCSC C2904242 by lcsc_fill.py), boost peak limit 8.06 / 10.00 / 11.99 A under L1\'s Isat; C147 330 pF'
     ' C0G by SNVSAI1D Equation 26 at 12 mOhm (333 pF); MODE stays at VCC; v2/docs/records/l4e6/L4E6-FAULT-HANDLING.md\n'),
]


def refuse(msg):
    sys.stderr.write("apply_gen_sch_a_r12: %s; refusing\n" % msg)
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


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    text = open(target, encoding="utf-8").read()
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_a.py", "b/gen_sch_a.py", n=0))
    if not write:
        print("apply_gen_sch_a_r12: CHECK OK, %d edit(s), nothing written" % len(EDITS))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep) != 1 for _o, rep in EDITS):
        refuse("the written file does not read back as the patched text")
    ast.parse(back)
    print("apply_gen_sch_a_r12: WRITTEN, %d edit(s)" % len(EDITS))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
