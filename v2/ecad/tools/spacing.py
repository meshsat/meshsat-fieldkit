#!/usr/bin/env python3
"""How far apart the high-voltage copper actually is (rule ISO-001, MESHSAT-862, 16 September 2026).

The registry's note has read "an HV net class widens the clearance on the PoE nets; no creepage or clearance
distance has ever been measured" since the audit. A net class is an instruction to the router; it is not a
measurement of the board, and the two differ wherever a pad, a zone edge or a hand-laid piece of copper is
involved, because a class clearance binds the router's tracks and not the shapes a generator drew.

This MEASURES, per board: the smallest distance from every conductor of a declared high-voltage net to the
nearest conductor of any other net, on the same layer, including pads and filled zones. It reports the ten
tightest with their positions and the nets involved.

WHAT IT DOES NOT DO, and this is the half that matters for the rule: it does not say whether the number is
ENOUGH. Creepage and clearance come from a standard's table for a working voltage, a pollution degree and a
material group, and IEC 60664-1 is not in this tree. The board declares `hv_spacing_mm` when it has an
authority for it and the verdict is judged against that; where nothing is declared the measurement is reported
and the rule stays unjudged, which is what "no source" has to mean if the registry means anything.

Usage: spacing.py <board.kicad_pcb> [--volts 20] [--window 5] [--json]
"""
import os, sys, json, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v
import boardtable as _bt


def seg_dist(p, q, r, s):
    """Distance between two segments, each given as endpoints.

    The endpoint-to-segment minimum is the answer ONLY when the segments do not cross: two crossing segments
    have four endpoints that can all be far from the other segment, and the first version of this returned
    5 mm for a pair that touch at their middle (16 September 2026, caught by its own fixture before it ever
    judged a board). Crossing is tested first and reads zero."""
    def pt_seg(px, py, ax, ay, bx, by):
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

    def side(o, a, c): return (a[0] - o[0]) * (c[1] - o[1]) - (a[1] - o[1]) * (c[0] - o[0])
    d1, d2 = side(r, s, p), side(r, s, q)
    d3, d4 = side(p, q, r), side(p, q, s)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)): return 0.0
    return min(pt_seg(p[0], p[1], r[0], r[1], s[0], s[1]), pt_seg(q[0], q[1], r[0], r[1], s[0], s[1]),
               pt_seg(r[0], r[1], p[0], p[1], q[0], q[1]), pt_seg(s[0], s[1], p[0], p[1], q[0], q[1]))


def main(a):
    if not a: print(__doc__); return _v.USAGE
    path = a[0]
    vmin = float(a[a.index("--volts") + 1]) if "--volts" in a else 20.0
    win = float(a[a.index("--window") + 1]) if "--window" in a else 5.0
    import pcbnew, intent
    mm = lambda v: v / 1e6
    b = pcbnew.LoadBoard(path)
    it = intent.load(path) or {}
    # THE WORKING VOLTAGE, NEVER THE NOMINAL (17 September 2026). ISO-001 asks for spacing at the voltage a
    # conductor pair actually stands off, and the standard this project cites says so in as many words: ECSS
    # clause 13.8.2 b, "voltage rating shall apply to the worst-case peak transient voltage". The intent has
    # carried `v_work` per rail since it was written, and this read `volts`: board E's shore and vehicle inlet
    # is 12 V nominal and **36 V working**, so the board whose own fact declares 36 V read "no rail on this
    # board reaches 20 V" and ISO-001 was answered about nothing on the one board of the three that carries a
    # wide-range input. A nominal is what a rail sits at; a working voltage is what the copper has to survive.
    def _vhi(r):
        return max(float(r.get("volts") or 0), float(r.get("v_work") or 0))
    hv = {n.lstrip("/") for n, r in (it.get("rails") or {}).items() if _vhi(r) >= vmin}
    out_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "out")
    if not hv:
        # AND A BOARD'S OWN FACT MAY CONTRADICT ITS INTENT, in which case this is a question and never a pass.
        # The registry decides that ISO-001 applies to a board from `max_rail_voltage_v` in pcb_board_facts.yaml;
        # if that says 36 and no rail in the intent reaches the threshold, one of the two is wrong and the rule
        # is unanswered, which is what INCONCLUSIVE with a missing input is for.
        declared = 0.0
        try:
            import rules_lib as _rl
            _l = _bt.letter_for(path)
            declared = float((_rl.board_facts().get(_l) or {}).get("max_rail_voltage_v") or 0)
        except Exception:
            declared = 0.0
        if declared >= vmin:
            msg = ("this board's facts declare %.0f V and no rail in its intent reaches %.0f: one of the two "
                   "is wrong and ISO-001 cannot be judged until they agree" % (declared, vmin))
            print("spacing: " + msg)
            return _v.write("spacing", _v.INCONCLUSIVE, denominator=0, inputs={"board": path},
                            missing_input=msg, note=msg, out_dir=out_dir)
        print("spacing: this board declares no rail at or above %.0f V, so ISO-001 has nothing on it to judge" % vmin)
        return _v.write("spacing", _v.INCONCLUSIVE, denominator=0, inputs={"board": path}, applicable=False,
                        note="no rail on this board reaches %.0f V" % vmin, out_dir=out_dir)

    # every conductor as (net, layer, segment or point, radius)
    items = []
    for t in b.GetTracks():
        n = t.GetNetname().lstrip("/")
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition(); r = mm(t.GetWidth(pcbnew.F_Cu)) / 2
            for L in (pcbnew.F_Cu, pcbnew.B_Cu): items.append((n, L, (mm(p.x), mm(p.y)), (mm(p.x), mm(p.y)), r))
        else:
            s, e = t.GetStart(), t.GetEnd()
            items.append((n, t.GetLayer(), (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y)), mm(t.GetWidth()) / 2))
    # A PAD IS A FAT SEGMENT, NOT A CIRCLE OF ITS LONGEST SIDE (16 September 2026). The first run on board A
    # reported a closest distance of 0.000 mm between its high-voltage nets and everything else, on a board
    # whose DRC reads hard 0: a 1.7 by 1.0 pad modelled as a circle has a radius of 0.85 where its real half
    # width across the short axis is 0.5, so it swallowed the tracks beside it. The centre line plus the short
    # half width is exactly an oval pad and close enough for a rectangle, which is what KiCad draws.
    for f in b.GetFootprints():
        for p in f.Pads():
            n = p.GetNetname().lstrip("/"); c = p.GetPosition(); sz = p.GetSize()
            sx, sy = mm(sz.x), mm(sz.y)
            r = min(sx, sy) / 2.0
            half = max(0.0, (max(sx, sy) - min(sx, sy)) / 2.0)
            ang = math.radians(p.GetOrientationDegrees() + (0.0 if sx >= sy else 90.0))
            dx, dy = half * math.cos(ang), -half * math.sin(ang)
            a_pt = (mm(c.x) - dx, mm(c.y) - dy); b_pt = (mm(c.x) + dx, mm(c.y) + dy)
            for L in (pcbnew.F_Cu, pcbnew.B_Cu):
                if p.IsOnLayer(L): items.append((n, L, a_pt, b_pt, r))
    hv_items = [i for i in items if i[0] in hv]
    other = [i for i in items if i[0] not in hv and i[0]]
    pairs = []
    for h in hv_items:
        for o in other:
            if o[1] != h[1]: continue
            if abs(h[2][0] - o[2][0]) > win + h[4] + o[4] and abs(h[3][0] - o[3][0]) > win + h[4] + o[4]: continue
            if abs(h[2][1] - o[2][1]) > win + h[4] + o[4] and abs(h[3][1] - o[3][1]) > win + h[4] + o[4]: continue
            d = seg_dist(h[2], h[3], o[2], o[3]) - h[4] - o[4]
            if d < win: pairs.append((round(max(d, 0.0), 4), h[0], o[0], b.GetLayerName(h[1]), h[2]))
    pairs.sort()
    lim = _bt.value(_bt.letter_for(path), "hv_spacing_mm")
    print("spacing: %d high-voltage net(s) (%s) against %d other conductor(s); %d pair(s) inside %.1f mm"
          % (len(hv), ", ".join(sorted(hv)), len(other), len(pairs), win))
    for d, n1, n2, L, p in pairs[:10]:
        print("  %.3f mm  %s to %s on %s at (%.1f, %.1f)" % (d, n1, n2, L, p[0], p[1]))
    if "--json" in a: print(json.dumps(pairs[:50], indent=1))
    worst = pairs[0][0] if pairs else None
    bad = [x for x in pairs if lim is not None and x[0] < float(lim)]
    return _v.write("spacing",
                    _v.INCONCLUSIVE if lim is None else (_v.FAIL if bad else _v.PASS),
                    counts={"hv_nets": len(hv), "pairs_measured": len(pairs),
                            "closest_mm": worst, "below_limit": len(bad)},
                    denominator=len(pairs) or 1,
                    evidence=["%.3f mm %s to %s on %s at (%.1f, %.1f)" % (x[0], x[1], x[2], x[3], x[4][0], x[4][1])
                              for x in (bad or pairs)[:20]],
                    inputs={"board": path, "hv_spacing_mm": lim, "volts": vmin},
                    note=("measured, not judged: this board declares no hv_spacing_mm, and creepage and clearance "
                          "come from a standard's table for a working voltage, a pollution degree and a material "
                          "group, which this tree does not hold" if lim is None else
                          "every high-voltage conductor against the spacing this board declares"),
                    out_dir=out_dir)


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
