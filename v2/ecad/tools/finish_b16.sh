#!/usr/bin/env bash
# B16: wait for route_parallel.sh (PARALLEL-DONE in the log), dangling clean-up FIRST, then the stub router on what is really open (on the four routing layers),
# a zone refill before its check, a second clean-up, the quality pass, legend pass, the pair gate (PCIe, USB 3, HDMI and Ethernet pairs within 1 mm), finish.
# Usage: finish_b16.sh <ecad dir> <parallel log, relative to pcb-b-compute>
cd "$1/pcb-b-compute"; N=pcb-b-compute; LOG="$2"
while ! grep -q PARALLEL-DONE "$LOG" 2>/dev/null; do sleep 30; done
grep -E 'attempt|WINNER' "$LOG"
cp $N.kicad_pcb out/$N-par-routed.kicad_pcb
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak' | tail -1
cp $N.kicad_pcb out/$N-cleaned.kicad_pcb
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
STUB_LAYERS=F.Cu,In2.Cu,In3.Cu,B.Cu STUB_GRID=0.1 nice -n 10 python3 ../tools/stub_router.py $N.kicad_pcb out/$N-drc.json > out/$N-stub.log 2>&1 || echo "stub router CRASHED, exit $? (out/$N-stub.log)"; grep -E 'closed|FAILED|stub_router|Error' out/$N-stub.log | head -12
python3 - "$N" <<'PY' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b); print('zones refilled after the stub router')
PY
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - "$N" <<'PY'
import json, collections, sys
d=json.load(open('out/%s-drc.json' % sys.argv[1])); c=collections.Counter(v['type'] for v in d['violations'])
hard=sum(c[t] for t in ('clearance','shorting_items','tracks_crossing','hole_clearance','hole_to_hole','copper_edge_clearance')); open('out/par-score.txt','w').write('%d' % hard); print('after stub router: hard', hard, 'unrouted', len(d.get('unconnected_items', [])))
PY
read H < out/par-score.txt; if [ "$H" -ne 0 ]; then python3 ../tools/stub_accept.py out/$N-par-routed.kicad_pcb $N.kicad_pcb out/$N-drc.json 2>&1 | grep stub_accept; kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1; H=$(python3 -c "import json,collections,sys; d=json.load(open('out/%s-drc.json' % sys.argv[1])); c=collections.Counter(v['type'] for v in d['violations']); print(sum(c[t] for t in ('clearance','shorting_items','tracks_crossing','hole_clearance','hole_to_hole','copper_edge_clearance')))" $N); echo "after stub_accept: hard $H"; if [ "$H" -ne 0 ]; then echo 'stub router hurt: reverting'; cp out/$N-par-routed.kicad_pcb $N.kicad_pcb; fi; fi
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak' | tail -1
bash ../tools/quality_pass.sh "$PWD" $N 2>&1 | grep "quality:" | tail -4
python3 ../tools/silk_fix_all.py $N.kicad_pcb b 2>&1 | grep -vE 'Debug|leak' | tail -2
# Owner ruling 5 Sep 2026 17:00 (appendix 32.40): a differential pair over 1 mm blocks the finish; pair_match.sh meanders the short legs itself, the session audits the rest.
if ! ../tools/pair_match.sh "$PWD" $N check_pcb_b.py 2>&1 | grep -E "pair_match|WARN|PASS|meander" | cut -c1-140; then
  mkdir -p out/audit; for pr in PCIE1_TX PCIE2_TX PCIE3_TX USB31_TX HDMI1_D0; do python3 ../tools/pair_audit.py $N.kicad_pcb $pr out/audit/$pr.png 2>&1 | grep pair_audit; done
  echo 'B16 PAIRS NOT MATCHED, not finishing (audit images in out/audit)'; echo open > out/b16-clean.txt; echo FINISH-B16-DONE; exit 1
fi
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - "$N" <<'PYX'
import json, collections, sys
d = json.load(open('out/%s-drc.json' % sys.argv[1])); c = collections.Counter(v['type'] for v in d['violations'])
hard = sum(c[t] for t in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'hole_to_hole', 'copper_edge_clearance')); un = len(d.get('unconnected_items', []))
print('routed-board gate: hard', hard, 'unrouted', un); open('out/b16-clean.txt', 'w').write(('clean' if hard == 0 and un == 0 else 'open') + '\n')
for u in d.get('unconnected_items', [])[:6]: print('  OPEN', ' ~ '.join('%s@(%.1f,%.1f)' % (i['description'][:50], i['pos']['x'], i['pos']['y']) for i in u['items']))
PYX
CLEAN=$(cat out/b16-clean.txt); if [ "$CLEAN" != clean ]; then echo 'B16 NOT CLEAN, not finishing'; echo FINISH-B16-DONE; exit 1; fi
python3 ../tools/check_pcb_b.py $N.kicad_pcb 2>&1 | grep -E 'FAIL|RESULT|WARN'
cd ..; ./tools/finish_board.sh pcb-b-compute pcb-b-compute post_fix_b13.py meshsat-pcb-b-revA-B16 2>&1 | tail -16
echo FINISH-B16-DONE
