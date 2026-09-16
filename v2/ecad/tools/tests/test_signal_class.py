#!/usr/bin/env python3
"""The signal classifier, and the four things that stop it becoming a way to wave a net through
(rule RET-001, MESHSAT-862, 16 September 2026).

This file exists because the change it tests RELAXES a gate. "A plane under every signal" was a heuristic
running as a law and it refused board E for an opto inhibit, a water sensor and an LDO output; the fix is to
ask each net the question its spectral content deserves. A fix of that shape is one wrong step from an
exemption mechanism, so each of these rules holds one of the properties that keeps it honest:

  * a declaration without a reason is refused;
  * a net nobody classified is judged at the STRICTEST bar, so an omission costs a failure and never buys a pass;
  * a declaration cannot downgrade a net the BOARD ITSELF says carries an impedance target;
  * the relaxed class asks a DIFFERENT QUESTION (does a return path exist) rather than a looser version of the
    same number, so loosening it cannot silently loosen the fast classes.
"""
import os, sys, json, tempfile, shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import signal_class as S


class _Net:
    def __init__(self, n): self._n = n
    def GetNetname(self): return self._n


class _NI:
    def __init__(self, names): self._n = list(names)
    def GetNetCount(self): return len(self._n)
    def GetNetItem(self, i): return _Net(self._n[i])


class _Board:
    def __init__(self, names, path="/tmp/anywhere/pcb-e1-dock.kicad_pcb"):   # the STEM is what names the board
        self._ni = _NI(names); self._p = path
    def GetNetInfo(self): return self._ni
    def GetFileName(self): return self._p


def _with_declarations(letter, rows):
    """Write a board table with the given signal_classes and give back a restore function."""
    p = os.path.join(TOOLS, "boards", "%s.json" % letter)
    original = open(p, encoding="utf-8").read() if os.path.exists(p) else None
    d = json.loads(original) if original else {}
    d["signal_classes"] = rows
    json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    def restore():
        if original is None: os.remove(p)
        else: open(p, "w", encoding="utf-8").write(original)
    return restore


def t_a_declaration_without_a_reason_is_refused():
    """An exemption nobody can audit is how the four never-auto floors of 12 September came to have holes in
    them. A class entry must say WHY the net has that spectral content, naming the part or the interface."""
    restore = _with_declarations("e", [
        {"pattern": "FOO_*", "class": "LOW_SPEED_OR_DC", "basis": ""},
        {"pattern": "BAR_*", "class": "LOW_SPEED_OR_DC", "basis": "slow"},
        {"pattern": "BAZ_*", "class": "NOT_A_CLASS", "basis": "a long enough sentence to pass the length test"},
        {"pattern": "QUX_*", "class": "UNKNOWN", "basis": "a long enough sentence to pass the length test"},
    ])
    try:
        good, bad = S.declarations("e")
        assert not good, "an entry with no basis was accepted: %s" % good
        assert len(bad) == 4, bad
        assert any("no basis" in x for x in bad) and any("not one of" in x for x in bad), bad
        assert any("UNKNOWN cannot be declared" in x for x in bad), \
            "UNKNOWN was accepted as a declaration, which would let a board declare its way out of the question"
    finally:
        restore()


def t_an_unclassified_net_is_judged_at_the_strictest_bar_not_waved_through():
    """The whole design of the classifier: absence is not permission. A net matched by nothing comes back
    UNKNOWN, the gate names it, and it is measured against the tightest tolerance in the table."""
    restore = _with_declarations("e", [
        {"pattern": "SLOW_*", "class": "LOW_SPEED_OR_DC", "basis": "a divider tap into an ADC, filtered"}])
    try:
        m, bad = S.classify(_Board(["/SLOW_A", "/MYSTERY"]), "/tmp/anywhere/pcb-e1-dock.kicad_pcb")
        assert not bad, bad
        assert m["/SLOW_A"][0] == "LOW_SPEED_OR_DC"
        assert m["/MYSTERY"][0] == "UNKNOWN", m["/MYSTERY"]
        assert S.QUESTION["UNKNOWN"] == "UNDECIDED"
        # and the strictest bar in the table is the one an undeclared net is held to by intent_checks
        src = open(os.path.join(TOOLS, "intent_checks.py")).read()
        assert "UNDECLARED so judged at the strictest bar" in src, \
            "intent_checks no longer holds an undeclared net to the strict criterion"
    finally:
        restore()


def t_a_declaration_cannot_downgrade_a_net_the_board_itself_calls_controlled_impedance():
    """The board's own net class is evidence and a declaration is a claim. Where they disagree the board wins,
    so no entry in a JSON file can take an impedance-targeted pair out of the strict criterion."""
    restore = _with_declarations("e", [
        {"pattern": "USB_*", "class": "LOW_SPEED_OR_DC", "basis": "an attempt to relax a pair that must not work"}])
    try:
        m, _bad = S.classify(_Board(["/USB_E6_P"]), "/tmp/anywhere/pcb-e1-dock.kicad_pcb",
                             targets={"USB"}, cls_of=lambda n: "USB")
        assert m["/USB_E6_P"][0] == "CONTROLLED_IMPEDANCE", \
            "a declaration downgraded a net the board's own class calls impedance-targeted: %s" % (m["/USB_E6_P"],)
    finally:
        restore()


def t_the_relaxed_class_asks_a_different_question_and_still_refuses_a_net_with_no_reference():
    """LOW_SPEED_OR_DC is not a bigger number, it is another question: does a return path EXIST. A net with no
    reference under any of its copper has a loop the size of the board whatever its speed, and still fails."""
    assert S.QUESTION["LOW_SPEED_OR_DC"] == "EXISTS"
    assert S.limit("LOW_SPEED_OR_DC", 500.0) is None, "the slow class has a length tolerance, so it is the same question after all"
    assert S.limit("CONTROLLED_IMPEDANCE", 100.0) == 10.0
    assert S.limit("CONTROLLED_IMPEDANCE", 1000.0) == 50.0, "the fraction no longer applies to a long net"
    assert S.limit("CLOCKED_DIGITAL", 100.0) > S.limit("CONTROLLED_IMPEDANCE", 100.0), \
        "a clocked bus is held to the same bar as a controlled-impedance pair, which was the defect"
    src = open(os.path.join(TOOLS, "intent_checks.py")).read()
    assert "a reference exists under" in src, "the EXISTS question is not implemented in the gate"
    assert "covered > 0" in src, "the EXISTS question does not refuse a net with no reference at all"


def t_the_committed_declarations_carry_a_basis_each():
    """Every board's own table, as it stands in the tree."""
    import glob
    bad = []
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        letter = os.path.splitext(os.path.basename(p))[0]
        good, errs = S.declarations(letter)
        bad += ["%s: %s" % (letter, e) for e in errs]
    assert not bad, "signal class declarations that are not usable: %s" % bad


def t_the_board_letter_comes_from_the_board_table_and_not_the_directory():
    """Found by running the gate sweep, 16 September 2026.

    The first version read the phase directory's name. The sweep runs every gate in a COPY of the project under
    out/sweep/, so the directory was called "sweep", no declarations were found, all 76 of board E's signal nets
    came out UNKNOWN and were judged at the strictest bar, and the gate reported 54 failures on a board with
    ten. A tool must learn which board it has from the board table, which is the one place that says so, and not
    from where the file happens to be sitting: this project has the same rule for how a tool picks a board at
    all (test_driver_hygiene), for the same reason.
    """
    assert S.board_letter("/root/sw_e/v2/ecad/pcb-e1-dock-e7/out/sweep/pcb-e1-dock.kicad_pcb") == "e"
    assert S.board_letter("/tmp/anywhere/at/all/pcb-b-compute.kicad_pcb") == "b"
    assert S.board_letter("/x/pcb-p-pack.kicad_pcb") == "p"
    assert S.board_letter("/x/not-a-board-of-this-project.kicad_pcb") == "", \
        "a file this project does not know came back with a letter, so some board's declarations would be applied to it"
    src = open(os.path.join(TOOLS, "signal_class.py")).read()
    assert "os.path.dirname(os.path.abspath(path))" not in src, \
        "the letter is being read from the directory again"


def t_the_return_via_screen_reads_the_same_class_as_the_return_path_rule():
    """RET-004. The owner's instruction names "a ground via beside every signal via" as a heuristic that must
    not become a law, and the governing principle is the same one rule 1 answers: a return via exists so the
    return current can follow its signal through a reference change. Where the signal has no edge worth
    speaking of there is no loop worth closing, and demanding one anyway refuses boards for nothing.

    Board D was one item from a clean gate on fifteen vias, and every one of them is a push-to-talk line or an
    expander output that changes state when a person presses a switch.

    Two properties: the screen reads the SAME declaration rule 1 reads, so a net cannot be slow for one rule
    and fast for the other; and a net nobody classified is judged as though it were fast.
    """
    src = open(os.path.join(TOOLS, "return_via.py")).read()
    assert "import signal_class" in src, "the return-via screen does not read the signal classification"
    assert 'LOW_SPEED_OR_DC' in src, "the screen does not exempt the slow class"
    assert '"UNKNOWN"' in src or "'UNKNOWN'" in src, \
        "an unclassified net is not defaulted, so it could fall into the slow branch"
    # the exemption is a COUNTED category and not a silent skip: the count travels in the verdict
    assert '"slow"' in src, "the slow vias are skipped without being counted, so nobody can see how many"
    import re
    assert re.search(r'counts=\{[^}]*"slow"', src), "the verdict does not carry the slow count"


def t_no_declaration_contradicts_its_own_basis():
    """A class is what the spectral content IS, and the basis is where that content is written down.

    Board E declared `FAN?_TACH` as CLOCKED_DIGITAL with the basis "under a kilohertz with a slow edge", which
    is the definition of the slow class in the same table. The rule was found by reading the five vias the
    return-via fixer could not place on board E: four are real (a bootstrap node, two gate drives and a USB
    line, all with edges), and the fifth was a declaration arguing with itself. A declaration that says one
    thing in its class and another in its reason is worse than no declaration, because it reads as considered."""
    import json, os, re, glob
    tools = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    slow = re.compile(r"under a kilohertz|a few hertz|slow edge|held static|changes once", re.I)
    bad = []
    for f in sorted(glob.glob(os.path.join(tools, "boards", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        for e in (d.get("signal_classes") or []):
            if e.get("class") != "LOW_SPEED_OR_DC" and slow.search(e.get("basis", "")) \
               and "contradicted" not in e.get("basis", ""):
                bad.append("%s: %s is %s but its basis says %r" %
                           (os.path.basename(f), e["pattern"], e["class"], e["basis"][:70]))
    assert not bad, "; ".join(bad)
