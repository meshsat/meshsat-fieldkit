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
