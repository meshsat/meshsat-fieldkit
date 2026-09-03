#!/usr/bin/env bash
# Full PCB-B phase B3 chain: B1 board -> netlist import + placement -> fanout -> route -> continuation -> close stubs -> DRC
set -uo pipefail
cd "$1"; N=pcb-b-compute
python3 ../tools/gen_pcb_b.py $N.kicad_pcb 2>&1 | grep saved
python3 ../tools/gen_pcb_b3.py $N.kicad_pcb out/$N.net 2>&1 | grep -E 'saved|WARN'
python3 ../tools/prefanout.py $N.kicad_pcb 2>&1 | grep -E 'fanout:'
cp $N.kicad_pcb out/$N-preroute.kicad_pcb
FR_XVFB=1 FR_JAR=$HOME/bin/freerouting-1.9.0.jar timeout 420 ../tools/route_pcb.sh . $N 30 2>&1 | grep -E 'SES import|tracks'
FR_XVFB=1 FR_JAR=$HOME/bin/freerouting-1.9.0.jar timeout 420 ../tools/route_pcb.sh . $N 40 2>&1 | grep -E 'SES import|tracks'
../tools/build_pcb.sh . $N 2>&1 | grep -E '^DRC'
python3 ../tools/finish_stubs.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -vi '^warning'
../tools/build_pcb.sh . $N 2>&1 | grep -E '^DRC'
grep -E '^\[' out/$N-drc.rpt | sed 's/:.*//' | sort | uniq -c | sort -rn | head -8
python3 - <<'PY'
import json, re, collections
d=json.load(open('out/pcb-b-compute-drc.json'))
c=collections.Counter()
for v in d.get('unconnected_items',[]):
    nets=set(re.findall(r'\[([^\]]+)\]', ' '.join(i.get('description','') for i in v.get('items',[])))); c[tuple(sorted(nets))]+=1
print('unrouted:', dict(c))
for v in d.get('unconnected_items',[]): print('   ', ' / '.join(i.get('description','')[:70] for i in v.get('items',[])))
for t in ('clearance','shorting_items','tracks_crossing','track_dangling','via_dangling','silk_overlap','silk_over_copper'):
    vs=[v for v in d['violations'] if v['type']==t]
    for v in vs[:3]: print(' ', t, '|', ' / '.join(i.get('description','')[:55] for i in v.get('items',[])))
PY
echo CHAIN-DONE
