#!/usr/bin/env python3
"""apply_gen_sch_a_ptc.py: DRAFT for board A's generator owner (Layer 8 record l8p, MESHSAT-1357, 4 October 2026). NOT APPLIED
to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).

Board A's half of the pack breaker's make-last enable loop (record l9stk section 15.4, C-1b, and 15.5, THE THERMAL GUARD,
SELECTED; owners "board A's generator with L4-E11 for the PTC beside the battery FETs"; branch fnd/l9stk at 2c8b29fb, unchanged at 0d72880b). The loop
from board P crosses the dock on two contacts and passes, on this board, the kit's PRF15BB103 chip PTC on the battery FETs'
copper. Murata prints for PRF15BB103RB6RC (DM-SA16-E056 Rev.1 201608, 3.1, p.4): 10 kOhm +-50 % at 25 C, 100 kOhm at a sensing
temperature over 110 C, 4.7 MOhm at 130 +-3 C, 32 V. The first inverter on board P is surely off from 341.2 kOhm at 16.8 V (the
loop's parts at 1 %), so the breaker is off before the PTC's copper passes 133 C: a guard against the battery FETs' installed path
never being met, unit by unit. Its no-trip side is NOT printed (finding L8P-F07, OPEN: L8P-BREAKER.md section 12j; E-13): the
guard's design is record l9stk's next round, and this draft draws the part that record selected.
(Rounds 1 to 5 quoted record l9stk 15.5 here, a 47 kOhm point at 130 +-3 C and a trip between it and a 338 kOhm point: that
column of Murata's table belongs to its 470 ohm parts, not to this one. Corrected in round 6, in this text, in the comment the
draft writes and in RT1's value text.)

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else:
  J_DOCK  pins 3 and 5 (until now ground) carry DOCK_EN_RET and DOCK_EN_OUT, pin 4 the ground between them in the 2 x 6 field's
          first row (C2); written as a post-edit of the part's own map after its call, which first asserts that pins 3 to 5 are
          still ground, so L4-E11's edit of the same call (pin 1 to VSYS_DOCK) applies in either order;
  RT1     PRF15BB103RB6RC (Murata, C443668, board P's RT1 part and land) from DOCK_EN_OUT to DOCK_EN_RET, placed on the battery
          FETs' copper (Q39, Q40 and L4-E11's third FET): the land and its thermal coupling are the layout's (L8P-10);
  intent  DOCK_EN_OUT and DOCK_EN_RET declared as nodes (board P's bounds, l9stk 15.4); one schematic section for RT1.
Not drawn here: the third battery FET (15.5, SELECTED), whose designator is L4-E11's to give (Q41 is record l8r2's VIN_RAW cut-off
FET); RT1 sits beside all three once L4-E11 draws it.
SESSION choices (L8P-BREAKER.md section 3): the designator RT1 (board A carries no RT designator), the dock positions 3 and 5
with 4 between, the 0402 land of board P's RT1.

Order: released with apply_gen_sch_p_breaker.py and apply_gen_sch_e_enable.py (never alone: the dock's two ends change together);
in board A's round in any position: it inserts before two lines that l8gnd's GND-002 draft also inserts before (each keeps the
line once), touches no text L4-E11's charger draft replaces, and adds no R or C (d8dec31's mainpb takes the next free R and C).

Usage:  apply_gen_sch_a_ptc.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator or
net is in use, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_ptc"
ADDS = ("RT1",)
NETS = ("DOCK_EN_OUT", "DOCK_EN_RET")

_ANCHOR_MAIN = ("# --- main power control LTC2954-1 (ltc2954.pdf): the panel MAIN button, EN to every converter's enable (RAIL_EN), "
                "INT = shutdown request, KILL from the panel controller through Q1\n")
_LOOP = (
    '# RECORD l8p (MESHSAT-1357, 4 October 2026; record l9stk 15.4, C-1b and condition C2, and 15.5, THE THERMAL GUARD): THE PACK\n'
    '# BREAKER\'S DOCK ENABLE LOOP CROSSES THIS BOARD. Board P\'s LM5069-1 breaker (record l8p\'s apply_gen_sch_p_breaker.py) is held off\n'
    '# unless a loop from its input, out over board E and the dock and back, is closed: J_DOCK pins 5 (DOCK_EN_OUT) and 3 (DOCK_EN_RET)\n'
    '# with pin 4, between them in the 2 x 6 field\'s first row, still ground (C2: a short between the two conductors meets ground\n'
    '# first). On this board the loop passes RT1, the kit\'s PRF15BB103 chip PTC, on the battery FETs\' copper: Murata prints 100 kOhm\n'
    '# over 110 C and 4.7 MOhm at 130 +-3 C, so the breaker is off before RT1\'s copper passes 133 C (its no-trip side is not printed:\n'
    '# record l8p\'s L8P-F07, OPEN; E-13), the guard against the battery FETs\' installed path never being met. The two enable\n'
    '# contacts mate at least 1 mm after every power pin (C1, Layer 7). The third battery FET is\n'
    '# L4-E11\'s to draw and name; RT1 sits beside all three. The map is changed after the call, which is left for the drafts that\n'
    '# edit it (L4-E11\'s pin 1); it refuses if pins 3 to 5 are not all ground any more.\n'
    'for _p8 in P:\n'
    '    if _p8["ref"] == "J_DOCK":\n'
    '        if (_p8["nets"]["3"], _p8["nets"]["4"], _p8["nets"]["5"]) != ("GND", "GND", "GND"):\n'
    '            raise SystemExit("record l8p: J_DOCK pins 3 to 5 are %r, not the ground the enable loop takes" % ((_p8["nets"]["3"], _p8["nets"]["4"], _p8["nets"]["5"]),))\n'
    '        _p8["nets"]["3"], _p8["nets"]["5"] = "DOCK_EN_RET", "DOCK_EN_OUT"\n'
    '        _v8 = re.sub(r"\\b([12])-7 GND, 8 SHORE_INHIBIT", lambda _m: "%s, 4, 6, 7 GND, 3 DOCK_EN_RET and 5 DOCK_EN_OUT (the pack breaker\'s make-last enable loop through RT1, record l8p), 8 SHORE_INHIBIT"\n'
    '                     % ("1, 2" if _m.group(1) == "1" else "2"), _p8["value"], count=1)\n'
    '        if _v8 == _p8["value"]:\n'
    '            raise SystemExit("record l8p: J_DOCK\'s description no longer names its ground pins as 1-7 or 2-7")\n'
    '        _p8["value"] = _v8\n'
    'part("RT1", "Device", "Thermistor_PTC", "PRF15BB103RB6RC chip PTC 10k, 100k over 110 C, 4.7M at 130 C (Murata): the pack breaker\'s thermal guard in the dock enable loop, on the battery FETs\' copper (record l8p; l9stk 15.5)",\n'
    '     "Resistor_SMD:R_0402_1005Metric", {"1": "DOCK_EN_OUT", "2": "DOCK_EN_RET"}, "C443668")\n'
    '_intent.node("DOCK_EN_OUT", 29.2, "the pack breaker\'s enable loop from board P (its BRK_VIN through 10 kOhm, BRK_VIN itself with the "\n'
    '             "loop open), J_DOCK pin 5 to RT1: at most the breaker\'s input clamp, 29.2 V (record l9stk 15.4)", v_work=16.8)\n'
    '_intent.node("DOCK_EN_RET", 17.4, "the loop\'s return from RT1 to J_DOCK pin 3 and board P\'s first inverter gate: at most 17.4 V under "\n'
    '             "the clamp\'s 29.2 V (record l9stk 15.4, the inverters\' bounds)")\n')

_ANCHOR_LISTED = "_listed = {r for _, refs in SECTIONS for r in refs}\n"
_SEC = ('SECTIONS.append(("THE PACK BREAKER\'S DOCK ENABLE LOOP: THE THERMAL GUARD RT1 ON THE BATTERY FETS\' COPPER (RECORD l8p)", ["RT1"]))   # Layer 8 record l8p\n')

EDITS = [
    (_ANCHOR_MAIN, _LOOP + _ANCHOR_MAIN),
    (_ANCHOR_LISTED, _SEC + _ANCHOR_LISTED),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def code_only(text):
    return "\n".join(l.split("#")[0] for l in text.splitlines())


def patched(text):
    code = code_only(text)
    for ref in ADDS:
        if re.search(r'"%s"' % re.escape(ref), code):
            refuse("designator %s is already in use in the target" % ref)
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), code):
            refuse("net %s already exists in the target" % net)
    if not re.search(r"^import re\b", text, re.M):
        refuse("the target does not import re, which the J_DOCK post-edit uses")
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once: %r" % (new.count(old), old[:70]))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: record l8p drafts this change for board A's generator owner and never applies it. Writing the repository's own
# gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; l8p's drafts wait on an accepted check")
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
