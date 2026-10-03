#!/usr/bin/env python3
"""apply_gen_sch_b_ph4.py: DRAFT for board B's generator owner (Layer 8 record l8r2, item 3, finding L5R2-F04, MESHSAT-1357,
3 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies.

The defect (L5R2-F04, HF-F04's class): board B's J_QMX is drawn on the land key PH1x4, which board B's footprint table maps to
Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical, a 2.54 mm pin header, while IF-LID-HF and ASSEMBLY.md section 4 say
PH 1x4 ("QMX USB | B16 `J_QMX` (PH 1x4) | ... PH at B16, USB-C at the unit", a lead made to a least bend radius of 20 in the lid
harness). J_CAM carries the same key while ASSEMBLY.md says "Camera | B16 `J_CAM` (PH 1x4) | ... PH both ends" (HF-F04, recorded
for IF-CAM). The evidence supports the JST PH land: both texts name it, the leads are made to it, and boards A (J_USBW) and D
(J_USB3) already fit the same 1x4 JST PH socket for the same kind of USB lead.

The correction: board B's footprint table gains PH4 = Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical (board A's key and
land), and J_QMX and J_CAM take it with JST's B4B-PH-K-S (LCSC C131334, the part J_USBW carries; JST PH catalogue, held at
v2/vendor/connectors/jst-ph-catalogue.pdf). The pins keep their numbers and nets (1 VBUS, 2 D-, 3 D+, 4 GND). PH1x4 stays in the
table (other headers on board B use it).

Usage:  apply_gen_sch_b_ph4.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_ph4"
GEN = "gen_sch_b.py"
ADDS = ()
NETS = ()
EDITS = [
    ('"PH1x4": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",',
     '"PH1x4": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", "PH4": "Connector_JST:JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical",   # l8r2 (L5R2-F04): the JST PH 1x4 of J_QMX and J_CAM, board A\'s key'),
    ('"QMX USB lead (bank 2 hub, port 4): VBUS D- D+ GND; pigtail to the unit\'s USB-C", "PH1x4",',
     '"QMX USB lead (bank 2 hub, port 4): VBUS D- D+ GND; JST PH 1x4 (B4B-PH-K-S), the lid harness\'s lead to the unit\'s USB-C (L5R2-F04)", "PH4",'),
    ('{"1": "VBUS_QMX", "2": "QMX_DM", "3": "QMX_DP", "4": "GND"}); esd("U35"',
     '{"1": "VBUS_QMX", "2": "QMX_DM", "3": "QMX_DP", "4": "GND"}, "C131334"); esd("U35"'),
    ('"camera lead (USB 2.0, bank 1 hub, port 3): 5V D- D+ GND", "PH1x4", {"1": "+5V_CAM", "2": "CAM_DM", "3": "CAM_DP", "4": "GND"})',
     '"camera lead (USB 2.0, bank 1 hub, port 3): 5V D- D+ GND; JST PH 1x4 (B4B-PH-K-S, HF-F04)", "PH4", {"1": "+5V_CAM", "2": "CAM_DM", "3": "CAM_DP", "4": "GND"}, "C131334")'),
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
