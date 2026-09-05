#!/usr/bin/env bash
# B14 length matching (owner decision 1, 5 Sep 2026): meanders on the short legs of the PCIe pairs, DRC, pair report, deliverable re-export.
# Usage: run_meander_b14.sh <ecad dir>; exits 1 and restores the board if the DRC hard count rises or the meander cannot be placed.
set -uo pipefail; cd "$1/pcb-b-compute"; N=pcb-b-compute
cp $N.kicad_pcb out/$N-before-meander.kicad_pcb
kicad-cli pcb drc --severity-all --format json -o out/$N-drc-before.json $N.kicad_pcb >/dev/null 2>&1
python3 ../tools/meander.py $N.kicad_pcb PCIe_TX_N 17.18 2>&1 | grep meander || { echo "MEANDER FAILED (TX)"; cp out/$N-before-meander.kicad_pcb $N.kicad_pcb; exit 1; }
python3 ../tools/meander.py $N.kicad_pcb PCIe_RX_P 1.92 2>&1 | grep meander || { echo "MEANDER FAILED (RX)"; cp out/$N-before-meander.kicad_pcb $N.kicad_pcb; exit 1; }
python3 - "$N" <<'PYY' 2>&1 | grep -vE 'Debug|leak'
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1] + '.kicad_pcb'); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1] + '.kicad_pcb', b); print('zones refilled')
PYY
kicad-cli pcb drc --severity-all --format json -o out/$N-drc.json $N.kicad_pcb >/dev/null 2>&1
python3 - "$N" <<'PYY'
import json, collections, sys
def hard(f):
    d = json.load(open(f)); c = collections.Counter(v['type'] for v in d['violations'])
    return sum(c[t] for t in ('clearance', 'shorting_items', 'tracks_crossing', 'hole_clearance', 'hole_to_hole', 'copper_edge_clearance')), len(d.get('unconnected_items', []))
h0, u0 = hard('out/%s-drc-before.json' % sys.argv[1]); h1, u1 = hard('out/%s-drc.json' % sys.argv[1])
print('meander DRC: before hard %d unrouted %d, after hard %d unrouted %d' % (h0, u0, h1, u1)); open('out/meander-ok.txt', 'w').write(('ok' if h1 == 0 and u1 == 0 else 'bad') + '\n')
PYY
if [ "$(cat out/meander-ok.txt)" != ok ]; then echo "MEANDER HURT THE BOARD, restored"; cp out/$N-before-meander.kicad_pcb $N.kicad_pcb; exit 1; fi
python3 ../tools/check_pcb_b.py $N.kicad_pcb 2>&1 | grep -E "pair length|RESULT" | cut -c1-150
cd ..; ./tools/finish_board.sh pcb-b-compute pcb-b-compute - meshsat-pcb-b-revA-B14 2>&1 | grep -E "unrouted|deliverables|Error|Trace" | cut -c1-140
echo MEANDER-B14-DONE
