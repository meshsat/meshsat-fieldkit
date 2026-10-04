#!/usr/bin/env python3
"""apply_gen_sch_e_packrtn.py: DRAFT for board E's generator owner (Layer 8 record l8r2, round 3, item 5, MESHSAT-1357, 3 October
2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).

The finding (record l9stk at 7388a84b, section 12 and l9stk_stackups.out section 2, "returns declared in the intents: board A none;
board E none"): the pack path's return on board E, GND from the XT60's return pin J_BATT pin 1 to the 12 AWG return pad P_CN, is
declared only as a NODE ("the board's reference"), so no power rule solves its copper, while its forward half (CELL+ from J_BATT
pin 2 to the blade F3, CELL_F from F3 to the pad P_CP) is a rail every copper rule solves. Board P declares its pack return PACK_N
as a rail returning PACK_P (gen_sch_p.py, 20 September 2026), and board B declares its GND as a rail (gen_sch_b.py).

What it writes, and nothing else: the node declaration of GND is replaced by a rail declaration of the same net, board B's form
with board P's `returns`:
  _intent.rail("GND", 0.0, 10.0, 18.0, "J_BATT", loads={"P_CN": 10.0}, returns="CELL_F", share=0.005, converted=False,
               always_on=True, ...)
  - source J_BATT (its pin 1, the pack's return lead) and the load P_CN (the 12 AWG return pad to the dock block), the mirror of
    CELL+ (J_BATT to F3) and CELL_F (F3 to P_CP); 10.0 A typical and 18.0 A peak, the pack's own (pcb_pack_protection.yaml), and
    the whole of it through P_CN, the upper bound (board E's own loads return part of it nearer J_BATT);
  - returns CELL_F: the drop is judged against CELL_F's 14.4 V (dc_drop, rule PI-002), not against the net's own 0 V, and the
    rail's watts are not counted a second time (thermal.py, rule THM-001), as for PACK_N;
  - share 0.005: this board's half percent of the loop, the share its CELL+ declares (check_contracts.py skips GND's shares);
  - volts 0.0 kept, so a part between a live net and ground is judged against the live net exactly as the node made it (derate).
Which rules then judge its copper (pcb_rules.yaml): PI-001 (conductor current capacity, dc_drop's density verdict on the routed
board at the declared 18 A), PI-002 (the drop from J_BATT to P_CN against 0.5 % of 14.4 V), PI-003 (the barrels where the return
changes face, from dc_drop's solved mesh), and PWR-001 (the rail's source and load on the regenerated netlist). Record l9stk's
decision lays the pack path and its return as bands shared by both outer faces at 1 oz; this declaration is what makes a rule read
the return's half.

Usage:  apply_gen_sch_e_packrtn.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, GND is already a
rail, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_e_packrtn"
ADDS = ()
NETS = ()

_OLD = ('_intent.node("GND", 0.0, "the board\'s reference, so a part between a live net and ground is judged against "\n'
        '             "the live net rather than reported as sitting on an undeclared one")\n')

_NEW = ('# THE PACK PATH\'S RETURN IS A RAIL (record l8r2 round 3, item 5, MESHSAT-1357, 3 October 2026; record l9stk\'s finding):\n'
        '# GND from the XT60\'s return pin J_BATT pin 1 to the 12 AWG return pad P_CN carries the pack\'s whole current, the other\n'
        '# half of CELL+ and CELL_F, and as a node no power rule solved it. Declared as board P declares PACK_N: its drop judged\n'
        '# against CELL_F\'s 14.4 V (PI-002), its copper at the pack\'s 18 A (PI-001, PI-003), its watts not counted twice. It keeps\n'
        '# volts 0.0, so a part between a live net and ground is judged against the live net, as the node made it.\n'
        '_intent.rail("GND", 0.0, 10.0, 18.0, "J_BATT", loads={"P_CN": 10.0}, returns="CELL_F", share=0.005, converted=False,\n'
        '             always_on=True,\n'
        '             always_on_why="the pack\'s return: nothing on this board or in the pack switches it; the pack\'s protection FETs "\n'
        '                           "are in its positive path on board P (Q1, Q2), which is what high-side protection means",\n'
        '             note="the board\'s reference and the pack path\'s return, from J_BATT pin 1 (the pack lead\'s return) to the 12 AWG "\n'
        '                  "return pad P_CN (the dock block\'s return targets), at the pack\'s own 10.0 A typical and 18.0 A peak, "\n'
        '                  "the whole of it through P_CN as the upper bound. Its drop is judged against CELL_F, the rail it returns, "\n'
        '                  "at this board\'s half percent, the share its CELL+ declares")\n')

EDITS = [(_OLD, _NEW)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if re.search(r'_intent\.rail\(\s*"GND"', text):
        refuse("GND is already declared as a rail in the target")
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
    if new.find('_intent.rail("CELL_F"') < 0 or new.find('_intent.rail("CELL_F"') > new.find('_intent.rail("GND"'):
        refuse("CELL_F, the rail the return names, is not declared before it")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: record l8r2 drafts this change for board E's generator owner and never applies it. Writing the repository's own
# gen_sch_e.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_e.py")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_e.py", "b/gen_sch_e.py", n=0))
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
