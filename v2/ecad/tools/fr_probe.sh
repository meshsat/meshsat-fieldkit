#!/usr/bin/env bash
# fr_probe: the capability probe of the Freerouting quality programme (Stage 0, 6 Sep 2026). Runs the jar once per claimed knob on a small board
# (the released D7 stripped back to its locked pre-route copper), measures every result with route_metrics.py, and writes
# tools/routeflow/bench/capabilities.json: a knob is PROBED only when it changes a measured number or the jar rejects it. Refuses to write the
# file if any run produced no session. Usage (on the build VM, service group stopped): fr_probe.sh [repo dir] [jar]
set -uo pipefail
R=${1:-$(cd "$(dirname "$0")/../../.." && pwd)}; T=$R/v2/ecad/tools; JAR=${2:-$HOME/bin/freerouting-1.9.0.jar}; OUT=$T/routeflow/bench; mkdir -p "$OUT"
W=${FR_PROBE_DIR:-$HOME/fr_probe}
if [ "${3:-}" = "--assemble" ]; then cd "$W"; JAR=${2:-$HOME/bin/freerouting-1.9.0.jar}; ASSEMBLE_ONLY=1; else rm -rf "$W"; mkdir -p "$W"; cd "$W"; ASSEMBLE_ONLY=0; fi
SRC=$(ls "$R"/v2/release/revA/boards/meshsat-pcb-d-revA-D7/*.kicad_pcb | head -1); N=pcb-d-aprs
JAVA=$(java -version 2>&1 | head -1 | tr -d '"'); SHA=$(sha256sum "$JAR" | cut -c1-16)
if [ $ASSEMBLE_ONLY = 0 ]; then
cp "$(dirname "$SRC")/$N.kicad_pro" .; python3 "$T/strip_route.py" "$SRC" "$N.kicad_pcb" 2>&1 | grep -v "Debug\|assert"
python3 - "$N.kicad_pcb" "$N.dsn" <<'PY' 2>&1 | grep -v "Debug\|assert"
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
for z in list(b.Zones()):
    if not z.GetIsRuleArea(): b.Remove(z)
tmp = sys.argv[2].replace(".dsn", "-noplanes.kicad_pcb"); pcbnew.SaveBoard(tmp, b); print("DSN export:", pcbnew.ExportSpecctraDSN(pcbnew.LoadBoard(tmp), sys.argv[2]))
PY
# a Freerouting rules file with the autoroute settings block (the format the router itself writes): via costs x4 against the default 50
LAYERS=$(grep -o "(layer [A-Za-z0-9_.]*" "$N.dsn" | awk '{print $2}' | sort -u)
{ echo "(rules PCB $N"; echo "  (snap_angle fortyfive_degree)"; echo "  (autoroute_settings (fanout off) (autoroute on) (postroute on) (vias on) (via_costs 200) (plane_via_costs 5) (start_ripup_costs 100) (start_pass_no 1)";
  for L in $LAYERS; do echo "    (layer_rule $L (active on) (preferred_direction horizontal) (preferred_direction_trace_costs 1.0) (against_preferred_direction_trace_costs 2.5))"; done; echo "  )"; echo ")"; } > via200.rules
declare -A KNOBS=( [base]="" [oit_0.5]="-oit 0.5" [us_global]="-us global" [us_hybrid_1_1]="-us hybrid -hr 1:1" [is_sequential]="-is sequential" [is_random]="-is random" [inc_PWR]="-inc PWR" [im]="-im" [mp_10]="-mp 10" )
nosession=0
run_one() {   # name, extra args...
  local name=$1; shift; local d="$W/$name"; mkdir -p "$d"; cp "$N.kicad_pcb" "$N.kicad_pro" "$d/"
  local t0=$(date +%s); timeout 600 xvfb-run -a java -jar "$JAR" -de "$N.dsn" -do "$d/$N.ses" -mp ${MP:-40} -mt 1 -oit 2 -dct 0 "$@" > "$d/fr.log" 2>&1; local rc=$?; local t1=$(date +%s)
  local auto=$(grep -a -o "Auto-routing was completed in [0-9]* minute(s) [0-9.]* seconds" "$d/fr.log" | head -1); local opt=$(grep -a -o "optimization was completed in [0-9]* minute(s) [0-9.]* seconds" "$d/fr.log" | head -1)
  if [ ! -s "$d/$N.ses" ]; then echo "  $name: NO SESSION (exit $rc, $((t1 - t0)) s)"; nosession=$((nosession + 1)); echo "\"$name\": {\"session\": false, \"exit\": $rc, \"wall_s\": $((t1 - t0)), \"args\": \"$*\"}" >> "$d/row.json"; return; fi
  python3 - "$d/$N.kicad_pcb" "$d/$N.ses" <<'PY' 2>&1 | grep -v "Debug\|assert"
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); print("SES import:", pcbnew.ImportSpecctraSES(b, sys.argv[2])); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b)
PY
  kicad-cli pcb drc --severity-all --format json -o "$d/drc.json" "$d/$N.kicad_pcb" >/dev/null 2>&1
  python3 "$T/route_metrics.py" "$d/$N.kicad_pcb" "$d/drc.json" --json "$d/metrics.json" --tag "$name" --wall $((t1 - t0)) 2>&1 | grep -v "Debug\|assert"
  python3 - "$d/metrics.json" "$name" "$*" "$((t1 - t0))" "$auto" "$opt" <<'PY' > "$d/row.json"
import json, sys
m = json.load(open(sys.argv[1])); print(json.dumps({"session": True, "args": sys.argv[3], "wall_s": int(sys.argv[4]), "autoroute": sys.argv[5], "optimizer": sys.argv[6], "hard": m["hard"], "unrouted": m["unrouted"], "vias": m["vias"], "vias_router": m["vias_router"], "length_mm": m["length_mm"], "tracks": m["tracks"], "detour_median": m["detour_median"]}))
PY
}
for name in base oit_0.5 us_global us_hybrid_1_1 is_sequential is_random inc_PWR im; do run_one "$name" ${KNOBS[$name]}; done
MP=10 run_one mp_10
run_one rules_via200 -dr via200.rules
# checkpoint probe: kill the jar after 20 s with -im and see whether any session or checkpoint file exists
mkdir -p "$W/kill_im"; cp "$N.kicad_pcb" "$N.kicad_pro" "$W/kill_im/"; timeout 20 xvfb-run -a java -jar "$JAR" -de "$N.dsn" -do "$W/kill_im/$N.ses" -mp 200 -mt 1 -oit 0.01 -dct 0 -im > "$W/kill_im/fr.log" 2>&1; sleep 1
echo "\"kill_im\": {\"session_after_kill\": $([ -s "$W/kill_im/$N.ses" ] && echo true || echo false), \"files\": \"$(ls "$W/kill_im" | tr '\n' ' ')\"}" > "$W/kill_im/row.json"
fi
nosession=$(grep -l '"session": false' "$W"/*/row.json 2>/dev/null | wc -l)
python3 - "$W" "$(basename "$JAR")" "$SHA" "$JAVA" <<'PY'
import json, sys, os, glob, datetime
W, jar, sha, java = sys.argv[1:5]; runs = {}
for d in sorted(glob.glob(os.path.join(W, "*", "row.json"))):
    name = os.path.basename(os.path.dirname(d)); t = open(d).read().strip()
    if t.startswith('"'): t = "{" + t + "}"; runs.update(json.loads(t)); continue
    runs[name] = json.loads(t)
c = {"jar": jar, "jar_sha256_16": sha, "java": java, "board": "D7 stripped", "date": datetime.datetime.now().isoformat(timespec="seconds"), "runs": runs}
base = runs.get("base", {})
verdict = {}
for k, r in runs.items():
    if k in ("base", "kill_im"): continue
    if not r.get("session"): verdict[k] = "REJECTED_OR_NO_SESSION"; continue
    changed = any(r.get(f) != base.get(f) for f in ("vias", "length_mm", "tracks", "hard", "unrouted"))
    verdict[k] = "PROBED (changes the result)" if changed else "NO_EFFECT (identical to base)"
c["verdict"] = verdict; json.dump(c, open(os.path.join(W, "caps.json"), "w"), indent=1)
for k, v in verdict.items(): print("  %-16s %s  %s" % (k, v, {f: runs[k].get(f) for f in ("vias", "length_mm", "tracks", "wall_s")}))
print("  base:", {f: base.get(f) for f in ("vias", "length_mm", "tracks", "wall_s", "autoroute")}); print("  kill_im:", runs.get("kill_im"))
PY
if [ $nosession = 0 ]; then cp caps.json "$OUT/capabilities.json"; echo "capabilities written: $OUT/capabilities.json"; else echo "capabilities NOT written: $nosession runs without a session (the file stays in $W/caps.json for reading)"; fi
echo PROBE-DONE
