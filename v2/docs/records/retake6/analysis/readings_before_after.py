#!/usr/bin/env python3
"""retake6: every tracked reading the re-take changed (v2/ecad/pcb-*/routed/*.verdict.json), before (at the commit
given, read with `git show`) and after (the file in the tree): verdict, denominator, counts, and the evidence lines
where the two differ. Read only. Usage, from the repository root: readings_before_after.py <commit before>
"""
import sys, json, subprocess, os
sys.dont_write_bytecode = True
base = sys.argv[1]
names = subprocess.run(["git", "diff", "--name-only", base, "--", "v2/ecad"], capture_output=True, text=True, check=True).stdout.split()
names = sorted(n for n in names if "/routed/" in n and n.endswith(".verdict.json"))
moved = same = 0
for n in names:
    r = subprocess.run(["git", "show", "%s:%s" % (base, n)], capture_output=True, text=True)
    a = json.loads(r.stdout) if r.returncode == 0 else None
    b = json.load(open(n, encoding="utf-8"))
    board = n.split("/")[2]; tool = os.path.basename(n)[:-len(".verdict.json")]
    va = (a or {}).get("verdict"); vb = b.get("verdict")
    ca = (a or {}).get("counts"); cb = b.get("counts")
    da = (a or {}).get("denominator"); db = b.get("denominator")
    ea = list((a or {}).get("evidence") or []); eb = list(b.get("evidence") or [])
    changed = (va, ca, da, ea) != (vb, cb, db, eb)
    tag = "RESULT MOVED" if va != vb else ("content moved" if changed else "same result, same counts, same evidence")
    if va != vb: moved += 1
    elif not changed: same += 1
    print("%-18s %-22s %s" % (board, tool, tag))
    print("     before: %-12s of %-5s %s  (taken %s, writer %s)" % (va, da, json.dumps(ca, sort_keys=True), (a or {}).get("ts"), ((a or {}).get("writer") or {}).get("sha16")))
    print("     after:  %-12s of %-5s %s  (taken %s, writer %s)" % (vb, db, json.dumps(cb, sort_keys=True), b.get("ts"), (b.get("writer") or {}).get("sha16")))
    if ea != eb:
        for e in ea:
            if e not in eb: print("       - gone: %s" % str(e)[:400])
        for e in eb:
            if e not in ea: print("       + new:  %s" % str(e)[:400])
print("\n%d readings; result moved %d; same result with other counts or evidence %d; unchanged in result, counts and evidence %d"
      % (len(names), moved, len(names) - moved - same, same))
