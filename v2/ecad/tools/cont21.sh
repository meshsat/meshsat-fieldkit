#!/usr/bin/env bash
# watched continuation with Freerouting 2.1 (headless): stop when the log shows 0 unrouted and a session is written, or on plateau
set -uo pipefail
cd "$1"; N=pcb-b-compute
cp $N.kicad_pcb out/$N-before-cont21.kicad_pcb
python3 - "$N.kicad_pcb" "out/$N-c21.dsn" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
for z in list(b.Zones()):
    if not z.GetIsRuleArea(): b.Remove(z)
tmp = sys.argv[2].replace(".dsn", "-noplanes.kicad_pcb"); pcbnew.SaveBoard(tmp, b)
print("DSN:", pcbnew.ExportSpecctraDSN(pcbnew.LoadBoard(tmp), sys.argv[2]))
PY
rm -f out/$N-c21.ses
( nice -n 10 java -Djava.awt.headless=true -jar $HOME/bin/freerouting-2.1.0.jar -de out/$N-c21.dsn -do out/$N-c21.ses -mt 4 -oit 1 > out/$N-c21.log 2>&1 ) &
RP=$!
last=""; same=0
for i in $(seq 1 60); do
  sleep 10
  [ -f out/$N-c21.ses ] && { echo "session written"; break; }
  kill -0 $RP 2>/dev/null || { echo "router exited"; break; }
  cur=$(grep -oE '\(([0-9]+) unrouted\)' out/$N-c21.log | tail -1)
  if [ "$cur" = "$last" ]; then same=$((same+1)); else same=0; fi; last="$cur"
  [ $((i % 6)) -eq 0 ] && echo "t=$((i*10))s $cur"
  if [ $same -ge 18 ] && [ -n "$cur" ]; then echo "plateau at $cur: killing"; pkill -9 -f '^java .*freerouting'; break; fi
done
wait $RP 2>/dev/null
if [ -f out/$N-c21.ses ]; then
python3 - "$N.kicad_pcb" "out/$N-c21.ses" <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); print("SES import:", pcbnew.ImportSpecctraSES(b, sys.argv[2])); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b)
PY
fi
../tools/build_pcb.sh . $N 2>&1 | grep -E '^DRC'
grep -E '^\[' out/$N-drc.rpt | sed 's/:.*//' | sort | uniq -c | sort -rn | head -6
echo CONT21-DONE
