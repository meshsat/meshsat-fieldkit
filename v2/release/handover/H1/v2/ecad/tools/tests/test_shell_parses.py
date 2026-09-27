#!/usr/bin/env python3
"""Every shell tool must parse (MESHSAT-862, 15 September 2026): a finish.sh with a missing `fi` reached origin for one commit
while the suite passed, because nothing in it asked bash. `bash -n` on every .sh under tools is that question."""
import glob, os, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def t_every_shell_tool_parses():
    bad = []
    for f in sorted(glob.glob(os.path.join(TOOLS, "**", "*.sh"), recursive=True)):
        r = subprocess.run(["bash", "-n", f], capture_output=True, text=True)
        if r.returncode != 0: bad.append("%s: %s" % (os.path.relpath(f, TOOLS), r.stderr.strip()[:120]))
    assert not bad, "\n".join(bad)
