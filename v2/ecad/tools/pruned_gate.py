#!/usr/bin/env python3
"""The pruned-escape gate (MESHSAT-862, 8 Sep 2026): escape_prune.py removes an escape whose stub sits in a hard violation and leaves the pad to
the router with only a count printed; on a 0.4 mm receptacle row that pad can end with no via site on any layer (the A19 SDA case) and no gate
saw it. escape_prune.py now writes out/<name>-pruned.txt (net, ref, pad, x, y); this gate reads the routed board and requires every listed pad
to be reached by a track or a via of its net (a track end or a via centre within the pad's bounding box grown by 0.05 mm).

Usage: pruned_gate.py <board.kicad_pcb> <pruned.txt>  -> one line per pad, `pruned_gate: N of M pruned pads reached`, exit 1 if any is not."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict

def main(a):
    if len(a) < 2: print(__doc__); return 2
    # escape_prune.py ALWAYS writes this file, "# none pruned" included, so its absence means the prune step did not
    # run. That was a silent pass here, which is the shape of every defect this stage exists to remove. 11 Sep 2026.
    if not os.path.exists(a[1]):
        print("pruned_gate: no pruned list at %s: escape_prune.py did not run, so nothing was judged" % a[1])
        return verdict.write("pruned_gate", verdict.INCONCLUSIVE, counts={"reached": 0}, denominator=0,
                             inputs={"board": a[0]}, note="no pruned list at %s" % a[1])
    rows = [l.split("\t") for l in open(a[1]).read().splitlines() if l and not l.startswith("#")]
    # pcbnew is imported HERE and not at the top: the "no pruned list" answer above is a real verdict about a
    # step that did not run, and a gate must be able to say that on a host without KiCad. 11 September 2026.
    import pcbnew
    b = pcbnew.LoadBoard(a[0]); bad = 0; unreached = []
    pads = {(f.GetReference(), p.GetNumber()): p for f in b.GetFootprints() for p in f.Pads()}
    for net, ref, num, x, y in rows:
        p = pads.get((ref, num))
        if p is None:
            print("pruned_gate: FAIL %s %s.%s not on the board" % (net, ref, num))
            bad += 1; unreached.append("%s %s.%s not on the board" % (net, ref, num)); continue
        bb = p.GetBoundingBox(); bb.Inflate(int(0.05e6)); hit = False
        for t in b.GetTracks():
            if t.GetNetname() != p.GetNetname(): continue
            pts = [t.GetPosition()] if t.GetClass() == "PCB_VIA" else [t.GetStart(), t.GetEnd()]
            if any(bb.Contains(q) for q in pts): hit = True; break
        print("pruned_gate: %s %s %s.%s at (%s, %s) %s" % ("PASS" if hit else "FAIL", net, ref, num, x, y, "reached by its net" if hit else "NOT reached: no track end or via on the pad"))
        if not hit: bad += 1; unreached.append("%s %s.%s at (%s, %s) not reached by its net" % (net, ref, num, x, y))
    print("pruned_gate: %d of %d pruned pads reached" % (len(rows) - bad, len(rows)))
    return verdict.write("pruned_gate", verdict.PASS if not bad else verdict.FAIL,
                         counts={"reached": len(rows) - bad, "not_reached": bad},
                         denominator=len(rows), evidence=unreached[:30],
                         inputs={"board": a[0], "pruned": a[1]})

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
