#!/usr/bin/env python3
"""apply_gen_sch_a_fb01.py: DRAFT for board A's generator owner (Layer 8 record l8r2, round 6, finding F5-03 as the collaborator's
recheck asks it corrected, MESHSAT-1357, 4 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch
copies (the tests write scratch copies).

The defect (F5-03; the collaborator's recheck astra-check-l9pf02-2, CONFIRMED OPEN): every LM5176 5.1 V stage sets its output with
53.6 k over 10 k, and the lm5176() helper writes the top resistor's tolerance itself (rfb_top + " 1%") and takes the bottom one as
"10k 1%" by default. On TI SNVSAI1D's VREF 0.788 to 0.812 V that divider gives 4.928 to 5.252 V before the FB pin's bias, 2 mV over
the CM5's 5.25 V input maximum (CM5 datasheet, the pin table's "4.75 V to 5.25 V main power input") and the USB devices' 5.25 V on
the device rail. The stages: slot 2 (U5, R32 and R33), the device rail (U7, R40 and R41), and, where record l8r2's
apply_gen_sch_a_slotlm.py is applied, slots 1 and 3 (U501 with R501 and R502, U531 with R531 and R532).

The correction: both divider resistors of each of those stages at 0.1 %: 0.788 x (1 + 53.6 x 0.999 / (10 x 1.001)) = 5.003 V to
0.812 x (1 + 53.6 x 1.001 / (10 x 0.999)) = 5.173 V, and with IBIAS(FB) at most 25 nA through 53.6 k (1.34 mV) 5.002 to 5.174 V,
inside the CM5's 4.75 to 5.25 V with 76 mV to its top before the load's transient; the least load voltage with the rail's 2 % drop
rises from 4.829 to 4.902 V, which lowers every constant-power corner of record l8r2's section 1u. The values stay 53.6 k and 10 k
(the nominal 5.088 V and every loop design of slot 2's stage unchanged); only their tolerance changes.

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else:
  1. the helper gains a keyword rfb_tol="1%" (the default keeps every other stage's text) and writes rfb_top + " " + rfb_tol;
  2. slot 2's and the device rail's calls pass rfb_val="10k 0.1%", rfb_tol="0.1%", with a comment line before slot 2's call;
  3. where slotlm's S1 and S3 calls are present, the same two keywords on each (slotlm applied after this draft writes them itself,
     so either order gives one generator).
No designator, net or land changes; record l6r2's LCSC table keys R32, R33, R40 and R41 by their 1 % values, so they keep no code
until 0.1 % rows are selected (a Layer 6 row owed, F6-02). Its anchors are lines no other draft of gen_sch_a.py touches.

Usage:  apply_gen_sch_a_fb01.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the repository's
own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_fb01"
ADDS = ()
NETS = ()
KW = ' rfb_val="10k 0.1%", rfb_tol="0.1%",'

_OLD_DEF = 'rfb_val="10k 1%", cout="10u 50V X7R 1210",'
_NEW_DEF = 'rfb_val="10k 1%", rfb_tol="1%", cout="10u 50V X7R 1210",'
_OLD_R = 'r(rft, rfb_top + " 1%", vout, N("FB"));'
_NEW_R = 'r(rft, rfb_top + " " + rfb_tol, vout, N("FB"));'
_OLD_S2 = 'lm5176("S2", "U5", "VBAT", "+5V_S2", "SLOT_EN2",'
_NEW_S2 = ('# F5-03, RECORD l8r2 ROUND 6 (MESHSAT-1357, 4 October 2026): THE 5.1 V STAGES\' DIVIDERS AT 0.1 %. On VREF 0.788 to 0.812 V\n'
           '# (SNVSAI1D) 53.6 k over 10 k at 1 % gives 4.928 to 5.252 V, over the CM5\'s and the USB devices\' 5.25 V; at 0.1 % 5.003 to\n'
           '# 5.173 V, 5.002 to 5.174 V with IBIAS(FB) 25 nA through 53.6 k. The values and every loop design are unchanged.\n'
           + _OLD_S2)
_OLD_S2K = 'cs_filter=("R173", "R174", "C138"), isns_filter=("R175", "R176", "C139"), isns="6m", isns_lcsc="C843882",'
_OLD_SDK = 'cs_filter=("R180", "R181", "C145"), isns_filter=("R182", "R183", "C146"), isns="6m", isns_lcsc="C843882",'
_OLD_S1K = 'cs_filter=("R509", "R510", "C513"), isns_filter=("R511", "R512", "C514"), isns="6m", isns_lcsc="C843882",'
_OLD_S3K = 'cs_filter=("R539", "R540", "C543"), isns_filter=("R541", "R542", "C544"), isns="6m", isns_lcsc="C843882",'

EDITS = [(_OLD_DEF, _NEW_DEF), (_OLD_R, _NEW_R), (_OLD_S2, _NEW_S2), (_OLD_S2K, _OLD_S2K + KW), (_OLD_SDK, _OLD_SDK + KW)]
OPTIONAL = [(_OLD_S1K, _OLD_S1K + KW), (_OLD_S3K, _OLD_S3K + KW)]   # slotlm's stages, where present


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if old in rep and new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if old not in rep and new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once" % new.count(old))
        new = new.replace(old, rep)
    for old, rep in OPTIONAL:
        if new.count(rep):
            refuse("already applied (a slot stage carries the keywords)")
        if new.count(old) > 1:
            refuse("a slot stage's anchor occurs %d times" % new.count(old))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: record l8r2 drafts this change for board A's generator owner and never applies it. Writing the repository's own
# gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_a.py", "b/gen_sch_a.py", n=0))
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
