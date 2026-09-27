#!/usr/bin/env bash
# route_part.sh <work dir> <partitioned dsn> <group> <passes> <timeout s> <part.json>: one Freerouting 1.9.0 job on one net group, every other group's
# classes ignored (-inc) and left on the board as obstacles. Writes <work dir>/<group>/route.ses and fr.log; prints PART-DONE <group> <exit>.
# Exit 8 in PART-DONE: the import was refused or lost something the DSN declares (fr_dialog_watch.sh), and no session is left to merge;
# exit 9: the import could not be confirmed. Records beside fr.log: import-probe.json, fr.log.watch.json (stage timing and every event).
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fr_jar.sh"
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fr_dialog_watch.sh"
W="$1"; DSN="$2"; G="$3"; P="$4"; T="$5"; PJ="$6"; mkdir -p "$W/$G"; rm -f "$W/$G/route.ses"   # a job that times out must not leave the PREVIOUS run's session to be merged (B19, 10 Sep 2026)
INC=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(','.join(c for g,cs in d['classes'].items() if g!=sys.argv[2] for c in cs))" "$PJ" "$G")
if [ "${CONFINE:-0}" = 1 ] && [ "$G" != GLOBAL ]; then python3 "$(dirname "$0")/dsn_confine.py" "$DSN" "$W/$G/job.dsn" "$PJ" "$G" ${CONFINE_LAYERS:-F.Cu In2.Cu In3.Cu B.Cu} && DSN="$W/$G/job.dsn"; fi   # CONFINE=1: keep-outs over the other regions' cores
JAR="$(fr_jar route_part)" || exit 2
echo "route_part $G: passes $P timeout $T ignoring $(echo "$INC" | tr ',' '\n' | wc -l) classes; start $(date -u +%H:%M:%S)"
# THE IMPORT IS CONFIRMED BEFORE THE ROUTE (MESHSAT-1357 round 8, review finding F): the jar imports this DSN once with
# the autorouter off and writes back what it holds, and fr_import_check.py compares it with the DSN. A loss, or a
# warning nobody has read, stops the job here instead of after hours of routing a board that is not the one declared.
fr_import_probe "$DSN" "$W/$G" "route_part $G"; _PRB=$?
if [ "$_PRB" != 0 ]; then
  echo "route_part $G: NO SESSION (the import $([ "$_PRB" = 3 ] && echo "was refused" || echo "could not be confirmed"); nothing was routed)"
  echo "PART-DONE $G $([ "$_PRB" = 3 ] && echo 8 || echo 9) $(date -u +%H:%M:%S)"; exit 0
fi
_XDISP=$(( 200 + ($$ + RANDOM) % 700 ))   # 12 September 2026: never let two routers race for a display (xvfb-run -a picks one by racing for it)
# THE MODAL DIALOG WATCHDOG, WHICH THIS LAUNCHER NEVER HAD (16 September 2026). route_one.sh got it on
# 15 September, when board B's router sat THREE HOURS on Freerouting's "The normalization of net failed"
# warning under Xvfb; this file launches the same jar the same way, was written on 7 September and never
# received it, so the first confined partition run of board B stalled on exactly that warning at 6 percent
# of one core. It is a shared function now (fr_dialog_watch.sh), because the fix reaching one launcher of
# five is what the last nine days cost.
timeout "$T" xvfb-run -n "$_XDISP" -a java -Dfreerouting.ses_per_pass="$W/$G/route.ses" -Dfreerouting.design_name="$(basename "$DSN")" -jar "$JAR" -de "$DSN" -do "$W/$G/route.ses" -mp "$P" -mt 1 -oit 100 -dct 0 -inc "$INC" > "$W/$G/fr.log" 2>&1 &
_RPID=$!
fr_watch "$_RPID" "$_XDISP" "$DSN" "route_part $G" "$W/$G/fr.log"; _FRW=$?
wait "$_RPID"; X=$?
if [ "$_FRW" = 3 ]; then
  [ -e "$W/$G/route.ses" ] && mv -f "$W/$G/route.ses" "$W/$G/route.ses.refused"
  echo "route_part $G: IMPORT-REFUSED during the run; no session is left to merge (fr.log.watch.json)"; X=8
elif [ "$_FRW" = 4 ] && [ ! -s "$W/$G/route.ses" ]; then
  echo "route_part $G: a stage limit stopped the router before any session (fr.log.watch.json)"; X=9
elif [ -s "$W/$G/route.ses" ]; then
  fr_after_route "$DSN" "$W/$G/route.ses" "route_part $G" "$W/$G/fr.log" "$INC"; _AR=$?
  if [ "$_AR" = 3 ]; then mv -f "$W/$G/route.ses" "$W/$G/route.ses.lost"; echo "route_part $G: the session lost something the DSN declares; not left to merge"; X=8; fi
fi
[ -s "$W/$G/route.ses" ] && echo "route_part $G: session $(stat -c %s "$W/$G/route.ses") bytes" || echo "route_part $G: NO SESSION"
echo "PART-DONE $G $X $(date -u +%H:%M:%S)"
