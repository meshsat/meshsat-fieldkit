#!/usr/bin/env python3
"""The nodes where a few millivolts change the answer (rule ANA-001, MESHSAT-862, 16 September 2026).

ANA-001 asks for a list per board of the sensitive nodes with, for each, its reference, its filter and its
clearance from switching nodes, and Kelvin connections where the measurement demands it. It read "generation
intends to comply and nothing verifies it" on four boards.

`pcb_sensitive.yaml` is the list. This gate has two halves and runs whichever it can:

  THE NETLIST HALF, everywhere: every declared node is a net that exists, every Kelvin pairing is mutual (if A
  says its partner is B, B must say A: a one-sided Kelvin declaration is a note somebody wrote, not a pair),
  and no board declares a node without a filter.

  THE BOARD HALF, where pcbnew is: the real distance from each sensitive net's copper to the copper of any
  SWITCHING net, measured on the routed board, reported beside the clearance the board asked for. A node
  closer than its own `keep_mm` is a failure; the measured distance travels in the verdict either way, so the
  number can be argued with from evidence rather than defended.

The `keep_mm` values are this project's own and no standard in this tree sets them, which is recorded in the
rule's coverage note rather than hidden here.

Usage: sensitive_nodes.py <board.kicad_pcb> [--board <letter>] [--sensitive pcb_sensitive.yaml] [--json]
"""
import os, re, sys, json, glob, math, fnmatch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

ECAD = os.path.dirname(HERE)
SENS = os.path.join(HERE, "pcb_sensitive.yaml")


def _nets_of(board):
    return {str(n) for n in board.GetNetInfo().NetsByName().keys()}


def _copper(board, netname):
    """Every track and via of a net as ((x0,y0),(x1,y1),width,layer) in mm.

    THE LAYER IS PART OF THE ANSWER (16 September 2026). The first version compared every segment with every
    other and reported board A's FE_CS as running -0.212 mm from the switch node, a negative gap, because the
    sense line runs UNDER the switch node on another layer. Copper on two layers cannot be 0.2 mm apart in the
    plane and touching: the clearance question is a same-layer question, and the layers question is a
    different one (capacitive coupling through the dielectric), which is reported separately rather than
    folded into a number that cannot mean what it says.

    A via spans layers, so it is given the layer `None`, which matches anything: a via of a switch node beside
    a sense track is a real clearance case whatever layer the track is on."""
    import pcbnew
    out = []
    for t in board.GetTracks():
        if str(t.GetNetname()).lstrip("/") != netname.lstrip("/"): continue
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition(); out.append(((p.x / 1e6, p.y / 1e6), (p.x / 1e6, p.y / 1e6), t.GetWidth() / 1e6, None))
        else:
            a, b = t.GetStart(), t.GetEnd()
            out.append(((a.x / 1e6, a.y / 1e6), (b.x / 1e6, b.y / 1e6), t.GetWidth() / 1e6, t.GetLayer()))
    return out


def _seg_distance(s1, s2):
    """Centreline distance between two segments, minus half of each width: the copper-to-copper gap."""
    import math
    (a, b, w1, _l1), (c, d, w2, _l2) = s1, s2

    def pt_seg(p, q, r):
        px, py = p; qx, qy = q; rx, ry = r
        dx, dy = rx - qx, ry - qy
        if dx == dy == 0: return math.hypot(px - qx, py - qy)
        t = max(0.0, min(1.0, ((px - qx) * dx + (py - qy) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - (qx + t * dx), py - (qy + t * dy))

    d0 = min(pt_seg(a, c, d), pt_seg(b, c, d), pt_seg(c, a, b), pt_seg(d, a, b))
    return d0 - (w1 + w2) / 2.0


def judge(board_path=None, letter=None, sens=None):
    import yaml
    doc = yaml.safe_load(open(sens or SENS, encoding="utf-8"))
    b = (doc.get("boards") or {}).get((letter or "").lower())
    if b is None:
        return dict(declared=0, fails=[], notes=["board %s declares no sensitive node list" % (letter or "?").upper()],
                    measured=[], applicable=False)
    nodes = b.get("nodes") or []
    fails, notes, measured = [], [], []
    by_net = {str(n.get("net")): n for n in nodes}
    for n in nodes:
        if not str(n.get("filter", "")).strip():
            fails.append("%s carries no filter" % n.get("net"))
        k = n.get("kelvin_with")
        if k:
            other = by_net.get(str(k))
            if other is None:
                fails.append("%s names %s as its Kelvin partner and %s is not declared" % (n.get("net"), k, k))
            elif str(other.get("kelvin_with") or "") != str(n.get("net")):
                fails.append("%s says its Kelvin partner is %s and %s does not say the same: a one-sided "
                             "Kelvin declaration is a note, not a pair" % (n.get("net"), k, k))
    try:
        import pcbnew
    except Exception:
        notes.append("pcbnew is not importable here, so only the netlist half was judged")
        return dict(declared=len(nodes), fails=fails, notes=notes, measured=[], applicable=True)
    if not board_path or not os.path.exists(board_path):
        notes.append("no board file given, so only the netlist half was judged")
        return dict(declared=len(nodes), fails=fails, notes=notes, measured=[], applicable=True)
    board = pcbnew.LoadBoard(board_path)
    names = {n.lstrip("/") for n in _nets_of(board)}
    for n in nodes:
        if str(n.get("net")) not in names:
            fails.append("%s is declared sensitive and the board has no such net" % n.get("net"))
    pats = b.get("switch_nets") or []
    sw = sorted({x for x in names if any(fnmatch.fnmatchcase(x, p) for p in pats)})
    if not sw:
        notes.append("this board has no switching net matching its own patterns, so only the declaration was judged")
        return dict(declared=len(nodes), fails=fails, notes=notes, measured=[], applicable=True)
    sw_copper = {s: _copper(board, s) for s in sw}
    for n in nodes:
        net = str(n.get("net"))
        if net not in names: continue
        mine = _copper(board, net)
        best, who, over, over_who = None, None, None, None
        for s, segs in sw_copper.items():
            for m in mine:
                for o in segs:
                    same = (m[3] is None or o[3] is None or m[3] == o[3])
                    d = _seg_distance(m, o)
                    if same:
                        if best is None or d < best: best, who = d, s
                    elif d < 0 and (over is None or d < over):
                        over, over_who = d, s       # it runs UNDER the switch node: a different question
        if over is not None:
            notes.append("%s runs under %s on another layer for at least %.2f mm of overlap: that is coupling "
                         "through the dielectric rather than a clearance, and this list sets no number for it"
                         % (net, over_who, abs(over)))
        if best is None: continue
        # HOW FAR FROM THE PART THAT JOINS THEM, AND FOR HOW LONG (16 September 2026). A current-sense line and
        # a switching node are adjacent BY CONSTRUCTION at the FET that makes both of them: the LM5176's low
        # side has its source on CS and its drain on SW, so the first fraction of a millimetre out of those two
        # pins is close whatever the router does, and a rule that reports only the smallest gap cannot tell
        # that from a sense line running beside a switch node for twenty millimetres. Both numbers are measured
        # now: the distance from the violation to the nearest pad of a part that touches BOTH nets, and the
        # length over which the two run inside the limit. A gap at the shared part's own pins is geometry; a
        # long parallel run is a routing decision, and only the second is something to fix on this board.
        _keep = None if n.get("keep_mm") is None else float(n["keep_mm"])
        _at_part, _run_mm = None, 0.0
        if _keep is not None and best < _keep - 1e-9:
            _shared = []
            for fp in board.GetFootprints():
                _pn = {str(pd.GetNetname()).lstrip("/") for pd in fp.Pads()}
                if net in _pn and who in _pn:
                    for pd in fp.Pads():
                        _p = pd.GetPosition(); _shared.append((_p.x / 1e6, _p.y / 1e6))
            for m in mine:
                for o in sw_copper.get(who, []):
                    if not (m[3] is None or o[3] is None or m[3] == o[3]): continue
                    d = _seg_distance(m, o)
                    if d >= _keep - 1e-9: continue
                    _len = min(math.hypot(m[1][0] - m[0][0], m[1][1] - m[0][1]),
                               math.hypot(o[1][0] - o[0][0], o[1][1] - o[0][1]))
                    _run_mm += _len
                    _mid = ((m[0][0] + m[1][0]) / 2.0, (m[0][1] + m[1][1]) / 2.0)
                    for _sp in _shared:
                        _dd = math.hypot(_mid[0] - _sp[0], _mid[1] - _sp[1])
                        if _at_part is None or _dd < _at_part: _at_part = _dd
        measured.append(dict(net=net, nearest_switch=who, gap_mm=round(best, 3), keep_mm=n.get("keep_mm"),
                             run_within_limit_mm=round(_run_mm, 2),
                             mm_from_the_part_that_joins_them=None if _at_part is None else round(_at_part, 2)))
        if _keep is not None and best < _keep - 1e-9:
            _where = ("%.2f mm from the pads of the part that carries both nets" % _at_part
                      if _at_part is not None else "with no part carrying both nets on this board")
            fails.append("%s runs %.3f mm from %s and its own list asks for %.2f; the two are inside that "
                         "limit over %.2f mm of copper, %s"
                         % (net, best, who, _keep, _run_mm, _where))
    return dict(declared=len(nodes), fails=fails, notes=notes, measured=measured, applicable=True)


def main(argv):
    board = argv[0] if argv and not argv[0].startswith("--") else None
    letter = argv[argv.index("--board") + 1] if "--board" in argv else None
    sens = argv[argv.index("--sensitive") + 1] if "--sensitive" in argv else None
    if not letter and board:
        try:
            import sch_prov
            letter = sch_prov.letter_for(os.path.basename(board).rsplit(".", 1)[0])
        except Exception: pass
    r = judge(board, letter, sens)
    if not r.get("applicable"):
        print("sensitive_nodes: %s" % (r["notes"][0] if r["notes"] else "no list for this board"))
        return _v.write("sensitive_nodes", _v.INCONCLUSIVE, denominator=0, rules=["ANA-001"],
                        inputs={"board": letter}, note="this board declares no sensitive-node list")
    print("sensitive_nodes: %d declared node(s), %d measured against switching copper" % (r["declared"], len(r["measured"])))
    for m in sorted(r["measured"], key=lambda x: x["gap_mm"])[:10]:
        print("  %-14s %6.3f mm from %-10s (asks %.2f)" % (m["net"], m["gap_mm"], m["nearest_switch"], m["keep_mm"] or 0))
    for n in r["notes"]: print("  note %s" % n)
    for f in r["fails"]: print("  FAIL %s" % f)
    if "--json" in argv: print(json.dumps(r, indent=1))
    res = _v.FAIL if r["fails"] else _v.PASS
    return _v.write("sensitive_nodes", res, rules=["ANA-001"],
                    counts={"declared": r["declared"], "measured": len(r["measured"]), "fail": len(r["fails"])},
                    denominator=max(1, r["declared"]), evidence=r["fails"][:20],
                    inputs={"board": letter, "list": os.path.basename(sens or SENS)},
                    note="every sensitive node declared with its filter and its Kelvin partner where the "
                         "measurement is a difference, and, where pcbnew is present, the real distance from "
                         "each one to the nearest switching copper measured on the routed board and reported "
                         "beside the clearance the board asks for. The clearances are this project's own")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
