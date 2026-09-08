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

def run(b, check, nets=None):
    zones = [z for z in b.Zones() if not z.GetIsRuleArea()]
    routed = any(t.GetClass() == "PCB_TRACK" and not t.IsLocked() for t in b.GetTracks())
    if not routed: return "copper_checks: pre-route board, the copper checks run on the routed and filled board"
    if not any(z.GetFilledArea() > 0 for z in zones):
        check(not zones, "copper_checks: %d zones on the routed board and none filled: refill before the gate" % len(zones)); return "copper_checks: 0 pours checked (no filled zone)"
    nets = nets if nets is not None else power_nets(b)
    pz = [z for z in zones if z.GetNetname() in nets and z.GetFilledArea() > 0]
    n1 = n2 = n3 = 0
    thru = [p for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() in nets and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    vias_all = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() in nets]
    for z in pz:
        L = z.GetFirstLayer(); fp = z.GetFilledPolysList(L); bb = z.GetBoundingBox()
        rect = z.Outline().Area() / 1e12; area = z.GetFilledArea() / 1e12   # against the zone's own outline area (a ring or an L is not its bounding box; review of 8 Sep 2026)
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
        solid_gnd = z.GetNetname() == "GND" and any(o.GetNetname() == "GND" and o.GetFirstLayer() != L and o.GetFilledArea() >= 0.8 * o.Outline().Area() for o in pz)   # a ground pour on a routing layer beside a solid ground plane: its islands are a note, not a defect
        if slivers: print("NOTE pour '%s' (%s, %s): %d piece(s) under %.1f mm2 not counted (isolated slivers, the fill's own crumbs)" % (z.GetZoneName() or "unnamed", z.GetNetname(), b.GetLayerName(L), slivers, SLIVER))
        if solid_gnd and loose: print("NOTE pour '%s' (%s, %s): %d of %d pieces loose; the solid ground plane on another layer carries the return" % (z.GetZoneName() or "unnamed", z.GetNetname(), b.GetLayerName(L), loose, fp.OutlineCount())); loose = 0
        check(loose == 0 and area >= MIN_COVER * rect, "pour '%s' (%s, %s): every piece anchored by a pad or via of its net (%d of %d loose), fill %.0f of %.0f mm2 of its outline (at least %.0f%%)" % (z.GetZoneName() or "unnamed", z.GetNetname(), b.GetLayerName(L), loose, fp.OutlineCount(), area, rect, MIN_COVER * 100)); n1 += 1
    for t in b.GetTracks():
        if t.Type() != pcbnew.PCB_VIA_T or not t.IsLocked() or t.GetNetname() not in nets: continue
        inside = [z for z in pz if z.GetNetname() == t.GetNetname() and z.Outline().Contains(t.GetPosition())]
        touched = any(tr.GetClass() == "PCB_TRACK" and tr.GetNetname() == t.GetNetname() and (tr.GetStart() == t.GetPosition() or tr.GetEnd() == t.GetPosition()) for tr in b.GetTracks())
        for z in inside:
            if t.GetNetname() == "GND" and any(o.GetNetname() == "GND" and o.GetFirstLayer() != z.GetFirstLayer() and o.GetFilledArea() >= 0.8 * o.Outline().Area() for o in pz): continue   # a ground via reaches the solid plane
            if not touched and not z.GetFilledPolysList(z.GetFirstLayer()).Contains(t.GetPosition()): print("NOTE stitch via %s at (%.1f, %.1f) outside the fill of '%s' (no track on it: it carries nothing)" % (t.GetNetname(), t.GetPosition().x / 1e6, t.GetPosition().y / 1e6, z.GetZoneName() or "unnamed")); continue   # P2's ground grid where the router's tracks pushed the fill away
            check(z.GetFilledPolysList(z.GetFirstLayer()).Contains(t.GetPosition()), "locked via %s at (%.1f, %.1f) sits in the fill of '%s' on %s" % (t.GetNetname(), t.GetPosition().x / 1e6, t.GetPosition().y / 1e6, z.GetZoneName() or "unnamed", b.GetLayerName(z.GetFirstLayer()))); n2 += 1
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
