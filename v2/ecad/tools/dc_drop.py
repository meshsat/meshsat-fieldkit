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


def dT_of(rail): return float(rail.get("density_dT", 10.0))   # a rail may declare its own rise, with a reason

# {net: {"drop": bool, "density": bool}} for the rails that missed, filled as each is judged. Two rules read
# this tool and each needs its own evidence; see the comment where it is written.
_MISSED_ON = {}

def ipc_limit(area_mm2, dT=10.0, internal=False):
    """IPC-2221 current for a cross-section (mm2) at dT K; returns amps."""
    a_mil2 = area_mm2 / (0.0254 ** 2); k = 0.024 if internal else 0.048
    return k * (dT ** 0.44) * (a_mil2 ** 0.725)

def _draw(png, net, jmap, occ, lname, cu_layers, x0, y0, cell, nx, ny, jl, marks, amps, verdict):
    """One panel per copper layer: the net's copper in grey, the current density on it, and the three worst
    places marked. This is what `--png` has meant in the usage line since 8 September 2026 and never did:
    the option was read by nothing, so every run that asked for a picture got a silent nothing back. It is
    written now because the necks this tool reports are geometry, and the record's own rule for a stopped
    chain is to draw the region and read it rather than reason about coordinates (owner decision 2, 5 Sep)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt, numpy as np
    live = [L for L in cu_layers if occ[L].any()]
    if not live: return
    ncol = min(3, len(live)); nrow = (len(live) + ncol - 1) // ncol
    fig, axes = plt.subplots(nrow, ncol, figsize=(6.2 * ncol, 4.6 * nrow), squeeze=False)
    ext = (x0, x0 + nx * cell, y0 + ny * cell, y0)          # board coordinates, y down as KiCad draws it
    for k, L in enumerate(live):
        ax = axes[k // ncol][k % ncol]
        ax.imshow(np.where(occ[L], 1.0, np.nan), extent=ext, cmap="Greys", vmin=0, vmax=3, interpolation="nearest")
        j = np.where(jmap[L] > 0, jmap[L], np.nan)
        im = ax.imshow(j, extent=ext, cmap="inferno", vmin=0, vmax=max(jl * 2.0, float(np.nanmax(j)) if np.isfinite(np.nanmax(j)) else jl), interpolation="nearest")
        fig.colorbar(im, ax=ax, shrink=0.8, label="A/mm2 (bar %.0f)" % jl)
        for txt, mlay, mx, my, mk in marks:
            if mlay is not None and mlay != lname[L]: continue
            ax.plot([mx], [my], mk, mfc="none", mec="deepskyblue", ms=13, mew=2)
        ax.set_title("%s on %s" % (net, lname[L]), fontsize=9); ax.set_aspect("equal")
        ax.tick_params(labelsize=7)
    for k in range(len(live), nrow * ncol): axes[k // ncol][k % ncol].axis("off")
    fig.suptitle("%s: %s, %.1f A. %s" % (net, verdict, amps, "; ".join(m[0] for m in marks)), fontsize=10)
    fig.tight_layout()
    out = png if len(png) > 4 and png.endswith(".png") else png + ".png"
    out = out[:-4] + "-" + net.strip("/").replace("+", "p") + ".png"
    fig.savefig(out, dpi=110); plt.close(fig)
    print("dc_drop: wrote %s" % out)


def main(a):
    if not a: print(__doc__); return 2
    import pcbnew, numpy as np, intent
    import verdict as _v
    from impedance_check import read_stackup
    cell = float(a[a.index("--cell") + 1]) if "--cell" in a else 0.5
    png = a[a.index("--png") + 1] if "--png" in a else None
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
        zone_occ = {L: np.zeros((ny, nx), dtype=bool) for L in cu_layers}   # cells a POUR or a pad of this net fills
        for z in b.Zones():
            if z.GetIsRuleArea() or z.GetNetname() not in netnames or z.GetFilledArea() <= 0: continue
            L = z.GetFirstLayer()
            if L in occ:
                before = int(occ[L].sum()); mark(L, z.GetFilledPolysList(L)); zone_occ[L] |= occ[L]; raster_note.append("%s %.0f of %.0f mm2" % (z.GetZoneName()[:18], (int(occ[L].sum()) - before) * cell * cell, z.GetFilledArea() / 1e12))
        vias = []
        # OWNER RULING 22, 13 September 2026: the per-cell density does not converge for copper narrower than
        # a cell (32.162: the verdict moved 41 to 56 percent between a 0.50 and a 0.25 mm cell, and CELL+
        # flipped). A TRACK has a width, so it does not need a grid to be judged: its through-current is read
        # off the solved mesh and compared with IPC-2221 for its own cross-section. The raster keeps the zones,
        # where it measurably does converge (VBAT moved 6 percent, the PA band 9). These two lists are what
        # that pass needs, collected here because this is where the geometry is already being walked.
        net_tracks = []
        trk_occ = {L: np.zeros((ny, nx), dtype=bool) for L in occ}
        # THE OTHER HALF OF RULING 22. Giving the LIMIT a track's real width is not enough while the mesh still
        # models that track as a cell-wide conductor: the current it attracts is then a function of the cell,
        # and the conductor ratio moves with it (measured: VBAT 4.69 to 2.32 across a two-fold cell change).
        # Every in-plane edge got one square of sheet resistance, which is right for a cell FULL of copper and
        # wrong for a cell a 0.4 mm track passes through. `frac` is the effective copper width in a cell as a
        # fraction of the cell, 1.0 for pour and pad copper and w/cell for a narrower track, and an edge is
        # scaled by the NARROWER of the two cells it joins, which is the series view. As the cell shrinks below
        # a track's width the factor goes to 1 and the model converges.
        frac = {L: np.zeros((ny, nx)) for L in occ}
        for tr in b.GetTracks():
            if tr.GetNetname() not in netnames: continue
            if tr.GetClass() == "PCB_VIA": vias.append(tr); continue
            L = tr.GetLayer()
            if L not in occ: continue
            n = max(2, int(tr.GetLength() / 1e6 / cell) + 2); w = tr.GetWidth() / 1e6
            net_tracks.append((L, tr.GetStart().x / 1e6, tr.GetStart().y / 1e6, tr.GetEnd().x / 1e6, tr.GetEnd().y / 1e6, w, tr.GetLength() / 1e6))
            for k in range(n):
                u = k / (n - 1); px = (tr.GetStart().x + u * (tr.GetEnd().x - tr.GetStart().x)) / 1e6; py = (tr.GetStart().y + u * (tr.GetEnd().y - tr.GetStart().y)) / 1e6
                for dx in (-w / 2, 0, w / 2):
                    for dy in (-w / 2, 0, w / 2):
                        gx, gy = int((px + dx - x0) / cell), int((py + dy - y0) / cell)
                        if 0 <= gx < nx and 0 <= gy < ny:
                            occ[L][gy, gx] = True; trk_occ[L][gy, gx] = True
                            frac[L][gy, gx] = max(frac[L][gy, gx], min(1.0, w / cell))
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
        # 13 September 2026: a cell a POUR fills is full copper even where a track crosses it. This line used
        # to fill only cells whose fraction was still zero, so a track lying INSIDE its own rail's island was
        # modelled as a bare 0.4 mm conductor with the island's copper thrown away, and the conductor pass
        # then judged it carrying current the island was really sharing. A24's +5V_S1 and +5V_S3 read exactly
        # 1.00 that way, on 4.9 mm of track that sits inside an 84 mm2 island of their own net.
        for L in occ: frac[L][zone_occ[L]] = 1.0
        for L in occ: frac[L][occ[L] & (frac[L] == 0.0)] = 1.0   # pad copper fills its cell; a track set its own
        for (L, gy, gx), i in index.items():
            g = 1.0 / sheet(t_of(L)); f_i = frac[L][gy, gx] or 1.0
            for dy, dx in ((0, 1), (1, 0)):
                j = index.get((L, gy + dy, gx + dx))
                if j is None: continue
                add(i, j, g * min(f_i, frac[L][gy + dy, gx + dx] or 1.0))
        net_vias = []    # (x, y, drill mm, barrel wall mm2, rv ohm, mesh nodes) for every barrel of this net
        barrels = [(v.GetPosition(), v.GetDrillValue() / 1e6, v.TopLayer(), v.BottomLayer()) for v in vias]
        barrels += [(p.GetPosition(), max(p.GetDrillSize().x, 1e5) / 1e6, pcbnew.F_Cu, pcbnew.B_Cu) for f, p in pads if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]   # a through-hole pad is a barrel through every layer (review of 8 Sep 2026)
        via_cells = {}   # (gy, gx) -> [barrel count, total barrel wall cross-section mm2]: where current enters a plane
        for pos, d, Lt, Lb in barrels:
            gx, gy = int((pos.x / 1e6 - x0) / cell), int((pos.y / 1e6 - y0) / cell)
            _vc = via_cells.setdefault((gy, gx), [0, 0.0]); _vc[0] += 1; _vc[1] += math.pi * d * PLATING * 1e3
            i_t, i_b = cu_layers.index(Lt) if Lt in cu_layers else 0, cu_layers.index(Lb) if Lb in cu_layers else len(cu_layers) - 1
            span = cu_layers[min(i_t, i_b):max(i_t, i_b) + 1]
            nodes = [index.get((L, gy, gx)) for L in span]; nodes = [n for n in nodes if n is not None]
            if len(nodes) < 2: continue
            rv = RHO * (1.6e-3 / max(1, len(span) - 1)) / (math.pi * d * 1e-3 * PLATING)
            for k in range(len(nodes) - 1): add(nodes[k], nodes[k + 1], 1.0 / rv)
            # RULING 22 APPLIED TO A VIA (13 September 2026). A plane cell at a via is a funnel: the barrel's
            # whole current crosses one cell face, and IPC-2221's figure is for a long conductor at thermal
            # steady state, not for a spreading region a millimetre across. E7's VIN_RAW read 2.20 on such a
            # cell while the barrel carrying it sat at 0.79 of its OWN limit, and clear of every via that
            # rail's worst cell reads 1.21. So the via is judged as a via, on its barrel's cross-section,
            # and the pour bar is applied to pour copper. The list is kept here because this is where the
            # geometry is walked; the current comes off the solved mesh below.
            net_vias.append((pos.x / 1e6, pos.y / 1e6, d, math.pi * d * PLATING * 1e3, rv, list(nodes)))
        # sources and loads
        def pad_nodes(f, p):
            out = []
            for L in cu_layers:
                if not p.IsOnLayer(L): continue
                gx, gy = int((p.GetPosition().x / 1e6 - x0) / cell), int((p.GetPosition().y / 1e6 - y0) / cell)
                n = index.get((L, gy, gx))
                if n is not None: out.append(n)
            return out
        # A rail may enter the board at more than one place, and a GROUND always does: B19's return leaves
        # through four JST-VH connectors, and holding one of them at 0 V would send all 21 A through one
        # connector's ground pin and measure a board that does not exist. `source` takes a list for that.
        srcrefs = list(r["source"]) if isinstance(r["source"], (list, tuple)) else [r["source"]]
        src = [n for f, p in pads if f.GetReference() in srcrefs for n in pad_nodes(f, p)]
        loads = r.get("loads") or {}
        guessed = None
        if not loads:
            cands = [f for f, p in pads if f.GetReference() not in srcrefs and f.GetReference()[0] in "UJ" and not f.GetReference().startswith("JP")]
            if not cands: cands = [f for f, p in pads if f.GetReference() not in srcrefs and not f.GetReference().startswith(("TP", "C", "R", "D"))]   # a pack board: the FETs and the leads
            refs = sorted({f.GetReference() for f in cands})
            loads = {ref: r["amps_typ"] / len(refs) for ref in refs} if refs else {}
            guessed = refs
            # 13 September 2026: A GUESSED LOAD IS NOT A MEASUREMENT, and this fallback was quietly deciding
            # boards. On 12 September CELL+ failed at 2.21 percent because it declared no loads and the guess
            # pushed 10 A through the charger's SENSE pin and its 0.20 mm escape; that rail was given its load
            # and the tool was left alone, so the same defect sat untouched in five more rails. It surfaced when
            # ruling 16 made the density a verdict: FIVE of the ten rails then failing declare no loads, and one
            # of them, A24's +12V_HF, reported its worst cell where the net has no copper within 3 mm, which is
            # what a current path invented between the wrong pads looks like.
            #
            # The fix is to the CLASS and not to the instance: a rail whose loads are undeclared is
            # INCONCLUSIVE. It still blocks, the way the seven silent passes of 11 September block, and the
            # line names what would have been guessed so the declaration can be written.
        sinks = {}
        for ref, amps in loads.items():
            ns = [n for f, p in pads if f.GetReference() == ref for n in pad_nodes(f, p)]
            for n in ns: sinks[n] = sinks.get(n, 0.0) + amps / len(ns)
        if not src or not sinks: results.append((net, "UNRESOLVED", "source %s pads %d, load pads %d" % ("+".join(srcrefs), len(src), len(sinks)), 0, 0, 0, {})); miss += 1; continue
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
                results.append((net, "MISSED", "%d of %d load pads on copper not connected to the source %s through this net's copper and vias (the mesh: %d pieces)" % (len(unreachable), len(sinks), "+".join(srcrefs), ncomp), 0, 1.0, 0, {})); miss += 1; continue
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
        worst_j = 0.0; worst = None; worst_l = None; share = {}
        zone_j = 0.0; zone_at = None; zone_l = None      # the cell measure restricted to copper that is NOT a track
        czone_j = 0.0; czone_at = None; czone_l = None   # the same, clear of every via: a plane cell that is not a funnel
        vzone_j = 0.0; vzone_at = None; vzone_l = None   # the worst cell that IS at a via, with that cell's barrels
        jmap = {L: np.zeros((ny, nx)) for L in cu_layers} if png else None   # the picture the usage line has promised since 8 September
        for (L, gy, gx), i in index.items():
            g0 = 1.0 / sheet(t_of(L)); t = t_of(L); f_i = frac[L][gy, gx] or 1.0
            for dy, dx in ((0, 1), (1, 0)):
                j = index.get((L, gy + dy, gx + dx))
                if j is None: continue
                g = g0 * min(f_i, frac[L][gy + dy, gx + dx] or 1.0)
                cur = abs(v[i] - v[j]) * g; jd = cur / (cell * t)   # A/mm2 through the cell face (width cell, thickness t)
                if jmap is not None:
                    jmap[L][gy, gx] = max(jmap[L][gy, gx], jd); jmap[L][gy + dy, gx + dx] = max(jmap[L][gy + dy, gx + dx], jd)
                share[lname[L]] = share.get(lname[L], 0.0) + cur
                if jd > worst_j: worst_j = jd; worst_l = L; worst = (lname[L], x0 + (gx + 0.5) * cell, y0 + (gy + 0.5) * cell, cur)
                # A face whose two cells are both off any track of this net is plane or pad copper, which is
                # where the raster converges (32.162). That is the only copper the cell measure now gates on.
                if not (trk_occ[L][gy, gx] or trk_occ[L][gy + dy, gx + dx]):
                    if jd > zone_j: zone_j = jd; zone_l = L; zone_at = (lname[L], x0 + (gx + 0.5) * cell, y0 + (gy + 0.5) * cell, cur)
                    # 13 September 2026: A PLANE CELL AT A VIA IS A FUNNEL, NOT A CONDUCTOR. Where a via
                    # injects a rail's current into a plane, the cell faces beside it carry the whole barrel
                    # current through one cell width, and IPC-2221's figure is for a long conductor at
                    # thermal steady state, not for a spreading region a millimetre across. The worst cell
                    # CLEAR of any via is measured beside it so the difference can be read rather than
                    # assumed, and the barrel itself is judged on its own cross-section below.
                    _at_via = (gy, gx) in via_cells or (gy + dy, gx + dx) in via_cells
                    if _at_via:
                        if jd > vzone_j: vzone_j = jd; vzone_l = L; vzone_at = (lname[L], x0 + (gx + 0.5) * cell, y0 + (gy + 0.5) * cell, cur, via_cells.get((gy, gx)) or via_cells.get((gy + dy, gx + dx)))
                    elif jd > czone_j:
                        czone_j = jd; czone_l = L; czone_at = (lname[L], x0 + (gx + 0.5) * cell, y0 + (gy + 0.5) * cell, cur)

        # ---- OWNER RULING 22: every TRACK judged on its own width, with no grid in the answer.
        # The mesh gives the potentials; a track's through-current is the largest face current along its
        # centreline, current being conserved along a series conductor. That current is compared with
        # IPC-2221 for the track's REAL cross-section, so the result does not move when the cell does.
        # 13 September 2026, THE CURRENT THIS PASS REPORTED COULD NOT BE TRUE. A24's +3V3, a rail given 0.3 A,
        # reported 22.27 A in a 0.250 mm track, and three more of A's rails reported a conductor carrying more
        # than the whole rail (+12V_HF 2.00 A of 1.0, +54V_POE 0.60 of 0.3, VBUS20 6.80 of 6.0). A series
        # conductor cannot carry more than is injected, so the number was not a measurement.
        #
        # The cause: it took `abs(v[nd] - v[prev]) * g` for consecutive cells ALONG THE CENTRELINE and a `g`
        # of its own construction. The mesh connects orthogonal neighbours only, and the cells a line steps
        # through are diagonal neighbours wherever the line is not axis-aligned, which is most tracks: that
        # potential difference is then taken across two hops or a longer path and multiplied by one cell's
        # conductance. The doubling is visible in the two rails that read exactly 2.0 times their own current.
        #
        # What replaces it is the mesh's OWN branch currents, which are conserved because they come from the
        # same conductances the system was solved with. At each cell the two branch currents to the x and y
        # neighbours make a current vector, and the through-current along the track is that vector projected
        # on the track's direction. It is exact for an axis-aligned track and correct for a diagonal one,
        # where the current really does split between the two edge directions.
        cond = []    # (ratio, width, amps, limit_amps, layer, x, y, length)
        short = []   # the same, for pieces too short to be a conductor: reported, never gated
        for L, ax, ay, bx, by, w, ln in net_tracks:
            if L not in occ or ln <= 0: continue
            t = t_of(L); g0 = 1.0 / sheet(t)
            ux, uy = (bx - ax) / ln, (by - ay) / ln
            steps = max(2, int(ln / cell) + 2)
            best = 0.0; at = None
            seen = set()
            for k in range(steps):
                u = k / (steps - 1)
                px, py = ax + u * (bx - ax), ay + u * (by - ay)
                gx, gy = int((px - x0) / cell), int((py - y0) / cell)
                if (gy, gx) in seen: continue
                seen.add((gy, gx))
                nd = index.get((L, gy, gx))
                if nd is None: continue
                # A track inside a filled pour of its OWN net is not a lone conductor: the pour is beside it
                # carrying the same current, and the pour is judged by the cell measure at those very cells.
                # Judging such a stretch on the track's own width counts the copper once and asks it to carry
                # everything. Only the stretches out in the open are judged here.
                if zone_occ[L][gy, gx]: continue
                f_i = frac[L][gy, gx] or 1.0
                comp = []
                for dy, dx in ((0, 1), (1, 0)):
                    j = index.get((L, gy + dy, gx + dx))
                    if j is None: comp.append(0.0); continue
                    ge = g0 * min(f_i, frac[L][gy + dy, gx + dx] or 1.0)
                    comp.append((v[nd] - v[j]) * ge)   # signed: +x and +y branch currents out of this cell
                cur = abs(comp[0] * ux + comp[1] * uy)
                if cur > best: best = cur; at = (px, py)
            if best <= 0 or at is None: continue
            lim_a = ipc_limit(w * t, dT_of(r), L not in (pcbnew.F_Cu, pcbnew.B_Cu))
            if lim_a <= 0: continue
            # A JOINT IS NOT A CONDUCTOR (13 September 2026). IPC-2221's curve is the steady-state rise of a
            # LONG trace, where the heat has nowhere to go sideways. A segment shorter than its own width is
            # a joint: the copper at both ends conducts its heat away and it cannot reach that rise at any
            # current. P3 was being failed on a 0.500 mm segment 0.0 mm long and D10 on one 0.1 mm long, both
            # of them a router's junction between two pieces that ARE judged. The bar is the larger of 1 mm
            # and twice the width, and every skipped piece is counted and the worst of them printed, so a
            # real neck hiding in a short segment shows up rather than disappearing.
            if ln < max(1.0, 2.0 * w):
                short.append((best / lim_a, w, best, lim_a, lname[L], at[0], at[1], ln)); continue
            cond.append((best / lim_a, w, best, lim_a, lname[L], at[0], at[1], ln))
        cond.sort(reverse=True); short.sort(reverse=True)
        # every barrel of this net on its own cross-section, the same question the conductor pass asks of a track
        via_worst = None
        for vx, vy, vd, vwall, vrv, vnodes in net_vias:
            cur = max((abs(v[vnodes[k]] - v[vnodes[k + 1]]) / vrv for k in range(len(vnodes) - 1)), default=0.0)
            lim = ipc_limit(vwall, dT_of(r), True)   # a barrel is enclosed copper: the inner-layer constant
            if lim <= 0: continue
            if via_worst is None or cur / lim > via_worst[0]: via_worst = (cur / lim, cur, lim, vd, vwall, vx, vy)
        tot = sum(share.values()) or 1.0; share = {k: round(x / tot, 2) for k, x in share.items()}
        amps = sum(sinks.values()); pct = drop / r["volts"] if r["volts"] else 0.0
        # FAIL CLOSED ON AN IMPOSSIBLE NUMBER. A series conductor cannot carry more current than the rail has:
        # if this pass says it does, the pass is wrong and the rail has not been measured. It is NOT judged,
        # the way a rail with no declared loads is not judged, because a verdict read off an impossible number
        # is worse than no verdict. This exists because four of A24's rails carried one for a day and the
        # tool reported them MISSED with a straight face.
        # A conductor cannot carry more than the rail is given, so the excess is clamped where it is small and
        # refused where it is not. A few percent is the discrete current vector at a bend or beside a pad,
        # where the two branch currents of one cell both project positively; with the centreline defect fixed
        # A24's worst two sit at 1.06 and 1.07 of their rail, and clamping them to the rail's own current
        # judges the copper at the most current that can possibly flow in it, which is the honest bar. An
        # excess of a quarter or more is the measure being wrong, and that is not judged at all.
        _clamped = [c for c in cond if c[2] > amps]
        if _clamped and cond[0][2] <= amps * 1.25:
            cond = sorted([( (min(c[2], amps) / c[3]) if c[3] else 0.0, c[1], min(c[2], amps), c[3], c[4], c[5], c[6], c[7]) for c in cond], reverse=True)
        if cond and cond[0][2] > amps * 1.25:
            results.append((net, "UNMEASURED",
                            "the conductor pass reports %.2f A in a %.3f mm track on %s while the whole rail is given "
                            "%.2f A, which is more than a quarter over. A series conductor cannot carry more than is "
                            "injected, so this is a defect in the measure and not a finding about the board: the rail "
                            "is NOT judged until it is fixed."
                            % (cond[0][2], cond[0][1], cond[0][4], amps), None, None, None, {}))
            miss += 1
            continue
        rb = float(r.get("budget", budget))   # a rail may carry its own budget in the intent (8 Sep 2026)
        # A RAIL THAT LEAVES THE BOARD IS JUDGED ON ITS SHARE (16 September 2026). `+5V_D8` is one conductor
        # from board A's eFuse through the mezzanine into board D's loads, and each board was measuring its own
        # half against the WHOLE budget: the two halves could sum past the rail's real budget with both boards
        # passing. Where the intent declares a share, that is this board's bar.
        if r.get("share"): rb = float(r["share"])
        # 8 September 2026 said the density "overstates by the cell-to-width ratio" and left it reported, not
        # gated, until the raster was validated. THE DIRECTION WAS BACKWARDS, measured 13 September 2026.
        # The bar is `ipc_limit(cell*t)` per cell and IPC's law is I = k dT^0.44 A^0.725, which is sublinear in
        # area, so N cells each at their own limit carry N^0.275 times what IPC allows the whole track. At a
        # 0.5 mm cell the per-cell bar is EXACT at 0.5 mm width and lenient everywhere else: +18 percent at
        # 0.4 mm, +65 at 0.25, +94 at 0.2, +21 at 1 mm, +64 at 3 mm, +98 at 6 mm. So a rail that exceeds this
        # bar exceeds a bar that is already too generous, and the exceedance is a floor, not a ceiling.
        # OWNER RULING 16, 13 September 2026 11:20: GATE IT. Twelve rails on three cut boards were over this
        # bar while every one of them read MET, because only the drop decided. A rail can be electrically quiet
        # and locally too hot at the same time, which is what a density check is for. Both now decide, and the
        # verdict names which of the two refused it so a reader is never left guessing.
        # A rail may declare its own rise with a reason in the intent file (`density_dT`), the way it may
        # already declare its own drop budget; the default is IPC's 10 K. A DECLARED rise is a design decision
        # with a written reason, which is not the same thing as ignoring the number.
        if guessed is not None:
            results.append((net, "UNDECLARED",
                            "the intent declares no loads for this rail, so its %.1f A has nowhere measured to go. "
                            "Neither the drop nor the density is judged. Guessing would have put the current into %s, "
                            "split evenly, which is how CELL+ came to read 2.21 percent through a 0.20 mm sense escape "
                            "on 12 September. Declare the loads in the schematic generator's intent and re-measure."
                            % (r.get("amps_typ", 0.0), ", ".join(guessed) if guessed else "nothing on the net"),
                            # None, never 0: a value that was explicitly NOT judged must not sit in the same
                            # slot as a measured one, or a later reader takes it for a measured zero.
                            None, None, None, {}))
            miss += 1
            continue
        dT = dT_of(r)
        jl = (ipc_limit(cell * t_of(zone_l), dT, zone_l not in (pcbnew.F_Cu, pcbnew.B_Cu)) / (cell * t_of(zone_l))) if zone_l is not None else 1e9

        # RULING 22's answer to ruling 20, and the tolerance is now measured rather than picked.
        #   TRACKS are judged on their own width, so there is NO grid error and NO tolerance: 1.00.
        #   ZONES keep the raster, because 32.162 measured that it converges there: the two rails carrying
        #   their current in planes and bands moved by +6 and -9 percent across a two-fold change of cell,
        #   where every track-carried rail moved by half. 1.10 is that measured sensitivity, rounded up.
        ZONE_TOL = 1.10
        cond_ratio = cond[0][0] if cond else 0.0
        # THE POUR BAR IS APPLIED TO POUR COPPER, AND A VIA IS JUDGED AS A VIA (13 September 2026). The cell
        # the current funnels through at a barrel is not a conductor cross-section, and the two boards where
        # this was measured say so in opposite directions: on all twelve of A24's rails the worst pour cell
        # is clear of every via, and on E7's VIN_RAW it IS a via, reading 2.20 while the barrel carrying that
        # current sits at 0.79 of its own limit and the worst cell clear of vias reads 1.21. So the gated
        # pour number is the worst cell CLEAR of every via, and every barrel is gated on its own wall
        # cross-section beside it. The funnel cell is still printed, because it is how a via with too little
        # copper around it shows up before the barrel itself is over.
        zone_ratio = (czone_j / jl) if czone_at else 0.0
        via_ratio = via_worst[0] if via_worst else 0.0
        drop_ok = pct <= rb
        # THE BARREL NUMBER IS REPORTED AND NOT GATED, and the measurement that decides this is the one
        # ruling 22 was built on. A barrel's current is read off the mesh as the branch current of a single
        # edge between two cells, and how much current chooses that edge depends on the conductance of the
        # cells around it, which is a function of the raster. Measured on P3's own board, one variable:
        # PACK_P's worst barrel reads 1.20 at a 0.50 mm cell and 1.71 at 0.25, and CELL4 goes MET to MISSED
        # across the same change. That is the per-cell density's defect in a new place, so it gets the same
        # answer: it does not decide a board until it is expressed with no grid in it.
        #
        # What it found before it was demoted is real and is fixed in the generators: P3 stitched a 10 A band
        # with THREE 0.4 mm barrels, which IPC gives 1.11 A each, and this project's rule of thumb of about
        # 2.5 A per 0.4 mm hole is more than twice that; E7's source pad had one. P3 now has eighteen 0.5 mm
        # barrels at the crossing and E7's pad has ten.
        dens_ok = cond_ratio <= 1.0 and zone_ratio <= ZONE_TOL
        verdict = "MET" if (drop_ok and dens_ok) else "MISSED"
        bad = ([] if drop_ok else ["the drop"]) + ([] if cond_ratio <= 1.0 else ["a track"]) + ([] if zone_ratio <= ZONE_TOL else ["a pour"])
        # WHICH criterion missed travels with the rail. Two rules read this tool: PI-002 is the voltage drop and
        # PI-001 is the conductor's current capacity, and they have different authorities and different
        # remedies. Board A read "MISSED VBAT 0.38% of 14.4 V" on 16 September, which looks like a voltage
        # failure and is a density one; a reader cannot act on that, and the rule with no verified source was
        # failing a board through the rule that has one.
        missed_on = {"drop": not drop_ok, "density": not dens_ok}
        why = "" if verdict == "MET" else " [MISSED on %s]" % " and ".join(bad)
        if cond:
            cr, cw, ca, cl, cL, cx, cy, cln = cond[0]
            cond_txt = ("worst CONDUCTOR %.3f mm wide on %s at (%.1f, %.1f), %.1f mm long: %.2f A against IPC's %.2f A "
                        "for its own cross-section at %.0f K, ratio %.2f" % (cw, cL, cx, cy, cln, ca, cl, dT, cr))
            # THE SECOND OPINION, WHERE THE BAR IS THE OPTIMISTIC ONE (16 September 2026, rule PI-001).
            # `ipc_limit` is the IPC-2221A internal-conductor model, published as a curve fit with its
            # constants in ECSS-Q-ST-70-12C Annex D (D.4; transcribed in v2/vendor/standards/). That document
            # also publishes the IPC-2152 fit which supersedes it, and the two cross: BELOW about 0.268 mm2 of
            # copper at 10 K the model here is the conservative one, and ABOVE it, which is every 2 oz pour
            # wider than 3.8 mm, it reads HIGHER than the modern standard. A rail on the wrong side of that
            # line gets the other two numbers printed beside it. It decides nothing: changing the bar changes
            # MET on boards that are already cut, and that is a decision with a number attached, not a patch.
            try:
                import track_current as _tcur
            except Exception:
                _tcur = None
            if _tcur is not None and cl > 0:
                # The conductor's own cross-section, recovered from the LIMIT rather than from the current:
                # `cl` is ipc_limit(area) for this piece, so area_for(cl) is that area back. Inverting the
                # current instead would answer a different question (the area the current would need).
                _a2 = _tcur.area_for(cl, dT, "IPC-2221A")
                if _a2 > _tcur.crossover(dT):
                    cond_txt += ("; SECOND OPINION: at %.3f mm2 this is past the %.3f mm2 where the IPC-2221A "
                                 "model stops being the conservative one, and the same copper rates %.2f A under "
                                 "IPC-2152 and %.2f A under CNES (ECSS-Q-ST-70-12C Annex D). Reported, not gated"
                                 % (_a2, _tcur.crossover(dT), _tcur.rating(_a2, dT, "IPC-2152"),
                                    _tcur.rating(_a2, dT, "CNES")))
        else:
            cond_txt = "no track of this net carries a measurable current, so the conductor test judged nothing"
        if short:
            cond_txt += ("; %d piece(s) shorter than a conductor were not judged, the worst %.3f mm wide and %.2f mm "
                         "long on %s at (%.1f, %.1f) carrying %.2f A against %.2f A"
                         % (len(short), short[0][1], short[0][7], short[0][4], short[0][5], short[0][6], short[0][2], short[0][3]))
        # The pour bar is IPC's current for ONE cell's cross-section, and it is LENIENT against the whole-track
        # figure because IPC is sublinear in area: 18 percent at 0.4 mm width, 21 at 1 mm, 64 at 3 mm, 98 at 6.
        # So a pour ratio over 1 is a floor on the exceedance, never a ceiling. The direction is written here
        # because it was recorded backwards for five days and a gate was built on the wrong sign.
        zone_txt = ("worst POUR cell %.1f A/mm2 at %s (%.1f, %.1f) against %.1f, ratio %.2f (raster, tolerance %.2f; "
                    "this per-cell bar is LENIENT against the whole-track IPC figure, so an exceedance is a floor)"
                    % (zone_j, zone_at[0], zone_at[1], zone_at[2], jl, zone_ratio, ZONE_TOL)) if zone_at else "this net has no pour copper"
        # DIAGNOSTIC, 13 September 2026, deciding nothing yet: is the worst pour cell a via's funnel? If it is,
        # the cell bar is being applied to a spreading region and the honest check at that point is the
        # BARREL's own cross-section. Both numbers are printed so the answer comes from boards and not from me.
        via_txt = (("worst VIA %.2f mm drill at (%.1f, %.1f): %.2f A against IPC's %.2f A for its own %.4f mm2 of "
                    "barrel wall, ratio %.2f (REPORTED, not gated: it moves with the raster)" % (via_worst[3], via_worst[5], via_worst[6], via_worst[1], via_worst[2],
                                                 via_worst[4], via_worst[0]))
                   if via_worst else "this net has no via")
        if vzone_at:
            _vl = ipc_limit(vzone_at[4][1], dT, True) if vzone_at[4] else 0.0
            zone_txt += ("; the worst cell AT A VIA is %.1f A/mm2 at %s (%.1f, %.1f), %d barrel(s) of %.4f mm2 wall "
                         "carrying %.2f A, which IPC gives %.2f A for its own cross-section, ratio %.2f"
                         % (vzone_j, vzone_at[0], vzone_at[1], vzone_at[2], vzone_at[4][0] if vzone_at[4] else 0,
                            vzone_at[4][1] if vzone_at[4] else 0.0, vzone_at[3], _vl, (vzone_at[3] / _vl) if _vl else 0.0))
        zone_txt += ("; GATED on the worst pour cell clear of every via, %.1f A/mm2 at %s (%.1f, %.1f), ratio %.2f"
                     % (czone_j, czone_at[0], czone_at[1], czone_at[2], czone_j / jl)) if czone_at else "; no pour cell of this net is clear of a via, so the pour is not gated"
        if verdict != "MET": miss += 1
        _MISSED_ON[net] = missed_on
        # THE BAR IS PRINTED AS IT IS JUDGED (16 September 2026). "%.0f" rounded board A's 1.5 percent share to
        # "budget 2%", which reads as the whole rail's budget and hides the very split the share exists to make;
        # board C's 0.75 would have printed as 1. The value is right and was always right; the line about it was
        # not, and a line nobody can check against the number it claims is how a wrong bar survives.
        results.append((net, verdict, "raster %s; %.1f A over %d nodes: worst drop %.0f mV (%.2f%% of %.1f V, bar %.3g%%); %s; %s; %s%s; layer share %s"
                        % ("; ".join(raster_note[:4]) or "-", amps, N, drop * 1e3, pct * 100, r["volts"], rb * 100, cond_txt, zone_txt, via_txt, why, share),
                        drop, pct, max(cond_ratio, zone_ratio), share))
        if png:
            marks = []
            if cond: marks.append(("worst conductor %.2f A in %.3f mm on %s (ratio %.2f)" % (cond[0][2], cond[0][1], cond[0][4], cond[0][0]), cond[0][4], cond[0][5], cond[0][6], "o"))
            if czone_at: marks.append(("worst pour cell clear of a via %.0f A/mm2 (ratio %.2f)" % (czone_j, czone_j / jl), czone_at[0], czone_at[1], czone_at[2], "s"))
            if via_worst: marks.append(("worst via %.2f A of %.2f (ratio %.2f)" % (via_worst[1], via_worst[2], via_worst[0]), None, via_worst[5], via_worst[6], "^"))
            _draw(png, net, jmap, occ, lname, cu_layers, x0, y0, cell, nx, ny, jl, marks, amps, verdict)
    if not results:
        print("dc_drop: FAIL no rail to check (the intent file lists none)")
        return _v.write("dc_drop", _v.INCONCLUSIVE, denominator=0, inputs={"board": a[0]},
                        note="the intent file lists no rail, so no drop was computed")
    for net, v, text, *_ in results: print("dc_drop: %-11s %-10s %s" % (v, net, text))
    undecl = [r[0] for r in results if r[1] in ("UNDECLARED", "UNMEASURED")]
    print("dc_drop: %d of %d rails MET (cell %.2f mm, default budget %.3g%%; a rail with a declared share is "
          "judged against THAT)%s"
          % (len(results) - miss, len(results), cell, budget * 100,
             ("; %d rail(s) NOT JUDGED (a declared load is missing, or the measure returned an impossible current): %s" % (len(undecl), ", ".join(undecl)) if undecl else "")
))
    if "--json" in a: json.dump([dict(net=r[0], verdict=r[1], text=r[2], drop_v=r[3], pct=r[4], j_max=r[5], share=r[6]) for r in results], open(a[a.index("--json") + 1], "w"), indent=1)
    # A rail nobody declared a load for is INCONCLUSIVE, never FAIL: the board is not refused for a property of
    # the board, it is refused for a property of the intent file, and the two have different remedies.
    # TWO CRITERIA, TWO VERDICTS. The voltage drop and the conductor's current capacity are different questions
    # with different authorities: the drop is judged against a budget this project sets for its own rails, and
    # the capacity against a current-capacity standard whose text this tree does not hold. Writing one verdict
    # for both meant a density miss failed the board through the drop rule, and a rule with no verified source
    # decided a board through a rule that has one. Each verdict now carries only the rails that missed ITS
    # criterion, and the registry maps PI-002 to the drop and PI-001 to the density.
    def _rows(kind):
        out = []
        for r in results:
            if r[1] == "MET": continue
            if r[1] in ("UNDECLARED", "UNMEASURED"): out.append(r); continue
            if (_MISSED_ON.get(r[0]) or {}).get(kind): out.append(r)
        return out

    def _evidence(rows, kind):
        """EACH VERDICT'S EVIDENCE IS THE NUMBER THAT DECIDED IT (16 September 2026, rule PI-001).

        Both lists used to print the voltage drop, so board A's four current-density misses read "MISSED VBAT
        on current density: 0.38% of 14.4 V", which is a voltage figure beside the word density and the
        opposite of a diagnosis: 0.38 percent of 14.4 V is a PASS of the drop criterion. The density verdict
        prints the ratio against the published bar, which is what its rows failed."""
        out = []
        for r in rows:
            if r[4] is None: out.append("%s %s NOT JUDGED" % (r[1], r[0])); continue
            if kind == "current density":
                out.append("%s %s on current density: worst conductor or pour cell at %.2f of its limit "
                           "(the drop was %.2f%% of %.1f V, which is not what failed)"
                           % (r[1], r[0], r[5], r[4] * 100, rails[r[0]]["volts"]))
            else:
                out.append("%s %s on %s: %.2f%% of %.1f V" % (r[1], r[0], kind, r[4] * 100, rails[r[0]]["volts"]))
        return out

    dens_rows = _rows("density"); dens_undecl = [r for r in dens_rows if r[1] in ("UNDECLARED", "UNMEASURED")]
    dens_miss = len(dens_rows) - len(dens_undecl)
    _v.write("dc_density", _v.PASS if not dens_rows else (_v.INCONCLUSIVE if len(dens_undecl) == len(dens_rows) else _v.FAIL),
             counts={"met": len(results) - len(dens_rows), "missed": dens_miss, "undeclared": len(dens_undecl)},
             denominator=len(results), evidence=_evidence(dens_rows, "current density"),
             inputs={"board": a[0]},
             note="the conductor and pour current capacity at %.0f K, cell %.2f mm. THE LIMIT HAS A DOCUMENT since "
                  "16 September 2026: the internal-conductor model is IPC-2221A figure 6-4 curve C, published as a "
                  "curve fit with its constants in ECSS-Q-ST-70-12C Annex D (D.4), transcribed in "
                  "v2/vendor/standards/ and implemented and self-tested in tools/track_current.py. Two gaps are "
                  "named rather than hidden: the external factor of two is fitted nowhere in that annex, and above "
                  "0.268 mm2 of copper at 10 K this model reads HIGHER than the IPC-2152 fit that supersedes it, "
                  "so on the widest pours the bar is the optimistic one" % (dT, cell),
             quiet=True)

    drop_rows = _rows("drop"); drop_undecl = [r for r in drop_rows if r[1] in ("UNDECLARED", "UNMEASURED")]
    drop_miss = len(drop_rows) - len(drop_undecl)
    _verdict = _v.PASS if not drop_rows else (_v.INCONCLUSIVE if len(drop_undecl) == len(drop_rows) else _v.FAIL)
    return _v.write("dc_drop", _verdict,
                    counts={"met": len(results) - len(drop_rows), "missed": drop_miss, "undeclared": len(drop_undecl),
                            "density_missed": dens_miss},
                    denominator=len(results),
                    evidence=_evidence(drop_rows, "the voltage drop"),
                    inputs={"board": a[0]},
                    note="the voltage drop against each rail's budget (cell %.2f mm, default %.0f%%); the current "
                         "capacity is judged separately in dc_density.verdict.json, where %d rail(s) missed"
                         % (cell, budget * 100, dens_miss))

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
