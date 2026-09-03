#!/usr/bin/env bash
# Usage: long_route.sh <dir> <name> <passes> : one long Freerouting run from the pre-route board (serialised), then DRC
cd "$1"; N="$2"; P="$3"
exec 9>/tmp/meshsat-freerouting.lock; flock 9
while pgrep -f '^java .*freerouting' >/dev/null; do sleep 20; done
cp out/$N-preroute.kicad_pcb $N.kicad_pcb; rm -f out/$N-freerouting.log
export FR_XVFB=1 FR_JAR=$HOME/bin/freerouting-1.9.0.jar
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
