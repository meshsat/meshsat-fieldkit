#!/usr/bin/env python3
"""apply_gen_sch_e_enable.py: DRAFT for board E's generator owner (Layer 8 record l8p, MESHSAT-1357, 4 October 2026). NOT
APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write scratch copies).

Board E's half of the pack breaker's make-last enable loop (record l9stk section 15.4, C-1b, conditions C1 and C2; DD-6's owner
row "board E's generator (two J_SMB contacts with a ground between)"; branch fnd/l9stk at 2c8b29fb). Board E is a pass-through:
the loop comes from board P on the SMBus lead and leaves for the dock block on the signal lands, and nothing on this board
touches it. Board P's draft (apply_gen_sch_p_breaker.py) drives it, board A's (apply_gen_sch_a_ptc.py) closes it through the
thermal guard RT1.

What it changes in v2/ecad/tools/gen_sch_e.py, and nothing else:
  J_SMB  a JST-XH 1x7 (B7B-XH-A), P's pin for pin: 1 SMBC, 2 SMBD, 3 GND, 4 PRES_LEAD (unchanged), 5 DOCK_EN_RET, 6 GND (the
         ground contact between the two loop conductors, C2), 7 DOCK_EN_OUT; no order code (the 7-way code is Layer 6's, L8P-06);
  J_BLK  pins 3 and 5 (until now ground) carry DOCK_EN_RET and DOCK_EN_OUT to the block, with pin 4 the ground between them on the
         block's 2 x 6 field (C2 "and on the block"); written as a post-edit of the part's own map after its call, which first
         asserts that pins 3 to 5 are still ground, so L4-E11's edit of the same call (pin 1 to VSYS_E) applies in either order;
  intent DOCK_EN_OUT and DOCK_EN_RET declared as nodes (board P's bounds, l9stk 15.4);
  title  the pack entry's schematic section names the 1x7 lead.
SESSION choices (L8P-BREAKER.md section 3): the dock positions 3 and 5 with 4 between (the only pair of free ground positions in
one row with a ground between whose outgoing conductor has no signal neighbour: pin 5's neighbours 4, 6 and 11 are ground), and
DOCK_EN_RET beside PRES on J_SMB (a short there pulls the gate side, never back-powers the controller from BRK_VIN).

Order: released with apply_gen_sch_p_breaker.py and apply_gen_sch_a_ptc.py (never alone: J_SMB's two ends and the dock's two
ends must change together); in board E's round in any position (no other board E draft touches J_SMB, the J_BLK pins it moves,
the line it inserts before, or the section title).

Usage:  apply_gen_sch_e_enable.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a net is in use,
or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_e_enable"
ADDS = ()
NETS = ("DOCK_EN_OUT", "DOCK_EN_RET")

_OLD_JSMB = ('part("J_SMB", "Connector_Generic", "Conn_01x04", "SMBus lead to board P, JST-XH 1x4 (B4B-XH-A), P\'s pin order: 1 SMBC, 2 SMBD, 3 GND, 4 PRES", "XH4",\n'
             '     {"1": "SMBC", "2": "SMBD", "3": "GND", "4": "PRES_LEAD"}, "C144395")\n')
_NEW_JSMB = (
    '# RECORD l8p (MESHSAT-1357, 4 October 2026; record l9stk 15.4, C-1b and condition C2): THE LEAD CARRIES THE PACK BREAKER\'S\n'
    '# DOCK ENABLE LOOP. Board P\'s J_SMB is a 1x7 now, so this end is the same 7-circuit JST XH header (B7B-XH-A, the held catalogue\'s\n'
    '# page 5 table), pin for pin P\'s order: 1 to 4 as round 4 set them, 5 DOCK_EN_RET, 6 GND (the ground contact between the two\n'
    '# loop conductors), 7 DOCK_EN_OUT. The loop passes this board untouched to J_BLK pins 3 and 5 (below). The 4-way code C144395\n'
    '# goes with the 4-way header; the 7-way code is Layer 6\'s to pin here (L8P-06).\n'
    'part("J_SMB", "Connector_Generic", "Conn_01x07", "SMBus and dock enable lead to board P, JST-XH 1x7 (B7B-XH-A), P\'s pin order: 1 SMBC, 2 SMBD, 3 GND, 4 PRES, 5 DOCK_EN_RET, 6 GND, 7 DOCK_EN_OUT",\n'
    '     "Connector_JST:JST_XH_B7B-XH-A_1x07_P2.50mm_Vertical", {"1": "SMBC", "2": "SMBD", "3": "GND", "4": "PRES_LEAD", "5": "DOCK_EN_RET", "6": "GND", "7": "DOCK_EN_OUT"})\n')

_ANCHOR_PVR = 'part("P_VR", "Connector", "Conn_01x01_Pin", "solder pad, 12 AWG wire to the block board VIN_RAW targets (board A\'s four 9 A power pins J_VR1-4, EQ-16)", "PAD86", {"1": "VIN_RAW"})\n'
_BLK = (
    '# RECORD l8p (MESHSAT-1357, 4 October 2026; record l9stk 15.4, C-1b, condition C2 "a ground contact between them in J_SMB and\n'
    '# on the block"): J_BLK pins 3 and 5 carry the pack breaker\'s enable loop to the block (DOCK_EN_RET and DOCK_EN_OUT, board A\'s\n'
    '# J_DOCK pins 3 and 5), and pin 4, between them in the 2 x 6 field\'s first row, stays ground. Written onto the part\'s own map\n'
    '# after its call so the call itself is left for the drafts that edit it (L4-E11\'s pin 1); it refuses if pins 3 to 5 are not\n'
    '# all ground any more, which would mean another change took them.\n'
    'for _p8 in P:\n'
    '    if _p8["ref"] == "J_BLK":\n'
    '        if (_p8["nets"]["3"], _p8["nets"]["4"], _p8["nets"]["5"]) != ("GND", "GND", "GND"):\n'
    '            raise SystemExit("record l8p: J_BLK pins 3 to 5 are %r, not the ground the enable loop takes" % ((_p8["nets"]["3"], _p8["nets"]["4"], _p8["nets"]["5"]),))\n'
    '        _p8["nets"]["3"], _p8["nets"]["5"] = "DOCK_EN_RET", "DOCK_EN_OUT"\n'
    '        _v8 = re.sub(r"\\b([12])-7 GND, 8 SHORE_INHIBIT", lambda _m: "%s, 4, 6, 7 GND, 3 DOCK_EN_RET and 5 DOCK_EN_OUT (the pack breaker\'s dock enable loop, record l8p), 8 SHORE_INHIBIT"\n'
    '                     % ("1, 2" if _m.group(1) == "1" else "2"), _p8["value"], count=1)\n'
    '        if _v8 == _p8["value"]:\n'
    '            raise SystemExit("record l8p: J_BLK\'s description no longer names its ground pins as 1-7 or 2-7")\n'
    '        _p8["value"] = _v8\n'
    '_intent.node("DOCK_EN_OUT", 29.2, "the pack breaker\'s enable loop from board P (BRK_VIN through 10 kOhm, BRK_VIN itself with the loop "\n'
    '             "open), J_SMB pin 7 to J_BLK pin 5: at most the breaker\'s input clamp, 29.2 V (record l9stk 15.4)", v_work=16.8)\n'
    '_intent.node("DOCK_EN_RET", 17.4, "the loop\'s return to board P\'s first inverter gate, J_BLK pin 3 to J_SMB pin 5: at most 17.4 V "\n'
    '             "under the clamp\'s 29.2 V (record l9stk 15.4, the inverters\' bounds)")\n')

_OLD_SEC = '"PACK ENTRY: PACK CABLE ON XT60, 25 A BLADE, PADS TO THE BLOCK, PACK SMBUS LEAD (JST-XH 1x4)"'
_NEW_SEC = '"PACK ENTRY: PACK CABLE ON XT60, 25 A BLADE, PADS TO THE BLOCK, PACK SMBUS AND DOCK ENABLE LEAD (JST-XH 1x7)"'

EDITS = [
    (_OLD_JSMB, _NEW_JSMB),
    (_ANCHOR_PVR, _BLK + _ANCHOR_PVR),
    (_OLD_SEC, _NEW_SEC),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def code_only(text):
    return "\n".join(l.split("#")[0] for l in text.splitlines())


def patched(text):
    code = code_only(text)
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), code):
            refuse("net %s already exists in the target" % net)
    if not re.search(r"^import re\b|^import re,|^import re, ", text, re.M):
        refuse("the target does not import re, which the J_BLK post-edit uses")
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


# NOT RELEASED: record l8p drafts this change for board E's generator owner and never applies it. Writing the repository's own
# gen_sch_e.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_e.py")
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
