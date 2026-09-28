#!/usr/bin/env python3
"""The commit in which each rail's declared currents took the value they have now (p3bind, MESHSAT-1357).

For every board's intent file: the commits that touched it between e3aedb25 and HEAD, oldest first, and for every rail
whose typical or peak current at HEAD differs from e3aedb25's (or that e3aedb25 did not declare), the first commit
whose copy of the file carries today's pair. Reads git and prints; writes nothing.
Usage: rail_commits.py
"""
import os, sys, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "v2", "ecad", "tools"))
import constraints_bound as CB
BASE = "e3aedb25"


def git(*a):
    r = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def rails_at(commit, rel):
    raw = git("show", "%s:%s" % (commit, rel))
    try: return (json.loads(raw) or {}).get("rails") or {}
    except ValueError: return {}


def pair(r):
    return (float(r.get("amps_typ") or 0), float(r.get("amps_peak") or 0)) if r else None


def main():
    RW = CB.load_calc()
    for letter in RW.ORDER:
        if letter in RW.NO_INTENT: continue
        rel = RW.BOARDS[letter][0]
        commits = [l.split(" ", 1) for l in git("log", "--reverse", "--format=%h %s", "%s..HEAD" % BASE, "--", rel).splitlines()]
        then, now = rails_at(BASE, rel), rails_at("HEAD", rel)
        print("## Board %s, %s: %d commit(s) since %s" % (letter.upper(), rel, len(commits), BASE))
        for h, s in commits: print("  %s %s" % (h, s[:150]))
        for net, r in now.items():
            if pair(r) == pair(then.get(net)) or pair(r) == (0.0, 0.0): continue
            first = next((h for h, _s in commits if pair(rails_at(h, rel).get(net)) == pair(r)), "?")
            print("  - %-16s %s -> %s, first in %s" % (net, pair(then.get(net)), pair(r), first))
            print("      note: %s" % str(r.get("note") or "")[:900])
        print()


if __name__ == "__main__":
    main()
