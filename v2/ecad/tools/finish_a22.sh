#!/usr/bin/env bash
# A22 (MESHSAT-830, 7 Sep 2026), from finish_a21.sh: wait for route_parallel.sh (PARALLEL-DONE in the log), stub router, dangling clean-up, pack-node and boost bars, legend pass, finish.
# Usage: finish_a22.sh <ecad dir> <parallel log, relative to pcb-a-power>
set -uo pipefail   # 8 Sep 2026 (MESHSAT-862): no set line before; the finish decides whether a board is clean
cd "$1/pcb-a-power"; N=pcb-a-power; LOG="$2"
rm -f out/a22-clean.txt out/par-score.txt out/contracts.log   # a stale clean flag must never finish a board (register class 6)
# A wait with a deadline (10 September 2026, report 1 item 4). If the producer crashes, or the wrong log is named, or the
# marker is never written, this job used to be immortal and nothing said so. FINISH_WAIT_S bounds it, default six hours,
# which is longer than any route this project has run; it refuses rather than carrying on with whatever is on disk.
W=0; while ! grep -q PARALLEL-DONE "$LOG" 2>/dev/null; do sleep 30; W=$((W + 30));
  if [ "$W" -ge "${FINISH_WAIT_S:-21600}" ]; then echo "finish: no PARALLEL-DONE in $LOG after ${W} s; refusing"; exit 1; fi
done
grep -E 'attempt|WINNER' "$LOG"
../tools/drc.sh $N.kicad_pcb out/$N-drc.json
cp $N.kicad_pcb out/$N-par-routed.kicad_pcb
# 7 Sep 2026: the router's knot (two nets' tracks tangled at one spot, 20 to 25 shorts) is removed before anything else; the stub router closes the nets it opens
python3 ../tools/unknot.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep unknot && python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup; ../tools/drc.sh $N.kicad_pcb out/$N-drc.json
# A21 (5 Sep 2026): a few open connections get one continuation pass of the router on the routed board before the stub router (cont_route.sh keeps the board only if it improves)
UN=$(python3 -c "import json; print(len(json.load(open('out/$N-drc.json')).get('unconnected_items', [])))") || { echo "no readable DRC JSON after the unknot step"; echo open > out/a22-clean.txt; echo FINISH-A22-DONE; exit 1; }
if [ "$UN" -gt 0 ] && [ "$UN" -le 6 ]; then ../tools/cont_route.sh "$PWD" $N 80 900 2>&1 | grep -E 'cont:'; ../tools/drc.sh $N.kicad_pcb out/$N-drc.json; fi
STUB_LAYERS=F.Cu,In2.Cu,In3.Cu,B.Cu STUB_GRID=0.1 STUB_WIN_SCALE=2.5 STUB_MAXN=16000000 nice -n 10 python3 ../tools/stub_router.py $N.kicad_pcb out/$N-drc.json > out/$N-stub.log 2>&1 || { echo "stub router CRASHED, exit $? (out/$N-stub.log)"; echo open > out/a22-clean.txt; echo FINISH-A22-DONE; exit 1; }; grep -E 'closed|FAILED|stub_router|Error' out/$N-stub.log | head -12
../tools/drc.sh $N.kicad_pcb out/$N-drc.json
python3 ../tools/hardset.py out/$N-drc.json post --score out/par-score.txt --label 'after stub router' | grep -v '^hardset:'   # 8 Sep 2026 (MESHSAT-862): tools/hardset.py is the one hard set
[ -s out/par-score.txt ] || { echo "no DRC score after the stub router (hardset refused)"; echo open > out/a22-clean.txt; echo FINISH-A22-DONE; exit 1; }; read H < out/par-score.txt; if [ "$H" -ne 0 ]; then python3 ../tools/stub_accept.py out/$N-par-routed.kicad_pcb $N.kicad_pcb out/$N-drc.json 2>&1 | grep stub_accept; ../tools/drc.sh $N.kicad_pcb out/$N-drc.json; H=$(python3 ../tools/hardset.py out/$N-drc.json post --score out/par-score.txt --label 'after stub_accept' >/dev/null; cat out/par-score.txt); echo "after stub_accept: hard $H"; if [ "$H" -ne 0 ]; then echo 'stub router hurt: reverting'; cp out/$N-par-routed.kicad_pcb $N.kicad_pcb; fi; fi
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup
bash ../tools/quality_pass.sh "$PWD" $N > out/$N-quality-run.log 2>&1 || echo "quality_pass.sh exited $? (out/$N-quality-run.log)"; grep -E "quality:|Traceback" out/$N-quality-run.log | tail -5   # Stage 3 of the quality programme (6 Sep 2026): straighten and via passes on a copy, DRC-gated, reverted when anything rises
# Owner ruling 5 Sep 2026 17:00 (appendix 32.40): a differential pair over 1 mm of intra-pair mismatch blocks the finish; pair_match.sh meanders the short
# legs itself, and when it still fails the session audits out/audit/*.png (pair_audit.py), traces the cause and iterates. No human look.
../tools/pair_match.sh "$PWD" $N check_pcb_a.py > out/pair-match.log 2>&1; PM=$?; grep -E "pair_match|WARN|PASS|meander" out/pair-match.log | cut -c1-140   # 8 Sep 2026: the status is pair_match.sh's own, not cut's (register class 1.3: the gate never fired before)
if [ "$PM" -ne 0 ]; then
  mkdir -p out/audit; for pr in USB_D8 USB_E6 USB_WALL; do python3 ../tools/pair_audit.py $N.kicad_pcb $pr out/audit/$pr.png 2>&1 | grep pair_audit; done
  echo 'A22 PAIRS NOT MATCHED, not finishing (audit images in out/audit)'; echo open > out/a22-clean.txt; echo FINISH-A22-DONE; exit 1
fi
python3 ../tools/silk_fix_all.py $N.kicad_pcb a 2>&1 | grep -vE 'Debug|leak' | tail -2
# A22: refill, then the board gate on the routed board (node and rail widths); an open or a FAIL stops the finish
python3 - "$N" <<'PYX' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b); print('zones refilled before the routed-board gate')
PYX
python3 ../tools/check_pcb_a.py $N.kicad_pcb > out/gate-$N.log 2>&1; GATE=$?; grep -E 'FAIL|band|stitch|routed at|RESULT|^verdict:' out/gate-$N.log | tail -12   # 11 Sep 2026 (MESHSAT-862, stage 0a): one run, and the exit code is the verdict. This gate used to run twice, the second time only to grep a string out of its stdout.
../tools/drc.sh $N.kicad_pcb out/$N-drc.json
python3 ../tools/hardset.py out/$N-drc.json post --flag out/a22-clean.txt --label 'routed-board gate' | sed 's/^hardset:/routed-board DRC:/'
[ "$GATE" -eq 0 ] || { echo "A22 GATE $(python3 ../tools/verdict.py read out/check_pcb_a.verdict.json 2>&1 | tail -1) on the routed board"; echo open > out/a22-clean.txt; }
# 8 Sep 2026 (MESHSAT-862 Stage C): the electrical verdicts before the clean flag: DC drop and current density of the intent rails, the impedance of the pair classes
python3 ../tools/dc_drop.py $N.kicad_pcb --json out/$N-dc_drop.json > out/$N-dc_drop.log 2>&1; DC=$?; grep -E 'dc_drop' out/$N-dc_drop.log | tail -14; [ "$DC" -eq 0 ] || { echo 'A22 DC DROP MISSED or unresolved (out/$N-dc_drop.log)'; echo open > out/a22-clean.txt; }
python3 ../tools/stackup_write.py $N.kicad_pcb 2>&1 | tail -1   # the routed board carries the stack for the read-back (8 Sep 2026)
python3 ../tools/impedance_check.py $N.kicad_pcb --json out/$N-impedance.json > out/$N-impedance.log 2>&1; IM=$?; grep -E 'impedance' out/$N-impedance.log | tail -14; [ "$IM" -eq 0 ] || { echo 'A22 IMPEDANCE MISSED (out/$N-impedance.log; openEMS on the missed pairs)'; echo open > out/a22-clean.txt; }
# 8 Sep 2026 (MESHSAT-862): the cross-board contracts are part of every finish (they were called by no chain before)
python3 ../tools/check_contracts.py .. > out/contracts.log 2>&1; grep -E 'FAIL|MISSING' out/contracts.log | head -12; if grep -q 'ALL CONTRACTS PASS' out/contracts.log; then echo 'contracts: ALL PASS'; else echo 'contracts: FAIL (out/contracts.log)'; echo open > out/a22-clean.txt; fi
CLEAN=$(cat out/a22-clean.txt); if [ "$CLEAN" != clean ]; then echo 'A22 NOT CLEAN, not finishing'; echo FINISH-A22-DONE; exit 1; fi
cd ..; ./tools/finish_board.sh pcb-a-power pcb-a-power - meshsat-pcb-a-revA-A22 2>&1 | tail -16
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "A22: finish_board REFUSED the deliverable (verify_deliverable or an export step failed)"; echo FINISH-A22-DONE; exit 1; }   # 8 Sep 2026: a pipeline's status is tail's, so a refused deliverable used to be reported finished
echo FINISH-A22-DONE
