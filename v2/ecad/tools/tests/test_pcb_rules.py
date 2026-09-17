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
    # the registry's field is the PHASE A assessment; the live maturity lives in the coverage map, and the two
    # were one name on two facts until 16 September, when they had drifted on 51 of the 56 rules
    r["maturity_at_writing"] = "ENFORCED"
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


def t_the_fingerprint_moves_when_a_rule_changes_what_it_demands_and_not_when_prose_changes():
    """The identity evidence records is a digest of what the rules DEMAND.

    The first version hashed the whole rule, so writing down which clause of a vendor datasheet a limit comes
    from marked every board's evidence stale: a tax on the one activity this audit exists to encourage. A board
    that passed a DRC has not been asked anything different because a rationale was rewritten. What must
    invalidate evidence is a change to the requirement, its applicability, its acceptance criteria, its release
    effect, its verification method or phase, or the boards and interfaces it names.
    """
    import copy
    reg = R.load()
    base = R.fingerprint(reg)

    prose = copy.deepcopy(reg)
    prose["rules"][0]["rationale"] = "rewritten for clarity, demanding exactly the same thing"
    prose["rules"][0]["sources"] = [{"title": "a document someone finally read", "issuer": "x"}]
    prose["rules"][0]["short_name"] = "a better name for the same rule"
    assert R.fingerprint(prose) == base, "documenting a rule invalidated every board's evidence"

    demand = copy.deepcopy(reg)
    demand["rules"][0]["acceptance_criteria"] = "a different bar entirely"
    assert R.fingerprint(demand) != base, "a rule's acceptance criteria changed and the evidence stayed current"

    effect = copy.deepcopy(reg)
    effect["rules"][0]["release_effect"] = "MUST_JUSTIFY" if reg["rules"][0]["release_effect"] == "BLOCKER" else "BLOCKER"
    assert R.fingerprint(effect) != base, "a rule stopped blocking and the evidence stayed current"

    # and the whole-text digest still exists, because a generated document has to be able to say which text it
    # came from even when the demands did not move
    assert R.documentation_digest(prose) != R.documentation_digest(reg)


def t_an_enforced_blocker_carries_a_false_positive_analysis():
    """Process control 4 of the owner's instruction of 16 September: no hard gate without authority,
    applicability, acceptance criteria AND a false-positive analysis.

    This project shipped gates that refused CORRECT boards five times in one week: a placement predictor that
    called 244 normal plane pads a defect, a DRC judgement that failed a pre-route board for being unrouted, a
    netlist comparison that read KiCad's unconnected-pin placeholder as a net, a pour coverage measured against
    a rectangle the board is not, and a return-path rule that refused an opto inhibit. Each cost a day or more,
    and each was found by a board being wrong rather than by anyone asking the question in advance. A rule that
    can refuse a board now has to say what a WRONG refusal would look like and what stops it.
    """
    import copy
    reg = copy.deepcopy(_reg())
    r = next(x for x in reg["rules"] if x["id"] == "PLC-001")
    assert len(str(r.get("false_positive_analysis") or "")) >= 80, "PLC-001 lost its false-positive analysis"
    r["false_positive_analysis"] = "none worth writing"
    errs, _ = R.validate(reg)
    assert any("PLC-001" in e and "false-positive" in e for e in errs), \
        "an enforced blocker validated with no false-positive analysis"


def t_the_registry_does_not_carry_a_live_maturity():
    """One fact, one owner. The registry's maturity and the coverage map's drifted apart on 51 of the 56 rules
    within a day of both existing, and the registry then read UNASSESSED for rules that were refusing boards."""
    reg = _reg()
    bare = [r["id"] for r in reg["rules"] if "maturity" in r]
    assert not bare, "these rules carry a bare `maturity`, which the coverage map owns: %s" % bare[:8]
    assert all("maturity_at_writing" in r for r in reg["rules"]), "a rule lost its Phase A assessment"


def t_a_rules_board_list_never_narrows_its_own_condition():
    """17 September 2026. `boards_affected` reads like documentation and is used as a FILTER: `rules_for` drops a
    board that is not in the list BEFORE it evaluates the condition, so a list written when a rule was drafted
    silently decides what the rule is judged on, and the condition, which is the designed mechanism and is
    resolved against each board's own facts, cannot widen it. Ten rules disagreed with themselves that morning:
    SCH-004 left out the three boards that carry the pack node, RF-001 left out the two with blind-mate RF
    interfaces, PAIR-001 the two boards that declare a pair class, PWR-003 the board with three fuses on it.
    A board that a rule's own condition selects is a board that rule is about."""
    reg = _reg(); facts = R.board_facts()
    bad = []
    for r in reg["rules"]:
        aff = r.get("boards_affected")
        if not isinstance(aff, list) or not aff or "ALL" in aff: continue
        for letter, f in sorted(facts.items()):
            ok, _why = R.applies_to(r, f)
            if ok and letter not in aff:
                bad.append("%s: its condition selects board %s and its boards_affected list does not name it"
                           % (r["id"], letter))
    assert not bad, "the registry narrows %d rule(s) below their own condition:\n  %s" % (len(bad), "\n  ".join(bad))


def t_every_board_table_and_the_facts_name_the_same_project():
    """17 September 2026, when board E5 got its first board table. Two files describe a board: the facts, which
    are DATA about the product and decide which rules apply to it, and the table, which is where the board's own
    declarations live. They are joined by the project directory's name, and a disagreement would make a rule
    apply to one board and a tool answer about another. `letter_for` reads the table; `applies_to` reads the
    facts."""
    import glob, os, json
    facts = R.board_facts()
    tools = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for p in sorted(glob.glob(os.path.join(tools, "boards", "*.json"))):
        L = os.path.basename(p)[:-5]
        d = json.load(open(p, encoding="utf-8"))
        assert L in facts, "boards/%s.json has no entry in pcb_board_facts.yaml" % L
        assert facts[L].get("project") == d.get("name"), \
            "%s: the table names %r and the facts name %r" % (L, d.get("name"), facts[L].get("project"))
