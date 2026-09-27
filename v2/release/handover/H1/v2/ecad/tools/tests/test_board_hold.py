#!/usr/bin/env python3
"""A board held by an open owner decision cannot be promoted, published or ordered (16 September 2026).

Board E routes 0 hard and 0 unrouted and its board gate passes 69 of 69. What holds it is not a measurement
anybody failed to take: rule TRN-001 says four of its exposed ports put the clamp BEHIND the active part, the
fix is a schematic change, and which fix is taken is the owner's decision 31, which is itself coupled to the
operating envelope of decision 34.

A hold like that has nowhere to live in the rule results without lying in one direction or the other: invent a
failing rule and the record is false, leave it out and the board reads releasable. So it is its own data, and
these are the three places a held board could otherwise get through:

  * the generated status page, which is what a person reads;
  * the final gate, which is what a release is read off;
  * make_handoff.py, which is the ONE producer of the JLCPCB upload set.

Fixtures both ways in each: a register with the hold (the committed state, expected to refuse) and one with it
removed (expected to let the board through on its own merits).
"""
import os, re, sys, json, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import rules_lib as R


def _write(d, body):
    p = os.path.join(d, "holds.yaml"); open(p, "w").write(body); return p


def t_a_hold_declares_all_four_status_fields():
    """DEFECTIVE fixture: a hold missing one field. A partial status line is how "held" becomes "nearly
    ready" over a few reports, so it is refused rather than printed short."""
    d = tempfile.mkdtemp(prefix="hold-partial-")
    p = _write(d, "holds:\n e:\n   decision: 31\n   ROUTING_STATUS: PASS\n   FAB_READINESS: NOT_READY\n"
                  "   PUBLICATION_STATUS: HELD\n")
    try:
        R.board_holds(p)
    except ValueError as e:
        assert "ELECTRICAL_PROTECTION_STATUS" in str(e), e
    else:
        raise AssertionError("a hold with three of the four status fields was accepted")


def t_a_hold_names_the_decision_that_would_lift_it():
    d = tempfile.mkdtemp(prefix="hold-nodecision-")
    p = _write(d, "holds:\n e:\n   ROUTING_STATUS: PASS\n   ELECTRICAL_PROTECTION_STATUS: BLOCKED_DECISION_31\n"
                  "   FAB_READINESS: NOT_READY\n   PUBLICATION_STATUS: HELD\n")
    try:
        R.board_holds(p)
    except ValueError as e:
        assert "decision" in str(e), e
    else:
        raise AssertionError("a hold that names no decision was accepted, so nothing says what lifts it")


def t_the_committed_hold_is_board_e_on_decision_31():
    """ACCEPTABLE fixture: the state as it stands. When decision 31 is ruled this test's expectation changes
    with the data, which is the point of keeping the hold as data."""
    h = R.board_holds()
    if not h: return   # the decision has been ruled and the entry deleted: nothing to assert
    assert "e" in h, sorted(h)
    e = h["e"]
    assert str(e["decision"]) == "31"
    assert e["PUBLICATION_STATUS"] == "HELD" and e["FAB_READINESS"] == "NOT_READY"
    assert e["ROUTING_STATUS"] == "PASS", "the hold must not misstate the routing result to justify itself"


def t_the_generated_board_page_carries_the_hold():
    """The page a person reads. Every one of the four fields, in the owner's own words."""
    h = R.board_holds()
    if not h: return
    page = os.path.join(TOOLS, "..", "..", "docs", "PCB-RULE-STATUS-E.md")
    if not os.path.exists(page): raise AssertionError("board E has no generated status page")
    txt = open(page, encoding="utf-8").read()
    for k in R.HOLD_FIELDS:
        assert "%s = %s" % (k, h["e"][k]) in txt, "the page does not carry %s" % k
    assert "DECISION 31" in txt.upper()


def t_the_final_gate_refuses_a_held_board_whose_folder_passes():
    """DEFECTIVE fixture: a board whose deliverable folder passes every property AND is held. The set must
    still fail, and the row must say why rather than reading PASS."""
    import final_gate as F
    calls = []

    def fake_run(cmd):
        calls.append(cmd)
        who = os.path.basename(cmd[1])
        if who == "verify_deliverable.py": return 0, "verify_deliverable: ALL PASS (21 of 21 properties)\n"
        if who == "check_contracts.py": return 0, "contracts ALL PASS\n"
        if who == "jlc_certify.py": return 0, "jlc_certify: 1 components, CERTIFIED 1\n"
        return 0, "claims_check: 0 without a qualifier\n"

    d = tempfile.mkdtemp(prefix="hold-gate-")
    boards = os.path.join(d, "boards"); os.makedirs(boards)
    json.dump({"name": "pcb-e1-dock", "phase": "E9"}, open(os.path.join(boards, "e.json"), "w"))
    folders = os.path.join(d, "release", "revA", "boards")
    os.makedirs(os.path.join(folders, "meshsat-pcb-e-revA-E9"))
    os.makedirs(os.path.join(folders, "meshsat-pcb-e5-revA-E5"))
    keep = F.BOARDS
    try:
        F.BOARDS = folders
        held = _write(d, "holds:\n e:\n   decision: 31\n   ROUTING_STATUS: PASS\n"
                         "   ELECTRICAL_PROTECTION_STATUS: BLOCKED_DECISION_31\n   FAB_READINESS: NOT_READY\n"
                         "   PUBLICATION_STATUS: HELD\n")
        rc = F.main(["--json", os.path.join(d, "out.json")], run=fake_run, boards_dir=boards, holds_path=held)
        got = json.load(open(os.path.join(d, "out.json")))
        row = next(r for r in got["rows"] if r["board"] == "E")
        assert row["verdict"] == "HELD", row
        assert "decision 31" in row["summary"], row["summary"]
        assert rc == 1, "the set passed with a held board in it (rc %s)" % rc

        # ACCEPTABLE fixture: the same folders with no hold declared. The board passes on its own merits.
        none = _write(tempfile.mkdtemp(prefix="hold-none-"), "holds: {}\n")
        rc2 = F.main(["--json", os.path.join(d, "out2.json")], run=fake_run, boards_dir=boards, holds_path=none)
        got2 = json.load(open(os.path.join(d, "out2.json")))
        row2 = next(r for r in got2["rows"] if r["board"] == "E")
        assert row2["verdict"] == "PASS", row2
        assert rc2 == 0, "a set with no hold and every folder passing did not pass (rc %s)" % rc2
    finally:
        F.BOARDS = keep


def t_an_unreadable_hold_file_is_never_a_pass():
    """The 16 September shape in a new place: a gate that cannot read its own input must not conclude that
    everything is fine. A missing library or a typo here would otherwise release a held board."""
    import final_gate as F
    d = tempfile.mkdtemp(prefix="hold-broken-")
    p = _write(d, "holds:\n e:\n   decision: 31\n   ROUTING_STATUS: PASS\n")   # three fields short
    holds, why = F._holds(p)
    assert holds == {} and why and "could not be read" in why, (holds, why)


def t_the_order_set_producer_refuses_a_held_board():
    """make_handoff.py is the one producer of the JLCPCB upload set, so it is the one place a held board could
    become orderable. The guard is read as source here, because the module needs pcbnew and the runner has
    none; what is asserted is that the refusal exists, has no environment escape, and runs before anything is
    written."""
    src = open(os.path.join(TOOLS, "make_handoff.py"), encoding="utf-8").read()
    i = src.index("board_holds()")
    j = src.index("shutil.rmtree(REV")
    assert i < j, "the hold check runs after the review folder is wiped"
    guard = src[i:j]
    assert "sys.exit" in guard, "the hold is read and not acted on"
    assert "HANDOFF_ALLOW" not in guard and "environ" not in guard, \
        "the hold guard has an environment escape; an owner decision is not a session's to override"
