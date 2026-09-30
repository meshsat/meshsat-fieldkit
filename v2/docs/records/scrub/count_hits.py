#!/usr/bin/env python3
"""Counts of the scrub's patterns in the tracked files, by token class (MESHSAT-1357, 30 September 2026).

Usage: count_hits.py [--commit <rev>]
  without --commit: the working tree's bytes of every tracked file; with it: the blobs of that commit.
Prints, per class, the instances and the files, then the files with their counts, then every tracked ZIP under
v2/release/handover/ with its entries that carry a pattern (the entry's path under its version folder). An instance is
one path or one name (scrub_lib.DETECT); nothing printed repeats a removed value.
"""
import io, os, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scrub_lib as S

TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()


def git(*a):
    return subprocess.run(["git", "-C", TOP] + list(a), capture_output=True, check=True).stdout


def files(commit):
    if not commit:
        for p in git("ls-files", "-z").decode().split("\0"):
            if p and os.path.isfile(os.path.join(TOP, p)): yield p, open(os.path.join(TOP, p), "rb").read()
        return
    for rec in git("ls-tree", "-r", "-z", commit).split(b"\0"):
        if not rec: continue
        meta, p = rec.split(b"\t", 1)
        if meta.split()[1] != b"blob": continue
        yield p.decode(), git("cat-file", "blob", meta.split()[2].decode())


def main(argv):
    commit = argv[argv.index("--commit") + 1] if "--commit" in argv else None
    per, tot, zips = {}, {c: [0, 0] for c in S.CLASSES}, {}
    for p, b in files(commit):
        if p.endswith(".zip") and p.startswith("v2/release/handover/"):
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                zips[p] = sorted((e.split("/", 1)[1], S.count(z.read(e))) for e in z.namelist()
                                 if not e.endswith("/") and S.count(z.read(e)))
            continue
        c = S.count(b)
        if not c: continue
        per[p] = c
        for k, v in c.items(): tot[k][0] += v; tot[k][1] += 1
    print("count_hits: %s" % ("commit " + git("rev-parse", commit).decode().strip()[:12] if commit else "the working tree"))
    print("tracked files with a pattern: %d; instances: %d" % (len(per), sum(v[0] for v in tot.values())))
    for k in S.CLASSES: print("  %-20s %4d instance(s) in %3d file(s)" % (k, tot[k][0], tot[k][1]))
    print("files:")
    for p in sorted(per): print("  %s  %s" % (p, ", ".join("%s %d" % (k, v) for k, v in sorted(per[p].items()))))
    print("handover ZIPs:")
    for z in sorted(zips):
        print("  %s: %d entr%s with a pattern" % (z, len(zips[z]), "y" if len(zips[z]) == 1 else "ies"))
        for e, c in zips[z]: print("    %s  %s" % (e, ", ".join("%s %d" % (k, v) for k, v in sorted(c.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
