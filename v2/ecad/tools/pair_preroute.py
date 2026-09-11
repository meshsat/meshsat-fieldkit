#!/usr/bin/env python3
"""Differential-pair pre-router (MESHSAT-862 rule 1 of appendix 32.67, 8 Sep 2026): Freerouting has no pair routing, so every released pair was
two lone traces millimetres apart (32.66). This lays both legs of a pair as LOCKED copper before Freerouting runs, at the class width w and
gap s, on the class's allowed layers (rule 2), so the router only sees two finished nets.

Method (the stub router's grid, 0.1 mm): the pair's centreline is routed by A* from the midpoint between the two P and N starts to the
midpoint between the two ends, on a map where every other-net copper item is grown by (clearance + w + s/2), the pair's half envelope; a
through via costs VIA_COST and is only allowed where two via sites (0.9 mm apart along the local normal) are free. The path is simplified to
straight runs; each run is offset by +-(w + s)/2 on its layer, consecutive runs meet at their offset intersection (a mitre); at a layer change
each leg gets its own via 0.9 mm from the centreline with a jog; at the ends short stubs join the offset ends to the pads (or to the escape
vias when the pads carry locked escapes). Everything added is locked. A pair whose centreline finds no path is reported and left to the
router (the gate then calls it UNCOUPLED). The caller runs DRC.

Rip-up and retry (10 Sep 2026): a pair that fails takes the laid pairs out of its corridor and is laid again before them, because a pair that
fails in the pass often lays alone on the same board (measured on B19), so the failure is the greedy order, not the placement. PAIR_RIPUP=0
turns it off and restores the plain greedy pass; PAIR_RIP_MARGIN, PAIR_RIP_MAX and PAIR_RIP_TOTAL bound how much is ripped.

Usage: pair_preroute.py <board.kicad_pcb> [--pairs STEM,STEM] [--layers F.Cu,In2.Cu] [--classes USB,DIFF100] [--test] [--grid 0.1]
  prints one line per pair and `pair_preroute: N of M pairs laid, R rip-up event(s)`, exit 1 when a pair failed."""
import sys, os, re, math, json, heapq, time

# ---------------------------------------------------------------- the compiled search needs an interpreter that has numba
# The corridor search is 13.5x faster compiled (2.26 million expansions a second against 167 thousand; `pairsearch.py bench`),
# and numba is not installable into the KiCad python of a rented box. A venv made with `--system-site-packages` has both, so
# rather than edit every chain the tool re-execs itself under that interpreter, says so, and checks first that the interpreter
# really imports pcbnew and numba. PAIR_VENV=0 stays here; PAIR_VENV=<python> names another one.
def _reexec_for_numba():
    import importlib.util, subprocess
    if os.environ.get("PAIR_VENV") == "0" or os.environ.get("_PAIR_REEXEC"): return
    if importlib.util.find_spec("numba") is not None: return
    cand = os.environ.get("PAIR_VENV") or "/root/venv-numba/bin/python"
    if not os.path.exists(cand): return
    try:
        if subprocess.run([cand, "-c", "import numba, pcbnew, numpy"], capture_output=True, timeout=120).returncode != 0: return
    except Exception: return
    os.environ["_PAIR_REEXEC"] = "1"
    print("pair_preroute: re-exec under %s, which has numba, for the compiled corridor search (PAIR_VENV=0 to stay here)" % cand, flush=True)
    try: os.execv(cand, [cand] + sys.argv)
    except Exception as e: print("pair_preroute: the re-exec failed (%s); the heapq search it is" % e, flush=True)
if __name__ == "__main__": _reexec_for_numba()   # only as a script: importing this module must never restart the caller's process
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
import pcbnew, numpy as np
try:
    from matplotlib.path import Path as _PATH   # the vectorised point-in-polygon test; without it the SWIG loop below is used
except Exception:
    _PATH = None
from pcbnew import VECTOR2I, FromMM
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pairsearch
_FAST_SEARCH = os.environ.get("PAIR_FAST_SEARCH", "1") != "0"   # the compiled search when numba is here, the heapq one otherwise; the same path either way (pairsearch.py selftest)
_SEARCH_KERNEL = ("compiled" if (_FAST_SEARCH and pairsearch.HAVE_NUMBA) else "heapq")   # printed and recorded: a 13x difference must never be invisible (round-two red teams, L2)

CLR = 0.16; HOLE_CLR = 0.30; VIA_COST = 60.0; VIA_SPLIT = 0.9
# The geometry a pair takes on an INNER layer, per class, because an inner layer is a stripline and the class width that hits
# its target outside does not hit it inside. Measured with the field solver on the JLC 3313 six-layer stack (appendix 32.102):
# at 0.127/0.127 an inner pair is 102 ohm, which is 13 percent high of a 90 ohm target and 2 percent high of a 100 ohm one, so
# the 100 ohm classes need nothing and the 90 ohm one needs 0.15/0.09 (88.9 ohm at 0.390 mm of envelope, against 0.381 today;
# 0.21/0.127 also hits 90 but its envelope is 0.547 and it costs more pairs than the inner layers win).
#   PAIR_INNER="USB:0.15/0.09,DIFF100:0.127/0.127"   per class
#   PAIR_INNER_WIDTH / PAIR_INNER_GAP                the same for every class (the scalar form, kept)
W_INNER = float(os.environ.get("PAIR_INNER_WIDTH", "0"))
S_INNER = float(os.environ.get("PAIR_INNER_GAP", "0"))
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

def _acc(M, i0, i1, j0, j1, mask):
    """OR a boolean mask into a boolean raster, ADD it into an integer one.

    The integer form is what makes the per-pair map exact (MESHSAT-862, round-two C3, 11 September 2026). A pair's
    forbidden map is "every cell some OTHER net blocks", and `all & ~own` does not compute that: where two nets' grown
    rasters overlap, clearing the pair's own bits also clears cells the other net blocks, which frees copper in the
    UNSAFE direction. Counting how many stamps cover each cell makes it exact: a cell is blocked by someone else iff
    the total count exceeds the pair's own count.
    """
    if M.dtype == bool: M[i0:i1 + 1, j0:j1 + 1] |= mask
    else: M[i0:i1 + 1, j0:j1 + 1] += mask


class Grid:
    def __init__(self, b, g):
        # 10 September 2026 (report 1, P1): the rasterisation cache used to be a CLASS attribute keyed by (part, grow) only, so
        # a second grid with a different cell size read masks rasterised in the first one's coordinate system. Nothing had gone
        # wrong yet because the adaptive grid is off by default, which is the definition of a latent defect. The cache belongs
        # to the grid that filled it; the reuse that matters (every pair of a pass shares one grid) is untouched.
        self._cache = {}
        self.b, self.G = b, g; eb = b.GetBoardEdgesBoundingBox()
        self.X0, self.Y0 = eb.GetLeft() / 1e6 - 1.0, eb.GetTop() / 1e6 - 1.0
        self.NX, self.NY = int(eb.GetWidth() / 1e6 / g) + 20, int(eb.GetHeight() / 1e6 / g) + 20
    def cell(self, x, y): return int(round((x - self.X0) / self.G)), int(round((y - self.Y0) / self.G))
    def xy(self, j, i): return self.X0 + j * self.G, self.Y0 + i * self.G
    def disc(self, M, cx, cy, r):
        G, X0, Y0, NX, NY = self.G, self.X0, self.Y0, self.NX, self.NY
        i0, i1 = max(0, int((cy - r - Y0) / G)), min(NY - 1, int((cy + r - Y0) / G) + 1); j0, j1 = max(0, int((cx - r - X0) / G)), min(NX - 1, int((cx + r - X0) / G) + 1)
        if i1 < i0 or j1 < j0: return
        ys = (np.arange(i0, i1 + 1) * G + Y0)[:, None]; xs = (np.arange(j0, j1 + 1) * G + X0)[None, :]
        _acc(M, i0, i1, j0, j1, (xs - cx) ** 2 + (ys - cy) ** 2 <= r * r)
    def seg(self, M, ax, ay, bx, by, r):
        G, X0, Y0, NX, NY = self.G, self.X0, self.Y0, self.NX, self.NY
        i0, i1 = max(0, int((min(ay, by) - r - Y0) / G)), min(NY - 1, int((max(ay, by) + r - Y0) / G) + 1); j0, j1 = max(0, int((min(ax, bx) - r - X0) / G)), min(NX - 1, int((max(ax, bx) + r - X0) / G) + 1)
        if i1 < i0 or j1 < j0: return
        ys = (np.arange(i0, i1 + 1) * G + Y0)[:, None]; xs = (np.arange(j0, j1 + 1) * G + X0)[None, :]
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
        t = 0 if L2 == 0 else np.clip(((xs - ax) * dx + (ys - ay) * dy) / L2, 0, 1)
        _acc(M, i0, i1, j0, j1, (xs - (ax + t * dx)) ** 2 + (ys - (ay + t * dy)) ** 2 <= r * r)
    # (key, grow) -> (i0, j0, mask): a pad or zone outline rasterised once per grow value, per grid (see __init__)
    def poly(self, M, sps, grow, key=None):
        bb = sps.BBox(); G, X0, Y0, NX, NY = self.G, self.X0, self.Y0, self.NX, self.NY; r = grow
        i0, i1 = max(0, int((mm(bb.GetTop()) - r - Y0) / G)), min(NY - 1, int((mm(bb.GetBottom()) + r - Y0) / G) + 1); j0, j1 = max(0, int((mm(bb.GetLeft()) - r - X0) / G)), min(NX - 1, int((mm(bb.GetRight()) + r - X0) / G) + 1)
        if i1 < i0 or j1 < j0: return
        ck = (key, round(grow, 4)) if key is not None else None
        if ck is not None and ck in self._cache:
            ci0, cj0, mask = self._cache[ck]
            _acc(M, ci0, ci0 + mask.shape[0] - 1, cj0, cj0 + mask.shape[1] - 1, mask); return
        grown = pcbnew.SHAPE_POLY_SET(sps)
        # +0.1 um so a cell centre exactly on the boundary counts as blocked. It is done on the POLYGON, not by matplotlib's
        # `radius`, which inflates every sub-path on its own and so fills a polygon's holes: with it the board-wide "edge band"
        # keep-out (a ring, 1,593 mm2 of band around a 65,060 mm2 hole) blocked all 6,708,420 cells of the map (10 Sep 2026).
        _g = grow + 1e-4
        try: grown.Inflate(FromMM(_g), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, FromMM(0.05))
        except Exception:
            # If BOTH inflate calls fail the polygon is rasterised at its bare outline, with no clearance ring, and a pair
            # is then laid against the pad it should have kept away from: a silent fallback in the UNSAFE direction
            # (round-two red teams, M1). The one-sided correctness gate never exercised this branch, because nothing raised
            # on the board it was measured against. It raises now.
            grown.Inflate(FromMM(_g), 16)
        # 10 September 2026, MEASURED (report 2, M1): this loop called SHAPE_POLY_SET.Contains through SWIG once per cell, and a
        # profile of three B19 pairs spent 270 of 330 seconds here across 56.4 million Contains calls and 112.8 million FromMM
        # conversions, against 41 seconds in the A* it exists to feed. The polygon's own vertices go to numpy once and
        # matplotlib's path test does every cell in one call. Same predicate, and the old loop stays as the fallback.
        mask = self._poly_mask(grown, i0, i1, j0, j1)
        if ck is not None: self._cache[ck] = (i0, j0, mask)
        _acc(M, i0, i1, j0, j1, mask)

    def _poly_mask(self, grown, i0, i1, j0, j1):
        """The cells of the box [i0..i1] x [j0..j1] whose centres lie inside `grown`."""
        G, X0, Y0 = self.G, self.X0, self.Y0
        ys = np.arange(i0, i1 + 1) * G + Y0; xs = np.arange(j0, j1 + 1) * G + X0
        if _PATH is not None:
            try:
                XX, YY = np.meshgrid(xs, ys)
                pts = np.column_stack((XX.ravel(), YY.ravel()))

                def _ring_mask(chain):
                    """The cells inside one closed ring. matplotlib's contains_points fills every sub-path whatever its winding
                    (checked: a square with a reversed inner square still reports the middle as inside), so a polygon's holes
                    cannot be expressed as sub-paths and are subtracted here instead. Without this the board-wide "edge band"
                    keep-out, a 1,593 mm2 ring around a 65,060 mm2 hole, blocked the whole map (10 September 2026)."""
                    n = chain.PointCount()
                    if n < 3: return np.zeros(pts.shape[0], dtype=bool)
                    v = [(chain.CPoint(k).x / 1e6, chain.CPoint(k).y / 1e6) for k in range(n)]
                    return _PATH(np.asarray(v + [v[0]]), np.asarray([1] + [2] * (n - 1) + [79], dtype=np.uint8)).contains_points(pts)

                inside = np.zeros(pts.shape[0], dtype=bool)
                for oi in range(grown.OutlineCount()):
                    m = _ring_mask(grown.Outline(oi))
                    for hi in range(grown.HoleCount(oi)): m &= ~_ring_mask(grown.Hole(oi, hi))
                    inside |= m
                return inside.reshape(len(ys), len(xs))
            except Exception as _e:
                # Falling back to the per-cell SWIG predicate is legitimate (it is the same answer) but it is 17.7x slower,
                # and it used to happen with no line anywhere: a pass could be twenty minutes slower for a reason nothing
                # recorded (round-two red teams, M1). It is counted and reported in the summary now.
                _RASTER_FALLBACK[0] += 1
                if _RASTER_FALLBACK[0] == 1: print("pair_preroute: the vectorised rasteriser fell back to the per-cell predicate (%s); the maps are correct and much slower" % _e, flush=True)
        mask = np.zeros((len(ys), len(xs)), dtype=bool)
        for ii in range(i0, i1 + 1):
            for jj in range(j0, j1 + 1):
                if grown.Contains(VECTOR2I(FromMM(X0 + jj * G), FromMM(Y0 + ii * G))): mask[ii - i0, jj - j0] = True
        return mask


_MAPS = {}   # (grid, layers, excluded nets, half, via radius, split) -> [trk, via, tracks already stamped, MAP_EPOCH when built]
_ALLMAPS = {}   # (grid, layers, half, via radius, split) -> the whole-board counts, built once for every pair of a pass

# PAIR_MAP_MODE=reference restores the per-pair full rebuild; PAIR_MAP_CHECK=1 runs both and refuses any difference.
MAP_MODE = os.environ.get("PAIR_MAP_MODE", "counts")
MAP_CHECK = os.environ.get("PAIR_MAP_CHECK") == "1"


def _pad_stamp(gr, layers, ref, p, trk, via_clr, half, via_r, split):
    """One pad's clearance into the count rasters. Shared by the whole-board pass and the per-pair pass."""
    pth = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
    pk = "%s.%s@%d,%d" % (ref, p.GetNumber(), p.GetPosition().x, p.GetPosition().y)   # the position is part of the key: a swapped resistor keeps its raster otherwise (D9, 8 Sep 2026 12:59)
    for L in layers:
        if p.IsOnLayer(L): gr.poly(trk[L], p.GetEffectivePolygon(L), CLR + half, key=(pk, L))
        if pth and p.IsOnLayer(L): c = p.GetPosition(); d = p.GetDrillSize(); gr.disc(trk[L], mm(c.x), mm(c.y), mm(max(d.x, d.y)) / 2 + HOLE_CLR + half)
    anyL = next((L for L in _ALL.values() if p.IsOnLayer(L)), None)   # any copper layer: a via is a hole through every layer
    if anyL is not None or pth: gr.poly(via_clr, p.GetEffectivePolygon(anyL if anyL is not None else pcbnew.F_Cu), CLR + via_r + split, key=(pk, "via", anyL))


def _track_stamp(gr, layers, t, trk, via_clr, half, via_r, split):
    """One track or via's clearance into the count rasters."""
    if t.GetClass() == "PCB_VIA":
        c = t.GetPosition(); r = mm(t.GetWidth(pcbnew.F_Cu)) / 2
        for L in layers: gr.disc(trk[L], mm(c.x), mm(c.y), r + CLR + half)
    else:
        a, e = t.GetStart(), t.GetEnd(); r = mm(t.GetWidth()) / 2; L = t.GetLayer()
        if L in trk: gr.seg(trk[L], mm(a.x), mm(a.y), mm(e.x), mm(e.y), r + CLR + half)
        gr.seg(via_clr, mm(a.x), mm(a.y), mm(e.x), mm(e.y), r + CLR + via_r + split)


def _stamp_board(gr, b, layers, trk, via_clr, via_holes, half, via_r, split, idx):
    """Every net's copper into the counts, once, and an index of which items belong to which net.

    The index is what makes the per-pair map cheap. Without it the own-net pass still walks every footprint,
    every pad and every track of the board to find the two nets it cares about, and SWIG's proxy-per-item
    iteration is most of that cost: measured on D, the counted map came out SLOWER than the per-pair rebuild
    it replaced, 21 s against 17 s, with identical pairs and identical expansions. 11 September 2026."""
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        for p in fp.Pads():
            if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
                c = p.GetPosition(); d = p.GetDrillSize(); gr.disc(via_holes, mm(c.x), mm(c.y), mm(max(d.x, d.y)) / 2 + 0.2 + 0.30)
            idx.setdefault(p.GetNetname(), [[], []])[0].append((ref, p))
            _pad_stamp(gr, layers, ref, p, trk, via_clr, half, via_r, split)
    # Footprint-local rule areas count too: they are not in b.Zones(), so a keep-out that belongs to a part (the E72's antenna clearance,
    # a connector's own no-track area) was invisible here while `prefanout.py` already read them. B17's pre-route came back with five
    # items_not_allowed, all of them pair copper laid straight through one (9 Sep 2026 02:20, MESHSAT-862). A rule area belongs to no
    # net, so it is stamped only here and can never be subtracted for the pair being laid.
    for z in list(b.Zones()) + [z for fp in b.GetFootprints() for z in fp.Zones()]:
        if z.GetIsRuleArea():
            zk = "zone.%s" % z.m_Uuid.AsString() if hasattr(z, "m_Uuid") else "zone.%d" % id(z)
            for L in layers:
                if z.IsOnLayer(L) and z.GetDoNotAllowTracks(): gr.poly(trk[L], z.Outline(), CLR + half, key=(zk, L))
            if z.GetDoNotAllowVias(): gr.poly(via_clr, z.Outline(), CLR + via_r + split, key=(zk, "via"))


def _stamp_new_copper(gr, b, layers, trk, via_clr, via_holes, half, via_r, split, seen, idx):
    """Tracks and vias laid since the last call, into the counts and the index. Returns how many were new."""
    n = 0
    for t in b.GetTracks():
        k = _track_key(t)
        if k in seen: continue
        seen.add(k); n += 1
        if t.GetClass() == "PCB_VIA":
            c = t.GetPosition(); gr.disc(via_holes, mm(c.x), mm(c.y), mm(t.GetDrillValue()) / 2 + 0.2 + 0.30 + split)
        idx.setdefault(t.GetNetname(), [[], []])[1].append(t)
        _track_stamp(gr, layers, t, trk, via_clr, half, via_r, split)
    return n


def _stamp_own(gr, layers, nets, idx, trk, via_clr, half, via_r, split):
    """Just this pair's own copper, from the index: a handful of pads and the legs laid so far."""
    for nm in nets:
        pads, tracks = idx.get(nm, ([], []))
        for ref, p in pads: _pad_stamp(gr, layers, ref, p, trk, via_clr, half, via_r, split)
        for t in tracks: _track_stamp(gr, layers, t, trk, via_clr, half, via_r, split)


def _all_counts(gr, b, layers, half, via_r, split):
    """The whole board counted once, with an index from net name to the items on it.

    This is the change of 11 September 2026 (round-two C3). Four of the five `build_maps` calls a pair makes exclude
    that pair's own nets, so the cache key was unique per pair and every one rebuilt the board in full: 1,010 s of a
    1,327 s B19 pass, 76 percent, against 115 s in the corridor search the pass exists to run."""
    ck = ((gr.G, gr.X0, gr.Y0, gr.NX, gr.NY), tuple(layers), round(half, 5), round(via_r, 5), round(split, 5))
    hit = _ALLMAPS.get(ck)
    if hit is not None and hit[4] == MAP_EPOCH[0]:
        _stamp_new_copper(gr, b, layers, hit[0], hit[1], hit[2], half, via_r, split, hit[3], hit[6])
        return hit
    trk = {L: np.zeros((gr.NY, gr.NX), dtype=np.uint16) for L in layers}
    via_clr = np.zeros((gr.NY, gr.NX), dtype=np.uint16)
    via_holes = np.zeros((gr.NY, gr.NX), dtype=bool)
    idx = {}
    _stamp_board(gr, b, layers, trk, via_clr, via_holes, half, via_r, split, idx)
    seen = set(); _stamp_new_copper(gr, b, layers, trk, via_clr, via_holes, half, via_r, split, seen, idx)
    scratch = ({L: np.zeros((gr.NY, gr.NX), dtype=np.uint16) for L in layers}, np.zeros((gr.NY, gr.NX), dtype=np.uint16))
    rec = [trk, via_clr, via_holes, seen, MAP_EPOCH[0], scratch, idx]
    _ALLMAPS[ck] = rec
    return rec


MAP_CALLS = [0]   # how many times a pair asked for its maps; the seconds are _T["maps"], the counter that already existed


def build_maps(gr, b, layers, nets, half, via_r, split=VIA_SPLIT):
    """Forbidden centreline cells per layer (other-net copper grown by half + CLR) and forbidden via-centre cells (any layer)."""
    MAP_CALLS[0] += 1
    return _build_maps(gr, b, layers, nets, half, via_r, split)


def _build_maps(gr, b, layers, nets, half, via_r, split=VIA_SPLIT):
    if MAP_MODE == "reference" and not MAP_CHECK:
        return _build_maps_reference(gr, b, layers, nets, half, via_r, split)
    rec = _all_counts(gr, b, layers, half, via_r, split)
    all_trk, all_via, holes, _seen, _ep, (own_trk, own_via), idx = rec
    for L in layers: own_trk[L].fill(0)
    own_via.fill(0)
    _stamp_own(gr, layers, set(nets), idx, own_trk, own_via, half, via_r, split)
    # "some net other than this pair's blocks the cell" is a comparison of counts, never a bitwise subtraction: where
    # two nets' grown rasters overlap, clearing the pair's own bits would free a cell the other net blocks.
    trk = {L: all_trk[L] > own_trk[L] for L in layers}
    via = (all_via > own_via) | holes
    _edge_band(gr, trk, via)
    if MAP_CHECK:
        rtrk, rvia = _build_maps_reference(gr, b, layers, nets, half, via_r, split)
        bad = [L for L in layers if not np.array_equal(trk[L], rtrk[L])]
        if bad or not np.array_equal(via, rvia):
            raise SystemExit("PAIR MAP CHECK FAILED for nets %s: layers %s differ, via differs %s (counts against the reference)"
                             % (sorted(nets), bad, not np.array_equal(via, rvia)))
    return trk, via


def _build_maps_reference(gr, b, layers, nets, half, via_r, split=VIA_SPLIT):
    """The per-pair full rebuild, kept as the thing the counted map is checked against (PAIR_MAP_CHECK=1).

    Cached per signature and topped up: a repeat call re-stamps nothing, it stamps only the tracks and vias laid since the last
    one. The caller mutates what it gets (`via1` is shared and written into), so a copy goes out and the cache keeps its own."""
    # Keyed by the grid's IDENTITY, not its address: one Grid per cell size is kept today so id() is safe today, but a
    # freed Grid whose address were reused would match a stale map (round-two red teams, L3).
    ck = ((gr.G, gr.X0, gr.Y0, gr.NX, gr.NY), tuple(layers), frozenset(nets), round(half, 5), round(via_r, 5), round(split, 5))
    hit = _MAPS.get(ck)
    if hit is not None and hit[3] == MAP_EPOCH[0]:
        trk, via, seen = hit[0], hit[1], hit[2]
        n_new = _stamp_tracks(gr, b, layers, nets, half, via_r, split, trk, via, seen)
        if n_new: _edge_band(gr, trk, via)   # the band is re-applied, the stamping cannot have cleared it but the cost is nothing
        return {L: trk[L].copy() for L in layers}, via.copy()
    trk = {L: np.zeros((gr.NY, gr.NX), dtype=bool) for L in layers}; via = np.zeros((gr.NY, gr.NX), dtype=bool)
    for fp in b.GetFootprints():
        for p in fp.Pads():
            pth = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
            if pth: c = p.GetPosition(); d = p.GetDrillSize(); gr.disc(via, mm(c.x), mm(c.y), mm(max(d.x, d.y)) / 2 + 0.2 + 0.30)
            if p.GetNetname() in nets: continue
            pk = "%s.%s@%d,%d" % (fp.GetReference(), p.GetNumber(), p.GetPosition().x, p.GetPosition().y)   # the position is part of the key: a swapped resistor keeps its raster otherwise (D9, 8 Sep 2026 12:59)
            for L in layers:
                if p.IsOnLayer(L): gr.poly(trk[L], p.GetEffectivePolygon(L), CLR + half, key=(pk, L))
                if pth and p.IsOnLayer(L): c = p.GetPosition(); d = p.GetDrillSize(); gr.disc(trk[L], mm(c.x), mm(c.y), mm(max(d.x, d.y)) / 2 + HOLE_CLR + half)
            anyL = next((L for L in _ALL.values() if p.IsOnLayer(L)), None)   # any copper layer: a via is a hole through every layer
            if anyL is not None or pth: gr.poly(via, p.GetEffectivePolygon(anyL if anyL is not None else pcbnew.F_Cu), CLR + via_r + split, key=(pk, "via", anyL))
    seen = set(); _stamp_tracks(gr, b, layers, nets, half, via_r, split, trk, via, seen)
    # Footprint-local rule areas count too: they are not in b.Zones(), so a keep-out that belongs to a part (the E72's antenna clearance,
    # a connector's own no-track area) was invisible here while `prefanout.py` already read them. B17's pre-route came back with five
    # items_not_allowed, all of them pair copper laid straight through one (9 Sep 2026 02:20, MESHSAT-862).
    for z in list(b.Zones()) + [z for fp in b.GetFootprints() for z in fp.Zones()]:
        if z.GetIsRuleArea():
            zk = "zone.%s" % z.m_Uuid.AsString() if hasattr(z, "m_Uuid") else "zone.%d" % id(z)
            for L in layers:
                if z.IsOnLayer(L) and z.GetDoNotAllowTracks(): gr.poly(trk[L], z.Outline(), CLR + half, key=(zk, L))
            if z.GetDoNotAllowVias(): gr.poly(via, z.Outline(), CLR + via_r + split, key=(zk, "via"))
    _edge_band(gr, trk, via)
    _MAPS[ck] = [trk, via, seen, MAP_EPOCH[0]]
    return {L: trk[L].copy() for L in layers}, via.copy()


def _edge_band(gr, trk, via):
    """The board's outer band: no centreline and no via within 0.8 mm of the grid edge."""
    m = int(0.8 / gr.G) + 12
    for M in list(trk.values()) + [via]: M[:m, :] = True; M[-m:, :] = True; M[:, :m] = True; M[:, -m:] = True


def _track_key(t):
    """A stable identity for a track: SWIG hands out a fresh proxy per iteration, so `is` and id() never match (5 Sep 2026)."""
    a, e = t.GetStart(), t.GetEnd()
    return (t.GetClass(), a.x, a.y, e.x, e.y, t.GetLayer(), t.GetNetCode(),
            t.GetDrillValue() if t.GetClass() == "PCB_VIA" else t.GetWidth())


def _stamp_tracks(gr, b, layers, nets, half, via_r, split, trk, via, seen):
    """Stamp every track not yet in `seen` into the maps. Returns how many were new."""
    n = 0
    for t in b.GetTracks():
        k = _track_key(t)
        if k in seen: continue
        seen.add(k); n += 1
        if t.GetClass() == "PCB_VIA": c = t.GetPosition(); gr.disc(via, mm(c.x), mm(c.y), mm(t.GetDrillValue()) / 2 + 0.2 + 0.30 + split)
        if t.GetNetname() in nets: continue
        if t.GetClass() == "PCB_VIA":
            c = t.GetPosition(); r = mm(t.GetWidth(pcbnew.F_Cu)) / 2
            for L in layers: gr.disc(trk[L], mm(c.x), mm(c.y), r + CLR + half)
        else:
            a, e = t.GetStart(), t.GetEnd(); r = mm(t.GetWidth()) / 2; L = t.GetLayer()
            if L in trk: gr.seg(trk[L], mm(a.x), mm(a.y), mm(e.x), mm(e.y), r + CLR + half)
            gr.seg(via, mm(a.x), mm(a.y), mm(e.x), mm(e.y), r + CLR + via_r + split)
    return n

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
    # OFF until it is measured on a board, because "it must be the same" is what the selftest is for and a pair
    # count is what the knob is for.
    if os.environ.get("PAIR_FAST_STUBS", "0") != "0":
        wi0, wi1 = max(0, imin), min(passable.shape[0] - 1, imax)
        wj0, wj1 = max(0, jmin), min(passable.shape[1] - 1, jmax)
        if not (wi0 <= si <= wi1 and wj0 <= sj <= wj1 and wi0 <= gi <= wi1 and wj0 <= gj <= wj1): return None
        win = np.ascontiguousarray(passable[wi0:wi1 + 1, wj0:wj1 + 1])[None, :, :]
        novia = np.ones(win.shape[1:], dtype=bool)   # every cell forbids a via: one layer, no layer change exists
        path_, nexp_, _why_ = pairsearch.search(win, novia, None, [(0, si - wi0, sj - wj0)], (0, gi - wi0, gj - wj0),
                                                max_exp=400000, fast=_FAST_SEARCH)
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
        if n > 400000: break
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

_MITRE = float(os.environ.get("PAIR_MITRE_LIMIT", "1.2"))   # above this multiple of d the outer join is arced, not mitred
def _isect(a, b, c, d):
    """The crossing point of segments a-b and c-d when they properly cross (never at a shared endpoint), else None."""
    r = (b[0] - a[0], b[1] - a[1]); s_ = (d[0] - c[0], d[1] - c[1])
    den = r[0] * s_[1] - r[1] * s_[0]
    if abs(den) < 1e-12: return None
    t = ((c[0] - a[0]) * s_[1] - (c[1] - a[1]) * s_[0]) / den
    u = ((c[0] - a[0]) * r[1] - (c[1] - a[1]) * r[0]) / den
    if not (1e-9 < t < 1 - 1e-9 and 1e-9 < u < 1 - 1e-9): return None
    return (a[0] + t * r[0], a[1] + t * r[1])


def deloop(pts):
    """Cut the self-intersections out of an offset polyline (10 September 2026, B19).

    A turn whose radius is smaller than the offset d folds the INNER leg back on itself: the offset polyline crosses
    itself, and where the two legs of a pair do that they cross each other, which is a short. Nine of B19's 113 pairs
    were rolled back for exactly that (three crossings each on HDMI3_CK, D0, D1, D2 and HDMIM_D0), and D10's USB3
    shipped two tracks_crossing violations from it before the crossing test caught them. The loop is a fold of at most
    d, so cutting it at the crossing point shortens the leg by well under a tenth of a millimetre and leaves the ends
    where they were."""
    out = list(pts); i = 0
    while i < len(out) - 2:
        j = len(out) - 2
        while j > i + 1:
            X = _isect(out[i], out[i + 1], out[j], out[j + 1])
            if X is not None:
                out = out[:i + 1] + [X] + out[j + 1:]
                break
            j -= 1
        i += 1
    return out


def fp_centre(fp):
    """The centre of a footprint's pads, in mm.

    NOT `fp.GetPosition()`, which is the footprint's ORIGIN: on every connector in this tree that origin is PIN 1,
    not the body. It is used to decide which way is "out" of a pair's station, and for a pair on the END row of a
    header the origin lies exactly ON the station line, so the dot product is zero, the test cannot flip anything
    and the default direction points straight INTO the pin field. Measured on D's /USB_D8 on 11 September 2026: the
    corridor end came out at (58.80, 85.35), between the two columns of J_HARN1 and one row inside it, and the fan
    into the pads had no path from there. The pads' own centre is (58.5, 92.0) for that part, which puts "out" north,
    off the end of the connector, where the board is empty."""
    pts = [(p.GetPosition().x, p.GetPosition().y) for p in fp.Pads()]
    if not pts: return fp.GetPosition().x / 1e6, fp.GetPosition().y / 1e6
    return sum(x for x, _ in pts) / len(pts) / 1e6, sum(y for _, y in pts) / len(pts) / 1e6


def offset_polyline(pts, d):
    """Offset a polyline (list of (x, y) mm) by d to its left; mitred joins."""
    if len(pts) < 2: return list(pts)
    segs = []
    for k in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[k], pts[k + 1]; dx, dy = bx - ax, by - ay; ln = math.hypot(dx, dy) or 1.0; nx, ny = -dy / ln * d, dx / ln * d
        segs.append(((ax + nx, ay + ny), (bx + nx, by + ny)))
    out = [segs[0][0]]
    for k in range(len(segs) - 1):
        (p1, p2), (p3, p4) = segs[k], segs[k + 1]
        d1 = (p2[0] - p1[0], p2[1] - p1[1]); d2 = (p4[0] - p3[0], p4[1] - p3[1]); den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-9: out.append(p2); continue
        t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / den; ix, iy = p1[0] + t * d1[0], p1[1] + t * d1[1]
        # 9 September 2026 (B19): the limit was 1.5, and a RIGHT ANGLE puts the mitre point at d times the square root of
        # two, 1.414, so every 90 degree corner took the mitre and stood 41 percent further from the centreline than the
        # straights do. `pair_report.py` says 46 of 160 failed attempts are the legs failing to clear, and a corridor that
        # fits along its straights and not at its corners is what that looks like. The arc is strictly closer to the
        # centreline than the mitre, so lowering the limit to 1.2 can only help; PAIR_MITRE_LIMIT restores the old value.
        if t > 1.0 and math.hypot(ix - p2[0], iy - p2[1]) > _MITRE * abs(d):   # the outer side of a bend: an arc around the corner keeps the legs parallel; the inner side keeps its mitre
            cx, cy = pts[k + 1]; a0 = math.atan2(p2[1] - cy, p2[0] - cx); a1 = math.atan2(p3[1] - cy, p3[0] - cx); da = a1 - a0
            while da > math.pi: da -= 2 * math.pi
            while da < -math.pi: da += 2 * math.pi
            n = max(2, int(abs(da) / math.radians(30)))
            for q in range(n + 1):
                a = a0 + da * q / n; pt = (cx + abs(d) * math.cos(a), cy + abs(d) * math.sin(a))
                if math.hypot(pt[0] - out[-1][0], pt[1] - out[-1][1]) >= 0.05: out.append(pt)
        else: out.append((ix, iy))
    out.append(segs[-1][1]); return deloop(out)

# 11 September 2026: the B19 arm's own profile said 703 s in the maps, 108 s in the corridor search and 769 s
# ELSEWHERE, which is half a pass in the one bucket nothing has ever measured. Three more wrappers name most of
# it: the stub search that reaches a pad from a corridor end, the leg offsets that legs_clear walks, and the
# stamping of laid copper into the maps. The cost is one time.time() per call of five functions.
stub_path = _timed("stubs", stub_path)
offset_polyline = _timed("legs", offset_polyline)
Grid.seg = _timed("stamp", Grid.seg)
Grid.disc = _timed("stamp", Grid.disc)


def main(a):
    if not a: print(__doc__); return 2
    board = a[0]; test = "--test" in a; g = float(a[a.index("--grid") + 1]) if "--grid" in a else 0.1
    _GLONG = float(os.environ.get("PAIR_GRID_LONG", "0")) or 0.0   # a coarser grid for the long pairs (0 = off)
    _LONG_MM = float(os.environ.get("PAIR_LONG_MM", "120"))
    # The pair classes live in the PROJECT file, not the board. A board without one, or with one that carries no
    # netclass assignments, has no pairs by construction, and this tool then printed "0 of 0 pairs laid" and exited 0.
    # A pre-router that finds no pairs and reports success is the exact shape this pipeline spent two days removing,
    # and it is easy to hit: `out/<name>-placed.kicad_pcb` has no project file beside it, and a project directory
    # copied for a route carries a stale one (the B19 trap of 9 September, appendix 32.91). It refuses now.
    # 11 September 2026 (MESHSAT-862).
    pro = os.path.splitext(board)[0] + ".kicad_pro"
    if not os.path.exists(pro):
        sys.stderr.write("pair_preroute: no project file at %s. The pair classes are in it, so this board has no pairs to lay,\n"
                         "  which is not the same as having laid them all. Run on the board in its project directory, or copy\n"
                         "  the .kicad_pro beside it.\n" % pro)
        # exit 2, not 1: a caller that sees 1 reads "a pair did not lay" and may retry the same board for ever.
        # This is a tooling error and nothing about it will change on a retry (reviewer, 11 September 2026).
        raise SystemExit(2)
    d = json.load(open(pro))
    assign = d.get("net_settings", {}).get("netclass_assignments") or {}
    classes = {c["name"]: c for c in (d.get("net_settings", {}).get("classes") or [])}
    if not assign:
        sys.stderr.write("pair_preroute: %s carries no netclass_assignments, so every net reads as Default and no pair\n"
                         "  would be found. The placement generator writes them into the project file OF THE DIRECTORY IT RUNS IN;\n"
                         "  a copied project directory needs that file copied too.\n" % pro)
        raise SystemExit(2)
    b = pcbnew.LoadBoard(board); gr = Grid(b, g); _grids = {g: gr}
    # Every position this pass changes, named at the end. The tool exchanges two passives when a station's fans cross,
    # and on D the routed board came back with R12 and R13 exchanged while the pass log named three swaps, none of them
    # those two: a part had moved and nothing said so. A move that decides whether the OTHER side of the station can be
    # routed (the hub pin to its series resistor, D's last open) must be in the report (11 September 2026).
    _POS0 = {f_.GetReference(): (f_.GetPosition().x, f_.GetPosition().y) for f_ in b.GetFootprints()}
    def cls_of(n):
        c = assign.get(n) or assign.get("/" + n.lstrip("/")) or assign.get(n.lstrip("/")); return (c[0] if isinstance(c, list) and c else c) or "Default"
    want_classes = set(a[a.index("--classes") + 1].split(",")) if "--classes" in a else {"USB", "DIFF100", "PCIE", "HDMI"}
    layers = [_ALL[x] for x in (a[a.index("--layers") + 1].split(",") if "--layers" in a else os.environ.get("PAIR_LAYERS", "F.Cu,B.Cu").split(",")) if x in _ALL]
    # the hop layers carry only the dives and the stubs' hops, never a corridor run: on the 7628 four-layer stack a 0.30/0.20 pair on In2 reads 137 ohm
    # against In1 across the 1.065 mm core (D9's USB_D8 took 42 mm of In2 in its corridor, 8 Sep 2026 14:44); the class geometry holds on the corridor layers only
    hops = [_ALL[x] for x in (a[a.index("--hop-layers") + 1].split(",") if "--hop-layers" in a else os.environ.get("PAIR_HOP_LAYERS", "").split(",")) if x in _ALL and _ALL[x] not in layers]
    maplayers = layers + hops
    def hop_of(L): return next((L2 for L2 in hops + layers if L2 != L), None)   # a hop layer first, else another corridor layer
    names = {str(n): n for n in b.GetNetInfo().NetsByName().keys()}
    stems = sorted({n[:-2] for n in names if n.endswith("_P") and n[:-2] + "_N" in names})
    suffixed = sorted({n[:-3] for n in names if n.endswith("_PR") and n[:-3] + "_NR" in names})   # USB1_PR / USB1_NR (the codec side of D9's port 1): P and N with a suffix
    pair_names = {st: (st + "_P", st + "_N") for st in stems}; pair_names.update({st + "_R": (st + "_PR", st + "_NR") for st in suffixed}); stems = stems + [st + "_R" for st in suffixed]
    if "--pairs" in a: stems = [s for s in stems if s.lstrip("/") in set(a[a.index("--pairs") + 1].split(","))]
    stems = [s for s in stems if cls_of(pair_names.get(s, (s + "_P", s + "_N"))[0]) in want_classes]
    # The long pairs go first (9 September 2026). This tool lays greedily and never rips up, so whichever pair is laid first takes the room
    # and the rest fit around it; alphabetical order decided that, which is no order at all. The span of a pair's own pads is a cheap proxy
    # for how hard it will be: a 90 mm PCIe run across B18 has one route and a 4 mm hub link has hundreds, so the long one is laid while the
    # board is still empty. Measured on B18 in the same build: PAIR_ORDER=name restores the old order for comparison.
    def _span(st):
        pn_, nn_ = pair_names.get(st, (st + "_P", st + "_N"))
        want = {pn_.lstrip("/"), nn_.lstrip("/")}
        pts = [q.GetPosition() for f in b.GetFootprints() for q in f.Pads() if q.GetNetname().lstrip("/") in want]
        if len(pts) < 2: return 0.0
        return max(math.hypot(u.x - v.x, u.y - v.y) for u in pts for v in pts) / 1e6
    # 10 September 2026: an explicit order, one stem per line, for the multi-pass driver `pair_passes.py`. The isolation test
    # of 32.95 proved the order decides: a pair that fails in the pass lays when it is alone on the board. Ripping the room
    # back from its neighbours does not work (32.98), so the other way round it is: the pairs that failed go FIRST next time.
    _ordf = os.environ.get("PAIR_ORDER_FILE")
    if _ordf and os.path.exists(_ordf):
        _want = [l.strip().lstrip("/") for l in open(_ordf) if l.strip()]
        _rank = {n: i for i, n in enumerate(_want)}
        stems = sorted(stems, key=lambda st: (_rank.get(st.lstrip("/"), 10 ** 6), -_span(st), st))
        print("pair_preroute: order from %s: %d named first, then the longest of the rest" % (os.path.basename(_ordf), len(_want)))
    elif os.environ.get("PAIR_ORDER", "span") == "span":
        stems = sorted(stems, key=lambda st: (-_span(st), st))
        if stems: print("pair_preroute: %d pairs, longest first (%s spans %.0f mm, %s spans %.0f mm)" % (len(stems), stems[0], _span(stems[0]), stems[-1], _span(stems[-1])))
    laid = 0; swapped = set()
    # 9 September 2026 (B19): the outcome lines used to be held until the pass ended, so a run of 113 pairs showed nothing
    # for hours and could not be steered or timed. They are printed as they happen now, and the same list is still summarised
    # at the end, so a driver watching the log can count LAID and FAIL while the pass is running.
    class _Report(list):
        def append(self, line):
            list.append(self, line); print("pair_preroute: " + line, flush=True)
    report = _Report()
    # 10 September 2026, rip-up and retry (MESHSAT-862), OFF by default on its own measurement (see PAIR_RIPUP below). /HOST2_1RX, /HDMIO_D1 and /HDMIO_CK
    # all FAIL in the full pass with "the legs clear no smoothing of the centreline" and all three LAY when they are the only pair
    # routed on the same board. What stops them is copper this tool laid for an earlier pair, not the placement and not the corner
    # geometry: it lays greedily and never rips up, so whichever pair went first took the room. When a section fails now, the laid
    # pairs whose copper lies in that section's corridor are taken off the board, the failed pair is queued to be laid again first
    # and they are queued behind it. PAIR_RIPUP=0 restores the greedy pass, which is how the two arms are compared.
    # MEASURED 10 September 2026 and OFF by default: rip-up as written LOSES pairs. On B19's placed board the greedy pass lays
    # 38 of 113; with rip-up the tool laid 224 times, spent 47 rip-up events and ended at 29, because a ripped pair is not
    # guaranteed to fit again once its room has been taken by the pair that ripped it, and nothing checks that the episode paid.
    # The episode has to become a trial that is accepted only when it leaves more pairs laid than it found; until it is, the flag
    # stays off (PAIR_RIPUP=1 to reproduce the measurement).
    LEG_EXACT = os.environ.get("PAIR_LEG_EXACT", "0") != "0"       # re-test a blocked leg point against the polygons before refusing the pair
    # A station swap exchanges two identical passives so the pair's own fans stop crossing. It is judged on the side the
    # pair is laid from and NOT on the other side of the same two parts, and on D that is what left the board one open:
    # round one swapped R12 and R13, which put the hub's DM1 pin across from the resistor of DP1, and /HUB_DM1 came back
    # with not one track laid on it. Round three of the same run did not swap them and routed that net. PAIR_SWAP=0 turns
    # every swap off, which is how the cost of the swap is measured rather than argued (11 September 2026).
    SWAP_OK = os.environ.get("PAIR_SWAP", "1") != "0"
    SWAP_BOTH = os.environ.get("PAIR_SWAP_BOTH_SIDES", "0") != "0"   # refuse a swap that crosses the parts' OTHER pads
    RIPUP = int(os.environ.get("PAIR_RIPUP", "0"))                 # rip-up events one pair may trigger
    RIP_MARGIN = float(os.environ.get("PAIR_RIP_MARGIN", "4.0"))   # mm from the failed section's line for a piece to count as in the way
    RIP_MAX = int(os.environ.get("PAIR_RIP_MAX", "6"))             # laid pairs taken off the board per event
    RIP_TOTAL = int(os.environ.get("PAIR_RIP_TOTAL", "60"))        # rip-up events in the whole pass (the pass is bounded by this)
    on_board = {}     # stem -> (pieces, stripped escapes) of a pair that is laid and can be ripped
    rip_events = {}   # stem -> how often this pair has ripped others
    rip_done = [0]
    episode = [None]  # the open rip-up episode: what it took off the board, and how many pairs were laid before it
    cur_seg = [0.0, 0.0, 0.0, 0.0]   # the section the corridor search is working on, for the rip-up window

    def _seg_d(px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy
        t = 0.0 if L2 <= 1e-9 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
        return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))

    def _nearest_edge(x, y, L, net, limit=3.0):
        """Distance in mm from a point to the nearest obstacle EDGE on one layer, ignoring `net`, or None past `limit`.

        Edges, not centres: the maps rasterise a pad by its polygon, so a centre distance is the wrong number to compare
        with them and reads as a pad "at 1.85 mm" blocking a cell it cannot reach (11 September 2026). Bounded by `limit`
        so the scan is a local one; the caller decides what distance is enough."""
        best = None
        pt = pcbnew.VECTOR2I(FromMM(x), FromMM(y))
        for f in b.GetFootprints():
            bb = f.GetBoundingBox(False, False)
            if mm(bb.GetLeft()) - limit > x or mm(bb.GetRight()) + limit < x or mm(bb.GetTop()) - limit > y or mm(bb.GetBottom()) + limit < y: continue
            for q in f.Pads():
                if q.GetNetname() == net or not q.IsOnLayer(L): continue
                if abs(mm(q.GetPosition().x) - x) > limit + 5 or abs(mm(q.GetPosition().y) - y) > limit + 5: continue
                # A pad whose polygon cannot be taken is an obstacle of UNKNOWN extent, so it answers 0.0 and the caller
                # refuses. The centre distance was the obvious fallback and it is larger than the edge distance, which
                # would accept copper the map had blocked: a silent fallback in the unsafe direction, the class of defect
                # the record has caught twice (the inflate fallback, the map expression).
                try: d_ = mm(int(q.GetEffectivePolygon(L).Distance(pt)))
                except Exception: d_ = 0.0
                if best is None or d_ < best: best = d_
        for t in b.GetTracks():
            if t.GetNetname() == net: continue
            if t.GetClass() == "PCB_VIA":
                d_ = math.hypot(mm(t.GetPosition().x) - x, mm(t.GetPosition().y) - y) - mm(t.GetDrillValue()) / 2 - 0.05
            else:
                if t.GetLayer() != L: continue
                d_ = _seg_d(x, y, mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetEnd().x), mm(t.GetEnd().y)) - mm(t.GetWidth()) / 2
            if d_ < limit and (best is None or d_ < best): best = d_
        for z in list(b.Zones()) + [z for fp in b.GetFootprints() for z in fp.Zones()]:
            if not (z.GetIsRuleArea() and z.IsOnLayer(L) and z.GetDoNotAllowTracks()): continue
            d_ = mm(int(z.Outline().Distance(pt)))
            if d_ < limit and (best is None or d_ < best): best = d_
        return best

    def _what_is_at(x, y, L, net):
        """The copper nearest to a point on one layer, named (10 September 2026). A debug line that says a leg hits `an
        obstacle` and does not say WHICH cost an evening once already (8 Sep, the escape-depth theory); the rule of the
        record is that a gate which strips or refuses copper names what it hit."""
        best = None
        for f in b.GetFootprints():
            for q in f.Pads():
                if q.GetNetname() == net or not q.IsOnLayer(L): continue
                d_ = math.hypot(mm(q.GetPosition().x) - x, mm(q.GetPosition().y) - y)
                if best is None or d_ < best[0]: best = (d_, "pad %s.%s (%s)" % (f.GetReference(), q.GetNumber(), q.GetNetname() or "no net"))
        for t in b.GetTracks():
            if t.GetNetname() == net: continue
            if t.GetClass() == "PCB_VIA":
                d_ = math.hypot(mm(t.GetPosition().x) - x, mm(t.GetPosition().y) - y); what = "via (%s)%s" % (t.GetNetname() or "no net", " locked" if t.IsLocked() else "")
            else:
                if t.GetLayer() != L: continue
                d_ = _seg_d(x, y, mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetEnd().x), mm(t.GetEnd().y)); what = "track (%s)%s" % (t.GetNetname() or "no net", " locked" if t.IsLocked() else "")
            if best is None or d_ < best[0]: best = (d_, what)
        # 11 September 2026: zones and rule areas were not scanned at all, so a leg stopped by a pour or a keep-out was
        # reported as the nearest PAD, which reads as a pad problem and is not one. It named "pad U2.1 at 1.85 mm" for a
        # cell no pad could reach, and 1.85 mm against a forbidden radius of about 1.35 is the tell that the answer was
        # the wrong object. The rule of the record is that a tool which refuses copper names what it hit.
        # 11 September 2026: RULE AREAS were not scanned at all, so a leg stopped by a keep-out was reported as the nearest
        # PAD, which reads as a pad problem and is not one. It named "pad U2.1 at 1.85 mm" for a cell no pad could reach, and
        # 1.85 mm against a forbidden radius near 1.35 is the tell that the answer was the wrong object. Footprint-local rule
        # areas are NOT in b.Zones() (the same trap build_maps closed on 9 September), so both lists are walked. A copper pour
        # is deliberately not named: build_maps stamps rule areas only, because a fill yields to a track and is no obstacle.
        pt = pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))
        for z in list(b.Zones()) + [z for fp in b.GetFootprints() for z in fp.Zones()]:
            if not (z.GetIsRuleArea() and z.IsOnLayer(L) and z.GetDoNotAllowTracks()): continue
            d_ = mm(int(z.Outline().Distance(pt)))
            what = "rule area %s of %s" % (z.GetZoneName() or "(unnamed)", z.GetParentFootprint().GetReference() if z.GetParentFootprint() else "the board")
            if best is None or d_ < best[0]: best = (d_, what)
        return "nothing within reach" if best is None else "%s at %.2f mm" % (best[1], best[0])

    def _in_way(pcs, x1, y1, x2, y2):
        """The distance from a laid pair's copper to the failed section's straight line (mm), 1e9 when it has none."""
        d = 1e9
        for t_ in pcs:
            if t_.GetClass() == "PCB_TRACK":
                d = min(d, _seg_d(mm(t_.GetStart().x), mm(t_.GetStart().y), x1, y1, x2, y2), _seg_d(mm(t_.GetEnd().x), mm(t_.GetEnd().y), x1, y1, x2, y2))
            else:
                d = min(d, _seg_d(mm(t_.GetPosition().x), mm(t_.GetPosition().y), x1, y1, x2, y2))
            if d <= RIP_MARGIN: break
        return d
    def settle_episode():
        """A rip-up episode is a TRIAL: it is kept only when it leaves more pairs laid than it found (10 September 2026).

        Measured without this: 47 episodes, 224 lays and 29 of B19's 113 pairs against the greedy pass's 38. A ripped pair is
        not guaranteed to fit again once the pair that ripped it has taken the room, so an episode that does not pay must be
        undone in full: what the members laid comes off, what was ripped goes back."""
        nonlocal laid
        ep = episode[0]
        if ep is None: return
        if laid <= ep["laid_before"]:
            for st2 in list(ep["members"]):
                if st2 in on_board:
                    pcs2, str2 = on_board.pop(st2)
                    for t_ in pcs2: board_remove(b, t_)
                    for t_ in str2: b.Add(t_)
                    laid -= 1
            for st2, (pcs2, str2) in ep["saved"].items():
                for t_ in pcs2: b.Add(t_)
                for t_ in str2: board_remove(b, t_)
                on_board[st2] = (pcs2, str2); laid += 1
            report.append("RIPUP %s: the episode ended with %d pairs laid against %d before it; every piece is put back" % (ep["trigger"], laid, ep["laid_before"]))
        else:
            report.append("RIPUP %s: the episode ended with %d pairs laid against %d before it; kept" % (ep["trigger"], laid, ep["laid_before"]))
        episode[0] = None

    def pinned(f):
        """A footprint whose pads already hold a track end (a section laid for another stem of the same nets, an escape) must not be moved: the second swap of
        R26/R27 on D9 (8 Sep 2026 12:20) left four locked pieces on pads of the wrong net."""
        return any(p.HitTest(t.GetStart()) or p.HitTest(t.GetEnd()) for t in b.GetTracks() if t.GetClass() == "PCB_TRACK" for p in f.Pads())

    def _seg_cross(a1, a2, b1, b2):
        def ccw(p, q, r): return (r[1] - p[1]) * (q[0] - p[0]) > (q[1] - p[1]) * (r[0] - p[0])
        return ccw(a1, b1, b2) != ccw(a2, b1, b2) and ccw(a1, a2, b1) != ccw(a1, a2, b2)

    def swap_breaks_other_side(fa, fb, pair_nets):
        """Would exchanging these two passives make the connections on their OTHER pads cross?

        A station swap is decided by the pair's own fans and the other side of the same two parts is not looked
        at. On D that cost the board its only open: exchanging R12 and R13 put the hub's DM1 pin across from
        DP1's resistor, the two hub-side connections crossed in a 2.7 mm gap, and /HUB_DM1 came back with not
        one track on it (11 September 2026, appendix 32.128). This asks the question the swap never asked.
        True means the swap introduces a crossing that is not there now, which is a reason to refuse it."""
        def _signal(n_):
            # A plane or rail pad has no single counterpart to cross with: its "nearest pad of the same net" is
            # whichever GND pad happens to be closest, and a crossing test on that is noise. Measured: without this
            # the guard refused four of D's swaps and cost the board two pairs (5 of 5 down to 3 of 5).
            k_ = n_.lstrip("/")
            return bool(k_) and k_ != "GND" and not k_.startswith(("+", "VBAT", "CELL", "VBUS", "PACK", "FUSED", "VIN", "PV_", "TRK_"))
        def other(f_):
            for q in f_.Pads():
                if q.GetNetname() not in pair_nets and _signal(q.GetNetname()): return q
            return None
        qa, qb = other(fa), other(fb)
        if qa is None or qb is None: return False
        def mate(q):
            """The nearest pad of the same net on another footprint: what that pad has to reach."""
            best = None
            for f2 in b.GetFootprints():
                if f2.GetReference() in (fa.GetReference(), fb.GetReference()): continue
                for p2 in f2.Pads():
                    if p2.GetNetname() != q.GetNetname(): continue
                    d_ = dist_p(q, p2)
                    if best is None or d_ < best[0]: best = (d_, (mm(p2.GetPosition().x), mm(p2.GetPosition().y)))
            return None if best is None else best[1]
        ma, mb = mate(qa), mate(qb)
        if ma is None or mb is None: return False
        pa_ = (mm(qa.GetPosition().x), mm(qa.GetPosition().y)); pb_ = (mm(qb.GetPosition().x), mm(qb.GetPosition().y))
        # after the swap each pad moves by the vector between the two footprint origins
        da = (mm(fb.GetPosition().x) - mm(fa.GetPosition().x), mm(fb.GetPosition().y) - mm(fa.GetPosition().y))
        pa2 = (pa_[0] + da[0], pa_[1] + da[1]); pb2 = (pb_[0] - da[0], pb_[1] - da[1])
        now = _seg_cross(pa_, ma, pb_, mb); after = _seg_cross(pa2, ma, pb2, mb)
        if after and not now:
            report.append("SWAP-REFUSED %s and %s: the swap uncrosses this pair's fans and CROSSES %s and %s on their other pads"
                          % (fa.GetReference(), fb.GetReference(), qa.GetNetname(), qb.GetNetname()))
        return after and not now

    def dist_p(p, q): return math.hypot(p.GetPosition().x - q.GetPosition().x, p.GetPosition().y - q.GetPosition().y) / 1e6
    pre_vias = []   # the locked vias present before a pair is laid (its own end vias must not become anchors of its next section)
    _pitch = {}
    def pitch_of(f):
        """The smallest centre distance between two SMD pads of the part (mm); 1e9 without two."""
        k = f.GetReference()
        if k not in _pitch:
            ps = [q.GetPosition() for q in f.Pads() if q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]; best = 1e9
            for i in range(len(ps)):
                for j in range(i + 1, len(ps)):
                    dd = math.hypot(ps[i].x - ps[j].x, ps[i].y - ps[j].y) / 1e6
                    if 0 < dd < best: best = dd
            _pitch[k] = best
        return _pitch[k]
    ROW_PITCH = 0.45   # a 0.4 mm receptacle row keeps escape.py's CM5IO scheme: the legs end at the escape via, never in the pad (B17, 8 Sep 2026 13:35)
    def row_scheme(f):
        """escape.py's own ROWS04 condition, kept in step with it: a 0.4 mm row, or a 0.5 mm row of 40 pads or more (a card socket),
        keeps its escapes and the escape via is where a pair leg ends. Out of step, the pre-router aims at pads that sit behind a wall
        of escape vias and reports "the legs clear no smoothing of the centreline": 57 of B17's 99 pairs (8 Sep 2026 19:55)."""
        pt = pitch_of(f); n = sum(1 for q in f.Pads() if q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD)
        return pt <= ROW_PITCH or (pt <= 0.5 and n >= 40)
    # 10 September 2026 (B19): PAIR_ENTRY_VIA=1 ends a leg at an IC's escape via instead of stripping the escape and entering
    # the pad. Measured because /HDMI1_D0 fails alone on the board with "no stub path at U3": the pad sits behind the picket of
    # the OTHER nets' escape vias, and stripping had just removed the one target this leg could still have reached. It applies
    # to a fanned part of eight SMD pads or more, which is escape.py's own fan condition; a passive couple keeps its pads.
    ENTRY_VIA = os.environ.get("PAIR_ENTRY_VIA", "0") == "1"
    via_entry_stems = set()   # pairs that failed once with the legs entering the pads and are laid again ending at the escape vias
    SLACK = float(os.environ.get("PAIR_CORRIDOR_SLACK", "0.12"))
    SLACK_SLIM = float(os.environ.get("PAIR_CORRIDOR_SLACK_SLIM", "0.05"))
    slim_stems = set()   # pairs that found no corridor at the measured slack and are searched again at the slim one

    def via_entry(f):
        return (ENTRY_VIA or stem in via_entry_stems) and sum(1 for q in f.Pads() if q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD) >= 8

    def anchor(p):
        """The pad: (x, y, layer or None for a via, object). A pad of a 0.4 mm row is anchored at its escape via (a locked via of its net within 3 mm, present before the pair was laid)."""
        pth = p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH)
        L = None if pth else next((L for L in _ALL.values() if p.IsOnLayer(L)), None)   # the pad's own copper layer (a through-hole pad is on every layer)
        if not pth and (row_scheme(p.GetParentFootprint()) or via_entry(p.GetParentFootprint())):
            vs = [v for v in pre_vias if v.GetNetname() == p.GetNetname() and math.hypot(v.GetPosition().x - p.GetPosition().x, v.GetPosition().y - p.GetPosition().y) < 3e6]
            if vs:
                v = min(vs, key=lambda v: math.hypot(v.GetPosition().x - p.GetPosition().x, v.GetPosition().y - p.GetPosition().y))
                return (mm(v.GetPosition().x), mm(v.GetPosition().y), None, v)
        return (mm(p.GetPosition().x), mm(p.GetPosition().y), L, p)

    # ===================================================================== negotiated congestion (10 September 2026, MESHSAT-862)
    # The measured plateau of 32.98 is a greedy-order plateau: whichever pair is laid first takes the room, and taking it back
    # by ripping the neighbours never pays (106 episodes, none kept). The way a router actually solves this is PathFinder's
    # negotiation: every pair routes as if it owned the board, cells used by more than one pair get a HISTORY cost, and the
    # iteration repeats until no cell is shared. `pair_negotiate.py` drives it; this tool does one half-iteration at a time.
    #   PAIR_PLAN_MODE=plan  search only, lay nothing, write the corridors and the cells two pairs both wanted
    #   PAIR_HIST_IN=<npz>   the history rasters of the iterations before this one
    #   PAIR_PRESENT=<w>     the weight of the cells THIS iteration has already given away
    #   PAIR_PLAN_OUT=<json> where the corridors go; PAIR_PLAN_IN=<json> lays a negotiated plan instead of searching
    PLAN_MODE = os.environ.get("PAIR_PLAN_MODE", "") == "plan"
    PRESENT_W = float(os.environ.get("PAIR_PRESENT", "0"))
    _li = {L: i for i, L in enumerate(layers)}
    NEG_COST = None; NEG_OCC = None
    _hist_in = os.environ.get("PAIR_HIST_IN")
    if PLAN_MODE or _hist_in:
        NEG_COST = {i: np.zeros((gr.NY, gr.NX), dtype=np.float32) for i in range(len(layers))}
        NEG_OCC = {i: np.zeros((gr.NY, gr.NX), dtype=np.int16) for i in range(len(layers))}
        if _hist_in and os.path.exists(_hist_in):
            _h = np.load(_hist_in)
            for _k, _ii, _jj, _vv in zip(_h["L"], _h["i"], _h["j"], _h["v"]):
                if int(_k) in NEG_COST: NEG_COST[int(_k)][int(_ii), int(_jj)] += float(_vv)
            print("pair_preroute: history from %s: %d cell(s) carry a cost" % (os.path.basename(_hist_in), len(_h["v"])))
    plan_out = {}   # stem -> [[[layer index, i, j], ...], ...] one list per section
    plan_in = {}
    _pin = os.environ.get("PAIR_PLAN_IN")
    if _pin and os.path.exists(_pin):
        plan_in = json.load(open(_pin))
        print("pair_preroute: laying the negotiated plan of %s (%d pairs)" % (os.path.basename(_pin), len(plan_in)))

    def neg_stamp(cells, half_mm):
        """Give this corridor's envelope to the pair that just took it: occupancy up by one, and the present cost with it."""
        if NEG_OCC is None: return
        for Lidx in {c[0] for c in cells}:
            run = [c for c in cells if c[0] == Lidx]
            if not run: continue
            tmp = np.zeros((gr.NY, gr.NX), dtype=bool)
            for a_, b_ in zip(run[:-1], run[1:]):
                x1, y1 = gr.xy(a_[2], a_[1]); x2, y2 = gr.xy(b_[2], b_[1])
                if abs(a_[1] - b_[1]) + abs(a_[2] - b_[2]) > 4: continue   # a layer change is not a run
                gr.seg(tmp, x1, y1, x2, y2, half_mm)
            NEG_OCC[Lidx][tmp] += 1
            if PRESENT_W: NEG_COST[Lidx][tmp] += PRESENT_W

    for stem in stems:   # a swapped pair is appended and laid again
        if episode[0] is not None and stem not in episode[0]["members"]: settle_episode()   # the episode's members are queued together: the first stem past them ends it
        PAIR_DEADLINE[0] = time.time() + PAIR_BUDGET if PAIR_BUDGET > 0 else 0.0
        PAIR_SPENT[0] = 0
        # 9 September 2026 (B19): the long pairs die on the expansion cap, not on geometry. SWP3_D spans 261 mm and its
        # corridor search stopped after 5,365,661 expansions of a 0.1 mm grid, which is 3320 x 2020 cells per layer. A
        # coarser grid for the long ones is four times fewer cells for the same millimetres of clearance, since every
        # obstacle margin here is in mm. Off by default until it is measured: PAIR_GRID_LONG=0.2 PAIR_LONG_MM=120.
        # 10 September 2026 (report 1, P1): the negotiation rasters are allocated once from the grid in use, so a pass that
        # changes the cell size mid-run would index them in another coordinate system. The two are not composable and the tool
        # says so rather than reading the wrong cells.
        if _GLONG and (NEG_COST is not None or plan_in):
            raise SystemExit("pair_preroute: PAIR_GRID_LONG cannot be combined with the negotiated plan or its cost rasters (they are sized from one grid)")
        # One Grid per cell size, kept: the polygon raster cache is instance-local since the fix above, so building a fresh Grid
        # for every long pair threw the whole board's pad rasters away twice per pair (10 September 2026).
        want = _GLONG if (_GLONG and _span(stem) >= _LONG_MM) else g
        if gr.G != want: gr = _grids.setdefault(want, Grid(b, want))
        pre_vias[:] = [v for v in b.GetTracks() if v.GetClass() == "PCB_VIA" and v.IsLocked()]   # the locked vias before this pair lays anything (the escape vias of a 0.4 mm row are anchors)
        pn, nn = pair_names.get(stem, (stem + "_P", stem + "_N")); cl = classes.get(cls_of(pn), {}); w = float(cl.get("diff_pair_width", cl.get("track_width", 0.2))); s = float(cl.get("diff_pair_gap", 0.15))
        vd, vdr = float(cl.get("via_diameter", 0.6)), float(cl.get("via_drill", 0.3)); clr_c = float(cl.get("clearance", CLR))
        try: min_clr = b.GetDesignSettings().m_MinClearance / 1e6
        except Exception: min_clr = 0.0
        clr_c = max(clr_c, min_clr); s = max(s, clr_c + 0.013)   # the legs' gap never below the clearance the DRC will apply (the board minimum wins over a smaller class value)
        # 10 September 2026, measured: the corridor's margin over its legs was 0.25 mm (a 0.15 mm mask margin plus one grid
        # cell) and that slack decides how many pairs can be laid. A leg needs w/2 + 0.02 from other copper on its own map
        # and sits (w + s)/2 off the centreline, so the centreline needs w + s/2 + 0.02; anything beyond that is clearance
        # the corridor demands and the legs do not, on a board whose gaps are measured in tenths. On B19's placed board:
        # 0.25 lays 38 of 113, 0.18 and 0.15 are in the sweep, 0.12 lays 49, 0.05 lays 42 (too little slack lets the
        # corridor into places the legs then fail out of, and legs_clear rejects the whole pair). D10 lays 4 of 5 at every
        # value, so the figure is not board-specific in the small. PAIR_CORRIDOR_SLACK restores any of them.
        # 10 September 2026, the slim retry. A 2.54 mm through-hole header leaves 0.94 mm between two 1.6 mm pads, and the
        # corridor at the measured slack asks for 2 x (w + s/2 + 0.12 + 0.16) = 1.02 mm, so a pair whose station is inside a
        # ribbon header has NO corridor out of the pin field: /USB_PNL at J_PANEL and /USB_E6 at J_AB1 both fail exactly
        # there, by eighty micrometres. At 0.05 mm of slack the same gap is 0.88 mm and the corridor fits. A board-wide 0.05
        # is worse (42 of 113 against 49), so it is a per-pair second chance like the escape-via entry: the measured slack
        # first, and the slim one for a pair that found no corridor at all. `legs_clear` still judges the legs either way.
        # A pair on an inner layer is a STRIPLINE and the class width that hits its target on the outside does not hit it inside.
        # Measured with the 2D field solver on the JLC 3313 six-layer stack (appendix 32.101, 32.102): 0.127 mm reads 102 ohm
        # against a 90 ohm target on In2 or In3 and 118 against 100, while 0.210 mm reads 90.2 and 101.7. So the width follows
        # the layer: PAIR_INNER_WIDTH names the inner one (0 keeps the class width everywhere, which is what every board did
        # while the corridors were confined to F.Cu and B.Cu). The corridor's own envelope takes the WIDER of the two, because
        # one map serves every layer and it must never under-block.
        _ic = INNER_BY_CLASS.get(cls_of(pn))
        w_in, s_in = (_ic if _ic else (W_INNER or w, S_INNER or s))
        def wid(L): return w_in if L in _INNER_CU else w
        def gap(L): return s_in if L in _INNER_CU else s
        def dof(L): return (wid(L) + gap(L)) / 2
        # 11 September 2026 (MESHSAT-862), measured on D's /USB_D8: the corridor did not cover its own legs, and the
        # difference was smaller than a grid cell. A leg sits dof = (w + s)/2 off the centreline and its own map grows
        # obstacles by w/2 + 0.02, so it reaches w + s/2 + 0.02 out; the corridor grew them by w + s/2 + slack, which is
        # 0.02 mm SHORT of that before the slack is counted. The author's own note above says the centreline needs
        # "w + s/2 + 0.02" and the code never added the 0.02. At the standard slack the whole margin is then 0.10 mm,
        # one cell of the 0.1 mm grid, and at the slim retry 0.03 mm, a third of a cell: a centreline the raster calls
        # free can have a leg the raster calls blocked, and the pass reports "the legs clear no smoothing of the
        # centreline", which reads as a smoothing problem and is a rounding one. Measured at the failure: pad U2.1's
        # polygon is 0.618 mm from the centreline where the corridor demanded 0.610, and 0.367 mm from the leg where
        # the leg demanded 0.330. Both fit in exact arithmetic, by 8 and 37 micrometres, and the cell centres do not.
        # PAIR_COVER_LEGS=1 makes the corridor cover the legs plus one grid cell, so that a free centreline implies free
        # legs and a pair that cannot pass an obstacle is refused by the SEARCH, which can go round, rather than by the
        # legs, which cannot. It is OFF, and that is the B19 arm of 11 September 2026 rather than an opinion. Same placed
        # board (md5 27dd5bd0), same slack 0.08/0.03, one pass, 113 pairs, counted by each pair's LAST failure:
        #
        #                                          off        on
        #   pairs laid                          47 of 113   45 of 113
        #   the legs clear no smoothing            25          10
        #   no stub path at a station or via       15          23
        #   no path on the map (expansion cap)      9          19
        #   no via site / no room for a via pair   12           3
        #
        # The rounding class is real and covering the legs removes 60 percent of it. It does not become laid pairs: the
        # stricter envelope costs the search its paths instead, and "no path on the map" doubles. Two fewer pairs, so
        # the knob stays off. What that says about the next arm is the useful part: widening the corridor is the wrong
        # way to remove the rounding, because this board is already at the edge of what its congestion allows (the slack
        # sweep of 32.117 was measuring that edge). The right way is to make the LEG CHECK exact where it matters: when
        # a leg point fails on the raster, re-test that point against the polygons before rejecting the pair. That
        # removes the rounding without touching the corridor. D lays 5 of 5 either way once the corridor leaves its
        # station on the right side.
        _cover = (0.02 + gr.G) if os.environ.get("PAIR_COVER_LEGS", "0") != "0" else 0.0   # OFF: the B19 arm above
        # The corridor envelope takes the wider of the two geometries: one map serves every layer and it must never under-block.
        half = max(w + s / 2, w_in + s_in / 2) + _cover + (SLACK_SLIM if stem in slim_stems else SLACK); d = (w + s) / 2
        def is_pull(p):
            """A two-pad passive whose other pad sits on GND or a supply: a pull resistor hanging off the pair, never a station (D9: the 15k pulldowns R14, R15)."""
            f = p.GetParentFootprint(); ps = list(f.Pads())
            if len(ps) != 2 or not f.GetReference()[:1] in "RCL": return False
            o = next((q for q in ps if q.GetNumber() != p.GetNumber()), None); on = (o.GetNetname() if o else "").lstrip("/")
            return on == "GND" or on.startswith("+") or on.startswith("V") or "VDD" in on or "VBUS" in on or "3V3" in on
        pads = {net: [p for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() == net and not is_pull(p)] for net in (pn, nn)}
        # a real leg is a chain of pads (connector, series resistor, ESD diode, hub pin): match each P pad to the nearest N pad within 5 mm (a station),
        # order the stations along the leg by nearest neighbour from the outermost one; unmatched pads (a lone test point) stay the router's stubs
        import itertools
        P_, N_ = pads[pn], pads[nn]; best = None
        small, large, flip = (P_, N_, False) if len(P_) <= len(N_) else (N_, P_, True)
        # This is an assignment problem and it was solved by enumerating every ordered selection, which is len(large)!/(len(large)
        # - len(small))! and rises off a cliff: 8 pads against 8 is 40,320 and 12 against 12 is 479 million (report 1 item 9).
        # Today's pairs are two to four pads, so the exhaustive search is kept where it is affordable and gives exactly the
        # matching the boards have been laid with; beyond that scipy's Hungarian solver answers the same question in polynomial
        # time. The threshold is on the actual count, not on a pad number, so it cannot be wrong about which side is cheap.
        _npermute = 1
        for _k in range(len(small)): _npermute *= (len(large) - _k)
        if _npermute > 50000:
            try:
                from scipy.optimize import linear_sum_assignment
                M = np.array([[dist_p(a_, b_) for b_ in large] for a_ in small], dtype=float)
                rows, cols = linear_sum_assignment(M)
                best = (float(M[rows, cols].sum()), tuple(int(c) for c in cols))
                report.append("MATCH %s: %d against %d pads matched by assignment (%d orderings would have been enumerated)" % (stem, len(small), len(large), _npermute))
            except ImportError: pass
        if best is None:
            for perm in itertools.permutations(range(len(large)), len(small)):
                cost = sum(dist_p(small[k], large[perm[k]]) for k in range(len(small)))
                if best is None or cost < best[0]: best = (cost, perm)
        stations = []
        if best:
            for k, idx in enumerate(best[1]):
                p, q = (small[k], large[idx]) if not flip else (large[idx], small[k])
                if dist_p(p, q) <= 5.0: stations.append((p, q))
        if len(stations) < 2: report.append("SKIP  %s: fewer than two matched stations (P %d, N %d pads)" % (stem, len(pads[pn]), len(pads[nn]))); continue
        for p_, q_ in stations:   # a station's two pads should sit side by side within about 2 mm; the packer's resistor rows put them 4 mm apart with another pad between (D8, 8 Sep)
            dd = dist_p(p_, q_)
            if dd > 2.5: report.append("STATION %s: %s and %s are %.1f mm apart (place the pair's parts side by side, pads across the pair axis)" % (stem, p_.GetParentFootprint().GetReference(), q_.GetParentFootprint().GetReference(), dd))
        def mid(st): return ((st[0].GetPosition().x + st[1].GetPosition().x) / 2e6, (st[0].GetPosition().y + st[1].GetPosition().y) / 2e6)
        far = max(stations, key=lambda st: sum(math.hypot(mid(st)[0] - mid(o)[0], mid(st)[1] - mid(o)[1]) for o in stations))
        order = [far]; rest = [st for st in stations if st is not far]
        while rest:
            nxt = min(rest, key=lambda st: math.hypot(mid(st)[0] - mid(order[-1])[0], mid(st)[1] - mid(order[-1])[1])); order.append(nxt); rest.remove(nxt)
        sections = [(a_, b_) for a_, b_ in zip(order[:-1], order[1:]) if a_[0].GetParentFootprint().GetReference() != b_[0].GetParentFootprint().GetReference()]   # a part's pass-through pins (the ESD's 1 and 6) are joined by join_adjacent_pins, not by a corridor
        for t in [t for t in b.GetTracks() if t.GetNetname() in (pn, nn) and not t.IsLocked()]: board_remove(b, t)   # a previous route of the pair goes; the locked escapes stay
        pieces = []   # everything this pair lays (removed on rollback)
        staircase = False   # set when a section fell back to the corridor as the search found it
        stripped = []   # the escape via and stubs of a fine-pitch station pad, removed so the legs enter the pad itself (restored on rollback)
        END_CANDS = int(os.environ.get("PAIR_END_CANDS", "12"))   # candidate corridor ends tested for reach before the nearest one is taken anyway
        END_OFFSET = os.environ.get("PAIR_END_OFFSET", "1") != "0"   # test the corridor end where the stubs will really start (round-two C2)
        # A SECOND knob for a second change. `_legs_leave` and `_end_reaches_offset` are two different predicates and
        # riding both on one switch would make every arm two variables, which is how the staircase comparison of
        # 9 September produced a number that could not be attributed (appendix 32.90 addendum). 11 September 2026.
        END_LEGS = os.environ.get("PAIR_END_LEGS", "1") != "0"

        def _reach_one(sx_, sy_, tx_, ty_, nm, cache):
            """Can a stub run from (sx_, sy_) to (tx_, ty_) on net nm's own map, on any allowed layer?"""
            if math.hypot(tx_ - sx_, ty_ - sy_) < 0.35: return True   # the end sits on the pad already
            for L_ in layers:
                if L_ not in trk1[nm]: continue
                if (nm, L_) not in cache: cache[(nm, L_)] = ~trk1[nm][L_]   # stub_path walks the PASSABLE map and writes in it, so each try gets its own copy
                w2 = (gr.cell(min(sx_, tx_) - 8, min(sy_, ty_) - 8), gr.cell(max(sx_, tx_) + 8, max(sy_, ty_) + 8))
                w2 = ((max(0, w2[0][0]), max(0, w2[0][1])), (min(gr.NX - 1, w2[1][0]), min(gr.NY - 1, w2[1][1])))
                if stub_path(gr, cache[(nm, L_)].copy(), (sx_, sy_), (tx_, ty_), w2): return True
            return False

        def _end_reaches(cx_, cy_, px, py, qx, qy, cache=None):
            """Can a stub run from this corridor end to BOTH pads of the station, on the legs' own maps? (10 September 2026)"""
            cache = {} if cache is None else cache
            return (_reach_one(cx_, cy_, px, py, pn, cache) and _reach_one(cx_, cy_, qx, qy, nn, cache))

        def _legs_leave(cx_, cy_, px, py, qx, qy, tx_, ty_, off):
            """Do the two OFFSET legs clear their own maps on the straight run from their pads to this corridor end?

            11 September 2026. The end-chooser tested that a STUB could reach each pad and never tested the LEGS, which
            is the predicate that later judges the pair, so it could choose an end no leg can reach and the pair then
            failed with "the legs clear no smoothing of the centreline". Measured on D's /USB_D8 at J_HARN1, a
            through-hole header whose pair sits in one column with ground pins on both sides: the P leg is blocked by
            its own partner's pad at 1.13 mm and the N leg by a GND pad at 0.87 mm, both just past the 1.2 mm station
            exemption, on every smoothing including the raw staircase. An end-chooser that does not share the predicate
            that judges is the same mistake as a debug print that does not share the predicate it explains.
            """
            dx_, dy_ = tx_ - cx_, ty_ - cy_; ln_ = math.hypot(dx_, dy_)
            if ln_ < 1e-9: return True
            ox_, oy_ = -dy_ / ln_ * off, dx_ / ln_ * off
            for (sp, sq) in (((cx_ + ox_, cy_ + oy_), (cx_ - ox_, cy_ - oy_)), ((cx_ - ox_, cy_ - oy_), (cx_ + ox_, cy_ + oy_))):
                ok_ = True
                for (ex_, ey_), (tx2, ty2), nm in ((sp, (px, py), pn), (sq, (qx, qy), nn)):
                    pm_ = trk1.get(nm, {}).get(pcbnew.F_Cu)
                    if pm_ is None: continue
                    L_ = math.hypot(ex_ - tx2, ey_ - ty2)
                    if L_ < 0.2: continue
                    for k in range(int(L_ / gr.G) + 1):
                        u = k * gr.G / L_
                        # the first 1.2 mm is inside the station's own pad pair and is not an obstacle: the SAME
                        # exemption legs_clear uses, which is the whole point of sharing the predicate
                        if u * L_ < 1.2: continue
                        jj, ii = gr.cell(tx2 + u * (ex_ - tx2), ty2 + u * (ey_ - ty2))
                        if 0 <= ii < gr.NY and 0 <= jj < gr.NX and pm_[ii, jj]: ok_ = False; break
                    if not ok_: break
                if ok_: return True
            return False

        def _end_reaches_offset(cx_, cy_, px, py, qx, qy, tx_, ty_, off, cache=None):
            """The same question asked where the stub will really start: at the OFFSET leg ends, not on the centreline.

            11 September 2026 (round-two C2, the 23 "no stub path" failures of the 60-of-113 arm). `free_end` tested
            reachability from the corridor's centreline end, and then the pass ran its stubs from the two offset leg
            ends, each displaced perpendicular to the corridor by half the pair pitch. At a fine-pitch part the picket
            of the other nets' escape vias has gaps at the via pitch, and half a pair gap sideways is the difference
            between a start inside a gap and a start inside a via's clearance. The test now asks about the points the
            stubs will use. Both sign assignments are tried, because which leg takes which side is decided later."""
            cache = {} if cache is None else cache
            dx_, dy_ = tx_ - cx_, ty_ - cy_; ln_ = math.hypot(dx_, dy_)
            if ln_ < 1e-9 or off <= 0: return _end_reaches(cx_, cy_, px, py, qx, qy, cache)
            ox_, oy_ = -dy_ / ln_ * off, dx_ / ln_ * off
            a_ = (cx_ + ox_, cy_ + oy_); b_ = (cx_ - ox_, cy_ - oy_)
            for (sp, sq) in ((a_, b_), (b_, a_)):
                if _reach_one(sp[0], sp[1], px, py, pn, cache) and _reach_one(sq[0], sq[1], qx, qy, nn, cache): return True
            return False

        def fine_part(f):
            """Pitch 0.7 mm or under: the legs enter the pads straight (the entry run)."""
            ps = [q.GetPosition() for q in f.Pads() if q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]; best = 1e18
            for i in range(len(ps)):
                for j in range(i + 1, len(ps)):
                    dd = math.hypot(ps[i].x - ps[j].x, ps[i].y - ps[j].y)
                    if 0 < dd < best: best = dd
            return best <= 0.7e6
        STRIP_MM = float(os.environ.get("PAIR_STRIP_MM", "6.0"))   # how far out of the pad an escape chain is followed

        def _escape_chain(p, net):
            """The locked escape pieces of `net` that hang off this pad, followed from the pad outward (10 September 2026).

            It used to be whatever piece STARTED within 3 mm of the pad, which is not the same thing: on B19 the other leg's
            escape survived past that radius and stood in the way of this leg 1.8 mm out of the station (SWP3_A, and the same
            shape in 30 of the 75 failures). The chain is followed piece by piece and bounded by PAIR_STRIP_MM from the pad,
            so nothing far from the station is touched, and rollback puts every piece back."""
            pool = [t for t in b.GetTracks() if t.IsLocked() and t.GetNetname() == net]
            px_, py_ = p.GetPosition().x, p.GetPosition().y; ends = []; take = []
            def _pts(t): return [t.GetPosition()] if t.GetClass() == "PCB_VIA" else [t.GetStart(), t.GetEnd()]
            grew = True
            while grew:
                grew = False
                for t in list(pool):
                    qs = _pts(t)
                    if not any(math.hypot(q.x - px_, q.y - py_) < STRIP_MM * 1e6 for q in qs): continue
                    if not (any(p.HitTest(q) for q in qs) or any(math.hypot(q.x - e.x, q.y - e.y) < 0.05e6 for q in qs for e in ends)): continue
                    take.append(t); pool.remove(t); ends.extend(qs); grew = True
            return take

        def fanned_part(f): return (fine_part(f) or bool(re.search(r"SOT-23-[68]", f.GetFPIDAsString()))) and not row_scheme(f)   # escape.py's rule: these parts carry escape stubs and vias; a 0.4 mm row keeps them (the via is the station)
        for net in (pn, nn):
            for p in pads[net]:
                if p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or via_entry(p.GetParentFootprint()) or not fanned_part(p.GetParentFootprint()): continue   # PAIR_ENTRY_VIA keeps an IC's escape and ends the legs at its vias
                for t in _escape_chain(p, net): board_remove(b, t); stripped.append(t)
        inpad = 0
        for p_, n_ in stations:   # a pin between the station's two pads (the SOT-23-6 ESD's ground pin 2): its escape stub would sit under the legs; a via in its pad instead
            f_ = p_.GetParentFootprint()
            if f_.GetReference() != n_.GetParentFootprint().GetReference() or not fanned_part(f_): continue
            for q in f_.Pads():
                if q.GetNetname() in (pn, nn) or q.GetAttribute() != pcbnew.PAD_ATTRIB_SMD: continue
                d1, d2 = dist_p(q, p_), dist_p(q, n_)
                if abs(d1 + d2 - dist_p(p_, n_)) > 0.3: continue   # not between them
                near = [t for t in b.GetTracks() if t.IsLocked() and t.GetNetname() == q.GetNetname() and math.hypot(t.GetPosition().x - q.GetPosition().x, t.GetPosition().y - q.GetPosition().y) < 2.5e6]
                for t in near: board_remove(b, t); stripped.append(t)
                v = pcbnew.PCB_VIA(b); v.SetPosition(q.GetPosition()); v.SetWidth(FromMM(min(vd, 0.5))); v.SetDrill(FromMM(min(vdr, 0.25))); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(q.GetNet()); v.SetLocked(True); b.Add(v); pieces.append(v); inpad += 1
        if stripped or inpad: print("pair_preroute: %s: %d escape pieces of fine-pitch station pads removed, the legs enter those pads directly; %d via(s) in the pad of a pin between them" % (stem, len(stripped), inpad))
        pre_vias[:] = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA" and t.IsLocked()]
        trk, via = build_maps(gr, b, maplayers, set(), half, vd / 2)   # every net's copper, the pair's own pads included: the corridor stops outside the stations, the stubs enter
        via1n = {pn: build_maps(gr, b, maplayers, {pn}, half, vd / 2, split=0.05)[1], nn: build_maps(gr, b, maplayers, {nn}, half, vd / 2, split=0.05)[1]}   # sites for a single end via per leg (plain margins; the other leg's pads block)
        via1 = via1n[pn]   # shared updates below go to both
        pad_layers = sorted({L for net in (pn, nn) for p in pads[net] for L in _ALL.values() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and p.IsOnLayer(L)} | set(maplayers), key=list(_ALL.values()).index)
        trk1 = {pn: build_maps(gr, b, pad_layers, {pn}, max(w, w_in) / 2 + 0.02, vd / 2)[0], nn: build_maps(gr, b, pad_layers, {nn}, max(w, w_in) / 2 + 0.02, vd / 2)[0]}   # the stub maps cover the pads' own layers too   # per leg: the other leg's copper is an obstacle (the P stub through the N pad of J_USB3, 8 Sep); 0.15 mm extra for the mask dam at through-hole pads
        def rebuild_maps():   # after a swap of two passives inside a section the maps still hold the pads at their old places (D9: a stub over the swapped pad, 8 Sep 2026 13:08)
            nonlocal trk, via, via1n, trk1
            trk, via = build_maps(gr, b, maplayers, set(), half, vd / 2)
            via1n = {pn: build_maps(gr, b, maplayers, {pn}, half, vd / 2, split=0.05)[1], nn: build_maps(gr, b, maplayers, {nn}, half, vd / 2, split=0.05)[1]}
            trk1 = {pn: build_maps(gr, b, pad_layers, {pn}, max(w, w_in) / 2 + 0.02, vd / 2)[0], nn: build_maps(gr, b, pad_layers, {nn}, max(w, w_in) / 2 + 0.02, vd / 2)[0]}
        net_p, net_n = b.GetNetInfo().GetNetItem(pn), b.GetNetInfo().GetNetItem(nn); added = 0; cells = 0; nruns = 0; failed = None; twist = None; laid_sections = 0
        def rollback():
            for t in pieces: board_remove(b, t)
            pieces.clear()
            for t in stripped: b.Add(t)   # the escapes come back with the pair's failure
            stripped.clear()
        def other_of(net): return nn if net.GetNetname() == pn else pn
        def seg(x1, y1, x2, y2, L, net):
            nonlocal added
            if math.hypot(x2 - x1, y2 - y1) < 0.01: return
            wL = wid(L)
            t = pcbnew.PCB_TRACK(b); t.SetStart(VECTOR2I(FromMM(x1), FromMM(y1))); t.SetEnd(VECTOR2I(FromMM(x2), FromMM(y2))); t.SetWidth(FromMM(wL)); t.SetLayer(L); t.SetNet(net); t.SetLocked(True); b.Add(t); added += 1; pieces.append(t)
            o = other_of(net)
            if L in trk1[o]: gr.seg(trk1[o][L], x1, y1, x2, y2, wL + clr_c + 0.01)   # the other leg keeps clear of this piece by the class clearance (the map's 0.16 floor blocked the other leg's own start 0.35 mm away)
            for vm in via1n.values(): gr.seg(vm, x1, y1, x2, y2, wL / 2 + clr_c + vd / 2 + 0.01)
            gr.seg(via, x1, y1, x2, y2, wL / 2 + CLR + vd / 2 + VIA_SPLIT)
        def via_at(x, y, net):
            nonlocal added
            v = pcbnew.PCB_VIA(b); v.SetPosition(VECTOR2I(FromMM(x), FromMM(y))); v.SetWidth(FromMM(vd)); v.SetDrill(FromMM(vdr)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net); v.SetLocked(True); b.Add(v); added += 1; pieces.append(v)
            o = other_of(net)
            for L in trk1[o]: gr.disc(trk1[o][L], x, y, vd / 2 + clr_c + w / 2 + 0.01)
            for vm in via1n.values(): gr.disc(vm, x, y, vdr + 0.30 + 0.02)
            gr.disc(via, x, y, vdr + 0.30 + VIA_SPLIT)
        # the stub, via-site and hop helpers of this pair (pair-level state only; they were inside the section loop and a pair whose last section took the direct legs left them undefined for the stub pass, 8 Sep 2026 12:47)
        def stub(ax_, ay_, bx_, by_, SL, net):
            """One stub on layer SL from (ax_, ay_) to the pad at (bx_, by_) on that leg's own map; a straight piece when no path exists."""
            pm = ~trk1[net.GetNetname()][SL] if SL in trk1[net.GetNetname()] else None
            win2 = (gr.cell(min(ax_, bx_) - 8, min(ay_, by_) - 8), gr.cell(max(ax_, bx_) + 8, max(ay_, by_) + 8)); win2 = ((max(0, win2[0][0]), max(0, win2[0][1])), (min(gr.NX - 1, win2[1][0]), min(gr.NY - 1, win2[1][1])))
            if gr.cell(ax_, ay_) == gr.cell(bx_, by_) or math.hypot(bx_ - ax_, by_ - ay_) < 1.5 * gr.G: seg(ax_, ay_, bx_, by_, SL, net); return True   # the offset end already sits on the pad
            sp = stub_path(gr, pm.copy(), (ax_, ay_), (bx_, by_), win2) if pm is not None else None
            if sp and len(sp) >= 2:
                for k in range(len(sp) - 1): seg(sp[k][0], sp[k][1], sp[k + 1][0], sp[k + 1][1], SL, net)
                seg(sp[-1][0], sp[-1][1], bx_, by_, SL, net); return True
            # A stub has to reach its own NET, not one point of it. Aiming only at the escape via made the last half millimetre the hardest
            # cell on the board, because the via sits inside its own part's fan: 34 of B18's 66 pair failures were "no stub path at via"
            # (9 September 2026). The escape track that leads to the via is the same copper and is reachable a millimetre earlier, so when
            # the via cannot be reached the nearest points of the net's own locked escape are tried in turn.
            if pm is not None:
                alts = []
                for t_ in b.GetTracks():
                    if t_.GetClass() != "PCB_TRACK" or not t_.IsLocked() or t_.GetNetname() != net.GetNetname() or t_.GetLayer() != SL: continue
                    ax2, ay2, bx2, by2 = mm(t_.GetStart().x), mm(t_.GetStart().y), mm(t_.GetEnd().x), mm(t_.GetEnd().y)
                    for px_, py_ in ((ax2, ay2), (bx2, by2), ((ax2 + bx2) / 2, (ay2 + by2) / 2)):
                        d_ = math.hypot(px_ - bx_, py_ - by_)
                        if 0.05 < d_ <= 4.0: alts.append((d_, px_, py_))
                for _d, px_, py_ in sorted(alts)[:8]:
                    sp2 = stub_path(gr, pm.copy(), (ax_, ay_), (px_, py_), win2)
                    if sp2 and len(sp2) >= 2:
                        for k in range(len(sp2) - 1): seg(sp2[k][0], sp2[k][1], sp2[k + 1][0], sp2[k + 1][1], SL, net)
                        seg(sp2[-1][0], sp2[-1][1], px_, py_, SL, net)
                        return True
            if os.environ.get("PAIR_DEBUG") and pm is not None:   # the stub map around the goal, one character per cell (S start, G goal, # forbidden)
                js, is_ = gr.cell(ax_, ay_); jg, ig = gr.cell(bx_, by_); r = 20
                print("pair_preroute: stub map 4 mm around the START (%.2f, %.2f):" % (ax_, ay_))
                for i in range(is_ - r, is_ + r + 1, 2):
                    rowtxt = ""
                    for j in range(js - r, js + r + 1):
                        if not (0 <= i < gr.NY and 0 <= j < gr.NX): rowtxt += " "; continue
                        rowtxt += "S" if (i, j) == (is_, js) else ("G" if (abs(i - ig) <= 1 and abs(j - jg) <= 1) else ("." if pm[i, j] else "#"))
                    print("   " + rowtxt)
                print("pair_preroute: stub %s on %s from (%.2f, %.2f) [%s] to (%.2f, %.2f) [%s], 4 mm around the goal:" % (net.GetNetname(), b.GetLayerName(SL), ax_, ay_, "free" if pm[is_, js] else "BLOCKED", bx_, by_, "free" if pm[ig, jg] else "BLOCKED"))
                for i in range(ig - r, ig + r + 1, 2):
                    rowtxt = ""
                    for j in range(jg - r, jg + r + 1):
                        if not (0 <= i < gr.NY and 0 <= j < gr.NX): rowtxt += " "; continue
                        rowtxt += "S" if (abs(i - is_) <= 1 and abs(j - js) <= 1) else ("G" if (i, j) == (ig, jg) else ("." if pm[i, j] else "#"))
                    print("   " + rowtxt)
            return False   # no blind straight piece (it shorted J_HARN1's pin 4 on D9)
        def fan_leg(ex_, ey_, px_, py_, L_, net_):
            """The last piece of a leg, from its corridor end into its own pad. It used to be laid straight and untested, which is how a
            pair's own fan came to sit on other nets' escapes: 24 of B17's 34 pruned escapes had a pre-routed pair leg as the counterparty
            (8 Sep 2026 23:15, 32.77). Straight when the straight line is clear on this leg's own map, with the last 1.2 mm exempt because
            it lies inside the pad pair (the exemption legs_clear already uses); otherwise routed by stub(), and False when neither works."""
            pm = trk1[net_.GetNetname()].get(L_)
            if pm is None: seg(ex_, ey_, px_, py_, L_, net_); return True
            ln_ = math.hypot(px_ - ex_, py_ - ey_)
            clear = True
            if ln_ > 1.2:
                n_ = int(ln_ / gr.G) + 2
                for k_ in range(n_ + 1):
                    u_ = k_ / n_
                    if ln_ * (1.0 - u_) < 1.2: break
                    jj_, ii_ = gr.cell(ex_ + u_ * (px_ - ex_), ey_ + u_ * (py_ - ey_))
                    if 0 <= ii_ < gr.NY and 0 <= jj_ < gr.NX and pm[ii_, jj_]: clear = False; break
            if clear: seg(ex_, ey_, px_, py_, L_, net_); return True
            return stub(ex_, ey_, px_, py_, L_, net_)
        def via_site(ex_, ey_, px_, py_, L, aL, net, away):
            """A free single-via site near the offset end (ex_, ey_): the nearest cell of via1 that is also clear on both layers' leg maps, preferring the
            side away from the other leg (unit vector `away`) and the direction of the pad; None when nothing within 3 mm."""
            cands = []
            for r10 in range(4, 31):
                r = r10 / 10.0
                for a10 in range(0, 360, 15):
                    a = math.radians(a10); cx_, cy_ = ex_ + r * math.cos(a), ey_ + r * math.sin(a); jj, ii = gr.cell(cx_, cy_)
                    if not (0 <= ii < gr.NY and 0 <= jj < gr.NX) or via1n[net.GetNetname()][ii, jj]: continue
                    cx_, cy_ = gr.xy(jj, ii)   # the site is the cell the maps cleared, not the polar sample up to 0.07 mm off it (a dive via 0.10 mm from the other leg, 8 Sep 2026 13:27)
                    if L in trk1[net.GetNetname()] and trk1[net.GetNetname()][L][ii, jj]: continue
                    if aL in trk1[net.GetNetname()] and trk1[net.GetNetname()][aL][ii, jj]: continue
                    score = r - 0.5 * ((cx_ - ex_) * away[0] + (cy_ - ey_) * away[1]) / r + 0.3 * math.hypot(cx_ - px_, cy_ - py_) / 10.0
                    cands.append((score, cx_, cy_))
            cands.sort(); return [(c[1], c[2]) for c in cands[:12]]   # the best twelve, tried in order until a hop path exists
        def via_hop(ex_, ey_, px_, py_, L, aL, net, away):
            """A via site with a hop path from the offset end on L: (vx, vy) or None; the hop is laid."""
            for vx_, vy_ in via_site(ex_, ey_, px_, py_, L, aL, net, away):
                if stub(ex_, ey_, vx_, vy_, L, net): return (vx_, vy_)
            return None
        def dive_p(x, y, ex, ey, L, aL, obj, net, away):
            """The P leg from its corridor end (ex, ey) on L to its pad (x, y) under the N leg: a via beside the corridor end, a hop on the other layer,
            a via beside the pad (none for a through-hole pad, which the hop layer reaches itself), the stub in. Returns the failure text or None."""
            if aL is not None and aL != L:   # the pad is on another layer: the P leg runs on the corridor layer to a via beside its pad, under the N stub
                site = None
                for cand in via_site(x, y, x, y, L, aL, net, away):
                    if stub(ex, ey, cand[0], cand[1], L, net): site = cand; break
                if site is None: return "no via site beside the pad with a hop path"
                via_at(site[0], site[1], net); gr.disc(via, site[0], site[1], VIA_SPLIT)
                return None if stub(site[0], site[1], x, y, aL, net) else "no stub path"
            hop = hop_of(L)   # the pad is on the corridor layer: dive through a hop layer (else the other corridor layer)
            if hop is None: return "no layer to dive through"
            aL_ = L if aL is None else aL
            site1 = via_hop(ex, ey, x, y, L, hop, net, away)
            if site1 is None: return "no via site for the dive"
            via_at(site1[0], site1[1], net); gr.disc(via, site1[0], site1[1], VIA_SPLIT)
            pth_ = hasattr(obj, "GetAttribute") and obj.GetAttribute() == pcbnew.PAD_ATTRIB_PTH
            if pth_ and stub(site1[0], site1[1], x, y, hop, net): return None   # a through-hole pad takes the leg on the hop layer
            for cand in via_site(x, y, x, y, hop, aL_, net, away):   # each site: the hop to it, the via, the stub into the pad; the next site when the stub finds no path (13:16)
                n0 = len(pieces)
                if not stub(site1[0], site1[1], cand[0], cand[1], hop, net): continue
                via_at(cand[0], cand[1], net); gr.disc(via, cand[0], cand[1], VIA_SPLIT)
                if stub(cand[0], cand[1], x, y, aL_, net): return None
                for t in pieces[n0:]: board_remove(b, t)
                del pieces[n0:]
            return "no via site beside the pad with a dive path and a stub into it"
        for _sec_k, ((pa, na), (pb, nb)) in enumerate(sections):
            A = [anchor(pa), anchor(na)]; B = [anchor(pb), anchor(nb)]
            sx, sy = (A[0][0] + A[1][0]) / 2, (A[0][1] + A[1][1]) / 2; gx, gy = (B[0][0] + B[1][0]) / 2, (B[0][1] + B[1][1]) / 2
            sL = gL = None   # the corridor picks its layer; the end stubs via to the pads' own layer (8 Sep: a start forced onto B.Cu inside the resistor cluster found no exit)
            # a station between two through-hole pads or two hub pins has no room for the corridor at its midpoint: slide the end outward along the normal of the
            # P-N line (both ways, up to 4 mm) to the first cell the corridor map allows on any of the layers; the stubs cover the rest
            def _free_cands(x, y, px, py, qx, qy, tx, ty):
                """The cells the corridor allows near a station, nearest first: the midpoint itself, then outward towards the other
                station (through the escape cloud of a hub or a connector), then along the normal of the P-N line, up to 12 mm."""
                def open_cell(jj, ii, r=3):   # free with a clear 7 x 7 block around it on that layer: a one-cell pocket between a header's pins is no corridor start (D9, J_HARN1)
                    return 0 <= ii - r and ii + r < gr.NY and 0 <= jj - r and jj + r < gr.NX and any(not trk[L][ii - r:ii + r + 1, jj - r:jj + r + 1].any() for L in layers)
                # 9 Sep 2026 (A24 USB_E6, appendix 32.83): the FIRST cell with a 0.6 mm block around it is often a pocket
                # inside a connector's escape cloud, and the corridor A* then dies in it after ninety expansions. A wider
                # block is far more likely to sit in open copper, so the search runs twice: 1.2 mm first, 0.6 mm after.
                dx_, dy_ = qx - px, qy - py; ln_ = math.hypot(dx_, dy_) or 1.0; nx_, ny_ = -dy_ / ln_, dx_ / ln_
                tdx, tdy = tx - x, ty - y; tl = math.hypot(tdx, tdy) or 1.0; tdx, tdy = tdx / tl, tdy / tl
                for _rr in (6, 3):
                  jj, ii = gr.cell(x, y)
                  if open_cell(jj, ii, _rr): yield x, y
                  for step in range(1, 121):   # up to 12 mm: a 0.4 mm hub's escape cloud is 4 to 8 mm deep
                    for ux, uy in ((nx_, ny_), (-nx_, -ny_), (tdx, tdy)):   # the P-N normal first: the legs then arrive side by side with the pads (8 Sep: an approach along the P-N line makes the far stub pass the near pad)
                        cx_, cy_ = x + ux * 0.1 * step, y + uy * 0.1 * step; jj, ii = gr.cell(cx_, cy_)
                        if open_cell(jj, ii, _rr): yield cx_, cy_
                  # three rays are a thin search; the sweep tries sixteen directions, the ones pointing at the other station first
                  order = sorted(range(16), key=lambda k: -(math.cos(k * math.pi / 8) * tdx + math.sin(k * math.pi / 8) * tdy))
                  for step in range(1, 121):
                    for k in order:
                        ux, uy = math.cos(k * math.pi / 8), math.sin(k * math.pi / 8)
                        cx_, cy_ = x + ux * 0.1 * step, y + uy * 0.1 * step; jj, ii = gr.cell(cx_, cy_)
                        if open_cell(jj, ii, _rr): yield cx_, cy_

            def free_end(x, y, px, py, qx, qy, tx, ty):
                """The corridor end at a station: the nearest allowed cell FROM WHICH BOTH LEGS CAN STILL REACH THEIR PADS.

                10 September 2026 (B19): the old version took the first open cell it found, in a sweep of sixteen directions up to
                12 mm. At a fine-pitch part that cell is regularly on the far side of the picket of the OTHER nets' escape vias, and
                the corridor then arrives somewhere the stub cannot leave: /HDMI1_D0 fails alone on the board with "no stub path for
                HDMI1_D0_N at U3" and its stub map shows a wall between the corridor end and the pad. Each candidate is now tested
                with the same stub search that will have to run later, and the first that works for both legs is taken; when none of
                the first PAIR_END_CANDS does, the nearest open cell is used as before, so nothing is lost."""
                best = None; centre_ok = None; cache = {}
                off_ = max((dof(L_) for L_ in layers), default=0.0) if END_OFFSET else 0.0
                for k_, (cx_, cy_) in enumerate(_free_cands(x, y, px, py, qx, qy, tx, ty)):
                    if best is None: best = (cx_, cy_)
                    # first choice: an end whose OFFSET leg starts both reach their pads, which is what the pass will do
                    if off_ > 0 and _end_reaches_offset(cx_, cy_, px, py, qx, qy, tx, ty, off_, cache) \
                       and (not END_LEGS or _legs_leave(cx_, cy_, px, py, qx, qy, tx, ty, off_)): return cx_, cy_
                    # second choice: the centreline test, which is what this did before; kept so the change can only
                    # improve on the old answer and never replace a working end with a worse one
                    if centre_ok is None and _end_reaches(cx_, cy_, px, py, qx, qy, cache): centre_ok = (cx_, cy_)
                    if off_ <= 0 and centre_ok is not None: return centre_ok
                    if k_ + 1 >= END_CANDS: break
                return centre_ok or best or (x, y)

            def fine_end(st, out_=2.5):
                """The corridor end of an entry station: on the outward normal of the pad pair (away from the parts' centre), the first open block at out_ mm or beyond."""
                p_, n_ = st; mx_, my_ = mid(st); fa_, fb_ = p_.GetParentFootprint(), n_.GetParentFootprint(); fx_, fy_ = [(a_ + b_) / 2 for a_, b_ in zip(fp_centre(fa_), fp_centre(fb_))]
                dx_, dy_ = n_.GetPosition().x / 1e6 - p_.GetPosition().x / 1e6, n_.GetPosition().y / 1e6 - p_.GetPosition().y / 1e6; ln_ = math.hypot(dx_, dy_) or 1.0
                nx_, ny_ = -dy_ / ln_, dx_ / ln_
                if (mx_ - fx_) * nx_ + (my_ - fy_) * ny_ < 0: nx_, ny_ = -nx_, -ny_   # outward
                padL = [L for L in layers if all(q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and q.IsOnLayer(L) for q in st)]   # an SMD station's end sits where its own layer is free
                Ls_ = padL or list(layers)   # (8 Sep 2026 12:53: an end free on In2 only, inside the top-layer keep-away between two stations 2.4 mm apart, left the corridor no start)
                for step in range(int(out_ * 10), 121):
                    cx_, cy_ = mx_ + nx_ * 0.1 * step, my_ + ny_ * 0.1 * step; jj, ii = gr.cell(cx_, cy_)
                    if 0 <= ii - 3 and ii + 3 < gr.NY and 0 <= jj - 3 and jj + 3 < gr.NX and any(not trk[L][ii - 3:ii + 4, jj - 3:jj + 4].any() for L in Ls_): return cx_, cy_
                # 10 September 2026 (D10 USB_D8): the outward normal of the P-N line is the WRONG way out of a through-hole header
                # whose pair sits across the two rows: the normal then runs ALONG the pin row and hits pin after pin, and the tool
                # returned a blocked point that A* refused with "the start cell is passable on no allowed layer". A pair on the old
                # diagonal pins escaped between four pins by luck of the geometry. None here means "no way out along the normal",
                # and the caller falls back to the sixteen-direction sweep of free_end.
                return None
            gx0, gy0 = gx, gy
            def entry_station0(st):
                if any(q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and (row_scheme(q.GetParentFootprint()) or via_entry(q.GetParentFootprint())) for q in st): return False   # a 0.4 mm row, or an IC under PAIR_ENTRY_VIA: the escape vias are the ends
                if not all((q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and q.IsOnLayer(pcbnew.F_Cu)) or q.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for q in st) or dist_p(st[0], st[1]) > 2.6: return False
                fa_, fb_ = st[0].GetParentFootprint(), st[1].GetParentFootprint()
                return fa_.GetReference() == fb_.GetReference() or (fa_.GetFPIDAsString() == fb_.GetFPIDAsString() and fa_.GetReference()[:1] in "RCL")
            fineA0, fineB0 = entry_station0((pa, na)), entry_station0((pb, nb))
            if fineA0 and fineB0 and math.hypot(mid((pb, nb))[0] - mid((pa, na))[0], mid((pb, nb))[1] - mid((pa, na))[1]) < 7.0:
                # two entry stations a few millimetres apart (the ESD beside its series resistors): straight legs pad to pad on F.Cu, no corridor
                # each leg: from its pad at the wider station to a waypoint 1.2 mm before the finer station's pad pair at +-(w+s)/2 of its axis, then straight into the pin
                # (a neighbouring pin's escape via sits 0.45 mm off the axis: a leg converging late would touch it)
                stA, stB = (pa, na), (pb, nb); wide_first = dist_p(*stA) >= dist_p(*stB)
                stF, stW = (stB, stA) if wide_first else (stA, stB)   # the finer station gets the waypoint
                mxF, myF = mid(stF); fa_, fb_ = stF[0].GetParentFootprint(), stF[1].GetParentFootprint(); fx_, fy_ = [(a_ + b_) / 2 for a_, b_ in zip(fp_centre(fa_), fp_centre(fb_))]
                dxF, dyF = stF[1].GetPosition().x / 1e6 - stF[0].GetPosition().x / 1e6, stF[1].GetPosition().y / 1e6 - stF[0].GetPosition().y / 1e6; lF = math.hypot(dxF, dyF) or 1.0; ax_, ay_ = dxF / lF, dyF / lF
                nxF, nyF = -ay_, ax_
                if (mxF - fx_) * nxF + (myF - fy_) * nyF < 0: nxF, nyF = -nxF, -nyF
                wx, wy = mxF + nxF * 1.2, myF + nyF * 1.2; fineF = dist_p(*stF) <= 0.7
                legs_ = []
                for k_, net in ((0, net_p), (1, net_n)):
                    pW, pF = stW[k_], stF[k_]; lat = (-d if k_ == 0 else d)   # P on the near side of the axis direction P->N
                    E_ = (mm(pF.GetPosition().x), mm(pF.GetPosition().y)); W_ = (wx + ax_ * lat, wy + ay_ * lat) if fineF else E_   # two wide stations: pad to pad
                    legs_.append((net, (mm(pW.GetPosition().x), mm(pW.GetPosition().y)), W_, E_))
                ok_ = True
                for net, S_, W_, E_ in legs_:
                    (x1_, y1_), (x2_, y2_) = S_, W_; ln_ = math.hypot(x2_ - x1_, y2_ - y1_); pm_ = trk1[net.GetNetname()].get(pcbnew.F_Cu)
                    for k in range(int(ln_ / gr.G) + 1):
                        u = k * gr.G / ln_ if ln_ else 0
                        if u * ln_ < 0.9 or (not fineF and (1 - u) * ln_ < 0.9): continue   # inside a station's own pad space
                        jj, ii = gr.cell(x1_ + u * (x2_ - x1_), y1_ + u * (y2_ - y1_))
                        if pm_ is not None and 0 <= ii < gr.NY and 0 <= jj < gr.NX and pm_[ii, jj]:
                            if ok_ and os.environ.get("PAIR_DEBUG"): print("pair_preroute: direct leg of %s blocked on F.Cu at (%.2f, %.2f), %.1f mm along the %.1f mm leg" % (net.GetNetname(), x1_ + u * (x2_ - x1_), y1_ + u * (y2_ - y1_), u * ln_, ln_))
                            ok_ = False
                def isx_(a_, b_, c_, d_):
                    def ccw(p1_, p2_, p3_): return (p3_[1] - p1_[1]) * (p2_[0] - p1_[0]) > (p2_[1] - p1_[1]) * (p3_[0] - p1_[0])
                    return ccw(a_, c_, d_) != ccw(b_, c_, d_) and ccw(a_, b_, c_) != ccw(a_, b_, d_)
                if ok_ and isx_(legs_[0][1], legs_[0][2], legs_[1][1], legs_[1][2]):   # the two fans cross: exchange the wide station's passives when they are a pair
                    fa2, fb2 = stW[0].GetParentFootprint(), stW[1].GetParentFootprint()
                    if SWAP_OK and not (SWAP_BOTH and swap_breaks_other_side(fa2, fb2, (pn, nn))) and fa2.GetReference() != fb2.GetReference() and fa2.GetFPIDAsString() == fb2.GetFPIDAsString() and not fa2.IsLocked() and not fb2.IsLocked() and not pinned(fa2) and not pinned(fb2):
                        p1_, p2_ = fa2.GetPosition(), fb2.GetPosition(); fa2.SetPosition(p2_); fb2.SetPosition(p1_); MAP_EPOCH[0] += 1; report.append("SWAP  %s: %s and %s exchanged positions so the legs reach their pins without crossing" % (stem, fa2.GetReference(), fb2.GetReference())); rebuild_maps()
                        legs_ = [(net, (mm(stW[k_].GetPosition().x), mm(stW[k_].GetPosition().y)), W_, E_) for (net, S_, W_, E_), k_ in zip(legs_, (0, 1))]
                    else: ok_ = False
                if ok_:
                    for net, S_, W_, E_ in legs_: seg(S_[0], S_[1], W_[0], W_[1], pcbnew.F_Cu, net); seg(W_[0], W_[1], E_[0], E_[1], pcbnew.F_Cu, net)
                    laid_sections += 1; continue
                # not clear: the corridor takes over, with shorter entries so the two ends do not overlap
            d_mid = math.hypot(mid((pb, nb))[0] - mid((pa, na))[0], mid((pb, nb))[1] - mid((pa, na))[1])
            def entry_out_(st):
                pitch = dist_p(st[0], st[1]); tgt = 0.0 if pitch <= 0.7 else (1.0 if pitch <= 1.0 else 1.6)
                return max(tgt + 0.8, min(2.5 + tgt, d_mid / 2 - 0.3))
            _fa = fine_end((pa, na), entry_out_((pa, na))) if fineA0 else None
            # An entry station's end comes from fine_end, which walks the OUTWARD NORMAL of the P-N line. When the pair
            # sits in one column of a through-hole header, that normal points ALONG the pin row, so the end is open for
            # the centreline and the offset legs leave straight through the neighbouring pins: measured on D's /USB_D8
            # at J_HARN1, the P leg blocked by its own partner's pad at 1.13 mm and the N leg by a GND pad at 0.87 mm.
            # An end whose legs cannot leave is not an end, so it is dropped and the sixteen-direction sweep is used.
            # 11 September 2026, and the same class as the 10 September finding about a pair across two rows.
            _offl = max((dof(L_) for L_ in layers), default=0.0) if END_LEGS else 0.0
            if _fa and _offl > 0 and not _legs_leave(_fa[0], _fa[1], A[0][0], A[0][1], A[1][0], A[1][1], gx0, gy0, _offl):
                report.append("ENDLEG %s: the entry end of %s is open for the centreline and its legs cannot leave it; taking the sweep instead"
                              % (stem, pa.GetParentFootprint().GetReference())); _fa = None
            sx, sy = _fa if _fa else free_end(sx, sy, A[0][0], A[0][1], A[1][0], A[1][1], gx0, gy0)
            _fb = fine_end((pb, nb), entry_out_((pb, nb))) if fineB0 else None
            if _fb and _offl > 0 and not _legs_leave(_fb[0], _fb[1], B[0][0], B[0][1], B[1][0], B[1][1], sx, sy, _offl):
                report.append("ENDLEG %s: the entry end of %s is open for the centreline and its legs cannot leave it; taking the sweep instead"
                              % (stem, pb.GetParentFootprint().GetReference())); _fb = None
            gx, gy = _fb if _fb else free_end(gx, gy, B[0][0], B[0][1], B[1][0], B[1][1], sx, sy)
            # 10 September 2026: the corridor search box is the two ends plus this margin. 25 mm was a guess; with the
            # corridor slack measured, "no path on the map" is the biggest remaining family (24 of B19's 64 misses) and
            # a pair that has to detour further than the box allows reads exactly like a pair with no path. PAIR_WINDOW.
            sj, si = gr.cell(sx, sy); gj, gi = gr.cell(gx, gy); win = float(os.environ.get("PAIR_WINDOW", "25"))
            window = (gr.cell(min(sx, gx) - win, min(sy, gy) - win), gr.cell(max(sx, gx) + win, max(sy, gy) + win))
            window = ((max(0, window[0][0]), max(0, window[0][1])), (min(gr.NX - 1, window[1][0]), min(gr.NY - 1, window[1][1])))
            cur_seg[:] = [sx, sy, gx, gy]   # the section the rip-up window is measured from
            behind = []
            if fineA0: mx_, my_ = mid((pa, na)); ln_ = math.hypot(sx - mx_, sy - my_) or 1.0; behind.append((sx, sy, (sx - mx_) / ln_, (sy - my_) / ln_))
            if fineB0: mx_, my_ = mid((pb, nb)); ln_ = math.hypot(gx - mx_, gy - my_) or 1.0; behind.append((gx, gy, (gx - mx_) / ln_, (gy - my_) / ln_))
            _planned = plan_in.get(stem.lstrip("/"), None)
            if _planned is not None and _sec_k < len(_planned) and _planned[_sec_k]:
                path = [tuple(c) for c in _planned[_sec_k]]   # the negotiated corridor, already agreed with every other pair
                # The plan owns its ends. `free_end` reads the board, and by the time this section is laid the board carries
                # the pairs laid before it, so it can choose a different cell than the planning pass did and the corridor
                # would then start away from its own first cell. The planned path's own ends win (10 September 2026).
                sx, sy = gr.xy(path[0][2], path[0][1]); gx, gy = gr.xy(path[-1][2], path[-1][1])
                sj, si = gr.cell(sx, sy); gj, gi = gr.cell(gx, gy); cur_seg[:] = [sx, sy, gx, gy]
            else:
                path = astar(gr, layers, trk, via, (sL, sj, si), (gL, gj, gi), window, behind, cost=NEG_COST)
            if PLAN_MODE:
                plan_out.setdefault(stem.lstrip("/"), []).append([list(c) for c in (path or [])])
                if path:
                    neg_stamp(path, half + CLR)
                    print("pair_preroute: PLAN  %s section %d of %d: %d cells" % (stem, _sec_k + 1, len(sections), len(path)), flush=True)
                elif stem not in slim_stems and SLACK_SLIM < SLACK:
                    slim_stems.add(stem); stems.append(stem); plan_out.pop(stem.lstrip("/"), None)
                    report.append("SLIM  %s: no corridor at %.2f mm of slack; planned again at %.2f" % (stem, SLACK, SLACK_SLIM))
                    break
                else:
                    report.append("FAIL  %s: section %s -> %s (%s)" % (stem, pa.GetParentFootprint().GetReference(), pb.GetParentFootprint().GetReference(), PATH_WHY[0] or "no corridor"))
                continue
            def dump(tag, cx, cy, R=3.0, layer_idx=0):   # PAIR_DEBUG=1: the corridor map around a point, one character per 2 cells (S start, G goal, # forbidden)
                if not os.environ.get("PAIR_DEBUG"): return
                jc, ic = gr.cell(cx, cy); r = int(R / gr.G); M = trk[layers[layer_idx]]; print("pair_preroute: map %s on %s around (%.1f, %.1f), %d mm square" % (tag, b.GetLayerName(layers[layer_idx]), cx, cy, 2 * R))
                for i in range(ic - r, ic + r + 1, 2):
                    row = ""
                    for j in range(jc - r, jc + r + 1, 2):
                        if not (0 <= i < gr.NY and 0 <= j < gr.NX): row += " "; continue
                        row += "S" if (i, j) == (si, sj) else ("G" if (i, j) == (gi, gj) else ("#" if M[i, j] else "."))
                    print("   " + row)
            if path is None:
                failed = "%s -> %s (%s)" % (pa.GetParentFootprint().GetReference(), pb.GetParentFootprint().GetReference(), PATH_WHY[0] or "no corridor")
                for li in range(len(layers)): dump("start of %s" % failed, sx, sy, 3.0, li); dump("goal of %s" % failed, gx, gy, 3.0, li)
                break
            def entry_station(st):
                if not all((q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and q.IsOnLayer(pcbnew.F_Cu)) or q.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for q in st): return False
                if dist_p(st[0], st[1]) > 2.6: return False
                fa_, fb_ = st[0].GetParentFootprint(), st[1].GetParentFootprint()
                return fa_.GetReference() == fb_.GetReference() or (fa_.GetFPIDAsString() == fb_.GetFPIDAsString() and fa_.GetReference()[:1] in "RCL")
            def entry_target(st):
                """Where the entry run ends: the pad pair's midpoint for a fine pitch, 1.0 mm short of it (on the outward normal) when the legs must fan out."""
                mx_, my_ = mid(st); pitch = dist_p(st[0], st[1])
                if pitch <= 0.7: return mx_, my_
                out_ = 1.0 if pitch <= 1.0 else (1.6 if pitch <= 2.0 else 2.2)
                p_, n_ = st; fa_, fb_ = p_.GetParentFootprint(), n_.GetParentFootprint(); fx_, fy_ = [(a_ + b_) / 2 for a_, b_ in zip(fp_centre(fa_), fp_centre(fb_))]
                dx_, dy_ = n_.GetPosition().x / 1e6 - p_.GetPosition().x / 1e6, n_.GetPosition().y / 1e6 - p_.GetPosition().y / 1e6; ln_ = math.hypot(dx_, dy_) or 1.0; nx_, ny_ = -dy_ / ln_, dx_ / ln_
                if (mx_ - fx_) * nx_ + (my_ - fy_) * ny_ < 0: nx_, ny_ = -nx_, -ny_
                return mx_ + nx_ * out_, my_ + ny_ * out_
            def fine_station(st):
                # The tail run (a straight line on F.Cu from the corridor's end into the pad pair) is only for a station whose pads the
                # corridor is meant to reach directly. A 0.4 mm row is not one: `entry_station0` already refuses it for the corridor's own
                # end because "the escape vias are the ends", and drawing a straight tail into the pad pair anyway crosses the whole fan.
                # That asymmetry between the two predicates is what "the legs clear no smoothing of the centreline" was on B17's socket and
                # switch sections: both legs cleared the corridor and hit at the first cell of the tail run (8 Sep 2026 22:30, 32.75).
                if any(q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and (row_scheme(q.GetParentFootprint()) or via_entry(q.GetParentFootprint())) for q in st): return False
                return entry_station(st)
            def entry_cells(frm, to):
                """Straight cells (i, j) from cell frm to cell to (Bresenham), both included."""
                (j0, i0), (j1, i1) = frm, to; n = max(abs(i1 - i0), abs(j1 - j0), 1)
                return [(int(round(i0 + (i1 - i0) * k / n)), int(round(j0 + (j1 - j0) * k / n))) for k in range(n + 1)]
            FL = layers.index(pcbnew.F_Cu) if pcbnew.F_Cu in layers else None
            fineA, fineB = fine_station((pa, na)), fine_station((pb, nb))
            runs = simplify(path); head_run = tail_run = None
            if FL is not None and fineB:   # the far station: from the corridor's end straight into the pad pair on F.Cu, a run of its own (never smoothed into the corridor)
                mB = gr.cell(*entry_target((pb, nb))); tail_run = [(FL, i, j) for i, j in entry_cells((path[-1][2], path[-1][1]), mB)]
                runs = runs + [tail_run]
            if FL is not None and fineA:
                mA = gr.cell(*entry_target((pa, na))); head_run = [(FL, i, j) for i, j in entry_cells(mA, (path[0][2], path[0][1]))]
                runs = [head_run] + runs
            cells += len(path); nruns += len(runs); laid_sections += 1
            first = runs[0]; (x0, y0) = gr.xy(first[0][2], first[0][1]); (x1, y1) = gr.xy(first[-1][2], first[-1][1]) if len(first) > 1 else (gx, gy)
            cross = (x1 - x0) * (A[0][1] - y0) - (y1 - y0) * (A[0][0] - x0); p_side = 1 if cross > 0 else -1   # which leg is left of the centreline: the P anchor's side
            prev_end = None; lp = ln = None
            # a twist: the P pad lies on one side of the line from station A to station B at A and on the other at B (a property of the placement, not of the path)
            dxab, dyab = gx - sx, gy - sy
            side_a = dxab * (A[0][1] - sy) - dyab * (A[0][0] - sx); side_b = dxab * (B[0][1] - gy) - dyab * (B[0][0] - gx)
            crossing = False
            def sigma(st):
                p_, n_ = st; mx_, my_ = mid(st); fa_, fb_ = p_.GetParentFootprint(), n_.GetParentFootprint(); fx_, fy_ = [(a_ + b_) / 2 for a_, b_ in zip(fp_centre(fa_), fp_centre(fb_))]
                dx_, dy_ = n_.GetPosition().x / 1e6 - p_.GetPosition().x / 1e6, n_.GetPosition().y / 1e6 - p_.GetPosition().y / 1e6; ln_ = math.hypot(dx_, dy_) or 1.0; nx_, ny_ = -dy_ / ln_, dx_ / ln_
                if (mx_ - fx_) * nx_ + (my_ - fy_) * ny_ < 0: nx_, ny_ = -nx_, -ny_
                return 1 if nx_ * (-dy_) - ny_ * (-dx_) > 0 else -1   # the P pad's side of the outward normal
            if fineA0 or fineB0: side_a, side_b = 1.0, -1.0   # an entry station's twist is settled when its fan is laid (a swap of the two passives there)
            if side_a * side_b < 0 and min(abs(side_a), abs(side_b)) > 1e-6:
                def swappable_(x_, y_):
                    fa_, fb_ = x_.GetParentFootprint(), y_.GetParentFootprint()
                    return fa_.GetReference() != fb_.GetReference() and fa_.GetFPIDAsString() == fb_.GetFPIDAsString() and abs(fa_.GetOrientationDegrees() - fb_.GetOrientationDegrees()) < 0.01 and not fa_.IsLocked() and not fb_.IsLocked() and not pinned(fa_) and not pinned(fb_) and stem not in swapped
                if swappable_(pb, nb): twist = ("%s -> %s" % (pa.GetParentFootprint().GetReference(), pb.GetParentFootprint().GetReference()), pb, nb); break
                if swappable_(pa, na): twist = ("%s -> %s" % (pa.GetParentFootprint().GetReference(), pb.GetParentFootprint().GetReference()), pa, na); break
                crossing = True   # both stations are fixed parts (a connector, a hub): the legs cross once at the near station, one stub under the other
            def legs_clear(sm):   # each offset leg of every run against its own single-track map (the other leg and every other net are obstacles)
                for r_i, run in enumerate(runs):
                    L = layers[run[0][0]]; pts = [gr.xy(j, i) for i, j in sm[r_i]]
                    if len(pts) == 1: pts = pts * 2
                    first_run, last_run = r_i == 0, r_i == len(runs) - 1
                    for poly, net in ((offset_polyline(pts, dof(L) * p_side), pn), (offset_polyline(pts, -dof(L) * p_side), nn)):
                        total = sum(math.hypot(poly[k + 1][0] - poly[k][0], poly[k + 1][1] - poly[k][1]) for k in range(len(poly) - 1)); walked = 0.0
                        for k in range(len(poly) - 1):
                            (x1, y1), (x2, y2) = poly[k], poly[k + 1]; ln_ = math.hypot(x2 - x1, y2 - y1); n = int(ln_ / gr.G) * 2 + 2
                            for q in range(n + 1):
                                u = q / n; along = walked + u * ln_
                                if (first_run and fineA and along < 1.2) or (last_run and fineB and total - along < 1.2): continue   # the fine-pitch entry ends inside the pad pair
                                px_, py_ = x1 + u * (x2 - x1), y1 + u * (y2 - y1)
                                jj, ii = gr.cell(px_, py_)
                                if 0 <= ii < gr.NY and 0 <= jj < gr.NX and trk1[net][L][ii, jj]:
                                    # The map is a raster and the leg's margin over it is smaller than a cell (the note at
                                    # `_cover` above has the arithmetic), so a blocked CELL is not yet a blocked LEG. Before
                                    # refusing the whole pair for one point, ask the geometry: the map grows an obstacle by
                                    # CLR + w/2 + 0.02, so the same question exactly is whether the nearest edge is that far.
                                    # Measured on D: 0.367 mm against a 0.330 demand, refused by 37 micrometres of rounding.
                                    # PAIR_LEG_EXACT=1 turns it on; it costs a local scan only where a pair would be refused.
                                    if not LEG_EXACT: return False
                                    _need = CLR + wid(L) / 2 + 0.02
                                    _d = _nearest_edge(px_, py_, L, net, limit=_need + 0.5)
                                    if _d is None or _d < _need: return False
                            walked += ln_
                return True
            def dp(pts_cells, tol):
                """Douglas-Peucker on cells: the fewest vertices within tol cells of the raw run."""
                if len(pts_cells) <= 2: return list(pts_cells)
                (i0, j0), (i1, j1) = pts_cells[0], pts_cells[-1]; dx_, dy_ = i1 - i0, j1 - j0; ln_ = math.hypot(dx_, dy_) or 1.0
                far = max(range(1, len(pts_cells) - 1), key=lambda k: abs((pts_cells[k][0] - i0) * dy_ - (pts_cells[k][1] - j0) * dx_) / ln_)
                dmax = abs((pts_cells[far][0] - i0) * dy_ - (pts_cells[far][1] - j0) * dx_) / ln_
                if dmax <= tol: return [pts_cells[0], pts_cells[-1]]
                return dp(pts_cells[:far + 1], tol)[:-1] + dp(pts_cells[far:], tol)
            def los_ok(cells, passable):
                for a_, b_ in zip(cells[:-1], cells[1:]):
                    n = max(abs(b_[0] - a_[0]), abs(b_[1] - a_[1])) * 4 + 1
                    for k in range(n + 1):
                        u = k / n; i = int(round(a_[0] + u * (b_[0] - a_[0]))); j = int(round(a_[1] + u * (b_[1] - a_[1])))
                        if not passable[i, j]: return False
                return True
            smoothed = None; staircase = False
            cand = [smooth(gr, [(c[1], c[2]) for c in run], ~trk[layers[run[0][0]]], None) for run in runs]
            if legs_clear(cand): smoothed = cand
            else:
                for tol in (1.5, 2.5, 4.0):   # gentler polylines (few long segments at free angles)
                    cand = [dp([(c[1], c[2]) for c in run], tol) for run in runs]
                    if all(los_ok(c, ~trk[layers[run[0][0]]]) for c, run in zip(cand, runs)) and legs_clear(cand): smoothed = cand; break
            if smoothed is None and os.environ.get("PAIR_STAIRCASE", "1") != "0":
                # 9 September 2026 (B19): the last resort is the corridor as the search found it, tidied only enough to drop
                # single-cell jitter. Until tonight the tool refused a staircase on quality grounds and left the pair to the
                # router instead, and `pair_report.py` measured what that costs: THIRTEEN of the first twenty four failures
                # were this one line. A staircase pair is coupled, holds its class geometry and can be straightened later by
                # `straighten.py`; a pair left to the router is uncoupled and fails the impedance gate. The owner's ruling of
                # 9 September is that the pairs are laid in the pre-router, so the coupled staircase wins on the requirement.
                for tol in (0.6, 0.0):
                    cand = [dp([(c[1], c[2]) for c in run], tol) if tol else [(c[1], c[2]) for c in run] for run in runs]
                    if all(los_ok(c, ~trk[layers[run[0][0]]]) for c, run in zip(cand, runs)) and legs_clear(cand):
                        smoothed = cand; staircase = True; break
            if smoothed is None:
                failed = "%s -> %s (the legs clear no smoothing of the centreline)" % (pa.GetParentFootprint().GetReference(), pb.GetParentFootprint().GetReference())
                if os.environ.get("PAIR_DEBUG"):
                    # where the legs hit: the first forbidden cell of each leg on the raw path, under the SAME exemption legs_clear uses
                    # (the first and last 1.2 mm at a fine-pitch station are inside the pad pair and are not obstacles). Without the
                    # exemption this print named a cell 0.23 mm from the pad that legs_clear had already skipped, and an evening went
                    # into a theory about pair escapes at the socket that the tool was never blocked by (8 Sep 2026 22:15).
                    for r_i, run in enumerate(runs):
                        L = layers[run[0][0]]; pts = [gr.xy(c[2], c[1]) for c in run]
                        first_run, last_run = r_i == 0, r_i == len(runs) - 1
                        for poly, net in ((offset_polyline(pts, dof(L) * p_side), pn), (offset_polyline(pts, -dof(L) * p_side), nn)):
                            seg = [math.hypot(poly[k + 1][0] - poly[k][0], poly[k + 1][1] - poly[k][1]) for k in range(len(poly) - 1)]
                            total = sum(seg); walked = 0.0; hit = None
                            for k in range(len(poly) - 1):
                                if not ((first_run and fineA and walked < 1.2) or (last_run and fineB and total - walked < 1.2)):
                                    jj, ii = gr.cell(*poly[k])
                                    if 0 <= ii < gr.NY and 0 <= jj < gr.NX and trk1[net][L][ii, jj]: hit = (poly[k], walked); break
                                walked += seg[k]
                            if hit:
                                # Is the CENTRELINE free where the leg is not? The corridor map is grown by `half` (the pair's
                                # half width plus the slack) and the leg maps by half a leg plus 0.02, so a leg 0.25 mm off the
                                # centreline reaches 0.42 mm out against the 0.52 mm the corridor guarantees, and the legs can
                                # only fail where the two maps disagree or where the offset itself has left the corridor.
                                _cl = min(pts, key=lambda q: math.hypot(q[0] - hit[0][0], q[1] - hit[0][1]))
                                _jj, _ii = gr.cell(*_cl)
                                _cb = trk[L][_ii, _jj] if 0 <= _ii < gr.NY and 0 <= _jj < gr.NX else True
                                print("pair_preroute: leg %s hits an obstacle at (%.2f, %.2f) on %s, %.2f mm along run %d of %d: %s | the centreline %.2f mm away at (%.2f, %.2f) is %s in the corridor map (half %.2f, leg offset %.2f)"
                                      % (net, hit[0][0], hit[0][1], b.GetLayerName(L), hit[1], r_i + 1, len(runs), _what_is_at(hit[0][0], hit[0][1], L, net),
                                         math.hypot(_cl[0] - hit[0][0], _cl[1] - hit[0][1]), _cl[0], _cl[1], "BLOCKED" if _cb else "free", half, dof(L)))
                            else: print("pair_preroute: leg %s clears run %d of %d on %s (the blocker is another run or the smoothing)" % (net, r_i + 1, len(runs), b.GetLayerName(L)))
                break
            merged = []   # [(layer index, points)] with consecutive same-layer runs joined into one polyline
            for r_i, run in enumerate(runs):
                pts_ = [gr.xy(j, i) for i, j in smoothed[r_i]]
                if merged and merged[-1][0] == run[0][0]: merged[-1][1].extend(pts_[1:] if pts_ and merged[-1][1] and pts_[0] == merged[-1][1][-1] else pts_)
                else: merged.append((run[0][0], list(pts_)))
            runs = [[(li, 0, 0)] for li, _ in merged]; smoothed = [None] * len(merged)   # the loop below reads the layer from runs and the points from merged
            for r_i, run in enumerate(runs):
                L = layers[run[0][0]]; pts = list(merged[r_i][1])
                if len(pts) == 1: pts = pts * 2
                lp = offset_polyline(pts, dof(L) * p_side); ln = offset_polyline(pts, -dof(L) * p_side)
                for poly, net in ((lp, net_p), (ln, net_n)):
                    for k in range(len(poly) - 1): seg(poly[k][0], poly[k][1], poly[k + 1][0], poly[k + 1][1], L, net)
                if r_i > 0 and layers[runs[r_i - 1][0][0]] == L:   # the same layer (an entry run meets the corridor): the legs join with a short piece
                    for poly_start, prev_poly_end, net in ((lp[0], prev_end[0], net_p), (ln[0], prev_end[1], net_n)): seg(prev_poly_end[0], prev_poly_end[1], poly_start[0], poly_start[1], L, net)
                elif r_i > 0:   # the layer change: two vias VIA_SPLIT either side of the centreline, on the previous run's last direction, walked back until both sites are free
                    ppts = list(merged[r_i - 1][1])
                    if len(ppts) == 1: ppts = ppts * 2
                    (ax, ay), (qx, qy) = ppts[-1], ppts[-2]; dx, dy = ax - qx, ay - qy; ll = math.hypot(dx, dy)
                    if ll < 1e-6: (bx, by) = pts[1]; dx, dy = bx - pts[0][0], by - pts[0][1]; ll = math.hypot(dx, dy) or 1.0
                    ux, uy = dx / ll, dy / ll; nx, ny = -uy, ux
                    Lprev = layers[runs[r_i - 1][0][0]]
                    (fx_, fy_) = pts[1]; fdx, fdy = fx_ - pts[0][0], fy_ - pts[0][1]; fl_ = math.hypot(fdx, fdy) or 1.0; fux, fuy = fdx / fl_, fdy / fl_   # the next run's first direction
                    def pair_free(cx_, cy_, nx_, ny_, split_):
                        for sign in (p_side, -p_side):
                            jj, ii = gr.cell(cx_ + nx_ * split_ * sign, cy_ + ny_ * split_ * sign)
                            if not (0 <= ii < gr.NY and 0 <= jj < gr.NX) or via1n[net_p.GetNetname() if sign == p_side else net_n.GetNetname()][ii, jj]: return False
                        return abs(2 * split_) >= vd + clr_c + 0.02
                    spot = None
                    for split_ in (VIA_SPLIT, 0.7, 0.55):   # the vias either side of the centreline; closer when the corridor is tight (their spacing stays a via plus the clearance)
                        if not (r_i == 1 and fineA):   # back along the previous run (never into an entry run: that is the pad row), up to 8 mm
                            for k_ in range(0, 81):
                                if pair_free(ax - ux * 0.1 * k_, ay - uy * 0.1 * k_, nx, ny, split_): spot = (ax - ux * 0.1 * k_, ay - uy * 0.1 * k_, nx, ny, split_); break
                        if spot is None:   # forward along the next run
                            for k_ in range(0, 81):
                                if pair_free(ax + fux * 0.1 * k_, ay + fuy * 0.1 * k_, -fuy, fux, split_): spot = (ax + fux * 0.1 * k_, ay + fuy * 0.1 * k_, -fuy, fux, split_); break
                        if spot is not None: break
                    if spot is None: failed = "%s -> %s (no room for the layer-change via pair)" % (pa.GetParentFootprint().GetReference(), pb.GetParentFootprint().GetReference()); break
                    cx_, cy_, nx, ny, split_ = spot
                    for sign, net, poly_start, prev_poly_end in ((p_side, net_p, lp[0], prev_end[0]), (-p_side, net_n, ln[0], prev_end[1])):
                        vx, vy = cx_ + nx * split_ * sign, cy_ + ny * split_ * sign
                        seg(prev_poly_end[0], prev_poly_end[1], vx, vy, Lprev, net); via_at(vx, vy, net); seg(vx, vy, poly_start[0], poly_start[1], L, net)
                prev_end = (lp[-1], ln[-1])
            if failed: break
            firstL = layers[runs[0][0][0]]; lastL = layers[runs[-1][0][0]]
            first_pts = list(merged[0][1]); last_pts = list(merged[-1][1])
            if len(first_pts) == 1: first_pts = first_pts * 2
            if len(last_pts) == 1: last_pts = last_pts * 2
            lp0, ln0 = offset_polyline(first_pts, dof(firstL) * p_side)[0], offset_polyline(first_pts, -dof(firstL) * p_side)[0]
            lp1, ln1 = offset_polyline(last_pts, dof(lastL) * p_side)[-1], offset_polyline(last_pts, -dof(lastL) * p_side)[-1]
            def end_crossing(P, Nn, lp_, ln_):
                """The stubs of an end cross when the P pad lies on the other side of the leg-pair axis than the P leg's offset end."""
                ux, uy = ln_[0] - lp_[0], ln_[1] - lp_[1]   # across the legs, P to N
                mx, my = (lp_[0] + ln_[0]) / 2, (lp_[1] + ln_[1]) / 2; px_, py_ = (P[0] + Nn[0]) / 2, (P[1] + Nn[1]) / 2
                ax_, ay_ = px_ - mx, py_ - my   # along: from the legs' ends to the station
                side_leg = ax_ * uy - ay_ * ux
                side_pad = ax_ * (Nn[1] - P[1]) - ay_ * (Nn[0] - P[0])
                return side_leg * side_pad < 0
            cross_near = end_crossing(A[0], A[1], lp0, ln0); cross_far = end_crossing(B[0], B[1], lp1, ln1)
            if crossing and not (cross_near or cross_far): pass
            ends = ((A[0], lp0, firstL, net_p, True, 1), (A[1], ln0, firstL, net_n, True, -1), (B[0], lp1, lastL, net_p, False, 1), (B[1], ln1, lastL, net_n, False, -1))
            for (x, y, aL, obj), (ex, ey), L, net, near, sgn in ends:
                if (near and fineA) or (not near and fineB):
                    st_ = (pa, na) if near else (pb, nb)
                    if dist_p(*st_) > 0.7 and net is net_p:   # the fan into a side-by-side pair, both legs at once (the N leg's turn is skipped below)
                        lpx, lpy = (ex, ey); lnx, lny = (ln0 if near else ln1)
                        def xing():
                            """The two fans against each other and against every top-layer piece of the other leg laid so far (an L-shaped corridor twists the order)."""
                            P_ = (mm(st_[0].GetPosition().x), mm(st_[0].GetPosition().y)); N_ = (mm(st_[1].GetPosition().x), mm(st_[1].GetPosition().y))
                            def ccw(a_, b_, c_): return (c_[1] - a_[1]) * (b_[0] - a_[0]) > (b_[1] - a_[1]) * (c_[0] - a_[0])
                            def isx(a_, b_, c_, d_): return ccw(a_, c_, d_) != ccw(b_, c_, d_) and ccw(a_, b_, c_) != ccw(a_, b_, d_)
                            if isx((lpx, lpy), P_, (lnx, lny), N_): return True
                            for t in pieces:
                                if t.GetClass() != "PCB_TRACK" or t.GetLayer() != pcbnew.F_Cu: continue
                                a_ = (mm(t.GetStart().x), mm(t.GetStart().y)); b_ = (mm(t.GetEnd().x), mm(t.GetEnd().y))
                                if t.GetNetname() == nn and isx((lpx, lpy), P_, a_, b_): return True
                                if t.GetNetname() == pn and isx((lnx, lny), N_, a_, b_): return True
                            return False
                        if xing():
                            fa_, fb_ = st_[0].GetParentFootprint(), st_[1].GetParentFootprint()
                            if SWAP_OK and not (SWAP_BOTH and swap_breaks_other_side(fa_, fb_, (pn, nn))) and fa_.GetReference() != fb_.GetReference() and fa_.GetFPIDAsString() == fb_.GetFPIDAsString() and not fa_.IsLocked() and not fb_.IsLocked() and not pinned(fa_) and not pinned(fb_):
                                pa_, pb_ = fa_.GetPosition(), fb_.GetPosition(); fa_.SetPosition(pb_); fb_.SetPosition(pa_); MAP_EPOCH[0] += 1; report.append("SWAP  %s: %s and %s exchanged positions so the legs fan into their pads without crossing" % (stem, fa_.GetReference(), fb_.GetReference())); rebuild_maps()
                            if xing():   # still crossing (one part's two pins, a pinned station): the N fan is laid straight and the P leg dives under it (8 Sep 2026 12:26)
                                # the N fan first runs 0.5 mm on along the corridor, then turns: its diagonal passed 1 um under the class clearance at P's turn into the dive (13:08)
                                ax2, ay2 = (lnx - lpx), (lny - lpy); al2 = math.hypot(ax2, ay2) or 1.0; ux2, uy2 = -ay2 / al2, ax2 / al2
                                smx, smy = (mm(st_[0].GetPosition().x) + mm(st_[1].GetPosition().x)) / 2, (mm(st_[0].GetPosition().y) + mm(st_[1].GetPosition().y)) / 2
                                if (smx - lnx) * ux2 + (smy - lny) * uy2 < 0: ux2, uy2 = -ux2, -uy2
                                lnx2, lny2 = lnx + 0.5 * ux2, lny + 0.5 * uy2
                                seg(lnx, lny, lnx2, lny2, pcbnew.F_Cu, net_n); seg(lnx2, lny2, mm(st_[1].GetPosition().x), mm(st_[1].GetPosition().y), pcbnew.F_Cu, net_n)
                                nnx_, nny_ = (lnx - lpx, lny - lpy); nl2_ = math.hypot(nnx_, nny_) or 1.0
                                err_ = dive_p(mm(st_[0].GetPosition().x), mm(st_[0].GetPosition().y), lpx, lpy, pcbnew.F_Cu, None, st_[0], net_p, (-nnx_ / nl2_, -nny_ / nl2_))
                                if err_: failed = "%s -> %s (the fan into %s crosses, %s)" % (pa.GetParentFootprint().GetReference(), pb.GetParentFootprint().GetReference(), st_[0].GetParentFootprint().GetReference(), err_); break
                                report.append("DIVE  %s: the P leg crosses under the N fan into %s on %s" % (stem, st_[0].GetParentFootprint().GetReference(), b.GetLayerName(hop_of(pcbnew.F_Cu) or pcbnew.F_Cu)))
                                continue
                        okp = fan_leg(lpx, lpy, mm(st_[0].GetPosition().x), mm(st_[0].GetPosition().y), pcbnew.F_Cu, net_p)
                        okn = fan_leg(lnx, lny, mm(st_[1].GetPosition().x), mm(st_[1].GetPosition().y), pcbnew.F_Cu, net_n)
                        if not (okp and okn): failed = "%s -> %s (the fan into %s is blocked and has no path)" % (pa.GetParentFootprint().GetReference(), pb.GetParentFootprint().GetReference(), st_[0].GetParentFootprint().GetReference()); break
                    continue   # a fine pitch: the legs entered the pads straight; the N leg of a fan was laid with the P leg
                crossing = cross_near if near else cross_far
                nnx, nny = (ln0[0] - lp0[0], ln0[1] - lp0[1]) if near else (ln1[0] - lp1[0], ln1[1] - lp1[1]); nl_ = math.hypot(nnx, nny) or 1.0
                away = (-sgn * nnx / nl_, -sgn * nny / nl_)   # from the other leg's end towards this one, continued
                _pf = obj.GetParentFootprint() if hasattr(obj, "GetParentFootprint") else None; ref_ = _pf.GetReference() if _pf else "via"   # a via's parent is None
                def fail_(what): return "%s -> %s (%s for %s at %s)" % (pa.GetParentFootprint().GetReference(), pb.GetParentFootprint().GetReference(), what, net.GetNetname(), ref_)
                if crossing and net is net_p:
                    err_ = dive_p(x, y, ex, ey, L, aL, obj, net, away)
                    if err_: failed = fail_(err_); break
                    continue
                if aL is None or aL == L:   # the pad (or an escape via) is on the corridor layer
                    if not stub(ex, ey, x, y, L, net): failed = fail_("no stub path"); break
                    continue
                site = via_hop(ex, ey, x, y, L, aL, net, away)   # the pad is on another layer: a via near the offset end with a hop path, the stub on the pad's layer
                if site is None: failed = fail_("no via site with a hop path"); break
                via_at(site[0], site[1], net); gr.disc(via, site[0], site[1], VIA_SPLIT)
                if not stub(site[0], site[1], x, y, aL, net): failed = fail_("no stub path"); break
            if failed: break
        if PLAN_MODE:   # a planning half-iteration searches and gives nothing back to the board
            rollback()
            continue
        if twist:
            rollback()
            # the P leg changes side between two stations: when the far station is two identical passives (the series resistors of the two legs), swapping
            # their positions is a legal pre-route placement move that untwists the pair (the packer placed them in arbitrary order); done once, then the pair is laid again
            twist, pa2, na2 = twist
            fa, fb = pa2.GetParentFootprint(), na2.GetParentFootprint()
            if SWAP_OK and not (SWAP_BOTH and swap_breaks_other_side(fa, fb, (pn, nn))) and fa.GetReference() != fb.GetReference() and fa.GetFPIDAsString() == fb.GetFPIDAsString() and abs(fa.GetOrientationDegrees() - fb.GetOrientationDegrees()) < 0.01 and not fa.IsLocked() and not fb.IsLocked() and stem not in swapped and not pinned(fa) and not pinned(fb):
                pa_, pb_ = fa.GetPosition(), fb.GetPosition(); fa.SetPosition(pb_); fb.SetPosition(pa_); MAP_EPOCH[0] += 1; swapped.add(stem)   # a swap moves pads, so every cached occupancy map is stale
                for t in [t for t in b.GetTracks() if t.GetNetname() in (pn, nn) and t not in stripped]: board_remove(b, t)   # its locked pieces so far go with the retry
                for t in stripped: b.Add(t)
                stripped.clear()
                report.append("SWAP  %s: %s and %s exchanged positions to untwist the pair; laid again" % (stem, fa.GetReference(), fb.GetReference())); stems.append(stem); continue
            why = ("one part's two pins" if fa.GetReference() == fb.GetReference() else ("different footprints %s / %s" % (fa.GetFPIDAsString().split(":")[-1], fb.GetFPIDAsString().split(":")[-1]) if fa.GetFPIDAsString() != fb.GetFPIDAsString() else ("orientations %s / %s" % (fa.GetOrientationDegrees(), fb.GetOrientationDegrees()) if abs(fa.GetOrientationDegrees() - fb.GetOrientationDegrees()) >= 0.01 else ("locked" if fa.IsLocked() or fb.IsLocked() else "already swapped once"))))
            report.append("TWIST %s: the P leg changes side between the stations %s (no swap: %s); a crossing would be needed, left to the router" % (stem, twist, why)); continue
        if failed:
            rollback()
            blockers = []
            if RIPUP and episode[0] is None and rip_done[0] < RIP_TOTAL and rip_events.get(stem, 0) < RIPUP:
                x1_, y1_, x2_, y2_ = cur_seg
                for st2, (pcs2, _s2) in on_board.items():
                    if st2 in swapped: continue   # a swapped pair's escapes were stripped at the old positions and the swap is not undone
                    d2 = _in_way(pcs2, x1_, y1_, x2_, y2_)
                    if d2 <= RIP_MARGIN: blockers.append((d2, st2))
                blockers = [s2 for _d2, s2 in sorted(blockers)[:RIP_MAX]]
            if blockers:
                rip_events[stem] = rip_events.get(stem, 0) + 1; rip_done[0] += 1
                saved = {}
                for st2 in blockers:
                    pcs2, str2 = on_board.pop(st2); saved[st2] = (pcs2, str2)
                    for t_ in pcs2: board_remove(b, t_)
                    for t_ in str2: b.Add(t_)   # that pair's escape pieces come back with it
                    laid -= 1
                episode[0] = {"trigger": stem, "members": set([stem]) | set(blockers), "saved": saved, "laid_before": laid + len(blockers)}
                stems.append(stem); stems.extend(blockers)
                report.append("RIPUP %s: section %s is blocked; %d laid pair(s) taken off the board (%s), this pair is laid again first and they follow" % (stem, failed, len(blockers), ", ".join(blockers)))
                continue
            # 10 September 2026, measured both ways: ending the legs at an IC's escape vias instead of stripping the escape and
            # entering the pads lays 27 more of B19's 113 pairs and COSTS D10 two of its five, so it is not a mode to switch on.
            # It is a fallback: the pads are tried first, and a pair that fails is laid again ending at the vias.
            if not ENTRY_VIA and stem not in via_entry_stems:
                via_entry_stems.add(stem); stems.append(stem)
                report.append("ENTRY %s: section %s failed with the legs entering the pads; laid again ending at the escape vias" % (stem, failed))
                continue
            if stem not in slim_stems and SLACK_SLIM < SLACK:
                slim_stems.add(stem); stems.append(stem)
                report.append("SLIM  %s: section %s; searched again with the corridor at %.2f mm of slack instead of %.2f" % (stem, failed, SLACK_SLIM, SLACK))
                continue
            report.append("FAIL  %s: section %s on %s at w %.2f s %.2f (%d of %d sections laid before it)" % (stem, failed, ",".join(b.GetLayerName(L) for L in layers), w, s, laid_sections, len(sections)))
            continue
        # every other pad of the two nets (a pull resistor, a test point, a part's second pin) gets a stub to the nearest laid piece of its net, so the router
        # has nothing left on a pair net (8 Sep 2026: Freerouting wandered 15 to 23 pieces over three layers to reach D9's pull-downs and the read-back called the pairs uncoupled)
        left = 0; stubs_ = 0; dives_ = 0; rebuild_maps()
        for net_obj, net in ((net_p, pn), (net_n, nn)):
            laid_pts = [(mm(t.GetStart().x), mm(t.GetStart().y), t.GetLayer()) for t in pieces if t.GetClass() == "PCB_TRACK" and t.GetNetname() == net] + [(mm(t.GetEnd().x), mm(t.GetEnd().y), t.GetLayer()) for t in pieces if t.GetClass() == "PCB_TRACK" and t.GetNetname() == net]
            if not laid_pts: continue
            station_pads = {(q.GetParentFootprint().GetReference(), q.GetNumber()) for st in stations for q in st}
            for f in b.GetFootprints():
                for q in f.Pads():
                    if q.GetNetname() != net or (f.GetReference(), q.GetNumber()) in station_pads: continue
                    qx, qy = mm(q.GetPosition().x), mm(q.GetPosition().y)
                    if any(math.hypot(qx - x_, qy - y_) < 0.3 for x_, y_, _ in laid_pts): continue   # already on the copper
                    near = sorted(laid_pts, key=lambda t: math.hypot(qx - t[0], qy - t[1]))[:6]
                    if math.hypot(qx - near[0][0], qy - near[0][1]) > 12.0: left += 1; continue   # too far: the router's
                    qL = None if q.GetAttribute() != pcbnew.PAD_ATTRIB_SMD else next((L for L in _ALL.values() if q.IsOnLayer(L)), None)
                    done = False
                    for x_, y_, L_ in near:
                        SL = qL if (qL is not None and qL == L_) else L_
                        if qL is not None and qL != L_:   # the pad on another layer: a via beside it, the stub on the pad's layer
                            site = via_hop(x_, y_, qx, qy, L_, qL, net_obj, (0.0, 0.0)) if L_ in trk1[net] else None
                            if site is None: continue
                            via_at(site[0], site[1], net_obj); gr.disc(via, site[0], site[1], VIA_SPLIT)
                            if stub(site[0], site[1], qx, qy, qL, net_obj): done = True; break
                            continue
                        if SL in trk1[net] and stub(x_, y_, qx, qy, SL, net_obj): done = True; break
                    if not done:   # the pad across the other leg (a pull-down whose side flipped with a swap): the stub dives under it on the other corridor layer (8 Sep 2026 12:59)
                        for x_, y_, L_ in near[:3]:
                            if L_ not in layers: continue
                            n0 = len(pieces)
                            if dive_p(qx, qy, x_, y_, L_, (None if (qL is None or qL == L_) else qL), q, net_obj, (0.0, 0.0)) is None: done = True; dives_ += 1; break
                            for t in pieces[n0:]: board_remove(b, t)
                            del pieces[n0:]
                    if done: stubs_ += 1
                    else: left += 1
        if stubs_ or left: report.append("STUBS %s: %d other pad(s) of the pair nets stubbed to the laid copper (%d by a dive), %d left to the router" % (stem, stubs_, dives_, left))
        # 9 Sep 2026 (D10 USB3, appendix 32.83): THE TWO LEGS OF A PAIR MAY NEVER CROSS EACH OTHER. Around a hairpin the
        # offset legs can swap sides and swap back, which D10's USB3 did twice on F.Cu and shipped two tracks_crossing
        # violations between USB3_P and USB3_N into the pre-route gate. A pair the pre-router cannot lay is one unrouted
        # net the router will take; a pair it lays crossed is a short. The pair is rolled back and reported instead.
        _segs = {}
        for _t in pieces:
            if _t.GetClass() != "PCB_TRACK": continue
            _segs.setdefault((_t.GetNetname(), _t.GetLayer()), []).append((mm(_t.GetStart().x), mm(_t.GetStart().y), mm(_t.GetEnd().x), mm(_t.GetEnd().y)))
        def _hit(a, c, d, e, f, g_, h, i_):
            def _o(px, py, qx, qy, rx, ry): return (qx - px) * (ry - py) - (qy - py) * (rx - px)
            o1, o2, o3, o4 = _o(a, c, d, e, f, g_), _o(a, c, d, e, h, i_), _o(f, g_, h, i_, a, c), _o(f, g_, h, i_, d, e)
            return (o1 > 1e-9) != (o2 > 1e-9) and (o3 > 1e-9) != (o4 > 1e-9) and abs(o1) + abs(o2) + abs(o3) + abs(o4) > 1e-9
        _cross = 0
        for _L in {k[1] for k in _segs}:
            for _a in _segs.get((pn, _L), []):
                for _b2 in _segs.get((nn, _L), []):
                    if _hit(*_a, *_b2): _cross += 1
        if _cross:
            rollback()
            # 10 September 2026: a crossing used to end the pair here, while a section failure got the escape-via fallback.
            # The crossings are 12 of the 64 misses that remain once the corridor slack is right, and the fallback changes
            # where the legs end, which is where most of them cross. The pair takes the same second chance.
            if not ENTRY_VIA and stem not in via_entry_stems:
                via_entry_stems.add(stem); stems.append(stem)
                report.append("ENTRY %s: the two legs crossed %d time(s) with the legs entering the pads; laid again ending at the escape vias" % (stem, _cross))
                continue
            report.append("FAIL  %s: the two legs cross each other %d time(s) on the laid path; rolled back, the router takes the pair" % (stem, _cross))
            continue
        laid += 1; on_board[stem] = (list(pieces), list(stripped))
        report.append("LAID  %s: class %s w %.2f s %.2f, %d sections over %d stations, %d cells, %d runs, %d pieces added%s" % (stem, cls_of(pn), w, s, len(sections), len(stations), cells, nruns, added, " (staircase corridor)" if staircase else ""))
    settle_episode()   # an episode that was still open at the end of the list is judged like any other
    if PLAN_MODE:
        _po = os.environ.get("PAIR_PLAN_OUT")
        if _po: json.dump(plan_out, open(_po, "w"))
        _done = sum(1 for v in plan_out.values() if v and all(x for x in v))
        _cL, _ci, _cj, _cv = [], [], [], []
        for _k, _occ in (NEG_OCC or {}).items():
            _ii, _jj = np.nonzero(_occ > 1)
            _cL.extend([_k] * len(_ii)); _ci.extend(_ii.tolist()); _cj.extend(_jj.tolist()); _cv.extend((_occ[_ii, _jj] - 1).tolist())
        _co = os.environ.get("PAIR_CONFLICT_OUT")
        if _co: np.savez_compressed(_co, L=np.array(_cL, dtype=np.int16), i=np.array(_ci, dtype=np.int32), j=np.array(_cj, dtype=np.int32), v=np.array(_cv, dtype=np.int16))
        print("pair_preroute: PLAN %d of %d pairs have a corridor for every section, %d contested cell(s)" % (_done, len(set(stems)), len(_cv)))
        return 0 if _done == len(set(stems)) else 1
    out = board if not test else board.replace(".kicad_pcb", "-pairs.kicad_pcb")
    pcbnew.SaveBoard(out, b)
    print("pair_preroute: --- summary ---")
    for l in report: print("pair_preroute: " + l)
    n_pairs = len(set(stems))   # a swapped pair is appended for its retry and counts once
    _moved = [(r_, _POS0[r_], (f_.GetPosition().x, f_.GetPosition().y)) for f_ in b.GetFootprints()
              for r_ in [f_.GetReference()] if r_ in _POS0 and _POS0[r_] != (f_.GetPosition().x, f_.GetPosition().y)]
    for r_, a_, c_ in sorted(_moved):
        print("pair_preroute: MOVED %s from (%.2f, %.2f) to (%.2f, %.2f)" % (r_, mm(a_[0]), mm(a_[1]), mm(c_[0]), mm(c_[1])))
    if _moved: print("pair_preroute: %d footprint(s) moved by this pass" % len(_moved))
    print("pair_preroute: %d of %d pairs laid, %d rip-up event(s) -> %s" % (laid, n_pairs, rip_done[0], out))
    print("pair_preroute: search kernel %s%s" % (_SEARCH_KERNEL, (", rasteriser fell back to the per-cell predicate %d time(s)" % _RASTER_FALLBACK[0]) if _RASTER_FALLBACK[0] else ""))
    # `_T["maps"]` already counted this and a second counter beside it would be one more pair of numbers to drift apart,
    # which this project has paid for twice. The map mode and the call count join the line that exists (11 Sep 2026).
    _known = _T["maps"] + _T["astar"] + _T["stubs"] + _T["legs"] + _T["stamp"]
    print("pair_preroute: seconds %.0f total, %.0f in the occupancy maps (%d call(s), mode %s%s), %.0f in the corridor search, "
          "%.0f in the stub search, %.0f in the leg offsets, %.0f stamping laid copper, %.0f elsewhere; %d expansions"
          % (time.time() - T0, _T["maps"], MAP_CALLS[0], MAP_MODE, ", CHECKED against the reference" if MAP_CHECK else "",
             _T["astar"], _T["stubs"], _T["legs"], _T["stamp"], max(0.0, time.time() - T0 - _known), PAIR_TOTAL[0]))
    print("pair_preroute: calls %s" % ", ".join("%s %d" % (k, _N[k]) for k in ("maps", "astar", "stubs", "legs", "stamp")))
    return 0 if laid == n_pairs else 1

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
