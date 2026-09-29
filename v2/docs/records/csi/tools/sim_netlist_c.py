#!/usr/bin/env python3
"""A STAND-IN for board C's regenerated netlist after apply_board_c_epd_series.py (stream csi, 29 September 2026). The
runner has no KiCad, so the drafted circuit change is not regenerated here: this rewrites the committed netlist's text the
way the drafted generator would wire it (R53 to R56, 27R, between U3's pins 4 to 7 and the four e-paper lines), for the
read-back and for SI-001 taken in scratch. It is NOT the regenerated netlist and is never committed as one; the
regeneration on the box is owed and its netlist is what readback_board_c_epd_series.py must be run on.
Usage: sim_netlist_c.py <committed board C netlist> <out path>"""
import re, sys

LINES = (("EPD_SCL", "4", "GPIO2", "R53"), ("EPD_SDA", "5", "GPIO3", "R54"), ("EPD_DC", "6", "GPIO4", "R55"), ("EPD_CS", "7", "GPIO5", "R56"))


def main(src, dst):
    t = open(src, encoding="utf-8").read()
    comps = "".join('    (comp (ref "%s")\n      (value "27R")\n      (footprint "Resistor_SMD:R_0603_1608Metric"))\n' % r
                    for _n, _p, _f, r in LINES)
    assert t.count("  (components\n") == 1
    t = t.replace("  (components\n", "  (components\n" + comps, 1)
    codes = [int(c) for c in re.findall(r'\(net \(code "(\d+)"\)', t)]
    extra = []
    for k, (net, pin, fn, ref) in enumerate(LINES):
        old = '(node (ref "U3") (pin "%s") (pinfunction "%s") (pintype "passive"))' % (pin, fn)
        head = '(net (code "'
        m = re.search(r'\(net \(code "\d+"\) \(name "/%s"\) \(class "Default"\)(.*?)(?=\(net \(code|\Z)' % net, t, re.S)
        assert m and m.group(1).count(old) == 1, net
        block = m.group(0).replace(old, '(node (ref "%s") (pin "2") (pintype "passive"))' % ref)
        t = t[:m.start()] + block + t[m.end():]
        extra.append('\n    (net (code "%d") (name "/%s_R") (class "Default")\n      %s\n      (node (ref "%s") (pin "1") (pintype "passive")))'
                     % (max(codes) + 1 + k, net, old, ref))
    assert t.endswith(")))))\n") or t.endswith(")))))")
    end = t.rstrip("\n")
    t = end[:-2] + "".join(extra) + "))\n"
    open(dst, "w", encoding="utf-8").write(t)


if __name__ == "__main__":
    if len(sys.argv) != 3: print(__doc__); sys.exit(2)
    main(sys.argv[1], sys.argv[2])
