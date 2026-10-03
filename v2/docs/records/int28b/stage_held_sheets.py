#!/usr/bin/env python3
"""stage_held_sheets.py: stage the makers' held-back documents a fresh worktree lacks, from checkouts on the same host that already
hold them, verified by the pins the records carry (MESHSAT-1357, set 28, 3 October 2026). The `held/` folders are gitignored (the
documents' terms keep them out of the public tree), so a new worktree holds none, and every Layer 4 reader that pins one refuses:
l3batt/runtime.py under L4-E5's reproduction chain, L4-E11's TI and Nexperia sheets, L4-E9's Littelfuse 997 sheet, and the rest.
Nothing is fetched from anywhere: a file is copied only from a local checkout whose copy has the sha256 a record pins for that path.

Usage, from anywhere:  stage_held_sheets.py [--write] [<source checkout> ...]
  Without --write it reports. The sources default to every sibling worktree of this one (the parent directory of the repository
  root) plus the checkouts named in HELD_SOURCES (colon-separated), such as a main checkout. Exit 0 when every pinned held path is present and verified; 3 when one is still missing."""
import glob
import hashlib
import os
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
PATH = re.compile(r"v2/vendor/[A-Za-z0-9_./-]*/held/[A-Za-z0-9_.-]+\.[A-Za-z0-9]+")   # a file with an extension (a path built from a format string is found by the sha pass)
HEX = re.compile(r"\b[0-9a-f]{64}\b")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pins():
    """path -> set of sha256 the records' scripts pin for it: a hash on the SAME line as the path only (a hash on the next line
    may be another file's, as L4-E7's INA169 pin under its ZA path assignment is); a path with no same-line hash is left to the
    sha pass below, which stages a file whose sha256 a record carries anywhere."""
    out = {}
    for py in glob.glob(os.path.join(TOP, "v2/docs/records/**/*.py"), recursive=True):
        for l in open(py, encoding="utf-8", errors="replace").read().split("\n"):
            for p in PATH.findall(l):
                out.setdefault(p, set()).update(HEX.findall(l))
    return out


def main(argv):
    write = "--write" in argv
    srcs = [a for a in argv if not a.startswith("--")]
    if not srcs:
        parent = os.path.dirname(TOP)
        srcs = sorted(d for d in glob.glob(os.path.join(parent, "*")) if os.path.isdir(os.path.join(d, "v2", "vendor")) and os.path.realpath(d) != os.path.realpath(TOP))
        srcs += [d for d in os.environ.get("HELD_SOURCES", "").split(":") if d and os.path.isdir(os.path.join(d, "v2", "vendor"))]
    need = pins()
    present = staged = missing = 0
    for rel in sorted(need):
        dest = os.path.join(TOP, rel)
        want = need[rel]
        if not want:
            continue                      # no same-line pin: the sha pass decides
        if os.path.isfile(dest) and sha(dest) in want:
            present += 1
            continue
        found = None
        for s in srcs:
            c = os.path.join(s, rel)
            if os.path.isfile(c) and sha(c) in want:
                found = c
                break
        if not found:
            missing += 1
            print("MISSING  %s (pins %s; no verified copy among %d sources)" % (rel, ", ".join(h[:16] for h in sorted(want)), len(srcs)))
            continue
        if write:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(found, dest)
            if sha(dest) not in want:
                print("BAD COPY %s" % rel); missing += 1; continue
            staged += 1
            print("staged   %s  from %s" % (rel, os.path.relpath(found, os.path.dirname(TOP))))
        else:
            staged += 1
            print("would    %s  from %s" % (rel, os.path.relpath(found, os.path.dirname(TOP))))
    # second pass, by sha: a held file in a source whose sha256 a record pins under a path built at run time (a format string the
    # path scan cannot see, as L4-E7's held Samsung readings) is staged at its own relative path when that path is absent here
    allhex = set()
    for py in glob.glob(os.path.join(TOP, "v2/docs/records/**/*.py"), recursive=True):
        allhex.update(HEX.findall(open(py, encoding="utf-8", errors="replace").read()))
    by_sha = 0
    for s in srcs:
        for f in glob.glob(os.path.join(s, "v2/vendor/**/held/*"), recursive=True):
            rel = os.path.relpath(f, s)
            dest = os.path.join(TOP, rel)
            if need.get(rel) or os.path.isfile(dest) or not os.path.isfile(f):   # a named path with a same-line pin was handled above
                continue
            h = sha(f)
            if h not in allhex:
                continue
            if write:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copyfile(f, dest)
                if sha(dest) != h:
                    print("BAD COPY %s" % rel); missing += 1; continue
            by_sha += 1
            print("%s %s  from %s (pinned by sha %s)" % ("staged  " if write else "would   ", rel, os.path.relpath(s, os.path.dirname(TOP)), h[:16]))
    unpinned = sorted(r for r in need if not need[r])
    print("stage_held_sheets: %d held path(s) named by the records, %d with a same-line pin: %d present and verified, %d %s, %d missing; "
          "%d more %s by their pinned sha%s"
          % (len(need), len(need) - len(unpinned), present, staged, "staged" if write else "stageable", missing, by_sha,
             "staged" if write else "stageable", ("; left to the sha pass (no same-line pin): %s" % ", ".join(unpinned)) if unpinned else ""))
    return 3 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
