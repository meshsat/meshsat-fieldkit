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
            guards, seen, frontier, crossed_active = [], {net}, [(net, False, True)], False
            for _hop in range(HOPS + 1):
                nxt = []
                for n, was_active, is_start in frontier:
                    # A RAIL REACHED BY TRAVERSAL IS NOT PART OF THIS PORT'S CHAIN. The starting net may be a
                    # rail, because a connector has power pins and a clamp on that rail is the right answer for
                    # them; a rail arrived at through two hops is the whole rest of the board.
                    if n in rails and not is_start: continue
                    for r, _p in sorted(by_net.get(n, ())):
                        if PROTECT.search(values.get(r, "") or "") or PROTECT.search(r):
                            guards.append("%s on %s" % (r, n))
                            if was_active: crossed_active = True
                            continue
                        act = bool(ACTIVE.match(r))
                        if (SERIES.match(r) or act) and len(by_ref.get(r, ())) >= 2:
                            for _q, n2 in by_ref[r]:
                                if n2 not in seen and n2.upper() not in SKIP_NETS:
                                    seen.add(n2); nxt.append((n2, was_active or act, False))
                if guards: break
                frontier = nxt
            if not guards: unprotected.append("%s.%s on %s" % (ref, pin, net))
            elif crossed_active:
                behind.append("%s.%s on %s: the clamp (%s) is behind an active part, which therefore sees the transient itself"
                              % (ref, pin, net, guards[0]))
        rows.append(dict(ref=ref, why=why, pins=len(by_ref[ref]), unprotected=unprotected, behind=behind,
                         off_board=(entry.get("off_board") if isinstance(entry, dict) else None)))
        if behind:
            bad.append("%s (%s): %d conductor(s) whose clamp is behind an active part: %s"
                       % (ref, why[:60], len(behind), "; ".join(behind[:3])))
        if unprotected:
            bad.append("%s (%s): %d conductor(s) reach a chip with nothing between: %s"
                       % (ref, why[:60], len(unprotected), ", ".join(unprotected[:6])))
    return rows, bad, missing_refs, len(ports)


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
        return _v.write("port_protect", _v.INCONCLUSIVE, denominator=0, inputs={"netlist": path, "board": letter},
                        note="this board declares no external port, and no board of this kit is truly internal: "
                             "the declaration has not been written yet")
    return _v.write("port_protect", _v.FAIL if bad else _v.PASS,
                    counts={"ports": len(rows), "declared": n_declared, "unprotected": sum(len(r["unprotected"]) for r in rows),
                            "not_on_netlist": len(missing)},
                    denominator=sum(r["pins"] for r in rows) or 1, evidence=bad[:20],
                    inputs={"netlist": path, "board": letter},
                    note=("every declared external conductor meets a protection part before a chip"
                          if not bad else "a conductor leaves the case and reaches a semiconductor with nothing between"))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
