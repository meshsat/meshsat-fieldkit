#!/usr/bin/env bash
# PCB-B B16 (MESHSAT-830) pre-route: footprints -> schematic -> ERC/netlist -> mechanical -> gate -> netlist import + placement -> gate -> escapes, joins, fanout -> pre-route DRC gate
# Usage: full_b16.sh <project dir>. Every generator's full output goes to out/*.log; the chain stops on a generator that does not save (C6 run 1 lesson).
set -uo pipefail
cd "$1"; N=pcb-b-compute; mkdir -p out
for f in ../tools/gen_footprints_b16.py ../tools/gen_sch_b.py ../tools/gen_pcb_b.py ../tools/gen_pcb_b3.py ../tools/check_pcb_b.py; do python3 -W error -c "import sys
with open(sys.argv[1]) as fh: compile(fh.read(), sys.argv[1], 'exec')" "$f" || { echo "BLOCK compile $f" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }; done
python3 ../tools/gen_footprints_b16.py ../meshsat.pretty > out/gen_fp.log 2>&1 || { echo "BLOCK footprint generator (out/gen_fp.log)" | tee out/preroute-gate.txt; tail -3 out/gen_fp.log; echo PREROUTE-DONE BLOCK; exit 1; }
grep gen_footprints out/gen_fp.log | cut -c1-120
python3 ../tools/gen_sch_b.py $N.kicad_sch $N > out/gen_sch.log 2>&1 || { echo "BLOCK schematic generator (out/gen_sch.log)" | tee out/preroute-gate.txt; tail -3 out/gen_sch.log; echo PREROUTE-DONE BLOCK; exit 1; }
grep -E 'wrote|single-pin nets' out/gen_sch.log
../tools/build_sch.sh . $N > out/build_sch.log 2>&1; grep -E 'ERC|netlist' out/build_sch.log
[ -s out/$N.net ] || { echo "BLOCK no netlist (out/build_sch.log)" | tee out/preroute-gate.txt; tail -5 out/build_sch.log; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/gen_pcb_b.py $N.kicad_pcb > out/gen_pcb_b.log 2>&1; grep -E 'saved|WARN|Trace' out/gen_pcb_b.log; grep -q saved out/gen_pcb_b.log || { echo "BLOCK mechanical generator" | tee out/preroute-gate.txt; tail -5 out/gen_pcb_b.log; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/check_pcb_b.py $N.kicad_pcb > out/check_b1.log 2>&1; grep -E 'FAIL|RESULT' out/check_b1.log
python3 ../tools/gen_pcb_b3.py $N.kicad_pcb out/$N.net > out/gen3.log 2>&1; GEN3=$?; grep -E 'saved|WARN|overflow|unplaced|Trace|SystemExit|zone net|not in the netlist|footprint missing' out/gen3.log
[ "$GEN3" -eq 0 ] || { echo "BLOCK placement generator exit $GEN3" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }
python3 ../tools/check_pcb_b.py $N.kicad_pcb > out/check_b3.log 2>&1; grep -E 'FAIL|RESULT' out/check_b3.log
grep -q 'RESULT: ALL PASS' out/check_b3.log || { echo "BLOCK numeric gate (out/check_b3.log)" | tee out/preroute-gate.txt; echo PREROUTE-DONE BLOCK; exit 1; }
ESCAPE_SKIP=U3,U4,J_HDMI python3 ../tools/escape.py $N.kicad_pcb 2>&1 | grep -E 'escape|no escape'   # the WQFN-42 display switches: the QFN scheme's vias collide on the 3.5 mm short sides, the router fans them itself
python3 ../tools/join_adjacent_pins.py $N.kicad_pcb 2>&1 | grep -E 'join_adjacent_pins|Traceback|Error'
python3 ../tools/prefanout.py $N.kicad_pcb 'GND,+5V_S1,+5V_S2,+5V_S3,+5V_DEV' fine   # only nets with a plane or pour to land on (7 Sep 2026: a pre-placed via of a net without a plane is one more open for the router) 2>&1 | grep -E 'fanout:'
kicad-cli pcb drc --severity-all --format json -o out/$N-preroute-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 ../tools/escape_prune.py $N.kicad_pcb out/$N-preroute-drc.json 2>&1 | grep escape_prune   # escapes in a hard violation go, the router fans those pads
cp $N.kicad_pcb out/$N-preroute.kicad_pcb
kicad-cli pcb drc --severity-all --format json -o out/$N-preroute-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - <<'PY'
import json, collections
d = json.load(open('out/pcb-b-compute-preroute-drc.json')); c = collections.Counter(v['type'] for v in d['violations']); print('pre-route DRC:', dict(c))
HARD = ('courtyards_overlap', 'shorting_items', 'clearance', 'copper_edge_clearance', 'hole_clearance', 'hole_to_hole', 'via_diameter', 'drill_out_of_range')
def _self(v):
    refs = [i.get('description', '').split('Footprint ')[-1] for i in v.get('items', [])]; return v['type'] == 'courtyards_overlap' and len(refs) == 2 and refs[0] == refs[1]
hard = sum(1 for v in d['violations'] if v['type'] in HARD and not _self(v))   # a footprint's own two courtyard polygons (the Wuerth USB 3 receptacle) are the library's business
for t in HARD:
    for v in [v for v in d['violations'] if v['type'] == t][:6]: print('  ', t, '|', ' / '.join(i.get('description', '')[:70] for i in v.get('items', [])))
open('out/preroute-gate.txt', 'w').write('OK' if hard == 0 else 'BLOCK %d' % hard)
PY
python3 ../tools/check_zone_nets.py $N.kicad_pcb 2>&1 | grep -E "FAIL|zone nets" || echo "BLOCK zone-nets" > out/preroute-gate.txt
echo PREROUTE-DONE $(cat out/preroute-gate.txt)
