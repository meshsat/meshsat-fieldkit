#!/usr/bin/env bash
# PCB-A retry: route the pre-route board with the given pass counts, close gaps, keep only if no hard DRC and fewer unrouted than BEST (arg 4)
cd "$1"; N=pcb-a-power; BEST="$4"
exec 9>/tmp/meshsat-freerouting.lock; flock 9
while pgrep -f '^java .*freerouting' >/dev/null; do sleep 20; done
cp $N.kicad_pcb out/$N-keep.kicad_pcb
cp out/$N-preroute.kicad_pcb $N.kicad_pcb
export FR_XVFB=1 FR_JAR=$HOME/bin/freerouting-1.9.0.jar
for P in "$2" "$3"; do rm -f out/$N-freerouting.log; timeout 2400 ../tools/route_pcb.sh . $N "$P" 2>&1 | grep -E 'SES import|tracks'; done
python3 ../tools/net_tie.py $N.kicad_pcb >/dev/null
python3 - <<'PY' 2>&1 | grep -vE 'Debug|leak'
import pcbnew
from pcbnew import VECTOR2I, FromMM
b=pcbnew.LoadBoard('pcb-a-power.kicad_pcb'); u3=[f for f in b.GetFootprints() if f.GetReference()=='U3'][0]
p3=[p for p in u3.Pads() if p.GetNumber()=='3' and p.GetSize().x>FromMM(0.5)][0]; ep=[p for p in u3.Pads() if p.GetNumber()=='13' and p.GetSize().x>FromMM(1.9)][0]
gnd=b.FindNet('GND'); a=p3.GetPosition(); c=ep.GetPosition(); mid=VECTOR2I(c.x, a.y)
for s,e in ((a,mid),(mid,c)):
    t=pcbnew.PCB_TRACK(b); t.SetStart(s); t.SetEnd(e); t.SetWidth(FromMM(0.2)); t.SetLayer(pcbnew.F_Cu); t.SetNet(gnd); b.Add(t)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard('pcb-a-power.kicad_pcb', b); print('EP tie added')
PY
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
cp $N.kicad_pcb out/$N-retry-routed.kicad_pcb
nice -n 10 python3 ../tools/stub_router.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -E 'closed|FAILED|stub_router'
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - <<'PY'
import json, collections
d = json.load(open('out/pcb-a-power-drc.json')); c = collections.Counter(v['type'] for v in d['violations'])
hard = sum(c[t] for t in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'copper_edge_clearance')); open('out/retry-score.txt', 'w').write('%d %d' % (hard, len(d.get('unconnected_items', []))))
print('after stub router: hard %d unrouted %d' % (hard, len(d.get('unconnected_items', []))))
PY
read H U < out/retry-score.txt
if [ "$H" -ne 0 ]; then echo 'stub router hurt: using the plain routed board'; cp out/$N-retry-routed.kicad_pcb $N.kicad_pcb; kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1; python3 - <<'PY'
import json, collections
d = json.load(open('out/pcb-a-power-drc.json')); c = collections.Counter(v['type'] for v in d['violations'])
hard = sum(c[t] for t in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'copper_edge_clearance')); open('out/retry-score.txt', 'w').write('%d %d' % (hard, len(d.get('unconnected_items', []))))
PY
read H U < out/retry-score.txt; fi
NO_GAPS=1 python3 ../tools/post_fix_a.py $N.kicad_pcb out/$N-drc.json >/dev/null 2>&1
echo "retry result: hard $H unrouted $U (best so far $BEST)"
if [ "$H" -eq 0 ] && [ "$U" -lt "$BEST" ]; then echo "RETRY BETTER: keeping"; cd ..; ./tools/finish_board.sh pcb-a-power pcb-a-power - "$5" 2>&1 | grep -E 'unrouted|deliverables|^    '
else echo "RETRY NOT BETTER: restoring the kept board"; cp out/$N-keep.kicad_pcb $N.kicad_pcb; kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1; fi
echo RETRY-DONE
