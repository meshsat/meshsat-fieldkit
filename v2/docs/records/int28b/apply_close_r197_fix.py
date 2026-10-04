#!/usr/bin/env python3
"""Correct the page row apply_close_r197.py wrote (MESHSAT-1357, set 28, 4 October 2026). That script wrote L4-E9's page counts
row for the release records as "CLOSED 2; DRAFTED 2; OPEN 0; OWED 8; APPLIED 0"; L4-E9's output prints a state only while its count
is not zero ("by state CLOSED 2; DRAFTED 2; OWED 8; APPLIED 0"), and test_l4e9's table check holds the page to the output, so the box
suite on 3b9aa97d failed that one test. This writes the output's form; it asserts the old text once and refuses a second run."""
import sys
PAGE = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
OUT = "v2/docs/records/l4e9/l4e9_power_path.out"
OLD, NEW = "CLOSED 2; DRAFTED 2; OPEN 0; OWED 8; APPLIED 0", "CLOSED 2; DRAFTED 2; OWED 8; APPLIED 0"
t = open(PAGE, encoding="utf-8").read()
if t.count(OLD) != 1:
    print("apply_close_r197_fix: REFUSED: %d occurrence(s) of the old row" % t.count(OLD)); sys.exit(1)
if ("by state " + NEW) not in open(OUT, encoding="utf-8").read():
    print("apply_close_r197_fix: REFUSED: the output does not print the new form"); sys.exit(1)
open(PAGE, "w", encoding="utf-8").write(t.replace(OLD, NEW))
print("apply_close_r197_fix: the page row reads the output's form")
