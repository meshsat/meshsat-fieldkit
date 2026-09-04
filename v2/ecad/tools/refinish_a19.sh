#!/usr/bin/env bash
# Re-run the A19 finishing tail on the routed board (stub router, clean-up, legends, finish), then rebuild the dock block from it.
cd "$(dirname "$0")/../pcb-a-power"
../tools/finish_a19.sh .. out/par-a19-pass5.log 2>&1 | grep -vE "Debug|leak"
cd ..; ./tools/build_e5.sh . meshsat-pcb-e5-revA-E5 2>&1 | grep -vE "Debug|leak" | tail -8
echo REFINISH-A19-DONE
