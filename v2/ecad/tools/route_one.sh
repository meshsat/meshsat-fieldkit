#!/usr/bin/env bash
# One Freerouting attempt in its own scratch directory. Usage: route_one.sh <project dir> <name> <k> <passes>
set -uo pipefail
cd "$1"; N="$2"; K="$3"; P="$4"; W="out/par/$K"; mkdir -p "$W"
cp "out/$N-preroute.kicad_pcb" "$W/$N.kicad_pcb"; cp "$N.kicad_pro" "$W/$N.kicad_pro"
python3 - "$W/$N.kicad_pcb" "$W/$N.dsn" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
for z in list(b.Zones()):
    if not z.GetIsRuleArea() and not z.GetZoneName().startswith(("VOUT island", "inductor tap")): b.Remove(z)          # the A21 output islands and inductor taps stay as planes (their pads are connected by the fill and the gate checks it); every other plane, band and island out of the DSN: GND/+5V route as ordinary nets (A21 run 8 of 5 Sep 2026: bands exported as planes made the router end tracks at band edges the fill never reached; bands are protected by track keep-outs instead)
tmp = sys.argv[2].replace(".dsn", "-noplanes.kicad_pcb"); pcbnew.SaveBoard(tmp, b)
b2 = pcbnew.LoadBoard(tmp); print("DSN export:", pcbnew.ExportSpecctraDSN(b2, sys.argv[2]))
PY
JAR=$HOME/bin/freerouting-1.9.0.jar
# FR_POWER_LAYERS="In1.Cu In4.Cu" (5 Sep 2026, B15): plane layers become power-type layers in the DSN (Freerouting routes no wire there, vias pass)
# and their board-wide wire keep-outs are dropped; a board-wide wire_keepout polygon made the router thrash for the whole time limit (B14 In1 test, B15 run 1)
if [ -n "${FR_POWER_LAYERS:-}" ]; then python3 - "$W/$N.dsn" $FR_POWER_LAYERS <<'PYPL'
import re, sys
fn = sys.argv[1]; layers = sys.argv[2:]; s = open(fn).read(); n1 = 0
for lay in layers:
    s, k = re.subn(r"(\(layer %s\s*\(type )signal(\))" % re.escape(lay), r"\1power\2", s); n1 += k
out = []; i = 0; n2 = 0
while True:
    j = s.find("(wire_keepout", i)
    if j < 0: out.append(s[i:]); break
    depth = 0; k = j
    while k < len(s):
        if s[k] == "(": depth += 1
        elif s[k] == ")":
            depth -= 1
            if depth == 0: break
        k += 1
    block = s[j:k + 1]
    if any(("(polygon %s" % lay) in block for lay in layers): out.append(s[i:j]); n2 += 1
    else: out.append(s[i:k + 1])
    i = k + 1
open(fn, "w").write("".join(out)); print("power layers in the DSN:", ", ".join(layers), "(%d layer types changed, %d wire keep-outs dropped)" % (n1, n2))
PYPL
fi
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
