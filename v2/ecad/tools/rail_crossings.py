#!/usr/bin/env python3
"""Every declared rail's own layer crossing, and the barrels its current needs there (rule PI-003's cheap half).

MESHSAT-862, 18 September 2026. Every PI-003 failure this project has found has one shape: a rail crosses
layers through ONE barrel. Board B is three slot rails at 2.20 A through a single 0.25 mm barrel sitting inside
that slot's bulk capacitor pad; board E was CELL_F at 1.42 A; board D was two `+5V_SA` crossings. `via_current`
finds them after a route, from the current `dc_drop`'s solved mesh puts through each barrel. A generator can
ask a cheaper question BEFORE a route: at the pad of a rail's declared SOURCE the whole rail current crosses,
and at a declared LOAD's pad that load's share does, so the barrels those need are arithmetic
(`via_current.barrels_for`, IPC-2221A's internal model as published in ECSS-Q-ST-70-12C Annex D, on the
fabricator's own 18 um plating).

IT RUNS ON THE FINISHED PLACEMENT AND NOT INSIDE THE FANOUT, and that is the whole reason this file exists
rather than a dozen lines at the end of `prefanout.py`. The first version printed its answer there and named
SEVEN crossings on board E's E20 generation, every one of which the stages that follow had already answered:
the ground grid alone lays 1,829 vias after the fanout, and the escapes lay more. A report that names sites
somebody else fixes ten seconds later is noise, and the next person stops reading it.

It REPORTS and lays nothing: where to put more copper is a placement question and its shape differs per board
(`barrel_sites.py --suggest` writes the generator lines from the SOLVED board). A site named here is one the
routed board will fail on unless the route happens to put less current through it than the whole rail.

Usage: rail_crossings.py <board.kicad_pcb> [--intent out/<stem>-intent.json]
"""
import os, sys, math, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import via_current as _vc

# KiCad IS IMPORTED IN `main` AND NOT HERE, so that `judge` can be exercised where KiCad is not. Everything the
# judge touches is a method name (`GetClass`, `Pads`, `GetDrill`), never a pcbnew constant, so the split rule
# that cost this tool a version is provable on the runner instead of skipping there. `test_pair_router_imports`
# exists because a rule that only runs on the box leaves the runner's suite green while the tool is broken.


def judge(b, rails, reach_mm=1.0):
    """(short, judged): the crossings with fewer barrels than the current needs, and how many were asked."""
    vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
    short, judged = [], 0
    for net, r in sorted(rails.items()):
        n = net.lstrip("/")
        amps = float(r.get("amps_peak") or r.get("amps_typ") or 0)
        if amps <= 0: continue
        # A RAIL'S SOURCE MAY BE SEVERAL REFERENCES, and on board B it is a LIST (the slot rails are fed from
        # more than one place). The first version used it as a dict key and raised `unhashable type: 'list'` on
        # the first board that has one, which is the 13 September lesson about a list used as a key, again.
        _src = r.get("source") or []
        if isinstance(_src, str): _src = [_src]
        want = {str(x): amps for x in _src if x}
        for ref, a in (r.get("loads") or {}).items():
            try: want[ref] = max(want.get(ref, 0.0), float(a))
            except (TypeError, ValueError): pass
        for fp in b.GetFootprints():
            ref = fp.GetReference()
            if ref not in want or not want[ref]: continue
            # A PART'S CURRENT IS SPLIT ACROSS THE PADS IT TAKES IT ON (18 September 2026, and this project has
            # made the other mistake before: the first hand-over report divided the RAIL'S WHOLE current by one
            # barrel at every site and called 29 of board A's 31 sites short). A compute module takes its core
            # rail on five pads; each of them carries about a fifth. Board B reads 102 short crossings of 103
            # with the whole current at every pad and ONE with the split, which is the difference between a
            # report somebody acts on and a report somebody turns off.
            _pads = [q for q in fp.Pads() if (q.GetNetname() or "").lstrip("/") == n]
            if not _pads: continue
            _share = want[ref] / float(len(_pads))
            for pad in _pads:
                bb = pad.GetBoundingBox(); c = pad.GetPosition()
                near = [v for v in vias if (v.GetNetname() or "").lstrip("/") == n
                        and math.hypot(v.GetPosition().x - c.x, v.GetPosition().y - c.y)
                        <= max(bb.GetWidth(), bb.GetHeight()) / 2 + reach_mm * 1e6]
                if not near: continue           # no crossing at this pad: nothing to count
                judged += 1
                drill = min(v.GetDrill() for v in near) / 1e6
                need = _vc.barrels_for(_share, drill)
                if len(near) < need:
                    short.append("%s at %s pad %s (%.2f, %.2f): %d barrel(s) of %.2f mm for %.2f A "
                                 "(%.2f A over this part's %d pad(s) on the rail), which needs %d at a 10 K rise"
                                 % (n, ref, pad.GetNumber(), c.x / 1e6, c.y / 1e6, len(near), drill, _share,
                                    want[ref], len(_pads), need))
    return short, judged


def main(a):
    if not a: print(__doc__); return 2
    path = a[0]
    # THE INTENT FILE IS NAMED AFTER THE PROJECT'S BOARD, not after the snapshot being read: a placed or
    # pre-route copy carries a suffix and its own directory is `out/` already. Strip both, and let a caller say.
    _stem = os.path.splitext(os.path.basename(path))[0]
    for _suf in ("-placed", "-preroute", "-par-routed", "-cleaned"):
        if _stem.endswith(_suf): _stem = _stem[: -len(_suf)]
    _dir = os.path.dirname(os.path.abspath(path))
    if os.path.basename(_dir) == "out": _dir = os.path.dirname(_dir)
    ip = a[a.index("--intent") + 1] if "--intent" in a else os.path.join(_dir, "out", _stem + "-intent.json")
    if not os.path.exists(ip):
        print("rail_crossings: no intent file at %s, so no rail declares a current here" % ip); return 0
    rails = json.load(open(ip, encoding="utf-8")).get("rails") or {}
    import pcbnew
    b = pcbnew.LoadBoard(path)
    short, judged = judge(b, rails)
    print("rail_crossings: %d crossing(s) of %d declared rail(s) carry the barrels their current needs, %d do not"
          % (judged - len(short), len(rails), len(short)))
    for s in short[:20]: print("rail_crossings:   %s" % s)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
