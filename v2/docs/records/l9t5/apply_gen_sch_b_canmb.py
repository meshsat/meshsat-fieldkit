#!/usr/bin/env python3
"""apply_gen_sch_b_canmb.py: DRAFT for board B's generator owner (Layer 9 record l9t5, task T10 round 7; Layer 4 task L4A-54: RE-5
and HO-C by method M-B, re-selected by W129 on W127's finding 1; MESHSAT-1357, 7 October 2026). NOT APPLIED to the tree by this
record, like every draft of L4-E9's change list (None is APPLIED); its author ran it only on scratch copies. It is the successor of
apply_gen_sch_b_iocguard.py: it applies straight after it (it edits its lines) and refuses a target without it.

Why (the ledger's RE-5 and HO-C, `records/l4close/REMAINING-ENGINEERING.md`; cx46 item 5; l9t5_t10.out 10j (c)): round 6's
transmit-share limiter admits a TX pin toggled as a GPIO under its least 4.7 % share and a latent stuck comparator, so CON-004's
quorum service stays OPEN. The record's own route (l9t5_t10.out 10j (c)): "each controller's TXD read by the other two and a 2-of-2
vote of the other two on its SHDN or its LDO's EN". This draft takes it on SHDN, per fabric:
  1. OBSERVATION (twelve inputs): each controller's TXD on each fabric (IOC{t}_CAN1_TX, IOC{t}_CAN2_TX) reaches each of the other
     two controllers through its own 4.7 kOhm 1 % (R(600 + 20k + 11 to 14)): pins 63 to 66 (PC6 to PC9, TIM3_CH1 to TIM3_CH4 on AF2,
     DS12110 Rev 10 Table 12) of the reader read the next controller's TXD on fabric A and B, then the one after it on A and B. The
     resistor keeps a faulty reader from moving the line: the TXD output holds its level against it (l9t5_canmb.out section 4).
  2. THE VOTE (twelve outputs, two per transceiver): each controller drives four votes on pins 55 to 58 (PD8 to PD11, GPIO), one
     per transceiver of the other two; each transceiver's two votes enter an SN74LVC1G08 (U(40 + 10k + 7 + j), the limiter's place)
     on the TARGET controller's own 3.3 V, whose output lifts that transceiver's SHDN through a 1N4148W (D(400 + 10k + 2j + 1), the
     limiter's diode) only while BOTH peers drive it: one faulty peer cannot silence a healthy controller. Each vote input is held
     low by 10 kOhm (R(600 + 20k + 4 + 4j) and R(600 + 20k + 5 + 4j), the limiter's dividers' places) while its voter is in reset
     or dark. The controller's own SHDN request keeps its diode and SD's 100 kOhm (canshdn and iocguard, unchanged).
  3. THE LIMITER REMOVED (SESSION W137-D2, reversible): the six TPS3701 share comparators, their 1 MOhm and 150 kOhm dividers, 1 uF
     filters and 10 kOhm pull-ups go; the rail trips of iocguard stay as they are (RE-6 and RE-7 are L4A-56 to L4A-58's).
CON-004's two fabrics, their six transceivers, their four split terminations and the two break links of test A7 are untouched.
Designators: twelve new resistors R611 to R614, R631 to R634, R651 to R654 (R(600 + 20k + 11 + 2j + i)); the gates take U47, U48,
U57, U58, U67, U68 and their decoupling C944, C946, C954, C956, C964, C966 (the comparators' places); removed: R606, R610, R626,
R630, R646, R650 and C943, C945, C953, C955, C963, C965. The SN74LVC1G08DBVR (JLCPCB C7666) and the 1N4148W (C81598) are board
B's parts already.
Usage:  apply_gen_sch_b_canmb.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (already applied, iocguard absent, an old text missing, a designator or a pin in use, or the
repository's own generator named before RELEASE-T10.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_canmb"
BOARD = "b"
ADDS = tuple("R%d" % (600 + 20 * k + 11 + n) for k in range(3) for n in range(4))
REMOVES = tuple("R%d" % (600 + 20 * k + n) for k in range(3) for n in (6, 10)) + tuple("C%d" % (940 + 10 * k + n) for k in range(3) for n in (3, 5))
# the pin plan, read by l9t5_canmb.py (never typed there): LQFP-100 pin -> (port, which peer (1 next, 2 the one after), fabric, use, AF)
OBS_PINS = {63: ("PC6", 1, "A", "TIM3_CH1", 2), 64: ("PC7", 1, "B", "TIM3_CH2", 2), 65: ("PC8", 2, "A", "TIM3_CH3", 2), 66: ("PC9", 2, "B", "TIM3_CH4", 2)}
VOTE_PINS = {55: ("PD8", 1, "A"), 56: ("PD9", 1, "B"), 57: ("PD10", 2, "A"), 58: ("PD11", 2, "B")}
R_ISO, R_VOTE, GATE, GATE_LCSC = "4.7k 1%", "10k", "SN74LVC1G08DBVR", "C7666"

_OLD_MAP = '              83: "IOC%s_CAN1_SHDN" % _tag, 53: "IOC%s_CAN2_SHDN" % _tag})\n'
_NEW_MAP = ('              83: "IOC%s_CAN1_SHDN" % _tag, 53: "IOC%s_CAN2_SHDN" % _tag,\n'
            '              # T10 ROUND 7 (record l9t5, L4A-54, M-B; apply_gen_sch_b_canmb.py, NOT APPLIED): the peers\' observation and vote.\n'
            '              # PC6 to PC9 (pins 63 to 66; TIM3_CH1 to TIM3_CH4, AF2, DS12110 Rev 10 Table 12) read the next controller\'s TXD on\n'
            '              # fabric A and B, then the one after it on A and B, each through the 4.7 kOhm of the controller it reads; PD8 to PD11\n'
            '              # (pins 55 to 58, GPIO outputs) are this controller\'s votes to silence those four transceivers (2 of 2 with the other peer)\n'
            '              63: "IOC%s_CAN1_OBS%s" % ("ABC"[(_k + 1) % 3], _tag), 64: "IOC%s_CAN2_OBS%s" % ("ABC"[(_k + 1) % 3], _tag),\n'
            '              65: "IOC%s_CAN1_OBS%s" % ("ABC"[(_k + 2) % 3], _tag), 66: "IOC%s_CAN2_OBS%s" % ("ABC"[(_k + 2) % 3], _tag),\n'
            '              55: "IOC%s_CAN1_VOTE%s" % ("ABC"[(_k + 1) % 3], _tag), 56: "IOC%s_CAN2_VOTE%s" % ("ABC"[(_k + 1) % 3], _tag),\n'
            '              57: "IOC%s_CAN1_VOTE%s" % ("ABC"[(_k + 2) % 3], _tag), 58: "IOC%s_CAN2_VOTE%s" % ("ABC"[(_k + 2) % 3], _tag)})\n')
_OLD_LIM = (
    '        # T10 ROUND 6 (record l9t5, cx45 Q3): THE TRANSMIT-SHARE LIMITER, independent of any firmware. TXD averaged over 130 ms (1 MOhm\n'
    "        # and 150 kOhm at 0.1 %, 1 uF): with TXD high when recessive the average is 0.130 of the rail times (1 - the dominant share); a TPS3701's\n"
    '        # comparator B holds LIMO low while the average is over its threshold (OUTB low) and releases it when the share passes 4.7 to\n'
    "        # 12.4 %; LIMO's pull-up then lifts SHDN through a diode. The controller's own SHDN request reaches SHDN through the other diode\n"
    "        # (the 100 kOhm on SD holds it low otherwise: TI's pin sources up to 4 uA, SLLSEQ7F IIL)\n"
    '        _j = _un - 3\n'
    '        _sd, _lim, _lo = "IOC%s_CAN%d_SD" % (_tag, _un - 2), "IOC%s_CAN%d_LIM" % (_tag, _un - 2), "IOC%s_CAN%d_LIMO" % (_tag, _un - 2)\n'
    '        part(_GD(2 * _j), "Device", "D", "1N4148W: controller %s\'s own SHDN request onto its fabric %s transceiver (cathode on SD)" % (_tag, _f), "SOD123", {"1": _sd, "2": "IOC%s_CAN%d_SHDN" % (_tag, _un - 2)}, "C81598")\n'
    '        part(_GD(2 * _j + 1), "Device", "D", "1N4148W: the transmit-share limiter onto the same SHDN (cathode on SD)", "SOD123", {"1": _sd, "2": _lo}, "C81598")\n'
    '        r(_GR(3 + 4 * _j), "100k", _sd, "GND")\n'
    '        r(_GR(4 + 4 * _j), "1M 0.1%", _tx, _lim); r(_GR(5 + 4 * _j), "150k 0.1%", _lim, "GND"); c(_GC(3 + 2 * _j), "1u 16V X7R", _lim, "GND")\n'
    '        ic(U_(7 + _j), 6, "TPS3701DDCR window comparator (TI SBVS240C): controller %s\'s fabric %s transmit-share limiter, OUTB released (SHDN high) over the share" % (_tag, _f), "SOT236",\n'
    '           {"1": "NC", "2": "GND", "3": "GND", "4": _lim, "5": "+5V_IOC", "6": _lo}, "C132788")   # INA unused (OUTA open)\n'
    '        r(_GR(6 + 4 * _j), "10k 1%", v33, _lo)   # LIMO\'s pull-up from the controller\'s own rail\n'
    '        c(_GC(4 + 2 * _j), "100n", "+5V_IOC", "GND")   # the comparator\'s VDD\n'
    '        _intent.bypass(_GC(4 + 2 * _j), U_(7 + _j), "5", "+5V_IOC")\n')
_NEW_VOTE = (
    "        # T10 ROUND 7 (record l9t5, Layer 4 task L4A-54: RE-5 and HO-C by method M-B; apply_gen_sch_b_canmb.py, a DRAFT, NOT APPLIED):\n"
    "        # THE PEERS' 2-OF-2 VOTE takes the place of round 6's transmit-share limiter (removed: SESSION W137-D2). This TXD reaches each\n"
    "        # of the other two controllers through its own 4.7 kOhm (a faulty reader cannot move the line: the push-pull output holds its\n"
    "        # level against it, l9t5_canmb.out section 4); those two each drive one input of an SN74LVC1G08 on THIS controller's own 3.3 V,\n"
    "        # whose output lifts this transceiver's SHDN through a 1N4148W only while BOTH drive it, so one faulty peer cannot silence a\n"
    "        # healthy controller (SHDN high: driver and receiver off, RXD high, SLLSEQ7F Table 6-5). Each vote input is held low by 10 kOhm\n"
    "        # while its voter is in reset or dark. The controller's own SHDN request keeps its diode; SD's 100 kOhm holds normal mode\n"
    "        # otherwise. CON-004's two fabrics, their transceivers and termination are unchanged (IOHA row 7, test A7)\n"
    '        _j = _un - 3\n'
    '        _sd, _mb = "IOC%s_CAN%d_SD" % (_tag, _un - 2), "IOC%s_CAN%d_MB" % (_tag, _un - 2)\n'
    '        _p1, _p2 = "ABC"[(_k + 1) % 3], "ABC"[(_k + 2) % 3]   # the next controller and the one after it\n'
    '        _v1, _v2 = "IOC%s_CAN%d_VOTE%s" % (_tag, _un - 2, _p1), "IOC%s_CAN%d_VOTE%s" % (_tag, _un - 2, _p2)\n'
    '        part(_GD(2 * _j), "Device", "D", "1N4148W: controller %s\'s own SHDN request onto its fabric %s transceiver (cathode on SD)" % (_tag, _f), "SOD123", {"1": _sd, "2": "IOC%s_CAN%d_SHDN" % (_tag, _un - 2)}, "C81598")\n'
    '        part(_GD(2 * _j + 1), "Device", "D", "1N4148W: the peers\' 2-of-2 vote onto the same SHDN (cathode on SD)", "SOD123", {"1": _sd, "2": _mb}, "C81598")\n'
    '        r(_GR(3 + 4 * _j), "100k", _sd, "GND")\n'
    '        r(_GR(4 + 4 * _j), "10k", _v1, "GND"); r(_GR(5 + 4 * _j), "10k", _v2, "GND")   # each vote input low while its voter is in reset or dark\n'
    '        lvc1g08(U_(7 + _j), _v1, _v2, _mb, v33, _GC(4 + 2 * _j), "controller %s\'s fabric %s silence, the 2-of-2 vote of controllers %s and %s (record l9t5, M-B)" % (_tag, _f, _p1, _p2))\n'
    '        for _i, _o in enumerate((_p1, _p2)):\n'
    '            r(_GR(11 + 2 * _j + _i), "4.7k 1%", _tx, "IOC%s_CAN%d_OBS%s" % (_tag, _un - 2, _o))   # controller _o reads this TXD through it\n')
EDITS = [(_OLD_MAP, _NEW_MAP), (_OLD_LIM, _NEW_VOTE)]
PLANNED = tuple(OBS_PINS) + tuple(VOTE_PINS)


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if "_CAN%d_MB\" % (_tag" in text or "_CAN1_OBS%s" in text:
        refuse("the change is already applied")
    if text.count(_OLD_LIM) != 1 or "_LDO_IN" not in text or "_CAN1_SHDN" not in text:
        refuse("record l9t5's iocguard draft (with iocbuck, iocpre, canshdn and iocset before it) is not in the target: apply it first")
    for ref in ADDS:
        if re.search(r'"%s"' % ref, text):
            refuse("%s is already drawn as a literal designator" % ref)
    if not re.search(r"U_ = lambda n, _k=_k: \"U%d\" % \(40 \+ 10 \* _k \+ n\)", text) or "def lvc1g08(" not in text:
        refuse("the controllers' numbering (U_(n) = U40 + 10k + n) or the SN74LVC1G08 helper is not the one this draft was written against")
    blk = text[text.index("    m.update({14: \"IOC%s_RST_n\" % _tag"):text.index(_OLD_MAP)]
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


# NOT RELEASED: record l9t5 drafts this change for the generator's owner and never applies it. Writing the repository's own generator
# is refused until RELEASE-T10.md beside this script reads "released: yes" on its first line and names an accepted check of task T10
# ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the record's script does).
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
