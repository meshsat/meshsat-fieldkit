#!/usr/bin/env python3
"""An owner-reserved choice reaches the owner as OPTIONS WITH A RECOMMENDATION, never as a question
(process control 5 of the owner's instruction of 16 September 2026, MESHSAT-862).

The owner has said the same thing twice in his own words: ask all the questions first, save the responses so
they are not lost, then do the work; and one decision per turn, with a full explanation, in language that does
not assume the field. What he has NOT asked for, and what this rule refuses, is a decision handed over as a
problem statement. A choice that reaches him without its options costed and without a recommendation is work
the session did not do, and it stops the boards while it sits there.

So every OPEN decision in the decisions file must carry at least two options and a recommendation. A decision
he has already ruled on needs neither, because the ruling replaces both.
"""
import os, re, sys

DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "docs")
DECISIONS = os.path.join(DOCS, "OWNER-DECISIONS-2026-09-11.md")


def _sections():
    """[(heading, body)] for every decision section of the file."""
    if not os.path.exists(DECISIONS): return []
    txt = open(DECISIONS, encoding="utf-8", errors="replace").read()
    parts = re.split(r"^## ", txt, flags=re.M)[1:]
    return [(p.split("\n", 1)[0].strip(), p.split("\n", 1)[1] if "\n" in p else "") for p in parts]


def t_every_open_decision_carries_at_least_two_options_and_a_recommendation():
    bad = []
    for head, body in _sections():
        h = head.upper()
        # The file's own convention, and the only one that can be read mechanically: an unanswered decision says
        # OPEN in its heading. Everything else in here is history, and a decision the owner has ruled on needs
        # neither options nor a recommendation, because the ruling replaces both.
        if "OPEN" not in h: continue
        low = body.lower()
        # options appear as a numbered list, a table of arms, or the word itself
        n_opts = len(re.findall(r"^\s*\d+\.\s+\*\*", body, flags=re.M)) or len(re.findall(r"^\|\s*\*\*?option", low, flags=re.M))
        if "option" not in low and n_opts < 2: bad.append("%s: no options at all" % head[:70])
        elif n_opts < 2 and len(re.findall(r"\boption\b", low)) < 2: bad.append("%s: fewer than two options" % head[:70])
        elif "recommend" not in low: bad.append("%s: options with no recommendation" % head[:70])
    assert not bad, ("open decisions that do not give the owner a costed choice:\n  " + "\n  ".join(bad))


def t_the_decisions_file_exists_and_is_not_empty():
    assert os.path.exists(DECISIONS), "the owner decisions file is gone"
    assert len(_sections()) >= 10, "the decisions file has lost its history"
