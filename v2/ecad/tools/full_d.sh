#!/usr/bin/env bash
# PCB-D pre-route chain: D1 mechanical -> verifier -> D2 schematic (ERC, netlist) -> D3 placement -> fanout -> pre-route DRC gate
set -uo pipefail
cd "$1"; N=pcb-d-aprs
python3 ../tools/gen_pcb_d.py $N.kicad_pcb 2>&1 | grep -E 'saved|WARN|Trace|Error'
python3 ../tools/check_pcb_d.py $N.kicad_pcb 2>&1 | grep -E 'FAIL|RESULT'
python3 ../tools/gen_sch_d.py $N.kicad_sch $N 2>&1 | tail -2
../tools/build_sch.sh . $N 2>&1 | grep -E 'ERC|netlist|bom'
python3 ../tools/gen_pcb_d3.py $N.kicad_pcb out/$N.net 2>&1 | grep -E 'saved|WARN|Trace|Error|overflow|EP|missing'
python3 ../tools/check_pcb_d.py $N.kicad_pcb 2>&1 | grep -E 'FAIL|RESULT'   # D7: the content checks need the placed parts
python3 ../tools/escape.py $N.kicad_pcb 2>&1 | grep -E 'escape|no escape'
python3 ../tools/prefanout.py $N.kicad_pcb "GND,+3V3" "U2,fine" 2>&1 | grep -E 'fanout:'
cp $N.kicad_pcb out/$N-preroute.kicad_pcb
kicad-cli pcb drc --severity-all --format json -o out/$N-preroute-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - <<'PY'
import json, collections
d = json.load(open('out/pcb-d-aprs-preroute-drc.json'))
c = collections.Counter(v['type'] for v in d['violations']); print('pre-route DRC:', dict(c))
for t in ('courtyards_overlap', 'shorting_items', 'clearance', 'copper_edge_clearance', 'hole_clearance', 'hole_to_hole', 'drill_out_of_range', 'text_height'):
    for v in [v for v in d['violations'] if v['type'] == t][:8]: print('  ', t, '|', ' / '.join(i.get('description', '')[:60] for i in v.get('items', [])))
hard = sum(c[t] for t in ('courtyards_overlap', 'shorting_items', 'clearance', 'copper_edge_clearance', 'hole_clearance', 'hole_to_hole'))
open('out/preroute-gate.txt', 'w').write('OK' if hard == 0 else 'BLOCK %d' % hard)
PY
echo PREROUTE-DONE $(cat out/preroute-gate.txt)
