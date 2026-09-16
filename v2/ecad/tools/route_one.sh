#!/usr/bin/env bash
# One Freerouting attempt in its own scratch directory. Usage: route_one.sh <project dir> <name> <k> <passes>
set -uo pipefail
_TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # resolved before the cd below, like the jar
. "$_TOOLS/fr_jar.sh"
cd "$1"; N="$2"; K="$3"; P="$4"; W="out/par/$K"; mkdir -p "$W"
# 13 September 2026 (MESHSAT-862): A ROUTE THAT DROPS ITS BOARD'S PLANE NETS MEASURES NOTHING, and I made
# that mistake twice in one afternoon. D's PWR class arm came back hard 0 with 121 unrouted and FOUR vias,
# and C's route hard 0 with 37 open, both because the driver set neither FR_PLANE_NETS nor FR_POWER_LAYERS
# while the board's own routeflow profile declares them: every ground pin then goes into the WIRE list at the
# class width instead of being reached by a via into a plane. Both numbers were withdrawn. The profiles are
# where those settings live, so a route started without them on a board whose profile declares them is
# refused here, at the one place every launcher passes through. FR_PLANES_CHECKED=0 says it was deliberate.
if [ "${FR_PLANES_CHECKED:-1}" != "0" ] && [ -z "${FR_PLANE_NETS:-}${FR_POWER_LAYERS:-}" ]; then
  _want=$(python3 - "$_TOOLS/routeflow" "$N" <<'PYCHK'
import glob, json, os, sys
d, stem = sys.argv[1], sys.argv[2]
for f in sorted(glob.glob(os.path.join(d, "*.json"))):
    try: p = json.load(open(f))
    except Exception: continue
    if p.get("board") != stem: continue
    r = p.get("route") or {}
    if r.get("plane_nets") or r.get("power_layers"):
        print("%s declares plane_nets %s on power_layers %s" % (os.path.basename(f), r.get("plane_nets"), r.get("power_layers")))
        break
PYCHK
)
  if [ -n "$_want" ]; then
    echo "route_one: REFUSED. This board's profile $_want, and this route sets neither FR_PLANE_NETS nor" >&2
    echo "           FR_POWER_LAYERS, so every pin of those nets would be routed as a wire and the result" >&2
    echo "           would measure the launcher and not the board. Set them, or FR_PLANES_CHECKED=0 to say" >&2
    echo "           the omission is deliberate." >&2
    exit 2
  fi
fi
cp "out/$N-preroute.kicad_pcb" "$W/$N.kicad_pcb"; cp "$N.kicad_pro" "$W/$N.kicad_pro"
# FR_PLANE_NETS="GND" (6 Sep 2026 04:50): the zones of these nets on the FR_POWER_LAYERS layers stay in the DSN as planes, so the router connects their pins
# by a via into the plane instead of routing them as wires (B15's DSN listed 258 GND pins for the router, 37 percent of its connections). Default: none, as before.
# FR_RAIL_PLANES=1 (15 September 2026, red team round four C2a, a MEASUREMENT): the locked rail copper of power_copper.py
# (a band or island whose net is a rail of the intent file and which carries a same-layer track keep-out) stays in the
# DSN as a plane on its own layer, so the router sees the rail's pads connected and lays no parallel wire for rail_prune
# to take off afterwards. The record's caution stands (32.39: a DSN plane is a connection and not an obstacle, and a track
# along a plane's edge made the fill retreat and cut an island's neck), which is why this is off until an A route
# measures it: rail_prune must then report nothing removed and the rails must still read MET.
python3 - "$W/$N.kicad_pcb" "$W/$N.dsn" "${FR_PLANE_NETS:-}" "${FR_POWER_LAYERS:-}" "${FR_RAIL_PLANES:-0}" "out/$N-intent.json" <<'PY'
import sys, json, os, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); keep_nets = set(x for x in sys.argv[3].split(",") if x); keep_layers = set(sys.argv[4].split()); kept = 0; rails_kept = 0
rails = set()
if sys.argv[5] == "1" and os.path.exists(sys.argv[6]):
    rails = {r.lstrip("/") for r in (json.load(open(sys.argv[6])).get("rails") or {})}
keepouts = [(z.GetFirstLayer(), z.Outline()) for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowTracks()]
def rail_zone(z):
    if z.GetIsRuleArea() or z.GetNetname().lstrip("/") not in rails: return False
    c = z.GetBoundingBox().GetCenter()
    return any(L == z.GetFirstLayer() and o.Contains(c) for L, o in keepouts)
for z in list(b.Zones()):
    if not z.GetIsRuleArea() and z.GetNetname() in keep_nets and any(b.GetLayerName(l) in keep_layers for l in z.GetLayerSet().Seq()): kept += 1; continue
    if rails and rail_zone(z): rails_kept += 1; continue
    if not z.GetIsRuleArea() and not z.GetZoneName().startswith(("VOUT island", "inductor tap")): b.Remove(z)
if keep_nets: print("planes kept in the DSN:", kept, "zone(s) of", sorted(keep_nets), "on", sorted(keep_layers))
if rails: print("rail planes kept in the DSN (FR_RAIL_PLANES):", rails_kept, "zone(s) of", sorted(rails))          # the A21 output islands and inductor taps stay as planes (their pads are connected by the fill and the gate checks it); every other plane, band and island out of the DSN: GND/+5V route as ordinary nets (A21 run 8 of 5 Sep 2026: bands exported as planes made the router end tracks at band edges the fill never reached; bands are protected by track keep-outs instead)
tmp = sys.argv[2].replace(".dsn", "-noplanes.kicad_pcb"); pcbnew.SaveBoard(tmp, b)
b2 = pcbnew.LoadBoard(tmp); print("DSN export:", pcbnew.ExportSpecctraDSN(b2, sys.argv[2]))
PY
# Our 1.9.0 build when it is on the host, the stock jar otherwise (10 September 2026). The patch adds a per-pass session write
# and nothing else, proved: on the same D board DSN with the same options the two jars produced BYTE IDENTICAL final sessions
# (139,311 bytes, cmp clean) and auto-routed in 1 min 23.13 s against 1 min 24.08 s. FR_JAR names another jar, e.g.
# ~/bin/freerouting-2.4.1.jar (needs Java 25).
JAR="$(fr_jar route_one)" || exit 2   # one answer for every launcher (tools/fr_jar.sh), python side routeflow.jar_in_use()
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
# FR_LAYER_RULES="USB:F.Cu,In2.Cu;RF:F.Cu,In2.Cu" (8 Sep 2026, MESHSAT-862 rule 2 of appendix 32.67): a net class may only use the listed copper layers
# (the layers with a plane next to them); written as (use_layer ...) into the class's (circuit ...) block of the DSN, which Freerouting honours.
if [ -n "${FR_LAYER_RULES:-}" ]; then python3 - "$W/$N.dsn" "$FR_LAYER_RULES" <<'PYLR'
import re, sys
fn = sys.argv[1]; s = open(fn).read(); n = 0
for rule in sys.argv[2].split(";"):
    if ":" not in rule: continue
    cls, layers = rule.split(":", 1); layers = [l.strip() for l in layers.split(",") if l.strip()]
    m = re.search(r"\(class %s\b" % re.escape(cls.strip()), s)
    if not m: print("layer rule: class %s not in the DSN" % cls); continue
    j = s.find("(circuit", m.end()); k = s.find("(class ", m.end())
    if j < 0 or (0 < k < j): print("layer rule: class %s has no (circuit) block" % cls); continue
    s = s[:j + len("(circuit")] + "\n        (use_layer %s)" % " ".join(layers) + s[j + len("(circuit"):]; n += 1
    print("layer rule: class %s on %s" % (cls, " ".join(layers)))
open(fn, "w").write(s); print("layer rules in the DSN: %d class(es)" % n)
PYLR
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
# 10 September 2026 (MESHSAT-862, red team M2): the per-pass session. Our build of 1.9.0 writes the Specctra session after every
# pass when -Dfreerouting.ses_per_pass names a file (tools/freerouting/ses_per_pass.py; proved on a D board DSN: seven sessions
# in ninety seconds, each importable by KiCad). It writes to the SAME path the run ends at, atomically, so a route that hits its
# time limit now leaves the best board it reached instead of nothing. The stock jar ignores an unknown -D property, so this line
# is safe with either jar and the NO_SESSION path stays for the stock one.
# 12 September 2026: `xvfb-run -a` picks a free display by RACING for it, so two routes started a minute apart
# on one host can land on the same number. This was suspected of killing C10's router at pass 24 of 60 and
# THAT WAS WRONG (the router was alive and the gap was the pass cadence), but the race is real and naming a
# display costs nothing. `-n` names one per work directory and `-a` still walks forward if it is taken.
_XDISP=$(( 200 + ($$ + $(printf '%s' "$W" | cksum | cut -d' ' -f1)) % 700 ))
# 15 September 2026 (MESHSAT-862): B19's router sat for THREE HOURS on a modal dialog under Xvfb ("The normalization of net
# /PCIE2_CLK_N failed: We reached the maximum normalization depth (16)", five pair nets whose fixed pieces Freerouting could
# not normalise), computing nothing, until a screenshot of its display showed the OK button and Return was sent to it; the
# route then ran normally. A warning the GUI holds for a click is not a route result. The router runs in the background and
# a watchdog reads its CPU time every 30 s; when it has not moved for 60 s inside the first twenty minutes and xdotool is
# on the host, Return goes to that display (the auth cookie is the one xvfb-run wrote for it) and the log says so.
timeout ${FR_TIMEOUT:-4500} xvfb-run -n "$_XDISP" -a "$JAVA" -Dfreerouting.ses_per_pass="$ASES" -Dfreerouting.design_name="$N.dsn" -jar "$JAR" -de "$ADSN" -do "$ASES" -mp "$P" -mt ${FR_THREADS:-6} -oit ${FR_OIT:-2} -dct 0 "${RULES_ARG[@]}" "${V2_ARGS[@]}" > "$W/fr.log" 2>&1 || echo "attempt $K: freerouting exit $?" &
_RPID=$!; _CPU0=-1; _STILL=0; _T0=$(date +%s)
while kill -0 "$_RPID" 2>/dev/null; do
  sleep 30
  _J=$(pgrep -f "[j]ava .*-de $(printf '%s' "$ADSN" | sed 's/[.]/\\./g') " | head -1)
  [ -n "$_J" ] || continue
  _CPU=$(awk '{print $14+$15}' /proc/$_J/stat 2>/dev/null || echo -1)
  if [ "$_CPU" = "$_CPU0" ]; then _STILL=$((_STILL+1)); else _STILL=0; fi; _CPU0=$_CPU
  # THE OPTIMISER IS NOT THE ROUTE, AND IT HAS HELD THIS BOX FOR HOURS (16 September 2026; the evidence is
  # 14 September's E8, fifteen minutes of autoroute and two hours forty of optimiser, none of it used, and
  # today's E12, twenty-eight minutes of autoroute converging at pass 232 of 260 and an optimiser that would
  # have run to the three-hour cap and been killed with nothing kept). Our build writes the session after
  # every autoroute pass, so the moment the autoroute is finished the result is already on disk; the
  # optimiser only improves length and vias, and only if the WHOLE job ends before the time limit. It is
  # given the autoroute's own duration to do that, with a five-minute floor, and then the run is stopped and
  # the session kept. FR_OPT_MAX_S sets the bound directly; FR_OPT_MAX_S=0 removes it.
  if [ -z "${_OPT_T0:-}" ] && grep -q "Auto-routing was completed" "$W/fr.log" 2>/dev/null; then
    _OPT_T0=$(date +%s); _AUTO=$(( _OPT_T0 - _T0 ))
    _OPT_CAP=${FR_OPT_MAX_S-$_AUTO}; [ "$_OPT_CAP" -lt 300 ] && [ "$_OPT_CAP" != 0 ] && _OPT_CAP=300
    echo "route_one: the autoroute finished in ${_AUTO}s and the optimiser has started; it is bounded to ${_OPT_CAP}s (0 = unbounded)"
  fi
  if [ -n "${_OPT_T0:-}" ] && [ "${_OPT_CAP:-0}" != 0 ] && [ -s "$W/$N.ses" ] \
     && [ $(( $(date +%s) - _OPT_T0 )) -ge "$_OPT_CAP" ]; then
    echo "route_one: stopping the optimiser after ${_OPT_CAP}s; the session the last autoroute pass wrote is kept"
    kill -TERM "$_J" 2>/dev/null || true
    break
  fi
  if [ "$_STILL" -ge 2 ] && [ $(( $(date +%s) - _T0 )) -lt 1200 ]; then
    if command -v xdotool >/dev/null 2>&1; then
      for _XA in $(ls -t /tmp/xvfb-run.*/Xauthority 2>/dev/null); do
        XAUTHORITY="$_XA" DISPLAY=":$_XDISP" xdotool key --clearmodifiers Return >/dev/null 2>&1 && { echo "route_one: the router had no CPU progress for 60 s on display :$_XDISP; Return sent to its window (a modal warning Freerouting holds for a click)"; break; }
      done
    else echo "route_one: the router has had no CPU progress for 60 s on display :$_XDISP and xdotool is not on this host to dismiss a dialog"; fi
    _STILL=0
  fi
done
wait "$_RPID" 2>/dev/null || true
pkill -9 -f "java .*-de $(printf '%s' "$ADSN" | sed 's/[.]/\\./g') " 2>/dev/null || true
[ -s "$W/$N.ses" ] || { echo "9999 9999 999999" > "$W/score.txt"; echo "attempt $K: no session file (killed or crashed), scored out"; echo "ROUTE-ONE-DONE $K"; exit 0; }
# 10 September 2026 (round-two red teams, report 1 P0): the import, the DRC and the score used to fail silently and the attempt
# still ended `ROUTE-ONE-DONE` with exit 0, so `routeflow.py` could never tell a broken attempt from a board that would not
# route and applied a routing remedy to an infrastructure failure. Each step reports now and the attempt exits non-zero.
python3 - "$W/$N.kicad_pcb" "$W/$N.ses" <<'PY'
import sys, os, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); ok = os.path.exists(sys.argv[2]) and pcbnew.ImportSpecctraSES(b, sys.argv[2]); print("SES import:", ok)
if not ok: sys.exit(4)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b)
print("tracks:", len([t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]), "vias:", len([t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]))
PY
IMP=$?; [ "$IMP" -eq 0 ] || { echo "attempt $K: the session did not import (exit $IMP)"; echo "ROUTE-ONE-DONE $K"; exit 4; }
python3 ../tools/net_tie.py "$W/$N.kicad_pcb" >/dev/null
../tools/drc.sh "$W/$N.kicad_pcb" "$W/drc.json" || { echo "attempt $K: the DRC did not run"; echo "ROUTE-ONE-DONE $K"; exit 5; }
python3 - "$W" <<'PY'
import json, sys, os as _os, re
sys.path.insert(0, _os.path.abspath(_os.path.join(_os.getcwd(), "..", "tools"))); sys.path.insert(0, _os.path.abspath(_os.path.join(_os.getcwd(), "tools")))
# The one hard set scores the attempt, and its absence is a failure. It used to fall back to a six-type tuple with no message,
# which is the drift of report 1's C1 living in the file that decides which attempt route_parallel.sh picks; and the tool's own
# rule, written for pairsearch.py the same day, is that a fallback must not be a regression.
import hardset
d = json.load(open(sys.argv[1] + "/drc.json"))
hard = hardset.counts(d)["hard"]; unr = len(d.get("unconnected_items", []))
ses = [f for f in _os.listdir(sys.argv[1]) if f.endswith(".ses")]
vias = len(re.findall(r"^\s*\(via ", open(_os.path.join(sys.argv[1], ses[0])).read(), re.M)) if ses else 9999
open(sys.argv[1] + "/score.txt", "w").write("%d %d %d\n" % (hard, unr, vias)); print("score: hard %d unrouted %d vias %d" % (hard, unr, vias))
PY
SC=$?; [ "$SC" -eq 0 ] || { echo "attempt $K: the score was not written (exit $SC)"; rm -f "$W/score.txt"; echo "ROUTE-ONE-DONE $K"; exit 6; }
echo "ROUTE-ONE-DONE $K"
