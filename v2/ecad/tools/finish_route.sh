#!/usr/bin/env bash
# close near misses, then a watched continuation pass (killed if the router log goes idle), then DRC + summary
set -uo pipefail
cd "$1"; N="${2:-pcb-b-compute}"
python3 ../tools/post_fix.py $N.kicad_pcb 2>&1 | grep -vi '^warning'
../tools/build_pcb.sh . $N 2>&1 | grep -E '^DRC'
python3 ../tools/finish_stubs.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -vi '^warning'
cp $N.kicad_pcb out/$N-routed-stage.kicad_pcb
export FR_XVFB=1 FR_JAR=$HOME/bin/freerouting-1.9.0.jar
rm -f out/$N-freerouting.log
( ../tools/route_pcb.sh . $N 20 2>&1 | grep -E 'SES import|tracks|non-zero' ) &
RP=$!
while kill -0 $RP 2>/dev/null; do
  sleep 20
  [ -f out/$N-freerouting.log ] || continue
  age=$(( $(date +%s) - $(stat -c %Y out/$N-freerouting.log) ))
  if [ $age -gt 540 ]; then echo "router idle ${age}s: killing"; pkill -9 -f '^java .*freerouting'; fi
done
wait $RP
../tools/build_pcb.sh . $N 2>&1 | grep -E '^DRC'
python3 ../tools/finish_stubs.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -vi '^warning'
../tools/build_pcb.sh . $N 2>&1 | grep -E '^DRC'
grep -E '^\[' out/$N-drc.rpt | sed 's/:.*//' | sort | uniq -c | sort -rn | head -8
export N; python3 - <<'PY'
import json, re, collections
import os
d=json.load(open('out/%s-drc.json' % os.environ.get('N','pcb-b-compute')))
for v in d.get('unconnected_items',[])[:12]: print('   unrouted:', ' / '.join(i.get('description','')[:70] for i in v.get('items',[])))
for t in ('clearance','shorting_items','tracks_crossing','track_dangling','via_dangling','silk_overlap','silk_over_copper','silk_edge_clearance','items_not_allowed'):
    for v in [v for v in d['violations'] if v['type']==t][:3]: print('  ', t, '|', ' / '.join(i.get('description','')[:55] for i in v.get('items',[])))
PY
echo FINISH-DONE
