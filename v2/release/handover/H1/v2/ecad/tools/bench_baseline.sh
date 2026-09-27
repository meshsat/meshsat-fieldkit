#!/usr/bin/env bash
# bench_baseline: measure the released boards into the quality baseline (Freerouting quality programme, Stage 1).
# Usage: bench_baseline.sh [repo dir]   -> tools/routeflow/bench/baseline.json ; self-check against the counts of 5 Sep 2026 (within 1 percent)
set -uo pipefail
R=${1:-$(cd "$(dirname "$0")/../../.." && pwd)}; T=$R/v2/ecad/tools; OUT=$T/routeflow/bench; mkdir -p "$OUT"; TMP=$(mktemp -d)
declare -A BOARDS=( [A21]=meshsat-pcb-a-revA-A21 [B14]=meshsat-pcb-b-revA-B14 [C5]=meshsat-pcb-c-revA-C5 [D7]=meshsat-pcb-d-revA-D7 [E4]=meshsat-pcb-e-revA-E4 [E5]=meshsat-pcb-e5-revA-E5 [B15]=meshsat-pcb-b-revA-B15 [C6]=meshsat-pcb-c-revA-C6 )
declare -A KNOWN=( [A21]="404 2051 10693" [B14]="704 4046 24675" [C5]="330 2015 21436" [D7]="148 958 3618" [E4]="142 773 3772" )   # vias tracks length_mm, measured 5 Sep 2026
echo "{" > "$TMP/baseline.json"; first=1; fails=0
for key in A21 B14 C5 D7 E4 E5 B15 C6; do
  d=$R/v2/release/revA/boards/${BOARDS[$key]}; f=$(ls "$d"/*.kicad_pcb 2>/dev/null | head -1); [ -z "$f" ] && { echo "skip $key: no deliverable board"; continue; }
  j=$(ls "$d"/*drc*.json 2>/dev/null | head -1)
  if [ -z "$j" ]; then j=$TMP/$key-drc.json; kicad-cli pcb drc --severity-all --format json -o "$j" "$f" >/dev/null 2>&1 || { echo "FAIL $key: DRC did not run"; fails=$((fails + 1)); continue; }; fi
  python3 "$T/route_metrics.py" "$f" "$j" --json "$TMP/$key.json" --tag "$key" 2>&1 | grep -v "Debug\|assert" || { echo "FAIL $key: metrics"; fails=$((fails + 1)); continue; }
  if [ -n "${KNOWN[$key]:-}" ]; then
    read kv kt kl <<< "${KNOWN[$key]}"
    python3 - "$TMP/$key.json" "$kv" "$kt" "$kl" <<'PY' || fails=$((fails + 1))
import json, sys
m = json.load(open(sys.argv[1])); kv, kt, kl = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
def ok(a, b): return abs(a - b) <= 0.01 * max(1, b)
good = ok(m["vias"], kv) and ok(m["tracks"], kt) and ok(m["length_mm"], kl)
print("  self-check %s: vias %d/%d tracks %d/%d length %.0f/%.0f -> %s" % (m["tag"], m["vias"], kv, m["tracks"], kt, m["length_mm"], kl, "OK" if good else "MISMATCH")); sys.exit(0 if good else 1)
PY
  fi
  [ $first = 1 ] || echo "," >> "$TMP/baseline.json"; first=0
  printf '"%s": ' "$key" >> "$TMP/baseline.json"; cat "$TMP/$key.json" >> "$TMP/baseline.json"
done
echo "}" >> "$TMP/baseline.json"
python3 -c "import json,sys; d=json.load(open('$TMP/baseline.json')); print('baseline boards:', ', '.join(d))" || { echo "FAIL: baseline JSON invalid"; exit 2; }
if [ $fails = 0 ]; then cp "$TMP/baseline.json" "$OUT/baseline.json"; echo "baseline written: $OUT/baseline.json"; else echo "baseline NOT written: $fails failures"; exit 1; fi
