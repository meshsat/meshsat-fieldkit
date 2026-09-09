#!/usr/bin/env python3
"""Reserve a slot beside each part for the decoupling capacitors it declares, BEFORE the region packer fills the board.

Owner ruling 9 September 2026 (appendix 32.74, option 3): every placement generator shelf-packed passives into region
rectangles in reference order, so a declared bypass capacitor landed wherever the packer reached. Measured on the
released set: not one capacitor of any board was within the 3 mm the gate asks for, and A22's worst two sat 117 and
121 mm from the pin they serve. `bypass_place.py` moves them afterwards and can only use space the packer left, which
on D9 was nine of sixteen. This runs first: the fixed parts are on the board, nothing else is, so every declared
capacitor takes the spot it needs and the packer works around them.

Call it from a placement generator between the FIXED placement and the region loop:

    import bypass_slots
    reserved = bypass_slots.reserve(board, place, to_case, entries)     # entries = intent's "bypass" list
    ... then skip `reserved` in every region's reference list ...

`place(ref, x, y, rot, back)` is the generator's own placer in case-frame mm; `to_case(vec)` converts a board
VECTOR2I to case-frame mm. A capacitor with no free spot within the limit is left for the packer and reported, so the
gate still sees it as far away rather than the tool pretending it fitted."""
import math, pcbnew

LIMIT = 3.0
_DETACHED = []   # KiCad 9: a footprint removed from the board must stay referenced in Python or the next FootprintLoad dies inside the IO plugin

def _courtyard(f):
    try:
        c = f.GetCourtyard(pcbnew.F_CrtYd if f.GetLayer() == pcbnew.F_Cu else pcbnew.B_CrtYd); bb = c.BBox()
        if bb.GetWidth() > 0: return bb
    except Exception: pass
    return f.GetBoundingBox(False, False)

def _fine(f):
    """A part whose pads are 0.7 mm apart or closer needs its escape fan, and a capacitor parked in it costs that part its pins."""
    ps = [q.GetPosition() for q in f.Pads() if q.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    best = 1e9
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            d = math.hypot(ps[i].x - ps[j].x, ps[i].y - ps[j].y)
            if 0 < d < best: best = d
    return best <= pcbnew.FromMM(0.7)

def reserve(board, place, to_case, entries, limit=LIMIT, quiet=False, fan=2.2):
    """Places each declared capacitor beside its pin. Returns the set of references it placed."""
    if not entries: return set()
    edge = board.GetBoardEdgesBoundingBox()
    rule = [z for z in board.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowFootprints()]   # only a no-footprint area blocks a part
    # D10 and C9, 9 September 2026: the first floor-plan pass put capacitors 1 mm from QFN and ZIF pins, and the escape pass then had no
    # room for the fans: U7 lost 6 of 17 pads, C9's U3 lost 23 of 57. A fine-pitch part's fan is not free space, so its courtyard grown by
    # `fan` mm is closed to this pass. A capacitor that cannot be served outside every fan is named, not forced.
    fans = []
    for g in board.GetFootprints():
        if _fine(g):
            box = pcbnew.BOX2I(_courtyard(g).GetOrigin(), _courtyard(g).GetSize()); box.Inflate(int(pcbnew.FromMM(fan)))
            fans.append((g.GetReference(), box))
    done, stuck, report = set(), [], []
    for e in entries:
        cap, ref, pin = e.get("cap"), e.get("part"), str(e.get("pin"))
        if not cap or cap in done: continue
        p = board.FindFootprintByReference(ref)
        if p is None: stuck.append((cap, ref, pin, "its part is not placed yet")); continue
        pad = next((q for q in p.Pads() if q.GetNumber() == pin), None)
        if pad is None: stuck.append((cap, ref, pin, "no such pin")); continue
        pc = pad.GetPosition(); side = p.GetLayer(); pcy = _courtyard(p)
        cx, cy = to_case(pc)
        fp = place(cap, cx, cy, 0.0, side != pcbnew.F_Cu)   # on the part's own side, then walked out to a free spot
        cyd = _courtyard(fp); w, h = cyd.GetWidth(), cyd.GetHeight()
        def free(at):
            box = pcbnew.BOX2I(pcbnew.VECTOR2I(at.x - w // 2, at.y - h // 2), pcbnew.VECTOR2I(w, h))
            if not edge.Contains(box): return False
            for g in board.GetFootprints():
                if g.GetReference() in (cap,) or g.GetLayer() != fp.GetLayer(): continue
                if _courtyard(g).Intersects(box): return False
            for _r, fb in fans:
                if fb.Intersects(box): return False
            for z in rule:
                if z.GetBoundingBox().Intersects(box): return False
            return True
        out = (pc.x - p.GetPosition().x, pc.y - p.GetPosition().y)
        n = math.hypot(*out) or 1.0; ux, uy = out[0] / n, out[1] / n
        spot = None
        for r10 in range(8, int(limit * 10) + 1):
            r = pcbnew.FromMM(r10 / 10.0)
            for ang in range(0, 360, 10):
                th = math.radians(ang); dx, dy = ux * math.cos(th) - uy * math.sin(th), ux * math.sin(th) + uy * math.cos(th)
                at = pcbnew.VECTOR2I(int(pc.x + dx * r), int(pc.y + dy * r))
                if pcy.Contains(at): continue                      # never inside the part it serves
                if free(at): spot = (at, r10 / 10.0); break
            if spot: break
        if spot is None:
            board.Remove(fp); _DETACHED.append(fp); stuck.append((cap, ref, pin, "no free spot within %.1f mm" % limit)); continue
        fp.SetPosition(spot[0]); done.add(cap); report.append((cap, ref, pin, spot[1]))
    if not quiet:
        print("bypass_slots: %d of %d declared capacitors reserved a slot within %.1f mm of their pin" % (len(done), len({e.get("cap") for e in entries}), limit))
        for cap, ref, pin, d in report[:6]: print("bypass_slots:   %-6s beside %s.%-3s at %.1f mm" % (cap, ref, pin, d))
        for cap, ref, pin, why in stuck: print("bypass_slots:   LEFT TO THE PACKER %-6s for %s.%-3s: %s" % (cap, ref, pin, why))
    return done
