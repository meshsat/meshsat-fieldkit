#!/usr/bin/env python3
"""apply_gen_sch_a_iocbuck.py: DRAFT for board A's generator owner (Layer 9 record l9t5, task T5, I-03 on the case row C-DEV rev 1,
MESHSAT-1357, 4 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies (the tests write
scratch copies).

The defect (I-03, the case row C-DEV rev 1; record l9t5 out 5): the device rail's LM5176 stage U7 at the least load voltage 4.9019 V,
every load at constant power, reads 7.4717 A against its average loop's least 7.0957 A (43 mV over R43's 6 mOhm at +1 percent, TI
SNVSAI1D p.7), and no 1 percent R43 both supplies the case (at most 5.6981 mOhm) and keeps the loop's highest under J_5V_DEV's JST-VH
10 A (at least 5.7576 mOhm). The correction selected (record l9t5 out 5, option (b), SESSION): the three supervisors' private LDOs on
board B (U40, U50, U60, AP2112K-3.3) leave the device rail for their own always-on 5 V buck on this board, on its own JST-VH lead:
  U601      TPS62933DRLR (TI SLUSEA4D: 3.8 to 30 V in, 3 A; IHS_LIMIT 4.2 / 5.0 / 5.8 A), the part U12, U33 and U41 are, EN on RAIL_EN
            (U12's and U41's enable: up whenever the board's converters are, held by L4-E11's U46 through the pack breaker's start,
            dropped by the hot stop's KILL), 500 kHz with RT open, SS 10 nF
  L601      6.8 uH XAL6060-682ME (U41's, Isat 9.2 A over the part's 5.8 A highest high-side limit)
  C601, C602  BST 100 nF, SS 10 nF; C603, C604 VIN 10 uF and 100 nF (U41's bypass class); C605, C606 two 22 uF 10 V 1210 out
  R601, R602  56.2k over 10.7k, 0.1 percent 25 ppm/C: stream s99a's divider of U41, 5.002 V nominal, 4.872 to 5.133 V
  J_5V_IOC  JST-VH 1x2 (the slot and device leads' part), the supervisors' 5 V to board B: + -
What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else:
  1. the block above, after the D8 mezzanine's eFuse and lead (U41's network, which it copies);
  2. +5V_IOC declared (0.36 A typical, the controllers' 0.12 A allocations on board B; 1.4749 A peak, from its basis since round 3:
     rv-pwr's HIGH for the three supervisors, 7.0380 W at the LDOs' inputs (each H743 at 400 mA, DS12110 Rev 10 Table 30 p.111's
     maximum at TJ 85 C at 400 MHz with all peripherals enabled, plus the declared 60 mA of its other parts: 1.3800 A of LDO current),
     taken by the case's own method, every load at constant power at the rail's least load voltage 4.7719 V (U601's window 4.8719 V
     less the rail's 2 percent), rounded up to 0.1 mA; this board's share of the rail's 2 percent is 0.5, as +5V_DEV's), its switching
     and bootstrap nodes; the lead is the device lead's make, 16 AWG, 150 mm, VH crimp both ends (v2/docs/ASSEMBLY.md section 4);
  3. VBAT's loads: Q32 (U7's entry) 1.61 to 1.47 A and U601 added at 0.14 A, the S-98 method (the typical over 0.90 and 14.4 V):
     3.74 A x 5.088 V / 12.96 V = 1.4683 A; 0.36 A x 5.002 V / 12.96 V = 0.1389 A;
  4. +5V_DEV's typical 4.1 to 3.74 A and J_5V_DEV's load 3.8 to 3.44 A (the controllers' 0.36 A allocation leaves); its peak from
     its basis since round 3 (record l8r2's finding L8R2-F35): stream s99's construction, board B's lead plus the wall port's 0.9142 A,
     with the lead at 6.0359 A (Layer 9's budget at HIGH, every load at constant power at the least load voltage 4.9019 V, the
     supervisors on +5V_IOC: record l9t5's l9t5_drafts.out) where it was a typed 6.0 A: 6.9501 A, 0.106797 A under the conditional
     7.056897 A the note names (rounds 1 and 2 kept 6.9142 A and called it an overstatement, which was true of the case and not of
     the construction); the note's sentence on the peak restated;
  5. a section for the new parts.
Order: board A's round, after L4-E9's 3g (record l8r2's slotlm and fb01, record l8p's PTC, L4-E11's dd7) and before d8dec31's mainpb
(the last taker, R-193): none of those touch its anchors, so it composes in any position of 3a to 3g as well; with its board B half
apply_gen_sch_b_iocbuck.py in one release (alone, the lead ends at nothing on board B and the supervisors stay on +5V_DEV).
Usage:  apply_gen_sch_a_iocbuck.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator or net is in
use, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_iocbuck"
ADDS = ("U601", "L601", "C601", "C602", "C603", "C604", "C605", "C606", "R601", "R602", "J_5V_IOC")
NETS = ("+5V_IOC", "IOCB_SW", "IOCB_BST", "IOCB_SS", "IOCB_FB")
IOC_TYP, IOC_PEAK = 0.36, 1.4749        # A: board B's three 0.12 A allocations; 7.0380 W (rv-pwr's HIGH) at 4.7719 V, rounded up (round 3)
DEV_LEAD_PEAK, WALL_LIMIT = 6.0359, 0.9142   # A: board B's device lead on C-DEV rev 1 with this draft (rounded up to 0.1 mA); U32's nominal limit
DEV_PEAK = 6.9501                       # A: stream s99's construction, the lead plus the wall port; l9t5_drafts.py holds each to its basis
Q32_NEW, U601_VBAT = 1.47, 0.14        # A at VBAT, the S-98 method (typical x V over 0.90 x 14.4 V), rounded as Q32 and U41 are

_BASIS = ("TI SLUSEA4D (TPS62933) 12.1 p.40: 'the most critical PCB feature is the loop formed by the input capacitors and power "
          "ground'; 'Place a 0.1-uF ceramic decoupling capacitor or capacitors as close as possible to VIN and GND pins'")
_OLD_AT = 'vh2("J_MEZZ_PWR1", "D8 mezzanine 5 V (JST-VH): + -", "+5V_D8")\n'
_HEAD = ("# I-03, RECORD l9t5 (task T5, MESHSAT-1357, 4 October 2026; v2/docs/records/l9t5/ out 5): THE THREE SUPERVISORS' 5 V LEAVES THE\n"
         "# DEVICE RAIL. On the case row C-DEV rev 1 U7 reads 7.4717 A at the least load voltage against its average loop's least 7.0957 A, and\n"
         "# no 1 percent R43 both supplies the case and keeps the loop's highest under J_5V_DEV's JST-VH 10 A. Board B's three supervisor LDOs\n"
         "# (U40, U50, U60) draw 1.4358 A of it at HIGH by the case's method: they take their own TPS62933, a copy of U41's network, EN on\n"
         "# RAIL_EN, on their own JST-VH lead, and U7's case becomes 6.0359 A. The buck's 3 A rating and its high-side limit 4.2 / 5.0 / 5.8 A\n"
         "# (SLUSEA4D 8.5) keep the lead under its 10 A. DRAFTED, not applied (apply_gen_sch_b_iocbuck.py is board B's half).\n"
         "# ROUND 3 (record l8r2's finding L8R2-F35): the lead is the device lead's make (16 AWG, 150 mm, VH crimp both ends, ASSEMBLY.md\n"
         "# section 4); +5V_IOC's and +5V_DEV's peaks are declared from their basis (Layer 9's budget at HIGH, every load at constant power\n"
         "# at the rail's least load voltage), not typed: 1.4749 A, and board B's lead 6.0359 A plus the wall port's 0.9142 A = 6.9501 A.\n"
         "# S-99's dated comment lines above keep their figures of 28 September (6.9142 A, B 6.0 + wall 0.9142).\n")
_PARTS = ('ic("U601", 8, "TPS62933DRLR 3 A buck, 5.0 V for the three supervisors\' LDOs on board B (I-03)", "SOT583", {"1": "NC", "2": "RAIL_EN", '
          '"3": "VBAT", "4": "GND", "5": "IOCB_SW", "6": "IOCB_BST", "7": "IOCB_SS", "8": "IOCB_FB"}, "C3200405")\n'
          'part("L601", "Device", "L", "6.8uH XAL6060-682ME (Isat 9.2 A)", "L6060", {"1": "IOCB_SW", "2": "+5V_IOC"})\n'
          'c("C601", "100n", "IOCB_BST", "IOCB_SW"); c("C602", "10n", "IOCB_SS", "GND")\n'
          'c("C603", "10u 25V 1210", "VBAT", "GND", "C1210", bypass=("U601", "3")); c("C604", "100n", "VBAT", "GND", bypass=("U601", "3"))\n')
_CLS = 'for _ci in ("C603", "C604"): _cls(_ci, "R", "' + _BASIS.replace('"', '\\"') + '")\n'
_OUT = ('c("C605", "22u 10V X7R 1210", "+5V_IOC", "GND", "C1210"); c("C606", "22u 10V X7R 1210", "+5V_IOC", "GND", "C1210")\n'
        'r("R601", "56.2k 0.1% 25ppm", "+5V_IOC", "IOCB_FB", lcsc="C705784"); r("R602", "10.7k 0.1% 25ppm", "IOCB_FB", "GND", lcsc="C861078")\n'
        'vh2("J_5V_IOC", "the three supervisors\' 5 V to B16 (JST-VH): + -", "+5V_IOC")\n')
_RAIL = ('_intent.rail("+5V_IOC", 5.0, %.2f, %.4f, "L601", loads={"J_5V_IOC": %.2f}, switch="U601", efficiency=0.90, fed_from="VBAT", budget=0.02, share=0.005, v_work=5.14,\n'
         '             note="record l9t5 (I-03, C-DEV rev 1): the three supervisors\' LDOs on board B (U40, U50, U60) from VBAT through U601, a "\n'
         '                  "TPS62933 as U41 (5.002 V nominal, 4.872 to 5.133 V by stream s99a\'s divider, so v_work 5.14 V), between the inductor "\n'
         '                  "L601 and the lead J_5V_IOC (16 AWG, 150 mm, VH crimp both ends, the device lead\'s make, ASSEMBLY.md section 4); "\n'
         '                  "%.2f A typical (board B\'s three 0.12 A allocations); %.4f A peak, from its basis: rv-pwr\'s HIGH, 7.0380 W at the LDOs\' "\n'
         '                  "inputs (each H743 at 400 mA, DS12110 Rev 10 Table 30\'s maximum at TJ 85 C, plus 60 mA of its other parts: 1.3800 A of "\n'
         '                  "LDO current), at constant power at the least load voltage 4.7719 V, rounded up; this board\'s share of the 2 percent "\n'
         '                  "is 0.5 as +5V_DEV\'s; the buck limits at 4.2 to 5.8 A peak (SLUSEA4D 8.5), under the lead\'s 10 A")\n') % (IOC_TYP, IOC_PEAK, IOC_TYP, IOC_TYP, IOC_PEAK)
_NODES = ('_intent.node("IOCB_SW", 16.8, "the supervisors\' buck U601\'s switching node: it swings to VBAT, the pack node that feeds it, and a diode drop below ground", v_min=-1.0)\n'
          '_intent.node("IOCB_BST", _intent.net_volts("IOCB_SW") + _TPS62933_BST,\n'
          '             "the supervisors\' buck U601\'s bootstrap supply (pin 6 BST): it rides on IOCB_SW at up to 5.5 V, SLUSEA4D 8.3\'s "\n'
          '             "recommended BST-SW maximum, and supplies only the part\'s own high-side driver",\n'
          '             rides_on="IOCB_SW", bias_v=_TPS62933_BST)\n')
_NEW_AT = _OLD_AT + _HEAD + _PARTS + _CLS + _OUT + _RAIL + _NODES
_OLD_VBAT = '"Q32": 1.61, "U41": 0.4,'
_NEW_VBAT = '"Q32": %.2f, "U41": 0.4, "U601": %.2f,' % (Q32_NEW, U601_VBAT)
_OLD_DEV = '_intent.rail("+5V_DEV", 5.0, 4.1, 6.9142, "R43", loads={"J_5V_DEV": 3.8, "U32": 0.3},'
_NEW_DEV = ('_intent.rail("+5V_DEV", 5.0, 3.74, %.4f, "R43", loads={"J_5V_DEV": 3.44, "U32": 0.3},   # record l9t5 (I-03): the supervisors\' 0.36 A on +5V_IOC; '
            'the peak is board B\'s lead %.4f A plus the wall port\'s %.4f A (round 3)\n             ' % (DEV_PEAK, DEV_LEAD_PEAK, WALL_LIMIT))
# round 3: the note's sentence on the declared peak, restated on the same construction (stream s99's) with the lead's corrected figure
_OLD_PEAKNOTE = ("The 6.9142 A declared peak (B 6.0 + the wall port's 0.9142 A, U32's nominal limit by TPS2596 equation 7, SLVSET8A p.28) "
                 "has 0.142697 A conditional margin")
_NEW_PEAKNOTE = ("The %.4f A declared peak (board B's lead %.4f A, Layer 9's budget at HIGH with every load at constant power at the least "
                 "load voltage 4.9019 V and the supervisors on +5V_IOC, record l9t5 round 3; + the wall port's %.4f A, U32's nominal limit by "
                 "TPS2596 equation 7, SLVSET8A p.28) has %.6f A conditional margin" % (DEV_PEAK, DEV_LEAD_PEAK, WALL_LIMIT, 7.056897 - DEV_PEAK))
_OLD_SEC = '            ("EMCON GATES 74AUP1G08'
_NEW_SEC = ('            ("SUPERVISORS\' 5 V: TPS62933 BUCK U601 ON RAIL_EN, LEAD J_5V_IOC TO B16 (RECORD l9t5, I-03)", ["U601", "L601", "C601", "C602", '
            '"C603", "C604", "C605", "C606", "R601", "R602", "J_5V_IOC"]),\n' + _OLD_SEC)
EDITS = [(_OLD_AT, _NEW_AT), (_OLD_VBAT, _NEW_VBAT), (_OLD_DEV, _NEW_DEV), (_OLD_SEC, _NEW_SEC), (_OLD_PEAKNOTE, _NEW_PEAKNOTE)]
if abs(DEV_PEAK - (DEV_LEAD_PEAK + WALL_LIMIT)) > 1e-9:
    raise SystemExit("apply_gen_sch_a_iocbuck: the device rail's peak is not its lead plus the wall port")


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
    for need_ in ("_TPS62933_BST", "def _cls(", "def vh2("):
        if need_ not in text:
            refuse("the target has no %s" % need_)
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


# NOT RELEASED: record l9t5 drafts this change for board A's generator owner and never applies it. Writing the repository's own
# gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check of
# this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
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
