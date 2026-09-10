#!/usr/bin/env python3
"""The corridor search: the compiled kernel, the array kernel and the heapq original must be one router.

If they ever diverge, every pre-router measurement taken on a box with numba means something different from one taken without
it, and the record's ladders stop comparing (plan stage 5, 10 September 2026)."""
import os
import pairsearch
import numpy as np
from harness import Skip


def t_the_three_implementations_agree():
    """Without numba this host has TWO implementations, not three, so a pass here would certify the compiled kernel by
    never running it (round-two red teams, H2). Every pair number in the record came from the compiled kernel, so the
    honest outcome on such a host is Skip. PAIR_REQUIRE_NUMBA=1 turns the absence into a failure, which is what the box
    that produces the measurements sets."""
    if pairsearch._run_nb is None:
        if os.environ.get("PAIR_REQUIRE_NUMBA") == "1":
            raise AssertionError("numba is absent and PAIR_REQUIRE_NUMBA=1: the compiled kernel cannot be certified here")
        assert pairsearch.selftest(16, seed=3, verbose=False) == 0, "the two available implementations disagree"
        raise Skip("no numba on this host: the heapq original and the array kernel agree, the compiled one was not run")
    assert pairsearch.selftest(16, seed=3, verbose=False) == 0, "the search implementations disagree"


def t_a_wall_of_blocked_cells_has_no_path():
    p = np.ones((1, 20, 20), dtype=bool); p[0, :, 10] = False
    v = np.zeros((20, 20), dtype=bool)
    path, n, why = pairsearch.search(p, v, None, [(0, 0, 0)], (0, 19, 19))
    assert path is None and why == "nopath", (path, why)


def t_a_via_is_taken_only_where_it_is_allowed():
    """Two layers, the goal reachable only by changing layer at one cell: blocked there, no path; free there, a path."""
    p = np.zeros((2, 5, 5), dtype=bool); p[0, 0, 0] = True; p[1, 0, 0] = True; p[1, :, :] = True
    v = np.ones((5, 5), dtype=bool)                      # every cell forbids a via
    assert pairsearch.search(p, v, None, [(0, 0, 0)], (1, 4, 4))[0] is None
    v[0, 0] = False                                      # except the start
    path, n, why = pairsearch.search(p, v, None, [(0, 0, 0)], (1, 4, 4))
    assert path is not None and path[0] == (0, 0, 0) and path[1] == (1, 0, 0), path


def t_the_cost_raster_bends_the_path():
    """The negotiated-congestion term: an expensive lane must push the corridor off it."""
    p = np.ones((1, 9, 9), dtype=bool); v = np.zeros((9, 9), dtype=bool)
    plain = pairsearch.search(p, v, None, [(0, 4, 0)], (0, 4, 8))[0]
    cost = np.zeros((1, 9, 9)); cost[0, 4, :] = 50.0
    bent = pairsearch.search(p, v, cost, [(0, 4, 0)], (0, 4, 8))[0]
    assert any(c[1] == 4 for c in plain[1:-1]), plain
    assert not any(c[1] == 4 for c in bent[1:-1]), bent


def t_the_expansion_cap_is_reported_as_capped():
    p = np.ones((1, 60, 60), dtype=bool); v = np.zeros((60, 60), dtype=bool)
    path, n, why = pairsearch.search(p, v, None, [(0, 0, 0)], (0, 59, 59), max_exp=5)
    assert path is None and why == "capped" and n <= 6, (n, why)


def t_no_start_is_an_empty_search_not_a_crash():
    p = np.ones((1, 5, 5), dtype=bool); v = np.zeros((5, 5), dtype=bool)
    assert pairsearch.search(p, v, None, [], (0, 4, 4)) == (None, 0, "empty")
