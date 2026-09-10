#!/usr/bin/env python3
"""Shared by the test runner and the tests, so `Skip` is one class however run.py was started (as a script it is __main__,
and a test importing `run` would get a second copy of the exception and every skip would read as a failure)."""


class Skip(Exception):
    """A test whose host cannot run it (no pcbnew, no kicad-cli, no scipy): reported, never a failure."""
