#!/usr/bin/env python3
"""Does an INCONCLUSIVE reliability reading reach the consumers of REL-001 as INCONCLUSIVE? Shown on fixtures.

Worker d6rel, MESHSAT-1357, 28 September 2026. READ ONLY: in-memory records through the reader's own functions
(rules_status.result_for, _supersedes, _after_meaning_changed); nothing is written anywhere.

The consumers of the reliability verdict, found by reading the tree (v2/docs/records/d6rel/README.md, section
"The consumers"): rules_status.py reads it for rule REL-001 through the coverage map (verification.verdict:
reliability); gate_sweep.sh runs the tool per board and copies the verdict; rules_render.py renders what
rules_status computes. final_gate.py, order_readiness.py and retake_schematic_phase.py do not read it.

Usage: consumers_probe.py <tools dir>
"""
import os, sys, copy


def main(argv):
    tools = os.path.abspath(argv[0]); sys.path.insert(0, tools)
    import rules_status as S, rules_lib as R
    reg = R.load(); rule = next(r for r in reg["rules"] if r["id"] == "REL-001")
    m = S.manifest(); cov = S.coverage(); fp = S._fingerprint_now()
    digest = R.rule_fingerprints().get("REL-001")

    def rec(verdict, ts, missing=None, note=""):
        return {"tool": "reliability", "name": "reliability", "verdict": verdict, "ts": ts, "missing_input": missing,
                "note": note, "counts": {"candidates": 0}, "denominator": 0, "applicable": True, "advisory": False,
                "policy": {"rule_set_fingerprint": fp, "rule_fingerprints": {"REL-001": digest}},
                "inputs": {"board": "a"}, "rules": ["REL-001"], "_path": "fixture/reliability.verdict.json"}

    print("1. rules_status.result_for on one INCONCLUSIVE reliability reading (board A):")
    inc = rec("INCONCLUSIVE", "2026-09-28T01:00:00Z", missing="board A has no netlist of its declared phase in this tree")
    r = S.result_for(rule, "a", cov, {"reliability": inc}, m, fp)
    print("   result %s: %s" % (r["result"], r["why"][:150]))
    assert r["result"] == S.INCONCLUSIVE, r
    print("   -> INCONCLUSIVE reaches the rule as INCONCLUSIVE, with the tool's own reason.")
    print()
    print("2. rules_status._supersedes: a NEW INCONCLUSIVE reading that declares its input absent, beside an OLD PASS")
    print("   from the word-list tool that never declared anything (the reviewer's case 4 read PASS of 0 with no netlist):")
    old_pass = rec("PASS", "2026-09-27T10:00:00Z")
    wins = S._supersedes(inc, old_pass)
    print("   new supersedes old: %s" % wins)
    print("   -> the OLD PASS stands in front of the new reading (the rule 'a reading taken with less input never replaces")
    print("      one taken with more', which cannot tell that the old reading had no input either).")
    print()
    print("3. The floor that closes it: pcb_rules_coverage.yaml REL-001 evidence_not_before (the apply script of this")
    print("   stream adds it). With the floor, the OLD PASS is not current evidence, whichever reading wins:")
    c2 = copy.deepcopy(cov); c2["REL-001"] = dict(c2["REL-001"], evidence_not_before={"reliability": "2026-09-28T00:00:00+02:00"})
    ok, why = S._after_meaning_changed(old_pass, "reliability", c2["REL-001"], "a")
    print("   old PASS under the floor: current=%s: %s" % (ok, why[:140]))
    assert not ok
    r2 = S.result_for(rule, "a", c2, {"reliability": old_pass}, m, fp)
    print("   result_for with the old PASS alone: %s: %s" % (r2["result"], r2["why"][:120]))
    assert r2["result"] == S.INCONCLUSIVE
    r3 = S.result_for(rule, "a", c2, {"reliability": rec("PASS", "2026-09-28T01:00:00Z")}, m, fp)
    print("   result_for with a PASS taken after the floor: %s" % r3["result"])
    assert r3["result"] == S.PASS
    print("   without the floor, the old PASS reads: %s" % S.result_for(rule, "a", cov, {"reliability": old_pass}, m, fp)["result"])
    print()
    print("4. A crashed tool (verdict.guard) writes INCONCLUSIVE with missing_input, which reaches the rule the same way:")
    crash = rec("INCONCLUSIVE", "2026-09-28T01:00:00Z", missing="a decision: the gate crashed with ValueError",
                note="the gate raised before it decided")
    r4 = S.result_for(rule, "a", cov, {"reliability": crash}, m, fp)
    print("   result %s: %s" % (r4["result"], r4["why"][:120]))
    assert r4["result"] == S.INCONCLUSIVE
    print()
    print("5. No verdict at all for the board:")
    r5 = S.result_for(rule, "a", cov, {}, m, fp)
    print("   result %s: %s" % (r5["result"], r5["why"]))
    assert r5["result"] == S.INCONCLUSIVE
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
