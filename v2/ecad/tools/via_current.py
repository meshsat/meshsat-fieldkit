#!/usr/bin/env python3
"""A rail's layer transition is carried by the vias at it, and the vias are counted and rated (rule PI-003,
MESHSAT-862, 16 September 2026).

The record has carried "about 2.5 A per 0.4 mm hole" in a generator comment since 5 September, and nothing has
ever measured a board against it. A rail that dives to an inner plane through one via is a rail whose whole
current crosses one plated barrel: the barrel is thin copper on the wall of a hole, not a track, and it is the
one place in a power path this project has never judged.

WHERE EVERY NUMBER COMES FROM, because a fabrication limit invented here would be exactly what this registry
exists to refuse:

  * the PLATING THICKNESS is the fabricator's own published figure, 18 um average hole plating, from
    `v2/vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md` (section "Holes and vias"). A board may
    declare `via_plating_um` to override it with its own quotation.
  * the BARREL CROSS-SECTION is geometry: a hole of diameter d plated to thickness t has an annulus of
    pi * (d + t) * t of copper. Nothing else is assumed: no pad, no track, no fill.
  * the CURRENT a cross-section carries at a temperature rise is IPC-2221's curve, the same expression
    `dc_drop.py` already uses for track density, with the INTERNAL constant, because a via barrel is enclosed
    by laminate on every side. IPC-2221 itself is not in this tree, so this rule carries SOURCE_UNVERIFIED and
    the number is a calculation this project made, not a limit a document gave it.
  * the RAIL CURRENT is the board's own intent file, the same place `dc_drop` reads it.

WHAT IT JUDGES. For each declared rail, the vias of that net are grouped into SITES: a site is a cluster of
this net's vias within `--site-mm` (default 6 mm) of each other, which is what a layer transition looks like
on these boards (a dive, a stitch field, a fan). The rail's peak current must be carried by the site that has
the least capacity, because a transition is a series element: every ampere that changes layer there goes
through those barrels. A rail with no via at all is reported and not failed: it never changes layer.

Usage: via_current.py <board.kicad_pcb> [--rise-k 10] [--site-mm 6] [--json]
"""
import os, sys, math, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v
import boardtable as _bt

PLATING_UM = 18.0        # the fabricator's published average hole plating
K_INTERNAL = 0.024       # IPC-2221's constant for an internal conductor
MM2_TO_MIL2 = 1550.0031


def ampacity(drill_mm, rise_k, plating_um=PLATING_UM):
    """IPC-2221 for the barrel of a plated hole: I = k * dT^0.44 * A^0.725, A in square mils."""
    t = plating_um / 1000.0
    area_mm2 = math.pi * (drill_mm + t) * t
    return K_INTERNAL * (rise_k ** 0.44) * ((area_mm2 * MM2_TO_MIL2) ** 0.725), area_mm2


def sites(pts, reach):
    """Single-link clusters of via positions: a transition is a group of barrels that sit together."""
    out = []
    left = list(range(len(pts)))
    while left:
        seed = left.pop(0); group = [seed]; moved = True
        while moved:
            moved = False
            for i in list(left):
                if any(math.hypot(pts[i][0] - pts[g][0], pts[i][1] - pts[g][1]) <= reach for g in group):
                    group.append(i); left.remove(i); moved = True
        out.append(group)
    return out


def main(a):
    if not a: print(__doc__); return _v.USAGE
    path = a[0]
    rise = float(a[a.index("--rise-k") + 1]) if "--rise-k" in a else 10.0
    reach = float(a[a.index("--site-mm") + 1]) if "--site-mm" in a else 6.0
    import pcbnew
    import intent
    mm = lambda v: v / 1e6
    b = pcbnew.LoadBoard(path)
    it = intent.load(path)
    out_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "out")
    if not it or not (it.get("rails") or {}):
        print("via_current: no intent file for this board, so no rail current is known")
        return _v.write("via_current", _v.INCONCLUSIVE, denominator=0, inputs={"board": path},
                        note="no intent file, so no rail current is known and no via could be judged",
                        out_dir=out_dir)
    letter = _bt.letter_for(path)
    plating = float(_bt.value(letter, "via_plating_um", PLATING_UM))
    vias = {}
    for t in b.GetTracks():
        if t.GetClass() != "PCB_VIA": continue
        vias.setdefault(t.GetNetname().lstrip("/"), []).append(
            (mm(t.GetPosition().x), mm(t.GetPosition().y), round(mm(t.GetDrill()), 4)))
    rows, bad, no_via = [], [], []
    for net, r in sorted((it.get("rails") or {}).items()):
        amps = float(r.get("amps_peak") or r.get("amps_typ") or 0)
        if amps <= 0: continue
        vs = vias.get(net.lstrip("/"), [])
        if not vs:
            no_via.append("%s carries %.2f A and has no via: it never changes layer" % (net, amps)); continue
        worst = None
        for g in sites([(v[0], v[1]) for v in vs], reach):
            cap = sum(ampacity(vs[i][2], rise, plating)[0] for i in g)
            if worst is None or cap < worst[0]: worst = (cap, len(g), vs[g[0]][0], vs[g[0]][1])
        cap, n, x, y = worst
        rows.append(dict(net=net, amps=amps, sites=len(sites([(v[0], v[1]) for v in vs], reach)),
                         worst_vias=n, worst_capacity_a=round(cap, 3), at=(round(x, 2), round(y, 2)),
                         ok=cap >= amps))
        if cap < amps:
            bad.append("%s: %.2f A crosses a transition of %d via(s) at (%.1f, %.1f) rated %.2f A at %.0f K "
                       "(%.0f um plating)" % (net, amps, n, x, y, cap, rise, plating))
    print("via_current: %d rail(s) with vias judged at %.0f K rise and %.0f um plating, %d over their weakest "
          "transition; %d rail(s) carry no via" % (len(rows), rise, plating, len(bad), len(no_via)))
    for x in bad[:20]: print("  FAIL %s" % x)
    for x in no_via[:6]: print("  note %s" % x)
    if "--json" in a: print(json.dumps(rows, indent=1))
    return _v.write("via_current", _v.FAIL if bad else (_v.INCONCLUSIVE if not rows else _v.PASS),
                    counts={"rails": len(rows), "over": len(bad), "no_via": len(no_via)},
                    denominator=len(rows), evidence=bad[:20],
                    inputs={"board": path, "rise_k": rise, "plating_um": plating, "site_mm": reach},
                    note=("no declared rail on this board carries a via, so nothing was judged" if not rows else
                          "every rail's weakest layer transition against IPC-2221 for a barrel of the "
                          "fabricator's own plating thickness"),
                    out_dir=out_dir)


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
