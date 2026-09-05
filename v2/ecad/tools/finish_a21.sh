#!/usr/bin/env bash
# A21: wait for route_parallel.sh (PARALLEL-DONE in the log), stub router, dangling clean-up, pack-node and boost bars, legend pass, finish.
# Usage: finish_a17.sh <ecad dir> <parallel log, relative to pcb-a-power>
cd "$1/pcb-a-power"; N=pcb-a-power; LOG="$2"
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
python3 ../tools/silk_fix_all.py $N.kicad_pcb a 2>&1 | grep -vE 'Debug|leak' | tail -2
# A21 (5 Sep 2026): refill, then the board gate on the routed board (band continuity, stitch vias in their bands, link widths); an open or a FAIL stops the finish
python3 - "$N" <<'PYX' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b); print('zones refilled before the routed-board gate')
PYX
python3 ../tools/check_pcb_a.py $N.kicad_pcb 2>&1 | grep -E 'FAIL|band|stitch|routed at|RESULT' | tail -12
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - "$N" <<'PYX'
import json, collections, sys
d = json.load(open('out/%s-drc.json' % sys.argv[1])); c = collections.Counter(v['type'] for v in d['violations'])
hard = sum(c[t] for t in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'hole_to_hole', 'copper_edge_clearance')); un = len(d.get('unconnected_items', []))
print('routed-board gate: hard', hard, 'unrouted', un); open('out/a21-clean.txt', 'w').write('clean' if hard == 0 and un == 0 else 'open')
PYX
if ! python3 ../tools/check_pcb_a.py $N.kicad_pcb 2>/dev/null | grep -q 'RESULT: ALL PASS'; then echo 'A21 GATE FAIL on the routed board'; echo open > out/a21-clean.txt; fi
read CLEAN < out/a21-clean.txt; if [ "$CLEAN" != clean ]; then echo 'A21 NOT CLEAN, not finishing'; echo FINISH-A21-DONE; exit 1; fi
cd ..; ./tools/finish_board.sh pcb-a-power pcb-a-power post_fix_a.py meshsat-pcb-a-revA-A21 2>&1 | tail -16
echo FINISH-A21-DONE
