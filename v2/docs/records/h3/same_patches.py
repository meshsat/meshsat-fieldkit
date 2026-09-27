#!/usr/bin/env python3
"""The commits H2-RESPONSE.md first cited, against the commits of main that carry the same patches (MESHSAT-1357).

Written by the H3 pages worker, 27 September 2026, for correction 6 of the H3 pages. H2-RESPONSE.md and REGENERATE.md
section 9 cited five commits of branch `fnd/h2m` as it stood when they were written (kept locally as `h2m-backup`,
never pushed). The branch was re-integrated on main, where the same changes have other ids. `git patch-id --stable`
hashes a commit's diff without its id, date or parent, so two commits with one patch id carry the same change. This
script prints both ids of every pair with their patch ids and subjects, asserts that each pair agrees, and says
whether each commit is an ancestor of main. It then lists the files in which the two trees of each pair differ (the
two lines started from different commits, ef144760 and 31cd29b9) and asserts that none is under v2/ecad, so a result
the pages quote as run "at" a cited commit was run on the same tools, registries and netlists as main's commit holds.
It reads only. It needs a clone that holds branch `h2m-backup`; where the old commits are absent it says so and checks
nothing for that pair.

Usage (from the repository root): python3 v2/docs/records/h3/same_patches.py [main's ref, default HEAD]
"""
import subprocess, sys

PAIRS = [("992f2bc2", "a54b1f4d"), ("248b951d", "90314d99"), ("2a3a1451", "ed988ba8"), ("1221262e", "ecfe5414"),
         ("44b87208", "5d568a66"), ("0ca85df3", "9d2f8dce")]
MAIN = sys.argv[1] if len(sys.argv) > 1 else "HEAD"


def git(*a, inp=None):
    r = subprocess.run(["git"] + list(a), capture_output=True, input=inp)
    return r.returncode, r.stdout


def patch_id(c):
    rc, d = git("show", c)
    return git("patch-id", "--stable", inp=d)[1].decode().split()[0][:16] if rc == 0 else None


bad = 0
print("same_patches: against %s (%s)" % (MAIN, git("rev-parse", "--short=8", MAIN)[1].decode().strip()))
print("%-10s %-10s %-18s %-18s %-9s %-9s %s" % ("cited", "on main", "patch id (cited)", "patch id (main)", "cited in",
                                               "main's in", "subject"))
for old, new in PAIRS:
    po, pn = patch_id(old), patch_id(new)
    subj = git("log", "-1", "--format=%s", new)[1].decode().strip()
    ao = "absent" if po is None else ("main" if git("merge-base", "--is-ancestor", old, MAIN)[0] == 0 else "not main")
    an = "main" if git("merge-base", "--is-ancestor", new, MAIN)[0] == 0 else "not main"
    print("%-10s %-10s %-18s %-18s %-9s %-9s %s" % (old, new, po or "-", pn or "-", ao, an, subj[:90]))
    if po is not None and po != pn: bad += 1
    if an != "main": bad += 1
print("files in which the trees of a pair differ:")
for old, new in PAIRS:
    rc, names = git("diff", "--name-only", old, new)
    if rc != 0:
        print("  %s against %s: not compared (a commit is absent)" % (old, new)); continue
    names = names.decode().split()
    ecad = [n for n in names if n.startswith("v2/ecad/")]
    print("  %s against %s: %d file(s), %d under v2/ecad: %s" % (old, new, len(names), len(ecad), " ".join(names)))
    if ecad: bad += 1
print("result: %s" % ("every pair carries one patch, main holds the second id of each, and no pair's trees differ "
                      "under v2/ecad" if not bad else "%d DISAGREEMENT(S)" % bad))
sys.exit(1 if bad else 0)
