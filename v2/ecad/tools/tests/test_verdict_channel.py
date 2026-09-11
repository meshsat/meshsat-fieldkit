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
         "check_pcb_p.py", "hardset.py", "impedance_check.py", "dc_drop.py", "check_contracts.py",
         "check_zone_nets.py", "intent_checks.py", "place_audit.py", "erc_gate.py",
         "verify_deliverable.py", "pruned_gate.py", "lcsc_fill.py"]

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
