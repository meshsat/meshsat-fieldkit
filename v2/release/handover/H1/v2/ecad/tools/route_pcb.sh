#!/usr/bin/env bash
# Usage: route_pcb.sh <dir> <name> [passes]   : DSN export -> Freerouting -> SES import -> zone fill -> save
set -euo pipefail
_TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # resolved before the cd below: every path to a tool uses it
. "$_TOOLS/fr_jar.sh"
D="$1"; N="$2"; PASSES="${3:-40}"; cd "$D"; mkdir -p out
python3 - "$N.kicad_pcb" "out/$N.dsn" <<'PY'
import sys, pcbnew
# export the routing job from a copy WITHOUT the copper planes, so GND / +5V are routed as ordinary nets
# (Freerouting treats plane-net pads as already connected otherwise); the real board keeps its planes
b = pcbnew.LoadBoard(sys.argv[1])
for z in list(b.Zones()):
    if not z.GetIsRuleArea(): b.Remove(z)
tmp = sys.argv[2].replace(".dsn", "-noplanes.kicad_pcb"); pcbnew.SaveBoard(tmp, b)
b2 = pcbnew.LoadBoard(tmp); ok = pcbnew.ExportSpecctraDSN(b2, sys.argv[2]); print("DSN export (no planes):", ok)
PY
# 12 September 2026: this was `ls ~/bin/freerouting-*.jar | tail -1`, which on a host carrying 2.4.1 picks it and
# launches it with 1.9.0 arguments under whatever java is first on PATH. long_route.sh pinned the stock jar by
# name to dodge exactly that, and so lost the per-pass session as well.
. "$_TOOLS/fr_dialog_watch.sh"   # round 8: this sat after the cd and resolved a relative script path against the project
JAR="$(fr_jar route_pcb)" || exit 2
echo "freerouting: $JAR, max passes $PASSES"
if [ -n "${FR_XVFB:-}" ] && command -v xvfb-run >/dev/null; then
  # 12 September 2026: this killed EVERY virtual display on the host, which would take any other route's router with
  # it. A named display plus xvfb-run's own walk-forward makes the stale-display problem local, and nothing else's
  # display is any of this script's business.
_XDISP=$(( 200 + ($$ + RANDOM) % 700 ))   # 12 September 2026: never let two routers race for a display (xvfb-run -a picks one by racing for it)
  # the dialog watchdog, 16 September 2026 (fr_dialog_watch.sh): this launcher never had it either
  # the import is confirmed first (MESHSAT-1357 round 8, review finding F; fr_dialog_watch.sh)
  fr_import_probe "$PWD/out/$N.dsn" "$PWD/out" "route_pcb" || { echo "route_pcb: the import was refused or could not be confirmed (out/import-probe.json); nothing routed"; exit 8; }
  nice -n 10 xvfb-run -n "$_XDISP" -a java -jar "$JAR" -de "$PWD/out/$N.dsn" -do "out/$N.ses" -mp "$PASSES" -mt 1 -oit 2 -dct 0 > "out/$N-freerouting.log" 2>&1 &
  _RPID=$!
  _FRW=0; fr_watch "$_RPID" "$_XDISP" "$PWD/out/$N.dsn" "route_pcb" "$PWD/out/$N-freerouting.log" || _FRW=$?
  wait "$_RPID" || echo "freerouting exited non-zero (see log)"
  [ "$_FRW" = 0 ] || { echo "route_pcb: IMPORT-REFUSED or stopped during the run (out/$N-freerouting.log.watch.json); the session is not imported"; exit 8; }
else
  nice -n 10 java -Djava.awt.headless=true -jar "$JAR" -de "out/$N.dsn" -do "out/$N.ses" -mp "$PASSES" -mt 1 -oit 2 > "out/$N-freerouting.log" 2>&1 || echo "freerouting exited non-zero (see log)"
  # headless there is no dialog to read, so the import's log is read instead: an unknown warning keeps the session out
  python3 "$_TOOLS/fr_import_check.py" classify "out/$N-freerouting.log" "out/$N.dsn" --stage import --json "out/$N-freerouting.log.import.json" \
    || { echo "route_pcb: the import logged something that is not understood (out/$N-freerouting.log.import.json); the session is not imported"; exit 8; }
fi
tail -3 "out/$N-freerouting.log" | cut -c1-200
[ -s "out/$N.ses" ] && { fr_after_route "$PWD/out/$N.dsn" "out/$N.ses" "route_pcb" "$PWD/out/$N-freerouting.log" || [ $? != 3 ] || { echo "route_pcb: the session lost something the DSN declares; not imported"; exit 8; }; }
python3 - "$N.kicad_pcb" "out/$N.ses" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); ok = pcbnew.ImportSpecctraSES(b, sys.argv[2]); print("SES import:", ok)
sys.path.insert(0, "../tools"); import ses_via_drill; ses_via_drill.restore_board(b, sys.argv[2])
f = pcbnew.ZONE_FILLER(b); f.Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b)
print("tracks:", len([t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]), "vias:", len([t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]))
PY
