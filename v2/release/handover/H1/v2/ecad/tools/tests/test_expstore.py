#!/usr/bin/env python3
"""The experiment store (15 September 2026, red team report 1 recommendation 2): a cycle is a first-class object with an
exact arm set; a duplicate arm, a second terminal result, or a missing result cannot read as a complete cycle."""
import os, sys, json, tempfile, sqlite3
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import expstore


def _store():
    return expstore.Store(os.path.join(tempfile.mkdtemp(prefix="expstore-"), "store.db"))


def t_a_cycle_with_every_arm_terminal_is_complete_and_exports():
    s = _store(); cid = s.new_cycle("pcb-b-compute", "place", "ctx1", 2)
    s.add_arm(cid, "gap_2p8", {"PLACE_COUPLE_GAP": 2.8}, {"metric": "pairs", "op": ">=", "value": 40})
    s.add_arm(cid, "gap_3p2", {"PLACE_COUPLE_GAP": 3.2}, {"metric": "pairs", "op": ">=", "value": 40})
    assert s.complete(cid) == (False, "no terminal result for ['gap_2p8', 'gap_3p2']")
    s.finish_arm(cid, "gap_2p8", "MET", metrics={"pairs": (41, 48), "hard": 0})
    s.finish_arm(cid, "gap_3p2", "ILLEGAL", note="4 hard", metrics={"pairs": (39, 48), "hard": 4})
    ok, why = s.complete(cid); assert ok, why
    rows = s.arms(cid); assert [r["verdict"] for r in rows] == ["MET", "ILLEGAL"] and rows[0]["metrics"]["pairs"] == (41.0, 48.0)
    out = os.path.join(os.path.dirname(s.path), "export.jsonl"); n = s.export_jsonl(out)
    assert n == 2 and len(open(out).read().splitlines()) == 2


def t_a_duplicate_arm_name_in_one_cycle_is_refused_by_the_schema():
    s = _store(); cid = s.new_cycle("pcb-b-compute", "pair", "ctx", 1)
    s.add_arm(cid, "x", {}, {})
    try: s.add_arm(cid, "x", {}, {}); raise AssertionError("a second arm named x was accepted")
    except sqlite3.IntegrityError: pass


def t_a_second_terminal_result_for_an_arm_is_refused():
    s = _store(); cid = s.new_cycle("pcb-b-compute", "pair", "ctx", 1)
    s.add_arm(cid, "x", {}, {}); s.finish_arm(cid, "x", "MET")
    try: s.finish_arm(cid, "x", "MISSED"); raise AssertionError("a second terminal result was accepted")
    except ValueError: pass


def t_a_cycle_with_fewer_arms_than_requested_is_incomplete():
    s = _store(); cid = s.new_cycle("pcb-b-compute", "pair", "ctx", 3)
    s.add_arm(cid, "x", {}, {}); s.finish_arm(cid, "x", "MET")
    ok, why = s.complete(cid); assert not ok and "1 arm(s) for 3 requested" in why


def t_a_non_terminal_status_is_not_a_result():
    s = _store(); cid = s.new_cycle("pcb-b-compute", "pair", "ctx", 1); s.add_arm(cid, "x", {}, {})
    try: s.finish_arm(cid, "x", "RUNNING"); raise AssertionError("a non-terminal status was stored as a result")
    except ValueError: pass


def t_the_verdict_envelope_names_the_tools_and_the_policy():
    import verdict
    d = tempfile.mkdtemp(prefix="verdict-env-")
    verdict.write("envelope_probe", verdict.PASS, counts={}, denominator=1, out_dir=d, quiet=True)
    rec = json.load(open(os.path.join(d, "envelope_probe.verdict.json")))
    assert "tools" in rec and "tools_tree_sha" in rec["tools"], rec.keys()
    assert rec.get("policy", {}).get("hard_types") == 15, rec.get("policy")
