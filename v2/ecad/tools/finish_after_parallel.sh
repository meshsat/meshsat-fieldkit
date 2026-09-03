#!/usr/bin/env bash
# Wait for route_parallel.sh (PARALLEL-DONE in the given log), then the finishing tail. Usage: finish_after_parallel.sh <project dir> <name> <parallel log> <postfix script or -> <downloads name> [eptie]
cd "$1"; D=$(basename "$PWD"); N="$2"; LOG="$3"; PF="$4"; DL="$5"; EPTIE="${6:-}"
while ! grep -q PARALLEL-DONE "$LOG" 2>/dev/null; do sleep 30; done
grep -E 'attempt|WINNER' "$LOG"
if [ "$EPTIE" = "eptie" ]; then python3 - <<'PY' 2>&1 | grep -vE 'Debug|leak'
import pcbnew
from pcbnew import VECTOR2I, FromMM
b=pcbnew.LoadBoard('pcb-a-power.kicad_pcb'); u3=[f for f in b.GetFootprints() if f.GetReference()=='U3'][0]
p3=[p for p in u3.Pads() if p.GetNumber()=='3' and p.GetSize().x>FromMM(0.5)][0]; ep=[p for p in u3.Pads() if p.GetNumber()=='13' and p.GetSize().x>FromMM(1.9)][0]
gnd=b.FindNet('GND'); a=p3.GetPosition(); c=ep.GetPosition(); mid=VECTOR2I(c.x, a.y)
for s,e in ((a,mid),(mid,c)):
    t=pcbnew.PCB_TRACK(b); t.SetStart(s); t.SetEnd(e); t.SetWidth(FromMM(0.2)); t.SetLayer(pcbnew.F_Cu); t.SetNet(gnd); b.Add(t)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard('pcb-a-power.kicad_pcb', b); print('EP tie added')
PY
fi
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
cp $N.kicad_pcb out/$N-par-routed.kicad_pcb
nice -n 10 python3 ../tools/stub_router.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -E 'closed|FAILED|stub_router'
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - "$N" <<'PY'
import json, collections, sys
d=json.load(open('out/%s-drc.json' % sys.argv[1])); c=collections.Counter(v['type'] for v in d['violations'])
hard=sum(c[t] for t in ('clearance','shorting_items','tracks_crossing','hole_clearance','hole_to_hole','copper_edge_clearance')); open('out/par-score.txt','w').write('%d' % hard); print('after stub router: hard', hard, 'unrouted', len(d.get('unconnected_items',[])))
PY
read H < out/par-score.txt; if [ "$H" -ne 0 ]; then echo 'stub router hurt: reverting'; cp out/$N-par-routed.kicad_pcb $N.kicad_pcb; kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1; fi
cd ..; ./tools/finish_board.sh "$D" "$N" "$PF" "$DL" 2>&1 | tail -12
echo FINISH-PAR-DONE
