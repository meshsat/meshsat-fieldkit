#!/usr/bin/env bash
# retake6 (MESHSAT-1357): what moved RF-002's readings, the walk or the netlists? Commit 910da406 of set 6 changed board
# B's circuit AND tx_inhibit.py (two logic families added, J_QMX moved from OWED to ACCESSORIES, U221 declared, AO3400 read
# as an N-FET), so the reading alone cannot say which of the two moved a row. Two scratch clones, neither of them the
# re-take's, each with ONE thing swapped, check_contracts.py run with VERDICT_DIR outside both:
#   walk-main_netlists-set6   the clone at 73ae2f21 with tx_inhibit.py as main 6ec37197 has it
#   walk-set6_netlists-main   the clone at 73ae2f21 with every board's schematic, netlist, its provenance and its intent
#                             file as main 6ec37197 has them (the sheets and the other declarations of set 6 stay)
# The two other cells are the tracked readings: main's (taken 13:22 UTC) and the re-take's. THESE ARE NOT EVIDENCE: a
# tree with a swapped file is no candidate, and nothing here is copied into any tree's evidence folders.
set -u
D=/root/retake6/attr; rm -rf $D; mkdir -p $D/out
export PYTHONDONTWRITEBYTECODE=1
MAIN=6ec37197; CAND=73ae2f2104c98bc39e5194f82a31e8862e12dbb5
for cell in walk-main_netlists-set6 walk-set6_netlists-main; do
  git clone -q /root/r8int6/repo $D/$cell && git -C $D/$cell checkout -q $CAND || { echo "clone failed for $cell"; continue; }
  if [ $cell = walk-main_netlists-set6 ]; then
    git -C $D/$cell show $MAIN:v2/ecad/tools/tx_inhibit.py > $D/$cell/v2/ecad/tools/tx_inhibit.py
  else
    # the schematic goes with its netlist: check_contracts.py refuses a netlist whose provenance names another schematic
    # than the tree holds (the first attempt swapped the netlists alone and read 56 contracts UNJUDGED, 6 boards absent)
    ( cd $D/$cell && for f in $(git ls-files 'v2/ecad/pcb-*/out/*.net' 'v2/ecad/pcb-*/out/*.net.prov.json' 'v2/ecad/pcb-*/out/*-intent.json' 'v2/ecad/pcb-*/*.kicad_sch'); do
        git cat-file -e $MAIN:$f 2>/dev/null && git show $MAIN:$f > $f; done )
  fi
  git -C $D/$cell status --short > $D/out/$cell-swapped.txt
  mkdir -p $D/out/$cell
  ( cd $D/$cell/v2/ecad/pcb-a-power-a23 && VERDICT_DIR=$D/out/$cell timeout 900 python3 ../tools/check_contracts.py $D/$cell/v2/ecad > $D/out/$cell.log 2>&1; echo "exit $?" >> $D/out/$cell.log )
done
python3 - $D/out <<'PY'
import json, os, sys
o = sys.argv[1]
for cell in ("walk-main_netlists-set6", "walk-set6_netlists-main"):
    print("== %s (swapped: %s)" % (cell, " ".join(l.strip() for l in open(os.path.join(o, cell + "-swapped.txt")))[:400]))
    for L in "abcdep":
        p = os.path.join(o, cell, "inhibit_chain_%s.verdict.json" % L)
        if not os.path.exists(p): print("   %s: no reading written" % L.upper()); continue
        d = json.load(open(p))
        print("   %s: %-12s of %-3s %s" % (L.upper(), d["verdict"], d["denominator"], json.dumps(d["counts"], sort_keys=True)))
        for e in d.get("evidence") or []: print("        - %s" % str(e)[:300])
PY
date -u +%FT%TZ > /root/retake6/done-attr
