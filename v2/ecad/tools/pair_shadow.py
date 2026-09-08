#!/usr/bin/env python3
"""Shadow routing of a differential pair (MESHSAT-862 Stage C, 8 Sep 2026): Freerouting has no differential-pair routing, so every released
"pair" was two lone traces millimetres apart (impedance_check.py: UNCOUPLED on A22, C7, D8, E6). This pass makes the N leg a parallel copy of
the routed P leg at the class gap: the P leg's unlocked segments and vias are chained from the P pad, the chain is offset by (w + s) to the side
on which the N pad lies, the old unlocked N copper is removed, the offset chain is added as N (same layers, same widths, vias where P has vias),
and the two ends are joined to the N pads by straight stubs. The caller runs DRC and keeps the result only if hard and open did not rise
(pair_match.sh pattern); a leg the pass cannot shadow (a fork, a T, or a P leg with locked pieces in the middle) is reported and left alone.
Escapes (locked pieces at the pads) are kept on both legs; the shadow starts where the P escape ends.

Usage: pair_shadow.py <board.kicad_pcb> <pair stem> [--gap mm] [--test]   -> writes the board (or a copy with --test), prints 'pair_shadow: ...', exit 1 when not shadowed."""
import sys, os, math, json, pcbnew

def chain_from(tracks, start, tol=20000):
    """Order unlocked tracks and vias into a path from the point start; returns the ordered list or None on a fork."""
    left = list(tracks); path = []; cur = start
    while left:
        near = [t for t in left if (t.GetClass() == "PCB_VIA" and dist(t.GetPosition(), cur) < tol) or (t.GetClass() == "PCB_TRACK" and (dist(t.GetStart(), cur) < tol or dist(t.GetEnd(), cur) < tol))]
        if not near: break
        if len(near) > 1 and all(t.GetClass() == "PCB_TRACK" for t in near): return None   # a fork
        t = near[0]; left.remove(t); path.append(t)
        if t.GetClass() == "PCB_TRACK": cur = t.GetEnd() if dist(t.GetStart(), cur) < tol else t.GetStart()
        else: cur = t.GetPosition()
    return path if not left else None

def dist(a, b): return math.hypot(a.x - b.x, a.y - b.y)

def main(a):
    if len(a) < 2: print(__doc__); return 2
    b = pcbnew.LoadBoard(a[0]); stem = a[1].lstrip("/"); test = "--test" in a
    names = {str(n).lstrip("/"): str(n) for n in b.GetNetInfo().NetsByName().keys()}
    pn, nn = names.get(stem + "_P"), names.get(stem + "_N")
    if not pn or not nn: print("pair_shadow: no nets %s_P/_N" % stem); return 1
    pads = {net: [p for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() == net] for net in (pn, nn)}
    if len(pads[pn]) != 2 or len(pads[nn]) != 2: print("pair_shadow: %s is not a two-pad pair (P %d pads, N %d)" % (stem, len(pads[pn]), len(pads[nn]))); return 1
    ncls = b.GetDesignSettings().m_NetSettings; cls = None
    try: cls = ncls.GetEffectiveNetClass(pn)
    except Exception: pass
    gap = float(a[a.index("--gap") + 1]) if "--gap" in a else (cls.GetDiffPairGap() / 1e6 if cls else 0.15)
    P = [t for t in b.GetTracks() if t.GetNetname() == pn]; N = [t for t in b.GetTracks() if t.GetNetname() == nn]
    p_locked = [t for t in P if t.IsLocked()]; p_free = [t for t in P if not t.IsLocked()]
    # the P chain starts where the escape of pad A ends: the free piece nearest pad A
    pa, pb = pads[pn]; na, nb = pads[nn]
    if dist(na.GetPosition(), pa.GetPosition()) > dist(nb.GetPosition(), pa.GetPosition()): na, nb = nb, na   # pair the N pads with the P pads by proximity
    start = min([t for t in p_free], key=lambda t: min(dist(t.GetStart(), pa.GetPosition()), dist(t.GetEnd(), pa.GetPosition())) if t.GetClass() == "PCB_TRACK" else dist(t.GetPosition(), pa.GetPosition()), default=None)
    if start is None: print("pair_shadow: P leg of %s has no free copper" % stem); return 1
    s0 = start.GetStart() if start.GetClass() == "PCB_TRACK" and dist(start.GetStart(), pa.GetPosition()) < dist(start.GetEnd(), pa.GetPosition()) else (start.GetEnd() if start.GetClass() == "PCB_TRACK" else start.GetPosition())
    path = chain_from(p_free, s0)
    if not path: print("pair_shadow: P leg of %s forks or has locked pieces mid-way, not shadowed" % stem); return 1
    # the offset side: the side of the first segment on which the N start pad lies
    first = next(t for t in path if t.GetClass() == "PCB_TRACK"); ax, ay = first.GetStart().x, first.GetStart().y; bx, by = first.GetEnd().x, first.GetEnd().y
    side = 1 if ((bx - ax) * (na.GetPosition().y - ay) - (by - ay) * (na.GetPosition().x - ax)) > 0 else -1
    w = first.GetWidth(); off = w + int(gap * 1e6)
    # remove the old free N copper
    removed = 0
    for t in N:
        if not t.IsLocked(): b.Remove(t); removed += 1
    net_n = b.GetNetInfo().GetNetItem(nn); added = []
    def add_seg(p1, p2, L, wd):
        t = pcbnew.PCB_TRACK(b); t.SetStart(p1); t.SetEnd(p2); t.SetWidth(wd); t.SetLayer(L); t.SetNet(net_n); t.SetLocked(False); b.Add(t); added.append(t); return t
    cur = s0
    # per segment: the offset copy at (w + gap); at a via the copy steps out to VIA_OFF (the hole-to-hole rule forbids a via at the track gap), jogs in
    # on the next layer; consecutive shifted segments meet at the next one's start (a short mitre)
    VIA_OFF = max(off, int(0.9e6)); items = []; nrm = None
    for t in path:
        if t.GetClass() == "PCB_TRACK":
            p1, p2 = (t.GetStart(), t.GetEnd()) if dist(t.GetStart(), cur) < 20000 else (t.GetEnd(), t.GetStart())
            dx, dy = p2.x - p1.x, p2.y - p1.y; ln = math.hypot(dx, dy) or 1.0; nrm = (-dy / ln * side, dx / ln * side)
            q1 = pcbnew.VECTOR2I(int(p1.x + nrm[0] * off), int(p1.y + nrm[1] * off)); q2 = pcbnew.VECTOR2I(int(p2.x + nrm[0] * off), int(p2.y + nrm[1] * off))
            items.append(("seg", q1, q2, t.GetLayer(), t.GetWidth())); cur = p2
        else:
            n = nrm or (1.0, 0.0); items.append(("via", t, pcbnew.VECTOR2I(int(t.GetPosition().x + n[0] * VIA_OFF), int(t.GetPosition().y + n[1] * VIA_OFF)))); cur = t.GetPosition()
    last = None; last_layer = None; last_w = None
    for k, item in enumerate(items):
        if item[0] == "seg":
            _, q1, q2, L, wd = item
            if last is not None and dist(last, q1) > 1000: add_seg(last, q1, L, wd)
            add_seg(q1, q2, L, wd); last = q2; last_layer = L; last_w = wd
        else:
            t, vq = item[1], item[2]
            if last is not None: add_seg(last, vq, last_layer, last_w)   # the jog out to the via on the layer we are leaving
            v = pcbnew.PCB_VIA(b); v.SetPosition(vq); v.SetWidth(t.GetWidth()); v.SetDrill(t.GetDrillValue()); v.SetViaType(t.GetViaType()); v.SetLayerPair(t.TopLayer(), t.BottomLayer()); v.SetNet(net_n); b.Add(v); added.append(v)
            last = vq
    pts = items
    # the end stubs to the N pads on the pads' layers
    first_seg = next(x for x in items if x[0] == "seg"); last_seg = next(x for x in reversed(items) if x[0] == "seg")
    def stub(pad, q, L, wd):
        Lp = L if pad.IsOnLayer(L) else (pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu)
        if Lp != L:
            v = pcbnew.PCB_VIA(b); v.SetPosition(q); v.SetWidth(int(0.7e6)); v.SetDrill(int(0.3e6)); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net_n); b.Add(v); added.append(v)
        add_seg(q, pad.GetPosition(), Lp, wd)
    stub(na, first_seg[1] if items[0][0] == "seg" else items[0][2], first_seg[3], first_seg[4]); stub(nb, last if last is not None else last_seg[2], last_seg[3], last_seg[4])
    out = a[0] if not test else a[0].replace(".kicad_pcb", "-shadow.kicad_pcb")
    pcbnew.SaveBoard(out, b)
    print("pair_shadow: %s: N leg rebuilt as a copy of P at gap %.2f mm (%d pieces removed, %d added, side %+d, layers %s) -> %s" % (stem, gap, removed, len(added), side, sorted({b.GetLayerName(x.GetLayer()) for x in added if x.GetClass() == "PCB_TRACK"}), out))
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
