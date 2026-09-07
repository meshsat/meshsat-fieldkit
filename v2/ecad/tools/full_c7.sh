#!/usr/bin/env bash
# PCB-C C7 pre-route chain (MESHSAT-830, 7 Sep 2026): schematic -> ERC/netlist -> mechanical panel -> netlist placement -> verifier -> escapes -> fanout -> pre-route DRC gate
set -uo pipefail
cd "$1"; N=pcb-c-display; mkdir -p out
for f in ../tools/gen_sch_c.py ../tools/gen_pcb_c.py ../tools/gen_pcb_c3.py ../tools/check_pcb_c.py ../tools/panel1450.py; do python3 -W error -c "import sys
with open(sys.argv[1]) as fh: compile(fh.read(), sys.argv[1], 'exec')" "$f" || { echo "BLOCK compile $f" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }; done
python3 ../tools/gen_sch_c.py $N.kicad_sch $N 2>&1 | tail -2
../tools/build_sch.sh . $N 2>&1 | grep -E 'ERC|netlist'
python3 ../tools/gen_pcb_c.py $N.kicad_pcb > out/gen_pcb_c.log 2>&1; grep -E 'saved|WARN|Trace|Error|note|not found' out/gen_pcb_c.log
grep -q '^saved' out/gen_pcb_c.log || { echo "BLOCK: gen_pcb_c.py did not save the board (see out/gen_pcb_c.log)"; tail -3 out/gen_pcb_c.log; echo 'BLOCK generator' > out/preroute-gate.txt; echo PREROUTE-DONE BLOCK generator; exit 1; }
python3 ../tools/gen_pcb_c3.py $N.kicad_pcb out/$N.net > out/gen_pcb_c3.log 2>&1; grep -E 'saved|WARN|Trace|Error|overflow|unplaced|missing|single-pin' out/gen_pcb_c3.log
grep -q '^saved' out/gen_pcb_c3.log || { echo "BLOCK: gen_pcb_c3.py did not save the board (see out/gen_pcb_c3.log)"; tail -3 out/gen_pcb_c3.log; echo 'BLOCK generator' > out/preroute-gate.txt; echo PREROUTE-DONE BLOCK generator; exit 1; }
python3 ../tools/check_pcb_c.py $N.kicad_pcb > out/check_c.log 2>&1; grep -E 'FAIL|RESULT' out/check_c.log; grep -q 'RESULT: ALL PASS' out/check_c.log || { echo 'BLOCK numeric gate (out/check_c.log)' | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/escape.py $N.kicad_pcb 2>&1 | grep -E 'escape|no escape'
python3 ../tools/join_adjacent_pins.py $N.kicad_pcb 2>&1 | grep -E 'join_adjacent_pins|Traceback|Error'
python3 ../tools/prefanout.py $N.kicad_pcb 'GND' fine   # only nets with a plane or pour to land on (7 Sep 2026: a pre-placed via of a net without a plane is one more open for the router) 2>&1 | grep -E 'fanout:'
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
