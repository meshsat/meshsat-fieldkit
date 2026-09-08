#!/usr/bin/env bash
# B16: wait for route_parallel.sh (PARALLEL-DONE in the log), dangling clean-up FIRST, then the stub router on what is really open (on the four routing layers),
# a zone refill before its check, a second clean-up, the quality pass, legend pass, the pair gate (PCIe, USB 3, HDMI and Ethernet pairs within 1 mm), finish.
# Usage: finish_b16.sh <ecad dir> <parallel log, relative to pcb-b-compute>
set -uo pipefail   # 8 Sep 2026 (MESHSAT-862): no set line before; the finish decides whether a board is clean
cd "$1/pcb-b-compute-b17"; N=pcb-b-compute; LOG="$2"
rm -f out/b17-clean.txt out/par-score.txt out/contracts.log   # a stale clean flag must never finish a board (register class 6)
while ! grep -q PARALLEL-DONE "$LOG" 2>/dev/null; do sleep 30; done
grep -E 'attempt|WINNER' "$LOG"
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
cp $N.kicad_pcb out/$N-par-routed.kicad_pcb
# 7 Sep 2026: the router's knot (two nets' tracks tangled at one spot, 20 to 25 shorts) is removed before anything else; the stub router closes the nets it opens
python3 ../tools/unknot.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep unknot && python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup; kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak' | tail -1
cp $N.kicad_pcb out/$N-cleaned.kicad_pcb
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
STUB_LAYERS=F.Cu,In2.Cu,In3.Cu,B.Cu STUB_GRID=0.1 nice -n 10 python3 ../tools/stub_router.py $N.kicad_pcb out/$N-drc.json > out/$N-stub.log 2>&1 || { echo "stub router CRASHED, exit $? (out/$N-stub.log)"; echo open > out/b17-clean.txt; echo FINISH-B17-DONE; exit 1; }; grep -E 'closed|FAILED|stub_router|Error' out/$N-stub.log | head -12
python3 - "$N" <<'PY' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b); print('zones refilled after the stub router')
PY
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 ../tools/hardset.py out/$N-drc.json post --score out/par-score.txt --label 'after stub router' | grep -v '^hardset:'   # 8 Sep 2026 (MESHSAT-862): tools/hardset.py is the one hard set
[ -s out/par-score.txt ] || { echo "no DRC score after the stub router (hardset refused)"; echo open > out/b17-clean.txt; echo FINISH-B17-DONE; exit 1; }; read H < out/par-score.txt; if [ "$H" -ne 0 ]; then python3 ../tools/stub_accept.py out/$N-par-routed.kicad_pcb $N.kicad_pcb out/$N-drc.json 2>&1 | grep stub_accept; kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1; H=$(python3 ../tools/hardset.py out/$N-drc.json post --score out/par-score.txt >/dev/null; cat out/par-score.txt); echo "after stub_accept: hard $H"; if [ "$H" -ne 0 ]; then echo 'stub router hurt: reverting'; cp out/$N-par-routed.kicad_pcb $N.kicad_pcb; fi; fi
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak' | tail -1
bash ../tools/quality_pass.sh "$PWD" $N > out/$N-quality-run.log 2>&1 || echo "quality_pass.sh exited $? (out/$N-quality-run.log)"; grep -E "quality:|Traceback" out/$N-quality-run.log | tail -5
python3 ../tools/silk_fix_all.py $N.kicad_pcb b 2>&1 | grep -vE 'Debug|leak' | tail -2
# Owner ruling 5 Sep 2026 17:00 (appendix 32.40): a differential pair over 1 mm blocks the finish; pair_match.sh meanders the short legs itself, the session audits the rest.
../tools/pair_match.sh "$PWD" $N check_pcb_b.py > out/pair-match.log 2>&1; PM=$?; grep -E "pair_match|WARN|PASS|meander" out/pair-match.log | cut -c1-140   # 8 Sep 2026: the status is pair_match.sh's own, not cut's (register class 1.3: the gate never fired before)
if [ "$PM" -ne 0 ]; then
  mkdir -p out/audit; for pr in PCIE1_TX PCIE2_TX PCIE3_TX USB31_TX HDMI1_D0; do python3 ../tools/pair_audit.py $N.kicad_pcb $pr out/audit/$pr.png 2>&1 | grep pair_audit; done
  echo 'B17 PAIRS NOT MATCHED, not finishing (audit images in out/audit)'; echo open > out/b17-clean.txt; echo FINISH-B17-DONE; exit 1
fi
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 ../tools/hardset.py out/$N-drc.json post --flag out/b17-clean.txt --label 'routed-board gate' | sed 's/^hardset:/routed-board DRC:/'
python3 -c "import json; d=json.load(open('out/$N-drc.json')); [print('  OPEN', ' ~ '.join('%s@(%.1f,%.1f)' % (i['description'][:50], i['pos']['x'], i['pos']['y']) for i in u['items'])) for u in d.get('unconnected_items', [])[:6]]"
python3 ../tools/pruned_gate.py $N.kicad_pcb out/$N-pruned.txt 2>&1 | grep -E 'pruned_gate' | tail -6; python3 ../tools/pruned_gate.py $N.kicad_pcb out/$N-pruned.txt >/dev/null 2>&1 || { echo 'B17 PRUNED PAD NOT REACHED by the router'; echo open > out/b17-clean.txt; }
python3 ../tools/check_pcb_b.py $N.kicad_pcb 2>&1 | grep -E 'FAIL|RESULT|WARN|pieces|stitch' | tail -14; if ! python3 ../tools/check_pcb_b.py $N.kicad_pcb 2>/dev/null | grep -q 'RESULT: ALL PASS'; then echo 'B17 GATE FAIL on the routed board'; echo open > out/b17-clean.txt; fi
# 8 Sep 2026 (MESHSAT-862 Stage C): the electrical verdicts before the clean flag: DC drop and current density of the intent rails, the impedance of the pair classes
python3 ../tools/dc_drop.py $N.kicad_pcb --json out/$N-dc_drop.json > out/$N-dc_drop.log 2>&1; DC=$?; grep -E 'dc_drop' out/$N-dc_drop.log | tail -14; [ "$DC" -eq 0 ] || { echo 'B17 DC DROP MISSED or unresolved (out/$N-dc_drop.log)'; echo open > out/b17-clean.txt; }
python3 ../tools/stackup_write.py $N.kicad_pcb 2>&1 | tail -1   # the routed board carries the stack for the read-back (8 Sep 2026)
python3 ../tools/impedance_check.py $N.kicad_pcb --json out/$N-impedance.json > out/$N-impedance.log 2>&1; IM=$?; grep -E 'impedance' out/$N-impedance.log | tail -14; [ "$IM" -eq 0 ] || { echo 'B17 IMPEDANCE MISSED (out/$N-impedance.log; openEMS on the missed pairs)'; echo open > out/b17-clean.txt; }
# 8 Sep 2026 (MESHSAT-862): the cross-board contracts are part of every finish (they were called by no chain before)
python3 ../tools/check_contracts.py .. > out/contracts.log 2>&1; grep -E 'FAIL|MISSING' out/contracts.log | head -12; if grep -q 'ALL CONTRACTS PASS' out/contracts.log; then echo 'contracts: ALL PASS'; else echo 'contracts: FAIL (out/contracts.log)'; echo open > out/b17-clean.txt; fi
CLEAN=$(cat out/b17-clean.txt); if [ "$CLEAN" != clean ]; then echo 'B17 NOT CLEAN, not finishing'; echo FINISH-B17-DONE; exit 1; fi
cd ..; ./tools/finish_board.sh pcb-b-compute-b17 pcb-b-compute post_fix_b13.py meshsat-pcb-b-revA-B17 2>&1 | tail -16
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "B17: finish_board REFUSED the deliverable (verify_deliverable or an export step failed)"; echo FINISH-B17-DONE; exit 1; }   # 8 Sep 2026: a pipeline's status is tail's, so a refused deliverable used to be reported finished
echo FINISH-B17-DONE
