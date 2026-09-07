#!/usr/bin/env python3
"""Join adjacent same-net pads of one footprint with a short locked track before routing (5 Sep 2026, B15 runs 2 and 3).

Freerouting treats every pad as its own target. Where a connector has two neighbouring pins on one net (J_PANEL pins 1 and 2, PANEL_5V) or a
fine-pitch part has consecutive pads on one rail (the hub U1's +3V3 pads 21 to 23, each with its own escape via), the router has to find a
separate exit for each pad in the densest part of the board, and it left exactly those open on every B15 run. Joining the neighbours here
turns each group into one island with one exit to find; the joiner is locked, so the router keeps it.

Rules: same footprint, same net (not GND, which the plane joins), pad centres at most MAX_GAP apart, no other pad of the footprint lying in the
corridor between them, both pads on the same copper side. The track is as wide as the narrower pad (never wider than the net class width when
the .kicad_pro states one) and runs centre to centre on the pads' layer.
Usage: join_adjacent_pins.py <board.kicad_pcb> [max gap mm = 2.6]"""
import sys, os, math, json, os, re, fnmatch, pcbnew
from pcbnew import VECTOR2I, FromMM

BOARD = sys.argv[1]; MAX_GAP = float(sys.argv[2]) if len(sys.argv) > 2 else 2.6
b = pcbnew.LoadBoard(BOARD); mm = pcbnew.ToMM
# net class widths from the project file (the KiCad 9 Python API does not expose them)
widths = {}
pro = os.path.splitext(BOARD)[0] + ".kicad_pro"
if os.path.exists(pro):
    p = json.load(open(pro)); ns = p.get("net_settings", {})
    cls = {c["name"]: c.get("track_width", 0.25) for c in ns.get("classes", [])}
    pats = [(pt["pattern"], pt["netclass"]) for pt in ns.get("netclass_patterns", [])]
    for ni in b.GetNetInfo().NetsByName().values():
        name = ni.GetNetname()
        for pat, c in pats:
            if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(name.lstrip("/"), pat): widths[name] = cls.get(c, 0.25); break
default_w = cls.get("Default", 0.25) if os.path.exists(pro) else 0.25

def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

joins = 0; per_ref = {}
ENDS = set()
for t in b.GetTracks():
    if t.GetClass() == "PCB_TRACK": ENDS.add((t.GetStart().x, t.GetStart().y)); ENDS.add((t.GetEnd().x, t.GetEnd().y))
def big(pd): return min(mm(pd.GetSize().x), mm(pd.GetSize().y)) >= 1.5                      # an exposed pad
def stubbed(pd): return (pd.GetPosition().x, pd.GetPosition().y) in ENDS                      # an escape already leaves it
# 7 Sep 2026 (E6 run 12): the ground pads of a part with an exposed pad are joined to it by locked tracks under the body: a full ring of 0.4 mm escape vias fences the
# ground plane on every layer, so the exposed pad's island would otherwise reach the outside only by luck
for fp in b.GetFootprints():
    pads = [pd for pd in fp.Pads() if pd.GetNetCode() > 0]   # ground pads too: every one of them joins the exposed pad (E6 run 12: the ring of 0.4 mm escape vias fences the plane under a QFN on every layer, the exposed pad's island reaches the outside only through a pad's escape via)
    for i, a in enumerate(pads):
        for c in pads[i + 1:]:
            if a.GetNetCode() != c.GetNetCode(): continue
            gnd = a.GetNetname() == "GND"
            if gnd and not (big(a) != big(c)): continue                                        # ground: only a pad-to-exposed-pad join
            ax, ay = mm(a.GetPosition().x), mm(a.GetPosition().y); cx, cy = mm(c.GetPosition().x), mm(c.GetPosition().y)
            if gnd:
                # the ground join runs along the small pad's own axis into the exposed pad's edge (a diagonal to its centre grazed the neighbouring pads, E6 run 15)
                small, ep = (a, c) if big(c) else (c, a); sx, sy = mm(small.GetPosition().x), mm(small.GetPosition().y); ex, ey = mm(ep.GetPosition().x), mm(ep.GetPosition().y)
                hw, hh = mm(ep.GetSize().x) / 2, mm(ep.GetSize().y) / 2; horiz = mm(small.GetSize().x) > mm(small.GetSize().y)
                if horiz and (ey - hh <= sy <= ey + hh): tx, ty = (ex - hw if sx < ex else ex + hw), sy
                elif (not horiz) and (ex - hw <= sx <= ex + hw): tx, ty = sx, (ey - hh if sy < ey else ey + hh)
                else: continue
                ax, ay, cx, cy = sx, sy, tx, ty
            d = math.hypot(cx - ax, cy - ay)
            if d > MAX_GAP or d < 0.05: continue
            la = pcbnew.F_Cu if a.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu; lc = pcbnew.F_Cu if c.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
            if la != lc: continue
            wa = min(mm(a.GetSize().x), mm(a.GetSize().y)); wc = min(mm(c.GetSize().x), mm(c.GetSize().y))
            w = min(wa, wc, widths.get(a.GetNetname(), default_w))
            # nothing of another net in the corridor (other pads of this footprint within half the corridor width plus their own half size)
            blocked = False
            for o in fp.Pads():   # SWIG hands out a new proxy per iteration: compare by number and position, never by identity
                if (o.GetNumber(), o.GetPosition().x, o.GetPosition().y) in ((a.GetNumber(), a.GetPosition().x, a.GetPosition().y), (c.GetNumber(), c.GetPosition().x, c.GetPosition().y)): continue
                ox, oy = mm(o.GetPosition().x), mm(o.GetPosition().y); r = min(mm(o.GetSize().x), mm(o.GetSize().y)) / 2   # the narrow half: a collinear row neighbour 0.5 mm away must not block a 0.2 mm joiner
                if gnd and big(o): continue
                if o.GetNumber() == "" or not o.IsOnCopperLayer(): continue   # the exposed pad's paste windows (unnumbered, paste layers only) are not obstacles
                if seg_dist(ox, oy, ax, ay, cx, cy) < w / 2 + r + 0.127:
                    blocked = True
                    if fp.GetReference() == os.environ.get("DEBUG_REF", ""): print("    %s-%s blocked by pad %s at %.3f" % (a.GetNumber(), c.GetNumber(), o.GetNumber(), seg_dist(ox, oy, ax, ay, cx, cy)))
                    break
            if blocked: continue
            t = pcbnew.PCB_TRACK(b); t.SetStart(VECTOR2I(FromMM(ax), FromMM(ay))); t.SetEnd(VECTOR2I(FromMM(cx), FromMM(cy))); t.SetWidth(FromMM(round(w, 3))); t.SetLayer(la); t.SetNetCode(a.GetNetCode()); t.SetLocked(True)
            b.Add(t); joins += 1; per_ref.setdefault(fp.GetReference(), []).append("%s-%s %s %.2f" % (a.GetNumber(), c.GetNumber(), a.GetNetname(), w))
pcbnew.SaveBoard(BOARD, b)
for ref, lst in sorted(per_ref.items()): print("  joined %-8s %s" % (ref, "; ".join(lst)))
print("join_adjacent_pins: %d locked joins on %d footprints (gap <= %.1f mm)" % (joins, len(per_ref), MAX_GAP))
