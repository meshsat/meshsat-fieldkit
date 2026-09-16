#!/usr/bin/env python3
"""Every crystal has the load network its oscillator needs (rule CLK-001, MESHSAT-862, 16 September 2026).

A crystal with no load capacitors, or with one, does not start. It is the cheapest possible way to have a
board that is perfectly routed, perfectly assembled, and dead: nothing electrical is wrong with it, the part
simply never oscillates, and every other check in this project passes.

WHAT THIS CHECKS, from the netlist and nothing else:
  * every crystal (a two or four pin part whose value names a frequency) has BOTH of its signal pins loaded to
    ground through a capacitor;
  * the two load capacitors are the SAME value, because an unbalanced pair pulls the oscillator off frequency;
  * nothing else shares those two nets except the driving IC and, where the design uses one, a series resistor.
    A crystal node with a third consumer on it is a stub on the most sensitive net of the board.

WHAT IT DOES NOT CHECK, and it is the number that matters most: whether the load capacitor VALUE is the one
this crystal's own datasheet asks for. That is C_L, it is per part, and it lives in a datasheet this tool does
not read. The check reports the value it found so a person can compare it, and the rule stays MUST_JUSTIFY
until each is checked against its own sheet.

Usage: clock_check.py <netlist.net> [--json]
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

# a value that names a frequency: 12MHz, 24 MHz, 32.768kHz, 25M
FREQ = re.compile(r"\b\d+(?:\.\d+)?\s*(?:M|k|G)?Hz\b|\b\d+(?:\.\d+)?\s*M\b", re.I)
CAP = re.compile(r"^(\d+(?:\.\d+)?)\s*([pnu])", re.I)


def netlist(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    by_net = {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\n    \(net |\n  \)\n)', txt, re.S):
        by_net[m.group(1).lstrip("/")] = set(re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)))
    values = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt))
    return by_net, values


def judge(path):
    by_net, values = netlist(path)
    pins_of = {}
    for net, nodes in by_net.items():
        for ref, pin in nodes: pins_of.setdefault(ref, []).append((pin, net))
    crystals = sorted(r for r, v in values.items()
                      if (r.startswith(("X", "Y")) and not r.startswith("XT")) and FREQ.search(v or ""))
    gnd = {n for n in by_net if n.upper() in ("GND", "GNDA", "AGND")}
    rows, bad = [], []
    for x in crystals:
        nets = sorted({n for _p, n in pins_of.get(x, []) if n.upper() not in ("GND", "GNDA", "AGND")})
        loads = []
        for n in nets:
            for ref, _pin in sorted(by_net.get(n, ())):
                if not ref.startswith("C"): continue
                other = {m for m, _q in sum((list(by_net.get(g, ())) for g in gnd), []) if m == ref}
                if other: loads.append((n, ref, values.get(ref, "?")))
        vals = sorted({v for _n, _r, v in loads})
        rows.append(dict(crystal=x, value=values.get(x, "?"), nets=nets, loads=loads, values=vals))
        if len(nets) < 2:
            bad.append("%s (%s) has %d signal net(s): a crystal needs two" % (x, values.get(x, "?"), len(nets)))
            continue
        per_net = {n: [r for nn, r, _v in loads if nn == n] for n in nets}
        missing = [n for n in nets if not per_net[n]]
        if missing:
            bad.append("%s (%s): no load capacitor to ground on %s" % (x, values.get(x, "?"), ", ".join(missing)))
        elif len(vals) > 1:
            bad.append("%s (%s): its two load capacitors differ (%s), which pulls the oscillator off frequency"
                       % (x, values.get(x, "?"), " and ".join(vals)))
        # A SERIES RESISTOR ON A CRYSTAL NODE IS NOT A STUB, it is the damping resistor the oscillator's own
        # datasheet asks for: board D's hub crystal carries "Rd 1.5k per SLLS413 figure 6" in its own value
        # string. The first version of this check called every one of them a defect, on four boards at once,
        # which is the exact shape this project keeps paying for: a guard whose condition is a hypothesis about
        # the data. What is refused is a SECOND driving part on the node, or more than one resistor.
        others = sorted({r for n in nets for r, _p in by_net.get(n, ())
                         if not r.startswith(("C", "TP")) and r != x})
        res = [r for r in others if r.startswith("R")]
        drivers = [r for r in others if not r.startswith("R")]
        if len(drivers) > 1:
            bad.append("%s (%s): %d driving parts share its nets (%s); a crystal node carries its own oscillator and nothing else"
                       % (x, values.get(x, "?"), len(drivers), ", ".join(drivers[:6])))
        if len(res) > 1:
            bad.append("%s (%s): %d resistors on its nets (%s); one series damping resistor is the most a crystal node carries"
                       % (x, values.get(x, "?"), len(res), ", ".join(res[:6])))
        if res: rows[-1]["damping"] = res[0]
    return rows, bad


def main(argv):
    if not argv: print(__doc__); return 2
    path = argv[0]
    if not os.path.exists(path):
        print("clock_check: no netlist at %s" % path)
        return _v.write("clock_check", _v.INCONCLUSIVE, denominator=0, inputs={"netlist": path},
                        note="no netlist: a crystal's load network cannot be read from nothing")
    rows, bad = judge(path)
    print("clock_check: %d crystal(s)" % len(rows))
    for r in rows:
        print("  %s %s: nets %s, load capacitors %s"
              % (r["crystal"], r["value"], ", ".join(r["nets"]) or "none", ", ".join(r["values"]) or "NONE"))
    for b in bad: print("  FAIL %s" % b)
    if rows: print("  the load capacitor VALUE is not judged here: C_L is per part and lives in its own datasheet")
    if "--json" in argv: print(json.dumps(rows, indent=1))
    if not rows:
        return _v.write("clock_check", _v.INCONCLUSIVE, denominator=0, inputs={"netlist": path},
                        note="this board carries no crystal, so nothing was judged")
    return _v.write("clock_check", _v.FAIL if bad else _v.PASS,
                    counts={"crystals": len(rows), "bad": len(bad)}, denominator=len(rows),
                    evidence=bad[:20], inputs={"netlist": path},
                    note=("every crystal has two matched load capacitors to ground and its own IC alone on its nets; "
                          "the VALUE against each part's own C_L is not judged here" if not bad else
                          "a crystal that does not start is a board that is perfectly routed and dead"))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
