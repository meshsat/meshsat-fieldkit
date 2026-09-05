#!/usr/bin/env bash
# Continuation route (A21, 5 Sep 2026): when the parallel attempts leave a few connections open, run Freerouting once more on the routed board
# (its tracks stay as normal wires, the router reroutes what is incomplete and may rip up the rest), then keep the result only if it is better.
# Usage: cont_route.sh <project dir> <name> <passes> [timeout s]; prints "cont: ..." lines; the board is replaced only when unrouted drops and hard stays 0.
set -uo pipefail
cd "$1"; N="$2"; P="${3:-80}"; T="${4:-900}"; W=out/cont; mkdir -p "$W"
cp "$N.kicad_pcb" "$W/$N-before.kicad_pcb"; cp "$N.kicad_pcb" "$W/$N.kicad_pcb"; cp "$N.kicad_pro" "$W/$N.kicad_pro"
python3 - "$W/$N.kicad_pcb" "$W/$N.dsn" <<'PYX'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
for z in list(b.Zones()):
    if not z.GetIsRuleArea() and not z.GetZoneName().startswith(("VOUT island", "inductor tap")): b.Remove(z)
tmp = sys.argv[2].replace(".dsn", "-noplanes.kicad_pcb"); pcbnew.SaveBoard(tmp, b)
b2 = pcbnew.LoadBoard(tmp); print("cont: DSN export", pcbnew.ExportSpecctraDSN(b2, sys.argv[2]))
PYX
JAR=$HOME/bin/freerouting-1.9.0.jar
timeout "$T" xvfb-run -a java -jar "$JAR" -de "$W/$N.dsn" -do "$W/$N.ses" -mp "$P" -mt ${FR_THREADS:-2} -oit 2 -dct 0 > "$W/fr.log" 2>&1 || echo "cont: freerouting exit $?"
pkill -9 -f "^java .*out/cont/$N\.dsn" 2>/dev/null || true
[ -s "$W/$N.ses" ] || { echo "cont: no session, board kept"; exit 0; }
python3 - "$W/$N.kicad_pcb" "$W/$N.ses" <<'PYX'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); print("cont: SES import", pcbnew.ImportSpecctraSES(b, sys.argv[2])); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b)
PYX
score() { kicad-cli pcb drc --severity-all --format json -o "$W/drc-$2.json" "$1" >/dev/null 2>&1; python3 - "$W/drc-$2.json" <<'PYX'
import json, collections, sys
d = json.load(open(sys.argv[1])); c = collections.Counter(v['type'] for v in d['violations'])
print(sum(c[t] for t in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'hole_to_hole', 'copper_edge_clearance')), len(d.get('unconnected_items', [])))
PYX
}
read H0 U0 < <(score "$W/$N-before.kicad_pcb" before); read H1 U1 < <(score "$W/$N.kicad_pcb" after)
echo "cont: before hard $H0 unrouted $U0, after hard $H1 unrouted $U1"
if [ "$H1" -eq 0 ] && [ "$U1" -lt "$U0" ]; then cp "$W/$N.kicad_pcb" "$N.kicad_pcb"; echo "cont: board replaced (unrouted $U0 -> $U1)"; else echo "cont: board kept"; fi
