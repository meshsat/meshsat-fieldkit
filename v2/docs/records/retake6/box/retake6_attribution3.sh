#!/usr/bin/env bash
# retake6 (MESHSAT-1357): the cell the two swapped-netlist attempts could not give (check_contracts.py refuses a netlist
# whose provenance does not name the schematic and generator of the tree, and read every contract UNJUDGED). Method
# changed: a scratch clone of MAIN 6ec37197, whose schematics, netlists and provenance agree, with set 6's tx_inhibit.py
# and the maker documents set 6 filed under v2/vendor (the walk cites them) copied in from 73ae2f21. Everything else is
# main's. NOT EVIDENCE: nothing is copied into any tree's evidence folders.
set -u
D=/root/retake6/attr; cell=walk-set6_tree-main; rm -rf $D/$cell $D/out/$cell; mkdir -p $D/out/$cell
export PYTHONDONTWRITEBYTECODE=1
MAIN=6ec37197; CAND=73ae2f2104c98bc39e5194f82a31e8862e12dbb5
git clone -q /root/r8int6/repo $D/$cell && git -C $D/$cell checkout -q $MAIN || { echo "clone failed"; exit 2; }
cd $D/$cell
git show $CAND:v2/ecad/tools/tx_inhibit.py > v2/ecad/tools/tx_inhibit.py
for f in $(git diff --name-only --diff-filter=A $MAIN $CAND -- v2/vendor); do mkdir -p $(dirname $f); git show $CAND:$f > $f; done
git status --short > $D/out/$cell-swapped.txt
( cd v2/ecad/pcb-a-power-a23 && VERDICT_DIR=$D/out/$cell timeout 900 python3 ../tools/check_contracts.py $D/$cell/v2/ecad > $D/out/$cell.log 2>&1; echo "exit $?" >> $D/out/$cell.log )
python3 - $D/out $cell <<'PY'
import json, os, sys
o, cell = sys.argv[1], sys.argv[2]
print("== %s (changed against main: %s)" % (cell, " ".join(l.strip() for l in open(os.path.join(o, cell + "-swapped.txt")))[:600]))
for L in "abcdep":
    p = os.path.join(o, cell, "inhibit_chain_%s.verdict.json" % L)
    if not os.path.exists(p): print("   %s: no reading written" % L.upper()); continue
    d = json.load(open(p))
    print("   %s: %-12s of %-3s %s" % (L.upper(), d["verdict"], d["denominator"], json.dumps(d["counts"], sort_keys=True)))
    for e in d.get("evidence") or []: print("        - %s" % str(e)[:300])
PY
grep -c "STALE\|MISSING" $D/out/$cell.log
date -u +%FT%TZ > /root/retake6/done-attr3
