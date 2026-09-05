#!/usr/bin/env bash
# quality_pass: run the post-route quality passes on a COPY of a routed board, refill, one kicad-cli DRC, and keep the result only if hard
# violations and opens did not rise (Freerouting quality programme, Stage 3). On a failure the batch is bisected once (straighten without
# shortcuts, then via_merge alone); if still worse, the board is left untouched and "quality: reverted" is printed. Prints before and after
# vias, length and segments with denominators. Usage: quality_pass.sh <project dir> <name>   (writes out/<name>-quality.log)
set -uo pipefail
cd "$1"; N="$2"; T=$(cd "$(dirname "$0")" && pwd); W=out/quality; rm -rf "$W"; mkdir -p "$W"; LOG=out/$N-quality.log; : > "$LOG"
drc_counts() {   # file -> "hard unrouted"
  python3 - "$1" <<'PY'
import json, sys, collections
d = json.load(open(sys.argv[1])); c = collections.Counter(v["type"] for v in d["violations"])
print(sum(c[t] for t in ("clearance", "shorting_items", "tracks_crossing", "hole_clearance", "hole_to_hole", "copper_edge_clearance")), len(d.get("unconnected_items", [])))
PY
}
measure() {   # board -> "vias length tracks"
  python3 - "$1" <<'PY' 2>/dev/null | grep -v "Debug\|assert"
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); mm = pcbnew.ToMM
tr = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]; print(sum(1 for t in b.GetTracks() if t.GetClass() == "PCB_VIA"), round(sum(mm(t.GetLength()) for t in tr)), len(tr))
PY
}
kicad-cli pcb drc --severity-all --format json -o "$W/before-drc.json" "$N.kicad_pcb" >/dev/null 2>&1 || { echo "quality: DRC of the input failed, nothing done" | tee -a "$LOG"; exit 0; }
read H0 U0 <<< "$(drc_counts "$W/before-drc.json")"; read V0 L0 S0 <<< "$(measure "$N.kicad_pcb")"
echo "quality: before hard $H0 unrouted $U0 vias $V0 length $L0 mm segments $S0" | tee -a "$LOG"
try() {   # label, required marker(s) regex, commands on $W/cand.kicad_pcb -> 0 if accepted; a pass that leaves no summary line is a failed pass, never an accept
  local label=$1 marker=$2; shift 2
  cp "$N.kicad_pcb" "$W/cand.kicad_pcb"; cp "$N.kicad_pro" "$W/cand.kicad_pro" 2>/dev/null; : > "$W/try.log"
  { "$@"; } > "$W/try.log" 2>&1; cat "$W/try.log" >> "$LOG"
  if grep -q "Traceback" "$W/try.log" || ! grep -q -E "$marker" "$W/try.log"; then echo "quality: $label FAILED (no summary line or a traceback; see $LOG)" | tee -a "$LOG"; return 1; fi
  kicad-cli pcb drc --severity-all --format json -o "$W/cand-drc.json" "$W/cand.kicad_pcb" >/dev/null 2>&1 || return 1
  read H1 U1 <<< "$(drc_counts "$W/cand-drc.json")"; read V1 L1 S1 <<< "$(measure "$W/cand.kicad_pcb")"
  echo "quality: $label -> hard $H1 unrouted $U1 vias $V1 length $L1 mm segments $S1" | tee -a "$LOG"
  if [ "$H1" -le "$H0" ] && [ "$U1" -le "$U0" ] && [ "$V1" -le "$V0" ] && [ "$L1" -le "$((L0 + L0 / 200 + 1))" ]; then cp "$W/cand.kicad_pcb" "$N.kicad_pcb"; return 0; fi
  return 1
}
both() { python3 "$T/straighten.py" "$W/cand.kicad_pcb" && { [ -f "$T/via_merge.py" ] && python3 "$T/via_merge.py" "$W/cand.kicad_pcb" || echo "via_merge: absent"; }; }
if try "straighten+via_merge" "straighten:.*via_merge:|via_merge:.*straighten:|straighten:" both; then echo "quality: accepted (both passes)" | tee -a "$LOG"
elif try "straighten only, no shortcuts" "straighten:" python3 "$T/straighten.py" "$W/cand.kicad_pcb" --no-shortcut; then echo "quality: accepted (straighten without shortcuts)" | tee -a "$LOG"
elif [ -f "$T/via_merge.py" ] && try "via_merge only" "via_merge:" python3 "$T/via_merge.py" "$W/cand.kicad_pcb"; then echo "quality: accepted (via_merge only)" | tee -a "$LOG"
else echo "quality: reverted (every batch raised hard, opens, vias or length)" | tee -a "$LOG"; fi
read V2 L2 S2 <<< "$(measure "$N.kicad_pcb")"; echo "quality: after vias $V2 of $V0, length $L2 of $L0 mm, segments $S2 of $S0" | tee -a "$LOG"; echo QUALITY-DONE
