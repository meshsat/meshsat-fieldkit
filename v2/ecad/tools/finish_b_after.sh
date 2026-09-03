#!/usr/bin/env bash
# wait for a B route, then stubs + finish. Usage: finish_b_after.sh <carrier dir> <route log name> <downloads name>
cd "$1"; while ! grep -q ROUTE-DONE "pcb-b-compute/out/$2" 2>/dev/null; do sleep 30; done
./tools/stub_and_finish.sh pcb-b-compute pcb-b-compute post_fix_b4.py "$3" 2>&1 | tail -14; echo B-FINISH-DONE
