#!/usr/bin/env bash
# Parallel Freerouting attempts from one pre-route board; the winner (no hard DRC, fewest open connections, fewest vias) becomes the working board.
# Usage: route_parallel.sh <project dir> <name> "<variant list>"
#
# A VARIANT IS `<passes>[:<via_costs>[:<ripup_costs>]]`, and the reason it is not just a pass count is that
# FREEROUTING IS DETERMINISTIC (5 September 2026: three attempts differing only in their pass ceiling returned
# byte-identical results, because the autorouter finished before any ceiling). Racing attempts that differ in
# nothing the router reads is racing one attempt N times. What the router does read is the rules file, and the
# capability probe of 6 September measured it: via_costs 200 against the default 50 cut board D's vias by 25
# percent for 13 percent more length. So a variant carries its own rules file and its own ceiling, the attempts
# run side by side on a box that is otherwise idle, and the best board wins on the same three numbers as before.
#
# `route_parallel.sh . pcb-b-compute "20 20:200 12:100:20 8:400"` is four genuinely different searches.
# A bare number keeps the old meaning exactly, so every existing caller is unchanged.
set -uo pipefail
cd "$1"; N="$2"; rm -rf out/par; mkdir -p out/par; K=0
# 10 September 2026 (round-two red teams, report 1 P0): this was a bare `wait`, which bash documents as returning zero when it
# is given no job ids, so every attempt's exit status was discarded before routeflow.py could see it. A tool failure inside an
# attempt (a session that would not import, a DRC that did not run, a score that was not written) then reached the supervisor
# as "no session" and drew a ROUTING remedy: another expensive route against an infrastructure fault. Each attempt is waited
# for by its own pid now and its status is kept; the supervisor exits non-zero when any attempt broke, which is what
# routeflow.py needs before INFRA_FAIL can ever fire.
PIDS=(); ATT=()
for V in $3; do
  K=$((K + 1))
  P="${V%%:*}"; REST="${V#*:}"
  if [ "$REST" = "$V" ]; then
    # a bare pass count: the caller's own FR_RULES (if any) applies, which is the behaviour every profile has today
    ../tools/route_one.sh . "$N" "$K" "$P" > "out/par/run-$K.log" 2>&1 & PIDS+=($!); ATT+=("$K")
  else
    VC="${REST%%:*}"; RU="${REST#*:}"; [ "$RU" = "$REST" ] && RU=""
    mkdir -p "out/par/$K"
    # the rules file needs the DSN's layer list, and the DSN is written by route_one.sh inside the attempt.
    # fr_rules.py falls back to every layer name it can find in the file, so the PRE-ROUTE dsn of the previous
    # run serves when one exists and the attempt writes its own otherwise; either way the costs are what differ.
    _SRC="out/$N.dsn"; [ -f "$_SRC" ] || _SRC="out/par/1/$N.dsn"
    if [ -f "$_SRC" ]; then
      python3 ../tools/fr_rules.py "$_SRC" "out/par/$K/variant.rules" --via-costs "$VC" ${RU:+--ripup "$RU"} > "out/par/$K/rules.log" 2>&1 \
        && echo "attempt $K: via_costs $VC${RU:+ ripup $RU}, $P passes"
      FR_RULES="$PWD/out/par/$K/variant.rules" ../tools/route_one.sh . "$N" "$K" "$P" > "out/par/run-$K.log" 2>&1 & PIDS+=($!); ATT+=("$K")
    else
      echo "attempt $K: no DSN to write a rules file from, running the caller's rules with $P passes"
      ../tools/route_one.sh . "$N" "$K" "$P" > "out/par/run-$K.log" 2>&1 & PIDS+=($!); ATT+=("$K")
    fi
  fi
done
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
