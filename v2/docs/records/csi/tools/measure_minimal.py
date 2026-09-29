#!/usr/bin/env python3
"""The routed lengths of the QSPI and crystal nets in Raspberry Pi's own RP2040 reference layout (stream csi,
MESHSAT-1357, 29 September 2026).

Raspberry Pi's hardware design guide says the QSPI pins "should be wired directly to the flash, using short connections
to maintain the signal integrity" and of the crystal "Try and keep the layout as short as possible", with no number.
Its minimal design example is published as a KiCad project (RP-008296-DS, "Minimal-KiCAD", MIT licence). This reads
that project's board file and sums, per net, the length of every track segment and arc on it, and counts its vias: the
lengths at which the maker's own layout runs these nets. Nothing here is estimated; the file is read as KiCad writes
it (an s-expression), segments by their end points, arcs through their three points.

The archive is not in this repository (it is the maker's to publish): it is named by its address and its sha256 and
fetched to a scratch path. Usage:
    measure_minimal.py --fetch <scratch dir>        fetch the archive, check its sha256, measure
    measure_minimal.py <path to the .kicad_pcb>     measure a file already extracted (its sha256 is checked)
"""
import hashlib, math, os, re, sys, zipfile, urllib.request

URL = "https://pip.raspberrypi.com/documents/RP-008296-DS"      # redirects to pip-assets.raspberrypi.com
ZIP_SHA256 = "8fdae5c1d3d8e58f43a45cd604ce9836b1ad4649f11eca4a9bea97eec6c2093a"
PCB_NAME = "RPI-RP2040-MINIMAL_R3-S1_public/RPI-RP2040-MINIMAL_R3-S1.kicad_pcb"
PCB_SHA256 = "f6c8e633a567ca884b269dc7ec934bebbce28534d0fdb84623a007840a01a471"
NETS = ("/QSPI_SCLK", "/QSPI_SS", "/QSPI_SD0", "/QSPI_SD1", "/QSPI_SD2", "/QSPI_SD3", "/XIN", "/XOUT",
        "Net-(C3-Pad1)", "/SWCLK", "/SWD",      # Net-(C3-Pad1): the crystal side of the 1 k XOUT resistor R5
        "Net-(U3-USB_DP)", "Net-(U3-USB_DM)")   # U3 pins 47 and 46 to their 27R series resistors R3 and R4 (the pin-to-resistor stubs)


def tokens(text):
    return re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)


def parse(text):
    """The file as nested lists; strings keep their quotes stripped."""
    stack, cur = [], []
    for t in tokens(text):
        if t == "(":
            stack.append(cur); cur = []
        elif t == ")":
            done = cur; cur = stack.pop(); cur.append(done)
        else:
            cur.append(t[1:-1] if t.startswith('"') else t)
    return cur[0]


def kid(node, key):
    return next((e for e in node if isinstance(e, list) and e and e[0] == key), None)


def xy(node):
    return float(node[1]), float(node[2])


def arc_len(s, m, e):
    """Length of the circular arc through s, m and e."""
    ax, ay = s; bx, by = m; cx, cy = e
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12: return math.dist(s, e)
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    r = math.dist((ux, uy), s)
    chord = math.dist(s, e)
    theta = 2 * math.asin(min(1.0, chord / (2 * r)))
    # the arc through m is the major one when m lies on the far side of the chord from the centre
    cross = lambda p: (e[0] - s[0]) * (p[1] - s[1]) - (e[1] - s[1]) * (p[0] - s[0])
    if cross(m) * cross((ux, uy)) > 0: theta = 2 * math.pi - theta
    return r * theta


def measure(pcb_text):
    root = parse(pcb_text)
    length, vias, layers = {}, {}, {}
    for item in root:
        if not isinstance(item, list) or not item: continue
        net = kid(item, "net")
        name = net[-1] if net else None
        if item[0] == "segment":
            L = math.dist(xy(kid(item, "start")), xy(kid(item, "end")))
        elif item[0] == "arc":
            L = arc_len(xy(kid(item, "start")), xy(kid(item, "mid")), xy(kid(item, "end")))
        elif item[0] == "via":
            vias[name] = vias.get(name, 0) + 1; continue
        else:
            continue
        length[name] = length.get(name, 0.0) + L
        layers.setdefault(name, set()).add(kid(item, "layer")[1])
    return length, vias, layers


C_MM_PER_PS = 0.299792458


def stack(root):
    """(thickness, [(layer, type, epsilon_r)]) from the board's setup stackup, as KiCad writes it."""
    setup = kid(root, "setup")
    st = kid(setup, "stackup") if setup else None
    gen = kid(root, "general")
    thick = float(kid(gen, "thickness")[1]) if gen and kid(gen, "thickness") else None
    rows = []
    for L in (st or [])[1:]:
        if isinstance(L, list) and L and L[0] == "layer":
            ty = kid(L, "type"); er = kid(L, "epsilon_r")
            rows.append((L[1], ty[1] if ty else "", float(er[1]) if er else None))
    return thick, rows


def outer_tpd(er):
    """edge_length.t_pd_ps_per_mm for an outer layer: a microstrip sees (er + 1) / 2 + 0.04."""
    return math.sqrt((er + 1.0) / 2.0 + 0.04) / C_MM_PER_PS


def main(argv):
    if not argv: print(__doc__); return 2
    if argv[0] == "--fetch":
        d = argv[1]; os.makedirs(d, exist_ok=True)
        zp = os.path.join(d, "RP-008296-DS-Minimal-KiCAD.zip")
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(zp, "wb") as f: f.write(r.read())
        got = hashlib.sha256(open(zp, "rb").read()).hexdigest()
        if got != ZIP_SHA256: print("the archive is not the one measured (sha256 %s, expected %s)" % (got, ZIP_SHA256)); return 1
        raw = zipfile.ZipFile(zp).read(PCB_NAME)
    else:
        raw = open(argv[0], "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8")
    if got != PCB_SHA256: print("the board file is not the one measured (sha256 %s, expected %s)" % (got, PCB_SHA256)); return 1
    length, vias, layers = measure(text)
    thick, rows = stack(parse(text))
    print("== Raspberry Pi RP2040 minimal design example, %s (sha256 %s), board file %s (sha256 %s)" % (URL, ZIP_SHA256, PCB_NAME, PCB_SHA256))
    print("   the routed length of each net (every track segment and arc on it, summed), its vias and its layers")
    for n in NETS:
        print("   %-11s %6.2f mm  vias %d  layers %s" % (n.lstrip("/"), length.get(n, 0.0), vias.get(n, 0), ",".join(sorted(layers.get(n, ())))))
    q = [length.get(n, 0.0) for n in NETS if "QSPI" in n]
    print("   QSPI: longest %.2f mm, shortest %.2f mm" % (max(q), min(q)))
    cu = [r[0] for r in rows if r[1] == "copper"]
    i = [r[0] for r in rows].index("F.Cu")
    under = next(r for r in rows[i + 1:] if r[2] is not None)
    used = sorted({x for n in NETS for x in layers.get(n, ())})
    assert used == ["F.Cu"] and not any(vias.get(n) for n in NETS), (used, vias)
    print("   the board: %s mm thick, %d copper layers (%s); every net above is on %s alone, with no via" % (
        thick, len(cu), ", ".join(cu), ", ".join(used)))
    print("   reference t_pd %.3f ps/mm: F.Cu is a microstrip over %s (%s, epsilon_r %s), by the formula edge_length.py "
          "uses for an outer layer, sqrt((er + 1) / 2 + 0.04) / c" % (outer_tpd(under[2]), under[0], under[1], under[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
