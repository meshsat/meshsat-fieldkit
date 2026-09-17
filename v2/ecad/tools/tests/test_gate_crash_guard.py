#!/usr/bin/env python3
"""A gate that crashes writes INCONCLUSIVE, and every impedance row has the shape the loop unpacks (18 September 2026).

`impedance_check.py` built one row with ten fields where the others carry eleven, so the first board with a pair
one of whose legs had no copper (B21, 416 open) crashed it at the unpack three lines from its writer; nothing was
written, and PAIR-001 and STK-001 read "no impedance_check verdict for this board" through two sweeps. Two rules:
every `results.append` in that gate carries eleven fields, and the gate's entry point runs under `verdict.guard`,
which turns an exception into an INCONCLUSIVE verdict naming it."""
import ast, os, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)


def t_every_impedance_row_has_the_eleven_fields_the_loop_unpacks():
    src = open(os.path.join(TOOLS, "impedance_check.py"), encoding="utf-8").read()
    tree = ast.parse(src); n = 0; bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "append" \
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "results":
            n += 1
            arg = node.args[0] if node.args else None
            if not isinstance(arg, ast.Tuple) or len(arg.elts) != 11: bad.append("line %d: %s fields" % (node.lineno, len(arg.elts) if isinstance(arg, ast.Tuple) else "?"))
    assert n >= 3, "the results rows are not where this rule expected them"
    assert not bad, "impedance rows that the loop cannot unpack: %s" % bad


def t_the_impedance_gate_runs_under_the_crash_guard():
    src = open(os.path.join(TOOLS, "impedance_check.py"), encoding="utf-8").read()
    assert 'guard("impedance_check", main' in src, "impedance_check's entry point is not guarded: a crash leaves no verdict"


def t_the_guard_writes_inconclusive_for_a_crash_and_passes_a_return_through():
    import tempfile, json
    import verdict
    d = tempfile.mkdtemp(prefix="guard-"); os.makedirs(os.path.join(d, "out")); cwd = os.getcwd(); os.chdir(d)
    try:
        def boom(a): raise ValueError("ten of eleven")
        rc = verdict.guard("guard_fixture", boom, ["x.kicad_pcb"], rules=None)
        v = json.load(open(os.path.join(d, "out", "guard_fixture.verdict.json")))
        assert rc == 3 and v["verdict"] == "INCONCLUSIVE" and "ValueError" in v.get("note", ""), (rc, v)
        assert verdict.guard("guard_fixture", lambda a: 0, ["x.kicad_pcb"]) == 0
    finally:
        os.chdir(cwd)
