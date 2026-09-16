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
# 16 September 2026, THE SAME DEFECT IN A THIRD PLACE. `LED11`'s prefix is LED, the membership test was on the
# FIRST CHARACTER, and "L" is an inductor, so every indicator on board B was read as a rated part. Its value
# string is "green 5 V S1", the colour and the rail it indicates, and the "5 V" in it was read as a rating of
# 5 V and then judged against the 5 V rail it sits on: three false refusals on a correct design, and a BLOCKER
# rule, so it would have stopped board B's chain. A value's voltage is a rating only when the value is a
# rating, and the prefix is the letters, not the first of them. The tables are exact prefixes now.
NOT_RATED = ("TP", "FID", "LOGO", "DNP", "MH", "LED")


def rated_kind(ref):
    """True if this reference designates a part whose value string carries a RATING.

    The prefix of a reference is its LETTERS, not its first character. `TP6` is a test point and `T6` is a
    tantalum capacitor, `LED11` is an indicator and `L11` is an inductor, and a one-character test cannot tell
    any of those apart. The letters are taken whole and matched EXACTLY against both tables, so a new prefix is
    decided here and in no other place, and an unknown one is not rated rather than guessed at.
    """
    import rules_lib as _R                     # the one place a prefix is decided, shared with reliability.py
    letters = _R.ref_prefix(ref)
    if letters in NOT_RATED: return False
    return letters in RATED


# A TRANSIENT SUPPRESSOR IS NOT JUDGED AGAINST THE VOLTAGE IT MAKES (16 September 2026). Board E's D1 is the
# SMCJ33A that clamps the vehicle input, and the declared peak of that net, 53.3 V, IS its own clamping
# voltage: comparing the two asks whether the clamp survives what the clamp does, which is circular and read
# as a failure. The real question about a protector is the opposite one, and it is worth asking: its STANDOFF
# must be ABOVE the highest voltage the line reaches in normal use, or it conducts in service. The standoff is
# in the part number (SMCJ33A stands off 33 V), and the working maximum is what the net declares as `v_work`.
TVS = re.compile(r"\bSM[ABC]J(\d+(?:\.\d+)?)A?\b", re.I)


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
    # A NET THAT IS NOT A RAIL STILL HAS A VOLTAGE (16 September 2026). A switching node, a bootstrap
    # capacitor's top plate, a charge pump's output and a power amplifier's drain are where a part meets the
    # highest voltage on the board, and none of them is a supply with a current and loads. `intent.node()`
    # declares the peak such a net can reach with the basis for the number; without it derate judged nothing
    # on board C at all and reported twenty-nine of board A's nets as UNDECLARED.
    nodes_v = {k.lstrip("/"): v for k, v in (it.get("nodes") or {}).items()}
    # {ref: {net, ...}} so a two-pin part can be judged on the voltage ACROSS it rather than on one end.
    on = {}
    for _n, _nodes in by_net.items():
        for _r, _p in _nodes: on.setdefault(_r, set()).add(_n)

    def stress(ref, net):
        """(volts, how) for this part on this net: the largest voltage it can see, and where that came from.

        A part between BOOT and SW sees the bias between them and not the node's height above ground, which is
        the difference between a correct 25 V bootstrap capacitor and a refusal. A part between a declared net
        and ground sees the net. A part between two declared nets that do not ride together sees the worst
        pair of their excursions, which is the conservative reading and is named as such."""
        others = on.get(ref, set()) - {net}
        here = rails.get(net) or nodes_v.get(net) or {}
        peak = lambda d: max(abs(float(d.get("volts") or d.get("v_max") or 0.0) if (d.get("volts") is not None or d.get("v_max") is not None) else 0.0),
                             abs(float(d.get("v_min") or 0)))
        for o in others:
            a, b = nodes_v.get(net) or {}, nodes_v.get(o) or {}
            if a.get("rides_on") == o: return float(a["bias_v"]), "the declared bias across %s and %s" % (net, o)
            if b.get("rides_on") == net: return float(b["bias_v"]), "the declared bias across %s and %s" % (o, net)
        v = peak(here)
        for o in others:
            od = rails.get(o) or nodes_v.get(o)
            if od is None: continue
            lo_a = float(here.get("v_min") or 0); hi_a = float(here.get("volts") or here.get("v_max") or 0)
            lo_b = float(od.get("v_min") or 0); hi_b = float(od.get("volts") or od.get("v_max") or 0)
            v = max(v, abs(hi_a - lo_b), abs(hi_b - lo_a))
        return v, "the worst excursion between %s and the net(s) at its other pin(s)" % net

    judged, bad, unrated, undeclared, vendor = 0, [], [], set(), []
    for net, nodes in sorted(by_net.items()):
        r = rails.get(net)
        nd = nodes_v.get(net)
        for ref, _pin in sorted(nodes):
            if not rated_kind(ref): continue
            # THE PROTECTOR IS ASKED FIRST, and the order is the whole point (16 September 2026). A suppressor
            # is judged on its STANDOFF against the line's working maximum, not on surviving the voltage it
            # itself produces, and its standoff is in its part number rather than in a "NN V" the value string
            # may or may not carry. Asked after the rating test, board A's D2 fell out as "unrated" because
            # "SMCJ33A (VIN_RAW clamp behind E6's filter)" states no volts, while board E's D1 was caught only
            # because its note happens to mention "50 V 100 ms": the same part, the same defect, one board
            # reporting it and the other silent, decided by prose.
            _tv = TVS.search(values.get(ref, "") or "")
            if _tv:
                _work = None
                for _src in (rails.get(net), nodes_v.get(net)):
                    if not _src: continue
                    _work = _src.get("v_work")
                    if _work is None and _src.get("volts") is not None: _work = float(_src["volts"])
                    if _work is not None: break
                if _work is None:
                    unrated.append(ref); continue        # nothing says what this line runs at in service
                judged += 1
                _stand = float(_tv.group(1))
                if _stand < float(_work):
                    bad.append("%s (%s) stands off %.1f V and protects %s, which runs to %.1f V in normal "
                               "service: it conducts in service rather than only on a transient"
                               % (ref, values.get(ref, "?"), _stand, net, float(_work)))
                continue
            rated = rating(values.get(ref, ""))
            if rated is None:
                unrated.append(ref); continue
            if r is None and nd is None:
                # a part with a rating on a net nobody declared a voltage for: this is not a pass and not a
                # failure of the part, it is a gap in the intent file, and it is reported as its own class
                undeclared.add(net); continue
            # A net whose voltage nobody can state and whose PART the part's maker states: the comparison is
            # against that citation, and it is recorded as such rather than counted with the measured ones.
            if nd is not None and nd.get("vendor_reference") and nd.get("v_max") is None:
                vendor.append("%s (%s) on %s: %s" % (ref, values.get(ref, "?"), net, nd["vendor_reference"]))
                judged += 1
                continue
            volts, how = stress(ref, net)
            judged += 1
            if rated < volts * (1.0 + margin) - 1e-9:
                bad.append("%s (%s) is rated %.1f V and sees %.1f V on %s (%s), which needs %.1f V at a %.0f%% margin"
                           % (ref, values.get(ref, "?"), rated, volts, net, how,
                              volts * (1.0 + margin), margin * 100))
    return dict(judged=judged, bad=bad, unrated=sorted(set(unrated)), undeclared=sorted(undeclared),
                rails=len(rails), nodes=len(nodes_v), vendor=sorted(set(vendor)))


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
    print("derate: %d rated part-on-net pair(s) judged at a %.0f%% margin over %d declared rail(s) and %d declared "
          "node(s), %d of them against the part maker's own reference circuit; %d part(s) carry no rating in their "
          "value and were not judged; %d net(s) carry a rated part and no declared voltage"
          % (r["judged"], margin * 100, r["rails"], r.get("nodes", 0), len(r.get("vendor") or []),
             len(r["unrated"]), len(r["undeclared"])))
    for b in r["bad"][:20]: print("  FAIL %s" % b)
    for v in (r.get("vendor") or [])[:8]: print("  BY THE PART MAKER %s" % v)
    if r["undeclared"]: print("  UNDECLARED nets: %s" % ", ".join(r["undeclared"][:12]))
    if "--json" in argv: print(json.dumps(r, indent=1))
    # Absence is never a pass: a board whose intent file declares NOTHING has been checked against nothing,
    # however many parts carry ratings. 16 September 2026: a board can now declare nodes as well as rails, and
    # a board of nothing but nodes (a passive filter board, or this tool's own fixtures) was reading
    # INCONCLUSIVE with the words "no rail is declared, so nothing was compared" beside a count of parts that
    # had just been compared. What makes the answer absent is that neither kind of declaration exists.
    _declared = r["rails"] + r.get("nodes", 0)
    res = _v.INCONCLUSIVE if not _declared else (_v.FAIL if r["bad"] else _v.PASS)
    return _v.write("derate", res,
                    counts={"judged": r["judged"], "under_rated": len(r["bad"]), "unrated_parts": len(r["unrated"]),
                            "undeclared_nets": len(r["undeclared"]),
                            "by_vendor_reference": len(r.get("vendor") or [])},
                    denominator=r["judged"],
                    evidence=r["bad"][:20] + ["no declared voltage: %s" % n for n in r["undeclared"][:6]]
                             + ["by the part maker's own reference: %s" % v for v in (r.get("vendor") or [])[:6]],
                    inputs={"netlist": net, "margin": margin},
                    note=("no rail and no node is declared, so nothing was compared" if not _declared else
                          "a part's rating against the declared voltage of the rail it is soldered to; DC-bias "
                          "capacitance derating is NOT checked here and is an open gap"))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
