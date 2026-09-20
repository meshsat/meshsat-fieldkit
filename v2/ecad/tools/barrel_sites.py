#!/usr/bin/env python3
"""Where a rail's over-rated layer transition is, and what is standing around it (a REPORT, 18 September 2026).

Rule PI-003 names a barrel that carries more current than its own wall is rated for, and `via_parallel.py` can
lay a second barrel beside it AFTER the route. On board D that fixer found no linkable site within 6 mm and the
record's answer became "D's PI-003 is the generator's": the generator does not have to search, because it knows
where the parts are, and locked copper between two pads of the same net with three barrels stitched into it
divides the current before any router sees the board (D15, 18 September 2026).

Doing that by hand took four readings: which barrel is over, what its net's pads are near it, what other nets'
pads stand in the way, and which corridor is clear. This is those four readings as one report, so the next
board's answer costs minutes rather than an afternoon. It decides nothing and writes no verdict: `via_current`
is the judge and this is the map its failure hands to whoever draws the copper.

What it prints, per barrel over its rating: the net, the current the solved mesh puts through it against the
barrel's rating, the position, the pads of ITS OWN net within reach (the anchors a locked run can join), and
every other net's pad within reach with its distance (the obstacles the corridor has to miss). Coordinates are
the board file's own millimetres and also relative to the board's aux origin where one is set, because the
generators draw in that frame.

Usage: barrel_sites.py <board.kicad_pcb> [--rise-k 10] [--reach 6.0] [--all] [--json] [--suggest]
       --all reports every measured barrel, not only the ones over their rating.
       --suggest prints the power_copper.cluster line each over-rated site would take, with the axis that
       has more room and the nearest other-net pad beside it. It prints; it never edits a generator.
"""
import os, sys, json, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _prov_seen(board_path):
    """Is there a barrel-provenance map beside this board at all? Absent, nothing can be told apart."""
    import os as _o
    stem = _o.path.splitext(_o.path.basename(board_path))[0]
    for suf in ("-placed", "-preroute", "-par-routed", "-cleaned"):
        if stem.endswith(suf): stem = stem[: -len(suf)]
    d = _o.path.dirname(_o.path.abspath(board_path))
    return any(_o.path.isfile(q) for q in (_o.path.join(d, "out", stem + "-barrel-provenance.json"),
                                           _o.path.join(d, stem + "-barrel-provenance.json")))


def _placed_by_src(board_path, net, x, y, tol=0.6):
    """The generator line that placed the barrel at this site, from the sidecar, or None.

    A SIDECAR AND NOT EVIDENCE: nothing is judged by it, its absence costs the reader a line and nothing
    else, and a board generated before `power_copper.write_provenance` existed simply has none."""
    import json as _j, os as _o
    try:
        stem = _o.path.splitext(_o.path.basename(board_path))[0]
        for suf in ("-placed", "-preroute", "-par-routed", "-cleaned"):
            if stem.endswith(suf): stem = stem[: -len(suf)]
        d = _o.path.dirname(_o.path.abspath(board_path))
        p = _o.path.join(d, "out", stem + "-barrel-provenance.json")
        if not _o.path.isfile(p): p = _o.path.join(d, stem + "-barrel-provenance.json")
        if not _o.path.isfile(p): return None
        rows = (_j.load(open(p, encoding="utf-8")) or {}).get("barrels") or []
    except Exception:
        return None
    best, bd = None, tol
    for r in rows:
        if str(r.get("net", "")).lstrip("/") != str(net).lstrip("/"): continue
        at = r.get("at") or [0, 0]
        d = math.hypot(float(at[0]) - x, float(at[1]) - y)
        if d <= bd: best, bd = r.get("src"), d
    return best


def main(argv):
    if not argv: print(__doc__); return 2
    import pcbnew, intent
    import via_current as _vc
    path = argv[0]
    rise = float(argv[argv.index("--rise-k") + 1]) if "--rise-k" in argv else 10.0
    reach = float(argv[argv.index("--reach") + 1]) if "--reach" in argv else 6.0
    every = "--all" in argv
    b = pcbnew.LoadBoard(path)
    it = intent.load(path) or {}
    out_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "out")
    mp = os.path.join(out_dir, os.path.splitext(os.path.basename(path))[0] + "-via-currents.json")
    if not os.path.exists(mp):
        print("barrel_sites: no solved barrel currents beside this board (%s); run dc_drop first" % mp)
        return 3
    md = json.load(open(mp, encoding="utf-8"))
    plating = float(md.get("plating_um") or 18.0)
    nets = {k.lstrip("/"): v for k, v in (md.get("nets") or {}).items()}

    try:
        ox, oy = b.GetDesignSettings().GetAuxOrigin().x / 1e6, b.GetDesignSettings().GetAuxOrigin().y / 1e6
    except Exception:
        ox = oy = 0.0
    pads = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            pads.append((fp.GetReference(), p.GetNumber(), p.GetNetname().lstrip("/"),
                         p.GetPosition().x / 1e6, p.GetPosition().y / 1e6,
                         p.GetSize().x / 1e6, p.GetSize().y / 1e6))
    rows, over = [], 0
    for net, barrels in sorted(nets.items()):
        for bar in barrels:
            drill = float(bar.get("drill_mm") or 0.4)
            amps = float(bar.get("amps") or 0.0)
            lim = _vc.ampacity(drill, rise, plating)[0]
            if lim <= 0: continue
            ratio = amps / lim
            if ratio <= 1.0 and not every: continue
            over += 1 if ratio > 1.0 else 0
            x, y = float(bar.get("x") or 0), float(bar.get("y") or 0)
            own, other = [], []
            for ref, num, pnet, px, py, sx, sy in pads:
                d = math.hypot(px - x, py - y)
                if d > reach: continue
                (own if pnet == net else other).append((round(d, 2), ref, num, pnet, round(px, 2), round(py, 2), round(sx, 2), round(sy, 2)))
            own.sort(); other.sort()
            # WHOSE BARREL IS IT (18 September 2026, found on board P): a locked via at the site is the
            # GENERATOR's own, and a cluster centred there would sit 0.45 mm from it, which is a hole-to-hole
            # violation. Where the barrel is the router's, the placement has nothing there and a cluster is
            # exactly right (board E). So the report says which, because the edit is a different one.
            mine = any(t.GetClass() == "PCB_VIA" and t.IsLocked()
                       and t.GetNetname().lstrip("/") == net
                       and math.hypot(t.GetPosition().x / 1e6 - x, t.GetPosition().y / 1e6 - y) < 0.15
                       for t in b.GetTracks())
            # AND WHETHER IT IS A BARREL AT ALL (20 September 2026). The drill above is the drill of the
            # thing ALREADY at the site, and at four of board E's ten suggested sites that thing is a
            # CONNECTOR'S PLATED COMPONENT HOLE, 1.78 mm at the XT60 and the DC inlet. Suggested as a cluster
            # and applied, E24 came back with EIGHT `annular_width` at -0.4900 mm and SIXTEEN `hole_to_hole`
            # at 0.0000: a lattice of 1.78 mm vias beside a connector is not a thing, and the four were the
            # whole of that hard set. A via cluster answers a VIA transition; a component hole that carries
            # too much current is the LAND's question, which is board P's 12 AWG wire lands by another route.
            pad_here = next((("%s.%s" % (ref, num), round(sx, 2), round(sy, 2))
                             for dd, ref, num, pnet, px, py, sx, sy in own
                             if dd < max(0.15, drill / 2.0)), None)
            rows.append(dict(net=net, amps=round(amps, 3), limit=round(lim, 3), ratio=round(ratio, 2),
                             drill=drill, at=(round(x, 2), round(y, 2)), locked_here=mine,
                             pad_here=pad_here,
                             at_origin=(round(x - ox, 2), round(oy - y, 2)) if (ox or oy) else None,
                             own=own[:8], other=other[:12]))
    print("barrel_sites: %d barrel(s) reported of %d measured net(s), %d over their own rating at %.0f K and "
          "%.0f um of plating" % (len(rows), len(nets), over, rise, plating))
    for r in rows:
        print("\n  %s  %.3f A against %.3f A for a %.2f mm barrel, ratio %.2f, at %s%s"
              % (r["net"], r["amps"], r["limit"], r["drill"], r["ratio"], r["at"],
                 ("  (board frame %s)" % (r["at_origin"],)) if r["at_origin"] else ""))
        print("    its own net's pads within %.1f mm (the anchors a locked run can join):" % reach)
        for d, ref, num, pnet, px, py, sx, sy in r["own"]:
            print("      %5.2f mm  %-7s pad %-3s at %8.2f %8.2f  pad %.2f x %.2f" % (d, ref, num, px, py, sx, sy))
        if not r["own"]: print("      none: this transition has no pad of its own net within reach, so the copper has to come from the route")
        print("    other nets' pads within %.1f mm (what the corridor has to miss):" % reach)
        for d, ref, num, pnet, px, py, sx, sy in r["other"]:
            print("      %5.2f mm  %-7s pad %-3s %-14s at %8.2f %8.2f" % (d, ref, num, pnet[:14], px, py))
        if not r["other"]: print("      none within reach: the neighbourhood is clear")
    if "--suggest" in argv:
        # THE LINES THE GENERATOR WOULD CARRY, suggested and never applied (18 September 2026). Board A has
        # thirty-two of these sites and hand-typing three coordinates apiece is how a table of ninety-six
        # numbers gets one wrong; the generator is code a person edits deliberately, so this prints and stops.
        # The axis is the one with more room in the obstacle list, and the nearest obstacle is printed beside
        # each line so the reader can veto it: a site whose nearest neighbour is under about 1.5 mm wants the
        # placement, not another barrel.
        print("\n=== suggested generator lines (read them, do not paste them blind) ===")
        import via_current as _vcx
        # SITES OF ONE NET THAT SIT ON TOP OF EACH OTHER ARE ONE TRANSITION (18 September 2026, found on board P).
        # Its two PACK_P sites are 1.03 mm apart and carry 1.965 A and 1.181 A: emitted as two clusters they put
        # two barrels 0.20 mm apart, which is a hole-to-hole violation and which `stitch` now refuses. They are
        # two barrels of ONE crossing, so they are grouped, their currents are added, and the count is taken from
        # the total with the barrels already there subtracted. A group is the sites of one net within 2 mm.
        groups = []
        for r in [x for x in rows if x["ratio"] > 1.0]:
            for g in groups:
                if g["net"] == r["net"] and min(math.hypot(r["at"][0] - q["at"][0], r["at"][1] - q["at"][1]) for q in g["sites"]) <= 2.0:
                    g["sites"].append(r); break
            else:
                groups.append({"net": r["net"], "sites": [r]})
        for g in groups:
            ss = g["sites"]
            amps = sum(x["amps"] for x in ss)
            drill = min(x["drill"] for x in ss)
            cx = sum(x["at"][0] for x in ss) / len(ss); cy = sum(x["at"][1] for x in ss) / len(ss)
            ox = sum((x["at_origin"] or x["at"])[0] for x in ss) / len(ss)
            oy = sum((x["at_origin"] or x["at"])[1] for x in ss) / len(ss)
            other = [o for x in ss for o in x["other"]]
            n = _vcx.barrels_for(amps, drill)
            pitch = drill + 0.4
            span = (n - 1) * pitch
            def worst(ax):
                # ROOM IS TO THE PAD'S EDGE AND NOT TO ITS CENTRE (20 September 2026, board E, E25). This
                # returned the distance to the nearest pad CENTRE, so `DC_F` was reported with "1.34 mm of
                # room on this axis" while its lattice landed 0.1450 mm from D1 pad 1, a 3.30 by 2.50 land
                # whose half-width is 1.65: the centre was 1.34 away and the copper was touching. Three
                # clearance violations and a chain run to find out. The gap is to the RECTANGLE now and the
                # barrel's own copper comes off it, which took `DC_F` from a reported 1.34 mm to 0.33 and
                # `DC_P` to 0.00 on its cross axis. IT IS STILL A MODEL AND NOT THE DRC: this walks a SINGLE
                # ROW of n barrels, and `cluster` may lay more than one row when the span does not fit, so a
                # site that reads a small number here is a warning and a site that reads a large one is not a
                # promise. The chain is the evidence, which is why E24, E25 and E26 were run.
                pts = [((cx - span / 2.0 + i * pitch, cy) if ax == "x" else (cx, cy - span / 2.0 + i * pitch)) for i in range(n)]
                rad = drill / 2.0 + 0.1                       # the barrel's copper, annular ring included
                gaps = []
                for px, py in pts:
                    for o in other:
                        dx = max(0.0, abs(px - o[4]) - o[6] / 2.0)
                        dy = max(0.0, abs(py - o[5]) - o[7] / 2.0)
                        gaps.append(max(0.0, math.hypot(dx, dy) - rad))
                return min(gaps or [99.0])
            wx, wy = worst("x"), worst("y")
            axis = "x" if wx >= wy else "y"
            room = ("%.2f mm of room on this axis, %.2f on the other" % (max(wx, wy), min(wx, wy))) if other else "nothing else within reach"
            _pad = next((x.get("pad_here") for x in ss if x.get("pad_here")), None)
            if _pad and drill >= 0.8:
                # A COMPONENT HOLE IS NOT A BARREL (20 September 2026, board E, E24). Nothing in a generator
                # can put a via cluster beside a 1.78 mm plated hole: the lattice pitch is the drill plus
                # 0.4 and the annular ring goes negative before the first point lands. Declined here with the
                # number, because the site IS over its rating and the answer is the land or the placement.
                print('    # %s at (%.2f, %.2f): the barrel here is %s, a plated COMPONENT HOLE of %.2f mm, '
                      'not a via.' % (g["net"], ox, oy, _pad[0], drill))
                print('    # %.3f A across it wants %d barrel(s) of that size and a via cluster cannot give '
                      'them: declined,' % (amps, n))
                print('    # the way board P\'s 12 AWG wire lands are. It is the LAND\'s question or the '
                      'placement\'s.')
                continue
            if any(x.get("locked_here") for x in ss):
                print('    # %s at (%.2f, %.2f): this barrel is the GENERATOR\'s own (a locked via sits on it), so a'
                      % (g["net"], ox, oy))
                # AND THE LINE, WHERE THE GENERATOR LEFT ONE (20 September 2026). `power_copper.stitch`
                # records the caller of every barrel it places and `write_provenance` puts the map beside the
                # board, so this can name the call instead of a coordinate. Board E has thirteen of these
                # sites and finding each call among arguments that are expressions is the hunt this removes.
                # Absent sidecar, absent line, and the sentence is what it was.
                _src = _placed_by_src(path, g["net"], ox, oy)
                if _src:
                    print('    # cluster centred here would land 0.%d mm from it. Add %d point(s) to the call '
                          'at %s' % (int(round((drill + 0.4) / 2 * 100)), max(0, n - len(ss)), _src))
                else:
                    # A LOCKED VIA IS NOT ALWAYS power_copper's (20 September 2026). `locked_here` asks only
                    # whether a LOCKED via sits at the site, and `escape.py` locks every escape stub's via
                    # and the pre-lay locks its own: seven of board E's thirteen such sites have no entry in
                    # the barrel provenance at all, so "add points to the call that placed it" is advice
                    # about a call that does not exist. Where the map is there and the site is not in it, the
                    # via belongs to the escape fan or the pre-lay and the answer is a different one.
                    print('    # cluster centred here would land 0.%d mm from it, and NO POWER-COPPER CALL '
                          'PLACED IT:' % int(round((drill + 0.4) / 2 * 100)))
                    print('    # the locked via here is the escape fan\'s or the pre-lay\'s%s, so the answer '
                          'is not points on a' % ("" if _prov_seen(path) else " (and this board carries no "
                                                 "barrel-provenance map, so it could not be checked)"))
                    print('    # call: it is the FANOUT\'s via count at that pad, which is a different edit.')
                print('    # instead, %.3f A over %d barrel(s) of %.2f mm, and keep %.4f mm between holes.'
                      % (amps, n, drill, drill + 0.2995))
                continue
            print('    _pc.cluster("%s", (%.2f, %.2f), amps=%.3f, drill=%.2f, axis="%s")   # %d barrel(s) over their rating here, worst %.2f, %s'
                  % (g["net"], ox, oy, amps, drill, axis, len(ss), max(x["ratio"] for x in ss), room))
    if "--json" in argv: print(json.dumps(rows, indent=1))
    return 0 if not over else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
