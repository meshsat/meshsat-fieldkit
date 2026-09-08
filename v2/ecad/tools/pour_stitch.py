#!/usr/bin/env python3
"""Stitch a pour island that has no via of its own net (MESHSAT-862, 8 Sep 2026).

A filled zone breaks into pieces around the tracks that cross it. A piece with no via is copper that reaches nothing:
KiCad reports it as an unconnected item between the zone and itself, and on a ground pour it is a piece of shield with
no path to the plane. D9 ended a clean route with eleven such pieces on its front ground pour, one of them 222 mm2.

For each island without a via of its net, the pass picks the point inside it furthest from any other copper, places a
locked via there, refills and re-reads the board, and keeps the via only if the hard count does not rise, the way
stub_accept.py keeps the stub router's closures. Islands too small or too crowded for a via are named and left.

Usage: pour_stitch.py <board.kicad_pcb> [--nets GND,+3V3] [--min-area 1.0] [--via=0.6/0.3] [--dry]"""
import sys, os, re, math, json, subprocess, pcbnew

bp = sys.argv[1]
nets = set((next((a.split("=",1)[1] for a in sys.argv[2:] if a.startswith("--nets=")), None) or "GND").split(","))
min_area = float(next((a.split("=",1)[1] for a in sys.argv[2:] if a.startswith("--min-area=")), 1.0))
opt = next((a.split("=",1)[1] for a in sys.argv[2:] if a.startswith("--via=")), None)
dry = "--dry" in sys.argv
b = pcbnew.LoadBoard(bp); mm = lambda v: v / 1e6
ds = b.GetDesignSettings()
VD, VDR = ((float(v) for v in opt.split("/")) if opt else (max(0.6, mm(ds.m_ViasMinSize)), max(0.3, mm(ds.m_MinThroughDrill))))
TOOLS = os.path.dirname(os.path.abspath(__file__))
tmp = os.path.splitext(bp)[0] + ("-stitch.kicad_pcb" if dry else ".kicad_pcb")
if dry:
    for e in (".kicad_pro", ".kicad_prl"):
        s_ = os.path.splitext(bp)[0] + e
        if os.path.exists(s_): __import__("shutil").copy(s_, os.path.splitext(tmp)[0] + e)
j = os.path.splitext(tmp)[0] + "-stitch-drc.json"

def measure():
    b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(tmp, b)
    subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "-o", j, tmp], capture_output=True)
    t = subprocess.run([sys.executable, os.path.join(TOOLS, "hardset.py"), j, "post"], capture_output=True, text=True).stdout
    m = re.search(r"hard (\d+) of", t); u = re.search(r"unrouted (\d+)", t)
    return (int(m.group(1)) if m else -1, int(u.group(1)) if u else -1)

cur = measure()
print("pour_stitch: start hard %d, unrouted %d" % cur)
def keepaways(net):
    """Copper that is not this net, as ("r", x0, y0, x1, y1) rectangles for pads and ("s", ax, ay, bx, by, half) segments
    for tracks and vias. A track is a segment, not a circle: scoring it by its centre and half length made every point on a
    long track read as tens of millimetres INSIDE it and no island could ever be stitched (8 Sep 2026 18:30)."""
    out = []
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname() == net: continue
            bb = p.GetBoundingBox(); out.append(("r", mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())))
    for t in b.GetTracks():
        if t.GetNetname() == net: continue
        if t.GetClass() == "PCB_VIA":
            c = t.GetPosition(); out.append(("s", mm(c.x), mm(c.y), mm(c.x), mm(c.y), mm(t.GetWidth()) / 2))
        else:
            out.append(("s", mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetEnd().x), mm(t.GetEnd().y), mm(t.GetWidth()) / 2))
    return out

def clearance_at(x, y, ka):
    """Distance from (x, y) to the nearest edge of any other-net copper, in mm."""
    best = 1e9
    for it in ka:
        if it[0] == "r":
            _, x0, y0, x1, y1 = it
            dx = max(x0 - x, 0.0, x - x1); dy = max(y0 - y, 0.0, y - y1); d = math.hypot(dx, dy)
        else:
            _, ax, ay, bx, by, half = it
            vx, vy = bx - ax, by - ay; L = vx * vx + vy * vy
            u = 0.0 if L == 0 else max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / L))
            d = math.hypot(x - (ax + u * vx), y - (ay + u * vy)) - half
        if d < best: best = d
    return best

# phase 1 collects the candidates without touching the board: a refill invalidates every polygon reference still in
# hand, and placing a via inside the loop over a zone's outlines segfaulted the process (8 Sep 2026 18:33)
cands = []
for z in list(b.Zones()):
    if z.GetIsRuleArea() or z.GetNetname().lstrip("/") not in nets: continue
    ka = keepaways(z.GetNetname())
    for L in z.GetLayerSet().Seq():
        try: fp = z.GetFilledPolysList(L)
        except Exception: continue
        if fp is None: continue
        for i in range(fp.OutlineCount()):
            o = fp.Outline(i); area = o.Area() / 1e12
            if area < min_area: continue
            if any(t.GetClass() == "PCB_VIA" and t.GetNetname() == z.GetNetname() and o.PointInside(t.GetPosition()) for t in b.GetTracks()): continue
            bb = o.BBox(); best = None
            x0, x1, y0, y1 = mm(bb.GetLeft()), mm(bb.GetRight()), mm(bb.GetTop()), mm(bb.GetBottom())
            step = max(0.25, min(1.0, (x1 - x0 + y1 - y0) / 60))
            yy = y0
            while yy <= y1:
                xx = x0
                while xx <= x1:
                    if o.PointInside(pcbnew.VECTOR2I(pcbnew.FromMM(xx), pcbnew.FromMM(yy))):
                        d = clearance_at(xx, yy, ka)
                        if best is None or d > best[0]: best = (d, xx, yy)
                    xx += step
                yy += step
            cands.append((area, b.GetLayerName(L), best, z.GetNet(), z.GetNetname()))
placed = 0; left = 0
for area, lname, best, netobj, netname in sorted(cands, key=lambda c: -c[0]):
    if best is None or best[0] < VD / 2 + 0.2:
        print("pour_stitch: %s island of %.1f mm2 on %s has no room for a via (clearest point %.2f mm)" % (netname, area, lname, best[0] if best else -1)); left += 1; continue
    v = pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(best[1]), pcbnew.FromMM(best[2])))
    v.SetWidth(pcbnew.FromMM(VD)); v.SetDrill(pcbnew.FromMM(VDR)); v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(netobj); v.SetLocked(True); b.Add(v)
    st = measure()
    if st[0] > cur[0]:
        b.Remove(v); print("pour_stitch: the via for the %.1f mm2 island at %.2f,%.2f raised hard %d -> %d, taken out" % (area, best[1], best[2], cur[0], st[0])); left += 1; continue
    print("pour_stitch: %.1f mm2 %s island on %s stitched at %.2f, %.2f (clearest %.2f mm); unrouted %d -> %d" % (area, netname, lname, best[1], best[2], best[0], cur[1], st[1]))
    cur = st; placed += 1
final = measure()
print("pour_stitch: %d island(s) stitched, %d left; hard %d, unrouted %d" % (placed, left, final[0], final[1]))
sys.exit(0 if final[1] == 0 else 1)
