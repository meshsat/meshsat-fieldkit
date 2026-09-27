#!/usr/bin/env python3
"""DRAFT registry change of stream w4r (MESHSAT-1357, 27 September 2026), for the integrator.

Applied to v2/ecad/tools/pcb_requirements.yaml of the tree named on the command line, by record id, with the edited
text asserted first. It adds no SC-nn and no S-nn (the stream's choice is recorded where the coverage map records tool
and evidence choices, INT-001's `_verdict_by_board_why`, with its reason and its reversal); it appends one sentence to
S-74's title, which lists what of EQ-16 is still in flight, so the open item names the reading that now shows its E5
half on current evidence.

S-74 stays OPEN. Nothing is rebound: S-74 records no artefact sha.

Usage: apply_registry.py <tree root holding v2/ecad>"""
import os, re, sys, textwrap

ROOT = sys.argv[1]
REG = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_requirements.yaml")
s = open(REG, encoding="utf-8").read(); orig = s

i = s.find("\n  - id: S-74\n")
if i < 0 or s.count("\n  - id: S-74\n") != 1: raise SystemExit("apply_registry: S-74 is not there exactly once")
j = s.find("\n  - id: ", i + 1)
blk = s[i + 1:j + 1]
m = re.search(r"(    title: >-\n)((?:      .*\n)+)", blk)
if not m: raise SystemExit("apply_registry: S-74 carries no folded title")
title = " ".join(m.group(2).split())
TAIL = "v2/docs/ARCHITECTURE.md's IF-AE-DOCK lines were brought to 14.10 A on the power pins in the same integration."
if not title.endswith(TAIL): raise SystemExit("apply_registry: S-74's title does not end as w4r read it: %r" % title[-120:])
ADD = ("Since stream w4r (27 September 2026) the dock block's contract reading check_contracts_e5 (block_contract.py) "
       "judges E5 against board A's current netlist instead of board A's board file, and reads FAIL on current evidence "
       "until E5 is regenerated for EQ-16: the targets under J_DOCK pins 1 to 4 and their wire lands still carry VIN_RAW where board "
       "A's netlist has GND, and no E5 target takes J_VR1 to J_VR4 or J_VN1 to J_VN4. It decides SCH-003 and, on E5, "
       "INT-001, which is how the E5 half of this item shows on the layout-entry page.")
assert ADD not in title
new_title = title + " " + ADD
folded = "\n".join(textwrap.wrap(new_title, width=112, initial_indent=" " * 6, subsequent_indent=" " * 6,
                                 break_long_words=False, break_on_hyphens=False)) + "\n"
nblk = blk[:m.start(2)] + folded + blk[m.end(2):]
s = s[:i + 1] + nblk + s[j + 1:]
assert s != orig
import yaml
d = yaml.safe_load(s)
rec = None
for k, v in (d or {}).items():
    if isinstance(v, list):
        for r in v:
            if isinstance(r, dict) and r.get("id") == "S-74": rec = r
assert rec and rec.get("status") == "OPEN" and rec["title"].endswith(ADD), rec
open(REG, "w", encoding="utf-8").write(s)
print("apply_registry: S-74's title carries the w4r sentence (S-74 stays OPEN)")
