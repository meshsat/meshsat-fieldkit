#!/usr/bin/env bash
# C5: footprints, pre-route chain, both gates (check_pcb_c ALL PASS and the pre-route DRC), then one Freerouting attempt (the panel rule) and the C5 finish.
cd "$(dirname "$0")/../pcb-c-display"
python3 ../tools/gen_footprints_panel.py ../meshsat.pretty 2>&1 | tail -1
../tools/full_c3.sh . 2>&1 | grep -vE "Debug|leak" | tee out/chain-c5.log
grep -q "RESULT: ALL PASS" out/chain-c5.log || { echo "CHAIN-C5-DONE BLOCK gate"; exit 1; }
grep -q "PREROUTE-DONE OK" out/chain-c5.log || { echo "CHAIN-C5-DONE BLOCK preroute"; exit 1; }
while pgrep -f "make_handof[f].py" >/dev/null; do sleep 30; done
../tools/route_parallel.sh . pcb-c-display "45" > out/par-c5.log 2>&1
grep -E "attempt|WINNER" out/par-c5.log
../tools/finish_c5.sh .. out/par-c5.log 2>&1 | grep -vE "Debug|leak"
echo CHAIN-C5-DONE
