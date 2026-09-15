# Extracted from pair_preroute.py on 15 September 2026 (red team round four C3: the split at measurable boundaries),
# behaviour-preserving: every name here is re-exported into pair_preroute's namespace by a star import, and the
# module-level lists and dicts (budgets, timers, caches, epochs) stay the SAME objects, so a function that mutates
# them from any module mutates the one the pass reads. Proved on the box by the pre-router laying the same pairs to
# the same board md5 on D and B before and after (tools/knob_measure).
"""occupancy"""
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
        if p.IsOnLayer(L): gr.poly(trk[L], p.GetEffectivePolygon(L), _obs_clr(p.GetNetname()) + half, key=(pk, L))
        if pth and p.IsOnLayer(L): c = p.GetPosition(); d = p.GetDrillSize(); gr.disc(trk[L], mm(c.x), mm(c.y), mm(max(d.x, d.y)) / 2 + HOLE_CLR + half)
    anyL = next((L for L in _ALL.values() if p.IsOnLayer(L)), None)   # any copper layer: a via is a hole through every layer
    if anyL is not None or pth: gr.poly(via_clr, p.GetEffectivePolygon(anyL if anyL is not None else pcbnew.F_Cu), _obs_clr(p.GetNetname()) + via_r + split, key=(pk, "via", anyL))


def _track_stamp(gr, layers, t, trk, via_clr, half, via_r, split):
    """One track or via's clearance into the count rasters."""
    _c = _obs_clr(t.GetNetname())
    if t.GetClass() == "PCB_VIA":
        c = t.GetPosition(); r = mm(t.GetWidth(pcbnew.F_Cu)) / 2
        for L in layers: gr.disc(trk[L], mm(c.x), mm(c.y), r + _c + half)
    else:
        a, e = t.GetStart(), t.GetEnd(); r = mm(t.GetWidth()) / 2; L = t.GetLayer()
        if L in trk: gr.seg(trk[L], mm(a.x), mm(a.y), mm(e.x), mm(e.y), r + _c + half)
        gr.seg(via_clr, mm(a.x), mm(a.y), mm(e.x), mm(e.y), r + _c + via_r + split)


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


def _stamp_own(gr, layers, nets, idx, trk, via_clr, half, via_r, split, pads_only=False):
    """Just this pair's own copper, from the index: a handful of pads and the legs laid so far.

    `pads_only` stamps the PADS and not the tracks, which is the exemption a fan needs at its own station:
    the pair's own pads legitimately block the map where the fan is going, its partner's tracks do not
    (12 September 2026, appendix 32.135; A's /USB_D8 fan crossed /USB_WALL because a pad-shaped exemption
    forgave every net's copper within 1.2 mm of a pad)."""
    for nm in nets:
        pads, tracks = idx.get(nm, ([], []))
        for ref, p in pads: _pad_stamp(gr, layers, ref, p, trk, via_clr, half, via_r, split)
        if pads_only: continue
        for t in tracks: _track_stamp(gr, layers, t, trk, via_clr, half, via_r, split)


def _all_counts(gr, b, layers, half, via_r, split):
    """The whole board counted once, with an index from net name to the items on it.

    This is the change of 11 September 2026 (round-two C3). Four of the five `build_maps` calls a pair makes exclude
    that pair's own nets, so the cache key was unique per pair and every one rebuilt the board in full: 1,010 s of a
    1,327 s B19 pass, 76 percent, against 115 s in the corridor search the pass exists to run."""
    ck = ((gr.G, gr.X0, gr.Y0, gr.NX, gr.NY), tuple(layers), round(half, 5), round(via_r, 5), round(split, 5), round(_CLR_NOW[0], 5))
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



def _via_site_blocked(b, pos, vd, clr, own, fp_own):
    """A through via spans every copper layer, so its site is judged against the copper of EVERY layer, not the one the pad
    is on. B19 is assembled on both sides and the via the pre-router drops into a station's middle pin (an ESD's ground
    pin between the pair's two pads) landed 0.01 to 0.12 mm from R147, R256 and R150 on the underside, eight of the
    pre-route DRC's 64 hard items (15 Sep 2026). Returns what blocks the site or None. The pads of the pin's own part are
    not asked: that is the geometry the station was drawn with and every board's pre-route DRC has judged it clean."""
    x, y = pos.x, pos.y; need = (vd / 2 + clr) * 1e6
    def seg_d(t):
        ax, ay, bx, by = t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y
        L2 = (bx - ax) ** 2 + (by - ay) ** 2
        u = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / L2))
        return math.hypot(x - (ax + u * (bx - ax)), y - (ay + u * (by - ay)))
    for fp in b.GetFootprints():
        if fp is fp_own or fp.GetReference() == fp_own.GetReference(): continue
        for p in fp.Pads():
            if p.GetNetname() == own: continue
            bb = p.GetBoundingBox(); c = bb.GetCenter()
            dx = max(0.0, abs(x - c.x) - bb.GetWidth() / 2.0); dy = max(0.0, abs(y - c.y) - bb.GetHeight() / 2.0)
            if math.hypot(dx, dy) < need: return "%s pad %s [%s] on %s" % (fp.GetReference(), p.GetNumber(), p.GetNetname(), "B.Cu" if fp.IsFlipped() else "F.Cu")
    for t in b.GetTracks():
        if t.GetNetname() == own: continue
        if t.GetClass() == "PCB_VIA":
            if math.hypot(t.GetPosition().x - x, t.GetPosition().y - y) < need + t.GetWidth() / 2.0: return "via [%s]" % t.GetNetname()
        elif seg_d(t) < need + t.GetWidth() / 2.0: return "track [%s] on %s" % (t.GetNetname(), t.GetLayerName())
    return None

def build_maps(gr, b, layers, nets, half, via_r, split=VIA_SPLIT, pads_only=False):
    """Forbidden centreline cells per layer (other-net copper grown by half + CLR) and forbidden via-centre cells (any layer).

    `pads_only=True` exempts only the named nets' PADS, never their tracks."""
    MAP_CALLS[0] += 1
    return _build_maps(gr, b, layers, nets, half, via_r, split, pads_only)


def _build_maps(gr, b, layers, nets, half, via_r, split=VIA_SPLIT, pads_only=False):
    if MAP_MODE == "reference" and not MAP_CHECK:
        # the reference path has no pads-only form: the conservative map (nothing exempt) is the safe answer there
        return _build_maps_reference(gr, b, layers, set() if pads_only else nets, half, via_r, split)
    rec = _all_counts(gr, b, layers, half, via_r, split)
    all_trk, all_via, holes, _seen, _ep, (own_trk, own_via), idx = rec
    for L in layers: own_trk[L].fill(0)
    own_via.fill(0)
    _stamp_own(gr, layers, set(nets), idx, own_trk, own_via, half, via_r, split, pads_only)
    # "some net other than this pair's blocks the cell" is a comparison of counts, never a bitwise subtraction: where
    # two nets' grown rasters overlap, clearing the pair's own bits would free a cell the other net blocks.
    trk = {L: all_trk[L] > own_trk[L] for L in layers}
    via = (all_via > own_via) | holes
    _edge_band(gr, trk, via)
    if MAP_CHECK and not pads_only:
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
    ck = ((gr.G, gr.X0, gr.Y0, gr.NX, gr.NY), tuple(layers), frozenset(nets), round(half, 5), round(via_r, 5), round(split, 5), round(_CLR_NOW[0], 5))
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
                if p.IsOnLayer(L): gr.poly(trk[L], p.GetEffectivePolygon(L), _obs_clr(p.GetNetname()) + half, key=(pk, L))
                if pth and p.IsOnLayer(L): c = p.GetPosition(); d = p.GetDrillSize(); gr.disc(trk[L], mm(c.x), mm(c.y), mm(max(d.x, d.y)) / 2 + HOLE_CLR + half)
            anyL = next((L for L in _ALL.values() if p.IsOnLayer(L)), None)   # any copper layer: a via is a hole through every layer
            if anyL is not None or pth: gr.poly(via, p.GetEffectivePolygon(anyL if anyL is not None else pcbnew.F_Cu), _obs_clr(p.GetNetname()) + via_r + split, key=(pk, "via", anyL))
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


__all__ = [_n for _n in dir() if not _n.startswith("__")]
