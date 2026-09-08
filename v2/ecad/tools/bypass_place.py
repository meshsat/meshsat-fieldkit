#!/usr/bin/env python3
"""Put every declared decoupling capacitor next to the pin it serves (MESHSAT-862 Stage C, 8 Sep 2026).

The audit's finding W2 was that the placement generators shelf-pack the capacitors into a rectangle by reference number
with no proximity rule at all. With the bypass entries of `intent.py` declared, that stopped being an assertion: on D9
every declared capacitor sat 8 to 22 mm from the pin it bypasses, against the 3 mm the gate asks for. A 100 nF at 13 mm
is loop inductance, not decoupling.

This pass moves each declared capacitor to the first free spot within LIMIT mm of its pin: on the part's own side, just
past the pin, walking outward and around; the capacitor keeps its orientation and only its position changes. A spot is
free when the capacitor's courtyard clears every other footprint's courtyard on that side, every rule area and the board
edge. It runs after the placement generator and before the escapes, and it reports moved, already close, and stuck.

Usage: bypass_place.py <board.kicad_pcb> [--limit 3.0] [--dry]   -> exit 1 when one is stuck (a placement question)."""
import sys, os, json, math, pcbnew

LIMIT = 3.0
def mm(v): return v / 1e6
def FM(v): return pcbnew.FromMM(v)

def courtyard(f):
    try:
        c = f.GetCourtyard(pcbnew.F_CrtYd if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd); bb = c.BBox()
        if bb.GetWidth() > 0: return bb
    except Exception: pass
    return f.GetBoundingBox(False, False)

def main(a):
    if not a: print(__doc__); return 2
    bp = a[0]; limit = float(a[a.index("--limit") + 1]) if "--limit" in a else LIMIT
    dry = "--dry" in a
    b = pcbnew.LoadBoard(bp)
    ip = os.path.join(os.path.dirname(os.path.abspath(bp)) or ".", "out", os.path.splitext(os.path.basename(bp))[0] + "-intent.json")
    if not os.path.exists(ip): print("bypass_place: no intent file at %s, nothing declared" % ip); return 0
    entries = json.load(open(ip)).get("bypass", [])
    if not entries: print("bypass_place: 0 bypass entries declared, nothing to place"); return 0
    edge = b.GetBoardEdgesBoundingBox()
    # only a rule area that forbids FOOTPRINTS blocks a placement; the board-wide "no tracks on In1" and edge-band areas cover
    # every spot on the board and are about copper, not parts (8 Sep 2026: testing every rule area made all 16 capacitors "stuck")
    rule = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowFootprints()]
    def blocked(f, at, side):
        """The capacitor's courtyard at `at` against every other footprint on that side, the rule areas and the edge."""
        cy = courtyard(f); w, h = cy.GetWidth(), cy.GetHeight()
        box = pcbnew.BOX2I(pcbnew.VECTOR2I(at.x - w // 2, at.y - h // 2), pcbnew.VECTOR2I(w, h))
        if not edge.Contains(box): return "off the board"
        for g in b.GetFootprints():
            if g.GetReference() == f.GetReference() or g.GetLayer() != side: continue
            if courtyard(g).Intersects(box): return g.GetReference()
        for z in rule:
            if z.GetBoundingBox().Intersects(box) and z.HitTestFilledArea(z.GetFirstLayer(), pcbnew.VECTOR2I(at.x, at.y), 0): return "rule area " + (z.GetZoneName() or "")
        return None
    moved = near = stuck = 0
    for e in entries:
        f = b.FindFootprintByReference(e["cap"]); p = b.FindFootprintByReference(e["part"])
        if f is None or p is None: print("bypass_place: %s or %s not on the board" % (e["cap"], e["part"])); stuck += 1; continue
        pin = next((q for q in p.Pads() if q.GetNumber() == str(e["pin"])), None)
        if pin is None: print("bypass_place: %s has no pin %s" % (e["part"], e["pin"])); stuck += 1; continue
        pc = pin.GetPosition(); d0 = mm(math.hypot(f.GetPosition().x - pc.x, f.GetPosition().y - pc.y))
        if d0 <= limit: near += 1; continue
        side = p.GetLayer()
        pcy = courtyard(p); out = (pc.x - p.GetPosition().x, pc.y - p.GetPosition().y)
        n = math.hypot(*out) or 1.0; ux, uy = out[0] / n, out[1] / n
        best = None
        for r in [x / 10.0 for x in range(10, int(limit * 10) + 1)]:
            for ang in range(0, 360, 10):
                th = math.radians(ang); dx, dy = ux * math.cos(th) - uy * math.sin(th), ux * math.sin(th) + uy * math.cos(th)
                at = pcbnew.VECTOR2I(int(pc.x + dx * FM(r)), int(pc.y + dy * FM(r)))
                if pcy.Contains(at): continue                      # never inside the part it serves
                if blocked(f, at, side) is None: best = (at, r); break
            if best: break
        if not best: print("bypass_place: STUCK %s -> %s.%s, no free spot within %.1f mm (it sits %.1f mm away)" % (e["cap"], e["part"], e["pin"], limit, d0)); stuck += 1; continue
        if f.GetLayer() != side: f.Flip(f.GetPosition(), False)
        if not dry: f.SetPosition(best[0])
        print("bypass_place: %-5s -> %s.%-3s %5.1f mm to %.1f mm" % (e["cap"], e["part"], e["pin"], d0, best[1]))
        moved += 1
    print("bypass_place: %d moved, %d already within %.1f mm, %d stuck of %d declared" % (moved, near, limit, stuck, len(entries)))
    if moved and not dry: pcbnew.SaveBoard(bp, b)
    return 1 if stuck else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
