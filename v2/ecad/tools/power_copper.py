#!/usr/bin/env python3
"""The power-copper rule as generator code (MESHSAT-862 rule 3 of appendix 32.67, 8 Sep 2026): rail current never travels in router tracks.
A21 proved the pattern by hand (appendix 32.39: output islands, bottom-side bands with a track keep-out, stitch vias, In2 feed columns), the
A22 generator dropped it and dc_drop.py measured the cost (32.66: 5 to 13 percent drops in 0.4 mm inner-layer tracks). This module is that
pattern as functions for every placement generator; the geometry per rail stays in the generator (it knows the positions), the judge is
dc_drop.py on the filled routed board, and copper_checks.py gates the pieces and the stitch vias.

  PowerCopper(board, net_for, P)          P maps case-frame (x, y) mm to the board frame like the generators' P()
  .band(net, name, rect, layers, priority, keepout=True, min_width=0.5)     a locked pour rectangle per layer (case frame), with a track keep-out
                                                                            (vias allowed) on each band layer so the router cannot slice it
  .island(net, name, pts, layer, priority)                                  a polygon pour (case frame) for a converter output
  .spine(net, x0, y0, x1, y1, w, layer)                                     a locked track inside a pour (the fill keeps its clearance from it)
  .stitch(net, pts, drill=0.4, width=0.8)                                   locked vias joining a rail's layers (about 2.5 A per 0.4 mm hole)
  .rail_run(net, name, a, b, width, layers, vias_per_end=3, priority=2)     a straight band from point a to point b (case frame), stitched at both ends
  .width_for(amps, layer_oz=1.0, dT=10)                                     the IPC-2221 outer-layer width in mm for amps at dT (0.5 oz inner: pass 0.5)
Coordinates: case frame mm (x right, y up), as the generators' FIXED tables; rectangles (x0, y0, x1, y1) with y0 < y1."""
import math, pcbnew
from pcbnew import VECTOR2I, FromMM

def width_for(amps, oz=1.0, dT=10.0, internal=False):
    """IPC-2221: I = k dT^0.44 A^0.725 (A in mil2, k 0.048 outer, 0.024 inner) solved for the width at the copper thickness."""
    k = 0.024 if internal else 0.048; a_mil2 = (amps / (k * dT ** 0.44)) ** (1 / 0.725); a_mm2 = a_mil2 * 0.0254 ** 2
    return a_mm2 / (0.035 * oz)

class PowerCopper:
    placed_by = []          # every barrel this RUN placed, with the line that placed it (class-wide, see __init__)
    def __init__(self, board, net_for, P):
        # `placed_by` IS THE CLASS'S AND NOT THE INSTANCE'S, because a generator builds several PowerCopper
        # objects in one run (board E makes one for its CELL_F cluster and another for the PI-003 sites) and
        # the sidecar is one file about one board. A per-instance list would record whichever object the
        # writer happened to be called on, which is the shape of half the defects in this record.
        self.b, self.net_for, self.P = board, net_for, P; self.made = []
    def _rect_outline(self, o, rect):
        x0, y0, x1, y1 = rect
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = self.P(x, y); o.Append(p.x, p.y)
    def band(self, net, name, rect, layers=(pcbnew.B_Cu,), priority=2, keepout=True, min_width=0.5, clearance=0.3):
        for L in layers:
            z = pcbnew.ZONE(self.b); z.SetLayer(L); z.SetNet(self.net_for(net, create=False)); z.SetZoneName("%s %s" % (name, self.b.GetLayerName(L)))
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); z.SetMinThickness(FromMM(min_width)); z.SetLocalClearance(FromMM(clearance))
            o = z.Outline(); o.NewOutline(); self._rect_outline(o, rect); z.SetAssignedPriority(priority); self.b.Add(z); self.made.append(z)
            if keepout: self.keepout("keep tracks off " + name, rect, L)
        return self
    def union(self, net, name, rects, layer=pcbnew.B_Cu, priority=2, keepout=True, min_width=0.5, clearance=0.3):
        """One pour from the union of rectangles (case frame): a band chain is one polygon, never abutting same-net zones with priorities (8 Sep 2026:
        abutting fills read as separate pieces to the judges, and a higher-priority band knocked the trunk in two). A track keep-out per rectangle."""
        u = pcbnew.SHAPE_POLY_SET()
        for rect in rects:
            r = pcbnew.SHAPE_POLY_SET(); r.NewOutline(); self._rect_outline(r, rect)
            try: u.BooleanAdd(r)                       # KiCad 9: no polygon-mode argument
            except TypeError: u.BooleanAdd(r, pcbnew.SHAPE_POLY_SET.PM_FAST)
        try: u.Simplify()
        except TypeError: u.Simplify(pcbnew.SHAPE_POLY_SET.PM_FAST)
        if u.OutlineCount() != 1: raise SystemExit("power copper: the rectangles of %s do not form one piece (%d outlines)" % (name, u.OutlineCount()))
        z = pcbnew.ZONE(self.b); z.SetLayer(layer); z.SetNet(self.net_for(net, create=False)); z.SetZoneName("%s %s" % (name, self.b.GetLayerName(layer)))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); z.SetMinThickness(FromMM(min_width)); z.SetLocalClearance(FromMM(clearance))
        o = z.Outline(); o.NewOutline(); src = u.Outline(0)
        for k in range(src.PointCount()): pt = src.CPoint(k); o.Append(pt.x, pt.y)
        z.SetAssignedPriority(priority); self.b.Add(z); self.made.append(z)
        if keepout:
            for rect in rects: self.keepout("keep tracks off " + name, rect, layer)
        return self
    def keepout(self, name, rect, layer):
        z = pcbnew.ZONE(self.b); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(False); z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
        z.SetLayer(layer); z.SetZoneName(name); o = z.Outline(); o.NewOutline(); self._rect_outline(o, rect); self.b.Add(z); return self
    def nopour(self, name, rect, layer):
        """A rule area that keeps every POUR off a rectangle on one layer and leaves tracks, vias and pads alone: where a
        plane would only thread a via fan (A33's VBAT plane between U2's escape vias, ratio 2.48) the rail is better
        carried by the outer band beside it, and the plane resumes past the fan (15 Sep 2026, MESHSAT-862)."""
        z = pcbnew.ZONE(self.b); z.SetIsRuleArea(True); z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(False); z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
        z.SetLayer(layer); z.SetZoneName(name); o = z.Outline(); o.NewOutline(); self._rect_outline(o, rect); self.b.Add(z); return self
    def island(self, net, name, pts, layer=pcbnew.F_Cu, priority=3, min_width=0.25, clearance=0.15):
        z = pcbnew.ZONE(self.b); z.SetLayer(layer); z.SetNet(self.net_for(net, create=False)); z.SetZoneName("%s %s" % (name, self.b.GetLayerName(layer)))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); z.SetMinThickness(FromMM(min_width)); z.SetLocalClearance(FromMM(clearance)); o = z.Outline(); o.NewOutline()
        for x, y in pts: p = self.P(x, y); o.Append(p.x, p.y)
        z.SetAssignedPriority(priority); self.b.Add(z); self.made.append(z); return self
    def spine(self, net, x0, y0, x1, y1, w=0.4, layer=pcbnew.F_Cu):
        t = pcbnew.PCB_TRACK(self.b); t.SetStart(self.P(x0, y0)); t.SetEnd(self.P(x1, y1)); t.SetWidth(FromMM(w)); t.SetLayer(layer); t.SetNet(self.net_for(net, create=False)); t.SetLocked(True); self.b.Add(t); return self
    def barrels_for(self, amps, drill, rise=10.0, plating=None):
        """The count that current needs, from the rule that judges it after the route (via_current.barrels_for)."""
        import sys as _s, os as _o
        _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
        import via_current as _vc
        return _vc.barrels_for(amps, drill, rise, plating if plating is not None else _vc.PLATING_UM)

    def write_provenance(self, board_path):
        """`out/<stem>-barrel-provenance.json` beside the board: every barrel this generator placed, with the
        line that placed it (20 September 2026).

        `barrel_sites --suggest` runs on a BOARD, long after the generator is gone, and its answer for a site
        the generator already owns is "add N points to the call that placed it". Without this it can only give
        a coordinate, and board E's thirteen such sites are a coordinate hunt through calls whose arguments are
        expressions. It is a SIDECAR and not evidence: nothing judges it, and its absence costs a reader the
        line and nothing else."""
        import json as _jsn, os as _osj
        # A TOOL THAT FINDS NOTHING SAYS SO. This returned None in silence and board E's first run then
        # looked exactly like a generator that had placed no barrels, which it had not: the only way to tell
        # the two apart was to add this line (20 September 2026).
        if not self.placed_by:
            print("power copper: no barrel was recorded with a source line, so no provenance is written "
                  "(stitch() places every barrel and records its caller; a run that placed none is normal)")
            return None
        stem = _osj.path.splitext(_osj.path.basename(board_path))[0]
        for suf in ("-placed", "-preroute", "-par-routed", "-cleaned"):
            if stem.endswith(suf): stem = stem[: -len(suf)]
        d = _osj.path.join(_osj.path.dirname(_osj.path.abspath(board_path)), "out")
        try:
            _osj.makedirs(d, exist_ok=True)
            p = _osj.path.join(d, stem + "-barrel-provenance.json")
            _jsn.dump({"barrels": self.placed_by}, open(p, "w", encoding="utf-8"), indent=1)
            print("power copper: %d barrel(s) recorded with the line that placed them -> %s"
                  % (len(self.placed_by), _osj.path.relpath(p, _osj.path.dirname(_osj.path.dirname(p)))))
            return p
        except Exception as e:
            print("power copper: the barrel provenance could not be written (%s)" % e); return None

    def stitch(self, net, pts, drill=0.4, width=0.8, amps=None):
        """`amps` is the current these points SHARE, and giving it makes the call self-checking.

        The points of one call are the barrels of one transition, so the count they supply is compared with the
        count that current needs and the generator REFUSES a board whose transition is short, naming the number.
        It is the same judgement `via_current` makes after the route, moved to where it can still be answered for
        free: before the board exists. Leave it out where one call places several unrelated clusters, because
        then the current is not one number and the check would be about nothing."""
        # THE HOLE-TO-HOLE FLOOR, checked here because the tool knows both numbers (18 September 2026). Raising
        # board E's block vias from 0.5 to 0.7 mm put its OTHER cluster, ten barrels on a 0.8 mm pitch, at 0.10 mm
        # hole to hole against the 0.2995 the board's own rules ask, and the placed board came back with eight
        # hole_to_hole violations. The DRC caught it, which is the point of the DRC, but a stitch call knows its
        # own pitch and its own drill and can say so before a board exists. Points from DIFFERENT calls are not
        # compared: a call is one cluster, and two clusters far apart are the normal case.
        _floor = drill + 0.2995
        for _i in range(len(pts)):
            for _j in range(_i + 1, len(pts)):
                _d = math.hypot(pts[_i][0] - pts[_j][0], pts[_i][1] - pts[_j][1])
                if _d < _floor - 1e-9:
                    raise SystemExit(
                        "power copper: %s stitches two %.2f mm barrels %.2f mm apart at (%.2f, %.2f) and "
                        "(%.2f, %.2f), which is %.2f mm hole to hole against the 0.2995 mm this project's "
                        "boards ask: widen the pitch or narrow the hole"
                        % (net, drill, _d, pts[_i][0], pts[_i][1], pts[_j][0], pts[_j][1], _d - drill))
        if amps is not None:
            need = self.barrels_for(amps, drill)
            if len(pts) < need:
                raise SystemExit(
                    "power copper: %s is given %d barrel(s) of %.2f mm for %.2f A and needs %d at a 10 K rise "
                    "(IPC-2221 for the fabricator's own plating, which is what via_current judges after the "
                    "route): add barrels, widen the hole, or say why in the board's own file"
                    % (net, len(pts), drill, float(amps), need))
        # A BARREL INSIDE ANOTHER NET'S PAD BECOMES THAT NET'S, SILENTLY (21 September 2026, board A's four rails).
        # KiCad's connectivity gives a via the net of the pad whose copper it touches, at the next fill or DRC,
        # with no message. Board A's slot runs each ended in a two-barrel column typed at xL + 1.0, which on the
        # placed board is 0.4 mm from the load capacitor's GROUND pad centre: the generator wrote +5V_S1, the
        # placed snapshot reads GND, the DRC is clean, place_audit says in passing that the island carries no via,
        # and the In3 run dead-ends a layer below the parts it was laid to feed. A89 routed that board as an arm
        # "with the three slot runs" and had no variable in it at the router, exactly D29's shape. So the tool
        # asks the question the DRC cannot: is this point on another net's copper pad. A barrel in a pad of ITS
        # OWN net is a via in pad and stays allowed (the fanout's fallback, named for the assembly note).
        _own = {str(net), "/" + str(net).lstrip("/")}
        for x, y in pts:
            _pos = self.P(x, y); _r = int(FromMM(width) / 2)
            for _fp in self.b.GetFootprints():
                for _pd in _fp.Pads():
                    if _pd.GetNetname() in _own or not _pd.IsOnCopperLayer(): continue
                    if _pd.HitTest(_pos, _r):
                        import os as _o
                        if _o.environ.get("POWER_COPPER_PAD_GUARD") == "report":
                            # A PROBE, NEVER A CHAIN SETTING: the first chain run of this guard stopped at the first
                            # of five sites, and a generator with thirty stitch calls is read in one pass this way.
                            print("power copper PAD GUARD (report): %s barrel at (%.2f, %.2f) on pad %s of %s, which carries %s"
                                  % (net, x, y, _pd.GetNumber(), _fp.GetReference(), _pd.GetNetname() or "no net")); continue
                        raise SystemExit(
                            "power copper: %s stitches a barrel at (%.2f, %.2f) on pad %s of %s, which carries %s: "
                            "KiCad gives a via the net of the pad it sits in, so this barrel would silently become "
                            "that net's and the run it ends would reach nothing; move the point onto %s's own copper"
                            % (net, x, y, _pd.GetNumber(), _fp.GetReference(), _pd.GetNetname() or "no net", net))
        # AND EVERY BARREL REMEMBERS THE LINE THAT PLACED IT (20 September 2026). `barrel_sites --suggest`
        # answers a site the generator already owns with "add N points to the call that placed it", and a
        # reader given a coordinate then has to find that call among lines whose arguments are expressions.
        # Board A's generator grew its own frame walk for this on 19 September and it works there and nowhere
        # else; board E has thirteen such sites and no equivalent, which is why they are still a coordinate
        # hunt. The caller is recorded HERE, once, for every board: the first frame outside this file, so a
        # helper like board A's `row`/`col` reports the generator's line and not its own.
        try:
            import sys as _sysp, os as _osp
            _f, _me = _sysp._getframe(1), _osp.path.abspath(__file__)
            while _f is not None and _osp.path.abspath(_f.f_code.co_filename) == _me: _f = _f.f_back
            _src = ("%s:%d" % (_osp.path.basename(_f.f_code.co_filename), _f.f_lineno)) if _f is not None else ""
        except Exception as _e:
            # A SILENT EXCEPT IS HOW A DAY PASSES. The first run of this recorded nothing and looked exactly
            # like a generator that had placed no barrels; the only way to tell was to say why (20 Sep 2026).
            _src = ""
            if not getattr(PowerCopper, "_src_warned", False):
                PowerCopper._src_warned = True
                print("power copper: the line that placed a barrel could not be read (%s), so the provenance "
                      "sidecar will be empty" % _e)
        for x, y in pts:
            v = pcbnew.PCB_VIA(self.b); v.SetPosition(self.P(x, y)); v.SetDrill(FromMM(drill)); v.SetWidth(FromMM(width)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetNet(self.net_for(net, create=False)); v.SetLocked(True); self.b.Add(v)
            if _src: self.placed_by.append(dict(net=str(net).lstrip("/"), at=[round(x, 2), round(y, 2)],
                                                drill=round(float(drill), 3), src=_src))
        return self
    def cluster(self, net, at, amps, drill=0.4, width=0.8, pitch=None, axis="x", skew=1.0):
        """The barrels one layer transition needs, placed for it (18 September 2026).

        `stitch(..., amps=)` refuses a transition that is short; this is the other half, for the case where the
        count is the only thing in question and the room is known to be there. The caller gives the point and
        the axis it may spread along, which it knows from `barrel_sites.py` (that report names every pad within
        reach of the site, its own net's and everyone else's); the count comes from the current and the drill.
        Centred on the point, so a site that already has one barrel there keeps the copper it has.

        Board A is why this exists: thirty-two sites over five rails, each a transition with one barrel where
        the mesh puts up to 3.4 A, and typing three coordinates apiece is how a table of ninety-six numbers gets
        one wrong. `pitch` defaults to the drill plus 0.4 mm, which keeps the 0.3 mm hole-to-hole floor of this
        project's own rule at every drill it uses.

        `skew` IS THE WORST BARREL'S SHARE DIVIDED BY AN EVEN ONE, and it defaults to 1.0, which is this
        method as it was (19 September 2026). Board E taught why it has to exist: the two barrels this method
        placed at CELL_F's fuse transition carry 1.198 A and 0.611 A on the solved mesh, so the site passes
        1.809 A and shares it about two to one, and a count taken from the TOTAL leaves the near barrel over
        its wall while the arithmetic says the pair is enough. With n barrels the worst one carries
        `amps * skew / n`, so the count that keeps it under the wall is `barrels_for(amps * skew)`. A caller
        passes a skew it has MEASURED on that site's own via currents, with the number in the board file
        beside the call; it is a model (it assumes the skew holds as the count grows) and the next reading on
        that site either confirms it or moves it. A skew under 1.0 is refused: the worst share cannot be
        smaller than the even one, so a number below it is a mistake rather than a generous declaration."""
        if float(skew) < 1.0:
            raise ValueError("cluster(%s): skew %.3f is below 1.0, and the worst barrel's share cannot be "
                             "smaller than an even one" % (net, float(skew)))
        n = self.barrels_for(float(amps) * float(skew), drill)
        pitch = pitch if pitch is not None else (drill + 0.4)
        x, y = at
        span = (n - 1) * pitch
        pts = [((x - span / 2.0 + i * pitch, y) if axis == "x" else (x, y - span / 2.0 + i * pitch)) for i in range(n)]
        self.stitch(net, pts, drill=drill, width=width)
        return pts

    def rail_run(self, net, name, a, b, width, layers=(pcbnew.B_Cu,), vias_per_end=3, priority=2, stitch_pitch=1.5):
        """A straight band along x or y from point a to point b (case frame), width mm, with stitch vias across the band at both ends."""
        (ax, ay), (bx, by) = a, b; h = width / 2
        if abs(bx - ax) >= abs(by - ay): rect = (min(ax, bx), ay - h, max(ax, bx), ay + h); ends = [(ax, ay), (bx, by)]; across = (0, 1)
        else: rect = (ax - h, min(ay, by), ax + h, max(ay, by)); ends = [(ax, ay), (bx, by)]; across = (1, 0)
        self.band(net, name, rect, layers, priority)
        for ex, ey in ends:
            pts = [(ex + across[0] * (k - (vias_per_end - 1) / 2) * stitch_pitch, ey + across[1] * (k - (vias_per_end - 1) / 2) * stitch_pitch) for k in range(vias_per_end)]
            self.stitch(net, pts)
        return self
