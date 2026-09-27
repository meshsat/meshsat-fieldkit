#!/usr/bin/env python3
"""The agent loop's decision, executed for every state (15 September 2026, red team report 1 P0): the runner's exit
status and the row count decide completeness before anything is graded; ILLEGAL is not measured; the cycle's verdict
is the arms' verdict and the review is a count."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agent"))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import loop, verdict

R = lambda n, v: {"arm": n, "verdict": v, "pairs": 10}   # the runner's rows carry the name as "arm" (the first live cycle read every row as absent)
APPROVE = {"verdict": "APPROVE"}; REFUSE = {"verdict": "REFUSE"}


def t_a_runner_that_did_not_run_to_a_verdict_is_incomplete_whatever_rows_exist():
    inc = loop.incomplete([R("a", "MET"), R("b", "MET")], {"a", "b"}, rc=2)
    assert inc and inc["counts"]["infra_fail"] == 1 and "exited 2" in inc["why"]
    inc = loop.incomplete([R("a", "MET"), R("b", "MET")], {"a", "b"}, rc=-9)
    assert inc and inc["counts"]["infra_fail"] == 1


def t_the_runners_fail_verdict_over_a_complete_row_set_is_the_rows_business():
    """arms.py exits 1 when no row is legal (an all-ILLEGAL set): the rows carry that and the cycle is complete."""
    assert loop.incomplete([R("a", "ILLEGAL")], {"a"}, rc=1) is None


def t_fewer_rows_than_arms_is_incomplete():
    inc = loop.incomplete([R("a", "MET")], {"a", "b", "c"}, rc=0)
    assert inc and inc["counts"]["absent"] == 2 and "absent: b" in inc["evidence"]


def t_a_duplicate_row_is_incomplete():
    inc = loop.incomplete([R("a", "MET"), R("a", "MISSED")], {"a"}, rc=0)
    assert inc and inc["counts"]["duplicate"] == 1


def t_one_row_per_arm_and_exit_zero_is_complete():
    assert loop.incomplete([R("a", "MET"), R("b", "MISSED")], {"a", "b"}, rc=0) is None


def t_an_all_illegal_set_is_inconclusive_never_pass():
    res, g, bad, refused = loop.cycle_result([R("a", "ILLEGAL"), R("b", "ILLEGAL")], APPROVE, False)
    assert res == verdict.INCONCLUSIVE and bad == 2


def t_a_mixed_legal_and_illegal_set_is_inconclusive():
    res, g, bad, refused = loop.cycle_result([R("a", "MET"), R("b", "ILLEGAL")], APPROVE, False)
    assert res == verdict.INCONCLUSIVE


def t_every_prediction_met_is_pass_and_a_missed_one_is_fail():
    assert loop.cycle_result([R("a", "MET"), R("b", "MET")], APPROVE, False)[0] == verdict.PASS
    assert loop.cycle_result([R("a", "MET"), R("b", "MISSED")], APPROVE, False)[0] == verdict.FAIL


def t_the_review_is_a_count_not_the_grade():
    res, g, bad, refused = loop.cycle_result([R("a", "MET")], REFUSE, False)
    assert res == verdict.PASS and refused, "a refused write-up must be recorded, not turn a met prediction into FAIL"
    res, g, bad, refused = loop.cycle_result([R("a", "MET")], None, False)
    assert res == verdict.INCONCLUSIVE, "no review at all leaves the cycle unjudged"


def t_the_reviewer_is_handed_only_this_cycles_verdicts():
    """Tier 2b found it on the fourth live cycle (15 September 2026): the previous cycle's agent_loop.verdict.json was in
    the material and the reviewer judged a gate file grading another arm."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agent", "loop.py"), errors="replace").read()
    assert 'not f.startswith("agent_loop")' in src, "the loop's own verdict is handed to the reviewer as material"
    assert 'rec.get("ts", "")' in src, "a verdict written before this cycle is handed to the reviewer as material"
