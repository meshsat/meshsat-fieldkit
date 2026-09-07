#!/usr/bin/env bash
# part_stage2.sh <project dir> <name> <passes> <timeout s> <group list>: after the GLOBAL job: import its session and lock its nets, export the DSN
# again (planes and power layers as the route scripts do), re-partition, route every listed group concurrently, wait, merge, DRC, report.
# Env: FR_PLANE_NETS (csv) and FR_POWER_LAYERS as for route_one.sh. Marker STAGE2-DONE.
set -uo pipefail
cd "$1"; N="$2"; P="$3"; T="$4"; GROUPS="$5"; W=$PWD/out/part; PJ=$W/part.json
python3 ../tools/ses_import_lock.py out/$N-preroute.kicad_pcb $W/GLOBAL/route.ses $PJ GLOBAL $W/stage1.kicad_pcb 2>&1 | grep -v -E "Debug|leak"
bash ../tools/dsn_export.sh $W/stage1.kicad_pcb $W/stage2-raw.dsn "${FR_PLANE_NETS:-}" "${FR_POWER_LAYERS:-}" 2>&1 | grep -v -E "Debug|leak"
python3 ../tools/dsn_partition.py $W/stage1.kicad_pcb $W/stage2-raw.dsn $W/stage2.dsn $W/part2.json 2>&1 | grep -v -E "Debug|leak" | grep -v "^partition [A-Z]"
for G in $GROUPS; do bash ../tools/route_part.sh $W $W/stage2.dsn $G $P $T $W/part2.json > $W/route-$G.log 2>&1 & done
wait
for G in $GROUPS; do tail -2 $W/route-$G.log; done
ARGS=""; for G in $GROUPS; do [ -s $W/$G/route.ses ] && ARGS="$ARGS $G=$W/$G/route.ses"; done
python3 ../tools/ses_merge.py $W/stage1.kicad_pcb $W/part2.json $W/merged.kicad_pcb $ARGS 2>&1 | grep -v -E "Debug|leak"
kicad-cli pcb drc --severity-all --format json -o $W/merged-drc.json $W/merged.kicad_pcb >/dev/null 2>&1
python3 - $W/merged-drc.json <<'PY'
import json, collections, sys
d = json.load(open(sys.argv[1])); c = collections.Counter(v['type'] for v in d['violations'])
print("stage2 merged: hard %d (%s) unconnected %d" % (sum(c[t] for t in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'hole_to_hole', 'copper_edge_clearance')), dict((k, v) for k, v in c.items() if v), len(d.get('unconnected_items', []))))
PY
echo "STAGE2-DONE $(date -u +%H:%M:%S)"
