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
import rules_render as RR
from harness import need

# Where the documents live is ONE fact and the renderer owns it. Written out a second time here, as
# `dirname(TOOLS)/docs`, it pointed at v2/ecad/docs, which does not exist, so the rule that refuses a
# hand-edited document SKIPPED on every run since it was written (16 September 2026). A rule that skips is
# not a rule.
DOCS = RR.DOCS


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
    need(os.path.join(DOCS, "PCB-GOLDEN-RULES.md"), "the rulebook has not been rendered yet")
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "rules_render.py"), "--check"],
                       capture_output=True, text=True, cwd=os.path.dirname(TOOLS))
    assert p.returncode == 0, "a generated document differs from the registry:\n%s" % (p.stdout + p.stderr)[-800:]


def t_the_readiness_manifest_matches_the_registry_manifest():
    m = S.manifest(); reg = R.load()
    assert set(m["boards"]) == set(reg["manifest"]["boards"]), \
        "the readiness manifest and the registry disagree about the set: %s vs %s" % (sorted(m["boards"]), sorted(reg["manifest"]["boards"]))


def t_the_manifest_and_the_registry_name_the_same_project_directory_for_a_board():
    """The board's project directory is ONE fact and two files carried it, so they drifted.

    The readiness manifest gave board E5 the project `pcb-e2-rfjunction`, the retired wall junction strip,
    while the registry's own facts said `pcb-e5-block`, which is where the board is. Every gate ran on the
    right directory, wrote 23 verdicts into it, and the status computation looked in the retired one and found
    none of them: E5 read INCONCLUSIVE on its board gate, its stackup and its DRC while holding a current
    verdict for all three (16 September 2026). A board's evidence directory is where its evidence is, and the
    two files that name it must say the same thing.
    """
    m = S.manifest(); facts = R.board_facts()
    bad = []
    for letter, b in sorted(m["boards"].items()):
        want = (facts.get(letter) or {}).get("project")
        got = b.get("project")
        if want and got and want != got:
            bad.append("%s: the manifest says %s, the registry facts say %s" % (letter, got, want))
        if got and not os.path.isdir(os.path.join(os.path.dirname(TOOLS), got)):
            bad.append("%s: the manifest names a project directory that does not exist: %s" % (letter, got))
    assert not bad, "; ".join(bad)


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


def t_a_coverage_entry_does_not_contradict_its_own_gap_category():
    """The maturity says WHY a rule is not enforced and the gap category says the same thing in one word; six
    entries said two different things at once.

    ISO-001, PI-003, SI-001, THM-001, RET-001 and RET-003 each carried maturity GENERATED_ONLY, which the
    status computation reports as "generation intends to comply and nothing verifies it", beside a gap
    category of SOURCE_OR_APPLICABILITY_UNRESOLVED and a remediation that says "obtain the table", "declare a
    rise time", "declare an efficiency per rail". A tool verifies every one of them; what is missing is the
    authority for its number. Reading the wrong reason six times is how a session spends a day writing a tool
    that already exists (16 September 2026).

    The percentages do not move: both maturities are INCONCLUSIVE. What moves is which sentence the owner
    reads on six of the seven boards.
    """
    cov = S.coverage(); bad = []
    for rid, c in sorted(cov.items()):
        gap, mat = c.get("gap_category"), c.get("maturity")
        if gap == "SOURCE_OR_APPLICABILITY_UNRESOLVED" and mat == "GENERATED_ONLY":
            bad.append("%s: the gap category says the source or the applicability is unresolved and the "
                       "maturity says nothing verifies it" % rid)
        if gap == "NONE" and mat not in ("ENFORCED", "VERIFIED_MANUALLY"):
            bad.append("%s: gap category NONE with maturity %s" % (rid, mat))
    assert not bad, "; ".join(bad)


def t_one_render_converges_when_a_rule_judges_a_page_the_same_run_writes():
    """A generated page judged against the copy of another generated page that this very run replaced.

    TST-001 and SGN-002 are decided by comparing `PCB-BRING-UP.md` and `PCB-PROTOTYPE-UNKNOWNS.md` with what
    the registry renders, and the per-board status pages print that decision out of `out/rule-audit/<L>.json`.
    Rendering both groups from one snapshot meant a run that CORRECTED a stale bring-up page still published
    seven status pages saying it was stale, and a second identical run was needed to agree with itself
    (16 September 2026: board C read TST-001 INCONCLUSIVE on a page written the same second as the document
    that satisfies it). A document set that does not converge in one write is a document set nobody can check.

    Executed against the real tree: the bring-up page is made stale, one write is run, and the result must be
    a tree `--check` accepts. The fixture is restored whatever happens."""
    import shutil, tempfile
    bring = os.path.join(DOCS, "PCB-BRING-UP.md")
    audit = os.path.join(TOOLS, "out", "rule-audit")
    need(bring, "the bring-up page has not been rendered yet")
    keep = tempfile.mkdtemp()
    shutil.copy(bring, os.path.join(keep, "bring.md"))
    # Only the page this rule damages is restored. The status pages the run rewrites are left as written,
    # because a converged tree is the correct outcome and putting an older copy back would un-converge it.
    try:
        open(bring, "a", encoding="utf-8").write("\n<!-- a hand edit, which is what this rule exists to catch -->\n")
        w = subprocess.run([sys.executable, os.path.join(TOOLS, "rules_render.py")],
                           capture_output=True, text=True, cwd=os.path.dirname(TOOLS))
        assert w.returncode == 0, (w.stdout + w.stderr)[-600:]
        c = subprocess.run([sys.executable, os.path.join(TOOLS, "rules_render.py"), "--check"],
                           capture_output=True, text=True, cwd=os.path.dirname(TOOLS))
        assert c.returncode == 0, \
            "one write did not converge: the status pages still disagree with the registry\n%s" % (c.stdout + c.stderr)[-600:]
    finally:
        shutil.copy(os.path.join(keep, "bring.md"), bring)


def t_the_status_pages_are_rendered_apart_from_the_pages_the_rules_judge():
    """The mechanism behind the rule above, so a refactor cannot fold the two groups back together."""
    src = open(os.path.join(TOOLS, "rules_render.py"), encoding="utf-8").read()
    assert "def render(out_dir=None, board_docs=True, generated=True)" in src, \
        "render() no longer separates the generated documents from the board status pages"
    body = src[src.index("def main(argv):"):]
    assert "board_docs=False" in body and "generated=False" in body, "main renders both groups from one snapshot"
    assert "_refresh_audit()" in body, "the audit is not refreshed between the two groups"


def t_a_remediation_that_is_done_carries_no_gap():
    """17 September 2026, the second time: the register counted five finished remediations in the morning, and
    two more this evening. A remediation whose action begins DONE is finished work, and a gap category other
    than NONE beside it puts that work back into the register and into the ETA page derived from it. The words
    and the category have to agree, so this asks them."""
    import os, sys, yaml
    tools = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cov = yaml.safe_load(open(os.path.join(tools, "pcb_rules_coverage.yaml"), encoding="utf-8"))["coverage"]
    bad = []
    for rid, e in sorted(cov.items()):
        act = str(((e or {}).get("remediation") or {}).get("action") or "").strip()
        if act.upper().startswith("DONE") and (e or {}).get("gap_category") not in (None, "NONE"):
            bad.append("%s: its remediation says DONE and its gap category is %s" % (rid, e.get("gap_category")))
    assert not bad, "the register counts finished work:\n  " + "\n  ".join(bad)


def t_the_routed_board_gate_decides_the_route_and_nothing_else():
    """A composite verdict decides every rule the coverage map points at it, so it must measure all of them.

    18 September 2026. `hardset-routed-board-gate` says one thing, in its own note: "routed board: hard and
    unrouted must both be zero". That is RTE-002's acceptance criteria word for word. RTE-001 is a different
    question, whether the board's design rules are inside a dated capability record from the fabricator, and
    `fab_limits.py` was written for exactly that; but the coverage map named BOTH verdicts for RTE-001 and the
    worst of the two decides, so on board B, whose `fab_limits` reads PASS on 24 checks with the note "every
    rule this board is designed to is inside the fabricator's capability for its own copper weight", RTE-001
    read FAIL. What failed was the route: hard 0, unrouted 416. Board B was recorded as designed to rules the
    fabricator cannot make because its router had not finished, which is the composite-verdict defect of 16
    September in a third place, and it is the reason this rule is mechanical rather than remembered.

    Board P is the control: its RTE-001 failure is `fab_limits` FAIL with 5 classes under capability, on a
    board whose routed-board gate reads hard 0 and unrouted 0, and it stays a failure after this correction.
    """
    cov = S.coverage()
    named = sorted(rid for rid, c in cov.items()
                   if S.ROUTE_GATE in [n.strip() for n in
                                       str(((c.get("verification") or {}).get("verdict")) or "").split(",") if n.strip()])
    assert named == ["RTE-002"], (
        "%s decides %s. It measures the ROUTE (hard and unrouted on the filled routed board), which is "
        "RTE-002's criteria; every other rule it is named for inherits a failure about something it does not "
        "ask. Give that rule its own instrument." % (S.ROUTE_GATE, named))


def t_a_verdict_that_decides_several_rules_says_what_it_measures_for_each():
    """Two of the five shared verdicts were deciding a rule they do not measure (18 September 2026).

    `hardset-routed-board-gate` failed RTE-001 on board B for its 416 unrouted connections, and
    `impedance_check` passed STK-001 on three boards with a denominator of zero pairs. Both were mappings made
    in one line with no sentence saying what the tool measures for the second rule, and where a rule names
    several verdicts the WORST decides, so the error is silent in both directions.

    The general property cannot be checked mechanically: nothing here can read a tool and a criteria sentence
    and decide whether one measures the other. What CAN be held mechanically is that the question was asked.
    A verdict named by more than one rule is a claim that one measurement answers both, and every rule making
    that claim carries `_shared_verdict_why` saying, in its own entry, what that tool measures for IT. The
    three that remain were each checked against their boards' current readings when this rule was written:
    `check_contracts_<letter>` (RF-002, SCH-003), `jlc_certify_<letter>` and `lcsc_fill` (CMP-002, SUP-001),
    and `intent_return_path` (RET-001, RET-002).
    """
    cov = S.coverage()
    by = {}
    for rid, c in cov.items():
        for n in [x.strip() for x in str(((c.get("verification") or {}).get("verdict")) or "").split(",") if x.strip()]:
            by.setdefault(n, []).append(rid)
    missing = []
    for verdict, rules in sorted(by.items()):
        if len(rules) < 2: continue
        for rid in sorted(rules):
            if not (cov[rid].get("_shared_verdict_why") or "").strip():
                missing.append("%s (shares %s with %s)" % (rid, verdict, ", ".join(r for r in sorted(rules) if r != rid)))
    assert not missing, (
        "a verdict decides every rule the map points at it, so these rules owe a `_shared_verdict_why` saying "
        "what that one tool measures for each of them: %s" % "; ".join(missing))


def t_the_coverage_map_names_the_registry_it_was_written_against():
    """A stamp in a file a person reads must describe the thing beside it (18 September 2026).

    `pcb_rules_coverage.yaml` carried `rule_set_fingerprint: 88f207606ad2945a` from the day it was written,
    while the registry computed `ff8151db3576437b`. Nothing reads the stamp, so nothing was wrong with any
    verdict; what was wrong is that a reader comparing the two would conclude the map belongs to a rule set
    this project does not have. The fingerprint covers the DECIDING fields only, so this asks for an edit
    exactly when a rule's demands change and never when a source or a rationale is written down."""
    import os, sys, re
    TOOLSDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, TOOLSDIR)
    import rules_lib as R
    txt = open(os.path.join(TOOLSDIR, "pcb_rules_coverage.yaml"), encoding="utf-8").read()
    m = re.search(r'^rule_set_fingerprint:\s*"([0-9a-f]+)"', txt, re.M)
    assert m, "the coverage map carries no fingerprint stamp at all"
    assert m.group(1) == R.fingerprint(), (
        "the coverage map says it was written against rule set %s and the registry computes %s: update the "
        "stamp in the change that moved the rules" % (m.group(1), R.fingerprint()))


def t_a_reading_that_answers_for_every_board_says_why_it_is_the_sets():
    """THE SIBLING OF `_shared_verdict_why` ON THE OTHER AXIS (20 September 2026). That rule holds one
    verdict named by several RULES; this one holds one verdict answering for several BOARDS, which is the
    defect this project has now found five times: DOC-001 split on the 16th, CMP-002, SUP-001 and DFM-001 on
    the 17th, DOC-002 on the 18th, and **DFA-001 on the 20th**, where one `assembly_set` verdict counting 42
    unchecked footprints over seven boards was the deciding reading for all seven and hid board E5's own
    PASS. The 18 September sweep that said there was no fifth instance was looking at the rules whose verdict
    NAME carries a letter; DFA-001's per-board verdicts are named `assembly_set` and told apart by the
    directory they sit in, so that sweep could not see it.

    The general property is not mechanical either: nothing here can read a tool and decide whether one
    measurement is honestly the set's. What IS mechanical is that the question was asked. The open-pairs
    audit already reports, from the evidence PATHS, every rule whose reading serves more than one board; a
    rule in that list is a claim that the set has one answer, and it carries `_set_level_why` in its own
    coverage entry saying why. OUT-001 is the true case: the order set is ONE artefact and a board cannot
    have its own answer about it.
    """
    from harness import Skip
    sys.path.insert(0, TOOLS)
    import open_pairs as O
    res = O.collect()
    if not res["boards"]: raise Skip("this tree holds no rule audit to classify")
    cov = S.coverage()
    missing = []
    for rid, n in res["set_readings"]:
        if n < 2: continue
        if not ((cov.get(rid) or {}).get("_set_level_why") or "").strip():
            missing.append("%s (one reading counted on %d boards)" % (rid, n))
    assert not missing, (
        "a reading that answers for every board is a claim that the set has one answer, so these rules owe a "
        "`_set_level_why` in the coverage map saying why a board cannot have its own: %s" % "; ".join(missing))
