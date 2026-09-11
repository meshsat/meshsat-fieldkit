#!/usr/bin/env python3
"""A comment appended to a generator line must not swallow the calls that follow it on that line.

This is the fourth time the project has paid for this shape, so it stops being a warning in section 8
of the handover and becomes a check:

  5 Sep 2026, the 0x43 patch put `# ...` after `ina219("U14", ...)` and swallowed C18 and C19; the
  generator died at layout and the chain quietly rebuilt from the previous schematic.
  5 Sep 2026, A21 run 11: a `# ...` note took the trailing comma off a jog tuple and the chain
  stopped at the placement generator.
  11 Sep 2026, twice in one session: `# E96: ...` after R141 swallowed R142 and R143 on PCB-A, and
  `# TI specifies 255 mOhm ...` after R12 swallowed R13 on PCB-B. The first cost a chain run on the
  box before anything reported it, as a KeyError on a reference that had silently stopped existing.

The generators put several calls on one line on purpose, which is what makes them readable as a
netlist. That is fine. What is never fine is a `#` in the middle of such a line, because everything
after it is gone and nothing in Python complains: the file still parses, the board still builds, and
the part is simply absent. A comment about one call on a shared line goes on its own line above.

This does not parse Python: it is a lexical rule about a line's shape, which is exactly why it can
catch a line that still compiles. Strings that merely contain a `#` are skipped by taking the first
`#` that is not inside quotes.

Usage: test_swallowed_calls.py [files...]   (default: every generator)   -> exit 1 on any finding
"""
import sys, os, re, glob

CALL = re.compile(r'\b(?:r|c|ic|part|nfet|pfet|ph|ina219|ina226|led|sw|tp|jp)\s*\(\s*"')


def split_comment(line):
    """The line's code and its comment, at the first `#` that is not inside a string literal."""
    q = None
    for i, ch in enumerate(line):
        if q:
            if ch == "\\":
                continue
            if ch == q:
                q = None
        elif ch in "\"'":
            q = ch
        elif ch == "#":
            return line[:i], line[i:]
    return line, ""


def findings(paths):
    out = []
    for path in paths:
        for n, line in enumerate(open(path, errors="replace"), 1):
            code, comment = split_comment(line)
            if not comment:
                continue
            # a call BEFORE the # and a call AFTER it: the second one is dead
            if CALL.search(code) and CALL.search(comment):
                out.append((path, n, line.rstrip()))
    return out


def main(argv):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = argv or sorted(glob.glob(os.path.join(here, "gen_sch_*.py")) +
                           glob.glob(os.path.join(here, "gen_pcb_*.py")) +
                           glob.glob(os.path.join(here, "gen_footprints_*.py")))
    bad = findings(paths)
    for path, n, line in bad:
        print("FAIL  %s:%d a comment swallows the calls after it on this line" % (os.path.basename(path), n))
        print("      %s" % line[:160])
        print("      move the comment to its own line above.")
    print("test_swallowed_calls: %s (%d generator file(s), %d finding(s))"
          % ("PASS" if not bad else "%d FAIL" % len(bad), len(paths), len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
