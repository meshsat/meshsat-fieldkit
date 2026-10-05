#!/usr/bin/env python3
"""apply_gen_sch_b_canshdn.py: DRAFT for board B's generator owner (Layer 9 record l9t5, task T10 round 5, findings L9T5-F16, F17
and F18, MESHSAT-1357, 5 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies. It is
order-free against the other drafts of board B (it touches only the supervisors' transceiver block); record l9t5 composes it
straight after apply_gen_sch_b_iocpre.py.

The correction (record l9t5's l9t5_t10.out section 10f): each of the six TCAN334D transceivers (U43, U44, U53, U54, U63, U64) has
its SHDN pin (pin 5) on no net today (the generator writes "NC"), so it rests on the part's internal pull-down, which TI calls a
fall-back that "should not be relied on by design" (SLLSEQ7F 6.3.6, p.20). The draft:
  1. puts each transceiver's pin 5 on a net of its own controller: IOC{t}_CAN1_SHDN on PD2 (pin 83) for fabric A, IOC{t}_CAN2_SHDN
     on PB14 (pin 53) for fabric B (both free on the generator's pin map; plain GPIO in DS12110 Rev 10 Table 7);
  2. pulls each of those nets to GND through 100 k (R_(4) and R_(5) of the controller's block: R67, R68, R79, R80, R91, R92), so a
     controller in reset or unpowered leaves its transceivers in normal mode, exactly as the board behaves today.
SHDN high is the transceiver's shutdown mode: driver and receiver off, at most 2.5 uA from VCC (SLLSEQ7F 5.5 and Table 6-5); the
firmware row FW-B21 (apply_hw_fw_contract_t10.py) drives it high on a faulted fabric. No other part, net or declaration changes.
Usage:  apply_gen_sch_b_canshdn.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the change is already applied, an old text is missing, a designator the draft adds is
already drawn, or the repository's own generator is named before RELEASE-T10.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_canshdn"
BOARD = "b"
ADDS = ("R67", "R68", "R79", "R80", "R91", "R92")
SHDN_PIN = {"A": 83, "B": 53}          # PD2 next to FDCAN1's PD0/PD1, PB14 next to FDCAN2's PB12/PB13
PULL = "100k"

_OLD_MAP = '              38: "BSEL1", 39: "BSEL2", 40: "BSEL3", 41: "WIFI_SEC"})\n'
_NEW_MAP = ('              38: "BSEL1", 39: "BSEL2", 40: "BSEL3", 41: "WIFI_SEC",\n'
            '              # T10 ROUND 5, RECORD l9t5 (L9T5-F16 to F18): each transceiver\'s SHDN from its controller, PD2 (pin 83) for fabric A\n'
            '              # and PB14 (pin 53) for fabric B; the firmware row FW-B21 shuts a faulted fabric\'s transceiver down\n'
            '              %d: "IOC%%s_CAN1_SHDN" %% _tag, %d: "IOC%%s_CAN2_SHDN" %% _tag})\n' % (SHDN_PIN["A"], SHDN_PIN["B"]))
_OLD_IC = ('           {"1": _tx, "2": "GND", "3": v33, "4": _rx, "5": "NC", "6": "CANL_%s%s" % (_f, _seg), "7": "CANH_%s%s" % (_f, _seg), "8": "GND"}, "C2871143")\n')
_NEW_IC = ('           {"1": _tx, "2": "GND", "3": v33, "4": _rx, "5": "IOC%s_CAN%d_SHDN" % (_tag, _un - 2), "6": "CANL_%s%s" % (_f, _seg), "7": "CANH_%s%s" % (_f, _seg), "8": "GND"}, "C2871143")\n'
           '        # T10 round 5 (record l9t5): SHDN held low by 100 k while the controller is in reset or dark (TI SLLSEQ7F 6.3.6: the internal\n'
           '        # pull-down is a fall-back only); the controller drives it high to shut a faulted fabric\'s transceiver down (Table 6-5)\n'
           + '        r(R_(_un + 1), "%s", "IOC%%s_CAN%%d_SHDN" %% (_tag, _un - 2), "GND")\n' % PULL)
EDITS = [(_OLD_MAP, _NEW_MAP), (_OLD_IC, _NEW_IC)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if "_CAN1_SHDN" in text or "_CAN2_SHDN" in text:
        refuse("the change is already applied")
    # the designators the draft adds must be free: R_(n) of a controller's block is R(63 + 12k + n)
    for ref in ADDS:
        if re.search(r'\br\(\s*"%s"' % ref, text):
            refuse("%s is already drawn as a literal designator" % ref)
    if not re.search(r"R_ = lambda n, _k=_k: \"R%d\" % \(63 \+ 12 \* _k \+ n\)", text):
        refuse("the controllers' resistor numbering (R_(n) = R63 + 12k + n) is not the one this draft was written against")
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
