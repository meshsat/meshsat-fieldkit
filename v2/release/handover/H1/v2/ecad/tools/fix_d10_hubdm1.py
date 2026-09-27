#!/usr/bin/env python3
"""Close D10's last connection, /HUB_DM1, by hand (12 September 2026, MESHSAT-862; the C7 and A22 precedent).

The router got the net to within 0.28 mm and stopped: `/HUB_DM1` leaves U4 pad 11 northward, takes a via at
(120.85, 89.35) down to In2, runs south-east and ENDS at (121.35, 92.75) with no via back up, while its
destination R13 pad 1 sits at (121.60, 92.88). Three attempts to make the router finish it failed and are in
the record (32.128, 32.132): the stub router with a six-fold window on three layers, 1.2 mm more room at the
station (which costs a pair), and three times the passes.

So it is closed the way this project closes a last connection: a locked via where the inner track ends and a
locked track from it to the pad, then the whole gate set on the result. Nothing here is a rule change; the DRC
decides, as it did for A22's VBUS20 and C7's U3 ring.

Usage: fix_d10_hubdm1.py <board.kicad_pcb> [--test]   -> writes the board (or <board>-hand.kicad_pcb) and prints the counts."""
import sys, os, math, json, subprocess, pcbnew
from pcbnew import VECTOR2I, FromMM
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hardset

NET = "/HUB_DM1"; DEST = ("R13", "1"); W = 0.25; VD, VDR = 0.45, 0.25
bp = sys.argv[1]; test = "--test" in sys.argv
# A test copy goes in out/, never beside the board: a project directory that holds a second board is the B5
# trap of 11 September, where a nine-day-old file sorted first and a wave script exported a BOM from it.
# tests/test_driver_hygiene.py caught this one before it was committed (12 September 2026).
_od = os.path.join(os.path.dirname(os.path.abspath(bp)) or ".", "out")
if test: os.makedirs(_od, exist_ok=True)
out = os.path.join(_od, os.path.basename(os.path.splitext(bp)[0]) + "-hand.kicad_pcb") if test else bp
b = pcbnew.LoadBoard(bp); mm = pcbnew.ToMM

pad = next((q for f in b.GetFootprints() if f.GetReference() == DEST[0] for q in f.Pads() if q.GetNumber() == DEST[1]), None)
if pad is None: sys.exit("fix_d10: no pad %s.%s" % DEST)
px, py = mm(pad.GetPosition().x), mm(pad.GetPosition().y)

# the end of the net's inner-layer copper that is nearest the pad, and it must be an END (one track only)
ends = []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA" or t.GetNetname() != NET or t.GetLayer() == pcbnew.F_Cu: continue
    for p in (t.GetStart(), t.GetEnd()):
        ends.append((math.hypot(mm(p.x) - px, mm(p.y) - py), mm(p.x), mm(p.y), t.GetLayer()))
if not ends: sys.exit("fix_d10: %s has no inner-layer copper" % NET)
d, ex, ey, L = min(ends)
print("fix_d10: %s ends on %s at (%.2f, %.2f), %.2f mm from %s.%s at (%.2f, %.2f)" % (NET, b.GetLayerName(L), ex, ey, d, DEST[0], DEST[1], px, py))
if d > 1.5: sys.exit("fix_d10: that end is %.2f mm away, which is not the closure this script is for" % d)

net = pad.GetNet()
v = pcbnew.PCB_VIA(b); v.SetPosition(VECTOR2I(FromMM(ex), FromMM(ey))); v.SetWidth(FromMM(VD)); v.SetDrill(FromMM(VDR))
v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net); v.SetLocked(True); b.Add(v)
t = pcbnew.PCB_TRACK(b); t.SetStart(VECTOR2I(FromMM(ex), FromMM(ey))); t.SetEnd(pad.GetPosition())
t.SetWidth(FromMM(W)); t.SetLayer(pcbnew.F_Cu); t.SetNet(net); t.SetLocked(True); b.Add(t)
print("fix_d10: 1 locked via at (%.2f, %.2f) and 1 locked track of %.2f mm to the pad" % (ex, ey, W))

b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(out, b)
drc = os.path.join(os.path.dirname(os.path.abspath(out)) or ".", "out", os.path.basename(os.path.splitext(out)[0]) + "-hand-drc.json")
os.makedirs(os.path.dirname(drc), exist_ok=True)
subprocess.run(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "-o", drc, out], capture_output=True)
txt = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "hardset.py"), drc, "post"], capture_output=True, text=True).stdout
print("fix_d10: " + (txt.strip().splitlines() or ["no hardset output"])[0])
