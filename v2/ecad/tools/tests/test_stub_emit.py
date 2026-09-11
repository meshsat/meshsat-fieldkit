#!/usr/bin/env python3
"""The stub router's path emission, which decides whether its closure is accepted at all.

12 September 2026. `emit()` merged straight runs by comparing the vector of the run SO FAR against the next
step: after one merge the run was two cells long and the step one, the test failed, and it appended. A straight
twenty-cell run came out as TEN segments instead of one.

Board E's last open was a 196 mm run between `J_BLK` pad 9 and `R29` pad 2 (the board is 267 mm wide and its two
inner layers carry no routed track, so the pair crosses it on F.Cu and B.Cu). The stub router found the path
every time and emitted it as 992 tracks; `stub_accept.py` refused that at its 400-item cap as "carpeting, not a
closure", and E stayed one open short through three router rounds. **The path was always fine. The emission was
not**, and no gate could see the difference because both look like a thousand items.

The merge is transcribed here rather than imported because `stub_router.py` needs pcbnew at module level. The
rule underneath keeps the transcription honest: it fails if the source stops carrying a run direction.
"""
import os, re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _merge(path):
    segs = []; cur = [path[0]]; run = None
    for k in range(1, len(path)):
        a, c = path[k - 1], path[k]
        if a[0] != c[0]:
            segs.append(("trk", cur)); segs.append(("via", c)); cur = [c]; run = None; continue
        step = (c[1] - a[1], c[2] - a[2])
        if step == (0, 0): continue
        if step == run: cur[-1] = c
        else: cur.append(c); run = step
    segs.append(("trk", cur))
    return sum(max(0, len(v) - 1) for kind, v in segs if kind == "trk"), sum(1 for k, _ in segs if k == "via")


def t_a_straight_run_is_one_segment():
    nt, _ = _merge([(0, 0, j) for j in range(21)])
    assert nt == 1, "a straight 20-cell run emitted %d segments" % nt


def t_a_staircase_is_one_segment_per_step():
    nt, _ = _merge([(0, 0, 0)] + [(0, j % 2, j) for j in range(1, 21)])
    assert nt == 20, nt


def t_two_legs_are_two_segments():
    nt, _ = _merge([(0, 0, j) for j in range(11)] + [(0, i, 10) for i in range(1, 11)])
    assert nt == 2, nt


def t_a_via_ends_the_run_whatever_its_direction():
    nt, nv = _merge([(0, 0, j) for j in range(6)] + [(1, 0, 5)] + [(1, 0, j) for j in range(6, 11)])
    assert (nt, nv) == (2, 1), (nt, nv)


def t_a_long_closure_stays_under_the_acceptance_cap():
    """The measured case: a 2,178-cell path of long straight legs. At ten segments per straight run it was 992
    tracks against stub_accept's 400-item cap; it has to come out in the tens."""
    path = []
    for leg in range(20):                       # twenty straight legs of about a hundred cells each
        for j in range(100):
            path.append((0, leg, leg * 100 + j) if leg % 2 == 0 else (0, leg, (leg + 1) * 100 - j))
        path.append((0, leg + 1, path[-1][2]))
    nt, _ = _merge(path)
    assert nt < 400, "a 2000-cell closure still emits %d items, over stub_accept's cap" % nt
    assert nt < 100, "a closure of twenty straight legs should be a few tens of segments, not %d" % nt


def t_the_source_carries_a_run_direction():
    """The transcription above is only worth anything while the source works the same way."""
    src = open(os.path.join(TOOLS, "stub_router.py"), errors="replace").read()
    i = src.index("def emit(")
    body = src[i:src.index("\nclosed = ", i)]
    assert "run = None" in body and "step == run" in body, \
        "emit() no longer carries a run direction; it merged one step at a time before it did"
