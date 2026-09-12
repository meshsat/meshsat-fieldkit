#!/usr/bin/env bash
# Usage: route_pcb.sh <dir> <name> [passes]   : DSN export -> Freerouting -> SES import -> zone fill -> save
set -euo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fr_jar.sh"   # resolved before the cd below
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
JAR="$(fr_jar route_pcb)" || exit 2
echo "freerouting: $JAR, max passes $PASSES"
if [ -n "${FR_XVFB:-}" ] && command -v xvfb-run >/dev/null; then
  # 12 September 2026: this killed EVERY virtual display on the host, which would take any other route's router with
  # it. A named display plus xvfb-run's own walk-forward makes the stale-display problem local, and nothing else's
  # display is any of this script's business.
_XDISP=$(( 200 + ($$ + RANDOM) % 700 ))   # 12 September 2026: never let two routers race for a display (xvfb-run -a picks one by racing for it)
  nice -n 10 xvfb-run -n "$_XDISP" -a java -jar "$JAR" -de "out/$N.dsn" -do "out/$N.ses" -mp "$PASSES" -mt 1 -oit 2 -dct 0 > "out/$N-freerouting.log" 2>&1 || echo "freerouting exited non-zero (see log)"
else
  nice -n 10 java -Djava.awt.headless=true -jar "$JAR" -de "out/$N.dsn" -do "out/$N.ses" -mp "$PASSES" -mt 1 -oit 2 > "out/$N-freerouting.log" 2>&1 || echo "freerouting exited non-zero (see log)"
fi
tail -3 "out/$N-freerouting.log" | cut -c1-200
python3 - "$N.kicad_pcb" "out/$N.ses" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); ok = pcbnew.ImportSpecctraSES(b, sys.argv[2]); print("SES import:", ok)
f = pcbnew.ZONE_FILLER(b); f.Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b)
print("tracks:", len([t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]), "vias:", len([t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]))
PY
