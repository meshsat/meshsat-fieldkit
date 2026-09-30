#!/usr/bin/env python3
"""Adds this folder's row to the worktrees table of v2/docs/records/README.md, after layer 3's L3-R2 row (MESHSAT-1357,
30 September 2026). Asserts the anchor row once and refuses a second run. Run: python3 <this file>."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = os.path.join(TOP, "v2/docs/records/README.md")
ROW = ("| `scrub/` | the public-file scrub (30 September 2026, branch `fnd/scrub` from `8fec0733`, on the owner's instruction "
       "of 29 September 2026): the runner's paths, session scratch paths and host names replaced by neutral tokens or "
       "derived in 57 files, the files left with the reason, the four snapshots reissued as H1-R1, H1.1-R1, H2-R1 and "
       "H3-R1 beside the ones they supersede, the guard `test_public_hygiene.py`, and `MAP.md`, every replacement by "
       "file, line and token class; history not rewritten |")

t = open(P, encoding="utf-8").read()
if "| `scrub/` |" in t: sys.exit("apply_index_row: REFUSED: the row is there already")
lines = t.split("\n")
at = [i for i, l in enumerate(lines) if l.startswith("| `l3r2/` |")]
if len(at) != 1: sys.exit("apply_index_row: REFUSED: the anchor row is there %d time(s)" % len(at))
lines.insert(at[0] + 1, ROW)
new = "\n".join(lines)
assert new != t
open(P, "w", encoding="utf-8").write(new)
print("apply_index_row: the scrub/ row added after line %d" % (at[0] + 1))
