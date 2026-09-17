#!/usr/bin/env bash
# Length matching as a hard gate (owner ruling 5 Sep 2026 17:00, appendix 32.40): read the pair report of the board's check, meander every short
# leg by its mismatch, refill, keep the board only if the DRC hard count stays 0, repeat up to three times; exit 1 when a pair is still over 1 mm.
# Usage: pair_match.sh <project dir> <name> <check script>   (e.g. pair_match.sh /root/.../pcb-b-compute pcb-b-compute check_pcb_b.py)
set -uo pipefail; cd "$1"; N="$2"; CHECK="$3"; mkdir -p out
report() { python3 ../tools/$CHECK $N.kicad_pcb 2>/dev/null | grep -E "pair length"; }
# The one hard set decides here too (10 September 2026, both round-two red teams C1); this counted six types while the finish
# refused on fifteen, and it is what says whether a meander hurt. A DRC that does not run is a refusal, not a zero.
# The same seam as cont_route.sh's score(): this function's stdout is read as ONE number, and drc.sh's cost
# line of 15 September was landing in it (16 September 2026).
hard() {   # board, report -> hard + unrouted
  ../tools/drc.sh "$1" "$2" >&2 || { echo 999999; return; }
  local c; c=$(mktemp)
  python3 ../tools/hardset.py "$2" post --counts "$c" --label "pair match trial" >/dev/null || { rm -f "$c"; echo 999999; return; }
  awk '{print $1 + $2}' "$c"; rm -f "$c"
}
# WHAT IS WORTH MEANDERING IS NOT ONLY WHAT FAILS (17 September 2026). The gate refuses a pair over this
# project's 1.00 mm, which is owner decision 36; the board check already PRINTS the number the interface's own
# host asks for beside each pair, because rule PAIR-001 asks for the citation. Board A's three pairs read 0.29,
# 0.12 and 0.01 mm against a compute module that asks for 0.15, so one of them passes the gate and misses the
# part's own budget by 0.14 mm of copper. Meandering to the TIGHTER number costs a trombone and is neutral to
# the ruling: if the interface's number is ruled, board A already meets it and needs no rework; if this
# project's is ruled, a tighter match is not worse. The REFUSAL is unchanged and still the 1.00 mm, because
# making the gate stricter would decide the owner's question for him.
actionable() {
  report | python3 -c '
import sys, re
for ln in sys.stdin:
    m = re.search(r"mismatch ([0-9.]+) mm", ln); a = re.search(r"asks for ([0-9.]+) mm", ln)
    if not m: continue
    over_gate = ln.startswith("WARN")
    over_part = bool(a) and float(m.group(1)) > float(a.group(1)) + 1e-9
    if over_gate or over_part: sys.stdout.write(ln)
'
}
for round in 1 2 3; do
  warn=$(actionable || true); [ -z "$warn" ] && { echo "pair_match: every pair within 1 mm and within its own interface's budget (round $round)"; report | cut -c1-120; exit 0; }
  echo "$warn" | cut -c1-120
  cp $N.kicad_pcb out/$N-pair-round$round.kicad_pcb; H0=$(hard $N.kicad_pcb out/$N-pair-drc0.json)
  echo "$warn" | while read -r line; do
    pair=$(echo "$line" | sed -E 's/^(WARN|PASS|FAIL)? *([A-Za-z0-9_]+) pair length.*/\2/'); lp=$(echo "$line" | sed -E 's/.*length P ([0-9.]+) mm.*/\1/'); ln=$(echo "$line" | sed -E 's/.*, N ([0-9.]+) mm.*/\1/')
    short=$(python3 -c "print('${pair}_N' if $ln < $lp else '${pair}_P')"); extra=$(python3 -c "print(round(abs($lp - $ln), 2))")
    # MEANDER_LOCKED: a pair the pre-router laid end to end has no unlocked copper, and this gate then
    # refuses a board nothing can fix. The DRC check below is the guard: a round that raises the hard
    # count is reverted whole (14 September 2026, A27's USB_D8 at 1.77 mm and USB_WALL at 1.50).
    MEANDER_LOCKED=1 python3 ../tools/meander.py $N.kicad_pcb "$short" "$extra" 2>&1 | grep meander | cut -c1-160
  done
  python3 - "$N" <<'PYY' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b)
PYY
  H1=$(hard $N.kicad_pcb out/$N-pair-drc1.json); echo "pair_match: round $round, DRC hard+open before $H0 after $H1"
  if [ "$H1" -gt "$H0" ]; then echo "pair_match: the meanders hurt the board, round $round restored"; cp out/$N-pair-round$round.kicad_pcb $N.kicad_pcb; fi
done
# THE REFUSAL IS THE GATE'S NUMBER, NOT THE INTERFACE'S: a pair inside 1.00 mm and outside its part's budget
# is REPORTED here and does not stop the finish, because which of the two decides is owner decision 36.
warn=$(report | grep "^WARN" || true)
near=$(actionable | grep -v "^WARN" || true)
[ -n "$near" ] && { echo "pair_match: still outside the interface's own budget (reported, not refused):"; echo "$near" | cut -c1-140; }
[ -z "$warn" ] && { echo "pair_match: every pair within 1 mm"; exit 0; }
echo "pair_match: STILL OVER 1 mm after 3 rounds:"; echo "$warn" | cut -c1-120; exit 1
