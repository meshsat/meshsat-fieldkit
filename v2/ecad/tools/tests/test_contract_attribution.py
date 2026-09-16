"""A cross-board contract says which boards it is about, and its verdict lands on those boards
(MESHSAT-862, 16 September 2026).

Board B was missing six PCIe coupling capacitors that the compute module's own datasheet requires. The
contract that found them is board B's, and `check_contracts` writes ONE verdict that every board reads as
evidence, so boards A, C, D, E, E5 and P all reported a failed rule for a defect on a board they do not
touch: four of the set's forty-five failing rule-board pairs were somebody else's.

Each contract now declares its boards and a per-board verdict is written beside the set's own, the pattern
`final_gate_<letter>` already uses. The declaration is explicit rather than read out of the sentence: the
first version inferred it, and it lost board A on two contracts within nine tries, because the English
article "A" has to be stripped before any such inference works at all.
"""
import os, re, sys, json, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
SRC = os.path.join(TOOLS, "check_contracts.py")


def t_every_contract_declares_the_boards_it_is_about():
    """Read statically: no call to check() may leave `boards` to a default, because there is no honest
    default. A contract with no board cannot be attributed and would silently land on none."""
    s = open(SRC, errors="replace").read()
    bad = []
    for m in re.finditer(r"^(?!def )\s*(?:\w+\s*=\s*)?check\(", s, re.M):
        # take the call's text up to the line that closes it
        rest = s[m.start():]
        depth = 0; end = 0
        for i, ch in enumerate(rest):
            if ch == "(": depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0: end = i; break
        call = rest[:end + 1]
        if "boards=" not in call:
            bad.append(call.replace("\n", " ")[:90])
    assert not bad, "contract(s) that do not declare their boards: %s" % bad


def t_a_contract_with_no_board_is_refused_rather_than_attributed_to_none():
    """Executed. The guard is in check() itself, so a contract added without boards fails loudly the first
    time it runs rather than quietly counting for no board."""
    ns = {}
    src = open(SRC, errors="replace").read()
    body = src[src.index("fails = []; checked = []"):src.index("def pinmap(")]
    import collections
    exec("import collections\n" + body, ns)
    ns["check"](True, "B: something", boards={"B"})
    assert ns["per_board"]["B"]["pass"] == 1
    ns["check"](False, "A and B disagree", boards={"A", "B"})
    assert ns["per_board"]["A"]["fail"] and ns["per_board"]["B"]["fail"]
    try:
        ns["check"](True, "a contract with no board")
    except AssertionError as e:
        assert "declares no board" in str(e), e
    else:
        raise AssertionError("a contract with no board was accepted")


def t_a_failure_on_one_board_does_not_fail_another():
    """The property the whole change exists for, on the shape that caused it: board B's own contract fails
    and board A's verdict is unaffected."""
    ns = {}
    src = open(SRC, errors="replace").read()
    body = src[src.index("fails = []; checked = []"):src.index("def pinmap(")]
    exec("import collections\n" + body, ns)
    ns["check"](True, "A: the pre-charge pin lands on a cell node net", boards={"A"})
    ns["check"](False, "B: PCIE1_RX_P has exactly one series AC coupling capacitor", boards={"B"})
    assert ns["per_board"]["A"]["fail"] == [], ns["per_board"]["A"]
    assert len(ns["per_board"]["B"]["fail"]) == 1, ns["per_board"]["B"]


def t_the_registry_reads_the_per_board_verdict_for_the_cross_board_rules():
    import rules_status as S
    cov = S.coverage()
    for rid in ("SCH-003", "RF-002"):
        v = (cov[rid].get("verification") or {}).get("verdict")
        assert v == "check_contracts_<letter>", "%s still reads the set verdict: %r" % (rid, v)
