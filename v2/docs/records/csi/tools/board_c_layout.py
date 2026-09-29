#!/usr/bin/env python3
"""Board C's layout-bound answers on a placed or routed board file (stream csi, MESHSAT-1357, 29 September 2026; the
independent check's B3 and the re-check's R2-B2, m2 and m4). A DRAFT instrument for the owner of board C's layout
generator, not a gate: it decides no rule.

1. THE ALLOWANCE NETS. For every net a HELD edge_allow entry of board C names (edge_length.load_allow: a refused entry is
   named and never used as a limit):
   * the routed length, summed over every track segment and arc on the net as edge_length.routed_main sums it, its vias
     and its layers, against the entry's max_mm;
   * the PLACEMENT LOWER BOUND: the largest distance between two pads of the net. Any copper that connects the net is at
     least that long, so a placement whose bound is past max_mm cannot meet the allowance however it is routed. It is a
     necessary condition only.
   * the escape via: the distance from U3's pad on the net to the nearest via of the net (a via at a pin spends the
     length budget before the net leaves the pin, and the escape fan occupies the space a close part needs).
2. THE SERIES TERMINATIONS' STUBS. A series resistor answers a net only when it sits at the driver, so the stub between
   U3's pin and its resistor (USB_DP_R, USB_DM_R today; EPD_SCL_R, EPD_SDA_R, EPD_DC_R and EPD_CS_R once the draft of
   apply/apply_board_c_epd_series.py is applied) is held to a limit with a basis: Raspberry Pi's hardware design guide
   (p. 12) asks for this chip's 27 ohm series resistors "placed close to the chip", and its own minimal design runs its
   two pin-to-27R stubs at the lengths readings/minimal-layout-lengths.txt quotes (Net-(U3-USB_DP), Net-(U3-USB_DM)),
   scaled as the allowances are, by the reference layout's delay over board C's slowest (edge_length.worst_delay). The
   stub's routed length and its placement bound (U3's pad to the resistor's pad) are held to that limit.
Usage: board_c_layout.py <board.kicad_pcb>     exit 1 when a net or a stub is past its limit, its placement cannot meet
it, or an entry is refused; 0 otherwise; 2 on usage."""
import fnmatch, hashlib, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "v2", "ecad", "tools"))
from measure_minimal import parse, kid, xy, arc_len

LISTING = "v2/docs/records/csi/readings/minimal-layout-lengths.txt"
STUB_REFS = ("Net-(U3-USB_DP)", "Net-(U3-USB_DM)")
# the stub, the U3 pin that drives it, and the series resistor that ends it (the resistor's references are the
# generator's: R2 and R3 today, R53 to R56 in the draft)
STUBS = (("USB_DP_R", "47", "R2"), ("USB_DM_R", "46", "R3"), ("EPD_SCL_R", "4", "R53"), ("EPD_SDA_R", "5", "R54"),
         ("EPD_DC_R", "6", "R55"), ("EPD_CS_R", "7", "R56"))


def net_of(item, names):
    """The net name of a track, an arc, a via or a pad: KiCad 9 writes (net <code>) or (net <code> "<name>"), KiCad 10
    (net "<name>")."""
    n = kid(item, "net")
    if not n or len(n) < 2: return None
    if len(n) >= 3: return n[2]
    try: return names[int(n[1])]
    except ValueError: return n[1]


def board(text):
    """({net: length}, {net: vias}, {net: layers}, {net: [(ref, pad, x, y)]}, {net: [(x, y) of each via]})."""
    root = parse(text)
    names = {int(e[1]): e[2] for e in root if isinstance(e, list) and e and e[0] == "net" and len(e) >= 3}
    L, V, Ly, pads, vxy = {}, {}, {}, {}, {}
    for it in root:
        if not isinstance(it, list) or not it: continue
        if it[0] in ("segment", "arc"):
            n = net_of(it, names)
            s, e = xy(kid(it, "start")), xy(kid(it, "end"))
            L[n] = L.get(n, 0.0) + (math.dist(s, e) if it[0] == "segment" else arc_len(s, xy(kid(it, "mid")), e))
            Ly.setdefault(n, set()).add(kid(it, "layer")[1])
        elif it[0] == "via":
            n = net_of(it, names); V[n] = V.get(n, 0) + 1
            vxy.setdefault(n, []).append(xy(kid(it, "at")))
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
    return L, V, Ly, pads, vxy


def stub_limit(tpd):
    """(limit_mm, how) for the pin-to-series-resistor stubs, read from the listing (its lines, its sha256/16)."""
    text = open(os.path.join(REPO, LISTING), encoding="utf-8").read()
    lens = {m.group(1): float(m.group(2)) for m in re.finditer(r"(?m)^\s*(\S+)\s+(\d+(?:\.\d+)?) mm\b", text) if m.group(1) in STUB_REFS}
    ref = float(re.search(r"reference t_pd (\d+(?:\.\d+)?) ps/mm", text).group(1))
    assert set(lens) == set(STUB_REFS), lens
    top = max(lens.values())
    lim = math.floor(top * ref / tpd * 10 + 1e-9) / 10
    return lim, "the maker's pin-to-27R stubs %s (%s, sha256/16 %s), the longest %.2f mm, times %.3f / %.3f ps/mm = %.2f, rounded down" % (
        ", ".join("%s %.2f mm" % kv for kv in sorted(lens.items())), LISTING,
        hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], top, ref, tpd, top * ref / tpd)


def far_pair(ps):
    far, pair = 0.0, ("", "")
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            d = math.dist(ps[i][2:], ps[j][2:])
            if d > far: far, pair = d, ("%s.%s" % ps[i][:2], "%s.%s" % ps[j][:2])
    return far, pair


def main(argv):
    if not argv: print(__doc__); return 2
    import edge_length as E
    held, refused = E.load_allow("c")
    tpd = E.worst_delay("c")[0]
    L, V, Ly, pads, vxy = board(open(argv[0], encoding="utf-8").read())
    print("== %s against board C's held edge_allow entries (%d held, %d refused) and the series stubs' limit" % (
        os.path.basename(argv[0]), len(held), len(refused)))
    bad = len(refused)
    for x in refused: print("   REFUSED ENTRY, not used as a limit: %s" % x)
    print("   %-10s %7s %9s %6s %5s  %-17s %9s  %-18s %s" % ("net", "max_mm", "routed", "ratio", "vias", "layers", "pads_far",
                                                              "the farthest pads", "U3 pin to its nearest via"))
    def via_gap(n):
        u3 = [(x, y) for r, p, x, y in pads.get(n, []) if r == "U3"]
        vs = vxy.get(n, [])
        if not (u3 and vs): return "-"
        return "%.2f mm" % min(math.dist(a, b) for a in u3 for b in vs)
    for n in sorted(k for k in set(L) | set(pads) if k):
        nm = n.lstrip("/")
        e = next((e for e in held if fnmatch.fnmatch(nm, e.get("pattern", ""))), None)
        if e is None: continue
        mm = float(e["max_mm"])
        far, pair = far_pair(pads.get(n, []))
        r = L.get(n, 0.0)
        bad += (r > mm or far > mm)
        print("   %-10s %7.2f %7.2f mm %6.1f %5d  %-17s %6.2f mm  %-18s %s%s%s" % (
            nm, mm, r, r / mm, V.get(n, 0), ",".join(sorted(Ly.get(n, ()))) or "-", far, "%s to %s" % pair, via_gap(n),
            "   PAST" if r > mm else "", "   PLACEMENT CANNOT MEET IT" if far > mm else ""))
    lim, how = stub_limit(tpd)
    print("   series stubs, limit %.2f mm: %s; hardware design guide p. 12, \"placed close to the chip\"" % (lim, how))
    for stub, pin, res in STUBS:
        n = next((k for k in set(L) | set(pads) if k and k.lstrip("/") == stub), None)
        if n is None:
            print("   %-10s not on this board (U3 pin %s, %s)" % (stub, pin, res)); continue
        ps = [p for p in pads.get(n, []) if (p[0] == "U3" and p[1] == pin) or p[0] == res]
        far, pair = far_pair(ps)
        r = L.get(n, 0.0)
        bad += (r > lim or far > lim)
        print("   %-10s %7.2f %7.2f mm %6.1f %5d  %-17s %6.2f mm  %-18s %s%s%s" % (
            stub, lim, r, r / lim, V.get(n, 0), ",".join(sorted(Ly.get(n, ()))) or "-", far, "%s to %s" % pair, via_gap(n),
            "   PAST" if r > lim else "", "   PLACEMENT CANNOT MEET IT" if far > lim else ""))
    print("board_c_layout: %d item(s) past their limit, with a placement that cannot meet it, or refused" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
