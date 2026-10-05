#!/usr/bin/env python3
"""Record l8r2, the P0 round's correction set after the focused check cx45 (question Q2; MESHSAT-1357, 5 October 2026, Slot A):
THE DEDICATED RETURN PLACED ON THE DRAWN BOARDS AND SOLVED AS A DISTRIBUTED NETWORK. PROTOTYPE DESIGN, DESK ARITHMETIC: nothing is
built, bought, powered or measured; no figure here is a measurement.

cx45 found that l8r2_p0.out's realisable-placement claim (one return socket a group) rested on group centres, not on placed lands,
courtyards or an electrical model that matches a distributed arrangement; its solver puts six return conductors in parallel behind one
common series resistance. This record:
  1. reads the placed boards A (pcb-a-power-a23) and B (pcb-b-compute-b19): every footprint's courtyard, every pad and its net, the
     board outline (Edge.Cuts), parsed from the s-expression;
  2. PLACES the parts the composed design adds and the return needs: J_5V_IOC beside J_5V_DEV and the three return sockets J_GR1 to
     J_GR3 (Amass XT60-F, its courtyard read from board E's placed XT60 J_BATT), one beside each group of 5 V entries on board B and
     its counterpart beside the same group's stage outputs on board A, each at the least distance to its group that leaves its
     courtyard 0.25 mm clear of every placed courtyard (either side: through-hole parts) and inside the outline by 0.5 mm (SESSION
     decision L8R2-D10, the placement draft, RETURN-PLACEMENT in the output);
  3. builds each board's ground as a resistive grid (1.5 mm cells inside the outline; the declared ground planes of record l9stk in
     parallel, A two and B three at 0.5 oz; copper thin by 15 % at one corner; a plane fill of 100 % and of 50 % to bound the
     antipads and splits no board here draws yet: ASSUMPTION), joins the boards by every ground conductor of the composed netlists
     (the six VH leads' pin 2, the seventeen ribbon ground conductors pin for pin, the six XT60 return contacts), each with its wire
     and two contacts in the record's box (VH and ribbon 0 to 20 mOhm, XT60 0 to 1 mOhm), and drives it with each lead's return
     current INJECTED AT ITS RAIL'S LOADS on board B (their ground pads on the placed board, weighted by the intent's loads; a load not
     placed yet takes its rail's entry) and TAKEN OUT AT THE LEAD'S LAND on board A (the stage beside its connector: a Layer 10
     placement condition);
  4. solves it for the case rows (C-DEV rev 2, the active row; C-DEV rev 1; the largest steady state; the declared upper bound) at
     -20 C and 76.25 C, both copper corners and both fills, over the contact vertex family (every conductor in turn with its own
     contacts low and every other contact high, and the two uniform vertices), and judges every conductor against its printed rating
     and the least rating its sheet allows at the inside air;
  5. adds the correction where a row fails (a fourth return lead or a return bar, placed the same way), and states what holds.
Run from the repository root: python3 v2/docs/records/l8r2/l8r2_dist.py (stdlib, numpy, scipy, PyYAML, pdftotext; about two minutes).
The committed output is regenerated only through _bin/regen_out.py.
"""
import hashlib
import importlib.util
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
REC = os.path.join(ROOT, "v2", "docs", "records")
sys.dont_write_bytecode = True
try:
    import numpy as np
    import scipy.sparse as sp
    import scipy.sparse.linalg as spla
except ImportError:                                   # pragma: no cover
    sys.stderr.write("l8r2_dist: numpy and scipy are needed; refusing\n")
    sys.exit(3)

PCB = {"a": "v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb", "b": "v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_pcb"}
PCB_E = "v2/ecad/pcb-e1-dock-e7/pcb-e1-dock.kicad_pcb"        # board E's placed XT60 (J_BATT): the XT60 body's courtyard
PINS = ["v2/docs/records/l8r2/l8r2_gndret.py", "v2/docs/records/l8r2/l8r2_gndret.out", "v2/docs/records/l8r2/l8r2_p0.py",
        "v2/docs/records/l8r2/l8r2_p0.out", "v2/docs/records/l8r2/apply_gen_sch_a_gndrtn.py", "v2/docs/records/l8r2/apply_gen_sch_b_gndrtn.py",
        "v2/docs/records/l9t5/l9t5_connected.py", "v2/docs/records/l9pwr/l9pwr_budget.out", PCB["a"], PCB["b"], PCB_E]
GROUPS = (("J_GR1", ("J_5V_S1",)), ("J_GR2", ("J_5V_S2", "J_5V_S3")), ("J_GR3", ("J_5V_DEV", "J_5V_IOC")))   # one socket a group (L8R2-D9)
LEADS = ("J_5V_S1", "J_5V_S2", "J_5V_S3", "J_5V_DEV", "J_5V_IOC", "J_54V")
RAIL_OF = {"J_5V_S1": "+5V_S1", "J_5V_S2": "+5V_S2", "J_5V_S3": "+5V_S3", "J_5V_DEV": "+5V_DEV", "J_5V_IOC": "+5V_IOC", "J_54V": "+54V_POE"}
RIBBONS = ("J_AB1", "J_AB2")
CELL = 1.5e-3                  # m: the grid's cell (MODEL)
CLEAR, EDGE = 0.25, 0.5        # mm: courtyard clearance and outline margin of a placed part (SESSION, the placement draft's rule)
SEARCH = 60.0                  # mm: the search radius around a group
FILLS = (1.0, 0.5)             # the planes' fill (ASSUMPTION: no split or antipad is drawn yet; 50 % bounds them)
RHO20, CU_ALPHA = 1.72e-8, 0.00393
GND = ("GND", "/GND")


def rel(p):
    return os.path.join(ROOT, p)


def sha(p, n=16):
    return hashlib.sha256(open(rel(p), "rb").read()).hexdigest()[:n]


def refuse(msg):
    sys.stderr.write("l8r2_dist: %s; refusing\n" % msg)
    sys.exit(3)


def load(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


G = load(os.path.join(HERE, "l8r2_gndret.py"), "l8r2_gndret_for_dist")
P0 = load(os.path.join(HERE, "l8r2_p0.py"), "l8r2_p0_for_dist")


# ------------------------------------------------------------------------------------------------ the placed boards, parsed
_TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+')


def _tree(text_):
    stack = [[]]
    for tok in _TOK.findall(text_):
        if tok == "(":
            stack.append([])
        elif tok == ")":
            n = stack.pop()
            stack[-1].append(n)
        else:
            stack[-1].append(tok[1:-1] if tok.startswith('"') else tok)
    return stack[0]


def _blocks(t, head):
    """every top-level '(head ...' block's text, by its parentheses"""
    out = []
    for m in re.finditer(r"\(%s[ \n]" % head, t):
        i = j = m.start()
        depth = 0
        while True:
            c = t[j]
            if c == '"':
                j += 1
                while t[j] != '"':
                    j += 2 if t[j] == "\\" else 1
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(t[i:j + 1])
    return out


def _kv(node, key):
    for x in node:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def _xf(at, px, py):
    a = math.radians(-at[2])
    return at[0] + px * math.cos(a) - py * math.sin(a), at[1] + px * math.sin(a) + py * math.cos(a)


def footprints(path):
    """{ref: dict(at, layer, pads [(num, x, y, net)], crt (x0, y0, x1, y1) or None, crt_local, name)}"""
    t = open(rel(path), encoding="utf-8").read()
    out = {}
    for b in _blocks(t, "footprint"):
        fp = _tree(b)[0]
        ref = None
        for x in fp:
            if isinstance(x, list) and x[:2] == ["property", "Reference"]:
                ref = x[2]
        if ref is None:
            continue
        at = _kv(fp, "at")
        at = (float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0)
        pads, pts, loc = [], [], []
        for x in fp:
            if not isinstance(x, list) or not x:
                continue
            if x[0] == "pad":
                pa = _kv(x, "at")
                net = _kv(x, "net")
                bx, by = _xf(at, float(pa[1]), float(pa[2]))
                pads.append((x[1], bx, by, net[-1] if net else ""))
            elif x[0] in ("fp_line", "fp_rect", "fp_poly", "fp_circle"):
                lay = _kv(x, "layer")
                if not lay or not str(lay[1]).endswith("CrtYd"):
                    continue
                if x[0] == "fp_poly":
                    xy = [(float(p[1]), float(p[2])) for p in _kv(x, "pts")[1:] if isinstance(p, list) and p[0] == "xy"]
                elif x[0] == "fp_circle":
                    c, e = _kv(x, "center"), _kv(x, "end")
                    r_ = math.hypot(float(e[1]) - float(c[1]), float(e[2]) - float(c[2]))
                    xy = [(float(c[1]) + r_, float(c[2]) + r_), (float(c[1]) - r_, float(c[2]) - r_)]
                else:
                    s_, e = _kv(x, "start"), _kv(x, "end")
                    xy = [(float(s_[1]), float(s_[2])), (float(e[1]), float(e[2]))]
                loc += xy
                pts += [_xf(at, px, py) for px, py in xy]
        crt = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)) if pts else None
        crt_local = (min(p[0] for p in loc), min(p[1] for p in loc), max(p[0] for p in loc), max(p[1] for p in loc)) if loc else None
        layer = _kv(fp, "layer")
        out[ref] = dict(at=at, layer=layer[1] if layer else "?", pads=pads, crt=crt, crt_local=crt_local, name=fp[1])
    return out


def outline(path):
    """the board outline's segments (mm) from Edge.Cuts: gr_line, gr_rect and gr_arc (an arc as eight chords)"""
    t = open(rel(path), encoding="utf-8").read()
    segs = []
    for head in ("gr_line", "gr_rect", "gr_arc"):
        for b in _blocks(t, head):
            n = _tree(b)[0]
            lay = _kv(n, "layer")
            if not lay or lay[1] != "Edge.Cuts":
                continue
            s_, e = _kv(n, "start"), _kv(n, "end")
            p0, p1 = (float(s_[1]), float(s_[2])), (float(e[1]), float(e[2]))
            if head == "gr_line":
                segs.append((p0, p1))
            elif head == "gr_rect":
                c = [p0, (p1[0], p0[1]), p1, (p0[0], p1[1])]
                segs += [(c[k], c[(k + 1) % 4]) for k in range(4)]
            else:
                mid = _kv(n, "mid")
                pm = (float(mid[1]), float(mid[2]))
                ax, ay = p0
                bx, by = pm
                cx, cy = p1
                d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
                ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
                uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
                r_ = math.hypot(ax - ux, ay - uy)
                a0, am, a1 = (math.atan2(p[1] - uy, p[0] - ux) for p in (p0, pm, p1))
                # the sweep from a0 to a1 through am
                def norm(a):
                    return (a - a0) % (2 * math.pi)
                sweep = norm(a1)
                if norm(am) > sweep:
                    sweep -= 2 * math.pi
                pts = [(ux + r_ * math.cos(a0 + sweep * k / 8), uy + r_ * math.sin(a0 + sweep * k / 8)) for k in range(9)]
                segs += list(zip(pts[:-1], pts[1:]))
    if not segs:
        refuse("%s has no Edge.Cuts outline" % path)
    return segs


def inside(segs, xs, ys):
    """even-odd point-in-outline for arrays of points (every Edge.Cuts loop counts: a cut-out is outside)"""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    res = np.zeros(xs.shape, bool)
    for (x0, y0), (x1, y1) in segs:
        if y0 == y1:
            continue
        cond = (ys >= min(y0, y1)) & (ys < max(y0, y1))
        xint = x0 + (ys - y0) * (x1 - x0) / (y1 - y0)
        res ^= cond & (xs < xint)
    return res


def seg_dist(segs, x, y):
    best = 1e9
    for (x0, y0), (x1, y1) in segs:
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        u = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / L2))
        best = min(best, math.hypot(x - x0 - u * dx, y - y0 - u * dy))
    return best


# ------------------------------------------------------------------------------------------------ the placement draft
def rot_box(local, rot):
    """a local bbox rotated by a multiple of 90 degrees, as an offset bbox"""
    x0, y0, x1, y1 = local
    pts = [_xf((0.0, 0.0, rot), px, py) for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))


def place(name, local_crt, pins_local, targets, fps, segs, taken=()):
    """the least-distance site for a part: its courtyard CLEAR from every placed courtyard (and from the parts this draft placed
    before it), inside the outline by EDGE; distance = the largest from its ground pins' centroid to the target lands"""
    boxes = np.array([f["crt"] for f in fps.values() if f["crt"]] + [b for b in taken], float)
    tx = np.mean([t[0] for t in targets])
    ty = np.mean([t[1] for t in targets])
    near = boxes[(boxes[:, 2] > tx - SEARCH - 25) & (boxes[:, 0] < tx + SEARCH + 25) & (boxes[:, 3] > ty - SEARCH - 25) & (boxes[:, 1] < ty + SEARCH + 25)]
    best = None
    steps = np.arange(-SEARCH, SEARCH + 1e-9, 1.0)
    for rot in (0.0, 90.0, 180.0, 270.0):
        ob = rot_box(local_crt, rot)
        pc = np.mean([_xf((0.0, 0.0, rot), px, py) for px, py in pins_local], axis=0)
        for dx in steps:
            cx = tx + dx
            for dy in steps:
                cy = ty + dy
                bx0, by0, bx1, by1 = cx + ob[0], cy + ob[1], cx + ob[2], cy + ob[3]
                d = max(math.hypot(cx + pc[0] - t[0], cy + pc[1] - t[1]) for t in targets)
                if best is not None and d >= best[0]:
                    continue
                if near.size and np.any((near[:, 0] < bx1 + CLEAR) & (near[:, 2] > bx0 - CLEAR) & (near[:, 1] < by1 + CLEAR) & (near[:, 3] > by0 - CLEAR)):
                    continue
                cs = [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]
                if not all(inside(segs, [p[0]], [p[1]])[0] for p in cs):
                    continue
                if min(seg_dist(segs, p[0], p[1]) for p in cs + [((bx0 + bx1) / 2, by0), ((bx0 + bx1) / 2, by1), (bx0, (by0 + by1) / 2), (bx1, (by0 + by1) / 2)]) < EDGE:
                    continue
                best = (d, cx, cy, rot, (bx0, by0, bx1, by1))
    if best is None:
        refuse("no site for %s within %.0f mm of its group" % (name, SEARCH))
    d, cx, cy, rot, box = best
    gap = min((max(near[k, 0] - box[2], box[0] - near[k, 2], near[k, 1] - box[3], box[1] - near[k, 3]) for k in range(len(near))), default=99.0)
    pins = [_xf((cx, cy, rot), px, py) for px, py in pins_local]
    return dict(name=name, at=(cx, cy, rot), box=box, dist=d, gap=gap, pins=pins)


# ------------------------------------------------------------------------------------------------ the distributed network
class Board:
    def __init__(self, segs, h_mm):
        xs = [p[0] for s in segs for p in s]
        ys = [p[1] for s in segs for p in s]
        self.x0, self.y0 = min(xs), min(ys)
        self.nx = int(math.ceil((max(xs) - self.x0) / h_mm)) + 1
        self.ny = int(math.ceil((max(ys) - self.y0) / h_mm)) + 1
        self.h = h_mm
        gx, gy = np.meshgrid(self.x0 + (np.arange(self.nx) + 0.5) * h_mm, self.y0 + (np.arange(self.ny) + 0.5) * h_mm)
        self.mask = inside(segs, gx.ravel(), gy.ravel()).reshape(self.ny, self.nx)
        self.idx = -np.ones((self.ny, self.nx), int)
        self.idx[self.mask] = np.arange(int(self.mask.sum()))
        self.n = int(self.mask.sum())
        self.gx, self.gy = gx, gy

    def node(self, x, y):
        """the nearest node inside the outline to a point (mm), and its distance"""
        i = int(round((y - self.y0) / self.h - 0.5))
        j = int(round((x - self.x0) / self.h - 0.5))
        best = None
        for di in range(-3, 4):
            for dj in range(-3, 4):
                ii, jj = i + di, j + dj
                if 0 <= ii < self.ny and 0 <= jj < self.nx and self.idx[ii, jj] >= 0:
                    d = math.hypot(self.gx[ii, jj] - x, self.gy[ii, jj] - y)
                    if best is None or d < best[0]:
                        best = (d, self.idx[ii, jj])
        if best is None:
            refuse("no grid node near (%.2f, %.2f)" % (x, y))
        return best[1]

    def edges(self):
        e = []
        for a, b in ((self.idx[:, :-1], self.idx[:, 1:]), (self.idx[:-1, :], self.idx[1:, :])):
            m = (a >= 0) & (b >= 0)
            e.append(np.stack([a[m], b[m]], axis=1))
        return np.concatenate(e)


def sheet_g(planes, T, thin, fill):
    """the planes' sheet conductance (S a square): planes in parallel, 0.5 oz, thin by THK_TOL at one corner, the fill fraction"""
    t = P0.OZ[0.5] * ((1 - P0.THK_TOL) if thin else 1.0)
    return fill * planes * t / (RHO20 * (1 + CU_ALPHA * (T - 20.0)))


def solve_family(BA, BB, gA, gB, branches, rhs_list, probe, ref_node=0):
    """K x = i with every contact high (one factorization), then any contact vertex exactly by the Woodbury identity in branch space:
    for a set S of conductors with their contacts low, the branch voltages are v_S = v - WZ[:, S] M^-1 v[S], M = diag(1/dg_S) + WZ[S, S],
    WZ = W^T K^-1 W. For each conductor c a LOCAL SEARCH over the vertices: start with c's own contacts low and every other high, set
    low every contact whose conductance raises c's current at the present vertex (the sign of dI_c/dg_j = -g_c WZ_S[c, j] v_S[j]),
    and repeat until the set is stable (a vertex where no single contact's move raises I_c). The probe (a weighted mean voltage on
    board B less a node on board A) is searched the same way. Returns per case: dict(own [I_c at c's searched vertex], flips [the
    contacts set low beyond c's own], hi [I at all high], lo [I at all low], shift_max)."""
    eA, eB = BA.edges(), BB.edges() + BA.n
    N = BA.n + BB.n
    rows, cols, vals = [], [], []
    for e, g in ((eA, gA), (eB, gB)):
        rows += [e[:, 0], e[:, 1], e[:, 0], e[:, 1]]
        cols += [e[:, 1], e[:, 0], e[:, 0], e[:, 1]]
        vals += [np.full(len(e), -g), np.full(len(e), -g), np.full(len(e), g), np.full(len(e), g)]
    p = np.array([b["p"] for b in branches]); q = np.array([b["q"] for b in branches])
    keep = np.ones(N, bool); keep[ref_node] = False
    g_hi = np.array([1.0 / b["r_hi"] for b in branches]); g_lo = np.array([1.0 / b["r_lo"] for b in branches])
    dg = g_lo - g_hi
    gg = g_hi
    r = rows + [p, q, p, q]; c = cols + [q, p, p, q]; v = vals + [-gg, -gg, gg, gg]
    K = sp.csc_matrix((np.concatenate(v), (np.concatenate(r), np.concatenate(c))), shape=(N, N))
    lu = spla.splu(K[keep][:, keep].tocsc())

    def solve(vec):
        x = np.zeros(N); x[keep] = lu.solve(vec[keep]); return x
    nb = len(branches)
    Z = np.zeros((N, nb))
    for k in range(nb):
        w = np.zeros(N); w[p[k]] = 1.0; w[q[k]] = -1.0
        Z[:, k] = solve(w)
    WZ = Z[p, :] - Z[q, :]
    pw, pa = probe
    lz = np.array([sum(wt * Z[nd, k] for nd, wt in pw) - Z[pa, k] for k in range(nb)])

    def at(S, vx, lx):
        """branch voltages, conductances and the probe at the vertex with the set S low"""
        S = sorted(S)
        g = g_hi.copy(); g[S] = g_lo[S]
        if not S:
            return vx, g, lx, WZ, lz
        M = np.diag(1.0 / dg[S]) + WZ[np.ix_(S, S)]
        Mi = np.linalg.inv(M)
        vxs = vx - WZ[:, S] @ (Mi @ vx[S])
        lxs = lx - lz[S] @ (Mi @ vx[S])
        WZs = WZ - WZ[:, S] @ Mi @ WZ[S, :]
        lzs = lz - lz[S] @ Mi @ WZ[S, :]
        return vxs, g, lxs, WZs, lzs
    res = []
    for i in rhs_list:
        x = solve(i)
        vx = x[p] - x[q]
        lx = sum(wt * x[nd] for nd, wt in pw) - x[pa]
        out = dict(own=[0.0] * nb, flips=[0] * nb, stable=True)
        vh, gh, _l, _w, _z = at(set(), vx, lx)
        vl, gl, _l2, _w2, _z2 = at(set(range(nb)), vx, lx)
        out["hi"], out["lo"] = list(vh * gh), list(vl * gl)
        for k in range(nb):
            S = {k}
            for _it in range(12):
                vxs, g, _lx, WZs, _lz = at(S, vx, lx)
                d = -g[k] * WZs[k, :] * vxs * np.sign(vxs[k] if vxs[k] != 0 else 1.0)
                newS = {k} | {j for j in range(nb) if j != k and d[j] > 0}
                if newS == S:
                    break
                S = newS
            else:
                out["stable"] = False
            vxs, g, _lx, _w3, _z3 = at(S, vx, lx)
            out["own"][k] = abs(vxs[k] * g[k])
            out["flips"][k] = len(S) - 1
        S = set()
        for _it in range(12):
            vxs, _g, lxs, _WZs, lzs = at(S, vx, lx)
            d = -lzs * vxs
            newS = {j for j in range(nb) if d[j] > 0}
            if newS == S:
                break
            S = newS
        else:
            out["stable"] = False
        out["shift_max"] = float(at(S, vx, lx)[2])
        res.append(out)
    return res


# ------------------------------------------------------------------------------------------------ the case rows' currents per lead
def case_currents(F, intent_b):
    bud = G.budget(rel("v2/docs/records/l9pwr/l9pwr_budget.out"))
    st = bud["PS-ALLTX"]
    big = max(bud, key=lambda s: sum(v["least"] for v in bud[s].values()))
    cs = " ".join(open(rel("v2/docs/records/l8r2/inputs/coordinator-cases-2026-10-05-cdev-rev2.md"), encoding="utf-8").read().split())
    ioc2 = float(re.search(r"\+5V_IOC ([\d.]+) A\*\* in place of ([\d.]+) A", cs).group(1))
    ioc1 = 1.3800
    u601_2 = ioc2 * F["cdev_u601"] / ioc1
    rails = {k.lstrip("/"): v for k, v in intent_b["rails"].items()}
    cases = []
    base = dict(J_5V_S1=st["S1"]["least"], J_5V_S2=st["S2"]["least"], J_5V_S3=st["S3"]["least"], J_5V_DEV=F["cdev_u7"], J_54V=0.0)
    cases.append(("C-DEV rev 2 (the active row; conditional on FW-B20/B21)", dict(base, J_5V_IOC=u601_2)))
    cases.append(("C-DEV rev 1 (the labelled scenario)", dict(base, J_5V_IOC=F["cdev_u601"])))
    b_ = bud[big]
    cases.append(("the largest steady state (%s, HIGH, the least load voltage)" % big,
                  dict(J_5V_S1=b_["S1"]["least"], J_5V_S2=b_["S2"]["least"], J_5V_S3=b_["S3"]["least"],
                       J_5V_DEV=b_["DEV"]["least"] - F["cdev_u601_at_u7"], J_5V_IOC=F["cdev_u601"], J_54V=0.0)))
    cases.append(("the declared upper bound (every lead at its declared peak, the composed intent)",
                  {ld: float(rails[RAIL_OF[ld]]["amps_peak"]) for ld in LEADS}))
    return cases, rails


def main():
    for p in PINS:
        if not os.path.isfile(rel(p)):
            refuse("%s is missing" % p)
    F = G.figures()
    C = load(os.path.join(REC, "l9t5", "l9t5_connected.py"), "l9t5_connected_for_dist")
    import tempfile
    import shutil
    tmp = tempfile.mkdtemp(prefix="l8r2_dist_")
    try:
        T = {}
        for b in "ab":
            gen, steps = C.compose(b, tmp, C.ORDER[b], "dist")
            if any(s[1] for s in steps):
                refuse("board %s does not compose: %s" % (b, [s for s in steps if s[1]]))
            raw, rc, tail, table = C.regen(b, gen, tmp, "dist")
            if raw is None:
                refuse("board %s does not regenerate: %s" % (b, tail))
            T[b] = table
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    net_parts = {b: {p["ref"]: p for p in T[b]["parts"]} for b in "ab"}
    cases, rails = case_currents(F, T["b"]["intent"])
    FP = {b: footprints(PCB[b]) for b in "ab"}
    SEG = {b: outline(PCB[b]) for b in "ab"}
    fpE = footprints(PCB_E)
    xt = fpE["J_BATT"]
    xt_local, xt_pins = xt["crt_local"], [(0.0, 0.0), (7.2, 0.0)]
    vh = FP["b"]["J_5V_DEV"]
    vh_local, vh_pins = vh["crt_local"], [(0.0, 0.0), (3.96, 0.0)]
    out = []
    w = out.append
    w("l8r2_dist: record l8r2, the P0 round's correction set after cx45 (Q2; Slot A, MESHSAT-1357, 5 October 2026): THE DEDICATED RETURN")
    w("PLACED ON THE DRAWN BOARDS AND SOLVED AS A DISTRIBUTED NETWORK. PROTOTYPE DESIGN, DESK ARITHMETIC: nothing built, bought, powered or")
    w("measured. Labels: PRINTED, TYPICAL, DECLARED, MODEL, ASSUMPTION, INFERRED, MISSING, PROVISIONAL.")
    w("")
    w("0. PINS (sha256/16 path)")
    for p in PINS:
        w("   %s %s" % (sha(p), p))
    w("")
    w("1. THE PLACED BOARDS AS READ (footprint blocks and Edge.Cuts parsed; no KiCad)")
    for b in "ab":
        n_crt = sum(1 for f in FP[b].values() if f["crt"])
        w("   board %s: %d footprints, %d with a courtyard; the outline %d segments" % (b.upper(), len(FP[b]), n_crt, len(SEG[b])))
    w("   the XT60's courtyard: board E's placed J_BATT (%s), %.2f x %.2f mm; the VH 1x2's: board B's J_5V_DEV, %.2f x %.2f mm" % (
        xt["name"], xt_local[2] - xt_local[0], xt_local[3] - xt_local[1], vh_local[2] - vh_local[0], vh_local[3] - vh_local[1]))
    w("")

    # 2. the placement draft
    w("2. THE PLACEMENT DRAFT (SESSION decision L8R2-D10: the sites below are reserved for the return; Layer 10 places from them; each")
    w("   courtyard %.2f mm clear of every placed courtyard on either side and %.1f mm inside the outline; the least largest distance from" % (CLEAR, EDGE))
    w("   the part's ground pins' centre to its group's ground lands)")
    PL = {"a": {}, "b": {}}
    for b in ("b", "a"):
        taken = []
        dev = [p for p in FP[b]["J_5V_DEV"]["pads"] if p[0] == "2"][0]
        pl = place("J_5V_IOC", vh_local, vh_pins, [(dev[1], dev[2])], FP[b], SEG[b])
        PL[b]["J_5V_IOC"] = pl
        taken.append(pl["box"])
        for gr, members in GROUPS:
            tg = []
            for m in members:
                if m == "J_5V_IOC":
                    tg.append(PL[b]["J_5V_IOC"]["pins"][1])
                else:
                    tg += [(p[1], p[2]) for p in FP[b][m]["pads"] if p[0] == "2"]
            pl = place(gr, xt_local, xt_pins, tg, FP[b], SEG[b], taken)
            PL[b][gr] = pl
            taken.append(pl["box"])
        for k, pl in PL[b].items():
            w("   board %s %-8s at (%.2f, %.2f) rotated %3.0f: courtyard (%.2f, %.2f)-(%.2f, %.2f), %.2f mm from the nearest placed courtyard; ground" % (
                b.upper(), k, pl["at"][0], pl["at"][1], pl["at"][2], pl["box"][0], pl["box"][1], pl["box"][2], pl["box"][3], pl["gap"]))
            w("     pins %s, at most %.1f mm from its group's ground lands" % (", ".join("(%.2f, %.2f)" % p for p in pl["pins"]), pl["dist"]))
    w("")

    # 3. the network
    BA, BB = Board(SEG["a"], CELL * 1e3), Board(SEG["b"], CELL * 1e3)
    w("3. THE NETWORK (MODEL): board A %d nodes, board B %d nodes at %.1f mm; planes A %d, B %d at 0.5 oz (record l9stk), %.0f %% thin at one" % (
        BA.n, BB.n, CELL * 1e3, P0.PLANES["a"], P0.PLANES["b"], 100 * P0.THK_TOL))
    w("   corner, fill %s (ASSUMPTION); the conductors of the composed netlists between the boards:" % " and ".join("%.0f %%" % (100 * f) for f in FILLS))

    def pad(b, ref, num):
        if ref in PL[b]:
            return PL[b][ref]["pins"][int(num) - 1]
        p = [x for x in FP[b][ref]["pads"] if x[0] == num]
        if not p:
            refuse("board %s %s has no pad %s" % (b, ref, num))
        return (p[0][1], p[0][2])
    gc = {b: {h: sorted((pn for pn, n in net_parts[b][h]["nets"].items() if n == "GND"), key=int) for h in RIBBONS} for b in "ab"}
    if gc["a"] != gc["b"]:
        refuse("the ribbons' ground pins differ between the boards: %s / %s" % (gc["a"], gc["b"]))
    branch_defs = []
    for ld in LEADS:
        if net_parts["b"][ld]["nets"].get("2") != "GND" or net_parts["a"][ld]["nets"].get("2") != "GND":
            refuse("%s pin 2 is not on GND on both boards" % ld)
        branch_defs.append((ld, "VH", ld, "2"))
    for h in RIBBONS:
        for pn in gc["b"][h]:
            branch_defs.append(("%s.%s" % (h, pn), "RIB", h, pn))
    for gr, _m in GROUPS:
        for pn in ("1", "2"):
            if net_parts["b"][gr]["nets"].get(pn) != "GND" or net_parts["a"][gr]["nets"].get(pn) != "GND":
                refuse("%s pin %s is not on GND on both boards" % (gr, pn))
            branch_defs.append(("%s.%s" % (gr, pn), "RET", gr, pn))
    n_kind = {k: sum(1 for d in branch_defs if d[1] == k) for k in ("VH", "RIB", "RET")}
    w("   %d VH lead pin 2s, %d ribbon ground conductors (J_AB1 pins %s; J_AB2 pins %s), %d XT60 return contacts (J_GR1 to J_GR3 pins 1 and 2)" % (
        n_kind["VH"], n_kind["RIB"], ",".join(gc["b"]["J_AB1"]), ",".join(gc["b"]["J_AB2"]), n_kind["RET"]))

    # injections: each lead's current at its rail's loads on board B (ground pads, weighted), out at the lead's land on board A. A load
    # not placed yet on board B is taken at its rail's entry ("entry") and, as the bound adverse to the ribbons, at J_AB1's ground pins
    # ("ribbon"); every figure below is the larger of the two
    rib_c = np.mean([pad("b", "J_AB1", pn) for pn in gc["b"]["J_AB1"]], axis=0)
    inj = {"entry": {}, "ribbon": {}}
    unplaced = {}
    for ld in LEADS:
        loads = rails[RAIL_OF[ld]].get("loads") or {}
        for var in ("entry", "ribbon"):
            pts = []
            for ref, amps in loads.items():
                f = FP["b"].get(ref)
                gp = [(x, y) for _n, x, y, net in (f["pads"] if f else []) if net in GND]
                if not gp:
                    if var == "entry":
                        unplaced.setdefault(ld, []).append(ref)
                    gp = [pad("b", ld, "2") if var == "entry" else tuple(rib_c)]
                for x, y in gp:
                    pts.append((x, y, float(amps) / len(gp)))
            if not pts:
                pts = [(pad("b", ld, "2")[0], pad("b", ld, "2")[1], 1.0)]
            tot = sum(p_[2] for p_ in pts)
            inj[var][ld] = [(x, y, a_ / tot) for x, y, a_ in pts]
    w("   each lead's return enters board B at its rail's loads' ground pads (the intent's loads as weights) and leaves board A at the lead's")
    w("   pin 2 land (the stage beside its connector: a Layer 10 placement condition, ASSUMPTION); a load not placed on board B yet is taken")
    w("   at its rail's entry and, as the bound adverse to the ribbons, at J_AB1's ground pins, the larger of the two kept: %s" % (
        "; ".join("%s: %s" % (k, ", ".join(sorted(v))) for k, v in sorted(unplaced.items())) or "none"))
    # the ground shift the supervisors' LDOs see: their ground pads on board B less J_5V_IOC's pin 2 land on board A (record l9t5's T10-A3)
    ldo_pads = [(x, y) for ref in ("U40", "U50", "U60") for _n, x, y, net in FP["b"][ref]["pads"] if net in GND]
    w("   the probe: the supervisors' LDOs' ground pads on board B (U40, U50, U60: %d pads) less J_5V_IOC's pin 2 on board A (T10-A3's shift)" % len(ldo_pads))
    w("")

    # the solve
    ratings = {}
    results = {}
    for Tt in (P0.TH, P0.TC):
        cond = {c[0]: c for c in G.conductors(F, Tt, True, n_ret=6, poe_awg=16)}
        bx = G.box(F)
        ratings[Tt] = P0.ratings(F, Tt)
        branches = []
        for name, kind, ref, pn in branch_defs:
            wire = cond["J_GR" if kind == "RET" else ref][3] * 1e-3
            lo, hi = bx[kind]
            p_ = BA.n + BB.node(*pad("b", ref, pn))
            q_ = BA.node(*pad("a", ref, pn))
            branches.append(dict(name=name, kind=kind, p=p_, q=q_, r_lo=wire + 2 * lo * 1e-3, r_hi=wire + 2 * hi * 1e-3))
        probe = ([(BA.n + BB.node(x, y), 1.0 / len(ldo_pads)) for x, y in ldo_pads], BA.node(*pad("a", "J_5V_IOC", "2")))
        rhs, tags = [], []
        for ci, (_lab, cur) in enumerate(cases):
            for var in ("entry", "ribbon"):
                i = np.zeros(BA.n + BB.n)
                for ld, amps in cur.items():
                    for x, y, f in inj[var][ld]:
                        i[BA.n + BB.node(x, y)] += amps * f
                    i[BA.node(*pad("a", ld, "2"))] -= amps
                rhs.append(i); tags.append((ci, var))
        for thin in (True, False):
            for fill in FILLS:
                gA = sheet_g(P0.PLANES["a"], Tt, thin, fill)
                gB = sheet_g(P0.PLANES["b"], Tt, thin, fill)
                res = solve_family(BA, BB, gA, gB, branches, rhs, probe)
                results[(Tt, thin, fill)] = (branches, tags, res)
    w("4. THE RETURN SOLVED (MODEL; per case, the largest current of each kind over the copper and fill corners, both injections and the")
    w("   contact vertices (each conductor at the vertex its search reaches, and the two uniform vertices), against its ratings)")
    worst, shifts, viol, pairs = {}, {}, 0, 0
    for ci, (lab, cur) in enumerate(cases):
        w("   %s: %.4f A (%s)" % (lab, sum(cur.values()), ", ".join("%s %.4f" % (k, v) for k, v in cur.items())))
        for Tt in (P0.TH, P0.TC):
            for kind in ("VH", "RIB", "RET"):
                best = None
                for thin in (True, False):
                    for fill in FILLS:
                        branches, tags, res = results[(Tt, thin, fill)]
                        for ri, (cj, var) in enumerate(tags):
                            if cj != ci:
                                continue
                            r = res[ri]
                            for k, b in enumerate(branches):
                                if b["kind"] != kind:
                                    continue
                                for which, I in (("searched vertex, %d other contacts low" % r["flips"][k], r["own"][k]), ("all high", r["hi"][k]), ("all low", r["lo"][k])):
                                    if best is None or abs(I) > best[0]:
                                        best = (abs(I), b["name"], which, thin, fill, var)
                pr, le = ratings[Tt][kind]
                worst[(ci, Tt, kind)] = (best, pr, le)
                w("     %+6.2f C %-3s %-9s %7.4f A (%s, copper %s, fill %.0f %%, %s): printed %.4f A %s; least %.4f A %s" % (
                    Tt, kind, best[1], best[0], best[2], "thin" if best[3] else "nominal", 100 * best[4], best[5], pr,
                    "holds" if best[0] <= pr else "OVER", le, "holds" if best[0] <= le else "OVER"))
            sh = max(r["shift_max"] for (Tx, _th, _fi), (_b, tg, rs) in results.items() if Tx == Tt for (cj, _v), r in zip(tg, rs) if cj == ci)
            shifts[(ci, Tt)] = sh
            w("     %+6.2f C the ground shift at the supervisors' LDOs, every vertex evaluated: at most %.4f V" % (Tt, sh))
    for (_Tx, _th, _fi), (_b, _tg, rs) in results.items():
        viol = max(viol, max(max(r["flips"]) for r in rs)); pairs += sum(sum(1 for f_ in r["flips"] if f_) for r in rs)
    w("   the vertex search (from each conductor's own contacts low and every other high, every contact whose move raises its current set")
    w("   low in turn until no single move raises it): %d searches ended away from the own-low vertex, at most %d other contacts low" % (pairs, viol))
    w("")
    # the comparison with the one-node model
    w("5. AGAINST THE ONE-NODE MODEL OF l8r2_p0.py (Rs = 0, the same totals; MODEL)")
    for ci, (lab, cur) in enumerate(cases):
        tot = sum(cur.values())
        for Tt in (P0.TH, P0.TC):
            r1 = P0.rows(F, tot, Tt)
            w("   %-60s %+6.2f C: one node VH %.4f, RIB %.4f, RET %.4f A; distributed VH %.4f, RIB %.4f, RET %.4f A" % (
                lab[:60], Tt, r1["VH"], r1["RIB"], r1["RET"], worst[(ci, Tt, "VH")][0][0], worst[(ci, Tt, "RIB")][0][0], worst[(ci, Tt, "RET")][0][0]))
    w("")
    # 5b. the route for the declared upper bound's ribbon row at the least rating: a fourth return lead beside the ribbon headers (a
    # what-if on the same model; NOT drafted: no service row needs it)
    PL4 = {}
    for b in ("b", "a"):
        tg = [pad(b, "J_AB1", pn) for pn in gc[b]["J_AB1"]]
        PL4[b] = place("J_GR4", xt_local, xt_pins, tg, FP[b], SEG[b], [pl["box"] for pl in PL[b].values()])
    ci_d = [ci for ci, (lab, _c) in enumerate(cases) if lab.startswith("the declared")][0]
    cond = {c[0]: c for c in G.conductors(F, P0.TH, True, n_ret=8, poe_awg=16)}
    branches4 = list(results[(P0.TH, True, 0.5)][0])
    for pn in (0, 1):
        branches4.append(dict(name="J_GR4.%d" % (pn + 1), kind="RET", p=BA.n + BB.node(*PL4["b"]["pins"][pn]), q=BA.node(*PL4["a"]["pins"][pn]),
                              r_lo=cond["J_GR"][3] * 1e-3 + 2 * G.box(F)["RET"][0] * 1e-3, r_hi=cond["J_GR"][3] * 1e-3 + 2 * G.box(F)["RET"][1] * 1e-3))
    rhs4 = []
    for var in ("entry", "ribbon"):
        i = np.zeros(BA.n + BB.n)
        for ld, amps in cases[ci_d][1].items():
            for x, y, f in inj[var][ld]:
                i[BA.n + BB.node(x, y)] += amps * f
            i[BA.node(*pad("a", ld, "2"))] -= amps
        rhs4.append(i)
    rib4 = 0.0
    for thin in (True, False):
        for fill in FILLS:
            res4 = solve_family(BA, BB, sheet_g(P0.PLANES["a"], P0.TH, thin, fill), sheet_g(P0.PLANES["b"], P0.TH, thin, fill), branches4, rhs4,
                                ([(BA.n + BB.node(x, y), 1.0 / len(ldo_pads)) for x, y in ldo_pads], BA.node(*pad("a", "J_5V_IOC", "2"))))
            for r in res4:
                rib4 = max(rib4, max(abs(r["own"][k]) for k, b in enumerate(branches4) if b["kind"] == "RIB"))
    w("5b. THE ROUTE FOR THE DECLARED UPPER BOUND'S RIBBON ROW (a what-if on the same model, NOT drafted: no service row needs it): a fourth")
    w("   return lead J_GR4 placed beside J_AB1 (board B at (%.2f, %.2f), %.1f mm from its ground pins; board A at (%.2f, %.2f), %.1f mm), the" % (
        PL4["b"]["at"][0], PL4["b"]["at"][1], PL4["b"]["dist"], PL4["a"]["at"][0], PL4["a"]["at"][1], PL4["a"]["dist"]))
    w("   declared upper bound at %+.2f C over every corner: the ribbon's largest %.4f A against the least %.4f A (%s)" % (
        P0.TH, rib4, ratings[P0.TH]["RIB"][1], "holds" if rib4 <= ratings[P0.TH]["RIB"][1] else "still OVER"))
    w("")
    # the verdict
    ok_pr = all(v[0][0] <= v[1] for v in worst.values())
    ok_le = all(v[0][0] <= v[2] for v in worst.values())
    act = [ci for ci, (lab, _c) in enumerate(cases) if lab.startswith("C-DEV rev 2") or lab.startswith("the largest")]
    ok_service_pr = all(worst[(ci, Tt, k)][0][0] <= worst[(ci, Tt, k)][1] for ci in act for Tt in (P0.TH, P0.TC) for k in ("VH", "RIB", "RET"))
    ok_service_le = all(worst[(ci, Tt, k)][0][0] <= worst[(ci, Tt, k)][2] for ci in act for Tt in (P0.TH, P0.TC) for k in ("VH", "RIB", "RET"))
    over = sorted({(cases[ci][0], Tt, k, worst[(ci, Tt, k)][0][0], worst[(ci, Tt, k)][2]) for (ci, Tt, k), v in worst.items() if v[0][0] > v[2]})
    rib_max = max(v[0][0] for (ci, Tt, k), v in worst.items() if k == "RIB")
    sh_max = max(shifts[(ci, Tt)] for ci in act for Tt in (P0.TH, P0.TC))
    w("6. VERDICT (MODEL; the sockets placed in section 2, the composed netlists, the corners and the vertex family above)")
    w("   every case row on the printed ratings: %s (the ribbon's largest %.4f A against 1 A: the declared upper bound's printed row, STILL OPEN" % (
        "HOLDS" if ok_pr else "DOES NOT HOLD", rib_max))
    w("     on the one-node model, holds on the placed distributed one); on the least ratings at the inside air: %s" % ("HOLDS" if ok_le else "DOES NOT HOLD"))
    w("   the service cases (C-DEV rev 2, the active row, and the largest steady state) on the printed ratings: %s; on the least: %s" % (
        "HOLD" if ok_service_pr else "DO NOT HOLD", "HOLD" if ok_service_le else "DO NOT HOLD"))
    for lab, Tt, k, cur_, le_ in over:
        w("     over the least rating: %s at %+.2f C, %s: %.4f A against %.4f A, the least rating the sheet allows (INFERRED)" % (lab.split(" (")[0], Tt, k, cur_, le_))
        if k == "VH":
            w("       the same lead's pin 1 carries its rail's whole declared peak on the same derating: L8R2-F43's vendor task (JST's curve)")
            w("       decides both pins; a return design cannot remove a pin 1 row")
        else:
            w("       Wurth's WR-CAB derating against ambient is not held: the vendor task L8R2-F44 (Wurth, UNSENT); the route if its curve is")
            w("       lower is a fourth return lead beside the ribbon headers (5b)")
    w("   the ground shift at the supervisors' LDOs on the service cases: at most %.4f V (the T10-A3 chain took %.4f V with the dedicated" % (sh_max, 0.0114))
    w("     return and %.4f V as drawn, both from the one-node model)" % 0.0681)
    w("   DISPOSITION OF V6-B1 (the author's; the targeted recheck decides): the three drafted sockets PLACED (section 2, L8R2-D10) and the return")
    w("     SOLVED as a distributed network at the copper, temperature, fill and contact corners: %s; no fourth lead or bar is" % (
        "every printed row holds and the service cases hold on the least ratings too" if (ok_pr and ok_service_le) else "NOT every row holds"))
    w("     needed by any service row (SESSION decision L8R2-D11: the fourth lead of 5b is a named route, not drafted; reversed if Wurth's")
    w("     WR-CAB curve or the owner makes the declared upper bound a served state); PROVISIONAL on the plane fill (50 % bounds no drawn")
    w("     split: Layer 10's routed extraction is the")
    w("     validation task) and on the stages' placement beside their connectors on board A; L8R2-F33a's 'within 17 mm' is withdrawn as the")
    w("     condition's form: the placed sites and this solve replace it")
    w("")
    P = {
        "every placed part's courtyard is clear of every placed courtyard and inside the outline": all(pl["gap"] >= CLEAR - 1e-9 for b in "ab" for pl in PL[b].values()),
        "the conductors read from the composed netlists are the record's six VH, seventeen ribbon and six XT60 contacts": n_kind == {"VH": 6, "RIB": 17, "RET": 6},
        "every case row holds on the printed ratings in the distributed model": ok_pr,
        "the service cases hold on the printed and the least ratings in the distributed model": ok_service_pr and ok_service_le,
        "every search ended at a stable vertex (no single contact's move raises its current or the shift there)": all(
            r["stable"] for (_b, _tg, rs) in results.values() for r in rs),
        "the distributed ground shift at the LDOs on the service cases stays under the T10-A3 chain's as-drawn figure": sh_max < 0.0681,
    }
    w("7. PREDICATES")
    for k, v in P.items():
        w("   %-120s %s" % (k, "yes" if v else "NO"))
    w("")
    w("l8r2_dist: done")
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
