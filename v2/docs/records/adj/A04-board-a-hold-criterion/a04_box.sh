#!/usr/bin/env bash
# A04 box driver (MESHSAT-1357): read-only. Everything writes under /root/r2/A04-board-a-hold-criterion/run.
set -u
B=/root/r2/A04-board-a-hold-criterion; R=$B/repo; O=$B/run; C=82dd1e4dc44efabeee1164a995cda4e866610f3d
rm -rf $O; mkdir -p $O/verdicts/trn001 $O/verdicts/sch002 $O/verdicts/cmp001_netlist $O/verdicts/cmp001_boardvalues
exec > >(tee $O/journal.txt) 2>&1
echo "A04 journal $(date -u +%FT%TZ) host $(hostname) clone $(git -C $R rev-parse HEAD) main-clone $(git -C /root/gitlab/products/meshsat/meshsat-fieldkit rev-parse HEAD)"
git -C $R status --short | head -5
echo "== 1. part-for-part comparison"
python3 $B/a04_compare.py $R $C $O; echo "exit $?"
T=$R/v2/ecad/tools; A=$R/v2/ecad/pcb-a-power-a23
echo "== 2. TRN-001 fresh on the committed netlist (port_protect.py)"
( cd $O/verdicts/trn001 && VERDICT_DIR=$O/verdicts/trn001 python3 $T/port_protect.py $A/out/pcb-a-power.net ); echo "exit $?"
echo "== 3. SCH-002 fresh: committed board against committed netlist (netlist_board.py)"
( cd $O/verdicts/sch002 && VERDICT_DIR=$O/verdicts/sch002 python3 $T/netlist_board.py $A/pcb-a-power.kicad_pcb $A/out/pcb-a-power.net ); echo "exit $?"
echo "== 4. CMP-001 on the committed netlist (derate.py)"
( cd $O/verdicts/cmp001_netlist && python3 $T/derate.py $A/out/pcb-a-power.net --intent $A/out/pcb-a-power-intent.json --out-dir $O/verdicts/cmp001_netlist ); echo "exit $?"
echo "== 5. CMP-001 on the same netlist carrying the BOARD's values (derate.py)"
( cd $O/verdicts/cmp001_boardvalues && python3 $T/derate.py $O/pcb-a-power.board-values.net --intent $A/out/pcb-a-power-intent.json --out-dir $O/verdicts/cmp001_boardvalues ); echo "exit $?"
echo "== 6. the clone is untouched"
git -C $R status --short | head -10
echo "done $(date -u +%FT%TZ)"
