#!/usr/bin/env bash
# After a PCB-A route: EP tie, grid router, checked closer, post-fix, DRC; then finish into the given Downloads folder
cd "$1"; N=pcb-a-power
TAG="$3"; while ! grep -q ROUTE-DONE out/route-$TAG.log 2>/dev/null; do sleep 30; done
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
cp $N.kicad_pcb out/$N-$TAG-routed.kicad_pcb
nice -n 10 python3 ../tools/stub_router.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -E 'closed|FAILED|stub_router'
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - <<'PY'
import json, collections
d=json.load(open('out/pcb-a-power-drc.json')); c=collections.Counter(v['type'] for v in d['violations'])
hard=sum(c[t] for t in ('clearance','shorting_items','tracks_crossing','hole_clearance','copper_edge_clearance')); print('after stub router: hard', hard, 'unrouted', len(d.get('unconnected_items',[])))
open('out/score.txt','w').write('%d' % hard)
PY
read H < out/score.txt; if [ "$H" -ne 0 ]; then echo 'stub router hurt: reverting to the routed board'; cp out/$N-$TAG-routed.kicad_pcb $N.kicad_pcb; kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1; fi
nice -n 10 python3 ../tools/gap_closer_checked.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -vE 'Debug|leak' | tail -3
cd ..; ./tools/finish_board.sh pcb-a-power pcb-a-power post_fix_a.py "$2" 2>&1 | tail -12
echo A-FINISH-DONE
