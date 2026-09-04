#!/usr/bin/env bash
# A19 pass 5: pre-route chain with locked fine-pitch escapes, four parallel routes, finish. Run from anywhere.
cd "$(dirname "$0")/../pcb-a-power"
../tools/full_a7.sh . 2>&1 | tee out/chain-a7-pass5.log
grep -q "PREROUTE-DONE OK" out/chain-a7-pass5.log || { echo "CHAIN-A19-PASS5-DONE BLOCK"; exit 1; }
../tools/route_parallel.sh . pcb-a-power "20 30 45 60" > out/par-a19-pass5.log 2>&1
grep -E "attempt|WINNER" out/par-a19-pass5.log
../tools/finish_a19.sh .. out/par-a19-pass5.log 2>&1 | grep -vE "Debug|leak"
echo CHAIN-A19-PASS5-DONE
