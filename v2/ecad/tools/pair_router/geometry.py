# Extracted from pair_preroute.py on 15 September 2026 (red team round four C3: the split at measurable boundaries),
# behaviour-preserving: every name here is re-exported into pair_preroute's namespace by a star import, and the
# module-level lists and dicts (budgets, timers, caches, epochs) stay the SAME objects, so a function that mutates
# them from any module mutates the one the pass reads. Proved on the box by the pre-router laying the same pairs to
# the same board md5 on D and B before and after (tools/knob_measure).
"""geometry"""
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


def _via_dia(t):
    """A via's diameter in mm. KiCad 9 asserts on PCB_VIA::GetWidth() with no layer (it can differ per layer on a
    blind via); every via this tool lays is a through via, so the front copper answers for all of them."""
    try: return mm(t.GetWidth(pcbnew.F_Cu))
    except Exception: return mm(t.GetWidth())   # SWIG raises TypeError on some builds and NotImplementedError on others


def _pt_seg(px, py, x1, y1, x2, y2):
    """Distance from a point to a segment, in millimetres."""
    dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy
    t = 0.0 if L2 <= 1e-12 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def _segs_cross(a, c, d, e, f, g_, h, i_):
    """Do the two segments properly intersect? (The orientation test, as the leg-crossing gate uses it.)"""
    def _o(px, py, qx, qy, rx, ry): return (qx - px) * (ry - py) - (qy - py) * (rx - px)
    o1, o2, o3, o4 = _o(a, c, d, e, f, g_), _o(a, c, d, e, h, i_), _o(f, g_, h, i_, a, c), _o(f, g_, h, i_, d, e)
    return (o1 > 1e-9) != (o2 > 1e-9) and (o3 > 1e-9) != (o4 > 1e-9) and abs(o1) + abs(o2) + abs(o3) + abs(o4) > 1e-9


def _seg_dist(a, c, d, e, f, g_, h, i_):
    """Distance between two segments, zero when they cross."""
    return 0.0 if _segs_cross(a, c, d, e, f, g_, h, i_) else _seg_gap(a, c, d, e, f, g_, h, i_)


def _seg_gap(a, c, d, e, f, g_, h, i_):
    """Distance between two segments that do not cross, in millimetres (the four endpoint-to-segment distances)."""
    return min(_pt_seg(a, c, f, g_, h, i_), _pt_seg(d, e, f, g_, h, i_), _pt_seg(f, g_, a, c, d, e), _pt_seg(h, i_, a, c, d, e))


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
Grid.seg = _timed("stamp", Grid.seg)
Grid.disc = _timed("stamp", Grid.disc)



__all__ = [_n for _n in dir() if not _n.startswith("__")]
