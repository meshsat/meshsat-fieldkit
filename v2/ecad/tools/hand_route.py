#!/usr/bin/env python3
"""hand_route.py <board.kicad_pcb> <net> <width mm> <OX> <OY> LAYER:x,y LAYER:x,y ... [--out=file] [--test] [--via=0.45/0.25]

A post-route closure by hand (the C7 lesson of 7 Sep 2026, appendix 32.61): locked tracks along the given waypoints (case-frame mm, converted with the
board's user origin OX, OY), each waypoint carrying its layer; where two consecutive waypoints share a position but not a layer, or the layer changes
between two points, a locked via (default 0.45/0.25) is placed at the second point. The net name may carry or omit the leading slash. With --test the
result goes to a copy (--out, default <board>-hand.kicad_pcb), the zones are refilled, the DRC runs and the hard and unconnected counts are printed;
without --test the board itself is written. The first and last waypoints should sit on existing copper of the net (a pad centre, a via, a track end):
the connectivity check decides, not this script. Prints 'hand_route: N segments, V vias, hard H, unconnected U'."""
import sys, os, json, subprocess, collections, pcbnew
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import hardset
args = [a for a in sys.argv[1:] if not a.startswith("--")]; opts = [a for a in sys.argv[1:] if a.startswith("--")]
board_path, net, width, OX, OY = args[0], args[1], float(args[2]), float(args[3]), float(args[4])
pts = []
for a in args[5:]:
    layer, xy = a.split(":"); x, y = (float(v) for v in xy.split(",")); pts.append((layer, x, y))
out = next((o.split("=", 1)[1] for o in opts if o.startswith("--out=")), os.path.splitext(board_path)[0] + "-hand.kicad_pcb")
via = next((o.split("=", 1)[1] for o in opts if o.startswith("--via=")), "0.45/0.25"); VD, VDR = (float(v) for v in via.split("/"))
test = "--test" in opts
b = pcbnew.LoadBoard(board_path)
n = b.FindNet(net) or b.FindNet("/" + net.lstrip("/")) or b.FindNet(net.lstrip("/"))
if n is None or n.GetNetCode() <= 0: raise SystemExit("net not found: " + net)
def P(x, y): return pcbnew.VECTOR2I(pcbnew.FromMM(OX + x), pcbnew.FromMM(OY - y))
k = v_n = 0
for (l0, x0, y0), (l1, x1, y1) in zip(pts, pts[1:]):
    if l0 != l1:
        v = pcbnew.PCB_VIA(b); v.SetPosition(P(x1, y1) if (x0, y0) == (x1, y1) else P(x0, y0)); v.SetWidth(pcbnew.FromMM(VD)); v.SetDrill(pcbnew.FromMM(VDR)); v.SetNet(n); v.SetLocked(True); b.Add(v); v_n += 1
        if (x0, y0) == (x1, y1): continue
        l0 = l1                                 # the segment after a layer change runs on the new layer from the via
    t = pcbnew.PCB_TRACK(b); t.SetStart(P(x0, y0)); t.SetEnd(P(x1, y1)); t.SetWidth(pcbnew.FromMM(width)); t.SetLayer(b.GetLayerID(l1)); t.SetNet(n); t.SetLocked(True); b.Add(t); k += 1
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
target = out if test else board_path
b.Save(target)
if test:
    pro = os.path.splitext(board_path)[0] + ".kicad_pro"; tpro = os.path.splitext(target)[0] + ".kicad_pro"
    if os.path.exists(pro) and not os.path.exists(tpro): subprocess.run(["cp", pro, tpro])
    drc = os.path.splitext(target)[0] + "-drc.json"
    subprocess.run(["kicad-cli", "pcb", "drc", "--severity-error", "--format", "json", "-o", drc, target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    d = json.load(open(drc)); c = collections.Counter(x["type"] for x in d["violations"])
    hard = sum(c[t] for t in hardset.HARD_POST)   # one definition (10 Sep 2026, both red teams C1)
    det = [(x["type"], [i["description"][:44] for i in x["items"]], round(x["items"][0]["pos"]["x"] - OX, 1), round(OY - x["items"][0]["pos"]["y"], 1)) for x in d["violations"] if x["type"] in hardset.HARD_POST][:4]
    print("hand_route: %d segments, %d vias (%s), hard %d, unconnected %d %s" % (k, v_n, net, hard, len(d.get("unconnected_items", [])), det))
else: print("hand_route: %d locked segments, %d vias (%s) written to %s" % (k, v_n, net, target))
