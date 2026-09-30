#!/usr/bin/env python3
"""Bind a filed energy basis (or the power path's record) to the tip its accepted check checked (L3-R2, MESHSAT-1357, 30
September 2026; CHECK-3 of L3-R2, B1).

A check is accepted for one tip of stream l3plane. A filed file counts only if it is byte identical to the file of the
same path at that tip, read with `git show <tip>:<path>` from this repository, and only if the check itself, filed at its
sha, reads "accepted: yes" on its first line and names that tip in its head ("tip `<tip>`"). set_energy_basis.py writes an
entry only when all of that holds; the hold (conditional/cond.py) and the gate (render_l3r2.py) verify it again every time
they run, so a file changed later, or a tip this repository does not carry, lifts no hold.

  verify(entry, root, repo, need_outputs)  -> (True, '') or (False, why)
  tip_sha16(repo, tip, path)               -> the sha256/16 of `git show tip:path`, or None
"""
import functools
import hashlib
import os
import subprocess


def sha16_bytes(b):
    return hashlib.sha256(b).hexdigest()[:16]


@functools.lru_cache(maxsize=None)
def tip_sha16(repo, tip, path):
    r = subprocess.run(["git", "-C", repo, "show", "%s:%s" % (tip, path)], capture_output=True)
    return sha16_bytes(r.stdout) if r.returncode == 0 else None


def verify(v, root, repo, need_outputs=False):
    if not v: return False, "not filed"
    tip = str(v.get("tip") or "")
    if not tip: return False, "it names no checked tip"
    if not v.get("check"): return False, "it names no check"
    if need_outputs and not v.get("outputs"): return False, "it names no outputs"
    for path, sha in [(v.get("record"), v.get("sha16"))] + [(o.get("path"), o.get("sha16")) for o in v.get("outputs") or []]:
        p = os.path.join(root, str(path))
        if not os.path.isfile(p) or sha16_bytes(open(p, "rb").read()) != str(sha):
            return False, "%s is not held at %s in this tree" % (path, sha)
        at_tip = tip_sha16(repo, tip, str(path))
        if at_tip is None: return False, "the checked tip %s carries no %s in this repository" % (tip, path)
        if at_tip != str(sha): return False, "%s differs from the file of that path at the checked tip %s" % (path, tip)
    cp = os.path.join(root, str(v["check"]))
    if not os.path.isfile(cp) or sha16_bytes(open(cp, "rb").read()) != str(v.get("check_sha16")):
        return False, "the check %s is not held at %s in this tree" % (v["check"], v.get("check_sha16"))
    head = open(cp, encoding="utf-8").read().split("\n")
    if head[0].strip() != "accepted: yes": return False, "its check reads %r, not 'accepted: yes'" % head[0].strip()
    if not any(("tip `%s`" % tip) in l for l in head[:12]): return False, "its check does not name the tip %s" % tip
    return True, ""
