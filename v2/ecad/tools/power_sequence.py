#!/usr/bin/env python3
"""What turns each rail on, and whether it can turn on at all (rule PWR-002, MESHSAT-862, 16 September 2026).

PWR-002 asks for a written sequencing statement per board: for each rail, what enables it, what it depends on,
the inrush limit and the device requirement it satisfies. It read "no verification" on four boards, and the
note said the sequencing "exists in the design and is written nowhere as a requirement with a check".

Writing it by hand would be sixty-one rails of prose that drifts from the schematic the day after. This DERIVES
it from the netlist the generators write, and checks the one thing in it that is a hard defect rather than a
preference:

  A RAIL WHOSE ENABLE IS DRIVEN ONLY BY A DEVICE POWERED FROM THAT SAME RAIL CANNOT START.

That is a deadlock, it is invisible on a schematic that looks perfectly reasonable, and it is the failure this
rule exists to catch. Its dual, a rail enabled by a device on a rail that comes up later, is a sequencing
ORDER question and is reported as the graph rather than decided, because which order is correct is a property
of the modules and lives in their datasheets.

HOW THE ENABLE IS FOUND, from evidence and never from a guess: the intent file names each rail's SOURCE part;
an enable is a pin of that part whose name or function ends in EN (the generators write the net label as the
pin function). The drivers of that net are its other nodes. A part's own supply is any pin of it that sits on a
declared rail. A rail whose source part has no enable pin at all is ALWAYS ON and is reported as such; a rail
whose enable cannot be resolved is named and makes the verdict INCONCLUSIVE, never a pass.

Usage: power_sequence.py <netlist.net> [--intent <intent.json>] [--json]
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

# An enable net's name ends in EN, with or without an index: SLOT_EN1, SLOT_EN2 and SLOT_EN3 are board A's
# three slot converters and the first version of this pattern matched none of them, because it required EN to be
# the last characters. A rule that reads two of a board's thirteen rails is a rule about its own regular
# expression (16 September 2026).
EN = re.compile(r"(^|_)EN[0-9]*$|(^|_)ENABLE[0-9]*$|_EN_|^EN[0-9]*_", re.I)


def netlist(path):
    """({net: [(ref, pin, function)]}, {ref: value})"""
    txt = open(path, encoding="utf-8", errors="replace").read()
    by_net = {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\n    \(net |\n  \)\n)', txt, re.S):
        name = m.group(1).lstrip("/")
        rows = []
        for n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)(?: \(pinfunction "([^"]*)"\))?', m.group(2)):
            rows.append((n.group(1), n.group(2), n.group(3) or ""))
        by_net[name] = rows
    values = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt))
    return by_net, values


def judge(net_path, intent_path=None):
    by_net, values = netlist(net_path)
    intent_path = intent_path or os.path.join(os.path.dirname(net_path),
                                              os.path.basename(net_path).replace(".net", "-intent.json"))
    it = json.load(open(intent_path)) if os.path.exists(intent_path) else {}
    rails = {k.lstrip("/"): v for k, v in (it.get("rails") or {}).items()}
    # where each reference sits: the declared rails it has a pin on
    on_rail = {}
    for rail, rows in ((r, by_net.get(r) or []) for r in rails):
        for ref, _pin, _fn in rows: on_rail.setdefault(ref, set()).add(rail)

    rows, unresolved, deadlocks, always_on = [], [], [], []
    for rail, r in sorted(rails.items()):
        # THE BOARD'S OWN DECLARATION IS READ FIRST (16 September 2026). The enable-pin search used to run
        # before it, so a rail declared always-on whose source part happens to carry an enable pin for ANOTHER
        # rail was judged as switched by it, and the fixture that proves a good board passes failed for that
        # reason. A declaration is evidence; a pattern match over pin names is a fallback.
        if r.get("always_on"):
            always_on.append(rail)
            rows.append(dict(rail=rail, source=[r.get("source") or "?"], enable=None, drivers=[],
                             note="declared always on: %s" % (r.get("always_on_why") or "no reason given")))
            if not r.get("always_on_why"):
                unresolved.append("%s: declared always on with no reason; a declaration without a reason is an "
                                  "assertion" % rail)
            continue
        src = r.get("source") or r.get("source_ref") or ""
        srcs = src if isinstance(src, list) else [src]
        en_nets = set()
        for s in srcs:
            for net, nodes in by_net.items():
                for ref, pin, fn in nodes:
                    if ref != s: continue
                    if EN.search(fn or "") or EN.search(net or ""): en_nets.add(net)
        if not srcs or not srcs[0]:
            unresolved.append("%s: the intent names no source part, so nothing says what switches it" % rail)
            continue
        if not en_nets:
            # THE INTENT'S SOURCE IS THE RAIL'S ELECTRICAL START, WHICH IS OFTEN A SHUNT OR A FUSE (the dc_drop
            # lesson of 12 September: naming the controller as the source put 2.9 A through a sense pin). Such a
            # part has no enable pin, and reading that as "always on" would be an assumption dressed as a fact.
            # So the second step looks for the SWITCH: a part with a pin on this rail's own net that also has an
            # enable pin of its own. One such part is the answer; none leaves the rail UNRESOLVED and named,
            # because absence is never a pass here either.
            # AND WHERE THE SOURCE PART HAS NO ENABLE PIN, THE BOARD SAYS WHICH PART SWITCHES THE RAIL.
            # Deriving it was tried and withdrawn the same hour (16 September 2026): the rail's net often begins
            # several passives away from its switch (`+5V_S1`'s source is the sense shunt R31, behind it S1_OUT,
            # behind that the inductor L3, and only then U4), and a walk across two-pin passives to find the
            # switch reached 28 candidate parts on board A, because crossing resistors wanders over the whole
            # board. A search that answers "one of twenty-eight" is not an answer. So the intent declares
            # `switch` (the part) or `always_on` (with its reason) per rail, which is what PWR-002 asks for in
            # the first place: a WRITTEN sequencing statement. What the tool does is check the writing against
            # the netlist and find the deadlock.
            cands = {}
            decl = (r.get("switch") or "").strip() if isinstance(r.get("switch"), str) else ""
            if decl:
                found = {}
                want = (r.get("enable_net") or "").lstrip("/")
                for net, nodes in by_net.items():
                    for r2, p2, f2 in nodes:
                        if r2 != decl: continue
                        # an enable net named by the board wins over the name pattern: the BQ4050 turns the pack
                        # terminal on through DSG_G, which no pattern over names would ever find
                        if (want and net.lstrip("/") == want) or EN.search(f2 or "") or EN.search(net or ""):
                            found.setdefault(decl, set()).add(net)
                if not found:
                    unresolved.append("%s: the board declares %s as its switch and that part has no enable pin "
                                      "in the netlist" % (rail, decl))
                    continue
                cands = found
            else:
                unresolved.append("%s: its source %s has no enable pin and the board declares neither a switch "
                                  "nor that the rail is always on" % (rail, ",".join(srcs)))
                continue
            if len(cands) == 1:
                ref = list(cands)[0]; en_nets = cands[ref]; srcs = srcs + [ref]
            elif len(cands) > 1:
                unresolved.append("%s: %d parts on this rail carry an enable pin (%s), so which one switches the "
                                  "rail is not derivable and the board must say"
                                  % (rail, len(cands), ", ".join(sorted(cands))))
                continue
            else:
                unresolved.append("%s: neither its source %s nor any part on the rail carries an enable pin; if "
                                  "it is always on the board should declare that rather than leave it derived"
                                  % (rail, ",".join(srcs)))
                continue
        for en in sorted(en_nets):
            drivers = [(ref, pin, fn) for ref, pin, fn in (by_net.get(en) or []) if ref not in srcs]
            # a driver's own supply: every declared rail it has a pin on
            supplies = {ref: sorted(on_rail.get(ref, set())) for ref, _p, _f in drivers}
            rows.append(dict(rail=rail, source=srcs, enable=en,
                             drivers=[d[0] for d in drivers], supplies=supplies))
            live = [ref for ref, sup in supplies.items() if sup and set(sup) - {rail}]
            if drivers and not live:
                only_self = [ref for ref, sup in supplies.items() if sup == [rail]]
                if only_self:
                    deadlocks.append("%s: its enable %s is driven only by %s, which is powered from %s itself"
                                     % (rail, en, ", ".join(sorted(only_self)), rail))
    return dict(rails=len(rails), rows=rows, unresolved=unresolved, deadlocks=deadlocks,
                always_on=sorted(always_on))


def main(argv):
    if not argv: print(__doc__); return 2
    net = argv[0]
    intent = argv[argv.index("--intent") + 1] if "--intent" in argv else None
    if not os.path.exists(net):
        print("power_sequence: no netlist at %s" % net)
        return _v.write("power_sequence", _v.INCONCLUSIVE, denominator=0, inputs={"netlist": net},
                        rules=["PWR-002"], note="no netlist, so no sequencing could be derived")
    r = judge(net, intent)
    if not r["rails"]:
        print("power_sequence: this board declares no rail, so there is no sequence to derive")
        return _v.write("power_sequence", _v.INCONCLUSIVE, denominator=0, inputs={"netlist": net},
                        rules=["PWR-002"], note="no rail is declared in the intent file")
    print("power_sequence: %d rail(s); %d always on" % (r["rails"], len(r["always_on"])))
    for row in r["rows"]:
        if row.get("enable"):
            print("  %-12s source %-14s enable %-14s driven by %s"
                  % (row["rail"], ",".join(row["source"]), row["enable"],
                     ", ".join("%s on %s" % (d, "+".join(row["supplies"].get(d) or ["?"])) for d in row["drivers"][:4]) or "nothing on this board"))
        else:
            print("  %-12s source %-14s ALWAYS ON" % (row["rail"], ",".join(row["source"])))
    for d in r["deadlocks"]: print("  FAIL %s" % d)
    for u in r["unresolved"]: print("  UNRESOLVED %s" % u)
    if "--json" in argv: print(json.dumps(r, indent=1, default=list))
    res = _v.FAIL if r["deadlocks"] else (_v.INCONCLUSIVE if r["unresolved"] else _v.PASS)
    return _v.write("power_sequence", res,
                    counts={"rails": r["rails"], "always_on": len(r["always_on"]),
                            "deadlocks": len(r["deadlocks"]), "unresolved": len(r["unresolved"])},
                    denominator=r["rails"], evidence=(r["deadlocks"] + r["unresolved"])[:20],
                    inputs={"netlist": os.path.basename(net)}, rules=["PWR-002"],
                    note="each rail's enable derived from the netlist and the part that drives it named; a rail "
                         "whose enable is driven only by a device powered from that same rail cannot start and "
                         "is a failure. The ORDER between rails is reported as the graph and not decided here, "
                         "because which order is correct is a property of the modules' own datasheets")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
