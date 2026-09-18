#!/usr/bin/env python3
"""A barrel that carries more than its wall is rated for gets parallel barrels beside it (rule PI-003's fixer,
MESHSAT-862, 18 September 2026).

`via_current.py` judges every rail's barrels on the current `dc_drop.py`'s solved mesh puts through them, and on
the night it stopped being advisory it failed four boards for the same shape: ONE via at a layer transition
carrying two to four times what IPC-2221's curve allows a barrel of the fabricator's 18 um plating (board A's
VBUS20 3.40 A through a 0.90 A wall, board E's CELL_F 1.93 A through 0.74, board D's +5V_SA 1.10 through 0.90,
twenty-one on board B). The router lays one via per transition because one via is a connection; the current
does not care. The answer is the one every power-copper rule in this project already uses: barrels in parallel.

WHAT IT DOES. For every barrel the solved mesh puts over its own rating, it asks how many more of the same barrel
would bring each under (ceil(current / rating) - 1, capped), and lays them within two millimetres, each joined to
the original by a short locked link on EVERY copper layer the original's net touches at that barrel (a track end
on it, or a fill containing it), because a via that is not joined on both sides of the transition carries nothing.
A site must clear every other net's copper by the board's own minimum clearance on every layer (a through via
spans them all), keep hole-to-hole room from every via, and lie inside the outline. Then the finish's own
instruments decide: `drc.sh` and `hardset` before and after, any new via or link that appears in a hard
violation comes off with its partner pieces, and if hard or unrouted rose against the board it was handed,
EVERYTHING it laid comes off and the board is byte for byte what it was. Last it re-solves the mesh (dc_drop)
and re-judges (via_current), so the number it prints is a measurement and not a promise.

WHAT IT DOES NOT DO. It does not widen a via (the fabricator's rows are per drill and a class change is the
generator's), it does not move copper, and it does not touch a barrel whose current the mesh has not solved
(`via_current` stays advisory there and says so). A rail with no declared loads has no solved barrel current and
is left alone with that reason.

Usage: via_parallel.py <board.kicad_pcb> [--dry] [--rise-k 10] [--max-extra 6] [--no-resolve] [--reach 3.0]
  --reach R: search rings out to R mm for a parallel site (default 3.0; D12's +5V_SA barrel at (68.8, 82.0) has no site
  within 3 mm and a barrel 4 to 6 mm away on the same net, linked on both layers, still shares the transition)
  exit 0 laid or nothing to do, 1 reverted (HURT), 3 no solved currents to work from."""
import sys, os, math, json, shutil, subprocess
TOOLS = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, TOOLS)
import pcbnew
import hardset, kicad_compat as _kc
import return_via as _rv
import via_current as _vc
import boardtable as _bt

RINGS = (0.9, 1.1, 1.3, 1.6, 2.0, 2.5, 3.0)
ROUNDS = 5             # solve, lay, judge, and again on what is still over: a chain of barrels moves the worst one along
DIRS = 16
FIELD = 6              # a barrel with this many vias of its net within 2 mm sits in a field: adding one more moves the worst along (E12, 39 vias in five rounds)
HOLE_TO_HOLE = 0.30      # centre to centre room this project's finish keeps between drilled holes (stub router's own rule)
mm = lambda v: v / 1e6


def _resolve(path):
    """Run dc_drop so the barrel currents beside the board are about THIS board."""
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "dc_drop.py"), path], capture_output=True, text=True,
                       cwd=os.path.dirname(os.path.abspath(path)))
    return r.returncode, (r.stdout + r.stderr)


def _currents(path):
    p = os.path.join(os.path.dirname(os.path.abspath(path)), "out",
                     os.path.splitext(os.path.basename(path))[0] + "-via-currents.json")
    if not os.path.exists(p): return None
    try: return json.load(open(p, encoding="utf-8")).get("nets") or {}
    except Exception: return None


def _measure(path):
    od = os.path.join(os.path.dirname(os.path.abspath(path)), "out"); os.makedirs(od, exist_ok=True)
    rep = os.path.join(od, os.path.basename(os.path.splitext(path)[0]) + "-via_parallel-drc.json")
    subprocess.run([os.path.join(TOOLS, "drc.sh"), path, rep], capture_output=True, text=True)
    d = hardset.load(rep); c = hardset.counts(d)
    return c["hard"], c["unrouted"], d


def _hit_positions(d, tol=0.02):
    """Every (x, y) in mm named by a hard violation of the report."""
    pts = []
    for v in d.get("violations", []):
        if v.get("type") not in hardset.HARD_POST: continue
        for i in v.get("items", []):
            p = i.get("pos") or {}
            if "x" in p and "y" in p: pts.append((float(p["x"]), float(p["y"])))
    return pts


def _layers_at(b, net, x, y, cu):
    """The copper layers on which `net` has copper touching the point: a track end within 0.05 mm, or a filled
    zone containing it. A via joined on fewer than two of them is not a transition."""
    P = pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)); out = {}
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK" or t.GetNetname() != net: continue
        for e in (t.GetStart(), t.GetEnd()):
            if math.hypot(e.x - P.x, e.y - P.y) <= 0.05e6:
                out[t.GetLayer()] = max(out.get(t.GetLayer(), 0), t.GetWidth())
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != net: continue
        for L in z.GetLayerSet().Seq():
            if L not in cu: continue
            try:
                if z.GetFilledPolysList(L).Contains(P): out.setdefault(L, 0)
            except Exception: pass
    return out


def _link_clear(b, net, ax, ay, cx, cy, w, clr, layer):
    """Every point along the link from the barrel to the site keeps the clearance from other nets' copper ON THAT
    LAYER, tracks by segment distance and pads by bounding box; a link laid across another net's track is a
    crossing the DRC refuses (D12's second barrel lost its via to that three rounds running, 18 September 2026)."""
    n = max(2, int(math.hypot(cx - ax, cy - ay) / 0.2) + 1)
    need = (w / 2 + clr) * 1e6
    for k in range(n + 1):
        X = (ax + (cx - ax) * k / n) * 1e6; Y = (ay + (cy - ay) * k / n) * 1e6
        for t in b.GetTracks():
            if t.GetNetname() == net or t.GetClass() != "PCB_TRACK" or t.GetLayer() != layer: continue
            sx, sy, ex, ey = t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y
            L2 = (ex - sx) ** 2 + (ey - sy) ** 2
            u = 0.0 if L2 == 0 else max(0.0, min(1.0, ((X - sx) * (ex - sx) + (Y - sy) * (ey - sy)) / L2))
            if math.hypot(X - (sx + u * (ex - sx)), Y - (sy + u * (ey - sy))) < need + t.GetWidth() / 2.0: return False
        for fp in b.GetFootprints():
            for pd in fp.Pads():
                if pd.GetNetname() == net or pd.GetNumber() == "" or not pd.IsOnLayer(layer): continue
                bb = pd.GetBoundingBox(); c = bb.GetCenter()
                dx = max(0.0, abs(X - c.x) - bb.GetWidth() / 2.0); dy = max(0.0, abs(Y - c.y) - bb.GetHeight() / 2.0)
                if math.hypot(dx, dy) < need: return False
    return True


def _in_own_fill(b, net, x, y, layer):
    P = pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6))
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != net or layer not in z.GetLayerSet().Seq(): continue
        try:
            if z.GetFilledPolysList(layer).Contains(P): return True
        except Exception: pass
    return False


def _worst(cur, rise, plating):
    """The worst barrel ratio over every solved rail, and the net it is on: the number a round must not raise."""
    w = (0.0, None)
    for net, rows in (cur or {}).items():
        for r in rows:
            drill = float(r.get("drill_mm") or 0); amps = float(r.get("amps") or 0)
            lim = _vc.ampacity(drill, rise, plating)[0] if drill > 0 else 0.0
            if lim > 0 and amps / lim > w[0]: w = (amps / lim, net)
    return w


def _field(b, net, x, y, reach=2.0):
    """How many vias of the net already sit within reach of the barrel: a field is the generator's answer, not this one's."""
    return sum(1 for t in b.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetname() == net
               and math.hypot(mm(t.GetPosition().x) - x, mm(t.GetPosition().y) - y) <= reach)


def _inside(b, x, y, margin):
    bb = b.GetBoardEdgesBoundingBox()
    X, Y, M = x * 1e6, y * 1e6, margin * 1e6
    return bb.GetLeft() + M < X < bb.GetRight() - M and bb.GetTop() + M < Y < bb.GetBottom() - M


def main(a):
    if not a: print(__doc__); return 2
    path = a[0]; dry = "--dry" in a
    rise = float(a[a.index("--rise-k") + 1]) if "--rise-k" in a else 10.0
    max_extra = int(a[a.index("--max-extra") + 1]) if "--max-extra" in a else 6
    if "--reach" in a:
        global RINGS
        reach = float(a[a.index("--reach") + 1])
        RINGS = tuple(list(RINGS) + [x / 10.0 for x in range(35, int(round(reach * 10)) + 1, 5) if x / 10.0 > RINGS[-1]])
    if dry:
        tmp = os.path.splitext(path)[0] + "-via_parallel-dry.kicad_pcb"; shutil.copy(path, tmp)
        for e in (".kicad_pro", ".kicad_prl"):
            if os.path.exists(os.path.splitext(path)[0] + e): shutil.copy(os.path.splitext(path)[0] + e, os.path.splitext(tmp)[0] + e)
        # the intent file is found by the board's stem, so the dry copy needs one under its own stem
        _od = os.path.join(os.path.dirname(os.path.abspath(path)), "out")
        _it = os.path.join(_od, os.path.splitext(os.path.basename(path))[0] + "-intent.json")
        if os.path.exists(_it): shutil.copy(_it, os.path.join(_od, os.path.splitext(os.path.basename(tmp))[0] + "-intent.json"))
        path = tmp; print("via_parallel: dry run on %s" % tmp)
    if "--no-resolve" not in a:
        rc, out = _resolve(path)
        if _currents(path) is None:
            print("via_parallel: dc_drop left no barrel currents beside this board (%s); nothing to work from" % out.strip().split("\n")[-1][:120])
            return 3
    cur = _currents(path)
    if cur is None:
        print("via_parallel: no solved barrel currents beside this board (out/<stem>-via-currents.json); run dc_drop first"); return 3
    letter = _bt.letter_for(path)
    plating = float(_bt.value(letter, "via_plating_um", _vc.PLATING_UM))
    b = pcbnew.LoadBoard(path); ds = b.GetDesignSettings()
    clr = max(mm(ds.m_MinClearance), 0.20)   # 0.20: room for the solder-mask web too, which the first D12 dry run bridged three times
    cu = list(b.GetEnabledLayers().CuStack())
    refused_sites = set(); total_kept = 0; rounds_run = 0
    worst_before = _worst(cur, rise, plating)
    for rnd in range(1, ROUNDS + 1):
        rounds_run = rnd
        if rnd > 1:
            b = pcbnew.LoadBoard(path)
        # THE ROUND IS A TRIAL AGAINST THE JUDGE'S OWN NUMBER (18 September 2026, E12): five rounds laid 39 vias in
        # VIN_RAW's transition field, each round chasing the barrel the mesh moved its current to, and the rail
        # ended with 4.86 A through one barrel where it began with 3.36. A round that raises the set's worst ratio
        # is put back and the pass stops there.
        round_bak = path + ".via_parallel.round"; shutil.copy(path, round_bak)
        # the barrels over their rating, and how many more each wants
        todo = []
        for net, rows in cur.items():
            for r in rows:
                drill = float(r.get("drill_mm") or 0); amps = float(r.get("amps") or 0)
                lim = _vc.ampacity(drill, rise, plating)[0] if drill > 0 else 0.0
                if lim <= 0 or amps <= lim: continue
                extra = min(max_extra, int(math.ceil(amps / lim)) - 1)
                todo.append((net, float(r["x"]), float(r["y"]), drill, amps, lim, extra))
        if not todo:
            if rnd == 1: print("via_parallel: every solved barrel is inside its rating at %.0f K; nothing to lay" % rise); return 0
            print("via_parallel: round %d: every solved barrel is inside its rating now" % rnd); break
        print("via_parallel: round %d: %d barrel(s) over their rating at %.0f K (%.0f um plating)" % (rnd, len(todo), rise, plating))
        if rnd == 1:
            keep = path + ".via_parallel.bak"; shutil.copy(path, keep)
            h0, u0, _ = _measure(path)
        b = pcbnew.LoadBoard(path)
        laid = []      # (net, (bx, by), [(vx, vy)], n_links)
        refused = []
        all_new_vias = []
        for net, bx, by, drill, amps, lim, extra in todo:
            netname = net if b.FindNet(net) is not None else ("/" + net if b.FindNet("/" + net) is not None else None)
            if netname is None:
                refused.append("%s at (%.1f, %.1f): the board has no such net" % (net, bx, by)); continue
            netobj = b.FindNet(netname)
            # the original barrel, for its diameter
            orig = None
            for t in b.GetTracks():
                if t.GetClass() == "PCB_VIA" and t.GetNetname() == netname and math.hypot(mm(t.GetPosition().x) - bx, mm(t.GetPosition().y) - by) < 0.05:
                    orig = t; break
            if orig is None:
                refused.append("%s at (%.1f, %.1f): no via of that net there any more" % (net, bx, by)); continue
            _nf = _field(b, netname, bx, by)
            if _nf >= FIELD:
                refused.append("%s at (%.1f, %.1f): already in a field of %d vias of its net within 2 mm; one more moves the worst along, a wider via or a generator field answers it" % (net, bx, by, _nf)); continue
            vd0 = mm(_kc.via_width(orig)); vdr0 = mm(orig.GetDrill())
            # THE SAME BARREL FIRST, THE BOARD'S SMALLEST SECOND (18 September 2026): D12's second +5V_SA barrel is a
            # 0.80 mm via with no free site for another within 3 mm, where a 0.40/0.20 via fits. A smaller barrel
            # carries less, so more of them are wanted: the current splits by wall conductance, which is the wall
            # area pi (d + t) t, so n small vias take n * r of the original's share, r = (d_s + t) t / (d + t) t, and
            # the original is inside its rating once 1 / (1 + n r) <= rating / current.
            _min_vd, _min_vdr = max(0.4, mm(ds.m_ViasMinSize)), max(0.2, mm(ds.m_MinThroughDrill))
            _sizes = [(vd0, vdr0, extra)]
            if _min_vd < vd0 - 1e-6:
                _t = plating / 1000.0
                _r = ((_min_vdr + _t) * _t) / ((vdr0 + _t) * _t)
                _n = int(math.ceil(((amps / lim) - 1.0) / _r)) if _r > 0 else max_extra
                _sizes.append((_min_vd, _min_vdr, min(max_extra, max(1, _n))))
            vd, vdr = vd0, vdr0
            layers = _layers_at(b, netname, bx, by, cu)
            if len(layers) < 2:
                refused.append("%s at (%.1f, %.1f): the net touches this barrel on %d layer(s), so which transition it carries is not readable"
                               % (net, bx, by, len(layers))); continue
            sites = []
            cands = [(round(bx + r * math.cos(k * 2 * math.pi / DIRS), 3), round(by + r * math.sin(k * 2 * math.pi / DIRS), 3))
                     for r in RINGS for k in range(DIRS)]
            taken = [(bx, by)] + [p for _, _, ps, _ in laid for p in ps]
            for vd, vdr, extra in _sizes:
              if sites: break
              for c in cands:
                if len(sites) >= extra: break
                if c in refused_sites: continue
                if not _inside(b, c[0], c[1], vd / 2 + clr + 0.3): continue
                if any(math.hypot(c[0] - q[0], c[1] - q[1]) < vd + HOLE_TO_HOLE for q in taken + sites): continue
                if not _rv._site_free(b, c[0], c[1], vd, clr, netname): continue
                # every link must have a clean run on its layer, and on a fill-only layer the site must sit in the
                # net's own fill, or the via joins nothing there and the link crosses another net's pour
                _ok = True
                for L, w in layers.items():
                    _w = mm(int(w)) if w else min(0.5, vd)
                    if not _link_clear(b, netname, bx, by, c[0], c[1], _w, clr, L): _ok = False; break
                    if not w and not _in_own_fill(b, netname, c[0], c[1], L): _ok = False; break
                if not _ok: continue
                # hole-to-hole room from every other via and drilled pad
                ok = True
                for t in b.GetTracks():
                    if t.GetClass() == "PCB_VIA" and math.hypot(mm(t.GetPosition().x) - c[0], mm(t.GetPosition().y) - c[1]) < vd / 2 + mm(_kc.via_width(t)) / 2 + HOLE_TO_HOLE:
                        ok = False; break
                if not ok: continue
                sites.append(c)
            if not sites:
                refused.append("%s at (%.1f, %.1f): no free site within %.1f mm for a %.2f mm via" % (net, bx, by, RINGS[-1], vd)); continue
            nlinks = 0
            for c in sites:
                v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(int(c[0] * 1e6), int(c[1] * 1e6)))
                v.SetDrill(int(vdr * 1e6)); v.SetWidth(int(vd * 1e6)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetNet(netobj); v.SetLocked(True)
                b.Add(v); all_new_vias.append(c)
                for L, w in layers.items():
                    t = pcbnew.PCB_TRACK(b); t.SetLayer(L); t.SetWidth(int(w) if w else int(min(0.5, vd) * 1e6))
                    t.SetStart(pcbnew.VECTOR2I(int(bx * 1e6), int(by * 1e6))); t.SetEnd(pcbnew.VECTOR2I(int(c[0] * 1e6), int(c[1] * 1e6)))
                    t.SetNet(netobj); t.SetLocked(True); b.Add(t); nlinks += 1
            laid.append((net, (bx, by), sites, nlinks))
            print("via_parallel: %s at (%.1f, %.1f) carried %.2f A against %.2f: %d parallel via(s) of %d wanted, joined on %s"
                  % (net, bx, by, amps, lim, len(sites), extra, ", ".join(b.GetLayerName(L) for L in sorted(layers))))
        if not laid:
            for r in refused[:12]: print("via_parallel:   %s" % r)
            if os.path.exists(round_bak): os.remove(round_bak)
            if rnd == 1: os.remove(keep); print("via_parallel: nothing laid"); return 0
            break
        pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(path, b)
        # the DRC decides which of the new pieces may stay
        h, u, d = _measure(path)
        hits = _hit_positions(d)
        # WHICH NEW PIECE A VIOLATION IS ABOUT. KiCad reports a track item at its START, which for every link here is
        # the ORIGINAL barrel's centre, and a via at its centre; so a hit at a new via names that via, a hit on a link's
        # run names that via, and a hit at the barrel centre cannot name one link over another and takes every new
        # via of that barrel (the first dry runs on D12 and E11 reverted whole because the hits sat on the links and
        # nothing matched a via centre, 18 September 2026).
        def _seg_dist(px, py, ax, ay, bx_, by_):
            L2 = (bx_ - ax) ** 2 + (by_ - ay) ** 2
            u = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * (bx_ - ax) + (py - ay) * (by_ - ay)) / L2))
            return math.hypot(px - (ax + u * (bx_ - ax)), py - (ay + u * (by_ - ay)))
        bad = set(); types = {}
        for v_ in d.get("violations", []):
            if v_.get("type") in hardset.HARD_POST: types[v_["type"]] = types.get(v_["type"], 0) + 1
        for net, (bx, by), ps, _ in laid:
            for c in ps:
                for hx, hy in hits:
                    if math.hypot(c[0] - hx, c[1] - hy) <= 0.02 or math.hypot(bx - hx, by - hy) <= 0.02 \
                            or _seg_dist(hx, hy, bx, by, c[0], c[1]) <= 0.3:
                        bad.add(c); break
        if types: print("via_parallel: the DRC after laying reads %s" % ", ".join("%s %d" % kv for kv in sorted(types.items())))
        if bad:
            b = pcbnew.LoadBoard(path)
            for t in list(b.GetTracks()):
                if not t.IsLocked(): continue
                if t.GetClass() == "PCB_VIA":
                    c = (round(mm(t.GetPosition().x), 3), round(mm(t.GetPosition().y), 3))
                    if c in bad: b.Remove(t)
                else:
                    e = (round(mm(t.GetEnd().x), 3), round(mm(t.GetEnd().y), 3))
                    if e in bad: b.Remove(t)
            pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(path, b)
            refused_sites |= bad
            print("via_parallel: round %d: %d new via(s) sat in a hard violation and came off with their links" % (rnd, len(bad)))
            h, u, d = _measure(path)
        if h > h0 or u > u0:
            print("via_parallel: HURT (hard %d -> %d, unrouted %d -> %d): reverting every via and link" % (h0, h, u0, u))
            shutil.copy(keep, path); os.remove(keep)
            if os.path.exists(round_bak): os.remove(round_bak)
            return 1
        kept = sum(len([c for c in ps if c not in bad]) for _, _, ps, _ in laid)
        for r in refused[:12]: print("via_parallel:   %s" % r)
        if kept == 0:
            if os.path.exists(round_bak): os.remove(round_bak)
            print("via_parallel: round %d: nothing kept" % rnd); break
        _resolve(path); cur = _currents(path) or {}
        worst_after = _worst(cur, rise, plating)
        if worst_after[0] > worst_before[0] + 1e-6:
            shutil.copy(round_bak, path); os.remove(round_bak)
            print("via_parallel: round %d: %d via(s) laid and the worst barrel went %.2f (%s) -> %.2f (%s): the round is put back and the pass stops"
                  % (rnd, kept, worst_before[0], worst_before[1], worst_after[0], worst_after[1]))
            _resolve(path); break
        os.remove(round_bak); total_kept += kept
        print("via_parallel: round %d: kept %d parallel via(s) at %d barrel(s) (hard %d -> %d, unrouted %d -> %d), worst barrel %.2f -> %.2f"
              % (rnd, kept, len(laid), h0, h, u0, u, worst_before[0], worst_after[0]))
        worst_before = worst_after
    if os.path.exists(path + ".via_parallel.bak"): os.remove(path + ".via_parallel.bak")
    print("via_parallel: %d parallel via(s) kept over %d round(s)" % (total_kept, rounds_run))

    if "--no-resolve" not in a:
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "via_current.py"), path, "--rise-k", str(rise)],
                           capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(path)))
        for l in (r.stdout + r.stderr).split("\n"):
            if l.startswith("via_current:") or l.startswith("  FAIL"): print("via_parallel: after: " + l)
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
