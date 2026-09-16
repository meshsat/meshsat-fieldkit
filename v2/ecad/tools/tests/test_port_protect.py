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


def _with_ports(letter, ports):
    p = os.path.join(TOOLS, "boards", "%s.json" % letter)
    original = open(p, encoding="utf-8").read()
    d = json.loads(original); d["external_ports"] = ports
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
    restore = _with_ports("d", [])
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
