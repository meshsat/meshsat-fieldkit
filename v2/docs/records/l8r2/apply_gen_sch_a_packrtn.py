#!/usr/bin/env python3
"""apply_gen_sch_a_packrtn.py: DRAFT for board A's generator owner (Layer 8 record l8r2, round 3, item 5, MESHSAT-1357, 3 October
2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).

The finding (record l9stk at 7388a84b, section 12 and l9stk_stackups.out section 2, "returns declared in the intents: board A none;
board E none"): the pack path's return on board A, GND from the four dock return contacts J_CN1 to J_CN4 to the ground ends of the
stages VBAT feeds, is declared only as a NODE ("the board's reference"), so no power rule solves its copper, while its forward half
(CELL+ on the dock contacts J_CP1 to J_CP4, CELL_FUSED, VBAT) is a rail every copper rule solves. Board P declares its pack return
PACK_N as a rail returning PACK_P (gen_sch_p.py, 20 September 2026), and board B declares its GND as a rail (gen_sch_b.py).

What it writes, and nothing else: the node declaration of GND is replaced by a rail declaration of the same net, board B's form
with board P's `returns`:
  _intent.rail("GND", 0.0, 10.0, 18.0, ["J_CN1", "J_CN2", "J_CN3", "J_CN4"], loads={...}, returns="CELL+", share=0.005, ...)
  - sources the four dock return contacts (a ground returns to several, intent.rail's own words); loads the ground end of every
    stage VBAT declares as a load, at VBAT's own figure: the AP64500 stages U4 and U6, the TPS62933 bucks U12 and U41, the eFuses
    U21 and U22 at their GND pins, and the LM5176 stages at their current-sense shunts, the part through which such a stage's input
    current returns to GND (S2's R170 for Q28, the device rail's R177 for Q32, the PA's R56 for Q11, HF's R122 for U15). The loads
    sum to 11.57 A, VBAT's own declared sum, under the 18.0 A peak;
  - returns CELL+: the drop is judged against CELL+'s 14.4 V (dc_drop, rule PI-002), not against the net's own 0 V, and the
    rail's watts are not counted a second time (thermal.py, rule THM-001), as for PACK_N;
  - share 0.005: this board's half percent of the loop, the share its CELL+ declares (check_contracts.py skips GND's shares);
  - volts 0.0 kept, so a part between a live net and ground is judged against the live net exactly as the node made it (derate).
A later draft that adds a VBAT load (L4-E11's U42, L4-E9's R227) does not add its return here: the return's copper at the dock
contacts carries the whole either way, and a load added to VBAT can be added here in the same release.
Round 4 (L9P-F02): where this record's apply_gen_sch_a_slotlm.py is already applied (VBAT's loads name its stages' entries Q501
and Q531), slots 1 and 3 are LM5176 stages and their ground ends are their CS shunts R506 and R536 at 2.22 A; slotlm applied
after this draft rewrites the same two entries, so either order gives one generator.
Which rules then judge its copper (pcb_rules.yaml): PI-001 (conductor current capacity, dc_drop's density verdict on the routed
board at the declared 18 A), PI-002 (the drop from the dock contacts to each stage against 0.5 % of 14.4 V), PI-003 (the barrels
where the return changes layer, from dc_drop's solved mesh; In1 and In4 are this board's ground planes), and PWR-001 (the rail's
sources and loads on the regenerated netlist). Record l9stk's decision lays the pack path and its return as bands shared by both
outer faces at 1 oz; this declaration is what makes a rule read the return's half.

Usage:  apply_gen_sch_a_packrtn.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, GND is already a
rail, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_packrtn"
ADDS = ()
NETS = ()
SOURCES = ("J_CN1", "J_CN2", "J_CN3", "J_CN4")
# the ground end of each load VBAT declares (gen_sch_a.py's VBAT rail), at VBAT's own figure
LOADS = (("U4", 2.0), ("R170", 2.22), ("U6", 2.0), ("R177", 1.61), ("U41", 0.4), ("R56", 1.5), ("R122", 0.3), ("U12", 0.2),
         ("U22", 0.65), ("U21", 0.69))
OF_VBAT = {"R170": "Q28", "R177": "Q32", "R56": "Q11", "R122": "U15"}   # the LM5176 stage's CS shunt for the load VBAT names
# round 4: with slotlm applied first, slots 1 and 3 are LM5176 stages (VBAT names Q501 and Q531 at 2.22 A; their CS shunts R506, R536)
SLOTLM_VBAT = '"Q501": 2.22, "Q28": 2.22, "Q531": 2.22,'
LOADS_SLOTLM = tuple(("R506", 2.22) if k == "U4" else ("R536", 2.22) if k == "U6" else (k, v) for k, v in LOADS)

_OLD = ('_intent.node("GND", 0.0, "the board\'s reference. It is declared so that a part between a live net and ground "\n'
        '             "is judged against the live net rather than reported as sitting on an undeclared one")\n')

def _new(loads):
    return ('# THE PACK PATH\'S RETURN IS A RAIL (record l8r2 round 3, item 5, MESHSAT-1357, 3 October 2026; record l9stk\'s finding):\n'
        '# GND from the dock return contacts J_CN1 to J_CN4 to the stages VBAT feeds carries the pack\'s whole current, the other\n'
        '# half of CELL+, CELL_FUSED and VBAT, and as a node no power rule solved it. Declared as board P declares PACK_N: its drop\n'
        '# judged against CELL+\'s 14.4 V (PI-002), its copper at the pack\'s 18 A (PI-001, PI-003), its watts not counted twice. Each\n'
        '# load is the ground end of a load VBAT declares, at VBAT\'s figure; an LM5176 stage\'s input current returns through its CS\n'
        '# shunt (R170 S2, R177 the device rail, R56 the PA, R122 HF). It keeps volts 0.0, so a part between a live net and ground\n'
        '# is judged against the live net, as the node made it.\n'
        '_intent.rail("GND", 0.0, 10.0, 18.0, ["J_CN%%d" %% _k for _k in range(1, 5)], returns="CELL+", share=0.005, converted=False,\n'
        '             loads={%s},\n'
        '             always_on=True,\n'
        '             always_on_why="the pack\'s return: nothing on this board or in the pack switches it; the pack\'s protection FETs "\n'
        '                           "are in its positive path on board P (Q1, Q2), which is what high-side protection means",\n'
        '             note="the board\'s reference and the pack path\'s return, from the dock return contacts J_CN1 to J_CN4 to the "\n'
        '                  "ground end of every stage VBAT feeds, at the pack\'s own 10.0 A typical and 18.0 A peak; the loads are "\n'
        '                  "VBAT\'s own, at their ground ends. Its drop is judged against CELL+, the rail it returns, at this "\n'
        '                  "board\'s half percent, the share its CELL+ declares")\n'
        % ", ".join('"%s": %s' % (k, v) for k, v in loads))


_NEW = _new(LOADS)
EDITS = [(_OLD, _NEW)]


def edits_for(text):
    """the edit for this target: slots 1 and 3's ground ends are their CS shunts where slotlm's stages are drawn"""
    return [(_OLD, _new(LOADS_SLOTLM))] if SLOTLM_VBAT in text else EDITS


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if re.search(r'_intent\.rail\(\s*"GND"', text):
        refuse("GND is already declared as a rail in the target")
    new = text
    for old, rep in edits_for(text):
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once" % new.count(old))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    if new.find('_intent.rail("CELL+"') < 0 or new.find('_intent.rail("CELL+"') > new.find('_intent.rail("GND"'):
        refuse("CELL+, the rail the return names, is not declared before it")
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
    if back != new or any(back.count(rep) != 1 for _o, rep in edits_for(text)):
        refuse("the written file does not read back as the patched text")
    ast.parse(back)
    print("%s: WRITTEN, %d edit(s)" % (NAME, len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
