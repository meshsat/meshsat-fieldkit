"""The decision rules of the computed board status (MESHSAT-862, 16 September 2026).

Executed against synthetic verdicts, never against source text: each case builds a world (a registry, a
coverage map, a manifest and a set of verdict records) and asserts the result the computation must reach.
The property under test throughout is ABSENCE IS NEVER A PASS: a missing verdict, a verdict older than the
evidence epoch, a verdict taken under another rule set, a rule with no implementation and a rule whose
authority is unverified all come out INCONCLUSIVE, and an inconclusive blocker keeps the set out of
READY_FOR_PROTOTYPE.
"""
import os, sys, json, copy, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rules_status as S
import rules_lib as R

EPOCH = "2026-09-16T00:35:00+02:00"
FP = "fingerprint0000"


def _manifest(frozen=False):
    return {"manifest_version": "test", "boards": {"x": {"project": "pcb-x", "required": True}},
            "promotion": {"frozen": frozen}, "evidence": {"epoch": EPOCH}}


def _rule(rid="R-1", effect="BLOCKER", phase="ROUTED_BOARD"):
    return {"id": rid, "domain": "ROUTING", "short_name": "n", "requirement": "r", "classification": "PROJECT_DECISION",
            "applicability": "UNIVERSAL_FOR_THIS_PROJECT", "risk_class": ["FABRICATION"], "release_effect": effect,
            "source_status": "NOT_REQUIRED_FOR_PROJECT_DECISION", "sources": [], "acceptance_criteria": "a",
            "rationale": "b", "failure_mode": "c", "verification_method": ["SCRIPT"], "verification_phase": phase,
            "automation_feasibility": "AUTOMATABLE", "boards_affected": ["ALL"], "interfaces_affected": ["NONE"],
            "implementation_location": "x.py", "evidence_scope": ["board_sha256"], "owner": "SESSION",
            "waiver_policy": {"allowed": False}, "maturity": "ENFORCED"}


def _verdict(result="PASS", ts="2026-09-16T01:00:00Z", fp=FP):
    rec = {"tool": "gate_x", "ts": ts, "verdict": result, "denominator": 10, "counts": {"fail": 0}}
    if fp: rec["policy"] = {"rule_set_fingerprint": fp}
    return {"gate_x": rec}


def _cov(maturity="ENFORCED", verdict_name="gate_x", waiver=None):
    c = {"R-1": {"implementation": "x.py", "verification": {"tool": "x.py", "verdict": verdict_name},
                 "maturity": maturity}}
    if waiver: c["R-1"]["waiver"] = waiver
    return c


def _result(cov, vs, m=None, rule=None, phase=None):
    return S.result_for(rule or _rule(), "x", cov, vs, m or _manifest(), FP, phase)["result"]


def t_a_current_pass_is_a_pass():
    assert _result(_cov(), _verdict("PASS")) == S.PASS


def t_a_fail_is_a_fail():
    assert _result(_cov(), _verdict("FAIL")) == S.FAIL


def t_a_missing_verdict_is_inconclusive_and_never_a_pass():
    assert _result(_cov(), {}) == S.INCONCLUSIVE


def t_a_verdict_older_than_the_evidence_epoch_is_inconclusive():
    """The whole point of the epoch: a board that passed under an unversioned rule set has history, not evidence."""
    assert _result(_cov(), _verdict("PASS", ts="2026-09-15T20:00:00Z")) == S.INCONCLUSIVE


def t_a_verdict_under_another_rule_set_is_inconclusive():
    assert _result(_cov(), _verdict("PASS", fp="somethingelse")) == S.INCONCLUSIVE


def t_a_verdict_that_does_not_name_its_rule_set_is_inconclusive():
    assert _result(_cov(), _verdict("PASS", fp=None)) == S.INCONCLUSIVE


def t_a_rule_with_no_implementation_is_inconclusive():
    for maturity in ("OPEN", "DOCUMENTED_ONLY", "GENERATED_ONLY", "SOURCE_UNVERIFIED", "OWNER_DECISION_REQUIRED"):
        assert _result(_cov(maturity), _verdict("PASS")) == S.INCONCLUSIVE, maturity


def t_a_waiver_is_waived_and_is_not_a_pass():
    w = {"active": True, "authority": "OWNER", "expiry": "2026-10-01", "reason": "measured", "evidence": "e"}
    assert _result(_cov(waiver=w), {}) == S.WAIVED
    rows = [dict(result=S.WAIVED, release_effect="BLOCKER", verification_phase="ROUTED_BOARD")]
    c = S.counts(rows)
    assert c["PASS"] == 0 and c["WAIVED"] == 1, c


def t_the_four_percentages_share_one_denominator_and_sum_to_a_hundred():
    rows = ([dict(result=S.PASS, release_effect="BLOCKER", verification_phase="ROUTED_BOARD")] * 3
            + [dict(result=S.FAIL, release_effect="BLOCKER", verification_phase="ROUTED_BOARD")]
            + [dict(result=S.INCONCLUSIVE, release_effect="MUST_JUSTIFY", verification_phase="ROUTED_BOARD")] * 4
            + [dict(result=S.WAIVED, release_effect="BLOCKER", verification_phase="ROUTED_BOARD")] * 2
            + [dict(result=S.NOT_APPLICABLE, release_effect="BLOCKER", verification_phase="PROTOTYPE")])
    c = S.counts(rows)
    assert c["denominator"] == 10, c
    total = c["pass_percent"] + c["fail_percent"] + c["inconclusive_percent"] + c["waived_percent"]
    assert abs(total - 100.0) < 0.5, total


def t_the_gate_state_is_the_worst_blocker_and_a_waiver_shows():
    m = _manifest()
    ok = [dict(result=S.PASS, release_effect="BLOCKER", verification_phase="ROUTED_BOARD")]
    assert S.gate_state(ok, m) == "READY_FOR_PROTOTYPE"
    assert S.gate_state(ok + [dict(result=S.INCONCLUSIVE, release_effect="BLOCKER", verification_phase="ROUTED_BOARD")], m) == "INCONCLUSIVE"
    assert S.gate_state(ok + [dict(result=S.FAIL, release_effect="BLOCKER", verification_phase="ROUTED_BOARD")], m) == "NOT_READY"
    assert S.gate_state(ok + [dict(result=S.WAIVED, release_effect="BLOCKER", verification_phase="ROUTED_BOARD")], m).endswith("WITH_WAIVERS")


def t_a_failure_beats_an_inconclusive():
    m = _manifest()
    rows = [dict(result=S.INCONCLUSIVE, release_effect="BLOCKER", verification_phase="ROUTED_BOARD"),
            dict(result=S.FAIL, release_effect="BLOCKER", verification_phase="ROUTED_BOARD")]
    assert S.gate_state(rows, m) == "NOT_READY"


def t_a_frozen_promotion_cannot_report_ready():
    """The freeze is the owner's instruction of 16 September: pre-audit evidence is not promoted. It must not be
    possible for a green board to read READY while the freeze is on."""
    ok = [dict(result=S.PASS, release_effect="BLOCKER", verification_phase="ROUTED_BOARD")]
    assert S.gate_state(ok, _manifest(frozen=True)) == "INCONCLUSIVE"


def t_a_later_phase_rule_is_not_applicable_to_an_earlier_phase_report():
    r = _rule(phase="PROTOTYPE")
    assert _result(_cov(), _verdict("PASS"), rule=r, phase="ROUTED_BOARD") == S.NOT_APPLICABLE


def t_the_committed_registry_and_coverage_compute_for_every_board():
    """The real registry, the real coverage map, the real manifest: every board computes, and nothing throws."""
    m = S.manifest(); reg = R.load(); cov = S.coverage()
    for letter in m["boards"]:
        st = S.board_status(letter, reg, R.facts(), cov, m, R.fingerprint(reg))
        assert st["rows"], letter
        for row in st["rows"]:
            assert row["result"] in R.RESULTS, row


def t_a_manual_verification_whose_record_is_a_generated_page_is_judged_by_rebuilding_it():
    """SGN-002 and every rule like it. The evidence for a manually verified rule is a RECORD, and the record
    here is a page generated from the registry. It counts as evidence only while it still matches the registry:
    a hand edit, a rule added after the page was last written, or a deleted row all read INCONCLUSIVE, because
    a list of prototype unknowns that has quietly shrunk looks exactly like a list that is complete.
    """
    doc = os.path.join(S.ECAD, "..", "docs", "PCB-PROTOTYPE-UNKNOWNS.md")   # the tool's own resolution, not a second copy of it
    S._DOC_CACHE.clear()
    ok, why = S._document_current("docs/PCB-PROTOTYPE-UNKNOWNS.md")
    assert ok, "the generated record does not match the registry: %s" % why

    original = open(doc).read()
    try:
        open(doc, "w").write(original.replace("| rule | what is unknown", "| rule | what is KNOWN", 1))
        S._DOC_CACHE.clear()
        ok2, why2 = S._document_current("docs/PCB-PROTOTYPE-UNKNOWNS.md")
        assert not ok2, "a hand-edited record still counted as evidence"
        cov = _cov("VERIFIED_MANUALLY"); cov["R-1"]["verification"] = {"tool": "rules_render.py", "document": "docs/PCB-PROTOTYPE-UNKNOWNS.md"}
        assert _result(cov, {}) == S.INCONCLUSIVE, "a stale record passed the rule it is the evidence for"
    finally:
        open(doc, "w").write(original)
        S._DOC_CACHE.clear()


def t_a_manual_verification_with_no_record_is_never_a_pass():
    cov = _cov("VERIFIED_MANUALLY"); cov["R-1"]["verification"] = {"tool": "a person reads it"}
    assert _result(cov, _verdict("PASS")) == S.INCONCLUSIVE, \
        "a rule claiming manual verification with no record to point at read as verified"


def t_the_completeness_verdict_asks_a_different_question_from_readiness():
    """SGN-001. rules_status says whether the boards pass; rules_complete says whether every rule that applies
    to a board reached one of the five results AT ALL. The second is the property the registry exists for and
    the one that would otherwise be invisible, because a rule missing from the table looks exactly like a rule
    that does not apply. Executed: run the computation into a temporary directory and read both verdicts back.
    """
    import subprocess, glob
    d = tempfile.mkdtemp(prefix="rules-complete-")
    ecad = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    p = subprocess.run([sys.executable, os.path.join(ecad, "tools", "rules_status.py"), "--out-dir", d],
                       cwd=ecad, capture_output=True, text=True, timeout=600)
    assert p.returncode in (0, 1, 3), p.stdout[-400:] + p.stderr[-400:]
    rec = json.load(open(os.path.join(ecad, "out", "rules_complete.verdict.json")))
    assert rec["verdict"] == "PASS", "a rule that applies to a board reached no result: %s" % rec.get("evidence")
    assert rec["denominator"] > 0 and rec["counts"]["unresolved"] == 0, rec
    # and it is NOT the readiness verdict: the set is not ready today, and completeness still passes
    rs = json.load(open(os.path.join(d, "rules_status.verdict.json")))
    assert rs["verdict"] != rec["verdict"], \
        "the completeness verdict is tracking the readiness verdict, so it is asking the same question"


def t_every_board_in_the_manifest_can_be_named_by_the_sweep():
    """A board the sweep cannot name is a board the readiness cannot re-judge (MESHSAT-862, 16 September 2026).

    Board E5 has no `boards/e5.json`, because it is a bare contact interposer generated from board A's own board
    file: no schematic, no netlist, no routed copper, so it never needed a chain. The sweep resolved a board's
    name through that file alone and stopped at "no board .kicad_pcb", so all twenty of E5's applicable
    rule-board pairs stayed INCONCLUSIVE for a reason that was about the script. The name now falls back to the
    registry's own applicability data, which has carried `project: pcb-e5-block` since Phase A."""
    import os, sys, json
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, here)
    import rules_lib
    facts = rules_lib.board_facts()
    m = json.load(open(os.path.join(here, "readiness_manifest.json"), encoding="utf-8"))
    for letter in m["boards"]:
        tbl = os.path.join(here, "boards", "%s.json" % letter)
        if os.path.exists(tbl):
            assert json.load(open(tbl, encoding="utf-8")).get("name"), "%s's board table carries no name" % letter
            continue
        assert (facts.get(letter) or {}).get("project"), \
            "board %s has neither a board table nor a project in the facts, so no sweep can name it" % letter
    src = open(os.path.join(here, "gate_sweep.sh"), encoding="utf-8").read()
    assert "board_facts()" in src, "the sweep no longer falls back to the registry's facts for a board with no table"


def t_a_verdict_taken_on_another_board_is_not_this_board_s_evidence():
    """A verdict says which board it was taken on and nothing compared it with the board being judged.

    Found by measurement on 16 September 2026: the SET-LEVEL out/, which every board's status reads, held a
    `fab_limits` verdict carrying board A's sha and a `port_protect` verdict naming board E. Only their
    timestamps kept each board's own sweep winning. Identity does not depend on who wrote a file where.

    The check costs nothing on the tree it was added to: every one of the 145 committed verdicts that names a
    board names the board it sits beside. It exists so that the day one does not, it says so.
    """
    ident = {"x", "abc123def456aaaa"}
    vs = _verdict("PASS"); vs["gate_x"]["inputs"] = {"board": {"path": "b.kicad_pcb", "sha256_16": "abc123def456aaaa"}}
    assert S.result_for(_rule(), "x", _cov(), vs, _manifest(), FP, None, ident)["result"] == S.PASS

    other = _verdict("PASS"); other["gate_x"]["inputs"] = {"board": {"path": "b.kicad_pcb", "sha256_16": "0000deadbeef0000"}}
    r = S.result_for(_rule(), "x", _cov(), other, _manifest(), FP, None, ident)
    assert r["result"] == S.INCONCLUSIVE, r
    assert "not a board this project directory holds" in r["why"], r["why"]

    byletter = _verdict("PASS"); byletter["gate_x"]["inputs"] = {"board": "y"}
    assert S.result_for(_rule(), "x", _cov(), byletter, _manifest(), FP, None, ident)["result"] == S.INCONCLUSIVE

    # a verdict that names no board at all is judged on its other properties, as the netlist gates are
    assert S.result_for(_rule(), "x", _cov(), _verdict("PASS"), _manifest(), FP, None, ident)["result"] == S.PASS


def t_a_dependency_cycle_is_refused_and_not_absorbed():
    """DEFECTIVE fixture: a register with a cycle must RAISE. ACCEPTABLE fixture: an acyclic one returns.

    `critical_path`'s walk carries a seen-set, which keeps it from recursing for ever and also makes a cycle
    invisible: the path is computed by silently truncating one of the two edges, and nothing says which was
    dropped or that the number is short. The register held two such cycles on 16 September 2026, RET-001
    against SI-001 and BAT-002 against PWR-003, while the critical path they produced was being reported to
    the owner every ten minutes. Breaking both moved it from 26 h to 22 h at P50.

    A number computed through a cycle is not a duration, so it is refused rather than returned.
    """
    import rules_eta as E

    acyclic = [{"rule": "A", "depends_on": [], "p50": 2.0, "p80": 4.0},
               {"rule": "B", "depends_on": ["A"], "p50": 3.0, "p80": 6.0}]
    assert E.cycles(acyclic) == [], "an acyclic register was reported as cyclic"
    assert E.critical_path(acyclic, "p50") == 5.0, "the chain A then B is not two plus three"

    cyclic = [{"rule": "A", "depends_on": ["B"], "p50": 2.0, "p80": 4.0},
              {"rule": "B", "depends_on": ["A"], "p50": 3.0, "p80": 6.0}]
    found = E.cycles(cyclic)
    assert found, "a two-rule cycle was not detected"
    assert set(found[0]) >= {"A", "B"}, found
    try:
        E.critical_path(cyclic, "p50")
    except ValueError as e:
        assert "cycle" in str(e), e
    else:
        raise AssertionError("a critical path was returned through a cycle, which is not a duration")

    # and the committed register must itself be acyclic, or the reported ETA is short by an unknown amount
    assert E.cycles(E.open_items()) == [], "the committed gap register has a dependency cycle"


def _route_gate(unrouted, ts="2026-09-16T01:00:00Z"):
    return {S.ROUTE_GATE: {"tool": S.ROUTE_GATE, "ts": ts, "verdict": "FAIL" if unrouted else "PASS",
                           "denominator": 15, "counts": {"hard": 0, "unrouted": unrouted},
                           "policy": {"rule_set_fingerprint": FP}}}


def t_a_routed_board_rule_on_a_board_that_is_not_routed_is_inconclusive_and_not_a_failure():
    """Board B, 17 September 2026. The board committed in its phase directory while the route runs is the
    PLACED one: 499 connections open and all six zones carrying zero filled area, because the fill happens in
    the finish. Judged against it the return-path rule read 214 nets of 566 without a reference (the same tool
    on the same board with the zones filled in memory reads ONE net over, by 0.6 mm), the return-via rule read
    204 signal vias without a ground via, and the via-current rule read 19 rails over their barrels. None of
    that is a property of the design; it is what a board looks like before it is finished.

    Prematurity is not failure, and it is not a pass either: the rule is INCONCLUSIVE, which still blocks."""
    vs = dict(_verdict("FAIL")); vs.update(_route_gate(499))
    assert _result(_cov(), vs) == S.INCONCLUSIVE, "a routed-board rule failed on a board that is not routed"


def t_the_same_rule_on_a_routed_board_still_fails():
    """The guard must not become an exemption: with nothing unrouted the failure stands."""
    vs = dict(_verdict("FAIL")); vs.update(_route_gate(0))
    assert _result(_cov(), vs) == S.FAIL, "the guard swallowed a real failure on a routed board"


def t_the_rule_that_measures_the_route_itself_keeps_its_result():
    """RTE-001 and RTE-002 read the routed-board gate as their own verdict, and 'nothing unrouted' is exactly
    what they are there to say: if they went INCONCLUSIVE on an unrouted board, no board could ever fail them.
    """
    cov = {"R-1": {"implementation": "hardset.py",
                   "verification": {"tool": "hardset.py", "verdict": S.ROUTE_GATE}, "maturity": "ENFORCED"}}
    assert _result(cov, _route_gate(499)) == S.FAIL


def t_a_rule_verified_before_the_route_is_untouched_by_an_unrouted_board():
    vs = dict(_verdict("FAIL")); vs.update(_route_gate(499))
    assert _result(_cov(), vs, rule=_rule(phase="PLACED_BOARD")) == S.FAIL
    assert _result(_cov(), vs, rule=_rule(phase="SCHEMATIC")) == S.FAIL


def t_a_run_about_one_board_does_not_write_the_set_s_completeness_verdict():
    """SGN-001 IS A SET-LEVEL QUESTION AND A SCOPED RUN CANNOT ANSWER IT (17 September 2026).

    `rules_status.py --board p` judges one board's forty-two pairs, and it used to write the SET-LEVEL
    `rules_complete` verdict from them, denominator and all, on top of the reading taken over all 301. SGN-001
    is a BLOCKER on every one of the seven boards and every board's generated page reads that one file, so a
    single scoped run made six boards claim a completeness check that had looked at one board: the pages read
    `rules_complete PASS of 42`. This is the `missing_input` doctrine one level up, and the honest answer is
    to take no reading at all rather than a narrower one.

    Executed: record the set-level verdict, run a scoped computation, and require the file to be untouched.
    """
    import subprocess, shutil
    ecad = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    setlevel = os.path.join(ecad, "out", "rules_complete.verdict.json")
    if not os.path.exists(setlevel):
        return "no set-level completeness verdict on this tree to protect"
    before = open(setlevel, "rb").read()
    keep = tempfile.mkdtemp(prefix="rules-scoped-")
    shutil.copy(setlevel, os.path.join(keep, "rules_complete.verdict.json"))
    letter = sorted(S.manifest()["boards"])[0]
    try:
        p = subprocess.run([sys.executable, os.path.join(ecad, "tools", "rules_status.py"),
                            "--board", letter, "--out-dir", keep],
                           cwd=ecad, capture_output=True, text=True, timeout=900)
        assert p.returncode in (0, 1, 3), p.stdout[-400:] + p.stderr[-400:]
        after = open(setlevel, "rb").read()
        if after != before:
            # put the full reading back before failing: a test must not leave the tree worse than it found it
            shutil.copy(os.path.join(keep, "rules_complete.verdict.json"), setlevel)
            rec = json.loads(after.decode("utf-8"))
            raise AssertionError("a run about board %s rewrote the SET's completeness verdict "
                                 "(denominator %s, counts %s): a reading taken with less input never replaces "
                                 "one taken with more" % (letter, rec.get("denominator"), rec.get("counts")))
        assert "NOT written" in p.stdout, \
            "the scoped run left the verdict alone and did not say so, which reads as though it had checked the set"
    finally:
        shutil.rmtree(keep, ignore_errors=True)


def t_a_verdict_under_an_older_rule_set_does_not_stand_in_front_of_a_current_one():
    """HISTORY NEVER STANDS IN FRONT OF A CURRENT READING (17 September 2026).

    `_supersedes` protects a reading that HAD its input from being replaced by one that declares its input
    absent, which is this project's own rule. On 17 September it protected a STALE one: board A's parts were
    last certified under rule set 8087c341, before that morning's applicability correction, and from the folder
    of a board this tree does not hold; the fresh reading says so with `missing_input` and was refused for
    saying it, so six rule-board pairs read "taken under rule set 8087c341" where the true reason is "there is
    no deliverable folder at the declared phase".

    A verdict taken under a superseded rule set is not evidence at all, since `_fresh` refuses it wherever it
    is read, so it cannot be the thing that keeps a current reading out. Fingerprint first, then input.
    """
    import copy
    old = {"tool": "t", "ts": "2026-09-17T00:00:00Z", "verdict": "PASS", "denominator": 9,
           "policy": {"rule_set_fingerprint": "an_older_one"}}
    new = {"tool": "t", "ts": "2026-09-17T12:00:00Z", "verdict": "INCONCLUSIVE", "denominator": 0,
           "missing_input": "no deliverable folder at the declared phase",
           "policy": {"rule_set_fingerprint": S._fingerprint_now()}}
    assert S._supersedes(new, old), \
        "a verdict taken under a superseded rule set kept a current reading out, which is how a board comes to " \
        "report the wrong reason for being inconclusive"
    # and the input rule still binds among readings of the SAME rule set
    same_old = copy.deepcopy(old); same_old["policy"]["rule_set_fingerprint"] = S._fingerprint_now()
    assert not S._supersedes(new, same_old), \
        "a reading that declares its input absent replaced one that had it, under the same rule set"
