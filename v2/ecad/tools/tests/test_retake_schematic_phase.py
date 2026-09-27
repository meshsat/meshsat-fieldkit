"""The consolidated schematic-phase re-take driver (MESHSAT-1357, 27 September 2026).

Three properties, each asked of the REAL registries and of a fixture that must break it:
  * the plan covers every applicable SCHEMATIC-phase rule of every board that the coverage map lists (every verdict
    name the map gives such a rule is written by a planned command, and a rule verified by a desk review is listed);
  * a verdict whose writer the driver does not know, or whose writer rules_status.CONFIG_INPUTS does not declare, is an
    ERROR in the plan, never a silent skip;
  * without --in-place no command writes outside VERDICT_DIR: cwd, VERDICT_DIR and every staged copy lie under the
    verdict root, every relative argument resolves under the cwd, every absolute one is a read-only tree argument, a
    verdict directory inside the repository is refused, and a writer that touches the tree's evidence fails the run.
Nothing here runs a gate: the run guard is exercised with a stand-in step in a temporary directory."""
import os, sys, copy, json, tempfile, atexit, shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import retake_schematic_phase as RT
import rules_lib as R
import rules_status as S


def _tmp(prefix):
    """A temporary directory removed when the test process ends (the runner is shared)."""
    d = tempfile.mkdtemp(prefix=prefix)
    atexit.register(shutil.rmtree, d, True)
    return d


def _root():
    return _tmp("rtk-vd-")


def t_the_plan_covers_every_schematic_rule_the_coverage_map_lists():
    reg, facts, cov, m = R.load(), R.facts(), S.coverage(), S.manifest()
    p = RT.plan(verdict_dir=_root(), reg=reg, facts=facts, cov=cov, m=m)
    assert not p["errors"], p["errors"]
    by = {b["letter"]: b for b in p["boards"]}
    assert set(by) == set(m["boards"]), (sorted(by), sorted(m["boards"]))
    checked = 0
    for L in m["boards"]:
        planned = {n for st in by[L]["steps"] for n in st["verdicts"]}
        listed = {r["rule"] for r in by[L]["rules"]}
        for rule, _why in R.rules_for(L, reg, facts):
            if rule["verification_phase"] != "SCHEMATIC": continue
            c = cov.get(rule["id"])
            assert c is not None, "%s applies to %s and the coverage map does not list it" % (rule["id"], L)
            assert rule["id"] in listed, "%s of board %s is missing from the plan" % (rule["id"], L)
            if c.get("maturity") == "ENFORCED":
                for n in S._names(c, L):
                    assert n in planned, "board %s: %s's verdict %s is written by no planned command" % (L, rule["id"], n)
                    checked += 1
    assert checked > 50, checked      # the real set: about seventy verdict names over seven boards


def t_the_layout_entry_rule_pass_requirements_are_in_the_plan():
    holds = R.board_holds()
    p = RT.plan(verdict_dir=_root())
    by = {b["letter"]: b for b in p["boards"]}
    for L, h in holds.items():
        if L not in by: continue
        for q in (h.get("layout_entry_requires") or []):
            if q.get("kind") == "rule_pass":
                assert q["rule"] in {r["rule"] for r in by[L]["rules"]}, (L, q["rule"])


def t_a_verdict_with_no_writer_in_the_map_is_an_error():
    cov = copy.deepcopy(S.coverage())
    cov["SCH-001"]["verification"]["verdict"] = "erc_gate, a_verdict_nobody_writes"
    p = RT.plan(boards=["a"], verdict_dir=_root(), cov=cov)
    assert p["errors"] and any("a_verdict_nobody_writes" in e for e in p["errors"]), p["errors"]
    row = [r for r in p["boards"][0]["rules"] if r["rule"] == "SCH-001"][0]
    assert row["action"].startswith("ERROR"), row


def t_a_rule_missing_from_the_coverage_map_is_an_error():
    cov = copy.deepcopy(S.coverage())
    del cov["SCH-004"]
    p = RT.plan(boards=["a"], verdict_dir=_root(), cov=cov)
    assert any("SCH-004" in e and "coverage" in e for e in p["errors"]), p["errors"]


def t_a_writer_not_declared_in_config_inputs_is_an_error():
    saved = S.CONFIG_INPUTS.pop("clock_check.py")
    try:
        p = RT.plan(boards=["a"], verdict_dir=_root())
        assert any("clock_check.py" in e and "CONFIG_INPUTS" in e for e in p["errors"]), p["errors"]
    finally:
        S.CONFIG_INPUTS["clock_check.py"] = saved


def t_no_writer_reaches_the_network():
    for key, (wf, _argv, _n) in list(RT.WRITERS.items()) + list(RT.WRITERS_NO_NETLIST.items()):
        assert wf not in RT.NETWORK_WRITERS, (key, wf)
    saved = RT.WRITERS["clock_check"]
    RT.WRITERS["clock_check"] = ("jlc_certify.py", ["{T}/jlc_certify.py"], None)
    try:
        p = RT.plan(boards=["a"], verdict_dir=_root())
        assert any("network" in e for e in p["errors"]), p["errors"]
    finally:
        RT.WRITERS["clock_check"] = saved


def t_no_command_writes_outside_the_verdict_dir_without_in_place():
    root = _root()
    p = RT.plan(verdict_dir=root)
    assert not p["in_place"]
    n = 0
    for bp in p["boards"]:
        assert RT._inside(bp["cwd"], root) and RT._inside(bp["verdict_dir"], root), bp["cwd"]
        for s in bp["stage"]:
            assert RT._inside(s["to"], root), s
            assert not RT._inside(s["from"], root), s
        for st in bp["steps"]:
            n += 1
            assert st["cwd"] == bp["cwd"], st
            assert RT._inside(st["env"]["VERDICT_DIR"], root), st["env"]
            assert os.path.normpath(st["env"]["VERDICT_DIR"]) == os.path.join(bp["cwd"], "out"), st["env"]
            for a, t in zip(st["argv"][1:], st["argv_template"][1:]):
                if os.path.isabs(a):
                    # an absolute argument is the tool itself or the tree named as a read-only input
                    assert t.startswith(RT.READ_ONLY_ARGS), (bp["letter"], a, t)
                    assert RT._inside(a, RT.HERE) or a == RT.ECAD, (bp["letter"], a)
                elif "/" in a or a.endswith((".net", ".kicad_pcb")) or a == ".":
                    assert RT._inside(os.path.join(st["cwd"], a), root), (bp["letter"], a)
    assert n > 50, n


def t_in_place_writes_into_the_phase_directory():
    p = RT.plan(boards=["b"], in_place=True)
    bp = p["boards"][0]
    pd = os.path.join(RT.ECAD, bp["phase_dir"])
    assert bp["cwd"] == pd and bp["verdict_dir"] == os.path.join(pd, "out"), bp
    assert not bp["stage"], bp["stage"]


def t_a_run_in_the_tree_is_refused_without_in_place():
    assert RT.check_call(False, None)                                             # no verdict directory at all
    assert RT.check_call(False, os.path.join(RT.ECAD, "pcb-a-power-a23", "out"))  # the tree's own evidence folder
    assert RT.check_call(False, RT.ECAD)
    assert RT.check_call(True, _root())                                           # the two modes are exclusive
    assert RT.check_call(False, _root()) is None
    assert RT.check_call(True, None) is None
    assert RT.main(["--run", "--board", "a"]) == 2
    assert RT.main(["--run", "--verdict-dir", os.path.join(RT.ECAD, "out")]) == 2


def t_a_writer_that_touches_the_tree_fails_the_run():
    """The guard, with a stand-in writer: a fake 'tree' evidence folder, a step that writes a verdict where it should
    and one that also writes into the fake tree. The first run is clean, the second is refused."""
    tree = _tmp("rtk-tree-")
    os.makedirs(os.path.join(tree, "out"))
    root = _root()
    cwd = os.path.join(root, "pcb-x"); os.makedirs(os.path.join(cwd, "out"))

    def fake(code):
        return {"in_place": False, "verdict_root": root, "errors": [], "boards": [{
            "letter": "x", "stem": "pcb-x", "phase_dir": "pcb-x", "cwd": cwd, "verdict_dir": os.path.join(cwd, "out"),
            "no_chain": True, "declared_phase": "X1", "netlist": None, "rules": [], "stage": [], "errors": [],
            "steps": [{"writer": "stand-in", "argv": [sys.executable, "-c", code], "argv_template": [], "needs": None,
                       "rules": ["SCH-000"], "verdicts": ["stand_in"], "cwd": cwd,
                       "env": {"VERDICT_DIR": os.path.join(cwd, "out")}}]}]}
    write_own = ("import json,os; json.dump({'verdict':'PASS','ts':'now'}, "
                 "open(os.path.join(os.environ['VERDICT_DIR'],'stand_in.verdict.json'),'w'))")
    saved = (RT.evidence_folders, RT.inputs_of)
    RT.evidence_folders = lambda m=None: [os.path.join(tree, "out")]
    RT.inputs_of = lambda bp: []
    try:
        res = RT.run(fake(write_own), log=lambda *a: None)
        assert res["ok"] and not res["tree_touched"], res
        rd = res["boards"][0]["steps"][0]["readings"]["stand_in"]
        assert rd["result"] == "PASS" and rd["written"], res          # the answer as verdict.write names it
        stray = write_own + "; open(%r,'w').write('x')" % os.path.join(tree, "out", "stray.verdict.json")
        res = RT.run(fake(stray), log=lambda *a: None)
        assert not res["ok"] and any(t.endswith("stray.verdict.json") for t in res["tree_touched"]), res
    finally:
        RT.evidence_folders, RT.inputs_of = saved


def t_an_uncommitted_input_is_named():
    d = _tmp("rtk-git-")
    f = os.path.join(d, "x.net"); open(f, "w").write("(export)\n")
    bad = RT.uncommitted([f])
    assert bad and bad[0][0] == f, bad


def t_routed_is_taken_only_in_place_and_an_unknown_argument_is_refused():
    root = _root()
    assert RT.check_call(False, root, routed=True)                 # routed/ is the tree's tracked evidence
    assert RT.check_call(True, None, routed=True) is None
    assert RT.main(["--run", "--routed", "--verdict-dir", root]) == 2
    assert RT.main(["--plan", "--inplace"]) == 2                     # a typo is refused, never read as "not in place"
    assert RT.main(["--plan", "--board"]) == 2
    assert os.listdir(root) == [], os.listdir(root)


def _fake_in_place(cwd, code, writer="edge_length.py", verdict="edge_length"):
    return {"in_place": True, "verdict_root": None, "errors": [], "boards": [{
        "letter": "x", "stem": "pcb-x", "phase_dir": "pcb-x", "cwd": cwd, "verdict_dir": os.path.join(cwd, "out"),
        "no_chain": True, "declared_phase": "X1", "netlist": None, "rules": [], "stage": [], "errors": [],
        "steps": [{"writer": writer, "argv": [sys.executable, "-c", code], "argv_template": [], "needs": None,
                   "rules": ["SI-001"], "verdicts": [verdict], "cwd": cwd, "env": {"VERDICT_DIR": os.path.join(cwd, "out")}}]}]}


def t_routed_copies_the_readings_and_the_companions_this_run_wrote():
    """--routed in place: the re-taken verdict and the table its writer wrote beside it go to <phase>/routed/, as
    gate_sweep.sh copies them; a table left by an earlier run beside a fresh verdict is not copied."""
    saved = RT.inputs_of
    RT.inputs_of = lambda bp: []
    try:
        cwd = _tmp("rtk-inplace-"); os.makedirs(os.path.join(cwd, "out"))
        both = ("import json,os; d=os.environ['VERDICT_DIR']; json.dump({'verdict':'INCONCLUSIVE','ts':'now'}, "
                "open(os.path.join(d,'edge_length.verdict.json'),'w')); open(os.path.join(d,'edge_length.table.json'),'w').write('{}')")
        res = RT.run(_fake_in_place(cwd, both), routed=True, log=lambda *a: None)
        assert res["ok"], res
        assert sorted(os.listdir(os.path.join(cwd, "routed"))) == ["edge_length.table.json", "edge_length.verdict.json"]
        cwd = _tmp("rtk-inplace-"); os.makedirs(os.path.join(cwd, "out"))
        old = os.path.join(cwd, "out", "edge_length.table.json"); open(old, "w").write("{}")
        os.utime(old, (1e9, 1e9))                                      # an earlier run's table
        only = ("import json,os; json.dump({'verdict':'PASS','ts':'now'}, "
                "open(os.path.join(os.environ['VERDICT_DIR'],'edge_length.verdict.json'),'w'))")
        res = RT.run(_fake_in_place(cwd, only), routed=True, log=lambda *a: None)
        assert res["ok"], res
        assert os.listdir(os.path.join(cwd, "routed")) == ["edge_length.verdict.json"], os.listdir(os.path.join(cwd, "routed"))
    finally:
        RT.inputs_of = saved


def t_a_step_that_writes_nothing_fails_the_run_and_copies_nothing():
    saved = RT.inputs_of
    RT.inputs_of = lambda bp: []
    try:
        cwd = _tmp("rtk-inplace-"); os.makedirs(os.path.join(cwd, "out"))
        res = RT.run(_fake_in_place(cwd, "pass"), routed=True, log=lambda *a: None)
        assert not res["ok"], res
        rd = res["boards"][0]["steps"][0]["readings"]["edge_length"]
        assert rd["result"] == "NOT WRITTEN" and not rd["written"], rd
        assert not os.listdir(os.path.join(cwd, "routed")), os.listdir(os.path.join(cwd, "routed"))
    finally:
        RT.inputs_of = saved
