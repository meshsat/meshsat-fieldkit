#!/usr/bin/env python3
"""What each copper layer of a board actually carries (MESHSAT-862, P0, 11 September 2026).

The owner reopened every board's layer count on 11 September, and the record's problem is that FOUR LAYERS HAS NO
WRITTEN RATIONALE AT ALL: its first appearance is a statement of state, and the promotions to six were session
decisions recorded inside an owner rulings list. A decision needs the measurement that forced it, and this is the
instrument that takes it: per copper layer, the track length and count, the vias, the zones and their nets, and
the share of the board's routing that sits on an inner layer.

It reads the board file as text, so it runs anywhere (the runner has no pcbnew). It is a REPORT and gates nothing:
what a layer count should be is a reserved class, and the owner rules on it.

Usage: layer_audit.py <board.kicad_pcb> [more boards...] [--json out.json]
"""
import sys, os, re, json, math

# KiCad 9 writes multi-line, tab-indented s-expressions; the one-line regexes that read a KiCad 7 file find
# nothing here and report a board with zero copper, which is why this walks balanced blocks instead.
def _blocks(t, tag):
    """Every top-level `(tag ...)` form of the board, as text, balanced on parentheses (quotes respected)."""
    out, key = [], "\n\t(%s" % tag
    i = t.find(key)
    while i >= 0:
        j = i + 2; depth = 0; q = False
        while j < len(t):
            c = t[j]
            if q: q = c != '"' if c != "\\" else q
            elif c == '"': q = True
            elif c == "(": depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0: break
            j += 1
        out.append(t[i + 2:j + 1]); i = t.find(key, j)
    return out


def _one(b, k, n=1):
    m = re.search(r"\(%s ((?:[-\d.]+\s*){%d})\)" % (k, n), b)
    return [float(x) for x in m.group(1).split()] if m else None


def _str(b, k):
    m = re.search(r'\(%s "([^"]*)"\)' % k, b)
    return m.group(1) if m else None


def _layer_table(t):
    """The board's own copper layer list, in stack order."""
    m = re.search(r"\n\t\(layers\n(.*?)\n\t\)\n", t, re.S)
    if not m: return []
    out = []
    for ln in m.group(1).splitlines():
        g = re.search(r'\(\d+\s+"([^"]+)"\s+(\w+)', ln)
        if g and re.fullmatch(r"(F|B|In\d+)\.Cu", g.group(1)): out.append(g.group(1))
    return out


def audit(path):
    t = open(path, errors="replace").read()
    layers = _layer_table(t)
    per = {L: {"tracks": 0, "mm": 0.0, "widths": set(), "nets": set()} for L in layers}
    for tag in ("segment", "arc"):
        for b in _blocks(t, tag):
            L = _str(b, "layer")
            if L not in per: continue
            a_, e_ = _one(b, "start", 2), _one(b, "end", 2); w = _one(b, "width")
            per[L]["tracks"] += 1
            if a_ and e_: per[L]["mm"] += math.hypot(e_[0] - a_[0], e_[1] - a_[1])
            if w: per[L]["widths"].add(round(w[0], 3))
            m = re.search(r"\(net (\d+)\)", b)
            if m: per[L]["nets"].add(int(m.group(1)))
    vias = []
    for b in _blocks(t, "via"):
        kind = "through"
        for k in ("micro", "blind"):
            if re.search(r"\(%s\b" % k, b[:40]): kind = k
        m = re.search(r'\(layers "([^"]+)" "([^"]+)"\)', b)
        vias.append((kind, _one(b, "size"), _one(b, "drill"), m.group(1) if m else "?", m.group(2) if m else "?"))
    zones = []
    for b in _blocks(t, "zone"):
        net = _str(b, "net_name") or ""
        names = re.findall(r'\(layer "([^"]+)"\)', b[:600]) + [x for g in re.findall(r'\(layers ((?:"[^"]+"\s*)+)\)', b[:600]) for x in re.findall(r'"([^"]+)"', g)]
        fills = len(re.findall(r"\(filled_polygon", b))
        for n in set(names):
            if re.fullmatch(r"(F|B|In\d+)\.Cu", n): zones.append((n, net, fills))
    xs, ys = [], []
    for tag in ("gr_line", "gr_arc", "gr_rect"):
        for b in _blocks(t, tag):
            if _str(b, "layer") != "Edge.Cuts": continue
            for k in ("start", "end", "mid"):
                v = _one(b, k, 2)
                if v: xs.append(v[0]); ys.append(v[1])
    size = (round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1)) if xs else None
    inner = [L for L in layers if L.startswith("In")]
    total_mm = sum(p["mm"] for p in per.values()) or 1.0
    plane_only = [L for L in inner if per[L]["tracks"] == 0 and any(z[0] == L for z in zones)]
    return {
        "board": os.path.basename(path), "size_mm": size, "copper_layers": len(layers), "layers": layers,
        "inner_signal_mm": round(sum(per[L]["mm"] for L in inner), 1),
        "inner_share": round(sum(per[L]["mm"] for L in inner) / total_mm, 3),
        "inner_nets": sorted({n for L in inner for n in per[L]["nets"]}) and len({n for L in inner for n in per[L]["nets"]}),
        "plane_only_inner": plane_only,
        "vias": len(vias), "via_kinds": sorted({v[0] for v in vias}),
        "per_layer": {L: {"tracks": per[L]["tracks"], "mm": round(per[L]["mm"], 1), "nets": len(per[L]["nets"]),
                          "widths": sorted(per[L]["widths"])[:6],
                          "zones": sorted({z[1] or "(no net)" for z in zones if z[0] == L})} for L in layers},
    }


def main(a):
    if not a: print(__doc__); return 2
    out = []
    for p in [x for x in a if not x.startswith("--")]:
        if not os.path.exists(p): print("layer_audit: no board at %s" % p); continue
        r = audit(p); out.append(r)
        print("\n%s  %s  %d copper (%s)" % (r["board"], "%.0f x %.0f mm" % r["size_mm"] if r["size_mm"] else "size?",
                                            r["copper_layers"], ", ".join(r["layers"])))
        for L, d in r["per_layer"].items():
            print("  %-8s %5d tracks  %8.1f mm  widths %-28s zones: %s"
                  % (L, d["tracks"], d["mm"], ",".join("%g" % w for w in d["widths"]) or "-",
                     ", ".join(d["zones"]) or "-"))
        print("  vias %d (%s); inner-layer routing %.1f mm = %.0f%% of all copper; plane-only inner layers: %s"
              % (r["vias"], ", ".join(r["via_kinds"]) or "-", r["inner_signal_mm"], 100 * r["inner_share"],
                 ", ".join(r["plane_only_inner"]) or "none"))
    if "--json" in a: json.dump(out, open(a[a.index("--json") + 1], "w"), indent=1)
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
