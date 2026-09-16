#!/usr/bin/env python3
"""An open item says HOW it executes, and an engineering hour is not an elapsed hour (MESHSAT-862, 16 Sep 2026).

Two questions were being answered with one number. "How much work is left" is effort and has one honest total;
"when is it done" depends on what can run beside what, and on whose clock each item runs. This project has
reported the first as though it were the second twice, and had to withdraw it twice.

So every open item in the gap register declares an execution class, an item that declares none is an ERROR
rather than a default (a default would put a route on the session's queue or the other way about), a rented
box's hours become days at twenty-four a day while the session's become days at the declared working day, and
every programme stage after the design package declares the KIND of its numbers, because none of them has been
measured by this project and a reader is entitled to know that.

Fixtures both ways per class of rule: a defective register that must be refused, and the committed one that
must be accepted.
"""
import os, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import rules_eta as E


def t_every_open_item_declares_a_known_execution_class():
    """ACCEPTABLE fixture: the committed register. Absence is not a default here."""
    items = E.open_items()
    assert items, "the gap register produced no open items at all"
    for i in items:
        assert i["execution"] in E.EXECUTION, "%s declares %r" % (i["rule"], i["execution"])


def t_an_item_with_no_execution_class_is_refused():
    """DEFECTIVE fixture: one remediation with the key removed must stop the ETA, not default it."""
    cov = {"ZZZ-001": {"maturity": "OPEN",
                       "remediation": {"action": "a thing", "owner": "SESSION", "depends_on": [], "p50_h": 1, "p80_h": 2}}}
    try:
        E.open_items(cov)
    except SystemExit as e:
        assert "execution" in str(e), e
    else:
        raise AssertionError("an item with no execution class was scheduled anyway")


def t_a_box_hour_and_a_session_hour_are_different_days():
    """The arithmetic behind both withdrawn ETAs, as a unit. A twelve hour route is half an elapsed day; twelve
    hours of this session's work is two working days."""
    box = {"rule": "X", "execution": "PARALLEL_BOX", "p50": 12.0, "p80": 12.0, "depends_on": []}
    ses = {"rule": "Y", "execution": "PARALLEL_AGENT", "p50": 12.0, "p80": 12.0, "depends_on": []}
    assert E.day_rate(box, 6.0) == 24.0 and E.day_rate(ses, 6.0) == 6.0
    assert abs(E.critical_path_days([box], "p50", 6.0) - 0.5) < 1e-9
    assert abs(E.critical_path_days([ses], "p50", 6.0) - 2.0) < 1e-9


def t_more_workers_never_shorten_the_dependency_chain():
    """The bound that keeps the width honest: work that must follow other work is not compressible by adding
    workers, so the design figure is never below the longest chain however wide the pool is."""
    m1 = E.model(6.0, agents=1, boxes=2)
    m9 = E.model(6.0, agents=99, boxes=99)
    assert m9["design_package_days"]["p50"] >= m9["critical_path_days"]["p50"] - 1e-9
    assert m9["design_package_days"]["p50"] <= m1["design_package_days"]["p50"] + 1e-9


def t_every_programme_stage_declares_the_kind_of_its_numbers():
    """ACCEPTABLE fixture: the committed stages. A number with no provenance is not an estimate."""
    st = E.stages()
    for name, v in st.items():
        assert v.get("source") in ("COMPUTED", "VENDOR_PUBLISHED", "DECLARED_ESTIMATE", "MEASURED_BY_THIS_PROJECT"), \
            "%s declares source %r" % (name, v.get("source"))
        assert v.get("basis"), "%s declares no basis" % name


def t_a_stage_with_no_source_kind_is_refused():
    """DEFECTIVE fixture: a stages file whose numbers claim no provenance."""
    d = tempfile.mkdtemp(prefix="eta-stage-")
    p = os.path.join(d, "s.yaml")
    open(p, "w").write("stages:\n X: {p50_days: 1, p80_days: 2, basis: \"because\"}\n")
    keep = E.STAGES
    try:
        E.STAGES = p
        try:
            E.stages()
        except SystemExit as e:
            assert "source" in str(e), e
        else:
            raise AssertionError("a stage with no source kind was accepted")
    finally:
        E.STAGES = keep


def t_the_programme_is_never_shorter_than_the_design_package():
    """The milestones are cumulative: a date that goes backwards means the chain was built wrong."""
    m = E.model(6.0, agents=1, boxes=2)
    ms = m["milestones"]
    assert ms[0]["stage"] == "DESIGN_PACKAGE_READY_FOR_PROTOTYPE"
    assert ms[-1]["stage"] == "PRODUCTION_RELEASE_READY"
    for a, b in zip(ms, ms[1:]):
        assert b["cumulative_p50_days"] >= a["cumulative_p50_days"], (a, b)
        assert b["cumulative_p80_days"] >= a["cumulative_p80_days"], (a, b)
