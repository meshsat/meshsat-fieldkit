#!/usr/bin/env python3
"""A gate that crashes writes INCONCLUSIVE, and every impedance row has the shape the loop unpacks (18 September 2026).

`impedance_check.py` built one row with ten fields where the others carry eleven, so the first board with a pair
one of whose legs had no copper (B21, 416 open) crashed it at the unpack three lines from its writer; nothing was
written, and PAIR-001 and STK-001 read "no impedance_check verdict for this board" through two sweeps. Two rules:
every `results.append` in that gate carries eleven fields, and the gate's entry point runs under `verdict.guard`,
which turns an exception into an INCONCLUSIVE verdict naming it."""
import ast, json, os, sys, tempfile

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


# The gates whose entry point is a one-line main and so can be guarded at the door. The board gates
# (check_pcb_*), check_contracts, check_zone_nets and lcsc_fill run at module level, so they install
# `verdict.crash_hook` at the top of the file instead (MODULE_GUARDED); hardset writes under a label per call
# and its guard is the writer's own BaseException handling.
GUARDED = ("impedance_check", "claims_check", "class_floor", "clock_check", "dc_drop", "derate", "erc_gate", "fab_limits",
           "place_audit", "port_protect", "pruned_gate", "verify_deliverable", "via_audit")


def t_every_gate_with_a_one_line_entry_runs_under_the_crash_guard():
    bad = []
    for g in GUARDED:
        src = open(os.path.join(TOOLS, g + ".py"), encoding="utf-8").read()
        if 'guard("%s", main' % g not in src: bad.append(g)
    assert not bad, "gates whose entry point is not guarded, so a crash there leaves no verdict: %s" % bad


MODULE_GUARDED = ("check_pcb_a", "check_pcb_b", "check_pcb_c", "check_pcb_d", "check_pcb_e", "check_pcb_p",
                  "check_contracts", "check_zone_nets", "lcsc_fill")


def t_every_module_level_gate_installs_the_crash_hook_before_it_loads_anything():
    bad = []
    for g in MODULE_GUARDED:
        src = open(os.path.join(TOOLS, g + ".py"), encoding="utf-8").read()
        i = src.find('crash_hook("%s"' % g)
        if i < 0 or i > 1500: bad.append((g, i))
    assert not bad, "module-level gates without the crash hook in their first lines: %s" % bad


def t_the_crash_hook_writes_inconclusive_and_exits_3_and_leaves_a_verdict_exit_alone():
    import subprocess
    d = tempfile.mkdtemp(prefix="hook-"); os.makedirs(os.path.join(d, "out"))
    prog = ("import sys; sys.path.insert(0, %r); import verdict as v; v.crash_hook('hook_fixture', ['x.kicad_pcb'])\n"
            "raise KeyError('the board has no such net')\n") % TOOLS
    r = subprocess.run([sys.executable, "-c", prog], cwd=d, capture_output=True, text=True)
    v = json.load(open(os.path.join(d, "out", "hook_fixture.verdict.json")))
    assert r.returncode == 3 and v["verdict"] == "INCONCLUSIVE" and "KeyError" in v.get("note", ""), (r.returncode, r.stdout, r.stderr, v)
    prog2 = ("import sys; sys.path.insert(0, %r); import verdict as v; v.crash_hook('hook_fixture2', [])\n"
             "sys.exit(v.write('hook_fixture2', v.PASS, denominator=1, inputs={}, rules=None))\n") % TOOLS
    r2 = subprocess.run([sys.executable, "-c", prog2], cwd=d, capture_output=True, text=True)
    assert r2.returncode == 0, (r2.returncode, r2.stdout, r2.stderr)
