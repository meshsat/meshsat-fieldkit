#!/usr/bin/env bash
# C5: wait for route_parallel.sh (PARALLEL-DONE in the log), stub router, dangling clean-up, legend pass, tenting check, seal DXF, finish.
# Usage: finish_c5.sh <ecad dir> <parallel log, relative to pcb-c-display>
cd "$1/pcb-c-display"; N=pcb-c-display; LOG="$2"
while ! grep -q PARALLEL-DONE "$LOG" 2>/dev/null; do sleep 30; done
grep -E 'attempt|WINNER' "$LOG"
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
cp $N.kicad_pcb out/$N-par-routed.kicad_pcb
nice -n 10 python3 ../tools/stub_router.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -E 'closed|FAILED|stub_router'
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - "$N" <<'PY'
import json, collections, sys
d=json.load(open('out/%s-drc.json' % sys.argv[1])); c=collections.Counter(v['type'] for v in d['violations'])
hard=sum(c[t] for t in ('clearance','shorting_items','tracks_crossing','hole_clearance','hole_to_hole','copper_edge_clearance')); open('out/par-score.txt','w').write('%d' % hard); print('after stub router: hard', hard, 'unrouted', len(d.get('unconnected_items', [])))
PY
read H < out/par-score.txt; if [ "$H" -ne 0 ]; then echo 'stub router hurt: reverting'; cp out/$N-par-routed.kicad_pcb $N.kicad_pcb; fi
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup
python3 ../tools/silk_fix_all.py $N.kicad_pcb c 2>&1 | grep -vE 'Debug|leak' | tail -2
grep -q "(tenting front back)" $N.kicad_pcb && echo "tenting: both faces" || { echo "BLOCK: vias not tented on both faces"; exit 1; }
python3 ../tools/check_pcb_c.py $N.kicad_pcb 2>&1 | grep -E 'FAIL|RESULT'
rm -rf out/$N-seals.dxf; kicad-cli pcb export dxf --mode-single --layers User.2,User.3,Edge.Cuts --output-units mm -o out/$N-seals.dxf $N.kicad_pcb >/dev/null 2>&1 && echo "seals DXF: out/$N-seals.dxf ($(grep -c -E '^(LINE|ARC|CIRCLE|LWPOLYLINE|POLYLINE)$' out/$N-seals.dxf) entities)"
cd ..; ./tools/finish_board.sh pcb-c-display pcb-c-display - meshsat-pcb-c-revA-C5 2>&1 | tail -16
cp pcb-c-display/out/$N-seals.dxf ../release/${MESHSAT_FK_REV:-revA}/boards/meshsat-pcb-c-revA-C5/ 2>/dev/null && echo "seals DXF copied into the deliverable folder"
echo FINISH-C5-DONE
