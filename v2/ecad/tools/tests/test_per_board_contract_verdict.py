#!/usr/bin/env python3
"""A per-board contract verdict named in the coverage map is the one read (MESHSAT-1357, 27 September 2026, stream w4r).

Board E5 has no netlist, so the set verdict check_contracts, which judges the contracts between the six boards that have
one, reads nothing of it: E5's INT-001 read AWAITING_REVALIDATION (UNBOUND) whatever was re-taken. The coverage map now
names, for E5 alone, the reading that judges E5's one interface (`verification.verdict_by_board: {e5: "interfaces_<letter>,
check_contracts_<letter>"}`), and block_contract.py writes it from E5's board file and board A's CURRENT netlist.

What is held here, without KiCad:
  * every reader of the map reads the per-board names on that board and the row's own names everywhere else
    (rules_status._names and result_for, and the re-take driver's plan), on a fixture and on the real map;
  * the reading decides every rule that names it, so it carries each rule's digest (block_contract.decides);
  * a verdict shared through a per-board line says why it measures that rule (as `_shared_verdict_why` does for the
    row's own names, test_rule_gate_mapping);
  * a reading that records what block_contract.py records binds on E5 against the tree as it is, and the same reading
    with board A's board file recorded would not (OTHER_BOARD), nor with a netlist that is not board A's (OTHER_DESIGN);
  * the J_DOCK mount the tool assumes is the one board A's placement generator states (parsed, not grepped);
  * on a host without pcbnew the tool writes this rule's own verdict declaring the absence, never a crash under a name
    no rule reads.
The KiCad half (the pin map by position, a power pin with no target) is tests/test_block_contract.py."""
import os, sys, ast, json, tempfile, atexit, shutil, subprocess, datetime

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
from harness import Skip, need
import rules_lib as R
import rules_status as S
import block_contract as B
import phase_artefacts as PA

ECAD = os.path.dirname(TOOLS)
E5 = os.path.join(ECAD, "pcb-e5-block", "pcb-e5-block.kicad_pcb")


def _tmp(prefix):
    d = tempfile.mkdtemp(prefix=prefix)
    atexit.register(shutil.rmtree, d, True)
    return d


def _reading(result, ts="2026-09-27T10:00:00Z"):
    return {"ts": ts, "verdict": result, "denominator": 1, "counts": {"pass": int(result == "PASS"), "fail": int(result == "FAIL")}}


def t_a_per_board_verdict_named_in_the_map_is_the_one_read():
    """The fixture: a row reads `gate_<letter>, set_gate` and names `gate_<letter>, board_gate_<letter>` for board e5.
    On e5 the per-board reading decides (it FAILs, so a PASS would mean the set verdict was read instead); on board a
    the row's own names decide and board a's per-board reading, which the row does not name there, is never read."""
    rule = {"id": "FIX-001", "verification_phase": "SCHEMATIC"}
    cov = {"FIX-001": {"maturity": "ENFORCED", "verification": {
        "verdict": "gate_<letter>, set_gate", "verdict_by_board": {"e5": "gate_<letter>, board_gate_<letter>"}}}}
    assert S._names(cov["FIX-001"], "e5") == ["gate_e5", "board_gate_e5"], S._names(cov["FIX-001"], "e5")
    assert S._names(cov["FIX-001"], "a") == ["gate_a", "set_gate"], S._names(cov["FIX-001"], "a")
    m = {"evidence": {}, "boards": {}}
    vs = {"gate_e5": dict(_reading("PASS"), _path="e5/gate"), "set_gate": dict(_reading("PASS"), _path="set"),
          "board_gate_e5": dict(_reading("FAIL"), _path="e5/board_gate")}
    r = S.result_for(rule, "e5", cov, vs, m, None)
    assert r["result"] == "FAIL" and r["evidence"] == "e5/board_gate" and "board_gate_e5" in r["why"], r
    vs_a = {"gate_a": dict(_reading("PASS"), _path="a/gate"), "set_gate": dict(_reading("PASS"), _path="set"),
            "board_gate_a": dict(_reading("FAIL"), _path="a/board_gate")}
    r = S.result_for(rule, "a", cov, vs_a, m, None)
    assert r["result"] == "PASS", r
    # a row that names nothing for the board reads as before, and one naming nothing at all is still refused
    cov2 = {"FIX-001": {"maturity": "ENFORCED", "verification": {"verdict": "gate_<letter>"}}}
    assert S._names(cov2["FIX-001"], "e5") == ["gate_e5"]
    cov3 = {"FIX-001": {"maturity": "ENFORCED", "verification": {"verdict_by_board": {"e5": ""}}}}
    r = S.result_for(rule, "e5", cov3, vs, m, None)
    assert r["result"] == "INCONCLUSIVE" and "names no verdict" in r["why"], r


def t_the_map_names_e5_s_own_contract_reading_for_int_001_and_nothing_else_moves():
    cov, m = S.coverage(), S.manifest()
    c = cov["INT-001"]
    assert S._names(c, "e5") == ["interfaces_e5", "check_contracts_e5"], S._names(c, "e5")
    for L in m["boards"]:
        if L == "e5": continue
        assert S._names(c, L) == ["interfaces_%s" % L, "check_contracts"], (L, S._names(c, L))
    # every per-board line in the map names only boards the manifest judges
    for rid, row in cov.items():
        per = ((row.get("verification") or {}).get("verdict_by_board")) or {}
        assert isinstance(per, dict), "%s: verdict_by_board is not a map of board to names" % rid
        assert set(per) <= set(m["boards"]), "%s names verdicts for boards the manifest does not judge: %s" % (rid, sorted(set(per) - set(m["boards"])))


def t_the_per_board_reading_decides_every_rule_that_names_it():
    """A verdict carries the digest of each rule it decides, so a change of one rule stales it and a registry edit
    elsewhere does not. verdict._rules_for_tool reads the row's own names only; block_contract.decides adds the rules
    that name its verdict for one board."""
    cov = S.coverage()
    want = {rid for rid, row in cov.items()
            for L, raw in ((((row.get("verification") or {}).get("verdict_by_board")) or {}).items())
            if B.NAME in [n.strip().replace("<letter>", L) for n in str(raw or "").split(",")]}
    want |= {rid for rid, row in cov.items() if "check_contracts_<letter>" in [n.strip() for n in str(((row.get("verification") or {}).get("verdict")) or "").split(",")]}
    got = set(B.decides())
    assert {"INT-001", "SCH-003"} <= got and want <= got, (sorted(got), sorted(want))


def t_a_verdict_shared_through_a_per_board_line_says_why():
    """The rule of test_rule_gate_mapping (a verdict decided by several rules says what it measures for each), for the
    per-board lines: a row that reads, on one board, a verdict another rule reads there carries `_verdict_by_board_why`."""
    cov, m = S.coverage(), S.manifest()
    missing = []
    for rid, row in cov.items():
        per = ((row.get("verification") or {}).get("verdict_by_board")) or {}
        for L in per:
            mine = set(S._names(row, L))
            others = {o for o, r2 in cov.items() if o != rid and mine & set(S._names(r2, L))}
            if others and not str(row.get("_verdict_by_board_why") or "").strip():
                missing.append("%s on %s shares %s with %s" % (rid, L, sorted(mine), sorted(others)))
    assert not missing, "; ".join(missing)


def _placement():
    """(rotation, back) of J_DOCK as gen_pcb_a3.py places it: FIXED["J_DOCK"] and membership of BACK, parsed."""
    tree = ast.parse(open(os.path.join(TOOLS, "gen_pcb_a3.py"), encoding="utf-8").read())
    rot = back = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name): continue
        name = node.targets[0].id
        if name == "FIXED" and isinstance(node.value, ast.Dict):
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == "J_DOCK":
                    rot = ast.literal_eval(v)[2]
        if name == "BACK":
            back = any(isinstance(x, ast.Constant) and x.value == "J_DOCK" for x in ast.walk(node.value))
    return rot, back


def t_the_dock_mount_is_the_one_board_a_s_placement_states():
    rot, back = _placement()
    assert rot is not None and back is not None, "gen_pcb_a3.py no longer states J_DOCK's place in FIXED and BACK"
    assert float(rot) == float(B.DOCK_MOUNT["rotation"]) and bool(back) == bool(B.DOCK_MOUNT["back"]), (
        "board A's placement mounts J_DOCK at rotation %s, %s, and block_contract.DOCK_MOUNT says %s: the block's "
        "targets would be matched under another pin" % (rot, "on the underside" if back else "on top", B.DOCK_MOUNT))


def t_the_netlist_is_parsed_whole():
    """Every node of board A's netlist, the same as rules_status's parse (the last net included, R4T-F1)."""
    n = PA.netlist("a")
    need(n, "board A's netlist is not in this tree")
    a = B.read_netlist(open(n, "rb").read())
    q = S.netlist_parse(n)
    mine = {(r, p): net for r, d in a["pins"].items() for p, net in d.items()}
    theirs = {(r, p): net for net, nodes in q["nets"].items() for r, p in nodes}
    assert mine == theirs and len(mine) > 100, (len(mine), len(theirs))
    assert a["footprint"].get(B.CONNECTOR, "").endswith("PogoPins_2x6"), a["footprint"].get(B.CONNECTOR)


def t_a_board_a_board_file_names_its_netlist_and_is_not_read():
    """gate_sweep.sh passes board A's board file; the tool reads that phase directory's netlist and says so."""
    p, how = B.a_netlist_for(os.path.join(ECAD, "pcb-a-power-a23", "pcb-a-power.kicad_pcb"))
    assert p.endswith(os.path.join("pcb-a-power-a23", "out", "pcb-a-power.net")) and "not read" in how, (p, how)
    assert B.a_netlist_for(None)[0] == PA.netlist("a")
    assert B.a_netlist_for("x.net") == ("x.net", "")


def t_a_reading_that_records_what_the_tool_records_binds_on_e5():
    """Against the tree as it is: a reading recording E5's board file, board A's current netlist and the land (what
    block_contract.inputs_for records) is BOUND for INT-001 on E5; the same reading with board A's BOARD FILE recorded is
    OTHER_BOARD (why the tool does not read it), and with a netlist that is not board A's current one OTHER_DESIGN."""
    need(E5, "board E5 is not in this tree")
    n = PA.netlist("a"); need(n, "board A's netlist is not in this tree")
    m = S.manifest()
    rule = next(r for r in R.load()["rules"] if r["id"] == "INT-001")
    cand = S.candidate("e5", m)
    regs = S.registers()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    land = B.land_file("meshsat:PogoPins_2x6")
    rec = {"ts": now, "inputs": B.inputs_for(E5, n, land)}
    b, cause, why, _e = S._bound(rule, "e5", B.NAME, rec, cand, regs, m)
    assert b and cause == "BOUND", (cause, why)
    a_board = os.path.join(os.path.dirname(os.path.dirname(n)), "pcb-a-power.kicad_pcb")
    if os.path.exists(a_board):
        rec2 = {"ts": now, "inputs": dict(B.inputs_for(E5, n, land), board_a=PA.record(a_board, content=False))}
        assert S._bound(rule, "e5", B.NAME, rec2, cand, regs, m)[1] == "OTHER_BOARD"
    rec3 = json.loads(json.dumps(rec))
    rec3["inputs"]["board_a_netlist"].update(sha256_16="0" * 16, content16="0" * 16)
    assert S._bound(rule, "e5", B.NAME, rec3, cand, regs, m)[1] == "OTHER_DESIGN"


def t_the_re_take_driver_plans_the_per_board_reading_with_its_own_writer():
    """The re-take driver reads the same names (rules_status._names) and must run the tool that WRITES the per-board
    reading: block_contract.py for check_contracts_e5 (check_contracts.py writes nothing for E5), declared in
    CONFIG_INPUTS so its reading can bind."""
    import retake_schematic_phase as RT
    p = RT.plan(boards=["e5"], verdict_dir=_tmp("w4r-plan-"))
    assert not p["errors"], p["errors"]
    steps = [st for st in p["boards"][0]["steps"] if B.NAME in st["verdicts"]]
    assert len(steps) == 1 and steps[0]["writer"] == "block_contract.py", steps
    assert "INT-001" in steps[0]["rules"], steps[0]["rules"]
    assert "block_contract.py" in S.CONFIG_INPUTS


def t_without_pcbnew_the_tool_writes_its_own_verdict_declaring_the_absence():
    try:
        import pcbnew  # noqa: F401
        raise Skip("pcbnew is importable here: the absence cannot be shown")
    except ImportError:
        pass
    need(E5, "board E5 is not in this tree")
    d = _tmp("w4r-nokicad-")
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "block_contract.py"), E5], capture_output=True, text=True,
                       env=dict(os.environ, VERDICT_DIR=d), cwd=ECAD)
    f = os.path.join(d, B.NAME + ".verdict.json")
    assert os.path.exists(f), (r.stdout + r.stderr)[-400:]
    rec = json.load(open(f))
    assert rec["verdict"] == "INCONCLUSIVE" and "pcbnew" in str(rec.get("missing_input")), rec
    assert not os.path.exists(os.path.join(d, "block_contract.verdict.json"))
