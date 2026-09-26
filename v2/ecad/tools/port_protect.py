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
# 26 September 2026 (review fix-up of round 4): the suppressor families kisch.tvs() can draw are protection here too
# (SMDJ, SMLJ, P4SMA, P6SMB, P6KE, 1.5KE, 1.5SMC, 3.0SMC, SMF, SM6T, SM15T, 5KP, 15KP), and so is any part the board's
# intent declares a clamp, because a P6KE18A drawn by the helper was a clamp to the polarity pass and a bare
# conductor to this one.
PROTECT = re.compile(r"(TVS|ESD|SMBJ|SMCJ|SMAJ|SMDJ|SMLJ|P4SMA|P6SMB|P6KE|1\.5KE|1\.5SMC|3\.0SMC|SMF\d|SM6T|SM15T|"
                     r"\b1?5KP|USBLC|PESD|SP\d{4}|GDT|arrest|polyfuse|PTC|common.?mode|"
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
# A POWER CONDUCTOR CONTINUES THROUGH A FUSE, A BEAD, A CHOKE OR A DIODE, NEVER THROUGH A PULL-UP (17 September
# 2026). Board E's sensor pod takes 3.3 V from `+3V3_E6`, which carries no clamp; the chain left the rail
# through R25, a pull-up onto the hot-swap controller's power-good net, crossed the controller and reported the
# SHORE INLET's SMCJ40A as the pod's protection. A resistor between a rail and a logic net is not that rail's
# conductor, and the physical question a power pin asks is what clamps THIS rail.
POWER_SERIES = re.compile(r"^(F|FB|L|D)\d")
ACTIVE = re.compile(r"^(Q|U|M)\d")
HOPS = 3
SKIP_NETS = ("GND", "GNDA", "AGND", "NC", "")
# GROUND IS EVERY NET'S NEIGHBOUR AND IS WHERE THE SEARCH STOPS, for the reason a rail is (17 September 2026).
# SKIP_NETS is a list of exact names and board E's isolated vehicle return is `GND_V`, which is not one of them:
# the pod's two I2C conductors walked SDA1 -> U10 -> SHORE_INHIBIT -> Q8 -> GND_V and were reported as protected
# by the shore inlet's own clamp, on the other side of the board with nothing to do with an I2C pair. A name is
# what this project has to go on, so the pattern is the families its generators write.
GROUND = re.compile(r"^(GND|AGND|DGND|PGND|GNDA|VSS|EARTH|CHASSIS)([_\-].*)?$", re.I)


def is_ground(name):
    """Is this net a ground or a return? Ground is skipped as a port conductor and stops a search."""
    return bool(GROUND.match((name or "").strip()))


def netlist(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    by_net, by_ref = {}, {}
    # THE LAST NET OF A KICAD NETLIST WAS NEVER READ (r4t, 26 September 2026). KiCad 9 closes the nets section on
    # the last net's own line, "...)))))", so a look-ahead for "\n  )\n" never matched it and every netlist lost
    # its last net here. Today that is always an unconnected single pin, which is why nothing noticed; a real net
    # sorting last would have vanished. A net now ends where the next one starts, or at the end of the file.
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\(net \(code|\Z)', txt, re.S):
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
    declared_clamps = set()
    if os.path.exists(intent_p):
        try:
            _it = json.load(open(intent_p))
            rails = {k.lstrip("/") for k in (_it.get("rails") or {})}
            declared_clamps = {str(k) for k in (_it.get("clamps") or {})}
        except ValueError: rails = set()
    rails |= {n for n in by_net if n.startswith("+")}
    letter = letter or ""
    ports = _bt.value(letter, "external_ports", []) or []
    rows, bad, missing_refs = [], [], []
    for entry in ports:
        ref = entry.get("ref") if isinstance(entry, dict) else str(entry)
        why = (entry.get("why") if isinstance(entry, dict) else "") or ""
        if ref not in by_ref: missing_refs.append(ref); continue
        unprotected, behind, in_part = [], [], []
        pins_wanted = entry.get("pins") if isinstance(entry, dict) else None
        off = (entry.get("off_board") if isinstance(entry, dict) else None)
        # THE PROTECTION IS SOMETIMES INSIDE THE PART THE CONDUCTOR REACHES (owner decision 31, ruled
        # 21 September 2026). Board A's two CC conductors run to U18 with no clamp between them and TI's own
        # datasheet says, in section 9.1.1, that the device has ESD protection built into the CC1 and CC2 pins
        # so that no external protection is necessary. That is an ANSWER and it is the cheapest kind there is,
        # so the declaration may carry it; and because it is also the easiest way to write a failure away, the
        # tool believes it only when the NETLIST agrees. A declaration is refused, and the conductor judged as
        # if it said nothing, when it carries no citation, or when the part it names is not on that conductor.
        ip = (entry.get("protected_in_part") if isinstance(entry, dict) else None) or {}
        ip_pins = [str(x) for x in (ip.get("pins") or [])]
        ip_part, ip_cite = str(ip.get("part") or "").strip(), str(ip.get("cite") or "").strip()
        for pin, net in sorted(by_ref[ref]):
            if net.upper() in SKIP_NETS or is_ground(net): continue
            if pins_wanted and pin not in [str(x) for x in pins_wanted]: continue
            if off: continue        # protected by a part in the wall, named in the declaration and listed below
            if pin in ip_pins:
                on_this_net = ip_part in {r for r, _p in by_net.get(net, ())}
                if not ip_cite:
                    bad.append("%s.%s on %s: the declaration says the protection is inside %s and gives no "
                               "citation, so it is an assertion and is not read" % (ref, pin, net, ip_part or "?"))
                elif not on_this_net:
                    bad.append("%s.%s on %s: the declaration says the protection is inside %s and %s is not on "
                               "that conductor in this netlist" % (ref, pin, net, ip_part, ip_part))
                else:
                    in_part.append("%s.%s on %s: protection inside %s, cited: %s" % (ref, pin, net, ip_part, ip_cite))
                    continue
            # WHICH active part, not whether one was crossed (16 September 2026). This carried
            # `crossed_active` as a boolean, so the evidence could say "the clamp is behind an active part"
            # and never say WHICH part takes the transient. That is the one fact an owner needs to rule on
            # the topology: the protection path is connector -> ACTIVE PART -> clamp, and naming only the
            # clamp describes two thirds of it. The frontier now carries the first active reference it
            # crossed, and the row names it beside the clamp.
            # (net, the first active part crossed, hops since it, the path, is this the starting net)
            guards, seen, frontier = [], {net}, [(net, None, 0, [net], True, False)]
            crossed_active, crossed_path = None, []
            for _hop in range(HOPS + 1):
                nxt = []
                for n, was_active, since, path, is_start, via_power in frontier:
                    # A RAIL REACHED BY TRAVERSAL IS NOT PART OF THIS PORT'S CHAIN. The starting net may be a
                    # rail, because a connector has power pins and a clamp on that rail is the right answer for
                    # them; a rail arrived at through two hops is the whole rest of the board.
                    # EXCEPT ALONG THE POWER PATH (21 September 2026, found while ruling decision 31). Connector,
                    # fuse, clamp is the textbook entry and board E has it twice. This rule was written to stop a
                    # sensor pod walking out through the whole board, and it also refused to look at the segment
                    # on the other side of a port's OWN fuse: board E's solar input read 'meets its own clamp
                    # before anything else' until 20 September, when PV_P was declared a rail for the power
                    # rules, and then read 'reaches a chip with nothing between' with its SMCJ28A untouched two
                    # millimetres away. A declaration made for one rule had silently changed another rule's
                    # answer. A rail reached through a fuse, a bead, a choke or a series diode FROM THIS PORT'S
                    # own conductor is still this conductor's chain; a rail reached through anything else, a
                    # pull-up above all, is not, and that is what `on_rail` below still refuses to cross.
                    if is_ground(n) and not is_start: continue
                    if n in rails and not is_start and not via_power: continue
                    on_rail = n in rails
                    for r, _p in sorted(by_net.get(n, ())):
                        if PROTECT.search(values.get(r, "") or "") or PROTECT.search(r) or r in declared_clamps:
                            # A CLAMP MORE THAN ONE HOP PAST THE ACTIVE PART IS SOMETHING ELSE'S CLAMP. Once the
                            # chain crosses a semiconductor, that part is what the transient meets; a clamp on
                            # one of ITS OWN nets is the topology owner decision 31 asks about, and anything
                            # further has left this conductor's circuit. Board E's pod read the shore inlet's
                            # SMCJ40A two parts away, which is the finding, not the protection.
                            if was_active and since != 1: continue
                            guards.append(("%s on %s" % (r, n), values.get(r, "") or "", was_active))
                            if was_active and crossed_active is None:
                                crossed_active, crossed_path = was_active, path + ["%s on %s" % (r, n)]
                            continue
                        act = bool(ACTIVE.match(r))
                        # on a rail only the power path continues: a fuse, a bead, a choke or a series diode
                        if on_rail and not POWER_SERIES.match(r): continue
                        if (SERIES.match(r) or act) and len(by_ref.get(r, ())) >= 2:
                            for _q, n2 in by_ref[r]:
                                if n2 not in seen and n2.upper() not in SKIP_NETS and not is_ground(n2):
                                    # the FIRST active part on this branch is the one that sees the transient
                                    seen.add(n2)
                                    nxt.append((n2, was_active or (("%s on %s" % (r, n)) if act else None),
                                                (since + 1) if (was_active or act) else 0,
                                                path + ["%s -> %s" % (r, n2)], False,
                                                bool(POWER_SERIES.match(r))))
                if guards: break
                frontier = nxt
            if not guards: unprotected.append("%s.%s on %s" % (ref, pin, net))
            elif crossed_active:
                _g, _gv, _ = guards[0]
                behind.append("%s.%s on %s: ACTIVE %s (%s) sees the transient; CLAMP %s (%s) is behind it [%s]"
                              % (ref, pin, net, crossed_active, values.get(crossed_active.split(" on ")[0], "") or "value not in the netlist",
                                 _g, _gv or "value not in the netlist", " | ".join(crossed_path)))
        rows.append(dict(ref=ref, why=why, pins=len(by_ref[ref]), unprotected=unprotected, behind=behind,
                         in_part=in_part,
                         off_board=(entry.get("off_board") if isinstance(entry, dict) else None)))
        if behind:
            bad.append("%s (%s): %d conductor(s) whose clamp is behind an active part: %s"
                       % (ref, why[:60], len(behind), "; ".join(behind[:3])))
        if unprotected:
            bad.append("%s (%s): %d conductor(s) reach a chip with nothing between: %s"
                       % (ref, why[:60], len(unprotected), ", ".join(unprotected[:6])))
    return rows, bad, missing_refs, len(ports)


# ---------------------------------------------------------------- clamp polarity (S-09, 26 September 2026)
#
# A ONE-WAY CLAMP THE WRONG WAY ROUND IS A DIODE ACROSS ITS OWN RAIL. Adjudication A03 of MESHSAT-1357 read all
# forty-nine protection parts of the set against their datasheets and their lands: sixteen are unidirectional, all
# sixteen were drawn with KiCad's Device:D_TVS (its own description: "Bidirectional transient-voltage-suppression
# diode", pins A1 and A2), and seven of them had the banded end on the return (board D's D1, board E's D1 to D4 and
# D10, board P's D1). A reversed SMCJ40A on a 36 V bus conducts forward at about 0.8 V: it is a short across the
# rail, found by the fuse. Nothing here could see it, because the only question this gate asked was whether a
# clamp TOUCHED the conductor. So every two-pin clamp on the netlist is now judged, on every board, whether or not
# it sits on a declared external port (board P declares none and carries one of the seven):
#   - a one-way part drawn with an A1/A2 symbol FAILS, because the schematic then hides its polarity from every
#     reader and every tool (kisch.tvs() draws it with Device:D_Zener, K on pin 1);
#   - a two-way part drawn with a K/A symbol FAILS, the other mismatch between the drawing and what is bought;
#   - a one-way clamp FAILS when its cathode is on the return and its anode on the protected conductor. The cathode
#     is the K pin, or on an A1/A2 drawing pad 1, the banded end on KiCad's Diode_SMD lands. The return is a ground
#     family net or a rail the board's intent declares with `returns=` (board P's PACK_N); between two rails the
#     cathode belongs on the higher declared voltage;
#   - a clamp whose two conductors cannot be placed that way is UNJUDGED, named, and makes the verdict
#     INCONCLUSIVE when nothing failed: a polarity nobody could read is not a pass.
#
# THE DRAWING IS NEVER THE SOURCE OF A DIRECTION (review fix-up of round 4, 26 September 2026). The first version
# fell back to the drawing when the part number could not be read: an A1/A2 drawing read as "two-way" and passed as
# N/A, which trusted exactly the drawing S-09 exists to distrust (a reversed SMAJ18A on Device:D_TVS read N/A), and
# a part kisch.tvs(..., direction="uni") draws on Device:D_Zener was not looked at at all unless its number was in
# CLAMP_VALUE (a reversed P6KE18A was absent from the rows). Now:
#   - every part on a Device:D_TVS* or Device:D_Zener* symbol, every D* part whose value names a suppressor family,
#     and every part the board's intent declares as a clamp (kisch.tvs() records each call under "clamps") is judged;
#   - the direction comes from the part number (kisch.tvs_direction, the families whose datasheets are held) or from
#     the generator's declaration, which kisch.tvs() writes with the datasheet basis its caller gave; if the two
#     disagree the row FAILS;
#   - with neither, the row is UNJUDGED whatever the drawing says, except that a K/A drawing with K on the return
#     FAILS as REVERSED: that is wrong for a one-way part and a drawing mismatch for a two-way one.
CLAMP_VALUE = re.compile(r"^(SMAJ|SMBJ|SMCJ|SMDJ|SMLJ|P4SMA|P6SMB|P6KE|1\.5KE|1\.5SMC|3\.0SMC|5\.0SMDJ|SMF\d|SM6T|SM15T|"
                         r"PESD|TVS|ESD\d|5KP|15KP)", re.I)
CLAMP_LIBS = ("Device:D_TVS", "Device:D_Zener")
_NOT_A_DIODE_PREFIX = {"R", "C", "L", "FB", "F", "TP", "J", "P", "SW", "Y", "X", "K", "BT", "H", "MH", "FID"}


class _NotADiode:
    """The references that are never a suppressor, by their exact letter prefix (so CR1, a diode, is not an R)."""
    @staticmethod
    def match(ref):
        m = re.match(r"^([A-Za-z]+)", ref or "")
        return (ref or "").startswith("#") or bool(m and m.group(1).upper() in _NOT_A_DIODE_PREFIX)


_NOT_A_DIODE = _NotADiode()


def components(path):
    """{ref: {"value", "lib", "fp"}} and {(ref, pin): pinfunction} from a KiCad netlist; a fixture that carries
    no libsource or pinfunction reads as "" for them."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    comps = {}
    for ch in re.split(r"\(comp ", txt)[1:]:
        m = re.match(r'\(ref "([^"]+)"\)\s*\(value "((?:[^"\\]|\\.)*)"\)', ch)
        if not m: continue
        head = ch[:4000]
        ls = re.search(r'\(libsource \(lib "([^"]*)"\) \(part "([^"]*)"\)', head)
        fp = re.search(r'\(footprint "([^"]*)"\)', head)
        comps[m.group(1)] = {"value": m.group(2), "lib": ("%s:%s" % ls.groups()) if ls else "",
                             "fp": fp.group(1) if fp else ""}
    funcs = {(r, p): f for r, p, f in
             re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\) \(pinfunction "([^"]*)"\)', txt)}
    return comps, funcs


def _intent_of(net_path):
    p = os.path.join(os.path.dirname(net_path), os.path.basename(net_path).replace(".net", "-intent.json"))
    try: return json.load(open(p))
    except (OSError, ValueError): return {}


def _direction(value):
    """The direction the part number says, through the schematic engine's own reader (kisch.tvs_direction)."""
    try:
        import kisch as _k
        return _k.tvs_direction(value)
    except Exception as e:                      # a reader that cannot be imported reads nothing, and says so
        return None, "the part-number reader could not be loaded (%s)" % type(e).__name__


def clamp_rows(net_path):
    """One row per two-pin clamp on the netlist: its direction, its drawing, where its cathode is, and the verdict
    (OK, REVERSED, SYMBOL, DECLARATION, UNJUDGED, or N/A for a two-way part drawn two-way)."""
    by_net, by_ref, values = netlist(net_path)
    comps, funcs = components(net_path)
    it = _intent_of(net_path)
    rails = {k.lstrip("/"): v for k, v in (it.get("rails") or {}).items()}
    nodes = {k.lstrip("/"): v for k, v in (it.get("nodes") or {}).items()}
    declared = {str(k): v for k, v in (it.get("clamps") or {}).items()}

    def is_return(n):
        return is_ground(n) or bool((rails.get(n) or {}).get("returns"))

    def volts(n):
        if is_ground(n): return 0.0
        if n in rails and rails[n].get("volts") is not None: return float(rails[n]["volts"])
        if n in nodes and nodes[n].get("v_max") is not None: return float(nodes[n]["v_max"])
        return None

    def negative(n):
        """A conductor below its return: a name that starts with '-' or a voltage the intent declares below zero."""
        v = volts(n)
        return str(n).startswith("-") or (v is not None and v < 0)

    def orient(nk, na, via):
        """(verdict, why) for a one-way clamp with its cathode on nk and its anode on na.

        A CONDUCTOR BELOW ITS RETURN TAKES THE CLAMP THE OTHER WAY ROUND (second fix-up of round 4, 26 September
        2026): the cathode belongs on the more positive side, which for a negative rail is the return. No board
        carries one today; the first version would have called the right orientation on one REVERSED."""
        rk, ra, vk, va = is_return(nk), is_return(na), volts(nk), volts(na)
        if ra and not rk:
            if negative(nk):
                return "REVERSED", ("cathode (%s) on %s, a conductor below its return %s, and anode on the return: on "
                                    "a negative conductor a one-way clamp the wrong way round conducts forward" % (via, nk, na))
            return "OK", "cathode (%s) on %s, anode on the return %s" % (via, nk, na)
        if rk and not ra:
            if negative(na):
                return "OK", "cathode (%s) on the return %s, anode on %s, a conductor below its return" % (via, nk, na)
            return "REVERSED", ("cathode (%s) on the return %s and anode on %s: a one-way clamp the wrong way round "
                                "conducts forward across the conductor it protects" % (via, nk, na))
        if not rk and not ra and vk is not None and va is not None:
            return ("OK" if vk >= va else "REVERSED"), "cathode (%s) on %s at %.2f V, anode on %s at %.2f V" % (
                via, nk, vk, na, va)
        return "UNJUDGED", ("cathode (%s) on %s and anode on %s: %s" % (
            via, nk, na, "both are returns" if (rk and ra) else
            "neither is a return and their voltages are not both declared in the intent"))

    out = []
    for ref in sorted(by_ref):
        c = comps.get(ref) or {"value": values.get(ref, ""), "lib": "", "fp": ""}
        val, lib = c["value"], c["lib"]
        pins = sorted(by_ref[ref])
        dec = declared.get(ref)
        # A SUPPRESSOR IS JUDGED WHATEVER ITS REFERENCE (second fix-up of round 4, 26 September 2026): the value
        # family matched only on D* references, so an SMAJ drawn as "Z1" or "TVS1" from another library was not a row.
        # Only the references that are never a diode are left out.
        if not (lib.startswith(CLAMP_LIBS) or (CLAMP_VALUE.match(val or "") and not _NOT_A_DIODE.match(ref)) or dec):
            continue
        if len(pins) != 2:
            if dec:        # a declared clamp that is not a two-pin part on the netlist is a declaration gone wrong
                out.append(dict(ref=ref, value=val, lib=lib or "(no libsource)", drawing="(%d pins)" % len(pins),
                                direction=dec.get("direction"), basis="declared", cathode_net="", anode_net="",
                                orientation="DECLARATION", symbol="OK", verdict="DECLARATION",
                                why="kisch.tvs() declared it a clamp and the netlist has it on %d pin(s)" % len(pins)))
            continue
        f = {p: funcs.get((ref, p), "") for p, _n in pins}
        net = {p: n for p, n in pins}
        drawing = "K/A" if set(f.values()) == {"K", "A"} else "A1/A2" if set(f.values()) == {"A1", "A2"} else ""
        d_mpn, basis = _direction(val)
        d_dec = (dec or {}).get("direction") if (dec or {}).get("direction") in ("uni", "bi") else None
        conflict = ""
        if d_mpn and d_dec and d_mpn != d_dec:
            conflict = ("the generator declares it %s (%s) and its part number says %s (%s)"
                        % (d_dec, (dec or {}).get("basis", "no basis given"), d_mpn, basis))
        if not d_mpn and d_dec:
            basis = "declared %s in the generator by kisch.tvs(): %s" % (d_dec, (dec or {}).get("basis") or "no basis given")
        direction = d_mpn or d_dec
        row = dict(ref=ref, value=val, lib=lib or "(no libsource)", drawing=drawing or "(no pin names)",
                   direction=direction, basis=basis, cathode_net="", anode_net="", verdict="", why="")
        why_sym = ""
        if direction == "uni" and drawing == "A1/A2":
            why_sym = ("a one-way part drawn with %s, whose pins A1/A2 name no cathode, so the schematic hides its "
                       "polarity (%s)" % (lib, basis))
        elif direction == "bi" and drawing == "K/A":
            why_sym = "a two-way part drawn with the one-way symbol %s (%s)" % (lib, basis)
        if direction == "uni":
            kp = [p for p, fn in f.items() if fn == "K"]
            k = kp[0] if drawing == "K/A" and kp else "1"
            a = [p for p in net if p != k][0]
            nk, na = net[k], net[a]
            row.update(cathode_net=nk, anode_net=na)
            verdict, why = orient(nk, na, "its K pin" if drawing == "K/A" else "pad 1, the banded end on KiCad's diode lands")
        elif direction == "bi":
            verdict, why = "N/A", "a two-way part (%s): either way round is correct" % basis
        elif drawing == "K/A":
            kp = [p for p, fn in f.items() if fn == "K"][0]
            nk, na = net[kp], [n for p, n in net.items() if p != kp][0]
            verdict, why = orient(nk, na, "its K pin")
            if verdict == "REVERSED":
                why = ("drawn one-way with " + why + "; its direction is read from neither its part number (%s) nor a "
                       "declaration, and a K/A drawing with K on the return is wrong either way" % basis)
            else:
                row.update(cathode_net=nk, anode_net=na)
                verdict, why = "UNJUDGED", ("its direction is read neither from its part number (%s) nor from a "
                                            "kisch.tvs() declaration; the K/A drawing is not evidence of what is "
                                            "bought (%s)" % (basis, why))
        else:
            verdict, why = "UNJUDGED", ("its direction is read neither from its part number (%s) nor from a "
                                        "kisch.tvs() declaration, and an %s drawing is not evidence of what is bought"
                                        % (basis, drawing or "unnamed-pin"))
        # the declaration must describe this part as it stands on the netlist
        if dec and not conflict and direction == "uni" and row["cathode_net"]:
            dp, dr = str(dec.get("protected", "")).lstrip("/"), str(dec.get("return", "")).lstrip("/")
            if dp and dr and (dp, dr) != (row["cathode_net"], row["anode_net"]):
                conflict = ("kisch.tvs() declared it protecting %s over %s and the netlist has its cathode on %s and "
                            "its anode on %s" % (dp, dr, row["cathode_net"], row["anode_net"]))
        # the orientation and the drawing are two findings; the verdict names the worse, the row keeps both
        row.update(orientation=verdict, symbol=("MISMATCH" if (why_sym or conflict) else "OK"))
        if conflict:
            verdict, why = "DECLARATION", conflict + "; " + why
        elif why_sym and verdict != "REVERSED":
            verdict, why = "SYMBOL", why_sym + "; orientation read from the land: " + why
        elif why_sym:
            why = why + "; and " + why_sym
        row.update(verdict=verdict, why=why)
        out.append(row)
    return out


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
    # A BOARD WITH NO NETLIST STILL HAS AN ANSWER IF IT DECLARES ONE (17 September 2026). Board E5 is generated
    # from board A's board file and has no schematic and no netlist, so every netlist rule read "no verdict for
    # this board" and counted as nobody having looked. It is a bare contact interposer: the question this rule
    # asks is answerable from its own declaration, and a declared zero with its reason is an answer here as it
    # is everywhere else in this registry. The board is named with --board, there being no netlist to name it.
    if path == "--board":
        letter = (argv[1] if len(argv) > 1 else "").lower()
        t = _bt.table(letter) or {}
        why = str(t.get("_external_ports_why") or "").strip()
        items = t.get("external_ports")
        out_dir = os.environ.get("VERDICT_DIR") or "out"
        if items:
            print("port_protect: board %s declares %d item(s) and has no netlist to judge them on" % (letter.upper(), len(items)))
            return _write_both(letter, _v.INCONCLUSIVE, counts={"declared": len(items)}, denominator=0,
                               inputs={"board": letter}, rules=["TRN-001"], out_dir=out_dir,
                               missing_input="this board declares items of this kind and has no netlist to judge them on",
                               note="declared, and not judgeable without a netlist")
        if ("external_ports" in t) and why:
            print("port_protect: board %s declares none, with its reason" % letter.upper())
            return _write_both(letter, _v.PASS, counts={"declared": 0}, denominator=0, evidence=[why],
                               inputs={"board": letter}, rules=["TRN-001"], out_dir=out_dir,
                               note="this board declares that it has none, with its reason, and it has no netlist")
        print("port_protect: board %s declares nothing and has no netlist" % letter.upper())
        return _write_both(letter, _v.INCONCLUSIVE, counts={"declared": 0}, denominator=0,
                           inputs={"board": letter}, rules=["TRN-001"], out_dir=out_dir,
                           missing_input="this board has no netlist and no declaration, so nobody has looked",
                           note="no netlist and no declaration")
    letter = _bt.letter_for(path.replace("/out/", "/").replace(".net", ".kicad_pcb"))
    if not letter:
        stem = os.path.basename(path).replace(".net", "")
        letter = _bt.letter_for(stem + ".kicad_pcb")
    rows, bad, missing, n_declared = judge(path, letter)
    # S-09 (26 September 2026): every clamp's polarity, on every board, before anything returns early.
    clamps = clamp_rows(path)
    c_bad = ["%s %s (%s): %s" % (c["verdict"], c["ref"], c["value"][:40], c["why"]) for c in clamps
             if c["verdict"] in ("REVERSED", "SYMBOL", "DECLARATION")]
    c_unj = ["%s (%s): %s" % (c["ref"], c["value"][:40], c["why"]) for c in clamps if c["verdict"] == "UNJUDGED"]
    c_counts = {"clamps": len(clamps),
                "clamps_one_way": sum(1 for c in clamps if c["cathode_net"]),
                "clamps_reversed": sum(1 for c in clamps if c["orientation"] == "REVERSED"),
                "clamps_symbol_mismatch": sum(1 for c in clamps if c["symbol"] == "MISMATCH"),
                "clamps_unjudged": len(c_unj)}
    print("port_protect: board %s declares %d external port(s); %d found on this netlist"
          % ((letter or "?").upper(), n_declared, len(rows)))
    print("port_protect: %d clamp(s) judged for polarity: %d reversed, %d drawn with a symbol that does not match the "
          "part's direction, %d unjudged" % (len(clamps), c_counts["clamps_reversed"], c_counts["clamps_symbol_mismatch"],
                                             len(c_unj)))
    for c in clamps:
        print("  CLAMP %-6s %-8s %-9s %-6s %s" % (c["ref"], c["verdict"], c["drawing"], c["direction"] or "?", c["why"][:150]))
    for r in rows:
        tail = ("protected off board by %s" % r["off_board"]) if r.get("off_board") else \
               ("%d unprotected, %d behind an active part, %d answered in the part it reaches"
                % (len(r["unprotected"]), len(r.get("behind") or []), len(r.get("in_part") or [])))
        print("  %-12s %d pin(s), %s  [%s]" % (r["ref"], r["pins"], tail, r["why"][:64]))
        for line in (r.get("in_part") or []): print("      ANSWERED %s" % line)
    for b in bad: print("  FAIL %s" % b)
    for m in missing: print("  NOTE declared port %s is not on this netlist" % m)
    if "--json" in argv: print(json.dumps(rows, indent=1))
    if not n_declared and c_bad:
        # A DECLARED ZERO OF PORTS SAYS NOTHING ABOUT A CLAMP THE WRONG WAY ROUND (S-09, 26 September 2026). Board P
        # declares that nothing of its own leaves the case, and its D1 sits across the pack terminals with the band
        # on PACK_N. The ports answer is still what the declared-zero block below would give; the clamps decide.
        for b in c_bad: print("  FAIL %s" % b)
        return _write_both(letter, _v.FAIL, denominator=len(clamps),
                           counts=dict({"ports": 0, "unprotected": 0}, **c_counts), evidence=c_bad[:20],
                           inputs={"netlist": path, "board": letter},
                           note="no external port is declared, and %d clamp(s) on this board are reversed or drawn "
                                "so their polarity cannot be read" % len(c_bad))
    if not n_declared and c_unj and "external_ports" in (_bt.table(letter) or {}) and \
            str((_bt.table(letter) or {}).get("_external_ports_why", "")).strip():
        for u in c_unj: print("  UNJUDGED %s" % u)
        return _write_both(letter, _v.INCONCLUSIVE, denominator=len(clamps),
                           counts=dict({"ports": 0, "unprotected": 0}, **c_counts), evidence=c_unj[:20],
                           inputs={"netlist": path, "board": letter},
                           note="no external port is declared, and %d clamp(s) could not be judged for polarity"
                                % len(c_unj))
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
            return _write_both(letter, _v.PASS, denominator=len(clamps), counts=dict({"ports": 0, "unprotected": 0}, **c_counts),
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
    n_in_part = sum(len(r.get("in_part") or []) for r in rows)
    for b in c_bad: print("  FAIL %s" % b)
    for u in c_unj: print("  UNJUDGED %s" % u)
    n_port_bad = len(bad)
    bad = bad + c_bad            # a reversed or unreadable clamp fails the rule as a bare conductor does (S-09)
    result = _v.FAIL if bad else _v.PASS if not c_unj else _v.INCONCLUSIVE
    return _write_both(letter, _v.FAIL if bad else _v.PASS if not c_unj else _v.INCONCLUSIVE,
                    counts=dict({"ports": len(rows), "declared": n_declared, "unprotected": n_unprot,
                                 "behind_an_active_part": n_behind, "answered_in_part": n_in_part,
                                 "not_on_netlist": len(missing)}, **c_counts),
                    denominator=(sum(r["pins"] for r in rows) or 1) + len(clamps),
                    evidence=(bad[:n_port_bad][:12] + c_bad[:12] + ["UNJUDGED " + u for u in c_unj[:6]])[:20],
                    inputs={"netlist": path, "board": letter},
                    note=("every declared external conductor meets a protection part before a chip, and every clamp "
                          "is drawn and placed the right way round" if result == _v.PASS else
                          ("every declared external conductor meets a protection part before a chip; %d clamp(s) could "
                           "not be judged for polarity" % len(c_unj)) if result == _v.INCONCLUSIVE else
                          "%d conductor(s) reach a semiconductor with nothing between, %d meet their clamp only "
                          "through an active part, which therefore sees the transient itself, and %d clamp(s) are "
                          "reversed or drawn so their polarity cannot be read" % (n_unprot, n_behind, len(c_bad))))


if __name__ == "__main__":
    import verdict as _vg   # a gate that crashes writes INCONCLUSIVE, never nothing (18 September 2026)
    sys.exit(_vg.guard("port_protect", main, sys.argv[1:]))
