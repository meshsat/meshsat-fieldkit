#!/usr/bin/env python3
"""Order the pairs by how contested their planned corridor is (12 September 2026, MESHSAT-862; appendix 32.137).

Plan mode searches every pair's corridor while laying nothing, so no pair takes room from another, and on B19
110 of 113 pairs come back with a corridor for every section. The greedy pass then lays 8 of 48 in the DIFF100
class, which means the corridors exist and forty pairs lose the room to a neighbour. This turns that map into an
order: the pass is greedy and never rips up, so whichever pair goes first takes the room, and the pair with the
least freedom should be the one that gets it.

Two rankings, because the right one is a measurement and not an opinion:
  contended  a pair's score is the contention of the cells its own corridor wants (sum of how many OTHER pairs
             wanted each of them), highest first: the pair fighting hardest for its room goes before the pairs
             that can go round.
  scarce     the same number divided by the corridor's length, highest first: a short corridor through a
             contested field has nowhere else to go, while a long one has alternatives.

Usage: pair_order_from_plan.py <plan.json> <conflict.npz> [contended|scarce] > order.txt
"""
import json, sys
import numpy as np

plan = json.load(open(sys.argv[1]))
z = np.load(sys.argv[2])
mode = sys.argv[3] if len(sys.argv) > 3 else "contended"

# the conflict file is a sparse list of cells wanted by more than one pair: L, i, j and v = how many MORE than one
contention = {}
for L, i, j, v in zip(z["L"].tolist(), z["i"].tolist(), z["j"].tolist(), z["v"].tolist()):
    contention[(L, i, j)] = v

rows = []
for stem, sections in plan.items():
    cells = [tuple(c) for sec in (sections or []) for c in (sec or [])]
    if not cells: continue
    score = sum(contention.get((c[0], c[1], c[2]), 0) for c in cells)
    rows.append((stem, score, len(cells)))

if mode == "scarce": rows.sort(key=lambda r: (-(r[1] / max(r[2], 1)), r[0]))
else: rows.sort(key=lambda r: (-r[1], r[0]))

for stem, score, n in rows: print(stem)
print("# %s: %d pairs, most contested %s (%d over %d cells), least %s (%d)"
      % (mode, len(rows), rows[0][0], rows[0][1], rows[0][2], rows[-1][0], rows[-1][1]), file=sys.stderr)
