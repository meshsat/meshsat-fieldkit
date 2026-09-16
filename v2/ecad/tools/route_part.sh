#!/usr/bin/env bash
# route_part.sh <work dir> <partitioned dsn> <group> <passes> <timeout s> <part.json>: one Freerouting 1.9.0 job on one net group, every other group's
# classes ignored (-inc) and left on the board as obstacles. Writes <work dir>/<group>/route.ses and fr.log; prints PART-DONE <group> <exit>.
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fr_jar.sh"
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fr_dialog_watch.sh"
W="$1"; DSN="$2"; G="$3"; P="$4"; T="$5"; PJ="$6"; mkdir -p "$W/$G"; rm -f "$W/$G/route.ses"   # a job that times out must not leave the PREVIOUS run's session to be merged (B19, 10 Sep 2026)
INC=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(','.join(c for g,cs in d['classes'].items() if g!=sys.argv[2] for c in cs))" "$PJ" "$G")
if [ "${CONFINE:-0}" = 1 ] && [ "$G" != GLOBAL ]; then python3 "$(dirname "$0")/dsn_confine.py" "$DSN" "$W/$G/job.dsn" "$PJ" "$G" ${CONFINE_LAYERS:-F.Cu In2.Cu In3.Cu B.Cu} && DSN="$W/$G/job.dsn"; fi   # CONFINE=1: keep-outs over the other regions' cores
JAR="$(fr_jar route_part)" || exit 2
echo "route_part $G: passes $P timeout $T ignoring $(echo "$INC" | tr ',' '\n' | wc -l) classes; start $(date -u +%H:%M:%S)"
_XDISP=$(( 200 + ($$ + RANDOM) % 700 ))   # 12 September 2026: never let two routers race for a display (xvfb-run -a picks one by racing for it)
# THE MODAL DIALOG WATCHDOG, WHICH THIS LAUNCHER NEVER HAD (16 September 2026). route_one.sh got it on
# 15 September, when board B's router sat THREE HOURS on Freerouting's "The normalization of net failed"
# warning under Xvfb; this file launches the same jar the same way, was written on 7 September and never
# received it, so the first confined partition run of board B stalled on exactly that warning at 6 percent
# of one core. It is a shared function now (fr_dialog_watch.sh), because the fix reaching one launcher of
# five is what the last nine days cost.
timeout "$T" xvfb-run -n "$_XDISP" -a java -Dfreerouting.ses_per_pass="$W/$G/route.ses" -Dfreerouting.design_name="$(basename "$DSN")" -jar "$JAR" -de "$DSN" -do "$W/$G/route.ses" -mp "$P" -mt 1 -oit 100 -dct 0 -inc "$INC" > "$W/$G/fr.log" 2>&1 &
_RPID=$!
fr_watch "$_RPID" "$_XDISP" "$DSN" "route_part $G"
wait "$_RPID"; X=$?
[ -s "$W/$G/route.ses" ] && echo "route_part $G: session $(stat -c %s "$W/$G/route.ses") bytes" || echo "route_part $G: NO SESSION"
echo "PART-DONE $G $X $(date -u +%H:%M:%S)"
