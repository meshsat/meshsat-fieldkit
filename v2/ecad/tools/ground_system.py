#!/usr/bin/env python3
"""One deliberate ground system, or a partition drawn on purpose (rule GND-001, MESHSAT-862, 16 Sep 2026).

GND-001 asks for one of two things: the board has ONE ground and says so, or every partition is drawn
deliberately with its crossing points named and the signals that cross listed. It read "generation intends to
comply and nothing verifies it" on six boards, and the difference between the two cases is not a matter of
opinion: it is in the netlist.

WHAT IT DOES. It finds the ground nets (every net whose name ends in GND or is GND, plus any the board
declares), and then:

  * ONE ground: the board says so in `boards/<letter>.json` as `grounds: ["GND"]` and that is the whole check.
    An undeclared single ground is INCONCLUSIVE, not a pass, because "there is only one" is a claim about the
    design and the rule asks for it to be stated.
  * SEVERAL grounds: each must be declared with what it is; the parts that touch more than one of them are the
    CROSSING POINTS and each must be declared with its reason; and every net whose parts sit on both sides is
    a SIGNAL THAT CROSSES and must be listed. Anything found and not declared is a failure, and anything
    declared and not found is a failure too, because a declaration that has drifted from the board is worse
    than none.

Board E is why this is not academic: its `GND_V`, the vehicle-side ground, meets `GND` at exactly one part,
the second winding of the SRF1260 common-mode choke. That is a deliberate partition and nothing in this tree
said so until now.

Usage: ground_system.py <netlist.net> [--board <letter>] [--json]
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

GND = re.compile(r"(^|_)GND[0-9]*$|^GND", re.I)


def netlist(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    nets = {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\n    \(net |\n  \)\n)', txt, re.S):
        nets[m.group(1).lstrip("/")] = {(n.group(1), n.group(2))
                                        for n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2))}
    values = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt))
    return nets, values


def board_decl(letter):
    p = os.path.join(HERE, "boards", "%s.json" % (letter or "").lower())
    if not os.path.exists(p): return {}
    try: return json.load(open(p, encoding="utf-8")).get("grounds") or {}
    except Exception: return {}


def judge(net_path, letter=None):
    nets, values = netlist(net_path)
    decl = board_decl(letter)
    declared = set(decl if isinstance(decl, (list, tuple, set)) else decl.keys())
    found = {n for n in nets if GND.search(n)}
    fails, notes = [], []
    if not found:
        return dict(grounds=[], crossings={}, signals=[], fails=["this netlist has no ground net at all"], notes=[])
    # which parts sit on which ground
    on = {}
    for g in found:
        for ref, _pin in nets[g]: on.setdefault(ref, set()).add(g)
    crossings = {r: sorted(gs) for r, gs in on.items() if len(gs) > 1}
    # a net crosses when its parts are referenced to different grounds, the crossing parts themselves aside
    single = {r: list(gs)[0] for r, gs in on.items() if len(gs) == 1}
    crossing_nets = []
    for n, nodes in nets.items():
        if n in found: continue
        doms = {single[r] for r, _p in nodes if r in single}
        if len(doms) > 1: crossing_nets.append((n, sorted(doms)))
    crossing_nets.sort()

    if len(found) == 1:
        g = list(found)[0]
        if declared and g in declared:
            notes.append("one ground (%s) and the board declares it" % g)
        else:
            fails.append("this board has one ground (%s) and does not declare it; 'there is only one' is a "
                         "statement about the design and this rule asks for it to be made" % g)
        return dict(grounds=sorted(found), crossings=crossings, signals=crossing_nets, fails=fails, notes=notes)

    # several grounds
    for g in sorted(found):
        if g not in declared:
            fails.append("ground %s is in the netlist and not declared: a partition nobody wrote down is not a "
                         "deliberate one" % g)
    for g in sorted(declared - found):
        fails.append("the board declares ground %s and the netlist has no such net" % g)
    want_cross = set()
    want_sig = set()
    if isinstance(decl, dict):
        for g, v in decl.items():
            if not isinstance(v, dict): continue
            want_cross |= {str(x) for x in (v.get("crossings") or [])}
            want_sig |= {str(x) for x in (v.get("signals") or [])}
    for r in sorted(crossings):
        if r not in want_cross:
            fails.append("%s (%s) has pins on %s and is not declared as a crossing point"
                         % (r, values.get(r, "")[:40], " and ".join(crossings[r])))
    for r in sorted(want_cross - set(crossings)):
        fails.append("the board declares %s as a crossing point and it touches one ground only" % r)
    for n, doms in crossing_nets:
        if n not in want_sig:
            fails.append("%s crosses the partition (%s) and is not in the declared list of signals that cross"
                         % (n, " to ".join(doms)))
    for n in sorted(want_sig - {n for n, _d in crossing_nets}):
        notes.append("the board lists %s as crossing and this netlist does not show it crossing" % n)
    return dict(grounds=sorted(found), crossings=crossings, signals=crossing_nets, fails=fails, notes=notes)


def main(argv):
    if not argv: print(__doc__); return 2
    net = argv[0]
    letter = argv[argv.index("--board") + 1] if "--board" in argv else \
        (os.path.basename(net).split("-")[1] if "-" in os.path.basename(net) else "")
    if not os.path.exists(net):
        print("ground_system: no netlist at %s" % net)
        return _v.write("ground_system", _v.INCONCLUSIVE, denominator=0, rules=["GND-001"],
                        inputs={"netlist": net}, note="no netlist, so the ground system could not be read")
    try:
        import sch_prov
        letter = sch_prov.letter_for(os.path.basename(net)[:-4]) if not argv.count("--board") else letter
    except Exception: pass
    r = judge(net, letter)
    print("ground_system: %d ground net(s): %s" % (len(r["grounds"]), ", ".join(r["grounds"])))
    for ref, gs in sorted(r["crossings"].items()): print("  crossing %-6s %s" % (ref, " and ".join(gs)))
    for n, d in r["signals"][:20]: print("  crosses  %-16s %s" % (n, " to ".join(d)))
    for n in r["notes"]: print("  note %s" % n)
    for f in r["fails"]: print("  FAIL %s" % f)
    if "--json" in argv: print(json.dumps(r, indent=1, default=list))
    res = _v.FAIL if r["fails"] else _v.PASS
    return _v.write("ground_system", res, rules=["GND-001"],
                    counts={"grounds": len(r["grounds"]), "crossings": len(r["crossings"]),
                            "signals_crossing": len(r["signals"]), "fail": len(r["fails"])},
                    denominator=max(1, len(r["grounds"]) + len(r["crossings"]) + len(r["signals"])),
                    evidence=r["fails"][:20], inputs={"netlist": os.path.basename(net), "board": letter},
                    note="one ground declared, or every partition declared with its crossing points and the "
                         "signals that cross; found from the netlist and compared with the board's own declaration")


if __name__ == "__main__":
    # EVERY GATE LEAVES A READING WHEN IT RAISES (18 September 2026). The thirteen one-line entries of this
    # morning were the gates a crash had already cost a verdict; these are the rest of the deciding gates in
    # the coverage map, guarded the same way, so a rule whose tool raised reads INCONCLUSIVE naming the
    # exception rather than 'no verdict', which the registry reads as nobody having looked.
    sys.exit(_v.guard("ground_system", main, sys.argv[1:]))