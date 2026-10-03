#!/usr/bin/env python3
"""Close register row R-197 (L4-RC01) through its integrator's hook (MESHSAT-1357, set 28, 4 October 2026).

R-197's acceptance: it closes only when L4-E7's guard round (fnd/l4e7rc) is integrated and its tests pass; the hook says to set the
State to CLOSED and write "the integration commit `<sha>`" and the passing test line as run.py prints it. The evidence, read on this
line: the guard round is integrated at the merge c4e4f7d7 (an ancestor of HEAD, asserted below); after set 28's final freeze
re-keyed L4-E7's results cache, `run.py test_l4e7 test_public_hygiene` on the frozen line f67ea9cf printed
"tests: 54 passed, 0 failed, 1 skipped" (the skip is the gated L4E7_RECOMPUTE test). This script writes that evidence into the row,
sets its State and next action as R-198's CLOSED row reads, and restates R-197's state where the register's header, L4-E9's page
and its README carry it, with the page's state counts (OPEN 1 to 0, CLOSED 1 to 2). It changes no figure and no other row.
Each old text must occur exactly once; a second run is refused. Run from the repository root; then regenerate L4-E9 through
regen_out (the freeze helper) and the later stage."""
import os
import re
import subprocess
import sys

REG = "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"
PAGE = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
README = "v2/docs/records/l4e9/README.md"
MERGE = "c4e4f7d7"
FROZEN = "f67ea9cf"
LINE = "tests: 54 passed, 0 failed, 1 skipped"


def refuse(msg):
    print("apply_close_r197: REFUSED: %s" % msg)
    sys.exit(1)


def once(t, old, new, where):
    if t.count(old) != 1:
        refuse("%s: %d occurrence(s) of %r, one expected" % (where, t.count(old), old[:80]))
    return t.replace(old, new)


def main():
    if not os.path.exists(REG):
        refuse("run from the repository root")
    for c in (MERGE, FROZEN):
        if subprocess.run(["git", "merge-base", "--is-ancestor", c, "HEAD"]).returncode != 0:
            refuse("%s is not an ancestor of HEAD" % c)
    reg = open(REG, encoding="utf-8").read()
    row = [l for l in reg.split("\n") if l.startswith("| R-197 |")]
    if len(row) != 1:
        refuse("%d R-197 row(s)" % len(row))
    cells = row[0].split(" | ")
    if cells[6].strip() != "OPEN":
        refuse("R-197's State reads %r: already closed?" % cells[6])
    r198 = [l for l in reg.split("\n") if l.startswith("| R-198 |")][0].split(" | ")
    hook = "(\"tests: N passed, 0 failed, ...\")"
    if hook not in cells[5]:
        refuse("R-197's acceptance does not carry the hook")
    cells[5] = cells[5] + (" Closed at set 28's integration (4 October 2026): the integration commit `%s` (L4-E7's guard round "
                           "`fnd/l4e7rc` at `8259c26e`); after set 28's final freeze re-keyed L4-E7's results cache, `run.py test_l4e7 "
                           "test_public_hygiene` on the frozen line `%s` printed \"%s\" (the skip is the gated L4E7_RECOMPUTE test)."
                           % (MERGE, FROZEN, LINE))
    cells[6] = "CLOSED"
    cells[9] = r198[9]
    reg = reg.replace(row[0], " | ".join(cells))
    reg = once(reg, "`fnd/l4e7rc` integrated at `c4e4f7d7`, OPEN until `test_l4e7` passes there, which waits on L4-E7's results cache "
                    "being regenerated;",
               "`fnd/l4e7rc` integrated at `c4e4f7d7`, CLOSED on `test_l4e7` passing on set 28's frozen line `%s` (\"%s\");"
               % (FROZEN, LINE), REG)
    page = open(PAGE, encoding="utf-8").read()
    page = once(page, "CLOSED 1; DRAFTED 2; OPEN 1; OWED 8; APPLIED 0", "CLOSED 2; DRAFTED 2; OPEN 0; OWED 8; APPLIED 0", PAGE)
    page = once(page, "R-197 OPEN, R-198 CLOSED", "R-197 and R-198 CLOSED", PAGE)
    rd = open(README, encoding="utf-8").read()
    rd = once(rd, "and OPEN until\n`test_l4e7` passes at the guard round's integration `c4e4f7d7`, where L4-E7's results cache does not hold.",
              "and OPEN until\n`test_l4e7` passes at the guard round's integration `c4e4f7d7`, where L4-E7's results cache did not hold; "
              "CLOSED at set 28's\nintegration on `test_l4e7` passing on the frozen line `%s` (\"%s\")." % (FROZEN, LINE), README)
    for p, t in ((REG, reg), (PAGE, page), (README, rd)):
        if re.search("[–—]", t):
            refuse("%s would carry an en or em dash" % p)
        open(p, "w", encoding="utf-8").write(t)
    print("apply_close_r197: R-197 CLOSED with the integration commit %s and the line %r read on %s; the register's header, "
          "L4-E9's page (counts OPEN 0, CLOSED 2) and README restated" % (MERGE, LINE, FROZEN))


if __name__ == "__main__":
    main()
