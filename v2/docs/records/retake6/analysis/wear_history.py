#!/usr/bin/env python3
"""retake6: which parts reliability.py asks for (its wear set) on a board's committed netlist at several commits, so
the difference between two readings can be named part by part. Read only: it imports reliability.py for its own
WEAR pattern, prefix list and identity(), reads netlists with `git show`, and writes no verdict.

Usage, from the repository root: wear_history.py <letter> <commit> [<commit> ...]
"""
import sys, os, re, subprocess, fnmatch
sys.dont_write_bytecode = True
T = os.path.abspath("v2/ecad/tools"); sys.path.insert(0, T)
import reliability as REL, rules_lib as R, rules_status as S
import yaml


def show(commit, path):
    r = subprocess.run(["git", "show", "%s:%s" % (commit, path)], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def wear(txt):
    parts = {r: v for r, v in re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt)}
    return {r: parts[r] for r in parts if REL.WEAR.search(parts[r] or "") and R.ref_prefix(r) not in REL.NOT_WEAR_PREFIX
            and REL.WEAR.search(REL.identity(parts[r]))}


if __name__ == "__main__":
    L = sys.argv[1].lower(); commits = sys.argv[2:]
    m = S.manifest(); stem = m["boards"][L]["project"]
    pd = os.path.relpath(S._phase_dir(L, m), os.getcwd())
    net = os.path.join(pd, "out", stem + ".net")
    prev = None
    for c in commits:
        txt = show(c, net)
        rel = yaml.safe_load(show(c, "v2/ecad/tools/pcb_reliability.yaml") or "{}")
        classes = ((rel.get("boards") or {}).get(L) or {}).get("classes") or []
        if txt is None: print("%s: no %s" % (c, net)); continue
        w = wear(txt)
        cov = {r for r in w if len([k for k in classes if any(fnmatch.fnmatchcase(r, p) for p in (k.get("refs") or []))]) == 1}
        print("%s  %s: wear set %d, covered by exactly one declared class %d, classes declared %d (%s)" % (
            c, net, len(w), len(cov), len(classes), "; ".join(str(k.get("name")) for k in classes)))
        if prev is not None:
            for r in sorted(set(w) - set(prev)): print("     + %-10s %s" % (r, w[r][:150]))
            for r in sorted(set(prev) - set(w)): print("     - %-10s %s" % (r, prev[r][:150]))
        prev = w
