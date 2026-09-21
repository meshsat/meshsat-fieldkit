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


def _kc_width(v):
    """The via's ring diameter. `PCB_VIA::GetWidth()` with no argument is an error in KiCad 9 (17 September),
    so `kicad_compat.via_width` is the one answer; a fake via in a fixture just answers GetWidth."""
    try:
        import kicad_compat as _kc
        return _kc.via_width(v)
    except Exception:
        return v.GetWidth()


def judge(b, rails, reach_mm=1.0, pin_sites=None, one_layer_sites=None):
    """(short, judged): the crossings with fewer barrels than the current needs, and how many were asked.

    The sentences are formatted from `rows()`, which is the same walk carrying its numbers instead of its
    prose. `rail_barrels.py`, the fixer, reads THOSE, so the thing that lays copper and the thing that judges
    it can never drift apart: a fixer with its own idea of which site is short is the 8 September defect about
    a debug print that does not share the predicate it explains, and this project has paid for it twice."""
    rows_, judged = rows(b, rails, reach_mm, pin_sites=pin_sites, one_layer_sites=one_layer_sites)
    return [r["why"] for r in rows_], judged


def rows(b, rails, reach_mm=1.0, pin_sites=None, one_layer_sites=None):
    """(short, judged) with each short crossing as a dict: net, ref, pad, at, drill, have, need, amps.

    `pin_sites`, when a list is given, collects the sites this walk does NOT judge because the land is a plated
    hole (see the comment at the test below): one dict each, net, ref, pad, at, drill, amps.
    `one_layer_sites`, when a list is given, collects the sites this walk does NOT judge because the net lies on
    ONE layer at generation (21 September 2026, 07:50 CEST): the 02:45 entry named such a site and left it in the
    count until A97 answered whether a cluster there pays. A97's solved board answered: FE_OUT carries 8 A through
    eleven vias with every millimetre of its copper on F.Cu, PD_OUT and HF_OUT the same, so the clusters the fixer
    pre-laid at those tabs reached nothing, and the twelve controller pins A97 left open beside them were their
    price. A crossing that exists only if the router makes one is `via_current`'s to judge on the solved mesh
    (`crosses_layers`), never this walk's to ask barrels for."""
    vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
    short, judged = [], 0
    for net, r in sorted(rails.items()):
        n = net.lstrip("/")
        # WHICH CURRENT THIS RULE ASKS ABOUT, AND WHY (20 September 2026, appendix 32.245). A BARREL is judged
        # at the PEAK. It has almost no thermal mass and a far higher current density than the conductor
        # feeding it, so the case that decides it is the worst the rail ever carries, not its continuous
        # load. The conductor rules PI-001 and PI-002 ask `amps_typ` for the opposite reason: IPC's 10 K rise
        # is a STEADY-STATE limit. So a via on VBAT is judged at 18 A while the track feeding it is judged at
        # 10, on the same board and from the same declaration, and the two rules' numbers are NOT comparable.
        # That is deliberate physics and it was undocumented until it was found by reading all four tools.
        amps = float(r.get("amps_peak") or r.get("amps_typ") or 0)
        if amps <= 0: continue
        # A RAIL'S SOURCE MAY BE SEVERAL REFERENCES, and on board B it is a LIST (the slot rails are fed from
        # more than one place). The first version used it as a dict key and raised `unhashable type: 'list'` on
        # the first board that has one, which is the 13 September lesson about a list used as a key, again.
        _src = r.get("source") or []
        if isinstance(_src, str): _src = [_src]
        # WHICH LAYERS THIS NET'S OWN COPPER LIES ON AT GENERATION (21 September 2026). via_current declines to
        # call a via a transition on a net whose copper lies on one layer (its `crosses_layers`); this judge
        # never asked, so board E's HS_S and board A's six FET drain tabs, every one of them F.Cu-only before the
        # route (no zone, no band, no plated hole), were counted as short crossings through the FANOUT's own
        # via, which reaches bare laminate. A one-layer net's crossing exists only if the ROUTER makes one,
        # which via_current judges on the solved mesh afterwards. The row carries the fact and its line says
        # it; the count is NOT changed here tonight, because A97 is routing with pre-laid clusters at exactly
        # those tabs and its solved mesh is the measurement of whether they pay (boards/a.json, A97).
        _lay = set()
        for _t in b.GetTracks():
            if (_t.GetNetname() or "").lstrip("/") == n and _t.GetClass() != "PCB_VIA" and hasattr(_t, "GetLayer"):
                _lay.add(_t.GetLayer())
        for _z in (b.Zones() if hasattr(b, "Zones") else []):
            if (_z.GetNetname() or "").lstrip("/") == n and not _z.GetIsRuleArea(): _lay.add(_z.GetFirstLayer())
        for _f in b.GetFootprints():
            for _q in _f.Pads():
                if (_q.GetNetname() or "").lstrip("/") != n: continue
                if getattr(_q, "GetDrillSizeX", lambda: 0)() > 0: _lay.add("PTH")
                # A SURFACE PAD IS COPPER ON ITS LAYER (21 September 2026, 07:57 CEST): the first version read
                # tracks, zones and plated holes and not the pads themselves, so a rail whose only copper besides
                # an inner pour was its SMD pads read as one layer; a pad's layer counts like a track's.
                elif hasattr(_q, "GetLayer"): _lay.add(_q.GetLayer())
        _one_layer = len(_lay) <= 1
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
            # PADS OF ONE NUMBER ARE ONE LAND AND ONE CROSSING (21 September 2026, board E). KiCad draws a PowerPAK
            # SO-8's drain as FIVE pads numbered 5, the tab and its four leads, joined inside the part; this loop
            # took each as a pad of its own, split Q7's 8.00 A five ways and judged four crossings of 1.60 A at
            # leads 1.27 mm apart, so `rail_barrels` answered two of them and the other two read short by 0.12 A
            # forever, while the tab itself, which carries the whole current, was never asked for 8.00 A. A pad
            # NUMBER is the unit: the share is the part's current over its distinct numbers on the rail, the
            # barrels counted are those within reach of ANY instance of the number (each once), and the row is
            # anchored on the largest instance, which is where the copper is.
            _groups = {}
            for q in _pads: _groups.setdefault(str(q.GetNumber()), []).append(q)
            # ADJACENT PADS OF ONE NET ON ONE PART ARE ONE LAND TOO (21 September 2026, 03:41 CEST, board E). A
            # TDSON-8's source is pins 1, 2 and 3, three pads at a 1.27 mm pitch joined inside the package and
            # numbered apart, so the rule above read Q2's source as three crossings of a third: the fixer laid
            # three barrels at pad 2, the judge then counted them inside pads 1's and 3's windows, and reported
            # both short by two, forever, because a barrel at pad 2 IS a barrel of that land. Pads of one net on
            # one part whose centres lie within a pitch and a half of each other are merged into one land
            # (label "1-3"), sharing the part's current once; pads further apart than that stay separate, so a
            # module's five core pads spread across its edge are still five crossings and a bare one is named.
            _MERGE = 1.5e6
            _names = sorted(_groups)
            _land = {_nm: _nm for _nm in _names}
            for i, a_ in enumerate(_names):
                for b_ in _names[i + 1:]:
                    if _land[b_] != b_: continue
                    if any(math.hypot(qa.GetPosition().x - qb.GetPosition().x, qa.GetPosition().y - qb.GetPosition().y) <= _MERGE
                           for qa in _groups[a_] for qb in _groups[b_]):
                        _land[b_] = _land[a_]
            _merged = {}
            for _nm in _names: _merged.setdefault(_land[_nm], []).extend(_groups[_nm])   # never `n`: that is the rail's net
            _joined = {}
            for root, qs in _merged.items():
                _members = sorted({str(q.GetNumber()) for q in qs}, key=lambda t: (len(t), t))
                _joined[(_members[0] + "-" + _members[-1]) if len(_members) > 1 else _members[0]] = qs
            _groups = _joined
            _share = want[ref] / float(len(_groups))
            for _num, _inst in sorted(_groups.items()):
                pad = max(_inst, key=lambda q: q.GetBoundingBox().GetWidth() * q.GetBoundingBox().GetHeight())
                bb = pad.GetBoundingBox(); c = pad.GetPosition()
                # A PLATED HOLE IS ITS OWN CROSSING (21 September 2026, 02:54 CEST). Board P's four "declined" sites
                # since 19 September are its 12 AWG wire lands and its fuse (W_BP, W_N, W_P, F1: 18 and 25 barrels
                # asked at the source pad), board E's are J_BLK's wire lands, board A's its blade fuse holders:
                # every one a pad DRILLED THROUGH, with a wire or a pin soldered into the hole. The current enters
                # the board on every copper layer at once through the solder-filled hole, so there is no thin
                # barrel wall to size and no via a fixer could add beside it that carries anything the hole does
                # not already carry. This walk counted only VIAS near the pad and read the fanout's single via
                # as the whole crossing; the 19 September note called that "the limit of the question" and it
                # was the question asked of the wrong land. A site whose land is plated through is not judged
                # here, and is reported as a pin site so the reader sees the count go down for a reason.
                if any(getattr(q, "GetDrillSizeX", lambda: 0)() > 0 for q in _inst):
                    if pin_sites is not None:
                        _dq = max(_inst, key=lambda q: q.GetDrillSizeX())
                        pin_sites.append({"net": net, "ref": ref, "pad": _num, "at": (c.x / 1e6, c.y / 1e6),
                                          "drill": _dq.GetDrillSizeX() / 1e6, "amps": _share})
                    continue
                r0 = max(bb.GetWidth(), bb.GetHeight()) / 2 + reach_mm * 1e6
                near, _seen = [], set()
                for q in _inst:
                    qb = q.GetBoundingBox(); qc = q.GetPosition()
                    qr = max(qb.GetWidth(), qb.GetHeight()) / 2 + reach_mm * 1e6
                    for v in vias:
                        if id(v) in _seen or (v.GetNetname() or "").lstrip("/") != n: continue
                        if math.hypot(v.GetPosition().x - qc.x, v.GetPosition().y - qc.y) <= qr:
                            _seen.add(id(v)); near.append(v)
                if not near: continue           # no crossing at this pad: nothing to count
                if _one_layer:
                    # NOT A CROSSING: the net changes layer nowhere at generation, so the vias here are the
                    # fanout's stubs into bare laminate and a barrel count is owed only once a router crosses,
                    # which is the solved mesh's question. Reported, never counted, never given a cluster.
                    if one_layer_sites is not None:
                        one_layer_sites.append({"net": n, "ref": ref, "pad": _num, "at": (c.x / 1e6, c.y / 1e6),
                                                "have": len(near), "amps": _share, "one_layer": True,
                                                "why": "%s at %s pad %s lies on one layer at generation: a crossing "
                                                       "only if the router makes one, which via_current judges on "
                                                       "the solved mesh" % (n, ref, _num)})
                    continue
                judged += 1
                # A SITE OF MIXED DRILLS IS JUDGED ON WHAT ITS BARRELS CARRY, NOT AT ITS SMALLEST HOLE (21 September
                # 2026). Board E's largest declined site, VIN_RAW at L2 pad 2, holds the generator's TEN 0.50 mm
                # barrels (1.05 A each, 10.5 A together) and ONE 0.25 mm fanout via, and this line took the 0.25 as
                # the site's drill and asked for sixteen of them for 10 A: a false busbar, declined as a placement
                # item since 20 September on a crossing that already carries its current. Each barrel is rated at
                # its own drill and the site is short only when the sum falls below the share. The drill and ring
                # a NEW barrel takes are the LARGEST already there (the fixer copies a barrel of the site, and the
                # generator's 0.50 is the one it meant), never the fanout's minimum via.
                carried = sum(_vc.ampacity(v.GetDrill() / 1e6, 10.0)[0] for v in near)
                _big = max(near, key=lambda v: v.GetDrill())
                drill = _big.GetDrill() / 1e6
                # THE BARREL ALREADY THERE CARRIES THE RING SIZE TOO, and the fixer needs it: a barrel added
                # beside this one must be the same via, not a via of the fixer's own invention. `rail_barrels`
                # laid 0.70 mm rings on a 0.40 mm drill on board A's first real run and the DRC refused all
                # seven sites, because board A declares a 0.20 mm annular floor and that ring is 0.15.
                width = _kc_width(_big) / 1e6
                # THE BARRELS ALREADY THERE, by position, because the fixer adds to this cluster rather than
                # beside it: a lattice centred on the pad puts its own holes half a pitch from the barrel that
                # is already on the site, which is board A's seven `hole_to_hole` refusals of this morning.
                need = len(near) + (_vc.barrels_for(_share - carried, drill) if _share > carried else 0)
                # THE WINDOW DOES NOT GROW, AND THE FIXER FITS INSIDE IT (19 September 2026, after a version
                # that got this the wrong way round). Widening the window to cover the cluster an answer would
                # take was tried for one commit and it LOOSENED the question: re-taken on the same three board
                # files with nothing but the judge changed, board A read 5 short where it read 8, board B 3
                # where it read 5 and board E 2 where it read 4. A window grown by (need - 1) * pitch / 2 does
                # not count the answer, it counts the NEIGHBOURHOOD: on a site needing seven barrels it reaches
                # 2.4 mm and sweeps up every fanout via of the same rail that happens to be near, none of which
                # is at this crossing. So the window stays at the pad plus `reach_mm`, and the fixer is told
                # what it is: a crossing whose cluster does not fit within a millimetre of its own pad is a
                # site where the copper has to be DESIGNED, and `rail_barrels` declines it as a placement item
                # rather than half-answering it. `reach` travels in the row so the two cannot disagree.
                at_near = [(v.GetPosition().x / 1e6, v.GetPosition().y / 1e6) for v in near]
                if _share > carried:
                    short.append({
                        "net": n, "ref": ref, "pad": _num, "at": (c.x / 1e6, c.y / 1e6),
                        "drill": drill, "width": width, "near": at_near, "have": len(near), "need": need,
                        "carried": carried,
                        "reach": r0 / 1e6, "at_pad": (c.x / 1e6, c.y / 1e6), "amps": _share,
                        "part_amps": want[ref], "pads": len(_groups), "instances": len(_inst), "one_layer": _one_layer,
                        "why": "%s at %s pad %s (%.2f, %.2f): %d barrel(s) carrying %.2f A at a 10 K rise for %.2f A "
                               "(%.2f A over this part's %d pad(s) on the rail%s), which needs %d at %.2f mm%s"
                               % (n, ref, _num, c.x / 1e6, c.y / 1e6, len(near), carried, _share,
                                  want[ref], len(_groups),
                                  (", pads %s drawn as one land" % _num.replace("-", " to ")) if "-" in _num else ((", pad %s drawn as %d pieces of one land" % (_num, len(_inst))) if len(_inst) > 1 else ""),
                                  need, drill,
                                  " [the net lies on one layer at generation: a crossing only if the router makes one]" if _one_layer else "")})
    return short, judged


def main(a):
    if not a: print(__doc__); return 2
    path = a[0]
    # THE INTENT FILE IS NAMED AFTER THE PROJECT'S BOARD, not after the snapshot being read: a placed or
    # pre-route copy carries a suffix and its own directory is `out/` already. Strip both, and let a caller say.
    _stem = os.path.splitext(os.path.basename(path))[0]
    for _suf in ("-placed", "-preroute", "-par-routed", "-cleaned"):
        if _stem.endswith(_suf): _stem = _stem[: -len(_suf)]
    _vc.placed_snapshot_note("rail_crossings", path)
    _dir = os.path.dirname(os.path.abspath(path))
    if os.path.basename(_dir) == "out": _dir = os.path.dirname(_dir)
    ip = a[a.index("--intent") + 1] if "--intent" in a else os.path.join(_dir, "out", _stem + "-intent.json")
    if not os.path.exists(ip):
        print("rail_crossings: no intent file at %s, so no rail declares a current here" % ip); return 0
    rails = json.load(open(ip, encoding="utf-8")).get("rails") or {}
    import pcbnew
    b = pcbnew.LoadBoard(path)
    _pins, _one = [], []
    short, judged = judge(b, rails, pin_sites=_pins, one_layer_sites=_one)
    print("rail_crossings: %d crossing(s) of %d declared rail(s) carry the barrels their current needs, %d do not"
          % (judged - len(short), len(rails), len(short)))
    if _one:
        print("rail_crossings: %d site(s) lie on a net that changes layer nowhere at generation and are not judged "
              "(a crossing there is the router's to make and via_current's to judge): %s" % (len(_one), ", ".join(
                  "%s at %s pad %s (%.2f A)" % (x["net"], x["ref"], x["pad"], x["amps"]) for x in _one[:12])))
    if _pins:
        print("rail_crossings: %d site(s) are plated holes with a wire or a pin soldered through them, which carry "
              "their own crossing and are not judged: %s" % (len(_pins), ", ".join(
                  "%s at %s pad %s (%.1f mm drill, %.2f A)" % (x["net"], x["ref"], x["pad"], x["drill"], x["amps"]) for x in _pins[:12])))
    for s in short[:20]: print("rail_crossings:   %s" % s)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
