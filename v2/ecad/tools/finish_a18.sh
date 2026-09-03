#!/usr/bin/env bash
# Usage: finish_a18.sh <ecad dir> : A18 = the routed A17 board with the J_DOCK drills at 1.1 mm (bump_a18.py) and the schematic
# rebuilt for the J_DOCK part text (build_sch.sh, nets unchanged), then finish_board.sh (DRC, gerbers, JLC files, deliverable).
set -uo pipefail
cd "$1/pcb-a-power"; N=pcb-a-power
python3 ../tools/bump_a18.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak'
python3 ../tools/gen_sch_a.py $N.kicad_sch $N 2>&1 | tail -1
../tools/build_sch.sh . $N 2>&1 | grep -E 'ERC|netlist'
cd ..; ./tools/finish_board.sh pcb-a-power pcb-a-power - meshsat-pcb-a-revA-A18 2>&1 | tail -14
echo FINISH-A18-DONE
