#!/usr/bin/env python3
"""The two return-current rules MEASURED on a routed board, as a report (15 September 2026, appendix 32.198): what the
gates would refuse and where. Rule 1 per net and per TRACK LAYER (the mm of track with no filled plane on a neighbouring
layer), rule 2 as the count of signal vias without a ground via within 1.5 mm. No intent file is needed (the rails then
come from the classes and the zone owners alone), no verdict is written: this is the instrument that says, before a
board is re-finished, whether its stack can meet the rule at all (a four-layer board's back-side track references In2,
and where In2 is a routing layer with a partial pour the return is a core away).

Usage: return_report.py <board.kicad_pcb> [--nets=N]   (N worst nets listed, default 12)"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew, signalnets, intent, return_via, netclass

def main(a):
    path = a[0]; nshow = int(next((x.split("=", 1)[1] for x in a[1:] if x.startswith("--nets=")), 12))
    b = pcbnew.LoadBoard(path); it = intent.load(path) or {}
    signals, why = signalnets.classify(b, path, it.get("rails", {}).keys())
    pro = os.path.splitext(path)[0] + ".kicad_pro"; assign = {}
    if os.path.exists(pro): assign = json.load(open(pro)).get("net_settings", {}).get("netclass_assignments", {}) or {}
    cu = list(b.GetEnabledLayers().CuStack())
    planes = {}
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetFilledArea() <= 0: continue
        n = z.GetNetname().lstrip("/")
        if n == "GND" or n.startswith(("+", "VBAT", "CELL", "VBUS", "PACK")):
            planes.setdefault(z.GetFirstLayer(), []).append(z.GetFilledPolysList(z.GetFirstLayer()))
    def nb(L):
        i = cu.index(L); return [cu[j] for j in (i - 1, i + 1) if 0 <= j < len(cu)]
    gaps, total, by_layer = {}, {}, {}
    for tr in b.GetTracks():
        if tr.GetClass() != "PCB_TRACK": continue
        net = tr.GetNetname()
        if not signalnets.is_signal(net, signals): continue
        L = tr.GetLayer(); length = tr.GetLength() / 1e6; n = max(1, int(length / 1.0)); total[net] = total.get(net, 0.0) + length
        ln = b.GetLayerName(L); by_layer.setdefault(ln, [0.0, 0.0]); by_layer[ln][0] += length
        for k in range(n + 1):
            u = k / n; p = pcbnew.VECTOR2I(int(tr.GetStart().x + u * (tr.GetEnd().x - tr.GetStart().x)), int(tr.GetStart().y + u * (tr.GetEnd().y - tr.GetStart().y)))
            if not any(pl.Contains(p) for Ln in nb(L) for pl in planes.get(Ln, [])):
                gaps[net] = gaps.get(net, 0.0) + length / (n + 1); by_layer[ln][1] += length / (n + 1)
    over = []
    for net in total:
        g = gaps.get(net, 0.0); lim = max(10.0, 0.05 * total[net])
        if g > lim: over.append((g, net, total[net], lim))
    over.sort(reverse=True)
    print("return_report: %s, %d copper layers; %d signal nets (%d excluded: %s)" % (os.path.basename(path), b.GetCopperLayerCount(), len(total), len(why), ", ".join("%s %d" % (k, v) for k, v in sorted({r: list(why.values()).count(r) for r in set(why.values())}.items()))))
    print("return_report: planes on %s" % ", ".join("%s (%d)" % (b.GetLayerName(L), len(v)) for L, v in sorted(planes.items())))
    for ln, (t, g) in sorted(by_layer.items()): print("return_report: rule 1 on %-6s %6.0f mm of signal track, %6.0f mm (%3.0f%%) with no plane on a neighbouring layer" % (ln, t, g, 100.0 * g / t if t else 0))
    print("return_report: rule 1: %d of %d signal nets over their limit%s" % (len(over), len(total), "" if not over else "; worst: " + "; ".join("%s %.0f of %.0f mm (limit %.0f)" % (n, g, t, l) for g, n, t, l in over[:nshow])))
    rv = return_via.judge(b, path)
    print("return_report: rule 2: %d of %d signal vias without a ground via within %.1f mm (%d exempt in fine-pitch fans)" % (len(rv["lacking"]), rv["judged"], return_via.RETURN_MM, rv["exempt"]))
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1:]))
