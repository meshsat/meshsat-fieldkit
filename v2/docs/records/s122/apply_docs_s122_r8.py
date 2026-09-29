#!/usr/bin/env python3
"""Stream s122, round 8 (S-122, MESHSAT-1357, 29 and 30 September 2026): the answer to the independent check of fnd/s122c
at b76e5fd3 (`checks/check-s122-7.md`, m1).

m1 found correction 36's "asserts every figure with a unit" looser than the scope statement: the scan compares a unit
only where its source states one (a board file's outline, a generator's rail intent and a sheet's range give numbers
without one). `apply_docs_s122_r7.py`'s text is committed, so this script adds the qualifier rather than rewriting it.
V2-SPEC.md is not a baselined definition: before it writes, the script reads the table of baselines of
`handover/DEFINITION-STATUS.md` (the helper of `apply_docs_s122_r6.py`) and refuses if V2-SPEC.md is among its documents,
and refuses if `s122lib.BASELINED` names it. The old passage is found once and the new one reads back once; no dash;
the document re-parses. Refuses a second run. Run: python3 apply_docs_s122_r8.py [--check]."""
import os, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402
import apply_docs_s122_r6 as R6  # noqa: E402

TAG = "apply_docs_s122_r8"
SPC = "v2/docs/V2-SPEC.md"
DOCS = {SPC: "4f1fd784aa325a0d"}
OLD = ("on the lines it closes (a number\n"
       "    with no unit is outside it; this wording since round 7, check-s122-6 m3). Line 47 named")
NEW = ("on the lines it closes, and\n"
       "    compares a unit only where the source states one (a number with no unit is outside it; this wording since\n"
       "    rounds 7 and 8, check-s122-6 m3 and check-s122-7 m1). Line 47 named")


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    raise SystemExit(2)


def main():
    check = "--check" in sys.argv
    head = subprocess.run(["git", "-C", L.TOP, "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()
    R6.TAG = TAG
    base = R6.baselined()
    if SPC in base or SPC in L.BASELINED: refuse("%s is a baselined document (%s)" % (SPC, base))
    for rel, s in DOCS.items():
        if L.sha16(rel) != s: refuse("%s is %s, not the file this script corrects (%s): already applied, or changed" % (rel, L.sha16(rel), s))
    txt = open(os.path.join(L.TOP, SPC), encoding="utf-8").read()
    if any(d in NEW for d in L.DASHES): refuse("a dash in the new text")
    if txt.count(OLD) != 1: refuse("the old passage is found %d times" % txt.count(OLD))
    txt = txt.replace(OLD, NEW)
    if txt.count(NEW) != 1: refuse("the new passage does not read back once")
    if check:
        print("%s: --check at %s: %s not among the baselines %s; 1 edit located; nothing written" % (TAG, head, SPC, ", ".join(base)))
        return 0
    open(os.path.join(L.TOP, SPC), "w", encoding="utf-8").write(txt)
    L.md_blocks(SPC)
    print("%s: at %s %s is not among the baselines (%s); 1 edit written; V2-SPEC.md to %s" % (
        TAG, head, SPC, ", ".join(base), L.sha16(SPC)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
