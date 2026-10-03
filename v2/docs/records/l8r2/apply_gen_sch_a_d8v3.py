#!/usr/bin/env python3
"""apply_gen_sch_a_d8v3.py: DRAFT for board A's generator owner (Layer 8 record l8r2, item 3, finding L5R2-F05, MESHSAT-1357,
3 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies.

The defect (L5R2-F05): board A's +3V3 (U12, a 3 A TPS62933 buck) reaches board D over one conductor of the mezzanine harness
(J_MEZZ1 pin 13, Wurth WR-CAB flat cable and WR-BHD socket, 1 A each at most) with no branch limiter, so a fault on board D's
3.3 V can carry U12's current limit on a 1 A conductor.

The correction: a TPS259631 eFuse U44 (board A's efuse() helper, TI SLVSET8A; the part board A fits as U21, U22, U23, U32, U39)
between +3V3 and a new net +3V3_A2D on J_MEZZ1 pin 13: its limit is the printed 3.83 k row, 0.224 to 0.269 A (R234 3.83 k), 2.2
times board D's declared 0.10 A peak (gen_sch_d.py's +3V3) and a quarter of the conductor's 1 A; on-resistance at most 143.4 mOhm
under 4 V (SLVSET8A 7.5), 14 mV at the 0.10 A peak. OVLO 30.1k over 10k (the pin at 0.81 to 0.86 V on 3.3 V, inside 0.5 to 2 V; cut at
4.62 to 4.97 V); EN to +3V3 through R238 100 k (note 2); FLT to +3V3 (the helper's 10 k). The +3V3 rail's load row for J_MEZZ1
moves to U44 and +3V3_A2D is declared; the harness contract IF-AD-HARNESS gains the alias +3V3_A2D / +3V3 on pin 13 (a Layer 5 text).

Usage:  apply_gen_sch_a_d8v3.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_d8v3"
GEN = "gen_sch_a.py"
ADDS = ("U44", "R234", "R235", "R236", "R237", "R238", "C242", "C243")
NETS = ("+3V3_A2D", "D8V3_EN", "D8V3_FLT")
_ROW = ' "1": "USB_D8_P", "2": "USB_D8_N", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "TR_APRS", "8": "TX_INHIBIT_n", "9": "PA_EN", "10": "SDA", "11": "SCL", "12": "EXP_INT", "13": "+3V3", "14": "GND", "15": "ZEROIZE_HW", "16": "AB_SPARE"})\n'
_NEW_ROW = (_ROW.replace('"13": "+3V3"', '"13": "+3V3_A2D"') +
            '# L5R2-F05, drafted by Layer 8 record l8r2 (MESHSAT-1357, 3 October 2026): board D\'s 3.3 V leaves on ONE harness conductor (1 A)\n'
            '# and U12 limits at amperes; U44 limits the branch at 0.224 to 0.269 A (R234 3.83 k, SLVSET8A\'s printed row), 2.2 times board\n'
            '# D\'s 0.10 A peak. OVLO 30.1k over 10k (0.81 to 0.86 V on the pin at 3.3 V; cut at 4.62 to 4.97 V); EN through R238 100 k (SLVSET8A note 2).\n'
            'efuse("U44", "+3V3", "+3V3_A2D", "D8V3_EN", "D8V3_FLT", ["C242", "R234", "R235", "R236", "R237", "C243"], "3.83k 1% (ILM: 0.247 A)", ovlo_top="30.1k 1%", ovlo_lcsc="C23000")\n'
            'r("R238", "100k", "D8V3_EN", "+3V3", lcsc="C25803")\n'
            '_intent.rail("+3V3_A2D", 3.3, 0.06, 0.10, "U44", loads={"J_MEZZ1": 0.10}, series_of="+3V3", converted=False, budget=0.03,\n'
            '             source_ic="U44 is a TPS2596 eFuse: its OUT pin IS the power path",\n'
            '             note="board D\'s 3.3 V on J_MEZZ1 pin 13 behind the eFuse U44 (0.224 to 0.269 A; L5R2-F05, record l8r2)")\n')
EDITS = [
    (_ROW, _NEW_ROW),
    ('             loads={"J_MEZZ1": 0.10, "U8": 0.03,', '             loads={"U44": 0.10, "U8": 0.03,'),
    ("_listed = {r for _, refs in SECTIONS for r in refs}\n",
     'SECTIONS.append(("BOARD D\'S 3.3 V BRANCH LIMIT (L5R2-F05): EFUSE U44", ["U44", "C242", "R234", "R235", "R236", "R237", "C243", "R238"]))   # Layer 8 record l8r2\n'
     "_listed = {r for _, refs in SECTIONS for r in refs}\n"),
]


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
