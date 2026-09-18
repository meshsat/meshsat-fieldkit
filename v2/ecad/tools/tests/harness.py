#!/usr/bin/env python3
"""Shared by the test runner and the tests, so `Skip` is one class however run.py was started (as a script it is __main__,
and a test importing `run` would get a second copy of the exception and every skip would read as a failure)."""


class Skip(Exception):
    """A test whose host cannot run it (no pcbnew, no kicad-cli, no scipy): reported, never a failure."""


def pre_router_source(tools):
    """The pre-router's whole source, the entry file and the pair_router package (split 15 September 2026)."""
    import sys
    sys.path.insert(0, tools); import pair_router
    return pair_router.source()


def need(path, why):
    """Skip a rule whose artefact is not on this host (a code-only checkout has no release/, no board, no appendix, no
    .git); the reason prints with the skip. 15 September 2026, red team round four H3: the Skip path written for that
    host had a NameError and five rules failed on a code-only archive."""
    import os
    if not os.path.exists(path): raise Skip("%s: %s" % (why, path))
    return path


def block(src, anchor, stops=("\ndef ", "\nclass ")):
    """The source from `anchor` to the end of the top-level construct holding it, for a rule about TWO LINES.

    A rule written as `src[src.find(anchor):][:700]` is not a rule about the code, it is a rule about how much
    prose sits between two lines: add a comment and it fails, remove code and it can start finding its literal
    inside a different function and pass for the wrong reason. It broke twice on 18 September 2026, in
    `test_stub_zone_obstacle` (a comment pushed `zpoly(via` past a 2,500-character slice) and in `test_prelay`
    (the pour-obstacle and lock flags landed between a set's declaration and the line that reads it), and 87
    slices of this shape were still in the suite when this was written.

    `stops` is the Python default; pass a shell's own boundary for a shell source. An anchor that is not there
    returns the empty string, so a rule keeps failing rather than passing on a slice it never found."""
    i = src.find(anchor)
    if i < 0: return ""
    return rest(src, i, stops, skip=len(anchor))


def rest(src, i, stops=("\ndef ", "\nclass "), skip=0):
    """`block` for a caller that already has the index, so an existing `i = src.find(...)` line stays as it is."""
    if i is None or i < 0: return ""
    j = len(src)
    for st in stops:
        k = src.find(st, i + skip)
        if k >= 0: j = min(j, k)
    return src[i:j]
