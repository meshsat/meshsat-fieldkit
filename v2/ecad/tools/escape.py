#!/usr/bin/env python3
"""Deterministic escapes for fine-pitch parts, before autorouting: every connected pad of a fine-pitch footprint gets a short
track straight out along its axis to a via, offsets staggered on alternate pads so neighbouring escapes never touch.
Fine pitch: minimum SMD pad centre distance <= 0.7 mm, or SOT-23-6/8. Exposed pads (>= 2 mm) are left alone.
Usage: escape.py <board.kicad_pcb>"""
import sys, re, math, pcbnew
from pcbnew import VECTOR2I, FromMM
b = pcbnew.LoadBoard(sys.argv[1]); CLR = FromMM(0.16)
def is_fine(fp):
    if re.search(r"SOT-23-[68]", fp.GetFPIDAsString()): return True
    pads = [p.GetPosition() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    best = 1e9
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = math.hypot(pads[i].x - pads[j].x, pads[i].y - pads[j].y)
            if 0 < d < best: best = d
    return best <= FromMM(0.7)
def min_pitch(fp):
    pads = [p.GetPosition() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]; best = 1e9
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = math.hypot(pads[i].x - pads[j].x, pads[i].y - pads[j].y)
            if 0 < d < best: best = d
    return best
def pad_poly(p):
    L = next((l for l in (pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In1_Cu) if p.IsOnLayer(l)), pcbnew.F_Cu)
    return p.GetEffectivePolygon(L)
allpads = [(p, p.GetPosition(), pad_poly(p), p.GetNetname(), fp.GetReference()) for fp in b.GetFootprints() for p in fp.Pads()]
def ep_numbers(fp):
    """Pad numbers that belong to an exposed pad (any pad of that number >= 2 mm): their small pieces are not pins."""
    return {p.GetNumber() for p in fp.Pads() if max(p.GetSize().x, p.GetSize().y) >= FromMM(2.0)}
rule_areas = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]   # A19: inner-layer track bans allow vias and must not block escapes or fanout
edges = b.GetBoardEdgesBoundingBox()
vias = [(t.GetPosition(), t.GetWidth(pcbnew.F_Cu) / 2, t.GetNetname()) for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
tracks = [(t.GetStart(), t.GetEnd(), t.GetWidth() / 2, t.GetNetname()) for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]
def seg_dist(p, a, c):
    dx, dy = c.x - a.x, c.y - a.y; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p.x - a.x) * dx + (p.y - a.y) * dy) / L2))
    return math.hypot(p.x - (a.x + t * dx), p.y - (a.y + t * dy))
import os
DEBUG_REF = os.environ.get("DEBUG_REF", "")
LAST = [""]
def clear(v, r, me, me_ref, net):
    """Circle (v, r) clear of: board edge, other-net pads (own footprint: plain clearance; other footprints: 0.75 mm lane rule), all vias, all tracks, rule areas."""
    LAST[0] = ""
    if not (edges.GetLeft() + FromMM(1.0) < v.x < edges.GetRight() - FromMM(1.0) and edges.GetTop() + FromMM(1.0) < v.y < edges.GetBottom() - FromMM(1.0)): LAST[0] = "edge"; return False
    for q, qp, qpoly, qnet, qref in allpads:
        if qp.x == me.GetPosition().x and qp.y == me.GetPosition().y: continue
        if qnet == net and qref == me_ref: continue
        gap = CLR if qref == me_ref else (FromMM(0.3) if qnet == net else FromMM(0.75))
        if abs(v.x - qp.x) > FromMM(6) or abs(v.y - qp.y) > FromMM(6): continue
        if qpoly.Collide(VECTOR2I(int(v.x), int(v.y)), int(r + gap)): LAST[0] = "pad %s.%s(%s)" % (qref, q.GetNumber(), qnet); return False
    for vp, vr, vnet in vias:
        if math.hypot(v.x - vp.x, v.y - vp.y) < vr + r + (CLR if vnet != net else FromMM(0.05)): LAST[0] = "via(%s)" % vnet; return False
    for s, e, tr, tnet in tracks:
        if tnet == net: continue
        if seg_dist(v, s, e) < tr + r + CLR: LAST[0] = "track(%s)" % tnet; return False
    for z in rule_areas:
        o = z.Outline()
        if o.Contains(VECTOR2I(int(v.x), int(v.y))) or o.Contains(VECTOR2I(int(v.x + r), int(v.y))) or o.Contains(VECTOR2I(int(v.x - r), int(v.y))) or o.Contains(VECTOR2I(int(v.x), int(v.y + r))) or o.Contains(VECTOR2I(int(v.x), int(v.y - r))): LAST[0] = "rule-area"; return False
    return True
added = skipped = 0
for fp in b.GetFootprints():
    if not is_fine(fp) or fp.GetReference().startswith("J"): continue      # connectors route fine without escapes
    if fp.GetReference() in set(filter(None, __import__("os").environ.get("ESCAPE_SKIP", "").split(","))): continue   # A19: parts the router escapes itself (mixed pad sizes)
    pitch = min_pitch(fp); fc = fp.GetPosition()
    if pitch <= FromMM(0.7): VIA_D, VIA_DR, TW, OFFS = FromMM(0.45), FromMM(0.25), FromMM(0.2), (0.9, 1.6, 2.3)
    else: VIA_D, VIA_DR, TW, OFFS = FromMM(0.6), FromMM(0.3), FromMM(0.25), (0.8, 1.5, 2.2)
    # group pads by side (outward direction), order along the side, alternate the offset
    sides = {}; eps = ep_numbers(fp)
    # one escape per pin: footprints like TI's SON draw each pin as several overlapping pieces, keep the largest per number
    largest = {}
    for pad in fp.Pads():
        if pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or pad.GetNetCode() <= 0 or pad.GetNetname().startswith("unconnected-"): continue
        if pad.GetNumber() in eps or max(pad.GetSize().x, pad.GetSize().y) >= FromMM(2.0): continue   # exposed pad and its pieces
        a = pad.GetSize().x * pad.GetSize().y
        if pad.GetNumber() not in largest or a > largest[pad.GetNumber()][0]: largest[pad.GetNumber()] = (a, pad)
    for _, pad in largest.values():
        c = pad.GetPosition(); sx, sy = pad.GetSize().x, pad.GetSize().y
        th = math.radians(pad.GetOrientationDegrees()); L = (math.cos(th), -math.sin(th)) if sx >= sy else (math.sin(th), math.cos(th))
        u = (c.x - fc.x, c.y - fc.y)
        if L[0] * u[0] + L[1] * u[1] < 0: L = (-L[0], -L[1])
        key = (round(L[0]), round(L[1])); along = -L[1] * c.x + L[0] * c.y
        sides.setdefault(key, []).append((along, pad, L))
    for key, lst in sides.items():
        lst.sort(key=lambda t: t[0])
        if pitch <= FromMM(0.5) and len(lst) >= 2:
            # FAN: 0.4 / 0.5 mm pitch rows cannot pass each other with staggered straight escapes; every pin goes straight out
            # 0.3 mm past its tip, then splays to a via row at 0.8 mm pitch, 1.3 mm past the tips (agent review, item 1)
            n = len(lst); L0 = lst[0][2]; side_dir = (-L0[1], L0[0])
            centre_along = sum(t[0] for t in lst) / n
            for idx, (along, pad, L) in enumerate(lst):
                c = pad.GetPosition(); half = max(pad.GetSize().x, pad.GetSize().y) / 2; net = pad.GetNetname()
                s_k = (idx - (n - 1) / 2.0) * FromMM(0.8) - (along - centre_along)     # lateral shift from the pad's own lane
                done = False
                for depth in (1.3, 1.7, 2.1):
                    knee = VECTOR2I(int(c.x + L[0] * (half + FromMM(0.3))), int(c.y + L[1] * (half + FromMM(0.3))))
                    v = VECTOR2I(int(c.x + L[0] * (half + FromMM(depth)) + side_dir[0] * s_k), int(c.y + L[1] * (half + FromMM(depth)) + side_dir[1] * s_k))
                    mids = [VECTOR2I(int(knee.x + (v.x - knee.x) * k / 5.0), int(knee.y + (v.y - knee.y) * k / 5.0)) for k in range(1, 5)]
                    if clear(v, VIA_D / 2, pad, fp.GetReference(), net) and clear(knee, TW / 2, pad, fp.GetReference(), net) and all(clear(m, TW / 2, pad, fp.GetReference(), net) for m in mids):
                        layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
                        via = pcbnew.PCB_VIA(b); via.SetPosition(v); via.SetDrill(VIA_DR); via.SetWidth(VIA_D); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(pad.GetNet()); b.Add(via)
                        for s0, e0 in ((c, knee), (knee, v)):
                            t = pcbnew.PCB_TRACK(b); t.SetStart(s0); t.SetEnd(e0); t.SetWidth(TW); t.SetLayer(layer); t.SetNet(pad.GetNet()); b.Add(t); tracks.append((s0, e0, TW / 2, net))
                        vias.append((v, VIA_D / 2, net)); added += 1; done = True; break
                if not done:
                    skipped += 1; print("  no escape for %s pad %s (%s)%s" % (fp.GetReference(), pad.GetNumber(), net, ("  last reject: " + LAST[0]) if fp.GetReference() == DEBUG_REF else ""))
            continue
        for idx, (along, pad, L) in enumerate(lst):
            c = pad.GetPosition(); half = max(pad.GetSize().x, pad.GetSize().y) / 2; net = pad.GetNetname()
            order = (OFFS[0], OFFS[1], OFFS[2]) if idx % 2 == 0 else (OFFS[1], OFFS[0], OFFS[2])
            done = False
            for off in order:
                v = VECTOR2I(int(c.x + L[0] * (half + FromMM(off))), int(c.y + L[1] * (half + FromMM(off))))
                mids = [VECTOR2I(int(c.x + (v.x - c.x) * k / 6.0), int(c.y + (v.y - c.y) * k / 6.0)) for k in range(2, 6)]
                if clear(v, VIA_D / 2, pad, fp.GetReference(), net) and all(clear(m, TW / 2, pad, fp.GetReference(), net) for m in mids):
                    layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
                    via = pcbnew.PCB_VIA(b); via.SetPosition(v); via.SetDrill(VIA_DR); via.SetWidth(VIA_D); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(pad.GetNet()); b.Add(via)
                    t = pcbnew.PCB_TRACK(b); t.SetStart(c); t.SetEnd(v); t.SetWidth(TW); t.SetLayer(layer); t.SetNet(pad.GetNet()); b.Add(t)
                    vias.append((v, VIA_D / 2, net)); tracks.append((c, v, TW / 2, net)); added += 1; done = True; break
            if not done:
                skipped += 1; print("  no escape for %s pad %s (%s)%s" % (fp.GetReference(), pad.GetNumber(), net, ("  last reject: " + LAST[0]) if fp.GetReference() == DEBUG_REF else ""))
    # exposed pad: give it vias of its own net when the footprint has none (KiCad's plain footprints carry no thermal vias)
    for pad in fp.Pads():
        if pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or max(pad.GetSize().x, pad.GetSize().y) < FromMM(2.0) or pad.GetNetCode() <= 0: continue
        if any(q.GetNumber() == pad.GetNumber() and q.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for q in fp.Pads()): continue
        c = pad.GetPosition(); big = min(pad.GetSize().x, pad.GetSize().y) >= FromMM(2.5)
        spots = [(dx, dy) for dx in ((-0.7, 0.7) if big else (0.0,)) for dy in ((-0.7, 0.7) if big else (0.0,))]
        for dx, dy in spots:
            v = VECTOR2I(int(c.x + FromMM(dx)), int(c.y + FromMM(dy)))
            via = pcbnew.PCB_VIA(b); via.SetPosition(v); via.SetDrill(FromMM(0.3)); via.SetWidth(FromMM(0.6)); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(pad.GetNet()); b.Add(via)
            vias.append((v, FromMM(0.3), pad.GetNetname())); added += 1
print("escape: %d escapes added, %d pads skipped" % (added, skipped))
pcbnew.SaveBoard(sys.argv[1], b)
