#!/usr/bin/env bash
# PCB-P P1 pre-route chain (MESHSAT-830, 7 Sep 2026, appendix 32.62): footprints, schematic, netlist, mechanical, placement, gate, escapes, joins, fanout, pre-route DRC
set -uo pipefail
cd "$1"; N=pcb-p-pack
mkdir -p out
python3 ../tools/gen_sch_p.py $N.kicad_sch $N > out/gen_sch.log 2>&1 || { echo 'BLOCK schematic generator (out/gen_sch.log)' | tee out/preroute-gate.txt; tail -3 out/gen_sch.log; echo PREROUTE-DONE BLOCK; exit 1; }; grep -E 'wrote|single-pin nets' out/gen_sch.log
../tools/build_sch.sh . $N 2>&1 | grep -E 'ERC|netlist'
python3 ../tools/gen_pcb_p.py $N.kicad_pcb 2>&1 | grep -E 'saved|WARN|Trace|Error|note'
python3 ../tools/gen_pcb_p3.py $N.kicad_pcb out/$N.net > out/gen3.log 2>&1; GEN3=$?; grep -E 'saved|WARN|Trace|Error|overflow|unplaced|missing|SystemExit|zone net|not in the netlist' out/gen3.log
[ "$GEN3" -eq 0 ] || { echo "BLOCK placement generator exit $GEN3" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/check_pcb_p.py $N.kicad_pcb > out/check_p.log 2>&1; grep -E 'FAIL|RESULT' out/check_p.log; grep -q 'RESULT: ALL PASS' out/check_p.log || { echo 'BLOCK numeric gate (out/check_p.log)' | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/escape.py $N.kicad_pcb 2>&1 | grep -E 'escape|no escape'
python3 ../tools/join_adjacent_pins.py $N.kicad_pcb 2>&1 | grep -E 'join_adjacent_pins|Traceback|Error'
python3 ../tools/prefanout.py $N.kicad_pcb 'GND' fine   # only nets with a plane or pour to land on (7 Sep 2026: a pre-placed via of a net without a plane is one more open for the router) 2>&1 | grep -E 'fanout:'
cp $N.kicad_pcb out/$N-preroute.kicad_pcb
kicad-cli pcb drc --severity-all --format json -o out/$N-preroute-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - <<'PY'
import json, collections
d = json.load(open('out/pcb-p-pack-preroute-drc.json'))
c = collections.Counter(v['type'] for v in d['violations']); print('pre-route DRC:', dict(c))
for t in ('courtyards_overlap', 'shorting_items', 'clearance', 'copper_edge_clearance', 'hole_clearance', 'hole_to_hole', 'items_not_allowed'):
    for v in [v for v in d['violations'] if v['type'] == t][:6]: print('  ', t, '|', ' / '.join(i.get('description', '')[:60] for i in v.get('items', [])))
hard = sum(c[t] for t in ('courtyards_overlap', 'shorting_items', 'clearance', 'copper_edge_clearance', 'hole_clearance', 'hole_to_hole', 'items_not_allowed'))
open('out/preroute-gate.txt', 'w').write('OK' if hard == 0 else 'BLOCK %d' % hard)
PY
python3 ../tools/check_zone_nets.py $N.kicad_pcb 2>&1 | grep -E "FAIL|zone nets" || echo "BLOCK zone-nets" > out/preroute-gate.txt
echo PREROUTE-DONE $(cat out/preroute-gate.txt)
