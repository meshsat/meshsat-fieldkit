#!/usr/bin/env python3
"""apply_gen_sch_b_vcoremon.py: DRAFT for board B's generator owner (record l9t5, Layer 4 task L4A-59, the ledger's HO-E; MESHSAT-1357,
W140, 7 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies. It is order-free against the
other drafts of board B: it touches only each supervisor's reset block and the decoupling class table, which no other pending draft
edits (record l9t5's iocpre, canshdn, iocset and iocguard, W137's canmb and W138's regstage are read for it in l9t5_hoe.out).

The correction (l9t5_hoe.out sections 5 and 8; HO-E-COMPARISON.md): a VCORE monitor per supervisor, independent of its firmware.
Each STM32H743's core voltage is on its VCAP pins (48 and 73, net IOC{t}_VCAP); ST prints that core voltage per voltage scale
(DS12110 Rev 11 Table 112, p.209: VOS3 0.95 to 1.05 V, VOS1 1.15 to 1.26 V, VOS0 1.26 to 1.40 V with the LDO on). A TI TPS37 (channel 1
overvoltage, the adjustable 0.8 V option "01", open-drain active-low, 2 % hysteresis) senses VCAP through a 0.1 % divider and holds
the supervisor's NRST low whenever VCAP is over a threshold that lies above VOS3's band and below VOS1's, so every entry to VOS1 and
therefore to VOS0 (RM0433 Rev 8 p.280: "VOS0 can be enabled only when VOS1 is programmed") resets the controller to its reset
state (RM0433 p.279: "After reset, the system starts on the lowest Run mode voltage scaling (VOS3)"), whatever its firmware does.
Per supervisor t (k = 0, 1, 2 for A, B, C; designators in the free 810 to 839 range of board B):
  U810+10k  TPS37 in WSON-10 (DSK): 1 VDD on the controller's own +3V3_IOC{t}; 2 SENSE1 on IOC{t}_VMON; 3 SENSE2 on +3V3_IOC{t} (the
            undervoltage channel held inert); 4 RESET1 on IOC{t}_MONRST; 5 RESET2, 6 CTR1/MR, 7 CTS1, 8 CTS2, 9 CTR2/MR open (the
            shortest delays, SNVSBJ1E Table 6-1 p.5); 10 GND; 11 the pad on GND (p.5: "can be connected to GND")
  R810+10k  the divider's top, VCAP to VMON (TOP below)        R811+10k  its bottom, VMON to GND (BOTTOM below)
  R812+10k  750 Ohm 1 % from MONRST to IOC{t}_RST_n: it keeps the open drain's current inside the recommended 5 mA while it
            discharges the reset capacitor (C409, C429, C449, 100 nF, ST's Figure 74) from the rail
  C810+k    100 nF at the TPS37's VDD (Table 6-1, p.5: "Bypass with a 0.1 uF capacitor to GND")
The values are the record's selection (l9t5_hoe.out section 5d, SESSION W140-2): the E96 top that keeps the threshold band inside
(1.05, 1.15) V with the largest least margin. No pin of the controller changes; no other part, net or declaration changes. The land
id WSON-10 2.5 x 2.5 mm is this draft's ASSUMPTION (the land check runs only where KiCad is; Layer 10). The TPS37's order code and
LCSC code are owed (Layer 6): TI's section 5 reads "minimum order quantities may apply".
Usage:  apply_gen_sch_b_vcoremon.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the change is already applied, an old text is missing, a designator the draft adds is
already drawn, or the repository's own generator is named before RELEASE-T10.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_vcoremon"
BOARD = "b"
TOP = "39.2k 0.1% 25ppm"       # IOC{t}_VCAP to IOC{t}_VMON
BOTTOM = "100k 0.1% 25ppm"     # IOC{t}_VMON to GND
SERIES = "750R 1%"             # IOC{t}_MONRST to IOC{t}_RST_n
LAND = "Package_SON:WSON-10-1EP_2.5x2.5mm_P0.5mm_EP1.2x2mm"
MONITOR = "TPS37 OV/UV monitor (CH1 OV adjustable 0.8 V option 01, open-drain active-low, 2 percent hysteresis; order code owed)"
ADDS = tuple("U%d" % (810 + 10 * k) for k in range(3)) + tuple("R%d" % (810 + 10 * k + n) for k in range(3) for n in range(3)) \
    + tuple("C%d" % (810 + k) for k in range(3))

_OLD_RST = '    r(R_(0), "10k", "IOC%s_RST_n" % _tag, v33); c(C_(9), "100n", "IOC%s_RST_n" % _tag, "GND")\n'
_NEW_RST = (_OLD_RST
            + '    # HO-E (record l9t5, Layer 4 task L4A-59, W140): a VCORE monitor of this controller, on its own rail and its own reset only.\n'
            + '    # A TPS37 (SNVSBJ1E) senses VCAP through a 0.1 % divider and holds NRST low while VCAP is over the band VOS3 may occupy\n'
            + '    # (DS12110 Rev 11 Table 112: VOS3 0.95 to 1.05 V, VOS1 from 1.15 V, VOS0 from 1.26 V), so an entry to VOS1 or VOS0 by any\n'
            + '    # firmware resets the controller to VOS3 (RM0433 Rev 8 p.279); the threshold band and the timing are l9t5_hoe.out section 5d.\n'
            + '    ic("U%%d" %% (810 + 10 * _k), 11, "%s, controller %%s: holds NRST while VCAP is over the VOS3 band" %% _tag, "%s",\n' % (MONITOR, LAND)
            + '       {"1": v33, "2": "IOC%s_VMON" % _tag, "3": v33, "4": "IOC%s_MONRST" % _tag, "5": "NC", "6": "NC", "7": "NC", "8": "NC",\n'
            + '        "9": "NC", "10": "GND", "11": "GND"})\n'
            + '    r("R%%d" %% (810 + 10 * _k), "%s", "IOC%%s_VCAP" %% _tag, "IOC%%s_VMON" %% _tag)\n' % TOP
            + '    r("R%%d" %% (811 + 10 * _k), "%s", "IOC%%s_VMON" %% _tag, "GND")\n' % BOTTOM
            + '    r("R%%d" %% (812 + 10 * _k), "%s", "IOC%%s_MONRST" %% _tag, "IOC%%s_RST_n" %% _tag)\n' % SERIES
            + '    c("C%d" % (810 + _k), "100n", v33, "GND")\n'
            + '    _intent.bypass("C%d" % (810 + _k), "U%d" % (810 + 10 * _k), "1", v33)\n'
            + '    _intent.node("IOC%s_VMON" % _tag, 1.40,\n'
            + '                 "controller %s\'s VCORE monitor sense node: VCAP through the divider, at most VCAP\'s 1.40 V (DS12110 Rev 11 Table 112)" % _tag)\n'
            + '    _intent.node("IOC%s_MONRST" % _tag, _intent.net_volts(v33),\n'
            + '                 "controller %s\'s VCORE monitor output: an open drain pulled to the controller\'s own 3.3 V through NRST\'s pull-up" % _tag)\n')
_OLD_CLASS = '    if pv.startswith("TPS3808"):\n'
_NEW_CLASS = ('    if pv.startswith("TPS37 "):   # HO-E (record l9t5, L4A-59): the supervisors\' VCORE monitors\n'
              '        return ("D", "TI TPS37 SNVSBJ1E (v2/vendor/ti/ti-tps37-snvsbj1e.pdf) Table 6-1, VDD: \\"Input Supply Voltage: Bypass with a "\n'
              '                     "0.1 uF capacitor to GND.\\" (p.5; the micro sign written u)")\n'
              + _OLD_CLASS)
EDITS = [(_OLD_RST, _NEW_RST), (_OLD_CLASS, _NEW_CLASS)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if "_VMON" in text or "_MONRST" in text:
        refuse("the change is already applied")
    for ref in ADDS:
        if re.search(r'(?:\br|\bc|\bic|\bpart)\(\s*"%s"' % ref, text):
            refuse("%s is already drawn as a literal designator" % ref)
    if not re.search(r'for _tag, _k in \(\("A", 0\), \("B", 1\), \("C", 2\)\):', text):
        refuse("the supervisors' loop (_tag, _k over A, B, C) is not the one this draft was written against")
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once: %r" % (new.count(old), old[:60]))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: record l9t5 drafts this change for the generator's owner and never applies it. Writing the repository's own generator
# is refused until RELEASE-T10.md beside this script reads "released: yes" on its first line and names an accepted check of task T10
# ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the record and its test do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_%s.py" % BOARD)
RELEASE = os.path.join(HERE, "RELEASE-T10.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE-T10.md; record l9t5's T10 drafts wait on an accepted check")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE-T10.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE-T10.md names no single check")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_%s.py" % BOARD, "b/gen_sch_%s.py" % BOARD, n=0))
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
