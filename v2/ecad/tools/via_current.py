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



def barrels_for(amps, drill_mm, rise_k=10.0, plating_um=PLATING_UM):
    """How many barrels of this drill a current needs (18 September 2026).

    This rule fails in one shape on every board measured today: a layer transition the generator gave ONE barrel
    where the solved mesh puts more current through it than one barrel's wall carries (board D 1.22, board E
    1.48, board A as far as 3.77 across thirty-two sites). The arithmetic was always available to the generator,
    which knows the point, the drill and the rail's declared current, and it simply was not asked; `power_copper`
    asks it now and refuses a stitch that is short. Ceil, never round: half a barrel carries nothing."""
    import math
    lim = ampacity(drill_mm, rise_k, plating_um)[0]
    return max(1, int(math.ceil(float(amps) / lim))) if lim > 0 else 1

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
    # THE CURRENT EACH BARREL ACTUALLY CARRIES, WHERE THE MESH HAS BEEN SOLVED (16 September 2026).
    # `dc_drop.py` solves a resistive mesh over this board's copper and computes the current in every barrel on
    # the way; it writes them beside the board now. With that file the question stops being "can this rail's
    # weakest cluster of its own vias carry the whole rail" and becomes "does any barrel carry more than it is
    # rated for", which is the question, and a lone stitch via at the end of a pour is judged on the almost
    # nothing it carries instead of on the rail's entire current. Without the file the old reading stands and
    # the verdict stays ADVISORY, because that reading is an assumption about attribution and not a measurement.
    measured = {}
    _mp = os.path.join(out_dir, os.path.splitext(os.path.basename(path))[0] + "-via-currents.json")
    if os.path.exists(_mp):
        try:
            _md = json.load(open(_mp, encoding="utf-8"))
            for _n, _vs in (_md.get("nets") or {}).items():
                measured[_n.lstrip("/")] = _vs
        except Exception as _e:
            print("via_current: the barrel currents beside this board could not be read (%s)" % _e)

    # EVERY BARREL OVER ITS RATING IS NAMED, not only its rail's worst (18 September 2026). The counts below
    # are per RAIL, which is what the denominator means and what the note says; but the reader of a failure is
    # the person who has to draw copper at the site, and board D's +5V_SA crosses layers TWICE with a single
    # barrel at each crossing, both carrying the whole 1.10 A. The record said "one barrel" for a day because
    # this list held one line per rail. `barrel_sites.py` is the map of what stands around each of them.
    rows, bad, bad_sites, no_via = [], [], [], []
    for net, r in sorted((it.get("rails") or {}).items()):
        amps = float(r.get("amps_peak") or r.get("amps_typ") or 0)
        if amps <= 0: continue
        key = net.lstrip("/")
        vs = vias.get(key, [])
        if not vs:
            no_via.append("%s carries %.2f A and has no via: it never changes layer" % (net, amps)); continue
        if key in measured and measured[key]:
            # Every barrel against its own rating, on the current the mesh put through it.
            worst_m = None
            for _b in measured[key]:
                _lim = ampacity(float(_b.get("drill_mm") or 0.4), rise, plating)[0]
                _cur = float(_b.get("amps") or 0.0)
                if _lim <= 0: continue
                if worst_m is None or _cur / _lim > worst_m[0]:
                    worst_m = (_cur / _lim, _cur, _lim, float(_b.get("x") or 0), float(_b.get("y") or 0))
            if worst_m is not None:
                _ratio, _cur, _lim, _x, _y = worst_m
                rows.append(dict(net=net, amps=amps, barrels=len(measured[key]), measured=True,
                                 worst_barrel_a=round(_cur, 3), worst_barrel_limit_a=round(_lim, 3),
                                 at=(round(_x, 2), round(_y, 2)), ok=_ratio <= 1.0))
                if _ratio > 1.0:
                    bad.append("%s: a barrel at (%.1f, %.1f) carries %.2f A of the solved mesh against %.2f A "
                               "for its own wall at %.0f K (%.0f um plating), ratio %.2f"
                               % (net, _x, _y, _cur, _lim, rise, plating, _ratio))
                for _b in measured[key]:
                    _l2 = ampacity(float(_b.get("drill_mm") or 0.4), rise, plating)[0]
                    _c2 = float(_b.get("amps") or 0.0)
                    if _l2 > 0 and _c2 / _l2 > 1.0:
                        bad_sites.append("%s: barrel at (%.1f, %.1f), %.2f A against %.2f A, ratio %.2f"
                                         % (net, float(_b.get("x") or 0), float(_b.get("y") or 0), _c2, _l2, _c2 / _l2))
                continue
        worst = None
        for g in sites([(v[0], v[1]) for v in vs], reach):
            cap = sum(ampacity(vs[i][2], rise, plating)[0] for i in g)
            if worst is None or cap < worst[0]: worst = (cap, len(g), vs[g[0]][0], vs[g[0]][1])
        cap, n, x, y = worst
        rows.append(dict(net=net, amps=amps, sites=len(sites([(v[0], v[1]) for v in vs], reach)),
                         worst_vias=n, worst_capacity_a=round(cap, 3), at=(round(x, 2), round(y, 2)),
                         measured=False, ok=cap >= amps))
        if cap < amps:
            bad.append("%s: %.2f A crosses a transition of %d via(s) at (%.1f, %.1f) rated %.2f A at %.0f K "
                       "(%.0f um plating), attributed rather than measured"
                       % (net, amps, n, x, y, cap, rise, plating))
    print("via_current: %d rail(s) with vias judged at %.0f K rise and %.0f um plating, %d over their weakest "
          "transition; %d rail(s) carry no via" % (len(rows), rise, plating, len(bad), len(no_via)))
    for x in bad[:20]: print("  FAIL %s" % x)
    for x in no_via[:6]: print("  note %s" % x)
    if "--json" in a: print(json.dumps(rows, indent=1))
    # ADVISORY UNTIL IT KNOWS WHICH VIA THE CURRENT CROSSES (16 September 2026, its first run on real boards).
    # It found something on all seven and most of it is the same false shape: a rail's WEAKEST site is often a
    # lone stitch via at the end of a pour, which carries almost none of the rail's current, while the current
    # itself travels in a band with a field of vias under it. Board E's CELL_F reads "18 A through 1 via" and
    # board P's FUSED the same, which is not what that copper does. The arithmetic is right and the ATTRIBUTION
    # is not: a via of the rail's net is not the same thing as a via the rail's current crosses, and telling
    # them apart needs the per-element current that `dc_drop`'s solved mesh already computes. So this is a
    # measurement for the record, not a bar: it is written, listed and hashed like any other verdict, the
    # collector leaves it out of the stage's worst, and the readiness reads the rule as unverified rather than
    # failed. A gate that refuses eleven rails on board A for a reason its author already doubts is exactly the
    # heuristic-as-law this registry exists to remove.
    # ...AND IT IS A BAR AGAIN ONCE EVERY RAIL IS MEASURED (16 September 2026). The advisory flag was about
    # ATTRIBUTION and nothing else. Where every judged rail's barrels carry the current `dc_drop`'s solved mesh
    # put through them, the attribution is a measurement and the reason to hold the verdict back is gone; where
    # even one rail falls back to the attributed reading, it stays advisory and the note says which.
    _measured = [r for r in rows if r.get("measured")]
    _all_measured = bool(rows) and len(_measured) == len(rows)
    _why = ("every rail's barrels against IPC-2221's curve for a barrel of the fabricator's own plating "
            "thickness, on the current dc_drop's solved mesh puts through each of them. The curve is the "
            "internal-conductor model published with its constants in ECSS-Q-ST-70-12C Annex D (D.4), "
            "transcribed in v2/vendor/standards/ and implemented in tools/track_current.py"
            if _all_measured else
            "every rail's weakest layer transition against IPC-2221's curve (ECSS-Q-ST-70-12C Annex D D.4) for "
            "a barrel of the fabricator's own plating thickness. ADVISORY: %d of %d judged rail(s) have no "
            "solved barrel current beside this board, so for those the rail's WHOLE current is attributed to "
            "its weakest cluster of vias, which on these boards is often a lone stitch via carrying almost none"
            % (len(rows) - len(_measured), len(rows)))
    return _v.write("via_current", _v.FAIL if bad else (_v.INCONCLUSIVE if not rows else _v.PASS),
                    counts={"rails": len(rows), "over": len(bad), "no_via": len(no_via),
                            "measured_rails": len(_measured), "over_barrels": len(bad_sites)},
                    denominator=len(rows), evidence=(bad + bad_sites)[:24], advisory=not _all_measured,
                    inputs={"board": path, "rise_k": rise, "plating_um": plating, "site_mm": reach},
                    note=("no declared rail on this board carries a via, so nothing was judged" if not rows
                          else _why),
                    out_dir=out_dir)


if __name__ == "__main__":
    # EVERY GATE LEAVES A READING WHEN IT RAISES (18 September 2026). The thirteen one-line entries of this
    # morning were the gates a crash had already cost a verdict; these are the rest of the deciding gates in
    # the coverage map, guarded the same way, so a rule whose tool raised reads INCONCLUSIVE naming the
    # exception rather than 'no verdict', which the registry reads as nobody having looked.
    sys.exit(_v.guard("via_current", main, sys.argv[1:]))