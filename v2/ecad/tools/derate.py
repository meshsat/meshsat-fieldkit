#!/usr/bin/env python3
"""No part sits on a rail that can reach its rated voltage (rule CMP-001, MESHSAT-862, 16 September 2026).

The finding this exists for is board A's, found by hand on 12 September: twenty-five capacitors specified as
`22u 50V X7R 1210` and, on the Power over Ethernet stage, sitting on a FIFTY-FOUR VOLT output. Nothing in this
project looked at a part's rating against the rail it is soldered to, so the only reason it was caught is that
a person happened to read the value string while doing something else.

WHAT THIS CHECKS, and it is deliberately the part that can be checked from data this project HOLDS: every
component whose value string carries a voltage rating, against the declared voltage of every rail its pins
touch, with a margin. The rails and their voltages come from the intent file the schematic generator writes,
so a rail that is not declared is not silently treated as zero volts: it is reported as UNDECLARED and the
verdict is INCONCLUSIVE, never a pass.

WHAT IT DOES NOT CHECK, said out loud rather than implied:
  * a part whose value string carries no voltage (most resistors, every IC). Their absolute maxima live in
    datasheets this tool does not read, and pretending otherwise would be the same mistake in a new place. They
    are COUNTED and reported, so the denominator is honest about what was judged.
  * DC-BIAS CAPACITANCE DERATING. An X7R 0402 at its rated voltage can lose most of its capacitance, which is a
    different failure (a decoupling network that is not there) from a part failing short. It needs each part's
    own bias curve and is recorded as an open gap, not implemented here.
  * transient and ringing peaks. The margin below is against the rail's DECLARED steady voltage; a switch node
    rings above its rail and a hot-swap event overshoots.

THE MARGIN is this project's own number and is a screen, not a law: 20 percent by default, so a part on a 54 V
rail needs a 68 V rating (the next standard value above 64.8), and a 50 V part is refused on anything above
41.7 V. It is declared per board in `boards/<letter>.json` as `derate_margin` where a board has a reason to
differ, and the registry records that no authoritative source backs the number yet.

Usage: derate.py <netlist.net> [--intent <intent.json>] [--margin 0.20] [--json]
"""
import os, re, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

MARGIN = 0.20
# A voltage rating inside a value string: "22u 50V X7R 1210", "100n 100V", "10u 6.3V". The unit is required, so
# a bare number ("2512") is never read as volts.
VOLT = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*V\b", re.I)
# Parts whose value string carries a voltage that is a RATING rather than a set point.
RATED = ("C", "D", "F", "L", "T")
# ... and the references that START with one of those letters and are NOT such a part. The membership test
# is on the FIRST CHARACTER, so "T" for a tantalum capacitor also caught "TP", a test point (16 September
# 2026). A test point's value string is the NET IT TAPS, so board C's `TP6` carried the value "+5V", was
# read as a part rated 5.0 V, was judged against the 5.0 V rail it taps, and failed for wanting a 20 percent
# margin over itself. CMP-001 is a BLOCKER, so that one line stopped board C's whole chain at the pre-route
# gate: "BLOCK a part is rated below the rail it sits on". A test point is a via with a name; it has no
# rating and nothing to derate.
NOT_RATED = ("TP", "FID", "LOGO", "DNP", "MH")


def rated_kind(ref):
    """True if this reference designates a part whose value string carries a RATING.

    The prefix of a reference is its LETTERS, not its first character. `TP6` is a test point and `T6` is a
    tantalum capacitor, and a one-character test cannot tell them apart; the letters are taken whole and
    judged against both tables, so a new prefix is decided here and in no other place.
    """
    letters = ref[:len(ref) - len(ref.lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ_"))].rstrip("_") if ref else ""
    if letters in NOT_RATED: return False
    return letters[:1] in RATED


def netlist(path):
    """({net: {(ref, pin)}}, {ref: value}) from a KiCad netlist."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    by_net = {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\n    \(net |\n  \)\n)', txt, re.S):
        name = m.group(1).lstrip("/")
        by_net[name] = {(n.group(1), n.group(2)) for n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2))}
    values = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt))
    return by_net, values


def rating(value):
    """The voltage a value string claims, or None. The LOWEST number with a V on it wins: a string carrying two
    (a converter's input and output, say) is claiming the part is good to the smaller of them."""
    v = [float(x) for x in VOLT.findall(value or "")]
    return min(v) if v else None


def judge(net_path, intent_path=None, margin=MARGIN):
    by_net, values = netlist(net_path)
    intent_path = intent_path or os.path.join(os.path.dirname(net_path),
                                              os.path.basename(net_path).replace(".net", "-intent.json"))
    it = json.load(open(intent_path)) if os.path.exists(intent_path) else {}
    rails = {k.lstrip("/"): v for k, v in (it.get("rails") or {}).items()}
    judged, bad, unrated, undeclared = 0, [], [], set()
    for net, nodes in sorted(by_net.items()):
        r = rails.get(net)
        for ref, _pin in sorted(nodes):
            if not rated_kind(ref): continue
            rated = rating(values.get(ref, ""))
            if rated is None:
                unrated.append(ref); continue
            if r is None:
                # a part with a rating on a net nobody declared a voltage for: this is not a pass and not a
                # failure of the part, it is a gap in the intent file, and it is reported as its own class
                undeclared.add(net); continue
            volts = float(r.get("volts") or 0)
            judged += 1
            if rated < volts * (1.0 + margin) - 1e-9:
                bad.append("%s (%s) is rated %.1f V and sits on %s at %.1f V, which needs %.1f V at a %.0f%% margin"
                           % (ref, values.get(ref, "?"), rated, net, volts, volts * (1.0 + margin), margin * 100))
    return dict(judged=judged, bad=bad, unrated=sorted(set(unrated)), undeclared=sorted(undeclared),
                rails=len(rails))


def main(argv):
    if not argv: print(__doc__); return 2
    net = argv[0]
    intent = argv[argv.index("--intent") + 1] if "--intent" in argv else None
    margin = float(argv[argv.index("--margin") + 1]) if "--margin" in argv else MARGIN
    if not os.path.exists(net):
        print("derate: no netlist at %s" % net)
        return _v.write("derate", _v.INCONCLUSIVE, denominator=0, inputs={"netlist": net},
                        note="no netlist: the rating of a part cannot be compared with a rail that is not there")
    r = judge(net, intent, margin)
    print("derate: %d rated part-on-rail pair(s) judged at a %.0f%% margin over %d declared rail(s); "
          "%d part(s) carry no rating in their value and were not judged; %d net(s) carry a rated part and no declared voltage"
          % (r["judged"], margin * 100, r["rails"], len(r["unrated"]), len(r["undeclared"])))
    for b in r["bad"][:20]: print("  FAIL %s" % b)
    if r["undeclared"]: print("  UNDECLARED nets: %s" % ", ".join(r["undeclared"][:12]))
    if "--json" in argv: print(json.dumps(r, indent=1))
    # Absence is never a pass: a board whose intent file declares no rail at all has been checked against
    # nothing, however many parts carry ratings.
    res = _v.INCONCLUSIVE if not r["rails"] else (_v.FAIL if r["bad"] else _v.PASS)
    return _v.write("derate", res,
                    counts={"judged": r["judged"], "under_rated": len(r["bad"]), "unrated_parts": len(r["unrated"]),
                            "undeclared_nets": len(r["undeclared"])},
                    denominator=r["judged"],
                    evidence=r["bad"][:20] + ["no declared voltage: %s" % n for n in r["undeclared"][:6]],
                    inputs={"netlist": net, "margin": margin},
                    note=("no rail is declared, so nothing was compared" if not r["rails"] else
                          "a part's rating against the declared voltage of the rail it is soldered to; DC-bias "
                          "capacitance derating is NOT checked here and is an open gap"))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
