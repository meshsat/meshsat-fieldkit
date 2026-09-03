#!/usr/bin/env bash
# Wait for each queued route to finish, then finish its board (runs unattended under nohup)
cd "$1"
wait_done() { while ! grep -q ROUTE-DONE "$1" 2>/dev/null; do sleep 30; done; }
wait_done pcb-b-compute/out/route-b5.log; echo "== B5 finish $(date +%H:%M)"; ./tools/finish_board.sh pcb-b-compute pcb-b-compute post_fix_b4.py meshsat-pcb-b-revA-B5 2>&1 | tail -14
wait_done pcb-a-power/out/route-a5.log;   echo "== A5 finish $(date +%H:%M)"; ./tools/finish_board.sh pcb-a-power pcb-a-power post_fix_a.py meshsat-pcb-a-revA-A5 2>&1 | tail -14
wait_done pcb-d-aprs/out/route-d3.log;    echo "== D3 finish $(date +%H:%M)"; ./tools/finish_board.sh pcb-d-aprs pcb-d-aprs post_fix_d.py meshsat-pcb-d-revA-D3 2>&1 | tail -14
echo FINISH-ALL-DONE
