#!/usr/bin/env python3
"""The through-current of a track, on a mesh that connects orthogonal neighbours (MESHSAT-862, 13 Sep 2026).

Owner ruling 22 judges every track on its own width against IPC-2221, which makes the current this pass
reports a verdict. On 13 September four of A24's twelve rails reported a conductor carrying MORE CURRENT THAN
THE WHOLE RAIL: +3V3 22.27 A of 0.3, +12V_HF 2.00 A of 1.0, +54V_POE 0.60 A of 0.3, VBUS20 6.80 A of 6.0. A
series conductor cannot, so the number was not a measurement, and three of those rails were being reported
MISSED on it.

The cause is geometric rather than numerical. The mesh joins orthogonal neighbours only. The cells a straight
line steps through are DIAGONAL neighbours wherever the line is not axis-aligned, so `v[a] - v[b]` for two
consecutive cells of the centreline is a potential difference across two hops, and multiplying it by ONE
cell's conductance gives about twice the current that flows. The two rails reading exactly 2.0 times their own
current are that factor in the open.

This builds the mesh the tool builds, on a uniform sheet with a known current, and measures both estimators on
a 45 degree line. It needs no board and no KiCad, so it runs everywhere.
"""
import os
import numpy as np

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sheet(n=41, g=1.0):
    """A square sheet of n x n cells, unit conductance per edge, 1 A injected at the left edge and taken at
    the right edge. The current is then 1 A through any vertical cut, whatever path is drawn across it."""
    import scipy.sparse as sp, scipy.sparse.linalg as spl
    N = n * n
    idx = lambda r, c: r * n + c
    rows, cols, vals = [], [], []
    def add(i, j, gg):
        rows.extend([i, j, i, j]); cols.extend([i, j, j, i]); vals.extend([gg, gg, -gg, -gg])
    for r in range(n):
        for c in range(n):
            if c + 1 < n: add(idx(r, c), idx(r, c + 1), g)
            if r + 1 < n: add(idx(r, c), idx(r + 1, c), g)
    G = sp.coo_matrix((vals, (rows, cols)), shape=(N, N)).tocsr()
    i_vec = np.zeros(N)
    for r in range(n): i_vec[idx(r, 0)] += 1.0 / n          # 1 A in, spread down the left edge
    src = [idx(r, n - 1) for r in range(n)]                 # held at 0 V: the right edge
    keep = np.array([i for i in range(N) if i not in set(src)])
    v = np.zeros(N)
    v[keep] = spl.spsolve(G[keep][:, keep].tocsc(), i_vec[keep])
    return v, idx, n, g


def _old_estimator(v, idx, n, g, ux, uy):
    """What the tool did: consecutive cells along the line, times one cell's conductance."""
    best = 0.0; prev = None
    for k in range(2 * n):
        u = k / (2 * n - 1.0)
        c = int(u * (n - 1) * ux + n * 0.1); r = int(u * (n - 1) * uy + n * 0.1)
        if not (0 <= r < n and 0 <= c < n): continue
        nd = idx(r, c)
        if prev is not None and prev != nd: best = max(best, abs(v[nd] - v[prev]) * g)
        prev = nd
    return best


def _new_estimator(v, idx, n, g, ux, uy):
    """What it does now: the mesh's own branch currents, projected on the line's direction."""
    best = 0.0; seen = set()
    for k in range(2 * n):
        u = k / (2 * n - 1.0)
        c = int(u * (n - 1) * ux + n * 0.1); r = int(u * (n - 1) * uy + n * 0.1)
        if not (0 <= r < n and 0 <= c < n) or (r, c) in seen: continue
        seen.add((r, c))
        ix = (v[idx(r, c)] - v[idx(r, c + 1)]) * g if c + 1 < n else 0.0
        iy = (v[idx(r, c)] - v[idx(r + 1, c)]) * g if r + 1 < n else 0.0
        best = max(best, abs(ix * ux + iy * uy))
    return best


def t_the_old_estimator_overstates_a_diagonal_line_and_the_new_one_does_not():
    v, idx, n, g = _sheet()
    # Along a 45 degree line, one cell of a uniform sheet carries about 1/n of the total in x.
    ux = uy = 0.7071
    old = _old_estimator(v, idx, n, g, ux, uy)
    new = _new_estimator(v, idx, n, g, ux, uy)
    per_cell = 1.0 / n           # the sheet carries 1 A spread over n rows
    # the truth for a diagonal line is the x-component projected: per_cell * ux, plus the y-component, which
    # is zero in this field because nothing flows vertically
    truth = per_cell * ux
    assert abs(new - truth) < 0.25 * truth, "the branch-current estimator is off: %.4f against %.4f" % (new, truth)
    # In a uniform field the overstatement is exactly the square root of two: the old estimator returns the
    # cell's whole current whatever direction the line runs in, so a 45 degree track is credited with 1.414
    # times what flows along it. That is the FLOOR of the error. It is unbounded where the line steps over a
    # cell the net has no copper in, which is the next fixture and is how a 0.3 A rail came to read 22 A.
    assert old > new * 1.3, ("the old estimator did not overstate here, so this fixture does not reproduce the "
                             "defect it was written for: old %.4f new %.4f" % (old, new))
    assert abs(old / new - 2 ** 0.5) < 0.1, "expected the square-root-of-two overstatement, got %.3f" % (old / new)


def t_the_old_estimator_is_unbounded_where_the_line_leaves_the_nets_copper():
    """The real damage. Two cells of the centreline that are not mesh neighbours have a potential difference
    taken across the whole path between them; multiplied by one cell's conductance it is any number at all.
    A24's +3V3 read 22.27 A on a rail given 0.3 A, which is 74 times its whole current."""
    v, idx, n, g = _sheet()
    # two cells on the same row, far apart: the centreline of a track that runs along a rail with a real drop
    a, b = idx(n // 2, 2), idx(n // 2, n - 3)
    apart = abs(v[a] - v[b]) * g            # what the old expression computes for such a pair
    true_branch = abs(v[a] - v[idx(n // 2, 3)]) * g   # the current actually flowing between neighbours
    assert apart > true_branch * 10, ("the fixture does not separate the two: %.5f against %.5f"
                                      % (apart, true_branch))


def t_the_pass_reads_the_meshs_own_conductance():
    src = open(os.path.join(TOOLS, "dc_drop.py")).read()
    assert "ge = g0 * min(f_i," in src, "the conductor pass does not use the mesh's own edge conductance"
    assert "comp[0] * ux + comp[1] * uy" in src, "the conductor pass does not project on the track direction"
    assert "abs(v[nd] - v[prev[0]]) * g" not in src, "the old centreline expression is still there"


def t_an_impossible_conductor_current_is_not_judged():
    src = open(os.path.join(TOOLS, "dc_drop.py")).read()
    assert 'cond[0][2] > amps * 1.25' in src, "a conductor current far above the rail's own total is still judged"
    assert '_clamped' in src and 'min(c[2], amps)' in src, "a small excess is not clamped to what the rail can supply"
    assert '"UNMEASURED"' in src
    assert '("UNDECLARED", "UNMEASURED")' in src, "an unmeasured rail does not reach the board's inconclusive verdict"


def t_a_pour_cell_is_full_copper_even_where_a_track_crosses_it():
    """A24's +5V_S1 and +5V_S3 read exactly 1.00 on 4.9 mm of track that lies INSIDE an 84 mm2 island of
    their own net. The mesh was giving that cell the track's fraction and throwing the island away, and then
    the conductor pass asked the track to carry what the island was sharing."""
    src = open(os.path.join(TOOLS, "dc_drop.py")).read()
    assert "zone_occ" in src, "the raster does not record which cells a pour fills"
    assert "frac[L][zone_occ[L]] = 1.0" in src, "a cell a pour fills is still modelled as a bare track"
    assert "if zone_occ[L][gy, gx]: continue" in src, \
        "the conductor pass still judges a track stretch that lies inside a pour of its own net"
    i = src.find("zone_occ[L] |= occ[L]")
    assert i > 0, "the zone mask is never filled from the zone raster"


def t_a_via_is_judged_on_its_own_barrel_and_not_on_the_cell_it_funnels_through():
    """Measured on two boards in opposite directions. On all twelve of A24's rails the worst pour cell is
    clear of every via. On E7's VIN_RAW it IS a via: the cell reads 2.20 while the barrel carrying that
    current sits at 0.79 of its own limit, and the worst cell clear of vias reads 1.21. A cell at a barrel is
    a spreading region a millimetre across, not a conductor at thermal steady state."""
    src = open(os.path.join(TOOLS, "dc_drop.py")).read()
    assert "net_vias.append" in src, "the barrels of a net are not collected"
    assert "via_worst" in src and "ipc_limit(vwall, dT_of(r), True)" in src, \
        "no barrel is judged on its own wall cross-section, with the rail's own rise read where it is needed"
    assert "via_ratio <= 1.0" not in src, \
        ("the barrel ratio is gating again. It does not converge: measured on P3, one variable, PACK_P's "
         "worst barrel reads 1.20 at a 0.50 mm cell and 1.71 at 0.25, and CELL4 goes MET to MISSED across "
         "the same change. Report it; do not let it decide a board until it has no grid in it.")
    assert "REPORTED, not gated" in src, "the report does not say the barrel number is not gated"
    assert "zone_ratio = (czone_j / jl)" in src, "the pour is still gated on a cell that may be a via's funnel"
    assert 'max(cond_ratio, zone_ratio)' in src, "the reported ratio carries a number that does not converge"


def t_the_barrel_limit_uses_the_wall_and_not_the_hole():
    """pi * d * plating is the copper, and the hole is not copper. A 0.4 mm drill at 25 um plating is
    0.0314 mm2 of wall, which IPC gives about 1.1 A: the number E7's worst barrel was judged against."""
    import math
    wall = math.pi * 0.4 * 25e-6 * 1e3
    assert abs(wall - 0.0314) < 0.0005, "the barrel wall arithmetic moved: %.4f" % wall
    a_mil2 = wall / (0.0254 ** 2)
    amps = 0.024 * (10.0 ** 0.44) * (a_mil2 ** 0.725)
    assert 0.9 < amps < 1.4, "a 0.4 mm barrel should carry about 1.1 A at 10 K, got %.2f" % amps


def t_a_piece_shorter_than_a_conductor_is_reported_and_not_gated():
    """IPC-2221's curve is the steady-state rise of a LONG trace, where heat has nowhere to go sideways. A
    segment shorter than its own width is a joint: the copper at both ends conducts its heat away. P3 was
    being failed on a 0.500 mm segment 0.0 mm long and D10 on one 0.1 mm long, each a router's junction
    between two pieces that ARE judged."""
    src = open(os.path.join(TOOLS, "dc_drop.py")).read()
    assert "ln < max(1.0, 2.0 * w)" in src, "a segment shorter than its own width is still judged as a conductor"
    assert "short.append" in src and "short.sort" in src, "the skipped pieces are not collected"
    assert "shorter than a conductor were not judged" in src, \
        "the skipped pieces are not reported, so a real neck could hide in one"
    i, j = src.find("short.append"), src.find("cond.append((best / lim_a")
    assert 0 < i < j, "the skip must come before the conductor list, or both lists carry it"


def t_the_drop_line_prints_the_bar_it_was_judged_against():
    """16 September 2026. dc_drop judges a rail against its declared SHARE where there is one, and printed the
    bar with "%.0f", so board A's 1.5 percent share came out as "budget 2%" and board C's 0.75 as "1". The
    number it judged by was right throughout; the sentence about it was not, and a line that cannot be checked
    against the number it claims is how a wrong bar survives a reading.

    The share exists to make a split visible, so printing it rounded to the whole rail's budget defeats the
    declaration this project just made on seven rails."""
    src = open(os.path.join(TOOLS, "dc_drop.py"), encoding="utf-8").read()
    line = next(l for l in src.splitlines() if "worst drop" in l and "%" in l)
    assert "budget %.0f%%" not in line, "the bar is still printed rounded to whole percent: %s" % line.strip()[:120]
    assert "%.3g%%" in line, "the bar must be printed at the precision it is judged at"
    assert "bar %.3g%%" in line, "say BAR rather than budget, because a share is not the rail's budget"
