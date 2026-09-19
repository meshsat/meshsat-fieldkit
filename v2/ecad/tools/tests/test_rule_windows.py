#!/usr/bin/env python3
"""A rule must be about the code and not about how much prose sits between two lines (18 September 2026).

Twice in one evening a rule failed because a COMMENT was added: `test_stub_zone_obstacle` sliced 2,500
characters after `zpoly(` and a new paragraph pushed the line it was looking for out of the slice, and
`test_prelay` sliced 700 after `_WANT = ` and the pour-obstacle and lock flags landed in between. Both were
repaired by asking for the two lines and their ORDER instead of their distance.

The silent direction is worse than the noisy one. A window that is generous enough not to break is also
generous enough to find its literal inside a DIFFERENT function after an edit, and then the rule passes while
the property it names is gone. Nothing in the suite would say so.

This file does not convert the remaining slices; it stops the number growing and says what it is, which is the
FIXTURE_DEBT idiom applied to a different debt. `harness.block(src, anchor)` is what a conversion uses."""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from harness import block

# The count on the tree this rule was written against, 18 September 2026. It may fall and never rise.
DECLARED = 83
WINDOW = re.compile(r"\[\s*_?[ijk]\s*:\s*_?[ijk]\s*\+\s*\d+\s*\]")


def _count():
    n, where = 0, {}
    for f in sorted(os.listdir(HERE)):
        if not (f.startswith("test_") and f.endswith(".py")): continue
        hits = WINDOW.findall(open(os.path.join(HERE, f), encoding="utf-8").read())
        if hits: n += len(hits); where[f] = len(hits)
    return n, where


def t_the_number_of_fixed_window_rules_never_rises():
    n, where = _count()
    assert n <= DECLARED, (
        "fixed-size source windows in the suite: %d against the declared %d. A rule that slices N characters "
        "after an anchor breaks when a comment is added and passes wrongly when code is removed; ask for the "
        "two lines and their order, or use harness.block(). Worst files: %s"
        % (n, DECLARED, sorted(where.items(), key=lambda kv: -kv[1])[:5]))


def t_the_declared_number_is_the_real_one_and_not_a_ceiling_nobody_lowers():
    """A debt declared far above the truth is not a ratchet, it is a licence. Keep it within five."""
    n, _ = _count()
    assert DECLARED - n <= 5, (
        "the declared debt is %d and the tree has %d: lower DECLARED to %d in the same change that converts them"
        % (DECLARED, n, n))


def t_the_helper_returns_the_construct_and_not_a_byte_count():
    src = ("def one():\n    X = 1\n    # a comment that would blow a small window\n"
           + "    # more prose\n" * 40 + "    use(X)\n\n\ndef two():\n    other(X)\n")
    b = block(src, "X = 1")
    assert "use(X)" in b, "the helper stopped short of the end of the function"
    assert "other(X)" not in b, "the helper ran past the function it was asked about"
    assert block(src, "not in this file at all") == "", "a missing anchor must not return the whole file"


def t_a_generated_document_whose_inputs_are_absent_is_not_rewritten_empty():
    """THE DEFECTIVE FIXTURE is a tree with no intent file: rendering the bring-up sheet there must REFUSE.
    THE ACCEPTABLE FIXTURE is this tree, where the intent files exist and the page renders.

    18 September 2026, found by running the suite on a box in an exact checkout of the runner's HEAD:
    `PCB-BRING-UP.md` is generated from each board's `out/<stem>-intent.json`, `out/` is untracked, and on a
    fresh checkout the page renders as six empty sections. A plain `rules_render` run there would have written
    that over the committed procedure and left the suite green, because the empty page is what the registry
    renders on that host. It is the sequence a person follows the first time current goes through a board that
    has never been powered."""
    import importlib.util, os, sys, tempfile
    TOOLSDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, TOOLSDIR)
    import rules_render as RR, rules_lib as R
    import rules_status as S

    body = RR.bringup_doc(R.load(), S.coverage())
    assert "## Board A" in body and len(body) > 2000, "the acceptable fixture did not render"

    # the defective fixture: the same renderer pointed at a tree with no intent file
    real = RR.HERE
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "ecad"))
        try:
            RR.HERE = os.path.join(d, "ecad", "tools")
            try:
                RR.bringup_doc(R.load(), S.coverage())
                raise AssertionError("a tree with no intent file rendered a bring-up sheet anyway")
            except RR.MissingInput as e:
                assert "intent" in str(e), str(e)
        finally:
            RR.HERE = real


# The unguarded reads of a flag's value on the tree this rule was written against, 18 September 2026.
FLAG_READS = 63   # 71 until 19 September 2026: hardset.py first, then dc_drop and place_audit. hardset is
                  # the instrument every board gate and every guard reads its counts from, and `--score`
                  # with nothing after it raised IndexError inside it; the other two are read by every
                  # finish. The number only ever comes down.
_FLAG = re.compile(r"(?:argv|a)\[(?:argv|a)\.index\(")


def _flag_reads():
    n, where = 0, {}
    here = os.path.dirname(HERE)
    for f in sorted(os.listdir(here)):
        if not f.endswith(".py"): continue
        hits = [l for l in open(os.path.join(here, f), encoding="utf-8").read().splitlines()
                if _FLAG.search(l) and "+ 1]" in l and "len(" not in l]
        if hits: n += len(hits); where[f] = len(hits)
    return n, where


def t_the_number_of_unguarded_flag_reads_never_rises():
    """A flag given no value must be answered, not raised (`verdict.opt`).

    `assembly_set.py --checklist` with nothing after it raised IndexError, the crash guard wrote an
    INCONCLUSIVE verdict naming the exception, and rule DFA-001 read as though seven boards had been judged.
    A gate that cannot tell a missing argument from a finding is worse than one that refuses to start. This
    does not convert the hundred that exist; it stops the number growing and names the helper."""
    n, where = _flag_reads()
    assert n <= FLAG_READS, (
        "unguarded reads of a flag's value: %d against the declared %d. Use verdict.opt(argv, flag, default), "
        "which also refuses to take the next flag as a value. Worst files: %s"
        % (n, FLAG_READS, sorted(where.items(), key=lambda kv: -kv[1])[:5]))


def t_the_helper_exists_and_answers_all_three_shapes():
    import importlib.util
    spec = importlib.util.spec_from_file_location("v_opt", os.path.join(os.path.dirname(HERE), "verdict.py"))
    v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
    assert v.opt(["x", "--a", "1"], "--a") == "1", "the value is not read"
    assert v.opt(["x", "--a"], "--a", "D") == "D", "a flag at the end of the line still raises or returns wrong"
    assert v.opt(["x", "--a", "--b"], "--a", "D") == "D", "the next flag is taken as the value"
    assert v.opt(["x"], "--a", "D") == "D", "an absent flag does not fall back"
