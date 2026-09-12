#!/usr/bin/env python3
"""Remove a locked stitch via that the pour has abandoned (MESHSAT-862, 11 September 2026).

A placement generator lays a grid of LOCKED stitch vias to bond a pour to its plane. The router then runs a
track past one, the fill retreats by its clearance, and the via's pour end is left touching nothing: dead
copper with a stub on the other side. `check_pcb_p.py` calls it out ("locked via GND at (84.5, 98.1) sits in
the fill of 'GND pour B.Cu'") and it is right to; `cleanup_dangling.py` leaves it alone because a via with a
track end on it is not dangling by its rule. Board P routed 0 hard and 0 unrouted and was refused for exactly
one of these.

What it removes, and only this: a via that is LOCKED, whose net has a filled zone whose OUTLINE contains it and
whose FILL does not, and which carries at most one track end. The stub that lands on it goes with it when that
stub touches nothing else at its far end. Everything is judged on a copy: the caller re-runs DRC and reverts if
unrouted rose, the same contract `stub_accept.py` works under.

Usage: stitch_prune.py <board.kicad_pcb> [--dry]   exit 0 always (it is a cleanup, not a gate); writes a verdict.
"""
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict


def main(a):
    if not a: print(__doc__); return verdict.USAGE
    path = a[0]; dry = "--dry" in a
    import pcbnew
    b = pcbnew.LoadBoard(path)
    zones = [z for z in b.Zones() if not z.GetIsRuleArea()]
    tracks = list(b.GetTracks())
    vias = [t for t in tracks if t.Type() == pcbnew.PCB_VIA_T]
    segs = [t for t in tracks if t.GetClass() == "PCB_TRACK"]

    def ends_on(pt, net, skip=None, layer=None):
        out = []
        for tr in segs:
            if tr is skip or tr.GetNetname() != net: continue
            if layer is not None and tr.GetLayer() != layer: continue
            for e in (tr.GetStart(), tr.GetEnd()):
                if abs(e.x - pt.x) < 20000 and abs(e.y - pt.y) < 20000: out.append(tr); break
        return out

    def pad_at(pt, net, layer=None):
        """A pad of this net at this point, on this layer when one is named.

        12 September 2026: without the layer this answered True for board P's thermal via in U1's exposed
        pad, which is F.Cu only, and so declared the via live on B.Cu as well. A pad that exists on one
        layer says nothing about the other end of a via."""
        for f in b.GetFootprints():
            for p in f.Pads():
                if p.GetNetname() != net or not p.HitTest(pt): continue
                if layer is None or p.IsOnLayer(layer): return True
        return False

    removed, kept, evidence = 0, 0, []
    for v in vias:
        if not v.IsLocked(): continue
        net = v.GetNetname()
        if not net: continue
        pos = v.GetPosition()
        # A via is abandoned only when NO zone of its net fills it on ANY layer. The first version broke at the
        # first zone whose outline contained it and whose fill did not, so a via whose F.Cu end sat in the F.Cu
        # ground fill and whose B.Cu end had been pushed out of the B.Cu fill read as abandoned and would have
        # been removed with its connection intact. A multi-layer zone had the same fault through
        # GetFirstLayer() (reviewer, 11 September 2026). Both are one question: is this via in ANY fill?
        abandoned, filled_anywhere = None, False
        for z in zones:
            if z.GetNetname() != net: continue
            try:
                if not z.Outline().Contains(pos): continue
            except Exception:
                continue
            for _L in (list(z.GetLayerSet().Seq()) or [z.GetFirstLayer()]):
                try:
                    if z.GetFilledPolysList(_L).Contains(pos): filled_anywhere = True; break
                except Exception:
                    continue
            if filled_anywhere: break
            if abandoned is None: abandoned = z
        if filled_anywhere: abandoned = None
        if abandoned is None: continue
        on = ends_on(pos, net)
        # A TRACK COUNT IS NOT A CONNECTION TEST, and this is what board P proved on 12 September 2026. The rule
        # was "more than one track lands on it, so it is alive", and P's one refused via has TWO tracks on it,
        # both on F.Cu, on a via that spans F.Cu to B.Cu with the B.Cu fill retreated: dead at its pour end,
        # which is the exact defect this tool exists for, and it was reported as the reason to leave it. The
        # question is per END: a via is alive only if each of the two layers it spans carries something of its
        # net, a track landing on it or a pad under it. (The fill is already answered above: `filled_anywhere`
        # is false by the time we are here, on every layer.)
        top, bot = v.TopLayer(), v.BottomLayer()
        live = [L for L in (top, bot) if ends_on(pos, net, layer=L) or pad_at(pos, net, layer=L)]
        if len(live) == 2:
            kept += 1
            evidence.append("%s at (%.1f, %.1f): live on both %s and %s, left alone"
                            % (net, pos.x / 1e6, pos.y / 1e6, b.GetLayerName(top), b.GetLayerName(bot)))
            continue
        if len(on) > 1:
            # Several tracks, all on ONE of its two layers: the via is dead at the other end and the tracks are
            # not. Take the via and leave every track where it is; finish.sh re-runs the DRC and reverts if the
            # unrouted count rose, which is the contract this tool works under.
            evidence.append("%s at (%.1f, %.1f): %d track(s) on %s and nothing on %s, dead at its %s end"
                            % (net, pos.x / 1e6, pos.y / 1e6, len(on),
                               b.GetLayerName(live[0]) if live else "neither layer",
                               b.GetLayerName(bot if (live and live[0] == top) else top),
                               b.GetLayerName(bot if (live and live[0] == top) else top)))
            if not dry: b.Remove(v)
            removed += 1
            continue
        stub = on[0] if on else None
        if stub is not None:
            far = stub.GetEnd() if abs(stub.GetStart().x - pos.x) < 20000 and abs(stub.GetStart().y - pos.y) < 20000 else stub.GetStart()
            # The far end reaching a pad or another track is the SAFE case, not the risky one: the network on
            # that side survives the removal, and the branch being removed is dead at the pour end anyway. The
            # first version of this had the test the other way round and so left the only via it found in place
            # (11 September 2026). A far end touching nothing is a dangling stub and cleanup_dangling's job,
            # so it is left here rather than removed twice by two tools with different rules.
            if not (pad_at(far, net) or ends_on(far, net, skip=stub)):
                kept += 1
                evidence.append("%s at (%.1f, %.1f): its stub hangs free at the far end, left to cleanup_dangling" % (net, pos.x / 1e6, pos.y / 1e6))
                continue
        evidence.append("%s at (%.1f, %.1f): abandoned by the fill of '%s'%s" %
                        (net, pos.x / 1e6, pos.y / 1e6, abandoned.GetZoneName() or "unnamed",
                         ", with its %.2f mm stub" % pcbnew.ToMM(stub.GetLength()) if stub is not None else ""))
        if not dry:
            if stub is not None: b.Remove(stub)
            b.Remove(v)
        removed += 1
    if removed and not dry:
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.SaveBoard(path, b)
    print("stitch_prune: %d locked via(s) removed, %d left alone, of %d locked via(s) on %d zone(s)%s"
          % (removed, kept, sum(1 for v in vias if v.IsLocked()), len(zones), " (dry run)" if dry else ""))
    for e in evidence[:8]: print("   " + e)
    return verdict.write("stitch_prune", verdict.PASS,
                         counts={"removed": removed, "left_alone": kept,
                                 "locked_vias": sum(1 for v in vias if v.IsLocked())},
                         denominator=sum(1 for v in vias if v.IsLocked()),
                         evidence=evidence[:20], inputs={"board": path},
                         note="a locked stitch via the fill no longer covers is dead at its pour end")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
