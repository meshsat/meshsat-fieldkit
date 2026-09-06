#!/usr/bin/env bash
# One Freerouting attempt in its own scratch directory. Usage: route_one.sh <project dir> <name> <k> <passes>
set -uo pipefail
cd "$1"; N="$2"; K="$3"; P="$4"; W="out/par/$K"; mkdir -p "$W"
cp "out/$N-preroute.kicad_pcb" "$W/$N.kicad_pcb"; cp "$N.kicad_pro" "$W/$N.kicad_pro"
# FR_PLANE_NETS="GND" (6 Sep 2026 04:50): the zones of these nets on the FR_POWER_LAYERS layers stay in the DSN as planes, so the router connects their pins
# by a via into the plane instead of routing them as wires (B15's DSN listed 258 GND pins for the router, 37 percent of its connections). Default: none, as before.
python3 - "$W/$N.kicad_pcb" "$W/$N.dsn" "${FR_PLANE_NETS:-}" "${FR_POWER_LAYERS:-}" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); keep_nets = set(x for x in sys.argv[3].split(",") if x); keep_layers = set(sys.argv[4].split()); kept = 0
for z in list(b.Zones()):
    if not z.GetIsRuleArea() and z.GetNetname() in keep_nets and any(b.GetLayerName(l) in keep_layers for l in z.GetLayerSet().Seq()): kept += 1; continue
    if not z.GetIsRuleArea() and not z.GetZoneName().startswith(("VOUT island", "inductor tap")): b.Remove(z)
if keep_nets: print("planes kept in the DSN:", kept, "zone(s) of", sorted(keep_nets), "on", sorted(keep_layers))          # the A21 output islands and inductor taps stay as planes (their pads are connected by the fill and the gate checks it); every other plane, band and island out of the DSN: GND/+5V route as ordinary nets (A21 run 8 of 5 Sep 2026: bands exported as planes made the router end tracks at band edges the fill never reached; bands are protected by track keep-outs instead)
tmp = sys.argv[2].replace(".dsn", "-noplanes.kicad_pcb"); pcbnew.SaveBoard(tmp, b)
b2 = pcbnew.LoadBoard(tmp); print("DSN export:", pcbnew.ExportSpecctraDSN(b2, sys.argv[2]))
PY
JAR=${FR_JAR:-$HOME/bin/freerouting-1.9.0.jar}   # FR_JAR (6 Sep 2026, Stage 4 A/B): another Freerouting jar, e.g. ~/bin/freerouting-2.4.1.jar (needs Java 25)
JAVA=${FR_JAVA:-java}; V2_ARGS=()
case "$(basename "$JAR")" in freerouting-2.*) [ -x /usr/lib/jvm/java-25-openjdk-amd64/bin/java ] && [ -z "${FR_JAVA:-}" ] && JAVA=/usr/lib/jvm/java-25-openjdk-amd64/bin/java
  V2_ARGS=(--gui.enabled=false --api_server.enabled=false --mcp_server.enabled=false "--router.fanout.enabled=${FR_FANOUT:-false}" "--router.job_timeout=$(printf '%02d:%02d:%02d' $((${FR_TIMEOUT:-4500} / 3600)) $((${FR_TIMEOUT:-4500} % 3600 / 60)) $((${FR_TIMEOUT:-4500} % 60)))");;   # never -drc here: in 2.4.1 it turns the run into a DRC-only job (no session)
esac
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
# FR_RULES: a Freerouting rules file (tools/fr_rules.py) with via costs, ripup costs, layer directions and activity; the probe of 6 Sep 2026 showed it is the lever 1.9.0 honours.
# FR_RULES_INJECT=1 (6 Sep 2026 11:30): the file's (autoroute_settings ...) block is written INTO the DSN's structure and no -dr is passed: a -dr file that
# carries only autoroute settings made Freerouting drop the design's clearance and edge rules (B15 with a "default" rules file: 17 shorts, 16 clearance
# violations and a track along the board edge, against 0 hard without the file on the same DSN).
RULES_ARG=()
if [ -n "${FR_RULES:-}" ] && [ -f "${FR_RULES}" ]; then
  if [ "${FR_RULES_INJECT:-0}" = "1" ]; then python3 - "$W/$N.dsn" "$FR_RULES" <<'PYINJ'
import sys
dsn, rules = sys.argv[1], sys.argv[2]; s = open(dsn, errors="replace").read(); r = open(rules).read()
i = r.find("(autoroute_settings")
if i < 0: print("inject: no autoroute_settings block in", rules); sys.exit(0)
depth = 0; j = i
while j < len(r):
    if r[j] == "(": depth += 1
    elif r[j] == ")":
        depth -= 1
        if depth == 0: break
    j += 1
block = r[i:j + 1]
k = s.find("(boundary")
if k < 0: print("inject: no boundary in the DSN"); sys.exit(0)
s = s[:k] + block + "\n    " + s[k:]; open(dsn, "w").write(s); print("inject: autoroute_settings written into the DSN structure (%d chars)" % len(block))
PYINJ
  else RULES_ARG=(-dr "${FR_RULES}"); fi
fi
{ echo "{\"jar\": \"$(basename "$JAR")\", \"jar_sha256_16\": \"$(sha256sum "$JAR" | cut -c1-16)\", \"java\": \"$($JAVA -version 2>&1 | grep -m1 -i version | tr -d '"')\", \"passes\": $P, \"threads\": ${FR_THREADS:-6}, \"timeout\": ${FR_TIMEOUT:-4500}, \"power_layers\": \"${FR_POWER_LAYERS:-}\", \"rules\": \"${FR_RULES:-}\", \"start\": \"$(date -Iseconds)\"}"; } > "$W/run.json"
# absolute paths for the router (6 Sep 2026 04:30): two experiments on different project directories with the same board and configuration names produced
# identical relative command lines, and the clean-up kill below took the OTHER experiment's router with it (every 1.9.0 B15 route on the box died the moment
# its B14 twin finished). The kill pattern now carries this run's absolute session directory.
ADSN="$PWD/$W/$N.dsn"; ASES="$PWD/$W/$N.ses"
timeout ${FR_TIMEOUT:-4500} xvfb-run -a "$JAVA" -jar "$JAR" -de "$ADSN" -do "$ASES" -mp "$P" -mt ${FR_THREADS:-6} -oit 2 -dct 0 "${RULES_ARG[@]}" "${V2_ARGS[@]}" > "$W/fr.log" 2>&1 || echo "attempt $K: freerouting exit $?"
pkill -9 -f "java .*-de $(printf '%s' "$ADSN" | sed 's/[.]/\\./g') " 2>/dev/null || true
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
