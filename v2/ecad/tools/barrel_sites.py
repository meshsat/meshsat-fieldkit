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
            rows.append(dict(net=net, amps=round(amps, 3), limit=round(lim, 3), ratio=round(ratio, 2),
                             drill=drill, at=(round(x, 2), round(y, 2)),
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
        for r in rows:
            if r["ratio"] <= 1.0: continue
            x, y = r["at_origin"] or r["at"]
            # THE AXIS IS THE ONE THAT KEEPS THE MOST ROOM, computed rather than guessed (18 September 2026).
            # The first version compared the obstacle's x and y displacement and picked the larger, which spreads
            # TOWARD the nearest pad: board P's second FUSED site has Q1's gate pad 0.68 mm away in x and 1.27 in
            # y, and that rule chose y, which walks a barrel to 1.07 mm from it where x keeps 1.29. So both axes
            # are measured: the barrels a cluster would place are laid out on each, the worst distance to any
            # other net's pad is taken, and the better axis wins. It is the same arithmetic the tool already does
            # for the count, applied to the direction.
            import via_current as _vcx
            _n = _vcx.barrels_for(r["amps"], r["drill"])
            _pitch = r["drill"] + 0.4
            _span = (_n - 1) * _pitch
            def _worst(ax):
                pts = [((r["at"][0] - _span / 2.0 + i * _pitch, r["at"][1]) if ax == "x"
                        else (r["at"][0], r["at"][1] - _span / 2.0 + i * _pitch)) for i in range(_n)]
                return min([math.hypot(px - o[4], py - o[5]) for px, py in pts for o in r["other"]] or [99.0])
            _wx, _wy = _worst("x"), _worst("y")
            axis = "x" if _wx >= _wy else "y"
            nearest = min(_wx, _wy) if r["other"] else None
            print('    _pc.cluster("%s", (%.2f, %.2f), amps=%.3f, drill=%.2f, axis="%s")   # ratio %.2f, nearest other-net pad %s'
                  % (r["net"], x, y, r["amps"], r["drill"], axis, r["ratio"],
                     ("%.2f mm to the nearest other-net pad on this axis (%.2f on the other)"
                      % (max(_wx, _wy), min(_wx, _wy))) if r["other"] else "none within reach"))
    if "--json" in argv: print(json.dumps(rows, indent=1))
    return 0 if not over else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
