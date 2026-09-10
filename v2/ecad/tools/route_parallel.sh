#!/usr/bin/env bash
# Parallel Freerouting attempts from one pre-route board; the winner (no hard DRC, fewest open connections, fewest vias) becomes the working board.
# Usage: route_parallel.sh <project dir> <name> "<passes list>"
set -uo pipefail
cd "$1"; N="$2"; rm -rf out/par; mkdir -p out/par; K=0
# 10 September 2026 (round-two red teams, report 1 P0): this was a bare `wait`, which bash documents as returning zero when it
# is given no job ids, so every attempt's exit status was discarded before routeflow.py could see it. A tool failure inside an
# attempt (a session that would not import, a DRC that did not run, a score that was not written) then reached the supervisor
# as "no session" and drew a ROUTING remedy: another expensive route against an infrastructure fault. Each attempt is waited
# for by its own pid now and its status is kept; the supervisor exits non-zero when any attempt broke, which is what
# routeflow.py needs before INFRA_FAIL can ever fire.
PIDS=(); ATT=()
for P in $3; do K=$((K + 1)); ../tools/route_one.sh . "$N" "$K" "$P" > "out/par/run-$K.log" 2>&1 & PIDS+=($!); ATT+=("$K"); done
BROKE=0
for i in "${!PIDS[@]}"; do
  if wait "${PIDS[$i]}"; then :; else
    rc=$?; BROKE=$((BROKE + 1))
    echo "attempt ${ATT[$i]}: FAILED with exit $rc (see out/par/run-${ATT[$i]}.log)"
    rm -f "out/par/${ATT[$i]}/score.txt"   # a broken attempt scores nothing; it must not win by holding a stale file
  fi
done
for d in out/par/*/; do k=$(basename "$d"); [ -f "$d/score.txt" ] && echo "$(cat $d/score.txt) $k" || echo "9999 9999 999999 $k"; done | sort -n -k1,1 -k2,2 -k3,3 > out/par/scores.txt
while read H U V k; do echo "attempt $k: hard $H unrouted $U vias $V"; done < out/par/scores.txt
read H U V best < out/par/scores.txt
cp "out/par/$best/$N.kicad_pcb" "$N.kicad_pcb"; echo "WINNER attempt $best: hard $H unrouted $U vias $V"
echo PARALLEL-DONE
[ "$BROKE" -eq 0 ] || { echo "route_parallel: $BROKE of $K attempt(s) failed as infrastructure, not as routing"; exit 7; }
