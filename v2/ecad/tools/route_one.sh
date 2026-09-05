#!/usr/bin/env bash
# One Freerouting attempt in its own scratch directory. Usage: route_one.sh <project dir> <name> <k> <passes>
set -uo pipefail
cd "$1"; N="$2"; K="$3"; P="$4"; W="out/par/$K"; mkdir -p "$W"
cp "out/$N-preroute.kicad_pcb" "$W/$N.kicad_pcb"; cp "$N.kicad_pro" "$W/$N.kicad_pro"
python3 - "$W/$N.kicad_pcb" "$W/$N.dsn" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
for z in list(b.Zones()):
    if not z.GetIsRuleArea(): b.Remove(z)          # planes, bands and islands out of the DSN: GND/+5V route as ordinary nets (A21 run 8 of 5 Sep 2026: bands exported as planes made the router end tracks at band edges the fill never reached; bands are protected by track keep-outs instead)
tmp = sys.argv[2].replace(".dsn", "-noplanes.kicad_pcb"); pcbnew.SaveBoard(tmp, b)
b2 = pcbnew.LoadBoard(tmp); print("DSN export:", pcbnew.ExportSpecctraDSN(b2, sys.argv[2]))
PY
JAR=$HOME/bin/freerouting-1.9.0.jar
timeout 4500 xvfb-run -a java -jar "$JAR" -de "$W/$N.dsn" -do "$W/$N.ses" -mp "$P" -mt ${FR_THREADS:-6} -oit 2 -dct 0 > "$W/fr.log" 2>&1 || echo "attempt $K: freerouting exit $?"
pkill -9 -f "^java .*par/$K/$N\.dsn" 2>/dev/null || true
[ -s "$W/$N.ses" ] || { echo "9999 9999 999999" > "$W/score.txt"; echo "attempt $K: no session file (killed or crashed), scored out"; echo "ROUTE-ONE-DONE $K"; exit 0; }
python3 - "$W/$N.kicad_pcb" "$W/$N.ses" <<'PY'
import sys, os, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); ok = os.path.exists(sys.argv[2]) and pcbnew.ImportSpecctraSES(b, sys.argv[2]); print("SES import:", ok)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b)
print("tracks:", len([t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]), "vias:", len([t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]))
PY
python3 ../tools/net_tie.py "$W/$N.kicad_pcb" >/dev/null
kicad-cli pcb drc --severity-all --format json -o "$W/drc.json" "$W/$N.kicad_pcb" >/dev/null 2>&1
python3 - "$W" <<'PY'
import json, sys, collections
d = json.load(open(sys.argv[1] + "/drc.json")); c = collections.Counter(v["type"] for v in d["violations"])
hard = sum(c[t] for t in ("clearance", "shorting_items", "tracks_crossing", "hole_clearance", "hole_to_hole", "copper_edge_clearance")); unr = len(d.get("unconnected_items", []))
import re
s = open(sys.argv[1] + "/fr.log").read(); vias = len(re.findall(r"^\s*\(via ", open(sys.argv[1] + "/" + [f for f in __import__("os").listdir(sys.argv[1]) if f.endswith(".ses")][0]).read(), re.M)) if any(f.endswith(".ses") for f in __import__("os").listdir(sys.argv[1])) else 9999
open(sys.argv[1] + "/score.txt", "w").write("%d %d %d\n" % (hard, unr, vias)); print("score: hard %d unrouted %d vias %d" % (hard, unr, vias))
PY
echo "ROUTE-ONE-DONE $K"
