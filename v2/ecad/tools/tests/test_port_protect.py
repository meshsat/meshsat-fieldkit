#!/usr/bin/env python3
"""Every conductor that leaves the case meets a protection device before a chip (rule TRN-001, MESHSAT-862,
16 September 2026).

This check produced FOUR distinct false positives before it produced a finding, and each has a rule here. That
is the point of the false-positive discipline: a gate that refuses correct boards is discovered by a board
being wrong for a week, unless someone writes the case down first.
"""
import os, sys, json, tempfile, subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import port_protect


def _net(d, comps, nets):
    os.makedirs(d, exist_ok=True)
    c = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v in sorted(comps.items()))
    n = ""
    for i, (name, nodes) in enumerate(sorted(nets.items()), 1):
        body = "".join('      (node (ref "%s") (pin "%s"))\n' % (r, p) for r, p in nodes)
        n += '    (net (code %d) (name "/%s")\n%s    )\n' % (i, name, body)
    p = os.path.join(d, "pcb-d-aprs.net")     # a stem the board table knows, so the declaration is found
    open(p, "w").write("(export (version E)\n  (components\n%s  )\n  (nets\n%s  )\n)\n" % (c, n))
    return p


def _with_ports(letter, ports, why=None, internal=None):
    """Set a board's declaration for the length of one test. `why` None REMOVES the reason, because since
    16 September an empty list WITH a reason is an answer and an empty list without one is not, and a fixture
    that leaves the board's own reason in place is testing the other case. `internal` None REMOVES the board's
    own internal_ports for the same reason (28 September 2026): the fixture's connectors are not the board's."""
    p = os.path.join(TOOLS, "boards", "%s.json" % letter)
    original = open(p, encoding="utf-8").read()
    d = json.loads(original); d["external_ports"] = ports
    if why is None: d.pop("_external_ports_why", None)
    else: d["_external_ports_why"] = why
    if internal is None: d.pop("internal_ports", None)
    else: d["internal_ports"] = internal
    json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return lambda: open(p, "w", encoding="utf-8").write(original)


REVIEWS = os.path.join(TOOLS, "pcb_port_reviews.json")
REVIEW_DOC = "v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md"
KEEP = object()


def _reviewed_as_declared(letter, net_path):
    """The reviewed record a fixture gets when it says nothing: exactly the pins it declares external, read from its
    own netlist (28 September 2026, S-88 item B1). A fixture that tests the reviewed set passes its own record."""
    t = json.loads(open(os.path.join(TOOLS, "boards", "%s.json" % letter), encoding="utf-8").read())
    _bn, by_ref, _v = port_protect.netlist(net_path)
    ext = {}
    for e in t.get("external_ports") or []:
        ref = e.get("ref") if isinstance(e, dict) else str(e)
        want = [str(x) for x in ((e.get("pins") if isinstance(e, dict) else None) or [])]
        for pin, net in sorted(by_ref.get(ref, ())):
            if port_protect.carries_conductor(net) and (not want or pin in want): ext.setdefault(ref, {})[pin] = net
    return {"review": REVIEW_DOC, "reviewed_on": "2026-09-28",
            "why": "a fixture of the tests: the set is what the fixture declares external, read from its own netlist",
            "external": ext, "changes": []}


def _with_reviewed(letter, record):
    """Set a board's reviewed record for the length of one run; None REMOVES it (a board nobody has reviewed)."""
    original = open(REVIEWS, encoding="utf-8").read()
    d = json.loads(original)
    if record is None: d["boards"].pop(letter, None)
    else: d["boards"][letter] = record
    open(REVIEWS, "w", encoding="utf-8").write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    return lambda: open(REVIEWS, "w", encoding="utf-8").write(original)


def _run(p, cwd, reviewed="as declared"):
    """Run the tool on netlist `p`. `reviewed` is the board's reviewed record for this run: "as declared" (the
    default, so a fixture about something else is not about the reviewed set), a record, None (no record), or KEEP
    (the tree's own file untouched)."""
    stem = os.path.basename(p).replace(".net", "")
    letter = port_protect._bt.letter_for(stem + ".kicad_pcb") or "d"
    restore = None
    if reviewed is not KEEP:
        restore = _with_reviewed(letter, _reviewed_as_declared(letter, p) if reviewed == "as declared" else reviewed)
    try:
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "port_protect.py"), p], cwd=cwd,
                           capture_output=True, text=True, timeout=120)
    finally:
        if restore: restore()
    return r.returncode, r.stdout + r.stderr


def t_a_bare_conductor_leaving_the_case_is_refused():
    restore = _with_ports("d", [{"ref": "J_X", "why": "a jack on the face that a person plugs a lead into"}])
    try:
        d = tempfile.mkdtemp(prefix="port-bare-")
        p = _net(d, {"J_X": "face jack", "U1": "amplifier"},
                 {"SIG": [("J_X", "1"), ("U1", "3")], "GND": [("J_X", "2")]})
        rc, out = _run(p, d)
        assert rc == 1, "a bare conductor passed:\n%s" % out[-400:]
        assert "nothing between" in out, out[-400:]
    finally:
        restore()


def t_a_part_number_after_a_family_name_is_still_a_clamp():
    """"SMBJ58A" is an SMBJ. The first regex required a word boundary after the family, which a part number
    does not provide, and board B's 54 V feed was called unprotected with its TVS sitting on it."""
    restore = _with_ports("d", [{"ref": "J_X", "why": "the power feed leaving the case"}])
    try:
        d = tempfile.mkdtemp(prefix="port-family-")
        p = _net(d, {"J_X": "feed", "D9": "SMBJ58A", "U1": "load"},
                 {"HV": [("J_X", "1"), ("D9", "1"), ("U1", "3")], "GND": [("J_X", "2"), ("D9", "2")]})
        rc, out = _run(p, d)
        assert rc == 0, "a TVS with a part number was not recognised:\n%s" % out[-400:]
    finally:
        restore()


def t_galvanic_isolation_is_protection():
    """Eight Ethernet lines behind their magnetics were called unprotected because the part's value says
    "magnetics" and not "TVS". Isolation is the strongest protection there is."""
    restore = _with_ports("d", [{"ref": "J_X", "why": "the wall Ethernet jack"}])
    try:
        d = tempfile.mkdtemp(prefix="port-mag-")
        p = _net(d, {"J_X": "RJ45", "T9": "Pulse H5007NL 1000BASE-T magnetics", "U1": "switch"},
                 {"MDI": [("J_X", "1"), ("T9", "23")], "SW": [("T9", "2"), ("U1", "5")], "GND": [("J_X", "2")]})
        rc, out = _run(p, d)
        assert rc == 0, "a port behind its magnetics was called unprotected:\n%s" % out[-400:]
    finally:
        restore()


def t_protection_is_a_chain_through_a_fuse():
    """A DC inlet's clamp normally sits behind the fuse. Demanding it on the connector's own net refused an
    inlet for having its fuse in the right place."""
    restore = _with_ports("d", [{"ref": "J_X", "why": "the shore DC inlet"}])
    try:
        d = tempfile.mkdtemp(prefix="port-chain-")
        p = _net(d, {"J_X": "inlet", "F9": "10 A blade", "D9": "SMCJ33A", "U1": "load"},
                 {"IN": [("J_X", "1"), ("F9", "1")], "FUSED": [("F9", "2"), ("D9", "1"), ("U1", "3")],
                  "GND": [("J_X", "2"), ("D9", "2")]})
        rc, out = _run(p, d)
        assert rc == 0, "a clamp behind the fuse was not found:\n%s" % out[-400:]
    finally:
        restore()


def t_a_clamp_behind_an_active_part_is_a_different_finding_from_none():
    """A clamp reached only through a FET protects everything except that FET. Board E's shore inlet is exactly
    that shape and it is reported as its own case, not as "no protection" and not as a pass."""
    restore = _with_ports("d", [{"ref": "J_X", "why": "the shore DC inlet"}])
    try:
        d = tempfile.mkdtemp(prefix="port-behind-")
        p = _net(d, {"J_X": "inlet", "F9": "10 A blade", "Q9": "pass FET", "D9": "SMCJ33A", "U1": "load"},
                 {"IN": [("J_X", "1"), ("F9", "1")], "FUSED": [("F9", "2"), ("Q9", "1")],
                  "OUT": [("Q9", "2"), ("D9", "1"), ("U1", "3")], "GND": [("J_X", "2"), ("D9", "2")]})
        rc, out = _run(p, d)
        assert rc == 1, "a clamp behind the pass FET was treated as protection:\n%s" % out[-500:]
        assert "behind an active part" in out, out[-500:]
    finally:
        restore()


def t_the_search_does_not_walk_out_through_a_power_rail():
    """Every part on a board touches a rail, so a search that steps onto one reaches the whole board: a sensor
    pod was reported as protected by a choke on the other side of it."""
    restore = _with_ports("d", [{"ref": "J_X", "why": "a sensor pod outside the case"}])
    try:
        d = tempfile.mkdtemp(prefix="port-rail-")
        p = _net(d, {"J_X": "pod", "U1": "sensor", "R9": "10k", "D9": "SMCJ33A", "U2": "something else"},
                 {"SDA": [("J_X", "3"), ("R9", "1"), ("U1", "5")],
                  "+3V3": [("R9", "2"), ("U1", "8"), ("U2", "1"), ("D9", "1")],
                  "GND": [("J_X", "4"), ("D9", "2")]})
        rc, out = _run(p, d)
        assert rc == 1, "the search walked out through the rail and found an unrelated clamp:\n%s" % out[-500:]
    finally:
        restore()


def t_a_board_that_declares_no_external_port_is_inconclusive():
    restore = _with_ports("d", [], why=None)     # no list AND no reason: nobody has looked
    try:
        d = tempfile.mkdtemp(prefix="port-none-")
        p = _net(d, {"J_X": "x"}, {"SIG": [("J_X", "1")]})
        rc, out = _run(p, d)
        assert rc == 3, "a board with no declaration passed:\n%s" % out[-300:]
    finally:
        restore()


def t_every_committed_declaration_says_where_the_port_goes():
    """An exemption nobody can audit is how the four never-auto floors of 12 September came to have holes."""
    import glob
    bad = []
    for f in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        letter = os.path.splitext(os.path.basename(f))[0]
        for e in (json.load(open(f, encoding="utf-8")).get("external_ports") or []):
            if not isinstance(e, dict) or not e.get("ref"): bad.append("%s: %r" % (letter, e))
            elif len((e.get("why") or "").strip()) < 20: bad.append("%s %s: no reason" % (letter, e.get("ref")))
    assert not bad, "external port declarations with no reason: %s" % bad


def t_the_counts_carry_the_category_that_decided_the_verdict():
    """Board A's sweep read FAIL beside "unprotected: 0" (MESHSAT-862, 16 September 2026).

    Its two failing conductors are the USB-C configuration channels, whose only clamp sits behind the Power
    Delivery controller, so the controller takes the transient itself. That is the rule's second category and
    the counts did not carry it, which makes a true verdict read as a contradiction. A verdict has to contain
    its own cause."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "port_protect.py"),
               encoding="utf-8").read()
    # 17 September 2026: the write goes through `_write_both`, which writes the board's own verdict name
    # beside the set's, so the rule looks for the decision rather than for one spelling of the call.
    i = src.index('_write_both(letter, _v.FAIL if bad else _v.PASS')
    seg = src[i:i + 900]
    assert "behind_an_active_part" in seg, "the counts do not carry the behind-an-active-part category"
    assert "unprotected" in seg


def t_an_empty_declaration_is_an_answer_and_a_missing_one_is_a_question():
    """Board P's route was blocked because the two were indistinguishable (MESHSAT-862, 16 September 2026).

    P carries nothing out of the case: cell taps, a thermistor lead and a gauge bus that all end inside the
    sealed case a few centimetres away. It says so now in `external_ports: []` with the reason, and the verdict
    marks TRN-001 inapplicable to that board rather than unanswered. A board with no key at all still blocks,
    because nobody having looked is not the same as having looked and found nothing."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "port_protect.py"),
               encoding="utf-8").read()
    assert 'answered = "external_ports" in' in src, "the tool cannot tell an empty declaration from a missing one"
    # 16 September 2026, evening: an answered board is a PASS and not an inapplicability. "Every exposed port
    # is protected" is true of a board that has none, which is this project's own declared-zero rule, and
    # INCONCLUSIVE counted board P against the set's readiness as a question nobody had answered.
    assert "if answered and why:" in src, "an answered board is still reported as unanswered"
    import json
    tbl = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "boards", "p.json")
    d = json.load(open(tbl, encoding="utf-8"))
    assert "external_ports" in d and d["external_ports"] == [], "board P no longer declares its ports"
    assert len((d.get("_external_ports_why") or "")) > 80, "board P's empty declaration carries no reason"


def t_the_rule_blocks_what_ships_and_not_what_routes():
    """Board E's route was refused for an owner decision that a route cannot change (16 September 2026).

    Four of E's conductors meet their clamp only through an active part, which is decision 31 and is open with
    the owner. TRN-001 is a SCHEMATIC property: the netlist decides it, a routing pass cannot make it better or
    worse, and stopping the route for it turns an open decision into a stop on unrelated work. The pre-route
    chain reports it; the finish blocks on it, which is the last gate before a board is cut."""
    import os
    tools = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full = open(os.path.join(tools, "full.sh"), encoding="utf-8").read()
    fin = open(os.path.join(tools, "finish.sh"), encoding="utf-8").read()
    i = full.index("port_protect.py")
    seg = full[i:i + 900]
    assert "block " not in seg.split("\n")[1], "the pre-route chain still blocks on the port rule"
    assert "does not block the route" in seg, "the pre-route chain does not say what it is doing"
    assert "port_protect.py" in fin and "PORTS a conductor leaves the case" in fin, \
        "the finish does not block on TRN-001, so moving it out of the pre-route weakened the rule"
    # and not blocking is only half of it: routeflow's pre stage collects every verdict and requires PASS, so
    # the phase has to reach the VERDICT as well as the shell (board E was refused twice for the same thing)
    assert "VERDICT_ADVISORY=1 python3 ../tools/port_protect.py" in full, \
        "the pre-route verdict is still a bar, so the collector refuses the route even though the shell does not"
    i2 = fin.index("port_protect.py")
    assert "VERDICT_ADVISORY" not in fin[max(0, i2 - 200):i2], \
        "the finish's own run is advisory too, which would leave TRN-001 deciding nothing anywhere"


def t_the_finding_names_the_active_part_that_takes_the_transient():
    """DEFECTIVE fixture, expected verdict FAIL, and the row must name BOTH parts of the path.

    The walk carried `crossed_active` as a boolean, so every row read "the clamp (D9 on OUT) is behind an
    active part" and no row ever said WHICH part. That is the one fact an owner needs in order to rule on the
    topology: the path is connector -> ACTIVE PART -> clamp, and naming only the clamp describes two thirds of
    it. Board E's decision 31 could not be written from this evidence on 16 September 2026.

    The acceptable-construction direction is held by t_protection_is_a_chain_through_a_fuse: a clamp behind a
    FUSE is protection and must not be reported here at all.
    """
    restore = _with_ports("d", [{"ref": "J_X", "why": "the shore DC inlet"}])
    try:
        d = tempfile.mkdtemp(prefix="port-name-")
        p = _net(d, {"J_X": "inlet", "F9": "10 A blade", "Q9": "CSD18510 pass FET", "D9": "SMCJ33A", "U1": "load"},
                 {"IN": [("J_X", "1"), ("F9", "1")], "FUSED": [("F9", "2"), ("Q9", "1")],
                  "OUT": [("Q9", "2"), ("D9", "1"), ("U1", "3")], "GND": [("J_X", "2"), ("D9", "2")]})
        rc, out = _run(p, d)
        assert rc == 1, "the defective fixture did not FAIL:\n%s" % out[-600:]
        assert "ACTIVE Q9" in out, "the row does not name the active part that sees the transient:\n%s" % out[-600:]
        assert "CLAMP D9" in out, "the row does not name the clamp:\n%s" % out[-600:]
        # and the values, because a ruling needs the part, not only the designator
        assert "CSD18510" in out and "SMCJ33A" in out, "the row names designators without their values:\n%s" % out[-600:]
    finally:
        restore()


def t_a_declared_zero_of_external_ports_is_an_answer():
    """This project's own rule, applied to this rule (16 September 2026). A board with no impedance-targeted
    pair class passes the pair gate; a board with nothing pruned passes the pruned gate; and board P, which
    declares with a reason that no conductor of its own leaves the enclosure, was reading INCONCLUSIVE and
    counting against the set's readiness as an unanswered question. "Every exposed port is protected" is TRUE
    of a board that has none. A zero with no reason behind it stays a question, and so does a missing key."""
    import os
    src = open(os.path.join(TOOLS, "port_protect.py"), encoding="utf-8").read()
    i = src.index("if not n_declared:")
    w = src[i:i + 2200]
    assert "if answered and why:" in w, "a declared zero cannot pass"
    assert "_v.PASS" in w, "the declared-zero branch writes no pass"
    assert "a zero with nothing" in w, "a declaration with no reason is not distinguished from one with"


def t_a_declared_zero_with_a_reason_passes_and_without_one_does_not():
    """The pair of cases, run rather than read. Board D stands in for both because the fixture can give it and
    take away its reason; board P is the real one."""
    restore = _with_ports("d", [], why="every conductor of this board ends inside the sealed case, and the "
                                       "reason is written here so the zero is an answer")
    try:
        dd = tempfile.mkdtemp(prefix="port-zero-why-")
        p = _net(dd, {"J_X": "x"}, {"SIG": [("J_X", "1")]})
        rc, out = _run(p, dd)
        assert rc == 0, "a declared zero with its reason did not pass:\n%s" % out[-300:]
    finally:
        restore()
    restore = _with_ports("d", [], why="")
    try:
        dd = tempfile.mkdtemp(prefix="port-zero-nowhy-")
        p = _net(dd, {"J_X": "x"}, {"SIG": [("J_X", "1")]})
        rc, out = _run(p, dd)
        assert rc == 3, "a zero with an empty reason passed:\n%s" % out[-300:]
    finally:
        restore()


def t_a_clamp_two_parts_past_the_active_one_is_not_this_conductors_protection():
    """17 September 2026, board E's sensor pod. The chain crossed the RP2040 onto an unrelated logic net, crossed
    a second transistor and landed on the SHORE INLET's SMCJ40A, and the two I2C conductors of a connector on the
    outside of the case were reported as protected by it. Once the chain has crossed a semiconductor, that part
    is what meets the transient; a clamp on one of ITS OWN nets is the topology owner decision 31 asks about, and
    anything past that belongs to another circuit. The defective fixture is that shape and must read FAIL."""
    restore = _with_ports("d", [{"ref": "J_X", "why": "a sensor pod outside the case, on a sealed lead"}])
    try:
        d = tempfile.mkdtemp(prefix="port-far-clamp-")
        p = _net(d, {"J_X": "pod", "U1": "RP2040 controller", "U2": "hot-swap controller", "D9": "SMCJ40A"},
                 {"SDA": [("J_X", "1"), ("U1", "3")], "PGOOD": [("U1", "4"), ("U2", "2")],
                  "DCP": [("U2", "1"), ("D9", "1")], "GND": [("J_X", "2"), ("D9", "2")]})
        rc, out = _run(p, d)
        assert rc == 1, "a clamp two parts away was accepted as the pod's protection:\n%s" % out[-500:]
        # the COUNTS, never the summary sentence, which carries both words whatever the answer
        assert '"unprotected": 1' in out and '"behind_an_active_part": 0' in out, \
            "the far clamp was reported as this conductor's protection:\n%s" % out[-500:]
    finally:
        restore()


def t_a_clamp_on_the_active_parts_own_net_is_still_reported_behind_it():
    """The acceptable half of the same rule, and the case owner decision 31 is actually about: board E's shore
    inlet is connector -> fuse -> ideal-diode FET -> SMCJ40A, so the clamp sits on a net of the part that meets
    the transient. That must keep reading as a clamp BEHIND an active part, named, and not become a bare
    'nothing between': the two are different questions and the decision needs them apart."""
    restore = _with_ports("d", [{"ref": "J_X", "why": "the shore DC inlet on the wall receptacle"}])
    try:
        d = tempfile.mkdtemp(prefix="port-behind-")
        p = _net(d, {"J_X": "inlet", "F1": "10 A", "Q1": "ideal diode FET", "D9": "SMCJ40A"},
                 {"DCIN": [("J_X", "1"), ("F1", "1")], "DCF": [("F1", "2"), ("Q1", "1")],
                  "DCP": [("Q1", "2"), ("D9", "1")], "GND": [("J_X", "2"), ("D9", "2")]})
        rc, out = _run(p, d)
        assert rc == 1, "the behind-an-active-part case no longer refuses:\n%s" % out[-500:]
        assert "ACTIVE Q1" in out and "CLAMP D9" in out, \
            "the row must name the part that sees the transient and the clamp behind it:\n%s" % out[-500:]
        assert '"unprotected": 0' in out and '"behind_an_active_part": 1' in out, \
            "a clamp on the FET's own net was counted as no protection at all:\n%s" % out[-500:]
    finally:
        restore()


def t_ground_is_where_the_search_stops_whatever_the_board_calls_it():
    """`SKIP_NETS` is a list of exact names and board E's isolated vehicle return is `GND_V`. Ground is every
    net's neighbour, so a chain that steps onto one reaches the whole board: this fixture puts the only clamp on
    a ground called `GND_V` and the conductor must read as unprotected."""
    restore = _with_ports("d", [{"ref": "J_X", "why": "a jack on the face"}])
    try:
        d = tempfile.mkdtemp(prefix="port-ground-")
        p = _net(d, {"J_X": "jack", "U1": "codec", "D9": "SMCJ40A"},
                 {"SIG": [("J_X", "1"), ("U1", "3")], "GND_V": [("U1", "4"), ("D9", "2"), ("J_X", "2")],
                  "DCP": [("D9", "1")]})
        rc, out = _run(p, d)
        assert rc == 1, "a clamp reached through a ground net was accepted:\n%s" % out[-500:]
        assert '"unprotected": 1' in out and '"behind_an_active_part": 0' in out, \
            "a clamp on the other side of a ground net was counted as protection:\n%s" % out[-500:]
    finally:
        restore()


def t_a_rail_conductor_continues_through_a_fuse_and_not_through_a_pull_up():
    """Board E's pod takes 3.3 V from a rail that carries no clamp, and the search left that rail through a
    pull-up onto a power-good net and reported the shore inlet's clamp as the pod's. A resistor between a rail
    and a logic net is not that rail's conductor; a fuse, a bead or a choke is. Both halves are run: the pull-up
    fixture must FAIL and the fuse fixture must PASS."""
    restore = _with_ports("d", [{"ref": "J_X", "why": "the sensor pod's power feed, outside the case"}])
    try:
        d = tempfile.mkdtemp(prefix="port-pullup-")
        p = _net(d, {"J_X": "pod", "R1": "10k", "U2": "hot-swap controller", "D9": "SMCJ40A"},
                 {"+3V3_X": [("J_X", "1"), ("R1", "1")], "PGOOD": [("R1", "2"), ("U2", "2")],
                  "DCP": [("U2", "1"), ("D9", "1")], "GND": [("J_X", "2"), ("D9", "2")]})
        rc, out = _run(p, d)
        assert rc == 1, "a rail left through a pull-up and took another circuit's clamp:\n%s" % out[-500:]
        assert '"unprotected": 1' in out and '"behind_an_active_part": 0' in out, \
            "the rail's pull-up carried the search into another circuit:\n%s" % out[-500:]
    finally:
        restore()
    restore = _with_ports("d", [{"ref": "J_X", "why": "the sensor pod's power feed, outside the case"}])
    try:
        d = tempfile.mkdtemp(prefix="port-fuse-")
        p = _net(d, {"J_X": "pod", "F1": "1 A", "D9": "SMCJ40A"},
                 {"+3V3_X": [("J_X", "1"), ("F1", "1")], "POD_P": [("F1", "2"), ("D9", "1")],
                  "GND": [("J_X", "2"), ("D9", "2")]})
        rc, out = _run(p, d)
        assert rc == 0, "a clamp behind the rail's own fuse was refused:\n%s" % out[-500:]
    finally:
        restore()


def t_a_conductor_whose_own_part_carries_the_protection_is_answered_with_its_citation():
    """ACCEPTABLE fixture, expected verdict PASS (decision 31, 21 September 2026).

    Board A's two CC conductors reach U18 with no clamp between, and TI's own datasheet says the part has ESD
    protection built into those pins so that no external protection is necessary. That is an ANSWER and not an
    exemption, so the declaration names the part and quotes the document, and the tool checks the named part is
    actually on that conductor before it believes a word of it."""
    restore = _with_ports("d", [{"ref": "J_X", "why": "a jack on the face",
                                 "protected_in_part": {"pins": ["1"], "part": "U1",
                                                       "cite": "vendor/x.pdf 9.1.1: protection is built into this pin"}}])
    try:
        d = tempfile.mkdtemp(prefix="port-inpart-ok-")
        p = _net(d, {"J_X": "face jack", "U1": "controller"},
                 {"SIG": [("J_X", "1"), ("U1", "3")], "GND": [("J_X", "2")]})
        rc, out = _run(p, d)
        assert rc == 0, "a cited in-part answer did not pass:\n%s" % out[-700:]
        assert "protection inside U1" in out, out[-700:]
        v = json.load(open(os.path.join(d, "out", "port_protect_d.verdict.json")))
        assert v["counts"].get("answered_in_part") == 1, v["counts"]
    finally:
        restore()


def t_an_in_part_declaration_that_names_a_part_the_conductor_does_not_reach_is_refused():
    """DEFECTIVE fixture, expected verdict FAIL. The whole risk of this declaration is that it becomes a way to
    write a failure away, so the tool asks the NETLIST whether the named part is on that conductor. Here it is
    not, and the conductor must read as what it is: bare."""
    restore = _with_ports("d", [{"ref": "J_X", "why": "a jack on the face",
                                 "protected_in_part": {"pins": ["1"], "part": "U9",
                                                       "cite": "a document that says something about U9"}}])
    try:
        d = tempfile.mkdtemp(prefix="port-inpart-bad-")
        p = _net(d, {"J_X": "face jack", "U1": "controller", "U9": "something else"},
                 {"SIG": [("J_X", "1"), ("U1", "3")], "OTHER": [("U9", "1")], "GND": [("J_X", "2")]})
        rc, out = _run(p, d)
        assert rc == 1, "a declaration naming a part off the conductor passed:\n%s" % out[-700:]
        assert "is not on" in out, out[-700:]
    finally:
        restore()


def t_an_in_part_declaration_with_no_citation_is_refused():
    """DEFECTIVE fixture, expected verdict FAIL. A part name without the document that says so is an assertion,
    and this rule exists precisely where the evidence is somebody else's datasheet."""
    restore = _with_ports("d", [{"ref": "J_X", "why": "a jack on the face",
                                 "protected_in_part": {"pins": ["1"], "part": "U1", "cite": "  "}}])
    try:
        d = tempfile.mkdtemp(prefix="port-inpart-nocite-")
        p = _net(d, {"J_X": "face jack", "U1": "controller"},
                 {"SIG": [("J_X", "1"), ("U1", "3")], "GND": [("J_X", "2")]})
        rc, out = _run(p, d)
        assert rc == 1, "an uncited in-part answer passed:\n%s" % out[-700:]
        assert "no citation" in out, out[-700:]
    finally:
        restore()


def t_a_clamp_on_the_next_segment_of_the_power_path_is_this_conductors_clamp():
    """ACCEPTABLE fixture, expected verdict PASS (21 September 2026, found while ruling decision 31).

    Connector, fuse, clamp is the textbook entry and board E has it twice. The search refused to look at a rail
    it reached by traversal, which was written to stop a sensor pod walking out through the whole board, and it
    also blinded the tool to the segment on the OTHER side of a port's own fuse: board E's solar input read
    'meets its own clamp before anything else' until 20 September, when PV_P was declared a rail for the power
    rules, and then read 'reaches a chip with nothing between' with its SMCJ28A untouched two millimetres away.
    A rail reached along the POWER PATH from the port's own conductor is still that conductor's chain. A rail
    reached through anything else is not, which the pull-up fixture beside this one holds."""
    restore = _with_ports("d", [{"ref": "J_X", "why": "the solar lead, outdoors by definition"}])
    try:
        d = tempfile.mkdtemp(prefix="port-fuse-clamp-")
        p = _net(d, {"J_X": "panel in", "F2": "10 A mini blade", "D4": "SMCJ28A panel surge", "U5": "controller"},
                 {"+PV_IN": [("J_X", "1"), ("F2", "1")],
                  "+PV_P": [("F2", "2"), ("D4", "1"), ("U5", "4")],
                  "GND": [("J_X", "2"), ("D4", "2")]})
        rc, out = _run(p, d)
        assert rc == 0, "a clamp one fuse past the connector was not seen:\n%s" % out[-700:]
    finally:
        restore()


# ---------------------------------------------------------------------------------------------------------
# CLAMP POLARITY (S-09 of MESHSAT-1357, 26 September 2026). A03 found sixteen one-way clamps all drawn with the
# bidirectional Device:D_TVS, and seven of them with the band on the return. These fixtures carry what a KiCad
# export carries (libsource and pinfunction), written the way kisch.tvs() draws a one-way part (Device:D_Zener,
# K on pin 1) or the way the boards drew them before (Device:D_TVS, A1 and A2).

def _net_full(d, comps, nets, stem="pcb-d-aprs", intent=None):
    """comps: {ref: (value, "Lib:Part")}; nets: {name: [(ref, pin, pinfunction)]}."""
    os.makedirs(d, exist_ok=True)
    c = "".join('    (comp (ref "%s")\n      (value "%s")\n      (footprint "Diode_SMD:D_SMB")\n'
                '      (libsource (lib "%s") (part "%s") (description ""))\n      (tstamps "x"))\n'
                % (r, v, lib.split(":")[0], lib.split(":")[1]) for r, (v, lib) in sorted(comps.items()))
    n = ""
    for i, (name, nodes) in enumerate(sorted(nets.items()), 1):
        body = "".join('      (node (ref "%s") (pin "%s") (pinfunction "%s") (pintype "passive"))\n' % (r, p, f)
                       for r, p, f in nodes)
        n += '    (net (code %d) (name "/%s")\n%s    )\n' % (i, name, body)
    p = os.path.join(d, "%s.net" % stem)
    open(p, "w").write("(export (version E)\n  (components\n%s  )\n  (nets\n%s  )\n)\n" % (c, n))
    if intent is not None:
        json.dump(intent, open(os.path.join(d, "%s-intent.json" % stem), "w"))
    return p


_JACK = {"ref": "J_X", "why": "the 5 V lead to the radio in its bay"}


def _clamp_fixture(prefix, k_net, a_net, lib="Device:D_Zener", value="SMBJ5.0A"):
    d = tempfile.mkdtemp(prefix=prefix)
    f1, f2 = ("K", "A") if lib.endswith("D_Zener") else ("A1", "A2")
    return d, _net_full(d, {"J_X": ("lead", "Connector_Generic:Conn_01x02"), "D1": (value, lib), "U1": ("load", "X:Y")},
                        {"+5V_X": [("J_X", "1", "Pin_1"), ("U1", "3", "VCC")] + ([("D1", "1", f1)] if k_net == "+5V_X" else [("D1", "2", f2)]),
                         "GND": [("J_X", "2", "Pin_2")] + ([("D1", "1", f1)] if k_net == "GND" else [("D1", "2", f2)])})


def t_a_one_way_clamp_with_its_band_on_the_return_is_refused():
    """DEFECTIVE (board D's D1 as drawn): the cathode on GND and the anode on the rail. The conductor still
    TOUCHES a clamp, which is all this gate used to ask, and the clamp is a forward diode across the rail."""
    restore = _with_ports("d", [_JACK])
    try:
        d, p = _clamp_fixture("clamp-rev-", "GND", "+5V_X")
        rc, out = _run(p, d)
        assert rc == 1, "a reversed one-way clamp passed:\n%s" % out[-700:]
        assert "REVERSED D1" in out and "the wrong way round" in out, out[-700:]
        v = json.load(open(os.path.join(d, "out", "port_protect.verdict.json")))
        assert v["counts"]["clamps_reversed"] == 1, v["counts"]
    finally:
        restore()


def t_a_one_way_clamp_drawn_with_its_cathode_on_the_rail_passes():
    """ACCEPTABLE: the same part the right way round, drawn as kisch.tvs() draws it (K on pin 1)."""
    restore = _with_ports("d", [_JACK])
    try:
        d, p = _clamp_fixture("clamp-ok-", "+5V_X", "GND")
        rc, out = _run(p, d)
        assert rc == 0, "a correct one-way clamp was refused:\n%s" % out[-700:]
        assert "CLAMP D1     OK" in out, out[-700:]
    finally:
        restore()


def t_a_one_way_part_on_the_bidirectional_symbol_is_refused_even_the_right_way_round():
    """DEFECTIVE (boards A and B as drawn): pad 1 is on the rail, so the land is right, and the schematic still
    shows a symbol with no cathode, so no reader and no tool can see which way the part points."""
    restore = _with_ports("d", [_JACK])
    try:
        d, p = _clamp_fixture("clamp-sym-", "+5V_X", "GND", lib="Device:D_TVS")
        rc, out = _run(p, d)
        assert rc == 1, "a one-way part on an A1/A2 symbol passed:\n%s" % out[-700:]
        assert "SYMBOL D1" in out and "hides its" in out, out[-700:]
    finally:
        restore()


def t_a_two_way_part_on_the_bidirectional_symbol_is_either_way_round():
    """ACCEPTABLE (board D's PESD5V0S1BA headset clamps): ground on pin 1 is correct for a two-way part."""
    restore = _with_ports("d", [_JACK])
    try:
        d, p = _clamp_fixture("clamp-bi-", "GND", "+5V_X", lib="Device:D_TVS", value="PESD5V0S1BA bidirectional ESD clamp")
        rc, out = _run(p, d)
        assert rc == 0, "a two-way clamp was judged for polarity:\n%s" % out[-700:]
        assert "N/A" in out, out[-700:]
    finally:
        restore()


def t_board_ds_microphone_clamp_is_judged_two_way_from_its_own_sheet():
    """ACCEPTABLE (board D's D10 and D13 since round 4, PESD12VL1BA on Device:D_TVS with ground on pin 1): the part
    number is read from Nexperia's own sheet for it (round 6); before, it read UNJUDGED and TRN-001 was INCONCLUSIVE."""
    restore = _with_ports("d", [_JACK])
    try:
        d, p = _clamp_fixture("clamp-pesd12-", "GND", "+5V_X", lib="Device:D_TVS",
                              value="PESD12VL1BA bidirectional ESD clamp at the jack: headset 1 microphone, above the electret bias")
        rc, out = _run(p, d)
        assert rc == 0 and "UNJUDGED" not in out, "the PESD12VL1BA was not read:\n%s" % out[-700:]
    finally:
        restore()


def t_board_as_restart_guard_zener_is_judged_one_way_from_its_own_sheet():
    """Board A's D22 since main 458b2873 (round 6 fourth pass): a BZT52C12-7-F on Device:D_Zener. ACCEPTABLE: cathode on
    the rail, anode on ground, OK and not UNJUDGED (the direction is read from Diodes' DS18004, "SURFACE MOUNT ZENER
    DIODE", "Polarity: Cathode Band"); on kisch 88b20565 it read UNJUDGED and the board INCONCLUSIVE. DEFECTIVE: the same
    part with its cathode on ground is REVERSED. A sibling type the sheet lists but no board fits (BZT52C15-7-F) is not
    read by family: UNJUDGED."""
    restore = _with_ports("d", [_JACK])
    try:
        val = "BZT52C12-7-F zener, the restart guard's pull-up clamp"
        d, p = _clamp_fixture("clamp-bzt-ok-", "+5V_X", "GND", value=val)
        rc, out = _run(p, d)
        assert rc == 0 and "CLAMP D1     OK" in out and "UNJUDGED" not in out, out[-700:]
        d, p = _clamp_fixture("clamp-bzt-rev-", "GND", "+5V_X", value=val)
        rc, out = _run(p, d)
        assert rc == 1 and "REVERSED D1" in out, out[-700:]
        d, p = _clamp_fixture("clamp-bzt15-", "+5V_X", "GND", value="BZT52C15-7-F")
        assert {c["ref"]: c for c in port_protect.clamp_rows(p)}["D1"]["verdict"] == "UNJUDGED"
    finally:
        restore()


def _pack(prefix, reversed_):
    """Board P's shape: no external port declared, D1 across the pack terminals, PACK_N declared as the return."""
    d = tempfile.mkdtemp(prefix=prefix)
    k, a = ("PACK_N", "PACK_P") if reversed_ else ("PACK_P", "PACK_N")
    lib = "Device:D_TVS" if reversed_ else "Device:D_Zener"
    f1, f2 = ("A1", "A2") if reversed_ else ("K", "A")
    p = _net_full(d, {"D1": ("SMBJ20A", lib), "W_P": ("lead +", "Connector:Conn_01x01_Pin"), "W_N": ("lead -", "Connector:Conn_01x01_Pin")},
                  {k: [("D1", "1", f1)] + [("W_P" if k == "PACK_P" else "W_N", "1", "1")],
                   a: [("D1", "2", f2)] + [("W_P" if a == "PACK_P" else "W_N", "1", "1")]},
                  stem="pcb-p-pack",
                  intent={"rails": {"PACK_P": {"volts": 14.4}, "PACK_N": {"volts": 0.05, "returns": "PACK_P"}}})
    return d, p


def t_a_board_that_declares_no_port_still_fails_a_reversed_clamp():
    """DEFECTIVE (board P's D1): a declared zero of external ports is an answer about ports, not about a clamp
    across the pack terminals with its band on PACK_N, the return the board's own intent declares."""
    restore = _with_ports("p", [], why="nothing of this board's own leaves the case")
    try:
        d, p = _pack("clamp-pack-rev-", True)
        rc, out = _run(p, d)
        assert rc == 1, "board P's reversed clamp passed on a declared zero:\n%s" % out[-700:]
        assert "REVERSED D1" in out and "PACK_N" in out, out[-700:]
    finally:
        restore()


def t_a_board_that_declares_no_port_and_carries_its_clamp_the_right_way_passes():
    restore = _with_ports("p", [], why="nothing of this board's own leaves the case")
    try:
        d, p = _pack("clamp-pack-ok-", False)
        rc, out = _run(p, d)
        assert rc == 0, "board P's corrected clamp was refused:\n%s" % out[-700:]
    finally:
        restore()


def t_a_clamp_between_two_conductors_nobody_placed_is_unjudged_not_passed():
    """Neither net is a ground or a declared return and no voltages are declared: the polarity cannot be read,
    and that is INCONCLUSIVE, never a pass."""
    restore = _with_ports("d", [_JACK])
    try:
        d = tempfile.mkdtemp(prefix="clamp-unj-")
        p = _net_full(d, {"J_X": ("lead", "Connector_Generic:Conn_01x02"), "D1": ("SMBJ5.0A", "Device:D_Zener"),
                          "D2": ("SMBJ5.0A", "Device:D_Zener")},
                      {"+5V_X": [("J_X", "1", "Pin_1"), ("D1", "1", "K")], "GND": [("J_X", "2", "Pin_2"), ("D1", "2", "A")],
                       "NODE_A": [("D2", "1", "K")], "NODE_B": [("D2", "2", "A")]})
        rc, out = _run(p, d)
        v = json.load(open(os.path.join(d, "out", "port_protect.verdict.json")))
        assert v["verdict"] == "INCONCLUSIVE", (v, out[-600:])
        assert v["counts"]["clamps_unjudged"] == 1, v["counts"]
    finally:
        restore()


def t_between_two_rails_the_cathode_belongs_on_the_higher_voltage():
    restore = _with_ports("d", [_JACK])
    try:
        for k, a, want in (("+12V", "+5V_X", 0), ("+5V_X", "+12V", 1)):
            d = tempfile.mkdtemp(prefix="clamp-rails-")
            p = _net_full(d, {"J_X": ("lead", "Connector_Generic:Conn_01x02"), "D1": ("SMBJ5.0A", "Device:D_Zener")},
                          {"+5V_X": [("J_X", "1", "Pin_1")], "GND": [("J_X", "2", "Pin_2")],
                           k: [("D1", "1", "K")] + ([("J_X", "1", "Pin_1")] if k == "+5V_X" else []),
                           a: [("D1", "2", "A")] + ([("J_X", "1", "Pin_1")] if a == "+5V_X" else [])},
                          intent={"rails": {"+12V": {"volts": 12.0}, "+5V_X": {"volts": 5.0}}})
            clamp = [c for c in port_protect.clamp_rows(p) if c["ref"] == "D1"][0]
            assert (clamp["orientation"] == "OK") == (want == 0), clamp
    finally:
        restore()


def t_the_last_net_of_a_kicad_netlist_is_read():
    """KiCad 9 closes the nets section on the last net's own line, "...)))))". The look-ahead this gate (and
    check_contracts) used needed a "\\n  )\\n" after it, so the last net of every netlist was never read (found by
    r4t's KiCad round trip on 26 September 2026, where the one-way clamp's anode sat on that last net)."""
    d = tempfile.mkdtemp(prefix="lastnet-")
    p = os.path.join(d, "pcb-d-aprs.net")
    open(p, "w").write('(export (version "E")\n  (components\n    (comp (ref "D1")\n      (value "SMBJ5.0A")\n'
                       '      (libsource (lib "Device") (part "D_Zener") (description ""))))\n  (nets\n'
                       '    (net (code "1") (name "/+5V_X") (class "Default")\n'
                       '      (node (ref "D1") (pin "1") (pinfunction "K") (pintype "passive")))\n'
                       '    (net (code "2") (name "/GND") (class "Default")\n'
                       '      (node (ref "D1") (pin "2") (pinfunction "A") (pintype "passive")))))\n')
    by_net, by_ref, _v = port_protect.netlist(p)
    assert set(by_net) == {"+5V_X", "GND"}, by_net
    rows = {c["ref"]: c for c in port_protect.clamp_rows(p)}
    assert rows["D1"]["orientation"] == "OK" and rows["D1"]["anode_net"] == "GND", rows
    src = open(os.path.join(TOOLS, "check_contracts.py"), encoding="utf-8").read()
    assert r'(?=\(net \(code|\Z)' in src, "check_contracts still stops a net at a closer KiCad 9 does not write"


# ---------------------------------------------------------------------------------------------------------
# THE DRAWING IS NEVER THE SOURCE OF A DIRECTION (review fix-up of round 4, 26 September 2026). The first polarity
# pass fell back to the drawing when the part number could not be read, so a reversed SMAJ18A on Device:D_TVS read
# N/A (a pass), and a clamp kisch.tvs(..., direction="uni") draws on Device:D_Zener was not a row at all unless its
# number was in the suppressor family list (a reversed P6KE18A was absent). Neither may read PASS.

def t_a_reversed_one_way_part_whose_number_is_not_read_does_not_pass_on_an_a1a2_drawing():
    """DEFECTIVE: SMAJ18A (not a family the helper reads) on Device:D_TVS with pad 1, the band, on GND."""
    restore = _with_ports("d", [_JACK])
    try:
        d, p = _clamp_fixture("clamp-smaj-", "GND", "+5V_X", lib="Device:D_TVS", value="SMAJ18A")
        rows = {c["ref"]: c for c in port_protect.clamp_rows(p)}
        assert rows["D1"]["verdict"] == "UNJUDGED", rows["D1"]
        rc, out = _run(p, d)
        v = json.load(open(os.path.join(d, "out", "port_protect.verdict.json")))
        assert v["verdict"] != "PASS" and rc != 0, (v["verdict"], out[-600:])
        assert v["counts"]["clamps_unjudged"] == 1, v["counts"]
    finally:
        restore()


def t_a_reversed_one_way_part_on_the_zener_symbol_is_a_row_and_fails():
    """DEFECTIVE: P6KE18A on Device:D_Zener with K on GND and A on the rail. It used to be absent from the rows."""
    restore = _with_ports("d", [_JACK])
    try:
        d, p = _clamp_fixture("clamp-p6ke-", "GND", "+5V_X", lib="Device:D_Zener", value="P6KE18A")
        rows = {c["ref"]: c for c in port_protect.clamp_rows(p)}
        assert "D1" in rows and rows["D1"]["verdict"] == "REVERSED", rows
        rc, out = _run(p, d)
        assert rc == 1, "a reversed P6KE18A on D_Zener passed:\n%s" % out[-700:]
    finally:
        restore()


def t_an_unread_part_on_the_zener_symbol_the_right_way_is_undecided_without_a_declaration():
    """A K/A drawing is not evidence of what is bought: P6KE18A, K on the rail, and no declaration of its direction."""
    restore = _with_ports("d", [_JACK])
    try:
        d, p = _clamp_fixture("clamp-p6ke-ok-", "+5V_X", "GND", lib="Device:D_Zener", value="P6KE18A")
        rows = {c["ref"]: c for c in port_protect.clamp_rows(p)}
        assert rows["D1"]["verdict"] == "UNJUDGED", rows["D1"]
        rc, out = _run(p, d)
        v = json.load(open(os.path.join(d, "out", "port_protect.verdict.json")))
        assert v["verdict"] == "INCONCLUSIVE", (v["verdict"], out[-500:])
    finally:
        restore()


def t_a_declared_direction_with_its_basis_is_read_from_the_intent():
    """ACCEPTABLE: kisch.tvs(..., direction="uni", basis=...) writes the declaration into the intent file, and the
    gate reads it; the same part reversed against its declaration FAILS."""
    restore = _with_ports("d", [_JACK])
    try:
        for k_net, want in (("+5V_X", "OK"), ("GND", "DECLARATION")):
            d = tempfile.mkdtemp(prefix="clamp-decl-")
            p = _net_full(d, {"J_X": ("lead", "Connector_Generic:Conn_01x02"), "D1": ("P6KE18A", "Device:D_Zener")},
                          {"+5V_X": [("J_X", "1", "Pin_1")] + ([("D1", "1", "K")] if k_net == "+5V_X" else [("D1", "2", "A")]),
                           "GND": [("J_X", "2", "Pin_2")] + ([("D1", "1", "K")] if k_net == "GND" else [("D1", "2", "A")])},
                          intent={"clamps": {"D1": {"direction": "uni", "basis": "maker sheet: P6KE18A is unidirectional",
                                                    "protected": "+5V_X", "return": "GND"}}})
            row = {c["ref"]: c for c in port_protect.clamp_rows(p)}["D1"]
            if want == "OK":
                assert row["verdict"] == "OK" and "declared uni" in row["basis"], row
            else:
                # the reversed land reads REVERSED and the declaration disagrees with the netlist: the worse is named
                assert row["verdict"] in ("DECLARATION", "REVERSED") and row["orientation"] == "REVERSED", row
            rc, out = _run(p, d)
            assert (rc == 0) == (want == "OK"), (want, out[-600:])
    finally:
        restore()


def t_a_declaration_that_contradicts_the_part_number_fails():
    restore = _with_ports("d", [_JACK])
    try:
        d = tempfile.mkdtemp(prefix="clamp-contra-")
        p = _net_full(d, {"J_X": ("lead", "Connector_Generic:Conn_01x02"), "D1": ("SMBJ5.0A", "Device:D_Zener")},
                      {"+5V_X": [("J_X", "1", "Pin_1"), ("D1", "1", "K")], "GND": [("J_X", "2", "Pin_2"), ("D1", "2", "A")]},
                      intent={"clamps": {"D1": {"direction": "bi", "basis": "a wrong claim", "protected": "+5V_X", "return": "GND"}}})
        row = {c["ref"]: c for c in port_protect.clamp_rows(p)}["D1"]
        assert row["verdict"] == "DECLARATION", row
        rc, out = _run(p, d)
        assert rc == 1, out[-500:]
    finally:
        restore()


# ---------------------------------------------------------------------------------------------------------
# Second fix-up of round 4 (26 September 2026): a clamp on a conductor below its return, and a suppressor whose
# reference does not start with D.

def t_on_a_negative_conductor_the_cathode_belongs_on_the_return():
    """A one-way clamp on -12V: ACCEPTABLE with its cathode on GND and its anode on -12V; DEFECTIVE the other way,
    which the first version called OK because it assumed every protected conductor is positive."""
    for k, a, want in (("GND", "-12V", "OK"), ("-12V", "GND", "REVERSED")):
        d = tempfile.mkdtemp(prefix="clamp-neg-")
        p = _net_full(d, {"D1": ("SMBJ12A", "Device:D_Zener")}, {k: [("D1", "1", "K")], a: [("D1", "2", "A")]},
                      intent={"rails": {"-12V": {"volts": -12.0}}})
        row = {c["ref"]: c for c in port_protect.clamp_rows(p)}["D1"]
        assert row["orientation"] == want, (k, a, row)


def t_a_suppressor_whose_reference_is_not_a_d_is_still_judged():
    """DEFECTIVE: an SMBJ5.0A drawn as Z1 from a library that is not Device, band on GND. It was not a row, because
    the value family was matched only on D references; a resistor whose value happens to start the same way is not."""
    d = tempfile.mkdtemp(prefix="clamp-z-")
    p = _net_full(d, {"Z1": ("SMBJ5.0A", "meshsat:TVS"), "CR1": ("SMBJ5.0A", "meshsat:TVS"), "R9": ("TVS bias 10k", "Device:R")},
                  {"+5V_X": [("Z1", "2", "A"), ("CR1", "1", "K"), ("R9", "1", "")],
                   "GND": [("Z1", "1", "K"), ("CR1", "2", "A"), ("R9", "2", "")]})
    rows = {c["ref"]: c for c in port_protect.clamp_rows(p)}
    assert rows["Z1"]["orientation"] == "REVERSED" and rows["CR1"]["orientation"] == "OK" and "R9" not in rows, rows


# ---------------------------------------------------------------------------------------------------------
# THE DECLARATION IS JUDGED TOO (28 September 2026, MESHSAT-1357, the review of decision 31). Board A declared J_DOCK
# pins 1 and 2 as the shore and vehicle input; session choice SC-55 (EQ-16) moved VIN_RAW to J_VR1 to J_VR4 and left
# those two pins ground. The tool skips a ground pin, so the entry judged nothing, TRN-001 read PASS, and the conductor
# the entry was written for stood on four pins no entry named.

def _verdict_of(d, letter="d"):
    return json.load(open(os.path.join(d, "out", "port_protect_%s.verdict.json" % letter)))


def t_a_declared_port_on_a_ground_pin_is_refused_and_the_real_supply_pin_is_reported():
    """DEFECTIVE, board A's shape: the declared pins are ground since the supply moved, and the supply's own pin,
    which reaches a controller with nothing between, is in no entry. It read PASS."""
    restore = _with_ports("d", [{"ref": "J_DOCK", "pins": ["1", "2"],
                                 "why": "shore and vehicle DC arriving over the dock from the wall receptacle"}])
    try:
        d = tempfile.mkdtemp(prefix="port-ground-pin-")
        p = _net(d, {"J_DOCK": "spring pins to the dock", "J_VR1": "9 A spring pin, VIN_RAW", "U2": "buck-boost controller"},
                 {"GND": [("J_DOCK", "1"), ("J_DOCK", "2"), ("U2", "9")], "VIN_RAW": [("J_VR1", "1"), ("U2", "2")]})
        rc, out = _run(p, d)
        assert rc == 1, "a port declared on two ground pins passed while the supply pin was in no entry:\n%s" % out[-900:]
        assert "J_DOCK.1 is on GND" in out and "J_DOCK.2 is on GND" in out and "names no conductor" in out, out[-900:]
        assert "UNCOVERED J_VR1.1 on VIN_RAW" in out, "the supply pin no entry covers was not reported:\n%s" % out[-900:]
        v = _verdict_of(d)
        assert v["verdict"] == "FAIL" and v["counts"]["declarations_refused"] == 2 and v["counts"]["uncovered_pins"] == 1, v["counts"]
    finally:
        restore()


def t_the_same_board_with_its_supply_pin_declared_is_judged_on_that_pin():
    """The corrected declaration, both ways: with a clamp on the supply it PASSES, and without one the conductor is
    judged and FAILS as bare, which is what the ground-pin entry had hidden."""
    ports = [{"ref": "J_VR1", "why": "shore and vehicle DC arriving over the dock from the wall receptacle"}]
    internal = [{"ref": "J_DOCK", "why": "signal pins between two boards inside the case, through the dock block"}]
    for clamp, want in ((True, 0), (False, 1)):
        restore = _with_ports("d", ports, internal=internal)
        try:
            d = tempfile.mkdtemp(prefix="port-supply-pin-")
            comps = {"J_DOCK": "spring pins to the dock", "J_VR1": "9 A spring pin, VIN_RAW", "U2": "buck-boost controller"}
            nets = {"GND": [("J_DOCK", "1"), ("J_DOCK", "2"), ("U2", "9")], "VIN_RAW": [("J_VR1", "1"), ("U2", "2")],
                    "SIG": [("J_DOCK", "8"), ("U2", "5")]}
            if clamp:
                comps["D2"] = "SMCJ40CA"; nets["VIN_RAW"].append(("D2", "1")); nets["GND"].append(("D2", "2"))
            p = _net(d, comps, nets)
            rc, out = _run(p, d)
            assert rc == want, (clamp, out[-900:])
            if not clamp: assert "nothing between" in out and "J_VR1.1 on VIN_RAW" in out, out[-900:]
            else: assert _verdict_of(d)["counts"]["internal_pins"] == 1, _verdict_of(d)["counts"]
        finally:
            restore()


def t_an_entry_none_of_whose_pins_carries_a_conductor_is_refused():
    """DEFECTIVE: a return pin declared as a port. Every pin is skipped, so the entry judges nothing."""
    restore = _with_ports("d", [{"ref": "J_VN1", "why": "the return of the shore and vehicle input over the dock"}])
    try:
        d = tempfile.mkdtemp(prefix="port-return-")
        p = _net(d, {"J_VN1": "9 A spring pin, return", "U1": "load"}, {"GND": [("J_VN1", "1"), ("U1", "2")]})
        rc, out = _run(p, d)
        assert rc == 1 and "no pin of this external entry carries a supply or a signal" in out, out[-700:]
    finally:
        restore()


def t_a_listed_pin_the_connector_does_not_have_is_refused():
    restore = _with_ports("d", [{"ref": "J_X", "pins": ["1", "7"], "why": "a jack on the face that a person plugs a lead into"}])
    try:
        d = tempfile.mkdtemp(prefix="port-nopin-")
        p = _net(d, {"J_X": "jack", "D9": "PESD5V0S1BA", "U1": "codec"},
                 {"SIG": [("J_X", "1"), ("D9", "2"), ("U1", "3")], "GND": [("J_X", "2"), ("D9", "1")]})
        rc, out = _run(p, d)
        assert rc == 1 and "lists pin 7 and J_X has no such pin" in out, out[-700:]
    finally:
        restore()


def t_a_connector_pin_no_entry_covers_is_a_question_and_an_internal_entry_answers_it():
    """The declared port is clamped and the rule used to stop there. A second connector reaches a chip and is in no
    entry: INCONCLUSIVE, named. With an internal entry and its reason: PASS. With an entry and no reason: FAIL."""
    ports = [{"ref": "J_X", "why": "a jack on the face that a person plugs a lead into"}]
    comps = {"J_X": "jack", "D9": "PESD5V0S1BA", "U1": "codec", "J_Y": "lead", "U2": "hub", "JP1": "solder jumper", "TP1": "probe"}
    nets = {"SIG": [("J_X", "1"), ("D9", "2"), ("U1", "3")], "GND": [("J_X", "2"), ("D9", "1"), ("J_Y", "4")],
            "USB_P": [("J_Y", "3"), ("U2", "20"), ("TP1", "1")], "BIAS": [("JP1", "1"), ("U1", "5")]}
    for internal, want, word in ((None, 3, "UNCOVERED J_Y.3 on USB_P"),
                                 ([{"ref": "J_Y", "why": "the touch lead of the monitor, which stays inside the case"}], 0, "1 connector pin(s) declared internal"),
                                 ([{"ref": "J_Y", "why": "inside"}], 1, "declared internal with no reason")):
        restore = _with_ports("d", ports, internal=internal)
        try:
            d = tempfile.mkdtemp(prefix="port-cover-")
            rc, out = _run(_net(d, comps, nets), d)
            assert rc == want and word in out, (internal, rc, out[-900:])
            # a solder jumper and a test point are not connectors, and a ground pin is not a conductor
            assert "UNCOVERED JP1" not in out and "UNCOVERED TP1" not in out and "UNCOVERED J_Y.4" not in out, out[-900:]
            assert "SKIPPED J_X.2 on GND" in out, "the skipped ground pin of a declared port is not named:\n%s" % out[-900:]
        finally:
            restore()


def t_a_pin_declared_external_and_internal_is_refused():
    restore = _with_ports("d", [{"ref": "J_X", "why": "a jack on the face that a person plugs a lead into"}],
                          internal=[{"ref": "J_X", "why": "the same jack, said to stay inside the case"}])
    try:
        d = tempfile.mkdtemp(prefix="port-both-")
        p = _net(d, {"J_X": "jack", "D9": "PESD5V0S1BA", "U1": "codec"},
                 {"SIG": [("J_X", "1"), ("D9", "2"), ("U1", "3")], "GND": [("J_X", "2"), ("D9", "1")]})
        rc, out = _run(p, d)
        assert rc == 1 and "declared both external and internal" in out, out[-700:]
    finally:
        restore()


def t_a_connector_is_read_by_its_reference_and_never_by_its_library():
    """These generators draw several integrated circuits and a choke with Connector_Generic symbols (board E's U3 and
    L2), so the library cannot say what a connector is. The reference can: J, P, PAD and W; never JP, TP, U or L."""
    for ref, want in (("J1", True), ("J_DOCK", True), ("P_VR", True), ("PAD_W1", True), ("W_P", True), ("P3", True),
                      ("JP1", False), ("TP13", False), ("U3", False), ("L2", False), ("PS1", False), ("Q1", False)):
        assert bool(port_protect.CONNECTOR.match(ref)) == want, ref
    assert not port_protect.carries_conductor("GND_V") and not port_protect.carries_conductor("unconnected-(J1-Pad3)")
    assert port_protect.carries_conductor("VIN_RAW") and port_protect.carries_conductor("+3V3_E6")


# ---------------------------------------------------------------------------------------------------------
# THE REVIEWED SET (28 September 2026, the fresh check of stream d8dec31, item B1; open item S-88, finding H3-02 of the
# independent review of handover H3). Open item S-88 asks that "moving or omitting a declared entry demands reconciliation
# and never shrinks the coverage in silence". Three shapes of moving: onto ground pins (refused, FAIL, above), out of the
# declaration (uncovered, INCONCLUSIVE, above), and from `external_ports` INTO `internal_ports` with a reason, which the
# tool accepted in silence (board A's J_USBW moved that way read PASS of 38 instead of 42). The reviewed set closes the
# third: the declaration's external pins must be exactly the pins a named review enumerated, pin by pin.

_COMPS = {"J_X": "jack", "D9": "PESD5V0S1BA", "U1": "codec", "J_Y": "lead", "D8": "USBLC6-2SC6", "U2": "hub"}
_NETS = {"SIG": [("J_X", "1"), ("D9", "2"), ("U1", "3")], "GND": [("J_X", "2"), ("D9", "1"), ("D8", "2"), ("J_Y", "4")],
         "USB_P": [("J_Y", "3"), ("U2", "20"), ("D8", "1")], "USB_N": [("J_Y", "2"), ("U2", "21"), ("D8", "3")]}
_EXT = [{"ref": "J_X", "why": "a jack on the face that a person plugs a lead into"},
        {"ref": "J_Y", "why": "the wall USB port on the connector plate, a stranger's stick goes in"}]
_INSIDE = "said to stay inside the case now, the port having moved to a lid harness"


def _reviewed(ext, changes=(), review=REVIEW_DOC, why=None):
    return {"review": review, "reviewed_on": "2026-09-28", "external": ext, "changes": list(changes),
            "why": why if why is not None else "a fixture record: the pins a review enumerated from this fixture's netlist, for the test"}


_REV_XY = {"J_X": {"1": "SIG"}, "J_Y": {"2": "USB_N", "3": "USB_P"}}


def t_the_declaration_that_matches_its_reviewed_set_passes():
    restore = _with_ports("d", _EXT)
    try:
        d = tempfile.mkdtemp(prefix="port-rev-ok-")
        rc, out = _run(_net(d, _COMPS, _NETS), d, reviewed=_reviewed(_REV_XY))
        assert rc == 0 and "holds 3 external pin(s) for board D, the declaration 3" in out, out[-900:]
        v = _verdict_of(d)
        assert v["counts"]["reviewed_pins"] == 3 and v["counts"]["declared_external_pins"] == 3 and \
            v["counts"]["review_disagreements"] == 0, v["counts"]
        assert v["inputs"]["port_reviews"]["sha256_16"], "the reviewed sets' file is not recorded as an input"
    finally:
        restore()


def t_a_reviewed_entry_moved_into_internal_ports_is_inconclusive_by_name():
    """THE THIRD SHAPE: J_Y leaves external_ports for internal_ports with a reason. Before: PASS of fewer pins, in
    silence. Now: INCONCLUSIVE, naming J_Y.2 and J_Y.3 as RECLASSIFIED, until the reviewed set carries the change."""
    restore = _with_ports("d", _EXT[:1], internal=[{"ref": "J_Y", "why": _INSIDE}])
    try:
        d = tempfile.mkdtemp(prefix="port-rev-moved-")
        rc, out = _run(_net(d, _COMPS, _NETS), d, reviewed=_reviewed(_REV_XY))
        assert rc == 3, "a reviewed external entry moved into internal_ports passed:\n%s" % out[-900:]
        assert "RECLASSIFIED J_Y.2 on USB_N" in out and "RECLASSIFIED J_Y.3 on USB_P" in out, out[-900:]
        v = _verdict_of(d)
        assert v["verdict"] == "INCONCLUSIVE" and v["counts"]["review_disagreements"] == 2, v["counts"]
        assert any("RECLASSIFIED J_Y.3" in e for e in v["evidence"]), v["evidence"]
    finally:
        restore()


def t_the_reviewed_set_changed_with_its_reason_and_its_review_reconciles_the_move():
    """The same move, reconciled: the reviewed set drops J_Y and records the change with a reason of forty characters
    and the review it rests on. PASS. With the reason too short, or a review that is not in the tree, or the set still
    holding the pin the change says left: INCONCLUSIVE, the record being no record."""
    restore = _with_ports("d", _EXT[:1], internal=[{"ref": "J_Y", "why": _INSIDE}])
    try:
        ok = [{"entry": "J_Y.2", "was": "external", "now": "internal", "on": "2026-09-28", "review": REVIEW_DOC,
               "why": "the wall USB port moved to the lid harness by a session choice, and the lead no longer leaves the case"},
              {"entry": "J_Y.3", "was": "external", "now": "internal", "on": "2026-09-28", "review": REVIEW_DOC,
               "why": "the wall USB port moved to the lid harness by a session choice, and the lead no longer leaves the case"}]
        for changes, ext, want, word in (
                (ok, {"J_X": {"1": "SIG"}}, 0, "3 external pin(s)"),
                ([dict(ok[0], why="moved inside"), ok[1]], {"J_X": {"1": "SIG"}}, 3, "no reason of 40 characters"),
                ([dict(ok[0], review="v2/docs/reviews/NO-SUCH-REVIEW.md"), ok[1]], {"J_X": {"1": "SIG"}}, 3, "which is not in this tree"),
                (ok, _REV_XY, 3, "left the set and the set still holds it")):
            d = tempfile.mkdtemp(prefix="port-rev-change-")
            rc, out = _run(_net(d, _COMPS, _NETS), d, reviewed=_reviewed(ext, changes))
            assert rc == want, (changes[0].get("why")[:20], changes[0].get("review"), rc, out[-900:])
            if want == 0: assert "holds 1 external pin(s) for board D, the declaration 1; 2 change(s) recorded" in out, out[-900:]
            else: assert word in out, (word, out[-900:])
    finally:
        restore()


def t_a_reviewed_entry_left_out_of_the_declaration_is_named_twice():
    """THE SECOND SHAPE, with the reviewed set: the entry is gone from both lists. UNCOVERED (the pin is in no entry)
    and REVIEWED (the review holds it external), both by name."""
    restore = _with_ports("d", _EXT[:1])
    try:
        d = tempfile.mkdtemp(prefix="port-rev-gone-")
        rc, out = _run(_net(d, _COMPS, _NETS), d, reviewed=_reviewed(_REV_XY))
        assert rc == 3 and "UNCOVERED J_Y.3 on USB_P" in out and "REVIEWED J_Y.3 on USB_P" in out, out[-900:]
    finally:
        restore()


def t_a_reviewed_entry_on_ground_pins_is_refused_and_the_reviewed_pin_is_named():
    """THE FIRST SHAPE, with the reviewed set: board A's J_DOCK. The entry lists two ground pins (FAIL, refused) and
    the pin the review holds external, J_VR1.1, is in no entry: named as REVIEWED and as UNCOVERED."""
    restore = _with_ports("d", [{"ref": "J_DOCK", "pins": ["1", "2"], "why": "shore and vehicle DC arriving over the dock"}])
    try:
        d = tempfile.mkdtemp(prefix="port-rev-ground-")
        p = _net(d, {"J_DOCK": "spring pins", "J_VR1": "9 A spring pin, VIN_RAW", "D2": "SMCJ40A", "U2": "controller"},
                 {"GND": [("J_DOCK", "1"), ("J_DOCK", "2"), ("U2", "9"), ("D2", "2")], "VIN_RAW": [("J_VR1", "1"), ("U2", "2"), ("D2", "1")]})
        rc, out = _run(p, d, reviewed=_reviewed({"J_VR1": {"1": "VIN_RAW"}}))
        assert rc == 1 and "J_DOCK.1 is on GND" in out and "UNCOVERED J_VR1.1 on VIN_RAW" in out, out[-900:]
        assert "REVIEWED J_VR1.1 on VIN_RAW" in out and "no external entry covers it" in out, out[-900:]
    finally:
        restore()


def t_a_declaration_narrowed_by_pins_is_inconclusive_for_the_pins_that_left():
    """J_Y declared external on pin 3 only and internal on pin 2: the reviewed set holds both external."""
    restore = _with_ports("d", [_EXT[0], dict(_EXT[1], pins=["3"])], internal=[{"ref": "J_Y", "pins": ["2"], "why": _INSIDE}])
    try:
        d = tempfile.mkdtemp(prefix="port-rev-narrow-")
        rc, out = _run(_net(d, _COMPS, _NETS), d, reviewed=_reviewed(_REV_XY))
        assert rc == 3 and "RECLASSIFIED J_Y.2 on USB_N" in out and "RECLASSIFIED J_Y.3" not in out, out[-900:]
    finally:
        restore()


def t_a_reviewed_pin_that_moved_to_ground_is_inconclusive_even_with_its_entry_in_place():
    """Board A's shape for an entry that lists no pins: the entry stays, the netlist moves the reviewed pin to
    ground, and the entry silently covers less. The reviewed set names the pin."""
    restore = _with_ports("d", _EXT)
    try:
        d = tempfile.mkdtemp(prefix="port-rev-toground-")
        nets = dict(_NETS); nets["GND"] = nets["GND"] + [("J_Y", "3")]; nets["USB_P"] = [("U2", "20"), ("D8", "1")]
        rc, out = _run(_net(d, _COMPS, nets), d, reviewed=_reviewed(_REV_XY))
        assert rc == 3 and "REVIEWED J_Y.3 (was USB_P)" in out and "a ground or a no-connect" in out, out[-900:]
    finally:
        restore()


def t_a_reviewed_connector_that_left_the_netlist_is_inconclusive():
    """Renamed or removed: J_Y is J_Z on the new netlist and declared internal. Without the reviewed set the rename
    would pass as a new internal lead; with it, J_Y.2 and J_Y.3 are named as not on this netlist."""
    restore = _with_ports("d", _EXT[:1], internal=[{"ref": "J_Z", "why": _INSIDE}])
    try:
        d = tempfile.mkdtemp(prefix="port-rev-renamed-")
        comps = dict(_COMPS); comps["J_Z"] = comps.pop("J_Y")
        nets = {k: [(("J_Z" if r == "J_Y" else r), p) for r, p in v] for k, v in _NETS.items()}
        rc, out = _run(_net(d, comps, nets), d, reviewed=_reviewed(_REV_XY))
        assert rc == 3 and "REVIEWED J_Y.2 (was USB_N)" in out and "the connector is not on this netlist" in out, out[-900:]
    finally:
        restore()


def t_a_declared_external_pin_no_review_holds_is_inconclusive():
    """Growth is reconciled too: the declaration's external pins are EXACTLY the reviewed ones, so a new external
    entry, one believed on its off_board text above all, waits for the review that judges it."""
    restore = _with_ports("d", _EXT + [{"ref": "J_N", "off_board": "an arrestor in the wall", "why": "a new antenna conductor to the wall"}])
    try:
        d = tempfile.mkdtemp(prefix="port-rev-grew-")
        comps = dict(_COMPS, J_N="SMA"); nets = dict(_NETS, RF=[("J_N", "1"), ("U2", "30")])
        rc, out = _run(_net(d, comps, nets), d, reviewed=_reviewed(_REV_XY))
        assert rc == 3 and "NOT REVIEWED J_N.1 on RF: declared off board and in no reviewed set" in out, out[-900:]
    finally:
        restore()


def t_a_board_that_declares_external_ports_and_has_no_reviewed_set_is_inconclusive():
    restore = _with_ports("d", _EXT)
    try:
        d = tempfile.mkdtemp(prefix="port-rev-none-")
        rc, out = _run(_net(d, _COMPS, _NETS), d, reviewed=None)
        assert rc == 3 and "NOT REVIEWED board D: it declares 2 external port(s) and no reviewed set holds them" in out, out[-900:]
    finally:
        restore()


def t_a_declared_zero_while_the_review_holds_pins_is_not_a_pass():
    """The largest reclassification: every external entry gone and the zero given its reason. Without the reviewed
    set that reads PASS; with it, INCONCLUSIVE naming the pins."""
    restore = _with_ports("d", [], why="every conductor of this board ends inside the sealed case, the reason written here")
    try:
        d = tempfile.mkdtemp(prefix="port-rev-zero-")
        rc, out = _run(_net(d, _COMPS, _NETS), d, reviewed=_reviewed(_REV_XY))
        assert rc == 3 and "REVIEWED J_X.1 on SIG" in out and _verdict_of(d)["verdict"] == "INCONCLUSIVE", out[-900:]
        # and a declared zero with no record for the board is read as before
        rc, out = _run(_net(d, _COMPS, _NETS), d, reviewed=None)
        assert rc == 0, out[-600:]
    finally:
        restore()


def t_a_reviewed_set_without_explicit_pins_or_without_its_review_is_no_record():
    restore = _with_ports("d", _EXT)
    try:
        for rec, word in ((_reviewed({"J_X": {}, "J_Y": {"2": "USB_N", "3": "USB_P"}}), "with no explicit pins"),
                          (_reviewed(_REV_XY, review="v2/docs/reviews/NO-SUCH-REVIEW.md"), "which is not in this tree"),
                          (_reviewed(_REV_XY, why="reviewed"), "no reason of 40 characters")):
            d = tempfile.mkdtemp(prefix="port-rev-shape-")
            rc, out = _run(_net(d, _COMPS, _NETS), d, reviewed=rec)
            assert rc == 3 and word in out, (word, out[-900:])
    finally:
        restore()


def t_the_committed_reviewed_sets_are_explicit_and_rest_on_a_review_in_the_tree():
    """The tree's own file: every record has the shape the tool demands, and the three boards of the review of
    decision 31 hold the pins that review enumerated (22, 8 and 5 pins on 18, 4 and 3 connectors)."""
    boards, problems = port_protect.reviews()
    assert not problems, problems
    for letter, rec in boards.items():
        assert not port_protect._record_shape(letter, rec), port_protect._record_shape(letter, rec)
    for letter, n_ref, n_pin in (("a", 18, 22), ("d", 4, 8), ("e", 3, 5)):
        ext = boards[letter]["external"]
        assert len(ext) == n_ref and sum(len(v) for v in ext.values()) == n_pin, (letter, len(ext), sum(len(v) for v in ext.values()))
        assert boards[letter]["review"] == REVIEW_DOC and boards[letter]["netlist_sha256_16"]
