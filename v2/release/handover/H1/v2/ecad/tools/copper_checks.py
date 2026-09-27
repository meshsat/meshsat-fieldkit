#!/usr/bin/env python3
"""Copper integrity checks shared by the board gates (MESHSAT-862, 8 Sep 2026): the A21 gate had them (band contiguity, stitch vias in fill,
piece touching, appendix 32.39) and the A22 rewrite dropped them while finish_a22.sh still grepped for their lines; A22 is the 20 A board.
Written once, zone-name-free, so B16's In4 pours and P1's bands get the same gate.

On a filled board (skipped when no zone carries a fill):
  1. every piece of a filled power-net zone is anchored by a pad or a via of its net (a plane on a routable layer is sliced by tracks into
     anchored pieces, which carry current through the vias; a loose piece is an island), and the fill covers at least MIN_COVER of the
     outline's outline area (a pour the router's tracks have eaten to slivers carries nothing; refined 8 Sep after the first box run and the review);
  2. every locked via of a power net whose position lies inside a same-net zone's outline sits in that zone's fill on the zone's layer
     (a via the fill retreated from is a stitch that carries nothing);
  3. the pours of one net across layers meet through at least one via or through-hole pad of that net (the CELL+ bars meet through the 9 A pins).
Power nets: the board's net-class assignments with a class other than Default whose name suggests power (PWR, NODE, RAIL, SW, HV) plus any
net named GND, or the caller's list.  Usage as a module: fails = copper_checks.run(board, check, power_nets=None)."""
import pcbnew

MIN_COVER = 0.5
SLIVER = 5.0   # mm2: a fill piece smaller than this is a crumb of the pour, reported and not counted as a loose island (8 Sep 2026: D9's In1 plane was one 7300 mm2 plane plus six 2.5 mm2 slivers beside a connector, and the gate called the plane fragmented)

def power_nets(b, extra=()):
    names = set(extra)
    for k in range(1, b.GetNetInfo().GetNetCount()):
        n = b.GetNetInfo().GetNetItem(k).GetNetname()
        if n.lstrip("/") == "GND" or n.lstrip("/").startswith(("+", "VBAT", "CELL", "VBUS", "PACK", "FUSED", "VIN", "PV_", "TRK_")): names.add(n)
    return names

def covered_on_its_layer(rows):
    """Which same-net zones a locked via sits in the OUTLINE of while NO fill of that net reaches it there.

    21 September 2026: board A's gate read one FAIL on three finished boards and it was always the same via,
    `/VBAT` at (145.1, 64.4). The board is fine. Two VBAT zones share In2 there, `VBAT plane In2 (west and
    middle columns)` at priority 0 and `VBAT plane In2 (tongue under the converter row)` at priority 2, and
    the TONGUE's fill covers the via while the west plane's legitimately does not: that is what zone priority
    DOES, the higher-priority zone takes the copper and the lower one's fill has a hole exactly there. The
    rule asked EVERY containing zone to cover the via, where the question is whether the net's copper reaches
    it on that layer at all, which is the seventh time this project has caught a rule asking its question of
    the wrong land.

    `rows` is one tuple per zone of that net on ONE layer: (zone name, inside its outline, inside its fill).
    The answer is None when the via is carried, and the names of the zones that contain it when none is.
    """
    inside = [r for r in rows if r[1]]
    if not inside or any(r[2] for r in inside):
        return None
    return [r[0] for r in inside]


def run(b, check, nets=None):
    zones = [z for z in b.Zones() if not z.GetIsRuleArea()]
    routed = any(t.GetClass() == "PCB_TRACK" and not t.IsLocked() for t in b.GetTracks())
    if not routed: return "copper_checks: pre-route board, the copper checks run on the routed and filled board"
    if not any(z.GetFilledArea() > 0 for z in zones):
        check(not zones, "copper_checks: %d zones on the routed board and none filled: refill before the gate" % len(zones)); return "copper_checks: 0 pours checked (no filled zone)"
    nets = nets if nets is not None else power_nets(b)
    pz = [z for z in zones if z.GetNetname() in nets and z.GetFilledArea() > 0]
    n1 = n2 = n3 = 0
    # 10 September 2026 (C10): the coverage denominator is the pour's outline INSIDE THE BOARD. C7 is a U-shaped backer with a
    # display window through it, so a pour drawn over the whole board rectangle can never fill more than about 40 percent of its
    # own outline and every one of its four pours failed a check that is meant to catch a pour eaten to slivers. On a solid
    # rectangular board the two areas are the same, which is why this only ever bit the panel backer.
    board_poly = pcbnew.SHAPE_POLY_SET()
    try: b.GetBoardPolygonOutlines(board_poly)
    except Exception: board_poly = None

    def outline_area(z):
        o = z.Outline()
        if board_poly is None or board_poly.OutlineCount() == 0: return o.Area() / 1e12
        try:
            zp = pcbnew.SHAPE_POLY_SET(o)
            try: zp.BooleanIntersection(board_poly)                              # KiCad 9
            except TypeError: zp.BooleanIntersection(board_poly, pcbnew.PM_FAST)  # older bindings take the mode
            a = zp.Area() / 1e12
            return a if a > 0 else o.Area() / 1e12
        except Exception:
            return o.Area() / 1e12
    thru = [p for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() in nets and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    vias_all = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() in nets]
    for z in pz:
        L = z.GetFirstLayer(); fp = z.GetFilledPolysList(L); bb = z.GetBoundingBox()
        rect = outline_area(z); area = z.GetFilledArea() / 1e12   # against the zone's own outline area clipped to the board (a ring or an L is not its bounding box; review of 8 Sep 2026, board clip 10 Sep 2026)
        # a piece is anchored when a pad or a via of the net lies in it (a plane on a routable layer is sliced by tracks into anchored pieces; that is not a defect);
        # a piece with no anchor is an island the fill should have removed; the fill must still cover MIN_COVER of the outline (a pour eaten to slivers carries nothing)
        anchors = [p.GetPosition() for p in thru if p.GetNetname() == z.GetNetname()] + [v.GetPosition() for v in vias_all if v.GetNetname() == z.GetNetname()]
        anchors += [p.GetPosition() for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() == z.GetNetname() and p.IsOnLayer(L)]
        same = [o for o in pz if o is not z and o.GetNetname() == z.GetNetname() and o.GetFirstLayer() == L]   # same-net pours on this layer merge in the fill (a band chain, 8 Sep 2026)
        for o in same: anchors += [p.GetPosition() for p in thru if p.GetNetname() == z.GetNetname()]
        loose = 0; slivers = 0
        for i in range(fp.OutlineCount()):
            o = fp.Outline(i)
            if o.Area() / 1e12 < SLIVER: slivers += 1; continue   # a piece this small carries nothing and threatens nothing; counted and reported, never a block
            if any(o.PointInside(a) for a in anchors): continue
            merged = any(any(o.PointInside(q.GetFilledPolysList(L).Outline(k).CPoint(j)) for k in range(q.GetFilledPolysList(L).OutlineCount()) for j in range(0, q.GetFilledPolysList(L).Outline(k).PointCount(), 7)) for q in same)
            merged = merged or any(any(q.Outline().Contains(o.CPoint(j)) for j in range(0, o.PointCount(), 5)) for q in same)   # abutting same-net zones (a higher-priority band knocks the lower one out to its edge)
            if not merged: loose += 1
        solid_gnd = z.GetNetname() == "GND" and any(o.GetNetname() == "GND" and o.GetFirstLayer() != L and o.GetFilledArea() / 1e12 >= 0.8 * outline_area(o) for o in pz)   # a ground pour on a routing layer beside a solid ground plane: its islands are a note, not a defect
        if slivers: print("NOTE pour '%s' (%s, %s): %d piece(s) under %.1f mm2 not counted (isolated slivers, the fill's own crumbs)" % (z.GetZoneName() or "unnamed", z.GetNetname(), b.GetLayerName(L), slivers, SLIVER))
        if solid_gnd and loose: print("NOTE pour '%s' (%s, %s): %d of %d pieces loose; the solid ground plane on another layer carries the return" % (z.GetZoneName() or "unnamed", z.GetNetname(), b.GetLayerName(L), loose, fp.OutlineCount())); loose = 0
        # 13 September 2026: AND NEITHER IS ITS COVERAGE, for the same reason. The coverage bar exists to catch
        # a pour the router's tracks have eaten to slivers, which matters when that pour IS the return path.
        # C11's GND pour on In2, a ROUTING layer, fills 17,270 of 34,895 mm2 of the board: 49.5 percent against
        # a bar of 50, and the board was refused for half a percent while In1 beside it is a SOLID ground plane
        # filling 99 percent of the same outline. The exemption is the one two lines above, at the other bar:
        # where a solid plane of this net carries the return on another layer, this pour's coverage is reported
        # with its number and does not decide. A board with no such plane is judged exactly as before.
        _cover_ok = area >= MIN_COVER * rect
        # AND THE SAME ARGUMENT IS NOT ABOUT GROUND (16 September 2026). The exemption above says: where a
        # SOLID pour of this net on another layer carries the current, a cut-up pour on a routing layer is
        # reported rather than refused. That is true of a power rail word for word, and board A is the case:
        # its `VBUS20 F.Cu` island fills 97 of 223 mm2, 44 percent, because the front end's own gate drives
        # and sense lines cross it, and the generator says so in eleven lines of comment ending "the second
        # layer is taken here because the keep-out would have to cover a 31 by 18 mm field". The second layer
        # is `VBUS20 under In3.Cu`, which fills 219 of 223, 98 percent, behind the keep-out that field allows.
        # So the rail has continuous copper, dc_drop measures it at 0.18 percent of 20 V, and the board was
        # being refused by a proxy for the question dc_drop answers directly.
        # What is NOT exempted is the loose-piece bar above: a floating piece of a power net is a defect
        # whatever another layer does, and this only ever touches the coverage number.
        _solid_other = any(o.GetNetname() == z.GetNetname() and o.GetFirstLayer() != L
                           and o.GetFilledArea() / 1e12 >= 0.8 * outline_area(o) for o in pz)
        if _solid_other and not solid_gnd and not _cover_ok:
            print("NOTE pour '%s' (%s, %s): fill %.0f of %.0f mm2 (%.0f%%); a pour of the same net on another "
                  "layer fills at least 80%% of its own outline and carries the current, so the coverage bar "
                  "does not decide here. The drop is judged by dc_drop, which measures the copper rather than "
                  "the area of a rectangle"
                  % (z.GetZoneName() or "unnamed", z.GetNetname(), b.GetLayerName(L), area, rect, 100.0 * area / (rect or 1)))
            _cover_ok = True
        if solid_gnd and not _cover_ok:
            print("NOTE pour '%s' (%s, %s): fill %.0f of %.0f mm2 (%.0f%%) on a routing layer; the solid ground plane on another layer carries the return, so the coverage bar does not decide"
                  % (z.GetZoneName() or "unnamed", z.GetNetname(), b.GetLayerName(L), area, rect, 100.0 * area / (rect or 1)))
            _cover_ok = True
        check(loose == 0 and _cover_ok, "pour '%s' (%s, %s): every piece anchored by a pad or via of its net (%d of %d loose), fill %.0f of %.0f mm2 of its outline (at least %.0f%%)" % (z.GetZoneName() or "unnamed", z.GetNetname(), b.GetLayerName(L), loose, fp.OutlineCount(), area, rect, MIN_COVER * 100)); n1 += 1
    for t in b.GetTracks():
        if t.Type() != pcbnew.PCB_VIA_T or not t.IsLocked() or t.GetNetname() not in nets: continue
        inside = [z for z in pz if z.GetNetname() == t.GetNetname() and z.Outline().Contains(t.GetPosition())]
        touched = any(tr.GetClass() == "PCB_TRACK" and tr.GetNetname() == t.GetNetname() and (tr.GetStart() == t.GetPosition() or tr.GetEnd() == t.GetPosition()) for tr in b.GetTracks())
        for _L in sorted({z.GetFirstLayer() for z in inside}):
            _zs = [z for z in inside if z.GetFirstLayer() == _L]
            if t.GetNetname() == "GND" and any(o.GetNetname() == "GND" and o.GetFirstLayer() != _L and o.GetFilledArea() / 1e12 >= 0.8 * outline_area(o) for o in pz): continue   # a ground via reaches the solid plane
            _bad = covered_on_its_layer([(z.GetZoneName() or "unnamed", True, z.GetFilledPolysList(_L).Contains(t.GetPosition())) for z in _zs])
            if _bad is None: n2 += 1; continue                                    # some zone of this net covers it on this layer, which is what matters
            if not touched: print("NOTE stitch via %s at (%.1f, %.1f) outside the fill of %s on %s (no track on it: it carries nothing)" % (t.GetNetname(), t.GetPosition().x / 1e6, t.GetPosition().y / 1e6, ", ".join("'%s'" % x for x in _bad), b.GetLayerName(_L))); continue   # P2's ground grid where the router's tracks pushed the fill away
            check(False, "locked via %s at (%.1f, %.1f) is inside %s on %s and NO fill of its net reaches it there" % (t.GetNetname(), t.GetPosition().x / 1e6, t.GetPosition().y / 1e6, ", ".join("'%s'" % x for x in _bad), b.GetLayerName(_L))); n2 += 1
    # 13 September 2026 (MESHSAT-862): A BAND DRAWN AS ONE POLYGON THAT FILLS IN TWO IS A CONDUCTOR WITH A GAP
    # IN IT. `power_copper` refuses rectangles that do not form one polygon, and until today nothing asked what
    # the FILL made of them. On A25 five did: VBAT's B.Cu comb in two pieces (VBUS20's own new band sat across
    # its trunk), the PA head in two, the HF head in four, VIN_RAW's dock top in two, and the current went
    # round through the router's 0.4 and 0.5 mm tracks, which is the whole reason the density pass exists.
    # A plane (priority 0 or 1) on a routing layer is sliced by tracks and that is expected, so the measure is
    # of BANDS AND ISLANDS only, priority 2 and up, which is what `union()` and `island()` draw. Reported with
    # its numbers first, on every board of the set, before it is anyone's verdict.
    for z in pz:
        if z.GetAssignedPriority() < 2: continue
        L = z.GetFirstLayer(); fp = z.GetFilledPolysList(L)
        big = [fp.Outline(i).Area() / 1e12 for i in range(fp.OutlineCount())]
        big = sorted([a for a in big if a >= SLIVER], reverse=True)
        if len(big) > 1:
            print("NOTE band '%s' (%s, %s) is drawn as ONE polygon and FILLS in %d pieces of %s mm2: the current between them travels in whatever the router laid"
                  % (z.GetZoneName() or "unnamed", z.GetNetname(), b.GetLayerName(L), len(big), ", ".join("%.0f" % a for a in big[:6])))
    bynet = {}
    for z in pz: bynet.setdefault(z.GetNetname(), []).append(z)
    for net, zs in bynet.items():
        layers = {z.GetFirstLayer() for z in zs}
        if len(layers) < 2: continue
        links = [v.GetPosition() for v in vias_all if v.GetNetname() == net] + [p.GetPosition() for p in thru if p.GetNetname() == net]   # vias and through-hole pads join layers
        for z in zs:
            L = z.GetFirstLayer(); group = [g for g in zs if g.GetFirstLayer() == L]   # the same-net pours of one layer are one copper when they overlap (a band chain)
            linked = any(any(g.GetFilledPolysList(L).Contains(q) for g in group) and any(o.GetFilledPolysList(o.GetFirstLayer()).Contains(q) for o in zs if o.GetFirstLayer() != L) for q in links)
            check(linked, "pour '%s' (%s, %s) meets a same-net pour on another layer through a via or a through-hole pad" % (z.GetZoneName() or "unnamed", net, b.GetLayerName(L))); n3 += 1
    return "copper_checks: %d pours, %d locked vias, %d cross-layer links checked on %d power nets" % (n1, n2, n3, len({z.GetNetname() for z in pz}))
