#!/usr/bin/env bash
cd "$1"
wait_done() { while ! grep -q ROUTE-DONE "$1" 2>/dev/null; do sleep 30; done; }
wait_done pcb-b-compute/out/route-b6.log; echo "== B6 finish $(date +%H:%M)"; ./tools/finish_board.sh pcb-b-compute pcb-b-compute post_fix_b4.py meshsat-pcb-b-revA-B6 2>&1 | tail -14
wait_done pcb-a-power/out/route-a6.log;   echo "== A6 finish $(date +%H:%M)"; ./tools/finish_board.sh pcb-a-power pcb-a-power post_fix_a.py meshsat-pcb-a-revA-A6 2>&1 | tail -14
echo FINISH-TWO-DONE
