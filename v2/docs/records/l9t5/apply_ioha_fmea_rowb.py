#!/usr/bin/env python3
"""apply_ioha_fmea_rowb.py: DRAFT apply script on v2/docs/ARCH-PCB-B-IOHA.md, section 12 (the FMEA) (Layer 9 record l9t5, round 10;
Layer 4 task L4A-61; MESHSAT-1357, 7 October 2026, W151). UNAPPLIED: the integrator runs it; this record runs it only on scratch copies.

WHAT IT IS: four FMEA rows for the failures row (b)'s drafts are built to survive or knowingly expose, appended after row 20, and one
paragraph after the table naming how each new row is shown (the contract's V rows). L9T5-F21 ("a supervisor whose firmware babbles on
both fabrics ... is in no FMEA row", record l9t5 `l9t5_t10.out` section 11) and W146-F7 ("IOHA section 12 needs the test's rows") are
the reasons. Rows 1 to 20 are left word for word: what row (b) changes in them is carried by the new rows (a supervisor out is still
row 3; both fabrics broken still row 8).
  21  a supervisor that babbles or drives its TX pin as a GPIO: the peers' attribution and 2-of-2 SHDN vote (record l9t5 canmb, canq);
  22  a supervisor's load over its limiter: the TPS2553-1's limit and latch, the peers' 2-of-2 restart (regstage, canen);
  23  a supervisor's limiter losing its limit, latently: the peers' in-service test (hodtest, record l4hod);
  24  the vote path's and the test path's own latent faults: the self-test (W143) and the test's steps and continuous checks (W146).
Every figure is the drafts' records' (DRAFTED, MODEL on printed figures, none applied, unchecked until row (b)'s check L4A-62).
Usage:  apply_ioha_fmea_rowb.py [TARGET] [--check | --write]   (default TARGET: the tree's v2/docs/ARCH-PCB-B-IOHA.md; default --check)
Exit 0: checked (or written); 3: refused (already applied, an anchor missing or not unique, or the result does not re-parse)."""
import os
import re
import sys

NAME = "apply_ioha_fmea_rowb"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE = os.path.join(REPO, "v2", "docs", "ARCH-PCB-B-IOHA.md")
ROW20 = "| 20 | The whole control plane is unpopulated (a build without it) |"
SEC13 = "\n## 13. Acceptance tests\n"
ROWS = (
    "| 21 | A supervisor's firmware babbles on both fabrics, or drives its TX pin as a GPIO (L9T5-F21) | n/a | its two peers read its "
    "TXDs through their own buffers and captures, attribute the deviation and vote its transceivers' SHDN, 2 of 2, within 1.310 ms; the "
    "quorum continues between the other two (record l9t5 `l9t5_canq.out`, method M-B, DRAFTED) | each peer's attribution of the TXD it "
    "reads against the frames on the bus (a dominant run over 11 bit-times, edges closer than half a bit-time, a frame outside its slot) "
    "| one faulty peer cannot silence a healthy controller (2 of 2); one firmware fault in all three is outside this row |\n"
    "| 22 | A supervisor's load over its limiter (a fault on its own 3.3 V, or a firmware state over its bound) | n/a | its TPS2553-1 limits "
    "it at 0.4702 to 0.5704 A and latches it off at most 10 ms later; the other two keep the quorum (row 3); its two peers restart it "
    "through the limiter's EN, 2 of 2, at most once in 10 s (records l9t5 `apply_gen_sch_b_regstage.py` and l4canen, DRAFTED) | its "
    "heartbeat stops on both fabrics; its limiter's FAULT, read by each peer | a fault that persists latches it again after each restart; "
    "its regulator's junction while its output is out of regulation is outside the criterion (W151-1, record l9t5 `l9t5_t10.out` 11a (f)) |\n"
    "| 23 | A supervisor's limiter loses its limit, latently | n/a | found by the peers' in-service test within 3602.341 s of its onset "
    "(102.341 s if present at start-up); a test takes its target out of the quorum for 5.945 s an hour, two of three serving meanwhile "
    "(record l4hod, DRAFTED) | the test's LIMIT NOT SHOWN or LIMIT HIGH | until it is found an overload on that rail is not limited (a "
    "second fault); during a test there is no spare, so a second supervisor lost then is row 4 |\n"
    "| 24 | The vote path or the test path fails latently (a stuck vote output, a dead buffer, a stuck test switch, a stuck FAULT read) | "
    "n/a | the vote path's self-test finds each within 2.60 s (8.545 s across an in-service test, W146-F2); the test path's own faults are "
    "found by the test's steps or its continuous checks, each within its bound (record l4hod, 35 rows) | the self-test's phases and the "
    "test's steps and continuous checks | a limiter whose latch does not clear on EN leaves its supervisor off (the restart route retries "
    "every 10 s) |\n")
NOTE = ("\nRows 21 to 24 (7 October 2026, record l9t5 round 10, Layer 4 task L4A-61) carry row (b)'s drafts, none applied and none checked "
        "yet (row (b)'s check is L4A-62): rows 21 and 24's vote path is shown by V-B22, row 22 by V-B23 and rows 23 and 24's test path by "
        "V-B25 of `HW-FW-CONTRACT.md`, all drafted (records l9t5 `apply_hw_fw_contract_canq.py` and `apply_hw_fw_contract_rowb.py`).\n")


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def fmea_rows(text):
    sec = text.split("\n## 12. FMEA\n", 1)
    if len(sec) != 2:
        refuse("section 12 (FMEA) is not in the file once")
    body = sec[1].split("\n## 13.", 1)[0]
    out = []
    for line in body.splitlines():
        if re.match(r"^\| \d+ \|", line):
            cells = line.strip().strip("|").split(" | ")
            if len(cells) != 6:
                refuse("an FMEA row carries %d cells, not 6: %s" % (len(cells), line[:30]))
            out.append(int(cells[0]))
    return out


def patched(text):
    if "| 21 | A supervisor's firmware babbles" in text or NOTE.strip() in text:
        refuse("the change is already applied")
    if fmea_rows(text) != list(range(1, 21)):
        refuse("section 12's rows are not 1 to 20 as this draft was written against")
    r20 = [l for l in text.splitlines(True) if l.startswith(ROW20)]
    if len(r20) != 1 or text.count(SEC13) != 1:
        refuse("row 20 or section 13's heading is not in the file once")
    new = text.replace(r20[0], r20[0] + ROWS)
    head, tail = new.split(SEC13)
    new = head.rstrip("\n") + "\n" + NOTE + SEC13 + tail
    if new == text:
        refuse("the result does not differ")
    if fmea_rows(new) != list(range(1, 25)):
        refuse("section 12's rows do not read 1 to 24 after the change")
    if re.search("[" + chr(0x2013) + chr(0x2014) + "]", ROWS + NOTE):
        refuse("a long dash in the new text")
    return new


def main(argv):
    target, mode = TREE, "--check"
    for a in argv:
        if a in ("--check", "--write"):
            mode = a
        else:
            target = os.path.abspath(a)
    if not os.path.isfile(target):
        refuse("no target %s" % target)
    old = open(target, encoding="utf-8").read()
    new = patched(old)
    if mode == "--write":
        tmp = target + ".rowb-tmp"
        open(tmp, "w", encoding="utf-8").write(new)
        os.replace(tmp, target)
        print("%s: WRITTEN, FMEA rows 21 to 24 and their note" % NAME)
    else:
        print("%s: CHECK OK, FMEA rows 21 to 24 and their note would be added (nothing written)" % NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
