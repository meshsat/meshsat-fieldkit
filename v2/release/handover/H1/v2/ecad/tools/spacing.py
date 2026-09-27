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



# ECSS-Q-ST-70-12C Table 13-3, TRANSCRIBED in v2/vendor/standards/ecss-q-st-70-12c-2014-07-14.md, the columns
# this project uses. The standard's own "AND" means both the per-volt figure and the floor apply, so the
# requirement is the larger of the two.
#
# WHY THE COATED COLUMN (decision 34, ruled 21 September 2026, the session's). Every ISO-001 number this
# project has recorded was read against "X,Y external WITHOUT conformal coating", and ASSEMBLY.md section 5
# has specified IPC-CC-830 acrylic, two thin coats, on A22, B16, D8, E6 and E5 since it was written. A board
# says whether it is coated and the column follows; a board that does not say is judged on the stricter
# column, because a declaration that cannot be found must never be the reason a rule gets easier.
#
# AND THE COATED ROW DISSOLVES THE TWO NUMBERS THAT HAD NO SOURCE. The envelope's altitude and the pollution
# degree were what ISO-001 was waiting for: this table is a SPACE standard's, stated for an as-manufactured
# rigid PCB without an altitude derating or a pollution degree, so the judgement holds at any altitude this
# kit can see. What it does NOT cover is a conductor at a point the coating is masked off: ASSEMBLY.md
# section 5 masks the connector faces, the spring-pin and pack targets, the RF bodies, the module and M.2
# receptacles and the test points, and a pair measured there is on the uncoated column. The verdict names
# the tightest pairs with their positions so that reading can be made.
ECSS_13_3 = {
    "external_coated":   lambda v: 0.120 if v <= 30 else max(0.002 * v, 0.160),
    "external_bare":     lambda v: (0.200 if v <= 10 else 0.300) if v <= 30 else max(0.005 * v, 0.500),
    "internal":          lambda v: 0.104 if v <= 30 else max(0.001 * v, 0.150),
}


def limit_for(volts, outer, coated):
    """The minimum insulation distance in mm for a working voltage, or None above the table's 500 V.

    Clause l: voltages above 500 V are subject to specific qualification of the design, so the table does not
    answer there and this says so rather than extrapolating."""
    v = max(0.0, float(volts or 0.0))
    if v > 500.0:
        return None
    if not outer:
        return ECSS_13_3["internal"](v)
    return ECSS_13_3["external_coated" if coated else "external_bare"](v)


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
    hv_v = {n.lstrip("/"): _vhi(r) for n, r in (it.get("rails") or {}).items() if _vhi(r) >= vmin}
    hv = set(hv_v)
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
    _letter = _bt.letter_for(path)
    lim = _bt.value(_letter, "hv_spacing_mm")
    coated = _bt.value(_letter, "conformal_coated")
    # PER VOLTAGE BAND AND PER LAYER, which is how the table is written. A board-wide scalar judged a 20 V bus
    # against a 36 V rail's floor and was the reason this rule could only ever be declared or unjudged.
    def _row(pair):
        return limit_for(hv_v.get(pair[1], 0.0), pair[3] in ("F.Cu", "B.Cu"), bool(coated))
    print("spacing: %d high-voltage net(s) (%s) against %d other conductor(s); %d pair(s) inside %.1f mm"
          % (len(hv), ", ".join(sorted(hv)), len(other), len(pairs), win))
    for d, n1, n2, L, p in pairs[:10]:
        print("  %.3f mm  %s to %s on %s at (%.1f, %.1f)" % (d, n1, n2, L, p[0], p[1]))
    if "--json" in a: print(json.dumps(pairs[:50], indent=1))
    worst = pairs[0][0] if pairs else None
    if lim is not None:
        bad = [x for x in pairs if x[0] < float(lim)]
        _basis = "the single spacing this board declares (%.3f mm)" % float(lim)
    elif coated is not None:
        bad = [x for x in pairs if _row(x) is not None and x[0] < _row(x)]
        _basis = ("ECSS-Q-ST-70-12C Table 13-3, per rail's working voltage and per layer, on the %s column "
                  "(this board declares conformal_coated: %s)" % ("coated" if coated else "bare", bool(coated)))
    else:
        bad = []
        _basis = None
    for x in pairs[:10]:
        r = _row(x)
        if r is not None and coated is not None:
            print("    %s at %.0f V wants %.3f mm on %s: %s" % (x[1], hv_v.get(x[1], 0.0), r, x[3],
                                                               "SHORT by %.3f mm" % (r - x[0]) if x[0] < r else "met"))
    return _v.write("spacing",
                    _v.INCONCLUSIVE if (lim is None and coated is None) else (_v.FAIL if bad else _v.PASS),
                    counts={"hv_nets": len(hv), "pairs_measured": len(pairs),
                            "closest_mm": worst, "below_limit": len(bad)},
                    denominator=len(pairs) or 1,
                    evidence=["%.3f mm %s to %s on %s at (%.1f, %.1f)" % (x[0], x[1], x[2], x[3], x[4][0], x[4][1])
                              for x in (bad or pairs)[:20]],
                    inputs={"board": path, "hv_spacing_mm": lim, "volts": vmin,
                            "conformal_coated": coated, "basis": _basis},
                    note=("measured, not judged: this board declares neither hv_spacing_mm nor whether it is "
                          "conformally coated, and the column of the table follows the coating"
                          if _basis is None else "every high-voltage conductor against " + _basis),
                    out_dir=out_dir)


if __name__ == "__main__":
    # EVERY GATE LEAVES A READING WHEN IT RAISES (18 September 2026). The thirteen one-line entries of this
    # morning were the gates a crash had already cost a verdict; these are the rest of the deciding gates in
    # the coverage map, guarded the same way, so a rule whose tool raised reads INCONCLUSIVE naming the
    # exception rather than 'no verdict', which the registry reads as nobody having looked.
    sys.exit(_v.guard("spacing", main, sys.argv[1:]))