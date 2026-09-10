#!/usr/bin/env bash
# Length matching as a hard gate (owner ruling 5 Sep 2026 17:00, appendix 32.40): read the pair report of the board's check, meander every short
# leg by its mismatch, refill, keep the board only if the DRC hard count stays 0, repeat up to three times; exit 1 when a pair is still over 1 mm.
# Usage: pair_match.sh <project dir> <name> <check script>   (e.g. pair_match.sh /root/.../pcb-b-compute pcb-b-compute check_pcb_b.py)
set -uo pipefail; cd "$1"; N="$2"; CHECK="$3"; mkdir -p out
report() { python3 ../tools/$CHECK $N.kicad_pcb 2>/dev/null | grep -E "pair length"; }
# The one hard set decides here too (10 September 2026, both round-two red teams C1); this counted six types while the finish
# refused on fifteen, and it is what says whether a meander hurt. A DRC that does not run is a refusal, not a zero.
hard() {   # board, report -> hard + unrouted
  ../tools/drc.sh "$1" "$2" || { echo 999999; return; }
  local c; c=$(mktemp)
  python3 ../tools/hardset.py "$2" post --counts "$c" >/dev/null || { rm -f "$c"; echo 999999; return; }
  awk '{print $1 + $2}' "$c"; rm -f "$c"
}
for round in 1 2 3; do
  warn=$(report | grep "^WARN" || true); [ -z "$warn" ] && { echo "pair_match: every pair within 1 mm (round $round)"; report | cut -c1-120; exit 0; }
  echo "$warn" | cut -c1-120
  cp $N.kicad_pcb out/$N-pair-round$round.kicad_pcb; H0=$(hard $N.kicad_pcb out/$N-pair-drc0.json)
  echo "$warn" | while read -r line; do
    pair=$(echo "$line" | sed -E 's/^WARN ([A-Za-z0-9_]+) pair length.*/\1/'); lp=$(echo "$line" | sed -E 's/.*length P ([0-9.]+) mm.*/\1/'); ln=$(echo "$line" | sed -E 's/.*, N ([0-9.]+) mm.*/\1/')
    short=$(python3 -c "print('${pair}_N' if $ln < $lp else '${pair}_P')"); extra=$(python3 -c "print(round(abs($lp - $ln), 2))")
    python3 ../tools/meander.py $N.kicad_pcb "$short" "$extra" 2>&1 | grep meander | cut -c1-160
  done
  python3 - "$N" <<'PYY' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b)
PYY
  H1=$(hard $N.kicad_pcb out/$N-pair-drc1.json); echo "pair_match: round $round, DRC hard+open before $H0 after $H1"
  if [ "$H1" -gt "$H0" ]; then echo "pair_match: the meanders hurt the board, round $round restored"; cp out/$N-pair-round$round.kicad_pcb $N.kicad_pcb; fi
done
warn=$(report | grep "^WARN" || true); [ -z "$warn" ] && { echo "pair_match: every pair within 1 mm"; exit 0; }
echo "pair_match: STILL OVER 1 mm after 3 rounds:"; echo "$warn" | cut -c1-120; exit 1
