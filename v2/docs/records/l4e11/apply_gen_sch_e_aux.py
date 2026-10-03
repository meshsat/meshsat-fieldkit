#!/usr/bin/env python3
"""apply_gen_sch_e_aux.py: DRAFT for board E's generator owner (task L4-E11, MESHSAT-1357, the fix round for the consolidation
review cx36, B1, 2 October 2026). NOT APPLIED to the tree by L4-E11; its author ran it only on scratch copies (the tests write
scratch copies).

Why (L4E11-SOURCE-ONLY-AND-ENTRY.md section 15a): with TI's BQ25730 and its battery FETs on board A (apply_gen_sch_a_charger.py),
CELL_F is the pack side of those FETs. Board E's auxiliary domain sat on CELL_F: U12 (the AP63205 that feeds the sensor
controller, the Geiger supply and the fans' logic), C31 and both mixer fans with their flyback diodes. With the charge held the
battery FETs are off (SLUSE65A p.38) and that domain still drained the pack; with the pack absent nothing fed it. It takes board
A's VSYS over the dock's pin 1 instead (VSYS_E here, VSYS_DOCK behind the eFuse U42 on board A), which the pack (through the battery FETs, on with the
battery alone, p.27) or a source holds, and which the source carries alone while the charge is held.

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else:
  J_BLK   pin 1 from GND to VSYS_E (one Preci-Dip 813 contact, 1.32 A declared against its 3.5 A); seven 813 contacts stay ground.
  +12V_FAN the mixers' regulated 12.0 V rail (section 18, Layer 7's F-L7-01: the Sanyo Denki 9WL0612P4H001 prints 10.8 to 13.2 V and
          VSYS_E runs 9.494 to 17.375 V): U22 LTC3115EFE-1 (ADI Rev. E, TA04's 12 V 1 MHz network) from VSYS_E, L4 XAL6060-103ME 10 uH,
          C135 10 uF 25 V in, C136 22 uF 25 V out, C137 4.7 uF PVCC, C138 and C139 100 nF bootstraps, R105 1M and R106 90.9k FB, R107 40.2k and
          C140 820 pF on VC, R108 10k and C141 33 pF feed-forward, R109 35.7k RT, R103 1.5M and R104 255k RUN (enable 8.33 V, disable 6.89 V),
          PWM/SYNC to VCC; the land keys HTSSOP20EP and L6060 added.
  J_FAN   J_FAN1 and J_FAN2 become four pins (12 V, GND, PWM, TACH); Q9 and Q10 stay as open-drain drivers of the fans' PWM inputs
          (FANn_PWM_OD, the fan's own pull-up; its level NOT READ, Layer 7); D7 and D8 (the flybacks of the chopped supply) and the FANn_SW
          nodes are removed (the old node loop is emptied, `for n in ():`, its text left for the owner to delete); the tach pull-ups R46
          and R47 stay.
  U12     VIN and EN, and C31 (its input capacitor and bypass), on VSYS_E; its section comment.
  fans    J_FAN1 and J_FAN2 pin 1 and the flyback diodes D7 and D8 on VSYS_E.
  intent  VSYS_E declared (source J_BLK, 1.32 A: U12 0.8, U22 0.52 at the floor, always on, v_work 17.4 V: VSYS reaches 17.375 V with
          the charge held); CELL_F's loads the pack path alone; +5V_E6's reason; E6_SW, E6_BST and the fans' switched returns
          re-declared to 17.4 V; a power flag on VSYS_E.
CELL_F keeps the pack path to board A (P_CP), D3, C1, TP8 and the pack monitor R42 and R43 (0.14 mA at 16.884 V, intended).

ORDER: with apply_gen_sch_a_charger.py (board A's J_DOCK pin 1 on VSYS_DOCK, behind U42) and apply_pcb_interfaces_dock.py; never alone, or the
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
           '_intent.rail("VSYS_E", 14.4, 1.32, 1.32, "J_BLK", always_on=True, v_work=17.4, converted=False,\n'
           '             always_on_why="board A\'s VSYS over the dock\'s pin 1 behind its eFuse U42: the pack (through the battery FETs, on with the battery alone) or a source holds it; nothing on this board switches it",\n'
           '             loads={"U12": 0.8, "U22": 0.52},\n'
           '             note="board A\'s VSYS_DOCK (VBAT through U42) on J_BLK pin 1: U12\'s VIN and EN, C31, and the mixers\' 12 V rail U22 (0.52 A at the 9.494 V floor with both fans at full speed; L4-E11 sections 15a and 18)")\n'
           '_intent.rail("+12V_FAN", 12.0, 0.34, 0.34, "L4", always_on=True, converted=True, efficiency=0.85, fed_from="VSYS_E",\n'
           '             always_on_why="U22\'s RUN divider enables it whenever VSYS_E is over about 8.3 V, so the rail follows VSYS_E and has no switch of its own; the fans\' speed is their PWM input",\n'
           '             loads={"J_FAN1": 0.17, "J_FAN2": 0.17},\n'
           '             note="L4-E11 section 18: the mixers\' regulated 12.0 V (Sanyo Denki 9WL0612P4H001, 10.8 to 13.2 V printed, 0.17 A each at 12 V, Layer 7), an LTC3115-1 buck-boost from VSYS_E 9.494 to 17.375 V")')
_FAN_OLD = ('for n in ("1", "2"):\n'
            '    ph("J_FAN%s" % n, 3, "mixer fan %s under the plate (12 V class fan on the pack node, low-side PWM, tachometer)" % n, {"1": "CELL_F", "2": "FAN%s_SW" % n, "3": "FAN%s_TACH" % n})\n'
            '    part("Q%s" % ("9" if n == "1" else "10"), "Transistor_FET", "2N7002", "2N7002 fan %s low-side switch (1 G, 2 S, 3 D)" % n, "SOT23", {"1": "FAN%s_G" % n, "2": "GND", "3": "FAN%s_SW" % n})\n'
            '    r("R%s" % ("44" if n == "1" else "45"), "100R", "FAN%s_PWM" % n, "FAN%s_G" % n); r("R%s" % ("46" if n == "1" else "47"), "10k", "FAN%s_TACH" % n, "+3V3_E6")\n'
            '    part("D%s" % ("7" if n == "1" else "8"), "Device", "D_Schottky", "SS14 flyback across fan %s" % n, "SMB", {"1": "CELL_F", "2": "FAN%s_SW" % n}, "C51897884")\n')
_FAN_NEW = 'for n in ("1", "2"):\n    ph("J_FAN%s" % n, 4, "mixer fan %s under the plate (Sanyo Denki 9WL0612P4H001, 12 V IP68, four wires: 12 V, GND, PWM, tachometer; L4-E11 section 18, Layer 7)" % n, {"1": "+12V_FAN", "2": "GND", "3": "FAN%s_PWM_OD" % n, "4": "FAN%s_TACH" % n})\n    part("Q%s" % ("9" if n == "1" else "10"), "Transistor_FET", "2N7002", "2N7002 fan %s PWM open-drain driver (1 G, 2 S, 3 D)" % n, "SOT23", {"1": "FAN%s_G" % n, "2": "GND", "3": "FAN%s_PWM_OD" % n})\n    r("R%s" % ("44" if n == "1" else "45"), "100R", "FAN%s_PWM" % n, "FAN%s_G" % n); r("R%s" % ("46" if n == "1" else "47"), "10k", "FAN%s_TACH" % n, "+3V3_E6")\n# L4-E11 section 18 (3 October 2026; Layer 7\'s F-L7-01): THE MIXERS\' 12.0 V RAIL. The fans Layer 7 selected print 10.8 to 13.2 V and VSYS_E\n# runs 9.494 to 17.375 V, so U22, an ADI LTC3115-1 four-switch buck-boost (Rev. E, held; input 2.7 to 40 V, inductor current limit 2.4 to\n# 3.7 A, internal 9 ms soft start), makes 12.0 V as ADI\'s TA04 draws it (10 uH, 1 MHz, FB 1M / 90.9k from the 1.000 V reference: 11.51 to\n# 12.43 V at FB\'s limits with the 1 % divider). Its RUN divider (1.5M / 255k) enables it at 8.33 V typical (7.98 to 8.67) and disables it at 6.89 V (6.55 to 7.23),\n# under the floor and over U12\'s 3.8 V start: a fan fault that drives U22 to its current limit against U42\'s lets VSYS_E fall only to U22\'s\n# disable. The fans are four-wire: Q9 and Q10 drive their PWM inputs open-drain; the chopped-supply flybacks D7 and D8 are gone.\nic("U22", 21, "LTC3115EFE-1 40 V 2 A buck-boost: the mixers\' 12.0 V rail from VSYS_E (TA04 network)", "HTSSOP20EP", {"1": "GND", "2": "F12_RUN", "3": "F12_SW2", "4": "+12V_FAN", "5": "GND", "6": "GND", "7": "F12_VC", "8": "F12_FB", "9": "F12_RT", "10": "GND", "11": "GND", "12": "F12_VCC", "13": "VSYS_E", "14": "F12_VCC", "15": "F12_BST2", "16": "F12_BST1", "17": "VSYS_E", "18": "F12_SW1", "19": "F12_VCC", "20": "GND", "21": "GND"})\npart("L4", "Device", "L", "10uH XAL6060-103ME (Isat 5.0 A, Irms 7.0 A)", "L6060", {"1": "F12_SW1", "2": "F12_SW2"})\nc("C135", "10u 25V 1210", "VSYS_E", "GND", "C1210"); c("C136", "22u 25V 1210", "+12V_FAN", "GND", "C1210"); c("C137", "4u7 10V", "F12_VCC", "GND")\nc("C138", "100n", "F12_BST1", "F12_SW1"); c("C139", "100n", "F12_BST2", "F12_SW2")\nr("R105", "1M 1%", "+12V_FAN", "F12_FB"); r("R106", "90.9k 1%", "F12_FB", "GND"); r("R107", "40.2k", "F12_VC", "F12_VCn"); c("C140", "820p", "F12_VCn", "GND")\nr("R108", "10k", "+12V_FAN", "F12_FFn"); c("C141", "33p", "F12_FFn", "F12_FB"); r("R109", "35.7k 1%", "F12_RT", "GND")\nr("R103", "1.5M 1%", "VSYS_E", "F12_RUN"); r("R104", "255k 1%", "F12_RUN", "GND")\n_intent.node("F12_SW1", 17.4, "U22\'s buck-side switching node: it swings to VSYS_E (at most 17.375 V) and to ground", v_min=-1.0)\n_intent.node("F12_SW2", 12.3, "U22\'s boost-side switching node: it swings to +12V_FAN (12.2 V at FB\'s upper limit) and to ground", v_min=-1.0)\n_intent.node("F12_BST1", 17.4 + 5.5, "U22\'s buck-side bootstrap: it rides on F12_SW1 by the VCC regulator\'s output")\n_intent.node("F12_BST2", 12.3 + 5.5, "U22\'s boost-side bootstrap: it rides on F12_SW2 by the VCC regulator\'s output")\nfor n in ("1", "2"):\n    _intent.node("FAN%s_PWM_OD" % n, 12.0, "mixer fan %s\'s PWM input, driven open-drain by Q%s (the fan\'s own pull-up; its level NOT READ, Layer 7): at most the fan\'s 12 V supply" % (n, "9" if n == "1" else "10"))\n'
_SW_OLD = 'for n in ("1", "2"):\n    _intent.node("FAN%s_SW" % n, 16.8 + 0.55, "mixer fan %s\'s switched low side (J_FAN%s pin 2, Q%s\'s drain): 0 V with the FET "\n'
_SW_NEW = '# L4-E11 section 18: the FANn_SW nodes of the chopped supply are gone with D7 and D8; the fans\' PWM inputs are the nodes FANn_PWM_OD above.\n_FAN_SW_RETIRED = ("1", "2")\nfor n in ():\n    _intent.node("FAN%s_SW" % n, 16.8 + 0.55, "mixer fan %s\'s switched low side (J_FAN%s pin 2, Q%s\'s drain): 0 V with the FET "\n'
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
    (_FAN_OLD, _FAN_NEW),
    (_SW_OLD, _SW_NEW),
    ('"TSOT6": "Package_TO_SOT_SMD:TSOT-23-6", "SOT235": "Package_TO_SOT_SMD:SOT-23-5",',
     '"TSOT6": "Package_TO_SOT_SMD:TSOT-23-6", "SOT235": "Package_TO_SOT_SMD:SOT-23-5", "HTSSOP20EP": "Package_SO:HTSSOP-20-1EP_4.4x6.5mm_P0.65mm_EP3.4x6.5mm", "L6060": "Inductor_SMD:L_Coilcraft_XAL6060-XXX",'),
    ('"R42", "R43", "D9", "J_FAN1", "Q9", "R44", "R46", "D7", "J_FAN2", "Q10", "R45", "R47", "D8",',
     '"R42", "R43", "D9", "J_FAN1", "Q9", "R44", "R46", "J_FAN2", "Q10", "R45", "R47", "U22", "L4", "C135", "C136", "C137", "C138", "C139", "C140", "C141", "R103", "R104", "R105", "R106", "R107", "R108", "R109",'),
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
