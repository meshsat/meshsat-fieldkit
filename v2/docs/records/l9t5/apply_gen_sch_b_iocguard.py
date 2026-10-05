#!/usr/bin/env python3
"""apply_gen_sch_b_iocguard.py: DRAFT for board B's generator owner (Layer 9 record l9t5, task T10 round 6, the check cx45's Q3,
MESHSAT-1357, 5 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies. It applies after
record l9t5's apply_gen_sch_b_iocbuck.py, apply_gen_sch_b_iocpre.py and apply_gen_sch_b_canshdn.py (it edits their lines) and refuses a
target without them.

Why (cx45 Q3 (a) to (c); l9t5_t10.out 10j): a supervisor whose firmware breaks FW-B21 (its transmit share) can deny both fabrics, and
one that breaks FW-B20 (its clock and load) can draw a current that takes its LDO over 125 C or 150 C; the only bounds were the
FAULTING firmware's own verification and its BOR. This draft adds two bounds that no firmware sets:
  1. A TRANSMIT-SHARE LIMITER per transceiver (six): TXD averaged over 130 ms by 1 MOhm and 150 kOhm (0.1 %) and 1 uF; a TPS3701
     (comparator B) whose open-drain OUTB holds LIMO low while the average shows a dominant share under 4.7 to 12.4 % and releases it;
     LIMO's 10 kOhm pull-up then lifts the transceiver's SHDN through a 1N4148W. The controller's own SHDN request (canshdn's GPIO)
     reaches SHDN through a second 1N4148W; SD is held low by 100 kOhm. A held-dominant TXD is silenced within 16 ms (the driver's own
     time-out frees the bus within 3.8 ms first), a babbler through its FDCAN within 0.23 s; the release is automatic.
  2. A RAIL TRIP per controller (three): 0.3 ohm from +5V_IOC to the LDO's input, an INA169 into 5.76 kOhm, a 1 s average (100 kOhm,
     10 uF) into a TPS3701 (comparator B) whose OUTB holds the LDO's EN low while the average current is over 0.22 to 0.25 A; the LDO's
     input capacitor C_(0) moves behind the sense resistor.
Designators: R600 to R650 (R(600 + 20k + n)), C940 to C966 (C(940 + 10k + n)), D400 to D413 (D(400 + 10k + n)), U45 to U48, U55 to U58,
U65 to U68 (U_(5) to U_(8) of each controller's block). The INA169NA/3K (LCSC C44322) and the TPS3701DDCR (LCSC C132788) are
the kit's parts already (v2/vendor/SOURCES.yaml, L4-E7's backstop); their sheets are held back (v2/docs/records/l4e7/fetch_held_back.py).
Usage:  apply_gen_sch_b_iocguard.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (already applied, an old text missing, a designator in use, or the repository's own generator
named before RELEASE-T10.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_iocguard"
BOARD = "b"
ADDS = tuple("R%d" % (600 + 20 * k + n) for k in range(3) for n in range(11)) + tuple("C%d" % (940 + 10 * k + n) for k in range(3) for n in range(7)) \
    + tuple("D%d" % (400 + 10 * k + n) for k in range(3) for n in range(4)) + tuple("U%d" % (40 + 10 * k + n) for k in range(3) for n in range(5, 9))
RAIL_TRIP = dict(rs="0.3R 1% 0805", rl="5.76k 1%", rf="100k 1%", cf="10u 16V X7R", amp="INA169NA/3K", cmp="TPS3701DDCR")
LIMITER = dict(r1="1M 0.1%", r2="150k 0.1%", c="1u 16V X7R", rpu="10k 1%", rsd="100k", cmp="TPS3701DDCR", diode="1N4148W")
_OLD_0 = '       {"1": "+5V_IOC", "2": "GND", "3": "IOC%s_LDO_EN" % _tag, "4": "NC", "5": v33})   # record l9t5 (I-03): was +5V_DEV\n'
_NEW_0 = '       {"1": "IOC%s_LDO_IN" % _tag, "2": "GND", "3": "IOC%s_LDO_EN" % _tag, "4": "NC", "5": v33})   # record l9t5 (I-03; T10 round 6): behind its rail trip\'s sense resistor\n'
_OLD_1 = '    c(C_(0), "1u", "+5V_IOC", "GND"); c(C_(1), "10u", v33, "GND", "C10u")\n'
_NEW_1 = '    c(C_(0), "1u", "IOC%s_LDO_IN" % _tag, "GND"); c(C_(1), "10u", v33, "GND", "C10u")   # T10 round 6: the LDO\'s input capacitor behind the sense resistor\n    # T10 ROUND 6 (record l9t5, the check cx45\'s Q3): THE RAIL TRIP, an independent bound on the controller\'s supply current that no\n    # firmware sets. 0.3 ohm from +5V_IOC to the LDO\'s input; an INA169 (1 mA/V) into 5.76 kOhm gives 0.4 V at about 0.23 A; 100 kOhm\n    # and 10 uF average it over 1 s; a TPS3701\'s comparator B holds the LDO\'s EN low while the average is over its threshold (OUTB low\n    # over VIT+(INB)), so a controller whose firmware runs a clock or a load outside FW-B20 is powered off until its average falls\n    # (record l9t5 l9t5_t10.out 10j: the window 0.22 to 0.25 A, the held-current bound and the transient\'s qualification limit)\n    _GR = lambda n, _k=_k: "R%d" % (600 + 20 * _k + n)\n    _GC = lambda n, _k=_k: "C%d" % (940 + 10 * _k + n)\n    _GD = lambda n, _k=_k: "D%d" % (400 + 10 * _k + n)\n    r(_GR(0), "0.3R 1% 0805", "+5V_IOC", "IOC%s_LDO_IN" % _tag)   # the sense resistor\n    ic(U_(5), 5, "INA169NA/3K high-side current-shunt monitor (TI SBOS181F): controller %s\'s rail current, 1 mA/V" % _tag, "SOT235",\n       {"1": "IOC%s_ISNS" % _tag, "2": "GND", "3": "+5V_IOC", "4": "IOC%s_LDO_IN" % _tag, "5": "+5V_IOC"}, "C44322")\n    c(_GC(0), "100n", "+5V_IOC", "GND")   # INA169\'s V+ (TI SBOS181F 8.2: a 0.1-uF capacitor near the V+ pin)\n    r(_GR(1), "5.76k 1%", "IOC%s_ISNS" % _tag, "GND")   # its output resistor\n    r(_GR(2), "100k 1%", "IOC%s_ISNS" % _tag, "IOC%s_ISF" % _tag); c(_GC(1), "10u 16V X7R", "IOC%s_ISF" % _tag, "GND")   # the 1 s average\n    ic(U_(6), 6, "TPS3701DDCR window comparator (TI SBVS240C): controller %s\'s rail trip, OUTB holds its LDO\'s EN low over the threshold" % _tag, "SOT236",\n       {"1": "NC", "2": "GND", "3": "GND", "4": "IOC%s_ISF" % _tag, "5": "+5V_IOC", "6": "IOC%s_LDO_EN" % _tag}, "C132788")   # INA unused (OUTA open)\n    c(_GC(2), "100n", "+5V_IOC", "GND")   # the comparator\'s VDD (TI SBVS240C pin table: a 0.1-uF ceramic capacitor close to this pin)\n'
_OLD_2 = '           {"1": _tx, "2": "GND", "3": v33, "4": _rx, "5": "IOC%s_CAN%d_SHDN" % (_tag, _un - 2), "6": "CANL_%s%s" % (_f, _seg), "7": "CANH_%s%s" % (_f, _seg), "8": "GND"}, "C2871143")\n'
_NEW_2 = '           {"1": _tx, "2": "GND", "3": v33, "4": _rx, "5": "IOC%s_CAN%d_SD" % (_tag, _un - 2), "6": "CANL_%s%s" % (_f, _seg), "7": "CANH_%s%s" % (_f, _seg), "8": "GND"}, "C2871143")\n'
_OLD_3 = '        r(R_(_un + 1), "100k", "IOC%s_CAN%d_SHDN" % (_tag, _un - 2), "GND")\n'
_NEW_3 = '        r(R_(_un + 1), "100k", "IOC%s_CAN%d_SHDN" % (_tag, _un - 2), "GND")\n        # T10 ROUND 6 (record l9t5, cx45 Q3): THE TRANSMIT-SHARE LIMITER, independent of any firmware. TXD averaged over 130 ms (1 MOhm\n        # and 150 kOhm at 0.1 %, 1 uF): with TXD high when recessive the average is 0.130 of the rail times (1 - the dominant share); a TPS3701\'s\n        # comparator B holds LIMO low while the average is over its threshold (OUTB low) and releases it when the share passes 4.7 to\n        # 12.4 %; LIMO\'s pull-up then lifts SHDN through a diode. The controller\'s own SHDN request reaches SHDN through the other diode\n        # (the 100 kOhm on SD holds it low otherwise: TI\'s pin sources up to 4 uA, SLLSEQ7F IIL)\n        _j = _un - 3\n        _sd, _lim, _lo = "IOC%s_CAN%d_SD" % (_tag, _un - 2), "IOC%s_CAN%d_LIM" % (_tag, _un - 2), "IOC%s_CAN%d_LIMO" % (_tag, _un - 2)\n        part(_GD(2 * _j), "Device", "D", "1N4148W: controller %s\'s own SHDN request onto its fabric %s transceiver (cathode on SD)" % (_tag, _f), "SOD123", {"1": _sd, "2": "IOC%s_CAN%d_SHDN" % (_tag, _un - 2)}, "C81598")\n        part(_GD(2 * _j + 1), "Device", "D", "1N4148W: the transmit-share limiter onto the same SHDN (cathode on SD)", "SOD123", {"1": _sd, "2": _lo}, "C81598")\n        r(_GR(3 + 4 * _j), "100k", _sd, "GND")\n        r(_GR(4 + 4 * _j), "1M 0.1%", _tx, _lim); r(_GR(5 + 4 * _j), "150k 0.1%", _lim, "GND"); c(_GC(3 + 2 * _j), "1u 16V X7R", _lim, "GND")\n        ic(U_(7 + _j), 6, "TPS3701DDCR window comparator (TI SBVS240C): controller %s\'s fabric %s transmit-share limiter, OUTB released (SHDN high) over the share" % (_tag, _f), "SOT236",\n           {"1": "NC", "2": "GND", "3": "GND", "4": _lim, "5": "+5V_IOC", "6": _lo}, "C132788")   # INA unused (OUTA open)\n        r(_GR(6 + 4 * _j), "10k 1%", v33, _lo)   # LIMO\'s pull-up from the controller\'s own rail\n        c(_GC(4 + 2 * _j), "100n", "+5V_IOC", "GND")   # the comparator\'s VDD\n        _intent.bypass(_GC(4 + 2 * _j), U_(7 + _j), "5", "+5V_IOC")\n'
_OLD_4 = '    _intent.bypass(C_(12), U_(1), "21", v33); _intent.bypass(C_(13), U_(1), "21", v33); _intent.bypass(C_(0), U_(0), "1", "+5V_IOC")\n'
_NEW_4 = '    _intent.bypass(C_(12), U_(1), "21", v33); _intent.bypass(C_(13), U_(1), "21", v33); _intent.bypass(C_(0), U_(0), "1", "IOC%s_LDO_IN" % _tag)   # T10 round 6: behind the sense resistor\n    _intent.bypass(_GC(0), U_(5), "5", "+5V_IOC")\n    _intent.bypass(_GC(2), U_(6), "5", "+5V_IOC")\n'
_OLD_5 = '    pv = str(byref[e["part"]]["value"]); cv = str(byref[e["cap"]]["value"]); pin = e["pin"]\n'
_NEW_5 = '    pv = str(byref[e["part"]]["value"]); cv = str(byref[e["cap"]]["value"]); pin = e["pin"]\n    if pv.startswith("INA169"):   # T10 round 6 (record l9t5, cx45 Q3): the rail trip\'s current monitor\n        return ("D", "TI INA139/INA169 SBOS181F (v2/vendor/ti/held/ti-ina169-sbos181f.pdf) 8.2: \\"TI recommends placing a 0.1-uF "\n                     "capacitor near the V+ pin on the INA139 or INA169\\"")\n    if pv.startswith("TPS3701"):   # T10 round 6 (record l9t5, cx45 Q3): the rail trip\'s and the share limiters\' comparators\n        return ("D", "TI TPS3701 SBVS240C (v2/vendor/ti/held/ti-tps3701-sbvs240c.pdf) pin functions, VDD: \\"good analog design "\n                     "practice to place a 0.1-uF ceramic capacitor close to this pin\\"")\n'
_OLD_6 = '_IOC_LOADS = {"U40": 0.12, "U50": 0.12, "U60": 0.12}   # the allocations +5V_DEV carried for them (S-98 M7)\n'
_NEW_6 = '_IOC_LOADS = {"R600": 0.12, "R620": 0.12, "R640": 0.12}   # the allocations +5V_DEV carried for them (S-98 M7); T10 round 6 (record l9t5): the LDOs U40, U50, U60 sit behind their rail trips\' sense resistors R600, R620, R640\n'
_OLD_7 = "_GND_LOADS.update(_IOC_LOADS)   # record l9t5 (I-03): the three LDOs' ground ends; the return is shared, not lead by lead (l8r2 round 7)\n"
_NEW_7 = '_GND_LOADS.update({"U40": 0.12, "U50": 0.12, "U60": 0.12})   # record l9t5 (I-03): the three LDOs\' ground ends; the return is shared, not lead by lead (l8r2 round 7)\n'
EDITS = [(_OLD_0, _NEW_0), (_OLD_1, _NEW_1), (_OLD_2, _NEW_2), (_OLD_3, _NEW_3), (_OLD_4, _NEW_4), (_OLD_5, _NEW_5), (_OLD_6, _NEW_6), (_OLD_7, _NEW_7)]

def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if "_LDO_IN" in text or "_CAN1_SD" in text:
        refuse("the change is already applied")
    if "_CAN1_SHDN" not in text or '"+5V_IOC", "GND", "3": "IOC%s_LDO_EN"' not in text.replace('{"1": "+5V_IOC", "2": "GND", "3": "IOC%s_LDO_EN"', '"+5V_IOC", "GND", "3": "IOC%s_LDO_EN"'):
        refuse("record l9t5's iocbuck and canshdn drafts are not in the target: apply them first")
    for ref in ADDS:
        if re.search(r'"%s"' % ref, text):
            refuse("%s is already drawn as a literal designator" % ref)
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
    return new


# NOT RELEASED: record l9t5 drafts this change for the generator's owner and never applies it. Writing the repository's own generator
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
