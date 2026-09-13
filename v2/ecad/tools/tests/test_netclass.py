#!/usr/bin/env python3
"""Which class a net is in, answered in ONE place (MESHSAT-862, 13 September 2026).

KiCad 9 writes `net_settings.netclass_assignments` as a map from net name to a LIST of class names. Five tools
read that map and they did not agree about it, which is the shape of defect this repository keeps meeting: one
representation, several readers, each with its own copy of the expression.

  - `straighten.py` used the value as a dict KEY and raised `TypeError: unhashable type: 'list'`. Board C10's
    quality pass reports "straighten+via_merge FAILED" and "straighten only FAILED" and accepted via_merge
    alone, so the straighten stage has never run on that board.
  - `stub_router.py` compared the value with a class NAME, which a list never equals, so the class lookup found
    nothing and the default track width and via size were kept in SILENCE for every net of every board whose
    project carries assignments. That is the worse half: a crash reports itself.
  - the other three each carried the same three-line expression with the same comment, written three times.

These rules hold the one answer in place: the function's behaviour on every value shape a project file can
carry, and the requirement that no tool reads the map its own way again.
"""
import os, re, sys, glob, json

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import netclass


def t_a_list_valued_assignment_yields_its_first_class():
    a = {"/+3V3": ["RAIL"], "/USB_DM_R": ["USB", "PWR"]}
    assert netclass.class_of(a, "/+3V3") == "RAIL"
    assert netclass.class_of(a, "/USB_DM_R") == "USB"


def t_the_leading_slash_is_tried_both_ways():
    """A root-sheet label is `/NAME` in the board and project files of different ages carry both forms."""
    assert netclass.class_of({"/+3V3": ["RAIL"]}, "+3V3") == "RAIL"
    assert netclass.class_of({"+3V3": ["RAIL"]}, "/+3V3") == "RAIL"


def t_a_string_assignment_still_works_and_nothing_else_becomes_a_class():
    assert netclass.class_of({"N": "PWR"}, "N") == "PWR"
    for v in ([], "", None, 5, {}):
        assert netclass.class_of({"N": v}, "N", "Default") == "Default", v
    assert netclass.class_of(None, "N", "Default") == "Default"
    assert netclass.class_of({}, "N") is None
    assert netclass.class_of({"N": ["RAIL"]}, "") is None


def t_the_list_form_of_a_real_project_file_resolves():
    """The tree's own project files, not a fixture: this is the format the tools actually meet."""
    seen = 0
    for pro in glob.glob(os.path.join(os.path.dirname(TOOLS), "pcb-*", "*.kicad_pro")):
        ns = (json.load(open(pro)).get("net_settings") or {})
        a = ns.get("netclass_assignments") or {}
        if not a: continue
        names = netclass.classes_by_name(ns)
        for net in a:
            c = netclass.class_of(a, net)
            assert c, "%s: %s resolves to no class" % (os.path.basename(pro), net)
            assert c in names or c == "Default", \
                "%s: %s resolves to %r, which is not one of the project's classes %s" % (os.path.basename(pro), net, c, sorted(names))
            seen += 1
    assert seen, "no project file in the tree carries netclass_assignments, so this rule judged nothing"


def t_no_tool_carries_its_own_copy_of_the_lookup():
    """The fingerprint of a private copy is the name lookup, not the read.

    Fetching the map into a variable is ordinary work. What must not be duplicated is the DECISION: trying the
    net name with and without its leading slash and then unwrapping a list. Three files carried that expression
    with the same comment, a fourth crashed on the list and a fifth quietly ignored it. This rule forbids the
    fingerprint anywhere but in the one answer.
    """
    offenders = []
    for f in sorted(glob.glob(os.path.join(TOOLS, "*.py"))):
        b = os.path.basename(f)
        if b == "netclass.py": continue
        src = open(f).read()
        if "netclass_assignments" not in src: continue
        for n, line in enumerate(src.split("\n"), 1):
            if line.lstrip().startswith("#"): continue
            if ('lstrip("/")' in line and re.search(r'\b_?assign\w*\.get\(', line) and "class_of" not in line):
                offenders.append("%s:%d %s" % (b, n, line.strip()[:100]))
            if "isinstance(" in line and "list" in line and ("assign" in line or "netclass_assignments" in line):
                offenders.append("%s:%d %s" % (b, n, line.strip()[:100]))
            # The second straighten site was found by RUNNING the fixed tool, not by this rule: the first
            # patch fixed the dict-key use and left `if _c in _pairc`, the same list against a set, four
            # lines below. So the map itself is off limits: the only way to a class name is class_of, and
            # the value is normalised once where it is fetched.
            if re.search(r'\b_?assign\w*\.get\(', line) and "class_of" not in line:
                offenders.append("%s:%d reads the assignment map directly: %s" % (b, n, line.strip()[:90]))
    assert not offenders, ("these carry their own copy of the class lookup instead of calling netclass.class_of:\n  "
                          + "\n  ".join(offenders))


def t_every_reader_imports_the_one_answer():
    for b in ("straighten.py", "stub_router.py", "impedance_check.py", "intent_checks.py", "pair_preroute.py"):
        src = open(os.path.join(TOOLS, b)).read()
        assert "netclass_assignments" in src, "%s no longer reads the map; drop it from this rule" % b
        assert re.search(r'^import netclass$|^import .*\bnetclass\b', src, re.M), \
            "%s reads netclass_assignments and does not import the one answer" % b
        assert "netclass.class_of(" in src, "%s imports it and does not use it" % b


def t_the_project_file_lookup_is_not_inside_the_try_it_is_the_fallback_for():
    """13 September 2026, and this is the defect that hid the netclass one for a week.

    `stub_router.py` reads the net's class twice: from pcbnew, and from the project file. The second was
    written on 7 September precisely because the first does not work (`netobj.GetNetClass()` returns a bare
    SwigPyObject on KiCad 9 and `GetTrackWidth()` on it raises AttributeError) and it was nested INSIDE the
    same `try` as the first, AFTER the raising statement. So the exception jumped past it every time and the
    fallback never ran on any board. Every stub closure since has been laid at the default 0.25 mm with a
    0.6/0.3 via whatever the net's class asked for, which on board C is half the width of a RAIL net.

    **A fallback inside the try of the thing it is a fallback for is not a fallback.** The rule reads the
    file's syntax tree rather than its text: the two lookups must be separate statements.
    """
    import ast
    src = open(os.path.join(TOOLS, "stub_router.py")).read()
    tree = ast.parse(src)

    def calls(node, name):
        return any(isinstance(n, ast.Attribute) and n.attr == name for n in ast.walk(node))

    def reads_project(node):
        return any(isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value == ".kicad_pro"
                   for n in ast.walk(node))

    bad = []
    for t in (n for n in ast.walk(tree) if isinstance(n, ast.Try)):
        if not calls(t, "GetNetClass"): continue
        for stmt in t.body:
            if reads_project(stmt) or any(isinstance(n, ast.Try) and reads_project(n) for n in ast.walk(stmt)):
                bad.append("line %d" % getattr(t, "lineno", 0))
    assert not bad, ("the project-file class lookup sits inside the try that guards the pcbnew one, so it is "
                     "skipped whenever pcbnew raises, which on KiCad 9 is always (%s)" % ", ".join(bad))


def t_a_stub_closure_says_what_width_it_is_laid_at():
    """0.25 mm on a 0.5 mm class survived a week because the number was never printed."""
    src = open(os.path.join(TOOLS, "stub_router.py")).read()
    assert re.search(r'print\([^)]*track [^)]*mm', src), \
        "stub_router does not report the track width of the closure it lays"
