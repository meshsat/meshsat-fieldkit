#!/usr/bin/env bash
# C7 (5 Sep 2026): wait for route_parallel.sh (PARALLEL-DONE in the log), stub router, dangling clean-up, legend pass, refill, the board gate, finish. The seals and lenses belong to the face plate (v2/cad/face_plate.py); no tenting rule: the backer is not the weather face.
# Usage: finish_c7.sh <ecad dir> <parallel log, relative to pcb-c-display>
set -uo pipefail   # 8 Sep 2026 (MESHSAT-862): no set line before; the finish decides whether a board is clean
cd "$1/pcb-c-display-c8"; N=pcb-c-display; LOG="$2"
rm -f out/c8-clean.txt out/par-score.txt out/contracts.log   # a stale clean flag must never finish a board (register class 6)
while ! grep -q PARALLEL-DONE "$LOG" 2>/dev/null; do sleep 30; done
grep -E 'attempt|WINNER' "$LOG"
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
cp $N.kicad_pcb out/$N-par-routed.kicad_pcb
# 7 Sep 2026: the router's knot (two nets' tracks tangled at one spot, 20 to 25 shorts) is removed before anything else; the stub router closes the nets it opens
python3 ../tools/unknot.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep unknot && python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup
# 8 Sep 2026: a fine-pitch pad its own plane cannot reach after the route (the tracks cut the pour off) gets a via in the pad, the closure this board family already ships
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 ../tools/zone_pad_via.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -v "^Debug" | tail -6; kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
STUB_LAYERS=F.Cu,In2.Cu,B.Cu STUB_GRID=0.1 nice -n 10 python3 ../tools/stub_router.py $N.kicad_pcb out/$N-drc.json > out/$N-stub.log 2>&1 || { echo "stub router CRASHED, exit $? (out/$N-stub.log)"; echo open > out/c8-clean.txt; echo FINISH-C8-DONE; exit 1; }; grep -E 'closed|FAILED|stub_router|Error' out/$N-stub.log | head -12
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 ../tools/hardset.py out/$N-drc.json post --score out/par-score.txt --label 'after stub router' | grep -v '^hardset:'   # 8 Sep 2026 (MESHSAT-862): tools/hardset.py is the one hard set
[ -s out/par-score.txt ] || { echo "no DRC score after the stub router (hardset refused)"; echo open > out/c8-clean.txt; echo FINISH-C8-DONE; exit 1; }; read H < out/par-score.txt; if [ "$H" -ne 0 ]; then python3 ../tools/stub_accept.py out/$N-par-routed.kicad_pcb $N.kicad_pcb out/$N-drc.json 2>&1 | grep stub_accept; kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1; H=$(python3 ../tools/hardset.py out/$N-drc.json post --score out/par-score.txt >/dev/null; cat out/par-score.txt); echo "after stub_accept: hard $H"; if [ "$H" -ne 0 ]; then echo 'stub router hurt: reverting'; cp out/$N-par-routed.kicad_pcb $N.kicad_pcb; fi; fi
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup
bash ../tools/quality_pass.sh "$PWD" $N > out/$N-quality-run.log 2>&1 || echo "quality_pass.sh exited $? (out/$N-quality-run.log)"; grep -E "quality:|Traceback" out/$N-quality-run.log | tail -5   # Stage 3 of the quality programme (6 Sep 2026): straighten and via passes on a copy, DRC-gated, reverted when anything rises
python3 ../tools/silk_fix_all.py $N.kicad_pcb c 2>&1 | grep -vE 'Debug|leak' | tail -2
python3 - "$N" <<'PYX' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b); print('zones refilled before the board gate')
PYX
python3 ../tools/check_pcb_c.py $N.kicad_pcb 2>&1 | grep -E 'FAIL|RESULT'
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 ../tools/hardset.py out/$N-drc.json post --flag out/c8-clean.txt --label 'routed-board gate' | sed 's/^hardset:/routed-board DRC:/'
python3 -c "import json; d=json.load(open('out/$N-drc.json')); [print('  OPEN', ' ~ '.join('%s@(%.1f,%.1f)' % (i['description'][:50], i['pos']['x'], i['pos']['y']) for i in u['items'])) for u in d.get('unconnected_items', [])[:6]]"
if ! python3 ../tools/check_pcb_c.py $N.kicad_pcb 2>/dev/null | grep -q 'RESULT: ALL PASS'; then echo 'C8 GATE FAIL on the routed board'; echo open > out/c8-clean.txt; fi
# 8 Sep 2026 (MESHSAT-862 Stage C): the electrical verdicts before the clean flag: DC drop and current density of the intent rails, the impedance of the pair classes
python3 ../tools/dc_drop.py $N.kicad_pcb --json out/$N-dc_drop.json > out/$N-dc_drop.log 2>&1; DC=$?; grep -E 'dc_drop' out/$N-dc_drop.log | tail -14; [ "$DC" -eq 0 ] || { echo 'C8 DC DROP MISSED or unresolved (out/$N-dc_drop.log)'; echo open > out/c8-clean.txt; }
python3 ../tools/stackup_write.py $N.kicad_pcb 2>&1 | tail -1   # the routed board carries the stack for the read-back (8 Sep 2026)
python3 ../tools/impedance_check.py $N.kicad_pcb --json out/$N-impedance.json > out/$N-impedance.log 2>&1; IM=$?; grep -E 'impedance' out/$N-impedance.log | tail -14; [ "$IM" -eq 0 ] || { echo 'C8 IMPEDANCE MISSED (out/$N-impedance.log; openEMS on the missed pairs)'; echo open > out/c8-clean.txt; }
# 8 Sep 2026 (MESHSAT-862): the cross-board contracts are part of every finish (they were called by no chain before)
python3 ../tools/check_contracts.py .. > out/contracts.log 2>&1; grep -E 'FAIL|MISSING' out/contracts.log | head -12; if grep -q 'ALL CONTRACTS PASS' out/contracts.log; then echo 'contracts: ALL PASS'; else echo 'contracts: FAIL (out/contracts.log)'; echo open > out/c8-clean.txt; fi
CLEAN=$(cat out/c8-clean.txt); if [ "$CLEAN" != clean ]; then echo 'C8 NOT CLEAN, not finishing'; echo FINISH-C8-DONE; exit 1; fi
rm -rf out/$N-seals.dxf; kicad-cli pcb export dxf --mode-single --layers User.2,User.3,Edge.Cuts --output-units mm -o out/$N-seals.dxf $N.kicad_pcb >/dev/null 2>&1 && echo "seals DXF: out/$N-seals.dxf ($(grep -c -E '^(LINE|ARC|CIRCLE|LWPOLYLINE|POLYLINE)$' out/$N-seals.dxf) entities)"
cd ..; ./tools/finish_board.sh pcb-c-display-c8 pcb-c-display - meshsat-pcb-c-revA-C8 2>&1 | tail -16
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "C8: finish_board REFUSED the deliverable (verify_deliverable or an export step failed)"; echo FINISH-C8-DONE; exit 1; }   # 8 Sep 2026: a pipeline's status is tail's, so a refused deliverable used to be reported finished
echo FINISH-C8-DONE
