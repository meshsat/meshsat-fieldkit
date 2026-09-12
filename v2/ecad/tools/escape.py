#!/usr/bin/env python3
"""Deterministic escapes for fine-pitch parts, before autorouting: every connected pad of a fine-pitch footprint gets a short
track straight out along its axis to a via, offsets staggered on alternate pads so neighbouring escapes never touch.
Escapes are LOCKED: KiCad exports locked tracks and vias as (type fix) in the DSN and Freerouting keeps them (4 Sep: unlocked
escapes were ripped up on A19 and the pads they served ended unrouted).
Fine pitch: minimum SMD pad centre distance <= 0.7 mm, or SOT-23-6/8. Exposed pads (>= 2 mm) are left alone.
Usage: escape.py <board.kicad_pcb>"""
import sys, re, math, pcbnew
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boardorder
from pcbnew import VECTOR2I, FromMM
b = pcbnew.LoadBoard(sys.argv[1]); CLR = FromMM(0.16)
NCC = {}
def _load_classes():
    """Net class clearances and patterns from the project file beside the board (the Python API hides NETCLASS in KiCad 9)."""
    import json, os
    try:
        d = json.load(open(os.path.splitext(sys.argv[1])[0] + ".kicad_pro")).get("net_settings", {})
        cls = {c["name"]: FromMM(c.get("clearance", 0.15)) for c in d.get("classes", [])}
        pats = [(e["pattern"], e["netclass"]) for e in d.get("netclass_patterns", [])]
        return cls, pats
    except Exception: return {}, []
NC_CLS, NC_PATS = _load_classes()
def net_clr(name):
    """Clearance a net needs: the escape default 0.16 or its net class value, whichever is larger (A19: BANK and RAIL ask 0.2)."""
    if name not in NCC:                      # cache the class value only: the floor CLR changes per footprint (0.127 on 0.4 mm rows, 0.16 elsewhere)
        import fnmatch
        v = 0
        for pat, cl in NC_PATS:
            if fnmatch.fnmatchcase(name, pat) or fnmatch.fnmatchcase(name.lstrip("/"), pat): v = NC_CLS.get(cl, 0); break
        NCC[name] = v
    return max(CLR, NCC[name])
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
# The pad's own half extent travels with it, because the nearness window below is measured from the pad
# CENTRE and a big land is nowhere near its own centre. BT1 is a CR2032 holder whose pad 2 is a land many
# millimetres across: an escape via three millimetres from its edge sits eight from its centre, fell
# outside a fixed 6 mm window, was never tested, and landed inside the pad. That is 53 of the 82 hard DRC
# violations left on B19's placed board after the land patterns were corrected, and nothing had read them
# because B19's chain blocks at the pair gate before the pre-route DRC (appendix 32.149, 12 September 2026).
def _is_copper(p):
    """A pad that exists on no copper layer is not an obstacle to anything.

    12 September 2026, board P. KiCad draws a modern exposed pad as one copper pad plus a grid of
    SOLDER PASTE apertures, and the apertures are pads too: F.Paste only, no number, no net. `clear()`
    read the BQ4050's nine apertures as pads of another net and refused all four of its exposed pad's
    thermal vias, on every board with such a land. P's gas gauge finished with the single via
    zone_pad_via.py rescues at the pad centre; the router then ran three BAT_F segments 0.51 mm from it
    on B.Cu, the ground fill retreated, and a QFN-32 gas gauge and primary protector ended with NO
    ground connection to the bottom layer. Paste is not copper."""
    return any(pcbnew.IsCopperLayer(L) for L in p.GetLayerSet().Seq())


allpads = [(p, p.GetPosition(), pad_poly(p), p.GetNetname(), fp.GetReference(),
            max(p.GetSize().x, p.GetSize().y) / 2 + p.GetBoundingBox().GetWidth() / 2)
           for fp in b.GetFootprints() for p in fp.Pads() if _is_copper(p)]
def ep_numbers(fp):
    """Pad numbers that belong to an exposed pad (any pad of that number >= 2 mm): their small pieces are not pins."""
    return {p.GetNumber() for p in fp.Pads() if max(p.GetSize().x, p.GetSize().y) >= FromMM(2.0)}
rule_areas = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()] + [z for fp in b.GetFootprints() for z in fp.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]   # A19: inner-layer track bans allow vias and must not block escapes or fanout; B13: footprint keep-outs (the E72 antenna) count too
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
def clear(v, r, me, me_ref, net, lane=0.75):
    """Circle (v, r) clear of: board edge, other-net pads (own footprint: plain clearance; other footprints: the lane rule, 0.75 mm by default,
    relaxed to 0.35 on a second pass when a fine-pitch row has a neighbour part right past its tips), all vias, all tracks, rule areas."""
    LAST[0] = ""
    if not (edges.GetLeft() + FromMM(1.0) < v.x < edges.GetRight() - FromMM(1.0) and edges.GetTop() + FromMM(1.0) < v.y < edges.GetBottom() - FromMM(1.0)): LAST[0] = "edge"; return False
    for q, qp, qpoly, qnet, qref, qreach in allpads:
        if qp.x == me.GetPosition().x and qp.y == me.GetPosition().y: continue
        if qnet == net and qref == me_ref: continue
        gap = CLR if qref == me_ref else (FromMM(0.3) if qnet == net else FromMM(lane))
        # the window carries the pad's own reach, so a large land is not skipped for being wide
        if abs(v.x - qp.x) > FromMM(6) + qreach or abs(v.y - qp.y) > FromMM(6) + qreach: continue
        if qpoly.Collide(VECTOR2I(int(v.x), int(v.y)), int(r + gap)): LAST[0] = "pad %s.%s(%s)" % (qref, q.GetNumber(), qnet); return False
    for vp, vr, vnet in vias:
        if math.hypot(v.x - vp.x, v.y - vp.y) < vr + r + (max(net_clr(net), net_clr(vnet)) if vnet != net else FromMM(0.3)): LAST[0] = "via(%s)" % vnet; return False   # same net: the 0.3 mm hole-to-hole rule (B16: the M.2 sockets' GND escapes sat 0.05 apart)
    for s, e, tr, tnet in tracks:
        if tnet == net: continue
        if seg_dist(v, s, e) < tr + r + max(net_clr(net), net_clr(tnet)): LAST[0] = "track(%s)" % tnet; return False
    for z in rule_areas:
        o = z.Outline()
        if o.Contains(VECTOR2I(int(v.x), int(v.y))) or o.Contains(VECTOR2I(int(v.x + r), int(v.y))) or o.Contains(VECTOR2I(int(v.x - r), int(v.y))) or o.Contains(VECTOR2I(int(v.x), int(v.y + r))) or o.Contains(VECTOR2I(int(v.x), int(v.y - r))): LAST[0] = "rule-area"; return False
    return True
added = skipped = ep_skipped = 0
ep_pads = []   # (ref, pad number, net, laid, wanted, refusal reasons) for every exposed pad that lost a via
for fp in boardorder.footprints(b):   # stage 0b, 11 Sep 2026: this loop LAYS, so its order decides what fits; board order follows a random uuid
    if not is_fine(fp) or (fp.GetReference().startswith("J") and min_pitch(fp) > FromMM(0.6)): continue      # coarse connectors route fine without escapes; a 0.5 mm M.2 socket (B14 J_WIFI1) does not (5 Sep: the router thrashed 75 min on its 67 bare pads)
    if fp.GetReference() in set(filter(None, __import__("os").environ.get("ESCAPE_SKIP", "").split(","))): continue   # A19: parts the router escapes itself (mixed pad sizes)
    ONLY = set(filter(None, os.environ.get("ESCAPE_ONLY", "").split(",")))
    if ONLY and fp.GetReference() not in ONLY: continue                    # test runs on one part
    pitch = min_pitch(fp); fc = fp.GetPosition()
    # 8 Sep 2026 (B17): the 0.5 mm rows take this scheme by pitch instead of by name. B14's M.2 socket was named here because it is
    # a 0.5 mm row and the splay cannot serve one; B17 has five of them, and on the splay their end pins landed 5 mm sideways. The
    # scheme's own margin is what decides: a 0.127 track passes a neighbour's 0.40 via at 0.5 mm lateral with 0.11 mm to spare, where
    # the 0.45 via and 0.2 track of the branch below leave 0.048 mm and 86 escapes were pruned as violations. The row has to be LONG for
    # this: taking every 0.5 mm part put A23's charger QFN on the shallow 0.3/1.0/1.7 depths of this scheme and its escape vias landed
    # 0.075 mm from their neighbours' tracks, four clearance violations on a board that had none (8 Sep 2026 17:30). A socket has 75 pads,
    # a QFN-32 has 33, so the count separates them and every short 0.5 mm part keeps the splay that has always worked for it.
    nsmd = sum(1 for q in fp.Pads() if q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD)
    ROWS04 = (pitch <= FromMM(0.45) or (pitch <= FromMM(0.5) and nsmd >= 40)) and b.GetDesignSettings().m_ViasMinSize <= FromMM(0.40) and b.GetDesignSettings().m_HoleClearance <= FromMM(0.19)   # B14: the 0.5 mm M.2 rows take the CM5IO tip-via scheme too (the 0.7 scheme left 0.096 mm between a stub and a neighbour via)   # only a board set up for it (B13: via 0.40/0.20, class clearance 0.127, hole clearance 0.19); A20 and D6 keep the QFN scheme
    FAN_OK = True; CLR = FromMM(0.127) if ROWS04 else FromMM(0.16)   # the 0.4 mm rows need the JLC floor itself; every other part keeps the 0.16 margin
    if ROWS04: VIA_D, VIA_DR, TW, OFFS, FAN_OK = FromMM(0.40), FromMM(0.20), FromMM(0.127), (0.3, 1.0, 1.7), False
    # 0.4 mm board-to-board rows (the CM5 receptacles, B13, appendix 32.35): the CM5IO scheme, a 0.40/0.20 via right past every pad tip,
    # neighbours alternating 0.3 and 1.0 mm deep, 0.127 mm tracks; a straight 0.127 track passes a neighbour's 0.40 via at 0.4 mm lateral
    # with 0.137 mm to spare, so the board's class clearance must be 0.127 (gen_pcb_b3.py sets it). No fan: a 50-pad row cannot splay.
    elif pitch <= FromMM(0.7): VIA_D, VIA_DR, TW, OFFS = FromMM(0.45), FromMM(0.25), FromMM(0.2), (0.9, 1.6, 2.3)
    else: VIA_D, VIA_DR, TW, OFFS = FromMM(0.6), FromMM(0.3), FromMM(0.25), (0.8, 1.5, 2.2)
    if b.GetCopperLayerCount() == 2: VIA_D, VIA_DR = max(VIA_D, FromMM(0.5)), max(VIA_DR, FromMM(0.3))   # JLC 2-layer floor (C5: 48 escape vias were at 0.25 on the 2-layer panel)
    # 9 Sep 2026 (D10, appendix 32.83): THE STAGGER MUST NOT LAND ON THE ROUTER'S OWN LIMIT. Two neighbouring escape
    # vias sit one pad pitch apart along the row and OFFS[1] - OFFS[0] apart in depth, so the copper gap between them is
    # sqrt(pitch^2 + dz^2) - VIA_D. On D10's PCA9555 (pitch 0.65, via 0.45, dz 0.7) that is 0.5052 mm and a 0.25 mm router
    # track with 0.127 mm clearance needs 0.504 mm: 1.2 microns of margin. Freerouting threaded it and wrote a
    # self-overlapping knot at U16 pins 7 and 8 (8 shorting_items, 3 clearance, 3 tracks_crossing between X_KEY and
    # X_PA_KEY on In2.Cu), which was every hard violation of the board. A corridor is safe when it is comfortably OPEN or
    # decisively CLOSED, never on the line, so the stagger deepens until the gap clears the passing track by 0.10 mm.
    # A pad whose deepened offset is then rejected falls back to its neighbour's depth, where the gap is pitch - VIA_D
    # (0.20 mm at 0.65 mm pitch): closed, and no knot either.
    _pass = 0.481 if ROWS04 else 0.604    # 0.127 + 2 x 0.127 + 0.10 on the 0.4 mm rows; 0.25 + 2 x 0.127 + 0.10 elsewhere
    _need = math.sqrt(max((_pass + pcbnew.ToMM(VIA_D)) ** 2 - pcbnew.ToMM(pitch) ** 2, 0.0))
    # only a real pad ROW has a corridor between neighbouring escape vias. A two-pad passive escapes its two pads in
    # OPPOSITE directions and has no such corridor, so deepening its offsets buys nothing and costs room: the first
    # run with this rule pushed C56's and C57's escapes 1.2 mm further out into their neighbours and returned two
    # clearance violations on a board that had none there (9 Sep 2026, D10 pre-route). Four SMD pads is the floor.
    if _need > OFFS[1] - OFFS[0] and nsmd >= 4:
        OFFS = (OFFS[0], OFFS[0] + _need, OFFS[0] + 2 * _need)
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
        if FAN_OK and pitch <= FromMM(0.5) and len(lst) >= 2:
            # FAN: 0.4 / 0.5 mm pitch rows cannot pass each other with staggered straight escapes; every pin goes straight out
            # 0.3 mm past its tip, then splays to a via row at 0.8 mm pitch, 1.3 mm past the tips (agent review, item 1)
            n = len(lst); L0 = lst[0][2]; side_dir = (-L0[1], L0[0])
            centre_along = sum(t[0] for t in lst) / n
            for idx, (along, pad, L) in enumerate(lst):
                c = pad.GetPosition(); half = max(pad.GetSize().x, pad.GetSize().y) / 2; net = pad.GetNetname()
                done = False
                # 8 Sep 2026 (B17): a splayed via row is `vpitch / pitch` times as wide as the pad row, so a long row (an M.2 socket's 37 pads at
                # 0.5 mm) throws its end pins 5 mm sideways into whatever stands beside the connector and ten to thirteen pads of every socket
                # got no escape at all. STAGGER first: each pin goes straight out on its own axis to one of `k` depths by index, so the via row
                # is exactly as wide as the pad row and the via pitch is k x the pad pitch. A neighbour's track passes a via at the pad pitch
                # (0.5 mm against 0.225 + 0.127 + 0.1 = 0.452 needed), which is why k = 2 is enough at 0.5 mm and k = 3 is the fallback.
                # vpitch 0 marks a staggered attempt; the splay attempts follow it unchanged for the rows where they do fit. The switch is the
                # splay's own overhang, (vpitch - pitch) x (n - 1) / 2: an LQFP's eight-pad side throws its end pin 1.05 mm wide and routes fine,
                # a 37-pad socket row throws it 5.4 mm into the neighbours, so rows that overhang more than 1.5 mm stagger and the rest do not move.
                # The margin term: a neighbour's track passes a via at one pad pitch, so pitch - via radius - track half must clear the class
                # clearance with room. At 0.4 mm with this branch's 0.45 via and 0.2 track that is 0.075 mm against 0.16 needed, which is what
                # A23's charger QFN reported four times (8 Sep 2026 17:45). The 0.4 and 0.5 mm rows that do need a stagger are the ones the
                # ROWS04 scheme above takes, with its 0.40 via and 0.127 track.
                for lane, vpitch, depth, k in ([(0.75, 0, 0.8, 2), (0.75, 0, 0.8, 3), (0.35, 0, 0.7, 2), (0.35, 0, 0.7, 3), (0.35, 0, 0.55, 2), (0.35, 0, 0.55, 3)] if (0.8 - pitch / 1e6) * (len(lst) - 1) / 2 > 1.5 and (pitch - VIA_D / 2 - TW / 2) >= CLR + FromMM(0.05) else []) + [(0.75, 0.8, dp, 1) for dp in (1.3, 1.7, 2.1)] + [(0.35, 0.8, 1.3, 1), (0.35, 0.8, 1.7, 1), (0.35, 0.7, 1.2, 1), (0.35, 0.7, 1.0, 1), (0.35, 0.7, 0.85, 1), (0.35, 0.8, 2.1, 1)]:
                    # A19 (4 Sep): the BQ25792's south row had a 1210 capacitor 1.7 mm past its tips; the 0.75 mm lane rule rejected every
                    # depth, the row went to the router without escapes and SDA could not be routed at all. Second pass with the lane at 0.35,
                    # the via row at 0.7 mm pitch (smaller splay) and shallower depths, for a row whose neighbour sits closer than the standard depth allows.
                    if k > 1: s_k = 0; depth_ = depth + (idx % k) * 0.8                      # straight out, one of k depths by index
                    else: s_k = (idx - (n - 1) / 2.0) * FromMM(vpitch) - (along - centre_along); depth_ = depth   # lateral shift from the pad's own lane
                    # nested knees: the outermost pin turns 0.3 past its tip, each pin further in turns 0.15 deeper, so a splay never runs
                    # past its outer neighbour's knee (a 0.4 mm row's second pin sat 0.14 mm from the first pin's knee and was always rejected)
                    kd = min(0.3 + 0.15 * min(idx, n - 1 - idx), depth_ - 0.3) if k == 1 else max(0.1, depth_ - 0.3)
                    knee = VECTOR2I(int(c.x + L[0] * (half + FromMM(kd))), int(c.y + L[1] * (half + FromMM(kd))))
                    v = VECTOR2I(int(c.x + L[0] * (half + FromMM(depth_)) + side_dir[0] * s_k), int(c.y + L[1] * (half + FromMM(depth_)) + side_dir[1] * s_k))
                    mids = [VECTOR2I(int(knee.x + (v.x - knee.x) * k / 12.0), int(knee.y + (v.y - knee.y) * k / 12.0)) for k in range(1, 12)]   # B16: a 0.4 mm via slipped between samples 0.4 mm apart on a long splay
                    if clear(v, VIA_D / 2, pad, fp.GetReference(), net, lane) and clear(knee, TW / 2, pad, fp.GetReference(), net, lane) and all(clear(m, TW / 2, pad, fp.GetReference(), net, lane) for m in mids):
                        layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
                        via = pcbnew.PCB_VIA(b); via.SetPosition(v); via.SetDrill(VIA_DR); via.SetWidth(VIA_D); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(pad.GetNet()); via.SetLocked(True); b.Add(via)
                        for s0, e0 in ((c, knee), (knee, v)):
                            t = pcbnew.PCB_TRACK(b); t.SetStart(s0); t.SetEnd(e0); t.SetWidth(TW); t.SetLayer(layer); t.SetNet(pad.GetNet()); t.SetLocked(True); b.Add(t); tracks.append((s0, e0, TW / 2, net))
                        vias.append((v, VIA_D / 2, net)); added += 1; done = True; break
                if not done:
                    skipped += 1; print("  no escape for %s pad %s (%s)%s" % (fp.GetReference(), pad.GetNumber(), net, ("  last reject: " + LAST[0]) if fp.GetReference() == DEBUG_REF else ""))
            continue
        for idx, (along, pad, L) in enumerate(lst):
            c = pad.GetPosition(); half = max(pad.GetSize().x, pad.GetSize().y) / 2; net = pad.GetNetname()
            # WITHDRAWN on measurement (8 Sep 2026 21:55): giving a differential pair's two pads the SAME depth so the pair leaves the row
            # together is geometrically impossible on this scheme. Two 0.40 mm vias one 0.5 mm pitch apart leave 0.10 mm of gap against a
            # 0.14 mm class clearance, so the second via is rejected and falls back to the alternating depth anyway. Measured on B17: the
            # attempt cost 5 escapes (1330 -> 1325) and 5 more skipped pads (58 -> 63) and laid no extra pair. The row alternates.
            order = (OFFS[0], OFFS[1], OFFS[2]) if idx % 2 == 0 else (OFFS[1], OFFS[0], OFFS[2])
            done = False
            for lane, off in [(ln, o) for ln in (0.75, 0.35) for o in order]:
                v = VECTOR2I(int(c.x + L[0] * (half + FromMM(off))), int(c.y + L[1] * (half + FromMM(off))))
                mids = [VECTOR2I(int(c.x + (v.x - c.x) * k / 12.0), int(c.y + (v.y - c.y) * k / 12.0)) for k in range(3, 12)]
                ok = clear(v, VIA_D / 2, pad, fp.GetReference(), net, lane) and all(clear(m, TW / 2, pad, fp.GetReference(), net, lane) for m in mids)
                if not ok and fp.GetReference() == DEBUG_REF: print("    %s pad %s lane %.2f off %.2f: %s" % (fp.GetReference(), pad.GetNumber(), lane, off, LAST[0]))
                if ok:
                    layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
                    via = pcbnew.PCB_VIA(b); via.SetPosition(v); via.SetDrill(VIA_DR); via.SetWidth(VIA_D); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(pad.GetNet()); via.SetLocked(True); b.Add(via)
                    t = pcbnew.PCB_TRACK(b); t.SetStart(c); t.SetEnd(v); t.SetWidth(TW); t.SetLayer(layer); t.SetNet(pad.GetNet()); t.SetLocked(True); b.Add(t)
                    vias.append((v, VIA_D / 2, net)); tracks.append((c, v, TW / 2, net)); added += 1; done = True; break
            if not done:
                skipped += 1; print("  no escape for %s pad %s (%s)%s" % (fp.GetReference(), pad.GetNumber(), net, ("  last reject: " + LAST[0]) if fp.GetReference() == DEBUG_REF else ""))
    # exposed pad: give it vias of its own net when the footprint has none (KiCad's plain footprints carry no thermal vias)
    for pad in fp.Pads():
        # AN EXPOSED PAD IS SQUARE-ISH, NOT MERELY LONG (12 September 2026). The test was `max(size) >= 2 mm`,
        # which reads every one of an HDMI receptacle's nineteen 0.3 x 2.5 mm signal fingers as an exposed pad
        # asking for a thermal via at its own centre; B19 printed eleven such refusals, each naming the
        # neighbouring finger. They laid nothing, so no copper ever depended on it, but the count and the
        # denominator were wrong and the report unreadable. The smaller dimension is what separates a land
        # from a finger.
        if pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or min(pad.GetSize().x, pad.GetSize().y) < FromMM(1.2) \
           or max(pad.GetSize().x, pad.GetSize().y) < FromMM(2.0) or pad.GetNetCode() <= 0: continue
        if any(q.GetNumber() == pad.GetNumber() and q.GetAttribute() == pcbnew.PAD_ATTRIB_PTH for q in fp.Pads()): continue
        c = pad.GetPosition(); big = min(pad.GetSize().x, pad.GetSize().y) >= FromMM(2.5)
        spots = [(dx, dy) for dx in ((-0.7, 0.7) if big else (0.0,)) for dy in ((-0.7, 0.7) if big else (0.0,))]
        ep_laid, ep_why = 0, []
        for dx, dy in spots:
            v = VECTOR2I(int(c.x + FromMM(dx)), int(c.y + FromMM(dy)))
            # THIS LOOP USED TO LAY COPPER WITHOUT ASKING ANYTHING (12 September 2026). A thermal via sits
            # inside its own exposed pad, so it looked safe, and it is a THROUGH via on a board assembled
            # on both sides: it comes out on B.Cu where the underside decoupling lives, and it landed on
            # other parts' pads there. That is 25 of the hard violations on B19's placed board, reading as
            # clearance, hole_clearance, solder_mask_bridge and shorting_items against a handful of
            # back-side resistors. It is the same shape as the pre-router's six unasked emissions
            # (appendix 32.135): an exemption that is true of the pad is not true of the other side.
            if not clear(v, FromMM(0.3), pad, fp.GetReference(), pad.GetNetname()):
                ep_skipped += 1
                ep_why.append("(%+.1f,%+.1f) %s" % (dx, dy, LAST[0] or "?"))
                continue
            via = pcbnew.PCB_VIA(b); via.SetPosition(v); via.SetDrill(FromMM(0.3)); via.SetWidth(FromMM(0.6)); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(pad.GetNet()); b.Add(via)
            vias.append((v, FromMM(0.3), pad.GetNetname())); added += 1; ep_laid += 1
        # A COUNT IS NOT A DIAGNOSIS (12 September 2026, board P). P's chain printed "4 thermal via(s)
        # refused" for two runs and nobody could say which pad or why; the BQ4050's 3.1 mm exposed pad
        # ended with ONE via of the four it asks for, the router then ran three BAT_F segments 0.51 mm
        # from it on B.Cu, the ground fill retreated, and the gas gauge's exposed pad finished with no
        # ground connection to the bottom layer at all. Every refusal names its spot and what it hit.
        if ep_why:
            ep_pads.append((fp.GetReference(), pad.GetNumber(), pad.GetNetname(), ep_laid, len(spots), list(ep_why)))
print("escape: %d escapes added, %d pads skipped, %d thermal via(s) refused for what is on the other side" % (added, skipped, ep_skipped))
for ref, num, net, laid, want, why in ep_pads:
    print("escape: exposed pad %s.%s (%s) got %d thermal via(s) of %d: %s%s"
          % (ref, num, net, laid, want, "; ".join(why[:4]), "" if laid else "   <-- NO VIA AT ALL"))
pcbnew.SaveBoard(sys.argv[1], b)
