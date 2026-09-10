#!/usr/bin/env bash
# part_reconcile.sh <project dir> <name>: after part_stage2.sh: on out/part/merged.kicad_pcb remove the boundary conflicts (shorts and crossings between
# the partitions' tracks, the unknot mechanism), clean up, close what that opened with the board-wide stub router, DRC, and leave the board as
# out/part/reconciled.kicad_pcb with its DRC json; prints RECONCILE hard/open lines and RECONCILE-DONE.
set -uo pipefail
cd "$1"; N="$2"; W=$PWD/out/part; B=$W/reconciled.kicad_pcb; cp $W/merged.kicad_pcb $B
cp $N.kicad_pro $W/reconciled.kicad_pro; cp $N.kicad_pro $W/merged.kicad_pro
# The one hard set scores the reconcile (10 September 2026, round-two red teams C1); it counted six types in a heredoc.
score() {   # board, report -> "hard unrouted"
  ../tools/drc.sh "$1" "$2" || { echo "999999 999999"; return; }
  local c; c=$(mktemp); python3 ../tools/hardset.py "$2" post --counts "$c" >/dev/null || { rm -f "$c"; echo "999999 999999"; return; }
  cat "$c"; rm -f "$c"
}
echo "RECONCILE merged: $(score $B $W/rec-0.json)"
for i in 1 2 3; do
  python3 ../tools/unknot.py $B $W/rec-$((i - 1)).json 2>&1 | grep unknot
  python3 ../tools/cleanup_dangling.py $B 2>&1 | grep cleanup
  echo "RECONCILE after rip $i: $(score $B $W/rec-$i.json)"
  read H _ < <(score $B $W/rec-$i.json)
  [ "$H" -eq 0 ] && break
done
cp $B $W/rec-before-stub.kicad_pcb   # 10 Sep 2026 (E7, appendix 32.89): the closures are judged, not kept blind
STUB_LAYERS=F.Cu,In2.Cu,In3.Cu,B.Cu STUB_GRID=0.2 STUB_WIN_SCALE=25 STUB_MAXN=80000000 nice -n 10 python3 ../tools/stub_router.py $B $W/rec-$i.json > $W/rec-stub.log 2>&1 || echo "stub router CRASHED ($W/rec-stub.log)"; grep -E 'closed|FAILED|stub_router' $W/rec-stub.log | tail -5
echo "RECONCILE after stub, before accept: $(score $B $W/rec-final.json)"
# Every other finish judges the stub router's work and this one did not: E7 kept 29,985 items that closed five nets and
# the finish then spent an hour in straighten.py. stub_accept drops the closures a DRC finds in a hard violation and, since
# 9 September, any whose item count is out of proportion to the net (STUB_MAX_ITEMS).
python3 ../tools/stub_accept.py $W/rec-before-stub.kicad_pcb $B $W/rec-final.json 2>&1 | grep stub_accept
echo "RECONCILE after accept: $(score $B $W/rec-final.json)"
echo "RECONCILE-DONE $(date -u +%H:%M:%S)"
