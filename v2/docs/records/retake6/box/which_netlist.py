#!/usr/bin/env python3
"""retake6: which netlist reliability.netlist_for picks per board in THIS tree, read only (no verdict is written).

reliability.py reads the newest <stem>*/out/<stem>.net by mtime and records no netlist, so the reading does not say
which file it judged. In a fresh clone every mtime is the checkout's, so this prints every candidate with its mtime and
sha256/16, the one the tool picks, and the netlist of the board's declared phase directory (rules_status._phase_dir),
and says whether they are the same file. Usage: which_netlist.py <v2/ecad/tools>
"""
import os, sys, glob, hashlib, json
T = os.path.abspath(sys.argv[1]); sys.path.insert(0, T)
import reliability as REL, rules_lib as R, rules_status as S
E = os.path.dirname(T)
m = S.manifest(); facts = R.board_facts()
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
ok = True
for L in m["boards"]:
    stem = (facts.get(L) or {}).get("project")
    c = sorted(p for p in glob.glob(os.path.join(E, stem + "*", "out", stem + ".net")) if os.path.isfile(p))
    pick = REL.netlist_for(stem, E)
    pd = S._phase_dir(L, m); want = os.path.join(pd, "out", stem + ".net")
    print("board %-2s stem %s" % (L.upper(), stem))
    for p in c:
        print("   candidate %-50s mtime_ns %d sha16 %s%s" % (os.path.relpath(p, E), os.stat(p).st_mtime_ns, sha(p), "  <- picked" if p == pick else ""))
    if not c: print("   no netlist (the tool says so in a note)")
    same = (pick is None and not os.path.exists(want)) or (pick is not None and os.path.realpath(pick) == os.path.realpath(want))
    print("   declared phase netlist %s: %s" % (os.path.relpath(want, E), "THE PICKED FILE" if same else "NOT the picked file"))
    ok = ok and same
print("every board's picked netlist is its declared phase's: %s" % ("yes" if ok else "NO"))
