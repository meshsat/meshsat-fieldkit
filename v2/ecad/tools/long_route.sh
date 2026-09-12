#!/usr/bin/env bash
# Usage: long_route.sh <dir> <name> <passes> : one long Freerouting run from the pre-route board (serialised), then DRC
cd "$1"; N="$2"; P="$3"
exec 9>/tmp/meshsat-freerouting.lock; flock 9
# A wait with a deadline (MESHSAT-862, stage 0a, 11 Sep 2026). This was the last unbounded wait in the tools:
# the flock above already serialises our own routes, so this loop only catches a router started outside the lock,
# and with no bound a stray java process made this job immortal with nothing saying so.
W=0
while pgrep -f '^java .*freerouting' >/dev/null; do
  sleep 20; W=$((W + 20))
  if [ "$W" -ge "${LONG_ROUTE_WAIT_S:-21600}" ]; then echo "long_route: another router still running after ${W} s; refusing"; echo LONG-ROUTE-DONE REFUSED; exit 1; fi
done
cp out/$N-preroute.kicad_pcb $N.kicad_pcb; rm -f out/$N-freerouting.log
export FR_XVFB=1   # the jar comes from fr_jar.sh through route_pcb.sh (it pinned the stock jar here)
( ../tools/route_pcb.sh . $N "$P" 2>&1 | grep -E 'SES import|tracks|non-zero' ) &
RP=$!
while kill -0 $RP 2>/dev/null; do sleep 20; [ -f out/$N-freerouting.log ] || continue; age=$(( $(date +%s) - $(stat -c %Y out/$N-freerouting.log) )); if [ $age -gt 900 ]; then echo "router idle ${age}s: killing"; pkill -9 -f '^java .*freerouting'; fi; done
wait $RP
../tools/build_pcb.sh . $N 2>&1 | grep -E '^DRC'
python3 - "$N" <<'PY'
import json, sys
d = json.load(open('out/%s-drc.json' % sys.argv[1])); print('unrouted:', len(d.get('unconnected_items', [])))
for v in d.get('unconnected_items', []): print('   ', ' / '.join(i.get('description', '')[:70] for i in v.get('items', [])))
PY
echo LONG-ROUTE-DONE
