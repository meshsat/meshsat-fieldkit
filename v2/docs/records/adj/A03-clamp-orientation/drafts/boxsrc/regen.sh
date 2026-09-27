#!/usr/bin/env bash
# Regenerate each board's schematic and netlist from the HEAD generators in this private clone (no placement, no routing).
set -u
R=/root/r2/A03-clamp-orientation; C=$R/repo/v2/ecad; O=$R/out/regen; mkdir -p $O
cd $C
echo "clone HEAD $(git -C $R/repo rev-parse --short HEAD)" > $O/regen.log
for pair in "pcb-a-power-a23 a pcb-a-power" "pcb-b-compute-b19 b pcb-b-compute" "pcb-c-display-c8 c pcb-c-display" "pcb-d-aprs-d9 d pcb-d-aprs" "pcb-e1-dock-e7 e pcb-e1-dock" "pcb-p-pack-p2 p pcb-p-pack"; do
  set -- $pair; dir=$1; L=$2; N=$3
  cp $dir/out/$N.net $O/$N.committed.net
  ( cd $dir && python3 ../tools/gen_sch_$L.py $O/$N.kicad_sch $N > $O/gen_sch_$L.log 2>&1; echo "gen_sch_$L exit $?" ) >> $O/regen.log
  kicad-cli sch export netlist --format kicadsexpr -o $O/$N.regen.net $O/$N.kicad_sch > $O/net_$L.log 2>&1; echo "netlist $L exit $?" >> $O/regen.log
done
git -C $R/repo status --short > $O/clone_status_after.txt
cat $O/regen.log
