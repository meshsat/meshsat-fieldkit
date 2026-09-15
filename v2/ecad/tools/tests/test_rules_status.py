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
