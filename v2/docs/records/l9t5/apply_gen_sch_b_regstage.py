#!/usr/bin/env python3
"""apply_gen_sch_b_regstage.py: DRAFT for board B's generator owner (Layer 4 task L4A-56, re-scoped by W135's CHANGE-METHOD; the
ledger's RE-6 and RE-7; record l4reg, MESHSAT-1357, 7 October 2026). NOT APPLIED to the tree by this record, like every draft of
L4-E9's change list (None is APPLIED); its author ran it only on scratch copies. It is a successor of record l9t5's
apply_gen_sch_b_iocguard.py: it applies straight after it (it edits that draft's lines) and refuses a target without it. It composes
with apply_gen_sch_b_canmb.py (W137, L4A-54) in either order: the two edit disjoint lines, share no designator added by either, and
share no net or controller pin (record l4reg, l4reg_compare.out section 9).

Why (record l4reg, v2/docs/records/l4reg/L4REG.md; W135's screen, record l4lim at fnd/l4lim aa6704b2, copied to
v2/docs/records/l4reg/inputs/): round 6's rail trip bounded each supervisor's AVERAGE current through an RC filter whose response the
check cx46 found unproven (RE-6) and whose average does not bound the LDO's periodic peak (RE-7). A current limiter ahead of the
AP2112K has no window on printed limits: its 125 C current at the 14.0k corner (0.3056 A on its 184 C/W) sits under row 7's served
peak (0.4240 A). The selected stage (SESSION W138-1, record l4reg section 7):
  1. THE LIMITER, one per controller (U45, U55, U65 take the INA169s' places): TI TPS2553-1 in SOT-23-6 (SLVS841F, latch-off,
     active-high EN), RILIM 49.9 kOhm 1 % (R601, R621, R641): IOS 0.475 to 0.565 A over -40 to 125 C TJ (7.5, the tested row), 0.4702
     to 0.5878 A with the resistor's 1 % (MODEL: the envelope of the row and Equation 1 at its bounds, W159); latched off after its overcurrent deglitch, 5 to 10 ms,
     until EN or power is cycled (9.3.1, 9.3.3). IN on +5V_IOC with its 100 nF (C940, C950, C960, kept); OUT on IOC{t}_LDO_IN; EN on
     IOC{t}_LIM_EN, pulled up to +5V_IOC by 100 kOhm (R602, R622, R642): the node the peers' restart and the in-service test of
     L4A-54 and L4A-58 would drive; FAULT open (L4A-58 reads it).
  2. THE REGULATOR, the LDO replaced (U40, U50, U60): TI TPS73733DCQRM3 (SBVS067W; the M3 suffix ships the new silicon only, Table
     8-1, CSO RFB), SOT-223-6: 1 IN, 2 OUT, 3 GND, 4 NR (open: the noise capacitor is optional, 6.3.1), 5 EN, 6 GND (the tab).
     Printed: R(theta)JA 76.0 C/W (new silicon, DCQ, 5.4), dropout at most 250 mV at 1 A (5.6), output within 1.5 % over line, load
     and temperature (5.6), current limit 1.05 to 2.2 A (5.6), input 2.2 to 5.5 V (5.3), output short-circuit duration indefinite
     (5.1). At the limiter's maximum 0.5878 A and the 14.0k corner's drop 0.8669 V its junction is 115.0 C at 76.25 C air (MODEL on
     the PRINTED 76.0 C/W), under 125 C for every waveform under the limit.
  3. ITS EN pulled up by R66, R78, R90 (100 kOhm) from IOC{t}_LDO_IN, its own input (was +5V_IOC): the TPS737 prints EN high from
     1.7 V to VIN (5.6); the bench jumper J_IOCOFF_x still holds it off (IOHA A4 and A6 unchanged).
  4. ROUND 6'S RAIL TRIP REMOVED (SESSION W138-2): the 0.3 ohm sense R600, R620, R640, the TPS3701 comparators U46, U56, U66, the
     filter capacitors C941, C951, C961 and the comparators' capacitors C942, C952, C962 go; the INA169s' places take the limiters.
     The share limiters (round 6's other half) are untouched; W137's canmb replaces them separately.
Designators added: none (every part above takes a place round 6 drew). Removed: R600, R620, R640, U46, U56, U66, C941, C951, C961,
C942, C952, C962. The two TI parts' order codes at LCSC are owed (Layer 6, finding L4REG-F4). The SOT-223-6 land id is this
draft's ASSUMPTION, read only where KiCad is (kisch's own land check runs there; finding L4REG-F5).
Usage:  apply_gen_sch_b_regstage.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (already applied, record l9t5's iocguard absent, an old text missing, or the repository's
own generator named before RELEASE-T10.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_regstage"
BOARD = "b"
ADDS = ()
REMOVES = tuple("R%d" % (600 + 20 * k) for k in range(3)) + tuple("U%d" % (46 + 10 * k) for k in range(3)) \
    + tuple("C%d" % (940 + 10 * k + n) for k in range(3) for n in (1, 2))
LIMITER = dict(part="TPS2553-1", package="SOT236", rilim="49.9k 1%", ren="100k", sheet="TI SLVS841F")
REGULATOR = dict(part="TPS73733DCQRM3", land="Package_TO_SOT_SMD:SOT-223-6", sheet="TI SBVS067W")

_OLD_0 = ('    ic(U_(0), 5, "AP2112K-3.3 LDO: the private 3.3 V of controller %s, its own branch off the device rail" % _tag, "SOT235",\n'
          '       {"1": "IOC%s_LDO_IN" % _tag, "2": "GND", "3": "IOC%s_LDO_EN" % _tag, "4": "NC", "5": v33})   # record l9t5 (I-03; T10 round 6): behind its rail trip\'s sense resistor\n'
          '    r(R_(3), "100k", "+5V_IOC", "IOC%s_LDO_EN" % _tag)\n')
_NEW_0 = ('    # L4A-56 (record l4reg, W138, 7 October 2026; apply_gen_sch_b_regstage.py, NOT APPLIED): THE REGULATOR. The AP2112K above is\n'
          '    # replaced by a TPS73733DCQRM3 (TI SBVS067W; the M3 suffix ships the new silicon only, Table 8-1), whose printed 76.0 C/W\n'
          '    # (DCQ, new silicon, 5.4) holds 125 C at the limiter\'s maximum 0.5878 A from the 14.0k corner (115.0 C, MODEL; the AP2112K\n'
          '    # read 170.0 C there). Its EN (pin 5) is pulled up from its own input, IOC_LDO_IN: the sheet prints EN high from 1.7 V to VIN\n'
          '    # (5.6) and low under 0.5 V, so the bench jumper still holds it off. The W5 note above gives the AP2112K\'s figures, as history.\n'
          '    ic(U_(0), 6, "TPS73733DCQRM3 1 A LDO, new silicon only (TI SBVS067W): the private 3.3 V of controller %s, its own branch behind its current limiter" % _tag,\n'
          '       "Package_TO_SOT_SMD:SOT-223-6", {"1": "IOC%s_LDO_IN" % _tag, "2": v33, "3": "GND", "4": "NC", "5": "IOC%s_LDO_EN" % _tag, "6": "GND"})\n'
          '    r(R_(3), "100k", "IOC%s_LDO_IN" % _tag, "IOC%s_LDO_EN" % _tag)   # L4A-56 (record l4reg): EN from the LDO\'s own input (was +5V_IOC)\n')
_OLD_1 = (
    '    c(C_(0), "1u", "IOC%s_LDO_IN" % _tag, "GND"); c(C_(1), "10u", v33, "GND", "C10u")   # T10 round 6: the LDO\'s input capacitor behind the sense resistor\n'
    "    # T10 ROUND 6 (record l9t5, the check cx45's Q3): THE RAIL TRIP, an independent bound on the controller's supply current that no\n"
    "    # firmware sets. 0.3 ohm from +5V_IOC to the LDO's input; an INA169 (1 mA/V) into 5.76 kOhm gives 0.4 V at about 0.23 A; 100 kOhm\n"
    "    # and 10 uF average it over 1 s; a TPS3701's comparator B holds the LDO's EN low while the average is over its threshold (OUTB low\n"
    "    # over VIT+(INB)), so a controller whose firmware runs a clock or a load outside FW-B20 is powered off until its average falls\n"
    "    # (record l9t5 l9t5_t10.out 10j: the window 0.22 to 0.25 A, the held-current bound and the transient's qualification limit)\n"
    '    _GR = lambda n, _k=_k: "R%d" % (600 + 20 * _k + n)\n'
    '    _GC = lambda n, _k=_k: "C%d" % (940 + 10 * _k + n)\n'
    '    _GD = lambda n, _k=_k: "D%d" % (400 + 10 * _k + n)\n'
    '    r(_GR(0), "0.3R 1% 0805", "+5V_IOC", "IOC%s_LDO_IN" % _tag)   # the sense resistor\n'
    '    ic(U_(5), 5, "INA169NA/3K high-side current-shunt monitor (TI SBOS181F): controller %s\'s rail current, 1 mA/V" % _tag, "SOT235",\n'
    '       {"1": "IOC%s_ISNS" % _tag, "2": "GND", "3": "+5V_IOC", "4": "IOC%s_LDO_IN" % _tag, "5": "+5V_IOC"}, "C44322")\n'
    '    c(_GC(0), "100n", "+5V_IOC", "GND")   # INA169\'s V+ (TI SBOS181F 8.2: a 0.1-uF capacitor near the V+ pin)\n'
    '    r(_GR(1), "5.76k 1%", "IOC%s_ISNS" % _tag, "GND")   # its output resistor\n'
    '    r(_GR(2), "100k 1%", "IOC%s_ISNS" % _tag, "IOC%s_ISF" % _tag); c(_GC(1), "10u 16V X7R", "IOC%s_ISF" % _tag, "GND")   # the 1 s average\n'
    '    ic(U_(6), 6, "TPS3701DDCR window comparator (TI SBVS240C): controller %s\'s rail trip, OUTB holds its LDO\'s EN low over the threshold" % _tag, "SOT236",\n'
    '       {"1": "NC", "2": "GND", "3": "GND", "4": "IOC%s_ISF" % _tag, "5": "+5V_IOC", "6": "IOC%s_LDO_EN" % _tag}, "C132788")   # INA unused (OUTA open)\n'
    '    c(_GC(2), "100n", "+5V_IOC", "GND")   # the comparator\'s VDD (TI SBVS240C pin table: a 0.1-uF ceramic capacitor close to this pin)\n')
_NEW_1 = (
    '    c(C_(0), "1u", "IOC%s_LDO_IN" % _tag, "GND"); c(C_(1), "10u", v33, "GND", "C10u")   # the LDO\'s input capacitor, behind its limiter (L4A-56; was behind round 6\'s sense resistor)\n'
    "    # L4A-56 (record l4reg, W138, 7 October 2026; apply_gen_sch_b_regstage.py, NOT APPLIED): THE LIMITER, in place of round 6's rail\n"
    "    # trip (0.3 ohm sense, INA169, 1 s average, TPS3701 on the LDO's EN; its response and its sustained bound were withdrawn by the\n"
    "    # check cx46, the ledger's RE-6 and RE-7). A TI TPS2553-1 (SLVS841F, latch-off, active-high EN) with RILIM 49.9 kOhm 1 %: IOS\n"
    "    # 0.475 to 0.565 A over -40 to 125 C TJ (7.5), over every state the design serves (row 7's peak 0.4240 A) and, with the LDO\n"
    "    # below, under the current at which the LDO reaches 125 C; latched off after its 5 to 10 ms overcurrent deglitch until EN or\n"
    "    # power is cycled (9.3.1, 9.3.3). EN is pulled up to +5V_IOC through 100 kOhm: the node the peers' restart and the in-service\n"
    "    # test would drive (L4A-54, L4A-58); FAULT is left open (L4A-58 reads it). Record l4reg's l4reg_compare.out has every figure.\n"
    '    _GR = lambda n, _k=_k: "R%d" % (600 + 20 * _k + n)\n'
    '    _GC = lambda n, _k=_k: "C%d" % (940 + 10 * _k + n)\n'
    '    _GD = lambda n, _k=_k: "D%d" % (400 + 10 * _k + n)\n'
    '    ic(U_(5), 6, "TPS2553-1 current-limited switch, latch-off, SOT-23-6 (TI SLVS841F): controller %s\'s supply, IOS 0.475 to 0.565 A at RILIM 49.9k" % _tag, "SOT236",\n'
    '       {"1": "+5V_IOC", "2": "GND", "3": "IOC%s_LIM_EN" % _tag, "4": "NC", "5": "IOC%s_ILIM" % _tag, "6": "IOC%s_LDO_IN" % _tag})\n'
    '    c(_GC(0), "100n", "+5V_IOC", "GND")   # the limiter\'s IN (TI SLVS841F pin functions: a 0.1 uF or greater ceramic capacitor from IN to GND)\n'
    '    r(_GR(1), "49.9k 1%", "IOC%s_ILIM" % _tag, "GND")   # RILIM: the tested 49.9 kOhm row (SLVS841F 7.5)\n'
    '    r(_GR(2), "100k", "+5V_IOC", "IOC%s_LIM_EN" % _tag)   # the limiter\'s EN pulled up (SLVS841F 7.3: EN 0 to 6.5 V)\n')
_OLD_2 = ('    _intent.bypass(_GC(0), U_(5), "5", "+5V_IOC")\n'
          '    _intent.bypass(_GC(2), U_(6), "5", "+5V_IOC")\n')
_NEW_2 = '    _intent.bypass(_GC(0), U_(5), "1", "+5V_IOC")   # L4A-56 (record l4reg): the limiter\'s IN\n'
_OLD_3 = '    if pv.startswith("INA169"):   # T10 round 6 (record l9t5, cx45 Q3): the rail trip\'s current monitor\n'
_NEW_3 = ('    if pv.startswith("TPS2553"):   # L4A-56 (record l4reg): the supervisors\' current limiters\n'
          '        return ("D", "TI TPS2552/TPS2553 SLVS841F (v2/vendor/ti/held/ti-tps2553-slvs841f.pdf) pin functions, IN: \\"connect a 0.1 uF "\n'
          '                     "or greater ceramic capacitor from IN to GND as close to the IC as possible\\"")\n'
          '    if pv.startswith("TPS73733"):   # L4A-56 (record l4reg): the supervisors\' LDOs; its output capacitor is C_(1), 10 uF, over the 1 uF floor\n'
          '        return ("D", "TI TPS737 SBVS067W (v2/vendor/ti/held/ti-tps737-sbvs067w.pdf) 7.2, Figure 7-2: \\"Optional input capacitor. "\n'
          '                     "May improve source impedance, noise, or PSRR.\\": an LDO\'s input capacitor is class D (DECOUPLING.md section 6)")\n'
          + _OLD_3)
_OLD_4 = '_IOC_LOADS = {"R600": 0.12, "R620": 0.12, "R640": 0.12}   # the allocations +5V_DEV carried for them (S-98 M7); T10 round 6 (record l9t5): the LDOs U40, U50, U60 sit behind their rail trips\' sense resistors R600, R620, R640\n'
_NEW_4 = '_IOC_LOADS = {"U45": 0.12, "U55": 0.12, "U65": 0.12}   # the allocations +5V_DEV carried for them (S-98 M7); L4A-56 (record l4reg): the LDOs U40, U50, U60 sit behind their current limiters U45, U55, U65 (was round 6\'s sense resistors)\n'
_OLD_5 = '                 source_ic="%s is an AP2112K-3.3 LDO in SOT-23-5: pin 5 IS its output power pin" % _u,\n'
_NEW_5 = '                 source_ic="%s is a TPS73733DCQRM3 LDO in SOT-223-6: pin 2 IS its output power pin (L4A-56, record l4reg)" % _u,\n'
EDITS = [(_OLD_0, _NEW_0), (_OLD_1, _NEW_1), (_OLD_2, _NEW_2), (_OLD_3, _NEW_3), (_OLD_4, _NEW_4), (_OLD_5, _NEW_5)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if "_LIM_EN" in text or "TPS73733" in text:
        refuse("the change is already applied")
    if _OLD_1 not in text or "_LDO_IN" not in text:
        refuse("record l9t5's iocguard draft (with iocbuck, iocpre, canshdn and iocset before it) is not in the target: apply it first")
    if not re.search(r"U_ = lambda n, _k=_k: \"U%d\" % \(40 \+ 10 \* _k \+ n\)", text):
        refuse("the controllers' IC numbering (U_(n) = U40 + 10k + n) is not the one this draft was written against")
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
    for ref in REMOVES:   # the removed places are gone: no literal and no lambda call draws them any more
        if re.search(r'"%s"' % ref, new):
            refuse("%s is still drawn as a literal designator" % ref)
    return new


# NOT RELEASED: this draft is written for the generator's owner and never applied by its author. Writing the repository's own generator
# is refused until RELEASE-T10.md beside this script reads "released: yes" on its first line and names an accepted check of task T10
# ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
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
