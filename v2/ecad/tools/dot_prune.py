#!/usr/bin/env python3
"""Remove a track that is a DOT: shorter than the process can draw, and standing on its own (MESHSAT-862,
16 September 2026).

Board E11 came back from its re-finish at hard 0 and unrouted 1, and the one open connection was this:

    Track [GND] on F.Cu, length 0.0002 mm   @ (3.8125, 208.3025)
    Pad 2 [GND] of U13 on F.Cu              @ (5.5375, 208.400)

Two tenths of a MICROMETRE of track. It is not a conductor and no fabricator draws it; what it is, is an island
of the GND net, and KiCad's connectivity is right to say the net has a piece that reaches nothing. The board
therefore reads one connection short, the finish refuses it, and a whole route round is spent on an artefact.

`cleanup_dangling.py` cannot see it: its first line skips every net that owns a zone, and GND owns several.
That skip is correct for its own job (a plane net's stubs are the pour's business) and it is what leaves this
class of artefact alive on exactly the nets most likely to carry it.

WHAT IT REMOVES, and nothing else: a TRACK whose length is under the threshold (default 5 micrometres, which is
two orders of magnitude under this fabricator's 0.09 mm minimum track) and which no other item of its net
touches, so it cannot be a bridge. A zero-length track still has a WIDTH, so it renders as a copper dot that
can genuinely join two things that both reach it: that case is kept, counted and named.

Everything is judged the way every other pass here is judged: the caller re-runs the DRC and reverts if the
board got worse. This tool also refuses to write when its own before-and-after connectivity says it lost a
connection.

Usage: dot_prune.py <board.kicad_pcb> [--dry] [--min-mm 0.005]
"""
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict


def main(a):
    if not a: print(__doc__); return verdict.USAGE
    path = a[0]; dry = "--dry" in a
    lim = float(a[a.index("--min-mm") + 1]) if "--min-mm" in a else 0.005
    import pcbnew
    mm = lambda v: v / 1e6
    b = pcbnew.LoadBoard(path)
    tracks = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]
    dots = []
    for t in tracks:
        s, e = t.GetStart(), t.GetEnd()
        if ((mm(s.x) - mm(e.x)) ** 2 + (mm(s.y) - mm(e.y)) ** 2) ** 0.5 < lim: dots.append(t)
    if not dots:
        print("dot_prune: no track under %.4f mm on this board" % lim)
        return verdict.write("dot_prune", verdict.PASS, counts={"dots": 0, "removed": 0},
                             denominator=len(tracks), inputs={"board": path},
                             note="nothing on this board is shorter than the process can draw",
                             out_dir=os.path.join(os.path.dirname(os.path.abspath(path)), "out"))

    # A DOT THAT TOUCHES TWO THINGS IS A BRIDGE, not an artefact: it is kept and named.
    def touches(t, other):
        r = mm(t.GetWidth()) / 2 + mm(other.GetWidth() if other.GetClass() != "PCB_VIA" else other.GetWidth()) / 2
        p = t.GetStart(); q = other.GetPosition() if other.GetClass() == "PCB_VIA" else None
        pts = [other.GetStart(), other.GetEnd()] if q is None else [q]
        return any(((mm(p.x) - mm(z.x)) ** 2 + (mm(p.y) - mm(z.y)) ** 2) ** 0.5 <= r for z in pts)

    take, keep = [], []
    for t in dots:
        net = t.GetNetname()
        others = [o for o in b.GetTracks() if o is not t and o.GetNetname() == net]
        n_touch = sum(1 for o in others if touches(t, o))
        pads = [p for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetname() == net
                and p.HitTest(t.GetStart())]
        if n_touch + len(pads) >= 2:
            keep.append("%s at (%.3f, %.3f): a dot of %.3f mm width touching %d item(s), which makes it a bridge"
                        % (net, mm(t.GetStart().x), mm(t.GetStart().y), mm(t.GetWidth()), n_touch + len(pads)))
        else:
            take.append(t)

    b.BuildConnectivity(); u0 = b.GetConnectivity().GetUnconnectedCount(False)
    names = ["%s at (%.4f, %.4f), %.6f mm long" % (t.GetNetname(), mm(t.GetStart().x), mm(t.GetStart().y),
             ((mm(t.GetStart().x) - mm(t.GetEnd().x)) ** 2 + (mm(t.GetStart().y) - mm(t.GetEnd().y)) ** 2) ** 0.5)
             for t in take]
    for t in take: b.Remove(t)
    b.BuildConnectivity(); u1 = b.GetConnectivity().GetUnconnectedCount(False)
    print("dot_prune: %d track(s) under %.4f mm; %d removable, %d kept as a bridge; unconnected %d -> %d"
          % (len(dots), lim, len(take), len(keep), u0, u1))
    for n in names[:10]: print("  removed %s" % n)
    for k in keep[:10]: print("  kept    %s" % k)
    if u1 > u0:
        print("dot_prune: removing them OPENED the board (%d -> %d): nothing written" % (u0, u1))
        return verdict.write("dot_prune", verdict.FAIL, counts={"dots": len(dots), "removed": 0},
                             denominator=len(tracks), evidence=names[:20], inputs={"board": path},
                             note="a dot that looked like an artefact was carrying a connection",
                             out_dir=os.path.join(os.path.dirname(os.path.abspath(path)), "out"))
    if take and not dry:
        pcbnew.SaveBoard(path, b)
    return verdict.write("dot_prune", verdict.PASS,
                         counts={"dots": len(dots), "removed": 0 if dry else len(take), "kept_as_bridge": len(keep)},
                         denominator=len(tracks), evidence=names[:20], inputs={"board": path},
                         note="a track shorter than the process can draw is an island, not a conductor",
                         out_dir=os.path.join(os.path.dirname(os.path.abspath(path)), "out"))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
