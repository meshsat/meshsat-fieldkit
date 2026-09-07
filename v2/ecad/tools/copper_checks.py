#!/usr/bin/env python3
"""Copper integrity checks shared by the board gates (MESHSAT-862, 8 Sep 2026): the A21 gate had them (band contiguity, stitch vias in fill,
piece touching, appendix 32.39) and the A22 rewrite dropped them while finish_a22.sh still grepped for their lines; A22 is the 20 A board.
Written once, zone-name-free, so B16's In4 pours and P1's bands get the same gate.

On a filled board (skipped when no zone carries a fill):
  1. every filled zone of a power net is one piece, or every piece touches the fill of another same-net zone on its layer (a higher-priority
     foot across a column legitimately splits a pour), and its fill covers at least MIN_COVER of its outline's bounding box (a pour that the
     router's tracks have eaten to slivers is a defect, not a fill);
  2. every locked via of a power net whose position lies inside a same-net zone's outline sits in that zone's fill on the zone's layer
     (a via the fill retreated from is a stitch that carries nothing);
  3. the pieces of one net across layers touch through at least one via of that net (a band on B.Cu and its riser on In2 must meet).
Power nets: the board's net-class assignments with a class other than Default whose name suggests power (PWR, NODE, RAIL, SW, HV) plus any
net named GND, or the caller's list.  Usage as a module: fails = copper_checks.run(board, check, power_nets=None)."""
import pcbnew

MIN_COVER = 0.5

def power_nets(b, extra=()):
    names = set(extra)
    for k in range(1, b.GetNetInfo().GetNetCount()):
        n = b.GetNetInfo().GetNetItem(k).GetNetname()
        if n.lstrip("/") == "GND" or n.lstrip("/").startswith(("+", "VBAT", "CELL", "VBUS", "PACK", "FUSED", "VIN", "PV_", "TRK_")): names.add(n)
    return names

def run(b, check, nets=None):
    zones = [z for z in b.Zones() if not z.GetIsRuleArea()]
    if not any(z.GetFilledArea() > 0 for z in zones): return "copper_checks: no filled zone on this board, nothing checked"
    nets = nets if nets is not None else power_nets(b)
    pz = [z for z in zones if z.GetNetname() in nets and z.GetFilledArea() > 0]
    n1 = n2 = n3 = 0
    for z in pz:
        L = z.GetFirstLayer(); fp = z.GetFilledPolysList(L); bb = z.GetBoundingBox()
        rect = bb.GetWidth() / 1e6 * bb.GetHeight() / 1e6; area = z.GetFilledArea() / 1e12
        others = [o for o in pz if o is not z and o.GetNetname() == z.GetNetname() and o.GetFirstLayer() == L]
        def touches(i):
            o = fp.Outline(i)
            return any(any(x.GetFilledPolysList(L).Collide(o.GetPoint(k), int(0.06e6)) for k in range(o.PointCount())) for x in others)
        joined = fp.OutlineCount() == 1 or all(touches(i) for i in range(fp.OutlineCount()))
        check(joined and area >= MIN_COVER * rect, "pour '%s' (%s, %s) is one piece or every piece touches a same-net zone, fill %.0f of %.0f mm2 (%d pieces)" % (z.GetZoneName() or "unnamed", z.GetNetname(), b.GetLayerName(L), area, rect, fp.OutlineCount())); n1 += 1
    for t in b.GetTracks():
        if t.Type() != pcbnew.PCB_VIA_T or not t.IsLocked() or t.GetNetname() not in nets: continue
        inside = [z for z in pz if z.GetNetname() == t.GetNetname() and z.Outline().Contains(t.GetPosition())]
        for z in inside:
            check(z.GetFilledPolysList(z.GetFirstLayer()).Contains(t.GetPosition()), "locked via %s at (%.1f, %.1f) sits in the fill of '%s' on %s" % (t.GetNetname(), t.GetPosition().x / 1e6, t.GetPosition().y / 1e6, z.GetZoneName() or "unnamed", b.GetLayerName(z.GetFirstLayer()))); n2 += 1
    bynet = {}
    for z in pz: bynet.setdefault(z.GetNetname(), []).append(z)
    for net, zs in bynet.items():
        layers = {z.GetFirstLayer() for z in zs}
        if len(layers) < 2: continue
        vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == net]
        for z in zs:
            L = z.GetFirstLayer(); fz = z.GetFilledPolysList(L)
            linked = any(fz.Contains(v.GetPosition()) and any(o.GetFilledPolysList(o.GetFirstLayer()).Contains(v.GetPosition()) for o in zs if o.GetFirstLayer() != L) for v in vias)
            check(linked, "pour '%s' (%s, %s) meets a same-net pour on another layer through a via" % (z.GetZoneName() or "unnamed", net, b.GetLayerName(L))); n3 += 1
    return "copper_checks: %d pours, %d locked vias, %d cross-layer links checked on %d power nets" % (n1, n2, n3, len({z.GetNetname() for z in pz}))
