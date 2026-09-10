#!/usr/bin/env bash
# B13: wait for route_parallel.sh (PARALLEL-DONE in the log), dangling clean-up FIRST, then the stub router on what is really open,
# a zone refill before its check (a stale fill reports every new via as a plane clearance violation), a second clean-up, legend pass, finish.
# Usage: finish_b13.sh <ecad dir> <parallel log, relative to pcb-b-compute>
cd "$1/pcb-b-compute"; N=pcb-b-compute; LOG="$2"
# A wait with a deadline (10 September 2026, report 1 item 4). If the producer crashes, or the wrong log is named, or the
# marker is never written, this job used to be immortal and nothing said so. FINISH_WAIT_S bounds it, default six hours,
# which is longer than any route this project has run; it refuses rather than carrying on with whatever is on disk.
W=0; while ! grep -q PARALLEL-DONE "$LOG" 2>/dev/null; do sleep 30; W=$((W + 30));
  if [ "$W" -ge "${FINISH_WAIT_S:-21600}" ]; then echo "finish: no PARALLEL-DONE in $LOG after ${W} s; refusing"; exit 1; fi
done
grep -E 'attempt|WINNER' "$LOG"
cp $N.kicad_pcb out/$N-par-routed.kicad_pcb
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak' | tail -1
cp $N.kicad_pcb out/$N-cleaned.kicad_pcb
../tools/drc.sh $N.kicad_pcb out/$N-drc.json
nice -n 10 python3 ../tools/stub_router.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -E 'closed|FAILED|stub_router'
python3 - "$N" <<'PY' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b); print('zones refilled after the stub router')
PY
../tools/drc.sh $N.kicad_pcb out/$N-drc.json
python3 - "$N" <<'PY'
import json, collections, sys
d=json.load(open('out/%s-drc.json' % sys.argv[1])); c=collections.Counter(v['type'] for v in d['violations'])
hard=sum(c[t] for t in ('clearance','shorting_items','tracks_crossing','hole_clearance','hole_to_hole','copper_edge_clearance')); open('out/par-score.txt','w').write('%d' % hard); print('after stub router: hard', hard, 'unrouted', len(d.get('unconnected_items', [])))
PY
read H < out/par-score.txt; if [ "$H" -ne 0 ]; then echo 'stub router hurt: reverting to the cleaned board'; cp out/$N-cleaned.kicad_pcb $N.kicad_pcb; fi
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak' | tail -1
python3 ../tools/silk_fix_all.py $N.kicad_pcb b 2>&1 | grep -vE 'Debug|leak' | tail -2
cd ..; ./tools/finish_board.sh pcb-b-compute pcb-b-compute post_fix_b13.py meshsat-pcb-b-revA-B13 2>&1 | tail -16
echo FINISH-B13-DONE
