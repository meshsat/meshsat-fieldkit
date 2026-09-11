#!/usr/bin/env python3
"""DC drop and current density of the power copper (MESHSAT-862 Stage C, 8 Sep 2026; MESHSAT-818 item 2 brought forward as a gate).
The pipeline never computed whether a rail's copper carries its current (appendix 32.64 W1); the A21 rule "rail current never travels in
router tracks" was enforced by eye and by width read-backs. This builds a resistive mesh from the filled board and solves it.

Model: every copper item of a rail net (filled zones, tracks, pads) is rasterised per copper layer on a square grid (CELL mm); each cell is a
node joined to its four neighbours by the sheet resistance of that layer (rho_cu 1.72e-8 ohm m at 20 C, thickness from the stackup block or
35 um outer and 15.2 um inner by default); vias of the net join the layers they span (R = rho L / (pi d t_plating), plating 25 um); the
source pads (the intent file's source reference) are held at 0 V and every load pad sinks its share of the intent current (loads by reference
where given, else the rail's typical current split over the pads of the parts whose only power pin on this net is a real load: the parts
listed in the intent's loads, or, failing that, every non-passive footprint on the net); the system G v = i is solved by scipy's DIRECT sparse solve
(`spsolve`; the docstring said conjugate gradient until 10 September 2026 and the code never did, report 1 item 7), and the solution's
relative residual is checked before any verdict is read off it.  Reported per rail: the worst node's drop in mV and percent of the rail
voltage, the worst cell's current density in A/mm2 and the IPC-2221 external and internal limits for 10 K rise (I = k dT^0.44 A^0.725,
k 0.048 external, 0.024 internal, A in mil2), the layer share of the current, and MET or MISSED against the rail's budget (its own if the
intent file gives it one, else --budget, default 2 percent).  **The drop alone decides the verdict**: the density at a single-cell neck
overstates by the cell-to-width ratio (a 0.4 mm track is one 0.5 mm cell), so it is printed and not gated until the raster is validated.

Usage: dc_drop.py <board.kicad_pcb> [--cell 0.5] [--budget 0.02] [--rails NET,NET] [--json out.json] [--png out.png]   -> exit 1 on a miss.
Every number comes from the board and the intent file; a rail without a resolvable source or load is reported UNRESOLVED and counts as a miss."""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RHO = 1.72e-8   # ohm m
PLATING = 25e-6

def sheet(t_mm): return RHO / (t_mm * 1e-3)   # ohm per square

def ipc_limit(area_mm2, dT=10.0, internal=False):
    """IPC-2221 current for a cross-section (mm2) at dT K; returns amps."""
    a_mil2 = area_mm2 / (0.0254 ** 2); k = 0.024 if internal else 0.048
    return k * (dT ** 0.44) * (a_mil2 ** 0.725)

def main(a):
    if not a: print(__doc__); return 2
    import pcbnew, numpy as np, intent
    import verdict as _v
    from impedance_check import read_stackup
    cell = float(a[a.index("--cell") + 1]) if "--cell" in a else 0.5
    budget = float(a[a.index("--budget") + 1]) if "--budget" in a else 0.02
    b = pcbnew.LoadBoard(a[0]); it = intent.load(a[0])
    if not it:
        print("dc_drop: FAIL no intent file for this board (out/<stem>-intent.json; the schematic generator writes it)")
        return _v.write("dc_drop", _v.INCONCLUSIVE, denominator=0, inputs={"board": a[0]},
                        note="no intent file for this board, so no rail budget was known")
    rails = it["rails"]
    if "--rails" in a: rails = {k: v for k, v in rails.items() if k in a[a.index("--rails") + 1].split(",")}
    stack = read_stackup(a[0]) or []; thick = {n: th for n, k, th, er in stack if k == "copper"}
    cu_layers = list(b.GetEnabledLayers().CuStack())   # KiCad 9 layer ids are not consecutive; the board's copper stack in order
    lname = {L: b.GetLayerName(L) for L in cu_layers}
    def t_of(L): return thick.get(lname[L], 0.035 if L in (pcbnew.F_Cu, pcbnew.B_Cu) else 0.0152)
    bb = b.GetBoardEdgesBoundingBox(); x0, y0 = bb.GetLeft() / 1e6, bb.GetTop() / 1e6; W, H = bb.GetWidth() / 1e6, bb.GetHeight() / 1e6
    nx, ny = int(W / cell) + 2, int(H / cell) + 2
    fps = list(b.GetFootprints()); results = []; miss = 0
    for net, r in rails.items():
        netnames = {net, "/" + net.lstrip("/")}
        # occupancy per layer
        occ = {L: np.zeros((ny, nx), dtype=bool) for L in cu_layers}
        def mark(L, poly_set, value=True):
            for i in range(poly_set.OutlineCount()):
                for h in range(poly_set.HoleCount(i)): _fill(L, poly_set.Hole(i, h), False)   # holes first would be undone by the outline: outline, then holes
                _fill(L, poly_set.Outline(i), True)
                for h in range(poly_set.HoleCount(i)): _fill(L, poly_set.Hole(i, h), False)
        def _fill(L, o, value):
                pts = [(o.GetPoint(k).x / 1e6, o.GetPoint(k).y / 1e6) for k in range(o.PointCount())]
                xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
                for gy in range(max(0, int((min(ys) - y0) / cell)), min(ny, int((max(ys) - y0) / cell) + 2)):
                    py = y0 + (gy + 0.5) * cell; xin = []
                    for k in range(len(pts)):
                        (ax, ay), (bx, by) = pts[k], pts[(k + 1) % len(pts)]
                        if (ay > py) != (by > py): xin.append(ax + (py - ay) * (bx - ax) / (by - ay))
                    xin.sort()
                    for k in range(0, len(xin) - 1, 2):
                        for gx in range(max(0, int((xin[k] - x0) / cell)), min(nx, int((xin[k + 1] - x0) / cell) + 1)): occ[L][gy, gx] = value
        raster_note = []
        for z in b.Zones():
            if z.GetIsRuleArea() or z.GetNetname() not in netnames or z.GetFilledArea() <= 0: continue
            L = z.GetFirstLayer()
            if L in occ:
                before = int(occ[L].sum()); mark(L, z.GetFilledPolysList(L)); raster_note.append("%s %.0f of %.0f mm2" % (z.GetZoneName()[:18], (int(occ[L].sum()) - before) * cell * cell, z.GetFilledArea() / 1e12))
        vias = []
        for tr in b.GetTracks():
            if tr.GetNetname() not in netnames: continue
            if tr.GetClass() == "PCB_VIA": vias.append(tr); continue
            L = tr.GetLayer()
            if L not in occ: continue
            n = max(2, int(tr.GetLength() / 1e6 / cell) + 2); w = tr.GetWidth() / 1e6
            for k in range(n):
                u = k / (n - 1); px = (tr.GetStart().x + u * (tr.GetEnd().x - tr.GetStart().x)) / 1e6; py = (tr.GetStart().y + u * (tr.GetEnd().y - tr.GetStart().y)) / 1e6
                for dx in (-w / 2, 0, w / 2):
                    for dy in (-w / 2, 0, w / 2):
                        gx, gy = int((px + dx - x0) / cell), int((py + dy - y0) / cell)
                        if 0 <= gx < nx and 0 <= gy < ny: occ[L][gy, gx] = True
        pads = []
        for f in fps:
            for p in f.Pads():
                if p.GetNetname() in netnames: pads.append((f, p))
        for f, p in pads:
            for L in cu_layers:
                if p.IsOnLayer(L): mark(L, p.GetEffectivePolygon(L) if hasattr(p, "GetEffectivePolygon") else p.GetEffectivePolygon())
        # nodes
        index = {}; coords = []
        for L in cu_layers:
            ys, xs = np.nonzero(occ[L])
            for gy, gx in zip(ys, xs): index[(L, gy, gx)] = len(coords); coords.append((L, gy, gx))
        N = len(coords)
        if N == 0: results.append((net, "UNRESOLVED", "no copper of this net", 0, 0, 0, {})); miss += 1; continue
        rows = []; cols = []; vals = []
        def add(i, j, g): rows.extend([i, j, i, j]); cols.extend([i, j, j, i]); vals.extend([g, g, -g, -g])
        for (L, gy, gx), i in index.items():
            g = 1.0 / sheet(t_of(L))
            for dy, dx in ((0, 1), (1, 0)):
                j = index.get((L, gy + dy, gx + dx))
                if j is not None: add(i, j, g)
        barrels = [(v.GetPosition(), v.GetDrillValue() / 1e6, v.TopLayer(), v.BottomLayer()) for v in vias]
        barrels += [(p.GetPosition(), max(p.GetDrillSize().x, 1e5) / 1e6, pcbnew.F_Cu, pcbnew.B_Cu) for f, p in pads if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]   # a through-hole pad is a barrel through every layer (review of 8 Sep 2026)
        for pos, d, Lt, Lb in barrels:
            gx, gy = int((pos.x / 1e6 - x0) / cell), int((pos.y / 1e6 - y0) / cell)
            i_t, i_b = cu_layers.index(Lt) if Lt in cu_layers else 0, cu_layers.index(Lb) if Lb in cu_layers else len(cu_layers) - 1
            span = cu_layers[min(i_t, i_b):max(i_t, i_b) + 1]
            nodes = [index.get((L, gy, gx)) for L in span]; nodes = [n for n in nodes if n is not None]
            if len(nodes) < 2: continue
            rv = RHO * (1.6e-3 / max(1, len(span) - 1)) / (math.pi * d * 1e-3 * PLATING)
            for k in range(len(nodes) - 1): add(nodes[k], nodes[k + 1], 1.0 / rv)
        # sources and loads
        def pad_nodes(f, p):
            out = []
            for L in cu_layers:
                if not p.IsOnLayer(L): continue
                gx, gy = int((p.GetPosition().x / 1e6 - x0) / cell), int((p.GetPosition().y / 1e6 - y0) / cell)
                n = index.get((L, gy, gx))
                if n is not None: out.append(n)
            return out
        src = [n for f, p in pads if f.GetReference() == r["source"] for n in pad_nodes(f, p)]
        loads = r.get("loads") or {}
        if not loads:
            cands = [f for f, p in pads if f.GetReference() != r["source"] and f.GetReference()[0] in "UJ" and not f.GetReference().startswith("JP")]
            if not cands: cands = [f for f, p in pads if f.GetReference() != r["source"] and not f.GetReference().startswith(("TP", "C", "R", "D"))]   # a pack board: the FETs and the leads
            refs = sorted({f.GetReference() for f in cands})
            loads = {ref: r["amps_typ"] / len(refs) for ref in refs} if refs else {}
        sinks = {}
        for ref, amps in loads.items():
            ns = [n for f, p in pads if f.GetReference() == ref for n in pad_nodes(f, p)]
            for n in ns: sinks[n] = sinks.get(n, 0.0) + amps / len(ns)
        if not src or not sinks: results.append((net, "UNRESOLVED", "source %s pads %d, load pads %d" % (r["source"], len(src), len(sinks)), 0, 0, 0, {})); miss += 1; continue
        try:
            import scipy.sparse as sp, scipy.sparse.linalg as spl, scipy.sparse.csgraph as csg
            G = sp.coo_matrix((vals, (rows, cols)), shape=(N, N)).tocsr()
            # only the copper reachable from the source carries current; a load on an unreachable piece is a real finding (the copper does not connect)
            ncomp, lab = csg.connected_components(sp.coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(N, N)), directed=False)
            reach = {lab[n] for n in src}; unreachable = [n for n in sinks if lab[n] not in reach]
            if unreachable:
                # the pieces, so the copper gap is found (8 Sep 2026): layer set, extent, cells, and whether the source or a load sits on it
                by = {}
                for n_, c_ in enumerate(lab): by.setdefault(int(c_), []).append(n_)
                srcset = set(src)
                for c_, ns_ in sorted(by.items(), key=lambda kv: -len(kv[1]))[:8]:
                    Ls_ = sorted({lname[coords[n_][0]] for n_ in ns_}); xs_ = [x0 + (coords[n_][2] + 0.5) * cell for n_ in ns_]; ys_ = [y0 + (coords[n_][1] + 0.5) * cell for n_ in ns_]
                    print("dc_drop:   piece of %s: %d cells on %s, x %.0f..%.0f y %.0f..%.0f%s%s" % (net, len(ns_), "+".join(Ls_), min(xs_), max(xs_), min(ys_), max(ys_), " SOURCE" if any(n_ in srcset for n_ in ns_) else "", (" loads %d" % sum(1 for n_ in ns_ if n_ in sinks)) if any(n_ in sinks for n_ in ns_) else ""))
                results.append((net, "MISSED", "%d of %d load pads on copper not connected to the source %s through this net's copper and vias (the mesh: %d pieces)" % (len(unreachable), len(sinks), r["source"], ncomp), 0, 1.0, 0, {})); miss += 1; continue
            keep = np.array([i for i in range(N) if lab[i] in reach and i not in set(src)]); i_vec = np.zeros(N)
            for n, amps in sinks.items(): i_vec[n] -= amps
            Gk = G[keep][:, keep].tocsc(); v = np.zeros(N)
            sol = spl.spsolve(Gk, i_vec[keep]); v[keep] = sol
            # 10 September 2026 (report 1 item 7): a verdict was read off whatever spsolve returned. A singular or badly
            # conditioned mesh gives a silent nonsense solution, so the residual is measured and a rail whose system was not
            # actually solved is UNRESOLVED, never MET.
            rhs = i_vec[keep]; resid = float(np.abs(Gk @ sol - rhs).max()); scale = float(np.abs(rhs).max()) or 1.0
            if not np.all(np.isfinite(sol)) or resid / scale > 1e-6:
                results.append((net, "UNRESOLVED", "the resistive mesh did not solve: residual %.3g against a %.3g A right-hand side (%d nodes)" % (resid, scale, len(keep)), 0, 0, 0, {})); miss += 1; continue
        except ImportError:
            results.append((net, "UNRESOLVED", "scipy missing on this host (apt-get install python3-scipy)", 0, 0, 0, {})); miss += 1; continue
        drop = -v.min() if v.min() < 0 else v.max(); drop = abs(v).max()
        # branch currents and density
        worst_j = 0.0; worst = None; share = {}
        for (L, gy, gx), i in index.items():
            g = 1.0 / sheet(t_of(L)); t = t_of(L)
            for dy, dx in ((0, 1), (1, 0)):
                j = index.get((L, gy + dy, gx + dx))
                if j is None: continue
                cur = abs(v[i] - v[j]) * g; jd = cur / (cell * t)   # A/mm2 through the cell face (width cell, thickness t)
                share[lname[L]] = share.get(lname[L], 0.0) + cur
                if jd > worst_j: worst_j = jd; worst = (lname[L], x0 + (gx + 0.5) * cell, y0 + (gy + 0.5) * cell, cur)
        tot = sum(share.values()) or 1.0; share = {k: round(x / tot, 2) for k, x in share.items()}
        amps = sum(sinks.values()); pct = drop / r["volts"] if r["volts"] else 0.0
        # density limit: the IPC-2221 current for one cell width of this copper at 10 K, as A/mm2
        lim = {}
        for L in cu_layers:
            t = t_of(L); lim[lname[L]] = ipc_limit(cell * t, 10.0, L not in (pcbnew.F_Cu, pcbnew.B_Cu)) / (cell * t)
        jl = lim.get(worst[0], 1e9) if worst else 1e9
        rb = float(r.get("budget", budget))   # a rail may carry its own budget in the intent (8 Sep 2026)
        verdict = "MET" if pct <= rb else "MISSED"   # the drop decides; the density at a single-cell neck (a 0.4 mm track is one 0.5 mm cell) overstates by the cell-to-width ratio and is reported, not gated, until the raster is validated (8 Sep 2026 02:25)
        if verdict != "MET": miss += 1
        results.append((net, verdict, "raster %s; %.1f A over %d nodes: worst drop %.0f mV (%.2f%% of %.1f V, budget %.0f%%); worst density %.1f A/mm2 at %s (%.1f, %.1f) against IPC-2221 %.1f A/mm2 at 10 K (reported, not gated); layer share %s" % ("; ".join(raster_note[:4]) or "-", amps, N, drop * 1e3, pct * 100, r["volts"], rb * 100, worst_j, worst[0], worst[1], worst[2], jl, share), drop, pct, worst_j, share))
    if not results:
        print("dc_drop: FAIL no rail to check (the intent file lists none)")
        return _v.write("dc_drop", _v.INCONCLUSIVE, denominator=0, inputs={"board": a[0]},
                        note="the intent file lists no rail, so no drop was computed")
    for net, v, text, *_ in results: print("dc_drop: %-10s %-10s %s" % (v, net, text))
    print("dc_drop: %d of %d rails MET (cell %.2f mm, budget %.0f%%)" % (len(results) - miss, len(results), cell, budget * 100))
    if "--json" in a: json.dump([dict(net=r[0], verdict=r[1], text=r[2], drop_v=r[3], pct=r[4], j_max=r[5], share=r[6]) for r in results], open(a[a.index("--json") + 1], "w"), indent=1)
    return _v.write("dc_drop", _v.PASS if not miss else _v.FAIL,
                    counts={"met": len(results) - miss, "missed": miss},
                    denominator=len(results),
                    evidence=["%s %s %.2f%% of %.1f V" % (r[1], r[0], r[4] * 100, rails[r[0]]["volts"]) for r in results if r[1] != "MET"],
                    inputs={"board": a[0]},
                    note="cell %.2f mm, default budget %.0f%%" % (cell, budget * 100))

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
