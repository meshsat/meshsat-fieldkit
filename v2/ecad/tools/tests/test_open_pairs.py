"""What an open rule-board pair is waiting on, as rules (MESHSAT-862, 19 September 2026).

The classification exists because the same question was answered by hand four times in three days and two of
those answers disagreed with each other. A hand count is a claim about a register; these are the properties
that claim must have, and each is executed against a synthetic world rather than against the tree, so a route
landing cannot make a rule pass or fail for the wrong reason.
"""
import os, sys, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import open_pairs as O


def _row(rid="R-1", result="INCONCLUSIVE", maturity="ENFORCED", why="because", evidence=None):
    return {"rule": rid, "result": result, "maturity": maturity, "why": why, "evidence": evidence,
            "release_effect": "BLOCKER", "verification_phase": "ROUTED_BOARD"}


def t_a_pair_an_open_decision_claims_is_the_decision_s_whatever_its_maturity_says():
    """RET-001 is SOURCE_UNVERIFIED and decision 39 claims it on six boards. Both statements are true and
    only one of them is an action: the limit's authority cannot be established by this project, and ruling
    39 moves the pair today. The ladder puts the decision first for that reason."""
    claims = {("R-1", "a"): (39, "the criterion a break in a reference is judged against")}
    c = O.classify(_row(maturity="SOURCE_UNVERIFIED"), "a", claims)
    assert c["category"] == O.DECISION and c["decision"] == 39, c
    # the same rule on a board the decision does not name stays the authority's
    c2 = O.classify(_row(maturity="SOURCE_UNVERIFIED"), "b", claims)
    assert c2["category"] == O.AUTHORITY, c2


def t_a_rule_that_says_a_decision_is_open_while_no_decision_claims_it_is_named_as_a_hole():
    """Found on its first run: STK-002 reads "an owner decision is open" on all seven boards and no open
    decision in the register claims it, so a reader following the readiness page could not find out which
    decision. That is a hole in the register, not a state of the board, and it must never be reported in
    the same bucket as a pair whose decision has a number."""
    c = O.classify(_row(maturity="OWNER_DECISION_REQUIRED"), "a", {})
    assert c["category"] == O.DECISION_UNCLAIMED, c
    assert c["decision"] is None, c


def t_a_ruled_or_closed_decision_claims_nothing():
    """A decision's blocks map is history once it is ruled. Reading a closed decision as a live claim would
    park a pair behind a question that was answered days ago, which is the opposite of the register's job."""
    ds = [{"n": 24, "status": "ruled", "title": "t", "blocks": {"R-1": ["a"]}},
          {"n": 31, "status": "closed", "title": "t", "blocks": {"R-2": ["a"]}},
          {"n": 39, "status": "open", "title": "live", "blocks": {"R-3": ["a"]}}]
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as fh:
        import rules_lib as R
        fh.write(R._yaml().safe_dump({"decisions": ds}))
        p = fh.name
    claims = O.decisions(p)
    assert ("R-3", "a") in claims, claims
    assert ("R-1", "a") not in claims and ("R-2", "a") not in claims, claims


def t_a_measured_failure_stays_a_measured_failure_in_every_cut_of_the_table():
    """TRN-001 on three boards is a FAIL and decision 31 claims it. The pair is reported under the decision,
    because the ruling is the action, and it must still be counted among the measured failures: a number
    that changes depending on which way the table is read is how a register stops being believed."""
    claims = {("R-1", "a"): (31, "port protection")}
    c = O.classify(_row(result="FAIL"), "a", claims)
    assert c["category"] == O.DECISION and c["measured"] is True, c
    c2 = O.classify(_row(result="FAIL"), "b", {})
    assert c2["category"] == O.MEASURED_FAILURE and c2["measured"] is True, c2


def t_an_input_the_reading_declared_absent_is_read_from_the_verdict_and_not_from_prose():
    """A reading taken with less input never replaces one taken with more (17 September), and the field that
    says so is `missing_input`. The category comes from that field, never from matching words in a sentence,
    so a gate that rewords its note does not move a pair into another bucket."""
    d = tempfile.mkdtemp(prefix="open-pairs-")
    p = os.path.join(d, "gate.verdict.json")
    with open(p, "w") as fh:
        json.dump({"tool": "gate", "verdict": "INCONCLUSIVE",
                   "missing_input": "no deliverable folder at the declared phase A32"}, fh)
    c = O.classify(_row(evidence=p), "a", {})
    assert c["category"] == O.MISSING_INPUT and "A32" in c["detail"], c
    # the same row with no such verdict beside it is not judged, and says so in the reading's own words
    c2 = O.classify(_row(why="gate INCONCLUSIVE: the ordering session has the only preview"), "a", {})
    assert c2["category"] == O.NOT_JUDGED and "preview" in c2["detail"], c2


def t_a_pair_that_is_not_open_is_never_on_this_page():
    """The page is the register of what is NOT done. A PASS or a rule that does not apply to the board has
    no business on it, and letting either in would make the open count disagree with the readiness count."""
    for result in ("PASS", "NOT_APPLICABLE", "WAIVED"):
        assert O.classify(_row(result=result), "a", {}) is None, result


def t_every_open_pair_of_the_tree_gets_exactly_one_category():
    """Executed against the tree when it holds an audit: the sum of the buckets is the open count, so no
    pair is counted twice and none falls through the ladder without a bucket."""
    from harness import Skip
    res = O.collect()
    if not res["boards"]: raise Skip("this tree holds no rule audit to classify")
    assert sum(res["counts"].values()) == res["open"], res["counts"]
    assert res["measured"] == sum(1 for p in res["pairs"] if p["result"] == "FAIL"), res
    for p in res["pairs"]: assert p["category"] in O.ORDER, p


def t_a_vendor_wait_and_the_ordering_session_s_own_work_are_not_unattributed():
    """THE DEFECTIVE FIXTURE (19 September 2026). Eight pairs sat in "not judged" while the coverage map
    already recorded who executes their remediation: VIA-002 on board P waits on the fabricator publishing
    its annular rows at 2 oz, and DFA-001 on every board waits on the assembler's own 2D preview, which is
    behind a login this repo forbids the runner to use. The ETA has read that field for days. A register whose
    job is to say what is REACHABLE has to say that neither of those is, and it may only do so for a pair the
    ladder above has not already claimed: a measured failure stays a measured failure whoever owns its fix."""
    execs = {"R-1": "VENDOR_OR_STANDARD_WAIT", "R-2": "OWNER", "R-3": "PARALLEL_BOX"}
    assert O.classify(_row("R-1"), "p", {}, execs)["category"] == O.VENDOR_WAIT
    assert O.classify(_row("R-2"), "a", {}, execs)["category"] == O.OWNER_WORK
    assert O.classify(_row("R-3"), "a", {}, execs)["category"] == O.NOT_JUDGED

    # a measured failure keeps its own bucket whoever owns the remediation
    assert O.classify(_row("R-1", result="FAIL"), "p", {}, execs)["category"] == O.MEASURED_FAILURE
    # and so does a pair an open decision claims
    claims = {("R-2", "a"): (34, "the envelope")}
    assert O.classify(_row("R-2"), "a", claims, execs)["category"] == O.DECISION


def t_the_execution_map_is_read_from_the_coverage_map_and_not_from_a_list():
    """The same law the 18 September rule made for the gate catalogue: the register reads the map, so a rule
    whose remediation owner changes moves here without anybody remembering to edit a list."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "open_pairs.py"),
               encoding="utf-8").read()
    assert "def executions(" in src and "remediation" in src, "the execution map is not read from the coverage map"
    ex = O.executions()
    if ex:
        assert ex.get("VIA-002") == "VENDOR_OR_STANDARD_WAIT", ex.get("VIA-002")
        assert ex.get("DFA-001") == "OWNER", ex.get("DFA-001")


def t_one_set_level_reading_is_not_seven_failures():
    """OUT-001 and DFA-001 are decided by a verdict written ONCE for the whole set, in v2/ecad/out/, while
    every per-board rule reads its own phase directory. A pair is what a BOARD must satisfy, so the table
    counts pairs; reporting 43 measured failures without saying that seven of them are one gate's single
    answer overstates how many separate things are wrong. The test is the evidence PATH the audit already
    carries: a path that serves more than one board is one reading."""
    from harness import Skip
    res = O.collect()
    if not res["boards"]: raise Skip("this tree holds no rule audit to classify")
    assert res["measured_distinct"] <= res["measured"], res
    shared = {rid for rid, _ in res["set_readings"]}
    if shared:
        for p in res["pairs"]:
            if p["rule"] in shared: assert p["set_reading"], p
        # a per-board rule is never marked shared
        for p in res["pairs"]:
            if p["rule"] == "PI-003": assert not p["set_reading"], p
