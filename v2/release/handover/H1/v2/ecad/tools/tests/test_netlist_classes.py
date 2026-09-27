#!/usr/bin/env python3
"""A COMMITTED NETLIST THAT CARRIES NO NET CLASSES IS EVIDENCE READ AGAINST A TABLE IT DOES NOT HAVE.

20 September 2026. Proving that tonight's thirty declaration changes moved no net, the six boards' netlists
were regenerated and diffed against their committed ones. Five came back byte-identical in the body. Board
B's differed in 804 lines and every one was a net header's CLASS: **its committed netlist has all 1,852 nets
in `Default`**, where its own generator assigns DIFF100 to 96 of them, USB to 237, PWR to 55 and HV to 14.

That is the 18 September finding in another place (the project file's class table was a second copy on five
boards, and the next phase of each is the first to carry its generator's own), and it was found by hand
because nothing asks the question. Anything judged from board B's netlist classes today reads `Default` for
every net: its impedance work, its pair classes and its RF class arrive with B23.

The rule REPORTS rather than blocks, because board B is knowingly in that state and its phase transition is
what fixes it. What it must not do is stay silent: a board whose evidence is read against a class table it
does not carry is a reading of something other than the board.
"""
import os, re, sys, glob

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ECAD = os.path.dirname(TOOLS)

# EMPTY SINCE 20 SEPTEMBER 2026, AND THE RULE BELOW IS WHY IT IS EMPTY. Board B was the one entry: its
# committed netlist held all 1,852 nets in `Default` while its generator assigns four real classes, because
# the netlist was exported at B19 and never re-exported. Regen 7 rebuilt all six at their declared phases and
# board B's came back with 804 lines different, EVERY ONE of them a net class (DIFF100, Default, HV, PWR,
# USB). The entry was removed because the rule refused to let it stand: a name on this list that is no longer
# in that state is a blanket over a board that has moved on, which is what `t_the_known_list_is_accurate_and_
# not_a_blanket` exists to catch, and it caught it in the same run that fixed it.
KNOWN = {}


def _classes(path):
    """{class: count} over the net headers of a KiCad s-expression netlist."""
    out = {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "[^"]*"\) \(class "([^"]*)"\)', open(path, encoding="utf-8", errors="replace").read()):
        out[m.group(1)] = out.get(m.group(1), 0) + 1
    return out


def t_a_committed_netlist_that_carries_one_class_for_every_net_is_named():
    """A board whose netlist assigns exactly one class, and that class `Default`, is reported with its reason.

    Not a failure: board B is deliberately at a phase that predates its class table. A board in that state
    and NOT in the known list is the finding, because it means a phase moved and nobody noticed.
    """
    unexplained = []
    for net in sorted(glob.glob(os.path.join(ECAD, "pcb-*", "out", "*.net"))):
        c = _classes(net)
        if not c: continue                       # a netlist this rule cannot read says nothing about the board
        if set(c) == {"Default"}:
            stem = os.path.basename(net)[:-4]
            if stem not in KNOWN:
                unexplained.append("%s: every one of its %d nets is in Default and no reason is recorded"
                                   % (stem, c["Default"]))
    assert not unexplained, ("a committed netlist with no class table is evidence read against a table it "
                             "does not have: " + "; ".join(unexplained))


def t_the_known_list_is_accurate_and_not_a_blanket():
    """A name on the known list must still BE in that state, or the list is hiding a board that has moved on."""
    stale = []
    for stem, why in sorted(KNOWN.items()):
        hits = glob.glob(os.path.join(ECAD, "pcb-*", "out", stem + ".net"))
        if not hits: continue                    # the netlist is not in this tree, which this rule cannot judge
        c = _classes(hits[0])
        if c and set(c) != {"Default"}:
            stale.append("%s carries %d class(es) now (%s) and is still listed as carrying none: %s"
                         % (stem, len(c), ", ".join(sorted(c)), why))
    assert not stale, "; ".join(stale)
