#!/usr/bin/env bash
# PCB-A: regenerate A1 + netlist import + fanout, then the routing chain
set -uo pipefail
cd "$1"; N=pcb-a-power
python3 ../tools/gen_pcb_a.py $N.kicad_pcb 2>&1 | grep saved
python3 ../tools/gen_pcb_a3.py $N.kicad_pcb out/$N.net 2>&1 | grep -E 'saved|WARN|overflow|unplaced'
python3 ../tools/prefanout.py $N.kicad_pcb 'GND,+5V,CELL+' 2>&1 | grep -E 'fanout:'
cp $N.kicad_pcb out/$N-preroute.kicad_pcb
exec ../tools/full_route.sh . $N
