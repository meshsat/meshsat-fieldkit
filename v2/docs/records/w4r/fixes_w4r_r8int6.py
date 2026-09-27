#!/usr/bin/env python3
"""r8int6 (the integrator of set 6 of the handover, 27 September 2026): two corrections the independent check of stream
w4r asked for (w4r check 1, minors), applied at integration after the stream's own drafts. Idempotent by marker.

1. The coverage map's INT-001 row: `_verdict_by_board_why` gains the reversal of the TOOL change (block_contract.py reads
   board A's netlist, not its board file), which the check found explained but without a written way back.
2. S-74's title gains what the reading's check 5 judges and what it does not, so E5's regeneration for EQ-16 names its
   T_VR targets as board A's J_VR net (VIN_RAW) and does not read a T_VN target as judged.

Usage: fixes_w4r_r8int6.py <tree root holding v2/ecad>"""
import os, re, sys, textwrap
import yaml

ROOT = sys.argv[1]
COV = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_rules_coverage.yaml")
REG = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_requirements.yaml")

# 1. the reversal of the tool change
s = open(COV, encoding="utf-8").read(); o = s
MARK1 = "Reverse the TOOL change (r8int6, from the independent check)"
if MARK1 not in s:
    old = 'Reverse by deleting verdict_by_board, which puts E5\n     back on the set verdict and UNBOUND.",'
    assert s.count(old) == 1, "fixes_w4r: the _verdict_by_board_why ending is not there exactly once (%d)" % s.count(old)
    new = ('Reverse by deleting verdict_by_board, which puts E5\n     back on the set verdict and UNBOUND. '
           + MARK1 + ': restore block_contract.py\'s read of board A\'s board file\n'
           '     in place of its declared-phase netlist and the J_DOCK land; the reading then records board A\'s layout and can bind\n'
           '     only once that layout is the candidate\'s (rules_status reads it OTHER_BOARD until then).",')
    s = s.replace(old, new); assert s != o
    d = yaml.safe_load(s)
    why = d["coverage"]["INT-001"]["_verdict_by_board_why"]
    assert MARK1 in why and why.endswith("until then)."), why[-160:]
    open(COV, "w", encoding="utf-8").write(s)
    print("fixes_w4r: INT-001's _verdict_by_board_why carries the tool change's reversal")
else:
    print("fixes_w4r: INT-001's reversal already present")

# 2. S-74: what check 5 judges
t = open(REG, encoding="utf-8").read(); o = t
MARK2 = "The reading's check 5 judges a T_VR target's net against board A's J_VR net"
if MARK2 not in t:
    assert t.count("\n  - id: S-74\n") == 1
    i = t.find("\n  - id: S-74\n"); j = t.find("\n  - id: ", i + 1)
    blk = t[i + 1:j + 1]
    m = re.search(r"(    title: >-\n)((?:      .*\n)+)", blk)
    assert m, "fixes_w4r: S-74 carries no folded title"
    title = " ".join(m.group(2).split())
    assert "Since stream w4r (27 September 2026)" in title, "fixes_w4r: apply the stream's apply_registry.py first"
    ADD = (MARK2 + " name (VIN_RAW), counts the targets of each power kind (CP, CN, PRE, VR, VN) and judges neither a "
           "T_VN target's net nor any power target's position (r8int6, from the independent check of w4r), so E5's "
           "regeneration names its T_VR targets VIN_RAW, and a T_VN target on a wrong net would still pass until a "
           "declared return net is judged.")
    folded = "\n".join(textwrap.wrap(title + " " + ADD, width=112, initial_indent=" " * 6, subsequent_indent=" " * 6,
                                     break_long_words=False, break_on_hyphens=False)) + "\n"
    blk2 = blk[:m.start(2)] + folded + blk[m.end(2):]
    t = t[:i + 1] + blk2 + t[j + 1:]
    assert t != o
    d = yaml.safe_load(t)
    rec = [r for v in d.values() if isinstance(v, list) for r in v if isinstance(r, dict) and r.get("id") == "S-74"][0]
    assert rec["status"] == "OPEN" and rec["title"].endswith(ADD)
    open(REG, "w", encoding="utf-8").write(t)
    print("fixes_w4r: S-74's title says what check 5 judges")
else:
    print("fixes_w4r: S-74 already carries the check-5 sentence")
