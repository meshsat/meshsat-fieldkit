#!/usr/bin/env bash
# C6 (5 Sep 2026): footprints, pre-route chain, both gates (check_pcb_c ALL PASS and the pre-route DRC), then one Freerouting attempt (the panel rule) and the C6 finish. Run it with the outer log elsewhere than out/chain-c6-inner.log.
cd "$(dirname "$0")/../pcb-c-display"
python3 ../tools/gen_footprints_panel.py ../meshsat.pretty 2>&1 | tail -1
../tools/full_c3.sh . 2>&1 | grep -vE "Debug|leak" | tee out/chain-c6-inner.log
grep -q "RESULT: ALL PASS" out/chain-c6.log || { echo "CHAIN-C6-DONE BLOCK gate"; exit 1; }
grep -q "PREROUTE-DONE OK" out/chain-c6.log || { echo "CHAIN-C6-DONE BLOCK preroute"; exit 1; }
while pgrep -f "make_handof[f].py" >/dev/null; do sleep 30; done
FR_THREADS=1 ../tools/route_parallel.sh . pcb-c-display "80" > out/par-c6.log 2>&1   # single thread: the multi-threaded optimiser is documented to leave clearance violations (C6 run 3 had one); 80 passes for the two-layer cluster
grep -E "attempt|WINNER" out/par-c6.log
../tools/finish_c6.sh .. out/par-c6.log 2>&1 | grep -vE "Debug|leak"
echo CHAIN-C6-DONE
