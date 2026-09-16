#!/usr/bin/env python3
"""The pre-router's occupancy maps: counted once for the board, compared per pair.

MESHSAT-862, round-two C3, 11 September 2026. Four of the five `build_maps` calls a pair makes excluded that pair's own
nets, so the cache key was unique per pair and each one rebuilt the whole board: 1,010 s of a 1,327 s B19 pass, against
115 s in the corridor search the pass exists to run.

The review's proposed expression was `all & ~own_P & ~own_N`. **That is not the same map.** Where two nets' grown
rasters overlap, clearing the pair's own bits also clears cells the other net blocks, and the error frees copper in the
unsafe direction. The fix counts how many stamps cover each cell and asks whether the total exceeds the pair's own.

These tests are pure numpy so they run on every host. The whole-board equivalence against the reference implementation
needs pcbnew and a real board, and is `PAIR_MAP_CHECK=1` on the box.
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _acc(M, i0, i1, j0, j1, mask):
    """The accumulation under test, copied in shape from pair_preroute._acc so this file needs no pcbnew."""
    if M.dtype == bool: M[i0:i1 + 1, j0:j1 + 1] |= mask
    else: M[i0:i1 + 1, j0:j1 + 1] += mask


def t_acc_ors_a_boolean_raster_and_adds_to_an_integer_one():
    b = np.zeros((4, 4), dtype=bool); n = np.zeros((4, 4), dtype=np.uint16)
    m = np.ones((2, 2), dtype=bool)
    _acc(b, 0, 1, 0, 1, m); _acc(b, 0, 1, 0, 1, m)
    _acc(n, 0, 1, 0, 1, m); _acc(n, 0, 1, 0, 1, m)
    assert b[0, 0] == True and b.sum() == 4, b
    assert n[0, 0] == 2 and n.sum() == 8, n


def t_counting_keeps_a_cell_two_nets_both_block():
    """The defect boolean subtraction would introduce, stated as a test.

    Net P covers cells 0..2, net Q covers cells 1..3. Cell 1 and 2 are covered by both. A pair on net P must still see
    cells 1 and 2 as blocked, because Q blocks them."""
    P = np.array([1, 1, 1, 0], dtype=bool)
    Q = np.array([0, 1, 1, 1], dtype=bool)

    reference = Q                                    # what build_maps must return for a pair on P: only other nets
    wrong = (P | Q) & ~P                             # the review's expression
    right = (P.astype(np.uint16) + Q) > P.astype(np.uint16)

    assert not np.array_equal(wrong, reference), "the test is pointless if the wrong expression happens to agree"
    assert list(wrong) == [False, False, False, True], list(wrong)
    assert np.array_equal(right, reference), (list(right), list(reference))
    assert list(right) == [False, True, True, True], list(right)


def t_a_net_that_covers_a_cell_twice_still_cancels_exactly():
    """One net can stamp a cell more than once (two pads of that net overlapping, a via on its own track). The own
    count must cancel the whole of that net's contribution and nothing else."""
    allc = np.zeros(3, dtype=np.uint16); own = np.zeros(3, dtype=np.uint16)
    for _ in range(3):                                # the pair's net covers cell 0 three times
        allc[0] += 1; own[0] += 1
    allc[1] += 1                                      # another net covers cell 1 once
    allc[2] += 2; own[2] += 2                         # the pair covers cell 2 twice and nobody else does
    got = allc > own
    assert list(got) == [False, True, False], list(got)


def t_the_own_count_never_exceeds_the_all_count():
    """The comparison is only safe because the own pass stamps a subset of the all pass, with the same keys and the
    same grow values. If that ever stopped holding, `all > own` would silently free cells."""
    rng = np.random.default_rng(20260911)
    for _ in range(200):
        nets = rng.integers(0, 2, size=(5, 40)).astype(np.uint16)   # 5 nets over 40 cells
        allc = nets.sum(axis=0, dtype=np.uint16)
        for k in range(5):
            own = nets[k]
            assert (own <= allc).all(), "the own count exceeded the all count"
            others = np.delete(nets, k, axis=0).sum(axis=0) > 0
            assert np.array_equal(allc > own, others)


def t_a_pair_is_two_nets_and_both_are_subtracted():
    rng = np.random.default_rng(11092026)
    for _ in range(200):
        nets = rng.integers(0, 2, size=(6, 30)).astype(np.uint16)
        allc = nets.sum(axis=0, dtype=np.uint16)
        own = (nets[0] + nets[1]).astype(np.uint16)
        others = nets[2:].sum(axis=0) > 0
        assert np.array_equal(allc > own, others)


def t_the_hole_to_hole_component_is_never_subtracted():
    """A drilled pad blocks a via centre by hole-to-hole whatever net it is on, the pair's own net included. That
    component is a separate boolean raster and is OR-ed back after the comparison, exactly as the reference stamps it
    before its own-net guard."""
    all_clr = np.array([1, 1, 0, 0], dtype=np.uint16)
    own_clr = np.array([1, 0, 0, 0], dtype=np.uint16)
    holes = np.array([True, False, False, True])
    via = (all_clr > own_clr) | holes
    assert list(via) == [True, True, False, True], list(via)


def t_an_existing_via_blocks_a_new_via_site():
    """DEFECTIVE fixture expects the via map to be stamped; ACCEPTABLE fixture is the track branch beside it.

    `_track_stamp` put a via into the TRACK raster only. A pad is stamped into both rasters and so is a track,
    but a via went into `trk` and never into `via_clr`, so the site search for a NEW via could not see a single
    via already on the board.

    Board B's placement pilot measured the cost on 16 September 2026: at every couple gap tried (2.4, 2.6, 3.0)
    the DIFF100 pass laid vias belonging to DIFFERENT pairs 0.1062 to 0.1075 mm apart against a 0.127 mm class
    clearance, and in one case two vias 0.0071 mm apart, which is one via on top of another. All three arms
    graded ILLEGAL against a legal baseline, which is how it surfaced.

    Run with fakes rather than a board: the function needs a recorder for `gr` and an object that answers the
    four methods it calls. pcbnew is imported by the module, so this skips on a host without it.
    """
    try:
        import pcbnew  # noqa: F401
    except Exception as e:
        from harness import Skip
        raise Skip("the pre-router's occupancy module imports pcbnew (%s)" % type(e).__name__)
    from pair_router import occupancy

    class Rec:
        def __init__(self): self.discs = []; self.segs = []; self.polys = []
        def disc(self, m, x, y, r, **k): self.discs.append((id(m), x, y, r))
        def seg(self, m, *a, **k): self.segs.append(id(m))
        def poly(self, m, *a, **k): self.polys.append(id(m))

    class FakePt:
        def __init__(self, x, y): self.x = int(x * 1e6); self.y = int(y * 1e6)

    class FakeVia:
        def GetClass(self): return "PCB_VIA"
        def GetPosition(self): return FakePt(10.0, 20.0)
        def GetWidth(self, *a): return int(0.7 * 1e6)
        def GetNetname(self): return "/PAIR_P"

    trk = {pcbnew.F_Cu: object(), pcbnew.B_Cu: object()}
    via_clr = object()
    gr = Rec()
    occupancy._track_stamp(gr, list(trk), FakeVia(), trk, via_clr, 0.0635, 0.35, 0.0)

    into_via_map = [d for d in gr.discs if d[0] == id(via_clr)]
    assert into_via_map, ("a via was stamped into the track map only, so the search for a new via site cannot "
                          "see it; discs went to %s, via_clr is %s" % ([d[0] for d in gr.discs], id(via_clr)))
    # the radius must carry the NEW via's radius too, or two vias may still sit a hole apart
    r = into_via_map[0][3]
    assert r >= 0.35 + 0.35, "the via-map radius %.3f does not include the new via's own radius" % r
