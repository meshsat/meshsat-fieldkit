#!/usr/bin/env bash
# kicad-cli's DRC with its report treated as an output rather than a file that happens to be there (10 September 2026,
# report 1 item 6). The target is deleted first and its absence afterwards is a failure, so no gate downstream can read the
# PREVIOUS run's report and call a board clean. Violations are not a failure here: kicad-cli exits non-zero when it finds any,
# and it is `hardset.py` that decides what a violation means.
# Usage: drc.sh <board.kicad_pcb> <report.json> [extra kicad-cli arguments]
set -uo pipefail
B="$1"; R="$2"; shift 2
rm -f "$R"
kicad-cli pcb drc --severity-all --format json -o "$R" "$@" "$B" >/dev/null 2>&1; X=$?
[ -s "$R" ] || { echo "drc: kicad-cli wrote no report for $B (exit $X)"; exit 1; }
exit 0
