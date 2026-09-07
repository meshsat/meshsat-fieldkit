#!/usr/bin/env bash
# A22 (MESHSAT-830, 7 Sep 2026), from finish_a21.sh: wait for route_parallel.sh (PARALLEL-DONE in the log), stub router, dangling clean-up, pack-node and boost bars, legend pass, finish.
# Usage: finish_a22.sh <ecad dir> <parallel log, relative to pcb-a-power>
cd "$1/pcb-a-power"; N=pcb-a-power; LOG="$2"
while ! grep -q PARALLEL-DONE "$LOG" 2>/dev/null; do sleep 30; done
grep -E 'attempt|WINNER' "$LOG"
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
cp $N.kicad_pcb out/$N-par-routed.kicad_pcb
# A21 (5 Sep 2026): a few open connections get one continuation pass of the router on the routed board before the stub router (cont_route.sh keeps the board only if it improves)
UN=$(python3 -c "import json; print(len(json.load(open('out/$N-drc.json')).get('unconnected_items', [])))" 2>/dev/null || echo 0)
if [ "$UN" -gt 0 ] && [ "$UN" -le 6 ]; then ../tools/cont_route.sh "$PWD" $N 80 900 2>&1 | grep -E 'cont:'; kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1; fi
STUB_LAYERS=F.Cu,In2.Cu,In3.Cu,B.Cu STUB_GRID=0.1 STUB_WIN_SCALE=2.5 STUB_MAXN=16000000 nice -n 10 python3 ../tools/stub_router.py $N.kicad_pcb out/$N-drc.json > out/$N-stub.log 2>&1 || echo "stub router CRASHED, exit $? (out/$N-stub.log)"; grep -E 'closed|FAILED|stub_router|Error' out/$N-stub.log | head -12
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - "$N" <<'PY'
import json, collections, sys
d=json.load(open('out/%s-drc.json' % sys.argv[1])); c=collections.Counter(v['type'] for v in d['violations'])
hard=sum(c[t] for t in ('clearance','shorting_items','tracks_crossing','hole_clearance','hole_to_hole','copper_edge_clearance')); open('out/par-score.txt','w').write('%d' % hard); print('after stub router: hard', hard, 'unrouted', len(d.get('unconnected_items', [])))
PY
read H < out/par-score.txt; if [ "$H" -ne 0 ]; then python3 ../tools/stub_accept.py out/$N-par-routed.kicad_pcb $N.kicad_pcb out/$N-drc.json 2>&1 | grep stub_accept; kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1; H=$(python3 -c "import json,collections,sys; d=json.load(open('out/%s-drc.json' % sys.argv[1])); c=collections.Counter(v['type'] for v in d['violations']); print(sum(c[t] for t in ('clearance','shorting_items','tracks_crossing','hole_clearance','hole_to_hole','copper_edge_clearance')))" $N); echo "after stub_accept: hard $H"; if [ "$H" -ne 0 ]; then echo 'stub router hurt: reverting'; cp out/$N-par-routed.kicad_pcb $N.kicad_pcb; fi; fi
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup
bash ../tools/quality_pass.sh "$PWD" $N 2>&1 | grep "quality:" | tail -4   # Stage 3 of the quality programme (6 Sep 2026): straighten and via passes on a copy, DRC-gated, reverted when anything rises
# Owner ruling 5 Sep 2026 17:00 (appendix 32.40): a differential pair over 1 mm of intra-pair mismatch blocks the finish; pair_match.sh meanders the short
# legs itself, and when it still fails the session audits out/audit/*.png (pair_audit.py), traces the cause and iterates. No human look.
if ! ../tools/pair_match.sh "$PWD" $N check_pcb_a.py 2>&1 | grep -E "pair_match|WARN|PASS|meander" | cut -c1-140; then
  mkdir -p out/audit; for pr in USB_D8 USB_E6 USB_WALL; do python3 ../tools/pair_audit.py $N.kicad_pcb $pr out/audit/$pr.png 2>&1 | grep pair_audit; done
  echo 'A22 PAIRS NOT MATCHED, not finishing (audit images in out/audit)'; echo open > out/a22-clean.txt; echo FINISH-A22-DONE; exit 1
fi
python3 ../tools/silk_fix_all.py $N.kicad_pcb a 2>&1 | grep -vE 'Debug|leak' | tail -2
# A22: refill, then the board gate on the routed board (node and rail widths); an open or a FAIL stops the finish
python3 - "$N" <<'PYX' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b); print('zones refilled before the routed-board gate')
PYX
python3 ../tools/check_pcb_a.py $N.kicad_pcb 2>&1 | grep -E 'FAIL|band|stitch|routed at|RESULT' | tail -12
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - "$N" <<'PYX'
import json, collections, sys
d = json.load(open('out/%s-drc.json' % sys.argv[1])); c = collections.Counter(v['type'] for v in d['violations'])
hard = sum(c[t] for t in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'hole_to_hole', 'copper_edge_clearance')); un = len(d.get('unconnected_items', []))
print('routed-board gate: hard', hard, 'unrouted', un); open('out/a22-clean.txt', 'w').write(('clean' if hard == 0 and un == 0 else 'open') + '\n')
PYX
if ! python3 ../tools/check_pcb_a.py $N.kicad_pcb 2>/dev/null | grep -q 'RESULT: ALL PASS'; then echo 'A22 GATE FAIL on the routed board'; echo open > out/a22-clean.txt; fi
CLEAN=$(cat out/a22-clean.txt); if [ "$CLEAN" != clean ]; then echo 'A22 NOT CLEAN, not finishing'; echo FINISH-A22-DONE; exit 1; fi
cd ..; ./tools/finish_board.sh pcb-a-power pcb-a-power - meshsat-pcb-a-revA-A22 2>&1 | tail -16
echo FINISH-A22-DONE
