#!/usr/bin/env python3
"""A committed board's class table against the one its generator writes (20 September 2026).

It is a REPORT and decides no rule, so these rules are about the READER rather than about the boards: that it
parses both shapes the generators use, that it never answers from a guess, and that the set's own list is
accurate on the tree as it stands. The gates all read the PROJECT FILE for a class, so a board cut before a
class existed is routed at Default geometry on every net that class was meant to govern, and the register
cannot see it, because it reads a verdict and not a date."""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ECAD = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import class_table_age as cta


def t_it_reads_a_dict_table_and_a_list_table(tmp=None):
    """THE DEFECTIVE FIXTURE FOR THE PARSER. Two generators in this set write CLASSES as a dict keyed by name
    (A and B) and four write a list of tuples; a reader that knows one shape answers nothing about half the
    set and says 'match' while it does it."""
    import tempfile
    d = tempfile.mkdtemp()
    a = os.path.join(d, "dict_gen.py"); b = os.path.join(d, "list_gen.py")
    open(a, "w").write('CLASSES = {"USB": (0.1,), "PACK": (0.2,)}\n')
    open(b, "w").write('CLASSES = [("USB", 0.1, 0.2), ("PACK", 0.3, 0.4)]\n')
    assert cta.generator_classes(a) == ["USB", "PACK"], cta.generator_classes(a)
    assert cta.generator_classes(b) == ["USB", "PACK"], cta.generator_classes(b)


def t_a_generator_with_no_table_is_unreadable_and_never_a_match():
    """THE ACCEPTABLE FIXTURE'S OTHER HALF: silence is not agreement. A generator whose table this cannot find
    must be REPORTED, because 'no classes found' and 'no classes missing' are the same empty list."""
    import tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, "no_table.py")
    open(p, "w").write("# this generator declares nothing\nX = 1\n")
    assert cta.generator_classes(p) is None


def t_the_sets_own_class_ages_are_what_the_tool_says():
    """The report run against this tree. It is held to the list because the list is the finding: four of the
    six boards are routed at a class table their generator has moved past, and in three of them the missing
    class is exactly the one whose rule fails on the readiness page (A's SENSE and ANA-001, B's PANEL and
    PWR-003 with RF and RF-001, P's PACK and PI-001). When a board is re-cut its row moves to `match` and this
    list is edited in the same commit, which is the point: the edit is the record that the gap closed."""
    got = {r["board"]: sorted(r.get("predates") or []) for r in cta.rows(ECAD) if r.get("readable")}
    want = {"a": ["SENSE"], "b": ["PANEL", "RF"], "c": [], "d": ["SENSE"], "e": [], "p": ["PACK"]}
    assert got == want, "class ages moved: %s" % got
