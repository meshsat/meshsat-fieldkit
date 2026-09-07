#!/usr/bin/env bash
# PCB-A A22 (MESHSAT-830) pre-route: schematic -> ERC/netlist -> mechanical -> netlist import + placement -> escapes, joins, fanout -> pre-route DRC gate
# Usage: full_a22.sh <project dir>. Every generator's full output goes to out/*.log; the chain stops on a generator that does not save (C6 run 1 lesson).
set -uo pipefail
cd "$1"; N=pcb-a-power; mkdir -p out
for f in ../tools/gen_sch_a.py ../tools/gen_pcb_a.py ../tools/gen_pcb_a3.py ../tools/check_pcb_a.py; do python3 -W error -c "import sys
with open(sys.argv[1]) as fh: compile(fh.read(), sys.argv[1], 'exec')" "$f" || { echo "BLOCK compile $f" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }; done
python3 ../tools/gen_sch_a.py $N.kicad_sch $N > out/gen_sch.log 2>&1 || { echo "BLOCK schematic generator (out/gen_sch.log)" | tee out/preroute-gate.txt; tail -3 out/gen_sch.log; echo PREROUTE-DONE BLOCK; exit 1; }
grep -E 'wrote|single-pin nets' out/gen_sch.log
../tools/build_sch.sh . $N > out/build_sch.log 2>&1; grep -E 'ERC|netlist' out/build_sch.log
[ -s out/$N.net ] || { echo "BLOCK no netlist (out/build_sch.log)" | tee out/preroute-gate.txt; tail -5 out/build_sch.log; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/gen_pcb_a.py $N.kicad_pcb > out/gen_pcb_a.log 2>&1; grep -E 'saved|WARN|Trace' out/gen_pcb_a.log; grep -q saved out/gen_pcb_a.log || { echo "BLOCK mechanical generator" | tee out/preroute-gate.txt; tail -5 out/gen_pcb_a.log; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/check_pcb_a.py $N.kicad_pcb > out/check_a1.log 2>&1; grep -E 'FAIL|RESULT' out/check_a1.log
python3 ../tools/gen_pcb_a3.py $N.kicad_pcb out/$N.net > out/gen3.log 2>&1; GEN3=$?; grep -E 'saved|WARN|overflow|unplaced|Trace|SystemExit|zone net|not in the netlist|footprint missing' out/gen3.log
[ "$GEN3" -eq 0 ] || { echo "BLOCK placement generator exit $GEN3" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/check_pcb_a.py $N.kicad_pcb > out/check_a3.log 2>&1; grep -E 'FAIL|RESULT' out/check_a3.log
grep -q 'RESULT: ALL PASS' out/check_a3.log || { echo "BLOCK numeric gate (out/check_a3.log)" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/escape.py $N.kicad_pcb 2>&1 | grep -E 'escape|no escape'
python3 ../tools/join_adjacent_pins.py $N.kicad_pcb 2>&1 | grep -E 'join_adjacent_pins|Traceback|Error'
python3 ../tools/prefanout.py $N.kicad_pcb 'GND,VBAT,CELL+,VBUS20,+5V_S1,+5V_S2,+5V_S3,+5V_DEV,+3V3' fine 2>&1 | grep -E 'fanout:'
cp $N.kicad_pcb out/$N-preroute.kicad_pcb
kicad-cli pcb drc --severity-all --format json -o out/$N-preroute-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - <<'PY'
import json, collections
d = json.load(open('out/pcb-a-power-preroute-drc.json')); c = collections.Counter(v['type'] for v in d['violations']); print('pre-route DRC:', dict(c))
HARD = ('courtyards_overlap', 'shorting_items', 'clearance', 'copper_edge_clearance', 'hole_clearance', 'hole_to_hole', 'via_diameter', 'drill_out_of_range')
hard = sum(c[t] for t in HARD)
for t in HARD:
    for v in [v for v in d['violations'] if v['type'] == t][:5]: print('  ', t, '|', ' / '.join(i.get('description', '')[:70] for i in v.get('items', [])))
open('out/preroute-gate.txt', 'w').write('OK' if hard == 0 else 'BLOCK %d' % hard)
PY
python3 ../tools/check_zone_nets.py $N.kicad_pcb 2>&1 | grep -E "FAIL|zone nets" || echo "BLOCK zone-nets" > out/preroute-gate.txt
echo PREROUTE-DONE $(cat out/preroute-gate.txt)
