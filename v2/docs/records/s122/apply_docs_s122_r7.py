#!/usr/bin/env python3
"""Stream s122, round 7 (S-122, MESHSAT-1357, 29 September 2026): the answer to the independent check of fnd/s122c at
1c187977 (`checks/check-s122-6.md`, m3).

m3 found correction 36's wording wider than its instrument: it said the closing check "asserts every figure and unit on
the lines it closes", while close_s122.py's scan reads a number only with a unit, or a spelled count (a number with no
unit, such as a socket's size code, is outside it). This script narrows the sentence to what the scan reads.
V2-SPEC.md is not a baselined definition: before it writes, the script reads the table of baselines of
`handover/DEFINITION-STATUS.md` ("## The two baselines", the helper of `apply_docs_s122_r6.py`) and refuses if V2-SPEC.md
is among its documents, and refuses if `s122lib.BASELINED` names it. The old passage is found once and the new one reads
back once; no dash; the document re-parses. Refuses a second run. Run: python3 apply_docs_s122_r7.py [--check]."""
import os, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402
import apply_docs_s122_r6 as R6  # noqa: E402

TAG = "apply_docs_s122_r7"
SPC = "v2/docs/V2-SPEC.md"
DOCS = {SPC: "c480bac24e8c048c"}
OLD = ("whose closing check\n"
       "    since that round asserts every figure and unit on the lines it closes. Line 47 named")
NEW = ("whose closing check\n"
       "    since that round asserts every figure with a unit, and every spelled count, on the lines it closes (a number\n"
       "    with no unit is outside it; this wording since round 7, check-s122-6 m3). Line 47 named")


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
