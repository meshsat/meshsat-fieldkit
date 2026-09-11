#!/usr/bin/env bash
# P1 (7 Sep 2026, from finish_d8.sh): wait for route_parallel.sh (PARALLEL-DONE in the log), stub router, dangling clean-up, legend pass, refill, the board gate, finish. The seals and lenses belong to the face plate (v2/cad/face_plate.py); no tenting rule: the backer is not the weather face.
# Usage: finish_p1.sh <ecad dir> <parallel log, relative to pcb-p-pack>
set -uo pipefail   # 8 Sep 2026 (MESHSAT-862): no set line before; the finish decides whether a board is clean
cd "$1/pcb-p-pack-p2"; N=pcb-p-pack; LOG="$2"
rm -f out/p2-clean.txt out/par-score.txt out/contracts.log   # a stale clean flag must never finish a board (register class 6)
# A wait with a deadline (10 September 2026, report 1 item 4). If the producer crashes, or the wrong log is named, or the
# marker is never written, this job used to be immortal and nothing said so. FINISH_WAIT_S bounds it, default six hours,
# which is longer than any route this project has run; it refuses rather than carrying on with whatever is on disk.
W=0; while ! grep -q PARALLEL-DONE "$LOG" 2>/dev/null; do sleep 30; W=$((W + 30));
  if [ "$W" -ge "${FINISH_WAIT_S:-21600}" ]; then echo "finish: no PARALLEL-DONE in $LOG after ${W} s; refusing"; exit 1; fi
done
grep -E 'attempt|WINNER' "$LOG"
../tools/drc.sh $N.kicad_pcb out/$N-drc.json
cp $N.kicad_pcb out/$N-par-routed.kicad_pcb
STUB_LAYERS=F.Cu,B.Cu STUB_GRID=0.1 nice -n 10 python3 ../tools/stub_router.py $N.kicad_pcb out/$N-drc.json > out/$N-stub.log 2>&1 || { echo "stub router CRASHED, exit $? (out/$N-stub.log)"; echo open > out/p2-clean.txt; echo FINISH-P2-DONE; exit 1; }; grep -E 'closed|FAILED|stub_router|Error' out/$N-stub.log | head -12
../tools/drc.sh $N.kicad_pcb out/$N-drc.json
python3 ../tools/hardset.py out/$N-drc.json post --score out/par-score.txt --label 'after stub router' | grep -v '^hardset:'   # 8 Sep 2026 (MESHSAT-862): tools/hardset.py is the one hard set
[ -s out/par-score.txt ] || { echo "no DRC score after the stub router (hardset refused)"; echo open > out/p2-clean.txt; echo FINISH-P2-DONE; exit 1; }; read H < out/par-score.txt; if [ "$H" -ne 0 ]; then python3 ../tools/stub_accept.py out/$N-par-routed.kicad_pcb $N.kicad_pcb out/$N-drc.json 2>&1 | grep stub_accept; ../tools/drc.sh $N.kicad_pcb out/$N-drc.json; H=$(python3 ../tools/hardset.py out/$N-drc.json post --score out/par-score.txt --label 'after stub_accept' >/dev/null; cat out/par-score.txt); echo "after stub_accept: hard $H"; if [ "$H" -ne 0 ]; then echo 'stub router hurt: reverting'; cp out/$N-par-routed.kicad_pcb $N.kicad_pcb; fi; fi
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup
# 8 Sep 2026: a fine-pitch pad its own plane cannot reach after the route (the tracks cut the pour off) gets a via in the pad, the closure this board family already ships
../tools/drc.sh $N.kicad_pcb out/$N-drc.json
python3 ../tools/zone_pad_via.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -v "^Debug" | tail -6

# 9 Sep 2026 (D10, appendix 32.83): pour_stitch.py was written on 8 Sep for D9's 57-island front pour and wired into NO finish;
# D10 ended its route with the B.Cu ground pour and the In1 plane reported open because no via of the net reached the island.
python3 ../tools/pour_stitch.py $N.kicad_pcb --nets=GND 2>&1 | grep -vE "^Debug|leak" | tail -4; ../tools/drc.sh $N.kicad_pcb out/$N-drc.json
# The router's knot: two nets tangled at one spot, the hard pattern hardset names KNOT. Three of the six finishes ran it and
# three did not (10 September 2026, report 2 H3); it removes nothing where there is no knot.
../tools/drc.sh $N.kicad_pcb out/$N-drc.json
python3 ../tools/unknot.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep unknot && python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup; ../tools/drc.sh $N.kicad_pcb out/$N-drc.json
bash ../tools/quality_pass.sh "$PWD" $N > out/$N-quality-run.log 2>&1 || echo "quality_pass.sh exited $? (out/$N-quality-run.log)"; grep -E "quality:|Traceback" out/$N-quality-run.log | tail -5   # Stage 3 of the quality programme (6 Sep 2026): straighten and via passes on a copy, DRC-gated, reverted when anything rises
python3 ../tools/silk_fix_all.py $N.kicad_pcb p 2>&1 | grep -vE 'Debug|leak' | tail -2
python3 - "$N" <<'PYX' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b); print('zones refilled before the board gate')
PYX
python3 ../tools/check_pcb_p.py $N.kicad_pcb > out/gate-$N.log 2>&1; GATE=$?; grep -E 'FAIL|RESULT|^verdict:' out/gate-$N.log   # 11 Sep 2026 (MESHSAT-862, stage 0a): one run, and the exit code is the verdict. This gate used to run twice, the second time only to grep a string out of its stdout.
../tools/drc.sh $N.kicad_pcb out/$N-drc.json
python3 ../tools/hardset.py out/$N-drc.json post --flag out/p2-clean.txt --label 'routed-board gate' | sed 's/^hardset:/routed-board DRC:/'
python3 -c "import json; d=json.load(open('out/$N-drc.json')); [print('  OPEN', ' ~ '.join('%s@(%.1f,%.1f)' % (i['description'][:50], i['pos']['x'], i['pos']['y']) for i in u['items'])) for u in d.get('unconnected_items', [])[:6]]"
[ "$GATE" -eq 0 ] || { echo "P2 GATE $(python3 ../tools/verdict.py read out/check_pcb_p.verdict.json 2>&1 | tail -1) on the routed board"; echo open > out/p2-clean.txt; }
# 8 Sep 2026 (MESHSAT-862 Stage C): the electrical verdicts before the clean flag: DC drop and current density of the intent rails, the impedance of the pair classes
python3 ../tools/dc_drop.py $N.kicad_pcb --json out/$N-dc_drop.json > out/$N-dc_drop.log 2>&1; DC=$?; grep -E 'dc_drop' out/$N-dc_drop.log | tail -14; [ "$DC" -eq 0 ] || { echo 'P2 DC DROP MISSED or unresolved (out/$N-dc_drop.log)'; echo open > out/p2-clean.txt; }
python3 ../tools/stackup_write.py $N.kicad_pcb 2>&1 | tail -1   # the routed board carries the stack for the read-back (8 Sep 2026)
python3 ../tools/impedance_check.py $N.kicad_pcb --json out/$N-impedance.json > out/$N-impedance.log 2>&1; IM=$?; grep -E 'impedance' out/$N-impedance.log | tail -14; [ "$IM" -eq 0 ] || { echo 'P2 IMPEDANCE MISSED (out/$N-impedance.log; openEMS on the missed pairs)'; echo open > out/p2-clean.txt; }
# 8 Sep 2026 (MESHSAT-862): the cross-board contracts are part of every finish (they were called by no chain before)
python3 ../tools/check_contracts.py .. > out/contracts.log 2>&1; grep -E 'FAIL|MISSING' out/contracts.log | head -12; if grep -q 'ALL CONTRACTS PASS' out/contracts.log; then echo 'contracts: ALL PASS'; else echo 'contracts: FAIL (out/contracts.log)'; echo open > out/p2-clean.txt; fi
CLEAN=$(cat out/p2-clean.txt); if [ "$CLEAN" != clean ]; then echo 'P2 NOT CLEAN, not finishing'; echo FINISH-P2-DONE; exit 1; fi
cd ..; ./tools/finish_board.sh pcb-p-pack-p2 pcb-p-pack - meshsat-pcb-p-revA-P3 2>&1 | tail -16
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "P2: finish_board REFUSED the deliverable (verify_deliverable or an export step failed)"; echo FINISH-P2-DONE; exit 1; }   # 8 Sep 2026: a pipeline's status is tail's, so a refused deliverable used to be reported finished
echo FINISH-P2-DONE
