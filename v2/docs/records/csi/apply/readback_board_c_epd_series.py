#!/usr/bin/env python3
"""The netlist read-back of apply_board_c_epd_series.py (stream csi, CSI-D3, 29 September 2026): run it on board C's
regenerated netlist. It parses the netlist (every net to its last, as edge_length.read_netlist reads it) and holds each
e-paper line to what the draft asks, printing one line per check:
  * U3's pin (4 GPIO2, 5 GPIO3, 6 GPIO4, 7 GPIO5) sits on <line>_R, and <line>_R carries nothing but that pin and pin 1 of
    its resistor (the stub between the controller and its termination);
  * the resistor (R53 to R56) is 27R and its pin 2 is on <line>;
  * <line> carries J_EPD's pin (12 CSB, 11 DC, 13 SCL, 14 SDA) and no U3 pin.
Exit 0 when every check holds, 1 when one does not (the committed netlist before the draft is the failing case), 2 on
usage. Usage: readback_board_c_epd_series.py <board C netlist>"""
import os, re, sys

CHECKS = (("EPD_SCL", "4", "R53", "13"), ("EPD_SDA", "5", "R54", "14"), ("EPD_DC", "6", "R55", "11"), ("EPD_CS", "7", "R56", "12"))


def read(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    nets = {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(?: \(class "([^"]*)"\))?(.*?)(?=\(net \(code|\Z)', txt, re.S):
        nets[m.group(1).lstrip("/")] = set(re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(3)))
    values = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt))
    return nets, values


def main(argv):
    if not argv: print(__doc__); return 2
    nets, values = read(argv[0])
    bad = 0
    def say(ok, words):
        nonlocal bad
        bad += 0 if ok else 1
        print("  %s %s" % ("HOLDS" if ok else "FAILS", words))
    for line, pin, ref, jpin in CHECKS:
        stub = nets.get(line + "_R")
        say(stub == {("U3", pin), (ref, "1")}, "%s_R carries U3 pin %s and %s pin 1 only (reads %s)" % (
            line, pin, ref, sorted(stub) if stub is not None else "no such net"))
        say(values.get(ref) == "27R", "%s is 27R (reads %r)" % (ref, values.get(ref)))
        far = nets.get(line, set())
        say((ref, "2") in far and ("J_EPD", jpin) in far, "%s carries %s pin 2 and J_EPD pin %s" % (line, ref, jpin))
        say(not any(r == "U3" for r, _p in far), "%s carries no U3 pin" % line)
    print("readback_board_c_epd_series: %s (%d check(s) failing)" % ("HOLDS" if not bad else "FAILS", bad))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
