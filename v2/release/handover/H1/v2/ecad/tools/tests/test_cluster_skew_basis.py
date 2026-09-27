#!/usr/bin/env python3
"""A TYPED SKEW IS A CLAIM ABOUT ONE BOARD'S OWN MESH (MESHSAT-862, 21 September 2026).

`cluster(skew=)` sizes a barrel cluster on how unevenly the site shares its current, and the number can only
come from a mesh solved on a ROUTED board. That makes it the same shape as the typed barrel coordinates that
went stale on board E this morning: true of the placement it was measured on, and a claim about every
placement after it. E36's landed board reads CELL_F's site at **1.72** where the generator declares 1.325, so
the one call in this tree that carries a skew already carries a stale one, four days after it was measured.

Nothing can check the VALUE from the source, and a rule that pretends to would be worse than none. What a
rule can check is that the number arrives with its BASIS: the board it was measured on and the date, beside
the call, so the next reader knows what to re-measure instead of inheriting a number with no provenance. The
existing call names E21's routed board, 19 September 2026, both solved currents and the board-file key, which
is what this rule asks of the next one.
"""
import os, re, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
from harness import block

# TO THE END OF THE LINE, never to the first `)`: a call reads `cluster("CELL_F", (-113.4, -104.11),
# amps=1.809, skew=1.325, ...)` and a non-greedy match stops inside the coordinate tuple, so the first
# version of this rule found NO calls at all and its acceptable half passed on a denominator of zero. Its own
# defective fixture caught it, which is what the pair is for.
CALL = re.compile(r"\.cluster\((.*)$", re.M)
BOARD = re.compile(r"\b[A-EP]\d{1,3}\b")                       # a phase: A98, E36, D12, P10
DATE = re.compile(r"\b\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) \d{4}\b")


def _generators():
    for f in sorted(os.listdir(TOOLS)):
        if f.startswith("gen_pcb_") and f.endswith(".py"):
            yield f, open(os.path.join(TOOLS, f), encoding="utf-8").read()


def _calls_with_skew(src):
    """Every `cluster(...)` call that passes a skew, with the twelve lines above it as its basis."""
    out = []
    for m in CALL.finditer(src):
        if "skew=" not in m.group(1): continue
        head = src[:m.start()].splitlines()[-12:]
        out.append((m.group(1), "\n".join(l for l in head if l.strip().startswith("#"))))
    return out


def t_every_typed_skew_names_the_board_and_the_date_it_was_measured_on():
    """THE ACCEPTABLE FIXTURE IS THIS TREE, and it is the stronger half: the one call that carries a skew
    names E21's routed board, 19 September 2026 and the two solved currents it came from."""
    bad = []
    for f, src in _generators():
        for args, basis in _calls_with_skew(src):
            if not (BOARD.search(basis) and DATE.search(basis)):
                bad.append("%s: cluster(%s) carries a skew with no basis above it" % (f, args[:70]))
    assert not bad, ("a typed skew is a measurement on ONE routed board and goes stale like a typed "
                     "coordinate; name the board and the date above the call:\n  " + "\n  ".join(bad))


def t_a_skew_with_no_basis_is_named():
    """THE DEFECTIVE FIXTURE: the same detector over a source that passes a skew with only a bare comment.
    Without it the rule above would pass on a tree with no skew in it at all, which is a rule about nothing."""
    src = ("# the count comes from the current\n"
           "_x = PowerCopper(b, n, P).cluster(\"CELL_F\", (1.0, 2.0), amps=1.8, skew=1.325, drill=0.5)\n")
    found = _calls_with_skew(src)
    assert found, "the detector does not see a cluster call carrying a skew"
    args, basis = found[0]
    assert not (BOARD.search(basis) and DATE.search(basis)), \
        "the detector accepts a skew whose comment names neither a board nor a date"
    good = ("# 19 September 2026, MEASURED ON E21's ROUTED BOARD: the solved mesh puts 1.198 A and 0.611 A\n"
            "# through the two barrels this call placed, so the site shares 1.809 A about two to one.\n"
            "_x = PowerCopper(b, n, P).cluster(\"CELL_F\", (1.0, 2.0), amps=1.8, skew=1.325, drill=0.5)\n")
    args2, basis2 = _calls_with_skew(good)[0]
    assert BOARD.search(basis2) and DATE.search(basis2), "the detector refuses a basis that is there"
