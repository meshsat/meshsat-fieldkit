#!/usr/bin/env python3
"""ANA-001's third report: can a fence reach the copper that breaks the rule? (21 September 2026)

The defect these are written against is a reading that cannot be acted on. `sensitive_nodes` names one
clearance per declared node and says nothing about WHO LAID the copper on either side, while `sense_fence`,
this rule's only instrument that reaches the router, can move only copper the ROUTER laid and can be grown
only around sense copper the PRE-LAY LOCKED. Twice in one morning that gap decided the next arm: on board E
every offending pair has a router-laid aggressor and locked sense copper, so its fence arm was a real
measurement; on board A the tightest rows are nets the pre-lay never touched, so a fence there protects the
rows that were already widest and the answer is a different pre-lay group.

The board-shaped rules drive a FAKE BOARD of six methods rather than pcbnew, the `test_rail_crossings`
pattern, so they run where KiCad is not; putting a stub in `sys.modules` is what this project forbids after a
stub made three rules run against it (19 September 2026)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)

import sense_reach as sr                                              # noqa: E402

MM = 1e6


class _T:
    """One track, in the six methods `segments()` asks of it."""

    def __init__(self, net, layer, x1, y1, x2, y2, w=0.25, locked=False):
        self._n, self._l, self._w, self._lk = net, layer, w, locked
        self._a, self._b = (x1, y1), (x2, y2)

    class _P:
        def __init__(self, x, y): self.x, self.y = int(x * MM), int(y * MM)

    def GetClass(self): return "PCB_TRACK"
    def GetNetname(self): return self._n
    def GetLayer(self): return self._l
    def IsLocked(self): return self._lk
    def GetWidth(self): return int(self._w * MM)
    def GetLength(self): return int(((self._a[0] - self._b[0]) ** 2 + (self._a[1] - self._b[1]) ** 2) ** 0.5 * MM)
    def GetStart(self): return _T._P(*self._a)
    def GetEnd(self): return _T._P(*self._b)


class _B:
    def __init__(self, tracks): self._t = tracks
    def GetTracks(self): return self._t
    def GetLayerName(self, l): return {0: "F.Cu", 31: "B.Cu"}.get(l, "In%d.Cu" % l)


def t_the_gap_is_edge_to_edge_and_not_centre_to_centre():
    """A clearance is between COPPER edges. Two 0.25 mm tracks 0.5 mm apart on their centrelines have a
    quarter of a millimetre of laminate between them, and a tool that reported 0.5 would pass a board the
    DRC refuses."""
    a = {"a": (0.0, 0.0), "b": (10.0, 0.0), "w": 0.25}
    b = {"a": (0.0, 0.5), "b": (10.0, 0.5), "w": 0.25}
    assert abs(sr.gap(a, b) - 0.25) < 1e-9, sr.gap(a, b)


def t_two_segments_on_different_layers_are_never_compared():
    """THE DEFECTIVE FIXTURE: the same two runs, once on one layer and once on two.

    An overlap through the dielectric is coupling and not clearance; `sensitive_nodes` says so in its own
    note and sets no number for it, and neither does this. A tool that counted it would report a violation
    the board's own rule does not have."""
    same = _B([_T("/CSP", 0, 0, 0, 10, 0), _T("/SW1", 0, 0, 0.3, 10, 0.3)])
    rs, _, _ = sr.rows(same, ["CSP"], ["SW1"], 0.50)
    assert len(rs) == 1, "two runs 0.05 mm apart on ONE layer are a pair: %s" % rs
    split = _B([_T("/CSP", 0, 0, 0, 10, 0), _T("/SW1", 31, 0, 0.3, 10, 0.3)])
    rs2, _, _ = sr.rows(split, ["CSP"], ["SW1"], 0.50)
    assert rs2 == [], "segments on different layers were compared as a clearance: %s" % rs2


def t_each_side_carries_who_laid_it_because_that_is_what_the_fence_can_move():
    """THE PROPERTY THE REPORT EXISTS FOR. A fence drawn after the pre-lay moves ROUTER copper; against a
    locked aggressor it can do nothing, and the reading would look like the fence failing when it was never
    able to answer."""
    b = _B([_T("/CSP", 0, 0, 0, 10, 0, locked=True), _T("/SW1", 0, 0, 0.3, 10, 0.3, locked=True)])
    rs, _, _ = sr.rows(b, ["CSP"], ["SW1"], 0.50)
    assert rs and rs[0]["switch_locked"] is True and rs[0]["sense_locked"] is True, rs
    b2 = _B([_T("/CSP", 0, 0, 0, 10, 0, locked=True), _T("/SW1", 0, 0, 0.3, 10, 0.3)])
    rs2, _, _ = sr.rows(b2, ["CSP"], ["SW1"], 0.50)
    assert rs2[0]["switch_locked"] is False and rs2[0]["sense_locked"] is True, rs2


def t_a_net_with_no_locked_sense_copper_is_named_as_one_the_fence_cannot_be_grown_from():
    """Board A's whole finding in one fixture: the tightest net is the one the pre-lay never touched."""
    b = _B([_T("/ISNS_P", 0, 0, 0, 10, 0),                    # router laid, so no fence can grow here
            _T("/CSF", 0, 0, 5, 10, 5, locked=True),          # pre-laid, so a fence can
            _T("/SW1", 0, 0, 0.3, 10, 0.3),
            _T("/SW1", 0, 0, 5.35, 10, 5.35)])
    rs, _, _ = sr.rows(b, ["ISNS_P", "CSF"], ["SW1"], 0.50)
    per = sr.summarise(rs, {"SW1"})
    assert per["ISNS_P"]["locked"] == 0, per
    assert per["CSF"]["locked"] >= 1, per
    assert per["ISNS_P"]["tightest"] < per["CSF"]["tightest"], per


def t_an_aggressor_the_declaration_does_not_carry_is_counted_apart():
    """The gate-drive half. ANA-001 measures against the DECLARED switching nets; on board E the tightest
    approach of all is a gate drive the declaration excludes by pin function. The report may measure it and
    must never silently fold it into the declared count."""
    b = _B([_T("/CSN", 0, 0, 0, 10, 0, locked=True),
            _T("/TG2", 0, 0, 0.3, 10, 0.3),
            _T("/SW2", 0, 0, 0.45, 10, 0.45)])
    rs, _, _ = sr.rows(b, ["CSN"], ["TG2", "SW2"], 0.50)
    per = sr.summarise(rs, {"SW2"})
    assert per["CSN"]["pairs"] == 2, rs
    assert per["CSN"]["undeclared_aggressor"] == 1, per


def t_it_is_a_report_and_never_decides_ana001():
    """A report that wrote a deciding verdict would be asserting the judgement it exists to put to someone
    else, which is via_current's advisory rule of 16 September in another place."""
    src = open(os.path.join(TOOLS, "sense_reach.py"), encoding="utf-8").read()
    assert "advisory=True" in src, "the verdict is not advisory, so this report can decide a rule"
    cov = open(os.path.join(TOOLS, "pcb_rules_coverage.yaml"), encoding="utf-8").read()
    i = cov.find("ANA-001:")
    assert i > 0, "ANA-001 is not in the coverage map any more"
    blk = cov[i:cov.find("\n\n", i)]
    assert "sense_reach.py" in blk, "the coverage map does not name this report under ANA-001"
    assert "sensitive_nodes.py" in blk and "tool: sensitive_nodes.py" in blk, \
        "ANA-001 is no longer decided by sensitive_nodes, which this report must not replace"


def t_two_segments_that_cross_are_not_reported_as_having_daylight():
    """THE DEFECT, found by checking the arithmetic against a brute-force sweep rather than trusting it
    (21 September 2026).

    For two segments that do NOT cross, the closest approach is always at an endpoint of one of them, so
    sampling the four endpoints is exact; over forty random pairs the worst difference from a sweep was
    0.034 mm, which is the sweep's own grid. For two that DO cross it is not exact at all: every endpoint can
    be far from the other segment while the middles meet, and the sweep read up to 2.70 mm of daylight where
    there is none. On these boards that case is a hard DRC violation and the boards this has run on read
    hard 0, so it has never occurred; a report that answers wrongly in a case it cannot meet is still a
    report that answers wrongly."""
    import ast
    import math
    src = open(os.path.join(TOOLS, "sense_reach.py"), encoding="utf-8").read()
    fn = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "gap"]
    assert fn, "sense_reach no longer carries gap"
    ns = {"math": math}
    exec(compile(ast.Module(body=fn, type_ignores=[]), "sense_reach.py", "exec"), ns)
    gap = ns["gap"]
    # an X: every endpoint is 7 mm from the other segment's endpoints, and the middles meet at the centre
    a = {"a": (0.0, 0.0), "b": (10.0, 10.0), "w": 0.25}
    b = {"a": (0.0, 10.0), "b": (10.0, 0.0), "w": 0.25}
    assert gap(a, b) <= 0.0, "two segments that cross were reported with daylight between them: %.3f" % gap(a, b)
    # and the acceptable fixture: two that do not cross keep their real clearance
    c = {"a": (0.0, 0.0), "b": (10.0, 0.0), "w": 0.25}
    d = {"a": (0.0, 0.6), "b": (10.0, 0.6), "w": 0.25}
    assert abs(gap(c, d) - 0.35) < 1e-9, gap(c, d)


def t_a_run_that_was_never_told_what_to_measure_is_not_a_pass():
    """THE DEFECT, found by running the tool on A98's frozen board and forgetting `--board`
    (21 September 2026).

    With no board letter and no explicit `--sense` list the tool measured NOTHING and wrote
    `sense_reach PASS of 0`, in the same words a real run prints when a board has no pair inside its
    clearance. An armed reader that drops the flag therefore logs a reassuring line and the reading looks
    taken; it is STK-001's `PASS on a denominator of zero` of 19 September in a third place, and the
    project's own answer to it is that a DECLARED zero is a pass with its reason while an undeclared zero
    is INCONCLUSIVE.

    The defective fixture is that run: nothing named on either side. The acceptable one is the same call
    with a subject, which must stay a pass."""
    assert hasattr(sr, "subject_missing"), \
        "sense_reach answers 'was I told what to measure' nowhere, so a run with no subject reads PASS of 0"
    assert sr.subject_missing(None, []), \
        "a run with no board letter and no --sense list reported nothing missing"
    assert sr.subject_missing("a", []), \
        "a board whose declaration carries no sensitive node reported nothing missing"
    assert sr.subject_missing(None, ["TRK_CSP"]) is None, \
        "a run given its nets on the command line was refused"
    assert sr.subject_missing("e", ["TRK_CSP"]) is None, \
        "a board that declares its nodes was refused"
    src = open(os.path.join(TOOLS, "sense_reach.py"), encoding="utf-8").read()
    assert "missing = subject_missing(" in src, \
        "main() does not take its missing_input from that one answer"
