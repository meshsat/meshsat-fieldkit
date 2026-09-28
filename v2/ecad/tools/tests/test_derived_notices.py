"""The evidence page's head sentence and its limitation notices are READ FROM THE REGISTRY, never typed (MESHSAT-1357,
28 September 2026: handover H3's erratum g, the reassessment's correction 3 and the owner's review of the restart plan).

A fixed sentence said the requirements baseline was still open while the registry read BASELINED; and a reading an
open item limits (TRN-001 on board A, REL-001 everywhere) was shown current with no mark at its points of use. Both
are derived here, so they change with the registry and vanish when the item closes."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import rules_status as S
import rules_render as RR
import test_evidence_class as EC

FEA_OPEN = {"id": "FEA-001", "kind": "feasibility", "status": "FEASIBILITY_OPEN", "stages": [], "holds_layout_entry": []}
FEA_DONE = dict(FEA_OPEN, status="DEFINED")
ITEM = {"id": "S-88", "class": "SESSION", "status": "OPEN",
        "title": "TRN-001 on board A does not judge VIN_RAW's entry. Open until the declaration names the real entry.",
        "limits_reading": [{"rule": "TRN-001", "boards": ["a"]}]}
ITEM_ALL = {"id": "S-89", "class": "SESSION", "status": "OPEN",
            "title": "REL-001's completeness can be false. Open until the population is an explicit inventory.",
            "limits_reading": [{"rule": "REL-001", "boards": "all"}]}


def t_the_head_sentence_follows_the_registry_baseline_state():
    s = RR.baseline_sentence({"baseline_state": "BASELINED at abc12345", "records": [FEA_OPEN], "open_items": []})
    assert "requirements baseline reads BASELINED at abc12345" in s, s
    assert "architecture baseline is still open (1 of 1 feasibility records FEASIBILITY_OPEN: FEA-001)" in s, s
    assert "requirements and architecture baselines are still open" not in s, s
    s2 = RR.baseline_sentence({"baseline_state": "OPEN", "records": [FEA_OPEN], "open_items": []})
    assert s2.startswith("the requirements and architecture baselines are still open"), s2
    s3 = RR.baseline_sentence({"baseline_state": "BASELINED at abc12345", "records": [FEA_DONE], "open_items": []})
    assert "every one of the 1 feasibility records is resolved" in s3 and "still open" not in s3, s3
    s4 = RR.baseline_sentence(None)
    assert "absent" in s4, s4
    # and on the page itself
    audits = {"x": EC._audit("x", [EC._row("R-1", "SCHEMATIC", "PASS", S.CURRENT_CANDIDATE)])}
    body = RR.current_evidence_doc(audits, holds={}, regs=EC.EMPTY,
                                   req={"baseline_state": "BASELINED at abc12345", "records": [FEA_OPEN], "open_items": []})
    assert "requirements baseline reads BASELINED at abc12345" in body, body[:900]
    assert "requirements and architecture baselines are still open" not in body


def t_a_limit_notice_appears_while_its_item_is_open_and_not_after():
    audits = {"a": EC._audit("a", [EC._row("TRN-001", "SCHEMATIC", "PASS", S.CURRENT_CANDIDATE)])}
    with_item = {"baseline_state": "BASELINED at abc12345", "records": [], "open_items": [ITEM, ITEM_ALL]}
    body = RR.current_evidence_doc(audits, holds={}, regs=EC.EMPTY, req=with_item)
    assert "TRN-001 on board A: LIMITED while S-88 stands: TRN-001 on board A does not judge VIN_RAW's entry." in body, body[-3000:]
    assert "REL-001 on every board: LIMITED while S-89 stands" in body
    closed = dict(with_item, open_items=[])
    body2 = RR.current_evidence_doc(audits, holds={}, regs=EC.EMPTY, req=closed)
    assert "LIMITED while" not in body2 and "No open item of the requirements registry limits a reading" in body2
    # a closed item (status not OPEN) derives nothing even if the field is still on it
    stale = dict(with_item, open_items=[dict(ITEM, status="CLOSED")])
    assert "LIMITED while" not in RR.current_evidence_doc(audits, holds={}, regs=EC.EMPTY, req=stale)


def t_the_board_page_marks_the_limited_row_at_its_point_of_use():
    limits = RR.reading_limits({"open_items": [ITEM, ITEM_ALL]})
    assert RR.limit_marker(limits, "TRN-001", "a") == "LIMITED (open item S-88)"
    assert RR.limit_marker(limits, "TRN-001", "b") == ""
    assert RR.limit_marker(limits, "REL-001", "e5") == "LIMITED (open item S-89)"
    assert RR.limit_marker(limits, "SCH-001", "a") == ""
    assert RR.reading_limits(None) == {} and RR.reading_limits({"open_items": []}) == {}
    # the row as the page prints it, with the marker in the why column and the table intact
    keep = RR._req_or_none
    try:
        RR._req_or_none = lambda req: {"open_items": [ITEM]}
        import rules_lib as R
        st = {"board": "a", "manifest_version": "t", "rule_set_fingerprint": "f", "evidence_epoch": "e",
              "subject": {"dir": "pcb-a", "board": None},
              "rows": [dict(EC._row("TRN-001", "SCHEMATIC", "PASS", S.CURRENT_CANDIDATE), why="w"),
                       dict(EC._row("SCH-001", "SCHEMATIC", "PASS", S.CURRENT_CANDIDATE), why="w")]}
        body = RR.board_doc("a", st, R.load(), S.coverage())
        rows = [l for l in body.split("\n") if l.startswith("| TRN-001 ") or l.startswith("| SCH-001 ")]
        assert len(rows) == 2 and all(l.count("|") == 6 for l in rows), rows
        assert "w; LIMITED (open item S-88) |" in rows[0], rows[0]
        assert "LIMITED" not in rows[1], rows[1]
    finally:
        RR._req_or_none = keep
