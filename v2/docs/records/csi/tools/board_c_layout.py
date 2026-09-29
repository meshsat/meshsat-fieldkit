#!/usr/bin/env python3
"""Board C's allowance nets on a placed or routed board file (stream csi, MESHSAT-1357, 29 September 2026; the independent
check's B3). A DRAFT instrument for the owner of board C's layout generator, not a gate: it decides no rule.

For every net that an edge_allow entry of tools/boards/c.json names (the entries' max_mm, read from the tree it runs in):
  * the routed length, summed over every track segment and arc on the net as edge_length.routed_main sums it, its vias
    and its layers, against max_mm (the ratio);
  * the PLACEMENT LOWER BOUND: the largest distance between any two pads of the net. Any copper that connects the net
    is at least that long, so a placement whose bound is past max_mm cannot meet the allowance however it is routed.
    It is a necessary condition only: a placement under it may still route long.
Usage: board_c_layout.py <board.kicad_pcb> [--table <boards/c.json>]     exit 1 when any net is past its limit or its
placement cannot meet it, 0 otherwise, 2 on usage."""
import fnmatch, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from measure_minimal import parse, kid, xy, arc_len

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))


def net_of(item, names):
    """The net name of a track, an arc, a via or a pad: KiCad 9 writes (net <code>) or (net <code> "<name>"), KiCad 10
    (net "<name>")."""
    n = kid(item, "net")
    if not n or len(n) < 2: return None
    if len(n) >= 3: return n[2]
    try: return names[int(n[1])]
    except ValueError: return n[1]


def board(text):
    """({net: length}, {net: vias}, {net: layers}, {net: [(ref, pad, x, y)]}) of a board file."""
    root = parse(text)
    names = {int(e[1]): e[2] for e in root if isinstance(e, list) and e and e[0] == "net" and len(e) >= 3}
    L, V, Ly, pads = {}, {}, {}, {}
    for it in root:
        if not isinstance(it, list) or not it: continue
        if it[0] in ("segment", "arc"):
            n = net_of(it, names)
            s, e = xy(kid(it, "start")), xy(kid(it, "end"))
            L[n] = L.get(n, 0.0) + (math.dist(s, e) if it[0] == "segment" else arc_len(s, xy(kid(it, "mid")), e))
            Ly.setdefault(n, set()).add(kid(it, "layer")[1])
        elif it[0] == "via":
            n = net_of(it, names); V[n] = V.get(n, 0) + 1
        elif it[0] == "footprint":
            at = kid(it, "at"); fx, fy = float(at[1]), float(at[2]); fr = math.radians(float(at[3]) if len(at) > 3 else 0.0)
            ref = next((e[2] for e in it if isinstance(e, list) and e[:2] == ["property", "Reference"]), None)
            for pd in it:
                if not (isinstance(pd, list) and pd and pd[0] == "pad"): continue
                n = net_of(pd, names)
                if not n: continue
                pa = kid(pd, "at"); px, py = float(pa[1]), float(pa[2])
                # KiCad rotates a footprint counter-clockwise on the page, whose y axis points down
                x = fx + px * math.cos(fr) + py * math.sin(fr)
                y = fy - px * math.sin(fr) + py * math.cos(fr)
                pads.setdefault(n, []).append((ref, pd[1], x, y))
    return L, V, Ly, pads


def main(argv):
    if not argv: print(__doc__); return 2
    tab = argv[argv.index("--table") + 1] if "--table" in argv else os.path.join(REPO, "v2", "ecad", "tools", "boards", "c.json")
    allow = json.load(open(tab, encoding="utf-8")).get("edge_allow") or []
    L, V, Ly, pads = board(open(argv[0], encoding="utf-8").read())
    print("== %s: board C's edge_allow nets, routed length and placement lower bound against max_mm" % os.path.basename(argv[0]))
    print("   %-10s %7s %9s %6s %5s  %-10s %9s  %s" % ("net", "max_mm", "routed", "ratio", "vias", "layers", "pads_far", "the farthest pads"))
    bad = 0
    for n in sorted(k for k in set(L) | set(pads) if k):
        nm = n.lstrip("/")
        e = next((e for e in allow if fnmatch.fnmatch(nm, e.get("pattern", ""))), None)
        if e is None or e.get("max_mm") is None: continue
        mm = float(e["max_mm"])
        ps = pads.get(n, [])
        far, pair = 0.0, ("", "")
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                d = math.dist(ps[i][2:], ps[j][2:])
                if d > far: far, pair = d, ("%s.%s" % ps[i][:2], "%s.%s" % ps[j][:2])
        r = L.get(n, 0.0)
        over = r > mm or far > mm
        bad += over
        print("   %-10s %7.1f %7.2f mm %6.1f %5d  %-10s %6.2f mm  %s to %s%s" % (
            nm, mm, r, r / mm, V.get(n, 0), ",".join(sorted(Ly.get(n, ()))) or "-", far, pair[0], pair[1],
            "   PAST" if r > mm else "", ) + ("   PLACEMENT CANNOT MEET IT" if far > mm else ""))
    print("board_c_layout: %d net(s) past their limit or with a placement that cannot meet it" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
