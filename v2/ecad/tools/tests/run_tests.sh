#!/usr/bin/env bash
# The gate tests. Runs everywhere; the board fixtures skip where pcbnew is not importable.
# Usage: tests/run_tests.sh [name substring ...]
set -uo pipefail
cd "$(dirname "$0")"
python3 run.py "$@"; rc=$?
if [ -x ./golden_sch.sh ] && [ "${GOLDEN:-0}" = 1 ]; then ./golden_sch.sh || rc=1; fi
exit $rc
