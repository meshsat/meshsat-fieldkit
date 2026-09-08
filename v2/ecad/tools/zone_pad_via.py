#!/usr/bin/env python3
"""Close a pad that its own plane cannot reach (MESHSAT-862, 8 Sep 2026).

After the route and the fill, KiCad reports "Pad 31 [GND] of U4 / Zone GND pour" as an unconnected item when the tracks
around a fine-pitch pin cut the pour off from it. The closure this board family already ships is a via down to the solid
inner plane: D8 went out with six ground vias in pads.

For every such open item on a net that has a filled zone this pass tries, in order, a via inside the pad at its outboard
tip, then a via just past the tip with a locked leg from the pad (the dogbone escape.py uses, for a pin too narrow to
hold a via: a 0.5 mm pad leaves 0.025 mm beside a 0.45 mm via and the clearance check refuses it). Each candidate is
accepted only if it closes something without raising the hard count, the way stub_accept.py keeps the stub router's good
closures; the first that sticks wins and the rest of that pad's candidates are dropped.

The board is refilled and re-read before anything is measured: the finish refills later, so a DRC handed in can be a fill
behind the board and the items this pass exists for are not in it.

Usage: zone_pad_via.py <board.kicad_pcb> <drc.json> [--via=0.45/0.25] [--dry]   -> exit 0 when no such item is left."""
import sys, os, re, json, subprocess, pcbnew

bp, drcp = sys.argv[1], sys.argv[2]
opt = next((a.split("=", 1)[1] for a in sys.argv[3:] if a.startswith("--via=")), None)
dry = "--dry" in sys.argv
b = pcbnew.LoadBoard(bp); mm = lambda v: v / 1e6
ds = b.GetDesignSettings()
VD, VDR = ((float(v) for v in opt.split("/")) if opt else (max(0.45, mm(ds.m_ViasMinSize)), max(0.25, mm(ds.m_MinThroughDrill))))
tmp = os.path.splitext(bp)[0] + ("-zpv.kicad_pcb" if dry else ".kicad_pcb")
if dry:
    for e in (".kicad_pro", ".kicad_prl"):
        s_ = os.path.splitext(bp)[0] + e
        if os.path.exists(s_): __import__("shutil").copy(s_, os.path.splitext(tmp)[0] + e)
j2 = os.path.splitext(tmp)[0] + "-zpv-drc.json"
TOOLS = os.path.dirname(os.path.abspath(__file__))

def measure(path, out):
    """Refill, save, run the DRC and return (hard, unrouted)."""
    b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(path, b)
    subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "-o", out, path], capture_output=True)
    txt = subprocess.run([sys.executable, os.path.join(TOOLS, "hardset.py"), out, "post"], capture_output=True, text=True).stdout
    m = re.search(r"hard (\d+) of", txt); u = re.search(r"unrouted (\d+)", txt)
    return (int(m.group(1)) if m else -1, int(u.group(1)) if u else -1)

before = measure(tmp, j2)
want = []
for v in json.load(open(j2)).get("unconnected_items", []):
    descs = [i.get("description", "") for i in v.get("items", [])]
    if not any(d.startswith("Zone") for d in descs): continue
    for d in descs:
        m = re.match(r"Pad (\S+) \[([^\]]*)\] of (\S+)", d)
        if m: want.append((m.group(3), m.group(1), m.group(2)))
if not want:
    print("zone_pad_via: no pad-to-zone item on the filled board (hard %d, unrouted %d)" % before); sys.exit(0 if before[1] == 0 else 1)

def candidates(ref, pn):
    """(via, leg or None) in the order to try: inside the pad at its outboard tip, then past the tip with a leg."""
    f = b.FindFootprintByReference(ref)
    if f is None: return []
    p = next((q for q in f.Pads() if q.GetNumber() == pn), None)
    if p is None or p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH: return []
    px, py = mm(p.GetPosition().x), mm(p.GetPosition().y); fx, fy = mm(f.GetPosition().x), mm(f.GetPosition().y)
    sx, sy = mm(p.GetSize().x), mm(p.GetSize().y)
    ax = (1.0, 0.0) if sx > sy else (0.0, 1.0)
    s = 1.0 if (px - fx) * ax[0] + (py - fy) * ax[1] >= 0 else -1.0
    tip = max(sx, sy) / 2
    steps = ([tip - VD / 2 - 0.05] if min(sx, sy) >= VD + 0.04 else []) + [tip + VD / 2 + g for g in (0.15, 0.35, 0.55, 0.8)]
    out = []
    for step in steps:
        vx, vy = px + s * ax[0] * step, py + s * ax[1] * step
        v_ = pcbnew.PCB_VIA(b); v_.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(vx), pcbnew.FromMM(vy)))
        v_.SetWidth(pcbnew.FromMM(VD)); v_.SetDrill(pcbnew.FromMM(VDR)); v_.SetViaType(pcbnew.VIATYPE_THROUGH)
        v_.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v_.SetNet(p.GetNet()); v_.SetLocked(True)
        leg = None
        if step > tip:
            L_ = next((L for L in (pcbnew.F_Cu, pcbnew.B_Cu) if p.IsOnLayer(L)), pcbnew.F_Cu)
            leg = pcbnew.PCB_TRACK(b); leg.SetStart(p.GetPosition()); leg.SetEnd(v_.GetPosition())
            leg.SetWidth(pcbnew.FromMM(min(0.25, min(sx, sy)))); leg.SetLayer(L_); leg.SetNet(p.GetNet()); leg.SetLocked(True)
        out.append((v_, leg, vx, vy))
    return out

closed = 0; stuck = 0; cur = before
for ref, pn, net in want:
    cands = candidates(ref, pn)
    if not cands: print("zone_pad_via: %s.%s is not a placeable SMD pad, left open" % (ref, pn)); stuck += 1; continue
    done = False
    for v_, leg, vx, vy in cands:
        b.Add(v_)
        if leg is not None: b.Add(leg)
        st = measure(tmp, j2)
        if st[0] <= cur[0] and st[1] < cur[1]:
            print("zone_pad_via: %s.%s [%s] closed by a via at %.3f, %.3f%s" % (ref, pn, net, vx, vy, "" if leg is None else " with a leg from the pad"))
            cur = st; closed += 1; done = True; break
        b.Remove(v_)
        if leg is not None: b.Remove(leg)
    if not done: print("zone_pad_via: %s.%s [%s] no candidate closed it without cost (%d tried)" % (ref, pn, net, len(cands))); stuck += 1
final = measure(tmp, j2)
print("zone_pad_via: %d of %d pad-to-zone item(s) closed, %d left; hard %d -> %d, unrouted %d -> %d" % (closed, len(want), stuck, before[0], final[0], before[1], final[1]))
sys.exit(0 if final[1] == 0 else 1)
