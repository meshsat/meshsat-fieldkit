"""Every gate names a rule, every rule's document is generated, and an ENFORCED rule has fixtures
(MESHSAT-862, 16 September 2026).

These are the repository rules that keep the registry and the tools from drifting apart. The project's own
history is the argument for each: gates were added one incident at a time and no document could say which
requirement they served, and every document that described a rule was hand-maintained beside the code that
enforced a different one.
"""
import os, sys, glob, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import rules_lib as R
import rules_status as S
from harness import need


def t_every_rule_has_a_coverage_entry():
    reg = R.load(); cov = S.coverage()
    ids = {r["id"] for r in reg["rules"]}
    missing = sorted(ids - set(cov)); extra = sorted(set(cov) - ids)
    assert not missing, "rules with no coverage entry: %s" % missing
    assert not extra, "coverage entries for rules that do not exist: %s" % extra


def t_an_enforced_rule_names_a_verdict_and_a_fixture():
    """ENFORCED is the strongest claim the coverage map can make: an executable gate, a machine-readable
    verdict and a behavioural fixture. Without the fixture it is GENERATED_ONLY."""
    cov = S.coverage(); bad = []
    for rid, c in sorted(cov.items()):
        if c.get("maturity") != "ENFORCED": continue
        v = c.get("verification") or {}
        if not v.get("verdict"): bad.append("%s names no verdict" % rid)
        elif not v.get("fixtures"): bad.append("%s names no fixture" % rid)
    assert not bad, "; ".join(bad)


def t_every_fixture_a_coverage_entry_names_exists():
    cov = S.coverage(); missing = []
    for rid, c in sorted(cov.items()):
        f = (c.get("verification") or {}).get("fixtures")
        if not f: continue
        for one in str(f).split(","):
            p = os.path.join(os.path.dirname(TOOLS), one.strip()) if one.strip().startswith("v2") else os.path.join(TOOLS, one.strip())
            if not os.path.exists(p): missing.append("%s -> %s" % (rid, one.strip()))
    assert not missing, "fixtures named and absent: %s" % missing


def t_every_verdict_the_coverage_map_names_is_written_by_a_tool():
    """A coverage entry pointing at a verdict nobody writes is a rule that can never pass."""
    cov = S.coverage(); src = ""
    for f in glob.glob(os.path.join(TOOLS, "*.py")) + glob.glob(os.path.join(TOOLS, "*.sh")):
        src += open(f, errors="replace").read()
    missing = []
    for rid, c in sorted(cov.items()):
        raw = (c.get("verification") or {}).get("verdict")
        if not raw: continue
        for name in str(raw).split(","):          # a rule may name several verdicts; each must be written
            name = name.strip()
            if not name: continue
            stem = name.split("<letter>")[0].split("-")[0]
            if stem and stem not in src: missing.append("%s -> %s" % (rid, name))
    assert not missing, "verdicts named in the coverage map that no tool writes: %s" % missing


def t_a_verdict_names_the_rules_it_decides_and_the_rule_set_it_was_taken_under():
    """Executed: write a verdict and read it back. A verdict that cannot say which rule it decided is how a
    project comes to enforce rules it never wrote down."""
    import tempfile, verdict
    d = tempfile.mkdtemp()
    verdict.write("erc_gate", verdict.PASS, denominator=1, out_dir=d, quiet=True)
    rec = json.load(open(os.path.join(d, "erc_gate.verdict.json")))
    assert rec["rules"], "a gate in the coverage map wrote a verdict naming no rule"
    assert rec["policy"].get("rule_set_fingerprint") == R.fingerprint(), "the verdict does not name the current rule set"


def t_the_documents_are_generated_and_not_hand_maintained():
    """rules_render --check regenerates every document into memory and refuses one that differs on disk."""
    need(os.path.join(os.path.dirname(TOOLS), "docs", "PCB-GOLDEN-RULES.md"), "the rulebook has not been rendered yet")
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "rules_render.py"), "--check"],
                       capture_output=True, text=True, cwd=os.path.dirname(TOOLS))
    assert p.returncode == 0, "a generated document differs from the registry:\n%s" % (p.stdout + p.stderr)[-800:]


def t_the_readiness_manifest_matches_the_registry_manifest():
    m = S.manifest(); reg = R.load()
    assert set(m["boards"]) == set(reg["manifest"]["boards"]), \
        "the readiness manifest and the registry disagree about the set: %s vs %s" % (sorted(m["boards"]), sorted(reg["manifest"]["boards"]))


def t_the_freeze_is_declared_with_its_authority_and_what_lifts_it():
    m = S.manifest()["promotion"]
    if m.get("frozen"):
        for k in ("why", "lifts_when", "authority", "frozen_at"):
            assert m.get(k), "the promotion freeze does not say %s" % k


def t_a_verdict_named_for_one_board_is_not_demanded_of_another():
    """A verdict name that carries a board letter is that board's own gate, and no other board can write it.

    Found on 16 September 2026: VIA-001 named "via_audit, check_pcb_c". Five boards held a current via_audit
    PASS and every one of them read INCONCLUSIVE, because the coverage map also demanded board C's gate of
    them. The worst-result rule then made the missing verdict the answer, so a rule that WAS verified on six
    boards reported as verified on one.

    The property is not "never name a board gate": a rule that applies to one board may name that board's
    gate, and several do. It is that the boards a rule applies to must all be able to produce every verdict it
    names. `<letter>` is the general form and is expanded per board, so it always satisfies this.
    """
    import re
    reg = R.load(); facts = R.facts(); cov = S.coverage(); m = S.manifest()
    letters = list(m["boards"])
    applies = {}
    for letter in letters:
        for rule, _why in R.rules_for(letter, reg, facts):
            applies.setdefault(rule["id"], set()).add(letter.lower())
    bad = []
    for rid, c in sorted(cov.items()):
        raw = (c.get("verification") or {}).get("verdict")
        if not raw: continue
        for name in [n.strip() for n in str(raw).split(",") if n.strip()]:
            if "<letter>" in name: continue
            mm = re.search(r"_(%s)$" % "|".join(sorted((l.lower() for l in letters), key=len, reverse=True)), name)
            if not mm: continue
            named = mm.group(1)
            on = applies.get(rid, set())
            if on - {named}:
                bad.append("%s names %s but applies to %s: %s cannot write it"
                           % (rid, name, ",".join(sorted(on)), ",".join(sorted(on - {named}))))
    assert not bad, "; ".join(bad)
