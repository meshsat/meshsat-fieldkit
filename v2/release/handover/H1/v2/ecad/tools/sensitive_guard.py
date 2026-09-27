#!/usr/bin/env python3
"""Keep the router away from a sensitive node's copper (rule ANA-001, MESHSAT-862, 16 September 2026).

WHAT THE BOARD SAYS AND WHAT IT GETS. `pcb_sensitive.yaml` declares nineteen nodes on board A, each with the
distance it wants from switching copper, and six of them are routed between 0.18 and 0.36 mm from a switch
node. Nothing enforces the distance: the router honours the NET CLASS clearance, which is 0.127 mm on this
board, and a class clearance is the wrong instrument because it applies between every pair of nets on the
board and a current-sense line only wants distance from one kind of neighbour.

WHAT THIS DOES. It draws a keep-out band around each sensitive net's already-laid copper, on the layers that
copper is on, and it draws it ON A COPY: route_one.sh exports the DSN from a temporary board with the planes
removed, and this writes into that temporary board only. So the band reaches the ROUTER, which is the thing
that needs to keep away, and never reaches the real board, its DRC or its fabrication outputs.

THREE THINGS IT MUST NOT DO, each learnt from a keep-out that cost connections (appendix 32.197, 15 Sep 2026):
  * it must not cover the sensitive net's OWN copper, or the router cannot finish that net: the band is an
    annulus, the net's own copper grown by the board's clearance subtracted from it;
  * it must not cover a FOREIGN PAD, because a pad inside a track keep-out is an escape the router can no
    longer make: every pad of another net inside the band is punched out of it with a margin;
  * it must not be drawn where the sensitive net has no copper at all, because a band around nothing is a
    band around the whole board.

Usage: sensitive_guard.py <board.kicad_pcb> <letter> [--clearance 0.127] [--dry]
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def nodes_for(letter):
    import yaml
    d = yaml.safe_load(open(os.path.join(HERE, "pcb_sensitive.yaml"), encoding="utf-8")) or {}
    d = d.get("boards", d)
    return ((d.get((letter or "").lower()) or {}).get("nodes") or [])


def main(argv):
    if len(argv) < 2: print(__doc__); return 2
    import pcbnew
    from pcbnew import FromMM
    path, letter = argv[0], argv[1]
    # THE LETTER IS RESOLVED FROM THE BOARD, NOT FROM ITS NAME (17 September 2026). A caller that slices the
    # letter out of a stem with a pattern gets "e1" for pcb-e1-dock, whose letter is "e", and "e5" for the one
    # board whose letter really is e5; the guard would then find no declaration and silently do nothing. The
    # board table is the one place that knows, and the argument stays as the fallback for a board it has never
    # heard of.
    try:
        import boardtable as _bt
        letter = _bt.letter_for(path) or _bt.letter_for(os.path.basename(path).split(".")[0]) or letter
    except Exception:
        pass
    clr = float(argv[argv.index("--clearance") + 1]) if "--clearance" in argv else 0.127
    dry = "--dry" in argv
    nodes = nodes_for(letter)
    if not nodes:
        print("sensitive_guard: board %s declares no sensitive node" % letter.upper())
        return 0
    b = pcbnew.LoadBoard(path)
    want = {str(n["net"]).lstrip("/"): float(n.get("keep_mm") or 0.0) for n in nodes if n.get("keep_mm")}
    segs = {}
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK": continue
        nm = t.GetNetname().lstrip("/")
        if nm in want: segs.setdefault((nm, t.GetLayer()), []).append(t)
    if not segs:
        print("sensitive_guard: none of board %s's %d sensitive nodes carries copper on this board, so there is "
              "nothing to draw a band around (pre-lay them first)" % (letter.upper(), len(want)))
        return 0
    pads = [p for fp in b.GetFootprints() for p in fp.Pads()]
    made = 0
    for (nm, layer), pieces in sorted(segs.items()):
        keep = want[nm]
        band = pcbnew.SHAPE_POLY_SET(); own = pcbnew.SHAPE_POLY_SET()
        for t in pieces:
            a, e = t.GetStart(), t.GetEnd(); w = t.GetWidth()
            for target, grow in ((band, keep), (own, clr)):
                seg = pcbnew.SHAPE_POLY_SET()
                seg.NewOutline()
                # a rectangle around the segment, then inflated: KiCad's own inflate rounds the ends
                seg.Append(a.x, a.y); seg.Append(e.x, e.y); seg.Append(e.x, e.y); seg.Append(a.x, a.y)
                seg.Inflate(int(w / 2 + FromMM(grow)), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, FromMM(0.01))
                target.BooleanAdd(seg)
        band.BooleanSubtract(own)
        # every foreign pad inside the band is punched out with a margin, or its escape is refused
        punched = 0
        for p in pads:
            if p.GetNetname().lstrip("/") == nm: continue
            if not p.IsOnLayer(layer): continue
            c = p.GetPosition()
            if not band.Contains(pcbnew.VECTOR2I(c.x, c.y)): continue
            hole = pcbnew.SHAPE_POLY_SET(p.GetEffectivePolygon(layer))
            hole.Inflate(FromMM(0.3), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, FromMM(0.01))
            band.BooleanSubtract(hole)
            punched += 1
        band.Simplify()
        if band.OutlineCount() == 0: continue
        if dry:
            print("sensitive_guard: %s on %s would take %d outline(s), %d foreign pad(s) punched out"
                  % (nm, b.GetLayerName(layer), band.OutlineCount(), punched))
            made += 1
            continue
        z = pcbnew.ZONE(b)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(False)
        z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
        z.SetLayer(layer)
        # THE POINTS GO INTO THE ZONE'S OWN OUTLINE, NEVER A POLYGON HANDED TO IT. `SetOutline(poly)` takes
        # ownership of a Python-owned SHAPE_POLY_SET and the board then frees it twice: the first version of
        # this segfaulted at the save, silently, after printing every band it had computed (16 September 2026,
        # and it is the second segfault of the day from KiCad's C++ ownership rules).
        o = z.Outline(); o.RemoveAllContours()
        for i in range(band.OutlineCount()):
            ol = band.Outline(i); o.NewOutline()
            for k in range(ol.PointCount()):
                q = ol.CPoint(k); o.Append(q.x, q.y)
            for hh in range(band.HoleCount(i)):
                hl = band.Hole(i, hh); hidx = o.NewHole(i)
                for k in range(hl.PointCount()):
                    q = hl.CPoint(k); o.Append(q.x, q.y, i, hidx)
        z.SetZoneName("sensitive %s keep %.2f mm" % (nm, keep))
        b.Add(z); made += 1
        print("sensitive_guard: %s on %s, %.2f mm band, %d outline(s), %d foreign pad(s) punched out"
              % (nm, b.GetLayerName(layer), keep, band.OutlineCount(), punched))
    if made and not dry:
        pcbnew.SaveBoard(path, b)
    print("sensitive_guard: %d band(s) %s on %s" % (made, "computed" if dry else "written", os.path.basename(path)))
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
