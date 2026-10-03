#!/usr/bin/env python3
"""apply_set28_procurement_renumber.py: PREPARED, NOT RUN by the set 28 preparation (MESHSAT-1357, 3 October 2026). The merges of
fnd/l6pwr and fnd/l7pwr both appended a section numbered 8 to v2/docs/parts/PROCUREMENT.md; the conflict was resolved by keeping both
additions verbatim, Layer 6's first (the brief: no content of either side dropped or rewritten), so the page now carries two sections
headed "## 8." (Layer 6's power parts, then Layer 7's fan picks). This script renumbers Layer 7's to 9 and brings its three mentions
and its test's heading assertion with it; the decision to run it is the integrator's (it rewrites Layer 7's text, which the
preparation was told not to do).

What it changes, each asserted present exactly once before, absent after:
  v2/docs/parts/PROCUREMENT.md            "## 8. Layer 7's fan picks ..." -> "## 9. Layer 7's fan picks ..."
  v2/docs/records/l7pwr/README.md         "`v2/docs/parts/PROCUREMENT.md` section 8" -> "... section 9"
  v2/docs/records/l7pwr/L7-FANS-AND-TH1.md  two mentions "`PROCUREMENT.md` section 8" -> "section 9"
  v2/ecad/tools/tests/test_l7pwr.py       the heading string asserted, and its message "PROCUREMENT.md section 8 lacks"
Layer 6's section 8 and its mentions are untouched. Usage: apply_set28_procurement_renumber.py [--write]; refuses (exit 3) a second
run (Layer 7's section already reads 9) or a text that is not the one above. Every write asserts the new text differs and reads back."""
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
H8 = "## 8. Layer 7's fan picks and the T-H1 mock-up set (record l7pwr, 3 October 2026)"
H9 = H8.replace("## 8.", "## 9.", 1)
EDITS = {
    "v2/docs/parts/PROCUREMENT.md": [(H8, H9, 1)],
    "v2/docs/records/l7pwr/README.md": [("| `v2/docs/parts/PROCUREMENT.md` section 8 |", "| `v2/docs/parts/PROCUREMENT.md` section 9 |", 1)],
    "v2/docs/records/l7pwr/L7-FANS-AND-TH1.md": [("`PROCUREMENT.md` section 8", "`PROCUREMENT.md` section 9", 2)],
    "v2/ecad/tools/tests/test_l7pwr.py": [('"%s"' % H8, '"%s"' % H9, 1), ('"PROCUREMENT.md section 8 lacks %r"', '"PROCUREMENT.md section 9 lacks %r"', 1)],
}


def refuse(msg):
    print("apply_set28_procurement_renumber: REFUSED: %s" % msg)
    sys.exit(3)


def main(argv):
    write = "--write" in argv
    page = open(os.path.join(TOP, "v2/docs/parts/PROCUREMENT.md"), encoding="utf-8").read()
    if H9 in page:
        refuse("already applied: Layer 7's section reads 9")
    if page.count("## 8. ") != 2:
        refuse("PROCUREMENT.md carries %d section(s) numbered 8, two expected (Layer 6's and Layer 7's)" % page.count("## 8. "))
    plan = {}
    for rel, edits in EDITS.items():
        old = open(os.path.join(TOP, rel), encoding="utf-8").read()
        new = old
        for a, b, n in edits:
            if new.count(a) != n:
                refuse("%s: %r occurs %d time(s), %d expected" % (rel, a[:60], new.count(a), n))
            new = new.replace(a, b)
        if new == old:
            refuse("%s: the new text does not differ" % rel)
        plan[rel] = (old, new)
    for rel, (old, new) in plan.items():
        if write:
            with open(os.path.join(TOP, rel), "w", encoding="utf-8") as fh:
                fh.write(new)
            if open(os.path.join(TOP, rel), encoding="utf-8").read() != new:
                refuse("%s does not read back" % rel)
        print("%s %s" % ("renumbered" if write else "would renumber", rel))
    if not write:
        print("apply_set28_procurement_renumber: --check, nothing written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
