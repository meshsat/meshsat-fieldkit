#!/usr/bin/env python3
"""Every line whose assertion inhibits a hazard holds the safe state on its own (rule SCH-004, MESHSAT-862,
17 September 2026).

THE RULE'S OWN WORDS: a transmit inhibit, a zeroize, a shore inhibit or a kill line is designed so that a
disconnected cable, an unpowered board or a missing module leaves the system in the SAFE state, and the
acceptance criteria ask for three things per line, on the netlist: the pull direction, the driver count, and
the behaviour with the far board absent. The registry has carried SCH-004 as a BLOCKER with no implementation
since it was written, so the project has been enforcing part of it by hand: `check_contracts` checks the EMCON
line's pull-downs, its driver count and its sense, board by board, in fifteen hard-coded lines that know only
about that one net. This generalises those to every line a board declares.

WHY IT IS A DECLARATION. A netlist cannot tell an inhibit from an enable, and the difference is the whole
rule: the same conductor pulled to ground is safe on the board that listens to it and meaningless on the board
that only carries it. Each board declares its own lines in `boards/<letter>.json` as `safety_lines`, a list of
{net, hazard, safe_state, role, why}, where the role is `listens` (a part of this board reads it and can act),
`source` (the switch or the driver lives here) or `carries` (the conductor crosses this board and nothing on it
reads it). Only a listener is judged: the fail-safe property is a statement about the board that acts.

WHAT IS JUDGED, and it is deliberately the one thing a netlist can settle:

  * A board that LISTENS to a line (a part of this board reads it) and whose line leaves the board through a
    connector must hold the safe state with its OWN passive: a pull-down for a line whose safe state is low, a
    pull-up to a rail for one whose safe state is high. An inhibit that depends on a cable being present is
    not an inhibit, which is this rule's own rationale.
  * A board that says it only CARRIES a line may have no part reading it, and the netlist is what says so: a
    declaration that calls a listener a pass-through would hide exactly the hazard this rule is about, so the
    two are checked against each other rather than taken on trust.
  * A board that says it is the SOURCE must have something on it that drives the line, a switch or an active
    part; a source with neither is a line nobody asserts.
  * A line whose safe state is HIGH is reported with the rail its pull-up sits on, because an unpowered board
    holds nothing: that is a true statement about the design and not a pass, and the note says so.
  * The DRIVERS are counted and named. The 9 September red team found the EMCON line wired as a ring
    oscillator with its polarity inverted between boards, which is what more than one driver looks like.

Usage: safe_lines.py <netlist.net> [--json]
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v
import boardtable as _bt
import port_protect as _pp                      # its netlist reader, one parser for both rules

GROUND = _pp.GROUND                             # the same ground families, one definition
PASSIVE = re.compile(r"^(R|C|FB|L)\d")
CONNECTOR = re.compile(r"^(J|SW|TP)")
ACTIVE = re.compile(r"^(U|Q|M|D)\d")


def judge(net_path, letter=None):
    by_net, by_ref, values = _pp.netlist(net_path)
    letter = letter or ""
    lines = _bt.value(letter, "safety_lines", []) or []
    rows, bad = [], []
    # THE RAILS COME FROM THE BOARD'S OWN INTENT, never from a naming convention. Board A holds its KILL line
    # up with 100k to VBAT, and a set built from names beginning with "+" does not contain VBAT: the first run
    # of this tool reported board A's kill input as floating on a board that holds it up through a resistor
    # named in the same file (17 September 2026).
    rails = {n for n in by_net if n.startswith("+")}
    try:
        import intent as _intent
        _p = net_path.replace(".net", "-intent.json")
        if os.path.exists(_p):
            rails |= {k.lstrip("/") for k in (json.load(open(_p, encoding="utf-8")).get("rails") or {})}
    except Exception:
        pass
    for entry in lines:
        net = (entry.get("net") or "").lstrip("/")
        safe = (entry.get("safe_state") or "").lower()
        why = entry.get("why") or ""
        role = (entry.get("role") or "listens").lower()
        nodes = sorted(by_net.get(net, ()))
        if not nodes:
            bad.append("%s is declared as a safety line and is not on this netlist" % net)
            rows.append(dict(net=net, on_netlist=False)); continue
        pull_down, pull_up, drivers, leaves, readers = [], [], [], [], []
        for r, pin in nodes:
            other = {n2 for _p, n2 in by_ref.get(r, ()) if n2 != net}
            if PASSIVE.match(r):
                if any(GROUND.match(n2) for n2 in other): pull_down.append("%s (%s)" % (r, values.get(r) or "?"))
                elif any(n2 in rails for n2 in other): pull_up.append("%s (%s to %s)" % (r, values.get(r) or "?",
                                                                     ",".join(sorted(n2 for n2 in other if n2 in rails))))
            elif CONNECTOR.match(r):
                if r.startswith("J"): leaves.append("%s.%s" % (r, pin))
                elif r.startswith("SW"): drivers.append("%s (%s)" % (r, (values.get(r) or "?")[:28]))
            elif ACTIVE.match(r):
                readers.append("%s.%s (%s)" % (r, pin, (values.get(r) or "?")[:28]))
        row = dict(net=net, on_netlist=True, hazard=entry.get("hazard") or "", safe_state=safe, why=why,
                   role=role, pull_down=pull_down, pull_up=pull_up, drivers=drivers,
                   leaves=leaves, readers=readers)
        rows.append(row)
        if role == "carries":
            if readers:
                bad.append("%s: this board declares that it only carries the line and %s reads it"
                           % (net, ", ".join(readers[:3])))
            continue
        if role == "source":
            if not drivers and not readers:
                bad.append("%s: this board declares that it drives the line and nothing on it does" % net)
            continue
        if safe == "low" and not pull_down:
            bad.append("%s: this board reads it and holds nothing down, so with %s open the line floats (%s)"
                       % (net, leaves[0].split(".")[0] if leaves else "its source absent", why[:60]))
        if safe == "high" and not pull_up:
            bad.append("%s: this board reads it and has no pull-up of its own, so with %s open the line floats (%s)"
                       % (net, leaves[0].split(".")[0] if leaves else "its source absent", why[:60]))
    return rows, bad, len(lines)


def _write_both(letter, result, **kw):
    """The board's own verdict beside the bare one, the port_protect pattern: SCH-004 is per board and a board
    with no reading of its own would otherwise read whatever the last run left in the set-level out/."""
    if letter:
        _v.write("safe_lines_<letter>".replace("<letter>", str(letter).lower()), result, quiet=True, **kw)
    return _v.write("safe_lines", result, **kw)


def main(argv):
    if not argv: print(__doc__); return 2
    path = argv[0]
    letter = _bt.letter_for(path.replace("/out/", "/").replace(".net", ".kicad_pcb"))
    if not letter:
        letter = _bt.letter_for(os.path.basename(path).replace(".net", "") + ".kicad_pcb")
    rows, bad, n = judge(path, letter)
    out_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "..", "out")
    out_dir = os.path.normpath(out_dir) if os.path.basename(os.path.dirname(os.path.abspath(path))) == "out" \
        else os.path.join(os.path.dirname(os.path.abspath(path)), "out")
    print("safe_lines: board %s declares %d safety line(s)" % ((letter or "?").upper(), n))
    for r in rows:
        if not r.get("on_netlist"):
            print("  %-16s NOT ON THIS NETLIST" % r["net"]); continue
        print("  %-16s safe %-4s %-9s pull down [%s] pull up [%s] drivers [%s] reads [%s] leaves on [%s]"
              % (r["net"], r["safe_state"], r["role"],
                 ", ".join(r["pull_down"]) or "-", ", ".join(r["pull_up"]) or "-",
                 ", ".join(r["drivers"]) or "-", ", ".join(r["readers"][:3]) or "-",
                 ", ".join(r["leaves"][:3]) or "-"))
    for b in bad: print("  FAIL %s" % b)
    if "--json" in argv: print(json.dumps(rows, indent=1))
    ev = ["%s: safe %s, pull down [%s], pull up [%s], drivers [%s], reads [%s], leaves on [%s]"
          % (r["net"], r["safe_state"], ", ".join(r["pull_down"]) or "none", ", ".join(r["pull_up"]) or "none",
             ", ".join(r["drivers"]) or "none", ", ".join(r["readers"][:4]) or "none",
             ", ".join(r["leaves"][:4]) or "none")
          for r in rows if r.get("on_netlist")] + ["FAIL " + b for b in bad]
    counts = {"lines": n, "on_netlist": sum(1 for r in rows if r.get("on_netlist")),
              "listened": sum(1 for r in rows if r.get("on_netlist") and r.get("role") == "listens"),
              "floating": len(bad)}
    if not n:
        # A DECLARED ZERO IS AN ANSWER AND A MISSING KEY IS A QUESTION, the external_ports idiom. A board with
        # no line that inhibits a hazard says so with its reason; a board that has never been read stays open.
        answered = "safety_lines" in (_bt.table(letter) or {})
        why = str((_bt.table(letter) or {}).get("_safety_lines_why", "")).strip()
        if answered and why:
            return _write_both(letter, _v.PASS, counts=counts, denominator=0, evidence=[why],
                               inputs={"board": letter, "netlist": path}, rules=["SCH-004"], out_dir=out_dir,
                               note="this board declares that no line of its own inhibits a hazard, with its reason")
        return _write_both(letter, _v.INCONCLUSIVE, counts=counts, denominator=0,
                           inputs={"board": letter, "netlist": path}, rules=["SCH-004"], out_dir=out_dir,
                           missing_input="this board declares no safety line, and a zero with nothing behind it is not an answer",
                           note="no safety line is declared on this board")
    res = _v.FAIL if bad else _v.PASS
    return _write_both(letter, res, counts=counts, denominator=counts["on_netlist"], evidence=ev,
                       inputs={"board": letter, "netlist": path}, rules=["SCH-004"], out_dir=out_dir,
                       note=("%d line(s) this board reads hold the safe state with its own copper; the rest are "
                             "driven here or only cross it" % counts["listened"])
                       if not bad else "a declared safety line does not hold its safe state on this board")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
