#!/usr/bin/env python3
"""What copper sits at a rail's worst current-density cell (MESHSAT-862, owner ruling 16, 13 September 2026).

`dc_drop.py` names a position and a layer and stops there, which is enough to refuse a board and not enough to
fix one. A density figure has three different causes and they need three different answers: a TRACK narrower
than the rail wants, a POUR pinched to a neck by something crossing it, or too few VIAS where the current
changes layer. This prints what is within a radius of the named point so the cause is read rather than
guessed.

Usage: density_probe.py <board.kicad_pcb> <net> <x> <y> [radius mm] [layer]
"""
import sys, math, pcbnew

def mm(v): return v / 1e6


def main(a):
    if len(a) < 4:
        print(__doc__); return 2
    board, net, x, y = a[0], a[1], float(a[2]), float(a[3])
    r = float(a[4]) if len(a) > 4 else 3.0
    want_layer = a[5] if len(a) > 5 else None
    b = pcbnew.LoadBoard(board)
    names = {net, "/" + net.lstrip("/"), net.lstrip("/")}

    print("%s at (%.2f, %.2f), everything of this net within %.1f mm" % (net, x, y, r))
    tracks, vias = [], []
    for t in b.GetTracks():
        if t.GetNetname() not in names: continue
        p0, p1 = t.GetStart(), t.GetEnd()
        d = min(math.hypot(mm(p0.x) - x, mm(p0.y) - y), math.hypot(mm(p1.x) - x, mm(p1.y) - y))
        if d > r: continue
        if t.GetClass() == "PCB_VIA":
            vias.append((d, mm(t.GetWidth()), mm(t.GetDrill()), b.GetLayerName(t.TopLayer()), b.GetLayerName(t.BottomLayer()), mm(p0.x), mm(p0.y)))
        else:
            tracks.append((d, mm(t.GetWidth()), b.GetLayerName(t.GetLayer()),
                           math.hypot(mm(p1.x) - mm(p0.x), mm(p1.y) - mm(p0.y)), t.IsLocked()))
    if tracks:
        widths = sorted(set(round(w, 3) for _, w, _, _, _ in tracks))
        print("  %d track(s), widths %s mm" % (len(tracks), ", ".join("%.3f" % w for w in widths)))
        for d, w, L, ln, lock in sorted(tracks)[:10]:
            print("    %5.2f mm away  %-9s %.3f mm wide, %6.2f mm long %s" % (d, L, w, ln, "LOCKED" if lock else ""))
    else:
        print("  no track of this net within the radius")
    if vias:
        print("  %d via(s):" % len(vias))
        for d, w, dr, t_, bt, vx, vy in sorted(vias)[:10]:
            print("    %5.2f mm away  %.2f/%.2f mm  %s to %s  at (%.2f, %.2f)" % (d, w, dr, t_, bt, vx, vy))
    else:
        print("  NO VIA of this net within the radius, so any layer change here is somewhere else")

    print("  zones of this net:")
    found = False
    for z in b.Zones():
        if z.GetNetname() not in names: continue
        L = b.GetLayerName(z.GetLayer())
        if want_layer and L != want_layer: continue
        bb = z.GetBoundingBox()
        inside = (mm(bb.GetLeft()) - r <= x <= mm(bb.GetRight()) + r and mm(bb.GetTop()) - r <= y <= mm(bb.GetBottom()) + r)
        if not inside: continue
        found = True
        area = z.GetFilledArea() / 1e12 if hasattr(z, "GetFilledArea") else 0.0
        print("    %-9s %-42s filled %8.1f mm2, min width %.2f mm%s"
              % (L, (z.GetZoneName() or "(unnamed)")[:42], area, mm(z.GetMinThickness()), ", RULE AREA" if z.GetIsRuleArea() else ""))
    if not found: print("    no zone of this net covers this point")

    print("  OTHER nets' copper within %.1f mm on that layer, which is what pinches a pour:" % r)
    near = {}
    for t in b.GetTracks():
        if t.GetNetname() in names or not t.GetNetname(): continue
        if want_layer and b.GetLayerName(t.GetLayer()) != want_layer and t.GetClass() != "PCB_VIA": continue
        p0 = t.GetStart()
        d = math.hypot(mm(p0.x) - x, mm(p0.y) - y)
        if d <= r:
            k = t.GetNetname()
            if k not in near or d < near[k][0]: near[k] = (d, t.GetClass(), mm(t.GetWidth()))
    for k, (d, cls, w) in sorted(near.items(), key=lambda kv: kv[1][0])[:8]:
        print("    %5.2f mm  %-18s %s %.3f mm" % (d, k[:18], "via" if cls == "PCB_VIA" else "track", w))
    if not near: print("    nothing, so the neck is not another net")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
