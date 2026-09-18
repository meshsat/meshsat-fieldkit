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
            # WHOSE BARREL IS IT (18 September 2026, found on board P): a locked via at the site is the
            # GENERATOR's own, and a cluster centred there would sit 0.45 mm from it, which is a hole-to-hole
            # violation. Where the barrel is the router's, the placement has nothing there and a cluster is
            # exactly right (board E). So the report says which, because the edit is a different one.
            mine = any(t.GetClass() == "PCB_VIA" and t.IsLocked()
                       and t.GetNetname().lstrip("/") == net
                       and math.hypot(t.GetPosition().x / 1e6 - x, t.GetPosition().y / 1e6 - y) < 0.15
                       for t in b.GetTracks())
            rows.append(dict(net=net, amps=round(amps, 3), limit=round(lim, 3), ratio=round(ratio, 2),
                             drill=drill, at=(round(x, 2), round(y, 2)), locked_here=mine,
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
                pts = [((cx - span / 2.0 + i * pitch, cy) if ax == "x" else (cx, cy - span / 2.0 + i * pitch)) for i in range(n)]
                return min([math.hypot(px - o[4], py - o[5]) for px, py in pts for o in other] or [99.0])
            wx, wy = worst("x"), worst("y")
            axis = "x" if wx >= wy else "y"
            room = ("%.2f mm of room on this axis, %.2f on the other" % (max(wx, wy), min(wx, wy))) if other else "nothing else within reach"
            if any(x.get("locked_here") for x in ss):
                print('    # %s at (%.2f, %.2f): this barrel is the GENERATOR\'s own (a locked via sits on it), so a'
                      % (g["net"], ox, oy))
                print('    # cluster centred here would land 0.%d mm from it. Add %d point(s) to the call that placed it'
                      % (int(round((drill + 0.4) / 2 * 100)), max(0, n - len(ss))))
                print('    # instead, %.3f A over %d barrel(s) of %.2f mm, and keep %.4f mm between holes.'
                      % (amps, n, drill, drill + 0.2995))
                continue
            print('    _pc.cluster("%s", (%.2f, %.2f), amps=%.3f, drill=%.2f, axis="%s")   # %d barrel(s) over their rating here, worst %.2f, %s'
                  % (g["net"], ox, oy, amps, drill, axis, len(ss), max(x["ratio"] for x in ss), room))
    if "--json" in argv: print(json.dumps(rows, indent=1))
    return 0 if not over else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
