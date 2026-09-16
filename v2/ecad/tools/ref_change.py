#!/usr/bin/env python3
"""Where does a signal's REFERENCE change, and to what (rule RET-003, MESHSAT-862, 16 September 2026).

A REPORT, not a gate. RET-003 is a blocker in the registry with nothing implementing it, and its coverage note
says so plainly: "nothing determines the reference conductor before and after a transition; return_via's
same-plane exemption is the nearest thing and is a geometric approximation". Before writing a gate, the thing
to know is how many transitions on these boards actually change reference, and to WHAT, because the answer
decides what the rule can demand:

  * ground plane to the SAME ground plane: nothing is owed, the return follows its signal.
  * ground plane to ANOTHER ground plane: a ground via near the transition, which is rule RET-004 and is
    already gated.
  * ground plane to a POWER plane: a ground via cannot help. The return has to cross between two different
    conductors, and the element that lets it is a capacitor between those two planes near the transition.
    Nothing in this project has ever looked for one.

`return_via.py` counts only GROUND pours as planes, so the third case is invisible to it today. This report
counts all three by treating every large filled zone as a possible reference, and says which net each is.

Usage: ref_change.py <board.kicad_pcb> [--frac 0.25]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pcbnew
import intent, signalnets


def planes(b, frac):
    """{layer: [(net, zone)]} for every zone filled over `frac` of the board: a reference is a reference whatever
    its net. The ZONE travels with the net because a layer can carry several pours and the one that matters is
    the one UNDER THE TRANSITION: board A's In2 carries GND and VBAT side by side, and which of them a via
    references is a question about that via's position, not about the layer."""
    bb = b.GetBoardEdgesBoundingBox(); area = (bb.GetWidth() / 1e6) * (bb.GetHeight() / 1e6) or 1.0
    out = {}
    for z in b.Zones():
        if z.GetIsRuleArea(): continue
        if z.GetFilledArea() / 1e12 < frac * area: continue
        out.setdefault(z.GetFirstLayer(), []).append((z.GetNetname().lstrip("/"), z))
    return out


def net_at(pl, layer, x, y, r=1.0, n=12):
    """The net of the pour under the copper AROUND (x, y) on `layer`, or None where no fill reaches.

    NOT at the point itself: the fill retreats from a via by its clearance, so the via's own centre sits in an
    anti-pad hole and every sample there reads "no pour". The first version of this report did exactly that and
    came back with every via undetermined on every board, which is the shape of a test asking the wrong
    question rather than a board with no planes. The reference is what the return current rides beside the
    transition, so the sample is a ring around it and the nearest hit wins."""
    import pcbnew as _p, math as _m
    for rad in (r, r * 2):
        for k in range(n):
            a = 2 * _m.pi * k / n
            pt = _p.VECTOR2I(int((x + rad * _m.cos(a)) * 1e6), int((y + rad * _m.sin(a)) * 1e6))
            for net, z in pl.get(layer, ()):
                try:
                    if z.HitTestFilledArea(layer, pt, 0): return net
                except Exception:
                    try:
                        if z.GetFilledPolysList(layer).Contains(pt): return net
                    except Exception: pass
    return None


def nearest(layer, cu, pl):
    i = cu.index(layer); best = None; refs = set()
    for L in pl:
        if L == layer: continue
        d = abs(cu.index(L) - i)
        if best is None or d < best: best, refs = d, {L}
        elif d == best: refs.add(L)
    return refs


def main(a):
    if not a: print(__doc__); return 2
    path = a[0]; frac = float(a[a.index("--frac") + 1]) if "--frac" in a else 0.25
    mm = lambda v: v / 1e6
    b = pcbnew.LoadBoard(path)
    it = intent.load(path) or {}
    signals, _ = signalnets.classify(b, path, (it.get("rails") or {}).keys())
    cu = list(b.GetEnabledLayers().CuStack()); pl = planes(b, frac)
    print("ref_change: %s: %d layer(s) carry a reference plane over %.0f%% of the board: %s"
          % (os.path.basename(path), len(pl), frac * 100,
             ", ".join("%s=%s" % (b.GetLayerName(L), "/".join(sorted(n for n, _z in zs))) for L, zs in sorted(pl.items()))))
    ends = {}
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK": continue
        for e in (t.GetStart(), t.GetEnd()):
            ends.setdefault((t.GetNetname(), round(mm(e.x), 2), round(mm(e.y), 2)), set()).add(t.GetLayer())
    same = other_gnd = to_power = unknown = 0; examples = []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_VIA": continue
        net = t.GetNetname()
        if not signalnets.is_signal(net, signals): continue
        p = (round(mm(t.GetPosition().x), 2), round(mm(t.GetPosition().y), 2))
        attached = ends.get((net, p[0], p[1]), set())
        if len(attached) < 2: unknown += 1; continue
        refs = [nearest(L, cu, pl) for L in attached]
        # the reference is the pour UNDER THIS VIA, not every pour that shares the layer with it
        nets = []
        for r in refs:
            found = set()
            for L in r:
                nm = net_at(pl, L, p[0], p[1])
                if nm: found.add(nm)
            nets.append(frozenset(found))
        if not all(nets): unknown += 1; continue
        if len(set(nets)) == 1 and len(set(frozenset(r) for r in refs)) == 1: same += 1; continue
        allnets = set().union(*nets)
        if allnets == {"GND"}: other_gnd += 1
        else:
            to_power += 1
            if len(examples) < 10:
                examples.append("%s at (%.1f, %.1f): %s" % (net.lstrip("/"), p[0], p[1],
                                " -> ".join("/".join(sorted(n)) for n in nets)))
    print("ref_change: signal vias: %d keep one reference, %d move between GROUND planes (a ground via closes "
          "those, rule RET-004), %d change to or from a POWER plane (a ground via cannot close those: the "
          "return needs a capacitor between the two planes), %d undetermined"
          % (same, other_gnd, to_power, unknown))
    for e in examples: print("  %s" % e)
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
