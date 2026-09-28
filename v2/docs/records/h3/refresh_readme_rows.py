#!/usr/bin/env python3
"""Bring the rows of v2/docs/records/README.md in line with the files they name (MESHSAT-1357, 27 September 2026).

The coherence check of handover H3 (v2/docs/records/handover/H3-COHERENCE-CHECK.md, findings m2 and m12) found five
rows of the index quoting the sha256 of a file as it was one commit earlier (the H3 records were re-taken in the
source commit and the index was not), and ten rows naming files the commit does not hold. This script reads every
row of the section "Filed files", recomputes sha256 and size of the file it names, rewrites the two cells where they
differ, and reports every row whose file is absent from the tree or not tracked by git. It adds rows for new files
given on the command line as path::origin::cited-by (paths relative to v2/docs/records). It changes nothing else, and
with --check it writes nothing and exits 1 if any row would change.

Usage (any folder of the checkout): python3 v2/docs/records/h3/refresh_readme_rows.py [--check] [new rows ...]
"""
import hashlib, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REC = os.path.join(TOP, "v2/docs/records")
P = os.path.join(REC, "README.md")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split(" | ")]


def main(argv):
    check = "--check" in argv
    new = [a for a in argv if a != "--check"]
    tracked = set(subprocess.run(["git", "ls-files", "v2/docs/records"], cwd=TOP, capture_output=True, check=True)
                  .stdout.decode().splitlines())
    everything = set(subprocess.run(["git", "ls-files"], cwd=TOP, capture_output=True, check=True).stdout.decode().splitlines())
    L = open(P, encoding="utf-8").read().split("\n")
    start = next(i for i, l in enumerate(L) if l.strip() == "## Filed files")
    changed, absent, untracked, rows, last = [], [], [], 0, None
    for i in range(start, len(L)):
        l = L[i]
        if not l.startswith("| `"):
            continue
        c = cells(l)
        if len(c) < 5 or not (c[1].startswith("`") and len(c[1].strip("`")) == 64):
            continue
        if c[0].count("`") != 2 or " " in c[0]:
            continue                      # a row of another table (a source named by branch and path), not a filed file
        rel = c[0].strip("`")
        f = os.path.join(TOP, rel) if rel.startswith("v2/") else os.path.join(REC, rel)
        rows += 1
        if not rel.startswith("v2/"):
            last = i
        if not os.path.isfile(f):
            absent.append(rel); continue
        full = rel if rel.startswith("v2/") else "v2/docs/records/" + rel
        if full not in tracked and full not in everything:
            untracked.append(rel)
        b = open(f, "rb").read()
        sha, size = hashlib.sha256(b).hexdigest(), str(len(b))
        if c[1].strip("`") != sha or c[2] != size:
            changed.append((rel, c[1].strip("`")[:8], sha[:8], c[2], size))
            parts = l.split(" | ")
            parts[1] = "`%s`" % sha; parts[2] = size
            L[i] = " | ".join(parts)
    added = []
    have = {cells(l)[0].strip("`") for l in L[start:] if l.startswith("| `")}
    for spec in new:
        rel, origin, cited = spec.split("::")
        assert rel not in have, "%s has a row already" % rel
        b = open(os.path.join(REC, rel), "rb").read()
        L.insert(last + 1 + len(added), "| `%s` | `%s` | %d | %s | %s |" % (rel, hashlib.sha256(b).hexdigest(), len(b), origin, cited))
        added.append(rel)
    print("refresh_readme_rows: %d rows read; %d with a changed sha256 or size; %d added; %d name a file absent from the tree; "
          "%d name a file git does not track" % (rows, len(changed), len(added), len(absent), len(untracked)))
    for r in changed: print("  changed  %s  sha256 %s.. to %s.., bytes %s to %s" % r)
    for r in added: print("  added    %s" % r)
    for r in absent: print("  ABSENT   %s" % r)
    for r in untracked: print("  UNTRACKED %s" % r)
    if check:
        return 1 if (changed or added) else 0
    if changed or added:
        open(P, "w", encoding="utf-8").write("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
