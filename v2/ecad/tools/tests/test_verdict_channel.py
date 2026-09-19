#!/usr/bin/env python3
"""The verdict channel: every gate decides in a file, and no driver decides by reading prose.

This is stage 0a of the control-plane programme (MESHSAT-862, 11 September 2026, `v2/docs/CONTROL-PLANE.md`).
Before it, eighteen gates announced their decision on stdout and thirteen drivers recovered it with
`grep -q 'RESULT: ALL PASS'`, which meant:

  * every finish ran its board gate TWICE, the second time only to produce a string to match;
  * a gate that crashed before printing its last line was indistinguishable from a gate that failed;
  * a gate that checked nothing printed exactly what a gate that checked everything and passed printed.

The rules below are lexical on purpose. They hold without pcbnew, without a board and without a box, which is
what lets them run on every host; and a lexical rule catches the reintroduction of the old shape in a new file,
which is the failure mode a one-off repair always has.
"""
import os, re, json, glob, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import verdict

# The gates named by the programme: each decides something a driver or a human acts on.
GATES = ["check_pcb_a.py", "check_pcb_b.py", "check_pcb_c.py", "check_pcb_d.py", "check_pcb_e.py",
         # check_pcb_e5.py, 16 September 2026: the seventh board had no gate at all, and it is the contact
         # block the whole energy chain passes through
         "check_pcb_e5.py", "check_pcb_p.py", "hardset.py", "impedance_check.py", "dc_drop.py", "check_contracts.py",
         "check_zone_nets.py", "intent_checks.py", "place_audit.py", "erc_gate.py",
         "verify_deliverable.py", "pruned_gate.py", "lcsc_fill.py",
         # added 16 September 2026 with the rule registry: every rule with an ENFORCED maturity needs a gate in
         # this catalogue, or the admission rule below cannot see whether it has fixtures
         # couple_gap.py (a measurement read back off the copper) and jumper_clearance.py (a fixer that widens
         # a pad's own clearance) are deliberately NOT here: neither decides whether a board may ship
         "class_floor.py", "claims_check.py", "return_via.py", "derate.py", "via_audit.py",
         "fab_limits.py", "clock_check.py", "port_protect.py"]

WRITES = re.compile(r"\b(?:verdict|_v)\.write\s*\(")
IMPORTS = re.compile(r"^\s*import verdict(?: as _v)?\s*$", re.M)
GREP_PROSE = re.compile(r"grep\s+-q\S*\s+\S*RESULT: ALL PASS")


def _shell_lines():
    for p in sorted(glob.glob(os.path.join(TOOLS, "*.sh"))):
        for n, line in enumerate(open(p, errors="replace"), 1):
            yield os.path.basename(p), n, line


def t_every_gate_writes_a_verdict():
    missing = [g for g in GATES if not WRITES.search(open(os.path.join(TOOLS, g)).read())]
    assert not missing, "these gates still decide only on stdout: %s" % missing


def t_every_gate_that_writes_a_verdict_imports_the_writer():
    """Compiling proves nothing here: `verdict.write(...)` in a file with no import is a NameError at the
    moment the gate decides, which is the one moment nobody is watching. erc_gate.py shipped exactly that
    for the length of one test run on 11 September 2026."""
    bad = []
    for g in GATES:
        s = open(os.path.join(TOOLS, g)).read()
        if WRITES.search(s) and not IMPORTS.search(s): bad.append(g)
    assert not bad, "these call the verdict writer without importing it: %s" % bad


def t_no_driver_decides_by_grepping_a_gates_prose():
    """The rule, not the instance: no shell script may branch on a gate's human-readable summary line."""
    bad = ["%s:%d" % (f, n) for f, n, line in _shell_lines() if GREP_PROSE.search(line)]
    assert not bad, "a driver still reads a verdict out of prose: %s" % bad


def t_no_driver_runs_a_board_gate_twice_on_one_line():
    """Two invocations of one check_pcb_* on a single line is the double-run shape: one to print, one to test."""
    bad = ["%s:%d" % (f, n) for f, n, line in _shell_lines()
           if not line.lstrip().startswith("#") and len(re.findall(r"check_pcb_[a-z]\.py", line)) > 1]
    assert not bad, "a driver runs its board gate twice: %s" % bad


def t_every_hardset_judgement_is_labelled():
    """hardset writes one verdict file per label. A finish makes three judgements with it (after the stub
    router, after stub_accept, the routed-board gate) and a fourth in the deliverable; unlabelled, they all
    land on out/hardset.verdict.json and only the last one survives to be read."""
    bad = []
    for f, n, line in _shell_lines():
        if line.lstrip().startswith("#"): continue
        for call in re.findall(r"hardset\.py\s[^|;)]*", line):
            if "--label" in call: continue
            if any(k in call for k in ("--score", "--counts", "--gate", "--flag")):
                bad.append("%s:%d %s" % (f, n, call.strip()[:60]))
    assert not bad, "an unlabelled hardset judgement would overwrite another's verdict: %s" % bad


def t_an_unrecognised_verdict_is_never_a_pass():
    d = tempfile.mkdtemp(prefix="verdict-test-")
    assert verdict.write("t", "ALL PASS", out_dir=d, quiet=True) == verdict.USAGE
    assert verdict.write("t", True, out_dir=d, quiet=True) == verdict.USAGE
    assert verdict.write("t", None, out_dir=d, quiet=True) == verdict.USAGE
    assert not os.path.exists(os.path.join(d, "t.verdict.json")), "a rejected verdict must write nothing"


def t_a_missing_verdict_reads_back_inconclusive():
    d = tempfile.mkdtemp(prefix="verdict-test-")
    rec, code = verdict.read(os.path.join(d, "nothing.verdict.json"))
    assert rec["verdict"] == verdict.INCONCLUSIVE and code == 3, (rec, code)
    open(os.path.join(d, "junk.verdict.json"), "w").write("{not json")
    rec, code = verdict.read(os.path.join(d, "junk.verdict.json"))
    assert rec["verdict"] == verdict.INCONCLUSIVE and code == 3, (rec, code)
    json.dump({"verdict": "probably fine"}, open(os.path.join(d, "odd.verdict.json"), "w"))
    rec, code = verdict.read(os.path.join(d, "odd.verdict.json"))
    assert code == 3, (rec, code)


def t_the_denominator_travels_with_every_verdict():
    d = tempfile.mkdtemp(prefix="verdict-test-")
    verdict.write("t", verdict.PASS, counts={"fail": 0}, denominator=0, out_dir=d, quiet=True)
    rec = json.load(open(os.path.join(d, "t.verdict.json")))
    assert "denominator" in rec and rec["denominator"] == 0, rec
    assert rec["version"] and rec["ts"], "a verdict names the code and the moment that produced it"


def t_the_exit_code_equals_the_verdict():
    d = tempfile.mkdtemp(prefix="verdict-test-")
    assert verdict.write("t", verdict.PASS, out_dir=d, quiet=True) == 0
    assert verdict.write("t", verdict.FAIL, out_dir=d, quiet=True) == 1
    assert verdict.write("t", verdict.INCONCLUSIVE, out_dir=d, quiet=True) == 3


# ---------------------------------------------------------------- the collector

def t_the_collector_takes_the_worst_verdict():
    d = tempfile.mkdtemp(prefix="vc-")
    verdict.write("a", verdict.PASS, denominator=3, out_dir=d, quiet=True)
    verdict.write("b", verdict.PASS, denominator=7, out_dir=d, quiet=True)
    worst, found, missing = verdict.collect(d)
    assert worst == 0 and len(found) == 2 and not missing, (worst, found, missing)
    verdict.write("c", verdict.FAIL, denominator=1, out_dir=d, quiet=True)
    assert verdict.collect(d)[0] == 1
    verdict.write("d", verdict.INCONCLUSIVE, denominator=0, out_dir=d, quiet=True)
    assert verdict.collect(d)[0] == 3, "INCONCLUSIVE is worse than FAIL here: it means a bar was not tested"


def t_a_required_verdict_that_is_absent_is_inconclusive():
    """A gate that did not run is the case this pipeline keeps mistaking for a gate that passed."""
    d = tempfile.mkdtemp(prefix="vc2-")
    verdict.write("ran", verdict.PASS, denominator=5, out_dir=d, quiet=True)
    worst, found, missing = verdict.collect(d, require=("ran", "never_ran"))
    assert missing == ["never_ran"], missing
    assert worst == 3, worst


def t_an_unreadable_verdict_does_not_become_a_pass():
    d = tempfile.mkdtemp(prefix="vc3-")
    verdict.write("good", verdict.PASS, denominator=1, out_dir=d, quiet=True)
    open(os.path.join(d, "junk.verdict.json"), "w").write("{not json")
    worst, found, missing = verdict.collect(d)
    assert worst == 3, (worst, found)


def t_no_profile_declares_a_key_nothing_reads():
    """A configuration key nobody reads is a claim about behaviour that does not happen. `budget_rounds` sat in
    twelve profiles and the CLI's --rounds decided; `expect.hard` and `expect.unrouted` sat in all twelve and
    were wired to a judge on 11 September rather than deleted, because those two express a real prediction."""
    import glob
    dead = ("budget_rounds",)
    bad = []
    for p in sorted(glob.glob(os.path.join(TOOLS, "routeflow", "*.json"))):
        d = json.load(open(p))
        for k in dead:
            if k in d: bad.append("%s carries %s" % (os.path.basename(p), k))
    src = open(os.path.join(TOOLS, "routeflow.py")).read()
    for k in ("expect", "hard", "unrouted"):
        assert k in src, "expect.%s must be read by the supervisor or removed from the profiles" % k
    assert not bad, bad


# ---------------------------------------------------------------- pre and post are different judgements
# `hardset.py <json> pre|post` has always taken the stage, and the printed line and the gate file honoured it.
# The VERDICT did not: it required unrouted == 0 in both, so a pre-route board failed for being unrouted, which
# is the state a pre-route board is defined by. Nothing read the file until the supervisor started deciding on
# verdicts, and then it blocked two of the wave's four boards on the first run (11 September 2026).

def _drc(unconnected=0, violations=()):
    import tempfile, json as _j
    d = tempfile.mkdtemp(prefix="hardset-stage-")
    _j.dump({"unconnected_items": [{"items": []} for _ in range(unconnected)],
             "violations": list(violations)}, open(os.path.join(d, "drc.json"), "w"))
    return d


def _hardset(stage, unconnected):
    import subprocess, json as _j
    d = _drc(unconnected)
    subprocess.run([sys.executable, os.path.join(TOOLS, "hardset.py"), os.path.join(d, "drc.json"), stage,
                    "--label", "t"], capture_output=True, text=True, cwd=d)
    return _j.load(open(os.path.join(d, "out", "hardset-t.verdict.json"))) if os.path.exists(os.path.join(d, "out", "hardset-t.verdict.json")) \
        else _j.load(open(os.path.join(d, "hardset-t.verdict.json")))


def t_a_pre_route_board_passes_the_hard_set_while_unrouted():
    rec = _hardset("pre", 357)
    assert rec["verdict"] == "PASS", rec
    assert rec["counts"]["unrouted"] == 357 and rec["counts"]["stage"] == "pre", rec


def t_a_routed_board_with_open_connections_fails():
    rec = _hardset("post", 5)
    assert rec["verdict"] == "FAIL", rec
    assert rec["counts"]["stage"] == "post", rec


def t_a_routed_board_with_nothing_open_passes():
    rec = _hardset("post", 0)
    assert rec["verdict"] == "PASS", rec


def t_the_collector_honours_a_horizon():
    """Verdict files persist in out/ across stages and rounds. Board E's second pre-route was blocked by a
    check_contracts verdict its first round's FINISH had written: a judgement about a different moment and a
    different question. `since` drops anything older; a record with no timestamp is kept, because dropping it
    would turn an unreadable record into a silent pass."""
    import tempfile, json as _j, sys as _s
    _s.path.insert(0, TOOLS)
    import verdict as v
    d = tempfile.mkdtemp(prefix="collect-since-")
    def put(tool, verd, ts):
        rec = {"tool": tool, "verdict": verd, "denominator": 1, "counts": {}, "evidence": [], "inputs": {}, "note": ""}
        if ts: rec["ts"] = ts
        _j.dump(rec, open(os.path.join(d, "%s.verdict.json" % tool), "w"))
    put("old_gate", "FAIL", "2026-09-11T10:00:00Z")
    put("new_gate", "PASS", "2026-09-11T12:00:00Z")
    worst, found, missing = v.collect(d, since="2026-09-11T11:00:00Z")
    assert worst == 0, (worst, found)
    assert set(found) == {"new_gate"}, found
    worst2, found2, _ = v.collect(d)
    assert worst2 == 1 and set(found2) == {"old_gate", "new_gate"}, (worst2, found2)
    put("no_ts", "FAIL", None)
    worst3, found3, _ = v.collect(d, since="2026-09-11T11:00:00Z")
    assert "no_ts" in found3 and worst3 == 1, (worst3, found3)


def t_the_horizon_and_the_stamp_come_from_one_clock():
    """The horizon is a string compared against a verdict's `ts`, so the two have to be the same format AND the
    same timezone. The first version passed routeflow's own now(), which is local time with a space separator,
    against a ts in UTC with a T and a Z: 'T' sorts after ' ', so every record landed on the keep side and the
    horizon excluded nothing at all. Board P stayed blocked by a stale verdict with the fix supposedly in.

    This drives both producers rather than either alone, because the defect was in neither."""
    import subprocess, tempfile, json as _j, time as _t
    _s = sys; _s.path.insert(0, TOOLS)
    import verdict as v, routeflow as rf
    assert callable(getattr(v, "now", None)), "verdict has no now(): the channel has no single clock"
    d = tempfile.mkdtemp(prefix="one-clock-")
    horizon = v.now()
    _t.sleep(1.1)
    rec = {"tool": "later_gate", "verdict": "FAIL", "denominator": 1, "counts": {}, "evidence": [], "inputs": {}, "note": "", "ts": v.now()}
    _j.dump(rec, open(os.path.join(d, "later_gate.verdict.json"), "w"))
    worst, found, _ = v.collect(d, since=horizon)
    assert "later_gate" in found, "a verdict written AFTER the horizon was excluded: the formats disagree"
    _t.sleep(1.1)   # the stamp has one-second resolution, so a horizon in the same second is not "after" it
    worst2, found2, _ = v.collect(d, since=v.now())
    assert "later_gate" not in found2, "a verdict written BEFORE the horizon was kept: the formats disagree"
    # and the trap itself: routeflow's display clock must never be used as a horizon
    src = open(os.path.join(TOOLS, "routeflow.py"), errors="replace").read()
    i = src.index("pre_started =")
    line = src[i:src.index("\n", i)]
    assert "verdict.now()" in line, "the horizon is taken from routeflow's local display clock: %s" % line.strip()


def t_an_advisory_verdict_is_recorded_and_never_decides_a_stage():
    """B19's pre stage printed PREROUTE-DONE OK and routeflow read GATE_BLOCKED (15 Sep 2026): the pre-route DRC on the
    pair copper BEFORE the prune and the predictor the board declares as a report had each written a FAIL, and the
    collector took the worst of everything in the directory. A measurement for the record is written, listed and
    hashed like any verdict, and left out of the stage's worst."""
    d = tempfile.mkdtemp(prefix="vc-")
    verdict.write("gate", verdict.PASS, denominator=3, out_dir=d, quiet=True)
    verdict.write("measure", verdict.FAIL, denominator=15, out_dir=d, quiet=True, advisory=True)
    worst, found, missing = verdict.collect(d)
    assert worst == 0 and "measure" in found and found["measure"].get("advisory") is True, (worst, found)
    os.environ["VERDICT_ADVISORY"] = "1"
    try: verdict.write("measure2", verdict.INCONCLUSIVE, denominator=0, out_dir=d, quiet=True)
    finally: os.environ.pop("VERDICT_ADVISORY", None)
    assert verdict.collect(d)[0] == 0, "the environment form must mark the verdict advisory too"
    e = tempfile.mkdtemp(prefix="vc-")
    verdict.write("only", verdict.PASS, denominator=1, out_dir=e, quiet=True, advisory=True)
    assert verdict.collect(e)[0] == 3, "a directory holding only measurements has judged nothing: INCONCLUSIVE"


def t_the_pair_copper_measurement_and_a_declared_off_predictor_are_advisory():
    s = open(os.path.join(TOOLS, "full.sh")).read()
    i = s.find("--label 'pre-route DRC on the pair copper'"); assert i > 0
    assert "VERDICT_ADVISORY=1" in s[s.rfind("\n", 0, i):i], "the pair-copper DRC before the prune is a bar the supervisor would read as the stage's"
    j = s.find("--label 'pre-route DRC on the refused board'"); assert j > 0
    assert "VERDICT_ADVISORY=1" in s[s.rfind("\n", 0, j):j], "the refused-board DRC is printed for the record and the chain's own DRC decides"
    assert 'PAOFF="VERDICT_ADVISORY=1"' in s and "env $PAOFF $ESCENV python3 ../tools/place_audit.py" in s, (
        "a board that declares the predictor as a report must not have its FAIL verdict read as the stage's")


def t_a_verdict_is_written_even_where_the_registry_cannot_be_read():
    """A gate's decision must not depend on the host being able to read the rule registry.

    16 September 2026, found by running the sweep on the box: `rules_lib` raises SystemExit when PyYAML is
    absent, SystemExit does not descend from Exception, and the two best-effort `except Exception` guards in
    the verdict writer let it straight through. Every gate on that host printed its result, wrote NO verdict
    file and exited 1, so a passing board read as a failing one and no evidence existed either way.

    Stamping the rule set is evidence ABOUT a verdict. It can never decide whether the verdict exists, and when
    it is missing the record says why, so a reader can tell "written before the registry" from "written on a
    host that could not read it".
    """
    import builtins, tempfile, importlib
    d = tempfile.mkdtemp(prefix="verdict-noyaml-")
    real = builtins.__import__

    def fake(name, *a, **k):
        if name in ("yaml", "rules_lib"): raise ImportError("not on this host")
        return real(name, *a, **k)

    v = importlib.import_module("verdict")
    v._RULESET[0] = None; v._BY_TOOL[0] = None; v._RULESET_WHY[0] = ""
    builtins.__import__ = fake
    try:
        rc = v.write("probe", v.PASS, denominator=7, out_dir=d, quiet=True)
    finally:
        builtins.__import__ = real
        v._RULESET[0] = None; v._BY_TOOL[0] = None; v._RULESET_WHY[0] = ""
    rec = json.load(open(os.path.join(d, "probe.verdict.json")))
    assert rc == 0 and rec["verdict"] == "PASS", (rc, rec)
    assert rec["policy"].get("rule_set_fingerprint_absent"), \
        "the verdict does not say why it carries no rule-set fingerprint: %s" % rec["policy"]


def t_every_gate_in_the_catalogue_maps_to_a_rule_of_the_registry():
    """Process controls 1 and 2 of the owner's instruction of 16 September: new rules enter through the
    registry, and every gate references the rule ids it decides.

    The argument is the whole reason the registry exists. This project accumulated gates one incident at a
    time, each defensible on its own, and no document could say which requirement any of them served. A gate
    that maps to no rule is either a requirement nobody wrote down or a check nobody can justify, and there is
    no way to tell which from the outside.

    The mapping is not typed into twenty gates: it is the coverage map inverted, so the registry stays the one
    source and a gate cannot drift from it.
    """
    import importlib
    v = importlib.import_module("verdict")
    v._BY_TOOL[0] = None
    import re as _re
    unmapped = []
    for g in GATES:
        stem = g[:-3]
        # The names a gate can write: its own stem, its labelled variants, and every literal it passes to the
        # verdict writer. Reading the source is what lets a tool SPLIT its verdict by rule without this rule
        # going off: intent_checks writes four now, one per rule it runs, because one decoupling capacitor
        # 3 mm too far from its pin was failing the return-path rule on six boards.
        src = open(os.path.join(TOOLS, g), errors="replace").read()
        names = [stem] + ["%s-%s" % (stem, x) for x in ("routed-board-gate", "placed")]
        names += _re.findall(r'(?:verdict|_v)\.write\(\s*"([a-zA-Z0-9_<>-]+)"', src)
        # a tool that writes its verdict names from a table declares them at module scope, so they can be read
        # without executing it (intent_checks writes four from a loop)
        _decl = _re.search(r'^RULE_VERDICTS\s*=\s*\(([^)]*)\)', src, _re.M)
        if _decl: names += _re.findall(r'"([a-zA-Z0-9_<>-]+)"', _decl.group(1))
        if stem.startswith("check_pcb_"): names.append("check_pcb_<letter>")
        if not any(v._rules_for_tool(n) for n in set(names)): unmapped.append(g)
    v._BY_TOOL[0] = None
    assert not unmapped, ("these gates decide a board and map to no rule in the registry, so nothing says which "
                          "requirement they serve: %s" % unmapped)


def t_an_inapplicable_rule_does_not_decide_a_stage_and_is_not_a_pass():
    """Board P's route was blocked by two verdicts that were both correct (MESHSAT-862, 16 September 2026).

    Its crystal check said the board carries no crystal and its exposed-port check said no conductor of its own
    leaves the case. Both are INCONCLUSIVE, because absence is never a pass and a gate that could not judge
    must never read as one; but neither is a gap, and the pre-route gate could not tell them from a check that
    failed to run. The record carries `applicable: false` now: the collector skips it, the verdict stays
    INCONCLUSIVE, and a stage made only of those still reads INCONCLUSIVE rather than passing."""
    import os, sys, tempfile, json
    sys.path.insert(0, TOOLS)
    import verdict as V
    d = tempfile.mkdtemp(prefix="applicability-")
    V.write("t_na", V.INCONCLUSIVE, denominator=0, out_dir=d, quiet=True, applicable=False,
            note="this board carries none of what this rule is about")
    V.write("t_ok", V.PASS, denominator=3, counts={"pass": 3}, out_dir=d, quiet=True)
    worst, found, missing = V.collect(d)
    assert worst == V.CODE[V.PASS], "an inapplicable rule decided the stage: %r" % worst
    rec = json.load(open(os.path.join(d, "t_na.verdict.json")))
    assert rec["verdict"] == V.INCONCLUSIVE and rec["applicable"] is False, rec
    d2 = tempfile.mkdtemp(prefix="applicability-only-")
    V.write("t_na2", V.INCONCLUSIVE, denominator=0, out_dir=d2, quiet=True, applicable=False)
    worst2, _, _ = V.collect(d2)
    assert worst2 == V.CODE[V.INCONCLUSIVE], "a stage of nothing but inapplicable rules read as a pass"


def t_a_check_with_no_input_writes_no_verdict_rather_than_one_about_the_host():
    """Evidence destroyed by a report, 16 September 2026.

    The cross-board contracts are judged from the NETLISTS the chains write into each project's untracked
    `out/`, so on the runner every board is absent. `final_gate.py` runs the check to print one summary line,
    and that incidental run wrote INCONCLUSIVE over board C's contract PASS taken on the box an hour earlier,
    and over the set's own reading: two rules on six boards moved backwards because of where the command was
    typed. A host that cannot see the input has nothing to say about it, and absence is INCONCLUSIVE to the
    readiness computation already, so writing nothing gives the same answer on a fresh tree and keeps the
    answer on a tree that has one.

    The set verdict is stricter than the per-board one: it means "the seven boards agree", which cannot be
    read at all with a board absent."""
    src = open(os.path.join(TOOLS, "check_contracts.py"), encoding="utf-8").read()
    per = src[src.index("for _bd in sorted(set(list(per_board)"):src.index("if (not checked or MISSING or _NO_INTENT)")]
    assert "_richer_on_disk(" in per and "continue" in per, \
        "a board whose netlist is absent still writes over a verdict taken where the netlist was"
    assert "if (not checked or MISSING or _NO_INTENT) and _richer_on_disk(" in src, \
        "the set verdict is written from a tree with less input than the reading already on disk"
    assert "_NO_INTENT = sorted(" in src, \
        "an absent intent file is still read as a board that declared nothing rather than as an absent input"
    i = src.index("if (not checked or MISSING or _NO_INTENT) and _richer_on_disk(")
    assert "sys.exit(3)" in src[i:i + 1200], "the check does not exit INCONCLUSIVE when it judged nothing"
    assert "A READING TAKEN WITH LESS INPUT NEVER REPLACES ONE TAKEN WITH MORE" in src, \
        "the rule behind the guard is no longer written down beside it"


def t_that_refusal_is_executed_and_leaves_an_existing_verdict_alone():
    """Run it: write a PASS where the check writes, run the check on a tree with no netlist, and the PASS must
    still be there afterwards."""
    import subprocess, tempfile, json as _j
    # An EMPTY tree, so the rule is exercised whatever this working copy happens to hold: check_contracts
    # takes the ecad directory to read, and a fresh one has no netlist for any board.
    d = tempfile.mkdtemp(prefix="contracts-keeps-")
    out = os.path.join(d, "out"); os.makedirs(out)
    import verdict
    verdict.write("check_contracts_c", verdict.PASS, denominator=7, out_dir=out, quiet=True,
                  note="a fixture standing in for the reading taken where the netlists are")
    p = os.path.join(out, "check_contracts_c.verdict.json")
    before = _j.load(open(p))
    env = dict(os.environ, VERDICT_DIR=out)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "check_contracts.py"), d],
                       capture_output=True, text=True, cwd=d, env=env)
    assert "no netlist" in (r.stdout + r.stderr), \
        "the rule was not exercised: this tree was expected to have none\n%s" % (r.stdout or "")[-300:]
    after = _j.load(open(p))
    was = before.get("verdict") or before.get("result")
    now = after.get("verdict") or after.get("result")
    assert now == was == "PASS", "the check overwrote a verdict taken where its input existed: %r" % now


def t_the_document_provenance_check_keeps_a_reading_taken_where_the_folders_are():
    """The same rule as the contracts', in the tool that judges the release documents (17 September 2026): a
    sweep tree holds the boards and not the release folders, so this check finds nothing there and would
    overwrite the reading taken where they exist."""
    src = open(os.path.join(TOOLS, "doc_provenance.py"), encoding="utf-8").read()
    assert "A READING TAKEN WITH LESS INPUT NEVER REPLACES ONE TAKEN WITH MORE" in src, \
        "the rule is not written down in the tool that needs it"
    i = src.index("if not rows:")
    seg = src[i:i + 900]
    assert "doc_provenance.verdict.json" in seg and "counts" in seg, \
        "the tool does not look at what is already on disk before writing its empty answer"


# ---------------------------------------------------------------------------------------------------------
# A VERDICT NAMES THE BOARD IT WAS GIVEN (17 September 2026).
#
# `rules_status` compares `inputs.board` with the boards a project directory holds, and a verdict that names
# none can only be attributed by the directory it sits in. That is how a reading about board B19 sat beside
# board B21 and answered for it. Twenty gates take the board as their first argument and passed it to nobody.

def t_a_gate_given_a_board_records_it_even_when_it_does_not_say_so():
    import subprocess, sys, os, json, tempfile, hashlib
    with tempfile.TemporaryDirectory() as d:
        b = os.path.join(d, "pcb-x.kicad_pcb")
        open(b, "wb").write(b"(kicad_pcb (version 20240108))\n")
        want = hashlib.sha256(open(b, "rb").read()).hexdigest()[:16]
        prog = ("import sys, os; sys.path.insert(0, %r); import verdict;"
                "sys.exit(verdict.write('probe', verdict.PASS, denominator=1))" % TOOLS)
        r = subprocess.run([sys.executable, "-c", prog, b], cwd=d, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        got = json.load(open(os.path.join(d, "out", "probe.verdict.json")))["inputs"]["board"]
        assert got["sha256_16"] == want and got["from"] == "argv", got


def t_a_gate_that_names_its_own_board_is_left_alone():
    import subprocess, sys, os, json, tempfile
    with tempfile.TemporaryDirectory() as d:
        b = os.path.join(d, "pcb-x.kicad_pcb"); open(b, "wb").write(b"(kicad_pcb)\n")
        prog = ("import sys, os; sys.path.insert(0, %r); import verdict;"
                "sys.exit(verdict.write('probe', verdict.PASS, denominator=1, inputs={'board': 'e5'}))" % TOOLS)
        r = subprocess.run([sys.executable, "-c", prog, b], cwd=d, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        assert json.load(open(os.path.join(d, "out", "probe.verdict.json")))["inputs"]["board"] == "e5"


def t_a_gate_with_no_board_on_its_command_line_names_none():
    import subprocess, sys, os, json, tempfile
    with tempfile.TemporaryDirectory() as d:
        prog = ("import sys, os; sys.path.insert(0, %r); import verdict;"
                "sys.exit(verdict.write('probe', verdict.PASS, denominator=1))" % TOOLS)
        r = subprocess.run([sys.executable, "-c", prog, "--json"], cwd=d, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        assert "board" not in json.load(open(os.path.join(d, "out", "probe.verdict.json")))["inputs"]


def t_a_gate_that_judges_a_pair_of_boards_names_neither_as_the_board():
    """board_diff compares two boards. Recording its first argument as "the board" would attribute a
    comparison to half of what it judged, so it says `board: None` and the command line is not read."""
    import subprocess, sys, os, json, tempfile
    with tempfile.TemporaryDirectory() as d:
        b = os.path.join(d, "pcb-x.kicad_pcb"); open(b, "wb").write(b"(kicad_pcb)\n")
        prog = ("import sys, os; sys.path.insert(0, %r); import verdict;"
                "sys.exit(verdict.write('probe', verdict.PASS, denominator=1, inputs={'a': 'x', 'board': None}))" % TOOLS)
        r = subprocess.run([sys.executable, "-c", prog, b], cwd=d, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        ins = json.load(open(os.path.join(d, "out", "probe.verdict.json")))["inputs"]
        assert ins["board"] is None, ins


# ---------------------------------------------------------------------------------------------------------
# A READING TAKEN WITH LESS INPUT NEVER REPLACES ONE TAKEN WITH MORE, held once for every tool
# (17 September 2026).
#
# This project has re-learnt that sentence five times: the cross-board contracts at both ends, the rotation
# table, the energy chain, the placement carry, and `doc_provenance`, whose reading taken in a sweep tree that
# holds no `v2/release/revA/order/` at all (0 documents of 0 folders) was forty minutes newer than the runner's
# reading of the seven real ones and stood in front of it on boards D, E, E5 and P. Those four boards read
# "nobody has checked" about documents that are on this disk, untraceable. The declaration is a field of the
# verdict now, and the reader prefers the verdict that HAD its input whatever the timestamps say.

def t_a_verdict_that_declares_its_input_absent_is_inconclusive_whatever_the_tool_said():
    import subprocess, sys, os, json, tempfile
    with tempfile.TemporaryDirectory() as d:
        prog = ("import sys; sys.path.insert(0, %r); import verdict;"
                "sys.exit(verdict.write('probe', verdict.PASS, denominator=0,"
                "                       missing_input='there is no rotation table in this tree'))" % TOOLS)
        r = subprocess.run([sys.executable, "-c", prog], cwd=d, capture_output=True, text=True)
        assert r.returncode == 3, (r.returncode, r.stdout, r.stderr)   # 3 is INCONCLUSIVE
        rec = json.load(open(os.path.join(d, "out", "probe.verdict.json")))
        assert rec["verdict"] == "INCONCLUSIVE", rec["verdict"]
        assert "rotation table" in (rec.get("missing_input") or ""), rec.get("missing_input")


def t_a_verdict_that_had_its_input_says_so_by_carrying_no_declaration():
    import subprocess, sys, os, json, tempfile
    with tempfile.TemporaryDirectory() as d:
        prog = ("import sys; sys.path.insert(0, %r); import verdict;"
                "sys.exit(verdict.write('probe', verdict.FAIL, denominator=7))" % TOOLS)
        r = subprocess.run([sys.executable, "-c", prog], cwd=d, capture_output=True, text=True)
        assert r.returncode == 1, r.stderr
        rec = json.load(open(os.path.join(d, "out", "probe.verdict.json")))
        assert rec["missing_input"] is None, rec["missing_input"]


def t_the_reading_that_had_its_input_is_the_board_s_reading():
    """Executed on the shape that caused it: the empty one is newer, and the one that read the seven documents
    is the one this board is judged on. On the tree before this change the newer empty verdict won."""
    import sys, os, json, tempfile
    sys.path.insert(0, TOOLS)
    import rules_status as S
    rich = {"tool": "doc_provenance", "verdict": "FAIL", "denominator": 7, "ts": "2026-09-17T01:59:12Z",
            "counts": {"documents": 7, "untraceable": 7}}
    empty = {"tool": "doc_provenance", "verdict": "INCONCLUSIVE", "denominator": 0, "ts": "2026-09-17T03:28:03Z",
             "counts": {"documents": 0}, "missing_input": "this tree holds no order folder"}
    assert S._supersedes(rich, empty) is True, "the reading with the documents does not displace the empty one"
    assert S._supersedes(empty, rich) is False, "an empty reading still displaces one taken with the input"
    # and the ordinary case is untouched: between two readings that both had their input, the newer wins
    newer = dict(rich, ts="2026-09-17T04:00:00Z", verdict="PASS")
    assert S._supersedes(newer, rich) is True and S._supersedes(rich, newer) is False

    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "one"), os.path.join(d, "two")
        os.makedirs(a); os.makedirs(b)
        json.dump(rich, open(os.path.join(a, "doc_provenance.verdict.json"), "w"))
        json.dump(empty, open(os.path.join(b, "doc_provenance.verdict.json"), "w"))
        _orig = S._project_dirs
        try:
            S._project_dirs = lambda letter, m: [a, b]
            got = S._verdicts("d", {"boards": {"d": {}}})["doc_provenance"]
        finally:
            S._project_dirs = _orig
        assert got["denominator"] == 7, got


def t_the_two_tools_that_can_run_without_their_input_declare_it():
    """Static, and specific: these are the two gates whose input is a file the ECAD tree does not contain, so
    they are the two that run in a sweep tree and read nothing."""
    import os
    for name, word in (("doc_provenance.py", "order folder"), ("assembly_set.py", "rotation table")):
        src = open(os.path.join(TOOLS, name), encoding="utf-8").read()
        assert "missing_input=" in src, "%s does not declare an absent input" % name
        assert word in src, "%s does not say which input was absent" % name


def t_a_gate_given_a_netlist_names_the_board_whose_netlist_it_is():
    """derate, clock_check and power_sequence judge the netlist and never the board file, so argv carries no
    .kicad_pcb and twenty-three verdicts on this disk name no board at all. One of them sits in the set-level
    out/ that every board reads, taken on board A's netlist, and only a timestamp keeps it from answering for
    another board."""
    import subprocess, sys, os, json, tempfile
    with tempfile.TemporaryDirectory() as d:
        n = os.path.join(d, "pcb-a-power.net"); open(n, "w").write("(export)\n")
        prog = ("import sys; sys.path.insert(0, %r); import verdict;"
                "sys.exit(verdict.write('probe', verdict.PASS, denominator=1, inputs={'netlist': 'x'}))" % TOOLS)
        r = subprocess.run([sys.executable, "-c", prog, n], cwd=d, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        assert json.load(open(os.path.join(d, "out", "probe.verdict.json")))["inputs"]["board"] == "a"


def t_a_netlist_no_board_table_names_leaves_the_board_unnamed():
    """The letter comes from the board tables, never from the file name's shape: an unknown stem names no
    board rather than inventing one."""
    import subprocess, sys, os, json, tempfile
    with tempfile.TemporaryDirectory() as d:
        n = os.path.join(d, "something-else.net"); open(n, "w").write("(export)\n")
        prog = ("import sys; sys.path.insert(0, %r); import verdict;"
                "sys.exit(verdict.write('probe', verdict.PASS, denominator=1, inputs={'netlist': 'x'}))" % TOOLS)
        r = subprocess.run([sys.executable, "-c", prog, n], cwd=d, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        assert "board" not in json.load(open(os.path.join(d, "out", "probe.verdict.json")))["inputs"]


def t_a_gate_given_the_board_s_stem_names_it():
    """`verify_deliverable` takes a deliverable folder and the board's NAME, `pcb-c-display`, which is what
    `boardtable.letter_for` resolves. It decides DFM-001, which is per board, and it named none: three gates
    were board-specific and anonymous on this disk after the 17 September sweep, and this is the last of the
    three (hardset takes --board <file>, emc_sheet takes --board <letter>, this one takes the stem)."""
    import subprocess, sys, os, json, tempfile
    with tempfile.TemporaryDirectory() as d:
        prog = ("import sys; sys.path.insert(0, %r); import verdict;"
                "sys.exit(verdict.write('probe', verdict.PASS, denominator=1, inputs={'folder': 'x'}))" % TOOLS)
        r = subprocess.run([sys.executable, "-c", prog, "/some/meshsat-pcb-c-revA-C24", "pcb-c-display", "6"],
                           cwd=d, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        assert json.load(open(os.path.join(d, "out", "probe.verdict.json")))["inputs"]["board"] == "c"


def t_a_word_that_is_not_a_board_stem_names_no_board():
    import subprocess, sys, os, json, tempfile
    with tempfile.TemporaryDirectory() as d:
        prog = ("import sys; sys.path.insert(0, %r); import verdict;"
                "sys.exit(verdict.write('probe', verdict.PASS, denominator=1, inputs={'folder': 'x'}))" % TOOLS)
        r = subprocess.run([sys.executable, "-c", prog, "something", "else", "6"], cwd=d,
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        assert "board" not in json.load(open(os.path.join(d, "out", "probe.verdict.json")))["inputs"]


def t_a_tool_whose_main_is_guarded_imports_the_writer_where_main_can_see_it():
    """THE GUARD THAT COULD NOT RUN (18 September 2026, found by running the tool rather than by reading it).

    This morning's change wrapped twenty deciding gates as `sys.exit(_v.guard("<tool>", main, sys.argv[1:]))`, so
    that a gate which raises leaves INCONCLUSIVE naming the exception instead of no verdict at all. In
    `ref_change.py` the writer was imported INSIDE main, in the branch that writes the verdict, so the guard line
    itself raised `NameError: name '_v' is not defined` before main was ever called: the one tool of the twenty
    that could not start, and the thing meant to leave a reading when a tool fails left none when it was the one
    failing. Rule RET-003's gate had been dead in every sweep since. It is the same shape as the fallback nested
    inside the try of the thing it guards (13 September): a guard that depends on the code it is guarding."""
    for name in sorted(os.path.basename(p) for p in glob.glob(os.path.join(TOOLS, "*.py"))):
        src = open(os.path.join(TOOLS, name), errors="replace").read()
        if "_v.guard(" not in src: continue
        head = src.split('if __name__ ==')[0]
        # ANCHORED AT COLUMN ZERO, because the defect IS an indented import: the first version of this rule
        # allowed leading whitespace and passed on the very file it was written for, where the writer is
        # imported inside main. A rule that passes on the tree it was written against is worse than none.
        assert re.search(r"^import verdict as _v", head, re.M), \
            "%s guards its main with _v.guard and imports the writer somewhere main cannot be reached from" % name


def t_a_guarded_main_is_given_the_function_and_the_argv_and_never_a_lambda():
    """`verdict.guard` CALLS its function with argv (`return fn(argv)`), so a zero-argument lambda raises the
    moment the tool runs, and the guard then turns that TypeError into an INCONCLUSIVE verdict about nothing.

    19 September 2026: `rail_barrels.py` shipped as `_v.guard("rail_barrels", lambda: main(sys.argv[1:]),
    sys.argv[1:])`, compiled, passed thirteen of its own rules on the runner, and crashed on all three boards
    the first time it met one, writing "the gate raised before it decided: TypeError". The guard behaved
    correctly and the reading was still worthless. The house form is `_v.guard("<tool>", main, sys.argv[1:])`,
    which is what the other twenty-odd gates carry, and it is checkable here rather than on a rented box."""
    import re
    bad = []
    for name in sorted(os.listdir(TOOLS)):
        if not name.endswith(".py"): continue
        src = open(os.path.join(TOOLS, name), encoding="utf-8").read()
        for m in re.finditer(r"guard\(\s*(\"[^\"]+\"|'[^']+')\s*,\s*([^,]+),", src):
            fn = m.group(2).strip()
            if "lambda" in fn or "(" in fn:
                bad.append("%s: guard's second argument is %r, not a bare function" % (name, fn[:60]))
    assert not bad, bad
