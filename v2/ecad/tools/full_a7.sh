#!/usr/bin/env bash
# PCB-A A6 (A17) pre-route: schematic -> ERC/netlist -> A1 mechanical -> netlist import + placement -> fanout -> queued route
set -uo pipefail
cd "$1"; N=pcb-a-power
python3 ../tools/gen_sch_a.py $N.kicad_sch $N 2>&1 | tail -1
../tools/build_sch.sh . $N 2>&1 | grep -E 'ERC|netlist'
python3 ../tools/gen_pcb_a.py $N.kicad_pcb 2>&1 | grep -E 'saved|WARN|Trace'
python3 ../tools/check_pcb_a.py $N.kicad_pcb 2>&1 | grep -E 'FAIL|RESULT'
python3 ../tools/gen_pcb_a3.py $N.kicad_pcb out/$N.net > out/gen3.log 2>&1; GEN3=$?; grep -E 'saved|WARN|overflow|unplaced|Trace|SystemExit|zone net|not in the netlist' out/gen3.log
[ "$GEN3" -eq 0 ] || { echo "BLOCK placement generator exit $GEN3" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/escape.py $N.kicad_pcb 2>&1 | grep -E 'escape|no escape'
python3 ../tools/prefanout.py $N.kicad_pcb 'GND,+5V_M1,CELL+' fine 2>&1 | grep -E 'fanout:'
cp $N.kicad_pcb out/$N-preroute.kicad_pcb
kicad-cli pcb drc --severity-all --format json -o out/$N-preroute-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - <<'PY'
import json, collections
d = json.load(open('out/pcb-a-power-preroute-drc.json')); c = collections.Counter(v['type'] for v in d['violations']); print('pre-route DRC:', dict(c))
hard = sum(c[t] for t in ('courtyards_overlap', 'shorting_items', 'clearance', 'copper_edge_clearance', 'hole_clearance', 'hole_to_hole', 'via_diameter', 'drill_out_of_range'))
for t in ('courtyards_overlap', 'shorting_items', 'clearance', 'copper_edge_clearance', 'hole_clearance', 'hole_to_hole', 'via_diameter', 'drill_out_of_range'):
    for v in [v for v in d['violations'] if v['type'] == t][:5]: print('  ', t, '|', ' / '.join(i.get('description', '')[:60] for i in v.get('items', [])))
open('out/preroute-gate.txt', 'w').write('OK' if hard == 0 else 'BLOCK %d' % hard)
PY
python3 ../tools/check_zone_nets.py $N.kicad_pcb 2>&1 | grep -E "FAIL|zone nets" || echo "BLOCK zone-nets" > out/preroute-gate.txt
echo PREROUTE-DONE $(cat out/preroute-gate.txt)
