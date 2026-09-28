#!/usr/bin/env python3
"""A scratch view of a worktree, outside every tree, in which the drafts can be applied and SI-001 taken without
writing one byte of the worktree (stream w5si2, 28 September 2026, MESHSAT-1357).

WHAT IS COPIED (so that a draft or a tool may write it): v2/ecad/tools without its caches, the files at the top of
v2/vendor (SOURCES.yaml, sources.txt, vendor-status.txt, ibis-manifest.yaml and the like), the files at the top of
v2/docs, and .gitignore. WHAT IS LINKED (read only by everything run here): every board directory of v2/ecad, every
folder of v2/vendor and of v2/docs, and the rest of v2. The scratch view is no git repository, so nothing that dates a
file by its commit can be asked of it; the fixtures of the tests do that.

--no-models leaves the `ibis` folder of every maker out of the view: the state of a clean clone, of the public
repository and of a handover ZIP, whatever the worktree holds.

Usage: scratch_tree.py <worktree> <new scratch directory> [--no-models]
"""
import os, sys, shutil


def build(src, dst, models=True):
    assert not os.path.exists(dst), "%s exists: a scratch view is built fresh" % dst
    assert not os.path.abspath(dst).startswith(os.path.abspath(src) + os.sep), "the scratch view must lie outside the worktree"
    os.makedirs(os.path.join(dst, "v2", "ecad"))
    if os.path.exists(os.path.join(src, ".gitignore")): shutil.copy2(os.path.join(src, ".gitignore"), os.path.join(dst, ".gitignore"))
    v2 = os.path.join(src, "v2")
    for name in sorted(os.listdir(v2)):
        if name in ("ecad", "vendor", "docs"): continue
        os.symlink(os.path.join(v2, name), os.path.join(dst, "v2", name))
    for name in sorted(os.listdir(os.path.join(v2, "ecad"))):
        a, b = os.path.join(v2, "ecad", name), os.path.join(dst, "v2", "ecad", name)
        if name == "tools": shutil.copytree(a, b, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"), symlinks=True)
        elif os.path.isdir(a): os.symlink(a, b)
        else: shutil.copy2(a, b)
    for top in ("vendor", "docs"):
        os.makedirs(os.path.join(dst, "v2", top))
        for name in sorted(os.listdir(os.path.join(v2, top))):
            a, b = os.path.join(v2, top, name), os.path.join(dst, "v2", top, name)
            if not os.path.isdir(a): shutil.copy2(a, b); continue
            if top == "vendor" and os.path.isdir(os.path.join(a, "ibis")):
                os.makedirs(b)
                for sub in sorted(os.listdir(a)):
                    if sub == "ibis" and not models: continue
                    os.symlink(os.path.join(a, sub), os.path.join(b, sub))
            else:
                os.symlink(a, b)
    return dst


if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    d = build(os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), models="--no-models" not in sys.argv)
    print("scratch view %s of %s, the makers' models %s" % (d, os.path.abspath(sys.argv[1]),
                                                           "left out" if "--no-models" in sys.argv else "as the worktree holds them"))
