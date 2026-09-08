#!/usr/bin/env python3
"""Close a pad that its own plane cannot reach (MESHSAT-862, 8 Sep 2026): after the route and the fill, KiCad reports
'Pad N [GND] of U6 / Zone GND pour' as an unconnected item when the tracks around a fine-pitch pin cut the pour off from it.
The established closure on this board family is a via in the pad, down to the solid inner plane (D8 shipped with six).

For every such open item on a net that has a filled zone, a locked via is placed inside the pad, at its outboard tip
(away from the part's centre) so it clears the pin's own neighbours; the zones are refilled and the DRC is read back.
The pass reverts every via it placed if the hard count rises, the way stub_accept.py guards the stub router.

Usage: zone_pad_via.py <board.kicad_pcb> <drc.json> [--via=0.45/0.25] [--dry]   -> exit 0 when nothing is left of this class."""
import sys, os, re, json, subprocess, pcbnew

bp, drcp = sys.argv[1], sys.argv[2]
via = next((a.split("=", 1)[1] for a in sys.argv[3:] if a.startswith("--via=")), None)
dry = "--dry" in sys.argv
b = pcbnew.LoadBoard(bp); mm = lambda v: v / 1e6
ds = b.GetDesignSettings()
VD, VDR = ((float(v) for v in via.split("/")) if via else (max(0.45, mm(ds.m_ViasMinSize)), max(0.25, mm(ds.m_MinThroughDrill))))

def hardset(j):
    out = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "hardset.py"), j, "post"], capture_output=True, text=True).stdout
    m = re.search(r"hard (\d+) of", out); u = re.search(r"unrouted (\d+)", out)
    return (int(m.group(1)) if m else -1, int(u.group(1)) if u else -1)

before = hardset(drcp)
want = []   # (footprint ref, pad number) of every pad an item pairs with a zone of its own net
for v in json.load(open(drcp)).get("unconnected_items", []):
    its = v.get("items", []); descs = [i.get("description", "") for i in its]
    if not any(d.startswith("Zone") for d in descs): continue
    for d in descs:
        m = re.match(r"Pad (\S+) \[([^\]]*)\] of (\S+)", d)
        if m: want.append((m.group(3), m.group(1), m.group(2)))
made = []
for ref, pn, net in want:
    f = b.FindFootprintByReference(ref)
    if f is None: print("zone_pad_via: no footprint %s" % ref); continue
    p = next((q for q in f.Pads() if q.GetNumber() == pn), None)
    if p is None or p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH: continue   # a through-hole pad is already a barrel
    px, py = mm(p.GetPosition().x), mm(p.GetPosition().y); fx, fy = mm(f.GetPosition().x), mm(f.GetPosition().y)
    sx, sy = mm(p.GetSize().x), mm(p.GetSize().y)
    if min(sx, sy) < VD + 0.04: 
        print("zone_pad_via: %s.%s pad %.2f x %.2f is narrower than a %.2f mm via, left open" % (ref, pn, sx, sy, VD)); continue
    ax = (1.0, 0.0) if sx > sy else (0.0, 1.0)
    s = 1.0 if (px - fx) * ax[0] + (py - fy) * ax[1] >= 0 else -1.0
    step = max(0.0, max(sx, sy) / 2 - VD / 2 - 0.05)
    vx, vy = px + s * ax[0] * step, py + s * ax[1] * step
    v_ = pcbnew.PCB_VIA(b); v_.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(vx), pcbnew.FromMM(vy)))
    v_.SetWidth(pcbnew.FromMM(VD)); v_.SetDrill(pcbnew.FromMM(VDR)); v_.SetViaType(pcbnew.VIATYPE_THROUGH)
    v_.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v_.SetNet(p.GetNet()); v_.SetLocked(True); b.Add(v_); made.append(v_)
    print("zone_pad_via: %s.%s [%s] via at %.3f, %.3f" % (ref, pn, net, vx, vy))
if not made:
    print("zone_pad_via: 0 of %d pad-to-zone items closed (nothing placeable)" % len(want)); sys.exit(0 if not want else 1)
b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones())
tmp = os.path.splitext(bp)[0] + ("-zpv.kicad_pcb" if dry else ".kicad_pcb")
if dry:
    for e in (".kicad_pro", ".kicad_prl"):
        s_ = os.path.splitext(bp)[0] + e
        if os.path.exists(s_): __import__("shutil").copy(s_, os.path.splitext(tmp)[0] + e)
pcbnew.SaveBoard(tmp, b)
j2 = os.path.splitext(tmp)[0] + "-zpv-drc.json"
subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "-o", j2, tmp], capture_output=True)
after = hardset(j2)
print("zone_pad_via: %d via(s) placed; hard %d -> %d, unrouted %d -> %d" % (len(made), before[0], after[0], before[1], after[1]))
if after[0] > before[0]:
    for v_ in made: b.Remove(v_)
    b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(tmp, b)
    print("zone_pad_via: the vias raised the hard count, all reverted"); sys.exit(1)
sys.exit(0 if after[1] == 0 else 1)
