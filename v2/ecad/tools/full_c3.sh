#!/usr/bin/env bash
# PCB-C C3 pre-route chain: schematic -> ERC/netlist -> mechanical panel -> netlist placement -> verifier -> escapes -> fanout -> pre-route DRC gate
set -uo pipefail
cd "$1"; N=pcb-c-display
python3 ../tools/gen_sch_c.py $N.kicad_sch $N 2>&1 | tail -2
../tools/build_sch.sh . $N 2>&1 | grep -E 'ERC|netlist'
python3 ../tools/gen_pcb_c.py $N.kicad_pcb 2>&1 | grep -E 'saved|WARN|Trace|Error|note'
python3 ../tools/gen_pcb_c3.py $N.kicad_pcb out/$N.net 2>&1 | grep -E 'saved|WARN|Trace|Error|overflow|unplaced|missing'
python3 ../tools/check_pcb_c.py $N.kicad_pcb 2>&1 | grep -E 'FAIL|RESULT'
python3 ../tools/escape.py $N.kicad_pcb 2>&1 | grep -E 'escape|no escape'
python3 ../tools/prefanout.py $N.kicad_pcb 'GND' fine 2>&1 | grep -E 'fanout:'
cp $N.kicad_pcb out/$N-preroute.kicad_pcb
kicad-cli pcb drc --severity-all --format json -o out/$N-preroute-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - <<'PY'
import json, collections
d = json.load(open('out/pcb-c-display-preroute-drc.json'))
c = collections.Counter(v['type'] for v in d['violations']); print('pre-route DRC:', dict(c))
for t in ('courtyards_overlap', 'shorting_items', 'clearance', 'copper_edge_clearance', 'hole_clearance', 'hole_to_hole', 'via_diameter', 'drill_out_of_range', 'items_not_allowed'):
    for v in [v for v in d['violations'] if v['type'] == t][:6]: print('  ', t, '|', ' / '.join(i.get('description', '')[:60] for i in v.get('items', [])))
hard = sum(c[t] for t in ('courtyards_overlap', 'shorting_items', 'clearance', 'copper_edge_clearance', 'hole_clearance', 'hole_to_hole', 'via_diameter', 'drill_out_of_range', 'items_not_allowed'))
open('out/preroute-gate.txt', 'w').write('OK' if hard == 0 else 'BLOCK %d' % hard)
PY
echo PREROUTE-DONE $(cat out/preroute-gate.txt)
