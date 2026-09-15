"""The rule registry's own rules (MESHSAT-862, 16 September 2026).

The registry exists because this project enforced gates it had never written down, and wrote down rules it
never enforced. These tests hold the properties that make the registry worth reading: it validates, every
domain of the coverage axis carries at least one rule, applicability is DATA and resolves for every board,
and the three honesty rules cannot be removed without a test failing. Each one is executed against a mutated
copy of a real rule, never against a source string.
"""
import os, sys, copy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import rules_lib as R


def _reg():
    return R.load()


def t_the_registry_validates():
    errs, warns = R.validate(_reg())
    assert not errs, "the committed registry does not validate: %s" % errs[:5]


def t_every_domain_of_the_coverage_axis_carries_a_rule():
    """The domain list IS the coverage axis. A domain with no rule is a part of PCB engineering this project
    has not said anything about, and that must be visible rather than absent."""
    have = {r["domain"] for r in _reg()["rules"]}
    missing = [d for d in R.DOMAINS if d not in have]
    assert not missing, "no rule in these domains: %s" % missing


def t_applicability_resolves_for_every_board_in_the_manifest():
    reg = _reg(); facts = R.facts()
    for letter in reg["manifest"]["boards"]:
        assert letter in R.board_facts(facts), "board %s is in the manifest and has no facts" % letter
        rs = R.rules_for(letter, reg, facts)
        assert rs, "no rule applies to board %s, which cannot be right" % letter
        for r, why in rs: assert why, "%s applies to %s with no reason" % (r["id"], letter)


def t_a_bare_board_gets_fewer_rules_than_a_routed_one():
    """E5 carries no schematic and no track. The conditions must actually discriminate: a registry whose
    conditions all evaluate true is a registry with no applicability."""
    n_e5 = len(R.rules_for("e5")); n_b = len(R.rules_for("b"))
    assert n_e5 < n_b, "the bare dock block (%d) is judged by as many rules as the compute board (%d)" % (n_e5, n_b)


def t_a_heuristic_may_not_be_a_blocker():
    reg = copy.deepcopy(_reg())
    r = next(x for x in reg["rules"] if x["classification"] == "HEURISTIC")
    r["release_effect"] = "BLOCKER"
    errs, _ = R.validate(reg)
    assert any("HEURISTIC" in e for e in errs), "a heuristic promoted to a blocker validated"


def t_a_blocker_with_no_citable_source_must_say_so_in_its_maturity():
    reg = copy.deepcopy(_reg())
    r = next(x for x in reg["rules"] if x["release_effect"] == "BLOCKER" and x["source_status"] == "SOURCE_UNVERIFIED")
    r["maturity"] = "ENFORCED"
    errs, _ = R.validate(reg)
    assert any(r["id"] in e and "unverified source" in e for e in errs), \
        "a blocker with no authority claimed to be enforced and validated"


def t_a_conditional_rule_carries_a_machine_readable_condition():
    reg = copy.deepcopy(_reg())
    r = next(x for x in reg["rules"] if x["applicability"] == "CONDITIONAL")
    r.pop("condition")
    errs, _ = R.validate(reg)
    assert any(r["id"] in e and "condition" in e for e in errs), "a conditional rule with no condition validated"


def t_a_verified_source_names_a_document():
    reg = copy.deepcopy(_reg())
    r = reg["rules"][0]; r["source_status"] = "VERIFIED"; r["sources"] = []
    errs, _ = R.validate(reg)
    assert any(r["id"] in e and "VERIFIED" in e for e in errs), "a rule claimed a verified source with no source"


def t_the_fingerprint_moves_when_a_rule_moves():
    """Evidence records the fingerprint. If the fingerprint did not move with the rules, evidence taken under
    an older registry would look current."""
    reg = _reg(); before = R.fingerprint(reg)
    reg2 = copy.deepcopy(reg); reg2["rules"][0]["acceptance_criteria"] += " (changed)"
    assert R.fingerprint(reg2) != before, "the fingerprint did not change when a rule's acceptance criteria did"


def t_a_condition_is_data_and_never_code():
    """Conditions are evaluated by rules_lib.evaluate over all/any/not and a fixed operator set. A condition
    carrying a python expression must not be executed by anything."""
    src = open(os.path.join(TOOLS, "rules_lib.py")).read()
    assert "eval(" not in src and "exec(" not in src, "rules_lib evaluates code"
    assert R.evaluate({"all": [{"fact": "layers", "op": "ge", "value": 4}]}, {"layers": 6}) is True
    assert R.evaluate({"any": [{"fact": "interfaces", "op": "contains", "value": "PCIE"}]}, {"interfaces": []}) is False
    try:
        R.evaluate({"fact": "layers", "op": "spawn_shell", "value": 1}, {"layers": 6}); raise AssertionError("unknown op accepted")
    except ValueError: pass


def t_the_manifest_and_the_facts_agree():
    reg = _reg(); facts = R.facts()
    boards = set(reg["manifest"]["boards"]); factual = set(R.board_facts(facts))
    assert boards == factual, "manifest %s and facts %s disagree" % (sorted(boards), sorted(factual))
