#!/usr/bin/env bash
# route -> continuation -> DRC -> close near misses -> DRC -> summary (no timeouts; run with nohup and poll)
set -uo pipefail
cd "$1"; N="${2:-pcb-b-compute}"
cp out/$N-preroute.kicad_pcb $N.kicad_pcb
export FR_XVFB=1 FR_JAR=$HOME/bin/freerouting-1.9.0.jar
watched_route() {   # $1 = passes; kills the router if its log goes idle for 150 s (Freerouting 1.9 sometimes hangs on re-import)
  rm -f out/$N-freerouting.log
  ( ../tools/route_pcb.sh . $N "$1" 2>&1 | grep -E 'SES import|tracks|non-zero' ) &
  local RP=$!
  while kill -0 $RP 2>/dev/null; do
    sleep 20
    [ -f out/$N-freerouting.log ] || continue                 # router not started yet
    local age=$(( $(date +%s) - $(stat -c %Y out/$N-freerouting.log) ))
    if [ $age -gt 540 ]; then echo "router idle ${age}s: killing"; pkill -9 -f '^java .*freerouting'; fi
  done
  wait $RP
}
watched_route 30
watched_route 40
../tools/build_pcb.sh . $N 2>&1 | grep -E '^DRC'
python3 ../tools/finish_stubs.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -vi '^warning'
../tools/build_pcb.sh . $N 2>&1 | grep -E '^DRC'
grep -E '^\[' out/$N-drc.rpt | sed 's/:.*//' | sort | uniq -c | sort -rn | head -8
export N; python3 - <<'PY'
import json, re, collections
import os
d=json.load(open('out/%s-drc.json' % os.environ.get('N','pcb-b-compute')))
c=collections.Counter()
for v in d.get('unconnected_items',[]):
    nets=set(re.findall(r'\[([^\]]+)\]', ' '.join(i.get('description','') for i in v.get('items',[])))); c[tuple(sorted(nets))]+=1
print('unrouted:', dict(c))
for v in d.get('unconnected_items',[])[:12]: print('   ', ' / '.join(i.get('description','')[:70] for i in v.get('items',[])))
for t in ('clearance','shorting_items','tracks_crossing','track_dangling','via_dangling','silk_overlap','silk_over_copper','silk_edge_clearance'):
    vs=[v for v in d['violations'] if v['type']==t]
    for v in vs[:3]: print(' ', t, '|', ' / '.join(i.get('description','')[:55] for i in v.get('items',[])))
PY
echo ROUTE-DONE
