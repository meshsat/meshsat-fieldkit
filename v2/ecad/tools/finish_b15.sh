#!/usr/bin/env bash
# B15: wait for route_parallel.sh (PARALLEL-DONE in the log), dangling clean-up FIRST, then the stub router on what is really open,
# a zone refill before its check (a stale fill reports every new via as a plane clearance violation), a second clean-up, legend pass, finish.
# Usage: finish_b13.sh <ecad dir> <parallel log, relative to pcb-b-compute>
cd "$1/pcb-b-compute"; N=pcb-b-compute; LOG="$2"
while ! grep -q PARALLEL-DONE "$LOG" 2>/dev/null; do sleep 30; done
grep -E 'attempt|WINNER' "$LOG"
cp $N.kicad_pcb out/$N-par-routed.kicad_pcb
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep cleanup
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak' | tail -1
cp $N.kicad_pcb out/$N-cleaned.kicad_pcb
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
nice -n 10 python3 ../tools/stub_router.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -E 'closed|FAILED|stub_router'
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
read H < out/par-score.txt; if [ "$H" -ne 0 ]; then echo 'stub router hurt: reverting to the cleaned board'; cp out/$N-cleaned.kicad_pcb $N.kicad_pcb; fi
python3 ../tools/cleanup_dangling.py $N.kicad_pcb 2>&1 | grep -vE 'Debug|leak' | tail -1
python3 ../tools/silk_fix_all.py $N.kicad_pcb b 2>&1 | grep -vE 'Debug|leak' | tail -2
# Owner ruling 5 Sep 2026 17:00 (appendix 32.40): a differential pair over 1 mm of intra-pair mismatch blocks the finish; pair_match.sh meanders the short
# legs itself, and when it still fails the session audits out/audit/*.png (pair_audit.py), traces the cause and iterates. No human look.
if ! ../tools/pair_match.sh "$PWD" $N check_pcb_b.py 2>&1 | grep -E "pair_match|WARN|PASS|meander" | cut -c1-140; then
  mkdir -p out/audit; for pr in PCIe_TX PCIe_RX PCIe_CLK; do python3 ../tools/pair_audit.py $N.kicad_pcb $pr out/audit/$pr.png 2>&1 | grep pair_audit; done
  echo 'B15 PAIRS NOT MATCHED, not finishing (audit images in out/audit)'; echo open > out/b15-clean.txt; echo FINISH-B15-DONE; exit 1
fi
# B15 (5 Sep 2026): the finish refuses an open or dirty board; the chain commits only on out/b15-clean.txt = clean
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - "$N" <<'PYX'
import json, collections, sys
d = json.load(open('out/%s-drc.json' % sys.argv[1])); c = collections.Counter(v['type'] for v in d['violations'])
hard = sum(c[t] for t in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'hole_to_hole', 'copper_edge_clearance')); un = len(d.get('unconnected_items', []))
print('routed-board gate: hard', hard, 'unrouted', un); open('out/b15-clean.txt', 'w').write(('clean' if hard == 0 and un == 0 else 'open') + '\n')
for u in d.get('unconnected_items', [])[:6]: print('  OPEN', ' ~ '.join('%s@(%.1f,%.1f)' % (i['description'][:50], i['pos']['x'], i['pos']['y']) for i in u['items']))
PYX
CLEAN=$(cat out/b15-clean.txt); if [ "$CLEAN" != clean ]; then echo 'B15 NOT CLEAN, not finishing'; echo FINISH-B15-DONE; exit 1; fi
python3 ../tools/retitle.py $N.kicad_pcb B15 2026-09-05 'MESHSAT-795 |=>MESHSAT-795/802 |' 2>&1 | grep -E 'retitle: [0-9]' | cut -c1-100   # the chain reuses the first generation's silk text
cd ..; ./tools/finish_board.sh pcb-b-compute pcb-b-compute post_fix_b13.py meshsat-pcb-b-revA-B15 2>&1 | tail -16
echo FINISH-B15-DONE
