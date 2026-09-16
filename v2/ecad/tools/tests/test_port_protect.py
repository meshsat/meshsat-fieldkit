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


def _with_ports(letter, ports, why=None):
    """Set a board's declaration for the length of one test. `why` None REMOVES the reason, because since
    16 September an empty list WITH a reason is an answer and an empty list without one is not, and a fixture
    that leaves the board's own reason in place is testing the other case."""
    p = os.path.join(TOOLS, "boards", "%s.json" % letter)
    original = open(p, encoding="utf-8").read()
    d = json.loads(original); d["external_ports"] = ports
    if why is None: d.pop("_external_ports_why", None)
    else: d["_external_ports_why"] = why
    json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return lambda: open(p, "w", encoding="utf-8").write(original)


def _run(p, cwd):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "port_protect.py"), p], cwd=cwd,
                       capture_output=True, text=True, timeout=120)
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
    i = src.index('_v.write("port_protect", _v.FAIL if bad else _v.PASS')
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
