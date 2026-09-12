#!/usr/bin/env python3
"""Before autorouting: give every SMD pad on a plane net (GND, +5V) a fanout via + stub so the inner planes reach it.
Usage: prefanout.py <board.kicad_pcb>"""
import sys, math, pcbnew
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boardorder
from pcbnew import VECTOR2I, FromMM
b = pcbnew.LoadBoard(sys.argv[1])
PLANES = {n.lstrip("/") for n in sys.argv[2].split(",")} if len(sys.argv) > 2 else {"GND", "+5V"}   # 7 Sep 2026: root-sheet labels are "/NAME" on the board; until now only the power-symbol nets (GND) ever got a via
SKIP = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else set()   # footprints whose plane pads are handled elsewhere ("fine" = every fine-pitch part, see escape.py)
import re as _re
def is_fine(fp):
    if _re.search(r"SOT-23-[68]", fp.GetFPIDAsString()): return True
    pads = [p.GetPosition() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    best = 1e9
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            d = math.hypot(pads[i].x - pads[j].x, pads[i].y - pads[j].y)
            if 0 < d < best: best = d
    return best <= FromMM(0.7)
_ds = b.GetDesignSettings()
VIA_D, VIA_DRILL, TRACK_W = max(_ds.m_ViasMinSize, FromMM(0.45)), max(_ds.m_MinThroughDrill, FromMM(0.25)), FromMM(0.4)   # 7 Sep 2026: the board's small via (0.45/0.25 on the four-layer boards) instead of 0.8/0.4, so a plane via fits beside a packed 0603; a 2-layer board keeps its 0.5/0.3 floor
if b.GetCopperLayerCount() == 2: VIA_D, VIA_DRILL = max(VIA_D, FromMM(0.5)), max(VIA_DRILL, FromMM(0.3))
# The board's OWN rules, not a number typed here. The in-pad fallback below kept a hard-wired 0.15 mm from
# every other-net pad, and this board's hole clearance is 0.19 and its minimum clearance 0.127: a via placed
# at a pad centre could satisfy the tool and fail the DRC, which is 25 of the 45 hard violations left on
# B19's placed board (12 September 2026). A margin that is not the board's is a second opinion about the
# board (appendix 32.149).
_DS = b.GetDesignSettings()
INPAD_CLR = max(_DS.m_HoleClearance, _DS.m_MinClearance, FromMM(0.15))
allpads = [(p, p.GetPosition(), max(p.GetSize().x, p.GetSize().y) / 2) for fp in b.GetFootprints() for p in fp.Pads()]
rule_areas = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()] + [z for fp in b.GetFootprints() for z in fp.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]   # A19: inner-layer track bans allow vias and must not block escapes or fanout; B13: footprint keep-outs (the E72 antenna) count too
edges = b.GetBoardEdgesBoundingBox()
placed = [t.GetPosition() for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]; placed_nets = []   # escapes already on the board count as placed vias
segs = [(t.GetStart(), t.GetEnd(), t.GetWidth() / 2, t.GetNetname()) for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]   # B16 (7 Sep 2026): escape stubs are obstacles too, a fanout via landed on one
def _seg_dist(p, a, c):
    ax, ay, bx, by = a.x, a.y, c.x, c.y; dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p.x - ax) * dx + (p.y - ay) * dy) / L2))
    return math.hypot(p.x - (ax + t * dx), p.y - (ay + t * dy))
def clear(v, me, r=None):
    r = VIA_D / 2 if r is None else r
    mp = me.GetPosition()
    if not (edges.GetLeft() + FromMM(1.5) < v.x < edges.GetRight() - FromMM(1.5) and edges.GetTop() + FromMM(1.5) < v.y < edges.GetBottom() - FromMM(1.5)): return False
    for q, qp, qr in allpads:
        if qp.x == mp.x and qp.y == mp.y: continue            # the pad itself (wrapper objects differ, compare by position)
        gap = FromMM(0.35) if q.GetNetname() == me.GetNetname() else FromMM(0.5)   # keep other-net pads' exit lanes open for the router (0.75 until 7 Sep 2026: half the ground pads of a packed region got no via and the router left islands)
        if math.hypot(v.x - qp.x, v.y - qp.y) < qr + r + gap: return False
    for w in placed:
        if math.hypot(v.x - w.x, v.y - w.y) < VIA_D + FromMM(0.35): return False
    for a, c, hw, _n in segs:
        if _seg_dist(v, a, c) < hw + r + FromMM(0.2): return False
    for z in rule_areas:
        o = z.Outline()
        for ddx, ddy in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r)):
            if o.Contains(VECTOR2I(int(v.x + ddx * 1.3), int(v.y + ddy * 1.3))): return False
    return True
added = skipped = inpad = 0
for fp in boardorder.footprints(b):   # stage 0b, 11 Sep 2026: this loop LAYS, so its order decides what fits; board order follows a random uuid
    skip_fp = fp.GetReference() in SKIP or ("fine" in SKIP and is_fine(fp))
    fc = fp.GetPosition()
    for pad in fp.Pads():
        if skip_fp and not (pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and min(pad.GetSize().x, pad.GetSize().y) >= FromMM(1.5) and pad.GetNetname().lstrip("/") in PLANES): continue   # a fine part's exposed pad still gets its plane via (D8 run 5: the amplifier's pad sat on an island)
        if skip_fp:
            c = pad.GetPosition()
            if not any(math.hypot(c.x - w.x, c.y - w.y) < VIA_D + FromMM(0.35) for w in placed):
                via = pcbnew.PCB_VIA(b); via.SetPosition(c); via.SetDrill(VIA_DRILL); via.SetWidth(VIA_D); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLocked(True)
                via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(pad.GetNet()); b.Add(via); placed.append(c); placed_nets.append((c, pad.GetNetname())); added += 1; inpad += 1
            continue
        if pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or pad.GetNetname().lstrip("/") not in PLANES: continue
        c = pad.GetPosition(); half = max(pad.GetSize().x, pad.GetSize().y) / 2
        TRACK_W = min(FromMM(0.4), max(FromMM(0.2), min(pad.GetSize().x, pad.GetSize().y)))   # never wider than the pad: fine-pitch neighbours keep a legal corridor
        dx, dy = c.x - fc.x, c.y - fc.y; n = math.hypot(dx, dy)
        u = (dx / n, dy / n) if n > FromMM(0.3) else (1.0, 0.0)
        sx, sy = pad.GetSize().x, pad.GetSize().y
        if max(sx, sy) > 1.4 * min(sx, sy):                       # elongated IC pad: leave along its long axis, away from the body
            th = math.radians(pad.GetOrientationDegrees())
            L = (math.cos(th), -math.sin(th)) if sx >= sy else (math.sin(th), math.cos(th))
            if L[0] * u[0] + L[1] * u[1] < 0: L = (-L[0], -L[1])
            u = L
        s2 = math.sqrt(0.5)
        dirs = [u, (-u[1], u[0]), (u[1], -u[0]), (-u[0], -u[1])]
        dirs += [((a[0] + b_[0]) * s2, (a[1] + b_[1]) * s2) for a, b_ in ((dirs[0], dirs[1]), (dirs[0], dirs[2]), (dirs[3], dirs[1]), (dirs[3], dirs[2]))]   # diagonals too (E6 round 6: two 0603 ground pads beside the RP2040's escapes had no axis-aligned room and their pour pieces stayed islands)
        done = False
        for off in (half + FromMM(0.65), half + FromMM(1.1), half + FromMM(1.6), half + FromMM(2.2), half + FromMM(2.9)):
            for ux, uy in dirs:
                v = VECTOR2I(int(c.x + ux * off), int(c.y + uy * off))
                mid = VECTOR2I(int((c.x + v.x) / 2), int((c.y + v.y) / 2)); q3 = VECTOR2I(int((c.x + 3 * v.x) / 4), int((c.y + 3 * v.y) / 4))
                # 9 Sep 2026 (D10, appendix 32.83): the stub was tested at its midpoint and three-quarter point only. On a
                # 3.4 mm stub that leaves 1.1 mm between samples, and the pairs now lie on the board before the fanout runs,
                # so a 3.375 mm GND stub crossed D10's laid USB3_N leg between two samples and blocked the whole pre-route.
                # The dense sample is against TRACKS ONLY: running the full clear() every 0.2 mm also tightened the
                # other-net PAD rule (0.5 mm of lane each side), which cost 18 fanout vias and drove ten of them into the
                # in-pad fallback on the same run. Crossing a laid track is the defect; passing a pad is not.
                def _crosses(a_, b_):
                    n_ = max(4, int(math.hypot(b_.x - a_.x, b_.y - a_.y) / FromMM(0.2)))
                    for k in range(0, n_ + 1):
                        q = VECTOR2I(int(a_.x + (b_.x - a_.x) * k / n_), int(a_.y + (b_.y - a_.y) * k / n_))
                        for s_, e_, hw_, n2_ in segs:
                            if n2_ == pad.GetNetname(): continue
                            if _seg_dist(q, s_, e_) < hw_ + TRACK_W / 2 + FromMM(0.15): return True
                    return False
                if clear(v, pad) and clear(mid, pad, TRACK_W / 2) and clear(q3, pad, TRACK_W / 2) and not _crosses(c, v):
                    layer = pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
                    via = pcbnew.PCB_VIA(b); via.SetPosition(v); via.SetDrill(VIA_DRILL); via.SetWidth(VIA_D); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLocked(True)   # locked like the escapes (5 Sep 2026): the router keeps the pad-to-pour tie and the width gates skip it
                    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(pad.GetNet()); b.Add(via)
                    t = pcbnew.PCB_TRACK(b); t.SetStart(c); t.SetEnd(v); t.SetWidth(TRACK_W); t.SetLayer(layer); t.SetNet(pad.GetNet()); t.SetLocked(True); b.Add(t)
                    placed.append(v); placed_nets.append((v, pad.GetNetname())); added += 1; done = True; break
            if done: break
        if not done and min(pad.GetSize().x, pad.GetSize().y) >= VIA_D + FromMM(0.1) and not any(math.hypot(c.x - w.x, c.y - w.y) < VIA_D + FromMM(0.35) for w in placed) \
           and all(math.hypot(c.x - qp.x, c.y - qp.y) >= qr + VIA_D / 2 + INPAD_CLR for q, qp, qr in allpads if q.GetNetname() != pad.GetNetname()) \
           and all(_seg_dist(c, a_, e_) >= hw_ + VIA_D / 2 + INPAD_CLR for a_, e_, hw_, n_ in segs if n_ != pad.GetNetname()):   # 8 Sep 2026: the in-pad fallback tested pads and vias but not TRACKS, so a via in a plane pad landed on a neighbour's locked escape and the escape was pruned for it (B17, 32.77). The via's ring must keep the class clearance from every other-net pad (D8 run 4: a 1210 neighbour 0.72 mm away)
            # 7 Sep 2026 (E6 run 8, D8 run 3): a plane pad with no room around it gets its via in the pad (0.45/0.25 inside a 0603 land), so no pour piece is ever left
            # hanging on a pad without a path to the plane; the count is reported for the order notes (via-in-pad is a prototype allowance)
            via = pcbnew.PCB_VIA(b); via.SetPosition(c); via.SetDrill(VIA_DRILL); via.SetWidth(VIA_D); via.SetViaType(pcbnew.VIATYPE_THROUGH); via.SetLocked(True)
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(pad.GetNet()); b.Add(via); placed.append(c); placed_nets.append((c, pad.GetNetname())); added += 1; inpad += 1; done = True
        if not done: skipped += 1; print("  no room for a fanout via at %s pad %s (%s)" % (fp.GetReference(), pad.GetNumber(), pad.GetNetname()))
print("fanout: %d vias added (%d in the pad), %d pads skipped" % (added, inpad, skipped))
pcbnew.SaveBoard(sys.argv[1], b)
