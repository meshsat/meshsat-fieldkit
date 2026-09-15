# Extracted from pair_preroute.py on 15 September 2026 (red team round four C3: the split at measurable boundaries),
# behaviour-preserving: every name here is re-exported into pair_preroute's namespace by a star import, and the
# module-level lists and dicts (budgets, timers, caches, epochs) stay the SAME objects, so a function that mutates
# them from any module mutates the one the pass reads. Proved on the box by the pre-router laying the same pairs to
# the same board md5 on D and B before and after (tools/knob_measure).
"""config"""
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

PATH_WHY = [""]   # why the last corridor search returned nothing (9 Sep 2026)
# 9 September 2026 (B19): a wall-clock budget per pair. The two searches are capped by EXPANSIONS (6,000,000 and 400,000),
# which is not a time bound: on B19's board, with 1412 escapes and 951 parts in the way, the longest pair spent eleven
# minutes without finishing one section, and a pass with 113 pairs has no predictable end. PAIR_BUDGET (seconds, default
# 600) makes each pair give up on its own rather than the pass hanging; a pair that runs out is reported unlaid like any
# other, which is honest, and the number of pairs laid is what the gate reads anyway.
PAIR_DEADLINE = [0.0]
PAIR_BUDGET = float(os.environ.get("PAIR_BUDGET", "600"))   # seconds per pair; 0 turns the budget off
# 9 September 2026, measured: a wall-clock budget makes the pass NON-REPRODUCIBLE. Two runs of the same board with the
# same placement and the same 1493 escapes laid 38 and 33 of 113, and the only difference was how loaded the box was
# while each ran: under load a pair gets fewer expansions inside its 300 seconds. A budget that decides the result must
# be counted in work, not in time, so the real cap is expansions and the clock is only the outer safety net.
PAIR_EXPANSIONS = int(os.environ.get("PAIR_EXPANSIONS", "12000000"))   # expansions per pair across all its searches; 0 = off
# Calibrated 10 September 2026: 3,000,000 laid 21 of B19's 113 pairs where the old 300 second clock laid 38, because the
# budget is spent by MANY searches per pair (the corridor plus a stub search per station), not by one. 12,000,000 is the
# figure that matches the clock on a quiet core, and unlike the clock it gives the same answer whatever else the box runs.
PAIR_SPENT = [0]      # expansions this PAIR has spent; reset per pair, because the budget is per pair
PAIR_TOTAL = [0]      # expansions the whole pass has spent; never reset, so the summary line means what it says
_RASTER_FALLBACK = [0]   # times the vectorised rasteriser fell back to the per-cell predicate; reported, never silent
T0 = time.time()   # the pass's own clock, for the phase line at the end
_FAST_SEARCH = os.environ.get("PAIR_FAST_SEARCH", "1") != "0"   # the compiled search when numba is here, the heapq one otherwise; the same path either way (pairsearch.py selftest)
# The stub search on the same kernel, ON where the kernel is compiled. Measured 11 September 2026 on B19, 113 pairs,
# same placed board: 47 of 113 either way, the pass 1586 s to 976 s, the stub search 675 s to 46 s, and the two boards
# byte-identical at 0 of 7,706 items. On D: 5 of 5 either way, 9 s to 3 s, 0 of 478 items. It is OFF without numba,
# because the same kernel interpreted is a numpy heap in a Python loop and that is slower than the heapq it replaces.
_FAST_STUBS = os.environ.get("PAIR_FAST_STUBS", "1" if pairsearch.HAVE_NUMBA else "0") != "0"
# The stub search's own cap, which was 400,000 expansions written into the loop. 14 of B19's 52 remaining failures
# at the peak slack are "no stub path at a station or via" (32.131), and the search that gives up on them is now a
# fifteenth of the cost it was, so the cap is a knob rather than a constant (12 September 2026).
STUB_EXPANSIONS = int(os.environ.get("PAIR_STUB_EXPANSIONS", "400000"))
# Test the legs against a map that exempts the pair's OWN two nets inside the station radius: a leg fans to its
# own pad there and passes its partner's pad on the way, which is an obstacle along the pair and not at its ends.
_SEARCH_KERNEL = ("compiled" if (_FAST_SEARCH and pairsearch.HAVE_NUMBA) else "heapq")   # printed and recorded: a 13x difference must never be invisible (round-two red teams, L2)

CLR = 0.16; HOLE_CLR = 0.30; VIA_COST = 60.0; VIA_SPLIT = 0.9
# 14 September 2026: EVERY OBSTACLE ON EVERY BOARD IS GROWN BY THE SAME 0.16 mm, whatever class it belongs to
# and whatever class the pair belongs to. `stub_router` carried the identical literal and it cost board C two
# connections; here it is the obstacle map the corridor and the leg searches read, so it decides pairs. B19's
# DIFF100 and USB classes ask for 0.127, and the escape fans the legs have to reach their own vias through are
# laid at 0.127 with 0.127 tracks: a lane of 0.254 mm loses a quarter of its width to 0.033 mm of margin at
# each side. 18 of B19's 48 remaining refusals are `no stub path at via`, which is exactly that geometry.
# KiCad's rule is that the clearance between two items is the LARGER of their two classes'. `PAIR_CLASS_CLEAR`
# is off until an arm grades it, because a map this tool reads everywhere is not a thing to change untested;
# with it off every number in the record stands unchanged.
CLASS_CLEAR = os.environ.get("PAIR_CLASS_CLEAR", "0") != "0"
_CLR_NOW = [CLR]     # the clearance of the class being laid, set per pair
_NET_CLR = {}        # net name (no leading slash) -> its class clearance
def _obs_clr(name):
    """the bar between the pair being laid and one obstacle: the larger of the two classes', or the literal"""
    if not CLASS_CLEAR: return CLR
    if not name: return _CLR_NOW[0]
    v = _NET_CLR.get(name[1:] if name.startswith("/") else name)
    return _CLR_NOW[0] if v is None else max(_CLR_NOW[0], v)
# The geometry a pair takes on an INNER layer, per class, because an inner layer is a stripline and the class width that hits
# its target outside does not hit it inside. Measured with the field solver on the JLC 3313 six-layer stack (appendix 32.102):
# at 0.127/0.127 an inner pair is 102 ohm, which is 13 percent high of a 90 ohm target and 2 percent high of a 100 ohm one, so
# the 100 ohm classes need nothing and the 90 ohm one needs 0.15/0.09 (88.9 ohm at 0.390 mm of envelope, against 0.381 today;
# 0.21/0.127 also hits 90 but its envelope is 0.547 and it costs more pairs than the inner layers win).
#   PAIR_INNER="USB:0.15/0.09,DIFF100:0.127/0.127"   per class
#   PAIR_INNER_WIDTH / PAIR_INNER_GAP                the same for every class (the scalar form, kept)
W_INNER = float(os.environ.get("PAIR_INNER_WIDTH", "0"))
S_INNER = float(os.environ.get("PAIR_INNER_GAP", "0"))
# 15 September 2026 (MESHSAT-862), B19's first route for a deliverable. The pre-route DRC on the pair copper read 64 hard,
# and 13 of them were a pair's OWN two legs at 0.122 to 0.126 mm against the 0.127 mm board minimum: the outer gap carried a
# 0.013 mm cushion over the clearance since 12 September and the INNER gap (INNER_BY_CLASS, PAIR_INNER_GAP) carried none, so
# every inner-layer pair laid at exactly the class gap came out a few micrometres under it at its arcs (the offset polyline
# of a chord is not the offset of the arc). On F.Cu the same happened by 18 micrometres with the 0.013 in place. The cushion
# is one number for both, read here, and 0.025 mm absorbs what was measured with a margin: on the 3313 stack it moves an
# inner 100 ohm pair by about 5 percent of its target, inside the judge's 10 percent.
GAP_CUSHION = float(os.environ.get("PAIR_GAP_CUSHION", "0.025"))
INNER_BY_CLASS = {}
for _e in os.environ.get("PAIR_INNER", "").split(","):
    if ":" not in _e: continue
    _c, _g = _e.split(":", 1); _w, _, _s = _g.partition("/")
    INNER_BY_CLASS[_c.strip()] = (float(_w), float(_s or _w))
# ---------------------------------------------------------------- the occupancy maps, built once and topped up (10 Sep 2026)
# MEASURED on B19's 113 pairs after the rasteriser was vectorised: 1,248 of the pass's 1,552 seconds were still in build_maps,
# against 113 in the corridor search. The pads and the rule areas are cached per polygon and cost almost nothing on a repeat;
# what grows is the COPPER THIS PASS LAYS. By the hundredth pair every one of the five maps rasterises thousands of segments
# that were already rasterised for the pair before it. So a map is cached per (layers, excluded nets, half, via radius, split)
# and a repeat call stamps only the tracks it has not seen. Adding copper is safe to top up; REMOVING any (a rollback, a
# stripped escape chain, a retry) invalidates every cached map, which is what MAP_EPOCH counts.
MAP_EPOCH = [0]
def board_remove(b, item):
    """Every removal of copper goes through here, so the cached occupancy maps know they are stale."""
    MAP_EPOCH[0] += 1; b.Remove(item)
_OUTER_CU = (pcbnew.F_Cu, pcbnew.B_Cu)
_ALL = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "In3.Cu": pcbnew.In3_Cu, "In4.Cu": pcbnew.In4_Cu, "B.Cu": pcbnew.B_Cu}

_INNER_CU = tuple(L for L in (pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.In4_Cu))

def mm(v): return v / 1e6


__all__ = [_n for _n in dir() if not _n.startswith("__")]
