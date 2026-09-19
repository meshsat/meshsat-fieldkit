#!/usr/bin/env python3
"""The decisions are data as well as prose (MESHSAT-862, 17 September 2026).

The record `v2/docs/OWNER-DECISIONS-2026-09-11.md` carries each decision with its evidence, its options and
their costs, in the order they were asked. It cannot answer the question that decides what this project can
finish, which is WHAT IS OPEN AND WHAT DOES EACH ONE HOLD UP, because that answer is spread over 2,400 lines
and several of the decisions were re-measured days after they were asked. `pcb_decisions.yaml` is the index
and `decisions_render.py` generates the page; these are the rules that stop the index falling behind the
record it indexes.
"""
import os, re, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import decisions_render as D
import rules_lib as R
from harness import need


def _record():
    p = os.path.join(D.RR.DOCS, "OWNER-DECISIONS-2026-09-11.md")
    need(p, "the decisions record is not in this tree")
    return open(p, encoding="utf-8", errors="replace").read()


def t_every_decision_in_the_record_is_in_the_register():
    """A decision written into the record and not registered is one nobody can count. The numbers are read
    from the record's own headings, which is where a new decision is written first."""
    txt = _record()
    nums = set()
    for line in txt.splitlines():
        if not line.startswith("#"): continue
        m = re.search(r"\bDecision (\d+)\b", line, re.I) or re.match(r"^##\s+(\d+)\.\s", line)
        if m: nums.add(int(m.group(1)))
    have = {d["n"] for d in D.load()}
    missing = sorted(n for n in nums if n not in have and n >= 23)
    assert not missing, ("these decisions are in the record and not in pcb_decisions.yaml: %s" % missing)


def t_every_open_decision_says_what_it_holds_and_what_is_being_asked():
    for d in D.load():
        if d.get("status") != "open": continue
        assert str(d.get("ask", "")).strip(), "decision %d is open and does not say what is being asked" % d["n"]
        # A decision may legitimately hold no rule TODAY and still be open: decision 33 asks whether the
        # numbers a rule is passing against were ever anybody's requirement, which is a question about the BAR
        # rather than about the copper. It has to say so in the register rather than leave the field empty,
        # because an empty field is how a note comes to look like a decision.
        assert d.get("blocks") or str(d.get("holds_nothing_today", "")).strip(), \
            ("decision %d is open, names no rule it holds and does not say why: a decision that blocks "
             "nothing and does not say so is a note" % d["n"])


def t_every_rule_a_decision_names_exists_and_every_board_is_in_the_manifest():
    """A register that names a rule the registry does not have counts pairs that cannot exist."""
    import rules_status as S
    ids = {r["id"] for r in R.load()["rules"]}
    boards = {b.lower() for b in (S.manifest().get("boards") or {})}
    bad = []
    for d in D.load():
        for rid, bs in (d.get("blocks") or {}).items():
            if rid not in ids: bad.append("decision %d names rule %s, which does not exist" % (d["n"], rid))
            for b in bs:
                if str(b).lower() not in boards:
                    bad.append("decision %d names board %s, which is not in the manifest" % (d["n"], b))
    assert not bad, "; ".join(bad)


def t_a_decision_the_register_calls_open_is_not_one_the_rule_already_passes_everywhere():
    """The register is not allowed to hold a rule hostage after the rule started passing. This reads the audit
    this tree last computed, so it says nothing at all on a tree that has never computed one."""
    state = D._state()
    if not state: raise __import__("harness").Skip("no rule audit in this tree")
    stale = []
    for d in D.load():
        if d.get("status") != "open": continue
        for rid, bs in (d.get("blocks") or {}).items():
            res = {state.get((rid, str(b).lower())) for b in bs}
            if res and res <= {"PASS"}:
                stale.append("decision %d still claims to hold %s, which passes on %s"
                             % (d["n"], rid, ", ".join(str(b).upper() for b in bs)))
    assert not stale, "; ".join(stale)


def t_the_page_is_generated_and_not_hand_maintained():
    """The page says what each open decision HOLDS, and that half is computed from this tree's evidence, so
    the rule is a question about the evidence as much as about the page. A tree that carries only the
    committed verdicts renders a different page for a true reason: the set-level readings live in
    `v2/ecad/out/`, which is gitignored, so a staged tree has 111 inconclusive where this one has 79. Found
    by running the suite where KiCad is (20 September 2026); a rule that cannot see its input declares that
    rather than reporting the page as hand-edited, which is the house rule applied to the suite itself."""
    import subprocess, glob as _glob
    need(os.path.join(D.RR.DOCS, "OWNER-DECISIONS-OPEN.md"), "the page has not been rendered yet")
    if not _glob.glob(os.path.join(os.path.dirname(TOOLS), "out", "*.verdict.json")):
        raise __import__("harness").Skip(
            "this tree carries no set-level verdicts, so the page's 'what it holds' half is computed "
            "from less evidence than the committed page was")
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "decisions_render.py"), "--check"],
                       capture_output=True, text=True, cwd=os.path.dirname(TOOLS))
    assert p.returncode == 0, (p.stdout + p.stderr)[-500:]
