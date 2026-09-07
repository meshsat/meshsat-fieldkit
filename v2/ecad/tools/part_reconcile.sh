#!/usr/bin/env bash
# part_reconcile.sh <project dir> <name>: after part_stage2.sh: on out/part/merged.kicad_pcb remove the boundary conflicts (shorts and crossings between
# the partitions' tracks, the unknot mechanism), clean up, close what that opened with the board-wide stub router, DRC, and leave the board as
# out/part/reconciled.kicad_pcb with its DRC json; prints RECONCILE hard/open lines and RECONCILE-DONE.
set -uo pipefail
cd "$1"; N="$2"; W=$PWD/out/part; B=$W/reconciled.kicad_pcb; cp $W/merged.kicad_pcb $B
score() { kicad-cli pcb drc --severity-all --format json -o "$2" "$1" >/dev/null 2>&1; python3 - "$2" <<'PY'
import json, collections, sys
d = json.load(open(sys.argv[1])); c = collections.Counter(v['type'] for v in d['violations'])
print("hard %d unconnected %d %s" % (sum(c[t] for t in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'hole_to_hole', 'copper_edge_clearance')), len(d.get('unconnected_items', [])), dict((k, v) for k, v in c.items() if v and k in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance'))))
PY
}
echo "RECONCILE merged: $(score $B $W/rec-0.json)"
for i in 1 2 3; do
  python3 ../tools/unknot.py $B $W/rec-$((i - 1)).json 2>&1 | grep unknot
  python3 ../tools/cleanup_dangling.py $B 2>&1 | grep cleanup
  echo "RECONCILE after rip $i: $(score $B $W/rec-$i.json)"
  H=$(python3 -c "import json,collections,sys; d=json.load(open(sys.argv[1])); c=collections.Counter(v['type'] for v in d['violations']); print(sum(c[t] for t in ('clearance','shorting_items','tracks_crossing','hole_clearance','hole_to_hole','copper_edge_clearance')))" $W/rec-$i.json)
  [ "$H" -eq 0 ] && break
done
STUB_LAYERS=F.Cu,In2.Cu,In3.Cu,B.Cu STUB_GRID=0.2 STUB_WIN_SCALE=25 STUB_MAXN=80000000 nice -n 10 python3 ../tools/stub_router.py $B $W/rec-$i.json > $W/rec-stub.log 2>&1 || echo "stub router CRASHED ($W/rec-stub.log)"; grep -E 'closed|FAILED|stub_router' $W/rec-stub.log | tail -5
echo "RECONCILE after stub: $(score $B $W/rec-final.json)"
echo "RECONCILE-DONE $(date -u +%H:%M:%S)"
