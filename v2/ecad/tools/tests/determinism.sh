#!/usr/bin/env bash
# Is the pre-route chain a function of its input? Run it twice in two clean copies and compare the BOARDS.
#
# Not in run_tests.sh: a chain takes minutes and needs KiCad, so this is the check you run on the box after
# touching a generator, escape.py, prefanout.py or anything else that lays copper. It is the standing form
# of the measurement of 11 September 2026 (MESHSAT-862, stage 0b), which found that two runs of D on
# identical input differed in four tracks and four vias because escape.py walked the board in the order
# KiCad had written it, and that order follows a random uuid.
#
# Usage: tests/determinism.sh <letter> [runs]      e.g. tests/determinism.sh d 3
# Exit 0 when every pair of runs produced the same board, 1 otherwise.
set -uo pipefail
L="${1:?usage: determinism.sh <letter> [runs]}"; K="${2:-2}"
T="$(cd "$(dirname "$0")/.." && pwd)"; E="$(cd "$T/.." && pwd)"
N="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['name'])" "$T/boards/$L.json")" || exit 2
export PREROUTE_STOP_AFTER_PLACE=1
tmp=$(mktemp -d); trap 'rm -rf "$tmp" "$E"/determinism-'"$L"'-*' EXIT
for r in $(seq 1 "$K"); do
  W="$E/determinism-$L-$r"; rm -rf "$W"; cp -a "$E/$N" "$W"; rm -rf "$W/out"; mkdir -p "$W/out"
  ( cd "$W" && bash "$T/full.sh" "$W" "$L" > "$tmp/run$r.log" 2>&1 )
  echo "determinism: $L run $r exit $? | $(tail -1 "$tmp/run$r.log")"
  [ -s "$W/out/$N-placed.kicad_pcb" ] || { echo "determinism: run $r wrote no placed board"; tail -6 "$tmp/run$r.log"; exit 1; }
done
rc=0
for i in $(seq 1 $((K-1))); do
  for j in $(seq $((i+1)) "$K"); do
    echo "determinism: $L run $i against run $j"
    ( cd "$E/determinism-$L-$i" && python3 "$T/board_diff.py" \
        "$E/determinism-$L-$i/out/$N-placed.kicad_pcb" "$E/determinism-$L-$j/out/$N-placed.kicad_pcb" \
        2>/dev/null | grep -E "^board_diff|^verdict" ) || rc=1
  done
done
echo "determinism: $L $([ $rc -eq 0 ] && echo "every pair of $K runs produced the same board" || echo "RUNS DIFFER")"
exit $rc
