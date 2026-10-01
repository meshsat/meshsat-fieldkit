#!/usr/bin/env python3
"""apply_lcsc_fill_r12.py: DRAFT for board A's generator owner (task L4-E6, MESHSAT-1357, 1 October 2026). NOT APPLIED to
the tree by L4-E6; its author ran it only on scratch copies with --check (and --write on copies in the tests).

What it changes in v2/ecad/tools/lcsc_fill.py, and nothing else: one MAP line, so the value apply_gen_sch_a_r12.py gives
R12, "12mOhm 1% 2512 (CS)", is bought as Milliohm HoJLR2512-3W-12mR-1%, LCSC C2904242 (JLCPCB's catalogue reading of L4-E4,
v2/docs/records/l4e4/inputs/jlc-search-hojlr2512-3w-2026-10-01.json: stock 3,407 on 1 October 2026). Its sheet is the held
HoJLR2512 series sheet (v2/vendor/passives/milliohm-hojlr2512-series.pdf: 3 W from 0.5 to 500 mOhm, +-1 %, 50 ppm/K). No
other value on any board reads "12mOhm 1% 2512" today, so the line changes no other part.

Usage:  apply_lcsc_fill_r12.py TARGET [--check | --write]     (default --check: nothing is written)
The old text must occur exactly once and the new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, or the change is already applied)."""
import ast
import difflib
import sys

ANCHOR = ' (r"^5mOhm 1% 2512", "R_2512"): "C500739",    # LR2512D-3W-5mR-1%, 3 W, stock 15,156 (CS, RSR, the slot shunts)\n'
EDITS = [
    (ANCHOR,
     ANCHOR + ' (r"^12mOhm 1% 2512", "R_2512"): "C2904242",  # HoJLR2512-3W-12mR-1%, 3 W, stock 3,407 on 1 Oct 2026 (board A\'s'
     ' FE CS shunt R12, L4-E6, MESHSAT-1357)\n'),
]


def refuse(msg):
    sys.stderr.write("apply_lcsc_fill_r12: %s; refusing\n" % msg)
    sys.exit(3)


def patched(text):
    new = text
    for old, rep in EDITS:
        added = rep[len(old):]
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(added) != 0:
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/lcsc_fill.py", "b/lcsc_fill.py", n=0))
    if not write:
        print("apply_lcsc_fill_r12: CHECK OK, %d edit(s), nothing written" % len(EDITS))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep[len(old):]) != 1 for old, rep in EDITS):
        refuse("the written file does not read back as the patched text")
    ast.parse(back)
    print("apply_lcsc_fill_r12: WRITTEN, %d edit(s)" % len(EDITS))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
