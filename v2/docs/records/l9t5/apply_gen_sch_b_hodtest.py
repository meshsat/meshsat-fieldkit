#!/usr/bin/env python3
"""apply_gen_sch_b_hodtest.py: DRAFT for board B's generator owner (Layer 4 task L4A-58, the ledger's HO-D under W138's limiter; record
l4hod reads it; MESHSAT-1357, 7 October 2026, W146). NOT APPLIED to the tree by this record, like every draft of L4-E9's change list
(None is APPLIED); its author ran it only on scratch copies. It applies after W138's apply_gen_sch_b_regstage.py (record l4reg, the
TPS2553-1 limiter whose FAULT pin and output this draft reaches) and refuses a target without it. It composes with W137's and W143's
apply_gen_sch_b_canmb.py and W143's apply_gen_sch_b_canen.py in every order those two admit (it edits none of their lines and shares
none of their designators, nets or controller pins); writing the tree's own generator also needs canen's EN route in it, because the
test's restore is that route (record l4canen).

Why (record l4hod, v2/docs/records/l4hod/L4HOD.md; W127's check 1a and finding 4; the register's row L4A-58): the TPS2553-1's FAULT
asserts only while it limits ("asserted during an overcurrent, overtemperature, or reverse-voltage condition", SLVS841F 9.3.3), so a
limiter that has lost its limit looks healthy in service: a latent first failure that leaves the supervisor's regulator without the
current bound RE-7's thermal case rests on, found by nothing (the objection L8P-BREAKER.md states for the guard). The quorum tolerates
one supervisor out (IOHA row 3), so the other two can test each supervisor's limiter in service, one at a time:
  1. THE TEST LOAD (R800, R820, R840): 3.0 Ohm 1 % in 2512 (1 W at 70 C, UNI-ROYAL's thick-film series) from the limiter's output
     IOC{t}_LDO_IN to IOC{t}_TL: at the least input it asks more than twice the limiter's highest limit, and with a limiter that has
     lost its limit it draws at most 1.386 A, which U601 and the survivors' inputs carry (record l4hod section 8).
  2. THE TEST SWITCH, two AO3400A in series below it (Q590 and Q591 for controller A; Q592, Q593; Q594, Q595), the upper one gated
     by the NEXT controller, the lower one by the one after, each through 1 kOhm (R801, R803) with 100 kOhm to ground (R802, R804):
     no single peer can load the rail (2 of 2 to start), either peer alone ends the load, a dark or reset peer leaves its half off,
     and a stuck half is found by the procedure's single-switch steps without latching anything.
  3. THE FAULT READ: the limiter's FAULT pin (pin 4, left open by regstage) on IOC{t}_LIM_FLT, read by each peer through its own
     BAT46W (D404 and D405; D414, D415; D424, D425; the cathode on FAULT) from its own pin node pulled to its own 3.3 V by 10 kOhm
     (R805, R806): FAULT low pulls each pin low; a dark peer's diode is reverse biased and loads nothing.
  4. THE OUTPUT READ: each peer reads the limiter's output on its own ADC pin through its own 10 kOhm over 20 kOhm, 0.1 % 25 ppm
     (R807 and R808; R809 and R810), with 10 nF at the pin (C970, C971; C980, C981; C990, C991).
  5. THE PINS (per controller): PE12 and PE13 (pins 42 and 43, outputs) its half of the test switch on the next controller and on the
     one after; PE14 and PE15 (pins 44 and 45, inputs) their FAULT; PC0 (pin 15, ADC123_INP10) and PB1 (pin 35, ADC12_INP5) their
     output. Free on the composed map (43 of 100 used with canen; 49 with this draft).
The procedure (record l4hod section 9, DRAFTED for Layer 5's contract; L4A-61 propagates it): the two peers take the target out of the
quorum; prove the restore route by pulling its EN low and releasing it (record l4canen's route); close each half alone for 4 ms (a
stuck other half shows as a load, under the 5 ms printed least deglitch, so nothing latches); close both, read the output (the limit's
current through the 3.0 Ohm) and FAULT (its 5 to 10 ms deglitch) and the latch; open; restore through the EN route; the target rejoins.
Designators added: R800 to R810, R820 to R830, R840 to R850, Q590 to Q595, D404, D405, D414, D415, D424, D425, C970, C971, C980, C981,
C990, C991 (51 parts); none removed; changed: U45, U55, U65 (pin 4, FAULT, from NC to IOC{t}_LIM_FLT); the controllers' pins 15, 35, 42
to 45. Order codes owed (Layer 6): the 3.0 Ohm 2512, the two 0.1 % values, the 10 nF.
Usage:  apply_gen_sch_b_hodtest.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (already applied, regstage absent, an old text missing, a designator or a pin in use, or the
repository's own generator named before RELEASE-T10.md releases it, or without canen's EN route in it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_hodtest"
BOARD = "b"
ADDS = (tuple("R%d" % (800 + 20 * k + n) for k in range(3) for n in range(11)) + tuple("Q%d" % (590 + n) for n in range(6))
        + tuple("D%d" % (404 + 10 * k + n) for k in range(3) for n in (0, 1)) + tuple("C%d" % (970 + 10 * k + n) for k in range(3) for n in (0, 1)))
REMOVES = ()
CHANGED = tuple("U%d" % (45 + 10 * k) for k in range(3))
# the pin plan, read by record l4hod (never typed there): LQFP-100 pin -> (port, use, which target: 1 the next controller, 2 the one after)
TEST_PINS = {42: ("PE12", "switch", 1), 43: ("PE13", "switch", 2), 44: ("PE14", "fault", 1), 45: ("PE15", "fault", 2),
             15: ("PC0", "adc", 1), 35: ("PB1", "adc", 2)}
ADC_FUNC = {15: "ADC123_INP10", 35: "ADC12_INP5"}
R_LOAD, R_GS, R_GPD, R_FPU, R_TOP, R_BOT, C_ADC = "3R 1% 2512 1W", "1k", "100k", "10k", "10k 0.1% 25ppm", "20k 0.1% 25ppm", "10n"
FET, FET_LCSC, DIODE, DIODE_LCSC = "AO3400A", "C20917", "BAT46W-7-F", "C83152"

_OLD_FLT = '       {"1": "+5V_IOC", "2": "GND", "3": "IOC%s_LIM_EN" % _tag, "4": "NC", "5": "IOC%s_ILIM" % _tag, "6": "IOC%s_LDO_IN" % _tag})\n'
_NEW_FLT = ('       {"1": "+5V_IOC", "2": "GND", "3": "IOC%s_LIM_EN" % _tag, "4": "IOC%s_LIM_FLT" % _tag, "5": "IOC%s_ILIM" % _tag, "6": "IOC%s_LDO_IN" % _tag})'
            '   # FAULT (pin 4) read by the two peers since L4A-58 (record l4hod, apply_gen_sch_b_hodtest.py, NOT APPLIED)\n')
_OLD_RL = '    r(_GR(1), "49.9k 1%", "IOC%s_ILIM" % _tag, "GND")   # RILIM: the tested 49.9 kOhm row (SLVS841F 7.5)\n'
_NEW_RL = (
    _OLD_RL
    + "    # L4A-58 (record l4hod, W146, 7 October 2026; apply_gen_sch_b_hodtest.py, a DRAFT, NOT APPLIED): HO-D UNDER THE LIMITER, the other two\n"
    "    # controllers' in-service test of this one's limiter. FAULT asserts only while the limiter limits (SLVS841F 9.3.3), so a lost limit is\n"
    "    # invisible in service; the quorum tolerates one supervisor out (IOHA row 3), so the peers take this one out, load its rail above the\n"
    "    # limit through two series switches, one per peer (no single peer can load it, either peer alone ends it), read the limit acting (the\n"
    "    # output across the 3.0 Ohm on each peer's own divider and ADC pin) and FAULT (each peer through its own Schottky from its own rail),\n"
    "    # and restore it through record l4canen's EN route. Record l4hod reads every level, the procedure, its detection interval and the\n"
    "    # test path's own faults on the makers' printed figures\n"
    '    _hr = lambda n, _k=_k: "R%d" % (800 + 20 * _k + n)\n'
    '    _hp, _hq = "ABC"[(_k + 1) % 3], "ABC"[(_k + 2) % 3]   # the next controller and the one after: the two halves of this test\n'
    '    _htl, _htm, _hga, _hgb, _hfl = ("IOC%s_%s" % (_tag, _n) for _n in ("TL", "TM", "TGA", "TGB", "LIM_FLT"))\n'
    '    _hsa, _hsb, _hfa, _hfb, _hva, _hvb = ("IOC%s_%s%s" % (_tag, _n, _p) for _n, _p in (("TSW", _hp), ("TSW", _hq), ("FLT", _hp), ("FLT", _hq), ("VS", _hp), ("VS", _hq)))\n'
    '    r(_hr(0), "3R 1% 2512 1W", "IOC%s_LDO_IN" % _tag, _htl, "R2512")   # the test load from the limiter\'s output (UNI-ROYAL thick film, 1 W at 70 C)\n'
    '    part("Q%d" % (590 + 2 * _k), "Transistor_FET", "AO3400A", "AO3400A: the upper test switch of controller %s\'s limiter, gated by controller %s (records l4hod, l9t5)" % (_tag, _hp), "SOT23",\n'
    '         {"1": _hga, "2": _htm, "3": _htl}, "C20917")   # 1 G 2 S 3 D (board B\'s Q212 part)\n'
    '    part("Q%d" % (591 + 2 * _k), "Transistor_FET", "AO3400A", "AO3400A: the lower test switch of controller %s\'s limiter, gated by controller %s (records l4hod, l9t5)" % (_tag, _hq), "SOT23",\n'
    '         {"1": _hgb, "2": "GND", "3": _htm}, "C20917")\n'
    '    r(_hr(1), "1k", _hsa, _hga); r(_hr(2), "100k", _hga, "GND")   # the upper half: the next controller\'s pin, held off while it is dark\n'
    '    r(_hr(3), "1k", _hsb, _hgb); r(_hr(4), "100k", _hgb, "GND")   # the lower half: the one after\'s pin\n'
    '    r(_hr(5), "10k", "+3V3_IOC%s" % _hp, _hfa); part(_GD(4), "Device", "D_Schottky", "BAT46W-7-F: controller %s reads controller %s\'s limiter FAULT (cathode on FAULT)" % (_hp, _tag), "SOD123", {"1": _hfl, "2": _hfa}, "C83152")\n'
    '    r(_hr(6), "10k", "+3V3_IOC%s" % _hq, _hfb); part(_GD(5), "Device", "D_Schottky", "BAT46W-7-F: controller %s reads controller %s\'s limiter FAULT (cathode on FAULT)" % (_hq, _tag), "SOD123", {"1": _hfl, "2": _hfb}, "C83152")\n'
    '    r(_hr(7), "10k 0.1% 25ppm", "IOC%s_LDO_IN" % _tag, _hva); r(_hr(8), "20k 0.1% 25ppm", _hva, "GND"); c("C%d" % (970 + 10 * _k), "10n", _hva, "GND")   # the next controller\'s read of the output\n'
    '    r(_hr(9), "10k 0.1% 25ppm", "IOC%s_LDO_IN" % _tag, _hvb); r(_hr(10), "20k 0.1% 25ppm", _hvb, "GND"); c("C%d" % (971 + 10 * _k), "10n", _hvb, "GND")   # the one after\'s\n')
_OLD_SYN = '    # D-13, 26 September 2026: the symbol, the value and the order line name the part bought, STM32H743VIT6 (C114409).\n'
_NEW_SYN = (
    "    # L4A-58 (record l4hod, W146; apply_gen_sch_b_hodtest.py, NOT APPLIED): the limiter's in-service test. PE12 and PE13 (pins 42 and 43,\n"
    "    # GPIO outputs) close this controller's half of the test switch on the next controller and on the one after (2 of 2 with the other\n"
    "    # peer); PE14 and PE15 (pins 44 and 45, inputs) read their limiters' FAULT through this controller's own Schottky and pull-up; PC0\n"
    "    # (pin 15, ADC123_INP10) and PB1 (pin 35, ADC12_INP5) read their limiters' output through this controller's own 10k over 20k\n"
    '    m.update({42: "IOC%s_TSW%s" % ("ABC"[(_k + 1) % 3], _tag), 43: "IOC%s_TSW%s" % ("ABC"[(_k + 2) % 3], _tag),\n'
    '              44: "IOC%s_FLT%s" % ("ABC"[(_k + 1) % 3], _tag), 45: "IOC%s_FLT%s" % ("ABC"[(_k + 2) % 3], _tag),\n'
    '              15: "IOC%s_VS%s" % ("ABC"[(_k + 1) % 3], _tag), 35: "IOC%s_VS%s" % ("ABC"[(_k + 2) % 3], _tag)})\n'
    + _OLD_SYN)
EDITS = [(_OLD_FLT, _NEW_FLT), (_OLD_RL, _NEW_RL), (_OLD_SYN, _NEW_SYN)]
PLANNED = tuple(TEST_PINS)


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if "_LIM_FLT" in text or "_TSW%s" in text:
        refuse("the change is already applied")
    if text.count(_OLD_FLT) != 1 or text.count(_OLD_RL) != 1 or "TPS2553-1" not in text:
        refuse("W138's regstage draft (apply_gen_sch_b_regstage.py, record l4reg, fnd/l4reg 86dbcdff) is not in the target: apply it first")
    for ref in ADDS:
        if re.search(r'"%s"' % ref, text):
            refuse("%s is already drawn as a literal designator" % ref)
    if (not re.search(r"_GR = lambda n, _k=_k: \"R%d\" % \(600 \+ 20 \* _k \+ n\)", text)
            or not re.search(r"_GD = lambda n, _k=_k: \"D%d\" % \(400 \+ 10 \* _k \+ n\)", text)):
        refuse("the controllers' numbering (_GR(n) = R600 + 20k + n, _GD(n) = D400 + 10k + n) is not the one this draft was written against")
    if text.count(_OLD_SYN) != 1 or text.count('    m.update({14: "IOC%s_RST_n" % _tag') != 1:
        refuse("the controllers' pin map is not the one this draft was written against")
    blk = text[text.index('    m.update({14: "IOC%s_RST_n" % _tag'):text.index(_OLD_SYN)]
    taken = [p for p in PLANNED if re.search(r"(?<![\d.])%d: " % p, blk)]
    if taken:
        refuse("pin(s) %s are already on the controllers' map" % taken)
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


# NOT RELEASED: record l4hod drafts this change for the generator's owner and never applies it. Writing the repository's own generator
# is refused until RELEASE-T10.md beside this script reads "released: yes" on its first line and names an accepted check of task T10
# ("check: <repository path whose first line is 'accepted: yes'>"), and until record l4canen's EN route (apply_gen_sch_b_canen.py) is in
# the generator: the test latches the limiter it tests and that route is its restore. A copy elsewhere may be written in any order (the
# record composes every order on scratch copies).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_%s.py" % BOARD)
RELEASE = os.path.join(HERE, "RELEASE-T10.md")


def released(text):
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
    if "_RSTV%s" not in text:
        refuse("NOT RELEASED: record l4canen's EN route (apply_gen_sch_b_canen.py) is not in the generator; the test's restore is that route")


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    text = open(target, encoding="utf-8").read()
    if write and os.path.realpath(target) == os.path.realpath(TREE_GEN):
        released(text)
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
