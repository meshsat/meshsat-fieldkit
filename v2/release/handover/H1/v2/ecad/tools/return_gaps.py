#!/usr/bin/env python3
"""Where rule 1's uncovered millimetres ARE (15 September 2026, MESHSAT-862). intent_checks item 1 reports, per signal net, how many
millimetres of track have no ground or power fill on a neighbouring layer; this prints the RUNS behind that number so the cause can
be fixed in a generator: for every net over its limit, each uncovered run with its layer, its ends, its length and what sits on the
neighbouring layers at its midpoint (a track of another net, a pad, a via, a rule area, or nothing at all, which is the fill's own
edge or a slot). Same sampling and the same plane set as the gate, so the totals agree with the gate's line.

Usage: return_gaps.py <board.kicad_pcb> [--all] [--top N]     (--all prints every judged net, not only those over the limit)"""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew, intent, netclass, signalnets, signal_class
from intent_checks import SAMPLE, GAP_MM


def main(a):
    path = a[0]; want_all = "--all" in a; top = int(a[a.index("--top") + 1]) if "--top" in a else 8
    b = pcbnew.LoadBoard(path); it = intent.load(path) or {}
    try: pcbnew.ZONE_FILLER(b).Fill(b.Zones())   # a saved board can carry stale or empty fills; the gate judges the filled board
    except Exception: pass
    pro = os.path.splitext(path)[0] + ".kicad_pro"; assign = json.load(open(pro)).get("net_settings", {}).get("netclass_assignments", {}) if os.path.exists(pro) else {}
    cu = list(b.GetEnabledLayers().CuStack())
    planes = {}
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetFilledArea() <= 0: continue
        n = z.GetNetname().lstrip("/")
        if n: planes.setdefault(z.GetFirstLayer(), []).append(z.GetFilledPolysList(z.GetFirstLayer()))   # every filled zone, as the gate counts it
    def neighbours(L):
        i = cu.index(L); return [cu[j] for j in (i - 1, i + 1) if 0 <= j < len(cu)]
    targets = {k for k, v in it.get("pair_classes", {}).items() if v}
    signals, _ = signalnets.classify(b, path, it.get("rails", {}).keys())
    runs = {}; total = {}
    for tr in b.GetTracks():
        if tr.GetClass() != "PCB_TRACK": continue
        net = tr.GetNetname()
        if netclass.class_of(assign, net, "Default") not in targets and not signalnets.is_signal(net, signals): continue
        L = tr.GetLayer(); length = tr.GetLength() / 1e6; n = max(1, int(length / SAMPLE)); total[net] = total.get(net, 0.0) + length
        cur = None
        for k in range(n + 1):
            u = k / n; p = pcbnew.VECTOR2I(int(tr.GetStart().x + u * (tr.GetEnd().x - tr.GetStart().x)), int(tr.GetStart().y + u * (tr.GetEnd().y - tr.GetStart().y)))
            covered = any(pl.Contains(p) for Ln in neighbours(L) for pl in planes.get(Ln, []))
            if not covered:
                if cur is None: cur = [L, p, p, 0.0]
                cur[2] = p; cur[3] += length / (n + 1)
            elif cur is not None: runs.setdefault(net, []).append(cur); cur = None
        if cur is not None: runs.setdefault(net, []).append(cur)
    def what_at(p, layers):
        out = []
        for Ln in layers:
            best = None
            for item in list(b.GetTracks()) + list(b.GetPads()) + list(b.Zones()):
                if not item.IsOnLayer(Ln): continue
                d = math.hypot(item.GetPosition().x - p.x, item.GetPosition().y - p.y) / 1e6 if item.GetClass() != "PCB_TRACK" else _seg_dist(item, p)
                if d <= 1.2 and (best is None or d < best[0]):
                    kind = "rule area" if item.GetClass() == "ZONE" and item.GetIsRuleArea() else item.GetClass().replace("PCB_", "").lower()
                    if item.GetClass() == "ZONE" and not item.GetIsRuleArea(): continue
                    best = (d, "%s %s%s" % (kind, item.GetNetname().lstrip("/") if hasattr(item, "GetNetname") and item.GetNetname() else "", (" of %s" % item.GetParentFootprint().GetReference()) if item.GetClass() == "PAD" else ""))
            out.append("%s: %s" % (b.GetLayerName(Ln), ("%s at %.2f mm" % (best[1], best[0])) if best else "no copper within 1.2 mm (fill edge, slot or keep-out)"))
        return "; ".join(out)
    def _seg_dist(t, p):
        ax, ay, bx, by = t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y; px, py = p.x, p.y
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
        u = 0 if L2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
        return math.hypot(px - (ax + u * dx), py - (ay + u * dy)) / 1e6
    # THE SAME BAR THE GATE USES, PER CLASS (17 September 2026). This file's first line says its totals agree
    # with the gate's, and since 16 September they did not: the gate asks each net the question its spectral
    # class deserves and this report kept the one uniform limit the gate had before that. On board C it named
    # 87 nets of 127 where the gate fails 18, which sends a reader to fix copper the gate does not refuse; and
    # a slow net, whose question is whether a reference EXISTS at all, was being failed for a gap.
    _cls, _ = signal_class.classify(b, path, targets, lambda n: netclass.class_of(assign, n, "Default"))
    over = []
    for net in sorted(total):
        g = sum(r[3] for r in runs.get(net, [])); sc = _cls.get(net, ("UNKNOWN", ""))[0]
        q = signal_class.QUESTION.get(sc, "UNDECIDED")
        if q == "EXISTS":
            lim = total[net] - 1e-9          # only a net with NO reference anywhere is over
        elif sc == "UNKNOWN":
            lim = max(GAP_MM, 0.05 * total[net])      # the strictest bar, as the gate holds an undeclared net
        else:
            lim = signal_class.limit(sc, total[net])
        if g > lim or want_all: over.append((g - lim, net, g, lim, sc))
    over.sort(reverse=True)
    print("return_gaps: %d signal nets judged, %d over their limit (per spectral class, as the gate judges them)"
          % (len(total), sum(1 for o in over if o[0] > 0)))
    for excess, net, g, lim, sc in over:
        rs = sorted(runs.get(net, []), key=lambda r: -r[3])
        print("%s (%s): %.1f of %.1f mm uncovered (limit %.1f, %+.1f), %d run(s)" % (net.lstrip("/"), sc, g, total[net], lim, g - lim, len(rs)))
        for L, p0, p1, ln in rs[:top]:
            mid = pcbnew.VECTOR2I((p0.x + p1.x) // 2, (p0.y + p1.y) // 2)
            print("   %5.1f mm on %-6s (%.1f, %.1f) to (%.1f, %.1f): %s" % (ln, b.GetLayerName(L), p0.x / 1e6, p0.y / 1e6, p1.x / 1e6, p1.y / 1e6, what_at(mid, neighbours(L))))
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
