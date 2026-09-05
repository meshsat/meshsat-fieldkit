#!/usr/bin/env bash
# C6 (5 Sep 2026): wait for route_parallel.sh (PARALLEL-DONE in the log), stub router, dangling clean-up, legend pass, refill, the board gate, finish. The seals and lenses belong to the face plate (v2/cad/face_plate.py); no tenting rule: the backer is not the weather face.
# Usage: finish_c6.sh <ecad dir> <parallel log, relative to pcb-c-display>
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
python3 - "$N" <<'PYX' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b); print('zones refilled before the board gate')
PYX
python3 ../tools/check_pcb_c.py $N.kicad_pcb 2>&1 | grep -E 'FAIL|RESULT'
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - "$N" <<'PYX'
import json, collections, sys
d = json.load(open('out/%s-drc.json' % sys.argv[1])); c = collections.Counter(v['type'] for v in d['violations'])
hard = sum(c[t] for t in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'hole_to_hole', 'copper_edge_clearance')); un = len(d.get('unconnected_items', []))
print('routed-board gate: hard', hard, 'unrouted', un); open('out/c6-clean.txt', 'w').write(('clean' if hard == 0 and un == 0 else 'open') + '\n')
PYX
if ! python3 ../tools/check_pcb_c.py $N.kicad_pcb 2>/dev/null | grep -q 'RESULT: ALL PASS'; then echo 'C6 GATE FAIL on the routed board'; echo open > out/c6-clean.txt; fi
CLEAN=$(cat out/c6-clean.txt); if [ "$CLEAN" != clean ]; then echo 'C6 NOT CLEAN, not finishing'; echo FINISH-C6-DONE; exit 1; fi
rm -rf out/$N-seals.dxf; kicad-cli pcb export dxf --mode-single --layers User.2,User.3,Edge.Cuts --output-units mm -o out/$N-seals.dxf $N.kicad_pcb >/dev/null 2>&1 && echo "seals DXF: out/$N-seals.dxf ($(grep -c -E '^(LINE|ARC|CIRCLE|LWPOLYLINE|POLYLINE)$' out/$N-seals.dxf) entities)"
cd ..; ./tools/finish_board.sh pcb-c-display pcb-c-display - meshsat-pcb-c-revA-C6 2>&1 | tail -16
echo FINISH-C6-DONE
