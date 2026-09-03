#!/usr/bin/env bash
# Parallel Freerouting attempts from one pre-route board; the winner (no hard DRC, fewest open connections, fewest vias) becomes the working board.
# Usage: route_parallel.sh <project dir> <name> "<passes list>"
set -uo pipefail
cd "$1"; N="$2"; rm -rf out/par; mkdir -p out/par; K=0
for P in $3; do K=$((K + 1)); ../tools/route_one.sh . "$N" "$K" "$P" > "out/par/run-$K.log" 2>&1 & done
wait
for d in out/par/*/; do k=$(basename "$d"); [ -f "$d/score.txt" ] && echo "$(cat $d/score.txt) $k" || echo "9999 9999 999999 $k"; done | sort -n -k1,1 -k2,2 -k3,3 > out/par/scores.txt
while read H U V k; do echo "attempt $k: hard $H unrouted $U vias $V"; done < out/par/scores.txt
read H U V best < out/par/scores.txt
cp "out/par/$best/$N.kicad_pcb" "$N.kicad_pcb"; echo "WINNER attempt $best: hard $H unrouted $U vias $V"
echo PARALLEL-DONE
