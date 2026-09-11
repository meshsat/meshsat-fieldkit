#!/usr/bin/env python3
"""Are two board files the same BOARD? (MESHSAT-862, stage 0b, 11 September 2026.)

`cmp` cannot answer this and neither can `diff`. KiCad mints a fresh `(uuid ...)` for every item it writes,
so two runs of one chain on one input differ on thousands of lines that carry no geometry at all; and a
footprint written in a different position in the file makes `diff` report its whole block as changed when
nothing about it moved. The first determinism measurement of 11 September read 26,142 differing lines of
36,724 on C and the largest bucket was `(uuid`, which says nothing.

So this reads both boards through pcbnew and compares what a board IS: where each footprint sits, what
copper exists, and which net each piece belongs to. Identity, not file order:

  footprints   keyed by reference: library id, position in nm, orientation, side, and the net of every pad
  tracks       a multiset of (layer, start, end, width, net) with the two ends ordered, so a segment drawn
               the other way round is the same segment
  vias         a multiset of (position, drill, diameter, net, layer span)
  zones        keyed by (net, layer, priority, rule-area flag) with the outline's corners in order
  rule areas   the same, because a keep-out is geometry the router obeys

UUIDs, timestamps, the title block and file order are ignored on purpose, and this docstring is the record
of that decision: they are not properties of the board.

Usage: board_diff.py <a.kicad_pcb> <b.kicad_pcb> [--verbose]
       exit 0 identical, 1 different, 3 a board that could not be read; writes out/board_diff.verdict.json
"""
import sys, os, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict


def _xy(p): return (p.x, p.y)


def summarise(path):
    import pcbnew
    b = pcbnew.LoadBoard(path)
    fps = {}
    for f in b.GetFootprints():
        pads = sorted((p.GetNumber(), p.GetNetname(), _xy(p.GetPosition()), (p.GetSize().x, p.GetSize().y))
                      for p in f.Pads())
        fps[f.GetReference()] = (str(f.GetFPIDAsString()), _xy(f.GetPosition()),
                                 round(f.GetOrientationDegrees(), 3), f.GetLayerName(), tuple(pads))
    tracks, vias = collections.Counter(), collections.Counter()
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            vias[(_xy(t.GetPosition()), t.GetDrillValue(), t.GetWidth(), t.GetNetname(),
                  b.GetLayerName(t.TopLayer()), b.GetLayerName(t.BottomLayer()))] += 1
        else:
            a, z = _xy(t.GetStart()), _xy(t.GetEnd())
            if z < a: a, z = z, a          # a segment drawn the other way round is the same segment
            tracks[(b.GetLayerName(t.GetLayer()), a, z, t.GetWidth(), t.GetNetname(), t.IsLocked())] += 1
    zones = {}
    for z in b.Zones():
        corners = []
        o = z.Outline()
        for oi in range(o.OutlineCount()):
            ln = o.Outline(oi)
            corners.append(tuple((ln.CPoint(i).x, ln.CPoint(i).y) for i in range(ln.PointCount())))
        key = (z.GetNetname(), b.GetLayerName(z.GetLayer()), z.GetAssignedPriority(), bool(z.GetIsRuleArea()),
               z.GetZoneName())
        zones.setdefault(key, []).append(tuple(corners))
    return {"footprints": fps, "tracks": tracks, "vias": vias,
            "zones": {k: sorted(v) for k, v in zones.items()}}


def compare(A, B, verbose=False):
    ev, counts = [], {}

    ka, kb = set(A["footprints"]), set(B["footprints"])
    for r in sorted(ka - kb): ev.append("footprint %s only in the first board" % r)
    for r in sorted(kb - ka): ev.append("footprint %s only in the second board" % r)
    moved = [r for r in sorted(ka & kb) if A["footprints"][r] != B["footprints"][r]]
    for r in moved[:20]:
        a, c = A["footprints"][r], B["footprints"][r]
        what = [n for n, i in (("library id", 0), ("position", 1), ("orientation", 2), ("side", 3), ("pads", 4))
                if a[i] != c[i]]
        ev.append("footprint %s differs in %s: %s against %s"
                  % (r, " and ".join(what), a[1] if "position" in what else a[2], c[1] if "position" in what else c[2]))
    counts["footprints"] = len(ka | kb)
    counts["footprints_differing"] = len(moved) + len(ka ^ kb)

    for name in ("tracks", "vias"):
        a, c = A[name], B[name]
        only_a, only_c = a - c, c - a
        counts[name] = sum(a.values())
        counts["%s_differing" % name] = sum(only_a.values()) + sum(only_c.values())
        for k, n in list(only_a.items())[:10]: ev.append("%s only in the first board (x%d): %s" % (name[:-1], n, k))
        for k, n in list(only_c.items())[:10]: ev.append("%s only in the second board (x%d): %s" % (name[:-1], n, k))

    za, zb = set(A["zones"]), set(B["zones"])
    zdiff = [k for k in sorted(za & zb) if A["zones"][k] != B["zones"][k]]
    for k in sorted(za - zb)[:10]: ev.append("zone %s only in the first board" % (k,))
    for k in sorted(zb - za)[:10]: ev.append("zone %s only in the second board" % (k,))
    for k in zdiff[:10]: ev.append("zone %s has a different outline" % (k,))
    counts["zones"] = len(za | zb)
    counts["zones_differing"] = len(zdiff) + len(za ^ zb)

    total = sum(counts[k] for k in ("footprints", "tracks", "vias", "zones"))
    diff = sum(counts[k] for k in counts if k.endswith("_differing"))
    return diff, total, counts, ev


def main(a):
    if len(a) < 2: print(__doc__); return verdict.USAGE
    try:
        A, B = summarise(a[0]), summarise(a[1])
    except Exception as e:
        print("board_diff: could not read a board (%s)" % e)
        return verdict.write("board_diff", verdict.INCONCLUSIVE, denominator=0,
                             inputs={"a": a[0], "b": a[1]}, note=str(e))
    diff, total, counts, ev = compare(A, B, "--verbose" in a)
    for line in (ev if "--verbose" in a else ev[:12]): print("board_diff: " + str(line)[:200])
    print("board_diff: %d of %d board items differ (%s)"
          % (diff, total, ", ".join("%s %d of %d" % (k.replace("_differing", ""), counts[k],
                                                     counts[k.replace("_differing", "")])
                                    for k in sorted(counts) if k.endswith("_differing"))))
    return verdict.write("board_diff", verdict.PASS if diff == 0 else verdict.FAIL,
                         counts=counts, denominator=total, evidence=[str(e) for e in ev],
                         inputs={"a": a[0], "b": a[1]},
                         note="uuids, file order and the title block are not properties of the board")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
