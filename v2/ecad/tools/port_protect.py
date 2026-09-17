#!/usr/bin/env python3
"""Every conductor that leaves the case meets a protection device before it meets a chip (rule TRN-001,
MESHSAT-862, 16 September 2026).

A port that leaves the enclosure is a wire a person will plug something into, in the rain, having walked across
a floor. Every one of them reaches a semiconductor, and the only thing between the two is a transient
suppressor, a common-mode choke, a series resistor into a clamp, or nothing.

WHAT THIS CHECKS. Each board DECLARES its external ports in `boards/<letter>.json` as `external_ports`, a list
of {ref, why} entries: the reference of a connector whose conductors leave the case, and a sentence saying
where it goes. For every signal and power pin of such a connector, the net it lands on must also touch a
protection part: a TVS or ESD device, a gas discharge tube, a common-mode choke, a polyfuse, or a part the
board declares as protection. Ground and a no-connect are skipped, and each is named in the output.

WHY IT IS A DECLARATION AND NOT A GUESS. Half the connectors on these boards are internal: board-to-board
ribbons, mezzanine harnesses, a fan lead inside a sealed case. Treating every J as external would refuse every
board for wires that never leave the enclosure, and treating none as external would check nothing. The board
knows which is which and nothing else does, so the board says, with a reason for each.

A board that declares no external port at all is INCONCLUSIVE, never a pass: no board of this kit is truly
internal, so an empty declaration means nobody has written it yet.

Usage: port_protect.py <netlist.net> [--json]
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v
import boardtable as _bt

# A part whose value or reference says "protection". Read from the value string, because that is where this
# project's generators put what a part IS.
# A part family name is followed by its part number with no word boundary between them, so the families end
# in a digit class rather than \b: board B's +54V rail carries D2 "SMBJ58A" and the first version of this
# regex read straight past it. GALVANIC ISOLATION is protection and the strongest kind: an Ethernet port
# behind its magnetics is not an unprotected port, and the first version called all eight of board B's MDI
# lines unprotected because T1's value says "magnetics" and not "TVS".
PROTECT = re.compile(r"(TVS|ESD|SMBJ|SMCJ|SMAJ|USBLC|PESD|SP\d{4}|GDT|arrest|polyfuse|PTC|common.?mode|"
                     r"choke|magnetic|transformer|isolat|opto|clamp|varistor|\bMOV\b|limiter|D_TVS)", re.I)
# Series parts a conductor may pass through on its way to a clamp. Protection is a CHAIN and not a single net:
# the normal topology on a DC inlet is a fuse, then the transient clamp behind it, and demanding the clamp on
# the connector's own net refused board E's shore inlet for having its fuse in the right place.
# PASSIVE series parts only. A fuse, a bead, a choke or a resistor passes the transient along to whatever
# clamps it, so a clamp behind one of those protects the inlet. A FET or a controller does NOT: it is itself
# the first semiconductor the transient meets, and a clamp on its far side protects everything except it.
# Board E's shore inlet is exactly that shape, so the two cases are reported as different things rather than
# one of them being called "no protection" and hidden.
SERIES = re.compile(r"^(F|FB|L|R|D)\d")
ACTIVE = re.compile(r"^(Q|U|M)\d")
HOPS = 3
SKIP_NETS = ("GND", "GNDA", "AGND", "NC", "")


def netlist(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    by_net, by_ref = {}, {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\n    \(net |\n  \)\n)', txt, re.S):
        name = m.group(1).lstrip("/")
        nodes = set(re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)))
        by_net[name] = nodes
        for r, p in nodes: by_ref.setdefault(r, set()).add((p, name))
    values = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt))
    return by_net, by_ref, values


def judge(net_path, letter=None):
    by_net, by_ref, values = netlist(net_path)
    # A SEARCH MUST NOT WALK OUT THROUGH A POWER RAIL. Every part on a board touches a rail, so a chain that
    # steps onto one reaches the whole board and finds a clamp belonging to something else entirely: board E's
    # sensor pod was reported as protected by a common-mode choke on the shore inlet, which is on the other
    # side of the board and has nothing to do with it. A rail is where the search STOPS: a power pin of an
    # external connector is protected by a clamp on its own rail or by nothing.
    rails = set()
    intent_p = os.path.join(os.path.dirname(net_path),
                            os.path.basename(net_path).replace(".net", "-intent.json"))
    if os.path.exists(intent_p):
        try: rails = {k.lstrip("/") for k in (json.load(open(intent_p)).get("rails") or {})}
        except ValueError: rails = set()
    rails |= {n for n in by_net if n.startswith("+")}
    letter = letter or ""
    ports = _bt.value(letter, "external_ports", []) or []
    rows, bad, missing_refs = [], [], []
    for entry in ports:
        ref = entry.get("ref") if isinstance(entry, dict) else str(entry)
        why = (entry.get("why") if isinstance(entry, dict) else "") or ""
        if ref not in by_ref: missing_refs.append(ref); continue
        unprotected, behind = [], []
        pins_wanted = entry.get("pins") if isinstance(entry, dict) else None
        off = (entry.get("off_board") if isinstance(entry, dict) else None)
        for pin, net in sorted(by_ref[ref]):
            if net.upper() in SKIP_NETS: continue
            if pins_wanted and pin not in [str(x) for x in pins_wanted]: continue
            if off: continue        # protected by a part in the wall, named in the declaration and listed below
            # WHICH active part, not whether one was crossed (16 September 2026). This carried
            # `crossed_active` as a boolean, so the evidence could say "the clamp is behind an active part"
            # and never say WHICH part takes the transient. That is the one fact an owner needs to rule on
            # the topology: the protection path is connector -> ACTIVE PART -> clamp, and naming only the
            # clamp describes two thirds of it. The frontier now carries the first active reference it
            # crossed, and the row names it beside the clamp.
            guards, seen, frontier = [], {net}, [(net, None, True)]
            crossed_active = None
            for _hop in range(HOPS + 1):
                nxt = []
                for n, was_active, is_start in frontier:
                    # A RAIL REACHED BY TRAVERSAL IS NOT PART OF THIS PORT'S CHAIN. The starting net may be a
                    # rail, because a connector has power pins and a clamp on that rail is the right answer for
                    # them; a rail arrived at through two hops is the whole rest of the board.
                    if n in rails and not is_start: continue
                    for r, _p in sorted(by_net.get(n, ())):
                        if PROTECT.search(values.get(r, "") or "") or PROTECT.search(r):
                            guards.append(("%s on %s" % (r, n), values.get(r, "") or "", was_active))
                            if was_active and crossed_active is None: crossed_active = was_active
                            continue
                        act = bool(ACTIVE.match(r))
                        if (SERIES.match(r) or act) and len(by_ref.get(r, ())) >= 2:
                            for _q, n2 in by_ref[r]:
                                if n2 not in seen and n2.upper() not in SKIP_NETS:
                                    # the FIRST active part on this branch is the one that sees the transient
                                    seen.add(n2); nxt.append((n2, was_active or (("%s on %s" % (r, n)) if act else None), False))
                if guards: break
                frontier = nxt
            if not guards: unprotected.append("%s.%s on %s" % (ref, pin, net))
            elif crossed_active:
                _g, _gv, _ = guards[0]
                behind.append("%s.%s on %s: ACTIVE %s (%s) sees the transient; CLAMP %s (%s) is behind it"
                              % (ref, pin, net, crossed_active, values.get(crossed_active.split(" on ")[0], "") or "value not in the netlist",
                                 _g, _gv or "value not in the netlist"))
        rows.append(dict(ref=ref, why=why, pins=len(by_ref[ref]), unprotected=unprotected, behind=behind,
                         off_board=(entry.get("off_board") if isinstance(entry, dict) else None)))
        if behind:
            bad.append("%s (%s): %d conductor(s) whose clamp is behind an active part: %s"
                       % (ref, why[:60], len(behind), "; ".join(behind[:3])))
        if unprotected:
            bad.append("%s (%s): %d conductor(s) reach a chip with nothing between: %s"
                       % (ref, why[:60], len(unprotected), ", ".join(unprotected[:6])))
    return rows, bad, missing_refs, len(ports)


def _write_both(letter, result, **kw):
    """The board's own verdict beside the bare one (17 September 2026).

    TRN-001 is per board and this tool wrote under ONE name, so a board with no reading of its own read
    whatever the last run left in the set-level `out/`: board E5 reads board E's FAIL there today, and the only
    reason it costs nothing is that TRN-001 does not apply to a bare contact block. The same shape cost
    DFM-001 six boards this afternoon. The per-letter name is spelled the way the registry spells it so the
    gate catalogue can read the mapping out of this line."""
    if letter:
        _v.write("port_protect_<letter>".replace("<letter>", str(letter).lower()), result, quiet=True, **kw)
    return _v.write("port_protect", result, **kw)


def main(argv):
    if not argv: print(__doc__); return 2
    path = argv[0]
    letter = _bt.letter_for(path.replace("/out/", "/").replace(".net", ".kicad_pcb"))
    if not letter:
        stem = os.path.basename(path).replace(".net", "")
        letter = _bt.letter_for(stem + ".kicad_pcb")
    rows, bad, missing, n_declared = judge(path, letter)
    print("port_protect: board %s declares %d external port(s); %d found on this netlist"
          % ((letter or "?").upper(), n_declared, len(rows)))
    for r in rows:
        tail = ("protected off board by %s" % r["off_board"]) if r.get("off_board") else \
               ("%d unprotected, %d behind an active part" % (len(r["unprotected"]), len(r.get("behind") or [])))
        print("  %-12s %d pin(s), %s  [%s]" % (r["ref"], r["pins"], tail, r["why"][:64]))
    for b in bad: print("  FAIL %s" % b)
    for m in missing: print("  NOTE declared port %s is not on this netlist" % m)
    if "--json" in argv: print(json.dumps(rows, indent=1))
    if not n_declared:
        # AN EMPTY DECLARATION IS AN ANSWER; A MISSING ONE IS A QUESTION (16 September 2026). Board P carries
        # nothing out of the case: its cell taps, its thermistor lead and its gauge bus all end inside the
        # sealed case a few centimetres away, and it says so in `external_ports: []` with the reason beside it.
        # That is TRN-001 not applying to this board, which is a different thing from nobody having looked, and
        # board P's route was blocked by the two being indistinguishable. A board with no key at all stays an
        # unanswered question and still blocks.
        answered = "external_ports" in (_bt.table(letter) or {})
        why = str((_bt.table(letter) or {}).get("_external_ports_why", "")).strip()
        # A DECLARED ZERO IS AN ANSWER (16 September 2026, evening, the project's own rule applied to this one).
        # It is already how a board with no impedance-targeted pair class passes the pair gate and how a board
        # with nothing pruned passes the pruned gate. Board P declares that no conductor of its own leaves the
        # enclosure, with the reason beside it, and "every exposed port is protected" is then TRUE of it: there
        # are none. Written as INCONCLUSIVE it counted against the set's readiness as an unanswered question,
        # which is the opposite of what the declaration says. A declaration with no reason stays a question,
        # and so does a board with no declaration at all.
        if answered and why:
            return _write_both(letter, _v.PASS, denominator=0, counts={"ports": 0, "unprotected": 0},
                            inputs={"netlist": path, "board": letter},
                            note="this board declares that no conductor of its own leaves the enclosure, so the "
                                 "rule is true of it with nothing to check: %s" % why[:180])
        return _write_both(letter, _v.INCONCLUSIVE, denominator=0, inputs={"netlist": path, "board": letter},
                        note=("this board declares no external port and gives no reason: a zero with nothing "
                              "behind it is a question, not an answer") if answered else
                             ("this board declares no external port, and no board of this kit is truly internal: "
                              "the declaration has not been written yet"))
    # THE COUNTS MUST CARRY WHAT DECIDED. Board A's sweep read FAIL beside "unprotected: 0" on 16 September,
    # because the two conductors that failed are in the other category: their clamp is BEHIND an active part,
    # which therefore takes the transient itself. A verdict whose counts do not contain its own cause is read
    # as a contradiction by everything downstream, including the person reading the sweep.
    n_behind = sum(len(r.get("behind") or []) for r in rows)
    n_unprot = sum(len(r["unprotected"]) for r in rows)
    return _write_both(letter, _v.FAIL if bad else _v.PASS,
                    counts={"ports": len(rows), "declared": n_declared, "unprotected": n_unprot,
                            "behind_an_active_part": n_behind, "not_on_netlist": len(missing)},
                    denominator=sum(r["pins"] for r in rows) or 1, evidence=bad[:20],
                    inputs={"netlist": path, "board": letter},
                    note=("every declared external conductor meets a protection part before a chip" if not bad else
                          "%d conductor(s) reach a semiconductor with nothing between, and %d meet their clamp only "
                          "through an active part, which therefore sees the transient itself" % (n_unprot, n_behind)))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
