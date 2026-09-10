#!/usr/bin/env python3
"""The pre-router's corridor search, as a pure function of arrays (MESHSAT-862, 10 September 2026; plan stage 5).

`pair_preroute.py` had the A* inside `main()`'s closure, reading KiCad objects and a Grid, so it could be neither tested on its
own nor compiled. Here it takes only numpy arrays in WINDOW coordinates and returns a path in the same coordinates:

    passable  (nL, H, W) bool   a cell a centreline may occupy on that layer
    viablock  (H, W)     bool   a cell where a via may NOT be placed (the pre-router's `via` map is the forbidden set)
    cost      (nL, H, W) float32 or None    added to every step, the negotiated-congestion term
    starts    [(L, i, j), ...]  every start cell, all at distance 0
    goal      (L, i, j)         L = -1 means any layer
    -> (path, expansions, why)  path = [(L, i, j), ...] or None; why = "" | "capped" | "empty" | "nopath"

Two implementations, and they are the same algorithm: `_run_py` in plain Python and `_run_nb` under numba's njit when numba
imports (it is not in the KiCad python on the box; `python3 -m venv --system-site-packages` plus `pip install numba` gives one
that has both). Both use the same binary heap over the same key `(f, d, state)` with `state = (L * H + i) * W + j`, which orders
exactly as the tuple `(L, i, j)` heapq used to compare, so the two return byte-identical paths and the fast one is not a new
router. `selftest` proves it on random maps.

The heuristic is `math.sqrt` of an EXACT integer sum, never `math.hypot` (round-two red teams, H1). A sum of two squared
integer cell offsets is exact in a float and `sqrt` is correctly rounded on every platform, while `hypot` is not required to
be, so CPython and the compiled kernel could differ by an ulp and reorder two entries of equal true distance. The paths
agreed even before this, for a reason worth stating rather than relying on: the possible predecessors of a cell differ from
it by at most one in each axis, so an ulp can only reorder nodes far apart in the heap and can never change which neighbour
wins a `prev`. With the sum exact, the equivalence argument no longer rests on that lemma.

The wall-clock budget is NOT checked inside the search any more: the kernel stops on expansions, which is reproducible, and the
caller looks at the clock between searches. The record's own rule (appendix 32.90: a budget that decides a result must be counted
in work, not in time) is why.

Usage: pairsearch.py selftest [N]"""
import sys, os, math
import numpy as np

VIA_COST_DEFAULT = 12.0

try:
    if os.environ.get("PAIR_NO_NUMBA") == "1": raise ImportError("PAIR_NO_NUMBA=1")
    from numba import njit
    HAVE_NUMBA = True
except Exception:
    HAVE_NUMBA = False
    def njit(*a, **k):   # so the source below is one text whether or not numba is here
        def d(f): return f
        return d if not a or not callable(a[0]) else a[0]


def _kernel(passable, viablock, cost, use_cost, starts_L, starts_i, starts_j, gL, gi, gj, via_cost, max_exp):
    """A* over (layer, i, j). Heap arrays grow by doubling; `dist` is float64 and `prev` int32 over the whole window."""
    nL, H, W = passable.shape
    N = nL * H * W
    dist = np.full(N, 1e18, dtype=np.float64)
    prev = np.full(N, -1, dtype=np.int32)
    cap = 1024
    hf = np.empty(cap, dtype=np.float64); hd = np.empty(cap, dtype=np.float64); hs = np.empty(cap, dtype=np.int64)
    hn = 0

    for k in range(starts_L.shape[0]):
        L = starts_L[k]; i = starts_i[k]; j = starts_j[k]
        if not passable[L, i, j]: continue
        s = (L * H + i) * W + j
        if dist[s] <= 0.0: continue
        dist[s] = 0.0
        f = math.sqrt(float((i - gi) * (i - gi) + (j - gj) * (j - gj)))
        if hn >= cap:
            cap *= 2
            nf = np.empty(cap, dtype=np.float64); nd = np.empty(cap, dtype=np.float64); ns = np.empty(cap, dtype=np.int64)
            nf[:hn] = hf[:hn]; nd[:hn] = hd[:hn]; ns[:hn] = hs[:hn]; hf = nf; hd = nd; hs = ns
        hf[hn] = f; hd[hn] = 0.0; hs[hn] = s; hn += 1
        c = hn - 1                                  # sift up
        while c > 0:
            p = (c - 1) // 2
            if hf[c] < hf[p] or (hf[c] == hf[p] and (hd[c] < hd[p] or (hd[c] == hd[p] and hs[c] < hs[p]))):
                hf[c], hf[p] = hf[p], hf[c]; hd[c], hd[p] = hd[p], hd[c]; hs[c], hs[p] = hs[p], hs[c]; c = p
            else: break

    di8 = np.array([-1, 1, 0, 0, -1, -1, 1, 1], dtype=np.int64)
    dj8 = np.array([0, 0, -1, 1, -1, 1, -1, 1], dtype=np.int64)
    dc8 = np.array([1.0, 1.0, 1.0, 1.0, 1.414, 1.414, 1.414, 1.414], dtype=np.float64)

    n = 0; found = -1; capped = False
    while hn > 0:
        f = hf[0]; d = hd[0]; s = hs[0]                                   # pop
        hn -= 1
        if hn > 0:
            hf[0] = hf[hn]; hd[0] = hd[hn]; hs[0] = hs[hn]
            p = 0
            while True:                                                    # sift down
                l = 2 * p + 1; r = l + 1; m = p
                if l < hn and (hf[l] < hf[m] or (hf[l] == hf[m] and (hd[l] < hd[m] or (hd[l] == hd[m] and hs[l] < hs[m])))): m = l
                if r < hn and (hf[r] < hf[m] or (hf[r] == hf[m] and (hd[r] < hd[m] or (hd[r] == hd[m] and hs[r] < hs[m])))): m = r
                if m == p: break
                hf[m], hf[p] = hf[p], hf[m]; hd[m], hd[p] = hd[p], hd[m]; hs[m], hs[p] = hs[p], hs[m]; p = m
        if d > dist[s]: continue
        L = s // (H * W); rem = s - L * H * W; i = rem // W; j = rem - i * W
        n += 1
        if i == gi and j == gj and (gL < 0 or L == gL):
            found = s; break
        if n > max_exp:
            capped = True; break
        for k in range(8):
            ni = i + di8[k]; nj = j + dj8[k]
            if ni < 0 or ni >= H or nj < 0 or nj >= W: continue
            if not passable[L, ni, nj]: continue
            if di8[k] != 0 and dj8[k] != 0 and not (passable[L, i, nj] and passable[L, ni, j]): continue
            nd_ = d + dc8[k]
            if use_cost: nd_ += cost[L, ni, nj]
            t = (L * H + ni) * W + nj
            if nd_ < dist[t]:
                dist[t] = nd_; prev[t] = s
                ff = nd_ + math.sqrt(float((ni - gi) * (ni - gi) + (nj - gj) * (nj - gj)))
                if hn >= cap:
                    cap *= 2
                    nf2 = np.empty(cap, dtype=np.float64); nd2 = np.empty(cap, dtype=np.float64); ns2 = np.empty(cap, dtype=np.int64)
                    nf2[:hn] = hf[:hn]; nd2[:hn] = hd[:hn]; ns2[:hn] = hs[:hn]; hf = nf2; hd = nd2; hs = ns2
                hf[hn] = ff; hd[hn] = nd_; hs[hn] = t; hn += 1
                c = hn - 1
                while c > 0:
                    p = (c - 1) // 2
                    if hf[c] < hf[p] or (hf[c] == hf[p] and (hd[c] < hd[p] or (hd[c] == hd[p] and hs[c] < hs[p]))):
                        hf[c], hf[p] = hf[p], hf[c]; hd[c], hd[p] = hd[p], hd[c]; hs[c], hs[p] = hs[p], hs[c]; c = p
                    else: break
        if not viablock[i, j]:
            for oL in range(nL):
                if oL == L or not passable[oL, i, j]: continue
                nd_ = d + via_cost
                if use_cost: nd_ += cost[oL, i, j]
                t = (oL * H + i) * W + j
                if nd_ < dist[t]:
                    dist[t] = nd_; prev[t] = s
                    ff = nd_ + math.sqrt(float((i - gi) * (i - gi) + (j - gj) * (j - gj)))
                    if hn >= cap:
                        cap *= 2
                        nf3 = np.empty(cap, dtype=np.float64); nd3 = np.empty(cap, dtype=np.float64); ns3 = np.empty(cap, dtype=np.int64)
                        nf3[:hn] = hf[:hn]; nd3[:hn] = hd[:hn]; ns3[:hn] = hs[:hn]; hf = nf3; hd = nd3; hs = ns3
                    hf[hn] = ff; hd[hn] = nd_; hs[hn] = t; hn += 1
                    c = hn - 1
                    while c > 0:
                        p = (c - 1) // 2
                        if hf[c] < hf[p] or (hf[c] == hf[p] and (hd[c] < hd[p] or (hd[c] == hd[p] and hs[c] < hs[p]))):
                            hf[c], hf[p] = hf[p], hf[c]; hd[c], hd[p] = hd[p], hd[c]; hs[c], hs[p] = hs[p], hs[c]; c = p
                        else: break
    return found, prev, n, capped


_run_py = _kernel
_run_nb = njit(cache=True)(_kernel) if HAVE_NUMBA else None


def search(passable, viablock, cost, starts, goal, via_cost=VIA_COST_DEFAULT, max_exp=6000000, fast=True, kernel=False):
    """The corridor search. Arrays are window-local; see the module docstring. Returns (path, expansions, why).

    Three implementations, one result. Compiled when numba is here; otherwise the heapq original, because the array kernel in
    plain Python is 5.2x SLOWER than heapq (measured: 48,575 expansions a second against 253,134) and a fallback must not be a
    regression. `kernel=True` forces the array kernel itself, which is what the selftest compares."""
    nL, H, W = passable.shape
    gL, gi, gj = goal
    if not starts: return None, 0, "empty"
    if not kernel and not (fast and _run_nb is not None):
        return astar_ref(passable, viablock, cost, starts, goal, via_cost, max_exp)
    sL = np.array([s[0] for s in starts], dtype=np.int64)
    si = np.array([s[1] for s in starts], dtype=np.int64)
    sj = np.array([s[2] for s in starts], dtype=np.int64)
    use_cost = cost is not None
    if not use_cost: cost = np.zeros((1, 1, 1), dtype=np.float64)
    passable = np.ascontiguousarray(passable, dtype=np.bool_)
    viablock = np.ascontiguousarray(viablock, dtype=np.bool_)
    cost = np.ascontiguousarray(cost, dtype=np.float64)
    run = _run_nb if (fast and _run_nb is not None) else _run_py
    found, prev, n, capped = run(passable, viablock, cost, use_cost, sL, si, sj,
                                 int(gL), int(gi), int(gj), float(via_cost), int(max_exp))
    if found < 0: return None, n, ("capped" if capped else "nopath")
    path = []; s = int(found)
    while s >= 0:
        L = s // (H * W); rem = s - L * H * W; i = rem // W
        path.append((int(L), int(i), int(rem - i * W)))
        s = int(prev[s])
    path.reverse()
    return path, n, ""



def astar_ref(passable, viablock, cost, starts, goal, via_cost=VIA_COST_DEFAULT, max_exp=6000000):
    """`pair_preroute.astar` as it was written: heapq over `(f, d, (L, i, j))` tuples and dicts for dist and prev. It is here so
    the array kernel can be proved to be the same router rather than merely a plausible one; the selftest compares all three."""
    import heapq
    nL, H, W = passable.shape; gL, gi, gj = goal
    def h(i, j): return math.sqrt(float((i - gi) * (i - gi) + (j - gj) * (j - gj)))
    dist = {}; prev = {}; pq = []
    for (L, i, j) in starts:
        if not passable[L, i, j]: continue
        st = (L, i, j)
        if st in dist: continue
        dist[st] = 0.0; heapq.heappush(pq, (h(i, j), 0.0, st))
    steps = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]
    n = 0; found = None; capped = False
    while pq:
        f, d, st = heapq.heappop(pq)
        if d > dist.get(st, 1e18): continue
        L, i, j = st; n += 1
        if (i, j) == (gi, gj) and (gL < 0 or L == gL): found = st; break
        if n > max_exp: capped = True; break
        for di, dj, c in steps:
            ni, nj = i + di, j + dj
            if not (0 <= ni < H and 0 <= nj < W): continue
            if not passable[L, ni, nj]: continue
            if di and dj and not (passable[L, i, nj] and passable[L, ni, j]): continue
            nd = d + c + (cost[L, ni, nj] if cost is not None else 0.0); t = (L, ni, nj)
            if nd < dist.get(t, 1e18): dist[t] = nd; prev[t] = st; heapq.heappush(pq, (nd + h(ni, nj), nd, t))
        if not viablock[i, j]:
            for oL in range(nL):
                if oL == L or not passable[oL, i, j]: continue
                nd = d + via_cost + (cost[oL, i, j] if cost is not None else 0.0); t = (oL, i, j)
                if nd < dist.get(t, 1e18): dist[t] = nd; prev[t] = st; heapq.heappush(pq, (nd + h(i, j), nd, t))
    if found is None: return None, n, ("capped" if capped else "nopath")
    path = [found]
    while path[-1] in prev: path.append(prev[path[-1]])
    return list(reversed(path)), n, ""



def bench(nL=2, H=260, W=260, block=0.25, seed=3):
    """Expansions per second on one window-sized map, plain against compiled. The pre-router's window is 25 mm at 0.1 mm."""
    import time
    rng = np.random.default_rng(seed)
    passable = rng.random((nL, H, W)) > block
    viablock = rng.random((H, W)) > 0.6
    passable[:, 0, 0] = True; passable[:, H - 1, W - 1] = True
    starts = [(0, 0, 0)]; goal = (-1, H - 1, W - 1)
    out = []
    t0 = time.time(); pr, nr, wr = astar_ref(passable, viablock, None, starts, goal); dtr = time.time() - t0
    print("pairsearch: %-8s %7d expansions in %6.2f s = %8.0f/s, %s, %d cells" % ("heapq", nr, dtr, nr / max(dtr, 1e-9), wr or "path", len(pr or [])))
    for fast in (False, True):
        if fast and _run_nb is None: continue
        if fast: search(passable[:, :8, :8].copy(), viablock[:8, :8].copy(), None, [(0, 0, 0)], (-1, 7, 7), fast=True)   # compile first, do not time the compiler
        t0 = time.time(); path, n, why = search(passable, viablock, None, starts, goal, fast=fast, kernel=not fast); dt = time.time() - t0
        out.append((fast, n, dt, why, len(path or [])))
        print("pairsearch: %-8s %7d expansions in %6.2f s = %8.0f/s, %s, %d cells" % ("compiled" if fast else "plain", n, dt, n / max(dt, 1e-9), why or "path", len(path or [])))
    if len(out) == 2: print("pairsearch: the compiled search is %.1fx the plain kernel and %.1fx the heapq original" % (out[0][2] / max(out[1][2], 1e-9), dtr / max(out[1][2], 1e-9)))
    print("pairsearch: the plain kernel is %.2fx the heapq original" % (dtr / max(out[0][2], 1e-9)))
    return 0


def selftest(n=12, seed=7, verbose=True):
    """The fast kernel and the plain one must return the SAME path, or the fast one is a different router."""
    rng = np.random.default_rng(seed); bad = 0; ran = 0
    for t in range(n):
        H = int(rng.integers(20, 70)); W = int(rng.integers(20, 70)); nL = int(rng.integers(1, 4))
        passable = rng.random((nL, H, W)) > (0.15 + 0.2 * rng.random())
        viablock = rng.random((H, W)) > 0.7
        cost = (rng.random((nL, H, W)) * 3.0) if t % 2 else None
        s = [(int(rng.integers(0, nL)), int(rng.integers(0, H)), int(rng.integers(0, W))) for _ in range(int(rng.integers(1, 4)))]
        g = (int(rng.integers(-1, nL)), int(rng.integers(0, H)), int(rng.integers(0, W)))
        for (L, i, j) in s: passable[L, i, j] = True
        if g[0] >= 0: passable[g[0], g[1], g[2]] = True
        else: passable[:, g[1], g[2]] = True
        pa, na, wa = search(passable, viablock, cost, s, g, fast=False, kernel=True)
        pb, nb, wb = search(passable, viablock, cost, s, g, fast=True, kernel=False) if _run_nb is not None else (None, -1, "skip")
        pr, nr, wr = astar_ref(passable, viablock, cost, s, g)
        if _run_nb is None: pb, nb, wb = pa, na, wa
        ran += 1
        if (pa, na, wa) != (pb, nb, wb) or (pa, na, wa) != (pr, nr, wr):
            bad += 1
            if verbose: print("pairsearch: MISMATCH case %d: plain %s/%d/%d, fast %s/%d/%d, heapq %s/%d/%d"
                              % (t, wa, na, len(pa or []), wb, nb, len(pb or []), wr, nr, len(pr or [])))
        elif verbose and t < 3:
            print("pairsearch: case %d %dx%dx%d cost=%s -> %s, %d expansions, %d cells" % (t, nL, H, W, cost is not None, wa or "path", na, len(pa or [])))
    print("pairsearch: selftest %d of %d cases identical across the heapq original, the array kernel and the compiled one, numba %s" % (ran - bad, ran, "on" if (HAVE_NUMBA and _run_nb is not None) else "OFF (the plain kernel ran twice)"))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "selftest": sys.exit(selftest(int(a[1]) if len(a) > 1 else 12))
    if a and a[0] == "bench": sys.exit(bench(*[int(x) for x in a[1:]]))
    print(__doc__); sys.exit(2)
