#!/usr/bin/env python3
"""A line whose assertion inhibits a hazard holds the safe state on its own (rule SCH-004, MESHSAT-862,
17 September 2026).

The rule had no implementation at all and the project was enforcing part of it by hand, in fifteen lines of
`check_contracts` that know only about the EMCON net. Every rule here is run against a netlist built for it,
and each defective fixture is a shape this kit has actually had: a consumer with no pull of its own (board B's
TX_INHIBIT_n before the 9 September red team), a line declared as merely passing through while a part reads it,
and a source that drives nothing.
"""
import os, sys, json, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import safe_lines


def _net(d, comps, nets, stem="pcb-d-aprs"):
    os.makedirs(d, exist_ok=True)
    c = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v in sorted(comps.items()))
    n = ""
    for i, (name, nodes) in enumerate(sorted(nets.items()), 1):
        body = "".join('      (node (ref "%s") (pin "%s"))\n' % (r, p) for r, p in nodes)
        n += '    (net (code %d) (name "/%s")\n%s    )\n' % (i, name, body)
    p = os.path.join(d, stem + ".net")
    open(p, "w").write("(export (version E)\n  (components\n%s  )\n  (nets\n%s  )\n)\n" % (c, n))
    return p


def _with_lines(letter, lines, why=None):
    p = os.path.join(TOOLS, "boards", "%s.json" % letter)
    original = open(p, encoding="utf-8").read()
    d = json.loads(original); d["safety_lines"] = lines
    if why is None: d.pop("_safety_lines_why", None)
    else: d["_safety_lines_why"] = why
    json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return lambda: open(p, "w", encoding="utf-8").write(original)


def _run(p, cwd):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "safe_lines.py"), p], cwd=cwd,
                       capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr


def t_a_consumer_with_no_pull_of_its_own_is_refused():
    """The defect this rule exists for: the board reads the inhibit and holds nothing, so with the ribbon out
    the line floats and the transmitter is keyed by noise."""
    restore = _with_lines("d", [{"net": "TX_INHIBIT_n", "hazard": "the amplifier is keyed", "safe_state": "low",
                                 "role": "listens", "why": "the key gate takes it"}])
    try:
        d = tempfile.mkdtemp(prefix="safe-nopull-")
        p = _net(d, {"J_H": "harness", "U12": "AND gate"},
                 {"TX_INHIBIT_n": [("J_H", "8"), ("U12", "2")], "GND": [("J_H", "3"), ("U12", "7")]})
        rc, out = _run(p, d)
        assert rc == 1, "a floating inhibit passed:\n%s" % out[-500:]
        assert '"floating": 1' in out, out[-400:]
    finally:
        restore()


def t_the_same_line_with_its_pull_down_passes():
    """The acceptable half, and it is board D as built: R2 holds the inhibit down, so a missing harness cannot
    key the transmitter."""
    restore = _with_lines("d", [{"net": "TX_INHIBIT_n", "hazard": "the amplifier is keyed", "safe_state": "low",
                                 "role": "listens", "why": "the key gate takes it and R2 holds it down"}])
    try:
        d = tempfile.mkdtemp(prefix="safe-pull-")
        p = _net(d, {"J_H": "harness", "U12": "AND gate", "R2": "100k"},
                 {"TX_INHIBIT_n": [("J_H", "8"), ("U12", "2"), ("R2", "1")],
                  "GND": [("J_H", "3"), ("U12", "7"), ("R2", "2")]})
        rc, out = _run(p, d)
        assert rc == 0, "a line held down by its own resistor was refused:\n%s" % out[-500:]
    finally:
        restore()


def t_a_line_declared_as_passing_through_while_a_part_reads_it_is_refused():
    """A declaration is not evidence. Calling a listener a pass-through would exempt exactly the board that can
    act on the line, so the netlist is asked."""
    restore = _with_lines("d", [{"net": "TX_INHIBIT_n", "hazard": "the amplifier is keyed", "safe_state": "low",
                                 "role": "carries", "why": "nothing here reads it"}])
    try:
        d = tempfile.mkdtemp(prefix="safe-carries-")
        p = _net(d, {"J_H": "harness", "U12": "AND gate"},
                 {"TX_INHIBIT_n": [("J_H", "8"), ("U12", "2")], "GND": [("J_H", "3")]})
        rc, out = _run(p, d)
        assert rc == 1, "a board that reads the line called it a pass-through and passed:\n%s" % out[-500:]
        assert "only carries" in out, out[-400:]
    finally:
        restore()


def t_a_source_that_drives_nothing_is_refused():
    restore = _with_lines("d", [{"net": "ZEROIZE_HW", "hazard": "the keys are wiped", "safe_state": "high",
                                 "role": "source", "why": "the toggle lives here"}])
    try:
        d = tempfile.mkdtemp(prefix="safe-source-")
        p = _net(d, {"J_H": "harness", "TP9": "test point"},
                 {"ZEROIZE_HW": [("J_H", "15"), ("TP9", "1")], "GND": [("J_H", "3")]})
        rc, out = _run(p, d)
        assert rc == 1, "a source with nothing driving it passed:\n%s" % out[-500:]
        assert "nothing on it does" in out, out[-400:]
    finally:
        restore()


def t_a_pull_up_to_a_rail_the_intent_names_is_a_pull_up():
    """Board A holds its kill input up with 100k to VBAT, and a rail set built from names that begin with a
    plus does not contain VBAT: the first run of this tool reported that board's kill line as floating on a
    board that holds it up through a resistor named in the same file. The rails come from the intent."""
    restore = _with_lines("d", [{"net": "KILL", "hazard": "the kit powers down", "safe_state": "high",
                                 "role": "listens", "why": "held up to the always-on rail"}])
    try:
        d = tempfile.mkdtemp(prefix="safe-rail-")
        p = _net(d, {"U1": "on off controller", "R4": "100k"},
                 {"KILL": [("U1", "8"), ("R4", "1")], "VBAT": [("R4", "2")], "GND": [("U1", "4")]})
        json.dump({"rails": {"VBAT": {"volts": 14.4}}},
                  open(p.replace(".net", "-intent.json"), "w", encoding="utf-8"))
        rc, out = _run(p, d)
        assert rc == 0, "a pull-up to a declared rail was not seen as one:\n%s" % out[-500:]
    finally:
        restore()


def t_a_declared_zero_is_an_answer_and_a_missing_declaration_is_not():
    restore = _with_lines("d", [], why="nothing on this board inhibits a hazard, and here is why")
    try:
        d = tempfile.mkdtemp(prefix="safe-zero-")
        p = _net(d, {"J_H": "harness"}, {"SIG": [("J_H", "1")]})
        rc, out = _run(p, d)
        assert rc == 0, "a declared zero with its reason did not pass:\n%s" % out[-400:]
    finally:
        restore()
    restore = _with_lines("d", [], why=None)
    try:
        d = tempfile.mkdtemp(prefix="safe-zero-nowhy-")
        p = _net(d, {"J_H": "harness"}, {"SIG": [("J_H", "1")]})
        rc, out = _run(p, d)
        assert rc == 3, "a zero with no reason passed:\n%s" % out[-400:]
    finally:
        restore()


def t_every_committed_declaration_says_what_the_hazard_is_and_why():
    import glob
    for f in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if "safety_lines" not in d: continue
        assert str(d.get("_safety_lines_why", "")).strip(), "%s declares safety lines with no reason" % os.path.basename(f)
        for e in d["safety_lines"]:
            for k in ("net", "hazard", "safe_state", "role", "why"):
                assert str(e.get(k, "")).strip(), "%s: %s has no %s" % (os.path.basename(f), e.get("net"), k)
            assert e["safe_state"] in ("low", "high"), "%s: %s" % (os.path.basename(f), e["net"])
            assert e["role"] in ("listens", "source", "carries"), "%s: %s" % (os.path.basename(f), e["net"])
