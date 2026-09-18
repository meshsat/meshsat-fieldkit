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
           "place_audit", "port_protect", "pruned_gate", "verify_deliverable", "via_audit",
           # the rest of the coverage map's deciding gates, guarded the same way on 18 September 2026
           "assembly_set", "block_contract", "closer_audit", "doc_provenance", "edge_length", "emc_sheet",
           "energy_chain", "ground_system", "interfaces", "ledger_verify", "netlist_board", "pin_map_lands",
           "power_sequence", "ref_change", "reliability", "rf_line", "sensitive_nodes", "spacing", "thermal",
           "via_current")


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


def t_hardset_is_guarded_under_the_name_its_label_makes():
    """hardset writes `hardset-<label>` because one finish makes four judgements with it, so the guard has to be
    given that name or a crash's INCONCLUSIVE lands where nothing reads it (18 September 2026: it was the last
    gate in the coverage map with no guard at all)."""
    src = open(os.path.join(TOOLS, "hardset.py"), encoding="utf-8").read()
    i = src.find('if __name__ == "__main__"')
    assert i > 0
    blk = src[i:]
    assert "verdict.guard(_vname(" in blk, "hardset's entry point is not guarded under its label's name"
    assert "--label" in blk, "the guard is given a name that does not come from the label"


def t_every_deciding_gate_in_the_coverage_map_is_guarded_one_way_or_another():
    """The list above is a list, and a list goes stale. This reads the coverage map instead: every tool it names as
    a rule's verification, whose entry point is the one-line `sys.exit(main(...))`, must be wrapped (18 September
    2026). Three gates parse their own argv before main and one writes no verdict; each is named here with why."""
    import yaml, re
    cov = yaml.safe_load(open(os.path.join(TOOLS, "pcb_rules_coverage.yaml"), encoding="utf-8"))["coverage"]
    OWN_ENTRY = {"jlc_certify.py": "its entry is a block that parses --boards before it decides",
                 "layer_judge.py": "its entry is a block, not a one-line main",
                 "safe_lines.py": "its entry is a block, not a one-line main",
                 "track_current.py": "a measurement printer: it writes no verdict"}
    bad = []
    for rid, v in cov.items():
        tool = (v.get("verification") or {}).get("tool") if isinstance(v, dict) else None
        for f in re.findall(r"([a-z_0-9]+\.py)", str(tool or "")):
            if f in OWN_ENTRY: continue
            path = os.path.join(TOOLS, f)
            if not os.path.exists(path): continue
            src = open(path, encoding="utf-8", errors="replace").read()
            i = src.find('if __name__ == "__main__"')
            if i < 0: continue
            if not re.search(r"sys\.exit\(main\(sys\.argv\[1:\]\)\)", src[i:i + 400]): continue
            if "guard(" not in src[i:i + 400] and "crash_hook" not in src[:1600]: bad.append((rid, f))
    assert not bad, "deciding gates with a one-line entry and no crash guard: %s" % sorted(set(b[1] for b in bad))
