#!/usr/bin/env python3
"""apply_gen_sch_b_iocbuck.py: DRAFT for board B's generator owner (Layer 9 record l9t5, task T5, I-03 on the case row C-DEV rev 1,
MESHSAT-1357, 4 October 2026), board B's half of apply_gen_sch_a_iocbuck.py. NOT APPLIED to the tree by this record; its author ran it
only on scratch copies (the tests write scratch copies).

The correction (record l9t5 out 5, option (b), SESSION): the three supervisors' private LDOs (U40, U50, U60, AP2112K-3.3, each the
own regulator of one controller's failure domain, ARCH-PCB-B-IOHA) take their input from +5V_IOC, a new rail that arrives from board
A's buck U601 on its own JST-VH lead, instead of +5V_DEV. Each controller keeps its own LDO, its own EN pull-up and bench jumper and
its own input capacitor; only the net they hang from changes, so one controller's fault still cannot pull the other two down through
a regulator they share (they shared U7's +5V_DEV before; they share U601's +5V_IOC now).
What it changes in v2/ecad/tools/gen_sch_b.py, and nothing else:
  1. the three LDOs' VIN (pin 1), their EN pull-ups R66, R78, R90 and their input capacitors C400, C420, C440 from +5V_DEV to +5V_IOC
     (the loop over the controllers draws all three from one text);
  2. +5V_DEV's allocations lose U40, U50 and U60 (0.12 A each) and its typical 3.8 to 3.44 A; its peak from its basis since round 3
     (record l8r2's finding L8R2-F35: rounds 1 and 2 kept a typed 6.0 A and said it overstated, which it did not): 6.0359 A, Layer 9's
     budget for this lead at HIGH with every load at constant power at the least load voltage 4.9019 V and the supervisors on +5V_IOC
     (29.5871 W; record l9t5's l9t5_drafts.out section 6), rounded up to 0.1 mA;
  3. +5V_IOC declared after +5V_DEV: 0.36 A typical (the same three 0.12 A allocations); 1.4749 A peak from its basis (rv-pwr's HIGH
     for the three supervisors, 7.0380 W at the LDOs' inputs: each H743 at 400 mA, DS12110 Rev 10 Table 30's maximum at TJ 85 C, plus
     60 mA, 1.3800 A of LDO current; at constant power at the rail's least load voltage 4.7719 V, rounded up), its source the lead
     J_5V_IOC (16 AWG, 150 mm, VH crimp both ends, the device lead's make, v2/docs/ASSEMBLY.md section 4); the three +3V3_IOCx rails
     fed from it;
  4. GND keeps the three LDOs among its loads and names J_5V_IOC a source. Round 3 (L8R2-F35): the return does NOT come back lead by
     lead: boards A and B share one ground, so J_5V_IOC's pin 2 carries a share of the whole A to B return divided by resistance over
     the VH contacts and the ribbons' ground conductors (record l8r2 round 7, its finding L8R2-F31, OPEN), whatever U601 supplies;
  5. J_5V_IOC (JST-VH socket, 10 A), its clamp D900 (SMBJ5.0A, as D1 on +5V_DEV) and its bulk C900 (10 uF) beside J_5V_DEV, in the
     shared power section.
Order: board B's round, after record l8gnd's GND-002 (R-195) and record l8r2's board B drafts (R-190, R-203, and its ph4 and panel5v),
before Layer 6's tables; none of those touch its anchors. In one release with apply_gen_sch_a_iocbuck.py.
Usage:  apply_gen_sch_b_iocbuck.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator or net is in
use, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_iocbuck"
ADDS = ("J_5V_IOC", "D900", "C900")
NETS = ("+5V_IOC",)
IOC_TYP, IOC_PEAK = 0.36, 1.4749        # A: the three 0.12 A allocations; 7.0380 W (rv-pwr's HIGH) at 4.7719 V, rounded up (round 3)
DEV_LEAD_PEAK = 6.0359                  # A: this lead on C-DEV rev 1 with the draft, 29.5871 W at 4.9019 V, rounded up (round 3, L8R2-F35)

_OLD_LOADS = '              "U40": 0.12, "U50": 0.12, "U60": 0.12,      # the three controllers\' private 3.3 V LDOs (AP2112K-3.3): each child rail\n'
_NEW_LOADS = ('              # U40, U50 and U60 left this rail for +5V_IOC (record l9t5, I-03): _IOC_LOADS below carries their 0.12 A each.\n'
              '              # Before: the three controllers\' private 3.3 V LDOs (AP2112K-3.3): each child rail\n')
_OLD_DEV = '_intent.rail("+5V_DEV", 5.0, 3.8, 6.0, "J_5V_DEV", loads=_DEV_LOADS,'
_NEW_DEV = '_intent.rail("+5V_DEV", 5.0, 3.44, %.4f, "J_5V_DEV", loads=_DEV_LOADS,' % DEV_LEAD_PEAK
_OLD_DEVNOTE = '             note="the device rail from A22; +0.8 A since the three hubs and their cores moved off the slot rails (ARCH-PCB-B-IOHA)")\n'
_NEW_DEVNOTE = (
    '             note="the device rail from A22; +0.8 A since the three hubs and their cores moved off the slot rails (ARCH-PCB-B-IOHA); "\n'
    '                  "the three supervisors\' LDOs moved to +5V_IOC (record l9t5, I-03), their 0.36 A out of the typical; the peak %.4f A is "\n'
    '                  "Layer 9\'s budget for this lead at HIGH, every load at constant power at the least load voltage 4.9019 V (29.5871 W, "\n'
    '                  "C-DEV rev 1 with the draft; record l9t5 round 3), where a typed 6.0 A stood under it (record l8r2\'s L8R2-F35)")\n'
    "# I-03, RECORD l9t5 (task T5, MESHSAT-1357, 4 October 2026; v2/docs/records/l9t5/ out 5): THE SUPERVISORS' OWN 5 V. Board A's\n"
    "# device rail U7 reads 7.4717 A on the case row C-DEV rev 1 against its loop's least 7.0957 A; the three controllers' LDOs (1.4358 A\n"
    "# of it at HIGH) move to +5V_IOC, board A's TPS62933 U601 on RAIL_EN over its own JST-VH lead J_5V_IOC. Each controller keeps its\n"
    "# own LDO, EN pull-up, bench jumper and input capacitor. DRAFTED, not applied (apply_gen_sch_a_iocbuck.py is board A's half).\n"
    "# ROUND 3 (record l8r2's finding L8R2-F35): the lead is the device lead's make (16 AWG, 150 mm, VH crimp both ends, ASSEMBLY.md\n"
    "# section 4). Its pin 1 carries this rail and nothing else; its pin 2 is one more contact of the ONE ground boards A and B share,\n"
    "# and carries a share of the whole return divided by resistance (record l8r2 round 7, finding L8R2-F31, OPEN), not this rail's own.\n"
    '_IOC_LOADS = {"U40": 0.12, "U50": 0.12, "U60": 0.12}   # the allocations +5V_DEV carried for them (S-98 M7)\n'
    '_intent.rail("+5V_IOC", 5.0, %.2f, %.4f, "J_5V_IOC", loads=_IOC_LOADS, budget=0.02, share=0.015, converted=False,\n'
    '             always_on=True, always_on_why="it arrives from board A\'s U601 (EN on RAIL_EN) over its own JST-VH lead; nothing on this board switches it",\n'
    '             note="record l9t5 (I-03): the three supervisors\' LDOs U40, U50, U60 over the lead J_5V_IOC (16 AWG, 150 mm, VH crimp both "\n'
    '                  "ends, ASSEMBLY.md section 4); %.2f A typical (their 0.12 A allocations); %.4f A peak, from its basis: rv-pwr\'s HIGH, "\n'
    '                  "7.0380 W at the LDOs\' inputs (each H743 at 400 mA, DS12110 Rev 10 Table 30\'s maximum at TJ 85 C, plus 60 mA of its "\n'
    '                  "other parts: 1.3800 A of LDO current), at constant power at the least load voltage 4.7719 V, rounded up")\n'
    % (DEV_LEAD_PEAK, IOC_TYP, IOC_PEAK, IOC_TYP, IOC_PEAK))
_OLD_GNDL = 'for _n in (1, 2, 3): _GND_LOADS.update(_SLOT_LOADS(_n))\n'
_NEW_GNDL = _OLD_GNDL + "_GND_LOADS.update(_IOC_LOADS)   # record l9t5 (I-03): the three LDOs' ground ends; the return is shared, not lead by lead (l8r2 round 7)\n"
_OLD_GNDS = '["J_5V_S1", "J_5V_S2", "J_5V_S3", "J_5V_DEV"], loads=_GND_LOADS'
_NEW_GNDS = '["J_5V_S1", "J_5V_S2", "J_5V_S3", "J_5V_DEV", "J_5V_IOC"], loads=_GND_LOADS'
_OLD_FED = 'fed_from="+5V_DEV",   # U40/U50/U60 pins 1 and 3 are both /+5V_DEV in the netlist'
_NEW_FED = 'fed_from="+5V_IOC",   # U40/U50/U60 pin 1 and their EN pull-ups are on /+5V_IOC (record l9t5, I-03)'
_OLD_WHY = 'so it follows the device rail and the controller is up whenever the kit is'
_NEW_WHY = 'so it follows +5V_IOC (board A\'s U601 on RAIL_EN, record l9t5) and the controller is up whenever the kit is'
_OLD_VIN = '{"1": "+5V_DEV", "2": "GND", "3": "IOC%s_LDO_EN" % _tag, "4": "NC", "5": v33})'
_NEW_VIN = '{"1": "+5V_IOC", "2": "GND", "3": "IOC%s_LDO_EN" % _tag, "4": "NC", "5": v33})   # record l9t5 (I-03): was +5V_DEV'
_OLD_EN = 'r(R_(3), "100k", "+5V_DEV", "IOC%s_LDO_EN" % _tag)'
_NEW_EN = 'r(R_(3), "100k", "+5V_IOC", "IOC%s_LDO_EN" % _tag)'
_OLD_CIN = 'c(C_(0), "1u", "+5V_DEV", "GND");'
_NEW_CIN = 'c(C_(0), "1u", "+5V_IOC", "GND");'
_OLD_TVS = 'kisch.tvs("D1", "SMBJ5.0A", "+5V_DEV", "GND", "TVS");'
_NEW_TVS = ('part("J_5V_IOC", "Connector_Generic", "Conn_01x02", "JST-VH socket, 10 A: the supervisors\' 5 V from A22 J_5V_IOC (record l9t5, I-03): + -", '
            '"VH2", {"1": "+5V_IOC", "2": "GND"}, "C274411")\n'
            'kisch.tvs("D900", "SMBJ5.0A", "+5V_IOC", "GND", "TVS"); c("C900", "10u", "+5V_IOC", "GND", "C10u")   # record l9t5 (I-03): as D1 and C4 on +5V_DEV\n'
            + _OLD_TVS)
_OLD_SEC = '["J_5V_DEV", "D1", "C1", "C2", '
_NEW_SEC = '["J_5V_DEV", "D1", "C1", "C2", "J_5V_IOC", "D900", "C900", '
# round 2 (4 October 2026 evening): the LDO's input capacitor is also declared by an explicit bypass entry naming its net; the round 1
# text missed it, and the generator with this draft alone refused ("intent: bypass C400 -> U40.1: the capacitor is not on that pin's
# net +5V_DEV"): record l9t5's l9t5_drafts.py section 4 keeps that refusal as the mutation that must fail
_OLD_BYP = '_intent.bypass(C_(0), U_(0), "1", "+5V_DEV")'
_NEW_BYP = '_intent.bypass(C_(0), U_(0), "1", "+5V_IOC")'
EDITS = [(_OLD_LOADS, _NEW_LOADS), (_OLD_DEV, _NEW_DEV), (_OLD_DEVNOTE, _NEW_DEVNOTE), (_OLD_GNDL, _NEW_GNDL), (_OLD_GNDS, _NEW_GNDS),
         (_OLD_FED, _NEW_FED), (_OLD_WHY, _NEW_WHY), (_OLD_VIN, _NEW_VIN), (_OLD_EN, _NEW_EN), (_OLD_CIN, _NEW_CIN), (_OLD_TVS, _NEW_TVS),
         (_OLD_SEC, _NEW_SEC), (_OLD_BYP, _NEW_BYP)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    for ref in ADDS:
        if re.search(r'"%s"' % re.escape(ref), text):
            refuse("designator %s is already in use in the target" % ref)
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), text):
            refuse("net %s already exists in the target" % net)
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


# NOT RELEASED: as apply_gen_sch_a_iocbuck.py, one RELEASE.md beside both.
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_b.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; record l9t5's drafts wait on an accepted check")
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_b.py", "b/gen_sch_b.py", n=0))
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
