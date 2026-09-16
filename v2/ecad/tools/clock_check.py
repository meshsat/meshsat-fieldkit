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

THE VALUE, which is the number that matters most, is checked against the crystal's own C_L (16 September
2026). C_L lives in the part's datasheet and no tool can read it out of a netlist, so the BOARD declares it:
`crystals` in `boards/<letter>.json`, one entry per reference with `c_load_pf`, the `stray_pf` this design
allows for its pins and tracks, and the `source` that says where the number came from. The tool then computes
what the fitted capacitors actually present, C1 in series with C2 plus the stray, and compares:

    C_presented = C1 * C2 / (C1 + C2) + C_stray        against        C_L from the datasheet

A crystal on the board with no declaration is INCONCLUSIVE and named, never a pass. The bar is 20 percent, and
it is chosen from what the error DOES rather than from taste: pulling is
Df/f = C_m / 2 * (1/(C_0 + C_L1) - 1/(C_0 + C_L2)), so with the usual C_m = 5 fF and C_0 = 2 pF, a 20 percent
load error on a 10 pF crystal moves it about 30 ppm, which is the whole tolerance of a good part and an eighth
of what USB full speed allows. Anything looser stops being a check; anything tighter starts refusing designs
whose stray allowance is an estimate, which every stray allowance is.

The Raspberry Pi RP2040 hardware design guide works this arithmetic for the exact part on boards C and E and
is the worked example this implements: an ABM8-272-T3 has a 10 pF load capacitance, two 15 pF capacitors give
7.5 pF in series, the pins and tracks add about 3 pF, and the total 10.5 pF is "close enough to the target of
10 pF".

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


_CAP_MULT = {"P": 1.0, "N": 1e3, "U": 1e6}


def cap_pf(value):
    """A capacitor value string in picofarads, or None when it does not name one."""
    m = CAP.match((value or "").strip())
    if not m: return None
    try: return float(m.group(1)) * _CAP_MULT[m.group(2).upper()]
    except Exception: return None


def presented_pf(c1_pf, c2_pf, stray_pf):
    """What the fitted network presents to the crystal: the two capacitors in SERIES, plus the stray."""
    if not c1_pf or not c2_pf: return None
    return (c1_pf * c2_pf) / (c1_pf + c2_pf) + float(stray_pf or 0.0)


def pull_ppm(c_l, presented, c_m_ff=5.0, c_0_pf=2.0):
    """The frequency error a load error makes, at the usual motional numbers. Reported, never used as the bar:
    C_m and C_0 are per part and these two are typical values, not this crystal's."""
    if not c_l or not presented: return None
    return (c_m_ff * 1e-3 / 2.0) * (1.0 / (c_0_pf + presented) - 1.0 / (c_0_pf + c_l)) * 1e6


def judge(path, letter=None):
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
        # THE VALUE AGAINST THE PART'S OWN C_L. The declaration is the board's, because the number is in a
        # datasheet and a netlist cannot hold it.
        d = (_declared(letter) or {}).get(x)
        if d is None:
            rows[-1]["undeclared"] = True
            continue
        c1 = cap_pf(vals[0]) if vals else None
        pres = presented_pf(c1, c1, d.get("stray_pf"))
        rows[-1].update(c_load_pf=d.get("c_load_pf"), stray_pf=d.get("stray_pf"), presented_pf=pres,
                        source=d.get("source"))
        if pres is None or not d.get("c_load_pf"):
            bad.append("%s (%s): its load capacitors read %s, which is not a capacitance this tool can compute with"
                       % (x, values.get(x, "?"), ", ".join(vals) or "none"))
            continue
        cl = float(d["c_load_pf"]); err = (pres - cl) / cl
        rows[-1]["error_percent"] = round(100.0 * err, 1)
        rows[-1]["pull_ppm"] = round(pull_ppm(cl, pres) or 0.0, 1)
        if abs(err) > 0.20:
            bad.append("%s (%s): its network presents %.1f pF (%s in series with itself plus %.1f pF of stray) "
                       "and the part asks for %.1f pF, which is %+.0f percent and pulls it about %+.0f ppm [%s]"
                       % (x, values.get(x, "?"), pres, vals[0], float(d.get("stray_pf") or 0), cl,
                          100.0 * err, rows[-1]["pull_ppm"], str(d.get("source", ""))[:70]))
    return rows, bad


def _declared(letter):
    """The board's own `crystals` table, or None when the board declares none."""
    if not letter: return None
    try:
        import boardtable as _bt
        return _bt.value(letter, "crystals", {}) or {}
    except Exception:
        return None


def main(argv):
    if not argv: print(__doc__); return 2
    path = argv[0]
    if not os.path.exists(path):
        print("clock_check: no netlist at %s" % path)
        return _v.write("clock_check", _v.INCONCLUSIVE, denominator=0, inputs={"netlist": path},
                        note="no netlist: a crystal's load network cannot be read from nothing")
    try:
        import boardtable as _bt
        letter = _bt.letter_for(path) or (os.path.basename(path).split("-")[1][:1] if "-" in os.path.basename(path) else None)
    except Exception:
        letter = None
    rows, bad = judge(path, letter)
    print("clock_check: %d crystal(s)%s" % (len(rows), (" on board %s" % letter.upper()) if letter else ""))
    for r in rows:
        line = ("  %s %s: nets %s, load capacitors %s"
                % (r["crystal"], r["value"], ", ".join(r["nets"]) or "none", ", ".join(r["values"]) or "NONE"))
        if r.get("c_load_pf"):
            line += " -> presents %.1f pF against the part's %.1f (%+.0f percent, about %+.0f ppm)" % (
                r.get("presented_pf") or 0.0, r["c_load_pf"], r.get("error_percent") or 0.0, r.get("pull_ppm") or 0.0)
        print(line)
    for b in bad: print("  FAIL %s" % b)
    undeclared = [r["crystal"] for r in rows if r.get("undeclared")]
    if undeclared:
        print("  no declared C_L: %s (boards/<letter>.json `crystals`: the load capacitance is in the part's "
              "datasheet and a netlist cannot hold it)" % ", ".join(undeclared))
    if "--json" in argv: print(json.dumps(rows, indent=1))
    if not rows:
        # NOT APPLICABLE, which is a different thing from "could not judge" (16 September 2026): board P's
        # route was blocked by this verdict and by the exposed-port one, both of them saying correctly that
        # there is nothing of theirs on that board. The verdict stays INCONCLUSIVE, because absence is never a
        # pass, and it says the rule does not apply here so a pre-route gate can tell the two apart.
        return _v.write("clock_check", _v.INCONCLUSIVE, denominator=0, inputs={"netlist": path},
                        applicable=False,
                        note="this board carries no crystal, so CLK-001 has nothing on it to judge")
    res = _v.FAIL if bad else (_v.INCONCLUSIVE if undeclared else _v.PASS)
    return _v.write("clock_check", res,
                    counts={"crystals": len(rows), "bad": len(bad), "undeclared": len(undeclared)},
                    denominator=len(rows),
                    evidence=(bad + ["no declared C_L: " + u for u in undeclared])[:20], inputs={"netlist": path},
                    note=("every crystal has two matched load capacitors to ground, its own IC alone on its nets, "
                          "and a network that presents what the part's own datasheet asks for within 20 percent"
                          if not bad and not undeclared else
                          "a crystal that does not start, or starts off frequency, is a board that is perfectly "
                          "routed and dead"))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
