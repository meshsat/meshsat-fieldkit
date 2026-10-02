#!/usr/bin/env python3
"""apply_gen_sch_e_aux.py: DRAFT for board E's generator owner (task L4-E11, MESHSAT-1357, the fix round for the consolidation
review cx36, B1, 2 October 2026). NOT APPLIED to the tree by L4-E11; its author ran it only on scratch copies (the tests write
scratch copies).

Why (L4E11-SOURCE-ONLY-AND-ENTRY.md section 15a): with TI's BQ25730 and its battery FETs on board A (apply_gen_sch_a_charger.py),
CELL_F is the pack side of those FETs. Board E's auxiliary domain sat on CELL_F: U12 (the AP63205 that feeds the sensor
controller, the Geiger supply and the fans' logic), C31 and both mixer fans with their flyback diodes. With the charge held the
battery FETs are off (SLUSE65A p.38) and that domain still drained the pack; with the pack absent nothing fed it. It takes board
A's VSYS over the dock's pin 1 instead (VSYS_E here, VBAT on board A), which the pack (through the battery FETs, on with the
battery alone, p.27) or a source holds, and which the source carries alone while the charge is held.

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else:
  J_BLK   pin 1 from GND to VSYS_E (one Preci-Dip 813 contact, 1.0 A declared against its 3.5 A); seven 813 contacts stay ground.
  U12     VIN and EN, and C31 (its input capacitor and bypass), on VSYS_E; its section comment.
  fans    J_FAN1 and J_FAN2 pin 1 and the flyback diodes D7 and D8 on VSYS_E.
  intent  VSYS_E declared (source J_BLK, 1.0 A: U12 0.8, the fans 0.1 each, always on, v_work 17.4 V: VSYS reaches 17.375 V with
          the charge held); CELL_F's loads the pack path alone; +5V_E6's reason; E6_SW, E6_BST and the fans' switched returns
          re-declared to 17.4 V; a power flag on VSYS_E.
CELL_F keeps the pack path to board A (P_CP), D3, C1, TP8 and the pack monitor R42 and R43 (0.14 mA at 16.884 V, intended).

ORDER: with apply_gen_sch_a_charger.py (board A's J_DOCK pin 1 on VBAT) and apply_pcb_interfaces_dock.py; never alone, or the
dock's pin 1 meets VSYS_E on E and GND on A.

Usage:  apply_gen_sch_e_aux.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_e_aux"
_VSYS_E = ('\n# L4-E11 (MESHSAT-1357, the fix round for the consolidation review cx36, B1, 2 October 2026): VSYS_E, THE AUXILIARY DOMAIN\'S\n'
           '# FEED. With TI\'s BQ25730 and its battery FETs on board A, CELL_F is the pack side of those FETs: U12 and the fans on CELL_F\n'
           '# would drain the pack while the charge is held and lose their supply with the pack absent. They take board A\'s VSYS over the\n'
           '# dock\'s pin 1 (one Preci-Dip 813 contact, 3.5 A maximum), which the pack or a source holds.\n'
           '_intent.rail("VSYS_E", 14.4, 1.0, 1.0, "J_BLK", always_on=True, v_work=17.4, converted=False,\n'
           '             always_on_why="board A\'s VSYS over the dock\'s pin 1: the pack (through the battery FETs, on with the battery alone) or a source holds it; nothing on this board switches it",\n'
           '             loads={"U12": 0.8, "J_FAN1": 0.1, "J_FAN2": 0.1},\n'
           '             note="board A\'s VBAT (VSYS) on J_BLK pin 1: U12\'s VIN and EN, C31, both mixer fans and their flyback diodes (L4-E11)")')
EDITS = [
    ('             loads={"P_CP": 9.0, "U12": 0.8, "J_FAN1": 0.1, "J_FAN2": 0.1},', '             loads={"P_CP": 9.0},'),
    ('             note="the pack node after the 25 A blade F3, to the block pads")', '             note="the pack node after the 25 A blade F3, to the block pads")' + _VSYS_E),
    ('always_on_why="U12 is an AP63205 whose EN pin is tied to CELL_F, the pack node it runs from, so this rail follows the pack and has no switch of its own",',
     'always_on_why="U12 is an AP63205 whose EN pin is tied to VSYS_E, board A\'s VSYS over the dock (L4-E11), so this rail follows VSYS, which the pack or a source holds, and has no switch of its own",'),
    ('"solder lands for the 12 signal wires to the block board underside (mirror of A22 J_DOCK): 1-7 GND, 8 SHORE_INHIBIT,',
     '"solder lands for the 12 signal wires to the block board underside (mirror of A22 J_DOCK): 1 VSYS_E from board A\'s VBAT (L4-E11), 2-7 GND, 8 SHORE_INHIBIT,'),
    ('{"1": "GND", "2": "GND", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "GND", "8": "SHORE_INHIBIT", "9": "USB_E6_P", "10": "USB_E6_N", "11": "GND", "12": "BLK_SPARE"})',
     '{"1": "VSYS_E", "2": "GND", "3": "GND", "4": "GND", "5": "GND", "6": "GND", "7": "GND", "8": "SHORE_INHIBIT", "9": "USB_E6_P", "10": "USB_E6_N", "11": "GND", "12": "BLK_SPARE"})'),
    ('# --- controller power: AP63205 5 V 2 A buck from the pack node (', '# --- controller power: AP63205 5 V 2 A buck from VSYS_E, board A\'s VSYS over the dock\'s pin 1 (L4-E11) ('),
    ('"TSOT6", {"1": "+5V_E6", "2": "CELL_F", "3": "CELL_F", "4": "GND", "5": "E6_SW", "6": "E6_BST"}, "C2071056")',
     '"TSOT6", {"1": "+5V_E6", "2": "VSYS_E", "3": "VSYS_E", "4": "GND", "5": "E6_SW", "6": "E6_BST"}, "C2071056")'),
    ('_intent.node("E6_SW", 16.8, "the AP63205\'s switching node: it swings to CELL_F, which is the pack at its 4S "\n             "termination of 16.8 V, and a diode drop below ground on the other half of the cycle", v_min=-1.0)',
     '_intent.node("E6_SW", 17.4, "the AP63205\'s switching node: it swings to VSYS_E, board A\'s VSYS at most 17.375 V with the "\n             "charge held (L4-E11), and a diode drop below ground on the other half of the cycle", v_min=-1.0)'),
    ('_intent.node("E6_BST", 16.8 + 6.0, ', '_intent.node("E6_BST", 17.4 + 6.0, '),
    ('so at most E6_SW\'s 16.8 V plus "', 'so at most E6_SW\'s 17.4 V plus "'),
    ('c("C31", "10u 25V 1210", "CELL_F", "GND", "C1210")', 'c("C31", "10u 25V 1210", "VSYS_E", "GND", "C1210")'),
    ('"mixer fan %s under the plate (12 V class fan on the pack node, low-side PWM, tachometer)" % n, {"1": "CELL_F",',
     '"mixer fan %s under the plate (12 V class fan on VSYS_E, board A\'s VSYS (L4-E11), low-side PWM, tachometer)" % n, {"1": "VSYS_E",'),
    ('"SS14 flyback across fan %s" % n, "SMB", {"1": "CELL_F", "2": "FAN%s_SW" % n}, "C51897884")',
     '"SS14 flyback across fan %s" % n, "SMB", {"1": "VSYS_E", "2": "FAN%s_SW" % n}, "C51897884")'),
    ('_intent.node("FAN%s_SW" % n, 16.8 + 0.55, ', '_intent.node("FAN%s_SW" % n, 17.4 + 0.55, '),
    ('"on, and at turn-off CELL_F\'s 16.8 V plus D%s\'s forward drop,', '"on, and at turn-off VSYS_E\'s 17.4 V plus D%s\'s forward drop,'),
    ('_intent.bypass("C31", "U12", "3", "CELL_F")', '_intent.bypass("C31", "U12", "3", "VSYS_E")'),
    ('"+5V_E6", "+3V3_E6", "E6_DVDD"), 1)', '"+5V_E6", "+3V3_E6", "E6_DVDD", "VSYS_E"), 1)'),
]

def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
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


# NOT RELEASED: task L4-E11 drafts this change for board E's generator owner and never applies it. Writing the repository's
# own gen_sch_e.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an
# accepted check of L4-E11 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written
# (the tests do, on scratch copies).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_e.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; L4-E11's values wait on an accepted check")
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
