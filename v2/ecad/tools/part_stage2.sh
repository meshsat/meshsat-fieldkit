#!/usr/bin/env bash
# part_stage2.sh <project dir> <name> <passes> <timeout s> <group list>: after the GLOBAL job: import its session and lock its nets, export the DSN
# again (planes and power layers as the route scripts do), re-partition, route every listed group concurrently, wait, merge, DRC, report.
# Env: FR_PLANE_NETS (csv) and FR_POWER_LAYERS as for route_one.sh. Marker STAGE2-DONE.
set -uo pipefail
cd "$1"; N="$2"; P="$3"; T="$4"; PARTS="$5"; W=$PWD/out/part; PJ=$W/part.json
echo "stage2: groups [$PARTS] passes $P timeout $T"; cp $N.kicad_pro out/$N-preroute.kicad_pro 2>/dev/null   # every board KiCad loads or checks needs the project file beside it (net classes, via sizes), or the DRC reports the default class
python3 ../tools/ses_import_lock.py out/$N-preroute.kicad_pcb $W/GLOBAL/route.ses $PJ GLOBAL $W/stage1.kicad_pcb 2>&1 | grep -v -E "Debug|leak"
cp $N.kicad_pro $W/stage1.kicad_pro
bash ../tools/dsn_export.sh $W/stage1.kicad_pcb $W/stage2-raw.dsn "${FR_PLANE_NETS:-}" "${FR_POWER_LAYERS:-}" 2>&1 | grep -v -E "Debug|leak"
python3 ../tools/dsn_partition.py $W/stage1.kicad_pcb $W/stage2-raw.dsn $W/stage2.dsn $W/part2.json 2>&1 | grep -v -E "Debug|leak" | grep -v "^partition [A-Z]"
# 10 September 2026 (B19, appendix 32.93): PART_SEQ=1 routes the groups ONE AT A TIME, importing and locking each result
# before the next job's DSN is exported, so a group sees its predecessors' copper as obstacles. Concurrent jobs cannot:
# each one only knows the locked copper of stage 1, so their boundaries collide, and on B19 the merge of five concurrent
# regions carried 1,121 hard violations that three rip passes could only bring to about 400. Sequential costs wall clock
# (five jobs in a row rather than five at once) and buys a merge that has nothing to reconcile.
for G in $PARTS; do rm -rf $W/$G $W/route-$G.log; done   # 10 Sep 2026: the merge and the report used to pick up the sessions and logs of a PREVIOUS pass for a group this pass never reached
if [ "${PART_SEQ:-0}" = 1 ]; then
  for G in $PARTS; do
    echo "stage2: sequential group $G"
    bash ../tools/route_part.sh $W $W/stage2.dsn $G $P $T $W/part2.json > $W/route-$G.log 2>&1
    [ -s $W/$G/route.ses ] || { echo "stage2: $G wrote no session, stopping the chain here"; break; }
    python3 ../tools/ses_import_lock.py $W/stage1.kicad_pcb $W/$G/route.ses $W/part2.json $G $W/stage1.kicad_pcb 2>&1 | grep -v -E "Debug|leak"
    bash ../tools/dsn_export.sh $W/stage1.kicad_pcb $W/stage2-raw.dsn "${FR_PLANE_NETS:-}" "${FR_POWER_LAYERS:-}" 2>&1 | tail -1
    python3 ../tools/dsn_partition.py $W/stage1.kicad_pcb $W/stage2-raw.dsn $W/stage2.dsn $W/part2.json 2>&1 | tail -1
  done
else
  for G in $PARTS; do bash ../tools/route_part.sh $W $W/stage2.dsn $G $P $T $W/part2.json > $W/route-$G.log 2>&1 & done
  wait
fi
for G in $PARTS; do tail -2 $W/route-$G.log; done
# 10 September 2026: in sequential mode every group's session was ALREADY imported and locked into stage1 as it finished, so
# merging the same sessions again laid each group's copper a second time on top of itself (B19: 1,770 DEVW tracks added to a
# board that already carried them, and the duplicate pieces read as clearance and shorting violations). The sequential board
# is stage1 as it stands.
if [ "${PART_SEQ:-0}" = 1 ]; then
  cp $W/stage1.kicad_pcb $W/merged.kicad_pcb
  echo "stage2: sequential mode, the merged board is stage1 (each group was imported and locked as it finished)"
else
  ARGS=""; for G in $PARTS; do [ -s $W/$G/route.ses ] && ARGS="$ARGS $G=$W/$G/route.ses"; done
  python3 ../tools/ses_merge.py $W/stage1.kicad_pcb $W/part2.json $W/merged.kicad_pcb $ARGS 2>&1 | grep -v -E "Debug|leak"
fi
cp $N.kicad_pro $W/merged.kicad_pro
kicad-cli pcb drc --severity-all --format json -o $W/merged-drc.json $W/merged.kicad_pcb >/dev/null 2>&1
python3 - $W/merged-drc.json <<'PY'
import json, collections, sys
d = json.load(open(sys.argv[1])); c = collections.Counter(v['type'] for v in d['violations'])
print("stage2 merged: hard %d (%s) unconnected %d" % (sum(c[t] for t in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'hole_to_hole', 'copper_edge_clearance')), dict((k, v) for k, v in c.items() if v), len(d.get('unconnected_items', []))))
PY
echo "STAGE2-DONE $(date -u +%H:%M:%S)"
