#!/usr/bin/env python3
"""pagenote.py (stream s119, S-119, MESHSAT-1357, 29 September 2026): the one helper the page scripts of this folder share.

apply(page, anchor, note, check) inserts `note` into `page` directly after `anchor` (a text that must occur exactly once in
the page, ending in a blank line), refuses a second run (the page already carries MARK), refuses a note with an em or en
dash, writes, re-reads the page, and checks that the page is its old text with exactly the note added and MARK once.
With check=True it validates in memory and writes nothing. Pages are the records of their streams: the note adds the
second issue's figures beside the first issue's, it rewrites none of them."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
MARK = "**Second issue of the charger rows (stream s119, S-119, 29 September 2026).**"
HEAD = (MARK + " The energy chain now carries board A's charger U3 at 0.979 (bracket 0.972 to 0.983; was 0.98, read from "
        "SLUSE66A Figure 8-4) and Option A(i)'s lid charger U3B at 0.961 (bracket 0.947 to 0.971; was 0.975, read from "
        "Figure 8-3), both by TI's loss equations (SLUSE66A Equations 6 to 22, printed pages 86 to 88) with the FETs of "
        "decision 57 (U3B: CSD17578Q5A in all four positions on its drafted 800 kHz row), R16 and R17 counted and the "
        "inductor's core loss excluded, so each figure is high by it (`records/s117/efficiency.out` section 7). The "
        "energy chain's scripts were re-issued with their pins moved and every output regenerated (`records/s119/README.md`, "
        "`records/s119/headline_diff.out`). Where this page quotes a figure listed here, the page's figure is the first "
        "issue's and is superseded by the one given here. Model results on the September reference day; nothing is measured.")


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def apply(page, anchor, note, check=False):
    path = os.path.join(TOP, page)
    old = open(path, encoding="utf-8").read()
    if MARK in old:
        refuse("%s already carries the s119 note (a second run)" % page)
    if old.count(anchor) != 1:
        refuse("the anchor occurs %d times in %s: %r" % (old.count(anchor), page, anchor[:80]))
    if not anchor.endswith("\n\n"):
        refuse("the anchor must end in a blank line")
    if "—" in note or "–" in note:
        refuse("the note carries an em or en dash")
    if not note.startswith(MARK):
        refuse("the note does not open with the mark")
    i = old.index(anchor) + len(anchor)
    new = old[:i] + note.rstrip("\n") + "\n\n" + old[i:]
    if new == old:
        refuse("the new text does not differ")
    if check:
        print("CHECK ONLY: %s would gain %d characters after its anchor; not written" % (page, len(new) - len(old)))
        return 0
    open(path, "w", encoding="utf-8").write(new)
    back = open(path, encoding="utf-8").read()
    if back != new or back.count(MARK) != 1 or back.replace(note.rstrip("\n") + "\n\n", "", 1) != old:
        refuse("%s did not read back as its old text plus the note" % page)
    print("APPLIED: %s gained the s119 note after its anchor" % page)
    return 0


def run(page, anchor, note):
    return apply(page, anchor, note, check="--check" in sys.argv[1:])
