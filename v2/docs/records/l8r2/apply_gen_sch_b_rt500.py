#!/usr/bin/env python3
"""apply_gen_sch_b_rt500.py: DRAFT for board B's generator owner (Layer 8 record l8r2, round 5, the answer to the collaborator's
check B2 of L9P-F02, MESHSAT-1357, 4 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch
copies (the tests write scratch copies).

The defect (open item O-20, records/r4b/r4-decisions.md; the collaborator's check B1 on board A's twin): every buck33 on board B
(the six AP64500 3.3 V stages U103, U104, U203, U204, U303, U304, the card sockets' and the NVMe and switch rails of the three
slots) draws its RT as 68 k with the value text "68k (RT: 500 kHz)". Diodes DS41979 Rev 5-2 Eq. 7 is RT[kOhm] = 100000 /
fsw[kHz], and its electrical table gives 450 to 550 kHz at RT = 200 k, so 68 k sets about 1.47 MHz: not the frequency of the
recipe's inductor and Table 1 row, and not the 500 kHz at which the maker plots every efficiency curve (Figures 2, 4, 5) and the
derating curve (Figure 24). The slot's load envelope (record l8r2 section 1s) takes the card's and the NVMe's input through those
curves, so at 1.47 MHz the envelope would rest on no maker figure.

The correction, O-20's own recommendation: RT = 200 k 1 % on buck33, which sets the 450 to 550 kHz the maker prints and plots.
O-20's check stands at either frequency for O-17's compensation (fc 12 to 18 kHz against fsw/10 of 50 kHz; Eq. 19's second term
5.3 pF against the 52 to 84 pF ESR term); the fitted 3.3 uH gives a ripple of 0.68 A at 500 kHz from 5.1 V (Eq. 8), inside the
inductor's rating and under the maker's 30 to 50 % of 5 A guidance, the direction of less ripple. Board A's twin, the slot AP64500s
U4 and U6, are retired by apply_gen_sch_a_slotlm.py, so O-20 has no part left on board A after this record's drafts.

What it changes in v2/ecad/tools/gen_sch_b.py, and nothing else: buck33's RT call (one line, the six parts) and the docstring's
sentence on the RT. No designator, net, land or code is added; Layer 6's LCSC table (record l6r2) keys each part by its value, so
the six RTs keep no code from it until a 200 k 1 % row is selected (a Layer 6 row owed, F5-04). Its anchors are lines no other
draft of gen_sch_b.py touches; Layer 6's land draft anchors the docstring line before this one, and the two apply in either order.

Usage:  apply_gen_sch_b_rt500.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the repository's
own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_rt500"
GEN = "gen_sch_b.py"
ADDS = ()
NETS = ()

_OLD_DOC = ("    for 500 kHz; but the 68k RT sets 1.47 MHz (DS41979 Rev 5-2 Eq. 7, RT[kOhm] = 100000 / fsw[kHz]), open item O-20.\n")
_NEW_DOC = ("    for 500 kHz; RT 200 k sets it (DS41979 Rev 5-2 Eq. 7, RT[kOhm] = 100000 / fsw[kHz], and 450 to 550 kHz at 200 k), the frequency of\n"
            "    the maker's efficiency and derating curves (O-20, drafted by record l8r2 round 5; the 68 k before it set 1.47 MHz).\n")
_OLD_RT = 'r(rrt, "68k (RT: 500 kHz)", tag + "_RT", "GND")'
_NEW_RT = 'r(rrt, "200k 1% (RT: 500 kHz)", tag + "_RT", "GND")'

EDITS = [(_OLD_DOC, _NEW_DOC), (_OLD_RT, _NEW_RT)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def in_use(text, ref):
    return re.search(r'(?:part|ic|r|c|tp|nfet|vh2|synth|q|esd|efuse)\(\s*"%s"' % re.escape(ref), text) is not None


def patched(text):
    for ref in ADDS:
        if in_use(text, ref):
            refuse("designator %s is already in use in the target" % ref)
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), text):
            refuse("net %s already exists in the target" % net)
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


# NOT RELEASED: record l8r2 drafts this change for the board's generator owner and never applies it. Writing the repository's own
# generator is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check of
# this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", GEN)
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; l8r2's drafts wait on an accepted check")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE.md names no single check")
    path = os.path.join(REPO, rec[0])
    if ".." in rec[0].split("/") or not os.path.isfile(path):
        refuse("NOT RELEASED: check %s is not in this tree" % rec[0])
    if open(path, encoding="utf-8").readline().rstrip("\n") != "accepted: yes":
        refuse("NOT RELEASED: check %s is not accepted" % rec[0])


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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/" + GEN, "b/" + GEN, n=0))
    if not write:
        print("%s: CHECK OK, %d edit(s), nothing written" % (NAME, len(EDITS)))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep) != 1 for _o, rep in EDITS):
        refuse("the written file does not read back as the patched text")
    ast.parse(back)
    print("%s: WRITTEN, %d edit(s)" % (NAME, len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
