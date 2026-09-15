# Extracted from pair_preroute.py on 15 September 2026 (red team round four C3: the split at measurable boundaries),
# behaviour-preserving: every name here is re-exported into pair_preroute's namespace by a star import, and the
# module-level lists and dicts (budgets, timers, caches, epochs) stay the SAME objects, so a function that mutates
# them from any module mutates the one the pass reads. Proved on the box by the pre-router laying the same pairs to
# the same board md5 on D and B before and after (tools/knob_measure).
"""search"""
import sys, os, re, math, json, heapq, time, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import netclass
import pcbnew, numpy as np
try:
    from matplotlib.path import Path as _PATH   # the vectorised point-in-polygon test; without it the SWIG loop below is used
except Exception:
    _PATH = None
from pcbnew import VECTOR2I, FromMM
import pairsearch
from .config import *
from .occupancy import *

def astar(gr, layers, trk, via, start, goal, window, behind=(), cost=None):
    """cost: {layer index: float raster} added to every step, the negotiated-congestion term of pair_negotiate.py (10 Sep 2026).

    behind: [(x, y, ux, uy), ...] (mm): cells within 2.5 mm of (x, y) on the side against (ux, uy) are blocked, so a corridor leaves an entry end outward."""
    LI = {L: i for i, L in enumerate(layers)}
    (jmin, imin), (jmax, imax) = window
    passable = {LI[L]: ~trk[L] for L in layers}
    sL, sj, si = start; gL, gj, gi = goal
    # 9 Sep 2026 (A24 USB_E6, appendix 32.83): the behind mask blocks a 2.5 mm half disc behind each entry station so a
    # corridor leaves outward instead of diving back under the connector. It was also walling in the very cell free_end
    # chose to start from: A's mezzanine-to-dock pair died after SIXTEEN expansions, which reads as a congested board and
    # is a pocket of the tool's own making. The ends keep the 0.6 mm block free_end measured; the rest of the half disc
    # stays blocked, so the rule still does its work.
    _r0 = max(1, int(0.6 / gr.G))
    _keep = {(L, e): passable[L][max(0, ii0 - _r0):ii0 + _r0 + 1, max(0, jj0 - _r0):jj0 + _r0 + 1].copy()
             for L in passable for e, (jj0, ii0) in (("s", (sj, si)), ("g", (gj, gi)))}
    for (bx, by, ux, uy) in behind:
        jc, ic = gr.cell(bx, by); r = int(2.5 / gr.G)
        for ii in range(max(0, ic - r), min(gr.NY, ic + r + 1)):
            for jj in range(max(0, jc - r), min(gr.NX, jc + r + 1)):
                x_, y_ = gr.xy(jj, ii)
                if (x_ - bx) * ux + (y_ - by) * uy < -0.05 and math.hypot(x_ - bx, y_ - by) <= 2.5:
                    for L in passable: passable[L][ii, jj] = False
    for L in passable:
        for e, (jj0, ii0) in (("s", (sj, si)), ("g", (gj, gi))):
            passable[L][max(0, ii0 - _r0):ii0 + _r0 + 1, max(0, jj0 - _r0):jj0 + _r0 + 1] = _keep[(L, e)]
    # the ends are the cells free_end chose: free on at least one layer; the path starts and ends only on layers where they are free (8 Sep: forcing
    # them passable on every layer let a path start on In2 inside a resistor's clearance and the legs hit at the first cell)
    # 10 September 2026 (plan stage 5): the loop that was here is `pairsearch.search`, which takes only arrays and returns the
    # same path. Two reasons. It can be compiled: with numba the same algorithm runs at 2.27 million expansions a second against
    # 26 thousand, so a pair's 12,000,000 budget costs seconds rather than eight minutes, which is what makes the tens of
    # iterations of a negotiated router affordable at all. And it can be TESTED: `pairsearch.py selftest` runs the array kernel,
    # the compiled kernel and a faithful copy of the heapq original on random maps and refuses any difference.
    (jmin, imin), (jmax, imax) = window
    H, W = imax - imin + 1, jmax - jmin + 1
    nL = len(layers)
    P = np.empty((nL, H, W), dtype=bool)
    for L in range(nL): P[L] = passable[L][imin:imax + 1, jmin:jmax + 1]
    VB = np.ascontiguousarray(via[imin:imax + 1, jmin:jmax + 1])
    C = None
    if cost is not None:
        C = np.empty((nL, H, W), dtype=np.float64)
        for L in range(nL): C[L] = cost[L][imin:imax + 1, jmin:jmax + 1]
    start_layers = [LI[sL]] if sL in LI else list(range(nL))
    starts = [(L, si - imin, sj - jmin) for L in start_layers
              if imin <= si <= imax and jmin <= sj <= jmax and passable[L][si, sj]]
    if not starts:
        PATH_WHY[0] = "the start cell is passable on no allowed layer"   # 9 Sep 2026 (D10 USB3): the search never began
        return None
    budget = 6000000
    if PAIR_EXPANSIONS: budget = min(budget, max(1, PAIR_EXPANSIONS - PAIR_SPENT[0]))
    # The clock is checked BETWEEN searches now, not inside one. A budget that decides a result must be counted in work
    # (appendix 32.90), and the expansion cap is the reproducible one; PAIR_BUDGET stays the outer safety net.
    if PAIR_DEADLINE[0] and time.time() > PAIR_DEADLINE[0]:
        PATH_WHY[0] = "the pair's time budget ran out (PAIR_BUDGET %.0f s)" % PAIR_BUDGET
        return None
    goal = (LI[gL] if gL in LI else -1, gi - imin, gj - jmin)
    cells, n, why = pairsearch.search(P, VB, C, starts, goal, VIA_COST, budget, fast=_FAST_SEARCH)
    PAIR_SPENT[0] += n; PAIR_TOTAL[0] += n
    if cells is None:
        # 9 Sep 2026 (A24 USB_E6 spans 189 mm; appendix 32.83): a corridor that cannot be found must say WHY. Three
        # different failures used to return the same None: the search never began, it ran out of its node budget, or
        # the map really has no path. Only the third is a placement question.
        if why == "capped" and PAIR_EXPANSIONS and PAIR_SPENT[0] >= PAIR_EXPANSIONS:
            PATH_WHY[0] = "the pair's expansion budget ran out (PAIR_EXPANSIONS %d)" % PAIR_EXPANSIONS
        elif why == "capped": PATH_WHY[0] = "the node budget of 6,000,000 ran out after %d expansions" % n
        else: PATH_WHY[0] = "no path on the map after %d expansions" % n
        return None
    PATH_WHY[0] = ""
    return [(L, i + imin, j + jmin) for (L, i, j) in cells]




# ---------------------------------------------------------------- where the seconds go (10 September 2026, MESHSAT-862)
# The profile that motivated the fast rasteriser (270 of 330 seconds in Grid.poly) had to be taken with cProfile on a copy of
# the board. Every arm needs that number, so the tool keeps it itself: one accumulator per phase, one line at the end of the
# pass. It costs a time.time() per call of two functions and it is what says whether the next change belongs in the maps or
# in the search.
_T = {"maps": 0.0, "astar": 0.0, "stubs": 0.0, "legs": 0.0, "stamp": 0.0}
_N = {k: 0 for k in _T}   # calls per bucket: seconds alone cannot say whether a bucket is many cheap calls or few dear ones
def _timed(name, fn):
    def w(*a, **k):
        t0 = time.time()
        try: return fn(*a, **k)
        finally:
            _T[name] += time.time() - t0; _N[name] += 1
    w.__name__ = fn.__name__; w.__doc__ = fn.__doc__; return w
build_maps = _timed("maps", build_maps)
astar = _timed("astar", astar)

def smooth(gr, pts_cells, passable, cap=None):
    """Greedy line-of-sight simplification of a run's cells [(i, j)...] on one layer: keep the farthest point (at most `cap` cells away) reachable
    by a straight segment whose samples (four per cell) all stay passable (the 8-direction grid path zigzags at cell scale, and offsetting a zigzag
    makes the legs cross)."""
    if len(pts_cells) <= 2: return list(pts_cells)
    def clear(a, b):
        (i0, j0), (i1, j1) = a, b; n = max(abs(i1 - i0), abs(j1 - j0)) * 4 + 1
        for k in range(n + 1):
            u = k / n; i = int(round(i0 + u * (i1 - i0))); j = int(round(j0 + u * (j1 - j0)))
            if not passable[i, j]: return False
        return True
    out = [pts_cells[0]]; k = 0
    while k < len(pts_cells) - 1:
        m = len(pts_cells) - 1 if cap is None else min(len(pts_cells) - 1, k + cap)
        while m > k + 1 and not clear(pts_cells[k], pts_cells[m]): m -= 1
        out.append(pts_cells[m]); k = m
    return out

def stub_path(gr, passable, start_xy, goal_xy, window):
    """A short A* for one track from start to goal (mm) on one layer's passable map; returns [(x, y)...] smoothed, or None."""
    sj, si = gr.cell(*start_xy); gj, gi = gr.cell(*goal_xy)
    # 9 Sep 2026 (B18 CARD1_CLK, D10 USB3; appendix 32.83): freeing ONE cell at each end is not enough. Both ends of a stub
    # lie on the net's OWN copper (the corridor end at one side, the escape via at the other), so every neighbour of that cell
    # is inside that copper's own clearance disc and the search cannot take a first step: the eight-neighbour loop finds
    # nothing passable and the stub is reported as "no stub path at the via" with a goal the map itself calls free. The
    # 0.2 mm disc at each end is same-net copper by construction; anything it wrongly opens is a hard violation the
    # pre-route DRC gate reads before the router is ever started.
    for (jj, ii) in ((sj, si), (gj, gi)):
        for di in range(-2, 3):
            for dj in range(-2, 3):
                if di * di + dj * dj > 5: continue
                a_, c_ = ii + di, jj + dj
                if 0 <= a_ < passable.shape[0] and 0 <= c_ < passable.shape[1]: passable[a_, c_] = True
    (jmin, imin), (jmax, imax) = window
    # 11 September 2026: this search is the pass. Profiled on D, which lays 5 of 5 pairs in 9 seconds: 6 of those
    # seconds are here, over 75 calls, against 2 in the occupancy maps and 0 in the corridor search (appendix
    # 32.127). The corridor search was extracted to `pairsearch.py` and compiled on 10 September, 13.5x, and this
    # one was left in interpreted Python doing almost the same thing on almost the same map. It does not need a new
    # kernel: a single-layer search IS `pairsearch.search` with nL=1, no via layer and the window as the array, and
    # that kernel is proved against its own reference by `pairsearch.py selftest`. PAIR_FAST_STUBS=1 takes it.
    # Measured on two boards and ON where numba is: B19 lays the same 47 of 113 with the pass at 976 s against
    # 1586 and the stub search at 46 s against 675, and the two boards differ in 0 of 7,706 items.
    if _FAST_STUBS:
        wi0, wi1 = max(0, imin), min(passable.shape[0] - 1, imax)
        wj0, wj1 = max(0, jmin), min(passable.shape[1] - 1, jmax)
        if not (wi0 <= si <= wi1 and wj0 <= sj <= wj1 and wi0 <= gi <= wi1 and wj0 <= gj <= wj1): return None
        win = np.ascontiguousarray(passable[wi0:wi1 + 1, wj0:wj1 + 1])[None, :, :]
        novia = np.ones(win.shape[1:], dtype=bool)   # every cell forbids a via: one layer, no layer change exists
        path_, nexp_, _why_ = pairsearch.search(win, novia, None, [(0, si - wi0, sj - wj0)], (0, gi - wi0, gj - wj0),
                                                max_exp=STUB_EXPANSIONS, fast=_FAST_SEARCH)
        PAIR_SPENT[0] += nexp_; PAIR_TOTAL[0] += nexp_
        if path_ is None: return None
        cells_ = [(i_ + wi0, j_ + wj0) for (_L, i_, j_) in path_]
        cells_ = smooth(gr, cells_, passable)
        pts_ = [gr.xy(j, i) for i, j in cells_]
        if pts_: pts_[0] = start_xy
        return pts_
    dist = {(si, sj): 0.0}; prev = {}; pq = [(0.0, 0.0, (si, sj))]; found = None; n = 0
    steps = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]
    while pq:
        f, d0, (i, j) = heapq.heappop(pq)
        if d0 > dist.get((i, j), 1e18): continue
        if (i, j) == (gi, gj): found = (i, j); break
        n += 1
        if n > STUB_EXPANSIONS: break
        if not n % 4096:
            PAIR_SPENT[0] += 4096; PAIR_TOTAL[0] += 4096
            if PAIR_EXPANSIONS and PAIR_SPENT[0] > PAIR_EXPANSIONS:
                PATH_WHY[0] = "the pair's expansion budget ran out (PAIR_EXPANSIONS %d)" % PAIR_EXPANSIONS; break
            if PAIR_DEADLINE[0] and time.time() > PAIR_DEADLINE[0]:
                PATH_WHY[0] = "the pair's time budget ran out (PAIR_BUDGET %.0f s)" % PAIR_BUDGET; break
        for di, dj, c in steps:
            ni, nj = i + di, j + dj
            if not (imin <= ni <= imax and jmin <= nj <= jmax) or not passable[ni, nj]: continue
            if di and dj and not (passable[i, nj] and passable[ni, j]): continue
            nd = d0 + c
            # sqrt of an exact integer sum, never hypot: the compiled kernel does the same and an ulp of
            # difference would reorder two entries of equal true distance (pairsearch.py, round-two H1).
            if nd < dist.get((ni, nj), 1e18): dist[(ni, nj)] = nd; prev[(ni, nj)] = (i, j); heapq.heappush(pq, (nd + math.sqrt(float((ni - gi) * (ni - gi) + (nj - gj) * (nj - gj))), nd, (ni, nj)))
    if found is None: return None
    path = [found]
    while path[-1] in prev: path.append(prev[path[-1]])
    path.reverse(); cells = smooth(gr, path, passable)
    pts_ = [gr.xy(j, i) for i, j in cells]
    if pts_: pts_[0] = start_xy   # the exact start (the grid snap pulled the two legs' hop starts within the clearance)
    return pts_

def simplify(path):
    """[(layer index, i, j)] -> runs [(L, [(x,y)...])] with collinear points merged, split at vias."""
    runs = []; cur = [path[0]]
    for k in range(1, len(path)):
        a, c = path[k - 1], path[k]
        if a[0] != c[0]: runs.append(cur); cur = [c]; continue
        if len(cur) >= 2:
            p0, p1 = cur[-2], cur[-1]
            if (p1[1] - p0[1], p1[2] - p0[2]) == (c[1] - p1[1], c[2] - p1[2]): cur[-1] = c; continue
        cur.append(c)
    runs.append(cur); return runs


# the timed wrappers rebind the searches once they exist; they sat past the geometry anchor in the first split and
# raised a NameError at import (A36's pre-route, 15 September 2026 21:55 CEST)
stub_path = _timed("stubs", stub_path)
Grid.seg = _timed("stamp", Grid.seg)
Grid.disc = _timed("stamp", Grid.disc)

__all__ = [_n for _n in dir() if not _n.startswith("__")]
