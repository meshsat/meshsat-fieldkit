#!/usr/bin/env python3
"""DRAFT for the owner of pcb_rules_coverage.yaml's SCH-003 row (stream w4r, MESHSAT-1357, 27 September 2026).

WHY. Stream w4r owns only the INT-001 row of the coverage map. SCH-003's note still describes block_contract.py as
comparing E5 with board A's BOARD FILE ("33 checks on the current A"); since w4r the tool reads board A's current
netlist and the J_DOCK land that netlist names, and it judges board A's blind-mate power pins too, and SCH-003 on E5
reads the same reading (check_contracts_e5, now shared with INT-001 on E5, whose row says why). One sentence is
appended to SCH-003's note; nothing that decides anything changes. Apply after the w4r coverage map lands.

Usage: patch_coverage_sch003.py <tree root holding v2/ecad>"""
import os, sys

p = os.path.join(sys.argv[1], "v2", "ecad", "tools", "pcb_rules_coverage.yaml")
s = open(p, encoding="utf-8").read(); o = s
old = 'so they decide inhibit_chain_<letter> and move neither check_contracts_<letter> nor the set verdict."}'
new = ('so they decide inhibit_chain_<letter> and move neither check_contracts_<letter> nor the set verdict. 27 September '
       '2026 (stream w4r): block_contract.py reads board A\'s CURRENT netlist and the J_DOCK land it names, mounted as '
       'gen_pcb_a3.py mounts it, and no longer board A\'s board file, whose committed layout predates EQ-16; it also '
       'judges every blind-mate power pin of board A\'s netlist against a target of its kind. On main 91894cd7\'s files '
       'the reading went from PASS 33 of 33 (against the board file) to FAIL, 28 of 38 (against the netlist): E5\'s '
       'targets under J_DOCK pins 1 to 4 and their wire lands still carry VIN_RAW and no target takes J_VR1 to J_VR4 or '
       'J_VN1 to J_VN4 (S-74). The same reading decides INT-001 on E5 (its row\'s verdict_by_board and '
       '_verdict_by_board_why)."}')
if s.count(old) != 1: raise SystemExit("patch_coverage_sch003: the anchor is not there exactly once (%d)" % s.count(old))
s = s.replace(old, new); assert s != o
import yaml
yaml.safe_load(s)
open(p, "w", encoding="utf-8").write(s)
print("patch_coverage_sch003: SCH-003's note carries the w4r sentence")
