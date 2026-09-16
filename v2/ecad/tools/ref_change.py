#!/usr/bin/env python3
"""Where does a signal's REFERENCE change, and to what (rule RET-003, MESHSAT-862, 16 September 2026).

A report AND, since 16 September 2026 07:00, a gate for one of the three cases. RET-003 is a blocker in the registry with nothing implementing it, and its coverage note
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

MEASURED FIRST, on every board in the tree: board A has 86 vias that keep their reference, 131 that move
between two ground planes, and 35 that move to or from a POWER plane; C has 62 and 166 and none; D 145 and
none; E 202 and none. The third column is board A alone, because A's In2 carries a GND pour and a VBAT pour
side by side, and it is board A's 35 that this gate is about.

THE GATE. A via whose reference changes between two DIFFERENT NETS needs a capacitor between those two nets
near it, because that is the only path the return current has. The radius is declared per board as
`stitch_cap_mm` with its reason; a board that declares none is INCONCLUSIVE rather than passing at a figure
this tool made up, the same refusal the registry makes of every unsourced limit.

Usage: ref_change.py <board.kicad_pcb> [--frac 0.25] [--check]
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
    # WHAT A REFERENCE CHANGE COSTS DEPENDS ON THE SIGNAL, which is the same law rules RET-001 and RET-004 were
    # rewritten under on 16 September 2026 and which this gate was missing on its first run: of board A's 34
    # transitions without a stitching capacitor, most are enable lines and inhibit lines, and a line that
    # changes state when a person presses a switch has no return loop worth closing. The class comes from the
    # same declaration those rules use, and a net nobody classified is judged as though it were fast.
    try:
        import signal_class as _sc
        _targets = {k for k, v in ((it.get("pair_classes") or {}).items()) if v}
        _cls = _sc.classify(b, path, _targets, None)[0]
    except Exception:
        _cls = {}
    ends = {}
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK": continue
        for e in (t.GetStart(), t.GetEnd()):
            ends.setdefault((t.GetNetname(), round(mm(e.x), 2), round(mm(e.y), 2)), set()).add(t.GetLayer())
    same = other_gnd = to_power = unknown = slow = 0; examples = []; power_vias = []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_VIA": continue
        net = t.GetNetname()
        if not signalnets.is_signal(net, signals): continue
        if (_cls.get(net) or ("UNKNOWN", ""))[0] == "LOW_SPEED_OR_DC": slow += 1; continue
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
            power_vias.append((p[0], p[1], frozenset(allnets), net.lstrip("/")))
            if len(examples) < 10:
                examples.append("%s at (%.1f, %.1f): %s" % (net.lstrip("/"), p[0], p[1],
                                " -> ".join("/".join(sorted(n)) for n in nets)))
    print("ref_change: signal vias: %d keep one reference, %d move between GROUND planes (a ground via closes "
          "those, rule RET-004), %d change to or from a POWER plane (a ground via cannot close those: the "
          "return needs a capacitor between the two planes), %d undetermined, %d slow (no edge worth a return "
          "loop, by the same declaration rules RET-001 and RET-004 read)"
          % (same, other_gnd, to_power, unknown, slow))
    for e in examples: print("  %s" % e)
    if "--check" not in a: return 0

    # THE GATE, for the third case only. The other two are RET-004's and are gated there.
    import verdict as _v, boardtable as _bt
    letter = _bt.letter_for(path)
    r = _bt.value(letter, "stitch_cap_mm")
    out_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "out")
    if r is None:
        return _v.write("return_stitch", _v.INCONCLUSIVE, denominator=len(power_vias),
                        counts={"plane_change_to_power": len(power_vias), "slow": slow}, inputs={"board": path},
                        applicable=not power_vias,
                        note=("this board has no transition between two different reference nets, so RET-003 has "
                              "nothing on it to judge" if not power_vias else
                              "this board declares no stitch_cap_mm, so the distance a stitching capacitor may "
                              "sit at is not established and the %d transition(s) stay unjudged" % len(power_vias)),
                        out_dir=out_dir)
    caps = []
    for fp in b.GetFootprints():
        pads = list(fp.Pads())
        if len(pads) != 2: continue
        nets = frozenset(p.GetNetname().lstrip("/") for p in pads)
        if len(nets) != 2: continue
        caps.append((nets, mm(fp.GetPosition().x), mm(fp.GetPosition().y), fp.GetReference()))
    bad = []
    for (x, y, want, net) in power_vias:
        near = [c for c in caps if c[0] == want and ((c[1] - x) ** 2 + (c[2] - y) ** 2) ** 0.5 <= r]
        if not near:
            bad.append("%s at (%.1f, %.1f): the reference changes %s and no capacitor between those nets is "
                       "within %.1f mm" % (net, x, y, " to ".join(sorted(want)), r))
    print("ref_change: %d transition(s) between different reference nets, %d without a stitching capacitor "
          "within %.1f mm" % (len(power_vias), len(bad), r))
    for x in bad[:20]: print("  FAIL %s" % x)
    return _v.write("return_stitch", _v.FAIL if bad else _v.PASS,
                    counts={"plane_change_to_power": len(power_vias), "without_capacitor": len(bad), "slow": slow},
                    denominator=len(power_vias) or 1, evidence=bad[:20],
                    inputs={"board": path, "stitch_cap_mm": r},
                    note="a return current that has to cross between two different reference conductors crosses "
                         "at a capacitor or it goes the long way round",
                    out_dir=out_dir)


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
