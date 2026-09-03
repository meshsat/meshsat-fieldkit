#!/usr/bin/env bash
# Usage: route_pcb.sh <dir> <name> [passes]   : DSN export -> Freerouting -> SES import -> zone fill -> save
set -euo pipefail
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
JAR="${FR_JAR:-$(ls ~/bin/freerouting-*.jar | grep -v disabled | tail -1)}"
echo "freerouting: $JAR, max passes $PASSES"
if [ -n "${FR_XVFB:-}" ] && command -v xvfb-run >/dev/null; then
  pkill -9 -f "^Xvfb" 2>/dev/null || true; sleep 1   # stale virtual displays from killed runs block xvfb-run ("Couldn't create window frame")
  nice -n 10 xvfb-run -a java -jar "$JAR" -de "out/$N.dsn" -do "out/$N.ses" -mp "$PASSES" -mt 1 -oit 2 -dct 0 > "out/$N-freerouting.log" 2>&1 || echo "freerouting exited non-zero (see log)"
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
