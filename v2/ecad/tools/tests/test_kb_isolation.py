#!/usr/bin/env python3
"""The knowledge base may never decide anything (MESHSAT-862, 10 September 2026).

The rule is one sentence: a retrieved passage is model-selected evidence, so it may inform a person
or a proposal and it may never appear on the path that judges a board. Four sibling projects on
this estate enforce the same separation, and the reason it is a test rather than a note is the
omoikane pattern their constitution states: an invariant survives only when a script or a CHECK
guards it. Three guards, one per way the rule could be broken:

  t_no_gate_imports_the_kb          a gate, check, finish or chain script importing or shelling out
                                    to kb_search puts retrieval on a verdict path
  t_truth_cap_is_a_constraint       the cap on a retrieved signal is a CHECK in the schema, not a
                                    number a caller is trusted to apply
  t_search_never_writes_a_verdict   kb_search.py does not import verdict.py at all: the tool that
                                    proposes evidence has no way to write a verdict about it

They are text checks, so they run anywhere, with no store, no KiCad and no network.
"""
import os, re, glob
from harness import Skip   # noqa: F401  (kept: a future guard may need to skip)

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB = os.path.join(TOOLS, "kb")

# Everything that decides something about a board, by the naming of this tree.
GATE_GLOBS = ("check_pcb_*.py", "*_gate.py", "hardset.py", "verdict.py", "impedance_check.py",
              "dc_drop.py", "intent_checks.py", "check_contracts.py", "verify_deliverable.py",
              "place_audit.py", "routeflow.py", "finish_*.sh", "full*.sh", "route_*.sh",
              "quality_pass.sh", "pair_match.sh", "part_*.sh", "drc.sh", "chain_*.sh")


def t_no_gate_imports_the_kb():
    hits = []
    for pat in GATE_GLOBS:
        for path in glob.glob(os.path.join(TOOLS, pat)):
            try:
                text = open(path, errors="replace").read()
            except OSError:
                continue
            for m in re.finditer(r"^(?!\s*#).*\b(kb_search|kb_verify|kb_ingest|kbdb|kbembed)\b.*$",
                                 text, re.M):
                line = m.group(0).strip()
                if line.startswith("#") or line.startswith("--"):
                    continue
                hits.append("%s: %s" % (os.path.basename(path), line[:110]))
    if hits:
        raise AssertionError("retrieval reached a verdict path, which is the one thing it may never "
                             "do:\n   " + "\n   ".join(hits[:10]))


def t_truth_cap_is_a_constraint():
    schema = open(os.path.join(KB, "schema.sql"), errors="replace").read()
    if "ck_truth_cap" not in schema or "CHECK (confidence <= 0.750)" not in schema:
        raise AssertionError("the schema no longer caps a retrieved signal below the action "
                             "threshold with a CHECK; a cap that lives only in the caller is a note")
    if "CONSTRAINT ck_advisory  CHECK (advisory = 1)" not in schema:
        raise AssertionError("the schema no longer forces every lookup to be advisory")


def t_search_never_writes_a_verdict():
    src = open(os.path.join(KB, "kb_search.py"), errors="replace").read()
    for m in re.finditer(r"^\s*(?:import|from)\s+verdict\b", src, re.M):
        raise AssertionError("kb_search.py imports verdict.py at %d: the thing that proposes "
                             "evidence must not be able to write a verdict on it" % m.start())
    if "TRUTH_CAP = 0.75" not in src:
        raise AssertionError("kb_search.py no longer declares the 0.75 cap it records with every lookup")
