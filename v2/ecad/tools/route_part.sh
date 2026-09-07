#!/usr/bin/env bash
# route_part.sh <work dir> <partitioned dsn> <group> <passes> <timeout s> <part.json>: one Freerouting 1.9.0 job on one net group, every other group's
# classes ignored (-inc) and left on the board as obstacles. Writes <work dir>/<group>/route.ses and fr.log; prints PART-DONE <group> <exit>.
set -uo pipefail
W="$1"; DSN="$2"; G="$3"; P="$4"; T="$5"; PJ="$6"; mkdir -p "$W/$G"
INC=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(','.join(c for g,cs in d['classes'].items() if g!=sys.argv[2] for c in cs))" "$PJ" "$G")
echo "route_part $G: passes $P timeout $T ignoring $(echo "$INC" | tr ',' '\n' | wc -l) classes; start $(date -u +%H:%M:%S)"
timeout "$T" xvfb-run -a java -jar "$HOME/bin/freerouting-1.9.0.jar" -de "$DSN" -do "$W/$G/route.ses" -mp "$P" -mt 1 -oit 100 -dct 0 -inc "$INC" > "$W/$G/fr.log" 2>&1; X=$?
[ -s "$W/$G/route.ses" ] && echo "route_part $G: session $(stat -c %s "$W/$G/route.ses") bytes" || echo "route_part $G: NO SESSION"
echo "PART-DONE $G $X $(date -u +%H:%M:%S)"
